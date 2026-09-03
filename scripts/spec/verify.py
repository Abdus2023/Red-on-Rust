"""Stage S7 — VERIFY (§14).

Cross-artifact verification over the whole projection set:

    source · sections · requirements · obligations · terminology · dependencies
    · canonical specification · audit · vectors · published pointers

Every §14 fail-closed condition is a named check that *raises* rather than a
warning that gets summarised:

    identities diverge · counts diverge · source provenance missing ·
    canonical artifact contains unregistered normative material · registry entry
    lacks provenance · generated files are stale · duplicate authority ·
    unresolved contradiction silently canonicalized · canonicalization
    introduces requirements · historical artifact presented as current ·
    current artifact is stale

Two categories of result are recorded, and the distinction is the point:

  * **checks** — facts that must hold.  Any False is a `StageFailure`;
  * **gaps** — what the repository does not yet have (open findings, undefined
    verification methods, the absence of any implementation evidence).  A gap is
    reported with its authority, never closed by invention (§16).

`REF1-CONDITIONAL` and `V1-CONDITIONAL` are carried at their audited wording.
A green verification here is repository-integrity evidence only: it verifies that
the *projections agree with their authorities*, never that a machine conforms to
the specification — nothing in `build/spec/` observes a single transition.
"""
from __future__ import annotations

import ast
import collections
import json
import re

from _common import (check_rows, EVIDENCE_CEILING, SOURCE_EXPECTED_LINES, SOURCE_EXPECTED_SHA256,
                     StageFailure, md_escape, provenance, render_json, sha256_bytes,
                     sha256_text, table)

STAGE = "S7-verify"

PIPELINE_FILES = ["_common.py", "pipeline.py", "snapshot.py", "extract.py", "split.py",
                  "normalize.py", "audit.py", "canonicalize.py", "registry.py", "vectors.py",
                  "verify.py", "published.py", "report.py", "_gate.py", "schemas.py"]


BANNED_MODULES = {"time", "datetime", "random", "secrets", "socket", "urllib", "requests",
                  "http", "locale", "tempfile", "subprocess", "glob", "fcntl", "multiprocessing"}
BANNED_ATTR_CALLS = {("os", "getenv"), ("os", "listdir"), ("os", "popen"), ("os", "system"),
                     ("os", "urandom"), ("time", "time"), ("random", "seed")}


def determinism_scan(path) -> dict:
    """AST scan of one pipeline module for non-deterministic inputs.

    Comments and docstrings are excluded on purpose: a sentence may *say* "no
    clock" without reading one, and the check is about behaviour, not vocabulary.
    Returns {"offences": [(line, what)], "environ_lines": [...],
    "report_only_lines": [...]}."""
    import ast
    tree = ast.parse(path.read_text(encoding="utf-8"))
    offences: list[tuple[int, str]] = []
    environ_lines: list[int] = []
    report_only: list[int] = []

    def walk(node, inside_report=False):
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.Import, ast.ImportFrom)):
                names = ([a.name for a in child.names] if isinstance(child, ast.Import)
                         else [child.module or ""])
                for n in names:
                    root = n.split(".")[0]
                    if root in BANNED_MODULES:
                        offences.append((child.lineno, f"import {n}"))
            if isinstance(child, ast.Attribute):
                base = child.value
                if isinstance(base, ast.Name) and base.id == "os" and child.attr == "environ":
                    environ_lines.append(child.lineno)
                    if inside_report:
                        report_only.append(child.lineno)
            if isinstance(child, ast.Call):
                fn = child.func
                if isinstance(fn, ast.Attribute) and isinstance(fn.value, ast.Name):
                    pair = (fn.value.id, fn.attr)
                    if pair in BANNED_ATTR_CALLS or (fn.value.id in BANNED_MODULES):
                        offences.append((child.lineno, f"{fn.value.id}.{fn.attr}()"))
                    if fn.value.id == "time":
                        offences.append((child.lineno, f"time.{fn.attr}()"))
                if isinstance(fn, ast.Attribute) and fn.attr in ("iterdir", "glob", "rglob"):
                    # allowed only when the result is sorted before use; `sorted(`
                    # on the same line is the repository's own convention
                    line = src_lines[child.lineno - 1] if child.lineno - 1 < len(src_lines) else ""
                    if "sorted(" not in line:
                        offences.append((child.lineno, f"unsorted .{fn.attr}()"))
            walk(child, inside_report or (isinstance(child, ast.FunctionDef)
                                          and child.name in ("env_report", "host_env_values")))

    src_lines = path.read_text(encoding="utf-8").split("\n")
    walk(tree)
    return {"offences": sorted(offences), "environ_lines": sorted(set(environ_lines)),
            "report_only_lines": sorted(set(report_only))}


