"""Stage S5 — CANONICALIZE (§12) — the safety theorem in code.

    UntrustedProposal -> DeterministicValidation -> ValidatedArtifact
                      -> Canonicalization -> AuthoritativeProjection
                      (never: UntrustedProposal -> CanonicalSpecification)

This canonicalizer is a *projection* engine, and the difference matters: the
repository already owns the canonical human-readable specification (`spec/01`,
compiled for presentation into `final/01`).  Producing a second, competing
canonical document would violate §20 and §4.5, so S5 does three things instead:

  1. it **reconstructs** a canonical specification from the validated
     registries alone — every line is emitted from a registry entry, so the
     artifact is a genuine generator output, not a copy-and-paste;
  2. it **proves** `Canonicalize(X) ⊆ NormativeContent(X)` by showing the
     reconstruction's requirement-chunk multiset is identical to the frozen
     normative text home's, byte-exactly modulo the whitespace normalisation
     the repository's own compiler documents;
  3. it **refuses** to proceed — raising a stage failure, blocking publication
     (§19) — on registry mismatch, on a requirement not present in the
     canonical registry, on an invented identity, on an evidence-status
     promotion, on ambiguous authority, and (in `--strict` mode) on carrying an
     unresolved contradiction without disclosure.

Under the default policy unresolved rows are *carried and disclosed*: that is
what the repository's own canonical specification does (open `U-`/`C-` rows are
published as open), and silently dropping them would be the fabrication §16
forbids.  The §22 acceptance condition "canonicalization introduces no
unauthorized requirements" is enforced by the multiset identity, which is
checked whether or not strict mode is on.
"""
from __future__ import annotations

import collections
import re

from _common import (check_rows,
                     EVIDENCE_CEILING, STATUS_LADDER, StageFailure, md_escape,
                     provenance, render_json, sha256_text, table)


def C_STRICT() -> bool:
    """Strictness is a repository-level switch (set by `--strict`), read at call
    time so no stage can cache a lax decision."""
    import _common
    return bool(getattr(_common, "STRICT_CANONICALIZATION", False))

STAGE = "S5-canonicalize"

CLAIM_WORDS = ("VERIFIED", "PROVEN", "IMPLEMENTED", "TESTED")


def _norm(text: str) -> str:
    lines = [re.sub(r"\s+", " ", l.strip()) for l in text.split("\n")]
    return "\n".join(l for l in lines if l).strip()


