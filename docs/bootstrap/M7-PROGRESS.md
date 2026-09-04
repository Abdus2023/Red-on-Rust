# M7 Implementation Progress — Persistence / WAL / Snapshot / Recovery

**Operation type:** M7 IMPLEMENTATION ONLY  
**Authority:** M7 PREFLIGHT @ `docs/bootstrap/M7-PREFLIGHT.md` — GREEN WITH DISCLOSED LIMITATIONS — IMPLEMENTATION AUTHORIZED  
**M6 review baseline:** ACCEPTED WITH DISCLOSED EVIDENCE LIMITATIONS  

```text
M7 IMPLEMENTATION = COMPLETE (workspace gates green)
NEXT = M7 IMPLEMENTATION REVIEW
```

---

## 1. Scope delivered

| Surface | Home | Status |
|---|---|---|
| WAL framing + checksum chain + sequence continuity | `ror-persistence/src/wal.rs` | DONE (U-32 provisional) |
| Unified journal kinds (Prepared/Issued/Completed/Reconciled/Event/Cap*) | `ror-persistence/src/journal.rs` | DONE |
| Atomic snapshot Begin→Body→Commit+digest | `ror-persistence/src/snapshot.rs` | DONE (U-02/U-17 provisional) |
| Recovery `Recover(D)=Replay(S,L,H)` + T0–T6 | `ror-persistence/src/recovery.rs` | DONE |
| Crash harness + security mutations | `ror-persistence` tests | DONE |
| Independent reference recovery | `ror-reference/src/recovery_model.rs` | DONE (core-only) |
| Differential recovery | `ror-differential/src/m7.rs` | DONE |
| M5 hinge (`IssuanceJournal` / `MemoryJournal`) | preserved | INTACT |
| M5/M6 regression | workspace `--lib` | GREEN |

---

## 2. Normative rules enforced

| Rule | Implementation |
|---|---|
| HostInvoked ⇒ DurableIssued (R-DUR-01) | Unchanged M5 hinge; `EffectJournal: IssuanceJournal` |
| Prepared ∧ ¬Issued ⇒ **Discard** (T1) | `EffectClass::Discard` |
| Issued ∧ ¬Completed ⇒ **Indeterminate** (T2–T4) | `EffectClass::Indeterminate` |
| Indeterminate ≠ NotExecuted | `is_not_executed_local() == false`; recon requires evidence_tag ∈ {1,2,3} |
| Completed ⇒ reconstruct; no re-host (T5 / R-RECOV-08) | `recover(DurableState)` — no host parameter |
| Snapshot resume (T6) | `SnapshotStore` + recover |
| No silent repair (R-RECOV-05) | checksum/seq/digest faults → `RecoveryFault` |
| Independent recovery (R-RECOV-04) | `ref_recover` does not import persistence |
| next_effect_id reconstruct (R-RECOV-09) | max(snapshot, max(id)+1) |
| Escrow / budget / logical_time not advanced on recover | restored from snapshot image |

---

## 3. Disclosed provisional codecs (OADs **not** closed)

| OAD | Choice |
|---|---|
| **U-32** | 5-field WalFrame: magic\|ver\|seq\|kind\|payload_len\|payload\|checksum; domain = SHA-256(prev‖seq‖kind‖payload) |
| **U-02** | `SnapshotImage` length-prefixed BE fields |
| **U-17** | Runnable queue **reconstructed** from actor status==Runnable (sorted) |
| **U-27** | Pending = status tag + pending_effect id |
| **U-30** | Mailbox as opaque bytes in actor snap |
| **U-06** residual | evidence_tag 1/2/3 admitted; 0 rejected |

```text
R-REG = 184 × SPECIFIED (no promotions)
No OAD closed by this implementation
```

---

## 4. Crash matrix evidence (harness)

| Point | Expected | Test |
|---|---|---|
| T0 | absent | `t0_before_prepared_absent` |
| T1 | Discard | `t1_prepared_not_issued_discard`, `t1_issued_sync_failure_still_discard` |
| T2 | Indeterminate | `t2_after_issued_indeterminate` |
| T3 | Indeterminate | `t3_after_host_invocation_still_indeterminate` |
| T4 | Indeterminate | `t4_host_complete_before_durable_completed_indeterminate` |
| T5 | Completed | `t5_completed_reconstruct_no_rehost` |
| T6 | snapshot resume | `t6_snapshot_commit_resume` |

Mutations (kill expected): checksum corrupt, sequence gap, truncated WAL, Indeterminate→NotExecuted without evidence, cap revocation monotonic, id counter advance, recovery determinism, budget/time freeze.

Differential: `m7::tests::diff_{t1,t2,t5,t6,empty}` — production ≡ reference observations.

---

## 5. Workspace gates

| Gate | Result |
|---|---|
| `cargo fmt --all` | exit 0 |
| `cargo check --workspace` | exit 0 |
| `cargo test --workspace --lib` | exit 0 (incl. M5/M6 + M7) |
| `cargo clippy --workspace --all-targets -- -D warnings` | exit 0 |
| Toolchain | `ror-stable` 1.88.0 |

---

## 6. Explicit non-claims

```text
M7 implementation review is NOT this operation.
M8 is NOT started.
Formal proof of crash safety is NOT claimed.
Host exactly-once is NOT inferred.
Provisional codecs do NOT freeze U-02/U-17/U-32.
R-REG remains 184 × SPECIFIED.
No OAD closed.
M5 HostInvoked ⇒ DurableIssued remains mandatory and intact.
```

---

## 7. Module map

```text
crates/ror-persistence/src/
  lib.rs          MemoryJournal + IssuanceJournal (M5) + crash_matrix_tests
  wal.rs          WalFrame / WalLog / checksum / sequence
  journal.rs      JournalRecord / EffectJournal
  snapshot.rs     SnapshotImage / SnapshotStore
  recovery.rs     recover / CrashHarness / EffectClass / T0–T6

crates/ror-reference/src/recovery_model.rs
  ref_recover     independent mirror (R-RECOV-04)

crates/ror-differential/src/m7.rs
  compare_m7 / fixtures
```

---

*End of M7 IMPLEMENTATION progress. NEXT = M7 IMPLEMENTATION REVIEW.*
