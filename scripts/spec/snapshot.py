"""Stage S0 — SNAPSHOT (§7).

Reads the frozen seed source without semantic modification, computes its
cryptographic identity, and records the provenance metadata every later stage
inherits.  The snapshot is immutable evidence of the input: it is the only
stage that touches the source bytes, and it touches them exactly once.

    python3 scripts/spec/pipeline.py --snapshot        # render to build/spec/
    python3 scripts/spec/pipeline.py --check           # verify against authorities

Rules honoured here:
  * no semantic modification — the stage never rewrites, re-wraps or reflows
    a single source byte; it only hashes and counts;
  * reproducibility — the recorded identity is (path, sha256, byte count,
    line count, pipeline version).  There is no timestamp: a timestamp would
    make the snapshot, and therefore every artifact that inherits it,
    unreproducible (§4.1/§4.2);
  * fail-closed — the computed hash is checked against the pinned expectation
    and against the hash the compiled registry records for the same file.  A
    mismatch is an audit failure, never a re-base to the new value.
"""
from __future__ import annotations

import re

from _common import (check_rows,
                     SOURCE_EXPECTED_LINES, SOURCE_EXPECTED_SHA256, StageFailure,
                     md_escape, provenance, render_json, sha256_hex, table)

STAGE = "S0-snapshot"
OUT = {"source.sha256": None, "snapshot.json": None}


def _fence_stats(lines):
    opens = 0
    fence_re = re.compile(r"^\s*```")
    for line in lines:
        if fence_re.match(line):
            opens += 1
    return {"fence_marker_lines": opens,
            "fence_markers_balanced": opens % 2 == 0}


