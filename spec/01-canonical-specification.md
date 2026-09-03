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

**R-CORE-11 (I2 predicate signatures, canonical form — frozen addendum).** The central theorem's predicates each have ONE canonical signature; all other frozen signatures are SUPERSEDED (quoted, not deleted). First conjunct: `ValidatedRequest(E)` — request-time validation inside the 16 gates — with the subsumption `ValidatedRequest(E) ⇒ ValidatedPlan(plan(E))`; the `ValidatedPlan` compiler-struct homonym (X-01) is disambiguated by qualification — `ValidatedPlan_pred` vs `ValidatedPlan_struct` — adopted repository-wide. Authorization: `Authorized(holder, c, E, t) ⇔ c ∈ κ_holder ∧ Valid(c, t) ∧ Authorized(κ_holder(c), E, t)` — holder first, possession a conjunct (formalizing R-KERN-04); the authority-first reading `Authorized(A, E, t)` is SUPERSEDED (quoted, not deleted). The 7-conjunct chain (R-CORE-02) is stated once, over these exact signatures; differential adjudication (R-TEST-09) MUST adjudicate against this form — weaker plan-time-only or authority-first readings MUST NOT satisfy the chain. *(Frozen addendum — post-audit remediation SEC-016; additive per R-SCOPE-03; extends R-CORE-02/R-KERN-04; resolves C-80 and, at the normative layer, term/ X-01/X-04/X-05; no source transcription.)*

**R-CORE-12 (fault totality and transition atomicity — frozen addendum).** Machine code (evaluator, kernel, budget, persistence, runtime transitions) MUST be panic-free on non-test paths: every fallible operation returns `Result`, and every failure maps to a declared `Fault` — `unwrap`/`expect`/`unreachable!`/`panic!` are FORBIDDEN outside test doubles (the `#![forbid(unsafe_code)]` policy extended with the panic clause). Check/commit drift MUST fault, not panic: a declared internal-consistency fault (`Fault::InternalInvariant` family) MUST exist, observable and differentially comparable. Transition atomicity: a transition either completes (all durable effects appended) or faults with R-EFFECT-04's five assertions — there is no third died-mid-transition outcome inside the trusted boundary. Durable appends MUST precede irreversible in-memory mutations where feasible, or the commit MUST be journal-driven — the mid-transition window is removed, not merely its panic failure mode. Machine crates MUST compile under `clippy::unwrap_used`/`clippy::expect_used` denial (R-REPO-03 structural enforcement). *(Frozen addendum — post-audit remediation SEC-020; additive per R-SCOPE-03; extends R-EFFECT-04/R-BUDGET-02/R-REPO-03; resolves C-83; mutation M034; no source transcription.)*

**R-CORE-13 (closed declared fault surface — frozen addendum).** The fault surface on every trust-boundary crossing (host→machine, storage→recovery, planner→machine) MUST be closed and declared: the full fault/error enumeration is frozen, including the six undeclared replay-path variants (`ReplayTraceExhausted`, the `ReplayCorruption` family), `StalePlan`, the unified `MarshalFault` (R-MARSHAL-05), and the `InternalInvariant` family (R-CORE-12); the two-variant `HostFault` declaration is SUPERSEDED (quoted, not deleted). Host faults map onto a closed machine-fault set; `format!("{:?}")` debug text of external errors MUST NOT enter machine values — opaque error codes or digests only (extends R-EFFECT-08 item 4). Resume-vs-fault behavior is pinned per variant: which faults resume continuations, which park actors, the budget effect, and the event-log delta — security-critical semantics, not cosmetics; differential fault comparison (R-REF-05) compares these four, not just labels. *(Frozen addendum — post-audit remediation SEC-012; additive per R-SCOPE-03; extends R-SCOPE-03/R-REF-05/R-EFFECT-08; resolves C-91, closing U-08/U-14 in the security direction; no source transcription.)*

**R-CORE-14 (canonical request protocol and transaction boundary — frozen addendum).** The request sequence is exactly the 16-step master-prompt form: (1) evaluate capability; (2) evaluate target; (3) evaluate arguments left-to-right; (4) construct the canonical `Effect` and `EffectDigest`; (5) validate the CapRef; (6) authorize the exact effect; (7) capability ceiling; (8) runtime budget; (9) runtime reservation; (10) deadline; (11) host policy; (12) allocate the `EffectId`; (13) commit issue budget/reservation; (14) durable issuance; (15) actor `Pending`; (16) host invocation. The turn-[21] 16-step form — in which the host emission precedes the durable `Issued` record — is SUPERSEDED (quoted, not deleted): `HostInvoked(E) ⇒ DurableIssued(E)` holds with no ordering exception, and the S-12 presentment of that earlier order is read only as the superseded historical text (C-103). The step-10 deadline premise MUST be the post-advance form `t + δ_t(req) ≤ W`; the pre-advance `t ≤ W` reading is SUPERSEDED (C-104). Steps 12–14b form ONE atomic section: between allocation of the `EffectId` and the second fsync of the `Issued` record no `SnapshotCommit`, no scheduler yield and no observable event MAY occur. Live-failure semantics of that section are R-DUR-07; the recovery boundary (snapshot cadence, `next_effect_id` reconstruction, completion order) is R-RECOV-09. *(Frozen addendum VII — request-pipeline remediation, owner decision 2026-09-03; additive per R-SCOPE-03; extends R-EFFECT-01/03, R-BUDGET-06, R-DUR-02, R-CORE-06/12; resolves C-103/C-104, decisions U-39/U-40; no source transcription.)*

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

**R-TRUST-04 (one complete trust table; the planner is never a provider — frozen addendum).** The trust table exists exactly once and MUST be complete over every module that enforces a security boundary: rows for MOD-06 (marshalling and delegation boundary), MOD-08 (the effect gate sequence), and MOD-10 (the canonical codec) are frozen here as authoritative machine boundary (trust: Yes); the 11-row earlier table is SUPERSEDED (quoted, not deleted). The planner module (MOD-13 / `ror-agent`) MUST NOT appear as the provider of any `SECURITY_DEPENDENCY` or `RUNTIME_DEPENDENCY` edge: its records are prohibitions — negative contracts homed at their enforcing modules (MOD-03/06/08); security obligations MUST NOT be discharged inside any LLM-facing crate. Verification: `dep/` regenerated with SC-1/2/3 promoted from advisory rows to hard failures. *(Frozen addendum — post-audit remediation SEC-022 (V-03/V-11); additive per R-SCOPE-03; extends R-TRUST-01/R-SCOPE-04; resolves C-84; no source transcription.)*

**R-TRUST-05 (structural carriability of the durability hinge — frozen addendum).** The frozen crate DAG MUST carry the R-DUR-02 hinge edge `ror-runtime → ror-persistence` (the step-14 durable append that `HostInvoked ⇒ DurableIssued` hangs on) — decided here in the direct direction; the inverted-trait alternative is SUPERSEDED (quoted, not deleted). The `ror-core → ror-kernel` implication is resolved per the frozen edge list's intent (forbidden; V-10b): authority storage stays kernel-side. The forbidden-edge list MUST be checked mechanically against the actual `Cargo.toml` DAG, and the crate-separation rule — no LLM-facing code in a crate holding runtime/compiler/persistence handles — is part of R-REPO-03's structural review. A build in which the durability call is structurally orphaned (a local journal shim) is a conformance failure. *(Frozen addendum — post-audit remediation SEC-022 (V-10) + the SEC-015 crate rule; additive per R-SCOPE-03; extends R-REPO-02/R-REPO-03/R-DUR-02; resolves C-85; no source transcription.)*

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

**R-ARCH-05 (isolation posture — frozen addendum).** The isolation ladder (U-05) is RETIRED by decision: the frozen minimum posture is in-process structural isolation (type safety, `#![forbid(unsafe_code)]`, the crate DAG, panic-free machine paths per R-CORE-12), and the residual risk — host compromise is machine compromise: same address space, memory adjacency to `GlobalState`, the kernel arena, and the revocation set — MUST be recorded in the trust model as accepted, not implied away by behavioral containment claims. For any deployment where host code is not fully trusted, the out-of-process host adapter is the REQUIRED mode: effects and receipts cross as canonical bytes only (the wire format already frozen, R-CANON-13). In-process `Box<dyn HostExecutor>` is testkit-only in production configurations (`PanicHost`/`MockKernel` doubles); production `ror-host` MUST NOT link `ror-runtime` internals beyond the adapter trait — a hard dependency/visibility gate. An untrusted agent's isolation level may never be weaker than its spawner's own. *(Frozen addendum — post-audit remediation SEC-013; additive per R-SCOPE-03; extends R-ARCH-03/R-TRUST-01/R-CORE-12; resolves C-93, retiring U-05; no source transcription.)*

