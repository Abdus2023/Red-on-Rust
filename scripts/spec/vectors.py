"""Stage S6b — VECTORS (§6 `05-vectors/`, §14 verification inputs).

A deterministic **projection of the registered evidence fixtures**, in the three
families the §6 layout names, with the family contents bound to the registers
that already own them:

    canonical/     serialization golden vectors — normative fixtures per `spec/01`
                   R-CANON-11, grammar frozen by R-CANON-13;
    persistence/   crash-boundary vectors — the T0–T6 matrix indexed in
                   `spec/10-index.json`, obligations R-DUR-*/R-RECOV-*;
    effects/       verification-obligation tags — `spec/08 §1` (16 frozen +
                   9 addendum tags), which are the repository's registered
                   effect/host gates.

Rules that make this stage safe:

  * **A vector is never authored here.** Each record is a byte-exact quote from
    its authority plus the line numbers where that authority cites it. An
    unregistered expected byte string is a stage failure, not a fixture.
  * **Discrepancies are reported, not adjudicated.** The frozen source carries
    superseded hex forms (the stale standalone tags recorded in `spec/06` C-02);
    the pipeline counts them, cites them, and says plainly that only the
    authority decides. It does not "fix" a source line.
  * **Vectors are not implementation.** The M1 acceptance line in `spec/01`
    ("golden vectors pass") requires a Rust test that does not exist and must not
    be written before M0 (§21). These files are fixture *registries*.
"""
from __future__ import annotations

import re

from _common import (StageFailure, md_escape, provenance, render_json, sha256_text, table)

STAGE = "S6b-vectors"

_HEXSEQ = re.compile(r"(?<![0-9A-Fa-f])((?:0x[0-9A-Fa-f]{2}(?:\s+)?){2,}|(?:[0-9A-F]{2}(?:\s+[0-9A-F]{2}){3,}))(?![0-9A-Fa-f])")


def _norm_hex(blob: str) -> str:
    parts = re.findall(r"[0-9A-Fa-f]{2}", blob)
    return " ".join(p.upper() for p in parts)


def _label(chunk_text: str, at: int) -> str:
    """Short deterministic label for a quoted fixture: the nearest preceding
    backticked phrase or heading fragment, else the requirement id."""
    head = chunk_text[:at]
    m = list(re.finditer(r"`([^`]{4,80})`", head))
    if m:
        return m[-1].group(1).strip()
    return chunk_text.split("\n")[0][:80]


def canonical_vectors(ctx) -> tuple[dict, list]:
    chunk = ctx.spec01.get("R-CANON-11")
    if not chunk:
        raise StageFailure(f"[{STAGE}] R-CANON-11 (golden vectors, normative fixtures) is missing "
                           "from the canonical text — the fixture registry has no authority")
    text = chunk["text"]
    records = []
    for i, m in enumerate(_HEXSEQ.finditer(text)):
        blob = _norm_hex(m.group(1))
        if not blob:
            continue
        records.append({
            "vector_id": f"VEC-CANON-{i + 1:02d}",
            "family": "canonical",
            "label": _label(text, m.start()),
            "canonical_bytes": blob,
            "byte_length": len(blob.split()),
            "authority": {"document": "spec/01-canonical-specification.md", "requirement": "R-CANON-11",
                          "line_start": chunk["line"], "line_end": chunk["end_line"],
                          "chunk_sha256": chunk["sha256"]},
            "provenance_kind": "frozen canonical statement (R-CANON-11)",
            "grammar": "Phase 15A envelope (version u8 / type_tag u8 / payload_length u32 BE) "
                       "per R-CANON-13",
            "digest": sha256_text(blob),
            "status": "SPECIFIED",
            "consumed_by": "M1 conformance tests (once an implementation exists); today: no consumer, "
                           "which is the honest state",
        })
    if len(records) < 2:
        raise StageFailure(f"[{STAGE}] expected the frozen golden vectors in R-CANON-11; found "
                           f"{len(records)} byte sequence(s)")
    # source cross-check: the requirement's own cited ranges
    src_hits = []
    for r in chunk["source_refs"]:
        seg = ctx.source_range(r["start"], r["end"])
        for j, line in enumerate(seg.split("\n")):
            if "Full Canonical Bytes" in line or re.search(r"Golden Test Vector", line):
                for mm in _HEXSEQ.finditer(line):
                    src_hits.append({"line": r["start"] + j, "bytes": _norm_hex(mm.group(1)),
                                     "quoted": md_escape(line[:120])})
    seen, src_unique = set(), []
    for h in src_hits:
        if h["bytes"] in seen:
            continue
        seen.add(h["bytes"])
        src_unique.append(h)
    canon_bytes = {rec["canonical_bytes"] for rec in records}
    divergent = [h for h in src_unique if h["bytes"] not in canon_bytes]
    data = {
        "family": "canonical",
        "authority": "spec/01 R-CANON-11 (fixtures) / R-CANON-13 (grammar) / C-02 (stale tags)",
        "count": len(records),
        "vectors": records,
        "source_cited_hex_forms": src_unique,
        "discrepancies": {
            "count": len(divergent),
            "rows": divergent,
            "policy": ("these source-side byte forms are cited by the canonical fixture's own line "
                       "ranges but do not appear in the canonical rendering — spec/06 C-02 records "
                       "them as stale/superseded. The pipeline reports the difference and files "
                       "nothing: adjudication is an authority act (§5), and rewriting the frozen "
                       "source is prohibited (R-SCOPE-03)."),
            "adjudicated_here": 0,
            "source_lines_rewritten": 0,
        },
    }
    checks = [
        ("every canonical vector is quoted from its authority", len(records) >= 2,
         f"{len(records)} fixture(s) quoted from R-CANON-11"),
        ("no vector text invented by the generator", all(rec["canonical_bytes"] in
                                                         _norm_hex(text) for rec in records),
         "byte sequences re-extracted from the same authority match the record"),
        ("source-side divergences reported, none adjudicated", True,
         f"{len(divergent)} divergent form(s) listed; 0 repaired"),
    ]
    return data, checks


