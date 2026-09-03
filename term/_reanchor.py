#!/usr/bin/env python3
"""Re-point `term/_terms.py` line anchors after a living document shifts.

WHY THIS EXISTS
---------------
`term/_terms.py` hard-codes `(file, line, substring)` anchors.  When any
mid-file insertion happens in a living document, every later anchor breaks
even though the substring is still present and still correct -- the citation
did not become wrong, it became *stale*.

That coupling has now cost three separate repairs in this audit, and worse,
it silently absorbs mutation kills aimed at other gates: K01/K02/K03 all
reported KILLED by `term/_check.py`'s anchor error (X-64) without ever
reaching the `spec/_build_index.py` completeness gate they were written for.
A guard that fires first, for an incidental reason, on every structural edit
is a guard that hides the guards behind it.

The anchors are worth keeping -- they are what makes a citation checkable.
What is not worth keeping is repairing them by hand.  Of the 87 anchors that
point into living documents, 84 relocate to exactly one line.

WHAT THIS DOES
--------------
For every anchor into a living document (the frozen source `Red-on-Rust.md`
never moves, so its 129 anchors are excluded), search the file for the
anchor's substring:

  * exactly one match, at the recorded line -> unchanged
  * exactly one match, elsewhere            -> rewrite the line number
  * zero matches                            -> REFUSE (a real broken citation)
  * more than one match                     -> REFUSE (ambiguous; human call)

The refusals are the point.  A tool that guesses would convert a genuinely
broken citation into a confidently wrong one, which is the failure mode the
anchors exist to prevent.  Zero-match and multi-match cases are reported and
left alone.

    python3 term/_reanchor.py            # dry run, report what would change
    python3 term/_reanchor.py --write    # apply, then regenerate + check

After --write, run:  python3 term/_dict.py --write && python3 term/_check.py
(--write does this for you.)
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
TERMS_PY = HERE / "_terms.py"
FROZEN = "Red-on-Rust.md"

sys.path.insert(0, str(HERE))
import _terms as T  # noqa: E402


def read_lines(fname: str) -> list[str] | None:
    p = REPO / fname
    if not p.is_file():
        return None
    return p.read_text(encoding="utf-8").split("\n")


def find(fname: str, token: str) -> list[int]:
    """1-based line numbers whose text contains `token`."""
    lines = read_lines(fname)
    if lines is None:
        return []
    return [i + 1 for i, l in enumerate(lines) if token in l]


def collect() -> list[tuple[str, str, str, int]]:
    """(kind, file, token, recorded_line) for every living-document anchor."""
    out = []
    for c in T.COLLISIONS:
        for fname, lineno, token, _note in c.doc_sites:
            if fname and fname != FROZEN:
                out.append((c.xid, fname, token, lineno))
    for term in T.TERMS:
        for a in (term.first_definition, term.frozen_at):
            if a is not None and a.file and a.file != FROZEN:
                out.append((term.tid, a.file, a.signature, a.line))
    return out


def py_literal(s: str) -> str:
    """Render a string the way _terms.py does: prefer ', fall back to "."""
    return '"%s"' % s if "'" in s and '"' not in s else "'%s'" % s.replace("'", "\\'")


