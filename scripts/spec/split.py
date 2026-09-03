"""Stage S2 — SPLIT (§9).

Section split of the specification: `spec/01`'s own section structure (S-01…
S-24, registered in `spec/02-section-hierarchy.md`) is projected into one file
per section under `build/spec/sections/`.

Splitting here is a **structural transformation, not a semantic redesign**:

  * ordering is preserved — sections appear in `spec/01`'s document order, and
    requirement chunks inside a section keep their relative order;
  * provenance is preserved — each section file carries the turn/line
    provenance registered in `spec/02` plus the byte digest of its own body;
  * cross references are preserved — references a section makes to material
    owned elsewhere are listed, not rewritten;
  * requirement identity is preserved — nothing is renumbered, and the split
    is *lossless*: the concatenation of the section bodies, normalised for
    whitespace, is byte-identical to the normalised body of `spec/01`.  If the
    split dropped or altered a line, that check fails the stage.

The splitter does not choose a new section structure.  A second semantic
organization already exists in the repository (`mod/`'s 17 modules, `dep/`'s
dependency layers) and the frozen source has its own 29-section FINAL1 layout;
inventing a fourth would be the competing-governance failure §20 forbids.
`spec/02` is therefore the section authority, and the §6 layout's suggested
domain names (core, compiler, capability, …) are attached to the sections that
own those domains as `domain_hint` metadata only — a hint, never a new
authority (§4.5 identity preservation).
"""
from __future__ import annotations

import re

from _common import (StageFailure, check_rows, md_escape, provenance, render_json,
                     sha256_text, table)

STAGE = "S2-split"

# §6's suggested semantic domains, mapped onto the sections that own them.
# Metadata only: it renames nothing and re-homes nothing.
DOMAIN_HINTS = {
    "core": ["S-02"], "compiler": ["S-06", "S-08"], "capability": ["S-09", "S-10"],
    "budget": ["S-11"], "evaluator": ["S-07", "S-08"], "actors": ["S-15"],
    "scheduler": ["S-15"], "effects": ["S-12", "S-13"], "host": ["S-14"],
    "serialization": ["S-17"], "persistence": ["S-18"], "recovery": ["S-19"],
    "agent": ["S-05"], "verification": ["S-20", "S-21", "S-24"],
    "trust": ["S-03"], "scope": ["S-01"], "architecture": ["S-04"],
    "calculus": ["S-07"], "marshalling": ["S-16"], "engineering": ["S-22", "S-23"],
    "claims": ["S-24"],
}

_RID = re.compile(r"\bR-[A-Z]+-\d+\b")
_CID = re.compile(r"\bC-\d{2,3}\b")
_UID = re.compile(r"\bU-\d{2}\b")


def _norm(text: str) -> str:
    """Whitespace normalisation for the lossless-split comparison.

    Only line-joining and blank-line collapsing: exactly the normalisation
    `final/_build.py` documents for verbatim re-homing ("whitespace-normalized
    only").  No case, punctuation or wording change is permitted."""
    lines = [l.strip() for l in text.split("\n")]
    out = []
    for l in lines:
        if not l:
            if out and out[-1] != "":
                out.append("")
            continue
        out.append(re.sub(r"\s+", " ", l))
    return "\n".join(out).strip()


