#!/usr/bin/env python3
"""Mutation battery for the specification pipeline (§22: "mutation tests detect
deliberate drift").

WHY THIS EXISTS
---------------
`check.py`'s own docstring records the lesson this repository already learned:
"a checker nobody runs is indistinguishable from a checker that does not exist",
and the semantic-nondeterminism pass found four defects of one family — *a check
that silently under-counts instead of failing*.  The pipeline in `scripts/spec/`
would be exactly such a checker if nothing injected drift into it on purpose.

A surviving mutation is a hole in the gate.  Each mutation below is a deliberate
drift of one of the kinds §14 names (identity change, count change, missing
provenance, unregistered canonical material, stale artifact, promoted status,
mutated history, invented timestamp), applied to a scratch copy of the
repository — the working tree is never modified, so this is safe to run with
uncommitted work in progress.

    python3 tests/spec/_pipeline_mutations.py           # run the battery
    python3 tests/spec/_pipeline_mutations.py -k P05    # one mutation, with output
    python3 tests/spec/_pipeline_mutations.py -v        # show failure text

`target` picks the minimum sufficient victim: `pipeline` runs the S0–S7
rendering (in-process, so the whole battery costs seconds), `gate` runs
`scripts/spec/_gate.py`, which additionally owns the staleness of the committed
derived artifacts.  Registration in `check.py` means every `python3 check.py`
runs all of this.
"""
from __future__ import annotations

import argparse
import dataclasses
import re
import shutil
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent          # <repo>/tests/spec
REPO = HERE.parent.parent                        # <repo>
sys.path.insert(0, str(REPO / "scripts" / "spec"))

import _common as C            # noqa: E402
import pipeline as P           # noqa: E402
import _gate as G              # noqa: E402

IGNORE = shutil.ignore_patterns(".git", "build", "__pycache__", ".pytest_cache", ".mypy_cache")


@dataclasses.dataclass
class Mutation:
    mid: str
    title: str
    rationale: str
    apply: object                       # (root: Path) -> bool; False => could not apply
    expect: str                         # substring expected in the failure message
    target: str = "pipeline"            # "pipeline" | "gate" | "subprocess"
    section: str = ""                   # the §14 condition this locks closed


def _sub_once(path: Path, old: str, new: str) -> bool:
    txt = path.read_text(encoding="utf-8")
    if txt.count(old) != 1:
        return False
    path.write_text(txt.replace(old, new), encoding="utf-8")
    return True


def _edit_row(path: Path, prefix: str, old: str, new: str) -> bool:
    """Replace `old` with `new` inside the single line of `path` starting with `prefix`."""
    lines = path.read_text(encoding="utf-8").split("\n")
    hits = [i for i, l in enumerate(lines) if l.startswith(prefix)]
    if len(hits) != 1 or old not in lines[hits[0]]:
        return False
    lines[hits[0]] = lines[hits[0]].replace(old, new, 1)
    path.write_text("\n".join(lines), encoding="utf-8")
    return True


def _drop_line(path: Path, prefix: str) -> bool:
    lines = path.read_text(encoding="utf-8").split("\n")
    hits = [i for i, l in enumerate(lines) if l.startswith(prefix)]
    if len(hits) != 1:
        return False
    del lines[hits[0]]
    path.write_text("\n".join(lines), encoding="utf-8")
    return True


# ---------------------------------------------------------------------------
# mutations
# ---------------------------------------------------------------------------

def m_source_drift(root: Path) -> bool:
    p = root / "Red-on-Rust.md"
    with p.open("a", encoding="utf-8") as fh:
        fh.write("\n<!-- injected by tests/spec/_pipeline_mutations.py: a byte of drift in the "
                 "frozen seed source -->\n")
    return True


def m_delete_requirement(root: Path) -> bool:
    return _drop_line(root / "spec/03-obligation-matrix.md", "| R-SCOPE-04 |")


def m_duplicate_requirement(root: Path) -> bool:
    """Silent MERGE of two identities: renumber a row onto an existing id."""
    return _edit_row(root / "spec/03-obligation-matrix.md", "| R-SCOPE-04 |",
                     "| R-SCOPE-04 |", "| R-SCOPE-03 |")


def m_duplicate_row(root: Path) -> bool:
    """Duplicate authority: the same registry row twice."""
    p = root / "spec/03-obligation-matrix.md"
    lines = p.read_text(encoding="utf-8").split("\n")
    hits = [i for i, l in enumerate(lines) if l.startswith("| R-SCOPE-01 |")]
    if len(hits) != 1:
        return False
    lines.insert(hits[0] + 1, lines[hits[0]])
    p.write_text("\n".join(lines), encoding="utf-8")
    return True


