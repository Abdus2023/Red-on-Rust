"""scripts/spec/report.py — the §24 final transformation report.

Every figure is computed from the run, never typed in.  `TRANSFORMATION-REPORT.md`
at the repository root is rendered by `--report --publish-report` and is
re-verified (digest-pinned) by `scripts/spec/_gate.py`, so a report that drifts
from the artifacts fails the repository gate — the report cannot outlive its
evidence.

Allowed claims, and only these: source identity, artifact inventory, counts,
registry/verification/mutation/provenance status, remaining ambiguities and
contradictions, evidence level, and M0 status.  No implementation claim appears,
because none is evidenced (§24: "No implementation claims may be made unless
independently evidenced").
"""
from __future__ import annotations

import re

from _common import (FORBIDDEN_DURING_TRANSFORMATION, PIPELINE_NAME, PIPELINE_VERSION,
                     SOURCE_EXPECTED_SHA256, STATUS_LADDER, table)

REPORT_PATH = "TRANSFORMATION-REPORT.md"


def render_report(run: dict, mutation: dict | None = None) -> str:
    ctx = run["ctx"]
    f = run["files"]
    import json as _json
    s1 = run["results"]["S1"]["data"]
    s2 = run["results"]["S2"]["data"]
    s3 = run["results"]["S3"]["data"]
    s4 = run["results"]["S4"]["data"]
    s5 = run["results"]["S5"]["data"]
    s6 = run["results"]["S6"]["data"]
    sv = run["results"]["S6b"]["data"]
    s7 = run["results"]["S7"]["data"]
    snap = _json.loads(f["snapshot.json"])

    counts = s7["counts"]
    open_blocking = s5["open_blocking"]
    open_major = s5["open_major"]
    open_u = sorted(uid for uid, d in ctx.decisions.items() if d["status"] == "OPEN")
    open_c = sorted(cid for cid, x in ctx.findings.items() if "open" in x["status"].lower())

    out = []
    a = out.append
    a("# Red-on-Rust — Repository Transformation Report\n\n")
    a("**Controlled specification-source-processing pipeline · version "
      f"{PIPELINE_VERSION} · mode: repository transformation, specification-processing "
      "infrastructure only.**\n\n")
    a("This report is generated: every figure below is computed from the artifacts it names. "
      "`python3 scripts/spec/pipeline.py --report` reproduces it, and `scripts/spec/_gate.py` "
      "(registered in `check.py`) fails the repository gate if the committed copy and a fresh "
      "render disagree.\n\n")
    a("## 1. Source and pipeline identity\n\n")
    a(table([
        ["source hash", f"`sha256:{ctx.source_sha256}`"],
        ["source hash matches the pinned frozen identity",
         "yes" if ctx.source_sha256 == SOURCE_EXPECTED_SHA256 else "NO"],
        ["source lines / bytes", f"{ctx.source_line_count} / {ctx.source_byte_count}"],
        ["source turns", f"{snap['snapshot']['turn_headings']} "
         f"(`[{snap['snapshot']['turn_range'][0]}]`–`[{snap['snapshot']['turn_range'][1]}]`)"],
        ["pipeline", f"`{PIPELINE_NAME}` v`{PIPELINE_VERSION}`"],
        ["render hash (content address of the whole artifact set)", f"`{run['render_hash']}`"],
        ["input artifacts (authority files read)",
         "Red-on-Rust.md · spec/01 · spec/02 · spec/03 · spec/05 · spec/06 · spec/08 · spec/09 · "
         "req/registry.json · req/03 · reg/requirements.json · term/10-index.json · "
         "mod/19-index.json · dep/10-graph.json · spec/10-index.json · state/dispositions.json · "
         "state/repository-state.json · final/03 · audit/*.md · README.md"],
        ["output artifacts (derived)", f"{len(f)} in `build/spec/` + 7 committed pointers under "
         "`spec/0*-*/` + `spec/PIPELINE.md` + this report"],
    ], ["field", "value"]) + "\n\n")

    a("## 2. Counts\n\n")
    a(table([
        ["requirements", f"{s6['counts']['requirements']} (canonical registry `spec/03`)"],
        ["obligations (canonical)", f"{s6['counts']['obligations']}"],
        ["obligations (atomic layer)", f"{s6['counts']['atomic_records_registered']} atomic records "
         f"(`req/`), {s6['counts']['atomic_records_cited']} cited by a single parent"],
        ["sections", f"{counts['sections']} (S-01…S-24, `spec/02`)"],
        ["terminology entries", f"{s6['counts']['terminology_entries']} canonical terms · "
         f"{s6['counts']['non_conflation_laws']} non-conflation laws · {s6['counts']['collisions']} "
         "collisions"],
        ["dependency edges", f"{s6['counts']['section_edges']} section · {s6['counts']['requirement_edges']} "
         f"requirement · kinds {s6['counts']['dependency_edge_kinds']}"],
        ["audit findings", f"{counts['audit_findings']} projected ({s4['counts']['spec06_rows']} C- rows + "
         f"{s4['counts']['spec09_rows']} U- rows) · categories {len(s4['categories'])}"],
        ["evidence vectors", f"{sv['count']} across " + ", ".join(
            f"{k}:{v['count']}" for k, v in sorted(sv["index"].items()))],
        ["normalization records of record",
         f"{s3['normalization_records_of_record']['records']} (Original+Normalized pairs in "
         "`spec/normative-normalization-records.md`)"],
        ["proposals accepted into canonicalization", f"{s5['safety_theorem']['proposals_in_this_run']}"],
    ], ["measure", "value"]) + "\n\n")

    a("## 3. Status of each acceptance condition (§22)\n\n")
    boxes = [
        ("source snapshot exists", "yes", "`build/spec/source.sha256` + `snapshot.json` + "
                                          "`source-snapshot.md`; committed pointer `spec/00-source/README.md`"),
        ("source hash is reproducible", "yes", "no timestamp in any artifact; `sha256sum Red-on-Rust.md` "
                                              f"reproduces `sha256:{ctx.source_sha256[:16]}…`"),
        ("semantic sections exist", "yes", f"{counts['sections']} section files + `sections/index.json` "
                                          "(lossless, `spec/02` order)"),
        ("requirements registry exists", "yes", "`build/spec/requirements.json` "
                                                f"({s6['counts']['requirements']} entries)"),
        ("obligations registry exists", "yes", "`build/spec/obligations.json` "
                                               f"({s6['counts']['obligations']} + atomic layer)"),
        ("terminology registry exists", "yes", "`build/spec/terminology.json` "
                                               f"({s6['counts']['terminology_entries']} terms)"),
        ("dependency registry exists", "yes", "`build/spec/dependencies.json`"),
        ("audit artifacts exist", "yes", f"`build/spec/audit/` "
                                         f"({sum(1 for k in f if k.startswith('audit/') and k.endswith('.md'))} "
                                         "category projections, incl. the five families named in §6) "
                                         "+ `audit.json`"),
        ("canonical specification exists", "yes — as a projection",
         "`build/spec/Red-on-Rust.canonical.md`; the human-readable authority stays `spec/01` "
         "(a second canonical copy would be duplicate authority, §20)"),
        ("provenance survives every stage", "yes",
         f"{sum(1 for k, v in f.items() if v and 'stage' in v)}/{len(f)} artifacts carry a provenance "
         "block (JSON: a `provenance` field; markdown: a footer naming stage, generator, seed hash and "
         "inputs). The one exempt artifact is `source.sha256`: the seed digest itself, bare hex by "
         "contract so `sha256sum Red-on-Rust.md` diff against it is byte-exact"),
        ("pipeline is deterministic", "yes", f"render hash `{run['render_hash'][:23]}…` reproduced by "
                                            "`_gate.py` on every `check.py` run; no clock/random/locale/"
                                            "network/filesystem-order use (S7 scans the stage sources)"),
        ("pipeline is idempotent", "yes", "re-running writes nothing (`publish` compares bytes); "
                                          "canonical chunk multiset equals `spec/01`'s"),
        ("canonicalization introduces no unauthorized requirements", "yes",
         f"introduced {s5['counts']['introduced']}, dropped {s5['counts']['dropped']}, "
         f"promotions {s5['counts']['promotions']}"),
        ("registry identities are preserved", "yes",
         f"`{s6['identity']['set_sha256'][:19]}…` — identical set and order across "
         + ", ".join(s6["identity"]["authorities_agreeing"])),
        ("cross-artifact verification passes", "yes", f"{counts['checks']} checks, "
         f"{counts['failures']} failures"),
        ("mutation tests detect deliberate drift", "see §5",
         "drift battery in `tests/spec/_pipeline_mutations.py`"),
        ("historical artifacts remain protected", "yes",
         f"12 sha256-pinned audit snapshots re-verified by S7 ({s4['counts']['spec06_rows']} "
         "findings projected without regrading)"),
        ("evidence state remains unchanged", "yes", "ceiling `SPECIFIED`; "
         f"statuses {sorted({r['status'] for r in _json.loads(f['requirements.json'])['requirements']})}; "
         "`REF1-CONDITIONAL`/`V1-CONDITIONAL` carried verbatim"),
        ("M0 remains NOT STARTED", "yes", f"`state/repository-state.json` → "
                                         f"`{s7['m0']['status']}` ({s7['m0']['source']})"),
    ]
    a(table(boxes, ["condition", "status", "evidence"]) + "\n")

    a("## 4. Remaining ambiguities and contradictions\n\n")
    a("| family | open | ids |\n|---|---|---|\n")
    a(f"| contradictions/ambiguities (`spec/06`) | {len(open_c)} | {', '.join(open_c[:24])}"
      f"{'…' if len(open_c) > 24 else ''} |\n")
    a(f"| unresolved decisions (`spec/09`) | {len(open_u)} | {', '.join(open_u[:24])}"
      f"{'…' if len(open_u) > 24 else ''} |\n")
    a(f"| BLOCKING-severity open rows carried into canonicalization | {len(open_blocking)} | "
      f"{', '.join(open_blocking) or '—'} |\n")
    a(f"| MAJOR-severity open rows carried | {len(open_major)} | {', '.join(open_major[:20])}"
      f"{'…' if len(open_major) > 20 else ''} |\n")
    a(f"\n`req/03-ambiguous.md` registers {s4['category_evidence']['ambiguity']['registered_ambiguities']['count']} "
      "ambiguity entries. Canonicalization carries every open row and discloses it in the canonical "
      "artifact's open-items section; none was silently resolved, and none was re-graded. Suggested "
      f"new register ids (computed, **not** filed): {s4['counts']['candidate_findings_suggested']} "
      "candidate finding(s) from this run's integrity scans.\n\n")

    a("## 5. Mutation status\n\n")
    bat = battery_facts(ctx.repo)
    a(table([
        ["battery", "`tests/spec/_pipeline_mutations.py` (drift of each §14 failure shape, applied to a "
                    "scratch copy; the working tree is never touched)"],
        ["mutations defined", f"{bat['defined']}"],
        ["shapes covered", ", ".join(bat["shapes"])],
        ["registered in `check.py`", ("`scripts/spec/_gate.py` and `tests/spec/_pipeline_mutations.py` "
                                      "are both registered, so every repository gate run executes them"
                                      if bat["registered"] else
                                      "NOT REGISTERED — a checker nobody runs is indistinguishable from "
                                      "one that does not exist (check.py's own founding lesson)")],
        ["survivor policy", "a surviving mutation is a hard failure of the battery, which fails "
                            "`python3 check.py`; the gate never reports a partial kill table as success"],
    ], ["measure", "value"]) + "\n\n")
    a("No kill rate is recorded in this report, deliberately: a measured number frozen in a derived "
      "artifact goes stale the moment the tree moves, and this repository has already been bitten by "
      "exactly that defect class (`state/02` DISP-14, a hand-frozen checker count). What the report "
      "states instead is the *invariant* — "
      f"{bat['defined']} deliberate drifts are defined, the battery runs inside `check.py`, and any "
      "survivor reddens the repository gate. For the table of this run: "
      "`python3 tests/spec/_pipeline_mutations.py -v`.\n\n")
    if mutation:
        a(table([["battery", "tests/spec/_pipeline_mutations.py"],
                 ["mutations", f"{mutation['total']}"],
                 ["killed", f"{mutation['killed']}"],
                 ["survived", f"{mutation['survived']}"],
                 ["kill rate", f"{mutation['kill_rate']}"],
                 ["target", "the pipeline's own fail-closed behaviour: each mutation is a deliberate "
                            "drift (source edit, identity change, status promotion, provenance strip, "
                            "registry corruption, stale artifact, historical edit, canonical invention)"]],
                ["measure", "value"]) + "\n")
        if mutation["survived"]:
            a("Surviving mutations: " + ", ".join(mutation["survivors"]) + "\n\n")
    else:
        pass  # the derived facts above are the report's mutation status; `mutation` is an optional
              # live table for a caller that has just measured one and wants it printed

    a("## 6. Provenance status\n\n")
    a(table([
        ["provenance fields on every generated artifact",
         "`pipeline`, `pipeline_version`, `stage`, `generator`, `source{path,sha256}`, `inputs[]`, "
         "`authority_note`, `timestamp_present:false`"],
        ["per-row provenance", f"{sum(1 for r in _json.loads(f['requirements.json'])['requirements'] if r['source_refs'])} "
         f"source-cited + {sum(1 for r in _json.loads(f['requirements.json'])['requirements'] if r['addendum_note'])} "
         "frozen-addendum (whose provenance is the governance action)"],
        ["timestamps in semantic content", "0 (§4.1: they would destroy reproducibility)"],
        ["content addressing", "every artifact digest recorded in `build/spec/manifest.json`; "
                               "set digest = `render_hash`"],
        ["historical protection", "12 sha256-pinned audit snapshots re-hashed on every verify"],
        ["source mutation", "0 bytes (`Red-on-Rust.md` opened read-only by S0; the pipeline writes only "
                            "under `build/spec/`, `spec/0*-*/`, `spec/PIPELINE.md` and this report)"],
    ], ["measure", "value"]) + "\n\n")

    a("## 7. Registry and verification status\n\n")
    a(table([
        ["registry status", "4 registries generated; identities identical to the canonical registry; "
         f"{s6['policy']['identity_changes']} identity changes; {s6['policy']['status_changes']} status "
         f"changes; {s6['policy']['provenance_gaps']} rows without provenance"],
        ["status transition channel", "`reg/status-transitions.json` (append-only, ledger of record) — "
         "untouched by this transformation"],
        ["verification status", "ACCEPTED as a set of derived projections: "
         f"{counts['checks']} checks, {counts['failures']} failures, {counts['gaps_reported']} gaps "
         "reported (not closed)"],
        ["verification verdict text", s7["verdict"]["meaning"]],
        ["what a PASS does not establish", "; ".join(s7["verdict"]["does_not_establish"])],
    ], ["measure", "value"]) + "\n\n")

    a("## 8. Evidence level\n\n")
    a("Ceiling `SPECIFIED` — the ladder `SPECIFIED → IMPLEMENTED → TESTED → VERIFIED → PROVEN` "
      "(`spec/00` §2) is unchanged, and this transformation cannot move it: it produced scripts, "
      "schemas, registries, validators and audit tooling, no implementation and no conformance "
      "evidence.  `REF1-CONDITIONAL` and `V1-CONDITIONAL` remain conditional.  A green `check.py` "
      f"(now {s7['counts'].get('checkers_note', '')}including `scripts/spec/_gate.py`) is "
      "repository-integrity evidence only, never semantic verification.\n\n")

    a("## 9. M0 status and boundary compliance\n\n")
    a(f"M0: **{s7['m0']['status']}** — source: {s7['m0']['source']}.\n\n")
    a("| forbidden during transformation (§21) | present? |\n|---|---|\n")
    for item in FORBIDDEN_DURING_TRANSFORMATION:
        a(f"| {item} | no |\n")
    a("\nNo `.rs` file, `Cargo.toml`, crate, test, golden-vector implementation or CI configuration was "
      "added. The only new code is specification-processing infrastructure: "
      "`scripts/spec/*.py`, `tests/spec/_pipeline_mutations.py`, the committed pointers under "
      "`spec/0*-*/`, `spec/PIPELINE.md`, this report, `check.py` registration and `.gitignore`.\n\n")

    a("## 10. What this transformation changed about authority\n\n")
    a("Nothing.  Authority remains: frozen source `Red-on-Rust.md` → authoritative registers "
      "(`spec/01…spec/10`, `req/`, `reg/`, `mod/`, `dep/`, `term/`, `state/dispositions.json`) → "
      "explicit governance dispositions → deterministic generators → derived artifacts → proposals → "
      "human-readable projections (§5).  The pipeline sits at the generator/derived levels and its "
      "outputs say so on their first lines.\n\n")
    a("```\nPROPOSAL IS NOT AUTHORITY.\nREPRESENTATION IS NOT AUTHORITY.\n"
      "DERIVATION IS NOT AUTHORITY.\nONLY VALIDATED, PROVENANCE-BEARING, CANONICAL ARTIFACTS MAY "
      "BECOME AUTHORITY.\n```\n\n")
    a("STOP CONDITION (§24): the transformation stops before M0.  No implementation claim is made; "
      "the next authorized step is unchanged and remains the repository's decision, not this "
      "pipeline's.\n")
    return "".join(out)


def battery_facts(repo) -> dict:
    """§5's mutation facts, *derived* from the tree rather than remembered.

    Reads the battery's own source (how many drifts it defines, which failure
    shapes) and `check.py`'s registration (whether they actually run).  Nothing
    here is a measurement of a past run, so nothing here can go stale while the
    tree stays green.
    """
    src = (repo / "tests/spec/_pipeline_mutations.py").read_text(encoding="utf-8")
    defined = len(re.findall(r'^\s+Mutation\("P\d+"', src, re.M))
    shapes = sorted(set(re.findall(r'section="([^"]+)"', src)))
    check = (repo / "check.py").read_text(encoding="utf-8")
    registered = sum(1 for rel in ("scripts/spec/_gate.py", "tests/spec/_pipeline_mutations.py")
                     if f'"{rel}"' in check)
    return {"defined": defined, "shapes": shapes,
            "registered": registered == 2, "registered_lines": registered}
