#!/usr/bin/env python3
"""spec_restore_dryrun.py — prove the SEC-023 restoration draft clears the corruption.

Applies audit/spec01-restoration-draft.md to TEMPORARY COPIES of:
  - spec/01-canonical-specification.md  (each flagged obligation's body <- its
    record's Original quotation, header and citation preserved), and
  - spec/normative-normalization-records.md (each flagged record's Normalized
    <- its Original; the substituted wording is retained as a
    "Superseded Normalized (SEC-023 substitution)" quote, per the
    quoted-not-deleted discipline),
then re-runs the spec_check detectors against the copies.

With --apply, the restored texts are written to the REAL files instead of
temporary copies (in-place restoration; the change is fully visible in git).

Exit 0 = run completed (see report).  Exit 2 = --apply requested but the
restored-text build did not touch exactly the flagged set (safety abort).
"""

from __future__ import annotations

import re
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from spec_check import MIN_OVERLAP, parse_records, signature, overlap  # noqa: E402

REPO = Path(__file__).resolve().parent.parent
SPEC01 = REPO / "spec" / "01-canonical-specification.md"
RECORDS = REPO / "spec" / "normative-normalization-records.md"
CHECKER = Path(__file__).resolve().parent / "spec_check.py"

PARA_RE = re.compile(r"\*\*(R-[A-Z]+-\d+)[^\n]*?\*\*(.+?)(?=\n\n\*\*R-|\n\n## |\n## |\Z)", re.S)
CITE_RE = re.compile(r"\*\(L[^)]*\)\.*\s*$")


def flatten(quoted: str) -> str:
    lines = []
    for ln in quoted.splitlines():
        ln = ln.strip()
        if ln.startswith("- **Original:**"):
            ln = ln.split("- **Original:**", 1)[1].strip()
        elif ln.startswith("- **Normalized:**"):
            ln = ln.split("- **Normalized:**", 1)[1].strip()
        if ln.startswith(">"):
            ln = ln[1:].strip()
        if ln:
            lines.append(ln)
    return " ".join(lines)


def flagged_ids(recs):
    out = []
    for rid in sorted(recs):
        o, n = recs[rid]
        if overlap(signature(o), signature(n)) < MIN_OVERLAP:
            out.append(rid)
    return out


def restore_spec01(flagged: set[str], recs) -> tuple[str, int]:
    text = SPEC01.read_text(encoding="utf-8")
    replaced = 0

    def sub(m):
        nonlocal replaced
        rid, body = m.group(1), m.group(2)
        if rid not in flagged:
            return m.group(0)
        replaced += 1
        header = m.group(0).split("**", 2)[1]  # **R-XXX-NN (title).**
        rest_text = flatten(recs[rid][0])
        cite = CITE_RE.search(body.strip())
        if cite and not re.search(r"\(L\d", rest_text):
            rest_text = rest_text.rstrip(".") + ". " + cite.group(0).strip()
        return f"**{header[len(rid) + 2:-2] if False else header}** {rest_text}"

    # simpler: rebuild using the full matched header span
    out = []
    last = 0
    for m in PARA_RE.finditer(text):
        rid = m.group(1)
        if rid not in flagged:
            continue
        header_end = m.group(0).find("**", m.group(0).find("**") + 2) + 2
        header = m.group(0)[:header_end]  # includes opening **...**
        rest_text = flatten(recs[rid][0])
        # a record's Original sometimes begins with its own bold header; strip
        # that duplicate (the body already carries the canonical header)
        rest_text = re.sub(rf"^\*\*{re.escape(rid)}\s*\([^*]*?\)\.\*\*\s*", "", rest_text)
        cite = CITE_RE.search(m.group(2).strip())
        if cite and not re.search(r"\(L\d", rest_text):
            rest_text = rest_text.rstrip(".") + ". " + cite.group(0).strip()
        out.append(text[last : m.start()])
        out.append(f"{header} {rest_text}")
        last = m.end()
        replaced += 1
    out.append(text[last:])
    return "".join(out), replaced


def restore_records(flagged: set[str], recs) -> tuple[str, int]:
    text = RECORDS.read_text(encoding="utf-8")
    parts = re.split(r"(?m)^(### R-[A-Z]+-\d+\s*)$", text)
    # parts: [pre, '### ID', body, '### ID', body, ...]
    fixed = 0
    rebuilt = [parts[0]]
    for i in range(1, len(parts), 2):
        head, body = parts[i], parts[i + 1]
        rid_m = re.match(r"### (R-[A-Z]+-\d+)", head)
        rid = rid_m.group(1) if rid_m else None
        if rid in flagged:
            orig_lines = [ln for ln in recs[rid][0].splitlines() if ln.strip()]
            norm_flat = flatten(recs[rid][1])
            new_norm = "\n".join("  " + ln if not ln.startswith(" ") else ln for ln in orig_lines)
            body = re.sub(
                r"(?ms)^(\s*- \*\*Normalized:\*\*.*)$(?=\s*- \*\*(Reason|Semantic Risk))",
                lambda _m: f"  - **Superseded Normalized (SEC-023 substitution, quoted not deleted):**\n"
                           f"  > {norm_flat}\n"
                           f"  - **Normalized:**\n{new_norm}",
                body,
                count=1,
            )
            fixed += 1
        rebuilt.append(head)
        rebuilt.append(body)
    return "".join(rebuilt), fixed


def main() -> int:
    apply = "--apply" in sys.argv[1:]
    recs = parse_records()
    flagged = set(flagged_ids(recs))
    print(f"flagged records: {len(flagged)}")

    spec01_new, n1 = restore_spec01(flagged, recs)
    records_new, n2 = restore_records(flagged, recs)
    print(f"restored bodies built for spec/01: {n1}; records Normalized restored: {n2}")

    if apply:
        if n1 != len(flagged) or n2 != len(flagged):
            print("SAFETY ABORT: restoration did not cover exactly the flagged set "
                  f"({n1}/{n2} vs {len(flagged)}); nothing written.")
            return 2
        SPEC01.write_text(spec01_new, encoding="utf-8")
        RECORDS.write_text(records_new, encoding="utf-8")
        print(f"APPLIED: {SPEC01.relative_to(REPO)} and {RECORDS.relative_to(REPO)} updated in place.")
        targets = [str(SPEC01), str(RECORDS)]
    else:
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            p1, p2 = td / "spec01.md", td / "records.md"
            p1.write_text(spec01_new, encoding="utf-8")
            p2.write_text(records_new, encoding="utf-8")
            print("dry run only (no repository file modified; pass --apply to restore in place)")
            r = subprocess.run(
                [sys.executable, str(CHECKER), "--spec01", str(p1), "--records", str(p2)],
                capture_output=True, text=True,
            )
            _report(r, False)
        return 0

    r = subprocess.run(
        [sys.executable, str(CHECKER), "--spec01", str(SPEC01), "--records", str(RECORDS)],
        capture_output=True, text=True,
    )
    _report(r, True)
    return 0


def _report(r, applied: bool) -> None:
    print("---- checker on restored files ----" if applied else "---- checker on restored copies ----")
    print(r.stdout.strip()[-3000:])
    d1 = r.stdout.count("[D1]")
    d2 = r.stdout.count("[D2]")
    d3 = r.stdout.count("[D3]")
    print(f"---- summary: exit={r.returncode}  D1={d1} D2={d2} D3={d3} (was 48/52/54) ----")


if __name__ == "__main__":
    sys.exit(main())
