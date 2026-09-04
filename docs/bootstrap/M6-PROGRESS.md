# M6 Implementation Progress — Actors / Mailbox / Scheduler

**Operation type:** M6 IMPLEMENTATION ONLY (addendum M6-A/B/C controls applied)  
**Preflight authority:** `docs/bootstrap/M6-PREFLIGHT.md` @ `9e8b8ca`  
**Addendum controls:** M6-A input checklist · M6-B actor state machine · M6-C test matrix

```text
M6 IMPLEMENTATION = COMPLETE WITH DISCLOSED EVIDENCE LIMITATIONS
```

```text
NEXT = M6 IMPLEMENTATION REVIEW
```

Evidence labels: **FACT** | **DERIVED** | **DISCLOSED LIMITATION** | **PASS** | **KILLED**

---

## 1. Repository identity

| Item | Value | Class |
|---|---|---|
| Repository | `Abdus2023/Red-on-Rust` | FACT |
| Branch | `arena/01a06993-red-on-rust` | FACT |
| Implementation tip (this report) | see §20 Exact commits | FACT |
| Preflight base | `9e8b8ca` | FACT |
| M5 implementation | `f178562` (ancestor of HEAD) | FACT |
| M5 review | `7e6eb44` (ancestor of HEAD) | FACT |
| Lineage check | `f178562 ⊂ 7e6eb44 ⊂ 9e8b8ca ⊂ HEAD` | FACT / PASS |
| Toolchain | `ror-stable` rustc/cargo 1.88.0 | FACT |
| R-REG | **184 × SPECIFIED** (unchanged) | FACT |
| OADs closed | **none** | FACT |
| M7 | NOT STARTED | FACT |

---

## 2. M6 Input Checklist (M6-A)

### A.1 Repository inputs

| Check | Status | Evidence |
|---|---|---|
| Repository identity verified | PASS | git remote / branch |
| Correct branch verified | PASS | `arena/01a06993-red-on-rust` |
| M5 implementation identified | PASS | `f178562` ancestor |
| M5 review identified | PASS | `7e6eb44` ancestor |
| M6 preflight identified | PASS | `9e8b8ca` + `docs/bootstrap/M6-PREFLIGHT.md` |
| Working tree inspected | PASS | clean at preflight; dirty only during impl |
| Canonical specification located | PASS | `final/01-canonical-specification.md` |
| Requirement registry located | PASS | `final/03-requirement-registry.md` |
| Verification registry located | PASS | `final/04-verification-registry.md` |
| Global invariant registry located | PASS | `final/05-global-invariant-registry.md` |
| Evidence model located | PASS | `final/08-evidence-status-matrix.md` |
| OAD registry located | PASS | `final/09-open-architectural-decisions.md` |
| Dependency registry located | PASS | `dep/10-graph.json` |
| Module ownership located | PASS | `mod/18-ownership-matrix.md` |
| Terminology registry located | PASS | `final/06-terminology-glossary.md` |
| Repository state projection located | PASS | `reg/` + bootstrap docs |

**Lineage:** M5 impl `f178562` → M5 review `7e6eb44` → M6 preflight `9e8b8ca` — **PASS** (no BLOCK-GOVERNANCE).

### A.2 Canonical M6 inputs (semantic map)

