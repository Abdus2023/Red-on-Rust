# Red-on-Rust — Canonical Specification (Cleaned)

**Status of this document:** normative cleaned rendering of the frozen source `Red-on-Rust.md`.
**Rule:** where this rendering and the source differ, the source's latest frozen text governs; any discrepancy must be recorded per `00-overview.md` §1. Requirement IDs (`R-…`) are defined in `03-obligation-matrix.md`; this file is the canonical home of their normative text.

---

# Part I — Foundations

## S-01 Scope, status, and conventions

**R-SCOPE-01.** Red-on-Rust MUST be a deterministic, capability-scoped, resource-bounded, crash-recoverable execution machine for probabilistically generated programs. It MUST serve as a Rust-based execution substrate for a family of homoiconic, dialect-oriented languages inspired by the REBOL/Red lineage. [INFORMATIVE: "deterministic" is explicitly defined in S-02 / R-CORE-08 as InitialState + SchedulerTrace + HostTrace ⇒ UniqueMachineTrace]. *(Provenance: turn [60]/README "Core Thesis"; L41293–41300.)*

**R-SCOPE-02.** The architecture, specification, reference contract, and verification contract MUST be maintained as FROZEN. The repository MUST remain in BOOTSTRAP state until implementation evidence is provided. A frozen specification MUST NOT be construed as a verified implementation; frozen status MUST indicate requirement stability without asserting evidence of conformance. *(L38929–38942, L41297–41315.)*

**R-SCOPE-03 (normative process rule).** The implementer MUST NOT redesign, reinterpret, simplify away, or silently modify frozen semantics (CEK semantics, evaluation order, lexical scoping, closure semantics, capability algebra, attenuation, revocation, budget algebra, effect authorization, effect issuance protocol, actor isolation, deterministic scheduling, marshalling rules, delegation semantics, canonical serialization, persistence protocol, crash matrix, recovery classification, LLM trust boundary, reference-model independence, differential-testing contract). If implementation difficulty exposes an ambiguity, the implementer MUST STOP and report it; semantic ambiguity MUST NOT be resolved by inventing behavior. [INFORMATIVE: "deterministic scheduling" is explicitly defined in S-15 / R-ACTOR-07]. *(L37664–37686.)*

**R-SCOPE-04.** The production implementation and the executable reference model MUST share zero core implementation logic (no `reference_* → production_*` calls for step, authorize, budget, recover, encode, scheduler). Shared semantic test fixtures MAY be used; shared transition implementations MUST NOT be used. *(L37696–37721.)*

## S-02 Core thesis and central invariants

**R-CORE-01 (central external-effect invariant).** The machine MUST enforce the central external-effect invariant: `LLMOutput ∧ UntrustedInput ↛ ExternalEffect`. The central security boundary MUST be the machine; neither the language surface nor the model generating the program MUST be treated as a security boundary. *(L41320–41335; L27505–27513.)*

**R-CORE-02 (external-effect chain).** An ExternalEffect(E) MUST NOT occur unless the complete validation chain holds invariant: `ExternalEffect(E) ⇒ ValidatedPlan(P) ∧ Authorized(E,κ,t) ∧ CapabilityWithinCeiling(E) ∧ BudgetAvailable(E) ∧ DeadlineValid(E,t) ∧ HostPolicyOK(E) ∧ Issued(E)`.
*(L41337–41351; L27491–27509.)*

**R-CORE-03 (no unauthorized effects).** If an effect E is not authorized, the machine MUST NOT produce an ExternalEffect: `¬Authorized(A,E,t) ⇒ ¬ExternalEffect(E)` (equivalently `¬Authorized ⇒ ¬Request` at the operational level). *(L42056–42064; L7413–7419.)*

**R-CORE-04 (no authority amplification).** Capability derivation MUST NOT amplify authority: `derive(A,C) ≼ A` MUST hold invariant for all authorities A and constraints C. *(L42066–42072; L6399–6406.)*

**R-CORE-05 (no budget teleportation).** Budget accounting MUST maintain the partition invariant `C_available + C_escrowed + C_consumed = C_initial`; actor spawn MUST be executed as a budget ownership transfer, MUST NOT create new budget, and MUST NOT consume budget. *(L42074–42080; L28203–28240.)*

**R-CORE-06 (no host-before-durability).** The host MUST NOT be invoked for an effect E before durable issuance is committed: `HostInvoked(E) ⇒ DurableIssued(E)`. An effect MUST NOT be treated as issued merely because an in-memory object exists; durable issuance MUST require a durable `Issued` record. *(L42082–42088; L35150–35156.)*

**R-CORE-07 (no raw capability transfer).** Ordinary marshalling of raw capability values MUST be rejected: `OrdinaryMarshal(Value::Capability) ⇒ Rejected`. Authority MUST NOT cross actor boundaries except via explicit delegation. *(L42090–42098; L25972–26001.)*

**R-CORE-08 (determinism).** Machine execution MUST satisfy the determinism theorem: `InitialState + SchedulerTrace + HostTrace ⇒ UniqueMachineTrace` (with an accepted planner trace for end-to-end runs). The LLM's stochasticity MUST remain strictly above the machine boundary and MUST NOT influence machine state transitions. [INFORMATIVE: "deterministic" is explicitly defined by this state-transition theorem]. *(L41623–41646; L27518–27547.)*

**R-CORE-09 (causal crash recovery).** Crash recovery MUST restore pre-crash state according to `Recover(Snapshot, EventLog, EffectJournal) ≡ PreCrashMachineState` for every crash at a defined persistence boundary, provided every interrupted external effect is (a) durably reconciled, (b) verified idempotent or replayable via recorded receipt, or (c) explicitly classified `Indeterminate` and prevented from silent continuation. The system MUST NOT infer "not executed" from a missing completion record. *(L27551–27569; L35159–35176.)*

**R-CORE-10 (no silent recovery corruption).** Invalid persistence state MUST produce an explicit `RecoveryFault`. Persistence corruption MUST NOT be silently repaired by mutation (the recovery engine MUST NOT drop duplicate runnable actors, MUST NOT adjust budget mismatches, MUST NOT ignore sequence gaps, and MUST NOT ignore checksum failures). *(L42100–42105; L35196–35208.)*

## S-03 Trust model and trusted computing base

**R-TRUST-01.** The system MUST adhere to the following normative trust assignments:

| Component | Trust | Role |
|---|---|---|
| LLM / planner | **No** | Proposal generation |
| `Block` (language data) | **No** | Untrusted program data |
| Compiler | Yes | Establishes executable invariants |
| Capability kernel | Yes | Authority decisions |
| CEK machine | Yes | Deterministic execution |
| Scheduler | Yes | Deterministic interleaving |
| Budget system | Yes | Resource conservation |
| Persistence / effect journal | Yes | Durable machine state, causal effect state |
| ReplayHost | Yes | Recorded-effect reconstruction |
| Live host | **Partial** | External-world execution (capability + policy constrained) |
| Supervisor | Yes | Lifecycle and recovery |

[INFORMATIVE: "deterministic" is explicitly defined in S-02 / R-CORE-08 and S-15 / R-ACTOR-07]. *(L41823–41841; L27611–27624.)*

**R-TRUST-02.** LLM output MUST NOT be included in TCB authority (`LLM output ∉ TCB authority`). The TCB MUST consist strictly of: CEK machine, capability kernel, budget algebra, deterministic scheduler, canonical serializer, WAL/recovery state machine, and effect boundary. [INFORMATIVE: "deterministic" is explicitly defined in S-15 / R-ACTOR-07]. *(L28178–28230.)*

**R-TRUST-03 (no hidden authority).** The LLM, AST, evaluator, scheduler, host adapter, or ordinary `Value` representation MUST never manufacture authority. Capabilities MUST be treated as opaque handles; only the capability kernel MUST decide authority. The evaluator MAY call `derive(capability, constraint, logical_time)` and `authorize(capability, effect, logical_time)`; it MUST NOT inspect authority internals. *(L37722–37748; L19153–19175.)*

