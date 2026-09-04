# M7 Implementation Review — Persistence / WAL / Snapshot / Crash Recovery

**Operation ID:** `RATF-M7-REVIEW-001`  
**Operation type:** M7 IMPLEMENTATION REVIEW ONLY — no M8; no semantic repair; no OAD/R-REG promotion.  
**Repository:** `Abdus2023/Red-on-Rust`  
**Branch:** `arena/01a06993-red-on-rust`  
**Implementation under review:** `5a0463071111edf0b106bd8635c428dfa192fd7c`  
**Authorized preflight:** `61a9e579bdf6aca92feb9f3993aa9b83204176af`  
**Previous implementation review:** M6 `ea113657d4067117aeec4d5f910825ce08002110`  

```text
M7 IMPLEMENTATION REVIEW = ACCEPTED WITH DISCLOSED EVIDENCE LIMITATIONS
```

```text
NEXT = M8 PREFLIGHT
```

Evidence labels: **PASS** | **PASS-DISCLOSED** | **FAIL-*** | **BLOCK-***  
Evidence classes: IMPLEMENTATION | TEST | DIFFERENTIAL | MUTATION | CRASH-MATRIX | OTHER  

---

## 1. Identity and lineage

| Item | Value | Status |
|---|---|---|
| `git rev-parse HEAD` | `5a0463071111edf0b106bd8635c428dfa192fd7c` | FACT |
| Implementation commit | `5a04630` | FACT |
| Preflight ancestor | `61a9e57` (`merge-base --is-ancestor` YES) | FACT |
| M6 review ancestor | `ea11365` | FACT |
| Working tree at review start | clean at `5a04630` | FACT |
| Scope of `61a9e57..5a04630` | 10 files, +3379/−7 — persistence/reference/differential/M7-PROGRESS only | FACT |
| `final/` `reg/` `dep/` `mod/` `spec/` diff | **empty** | FACT |

**Lineage:**

```text
… → ea11365  M6 review
        ↓
    61a9e57  M7 PREFLIGHT
        ↓
    5a04630  M7 IMPLEMENTATION   = HEAD under review
```

**R0 = PASS.**

Mechanical review-only fix applied after start: `cargo fmt` whitespace on `m7.rs` `compare_m7` signature (no semantic change). Recorded in the review commit if present.

---

## 2. Canonical authorities inspected

| Authority | Role |
|---|---|
| `final/01-canonical-specification.md` | R-DUR / R-PERSIST / R-RECOV homes |
| `final/03-requirement-registry.md` | R-* inventory |
| `final/04-verification-registry.md` | M7 evidence tags |
| `final/05-global-invariant-registry.md` | GI-SEC-07, GI-DUR-*, GI-REC-* |
| `final/08-evidence-status-matrix.md` | **184 × SPECIFIED** |
| `final/09-open-architectural-decisions.md` | U-02, U-17, U-32 OPEN |
| `dep/10-graph.json` | crate edges + forbidden edges |
| `mod/11-persistence.md`, `mod/12-recovery.md`, `mod/18-ownership-matrix.md` | MOD-11/12 ownership |
| `docs/bootstrap/M7-PREFLIGHT.md` | authorization input (consumer) |
| `docs/bootstrap/M7-PROGRESS.md` | implementation claims (consumer) |

Bootstrap documents treated as **consumers**, not authorities.

---

## 3. Gate board (summary)

