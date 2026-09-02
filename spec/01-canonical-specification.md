# Red-on-Rust — Canonical Specification (Cleaned)

**Status of this document:** normative cleaned rendering of the frozen source `Red-on-Rust.md`.
**Rule:** where this rendering and the source differ, the source's latest frozen text governs; any discrepancy must be recorded per `00-overview.md` §1. Requirement IDs (`R-…`) are defined in `03-obligation-matrix.md`; this file is the canonical home of their normative text.

---

# Part I — Foundations

## S-01 Scope, status, and conventions

**R-SCOPE-01.** Red-on-Rust is a deterministic, capability-scoped, resource-bounded, crash-recoverable execution machine for probabilistically generated programs. It is a Rust-based execution substrate for a family of homoiconic, dialect-oriented languages inspired by the REBOL/Red lineage. *(Provenance: turn [60]/README "Core Thesis"; L41293–41300.)*

**R-SCOPE-02.** The architecture, specification, reference contract, and verification contract are FROZEN. The repository is in BOOTSTRAP state. A frozen specification is not a verified implementation; frozen means the requirements are stable, not that evidence of conformance exists. *(L38929–38942, L41297–41315.)*

**R-SCOPE-03 (normative process rule).** The implementer MUST NOT redesign, reinterpret, simplify away, or silently modify frozen semantics (CEK semantics, evaluation order, lexical scoping, closure semantics, capability algebra, attenuation, revocation, budget algebra, effect authorization, effect issuance protocol, actor isolation, deterministic scheduling, marshalling rules, delegation semantics, canonical serialization, persistence protocol, crash matrix, recovery classification, LLM trust boundary, reference-model independence, differential-testing contract). If implementation difficulty exposes an ambiguity, the implementer MUST STOP and report it; semantic ambiguity MUST NOT be resolved by inventing behavior. *(L37664–37686.)*

**R-SCOPE-04.** The production implementation and the executable reference model MUST share zero core implementation logic (no `reference_* → production_*` calls for step, authorize, budget, recover, encode, scheduler). Shared semantic test fixtures are allowed; shared transition implementations are forbidden. *(L37696–37721.)*

## S-02 Core thesis and central invariants

**R-CORE-01 (central external-effect invariant).** `LLMOutput ∧ UntrustedInput ↛ ExternalEffect`. The central security boundary is the machine — not the language surface and not the model generating the program. *(L41320–41335; L27505–27513.)*

**R-CORE-02 (external-effect chain).**
`ExternalEffect(E) ⇒ ValidatedPlan(P) ∧ Authorized(E,κ,t) ∧ CapabilityWithinCeiling(E) ∧ BudgetAvailable(E) ∧ DeadlineValid(E,t) ∧ HostPolicyOK(E) ∧ Issued(E)`. *(L41337–41351; L27491–27509.)*

**R-CORE-03 (no unauthorized effects).** `¬Authorized(A,E,t) ⇒ ¬ExternalEffect(E)` (equivalently `¬Authorized ⇒ ¬Request` at the operational level). *(L42056–42064; L7413–7419.)*

**R-CORE-04 (no authority amplification).** `derive(A,C) ≼ A` always holds. *(L42066–42072; L6399–6406.)*

**R-CORE-05 (no budget teleportation).** `C_available + C_escrowed + C_consumed = C_initial`, with explicit accounting partitions; spawn is an ownership transfer, not creation or consumption. *(L42074–42080; L28203–28240.)*

**R-CORE-06 (no host-before-durability).** `HostInvoked(E) ⇒ DurableIssued(E)`. An effect is not "issued" because an in-memory object exists; durable issuance means the `Issued` record is durable. *(L42082–42088; L35150–35156.)*

**R-CORE-07 (no raw capability transfer).** `OrdinaryMarshal(Value::Capability) ⇒ Rejected`. Authority crosses actor boundaries only via explicit delegation. *(L42090–42098; L25972–26001.)*

**R-CORE-08 (determinism).** `InitialState + SchedulerTrace + HostTrace ⇒ UniqueMachineTrace` (with an accepted planner trace for end-to-end runs). The LLM's stochasticity is above the deterministic machine, never inside it. *(L41623–41646; L27518–27547.)*

**R-CORE-09 (causal crash recovery).** `Recover(Snapshot, EventLog, EffectJournal) ≡ PreCrashMachineState` for every crash at a defined persistence boundary, **provided** every interrupted external effect is (a) durably reconciled, (b) safely idempotent/replayable, or (c) explicitly classified `Indeterminate` and prevented from silent continuation. The system MUST NOT infer "not executed" from a missing completion record. *(L27551–27569; L35159–35176.)*

**R-CORE-10 (no silent recovery corruption).** Invalid persistence state produces an explicit `RecoveryFault`. It is never silently repaired by mutation (no dropping duplicate runnable actors, no "fixing" budget mismatches, no ignoring sequence gaps or checksum failures). *(L42100–42105; L35196–35208.)*

## S-03 Trust model and trusted computing base

**R-TRUST-01.** Trust assignment (normative):

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

*(L41823–41841; L27611–27624.)*

**R-TRUST-02.** `LLM output ∉ TCB authority`. The TCB consists of: CEK machine, capability kernel, budget algebra, deterministic scheduler, canonical serializer, WAL/recovery state machine, effect boundary. *(L28178–28230.)*

**R-TRUST-03 (no hidden authority).** The LLM, AST, evaluator, scheduler, host adapter, or ordinary `Value` representation MUST never manufacture authority. Capabilities are opaque handles; only the capability kernel decides authority. The evaluator may call `derive(capability, constraint, logical_time)` and `authorize(capability, effect, logical_time)`; it MUST NOT inspect authority internals. *(L37722–37748; L19153–19175.)*

## S-04 System architecture and component boundaries

**R-ARCH-01 (pipeline).** The normative end-to-end path is:

```
LLM/Planner → PlanProposal → staleness validation → Block
→ parse → normalize → validate → lower → capability analysis → resource bounds
→ ExecutablePlan → CEK Machine → Capability Kernel / Budget System
→ Effect Issuance → Durable Boundary → Host
```

*(L37750–37780; L27287–27310.)*

**R-ARCH-02.** The verification architecture is independent and co-equal:

```
Production → Observation (normalized) → Reference
```

Production and reference do not share core transition logic. *(L41406–41424; L37696.)*

**R-ARCH-03 (boundary integrity).** The boundaries among compiler, capability kernel, evaluator, runtime, persistence, host, and reference model MUST remain intact: a raw `Block` has **no path into `step()`**; `ExecutablePlan` constructors are private to the compiler; the production runtime only ever receives an `ExecutablePlan`. *(L9086–9097; L39296–39318.)*

**R-ARCH-04.** Dependency direction (normative): capability algebra → capability kernel → effect/cost & revocation → executable plan → actor state → global config → scheduler → host executor / replay host. *(L9059–9085.)*

## S-05 LLM / planner boundary

**R-PLANNER-01 (proposal data).** The planner returns a `PlanProposal { observation_sequence: EventSequence, block: Block, planner_metadata }`. `LLMOutput ∈ Data`, not authority. *(L27176–27198.)*

**R-PLANNER-02 (cannot).** The model MUST NOT: allocate capabilities; authorize effects; modify budgets; modify the event log; allocate actors directly; invoke the host; bypass validation; alter scheduler state. It may only propose a `Block`, which enters the ordinary compiler pipeline. *(L27271–27285; L37781–37790.)*

**R-PLANNER-03 (staleness).** A proposal is causally bound to the machine state from which it was generated. The machine MUST verify `proposal.observation_sequence = current_planning_epoch` and otherwise reject it as `StalePlan` — a normal machine-visible outcome, with no state mutation. *(L27199–27236; L28373.)*

**R-PLANNER-04 (planner determinism).** The LLM need not be deterministic. The machine theorem is `InitialState + Plan + SchedulerTrace + HostTrace ⇒ UniqueMachineTrace`. For exact end-to-end replay, the machine records a `PlannerAccepted { observation_sequence, proposal_digest, block }` and replay consumes the recorded proposal instead of querying the LLM. *(L27392–27414.)*

**R-PLANNER-05 (LLM outer-loop conformance, normative test obligation).** The conformance suite MUST include: (1) untrusted-input rejection — raw/malformed/malicious `Block` data fed directly to the runtime is rejected at the compiler boundary; (2) stale-proposal rejection — advanced machine state + old proposal ⇒ rejection without state mutation; (3) end-to-end replay — live session vs replay with recorded proposal + `ReplayHost` ⇒ byte-for-byte identical final `GlobalState` and `EventLog`. *(L27920–27931; L28513–28521.)*