## S-04 System architecture and component boundaries

**R-ARCH-01 (pipeline).** The normative end-to-end execution path MUST strictly follow the pipeline sequence:

```
LLM/Planner → PlanProposal → staleness validation → Block
→ parse → normalize → validate → lower → capability analysis → resource bounds
→ ExecutablePlan → CEK Machine → Capability Kernel / Budget System
→ Effect Issuance → Durable Boundary → Host
```

*(L37750–37780; L27287–27310.)*

**R-ARCH-02.** The verification architecture MUST maintain an independent and co-equal structure:

```
Production → Observation (normalized) → Reference
```

The production implementation and executable reference model MUST NOT share core transition logic. *(L41406–41424; L37696.)*

**R-ARCH-03 (boundary integrity).** The boundaries among compiler, capability kernel, evaluator, runtime, persistence, host, and reference model MUST remain intact: a raw `Block` MUST NOT have any path into `step()`; `ExecutablePlan` constructors MUST remain private to the compiler; the production runtime MUST only ever receive an `ExecutablePlan`. *(L9086–9097; L39296–39318.)*

**R-ARCH-04.** Architectural dependencies MUST strictly adhere to the linear direction: capability algebra → capability kernel → effect/cost & revocation → executable plan → actor state → global config → scheduler → host executor / replay host. *(L9059–9085.)*

## S-05 LLM / planner boundary

**R-PLANNER-01 (proposal data).** The planner MUST return proposals as `PlanProposal { observation_sequence: EventSequence, block: Block, planner_metadata }`. LLM output MUST be treated as data (`LLMOutput ∈ Data`) and MUST NOT confer authority. *(L27176–27198.)*

**R-PLANNER-02 (cannot).** The model MUST NOT: allocate capabilities; authorize effects; modify budgets; modify the event log; allocate actors directly; invoke the host; bypass validation; alter scheduler state. It MAY only propose a `Block`, which enters the ordinary compiler pipeline. *(L27271–27285; L37781–37790.)*

**R-PLANNER-03 (staleness).** A proposal MUST be causally bound to the machine state from which it was generated. The machine MUST verify `proposal.observation_sequence = current_planning_epoch` and MUST otherwise reject it as `StalePlan` — a normal machine-visible outcome without state mutation. *(L27199–27236; L28373.)*

**R-PLANNER-04 (planner determinism).** The LLM MAY be non-deterministic. The machine MUST satisfy the determinism theorem: `InitialState + Plan + SchedulerTrace + HostTrace ⇒ UniqueMachineTrace`. For exact end-to-end replay, the machine MUST record a `PlannerAccepted { observation_sequence, proposal_digest, block }` record, and replay MUST consume the recorded proposal without querying the LLM. [INFORMATIVE: "deterministic" is explicitly defined by this state-transition theorem]. *(L27392–27414.)*

**R-PLANNER-05 (LLM outer-loop conformance, normative test obligation).** The conformance suite MUST include: (1) untrusted-input rejection — raw/malformed/malicious `Block` data fed directly to the runtime MUST be rejected at the compiler boundary; (2) stale-proposal rejection — advanced machine state + old proposal MUST yield rejection without state mutation; (3) end-to-end replay — live session vs replay with recorded proposal + `ReplayHost` MUST yield byte-for-byte identical final `GlobalState` and `EventLog`. *(L27920–27931; L28513–28521.)*

## S-06 Compilation boundary

**R-COMPILE-01.** The compiler MUST enforce `Block ≠ ExecutablePlan`. Only validated executable plans MUST enter the trusted machine; no `Block` MUST bypass compilation. *(L41440–41452; L3834–3838.)*

**R-COMPILE-02 (pipeline).** Compilation MUST pass the stages: parse → normalize → validate → lower → capability analysis → resource analysis. Any failed stage MUST yield `fault(F_compilation)`; no raw `Block` MUST reach execution. *(L1930–1960 (J1–J4 and compilation theorem, superseded form); L39253–39267 (frozen pipeline).)*

**R-COMPILE-03 (static checks, frozen intent).** The static compilation judgment `Γ; κ_static ⊢ e : τ ! F @ B` MUST thread type, possible-effect set `F` (conservative over-approximation; pure terms MUST yield `F = ∅`), capability requirements, and static budget upper bound `B`. If a term's worst-case cost exceeds `B_max`, compilation MUST fail. *(L3874–3905 (v2 form); L1953–1980 (v1 J1–J4, superseded form).)*

**R-COMPILE-04 (plan immutability / temporal integrity).** An `ExecutablePlan` MUST be immutable; a new plan MAY only be produced by another validated compilation transition (plan₁ → execution/observation → planner → Block₂ → compiler → plan₂). A plan authorized at `t₀` MUST NOT silently acquire new authority at `t₁`. *(L1722–1745; L2052–2070 (v1 Theorem 6).)*

**R-COMPILE-05.** `ExecutablePlan` constructors MUST remain private to the compiler crate.  [INFORMATIVE (gap): The detailed effect-set inference (v1 judgment J2, `Γ ⊢ e ↝ Φ`) is not re-specified]. *(L39296–39318.)*

**Non-normative (gap).** The detailed effect-set inference (v1 judgment J2, `Γ ⊢ e ↝ Φ`) is not re-specified in the frozen pipeline stages; see `U-22` in `09-unresolved-decisions.md`.

---

# Part II — Language and machine semantics

## S-07 Core calculus (syntax)

**R-CALC-01 (value domain, machine).** The machine value domain MUST strictly consist of: `v ::= Unit | Bool(bool) | Integer(i64) | Bytes(Vec<u8>) | Symbol(Symbol) | String(String) | List(Vec<Value>) | Tuple(Vec<Value>) | Function(FunctionValue) | Capability(CapRef) | DelegatedCapability(DelegatedCapability)`. Raw capabilities MAY only be constructed by the capability kernel and MUST NOT be constructed by untrusted code. Delegated capabilities MAY only be constructed by the marshaller.

*(L12290–12312 (turn [21]); L19153–19175.)*

**R-CALC-02 (expression domain, frozen surface).** The frozen `Expr` AST MUST consist strictly of declarative constructors: `Value(Value) | Var(Symbol) | Let { name, value, body } | Seq { first, second } | If { condition, then_branch, else_body } | Lambda { params, body } | Call { func, args } | Attenuate { cap, constraint } | Request { capability, operation, target, params } | Spawn { expr, initial_budget, capabilities } | Send { target, message } | Receive | Yield | Halt`. Expressions MUST NOT embed host callbacks.

*(L12132–12170 (turn [21]).)*

**R-CALC-03 (symbols).** Runtime variable identity MUST be `Symbol(u32)` and MUST NOT use `String`. The compiler MUST maintain the name→Symbol mapping; the evaluator MUST operate entirely on symbols. *(L12250–12270.)*

**R-CALC-04 (effect descriptor).** An effect MUST be immutable data: `Effect { capability: CapRef, operation: Op, target: Target, params: Params, cost: EffectCost }`. Effect identity MUST be canonical according to `EffectDigest = SHA-256(canonical_bytes(effect))`. *(L9288–9348 (early form, capability carried in `EffectRequest.cap`, superseded); L23726–23772 (frozen form).)*

**R-CALC-05 (effect cost, frozen form).** Effect cost MUST be structured as `EffectCost { issue: Consumable, complete_max: Consumable, reserve: Reserved }`. `issue` MUST be charged at request time; `complete_max` MUST be escrowed at issuance so completion accounting MUST NOT fail; `reserve` MUST hold capacity until completion. *(L25799–25825 (Phase 12 correction); L23726–23772 (pre-correction form, superseded).)*

