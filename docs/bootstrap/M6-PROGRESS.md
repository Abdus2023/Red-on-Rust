# M6 Implementation Progress — Actors / Mailbox / Scheduler

**Operation type:** M6 IMPLEMENTATION ONLY  
**Preflight authority:** `docs/bootstrap/M6-PREFLIGHT.md` @ `9e8b8ca`  
**Verdict class:**

```text
M6 IMPLEMENTATION = COMPLETE WITH DISCLOSED EVIDENCE LIMITATIONS
```

```text
NEXT = M6 IMPLEMENTATION REVIEW
```

Evidence labels: **FACT** | **DERIVED** | **DISCLOSED LIMITATION**

---

## 1. Identity

| Item | Value | Class |
|---|---|---|
| Branch | `arena/01a06993-red-on-rust` | FACT |
| Preflight base | `9e8b8ca` | FACT |
| M5 implementation ancestor | `f178562` | FACT |
| M5 review tip | `7e6eb44` | FACT |
| Toolchain | `ror-stable` 1.88.0 (offline) | FACT |
| R-REG | **184 × SPECIFIED** (unchanged) | FACT |
| OADs closed | **none** | FACT |

---

## 2. Scope delivered

| Surface | Status | Location |
|---|---|---|
| Monotonic `ActorIdAlloc` | DONE | `ror-core::types::ActorIdAlloc` |
| `ActorStatus` minimal set | DONE (U-27 provisional) | `ror-runtime::actor` |
| `GlobalState` + `BTreeMap` actors | DONE (U-34 provisional) | `ror-runtime::actor` |
| FIFO `RunnableQueue` at-most-once | DONE | `ror-runtime::actor` |
| FIFO `Mailbox` + capacity admission | DONE | `ror-runtime::actor` |
| Marshal reject Cap/Fn/Delegated | DONE | `marshal_message` |
| Transactional spawn + empty default caps | DONE | `spawn_child` |
| Spawn manifest derive-only | DONE | `spawn_child` + tests |
| Async send + wake-once | DONE | `send_async` |
| Blocking receive (no fuel) | DONE | `receive_or_block` |
| Scheduler 1-turn FIFO | DONE | `scheduler_turn` |
| Pending exclusion | DONE | `set_pending` |
| Deadlock vs QuiescenceReconcile | DONE (thin Indeterminate) | `finish_empty_runnable` |
| `Expr::Delegate` + envelope path | DONE (L-M6-DELEG-AST) | core AST + `issue_delegation` / `admit_delegation` / `send_delegation` |
| M5 hinge preserved | DONE | no Actor→Host path; Request still via `run_effect_pipeline` only |
| Independent reference mirror | DONE | `ror-reference::actor_model` |
| Differential m6 | DONE | `ror-differential::m6` |
| Mutations (intent tests) | DONE | runtime + differential tests |
| M1–M5 regression | DONE | full workspace `--lib` green |

### Explicitly not done / thin

| Item | Disposition |
|---|---|
| Full R-RECOV-08 host reconcile engine | Thin Indeterminate record only (L-M6-RECOV) |
| Message-to-terminated policy | Reject `ActorNotFound` only — no invented drop/undeliverable (L-M6-TERM) |
| Pending-on-death auto-cancel | **Not implemented** (forbidden invention) |
| ActorId reuse | **Not implemented** |
| Yield/Halt full CEK | Value-as-terminal thin; bare CEK still Unsupported for Yield/Halt |
| Full multi-frame actor CEK for Spawn/Send/Receive subexpr eval | Thin Value-leaf forms in actor turn; bare CEK still faults those forms without GlobalState |
| U-30 checked-bytes mailbox wire form | In-memory checked `Value` after marshal (DISCLOSED) |
| U-03 full BudgetAllocationSpec | Integer unit escrow only (DISCLOSED) |
| OAD close / R-REG promotion | **Forbidden** — not done |

---

## 3. Module map

```text
crates/ror-core/src/types.rs          ActorIdAlloc
crates/ror-core/src/machine.rs       Fault::{MarshalCapabilityRejected,ReservedCapacityExceeded,ActorNotFound}
                                     Expr::Delegate; DelegatedCapability envelope fields
crates/ror-runtime/src/actor.rs      GlobalState, Mailbox, RunnableQueue, spawn/send/receive/delegate, scheduler
crates/ror-runtime/src/cek.rs        bare Spawn/Send/Receive/Delegate still Unsupported without GlobalState
crates/ror-runtime/src/lib.rs        exports actor surface
crates/ror-reference/src/actor_model.rs  independent mirror
crates/ror-reference/src/cap_algebra.rs  parent_of for revalidation
crates/ror-differential/src/m6.rs    P↔R actor observations
docs/bootstrap/M6-PROGRESS.md        this file
```

---