## S-06 Compilation boundary

**R-COMPILE-01.** `Block ≠ ExecutablePlan`. Only validated executable plans enter the trusted machine; no `Block` bypasses compilation. *(L41440–41452; L3834–3838.)*

**R-COMPILE-02 (pipeline).** Compilation MUST pass the stages: parse → normalize → validate → lower → capability analysis → resource analysis. Any failed stage yields `fault(F_compilation)`; no raw `Block` reaches execution. *(L1930–1960 (J1–J4 and compilation theorem, superseded form); L39253–39267 (frozen pipeline).)*

**R-COMPILE-03 (static checks, frozen intent).** The combined static judgment `Γ; κ_static ⊢ e : τ ! F @ B` threads type, possible-effect set `F` (conservative over-approximation; pure terms yield `F = ∅`), capability requirements, and a static budget upper bound `B`. If the term's worst-case cost exceeds `B_max`, compilation fails. *(L3874–3905 (v2 form); L1953–1980 (v1 J1–J4, superseded form).)*

**R-COMPILE-04 (plan immutability / temporal integrity).** An `ExecutablePlan` is immutable; a new plan can only be produced by another validated compilation transition (plan₁ → execution/observation → planner → Block₂ → compiler → plan₂). A plan authorized at `t₀` never silently acquires new authority at `t₁`. *(L1722–1745; L2052–2070 (v1 Theorem 6).)*

**R-COMPILE-05.** `ExecutablePlan` constructors MUST remain private to the compiler crate. *(L39296–39318.)*

**Non-normative (gap).** The detailed effect-set inference (v1 judgment J2, `Γ ⊢ e ↝ Φ`) is not re-specified in the frozen pipeline stages; see `U-22` in `09-unresolved-decisions.md`.

---

# Part II — Language and machine semantics

## S-07 Core calculus (syntax)

**R-CALC-01 (value domain, machine).** The machine value domain is:
`v ::= Unit | Bool(bool) | Integer(i64) | Bytes(Vec<u8>) | Symbol(Symbol) | String(String) | List(Vec<Value>) | Tuple(Vec<Value>) | Function(FunctionValue) | Capability(CapRef) | Actor(ActorId)`.
`Value::Capability(CapRef)` does **not** grant the evaluator inspection rights; the evaluator may only pass the opaque reference back to the kernel. *(L12290–12312 (turn [21]); L19153–19175.)*

**R-CALC-02 (expression domain, frozen surface).** The frozen `Expr` AST (declarative operations only; no host callbacks in the AST) has the constructors:
`Value(Value) | Var(Symbol) | Let { name, value, body } | Seq { first, second } | If { condition, then, else } | Call { function, args } | Lambda { params, body } | Attenuate { capability, constraint, body } | Request { capability, operation, target, params } | Spawn { body, budget } | Send { target, value } | Receive`.
*(L12132–12170 (turn [21]).)*

**R-CALC-03 (symbols).** Runtime variable identity is `Symbol(u32)`, not `String`. The compiler maintains the name→Symbol mapping; the evaluator operates entirely on symbols. *(L12250–12270.)*

**R-CALC-04 (effect descriptor).** An effect is immutable data: `Effect { capability: CapRef, operation: Op, target: Target, params: Params, cost: EffectCost }`. Effect identity is canonical: `EffectDigest = SHA-256(canonical_bytes(effect))`. `EffectId` (monotonic u64 allocator counter) and `EffectDigest` (semantic identity) serve different purposes and both MUST be validated on receipt. *(L9288–9348 (early form, capability carried in `EffectRequest.cap`, superseded); L23726–23772 (frozen form).)*

**R-CALC-05 (effect cost, frozen form).** `EffectCost { issue: Consumable, complete_max: Consumable, reserve: Reserved }`. `issue` is charged at request time; `complete_max` is escrowed at issuance so completion accounting cannot fail; `reserve` is reserved at request and released at receipt. *(L25799–25825 (Phase 12 correction); L23726–23772 (pre-correction form, superseded).)*

**R-CALC-06 (fault taxonomy).** The frozen fault taxonomy is the Rust `Fault` enum: `Capability(CapabilityError) | BudgetExhausted | DeadlineExceeded | HostPolicyDenied(HostPolicyError) | EffectCanonicalization(EffectError) | Host(HostFault) | ReplayCorruption | InvalidReceipt` (plus `StalePlan` at the planner boundary). *(L23784–23819; L27236. See C-08 for naming inconsistencies in earlier drafts.)* **Non-normative annotation (X-64, X-67, X-68, C-54, C-57, C-58; the normative sentence above is unchanged and governs):** `StalePlan` is *not* a variant of any `pub enum Fault` declaration — it occurs only as a bare token at L27236 and in prose at L28373, and `Fault::StalePlan` occurs nowhere in L1–42312; the parenthetical is therefore a canonicalization-layer addition, not frozen text, and L27236 supports the *staleness* fact but not *variant membership*. The eight enumerated variants are correct as written, but the frozen declaration at L23806 carries an explicit `// ... (previous faults)` elision at L23807, so the list is not closed by the source. The payload type `HostFault` in `Host(HostFault)` is declared once (L10820) with two variants while eight undeclared `HostFault::` paths are used, six on the frozen replay path (C-57, **blocking**); and `HostFault` and `Revoked` additionally denote *members of the v1 fault grammar* `F` at L1949, i.e. a different level of the taxonomy than the flat variant list stated here (C-58). Whether `StalePlan` should join the taxonomy is U-08's decision; this annotation records the defect rather than silently amending normative text (R-SCOPE-03).

**R-CALC-07 (effect properties).** Effect semantics carry replayability/reversibility/idempotence properties; an effect's *machine result* can be replayed even when the real-world operation cannot. **Non-normative:** the per-operation property table (FileRead/FileWrite/NetGet/NetSend/SpawnProcess with yes/no/sometimes/depends entries) is an illustrative example, not a frozen operation table (see `U-06`, `C-05`). *(L2141–2156 (v1) / L3858–3873 (v2) (declared domain + illustrative table); L26669–26735 (Phase 14 effect classes).)*

**R-CALC-08 (configuration).** Machine configuration `Σ = ⟨e, ρ, κ, B, t, H, L⟩` (current term, local environment, capability kernel, budget, logical time, isolated heap, append-only event log); global configuration `G = ⟨A, t, L, N_h, N_a⟩` (actors, logical time, event log, effect-ID allocator, actor-ID allocator). Logical time, ID allocation, and the event log are strictly global; actors hold only isolated execution state. *(L7119–7144; L8653–8682; L24148–24163.)*

## S-08 CEK machine

**R-CEK-01 (explicit machine).** Evaluation uses an explicit CEK-style machine: state `EvalState { expr: Expr, env: Environment, continuation: Continuation }`. The evaluator MUST NOT depend on recursive host-language calls for call-stack management; continuation state is explicit, serializable, replayable, recoverable. *(L41484–41499; L37800–37812.)*

**R-CEK-02 (value-return invariant, hard).** A value is terminal only when its continuation is empty:
`Value ∧ K = ε ⇒ Halt`; `Value ∧ K ≠ ε ⇒ Resume(K, Value)`.
The pattern `Expr::Value(v) => Halt(v)` without checking the continuation is a violation. *(L16878–16905 (frozen); L17379–17412 (correction, same rule); L37826–37838.)*

**R-CEK-03 (continuation frames).** The frozen frame set is:
`LetValue { name, body, env } | Seq { second, env } | If { then, else, env } | CallFunction { args, env } | CallArgument { function, evaluated, remaining, caller_env } | Attenuate { name, body, env } | RequestCapability { operation, target, params, env } | RequestTarget { capability, operation, params, caller_env } | RequestArgument { capability, operation, target, evaluated, remaining, caller_env }`.
`function.env` (closure lexical environment) and `caller_env` (call-site environment) are semantically different and MUST never be conflated. *(L16928–16958; L23821–23856.)*

**R-CEK-04 (lambda).** Lambda creation is pure and deterministic: it captures the lexical environment at creation and produces `FunctionValue { params, body, env }`; the resulting value goes through the ordinary value-return mechanism (lambda creation does not immediately halt the machine). *(L16971–16995; L19095–19110 (attenuate/lexical invariant context).)*