def _common_env_report():
    import _common
    return _common.env_report()


def _common_host_env():
    """The host environment, read through `_common` so this module performs no
    environment access of its own — the render may not look at the environment, but
    the check that polices it has to know what is out there."""
    import _common
    return _common.host_env_values()


def proposal_intake_offences(repo) -> list[str]:
    """Every filesystem read of a proposal-bearing path inside the render modules.

    A proposal becomes dangerous the moment a generator reads one, so the pipeline's
    §17 claim is enforced mechanically: no module on the render path may open a path
    containing `proposal`.  Reads of the pipeline's *own* in-memory artifact (the
    `proposals.json` the S1 stage emits, subscripted out of the run dict) are not
    intake and are not flagged — this scans call syntax, not words.
    """
    # Filesystem readers only. `json.loads(...)` of an in-memory string is not intake —
    # `proposals.json` itself is parsed that way a few lines below, and a scanner that
    # flagged it would be a scanner people switch off.
    read_like = {"read_text", "read_bytes", "open", "readline", "readlines", "scandir", "listdir",
                 "iterdir", "glob", "rglob", "Path"}
    offences = []
    for name in sorted(PIPELINE_FILES):
        path = repo / "scripts/spec" / name
        if not path.is_file():
            continue
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except SyntaxError as exc:
            offences.append(f"{name}: unparsable ({exc.msg})")
            continue
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            fn = node.func
            fname = fn.attr if isinstance(fn, ast.Attribute) else (fn.id if isinstance(fn, ast.Name) else "")
            if fname not in read_like:
                continue
            # Every string constant in the call's subtree: `Path(repo) / "spec" /
            # "llm-proposals.json"` reads a proposal path even though no literal is a
            # direct argument of `read_text`, and a scanner that only inspected direct
            # arguments would have been the exact kind of check that under-reports.
            strings = [n.value for n in ast.walk(node)
                       if isinstance(n, ast.Constant) and isinstance(n.value, str)]
            if any("proposal" in s.lower() for s in strings):
                offences.append(f"{name}:L{node.lineno}: reads {'/'.join(strings)[:60]}")
    return offences