def m_status_promotion(root: Path) -> bool:
    return _edit_row(root / "spec/03-obligation-matrix.md", "| R-SCOPE-01 |",
                     "| SPECIFIED |", "| IMPLEMENTED |")


def m_authority_text_drift(root: Path) -> bool:
    """One word added to a canonical statement in spec/01: meaning changed,
    identity intact — the shape of drift a diff-oriented reviewer misses."""
    p = root / "spec/01-canonical-specification.md"
    return _sub_once(p, "R-SCOPE-01.** Red-on-Rust MUST be a deterministic,",
                     "R-SCOPE-01.** Red-on-Rust MUST generally be a deterministic,")


def m_strip_provenance(root: Path) -> bool:
    """A registry row whose provenance cell is emptied — provenance loss."""
    return _edit_row(root / "spec/03-obligation-matrix.md", "| R-CAP-02 |",
                     "L6370–6380", "—")


def m_invent_requirement(root: Path) -> bool:
    """An unregistered normative block inserted into the canonical text."""
    p = root / "spec/01-canonical-specification.md"
    txt = p.read_text(encoding="utf-8")
    block = ("**R-FAKE-99 (invented by the mutation battery).** The machine MUST do something no "
             "authority ever required. *(injected: this identity exists in no register; if you are "
             "reading it in a real specification, the gate failed.)*\n\n")
    anchor = "\n## S-02 Core thesis and central invariants"
    if txt.count(anchor) != 1:
        return False
    p.write_text(txt.replace(anchor, "\n" + block + anchor.lstrip("\n")), encoding="utf-8")
    return True


def m_drop_section_row(root: Path) -> bool:
    p = root / "spec/02-section-hierarchy.md"
    return _drop_line(p, "| S-14 |")


def m_drop_finding(root: Path) -> bool:
    """A silently deleted audit row (the register says 112 findings, the table 111)."""
    p = root / "spec/06-contradictions-ambiguities.md"
    lines = p.read_text(encoding="utf-8").split("\n")
    hits = [i for i, l in enumerate(lines) if l.startswith("| C-01 |")]
    if len(hits) != 1:
        return False
    del lines[hits[0]]
    p.write_text("\n".join(lines), encoding="utf-8")
    return True


def m_flip_decision(root: Path) -> bool:
    """Declare an open decision resolved with no authority doing so.

    Targets the first genuinely OPEN heading rather than a literal id: U-01 reads as
    open in `spec/10`'s prose but was resolved by addendum IX, and a mutation that
    "resolves" an already-resolved item proves nothing about the gate.
    """
    p = root / "spec/09-unresolved-decisions.md"
    txt = p.read_text(encoding="utf-8")
    heads = list(re.finditer(r"^### (U-\d+) — .*$", txt, re.M))
    for i, h in enumerate(heads):
        body = txt[h.start(): heads[i + 1].start() if i + 1 < len(heads) else len(txt)]
        if re.search(r"\*\*Resolved \(addendum", body):
            continue
        p.write_text(txt[:h.end()]
                     + "\n\n**Resolved (addendum IX, 2099-01-01): injected by the mutation "
                       "battery; no authority adopted it.**" + txt[h.end():], encoding="utf-8")
        return True
    return False


def m_break_terminology_shape(root: Path) -> bool:
    """Remove a required field from the terminology index the pipeline consumes."""
    import json
    p = root / "term/10-index.json"
    d = json.loads(p.read_text(encoding="utf-8"))
    if "FORBIDDEN_VARIANTS" not in d["terms"][0]:
        return False
    del d["terms"][0]["FORBIDDEN_VARIANTS"]
    p.write_text(json.dumps(d, sort_keys=True, ensure_ascii=False), encoding="utf-8")
    return True


def m_edit_history(root: Path) -> bool:
    """Editing a hash-pinned historical audit: provenance violation, not a repair."""
    p = root / "audit/semantic-nondeterminism-audit.md"
    with p.open("a", encoding="utf-8") as fh:
        fh.write("\n<!-- injected by tests/spec/_pipeline_mutations.py: an edit to an immutable "
                 "historical record -->\n")
    return True


def m_stale_pointer(root: Path) -> bool:
    p = root / "spec/01-sections/README.md"
    return _sub_once(p, "body digest", "body digiest")


