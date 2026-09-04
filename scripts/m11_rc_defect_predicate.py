#!/usr/bin/env python3
"""Canonical M11 RC defect predicate (R-ORDER-02).

Authority:
  final/01 R-ORDER-02 — M11 acceptance includes «zero open high defects pass»
  final/09 — open C-row register (severity × state)

This module does NOT redefine R-ORDER-02. It implements a fail-closed
executable reading of the open C-row register for the RC gate.

Severity mapping (documented, not invented categories):
  - BLOCKING  → always RC-high (release-blocking by name; R-TEST-05 analogy)
  - CRITICAL / HIGH → RC-high if present as open product defects
  - MAJOR → counted as RC-high under the conservative reading used by
    M11-REVIEW RF-01 (R-ORDER-02 «high» is not a separate enum in final/09;
    MAJOR is the next grade below BLOCKING). Narrow reading (BLOCKING-only)
    is also reported; either way open BLOCKING alone violates the condition.
  - MINOR → not RC-high

«Open» = register cell contains open / **open** (not RESOLVED, not
resolved-by-addendum as sole status). Rows marked resolved-by-later-text
with incompleteness still **open** remain open.

Fail-closed: missing/unreadable/malformed registry → predicate FAIL
(not PASS).

Does not close OADs, re-grade rows, or promote R-REG.
"""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parent.parent
DEFAULT_REGISTER = REPO / "final" / "09-open-architectural-decisions.md"

# Canonical severity tokens appearing in final/09 C-rows.
HIGH_ALWAYS = frozenset({"BLOCKING", "CRITICAL", "HIGH"})
# Conservative inclusion for R-ORDER-02 «high» (see module doc).
HIGH_CONSERVATIVE = HIGH_ALWAYS | frozenset({"MAJOR", "MINOR→MAJOR", "MINOR->MAJOR"})


@dataclass
class DefectRow:
    defect_id: str
    severity: str
    state_raw: str
    is_open: bool
    rc_high_narrow: bool  # BLOCKING/CRITICAL/HIGH only
    rc_high_conservative: bool  # + MAJOR
    source_line: str


@dataclass
class DefectPredicateResult:
    ok: bool
    """True iff zero applicable open high defects under the governing reading."""
    fail_closed: bool
    """True if failure was due to missing/malformed authority input."""
    governing_reading: str
    open_blocking: list[str]
    open_major: list[str]
    open_high_narrow: list[str]
    open_high_conservative: list[str]
    rows_parsed: int
    register_path: str
    detail: str
    rows: list[dict[str, Any]]


def _normalize_sev(sev: str) -> str:
    s = sev.strip().upper().replace(" ", "")
    s = s.replace("**", "")
    return s


def _is_open_state(state: str) -> bool:
    st = state.strip().lower()
    # Explicit closed/resolved forms
    if st.startswith("resolved") and "open" not in st:
        return False
    if "resolved-by-addendum" in st and "open" not in st:
        return False
    if st in {"closed", "wontfix", "mitigated", "deferred"}:
        return False
    # Open forms (including "resolved-by-later-text (incompleteness **open**)")
    if "open" in st:
        return True
    if st.startswith("**open**") or st == "open":
        return True
    return False


def parse_c_rows(text: str) -> list[DefectRow]:
    """Parse final/09 C-ID table rows: | `C-nn` | SEVERITY | state |"""
    rows: list[DefectRow] = []
    # Match table rows with C-ids
    pat = re.compile(
        r"^\|\s*`?(C-\d+)`?\s*\|\s*([^|]+)\|\s*([^|\n]+)\|?\s*$",
        re.MULTILINE,
    )
    for m in pat.finditer(text):
        cid = m.group(1).strip()
        sev_raw = m.group(2).strip()
        state_raw = m.group(3).strip()
        sev = _normalize_sev(sev_raw)
        # Collapse MINOR→MAJOR unicode arrow variants
        sev = sev.replace("→", "->").replace("−", "-")
        if "MAJOR" in sev and "MINOR" in sev:
            sev_key = "MINOR→MAJOR"
        elif sev == "BLOCKING":
            sev_key = "BLOCKING"
        elif sev == "MAJOR":
            sev_key = "MAJOR"
        elif sev == "MINOR":
            sev_key = "MINOR"
        elif sev in {"CRITICAL", "HIGH"}:
            sev_key = sev
        else:
            # Unknown severity → fail-closed: treat open unknown as high
            sev_key = f"UNKNOWN:{sev}" if sev else "UNKNOWN:EMPTY"

        is_open = _is_open_state(state_raw)
        # UNKNOWN open severity treated as high (fail-closed)
        unknown = sev_key.startswith("UNKNOWN:")
        narrow = is_open and (sev_key in HIGH_ALWAYS or unknown)
        conservative = is_open and (
            sev_key in HIGH_CONSERVATIVE
            or sev_key == "MINOR→MAJOR"
            or unknown
        )
        rows.append(
            DefectRow(
                defect_id=cid,
                severity=sev_key,
                state_raw=state_raw,
                is_open=is_open,
                rc_high_narrow=narrow,
                rc_high_conservative=conservative,
                source_line=m.group(0)[:200],
            )
        )
    return rows


