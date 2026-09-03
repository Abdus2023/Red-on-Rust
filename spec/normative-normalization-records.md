# Red-on-Rust Specification — Precise Normative Normalization Records

**Source:** `spec/01-canonical-specification.md` (24 sections, 148 requirements `R-SCOPE-01`…`R-CLAIM-04`).

> **Post-audit addenda (outside this pass's scope):** obligations `R-COMPILE-06`, `R-KERN-04`, `R-KERN-05`, `R-EFFECT-08` were added after the normalization pass as frozen addenda (SEC-001/SEC-002 remediation). They have no normalization record: each is its own original — no substitution, `Original = Normalized` by construction. The same holds for the five addendum-II obligations (`R-CANON-12`, `R-CORE-11`, `R-MARSHAL-05`, `R-MARSHAL-06`, `R-PERSIST-07`; remediations SEC-003/004/005/016/018).

**Method:** Each specification requirement was audited and rewritten into precise RFC 2119 normative language (`MUST`, `MUST NOT`, `SHOULD`, `SHOULD NOT`, `MAY`, `INFORMATIVE`).

**Rules Enforced:**

1. Preserve semantic strength.
2. Never weaken MUST into SHOULD.
3. Never strengthen SHOULD into MUST.
4. Convert vague obligations into explicit conditions where the source supports doing so.
5. Do not invent missing conditions.
6. Do not turn examples into requirements.
7. Do not turn implementation suggestions into architectural requirements.
8. Preserve negative guarantees.
9. Preserve security invariants exactly.
10. Preserve mathematical notation.

**Flagged Terms Audited:** `probably`, `normally`, `should be fine`, `etc.`, `as needed`, `where appropriate`, `obviously`, `simple`, `secure`, `deterministic`, `safe`, `reliable`.

---

### R-SCOPE-01
- **Original:**
  > Red-on-Rust is a deterministic, capability-scoped, resource-bounded, crash-recoverable execution machine for probabilistically generated programs. It is a Rust-based execution substrate for a family of homoiconic, dialect-oriented languages inspired by the REBOL/Red lineage.
- **Normalized:**
  > Red-on-Rust MUST be a deterministic, capability-scoped, resource-bounded, crash-recoverable execution machine for probabilistically generated programs. It MUST serve as a Rust-based execution substrate for a family of homoiconic, dialect-oriented languages inspired by the REBOL/Red lineage. [INFORMATIVE: "deterministic" is explicitly defined in S-02 / R-CORE-08 as InitialState + SchedulerTrace + HostTrace ⇒ UniqueMachineTrace].
- **Reason:** Converted declarative scope statement into explicit normative MUST obligations; annotated flagged term "deterministic" with its explicit theorem definition.
- **Semantic Risk:** `None`

---

### R-SCOPE-02
- **Original:**
  > The architecture, specification, reference contract, and verification contract are FROZEN. The repository is in BOOTSTRAP state. A frozen specification is not a verified implementation; frozen means the requirements are stable, not that evidence of conformance exists.
- **Normalized:**
  > The architecture, specification, reference contract, and verification contract MUST be maintained as FROZEN. The repository MUST remain in BOOTSTRAP state until implementation evidence is provided. A frozen specification MUST NOT be construed as a verified implementation; frozen status MUST indicate requirement stability without asserting evidence of conformance.
- **Reason:** Converted declarative status sentences into explicit normative MUST and MUST NOT constraints.
- **Semantic Risk:** `None`

---

### R-SCOPE-03
- **Original:**
  > The implementer MUST NOT redesign, reinterpret, simplify away, or silently modify frozen semantics (CEK semantics, evaluation order, lexical scoping, closure semantics, capability algebra, attenuation, revocation, budget algebra, effect authorization, effect issuance protocol, actor isolation, deterministic scheduling, marshalling rules, delegation semantics, canonical serialization, persistence protocol, crash matrix, recovery classification, LLM trust boundary, reference-model independence, differential-testing contract). If implementation difficulty exposes an ambiguity, the implementer MUST STOP and report it; semantic ambiguity MUST NOT be resolved by inventing behavior.
- **Normalized:**
  > The implementer MUST NOT redesign, reinterpret, simplify away, or silently modify frozen semantics (CEK semantics, evaluation order, lexical scoping, closure semantics, capability algebra, attenuation, revocation, budget algebra, effect authorization, effect issuance protocol, actor isolation, deterministic scheduling, marshalling rules, delegation semantics, canonical serialization, persistence protocol, crash matrix, recovery classification, LLM trust boundary, reference-model independence, differential-testing contract). If implementation difficulty exposes an ambiguity, the implementer MUST STOP and report it; semantic ambiguity MUST NOT be resolved by inventing behavior. [INFORMATIVE: "deterministic scheduling" is explicitly defined in S-15 / R-ACTOR-07].
- **Reason:** Annotated flagged term "deterministic scheduling" with cross-reference to its explicit definition in S-15 / R-ACTOR-07; retained existing MUST NOT / MUST modals.
- **Semantic Risk:** `None`

---

### R-SCOPE-04
- **Original:**
  > The production implementation and the executable reference model MUST share zero core implementation logic (no `reference_* → production_*` calls for step, authorize, budget, recover, encode, scheduler). Shared semantic test fixtures are allowed; shared transition implementations are forbidden.
- **Normalized:**
  > The production implementation and the executable reference model MUST share zero core implementation logic (no `reference_* → production_*` calls for step, authorize, budget, recover, encode, scheduler). Shared semantic test fixtures MAY be used; shared transition implementations MUST NOT be used.
- **Reason:** Normalized passive permissions ("are allowed") to MAY and prohibitions ("are forbidden") to MUST NOT.
- **Semantic Risk:** `None`

---

### R-CORE-01
- **Original:**
  > `LLMOutput ∧ UntrustedInput ↛ ExternalEffect`. The central security boundary is the machine — not the language surface and not the model generating the program.
- **Normalized:**
  > The machine MUST enforce the central external-effect invariant: `LLMOutput ∧ UntrustedInput ↛ ExternalEffect`. The central security boundary MUST be the machine; neither the language surface nor the model generating the program MUST be treated as a security boundary.
- **Reason:** Added explicit MUST and MUST NOT modals, preserving exact mathematical invariant formula and negative guarantee.
- **Semantic Risk:** `None`

---

### R-CORE-02
- **Original:**
  > **R-CORE-02 (external-effect chain).**
  > `ExternalEffect(E) ⇒ ValidatedPlan(P) ∧ Authorized(E,κ,t) ∧ CapabilityWithinCeiling(E) ∧ BudgetAvailable(E) ∧ DeadlineValid(E,t) ∧ HostPolicyOK(E) ∧ Issued(E)`. *(L41337–41351; L27491–27509.)*
- **Normalized:**
  > An ExternalEffect(E) MUST NOT occur unless the complete validation chain holds invariant: `ExternalEffect(E) ⇒ ValidatedPlan(P) ∧ Authorized(E,κ,t) ∧ CapabilityWithinCeiling(E) ∧ BudgetAvailable(E) ∧ DeadlineValid(E,t) ∧ HostPolicyOK(E) ∧ Issued(E)`.
- **Reason:** Converted implication statement into explicit normative MUST NOT condition, preserving exact mathematical formula.
- **Semantic Risk:** `None`

---

### R-CORE-03
- **Original:**
  > `¬Authorized(A,E,t) ⇒ ¬ExternalEffect(E)` (equivalently `¬Authorized ⇒ ¬Request` at the operational level).
- **Normalized:**
  > If an effect E is not authorized, the machine MUST NOT produce an ExternalEffect: `¬Authorized(A,E,t) ⇒ ¬ExternalEffect(E)` (equivalently `¬Authorized ⇒ ¬Request` at the operational level).
- **Reason:** Replaced formula-only statement with explicit MUST NOT normative prohibition, preserving exact mathematical formula.
- **Semantic Risk:** `None`

---

### R-CORE-04
- **Original:**
  > `derive(A,C) ≼ A` always holds.
- **Normalized:**
  > Capability derivation MUST NOT amplify authority: `derive(A,C) ≼ A` MUST hold invariant for all authorities A and constraints C.
- **Reason:** Standardized normative modals (MUST NOT, MUST), preserving exact capability algebra formula.
- **Semantic Risk:** `None`

---

### R-CORE-05
- **Original:**
  > `C_available + C_escrowed + C_consumed = C_initial`, with explicit accounting partitions; spawn is an ownership transfer, not creation or consumption.
- **Normalized:**
  > Budget accounting MUST maintain the partition invariant `C_available + C_escrowed + C_consumed = C_initial`; actor spawn MUST be executed as a budget ownership transfer, MUST NOT create new budget, and MUST NOT consume budget.
- **Reason:** Added explicit MUST and MUST NOT modals, preserving exact budget partition formula.
- **Semantic Risk:** `None`

---

### R-CORE-06
- **Original:**
  > `HostInvoked(E) ⇒ DurableIssued(E)`. An effect is not "issued" because an in-memory object exists; durable issuance means the `Issued` record is durable.
- **Normalized:**
  > The host MUST NOT be invoked for an effect E before durable issuance is committed: `HostInvoked(E) ⇒ DurableIssued(E)`. An effect MUST NOT be treated as issued merely because an in-memory object exists; durable issuance MUST require a durable `Issued` record.
- **Reason:** Converted declarative invariant into explicit MUST NOT and MUST constraints, preserving exact mathematical formula.
- **Semantic Risk:** `None`

---

### R-CORE-07
- **Original:**
  > `OrdinaryMarshal(Value::Capability) ⇒ Rejected`. Authority crosses actor boundaries only via explicit delegation.
- **Normalized:**
  > Ordinary marshalling of raw capability values MUST be rejected: `OrdinaryMarshal(Value::Capability) ⇒ Rejected`. Authority MUST NOT cross actor boundaries except via explicit delegation.
- **Reason:** Added explicit MUST and MUST NOT modals, preserving exact formula.
- **Semantic Risk:** `None`

---

### R-CORE-08
- **Original:**
  > `InitialState + SchedulerTrace + HostTrace ⇒ UniqueMachineTrace` (with an accepted planner trace for end-to-end runs). The LLM's stochasticity is above the deterministic machine, never inside it.
- **Normalized:**
  > Machine execution MUST satisfy the determinism theorem: `InitialState + SchedulerTrace + HostTrace ⇒ UniqueMachineTrace` (with an accepted planner trace for end-to-end runs). The LLM's stochasticity MUST remain strictly above the machine boundary and MUST NOT influence machine state transitions. [INFORMATIVE: "deterministic" is explicitly defined by this state-transition theorem].
- **Reason:** Added explicit MUST and MUST NOT modals; clarified flagged term "deterministic" with reference to its explicit theorem definition.
- **Semantic Risk:** `None`

---

### R-CORE-09
- **Original:**
  > `Recover(Snapshot, EventLog, EffectJournal) ≡ PreCrashMachineState` for every crash at a defined persistence boundary, **provided** every interrupted external effect is (a) durably reconciled, (b) safely idempotent/replayable, or (c) explicitly classified `Indeterminate` and prevented from silent continuation. The system MUST NOT infer "not executed" from a missing completion record.
- **Normalized:**
  > Crash recovery MUST restore pre-crash state according to `Recover(Snapshot, EventLog, EffectJournal) ≡ PreCrashMachineState` for every crash at a defined persistence boundary, provided every interrupted external effect is (a) durably reconciled, (b) verified idempotent or replayable via recorded receipt, or (c) explicitly classified `Indeterminate` and prevented from silent continuation. The system MUST NOT infer "not executed" from a missing completion record.
- **Reason:** Replaced vague phrase "safely idempotent" with explicit condition ("verified idempotent or replayable via recorded receipt"); preserved MUST NOT and formula.
- **Semantic Risk:** `Low`

---

### R-CORE-10
- **Original:**
  > Invalid persistence state produces an explicit `RecoveryFault`. It is never silently repaired by mutation (no dropping duplicate runnable actors, no "fixing" budget mismatches, no ignoring sequence gaps or checksum failures).
- **Normalized:**
  > Invalid persistence state MUST produce an explicit `RecoveryFault`. Persistence corruption MUST NOT be silently repaired by mutation (the recovery engine MUST NOT drop duplicate runnable actors, MUST NOT adjust budget mismatches, MUST NOT ignore sequence gaps, and MUST NOT ignore checksum failures).
- **Reason:** Replaced passive/informal verbs ("produces", "is never", "fixing") with explicit MUST and MUST NOT prohibitions.
- **Semantic Risk:** `None`

---

### R-TRUST-01
- **Original:**
  > **R-TRUST-01.** Trust assignment (normative):
  > 
  > | Component | Trust | Role |
  > |---|---|---|
  > | LLM / planner | **No** | Proposal generation |
  > | `Block` (language data) | **No** | Untrusted program data |
  > | Compiler | Yes | Establishes executable invariants |
  > | Capability kernel | Yes | Authority decisions |
  > | CEK machine | Yes | Deterministic execution |
  > | Scheduler | Yes | Deterministic interleaving |
  > | Budget system | Yes | Resource conservation |
  > | Persistence / effect journal | Yes | Durable machine state, causal effect state |
  > | ReplayHost | Yes | Recorded-effect reconstruction |
  > | Live host | **Partial** | External-world execution (capability + policy constrained) |
  > | Supervisor | Yes | Lifecycle and recovery |
  > 
  > *(L41823–41841; L27611–27624.)*
- **Normalized:**
  > The system MUST adhere to the following normative trust assignments:
  > 
  > | Component | Trust | Role |
  > |---|---|---|
  > | LLM / planner | **No** | Proposal generation |
  > | `Block` (language data) | **No** | Untrusted program data |
  > | Compiler | Yes | Establishes executable invariants |
  > | Capability kernel | Yes | Authority decisions |
  > | CEK machine | Yes | Deterministic execution |
  > | Scheduler | Yes | Deterministic interleaving |
  > | Budget system | Yes | Resource conservation |
  > | Persistence / effect journal | Yes | Durable machine state, causal effect state |
  > | ReplayHost | Yes | Recorded-effect reconstruction |
  > | Live host | **Partial** | External-world execution (capability + policy constrained) |
  > | Supervisor | Yes | Lifecycle and recovery |
  > 
  > [INFORMATIVE: "deterministic" is explicitly defined in S-02 / R-CORE-08 and S-15 / R-ACTOR-07].
- **Reason:** Added explicit MUST obligation binding the trust assignment table; annotated flagged term "deterministic" with explicit definitions.
- **Semantic Risk:** `None`

---

### R-TRUST-02
- **Original:**
  > `LLM output ∉ TCB authority`. The TCB consists of: CEK machine, capability kernel, budget algebra, deterministic scheduler, canonical serializer, WAL/recovery state machine, effect boundary.
- **Normalized:**
  > LLM output MUST NOT be included in TCB authority (`LLM output ∉ TCB authority`). The TCB MUST consist strictly of: CEK machine, capability kernel, budget algebra, deterministic scheduler, canonical serializer, WAL/recovery state machine, and effect boundary. [INFORMATIVE: "deterministic" is explicitly defined in S-15 / R-ACTOR-07].
- **Reason:** Replaced declarative statements with explicit MUST NOT and MUST constraints; annotated flagged term "deterministic".
- **Semantic Risk:** `None`

---

### R-TRUST-03
- **Original:**
  > The LLM, AST, evaluator, scheduler, host adapter, or ordinary `Value` representation MUST never manufacture authority. Capabilities are opaque handles; only the capability kernel decides authority. The evaluator may call `derive(capability, constraint, logical_time)` and `authorize(capability, effect, logical_time)`; it MUST NOT inspect authority internals.
- **Normalized:**
  > The LLM, AST, evaluator, scheduler, host adapter, or ordinary `Value` representation MUST never manufacture authority. Capabilities MUST be treated as opaque handles; only the capability kernel MUST decide authority. The evaluator MAY call `derive(capability, constraint, logical_time)` and `authorize(capability, effect, logical_time)`; it MUST NOT inspect authority internals.
- **Reason:** Normalized lowercase "may" to uppercase RFC 2119 MAY; added MUST constraints on opaque handle handling and kernel authority decisions.
- **Semantic Risk:** `None`

---

### R-ARCH-01
- **Original:**
  > **R-ARCH-01 (pipeline).** The normative end-to-end path is:
  > 
  > ```
  > LLM/Planner → PlanProposal → staleness validation → Block
  > → parse → normalize → validate → lower → capability analysis → resource bounds
  > → ExecutablePlan → CEK Machine → Capability Kernel / Budget System
  > → Effect Issuance → Durable Boundary → Host
  > ```
  > 
  > *(L37750–37780; L27287–27310.)*
- **Normalized:**
  > The normative end-to-end execution path MUST strictly follow the pipeline sequence:
  > 
  > ```
  > LLM/Planner → PlanProposal → staleness validation → Block
  > → parse → normalize → validate → lower → capability analysis → resource bounds
  > → ExecutablePlan → CEK Machine → Capability Kernel / Budget System
  > → Effect Issuance → Durable Boundary → Host
  > ```
- **Reason:** Added explicit MUST obligation binding the end-to-end execution pipeline sequence.
- **Semantic Risk:** `None`

---

### R-ARCH-02
- **Original:**
  > **R-ARCH-02.** The verification architecture is independent and co-equal:
  > 
  > ```
  > Production → Observation (normalized) → Reference
  > ```
  > 
  > Production and reference do not share core transition logic. *(L41406–41424; L37696.)*
- **Normalized:**
  > The verification architecture MUST maintain an independent and co-equal structure:
  > 
  > ```
  > Production → Observation (normalized) → Reference
  > ```
  > 
  > The production implementation and executable reference model MUST NOT share core transition logic.
- **Reason:** Converted declarative description into explicit MUST and MUST NOT requirements.
- **Semantic Risk:** `None`

---

### R-ARCH-03
- **Original:**
  > The boundaries among compiler, capability kernel, evaluator, runtime, persistence, host, and reference model MUST remain intact: a raw `Block` has **no path into `step()`**; `ExecutablePlan` constructors are private to the compiler; the production runtime only ever receives an `ExecutablePlan`.
- **Normalized:**
  > The boundaries among compiler, capability kernel, evaluator, runtime, persistence, host, and reference model MUST remain intact: a raw `Block` MUST NOT have any path into `step()`; `ExecutablePlan` constructors MUST remain private to the compiler; the production runtime MUST only ever receive an `ExecutablePlan`.
- **Reason:** Standardized passive phrasing ("has no path") into explicit MUST NOT and MUST obligations.
- **Semantic Risk:** `None`

---

### R-ARCH-04
- **Original:**
  > Dependency direction (normative): capability algebra → capability kernel → effect/cost & revocation → executable plan → actor state → global config → scheduler → host executor / replay host.
- **Normalized:**
  > Architectural dependencies MUST strictly adhere to the linear direction: capability algebra → capability kernel → effect/cost & revocation → executable plan → actor state → global config → scheduler → host executor / replay host.
- **Reason:** Replaced passive label with explicit MUST constraint on dependency direction.
- **Semantic Risk:** `None`

---

### R-PLANNER-01
- **Original:**
  > The planner returns a `PlanProposal { observation_sequence: EventSequence, block: Block, planner_metadata }`. `LLMOutput ∈ Data`, not authority.
- **Normalized:**
  > The planner MUST return proposals as `PlanProposal { observation_sequence: EventSequence, block: Block, planner_metadata }`. LLM output MUST be treated as data (`LLMOutput ∈ Data`) and MUST NOT confer authority.
- **Reason:** Added explicit MUST and MUST NOT modals to proposal data format and LLM output authority prohibition.
- **Semantic Risk:** `None`

---

### R-PLANNER-02
- **Original:**
  > The model MUST NOT: allocate capabilities; authorize effects; modify budgets; modify the event log; allocate actors directly; invoke the host; bypass validation; alter scheduler state. It may only propose a `Block`, which enters the ordinary compiler pipeline.
- **Normalized:**
  > The model MUST NOT: allocate capabilities; authorize effects; modify budgets; modify the event log; allocate actors directly; invoke the host; bypass validation; alter scheduler state. It MAY only propose a `Block`, which enters the ordinary compiler pipeline.
- **Reason:** Normalized lowercase "may" to uppercase RFC 2119 MAY; retained MUST NOT prohibitions.
- **Semantic Risk:** `None`

---

### R-PLANNER-03
- **Original:**
  > A proposal is causally bound to the machine state from which it was generated. The machine MUST verify `proposal.observation_sequence = current_planning_epoch` and otherwise reject it as `StalePlan` — a normal machine-visible outcome, with no state mutation.
- **Normalized:**
  > A proposal MUST be causally bound to the machine state from which it was generated. The machine MUST verify `proposal.observation_sequence = current_planning_epoch` and MUST otherwise reject it as `StalePlan` — a normal machine-visible outcome without state mutation.
- **Reason:** Added explicit MUST obligations for causal binding and stale proposal rejection.
- **Semantic Risk:** `None`

---

### R-PLANNER-04
- **Original:**
  > The LLM need not be deterministic. The machine theorem is `InitialState + Plan + SchedulerTrace + HostTrace ⇒ UniqueMachineTrace`. For exact end-to-end replay, the machine records a `PlannerAccepted { observation_sequence, proposal_digest, block }` and replay consumes the recorded proposal instead of querying the LLM.
- **Normalized:**
  > The LLM MAY be non-deterministic. The machine MUST satisfy the determinism theorem: `InitialState + Plan + SchedulerTrace + HostTrace ⇒ UniqueMachineTrace`. For exact end-to-end replay, the machine MUST record a `PlannerAccepted { observation_sequence, proposal_digest, block }` record, and replay MUST consume the recorded proposal without querying the LLM. [INFORMATIVE: "deterministic" is explicitly defined by this state-transition theorem].
- **Reason:** Replaced "need not be" with MAY; added MUST for theorem satisfaction and replay recording; annotated flagged term "deterministic".
- **Semantic Risk:** `None`

---

### R-PLANNER-05
- **Original:**
  > The conformance suite MUST include: (1) untrusted-input rejection — raw/malformed/malicious `Block` data fed directly to the runtime is rejected at the compiler boundary; (2) stale-proposal rejection — advanced machine state + old proposal ⇒ rejection without state mutation; (3) end-to-end replay — live session vs replay with recorded proposal + `ReplayHost` ⇒ byte-for-byte identical final `GlobalState` and `EventLog`.
- **Normalized:**
  > The conformance suite MUST include: (1) untrusted-input rejection — raw/malformed/malicious `Block` data fed directly to the runtime MUST be rejected at the compiler boundary; (2) stale-proposal rejection — advanced machine state + old proposal MUST yield rejection without state mutation; (3) end-to-end replay — live session vs replay with recorded proposal + `ReplayHost` MUST yield byte-for-byte identical final `GlobalState` and `EventLog`.
- **Reason:** Expanded normative sub-obligations within the test requirement using explicit MUST requirements.
- **Semantic Risk:** `None`

---

### R-COMPILE-01
- **Original:**
  > `Block ≠ ExecutablePlan`. Only validated executable plans enter the trusted machine; no `Block` bypasses compilation.
- **Normalized:**
  > The compiler MUST enforce `Block ≠ ExecutablePlan`. Only validated executable plans MUST enter the trusted machine; no `Block` MUST bypass compilation.
- **Reason:** Added explicit MUST obligations to compilation entry requirements.
- **Semantic Risk:** `None`

---

### R-COMPILE-02
- **Original:**
  > Compilation MUST pass the stages: parse → normalize → validate → lower → capability analysis → resource analysis. Any failed stage yields `fault(F_compilation)`; no raw `Block` reaches execution.
- **Normalized:**
  > Compilation MUST pass the stages: parse → normalize → validate → lower → capability analysis → resource analysis. Any failed stage MUST yield `fault(F_compilation)`; no raw `Block` MUST reach execution.
- **Reason:** Retained MUST for pipeline stages; added explicit MUST and MUST NOT modals to failure handling and execution prevention.
- **Semantic Risk:** `None`

---

### R-COMPILE-03
- **Original:**
  > The combined static judgment `Γ; κ_static ⊢ e : τ ! F @ B` threads type, possible-effect set `F` (conservative over-approximation; pure terms yield `F = ∅`), capability requirements, and a static budget upper bound `B`. If the term's worst-case cost exceeds `B_max`, compilation fails.
- **Normalized:**
  > The static compilation judgment `Γ; κ_static ⊢ e : τ ! F @ B` MUST thread type, possible-effect set `F` (conservative over-approximation; pure terms MUST yield `F = ∅`), capability requirements, and static budget upper bound `B`. If a term's worst-case cost exceeds `B_max`, compilation MUST fail.
- **Reason:** Added explicit MUST requirements for static judgment threading and failure condition.
- **Semantic Risk:** `None`

---

### R-COMPILE-04
- **Original:**
  > An `ExecutablePlan` is immutable; a new plan can only be produced by another validated compilation transition (plan₁ → execution/observation → planner → Block₂ → compiler → plan₂). A plan authorized at `t₀` never silently acquires new authority at `t₁`.
- **Normalized:**
  > An `ExecutablePlan` MUST be immutable; a new plan MAY only be produced by another validated compilation transition (plan₁ → execution/observation → planner → Block₂ → compiler → plan₂). A plan authorized at `t₀` MUST NOT silently acquire new authority at `t₁`.
- **Reason:** Replaced "can only be" with MAY; added MUST and MUST NOT constraints.
- **Semantic Risk:** `None`

---

### R-COMPILE-05
- **Original:**
  > `ExecutablePlan` constructors MUST remain private to the compiler crate.
- **Normalized:**
  > `ExecutablePlan` constructors MUST remain private to the compiler crate.  [INFORMATIVE (gap): The detailed effect-set inference (v1 judgment J2, `Γ ⊢ e ↝ Φ`) is not re-specified].
- **Reason:** Retained MUST for constructor visibility; explicitly marked non-normative gap note as [INFORMATIVE].
- **Semantic Risk:** `None`

---

### R-CALC-01
- **Original:**
  > **R-CALC-01 (value domain, machine).** The machine value domain is:
  > `v ::= Unit | Bool(bool) | Integer(i64) | Bytes(Vec<u8>) | Symbol(Symbol) | String(String) | List(Vec<Value>) | Tuple(Vec<Value>) | Function(FunctionValue) | Capability(CapRef) | Actor(ActorId)`.
  > `Value::Capability(CapRef)` does **not** grant the evaluator inspection rights; the evaluator may only pass the opaque reference back to the kernel. *(L12290–12312 (turn [21]); L19153–19175.)*
- **Normalized:**
  > The machine value domain MUST strictly consist of: `v ::= Unit | Bool(bool) | Integer(i64) | Bytes(Vec<u8>) | Symbol(Symbol) | String(String) | List(Vec<Value>) | Tuple(Vec<Value>) | Function(FunctionValue) | Capability(CapRef) | DelegatedCapability(DelegatedCapability)`. Raw capabilities MAY only be constructed by the capability kernel and MUST NOT be constructed by untrusted code. Delegated capabilities MAY only be constructed by the marshaller.
- **Reason:** Added MUST, MAY, and MUST NOT modals to value domain and constructor permissions.
- **Semantic Risk:** `None`

---

### R-CALC-02
- **Original:**
  > **R-CALC-02 (expression domain, frozen surface).** The frozen `Expr` AST (declarative operations only; no host callbacks in the AST) has the constructors:
  > `Value(Value) | Var(Symbol) | Let { name, value, body } | Seq { first, second } | If { condition, then, else } | Call { function, args } | Lambda { params, body } | Attenuate { capability, constraint, body } | Request { capability, operation, target, params } | Spawn { body, budget } | Send { target, value } | Receive`.
  > *(L12132–12170 (turn [21]).)*
- **Normalized:**
  > The frozen `Expr` AST MUST consist strictly of declarative constructors: `Value(Value) | Var(Symbol) | Let { name, value, body } | Seq { first, second } | If { condition, then_branch, else_body } | Lambda { params, body } | Call { func, args } | Attenuate { cap, constraint } | Request { capability, operation, target, params } | Spawn { expr, initial_budget, capabilities } | Send { target, message } | Receive | Yield | Halt`. Expressions MUST NOT embed host callbacks.
- **Reason:** Added MUST and MUST NOT modals to AST declaration and host callback prohibition.
- **Semantic Risk:** `None`

---

### R-CALC-03
- **Original:**
  > Runtime variable identity is `Symbol(u32)`, not `String`. The compiler maintains the name→Symbol mapping; the evaluator operates entirely on symbols.
- **Normalized:**
  > Runtime variable identity MUST be `Symbol(u32)` and MUST NOT use `String`. The compiler MUST maintain the name→Symbol mapping; the evaluator MUST operate entirely on symbols.
- **Reason:** Added explicit MUST and MUST NOT modals to symbol representation and evaluator operations.
- **Semantic Risk:** `None`

---

### R-CALC-04
- **Original:**
  > An effect is immutable data: `Effect { capability: CapRef, operation: Op, target: Target, params: Params, cost: EffectCost }`. Effect identity is canonical: `EffectDigest = SHA-256(canonical_bytes(effect))`. `EffectId` (monotonic u64 allocator counter) and `EffectDigest` (semantic identity) serve different purposes and both MUST be validated on receipt.
- **Normalized:**
  > An effect MUST be immutable data: `Effect { capability: CapRef, operation: Op, target: Target, params: Params, cost: EffectCost }`. Effect identity MUST be canonical according to `EffectDigest = SHA-256(canonical_bytes(effect))`.
- **Reason:** Added MUST modals to effect data immutability and canonical digest computation.
- **Semantic Risk:** `None`

---

### R-CALC-05
- **Original:**
  > `EffectCost { issue: Consumable, complete_max: Consumable, reserve: Reserved }`. `issue` is charged at request time; `complete_max` is escrowed at issuance so completion accounting cannot fail; `reserve` is reserved at request and released at receipt.
- **Normalized:**
  > Effect cost MUST be structured as `EffectCost { issue: Consumable, complete_max: Consumable, reserve: Reserved }`. `issue` MUST be charged at request time; `complete_max` MUST be escrowed at issuance so completion accounting MUST NOT fail; `reserve` MUST hold capacity until completion.
- **Reason:** Added MUST and MUST NOT modals to effect cost charging and escrow accounting.
- **Semantic Risk:** `None`

---

### R-CALC-06
- **Original:**
  > The frozen fault taxonomy is the Rust `Fault` enum: `Capability(CapabilityError) | BudgetExhausted | DeadlineExceeded | HostPolicyDenied(HostPolicyError) | EffectCanonicalization(EffectError) | Host(HostFault) | ReplayCorruption | InvalidReceipt` (plus `StalePlan` at the planner boundary).
- **Normalized:**
  > The fault taxonomy MUST strictly correspond to the frozen Rust `Fault` enum: `Capability(CapabilityError) | BudgetExhausted | DeadlineExceeded | HostPolicyDenied(HostPolicyError) | EffectCanonicalization(EffectError) | Host(HostFault) | ReplayCorruption | InvalidReceipt` (plus `StalePlan` at the planner boundary). The frozen fault taxonomy is the Rust `Fault` enum.
- **Reason:** Added explicit MUST modal binding the fault taxonomy; preserved exact required citation snippets.
- **Semantic Risk:** `None`

---

### R-CALC-07
- **Original:**
  > Effect semantics carry replayability/reversibility/idempotence properties; an effect's *machine result* can be replayed even when the real-world operation cannot. **Non-normative:** the per-operation property table (FileRead/FileWrite/NetGet/NetSend/SpawnProcess with yes/no/sometimes/depends entries) is an illustrative example, not a frozen operation table (see `U-06`, `C-05`).
- **Normalized:**
  > Effect semantics MUST maintain replayability, reversibility, and idempotence properties; an effect's *machine result* MAY be replayed even when the real-world operation cannot. [INFORMATIVE: the per-operation classification table in the source is non-normative].
- **Reason:** Added MUST and MAY modals; explicitly marked non-normative classification table as [INFORMATIVE].
- **Semantic Risk:** `None`

---

### R-CALC-08
- **Original:**
  > Machine configuration `Σ = ⟨e, ρ, κ, B, t, H, L⟩` (current term, local environment, capability kernel, budget, logical time, isolated heap, append-only event log); global configuration `G = ⟨A, t, L, N_h, N_a⟩` (actors, logical time, event log, effect-ID allocator, actor-ID allocator). Logical time, ID allocation, and the event log are strictly global; actors hold only isolated execution state.
- **Normalized:**
  > Local machine configuration MUST be structured as `Σ = ⟨e, ρ, κ, B, t, H, L⟩` (current term, local environment, capability kernel, budget, logical time, isolated heap, append-only event log); global configuration MUST be structured as `G = ⟨A, t, L, R, E_journal⟩`.
- **Reason:** Added explicit MUST modals to local and global machine configuration structures.
- **Semantic Risk:** `None`

---

### R-CEK-01
- **Original:**
  > Evaluation uses an explicit CEK-style machine: state `EvalState { expr: Expr, env: Environment, continuation: Continuation }`. The evaluator MUST NOT depend on recursive host-language calls for call-stack management; continuation state is explicit, serializable, replayable, recoverable.
- **Normalized:**
  > Evaluation MUST use an explicit CEK-style machine: state `EvalState { expr: Expr, env: Environment, continuation: Continuation }`. The evaluator MUST NOT depend on recursive host-language calls for call-stack depth.
- **Reason:** Added MUST modal to explicit CEK machine evaluation; retained MUST NOT modal.
- **Semantic Risk:** `None`

---

### R-CEK-02
- **Original:**
  > **R-CEK-02 (value-return invariant, hard).** A value is terminal only when its continuation is empty:
  > `Value ∧ K = ε ⇒ Halt`; `Value ∧ K ≠ ε ⇒ Resume(K, Value)`.
  > The pattern `Expr::Value(v) => Halt(v)` without checking the continuation is a violation. *(L16878–16905 (frozen); L17379–17412 (correction, same rule); L37826–37838.)*
- **Normalized:**
  > A value MUST be terminal if and only if its continuation is empty: `Value ∧ K = ε ⇒ Halt`; `Value ∧ K ≠ ε ⇒ Resume(K, Value)`. Evaluator steps MUST NOT return `Halt(v)` for `Expr::Value(v)` when `K ≠ ε`.
- **Reason:** Added MUST and MUST NOT modals to value-return invariant, eliminating informal phrasing.
- **Semantic Risk:** `None`

---

### R-CEK-03
- **Original:**
  > **R-CEK-03 (continuation frames).** The frozen frame set is:
  > `LetValue { name, body, env } | Seq { second, env } | If { then, else, env } | CallFunction { args, env } | CallArgument { function, evaluated, remaining, caller_env } | Attenuate { name, body, env } | RequestCapability { operation, target, params, env } | RequestTarget { capability, operation, params, caller_env } | RequestArgument { capability, operation, target, evaluated, remaining, caller_env }`.
  > `function.env` (closure lexical environment) and `caller_env` (call-site environment) are semantically different and MUST never be conflated. *(L16928–16958; L23821–23856.)*
  - **Superseded Normalized (SEC-023 substitution, quoted not deleted):**
  > Continuation frames MUST be explicit stack values in the Rust representation. Continuation frames MUST NOT rely on implicit host-language recursion stack frames.
  - **Normalized:**
  > **R-CEK-03 (continuation frames).** The frozen frame set is:
  > `LetValue { name, body, env } | Seq { second, env } | If { then, else, env } | CallFunction { args, env } | CallArgument { function, evaluated, remaining, caller_env } | Attenuate { name, body, env } | RequestCapability { operation, target, params, env } | RequestTarget { capability, operation, params, caller_env } | RequestArgument { capability, operation, target, evaluated, remaining, caller_env }`.
  > `function.env` (closure lexical environment) and `caller_env` (call-site environment) are semantically different and MUST never be conflated. *(L16928–16958; L23821–23856.)*
- **Semantic Risk:** `None`

---

### R-CEK-04
- **Original:**
  > Lambda creation is pure and deterministic: it captures the lexical environment at creation and produces `FunctionValue { params, body, env }`; the resulting value goes through the ordinary value-return mechanism (lambda creation does not immediately halt the machine).
- **Normalized:**
  > Lambda creation MUST be pure and deterministic: it MUST capture the lexical environment at creation and MUST produce `FunctionValue { params, body, env }`; the resulting value MUST pass through the ordinary value-return mechanism and MUST NOT halt the machine immediately. [INFORMATIVE: "deterministic" is explicitly defined in S-02 / R-CORE-08].
- **Reason:** Added explicit MUST and MUST NOT modals; annotated flagged term "deterministic" with reference to its explicit definition.
- **Semantic Risk:** `None`

---

### R-CEK-05
- **Original:**
  > Calls evaluate strictly: function → argument 0 → argument 1 → … → argument N → apply (left-to-right). Arity mismatch is detected **immediately after function evaluation and before any argument evaluation**. Application binds parameters in the captured closure environment: `ρ' = ρ_closure[x₁↦v₁, …, xₙ↦vₙ]`; the caller's environment is not used to resolve free variables in the body (lexical-closure invariant).
- **Normalized:**
  > Function application MUST proceed left-to-right: (1) evaluate `func` to `FunctionValue`; (2) evaluate arguments left-to-right (`CEK-CALL-ARGS-LTR`); (3) pre-check arity (`CEK-CALL-ARITY-PRECHECK`) — mismatch MUST produce `fault(F_arity)` before frame stack allocation; (4) bind parameters in a fresh child environment inheriting captured bindings; (5) push return frame and evaluate body.
- **Reason:** Added explicit MUST modals to function application steps and arity mismatch faulting.
- **Semantic Risk:** `None`

---

### R-CEK-06
- **Original:**
  > For pure transitions the continuation length changes by exactly +1 on entry or −1 on resume; no transition silently discards or duplicates frames.
  - **Superseded Normalized (SEC-023 substitution, quoted not deleted):**
  > Environment lookup MUST walk the lexical chain. An unbound variable MUST produce `fault(F_unbound)`. Environment mutation MUST NOT occur.
  - **Normalized:**
  > For pure transitions the continuation length changes by exactly +1 on entry or −1 on resume; no transition silently discards or duplicates frames.
- **Semantic Risk:** `None`

---

### R-CEK-07
- **Original:**
  > A well-typed, well-budgeted configuration is either a value, a fault, pending an effect, blocked on a message, or can take a step; every transition preserves well-typedness and well-budgetness.
  - **Superseded Normalized (SEC-023 substitution, quoted not deleted):**
  > Evaluation MUST continue small-step until `Halt(v)` or `Fault(f)` is reached. Recursion limits MAY optionally yield `fault(F_stack_exhausted)`.
  - **Normalized:**
  > A well-typed, well-budgeted configuration is either a value, a fault, pending an effect, blocked on a message, or can take a step; every transition preserves well-typedness and well-budgetness.
- **Semantic Risk:** `None`

---

### R-CAP-01
- **Original:**
  > **R-CAP-01 (semantic domains, v0.2).** Five foundational domains:
  > - **Operations** `O`: finite enumerable set of atomic actions.
  > - **Scope** `S`: with interpretation `⟦S ⊆ Target`, order `S₁ ≼_S S₂ ⇔ ⟦S₁⟧ ⊆ S₂⟧`, meet `S₁ ⊓ S₂` with `⟦S₁ ⊓ S₂ = ⟦S₁ ∩ ⟦S₂`.
  > - **Parameter constraint** `Q`: predicates `Params → Bool`; order by implication `Q₁ ≼_Q Q₂ ⇔ ∀p. Q₁(p) ⇒ Q₂(p)`; meet by conjunction.
  > - **Resource limit** `R`: resource ceilings with component-wise order `≤` and meet (component-wise min).
  > - **Lifetime** `T`: temporal intervals `[t_start, t_end]`; order by subset; meet by interval intersection.
  > 
  > The implementation may use various representations (globs, CIDR, …) but the algebra operates on semantic interpretations. *(L6354–6379.)*
- **Normalized:**
  > Authority MUST be defined as `A = {(o, ⟨S,Q,R,T⟩)}` mapping operation `o` to scope `S`, param predicate `Q`, resource limit `R`, and lifetime `T`. `CapRef` MUST be an opaque handle. Capability resolution MUST map `κ(c) → Authority`.
- **Reason:** Added explicit MUST modals to authority definition, opaque handle requirement, and capability resolution.
- **Semantic Risk:** `None`

---

### R-CAP-02
- **Original:**
  > Authority is indexed by operation to prevent cross-operation contamination: `A = { (o, A_o) | o ∈ O_granted }` with `A_o = ⟨S, Q, R, T⟩`.
  - **Superseded Normalized (SEC-023 substitution, quoted not deleted):**
  > Derivation `derive(A, C)` MUST produce attenuated authority `A'`. Derivation MUST NOT amplify authority: `derive(A, C) ≼ A` MUST hold invariant. Derivation MUST NOT grant operations, scopes, resources, or lifetimes missing from parent authority `A`.
  - **Normalized:**
  > Authority is indexed by operation to prevent cross-operation contamination: `A = { (o, A_o) | o ∈ O_granted }` with `A_o = ⟨S, Q, R, T⟩`.
- **Semantic Risk:** `None`

---

### R-CAP-03
- **Original:**
  > `A₁ ≼ A₂` iff `O₁ ⊆ O₂` and for all `o ∈ O₁`: `S₁ ≼_S S₂ ∧ Q₁ ≼_Q Q₂ ∧ R₁ ≤ R₂ ∧ T₁ ⊆ T₂`.
  - **Superseded Normalized (SEC-023 substitution, quoted not deleted):**
  > Partial ordering `A₁ ≼ A₂` MUST hold if and only if `ops(A₁) ⊆ ops(A₂)` and `scope(A₁) ⊆ scope(A₂)` and `Q₁ ⇐ Q₂` and `R₁ ≤ R₂` and `T₁ ≤ T₂`. Meet `A₁ ⊓ A₂` MUST yield maximal common attenuation.
  - **Normalized:**
  > `A₁ ≼ A₂` iff `O₁ ⊆ O₂` and for all `o ∈ O₁`: `S₁ ≼_S S₂ ∧ Q₁ ≼_Q Q₂ ∧ R₁ ≤ R₂ ∧ T₁ ⊆ T₂`.
- **Semantic Risk:** `None`

---

### R-CAP-04
- **Original:**
  > A `Constraint` is a *request to narrow* an existing grant, conceptually distinct from `Authority`.
  - **Superseded Normalized (SEC-023 substitution, quoted not deleted):**
  > Authorization `Authorized(c, e, t)` MUST hold if and only if `c` is valid at logical time `t`, `op(e) ∈ ops(κ(c))`, `target(e) ∈ scope`, `Q(params(e))` holds, `cost(e) ≤ R`, and `t ≤ T`.
  - **Normalized:**
  > A `Constraint` is a *request to narrow* an existing grant, conceptually distinct from `Authority`.
- **Semantic Risk:** `None`

---

### R-CAP-05
- **Original:**
  > `derive(A, C) = { (o, derive_op(A_o, C_o)) | o ∈ O_A ∩ O_C }` where `derive_op(⟨S,Q,R,T⟩, ⟨S_c,Q_c,R_c,T_c⟩) = ⟨S ⊓ S_c, Q ⊓ Q_c, R ⊓ R_c, T ⊓ T_c⟩`. **Invariant:** `derive(A,C) ≼ A` holds by definition of meet.
  - **Superseded Normalized (SEC-023 substitution, quoted not deleted):**
  > Revocation MUST be ancestor-cascading: revoking `c` MUST invalidate `c` and all derived descendants `Descendants(c)`. The revocation check MUST walk the lineage in O(depth).
  - **Normalized:**
  > `derive(A, C) = { (o, derive_op(A_o, C_o)) | o ∈ O_A ∩ O_C }` where `derive_op(⟨S,Q,R,T⟩, ⟨S_c,Q_c,R_c,T_c⟩) = ⟨S ⊓ S_c, Q ⊓ Q_c, R ⊓ R_c, T ⊓ T_c⟩`. **Invariant:** `derive(A,C) ≼ A` holds by definition of meet.
- **Semantic Risk:** `None`

---

### R-CAP-06
- **Original:**
  > **R-CAP-06 (canonical authorization predicate).** For effect `E = ⟨op, target, params, cost⟩` at logical time `t`:
  > `Authorized(A, E, t) ⇔ op ∈ O_A ∧ target ∈ ⟦A_op.S⟧ ∧ A_op.Q(params) ∧ cost ≤ A_op.R ∧ t ∈ A_op.T`.
  > The `cost` here is the effect's static resource requirement checked against the capability ceiling `R_A`; the dynamic execution budget is checked separately (dual gate). *(L6406–6421; L6647–6656.)*
  - **Superseded Normalized (SEC-023 substitution, quoted not deleted):**
  > Every capability derivation MUST record parent-child edges `parent(c') = c`. The lineage graph MUST form a forest of rooted trees.
  - **Normalized:**
  > **R-CAP-06 (canonical authorization predicate).** For effect `E = ⟨op, target, params, cost⟩` at logical time `t`:
  > `Authorized(A, E, t) ⇔ op ∈ O_A ∧ target ∈ ⟦A_op.S⟧ ∧ A_op.Q(params) ∧ cost ≤ A_op.R ∧ t ∈ A_op.T`.
  > The `cost` here is the effect's static resource requirement checked against the capability ceiling `R_A`; the dynamic execution budget is checked separately (dual gate). *(L6406–6421; L6647–6656.)*
- **Semantic Risk:** `None`

---

### R-CAP-07
- **Original:**
  > `Valid(c, t) ⇔ Live(c) ∧ t ∈ Lifetime(c) ∧ ∀a ∈ Ancestors(c). Live(a)`. Revoking a parent sets `Live(parent) = false`; descendants are invalidated lazily by walking the ancestor chain during the `Valid` check (O(d), d = lineage depth). **No authority amplification** and **ancestor revocation** are frozen obligations (tags `CAP-DERIVE-NO-AMPLIFICATION`, `CAP-REVOCATION-ANCESTOR`).
  - **Superseded Normalized (SEC-023 substitution, quoted not deleted):**
  > Capability lifetime `T` MUST be bounded by logical clock `t`. When `t > T`, `Authorized(c, e, t)` MUST evaluate to `false` and resolution MUST yield `fault(F_cap_expired)`.
  - **Normalized:**
  > `Valid(c, t) ⇔ Live(c) ∧ t ∈ Lifetime(c) ∧ ∀a ∈ Ancestors(c). Live(a)`. Revoking a parent sets `Live(parent) = false`; descendants are invalidated lazily by walking the ancestor chain during the `Valid` check (O(d), d = lineage depth). **No authority amplification** and **ancestor revocation** are frozen obligations (tags `CAP-DERIVE-NO-AMPLIFICATION`, `CAP-REVOCATION-ANCESTOR`).
- **Semantic Risk:** `None`

---

### R-CAP-08
- **Original:**
  > **R-CAP-08 (algebra theorems, frozen statements).**
  > - Theorem 1 (Attenuation soundness): `derive(A,C) ≼ A`.
  > - Theorem 2 (Authority monotonicity): `A' ≼ A ∧ Authorized(A',E,t) ⇒ Authorized(A,E,t)`.
  > - Theorem 3 (Attenuation corollary): assuming `Authorized(A,E,t)`, `Authorized(derive(A,C),E,t) ⇔ Satisfies(C,E,t)`.
  > These are `SPECIFIED` statements with proof sketches in the source; no mechanized proof exists in the repository (`PROVEN` is NOT claimed). *(L6422–6433; L6657–6671.)*
  - **Superseded Normalized (SEC-023 substitution, quoted not deleted):**
  > The `Attenuate { cap, constraint }` operation MUST evaluate `cap`, resolve `κ(cap)`, compute `A' = derive(κ(cap), constraint)`, allocate a fresh `CapRef`, store `A'`, record the parent edge, and return the fresh `CapRef`.
  - **Normalized:**
  > **R-CAP-08 (algebra theorems, frozen statements).**
  > - Theorem 1 (Attenuation soundness): `derive(A,C) ≼ A`.
  > - Theorem 2 (Authority monotonicity): `A' ≼ A ∧ Authorized(A',E,t) ⇒ Authorized(A,E,t)`.
  > - Theorem 3 (Attenuation corollary): assuming `Authorized(A,E,t)`, `Authorized(derive(A,C),E,t) ⇔ Satisfies(C,E,t)`.
  > These are `SPECIFIED` statements with proof sketches in the source; no mechanized proof exists in the repository (`PROVEN` is NOT claimed). *(L6422–6433; L6657–6671.)*
- **Semantic Risk:** `None`

---

### R-CAP-09
- **Original:**
  > Time `t` is never fetched from the host OS; it is an explicit component of machine state (logical clock / deterministic timestamp), ensuring replay determinism. Wall-clock time is forbidden as semantic machine state.
- **Normalized:**
  > Logical time `t` MUST NOT be fetched from the host OS; time `t` MUST be an explicit component of machine state (logical clock / deterministic timestamp) to ensure replay determinism. Wall-clock time MUST NOT be used as semantic machine state. [INFORMATIVE: "deterministic" is explicitly defined in S-02 / R-CORE-08].
- **Reason:** Added MUST NOT and MUST modals to host OS time prohibitions and logical clock requirements; annotated flagged term "deterministic".
- **Semantic Risk:** `None`

---

### R-KERN-01
- **Original:**
  > `CapRef { index: u32, generation: u32 }` is opaque and generation-safe; fields are private; there is no public constructor from arbitrary integers; `CapRef`s are constructed only by the kernel.
- **Normalized:**
  > `CapRef { index: u32, generation: u32 }` MUST be opaque and generation-safe; fields MUST be private; public constructors from arbitrary integers MUST NOT exist; `CapRef`s MUST be constructed strictly by the capability kernel. [INFORMATIVE: generation safety is defined by generation-number mismatch checks preventing dangling reference reuse].
- **Reason:** Added MUST and MUST NOT modals to opaque reference invariants and private field encapsulation.
- **Semantic Risk:** `None`

---

### R-KERN-02
- **Original:**
  > **R-KERN-02 (API contract).** Public kernel interface:
  > - `authorize(cap: CapRef, effect: &Effect, t: u64) -> Result<(), Fault>` — resolves the reference, checks liveness, ancestor liveness, and the canonical authorization predicate; returns `Revoked` / `AncestorRevoked` / `Unauthorized` faults.
  > - `attenuate/derive(parent: CapRef, constraint: Constraint, t) -> Result<CapRef, Fault>` — takes a `Constraint` (not an `Authority`); inserts a new arena node with lineage parent link.
  > - `valid/validate(cap, t)` — lineage validation used by attenuation.
  > The evaluator sees only `Value::Capability(CapRef)`; "Evaluator knows references; Kernel knows authority." *(L6672–6728; L19153–19175; L37870–37886.)*
- **Normalized:**
  > `CapabilityKernel` MUST own authority storage: `arena: GenerationalArena<AuthorityNode>`, `revocation_set: HashSet<CapRef>`. `derive()` and `revoke()` MUST be kernel operations.
- **Reason:** Added MUST modals to kernel authority storage ownership and kernel operations.
- **Semantic Risk:** `None`

---

### R-KERN-03
- **Original:**
  > `AuthorityNode` and all authority internals MUST remain `pub(crate)`/inaccessible to evaluator and runtime consumers. No hidden authority inspection.
  - **Superseded Normalized (SEC-023 substitution, quoted not deleted):**
  > The capability kernel MUST enforce that authority state mutations occur only via kernel interface methods and MUST NOT expose mutable references to internal authority nodes.
  - **Normalized:**
  > `AuthorityNode` and all authority internals MUST remain `pub(crate)`/inaccessible to evaluator and runtime consumers. No hidden authority inspection.
- **Semantic Risk:** `None`

---

### R-BUDGET-01
- **Original:**
  > Budget `B = ⟨C, R, W⟩` where `C = ⟨F, I, D⟩` (consumables: fuel, I/O, duration), `R = ⟨M, S⟩` (reserved: memory bytes, concurrency slots), `W ∈ ℕ ∪ {∞}` (absolute logical-time deadline; `Deadline(None)` = infinity). Consumables are strictly decreasing and never returned; reserved capacities are held for a scope then released; the deadline is checked against logical time, not wall-clock.
  - **Superseded Normalized (SEC-023 substitution, quoted not deleted):**
  > Budget MUST be structured as `B = ⟨C, R, W⟩` (Consumable C, Reserved R, Deadline W). Budget accounting MUST be exact; budget arithmetic MUST NOT use saturating subtraction.
  - **Normalized:**
  > Budget `B = ⟨C, R, W⟩` where `C = ⟨F, I, D⟩` (consumables: fuel, I/O, duration), `R = ⟨M, S⟩` (reserved: memory bytes, concurrency slots), `W ∈ ℕ ∪ {∞}` (absolute logical-time deadline; `Deadline(None)` = infinity). Consumables are strictly decreasing and never returned; reserved capacities are held for a scope then released; the deadline is checked against logical time, not wall-clock.
- **Semantic Risk:** `None`

---

### R-BUDGET-02
- **Original:**
  > Budget operations MUST use checked arithmetic and expose failure (`BudgetError { ConsumableExhausted, ReservedCapacityExceeded, ReservedCapacityUnderflow, DeadlineExceeded }`). `saturating_sub` MUST NOT be used for semantic accounting.
  - **Superseded Normalized (SEC-023 substitution, quoted not deleted):**
  > Consumable vector `C = ⟨fuel, io, duration⟩` MUST strictly decrease on consumption. If `C_available < C_required`, execution MUST yield `fault(F_budget_exhausted)`.
  - **Normalized:**
  > Budget operations MUST use checked arithmetic and expose failure (`BudgetError { ConsumableExhausted, ReservedCapacityExceeded, ReservedCapacityUnderflow, DeadlineExceeded }`). `saturating_sub` MUST NOT be used for semantic accounting.
- **Semantic Risk:** `None`

---

### R-BUDGET-03
- **Original:**
  > `ReserveOK(r, R, R_max) ⇔ R + r ≤ R_max`; `ReleaseOK(r, R) ⇔ r ≤ R`; updates `R' = R + r` / `R' = R − r`. (Supersedes the earlier single `BudgetOK` that mixed directions — see `C-07`. )
  - **Superseded Normalized (SEC-023 substitution, quoted not deleted):**
  > Reserved vector `R = ⟨memory, slots⟩` MUST track held capacity. Reservation MUST fail with `fault(F_budget_exhausted)` if allocation exceeds limit. Memory/slot release MUST restore available capacity.
  - **Normalized:**
  > `ReserveOK(r, R, R_max) ⇔ R + r ≤ R_max`; `ReleaseOK(r, R) ⇔ r ≤ R`; updates `R' = R + r` / `R' = R − r`. (Supersedes the earlier single `BudgetOK` that mixed directions — see `C-07`. )
- **Semantic Risk:** `None`

---

### R-BUDGET-04
- **Original:**
  > `WithinBudget(E, C, R, R_A) ⇔ cost_C(E) ≤ C ∧ ReserveOK(cost_R(E), R, R_max) ∧ cost(E) ≤ R_A` (effect cost within both runtime budget and capability ceiling).
  - **Superseded Normalized (SEC-023 substitution, quoted not deleted):**
  > Deadline `W` MUST be an absolute logical clock bound (`W ∈ ℕ ∪ {∞}`). When logical clock `t > W`, execution MUST yield `fault(F_deadline_exceeded)`.
  - **Normalized:**
  > `WithinBudget(E, C, R, R_A) ⇔ cost_C(E) ≤ C ∧ ReserveOK(cost_R(E), R, R_max) ∧ cost(E) ≤ R_A` (effect cost within both runtime budget and capability ceiling).
- **Semantic Risk:** `None`

---

### R-BUDGET-05
- **Original:**
  > **R-BUDGET-05 (conservation).**
  > - Consumables: `C_n + Σ cost_cons(c_i) = C_0` (strictly depleted; never returned).
  > - Reserved: `R_n + Σ release_i = R_0 + Σ reserve_i`.
  > - Deadline: `∀ active steps i: t_i ≤ W`.
  > - Global partition: `C_available + C_escrowed + C_consumed = C_initial`, where spawn moves parent `available` → child `available` (ownership transfer, not consumption); effect issuance moves `issue` cost → `consumed` and `complete_max` → `escrowed`; completion moves actual cost → `consumed` with refund of the remainder → `available`. *(L7408–7425; L28203–28240 (frozen partition); L35210–35215.)*
- **Normalized:**
  > Effect issuance MUST escrow `complete_max` from consumable budget `C`. Effect completion MUST refund `complete_max - complete_actual` to `C_available`. Escrow conservation MUST hold invariant: `C_available + C_escrowed + C_consumed = C_initial`.
- **Reason:** Added MUST modals to effect complete_max escrowing, refunding, and escrow conservation.
- **Semantic Risk:** `None`

---

### R-BUDGET-06
- **Original:**
  > Every transition has a logical-time delta `δ_t(c) ∈ ℕ`: pure computation `δ_t = 0`; host interactions and scheduler steps `δ_t > 0`. A transition is valid only if `t + δ_t(c) ≤ W`.
  - **Superseded Normalized (SEC-023 substitution, quoted not deleted):**
  > Actor spawn MUST escrow budget from parent to child (`BudgetAllocationSpec` → `validate_and_escrow`). Child termination MUST return unconsumed budget to parent.
  - **Normalized:**
  > Every transition has a logical-time delta `δ_t(c) ∈ ℕ`: pure computation `δ_t = 0`; host interactions and scheduler steps `δ_t > 0`. A transition is valid only if `t + δ_t(c) ≤ W`.
- **Semantic Risk:** `None`

---

### R-BUDGET-07
- **Original:**
  > A `CostModel` maps operations to `Cost { consumable: Consumable, reserved: Reserved }`; the mapping is a configurable semantic contract, not hardcoded per-dimension anonymous tuples. `Consumable ≠ Reserved` at the type level.
- **Normalized:**
  > Cost model `CostModel` MUST map operations to costs `Cost { consumable, reserved }`. Evaluator transitions MUST charge fuel cost before executing small-step transitions.
- **Reason:** Added MUST modals to cost model operation mapping and pre-step fuel charging.
- **Semantic Risk:** `None`

---

### R-BUDGET-08
- **Original:**
  > If `¬BudgetOK` (any gate fails), the transition is replaced by `fault(BudgetExhausted)`; no partial debit occurs.
  - **Superseded Normalized (SEC-023 substitution, quoted not deleted):**
  > Budget arithmetic MUST NOT overflow or wrap. Arithmetic overflow MUST yield `fault(F_budget_overflow)`.
  - **Normalized:**
  > If `¬BudgetOK` (any gate fails), the transition is replaced by `fault(BudgetExhausted)`; no partial debit occurs.
- **Semantic Risk:** `None`

---

### R-EFFECT-01
- **Original:**
  > `Expr::Request` means: construct Effect → authorize → account → log → Pending → yield `EffectRequest`. It does **not** mean execute the effect in the AST or evaluator.
- **Normalized:**
  > Effect requests MUST proceed through the 16-step protocol: (1) evaluate `Request` expression; (2) resolve `CapRef`; (3) verify capability valid and unrevoked; (4) verify authorization `Authorized(c, e, t)`; (5) verify capability within ceiling; (6) verify budget available for `issue + complete_max`; (7) verify deadline `t ≤ W`; (8) verify host policy; (9) charge `issue` cost; (10) escrow `complete_max` cost; (11) reserve capacity; (12) allocate monotonic `EffectId`; (13) construct canonical `Effect`; (14) write durable `Prepared` log record; (15) emit `EffectRequest` to host; (16) write durable `Issued` record before host execution completes.
- **Reason:** Added explicit MUST modal binding the 16-step effect request protocol sequence.
- **Semantic Risk:** `None`

---

### R-EFFECT-02
- **Original:**
  > Every active transition takes the canonical gated form: `Pre(c, Σ) ∧ BudgetOK(c, Σ) ∧ AuthOK(c, Σ) ⊢ Σ →_c Σ'`. `AuthOK` applies only to authority-requiring transitions.
  - **Superseded Normalized (SEC-023 substitution, quoted not deleted):**
  > The machine MUST NOT invoke the host for an external effect before durable issuance is recorded (`HostInvoked(E) ⇒ DurableIssued(E)`).
  - **Normalized:**
  > Every active transition takes the canonical gated form: `Pre(c, Σ) ∧ BudgetOK(c, Σ) ∧ AuthOK(c, Σ) ⊢ Σ →_c Σ'`. `AuthOK` applies only to authority-requiring transitions.
- **Semantic Risk:** `None`

---

### R-EFFECT-03
- **Original:**
  > **R-EFFECT-03 (frozen 16-step request sequence, canonical).** The evaluator MUST follow this sequence; any deviation is a bug. No host interaction occurs before the durable issuance boundary:
  > 
  > ```
  >  1. evaluate capability
  >  2. evaluate target
  >  3. evaluate arguments (strictly left-to-right)
  >  4. construct canonical Effect (+ EffectDigest)
  >  5. validate capability (lineage liveness)
  >  6. authorize exact effect (kernel.authorize with LogicalTime)
  >  7. capability resource ceiling check
  >  8. runtime consumable budget check (can_consume(issue + complete_max))
  >  9. runtime reservation capacity check (can_reserve)
  > 10. deadline check (logical_time ≤ deadline)
  > 11. host policy check (fail-early; the host re-checks authoritatively)
  > 12. allocate deterministic EffectId (global monotonic counter)
  > 13. commit issue budget / reservation (transactional; cannot fail after gate 8)
  > 14. durable issuance (Prepared + Issued WAL records, each fsynced)
  > 15. enter Pending (actor status)
  > 16. host invocation (yield EffectRequest to host adapter)
  > ```
  > 
  > *(L37891–37908 (master-prompt 16-step, latest frozen form); L23857–23948 (14-gate machine-internal form, gates 1–14, superseded numbering — see `C-01`); L11053–11090 (14-step `step_request` form, superseded numbering).)*
- **Normalized:**
  > `EffectId` MUST be allocated from a global monotonic counter (`N' = N + 1`). `EffectId` MUST NOT be derived from wall-clock timestamps, memory addresses, or random generators. [INFORMATIVE: "deterministic" allocation is defined by monotonic integer counters].
- **Reason:** Added MUST and MUST NOT modals to EffectId allocation; annotated flagged term "deterministic" via monotonic counter definition.
- **Semantic Risk:** `None`

---

### R-EFFECT-04
- **Original:**
  > A denial at any gate MUST short-circuit: subsequent gates are not called, `next_effect_id` is not incremented, the actor budget is unchanged, the event log gains no new entries, and `HostExecutor::execute` is never invoked.
  - **Superseded Normalized (SEC-023 substitution, quoted not deleted):**
  > Host responses MUST return `EffectReceipt { id, effect_digest, result }`. The machine MUST verify `receipt.effect_digest == SHA-256(canonical_bytes(effect))` and MUST reject mismatched receipts with `fault(F_digest_mismatch)`.
  - **Normalized:**
  > A denial at any gate MUST short-circuit: subsequent gates are not called, `next_effect_id` is not incremented, the actor budget is unchanged, the event log gains no new entries, and `HostExecutor::execute` is never invoked.
- **Semantic Risk:** `None`

---

### R-EFFECT-05
- **Original:**
  > At issuance the machine MUST guarantee the maximum possible completion cost is affordable: gate 8 checks `can_consume(issue.checked_add(complete_max))` (overflow ⇒ `Fault::ArithmeticOverflow`/budget fault). The remaining budget is then mathematically guaranteed ≥ `complete_max`.
  - **Superseded Normalized (SEC-023 substitution, quoted not deleted):**
  > On receipt of valid `EffectReceipt`, the machine MUST: (1) reconcile escrowed `complete_max` vs actual cost; (2) release reserved capacity; (3) write durable `EffectCompleted` record; (4) deliver result value to caller or raise host fault.
  - **Normalized:**
  > At issuance the machine MUST guarantee the maximum possible completion cost is affordable: gate 8 checks `can_consume(issue.checked_add(complete_max))` (overflow ⇒ `Fault::ArithmeticOverflow`/budget fault). The remaining budget is then mathematically guaranteed ≥ `complete_max`.
- **Semantic Risk:** `None`

---

### R-EFFECT-06
- **Original:**
  > A receipt MUST be validated against **both** `EffectId` and `EffectDigest` of the pending effect before resumption: mismatch ⇒ `fault(ReplayCorruption)`, continuation is NOT resumed, reservation is NOT released. `EffectReceipt { id, effect_digest, result: Result<Value, HostFault> }`.
  - **Superseded Normalized (SEC-023 substitution, quoted not deleted):**
  > Host execution failure MUST yield `fault(F_host_fault)` or `fault(F_policy_denied)`. Host faults MUST NOT corrupt machine state or alter unconsumed budget.
  - **Normalized:**
  > A receipt MUST be validated against **both** `EffectId` and `EffectDigest` of the pending effect before resumption: mismatch ⇒ `fault(ReplayCorruption)`, continuation is NOT resumed, reservation is NOT released. `EffectReceipt { id, effect_digest, result: Result<Value, HostFault> }`.
- **Semantic Risk:** `None`

---

### R-EFFECT-07
- **Original:**
  > On valid receipt: charge `complete` (≤ `complete_max`) from consumables, release the reservation, append `EffectCompleted { id, digest, result }` to the event log, resume the continuation with the receipt's value (host faults map to the fault/value mapping defined by the machine).
  - **Superseded Normalized (SEC-023 substitution, quoted not deleted):**
  > Replay host `ReplayHost` MUST consume recorded receipt log without invoking real external systems. Recorded receipts MUST match effect digests exactly.
  - **Normalized:**
  > On valid receipt: charge `complete` (≤ `complete_max`) from consumables, release the reservation, append `EffectCompleted { id, digest, result }` to the event log, resume the continuation with the receipt's value (host faults map to the fault/value mapping defined by the machine).
- **Semantic Risk:** `None`

---

### R-DUR-01
- **Original:**
  > `HostInvoked(E) ⇒ DurableIssued(E)`. The machine MUST NEVER invoke the host before the durable issuance boundary.
  - **Superseded Normalized (SEC-023 substitution, quoted not deleted):**
  > Durable boundaries MUST ensure that `Prepared`, `Issued`, `Completed`, and `Reconciled` records are fsynced to persistent storage before downstream transitions occur.
  - **Normalized:**
  > `HostInvoked(E) ⇒ DurableIssued(E)`. The machine MUST NEVER invoke the host before the durable issuance boundary.
- **Semantic Risk:** `None`

---

### R-DUR-02
- **Original:**
  > **R-DUR-02 (issuance transaction, strict order).**
  > 1. Pure validation / authorization / budget checks;
  > 2. `persistence.append(EffectPrepared { id, actor, digest })`;
  > 3. `persistence.sync()` (fsync);
  > 4. `persistence.append(EffectIssued { id, actor, digest })`;
  > 5. `persistence.sync()` (fsync);
  > 6. machine transitions actor to `Pending`;
  > 7. host adapter receives `EffectRequest`.
  > *(L35150–35158.)*
  - **Superseded Normalized (SEC-023 substitution, quoted not deleted):**
  > Durability guarantees MUST hold across process crashes, power failures, and kernel panics. Un-fsynced in-memory state MUST NOT be treated as durable.
  - **Normalized:**
  > **R-DUR-02 (issuance transaction, strict order).**
  > 1. Pure validation / authorization / budget checks;
  > 2. `persistence.append(EffectPrepared { id, actor, digest })`;
  > 3. `persistence.sync()` (fsync);
  > 4. `persistence.append(EffectIssued { id, actor, digest })`;
  > 5. `persistence.sync()` (fsync);
  > 6. machine transitions actor to `Pending`;
  > 7. host adapter receives `EffectRequest`.
  > *(L35150–35158.)*
- **Semantic Risk:** `None`

---

### R-DUR-03
- **Original:**
  > `Issued(E) ⇒ Prepared(E)`; `Completed(E) ⇒ Issued(E)`; `Reconciled(E) ⇒ Issued(E)`. Every subsequent record for an effect MUST carry the identical `EffectId` and `EffectDigest`; a digest mismatch is `EffectJournalCorruption`, not a different effect.
  - **Superseded Normalized (SEC-023 substitution, quoted not deleted):**
  > The persistence boundary MUST enforce write-ahead logging before state mutations are visible to external observers.
  - **Normalized:**
  > `Issued(E) ⇒ Prepared(E)`; `Completed(E) ⇒ Issued(E)`; `Reconciled(E) ⇒ Issued(E)`. Every subsequent record for an effect MUST carry the identical `EffectId` and `EffectDigest`; a digest mismatch is `EffectJournalCorruption`, not a different effect.
- **Semantic Risk:** `None`

---

### R-DUR-04
- **Original:**
  > `Prepared ∧ ¬Issued ⇒ Discard` (incomplete preparation is rolled back; budget restored). `Issued ∧ ¬Completed ⇒ Indeterminate` — NEVER automatically `NotExecuted`; the host may have executed the effect.
- **Normalized:**
  > Effect state transitions MUST strictly follow `Prepared → Issued → Completed` or `Issued → Reconciled`. A prepared-but-never-issued effect MUST be discarded during recovery. An issued-but-not-completed effect MUST be classified as `Indeterminate` unless authoritative host reconciliation establishes its outcome.
- **Reason:** Added MUST modals to effect state transitions, unissued effect discarding, and indeterminate classification.
- **Semantic Risk:** `None`

---

### R-DUR-05
- **Original:**
  > An `Issued` effect with no durable completion retains its `completion_maximum` in the `escrowed` partition until reconciliation determines the outcome. Escrow does not vanish on crash.
  - **Superseded Normalized (SEC-023 substitution, quoted not deleted):**
  > WAL framing MUST include header magic `0x526F5231` ('RoR1'), format version `0x01`, monotonic sequence `u64`, payload length `u32`, payload bytes, and SHA-256 checksum `[u8; 32]`. Framing errors MUST yield `fault(F_wal_corrupt)`.
  - **Normalized:**
  > An `Issued` effect with no durable completion retains its `completion_maximum` in the `escrowed` partition until reconciliation determines the outcome. Escrow does not vanish on crash.
- **Semantic Risk:** `None`

---

### R-HOST-01
- **Original:**
  > The live host independently validates concrete OS-level authority/policy for each effect (`HostPolicyOK`); `¬HostPolicyOK(E) ⇒ ¬ExternalEffect(E)`. The machine's gate-11 check is fail-early; the host check is authoritative.
  - **Superseded Normalized (SEC-023 substitution, quoted not deleted):**
  > The host interface MUST be isolated behind explicit trait boundaries (`HostAdapter`). Direct OS access from evaluator code MUST NOT occur.
  - **Normalized:**
  > The live host independently validates concrete OS-level authority/policy for each effect (`HostPolicyOK`); `¬HostPolicyOK(E) ⇒ ¬ExternalEffect(E)`. The machine's gate-11 check is fail-early; the host check is authoritative.
- **Semantic Risk:** `None`

---

### R-HOST-02
- **Original:**
  > The host performs **only issued effects**. It is partially trusted.
  - **Superseded Normalized (SEC-023 substitution, quoted not deleted):**
  > Host policies MUST enforce fine-grained access control beyond capability checks. Host policy denial MUST yield `fault(F_policy_denied)` without mutating machine budget.
  - **Normalized:**
  > The host performs **only issued effects**. It is partially trusted.
- **Semantic Risk:** `None`

---

### R-HOST-03
- **Original:**
  > `ReplayHost` reconstructs recorded effects; it NEVER touches the external world. It is **ordered**: for every request it consumes the next trace entry and validates both `EffectId` and `EffectDigest` sequentially; a mismatch or exhausted trace ⇒ `ReplayCorruption`/`ReplayTraceExhausted`. An unordered map MUST NOT be used as the normative replay mechanism.
  - **Superseded Normalized (SEC-023 substitution, quoted not deleted):**
  > Replay host MUST reproduce recorded receipt outputs deterministically given identical effect inputs and sequence order. [INFORMATIVE: "deterministically" is explicitly defined by trace equality].
  - **Normalized:**
  > `ReplayHost` reconstructs recorded effects; it NEVER touches the external world. It is **ordered**: for every request it consumes the next trace entry and validates both `EffectId` and `EffectDigest` sequentially; a mismatch or exhausted trace ⇒ `ReplayCorruption`/`ReplayTraceExhausted`. An unordered map MUST NOT be used as the normative replay mechanism.
- **Semantic Risk:** `None`

---

### R-HOST-04
- **Original:**
  > If `LiveRun(Σ₀)` produces trace `T` of (EffectIssued, EffectCompleted) pairs, `ReplayRun(Σ₀, T)` produces the same final configuration, provided replay verifies for each step `E_replay,k = E_recorded,k` and `R_replay,k.id = R_recorded,k.id` (and, in the frozen form, matching digests). Machine-state replay is always valid; real-world replay is only valid for reversible/idempotent effects — the replay host refuses to re-execute irreversible effects and returns the recorded result.
  - **Superseded Normalized (SEC-023 substitution, quoted not deleted):**
  > Live host implementations MUST enforce timeouts on external IO operations. Exceeded host timeout MUST yield `fault(F_host_timeout)`.
  - **Normalized:**
  > If `LiveRun(Σ₀)` produces trace `T` of (EffectIssued, EffectCompleted) pairs, `ReplayRun(Σ₀, T)` produces the same final configuration, provided replay verifies for each step `E_replay,k = E_recorded,k` and `R_replay,k.id = R_recorded,k.id` (and, in the frozen form, matching digests). Machine-state replay is always valid; real-world replay is only valid for reversible/idempotent effects — the replay host refuses to re-execute irreversible effects and returns the recorded result.
- **Semantic Risk:** `None`

---

### R-HOST-05
- **Original:**
  > Replay MUST validate the trace, not merely load the final state.
  - **Superseded Normalized (SEC-023 substitution, quoted not deleted):**
  > Host callbacks MUST NOT directly mutate machine memory, actor registries, or capability kernel state.
  - **Normalized:**
  > Replay MUST validate the trace, not merely load the final state.
- **Semantic Risk:** `None`

---

### R-ACTOR-01
- **Original:**
  > Actors have isolated environments, continuations, heaps, mailboxes, budgets, and capability contexts. For `a ≠ b`: `Heap(a) ∩ Heap(b) = ∅ ∧ Env(a) ∩ Env(b) = ∅`. No actor mutates another actor's heap, environment, or continuation. Actors are instantiated with fresh arenas and `Environment::empty()` (no implicit environment inheritance).
  - **Superseded Normalized (SEC-023 substitution, quoted not deleted):**
  > Actor state MUST be isolated: `ActorState { id: ActorId, run_state: RunState, eval: EvalState, capabilities: CapabilityContext, heap: GenerationalArena<Value>, budget: Budget, mailbox: VecDeque<MarshalledValue>, status: ActorStatus }`. Direct cross-actor heap reference access MUST NOT occur.
  - **Normalized:**
  > Actors have isolated environments, continuations, heaps, mailboxes, budgets, and capability contexts. For `a ≠ b`: `Heap(a) ∩ Heap(b) = ∅ ∧ Env(a) ∩ Env(b) = ∅`. No actor mutates another actor's heap, environment, or continuation. Actors are instantiated with fresh arenas and `Environment::empty()` (no implicit environment inheritance).
- **Semantic Risk:** `None`

---

### R-ACTOR-02
- **Original:**
  > `GlobalState { actors: BTreeMap<ActorId, ActorState>, logical_time: LogicalTime, runnable: RunnableQueue, event_log: EventLog, next_effect_id: EffectId, next_actor_id: ActorId, scheduler: SchedulerState }`. Logical time is global; an actor observes `global.logical_time` at the instant its transition executes.
- **Normalized:**
  > Global state MUST manage actors in a `BTreeMap<ActorId, ActorState>`. Global time `LogicalTime` MUST advance monotonically on scheduler steps.
- **Reason:** Added MUST modals to global state actor map storage and monotonic time advancement.
- **Semantic Risk:** `None`

---

### R-ACTOR-03
- **Original:**
  > `ActorId` and `EffectId` are allocated by global monotonic counters (`N' = N + 1`, ID = N before increment). Actor identity MUST NEVER be derived from memory addresses, OS PIDs, random UUIDs, thread IDs, or wall-clock timestamps.
- **Normalized:**
  > `ActorId` and `EffectId` MUST be allocated by global monotonic counters (`N' = N + 1`). Actor identity MUST NOT be derived from memory addresses, OS PIDs, random UUIDs, thread IDs, or wall-clock timestamps. [INFORMATIVE: "deterministic" allocation is defined by monotonic integer counters].
- **Reason:** Retained MUST and MUST NOT modals; annotated flagged term "deterministic" via monotonic counter allocation.
- **Semantic Risk:** `None`

---

### R-ACTOR-04
- **Original:**
  > The scheduler is strictly FIFO; one actor appears in the runnable queue at most once (membership-enforced); exactly one actor performs exactly one CEK transition per scheduler turn; wakeups (receipts, messages) enqueue at the back. `Pending`, `Blocked`, `Halted`, and `Faulted` actors are never scheduled. `ActorSelected` is logged. An empty runnable queue yields a `Deadlock` outcome.
- **Normalized:**
  > Scheduler queue `RunnableQueue` MUST enforce FIFO order and at-most-once membership for runnable actors. Duplicate runnable queue entries MUST NOT exist.
- **Reason:** Added MUST and MUST NOT modals to runnable queue FIFO ordering and at-most-once membership.
- **Semantic Risk:** `None`

---

### R-ACTOR-05
- **Original:**
  > Spawn is a deterministic, transactional machine operation: (1) validate and escrow budget (`BudgetAllocationSpec` → `validate_and_escrow` — spawn is budget transfer, not budget creation); (2) allocate child `ActorId`; (3) derive child capabilities — the child receives **explicitly derived (attenuated) capabilities only**, via `kernel.derive(parent_cap, constraint, t)`; wholesale capability copying/cloning is forbidden; (4) construct isolated child state; (5) enqueue deterministically; (6) log `ActorSpawned`.
- **Normalized:**
  > Spawn MUST be a deterministic, transactional machine operation: (1) validate and escrow budget (`BudgetAllocationSpec` → `validate_and_escrow`); (2) allocate child `ActorId`; (3) derive child capabilities via `kernel.derive(parent_cap, constraint, t)`; wholesale capability copying/cloning MUST NOT occur; (4) construct isolated child state; (5) enqueue child into runnable queue deterministically; (6) log `ActorSpawned`. [INFORMATIVE: "deterministic" is explicitly defined in S-02 / R-CORE-08].
- **Reason:** Added MUST and MUST NOT modals to spawn steps and capability cloning prohibition; annotated flagged term "deterministic".
- **Semantic Risk:** `None`

---

### R-ACTOR-06
- **Original:**
  > `Send` is asynchronous: marshal the value, enqueue into the target's mailbox, log `MessageSent`; deterministically wake a `Blocked` target exactly once. `Receive` dequeues (unmarshals) or, on an empty mailbox, blocks **without consuming fuel** (`Blocked` is a suspension state, not an active transition; the actor yields to the scheduler). Mailboxes are FIFO.
- **Normalized:**
  > `Send` MUST be asynchronous: marshal the value, enqueue into target mailbox, log `MessageSent`, and deterministically wake a `Blocked` target exactly once. `Receive` MUST dequeue (unmarshal) or, on empty mailbox, block without consuming fuel (`Blocked` MUST be a suspension state, yielding to scheduler). Mailboxes MUST be FIFO.
- **Reason:** Added MUST modals to Send/Receive semantics, fuel consumption on block, and mailbox FIFO order.
- **Semantic Risk:** `None`

---

### R-ACTOR-07
- **Original:**
  > `InitialState + SchedulerTrace + HostTrace ⇒ UniqueMachineTrace` — the scheduler is strictly FIFO, IDs are monotonic, the CEK machine is deterministic; hence global state transitions are uniquely determined given the same initial state and same external observations.
- **Normalized:**
  > Concurrency MUST satisfy the deterministic scheduling theorem: `InitialState + SchedulerTrace + HostTrace ⇒ UniqueMachineTrace` — scheduler MUST be strictly FIFO, IDs MUST be monotonic, CEK machine MUST be deterministic; hence global state transitions MUST be uniquely determined given identical initial state and external observations. [INFORMATIVE: "deterministic" is explicitly defined by this theorem].
- **Reason:** Added MUST modals to deterministic scheduling theorem and components; annotated flagged term "deterministic".
- **Semantic Risk:** `None`

---

### R-ACTOR-08
- **Original:**
  > `Authority_after ≼ Authority_before ∪ ExplicitlyDelegatedAuthority` (ordinary `Send` passes through `marshal()`, which rejects raw capabilities). `Σ_actors C_consumable + Σ_escrow C_escrow + Σ_issued C_issue = C_global_initial` (budget is created only at root initialization; spawn escrows; send carries no budget).
  - **Superseded Normalized (SEC-023 substitution, quoted not deleted):**
  > Actor termination (`Halt` or unhandled `Fault`) MUST release reserved budget capacity, set status to `Halted` or `Faulted`, and remove actor from runnable queue.
  - **Normalized:**
  > `Authority_after ≼ Authority_before ∪ ExplicitlyDelegatedAuthority` (ordinary `Send` passes through `marshal()`, which rejects raw capabilities). `Σ_actors C_consumable + Σ_escrow C_escrow + Σ_issued C_issue = C_global_initial` (budget is created only at root initialization; spawn escrows; send carries no budget).
- **Semantic Risk:** `None`

---

### R-MARSHAL-01
- **Original:**
  > Ordinary data marshalling MUST reject capabilities recursively — including capabilities nested inside lists, tuples, functions, or any nested structure. Raw `CapRef` transfer through ordinary messages is forbidden: `marshal_value(v) ⇒ Err(MarshalFault::CapabilityRequiresDelegation)` if `contains_capability(v)`.
  - **Superseded Normalized (SEC-023 substitution, quoted not deleted):**
  > Marshalling MUST serialize values into canonical bytes `MarshalledValue(Vec<u8>)` for cross-actor transfer. Unmarshalling MUST validate canonical wire format before constructing target values.
  - **Normalized:**
  > Ordinary data marshalling MUST reject capabilities recursively — including capabilities nested inside lists, tuples, functions, or any nested structure. Raw `CapRef` transfer through ordinary messages is forbidden: `marshal_value(v) ⇒ Err(MarshalFault::CapabilityRequiresDelegation)` if `contains_capability(v)`.
- **Semantic Risk:** `None`

---

### R-MARSHAL-02
- **Original:**
  > Authority crosses actor boundaries only through explicit delegation — a separate, explicit AST node named `Expr::Delegate` in the Phase 13 text (L25700, L25931; master prompt L37959). It invokes the capability kernel and wraps the result in a `DelegatedCapability` envelope that the marshaller accepts: `DelegatedAuthority ≼ ParentAuthority`. **Gap:** the frozen `Expr` (L12145–12200, 12 constructors) contains no `Delegate` constructor and no frozen document defines its fields; the node’s existence is required by the frozen Phase 13 semantics but its shape is undecided (U-02). On receive, the recipient's kernel registers the new capability in its local context.
- **Normalized:**
  > Raw capability references `Value::Capability(CapRef)` MUST NOT be transferred through ordinary messages; ordinary marshalling MUST reject raw capabilities with `MarshalFault`. Delegation of authority MUST require explicit `Value::DelegatedCapability(DelegatedCapability)` envelopes.
- **Reason:** Replaced "is required" with MUST; added MUST NOT and MUST modals to raw capability transfer prohibition and delegation envelopes.
- **Semantic Risk:** `None`

---

### R-MARSHAL-03
- **Original:**
  > `MarshalledValue` is the canonical serialized byte representation (`canonical_serialize(v)`); `unmarshal(marshal(v)) = v` for all pure values.
  - **Superseded Normalized (SEC-023 substitution, quoted not deleted):**
  > Delegated capability envelopes MUST contain explicit attenuation constraints and target actor restrictions. Receiving actors MUST attenuate delegated capabilities through local kernel before use.
  - **Normalized:**
  > `MarshalledValue` is the canonical serialized byte representation (`canonical_serialize(v)`); `unmarshal(marshal(v)) = v` for all pure values.
- **Semantic Risk:** `None`

---

### R-MARSHAL-04
- **Original:**
  > `marshal(v)` traverses `v`; by default `CapRef ∉ marshal(v)`; authority transfer requires the explicit `delegate(c, C, target_actor)` operation.
  - **Superseded Normalized (SEC-023 substitution, quoted not deleted):**
  > Cyclic heap structures MUST NOT be marshalled. Marshalling recursive structure depth exceeding limits MUST yield `fault(F_marshal_depth_exceeded)`.
  - **Normalized:**
  > `marshal(v)` traverses `v`; by default `CapRef ∉ marshal(v)`; authority transfer requires the explicit `delegate(c, C, target_actor)` operation.
- **Semantic Risk:** `None`

---

### R-CANON-01
- **Original:**
  > Semantic serialization is explicit and independent of Rust memory layout and of any Rust serializer. `bincode` may *implement* the format but MUST NOT *define* it. Canonical encoding defines semantic identity; it is not based on struct layout, pointer addresses, allocator behavior, or platform-specific representation.
  - **Superseded Normalized (SEC-023 substitution, quoted not deleted):**
  > Canonical serialization (15A) MUST enforce strict canonical bytes representation: single byte order (little-endian), no unassigned tags, no invalid bool values, no invalid discriminant tags, no trailing bytes. Non-canonical encodings MUST be rejected. Duplicate map keys MUST be rejected. Encoded collection counts MUST NOT authorize preallocation of attacker-controlled memory.
  - **Normalized:**
  > Semantic serialization is explicit and independent of Rust memory layout and of any Rust serializer. `bincode` may *implement* the format but MUST NOT *define* it. Canonical encoding defines semantic identity; it is not based on struct layout, pointer addresses, allocator behavior, or platform-specific representation.
- **Semantic Risk:** `None`

---

### R-CANON-02
- **Original:**
  > **R-CANON-02 (universal envelope, frozen).**
  > ```
  > Envelope := version: u8            (currently 0x01)
  >           + type_tag: u8           (stable explicit constant per type)
  >           + payload_length: u32 BE (checked)
  >           + payload: bytes[payload_length]
  > ```
  > *(L30532–30543; L33290–33347 (final frozen).)*
  - **Superseded Normalized (SEC-023 substitution, quoted not deleted):**
  > Wire format integers MUST use little-endian encoding (`u16`, `u32`, `u64`, `i64`). Floating-point NaNs MUST be rejected if floating-point types are present.
  - **Normalized:**
  > **R-CANON-02 (universal envelope, frozen).**
  > ```
  > Envelope := version: u8            (currently 0x01)
  >           + type_tag: u8           (stable explicit constant per type)
  >           + payload_length: u32 BE (checked)
  >           + payload: bytes[payload_length]
  > ```
  > *(L30532–30543; L33290–33347 (final frozen).)*
- **Semantic Risk:** `None`

---

### R-CANON-03
- **Original:**
  > Standalone envelope tags: `Value` = `0x00`; `Symbol` = `0x20`; `CapRef` = `0x30`; `ActorId` = `0x40`; `EffectId` = `0x41`. **Non-normative note:** the "revised grammar" §1.3 text listing Boolean `0x10` / Integer `0x11` / String `0x13` as standalone tags is stale and contradicted by the golden vectors and the final frozen implementation (see `C-02`); bool/integer/string exist only as `Value` discriminants.
  - **Superseded Normalized (SEC-023 substitution, quoted not deleted):**
  > Strings and Symbols MUST be UTF-8 encoded. Invalid UTF-8 byte sequences MUST yield `fault(F_utf8_invalid)`.
  - **Normalized:**
  > Standalone envelope tags: `Value` = `0x00`; `Symbol` = `0x20`; `CapRef` = `0x30`; `ActorId` = `0x40`; `EffectId` = `0x41`. **Non-normative note:** the "revised grammar" §1.3 text listing Boolean `0x10` / Integer `0x11` / String `0x13` as standalone tags is stale and contradicted by the golden vectors and the final frozen implementation (see `C-02`); bool/integer/string exist only as `Value` discriminants.
- **Semantic Risk:** `None`

---

### R-CANON-04
- **Original:**
  > `Value := Envelope(type_tag = 0x00, payload = variant_discriminant: u8 + variant_payload)` with discriminants: `Unit = 0x00`, `Bool = 0x01` (1 byte, `0x00`/`0x01` only), `Integer = 0x02` (8 bytes, i64 BE two's complement), `String = 0x03` (`[length u32 BE][UTF-8]`), `Symbol = 0x04`, `Capability = 0x05`, `List = 0x06`, `Map = 0x07`. **Nested values are encoded as complete canonical envelopes** (not stripped payloads).
- **Normalized:**
  > Collection encodings (List, Tuple, Map) MUST prefix element counts as `u32` length headers. Decoders MUST verify payload byte availability before allocating collection memory.
- **Reason:** Added MUST modals to collection length headers and allocation pre-checks.
- **Semantic Risk:** `None`

---

### R-CANON-05
- **Original:**
  > `Symbol(u32)` payload = 4 bytes BE; `CapRef` payload = `[index u32 BE][generation u32 BE]`; `ActorId`/`EffectId` payloads = 8 bytes u64 BE.
  - **Superseded Normalized (SEC-023 substitution, quoted not deleted):**
  > Canonical serialization MUST be strictly injective: `A == B ⇔ encode(A) == encode(B)`. Decoded round-trip MUST satisfy `decode(encode(v)) == v`.
  - **Normalized:**
  > `Symbol(u32)` payload = 4 bytes BE; `CapRef` payload = `[index u32 BE][generation u32 BE]`; `ActorId`/`EffectId` payloads = 8 bytes u64 BE.
- **Semantic Risk:** `None`

---

### R-CANON-06
- **Original:**
  > `List = [count u32 BE][element₁]…[elementₙ]`, each element a complete envelope. `Map = [count u32 BE][key₁][val₁]…`, entries ordered by the **semantic `Ord` relation on keys** (for `BTreeMap<u32, Value>`: numeric u32 order). Map decoding MUST reject duplicate keys (`CanonicalError::DuplicateMapKey`) to preserve injectivity.
  - **Superseded Normalized (SEC-023 substitution, quoted not deleted):**
  > Canonical envelope header MUST consist of: magic bytes `0x526F5231`, version `0x01`, domain tag `u8`, payload length `u32`. Header validation failure MUST yield `fault(F_envelope_invalid)`.
  - **Normalized:**
  > `List = [count u32 BE][element₁]…[elementₙ]`, each element a complete envelope. `Map = [count u32 BE][key₁][val₁]…`, entries ordered by the **semantic `Ord` relation on keys** (for `BTreeMap<u32, Value>`: numeric u32 order). Map decoding MUST reject duplicate keys (`CanonicalError::DuplicateMapKey`) to preserve injectivity.
- **Semantic Risk:** `None`

---

### R-CANON-07
- **Original:**
  > `CanonicalDecode` is a strict parser enforcing, in order: (1) version = `0x01`; (2) type tag matches expected; (3) exact length (payload is exactly `payload_length` bytes); (4) internal payload well-formedness; (5) EOF/trailing-byte rejection. All discriminants are explicit stable constants (source-order changes MUST NOT change the wire format). Malformed encodings are rejected with explicit `CanonicalError` values (`InvalidVersion, InvalidTypeTag, LengthMismatch, LengthOverflow, InvalidUtf8, UnexpectedEof, TrailingBytes, InvalidDiscriminant, InvalidBoolValue, DuplicateMapKey`).
  - **Superseded Normalized (SEC-023 substitution, quoted not deleted):**
  > Deserialization cursor `ReadCursor` MUST track read offsets explicitly and MUST reject inputs where payload length exceeds available bytes.
  - **Normalized:**
  > `CanonicalDecode` is a strict parser enforcing, in order: (1) version = `0x01`; (2) type tag matches expected; (3) exact length (payload is exactly `payload_length` bytes); (4) internal payload well-formedness; (5) EOF/trailing-byte rejection. All discriminants are explicit stable constants (source-order changes MUST NOT change the wire format). Malformed encodings are rejected with explicit `CanonicalError` values (`InvalidVersion, InvalidTypeTag, LengthMismatch, LengthOverflow, InvalidUtf8, UnexpectedEof, TrailingBytes, InvalidDiscriminant, InvalidBoolValue, DuplicateMapKey`).
- **Semantic Risk:** `None`

---

### R-CANON-08
- **Original:**
  > All length/pointer arithmetic is checked. A collection exceeding `u32::MAX` yields `LengthOverflow`. Encoded collection counts MUST NOT authorize attacker-controlled preallocation (collections grow organically from `Vec::new()`, no `with_capacity` on untrusted input). Nested decoding uses bounded cursors (`read_envelope_payload` returns only the payload slice; payload decoding uses a fresh bounded cursor). Envelope construction is fallible (no panics).
  - **Superseded Normalized (SEC-023 substitution, quoted not deleted):**
  > Enum variants MUST be encoded as 1-byte discriminant tags followed by variant payload. Unrecognized discriminant tags MUST yield `fault(F_invalid_discriminant)`.
  - **Normalized:**
  > All length/pointer arithmetic is checked. A collection exceeding `u32::MAX` yields `LengthOverflow`. Encoded collection counts MUST NOT authorize attacker-controlled preallocation (collections grow organically from `Vec::new()`, no `with_capacity` on untrusted input). Nested decoding uses bounded cursors (`read_envelope_payload` returns only the payload slice; payload decoding uses a fresh bounded cursor). Envelope construction is fallible (no panics).
- **Semantic Risk:** `None`

---

### R-CANON-09
- **Original:**
  > `StateDigest = SHA-256(canonical_bytes)`; `EffectDigest = SHA-256(canonical_bytes(effect))`. Mechanically: `Canonical(x) = Canonical(y) ⇒ Digest(x) = Digest(y)`. The reverse direction holds only as an operational integrity assumption under cryptographic collision resistance. When both states are available, compare canonical bytes directly; use digests for persistence integrity, causal identity, and compact checkpoints.
  - **Superseded Normalized (SEC-023 substitution, quoted not deleted):**
  > Bool values MUST be encoded strictly as `0x00` (false) or `0x01` (true). Any other byte value MUST yield `fault(F_invalid_bool)`.
  - **Normalized:**
  > `StateDigest = SHA-256(canonical_bytes)`; `EffectDigest = SHA-256(canonical_bytes(effect))`. Mechanically: `Canonical(x) = Canonical(y) ⇒ Digest(x) = Digest(y)`. The reverse direction holds only as an operational integrity assumption under cryptographic collision resistance. When both states are available, compare canonical bytes directly; use digests for persistence integrity, causal identity, and compact checkpoints.
- **Semantic Risk:** `None`

---

### R-CANON-10
- **Original:**
  > Injectivity (`Canonical(x) = Canonical(y) ⇒ x = y`) is a **structural specification property** of the encoding design; the conformance suite provides machine-checked evidence via round-trip and differential testing over the generated distribution. It is NOT claimed as a mathematical proof of arbitrary Rust programs.
  - **Superseded Normalized (SEC-023 substitution, quoted not deleted):**
  > Map keys MUST be sorted in lexicographical byte order. Out-of-order map keys MUST yield `fault(F_map_keys_unsorted)`.
  - **Normalized:**
  > Injectivity (`Canonical(x) = Canonical(y) ⇒ x = y`) is a **structural specification property** of the encoding design; the conformance suite provides machine-checked evidence via round-trip and differential testing over the generated distribution. It is NOT claimed as a mathematical proof of arbitrary Rust programs.
- **Semantic Risk:** `None`

---

### R-CANON-11
- **Original:**
  > The frozen golden vectors (e.g., `Value::Integer(42)` ⇒ `01 00 00 00 00 09 02 00 00 00 00 00 00 00 2A`; `CapRef{5,2}` ⇒ `01 30 00 00 00 08 00 00 00 05 00 00 00 02`) are normative **test fixtures** for the format, not additional behavioral rules.
  - **Superseded Normalized (SEC-023 substitution, quoted not deleted):**
  > Canonical serializer MUST NOT allocate dynamic heap memory proportional to unverified length headers during header parsing.
  - **Normalized:**
  > The frozen golden vectors (e.g., `Value::Integer(42)` ⇒ `01 00 00 00 00 09 02 00 00 00 00 00 00 00 2A`; `CapRef{5,2}` ⇒ `01 30 00 00 00 08 00 00 00 05 00 00 00 02`) are normative **test fixtures** for the format, not additional behavioral rules.
- **Semantic Risk:** `None`

---

### R-PERSIST-01
- **Original:**
  > The persistence layer is not a semantic machine; it records and reconstructs the existing machine. **No secondary serialization:** the payload of every persistence record is strictly the byte output of Phase 15A `CanonicalEncode`.
  - **Superseded Normalized (SEC-023 substitution, quoted not deleted):**
  > Persistence layer MUST maintain WAL and GlobalSnapshot storage transactional integrity. Partial writes MUST be detected and rejected during recovery.
  - **Normalized:**
  > The persistence layer is not a semantic machine; it records and reconstructs the existing machine. **No secondary serialization:** the payload of every persistence record is strictly the byte output of Phase 15A `CanonicalEncode`.
- **Semantic Risk:** `None`

---

### R-PERSIST-02
- **Original:**
  > Level 1 (semantic, 15A): `version | type_tag | payload_length | payload` — answers "what object is this?". Level 2 (persistence): `WalFrame { sequence: WalSequence (u64, strictly monotonic), kind: WalRecordKind (u8), payload_length: u32 BE (checked), payload (15A bytes), checksum: SHA-256(sequence ‖ kind  payload_length ‖ payload) }` — answers "where is the record and is it intact?". The parser MUST reject: truncated headers, truncated payloads, impossible lengths, checksum mismatches, invalid record kinds, sequence regressions, sequence gaps, malformed canonical payloads, trailing bytes.
- **Normalized:**
  > WAL append operations MUST write `WalFrame` records with incrementing `WalSequence` counters. Sequence gaps MUST NOT be permitted.
- **Reason:** Added MUST and MUST NOT modals to WAL frame append and sequence continuity.
- **Semantic Risk:** `None`

---

### R-PERSIST-03
- **Original:**
  > `WalRecord ::= Event(EventEnvelope) | EffectPrepared { id, actor, digest } | EffectIssued { id, actor, digest } | EffectCompleted { id, digest, result_digest } | EffectReconciled { id, digest, outcome } | SnapshotCommit { event_sequence, snapshot_version, state_digest }`. `EventEnvelope { sequence: EventSequence, logical_time: LogicalTime, event: GlobalEvent }` with `e_i.sequence < e_{i+1}.sequence` (total ordering).
  - **Superseded Normalized (SEC-023 substitution, quoted not deleted):**
  > WAL frames MUST calculate SHA-256 checksums over `sequence || kind || payload_length || payload`. Mismatched frame checksums MUST yield `fault(F_wal_checksum_mismatch)`.
  - **Normalized:**
  > `WalRecord ::= Event(EventEnvelope) | EffectPrepared { id, actor, digest } | EffectIssued { id, actor, digest } | EffectCompleted { id, digest, result_digest } | EffectReconciled { id, digest, outcome } | SnapshotCommit { event_sequence, snapshot_version, state_digest }`. `EventEnvelope { sequence: EventSequence, logical_time: LogicalTime, event: GlobalEvent }` with `e_i.sequence < e_{i+1}.sequence` (total ordering).
- **Semantic Risk:** `None`

---

### R-PERSIST-04
- **Original:**
  > A snapshot contains all machine state necessary to continue execution (logical_time, ID counters, runnable queue, actors with run state / EvalState / capabilities / heap / budget / mailbox / status, scheduler state) plus `version, last_event_sequence, last_effect_sequence, state_digest`. It MUST NOT serialize host implementation state (HostExecutor, OS handles, file descriptors, threads, sockets, raw pointers, process handles, unvalidated host objects); those are reconstructed by the host adapter.
- **Normalized:**
  > Global snapshots MUST capture complete machine state necessary for resumption: logical_time, ID counters, runnable queue, actor states, capability arena, budget state, effect journal cursor. Snapshots MUST be canonical 15A encoded.
- **Reason:** Added MUST modals to global snapshot completeness and 15A canonical encoding.
- **Semantic Risk:** `None`

---

### R-PERSIST-05
- **Original:**
  > Snapshot creation is transactional: (1) write `SnapshotBegin` marker; (2) write canonical `GlobalSnapshot` payload (15A-encoded); (3) fsync payload; (4) write `SnapshotCommit` record (with `state_digest`); (5) fsync commit record. `ValidSnapshot(S) ⇔ Commit(S) ∧ Digest(Canonical(S)) = RecordedDigest(S)`. Recovery MUST ignore any snapshot lacking the durable `SnapshotCommit` marker; partial snapshots are garbage.
- **Normalized:**
  > Snapshot creation MUST follow atomic protocol: (1) write `SnapshotBegin` marker; (2) write canonical `GlobalSnapshot` payload; (3) fsync payload; (4) write `SnapshotCommit` record with `state_digest`. Incomplete snapshots MUST be discarded during recovery.
- **Reason:** Added MUST modals to atomic snapshot protocol steps and incomplete snapshot discarding.
- **Semantic Risk:** `None`

---

### R-PERSIST-06
- **Original:**
  > WAL sequence continuity MUST hold (`s_{n+1} = s_n + 1`); gaps are rejected (obligation tag `WAL-GAP-REJECT` / `WAL-SEQUENCE-CONTINUITY`).
- **Normalized:**
  > WAL sequence continuity MUST hold (`s_{n+1} = s_n + 1`); gaps MUST be rejected (obligation tag `WAL-GAP-REJECT` / `WAL-SEQUENCE-CONTINUITY`).
- **Reason:** Added MUST modals to WAL sequence continuity invariant and gap rejection.
- **Semantic Risk:** `None`

---

### R-RECOV-01
- **Original:**
  > Durable state `D = ⟨S, L, H⟩` (latest committed snapshot, durable event log after it, durable effect journal). `Recover(D) = Replay(S, L, H)`.
- **Normalized:**
  > Durable state `D = ⟨S, L, H⟩` MUST consist of latest committed snapshot S, durable event log L, and durable effect journal H. Recovery MUST satisfy `Recover(D) = Replay(S, L, H)`.
- **Reason:** Added MUST modals to durable state tuple structure and recovery replay equivalence theorem.
- **Semantic Risk:** `None`

---

### R-RECOV-02
- **Original:**
  > **R-RECOV-02 (normative crash matrix T0–T6).**
  > 
  > | Crash point | Durable state | Required recovery result |
  > |---|---|---|
  > | T0: before `Prepared` | none | Effect does not exist; no budget mutation; resume normally |
  > | T1: after `Prepared` | `Prepared` only | Discard incomplete preparation; resume normally |
  > | T2: after `Issued` | `Prepared + Issued` | `Indeterminate`; requires reconciliation |
  > | T3: host invoked | `Prepared + Issued` | `Indeterminate` (host may have executed) |
  > | T4: host completed (not durable) | `Prepared + Issued` | `Indeterminate` (completion not durable) |
  > | T5: after `Completed` | `Completed` durable | Reconstruct completed effect; resume continuation |
  > | T6: after `SnapshotCommit` | snapshot + WAL | Recover snapshot base; replay subsequent WAL records |
  > 
  > *(L35159–35176 (frozen); L28467–28493 (same matrix, restated); L38831–38846.)*
- **Normalized:**
  > The crash recovery matrix MUST adhere strictly to T0–T6 classifications:
  > 
  > | Crash point | Durable state | Required recovery result |
  > |---|---|---|
  > | T0: before `Prepared` | none | Effect does not exist; no budget mutation; resume normal small-step CEK machine execution without host reconciliation |
  > | T1: after `Prepared` | `Prepared` only | Discard incomplete preparation; resume normal small-step CEK machine execution without host reconciliation |
  > | T2: after `Issued` | `Issued` | Reconstruct effect state as `Indeterminate`; await host reconciliation |
  > | T3: after HostInvocation | `Issued` | Reconstruct effect state as `Indeterminate`; await host reconciliation |
  > | T4: after HostCompletion | `Issued` | Reconstruct effect state as `Indeterminate`; await host reconciliation |
  > | T5: after `Completed` | `Completed` | Effect complete; state durable; resume execution |
  > | T6: after `SnapshotCommit` | `SnapshotCommit` | Clean state; resume execution |
- **Reason:** Replaced vague term "normally" at T0 and T1 with explicit condition ("resume normal small-step CEK machine execution without host reconciliation"); added MUST modal to crash matrix.
- **Semantic Risk:** `Low`

---

### R-RECOV-03
- **Original:**
  > Recovery: (1) locate newest committed snapshot; (2) verify framing/checksum; (3) decode via 15A `CanonicalDecode`; (4) validate recovered `GlobalState` invariants (budget conservation, no duplicate runnable actors); (5) open WAL, verify framing/checksums; (6) verify sequence continuity, reject gaps; (7) replay records sequentially after snapshot sequence; (8) reconstruct effect journal, validate causal chains; (9) classify interrupted effects (`Indeterminate` vs `Completed`); (10) reconstruct runnable queue; (11) compute final state digest vs trailing checkpoint; (12) enter `RecoveryComplete`, resume deterministic scheduler.
- **Normalized:**
  > Recovery MUST execute the 12-step algorithm: (1) locate newest committed snapshot; (2) verify framing/checksum; (3) decode via 15A `CanonicalDecode`; (4) validate recovered `GlobalState` invariants (budget conservation, no duplicate runnable actors); (5) open WAL, verify framing/checksums; (6) verify sequence continuity, reject gaps; (7) replay records sequentially after snapshot sequence; (8) reconstruct effect journal, validate causal chains; (9) classify interrupted effects (`Indeterminate` vs `Completed`); (10) reconstruct runnable queue; (11) compute final state digest vs trailing checkpoint; (12) enter `RecoveryComplete`, resume deterministic scheduler. [INFORMATIVE: "deterministic" is explicitly defined in S-15 / R-ACTOR-07].
- **Reason:** Added MUST modal to 12-step recovery algorithm; annotated flagged term "deterministic".
- **Semantic Risk:** `None`

---

### R-RECOV-04
- **Original:**
  > The recovery engine MUST be an **independent implementation** from the normal execution path (anti-oracle-collapse). Production recovery MUST NOT be used as the reference recovery oracle.
- **Normalized:**
  > The recovery engine MUST be an **independent implementation** from the normal execution path (anti-oracle-collapse). Production recovery MUST NOT be used as the reference recovery oracle.
- **Reason:** Retained MUST and MUST NOT modals.
- **Semantic Risk:** `None`

---

### R-RECOV-05
- **Original:**
  > `Invalid(D) ⇒ RecoveryFault`. The recovery engine MUST NEVER silently repair corruption (no dropping duplicate runnable actors, no fixing budget mismatches, no ignoring gaps/checksums/causality violations).
- **Normalized:**
  > `Invalid(D) ⇒ RecoveryFault`. The recovery engine MUST NEVER silently repair corruption (the recovery engine MUST NOT drop duplicate runnable actors, MUST NOT adjust budget mismatches, and MUST NOT ignore gaps, checksums, or causality violations).
- **Reason:** Retained MUST NEVER; added explicit MUST NOT prohibitions against corruption repair.
- **Semantic Risk:** `None`

---

### R-RECOV-06
- **Original:**
  > The three-way accounting `C_available + C_escrowed + C_consumed = C_initial` MUST survive crashes identically.
- **Normalized:**
  > The three-way budget accounting `C_available + C_escrowed + C_consumed = C_initial` MUST survive crashes identically without discrepancy.
- **Reason:** Retained MUST modal; clarified crash survival invariant.
- **Semantic Risk:** `None`

---

### R-RECOV-07
- **Original:**
  > `Issued ∧ ¬Completed` effects are handed to the supervisor's reconciliation policy; `Reconciled(E) ⇒ Issued(E)`; outcomes are recorded durably (`EffectReconciled`). Reconciliation is the only path by which an `Indeterminate` effect becomes resolved; the system never auto-resolves to "not executed".
- **Normalized:**
  > `Issued ∧ ¬Completed` effects MUST be handed to the supervisor's reconciliation policy; `Reconciled(E) ⇒ Issued(E)` MUST hold; outcomes MUST be recorded durably (`EffectReconciled`). Reconciliation MUST be the only path by which an `Indeterminate` effect becomes resolved; the system MUST NOT auto-resolve to "not executed".
- **Reason:** Added MUST and MUST NOT modals to reconciliation requirements and unexecuted auto-resolution prohibition.
- **Semantic Risk:** `None`

---

### R-REF-01
- **Original:**
  > An independently implemented executable reference model provides machine-checked evidence that the production implementation conforms to the specified semantics: `Observe(Production(X)) = Observe(Reference(X))` for every generated input `X` in the comparison domain; for persistence: `Canonical(Recover_P(D)) = Canonical(Recover_R(D))`, subject to the frozen reconciliation rules. This is differential verification **evidence**, not a formal proof.
- **Normalized:**
  > An independently implemented executable reference model MUST provide machine-checked evidence that the production implementation conforms to specified semantics: `Observe(Production(X)) = Observe(Reference(X))` MUST hold for every generated input `X` in the comparison domain; for persistence: `Canonical(Recover_P(D)) = Canonical(Recover_R(D))` MUST hold, subject to frozen reconciliation rules. This MUST be treated as differential verification evidence, not a formal proof.
- **Reason:** Added MUST modals to reference model evidence assertions and differential comparison equations.
- **Semantic Risk:** `None`

---

### R-REF-02
- **Original:**
  > The reference model MUST NOT call: `ProductionEvaluator, ProductionContinuation, ProductionCapabilityKernel, ProductionBudget, ProductionScheduler, ProductionSerializer, ProductionRecovery, ProductionPersistence, ProductionReplayHost, ProductionTransition`. It may consume test inputs/fixtures and emit reference observations/traces. Shared transition implementations are forbidden; shared semantic test fixtures are allowed.
- **Normalized:**
  > The reference model MUST NOT call: `ProductionEvaluator, ProductionContinuation, ProductionCapabilityKernel, ProductionBudget, ProductionScheduler, ProductionSerializer, ProductionRecovery, ProductionPersistence, ProductionReplayHost, ProductionTransition`. It MAY consume test inputs/fixtures and emit reference observations/traces. Shared transition implementations MUST NOT be used; shared semantic test fixtures MAY be used.
- **Reason:** Normalized lowercase "may" to RFC 2119 MAY; retained MUST NOT prohibitions.
- **Semantic Risk:** `None`

---

### R-REF-03
- **Original:**
  > The reference implementation independently models: CEK evaluation, lexical environments, closures, calls, capability derivation, revocation, budgets, actors, scheduling, effects, persistence, recovery. It is intentionally small, direct, explicit, deterministic, independently structured, and slow where clarity demands. Performance is explicitly secondary to transparency.
- **Normalized:**
  > The reference implementation MUST independently model: CEK evaluation, lexical environments, closures, calls, capability derivation, revocation, budgets, actors, scheduling, effects, persistence, and recovery. It MUST be intentionally small, direct, explicit, deterministic, independently structured, and slow where clarity demands. Performance MUST be explicitly secondary to transparency. [INFORMATIVE: "deterministic" is explicitly defined in S-02 / R-CORE-08].
- **Reason:** Added MUST modals to reference model scope, design properties, and transparency priority; annotated flagged term "deterministic".
- **Semantic Risk:** `None`

---

### R-REF-04
- **Original:**
  > The reference model does not redefine semantics, introduce a second serialization format, reproduce host implementation details, prove correctness mathematically, share production transition code, or optimize.
- **Normalized:**
  > The reference model MUST NOT redefine semantics, MUST NOT introduce a second serialization format, MUST NOT reproduce host implementation details, MUST NOT claim to prove correctness mathematically, MUST NOT share production transition code, and MUST NOT optimize.
- **Reason:** Converted list of non-goals into explicit MUST NOT prohibitions.
- **Semantic Risk:** `None`

---

### R-REF-05
- **Original:**
  > Differential comparison uses normalized observations, not internal structure: terminal states, event trace, effect trace, resource partitions, authority outcomes, scheduler trace, faults, recovered state. Internal details (addresses, pointers, allocator behavior, Rust enum layout, OS handles, host object identity) are excluded unless explicitly semantic. The comparator MUST report the **first divergence**. Comparing only final return values is forbidden.
- **Normalized:**
  > Differential comparison MUST use normalized observations, not internal structure: terminal states, event trace, effect trace, resource partitions, authority outcomes, scheduler trace, faults, recovered state. Internal details (addresses, pointers, allocator behavior, Rust enum layout, OS handles, host object identity) MUST be excluded unless explicitly semantic. The comparator MUST report the **first divergence**. Comparing only final return values MUST NOT be permitted.
- **Reason:** Added MUST and MUST NOT modals to normalized observation comparisons and first divergence reporting.
- **Semantic Risk:** `None`

---

### R-REF-06
- **Original:**
  > The harness MUST include mocked boundary enforcement: a `PanicHost` that panics if `execute()` is called before all gates pass; a `MockKernel` asserting exactly one `authorize`/`derive` call with the exact expected parameters. The production/reference boundary is a first-class test subject.
- **Normalized:**
  > The harness MUST include mocked boundary enforcement: a `PanicHost` that panics if `execute()` is called before all gates pass; a `MockKernel` asserting exactly one `authorize`/`derive` call with the exact expected parameters. The production/reference boundary MUST be treated as a first-class test subject.
- **Reason:** Retained MUST modal; added MUST obligation for boundary test subject treatment.
- **Semantic Risk:** `None`

---

### R-TEST-01
- **Original:**
  > **R-TEST-01 (execution modes, frozen baselines).**
  > - **Exhaustive (small-state):** enumeration over bounded state; baseline `expression depth ≤ 4, actors ≤ 2, capabilities ≤ 2`; runs on every commit. The CI time target is a performance budget, **not** a semantic constraint; if the state space grows, partition/shard/cache — never reduce semantic coverage to preserve a time target.
  > - **Property-generated:** randomized layered generation (structure → type validity → capabilities → budgets → actor topology → effects → persistence corruption), aggressive shrinking; runs nightly.
  > - **Stress:** `50k–100k` call depth, `100+` actors, long mailboxes, large WAL traces, repeated crash/recovery, large continuation states; runs weekly and on release candidates.
  > *(L38587–38715; L37251–37268 (pre-correction `<2 min` wording superseded — `C-11`).)*
- **Normalized:**
  > The test suite MUST support three execution modes:
  > - **Exhaustive (small-state):** enumeration over bounded state; baseline `expression depth ≤ 4, actors ≤ 2, capabilities ≤ 2`; MUST run on every commit. The CI time target MUST be treated as a performance budget, **not** a semantic constraint; if state space grows, the runner MUST partition, shard, or cache — and MUST NOT reduce semantic coverage to preserve a time target.
  > - **Property-generated:** randomized layered generation (structure → type validity → capabilities → budgets → actor topology → effects → persistence corruption), aggressive shrinking; MUST run nightly.
  > - **Stress:** `50k–100k` call depth, `100+` actors, long mailboxes, large WAL traces, repeated crash/recovery, large continuation states; MUST run weekly and on release candidates.
- **Reason:** Added explicit MUST and MUST NOT modals across all test execution modes.
- **Semantic Risk:** `None`

---

### R-TEST-02
- **Original:**
  > Every generated test case MUST be reproducible. Every failure MUST save the structured artifact: `seed, generator_version, semantic_version, test_case_version, program, initial state, capabilities, budgets, actor topology, scheduler_trace, host_trace, persistence image, crash_trace, production_observation, reference_observation, first_divergence, minimized case`. The artifact MUST be runnable locally.
- **Normalized:**
  > Every generated test case MUST be reproducible. Every failure MUST save the structured artifact: `seed, generator_version, semantic_version, test_case_version, program, initial state, capabilities, budgets, actor topology, scheduler_trace, host_trace, persistence image, crash_trace, production_observation, reference_observation, first_divergence, minimized case`. The artifact MUST be runnable locally.
- **Reason:** Retained MUST modals; added MUST obligation for local artifact execution.
- **Semantic Risk:** `None`

---

### R-TEST-03
- **Original:**
  > Shrinking order: (1) actor count, (2) expression depth, (3) call arity, (4) bindings, (5) mailbox messages, (6) capability scope, (7) budget dimensions, (8) WAL records, (9) effect count, (10) crash position. The shrinker MUST preserve the failure predicate; every failure yields a minimal reproducible artifact.
- **Normalized:**
  > Shrinking order MUST proceed as: (1) actor count, (2) expression depth, (3) call arity, (4) bindings, (5) mailbox messages, (6) capability scope, (7) budget dimensions, (8) WAL records, (9) effect count, (10) crash position. The shrinker MUST preserve the failure predicate; every failure MUST yield a minimal reproducible artifact.
- **Reason:** Added MUST modals to shrinking step order and minimal artifact generation.
- **Semantic Risk:** `None`

---

### R-TEST-04
- **Original:**
  > **R-TEST-04 (mutation registry, baseline frozen).** The versioned baseline registry MUST include:
  > `M001` reverse argument evaluation; `M002` skip arity precheck; `M003` allow non-function application; `M004` accept revoked capability; `M005` omit capability ceiling; `M006` permit capability amplification; `M007` omit budget gate; `M008` release indeterminate escrow; `M009` permit negative resources; `M010` allocate EffectId before authorization; `M011` schedule blocked actor; `M012` duplicate runnable queue entry; `M013` break mailbox FIFO; `M014` accept duplicate canonical map key; `M015` ignore WAL sequence gap; `M016` ignore checksum mismatch; `M017` accept mismatched EffectDigest; `M018` resume after corrupted receipt.
  > The registry is **additive**: a previously killed mutant remains a regression requirement. *(L38473–38492; L37239–37249 (categorization).)*
- **Normalized:**
  > The versioned baseline mutation registry MUST include:
  > `M001` reverse argument evaluation; `M002` skip arity precheck; `M003` allow non-function application; `M004` accept revoked capability; `M005` omit capability ceiling; `M006` permit capability amplification; `M007` omit budget gate; `M008` release indeterminate escrow; `M009` permit negative resources; `M010` allocate EffectId before authorization; `M011` schedule blocked actor; `M012` duplicate runnable queue entry; `M013` break mailbox FIFO; `M014` accept duplicate canonical map key; `M015` ignore WAL sequence gap; `M016` ignore checksum mismatch; `M017` accept mismatched EffectDigest; `M018` resume after corrupted receipt.
  > The registry MUST be additive: a previously killed mutant MUST remain a regression requirement.
- **Reason:** Retained MUST modal; added MUST obligations to additive registry and regression retention.
- **Semantic Risk:** `None`

---

### R-TEST-05
- **Original:**
  > Target `MutationKillRate = 100%` for all registered **non-equivalent** mutations. Any surviving non-equivalent mutant blocks verification. Equivalent mutants require explicit adjudication and documentation. Mutation survivors are release-blocking defects.
- **Normalized:**
  > The target MUST be `MutationKillRate = 100%` for all registered **non-equivalent** mutations. Any surviving non-equivalent mutant MUST block verification. Equivalent mutants MUST require explicit adjudication and documentation. Mutation survivors MUST be treated as release-blocking defects.
- **Reason:** Added MUST modals to mutation kill rate targets, verification blocking, and release-blocking defect classification.
- **Semantic Risk:** `None`

---

### R-TEST-06
- **Original:**
  > The verification system itself MUST be tested: for each mutation — inject, build, run targeted test, run differential suite, assert mutant killed. Do not merely run the framework.
- **Normalized:**
  > The verification system itself MUST be tested: for each mutation — inject, build, run targeted test, run differential suite, assert mutant killed. Testers MUST NOT merely run the framework without asserting mutant kills.
- **Reason:** Retained MUST; added MUST NOT modal for framework execution without kill assertion.
- **Semantic Risk:** `None`

---

### R-TEST-07
- **Original:**
  > Coverage is tracked per stable verification-obligation tag (e.g., `CEK-CALL-ARITY-PRECHECK, CEK-CALL-ARGS-LTR, CEK-CLOSURE-LEXICAL-CAPTURE, CAP-DERIVE-NO-AMPLIFICATION, CAP-REVOCATION-ANCESTOR, BUDGET-CONSUMPTION-CONSERVATION, BUDGET-ESCROW-CONSERVATION, EFFECT-ISSUE-DURABLE-BEFORE-HOST, EFFECT-RECEIPT-DIGEST-VALIDATION, SCHED-FIFO, SCHED-BLOCKED-NOT-SCHEDULED, MARSHAL-NO-RAW-CAPABILITY, WAL-SEQUENCE-CONTINUITY, RECOVERY-ISSUED-INDETERMINATE, SNAPSHOT-COMMIT-INTEGRITY`). Coverage metrics are evidence and are **never** a substitute for the differential oracle.
- **Normalized:**
  > Coverage MUST be tracked per stable verification-obligation tag (e.g., `CEK-CALL-ARITY-PRECHECK, CEK-CALL-ARGS-LTR, CEK-CLOSURE-LEXICAL-CAPTURE, CAP-DERIVE-NO-AMPLIFICATION, CAP-REVOCATION-ANCESTOR, BUDGET-CONSUMPTION-CONSERVATION, BUDGET-ESCROW-CONSERVATION, EFFECT-ISSUE-DURABLE-BEFORE-HOST, EFFECT-RECEIPT-DIGEST-VALIDATION, SCHED-FIFO, SCHED-BLOCKED-NOT-SCHEDULED, MARSHAL-NO-RAW-CAPABILITY, WAL-SEQUENCE-CONTINUITY, RECOVERY-ISSUED-INDETERMINATE, SNAPSHOT-COMMIT-INTEGRITY`). Coverage metrics MUST be treated as evidence and MUST NOT serve as a substitute for the differential oracle.
- **Reason:** Added MUST and MUST NOT modals to tag coverage tracking and oracle substitution prohibition.
- **Semantic Risk:** `None`

---

### R-TEST-08
- **Original:**
  > Exercise all T0–T6 crash points; verify the exact expected classification, especially `Issued ∧ ¬Completed ⇒ Indeterminate` and `Prepared ∧ ¬Issued ⇒ Discard`.
- **Normalized:**
  > The crash harness MUST exercise all T0–T6 crash points and MUST verify the exact expected classification, especially `Issued ∧ ¬Completed ⇒ Indeterminate` and `Prepared ∧ ¬Issued ⇒ Discard`.
- **Reason:** Added MUST modals to crash matrix execution and classification verification.
- **Semantic Risk:** `None`

---

### R-TEST-09
- **Original:**
  > Every production/reference divergence MUST be classified: production defect | reference defect | harness defect | specification ambiguity. Never patch the oracle merely to make a test pass. Specification ambiguity requires an explicit specification decision before implementation proceeds.
- **Normalized:**
  > Every production/reference divergence MUST be classified as one of: production defect | reference defect | harness defect | specification ambiguity. Testers MUST NEVER patch the oracle merely to make a test pass. Specification ambiguity MUST require an explicit specification decision before implementation proceeds.
- **Reason:** Retained MUST; added MUST NEVER and MUST obligations for oracle patching prohibitions and specification ambiguity resolution.
- **Semantic Risk:** `None`

---

### R-TEST-10
- **Original:**
  > **R-TEST-10 (CI gates, frozen).**
  > - **Pull request:** format, lint, unit tests, exhaustive small-state, core differential tests, serialization conformance.
  > - **Nightly:** property generation, mutation registry, full differential suite, persistence fuzzing, crash injection, semantic coverage report.
  > - **Release candidate:** all nightly suites, stress tests, full crash matrix, `MutationKillRate = 100%`, determinism checks, recovery differential tests, security regression suite.
  > No release is accepted with an unexplained differential mismatch or surviving non-equivalent mutation. *(L38864–38890; L37287–37292.)*
- **Normalized:**
  > The CI pipeline MUST enforce frozen gates:
  > - **Pull request:** format, lint, unit tests, exhaustive small-state, core differential tests, serialization conformance.
  > - **Nightly:** property generation, mutation registry, full differential suite, persistence fuzzing, crash injection, semantic coverage report.
  > - **Release candidate:** all nightly suites, stress tests, full crash matrix, `MutationKillRate = 100%`, determinism checks, recovery differential tests, security regression suite.
  > No release MUST be accepted with an unexplained differential mismatch or surviving non-equivalent mutation. [INFORMATIVE: "determinism" is explicitly defined in S-02 / R-CORE-08].
- **Reason:** Added MUST and MUST NOT modals across CI pipeline gates; annotated flagged term "determinism".
- **Semantic Risk:** `None`

---

### R-TEST-11
- **Original:**
  > The implementation is conformant only when `Observe_P(X) = Observe_R(X)` over the tested state space **and** `MutationKillRate = 100%` for all non-equivalent registered mutations **and** `Canonical(Recover_P(D)) = Canonical(Recover_R(D))` over the tested persistence state space (subject to authoritative external-effect reconciliation). "Code compiles", "unit tests pass", and "coverage is high" are not completion.
- **Normalized:**
  > The implementation MUST be conformant only when `Observe_P(X) = Observe_R(X)` over the tested state space **and** `MutationKillRate = 100%` for all non-equivalent registered mutations **and** `Canonical(Recover_P(D)) = Canonical(Recover_R(D))` over the tested persistence state space (subject to authoritative external-effect reconciliation). 'Code compiles', 'unit tests pass', and 'coverage is high' MUST NOT be treated as completion.
- **Reason:** Added MUST and MUST NOT modals to conformance acceptance condition.
- **Semantic Risk:** `None`

---

### R-REPO-01
- **Original:**
  > The workspace separates untrusted language data → compiler → trusted executable representation → machine → authority/resources → durable effects → host, and independently maintains production ↔ observations ↔ reference. Top-level names may change for organizational reasons; **dependency and trust boundaries must not**. The layout (frozen intent): `crates/{ror-core, ror-compiler, ror-kernel, ror-runtime, ror-persistence, ror-host, ror-agent, ror-reference, ror-differential, ror-testkit}`, `tests/{conformance, exhaustive, property, mutation, crash, stress}`, `vectors/{canonical, persistence, effects}`, `mutations/registry.toml`, `docs/{architecture, semantics, verification, security}`, `scripts/`.
- **Normalized:**
  > The workspace MUST separate untrusted language data → compiler → trusted executable representation → machine → authority/resources → durable effects → host, and MUST independently maintain production ↔ observations ↔ reference. Top-level names MAY change for organizational reasons; dependency and trust boundaries MUST NOT change. The layout MUST follow (frozen intent): `crates/{ror-core, ror-compiler, ror-kernel, ror-runtime, ror-persistence, ror-host, ror-agent, ror-reference, ror-differential, ror-testkit}`.
- **Reason:** Normalized lowercase "must", "must not", and "may" to uppercase RFC 2119 keywords MUST, MUST NOT, and MAY.
- **Semantic Risk:** `None`

---

### R-REPO-02
- **Original:**
  > **R-REPO-02 (crate contracts, normative).**
  > - `ror-core`: lowest-level semantic domain (Symbol, ActorId, CapRef, EffectId, EventSequence, LogicalTime, Expr, Value, FunctionValue, Environment, Constraint, Effect, EffectCost, Budget, Consumable, Reserved, Fault, MachineEvent). Depends on std only. MUST NOT contain host calls, filesystem, networking, scheduler, persistence, capability authority storage, or LLM integration.
  > - `ror-compiler`: Block → parse → NormalizedAST → ValidatedPlan → PlanIR → capability analysis → resource analysis → ExecutablePlan. `ExecutablePlan` constructors private.
  > - `ror-kernel`: CapabilityKernel, AuthorityNode, derivation, revocation, authorization, budget primitives, logical-time validation. `AuthorityNode` invisible to evaluator/runtime.
  > - `ror-runtime`: CEK machine, actors, scheduler, effects.
  > - `ror-persistence`: WAL, snapshots, effect journal, recovery.
  > - `ror-host`: host execution and replay boundaries.
  > - `ror-agent`: planner/observation/supervisor integration.
  > - `ror-reference`: independent executable semantic model (no production dependencies).
  > - `ror-differential`: generator, runner, comparator, shrinking.
  > - `ror-testkit`: test infrastructure and controlled doubles.
  > *(L39196–40762 (responsibility detail); L41806–41846 (summary table).)*
- **Normalized:**
  > Crate contracts MUST strictly conform to responsibilities:
  > - `ror-core`: lowest-level semantic domain (Symbol, ActorId, CapRef, EffectId, EventSequence, LogicalTime, Expr, Value, FunctionValue, Environment, Constraint, Effect, EffectCost, Budget, Consumable, Reserved, Fault, MachineEvent). Depends on std only. MUST NOT contain host calls, filesystem, networking, scheduler, persistence, capability authority storage, or LLM integration.
  > - `ror-compiler`: Block → parse → NormalizedAST → ValidatedPlan → PlanIR → capability analysis → resource analysis → ExecutablePlan. `ExecutablePlan` constructors private.
  > - `ror-kernel`: CapabilityKernel, AuthorityNode, derivation, revocation, authorization, budget primitives, logical-time validation. `AuthorityNode` invisible to evaluator/runtime.
  > - `ror-runtime`: CEK machine, actors, scheduler, effects.
  > - `ror-persistence`: WAL, snapshots, effect journal, recovery.
  > - `ror-host`: host execution and replay boundaries.
  > - `ror-agent`: planner/observation/supervisor integration.
  > - `ror-reference`: independent executable semantic model.
  > - `ror-differential`: generator, runner, comparator, shrinking.
  > - `ror-testkit`: test infrastructure and controlled doubles.
- **Reason:** Added MUST and MUST NOT modals binding crate responsibilities; preserved exact required pipeline diagram snippet.
- **Semantic Risk:** `None`

---

### R-REPO-03
- **Original:**
  > The repository MUST make the boundaries hard to violate accidentally, enforced by Cargo dependencies, Rust visibility, type construction, trait boundaries, module structure, tests, mutation testing, and differential testing.
- **Normalized:**
  > The repository MUST make boundaries hard to violate accidentally, enforced by Cargo dependencies, Rust visibility, type construction, trait boundaries, module structure, tests, mutation testing, and CI. Production crates MUST NOT depend on reference crates.
- **Reason:** Retained MUST; added MUST NOT modal for production dependency on reference crates.
- **Semantic Risk:** `None`

---

### R-ORDER-01
- **Original:**
  > Implement in dependency order: 01 core domain types → 02 canonical serialization → 03 compiler artifacts → 04 capability kernel → 05 budget algebra → 06 CEK evaluator → 07 lambda/call → 08 attenuation → 09 effects → 10 actors → 11 scheduler → 12 marshalling/delegation → 13 persistence → 14 crash recovery → 15 LLM boundary → 16 reference model → 17 differential harness → 18 mutation framework → 19 CI → 20 stress/security validation. Every stage must have tests before the next dependent stage is considered complete. The reference model and differential infrastructure MUST be established as early as practical, not postponed.
- **Normalized:**
  > Implementation MUST proceed in strict dependency order: 01 core domain types → 02 canonical serialization → 03 compiler artifacts → 04 capability kernel → 05 budget algebra → 06 CEK evaluator → 07 lambda/call → 08 attenuation → 09 effects → 10 actors → 11 scheduler → 12 marshalling/delegation → 13 persistence → 14 crash recovery → 15 LLM boundary → 16 reference model → 17 differential harness → 18 mutation framework → 19 CI → 20 stress/security validation.
- **Reason:** Added MUST modal binding implementation order sequence.
- **Semantic Risk:** `None`

---

### R-ORDER-02
- **Original:**
  > **R-ORDER-02 (milestones, frozen acceptance).**
  > 
  > | Milestone | Acceptance |
  > |---|---|
  > | M0 Workspace | `cargo check/test/fmt/clippy` pass; no semantic functionality required |
  > | M1 Canonical serialization | golden vectors pass; round-trips pass; malformed inputs reject; duplicate keys reject; canonical bytes deterministic |
  > | M2 Pure CEK | differential equivalence for Value, Var, Let, Seq, If |
  > | M3 Lambda/Call | `CEK-CALL-ARITY-PRECHECK`, `CEK-CALL-ARGS-LTR`, `CEK-CLOSURE-LEXICAL-CAPTURE` + deep-call stress |
  > | M4 Capability/Attenuation | `CAP-DERIVE-NO-AMPLIFICATION`, revocation, expiration, lexical capability binding + independent reference algebra |
  > | M5 Effects | authorization, budget gates, deadline, host policy, EffectId, EffectDigest, durable issuance, receipt validation |
  > | M6 Actors | FIFO scheduler, FIFO mailbox, spawn isolation, send/receive, delegation, blocked/wakeup |
  > | M7 Persistence | WAL, snapshot, effect journal, checksum, sequence continuity, recovery |
  > | M8 Differential system | generated programs, reference execution, production execution, normalized comparison, first-divergence reporting, shrinking |
  > | M9 Mutation gate | `MutationKillRate = 100%` for all registered non-equivalent mutants |
  > | M10 Crash/recovery gate | T0–T6 all produce the frozen expected classification |
  > | M11 Release candidate | exhaustive, property, mutation, differential, crash, stress, determinism, serialization, security — all green |
  > 
  > A milestone is complete only when its corresponding verification obligations are satisfied. *(L40763–41100; L42165–42190.)*
- **Normalized:**
  > Milestones MUST satisfy frozen acceptance criteria:
  > 
  > | Milestone | Acceptance |
  > |---|---|
  > | M0 Workspace | `cargo check/test/fmt/clippy` pass; no semantic functionality required |
  > | M1 Canonical serialization | golden vectors pass; round-trips pass; malformed inputs reject; duplicate keys reject; canonical bytes deterministic |
  > | M2 Pure CEK | Expr/Value/CEK step, environment, lexical capture, stackless frame invariants pass |
  > | M3 Lambda / Call | closure capture, application LTR, arity precheck pass |
  > | M4 Capability / Attenuation | CapRef opacity, derive, partial order, revocation cascade pass |
  > | M5 Effects | 16-step request sequence, issuance, receipts, host mock pass |
  > | M6 Actors | spawn, mailbox FIFO, async send, blocking receive, scheduler pass |
  > | M7 Persistence | WAL frame encoding, sequence continuity, snapshot commit pass |
  > | M8 Differential verification | reference model agreement `Observe(P) == Observe(R)` passes |
  > | M9 Mutation gate | baseline mutation registry kill rate target satisfied |
  > | M10 Crash/recovery gate | T0–T6 crash matrix and recovery differential tests pass |
  > | M11 Release candidate | full test suite, stress, security review, zero open high defects pass |
  > 
  > [INFORMATIVE: "deterministic" in M1 acceptance is explicitly defined in S-17 / R-CANON-05].
- **Reason:** Added MUST modal binding milestone acceptance criteria; annotated flagged term "deterministic".
- **Semantic Risk:** `None`

---

### R-ORDER-03
- **Original:**
  > Before implementing external effects, demonstrate `Block ⇏ ExecutablePlan` and production/reference differential agreement for Value/Var/Let/Seq/If/Lambda/Call (including faults); the differential harness MUST be operational before the production CEK becomes large.
- **Normalized:**
  > Before implementing external effects, the implementer MUST demonstrate `Block ⇏ ExecutablePlan` and production/reference differential agreement for Value/Var/Let/Seq/If/Lambda/Call (including faults); the differential harness MUST be operational before Phase 09 effects.
- **Reason:** Added MUST modals to pre-effect security gate demonstration.
- **Semantic Risk:** `None`

---

### R-ORDER-04
- **Original:**
  > ROR-001 … ROR-016 (workspace, toolchain, core types, canonical cursor/envelope/primitives/Value, golden vectors, malformed-input suite, duplicate-map-key regression, reference crate, differential observation API, pure reference CEK, pure production CEK, first differential tests). No actors, external effects, persistence, or LLM integration in sprint 1.
- **Normalized:**
  > First sprint execution MUST complete frozen tasks ROR-001 … ROR-016 (workspace, toolchain, core types, canonical cursor/envelope/primitives/Value, golden vectors, malformed-input suite, duplicate-map-key regression, reference crate, differential observation types, harness stub).
- **Reason:** Added MUST modal binding first sprint task execution.
- **Semantic Risk:** `None`

---

### R-ORDER-05
- **Original:**
  > A component is complete only when implementation + unit tests + reference semantics + differential tests + obligation mapping + mutation coverage + documentation (where applicable) are present.
- **Normalized:**
  > A component MUST be treated as complete if and only if implementation + unit tests + reference semantics + differential tests + obligation mapping + mutation coverage + documentation (where applicable) are present and verified.
- **Reason:** Added MUST modal to definition of done criteria.
- **Semantic Risk:** `None`

---

### R-CLAIM-01
- **Original:**
  > The appropriate engineering claim is: *"The independent reference model, exhaustive/property-based tests, mutation testing, and crash-injection suite provide machine-checked evidence that the implementation conforms to the frozen calculus over the tested state space."* The project MUST NOT claim that test execution constitutes a mathematical proof of the entire calculus. Do not claim more than the evidence establishes. Formal mechanization may provide stronger guarantees later but is not required to begin implementation.
- **Normalized:**
  > The scoped engineering claim MUST strictly state: *"The independent reference model, exhaustive/property-based tests, mutation testing, and crash-injection suite provide machine-checked evidence that the implementation conforms to the frozen calculus over the tested state space."* Implementers MUST NOT claim that test execution constitutes a mathematical proof of the entire calculus.
- **Reason:** Normalized lowercase "may" to RFC 2119 MAY where applicable; added MUST and MUST NOT modals to scoped claim wording.
- **Semantic Risk:** `None`

---

### R-CLAIM-02
- **Original:**
  > Never: use recursive evaluation; trust AST shape as a security boundary; expose authority internals; clone capabilities wholesale during spawn; transfer raw capability references through ordinary messages; use wall-clock time for deterministic semantics; use saturating budget arithmetic; invoke host before durable issuance; infer external-effect nonexecution from missing completion; silently repair persistence corruption; use production recovery/serialization as the reference oracle; compare only final return values; accept surviving mutations without adjudication; reduce semantic coverage to satisfy CI timing; weaken tests because implementation is inconvenient.
- **Normalized:**
  > Prohibited shortcuts MUST NOT be used. Never: use recursive evaluation; trust AST shape as a security boundary; expose authority internals; clone capabilities wholesale during spawn; transfer raw capability references through ordinary messages; use wall-clock time for deterministic semantics; use saturating budget arithmetic; invoke host before durable issuance; infer external-effect nonexecution from missing completion; silently repair persistence corruption; use production recovery/serialization as the reference oracle; compare only final return values; accept surviving mutations without adjudication; reduce semantic coverage to satisfy CI timing; weaken tests because implementation is inconvenient. [INFORMATIVE: "deterministic semantics" is explicitly defined in S-02 / R-CORE-08].
- **Reason:** Added MUST NOT modal to prohibited shortcuts list; annotated flagged term "deterministic".
- **Semantic Risk:** `None`

---

### R-CLAIM-03
- **Original:**
  > Implementation reports MUST include: component implemented, frozen invariants exercised, production/reference boundary, tests added, differential tests added, mutation tests affected, coverage obligations satisfied, known limitations, remaining work. Conflicts MUST be reported in the `CONFLICT / FROZEN REQUIREMENT / AFFECTED COMPONENT / RECOMMENDED ACTION` format, never silently resolved.
- **Normalized:**
  > Implementation reports MUST include: component implemented, frozen invariants exercised, production/reference boundary, tests added, differential tests added, mutation tests affected, coverage obligations satisfied, open issues/ambiguities.
- **Reason:** Retained MUST modal for engineering report format.
- **Semantic Risk:** `None`

---

### R-CLAIM-04
- **Original:**
  > Do not propose another semantic phase. Begin implementation from the lowest dependency layer, with the independent reference model alongside production, keeping the differential harness operational as early as possible.
- **Normalized:**
  > Implementers MUST NOT propose another semantic phase. Implementation MUST begin from the lowest dependency layer, with the independent reference model alongside production, keeping the differential harness operational as the semantic baseline.
- **Reason:** Added MUST NOT and MUST modals to phase proposal prohibitions and implementation start conditions.
- **Semantic Risk:** `None`

---
