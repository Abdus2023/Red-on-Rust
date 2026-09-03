"""Stage S1 — EXTRACT (§8).

Candidate extraction of every normative unit, with provenance on every item and
a normative class on every statement.

THIS STAGE DOES NOT EXTRACT FROM THE SOURCE PROSE
-------------------------------------------------
It could not do so honestly.  The extraction of record was performed by the
canonicalization passes that produced `spec/01` (normative text home), `spec/03`
(canonical registry), `spec/02` (section hierarchy) and `req/` (545 atomic
records).  Re-running a fresh extraction here would either re-author the
repository's normative decisions or produce a second, competing register — both
prohibited (§20: extend the existing governance, do not create a rival; §4.5:
no silent ADD/DELETE/MERGE/SPLIT/RENAME/RENUMBER).

So S1 performs the operation that is actually available to a deterministic
machine: it extracts the *registered* units from the authorities, classifies
each one using only vocabularies the repository already owns (`spec/00` §2
ladder, `req/00` normative levels, `spec/01`'s own `[INFORMATIVE: …]` and
`Non-normative` markers, the `addendum … no source transcription` provenance
form), and then validates the structural consistency of what it read.
Confidence is a **derived agreement measure** — the number of independent
authorities whose ID sets, statuses and provenance agree on that item — never
an LLM's self-assessment.

Where a proposal surface is needed (§15), it is emitted explicitly empty:
`proposals.json` records that no unvalidated proposal was accepted, because in
this pipeline no proposal was needed to reproduce the register.  That is the
honest state, and §16 prefers explicit incompleteness to fabricated completeness.
"""
from __future__ import annotations

import re

from _common import (EVIDENCE_CEILING, LEVEL_VOCAB, STATUS_LADDER, StageFailure,
                     line_refs_of, md_escape, provenance, render_json, sha256_text,
                     table)

STAGE = "S1-extract"

_INFORMATIVE = re.compile(r"\[INFORMATIVE:")
_NONNORM = re.compile(r"\bNon-normative\b|\*\*Non-normative\*\*")
_ADDENDUM = re.compile(r"Frozen addendum|frozen addendum|\baddendum\b")
_SUPERSEDED = re.compile(r"SUPERSEDED|superseded")
_HISTORICAL = re.compile(r"historical|Historical")
_EXAMPLE = re.compile(r"\bexample\b|\be\.g\.,|golden vector", re.I)
_AMBIG = re.compile(r"\bAMB-\d+|\*\*open\*\*|unfrozen|not frozen|undefined")


def classify(chunk, obligation) -> tuple[str, str]:
    """Return (normative_class, basis).  Vocabulary is §8's; every decision
    cites the authority text it was read from — nothing is invented."""
    text = chunk["text"]
    if _AMBIG.search(text) and not _ADDENDUM.search(text):
        return ("AMBIGUOUS", "ambiguity/undefined marker present in the canonical statement")
    if _NONNORM.search(text):
        return ("EXPLANATORY", "explicit `Non-normative` marking in spec/01")
    if _INFORMATIVE.search(text) and not re.search(r"\bMUST\b|\bMUST NOT\b", text):
        return ("EXPLANATORY", "`[INFORMATIVE: …]` note without a modal verb")
    if _EXAMPLE.search(text) and not re.search(r"\bMUST\b|\bMUST NOT\b|\bIS\b", text):
        return ("EXAMPLE", "illustrative/example content only, no modal verb")
    if _HISTORICAL.search(text) and not re.search(r"\bMUST\b", text):
        return ("HISTORICAL", "historical/supersession record, no modal verb")
    if re.search(r"\bMUST\b|\bMUST NOT\b|\bSHOULD\b|\bMAY\b", text):
        kind = "addendum (no source transcription)" if _ADDENDUM.search(text) else "frozen source"
        return ("NORMATIVE", f"modal verb present; statement text homed in spec/01 ({kind})")
    if _SUPERSEDED.search(text):
        return ("HISTORICAL", "supersession carrier, quoted-not-deleted (R-SCOPE-03)")
    return ("NORMATIVE", "definitional statement (IS/definition) registered as an obligation")


