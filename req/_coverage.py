"""Omission audit: which normative-looking source lines are cited by no record?

Run:  python3 req/_coverage.py [--full]

The registry cites line ranges; this script inverts that mapping.  It scans the
requirement-dense regions of the frozen source for lines that carry a normative
marker (MUST / MUST NOT / SHALL / SHOULD / MAY / never / always / immutable /
required / forbidden / exactly / boxed formula) and reports the ones that fall
outside every range cited by any record.

It is an audit aid, not a gate: an uncited line is a candidate omission that a
human must judge, because explanatory prose also uses these words.  `--full`
prints every uncited candidate line; the default prints a per-section summary.
"""

from __future__ import annotations

import re
import sys

import _anchors as A

# Requirement-dense regions of the frozen source.
REGIONS = [
    ("master prompt (turn [54])", 37638, 38968),
    ("bootstrap pack (turn [58])", 40600, 41273),
    ("closing turns [59]-[60]", 41274, 42312),
]

NORMATIVE = re.compile(
    r"\b(MUST NOT|MUST|SHALL NOT|SHALL|SHOULD NOT|SHOULD|MAY NOT|MAY|never|always|"
    r"immutable|required|forbidden|prohibited|exactly|reject|only when|iff)\b"
)
BOXED = re.compile(r"\\boxed|\\Rightarrow|\\iff|\\preceq|\\forall")
NOISE = re.compile(r"^\s*(\||#|\*|`{3}|<|\\begin|\\end|\\mid|\\frac|\$\$|\)|\})")


def covered(lines: list[str]) -> list[bool]:
    """True for every line inside at least one range cited by a record."""
    mask = [False] * (len(lines) + 2)
    for rec in A.load_registry_records():
        for lo, hi in A.cited_ranges(rec.get("SOURCE", "")):
            for i in range(lo, min(hi, len(lines)) + 1):
                mask[i] = True
    return mask


def all_turns(lines: list[str], mask: list[bool], full: bool) -> int:
    """Per-turn coverage over the whole 60-turn transcript."""
    starts = A.turn_starts(lines)
    total_cand = total_uncited = 0
    rows = []
    for i, (turn, first) in enumerate(starts):
        last = starts[i + 1][1] - 1 if i + 1 < len(starts) else A.SOURCE_MAX_LINE
        cand, uncited = [], []
        for n in range(first, last + 1):
            text = lines[n - 1]
            if not text.strip() or NOISE.match(text):
                continue
            if NORMATIVE.search(text) or BOXED.search(text):
                cand.append(n)
                if not mask[n]:
                    uncited.append(n)
        total_cand += len(cand)
        total_uncited += len(uncited)
        rows.append((turn, first, last, cand, uncited))
    rows.sort(key=lambda r: -len(r[4]))
    print(f"{'turn':>5} {'span':>18} {'norm':>5} {'uncited':>8}")
    for turn, first, last, cand, uncited in rows:
        if not cand:
            continue
        print(f"[{turn:>3}] L{first:>6}-L{last:<6} {len(cand):>5} {len(uncited):>8}")
        if full:
            for n in uncited:
                print(f"        L{n}: {lines[n-1].strip()[:110]}")
    print(f"\nTOTAL normative-marker lines: {total_cand}, uncited: {total_uncited}")
    return 0


def main() -> int:
    full = "--full" in sys.argv
    lines = A.read_source_lines()
    mask = covered(lines)
    records = A.load_registry_records()
    print(f"records: {len(records)}   cited lines: {sum(mask)} / {A.SOURCE_MAX_LINE}")
    if "--all-turns" in sys.argv:
        return all_turns(lines, mask, full)
    total_cand = total_uncited = 0
    for name, lo, hi in REGIONS:
        cand, uncited = [], []
        for n in range(lo, min(hi, len(lines)) + 1):
            text = lines[n - 1]
            if not text.strip() or NOISE.match(text):
                continue
            if NORMATIVE.search(text) or BOXED.search(text):
                cand.append(n)
                if not mask[n]:
                    uncited.append(n)
        total_cand += len(cand)
        total_uncited += len(uncited)
        pct = 100.0 * (len(cand) - len(uncited)) / len(cand) if cand else 100.0
        print(f"\n{name}: L{lo}-L{hi}")
        print(f"  normative-marker lines : {len(cand)}")
        print(f"  cited by a record      : {len(cand) - len(uncited)}  ({pct:.1f}%)")
        print(f"  uncited candidates     : {len(uncited)}")
        if full:
            for n in uncited:
                print(f"    L{n}: {lines[n-1].strip()[:120]}")
        else:
            # compact: group consecutive lines
            groups, cur = [], []
            for n in uncited:
                if cur and n == cur[-1] + 1:
                    cur.append(n)
                else:
                    if cur:
                        groups.append(cur)
                    cur = [n]
            if cur:
                groups.append(cur)
            for g in groups[:40]:
                span = f"L{g[0]}" if len(g) == 1 else f"L{g[0]}-{g[-1]}"
                print(f"    {span}: {lines[g[0]-1].strip()[:100]}")
    print(f"\nTOTAL normative-marker lines: {total_cand}, uncited: {total_uncited}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
