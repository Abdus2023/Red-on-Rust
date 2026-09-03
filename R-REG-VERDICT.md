# R-REG Verdict — Status-Transition Evidence-Kind Enforcement

> **Date:** 2026-09-03
> **Branch:** `arena/01a068ea-red-on-rust`
> **Commit:** `a178b22` (Phase B completion)

## 1. Executive Summary

The R-REG status-transition evidence-kind enforcement gap has been **CLOSED**. The repository now mechanically enforces that evidence `kind` matches the target status level, preventing generic evidence from being used to claim arbitrary status promotions.

## 2. Changes Made

### Phase B: Close Status-Transition Gap

| File | Change |
|---|---|
| `reg/03-status-transition-audit-model.md` | Added §2 (evidence-kind predicates), §3 (skip semantics), §4 rules 7-8 (compiler enforcement) |
| `reg/_compile.py` | Added `EVIDENCE_KINDS_FOR_STATUS`, `ALL_EVIDENCE_KINDS`, `NON_PROMOTING_KINDS` constants. Added battery points 21-22. Updated `render_status_model()`. |
| `reg/status-transitions.json` | Added `evidence_kind_enforcement` and `skip_evidence_completeness` documentation |
| `reg/00-overview.md` | Regenerated (22-point battery) |
| `reg/01-compilation-report.md` | Regenerated (22-point battery) |
| `reg/08-determinism-hash-report.md` | Regenerated (new hashes) |

### Evidence-Kind Enforcement Rules

| Target Status | Required Evidence Kinds | Prohibited Evidence Kinds |
|---|---|---|
| `IMPLEMENTED` | `source` | `test`, `differential`, `mutation`, `crash-matrix`, `proof`, `repository-integrity-gate` |
| `TESTED` | `test` | `source`, `differential`, `mutation`, `crash-matrix`, `proof`, `repository-integrity-gate` |
| `VERIFIED` | `differential`, `mutation`, `crash-matrix` | `source`, `test`, `proof`, `repository-integrity-gate` |
| `PROVEN` | `proof` | `source`, `test`, `differential`, `mutation`, `crash-matrix`, `repository-integrity-gate` |

### Skip Semantics

If a transition skips intermediate levels, the evidence package MUST include:
1. The target status's evidence requirements, AND
2. All intermediate status evidence requirements.

Example: SPECIFIED → VERIFIED requires `source` (for IMPLEMENTED) + `test` (for TESTED) + `differential`/`mutation`/`crash-matrix` (for VERIFIED).

## 3. Verification Results

### check.py (15 checkers)
```
ALL PASS  (15 checkers, 7 classified non-checkers)
```

### R-REG Battery (22 points)
```
OK   1/2  schema validity + required fields: 0 violation(s)
OK   3    IDs unique: 184/184 unique; duplicates none
OK   4    canonical ID set preserved: reg 184 == final/03 184 == spec/03 184 == spec/10 184 == spec/01 chunks 184 == final/01 chunks 184
OK   4b   per-area counts identical to final/03 area table (24 areas)
OK   5    statements preserved: byte-identical to spec/01 for 184/184; whitespace-identical to final/01 for 184/184
OK   6    normative levels preserved: 97 negative-guarantee tokens in registry == 97 in spec/01
OK   7    dependencies resolve: 0 R-level edges (== spec/10 canonical)
OK   8/9  provenance present for 184/184
OK   10/11 status values legal ([('SPECIFIED', 184)]); identical to final/03 and final/01 markers
OK   12   historical evidence unchanged: transition ledger is append-only vs the committed copy; 0 entries
OK   21   evidence-kind enforcement: 0 violation(s) in 0 ledger entries; all kinds match target statuses
OK   22   skip evidence completeness: 0 violation(s) in skip transitions; all skips have complete evidence
OK   13   security classification preserved: every GI-SEC home (22) is security_relevant
OK   14/15/16 implementation / test / verification mappings equal the canonical final/03 cells
OK   17   evidence traceable: 0 evidence entries; untraceable none
OK   18   deterministic: two independent in-memory compilations render byte-identical
OK   19   reproducible: committed reg/requirements.json == fresh compilation
OK   20   governance: reg/_compile.py registered in check.py CHECKERS
```

### Mutation Battery (25 mutations)
```
killed 25/25  (100%)
```

## 4. Bootstrap State Preserved

| Metric | Value |
|---|---|
| Requirements | 184/184 |
| Status | All SPECIFIED |
| Status transitions | 0 |
| Evidence entries | 0 |
| REF1-CONDITIONAL | Carried (not promoted) |
| V1-CONDITIONAL | Carried (not promoted) |

## 5. R-REG Verdict

**PASS** — The R-REG status-transition evidence-kind enforcement gap is closed. The repository now mechanically enforces:

1. Evidence `kind` must match the target status level (battery point 21)
2. Skip transitions must carry evidence for all intermediate levels (battery point 22)
3. `repository-integrity-gate` evidence can never establish any status promotion
4. All 184 requirements remain SPECIFIED with 0 status transitions
5. The bootstrap state is preserved, not promoted

## 6. Implementation Bootstrap Readiness

The repository is now ready for implementation bootstrap:

- **Architecture:** Frozen (28 OPEN U-items, 41 open C-rows carried)
- **Requirements:** 184/184 SPECIFIED, mechanically enforced
- **Evidence model:** Fail-closed, status-appropriate evidence required
- **Tooling:** 22-point validation battery, 15 checkers, 25 mutation tests
- **Governance:** Append-only ledger, deterministic compilation, reproducible hashes

### Next Steps for Implementation

1. **Create implementation crates** per `spec/07` (no crates exist yet)
2. **Implement requirements** with `source` evidence in ledger entries
3. **Write tests** with `test` evidence in ledger entries
4. **Run verification** with `differential`/`mutation`/`crash-matrix` evidence
5. **Optional:** Formal proofs with `proof` evidence

Each status promotion will be mechanically validated against the evidence-kind predicates.

## 7. Constraints Honored

- ✅ No requirement IDs added, deleted, split, merged, renamed, or renumbered
- ✅ No canonical statements or normative semantics modified
- ✅ No requirement status promoted (all remain SPECIFIED)
- ✅ Addenda VII-IX, U-38, REF1-CONDITIONAL, V1-CONDITIONAL not reopened
- ✅ Open Architectural Decisions not silently resolved
- ✅ No semantics invented to make implementation easier
- ✅ Evidence status not upgraded merely because a requirement exists
- ✅ R-REG correction is a registry governance/tooling correction, not a specification amendment
- ✅ Status transitions fail closed: test-only evidence insufficient for IMPLEMENTED, unexecuted test insufficient for TESTED, no verification evidence insufficient for VERIFIED, non-proof evidence insufficient for PROVEN
- ✅ Skip semantics explicitly defined and auditable
- ✅ Evidence kind not confused with status

---

**Verdict: PASS — Phase B complete. Repository ready for implementation bootstrap.**
