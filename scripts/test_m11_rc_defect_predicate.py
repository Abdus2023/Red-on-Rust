#!/usr/bin/env python3
"""RF-02 regression: R-ORDER-02 defect predicate + fail-closed behavior.

Exercises production logic in m11_rc_defect_predicate (not a duplicate oracle).
"""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from m11_rc_defect_predicate import evaluate_defect_predicate, parse_c_rows

REPO = Path(__file__).resolve().parent.parent
REGISTER = REPO / "final" / "09-open-architectural-decisions.md"


def assert_true(cond: bool, msg: str) -> None:
    if not cond:
        raise AssertionError(msg)


def test_live_register_has_open_blocking() -> None:
    """Canonical live register: open BLOCKING ⇒ predicate FAIL (RF-01)."""
    res = evaluate_defect_predicate(REGISTER, reading="all")
    assert_true(not res.fail_closed, "live register must parse")
    assert_true(res.rows_parsed >= 10, f"expected many C-rows, got {res.rows_parsed}")
    assert_true(len(res.open_blocking) >= 1, f"expected open BLOCKING, got {res.open_blocking}")
    assert_true(not res.ok, f"expected FAIL on open high defects: {res.detail}")
    # Narrow alone also fails
    narrow = evaluate_defect_predicate(REGISTER, reading="narrow")
    assert_true(not narrow.ok, "narrow reading must fail on open BLOCKING")
    print("PASS test_live_register_has_open_blocking", res.detail)


def test_clean_register_passes() -> None:
    """Synthetic register with no open high rows ⇒ defect predicate PASS."""
    body = """
## B. open rows

| C-ID | Severity | Linked decision |
|---|---|---|
| `C-900` | MINOR | RESOLVED by test fixture |
| `C-901` | MAJOR | RESOLVED by test fixture |
| `C-902` | BLOCKING | RESOLVED by test fixture |
"""
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "09.md"
        p.write_text(body, encoding="utf-8")
        res = evaluate_defect_predicate(p, reading="all")
        assert_true(not res.fail_closed, res.detail)
        assert_true(res.rows_parsed == 3, f"rows={res.rows_parsed}")
        assert_true(res.ok, f"expected PASS, got {res.detail}")
        assert_true(res.open_blocking == [], res.open_blocking)
        assert_true(res.open_major == [], res.open_major)
    print("PASS test_clean_register_passes")


def test_open_blocking_fails() -> None:
    body = """
| C-ID | Severity | State |
|---|---|---|
| `C-910` | BLOCKING | **open** → U-TEST |
| `C-911` | MINOR | **open** → noise |
"""
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "09.md"
        p.write_text(body, encoding="utf-8")
        res = evaluate_defect_predicate(p, reading="all")
        assert_true(not res.ok, res.detail)
        assert_true("C-910" in res.open_blocking, res.open_blocking)
        assert_true("C-911" not in res.open_high_narrow, "MINOR not narrow-high")
    print("PASS test_open_blocking_fails")


def test_open_major_fails_conservative() -> None:
    body = """
| C-ID | Severity | State |
|---|---|---|
| `C-920` | MAJOR | **open** → U-X |
"""
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "09.md"
        p.write_text(body, encoding="utf-8")
        narrow = evaluate_defect_predicate(p, reading="narrow")
        cons = evaluate_defect_predicate(p, reading="conservative")
        allr = evaluate_defect_predicate(p, reading="all")
        assert_true(narrow.ok, "narrow should pass MAJOR-only open")
        assert_true(not cons.ok, "conservative must fail MAJOR open")
        assert_true(not allr.ok, "all must fail MAJOR open")
    print("PASS test_open_major_fails_conservative")


def test_missing_register_fail_closed() -> None:
    res = evaluate_defect_predicate(Path("/nonexistent/final/09-open-architectural-decisions.md"))
    assert_true(res.fail_closed, "must fail_closed")
    assert_true(not res.ok, "must not PASS")
    print("PASS test_missing_register_fail_closed")


def test_malformed_empty_fail_closed() -> None:
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "empty.md"
        p.write_text("# no tables\n", encoding="utf-8")
        res = evaluate_defect_predicate(p, reading="all")
        assert_true(res.fail_closed, res.detail)
        assert_true(not res.ok, res.detail)
    print("PASS test_malformed_empty_fail_closed")


def test_unknown_severity_open_fail_closed_high() -> None:
    body = """
| C-ID | Severity | State |
|---|---|---|
| `C-930` | WEIRDGRADE | **open** → ?
"""
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "09.md"
        p.write_text(body, encoding="utf-8")
        res = evaluate_defect_predicate(p, reading="narrow")
        assert_true(not res.ok, f"unknown open severity must not PASS: {res.detail}")
        assert_true(
            "C-930" in res.open_high_narrow,
            f"expected C-930 in narrow high, got {res.open_high_narrow} rows={res.rows}",
        )
    print("PASS test_unknown_severity_open_fail_closed_high")


def test_parse_live_sample() -> None:
    text = REGISTER.read_text(encoding="utf-8")
    rows = parse_c_rows(text)
    assert_true(any(r.defect_id == "C-98" for r in rows), "C-98 expected")
    c98 = next(r for r in rows if r.defect_id == "C-98")
    assert_true(c98.is_open and c98.severity == "BLOCKING", c98)
    print("PASS test_parse_live_sample", json.dumps({"c98": c98.severity}))


def main() -> int:
    tests = [
        test_live_register_has_open_blocking,
        test_clean_register_passes,
        test_open_blocking_fails,
        test_open_major_fails_conservative,
        test_missing_register_fail_closed,
        test_malformed_empty_fail_closed,
        test_unknown_severity_open_fail_closed_high,
        test_parse_live_sample,
    ]
    failed = 0
    for t in tests:
        try:
            t()
        except Exception as e:
            failed += 1
            print(f"FAIL {t.__name__}: {e}")
    if failed:
        print(f"SUMMARY {failed}/{len(tests)} failed")
        return 1
    print(f"SUMMARY {len(tests)}/{len(tests)} passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
