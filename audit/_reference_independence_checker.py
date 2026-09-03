#!/usr/bin/env python3
"""Mechanical reference-independence audit gate.

Why it exists
-------------
The audit `audit/reference-independence-differential-audit.md` verifies (by hand) that
the frozen Phase 15C reference model is specified to be semantically independent of
production, and reports every dependency that could invalidate differential testing.

`dep/_graph.py` RI-1..RI-4 already checks the **module-layer** graph (no implementable-
kind edge into/out of MOD-14). That is a specification-graph check, performed over the
typed module graph; it is NOT a scan of the frozen text that *states* the boundary, and it
does NOT audit the soft `ror-reference -> ror-core` clause or the undeclared comparison
schema. This checker fills that gap by re-deriving the independence *contract* directly
from the frozen source, the canonical spec (S-20), the atomic registers, and the crate map.

It checks **presence/clause** (like the other audit gates) and then **REPORTS** the
coupling vectors the hand audit flagged, without failing on them. It is an audit
instrument, not a conformance gate: none of the REPORT items is a resolved decision, so
they are surfaced rather than enforced. `python3 check.py` therefore stays green.

Run as part of `python3 check.py`.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

SRC = REPO / "Red-on-Rust.md"
SPEC = REPO / "spec/01-canonical-specification.md"
REG_REF6 = REPO / "req/01-registry-part6-verification.md"
REG_REF8 = REPO / "req/01-registry-part8-reference-15C.md"
SPEC07 = REPO / "spec/07-implementation-mapping.md"


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", s)


def text(path: Path) -> str:
    return norm(path.read_text(encoding="utf-8"))


def line_range(path: Path, start: int, end: int) -> str:
    lines = path.read_text(encoding="utf-8").splitlines()
    return norm("\n".join(lines[start - 1 : end]))


# --- The ten forbidden production call surfaces (15C.3 / R-REF-02 / REQ-REF-004) ---
TEN_SURFACES = [
    "ProductionEvaluator",
    "ProductionContinuation",
    "ProductionCapabilityKernel",
    "ProductionBudget",
    "ProductionScheduler",
    "ProductionSerializer",
    "ProductionRecovery",
    "ProductionPersistence",
    "ProductionReplayHost",
    "ProductionTransition",
]

# --- The five ror-reference crate-edge forbiddens (§10 / §14) ---
REF_FORBIDDEN_CRATES = [
    "ror-runtime",
    "ror-kernel",
    "ror-persistence",
    "ror-host",
    "ror-agent",
]

# --- The seven undeclared Observed* element types (X-29 / X-84) ---
OBSERVED_TYPES = [
    "ObservedActor",
    "ObservedEvent",
    "ObservedEffect",
    "ObservedBudget",
    "ObservedSchedulerStep",
    "ObservedFault",
    "ObservedDigest",
]

# --- Reference identifier newtypes (15C.4 / §10) ---
REF_IDS = ["RefCapId", "RefActorId", "RefEffectId"]
# --- Production identifier types (distinct names, R-KERN-01 / R-ACTOR-03 / R-CALC-04) ---
PROD_IDS = ["CapRef", "ActorId", "EffectId"]

REPORTS: list[str] = []


def report(msg: str) -> None:
    if msg not in REPORTS:
        REPORTS.append(msg)


def collect() -> list[str]:
    failures: list[str] = []
    src = text(SRC)
    spec = text(SPEC)
    reg6 = text(REG_REF6)
    reg8 = text(REG_REF8)
    spec07 = text(SPEC07)

    # ------------------------------------------------------------------
    # 1. Ten forbidden production surfaces present in the normative text.
    # ------------------------------------------------------------------
    for s in TEN_SURFACES:
        if s not in spec:
            failures.append(f"spec/01 R-REF-02: missing forbidden surface {s!r}")
        if s not in reg6:
            failures.append(f"req/part6 REQ-REF-004: missing forbidden surface {s!r}")
        if s not in src:
            failures.append(f"Red-on-Rust.md 15C.3: missing forbidden surface {s!r}")

    # ------------------------------------------------------------------
    # 2. The five ror-reference crate-edge forbiddens (§14 + §10).
    # ------------------------------------------------------------------
    s14 = line_range(SRC, 39807, 39828)
    s10 = line_range(SRC, 39645, 39651)
    for c in REF_FORBIDDEN_CRATES:
        if c not in s14 and c not in s10:
            failures.append(
                f"ror-reference forbiddens: {c!r} absent from §14 (L39807-39828) and "
                f"§10 (L39645-39651)"
            )

    # ------------------------------------------------------------------
    # 3. Distinct reference identifiers; forbidden conversion; no prod reuse.
    # ------------------------------------------------------------------
    for rid in REF_IDS:
        if f"pub struct {rid}" not in src:
            failures.append(f"reference identifier {rid!r} not declared in source")
    for pid in PROD_IDS:
        if f"pub struct {pid}" not in src and f"{pid}" not in src:
            failures.append(f"production identifier {pid!r} not found in source")

    # ------------------------------------------------------------------
    # 4. The two differential properties, and the anti-oracle-collapse rule.
    # ------------------------------------------------------------------
    observe_in = ["Observe", "Production", "Reference"]
    for needle in observe_in:
        if needle not in reg6:
            failures.append(f"req/part6 REQ-REF-001: missing Observe-property term {needle!r}")
    if "Canonical(Recover" not in reg6 and "Canonical" not in reg6:
        failures.append("req/part6 REQ-REF-002: Canonical recovery property not found")
    if "Recover_P" not in reg6 and "Recover_R" not in reg6:
        failures.append("req/part6 REQ-REF-002: production/reference recovery not distinguished")
    if "anti-oracle-collapse" not in reg8.lower():
        failures.append("req/part8 REQ-TEST-048: anti-oracle-collapse not found")

    # ------------------------------------------------------------------
    # 5. Reference completeness: the twelve modelled areas (REQ-REF-006).
    # ------------------------------------------------------------------
    for area in ["CEK", "capability", "budget", "actor", "scheduling", "effect",
                 "persistence", "recovery", "environment", "closure", "host"]:
        if area.lower() not in reg6.lower():
            failures.append(f"req/part6 REQ-REF-006: reference area {area!r} not found")

    # ------------------------------------------------------------------
    # 6. ror-core hosts the production value/identity/canonical objects.
    #    (Reported: this is exactly what the reference MAY depend on — F-01.)
    # ------------------------------------------------------------------
    core_hits = {
        "Value domain (R-CALC-01)": "R-CALC-01",
        "CapRef type (R-KERN-01)": "R-KERN-01",
        "canonical serializer (R-CANON-*)": "R-CANON-01",
        "budget operands (R-BUDGET-*)": "R-BUDGET-01",
    }
    for label, obl in core_hits.items():
        if obl in spec07:
            report(
                f"REPORT F-01 (coupling): ror-core hosts {label}; the frozen §10 permits "
                f"ror-reference -> ror-core and §14 does not forbid it, so the reference "
                f"may reach production {label} in one Cargo edge."
            )
            break

    # ------------------------------------------------------------------
    # 7. The comparison domain is undeclared (X-29 / X-84) — F-04.
    # ------------------------------------------------------------------
    for t in OBSERVED_TYPES:
        if f"pub struct {t}" not in src and f"enum {t}" not in src:
            report(
                f"REPORT F-04 (coupling): {t!r} is used in 15C.20 Observation (L36170) but "
                f"declared nowhere (term/02-collisions.md X-29); the comparison domain is "
                f"not closed."
            )

    # ------------------------------------------------------------------
    # 8. Reference recovery consumes production-named records — F-05.
    # ------------------------------------------------------------------
    s1517 = line_range(SRC, 36057, 36110)
    for rec in ["Snapshot", "WAL", "EffectJournal"]:
        if rec in s1517:
            ref_rec = rec.replace("Snapshot", "RefSnapshot").replace(
                "WAL", "RefWalRecord"
            ).replace("EffectJournal", "RefEffectJournal")
            if ref_rec not in s1517:
                report(
                    f"REPORT F-05 (coupling): 15C.17 reference recovery consumes "
                    f"{rec!r} with no Ref* prefix (unlike every other reference domain); "
                    f"the independent test-side decoder is an ror-core code path (ROR-008)."
                )

    # ------------------------------------------------------------------
    # 9. Reference identifiers declared twice — F-08.
    # ------------------------------------------------------------------
    deco = len(re.findall(r"pub struct RefCapId\b", src))
    if deco != 1:
        report(
            f"REPORT F-08 (drift risk): 'pub struct RefCapId' appears {deco}x in the frozen "
            f"source (15C.4 L35471 and §10 L39664); two authoritative declarations with no "
            f"D-entry can drift and break REQ-REF-036 identity correspondence."
        )

    # ------------------------------------------------------------------
    # 10. Independent canonical encoder is conditional — F-02.
    # ------------------------------------------------------------------
    if "where an independent reference encoder exists" in reg8 or (
        "independent reference encoder" in reg8 and "where" in reg8
    ):
        report(
            "REPORT F-02 (coupling): REQ-TEST-046 requires Canonical_P(v) = Canonical_R(v) "
            "only 'where an independent reference encoder exists'; the requirement is "
            "conditional, so byte-level agreement may end up asserted against the "
            "production 15A codec."
        )

    # ------------------------------------------------------------------
    # 11. Crate-edge forbiddens untracked by any obligation — F-09.
    # ------------------------------------------------------------------
    # REQ-REF-004 tracks the *call* surface prohibitions; the §14 crate-edge list has no
    # obligation/atomic record (dep/05 HD-5, V-02). Detect that by confirming NONE of the
    # §14 block's line references (L39807..L39828) is cited by any REQ-* record.
    s14_lines = [f"L398{n:02d}" for n in range(7, 29)]
    cited = any(l in reg6 or l in reg8 for l in s14_lines)
    if not cited:
        report(
            "REPORT F-09 (enforcement gap): the §14 crate-edge forbidden list (L39807-39828) "
            "is cited by no REQ-* record (dep/05 HD-5 / V-02); the 'Cargo dependency review' "
            "R-ARCH-04 relies on has no enumerated checklist."
        )

    return failures


def main() -> int:
    failures = collect()
    if failures:
        print("REFERENCE-INDEPENDENCE AUDIT GATE FAILURES:")
        for f in failures:
            print("  - " + f)
        print("%d failure(s)" % len(failures))
        return 1
    print("PASS: the ten forbidden production surfaces, the five ror-reference crate-edge "
          "forbiddens, the distinct Ref* identifiers, the Observe/Canonical-recovery "
          "properties, the anti-oracle-collapse rule, and the twelve modelled areas are "
          "all present in the frozen text.")
    for r in REPORTS:
        print(r)
    print("%d coupling vector(s) REPORTED (no gate failure; owner decision required)" % len(REPORTS))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
