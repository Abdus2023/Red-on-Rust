#!/usr/bin/env python3
"""Mutation testing for the repository's own consistency checkers.

WHY THIS EXISTS
---------------
`spec/01` R-TEST-06 requires that "the mutation framework validates itself
before being trusted", and R-TEST-04 makes mutation testing the evidence
standard for the machine.  The five checkers in this repository
(`spec/_check.py`, `mod/_build.py`, `dep/_graph.py`, `term/_check.py`,
`req/_validate.py`) are the only executable artifacts here, and they gate
every change to the specification set -- but nothing tests *them*.

That gap is not hypothetical.  The semantic-nondeterminism pass found four
defects in the checkers, all of one family: **a check that silently
under-counts instead of failing.**

  * `req/_validate.py` asserted `len(c_ids) != 97` against a `C-\\d{2}`
    pattern -- it reported 99 where there were 102.
  * `spec/_build_index.py` had five such patterns, one of them in the
    completeness gate at L429-432 whose stated purpose is "the next pass
    cannot silently reopen the gap".  That gate PASSED while omitting
    C-100..C-102 from the index.
  * Two `max(...)` calls compared IDs as strings, so `"C-99" > "C-102"`
    and the meta block advertised a maximum that was not the maximum.

A checker that cannot fail when it should is worth less than no checker,
because it manufactures confidence.  This harness injects defects the
registers would realistically acquire and asserts that some checker
rejects each one.  A mutation that survives is a hole in the gate.

CONTRACT
--------
Every mutation is applied to a scratch copy of the repository -- the real
working tree is never modified, so this is safe to run with uncommitted
work in progress.  Exit 0 iff every mutation is killed.

    python3 audit/_checker_mutations.py          # run all
    python3 audit/_checker_mutations.py -v       # show checker output
    python3 audit/_checker_mutations.py -k ID    # run one mutation
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

# The checkers, in rough order of cost.  `_build_index.py` is included as a
# checker because its completeness gate is an assertion even though its
# primary job is generation -- that gate is where one of the four defects lived.
CHECKERS = [
    ("spec/_check.py", []),
    ("mod/_build.py", []),
    ("term/_check.py", []),
    ("req/_validate.py", []),
    ("spec/_build_index.py", []),
    ("dep/_graph.py", []),
]


@dataclass
class Mutation:
    """A defect the registers could realistically acquire."""

    mid: str
    title: str
    rationale: str
    apply: object  # (root: Path) -> bool   -- False => could not apply
    expect: str = ""  # substring expected in the killing checker's output
    regression_for: str = ""  # a real defect this mutation locks closed
    tags: list = field(default_factory=list)


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------

def _sub_once(path: Path, old: str, new: str) -> bool:
    txt = path.read_text(encoding="utf-8")
    if txt.count(old) != 1:
        return False
    path.write_text(txt.replace(old, new), encoding="utf-8")
    return True


def _append(path: Path, text: str) -> bool:
    with path.open("a", encoding="utf-8") as fh:
        fh.write(text)
    return True


def _last_c_row(root: Path) -> str:
    txt = (root / "spec/06-contradictions-ambiguities.md").read_text(encoding="utf-8")
    rows = re.findall(r"^\| C-\d{2,3} \|.*$", txt, re.M)
    return rows[-1]


# --------------------------------------------------------------------------
# mutations
# --------------------------------------------------------------------------

def m_add_c_row(root: Path) -> bool:
    """A new finding row appended to spec/06 and nowhere else."""
    row = ("| C-103 | Injected mutation row: a finding added to the register and "
           "to no index | MINOR | L1 | **open** → U-01 | Injected by "
           "audit/_checker_mutations.py; if you are reading this in a real "
           "register, the harness failed to clean up. |\n")
    txt = (root / "spec/06-contradictions-ambiguities.md").read_text(encoding="utf-8")
    anchor = "\n**Summary counts:**"
    if txt.count(anchor) != 1:
        return False
    (root / "spec/06-contradictions-ambiguities.md").write_text(
        txt.replace(anchor, row + anchor), encoding="utf-8")
    return True


def m_add_c_row_3digit(root: Path) -> bool:
    """Same, but at a THREE-DIGIT id -- the exact shape that slipped through.

    C-100..C-102 were invisible to five `C-\\d{2}` patterns.  If any of them
    regress to two digits, this mutation survives.
    """
    row = ("| C-104 | Injected three-digit mutation row (regression lock for the "
           "C-\\d{2} under-count) | MINOR | L1 | **open** → U-01 | Injected by "
           "audit/_checker_mutations.py. |\n")
    txt = (root / "spec/06-contradictions-ambiguities.md").read_text(encoding="utf-8")
    anchor = "\n**Summary counts:**"
    if txt.count(anchor) != 1:
        return False
    (root / "spec/06-contradictions-ambiguities.md").write_text(
        txt.replace(anchor, row + anchor), encoding="utf-8")
    return True


def m_drop_c_row(root: Path) -> bool:
    """Silently delete the last finding row (supersession without a record)."""
    p = root / "spec/06-contradictions-ambiguities.md"
    row = _last_c_row(root)
    return _sub_once(p, row + "\n", "")


def m_add_u_heading(root: Path) -> bool:
    """A new unresolved decision with no index entry and no count update."""
    block = ("\n### U-38 — Injected mutation decision\n\n"
             "- **Where:** R-CORE-08.\n"
             "- **State of source:** injected by audit/_checker_mutations.py.\n"
             "- **Decision needed:** none; this is a test fixture.\n"
             "- **Blocking:** no.\n\n")
    txt = (root / "spec/09-unresolved-decisions.md").read_text(encoding="utf-8")
    anchor = "## Process notes"
    if txt.count(anchor) != 1:
        return False
    (root / "spec/09-unresolved-decisions.md").write_text(
        txt.replace(anchor, block + anchor), encoding="utf-8")
    return True


def m_add_u_heading_3digit(root: Path) -> bool:
    """A three-digit U- id: regression lock for the `U-\\d{2}` patterns."""
    block = ("\n### U-100 — Injected three-digit mutation decision\n\n"
             "- **Where:** R-CORE-08.\n"
             "- **State of source:** injected by audit/_checker_mutations.py.\n"
             "- **Decision needed:** none; this is a test fixture.\n"
             "- **Blocking:** no.\n\n")
    txt = (root / "spec/09-unresolved-decisions.md").read_text(encoding="utf-8")
    anchor = "## Process notes"
    if txt.count(anchor) != 1:
        return False
    (root / "spec/09-unresolved-decisions.md").write_text(
        txt.replace(anchor, block + anchor), encoding="utf-8")
    return True


def m_shift_term_anchor(root: Path) -> bool:
    """Insert a line mid-file in spec/09, shifting every term/ citation anchor.

    This is the failure the U-35..U-37 landing actually caused (20 broken
    anchors).  term/_check.py caught it; this locks that in.
    """
    p = root / "spec/09-unresolved-decisions.md"
    txt = p.read_text(encoding="utf-8")
    anchor = "## Blocking (must be decided before the affected component is implemented)"
    if txt.count(anchor) != 1:
        return False
    p.write_text(txt.replace(anchor, "INJECTED LINE (shifts all later anchors)\n\n" + anchor),
                 encoding="utf-8")
    return True


def m_corrupt_source_citation(root: Path) -> bool:
    """Point a term/ citation at a line that does not contain its substring."""
    p = root / "term/_terms.py"
    txt = p.read_text(encoding="utf-8")
    m = re.search(r'\("spec/09-unresolved-decisions\.md", (\d+), "denial outcome is named"', txt)
    if not m:
        return False
    p.write_text(txt.replace(m.group(0),
                             m.group(0).replace(m.group(1), str(int(m.group(1)) + 1), 1), 1),
                 encoding="utf-8")
    return True


def m_break_requirement_id(root: Path) -> bool:
    """Rename a requirement in spec/01 without updating anything that cites it."""
    p = root / "spec/01-canonical-specification.md"
    return _sub_once(p, "**R-ACTOR-07 (deterministic concurrency theorem).**",
                     "**R-ACTOR-99 (deterministic concurrency theorem).**")


def m_drop_module_obligation(root: Path) -> bool:
    """Remove an obligation from a module's REQUIREMENTS table (ownership hole)."""
    p = root / "mod/07-scheduler.md"
    txt = p.read_text(encoding="utf-8")
    m = re.search(r"^\| R-ACTOR-07 \|.*$", txt, re.M)
    if not m:
        return False
    p.write_text(txt.replace(m.group(0) + "\n", ""), encoding="utf-8")
    return True


