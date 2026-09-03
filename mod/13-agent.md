# MOD-13 — AGENT: LLM / planner boundary

> Owns the membrane around the probabilistic planner: what it may emit, what it can
> never do, how proposals expire, and how its stochasticity is kept outside the
> deterministic machine.

## SECTION-ID

`MOD-13` (domain `AGENT`). Owner module file for the `PLANNER` obligation area.

## TITLE

LLM / planner boundary — proposal schema, the eight prohibitions, causal staleness
checking, planner non-determinism with recorded `PlannerAccepted` replay, and the
LLM outer-loop conformance suite.

## PURPOSE

Keep the thesis true at the only probabilistic input port: the planner generates
*proposals*, never authority. A proposal is data that earns execution only by
surviving MOD-02's pipeline and the machine's own staleness check; and because the
planner need not be deterministic, everything needed to replay its acceptance is
recorded durably so determinism (MOD-07) survives a probabilistic generator.

## NORMATIVE-CONTENT

Normative text home: `spec/01` S-05; atomic renderings
`req/01-registry-part1-foundations.md` (PLANNER block). This module owns:

- **Proposal schema** (R-PLANNER-01): `PlanProposal { observation_sequence:
  EventSequence, block: Block, planner_metadata }`; `LLMOutput ∈ Data` — it is not
  authority, not code-to-execute, not machine state.
- **The eight prohibitions** (R-PLANNER-02): the model MUST NOT allocate
  capabilities (MOD-03), authorize effects (MOD-03/08), modify budgets (MOD-04),
  modify the event log (MOD-11), allocate actors directly (MOD-06), invoke the host
  (MOD-09), bypass validation (MOD-02), or alter scheduler state (MOD-07). It may
  only propose a `Block` that enters the ordinary compiler pipeline.
- **Staleness** (R-PLANNER-03): a proposal is causally bound to the machine state it
  was generated from; the machine verifies `proposal.observation_sequence` against
  `current_planning_epoch` and rejects stale proposals as `StalePlan` — a normal,
  machine-visible outcome with **no state mutation** (exact predicate shape open —
  C-38/U-13: equality phrasing vs `< current ⇒ stale`).
- **Planner determinism not required** (R-PLANNER-04): the machine theorem is
  `InitialState + Plan + SchedulerTrace + HostTrace ⇒ UniqueMachineTrace`; for exact
  end-to-end replay the machine records `PlannerAccepted { observation_sequence,
  proposal_digest, block }` and replay consumes the record instead of querying the
  LLM.
- **Outer-loop conformance** (R-PLANNER-05): the conformance suite MUST include
  (1) untrusted-input rejection at the compiler boundary, (2) stale-proposal
  rejection without state mutation, (3) end-to-end replay: live session vs replay
  with recorded proposal + `ReplayHost` ⇒ byte-identical final `GlobalState` and
  `EventLog`.

Crate contract (mirrored by pointer): `ror-agent` — planner/observation/supervisor
integration (R-REPO-02).

## NON-NORMATIVE-CONTENT

- The early "isolation-ladder planner interface" sketch (turn [3], L306–325) is
  retained as superseded traceability (spec/02 S-05), not as requirements.
- `PlannerMetadata` fields and the canonical form of `ProposalDigest` are undefined
  (U-13); nothing here may be invented — records exist so tests cannot silently
  assume them.
- README/planner narrative ("plausible programs shouldn't receive authority") is
  orientation prose.

## INPUTS

- `PlanProposal` values from the (untrusted, out-of-process) LLM/planner.
- Current planning epoch (derived from the machine's event sequence — MOD-06 global
  state / MOD-11 durable log).
- Supervisor lifecycle signals (trusted; recovery/reconciliation triggers — MOD-12).

## OUTPUTS

- `Block` (post-staleness-check) to MOD-02 — the only thing that ever leaves this
  module toward the machine core.
