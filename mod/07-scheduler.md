# MOD-07 — SCHEDULER: Deterministic scheduling and wakeups

> Owns interleaving: who runs next, when a turn ends, and why the whole machine is
> nonetheless deterministic.

## SECTION-ID

`MOD-07` (domain `SCHEDULER`). Owner module file for the scheduling obligations of
the `ACTOR` area (R-ACTOR-04, R-ACTOR-07).

## TITLE

Deterministic FIFO scheduler — one CEK transition per actor per turn, at-most-once
runnable membership, deterministic wakeups, and the global determinism theorem that
these rules induce.

## PURPOSE

Make concurrency a *deterministic* mechanism: given the same initial state and the
same external traces (scheduler, host, planner), the machine must produce exactly one
trace. The scheduler is where nondeterminism would sneak in (selection order,
duplicate queue membership, scheduling of non-runnable actors); this module freezes
each of those choices.

## NORMATIVE-CONTENT

Normative text home: `spec/01` S-15 (scheduler portion); atomic renderings in
`req/01-registry-part4-durability-concurrency.md` (ACTOR block, records 010–016,
031). This module owns:

- **FIFO scheduler discipline** (R-ACTOR-04 — placed here per architectural
  responsibility; prefix is historical, see `mod/00-overview.md` §3): strictly FIFO
  selection; an actor appears in the runnable queue **at most once**
  (membership-enforced); exactly one actor performs exactly one CEK transition per
  scheduler turn; wakeups (effect receipts, message arrivals) enqueue at the **back**;
  `Pending`, `Blocked`, `Halted`, and `Faulted` actors are never scheduled;
  `ActorSelected` is logged per turn; an empty runnable queue yields a `Deadlock`
  outcome.
- **Deterministic concurrency theorem** (R-ACTOR-07): `InitialState + SchedulerTrace
  + HostTrace ⇒ UniqueMachineTrace` — the scheduler is strictly FIFO, IDs are
  monotonic (MOD-06), the CEK machine is deterministic (MOD-05); hence global
  transitions are uniquely determined given identical initial state and external
  observations. Canonical operative statement; central restatement R-CORE-08 in
  MOD-01 — marked duplication D-05.

Crate contract (mirrored by pointer): scheduler lives in `ror-runtime` (R-REPO-02).

## NON-NORMATIVE-CONTENT

- "Deterministic interleaving" (trust-table wording) is loose prose; the normative
  rule is FIFO one-transition-per-turn (C-37).
- `RunState.Runnable` is the scheduler-visible notion; its exact correspondence to
  `ActorStatus` is implied, not tabulated (C-18/AMB-05; mapping record
  REQ-ACTOR-035 is owned by MOD-06 and cross-referenced here).
- The shape of `SchedulerState` internals is not specified beyond the queue (U-02
  family).

## INPUTS

- Runnable membership changes: spawns (MOD-06), wakeups from receipts (MOD-08/09)
  and sends (MOD-06), halts/faults (MOD-05).
- Logical time (global state, MOD-06) for `ActorSelected` records and `δ_t` account
  (MOD-04: scheduler steps have `δ_t > 0`).

## OUTPUTS

- The single selected actor per turn (`ActorSelected` event → event log → MOD-11 WAL).
- Turn boundaries (authoritative for `δ_t` accounting and for observation slicing in
  MOD-15).
- `Deadlock` outcome on empty queue.

## DEPENDENCIES

- Module dependencies: MOD-01 (`GlobalState` shape R-CALC-08), MOD-05 (one CEK
  transition per turn), MOD-06 (isolation, queue contents, wakeups), MOD-04 (turn
  time advancement).
- Consumers: MOD-06 (actors run only under selection), MOD-12 (queue reconstruction
  at recovery), MOD-11 (selection events durable), MOD-14/15 (reference scheduler
  + trace comparison).
- Crate edge: inside `ror-runtime`.
- Blocking open items: **U-35** (the determinism theorem's own four terms are
  undefined — this module owns R-ACTOR-07, the canonical statement, so U-35 lands
  here first; it gates Track A and Track D), **U-07** (per-turn `δ_t` value, with
  MOD-04), **U-17** (snapshot queue vs reconstruction authority, with MOD-11/12).

## INVARIANTS

- FIFO: selection order is queue order; wakeups enqueue at back (R-ACTOR-04).
- At-most-once membership: an actor is in the runnable queue ≤ 1 time (R-ACTOR-04;
  mutation M012 tests duplication).
- Non-schedulable states: `Pending`/`Blocked`/`Halted`/`Faulted` are never selected
  (R-ACTOR-04; mutation M011).