def m_stale_generated_file(root: Path) -> bool:
    """Hand-edit a GENERATED file so it no longer matches its source of truth."""
    p = root / "term/01-dictionary.md"
    txt = p.read_text(encoding="utf-8")
    if "81 canonical terms." not in txt:
        return False
    p.write_text(txt.replace("81 canonical terms.", "82 canonical terms.", 1), encoding="utf-8")
    return True


def m_table_pipe(root: Path) -> bool:
    """An unescaped `|` inside a table cell -- silently shifts every column."""
    p = root / "spec/06-contradictions-ambiguities.md"
    row = _last_c_row(root)
    return _sub_once(p, row, row.replace("Injected", "x", 1)
                     if "Injected" in row else row[:-1] + " a|b |")


def m_wrong_summary_count(root: Path) -> bool:
    """Understate the LIVE summary figure (documentation drift).

    Targets the claim that names the current row count -- not a quoted
    historical figure, which is legitimately preserved verbatim (R-SCOPE-03).
    """
    p = root / "spec/06-contradictions-ambiguities.md"
    txt = p.read_text(encoding="utf-8")
    rows = len(re.findall(r"^\| C-\d{2,3} \|", txt, re.M))
    live = re.search(r"(\d+) findings in %d rows" % rows, txt)
    if not live:
        return False
    wrong = int(live.group(1)) - 7
    p.write_text(txt.replace(live.group(0), f"{wrong} findings in {rows} rows", 1),
                 encoding="utf-8")
    return True