**R-CALC-06 (fault taxonomy).** The fault taxonomy MUST strictly correspond to the frozen Rust `Fault` enum: `Capability(CapabilityError) | BudgetExhausted | DeadlineExceeded | HostPolicyDenied(HostPolicyError) | EffectCanonicalization(EffectError) | Host(HostFault) | ReplayCorruption | InvalidReceipt` (plus `StalePlan` at the planner boundary). The frozen fault taxonomy is the Rust `Fault` enum. *(L23784–23819; L27236. See C-08 for naming inconsistencies in earlier drafts.)* **Non-normative annotation (X-64, X-67, X-68, X-69, C-54, C-57, C-58; the normative sentence above is unchanged and governs):** the parenthetical is **source-supported** — L28373 (turn [36]) states that a stale proposal “is rejected with `Fault::StalePlan`”, and L27236 (turn [33]) gives `StalePlan` as a bare token. It is nevertheless not a variant of the declaration this obligation cites: none of the seven `pub enum Fault` declarations (L10882, L17788, L18125, L22415, L23319, L23806, L26865) contains `StalePlan`, and L23807 carries an explicit `// ... (previous faults)` elision, so the eight enumerated variants do not close the set. `StalePlan` is one of **twelve** `Fault::` paths the source uses but never declares (X-69). The payload type `HostFault` in `Host(HostFault)` is declared once with two variants while eight undeclared `HostFault::` paths are used, six on the frozen replay path (C-57, **blocking**); and `HostFault` and `Revoked` additionally denote *members of the v1 fault grammar* `F` at L1949 — a different level of the taxonomy than the flat variant list stated here (C-58). **An earlier revision of this annotation asserted that `Fault::StalePlan` “occurs nowhere in L1–42312”; that claim was false and is withdrawn here rather than silently overwritten (R-SCOPE-03).** Which variants the taxonomy finally contains is U-08's decision.

**R-CALC-07 (effect properties).** Effect semantics MUST maintain replayability, reversibility, and idempotence properties; an effect's *machine result* MAY be replayed even when the real-world operation cannot. [INFORMATIVE: the per-operation classification table in the source is non-normative]. *(L2141–2156 (v1) / L3858–3873 (v2) (declared domain + illustrative table); L26669–26735 (Phase 14 effect classes).)*

**R-CALC-08 (configuration).** Local machine configuration MUST be structured as `Σ = ⟨e, ρ, κ, B, t, H, L⟩` (current term, local environment, capability kernel, budget, logical time, isolated heap, append-only event log); global configuration MUST be structured as `G = ⟨A, t, L, R, E_journal⟩`. *(L7119–7144; L8653–8682; L24148–24163.)*

## S-08 CEK machine

**R-CEK-01 (explicit machine).** Evaluation MUST use an explicit CEK-style machine: state `EvalState { expr: Expr, env: Environment, continuation: Continuation }`. The evaluator MUST NOT depend on recursive host-language calls for call-stack depth. *(L41484–41499; L37800–37812.)*

**R-CEK-02 (value-return invariant, hard).** A value MUST be terminal if and only if its continuation is empty: `Value ∧ K = ε ⇒ Halt`; `Value ∧ K ≠ ε ⇒ Resume(K, Value)`. Evaluator steps MUST NOT return `Halt(v)` for `Expr::Value(v)` when `K ≠ ε`.

*(L16878–16905 (frozen); L17379–17412 (correction, same rule); L37826–37838.)*

**R-CEK-03 (continuation frames).** Continuation frames MUST be explicit stack values in the Rust representation. Continuation frames MUST NOT rely on implicit host-language recursion stack frames.

*(L16928–16958; L23821–23856.)*

**R-CEK-04 (lambda).** Lambda creation MUST be pure and deterministic: it MUST capture the lexical environment at creation and MUST produce `FunctionValue { params, body, env }`; the resulting value MUST pass through the ordinary value-return mechanism and MUST NOT halt the machine immediately. [INFORMATIVE: "deterministic" is explicitly defined in S-02 / R-CORE-08]. *(L16971–16995; L19095–19110 (attenuate/lexical invariant context).)*

**R-CEK-05 (call).** Function application MUST proceed left-to-right: (1) evaluate `func` to `FunctionValue`; (2) evaluate arguments left-to-right (`CEK-CALL-ARGS-LTR`); (3) pre-check arity (`CEK-CALL-ARITY-PRECHECK`) — mismatch MUST produce `fault(F_arity)` before frame stack allocation; (4) bind parameters in a fresh child environment inheriting captured bindings; (5) push return frame and evaluate body. *(L16878–16905 (frozen); L37840–37862; L18723–18851.)*

**R-CEK-06 (continuation preservation).** Environment lookup MUST walk the lexical chain. An unbound variable MUST produce `fault(F_unbound)`. Environment mutation MUST NOT occur. *(L14632–14642.)*

**R-CEK-07 (progress & preservation).** Evaluation MUST continue small-step until `Halt(v)` or `Fault(f)` is reached. Recursion limits MAY optionally yield `fault(F_stack_exhausted)`. *(L7273–7277; L8850.)*

## S-09 Capability algebra

**R-CAP-01 (semantic domains, v0.2).** Authority MUST be defined as `A = {(o, ⟨S,Q,R,T⟩)}` mapping operation `o` to scope `S`, param predicate `Q`, resource limit `R`, and lifetime `T`. `CapRef` MUST be an opaque handle. Capability resolution MUST map `κ(c) → Authority`.






*(L6354–6379.)*

**R-CAP-02 (operation-indexed authority).** Derivation `derive(A, C)` MUST produce attenuated authority `A'`. Derivation MUST NOT amplify authority: `derive(A, C) ≼ A` MUST hold invariant. Derivation MUST NOT grant operations, scopes, resources, or lifetimes missing from parent authority `A`. *(L6370–6380.)*

**R-CAP-03 (partial order).** Partial ordering `A₁ ≼ A₂` MUST hold if and only if `ops(A₁) ⊆ ops(A₂)` and `scope(A₁) ⊆ scope(A₂)` and `Q₁ ⇐ Q₂` and `R₁ ≤ R₂` and `T₁ ≤ T₂`. Meet `A₁ ⊓ A₂` MUST yield maximal common attenuation. *(L6381–6390.)*

**R-CAP-04 (constraint vs authority).** Authorization `Authorized(c, e, t)` MUST hold if and only if `c` is valid at logical time `t`, `op(e) ∈ ops(κ(c))`, `target(e) ∈ scope`, `Q(params(e))` holds, `cost(e) ≤ R`, and `t ≤ T`. *(L6391–6396; L6406.)*

**R-CAP-05 (derivation).** Revocation MUST be ancestor-cascading: revoking `c` MUST invalidate `c` and all derived descendants `Descendants(c)`. The revocation check MUST walk the lineage in O(depth). *(L6397–6404; Theorem 1, L6657–6661.)*

**R-CAP-06 (canonical authorization predicate).** Every capability derivation MUST record parent-child edges `parent(c') = c`. The lineage graph MUST form a forest of rooted trees.

*(L6406–6421; L6647–6656.)*

**R-CAP-07 (revocation / lineage).** Capability lifetime `T` MUST be bounded by logical clock `t`. When `t > T`, `Authorized(c, e, t)` MUST evaluate to `false` and resolution MUST yield `fault(F_cap_expired)`. *(L6434–6445; L6647–6656.)*

**R-CAP-08 (algebra theorems, frozen statements).** The `Attenuate { cap, constraint }` operation MUST evaluate `cap`, resolve `κ(cap)`, compute `A' = derive(κ(cap), constraint)`, allocate a fresh `CapRef`, store `A'`, record the parent edge, and return the fresh `CapRef`.



*(L6422–6433; L6657–6671.)*

**R-CAP-09 (time).** Logical time `t` MUST NOT be fetched from the host OS; time `t` MUST be an explicit component of machine state (logical clock / deterministic timestamp) to ensure replay determinism. Wall-clock time MUST NOT be used as semantic machine state. [INFORMATIVE: "deterministic" is explicitly defined in S-02 / R-CORE-08]. *(L6434–6436; L38858–38890.)*

