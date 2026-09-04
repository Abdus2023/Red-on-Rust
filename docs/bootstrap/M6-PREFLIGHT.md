# M6 Preflight — Authority Reconciliation & Concurrency-Surface Freeze

**Operation type:** M6 PREFLIGHT ONLY — no actor/scheduler implementation.  
**Final authorization:**

```text
M6 PREFLIGHT = GREEN WITH DISCLOSED LIMITATIONS — IMPLEMENTATION AUTHORIZED
```

```text
NEXT = M6 IMPLEMENTATION
```

Evidence labels: **FACT** | **DERIVED** | **DISCLOSED LIMITATION** | **AMBIGUOUS** | **PASS** | **PASS-DISCLOSED**

---

## 1. Repository identity

| Item | Observation | Class |
|---|---|---|
| Branch | `arena/01a06993-red-on-rust` | FACT |
| Git `HEAD` (preflight base) | `7e6eb441e5536d12f92dc79a7ca1c0e8764d7d61` — M5 review tip | FACT |
| M5 implementation | `f1785629d745da176b30de8e5dc5c7c9562701e1` — ancestor of HEAD | FACT |
| M5 review | `7e6eb44` | FACT |
| M5 preflight | `b64fb9a` | FACT |
| Working tree (pre this file) | clean on M5 tip | FACT |
| M5 code surface | Request CEK + effects + host/persistence; Spawn/Send/Receive still `UnsupportedInM2` | FACT |
| Canonical `final/*` | Present; R-ORDER-02 M6 row; R-ACTOR-01…10 SPECIFIED | FACT |
| R-REG | **184 × SPECIFIED**; transitions empty | FACT |
| Toolchain posture | `ror-stable` 1.88.0 | FACT |

### G-01 disposition

**PASS**.

**Rationale:** Branch, M5 implementation commit `f178562`, and M5 review commit `7e6eb44` match the mission starting point. No governance identity mismatch.

**Non-claim:** This preflight does not re-run the full M5 gate battery; it consumes M5 **ACCEPTED WITH DISCLOSED EVIDENCE LIMITATIONS** and the in-tree effect hinge as authoritative inputs.

---

## 2. Starting M5 state

| Item | State |
|---|---|
| M5 preflight | GREEN WITH DISCLOSED LIMITATIONS (`b64fb9a` per docs) |
| M5 implementation | ACCEPTED WITH DISCLOSED EVIDENCE LIMITATIONS (`f178562` per docs; code in tree) |
| M5 review | COMPLETE (`7e6eb44` per docs) |
| Hard hinge | `HostInvoked(E) ⇒ DurableIssued(E)` (GI-SEC-07 / R-DUR-01) — **authoritative; must not be bypassed by actors/scheduler** |
| R-REG | 184 × SPECIFIED |
| M6 / M7 | NOT STARTED |

Current CEK posture (FACT): `Expr::{Spawn,Send,Receive,Yield,Halt}` fault `UnsupportedInM2` — correct pre-M6.

---

## 3. Canonical authorities inspected

| Source | Role for M6 |
|---|---|
| `final/01` §09 Actors, §10 Scheduler, R-BUDGET-16, R-CORE-07/08, R-MARSHAL-*, R-ORDER-02 | Normative homes |
| `final/03` | R-ACTOR-01…10, R-BUDGET-16 rows — all **SPECIFIED** |
| `final/04` | M6 milestone row; SCHED-FIFO; SCHED-BLOCKED-NOT-SCHEDULED; M011–M013, M025, M033 |
| `final/05` | GI-DET-01…03; GI-SEC-07 (effect hinge unchanged) |
| `final/08` | Evidence ceiling 184 × SPECIFIED |
| `final/09` | OADs U-03, U-27, U-30, U-34, U-35 OPEN; U-01/U-07 RESOLVED |
| `dep/10-graph.json` / `mod/18-ownership-matrix.md` | MOD-06 ACTOR, MOD-07 SCHEDULER in `ror-runtime` |
| `reg/requirements.json` | 184 × SPECIFIED (no edit) |
| `docs/bootstrap/M5-{PREFLIGHT,PROGRESS,REVIEW}.md` | M5 boundary carry-forward |

**Authority hierarchy respected:** specification/registries > bootstrap. No bootstrap statement elevated over R-ACTOR-*.

---

## 4. M6 scope matrix

Canonical M6 name (**R-ORDER-02**, FACT):

```text
M6 Actors — spawn, mailbox FIFO, async send, blocking receive, scheduler pass
```

**final/04** M6 row (FACT):

```text
FIFO scheduler, FIFO mailbox, spawn isolation, send/receive, delegation, blocked/wakeup
```