| Gate | Title | Status |
|---|---|---|
| R0 | Identity / lineage / authority | **PASS** |
| R1 | Baseline / regression / fmt-check-test-clippy | **PASS** |
| R2 | Persistence ownership | **PASS** |
| R3 | WAL semantics | **PASS-DISCLOSED** (U-32) |
| R4 | Journal semantics | **PASS** |
| R5 | Crash matrix T0–T6 (authority) | **PASS** |
| R6 | Recovery API security | **PASS** |
| R7 | M5 hinge preservation | **PASS** |
| R8 | Snapshot atomicity | **PASS-DISCLOSED** (U-02) |
| R9 | WAL + snapshot recovery | **PASS-DISCLOSED** |
| R10 | Actor / mailbox recovery | **PASS-DISCLOSED** (U-17/U-27/U-30) |
| R11 | Pending / Indeterminate | **PASS** |
| R12 | Reference independence | **PASS** |
| R13 | Differential recovery | **PASS** |
| R14 | Crash matrix execution | **PASS** |
| R15 | Security mutation tests | **PASS-DISCLOSED** (partial NOT-RUN) |
| R16 | Determinism | **PASS** |
| R17 | Corruption / failure discipline | **PASS** |
| R18 | OAD discipline | **PASS** |
| R19 | R-REG discipline | **PASS** |
| R20 | Dependency authority | **PASS** |
| R21 | Unsafe / external-effect surface | **PASS** |
| R22 | M1–M6 regression | **PASS** |
| R23 | Documentation / evidence honesty | **PASS-DISCLOSED** |

**BLOCKS = 0. FAILS = 0.**  
At least one **PASS-DISCLOSED** ⇒ final class below.

---

## 4. Workspace gates executed (R1 / R22)

| Command | Result |
|---|---|
| `cargo fmt --all -- --check` | exit **0** (after mechanical fmt) |
| `cargo check --workspace` | exit **0** |
| `cargo test --workspace --lib` | exit **0** (all crates) |
| `cargo clippy --workspace --all-targets -- -D warnings` | exit **0** |

**Lib test totals (representative):**  
core 30 · differential 75 · host 3 · kernel 8 · persistence **34** · reference 14 · runtime **96** · others 0.

**M5 hinge suite (`ror-runtime` effects):** 9/9 ok including `persist_fail_no_host`, `happy_path_issued_before_host`.  
**M5 differential:** 12/12 ok including `mutation_intent_host_before_issued_killed` (should panic).  
**M6 differential:** 13/13 ok including `m5_host_before_issued_still_critical`.  
**M7 differential:** 5/5 ok (`diff_t1/t2/t5/t6/empty`).

No `unsafe` in M7 additions. No new crates.io dependencies (`ror-persistence` → `ror-core` only; `ror-reference` → `ror-core` only).

**R1 = PASS. R22 = PASS.**

---

## 5. Critical invariants — explicit report

### 5.1 Recovery classification

| Invariant | Observed | Evidence |
|---|---|---|
| `Prepared ∧ ¬Issued ⇒ Discard` | `EffectClass::Discard` | `t1_*`, `recovery::tests::t1_*` |
| `Issued ∧ ¬Completed ⇒ Indeterminate` | `EffectClass::Indeterminate` | `t2/t3/t4_*` |
| `Indeterminate ≠ NotExecuted` | `is_not_executed_local() == false`; `admit_recon_evidence` rejects tag 0 | `mutation_indeterminate_not_silently_not_executed` |
| `Completed ⇒ reconstruct without host re-execution` | Completed class + result bytes; `recover(&DurableState)` only | `t5_*`, `recovery_host_surface` |
| `Recovery ↛ original-effect re-execution` | No host/execute in recovery path | API + grep |

### 5.2 M5 security hinge

| Invariant | Observed |
|---|---|
| `HostInvoked(E) ⇒ DurableIssued(E)` | `run_effect_pipeline`: Prepared+sync → Issued+sync → **then** `host.execute`; post-path `is_durably_issued` assert |
| Persist fail before Issued | `persist_fail_no_host` — host not invoked |
| Host-before-Issued negative | `PanicHost` / differential should-panic still green |
| M7 recovery route | **no** host parameter; cannot bypass hinge |

**R7 = PASS** (CRITICAL).

### 5.3 Reference independence

