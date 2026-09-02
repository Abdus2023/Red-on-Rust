# Atomic Requirement Registry — Part 1: Foundations (S-01 … S-06)

Areas: `SCOPE` (12), `CORE` (16), `TRUST` (9), `ARCH` (6), `PLANNER` (22), `COMPILE` (14) — 79 atomic units.
Field semantics: `req/00-method.md` §2. Evidence discipline: §3. All records are `SPECIFIED`.

---

## S-01 Scope, status, conventions

### REQ-SCOPE-001
- REQ-ID: REQ-SCOPE-001
- CATEGORY: scope
- SOURCE: Red-on-Rust.md L41293–41300([60]); README "Core Thesis"; spec/01 S-01 R-SCOPE-01
- NORMATIVE-LEVEL: MUST
- STATEMENT: The machine is deterministic: `InitialState + SchedulerTrace + HostTrace ⇒ UniqueMachineTrace`.
- PRECONDITIONS: a fixed initial state, a fixed scheduler trace, a fixed host trace
- POSTCONDITIONS: exactly one machine trace exists
- INVARIANTS: `InitialState + SchedulerTrace + HostTrace ⇒ UniqueMachineTrace`
- DEPENDENCIES: REQ-CORE-011, REQ-ACTOR-013, REQ-CEK-001
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: live-vs-replay determinism differential; `SCHED-FIFO`
- EVIDENCE-STATUS: SPECIFIED

### REQ-SCOPE-002
- REQ-ID: REQ-SCOPE-002
- CATEGORY: scope
- SOURCE: Red-on-Rust.md L41293–41300([60]); spec/01 S-01 R-SCOPE-01
- NORMATIVE-LEVEL: MUST
- STATEMENT: The machine is capability-scoped: no external effect occurs without kernel authorization of an attenuable capability grant.
- PRECONDITIONS: any transition that could produce an external effect
- POSTCONDITIONS: effect refused unless `Authorized(A,E,t)`
- INVARIANTS: `¬Authorized(A,E,t) ⇒ ¬ExternalEffect(E)`
- DEPENDENCIES: REQ-CORE-003, REQ-CAP-010
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: Track C gate matrix; mutations M004, M005, M006
- EVIDENCE-STATUS: SPECIFIED

### REQ-SCOPE-003
- REQ-ID: REQ-SCOPE-003
- CATEGORY: scope
- SOURCE: Red-on-Rust.md L41293–41300([60]); spec/01 S-01 R-SCOPE-01
- NORMATIVE-LEVEL: MUST
- STATEMENT: The machine is resource-bounded: every transition is gated on budget and deadline.
- PRECONDITIONS: any active transition
- POSTCONDITIONS: transition replaced by `fault(BudgetExhausted)` when any budget gate fails
- INVARIANTS: `t + δ_t(c) ≤ W`; `C_available + C_escrowed + C_consumed = C_initial`
- DEPENDENCIES: REQ-BUDGET-014, REQ-BUDGET-019, REQ-CORE-005
- SECURITY-IMPACT: medium
- VERIFICATION-METHOD: `BUDGET-CONSUMPTION-CONSERVATION`; mutations M007, M009
- EVIDENCE-STATUS: SPECIFIED

### REQ-SCOPE-004
- REQ-ID: REQ-SCOPE-004
- CATEGORY: scope
- SOURCE: Red-on-Rust.md L41293–41300([60]); spec/01 S-01 R-SCOPE-01
- NORMATIVE-LEVEL: MUST
- STATEMENT: The machine is crash-recoverable: machine state and causal effect state are reconstructed from durable artifacts at defined persistence boundaries.
- PRECONDITIONS: crash at a defined persistence boundary
- POSTCONDITIONS: recovery yields the pre-crash machine state, subject to REQ-CORE-013's proviso
- INVARIANTS: `Recover(Snapshot, EventLog, EffectJournal) ≡ PreCrashMachineState`
- DEPENDENCIES: REQ-CORE-013, REQ-RECOV-001, REQ-RECOV-002
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: crash-injection matrix T0–T6; recovery differential
- EVIDENCE-STATUS: SPECIFIED

### REQ-SCOPE-005
- REQ-ID: REQ-SCOPE-005
- CATEGORY: scope
- SOURCE: Red-on-Rust.md L41293–41300([60]); README; spec/01 S-01 R-SCOPE-01
- NORMATIVE-LEVEL: IS
- STATEMENT: Red-on-Rust is a Rust-based execution substrate for a family of homoiconic, dialect-oriented languages inspired by the REBOL/Red lineage.
- PRECONDITIONS: —
- POSTCONDITIONS: —
- INVARIANTS: —
- DEPENDENCIES: —
- SECURITY-IMPACT: none (descriptive)
- VERIFICATION-METHOD: UNDEFINED (see req/04, VU-01)
- EVIDENCE-STATUS: SPECIFIED

### REQ-SCOPE-006
- REQ-ID: REQ-SCOPE-006
- CATEGORY: process
- SOURCE: Red-on-Rust.md L38921–38924([54] §30); L41297–41315([60]); spec/01 S-01 R-SCOPE-02
- NORMATIVE-LEVEL: MUST
- STATEMENT: The architecture, specification, reference contract, and verification contract are FROZEN; the repository is in BOOTSTRAP state; no new semantic phase may be proposed.
- PRECONDITIONS: any implementation activity
- POSTCONDITIONS: changes occur only via a numbered frozen addendum
- INVARIANTS: —
- DEPENDENCIES: REQ-SCOPE-008, REQ-CLAIM-020
- SECURITY-IMPACT: low
- VERIFICATION-METHOD: specification-change review (process gate)
- EVIDENCE-STATUS: SPECIFIED

### REQ-SCOPE-007
- REQ-ID: REQ-SCOPE-007
- CATEGORY: process
- SOURCE: Red-on-Rust.md L38929–38942([54]); L42191–42265([60]); spec/01 S-01 R-SCOPE-02
- NORMATIVE-LEVEL: MUST
- STATEMENT: A frozen specification is not a verified implementation; "frozen" means the requirements are stable, not that conformance evidence exists.
- PRECONDITIONS: any conformance or status claim
- POSTCONDITIONS: claims are labelled on the evidence ladder with a cited artifact
- INVARIANTS: —
- DEPENDENCIES: REQ-CLAIM-017
- SECURITY-IMPACT: medium (claim discipline)
- VERIFICATION-METHOD: report review against `req/00-method.md` §3
- EVIDENCE-STATUS: SPECIFIED

### REQ-SCOPE-008
- REQ-ID: REQ-SCOPE-008
- CATEGORY: process
- SOURCE: Red-on-Rust.md L37664–37688([54] §1.1); L37648([54] §1.1 freeze rule); spec/01 S-01 R-SCOPE-03
- NORMATIVE-LEVEL: MUST NOT
- STATEMENT: The implementer MUST NOT redesign, reinterpret, simplify away, or silently modify frozen semantics: CEK semantics; evaluation order; lexical scoping; closure semantics; capability algebra; attenuation; revocation; budget algebra; effect authorization; effect issuance protocol; actor isolation; deterministic scheduling; marshalling rules; delegation semantics; canonical serialization; persistence protocol; crash matrix; recovery classification; LLM trust boundary; reference-model independence; differential-testing contract.
- PRECONDITIONS: any implementation decision touching the enumerated surface
- POSTCONDITIONS: the enumerated semantics are realized as specified
- INVARIANTS: — (closed enumeration; kept whole per rule 6)
- DEPENDENCIES: REQ-SCOPE-009, REQ-SCOPE-010
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: differential oracle over the affected area; mutation registry; fault adjudication `specification ambiguity` class
- EVIDENCE-STATUS: SPECIFIED

### REQ-SCOPE-009
- REQ-ID: REQ-SCOPE-009
- CATEGORY: process
- SOURCE: Red-on-Rust.md L37690([54] §1.1); spec/01 S-01 R-SCOPE-03
- NORMATIVE-LEVEL: MUST
- STATEMENT: If implementation difficulty exposes an ambiguity, the implementer MUST STOP and report it.
- PRECONDITIONS: an ambiguity is exposed during implementation
- POSTCONDITIONS: work on the affected component halts; a report is issued
- INVARIANTS: —
- DEPENDENCIES: REQ-CLAIM-019
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: process review; conflict reports in the frozen format
- EVIDENCE-STATUS: SPECIFIED