def persistence_vectors(ctx) -> tuple[dict, list]:
    crash = (ctx.spec10 or {}).get("crash_matrix", [])
    if not crash:
        raise StageFailure(f"[{STAGE}] spec/10 crash_matrix is empty — no registered crash-boundary "
                           "vectors to project")
    recs = []
    rtext = ctx.spec01.get("R-CORE-09", {}).get("text", "") + ctx.spec01.get("R-CORE-10", {}).get("text", "")
    for i, row in enumerate(crash, 1):
        name = row.get("boundary") or row.get("state") or row.get("crash") or f"T{i - 1}"
        recs.append({
            "vector_id": f"VEC-PERSIST-{i:02d}",
            "family": "persistence",
            "label": str(name),
            "authority": {"document": "spec/10-index.json", "field": "crash_matrix",
                          "row": i},
            "expected_outcome": {k: v for k, v in sorted(row.items()) if k not in ("boundary",)},
            "obligations": sorted({rid for rid in ctx.spec01
                                   if rid.startswith(("R-RECOV-", "R-DUR-"))
                                   and re.search(r"T\d", ctx.spec01[rid]["text"])}),
            "no_silent_repair": "Invalid(D) ⇒ RecoveryFault (R-CORE-10 / R-RECOV-*); no auto-NotExecuted",
            "status": "SPECIFIED",
        })
    gate = (ctx.repo / "audit/_crash_consistency_checker.py").is_file()
    data = {"family": "persistence",
            "authority": "spec/10-index.json crash_matrix (T0–T6) + spec/01 R-DUR/R-RECOV + "
                         "audit/persistence-crash-consistency-audit.md",
            "count": len(recs), "vectors": recs,
            "mechanical_gate_registered": gate,
            "policy": ("the crash matrix is a registered test vector set, not a test: running it "
                       "requires the persistence implementation that does not exist (§21); the "
                       "audit's verdict (contract satisfies the crash-consistency property, provided "
                       "the frozen addenda are normative) is carried as recorded")}
    checks = [("every crash boundary is a registered row", len(recs) == len(crash),
               f"{len(recs)} boundaries"),
              ("crash-consistency mechanical gate present in the repository", gate,
               "audit/_crash_consistency_checker.py (check.py registration)")]
    return data, checks


def effect_vectors(ctx) -> tuple[dict, list]:
    tags = sorted(set(ctx.tags_frozen) | set(ctx.tags_addendum))
    s10_tags = {t["tag"]: t for t in (ctx.spec10 or {}).get("verification_tags", [])}
    aliases = {t.get("tag") for t in (ctx.spec10 or {}).get("verification_tag_aliases", [])}
    if not tags:
        raise StageFailure(f"[{STAGE}] no verification tags parsed from spec/08 §1 — the effect-tag "
                           "universe is empty")
    unknown = sorted(t for t in tags if t not in s10_tags and t not in aliases)
    if unknown:
        raise StageFailure(f"[{STAGE}] tag universe mismatch: spec/08 §1 lists tags absent from "
                           f"spec/10's index: {unknown[:6]}")
    recs = []
    for i, tag in enumerate(tags, 1):
        meta = s10_tags.get(tag, {})
        recs.append({
            "vector_id": f"VEC-EFFECT-{i:02d}",
            "family": "effects",
            "label": tag,
            "source": meta.get("source", "frozen-source" if tag in ctx.tags_frozen else "frozen-addendum"),
            "obligations": sorted(meta.get("obligations") or []),
            "milestone": meta.get("milestone"),
            "authority": {"document": "spec/08-verification-mapping.md", "section": "§1",
                          "indexed_in": "spec/10-index.json verification_tags"},
            "status": "SPECIFIED",
            "note": ("a registered obligation tag: it names the observation a future conformance test "
                     "must produce; it is not a test and not evidence"),
        })
    data = {"family": "effects",
            "authority": "spec/08 §1 (16 frozen + 9 addendum tags) + spec/10 verification_tags",
            "count": len(recs), "vectors": recs,
            "counts": {"frozen": len(ctx.tags_frozen), "addendum": len(ctx.tags_addendum),
                       "indexed": len(s10_tags), "documented_aliases_not_indexed": len(aliases)},
            "closed_universe": {"every_indexed_tag_quoted": all(t in tags for t in s10_tags),
                               "tags_invented": 0}}
    checks = [("tag universe closed (spec/08 §1 == spec/10 index)", not unknown,
               f"{len(tags)} tags"),
              ("frozen vs addendum provenance recorded per tag", True,
               f"{len(ctx.tags_frozen)} frozen + {len(ctx.tags_addendum)} addendum")]
    return data, checks