- `StalePlan` rejections (fault surface, MOD-01's taxonomy).
- `PlannerAccepted` records (to MOD-11 durable log) enabling replay (MOD-09
  composition, MOD-15 comparison).

## DEPENDENCIES

- Module dependencies: MOD-01 (types, fault surface), MOD-02 (compilation),
  MOD-06 (epoch/state), MOD-11 (durable recording).
- Withdrawn with addendum III (R-TRUST-04, dep/05 V-04d applied): the old
  "replay composition for the conformance suite" dependency on the host
  module. The conformance suite (`tests/`) composes host and agent at test
  time; neither crate owns it and no crate edge is implied. Kept here as a
  record, not a dependency.
- Consumers: MOD-02 (downstream), MOD-12 (supervisor reconciliation entry point),
  MOD-15/17 (outer-loop tests).
- Crate edge: `ror-agent → ror-core, ror-compiler, ror-runtime` (`spec/07` §6).
- Blocking open items: **U-13** (`PlannerMetadata` fields, `ProposalDigest` canonical
  form, exact staleness predicate — AMB-10, C-38; AMB-25 naming).

## INVARIANTS

- `LLMOutput ∈ Data`; the planner possesses no authority-manipulating operation
  (R-PLANNER-01/02; the eight prohibitions distribute across their owning modules —
  central enforcement of R-CORE-01).
- Staleness: proposal accepted only when causally current; stale ⇒ `StalePlan` with
  zero state mutation (R-PLANNER-03).
- Replay fidelity: end-to-end replay substitutes `PlannerAccepted` for the live LLM
  and must yield identical final `GlobalState` + `EventLog` (R-PLANNER-04/05(3)).
- The planner's nondeterminism never enters the machine: determinism theorem carries
  the planner *trace*, not the planner process (R-PLANNER-04; with R-ACTOR-07 MOD-07).

## REQUIREMENTS

Canonical text: `spec/01` S-05; addendum IV. All 7 obligations `SPECIFIED`.

| ID | Obligation (short) | Provenance (`Red-on-Rust.md`) | Verification |
|---|---|---|---|
| R-PLANNER-01 | PlanProposal {observation_sequence, block, metadata}; LLMOutput ∈ Data | L27176–27198 | — |
| R-PLANNER-02 | Planner cannot allocate/authorize/modify/invoke/bypass (8 prohibitions) | L27271–27285, L37781–37790 | R-PLANNER-05(1) |
| R-PLANNER-03 | Staleness check; StalePlan rejection, no state mutation | L27199–27236, L28373 | R-PLANNER-05(2) — U-13 open |
| R-PLANNER-04 | Planner need not be deterministic; PlannerAccepted recording for replay | L27392–27414 | R-PLANNER-05(3) |
| R-PLANNER-05 | LLM outer-loop conformance (3 test obligations) | L27920–27931, L28513–28521 | 15E suite |
| R-PLANNER-06 | Staleness is exact equality: observation_sequence = current_planning_epoch; either-direction mismatch ⇒ StalePlan with zero state mutation; less-than-only reading superseded; future-tagged proposals mandatory rejection test (C-86 resolved; M026) | addendum IV (SEC-007) | M026, epoch-boundary conformance |
| R-PLANNER-07 | Observation channel capability-opaque: CapabilitySummary frozen as non-referential projection (counts, classes, ceilings); EffectIssued carries {id, actor, digest} only, cap-bearing log shape superseded; Capability ∉ Observables(LLM) (C-87 resolved; M027) | addendum IV (SEC-008) | M027, observation-opacity property |

Atomic registry records under this module: REQ-PLANNER-001…022; REQ-TEST-051 (the
LLM appears in the harness only as an input generator — parent R-PLANNER-05).
**7 obligations / 23 records.**

## SECURITY-BOUNDARY

The LLM is the only deliberately *hostile-by-default* input source (trust: No,
R-TRUST-01; `LLM output ∉ TCB authority`, R-TRUST-02). This module's boundary is
unusually simple: it emits `Block` data and epoch-tagged metadata, and everything
dangerous is someone else's gate. That simplicity is the point of the architecture —
there is exactly one thing to get right here (propose, validate staleness, record
acceptance) and all authority questions are answered downstream, which the eight
prohibitions enumerate by pointing at their owners.

## VERIFICATION-OBLIGATIONS

- The frozen 15E / outer-loop suite (R-PLANNER-05): untrusted-input rejection,
  stale-proposal rejection, end-to-end replay byte-equality (with MOD-02, MOD-09).
- Harness rules: the LLM appears only as an input generator; generated `PlanProposal`
  values are harness data (REQ-TEST-051, MOD-15 machinery).
- No mutation registry entries target this module directly; its protections are the
  gates it feeds (M004–M008 family, owners MOD-03/04/08/11).
- Milestone gates: contributes evidence to M11 (end-to-end determinism) and gating
  order item 15 of the frozen 20-step implementation order (R-ORDER-01, MOD-17).

## SOURCE-PROVENANCE

- Planner boundary frozen: [33] (L27150–27480); conformance obligations [34]
  (L27920–27931); master prompt §2 trust boundary (L37746–37798); 15C.41 harness
  boundary [48] (L36977–36996).
- Canonical set: `spec/02` S-05; `req/01-registry-part1-foundations.md` (PLANNER
  block).

## CROSS-REFERENCES

Owned here, binding elsewhere:

- R-PLANNER-02 → enforcement homes: MOD-03 (allocate/authorize), MOD-04 (budgets),
  MOD-07 (scheduler), MOD-06 (actors), MOD-09 (host), MOD-02 (validation bypass),
  MOD-11 (event log / persistence bypass) — each prohibition is technically enforced
  at the target module's API surface; this module owns the *negative contract* as a
  whole.
- R-PLANNER-03 → MOD-02 (checked before compilation), MOD-11 (epoch vs durable log).
- R-PLANNER-04 → MOD-11 (`PlannerAccepted` durable record), MOD-09 (replay consumes),
  MOD-07 (determinism theorem term).
- R-PLANNER-05 → MOD-17 (harness side via `ror-testkit`), MOD-09 (`ReplayHost`),
  MOD-02 (rejection case 1).

Owned elsewhere, binding AGENT: R-CORE-01 (MOD-01 central thesis this module
operationalizes), R-TRUST-01/02 (MOD-01 trust rows: planner No / outside TCB),
R-COMPILE-01/02 (MOD-02 — the only road from proposal to plan), R-ARCH-01 (MOD-01 —
pipeline stage 1). Open items: U-13 (this module, blocking outer-loop conformance
exactness), C-38, AMB-10, AMB-25.