### REQ-SCOPE-010
- REQ-ID: REQ-SCOPE-010
- CATEGORY: process
- SOURCE: Red-on-Rust.md L37690–37691([54] §1.1); L38692–38712([54] §24); spec/01 S-01 R-SCOPE-03
- NORMATIVE-LEVEL: MUST NOT
- STATEMENT: Semantic ambiguity MUST NOT be resolved by inventing behavior; it requires an explicit specification decision before implementation proceeds.
- PRECONDITIONS: an ambiguity is exposed
- POSTCONDITIONS: no behavior is chosen locally to close the gap
- INVARIANTS: —
- DEPENDENCIES: REQ-SCOPE-009, REQ-TEST-022
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: process review; `req/03-ambiguous.md` remains open until addenda exist
- EVIDENCE-STATUS: SPECIFIED

### REQ-SCOPE-011
- REQ-ID: REQ-SCOPE-011
- CATEGORY: verification
- SOURCE: Red-on-Rust.md L37696–37720([54] §1.2); L35330–35375([48]); spec/01 S-01 R-SCOPE-04
- NORMATIVE-LEVEL: MUST NOT
- STATEMENT: The production implementation and the executable reference model MUST share zero core implementation logic — no `reference_* → production_*` calls for `step`, `authorize`, `budget`, `recover`, `encode`, or `scheduler`.
- PRECONDITIONS: both implementations exist in the workspace
- POSTCONDITIONS: no core-logic call edge from reference to production
- INVARIANTS: —
- DEPENDENCIES: REQ-REF-004
- SECURITY-IMPACT: high (oracle collapse would void all differential evidence)
- VERIFICATION-METHOD: Cargo dependency-graph and visibility review
- EVIDENCE-STATUS: SPECIFIED

### REQ-SCOPE-012
- REQ-ID: REQ-SCOPE-012
- CATEGORY: verification
- SOURCE: Red-on-Rust.md L37696–37720([54] §1.2); spec/01 S-01 R-SCOPE-04
- NORMATIVE-LEVEL: MAY
- STATEMENT: Shared semantic test fixtures are allowed; shared transition implementations are forbidden.
- PRECONDITIONS: test-fixture authoring
- POSTCONDITIONS: fixtures may be consumed by both sides; transition code may not
- INVARIANTS: —
- DEPENDENCIES: REQ-SCOPE-011
- SECURITY-IMPACT: medium
- VERIFICATION-METHOD: dependency review (fixtures crate vs transition crates)
- EVIDENCE-STATUS: SPECIFIED

---

## S-02 Core thesis and central invariants

