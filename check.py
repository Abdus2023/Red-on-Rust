#!/usr/bin/env python3
"""Run every checker in the repository, in dependency order.

WHY THIS EXISTS
---------------
The repository contains fifteen executables. Until this file was written there
was no single entrypoint, and the practical consequence was measurable: the
`ReplayHost` shape count was wrong in five documents for four commits because
`term/_structs.py` — which derives the correct answer mechanically — was never
run. A checker nobody runs is indistinguishable from a checker that does not
exist.

The rule this file enforces is: **you do not have to know which checkers exist.**
It discovers them, runs them all, and fails if any fails. New `*/_*.py` gates
are picked up automatically by the inventory check at the end, which fails when
an executable is neither run nor explicitly classified as a non-checker.

    python3 check.py           # run everything, exit non-zero on any failure
    python3 check.py -q        # only failures
    python3 check.py --list    # show the inventory and classifications

Generators are run in CHECK mode (no --write): they must be idempotent, so a
generator that would change its output is a failure, not a silent fix.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parent

# Ordered: registers and generated artifacts first, then the cross-cutting
# checks that read them, then the meta-check that tests the checkers.
CHECKERS: list[tuple[str, str]] = [
    ("spec/_build_index.py", "regenerates spec/10-index.json; carries the completeness "
                             "gate and the spec/08 mutation-register comparison"),
    ("spec/_check.py",       "obligation bodies vs frozen source and vs spec/03 (D1 hard, "
                             "D2/D3 warn -- see U-38; `--allowlist` hard-fails any warning "
                             "not in spec/_check_allowlist.txt, which is U-38 option (b) "
                             "built but not adopted)"),
    ("mod/_build.py",        "module ownership: exactly one canonical owner per obligation"),
    ("dep/_graph.py",        "dependency edges and cycle checks"),
    ("term/_check.py",       "re-greps every term/ citation; verifies term<->collision links"),
    ("term/_structs.py",     "re-derives every struct declaration from the frozen source "
                             "and groups by field set (caught the X-87 shape miscount)"),
    ("req/_validate.py",     "register sizes, prose-count gates, cross-reference tokens"),
    ("req/_coverage.py",     "omission audit: normative-looking source lines cited by no record"),
    ("term/_reanchor.py",    "living-document line anchors resolve uniquely"),
    ("audit/_checker_mutations.py", "mutation-tests the checkers themselves"),
]

# Executables that are libraries or write-mode tools, not checkers. Listed so
# the inventory check below can prove nothing was forgotten.
NON_CHECKERS: dict[str, str] = {
    "term/_terms.py":     "data module: the term/ register itself",
    "term/_dict.py":      "generator: writes term/01,02,03,10 (run with --write)",
    "req/_anchors.py":    "data module: shared provenance constants",
    "mod/_ownership.py":  "data module: the ownership map",
    "dep/_edges.py":      "data module: typed edge tables",
}


def run(rel: str, quiet: bool) -> tuple[bool, float, str]:
    t0 = time.time()
    p = subprocess.run([sys.executable, rel], cwd=REPO, capture_output=True, text=True)
    return p.returncode == 0, time.time() - t0, (p.stdout + p.stderr)


def inventory() -> list[str]:
    """Every `*/_*.py` plus this file's peers, relative to the repo root."""
    found = sorted(str(p.relative_to(REPO)) for p in REPO.glob("*/_*.py"))
    return found


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("-q", "--quiet", action="store_true", help="only show failures")
    ap.add_argument("--list", action="store_true", help="show inventory and exit")
    args = ap.parse_args()

    known = {c for c, _ in CHECKERS} | set(NON_CHECKERS)
    found = inventory()

    if args.list:
        print("CHECKERS (run by this script):")
        for c, why in CHECKERS:
            print("  %-30s %s" % (c, why))
        print("\nNON-CHECKERS (data modules and write-mode generators):")
        for c, why in sorted(NON_CHECKERS.items()):
            print("  %-30s %s" % (c, why))
        unknown = [f for f in found if f not in known]
        print("\nUNCLASSIFIED: %s" % (unknown or "none"))
        return 0

    failures: list[str] = []
    for rel, _why in CHECKERS:
        if not (REPO / rel).is_file():
            print("MISSING  %s" % rel)
            failures.append(rel)
            continue
        ok, secs, out = run(rel, args.quiet)
        if ok:
            if not args.quiet:
                print("PASS  %-30s %5.1fs" % (rel, secs))
        else:
            print("FAIL  %-30s %5.1fs" % (rel, secs))
            print("\n".join("        " + l for l in out.strip().split("\n")[-12:]))
            failures.append(rel)

    # A new gate must not be able to appear without being run. This is the
    # check that would have caught term/_structs.py sitting unattended.
    unknown = [f for f in found if f not in known]
    if unknown:
        print("\nUNCLASSIFIED EXECUTABLES -- add to CHECKERS or NON_CHECKERS in check.py:")
        for f in unknown:
            print("  %s" % f)
        failures.append("inventory")

    print("\n%s  (%d checkers, %d classified non-checkers)"
          % ("ALL PASS" if not failures else "FAILED: " + ", ".join(failures),
             len(CHECKERS), len(NON_CHECKERS)))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