## S-10 Capability kernel

**R-KERN-01 (opaque references).** `CapRef { index: u32, generation: u32 }` MUST be opaque and generation-safe; fields MUST be private; public constructors from arbitrary integers MUST NOT exist; `CapRef`s MUST be constructed strictly by the capability kernel. [INFORMATIVE: generation safety is defined by generation-number mismatch checks preventing dangling reference reuse]. *(L9127–9133; L10178–10208.)*

**R-KERN-02 (API contract).** `CapabilityKernel` MUST own authority storage: `arena: GenerationalArena<AuthorityNode>`, `revocation_set: HashSet<CapRef>`. `derive()` and `revoke()` MUST be kernel operations.



*(L6672–6728; L19153–19175; L37870–37886.)*

**R-KERN-03 (substrate privacy).** The capability kernel MUST enforce that authority state mutations occur only via kernel interface methods and MUST NOT expose mutable references to internal authority nodes. *(L39397–39407; L37722–37748.)*

---

# Part III — Resources

## S-11 Budget model

**R-BUDGET-01 (structure).** Budget MUST be structured as `B = ⟨C, R, W⟩` (Consumable C, Reserved R, Deadline W). Budget accounting MUST be exact; budget arithmetic MUST NOT use saturating subtraction. *(L8683–8700 (v0.3 frozen); L9161–9175 (Rust shapes); L41537–41560.)*

**R-BUDGET-02 (checked arithmetic).** Consumable vector `C = ⟨fuel, io, duration⟩` MUST strictly decrease on consumption. If `C_available < C_required`, execution MUST yield `fault(F_budget_exhausted)`. *(L9207–9245; L38044–38046; L41557.)*

**R-BUDGET-03 (reservation predicates).** Reserved vector `R = ⟨memory, slots⟩` MUST track held capacity. Reservation MUST fail with `fault(F_budget_exhausted)` if allocation exceeds limit. Memory/slot release MUST restore available capacity. *(L7487–7520; L8692–8696.)*

**R-BUDGET-04 (dual-gate within-budget).** Deadline `W` MUST be an absolute logical clock bound (`W ∈ ℕ ∪ {∞}`). When logical clock `t > W`, execution MUST yield `fault(F_deadline_exceeded)`. *(L8692–8696; L7426–7440.)*

**R-BUDGET-05 (conservation).** Effect issuance MUST escrow `complete_max` from consumable budget `C`. Effect completion MUST refund `complete_max - complete_actual` to `C_available`. Escrow conservation MUST hold invariant: `C_available + C_escrowed + C_consumed = C_initial`.



*(L7408–7425; L28203–28240 (frozen partition); L35210–35215.)*

**R-BUDGET-06 (time advancement).** Actor spawn MUST escrow budget from parent to child (`BudgetAllocationSpec` → `validate_and_escrow`). Child termination MUST return unconsumed budget to parent. *(L8698–8700; L10164–10168. The per-transition delta values beyond this rule are an open item — see `U-07`.)*

**R-BUDGET-07 (cost model).** Cost model `CostModel` MUST map operations to costs `Cost { consumable, reserved }`. Evaluator transitions MUST charge fuel cost before executing small-step transitions. *(L9155–9205; L10171–10177.)*

**R-BUDGET-08 (budget fault).** Budget arithmetic MUST NOT overflow or wrap. Arithmetic overflow MUST yield `fault(F_budget_overflow)`. *(L7345–7352; L7410–7419.)*

---

# Part IV — Effects

## S-12 Effect model and request sequence

**R-EFFECT-01 (request semantics).** Effect requests MUST proceed through the 16-step protocol: (1) evaluate `Request` expression; (2) resolve `CapRef`; (3) verify capability valid and unrevoked; (4) verify authorization `Authorized(c, e, t)`; (5) verify capability within ceiling; (6) verify budget available for `issue + complete_max`; (7) verify deadline `t ≤ W`; (8) verify host policy; (9) charge `issue` cost; (10) escrow `complete_max` cost; (11) reserve capacity; (12) allocate monotonic `EffectId`; (13) construct canonical `Effect`; (14) write durable `Prepared` log record; (15) emit `EffectRequest` to host; (16) write durable `Issued` record before host execution completes. *(L12177–12194.)*

**R-EFFECT-02 (gated transition shape).** The machine MUST NOT invoke the host for an external effect before durable issuance is recorded (`HostInvoked(E) ⇒ DurableIssued(E)`). *(L7145–7155; L8700–8710.)*

**R-EFFECT-03 (frozen 16-step request sequence, canonical).** `EffectId` MUST be allocated from a global monotonic counter (`N' = N + 1`). `EffectId` MUST NOT be derived from wall-clock timestamps, memory addresses, or random generators. [INFORMATIVE: "deterministic" allocation is defined by monotonic integer counters].




















*(L37891–37908 (master-prompt 16-step, latest frozen form); L23857–23948 (14-gate machine-internal form, gates 1–14, superseded numbering — see `C-01`); L11053–11090 (14-step `step_request` form, superseded numbering).)*

**R-EFFECT-04 (short-circuit).** Host responses MUST return `EffectReceipt { id, effect_digest, result }`. The machine MUST verify `receipt.effect_digest == SHA-256(canonical_bytes(effect))` and MUST reject mismatched receipts with `fault(F_digest_mismatch)`. *(L24003–24045 (Track C); L37891–37908.)*

**R-EFFECT-05 (guaranteed completion accounting).** On receipt of valid `EffectReceipt`, the machine MUST: (1) reconcile escrowed `complete_max` vs actual cost; (2) release reserved capacity; (3) write durable `EffectCompleted` record; (4) deliver result value to caller or raise host fault. *(L25799–25825.)*

**R-EFFECT-06 (causal receipt validation).** Host execution failure MUST yield `fault(F_host_fault)` or `fault(F_policy_denied)`. Host faults MUST NOT corrupt machine state or alter unconsumed budget. *(L23949–24002; L25952–25970; L37910–37922.)*

**R-EFFECT-07 (completion accounting).** Replay host `ReplayHost` MUST consume recorded receipt log without invoking real external systems. Recorded receipts MUST match effect digests exactly. *(L23949–24002; L25799–25825.)*

## S-13 Transactional issuance and durability boundary

**R-DUR-01.** Durable boundaries MUST ensure that `Prepared`, `Issued`, `Completed`, and `Reconciled` records are fsynced to persistent storage before downstream transitions occur. *(L35150–35156; L37910.)*

**R-DUR-02 (issuance transaction, strict order).** Durability guarantees MUST hold across process crashes, power failures, and kernel panics. Un-fsynced in-memory state MUST NOT be treated as durable.







*(L35150–35158.)*

**R-DUR-03 (causal effect protocol).** The persistence boundary MUST enforce write-ahead logging before state mutations are visible to external observers. *(L35111–35144; L37953–37965.)*

**R-DUR-04 (crash classification of effects).** Effect state transitions MUST strictly follow `Prepared → Issued → Completed` or `Issued → Reconciled`. A prepared-but-never-issued effect MUST be discarded during recovery. An issued-but-not-completed effect MUST be classified as `Indeterminate` unless authoritative host reconciliation establishes its outcome. *(L35159–35176; L37968–37981.)*

**R-DUR-05 (escrow survives crash).** WAL framing MUST include header magic `0x526F5231` ('RoR1'), format version `0x01`, monotonic sequence `u64`, payload length `u32`, payload bytes, and SHA-256 checksum `[u8; 32]`. Framing errors MUST yield `fault(F_wal_corrupt)`. *(L35210–35215.)*

## S-14 Host boundary and replay

**R-HOST-01 (host gate, defense in depth).** The host interface MUST be isolated behind explicit trait boundaries (`HostAdapter`). Direct OS access from evaluator code MUST NOT occur. *(L8560–8580; L10168–10172.)*

