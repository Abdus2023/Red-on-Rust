# FINAL1 — 03. Canonical Requirement Registry

Generated from `spec/03` (cleaned obligation matrix); the `R-…` IDs and their canonical normative text are single-homed in `spec/01` — re-homed here by FINAL1 into `final/01` §01–§28 verbatim (byte-verified; `final/07` §3).

## Registry governance (inherited, binding)

- Every normative requirement has **exactly one stable ID**; IDs are never renumbered, reused, or silently reinterpreted (FINAL1 requirement + `spec/00` §3).
- The registry is preserved as it stands in the frozen authorities; owner-approved change history: 148 frozen-source obligations + 36 post-audit frozen addendum obligations = **184** the 36 are enumerated by ID in `spec/03`'s total line — `spec/03` records no per-addendum split, so none is asserted here).
- **ID space gaps are deliberate and non-reusable:** `R-BUDGET-12` (proposal folded into R-BUDGET-15/16 by addendum IX; no ID frozen) and `R-BUDGET-14` (deferred to a resource-family pass). No other gaps: all areas are dense up to their maximum.
- Every row retains its verification/evidence state; **all 184 are `SPECIFIED`** — no promotion by this or any other document without explicit evidence (`spec/00` §2 ladder; §28).

## The registry

| R-ID | Obligation (short) | Provenance | Status | Impl→ | Verify→ | Home § | Cleaned § |
|---|---|---|---|---|---|---|---|
| R-SCOPE-01 | Thesis: deterministic, capability-scoped, resource-bounded, crash-recoverable machine | L41293–41300 | SPECIFIED | — | — | §01 | S-01 |
| R-SCOPE-02 | Architecture/spec/verification FROZEN; frozen ≠ verified | L38929–38942, L41297–41315 | SPECIFIED | — | — | §01 | S-01 |
| R-SCOPE-03 | STOP-and-report on ambiguity; no silent semantic modification | L37664–37686 | SPECIFIED | all | R-TEST-09 | §01 | S-01 |
| R-SCOPE-04 | Zero shared core logic production/reference | L37696–37721 | SPECIFIED | ror-reference, ror-differential | R-REF-02, dependency-graph review | §01 | S-01 |
| R-CORE-01 | LLMOutput ∧ UntrustedInput ↛ ExternalEffect | L41320–41335, L27505–27513 | SPECIFIED | all | R-PLANNER-05, mutation M004–M008 | §02 | S-02 |
| R-CORE-02 | ExternalEffect chain (7 conjuncts) | L41337–41351, L27491–27509 | SPECIFIED | all | R-TEST-07 tags | §02 | S-02 |
| R-CORE-03 | ¬Authorized ⇒ ¬ExternalEffect | L42056–42064, L7413–7419 | SPECIFIED | ror-kernel, ror-runtime | M004, M005 | §02 | S-02 |
| R-CORE-04 | derive(A,C) ≼ A (no amplification) | L42066–42072, L6399–6406 | SPECIFIED | ror-kernel | CAP-DERIVE-NO-AMPLIFICATION, M006 | §02 | S-02 |
| R-CORE-05 | Budget partition conservation (no teleportation) | L42074–42080, L28203–28240 | SPECIFIED | ror-core, ror-runtime | BUDGET-CONSUMPTION-CONSERVATION, BUDGET-ESCROW-CONSERVATION, M007, M009 | §02 | S-02 |
| R-CORE-06 | HostInvoked ⇒ DurableIssued | L42082–42088, L35150–35156 | SPECIFIED | ror-runtime, ror-persistence, ror-host | EFFECT-ISSUE-DURABLE-BEFORE-HOST | §02 | S-02 |
| R-CORE-07 | Ordinary marshal rejects raw capabilities | L42090–42098, L25972–26001 | SPECIFIED | ror-runtime | MARSHAL-NO-RAW-CAPABILITY (source tag MARSHAL-CAPABILITY-REJECT), M006-class | §02 | S-02 |
| R-CORE-08 | Determinism: state+traces ⇒ unique machine trace | L41623–41646, L27518–27547 | SPECIFIED | ror-runtime | SCHED-FIFO, R-REF-05 | §02 | S-02 |
| R-CORE-09 | Causal crash recovery (qualified theorem) | L27551–27569, L35159–35176 | SPECIFIED | ror-persistence | R-RECOV-02 T0–T6 | §02 | S-02 |
| R-CORE-10 | No silent recovery corruption | L42100–42105, L35196–35208 | SPECIFIED | ror-persistence | M015, M016, negative recovery tests | §02 | S-02 |
| R-CORE-11 | One canonical signature per I2 predicate: ValidatedRequest(E) request-time subsuming ValidatedPlan(plan(E)); Authorized(holder, c, E, t) possession conjunct (formalizes R-KERN-04); ValidatedPlan_pred vs ValidatedPlan_struct; chain stated once (X-01/X-04/X-05; C-80 resolved) | addendum (SEC-016) | SPECIFIED | ror-kernel, ror-runtime | R-TEST-09 differential adjudication | §02 | S-02 |
| R-CORE-12 | Fault totality on machine paths: panic-free non-test code, failures map to declared Fault (InternalInvariant family); transition atomicity — complete or fault, no died-mid-transition; durable append precedes in-memory mutation; clippy unwrap/expect denial (C-83 resolved; M034) | addendum (SEC-020) | SPECIFIED | all machine crates | M034, panic-catching fuzz harness | §02 | S-02 |
| R-CORE-13 | Closed declared fault surface on every trust-boundary crossing: six replay-path variants, StalePlan, unified MarshalFault, InternalInvariant declared; no debug-formatted external error text in machine values; resume-vs-fault pinned per variant (C-91 resolved) | addendum (SEC-012) | SPECIFIED | all machine crates | fault-coverage lint, differential fault matrix | §02 | S-02 |
| R-CORE-14 | Canonical request protocol and transaction boundary: master-prompt 16-step order governs, turn-[21] host-before-Issued order superseded; step-10 premise `t + δ_t(req) ≤ W`; steps 12–14b one atomic section (C-103/C-104 resolved) | addendum (request-pipeline) | SPECIFIED | ror-runtime | M037/M038, gate short-circuit matrix | §02 | S-02 |
| R-TRUST-01 | Trust table (LLM/Block No; host Partial; rest Yes) | L41823–41841, L27611–27624 | SPECIFIED | — | — | §03 | S-03 |
| R-TRUST-02 | TCB composition; LLM output ∉ TCB authority | L28178–28230 | SPECIFIED | — | — | §03 | S-03 |
| R-TRUST-03 | No hidden authority; evaluator sees refs only | L37722–37748, L19153–19175 | SPECIFIED | ror-kernel, ror-runtime | Track B (mock kernel), visibility checks | §03 | S-03 |
| R-TRUST-04 | One complete trust table: MOD-06/08/10 rows frozen (authoritative machine boundary); 11-row table superseded; planner never a security/runtime provider — prohibitions homed at enforcing modules; dep/ SC-1/2/3 hard failures (C-84 resolved) | addendum (SEC-022) | SPECIFIED | — | dep/ regeneration with SC-1/2/3 hard-gated | §03 | S-03 |
| R-TRUST-05 | Crate DAG carries the R-DUR-02 hinge edge ror-runtime → ror-persistence (inverted trait superseded); ror-core → ror-kernel forbidden; forbidden-edge list checked against Cargo.toml; crate-separation rule (C-85 resolved) | addendum (SEC-022) | SPECIFIED | ror-runtime, ror-persistence | Cargo.toml DAG mechanical check | §03 | S-03 |
| R-ARCH-01 | End-to-end pipeline (16 stages, LLM→host) | L37750–37780, L27287–27310 | SPECIFIED | ror-agent, ror-compiler, ror-runtime | — | §02 | S-04 |
| R-ARCH-02 | Independent verification architecture | L41406–41424 | SPECIFIED | ror-differential | R-REF-01 | §02 | S-04 |
| R-ARCH-03 | Block has no path into step(); plan constructors private | L9086–9097, L39296–39318 | SPECIFIED | ror-compiler, ror-runtime | R-ORDER-03 (first security gate) | §02 | S-04 |
| R-ARCH-04 | Dependency direction (algebra→kernel→plan→actor→global→scheduler→host) | L9059–9085 | SPECIFIED | all | Cargo dependency review | §02 | S-04 |
| R-ARCH-05 | Isolation posture decided: ladder retired — in-process structural isolation is the frozen minimum with residual risk (host compromise = machine compromise) recorded; out-of-process host adapter (canonical-bytes effects/receipts) required where host not fully trusted; in-process executor testkit-only (C-93 resolved) | addendum (SEC-013) | SPECIFIED | ror-host | dependency/visibility hard gate; dual-host-mode differential | §02 | S-04 |
| R-PLANNER-01 | PlanProposal {observation_sequence, block, metadata}; LLMOutput ∈ Data | L27176–27198 | SPECIFIED | ror-agent | — | §16 | S-05 |
| R-PLANNER-02 | Planner cannot allocate/authorize/modify/invoke/bypass | L27271–27285, L37781–37790 | SPECIFIED | ror-agent | R-PLANNER-05(1) | §16 | S-05 |
| R-PLANNER-03 | Staleness check; StalePlan rejection, no state mutation | L27199–27236, L28373 | SPECIFIED | ror-agent, ror-runtime | R-PLANNER-05(2) | §16 | S-05 |
| R-PLANNER-04 | Planner need not be deterministic; PlannerAccepted recording for replay | L27392–27414 | SPECIFIED | ror-agent | R-PLANNER-05(3) | §16 | S-05 |
| R-PLANNER-05 | LLM outer-loop conformance (3 test obligations) | L27920–27931, L28513–28521 | SPECIFIED | ror-agent, ror-testkit | 15E suite | §16 | S-05 |
| R-PLANNER-06 | Staleness is exact equality: observation_sequence = current_planning_epoch; either-direction mismatch ⇒ StalePlan with zero state mutation; less-than-only reading superseded; future-tagged proposals mandatory rejection test (C-86 resolved; M026) | addendum (SEC-007) | SPECIFIED | ror-agent, ror-runtime | M026, epoch-boundary conformance | §16 | S-05 |
| R-PLANNER-07 | Observation channel capability-opaque: CapabilitySummary frozen as non-referential projection (counts, classes, ceilings); EffectIssued carries {id, actor, digest} only, cap-bearing log shape superseded; Capability ∉ Observables(LLM) (C-87 resolved; M027) | addendum (SEC-008) | SPECIFIED | ror-agent | M027, observation-opacity property | §16 | S-05 |
| R-COMPILE-01 | Block ≠ ExecutablePlan | L41440–41452, L3834–3838 | SPECIFIED | ror-compiler | R-ORDER-03 | §05 | S-06 |
| R-COMPILE-02 | Pipeline stages; any failure ⇒ fault, no bypass | L39253–39267 | SPECIFIED | ror-compiler | malformed-Block rejection | §05 | S-06 |
| R-COMPILE-03 | Combined static judgment (type, effects, capability req, budget bound) | L3874–3905 | SPECIFIED | ror-compiler | U-22 (J2 re-spec gap) | §05 | S-06 |
| R-COMPILE-04 | Plan immutability / temporal integrity | L1722–1745, L2052–2070 | SPECIFIED | ror-compiler | — | §05 | S-06 |
| R-COMPILE-05 | ExecutablePlan constructors private to compiler | L39296–39318 | SPECIFIED | ror-compiler | visibility review | §05 | S-06 |
| R-COMPILE-06 | Embedded Value::Capability literals must be plan-bound: foreign/garbage/undeclared capability literal is a compilation fault (U-22 security-direction closure) | addendum (SEC-002) | SPECIFIED | ror-compiler | compiler conformance: embedded-literal battery | §05 | S-06 |
| R-CALC-01 | Machine Value domain (11 variants); Capability is opaque data | L12290–12312 | SPECIFIED | ror-core | — | §04 | S-07 |
| R-CALC-02 | Frozen Expr AST (12 constructors, declarative only) | L12132–12170 | SPECIFIED | ror-core | — | §04 | S-07 |
| R-CALC-03 | Symbol(u32) runtime identity; compiler maps names | L12250–12270 | SPECIFIED | ror-core, ror-compiler | — | §04 | S-07 |
| R-CALC-04 | Effect = immutable data; EffectDigest = SHA-256(canonical); ID vs digest roles | L9288–9348, L23726–23772 | SPECIFIED | ror-core | EFFECT-RECEIPT-DIGEST-VALIDATION | §04 | S-07 |
| R-CALC-05 | EffectCost {issue, complete_max, reserve} | L25799–25825 | SPECIFIED | ror-core | R-EFFECT-05 | §04 | S-07 |
| R-CALC-06 | Frozen Fault taxonomy | L23784–23819, L27236 | SPECIFIED | ror-core | fault-coverage metric | §04 | S-07 |
| R-CALC-07 | Effect replayability/reversibility/idempotence (properties; table illustrative) | L2141–2156, L3858–3873, L26669–26735 | SPECIFIED | ror-core | U-06 | §04 | S-07 |
| R-CALC-08 | Σ and G configurations; global vs local state split | L7119–7144, L8653–8682, L24148–24163 | SPECIFIED | ror-core, ror-runtime | — | §04 | S-07 |
| R-CEK-01 | Explicit CEK; no recursive evaluation | L41484–41499, L37800–37812 | SPECIFIED | ror-runtime | deep-call stress, R-TEST-01 | §08 | S-08 |
| R-CEK-02 | Value-return invariant (terminal iff continuation empty) | L16878–16905, L37826–37838 | SPECIFIED | ror-runtime, ror-reference | push/pop structural invariants (L14632) | §08 | S-08 |
| R-CEK-03 | Frozen frame set; closure env ≠ caller env | L16928–16958, L23821–23856 | SPECIFIED | ror-runtime | CEK-CLOSURE-LEXICAL-CAPTURE | §08 | S-08 |
| R-CEK-04 | Lambda: lexical capture, pure, value-return path | L16971–16995 | SPECIFIED | ror-runtime | CEK-CLOSURE-LEXICAL-CAPTURE | §08 | S-08 |
| R-CEK-05 | Call: LTR evaluation; arity precheck before args; closure-env application | L16878–16905, L37840–37862 | SPECIFIED | ror-runtime | CEK-CALL-ARITY-PRECHECK, CEK-CALL-ARGS-LTR, M001, M002, M003 | §08 | S-08 |
| R-CEK-06 | Continuation preservation (+1/−1 per entry/resume) | L14632–14642 | SPECIFIED | ror-runtime | structural invariant tests | §08 | S-08 |
| R-CEK-07 | Progress & preservation | L7273–7277, L8850 | SPECIFIED | ror-runtime | differential equivalence | §08 | S-08 |
| R-CAP-01 | Five semantic domains (O, S, Q, R, T) with orders/meets | L6354–6379 | SPECIFIED | ror-core, ror-kernel | algebra property tests | §06 | S-09 |
| R-CAP-02 | Operation-indexed authority | L6370–6380 | SPECIFIED | ror-kernel | cross-op contamination tests | §06 | S-09 |
| R-CAP-03 | Authority partial order ≼ | L6381–6390 | SPECIFIED | ror-kernel | monotonicity property | §06 | S-09 |
| R-CAP-04 | Constraint ≠ Authority (narrowing request) | L6391–6396, L6406 | SPECIFIED | ror-core, ror-kernel | — | §06 | S-09 |
| R-CAP-05 | derive = per-op meet; derive(A,C) ≼ A | L6397–6404 | SPECIFIED | ror-kernel | CAP-DERIVE-NO-AMPLIFICATION, M006 | §06 | S-09 |
| R-CAP-06 | Canonical Authorized(A,E,t) predicate (5 conjuncts) | L6406–6421, L6647–6656 | SPECIFIED | ror-kernel | Track B mock-kernel tests | §06 | S-09 |
| R-CAP-07 | Valid(c,t) incl. ancestor liveness; lazy revocation | L6434–6445, L6647–6656 | SPECIFIED | ror-kernel | CAP-REVOCATION-ANCESTOR, M004 | §06 | S-09 |
| R-CAP-08 | Algebra theorems 1–3 (stated, proof-sketch only) | L6422–6433, L6657–6671 | SPECIFIED | ror-kernel | property tests (NOT PROVEN) | §06 | S-09 |
| R-CAP-09 | Explicit logical time; no wall-clock | L6434–6436, L38858–38890 | SPECIFIED | ror-core, ror-runtime | determinism tests | §06 | S-09 |
| R-CAP-10 | AdmissibleConstraint defined: decidable well-formedness per semantic domain (O/S/Q/R/T); inadmissible constraint faults (InvalidConstraint), never identity/top-default; compile-time validation of attacker-authored constraints (C-94 resolved; M030) | addendum (SEC-014) | SPECIFIED | ror-kernel, ror-compiler | M030, compiler negative suite | §06 | S-09 |
| R-CAP-11 | Lifetime is logical time: half-open `[start, end)` validity, call sites pass logical time, five Unix annotations superseded-quoted; `max_duration` declared-info only; `Deadline` stays `Option<LogicalTime>` (C-100 resolved; U-36) | addendum (duration-semantics) | SPECIFIED | ror-core, ror-kernel | M4 expiration/authorization gate tests | §06 | S-09 |
| R-KERN-01 | CapRef opaque, generation-safe, private fields, kernel-only construction | L9127–9133, L10178–10208 | SPECIFIED | ror-core, ror-kernel | visibility review | §06 | S-10 |
| R-KERN-02 | Kernel API: authorize/derive/validate with logical time | L6672–6728, L19153–19175 | SPECIFIED | ror-kernel | exactly-one-call mock tests | §06 | S-10 |
| R-KERN-03 | Authority internals pub(crate)/inaccessible | L39397–39407 | SPECIFIED | ror-kernel | visibility + mutation M005-class | §06 | S-10 |
| R-KERN-04 | Possession-gated authorization: authorize(holder, cap, effect, t) resolves the CapRef through the actor capability context; global-arena no-holder authorize superseded; CapRef bits never suffice (C-77 resolved) | addendum (SEC-002) | SPECIFIED | ror-kernel | M021, brute-force CapRef exhaustion from a non-holder | §06 | S-10 |
| R-KERN-05 | CapabilityContext real frozen possession type; unit-type sketch superseded; snapshots carry capability context; recovery reconstructs possession before gate authorization | addendum (SEC-002) | SPECIFIED | ror-kernel, ror-persistence | snapshot/recovery round-trip of possession sets | §06 | S-10 |
| R-KERN-06 | Root-grant protocol frozen: Grant(source, authority, ceiling, t) with durable CapabilityGranted record, authority ≼ deployment ceiling, root minted once at initialization; Supervisor.host removed or issued-effect-only (R-HOST-02 binds all callers); planner I/O crate-separated (C-95 resolved) | addendum (SEC-015) | SPECIFIED | ror-kernel, ror-agent | PanicHost-wraps-all-handles conformance; grant audit test | §06 | S-10 |
| R-BUDGET-01 | B = ⟨C=⟨F,I,D⟩, R=⟨M,S⟩, W⟩ semantics | L8683–8700, L9161–9175 | SPECIFIED | ror-core | U-01 (D semantics) | §07 | S-11 |
| R-BUDGET-02 | Checked arithmetic; no saturating_sub | L9207–9245, L38044–38046 | SPECIFIED | ror-core | M007, M009 | §07 | S-11 |
| R-BUDGET-03 | ReserveOK / ReleaseOK predicates | L7487–7520, L8692–8696 | SPECIFIED | ror-core | reservation property tests | §07 | S-11 |
| R-BUDGET-04 | WithinBudget dual gate (runtime + capability ceiling) | L8692–8696 | SPECIFIED | ror-runtime, ror-kernel | short-circuit Track C | §07 | S-11 |
| R-BUDGET-05 | Conservation (consumables, reserved, deadline, global partition) | L7408–7425, L28203–28240, L35210–35215 | SPECIFIED | ror-core, ror-runtime | BUDGET-*-CONSERVATION tags, teleportation test | §07 | S-11 |
| R-BUDGET-06 | Time advancement δ_t (pure=0, host/scheduler>0, t+δ_t ≤ W) | L8698–8700, L10164–10168 | SPECIFIED | ror-runtime | U-07 | §07 | S-11 |
| R-BUDGET-07 | CostModel contract; Consumable ≠ Reserved typing | L9155–9205, L10171–10177 | SPECIFIED | ror-core | — | §07 | S-11 |
| R-BUDGET-08 | ¬BudgetOK ⇒ fault(BudgetExhausted), no partial debit | L7345–7352, L7410–7419 | SPECIFIED | ror-runtime | Track C budget-gate test | §07 | S-11 |
| R-BUDGET-09 | Escrow disposition totality: every escrowed unit leaves via exactly one frozen path (Completed / host-failure consumption / durable Reconciled); live faults unified with crash reconciliation; logical-time deadline bound to Indeterminate; no quiescent strand (C-97 resolved; M035) | addendum (SEC-021) | SPECIFIED | ror-runtime, ror-persistence | M035, ledger liveness, mixed crash+live harness | §07 | S-11 |
| R-BUDGET-10 | Resource-state atomicity: every Op transition is one transactional resource mutation; precondition failure ⇒ `Σ' = Σ` (zero drift, zero partial debit); post-issuance host-failure caveat (C-108 resolved; U-45) | addendum (resource-accounting) | SPECIFIED | ror-runtime, ror-persistence | Op-01…Op-22 atomicity harness (conservation checker) | §07 | S-11 |
| R-BUDGET-11 | Escrow disposition normal form (RECONCILED): R-BUDGET-09's three paths are the totality; Consumed/Refunded are its completion leaves, Transferred/Disposed-with-explicit-sink its reconciled leaves; `Remains-Indeterminate` is a bounded transient, never terminal (C-108 resolved; U-45) | addendum (resource-accounting) | SPECIFIED | ror-runtime (classification), ror-persistence (records) | M039, ledger liveness, T0–T6 | §07 | S-11 |
| R-BUDGET-13 | Persistent-capacity accounting: volatile RAM distinct from persistent storage; RAM released on scope exit/halt; durable storage retained and snapshot-compacted; overflow faults (C-108 resolved; U-45) | addendum (resource-accounting) | SPECIFIED | ror-persistence | M7 snapshot-capacity tests | §07 | S-11 |
| R-BUDGET-15 | Duration consumable semantics: per-actor D; `ΔD := δ_t` exactly once per time advance; no double charge (`cost_C(E)` duration declared/diagnostic only); `δ_t > D` ⇒ `DeadlineExceeded` zero-mutation; precedence `CapabilityViolation → BudgetExhausted → DeadlineExceeded → HostPolicyDenied` (C-114/C-115 resolved; U-01/U-07) | addendum (duration-semantics) | SPECIFIED | ror-core, ror-runtime | M042, budget-gate tests | §07 | S-11 |
| R-BUDGET-16 | Exhaustive δ_t table (pure 0; issuance +1; receipt +1; spawn/send/receive/blocked 0; turn carries the executed δ_t; per host round trip = 2; reconciliation 0); Pending W-eligibility on each advance; late receipts settle via R-RECOV-08 (`t+δ_t ≤ W` superseded-quoted); stable quiescence `Deadlock ∧ ∃Pending` ⇒ driver `QuiescenceReconcile` δ_t=0/ΔD=0, each pending → `Indeterminate` + R-RECOV-08 (C-112/C-113 resolved; U-01/U-07) | addendum (duration-semantics) | SPECIFIED | ror-runtime | M040, M041, QUIESCENCE-RECONCILES-PENDING, ledger liveness | §07 | S-11 |
| R-EFFECT-01 | Request = construct→authorize→account→log→Pending→yield | L12177–12194 | SPECIFIED | ror-runtime | — | §11 | S-12 |
| R-EFFECT-02 | Gated transition shape Pre∧BudgetOKAuthOK | L7145–7155, L8700–8710 | SPECIFIED | ror-runtime | — | §11 | S-12 |
| R-EFFECT-03 | Frozen 16-step request sequence | L37891–37908 | SPECIFIED | ror-runtime, ror-persistence | gate short-circuit matrix | §11 | S-12 |
| R-EFFECT-04 | Denial short-circuits all subsequent gates | L24003–24045 | SPECIFIED | ror-runtime | Track C (5 assertions per gate) | §11 | S-12 |
| R-EFFECT-05 | complete_max affordability at issuance | L25799–25825 | SPECIFIED | ror-runtime | budget escrow tests | §11 | S-12 |
| R-EFFECT-06 | Receipt validates ID + digest; mismatch ⇒ ReplayCorruption, no resume | L23949–24002, L25952–25970 | SPECIFIED | ror-runtime | EFFECT-RECEIPT-DIGEST-VALIDATION, M017, M018 | §11 | S-12 |
| R-EFFECT-07 | Completion accounting (charge complete, release reservation, log, resume) | L23949–24002 | SPECIFIED | ror-runtime | conservation tests | §11 | S-12 |
| R-EFFECT-08 | Receipt-result admission: recursive contains_capability over the result payload at any nesting depth; no capability, no closure; data-domain only; host error via declared closed fault mapping only | addendum (SEC-001) | SPECIFIED | ror-runtime | EFFECT-RECEIPT-RESULT-NO-AUTHORITY, M019, M020 | §11 | S-12 |
| R-DUR-01 | HostInvoked ⇒ DurableIssued | L35150–35156, L37910 | SPECIFIED | ror-runtime, ror-persistence | EFFECT-ISSUE-DURABLE-BEFORE-HOST | §11 | S-13 |
| R-DUR-02 | Issuance transaction order (7 steps, 2 fsyncs) | L35150–35158 | SPECIFIED | ror-persistence | crash harness T0–T4 | §11 | S-13 |
| R-DUR-03 | Causal effect protocol (Issued⇒Prepared; Completed⇒Issued; Reconciled⇒Issued; ID+digest identity) | L35111–35144, L37953–37965 | SPECIFIED | ror-persistence | journal validator, M017 | §11 | S-13 |
| R-DUR-04 | Prepared∧¬Issued⇒Discard; Issued∧¬Completed⇒Indeterminate (never NotExecuted) | L35159–35176, L37968–37981 | SPECIFIED | ror-persistence | RECOVERY-ISSUED-INDETERMINATE, crash harness | §11 | S-13 |
| R-DUR-05 | Escrow survives crash | L35210–35215 | SPECIFIED | ror-persistence | post-recovery invariant check, M008 | §11 | S-13 |
| R-DUR-06 | Durable issuance payload: `Prepared`/`Issued` carry `effect_bytes` + `EffectCost` triple; `{id, actor, digest}` superseded as persistence payload; digest re-verified at append/recovery (C-105 resolved) | addendum (request-pipeline) | SPECIFIED | ror-persistence | M038, T1/T2–T5 reconstruction harness | §11 | S-13 |
| R-DUR-07 | Live issuance failure: journal-driven commit; declared `Fault::PersistenceError`; append/sync error ⇒ pre-s12 state and R-EFFECT-04 five assertions; second-sync failure ⇒ `Prepared ∧ ¬Issued ⇒ Discard` (C-106 resolved) | addendum (request-pipeline) | SPECIFIED | ror-runtime, ror-persistence | M037, live-fault harness, T0–T1 | §11 | S-13 |
| R-HOST-01 | Host independently validates OS authority (defense in depth) | L8560–8580, L10168–10172 | SPECIFIED | ror-host | host policy tests | §12 | S-14 |
| R-HOST-02 | Host performs only issued effects; partially trusted | L41823–41841, L27644 | SPECIFIED | ror-host | PanicHost harness | §12 | S-14 |
| R-HOST-03 | Ordered ReplayHost; ID+digest per entry; no unordered map | L25972–25996, L37985–38000 | SPECIFIED | ror-host, ror-reference | replay property tests | §12 | S-14 |
| R-HOST-04 | Replay correspondence (machine replay valid; real-world replay per effect class) | L3947–3958, L26249–26262 | SPECIFIED | ror-host, ror-reference | R-REF-01 recovery equivalence | §12 | S-14 |
| R-HOST-05 | Replay validates trace, not just final state | L38278–38300 | SPECIFIED | ror-host | trace comparison | §12 | S-14 |
| R-HOST-06 | Durable receipt results representable: EffectCompleted {id, digest, result_digest, result: CanonicalData}; replay verifies ResultDigest(result) = result_digest before resumption — third identity conjunct; no ad-hoc result records (C-90 resolved; M029) | addendum (SEC-011) | SPECIFIED | ror-persistence, ror-runtime | M029, T5 byte-exact resumption | §12 | S-14 |
| R-ACTOR-01 | Actor isolation (heaps, envs, continuations, mailboxes, budgets, caps) | L41623–41641, L24268–24290 | SPECIFIED | ror-runtime | Track D, isolation properties | §09 | S-15 |
| R-ACTOR-02 | GlobalState shape; logical time global | L24148–24163, L25514–25546 | SPECIFIED | ror-runtime | — | §09 | S-15 |
| R-ACTOR-03 | Deterministic ID allocation; no address/PID/UUID/wall-clock identity | L24226–24245 | SPECIFIED | ror-runtime | determinism tests | §09 | S-15 |
| R-ACTOR-04 | FIFO scheduler; at-most-once membership; 1 transition/turn; blocked/pending/terminal never scheduled | L25558–25615, L37924–37937 | SPECIFIED | ror-runtime | SCHED-FIFO, SCHED-BLOCKED-NOT-SCHEDULED, M011, M012, M013, starvation test | §10 | S-15 |
| R-ACTOR-05 | Spawn: escrow + derived capabilities only; no wholesale clone | L25573–25615, L37941–37951 | SPECIFIED | ror-runtime, ror-kernel | Track D, amplification test, U-03 | §09 | S-15 |
| R-ACTOR-06 | Send async + deterministic wakeup; Receive blocks without fuel; FIFO mailbox | L25702–25749, L37941–37951 | SPECIFIED | ror-runtime | Track D, M013 | §09 | S-15 |
| R-ACTOR-07 | Deterministic concurrency theorem | L25759–25766 | SPECIFIED | ror-runtime | global differential (Track D) | §10 | S-15 |
| R-ACTOR-08 | No amplification / no teleportation theorems | L26048–26070 | SPECIFIED | ror-runtime | teleportation test, amplification test | §09 | S-15 |
| R-ACTOR-09 | Spawn transfers no capabilities by default (delegation is the only default path); explicit manifest + constraint compiler-checked, strictly attenuated; Authority(child) ≺ parent; trust_level phantom retracted; BudgetAllocationSpec bounds (C-82 resolved; M025) | addendum (SEC-006) | SPECIFIED | ror-runtime, ror-kernel | M025, spawn fan-out amplification tests | §09 | S-15 |
| R-ACTOR-10 | Mailbox resource admission: enqueue requires recipient capacity (M reservation; ReservedCapacityExceeded faults the sender, sender pays); payload-proportional send cost over canonical length; constructed value size bounded against constructor's M; footprint bounded by reserved M (C-96 resolved; M033) | addendum (SEC-019) | SPECIFIED | ror-runtime | M033, sender-flood stress, footprint-bounded property | §09 | S-15 |
| R-MARSHAL-01 | Recursive capability rejection in ordinary marshal | L41647–41658, L25674–25701, L37946–37951 | SPECIFIED | ror-runtime | MARSHAL-NO-RAW-CAPABILITY | §13 | S-16 |
| R-MARSHAL-02 | Explicit delegation only; DelegatedCapability envelope; ≼ parent | L25972–26001, L37953–37959 | SPECIFIED | ror-runtime, ror-kernel | Track C (delegation) | §13 | S-16 |
| R-MARSHAL-03 | MarshalledValue = canonical bytes; unmarshal(marshal(v)) = v | L25674–25701 | SPECIFIED | ror-runtime | Track B (marshalling) | §13 | S-16 |
| R-MARSHAL-04 | Semantic marshalling rule (CapRef ∉ marshal(v)) | L8695–8698 | SPECIFIED | ror-runtime | Track B | §13 | S-16 |
| R-MARSHAL-05 | Delegation constructible: Expr::Delegate calls kernel.derive and yields a kernel-constructed envelope, never a plain Value variant; receive-side revalidation (liveness, lineage, target, generation) before registration, faults leave the recipient CapabilityContext byte-identical; MarshalledValue is the checked-bytes form; MarshalFault unified (X-65; C-79 resolved) | addendum (SEC-005) | SPECIFIED | ror-runtime, ror-kernel | M024, delegation negative suite | §13 | S-16 |
| R-MARSHAL-06 | contains_capability is a frozen total predicate: closed traversal domain descending into List, Map, Tuple at any depth and FunctionValue.env recursively; sole exclusion kernel-sealed delegation envelopes; Bytes are data; marshal Ok implies no reachable capability (C-81 resolved) | addendum (SEC-018) | SPECIFIED | ror-runtime | M032, closure-smuggling corpus | §13 | S-16 |
| R-CANON-01 | Serialization independent of Rust layout/serializers | L28185–28228, L28453–28465 | SPECIFIED | ror-core | format review | §13 | S-17 |
| R-CANON-02 | Universal envelope (version/tag/len/payload) | L30532–30543, L33290–33347 | SPECIFIED | ror-core | golden vectors | §13 | S-17 |
| R-CANON-03 | Frozen standalone type tags (0x00, 0x20, 0x30, 0x40, 0x41) | L33087–33154 | SPECIFIED | ror-core | golden vectors; C-02 | §13 | S-17 |
| R-CANON-04 | Value discriminants + nested-complete-envelope rule | L30544–30552, L33155–33265 | SPECIFIED | ror-core | golden vectors, round-trip | §13 | S-17 |
| R-CANON-05 | Primitive payloads (Symbol/CapRef/ActorId/EffectId) | L33087–33154 | SPECIFIED | ror-core | golden vectors | §13 | S-17 |
| R-CANON-06 | Collections: count-prefixed; maps semantically ordered; duplicate keys rejected | L30566–30573, L34987–35024, L38164–38172 | SPECIFIED | ror-core | M014, duplicate-key regression (ROR-011) | §13 | S-17 |
| R-CANON-07 | Strict decoder contract (5 checks; explicit discriminants; CanonicalError set) | L30575–30586, L32948–33049 | SPECIFIED | ror-core | malformed-input suite (ROR-010) | §13 | S-17 |
| R-CANON-08 | Checked arithmetic; no attacker preallocation; bounded nested cursors; fallible envelope | L30574–30578, L32948–33265 | SPECIFIED | ror-core | hostile-input property tests | §13 | S-17 |
| R-CANON-09 | Digest rules + when-to-compare-bytes rule | L28185–28228, L30588–30590 | SPECIFIED | ror-core | digest property tests | §13 | S-17 |
| R-CANON-10 | Injectivity as structural property + scoped evidence claim | L30592–30598, L35068 | SPECIFIED | ror-core | round-trip + differential | §13 | S-17 |
| R-CANON-11 | Golden vectors as normative fixtures | L30599–30646, L31948–32010, L33266–33286 | SPECIFIED | ror-core (vectors/) | M1 acceptance | §13 | S-17 |
| R-CANON-12 | Data decoder rejects capability payloads: 0x05 and standalone 0x30 yield CanonicalError::CapabilityInData; only the kernel-mediated codec path produces or consumes capability payloads; unmarshal runs contains_capability — symmetric boundary (C-14/U-02 security direction; C-78 resolved) | addendum (SEC-003) | SPECIFIED | ror-core | M022, negative golden vectors | §13 | S-17 |
| R-CANON-13 | One canonical grammar: 15A BE envelope sole; LE revised grammar superseded in-source; single TAG_* namespace (X-50/X-54 resolved); all digests defined over 15A; bidirectional byte-exact golden vectors; LE variants rejected (C-92 resolved; M031) | addendum (SEC-017) | SPECIFIED | ror-core | M031, bidirectional golden vectors | §13 | S-17 |
| R-PERSIST-01 | Persistence = recording, not a semantic machine; no secondary serialization | L33757–33790, L35078–35087 | SPECIFIED | ror-persistence | dependency review (15B acceptance matrix) | §14 | S-18 |
| R-PERSIST-02 | Two-level framing; WalFrame checksum; 8 rejection classes | L33802–33830, L35088–35110 | SPECIFIED | ror-persistence | negative parsing tests, M016 | §14 | S-18 |
| R-PERSIST-03 | Record taxonomy; EventEnvelope monotonic sequence | L33861–33900, L35111–35144 | SPECIFIED | ror-persistence | sequence property | §14 | S-18 |
| R-PERSIST-04 | Snapshot content (include/exclude lists) | L26293–26330 | SPECIFIED | ror-persistence | snapshot review, U-02 | §14 | S-18 |
| R-PERSIST-05 | Atomic snapshot protocol; ValidSnapshot iff commit+digest | L26216–26240, L35177–35188 | SPECIFIED | ror-persistence | SNAPSHOT-COMMIT-INTEGRITY, crash harness T6 | §14 | S-18 |
| R-PERSIST-06 | WAL sequence continuity; gaps rejected | L35088–35110, L35189–35208 | SPECIFIED | ror-persistence | WAL-SEQUENCE-CONTINUITY, WAL-GAP-REJECT, M015 | §14 | S-18 |
| R-PERSIST-07 | Durable authority lattice: snapshot carries the AuthorityNode set, revocation_set and generation counters; WAL event kinds CapabilityGranted/Derived/Revoked; recovery reconstructs the arena, replays capability events, faults on dangling or generation-mismatched CapRef; revocation monotonic across crashes (RECOVERY-REVOCATION-DURABLE) | addendum (SEC-004) | SPECIFIED | ror-persistence, ror-kernel | RECOVERY-REVOCATION-DURABLE, M023, crash matrix T0–T6 with pre-crash revocation | §14 | S-18 |
| R-PERSIST-08 | Storage integrity rewinding resistance: chained checksums (checksum_n = H(checksum_{n−1} ‖ frame_n)); snapshot commit covers state digest + last WAL sequence; keyed chain if storage adversarial, else trust-table records the trusted-writable assumption; consistently-forged negative tests (C-88 resolved) | addendum (SEC-009) | SPECIFIED | ror-persistence | tamper-at-every-T matrix, forged-record negatives | §14 | S-18 |
| R-RECOV-01 | D = ⟨S,L,H⟩; Recover = Replay | L26122–26140 | SPECIFIED | ror-persistence | recovery differential | §15 | S-19 |
| R-RECOV-02 | Normative crash matrix T0–T6 | L35159–35176, L28467–28493 | SPECIFIED | ror-persistence | crash harness, M10 | §15 | S-19 |
| R-RECOV-03 | Recovery algorithm (12 steps) | L35189–35208, L26272–26300 | SPECIFIED | ror-persistence | recovery differential (R-REF-01) | §15 | S-19 |
| R-RECOV-04 | Independent recovery implementation | L35189–35195, L38858–38890 | SPECIFIED | ror-persistence, ror-reference | dependency review | §15 | S-19 |
| R-RECOV-05 | Invalid(D) ⇒ RecoveryFault; never silently repair | L35196–35208, L38254–38272 | SPECIFIED | ror-persistence | negative corruption tests | §15 | S-19 |
| R-RECOV-06 | Budget partition invariant survives crash | L35210–35215 | SPECIFIED | ror-persistence | post-recovery invariant | §15 | S-19 |
| R-RECOV-07 | Reconciliation is the only resolution path for Indeterminate | L35111–35144, L26249–26262 | SPECIFIED | ror-persistence, ror-host | U-15, reconciliation tests | §15 | S-19 |
| R-RECOV-08 | Reconciliation frozen: I2 holds on every host path incl. supervisor; never re-executes (idempotent query at most); compensations are ordinary gated requests; NotExecuted gated behind authoritative evidence; supervisor allocates lifecycle, not effects (C-89 resolved; M028) | addendum (SEC-010) | SPECIFIED | ror-agent (policy), ror-persistence (record contract) | M028, T2/T3/T4 admissibility table | §15 | S-19 |
| R-RECOV-09 | Recovery reconstruction authority: `next_effect_id` from max replayed `Issued`; no `SnapshotCommit` in s12–s14b (`RecoveryFault`); completion order append→sync→charge→resume (C-107/C-109 resolved) | addendum (request-pipeline) | SPECIFIED | ror-persistence, ror-reference | M10, crash matrix T4/T5, snapshot-cadence tests | §15 | S-19 |
| R-REF-01 | Observe_P = Observe_R (+ recovery equivalence); evidence, not proof | L35281–35310, L38935–38953 | SPECIFIED | ror-differential | the gate itself | §17 | S-20 |
| R-REF-02 | Independence boundary (10 forbidden production deps) | L35330–35375, L37696–37721 | SPECIFIED | ror-reference | dependency graph review | §17 | S-20 |
| R-REF-03 | Reference models all 12 semantic areas; clarity over speed | L41848–41866, L35281–35322, L35341 | SPECIFIED | ror-reference | — | §17 | S-20 |
| R-REF-04 | Reference non-goals | L35326–35339 | SPECIFIED | ror-reference | — | §17 | S-20 |
| R-REF-05 | Normalized observations; first divergence; no final-value-only comparison | L38420–38470 (§16), L41869–41906 | SPECIFIED | ror-differential | comparator review | §18 | S-20 |
| R-REF-06 | PanicHost / MockKernel boundary enforcement | L27891–27902 | SPECIFIED | ror-testkit | harness tests | §18 | S-20 |
| R-TEST-01 | Three execution modes + frozen baselines; time ≠ semantics | L38587–38715, L37251–37268 | SPECIFIED | tests/ | CI | §20 | S-21 |
| R-TEST-02 | Reproducible counterexample artifact (16 fields) | L38891–38920, L37293–37315 | SPECIFIED | ror-differential | artifact schema | §21 | S-21 |
| R-TEST-03 | Shrinking protocol (10 ordered priorities) | L38441–38463 | SPECIFIED | ror-differential | shrinking tests | §21 | S-21 |
| R-TEST-04 | Baseline mutation registry M001–M018; additive | L38473–38492 | SPECIFIED | mutations/ | registry review | §19 | S-21 |
| R-TEST-05 | 100% kill rate (non-equivalent); adjudication for equivalents | L38494–38500, L37390–37400 | SPECIFIED | — | M9 gate | §19 | S-21 |
| R-TEST-06 | Mutation validation (verification system tested) | L38515–38540 | SPECIFIED | ror-testkit | framework tests | §19 | S-21 |
| R-TEST-07 | Semantic coverage by obligation tags; metrics ≠ oracle | L38523–38560, L37402–37414 | SPECIFIED | ror-differential | coverage report | §18 | S-21 |
| R-TEST-08 | Crash-injection matrix T0–T6 | L38831–38846, L35216–35236 | SPECIFIED | ror-testkit | M10 gate | §18 | S-21 |
| R-TEST-09 | Fault adjudication (4-way classification) | L38848–38862, L37404–37414 | SPECIFIED | process | R-SCOPE-03 | §18 | S-21 |
| R-TEST-10 | CI gates (PR / nightly / release) | L38864–38890, L37287–37292 | SPECIFIED | CI | gates | §18 | S-21 |
| R-TEST-11 | Final acceptance condition (3 conjuncts) | L38885–38911, L41196–41210 | SPECIFIED | — | M11 | §18 | S-21 |
| R-TEST-12 | Request-frame verification tags: `REQUEST-ARGS-LTR` and `REQUEST-NON-CAP-SHORT-CIRCUIT` added to R-TEST-07's obligation-tagged coverage list; Track A coverage (U-44 resolved) | addendum (request-pipeline) | SPECIFIED | tests/ | Track A request suite | §18 | S-21 |
| R-REPO-01 | Workspace layout; boundaries frozen, names flexible | L39140–39195 | SPECIFIED | workspace | R-ARCH-02 | §02 | S-22 |
| R-REPO-02 | Ten crate contracts (contents + prohibitions) | L39196–40762 | SPECIFIED | crates/ | dependency + visibility review | §02 | S-22 |
| R-REPO-03 | Boundaries enforced structurally (deps, visibility, types, traits, tests) | L41223–41273 | SPECIFIED | workspace | mutation + differential | §02 | S-22 |
| R-ORDER-01 | 20-step implementation order; tests before dependents; reference early | L37793–37812, L42108–42142 | SPECIFIED | process | — | §27 | S-23 |
| R-ORDER-02 | M0–M11 acceptance criteria | L40763–41100, L42165–42190 | SPECIFIED | process | milestones | §27 | S-23 |
| R-ORDER-03 | First security gate (Block ⇏ ExecutablePlan; 7-form differential) | L41155–41195 | SPECIFIED | ror-compiler, ror-runtime | gate | §27 | S-23 |
| R-ORDER-04 | Sprint 1 task set ROR-001…ROR-016 | L41091–41112 | SPECIFIED | process | — | §27 | S-23 |
| R-ORDER-05 | Definition of done (7 components) | L41124–41142 | SPECIFIED | process | — | §27 | S-23 |
| R-CLAIM-01 | Scoped conformance claim (frozen wording) | L38913–38917, L42191–42265 | SPECIFIED | — | — | §28 | S-24 |
| R-CLAIM-02 | 16 prohibited shortcuts | L38858–38890, L42144–42188 | SPECIFIED | all | mutation + review | §28 | S-24 |
| R-CLAIM-03 | Engineering response format; CONFLICT reporting | L38808–38846 | SPECIFIED | process | — | §28 | S-24 |
| R-CLAIM-04 | Start condition (no new semantic phase; reference alongside) | L38921–38928 | SPECIFIED | process | — | §28 | S-24 |

