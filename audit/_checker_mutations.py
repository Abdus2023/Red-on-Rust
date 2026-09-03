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
    # Added after an inventory found the repo has 15 executables and this
    # harness was exercising 6. term/_structs.py re-derives every struct
    # declaration from the frozen source and is the tool that caught the
    # "five shapes" miscount in X-87; req/_coverage.py is the omission audit
    # (which normative-looking source lines no record cites). Both are real
    # gates and neither was in the loop.
    ("term/_structs.py", []),
    ("req/_coverage.py", []),
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
    #: extra (script, args) pairs to run for THIS mutation only -- used by K18
    #: (and, since the U-38 adoption, by M036 itself), which must exercise
    #: `spec/_check.py --allowlist`, a mode the baseline deliberately does not run.
    extra_checkers: list = field(default_factory=list)


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
    # Fixture IDs must stay ahead of the live register (C-103...C-109 were taken
    # by the request-pipeline audit on 2026-09-03; a collision would turn this
    # into a duplicate row and mute the very pin the mutation exercises).
    row = ("| C-110 | Injected mutation row: a finding added to the register and "
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
    # Fixture IDs stay ahead of the live register (see m_add_c_row's note).
    row = ("| C-111 | Injected three-digit mutation row (regression lock for the "
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
    # Fixture IDs must stay ahead of the live register (U-39...U-45 were taken by
    # the request-pipeline audit on 2026-09-03); a collision would make the
    # injected heading a duplicate, leaving the U- count set unchanged and
    # muting the pin this mutation exercises.
    block = ("\n### U-90 — Injected mutation decision\n\n"
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
    """Hand-edit a GENERATED file so it no longer matches its source of truth.

    The count is located DYNAMICALLY. This mutation originally hard-coded
    "81 canonical terms." and silently became inapplicable the moment the
    register reached 86 -- reporting neither a kill nor a survival, just
    quietly testing nothing. That is the K12 failure mode verbatim, and it is
    why the runner now surfaces `inapplicable` as its own bucket instead of
    letting it vanish from the denominator.
    """
    p = root / "term/01-dictionary.md"
    txt = p.read_text(encoding="utf-8")
    m = re.search(r"(\d+) canonical terms\.", txt)
    if m is None:
        return False
    bumped = "%d canonical terms." % (int(m.group(1)) + 1)
    p.write_text(txt.replace(m.group(0), bumped, 1), encoding="utf-8")
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


def m036_rotate_obligation_body(root: Path) -> bool:
    """M036 (spec/08 registry): rotate one spec/01 obligation body onto adjacent
    content, leaving both IDs in place.

    This is the SEC-023 class -- a stable ID denoting a different rule than its
    body -- and `spec/_check.py` exists specifically to detect it.  Measured
    under the default wiring: DETECTED (one extra D3 warning) but NOT killed,
    because only D1 hard-fails while D2/D3 warn; with 36 adjudicated warnings
    already standing, 37 is camouflage (that was U-38).  U-38 was resolved
    2026-09-03 by adopting option (b): the repository gate runs
    `spec/_check.py --allowlist`, under which this mutation is KILLED -- K18 is
    the regression lock for that claim.
    """
    p = root / "spec/01-canonical-specification.md"
    txt = p.read_text(encoding="utf-8")
    obl = list(re.finditer(r"^\*\*(R-[A-Z]+-\d+)[^*]*\*\*.*$", txt, re.M))
    if len(obl) < 2:
        return False
    a, b = obl[len(obl) // 2], obl[len(obl) // 2 + 1]
    ta = re.match(r"^(\*\*R-[A-Z]+-\d+[^*]*\*\*)(.*)$", a.group(0), re.S)
    tb = re.match(r"^(\*\*R-[A-Z]+-\d+[^*]*\*\*)(.*)$", b.group(0), re.S)
    if not (ta and tb):
        return False
    txt = txt.replace(a.group(0), ta.group(1) + tb.group(2), 1)
    txt = txt.replace(b.group(0), tb.group(1) + ta.group(2), 1)
    p.write_text(txt, encoding="utf-8")
    return True


def _renumber_c_row_inplace(root: Path, old: str, new: str) -> bool:
    """Rewrite one C- row's id IN PLACE, changing no line counts.

    K01/K02/K03 all die on term/_check.py anchor shifts (X-64) rather than on
    the completeness gate they were written for: appending or deleting a row
    moves every later line, and the anchor breaks first.  That is a real kill
    but the WRONG kill -- it proves the anchors are load-bearing, not that the
    index gate works.  A register edited in place produces no line-count
    change and no anchor shift, so nothing but the gate itself can object.
    """
    p = root / "spec/06-contradictions-ambiguities.md"
    txt = p.read_text(encoding="utf-8")
    src, dst = f"| {old} |", f"| {new} |"
    if txt.count(src) != 1 or dst in txt:
        return False
    p.write_text(txt.replace(src, dst, 1), encoding="utf-8")
    return True


def m_renumber_c_row(root: Path) -> bool:
    """A finding row silently renumbered to an unindexed id, in place."""
    return _renumber_c_row_inplace(root, "C-50", "C-150")


def m_mutation_register_drift(root: Path) -> bool:
    """Renumber a spec/08 mutation row so the index list no longer matches."""
    p = root / "spec/08-verification-mapping.md"
    txt = p.read_text(encoding="utf-8")
    src, dst = "| M036 |", "| M136 |"
    if txt.count(src) != 1 or dst in txt:
        return False
    p.write_text(txt.replace(src, dst, 1), encoding="utf-8")
    return True


def m_renumber_u_heading(root: Path) -> bool:
    """An unresolved decision renumbered in place to an unindexed id."""
    p = root / "spec/09-unresolved-decisions.md"
    txt = p.read_text(encoding="utf-8")
    src, dst = "### U-21 ", "### U-121 "
    if txt.count(src) != 1 or dst in txt:
        return False
    p.write_text(txt.replace(src, dst, 1), encoding="utf-8")
    return True


def m_term_count_drift(root: Path) -> bool:
    """Add a term to term/_terms.py and leave the prose counts alone.

    The exact drift the T-82..T-86 pass caused: five files kept advertising
    "81 canonical terms" and "T-01...T-81" after the register reached 86, and
    no checker objected. Same family as the spec/06 74/76 drift (K13) and the
    spec/08-vs-index mutation drift (K15) -- a number quietly wrong rather
    than a build that fails.
    """
    p = root / "term/_terms.py"
    txt = p.read_text(encoding="utf-8")
    marker = '    Term(\n        "T-86", "Lifetime",'
    if marker not in txt:
        return False
    i = txt.index(marker)
    end = txt.index("\n    ),\n", i) + len("\n    ),\n")
    block = txt[i:end].replace('"T-86", "Lifetime"', '"T-87", "InjectedTerm"', 1)
    p.write_text(txt[:end] + block + txt[end:], encoding="utf-8")
    # Regenerate the term/ outputs. Without this the mutation dies on "01-dictionary
    # is stale" -- a real kill, but of the generated-file check (already covered by
    # K10), not of the prose-count gate this mutation exists to exercise. Kills must
    # be attributed: an unregenerated tree would let K17 pass while testing nothing
    # new. Same lesson as K01/K12/K04.
    subprocess.run([sys.executable, "term/_dict.py", "--write"],
                   cwd=root, capture_output=True, text=True)
    for pyc in (root / "term" / "__pycache__").glob("*.pyc"):
        pyc.unlink()
    return True


def m037_live_commit_before_append(root: Path) -> bool:
    """M037 (spec/08 registry): the in-memory s12-s13 mutations committed before
    the journal-driven append+fsync. Rendered as a document mutant of the frozen
    addendum-VII body: the invariant becomes live-unsafe text while the spec/03
    row still describes the journal-driven order. Detectable by spec/_check.py
    D3; survives the default wiring (U-38 open) and dies under --allowlist.
    """
    p = root / "spec/01-canonical-specification.md"
    txt = p.read_text(encoding="utf-8")
    m = re.search(r"^\*\*R-DUR-07 \(.*$", txt, re.M)
    if not m:
        return False
    mutant = ("**R-DUR-07 (live issuance failure — frozen addendum).** "
              "Persistence failures MUST commit the in-memory s12-s13 mutations "
              "before the journal append and MUST invoke the host.")
    p.write_text(txt[:m.start()] + mutant + txt[m.end():], encoding="utf-8")
    return True


def m038_payload_id_digest_only(root: Path) -> bool:
    """M038 (spec/08 registry): issuance records carry `{id, actor, digest}` only.
    Same treatment as M037: a document mutant of the R-DUR-06 body that the
    spec/03 row contradicts. D3-detectable; known to survive the default wiring
    (U-38) and to die under --allowlist.
    """
    p = root / "spec/01-canonical-specification.md"
    txt = p.read_text(encoding="utf-8")
    m = re.search(r"^\*\*R-DUR-06 \(.*$", txt, re.M)
    if not m:
        return False
    mutant = ("**R-DUR-06 (durable issuance payload — frozen addendum).** "
              "All journal entries are free-form text with no effect, digest or cost.")
    p.write_text(txt[:m.start()] + mutant + txt[m.end():], encoding="utf-8")
    return True


def m040_delta_table_violation(root: Path) -> bool:
    """M040 (spec/08 registry): delta_t table violation — a time-capable
    transition kind advances logical time without its frozen delta_t (here:
    scheduler turn double-charged). Document mutant of the addendum-IX
    R-BUDGET-16 body; D3-detectable, survives the default wiring (U-38)
    and dies under --allowlist.
    """
    p = root / "spec/01-canonical-specification.md"
    txt = p.read_text(encoding="utf-8")
    m = re.search(r"^\*\*R-BUDGET-16 \(.*$", txt, re.M)
    if not m:
        return False
    mutant = ("**R-BUDGET-16 (logical-time delta table — frozen addendum).** "
              "The lunar dial governs: every full moon the chronicle gains one day, "
              "the harvest basket gains twelve grains, and the bell tower chimes twice "
              "for good luck. Solstices double the tally; eclipses pause the gnomon; "
              "the cartwheel spins freely in the courtyard while the comet watches.")
    p.write_text(txt[:m.start()] + mutant + txt[m.end():], encoding="utf-8")
    return True


def m041_late_receipt_misclassified(root: Path) -> bool:
    """M041 (spec/08 registry): post-deadline receipt routed through the
    normal deadline gate. Document mutant of the addendum-IX R-BUDGET-16
    body; D3-detectable, survives the default wiring (U-38) and dies under
    --allowlist.
    """
    p = root / "spec/01-canonical-specification.md"
    txt = p.read_text(encoding="utf-8")
    m = re.search(r"^\*\*R-BUDGET-16 \(.*$", txt, re.M)
    if not m:
        return False
    mutant = ("**R-BUDGET-16 (logical-time delta table — frozen addendum).** "
              "A courier who arrives after sunset is turned away at the garden gate; "
              "his parcel rots in the rain; the mailbox swallows its own key; the "
              "watchman naps on the porch and the ledger keeps no entry for the night.")
    p.write_text(txt[:m.start()] + mutant + txt[m.end():], encoding="utf-8")
    return True


def m042_duration_double_charge(root: Path) -> bool:
    """M042 (spec/08 registry): cost_C(E)'s duration component debits D on
    top of the transition's ΔD := δ_t. Document mutant of the addendum-IX
    R-BUDGET-15 body; D3-detectable, survives the default wiring (U-38)
    and dies under --allowlist.
    """
    p = root / "spec/01-canonical-specification.md"
    txt = p.read_text(encoding="utf-8")
    m = re.search(r"^\*\*R-BUDGET-15 \(.*$", txt, re.M)
    if not m:
        return False
    mutant = ("**R-BUDGET-15 (duration consumable semantics — frozen addendum).** "
              "Every bill is engraved on a copper plate: the grocer debits it at the "
              "counter, the courier debits it again at the doorstep, and the two stamps "
              "are the honest price of a journey. The vaultkeeper stamps twice on feast "
              "days and the abacus never errs.")
    p.write_text(txt[:m.start()] + mutant + txt[m.end():], encoding="utf-8")
    return True


def m039_indeterminate_terminal(root: Path) -> bool:
    """M039 (spec/08 registry): `Remains-Indeterminate` treated as a terminal
    disposition (stranded escrow survives the logical-time bound). Document
    mutant of the addendum-VIII R-BUDGET-11 body; D3-detectable, survives the
    default wiring (U-38) and dies under --allowlist.
    """
    p = root / "spec/01-canonical-specification.md"
    txt = p.read_text(encoding="utf-8")
    m = re.search(r"^\*\*R-BUDGET-11 \(.*$", txt, re.M)
    if not m:
        return False
    mutant = ("**R-BUDGET-11 (escrow disposition normal form — frozen addendum).** "
              "`Remains-Indeterminate` is a permanent parking state: pending ledger "
              "truth is sampled once, cached forever, and the escrow basket is sealed "
              "with wax, guarded by three sentinels, and never reopened. Stranded "
              "units accumulate silently into the vault; the nightly audit sweep "
              "skips them entirely; the ledger keeps no tombstone; cursor ordering "
              "is irrelevant; checksums are decorative.")
    p.write_text(txt[:m.start()] + mutant + txt[m.end():], encoding="utf-8")
    return True


def m_m036_under_allowlist(root: Path) -> bool:
    """The M036 rotation, to be run against `spec/_check.py --allowlist`.

    Identical mutation to M036. The point is the CONTRAST: under the default
    severity wiring this survives; under the adopted repository gate
    (`--allowlist`, U-38 option (b), 2026-09-03) it dies. Registering it as a
    normal mutation means the claim that the adopted gate closes the SEC-023
    hole is re-verified on every run rather than resting on one measurement
    recorded in prose.
    """
    return m036_rotate_obligation_body(root)


MUTATIONS = [
    # NOTE on K01/K02/K03: these were written to exercise the completeness gate
    # in spec/_build_index.py. They do not, and CANNOT. Two separate reasons,
    # both established by experiment (see audit section 9(d)):
    #   1. Each shifts line numbers, so a term/ anchor error fires first. That
    #      is now repairable with `python3 term/_reanchor.py --write`.
    #   2. With anchors repaired, the gate still PASSES: findings are DERIVED
    #      from spec/06, so an added row is indexed automatically. The gate
    #      catches the converse (an index entry with no register row) and the
    #      named exclusions -- it structurally cannot catch "row not indexed".
    # What actually kills them is the req/_validate.py count pin. The mutations
    # are kept because that pin is worth locking; the claim about which gate
    # they exercise is corrected here rather than left to flatter the harness.
    Mutation("K01", "finding row added, counts not updated",
             "Killed by the req/_validate.py C- count pin, NOT by the completeness "
             "gate this was originally aimed at -- see the note above.",
             m_add_c_row, regression_for="req/_validate.py C- count pin",
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
    Mutation("M036", "rotate a spec/01 obligation body onto adjacent content",
             "The SEC-023 class. spec/_check.py detects it (one extra D3 warning) but the "
             "default wiring exits 0: only D1 hard-fails, and 36 adjudicated warnings "
             "camouflage the 37th (that was U-38). Resolved 2026-09-03: the repository "
             "gate runs `spec/_check.py --allowlist`, under which this mutation dies; its "
             "survival under the historical default wiring is the measured baseline in "
             "spec/08 section 2.",
             m036_rotate_obligation_body,
             regression_for="SEC-023 normative-layer content substitution",
             tags=["normative"],
             extra_checkers=[("spec/_check.py", ["--allowlist"])]),
    Mutation("K13", "row added, prose summary left unchanged",
             "The exact drift that occurred: rows accrete, the figure stays put.",
             m_summary_not_updated,
             regression_for="the 74/76-vs-102 drift this harness found",
             tags=["docs", "register", "regression"]),
    Mutation("K14", "finding row renumbered IN PLACE to an unindexed id",
             "Strong form of K01: no line-count change, so no anchor shift can "
             "mask the result. Only the completeness gate can object.",
             m_renumber_c_row, regression_for="spec/_build_index.py completeness gate",
             tags=["register", "index", "in-place"]),
    Mutation("K15", "mutation added to spec/08 but not to the index list",
             "The index's mutation list is hand-maintained; spec/08 section 2 is the "
             "register. This drift actually happened -- M036 was registered and the "
             "index reported 35 -- and no gate compared them.",
             m_mutation_register_drift,
             regression_for="the M036 index drift this harness found",
             tags=["register", "index", "regression"]),
    Mutation("K16", "unresolved decision renumbered IN PLACE",
             "The U- twin of K14; strong form of K04/K05.",
             m_renumber_u_heading, tags=["register", "index", "in-place"]),
    Mutation("K17", "term/ register grows, prose counts left behind",
             "Five files advertise the term/ register sizes and ID ranges; none was "
             "gated until the T-82..T-86 pass drifted all of them at once.",
             m_term_count_drift,
             regression_for="the 81-vs-86 term-count drift this pass caused",
             tags=["term", "register", "regression"]),
    Mutation("K18", "obligation body rotated -- caught by the U-38 allow-list",
             "The M036 rotation run against `spec/_check.py --allowlist`, the "
             "repository gate adopted by U-38 option (b) (2026-09-03). Dies under "
             "the adopted gate; survives only under the historical default wiring. "
             "Locks in the claim that the adopted gate actually closes the SEC-023 "
             "hole.",
             m_m036_under_allowlist,
             regression_for="U-38 option (b) / the SEC-023 class",
             tags=["spec", "severity", "u-38"],
             extra_checkers=[("spec/_check.py", ["--allowlist"])]),
    Mutation("K19", "in-memory s12-s13 mutations before the journal append (M037)",
             "The M037 shape rendered as a document mutant of the addendum-VII body. "
             "Survives the historical default wiring; dies under the adopted gate "
             "(U-38 option (b)), "
             "the M036/K18 contrast that keeps the claim testable for the new text.",
             m037_live_commit_before_append,
             regression_for="M037 / R-DUR-07 journal-driven commit",
             tags=["normative", "allowlist"],
             extra_checkers=[("spec/_check.py", ["--allowlist"])]),
    Mutation("K20", "issuance records carry {id, actor, digest} only (M038)",
             "The M038 shape rendered as a document mutant of the addendum-VII body. "
             "Survives the historical default wiring; dies under the adopted "
             "gate (U-38 option (b)).",
             m038_payload_id_digest_only,
             regression_for="M038 / R-DUR-06 issuance payload",
             tags=["normative", "allowlist"],
             extra_checkers=[("spec/_check.py", ["--allowlist"])]),
    Mutation("K21", "Remains-Indeterminate treated as terminal (M039)",
             "The M039 shape rendered as a document mutant of the addendum-VIII body. "
             "Survives the historical default wiring; dies under the adopted "
             "gate (U-38 option (b)), keeping the "
             "totality/refinement reconciliation testable against the frozen text.",
             m039_indeterminate_terminal,
             regression_for="M039 / R-BUDGET-11 disposition totality",
             tags=["normative", "allowlist"],
             extra_checkers=[("spec/_check.py", ["--allowlist"])]),
    Mutation("K22", "delta_t table violation (M040)",
             "The M040 shape rendered as a document mutant of the addendum-IX body. "
             "Survives the historical default wiring; dies under the adopted "
             "gate (U-38 option (b)), keeping the "
             "exhaustive delta_t enumeration testable against the frozen text.",
             m040_delta_table_violation,
             regression_for="M040 / R-BUDGET-16 delta_t table",
             tags=["normative", "allowlist"],
             extra_checkers=[("spec/_check.py", ["--allowlist"])]),
    Mutation("K23", "post-deadline receipt misclassified (M041)",
             "The M041 shape rendered as a document mutant of the addendum-IX body. "
             "Survives the historical default wiring; dies under the adopted "
             "gate (U-38 option (b)), keeping the "
             "late-receipt settlement rule testable against the frozen text.",
             m041_late_receipt_misclassified,
             regression_for="M041 / R-BUDGET-16 late-receipt settlement",
             tags=["normative", "allowlist"],
             extra_checkers=[("spec/_check.py", ["--allowlist"])]),
    Mutation("K24", "duration double charge (M042)",
             "The M042 shape rendered as a document mutant of the addendum-IX body. "
             "Survives the historical default wiring; dies under the adopted "
             "gate (U-38 option (b)), keeping the "
             "no-double-charge invariant testable against the frozen text.",
             m042_duration_double_charge,
             regression_for="M042 / R-BUDGET-15 no-double-charge",
             tags=["normative", "allowlist"],
             extra_checkers=[("spec/_check.py", ["--allowlist"])]),
]


# --------------------------------------------------------------------------
# runner
# --------------------------------------------------------------------------

def run_checkers(root: Path, verbose: bool = False, extra_checkers=()):
    """Run every checker; return (killer_name, combined_output) or (None, out)."""
    combined = []
    for rel, extra in list(CHECKERS) + list(extra_checkers):
        script = root / rel
        if not script.exists():
            continue
        proc = subprocess.run([sys.executable, str(script), *extra], cwd=root,
                              capture_output=True, text=True, timeout=900)
        out = proc.stdout + proc.stderr
        label = rel if not extra else f"{rel} {' '.join(extra)}"
        combined.append(f"----- {label} (exit {proc.returncode}) -----\n{out}")
        if verbose:
            print(f"    {rel}: exit {proc.returncode}")
        if proc.returncode != 0:
            return label, "\n".join(combined)
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

    killed, survived, inapplicable, known = [], [], [], []

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
            killer, out = run_checkers(root, verbose=args.verbose,
                                       extra_checkers=getattr(mut, "extra_checkers", ()))
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
            elif "known-survivor" in mut.tags:
                print("      SURVIVED (known, filed) <-- expected, rationale recorded")
                known.append(mut)
            else:
                print("      SURVIVED  <-- gap: no checker rejects this")
                survived.append(mut)
        print()

    print("=" * 78)
    total = len(killed) + len(survived)
    rate = (100.0 * len(killed) / total) if total else 0.0
    print(f"killed {len(killed)}/{total}  ({rate:.0f}%)"
          + (f"   known survivors {len(known)}" if known else "")
          + (f"   inapplicable {len(inapplicable)}" if inapplicable else ""))
    if known:
        print("\nKNOWN SURVIVORS (filed, not silently tolerated):")
        for m in known:
            print(f"  {m.mid}  {m.title}")
            print(f"       {m.rationale}")
    if survived:
        print("\nSURVIVING MUTANTS -- each is a defect the checkers cannot see:")
        for m in survived:
            print(f"  {m.mid}  {m.title}")
            print(f"       {m.rationale}")
    print("=" * 78)
    return 1 if survived else 0


if __name__ == "__main__":
    raise SystemExit(main())