| Surface | Classification | Canonical evidence |
|---|---|---|
| Actor isolation (env/heap/kont/mailbox/budget/caps) | **M6 REQUIRED** | R-ACTOR-01 |
| GlobalState `BTreeMap<ActorId, ActorState>`; global LogicalTime | **M6 REQUIRED** | R-ACTOR-02 |
| Monotonic ActorId (+ EffectId remains M5) | **M6 REQUIRED** | R-ACTOR-03 |
| FIFO runnable queue; at-most-once; 1 transition/turn; blocked/pending/terminal never scheduled | **M6 REQUIRED** | R-ACTOR-04; SCHED-FIFO; SCHED-BLOCKED-NOT-SCHEDULED |
| Spawn transactional (escrow, derive caps, isolate child, enqueue, log) | **M6 REQUIRED** | R-ACTOR-05 |
| Spawn default empty authority; explicit manifest only; Authority(child) ≺ parent | **M6 REQUIRED** | R-ACTOR-09 |
| Send async + marshal + FIFO enqueue + deterministic wakeup | **M6 REQUIRED** | R-ACTOR-06 |
| Receive dequeue or Block without fuel | **M6 REQUIRED** | R-ACTOR-06 |
| Mailbox FIFO | **M6 REQUIRED** | R-ACTOR-06; M013 |
| Mailbox admission / payload cost / footprint bound | **M6 REQUIRED** | R-ACTOR-10; M033 |
| No amplification / no teleportation (send path) | **M6 REQUIRED** | R-ACTOR-08; R-CORE-07; R-MARSHAL-01 |
| Deterministic concurrency theorem (operational form) | **M6 REQUIRED** | R-ACTOR-07; R-CORE-08 |
| Delegation channel (`Expr::Delegate` / envelope) for cap transfer | **M6 REQUIRED** (final/04 “delegation”) | R-MARSHAL-05; R-CORE-07 |
| CEK `Spawn` / `Send` / `Receive` evaluation | **M6 REQUIRED** | R-CALC-02 + R-ACTOR-05/06 |
| Pending actor status while effect issued (step 15) | **M6 REQUIRED** (thin multi-actor form of M5 step 15) | R-CORE-14 step 15; R-EFFECT-03 ownership MOD-07 |
| `QuiescenceReconcile` driver when `Deadlock ∧ ∃Pending` | **M6 REQUIRED** (driver transition; not full recovery engine) | R-BUDGET-16 |
| Yield / Halt full semantics | **M6 ALLOWED SUPPORT** if needed for scheduler tests; else **DEFERRED** if not required by R-ORDER-02 M6 row | R-CALC-02 constructors exist; M6 row does not name Yield/Halt |
| Full R-RECOV-08 host reconciliation engine | **M6 DEFERRED** (M7 / recovery track) | R-RECOV-*; M5 pattern: thin record only |
| WAL / snapshot / T0–T6 crash matrix | **M6 FORBIDDEN** | M7; R-ORDER-02 |
| New effect authorization / alternate HostExecutor path | **M6 FORBIDDEN** | R-CORE-14; GI-SEC-07; M5 freeze |
| New capability algebra redesign | **M6 FORBIDDEN** | M4 freeze; R-ACTOR-09 uses derive |
| LLM/planner | **M6 FORBIDDEN** | later |
| OAD close / R-REG promotion | **M6 FORBIDDEN** | governance |
| ActorId reuse/recycling policy | **AMBIGUOUS** — do **not** implement reuse | silence + R-ACTOR-03 monotonic only |
| Exact `ActorStatus` enum shape | **AMBIGUOUS** (U-27 OPEN) — implement **minimal** statuses required by R-ACTOR-04 (runnable/blocked/pending/terminal) without claiming U-27 closed | U-27; registry R-ACTOR-04 |
| `SchedulerTrace` / `HostTrace` formal parameters | **AMBIGUOUS** (U-35 OPEN) — operational FIFO+monotonic IDs still REQUIRED | U-35; GI-DET-01 note |
| Spawn `BudgetAllocationSpec` numeric policy details | **AMBIGUOUS** (U-03 OPEN) — R-ACTOR-09 bounds direction REQUIRED; exact splits may be thin/test-domain | U-03; R-ACTOR-09 |
| Full `MachineEvent` vocabulary | **AMBIGUOUS** (U-28 OPEN) — log minimum events named by R-ACTOR-05/06 (`ActorSpawned`, `MessageSent`) | U-28 |

---

## 5. M6 non-goals