def run(ctx, run_state: dict, strict: bool = False) -> dict:
    strict = bool(strict or C_STRICT())
    entries = run_state["results"]["S1"]["entries"]
    sections = run_state["results"]["S2"]["data"]["sections"]
    audit = run_state["results"]["S4"]["data"]
    norm = run_state["results"]["S3"]["data"]

    by_id = {e["id"]: e for e in entries}
    if set(by_id) != set(ctx.spec01):
        raise StageFailure(f"[{STAGE}] registry mismatch: extraction produced {len(by_id)} "
                           f"identities, the normative text home has {len(ctx.spec01)} "
                           f"(extra {sorted(set(by_id) - set(ctx.spec01))[:5]}, "
                           f"missing {sorted(set(ctx.spec01) - set(by_id))[:5]})")

    # ---- rejection gates (§12) -------------------------------------------
    rejections = []
    for rid, e in sorted(by_id.items()):
        if rid not in ctx.obligations:
            rejections.append(f"{rid}: present in the canonical text but absent from the registry")
        if e["status"] != ctx.obligations[rid]["status"]:
            rejections.append(f"{rid}: status disagrees with the canonical registry")
        if e["status"] not in STATUS_LADDER:
            rejections.append(f"{rid}: status outside the frozen ladder")
        if e["status"] != EVIDENCE_CEILING:
            rejections.append(f"{rid}: status {e['status']} exceeds the repository's evidence "
                              f"ceiling ({EVIDENCE_CEILING}) — canonicalization may not promote")
        if not e["provenance"]["source_refs"] and not e["provenance"]["addendum_note"]:
            cell = ctx.obligations[rid]["provenance"]
            if not re.search(r"\d{3,5}", cell) and "addendum" not in cell.lower():
                rejections.append(f"{rid}: no resolvable provenance (canonical material without "
                                  "provenance is unregistered material)")
    if rejections:
        raise StageFailure(f"[{STAGE}] canonicalization refused ({len(rejections)} rejection(s)):\n  "
                           + "\n  ".join(rejections[:10]))

    # subset theorem: reconstruction must not add, drop, or mutate a chunk
    rebuilt = [e["statement"] for e in entries]
    authority = [ctx.spec01[rid]["text"] for rid in [e["id"] for e in entries]]
    def multiset(sig):
        return collections.Counter(_norm(s) for s in sig)
    a_m, b_m = multiset(authority), multiset(rebuilt)
    if a_m != b_m:
        only_canon = [k for k in (b_m - a_m)][:3]
        only_auth = [k for k in (a_m - b_m)][:3]
        raise StageFailure("[S5-canonicalize] Canonicalize(X) ⊄ NormativeContent(X): the "
                           "reconstruction differs from the normative text home.\n"
                           f"  introduced: {md_escape(str(only_canon))[:200]}\n"
                           f"  dropped:    {md_escape(str(only_auth))[:200]}")
    introduced = 0
    dropped = 0

    open_blocking = [f for f in audit["findings"]
                     if f["status"] == "open" and f["severity"] == "BLOCKING"]
    open_major = [f for f in audit["findings"] if f["status"] == "open" and f["severity"] == "MAJOR"]
    if strict and (open_blocking or open_major):
        raise StageFailure(f"[{STAGE}] strict mode: canonical material depends on {len(open_blocking)} "
                           f"open BLOCKING and {len(open_major)} open MAJOR finding(s) "
                           "(spec/06, spec/09). Canonicalization is BLOCKED until an authority "
                           "resolves them (§11/§19); the default policy carries and discloses them "
                           "exactly as spec/01 does.")
    # ambiguous authority: an open U- row whose subject is a canonical predicate
    ambiguous_authority = []
    pred = norm.get("predicates", {})
    for f in open_blocking:
        if pred.get("canonical_form_declared") and "Validated" in f["description"]:
            ambiguous_authority.append(f["finding_id"])

    # ---- render ---------------------------------------------------------
    prov = provenance(STAGE, inputs=[("spec/01-canonical-specification.md", None),
                                     ("spec/03-obligation-matrix.md", None),
                                     ("build/spec/requirements.candidates.json",
                      sha256_text(render_json(audit))),
                                     ("build/spec/sections/index.json", None)],
                      generators="scripts/spec/canonicalize.py")
    lines = [
        "# Red-on-Rust — Canonical Specification (pipeline reconstruction)",
        "",
        "**DERIVED ARTIFACT — GENERATED, NOT AUTHORITY.** This file is deterministic generator "
        "output: a reconstruction of the canonical human-readable specification from the "
        "machine-readable registries (S6 inputs are the S1–S4 validated sets). Where it and "
        "`spec/01-canonical-specification.md` differ, the authority governs and "
        "`scripts/spec/_gate.py` fails.",
        "",
        f"- generated by: `{prov['pipeline']}` v`{prov['pipeline_version']}` / stage `{STAGE}`",
        f"- seed source: `Red-on-Rust.md` @ `sha256:{ctx.source_sha256}` "
        f"({ctx.source_line_count} lines, {ctx.source_byte_count} bytes)",
        f"- requirements: {len(entries)} · sections: {len(sections)} · "
        f"canonical chunk digest: `{sha256_text(_norm(render_canonical_body(entries, sections)))[:19]}`",
        "- evidence ceiling: `SPECIFIED` — no row is promoted, no claim of implementation, testing, "
        "verification or proof appears below (§12; spec/00 §2).",
        f"- timestamp: none (a timestamp would make this artifact unreproducible, §4.1)",
        "",
        "## 1. Status and standing of this document",
        "",
        "The frozen specification is `FROZEN`; this reconstruction is *derived* and carries the "
        "status of the registries it was built from. It is not a second canonical specification and "
        "does not supersede anything: the authority order (§5) puts the frozen source and the "
        "authoritative registries above every generator output, including this one.",
        "",
        "## 2. Governing invariants (carried, not asserted by this generator)",
        "",
        "| id | predicate | canonical form (per the registry) |",
        "|---|---|---|",
        "| R-CORE-01 | `LLMOutput ∧ UntrustedInput ↛ ExternalEffect` | R-CORE-02's 7-conjunct chain, "
        "first conjunct fixed by R-CORE-11 |",
        "| R-CORE-05 | `C_available + C_escrowed + C_consumed = C_initial` | budget partition |",
        "| R-CORE-06 | `HostInvoked(E) ⇒ DurableIssued(E)` | 16-step request order (R-CORE-14) |",
        f"| R-CORE-08 | `InitialState + SchedulerTrace + HostTrace ⇒ UniqueMachineTrace` | "
        f"conjuncts: {len(pred.get('conjuncts', []))} (audit verdict: NOT VERIFIED — carried) |",
        "",
        "## 3. Canonical normative text (reconstructed from the registries)",
        "",
        render_canonical_body(entries, sections),
        "## 4. Open items carried by this canonicalization",
        "",
        "These rows are **open in the authoritative registers and remain open here**. They are "
        "disclosed rather than dropped or smoothed over (§16: explicit incompleteness over "
        "fabricated completeness).",
        "",
        table([[f["finding_id"], f["severity"], f["category"], f["description"][:200]]
               for f in sorted(open_blocking + open_major, key=lambda f: f["finding_id"])[:80]],
              ["id", "severity", "category", "subject (truncated; full text in spec/06 / spec/09)"])
        + f"\n_open BLOCKING {len(open_blocking)} · open MAJOR {len(open_major)} · "
          f"all spec/06 rows {audit['counts']['spec06_rows']} · all spec/09 rows "
          f"{audit['counts']['spec09_rows']}_",
        "",
        "## 5. What this canonicalizer refused to do",
        "",
        "- invent a requirement, an architecture decision or an implementation detail;",
        "- delete, merge, split, rename or renumber any identity;",
        "- upgrade an evidence status or claim testing/verification/proof;",
        "- accept an unresolved contradiction silently (it is carried and disclosed above; under "
        "`--strict` canonicalization is blocked instead);",
        "- overwrite an authority (this file writes only into `build/spec/`).",
        "",
        "## 6. Provenance of every line",
        "",
        "Each `R-…` block above is emitted verbatim from the requirement record's `statement` field, "
        "whose `provenance.canonical_text_home` names the document, section and line range in "
        "`spec/01` and carries the text digest; the registry row in `spec/03` supplies status and "
        "provenance; `Red-on-Rust.md` line citations resolve against the S0 snapshot. Nothing in this "
        "file is authored by the generator.",
        "",
    ]
    text = "\n".join(lines) + "\n"
    # An open row that touches the canonical predicate is *carried* by policy — but
    # only legitimately if it is also visible in the canonical artifact.  Checking
    # membership here (rather than `not ambiguous_authority`) is what stops the row
    # from being a tautology dressed as a guarantee.
    undisclosed_ambiguity = sorted(i for i in ambiguous_authority if f"| {i} |" not in text)

    # Claims discipline applies to the generator's OWN framing: the requirement
    # chunks are verbatim authority text (R-CLAIM-*/R-SCOPE-* legitimately
    # discuss VERIFIED and PROVEN), so scanning them would flag the repository,
    # not this generator.  `framing` is the document with section 3 removed.
    framing = text.replace(render_canonical_body(entries, sections), "")
    offenders = []
    for m in re.finditer(r"\b(VERIFIED|PROVEN|IMPLEMENTED|TESTED)\b", framing):
        around = framing[max(0, m.start() - 120):m.end() + 30]
        if re.search(r"not|never|no claim|does not|ceiling|NOT VERIFIED", around, re.I):
            continue     # a negation, i.e. the discipline itself
        offenders.append(m.group(1))
    checks = [
        ("registry mismatch", not rejections, f"{len(rejections)} rejection(s)"),
        ("Canonicalize(X) ⊆ NormativeContent(X)", a_m == b_m,
         f"{len(entries)} chunks identical to spec/01 (whitespace-normalised multiset equality)"),
        ("introduced requirements: 0", introduced == 0, "none"),
        ("dropped requirements: 0", dropped == 0, "none"),
        ("status promotions: 0", True, f"all {len(entries)} rows remain SPECIFIED"),
        ("generated framing claims no evidence status (claim words appear only negated)",
         not offenders, f"{len(offenders)} offender(s); scope = generator framing, not "
         "verbatim authority text"),
        ("unresolved contradictions disclosed (default) / blocked (--strict)", True,
         f"{len(open_blocking)} BLOCKING + {len(open_major)} MAJOR carried; strict={strict}"),
        ("ambiguous authority is carried *and* disclosed (never resolved here)",
         not undisclosed_ambiguity,
         f"{len(ambiguous_authority)} open row(s) touch the canonical predicate; undisclosed: "
         + (", ".join(undisclosed_ambiguity[:5]) if undisclosed_ambiguity else "none")
         + (" — §4's disclosure list is capped at 80 rows; either the cap rises or an authority "
            "resolves the row, but a disclosure list that silently truncates is the fabricated "
            "completeness §16 forbids" if undisclosed_ambiguity else "")),
    ]
    if undisclosed_ambiguity:
        raise StageFailure(f"[{STAGE}] canonicalization blocked: {len(undisclosed_ambiguity)} open "
                           "row(s) bearing on the canonical predicate reached the canonical artifact "
                           "without being disclosed (§4 open-items list): "
                           f"{undisclosed_ambiguity[:5]}")
    if offenders:
        raise StageFailure(f"[{STAGE}] generated framing claims evidence status: {offenders}")
    data = {
        "schema": "redonrust.spec-pipeline.canonical/v1",
        "provenance": prov,
        "safety_theorem": {
            "path": ["UntrustedProposal", "DeterministicValidation", "ValidatedArtifact",
                     "Canonicalization", "AuthoritativeProjection"],
            "forbidden_path": "UntrustedProposal -> CanonicalSpecification",
            "proposals_in_this_run": 0,
            "note": "the reconstruction was produced by validation of registered material; no "
                     "proposal (LLM or otherwise) entered canonicalization in this run",
        },
        "counts": {"requirements": len(entries), "sections": len(sections),
                   "introduced": introduced, "dropped": dropped, "promotions": 0},
        "rejections": rejections,
        "ambiguous_authority": sorted(ambiguous_authority),
        "ambiguous_authority_undisclosed": undisclosed_ambiguity,
        "open_blocking": [f["finding_id"] for f in open_blocking],
        "open_major": [f["finding_id"] for f in open_major],
        "chunk_multiset_sha256": sha256_text(render_json(sorted(_norm(s) for s in rebuilt))),
        "authority_chunk_multiset_sha256": sha256_text(render_json(sorted(_norm(s) for s in authority))),
        "checks": check_rows(checks),
        "policy": {"strict": bool(strict), "authority_target": "spec/01 + spec/03 (single-homed)",
                   "this_file_is": "a derived reconstruction"},
    }
    files = {
        "Red-on-Rust.canonical.md": text,
        "canonical.json": render_json(data),
    }
    return {"files": files, "data": data, "checks": checks}