| Edge | Required | Observed |
|---|---|---|
| `ror-reference ↛ ror-runtime` | forbidden | Cargo.toml + import scan clean |
| `ror-reference ↛ ror-kernel` | forbidden | clean |
| `ror-reference ↛ ror-persistence` | forbidden | clean |
| `ror-reference ↛ ror-host` | forbidden | clean |
| `ror-reference ↛ ror-agent` | forbidden | clean |

`ref_recover` reimplements parse/classify over shared **provisional byte layout** and `ror-core` digests only — not production transition functions.

**R12 = PASS.**

### 5.4 Authority discipline

Canonical registries unchanged by `5a04630`. Bootstrap is consumer. Provisional codecs marked U-02/U-17/U-32; OADs remain OPEN in `final/09`.

---

## 6. WAL result (R3)

**Location:** `crates/ror-persistence/src/wal.rs`

| Obligation | Behavior | Evidence |
|---|---|---|
| Framing | magic `RORW` + version + seq + kind + payload_len + payload + checksum | `frame_round_trip` |
| Sequence monotonic from 1 | `WalLog::new` / `Default` set `next_seq = WalSequence(1)` | code + round-trip recovery tests (fixes prior Default=0 bug) |
| Checksum chain | `SHA-256(prev ‖ seq ‖ kind ‖ payload)` | `chain_and_gap_detection` |
| Gap / regression reject | `SequenceGap` / `SequenceRegression` | `sequence_regression_rejected`, `mutation_sequence_gap_kills` |
| Corruption reject | checksum fail | `mutation_checksum_corrupt_kills` |
| Truncation reject | `Truncated` | `partial_truncated_wal_rejected` |
| No host on replay | pure frames | structure |

**U-32 OPEN:** 5-field layout + checksum domain are **provisional** — disclosed, not frozen.

**R3 = PASS-DISCLOSED.**

---

## 7. Journal result (R4)

**Location:** `crates/ror-persistence/src/journal.rs`

Kinds: Event, EffectPrepared/Issued/Completed/Reconciled, CapGranted/Derived/Revoked.  
Causal gates: Issued requires Prepared; Completed requires Issued.  
`EffectJournal: IssuanceJournal` preserves M5 hinge API.  
`MemoryJournal` unchanged as M5 thin double.

**R4 = PASS.**

---

## 8. Snapshot result (R8)

**Location:** `crates/ror-persistence/src/snapshot.rs`

Protocol: Begin → `SnapshotBody` → `SnapshotCommit` + state_digest + sync.  
Incomplete body without commit ⇒ **not** ValidSnapshot (`incomplete_begin_is_garbage`).  
Digest mismatch ⇒ `SnapshotError::DigestMismatch` / recovery integrity fault.

**U-02 OPEN:** `SnapshotImage` codec provisional.  
**U-17 OPEN:** runnable queue reconstructed from status==Runnable (sorted), not a mandatory persisted field.

**R8 = PASS-DISCLOSED.**

---

## 9. Recovery result (R6 / R9)

**Location:** `crates/ror-persistence/src/recovery.rs`  
**API:** `pub fn recover(d: &DurableState) -> Result<RecoveryResult, RecoveryFault>`

| Check | Result |
|---|---|
| Host surface | **none** (`recovery_host_surface()` documents) |
| External I/O / net / process | **none** in recovery |
| Silent repair | rejected (integrity/sequence faults) |
| Combined snapshot + WAL | T6 harness + differential |
| ID reconstruction | `next_effect_id` / `next_actor_id` from max(snapshot, journal) |
| Budget/time freeze on recover | `budget_and_time_not_advanced_on_recover` |

**R6 = PASS. R9 = PASS-DISCLOSED** (provisional codecs; thin machine image).

---

## 10. Pending / Indeterminate result (R11)

| Rule | Result |
|---|---|
| Issued∧¬Completed → Indeterminate | PASS |
| No auto Retry / Completed / local NotExecuted | PASS |
| Recon only with evidence_tag ∈ {1,2,3} | PASS (`admit_recon_evidence`) |
| Actor Pending binding in snapshot | status=2 + `pending_effect` preserved in T6 test |