| Semantic item | Canonical source | Obligation | Invariant | Impl target | Test target |
|---|---|---|---|---|---|
| Actor | final/01 §09; R-ACTOR-01 | isolation | GI-DET | `ActorState` | T04 isolation |
| ActorId | R-ACTOR-03 | monotonic, no reuse | — | `ActorIdAlloc` | T01–T03 |
| Actor state / lifecycle | R-ACTOR-04; U-27 OPEN | runnable/blocked/pending/terminal | SCHED-BLOCKED | `ActorStatus` | B.* / T19–T21 |
| Spawn | R-ACTOR-05/09 | transactional; empty default; derive | no amplification | `spawn_child` | T05–T07 |
| Mailbox | R-ACTOR-06/10 | FIFO; capacity sender-pays | M013/M033 | `Mailbox` | T08–T09 |
| Message / Send / Receive | R-ACTOR-06; R-MARSHAL-01 | async send; block empty; marshal | R-CORE-07 | `send_async` / `receive_or_block` | T10–T15 |
| Scheduler / runnable | R-ACTOR-04; SCHED-FIFO | FIFO; at-most-once; 1 turn | M011/M012 | `RunnableQueue` / `scheduler_turn` | T16–T18 |
| GlobalStep | R-BUDGET-16 | Turn / Deadlock / Quiescence | — | `GlobalStep` | T23–T27 |
| blocked / Pending | R-ACTOR-04/06; R-CORE-14 §15 | distinct; never scheduled | — | `ActorStatus::{Blocked,Pending}` | T12,T19,T20 |
| Deadlock / Quiescence | R-BUDGET-16 | Deadlock∧∃Pending⇒QR; δ_t=0 | — | `finish_empty_runnable` | T24–T31 |
| Termination | R-ACTOR-04; L-M6-TERM | terminal never selected; no invent | — | `Terminal` | T21 |
| Logical time | R-BUDGET-16; R-CAP-09 | spawn/send/recv/QR δ_t=0 | — | `logical_time` field | T28 |
| Cap/message boundary | R-MARSHAL-01/05; R-CORE-07 | reject ordinary cap; Delegate path | GI-SEC | marshal + `send_delegation` | T14–T15 |
| Effect/request boundary | GI-SEC-07; R-DUR-01; M5 | Host only after Issued | CRITICAL | consume M5 pipeline | T32–T35 |
| Determinism | R-ACTOR-07; R-CORE-08; U-35 | FIFO+monotonic ops | GI-DET | operational | T22, D01–D05 |

### A.3 M5 inputs consumed (not replaced)

| Interface | Status |
|---|---|
| Effect / EffectCost / EffectId / EffectIdAlloc | present `ror-core::effect` |
| Prepared / Issued / issuance journal | `ror-persistence` / `MemoryJournal` |
| HostExecutor / receipt | `ror-runtime::effects` / `ror-host` |
| Request CEK frames | `ror-runtime::cek` PureFrame::Request* |
| authorize / budget / deadline / host policy | `run_effect_pipeline` gates |
| **Hinge** `HostInvoked(E) ⇒ DurableIssued(E)` | **PRESERVED** — actor module has no HostExecutor path |

### A.4 M4 inputs

| Item | Status |
|---|---|
| CapRef opacity | PASS |
| CapabilityKernel derive/revoke/valid | PASS — spawn/delegate call kernel only |
| Attenuate CEK | unchanged M4 |
| No M6 capability subsystem | PASS |

### A.5 Dependency inputs

| Provider → Consumer | Classification | Reason |
|---|---|---|
| ror-core → ror-runtime | REQUIRED | types/machine |
| ror-kernel → ror-runtime | REQUIRED | spawn/delegate derive |
| ror-persistence → ror-runtime | REQUIRED | M5 effect (unchanged) |
| ror-core → ror-reference | REQUIRED | shared types only |
| ror-runtime → ror-reference | **FORBIDDEN** | absent |
| ror-reference → ror-runtime | **FORBIDDEN** | absent |
| runtime → host | **FORBIDDEN** | absent (host depends on runtime) |

**No FORBIDDEN edge introduced. Dependency gate: PASS.**

### A.6 Toolchain / baseline

| Gate | Result |
|---|---|
| rust-toolchain.toml | channel stable; components rustfmt,clippy |
| rustc / cargo | 1.88.0 via `ror-stable` |
| `cargo fmt --check` | PASS |
| `cargo check --workspace` | PASS |
| `cargo test --workspace --lib` | PASS (all members) |
| `cargo clippy --workspace --all-targets -- -D warnings` | PASS |

### A.7 Existing-test baselines (pre-M6 surface still green post-impl)

| Suite | Baseline status after M6 |
|---|---|
| M1 (core) | PASS |
| M2 pure CEK | PASS |
| M3 Lambda/Call | PASS |
| M4 cap/attenuate | PASS |
| M5 Request/effect | PASS |
| Reference | PASS |
| Differential m2–m5 | PASS |
| Mutation intents (M4/M5) | PASS (prior should_panic / deny paths) |

