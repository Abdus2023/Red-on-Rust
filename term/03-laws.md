<!-- GENERATED FILE — DO NOT EDIT BY HAND. -->
<!-- Source of truth: `term/_terms.py`.  Regenerate: `python3 term/_dict.py --write`. -->
<!-- Every line citation below is re-grepped against `Red-on-Rust.md` by `python3 term/_check.py`. -->

# 03 — Non-Conflation Laws

31 laws. A law states that two canonical terms must never be used for each other. The first nine are mandated by the request's special rule about not silently renaming an API, type, mathematical symbol or protocol field; the rest are mandated by the request's list of required distinctions or by a named part of the frozen specification. A law is not a rename: both terms keep their frozen names, and the law says which one a given sentence must use.

| ID | Law | Mandated by | Enforced by |
|---|---|---|---|
| [N-01](#n-01) | `Block ≠ ExecutablePlan` | request §Special rule; frozen source L3834, L41440-41452 | R-COMPILE-01, R-COMPILE-05, R-ARCH-03, R-ORDER-03 gate property 1 |
| [N-02](#n-02) | `PlanProposal ≠ ExecutablePlan` | request §Special rule | R-PLANNER-01, R-PLANNER-02, R-CORE-01, R-COMPILE-02 |
| [N-03](#n-03) | `CapRef ≠ Authority` | request §Special rule; frozen source L7323, L41052 | R-CAP-01, R-CAP-05, R-KERN-03, R-TRUST-03, R-ORDER-03 gate property 2 |
| [N-04](#n-04) | `EffectRequest ≠ EffectIssued` | request §Special rule; frozen source L23726-23772 | R-DUR-01, R-DUR-02, R-EFFECT-03 step 14, R-CORE-06 |
| [N-05](#n-05) | `EffectIssued ≠ EffectCompleted` | request §Special rule; frozen source L26576, L35140 | R-DUR-03, R-DUR-04, R-RECOV-02, R-CORE-09, RECOVERY-ISSUED-INDETERMINATE |
| [N-06](#n-06) | `Specification ≠ Implementation` | request §Special rule | R-SCOPE-02, R-CLAIM-01, spec/00 §2 ladder |
| [N-07](#n-07) | `Implementation ≠ Verification` | request §Special rule | R-SCOPE-04, R-REF-02, R-CLAIM-01, R-TEST-09 |
| [N-08](#n-08) | `Verification ≠ Proof` | request §Special rule; frozen source L28263, L37444-37452 | R-CLAIM-01, R-CLAIM-03, spec/00 §2 `PROVEN` rung |
| [N-09](#n-09) | `LLM output ≠ Authority` | request §Special rule; frozen source L27271-27285 | R-CORE-01, R-PLANNER-01, R-PLANNER-02, R-TRUST-01, R-TRUST-02 |
| [N-10](#n-10) | `ParsedBlock ≠ ValidatedPlan` | request §Required distinctions | R-COMPILE-02, R-COMPILE-03 |
| [N-11](#n-11) | `ValidatedPlan ≠ CapabilityCheckedPlan` | request §Required distinctions | R-COMPILE-03, R-CAP-04 |
| [N-12](#n-12) | `CapabilityCheckedPlan ≠ ExecutablePlan` | request §Required distinctions | R-COMPILE-03, R-COMPILE-05, R-BUDGET-01 |
| [N-13](#n-13) | `Effect ≠ EffectRequest` | request §Required distinctions | R-CALC-04, R-EFFECT-01, R-EFFECT-06 |
| [N-14](#n-14) | `EffectIssued ≠ EffectReceipt` | request §Required distinctions | R-EFFECT-06, R-DUR-03, R-HOST-03, EFFECT-RECEIPT-DIGEST-VALIDATION |
| [N-15](#n-15) | `ActorStatus ≠ RunState` | request §Required distinctions; C-18 | R-ACTOR-02, R-ACTOR-04, SCHED-BLOCKED-NOT-SCHEDULED |
| [N-16](#n-16) | `Budget ≠ Consumable` | request §Required distinctions | R-BUDGET-01, R-CORE-05, BUDGET-CONSUMPTION-CONSERVATION |
| [N-17](#n-17) | `Consumable ≠ Reserved` | request §Required distinctions; C-07 | R-BUDGET-03, R-BUDGET-04, BUDGET-ESCROW-CONSERVATION |
| [N-18](#n-18) | `LogicalTime ≠ Deadline` | request §Required distinctions | R-BUDGET-06, R-CAP-09, R-CORE-08 |
| [N-19](#n-19) | `WAL ≠ EventLog` | request §Required distinctions; U-16 | R-PERSIST-01, R-PERSIST-03, R-DUR-01, WAL-GAP-REJECT |
| [N-20](#n-20) | `WAL ≠ EffectJournal` as STRUCTURES, but the journal is not a separate durable file either: in the frozen 15B model the journal's records ARE `WalRecord` kinds | request §Required distinctions; C-25 | R-DUR-02, R-DUR-03, R-PERSIST-03 |
| [N-21](#n-21) | `Snapshot ≠ WAL` | request §Required distinctions | R-PERSIST-04, R-PERSIST-05, R-RECOV-01, R-RECOV-03, SNAPSHOT-COMMIT-INTEGRITY |
| [N-22](#n-22) | `Observation (planner-facing) ≠ Observation (differential)` | request §Required distinctions; X-06 | R-PLANNER-01, R-REF-05, R-TEST-03 |
| [N-23](#n-23) | `EffectId ≠ EffectDigest` | request §Required distinctions | R-CALC-04, R-DUR-03, R-EFFECT-06, R-HOST-03 |
| [N-24](#n-24) | `Indeterminate ≠ NotExecuted` | request §Required distinctions | R-DUR-04, R-RECOV-02, R-RECOV-07, R-CORE-09, R-CLAIM-02 |
| [N-25](#n-25) | `HostPolicy ≠ Authority` | request §Required distinctions | R-HOST-01, R-CORE-02, R-TRUST-01 |
| [N-26](#n-26) | `ReplayHost ≠ LiveHost` | request §Required distinctions; C-22 | R-HOST-02, R-HOST-03, R-HOST-04, R-CORE-08 |
| [N-27](#n-27) | `ReferenceModel ≠ Production implementation` | request §Required distinctions | R-SCOPE-04, R-REF-01, R-REF-02, R-REF-04 |
| [N-28](#n-28) | `Constraint ≠ Authority` | request §Required distinctions | R-CAP-02, R-CAP-04, R-CORE-04, CAP-DERIVE-NO-AMPLIFICATION |
| [N-29](#n-29) | `delegate ≠ attenuate ≠ derive` | spec/05 §1 (derive/attenuate/delegate row) | R-MARSHAL-01, R-MARSHAL-02, R-CAP-04, R-CORE-07 |
| [N-30](#n-30) | `Mailbox ≠ RunnableQueue` | request §Required distinctions | R-ACTOR-03, R-ACTOR-04, R-ACTOR-07, SCHED-FIFO |
| [N-31](#n-31) | `Frozen ≠ Verified` | spec/05 §6.9-6.10; request §Special rule (by implication) | R-SCOPE-02, R-SCOPE-03, R-TEST-09 |

---

## N-01

**`Block ≠ ExecutablePlan`. Untrusted homoiconic data is never machine input; the transition requires the whole privileged pipeline and no raw `Block` has a path into `step()`.**

- **Left term:** T-01 `Block`
- **Right term:** T-06 `ExecutablePlan`
- **Mandated by:** request §Special rule; frozen source L3834, L41440-41452
- **Enforced by:** R-COMPILE-01, R-COMPILE-05, R-ARCH-03, R-ORDER-03 gate property 1

### Evidence

- `Red-on-Rust.md` L41440 — R-COMPILE-01 obligation text
- `Red-on-Rust.md` L3834 — `Block ≠ ExecutablePlan` stated
- `Red-on-Rust.md` L9115 — A raw `Block` should have no path into `step()`
- `Red-on-Rust.md` L869 — `ExecutablePlan` carries `_sealed: Sealed`, private to `mod compiler`

### Consequence of conflating them

Conflation makes the language surface a security boundary. It is the first of the four boxed properties of the first security gate (§36), and mutation M001-M003 target it.

## N-02

**`PlanProposal ≠ ExecutablePlan`. A proposal is untrusted data produced by a probabilistic generator; an executable plan is a validated, sealed compiler artifact. No proposal is a plan, and no plan is a proposal.**

- **Left term:** T-02 `PlanProposal`
- **Right term:** T-06 `ExecutablePlan`
- **Mandated by:** request §Special rule
- **Enforced by:** R-PLANNER-01, R-PLANNER-02, R-CORE-01, R-COMPILE-02

### Evidence

- `Red-on-Rust.md` L27175 — `PlanProposal { observation_sequence, block, planner_metadata }` — it *contains* a `Block`, it is not a plan
- `Red-on-Rust.md` L27271 — the planner cannot bypass compilation
- `Red-on-Rust.md` L41440 — `Block ≠ ExecutablePlan`, and a proposal's payload is a `Block`

### Consequence of conflating them

Conflation lets the LLM's output reach the machine without compilation, defeating R-CORE-01 (`LLMOutput ∧ UntrustedInput ↛ ExternalEffect`).

## N-03

**`CapRef ≠ Authority`. A `CapRef` is an opaque generational REFERENCE (`{index, generation}`) that the evaluator may hold and pass; `Authority` is the kernel-private grant set `A = {(o, ⟨S,Q,R,T⟩)}` it denotes. The bridge is a function, not an identity: `κ(c) = Authority(c) = A_c`. The evaluator can never inspect authority internals.**

- **Left term:** T-09 `CapRef`
- **Right term:** T-10 `Authority`
- **Mandated by:** request §Special rule; frozen source L7323, L41052
- **Enforced by:** R-CAP-01, R-CAP-05, R-KERN-03, R-TRUST-03, R-ORDER-03 gate property 2

### Evidence

- `Red-on-Rust.md` L7323 — `AuthOK(c,E,t) ⇔ Valid(c,t) ∧ Authorized(Authority(c),E,t)` — the authority is obtained FROM the reference
- `Red-on-Rust.md` L9131 — `CapRef { index: u32, generation: u32 }`, fields private
- `Red-on-Rust.md` L6375 — `A_o = ⟨S,Q,R,T⟩` — a grant set, not a reference
- `Red-on-Rust.md` L39373 — `pub(crate) struct AuthorityNode { ... }` must remain inaccessible
- `Red-on-Rust.md` L41054 — gate property 2: `CapRef ⇏ AuthorityInspection`

### Consequence of conflating them

Conflation makes authority inspectable from the evaluator, which is exactly the 'no hidden authority' violation R-TRUST-03 prohibits, and it makes attenuation and revocation unimplementable as algebra.

## N-04

**`EffectRequest ≠ EffectIssued`. A request is a TRANSIENT in-memory message `{id, effect}`; an issuance is a DURABLE commitment fact. The existence of a request object is never evidence that an effect was issued: 'an effect is not considered merely issued because an in-memory object exists.'**

- **Left term:** T-17 `EffectRequest`
- **Right term:** T-18 `EffectIssued`
- **Mandated by:** request §Special rule; frozen source L23726-23772
- **Enforced by:** R-DUR-01, R-DUR-02, R-EFFECT-03 step 14, R-CORE-06

### Evidence

- `Red-on-Rust.md` L23758 — `EffectRequest` — comment: 'Transient message to the host adapter'
- `Red-on-Rust.md` L23765 — `EffectIssued` — comment: 'Durable, deterministic fact of commitment'
- `Red-on-Rust.md` L38050 — durable issuance precedes host invocation
- `Red-on-Rust.md` L42082 — `HostInvoked(E) ⇒ DurableIssued(E)`

### Consequence of conflating them

Conflation permits host invocation before durability, the exact defect `EFFECT-ISSUE-DURABLE-BEFORE-HOST` and crash point T2 exist to catch.

## N-05

**`EffectIssued ≠ EffectCompleted`. Issuance commits the machine to an effect; completion records the host's result. `Completed(E) ⇒ Issued(E)`, never the converse, and `Issued(E) ∧ ¬Completed(E)` is `Indeterminate` — NOT `NotExecuted`. A missing completion record is not evidence of non-execution.**

- **Left term:** T-18 `EffectIssued`
- **Right term:** T-19 `EffectReceipt`
- **Mandated by:** request §Special rule; frozen source L26576, L35140
- **Enforced by:** R-DUR-03, R-DUR-04, R-RECOV-02, R-CORE-09, RECOVERY-ISSUED-INDETERMINATE

### Evidence

- `Red-on-Rust.md` L35140 — `Completed(E) ⇒ Issued(E)`
- `Red-on-Rust.md` L26576 — `Issued(E) ∧ ¬Completed(E)` — the indeterminate classification
- `Red-on-Rust.md` L38232 — crash classification: issued-but-not-completed ⇒ indeterminate
- `Red-on-Rust.md` L42100 — never infer NotExecuted from a missing completion record

### Consequence of conflating them

Conflation causes an indeterminate effect's escrow to be released (mutation M012) and turns a possibly-executed external effect into a silently discarded one — a double-execution or lost-effect hazard.

## N-06

**`Specification ≠ Implementation`. Frozen requirement text describes required behavior; it is not code and confers no `IMPLEMENTED` status. A Rust code block inside `Red-on-Rust.md` is specification text, never repository evidence.**

- **Left term:** T-64 `Specification`
- **Right term:** T-65 `Implementation`
- **Mandated by:** request §Special rule
- **Enforced by:** R-SCOPE-02, R-CLAIM-01, spec/00 §2 ladder

### Evidence

- `Red-on-Rust.md` L38929 — status block: SPECIFICATION FROZEN / IMPLEMENTATION READY — two different axes
- `Red-on-Rust.md` L28263 — 'machine-checked evidence that the implementation refines …' — the implementation is a separate object

### Consequence of conflating them

Conflation promotes claims without evidence, which is the failure mode spec/00 §2 exists to prevent; at this commit every obligation is `SPECIFIED`.

## N-07

**`Implementation ≠ Verification`. Code that exists is not code that conforms. Verification is independent evidence — differential agreement, mutation kills, crash-matrix classification — produced by machinery that shares no core logic with the implementation.**

- **Left term:** T-65 `Implementation`
- **Right term:** T-66 `Verification`
- **Mandated by:** request §Special rule
- **Enforced by:** R-SCOPE-04, R-REF-02, R-CLAIM-01, R-TEST-09

### Evidence

- `Red-on-Rust.md` L37696 — zero shared core logic between production and reference
- `Red-on-Rust.md` L11779 — 'testing an implementation against its own buggy logic merely proves consistency, not correctness'
- `Red-on-Rust.md` L28277 — corrected claim wording: evidence of refinement over the tested space

### Consequence of conflating them

Conflation makes a test suite validate its own bugs and turns coverage into a conformance claim (R-TEST-09 prohibits weakening tests for convenience).

## N-08

**`Verification ≠ Proof`. Machine-checked evidence over a tested state space is not a mathematical proof of the calculus. No theorem in the frozen source has a mechanized proof; Theorems 1-6 carry proof sketches only and remain `SPECIFIED`.**

- **Left term:** T-66 `Verification`
- **Right term:** T-67 `Proof`
- **Mandated by:** request §Special rule; frozen source L28263, L37444-37452
- **Enforced by:** R-CLAIM-01, R-CLAIM-03, spec/00 §2 `PROVEN` rung

### Evidence

- `Red-on-Rust.md` L37331 — superseded phrasing 'the property tests prove the code obeys the calculus'
- `Red-on-Rust.md` L28263 — frozen phrasing: 'formal proof obligations remain separately identified'
- `Red-on-Rust.md` L2028 — Theorem 1 with a proof sketch, not a proof

### Consequence of conflating them

Conflation produces an unjustified conformance claim; C-34 records that any report using the uncorrected phrasing violates R-CLAIM-01.

## N-09

**`LLM output ≠ Authority`. `LLMOutput ∈ Data`. The planner proposes and holds no authority: it cannot allocate capabilities, authorize effects, modify budgets or scheduler state, allocate actors, invoke the host, bypass compilation, or bypass persistence.**

- **Left term:** T-56 `LLMOutput`
- **Right term:** T-10 `Authority`
- **Mandated by:** request §Special rule; frozen source L27271-27285
- **Enforced by:** R-CORE-01, R-PLANNER-01, R-PLANNER-02, R-TRUST-01, R-TRUST-02

### Evidence

- `Red-on-Rust.md` L27271 — the eight enumerated planner prohibitions
- `Red-on-Rust.md` L27253 — `LLMOutput ∈ Data`
- `Red-on-Rust.md` L41320 — `LLMOutput ∧ UntrustedInput ↛ ExternalEffect`
- `Red-on-Rust.md` L41828 — trust table: LLM/planner = No

### Consequence of conflating them

Conflation is the whole threat model's failure: it makes a probabilistic generator a source of authority and defeats R-CORE-01 outright.

## N-10

**`ParsedBlock ≠ ValidatedPlan`. Syntactic validation against the dialect grammar produces a `ParsedBlock`; static effect annotation produces a `ValidatedPlan`. Judgments 11 and 12 of turn [3] are separate gates with separate failure modes.**

- **Left term:** T-03 `ParsedBlock`
- **Right term:** T-04 `ValidatedPlan`
- **Mandated by:** request §Required distinctions
- **Enforced by:** R-COMPILE-02, R-COMPILE-03

### Evidence

- `Red-on-Rust.md` L734 — judgment 11: `Block → ParsedBlock`
- `Red-on-Rust.md` L737 — judgment 12: `ParsedBlock → ValidatedPlan`
- `Red-on-Rust.md` L864 — `ParsedBlock { ast: NormalizedAST }`
- `Red-on-Rust.md` L865 — `ValidatedPlan { ir: PlanIR, effects: EffectSet }`

### Consequence of conflating them

Conflation collapses two compiler gates into one and makes U-22 (no effect-set inference stage) invisible.

## N-11

**`ValidatedPlan ≠ CapabilityCheckedPlan`. An effect-set annotation is not an authority verdict. Capability checking computes `κ_req` and requires `κ_req ⪯ κ_ambient`; a `ValidatedPlan` has been checked for neither.**

- **Left term:** T-04 `ValidatedPlan`
- **Right term:** T-05 `CapabilityCheckedPlan`
- **Mandated by:** request §Required distinctions
- **Enforced by:** R-COMPILE-03, R-CAP-04

### Evidence

- `Red-on-Rust.md` L737 — judgment 12 yields `ValidatedPlan`
- `Red-on-Rust.md` L740 — judgment 13: `ValidatedPlan → CapabilityCheckedPlan`
- `Red-on-Rust.md` L866 — `CapabilityCheckedPlan { ir: PlanIR, required_caps: CapSet }`

### Consequence of conflating them

Conflation lets an effect-annotated but authority-unchecked artifact be treated as safe, and makes `CAP-DERIVE-NO-AMPLIFICATION` untestable at the boundary.

## N-12

**`CapabilityCheckedPlan ≠ ExecutablePlan`. Static capability satisfaction is not resource bounding. Only the fourth stage carries `bounds: ResourceBounds` and the `_sealed` marker that makes forgery impossible.**

- **Left term:** T-05 `CapabilityCheckedPlan`
- **Right term:** T-06 `ExecutablePlan`
- **Mandated by:** request §Required distinctions
- **Enforced by:** R-COMPILE-03, R-COMPILE-05, R-BUDGET-01

### Evidence

- `Red-on-Rust.md` L743 — judgment 14: `CapabilityCheckedPlan → ExecutablePlan`, 'statically bounds fuel/memory'
- `Red-on-Rust.md` L866 — no `bounds` field
- `Red-on-Rust.md` L869 — `bounds: ResourceBounds` + `_sealed: Sealed`

### Consequence of conflating them

Conflation admits an unbounded plan to the machine, defeating the resource-bounded half of the thesis and R-BUDGET-01.

## N-13

**`Effect ≠ EffectRequest`. An `Effect` is immutable effect DATA `{op, target, params, cost}` whose canonical bytes define `EffectDigest`; an `EffectRequest` is the transient message that carries one effect plus an allocated id.**

- **Left term:** T-16 `Effect`
- **Right term:** T-17 `EffectRequest`
- **Mandated by:** request §Required distinctions
- **Enforced by:** R-CALC-04, R-EFFECT-01, R-EFFECT-06

### Evidence

- `Red-on-Rust.md` L9297 — `Effect { op, target, params, cost }`
- `Red-on-Rust.md` L23758 — `EffectRequest { id, effect }`
- `Red-on-Rust.md` L23738 — `EffectDigest(pub [u8;32])` — 'Canonical hash of the Effect'

### Consequence of conflating them

Conflation puts the id (an allocation counter) inside the digested bytes, so re-issuing the same effect would produce a different digest and break `EFFECT-RECEIPT-DIGEST-VALIDATION`.

## N-14

**`EffectIssued ≠ EffectReceipt`. The issued record is the machine's durable commitment (written before host invocation); the receipt is the host's result (received after). A receipt is validated AGAINST the issued record's id and digest; it never replaces it.**

- **Left term:** T-18 `EffectIssued`
- **Right term:** T-19 `EffectReceipt`
- **Mandated by:** request §Required distinctions
- **Enforced by:** R-EFFECT-06, R-DUR-03, R-HOST-03, EFFECT-RECEIPT-DIGEST-VALIDATION

### Evidence

- `Red-on-Rust.md` L23765 — `EffectIssued` — durable fact
- `Red-on-Rust.md` L23775 — `EffectReceipt` — host result
- `Red-on-Rust.md` L38052 — 'Receipt must validate both:' id and digest

### Consequence of conflating them

Conflation accepts a host result for an effect that was never durably committed, or accepts a mismatched receipt (mutations M011, M017).

## N-15

**`ActorStatus ≠ RunState`. Two distinct frozen enums: `ActorStatus` is machine-visible (`Running/Pending/Blocked/Halted/Fault`) and `RunState` is scheduler-visible (`Runnable/Running/Pending/Blocked/Halted/Faulted`). Neither subsumes the other; `Runnable` exists only in `RunState`, `Fault` only in `ActorStatus`.**

- **Left term:** T-35 `ActorStatus`
- **Right term:** T-36 `RunState`
- **Mandated by:** request §Required distinctions; C-18
- **Enforced by:** R-ACTOR-02, R-ACTOR-04, SCHED-BLOCKED-NOT-SCHEDULED

### Evidence

- `Red-on-Rust.md` L23793 — frozen `ActorStatus`
- `Red-on-Rust.md` L25526 — frozen `RunState`
- `Red-on-Rust.md` L25546 — `ActorState` holds BOTH: `run_state` and `status`

### Consequence of conflating them

Conflation schedules blocked actors (mutation M013) or loses the `Runnable` at-most-once queue invariant. C-18 keeps both; the mapping is never tabulated.

## N-16

**`Budget ≠ Consumable`. `Budget` is the triple `B = ⟨C, R, W⟩`; `Consumable` is one component of it (`C = ⟨F, I, D⟩`), the strictly-decreasing part. A budget also holds reservations and a deadline, which are not spent.**

- **Left term:** T-24 `Budget`
- **Right term:** T-25 `Consumable`
- **Mandated by:** request §Required distinctions
- **Enforced by:** R-BUDGET-01, R-CORE-05, BUDGET-CONSUMPTION-CONSERVATION

### Evidence

- `Red-on-Rust.md` L7129 — `B = ⟨C, R, W⟩`
- `Red-on-Rust.md` L7130 — `C = ⟨F, I, D⟩`: Consumable balances
- `Red-on-Rust.md` L9172 — `Budget { consumable, reserved, deadline }`

### Consequence of conflating them

Conflation treats a deadline as spendable or a reservation as consumed, breaking `C_available + C_escrowed + C_consumed = C_initial`.

## N-17

**`Consumable ≠ Reserved`. Consumables are strictly decreasing and never returned; reserved quantities are held and then RELEASED. `ReserveOK(r,R) ⇔ R + r ≤ R_max` and `ReleaseOK(r,R) ⇔ r ≤ R` are different checks in different directions.**

- **Left term:** T-25 `Consumable`
- **Right term:** T-26 `Reserved`
- **Mandated by:** request §Required distinctions; C-07
- **Enforced by:** R-BUDGET-03, R-BUDGET-04, BUDGET-ESCROW-CONSERVATION

### Evidence

- `Red-on-Rust.md` L7130 — consumables: fuel, I/O, duration
- `Red-on-Rust.md` L7131 — reserved: memory bytes, concurrency slots
- `Red-on-Rust.md` L7487 — the [15] correction giving `ReserveOK`/`ReleaseOK`
- `Red-on-Rust.md` L7314 — the pre-fix `BudgetOK` with the WRONG reservation direction

### Consequence of conflating them

Conflation re-introduces the C-07 direction error (an unbounded reservation passes) or leaks reserved capacity on release.

## N-18

**`LogicalTime ≠ Deadline`. `LogicalTime` (`t`) is the machine's current explicit time, advanced by `δ_t`; a `Deadline` (`W`) is an absolute bound checked against it (`t + δ_t ≤ W`). Neither is wall-clock time.**

- **Left term:** T-28 `LogicalTime`
- **Right term:** T-27 `Deadline`
- **Mandated by:** request §Required distinctions
- **Enforced by:** R-BUDGET-06, R-CAP-09, R-CORE-08

### Evidence

- `Red-on-Rust.md` L9137 — `pub struct LogicalTime(pub u64)`
- `Red-on-Rust.md` L9140 — `pub struct Deadline(pub Option<LogicalTime>)`
- `Red-on-Rust.md` L6437 — 'Time t is not fetched from the host OS'
- `Red-on-Rust.md` L6748 — a deadline is checked, not spent

### Consequence of conflating them

Conflation spends the deadline as a consumable or reads the clock from the host, violating R-CAP-09 and destroying replay determinism.

## N-19

**`WAL ≠ EventLog`. The WAL is DURABLE framing (`WalFrame`/`WalRecord`/`WalSequence`); the `EventLog` is the IN-MEMORY append log of `EventEnvelope`s held in `GlobalState.event_log`. Snapshot serialization records the event log's LENGTH because its contents live in the WAL.**

- **Left term:** T-45 `WAL`
- **Right term:** T-49 `EventLog`
- **Mandated by:** request §Required distinctions; U-16
- **Enforced by:** R-PERSIST-01, R-PERSIST-03, R-DUR-01, WAL-GAP-REJECT

### Evidence

- `Red-on-Rust.md` L27706 — 'actual events are in the WAL' — the in-memory log is not the WAL
- `Red-on-Rust.md` L27716 — the WAL protocol is a durable write ordering
- `Red-on-Rust.md` L25539 — `GlobalState.event_log: EventLog`
- `Red-on-Rust.md` L35127 — `WalRecord::Event(EventEnvelope)`

### Consequence of conflating them

Conflation treats an in-memory append as durability, defeating `HostInvoked(E) ⇒ DurableIssued(E)` and the WAL gap checks.

## N-20

**`WAL ≠ EffectJournal` as STRUCTURES, but the journal is not a separate durable file either: in the frozen 15B model the journal's records ARE `WalRecord` kinds. The journal is a causal record TAXONOMY; the WAL is the durable framing that carries it.**

- **Left term:** T-45 `WAL`
- **Right term:** T-23 `EffectJournal`
- **Mandated by:** request §Required distinctions; C-25
- **Enforced by:** R-DUR-02, R-DUR-03, R-PERSIST-03

### Evidence

- `Red-on-Rust.md` L26216 — 'a durable effect journal separate from the ordinary machine event log' — turn-[33] wording
- `Red-on-Rust.md` L35127 — 15B: journal records are `WalRecord` variants
- `Red-on-Rust.md` L28427 — the boxed theorem names `CommittedSnapshot + DurableLog + EffectJournal` as three components

### Consequence of conflating them

Conflation either duplicates durable state (two logs to keep consistent) or loses the causal laws `Issued ⇒ Prepared`, `Completed ⇒ Issued`, `Reconciled ⇒ Issued`.

## N-21

**`Snapshot ≠ WAL`. A snapshot is a committed, self-consistent, canonically encoded image of `GlobalState` with a version and digest; the WAL is the ordered durable log after it. `D = ⟨S, L, H⟩` and `Recover(D) = Replay(S, L, H)`: recovery needs both, and neither substitutes for the other.**

- **Left term:** T-48 `Snapshot`
- **Right term:** T-45 `WAL`
- **Mandated by:** request §Required distinctions
- **Enforced by:** R-PERSIST-04, R-PERSIST-05, R-RECOV-01, R-RECOV-03, SNAPSHOT-COMMIT-INTEGRITY

### Evidence

- `Red-on-Rust.md` L26127 — `D = ⟨S,L,H⟩`
- `Red-on-Rust.md` L26132 — `S` = persisted `GlobalState` snapshot
- `Red-on-Rust.md` L26133 — `L` = append-only durable event log AFTER that snapshot
- `Red-on-Rust.md` L26410 — `CommittedSnapshot(S) ⇒ S is self-consistent`

### Consequence of conflating them

Conflation loses the replay-after-snapshot ordering, so recovery reconstructs a state that never existed (crash point T6).

## N-22

**`Observation (planner-facing) ≠ Observation (differential)`. Two frozen types share the name `Observation`: the planner-facing summary is UNTRUSTED-BOUNDARY data (LLM input, capability summaries only) and the differential observation is TEST data (the comparison domain). They have disjoint field sets.**

- **Left term:** T-54 `Observation (planner-facing)`
- **Right term:** T-57 `Observation (differential)`
- **Mandated by:** request §Required distinctions; X-06
- **Enforced by:** R-PLANNER-01, R-REF-05, R-TEST-03

### Evidence

- `Red-on-Rust.md` L27156 — planner-facing `Observation { sequence, actor, value, events, faults, available_capabilities, budget }`
- `Red-on-Rust.md` L36170 — differential `Observation { terminal_states, event_trace, effects, budgets, scheduler_trace, faults, state_digest }`
- `Red-on-Rust.md` L36183 — 'a test representation, not a runtime serialization format'

### Consequence of conflating them

Conflation lets an LLM-facing structure become the differential oracle, which collapses the oracle (15C.38 anti-oracle-collapse) and leaks machine state to the planner.

## N-23

**`EffectId ≠ EffectDigest`. An id is a monotonic ALLOCATION counter value; a digest is `SHA-256(canonical_bytes(effect))`, the SEMANTIC identity. Two distinct requests can carry the same digest; the same request never carries two ids. Receipt validation requires BOTH to match.**

- **Left term:** T-20 `EffectId`
- **Right term:** T-21 `EffectDigest`
- **Mandated by:** request §Required distinctions
- **Enforced by:** R-CALC-04, R-DUR-03, R-EFFECT-06, R-HOST-03

### Evidence

- `Red-on-Rust.md` L23735 — `pub struct EffectId(pub u64)`
- `Red-on-Rust.md` L23738 — `pub struct EffectDigest(pub [u8;32])`
- `Red-on-Rust.md` L35143 — 'must carry the identical `EffectId` and `EffectDigest`'
- `Red-on-Rust.md` L38052 — 'Receipt must validate both:'

### Consequence of conflating them

Conflation lets a corrupted or divergent program issue a DIFFERENT effect and consume the next recorded result — 'deterministic nonsense rather than deterministic replay' (L1390).

## N-24

**`Indeterminate ≠ NotExecuted`. An interrupted effect is classified indeterminate; `NotExecuted` is reachable ONLY as an authoritative `ReconciliationOutcome` from the host reconciliation protocol, never as an inference from a missing record.**

- **Left term:** T-50 `Indeterminate`
- **Right term:** T-51 `ReconciliationOutcome`
- **Mandated by:** request §Required distinctions
- **Enforced by:** R-DUR-04, R-RECOV-02, R-RECOV-07, R-CORE-09, R-CLAIM-02

### Evidence

- `Red-on-Rust.md` L26576 — `Issued(E) ∧ ¬Completed(E)` ⇒ indeterminate
- `Red-on-Rust.md` L26593 — `enum ReconciliationOutcome { Completed(EffectReceipt), NotExecuted, Indeterminate }`
- `Red-on-Rust.md` L42100 — 'never infer NotExecuted'
- `Red-on-Rust.md` L38232 — crash classification at T3/T4

### Consequence of conflating them

Conflation re-executes an effect that may already have happened — a double-spend/double-write hazard; it is also prohibited outright by R-CLAIM-02.

## N-25

**`HostPolicy ≠ Authority`. The host gate is an INDEPENDENT defence-in-depth check that the concrete host will perform the effect; the kernel's `Authorized(A_c,E,t)` is the authority decision. Both must hold: the machine fails early on host policy at step 11 and the host's own check remains authoritative.**

- **Left term:** T-41 `HostPolicy`
- **Right term:** T-10 `Authority`
- **Mandated by:** request §Required distinctions
- **Enforced by:** R-HOST-01, R-CORE-02, R-TRUST-01

### Evidence

- `Red-on-Rust.md` L21893 — 'This is deliberately separate from the capability kernel'
- `Red-on-Rust.md` L10162 — 'Independent of the capability kernel's abstract authorization'
- `Red-on-Rust.md` L8733 — `HostPolicyOK(E)` // Gate 3
- `Red-on-Rust.md` L8820 — both `Authorized(A_c,E,t)` and `HostPolicyOK(E)` in one theorem

### Consequence of conflating them

Conflation makes one gate cover for the other: either the host becomes an authority source (untrusted, partially trusted at best) or the kernel is assumed to know OS-level permissions it cannot know.

## N-26

**`ReplayHost ≠ LiveHost`. The replay host consumes an ordered recorded trace and NEVER touches the external world; the live host performs real effects and is only PARTIALLY trusted. Both implement `HostExecutor`; they are not interchangeable and an unordered map is not the normative replay mechanism.**

- **Left term:** T-42 `ReplayHost`
- **Right term:** T-43 `LiveHost`
- **Mandated by:** request §Required distinctions; C-22
- **Enforced by:** R-HOST-02, R-HOST-03, R-HOST-04, R-CORE-08

### Evidence

- `Red-on-Rust.md` L34498 — `ReplayHost { trace: Vec<EffectReceipt>, cursor: usize }`
- `Red-on-Rust.md` L1191 — `LiveHost`
- `Red-on-Rust.md` L24011 — the superseded `HashMap` replay form
- `Red-on-Rust.md` L38298 — 'Do not use an unordered map as the normative replay mechanism'
- `Red-on-Rust.md` L41836 — trust table: Replay host = Yes, Live host = Partial

### Consequence of conflating them

Conflation either re-executes real external effects during replay (a live side effect inside a test) or accepts unordered replay, defeating R-CORE-08 determinism.

## N-27

**`ReferenceModel ≠ Production implementation`. They share ZERO core transition logic. The reference model is not a second copy, not a wrapper, and not a specification: it is an independently written implementation used as a comparator.**

- **Left term:** T-58 `ReferenceModel`
- **Right term:** T-65 `Implementation`
- **Mandated by:** request §Required distinctions
- **Enforced by:** R-SCOPE-04, R-REF-01, R-REF-02, R-REF-04

### Evidence

- `Red-on-Rust.md` L37696 — R-SCOPE-04: zero shared core logic
- `Red-on-Rust.md` L35347 — 15C.3 independence boundary; ten forbidden dependencies
- `Red-on-Rust.md` L11779 — 'testing an implementation against its own buggy logic merely proves consistency'

### Consequence of conflating them

Conflation makes the differential oracle tautological (oracle collapse, 15C.38) and destroys the only independent semantic evidence the project has.

## N-28

**`Constraint ≠ Authority`. A constraint is a NARROWING REQUEST — the argument of `derive` — and can never widen: `derive(A,C) ⪯ A` and each component meets (`S ⊓ S_c`, …). A constraint is not a grant, and holding one confers nothing.**

- **Left term:** T-12 `Constraint`
- **Right term:** T-10 `Authority`
- **Mandated by:** request §Required distinctions
- **Enforced by:** R-CAP-02, R-CAP-04, R-CORE-04, CAP-DERIVE-NO-AMPLIFICATION

### Evidence

- `Red-on-Rust.md` L6402 — `derive_op(⟨S,Q,R,T⟩, ⟨S_c,Q_c,R_c,T_c⟩) = ⟨S⊓S_c, Q⊓Q_c, R⊓R_c, T⊓T_c⟩`
- `Red-on-Rust.md` L6098 — `derive(A,C) ⪯ A`
- `Red-on-Rust.md` L6536 — `pub struct Constraint<S,Q,R,L>`

### Consequence of conflating them

Conflation permits authority amplification through a 'constraint' that actually widens — the defect `CAP-DERIVE-NO-AMPLIFICATION` and mutation M006 exist to kill.

## N-29

**`delegate ≠ attenuate ≠ derive`. `derive` is the ALGEBRA operation (`derive(A,C) ⪯ A`); `attenuate` is the in-actor MACHINE operation (`Expr::Attenuate`, rule E-Attenuate); `delegate` is the CROSS-ACTOR authority transfer accepted by the marshaller (`Expr::Delegate` / `Value::DelegatedCapability`). Ordinary marshalling rejects raw capabilities.**

- **Left term:** T-15 `DelegatedCapability`
- **Right term:** T-12 `Constraint`
- **Mandated by:** spec/05 §1 (derive/attenuate/delegate row)
- **Enforced by:** R-MARSHAL-01, R-MARSHAL-02, R-CAP-04, R-CORE-07

### Evidence

- `Red-on-Rust.md` L6397 — `derive` in the algebra
- `Red-on-Rust.md` L8717 — rule E-Attenuate uses `kernel.derive`
- `Red-on-Rust.md` L25989 — `Expr::Delegate { capability, constraint }`
- `Red-on-Rust.md` L42090 — `OrdinaryMarshal(Value::Capability) ⇒ Rejected`

### Consequence of conflating them

Conflation lets authority cross an actor boundary by ordinary message passing, amplifying the receiver's authority — `MARSHAL-NO-RAW-CAPABILITY` and mutation M008 target it.

## N-30

**`Mailbox ≠ RunnableQueue`. Both are FIFOs, and both are per-machine, but a mailbox holds `MarshalledValue`s for one actor while the runnable queue holds actor identities with AT-MOST-ONCE membership. A duplicate runnable entry is a defect; a duplicate message is not.**

- **Left term:** T-39 `Mailbox`
- **Right term:** T-40 `RunnableQueue`
- **Mandated by:** request §Required distinctions
- **Enforced by:** R-ACTOR-03, R-ACTOR-04, R-ACTOR-07, SCHED-FIFO

### Evidence

- `Red-on-Rust.md` L25538 — `GlobalState.runnable: RunnableQueue // FIFO, explicitly ordered`
- `Red-on-Rust.md` L8666 — `A_a` carries a `mailbox` component
- `Red-on-Rust.md` L25579 — `Deadlock` when all actors block
- `Red-on-Rust.md` L38489 — mutation: accepting duplicate runnable entries

### Consequence of conflating them

Conflation schedules an actor twice per turn (breaking one-transition-per-turn determinism) or treats message duplication as a scheduler defect.

## N-31

**`Frozen ≠ Verified`. 'FROZEN' means the requirement text is stable; it never means the behavior has been verified. `VERIFICATION CONTRACT: FROZEN` freezes the CONTRACT, not the evidence, and a frozen specification may still contain open contradictions and undecided items.**

- **Left term:** T-69 `Frozen`
- **Right term:** T-66 `Verification`
- **Mandated by:** spec/05 §6.9-6.10; request §Special rule (by implication)
- **Enforced by:** R-SCOPE-02, R-SCOPE-03, R-TEST-09

### Evidence

- `Red-on-Rust.md` L38935 — the four FROZEN status lines
- `Red-on-Rust.md` L37664 — 'frozen means frozen'
- `Red-on-Rust.md` L41297 — README: 'Frozen specification ≠ verified implementation'

### Consequence of conflating them

Conflation treats a stable document as evidence of correctness and suppresses the STOP-and-report rule when an ambiguity is found.