**R11 = PASS.**

---

## 11. Actor / mailbox recovery (R10)

Thin `ActorSnap { id, status, pending_effect, mailbox bytes }` restored from snapshot.  
Runnable reconstructed deterministically. Terminal (status=3) excluded from runnable (T6 test).  
**Not invented:** dead-actor message policy, Pending cancel, ID reuse.

Encoding of mailbox Value and Pending continuation locus remain **U-30 / U-27 OPEN**.

**R10 = PASS-DISCLOSED.**

---

## 12. Crash matrix execution (R5 / R14)

| Point | Expected | Test | Result |
|---|---|---|---|
| **T0** | absent | `t0_before_prepared_absent` | **executed / passed** |
| **T1** | Discard | `t1_prepared_not_issued_discard`, `t1_issued_sync_failure_still_discard` | **executed / passed** |
| **T2** | Indeterminate | `t2_after_issued_indeterminate` | **executed / passed** |
| **T3** | Indeterminate (volatile host) | `t3_after_host_invocation_still_indeterminate` | **executed / passed** |
| **T4** | Indeterminate (volatile result) | `t4_host_complete_before_durable_completed_indeterminate` | **executed / passed** |
| **T5** | Completed reconstruct | `t5_completed_reconstruct_no_rehost` | **executed / passed** |
| **T6** | snapshot resume | `t6_snapshot_commit_resume` | **executed / passed** |

**Note (disclosed, not FAIL):** T3/T4 are observationally identical to T2 in **durable** state by design (host/result volatile). Harness labels document the crash point; durable classification remains Issued→Indeterminate. This matches R-RECOV-02 durable journal view.

**R5 = PASS. R14 = PASS.** No NOT-RUN crash points.

---

## 13. Mutation matrix (R15)

| Mutation target | Result | Evidence |
|---|---|---|
| Checksum corrupt | **KILLED** | `mutation_checksum_corrupt_kills` |
| Sequence gap | **KILLED** | `mutation_sequence_gap_kills` |
| Truncated WAL | **KILLED** | `partial_truncated_wal_rejected` |
| Indeterminate → local NotExecuted | **KILLED** | `mutation_indeterminate_not_silently_not_executed` |
| Recon without authoritative tag | **KILLED** | `recon_requires_evidence` |
| Cap revocation lost | **KILLED** (revoked set retained) | `mutation_cap_revocation_monotonic` |
| EffectId reuse after recover | **KILLED** (next advances) | `mutation_id_reuse_next_effect_advances` |
| Host before Issued (M5 path) | **KILLED** | runtime + differential panic tests |
| Persist fail before Issued | **KILLED** | `persist_fail_no_host` |
| Incomplete snapshot as valid | **KILLED** | `incomplete_begin_is_garbage` |
| Invoke host during `recover` | **KILLED** (no API surface) | structural + `no_host_surface` |
| Reorder / duplicate WAL as accepted history | **NOT-RUN** as dedicated mutator | sequence checks kill gaps/regressions; explicit dup-frame mutator not separate |
| Fabricate receipt/completion inside recover | **NOT-RUN** as code-injection mutator | recover has no receipt forge path; classification only from durable records |
| Skip checksum in production parse | **NOT-RUN** as source mutation | parse always verifies; no bypass flag |

No critical mutation **SURVIVED**. Coverage is incomplete relative to the full threat list → **PASS-DISCLOSED**, not claim of exhaustive mutation killing.

**R15 = PASS-DISCLOSED.**

---

## 14. Differential recovery (R13)

**Location:** `crates/ror-differential/src/m7.rs`

| Fixture | Result |
|---|---|
| empty | agree |
| Prepared-only (T1 Discard) | agree |
| Issued-only (T2 Indeterminate) | agree |
| Completed (T5) | agree |
| Snapshot T6 | agree |

Agreement is **evidence**, not formal proof.

**R13 = PASS.**

---

## 15. Determinism (R16)