**R-HOST-02 (host adapter scope).** Host policies MUST enforce fine-grained access control beyond capability checks. Host policy denial MUST yield `fault(F_policy_denied)` without mutating machine budget. *(L41823–41841; L27644.)*

**R-HOST-03 (replay host).** Replay host MUST reproduce recorded receipt outputs deterministically given identical effect inputs and sequence order. [INFORMATIVE: "deterministically" is explicitly defined by trace equality]. *(L25972–25996 (Phase 12 digest-validation correction); L33757+ §15B.9; L37985–38000.)*

**R-HOST-04 (replay correspondence theorem).** Live host implementations MUST enforce timeouts on external IO operations. Exceeded host timeout MUST yield `fault(F_host_timeout)`. *(L3947–3958 (v2 Theorem 4); L26249–26262 (effect classes, A7 refinement).)*

**R-HOST-05 (replay validates trace, not just final state).** Host callbacks MUST NOT directly mutate machine memory, actor registries, or capability kernel state. *(L38278–38300.)*

---

# Part V — Concurrency

## S-15 Actors and deterministic scheduling

**R-ACTOR-01 (isolation).** Actor state MUST be isolated: `ActorState { id: ActorId, run_state: RunState, eval: EvalState, capabilities: CapabilityContext, heap: GenerationalArena<Value>, budget: Budget, mailbox: VecDeque<MarshalledValue>, status: ActorStatus }`. Direct cross-actor heap reference access MUST NOT occur. *(L41623–41641; L24268–24290; L25884–25900 (Theorem 4).)*

**R-ACTOR-02 (global state).** Global state MUST manage actors in a `BTreeMap<ActorId, ActorState>`. Global time `LogicalTime` MUST advance monotonically on scheduler steps. *(L24148–24163; L25514–25546.)*

**R-ACTOR-03 (deterministic IDs).** `ActorId` and `EffectId` MUST be allocated by global monotonic counters (`N' = N + 1`). Actor identity MUST NOT be derived from memory addresses, OS PIDs, random UUIDs, thread IDs, or wall-clock timestamps. [INFORMATIVE: "deterministic" allocation is defined by monotonic integer counters]. *(L24226–24245.)*

**R-ACTOR-04 (FIFO scheduler).** Scheduler queue `RunnableQueue` MUST enforce FIFO order and at-most-once membership for runnable actors. Duplicate runnable queue entries MUST NOT exist. *(L25558–25615 (frozen with at-most-once invariant); L24165–24224; L37924–37937.)*

**R-ACTOR-05 (spawn).** Spawn MUST be a deterministic, transactional machine operation: (1) validate and escrow budget (`BudgetAllocationSpec` → `validate_and_escrow`); (2) allocate child `ActorId`; (3) derive child capabilities via `kernel.derive(parent_cap, constraint, t)`; wholesale capability copying/cloning MUST NOT occur; (4) construct isolated child state; (5) enqueue child into runnable queue deterministically; (6) log `ActorSpawned`. [INFORMATIVE: "deterministic" is explicitly defined in S-02 / R-CORE-08]. *(L25573–25615; L25616–25673; L37941–37951.)*

**R-ACTOR-06 (send/receive).** `Send` MUST be asynchronous: marshal the value, enqueue into target mailbox, log `MessageSent`, and deterministically wake a `Blocked` target exactly once. `Receive` MUST dequeue (unmarshal) or, on empty mailbox, block without consuming fuel (`Blocked` MUST be a suspension state, yielding to scheduler). Mailboxes MUST be FIFO. *(L25702–25749; L25674–25701; L37941–37951.)*

**R-ACTOR-07 (deterministic concurrency theorem).** Concurrency MUST satisfy the deterministic scheduling theorem: `InitialState + SchedulerTrace + HostTrace ⇒ UniqueMachineTrace` — scheduler MUST be strictly FIFO, IDs MUST be monotonic, CEK machine MUST be deterministic; hence global state transitions MUST be uniquely determined given identical initial state and external observations. [INFORMATIVE: "deterministic" is explicitly defined by this theorem]. *(L25759–25766 (Theorem 1).)*

**R-ACTOR-08 (no amplification / no teleportation theorems).** Actor termination (`Halt` or unhandled `Fault`) MUST release reserved budget capacity, set status to `Halted` or `Faulted`, and remove actor from runnable queue. *(L26048–26070 (Theorems 2–3).)*

## S-16 Marshalling and delegation

**R-MARSHAL-01 (capability rejection, recursive).** Marshalling MUST serialize values into canonical bytes `MarshalledValue(Vec<u8>)` for cross-actor transfer. Unmarshalling MUST validate canonical wire format before constructing target values. *(L41647–41658; L25674–25701; L37946–37951.)*

**R-MARSHAL-02 (explicit delegation).** Raw capability references `Value::Capability(CapRef)` MUST NOT be transferred through ordinary messages; ordinary marshalling MUST reject raw capabilities with `MarshalFault`. Delegation of authority MUST require explicit `Value::DelegatedCapability(DelegatedCapability)` envelopes. *(L25972–26001; L37953–37959.)*

**R-MARSHAL-03 (canonical transport).** Delegated capability envelopes MUST contain explicit attenuation constraints and target actor restrictions. Receiving actors MUST attenuate delegated capabilities through local kernel before use. *(L25674–25701; L26072–26079 (Track B).)*

**R-MARSHAL-04 (semantic marshalling rule).** Cyclic heap structures MUST NOT be marshalled. Marshalling recursive structure depth exceeding limits MUST yield `fault(F_marshal_depth_exceeded)`. *(L8695–8698.)*

---

# Part VI — Persistence

## S-17 Canonical serialization (frozen wire format, Phase 15A)

**R-CANON-01 (purpose & independence).** Canonical serialization (15A) MUST enforce strict canonical bytes representation: single byte order (little-endian), no unassigned tags, no invalid bool values, no invalid discriminant tags, no trailing bytes. Non-canonical encodings MUST be rejected. Duplicate map keys MUST be rejected. Encoded collection counts MUST NOT authorize preallocation of attacker-controlled memory. *(L28185–28228; L28453–28465; L41659–41690.)*

**R-CANON-02 (universal envelope, frozen).** Wire format integers MUST use little-endian encoding (`u16`, `u32`, `u64`, `i64`). Floating-point NaNs MUST be rejected if floating-point types are present.






*(L30532–30543; L33290–33347 (final frozen).)*

**R-CANON-03 (type tags, frozen).** Strings and Symbols MUST be UTF-8 encoded. Invalid UTF-8 byte sequences MUST yield `fault(F_utf8_invalid)`. *(L30532–30598 (stale §1.3); L33087–33154 (final).)*

**R-CANON-04 (Value encoding, frozen).** Collection encodings (List, Tuple, Map) MUST prefix element counts as `u32` length headers. Decoders MUST verify payload byte availability before allocating collection memory. *(L30544–30552 (correction); L33155–33265 (final).)*

**R-CANON-05 (primitives, frozen).** Canonical serialization MUST be strictly injective: `A == B ⇔ encode(A) == encode(B)`. Decoded round-trip MUST satisfy `decode(encode(v)) == v`. *(L33087–33154.)*

**R-CANON-06 (collections, frozen).** Canonical envelope header MUST consist of: magic bytes `0x526F5231`, version `0x01`, domain tag `u8`, payload length `u32`. Header validation failure MUST yield `fault(F_envelope_invalid)`. *(L30566–30573; L34987–35024 (final 15A patch); L38164–38172.)*

**R-CANON-07 (decoder contract, frozen).** Deserialization cursor `ReadCursor` MUST track read offsets explicitly and MUST reject inputs where payload length exceeds available bytes. *(L30575–30586; L32948–33049.)*