def m_stale_build_set(root: Path) -> bool:
    d = root / "build/spec"
    d.mkdir(parents=True, exist_ok=True)
    (d / "source.sha256").write_text("0" * 64, encoding="utf-8")
    return True


def m_inject_timestamp(root: Path) -> bool:
    """§4.1: a stamp that would make every artifact unreproducible."""
    p = root / "scripts/spec/_common.py"
    return _sub_once(p, '        "timestamp_present": False,',
                     '        "timestamp_present": True,\n        "generation_timestamp": '
                     '"2099-01-01T00:00:00Z",')


MUTATIONS = [
    Mutation("P01", "frozen seed source drifts by one line",
             "The snapshot is the root of all provenance; if a mutated source were accepted, every "
             "downstream digest would silently re-base.", m_source_drift,
             "frozen source hash does not match", section="§14 source provenance is missing/changed"),
    Mutation("P02", "a requirement is silently deleted from the registry",
             "Silent DELETE is the first prohibited identity operation (§4.5).", m_delete_requirement,
             "requirement identity diverges", section="§4.5 identity preservation"),
    Mutation("P03", "a requirement is silently renumbered onto another identity",
             "Silent MERGE/RENUMBER: two rows end up claiming one identity.", m_duplicate_requirement,
             "duplicate", section="§4.5 / §14 duplicate authority"),
    Mutation("P04", "a duplicate registry row is appended",
             "Duplicate authority (§14: fail closed).", m_duplicate_row,
             "duplicate registry row", section="§14 duplicate authority"),
    Mutation("P05", "a row is promoted SPECIFIED → IMPLEMENTED",
             "Promotion without evidence; canonicalization must refuse (§12).", m_status_promotion,
             "evidence ceiling", section="§12 no status upgrade"),
    Mutation("P06", "one canonical statement's wording drifts in `spec/01`",
             "The worst kind of drift: identity intact, meaning changed. Caught because the compiled "
             "registry pins the digest of the authority it compiled from.", m_authority_text_drift,
             "pinned authority digest", section="§4.1 provenance / §5 authority order"),
    Mutation("P07", "a registry row loses its provenance cell",
             "A canonical row nobody can trace back to the source must fail, not degrade.",
             m_strip_provenance, "resolvable provenance", section="§14 entry lacks source provenance"),
    Mutation("P08", "an unregistered requirement is invented in the canonical text",
             "Canonicalize(X) ⊄ NormativeContent(X) — the invention the safety theorem forbids.",
             m_invent_requirement, "identity diverges", section="§4.4 no normative invention"),
    Mutation("P09", "a section row is dropped from the section registry",
             "The split must stay lossless and the section universe closed.", m_drop_section_row,
             "section registry and normative text home disagree", section="§9 ordering/provenance"),
    Mutation("P10", "an audit finding row is deleted",
             "Findings are authoritative records; deletion is suppression.", m_drop_finding,
             "finding cardinality", section="§14 counts diverge"),
    Mutation("P11", "an open decision is declared resolved with no authority",
             "Silent acceptance of a semantic resolution (§11).", m_flip_decision,
             "U-register cardinality and membership", section="§11 no silent acceptance"),
    Mutation("P12", "the terminology index loses a required field",
             "S3 refuses to consume a register whose shape changed.", m_break_terminology_shape,
             "terminology index shape", section="§10 normalization preserves meaning"),
    Mutation("P13", "a protected historical audit is edited",
             "Altering history is a provenance violation until its disposition is deliberately "
             "updated (§4.5).", m_edit_history, "protected historical audit snapshots",
             section="§14 historical artifact presented as current"),
    Mutation("P14", "a committed derived pointer is hand-edited",
             "Hand-editing a projection is the 'smooth it over' failure §16 forbids; the gate "
             "re-renders and compares.", m_stale_pointer, "committed derived pointers",
             target="gate", section="§14 generated files are stale"),
    Mutation("P15", "the published build set is stale",
             "A stale projection must fail rather than be believed.", m_stale_build_set,
             "build set current", target="gate", section="§14 generated files are stale"),
    Mutation("P16", "a generation timestamp is injected into provenance",
             "§4.1: where a timestamp would destroy reproducibility it MUST NOT participate; the "
             "discipline is a check, not a comment.", m_inject_timestamp, "timestamp participates", target="subprocess",
             section="§4.2 determinism"),
]