| Non-goal | Why |
|---|---|
| Persistence recovery / WAL replay / snapshots / T0–T6 | M7 |
| Redesign M5 16-step / HostExecutor / issuance journal | M5 freeze; GI-SEC-07 |
| New Op/Target/Params ontology | U-21 OPEN; not M6 |
| Close OADs or promote R-REG | governance |
| Reference-model redesign beyond independent actor/scheduler mirror | R-REF-02 |
| Differential framework redesign | extend m5 pattern only |
| LLM/planner execution | out of milestone |
| Live OS host adapters | host track |
| Wall-clock / random / HashMap-order scheduling | R-ACTOR-03/04/07 |
| Ordinary capability-in-message | R-MARSHAL-01 / R-CORE-07 |
| Auto-cancel Pending on actor death without canonical rule | do not invent |
| ActorId reuse | not specified — **DO NOT IMPLEMENT REUSE** |

**M6 consumes M5 effect boundary; does not redesign it.**

---

## 6. Actor model

### Identity (R-ACTOR-03)

- `ActorId` via **global monotonic counter** `N' = N + 1` (same discipline as EffectId).
- **Forbidden** sources: addresses, PIDs, UUIDs, thread IDs, wall-clock.
- **Reuse:** not defined → **must not implement recycling**.
- Serialization of ActorId as data payload: R-CANON-05 exists; full machine-state codecs remain U-02 OPEN (in-memory GlobalState OK for M6).

### Isolation (R-ACTOR-01)

For `a ≠ b`: disjoint heaps, envs, continuations; isolated mailboxes, budgets, capability contexts. Spawn starts from `Environment::empty()` (no implicit inheritance).

### Global state (R-ACTOR-02)

- Actors in `BTreeMap<ActorId, ActorState>` (deterministic map order).
- Global `LogicalTime` advances on scheduler steps per δ_t table (R-BUDGET-16): pure/spawn/send/receive/blocked **0**; request issuance/receipt still **1** each when those transitions run.

### Spawn (R-ACTOR-05 + R-ACTOR-09)

Transactional order (canonical):

1. Validate + escrow budget (`BudgetAllocationSpec` — bounds per R-ACTOR-09; U-03 OPEN on policy detail).
2. Allocate child `ActorId`.
3. Derive child capabilities via `kernel.derive` only — **no wholesale clone**.
4. Construct isolated child state.
5. Enqueue child **deterministically** on runnable queue (FIFO back).
6. Log `ActorSpawned`.

Default child authority **empty**; only explicit manifest+constraint (compiler-checked direction; runtime must still enforce derive attenuation). Theorem: `Authority(child) ≺ Authority(parent)` for spawn-time grants.

### Status / scheduling eligibility (R-ACTOR-04)

Runnable queue must **never** select: Blocked, Pending (effect-wait), Halted/Faulted/terminal. Exact enum spelling = U-27 OPEN → minimal set sufficient to enforce the rule; disclose provisional labels (U-08).

---

## 7. Mailbox model

| Rule | Authority |
|---|---|
| **FIFO** per mailbox | R-ACTOR-06 |
| Ordering relation | **Per-actor mailbox FIFO** (not global message order; not “implementation-defined”) |
| Send | Async: marshal → enqueue → log `MessageSent` → wake Blocked target **exactly once** (deterministic) |
| Receive | Dequeue if non-empty; else **Blocked** suspension **without fuel** |
| Empty mailbox | Block (not busy-spin; not drop) |
| Ownership | Mailbox is part of actor isolation (R-ACTOR-01) |
| Admission | Recipient capacity from reserved `M`; deny → **sender** faults `ReservedCapacityExceeded` (R-ACTOR-10) |
| Send cost | Payload-proportional over **canonical length** (R-ACTOR-10) |
| Payload form | `MarshalledValue` checked-bytes direction (R-MARSHAL-05); U-30 OPEN — follow addendum “checked bytes”, not raw `Value` in mailbox storage |
| Cap in ordinary message | **Rejected** (R-MARSHAL-01 recursive `contains_capability`) |
| Cap transfer | **Only** delegation envelope path (R-MARSHAL-05), not ordinary Send |

**Do not** infer stronger ordering (global total order, per-sender-pair) than per-mailbox FIFO.

---

## 8. Scheduler model