def run(ctx) -> dict:
    """Return {"files": {rel: text}, "data": {...}, "checks": [...]}."""
    checks = []
    checks.append(("source bytes read verbatim", True,
                   f"{ctx.source_byte_count} bytes, {ctx.source_line_count} lines, "
                   f"LF-normalised count only reported, never rewritten"))
    if ctx.source_sha256 != SOURCE_EXPECTED_SHA256:
        raise StageFailure(
            f"[{STAGE}] frozen source hash does not match the pinned identity: "
            f"computed sha256:{ctx.source_sha256}, expected sha256:{SOURCE_EXPECTED_SHA256}. "
            "The seed source is FROZEN: a changed source is a governance event (a new frozen "
            "source requires an explicit governance operation), not a pipeline re-base. "
            "Refusing to snapshot.")
    checks.append(("hash matches the pinned frozen-source identity", True,
                   "sha256:" + SOURCE_EXPECTED_SHA256))

    # cross-check the snapshot against what the derived registries recorded for
    # the same file (agreement is evidence; disagreement is a hard failure —
    # the pipeline never picks a value, §5).
    xcheck = []
    if ctx.reg is not None:
        got = ctx.reg.get("sources", {}).get("Red-on-Rust.md")
        ok = got == "sha256:" + ctx.source_sha256
        xcheck.append({"authority": "reg/requirements.json sources[Red-on-Rust.md]",
                       "recorded": got, "matches_snapshot": ok})
        if not ok:
            raise StageFailure(f"[{STAGE}] reg/ pin {got} disagrees with the computed snapshot "
                               "sha256:" + ctx.source_sha256)
        checks.append(("compiled-registry pin agrees (reg/requirements.json)", True,
                       "same digest recorded for the same path"))
    if ctx.spec10 is not None:
        sor = ctx.spec10["meta"]["source_of_record"]
        ok = sor.get("lines") == ctx.source_line_count == SOURCE_EXPECTED_LINES
        xcheck.append({"authority": "spec/10-index.json meta.source_of_record",
                       "recorded": sor, "matches_snapshot": ok})
        if not ok:
            raise StageFailure(f"[{STAGE}] spec/10 declares {sor.get('lines')} source lines; "
                               f"computed {ctx.source_line_count} (pinned {SOURCE_EXPECTED_LINES})")
        checks.append(("source line count agrees with spec/10 meta", True,
                       f"{ctx.source_line_count} lines"))

    lines = ctx.source_lines
    stats = {
        "lines": ctx.source_line_count,
        "bytes": ctx.source_byte_count,
        "sha256_raw": "sha256:" + ctx.source_sha256,
        "turn_headings": len(ctx.turns),
        "turn_range": [min(ctx.turns), max(ctx.turns)] if ctx.turns else None,
        "h1_headings": sum(1 for l in lines if l.startswith("# ")),
        "h2_headings": sum(1 for l in lines if l.startswith("## ")),
        "h3_headings": sum(1 for l in lines if l.startswith("### ")),
        "table_rows": sum(1 for l in lines if l.startswith("|")),
        "code_block_lines": sum(1 for l in lines if l.startswith("```")),
    }
    stats.update(_fence_stats(lines))

    prov = provenance(STAGE, inputs=[("Red-on-Rust.md", "sha256:" + ctx.source_sha256)],
                      generators="scripts/spec/snapshot.py")
    prov["source"]["sha256"] = "sha256:" + ctx.source_sha256
    prov["reproducibility"] = {
        "reproduce_with": "sha256sum Red-on-Rust.md",
        "determinism_inputs": ["frozen source bytes", "pipeline version"],
        "excluded_by_design": ["generation timestamp", "file mtime", "locale",
                               "host filesystem order", "network state", "LLM output"],
    }

    data = {
        "schema": "redonrust.spec-pipeline.snapshot/v1",
        "provenance": prov,
        "snapshot": stats,
        "checks": check_rows(checks),
        "cross_artifact": xcheck,
        "policy": {
            "snapshot_is": "immutable evidence of the input, not a normative artifact",
            "mutation_of_source": "a governance event, never a pipeline re-base",
            "semantic_modification_performed": False,
        },
    }

    files = {
        "source.sha256": ctx.source_sha256,          # exactly 64 lowercase hex, no newline
        "snapshot.json": render_json(data),
    }
    md = [
        "# 00 — Source Snapshot (Stage S0)\n\n",
        "**Derived artifact of the controlled specification pipeline. "
        "Not a normative source.**\n\n",
        f"Seed source: `Red-on-Rust.md` — the frozen 60-turn design transcript "
        f"(turns [{min(ctx.turns)}]–[{max(ctx.turns)}]) that the repository treats as its "
        "single normative authority.\n\n",
        "## 1. Identity\n\n",
        "| Field | Value |\n|---|---|\n",
        f"| sha256 (raw bytes) | `sha256:{ctx.source_sha256}` |\n",
        f"| bytes | {ctx.source_byte_count} |\n",
        f"| lines | {ctx.source_line_count} |\n",
        f"| pipeline version | `{data['provenance']['pipeline_version']}` |\n",
        "| timestamp | none — recorded timestamps would make the snapshot unreproducible |\n\n",
        "## 2. Structure (counted, never modified)\n\n",
        table([[k, v] for k, v in sorted(stats.items())], ["measure", "value"]),
        "\n## 3. Checks performed by S0\n\n",
        table([[c, "PASS" if p else "FAIL", d] for c, p, d in checks],
              ["check", "result", "detail"]),
        "\n## 4. Why no copy of the source is made here\n\n",
        "The frozen source has exactly one home in this repository (`Red-on-Rust.md`). "
        "`spec/00-source/` carries a *pointer* with this identity rather than a second copy: "
        "a copy would be a competing authority — two byte-identical normative files that can "
        "drift apart. Determinism and reproducibility are preserved by pinning the digest, not "
        "by duplicating the bytes (§4.1 provenance, §20 no competing governance system).\n",
    ]
    files["source-snapshot.md"] = "".join(md)
    return {"files": files, "data": data, "checks": checks}