def evaluate_defect_predicate(
    register_path: Path | None = None,
    *,
    reading: str = "narrow",
) -> DefectPredicateResult:
    """Evaluate R-ORDER-02 zero-open-high-defects against final/09.

    reading:
      - «narrow»: BLOCKING/CRITICAL/HIGH (+ unknown) only
      - «conservative»: narrow + MAJOR (M11-REVIEW RF-01 reading)
    Governing default for the RC gate is «narrow» for BLOCKING certainty,
    but the gate FAILS if EITHER reading finds open high defects — i.e.
    open BLOCKING alone fails; open MAJOR alone fails under conservative
    which the gate also reports. Practical rule: fail if open_high_narrow
    OR open_high_conservative is non-empty when reading=all.

    For the production gate we use reading=«all»: fail if any open
    BLOCKING/CRITICAL/HIGH OR any open MAJOR (conservative union).
    """
    path = register_path or DEFAULT_REGISTER
    if not path.is_file():
        return DefectPredicateResult(
            ok=False,
            fail_closed=True,
            governing_reading=reading,
            open_blocking=[],
            open_major=[],
            open_high_narrow=[],
            open_high_conservative=[],
            rows_parsed=0,
            register_path=str(path),
            detail=f"fail-closed: register missing: {path}",
            rows=[],
        )
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as e:
        return DefectPredicateResult(
            ok=False,
            fail_closed=True,
            governing_reading=reading,
            open_blocking=[],
            open_major=[],
            open_high_narrow=[],
            open_high_conservative=[],
            rows_parsed=0,
            register_path=str(path),
            detail=f"fail-closed: register unreadable: {e}",
            rows=[],
        )

    rows = parse_c_rows(text)
    if not rows:
        return DefectPredicateResult(
            ok=False,
            fail_closed=True,
            governing_reading=reading,
            open_blocking=[],
            open_major=[],
            open_high_narrow=[],
            open_high_conservative=[],
            rows_parsed=0,
            register_path=str(path),
            detail="fail-closed: no C-rows parsed from register",
            rows=[],
        )

    open_blocking = [r.defect_id for r in rows if r.is_open and r.severity == "BLOCKING"]
    open_major = [
        r.defect_id
        for r in rows
        if r.is_open and r.severity in {"MAJOR", "MINOR→MAJOR"}
    ]
    open_high_narrow = [r.defect_id for r in rows if r.rc_high_narrow]
    open_high_conservative = [r.defect_id for r in rows if r.rc_high_conservative]

    # Governing: fail if narrow high non-empty OR (if conservative/all) major high
    if reading == "narrow":
        violators = open_high_narrow
        gov = "narrow (BLOCKING/CRITICAL/HIGH/unknown)"
    elif reading == "conservative":
        violators = open_high_conservative
        gov = "conservative (narrow + MAJOR)"
    else:  # all — union; open BLOCKING or MAJOR both fail
        violators = sorted(set(open_high_narrow) | set(open_high_conservative))
        gov = "all (narrow ∪ conservative)"

    ok = len(violators) == 0
    detail = (
        "zero open high defects"
        if ok
        else (
            f"open high defects under {gov}: {', '.join(violators)} "
            f"(blocking={open_blocking}, major={open_major})"
        )
    )
    return DefectPredicateResult(
        ok=ok,
        fail_closed=False,
        governing_reading=gov,
        open_blocking=open_blocking,
        open_major=open_major,
        open_high_narrow=open_high_narrow,
        open_high_conservative=open_high_conservative,
        rows_parsed=len(rows),
        register_path=str(path),
        detail=detail,
        rows=[asdict(r) for r in rows],
    )


def main() -> int:
    import json
    import sys

    reading = "all"
    path = None
    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] == "--reading" and i + 1 < len(args):
            reading = args[i + 1]
            i += 2
        elif args[i] == "--register" and i + 1 < len(args):
            path = Path(args[i + 1])
            i += 2
        else:
            i += 1
    res = evaluate_defect_predicate(path, reading=reading)
    out = {
        "ok": res.ok,
        "fail_closed": res.fail_closed,
        "governing_reading": res.governing_reading,
        "open_blocking": res.open_blocking,
        "open_major": res.open_major,
        "open_high_narrow": res.open_high_narrow,
        "open_high_conservative": res.open_high_conservative,
        "rows_parsed": res.rows_parsed,
        "register_path": res.register_path,
        "detail": res.detail,
    }
    print(json.dumps(out, indent=2))
    return 0 if res.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