| Rule | Authority |
|---|---|
| Structure | `RunnableQueue` **FIFO** | R-ACTOR-04 |
| Membership | **At-most-once** (no duplicate entries) | R-ACTOR-04; M012 |
| Selection | Head of FIFO queue | R-ACTOR-04; SCHED-FIFO |
| Quantum | **1 transition per turn** (registry R-ACTOR-04 short text; verification starvation test context) | R-ACTOR-04 |
| Ineligible | Blocked / Pending / terminal never scheduled | SCHED-BLOCKED-NOT-SCHEDULED; M011 |
| Wakeup | Enqueue at **back** (MOD-18 cross-ref; R-ACTOR-06 deterministic wake once) | R-ACTOR-06 |
| Trust | Scheduler is **TCB / trusted semantic machinery** (R-TRUST-02) but **not** an authority issuer | R-TRUST-02; §16 below |
| Nondeterminism forbidden | No wall-clock, random, thread, HashMap iteration for selection | R-ACTOR-03/04/07 |

**Do not** use Rust `HashMap` iteration for actor selection. Prefer `BTreeMap` / explicit FIFO deque.

---

## 9. GlobalStep model

Canonical text uses `GlobalStep::Deadlock` inside **R-BUDGET-16** (not a full enum freeze in §10 body).

| Concept | Canonical meaning for M6 |
|---|---|
| Scheduler turn / step | Select one eligible actor; execute **one** machine transition; apply that transition’s `δ_t` (no extra turn charge) |
| `GlobalStep::Deadlock` | Stable state: no runnable actor (all blocked/pending/terminal as applicable) |
| `Deadlock ∧ ∃Pending` | **Not** self-healing inside Deadlock; triggers driver transition **`QuiescenceReconcile`** |
| `QuiescenceReconcile` | `δ_t = 0`, `ΔD = 0`, no W check, **no budget mutation**; each Pending → record **Indeterminate** + bind to R-RECOV-08 protocol (**do not re-execute**; full reconcile engine may remain thin/M7) |
| `Deadlock` without Pending | **No** reconciliation transition |
| Pending vs Deadlock | **Pending(E) ≠ Deadlock**; Pending **survives** observing Deadlock until QuiescenceReconcile |

M6 MUST **consume** this freeze — **not redesign** timers/clocks/per-effect counters.

---

## 10. Determinism model

| Rule | Source |
|---|---|
| `InitialState + SchedulerTrace + HostTrace ⇒ UniqueMachineTrace` | R-CORE-08 / R-ACTOR-07 |
| Operational pillars: FIFO scheduler, monotonic IDs, deterministic CEK | R-ACTOR-07 body |
| Theorem parameter definitions incomplete | **U-35 OPEN** — DISCLOSED; still implement operational pillars |
| Global actor map ordered | `BTreeMap` (R-ACTOR-02) |
| Mailbox FIFO | R-ACTOR-06 |
| Logical time only | R-CAP-09; R-BUDGET-16 |
| No random / wall-clock / thread scheduling in semantics | R-ACTOR-03 |

Forbidden unless explicitly authorized: wall-clock scheduling, random decisions, unordered iteration affecting semantics, OS-thread interleaving as semantic input.

---

## 11. Pending / Deadlock / Quiescence model

**Frozen distinctions (R-BUDGET-16; U-01/U-07 RESOLVED):**

```text
Pending(E)  ≠  Deadlock  ≠  QuiescenceReconcile
```

| Rule | M6 duty |
|---|---|
| Actor waiting on issued effect | Status **Pending** (or equivalent); **not** scheduled (R-ACTOR-04) |
| `Pending(E)` across Deadlock observation | **Survives** until QuiescenceReconcile |
| `Deadlock ∧ ∃Pending` | Driver `QuiescenceReconcile`: δ_t=0, ΔD=0, no budget mutation; pendings → Indeterminate + R-RECOV-08 binding |
| Host still only after Issued | GI-SEC-07 unchanged when effect path runs |
| Full host reconciliation outcomes | Thin: may record Indeterminate; **full** R-RECOV-08 admission table execution can lag as DISCLOSED (not silent NotExecuted) |

**Conflict with this freeze → BLOCK-CANONICAL** (none found for authorizing M6 scope).

---

## 12. Termination model

| Topic | Canonical stance | M6 rule |
|---|---|---|
| Terminal statuses never scheduled | R-ACTOR-04 | REQUIRED |
| Exact Halt/Faulted/Terminated vocabulary | U-27/U-08 OPEN | Provisional labels OK; disclose |
| Messages to terminated actors | **Not fully spelled** in R-ACTOR-06 body | **AMBIGUOUS** — do not invent drop/undeliverable policy; STOP if needed mid-impl or keep messages only to live actors in tests until authority found |
| Pending owned by terminated actor | Not fully spelled | **AMBIGUOUS** — must **not** auto-resolve to NotExecuted (R-DUR-04 / R-RECOV-08 direction); prefer keep Indeterminate / explicit fault |
| Global quiescence vs per-actor halt | Distinct | Deadlock is global; actor terminal is local |