## 4. Semantic freezes consumed (no redesign)

| Freeze | Evidence |
|---|---|
| FIFO runnable + at-most-once + 1 transition/turn | `RunnableQueue` + `scheduler_turn` tests |
| Blocked/Pending/Terminal never scheduled | tests + defensive skip |
| Spawn transactional; default empty caps; derive-only manifest | `spawn_child` + M025-intent test |
| Mailbox FIFO; sender pays capacity | mailbox tests |
| Cap-in-ordinary-Send reject | marshal + send tests |
| Delegation only via dedicated path | `send_delegation` / ordinary reject of `DelegatedCapability` |
| Pending ≠ Deadlock; Deadlock∧∃Pending ⇒ QuiescenceReconcile δ_t=0 no budget mut | pending tests |
| Host only via M5 pipeline | no HostExecutor in actor module; structural test |
| No id reuse | `ActorIdAlloc` saturating monotonic |

---

## 5. Test evidence (executed)

```text
cargo fmt --all
cargo clippy --workspace --all-targets -- -D warnings   # exit 0
cargo test --workspace --lib                            # all crates green
```

| Crate | Lib tests (approx) |
|---|---|
| ror-runtime | 79 (incl. 28 actor) |
| ror-reference | 13 (incl. actor_model) |
| ror-differential | 66 (incl. 9 m6) |
| ror-core / kernel / host / persistence | prior suites green |

Selected production unit coverage:

- ActorId monotonic; mailbox FIFO; capacity deny
- runnable at-most-once; FIFO selection order; determinism
- blocked / pending / terminal never scheduled
- send wake-once; marshal reject Cap/Fn/Delegated
- spawn empty default + manifest attenuate + budget fail atomic
- quiescence no budget mutation; Pending preserved
- delegation issue/admit; wrong-target ctx identical
- mutation intents: FIFO, M011 blocked, M012 dup, M025 no clone, M033 capacity, cap-send, host-from-actor absent

Differential:

- three-roots FIFO agree
- receive-block Deadlock agree
- pending Quiescence agree
- send wakeup mailbox FIFO agree
- spawn budget/events agree
- marshal reject agree

---

## 6. M5 hinge integrity

```text
HostInvoked(E) ⇒ DurableIssued(E)
```

- Actor/Scheduler/Mailbox modules do **not** take or call `HostExecutor`.
- `Expr::Request` remains M5 CEK + `run_effect_pipeline` only.
- Multi-actor Pending is a **status** hook; full effect-in-turn wiring reuses M5 services when a later driver supplies them — M6 does not open a second host path.

---

## 7. Reference independence (R-REF-02)

| Check | Result |
|---|---|
| `ror-reference` Cargo deps | `ror-core` only |
| Actor mirror location | `actor_model.rs` (separate authorship) |
| Production imports reference | **no** |
| Differential harness only compares observations | yes |

---

## 8. Disclosed limitations (carry + M6)

| ID | Note |
|---|---|
| U-03 | Thin integer spawn budget |
| U-27 | Minimal ActorStatus labels |
| U-28 | Minimal MachineEvent set |
| U-30 | Checked in-memory Value post-marshal, not 15A bytes |
| U-34 | GlobalState/RunnableQueue provisional |
| U-35 | Operational FIFO+IDs; theorem params open |
| U-02/U-08/U-09 | Codecs / faults / value domains open |
| L-M6-TERM | No invented message-to-dead / pending-on-death policy |
| L-M6-RECOV | Quiescence records Indeterminate only |
| L-M6-DELEG-AST | `Expr::Delegate` addendum constructor implemented |
| L-M6-CEK-CTX | Bare CEK still Unsupported for actor forms; actor module owns GlobalState turns |
| M5 carry | CapRef public ctor; HostExecutor packaging; thin effect budget |

---

## 9. R-REG / OAD

```text
184 × SPECIFIED — no edits
No OAD closed
No requirement promotion claimed
```

---

## 10. Non-claims

```text
No formal proof of R-ACTOR-07 determinism theorem (U-35 open).
No production certification.
No M7 recovery/WAL/snapshot work.
No claim that bare single-threaded evaluate(Spawn) works without GlobalState.
No claim that full multi-frame CEK nesting of Spawn/Send/Receive is complete.
M6 review is a separate operation.
```

---

## 11. Completion board

```text
M6 preflight                 GREEN WITH DISCLOSED LIMITATIONS — IMPLEMENTATION AUTHORIZED
M6 implementation            COMPLETE WITH DISCLOSED EVIDENCE LIMITATIONS
M6 semantic verification     NOT CLAIMED (review next)
R-REG                        184 × SPECIFIED
M7                           NOT STARTED
NEXT                         M6 IMPLEMENTATION REVIEW
```

---

*End of M6-PROGRESS.*