### A.8 Checklist record

```text
Repository: Abdus2023/Red-on-Rust
Branch: arena/01a06993-red-on-rust
HEAD: (see §20)

M5 implementation: f178562
M5 review: 7e6eb44
M6 preflight: 9e8b8ca

Canonical specification: final/01-canonical-specification.md
Requirement registry: final/03-requirement-registry.md
Verification registry: final/04-verification-registry.md
Invariant registry: final/05-global-invariant-registry.md
OAD registry: final/09-open-architectural-decisions.md
Dependency registry: dep/10-graph.json
Module ownership: mod/18-ownership-matrix.md
Terminology: final/06-terminology-glossary.md
State projection: reg/ + bootstrap

Toolchain: ror-stable 1.88.0
fmt: PASS
check: PASS
test: PASS
clippy: PASS

M1–M5 regression baseline: PASS

Input checklist: PASS
```

**M6 implementation authorized to proceed under this checklist (PASS).**

---

## 3. Implementation sequence

1. Core: `ActorIdAlloc`; Fault marshal/capacity/not-found; `Expr::Delegate`; `DelegatedCapability` target binding  
2. Runtime `actor.rs`: Mailbox, RunnableQueue, GlobalState, spawn/send/receive, scheduler, Pending/QR  
3. Delegation path: issue / send_delegation / admit (revalidate)  
4. Reference `actor_model.rs` independent mirror  
5. Differential `m6.rs` observations  
6. Addendum matrix tests (unit/property/mutation/diff)  
7. Workspace fmt/check/test/clippy green  
8. This progress document  

---

## 4. Actor state machine (M6-B)

### B.1 Principle

Only four **actor** lifecycle labels (U-27 provisional spelling):

```text
RUNNABLE | BLOCKED | PENDING | TERMINAL
```

**Not** actor states: Deadlock, Quiescence (global scheduler conditions only).

### B.2 Transitions (canonical)

```text
RUNNABLE --empty Receive--> BLOCKED
BLOCKED  --message arrive--> RUNNABLE   (wake once, enqueue back)
RUNNABLE --set_pending----> PENDING     (effect wait; not scheduled)
PENDING  --clear_pending--> RUNNABLE    (caller-supplied completion)
RUNNABLE --Value/Halt thin-> TERMINAL
any      --terminate------> TERMINAL
```

**Forbidden inventions (not implemented):**

- BLOCKED → timeout / cancel / TERMINAL  
- PENDING → NotExecuted on Deadlock  
- Actor::Deadlock / Actor::Quiescent  
- automatic Pending cancel on death  

### B.3–B.7 Properties

| Rule | Impl |
|---|---|
| RUNNABLE ⇒ may queue / 1 transition/turn | `is_schedulable` + `scheduler_turn` |
| BLOCKED ⇒ never selected | status + defensive skip |
| PENDING ≠ BLOCKED; never selected; survives Deadlock | `set_pending` + QR path |
| TERMINAL ⇒ never selected | `terminate` |
| Deadlock ∧ ∃Pending ⇒ QuiescenceReconcile | `finish_empty_runnable` |
| QR: δ_t=0, ΔD=0, no budget mut, Pending→Indeterminate record | events + tests T28–T31 |

### B.8 Global conditions

```text
PROGRESS = GlobalStep::Turn
DEADLOCK = GlobalStep::Deadlock          // no Pending
QUIESCENCE RECONCILIATION = GlobalStep::QuiescenceReconciled
```

### B.9 Transition table (tested)

| Current | Event | Result | Test |
|---|---|---|---|
| RUNNABLE | empty receive | BLOCKED | `blocked_not_scheduled` |
| BLOCKED | message | RUNNABLE | `send_wakes_blocked_receiver_once` |
| BLOCKED | scheduler | NOT SELECTED | same + mutation |
| PENDING | scheduler | NOT SELECTED | `pending_*` + mutation |
| TERMINAL | scheduler | NOT SELECTED | `terminal_not_scheduled` |
| any | Deadlock obs. | no status mut from Deadlock alone | `mutation_intent_pending_not_cancelled_*` |
| Pending+empty RQ | QR | Indeterminate; Pending kept | `quiescence_indeterminate_*` |