**DO NOT invent automatic cancellation of Pending on death.**

---

## 13. Capability / message boundary

```text
OrdinaryMarshal(Value::Capability) ⇒ Rejected          # R-CORE-07
marshal_value(v) faults if contains_capability(v)       # R-MARSHAL-01 recursive
Authority crosses actors only via explicit delegation   # R-MARSHAL-05
```

| May appear in ordinary messages? | Verdict |
|---|---|
| Ordinary data Values (unit/bool/int/string/bytes/list/tuple without caps) | YES (after marshal) |
| `ActorId` as data | YES if treated as data id (R-CANON-05); not authority |
| `EffectId` as data | YES as data id; not host power |
| Raw `Capability` / nested caps | **NO** |
| `FunctionValue` / closures | Treat as non-ordinary for marshal until proven data-safe — **prefer reject** if contains env caps (DERIVED under R-MARSHAL-01 spirit); if unspecified, **AMBIGUOUS** — default **reject Function in messages** for M6 safety unless authority found |
| Delegation envelope | YES via **Delegate** path only, with receive-side kernel revalidation |

**New authority channel via mailbox = BLOCK-SECURITY.**

Revocation/expiration vs **queued** messages: not fully frozen for “message already enqueued” — **AMBIGUOUS**. Safe M6 posture: revalidate delegation envelopes at receive (R-MARSHAL-05 already requires revalidation); ordinary data unchanged.

---

## 14. M5 effect-boundary preservation

### Hard rule (unchanged)

```text
HostInvoked(E) ⇒ DurableIssued(E)
```

### Actor → effect path (REQUIRED shape)

| Question | Answer (canonical) |
|---|---|
| Who creates Request? | Actor CEK evaluates `Expr::Request` (same AST) |
| Who evaluates? | MOD-05 CEK inside actor turn |
| Who owns EffectId? | Global monotonic allocator (R-EFFECT-03 / R-ACTOR-03) — **not** untrusted Expr |
| Who authorizes? | Kernel Valid + authorize (M4/M5) |
| Who reserves budget? | Actor/runtime budget gates (M5 thin → multi-actor partition R-ACTOR-08) |
| Who persists Prepared/Issued? | `ror-persistence` issuance API (M5) via runtime |
| Who invokes HostExecutor? | Runtime effect pipeline **only after** Issued+sync |
| Who receives receipt? | Runtime validates; resumes **that actor’s** continuation |
| Completion status | Pending → runnable/resume per CEK; not scheduler host call |

### Forbidden M6 shapes

```text
Actor → HostExecutor
Scheduler → HostExecutor
Mailbox → HostExecutor
Message → Effect issuance
Spawn → HostExecutor
```

Any such path → **BLOCK-SECURITY**.

### Interface freeze

- Reuse `run_effect_pipeline` / `EffectServices` / `IssuanceJournal` / `HostExecutor`.
- **Do not** duplicate authorize or second journal.
- Step 15 Pending becomes real multi-actor status (was thin single-actor in M5).

---

## 15. Dependency reconciliation

| Edge | Classification | Evidence |
|---|---|---|
| runtime → core | REQUIRED | mod/18 MOD-06/07 |
| runtime → kernel | REQUIRED | spawn/delegation derive; authorize |
| runtime → persistence | REQUIRED | R-TRUST-05; effect step 14 |
| host → runtime | REQUIRED | unchanged M5 |
| persistence → core | REQUIRED | unchanged |
| reference → core only | REQUIRED independence | R-REF-02 |
| reference ↛ runtime/kernel/host/persistence | FORBIDDEN absent | keep |
| differential → runtime/reference/kernel/(host)/(persistence) | ALLOWED test harness | mod/15 |
| **New crates for actors** | **NOT REQUIRED** | Actors live **in** `ror-runtime` (mod/18) |
| runtime → host | FORBIDDEN | do not add |

**No FORBIDDEN required edge proposed.** HostExecutor trait packaging remains M5 disclosure (L-M5-04).

**G-16 Dependency:** PASS.

---

## 16. Reference-model requirements

Independent `ror-reference` MUST gain (when M6 implements) a **separately authored** mirror of:

- ActorId allocation  
- Actor state / isolation  
- Mailbox FIFO  
- Runnable FIFO scheduler  
- Spawn/Send/Receive observations  
- Pending / Deadlock / QuiescenceReconcile observations (thin)  
- Effect handoff observations **without** calling production `run_effect_pipeline`

Shared `ror-core` types OK. Shared admissibility helper remains M4 disclosure.

Production MUST NOT import reference transitions.

**G-13 Reference independence (readiness):** PASS (structure already holds; M6 code N/YI).