**R-CEK-05 (call).** Calls evaluate strictly: function → argument 0 → argument 1 → … → argument N → apply (left-to-right). Arity mismatch is detected **immediately after function evaluation and before any argument evaluation**. Application binds parameters in the captured closure environment: `ρ' = ρ_closure[x₁↦v₁, …, xₙ↦vₙ]`; the caller's environment is not used to resolve free variables in the body (lexical-closure invariant). *(L16878–16905 (frozen); L37840–37862; L18723–18851.)*

**R-CEK-06 (continuation preservation).** For pure transitions the continuation length changes by exactly +1 on entry or −1 on resume; no transition silently discards or duplicates frames. *(L14632–14642.)*

**R-CEK-07 (progress & preservation).** A well-typed, well-budgeted configuration is either a value, a fault, pending an effect, blocked on a message, or can take a step; every transition preserves well-typedness and well-budgetness. *(L7273–7277; L8850.)*

## S-09 Capability algebra

**R-CAP-01 (semantic domains, v0.2).** Five foundational domains:
- **Operations** `O`: finite enumerable set of atomic actions.
- **Scope** `S`: with interpretation `⟦S ⊆ Target`, order `S₁ ≼_S S₂ ⇔ ⟦S₁⟧ ⊆ S₂⟧`, meet `S₁ ⊓ S₂` with `⟦S₁ ⊓ S₂ = ⟦S₁ ∩ ⟦S₂`.
- **Parameter constraint** `Q`: predicates `Params → Bool`; order by implication `Q₁ ≼_Q Q₂ ⇔ ∀p. Q₁(p) ⇒ Q₂(p)`; meet by conjunction.
- **Resource limit** `R`: resource ceilings with component-wise order `≤` and meet (component-wise min).
- **Lifetime** `T`: temporal intervals `[t_start, t_end]`; order by subset; meet by interval intersection.

The implementation may use various representations (globs, CIDR, …) but the algebra operates on semantic interpretations. *(L6354–6379.)*

**R-CAP-02 (operation-indexed authority).** Authority is indexed by operation to prevent cross-operation contamination: `A = { (o, A_o) | o ∈ O_granted }` with `A_o = ⟨S, Q, R, T⟩`. *(L6370–6380.)*

**R-CAP-03 (partial order).** `A₁ ≼ A₂` iff `O₁ ⊆ O₂` and for all `o ∈ O₁`: `S₁ ≼_S S₂ ∧ Q₁ ≼_Q Q₂ ∧ R₁ ≤ R₂ ∧ T₁ ⊆ T₂`. *(L6381–6390.)*

**R-CAP-04 (constraint vs authority).** A `Constraint` is a *request to narrow* an existing grant, conceptually distinct from `Authority`. *(L6391–6396; L6406.)*

**R-CAP-05 (derivation).** `derive(A, C) = { (o, derive_op(A_o, C_o)) | o ∈ O_A ∩ O_C }` where `derive_op(⟨S,Q,R,T⟩, ⟨S_c,Q_c,R_c,T_c⟩) = ⟨S ⊓ S_c, Q ⊓ Q_c, R ⊓ R_c, T ⊓ T_c⟩`. **Invariant:** `derive(A,C) ≼ A` holds by definition of meet. *(L6397–6404; Theorem 1, L6657–6661.)*

**R-CAP-06 (canonical authorization predicate).** For effect `E = ⟨op, target, params, cost⟩` at logical time `t`:
`Authorized(A, E, t) ⇔ op ∈ O_A ∧ target ∈ ⟦A_op.S⟧ ∧ A_op.Q(params) ∧ cost ≤ A_op.R ∧ t ∈ A_op.T`.
The `cost` here is the effect's static resource requirement checked against the capability ceiling `R_A`; the dynamic execution budget is checked separately (dual gate). *(L6406–6421; L6647–6656.)*

**R-CAP-07 (revocation / lineage).** `Valid(c, t) ⇔ Live(c) ∧ t ∈ Lifetime(c) ∧ ∀a ∈ Ancestors(c). Live(a)`. Revoking a parent sets `Live(parent) = false`; descendants are invalidated lazily by walking the ancestor chain during the `Valid` check (O(d), d = lineage depth). **No authority amplification** and **ancestor revocation** are frozen obligations (tags `CAP-DERIVE-NO-AMPLIFICATION`, `CAP-REVOCATION-ANCESTOR`). *(L6434–6445; L6647–6656.)*

**R-CAP-08 (algebra theorems, frozen statements).**
- Theorem 1 (Attenuation soundness): `derive(A,C) ≼ A`.
- Theorem 2 (Authority monotonicity): `A' ≼ A ∧ Authorized(A',E,t) ⇒ Authorized(A,E,t)`.
- Theorem 3 (Attenuation corollary): assuming `Authorized(A,E,t)`, `Authorized(derive(A,C),E,t) ⇔ Satisfies(C,E,t)`.
These are `SPECIFIED` statements with proof sketches in the source; no mechanized proof exists in the repository (`PROVEN` is NOT claimed). *(L6422–6433; L6657–6671.)*

**R-CAP-09 (time).** Time `t` is never fetched from the host OS; it is an explicit component of machine state (logical clock / deterministic timestamp), ensuring replay determinism. Wall-clock time is forbidden as semantic machine state. *(L6434–6436; L38858–38890.)*

## S-10 Capability kernel

**R-KERN-01 (opaque references).** `CapRef { index: u32, generation: u32 }` is opaque and generation-safe; fields are private; there is no public constructor from arbitrary integers; `CapRef`s are constructed only by the kernel. *(L9127–9133; L10178–10208.)*

**R-KERN-02 (API contract).** Public kernel interface:
- `authorize(cap: CapRef, effect: &Effect, t: u64) -> Result<(), Fault>` — resolves the reference, checks liveness, ancestor liveness, and the canonical authorization predicate; returns `Revoked` / `AncestorRevoked` / `Unauthorized` faults.
- `attenuate/derive(parent: CapRef, constraint: Constraint, t) -> Result<CapRef, Fault>` — takes a `Constraint` (not an `Authority`); inserts a new arena node with lineage parent link.
- `valid/validate(cap, t)` — lineage validation used by attenuation.
The evaluator sees only `Value::Capability(CapRef)`; "Evaluator knows references; Kernel knows authority." *(L6672–6728; L19153–19175; L37870–37886.)*

**R-KERN-03 (substrate privacy).** `AuthorityNode` and all authority internals MUST remain `pub(crate)`/inaccessible to evaluator and runtime consumers. No hidden authority inspection. *(L39397–39407; L37722–37748.)*

---

# Part III — Resources

## S-11 Budget model

**R-BUDGET-01 (structure).** Budget `B = ⟨C, R, W⟩` where `C = ⟨F, I, D⟩` (consumables: fuel, I/O, duration), `R = ⟨M, S⟩` (reserved: memory bytes, concurrency slots), `W ∈ ℕ ∪ {∞}` (absolute logical-time deadline; `Deadline(None)` = infinity). Consumables are strictly decreasing and never returned; reserved capacities are held for a scope then released; the deadline is checked against logical time, not wall-clock. *(L8683–8700 (v0.3 frozen); L9161–9175 (Rust shapes); L41537–41560.)*

**R-BUDGET-02 (checked arithmetic).** Budget operations MUST use checked arithmetic and expose failure (`BudgetError { ConsumableExhausted, ReservedCapacityExceeded, ReservedCapacityUnderflow, DeadlineExceeded }`). `saturating_sub` MUST NOT be used for semantic accounting. *(L9207–9245; L38044–38046; L41557.)*

**R-BUDGET-03 (reservation predicates).** `ReserveOK(r, R, R_max) ⇔ R + r ≤ R_max`; `ReleaseOK(r, R) ⇔ r ≤ R`; updates `R' = R + r` / `R' = R − r`. (Supersedes the earlier single `BudgetOK` that mixed directions — see `C-07`. ) *(L7487–7520; L8692–8696.)*

**R-BUDGET-04 (dual-gate within-budget).** `WithinBudget(E, C, R, R_A) ⇔ cost_C(E) ≤ C ∧ ReserveOK(cost_R(E), R, R_max) ∧ cost(E) ≤ R_A` (effect cost within both runtime budget and capability ceiling). *(L8692–8696; L7426–7440.)*