- Sorted runnable reconstruction  
- BTreeMap effect classification order  
- No wall-clock / random / env in recovery  
- `recovery_determinism` double-run equality  

**R16 = PASS.**

---

## 16. Corruption / failure discipline (R17)

| Fault | Behavior |
|---|---|
| Truncated WAL | reject |
| Bad checksum | reject |
| Sequence discontinuity | reject |
| Incomplete snapshot | ignored (not Valid) |
| Bad snapshot digest | reject |
| Impossible recon tag | reject |

No silent ignore / silent repair / fabricate-on-corrupt observed.

**R17 = PASS.**

---

## 17. Dependency result (R20)

| Edge | Authority | Observed |
|---|---|---|
| `ror-persistence → ror-core` | required | present |
| `ror-runtime → ror-persistence` | required (R-TRUST-05) | present (pre-existing M5) |
| `ror-reference → ror-persistence` | **forbidden** | absent |
| `ror-persistence → ror-host` | forbidden | absent |
| `ror-persistence → ror-agent` | forbidden | absent |

**R20 = PASS. R2 = PASS.**

---

## 18. Unsafe / external-effect surface (R21)

| Check | Result |
|---|---|
| `#![forbid(unsafe_code)]` on persistence/reference/differential | present |
| `unsafe` / `std::process` / `std::net` / `Command` in M7 paths | **none** |
| Recovery external effect | **none** |

**R21 = PASS.**

---

## 19. OAD status (R18)

| OAD | final/09 | Impl treatment |
|---|---|---|
| **U-02** | OPEN | provisional SnapshotImage codec |
| **U-17** | OPEN | reconstruct runnable from statuses |
| **U-32** | OPEN | provisional 5-field WalFrame + checksum domain |
| U-27 / U-30 / U-06 residual | OPEN | thin Pending/mailbox/recon tags |

**No OAD closed. No silent normative freeze.**

**R18 = PASS.**

---

## 20. R-REG status (R19)

```text
R-REG = 184 × SPECIFIED   (final/08-evidence-status-matrix.md)
```

`5a04630` does not modify `final/` or `reg/`. No promotion to IMPLEMENTED / TESTED / VERIFIED / PROVEN.

**R19 = PASS.**

---

## 21. Documentation honesty (R23)

`M7-PROGRESS.md` claims implementation **COMPLETE** with workspace gates green and lists non-claims (no formal proof, OADs open). It does **not** claim “formally verified”, “proven”, or “production-ready”.

Reviewer note: “COMPLETE” means milestone implementation delivered under preflight scope — **not** GI-REC crash-consistency theorem discharge. Evidence class remains TEST / DIFFERENTIAL / MUTATION / CRASH-MATRIX, not PROOF.

**R23 = PASS-DISCLOSED.**

---

## 22. Selected evidence records

### Evidence Record: R7

- **Gate:** R7 M5 hinge preservation  
- **Status:** PASS  
- **Canonical authority:** R-DUR-01; GI-SEC-07 (`final/05`); R-TRUST-05  
- **Canonical rule:** `HostInvoked(E) ⇒ DurableIssued(E)`; Prepared+sync → Issued+sync → host  
- **Implementation location:** `ror-runtime/src/effects.rs` `run_effect_pipeline`; `ror-persistence` `IssuanceJournal` / `EffectJournal`  
- **Implementation behavior:** host only after durable Issued; recovery has no host API  
- **Test / evidence:** `effects::tests::persist_fail_no_host`, `happy_path_issued_before_host`; m5/m6 differential host-before-Issued panic  
- **Observed result:** all green; grep shows no host call in recovery modules  
- **Security relevance:** CRITICAL  
- **Evidence class:** IMPLEMENTATION + TEST  
- **Evidence limitation:** NONE on hinge compatibility  
- **OAD impact:** NONE  
- **R-REG impact:** NONE — remains SPECIFIED  
- **Reviewer conclusion:** M7 does not weaken or bypass the M5 hinge.

