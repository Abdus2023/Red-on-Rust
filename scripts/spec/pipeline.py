"""scripts/spec/pipeline.py — the single entry point for the controlled
specification-processing pipeline (§18).

    python3 scripts/spec/pipeline.py Red-on-Rust.md            # full run -> build/spec/
    python3 scripts/spec/pipeline.py Red-on-Rust.md --check    # render + cross-verify, write nothing
    python3 scripts/spec/pipeline.py --report                  # §24 transformation report
    python3 scripts/spec/pipeline.py --list                    # stages and their contracts

STAGE ORDER (default full pipeline, §18)
---------------------------------------
    SNAPSHOT -> EXTRACT -> SPLIT -> NORMALIZE -> AUDIT -> CANONICALIZE -> REGISTER -> VERIFY
      S0          S1         S2        S3          S4         S5              S6         S7

FAIL-CLOSED RULE (§19)
---------------------
Any stage failure aborts the run *before* anything is written: `StageFailure`
propagates, exit code is 1, and no partial canonical artifact is published. A
failed audit blocks canonicalization; a registry mismatch fails verification;
verification failure means the canonical state is not accepted. The pipeline
never emits a "best effort" specification.

DETERMINISM / IDEMPOTENCE (§4.2/§4.3)
------------------------------------
Output is a pure function of (frozen source bytes, committed authorities,
pipeline version).  Nothing reads a clock, the locale, the network, the
filesystem order, or an LLM.  Re-running produces byte-identical files; the
`--check` mode proves it by re-rendering and comparing (and `scripts/spec/_gate.py`
is registered in `check.py` so drift fails the repository gate).

WHAT THIS PIPELINE IS NOT (§21 pre-M0 boundary)
----------------------------------------------
It writes no Rust, defines no runtime, designs no CEK machine, capability
kernel, actor, scheduler, host, persistence or effect implementation, and starts
no milestone: M0 remains NOT STARTED.  It is specification-processing
infrastructure only — scripts, registries, validators, provenance machinery,
canonicalization machinery, audit tooling and pipeline test fixtures.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
sys.path.insert(0, str(HERE))

import _common as C                                    # noqa: E402
import snapshot as S0                                   # noqa: E402
import extract as S1                                    # noqa: E402
import split as S2                                      # noqa: E402
import normalize as S3                                  # noqa: E402
import audit as S4                                      # noqa: E402
import canonicalize as S5                               # noqa: E402
import registry as S6                                   # noqa: E402
import vectors as SV                                    # noqa: E402
import verify as S7                                     # noqa: E402

STAGE_GENERATORS = {"S0": "snapshot.py", "S1": "extract.py", "S2": "split.py",
                    "S3": "normalize.py", "S4": "audit.py", "S5": "canonicalize.py",
                    "S6": "registry.py", "S6b": "vectors.py", "S7": "verify.py"}

STAGES = [
    ("--snapshot", "S0 SNAPSHOT", "seed source -> source.sha256 + snapshot.json (+ md)"),
    ("--extract", "S1 EXTRACT", "authorities -> candidate requirements/obligations + proposals"),
    ("--split", "S2 SPLIT", "spec/01 + spec/02 -> sections/S-nn-*.md (lossless)"),
    ("--normalize", "S3 NORMALIZE", "term/ + spec/01 -> terminology.json + conformance proof"),
    ("--audit", "S4 AUDIT", "spec/06, spec/09, req/03, audit/, dep/ -> audit/*.md"),
    ("--canonicalize", "S5 CANONICALIZE", "validated material -> Red-on-Rust.canonical.md"),
    ("--register", "S6 REGISTER", "-> requirements.json, obligations.json, dependencies.json"),
    ("--vectors", "S6b VECTORS", "-> vectors/{canonical,persistence,effects}/*.json"),
    ("--verify", "S7 VERIFY", "cross-artifact verification -> verification.json/md"),
]


def build_all(source: Path) -> dict:
    """Run every stage in order and return {relpath: text} plus the run record.

    Pure with respect to the repository: writes nothing.  `publish()` is the
    only function that touches the filesystem, so `--check` and the gate can run
    the whole pipeline without side effects."""
    ctx = C.Ctx(source.parent if source.is_dir() else Path(source).resolve().parent)
    if Path(source).name != C.SOURCE_REL:
        raise C.StageFailure(
            f"[driver] the seed source must be the frozen `{C.SOURCE_REL}`; got '{source}'. "
            "Processing a different file would produce a projection whose provenance does not name "
            "the repository's authority (§4.1).")
    run: dict = {"files": {}, "stages": [], "ctx": ctx, "stage_of": {}, "generator_of": {},
                 "inputs_of": {}}

    for mod, label in ((S0, "S0"), (S1, "S1"), (S2, "S2"), (S3, "S3")):
        _merge(run, label, mod.run(ctx))

    _merge(run, "S4", S4.run(ctx, split_result=run["results"]["S2"]))
    _merge(run, "S5", S5.run(ctx, run))
    _merge(run, "S6", S6.run(ctx, run))
    _merge(run, "S6b", SV.run(ctx, run))

    # provenance footer on every human-readable artifact, then content-address
    # the set.  S7's own output cannot participate in the proof of its own
    # inputs, so `content_hash` is over the verified set and `render_hash` over
    # the published set.
    add_provenance_footers(run, ctx)
    run["content_hash"] = C.pipeline_render_hash("build/spec:content", run["files"])
    _merge(run, "S7", S7.run(ctx, run))
    add_provenance_footers(run, ctx)
    run["render_hash"] = C.pipeline_render_hash("build/spec", run["files"])
    return run


def add_provenance_footers(run: dict, ctx) -> None:
    """§4.1: every generated artifact is traceable to source hash, source path,
    pipeline version, stage and generator.  The JSON artifacts carry it as a
    `provenance` block; markdown carries it as this footer, so the property holds
    for a reader of either form.  No timestamp participates."""
    for rel, text in list(run["files"].items()):
        if not rel.endswith(".md") or "pipeline_version" in text:
            continue
        stage = run["stage_of"].get(rel, "build")
        gen = run["generator_of"].get(rel, "scripts/spec/pipeline.py")
        footer = (
            "\n\n---\n\n"
            "*generated by `redonrust-spec-pipeline` (pipeline_version `" + C.PIPELINE_VERSION
            + "`) · stage `" + stage
            + "` · generator `" + gen + "` · seed source `Red-on-Rust.md` @ `sha256:"
            + ctx.source_sha256 + "` (" + str(ctx.source_line_count) + " lines) · "
            + _inputs_note(run, rel) + " · "
            + "no generation timestamp: a stamp would make this file unreproducible (§4.1)*\n")
        run["files"][rel] = text + footer


def _merge(run: dict, label: str, res: dict) -> None:
    run.setdefault("stage_of", {})
    stage_inputs = [i for i in ((res.get("data") or {}).get("provenance") or {}).get("inputs", [])]
    for rel in res["files"]:
        run["stage_of"].setdefault(rel, label)
        run["generator_of"].setdefault(rel, "scripts/spec/" + STAGE_GENERATORS.get(label, "pipeline.py"))
        run["inputs_of"].setdefault(rel, [{"path": i.get("path"), "sha256": i.get("sha256")}
                                          for i in stage_inputs])
    for rel, text in res["files"].items():
        if rel in run["files"] and run["files"][rel] != text:
            raise C.StageFailure(f"[driver] stage {label} would overwrite another stage's artifact "
                                 f"'{rel}' — two stages claiming one file is a determinism defect")
        run["files"][rel] = text
    run.setdefault("results", {})[label] = res
    run["stages"].append({
        "stage": label,
        "checks": C.check_rows(res.get("checks", [])),
    })


def publish(run: dict, outdir: Path) -> tuple[list[str], list[str]]:
    """Write the rendered artifacts, byte-exactly, in sorted order.

    The published set is accompanied by `manifest.json`, which records the
    render hash — that is how a later `--check` can prove what is on disk is the
    current render and not a stale one (§14)."""
    files = dict(run["files"])
    files["manifest.json"] = C.render_json({
        "schema": "redonrust.spec-pipeline.manifest/v1",
        "render_hash": run["render_hash"],
        "content_hash": run["content_hash"],
        "pipeline": C.PIPELINE_NAME,
        "pipeline_version": C.PIPELINE_VERSION,
        "source": {"path": "Red-on-Rust.md", "sha256": "sha256:" + run["ctx"].source_sha256},
        "artifact_count": len(run["files"]),
        "artifacts": {rel: C.sha256_text(text) for rel, text in sorted(run["files"].items())},
        "timestamp_present": False,
        "staleness_rule": ("an artifact on disk whose digest is not listed here is STALE; "
                           "verification fails closed on staleness (§14)"),
    })
    written, changed = [], []
    for rel in sorted(files):
        path = outdir / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = files[rel].encode("utf-8")
        written.append(rel)
        if path.is_file() and path.read_bytes() == payload:
            continue                      # idempotence: a no-op run touches no byte
        path.write_bytes(payload)
        changed.append(rel)
    return written, changed


def check(run: dict, outdir: Path) -> list[str]:
    """Compare the on-disk build set with the fresh render.  Returns the list of
    stale/missing files (empty == current).  Extra files are drift too: an
    artifact nothing renders is an artifact nothing verifies."""
    problems = []
    expected = dict(run["files"])
    expected["manifest.json"] = None      # value checked by digest membership below
    for rel in sorted(expected):
        path = outdir / rel
        if not path.is_file():
            problems.append(f"missing: {rel}")
            continue
        if expected[rel] is None:
            continue
        if path.read_text(encoding="utf-8") != expected[rel]:
            problems.append(f"stale: {rel}")
    for path in sorted(outdir.rglob("*")) if outdir.is_dir() else []:
        if path.is_file():
            rel = str(path.relative_to(outdir))
            if rel not in expected:
                problems.append(f"unrendered artifact present: {rel}")
    return problems


def _inputs_note(run: dict, rel: str) -> str:
    ins = run["inputs_of"].get(rel) or []
    if not ins:
        return "inputs recorded in the stage's JSON artifact"
    names = ", ".join("`" + str(i.get("path")) + "`" for i in ins[:4])
    return f"{len(ins)} input artifact(s): {names}{'…' if len(ins) > 4 else ''}"


def published_pointers(run: dict) -> dict:
    """The durable, committed artifacts under `spec/0…-*/` — pointers and digests
    only, never copies of normative text (§20: no competing authority)."""
    ctx = run["ctx"]
    prov = C.provenance("PUB", inputs=[("build/spec/ (rendered in memory)", run["render_hash"])],
                        generators="scripts/spec/pipeline.py")
    return __import__("published").render(ctx, run, prov)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="python3 scripts/spec/pipeline.py",
                                 description="Controlled specification-processing pipeline (pre-M0).")
    ap.add_argument("source", nargs="?", default=str(REPO / "Red-on-Rust.md"),
                    help="frozen seed source (must be Red-on-Rust.md)")
    for flag, label, doc in STAGES:
        ap.add_argument(flag, action="store_true", help=f"{label}: {doc}")
    ap.add_argument("--all", action="store_true", help="full pipeline (default)")
    ap.add_argument("--out", default=str(REPO / "build/spec"), help="output directory (default build/spec)")
    ap.add_argument("--check", action="store_true",
                    help="render + cross-verify, write nothing; fail on any drift (gate mode)")
    ap.add_argument("--no-publish", "--verify-only", dest="no_publish", action="store_true",
                    help="render and run the S7 battery, write nothing")
    ap.add_argument("--report", action="store_true", help="print the §24 transformation report")
    ap.add_argument("--list", action="store_true", help="list stages and exit")
    ap.add_argument("--publish-derived", action="store_true",
                    help="(re)write the committed derived pointers under spec/00-…05-*/")
    ap.add_argument("--strict", action="store_true",
                    help="canonicalization refuses to run while an open BLOCKING/MAJOR finding bears "
                         "on it (default: carry and disclose, the policy spec/01 publishes under)")
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args(argv)

    if args.list:
        print(f"{C.PIPELINE_NAME} v{C.PIPELINE_VERSION} — {C.PIPELINE_MODE}")
        for flag, label, doc in STAGES:
            print(f"  {flag:<16} {label:<12} {doc}")
        print(f"\nentry point: python3 scripts/spec/pipeline.py Red-on-Rust.md")
        print(f"authority order (§5): frozen source > registries > governance dispositions > "
              f"this deterministic pipeline > derived artifacts > proposals > projections")
        return 0

    if args.strict:
        C.STRICT_CANONICALIZATION = True
    try:
        run = build_all(Path(args.source))
    except C.StageFailure as e:
        print(f"PIPELINE FAILED (fail-closed): {e}", file=sys.stderr)
        print("No canonical artifact was published. §19: a stage failure prevents publication.",
              file=sys.stderr)
        return 1

    # Stage flags select what is *reported*, never what is *executed*: a stage
    # that could run alone would be a stage whose failure the others could not see
    # (§19), so `build_all` always runs S0…S7 and the flags choose the summary.
    selected = [label.split(" ", 1)[0] for flag, label, _ in STAGES
                if getattr(args, flag[2:].replace("-", "_"), False)]
    if args.__dict__.get("publish_derived"):
        files = published_pointers(run)
        from report import render_report, REPORT_PATH        # noqa: WPS433
        files[REPORT_PATH] = render_report(run)
        changed = 0
        for rel, text in sorted(files.items()):
            path = REPO / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            if path.is_file() and path.read_text(encoding="utf-8") == text:
                continue
            path.write_text(text, encoding="utf-8")
            changed += 1
        print(f"published {len(files)} derived artifact(s) under spec/ ({changed} changed)")
        return 0
    if args.report:
        from report import render_report                     # noqa: WPS433 (local by design)
        print(render_report(run))
        return 0

    outdir = Path(args.out)
    problems = check(run, outdir) if (args.check or args.no_publish) else []
    if args.check and problems:
        print("PIPELINE FAILED (fail-closed): build/spec/ is not the current render:", file=sys.stderr)
        for p in problems:
            print("  " + p, file=sys.stderr)
        print("  fix: python3 scripts/spec/pipeline.py   (regenerate), then re-run the gate",
              file=sys.stderr)
        return 1
    if not (args.check or args.no_publish):
        written, changed = publish(run, outdir)
        print(f"published {len(written)} artifact(s) to {outdir} "
              f"({len(changed)} byte(s)-different; a no-op run writes nothing)")
    keys = {st["stage"]: st for st in run["stages"]}
    for key in (selected or ([s["stage"] for s in run["stages"]] if (args.all or args.verbose) else [])):
        st = keys.get(key)
        if st is None:
            continue
        name = dict((l.split(" ", 1)[0], l.split(" ", 1)[1]) for _, l, _ in STAGES).get(key, "")
        nfiles = sum(1 for v in run["stage_of"].values() if v == key)
        conf = [c for c in st["checks"] if c.get("kind", "conformance") != "disclosure"]
        disc = [c for c in st["checks"] if c.get("kind") == "disclosure"]
        print(f"{key} {name.lower()}: {sum(1 for c in conf if c['pass'])}/{len(conf)} conformance "
              f"predicates hold · {len(disc)} disclosure(s) · {nfiles} artifact(s)")
        for chk in st["checks"]:
            tag = "ok" if chk["pass"] else ("NOTE" if chk.get("kind") == "disclosure" else "FAIL")
            print(f"    {tag:<4} {chk['check']}"
                  + (f"  —  {str(chk['detail'])[:110]}" if chk["detail"] else ""))
    vdata = run["results"]["S7"]["data"]
    print(f"render {run['render_hash'][:23]}…  "
          f"artifacts {len(run['files'])}  requirements {vdata['counts']['requirements']}  "
          f"sections {vdata['counts']['sections']}  findings {vdata['counts']['audit_findings']}  "
          f"verification: {'PASS' if vdata['all_pass'] else 'FAIL'}  "
          f"M0: {vdata['m0']['status']}")
    return 0 if vdata["all_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