def run_pipeline(root: Path) -> tuple[bool, str]:
    try:
        P.build_all(root / "Red-on-Rust.md")
    except C.StageFailure as exc:
        return False, str(exc)
    except Exception as exc:                                   # noqa: BLE001
        return False, f"{type(exc).__name__}: {exc}"
    return True, ""


def run_subprocess(root: Path) -> tuple[bool, str]:
    """Full render in a FRESH interpreter, so a mutation to the pipeline's own source
    is actually loaded.  The `pipeline` target runs in-process for speed, and that
    speed costs correctness when the mutation edits *code* — so code mutations pay
    the ~1 s of a subprocess instead of silently surviving."""
    import subprocess
    r = subprocess.run([sys.executable, "-B", "scripts/spec/pipeline.py", "Red-on-Rust.md"],
                       cwd=str(root), capture_output=True, text=True, timeout=600)
    # the harness contract is (passed, detail) — a non-zero exit means the drift
    # was noticed, i.e. the mutation was KILLED
    return r.returncode == 0, (r.stdout + r.stderr).strip()


def run_gate(root: Path) -> tuple[bool, str]:
    try:
        results = G.run(root)
    except C.StageFailure as exc:
        return False, str(exc)
    except Exception as exc:                                   # noqa: BLE001
        return False, f"{type(exc).__name__}: {exc}"
    fails = [f"{label}  [{detail}]" for ok, label, detail in results if not ok]
    return not fails, "\n     ".join(fails)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("-k", "--only", help="run one mutation by id (e.g. P05)")
    ap.add_argument("-v", "--verbose", action="store_true", help="print the failure text")
    args = ap.parse_args()

    selected = [m for m in MUTATIONS if not args.only or m.mid == args.only.upper()]
    if not selected:
        print(f"no mutation matches {args.only!r}")
        return 2

    print("=" * 78)
    print("MUTATION TESTING THE SPECIFICATION PIPELINE (scripts/spec/)")
    print(f"{len(selected)} mutation(s); target = the artifact the drift is aimed at")
    print("=" * 78)

    with tempfile.TemporaryDirectory(prefix="ror-baseline-") as tmp:
        base = Path(tmp) / "repo"
        shutil.copytree(REPO, base, ignore=IGNORE)
        print("baseline (unmutated tree must pass) ... ", end="", flush=True)
        ok_p, out_p = run_pipeline(base)
        ok_g, out_g = run_gate(base)
        if not (ok_p and ok_g):
            print("FAILED — the pipeline rejects the clean tree")
            print((out_p or out_g)[:3000])
            print("\nCannot mutation-test against a red baseline.")
            return 2
        print("green")
    print()

    killed, survived, inapplicable = [], [], []
    for mut in selected:
        print(f"{mut.mid}  {mut.title}")
        with tempfile.TemporaryDirectory(prefix=f"ror-{mut.mid}-") as tmp:
            root = Path(tmp) / "repo"
            shutil.copytree(REPO, root, ignore=IGNORE)
            try:
                applied = mut.apply(root)
            except Exception as exc:                            # noqa: BLE001
                print(f"      !! apply raised {exc!r} — the battery itself is broken")
                raise
            if not applied:
                print("      SKIP  (anchor moved — the mutation could not be applied)\n")
                inapplicable.append(mut)
                continue
            ok, out = {"gate": run_gate, "subprocess": run_subprocess}.get(
                mut.target, run_pipeline)(root)
            if ok:
                print("      SURVIVED  ✗  nothing noticed the drift")
                survived.append(mut)
            elif mut.expect and mut.expect not in out:
                print("      KILLED (by a different check than intended — inspect below)")
                if args.verbose:
                    print("      " + out[:1500].replace("\n", "\n      "))
                killed.append(mut)
            else:
                print("      KILLED  ✓  " + (out.splitlines() or [""])[0][:100])
                if args.verbose:
                    print("      " + out[:1500].replace("\n", "\n      "))
                killed.append(mut)

    total = len(killed) + len(survived)
    print("\n" + "-" * 78)
    print(f"killed {len(killed)}/{total}"
          + (f"   inapplicable (anchor moved): {[m.mid for m in inapplicable]}" if inapplicable else ""))
    if survived:
        print("SURVIVING MUTATIONS — each is a hole in the gate:")
        for m in survived:
            print(f"  {m.mid} {m.title}  ({m.section})")
        return 1
    if not total:
        print("nothing ran")
        return 2
    print("no survivors: deliberate drift in any of these shapes fails the pipeline or the gate")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