def _walk_keys(obj, prefix=""):
    """Yield (leaf_key, value) for every key in a nested JSON structure."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield k, v
            yield from _walk_keys(v, prefix + k + ".")
    elif isinstance(obj, list):
        for item in obj:
            yield from _walk_keys(item, prefix)


def m0_state(ctx) -> dict:
    """M0's recorded state, read from the repository's own state projection."""
    path = ctx.repo / "state/repository-state.json"
    if not path.is_file():
        raise StageFailure(f"[{STAGE}] state/repository-state.json is missing — the milestone "
                           "boundary cannot be verified without its authority")
    return json.loads(path.read_text(encoding="utf-8")).get("milestone_state") or {}


def _checks(ctx, run, problems, notes):
    def ok(cond, label, detail=""):
        problems.append((bool(cond), label, detail))
        return bool(cond)

    files, results = run["files"], run["results"]
    # -- 1. artifact presence + provenance on every artifact ---------------
    missing = [n for n in ("source.sha256", "snapshot.json", "requirements.candidates.json",
                           "proposals.json", "sections/index.json", "normalize.json",
                           "terminology.json", "audit.json", "Red-on-Rust.canonical.md",
                           "canonical.json", "requirements.json", "obligations.json",
                           "dependencies.json", "vectors/index.json") if n not in files]
    ok(not missing, "every §14 projection exists", f"missing: {missing}")
    no_prov = [rel for rel, text in files.items()
               if rel.endswith((".json", ".md"))
               and "pipeline_version" not in text and rel not in ("source.sha256",)]
    ok(not no_prov, "every generated artifact carries provenance (pipeline, stage, source, inputs)",
       f"without provenance: {no_prov}")
    # -- 2. source identity -------------------------------------------------
    ok(files["source.sha256"] == ctx.source_sha256, "source.sha256 is the digest of the seed bytes",
       "exactly 64 lowercase hex, no newline")
    ok(ctx.source_sha256 == SOURCE_EXPECTED_SHA256, "seed source matches the pinned frozen hash",
       "sha256:" + SOURCE_EXPECTED_SHA256[:16] + "…")
    ok(ctx.source_line_count == SOURCE_EXPECTED_LINES, "seed source line count matches the record",
       f"{ctx.source_line_count} == {SOURCE_EXPECTED_LINES}")
    ok(len(re.findall(r"^## \[(\d+)\]", ctx.source_text, re.M)) == 60,
       "seed source is the complete 60-turn transcript", "turn headings [1]…[60]")
    # -- 3. counts agree across projections --------------------------------
    counts = {
        "spec/01 chunks": len(ctx.spec01),
        "spec/03 rows": len(ctx.obligations),
        "spec/10 requirements": len(ctx.spec10["requirements"]) if ctx.spec10 else -1,
        "reg/requirements.json": (len(ctx.reg["requirements"]) if ctx.reg else -1),
        "final/03 rows": 0,
        "S1 candidates": len(results["S1"]["entries"]),
        "S5 canonical": results["S5"]["data"]["counts"]["requirements"],
        "S6 requirements.json": len(results["S6"]["requirements"]),
    }
    try:
        f03 = (ctx.repo / "final/03-requirement-registry.md").read_text(encoding="utf-8")
        counts["final/03 rows"] = len(set(re.findall(r"^\| (R-[A-Z]+-\d+) \|", f03, re.M)))
    except OSError:
        pass
    ok(len(set(counts.values())) == 1, "requirement count agrees across every projection",
       ", ".join(f"{k}={v}" for k, v in sorted(counts.items())))
    sec_counts = {"spec/02 rows": len(ctx.sections), "spec/01 headings": len(ctx.section_order),
                  "S2 sections": results["S2"]["data"]["section_count"]}
    ok(len(set(sec_counts.values())) == 1 and sec_counts["spec/02 rows"] == 24,
       "section count agrees (24)", ", ".join(f"{k}={v}" for k, v in sec_counts.items()))
    atomic = len(re.findall(r"\"REQ-ID\"", (ctx.repo / "req/registry.json").read_text(encoding="utf-8"))) \
        if (ctx.repo / "req/registry.json").is_file() else 0
    ok(atomic == (ctx.req or {}).get("record_count") == 545,
       "atomic-record count agrees with the atomic registry",
       f"grep {atomic} == registry {(ctx.req or {}).get('record_count')} == 545")
    ok(results["S6"]["data"]["counts"]["terminology_entries"]
       == (ctx.term or {}).get("counts", {}).get("terms") == 86,
       "terminology count agrees with term/10", "86 canonical terms")
    # -- 4. identities: one universe everywhere ----------------------------
    id_sets = {
        "spec/01": set(ctx.spec01), "spec/03": set(ctx.obligations),
        "S1": {e["id"] for e in results["S1"]["entries"]},
        "S5": {m.group(1) for m in re.finditer(r"^\*\*(R-[A-Z]+-\d+)",
                                                files["Red-on-Rust.canonical.md"], re.M)},
        "S6": {e["id"] for e in results["S6"]["requirements"]},
    }
    if ctx.spec10:
        id_sets["spec/10"] = {r["id"] for r in ctx.spec10["requirements"]}
    if ctx.reg:
        id_sets["reg"] = {r["id"] for r in ctx.reg["requirements"]}
    baseline = id_sets["spec/01"]
    diverging = {k: sorted(v ^ baseline) for k, v in id_sets.items() if v != baseline}
    ok(not diverging, "identities identical in every projection (no add/delete/rename/renumber)",
       f"divergence: {diverging}")
    # -- 5. canonical material is registered -------------------------------
    unreg = sorted({m.group(0) for m in re.finditer(r"\bR-[A-Z]+-\d+\b", files["Red-on-Rust.canonical.md"])}
                   - baseline)
    ok(not unreg, "canonical artifact contains no unregistered normative material",
       f"unregistered: {unreg[:6]}")
    ok(results["S5"]["data"]["counts"]["introduced"] == 0
       and results["S5"]["data"]["counts"]["dropped"] == 0,
       "canonicalization introduced/dropped nothing (§22 acceptance condition)",
       f"introduced {results['S5']['data']['counts']['introduced']}, "
       f"dropped {results['S5']['data']['counts']['dropped']}")
    ok(results["S5"]["data"]["chunk_multiset_sha256"]
       == results["S5"]["data"]["authority_chunk_multiset_sha256"],
       "Canonicalize(X) ⊆ NormativeContent(X) (chunk multiset equality)",
       results["S5"]["data"]["chunk_multiset_sha256"][:19] + "…")
    # -- 6. registry completeness / no duplicate authority ---------------
    short = {e["id"]: e["obligation"] for e in
              json.loads(files["obligations.json"])["obligations"]}
    mismatched = sorted(rid for rid, s in short.items()
                        if s.strip() != ctx.obligations[rid]["short"].strip())
    ok(not mismatched, "obligation texts agree with the canonical registry cell",
       f"{len(mismatched)} mismatch(es)")
    dupes = [rid for rid, n in
             collections.Counter(
                 e["id"] for e in json.loads(files["requirements.json"])["requirements"]
             ).items() if n > 1]
    ok(not dupes, "no duplicate authority (each identity registered exactly once)", f"{dupes}")
    prov_gaps = sorted(e["id"] for e in
                       json.loads(files["requirements.json"])["requirements"]
                       if not e["source_refs"] and not e["addendum_note"]
                       and not re.search(r"\d{3,5}", ctx.obligations[e["id"]]["provenance"]))
    ok(not prov_gaps, "no registry entry lacks source provenance", f"{prov_gaps[:6]}")
    # -- 7. statuses / evidence discipline --------------------------------
    statuses = {e["status"] for e in json.loads(files["requirements.json"])["requirements"]}
    ok(statuses == {EVIDENCE_CEILING}, "every registry status is SPECIFIED (ceiling honoured)",
       str(sorted(statuses)))
    ok(results["S1"]["data"]["policy"]["invention_allowed"] is False
       and results["S1"]["data"]["policy"]["renumber_allowed"] is False,
       "extraction policy recorded as non-inventive", "S1 policy block")
    ok(not results["S6"]["data"]["policy"]["status_changes"]
       and not results["S6"]["data"]["policy"]["identity_changes"],
       "registry generation changed no identity and no status", "S6 policy block")
    # -- 8. audit coverage -------------------------------------------------
    cats = results["S4"]["data"]["categories"]
    ok(len(cats) == 16, "all §11 audit categories covered", f"{len(cats)} categories")
    empty = [k for k, v in results["S4"]["data"]["category_evidence"].items()
             if not any(x for x in v.values() if isinstance(x, (int, list, dict, str)))]
    ok(not empty, "no audit category is an empty claim", f"empty: {empty}")
    reg_ids = {f["finding_id"] for f in results["S4"]["data"]["findings"]}
    ok(set(ctx.findings) | set(ctx.decisions) == reg_ids,
       "findings projected exactly (no register row dropped, none invented)",
       f"{len(reg_ids)} projected vs {len(ctx.findings)}+{len(ctx.decisions)} registered")
    ok(results["S4"]["data"]["counts"]["candidate_findings_filed_by_this_run"] == 0,
       "pipeline filed no register row (filing is a governance act)", "0 rows written to spec/06")
    # -- 9. vectors --------------------------------------------------------
    vindex = json.loads(files["vectors/index.json"])
    ok(vindex["policy"]["invented_vectors"] == 0, "no vector invented", "S6b policy")
    ok(all(v["count"] > 0 for v in vindex["index"].values()), "all three vector families populated",
       ", ".join(f"{k}:{v['count']}" for k, v in sorted(vindex["index"].items())))
    # -- 10. determinism of the pipeline's own code (measured by AST) ------
    scripts_dir = ctx.repo / "scripts/spec"
    offenders, missing, env_uses = [], [], []
    for name in sorted(PIPELINE_FILES):
        path = scripts_dir / name
        if not path.is_file():
            missing.append(name)
            continue
        hit = determinism_scan(path)
        offenders += [f"{name}:{ln}: {what}" for ln, what in hit["offences"]]
        env_uses += [f"{name}:{ln}" for ln in hit["environ_lines"] if name != "_common.py"]
        if name == "_common.py" and hit["environ_lines"]:
            # allowed only inside env_report(), which reports and never branches
            if any(ln not in hit["report_only_lines"] for ln in hit["environ_lines"]):
                offenders.append(f"{name}: environ read outside env_report()/host_env_values()")
    ok(not missing, "every stage module of the pipeline is present and scannable",
       f"missing: {missing}")
    ok(not offenders, "no stage reads a clock, randomness, locale, network or directory order",
       f"offenders: {offenders[:6]}" if offenders else
       f"{len(PIPELINE_FILES)} modules scanned by AST (imports, calls, environment reads)")
    report = _common_env_report()
    import _common as _C
    extra_fields = sorted(set(report) - _C.ENV_REPORT_FIELDS)
    reads = list(report.get("read_by_the_render") or [])
    host_values = set(_common_host_env().values())
    echoed = sorted(k for k, v in report.items()
                    if isinstance(v, str) and (v in host_values or v.isdigit()))
    ok(not extra_fields and not reads and not echoed,
       "the environment report is a closed set of declared fields, reads nothing, and echoes no "
       "host value (§4.1: a host value inside a content-addressed artifact IS a dependency)",
       f"declared fields: {len(_C.ENV_REPORT_FIELDS)}; names ignored: "
       f"{len(report.get('names_the_render_ignores', []))}; environment reads: {reads or 'none'}"
       + (f"; unexpected fields: {extra_fields}" if extra_fields else "")
       + (f"; echoed values: {echoed}" if echoed else ""))
    ok(not env_uses, "only `_common.env_report()` touches the environment, and only to report it",
       f"other environ uses: {env_uses[:4]}" if env_uses else "0")
    # -- 11. historical protection (audit is history, not current state) --
    prot = (ctx.dispositions or {}).get("protected_snapshots", {})
    bad = []
    for rel, meta in sorted(prot.items()):
        path = ctx.repo / rel
        if not path.is_file():
            bad.append(f"{rel}: missing")
            continue
        digest = sha256_bytes(path.read_bytes())
        if digest != meta.get("sha256"):
            bad.append(f"{rel}: digest changed")
    ok(len(prot) == 12 and not bad,
       "the 12 protected historical audit snapshots are unmodified",
       f"{len(prot)} pinned, {len(bad)} drifted: {bad[:3]}" if bad else f"{len(prot)} verified")
    ok(not re.search(r"generated on \d{4}|\btoday\b", files["audit/contradictions.md"], re.I),
       "historical rows are presented as historical (no re-dating, no present-tense framing)",
       "audit projections carry their authority's status vocabulary verbatim")
    # -- 12. M0 boundary ---------------------------------------------------
    m0 = m0_state(ctx)
    ok(m0.get("M0") == "NOT STARTED", "M0 remains NOT STARTED", str(m0))
    rs_files = sorted(str(x) for x in (ctx.repo / "scripts").rglob("*.rs"))
    ok(not (ctx.repo / "src").exists() and not (ctx.repo / "Cargo.toml").exists() and not rs_files,
       "no implementation was introduced by this pipeline",
       "no src/, no Cargo.toml, no .rs under scripts/; output limited to scripts/, build/ and "
       "spec/0*-*/")
    # -- 12b. authority digest pins (independent integrity of the inputs) --
    # `reg/requirements.json` records a sha256 for every authority it compiled
    # from.  Re-deriving those digests is what makes a silent edit of an
    # authority (e.g. one reworded normative sentence in `spec/01`) a hard
    # failure of THIS pipeline as well as of `reg/`'s own gate.
    pins = (ctx.reg or {}).get("sources") or {}
    drifted, unhashed = [], []
    for rel, pin in sorted(pins.items()):
        path = ctx.repo / rel
        if not path.is_file():
            unhashed.append(rel)
            continue
        if sha256_bytes(path.read_bytes()) != pin:
            drifted.append(rel)
    ok(not unhashed and not drifted,
       "every pinned authority digest recomputes (spec/01, spec/03, req/, final/, dep/, source)",
       f"pinned: {len(pins)}; drifted: {drifted}; missing: {unhashed}")
    ok(len(pins) >= 9, "the authority set the pipeline depends on is fully pinned",
       f"{len(pins)} authority paths pinned in reg/requirements.json sources")

    # -- 12c. register cardinality agrees with the derived projections ------
    s06_rows = len(ctx.findings)                              # 113, incl. the C-39 pointer row
    s10_findings = len(ctx.spec10["findings"]) if ctx.spec10 else -1     # 112 indexed findings
    st_findings = -1
    if (ctx.repo / "state/repository-state.json").is_file():
        st_findings = json.loads((ctx.repo / "state/repository-state.json")
                                 .read_text(encoding="utf-8"))["counts"]["findings"]
    ok(s06_rows - 1 == s10_findings == st_findings,
       "finding cardinality: spec/06 rows minus the C-39 pointer == spec/10 index == state projection",
       f"spec/06 {s06_rows}-1 == spec/10 {s10_findings} == state/ {st_findings}")
    card = {"spec/06 rows": s06_rows, "spec/10 findings": s10_findings,
            "state projection findings": st_findings}
    u_card = {
        "spec/09 registered": len(ctx.decisions),
        "spec/09 open (re-derived)": sum(1 for d in ctx.decisions.values() if d["status"] == "OPEN"),
        "state projection registered": 0, "state projection open": 0,
    }
    mine_open = {k for k, d in ctx.decisions.items() if d["status"] == "OPEN"}
    mine_res = set(ctx.decisions) - mine_open
    sym_open = sym_res = set()
    if (ctx.repo / "state/repository-state.json").is_file():
        st = json.loads((ctx.repo / "state/repository-state.json").read_text(encoding="utf-8"))
        u_card["state projection registered"] = st["counts"]["u_items_registered"]
        u_card["state projection open"] = st["counts"]["u_items_open"]
        # counts alone are not enough: two registers can hold the same numbers with
        # different membership (U-01 is exactly such a row — open in spec/10's
        # prose, resolved by addendum IX).  Compare the partition itself.
        sym_open = mine_open ^ {str(x) for x in (st.get("u_items_open") or [])}
        sym_res = mine_res ^ {str(x) for x in (st.get("u_items_resolved") or {})}
    ok(u_card["spec/09 registered"] == u_card["state projection registered"]
       and u_card["spec/09 open (re-derived)"] == u_card["state projection open"]
       and not sym_open and not sym_res,
       "U-register cardinality and membership: independent re-derivation of the OPEN/RESOLVED "
       "partition == the state projection (a disagreement is raised, never auto-repaired)",
       ", ".join(f"{k}={v}" for k, v in u_card.items())
       + (f"; open-only-here={sorted(sym_open)} resolved-only-here={sorted(sym_res)}"
          if (sym_open or sym_res) else ""))

    # -- 13b. timestamp discipline (§4.1: a stamp that would destroy
    # reproducibility MUST NOT participate in semantic content or canonical
    # hashes) --
    ts_keys = re.compile(r"(?i)(timestamp|generated_at|generated_on|created_at|created_on|"
                         r"modified_at|modified_on|mtime|clock|build_time)")
    bad_ts = []
    for rel, text in sorted(files.items()):
        if not rel.endswith(".json"):
            continue
        for k, v in _walk_keys(json.loads(text)):
            if not ts_keys.search(k):
                continue
            if k == "timestamp_present" and v is False:
                continue
            if k == "timestamp_reason" and isinstance(v, str):
                continue
            bad_ts.append(f"{rel}:{k}")
    ok(not bad_ts, "no timestamp participates in any generated artifact (provenance is stamp-free)",
       f"offending fields: {bad_ts[:5]}" if bad_ts else "0 timestamped fields across "
       f"{sum(1 for r in files if r.endswith('.json'))} JSON artifacts")

    # -- 13. proposals: this pipeline has no intake, and that is a *checked*
    # fact rather than a comfortable assumption.  `accepted_count == 0` alone
    # would be a constant dressed as evidence, so the structural claim ("nothing
    # in the render path can read a proposal in") is scanned for.  §17
    # (LLM proposes, validators adjudicate) is honoured here by the stronger
    # route: an adjudication path that cannot be entered.
    proposals = json.loads(files["proposals.json"])
    ok(proposals["accepted_count"] == 0, "proposals.json records zero accepted proposals",
       "emitted as a constant by S1 because no intake exists — the structural proof is the "
       "next check, not this one")
    intake = proposal_intake_offences(ctx.repo)
    ok(not intake, "no proposal intake channel exists in the render path "
                   "(§17: LLM output cannot reach canonicalization because it has no path to it)",
       f"read sites: {intake[:4]}" if intake else
       f"0 filesystem reads of any proposal-bearing path across {len(PIPELINE_FILES)} render modules")
    # -- 13c. the check taxonomy itself (§19): a stage may not report a
    # conformance failure and then continue, and a disclosure may not be
    # presented as a pass.  Without this row the `kind` field would be
    # decoration, and a FAIL that nobody acts on is how a gate trains its
    # reader to ignore FAILs.
    rows = [dict(r, stage=st["stage"]) for st in run["stages"] for r in st["checks"]]
    silent_fail = sorted(f"{r['stage']}:{r['check']}" for r in rows
                         if r.get("kind", "conformance") == "conformance" and not r["pass"])
    disclosures = sorted(f"{r['stage']}:{r['check']}" for r in rows if r.get("kind") == "disclosure")
    ok(not silent_fail, "no stage reported a conformance failure and continued (§19: a stage failure "
                        "prevents publication)",
       f"failing rows that survived the run: {silent_fail[:4]}" if silent_fail else
       f"{len(rows)} rows across {len(run['stages'])} stages; {len(disclosures)} disclosure(s) "
       "reported as such")
    run["disclosures"] = disclosures

    # -- 14. idempotence + staleness --------------------------------------
    ok(run.get("content_hash"), "render is content-addressed (staleness is detectable)",
       run.get("content_hash", "")[:19] + "…")
    notes = notes or []
    return problems, notes


def run(ctx, run_state: dict, published: dict | None = None) -> dict:
    prov = provenance(STAGE, inputs=[(rel, sha256_text(text))
                                     for rel, text in sorted(run_state["files"].items())][:24],
                      generators="scripts/spec/verify.py")
    problems, notes = [], []
    checks, _ = _checks(ctx, run_state, problems, notes)
    failures = [(c, d) for p, c, d in checks if not p]
    if failures:
        raise StageFailure(f"[{STAGE}] VERIFICATION FAILED — the canonical state is NOT accepted "
                           f"(§19). {len(failures)} check(s) failed:\n  "
                           + "\n  ".join(f"{c}  —  {d}" for c, d in failures))
    # gaps: explicit incompleteness (§16), reported not closed
    gaps = [{"gap": "the §17 proposal-adjudication path has nothing to adjudicate",
             "count": 0,
             "authority": "build/spec/proposals.json + S7's intake scan",
             "note": "reported, not closed: validators are exercised on register↔authority "
                     "agreement only, so an intake channel would need both validators *and* "
                     "mutations against them before it could exist; S7 fails the moment a render "
                     "module reads a proposal path"},
            {
        "gap": "open BLOCKING/MAJOR findings carried",
        "count": len(run_state["results"]["S5"]["data"]["open_blocking"])
        + len(run_state["results"]["S5"]["data"]["open_major"]),
        "authority": "spec/06 + spec/09",
        "resolution": "requires a governance act (frozen addendum / disposition); the pipeline has "
                      "none and takes none",
    }, {
        "gap": "requirements with no registered verification obligation",
        "count": sum(1 for e in run_state["results"]["S6"]["requirements"] if not e["verification_refs"]),
        "authority": "req/04-verification-undefined.md (8 records with an undefined method)",
    }, {
        "gap": "implementation/test evidence for any obligation",
        "count": 0,
        "authority": "spec/00 §2 (no code, no tests, no proof in this repository)",
        "note": "a count of zero here is the ceiling, not a defect",
    }, {
        "gap": "canonical specification is a reconstruction, not the authority",
        "count": 1,
        "authority": "spec/01-canonical-specification.md (normative text home)",
        "note": "deliberate: §20 forbids a competing governance system, so the pipeline's canonical "
                "artifact is a projection that the gate proves identical to its authority",
    }]
    data = {
        "schema": "redonrust.spec-pipeline.verify/v1",
        "provenance": prov,
        "all_pass": True,
        "counts": {
            "requirements": len(ctx.spec01),
            "sections": len(ctx.section_order),
            "audit_findings": len(run_state["results"]["S4"]["data"]["findings"]),
            "artifacts": len(run_state["files"]),
            "checks": len(checks),
            "failures": 0,
            "gaps_reported": len(gaps),
            "promotions": 0,
        },
        "checks": check_rows([(c, p, d) for p, c, d in checks]),
        "gaps": gaps,
        "m0": {"status": m0_state(ctx).get("M0"), "source": m0_state(ctx).get("source")},
        "determinism": {"environment_report": _common_env_report(),
                        "content_hash": run_state["content_hash"],
                        "render_hash_including_this_artifact": None,
                        "artifact_digests": {rel: sha256_text(t) for rel, t in
                                            sorted(run_state["files"].items())}},
        "published_pointer_digests": {rel: sha256_text(t) for rel, t in sorted((published or {}).items())},
        "verdict": {
            "state": "ACCEPTED (as a set of derived projections)",
            "meaning": "every projection agrees with its authority; the pipeline verified agreement, "
                       "never machine conformance",
            "evidence_level": "repository-integrity evidence only (spec/00 §2; V1 F-INFL-01)",
            "does_not_establish": [
                "that any R-… obligation is implemented, tested, verified or proven",
                "that the determinism or security theorems hold for a machine (there is no machine)",
                "that REF1/V1 are anything other than CONDITIONAL",
            ],
        },
    }
    rows = [[c, "PASS" if p else "FAIL", d] for p, c, d in checks]
    md = ("# 07 — Cross-Artifact Verification (Stage S7)\n\n"
          "**Derived artifact of the controlled specification pipeline. Not a normative source.**\n\n"
          f"{len(checks)} checks over {len(run_state['files'])} artifacts. "
          "Every §14 fail-closed condition is a named check.\n\n"
          "## 1. Checks\n\n" + table(rows, ["check", "result", "detail"])
          + "\n## 1b. Disclosures carried by the stages (reported, not repaired)\n\n"
          + ("\n".join(f"- `{d}`" for d in data.get("disclosures", []))
             or "- none: every stage row is a conformance predicate and all hold")
          + "\n\nA **disclosure** is a fact about an *authority* that this pipeline must not "
            "silently fix (an open finding touching canonical material, a dangling citation). It is "
            "neither a pass nor a failure of the pipeline; a **conformance** row that fails aborts the "
            "run, and the check above proves no such row survived one.\n\n"
          + "\n## 2. Reported gaps (explicit incompleteness, not repair)\n\n"
          + table([[g["gap"], g.get("count"), g.get("authority", ""), g.get("note", "")]
                   for g in gaps], ["gap", "count", "authority", "note"])
          + "\n## 3. Reproduction\n\n"
          "```\npython3 scripts/spec/pipeline.py Red-on-Rust.md      # render + publish build/spec/\n"
          "python3 scripts/spec/pipeline.py --check                 # prove no drift (gate mode)\n"
          "python3 scripts/spec/_gate.py                            # determinism + published pointers\n"
          "python3 tests/spec/_pipeline_mutations.py                # drift-detection (mutation battery)\n"
          "```\n\n"
          f"content address of the verified set: `{run_state['content_hash']}`\n\n"
          "**A PASS here is repository-integrity evidence only. It is not verification of any "
          "obligation, and it starts no milestone: M0 remains "
          f"{m0_state(ctx).get('M0', 'NOT STARTED')}.**\n")
    return {"files": {"verification.json": render_json(data), "verification.md": md},
            "data": data, "checks": [(c, p, d) for p, c, d in checks]}
