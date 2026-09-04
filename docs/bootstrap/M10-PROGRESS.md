# M10 Implementation Progress — Crash / Recovery Verification

**Operation type:** M10 IMPLEMENTATION ONLY  
**Authority:** M10 PREFLIGHT @ `docs/bootstrap/M10-PREFLIGHT.md` — GREEN WITH DISCLOSED LIMITATIONS — IMPLEMENTATION AUTHORIZED  
**Preflight commit:** `4d3893f84e7783ae40c2024a22aee17fbc329b9d`  
**M9 review lineage:** `5a9615e → 2e92bf4 → b5563db → dfecc8c → 4d3893f`  

```text
M10 IMPLEMENTATION = COMPLETE WITH DISCLOSED EVIDENCE LIMITATIONS
NEXT = M10 IMPLEMENTATION REVIEW
```

---

## 1. Implementation identity

| Item | Value |
|---|---|
| Operation | M10 crash/recovery verification gate |
| Preflight base HEAD | `4d3893f` |
| Primary home | `crates/ror-differential/src/m10.rs` (MOD-15 / MOD-17 verification layer) |
| Production recovery consumed | `ror_persistence::{recover, CrashHarness, EffectJournal, …}` (M7) |
| Reference recovery consumed | `ror_reference::ref_recover` (independent; core-only) |
| Differential observation | `ror_differential::m7::{compare_m7, observe_*_m7}` |
| Toolchain | `ror-stable` rustc/cargo **1.88.0** |

This progress report is **not** a canonical authority.

---

## 2. Preflight identity

| Check | Result |
|---|---|
| Preflight artifact | `docs/bootstrap/M10-PREFLIGHT.md` present |
| Preflight classification | GREEN WITH DISCLOSED LIMITATIONS |
| IMPLEMENTATION AUTHORIZATION | AUTHORIZED |
| M9 reopened | NO |
| Canonical matrix rows | exactly **T0–T6** (7) |

---

## 3. Canonical authority (implemented projection)

| Requirement | Surface |
|---|---|
| **R-ORDER-02 M10** | T0–T6 crash matrix + recovery differential tests pass |
| **R-TEST-08** | All T0–T6 exercised; exact class; `Issued∧¬Completed⇒Indeterminate`; `Prepared∧¬Issued⇒Discard` |
| **R-RECOV-02** | Normative 7-row matrix (derived `MATRIX` const — not new authority) |
| **R-RECOV-01/03** | `recover(DurableState)` over real WAL bytes |
| **R-RECOV-04** | Production vs independent `ref_recover` |
| **R-RECOV-05** | Corruption / gap / truncate → fault (no silent repair) |
| **R-RECOV-06 / R-DUR-05** | Budget/escrow restored from durable snapshot only |
| **R-RECOV-07/08** | Indeterminate ≠ NotExecuted; recon needs evidence; no host in recover |
| **R-RECOV-09** | Snapshot resume path (T6); counters from durable facts |
| **R-DUR-01 / GI-SEC-07** | M5 hinge intact; `recovery_host_surface() = none` |

---

## 4. Implementation scope

### Delivered

| Surface | Status |
|---|---|
| Derived 7-row matrix projection (`MatrixRow` / `MATRIX` / `ExpectedClass`) | DONE |
| Deterministic crash injection via `CrashHarness` + `EffectJournal` (real WAL) | DONE |
| Per-row production recover + reference recover + compare | DONE |
| Aggregate gate `run_full_matrix` / `m10_gate_status` → **7/7** | DONE |
| Distinguishing tests (Prepared vs Issued vs Completed; Indeterminate ≠ NotExecuted) | DONE |
| Negative hazards (checksum, sequence gap, truncate, host surface, budget invent, cap revoke) | DONE |
| Multi-effect-type payload variants (deterministic stand-in for randomized types) | DONE |
| Recovery determinism (same D → same result, repeated) | DONE |
| M5 hinge / no recover→host | DONE |
| Reference independence preserved (`ror-reference` Cargo deps unchanged) | DONE |

### Explicitly out of scope (preserved)

| Non-goal | Status |
|---|---|
| Second WAL / journal / snapshot / checksum | NOT created |
| M7 semantic redesign | NOT done |
| M9 registry growth | NOT done |
| OAD closure (F-04, U-02, U-17, AMB-27, U-35, …) | NOT closed |
| R-REG promotion | NOT done |
| M11 RC / stress floors | NOT claimed |
| Formal crash-consistency proof | NOT claimed |

---

## 5. Files changed