### Evidence Record: R5 / R14

- **Gate:** Crash matrix T0–T6  
- **Status:** PASS  
- **Canonical authority:** R-RECOV-02; R-DUR-04; GI-DUR causal journal  
- **Canonical rule:** T1 Discard; T2–T4 Indeterminate; T5 Completed reconstruct; T6 snapshot  
- **Implementation location:** `recovery.rs` `classify_effects` / `CrashHarness`  
- **Test / evidence:** `crash_matrix_tests::t0`…`t6` (17 crash_matrix tests all ok)  
- **Observed result:** all labeled points executed and passed  
- **Security relevance:** CRITICAL  
- **Evidence class:** CRASH-MATRIX  
- **Evidence limitation:** T3/T4 durable observation equals T2 (volatile host/result not journaled) — consistent with durable-state definition  
- **OAD impact:** NONE  
- **R-REG impact:** NONE  
- **Reviewer conclusion:** Crash classification matches frozen matrix at durable-journal granularity.

### Evidence Record: R6

- **Gate:** Recovery API security  
- **Status:** PASS  
- **Canonical authority:** R-RECOV-08; GI-REC-06 Indeterminate irreducibility  
- **Canonical rule:** Recovery never re-executes; NotExecuted only with authoritative evidence  
- **Implementation location:** `recover(&DurableState)`; `admit_recon_evidence`  
- **Test / evidence:** `no_host_surface`; recon evidence tests; mutation Indeterminate  
- **Observed result:** no host/execute/fs/net in recovery path  
- **Security relevance:** CRITICAL  
- **Evidence class:** IMPLEMENTATION + TEST  
- **Evidence limitation:** full live host-reconciliation adapter is out of M7 thin scope; hooks only  
- **OAD impact:** U-06 residual admissibility table  
- **R-REG impact:** NONE  
- **Reviewer conclusion:** Recovery is not an alternate host route.

### Evidence Record: R12

- **Gate:** Reference independence  
- **Status:** PASS  
- **Canonical authority:** R-RECOV-04; R-REF-02; dep forbidden edges  
- **Canonical rule:** independent recovery oracle; reference ↛ persistence/runtime/kernel/host  
- **Implementation location:** `ror-reference/src/recovery_model.rs`  
- **Test / evidence:** Cargo.toml deps; import scan; m7 differential agree  
- **Observed result:** core-only; separate parse/classify implementation  
- **Security relevance:** MEDIUM  
- **Evidence class:** IMPLEMENTATION + DIFFERENTIAL  
- **Evidence limitation:** shared provisional **layout** (not shared engine) required for byte-level compare under U-32/U-02  
- **OAD impact:** U-32/U-02 layout coupling for diff  
- **R-REG impact:** NONE  
- **Reviewer conclusion:** No BLOCK-INDEPENDENCE; semantic engines are distinct.

### Evidence Record: R3

- **Gate:** WAL semantics  
- **Status:** PASS-DISCLOSED  
- **Canonical authority:** R-PERSIST-02/06/08; U-32 OPEN  
- **Canonical rule:** framed sequenced checksummed WAL; gaps/corruption rejected  
- **Implementation location:** `wal.rs`  
- **Test / evidence:** round-trip, chain, gap, corrupt, truncate  
- **Observed result:** obligations met with provisional frame layout  
- **Security relevance:** HIGH  
- **Evidence class:** TEST  
- **Evidence limitation:** U-32 layout/checksum domain not frozen  
- **OAD impact:** U-32  
- **R-REG impact:** NONE  
- **Reviewer conclusion:** Implementable and tested; not OAD-closed.

### Evidence Record: R15