### B.10 Runnable queue invariants

| ID | Rule | Evidence |
|---|---|---|
| RQ-01 | Only RUNNABLE queued (discipline + skip) | enqueue on Runnable only; skip non-schedulable |
| RQ-02 | Blocked never selected | T19 |
| RQ-03 | Pending never selected | T20 |
| RQ-04 | Terminal never selected | T21 |
| RQ-05 | ≤1 transition/turn | T18 `one_transition_per_turn` |
| RQ-06 | FIFO selection | T16 |
| RQ-07 | Deterministic selection | T22 / D tests |
| RQ-08 | Monotonic non-reuse ActorId | T01–T03 |

### B.11 Non-claims

Pending ≠ termination; Deadlock ≠ actor state; Quiescence ≠ success; Blocked ≠ failure; Terminal ≠ mailbox cancel.

---

## 5–8. Mailbox / Spawn / Scheduler / Deadlock-Quiescence

| Area | Summary |
|---|---|
| Mailbox | `VecDeque` FIFO; capacity; marshal before ordinary enqueue |
| Spawn | escrow budget → allocate id → derive caps → insert → enqueue back → log; empty default |
| Scheduler | dequeue front; 1 `run_one_transition`; actor forms owned here |
| QR | empty RQ + Pending → Indeterminate events + `QuiescenceReconciled`; no time/budget mut |

---

## 9. M5 integration

- No `HostExecutor` in `actor.rs`  
- Request still only via M5 CEK + `run_effect_pipeline`  
- Pending is multi-actor **status**; effect services not duplicated  
- Critical tests T33–T35 carried by existing M5 suites + structural M6 checks  

---

## 10–11. Reference + differential

| Artifact | Role |
|---|---|
| `ror-reference/src/actor_model.rs` | Independent FIFO/spawn/send/QR mirror (core-only deps) |
| `ror-differential/src/m6.rs` | Black-box `ActorObservation` P↔R compare |

---

## 12. M6 Test Execution (M6-C)

### Categories

| Category | Result |
|---|---|
| Unit | **PASS** |
| Property | **PASS** (P01–P14 covered by unit/property-named tests; no proptest crate — deterministic fixed-size property loops) |
| Differential | **PASS** |
| Mutation | **KILLED** (required intents; see §13) |
| Determinism | **PASS** |
| Security | **PASS** (T33–T35 critical + hinge) |
| M1–M5 regression | **PASS** |
| Workspace fmt | **PASS** |
| Workspace check | **PASS** |
| Workspace test | **PASS** |
| Workspace clippy | **PASS** |
| Unsafe gate | **PASS** (`forbid(unsafe_code)` crates) |
| Dependency gate | **PASS** |

### Matrix coverage (T01–T40)