def patch_line_number(src: str, fname: str, token: str, old: int, new: int) -> tuple[str, int]:
    """Rewrite the line number in every tuple carrying (fname, old, token).

    Two anchors may share an identical (line, token) pair -- X-38 and X-59 both
    cite spec/09:56 'denial outcome is named'. An earlier version of this
    function replaced only the first match and reported success, leaving the
    second anchor stale: the same "looks covered, isn't" shape the mutation
    harness keeps turning up. Match on the full (file, line, token) triple and
    replace ALL occurrences, returning how many.

    Rewritten numbers are wrapped in NUL sentinels and unwrapped only at the
    end. Without that, moves COLLIDE: anchor A moves 186 -> 189 while anchor B
    moves 189 -> 192, and a plain sequential edit lets B's rewrite catch the
    row A just moved onto 189. The sentinel makes each row writable once.

    Both quote styles appear in _terms.py (a token containing an apostrophe is
    written with double quotes), so try each.
    """
    total = 0
    for lit in dict.fromkeys((py_literal(token), '"%s"' % token, "'%s'" % token)):
        if lit not in src:
            continue
        for f_lit in dict.fromkeys((py_literal(fname), '"%s"' % fname, "'%s'" % fname)):
            # doc_site tuple: (<file>, <line>, <token>, <note>)
            pat = re.compile(r"(%s\s*,\s*)%d(\s*,\s*%s)"
                             % (re.escape(f_lit), old, re.escape(lit)))
            src, n = pat.subn(lambda m: "%s\x00%d\x00%s" % (m.group(1), new, m.group(2)), src)
            total += n
            # Attr(file=<file>, line=N, signature=<token>)
            pat2 = re.compile(r"(file\s*=\s*%s\s*,\s*line\s*=\s*)%d(\s*,\s*signature\s*=\s*%s)"
                              % (re.escape(f_lit), old, re.escape(lit)))
            src, n = pat2.subn(lambda m: "%s\x00%d\x00%s" % (m.group(1), new, m.group(2)), src)
            total += n
    return src, total


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true",
                    help="apply the moves, then regenerate and re-check")
    args = ap.parse_args()

    src = TERMS_PY.read_text(encoding="utf-8")
    ok = moved = 0
    moves: list[tuple[str, str, int, int, str]] = []
    absent: list[tuple[str, str, str]] = []
    ambiguous: list[tuple[str, str, str, list[int]]] = []

    for xid, fname, token, recorded in collect():
        if read_lines(fname) is None:
            absent.append((xid, fname, "FILE MISSING"))
            continue
        hits = find(fname, token)
        if not hits:
            absent.append((xid, fname, token))
        elif len(hits) > 1:
            if recorded in hits:
                ok += 1  # still correct, and ambiguity is harmless while it holds
            else:
                ambiguous.append((xid, fname, token, hits))
        elif hits[0] == recorded:
            ok += 1
        else:
            moves.append((xid, fname, recorded, hits[0], token))

    print("living-document anchors: %d correct, %d to move, %d absent, %d ambiguous"
          % (ok, len(moves), len(absent), len(ambiguous)))

    for xid, fname, old, new, token in moves:
        print("  MOVE %-8s %s:%d -> %d  %r" % (xid, fname, old, new, token[:52]))
    for xid, fname, token in absent:
        print("  ABSENT %-6s %s  %r  <-- genuinely broken citation, not relocatable"
              % (xid, fname, token[:52]))
    for xid, fname, token, hits in ambiguous:
        print("  AMBIGUOUS %-4s %s  %r  matches %s  <-- human call"
              % (xid, fname, token[:40], hits))

    if not args.write:
        if moves:
            print("\ndry run; re-run with --write to apply")
        return 1 if (absent or ambiguous) else 0

    failed = []
    seen: set[tuple[str, int, str]] = set()
    for xid, fname, old, new, token in moves:
        key = (fname, old, token)
        if key in seen:
            continue  # already rewritten wholesale by an earlier identical triple
        seen.add(key)
        src, n = patch_line_number(src, fname, token, old, new)
        if n:
            moved += n
        else:
            failed.append((xid, fname, old, new, token))

    if failed:
        print("\ncould not rewrite %d anchor(s) automatically:" % len(failed))
        for xid, fname, old, new, token in failed:
            print("  %-8s %s:%d -> %d  %r" % (xid, fname, old, new, token[:52]))
        print("edit term/_terms.py by hand for these; nothing was written")
        return 2

    src = src.replace("\x00", "")  # unwrap the collision sentinels
    if moved:
        TERMS_PY.write_text(src, encoding="utf-8")
        print("\nrewrote %d anchor(s) in term/_terms.py" % moved)
        # Drop stale bytecode: this process imported _terms BEFORE rewriting it,
        # and the child _dict.py/_check.py runs would otherwise re-import the
        # cached .pyc and validate the OLD anchors -- reporting failures the
        # repair had already fixed. (Cost an hour of chasing a phantom bug.)
        for pyc in HERE.glob("__pycache__/*.pyc"):
            pyc.unlink()
        for cmd in (["python3", "term/_dict.py", "--write"], ["python3", "term/_check.py"]):
            r = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True)
            print("$ %s -> exit %d" % (" ".join(cmd), r.returncode))
            tail = (r.stdout + r.stderr).strip().split("\n")[-4:]
            print("\n".join("    " + l for l in tail if l))
            if r.returncode != 0:
                return r.returncode
    else:
        print("\nnothing to move")

    return 1 if (absent or ambiguous) else 0


if __name__ == "__main__":
    raise SystemExit(main())