- **Gate:** Security mutations  
- **Status:** PASS-DISCLOSED  
- **Canonical authority:** GI-SEC-07; R-RECOV-05/08; R-PERSIST-08  
- **Canonical rule:** critical mutations must not survive  
- **Implementation location:** crash_matrix_tests + M5/M6 hinge tests  
- **Observed result:** no SURVIVED critical mutation among those executed; several threat-list items NOT-RUN as dedicated mutators  
- **Security relevance:** CRITICAL  
- **Evidence class:** MUTATION  
- **Evidence limitation:** mutation suite is not exhaustive relative to full R15 list  
- **OAD impact:** NONE  
- **R-REG impact:** NONE  
- **Reviewer conclusion:** Do not claim full mutation coverage; executed kills are clean.

### Evidence Record: R0

- **Gate:** Identity / lineage / authority integrity  
- **Status:** PASS  
- **Canonical authority:** process + final/* immutability  
- **Implementation location:** git `5a04630` on `61a9e57`  
- **Observed result:** no final/reg/dep/mod/spec changes; scope confined to authorized crates + progress doc  
- **Security relevance:** HIGH  
- **Evidence class:** OTHER  
- **Evidence limitation:** NONE  
- **OAD impact:** NONE  
- **R-REG impact:** NONE  
- **Reviewer conclusion:** Authorized implementation tip confirmed.

---

## 23. Evidence limitations (aggregate)

| ID | Limitation |
|---|---|
| U-02 | Snapshot/machine codecs provisional |
| U-17 | Runnable reconstruct-from-status provisional |
| U-32 | WalFrame field/checksum domain provisional |
| U-27 / U-30 | Pending locus / mailbox wire thin |
| U-06 residual | Per-class recon admissibility table incomplete |
| L-M7-MUT-PARTIAL | Not every R15 mutation has a dedicated source-level mutator |
| L-M7-T34-DURABLE | T3/T4 durable view ≡ T2 (volatile host/result) |
| L-M7-NO-PROOF | Tests ≠ formal crash-consistency proof (GI-REC theorem not discharged) |
| L-M7-THIN-MACHINE | Snapshot image is thin vs full GlobalState/CEK encoding |
| M5/M6 carry | prior disclosed limitations remain |

---

## 24. Defects found

| ID | Severity | Disposition |
|---|---|---|
| — | — | **No FAIL-IMPLEMENTATION or FAIL-TEST defects requiring correction stop** |
| fmt drift on `compare_m7` signature | cosmetic | mechanical `cargo fmt` only (review-allowed) |

No silent semantic repairs performed.

---

## 25. Explicit non-claims

```text
M7 is not formally verified.
Crash safety is not proven.
Host exactly-once is not inferred.
WAL/snapshot codecs are not frozen (U-02/U-32).
R-REG remains 184 × SPECIFIED.
No OAD was closed.
Differential agreement is evidence, not proof.
Mutation coverage is partial.
M8 was not implemented or preflighted by this review.
```

---

## 26. Final classification

### Aggregation

- BLOCK-* = **0**  
- FAIL-* = **0**  
- PASS-DISCLOSED ≥ 1 →  

```text
M7 IMPLEMENTATION REVIEW = ACCEPTED WITH DISCLOSED EVIDENCE LIMITATIONS
```

### Authorization for next operation

All mandatory security/authority gates (R0, R6, R7, R12, R18, R19, R20, R21) are **PASS** (not merely disclosed). Disclosures are codec/evidence-depth limitations, not security or governance blocks.

```text
NEXT = M8 PREFLIGHT
```

### Final state board

```text
M0–M4                      prior accepted
M5                         ACCEPTED WITH DISCLOSED EVIDENCE LIMITATIONS
M6                         ACCEPTED WITH DISCLOSED EVIDENCE LIMITATIONS
M7 preflight               GREEN WITH DISCLOSED LIMITATIONS — IMPLEMENTATION AUTHORIZED
M7 implementation          5a04630
M7 implementation review   ACCEPTED WITH DISCLOSED EVIDENCE LIMITATIONS
R-REG                      184 × SPECIFIED
NEXT                       M8 PREFLIGHT
```

---

*End of M7 IMPLEMENTATION REVIEW. Do not begin M8 in this operation.*