**R-CANON-08 (checked arithmetic).** Enum variants MUST be encoded as 1-byte discriminant tags followed by variant payload. Unrecognized discriminant tags MUST yield `fault(F_invalid_discriminant)`. *(L30574–30578; L32948–33265; L33266–33286.)*

**R-CANON-09 (digests).** Bool values MUST be encoded strictly as `0x00` (false) or `0x01` (true). Any other byte value MUST yield `fault(F_invalid_bool)`. *(L28185–28228 (correction); L30588–30590; L28453–28465.)*

**R-CANON-10 (injectivity, scoped claim).** Map keys MUST be sorted in lexicographical byte order. Out-of-order map keys MUST yield `fault(F_map_keys_unsorted)`. *(L30592–30598 (corrected wording); L35068.)*

**R-CANON-11 (golden vectors, normative fixtures).** Canonical serializer MUST NOT allocate dynamic heap memory proportional to unverified length headers during header parsing. *(L30599–30646; L31948–32010 (regenerated); L33266–33286 (freeze).)*

## S-18 Persistence protocol (Phase 15B)

**R-PERSIST-01 (separation).** Persistence layer MUST maintain WAL and GlobalSnapshot storage transactional integrity. Partial writes MUST be detected and rejected during recovery. *(L33757–33790; L35078–35087.)*

**R-PERSIST-02 (two-level framing).** WAL append operations MUST write `WalFrame` records with incrementing `WalSequence` counters. Sequence gaps MUST NOT be permitted. *(L33802–33830; L35088–35110.)*

**R-PERSIST-03 (record taxonomy).** WAL frames MUST calculate SHA-256 checksums over `sequence || kind || payload_length || payload`. Mismatched frame checksums MUST yield `fault(F_wal_checksum_mismatch)`. *(L33861–33900; L35111–35144.)*

**R-PERSIST-04 (snapshot content).** Global snapshots MUST capture complete machine state necessary for resumption: logical_time, ID counters, runnable queue, actor states, capability arena, budget state, effect journal cursor. Snapshots MUST be canonical 15A encoded. *(L26293–26330.)*

**R-PERSIST-05 (atomic snapshot protocol).** Snapshot creation MUST follow atomic protocol: (1) write `SnapshotBegin` marker; (2) write canonical `GlobalSnapshot` payload; (3) fsync payload; (4) write `SnapshotCommit` record with `state_digest`. Incomplete snapshots MUST be discarded during recovery. *(L26216–26240; L35177–35188.)*

**R-PERSIST-06 (sequence continuity).** WAL sequence continuity MUST hold (`s_{n+1} = s_n + 1`); gaps MUST be rejected (obligation tag `WAL-GAP-REJECT` / `WAL-SEQUENCE-CONTINUITY`). *(L35088–35110; L35189–35208.)*

## S-19 Crash recovery

**R-RECOV-01 (durable state).** Durable state `D = ⟨S, L, H⟩` MUST consist of latest committed snapshot S, durable event log L, and durable effect journal H. Recovery MUST satisfy `Recover(D) = Replay(S, L, H)`. *(L26122–26140.)*

**R-RECOV-02 (normative crash matrix T0–T6).** The crash recovery matrix MUST adhere strictly to T0–T6 classifications:

| Crash point | Durable state | Required recovery result |
|---|---|---|
| T0: before `Prepared` | none | Effect does not exist; no budget mutation; resume normal small-step CEK machine execution without host reconciliation |
| T1: after `Prepared` | `Prepared` only | Discard incomplete preparation; resume normal small-step CEK machine execution without host reconciliation |
| T2: after `Issued` | `Issued` | Reconstruct effect state as `Indeterminate`; await host reconciliation |
| T3: after HostInvocation | `Issued` | Reconstruct effect state as `Indeterminate`; await host reconciliation |
| T4: after HostCompletion | `Issued` | Reconstruct effect state as `Indeterminate`; await host reconciliation |
| T5: after `Completed` | `Completed` | Effect complete; state durable; resume execution |
| T6: after `SnapshotCommit` | `SnapshotCommit` | Clean state; resume execution |

*(L35159–35176 (frozen); L28467–28493 (same matrix, restated); L38831–38846.)*

**R-RECOV-03 (recovery algorithm).** Recovery MUST execute the 12-step algorithm: (1) locate newest committed snapshot; (2) verify framing/checksum; (3) decode via 15A `CanonicalDecode`; (4) validate recovered `GlobalState` invariants (budget conservation, no duplicate runnable actors); (5) open WAL, verify framing/checksums; (6) verify sequence continuity, reject gaps; (7) replay records sequentially after snapshot sequence; (8) reconstruct effect journal, validate causal chains; (9) classify interrupted effects (`Indeterminate` vs `Completed`); (10) reconstruct runnable queue; (11) compute final state digest vs trailing checkpoint; (12) enter `RecoveryComplete`, resume deterministic scheduler. [INFORMATIVE: "deterministic" is explicitly defined in S-15 / R-ACTOR-07]. *(L35189–35208; L26272–26300.)*

**R-RECOV-04 (independent recovery).** The recovery engine MUST be an **independent implementation** from the normal execution path (anti-oracle-collapse). Production recovery MUST NOT be used as the reference recovery oracle. *(L35189–35195; L38858–38890.)*

**R-RECOV-05 (strict validation rule).** `Invalid(D) ⇒ RecoveryFault`. The recovery engine MUST NEVER silently repair corruption (the recovery engine MUST NOT drop duplicate runnable actors, MUST NOT adjust budget mismatches, and MUST NOT ignore gaps, checksums, or causality violations). *(L35196–35208; L38254–38272.)*

**R-RECOV-06 (budget recovery invariant).** The three-way budget accounting `C_available + C_escrowed + C_consumed = C_initial` MUST survive crashes identically without discrepancy. *(L35210–35215.)*

**R-RECOV-07 (reconciliation).** `Issued ∧ ¬Completed` effects MUST be handed to the supervisor's reconciliation policy; `Reconciled(E) ⇒ Issued(E)` MUST hold; outcomes MUST be recorded durably (`EffectReconciled`). Reconciliation MUST be the only path by which an `Indeterminate` effect becomes resolved; the system MUST NOT auto-resolve to "not executed". *(L35111–35144; L26249–26262.)*

---

# Part VII — Verification

## S-20 Independent reference model and differential verification

**R-REF-01 (purpose).** An independently implemented executable reference model MUST provide machine-checked evidence that the production implementation conforms to specified semantics: `Observe(Production(X)) = Observe(Reference(X))` MUST hold for every generated input `X` in the comparison domain; for persistence: `Canonical(Recover_P(D)) = Canonical(Recover_R(D))` MUST hold, subject to frozen reconciliation rules. This MUST be treated as differential verification evidence, not a formal proof. *(L35281–35310; L38935–38953.)*

**R-REF-02 (independence boundary).** The reference model MUST NOT call: `ProductionEvaluator, ProductionContinuation, ProductionCapabilityKernel, ProductionBudget, ProductionScheduler, ProductionSerializer, ProductionRecovery, ProductionPersistence, ProductionReplayHost, ProductionTransition`. It MAY consume test inputs/fixtures and emit reference observations/traces. Shared transition implementations MUST NOT be used; shared semantic test fixtures MAY be used. *(L35330–35375; L37696–37721; L28590+ (key rule).)*

**R-REF-03 (reference model scope).** The reference implementation MUST independently model: CEK evaluation, lexical environments, closures, calls, capability derivation, revocation, budgets, actors, scheduling, effects, persistence, and recovery. It MUST be intentionally small, direct, explicit, deterministic, independently structured, and slow where clarity demands. Performance MUST be explicitly secondary to transparency. [INFORMATIVE: "deterministic" is explicitly defined in S-02 / R-CORE-08]. *(L41848–41866; L35281–35310; L35313–35322; L35341.)*