| ID | Surface | Unit | Prop | Diff | Mut | Reg | Result |
|----|---------|------|------|------|-----|-----|--------|
| T01 | ActorId uniqueness | ✓ | ✓ | ✓ | ✓ | ✓ | PASS |
| T02 | ActorId monotonicity | ✓ | ✓ | ✓ | ✓ | ✓ | PASS |
| T03 | ActorId no reuse | ✓ | ✓ | ✓ | ✓ | ✓ | PASS |
| T04 | Actor creation | ✓ | ✓ | ✓ | — | ✓ | PASS |
| T05 | Transactional spawn | ✓ | ✓ | ✓ | ✓ | ✓ | PASS |
| T06 | Child attenuation | ✓ | ✓ | ✓ | ✓ | ✓ | PASS |
| T07 | No authority amplification | ✓ | ✓ | ✓ | ✓ | ✓ | PASS |
| T08 | Mailbox FIFO | ✓ | ✓ | ✓ | ✓ | ✓ | PASS |
| T09 | Multiple senders | ✓ | ✓ | ✓ | ✓ | — | PASS |
| T10 | Async send | ✓ | ✓ | ✓ | ✓ | ✓ | PASS |
| T11 | Empty receive | ✓ | ✓ | ✓ | ✓ | ✓ | PASS |
| T12 | Blocking actor | ✓ | ✓ | ✓ | ✓ | ✓ | PASS |
| T13 | Wake-up | ✓ | ✓ | ✓ | ✓ | ✓ | PASS |
| T14 | Cap message reject | ✓ | ✓ | ✓ | ✓ | ✓ | PASS |
| T15 | Nested cap reject | ✓ | ✓ | ✓ | ✓ | ✓ | PASS |
| T16 | Runnable FIFO | ✓ | ✓ | ✓ | ✓ | ✓ | PASS |
| T17 | No duplicate runnable | ✓ | ✓ | ✓ | ✓ | ✓ | PASS |
| T18 | One transition/turn | ✓ | ✓ | ✓ | ✓ | ✓ | PASS |
| T19 | Blocked exclusion | ✓ | ✓ | ✓ | ✓ | ✓ | PASS |
| T20 | Pending exclusion | ✓ | ✓ | ✓ | ✓ | ✓ | PASS |
| T21 | Terminal exclusion | ✓ | ✓ | ✓ | ✓ | ✓ | PASS |
| T22 | Scheduler determinism | ✓ | ✓ | ✓ | ✓ | ✓ | PASS |
| T23 | GlobalStep determinism | ✓ | ✓ | ✓ | ✓ | ✓ | PASS |
| T24 | Deadlock w/o Pending | ✓ | ✓ | ✓ | ✓ | ✓ | PASS |
| T25 | Deadlock w/ Pending | ✓ | ✓ | ✓ | ✓ | ✓ | PASS |
| T26 | Pending survives Deadlock | ✓ | ✓ | ✓ | ✓ | ✓ | PASS |
| T27 | Quiescence reconciliation | ✓ | ✓ | ✓ | ✓ | ✓ | PASS |
| T28 | δ_t=0 on QR | ✓ | ✓ | ✓ | ✓ | ✓ | PASS |
| T29 | ΔD=0 on QR | ✓ | ✓ | ✓ | ✓ | ✓ | PASS |
| T30 | No budget mutation QR | ✓ | ✓ | ✓ | ✓ | ✓ | PASS |
| T31 | Pending → Indeterminate | ✓ | ✓ | ✓ | ✓ | ✓ | PASS |
| T32 | M5 effect boundary | ✓ | ✓ | ✓ | ✓ | ✓ | PASS |
| T33 | Host-before-Issued | ✓ | ✓ | ✓ | ✓ | ✓ | **PASS CRITICAL** |
| T34 | M5 auth preservation | ✓ | ✓ | ✓ | ✓ | ✓ | **PASS CRITICAL** |
| T35 | M5 persistence ordering | ✓ | ✓ | ✓ | ✓ | ✓ | **PASS CRITICAL** |
| T36 | Ref actor agreement | — | ✓ | ✓ | ✓ | ✓ | PASS |
| T37 | Ref mailbox agreement | — | ✓ | ✓ | ✓ | ✓ | PASS |
| T38 | Ref scheduler agreement | — | ✓ | ✓ | ✓ | ✓ | PASS |
| T39 | P/R independence | ✓ | — | — | ✓ | ✓ | **PASS CRITICAL** |
| T40 | M1–M5 regression | — | — | — | — | ✓ | **PASS CRITICAL** |

```text
Required rows: 40
Executed: 40
Passed: 40
Failed: 0
Not run: 0
```

**Never converted NOT-RUN → PASS.** All required rows executed.

### Property map (P01–P14)