| Path | Role |
|---|---|
| `crates/ror-differential/src/m10.rs` | **NEW** — M10 matrix, injection, gate, tests |
| `crates/ror-differential/src/lib.rs` | Export `m10` module + public API |
| `docs/bootstrap/M10-PROGRESS.md` | This progress report |

**Unchanged production crates:** `ror-persistence`, `ror-runtime`, `ror-host`, `ror-kernel`, `ror-reference`, `ror-core`, `ror-testkit`.  
**Unchanged:** `mutations/registry.toml`, canonical `final/*`, `reg/requirements.json`, OADs.

---

## 6. T0–T6 matrix

Derived projection of R-RECOV-02 (labels only; authority remains final/01):

| Row | Durable prefix | Expected | Host volatile? | Result |
|---|---|---|---|---|
| **T0** | none | Absent | no | **PASS** |
| **T1** | Prepared only | Discard | no | **PASS** |
| **T2** | Prepared+Issued | Indeterminate | no | **PASS** |
| **T3** | Prepared+Issued | Indeterminate | host invoked (not WAL) | **PASS** |
| **T4** | Prepared+Issued | Indeterminate | host completed volatile (not WAL) | **PASS** |
| **T5** | …+Completed | Completed | no | **PASS** |
| **T6** | SnapshotCommit | Snapshot resume | no | **PASS** |

```text
T0=PASS T1=PASS T2=PASS T3=PASS T4=PASS T5=PASS T6=PASS
M10 T-MATRIX = 7/7 PASS
```

Binding laws verified:

```text
Prepared ∧ ¬Issued          → Discard
Issued ∧ ¬Completed         → Indeterminate
Issued ∧ ¬Completed        ≠ NotExecuted
recover                     ↛ HostExecutor
recover                     ↛ effect re-execution
```

---

## 7. Test commands

Exact commands used for M10 evidence (toolchain `ror-stable` 1.88.0):

```bash
export PATH="$HOME/.ror-toolchain/ror-stable/bin:$PATH"
export RUSTUP_TOOLCHAIN=ror-stable

cargo fmt --all -- --check
cargo check --workspace
cargo clippy --workspace --all-targets --all-features -- -D warnings
cargo test -p ror-differential m10 -- --test-threads=1
cargo test --workspace --lib -- --test-threads=1
cargo test -p ror-runtime --lib effects::tests -- --test-threads=1
python3 scripts/m9_mutation_run.py -o /tmp/m10-m9-regression.json
```

M10-specific filter: `cargo test -p ror-differential m10`.

---

## 8. Test results

| Suite | Result |
|---|---|
| `m10::tests::*` | **26 passed**, 0 failed |
| `full_matrix_7_of_7` | **PASS** (`M10 T-MATRIX = 7/7 PASS`) |
| `ror-differential` lib total | **116 passed** (incl. M2–M8 + M10) |
| `ror-persistence` lib | **36 passed** (M7 machinery intact) |
| `ror-runtime` effects (M5 hinge) | **16 passed** |
| Workspace `--lib` | **all crates green** (327 unit tests across workspace libs) |

Per-row explicit tests (cannot hide a missing T-row behind a global PASS):

- `t0_before_prepared_absent`
- `t1_prepared_not_issued_discard` + `t1_journal_crash_before_issued_sync`
- `t2_after_issued_indeterminate`
- `t3_host_invoked_still_indeterminate`
- `t4_host_completed_volatile_still_indeterminate`
- `t5_completed_reconstruct_no_rehost`
- `t6_snapshot_commit_resume`

---

## 9. Differential results

| Check | Result |
|---|---|
| `compare_m7` on every T0–T6 injection | **PASS** (`differential_all_rows`) |
| Multi-payload effect-type variants × rows | **PASS** |
| Production observation == reference observation | **PASS** |
| Reference does not import production recovery | **PASS** (Cargo + runtime labels) |
| F-04 Observed* schema | **OPEN** (provisional `RecoveryObservation` reused; not closed) |

```text
recovery differential = PASS
reference independence = PASS
```

---

## 10. Security results

| Check | Result |
|---|---|
| `HostInvoked(E) ⇒ DurableIssued(E)` (M5 effects suite) | **INTACT** |
| `recovery_host_surface() == "none — recover(DurableState) only"` | **PASS** |
| recover takes only `DurableState` on all T-rows | **PASS** |
| Issued∧¬Completed stays Indeterminate (T2–T4) | **PASS** |
| Local NotExecuted without evidence rejected | **PASS** |
| Prepared-only not promoted to Issued/Completed | **PASS** |
| Cap revocation monotonic across crash | **PASS** |
| Budget not invented on empty recover | **PASS** |

```text
M5 hinge = INTACT
no recovery→host shortcut = PASS
no unauthorized effect re-execution = PASS
```