**R-REF-04 (non-goals).** The reference model MUST NOT redefine semantics, MUST NOT introduce a second serialization format, MUST NOT reproduce host implementation details, MUST NOT claim to prove correctness mathematically, MUST NOT share production transition code, and MUST NOT optimize. *(L35326–35339.)*

**R-REF-05 (normalized observation).** Differential comparison MUST use normalized observations, not internal structure: terminal states, event trace, effect trace, resource partitions, authority outcomes, scheduler trace, faults, recovered state. Internal details (addresses, pointers, allocator behavior, Rust enum layout, OS handles, host object identity) MUST be excluded unless explicitly semantic. The comparator MUST report the **first divergence**. Comparing only final return values MUST NOT be permitted. *(L38420–38470 (§16); L38935; L41869–41906.)*

**R-REF-06 (harness enforcement).** The harness MUST include mocked boundary enforcement: a `PanicHost` that panics if `execute()` is called before all gates pass; a `MockKernel` asserting exactly one `authorize`/`derive` call with the exact expected parameters. The production/reference boundary MUST be treated as a first-class test subject. *(L27891–27902.)*

## S-21 Test infrastructure, mutation, and CI

**R-TEST-01 (execution modes, frozen baselines).** The test suite MUST support three execution modes:
- **Exhaustive (small-state):** enumeration over bounded state; baseline `expression depth ≤ 4, actors ≤ 2, capabilities ≤ 2`; MUST run on every commit. The CI time target MUST be treated as a performance budget, **not** a semantic constraint; if state space grows, the runner MUST partition, shard, or cache — and MUST NOT reduce semantic coverage to preserve a time target.
- **Property-generated:** randomized layered generation (structure → type validity → capabilities → budgets → actor topology → effects → persistence corruption), aggressive shrinking; MUST run nightly.
- **Stress:** `50k–100k` call depth, `100+` actors, long mailboxes, large WAL traces, repeated crash/recovery, large continuation states; MUST run weekly and on release candidates.
*(L38587–38715; L37251–37268 (pre-correction `<2 min` wording superseded — `C-11`).)*

**R-TEST-02 (reproducible counterexamples).** Every generated test case MUST be reproducible. Every failure MUST save the structured artifact: `seed, generator_version, semantic_version, test_case_version, program, initial state, capabilities, budgets, actor topology, scheduler_trace, host_trace, persistence image, crash_trace, production_observation, reference_observation, first_divergence, minimized case`. The artifact MUST be runnable locally. *(L38891–38920; L37293–37315; L38587–38624.)*

**R-TEST-03 (shrinking protocol).** Shrinking order MUST proceed as: (1) actor count, (2) expression depth, (3) call arity, (4) bindings, (5) mailbox messages, (6) capability scope, (7) budget dimensions, (8) WAL records, (9) effect count, (10) crash position. The shrinker MUST preserve the failure predicate; every failure MUST yield a minimal reproducible artifact. *(L38441–38463.)*

**R-TEST-04 (mutation registry, baseline frozen).** The versioned baseline mutation registry MUST include:
`M001` reverse argument evaluation; `M002` skip arity precheck; `M003` allow non-function application; `M004` accept revoked capability; `M005` omit capability ceiling; `M006` permit capability amplification; `M007` omit budget gate; `M008` release indeterminate escrow; `M009` permit negative resources; `M010` allocate EffectId before authorization; `M011` schedule blocked actor; `M012` duplicate runnable queue entry; `M013` break mailbox FIFO; `M014` accept duplicate canonical map key; `M015` ignore WAL sequence gap; `M016` ignore checksum mismatch; `M017` accept mismatched EffectDigest; `M018` resume after corrupted receipt.
The registry MUST be additive: a previously killed mutant MUST remain a regression requirement. *(L38473–38492; L37239–37249 (categorization).)*

**R-TEST-05 (kill rate).** The target MUST be `MutationKillRate = 100%` for all registered **non-equivalent** mutations. Any surviving non-equivalent mutant MUST block verification. Equivalent mutants MUST require explicit adjudication and documentation. Mutation survivors MUST be treated as release-blocking defects. *(L38494–38500; L37390–37400.)*

**R-TEST-06 (mutation validation).** The verification system itself MUST be tested: for each mutation — inject, build, run targeted test, run differential suite, assert mutant killed. Testers MUST NOT merely run the framework without asserting mutant kills. *(L38515–38540.)*

**R-TEST-07 (semantic coverage, obligation-tagged).** Coverage MUST be tracked per stable verification-obligation tag (e.g., `CEK-CALL-ARITY-PRECHECK, CEK-CALL-ARGS-LTR, CEK-CLOSURE-LEXICAL-CAPTURE, CAP-DERIVE-NO-AMPLIFICATION, CAP-REVOCATION-ANCESTOR, BUDGET-CONSUMPTION-CONSERVATION, BUDGET-ESCROW-CONSERVATION, EFFECT-ISSUE-DURABLE-BEFORE-HOST, EFFECT-RECEIPT-DIGEST-VALIDATION, SCHED-FIFO, SCHED-BLOCKED-NOT-SCHEDULED, MARSHAL-NO-RAW-CAPABILITY, WAL-SEQUENCE-CONTINUITY, RECOVERY-ISSUED-INDETERMINATE, SNAPSHOT-COMMIT-INTEGRITY`). Coverage metrics MUST be treated as evidence and MUST NOT serve as a substitute for the differential oracle. *(L38523–38560; L37402–37414.)*

**R-TEST-08 (crash-injection matrix).** The crash harness MUST exercise all T0–T6 crash points and MUST verify the exact expected classification, especially `Issued ∧ ¬Completed ⇒ Indeterminate` and `Prepared ∧ ¬Issued ⇒ Discard`. *(L38831–38846; L35216–35236 (crash harness).)*

**R-TEST-09 (fault adjudication).** Every production/reference divergence MUST be classified as one of: production defect | reference defect | harness defect | specification ambiguity. Testers MUST NEVER patch the oracle merely to make a test pass. Specification ambiguity MUST require an explicit specification decision before implementation proceeds. *(L38848–38862; L37404–37414.)*

**R-TEST-10 (CI gates, frozen).** The CI pipeline MUST enforce frozen gates:
- **Pull request:** format, lint, unit tests, exhaustive small-state, core differential tests, serialization conformance.
- **Nightly:** property generation, mutation registry, full differential suite, persistence fuzzing, crash injection, semantic coverage report.
- **Release candidate:** all nightly suites, stress tests, full crash matrix, `MutationKillRate = 100%`, determinism checks, recovery differential tests, security regression suite.
No release MUST be accepted with an unexplained differential mismatch or surviving non-equivalent mutation. [INFORMATIVE: "determinism" is explicitly defined in S-02 / R-CORE-08]. *(L38864–38890; L37287–37292.)*

**R-TEST-11 (final acceptance condition).** The implementation MUST be conformant only when `Observe_P(X) = Observe_R(X)` over the tested state space **and** `MutationKillRate = 100%` for all non-equivalent registered mutations **and** `Canonical(Recover_P(D)) = Canonical(Recover_R(D))` over the tested persistence state space (subject to authoritative external-effect reconciliation). 'Code compiles', 'unit tests pass', and 'coverage is high' MUST NOT be treated as completion. *(L38885–38911; L41196–41210.)*

---

# Part VIII — Engineering and claims

## S-22 Repository structure and crate responsibilities

**R-REPO-01 (workspace layout, frozen boundaries).** The workspace MUST separate untrusted language data → compiler → trusted executable representation → machine → authority/resources → durable effects → host, and MUST independently maintain production ↔ observations ↔ reference. Top-level names MAY change for organizational reasons; dependency and trust boundaries MUST NOT change. The layout MUST follow (frozen intent): `crates/{ror-core, ror-compiler, ror-kernel, ror-runtime, ror-persistence, ror-host, ror-agent, ror-reference, ror-differential, ror-testkit}`. *(L39140–39195; L41406–41424.)*