**R-BUDGET-05 (conservation).**
- Consumables: `C_n + Σ cost_cons(c_i) = C_0` (strictly depleted; never returned).
- Reserved: `R_n + Σ release_i = R_0 + Σ reserve_i`.
- Deadline: `∀ active steps i: t_i ≤ W`.
- Global partition: `C_available + C_escrowed + C_consumed = C_initial`, where spawn moves parent `available` → child `available` (ownership transfer, not consumption); effect issuance moves `issue` cost → `consumed` and `complete_max` → `escrowed`; completion moves actual cost → `consumed` with refund of the remainder → `available`. *(L7408–7425; L28203–28240 (frozen partition); L35210–35215.)*

**R-BUDGET-06 (time advancement).** Every transition has a logical-time delta `δ_t(c) ∈ ℕ`: pure computation `δ_t = 0`; host interactions and scheduler steps `δ_t > 0`. A transition is valid only if `t + δ_t(c) ≤ W`. *(L8698–8700; L10164–10168. The per-transition delta values beyond this rule are an open item — see `U-07`.)*

**R-BUDGET-07 (cost model).** A `CostModel` maps operations to `Cost { consumable: Consumable, reserved: Reserved }`; the mapping is a configurable semantic contract, not hardcoded per-dimension anonymous tuples. `Consumable ≠ Reserved` at the type level. *(L9155–9205; L10171–10177.)*

**R-BUDGET-08 (budget fault).** If `¬BudgetOK` (any gate fails), the transition is replaced by `fault(BudgetExhausted)`; no partial debit occurs. *(L7345–7352; L7410–7419.)*

---

# Part IV — Effects

## S-12 Effect model and request sequence

**R-EFFECT-01 (request semantics).** `Expr::Request` means: construct Effect → authorize → account → log → Pending → yield `EffectRequest`. It does **not** mean execute the effect in the AST or evaluator. *(L12177–12194.)*

**R-EFFECT-02 (gated transition shape).** Every active transition takes the canonical gated form: `Pre(c, Σ) ∧ BudgetOK(c, Σ) ∧ AuthOK(c, Σ) ⊢ Σ →_c Σ'`. `AuthOK` applies only to authority-requiring transitions. *(L7145–7155; L8700–8710.)*

**R-EFFECT-03 (frozen 16-step request sequence, canonical).** The evaluator MUST follow this sequence; any deviation is a bug. No host interaction occurs before the durable issuance boundary:

```
 1. evaluate capability
 2. evaluate target
 3. evaluate arguments (strictly left-to-right)
 4. construct canonical Effect (+ EffectDigest)
 5. validate capability (lineage liveness)
 6. authorize exact effect (kernel.authorize with LogicalTime)
 7. capability resource ceiling check
 8. runtime consumable budget check (can_consume(issue + complete_max))
 9. runtime reservation capacity check (can_reserve)
10. deadline check (logical_time ≤ deadline)
11. host policy check (fail-early; the host re-checks authoritatively)
12. allocate deterministic EffectId (global monotonic counter)
13. commit issue budget / reservation (transactional; cannot fail after gate 8)
14. durable issuance (Prepared + Issued WAL records, each fsynced)
15. enter Pending (actor status)
16. host invocation (yield EffectRequest to host adapter)
```

*(L37891–37908 (master-prompt 16-step, latest frozen form); L23857–23948 (14-gate machine-internal form, gates 1–14, superseded numbering — see `C-01`); L11053–11090 (14-step `step_request` form, superseded numbering).)*

**R-EFFECT-04 (short-circuit).** A denial at any gate MUST short-circuit: subsequent gates are not called, `next_effect_id` is not incremented, the actor budget is unchanged, the event log gains no new entries, and `HostExecutor::execute` is never invoked. *(L24003–24045 (Track C); L37891–37908.)*

**R-EFFECT-05 (guaranteed completion accounting).** At issuance the machine MUST guarantee the maximum possible completion cost is affordable: gate 8 checks `can_consume(issue.checked_add(complete_max))` (overflow ⇒ `Fault::ArithmeticOverflow`/budget fault). The remaining budget is then mathematically guaranteed ≥ `complete_max`. *(L25799–25825.)*

**R-EFFECT-06 (causal receipt validation).** A receipt MUST be validated against **both** `EffectId` and `EffectDigest` of the pending effect before resumption: mismatch ⇒ `fault(ReplayCorruption)`, continuation is NOT resumed, reservation is NOT released. `EffectReceipt { id, effect_digest, result: Result<Value, HostFault> }`. *(L23949–24002; L25952–25970; L37910–37922.)*

**R-EFFECT-07 (completion accounting).** On valid receipt: charge `complete` (≤ `complete_max`) from consumables, release the reservation, append `EffectCompleted { id, digest, result }` to the event log, resume the continuation with the receipt's value (host faults map to the fault/value mapping defined by the machine). *(L23949–24002; L25799–25825.)*

## S-13 Transactional issuance and durability boundary

**R-DUR-01.** `HostInvoked(E) ⇒ DurableIssued(E)`. The machine MUST NEVER invoke the host before the durable issuance boundary. *(L35150–35156; L37910.)*

**R-DUR-02 (issuance transaction, strict order).**
1. Pure validation / authorization / budget checks;
2. `persistence.append(EffectPrepared { id, actor, digest })`;
3. `persistence.sync()` (fsync);
4. `persistence.append(EffectIssued { id, actor, digest })`;
5. `persistence.sync()` (fsync);
6. machine transitions actor to `Pending`;
7. host adapter receives `EffectRequest`.
*(L35150–35158.)*

**R-DUR-03 (causal effect protocol).** `Issued(E) ⇒ Prepared(E)`; `Completed(E) ⇒ Issued(E)`; `Reconciled(E) ⇒ Issued(E)`. Every subsequent record for an effect MUST carry the identical `EffectId` and `EffectDigest`; a digest mismatch is `EffectJournalCorruption`, not a different effect. *(L35111–35144; L37953–37965.)*

**R-DUR-04 (crash classification of effects).** `Prepared ∧ ¬Issued ⇒ Discard` (incomplete preparation is rolled back; budget restored). `Issued ∧ ¬Completed ⇒ Indeterminate` — NEVER automatically `NotExecuted`; the host may have executed the effect. *(L35159–35176; L37968–37981.)*

**R-DUR-05 (escrow survives crash).** An `Issued` effect with no durable completion retains its `completion_maximum` in the `escrowed` partition until reconciliation determines the outcome. Escrow does not vanish on crash. *(L35210–35215.)*

## S-14 Host boundary and replay

**R-HOST-01 (host gate, defense in depth).** The live host independently validates concrete OS-level authority/policy for each effect (`HostPolicyOK`); `¬HostPolicyOK(E) ⇒ ¬ExternalEffect(E)`. The machine's gate-11 check is fail-early; the host check is authoritative. *(L8560–8580; L10168–10172.)*

**R-HOST-02 (host adapter scope).** The host performs **only issued effects**. It is partially trusted. *(L41823–41841; L27644.)*

**R-HOST-03 (replay host).** `ReplayHost` reconstructs recorded effects; it NEVER touches the external world. It is **ordered**: for every request it consumes the next trace entry and validates both `EffectId` and `EffectDigest` sequentially; a mismatch or exhausted trace ⇒ `ReplayCorruption`/`ReplayTraceExhausted`. An unordered map MUST NOT be used as the normative replay mechanism. *(L25972–25996 (Phase 12 digest-validation correction); L33757+ §15B.9; L37985–38000.)*

**R-HOST-04 (replay correspondence theorem).** If `LiveRun(Σ₀)` produces trace `T` of (EffectIssued, EffectCompleted) pairs, `ReplayRun(Σ₀, T)` produces the same final configuration, provided replay verifies for each step `E_replay,k = E_recorded,k` and `R_replay,k.id = R_recorded,k.id` (and, in the frozen form, matching digests). Machine-state replay is always valid; real-world replay is only valid for reversible/idempotent effects — the replay host refuses to re-execute irreversible effects and returns the recorded result. *(L3947–3958 (v2 Theorem 4); L26249–26262 (effect classes, A7 refinement).)*

**R-HOST-05 (replay validates trace, not just final state).** Replay MUST validate the trace, not merely load the final state. *(L38278–38300.)*

---

# Part V — Concurrency

## S-15 Actors and deterministic scheduling