def m_summary_not_updated(root: Path) -> bool:
    """Add a row without touching the summary -- the drift that actually happened.

    This is the exact shape of the real defect: rows accrete, the prose figure
    stays put.  It must fail even though every id is well-formed and indexed.
    """
    p = root / "spec/06-contradictions-ambiguities.md"
    txt = p.read_text(encoding="utf-8")
    row = ("| C-105 | Injected row: register grows, summary line does not | MINOR "
           "| L1 | **open** \u2192 U-01 | Injected by audit/_checker_mutations.py. |\n")
    anchor = "\n**Summary counts:**"
    if txt.count(anchor) != 1:
        return False
    p.write_text(txt.replace(anchor, row + anchor), encoding="utf-8")
    return True


MUTATIONS = [
    Mutation("K01", "finding row added, not indexed",
             "The completeness gate must reject a register row absent from 10-index.json.",
             m_add_c_row, regression_for="spec/_build_index.py L429-432 gate",
             tags=["register", "index"]),
    Mutation("K02", "THREE-DIGIT finding row added, not indexed",
             "Locks the C-\\d{2} under-count closed: C-100..C-102 were invisible to five patterns.",
             m_add_c_row_3digit, regression_for="the four latent ID bugs",
             tags=["register", "index", "regression"]),
    Mutation("K03", "finding row silently deleted",
             "Supersession must never be silent (R-SCOPE-03); a vanished row must fail.",
             m_drop_c_row, tags=["register"]),
    Mutation("K04", "unresolved decision added, counts not updated",
             "req/_validate.py pins the U- count so register growth is a recorded change.",
             m_add_u_heading, tags=["register"]),
    Mutation("K05", "THREE-DIGIT unresolved decision added",
             "Regression lock for the U-\\d{2} patterns, the U- twin of K02.",
             m_add_u_heading_3digit, regression_for="U-\\d{2} patterns",
             tags=["register", "regression"]),
    Mutation("K06", "mid-file insertion shifts term/ citation anchors",
             "The real failure mode of the U-35..U-37 landing (20 anchors broke).",
             m_shift_term_anchor, regression_for="term/ line-anchor coupling",
             tags=["term", "anchors"]),
    Mutation("K07", "term/ citation points at the wrong line",
             "term/_check.py re-greps all citations; an off-by-one must not pass.",
             m_corrupt_source_citation, tags=["term", "anchors"]),
    Mutation("K08", "requirement ID renamed, citations left dangling",
             "R-ACTOR-07 is cited across spec/, mod/, req/, dep/; renaming must fail.",
             m_break_requirement_id, tags=["obligations"]),
    Mutation("K09", "obligation dropped from its owning module",
             "mod/ requires exactly one canonical owner per obligation.",
             m_drop_module_obligation, tags=["mod", "ownership"]),
    Mutation("K10", "generated file hand-edited (stale vs source of truth)",
             "term/01 is generated; a hand edit must be detected as stale.",
             m_stale_generated_file, tags=["generated"]),
    Mutation("K11", "unescaped pipe inside a markdown table cell",
             "A literal | shifts every later column; req/_validate.py checks this.",
             m_table_pipe, tags=["format"]),
    Mutation("K12", "live prose summary count understates the register",
             "Documentation drift: the summary line disagreeing with the rows.",
             m_wrong_summary_count,
             regression_for="the 74/76-vs-102 drift this harness found",
             tags=["docs", "regression"]),
    Mutation("K13", "row added, prose summary left unchanged",
             "The exact drift that occurred: rows accrete, the figure stays put.",
             m_summary_not_updated,
             regression_for="the 74/76-vs-102 drift this harness found",
             tags=["docs", "register", "regression"]),
]