*(Frozen addendum VI — owner decision 2026-09-03, resolving `dep/05` V-01; additive per R-SCOPE-03; refines R-ARCH-03/R-REPO-02; no source transcription.)*

**ExecutablePlan crate home and seal (normative refinement).** The `ExecutablePlan` type and its `Sealed` marker MUST be defined in `ror-core`. Construction MUST remain compiler-only (R-ARCH-03 unchanged): `finalize` requires a `PlanSeal` token whose sole constructor is `pub` in `ror-core` and denied by the workspace clippy `disallowed-methods` configuration in every crate except `ror-compiler` (R-REPO-03 structural enforcement — the same mechanism class as R-CORE-12's `unwrap`/`expect` denial; Track-B). The source's `pub(crate) fn finalize` phrasing (L39947-39950 §16) is per-crate visibility and cannot express this cross-crate privacy; that reading is SUPERSEDED (quoted, not deleted — `dep/05` V-01). No new crate edge results: `ror-runtime` already depends on `ror-core` (`spec/07` §6), which is why the type home moves rather than the edge.

## S-05 LLM / planner boundary

**R-PLANNER-01 (proposal data).** The planner MUST return proposals as `PlanProposal { observation_sequence: EventSequence, block: Block, planner_metadata }`. LLM output MUST be treated as data (`LLMOutput ∈ Data`) and MUST NOT confer authority. *(L27176–27198.)*

**R-PLANNER-02 (cannot).** The model MUST NOT: allocate capabilities; authorize effects; modify budgets; modify the event log; allocate actors directly; invoke the host; bypass validation; alter scheduler state. It MAY only propose a `Block`, which enters the ordinary compiler pipeline. *(L27271–27285; L37781–37790.)*

**R-PLANNER-03 (staleness).** A proposal MUST be causally bound to the machine state from which it was generated. The machine MUST verify `proposal.observation_sequence = current_planning_epoch` and MUST otherwise reject it as `StalePlan` — a normal machine-visible outcome without state mutation. *(L27199–27236; L28373.)*

**R-PLANNER-04 (planner determinism).** The LLM MAY be non-deterministic. The machine MUST satisfy the determinism theorem: `InitialState + Plan + SchedulerTrace + HostTrace ⇒ UniqueMachineTrace`. For exact end-to-end replay, the machine MUST record a `PlannerAccepted { observation_sequence, proposal_digest, block }` record, and replay MUST consume the recorded proposal without querying the LLM. [INFORMATIVE: "deterministic" is explicitly defined by this state-transition theorem]. *(L27392–27414.)*

**R-PLANNER-05 (LLM outer-loop conformance, normative test obligation).** The conformance suite MUST include: (1) untrusted-input rejection — raw/malformed/malicious `Block` data fed directly to the runtime MUST be rejected at the compiler boundary; (2) stale-proposal rejection — advanced machine state + old proposal MUST yield rejection without state mutation; (3) end-to-end replay — live session vs replay with recorded proposal + `ReplayHost` MUST yield byte-for-byte identical final `GlobalState` and `EventLog`. *(L27920–27931; L28513–28521.)*

**R-PLANNER-06 (staleness is exact equality — frozen addendum).** `AcceptProposal(p) ⇔ p.observation_sequence = current_planning_epoch` — EXACT EQUALITY. A proposal whose `observation_sequence` differs from the current planning epoch in EITHER direction MUST be rejected with `Fault::StalePlan` and zero state mutation; the strictly-less-only reading (reject only when `< current`, thereby accepting future-tagged proposals) is SUPERSEDED (quoted, not deleted). The epoch check is the exact planner-boundary check: a proposal is causally bound to the machine state it was generated from, in both directions. Future-epoch proposals are a mandatory rejection test (`obs_seq ∈ {current−1, current, current+1, current+10⁹}`: accept only `current`, zero state mutation on both rejections). C-38's canonical description is corrected hereby: the two phrasings define different acceptance sets, not one check stated twice. *(Frozen addendum — post-audit remediation SEC-007; additive per R-SCOPE-03; extends R-PLANNER-03/R-PLANNER-05; resolves C-86; mutation M026; no source transcription.)*

**R-PLANNER-07 (observation channel is capability-opaque — frozen addendum).** The untrusted observation channel MUST be capability-opaque by construction: `Observation` carries capability *summaries* — counts, operation classes, ceilings — NEVER references; `CapabilitySummary` is frozen as a non-referential projection (defining the phantom); `Capability ∉ Observables(LLM)` is the dual of `LLMOutput ∈ Data`. The `EffectIssued` log/event shape carries `{id, actor, digest}` ONLY — the `EffectRequest`-with-`cap` shape in the log is SUPERSEDED (quoted, not deleted; the v0.3 rule-5 shape governs), and the `EffectRequest.cap` shape conflict is registered. Events visible to the planner are filtered/redacted by a frozen observation projection rule. Property: for every machine state and observation emission, `contains_capability(Observation) = false` (recursive, events included); no `0x30`/`0x05` payloads appear in planner-facing canonical encodings. *(Frozen addendum — post-audit remediation SEC-008; additive per R-SCOPE-03; extends R-PLANNER-01/R-KERN-01; resolves C-87; mutation M027; no source transcription.)*

## S-06 Compilation boundary

**R-COMPILE-01.** The compiler MUST enforce `Block ≠ ExecutablePlan`. Only validated executable plans MUST enter the trusted machine; no `Block` MUST bypass compilation. *(L41440–41452; L3834–3838.)*

**R-COMPILE-02 (pipeline).** Compilation MUST pass the stages: parse → normalize → validate → lower → capability analysis → resource analysis. Any failed stage MUST yield `fault(F_compilation)`; no raw `Block` MUST reach execution. *(L1930–1960 (J1–J4 and compilation theorem, superseded form); L39253–39267 (frozen pipeline).)*

**R-COMPILE-03 (static checks, frozen intent).** The static compilation judgment `Γ; κ_static ⊢ e : τ ! F @ B` MUST thread type, possible-effect set `F` (conservative over-approximation; pure terms MUST yield `F = ∅`), capability requirements, and static budget upper bound `B`. If a term's worst-case cost exceeds `B_max`, compilation MUST fail. *(L3874–3905 (v2 form); L1953–1980 (v1 J1–J4, superseded form).)*

**R-COMPILE-04 (plan immutability / temporal integrity).** An `ExecutablePlan` MUST be immutable; a new plan MAY only be produced by another validated compilation transition (plan₁ → execution/observation → planner → Block₂ → compiler → plan₂). A plan authorized at `t₀` MUST NOT silently acquire new authority at `t₁`. *(L1722–1745; L2052–2070 (v1 Theorem 6).)*

**R-COMPILE-05.** `ExecutablePlan` constructors MUST remain private to the compiler crate.  [INFORMATIVE (gap): The detailed effect-set inference (v1 judgment J2, `Γ ⊢ e ↝ Φ`) is not re-specified]. *(L39296–39318.)*

**R-COMPILE-06 (capability literals must be plan-bound — frozen addendum).** A `Block` MUST NOT carry a `Value::Capability` literal that is not plan-bound: compilation MUST fault on any embedded capability literal — foreign, garbage-generation, or own-but-undeclared — unless the compiler itself substituted it from the plan's declared capability set. Undecided capability-analysis depth (U-22) MUST NOT leave embedded authority literals unconstrained; this closes the U-22 gap in the security direction. *(Frozen addendum — post-audit remediation SEC-002 item 3; additive per R-SCOPE-03; extends R-COMPILE-02/R-COMPILE-03; no source transcription.)*

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

**R-CEK-03 (continuation frames).** The frozen frame set is: `LetValue { name, body, env } | Seq { second, env } | If { then, else, env } | CallFunction { args, env } | CallArgument { function, evaluated, remaining, caller_env } | Attenuate { name, body, env } | RequestCapability { operation, target, params, env } | RequestTarget { capability, operation, params, caller_env } | RequestArgument { capability, operation, target, evaluated, remaining, caller_env }`. `function.env` (closure lexical environment) and `caller_env` (call-site environment) are semantically different and MUST never be conflated. *(L16928–16958; L23821–23856.)*

**R-CEK-04 (lambda).** Lambda creation MUST be pure and deterministic: it MUST capture the lexical environment at creation and MUST produce `FunctionValue { params, body, env }`; the resulting value MUST pass through the ordinary value-return mechanism and MUST NOT halt the machine immediately. [INFORMATIVE: "deterministic" is explicitly defined in S-02 / R-CORE-08]. *(L16971–16995; L19095–19110 (attenuate/lexical invariant context).)*

**R-CEK-05 (call).** Function application MUST proceed left-to-right: (1) evaluate `func` to `FunctionValue`; (2) evaluate arguments left-to-right (`CEK-CALL-ARGS-LTR`); (3) pre-check arity (`CEK-CALL-ARITY-PRECHECK`) — mismatch MUST produce `fault(F_arity)` before frame stack allocation; (4) bind parameters in a fresh child environment inheriting captured bindings; (5) push return frame and evaluate body. *(L16878–16905 (frozen); L37840–37862; L18723–18851.)*

**R-CEK-06 (continuation preservation).** For pure transitions the continuation length changes by exactly +1 on entry or −1 on resume; no transition silently discards or duplicates frames.

**R-CEK-07 (progress & preservation).** A well-typed, well-budgeted configuration is either a value, a fault, pending an effect, blocked on a message, or can take a step; every transition preserves well-typedness and well-budgetness.

## S-09 Capability algebra

**R-CAP-01 (semantic domains, v0.2).** Authority MUST be defined as `A = {(o, ⟨S,Q,R,T⟩)}` mapping operation `o` to scope `S`, param predicate `Q`, resource limit `R`, and lifetime `T`. `CapRef` MUST be an opaque handle. Capability resolution MUST map `κ(c) → Authority`.






*(L6354–6379.)*

**R-CAP-02 (operation-indexed authority).** Authority is indexed by operation to prevent cross-operation contamination: `A = { (o, A_o) | o ∈ O_granted }` with `A_o = ⟨S, Q, R, T⟩`.

**R-CAP-03 (partial order).** `A₁ ≼ A₂` iff `O₁ ⊆ O₂` and for all `o ∈ O₁`: `S₁ ≼_S S₂ ∧ Q₁ ≼_Q Q₂ ∧ R₁ ≤ R₂ ∧ T₁ ⊆ T₂`.

**R-CAP-04 (constraint vs authority).** A `Constraint` is a *request to narrow* an existing grant, conceptually distinct from `Authority`.

**R-CAP-05 (derivation).** `derive(A, C) = { (o, derive_op(A_o, C_o)) | o ∈ O_A ∩ O_C }` where `derive_op(⟨S,Q,R,T⟩, ⟨S_c,Q_c,R_c,T_c⟩) = ⟨S ⊓ S_c, Q ⊓ Q_c, R ⊓ R_c, T ⊓ T_c⟩`. **Invariant:** `derive(A,C) ≼ A` holds by definition of meet.

**R-CAP-06 (canonical authorization predicate).** For effect `E = ⟨op, target, params, cost⟩` at logical time `t`: `Authorized(A, E, t) ⇔ op ∈ O_A ∧ target ∈ ⟦A_op.S⟧ ∧ A_op.Q(params) ∧ cost ≤ A_op.R ∧ t ∈ A_op.T`. The `cost` here is the effect's static resource requirement checked against the capability ceiling `R_A`; the dynamic execution budget is checked separately (dual gate). *(L6406–6421; L6647–6656.)*

**R-CAP-07 (revocation / lineage).** `Valid(c, t) ⇔ Live(c) ∧ t ∈ Lifetime(c) ∧ ∀a ∈ Ancestors(c). Live(a)`. Revoking a parent sets `Live(parent) = false`; descendants are invalidated lazily by walking the ancestor chain during the `Valid` check (O(d), d = lineage depth). **No authority amplification** and **ancestor revocation** are frozen obligations (tags `CAP-DERIVE-NO-AMPLIFICATION`, `CAP-REVOCATION-ANCESTOR`).

**R-CAP-08 (algebra theorems, frozen statements).** - Theorem 1 (Attenuation soundness): `derive(A,C) ≼ A`. - Theorem 2 (Authority monotonicity): `A' ≼ A ∧ Authorized(A',E,t) ⇒ Authorized(A,E,t)`. - Theorem 3 (Attenuation corollary): assuming `Authorized(A,E,t)`, `Authorized(derive(A,C),E,t) ⇔ Satisfies(C,E,t)`. These are `SPECIFIED` statements with proof sketches in the source; no mechanized proof exists in the repository (`PROVEN` is NOT claimed). *(L6422–6433; L6657–6671.)*

**R-CAP-09 (time).** Logical time `t` MUST NOT be fetched from the host OS; time `t` MUST be an explicit component of machine state (logical clock / deterministic timestamp) to ensure replay determinism. Wall-clock time MUST NOT be used as semantic machine state. [INFORMATIVE: "deterministic" is explicitly defined in S-02 / R-CORE-08]. *(L6434–6436; L38858–38890.)*

**R-CAP-10 (`AdmissibleConstraint` defined — frozen addendum).** `AdmissibleConstraint` is DEFINED: decidable well-formedness per semantic domain — operation set `O` nonempty and within the parent's interpretation, scope constraint `S` interpretable, predicate `Q` closed over params, resource ceiling `R` within the parent's, lifetime `T` a satisfiable interval. The derivation law is total on admissible inputs only: `¬AdmissibleConstraint(C) ⇒ ¬∃c'. derive(A,C) = c'` — `derive(A, C)` MUST fault (`Fault::InvalidConstraint`, in the R-CORE-13 closed enumeration; the `Invalid`-variant drift C-56 is resolved there), never identity: the ⊤-default reading (inadmissible constraint silently ignored, `derive(A, C_garbage) = A`) is FORBIDDEN. Constraints are attacker-authored (authored inside untrusted `Block`s: `Attenuate`, spawn manifests per R-ACTOR-09, `Delegate` per R-MARSHAL-05): the compiler MUST validate constraint admissibility at compile time (extends R-COMPILE-02/03) before any kernel call. Property: `derive` with an inadmissible constraint never returns a CapRef, across the full generated constraint space. *(Frozen addendum — post-audit remediation SEC-014; additive per R-SCOPE-03; extends R-CAP-04/R-CAP-05/R-COMPILE-06; resolves C-94, closing AMB-12/U-09's admissibility clause; mutation M030; no source transcription.)*

## S-10 Capability kernel

**R-KERN-01 (opaque references).** `CapRef { index: u32, generation: u32 }` MUST be opaque and generation-safe; fields MUST be private; public constructors from arbitrary integers MUST NOT exist; `CapRef`s MUST be constructed strictly by the capability kernel. [INFORMATIVE: generation safety is defined by generation-number mismatch checks preventing dangling reference reuse]. *(L9127–9133; L10178–10208.)*

**R-KERN-02 (API contract).** `CapabilityKernel` MUST own authority storage: `arena: GenerationalArena<AuthorityNode>`, `revocation_set: HashSet<CapRef>`. `derive()` and `revoke()` MUST be kernel operations.



*(L6672–6728; L19153–19175; L37870–37886.)*

**R-KERN-03 (substrate privacy).** `AuthorityNode` and all authority internals MUST remain `pub(crate)`/inaccessible to evaluator and runtime consumers. No hidden authority inspection.

**R-KERN-04 (holder-possession binding at the gate — frozen addendum).** Authority exercise at the machine's authorization gate MUST be possession-gated: `Authorized_gated(actor, c, E, t) ⇔ c ∈ CapabilityContext(actor) ∧ Valid(c, t) ∧ Authorized(κ(c), E, t)` — possession is a conjunct of the gated authorization predicate, not a marshalling courtesy. The kernel `authorize` API MUST be holder-parameterized (`authorize(holder, cap, effect, t)`) and MUST resolve the `CapRef` through the requesting actor's capability context; the global-arena no-holder form (`authorize(cap, effect, t)`) is SUPERSEDED (quoted, not deleted). `CapRef` bits MUST NOT suffice to exercise authority — `CapRef ≠ authority ownership` is a kernel-side possession rule. This binds the per-actor reading of the v0.3 formal rules (`Authorized(κ(c), E, t)`) over the kernel-substrate global arena (conflict C-77, resolved by this addendum). *(Frozen addendum — post-audit remediation SEC-002 items 1 and 4; additive per R-SCOPE-03; extends R-CAP-06/R-KERN-02; no source transcription.)*

**R-KERN-05 (CapabilityContext is a real possession type — frozen addendum).** `CapabilityContext` MUST be a real frozen type: the per-actor possession structure mapping the actor's capability slots to live `CapRef`s. The unit-type sketch (`pub type CapabilityContext = ();`) is SUPERSEDED (quoted, not deleted). Snapshots MUST carry the capability context, and recovery MUST reconstruct each actor's possession set before any gate authorization — a possession gate that does not survive recovery enforces nothing. *(Frozen addendum — post-audit remediation SEC-002 item 2; additive per R-SCOPE-03; extends R-KERN-02/R-KERN-04; no source transcription.)*

**R-KERN-06 (root-grant protocol — frozen addendum).** Authority enters the machine ONLY through the frozen grant protocol: `Grant(source, authority, ceiling, t)` MUST produce a durable `CapabilityGranted` record (the R-PERSIST-07 event kind) and the authority MUST stay `≼` the deployment ceiling; root authority is minted exactly once, at machine initialization, by the deployment — no runtime minting path exists. `Supervisor.host` is REMOVED from the `Supervisor` struct, or typed as an issued-effect-only handle: R-HOST-02 (host performs only issued effects) binds EVERY host caller, not only the machine — `HostInvoked ⇒ DurableIssued` with no exception for supervisor or integration code. Planner-facing I/O MUST be structurally separated from supervisor/runtime/compiler handles (the `ror-planner-io` split: the untrusted side emits `PlanProposal` data only, no compiler/runtime edges) — no crate containing LLM/planner I/O may depend on `ror-compiler` or `ror-runtime`. Audit test: every live root authority in a recovered arena traces to a durable `CapabilityGranted` record. *(Frozen addendum — post-audit remediation SEC-015; additive per R-SCOPE-03; extends R-KERN-01/R-HOST-02/R-PLANNER-02/R-TRUST-05; resolves C-95; no source transcription.)*

## S-11 Budget model

**R-BUDGET-01 (structure).** Budget `B = ⟨C, R, W⟩` where `C = ⟨F, I, D⟩` (consumables: fuel, I/O, duration), `R = ⟨M, S⟩` (reserved: memory bytes, concurrency slots), `W ∈ ℕ ∪ {∞}` (absolute logical-time deadline; `Deadline(None)` = infinity). Consumables are strictly decreasing and never returned; reserved capacities are held for a scope then released; the deadline is checked against logical time, not wall-clock.

**R-BUDGET-02 (checked arithmetic).** Budget operations MUST use checked arithmetic and expose failure (`BudgetError { ConsumableExhausted, ReservedCapacityExceeded, ReservedCapacityUnderflow, DeadlineExceeded }`). `saturating_sub` MUST NOT be used for semantic accounting.

**R-BUDGET-03 (reservation predicates).** `ReserveOK(r, R, R_max) ⇔ R + r ≤ R_max`; `ReleaseOK(r, R) ⇔ r ≤ R`; updates `R' = R + r` / `R' = R − r`. (Supersedes the earlier single `BudgetOK` that mixed directions — see `C-07`. )

**R-BUDGET-04 (dual-gate within-budget).** `WithinBudget(E, C, R, R_A) ⇔ cost_C(E) ≤ C ∧ ReserveOK(cost_R(E), R, R_max) ∧ cost(E) ≤ R_A` (effect cost within both runtime budget and capability ceiling).

**R-BUDGET-05 (conservation).** Effect issuance MUST escrow `complete_max` from consumable budget `C`. Effect completion MUST refund `complete_max - complete_actual` to `C_available`. Escrow conservation MUST hold invariant: `C_available + C_escrowed + C_consumed = C_initial`.



*(L7408–7425; L28203–28240 (frozen partition); L35210–35215.)*

**R-BUDGET-06 (time advancement).** Every transition has a logical-time delta `δ_t(c) ∈ ℕ`: pure computation `δ_t = 0`; host interactions and scheduler steps `δ_t > 0`. A transition is valid only if `t + δ_t(c) ≤ W`.

**R-BUDGET-07 (cost model).** Cost model `CostModel` MUST map operations to costs `Cost { consumable, reserved }`. Evaluator transitions MUST charge fuel cost before executing small-step transitions. *(L9155–9205; L10171–10177.)*

**R-BUDGET-08 (budget fault).** If `¬BudgetOK` (any gate fails), the transition is replaced by `fault(BudgetExhausted)`; no partial debit occurs.

**R-BUDGET-09 (escrow disposition totality — frozen addendum).** Escrow disposition is TOTAL: every unit entering the escrowed partition eventually leaves via exactly one frozen path — `Completed` (actual ≤ `complete_max` charged, remainder released), host-failure consumption (the C-23 rule), or durable `Reconciled` (R-RECOV-08). Held-forever-in-a-live-machine is NOT a disposition. Live faults unify with crash reconciliation: an actor fatal fault with an open effect enters the same reconciliation protocol as post-crash `Indeterminate`, and the supervisor fatal-fault policy MUST reference it. A logical-time bound moves stalled effects to reconciliation: a `Pending` effect whose deadline `W` expires (or a frozen per-effect logical timeout elapses) transitions to `Indeterminate` + reconciliation — machine state only, no wall clock (R-CAP-09), determinism preserved. Invariant: no reachable quiescent machine state contains escrow that no frozen rule can move; `C_available` shrinks only via `consumed` or durable `Reconciled`, never by strand. *(Frozen addendum — post-audit remediation SEC-021; additive per R-SCOPE-03; extends R-DUR-05/R-EFFECT-05/R-RECOV-08; resolves C-97; mutation M035; no source transcription.)*

**R-BUDGET-10 (resource-state atomicity — frozen addendum).** All resource mutations belonging to an operational transition occur transactionally: a failed precondition produces zero state drift and zero partial debit — `Precondition failure ⇒ Σ' = Σ` — except for post-issuance host-failure transitions, where `c_issue` remains consumed and the escrow is disposed via host-failure consumption/refund (R-DUR-07, R-BUDGET-11). This is the resource-level refinement of R-CORE-12's transition atomicity and R-CORE-14's s12–s14b atomic section: every Op-01…Op-22 transition is a single atomic resource mutation, and the `audit/_conservation_checker.py` randomized-transition harness is the gate evidence. *(Frozen addendum VIII — resource-accounting audit, owner decision 2026-09-03; additive per R-SCOPE-03; extends R-CORE-05/12, R-DUR-07; resolves C-108, decision U-45; no source transcription.)*

**R-BUDGET-11 (escrow disposition normal form — frozen addendum).** R-BUDGET-09's three paths are the escrow-disposition totality: every escrowed amount terminates via `Completed`, host-failure consumption, or durable `Reconciled`; the five-path normal form (`Consumed`, `Refunded`, `Transferred`, `Disposed-with-explicit-sink`, `Remains-Indeterminate`) is the complete fine structure OF that totality, not a fifth terminal path. `Consumed` (`C_consumed`) and `Refunded` (`C_available`) are the two leaves of `Completed` and of host-failure consumption (`actual ≤ complete_max` charged, remainder refunded; R-DUR-07). `Transferred` (child available partition) and `Disposed-with-explicit-sink` (`C_disposed` / `C_supervisor`) are the reconciled-outcome leaves selected per the R-RECOV-08 admissible-outcome table. `Remains-Indeterminate` (awaiting authoritative reconciliation) is a BOUNDED transient, not a disposition: it MUST reach reconciliation by the R-BUDGET-09 logical-time bound (machine state only, R-CAP-09) and then terminate via one of the four terminal leaves. No escrow may remain in any leaf indefinitely — the R-BUDGET-09 quiescent-strand invariant holds, and `C_available + C_escrowed + C_consumed + C_disposed = C_initial` at every reachable point. *(Frozen addendum VIII — resource-accounting audit, owner decision 2026-09-03; additive per R-SCOPE-03; extends R-BUDGET-09, R-DUR-05/07, R-EFFECT-05, R-RECOV-08/09; resolves C-108, decision U-45; mutation M039; no source transcription.)*

**R-BUDGET-13 (persistent-capacity accounting — frozen addendum).** Volatile RAM (`MEMORY` `M`) is kept strictly distinct from persistent storage capacity (`PERSISTENT_STORAGE` `M_storage`): RAM is released on scope exit or actor halt, while durable storage is retained across actor halts and managed via snapshot compaction (R-PERSIST-05/07, R-BUDGET-03 reservation predicates apply to each dimension separately). Persistent capacity MUST be accounted per WAL frame and per snapshot artifact; a snapshot that would exceed `M_storage` MUST fault, never silently truncate. *(Frozen addendum VIII — resource-accounting audit, owner decision 2026-09-03; additive per R-SCOPE-03; extends R-BUDGET-03/05, R-PERSIST-04/05/07; resolves C-108, decision U-45; no source transcription.)*

## S-12 Effect model and request sequence

**R-EFFECT-01 (request semantics).** Effect requests MUST proceed through the 16-step protocol: (1) evaluate `Request` expression; (2) resolve `CapRef`; (3) verify capability valid and unrevoked; (4) verify authorization `Authorized(c, e, t)`; (5) verify capability within ceiling; (6) verify budget available for `issue + complete_max`; (7) verify deadline `t ≤ W`; (8) verify host policy; (9) charge `issue` cost; (10) escrow `complete_max` cost; (11) reserve capacity; (12) allocate monotonic `EffectId`; (13) construct canonical `Effect`; (14) write durable `Prepared` log record; (15) emit `EffectRequest` to host; (16) write durable `Issued` record before host execution completes. *(L12177–12194.)*

**R-EFFECT-02 (gated transition shape).** Every active transition takes the canonical gated form: `Pre(c, Σ) ∧ BudgetOK(c, Σ) ∧ AuthOK(c, Σ) ⊢ Σ →_c Σ'`. `AuthOK` applies only to authority-requiring transitions.

**R-EFFECT-03 (frozen 16-step request sequence, canonical).** `EffectId` MUST be allocated from a global monotonic counter (`N' = N + 1`). `EffectId` MUST NOT be derived from wall-clock timestamps, memory addresses, or random generators. [INFORMATIVE: "deterministic" allocation is defined by monotonic integer counters].




















*(L37891–37908 (master-prompt 16-step, latest frozen form); L23857–23948 (14-gate machine-internal form, gates 1–14, superseded numbering — see `C-01`); L11053–11090 (14-step `step_request` form, superseded numbering).)*

**R-EFFECT-04 (short-circuit).** A denial at any gate MUST short-circuit: subsequent gates are not called, `next_effect_id` is not incremented, the actor budget is unchanged, the event log gains no new entries, and `HostExecutor::execute` is never invoked.

**R-EFFECT-05 (guaranteed completion accounting).** At issuance the machine MUST guarantee the maximum possible completion cost is affordable: gate 8 checks `can_consume(issue.checked_add(complete_max))` (overflow ⇒ `Fault::ArithmeticOverflow`/budget fault). The remaining budget is then mathematically guaranteed ≥ `complete_max`.

**R-EFFECT-06 (causal receipt validation).** A receipt MUST be validated against **both** `EffectId` and `EffectDigest` of the pending effect before resumption: mismatch ⇒ `fault(ReplayCorruption)`, continuation is NOT resumed, reservation is NOT released. `EffectReceipt { id, effect_digest, result: Result<Value, HostFault> }`.

**R-EFFECT-07 (completion accounting).** On valid receipt: charge `complete` (≤ `complete_max`) from consumables, release the reservation, append `EffectCompleted { id, digest, result }` to the event log, resume the continuation with the receipt's value (host faults map to the fault/value mapping defined by the machine).

**R-EFFECT-08 (receipt-result admission — frozen addendum).** A receipt may complete an effect; it MUST NOT confer authority. Before any continuation is resumed, the machine MUST run the recursive `contains_capability` predicate over the receipt's result payload at every nesting depth (`List`/`Map`/`Tuple` included) and MUST fault (`Fault::InvalidReceipt` family) on any `Value::Capability` and on any host `Function`/closure value. An admitted result MUST lie in the canonical data-domain (the 8-variant codec value set); host error results MUST enter machine values only through a declared, closed fault mapping — raw debug-formatted host text MUST NOT. This extends R-EFFECT-06 (causal validation of `id` and digest) from the receipt's identity to its payload: every value-crossing — messages, receipts, snapshots, replay traces — is subject to the no-raw-capability-transfer rule (R-CORE-07). *(Frozen addendum — post-audit remediation SEC-001 items 1–4; additive per R-SCOPE-03; extends R-EFFECT-06/R-EFFECT-07; no source transcription.)*

## S-13 Transactional issuance and durability boundary

**R-DUR-01.** `HostInvoked(E) ⇒ DurableIssued(E)`. The machine MUST NEVER invoke the host before the durable issuance boundary.

**R-DUR-02 (issuance transaction, strict order).** 1. Pure validation / authorization / budget checks; 2. `persistence.append(EffectPrepared { id, actor, digest })`; 3. `persistence.sync()` (fsync); 4. `persistence.append(EffectIssued { id, actor, digest })`; 5. `persistence.sync()` (fsync); 6. machine transitions actor to `Pending`; 7. host adapter receives `EffectRequest`. *(L35150–35158.)*

**R-DUR-03 (causal effect protocol).** `Issued(E) ⇒ Prepared(E)`; `Completed(E) ⇒ Issued(E)`; `Reconciled(E) ⇒ Issued(E)`. Every subsequent record for an effect MUST carry the identical `EffectId` and `EffectDigest`; a digest mismatch is `EffectJournalCorruption`, not a different effect.

**R-DUR-04 (crash classification of effects).** Effect state transitions MUST strictly follow `Prepared → Issued → Completed` or `Issued → Reconciled`. A prepared-but-never-issued effect MUST be discarded during recovery. An issued-but-not-completed effect MUST be classified as `Indeterminate` unless authoritative host reconciliation establishes its outcome. *(L35159–35176; L37968–37981.)*

**R-DUR-05 (escrow survives crash).** An `Issued` effect with no durable completion retains its `completion_maximum` in the `escrowed` partition until reconciliation determines the outcome. Escrow does not vanish on crash.

**R-DUR-06 (durable issuance payload — frozen addendum).** The issuance records MUST carry the effect and its cost: `EffectPrepared { id, actor, digest, effect_bytes, issue, complete_max, reserve }` and `EffectIssued { id, actor, digest, effect_bytes, issue, complete_max, reserve }` MUST be the persistence payloads — the canonical bytes of the effect, its `EffectDigest`, and the `EffectCost { issue, complete_max, reserve }`. The `{id, actor, digest}` shapes are SUPERSEDED as persistence payloads (quoted, not deleted); `{id, actor, digest}` remains valid only as the planner-visible observation projection (R-PLANNER-07). The escrowed `complete_max` and the reservation MUST thereby be reconstructible at every T0–T6 point: T1 discard restores from the record, T2–T4 classification and reconciliation carry the effect they must query about, and T5 resumption is byte-exact from the record. `effect_bytes` MUST verify `EffectDigest(effect_bytes) = digest` at append and at recovery — a mismatch is `EffectJournalCorruption` (C-105). The records MUST NOT contain raw capability values (R-CORE-07/R-CANON-12: the kernel-mediated codec governs). *(Frozen addendum VII — request-pipeline remediation, owner decision 2026-09-03; additive per R-SCOPE-03; extends R-DUR-02/05, R-PERSIST-03, R-EFFECT-05, R-RECOV-06; resolves C-105, decision U-41; mutation M038; no source transcription.)*

**R-DUR-07 (live issuance failure — frozen addendum).** Persistence failures on the issuance path are data, never panics (R-CORE-12), and MUST fault with the declared `Fault::PersistenceError`, added to the R-CORE-13 closed declaration by this addendum. The commit is journal-driven: `persistence.append(EffectPrepared …)` per R-DUR-06 followed by `persistence.sync()` is the ONE durable mutation that also journals the ID allocation and the budget/reservation/escrow commit; the in-memory mutations of steps 12–13 MUST NOT occur before that append+fsync returns Ok (C-106). On any append or sync error: the transition faults, `next_effect_id`, budget, reservations and escrow are at their pre-s12 values, the event log gains no entry, and `HostExecutor::execute` is NEVER invoked — R-EFFECT-04's five assertions hold on this path. A failure of the second `sync()` (the `Issued` record's fsync) is likewise `Fault::PersistenceError`, with the machine rolled back to the `Prepared`-durable state and the journal classifying the effect `Prepared ∧ ¬Issued ⇒ Discard` at recovery (R-DUR-04, R-RECOV-02 T1). No `InternalInvariant` classification is permitted for a storage error — this is the single declared fault family for the issuance path. *(Frozen addendum VII — request-pipeline remediation, owner decision 2026-09-03; additive per R-SCOPE-03; extends R-DUR-02/04, R-EFFECT-04, R-CORE-12/13, R-PERSIST-02/03; resolves C-106, decision U-42; mutation M037; no source transcription.)*

## S-14 Host boundary and replay

**R-HOST-01 (host gate, defense in depth).** The live host independently validates concrete OS-level authority/policy for each effect (`HostPolicyOK`); `¬HostPolicyOK(E) ⇒ ¬ExternalEffect(E)`. The machine's gate-11 check is fail-early; the host check is authoritative.

**R-HOST-02 (host adapter scope).** The host performs **only issued effects**. It is partially trusted.

**R-HOST-03 (replay host).** `ReplayHost` reconstructs recorded effects; it NEVER touches the external world. It is **ordered**: for every request it consumes the next trace entry and validates both `EffectId` and `EffectDigest` sequentially; a mismatch or exhausted trace ⇒ `ReplayCorruption`/`ReplayTraceExhausted`. An unordered map MUST NOT be used as the normative replay mechanism.

**R-HOST-04 (replay correspondence theorem).** If `LiveRun(Σ₀)` produces trace `T` of (EffectIssued, EffectCompleted) pairs, `ReplayRun(Σ₀, T)` produces the same final configuration, provided replay verifies for each step `E_replay,k = E_recorded,k` and `R_replay,k.id = R_recorded,k.id` (and, in the frozen form, matching digests). Machine-state replay is always valid; real-world replay is only valid for reversible/idempotent effects — the replay host refuses to re-execute irreversible effects and returns the recorded result.

**R-HOST-05 (replay validates trace, not just final state).** Replay MUST validate the trace, not merely load the final state.

**R-HOST-06 (durable receipt results — frozen addendum).** Durable receipt results MUST be representable under a frozen contract: `EffectCompleted` carries `{id, digest, result_digest, result: CanonicalData}` — `result` scoped to the canonical data domain (R-CANON-12 / the R-EFFECT-08 admission rule). Replay MUST verify `ResultDigest(result) = result_digest` before the receipt may resume anything: a third identity conjunct extending R-EFFECT-06 (id, effect digest, result digest). Tampering `result` while keeping the digest-pair ⇒ `ReplayCorruption`. No ad-hoc result-bearing record kind may exist outside this contract (the unfrozen-record channel is closed); T5 recovery resumes the continuation with the recorded result byte-exactly. *(Frozen addendum — post-audit remediation SEC-011; additive per R-SCOPE-03; extends R-EFFECT-06/R-EFFECT-08/R-HOST-03/R-HOST-04; resolves C-90; mutation M029; no source transcription.)*

## S-15 Actors and deterministic scheduling

**R-ACTOR-01 (isolation).** Actors have isolated environments, continuations, heaps, mailboxes, budgets, and capability contexts. For `a ≠ b`: `Heap(a) ∩ Heap(b) = ∅ ∧ Env(a) ∩ Env(b) = ∅`. No actor mutates another actor's heap, environment, or continuation. Actors are instantiated with fresh arenas and `Environment::empty()` (no implicit environment inheritance).

**R-ACTOR-02 (global state).** Global state MUST manage actors in a `BTreeMap<ActorId, ActorState>`. Global time `LogicalTime` MUST advance monotonically on scheduler steps. *(L24148–24163; L25514–25546.)*

**R-ACTOR-03 (deterministic IDs).** `ActorId` and `EffectId` MUST be allocated by global monotonic counters (`N' = N + 1`). Actor identity MUST NOT be derived from memory addresses, OS PIDs, random UUIDs, thread IDs, or wall-clock timestamps. [INFORMATIVE: "deterministic" allocation is defined by monotonic integer counters]. *(L24226–24245.)*

**R-ACTOR-04 (FIFO scheduler).** Scheduler queue `RunnableQueue` MUST enforce FIFO order and at-most-once membership for runnable actors. Duplicate runnable queue entries MUST NOT exist. *(L25558–25615 (frozen with at-most-once invariant); L24165–24224; L37924–37937.)*

**R-ACTOR-05 (spawn).** Spawn MUST be a deterministic, transactional machine operation: (1) validate and escrow budget (`BudgetAllocationSpec` → `validate_and_escrow`); (2) allocate child `ActorId`; (3) derive child capabilities via `kernel.derive(parent_cap, constraint, t)`; wholesale capability copying/cloning MUST NOT occur; (4) construct isolated child state; (5) enqueue child into runnable queue deterministically; (6) log `ActorSpawned`. [INFORMATIVE: "deterministic" is explicitly defined in S-02 / R-CORE-08]. *(L25573–25615; L25616–25673; L37941–37951.)*

**R-ACTOR-06 (send/receive).** `Send` MUST be asynchronous: marshal the value, enqueue into target mailbox, log `MessageSent`, and deterministically wake a `Blocked` target exactly once. `Receive` MUST dequeue (unmarshal) or, on empty mailbox, block without consuming fuel (`Blocked` MUST be a suspension state, yielding to scheduler). Mailboxes MUST be FIFO. *(L25702–25749; L25674–25701; L37941–37951.)*

**R-ACTOR-07 (deterministic concurrency theorem).** Concurrency MUST satisfy the deterministic scheduling theorem: `InitialState + SchedulerTrace + HostTrace ⇒ UniqueMachineTrace` — scheduler MUST be strictly FIFO, IDs MUST be monotonic, CEK machine MUST be deterministic; hence global state transitions MUST be uniquely determined given identical initial state and external observations. [INFORMATIVE: "deterministic" is explicitly defined by this theorem]. *(L25759–25766 (Theorem 1).)*

**R-ACTOR-08 (no amplification / no teleportation theorems).** `Authority_after ≼ Authority_before ∪ ExplicitlyDelegatedAuthority` (ordinary `Send` passes through `marshal()`, which rejects raw capabilities). `Σ_actors C_consumable + Σ_escrow C_escrow + Σ_issued C_issue = C_global_initial` (budget is created only at root initialization; spawn escrows; send carries no budget).

**R-ACTOR-09 (spawn authority rule — frozen addendum).** `Expr::Spawn` MUST NOT transfer parent capabilities by default: a spawned child's initial authority context is empty, and delegation (R-MARSHAL-05) is the only default transfer path. Any spawn-time authority transfer MUST be explicit: the plan declares a capability manifest plus constraint, compiler-checked against the plan's declared capability set (the R-COMPILE-06 discipline), and the kernel derives each manifest entry strictly attenuated (constraint ≠ ⊤ — identity derivation is not spawn). The spawn security theorem is strict: `Authority(child) ≺ Authority(parent)` — `≼` is reserved for delegation; wholesale capability copying (iterating the parent context under one constraint) is FORBIDDEN: the engineering rule binds the default case, not only explicit cloning. The v0.3 `trust_level`/`attenuated_context(κ_parent, trust_level)` form is SUPERSEDED (quoted, not deleted; the AMB-04 phantom is resolved by retraction). `BudgetAllocationSpec::validate_and_escrow` MUST be bounded: maximum child share, minimum parent retention, fault on violation (closes U-03 in the security direction). *(Frozen addendum — post-audit remediation SEC-006; additive per R-SCOPE-03; extends R-ACTOR-05/R-COMPILE-06/R-MARSHAL-05; resolves C-82; mutation M025; no source transcription.)*

**R-ACTOR-10 (mailbox resource admission — frozen addendum).** Mailbox admission is resource-gated: `Enqueue(v, target)` requires available recipient mailbox capacity — capacity is part of the recipient's `M` reservation — and on denial the SENDER faults with `ReservedCapacityExceeded` (sender pays; never silent growth). The send cost MUST be payload-proportional: `cost_C(send) ≥ f(canonical_len(v))` for a frozen monotone `f` bounded away from zero per byte (deterministic over canonical bytes, replay-stable). Constructed value size is bounded against the constructing actor's `M` reservation (allocation is the resource the reservation exists for). Invariant: for any reachable state, the total mailbox footprint is bounded by total reserved `M` at every step — the resource-bounded thesis holds in the heap, not only in the algebra. *(Frozen addendum — post-audit remediation SEC-019; additive per R-SCOPE-03; extends R-ACTOR-06/R-BUDGET-01/R-EFFECT-04; resolves C-96, closing the U-03/U-07 resource-admission direction; mutation M033; no source transcription.)*

## S-16 Marshalling and delegation

**R-MARSHAL-01 (capability rejection, recursive).** Ordinary data marshalling MUST reject capabilities recursively — including capabilities nested inside lists, tuples, functions, or any nested structure. Raw `CapRef` transfer through ordinary messages is forbidden: `marshal_value(v) ⇒ Err(MarshalFault::CapabilityRequiresDelegation)` if `contains_capability(v)`.

**R-MARSHAL-02 (explicit delegation).** Raw capability references `Value::Capability(CapRef)` MUST NOT be transferred through ordinary messages; ordinary marshalling MUST reject raw capabilities with `MarshalFault`. Delegation of authority MUST require explicit `Value::DelegatedCapability(DelegatedCapability)` envelopes. *(L25972–26001; L37953–37959.)*

**R-MARSHAL-03 (canonical transport).** `MarshalledValue` is the canonical serialized byte representation (`canonical_serialize(v)`); `unmarshal(marshal(v)) = v` for all pure values.

**R-MARSHAL-04 (semantic marshalling rule).** `marshal(v)` traverses `v`; by default `CapRef ∉ marshal(v)`; authority transfer requires the explicit `delegate(c, C, target_actor)` operation.

**R-MARSHAL-05 (delegation surface constructible and revalidated — frozen addendum).** The sanctioned authority-transfer channel MUST be constructible as frozen: `Expr::Delegate { capability, constraint }` evaluates by calling `kernel.derive` with the declared constraint and produces a kernel-constructed delegation envelope — NOT a plain `Value` variant; `Value::DelegatedCapability` as a data variant is forbidden. Envelope admission at `Receive`: `register(envelope, recipient)` MUST be preceded by kernel revalidation — liveness, lineage (`DelegatedAuthority ≼ ParentAuthority`), target binding, and generation — against an existing kernel derivation record `d` with `envelope.cap = d.child ∧ d.parent ∈ sender.context`; any failure MUST fault with the recipient's `CapabilityContext` byte-identical (no partial registration). `MarshalledValue` is the checked-bytes form (R-MARSHAL-03): mailbox bytes MUST NOT exist as a `Value`, snapshots storing mailboxes store the checked form, and the private-constructor-wrapper reading is SUPERSEDED (quoted, not deleted). `MarshalFault` has ONE unified closed variant set. *(Frozen addendum — post-audit remediation SEC-005; additive per R-SCOPE-03; extends R-MARSHAL-02/R-MARSHAL-04; resolves C-79 and, at the normative layer, term/ X-65; no source transcription.)*

**R-MARSHAL-06 (contains_capability is a frozen total predicate — frozen addendum).** `contains_capability(v)` MUST be a total predicate with an explicitly closed traversal domain: it MUST descend recursively, at unbounded structural depth, into `List`, `Map` (keys and values), `Tuple` elements, and — the load-bearing case — `FunctionValue.env` (captured closure environments, recursively: environments bind names to `Value`, and a closure whose environment binds a capability carries authority). Kernel-sealed delegation envelopes (R-MARSHAL-05) are the sole exclusion, and then only sealed by the kernel. `Bytes` are data — the decode-side rule (R-CANON-12) governs their rehydration. The boundary invariant is stated over reachability, not one value domain: `marshal(v) = Ok ⇒ ¬∃c. Reachable(env_of(v), c)` outside kernel-sealed envelopes. Closure-carrying values whose environments bind capabilities MUST fault at `marshal`, never round-trip. *(Frozen addendum — post-audit remediation SEC-018; additive per R-SCOPE-03; extends R-CORE-07/R-MARSHAL-01; resolves C-81; no source transcription.)*

## S-17 Canonical serialization (frozen wire format, Phase 15A)

**R-CANON-01 (purpose & independence).** Semantic serialization is explicit and independent of Rust memory layout and of any Rust serializer. `bincode` may *implement* the format but MUST NOT *define* it. Canonical encoding defines semantic identity; it is not based on struct layout, pointer addresses, allocator behavior, or platform-specific representation.

**R-CANON-02 (universal envelope, frozen).** ``` Envelope := version: u8            (currently 0x01) + type_tag: u8           (stable explicit constant per type) + payload_length: u32 BE (checked) + payload: bytes[payload_length] ``` *(L30532–30543; L33290–33347 (final frozen).)*

**R-CANON-03 (type tags, frozen).** Standalone envelope tags: `Value` = `0x00`; `Symbol` = `0x20`; `CapRef` = `0x30`; `ActorId` = `0x40`; `EffectId` = `0x41`. **Non-normative note:** the "revised grammar" §1.3 text listing Boolean `0x10` / Integer `0x11` / String `0x13` as standalone tags is stale and contradicted by the golden vectors and the final frozen implementation (see `C-02`); bool/integer/string exist only as `Value` discriminants.

**R-CANON-04 (Value encoding, frozen).** Collection encodings (List, Tuple, Map) MUST prefix element counts as `u32` length headers. Decoders MUST verify payload byte availability before allocating collection memory. *(L30544–30552 (correction); L33155–33265 (final).)*

**R-CANON-05 (primitives, frozen).** `Symbol(u32)` payload = 4 bytes BE; `CapRef` payload = `[index u32 BE][generation u32 BE]`; `ActorId`/`EffectId` payloads = 8 bytes u64 BE.

**R-CANON-06 (collections, frozen).** `List = [count u32 BE][element₁]…[elementₙ]`, each element a complete envelope. `Map = [count u32 BE][key₁][val₁]…`, entries ordered by the **semantic `Ord` relation on keys** (for `BTreeMap<u32, Value>`: numeric u32 order). Map decoding MUST reject duplicate keys (`CanonicalError::DuplicateMapKey`) to preserve injectivity.

**R-CANON-07 (decoder contract, frozen).** `CanonicalDecode` is a strict parser enforcing, in order: (1) version = `0x01`; (2) type tag matches expected; (3) exact length (payload is exactly `payload_length` bytes); (4) internal payload well-formedness; (5) EOF/trailing-byte rejection. All discriminants are explicit stable constants (source-order changes MUST NOT change the wire format). Malformed encodings are rejected with explicit `CanonicalError` values (`InvalidVersion, InvalidTypeTag, LengthMismatch, LengthOverflow, InvalidUtf8, UnexpectedEof, TrailingBytes, InvalidDiscriminant, InvalidBoolValue, DuplicateMapKey`).

**R-CANON-08 (checked arithmetic).** All length/pointer arithmetic is checked. A collection exceeding `u32::MAX` yields `LengthOverflow`. Encoded collection counts MUST NOT authorize attacker-controlled preallocation (collections grow organically from `Vec::new()`, no `with_capacity` on untrusted input). Nested decoding uses bounded cursors (`read_envelope_payload` returns only the payload slice; payload decoding uses a fresh bounded cursor). Envelope construction is fallible (no panics).

**R-CANON-09 (digests).** `StateDigest = SHA-256(canonical_bytes)`; `EffectDigest = SHA-256(canonical_bytes(effect))`. Mechanically: `Canonical(x) = Canonical(y) ⇒ Digest(x) = Digest(y)`. The reverse direction holds only as an operational integrity assumption under cryptographic collision resistance. When both states are available, compare canonical bytes directly; use digests for persistence integrity, causal identity, and compact checkpoints.

**R-CANON-10 (injectivity, scoped claim).** Injectivity (`Canonical(x) = Canonical(y) ⇒ x = y`) is a **structural specification property** of the encoding design; the conformance suite provides machine-checked evidence via round-trip and differential testing over the generated distribution. It is NOT claimed as a mathematical proof of arbitrary Rust programs.

**R-CANON-11 (golden vectors, normative fixtures).** The frozen golden vectors (e.g., `Value::Integer(42)` ⇒ `01 00 00 00 00 09 02 00 00 00 00 00 00 00 2A`; `CapRef{5,2}` ⇒ `01 30 00 00 00 08 00 00 00 05 00 00 00 02`) are normative **test fixtures** for the format, not additional behavioral rules.

**R-CANON-12 (decode-side authority minting forbidden — frozen addendum).** The data codec — the decoder for messages, receipt results, plan literals, and mailbox/snapshot value payloads — MUST reject capability payloads on decode: discriminant `0x05` (`TAG_CAPABILITY`) and standalone `0x30` (`CapRef::TYPE_TAG`) MUST yield `CanonicalError::CapabilityInData`, not a `Value::Capability`. Only the kernel-mediated codec path — persistence of kernel authority state and kernel-sealed delegation envelopes (R-MARSHAL-05) — may produce or consume capability payloads. `unmarshal` MUST run `contains_capability` (R-MARSHAL-06) over the decoded value regardless of provenance, making the marshalling boundary symmetric with `marshal`. Property: for all bytes `b`, `contains_capability(unmarshal_data(b)) = false ∨ unmarshal_data(b) = Err`. Resolves C-14/U-02 in the direction of the design rule (a serialized capability must go through explicit delegation); negative golden vectors (capability bytes, nested-at-depth, standalone envelope) are normative fixtures. *(Frozen addendum — post-audit remediation SEC-003; additive per R-SCOPE-03; extends R-CANON-11/R-MARSHAL-03; resolves C-78; no source transcription.)*

**R-CANON-13 (one canonical grammar — frozen addendum).** Exactly ONE canonical byte grammar is frozen: Phase 15A — universal envelope `version u8 / type_tag u8 / payload_length u32 BE`, length prefixes `u32 BE`, `CapRef [index u32 BE][generation u32 BE]`. The revised-grammar Little-Endian sections are SUPERSEDED in-source (quoted, not deleted); field names are the 15A names (`payload_length`); the `TAG_*` constants denote ONE namespace (the 15A tags; the revised-grammar tag set is superseded) — resolving term/ X-50/X-54. All integrity predicates (`EffectDigest`, `StateDigest`, `ResultDigest`, WAL checksum inputs) are defined over 15A bytes alone; cross-implementation digest equality is meaningful by construction (R-CANON-01: canonical encoding defines semantic identity). Golden vectors are asserted byte-exact bidirectionally for production, reference, and the persistence payload writer; LE-encoded variants of every golden vector MUST be rejected by all three. *(Frozen addendum — post-audit remediation SEC-017; additive per R-SCOPE-03; extends R-CANON-01/R-CANON-11/R-PERSIST-01; resolves C-92; mutation M031; no source transcription.)*

## S-18 Persistence protocol (Phase 15B)

**R-PERSIST-01 (separation).** The persistence layer is not a semantic machine; it records and reconstructs the existing machine. **No secondary serialization:** the payload of every persistence record is strictly the byte output of Phase 15A `CanonicalEncode`.

**R-PERSIST-02 (two-level framing).** WAL append operations MUST write `WalFrame` records with incrementing `WalSequence` counters. Sequence gaps MUST NOT be permitted. *(L33802–33830; L35088–35110.)*

**R-PERSIST-03 (record taxonomy).** `WalRecord ::= Event(EventEnvelope) | EffectPrepared { id, actor, digest } | EffectIssued { id, actor, digest } | EffectCompleted { id, digest, result_digest } | EffectReconciled { id, digest, outcome } | SnapshotCommit { event_sequence, snapshot_version, state_digest }`. `EventEnvelope { sequence: EventSequence, logical_time: LogicalTime, event: GlobalEvent }` with `e_i.sequence < e_{i+1}.sequence` (total ordering).

**R-PERSIST-04 (snapshot content).** Global snapshots MUST capture complete machine state necessary for resumption: logical_time, ID counters, runnable queue, actor states, capability arena, budget state, effect journal cursor. Snapshots MUST be canonical 15A encoded. *(L26293–26330.)*

**R-PERSIST-05 (atomic snapshot protocol).** Snapshot creation MUST follow atomic protocol: (1) write `SnapshotBegin` marker; (2) write canonical `GlobalSnapshot` payload; (3) fsync payload; (4) write `SnapshotCommit` record with `state_digest`. Incomplete snapshots MUST be discarded during recovery. *(L26216–26240; L35177–35188.)*

**R-PERSIST-06 (sequence continuity).** WAL sequence continuity MUST hold (`s_{n+1} = s_n + 1`); gaps MUST be rejected (obligation tag `WAL-GAP-REJECT` / `WAL-SEQUENCE-CONTINUITY`). *(L35088–35110; L35189–35208.)*

**R-PERSIST-07 (durable authority lattice — frozen addendum).** The kernel authority image — `AuthorityNode` set with parent links, the `revocation_set`, and generation counters — MUST be durable: snapshots MUST contain it (the invariant is frozen here; byte encoding remains U-02 scope), and the WAL MUST carry `CapabilityGranted`, `CapabilityDerived`, and `CapabilityRevoked` event kinds (freezing the event set in the security direction). Recovery MUST reconstruct the kernel arena, replay capability events after the snapshot sequence, and reject with `RecoveryFault` — never silently repair (R-RECOV-05, R-CORE-10) — any CapRef (in contexts, heaps, frames, mailboxes) that does not resolve with matching generation. Post-recovery, every actor capability MUST be revalidated: `∀ a, ∀ c ∈ caps(a): Valid(c, t_recovered)`; revocation MUST be monotonic across crashes — a revoked capability MUST NOT become valid again without a new explicit grant. `Recover(D) ≡ PreCrashMachineState` includes the authority lattice. *(Frozen addendum — post-audit remediation SEC-004; additive per R-SCOPE-03; extends R-PERSIST-04/R-CAP-07/R-CORE-09; tag `RECOVERY-REVOCATION-DURABLE`; no source transcription.)*

**R-PERSIST-08 (storage integrity rewinding-resistance — frozen addendum).** Persistence integrity MUST gain rewinding resistance: WAL checksums MUST be chained (`checksum_n = H(checksum_{n−1} ‖ frame_n)`) so rewrite or truncation of any prefix breaks every later frame; the snapshot commit record MUST cover the state digest and the last WAL sequence. If the storage medium is adversarial, the chain MUST be keyed (MAC or signature over the sequence-linked chain; key-epoch mismatch ⇒ `RecoveryFault`); if the storage medium is trusted-writable, that assumption MUST be recorded in the trust table as such — keyless chaining detects corruption and rewinding but does not authenticate, and the accepted risk is documented explicitly. Consistently forged records (recomputed checksums, contiguous sequences, balanced budget) are the mandatory negative test class. `Durable(D) ⇒ Authentic(D)` where keyed; the effect evidence chain (`Prepared → Issued → Completed → Reconciled`) must be unforgeable, not merely well-ordered. *(Frozen addendum — post-audit remediation SEC-009; additive per R-SCOPE-03; extends R-PERSIST-02/R-PERSIST-05; resolves C-88; no source transcription.)*

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

**R-RECOV-08 (reconciliation protocol — frozen addendum).** Reconciliation is frozen: I2 (the 7-conjunct chain) holds for EVERY host invocation path including supervisor/reconciliation ones — `Reconcile(E) ⇒ Issued(E) ∧ outcome ∈ AdmissibleOutcomes(class(E))`, with per-effect-class admissible outcome variants (closing U-06/U-15 in the security direction). Reconciliation NEVER re-executes an effect: an idempotent host query at most; any compensating or retry action is itself an ordinary `Request` through gates 1–16. `NotExecuted` as a durable resolution is gated behind authoritative host-reconciliation evidence — no component, trusted or not, may resolve `Indeterminate → NotExecuted` on local policy (R-DUR-04); `Completed(EffectReceipt)` inherits the R-EFFECT-08 result-admission rule and R-HOST-06 result-digest verification. The Supervisor allocates lifecycle decisions, not effects: `Supervisor.host` is reachable only through the issuance boundary. Escrow moves only per the frozen admissibility table. *(Frozen addendum — post-audit remediation SEC-010; additive per R-SCOPE-03; extends R-DUR-04/R-DUR-05/R-RECOV-07; resolves C-89; mutation M028; no source transcription.)*

**R-RECOV-09 (recovery reconstruction authority — frozen addendum).** Recovery MUST reconstruct `next_effect_id = max({id ∈ replayed EffectIssued}) + 1`; a snapshot counter less than the journal maximum is stale and MUST be advanced (recorded, never silently repaired). A snapshot counter GREATER than the journal maximum is a `RecoveryFault`. No `SnapshotCommit` MAY exist with its last-effect sequence inside an issuance section (steps 12–14b) — the recovery of such a snapshot, if ever found, is a `RecoveryFault`, and the snapshot-taker MUST serialize against the section (C-107). The completion order is frozen: `append(EffectCompleted)`, then `sync()`, then the charge/release accounting, then the continuation resume (R-EFFECT-07) — a crash after the host returns but before that fsync is T4 (`Indeterminate`), and byte-exact resumption (T5) requires the fsync to precede the resume (C-109). *(Frozen addendum VII — request-pipeline remediation, owner decision 2026-09-03; additive per R-SCOPE-03; extends R-PERSIST-04/05/06, R-RECOV-02/03/07, R-EFFECT-07; resolves C-107/C-109, decision U-43; no source transcription.)*

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

**R-TEST-12 (request-frame verification tags — frozen addendum).** The R-TEST-07 obligation-tagged coverage list MUST additionally include `REQUEST-ARGS-LTR` (request arguments evaluated strictly left-to-right, exactly one per CEK step; step 3 of the frozen sequence, R-EFFECT-01) and `REQUEST-NON-CAP-SHORT-CIRCUIT` (a non-capability capability expression faults before any target/parameter evaluation and before any step 4–16 runs, with no `EffectId`, budget or log mutation and no host invocation; R-EFFECT-04). Both tags MUST be covered by the request-path Track A suite, registered in `spec/08`, and tracked in `mod/05`/`mod/08`. Coverage of these tags MUST NOT substitute for the differential oracle (R-TEST-07). *(Frozen addendum VII — request-pipeline remediation, owner decision 2026-09-03; additive per R-SCOPE-03; extends R-TEST-07; resolves decision U-44; no source transcription.)*

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

*(Frozen addendum VI — owner decision 2026-09-03, resolving `dep/05` V-09; additive per R-SCOPE-03; refines R-REPO-02/R-BUDGET-01…09; no source transcription.)*

**Budget crate home made explicit (normative refinement).** The R-REPO-02 `ror-kernel` bullet's "budget primitives" MUST be read as: the kernel CONSUMES the budget operand types defined in `ror-core`; no budget algebra, operand type or per-transition gate lives in `ror-kernel`. The shared ceiling/operand types MUST live in `ror-core` (`ror-core → ror-kernel` is forbidden by §14's frozen list, upheld by R-TRUST-05); per-transition gate CALLS live in `ror-runtime` (`spec/07` §2 already splits the R-BUDGET obligations across `ror-core` and the runtime gates). MOD-04 BUDGET keeps one module with an explicit two-crate home — algebra + operand types in `ror-core`, gate calls in `ror-runtime` (`mod/04` DEPENDENCIES states it).

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