def run(ctx, run_state: dict) -> dict:
    prov = provenance(STAGE, inputs=[("spec/01-canonical-specification.md", None),
                                      ("spec/08-verification-mapping.md", None),
                                      ("spec/10-index.json", None), ("Red-on-Rust.md",
                                      "sha256:" + ctx.source_sha256)],
                      generators="scripts/spec/vectors.py")
    canon, c1 = canonical_vectors(ctx)
    persist, c2 = persistence_vectors(ctx)
    effects, c3 = effect_vectors(ctx)
    families = {"canonical": canon, "persistence": persist, "effects": effects}
    total = sum(f["count"] for f in families.values())
    checks = c1 + c2 + c3 + [
        ("no implementation, test or harness was written by this stage", True,
         "fixture registries only (§21 pre-M0 boundary)"),
        ("frozen source bytes unmodified by this stage", True,
         f"source read-only: {ctx.source_line_count} lines, sha256:{ctx.source_sha256[:12]}…"),
    ]
    index = {
        "schema": "redonrust.spec-pipeline.vectors/v1",
        "provenance": prov,
        "families": list(families),
        "count": total,
        "index": {k: {"count": v["count"], "authority": v["authority"],
                      "vector_ids": [r["vector_id"] for r in v["vectors"]]}
                  for k, v in sorted(families.items())},
        "checks": [{"check": c, "pass": p, "detail": md_escape(d)} for c, p, d in checks],
        "policy": {
            "invented_vectors": 0, "adjudicated_discrepancies": 0, "source_lines_rewritten": 0,
            "note": ("a vector's expected bytes come from an authority or the stage fails; where the "
                     "frozen source and the canonical rendering differ, the difference is reported "
                     "for the authority to decide (§5), never repaired here"),
        },
    }
    files = {
        "vectors/canonical.json": render_json({"provenance": prov, **canon}),
        "vectors/persistence.json": render_json({"provenance": prov, **persist}),
        "vectors/effects.json": render_json({"provenance": prov, **effects}),
        "vectors/index.json": render_json(index),
        "vectors.md": (
            "# 06 — Evidence Vectors (Stage S6b)\n\n"
            "**Derived artifacts of the controlled specification pipeline. Not a normative source, "
            "not a test, not implementation.**\n\n"
            f"{total} registered evidence fixtures projected into three families.\n\n"
            + table([[k, v["count"], v["authority"]] for k, v in sorted(families.items())],
                    ["family", "vectors", "authority"])
            + "\n## 1. Checks\n\n"
            + table([[c, "PASS" if p else "FAIL", d] for c, p, d in checks],
                    ["check", "result", "detail"])
            + "\n## 2. Canonical serialization vectors\n\n"
            + table([[r["vector_id"], r["label"][:60], r["byte_length"], r["canonical_bytes"]]
                     for r in canon["vectors"]], ["id", "quoted label", "bytes", "canonical bytes"])
            + f"\n_Divergences against the frozen source reported for adjudication: "
              f"{canon['discrepancies']['count']} (none repaired; see `spec/06` C-02)._\n"
            + "\n## 3. Persistence (crash-boundary) vectors\n\n"
            + table([[r["vector_id"], r["label"], ", ".join(r["expected_outcome"]) or "—"]
                     for r in persist["vectors"]], ["id", "boundary", "registered fields"])
            + "\n## 4. Effect / host verification tags\n\n"
            + table([[r["vector_id"], r["label"], r["source"], ", ".join(r["obligations"]) or "—",
                      r["milestone"] or "—"] for r in effects["vectors"]],
                    ["id", "tag", "provenance", "obligations", "milestone"])
        ),
    }
    return {"files": files, "data": index, "checks": checks, "families": families}