---

## 11. Dependency results

| Edge | Required | Observed |
|---|---|---|
| `ror-reference ↛ ror-persistence` | forbidden | absent |
| `ror-reference ↛ ror-runtime` | forbidden | absent |
| `ror-reference ↛ ror-host` | forbidden | absent |
| `ror-reference ↛ ror-kernel` | forbidden | absent |
| `ror-differential → ror-persistence` | verification OK | present (pre-existing) |
| `ror-differential → ror-reference` | verification OK | present |
| New production semantic edges | none required | none added |

```text
dependency gate = PASS
```

---

## 12. Regression results

| Milestone / gate | Result |
|---|---|
| M1–M8 workspace lib suites | GREEN |
| M5 effects hinge | 16/16 PASS |
| M7 persistence crash_matrix_tests | still green (36 persistence tests) |
| M8 differential system | still green |
| **M9 mutation campaign** | **42/42 KILLED, 100%, gate_ok=true, critical_survived=false** |
| M9 registry.toml | **unchanged** |
| `cargo fmt --check` | exit 0 |
| `cargo check --workspace` | exit 0 |
| `cargo clippy … -D warnings` | exit 0 |
| `cargo test --workspace --lib` | exit 0 |
| `unsafe` in m10 | none |
| External network/host effects in M10 | none (in-memory WAL only) |

M9 regression command provenance:

```text
python3 scripts/m9_mutation_run.py -o /tmp/m10-m9-regression.json
→ registered=42 killed=42 kill_rate_percent=100 gate_ok=true harness_pass=true
```

(Campaign output written only under `/tmp`; live `mutations/m9-*.json|md` left as M9 closed artifacts.)

---

## 13. Evidence classification

| Claim | Classification |
|---|---|
| T0–T6 matrix implemented and tested | **IMPLEMENTED / TESTED** |
| Recovery differential agreement | **TESTED** (evidence, not proof) |
| M5 hinge intact under M10 | **TESTED** |
| M9 42/42 under M10 tree | **TESTED** (campaign re-run) |
| Crash consistency formally proven | **NOT CLAIMED** |
| R-REG VERIFIED/PROVEN | **NOT CLAIMED** (184 × SPECIFIED) |
| OAD closed | **NOT CLAIMED** |
| Production ready | **NOT CLAIMED** |

---

## 14. Known limitations

| ID | Limitation |
|---|---|
| L-M10-F04 | Recovery observations use provisional M7/M8 schema; F-04 OPEN |
| L-M10-U02-17 | Snapshot/queue encodings remain provisional (U-02/U-17) |
| L-M10-AMB27 | 12-step vs finer recovery enumeration still open |
| L-M10-U35 | Determinism theorem OPEN; operational determinism only |
| L-M10-RAND | Effect-type coverage is deterministic payload variants, not a PRNG campaign |
| L-M10-NO-PROOF | Differential agreement ≠ formal crash-consistency proof |
| L-M10-M7-UNIT | Pre-existing M7 unit harness remains; M10 adds gate-level aggregate 7/7 |

---

## 15. Explicit non-claims

```text
Crash/recovery is NOT formally proven.
R-REG is NOT VERIFIED or PROVEN (remains 184 × SPECIFIED).
OADs are NOT closed (F-04, U-02, U-17, AMB-27, U-35, …).
M11 is NOT complete.
M10 implementation review is NOT this operation.
Host exactly-once is NOT inferred from crash tests alone.
Provisional codecs do NOT freeze U-02/U-17/U-32.
M9 42/42 is mutation evidence, not a substitute for the crash matrix.
No production readiness claim.
```

---

## 16. Next step

```text
M10 IMPLEMENTATION = COMPLETE WITH DISCLOSED EVIDENCE LIMITATIONS
NEXT = M10 IMPLEMENTATION REVIEW
```

Do **not** begin M10 review in this operation.

### Final state board

```text
M0–M8                      prior accepted (disclosed where noted)
M9                         ACCEPTED WITH DISCLOSED EVIDENCE LIMITATIONS
M10 preflight              GREEN WITH DISCLOSED LIMITATIONS
M10 implementation         COMPLETE WITH DISCLOSED EVIDENCE LIMITATIONS
M10 T-MATRIX               7/7 PASS
Recovery differential      PASS
M5 hinge                   INTACT
M7 boundary                PRESERVED
M8 reference independence  PASS
M9 regression              42/42 KILLED (100%)
R-REG                      184 × SPECIFIED
OADs                       OPEN
NEXT                       M10 IMPLEMENTATION REVIEW
```

---

*End of M10 PROGRESS. M10 review is a separate authorization.*