**R-ACTOR-01 (isolation).** Actors have isolated environments, continuations, heaps, mailboxes, budgets, and capability contexts. For `a ≠ b`: `Heap(a) ∩ Heap(b) = ∅ ∧ Env(a) ∩ Env(b) = ∅`. No actor mutates another actor's heap, environment, or continuation. Actors are instantiated with fresh arenas and `Environment::empty()` (no implicit environment inheritance). *(L41623–41641; L24268–24290; L25884–25900 (Theorem 4).)*

**R-ACTOR-02 (global state).** `GlobalState { actors: BTreeMap<ActorId, ActorState>, logical_time: LogicalTime, runnable: RunnableQueue, event_log: EventLog, next_effect_id: EffectId, next_actor_id: ActorId, scheduler: SchedulerState }`. Logical time is global; an actor observes `global.logical_time` at the instant its transition executes. *(L24148–24163; L25514–25546.)*

**R-ACTOR-03 (deterministic IDs).** `ActorId` and `EffectId` are allocated by global monotonic counters (`N' = N + 1`, ID = N before increment). Actor identity MUST NEVER be derived from memory addresses, OS PIDs, random UUIDs, thread IDs, or wall-clock timestamps. *(L24226–24245.)*

**R-ACTOR-04 (FIFO scheduler).** The scheduler is strictly FIFO; one actor appears in the runnable queue at most once (membership-enforced); exactly one actor performs exactly one CEK transition per scheduler turn; wakeups (receipts, messages) enqueue at the back. `Pending`, `Blocked`, `Halted`, and `Faulted` actors are never scheduled. `ActorSelected` is logged. An empty runnable queue yields a `Deadlock` outcome. *(L25558–25615 (frozen with at-most-once invariant); L24165–24224; L37924–37937.)*

**R-ACTOR-05 (spawn).** Spawn is a deterministic, transactional machine operation: (1) validate and escrow budget (`BudgetAllocationSpec` → `validate_and_escrow` — spawn is budget transfer, not budget creation); (2) allocate child `ActorId`; (3) derive child capabilities — the child receives **explicitly derived (attenuated) capabilities only**, via `kernel.derive(parent_cap, constraint, t)`; wholesale capability copying/cloning is forbidden; (4) construct isolated child state; (5) enqueue deterministically; (6) log `ActorSpawned`. *(L25573–25615; L25616–25673; L37941–37951.)*

**R-ACTOR-06 (send/receive).** `Send` is asynchronous: marshal the value, enqueue into the target's mailbox, log `MessageSent`; deterministically wake a `Blocked` target exactly once. `Receive` dequeues (unmarshals) or, on an empty mailbox, blocks **without consuming fuel** (`Blocked` is a suspension state, not an active transition; the actor yields to the scheduler). Mailboxes are FIFO. *(L25702–25749; L25674–25701; L37941–37951.)*

**R-ACTOR-07 (deterministic concurrency theorem).** `InitialState + SchedulerTrace + HostTrace ⇒ UniqueMachineTrace` — the scheduler is strictly FIFO, IDs are monotonic, the CEK machine is deterministic; hence global state transitions are uniquely determined given the same initial state and same external observations. *(L25759–25766 (Theorem 1).)*

**R-ACTOR-08 (no amplification / no teleportation theorems).** `Authority_after ≼ Authority_before ∪ ExplicitlyDelegatedAuthority` (ordinary `Send` passes through `marshal()`, which rejects raw capabilities). `Σ_actors C_consumable + Σ_escrow C_escrow + Σ_issued C_issue = C_global_initial` (budget is created only at root initialization; spawn escrows; send carries no budget). *(L26048–26070 (Theorems 2–3).)*

## S-16 Marshalling and delegation

**R-MARSHAL-01 (capability rejection, recursive).** Ordinary data marshalling MUST reject capabilities recursively — including capabilities nested inside lists, tuples, functions, or any nested structure. Raw `CapRef` transfer through ordinary messages is forbidden: `marshal_value(v) ⇒ Err(MarshalFault::CapabilityRequiresDelegation)` if `contains_capability(v)`. *(L41647–41658; L25674–25701; L37946–37951.)*

**R-MARSHAL-02 (explicit delegation).** Authority crosses actor boundaries only through explicit delegation — a separate, explicit AST node named `Expr::Delegate` in the Phase 13 text (L25700, L25931; master prompt L37959). It invokes the capability kernel and wraps the result in a `DelegatedCapability` envelope that the marshaller accepts: `DelegatedAuthority ≼ ParentAuthority`. **Gap:** the frozen `Expr` (L12145–12200, 12 constructors) contains no `Delegate` constructor and no frozen document defines its fields; the node’s existence is required by the frozen Phase 13 semantics but its shape is undecided (U-02). On receive, the recipient's kernel registers the new capability in its local context. *(L25972–26001; L37953–37959.)*

**R-MARSHAL-03 (canonical transport).** `MarshalledValue` is the canonical serialized byte representation (`canonical_serialize(v)`); `unmarshal(marshal(v)) = v` for all pure values. *(L25674–25701; L26072–26079 (Track B).)*

**R-MARSHAL-04 (semantic marshalling rule).** `marshal(v)` traverses `v`; by default `CapRef ∉ marshal(v)`; authority transfer requires the explicit `delegate(c, C, target_actor)` operation. *(L8695–8698.)*

---

# Part VI — Persistence

## S-17 Canonical serialization (frozen wire format, Phase 15A)

**R-CANON-01 (purpose & independence).** Semantic serialization is explicit and independent of Rust memory layout and of any Rust serializer. `bincode` may *implement* the format but MUST NOT *define* it. Canonical encoding defines semantic identity; it is not based on struct layout, pointer addresses, allocator behavior, or platform-specific representation. *(L28185–28228; L28453–28465; L41659–41690.)*

**R-CANON-02 (universal envelope, frozen).**
```
Envelope := version: u8            (currently 0x01)
          + type_tag: u8           (stable explicit constant per type)
          + payload_length: u32 BE (checked)
          + payload: bytes[payload_length]
```
*(L30532–30543; L33290–33347 (final frozen).)*

**R-CANON-03 (type tags, frozen).** Standalone envelope tags: `Value` = `0x00`; `Symbol` = `0x20`; `CapRef` = `0x30`; `ActorId` = `0x40`; `EffectId` = `0x41`. **Non-normative note:** the "revised grammar" §1.3 text listing Boolean `0x10` / Integer `0x11` / String `0x13` as standalone tags is stale and contradicted by the golden vectors and the final frozen implementation (see `C-02`); bool/integer/string exist only as `Value` discriminants. *(L30532–30598 (stale §1.3); L33087–33154 (final).)*