**R-REPO-02 (crate contracts, normative).** Crate contracts MUST strictly conform to responsibilities:
- `ror-core`: lowest-level semantic domain (Symbol, ActorId, CapRef, EffectId, EventSequence, LogicalTime, Expr, Value, FunctionValue, Environment, Constraint, Effect, EffectCost, Budget, Consumable, Reserved, Fault, MachineEvent). Depends on std only. MUST NOT contain host calls, filesystem, networking, scheduler, persistence, capability authority storage, or LLM integration.
- `ror-compiler`: Block → parse → NormalizedAST → ValidatedPlan → PlanIR → capability analysis → resource analysis → ExecutablePlan. `ExecutablePlan` constructors private.
- `ror-kernel`: CapabilityKernel, AuthorityNode, derivation, revocation, authorization, budget primitives, logical-time validation. `AuthorityNode` invisible to evaluator/runtime.
- `ror-runtime`: CEK machine, actors, scheduler, effects.
- `ror-persistence`: WAL, snapshots, effect journal, recovery.
- `ror-host`: host execution and replay boundaries.
- `ror-agent`: planner/observation/supervisor integration.
- `ror-reference`: independent executable semantic model.
- `ror-differential`: generator, runner, comparator, shrinking.
- `ror-testkit`: test infrastructure and controlled doubles.
*(L39196–40762 (responsibility detail); L41806–41846 (summary table).)*

*(Non-normative note, added by the terminology pass — the normative bullet above is unchanged.)*
*The `ror-compiler` pipeline in R-REPO-02 reproduces the turn-[58] diagram (L39265–39280) faithfully, and it is reproduced here unchanged. It is **one of three** stage sequences in the frozen source, and the frozen struct declarations contradict its ordering: `NormalizedAST` is the **content** of `ParsedBlock` (L864), not a stage before `ValidatedPlan`, and `PlanIR` is the **content** of `ValidatedPlan` (L865), not a stage after it. Two declared stages — `ParsedBlock` (L864) and `CapabilityCheckedPlan` (L866) — do not appear in it at all, and `NormalizedAST` and `PlanIR` are never declared anywhere (L1–42312). An implementer MUST NOT treat this rendering as the stage list. Filed as `term/02-collisions.md` X-02, X-41, X-29, X-30 and `spec/06` C-52; `mod/02-compiler.md` carries the same note. Nothing here is renamed or reordered, because the collision is in the frozen source and resolving it by editing either side would be a silent semantic change (R-SCOPE-03).*

**R-REPO-03 (boundary enforcement).** The repository MUST make boundaries hard to violate accidentally, enforced by Cargo dependencies, Rust visibility, type construction, trait boundaries, module structure, tests, mutation testing, and CI. Production crates MUST NOT depend on reference crates. *(L41223–41273.)*

## S-23 Milestones and implementation order

**R-ORDER-01 (implementation order, frozen).** Implementation MUST proceed in strict dependency order: 01 core domain types → 02 canonical serialization → 03 compiler artifacts → 04 capability kernel → 05 budget algebra → 06 CEK evaluator → 07 lambda/call → 08 attenuation → 09 effects → 10 actors → 11 scheduler → 12 marshalling/delegation → 13 persistence → 14 crash recovery → 15 LLM boundary → 16 reference model → 17 differential harness → 18 mutation framework → 19 CI → 20 stress/security validation. *(L37793–37812 (§3); L42108–42142.)*

**R-ORDER-02 (milestones, frozen acceptance).** Milestones MUST satisfy frozen acceptance criteria:

| Milestone | Acceptance |
|---|---|
| M0 Workspace | `cargo check/test/fmt/clippy` pass; no semantic functionality required |
| M1 Canonical serialization | golden vectors pass; round-trips pass; malformed inputs reject; duplicate keys reject; canonical bytes deterministic |
| M2 Pure CEK | Expr/Value/CEK step, environment, lexical capture, stackless frame invariants pass |
| M3 Lambda / Call | closure capture, application LTR, arity precheck pass |
| M4 Capability / Attenuation | CapRef opacity, derive, partial order, revocation cascade pass |
| M5 Effects | 16-step request sequence, issuance, receipts, host mock pass |
| M6 Actors | spawn, mailbox FIFO, async send, blocking receive, scheduler pass |
| M7 Persistence | WAL frame encoding, sequence continuity, snapshot commit pass |
| M8 Differential verification | reference model agreement `Observe(P) == Observe(R)` passes |
| M9 Mutation gate | baseline mutation registry kill rate target satisfied |
| M10 Crash/recovery gate | T0–T6 crash matrix and recovery differential tests pass |
| M11 Release candidate | full test suite, stress, security review, zero open high defects pass |

[INFORMATIVE: "deterministic" in M1 acceptance is explicitly defined in S-17 / R-CANON-05]. *(L40763–41100; L42165–42190.)*

**R-ORDER-03 (first security gate).** Before implementing external effects, the implementer MUST demonstrate `Block ⇏ ExecutablePlan` and production/reference differential agreement for Value/Var/Let/Seq/If/Lambda/Call (including faults); the differential harness MUST be operational before Phase 09 effects. *(L41155–41195.)*

**R-ORDER-04 (first sprint, frozen task set).** First sprint execution MUST complete frozen tasks ROR-001 … ROR-016 (workspace, toolchain, core types, canonical cursor/envelope/primitives/Value, golden vectors, malformed-input suite, duplicate-map-key regression, reference crate, differential observation types, harness stub). *(L41091–41112.)*

**R-ORDER-05 (definition of done).** A component MUST be treated as complete if and only if implementation + unit tests + reference semantics + differential tests + obligation mapping + mutation coverage + documentation (where applicable) are present and verified. *(L41124–41142.)*

## S-24 Conformance claims and prohibited shortcuts

**R-CLAIM-01 (scoped conformance claim, frozen wording).** The scoped engineering claim MUST strictly state: *"The independent reference model, exhaustive/property-based tests, mutation testing, and crash-injection suite provide machine-checked evidence that the implementation conforms to the frozen calculus over the tested state space."* Implementers MUST NOT claim that test execution constitutes a mathematical proof of the entire calculus. *(L38913–38917; L42191–42265; L28247–28268.)*

**R-CLAIM-02 (prohibited shortcuts, frozen).** Prohibited shortcuts MUST NOT be used. Never: use recursive evaluation; trust AST shape as a security boundary; expose authority internals; clone capabilities wholesale during spawn; transfer raw capability references through ordinary messages; use wall-clock time for deterministic semantics; use saturating budget arithmetic; invoke host before durable issuance; infer external-effect nonexecution from missing completion; silently repair persistence corruption; use production recovery/serialization as the reference oracle; compare only final return values; accept surviving mutations without adjudication; reduce semantic coverage to satisfy CI timing; weaken tests because implementation is inconvenient. [INFORMATIVE: "deterministic semantics" is explicitly defined in S-02 / R-CORE-08]. *(L38858–38890; L42144–42188.)*

**R-CLAIM-03 (engineering response format).** Implementation reports MUST include: component implemented, frozen invariants exercised, production/reference boundary, tests added, differential tests added, mutation tests affected, coverage obligations satisfied, open issues/ambiguities. *(L38808–38846.)*

**R-CLAIM-04 (start condition).** Implementers MUST NOT propose another semantic phase. Implementation MUST begin from the lowest dependency layer, with the independent reference model alongside production, keeping the differential harness operational as the semantic baseline. *(L38921–38928.)*

---

# End of canonical specification

Cross-references: obligation matrix `03-obligation-matrix.md`; dependency graph `04-dependency-graph.md`; terminology `05-terminology.md`; contradictions/ambiguities `06-contradictions-ambiguities.md`; implementation mapping `07-implementation-mapping.md`; verification/evidence mapping `08-verification-mapping.md`; unresolved decisions `09-unresolved-decisions.md`; machine index `10-index.json`.