---

## 17. Differential surface (minimum)

Black-box observations (semantic, not Rust internals):

| Observation | Notes |
|---|---|
| ActorId sequence under fixed spawn order | monotonic |
| Runnable selection order | FIFO |
| Mailbox FIFO content order | enqueue/dequeue |
| Send → wakeup exactly once | blocked target |
| Receive block on empty | status |
| Spawn isolation | child env empty; authority ≺ |
| Cap-in-Send reject | marshal fault |
| Scheduler never selects blocked/pending/terminal | |
| GlobalStep Deadlock detection | |
| Deadlock+Pending → QuiescenceReconcile side effects | Indeterminate record; δ_t=0 |
| Request from actor still Issued-before-host | hinge |
| Termination not scheduled | |

Normalize only non-semantic representation. Do not hide FIFO bugs via sort-normalization of mailboxes.

---

## 18. Test requirements

| Class | Targets (canonical tags / mutations) |
|---|---|
| UNIT | ActorId monotonic; mailbox FIFO; queue at-most-once; block-without-fuel |
| PROPERTY | Isolation heaps/envs; budget conservation spawn/send; Authority(child)≺parent |
| DIFFERENTIAL | Track D surface above; P↔R |
| MUTATION | M011 schedule blocked; M012 duplicate runnable; M013 break FIFO; M025 unattenuated spawn; M033 enqueue without capacity |
| DETERMINISM | Same initial+traces → same actor/mailbox/order observations |
| SECURITY | Cap-in-message reject; no host-before-Issued from actor path; no scheduler authority mint |
| REGRESSION | M1–M5 suites remain green |

**Do not claim tests exist until M6 implementation writes them.** This section is the **required surface**, not evidence of passage.

---

## 19. Mutation targets

| Mutation | Class |
|---|---|
| Reverse runnable order / non-FIFO select | **REQUIRED M6 MUTATION** (SCHED-FIFO) |
| Duplicate runnable membership | **REQUIRED** (M012) |
| Schedule blocked/pending/terminal | **REQUIRED** (M011) |
| Break mailbox FIFO / drop / duplicate message | **REQUIRED** (M013) |
| Reuse ActorId | **REQUIRED** negative |
| Spawn clones parent caps | **REQUIRED** (M025) |
| Enqueue without capacity check | **REQUIRED** (M033) |
| Host before Issued via actor/scheduler path | **REQUIRED** (GI-SEC-07) |
| Cap through ordinary Send | **REQUIRED** (R-MARSHAL-01) |
| Mutate budgets on QuiescenceReconcile | **REQUIRED** (R-BUDGET-16) |
| Convert Pending → NotExecuted on Deadlock | **REQUIRED** negative (R-DUR-04/R-RECOV-08) |
| Random/wall-clock schedule | **REQUIRED** negative |
| Full crash T0–T6 | **ALLOWED FUTURE** (M7) |
| Live OS host | **NOT CANONICALLY JUSTIFIED** in M6 |

Preflight does **not** run the battery.

---

## 20. Gate board

| Gate | Status | Notes |
|---|---|---|
| G-01 Repository Identity | **PASS** | Branch + `f178562` + `7e6eb44` verified |
| G-02 Canonical Authority Alignment | **PASS** | R-ORDER-02 M6 + R-ACTOR-* + R-BUDGET-16 located |
| G-03 M6 Scope | **PASS-DISCLOSED** | Frozen REQUIRED set; Yield/Halt optional; recovery thin |
| G-04 Actor Identity | **PASS-DISCLOSED** | Monotonic required; reuse forbidden; U-27 status shape open |
| G-05 Mailbox Semantics | **PASS-DISCLOSED** | FIFO+admission frozen; U-30 storage form follow R-MARSHAL-05 bytes |
| G-06 Scheduler / GlobalStep | **PASS-DISCLOSED** | FIFO+1-turn+eligibility frozen; U-35 theorem params open |
| G-07 Determinism | **PASS-DISCLOSED** | Operational rules frozen; U-35 assurance gap |
| G-08 Pending / Deadlock / Quiescence | **PASS** | R-BUDGET-16 freeze consumed |
| G-09 Actor Termination | **PASS-DISCLOSED** | Terminal not scheduled frozen; message-to-dead / pending-on-death AMBIGUOUS — no invention authorized |
| G-10 Capability / Message Boundary | **PASS** | R-MARSHAL-01/05; R-CORE-07 |
| G-11 M5 Effect Boundary | **PASS** | Hinge intact; no alternate host/persist path authorized |
| G-12 Scheduler Authority Boundary | **PASS** | Trusted machinery ≠ Cap/Host issuer |
| G-13 Reference Independence | **PASS** | Structure ready; impl N/YI |
| G-14 Differential Surface | **PASS** | Minimum surface defined |
| G-15 Mutation Surface | **PASS** | Required mutations listed |
| G-16 Dependency Authority | **PASS** | No forbidden edges |
| G-17 R-REG Evidence Ceiling | **PASS** | 184 × SPECIFIED; no edits |
| G-18 OAD Integrity | **PASS** | OPEN OADs recorded; none closed |
| G-19 Regression Baseline | **PASS-DISCLOSED** | M5 accepted tip; full cargo re-confirm required at M6 impl Phase A |
| G-20 Evidence Integrity | **PASS-DISCLOSED** | Preflight evidence; not implementation proof |