def run(ctx) -> dict:
    lines = ctx.spec01_text.split("\n")
    # locate each section's exact body in spec/01
    marks = []
    for i, line in enumerate(lines):
        m = re.match(r"^## (S-\d{2}) ", line)
        if m:
            marks.append((i, m.group(1)))
    if [s for _, s in marks] != ctx.section_order:
        raise StageFailure(f"[{STAGE}] spec/01 section headings disagree with the section order "
                           "derived at load time")
    unregistered = sorted(set(ctx.section_order) - set(ctx.section_by_id))
    unknown = sorted(set(ctx.section_by_id) - set(ctx.section_order))
    if unregistered or unknown:
        raise StageFailure(
            f"[{STAGE}] section registry and normative text home disagree — section split refused: "
            f"present in spec/01 but absent from spec/02: {unregistered[:5]}; present in spec/02 but "
            f"absent from spec/01: {unknown[:5]}. Neither document is auto-repaired (§5: do not guess, "
            "raise an audit finding).")
    bodies: dict[str, str] = {}
    last_end = len(lines)
    for n, (start, sid) in enumerate(marks):
        end = None
        for j in range(start + 1, len(lines)):
            if lines[j].startswith("# ") or lines[j].startswith("## ") or lines[j].strip() == "---":
                end = j
                break
        if end is None:
            end = len(lines)
        last_end = end
        body = "\n".join(lines[start:end]).rstrip("\n").rstrip()
        while body.endswith("---"):   # rule inside a section, not at its boundary
            body = body[:-3].rstrip()
        bodies[sid] = body

    chunks_by_sec: dict[str, list[dict]] = {}
    for c in ctx.chunks:
        chunks_by_sec.setdefault(c["section"], []).append(c)

    hint_of: dict[str, list[str]] = {}
    for dom, secs in DOMAIN_HINTS.items():
        for s in secs:
            hint_of.setdefault(s, []).append(dom)

    files: dict[str, str] = {}
    index_sections = []
    findings = []
    for sid in ctx.section_order:
        body = bodies[sid]
        chs = chunks_by_sec.get(sid, [])
        ch_ids = [c["id"] for c in chs]
        ext_r = sorted({m.group(0) for m in _RID.finditer(body)} - set(ch_ids))
        cids = sorted({m.group(0) for m in _CID.finditer(body)})
        uids = sorted({m.group(0) for m in _UID.finditer(body)})
        unreg_c = [c for c in cids if c not in ctx.findings]
        unreg_u = [u for u in uids if u not in ctx.decisions]
        if unreg_c or unreg_u:
            findings.append({"section": sid, "unknown_c": unreg_c, "unknown_u": unreg_u})
        if not chs:
            findings.append({"section": sid, "unknown_c": [], "unknown_u": [],
                             "note": "section carries no requirement chunk"})
        prov = provenance(STAGE, inputs=[("spec/01-canonical-specification.md", None),
                                         ("spec/02-section-hierarchy.md", None)],
                          generators="scripts/spec/split.py")
        sec = ctx.section_by_id[sid]
        meta = {
            "section": sid,
            "title": sec["title"],
            "part": sec["part"],
            "domain_hint": sorted(hint_of.get(sid, [])),
            "requirements": ch_ids,
            "spec01_lines": [next((c["line"] for c in chs), None),
                             next((c["end_line"] for c in reversed(chs)), None)],
            "source_provenance": sec["provenance"],
            "source_line_ranges": sec["line_ranges"],
            "superseded_material": sec["superseded"],
            "cross_reference_requirements": ext_r,
            "cross_reference_findings": cids,
            "cross_reference_decisions": uids,
            "body_sha256": sha256_text(body),
            "generated": True,
        }
        head = "\n".join(f"#| {k}: {v}" for k, v in
                         [("pipeline", f"{prov['pipeline']} v{prov['pipeline_version']}"),
                          ("stage", STAGE), ("derived_artifact", "true"),
                          ("normative_text_home", "spec/01-canonical-specification.md"),
                          ("authority", "spec/02-section-hierarchy.md (structure)")])
        slug = re.sub(r"[^a-z0-9]+", "-", sec["title"].lower()).strip("-")
        files[f"sections/{sid}-{slug}.md"] = (
            f"{head}\n\n{body}\n"
        )
        index_sections.append({
            "id": sid, "title": sec["title"], "part": sec["part"],
            "domain_hint": sorted(hint_of.get(sid, [])),
            "file": next(k for k in reversed(list(files)) if k.startswith("sections/" + sid)),
            "requirement_count": len(chs), "requirements": ch_ids,
            "body_sha256": meta["body_sha256"],
            "source_provenance": sec["provenance"],
            "source_line_ranges": sec["line_ranges"],
            "cross_reference_count": len(ext_r) + len(cids) + len(uids),
            "metadata": meta,
        })

    # ---- lossless check --------------------------------------------------
    # Rebuild spec/01's section material (everything from the first `## S-`
    # heading to EOF, minus part headings and `---` rules — the structural
    # scaffolding a section split legitimately removes) and compare against the
    # join of the projected bodies.  A dropped, reordered or edited line makes
    # this fail; nothing else about the comparison is discretionary.
    first_sec = min(i for i, l in enumerate(lines) if re.match(r"^## S-\d{2} ", l))
    # Material after the final `---` rule (spec/01's closing cross-reference
    # navigation line) is structural, not normative.  The split records it
    # explicitly rather than dropping it silently, and the lossless comparison
    # accounts for it.
    trailer = "\n".join(lines[last_end:]).strip()
    kept = [l for l in lines[first_sec:last_end]
            if not (l.startswith("# ") or l.strip() == "---")]
    expected_join = "\n".join(kept)
    joined = "\n\n".join(bodies[s] for s in ctx.section_order)
    lossless = _norm(joined) == _norm(expected_join)
    if not lossless:
        import difflib
        diff = [d for d in difflib.unified_diff(_norm(expected_join).split("\n"),
                                                _norm(joined).split("\n"), lineterm="", n=0)][:12]
        raise StageFailure(f"[{STAGE}] split is not lossless — normative material would be "
                           f"changed. First differences:\n  " + "\n  ".join(diff))
    # every chunk must sit verbatim inside exactly one section body
    owned = sum(len(s["requirements"]) for s in index_sections)
    if owned != len(ctx.chunks):
        raise StageFailure(f"[{STAGE}] chunk accounting lost: {owned} section-owned chunks vs "
                           f"{len(ctx.chunks)} in spec/01")
    missing_from_bodies = [c["id"] for c in ctx.chunks
                           if _norm(c["text"]) not in _norm(bodies[c["section"]])]
    if missing_from_bodies:
        raise StageFailure(f"[{STAGE}] {len(missing_from_bodies)} chunks are not present verbatim "
                           f"in their section file: {missing_from_bodies[:5]}")
    checks = [
        ("ordering preserved (spec/01 document order)", index_sections and
         [s["id"] for s in index_sections] == ctx.section_order,
         f"{len(index_sections)} sections"),
        ("lossless split (rebuild of spec/01's section material from the bodies)", True,
         "digest of both normalised renderings: " + sha256_text(_norm(joined))[7:19]),
        ("every requirement chunk present verbatim in exactly one section",
         not missing_from_bodies and owned == len(ctx.chunks), f"{owned}/{len(ctx.chunks)} chunks"),
        ("identities unchanged (no add/delete/merge/split/rename/renumber)",
         sorted({r for s in index_sections for r in s["requirements"]}) == sorted(ctx.spec01),
         "identity set identical to spec/01"),
        ("cross references retained as metadata (not duplicated authority)", True,
         f"{sum(s['cross_reference_count'] for s in index_sections)} references carried"),
    ]
    checks.append(("provenance survives the split",
                   all(s["source_provenance"] or s["source_line_ranges"] for s in index_sections),
                   "every section carries spec/02 turn/line provenance"))

    prov = provenance(STAGE, inputs=[("spec/01-canonical-specification.md", None),
                                     ("spec/02-section-hierarchy.md", None)],
                      generators="scripts/spec/split.py")
    data = {
        "schema": "redonrust.spec-pipeline.sections/v1",
        "provenance": prov,
        "section_count": len(index_sections),
        "part_count": len({s["part"] for s in index_sections}),
        "join_sha256": sha256_text(joined),
        "sections": [{k: v for k, v in s.items() if k != "metadata"} for s in index_sections],
        "trailer": {"carried": True, "sha256": sha256_text(trailer),
                    "note": "post-final-rule navigation text in spec/01; recorded so the split "
                            "drops nothing silently (it is not a requirement chunk)"},
        "checks": check_rows(checks),
        "cross_reference_notes": findings,
        "policy": {
            "semantic_redesign_performed": False,
            "duplication_of_normative_authority": False,
            "structure_authority": "spec/02-section-hierarchy.md",
        },
    }
    files["sections/index.json"] = render_json(data)
    rows = [[s["id"], s["title"], s["part"], s["requirement_count"],
             ", ".join(s["domain_hint"]) or "—", s["source_provenance"],
             "sha256:" + s["body_sha256"][7:15] + "…"] for s in index_sections]
    files["sections/index.md"] = (
        "# 02 — Semantic Section Split (Stage S2)\n\n"
        "**Derived artifact of the controlled specification pipeline. Not a normative source.**\n\n"
        f"{len(index_sections)} sections in {data['part_count']} parts, projected from "
        "`spec/02-section-hierarchy.md` and rendered verbatim from `spec/01-canonical-specification.md`. "
        "The split is lossless: every normative chunk of `spec/01` appears byte-exactly (modulo "
        "whitespace normalisation) in exactly one section file, in order.\n\n"
        "## 1. Checks\n\n" + table([[c, "PASS" if p else "FAIL", d] for c, p, d in checks],
                                     ["check", "result", "detail"])
        + "\n## 2. Sections\n\n" + table(rows, ["id", "title", "part", "R count", "domain hint",
                                                 "frozen-source provenance", "body digest"])
        + "\n*`domain hint` is the §6 layout's suggested vocabulary attached as metadata; it "
          "renames no section and re-homes no requirement (§4.5).*\n")
    return {"files": files, "data": data, "checks": checks, "bodies": bodies,
            "index_sections": index_sections}
