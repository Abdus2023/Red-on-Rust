#!/usr/bin/env python3
"""M11 Release Candidate gate runner (R-ORDER-02 / R-TEST-10 / R-TEST-11).

Orchestrates repository-supported commands only:
  - workspace fmt/check/test/clippy
  - in-process RC domains (cargo test -p ror-differential m11)
  - M10 crash matrix (cargo test -p ror-differential m10)
  - M9 mutation campaign (scripts/m9_mutation_run.py) — registry untouched
  - M5 hinge (cargo test -p ror-runtime --lib effects::tests)
  - R-ORDER-02 defect predicate (scripts/m11_rc_defect_predicate.py) — RF-02

Does NOT promote R-REG, close OADs, or claim VERIFIED/PROVEN.

Fail-closed on:
  - any stage exit ≠ 0
  - mutation parse failure
  - missing/malformed defect register (via defect predicate)
  - open applicable high defects (R-ORDER-02 «zero open high defects pass»)

Exit 0 iff all required stages pass INCLUDING the defect predicate.
Historical rejected review 96b6d0b remains immutable evidence of the prior
oracle that could PASS while open BLOCKING/MAJOR rows remained.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
ENV = os.environ.copy()
_tc = Path.home() / ".ror-toolchain" / "ror-stable" / "bin"
if _tc.is_dir():
    ENV["PATH"] = f"{_tc}:{ENV.get('PATH', '')}"
ENV["RUSTUP_TOOLCHAIN"] = ENV.get("RUSTUP_TOOLCHAIN", "ror-stable")
ENV["CARGO_TERM_COLOR"] = "never"

# Import sibling predicate module (same directory).
sys.path.insert(0, str(REPO / "scripts"))
from m11_rc_defect_predicate import evaluate_defect_predicate  # noqa: E402


def run(cmd: list[str], timeout: int = 1800) -> tuple[int, str]:
    p = subprocess.run(
        cmd,
        cwd=REPO,
        env=ENV,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        timeout=timeout,
    )
    return p.returncode, p.stdout


def main() -> int:
    stages: list[dict] = []
    overall = True

    def stage(name: str, cmd: list[str], timeout: int = 1800) -> None:
        nonlocal overall
        print(f"[M11-RC] {name}: {' '.join(cmd)}", flush=True)
        code, out = run(cmd, timeout=timeout)
        tail = "\n".join(out.strip().splitlines()[-20:])
        ok = code == 0
        if not ok:
            overall = False
        stages.append(
            {
                "name": name,
                "cmd": cmd,
                "exit": code,
                "pass": ok,
                "tail": tail,
            }
        )
        print(f"  → exit={code} pass={ok}", flush=True)
        if not ok:
            print(tail, flush=True)

    # Workspace gates (R-REPO / process)
    stage("fmt", ["cargo", "fmt", "--all", "--", "--check"], timeout=120)
    stage("check", ["cargo", "check", "--workspace"], timeout=300)
    stage(
        "clippy",
        [
            "cargo",
            "clippy",
            "--workspace",
            "--all-targets",
            "--all-features",
            "--",
            "-D",
            "warnings",
        ],
        timeout=600,
    )
    stage(
        "test_workspace_lib",
        ["cargo", "test", "--workspace", "--lib", "--", "--test-threads=1"],
        timeout=600,
    )

    # In-process RC domains (R-TEST-01/08/10 domains except mutation)
    stage(
        "m11_in_process",
        ["cargo", "test", "-p", "ror-differential", "m11", "--", "--test-threads=1"],
        timeout=600,
    )
    stage(
        "m10_matrix",
        ["cargo", "test", "-p", "ror-differential", "m10", "--", "--test-threads=1"],
        timeout=300,
    )
    stage(
        "m5_hinge",
        [
            "cargo",
            "test",
            "-p",
            "ror-runtime",
            "--lib",
            "effects::tests",
            "--",
            "--test-threads=1",
        ],
        timeout=300,
    )

    # Mutation conjunct (R-TEST-11 c2 / R-TEST-05) — full campaign
    mut_out = Path("/tmp/m11-m9-regression.json")
    stage(
        "m9_mutation",
        [sys.executable, str(REPO / "scripts" / "m9_mutation_run.py"), "-o", str(mut_out)],
        timeout=1800,
    )

    mut = {}
    if mut_out.is_file():
        mut = json.loads(mut_out.read_text())
    mut_ok = bool(
        mut.get("gate_ok")
        and mut.get("killed") == 42
        and mut.get("registered") == 42
        and mut.get("kill_rate_percent") == 100
        and not mut.get("critical_survived")
    )
    if not mut_ok:
        overall = False
    stages.append(
        {
            "name": "m9_mutation_parse",
            "cmd": ["parse", str(mut_out)],
            "exit": 0 if mut_ok else 1,
            "pass": mut_ok,
            "tail": json.dumps(
                {
                    "killed": mut.get("killed"),
                    "registered": mut.get("registered"),
                    "rate": mut.get("kill_rate_percent"),
                    "gate_ok": mut.get("gate_ok"),
                }
            ),
        }
    )

    # Reference independence spot-check
    ref_toml = (REPO / "crates" / "ror-reference" / "Cargo.toml").read_text()
    forbidden = ["ror-runtime", "ror-persistence", "ror-host", "ror-kernel", "ror-agent"]
    dep_sec = ref_toml.split("[dependencies]", 1)[-1].split("[", 1)[0]
    ref_ok = all(f not in dep_sec for f in forbidden) and "ror-core" in dep_sec
    if not ref_ok:
        overall = False
    stages.append(
        {
            "name": "reference_independence",
            "cmd": ["inspect", "ror-reference/Cargo.toml"],
            "exit": 0 if ref_ok else 1,
            "pass": ref_ok,
            "tail": "ror-core only" if ref_ok else "forbidden dep present",
        }
    )

    # R-REG count
    reg = json.loads((REPO / "reg" / "requirements.json").read_text())
    rreg_ok = reg.get("requirement_count") == 184 and len(reg.get("requirements", [])) == 184
    if not rreg_ok:
        overall = False
    stages.append(
        {
            "name": "r_reg",
            "cmd": ["inspect", "reg/requirements.json"],
            "exit": 0 if rreg_ok else 1,
            "pass": rreg_ok,
            "tail": f"count={reg.get('requirement_count')}",
        }
    )

    # RF-02: R-ORDER-02 defect predicate — fail closed; never trust prior PASS flag
    print("[M11-RC] defect_predicate: evaluate_defect_predicate(reading=all)", flush=True)
    defect = evaluate_defect_predicate(reading="all")
    defect_ok = bool(defect.ok) and not defect.fail_closed
    # fail_closed True ⇒ ok already False; still force overall false
    if defect.fail_closed or not defect.ok:
        overall = False
        defect_ok = False
    stages.append(
        {
            "name": "defect_predicate_r_order_02",
            "cmd": [
                "m11_rc_defect_predicate.evaluate_defect_predicate",
                f"reading={defect.governing_reading}",
                defect.register_path,
            ],
            "exit": 0 if defect_ok else 1,
            "pass": defect_ok,
            "tail": defect.detail,
            "open_blocking": defect.open_blocking,
            "open_major": defect.open_major,
            "rows_parsed": defect.rows_parsed,
            "fail_closed": defect.fail_closed,
        }
    )
    print(
        f"  → defect_ok={defect_ok} fail_closed={defect.fail_closed} detail={defect.detail}",
        flush=True,
    )

    report = {
        "schema": "m11-rc-gate-v2",
        "authority": "R-ORDER-02 / R-TEST-10 / R-TEST-11",
        "oracle_version": "v2-rf02-defect-predicate",
        "supersedes_oracle": "v1 (pre-corrective; review 96b6d0b)",
        "overall_pass": overall,
        "stages": stages,
        "r_test_11": {
            "c1_observe_p_eq_observe_r": "see m11_in_process EXH/PROP/DIFF",
            "c2_mutation_kill_rate_100": mut_ok,
            "c3_recover_p_eq_recover_r": "see m11_in_process CRASH/DIFF + m10_matrix",
        },
        "r_order_02_defect": {
            "ok": defect.ok,
            "fail_closed": defect.fail_closed,
            "governing_reading": defect.governing_reading,
            "open_blocking": defect.open_blocking,
            "open_major": defect.open_major,
            "detail": defect.detail,
            "register_path": defect.register_path,
            "rows_parsed": defect.rows_parsed,
        },
        "mutation": {
            "killed": mut.get("killed"),
            "registered": mut.get("registered"),
            "kill_rate_percent": mut.get("kill_rate_percent"),
            "gate_ok": mut.get("gate_ok"),
        },
        "disclosures": [
            "F-04 OPEN",
            "U-35 OPEN",
            "M10 L-01/L-02 carried",
            "open MAJOR/BLOCKING register rows evaluated by defect predicate",
            "evidence is TESTED not VERIFIED/PROVEN",
            "stress deep-call uses 50k (low end of 50k-100k floor)",
            "historical review 96b6d0b immutable; v1 oracle results stale for v2 claims",
        ],
        "note": (
            "RC gate PASS requires defect predicate ok under R-ORDER-02. "
            "Not formal proof. Not production ready."
        ),
    }
    out_path = Path("/tmp/m11-rc-report.json")
    out_path.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"overall_pass": overall, "report": str(out_path)}, indent=2))
    return 0 if overall else 1


if __name__ == "__main__":
    sys.exit(main())