- One transition per turn; `ActorSelected` logged; empty queue ⇒ `Deadlock`
  (R-ACTOR-04).
- Determinism: `InitialState + SchedulerTrace + HostTrace ⇒ UniqueMachineTrace`
  (R-ACTOR-07; canonical statement — central restatement R-CORE-08, D-05).
  **Qualified by U-35 (blocking):** this invariant is not yet *well-formed* — none of
  `SchedulerTrace`, `HostTrace`, `InitialState` or `UniqueMachineTrace` is defined
  anywhere in the frozen source or in this document set, and trace equality is never
  specified, so the invariant cannot currently be stated as a testable predicate
  (`spec/06` C-98; audit DET-001). The FIFO and at-most-once invariants above are
  independent of U-35 and stand on their own.

## REQUIREMENTS

Canonical text: `spec/01` S-15 (scheduler rules). All 2 obligations `SPECIFIED`.

| ID | Obligation (short) | Provenance (`Red-on-Rust.md`) | Verification |
|---|---|---|---|
| R-ACTOR-04 | FIFO scheduler; at-most-once membership; 1 transition/turn; blocked/pending/terminal never scheduled | L25558–25615, L38074–38106 | `SCHED-FIFO`, `SCHED-BLOCKED-NOT-SCHEDULED`, M011, M012, M013-cross, starvation test |
| R-ACTOR-07 | Deterministic concurrency theorem (D-05 canonical) | L25759–25766 | global differential (Track D) |

Atomic registry records under this module (parent-propagated): REQ-ACTOR-010…016;
REQ-ACTOR-031. **2 obligations / 8 records.**

## SECURITY-BOUNDARY

The scheduler is a TCB member (R-TRUST-01: "Deterministic interleaving"). Its
security content is *denial of covert channels and confusion*: a scheduler that can
pick non-FIFO, double-schedule, or wake the blocked would let an attacker reorder
observable effects and break replay equivalence, invalidating recovery evidence and
the determinism theorem MOD-15 relies on as oracle.

## VERIFICATION-OBLIGATIONS

- Tags: `SCHED-FIFO` (FIFO selection; deterministic wakeup — M012),
  `SCHED-BLOCKED-NOT-SCHEDULED` (Pending/Blocked/Halted/Faulted never selected —
  M011).
- Mutations: M011 (schedule blocked actor), M012 (duplicate runnable queue entry);
  M013's mailbox effect is observed here (owned by MOD-06).
- Conformance: starvation test (strict interleaving, 100 actors); global determinism
  differential — live vs replay final-state digest equality (with MOD-09 replay).
- Tracks: Track A (scheduler-order equivalence; REQ-TEST-058).
- Milestone gates: M6 (FIFO scheduler, blocked/wakeup); feeds M5 wakeup ordering.

## SOURCE-PROVENANCE

- Frozen scheduler text: [32] (L25558–25615, at-most-once invariant), [31]
  (L24165–24224, queue/turn machinery), theorem [32] (L25759–25766); master prompt §9
  (L38074–38106); one-transition-per-turn restatement L24345–24361
  (REQ-ACTOR-012 second citation per registry pass).
- Canonical set: `spec/02` S-15; `req/01-registry-part4-durability-concurrency.md`.

## CROSS-REFERENCES

Owned here, binding elsewhere:

- R-ACTOR-04 → MOD-06 (mailbox/wakeup producers enqueue deterministically),
  MOD-12 (recovery step 10 reconstructs + revalidates the queue — U-17),
  MOD-11 (selection events are durable WAL content).
- R-ACTOR-07 → MOD-01 (central restatement R-CORE-08 — D-05), MOD-09 (the host-trace
  term), MOD-13 (planner trace for end-to-end replay), MOD-15 (the property its
  differential oracle asserts), MOD-12 (recovery must re-enter deterministic
  scheduling).

Owned elsewhere, binding SCHEDULER: R-ACTOR-02 (MOD-06 owns `GlobalState`; the
runnable queue is a field of it), R-BUDGET-06 (MOD-04 owns `δ_t`; scheduler steps
have positive delta), R-PLANNER-02 (MOD-13: planner cannot touch scheduler state),
R-RECOV-03 step 12 (MOD-12: recovery ends by re-entering the deterministic
scheduler). Open items: U-35 (theorem terms undefined — C-98/C-99, this module's
own R-ACTOR-07), U-07 (with MOD-04), U-17 (with MOD-11/12), AMB-05 (enum
mapping, MOD-06-side).
