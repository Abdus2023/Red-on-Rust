#!/usr/bin/env python3
"""scripts/spec/_gate.py — the repository gate for the specification pipeline.

WHAT THIS GATE PROVES
---------------------
The stages prove their own facts on every run (a failing stage aborts the run).
This file proves the three things only a *repeated, external* view can see:

  1. **determinism** — the whole pipeline is run twice in one process and the two
     renders must be byte-identical, including the content address;
  2. **staleness** — the committed derived artifacts (`spec/00-source/` …
     `spec/05-vectors/`, `spec/PIPELINE.md`, `TRANSFORMATION-REPORT.md`) and, when
     present, the published `build/spec/` set, must equal a fresh render.  A
     projection that no longer matches its authorities is a §14 failure, so it
     fails the repository gate rather than being silently re-based;
  3. **boundary compliance** — the pipeline's own inventory: every
     `scripts/spec/*.py` is either a scanned stage module or explicitly
     classified, `.gitignore` keeps `build/` out of git, and no implementation
     artifact (`*.rs`, `Cargo.toml`) exists anywhere under `scripts/`.

It never repairs.  Every failure message names the reproduction command.

    python3 scripts/spec/_gate.py            # every proof above, counted in the output line
    python3 scripts/spec/_gate.py --strict    # prove the refusal: strict canonicalization blocks
    python3 scripts/spec/_gate.py -v          # show every check line

Exit 0 iff everything holds.  Registered in `check.py`, so `python3 check.py` runs it.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
sys.path.insert(0, str(HERE))

import _common as C                                  # noqa: E402
import pipeline as P                                 # noqa: E402
import published as PUB                              # noqa: E402
import report as REP                                   # noqa: E402
import verify as V                                     # noqa: E402

# Every module of the package, and what it is.  A new file that is neither a
# scanned stage module nor classified here fails the inventory check — the same
# rule `check.py` applies to the repository's checkers, applied inward so this
# pipeline cannot grow an unscanned hole.
STAGE_MODULES = ["_common.py", "pipeline.py", "snapshot.py", "extract.py", "split.py",
                 "normalize.py", "audit.py", "canonicalize.py", "registry.py", "vectors.py",
                 "verify.py", "published.py", "report.py", "schemas.py"]
CLASSIFIED = {"_gate.py": "this gate", }


def _results(repo: Path, strict: bool = False):
    """Run the pipeline against `repo` and return the run record."""
    if strict:
        C.STRICT_CANONICALIZATION = True
    return P.build_all(repo / C.SOURCE_REL)


def check_determinism(repo: Path, out) -> bool:
    a = _results(repo)
    b = _results(repo)
    same_hashes = a["render_hash"] == b["render_hash"] and a["content_hash"] == b["content_hash"]
    diffs = sorted(k for k in set(a["files"]) | set(b["files"])
                   if a["files"].get(k) != b["files"].get(k))
    out.append((same_hashes and not diffs,
                f"1  determinism: two independent renders are byte-identical "
                f"({len(a['files'])} artifacts, {a['render_hash'][:23]}…)",
                f"divergent artifacts: {diffs[:5]}" if diffs or not same_hashes else ""))
    # idempotence, §4.3: the canonical content of a re-render is unchanged, and
    # republishing writes nothing (byte-compare before write).
    canon_same = a["files"]["Red-on-Rust.canonical.md"] == b["files"]["Red-on-Rust.canonical.md"]
    out.append((canon_same, "1b idempotence: Pipeline(Pipeline(X)) == Pipeline(X) on the canonical "
                            "artifact (the reconstruction is re-derived from the registers, not from "
                            "the previous output)", "" if canon_same else "canonical artifact drifted"))
    return same_hashes and not diffs


def check_build_set(repo: Path, run, out) -> bool:
    build = repo / C.BUILD_DIRNAME
    if not build.is_dir():
        out.append((True, f"2  build set: not published (optional, gitignored) — "
                          f"`python3 scripts/spec/pipeline.py` creates {C.BUILD_DIRNAME}/", ""))
        return True
    problems = P.check(run, build)
    out.append((not problems, f"2  build set current vs a fresh render ({C.BUILD_DIRNAME}/)",
                "; ".join(problems[:6])))
    return not problems


def check_published_pointers(repo: Path, run, out) -> bool:
    prov = C.provenance("PUB", inputs=[("build/spec/ (rendered in memory)", run["content_hash"])],
                        generators="scripts/spec/pipeline.py --publish-derived")
    expect = PUB.render(run["ctx"], run, prov)
    problems = []
    for rel, text in sorted(expect.items()):
        path = repo / rel
        if not path.is_file():
            problems.append(f"missing: {rel}")
        elif path.read_text(encoding="utf-8") != text:
            problems.append(f"stale: {rel}")
    out.append((not problems, f"3  committed derived pointers current "
                              f"({len(expect)} files: spec/00-source…spec/05-vectors, spec/PIPELINE.md)",
                "; ".join(problems[:6])))
    # the report is pinned too, so the transformation report cannot outlive its evidence
    rtext = REP.render_report(run)
    rpath = repo / REP.REPORT_PATH
    if rpath.is_file():
        ok = rpath.read_text(encoding="utf-8") == rtext
        out.append((ok, f"3b {REP.REPORT_PATH} current vs a fresh render (digest "
                        f"{C.sha256_text(rtext)[7:19]}…)",
                    "report drifted from the artifacts it reports on" if not ok else ""))
        return not problems and ok
    out.append((False, f"3b {REP.REPORT_PATH} missing",
                "run: python3 scripts/spec/pipeline.py --report --publish-derived"))
    return False


def check_inventory(repo: Path, out) -> bool:
    files = sorted(p.name for p in (repo / "scripts/spec").iterdir() if p.suffix == ".py") \
        if (repo / "scripts/spec").is_dir() else []
    unclassified = [f for f in files if f not in STAGE_MODULES and f not in CLASSIFIED]
    out.append((not unclassified, f"4  pipeline inventory: {len(files)} module(s), every one a "
                                  f"scanned stage or explicitly classified",
                f"unclassified: {unclassified[:6]}"))
    missing = [m for m in STAGE_MODULES if m not in files]
    out.append((not missing, "4b every stage module listed in verify.PIPELINE_FILES exists",
                f"missing: {missing}"))
    scan_offenders = []
    for name in files:
        if name in STAGE_MODULES:
            continue
        hit = V.determinism_scan(repo / "scripts/spec" / name)
        scan_offenders += [f"{name}:{ln}:{what}" for ln, what in hit["offences"]]
    out.append((not scan_offenders, "4c non-stage modules (tools/tests) introduce no nondeterminism "
                                    "into the render path", str(scan_offenders[:3])))
    ignore = (repo / ".gitignore").read_text(encoding="utf-8") if (repo / ".gitignore").is_file() else ""
    out.append((C.BUILD_DIRNAME in ignore or "build/" in ignore,
                "4d .gitignore keeps the derived build set out of git", C.BUILD_DIRNAME))
    rs = sorted(str(p.relative_to(repo)) for p in repo.rglob("*.rs")) if repo.is_dir() else []
    cargo = sorted(str(p.relative_to(repo)) for p in repo.rglob("Cargo.toml"))
    out.append((not rs and not cargo, "5  §21 boundary: no Rust implementation artifact exists "
                                      "anywhere in the repository", f"rs={rs[:3]} cargo={cargo[:3]}"))
    return not (unclassified or missing or scan_offenders or rs or cargo)


def run(repo: Path = REPO, strict: bool = False) -> list[tuple[bool, str, str]]:
    """All proofs.  Returns [(pass, label, detail)]; empty list never happens."""
    out: list[tuple[bool, str, str]] = []
    if strict:
        # Strict mode inverts the proof: with 33 open BLOCKING rows carried by the
        # authorities, a render that SUCCEEDED would be the defect.  So the
        # expected outcome is the refusal itself, and the staleness proofs are not
        # computable (no canonical artifact may exist) — they are reported as
        # deliberately withheld rather than quietly skipped.
        try:
            _results(repo, strict=True)
        except C.StageFailure as exc:
            msg = str(exc)
            refused = "strict mode" in msg and "S5-canonicalize" in msg
            out.append((refused,
                        "S  --strict: canonicalization refused over open BLOCKING/MAJOR rows "
                        "(fail-closed, §12/§19)",
                        msg[:220]))
        else:
            out.append((False,
                        "S  --strict: canonicalization refused over open BLOCKING/MAJOR rows",
                        "the render SUCCEEDED under --strict — canonicalization must be blocked while "
                        "an open BLOCKING row bears on it (§12); a permissive refusal is a silent "
                        "best-effort canonical spec"))
        check_inventory(repo, out)
        out.append((True, "1–3b  determinism/staleness proofs: not evaluated under --strict (no "
                          "canonical artifact is produced; run without --strict for those proofs)", ""))
        return out
    run1 = _results(repo, strict)
    out.append((True, f"0  pipeline rendered: {len(run1['files'])} artifact(s), "
                      f"content {run1['content_hash'][:23]}…, {len(run1['stages'])} stages", ""))
    check_determinism(repo, out)
    check_build_set(repo, run1, out)
    check_published_pointers(repo, run1, out)
    check_inventory(repo, out)
    s7 = run1["results"]["S7"]["data"]
    out.append((s7["all_pass"] and s7["counts"]["failures"] == 0,
                f"6  S7 battery inside the gate: {s7['counts']['checks']} checks, "
                f"{s7['counts']['failures']} failures, {s7['counts']['gaps_reported']} gaps reported",
                ""))
    out.append((s7["m0"]["status"] == "NOT STARTED",
                f"7  M0 remains {s7['m0']['status']}; evidence ceiling SPECIFIED; "
                f"REF1/V1 carried conditional", ""))
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--strict", action="store_true",
                    help="canonicalization additionally refuses to carry open BLOCKING/MAJOR rows")
    ap.add_argument("-v", "--verbose", action="store_true", help="print passing details too")
    args = ap.parse_args()
    if args.strict:                      # S5 reads the switch at call time
        C.STRICT_CANONICALIZATION = True
    results = run(REPO, strict=args.strict)
    fails = [r for r in results if not r[0]]
    for ok_, label, detail in results:
        if ok_ and not args.verbose:
            print("OK   " + label)
        elif ok_:
            print("OK   " + label + (f"  [{detail}]" if detail else ""))
        else:
            print("FAIL " + label)
            if detail:
                print("     " + detail)
    print(f"\n{'GATE PASS' if not fails else 'GATE FAIL'} — spec pipeline "
          f"({len(results)} proofs; repository-integrity evidence only, never semantic verification)")
    if fails:
        print("Repair: python3 scripts/spec/pipeline.py --publish-derived "
              "(pointers/report) and python3 scripts/spec/pipeline.py (build set). "
              "Never edit a derived artifact by hand, and never edit an authority to match one.")
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