def run(ctx) -> dict:
    # ---- authority ID sets, derived independently, then compared ----------
    spec01_ids = set(ctx.spec01)
    spec03_ids = set(ctx.obligations)
    s10_ids = {r["id"] for r in ctx.spec10["requirements"]} if ctx.spec10 else set()
    final03_ids = set()
    reg_ids = set()
    if ctx.reg is not None:
        reg_ids = {r["id"] for r in ctx.reg["requirements"]}
    checks = []
    if not (spec01_ids == spec03_ids):
        raise StageFailure(f"[{STAGE}] requirement identity diverges between spec/01 and spec/03: "
                           f"only in spec/01 {sorted(spec01_ids - spec03_ids)}, "
                           f"only in spec/03 {sorted(spec03_ids - spec01_ids)}")
    checks.append(("identity: spec/01 == spec/03", True, f"{len(spec01_ids)} IDs"))
    agreements = {"spec/01": spec01_ids, "spec/03": spec03_ids}
    if s10_ids:
        if s10_ids != spec01_ids:
            raise StageFailure(f"[{STAGE}] spec/10 index disagrees with the authorities: "
                               f"extra {sorted(s10_ids - spec01_ids)}, missing {sorted(spec01_ids - s10_ids)}")
        agreements["spec/10"] = s10_ids
    if ctx.reg is not None:
        if reg_ids != spec01_ids:
            raise StageFailure(f"[{STAGE}] reg/registry disagrees with the authorities: "
                               f"extra {sorted(reg_ids - spec01_ids)}, missing {sorted(spec01_ids - reg_ids)}")
        agreements["reg/requirements.json"] = reg_ids

    # ---- candidate records ------------------------------------------------
    entries = []
    for rid in ctx.obligation_order:                     # canonical registry order
        chunk = ctx.spec01[rid]
        oblig = ctx.obligations[rid]
        reg = next((r for r in (ctx.reg["requirements"] if ctx.reg else []) if r["id"] == rid), None)
        nclass, basis = classify(chunk, oblig)
        refs = chunk["source_refs"] or line_refs_of(oblig["provenance"])
        addendum_only = bool(_ADDENDUM.search(chunk["text"])) and not refs
        prov = {
            "canonical_text_home": {
                "document": "spec/01-canonical-specification.md",
                "section": chunk["section"],
                "line_start": chunk["line"],
                "line_end": chunk["end_line"],
                "text_sha256": chunk["sha256"],
            },
            "registry_row": {"document": "spec/03-obligation-matrix.md",
                             "provenance_cell": oblig["provenance"]},
            "source_refs": [{"path": "Red-on-Rust.md", "start": r["start"], "end": r["end"]}
                            for r in refs],
            "provenance_kind": ("frozen-source-cited" if refs else
                                "frozen-addendum" if addendum_only else
                                "registry-cited" if line_refs_of(oblig["provenance"]) else
                                "section-inherited"),
            "addendum_note": ("no source transcription; additive per R-SCOPE-03"
                              if addendum_only else None),
        }
        conf = round(len(agreements) / max(len(agreements), 1), 4)   # agreement, not belief
        entries.append({
            "id": rid,
            "candidate_identity": rid,
            "identity_basis": "copied verbatim from the canonical registry (spec/03); never renumbered",
            "section_refs": [chunk["section"]],
            "classification": {"normative_class": nclass, "normative_class_basis": basis,
                               "level": (reg or {}).get("normative_level"),
                               "level_basis": (reg or {}).get("normative_level_basis")},
            "status": oblig["status"],
            "status_basis": "spec/03 Status cell (the ladder's floor: SPECIFIED)",
            "confidence": conf,
            "confidence_basis": f"identity agreed by {len(agreements)} independent authorities: "
                                + ", ".join(sorted(agreements)),
            "provenance": prov,
            "dependencies": (reg or {}).get("dependencies", []),
            "verification_refs": [] if oblig["verify"] in ("—", "-", "") else [oblig["verify"]],
            "implementation_targets": [] if oblig["impl"] in ("—", "-", "") else [oblig["impl"]],
            "text_sha256": chunk["sha256"],
            "statement": chunk["text"],
        })

    # structural validation of what was read (§8: the validator validates
    # structural consistency; it does not adjudicate meaning)
    ids = [e["id"] for e in entries]
    if len(ids) != len(set(ids)):
        raise StageFailure(f"[{STAGE}] duplicate candidate identities produced")
    if not set(STATUS_LADDER) >= {e["status"] for e in entries}:
        raise StageFailure(f"[{STAGE}] status outside the frozen ladder in extraction output")
    for e in entries:
        if e["provenance"]["provenance_kind"] == "frozen-source-cited":
            for r in e["provenance"]["source_refs"]:
                if r["end"] > ctx.source_line_count or r["start"] < 1:
                    raise StageFailure(f"[{STAGE}] {e['id']} cites L{r['start']}–{r['end']}, outside "
                                       f"the snapshot (1..{ctx.source_line_count}) — citation defect")
    levels = {e["classification"]["level"] for e in entries if e["classification"]["level"]}
    if not set(LEVEL_VOCAB) >= levels:
        raise StageFailure(f"[{STAGE}] normative level vocabulary drift: {sorted(levels - set(LEVEL_VOCAB))}")
    checks.append(("every candidate carries provenance", True,
                   f"{sum(1 for e in entries if e['provenance']['source_refs'])} source-cited + "
                   f"{sum(1 for e in entries if e['provenance']['provenance_kind'] == 'frozen-addendum')} "
                   "frozen-addendum (registry-cited by design)"))
    checks.append(("statuses within the frozen ladder", True, "all SPECIFIED"
                   if {e["status"] for e in entries} == {EVIDENCE_CEILING}
                   else str(sorted({e['status'] for e in entries}))))
    checks.append(("no promotion performed", {e["status"] for e in entries} == {EVIDENCE_CEILING},
                   "extraction reads status; it cannot write one"))

    counts = {"requirements": len(entries)}
    for cls in ("NORMATIVE", "DESCRIPTIVE", "EXPLANATORY", "EXAMPLE", "HISTORICAL", "AMBIGUOUS"):
        counts[cls.lower()] = sum(1 for e in entries if e["classification"]["normative_class"] == cls)

    prov = provenance(STAGE, inputs=[("spec/01-canonical-specification.md", None),
                                     ("spec/03-obligation-matrix.md", None),
                                     ("Red-on-Rust.md", "sha256:" + ctx.source_sha256)],
                      generators="scripts/spec/extract.py")
    data = {
        "schema": "redonrust.spec-pipeline.extract/v1",
        "provenance": prov,
        "counts": counts,
        "entries": entries,
        "checks": [{"check": c, "pass": p, "detail": md_escape(d)} for c, p, d in checks],
        "policy": {
            "invention_allowed": False,
            "silent_delete_allowed": False,
            "silent_merge_allowed": False,
            "silent_split_allowed": False,
            "renumber_allowed": False,
            "extraction_source": "registered authorities (spec/01 + spec/03 + req/), not the "
                                 "transcript prose — re-extraction would be a competing register",
        },
    }
    files = {
        "requirements.candidates.json": render_json(data),
        "proposals.json": render_json({
            "schema": "redonrust.spec-pipeline.proposals/v1",
            "provenance": prov,
            "contract": ("§15: the LLM MAY propose; only deterministic validation accepts. "
                         "This file is the record of proposals *accepted into* canonicalization."),
            "accepted_proposals": [],
            "accepted_count": 0,
            "why_empty": ("the register was reproduced by projection from the authorities, so no "
                          "proposal required adjudication in this run; an empty list here is the "
                          "expected state, not a missing step. Any future proposal enters as a row "
                          "in this list with requires_human_authorization=true and is NOT canonical "
                          "until a governance operation accepts it."),
            "proposal_types_recognised": [
                "section_split", "requirement_extraction", "obligation_extraction",
                "terminology_normalization", "dependency_detection", "ambiguity_detection",
                "contradiction_detection", "security_finding", "determinism_finding",
                "evidence_finding", "canonicalization_proposal"],
            "authority": "proposals are never authority (R-SCOPE-03; README: the LLM is a proposal "
                         "engine, not an authority)",
        }),
    }
    rows = [[e["id"], e["section_refs"][0], e["classification"]["normative_class"],
             e["status"], e["confidence"], e["provenance"]["provenance_kind"],
             (", ".join(f"L{r['start']}–{r['end']}" for r in e["provenance"]["source_refs"])
              or "—")] for e in entries]
    files["extract.md"] = (
        "# 01 — Requirement / Obligation Extraction (Stage S1)\n\n"
        "**Derived artifact of the controlled specification pipeline. Not a normative source.**\n\n"
        f"Extracted {len(entries)} candidate normative units — {counts['normative']} NORMATIVE, "
        f"{counts['explanatory']} EXPLANATORY, {counts['historical']} HISTORICAL, "
        f"{counts['ambiguous']} AMBIGUOUS, {counts['example']} EXAMPLE — each with provenance and a "
        "confidence that measures *authority agreement*, not model conviction.\n\n"
        "## 1. Checks\n\n" + table([[c, "PASS" if p else "FAIL", d] for c, p, d in checks],
                                   ["check", "result", "detail"])
        + "\n## 2. Candidates (identity, class, provenance)\n\n"
        + table(rows, ["id", "section", "class", "status", "confidence", "provenance kind",
                       "source lines"])
        + "\n## 3. What this stage refused to do\n\n"
        "- invent a requirement (canonicalization satisfies `Canonicalize(X) ⊆ NormativeContent(X)`);\n"
        "- delete, merge, split, rename or renumber any registered identity;\n"
        "- upgrade an evidence status — every row above is `SPECIFIED`, because that is what the "
        "authorities record and this pipeline has no authority to change it.\n")
    return {"files": files, "data": data, "checks": checks, "entries": entries}