**No BLOCK-\*. No FAIL-\*.**

**Implementation-readiness field:** M6 code **NOT-YET-IMPLEMENTED** (expected).

---

## 21. Evidence index (selected)

| ID | Gate | Kind | Result | Security | Limitation |
|---|---|---|---|---|---|
| E-M6-01 | G-01 | MECHANICAL | PASS | NONE | NONE |
| E-M6-02 | G-02 | OTHER | PASS | HIGH | NONE |
| E-M6-03 | G-03 | OTHER | PASS | HIGH | Thin recovery |
| E-M6-04 | G-04 | OTHER | PASS | HIGH | U-27; no id reuse |
| E-M6-05 | G-05 | OTHER | PASS | CRITICAL | U-30 |
| E-M6-06 | G-06 | OTHER | PASS | CRITICAL | U-35 |
| E-M6-07 | G-08 | OTHER | PASS | CRITICAL | Thin R-RECOV-08 depth |
| E-M6-08 | G-10 | OTHER | PASS | CRITICAL | NONE |
| E-M6-09 | G-11 | IMPLEMENTATION | PASS | CRITICAL | M5 hinge in-tree |
| E-M6-10 | G-16 | OTHER | PASS | HIGH | NONE |
| E-M6-11 | G-17 | MECHANICAL | PASS | NONE | NONE |
| E-M6-12 | G-18 | OTHER | PASS | LOW | OPEN OADs listed |

### Evidence Record: E-M6-01

- **Gate:** G-01  
- **Canonical authority:** Process identity / mission  
- **Canonical rule:** Start from accepted M5 on session branch  
- **Observed repository state:** HEAD `7e6eb44`; `f178562` ancestor; branch `arena/01a06993-red-on-rust`  
- **Relevant implementation:** committed M5 tree at `f178562`…`7e6eb44`  
- **Relevant test:** `git rev-parse` / `git log` / `git merge-base --is-ancestor f178562 HEAD`  
- **Evidence kind:** MECHANICAL  
- **Result:** PASS  
- **Limitation:** NONE  
- **Security relevance:** NONE  
- **Reviewer conclusion:** Repository identity matches authorized M5 tip.
### Evidence Record: E-M6-09

- **Gate:** G-11  
- **Canonical authority:** GI-SEC-07; R-DUR-01; M5-REVIEW  
- **Canonical rule:** Host only after durable Issued  
- **Observed repository state:** `run_effect_pipeline` still sole production host path; Spawn/Send/Receive unsupported  
- **Relevant implementation:** `crates/ror-runtime/src/effects.rs`  
- **Relevant test:** prior M5 suites (not re-run as M6 gate pass claim)  
- **Evidence kind:** IMPLEMENTATION  
- **Result:** PASS  
- **Limitation:** Full workspace green reconfirm at M6 impl start  
- **Security relevance:** CRITICAL  
- **Reviewer conclusion:** No pre-existing actor bypass; M6 must not add one.

---

## 22. Disclosed limitations

| ID | Limitation |
|---|---|
| U-03 | Spawn budget allocation policy detail OPEN — implement R-ACTOR-09 bounds thinly |
| U-27 | ActorStatus shape OPEN — minimal eligibility set only |
| U-28 | MachineEvent names OPEN — minimum spawn/send logs |
| U-30 | MarshalledValue payload OPEN — follow R-MARSHAL-05 checked-bytes direction |
| U-34 | run_state/members/scheduler struct OPEN — in-memory structures provisional |
| U-35 | Determinism theorem parameters OPEN — operational FIFO+IDs still required |
| U-02/U-08/U-09 | Machine codecs / faults / values OPEN — carry forward |
| L-M6-TERM | Message-to-terminated / pending-on-death not fully frozen — no invention |
| L-M6-RECOV | QuiescenceReconcile records Indeterminate; full R-RECOV-08 host reconcile may remain thin |
| L-M6-DELEG-AST | `Expr::Delegate` from R-MARSHAL-05 addendum vs R-CALC-02 historical list — treat Delegate as **addendum-authorized** constructor for M6 delegation |
| M5 carry | CapRef public ctor; HostExecutor trait packaging; thin budget; BE effect bytes |