**R-CANON-04 (Value encoding, frozen).** `Value := Envelope(type_tag = 0x00, payload = variant_discriminant: u8 + variant_payload)` with discriminants: `Unit = 0x00`, `Bool = 0x01` (1 byte, `0x00`/`0x01` only), `Integer = 0x02` (8 bytes, i64 BE two's complement), `String = 0x03` (`[length u32 BE][UTF-8]`), `Symbol = 0x04`, `Capability = 0x05`, `List = 0x06`, `Map = 0x07`. **Nested values are encoded as complete canonical envelopes** (not stripped payloads). *(L30544–30552 (correction); L33155–33265 (final).)*

**R-CANON-05 (primitives, frozen).** `Symbol(u32)` payload = 4 bytes BE; `CapRef` payload = `[index u32 BE][generation u32 BE]`; `ActorId`/`EffectId` payloads = 8 bytes u64 BE. *(L33087–33154.)*

**R-CANON-06 (collections, frozen).** `List = [count u32 BE][element₁]…[elementₙ]`, each element a complete envelope. `Map = [count u32 BE][key₁][val₁]…`, entries ordered by the **semantic `Ord` relation on keys** (for `BTreeMap<u32, Value>`: numeric u32 order). Map decoding MUST reject duplicate keys (`CanonicalError::DuplicateMapKey`) to preserve injectivity. *(L30566–30573; L34987–35024 (final 15A patch); L38164–38172.)*

**R-CANON-07 (decoder contract, frozen).** `CanonicalDecode` is a strict parser enforcing, in order: (1) version = `0x01`; (2) type tag matches expected; (3) exact length (payload is exactly `payload_length` bytes); (4) internal payload well-formedness; (5) EOF/trailing-byte rejection. All discriminants are explicit stable constants (source-order changes MUST NOT change the wire format). Malformed encodings are rejected with explicit `CanonicalError` values (`InvalidVersion, InvalidTypeTag, LengthMismatch, LengthOverflow, InvalidUtf8, UnexpectedEof, TrailingBytes, InvalidDiscriminant, InvalidBoolValue, DuplicateMapKey`). *(L30575–30586; L32948–33049.)*

**R-CANON-08 (checked arithmetic).** All length/pointer arithmetic is checked. A collection exceeding `u32::MAX` yields `LengthOverflow`. Encoded collection counts MUST NOT authorize attacker-controlled preallocation (collections grow organically from `Vec::new()`, no `with_capacity` on untrusted input). Nested decoding uses bounded cursors (`read_envelope_payload` returns only the payload slice; payload decoding uses a fresh bounded cursor). Envelope construction is fallible (no panics). *(L30574–30578; L32948–33265; L33266–33286.)*

**R-CANON-09 (digests).** `StateDigest = SHA-256(canonical_bytes)`; `EffectDigest = SHA-256(canonical_bytes(effect))`. Mechanically: `Canonical(x) = Canonical(y) ⇒ Digest(x) = Digest(y)`. The reverse direction holds only as an operational integrity assumption under cryptographic collision resistance. When both states are available, compare canonical bytes directly; use digests for persistence integrity, causal identity, and compact checkpoints. *(L28185–28228 (correction); L30588–30590; L28453–28465.)*

**R-CANON-10 (injectivity, scoped claim).** Injectivity (`Canonical(x) = Canonical(y) ⇒ x = y`) is a **structural specification property** of the encoding design; the conformance suite provides machine-checked evidence via round-trip and differential testing over the generated distribution. It is NOT claimed as a mathematical proof of arbitrary Rust programs. *(L30592–30598 (corrected wording); L35068.)*

**R-CANON-11 (golden vectors, normative fixtures).** The frozen golden vectors (e.g., `Value::Integer(42)` ⇒ `01 00 00 00 00 09 02 00 00 00 00 00 00 00 2A`; `CapRef{5,2}` ⇒ `01 30 00 00 00 08 00 00 00 05 00 00 00 02`) are normative **test fixtures** for the format, not additional behavioral rules. *(L30599–30646; L31948–32010 (regenerated); L33266–33286 (freeze).)*

## S-18 Persistence protocol (Phase 15B)

**R-PERSIST-01 (separation).** The persistence layer is not a semantic machine; it records and reconstructs the existing machine. **No secondary serialization:** the payload of every persistence record is strictly the byte output of Phase 15A `CanonicalEncode`. *(L33757–33790; L35078–35087.)*

**R-PERSIST-02 (two-level framing).** Level 1 (semantic, 15A): `version | type_tag | payload_length | payload` — answers "what object is this?". Level 2 (persistence): `WalFrame { sequence: WalSequence (u64, strictly monotonic), kind: WalRecordKind (u8), payload_length: u32 BE (checked), payload (15A bytes), checksum: SHA-256(sequence ‖ kind  payload_length ‖ payload) }` — answers "where is the record and is it intact?". The parser MUST reject: truncated headers, truncated payloads, impossible lengths, checksum mismatches, invalid record kinds, sequence regressions, sequence gaps, malformed canonical payloads, trailing bytes. *(L33802–33830; L35088–35110.)*

**R-PERSIST-03 (record taxonomy).** `WalRecord ::= Event(EventEnvelope) | EffectPrepared { id, actor, digest } | EffectIssued { id, actor, digest } | EffectCompleted { id, digest, result_digest } | EffectReconciled { id, digest, outcome } | SnapshotCommit { event_sequence, snapshot_version, state_digest }`. `EventEnvelope { sequence: EventSequence, logical_time: LogicalTime, event: GlobalEvent }` with `e_i.sequence < e_{i+1}.sequence` (total ordering). *(L33861–33900; L35111–35144.)*

**R-PERSIST-04 (snapshot content).** A snapshot contains all machine state necessary to continue execution (logical_time, ID counters, runnable queue, actors with run state / EvalState / capabilities / heap / budget / mailbox / status, scheduler state) plus `version, last_event_sequence, last_effect_sequence, state_digest`. It MUST NOT serialize host implementation state (HostExecutor, OS handles, file descriptors, threads, sockets, raw pointers, process handles, unvalidated host objects); those are reconstructed by the host adapter. *(L26293–26330.)*

**R-PERSIST-05 (atomic snapshot protocol).** Snapshot creation is transactional: (1) write `SnapshotBegin` marker; (2) write canonical `GlobalSnapshot` payload (15A-encoded); (3) fsync payload; (4) write `SnapshotCommit` record (with `state_digest`); (5) fsync commit record. `ValidSnapshot(S) ⇔ Commit(S) ∧ Digest(Canonical(S)) = RecordedDigest(S)`. Recovery MUST ignore any snapshot lacking the durable `SnapshotCommit` marker; partial snapshots are garbage. *(L26216–26240; L35177–35188.)*

**R-PERSIST-06 (sequence continuity).** WAL sequence continuity MUST hold (`s_{n+1} = s_n + 1`); gaps are rejected (obligation tag `WAL-GAP-REJECT` / `WAL-SEQUENCE-CONTINUITY`). *(L35088–35110; L35189–35208.)*

## S-19 Crash recovery

**R-RECOV-01 (durable state).** Durable state `D = ⟨S, L, H⟩` (latest committed snapshot, durable event log after it, durable effect journal). `Recover(D) = Replay(S, L, H)`. *(L26122–26140.)*

**R-RECOV-02 (normative crash matrix T0–T6).**

| Crash point | Durable state | Required recovery result |
|---|---|---|
| T0: before `Prepared` | none | Effect does not exist; no budget mutation; resume normally |
| T1: after `Prepared` | `Prepared` only | Discard incomplete preparation; resume normally |
| T2: after `Issued` | `Prepared + Issued` | `Indeterminate`; requires reconciliation |
| T3: host invoked | `Prepared + Issued` | `Indeterminate` (host may have executed) |
| T4: host completed (not durable) | `Prepared + Issued` | `Indeterminate` (completion not durable) |
| T5: after `Completed` | `Completed` durable | Reconstruct completed effect; resume continuation |
| T6: after `SnapshotCommit` | snapshot + WAL | Recover snapshot base; replay subsequent WAL records |

*(L35159–35176 (frozen); L28467–28493 (same matrix, restated); L38831–38846.)*

**R-RECOV-03 (recovery algorithm).** Recovery: (1) locate newest committed snapshot; (2) verify framing/checksum; (3) decode via 15A `CanonicalDecode`; (4) validate recovered `GlobalState` invariants (budget conservation, no duplicate runnable actors); (5) open WAL, verify framing/checksums; (6) verify sequence continuity, reject gaps; (7) replay records sequentially after snapshot sequence; (8) reconstruct effect journal, validate causal chains; (9) classify interrupted effects (`Indeterminate` vs `Completed`); (10) reconstruct runnable queue; (11) compute final state digest vs trailing checkpoint; (12) enter `RecoveryComplete`, resume deterministic scheduler. *(L35189–35208; L26272–26300.)*

**R-RECOV-04 (independent recovery).** The recovery engine MUST be an **independent implementation** from the normal execution path (anti-oracle-collapse). Production recovery MUST NOT be used as the reference recovery oracle. *(L35189–35195; L38858–38890.)*

**R-RECOV-05 (strict validation rule).** `Invalid(D) ⇒ RecoveryFault`. The recovery engine MUST NEVER silently repair corruption (no dropping duplicate runnable actors, no fixing budget mismatches, no ignoring gaps/checksums/causality violations). *(L35196–35208; L38254–38272.)*

**R-RECOV-06 (budget recovery invariant).** The three-way accounting `C_available + C_escrowed + C_consumed = C_initial` MUST survive crashes identically. *(L35210–35215.)*

**R-RECOV-07 (reconciliation).** `Issued ∧ ¬Completed` effects are handed to the supervisor's reconciliation policy; `Reconciled(E) ⇒ Issued(E)`; outcomes are recorded durably (`EffectReconciled`). Reconciliation is the only path by which an `Indeterminate` effect becomes resolved; the system never auto-resolves to "not executed". *(L35111–35144; L26249–26262.)*

---

# Part VII — Verification

## S-20 Independent reference model and differential verification

**R-REF-01 (purpose).** An independently implemented executable reference model provides machine-checked evidence that the production implementation conforms to the specified semantics: `Observe(Production(X)) = Observe(Reference(X))` for every generated input `X` in the comparison domain; for persistence: `Canonical(Recover_P(D)) = Canonical(Recover_R(D))`, subject to the frozen reconciliation rules. This is differential verification **evidence**, not a formal proof. *(L35281–35310; L38935–38953.)*

**R-REF-02 (independence boundary).** The reference model MUST NOT call: `ProductionEvaluator, ProductionContinuation, ProductionCapabilityKernel, ProductionBudget, ProductionScheduler, ProductionSerializer, ProductionRecovery, ProductionPersistence, ProductionReplayHost, ProductionTransition`. It may consume test inputs/fixtures and emit reference observations/traces. Shared transition implementations are forbidden; shared semantic test fixtures are allowed. *(L35330–35375; L37696–37721; L28590+ (key rule).)*

**R-REF-03 (reference model scope).** The reference implementation independently models: CEK evaluation, lexical environments, closures, calls, capability derivation, revocation, budgets, actors, scheduling, effects, persistence, recovery. It is intentionally small, direct, explicit, deterministic, independently structured, and slow where clarity demands. Performance is explicitly secondary to transparency. *(L41848–41866; L35281–35310; L35313–35322; L35341.)*

**R-REF-04 (non-goals).** The reference model does not redefine semantics, introduce a second serialization format, reproduce host implementation details, prove correctness mathematically, share production transition code, or optimize. *(L35326–35339.)*

**R-REF-05 (normalized observation).** Differential comparison uses normalized observations, not internal structure: terminal states, event trace, effect trace, resource partitions, authority outcomes, scheduler trace, faults, recovered state. Internal details (addresses, pointers, allocator behavior, Rust enum layout, OS handles, host object identity) are excluded unless explicitly semantic. The comparator MUST report the **first divergence**. Comparing only final return values is forbidden. *(L38420–38470 (§16); L38935; L41869–41906.)*

**R-REF-06 (harness enforcement).** The harness MUST include mocked boundary enforcement: a `PanicHost` that panics if `execute()` is called before all gates pass; a `MockKernel` asserting exactly one `authorize`/`derive` call with the exact expected parameters. The production/reference boundary is a first-class test subject. *(L27891–27902.)*

## S-21 Test infrastructure, mutation, and CI

**R-TEST-01 (execution modes, frozen baselines).**
- **Exhaustive (small-state):** enumeration over bounded state; baseline `expression depth ≤ 4, actors ≤ 2, capabilities ≤ 2`; runs on every commit. The CI time target is a performance budget, **not** a semantic constraint; if the state space grows, partition/shard/cache — never reduce semantic coverage to preserve a time target.
- **Property-generated:** randomized layered generation (structure → type validity → capabilities → budgets → actor topology → effects → persistence corruption), aggressive shrinking; runs nightly.
- **Stress:** `50k–100k` call depth, `100+` actors, long mailboxes, large WAL traces, repeated crash/recovery, large continuation states; runs weekly and on release candidates.
*(L38587–38715; L37251–37268 (pre-correction `<2 min` wording superseded — `C-11`).)*

**R-TEST-02 (reproducible counterexamples).** Every generated test case MUST be reproducible. Every failure MUST save the structured artifact: `seed, generator_version, semantic_version, test_case_version, program, initial state, capabilities, budgets, actor topology, scheduler_trace, host_trace, persistence image, crash_trace, production_observation, reference_observation, first_divergence, minimized case`. The artifact MUST be runnable locally. *(L38891–38920; L37293–37315; L38587–38624.)*

**R-TEST-03 (shrinking protocol).** Shrinking order: (1) actor count, (2) expression depth, (3) call arity, (4) bindings, (5) mailbox messages, (6) capability scope, (7) budget dimensions, (8) WAL records, (9) effect count, (10) crash position. The shrinker MUST preserve the failure predicate; every failure yields a minimal reproducible artifact. *(L38441–38463.)*

**R-TEST-04 (mutation registry, baseline frozen).** The versioned baseline registry MUST include:
`M001` reverse argument evaluation; `M002` skip arity precheck; `M003` allow non-function application; `M004` accept revoked capability; `M005` omit capability ceiling; `M006` permit capability amplification; `M007` omit budget gate; `M008` release indeterminate escrow; `M009` permit negative resources; `M010` allocate EffectId before authorization; `M011` schedule blocked actor; `M012` duplicate runnable queue entry; `M013` break mailbox FIFO; `M014` accept duplicate canonical map key; `M015` ignore WAL sequence gap; `M016` ignore checksum mismatch; `M017` accept mismatched EffectDigest; `M018` resume after corrupted receipt.
The registry is **additive**: a previously killed mutant remains a regression requirement. *(L38473–38492; L37239–37249 (categorization).)*

**R-TEST-05 (kill rate).** Target `MutationKillRate = 100%` for all registered **non-equivalent** mutations. Any surviving non-equivalent mutant blocks verification. Equivalent mutants require explicit adjudication and documentation. Mutation survivors are release-blocking defects. *(L38494–38500; L37390–37400.)*

**R-TEST-06 (mutation validation).** The verification system itself MUST be tested: for each mutation — inject, build, run targeted test, run differential suite, assert mutant killed. Do not merely run the framework. *(L38515–38540.)*

**R-TEST-07 (semantic coverage, obligation-tagged).** Coverage is tracked per stable verification-obligation tag (e.g., `CEK-CALL-ARITY-PRECHECK, CEK-CALL-ARGS-LTR, CEK-CLOSURE-LEXICAL-CAPTURE, CAP-DERIVE-NO-AMPLIFICATION, CAP-REVOCATION-ANCESTOR, BUDGET-CONSUMPTION-CONSERVATION, BUDGET-ESCROW-CONSERVATION, EFFECT-ISSUE-DURABLE-BEFORE-HOST, EFFECT-RECEIPT-DIGEST-VALIDATION, SCHED-FIFO, SCHED-BLOCKED-NOT-SCHEDULED, MARSHAL-NO-RAW-CAPABILITY, WAL-SEQUENCE-CONTINUITY, RECOVERY-ISSUED-INDETERMINATE, SNAPSHOT-COMMIT-INTEGRITY`). Coverage metrics are evidence and are **never** a substitute for the differential oracle. *(L38523–38560; L37402–37414.)*

**R-TEST-08 (crash-injection matrix).** Exercise all T0–T6 crash points; verify the exact expected classification, especially `Issued ∧ ¬Completed ⇒ Indeterminate` and `Prepared ∧ ¬Issued ⇒ Discard`. *(L38831–38846; L35216–35236 (crash harness).)*

**R-TEST-09 (fault adjudication).** Every production/reference divergence MUST be classified: production defect | reference defect | harness defect | specification ambiguity. Never patch the oracle merely to make a test pass. Specification ambiguity requires an explicit specification decision before implementation proceeds. *(L38848–38862; L37404–37414.)*

**R-TEST-10 (CI gates, frozen).**
- **Pull request:** format, lint, unit tests, exhaustive small-state, core differential tests, serialization conformance.
- **Nightly:** property generation, mutation registry, full differential suite, persistence fuzzing, crash injection, semantic coverage report.
- **Release candidate:** all nightly suites, stress tests, full crash matrix, `MutationKillRate = 100%`, determinism checks, recovery differential tests, security regression suite.
No release is accepted with an unexplained differential mismatch or surviving non-equivalent mutation. *(L38864–38890; L37287–37292.)*

**R-TEST-11 (final acceptance condition).** The implementation is conformant only when `Observe_P(X) = Observe_R(X)` over the tested state space **and** `MutationKillRate = 100%` for all non-equivalent registered mutations **and** `Canonical(Recover_P(D)) = Canonical(Recover_R(D))` over the tested persistence state space (subject to authoritative external-effect reconciliation). "Code compiles", "unit tests pass", and "coverage is high" are not completion. *(L38885–38911; L41196–41210.)*

---

# Part VIII — Engineering and claims

## S-22 Repository structure and crate responsibilities

**R-REPO-01 (workspace layout, frozen boundaries).** The workspace separates untrusted language data → compiler → trusted executable representation → machine → authority/resources → durable effects → host, and independently maintains production ↔ observations ↔ reference. Top-level names may change for organizational reasons; **dependency and trust boundaries must not**. The layout (frozen intent): `crates/{ror-core, ror-compiler, ror-kernel, ror-runtime, ror-persistence, ror-host, ror-agent, ror-reference, ror-differential, ror-testkit}`, `tests/{conformance, exhaustive, property, mutation, crash, stress}`, `vectors/{canonical, persistence, effects}`, `mutations/registry.toml`, `docs/{architecture, semantics, verification, security}`, `scripts/`. *(L39140–39195; L41406–41424.)*

**R-REPO-02 (crate contracts, normative).**
- `ror-core`: lowest-level semantic domain (Symbol, ActorId, CapRef, EffectId, EventSequence, LogicalTime, Expr, Value, FunctionValue, Environment, Constraint, Effect, EffectCost, Budget, Consumable, Reserved, Fault, MachineEvent). Depends on std only. MUST NOT contain host calls, filesystem, networking, scheduler, persistence, capability authority storage, or LLM integration.
- `ror-compiler`: Block → parse → NormalizedAST → ValidatedPlan → PlanIR → capability analysis → resource analysis → ExecutablePlan. `ExecutablePlan` constructors private.
- `ror-kernel`: CapabilityKernel, AuthorityNode, derivation, revocation, authorization, budget primitives, logical-time validation. `AuthorityNode` invisible to evaluator/runtime.
- `ror-runtime`: CEK machine, actors, scheduler, effects.
- `ror-persistence`: WAL, snapshots, effect journal, recovery.
- `ror-host`: host execution and replay boundaries.
- `ror-agent`: planner/observation/supervisor integration.
- `ror-reference`: independent executable semantic model (no production dependencies).
- `ror-differential`: generator, runner, comparator, shrinking.
- `ror-testkit`: test infrastructure and controlled doubles.
*(L39196–40762 (responsibility detail); L41806–41846 (summary table).)*

*(Non-normative note, added by the terminology pass — the normative bullet above is unchanged.)*
*The `ror-compiler` pipeline in R-REPO-02 reproduces the turn-[58] diagram (L39265–39280) faithfully, and it is reproduced here unchanged. It is **one of three** stage sequences in the frozen source, and the frozen struct declarations contradict its ordering: `NormalizedAST` is the **content** of `ParsedBlock` (L864), not a stage before `ValidatedPlan`, and `PlanIR` is the **content** of `ValidatedPlan` (L865), not a stage after it. Two declared stages — `ParsedBlock` (L864) and `CapabilityCheckedPlan` (L866) — do not appear in it at all, and `NormalizedAST` and `PlanIR` are never declared anywhere (L1–42312). An implementer MUST NOT treat this rendering as the stage list. Filed as `term/02-collisions.md` X-02, X-41, X-29, X-30 and `spec/06` C-52; `mod/02-compiler.md` carries the same note. Nothing here is renamed or reordered, because the collision is in the frozen source and resolving it by editing either side would be a silent semantic change (R-SCOPE-03).*

**R-REPO-03 (boundary enforcement).** The repository MUST make the boundaries hard to violate accidentally, enforced by Cargo dependencies, Rust visibility, type construction, trait boundaries, module structure, tests, mutation testing, and differential testing. *(L41223–41273.)*

## S-23 Milestones and implementation order

**R-ORDER-01 (implementation order, frozen).** Implement in dependency order: 01 core domain types → 02 canonical serialization → 03 compiler artifacts → 04 capability kernel → 05 budget algebra → 06 CEK evaluator → 07 lambda/call → 08 attenuation → 09 effects → 10 actors → 11 scheduler → 12 marshalling/delegation → 13 persistence → 14 crash recovery → 15 LLM boundary → 16 reference model → 17 differential harness → 18 mutation framework → 19 CI → 20 stress/security validation. Every stage must have tests before the next dependent stage is considered complete. The reference model and differential infrastructure MUST be established as early as practical, not postponed. *(L37793–37812 (§3); L42108–42142.)*

**R-ORDER-02 (milestones, frozen acceptance).**

| Milestone | Acceptance |
|---|---|
| M0 Workspace | `cargo check/test/fmt/clippy` pass; no semantic functionality required |
| M1 Canonical serialization | golden vectors pass; round-trips pass; malformed inputs reject; duplicate keys reject; canonical bytes deterministic |
| M2 Pure CEK | differential equivalence for Value, Var, Let, Seq, If |
| M3 Lambda/Call | `CEK-CALL-ARITY-PRECHECK`, `CEK-CALL-ARGS-LTR`, `CEK-CLOSURE-LEXICAL-CAPTURE` + deep-call stress |
| M4 Capability/Attenuation | `CAP-DERIVE-NO-AMPLIFICATION`, revocation, expiration, lexical capability binding + independent reference algebra |
| M5 Effects | authorization, budget gates, deadline, host policy, EffectId, EffectDigest, durable issuance, receipt validation |
| M6 Actors | FIFO scheduler, FIFO mailbox, spawn isolation, send/receive, delegation, blocked/wakeup |
| M7 Persistence | WAL, snapshot, effect journal, checksum, sequence continuity, recovery |
| M8 Differential system | generated programs, reference execution, production execution, normalized comparison, first-divergence reporting, shrinking |
| M9 Mutation gate | `MutationKillRate = 100%` for all registered non-equivalent mutants |
| M10 Crash/recovery gate | T0–T6 all produce the frozen expected classification |
| M11 Release candidate | exhaustive, property, mutation, differential, crash, stress, determinism, serialization, security — all green |

A milestone is complete only when its corresponding verification obligations are satisfied. *(L40763–41100; L42165–42190.)*

**R-ORDER-03 (first security gate).** Before implementing external effects, demonstrate `Block ⇏ ExecutablePlan` and production/reference differential agreement for Value/Var/Let/Seq/If/Lambda/Call (including faults); the differential harness MUST be operational before the production CEK becomes large. *(L41155–41195.)*

**R-ORDER-04 (first sprint, frozen task set).** ROR-001 … ROR-016 (workspace, toolchain, core types, canonical cursor/envelope/primitives/Value, golden vectors, malformed-input suite, duplicate-map-key regression, reference crate, differential observation API, pure reference CEK, pure production CEK, first differential tests). No actors, external effects, persistence, or LLM integration in sprint 1. *(L41091–41112.)*

**R-ORDER-05 (definition of done).** A component is complete only when implementation + unit tests + reference semantics + differential tests + obligation mapping + mutation coverage + documentation (where applicable) are present. *(L41124–41142.)*

## S-24 Conformance claims and prohibited shortcuts

**R-CLAIM-01 (scoped conformance claim, frozen wording).** The appropriate engineering claim is: *"The independent reference model, exhaustive/property-based tests, mutation testing, and crash-injection suite provide machine-checked evidence that the implementation conforms to the frozen calculus over the tested state space."* The project MUST NOT claim that test execution constitutes a mathematical proof of the entire calculus. Do not claim more than the evidence establishes. Formal mechanization may provide stronger guarantees later but is not required to begin implementation. *(L38913–38917; L42191–42265; L28247–28268.)*

**R-CLAIM-02 (prohibited shortcuts, frozen).** Never: use recursive evaluation; trust AST shape as a security boundary; expose authority internals; clone capabilities wholesale during spawn; transfer raw capability references through ordinary messages; use wall-clock time for deterministic semantics; use saturating budget arithmetic; invoke host before durable issuance; infer external-effect nonexecution from missing completion; silently repair persistence corruption; use production recovery/serialization as the reference oracle; compare only final return values; accept surviving mutations without adjudication; reduce semantic coverage to satisfy CI timing; weaken tests because implementation is inconvenient. *(L38858–38890; L42144–42188.)*

**R-CLAIM-03 (engineering response format).** Implementation reports MUST include: component implemented, frozen invariants exercised, production/reference boundary, tests added, differential tests added, mutation tests affected, coverage obligations satisfied, known limitations, remaining work. Conflicts MUST be reported in the `CONFLICT / FROZEN REQUIREMENT / AFFECTED COMPONENT / RECOMMENDED ACTION` format, never silently resolved. *(L38808–38846.)*

**R-CLAIM-04 (start condition).** Do not propose another semantic phase. Begin implementation from the lowest dependency layer, with the independent reference model alongside production, keeping the differential harness operational as early as possible. *(L38921–38928.)*

---

# End of canonical specification

Cross-references: obligation matrix `03-obligation-matrix.md`; dependency graph `04-dependency-graph.md`; terminology `05-terminology.md`; contradictions/ambiguities `06-contradictions-ambiguities.md`; implementation mapping `07-implementation-mapping.md`; verification/evidence mapping `08-verification-mapping.md`; unresolved decisions `09-unresolved-decisions.md`; machine index `10-index.json`.
