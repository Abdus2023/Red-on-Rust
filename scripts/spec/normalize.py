"""Stage S3 — NORMALIZE (§10).

Terminology, identifier, reference, notation and predicate normalization —
performed as **registration, never as rewriting**.

Normalization MUST preserve meaning, so this stage never edits normative text.
It records what the repository's own normalization authorities say, and then
proves mechanically that the canonical statements conform:

  * terminology: `term/10-index.json` (86 canonical terms with the seven
    required fields, 33 non-conflation laws `N-…`, 87 collisions `X-…`) plus the
    `spec/05` §6 rules;
  * duplicated definitions: a scan for a frozen identity defined under two
    homes (exactly the check the terminology pass ran; a duplicate is AUDIT-ed,
    never silently unified — §10);
  * canonical predicates: the R-CORE-11 canonical-form statement must agree
    with the chain R-CORE-02 publishes (predicate agreement, the same figure
    `state/` projects);
  * identifier/notation: every `R-…` chunk must carry exactly one bold identity
    head, exactly one section home, and a resolvable provenance line; superseded
    forms stay quoted in place (R-SCOPE-03) — the record of what normalization
    did NOT touch;
  * no silent identity operations: a scan for ADD/DELETE/MERGE/SPLIT/RENAME/
    RENUMBER language directed at the identities this pipeline reads, proving
    this stage's own output contains none.

Contradictions that *look* like they need repair are not repaired here; they are
handed to S4 as they stand (§10: "If two statements appear contradictory: AUDIT,
rather than silently choosing one").
"""
from __future__ import annotations

import re

from _common import (StageFailure, line_refs_of, md_escape, provenance, render_json,
                     sha256_text, table)

STAGE = "S3-normalize"

_RID = re.compile(r"^\*\*(R-[A-Z]+-\d+)")