---

## 23. OAD impact

| OAD | Status | M6 effect |
|---|---|---|
| U-01, U-07, U-36, U-39…U-44 | RESOLVED | Consumed (δ_t, quiescence, request pipeline) |
| U-03 | OPEN | Thin spawn budget bounds; no silent policy close |
| U-27 | OPEN | Minimal ActorStatus |
| U-30 | OPEN | Checked-bytes mailbox direction |
| U-34 | OPEN | Provisional global structs |
| U-35 | OPEN | Operational determinism without claiming theorem falsifiability closed |
| U-02/U-08/U-09/U-21/U-31 | OPEN | Carry M5 disclosures |

**No OAD closed.**

---

## 24. R-REG impact

```text
184 × SPECIFIED
No edits to reg/requirements.json or status-transitions.json
Preflight ≠ IMPLEMENTED evidence
```

---

## 25. Final authorization decision

### Stop policy

No `BLOCK-CANONICAL`, `BLOCK-SECURITY`, `BLOCK-DEPENDENCY`, `BLOCK-INDEPENDENCE`, `BLOCK-SCOPE`, `BLOCK-GOVERNANCE`, or `BLOCK-REGRESSION` on the **authority reconciliation** of M6 scope.

### Authorization criteria checklist

| Criterion | Met? |
|---|---|
| No BLOCK-* | yes |
| No unresolved contradiction blocking scope freeze | yes (remaining items AMBIGUOUS with “do not invent” rules) |
| No unresolved security boundary | yes — hinge + marshal frozen |
| No forbidden dependency | yes |
| Reference independence structure OK | yes |
| M5 effect boundary intact | yes |
| M6 scope frozen sufficiently | yes |
| Test/differential/mutation surfaces identified | yes |
| R-REG unchanged | yes |
| OAD status correct | yes |
| Repository identity (f178562 / 7e6eb44) | yes |
```text
M6 PREFLIGHT = GREEN WITH DISCLOSED LIMITATIONS — IMPLEMENTATION AUTHORIZED
```

```text
NEXT = M6 IMPLEMENTATION
```

### Frozen implementation scope (for the next sprint)

**In:**

1. GlobalState + monotonic ActorId + BTreeMap actors  
2. FIFO runnable queue (at-most-once, 1 transition/turn, eligibility rules)  
3. Actor-local CEK integration for Spawn / Send / Receive  
4. FIFO mailboxes + R-ACTOR-10 admission  
5. Spawn transaction R-ACTOR-05/09 (derive-only caps; default empty)  
6. Send/Receive R-ACTOR-06 + marshal reject caps  
7. Delegation path R-MARSHAL-05 (addendum Expr::Delegate / envelope) as required by final/04 “delegation”  
8. Pending status + scheduler exclusion; QuiescenceReconcile driver per R-BUDGET-16 (thin Indeterminate recording)  
9. All effect issuance still through M5 pipeline only  
10. Independent reference actor/scheduler observations + differential m6 + required mutations  
11. M1–M5 regression green  

**Out:**

- M7 recovery/WAL/snapshots/T0–T6  
- Host/effect/capability algebra redesign  
- ActorId reuse; invented termination delivery policies  
- OAD closure; R-REG promotion  
- Wall-clock/random scheduling  

---

## 26. Explicit non-claims

```text
M6 is not implemented.
No M6 semantic verification is claimed.
No formal proof is claimed.
No production certification is claimed.
No R-REG status promotion occurred.
No OAD closure occurred.
M5 implementation identity f178562 was not amended by this preflight.
M5 security hinge remains authoritative.
```

---

## 27. Final state board

```text
M0                         GREEN (historical)
M1–M4                      ACCEPTED WITH DISCLOSED EVIDENCE LIMITATIONS (prior)
M5 preflight               GREEN WITH DISCLOSED LIMITATIONS
M5 implementation          ACCEPTED WITH DISCLOSED EVIDENCE LIMITATIONS
M5 semantic verification   NOT CLAIMED
M6 preflight               GREEN WITH DISCLOSED LIMITATIONS — IMPLEMENTATION AUTHORIZED
M6 implementation          NOT STARTED
R-REG                      184 × SPECIFIED
M7                         NOT STARTED
NEXT                       M6 IMPLEMENTATION
```

---

*End of M6 PREFLIGHT. Do not begin M6 implementation in this operation.*