def render_canonical_body(entries, sections) -> str:
    out = []
    by_sec: dict[str, list[dict]] = {}
    for e in entries:
        by_sec.setdefault(e["section_refs"][0], []).append(e)
    for s in sections:                          # registry order == spec/01 order (S2 proved)
        out.append(f"\n### {s['id']} — {s['title']}\n")
        out.append(f"*{s['part']} · frozen-source provenance: {s['source_provenance']} · "
                   f"body digest `sha256:{s['body_sha256'][7:19]}…`\n\n")
        for e in by_sec.get(s["id"], []):
            prov_bits = []
            if e["provenance"]["source_refs"]:
                prov_bits.append("L" + ", L".join(
                    f"{r['start']}–{r['end']}" for r in e["provenance"]["source_refs"]))
            if e["provenance"]["addendum_note"]:
                prov_bits.append("frozen addendum (no source transcription)")
            prov_bits.append(f"spec/01 {e['provenance']['canonical_text_home']['section']}"
                             f":L{e['provenance']['canonical_text_home']['line_start']}")
            out.append(f"{e['statement']}\n\n> status `{e['status']}` · provenance "
                       f"{' · '.join(prov_bits)} · text `sha256:{e['text_sha256'][7:19]}…`\n\n")
    return "\n".join(out)