### REQ-CORE-001
- REQ-ID: REQ-CORE-001
- CATEGORY: security-invariant
- SOURCE: Red-on-Rust.md L41320–41335([60]); L27505–27513([33] §23); spec/01 S-02 R-CORE-01
- NORMATIVE-LEVEL: MUST
- STATEMENT: `LLMOutput ∧ UntrustedInput ↛ ExternalEffect`. The central security boundary is the machine — not the language surface and not the model generating the program.
- PRECONDITIONS: any execution fed LLM output and/or untrusted input
- POSTCONDITIONS: no external effect occurs except through the chain of REQ-CORE-002
- INVARIANTS: `LLMOutput ∧ UntrustedInput ↛ ExternalEffect`
- DEPENDENCIES: REQ-CORE-002, REQ-COMPILE-002, REQ-DUR-001
- SECURITY-IMPACT: critical (the project's central property)
- VERIFICATION-METHOD: Track C gate short-circuit matrix; LLM outer-loop suite (untrusted-input rejection); mutations M004–M008
- EVIDENCE-STATUS: SPECIFIED

### REQ-CORE-002
- REQ-ID: REQ-CORE-002
- CATEGORY: security-invariant
- SOURCE: Red-on-Rust.md L27491–27509([33] §23); L41337–41351([60]); spec/01 S-02 R-CORE-02
- NORMATIVE-LEVEL: MUST
- STATEMENT: `ExternalEffect(E) ⇒ ValidatedPlan(P) ∧ Authorized(E,κ,t) ∧ CapabilityWithinCeiling(E) ∧ BudgetAvailable(E) ∧ DeadlineValid(E,t) ∧ HostPolicyOK(E) ∧ Issued(E)`.
- PRECONDITIONS: an external effect occurs
- POSTCONDITIONS: all seven conjuncts held for that effect, in the order enforced by REQ-EFFECT-005
- INVARIANTS: the 7-conjunct boxed formula (kept whole per rule 6)
- DEPENDENCIES: REQ-COMPILE-002, REQ-CAP-010, REQ-BUDGET-014, REQ-BUDGET-019, REQ-HOST-002, REQ-DUR-001
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: gate short-circuit matrix (per gate: subsequent gates untouched); `EFFECT-ISSUE-DURABLE-BEFORE-HOST`
- EVIDENCE-STATUS: SPECIFIED

### REQ-CORE-003
- REQ-ID: REQ-CORE-003
- CATEGORY: security-invariant
- SOURCE: Red-on-Rust.md L42056–42064([60]); L7413–7419([13]); spec/01 S-02 R-CORE-03
- NORMATIVE-LEVEL: MUST
- STATEMENT: `¬Authorized(A,E,t) ⇒ ¬ExternalEffect(E)`; operationally `¬Authorized ⇒ ¬Request`.
- PRECONDITIONS: authorization denied for effect E at logical time t
- POSTCONDITIONS: no host request is produced; actor faults or is refused
- INVARIANTS: `¬Authorized(A,E,t) ⇒ ¬ExternalEffect(E)`
- DEPENDENCIES: REQ-CAP-010, REQ-EFFECT-006
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: Track B mock-kernel denial tests; mutations M004, M005
- EVIDENCE-STATUS: SPECIFIED

### REQ-CORE-004
- REQ-ID: REQ-CORE-004
- CATEGORY: security-invariant
- SOURCE: Red-on-Rust.md L42066–42072([60]); L6404([11]); L37931–37935([54] §6); L41526–L41530([60] restated [60]); spec/01 S-02 R-CORE-04
- NORMATIVE-LEVEL: MUST
- STATEMENT: No authority amplification: `derive(A,C) ≼ A` always holds.
- PRECONDITIONS: any derivation/attenuation/delegation
- POSTCONDITIONS: the derived grant is component-wise no stronger than the parent
- INVARIANTS: `derive(A,C) ≼ A`
- DEPENDENCIES: REQ-CAP-012, REQ-CAP-007
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: `CAP-DERIVE-NO-AMPLIFICATION`; property test over generated authorities; mutation M006
- EVIDENCE-STATUS: SPECIFIED

### REQ-CORE-005
- REQ-ID: REQ-CORE-005
- CATEGORY: security-invariant
- SOURCE: Red-on-Rust.md L42074–42080([60]); L28203–28240([35]); L38006–38010([54] §7); spec/01 S-02 R-CORE-05
- NORMATIVE-LEVEL: MUST
- STATEMENT: No budget teleportation: `C_available + C_escrowed + C_consumed = C_initial`, with explicit accounting partitions.
- PRECONDITIONS: any budget mutation, spawn, issuance, or completion
- POSTCONDITIONS: the three-way sum is unchanged
- INVARIANTS: `C_available + C_escrowed + C_consumed = C_initial`
- DEPENDENCIES: REQ-BUDGET-019, REQ-CORE-006, REQ-RECOV-013
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: `BUDGET-CONSUMPTION-CONSERVATION`; mutation M007; teleportation test over actor tree
- EVIDENCE-STATUS: SPECIFIED

### REQ-CORE-006
- REQ-ID: REQ-CORE-006
- CATEGORY: security-invariant
- SOURCE: Red-on-Rust.md L28203–28240([35]); L25931–25945([32]); spec/01 S-02 R-CORE-05
- NORMATIVE-LEVEL: MUST
- STATEMENT: Spawn is an ownership transfer of budget, not creation and not consumption.
- PRECONDITIONS: `Expr::Spawn` executes
- POSTCONDITIONS: parent `available` decreases by the escrowed amount; child `available` increases by the same amount; global sum unchanged
- INVARIANTS: `Σ_actors C_consumable + Σ_escrow C_escrow + Σ_issued C_issue = C_global_initial`
- DEPENDENCIES: REQ-ACTOR-017, REQ-BUDGET-019
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: teleportation test; randomized Spawn/Request/Complete conservation sequences
- EVIDENCE-STATUS: SPECIFIED

### REQ-CORE-007
- REQ-ID: REQ-CORE-007
- CATEGORY: security-invariant
- SOURCE: Red-on-Rust.md L42082–42088([60]); L35147–35156([47]); L38050([54] §8); spec/01 S-02 R-CORE-06
- NORMATIVE-LEVEL: MUST
- STATEMENT: No host-before-durability: `HostInvoked(E) ⇒ DurableIssued(E)`.
- PRECONDITIONS: host adapter invoked for effect E
- POSTCONDITIONS: a durable `Issued` record for E exists before the call
- INVARIANTS: `HostInvoked(E) ⇒ DurableIssued(E)`
- DEPENDENCIES: REQ-DUR-001, REQ-DUR-002
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: `EFFECT-ISSUE-DURABLE-BEFORE-HOST`; `PanicHost` harness; crash points T0–T4
- EVIDENCE-STATUS: SPECIFIED

### REQ-CORE-008
- REQ-ID: REQ-CORE-008
- CATEGORY: security-invariant
- SOURCE: Red-on-Rust.md L35150–35156([47]); L42082–42088([60]); spec/01 S-02 R-CORE-06
- NORMATIVE-LEVEL: MUST NOT
- STATEMENT: An effect is not "issued" because an in-memory object exists; durable issuance means the `Issued` record is durable.
- PRECONDITIONS: issuance path executes
- POSTCONDITIONS: `Issued` state is reachable only after the durable record is synced
- INVARIANTS: —
- DEPENDENCIES: REQ-DUR-002, REQ-PERSIST-003
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: crash injection between append and sync (T1/T2); journal validator
- EVIDENCE-STATUS: SPECIFIED

### REQ-CORE-009
- REQ-ID: REQ-CORE-009
- CATEGORY: security-invariant
- SOURCE: Red-on-Rust.md L42090–42098([60]); L25685–25694([32]); L37955–37960([54] §6); spec/01 S-02 R-CORE-07
- NORMATIVE-LEVEL: MUST NOT
- STATEMENT: `OrdinaryMarshal(Value::Capability) ⇒ Rejected`; raw capability references MUST NOT cross actor boundaries through ordinary messages.
- PRECONDITIONS: `marshal(v)` encounters a capability anywhere in `v`
- POSTCONDITIONS: `Err(MarshalFault::CapabilityRequiresDelegation)`; recipient context unchanged
- INVARIANTS: `CapRef ∉ marshal(v)`
- DEPENDENCIES: REQ-MARSHAL-001, REQ-MARSHAL-005
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: `MARSHAL-NO-RAW-CAPABILITY` (README tag `MARSHAL-CAPABILITY-REJECT`); amplification test; mutation M006-class
- EVIDENCE-STATUS: SPECIFIED

### REQ-CORE-010
- REQ-ID: REQ-CORE-010
- CATEGORY: security-invariant
- SOURCE: Red-on-Rust.md L25700–25710([32] §4); L42090–42098([60]); L25294–25302([31] §26 region); spec/01 S-02 R-CORE-07
- NORMATIVE-LEVEL: MUST
- STATEMENT: Authority crosses actor boundaries only via explicit delegation.
- PRECONDITIONS: authority must reach another actor
- POSTCONDITIONS: transfer occurs only through the explicit delegation operation and the `DelegatedCapability` envelope
- INVARIANTS: `DelegatedAuthority ≼ ParentAuthority`; `Send(v) ∧ v contains no delegation ⇒ Authority_{receiver}' = Authority_{receiver}`
- DEPENDENCIES: REQ-MARSHAL-003, REQ-MARSHAL-004
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: Track C delegation tests; amplification test
- EVIDENCE-STATUS: SPECIFIED

### REQ-CORE-011
- REQ-ID: REQ-CORE-011
- CATEGORY: security-invariant
- SOURCE: Red-on-Rust.md L41623–41646([60]); L27518–27547([33] §24); spec/01 S-02 R-CORE-08
- NORMATIVE-LEVEL: MUST
- STATEMENT: Determinism: `InitialState + SchedulerTrace + HostTrace ⇒ UniqueMachineTrace`, with an accepted planner trace for end-to-end runs.
- PRECONDITIONS: identical initial state, scheduler trace, host trace (and accepted planner trace)
- POSTCONDITIONS: identical machine trace and final `GlobalState`
- INVARIANTS: `InitialState + SchedulerTrace + HostTrace ⇒ UniqueMachineTrace`
- DEPENDENCIES: REQ-ACTOR-013, REQ-PLANNER-017, REQ-HOST-011
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: live-vs-replay byte-identical `GlobalState`/`EventLog`; global differential
- EVIDENCE-STATUS: SPECIFIED

### REQ-CORE-012
- REQ-ID: REQ-CORE-012
- CATEGORY: trust-model
- SOURCE: Red-on-Rust.md L27518–27547([33] §24); L27392–27414([33]); spec/01 S-02 R-CORE-08
- NORMATIVE-LEVEL: MUST NOT
- STATEMENT: The LLM's stochasticity is above the deterministic machine, never inside it.
- PRECONDITIONS: any planner interaction
- POSTCONDITIONS: no nondeterminism enters machine state except via recorded, replayable observations
- INVARIANTS: —
- DEPENDENCIES: REQ-PLANNER-016, REQ-PLANNER-018
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: end-to-end replay with recorded proposal + `ReplayHost`
- EVIDENCE-STATUS: SPECIFIED

### REQ-CORE-013
- REQ-ID: REQ-CORE-013
- CATEGORY: security-invariant
- SOURCE: Red-on-Rust.md L27551–27569([33] §25); L35159–35176([47]); spec/01 S-02 R-CORE-09
- NORMATIVE-LEVEL: MUST
- STATEMENT: Causal crash recovery: `Recover(Snapshot, EventLog, EffectJournal) ≡ PreCrashMachineState` for every crash at a defined persistence boundary, **provided** every interrupted external effect is (a) durably reconciled, (b) safely idempotent/replayable, or (c) explicitly classified `Indeterminate` and prevented from silent continuation.
- PRECONDITIONS: crash at a defined persistence boundary; every interrupted effect satisfies (a), (b), or (c)
- POSTCONDITIONS: recovered machine state equals the pre-crash state
- INVARIANTS: `Recover(Snapshot, EventLog, EffectJournal) ≡ PreCrashMachineState` (qualified; kept whole per rule 6)
- DEPENDENCIES: REQ-RECOV-002…REQ-RECOV-008, REQ-DUR-008, U-06
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: crash matrix T0–T6 with exact classification; `Canonical(Recover_P(D)) = Canonical(Recover_R(D))`
- EVIDENCE-STATUS: SPECIFIED

### REQ-CORE-014
- REQ-ID: REQ-CORE-014
- CATEGORY: security-invariant
- SOURCE: Red-on-Rust.md L27563–27569([33] §25); L38233–38248([54] §12); L42082–42088 ([60]); L26186–26196([33] §7 region); spec/01 S-02 R-CORE-09
- NORMATIVE-LEVEL: MUST NOT
- STATEMENT: The system MUST NOT infer "not executed" from a missing completion record.
- PRECONDITIONS: `Issued` record exists with no durable `Completed`
- POSTCONDITIONS: effect classified `Indeterminate`; resolution only via reconciliation
- INVARIANTS: `Issued ∧ ¬Completed ⇒ Indeterminate`, never `NotExecuted`
- DEPENDENCIES: REQ-DUR-008, REQ-RECOV-014
- SECURITY-IMPACT: critical (a false "not executed" permits duplicated external effects)
- VERIFICATION-METHOD: `RECOVERY-ISSUED-INDETERMINATE`; crash points T2–T4
- EVIDENCE-STATUS: SPECIFIED

### REQ-CORE-015
- REQ-ID: REQ-CORE-015
- CATEGORY: security-invariant
- SOURCE: Red-on-Rust.md L42100–42105([60]); L35196–35208([47]); spec/01 S-02 R-CORE-10
- NORMATIVE-LEVEL: MUST
- STATEMENT: Invalid persistence state produces an explicit `RecoveryFault`.
- PRECONDITIONS: recovery validates durable state `D` and finds it invalid
- POSTCONDITIONS: `RecoveryFault` raised; no machine state is resumed
- INVARIANTS: `Invalid(D) ⇒ RecoveryFault`
- DEPENDENCIES: REQ-RECOV-011
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: negative corruption tests (checksum, gap, causality)
- EVIDENCE-STATUS: SPECIFIED

### REQ-CORE-016
- REQ-ID: REQ-CORE-016
- CATEGORY: security-invariant
- SOURCE: Red-on-Rust.md L35196–35208([47]); L38254–38272([54] §13); spec/01 S-02 R-CORE-10
- NORMATIVE-LEVEL: MUST NOT
- STATEMENT: Corruption is never silently repaired by mutation: no dropping duplicate runnable actors, no "fixing" budget mismatches, no ignoring sequence gaps or checksum failures.
- PRECONDITIONS: recovery encounters corruption
- POSTCONDITIONS: durable artifacts are not rewritten to make recovery succeed
- INVARIANTS: — (closed enumeration; kept whole per rule 6)
- DEPENDENCIES: REQ-RECOV-011, REQ-RECOV-012
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: mutations M015, M016; negative recovery tests
- EVIDENCE-STATUS: SPECIFIED

---

## S-03 Trust model and trusted computing base

### REQ-TRUST-001
- REQ-ID: REQ-TRUST-001
- CATEGORY: trust-model
- SOURCE: Red-on-Rust.md L27611–27624([33]); L41823–41841([60]); L28425([36] The Three Central Implications); spec/01 S-03 R-TRUST-01
- NORMATIVE-LEVEL: MUST
- STATEMENT: The LLM / planner is not trusted; its role is proposal generation only.
- PRECONDITIONS: —
- POSTCONDITIONS: no planner output is treated as authority
- INVARIANTS: `LLM output ∉ TCB authority`
- DEPENDENCIES: REQ-PLANNER-003…REQ-PLANNER-010
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: Track B mock-kernel call assertions; LLM outer-loop rejection suite
- EVIDENCE-STATUS: SPECIFIED

### REQ-TRUST-002
- REQ-ID: REQ-TRUST-002
- CATEGORY: trust-model
- SOURCE: Red-on-Rust.md L27611–27624([33]); L41440–41452([60]); L13572([21] type-system boundary); spec/01 S-03 R-TRUST-01
- NORMATIVE-LEVEL: MUST
- STATEMENT: `Block` (language data) is not trusted; it is untrusted program data and never a security boundary.
- PRECONDITIONS: —
- POSTCONDITIONS: `Block` structure is never used as an authority decision input
- INVARIANTS: `Block ⇏ ExecutablePlan`
- DEPENDENCIES: REQ-COMPILE-001, REQ-ORDER-017
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: malformed-`Block` rejection suite; first security gate
- EVIDENCE-STATUS: SPECIFIED

### REQ-TRUST-003
- REQ-ID: REQ-TRUST-003
- CATEGORY: trust-model
- SOURCE: Red-on-Rust.md L27622([33]); L41823–41841([60]); spec/01 S-03 R-TRUST-01
- NORMATIVE-LEVEL: IS
- STATEMENT: The live host is partially trusted: it executes in the external world under capability and policy constraints.
- PRECONDITIONS: an issued effect reaches the host
- POSTCONDITIONS: host execution remains capability- and policy-bounded
- INVARIANTS: —
- DEPENDENCIES: REQ-HOST-001, REQ-HOST-003
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: host policy tests; `PanicHost` boundary enforcement
- EVIDENCE-STATUS: SPECIFIED

### REQ-TRUST-004
- REQ-ID: REQ-TRUST-004
- CATEGORY: trust-model
- SOURCE: Red-on-Rust.md L27611–27624([33]); L41823–41841([60]); spec/01 S-03 R-TRUST-01
- NORMATIVE-LEVEL: IS
- STATEMENT: Trusted components are: compiler (establishes executable invariants), capability kernel (authority decisions), CEK machine (deterministic execution), scheduler (deterministic interleaving), budget system (resource conservation), persistence/effect journal (durable machine and causal effect state), ReplayHost (recorded-effect reconstruction), supervisor (lifecycle and recovery).
- PRECONDITIONS: —
- POSTCONDITIONS: —
- INVARIANTS: — (closed component set)
- DEPENDENCIES: REQ-TRUST-005
- SECURITY-IMPACT: medium
- VERIFICATION-METHOD: TCB composition review
- EVIDENCE-STATUS: SPECIFIED

### REQ-TRUST-005
- REQ-ID: REQ-TRUST-005
- CATEGORY: trust-model
- SOURCE: Red-on-Rust.md L28178–28230([35]); L27102([33] §18 region); spec/01 S-03 R-TRUST-02
- NORMATIVE-LEVEL: MUST
- STATEMENT: `LLM output ∉ TCB authority`. The TCB consists of the CEK machine, capability kernel, budget algebra, deterministic scheduler, canonical serializer, WAL/recovery state machine, and effect boundary.
- PRECONDITIONS: —
- POSTCONDITIONS: no authority decision derives from planner output
- INVARIANTS: —
- DEPENDENCIES: REQ-TRUST-001, REQ-TRUST-006
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: TCB review; differential authority-outcome comparison
- EVIDENCE-STATUS: SPECIFIED

### REQ-TRUST-006
- REQ-ID: REQ-TRUST-006
- CATEGORY: security-invariant
- SOURCE: Red-on-Rust.md L37722–37744([54] §1.3); L19153–19175([27]); spec/01 S-03 R-TRUST-03
- NORMATIVE-LEVEL: MUST NOT
- STATEMENT: The LLM, AST, evaluator, scheduler, host adapter, or ordinary `Value` representation MUST never manufacture authority.
- PRECONDITIONS: any component handling capabilities or effects
- POSTCONDITIONS: authority exists only as kernel-held state
- INVARIANTS: —
- DEPENDENCIES: REQ-KERN-006
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: `CapRef ⇏ AuthorityInspection` gate; visibility review; Track B mock kernel
- EVIDENCE-STATUS: SPECIFIED

### REQ-TRUST-007
- REQ-ID: REQ-TRUST-007
- CATEGORY: security-invariant
- SOURCE: Red-on-Rust.md L37722–37744([54] §1.3); L19153–19175([27]); spec/01 S-03 R-TRUST-03
- NORMATIVE-LEVEL: MUST
- STATEMENT: Capabilities are opaque handles; only the capability kernel decides authority.
- PRECONDITIONS: any authority decision
- POSTCONDITIONS: decision produced by kernel code only
- INVARIANTS: —
- DEPENDENCIES: REQ-KERN-001, REQ-KERN-006
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: visibility review; mock-kernel exactly-one-call assertions
- EVIDENCE-STATUS: SPECIFIED

### REQ-TRUST-008
- REQ-ID: REQ-TRUST-008
- CATEGORY: capability-kernel
- SOURCE: Red-on-Rust.md L37722–37744([54] §1.3); L19153–19175([27]); spec/01 S-03 R-TRUST-03
- NORMATIVE-LEVEL: MAY
- STATEMENT: The evaluator may call `derive(capability, constraint, logical_time)` and `authorize(capability, effect, logical_time)`.
- PRECONDITIONS: evaluator holds a `CapRef`
- POSTCONDITIONS: kernel performs the decision; evaluator receives only a result or fault
- INVARIANTS: —
- DEPENDENCIES: REQ-KERN-004, REQ-KERN-005
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: mock-kernel exactly-one-call with exact expected parameters
- EVIDENCE-STATUS: SPECIFIED

### REQ-TRUST-009
- REQ-ID: REQ-TRUST-009
- CATEGORY: security-invariant
- SOURCE: Red-on-Rust.md L37722–37744([54] §1.3); L39397–39407([58]); spec/01 S-03 R-TRUST-03
- NORMATIVE-LEVEL: MUST NOT
- STATEMENT: The evaluator MUST NOT inspect authority internals.
- PRECONDITIONS: evaluator holds a `CapRef`
- POSTCONDITIONS: no read path from evaluator to authority fields
- INVARIANTS: `CapRef ⇏ AuthorityInspection`
- DEPENDENCIES: REQ-KERN-006, REQ-ORDER-018
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: Rust visibility review; first security gate property 2
- EVIDENCE-STATUS: SPECIFIED

---

## S-04 System architecture and component boundaries

### REQ-ARCH-001
- REQ-ID: REQ-ARCH-001
- CATEGORY: architecture
- SOURCE: Red-on-Rust.md L37746–37798([54] §2); L27287–27310([33]); spec/01 S-04 R-ARCH-01
- NORMATIVE-LEVEL: MUST
- STATEMENT: The normative end-to-end path is: LLM/Planner → `PlanProposal` → staleness validation → `Block` → parse → normalize → validate → lower → capability analysis → resource bounds → `ExecutablePlan` → CEK machine → capability kernel / budget system → effect issuance → durable boundary → host.
- PRECONDITIONS: an end-to-end run from planner proposal to external effect
- POSTCONDITIONS: every stage occurs, in this order, with no stage skipped
- INVARIANTS: — (ordered chain; kept whole per rule 6)
- DEPENDENCIES: REQ-PLANNER-013, REQ-COMPILE-004, REQ-EFFECT-005, REQ-DUR-002
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: end-to-end conformance run; first differential gate
- EVIDENCE-STATUS: SPECIFIED

### REQ-ARCH-002
- REQ-ID: REQ-ARCH-002
- CATEGORY: architecture
- SOURCE: Red-on-Rust.md L41406–41424([60]); L41205–41215([58] §39); L37696([54] §1.2); spec/01 S-04 R-ARCH-02
- NORMATIVE-LEVEL: MUST
- STATEMENT: The verification architecture is independent and co-equal: Production → Observation (normalized) → Reference; production and reference do not share core transition logic.
- PRECONDITIONS: differential verification is in use
- POSTCONDITIONS: both sides execute independently and emit normalized observations
- INVARIANTS: —
- DEPENDENCIES: REQ-SCOPE-011, REQ-REF-001
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: dependency-graph review; differential harness operation
- EVIDENCE-STATUS: SPECIFIED

### REQ-ARCH-003
- REQ-ID: REQ-ARCH-003
- CATEGORY: security-invariant
- SOURCE: Red-on-Rust.md L9086–9097([17]); L41038–41050([58] §36); spec/01 S-04 R-ARCH-03
- NORMATIVE-LEVEL: MUST NOT
- STATEMENT: A raw `Block` has no path into `step()`.
- PRECONDITIONS: any call to the machine's transition function
- POSTCONDITIONS: the argument is always an `ExecutablePlan`
- INVARIANTS: `Block ⇏ ExecutablePlan`
- DEPENDENCIES: REQ-COMPILE-002, REQ-ORDER-017
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: type-level/visibility review; first security gate; malformed-`Block` rejection
- EVIDENCE-STATUS: SPECIFIED

### REQ-ARCH-004
- REQ-ID: REQ-ARCH-004
- CATEGORY: architecture
- SOURCE: Red-on-Rust.md L39296–39318([58]); L9086–9097([17]); spec/01 S-04 R-ARCH-03
- NORMATIVE-LEVEL: MUST
- STATEMENT: `ExecutablePlan` constructors are private to the compiler.
- PRECONDITIONS: workspace build
- POSTCONDITIONS: no crate other than the compiler can construct an `ExecutablePlan`
- INVARIANTS: —
- DEPENDENCIES: REQ-COMPILE-013
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: Rust visibility review; `cargo` API-surface check
- EVIDENCE-STATUS: SPECIFIED

### REQ-ARCH-005
- REQ-ID: REQ-ARCH-005
- CATEGORY: architecture
- SOURCE: Red-on-Rust.md L9086–9097([17]); L39296–39318([58]); spec/01 S-04 R-ARCH-03
- NORMATIVE-LEVEL: MUST
- STATEMENT: The production runtime only ever receives an `ExecutablePlan`.
- PRECONDITIONS: runtime entry points
- POSTCONDITIONS: no runtime API accepts `Block` or intermediate plan forms
- INVARIANTS: —
- DEPENDENCIES: REQ-ARCH-003, REQ-ARCH-004
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: API-surface/visibility review
- EVIDENCE-STATUS: SPECIFIED

### REQ-ARCH-006
- REQ-ID: REQ-ARCH-006
- CATEGORY: architecture
- SOURCE: Red-on-Rust.md L9059–9085([17]); spec/01 S-04 R-ARCH-04
- NORMATIVE-LEVEL: MUST
- STATEMENT: Dependency direction is: capability algebra → capability kernel → effect/cost & revocation → executable plan → actor state → global config → scheduler → host executor / replay host.
- PRECONDITIONS: workspace crate/module layout
- POSTCONDITIONS: no edge violates the stated direction
- INVARIANTS: —
- DEPENDENCIES: REQ-REPO-001, REQ-REPO-014
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: Cargo dependency review
- EVIDENCE-STATUS: SPECIFIED

---

## S-05 LLM / planner boundary

### REQ-PLANNER-001
- REQ-ID: REQ-PLANNER-001
- CATEGORY: planner-boundary
- SOURCE: Red-on-Rust.md L27175–27198([33]); spec/01 S-05 R-PLANNER-01
- NORMATIVE-LEVEL: IS
- STATEMENT: The planner returns `PlanProposal { observation_sequence: EventSequence, block: Block, planner_metadata }`.
- PRECONDITIONS: planner invoked
- POSTCONDITIONS: proposal has exactly these components
- INVARIANTS: —
- DEPENDENCIES: REQ-PLANNER-012; U-13 (`PlannerMetadata`/`ProposalDigest` undefined)
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: type review; stale-proposal test harness
- EVIDENCE-STATUS: SPECIFIED

### REQ-PLANNER-002
- REQ-ID: REQ-PLANNER-002
- CATEGORY: trust-model
- SOURCE: Red-on-Rust.md L27176–27198([33]); spec/01 S-05 R-PLANNER-01
- NORMATIVE-LEVEL: MUST
- STATEMENT: `LLMOutput ∈ Data`, not authority.
- PRECONDITIONS: any planner output
- POSTCONDITIONS: output is treated as data entering the compiler pipeline
- INVARIANTS: —
- DEPENDENCIES: REQ-TRUST-001, REQ-TRUST-005
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: untrusted-input rejection test; Track B mock kernel
- EVIDENCE-STATUS: SPECIFIED

### REQ-PLANNER-003
- REQ-ID: REQ-PLANNER-003
- CATEGORY: planner-boundary
- SOURCE: Red-on-Rust.md L27271–27285([33]); L41423–41425([60]); spec/01 S-05 R-PLANNER-02
- NORMATIVE-LEVEL: MUST NOT
- STATEMENT: The model MUST NOT allocate capabilities.
- PRECONDITIONS: any planner interaction
- POSTCONDITIONS: capability allocation occurs only in the kernel via `derive`
- INVARIANTS: —
- DEPENDENCIES: REQ-KERN-005
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: mock-kernel exactly-one-`derive`-call assertion (Track B)
- EVIDENCE-STATUS: SPECIFIED

### REQ-PLANNER-004
- REQ-ID: REQ-PLANNER-004
- CATEGORY: planner-boundary
- SOURCE: Red-on-Rust.md L27271–27285([33]); L41423–41425([60]); spec/01 S-05 R-PLANNER-02
- NORMATIVE-LEVEL: MUST NOT
- STATEMENT: The model MUST NOT authorize effects.
- PRECONDITIONS: any planner interaction
- POSTCONDITIONS: authorization occurs only in `kernel.authorize`
- INVARIANTS: —
- DEPENDENCIES: REQ-KERN-004
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: mock-kernel call assertion; gate matrix
- EVIDENCE-STATUS: SPECIFIED

### REQ-PLANNER-005
- REQ-ID: REQ-PLANNER-005
- CATEGORY: planner-boundary
- SOURCE: Red-on-Rust.md L27271–27285([33]); L41423–41425([60]); spec/01 S-05 R-PLANNER-02
- NORMATIVE-LEVEL: MUST NOT
- STATEMENT: The model MUST NOT modify budgets.
- PRECONDITIONS: any planner interaction
- POSTCONDITIONS: budget state changes only through machine transitions
- INVARIANTS: `C_available + C_escrowed + C_consumed = C_initial`
- DEPENDENCIES: REQ-CORE-005
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: budget conservation test across a planner cycle
- EVIDENCE-STATUS: SPECIFIED

### REQ-PLANNER-006
- REQ-ID: REQ-PLANNER-006
- CATEGORY: planner-boundary
- SOURCE: Red-on-Rust.md L27271–27285([33]); spec/01 S-05 R-PLANNER-02
- NORMATIVE-LEVEL: MUST NOT
- STATEMENT: The model MUST NOT modify the event log.
- PRECONDITIONS: any planner interaction
- POSTCONDITIONS: the append-only log is written only by the machine/persistence layer
- INVARIANTS: event log is append-only
- DEPENDENCIES: REQ-PERSIST-006
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: log-diff assertion across a planner cycle
- EVIDENCE-STATUS: SPECIFIED

### REQ-PLANNER-007
- REQ-ID: REQ-PLANNER-007
- CATEGORY: planner-boundary
- SOURCE: Red-on-Rust.md L27271–27285([33]); L41423–41425([60]); spec/01 S-05 R-PLANNER-02
- NORMATIVE-LEVEL: MUST NOT
- STATEMENT: The model MUST NOT allocate actors directly.
- PRECONDITIONS: any planner interaction
- POSTCONDITIONS: actors are created only by the `Spawn` transition
- INVARIANTS: actor IDs come from the global monotonic counter
- DEPENDENCIES: REQ-ACTOR-009, REQ-ACTOR-017
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: actor-count assertion across a planner cycle
- EVIDENCE-STATUS: SPECIFIED

### REQ-PLANNER-008
- REQ-ID: REQ-PLANNER-008
- CATEGORY: planner-boundary
- SOURCE: Red-on-Rust.md L27271–27285([33]); L41423–41425([60]); spec/01 S-05 R-PLANNER-02
- NORMATIVE-LEVEL: MUST NOT
- STATEMENT: The model MUST NOT invoke the host.
- PRECONDITIONS: any planner interaction
- POSTCONDITIONS: `HostExecutor::execute` is reachable only from step 16 of the request sequence
- INVARIANTS: `HostInvoked(E) ⇒ DurableIssued(E)`
- DEPENDENCIES: REQ-DUR-001
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: `PanicHost` harness; gate matrix
- EVIDENCE-STATUS: SPECIFIED

### REQ-PLANNER-009
- REQ-ID: REQ-PLANNER-009
- CATEGORY: planner-boundary
- SOURCE: Red-on-Rust.md L27271–27285([33]); L37781–37790([54] §2); spec/01 S-05 R-PLANNER-02
- NORMATIVE-LEVEL: MUST NOT
- STATEMENT: The model MUST NOT bypass validation.
- PRECONDITIONS: any planner proposal
- POSTCONDITIONS: the proposal's `Block` enters the full compiler pipeline
- INVARIANTS: `Block ⇏ ExecutablePlan`
- DEPENDENCIES: REQ-COMPILE-003, REQ-COMPILE-004
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: untrusted-input rejection suite; first security gate
- EVIDENCE-STATUS: SPECIFIED

### REQ-PLANNER-010
- REQ-ID: REQ-PLANNER-010
- CATEGORY: planner-boundary
- SOURCE: Red-on-Rust.md L27271–27285([33]); spec/01 S-05 R-PLANNER-02
- NORMATIVE-LEVEL: MUST NOT
- STATEMENT: The model MUST NOT alter scheduler state.
- PRECONDITIONS: any planner interaction
- POSTCONDITIONS: runnable queue and scheduler state change only via machine transitions
- INVARIANTS: an actor appears in the runnable queue at most once
- DEPENDENCIES: REQ-ACTOR-011, REQ-ACTOR-012
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: scheduler-trace assertion across a planner cycle
- EVIDENCE-STATUS: SPECIFIED

### REQ-PLANNER-011
- REQ-ID: REQ-PLANNER-011
- CATEGORY: planner-boundary
- SOURCE: Red-on-Rust.md L27271–27285([33]); spec/01 S-05 R-PLANNER-02
- NORMATIVE-LEVEL: MUST
- STATEMENT: The model may only propose a `Block`, which enters the ordinary compiler pipeline.
- PRECONDITIONS: planner output accepted for consideration
- POSTCONDITIONS: the `Block` is compiled like any other program text
- INVARIANTS: —
- DEPENDENCIES: REQ-COMPILE-002
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: end-to-end conformance run
- EVIDENCE-STATUS: SPECIFIED

### REQ-PLANNER-012
- REQ-ID: REQ-PLANNER-012
- CATEGORY: planner-boundary
- SOURCE: Red-on-Rust.md L27175–27236([33]); spec/01 S-05 R-PLANNER-03
- NORMATIVE-LEVEL: MUST
- STATEMENT: A proposal is causally bound to the machine state from which it was generated (`observation_sequence`).
- PRECONDITIONS: proposal generated from an observation sequence
- POSTCONDITIONS: the binding is checked before the proposal is used
- INVARIANTS: —
- DEPENDENCIES: REQ-PLANNER-013
- SECURITY-IMPACT: high (stale proposals act on obsolete authority/budget state)
- VERIFICATION-METHOD: stale-proposal rejection test
- EVIDENCE-STATUS: SPECIFIED

### REQ-PLANNER-013
- REQ-ID: REQ-PLANNER-013
- CATEGORY: planner-boundary
- SOURCE: Red-on-Rust.md L27236([33]); L28373([36]); L27918([34]); spec/01 S-05 R-PLANNER-03; see C-38/U-13
- NORMATIVE-LEVEL: AMBIGUOUS
- STATEMENT: The machine MUST verify the proposal's `observation_sequence` against current machine state and reject otherwise. The source states the predicate two ways: "`proposal.observation_sequence = current_planning_epoch`" (L27236) and "`observation_sequence < current_sequence` ⇒ `StalePlan`" (L28373, L27918). Which predicate is frozen is not stated.
- PRECONDITIONS: a proposal is submitted to the machine boundary
- POSTCONDITIONS: accepted proposals proceed to compilation; others are rejected as `StalePlan`
- INVARIANTS: —
- DEPENDENCIES: U-13
- SECURITY-IMPACT: high (the edge cases differ: accept-newer vs reject-equal-but-rebased)
- VERIFICATION-METHOD: UNDEFINED until the predicate is frozen (req/04, VU-06)
- EVIDENCE-STATUS: SPECIFIED

### REQ-PLANNER-014
- REQ-ID: REQ-PLANNER-014
- CATEGORY: planner-boundary
- SOURCE: Red-on-Rust.md L27199–27236([33]); L28517([36]); spec/01 S-05 R-PLANNER-03
- NORMATIVE-LEVEL: MUST
- STATEMENT: A stale proposal is rejected as `StalePlan` with no state mutation.
- PRECONDITIONS: staleness check fails
- POSTCONDITIONS: machine state, budget, event log, and actor set are byte-identical to before submission
- INVARIANTS: —
- DEPENDENCIES: REQ-PLANNER-013
- SECURITY-IMPACT: high ; AMB-25
- VERIFICATION-METHOD: stale-proposal test asserting zero state mutation (LLM outer-loop obligation 2)
- EVIDENCE-STATUS: SPECIFIED

### REQ-PLANNER-015
- REQ-ID: REQ-PLANNER-015
- CATEGORY: planner-boundary
- SOURCE: Red-on-Rust.md L27236([33]); L23806([30] `Fault`); spec/01 S-05 R-PLANNER-03
- NORMATIVE-LEVEL: MUST
- STATEMENT: `StalePlan` is a normal machine-visible outcome (a `Fault` variant), not an exception path outside the machine.
- PRECONDITIONS: staleness rejection occurs
- POSTCONDITIONS: the outcome is observable in the machine's fault channel and in normalized observations
- INVARIANTS: —
- DEPENDENCIES: REQ-CALC-013
- SECURITY-IMPACT: medium
- VERIFICATION-METHOD: fault-channel comparison in the differential observation
- EVIDENCE-STATUS: SPECIFIED

### REQ-PLANNER-016
- REQ-ID: REQ-PLANNER-016
- CATEGORY: planner-boundary
- SOURCE: Red-on-Rust.md L27392–27414([33]); spec/01 S-05 R-PLANNER-04
- NORMATIVE-LEVEL: MAY
- STATEMENT: The LLM need not be deterministic.
- PRECONDITIONS: —
- POSTCONDITIONS: —
- INVARIANTS: —
- DEPENDENCIES: REQ-CORE-012
- SECURITY-IMPACT: low
- VERIFICATION-METHOD: not applicable (permission, not obligation)
- EVIDENCE-STATUS: SPECIFIED

### REQ-PLANNER-017
- REQ-ID: REQ-PLANNER-017
- CATEGORY: security-invariant
- SOURCE: Red-on-Rust.md L27392–27414([33]); L28426([36] The Three Central Implications); spec/01 S-05 R-PLANNER-04
- NORMATIVE-LEVEL: MUST
- STATEMENT: The machine theorem is `InitialState + Plan + SchedulerTrace + HostTrace ⇒ UniqueMachineTrace`.
- PRECONDITIONS: an accepted plan is fixed
- POSTCONDITIONS: the machine trace is unique
- INVARIANTS: `InitialState + Plan + SchedulerTrace + HostTrace ⇒ UniqueMachineTrace`
- DEPENDENCIES: REQ-CORE-011, REQ-ACTOR-013
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: replay determinism differential
- EVIDENCE-STATUS: SPECIFIED

### REQ-PLANNER-018
- REQ-ID: REQ-PLANNER-018
- CATEGORY: planner-boundary
- SOURCE: Red-on-Rust.md L27411–27414([33]); L27927([34]); spec/01 S-05 R-PLANNER-04
- NORMATIVE-LEVEL: MUST
- STATEMENT: For exact end-to-end replay the machine records `PlannerAccepted { observation_sequence, proposal_digest, block }`.
- PRECONDITIONS: a proposal is accepted
- POSTCONDITIONS: the record exists and is replayable
- INVARIANTS: —
- DEPENDENCIES: REQ-PLANNER-019; U-13 (`proposal_digest` canonical form undefined)
- SECURITY-IMPACT: high ; AMB-10
- VERIFICATION-METHOD: end-to-end replay test using the recorded proposal
- EVIDENCE-STATUS: SPECIFIED

### REQ-PLANNER-019
- REQ-ID: REQ-PLANNER-019
- CATEGORY: planner-boundary
- SOURCE: Red-on-Rust.md L27392–27414([33]); L28520([36]); spec/01 S-05 R-PLANNER-04
- NORMATIVE-LEVEL: MUST
- STATEMENT: Replay consumes the recorded proposal instead of querying the LLM.
- PRECONDITIONS: a replay run is started
- POSTCONDITIONS: no planner call occurs; the recorded `block` is used
- INVARIANTS: —
- DEPENDENCIES: REQ-PLANNER-018
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: end-to-end replay equality of final `GlobalState` and `EventLog`
- EVIDENCE-STATUS: SPECIFIED

### REQ-PLANNER-020
- REQ-ID: REQ-PLANNER-020
- CATEGORY: verification
- SOURCE: Red-on-Rust.md L27920–27931([34]); L28513–28517([36]); spec/01 S-05 R-PLANNER-05
- NORMATIVE-LEVEL: MUST
- STATEMENT: The conformance suite MUST include untrusted-input rejection: raw/malformed/malicious `Block` data fed directly to the runtime is rejected at the compiler boundary.
- PRECONDITIONS: conformance suite runs
- POSTCONDITIONS: every such input is rejected before any machine transition
- INVARIANTS: `Block ⇏ ExecutablePlan`
- DEPENDENCIES: REQ-COMPILE-003, REQ-ARCH-003
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: untrusted-input rejection suite (LLM outer-loop obligation 1)
- EVIDENCE-STATUS: SPECIFIED

### REQ-PLANNER-021
- REQ-ID: REQ-PLANNER-021
- CATEGORY: verification
- SOURCE: Red-on-Rust.md L27920–27931([34]); L28517([36]); spec/01 S-05 R-PLANNER-05
- NORMATIVE-LEVEL: MUST
- STATEMENT: The conformance suite MUST include stale-proposal rejection: advanced machine state plus an old proposal yields rejection without state mutation.
- PRECONDITIONS: conformance suite runs
- POSTCONDITIONS: rejection observed and state unchanged
- INVARIANTS: —
- DEPENDENCIES: REQ-PLANNER-014
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: stale-proposal test (LLM outer-loop obligation 2)
- EVIDENCE-STATUS: SPECIFIED

### REQ-PLANNER-022
- REQ-ID: REQ-PLANNER-022
- CATEGORY: verification
- SOURCE: Red-on-Rust.md L27920–27931([34]); L28520([36]); spec/01 S-05 R-PLANNER-05
- NORMATIVE-LEVEL: MUST
- STATEMENT: The conformance suite MUST include end-to-end replay: a live session versus a replay with the recorded proposal and `ReplayHost` yields byte-for-byte identical final `GlobalState` and `EventLog`.
- PRECONDITIONS: conformance suite runs
- POSTCONDITIONS: byte equality of final state and log
- INVARIANTS: —
- DEPENDENCIES: REQ-PLANNER-019, REQ-HOST-008, REQ-CORE-011
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: end-to-end replay differential (LLM outer-loop obligation 3)
- EVIDENCE-STATUS: SPECIFIED

---

## S-06 Compilation boundary

### REQ-COMPILE-001
- REQ-ID: REQ-COMPILE-001
- CATEGORY: security-invariant
- SOURCE: Red-on-Rust.md L41440–41452([60]); L3834–3838([7]); L41038–41050([58] §36); spec/01 S-06 R-COMPILE-01
- NORMATIVE-LEVEL: MUST
- STATEMENT: `Block ≠ ExecutablePlan`.
- PRECONDITIONS: —
- POSTCONDITIONS: the two types are distinct and non-interchangeable
- INVARIANTS: `Block ⇏ ExecutablePlan`
- DEPENDENCIES: REQ-ARCH-003, REQ-ORDER-017
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: type-level review; first security gate
- EVIDENCE-STATUS: SPECIFIED

### REQ-COMPILE-002
- REQ-ID: REQ-COMPILE-002
- CATEGORY: security-invariant
- SOURCE: Red-on-Rust.md L41440–41452([60]); L9086–9097([17]); spec/01 S-06 R-COMPILE-01
- NORMATIVE-LEVEL: MUST
- STATEMENT: Only validated executable plans enter the trusted machine.
- PRECONDITIONS: machine start or continuation of a plan
- POSTCONDITIONS: the plan carries evidence of completed validation stages
- INVARIANTS: —
- DEPENDENCIES: REQ-COMPILE-004, REQ-ARCH-005
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: API-surface review; first differential gate
- EVIDENCE-STATUS: SPECIFIED

### REQ-COMPILE-003
- REQ-ID: REQ-COMPILE-003
- CATEGORY: security-invariant
- SOURCE: Red-on-Rust.md L41440–41452([60]); L39253–39267([58]); spec/01 S-06 R-COMPILE-01
- NORMATIVE-LEVEL: MUST NOT
- STATEMENT: No `Block` bypasses compilation.
- PRECONDITIONS: any path from planner output to execution
- POSTCONDITIONS: every path passes the compiler
- INVARIANTS: —
- DEPENDENCIES: REQ-ARCH-003
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: dependency/visibility review; untrusted-input rejection suite
- EVIDENCE-STATUS: SPECIFIED

### REQ-COMPILE-004
- REQ-ID: REQ-COMPILE-004
- CATEGORY: compilation
- SOURCE: Red-on-Rust.md L39253–39267([58]); L37746–37798([54] §2); spec/01 S-06 R-COMPILE-02
- NORMATIVE-LEVEL: MUST
- STATEMENT: Compilation MUST pass the stages parse → normalize → validate → lower → capability analysis → resource analysis.
- PRECONDITIONS: a `Block` is compiled
- POSTCONDITIONS: an `ExecutablePlan` exists only if all six stages succeeded
- INVARIANTS: — (ordered stage list; kept whole per rule 6)
- DEPENDENCIES: REQ-COMPILE-005; U-22 (no explicit effect-set-inference stage)
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: malformed-`Block` rejection suite; stage-coverage conformance test
- EVIDENCE-STATUS: SPECIFIED

### REQ-COMPILE-005
- REQ-ID: REQ-COMPILE-005
- CATEGORY: compilation
- SOURCE: Red-on-Rust.md L1953–1980([5], compilation theorem, superseded form); L39253–39267([58]); spec/01 S-06 R-COMPILE-02
- NORMATIVE-LEVEL: MUST
- STATEMENT: Any failed compilation stage yields `fault(F_compilation)`.
- PRECONDITIONS: a stage fails
- POSTCONDITIONS: a compilation fault is produced; no plan is emitted
- INVARIANTS: —
- DEPENDENCIES: REQ-CALC-013 (the name `F_compilation` has no counterpart in the frozen `Fault` enum — see req/03 AMB-08)
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: malformed-input suite asserting a fault, not a panic or a plan
- EVIDENCE-STATUS: SPECIFIED

### REQ-COMPILE-006
- REQ-ID: REQ-COMPILE-006
- CATEGORY: security-invariant
- SOURCE: Red-on-Rust.md L1930–1960([5]); L39253–39267([58]); spec/01 S-06 R-COMPILE-02
- NORMATIVE-LEVEL: MUST NOT
- STATEMENT: No raw `Block` reaches execution.
- PRECONDITIONS: compilation fails or is skipped
- POSTCONDITIONS: execution does not start
- INVARIANTS: `Block ⇏ ExecutablePlan`
- DEPENDENCIES: REQ-COMPILE-003, REQ-ARCH-003
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: untrusted-input rejection suite
- EVIDENCE-STATUS: SPECIFIED

### REQ-COMPILE-007
- REQ-ID: REQ-COMPILE-007
- CATEGORY: compilation
- SOURCE: Red-on-Rust.md L3874–3905([7] v2 form); L1953–1980([5] J1–J4, superseded form); L1953–1981([5] J1–J4 form, superseded); spec/01 S-06 R-COMPILE-03; spec/06 C-35
- NORMATIVE-LEVEL: IS
- STATEMENT: The combined static judgment `Γ; κ_static ⊢ e : τ ! F @ B` threads type, possible-effect set `F`, capability requirements, and a static budget upper bound `B`.
- PRECONDITIONS: a term is type-checked
- POSTCONDITIONS: the judgment produces all four components
- INVARIANTS: —
- DEPENDENCIES: U-22
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: compiler judgment conformance tests
- EVIDENCE-STATUS: SPECIFIED

### REQ-COMPILE-008
- REQ-ID: REQ-COMPILE-008
- CATEGORY: compilation
- SOURCE: Red-on-Rust.md L3874–3905([7]); spec/01 S-06 R-COMPILE-03
- NORMATIVE-LEVEL: MUST
- STATEMENT: `F` is a conservative over-approximation of the effect set; pure terms yield `F = ∅`.
- PRECONDITIONS: any term
- POSTCONDITIONS: no possible effect is omitted from `F`
- INVARIANTS: pure term ⇒ `F = ∅`
- DEPENDENCIES: REQ-COMPILE-007; U-22
- SECURITY-IMPACT: high (an unsound `F` would under-gate effects)
- VERIFICATION-METHOD: effect-set conformance tests over generated programs
- EVIDENCE-STATUS: SPECIFIED

### REQ-COMPILE-009
- REQ-ID: REQ-COMPILE-009
- CATEGORY: compilation
- SOURCE: Red-on-Rust.md L3874–3905([7]); L3925–3928([7]); spec/01 S-06 R-COMPILE-03
- NORMATIVE-LEVEL: MUST
- STATEMENT: If the term's worst-case cost exceeds the budget allocated to the term ($B_{\text{alloc}}$ in the S-Spawn premise $B_{\text{child}} \le B_{\text{alloc}}$), compilation fails.
- PRECONDITIONS: static resource analysis produces a bound above $B_{\text{alloc}}$
- POSTCONDITIONS: compilation fails; no plan is emitted
- INVARIANTS: —
- DEPENDENCIES: REQ-COMPILE-007, REQ-BUDGET-021
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: over-budget program rejection test
- EVIDENCE-STATUS: SPECIFIED

### REQ-COMPILE-010
- REQ-ID: REQ-COMPILE-010
- CATEGORY: compilation
- SOURCE: Red-on-Rust.md L1722–1745([4]); L2052–2070([5] Theorem 6); spec/01 S-06 R-COMPILE-04
- NORMATIVE-LEVEL: MUST
- STATEMENT: An `ExecutablePlan` is immutable.
- PRECONDITIONS: a plan exists
- POSTCONDITIONS: no in-place modification is possible
- INVARIANTS: —
- DEPENDENCIES: REQ-COMPILE-011
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: type/immutability review
- EVIDENCE-STATUS: SPECIFIED

### REQ-COMPILE-011
- REQ-ID: REQ-COMPILE-011
- CATEGORY: compilation
- SOURCE: Red-on-Rust.md L1722–1745([4]); spec/01 S-06 R-COMPILE-04
- NORMATIVE-LEVEL: MUST
- STATEMENT: A new plan can only be produced by another validated compilation transition (`plan₁ → execution/observation → planner → Block₂ → compiler → plan₂`).
- PRECONDITIONS: behavior must change
- POSTCONDITIONS: the change goes through the full pipeline again
- INVARIANTS: —
- DEPENDENCIES: REQ-COMPILE-004
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: dependency review (no plan-mutation API)
- EVIDENCE-STATUS: SPECIFIED

### REQ-COMPILE-012
- REQ-ID: REQ-COMPILE-012
- CATEGORY: security-invariant
- SOURCE: Red-on-Rust.md L2052–2070([5] Theorem 6, temporal integrity); spec/01 S-06 R-COMPILE-04
- NORMATIVE-LEVEL: MUST NOT
- STATEMENT: A plan authorized at `t₀` never silently acquires new authority at `t₁`.
- PRECONDITIONS: a plan executes across logical times
- POSTCONDITIONS: authority is re-checked per effect at the current logical time
- INVARIANTS: temporal integrity
- DEPENDENCIES: REQ-CAP-010, REQ-CAP-009
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: attenuation/expiration conformance tests at advancing logical time
- EVIDENCE-STATUS: SPECIFIED

### REQ-COMPILE-013
- REQ-ID: REQ-COMPILE-013
- CATEGORY: compilation
- SOURCE: Red-on-Rust.md L39296–39318([58]); spec/01 S-06 R-COMPILE-05
- NORMATIVE-LEVEL: MUST
- STATEMENT: `ExecutablePlan` constructors MUST remain private to the compiler crate.
- PRECONDITIONS: workspace build
- POSTCONDITIONS: construction is impossible outside the compiler crate
- INVARIANTS: —
- DEPENDENCIES: REQ-ARCH-004
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: Rust visibility review; API-surface test
- EVIDENCE-STATUS: SPECIFIED

### REQ-COMPILE-014
- REQ-ID: REQ-COMPILE-014
- CATEGORY: compilation
- SOURCE: Red-on-Rust.md L1953–1980([5] J2); spec/01 S-06 non-normative gap note; U-22
- NORMATIVE-LEVEL: NON-NORMATIVE
- STATEMENT: Explanatory note in the canonical spec: detailed effect-set inference (v1 judgment J2, `Γ ⊢ e ↝ Φ`) is not re-specified as a frozen pipeline stage.
- PRECONDITIONS: —
- POSTCONDITIONS: —
- INVARIANTS: —
- DEPENDENCIES: REQ-COMPILE-007, REQ-COMPILE-008, U-22
- SECURITY-IMPACT: none (descriptive; the gap itself is tracked as AMB-13)
- VERIFICATION-METHOD: not applicable
- EVIDENCE-STATUS: SPECIFIED