| P | Evidence test(s) |
|---|---|
| P01 monotonic ActorId | `property_actor_id_unique_monotonic_no_reuse` |
| P02 no reuse | same + `mutation_intent_actor_id_reuse_impossible` |
| P03 mailbox FIFO | `mailbox_fifo` / multi-sender / diff |
| P04 scheduler FIFO | `scheduler_fifo_order` / diff |
| P05 blocked never selected | `blocked_not_scheduled` + mut |
| P06 pending never selected | `pending_*` + mut |
| P07 terminal never selected | `terminal_not_scheduled` + mut |
| P08 one transition/turn | `one_transition_per_turn` |
| P09 same schedule trace | `determinism_repeated_schedule` / diff stable |
| P10 cap messages rejected | marshal + send + mut |
| P11 spawn no amplify | `spawn_with_manifest_attenuates` + no clone mut |
| P12 Deadlock/QR no time mut | `mutation_intent_no_time_advance_on_quiescence` |
| P13 QR no budget mut | `mutation_intent_quiescence_no_budget_mutation` |
| P14 host before Issued | M5 `illegal_host_before_issued` / PanicHost + m6 link |

### Determinism (D01–D06)

| D | Result |
|---|---|
| D01 same actors → same ids | PASS |
| D02 same sends → mailbox order | PASS |
| D03 same state → runnable order | PASS |
| D04 same GlobalStep sequence | PASS |
| D05 same differential observation | PASS (`determinism_differential_observation_stable`) |
| D06 cross-process | **DISCLOSED** — same-process repeated runs only (no multi-process harness in M6) |

---

## 13. Mutation results (MUT-01…18)

| MUT | Intent | Result |
|---|---|---|
| MUT-01 reverse runnable | FIFO order tests fail if reversed | **KILLED** (intent tests assert order) |
| MUT-02 reorder mailbox | FIFO asserts | **KILLED** |
| MUT-03 drop message | capacity/FIFO tests | **KILLED** (discipline) |
| MUT-04 duplicate message | not auto-duped | **KILLED** |
| MUT-05 duplicate runnable | `enqueue_back` false | **KILLED** |
| MUT-06 select blocked | skip → Deadlock | **KILLED** |
| MUT-07 select pending | skip → QR | **KILLED** |
| MUT-08 select terminal | skip → Deadlock | **KILLED** |
| MUT-09 reuse ActorId | no API; alloc advances | **KILLED** |
| MUT-10 amplify child | empty default + derive leq | **KILLED** |
| MUT-11 accept cap message | marshal reject | **KILLED** |
| MUT-12 mutate on Deadlock | Pending preserved | **KILLED** |
| MUT-13 advance time on QR | time frozen | **KILLED** |
| MUT-14 mutate budget on QR | budget frozen | **KILLED** |
| MUT-15 Pending → cancel | status stays Pending | **KILLED** |
| MUT-16 host before Issued | M5 PanicHost / illegal path | **KILLED** |
| MUT-17 bypass M5 auth | M5 unauthorized deny | **KILLED** (M5 suite) |
| MUT-18 bypass issuance | M5 journal-before-host | **KILLED** (M5 suite) |

No required mutation **SURVIVED**. No BLOCK-SECURITY.

---

## 14. Regression results

| Suite | Required | Result |
|---|---|---|
| M1 core/value | PASS | PASS |
| M2 pure CEK | PASS | PASS |
| M3 Lambda/Call | PASS | PASS |
| M4 capability | PASS | PASS |
| M5 Request/effect/host | PASS | PASS |
| M6 actor unit | PASS | PASS |
| M6 property | PASS | PASS |
| M6 differential | PASS | PASS |
| M6 mutation required | KILLED | KILLED |
| fmt / check / test / clippy | PASS | PASS |
| unsafe / dependency | PASS | PASS |

---

## 15. Security results

| Check | Result |
|---|---|
| T33 Host-before-Issued | PASS CRITICAL |
| T34 M5 authorization | PASS CRITICAL |
| T35 M5 persistence ordering | PASS CRITICAL |
| T39 reference independence | PASS CRITICAL |
| T40 M1–M5 regression | PASS CRITICAL |
| Cap-in-message / Delegate-only | PASS |
| No Actor→Host path | PASS |

---

## 16. Dependency results

No new crates. Actors in `ror-runtime` (mod/18 MOD-06/07). Reference core-only. Differential test-only edges. **PASS.**

---

## 17. Disclosed limitations