## Per-area counts and atomic-record coverage

| Area | Registry rows | FINAL1 home section(s) |
|---|---|---|
| R-ACTOR | 10 | §09, §10 |
| R-ARCH | 5 | §02 |
| R-BUDGET | 14 | §07 |
| R-CALC | 8 | §04 |
| R-CANON | 13 | §13 |
| R-CAP | 11 | §06 |
| R-CEK | 7 | §08 |
| R-CLAIM | 4 | §28 |
| R-COMPILE | 6 | §05 |
| R-CORE | 14 | §02 |
| R-DUR | 7 | §11 |
| R-EFFECT | 8 | §11 |
| R-HOST | 6 | §12 |
| R-KERN | 6 | §06 |
| R-MARSHAL | 6 | §13 |
| R-ORDER | 5 | §27 |
| R-PERSIST | 8 | §14 |
| R-PLANNER | 7 | §16 |
| R-RECOV | 9 | §15 |
| R-REF | 6 | §17, §18 |
| R-REPO | 3 | §02 |
| R-SCOPE | 4 | §01 |
| R-TEST | 12 | §18, §19, §20, §21 |
| R-TRUST | 5 | §03 |

**Atomic record layer (`req/`, cleaned authority):** 545 records, EVIDENCE-STATUS distribution {'SPECIFIED': 545} — i.e. **every one SPECIFIED**; normative levels {'MUST': 368, 'IS': 50, 'MUST NOT': 96, 'MAY': 8, 'AMBIGUOUS': 8, 'NON-NORMATIVE': 4, 'SHOULD': 11}. Coverage: 148/148 frozen-source parent obligations; the 36 post-audit addendum obligations are registry rows in `spec/03`/this table **without** individual atomic records (the atomic layer was frozen at 148 coverage) — a recorded coverage boundary, not a defect to paper over.

Stale prose counts observed inside `req/README.md` / `req/04-verification-undefined.md` (e.g. "all 497 registry records", "8 records" vs 9 VU rows) are recorded in `final/09` §C as register staleness in the inputs; this file's counts are computed from `req/registry.json` directly.