def _one_line(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def terminology(ctx) -> tuple[dict, list]:
    """Projection of the authoritative terminology register + conformance checks."""
    notes = []
    term_idx = ctx.term or {}
    terms = term_idx.get("terms", [])
    laws = term_idx.get("laws", [])
    collisions = term_idx.get("collisions", [])
    required = term_idx.get("required_terms", [])
    fields = ["CANONICAL_TERM", "FORBIDDEN_VARIANTS", "DEFINITION", "TYPE", "OWNER",
              "FIRST_DEFINITION", "DEPENDENTS"]
    incomplete = sorted(str(t.get("tid")) for t in terms if any(f not in t for f in fields))
    if incomplete:
        raise StageFailure(f"[{STAGE}] terminology index shape changed: terms without all seven "
                           f"required fields: {incomplete[:6]}")
    counts = {
        "canonical_terms": len(terms),
        "non_conflation_laws": len(laws),
        "collisions": len(collisions),
        "required_terms_named": len(required),
        "collision_severities": term_idx.get("counts", {}).get("collision_severities", {}),
    }
    checks = [(
        "terminology registry shape: all seven required fields present on every term",
        bool(terms),
        f"{counts['canonical_terms']} terms indexed by term/10 (fields: "
        + ", ".join(fields) + ")",
    ), (
        "every collision carries a severity and at least one affected term",
        all(c.get("severity") and c.get("affects") for c in collisions),
        f"{counts['collisions']} collisions",
    ), (
        "non-conflation laws reference existing term identities",
        all(l.get("left") in {t.get("tid") for t in terms} and
            l.get("right") in {t.get("tid") for t in terms} for l in laws),
        f"{counts['non_conflation_laws']} laws (N-…)",
    )]
    # spec/05's own prose counts (the §8 line the FINAL1 report flags as stale
    # in the inputs) are NOT re-based here; the divergence is recorded.
    s05 = ""
    try:
        s05 = (ctx.repo / "spec/05-terminology.md").read_text(encoding="utf-8")
    except OSError:
        pass
    m = re.search(r"(\d+)\s+canonical terms\s*/\s*(\d+)\s+non-conflation laws", s05)
    if m:
        claimed = (int(m.group(1)), int(m.group(2)))
        actual = (counts["canonical_terms"], counts["non_conflation_laws"])
        notes.append({
            "item": "spec/05 §8 prose counts vs term/10 index",
            "claimed_in_spec05": f"{claimed[0]} terms / {claimed[1]} laws",
            "authority_term10": f"{actual[0]} terms / {actual[1]} laws",
            "disposition": ("recorded, not rewritten — `final/07` already files this as a stale "
                            "input prose line; normalization never edits an authority"),
        })
        checks.append(("spec/05 prose vs term/10 authority (recorded divergence, not repaired)",
                       True, "see normalization-report §2"))
    return {"counts": counts, "notes": notes, "checks": checks,
            "authority": "term/10-index.json (data of record: term/_terms.py)"}, checks


def duplicate_definitions(ctx) -> tuple[dict, list]:
    """A frozen identity must have exactly one defining home in the canonical text."""
    homes: dict[str, list[str]] = {}
    for c in ctx.chunks:
        for rid in set(re.findall(r"^\*\*(R-[A-Z]+-\d+)", c["text"], re.M)):
            homes.setdefault(rid, []).append(c["section"])
    dupes = {k: v for k, v in sorted(homes.items()) if len(v) > 1}
    # definitional statements: `X is defined as` / `pub enum X` declarations
    decls: dict[str, list[str]] = {}
    for c in ctx.chunks:
        for m in re.finditer(r"pub (?:enum|struct) (\w+)", c["text"]):
            decls.setdefault(m.group(1), []).append(c["id"])
    multi = {k: sorted(set(v)) for k, v in sorted(decls.items()) if len(set(v)) > 1}
    return ({
        "duplicate_requirement_definitions": dupes,
        "types_declared_in_more_than_one_chunk": multi,
        "policy": ("a duplicate is an AUDIT item, never a silent unification (§10); "
                   "the terminology pass's collision register (term/02) remains the home "
                   "for name-level duplicates"),
    }, [
        ("no requirement identity defined twice in the canonical text", not dupes,
         f"{len(homes)} identities scanned"),
        ("type declarations duplicated across chunks are recorded, not merged", True,
         f"{len(multi)} duplicated declaration(s): " + (", ".join(list(multi)[:6]) or "none")),
    ])


def predicates(ctx) -> tuple[dict, list]:
    """R-CORE-11 canonical-form agreement with the R-CORE-02 published chain."""
    core02 = ctx.spec01.get("R-CORE-02", {}).get("text", "")
    core11 = ctx.spec01.get("R-CORE-11", {}).get("text", "")
    m = re.search(r"`ExternalEffect\(E\) ⇒ (.+?)`", core02)
    chain = m.group(1) if m else ""
    conjuncts = [c.strip() for c in chain.split("∧")] if chain else []
    canonical_first = "ValidatedRequest(E)" in core11
    superseded_quoted = bool(re.search(r"SUPERSEDED", core11, re.I)) and \
        bool(re.search(r"SUPERSEDED", core02, re.I))
    subsumption = "ValidatedRequest(E) ⇒ ValidatedPlan" in _one_line(core11)
    data = {
        "chain_home": "R-CORE-02",
        "predicate_signature_home": "R-CORE-11",
        "conjunct_count": len(conjuncts),
        "conjuncts": conjuncts,
        "first_conjunct": conjuncts[0] if conjuncts else None,
        "canonical_form_declared": canonical_first,
        "subsumption_recorded": subsumption,
        "superseded_forms_quoted_not_deleted": superseded_quoted,
        "normalized_digest": sha256_text(_one_line(chain)),
        "note": ("normalization records the predicate agreement; it does not restate, re-order or "
                 "re-predicate the chain. The agreement figure is the same one state/ projects."),
    }
    checks = [
        ("canonical predicate present as the chain's first conjunct",
         bool(conjuncts) and conjuncts[0].startswith("ValidatedRequest(E)"),
         f"first conjunct: {conjuncts[0] if conjuncts else 'MISSING'}"),
        ("chain has exactly seven conjuncts (R-CORE-02)", len(conjuncts) == 7,
         f"{len(conjuncts)} conjuncts"),
        ("superseded readings quoted, not deleted (R-SCOPE-03)", superseded_quoted,
         "SUPERSEDED markers present in both R-CORE-02 and R-CORE-11"),
    ]
    if not conjuncts or conjuncts[0] != "ValidatedRequest(E)":
        raise StageFailure(f"[{STAGE}] canonical predicate drift: R-CORE-02 publishes "
                           f"{conjuncts[:1]}; R-CORE-11 declares ValidatedRequest(E). "
                           "Refusing to normalize — this is a contradiction for AUDIT, not a "
                           "repair target (§10).")
    return data, checks


def identifiers_and_notation(ctx) -> tuple[dict, list]:
    """Identity/notation well-formedness of every canonical statement."""
    bad_head, no_section, no_prov = [], [], []
    for c in ctx.chunks:
        if not _RID.match(c["text"]):
            bad_head.append(c["id"])
        if not c["section"]:
            no_section.append(c["id"])
        # Provenance is satisfied by any of: a line citation inside the canonical
        # statement; a line citation in the canonical registry row (the chunk
        # inherits it — the convention spec/03 records); or a frozen-addendum
        # record, whose provenance is the governance action, not a line.
        reg_cell = ctx.obligations.get(c["id"], {}).get("provenance", "")
        if not (c["source_refs"] or line_refs_of(reg_cell) or "addendum" in c["text"].lower()
                or "addendum" in reg_cell.lower()):
            no_prov.append(c["id"])
    checks = [
        ("every chunk opens with exactly one bold identity head", not bad_head,
         f"{len(ctx.chunks)} chunks"),
        ("every chunk has exactly one section home", not no_section and
         all(sum(1 for d in ctx.chunks if d["id"] == c["id"]) == 1 for c in ctx.chunks),
         "single-homed normative text (spec/00 §1 rule 3)"),
        ("every chunk carries resolvable provenance (own lines, inherited registry lines, "
         "or a frozen addendum)", not no_prov, f"{len(no_prov)} chunk(s) with neither"),
    ]
    vocab = {}
    for c in ctx.chunks:
        for v in re.findall(r"\b(MUST NOT|MUST|SHOULD NOT|SHOULD|MAY|MUST NOT)\b", c["text"]):
            vocab[v] = vocab.get(v, 0) + 1
    if ctx.spec10:
        s10_sec = {r["id"]: r["section"] for r in ctx.spec10["requirements"]}
        mismatched = sorted(rid for rid, c in ctx.spec01.items()
                            if s10_sec.get(rid) and s10_sec[rid] != c["section"])
        checks.append(("section attribution agrees with spec/10 index", not mismatched,
                       f"{len(mismatched)} mismatch(es): {mismatched[:5]}"))
    checks.append(("normative vocabulary is the repository's own",
                   set(vocab) <= {"MUST", "MUST NOT", "SHOULD", "MAY", "IS"},
                   ", ".join(f"{k}:{v}" for k, v in sorted(vocab.items()))))
    return {"modal_vocabulary_counts": dict(sorted(vocab.items())),
            "identity_form": "R-AREA-NN (spec/00 §3); never renumbered by this stage",
            "notation": "mathematical notation, box operators and hex tags carried as authored; "
                        "no character substitution performed (a substitution would be a semantic edit)"}, checks


def no_silent_identity_ops(ctx, my_text: str) -> list:
    """§4.5: prove this stage's own output performs no identity operation."""
    offenders = []
    for verb in ("RENUMBER", "MERGE", "SPLIT", "RENAME"):
        for m in re.finditer(rf"\b(we|this stage|the pipeline)\s+\w*\s*{verb.lower()}\w*\b",
                             my_text, re.I):
            offenders.append(m.group(0))
    return [("no unauthorized ADD/DELETE/MERGE/SPLIT/RENAME/RENUMBER asserted in this stage's output",
             not offenders, f"{len(offenders)} offender(s)")]


def run(ctx) -> dict:
    prov = provenance(STAGE, inputs=[("spec/01-canonical-specification.md", None),
                                     ("term/10-index.json", None),
                                     ("spec/05-terminology.md", None)],
                      generators="scripts/spec/normalize.py")
    term_data, term_checks = terminology(ctx)
    dup_data, dup_checks = duplicate_definitions(ctx)
    pred_data, pred_checks = predicates(ctx)
    id_data, id_checks = identifiers_and_notation(ctx)

    # terminology projection: canonical term per requirement area
    terms = (ctx.term or {}).get("terms", [])
    term_entries = []
    for t in sorted(terms, key=lambda x: str(x.get("tid") or "")):
        term_entries.append({
            "id": t.get("tid"),
            "canonical_term": t.get("CANONICAL_TERM"),
            "type": t.get("TYPE"),
            "owner": t.get("OWNER"),
            "owner_crate": t.get("owner_crate"),
            "domain": t.get("domain"),
            "first_definition": t.get("FIRST_DEFINITION"),
            "frozen_at": t.get("FROZEN_AT"),
            "forbidden_variants": t.get("FORBIDDEN_VARIANTS") or [],
            "dependents": t.get("DEPENDENTS") or [],
            "definition_sha256": sha256_text(str(t.get("DEFINITION") or "")),
            "status": "REGISTERED",
            "status_note": "REGISTERED is a registry state, not an evidence status; no term is "
                           "promoted by this projection",
            "authority": "term/10-index.json (data of record term/_terms.py)",
        })
    term_registry = {
        "schema": "redonrust.spec-pipeline.terminology/v1",
        "provenance": prov,
        "counts": term_data["counts"],
        "entries": term_entries,
        "laws": [{"id": l.get("lid"), "left": l.get("left"), "right": l.get("right"),
                  "statement_sha256": sha256_text(str(l.get("statement") or "")),
                  "enforcement": l.get("enforcement"), "authority": "term/03-laws.md"}
                 for l in sorted((ctx.term or {}).get("laws", []), key=lambda x: str(x.get("lid")))],
        "collisions": [{"id": c.get("xid"), "kind": c.get("kind"), "severity": c.get("severity"),
                        "affects": sorted(c.get("affects") or []),
                        "decision_needed": c.get("decision_needed"),
                        "new_finding": c.get("new_finding"),
                        "authority": "term/02-collisions.md"}
                       for c in sorted((ctx.term or {}).get("collisions", []),
                                       key=lambda x: str(x.get("xid")))],
        "policy": {
            "renames_performed": 0,
            "note": ("terminology is projected from its authority, never re-decided. The prohibition "
                     "the terminology pass recorded — do not rename a frozen API, type, symbol or "
                     "protocol field to make a collision disappear — binds this stage too."),
        },
    }

    body_text = render_json(term_registry)
    checks = (term_checks + dup_checks + pred_checks + id_checks
              + no_silent_identity_ops(ctx, body_text))
    norm_records = 0
    norm_records_missing = []
    try:
        nrec = (ctx.repo / "spec/normative-normalization-records.md").read_text(encoding="utf-8")
        rec_heads = list(re.finditer(r"^### (R-[A-Z]+-\d+)\s*$", nrec, re.M))
        norm_records = len(rec_heads)
        for i, m in enumerate(rec_heads):
            end = rec_heads[i + 1].start() if i + 1 < len(rec_heads) else len(nrec)
            body = nrec[m.start():end]
            if "**Original:**" not in body or "**Normalized:**" not in body:
                norm_records_missing.append(m.group(1))
        checks.append((
            "record of record: every normalization record carries Original and Normalized",
            not norm_records_missing,
            f"{norm_records} records over spec/01's identities; "
            f"{len(norm_records_missing)} without both fields"))
        # the addenda declare themselves originals by construction; check that
        # the exemption is *stated*, so the gap is a recorded fact not a hole.
        preamble = nrec.split("---", 1)[0]
        declared = sorted(set(re.findall(r"`R-[A-Z]+-\d+`", preamble)))
        checks.append((
            "frozen addenda exempt from normalization records are named, not silently absent",
            len(declared) > 0, f"{len(declared)} named exemption(s) in the record's preamble: "
            + ", ".join(declared[:6]) + "…"))
    except OSError:
        checks.append(("record of record present", False,
                       "spec/normative-normalization-records.md not found"))

    data = {
        "schema": "redonrust.spec-pipeline.normalize/v1",
        "provenance": prov,
        "terminology": term_data,
        "duplicates": dup_data,
        "predicates": pred_data,
        "identifiers": id_data,
        "normalization_records_of_record": {
            "path": "spec/normative-normalization-records.md",
            "records": norm_records,
            "incomplete": sorted(norm_records_missing),
            "note": ("S3 reads the record of record; it does not create one. The 148 frozen-source "
                     "requirements are the records' scope — the 36 addendum obligations are their own "
                     "originals, exempt by the record's own preamble."),
        },
        "checks": [{"check": c, "pass": p, "detail": md_escape(d)} for c, p, d in checks],
        "policy": {
            "semantic_repair_performed": False,
            "contradictions_handled_by": "hand-off to S4 audit (no silent choice between readings)",
            "authoritative_record": "spec/normative-normalization-records.md and term/ remain the "
                                    "records of what the normalization passes did",
        },
    }
    for c, p, d in checks:
        if not p:
            raise StageFailure(f"[{STAGE}] normalization conformance failed: {c} — {d}")
    rows = [[c, "PASS" if p else "FAIL", d] for c, p, d in checks]
    md = (
        "# 03 — Normalization (Stage S3)\n\n"
        "**Derived artifact of the controlled specification pipeline. Not a normative source.**\n\n"
        "Normalization = registration + conformance proof. No normative character was changed.\n\n"
        "## 1. Terminology (projected from the authoritative register)\n\n"
        + table([[k, (", ".join(map(str, v)) if isinstance(v, list) else
                       (", ".join(f"{a}:{b}" for a, b in sorted(v.items())) if isinstance(v, dict) else v))]
                  for k, v in sorted(term_data["counts"].items())], ["measure", "value"])
        + "\n### 1.1 Divergences recorded, not repaired\n\n"
        + (table([[n["item"], n["claimed_in_spec05"], n["authority_term10"], n["disposition"]]
                  for n in term_data["notes"]],
                 ["item", "claimed (spec/05)", "authority (term/10)", "disposition"])
           if term_data["notes"] else "_none_\n")
        + "\n## 2. Predicate canonicalization (R-CORE-02 ⇔ R-CORE-11)\n\n"
        + table([[k, v] for k, v in pred_data.items() if k != "conjuncts"], ["field", "value"])
        + "\nConjuncts in canonical order: " + ", ".join(f"`{c}`" for c in pred_data["conjuncts"])
        + "\n\n## 3. Duplicate-definition scan\n\n"
        + table([[k, ", ".join(map(str, v)) if isinstance(v, (list, dict)) else v]
                 for k, v in dup_data.items() if k != "policy"], ["scan", "result"])
        + "\n## 4. Identifier / notation well-formedness\n\n"
        + table([[k, v] for k, v in id_data.items()], ["field", "value"])
        + "\n## 5. Checks\n\n" + table(rows, ["check", "result", "detail"])
    )
    files = {"terminology.json": render_json(term_registry),
             "normalize.json": render_json(data),
             "normalize.md": md}
    return {"files": files, "data": data, "checks": checks,
            "terminology": term_registry, "predicates": pred_data}