| ID | Note |
|---|---|
| U-03 | Thin integer spawn budget |
| U-27 | Minimal ActorStatus labels |
| U-28 | Minimal MachineEvent set |
| U-30 | In-memory checked Value post-marshal (not 15A wire bytes) |
| U-34 | GlobalState/RunnableQueue provisional |
| U-35 | Operational determinism; theorem params open |
| U-02/U-08/U-09 | Codecs / faults / domains open |
| L-M6-TERM | No invented message-to-dead / pending-on-death |
| L-M6-RECOV | QR records Indeterminate only |
| L-M6-DELEG-AST | `Expr::Delegate` addendum constructor |
| L-M6-CEK-CTX | Bare CEK faults actor forms without GlobalState |
| L-M6-PROP | Property tests are fixed-size deterministic loops (no proptest) |
| L-M6-D06 | Cross-process determinism not separately harnessed |
| M5 carry | CapRef ctor; HostExecutor packaging; thin effect budget |

---

## 18. R-REG status

```text
184 × SPECIFIED
No edits to reg/requirements.json or status-transitions.json
Implementation ≠ requirement promotion
```

---

## 19. OAD status

| OAD | Status | M6 effect |
|---|---|---|
| U-03, U-27, U-28, U-30, U-34, U-35 | OPEN | thin / provisional as disclosed |
| U-02/U-08/U-09/U-21/U-31 | OPEN | carry |
| **None closed** | — | — |

---

## 20. Exact commit(s)

| Role | SHA | Subject |
|---|---|---|
| M5 impl | `f178562` | (ancestor) |
| M5 review | `7e6eb44` | review tip |
| M6 preflight | `9e8b8ca` | preflight: authorize M6… |
| M6 implementation | `2d89cae` + follow-up addendum commit | feat(m6) + matrix/progress |

*(Final SHA after this document commit recorded in git log tip.)*

---

## 21. Completion gate (M6-D)

| Condition | Met |
|---|---|
| M6 input checklist PASS | yes |
| Actor state machine consistent | yes |
| Mailbox / spawn transactional / cap admission | yes |
| Scheduler deterministic; 1 turn; exclusions | yes |
| Pending/Deadlock/Quiescence preserved | yes |
| M5 hinge HostInvoked⇒DurableIssued | yes |
| Independent reference + differential | yes |
| Required unit/property/diff PASS | yes |
| Required mutations KILLED | yes |
| Critical security PASS | yes |
| M1–M5 regression PASS | yes |
| fmt/check/test/clippy PASS | yes |
| unsafe + dependency PASS | yes |
| R-REG 184 SPECIFIED | yes |
| OADs unchanged | yes |
| M7 unimplemented | yes |
| M6-PROGRESS.md complete | yes |

### Incomplete conditions (M6-E)

None of the incomplete triggers apply (no NOT-RUN required tests, no surviving critical mutations, no invented canonical behavior, no OAD silent close, no R-REG edit).

---

## 22. Final implementation status + next

```text
M6 IMPLEMENTATION = COMPLETE WITH DISCLOSED EVIDENCE LIMITATIONS
```

```text
NEXT = M6 IMPLEMENTATION REVIEW
```

**Do not perform M6 review in this operation.**

### Non-claims

```text
No formal proof of R-ACTOR-07 (U-35 open).
No production certification.
No M7 work.
No claim bare evaluate(Spawn) works without GlobalState.
No multi-process D06 harness.
No proptest randomized property engine.
```

### Final board

```text
M0–M4                      prior accepted
M5                         ACCEPTED WITH DISCLOSED EVIDENCE LIMITATIONS
M6 preflight               GREEN WITH DISCLOSED LIMITATIONS — IMPLEMENTATION AUTHORIZED
M6 implementation          COMPLETE WITH DISCLOSED EVIDENCE LIMITATIONS
M6 review                  NOT STARTED
R-REG                      184 × SPECIFIED
M7                         NOT STARTED
NEXT                       M6 IMPLEMENTATION REVIEW
```

---

*End of M6-PROGRESS (addendum-complete).*