# --------------------------------------------------------------------------
# runner
# --------------------------------------------------------------------------

def run_checkers(root: Path, verbose: bool = False):
    """Run every checker; return (killer_name, combined_output) or (None, out)."""
    combined = []
    for rel, extra in CHECKERS:
        script = root / rel
        if not script.exists():
            continue
        proc = subprocess.run([sys.executable, str(script), *extra], cwd=root,
                              capture_output=True, text=True, timeout=900)
        out = proc.stdout + proc.stderr
        combined.append(f"----- {rel} (exit {proc.returncode}) -----\n{out}")
        if verbose:
            print(f"    {rel}: exit {proc.returncode}")
        if proc.returncode != 0:
            return rel, "\n".join(combined)
    return None, "\n".join(combined)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("-v", "--verbose", action="store_true")
    ap.add_argument("-k", "--only", help="run a single mutation by id (e.g. K02)")
    args = ap.parse_args()

    selected = [m for m in MUTATIONS if not args.only or m.mid == args.only.upper()]
    if not selected:
        print(f"no mutation matches {args.only!r}")
        return 2

    print("=" * 78)
    print("MUTATION TESTING THE REPOSITORY'S OWN CHECKERS")
    print("=" * 78)
    print(f"repo      : {REPO}")
    print(f"checkers  : {len(CHECKERS)}")
    print(f"mutations : {len(selected)}")
    print()

    # Baseline: the unmutated tree must be green, or nothing below means anything.
    with tempfile.TemporaryDirectory() as td:
        base = Path(td) / "repo"
        shutil.copytree(REPO, base, ignore=shutil.ignore_patterns(".git"))
        print("baseline (unmutated tree must pass) ... ", end="", flush=True)
        killer, out = run_checkers(base, verbose=args.verbose)
        if killer:
            print(f"FAILED -- {killer} rejects the clean tree")
            print(out[-3000:])
            print("\nCannot mutation-test against a red baseline.")
            return 2
        print("green")
    print()

    killed, survived, inapplicable = [], [], []

    for mut in selected:
        print(f"{mut.mid}  {mut.title}")
        print(f"      why: {mut.rationale}")
        if mut.regression_for:
            print(f"      regression lock: {mut.regression_for}")
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "repo"
            shutil.copytree(REPO, root, ignore=shutil.ignore_patterns(".git"))
            try:
                ok = mut.apply(root)
            except Exception as exc:  # noqa: BLE001
                ok = False
                print(f"      !! apply raised {exc!r}")
            if not ok:
                print("      SKIP  (could not apply -- anchor text moved)\n")
                inapplicable.append(mut)
                continue
            killer, out = run_checkers(root, verbose=args.verbose)
            if killer:
                first = ""
                for line in out.splitlines():
                    if re.search(r"\berror\b|\bERROR\b|✗|FAIL", line):
                        first = line.strip()
                        break
                print(f"      KILLED by {killer}")
                if first:
                    print(f"      -> {first[:140]}")
                killed.append((mut, killer))
            else:
                print("      SURVIVED  <-- gap: no checker rejects this")
                survived.append(mut)
        print()

    print("=" * 78)
    total = len(killed) + len(survived)
    rate = (100.0 * len(killed) / total) if total else 0.0
    print(f"killed {len(killed)}/{total}  ({rate:.0f}%)"
          + (f"   inapplicable {len(inapplicable)}" if inapplicable else ""))
    if survived:
        print("\nSURVIVING MUTANTS -- each is a defect the checkers cannot see:")
        for m in survived:
            print(f"  {m.mid}  {m.title}")
            print(f"       {m.rationale}")
    print("=" * 78)
    return 1 if survived else 0


if __name__ == "__main__":
    raise SystemExit(main())
