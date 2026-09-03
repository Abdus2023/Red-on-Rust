# mod/18 — Obligation Ownership Matrix (GENERATED — do not edit; edit `mod/_ownership.py` and run `python3 mod/_build.py --write`)

Total, duplicate-free partition of the 148 canonical obligations (`spec/03`) and of the
545 atomic records (`req/`) over the 17 semantic modules, per the ownership rules in
`mod/00-overview.md` §2. Every obligation below is `SPECIFIED` (status ladder `spec/00` §2).
Cross-reference column lists other modules the obligation binds (reasons abbreviated;
full cross-reference prose lives in the module files' CROSS-REFERENCES sections).
The provenance column quotes `spec/03` verbatim; where `req/00-method.md` §5.1 corrected
an anchor, the corrected range is carried in the owning module file's SOURCE-PROVENANCE.

## 0. Module dependency graph (structural; mirrors the frozen crate direction)

Edges below restate the frozen crate dependency direction (`spec/07` §6, R-REPO-02 /
R-ARCH-04) at module granularity: each edge is an existing architectural fact, not a
choice made by this split. Semantic couplings richer than crate edges live in the
module files' DEPENDENCIES/CROSS-REFERENCES prose. The graph is acyclic (checked by
`mod/_build.py`, Kahn's algorithm); intra-crate couplings never appear as edges:

- `ror-core` hosts MOD-01 CORE; MOD-04 BUDGET; MOD-10 SERIALIZATION (couplings inside the crate are cross-references, not module dependencies)
- `ror-runtime` hosts MOD-05 EVALUATOR; MOD-06 ACTOR; MOD-07 SCHEDULER; MOD-08 EFFECT (couplings inside the crate are cross-references, not module dependencies)
- `ror-persistence` hosts MOD-11 PERSISTENCE; MOD-12 RECOVERY (couplings inside the crate are cross-references, not module dependencies)

```
MOD-01 CORE + MOD-14 REFERENCE   (no module dependencies; REFERENCE is forbidden production deps by R-REF-02)
MOD-02 COMPILER     -> MOD-01 CORE           [crate] ror-compiler -> ror-core
MOD-03 CAPABILITY   -> MOD-01 CORE           [crate] ror-kernel -> ror-core
MOD-04 BUDGET       -> MOD-03 CAPABILITY     [crate] budget primitives co-located with ror-kernel; ceiling operand from the algebra
MOD-05 EVALUATOR    -> MOD-01 CORE           [crate] ror-runtime -> ror-core
MOD-05 EVALUATOR    -> MOD-03 CAPABILITY     [crate] ror-runtime -> ror-kernel (authorize/derive calls)
MOD-06 ACTOR        -> MOD-01 CORE           [crate] ror-runtime -> ror-core
MOD-06 ACTOR        -> MOD-03 CAPABILITY     [crate] ror-runtime -> ror-kernel (spawn/delegation derive)
MOD-07 SCHEDULER    -> MOD-01 CORE           [crate] ror-runtime -> ror-core
MOD-07 SCHEDULER    -> MOD-03 CAPABILITY     [crate] ror-runtime -> ror-kernel
MOD-08 EFFECT       -> MOD-01 CORE           [crate] ror-runtime -> ror-core
MOD-08 EFFECT       -> MOD-03 CAPABILITY     [crate] ror-runtime -> ror-kernel (gates 5..7)
MOD-08 EFFECT       -> MOD-11 PERSISTENCE    [crate] request step 14 calls ror-persistence append/sync
MOD-09 HOST         -> MOD-01 CORE           [crate] ror-host -> ror-core
MOD-09 HOST         -> MOD-08 EFFECT         [crate] ror-host -> ror-runtime (adapter boundary, spec/07 section 6)
MOD-11 PERSISTENCE  -> MOD-01 CORE           [crate] ror-persistence -> ror-core
MOD-12 RECOVERY     -> MOD-01 CORE           [crate] ror-persistence -> ror-core
MOD-12 RECOVERY     -> MOD-14 REFERENCE      [oracle] independent recovery oracle (R-RECOV-04, REQ-TEST-045) - not a crate edge
MOD-13 AGENT        -> MOD-01 CORE           [crate] ror-agent -> ror-core
MOD-13 AGENT        -> MOD-02 COMPILER       [crate] ror-agent -> ror-compiler
MOD-13 AGENT        -> MOD-05 EVALUATOR      [crate] ror-agent -> ror-runtime
MOD-15 DIFFERENTIAL -> MOD-14 REFERENCE      [crate] ror-differential -> ror-reference
MOD-15 DIFFERENTIAL -> MOD-05 EVALUATOR      [sut] ror-differential -> ror-runtime as black-box SUT
MOD-15 DIFFERENTIAL -> MOD-17 VERIFICATION   [crate] ror-differential -> ror-testkit
MOD-16 MUTATION     -> MOD-15 DIFFERENTIAL   [crate] kill evidence gathered through the differential harness
MOD-16 MUTATION     -> MOD-17 VERIFICATION   [crate] injection infrastructure in ror-testkit
MOD-17 VERIFICATION orchestrates all modules as SUT (tests/, scripts/); no producer dependencies.
```

## 1. Obligation partition (148)

### MOD-01 — CORE (32 obligations)

| Obligation | Short text (from `spec/03`) | Provenance | Cross-references | Duplication |
|---|---|---|---|---|
| R-ARCH-01 | End-to-end pipeline (16 stages, LLM→host) | L37750–37780, L27287–27310 | MOD-13 (stage 1), MOD-02 (compile stages), MOD-05 (CEK stage), MOD-08 (issuance stage), MOD-11 (durable stage), MOD-09 (host stage) | — |
| R-ARCH-02 | Independent verification architecture | L41406–41424 | MOD-14 (independent side), MOD-15 (comparison side) | — |
| R-ARCH-03 | Block has no path into step(); plan constructors private | L9086–9097, L39296–39318 | MOD-02 (operative owner (D-11)), MOD-05 (no Block path into step()) | D-11 (marked restatement — canonical statement R-COMPILE-01, MOD-02) |
| R-ARCH-04 | Dependency direction (algebra→kernel→plan→actor→global→scheduler→host) | L9059–9085 | MOD-17 (enforced via Cargo/visibility rules (R-REPO-03)) | — |
| R-ARCH-05 | Isolation posture decided: ladder retired — in-process structural isolation is the frozen minimum with residual risk (host compromise = machine compromise) recorded; out-of-process host adapter (canonical-bytes effects/receipts) required where host not fully trusted; in-process executor testkit-only (C-93 resolved) | addendum (SEC-013) | — | — |
| R-CALC-01 | Machine Value domain (11 variants); Capability is opaque data | L12290–12312 | MOD-05 (consumer of machine Value), MOD-10 (two Value domains collide - U-09) | — |
| R-CALC-02 | Frozen Expr AST (12 constructors, declarative only) | L12132–12170 | MOD-02 (input surface), MOD-05 (evaluated term), MOD-06 (Delegate constructor absent - U-02), MOD-17 (await retraction - U-04) | — |
| R-CALC-03 | Symbol(u32) runtime identity; compiler maps names | L12250–12270 | MOD-02 (name mapping built here), MOD-05 (symbols only) | — |
| R-CALC-04 | Effect = immutable data; EffectDigest = SHA-256(canonical); ID vs digest roles | L9288–9348, L23726–23772 | MOD-08 (descriptor used at gates), MOD-10 (digest bytes computed over canonical form), MOD-09 (receipt re-validation) | — |
| R-CALC-05 | EffectCost {issue, complete_max, reserve} | L25799–25825 | MOD-08 (issue/complete_max charging), MOD-04 (escrow accounting) | — |
| R-CALC-06 | Frozen Fault taxonomy | L23784–23819, L27236 | MOD-15 (faults compared in differential observation), MOD-12 (RecoveryFault variant), MOD-17 (variant enumeration open - U-08/U-14) | — |
| R-CALC-07 | Effect replayability/reversibility/idempotence (properties; table illustrative) | L2141–2156, L3858–3873, L26669–26735 | MOD-09 (replay classes), MOD-12 (recovery classification input), MOD-17 (property table non-normative - U-06) | — |
| R-CALC-08 | Σ and G configurations; global vs local state split | L7119–7144, L8653–8682, L24148–24163 | MOD-05 (local Sigma), MOD-06 (actor state / global state) | — |
| R-CORE-01 | LLMOutput ∧ UntrustedInput ↛ ExternalEffect | L41320–41335, L27505–27513 | MOD-13 (planner has no authority), MOD-02 (Block rejected at compiler boundary), MOD-08 (only validated plans reach effect gates) | — |
| R-CORE-02 | ExternalEffect chain (7 conjuncts) | L41337–41351, L27491–27509 | MOD-08 (7 conjuncts realized as gates 5..16 of the 16-step sequence (D-12)), MOD-03 (Authorized conjunct), MOD-04 (BudgetAvailable conjunct), MOD-09 (HostPolicyOK conjunct), MOD-11 (Issued conjunct (durable)) | D-12 (marked restatement — canonical statement R-EFFECT-03, MOD-08) |
| R-CORE-03 | ¬Authorized ⇒ ¬ExternalEffect | L42056–42064, L7413–7419 | MOD-03 (predicate owner (D-08)), MOD-08 (gate application) | D-08 (marked restatement — canonical statement R-CAP-06, MOD-03) |
| R-CORE-04 | derive(A,C) ≼ A (no amplification) | L42066–42072, L6399–6406 | MOD-03 (operative owner (D-01)), MOD-06 (cross-actor transfer still bounded by delegation) | D-01 (marked restatement — canonical statement R-CAP-05, MOD-03) |
| R-CORE-05 | Budget partition conservation (no teleportation) | L42074–42080, L28203–28240 | MOD-04 (operative owner (D-02)), MOD-12 (survives crash (R-RECOV-06)), MOD-06 (spawn transfer, not creation) | D-02 (marked restatement — canonical statement R-BUDGET-05, MOD-04) |
| R-CORE-06 | HostInvoked ⇒ DurableIssued | L42082–42088, L35150–35156 | MOD-11 (operative owner (D-03)), MOD-08 (sequence position (steps 14 before 16)), MOD-09 (host never invoked earlier) | D-03 (marked restatement — canonical statement R-DUR-01, MOD-11) |
| R-CORE-07 | Ordinary marshal rejects raw capabilities | L42090–42098, L25972–26001 | MOD-06 (operative owner (D-04)), MOD-03 (delegation is a kernel derive) | D-04 (marked restatement — canonical statement R-MARSHAL-01, MOD-06) |
| R-CORE-08 | Determinism: state+traces ⇒ unique machine trace | L41623–41646, L27518–27547 | MOD-07 (operative owner (D-05)), MOD-09 (host trace term), MOD-13 (planner trace for end-to-end runs) | D-05 (marked restatement — canonical statement R-ACTOR-07, MOD-07) |
| R-CORE-09 | Causal crash recovery (qualified theorem) | L27551–27569, L35159–35176 | MOD-12 (operative owner (D-06)), MOD-11 (journal classification protocol), MOD-09 (host reconciliation role) | D-06 (marked restatement — canonical statement R-RECOV-02, MOD-12) |
| R-CORE-10 | No silent recovery corruption | L42100–42105, L35196–35208 | MOD-12 (operative owner (D-07)), MOD-11 (rejection points that may raise it) | D-07 (marked restatement — canonical statement R-RECOV-05, MOD-12) |
| R-CORE-11 | One canonical signature per I2 predicate: ValidatedRequest(E) request-time subsuming ValidatedPlan(plan(E)); Authorized(holder, c, E, t) possession conjunct (formalizes R-KERN-04); ValidatedPlan_pred vs ValidatedPlan_struct; chain stated once (X-01/X-04/X-05; C-80 resolved) | addendum (SEC-016) | — | — |
| R-CORE-12 | Fault totality on machine paths: panic-free non-test code, failures map to declared Fault (InternalInvariant family); transition atomicity — complete or fault, no died-mid-transition; durable append precedes in-memory mutation; clippy unwrap/expect denial (C-83 resolved; M034) | addendum (SEC-020) | — | — |
| R-CORE-13 | Closed declared fault surface on every trust-boundary crossing: six replay-path variants, StalePlan, unified MarshalFault, InternalInvariant declared; no debug-formatted external error text in machine values; resume-vs-fault pinned per variant (C-91 resolved) | addendum (SEC-012) | — | — |
| R-SCOPE-01 | Thesis: deterministic, capability-scoped, resource-bounded, crash-recoverable machine | L41293–41300 | MOD-02 (capability-scoped), MOD-04 (resource-bounded), MOD-07 (deterministic), MOD-12 (crash-recoverable) | — |
| R-SCOPE-02 | Architecture/spec/verification FROZEN; frozen ≠ verified | L38929–38942, L41297–41315 | MOD-17 (status ladder enforced as evidence discipline) | — |
| R-TRUST-01 | Trust table (LLM/Block No; host Partial; rest Yes) | L41823–41841, L27611–27624 | MOD-17 (boundary enforcement review), MOD-09 (live host is the only Partial row) | — |
| R-TRUST-02 | TCB composition; LLM output ∉ TCB authority | L28178–28230 | MOD-05 (TCB member), MOD-03 (TCB member), MOD-04 (TCB member), MOD-07 (TCB member), MOD-10 (TCB member), MOD-11 (TCB member), MOD-13 (LLM output outside TCB) | — |
| R-TRUST-03 | No hidden authority; evaluator sees refs only | L37722–37748, L19153–19175 | MOD-03 (operative owner (D-09)), MOD-05 (evaluator must not inspect) | D-09 (marked restatement — canonical statement R-KERN-03, MOD-03) |
| R-TRUST-04 | One complete trust table: MOD-06/08/10 rows frozen (authoritative machine boundary); 11-row table superseded; planner never a security/runtime provider — prohibitions homed at enforcing modules; dep/ SC-1/2/3 hard failures (C-84 resolved) | addendum (SEC-022) | — | — |

### MOD-02 — COMPILER (6 obligations)

| Obligation | Short text (from `spec/03`) | Provenance | Cross-references | Duplication |
|---|---|---|---|---|
| R-COMPILE-01 | Block ≠ ExecutablePlan | L41440–41452, L3834–3838 | MOD-05 (runtime only receives ExecutablePlan), MOD-13 (proposal enters here) | D-11 (canonical statement) |
| R-COMPILE-02 | Pipeline stages; any failure ⇒ fault, no bypass | L39253–39267 | MOD-17 (open stage question - U-22) | — |
| R-COMPILE-03 | Combined static judgment (type, effects, capability req, budget bound) | L3874–3905 | MOD-04 (static bound B vs CostModel), MOD-03 (capability requirements descriptor) | — |
| R-COMPILE-04 | Plan immutability / temporal integrity | L1722–1745, L2052–2070 | MOD-13 (staleness + PlannerAccepted lifecycle), MOD-03 (authority fixed at t0) | — |
| R-COMPILE-05 | ExecutablePlan constructors private to compiler | L39296–39318 | MOD-17 (visibility review) | D-11 (marked restatement — canonical statement R-COMPILE-01, MOD-02) |
| R-COMPILE-06 | Embedded Value::Capability literals must be plan-bound: foreign/garbage/undeclared capability literal is a compilation fault (U-22 security-direction closure) | addendum (SEC-002) | — | — |

### MOD-03 — CAPABILITY (16 obligations)

| Obligation | Short text (from `spec/03`) | Provenance | Cross-references | Duplication |
|---|---|---|---|---|
| R-CAP-01 | Five semantic domains (O, S, Q, R, T) with orders/meets | L6354–6379 | — | — |
| R-CAP-02 | Operation-indexed authority | L6370–6380 | — | — |
| R-CAP-03 | Authority partial order ≼ | L6381–6390 | — | — |
| R-CAP-04 | Constraint ≠ Authority (narrowing request) | L6391–6396, L6406 | — | — |
| R-CAP-05 | derive = per-op meet; derive(A,C) ≼ A | L6397–6404 | MOD-01 (central restatement R-CORE-04 (D-01)), MOD-06 (spawn/delegation derive) | D-01 (canonical statement) |
| R-CAP-06 | Canonical Authorized(A,E,t) predicate (5 conjuncts) | L6406–6421, L6647–6656 | MOD-08 (gate 6 of 16), MOD-04 (ceiling conjunct cost <= R_A), MOD-01 (central restatement R-CORE-03 (D-08)) | D-08 (canonical statement) |
| R-CAP-07 | Valid(c,t) incl. ancestor liveness; lazy revocation | L6434–6445, L6647–6656 | MOD-06 (delegated envelopes keep lineage) | — |
| R-CAP-08 | Algebra theorems 1–3 (stated, proof-sketch only) | L6422–6433, L6657–6671 | — | — |
| R-CAP-09 | Explicit logical time; no wall-clock | L6434–6436, L38858–38890 | MOD-06 (logical time is global state), MOD-04 (deadline comparison), MOD-07 (scheduler steps advance t) | — |
| R-CAP-10 | AdmissibleConstraint defined: decidable well-formedness per semantic domain (O/S/Q/R/T); inadmissible constraint faults (InvalidConstraint), never identity/top-default; compile-time validation of attacker-authored constraints (C-94 resolved; M030) | addendum (SEC-014) | — | — |
| R-KERN-01 | CapRef opaque, generation-safe, private fields, kernel-only construction | L9127–9133, L10178–10208 | MOD-10 (CapRef payload 0x30), MOD-11 (capability contexts in snapshots), MOD-06 (marshal rejection target) | — |
| R-KERN-02 | Kernel API: authorize/derive/validate with logical time | L6672–6728, L19153–19175 | MOD-05 (evaluator calls authorize/derive), MOD-06 (spawn and delegation call derive) | — |
| R-KERN-03 | Authority internals pub(crate)/inaccessible | L39397–39407 | MOD-01 (central restatement R-TRUST-03 (D-09)), MOD-17 (visibility enforcement review) | D-09 (canonical statement) |
| R-KERN-04 | Possession-gated authorization: authorize(holder, cap, effect, t) resolves the CapRef through the actor capability context; global-arena no-holder authorize superseded; CapRef bits never suffice (C-77 resolved) | addendum (SEC-002) | — | — |
| R-KERN-05 | CapabilityContext real frozen possession type; unit-type sketch superseded; snapshots carry capability context; recovery reconstructs possession before gate authorization | addendum (SEC-002) | — | — |
| R-KERN-06 | Root-grant protocol frozen: Grant(source, authority, ceiling, t) with durable CapabilityGranted record, authority ≼ deployment ceiling, root minted once at initialization; Supervisor.host removed or issued-effect-only (R-HOST-02 binds all callers); planner I/O crate-separated (C-95 resolved) | addendum (SEC-015) | — | — |

### MOD-04 — BUDGET (9 obligations)

| Obligation | Short text (from `spec/03`) | Provenance | Cross-references | Duplication |
|---|---|---|---|---|
| R-BUDGET-01 | B = ⟨C=⟨F,I,D⟩, R=⟨M,S⟩, W⟩ semantics | L8683–8700, L9161–9175 | MOD-03 (capability ceiling R shares component-wise order), MOD-17 (D semantics open - U-01) | — |
| R-BUDGET-02 | Checked arithmetic; no saturating_sub | L9207–9245, L38044–38046 | — | — |
| R-BUDGET-03 | ReserveOK / ReleaseOK predicates | L7487–7520, L8692–8696 | — | — |
| R-BUDGET-04 | WithinBudget dual gate (runtime + capability ceiling) | L8692–8696 | MOD-03 (capability ceiling is the second gate), MOD-08 (gates 7..10 of 16) | — |
| R-BUDGET-05 | Conservation (consumables, reserved, deadline, global partition) | L7408–7425, L28203–28240, L35210–35215 | MOD-01 (central restatement R-CORE-05 (D-02)), MOD-06 (spawn transfer), MOD-08 (escrow at issuance), MOD-12 (survival after crash) | D-02 (canonical statement) |
| R-BUDGET-06 | Time advancement δ_t (pure=0, host/scheduler>0, t+δ_t ≤ W) | L8698–8700, L10164–10168 | MOD-07 (scheduler step delta positive), MOD-09 (host interaction delta positive), MOD-17 (per-transition deltas open - U-07) | — |
| R-BUDGET-07 | CostModel contract; Consumable ≠ Reserved typing | L9155–9205, L10171–10177 | MOD-02 (static budget bound uses CostModel), MOD-08 (EffectCost is a Cost) | — |
| R-BUDGET-08 | ¬BudgetOK ⇒ fault(BudgetExhausted), no partial debit | L7345–7352, L7410–7419 | MOD-08 (denial leaves budget unchanged) | — |
| R-BUDGET-09 | Escrow disposition totality: every escrowed unit leaves via exactly one frozen path (Completed / host-failure consumption / durable Reconciled); live faults unified with crash reconciliation; logical-time deadline bound to Indeterminate; no quiescent strand (C-97 resolved; M035) | addendum (SEC-021) | — | — |

### MOD-05 — EVALUATOR (7 obligations)

| Obligation | Short text (from `spec/03`) | Provenance | Cross-references | Duplication |
|---|---|---|---|---|
| R-CEK-01 | Explicit CEK; no recursive evaluation | L41484–41499, L37800–37812 | MOD-11 (continuation must be snapshot-serializable), MOD-17 (recursive evaluator prohibited (R-CLAIM-02)) | — |
| R-CEK-02 | Value-return invariant (terminal iff continuation empty) | L16878–16905, L37826–37838 | — | — |
| R-CEK-03 | Frozen frame set; closure env ≠ caller env | L16928–16958, L23821–23856 | MOD-11 (frames need canonical encoding - U-02) | — |
| R-CEK-04 | Lambda: lexical capture, pure, value-return path | L16971–16995 | — | — |
| R-CEK-05 | Call: LTR evaluation; arity precheck before args; closure-env application | L16878–16905, L37840–37862 | MOD-16 (mutations M001-M003 target this) | — |
| R-CEK-06 | Continuation preservation (+1/−1 per entry/resume) | L14632–14642 | — | — |
| R-CEK-07 | Progress & preservation | L7273–7277, L8850 | MOD-15 (progress/preservation exercised differentially) | — |

### MOD-06 — ACTOR (14 obligations)

| Obligation | Short text (from `spec/03`) | Provenance | Cross-references | Duplication |
|---|---|---|---|---|
| R-ACTOR-01 | Actor isolation (heaps, envs, continuations, mailboxes, budgets, caps) | L41623–41641, L24268–24290 | MOD-03 (isolated capability contexts), MOD-11 (isolated state is snapshot content) | — |
| R-ACTOR-02 | GlobalState shape; logical time global | L24148–24163, L25514–25546 | MOD-07 (runnable queue lives here), MOD-04 (global time/deadline), MOD-11 (GlobalSnapshot content) | — |
| R-ACTOR-03 | Deterministic ID allocation; no address/PID/UUID/wall-clock identity | L24226–24245 | MOD-11 (counters restored from snapshot), MOD-01 (identity is data, not pointers) | — |
| R-ACTOR-05 | Spawn: escrow + derived capabilities only; no wholesale clone | L25573–25615, L37941–37951 | MOD-03 (child capabilities only via derive), MOD-04 (escrow transfer), MOD-02 (BudgetAllocationSpec surface - U-03) | — |
| R-ACTOR-06 | Send async + deterministic wakeup; Receive blocks without fuel; FIFO mailbox | L25702–25749, L37941–37951 | MOD-07 (wakeup enqueues at back), MOD-04 (Receive blocks without fuel) | — |
| R-ACTOR-08 | No amplification / no teleportation theorems | L26048–26070 | MOD-01 (corollaries of R-CORE-04/R-CORE-05) | — |
| R-ACTOR-09 | Spawn transfers no capabilities by default (delegation is the only default path); explicit manifest + constraint compiler-checked, strictly attenuated; Authority(child) ≺ parent; trust_level phantom retracted; BudgetAllocationSpec bounds (C-82 resolved; M025) | addendum (SEC-006) | — | — |
| R-ACTOR-10 | Mailbox resource admission: enqueue requires recipient capacity (M reservation; ReservedCapacityExceeded faults the sender, sender pays); payload-proportional send cost over canonical length; constructed value size bounded against constructor's M; footprint bounded by reserved M (C-96 resolved; M033) | addendum (SEC-019) | — | — |
| R-MARSHAL-01 | Recursive capability rejection in ordinary marshal | L41647–41658, L25674–25701, L37946–37951 | MOD-10 (recursive rejection over canonical domain), MOD-03 (authority never in ordinary data), MOD-01 (central restatement R-CORE-07 (D-04)) | D-04 (canonical statement) |
| R-MARSHAL-02 | Explicit delegation only; DelegatedCapability envelope; ≼ parent | L25972–26001, L37953–37959 | MOD-03 (delegation = kernel derive), MOD-02 (Expr::Delegate surface undecided - U-02), MOD-10 (DelegatedCapability envelope encoding) | — |
| R-MARSHAL-03 | MarshalledValue = canonical bytes; unmarshal(marshal(v)) = v | L25674–25701 | MOD-10 (MarshalledValue is canonical bytes; round-trip scope open - AMB-06) | — |
| R-MARSHAL-04 | Semantic marshalling rule (CapRef ∉ marshal(v)) | L8695–8698 | MOD-10 (traversal over canonical encoding), MOD-03 (explicit delegate() only) | — |
| R-MARSHAL-05 | Delegation constructible: Expr::Delegate calls kernel.derive and yields a kernel-constructed envelope, never a plain Value variant; receive-side revalidation (liveness, lineage, target, generation) before registration, faults leave the recipient CapabilityContext byte-identical; MarshalledValue is the checked-bytes form; MarshalFault unified (X-65; C-79 resolved) | addendum (SEC-005) | — | — |
| R-MARSHAL-06 | contains_capability is a frozen total predicate: closed traversal domain descending into List, Map, Tuple at any depth and FunctionValue.env recursively; sole exclusion kernel-sealed delegation envelopes; Bytes are data; marshal Ok implies no reachable capability (C-81 resolved) | addendum (SEC-018) | — | — |

### MOD-07 — SCHEDULER (2 obligations)

| Obligation | Short text (from `spec/03`) | Provenance | Cross-references | Duplication |
|---|---|---|---|---|
| R-ACTOR-04 | FIFO scheduler; at-most-once membership; 1 transition/turn; blocked/pending/terminal never scheduled | L25558–25615, L37924–37937 | MOD-06 (mailbox wakeup enqueues), MOD-12 (queue reconstructed at recovery), MOD-01 (feeds determinism (D-05)) | — |
| R-ACTOR-07 | Deterministic concurrency theorem | L25759–25766 | MOD-01 (central restatement R-CORE-08 (D-05)), MOD-09 (host trace term), MOD-13 (planner trace term) | D-05 (canonical statement) |

### MOD-08 — EFFECT (8 obligations)

| Obligation | Short text (from `spec/03`) | Provenance | Cross-references | Duplication |
|---|---|---|---|---|
| R-EFFECT-01 | Request = construct→authorize→account→log→Pending→yield | L12177–12194 | MOD-05 (Request yields EffectRequest), MOD-09 (host receives only issued requests) | — |
| R-EFFECT-02 | Gated transition shape Pre∧BudgetOKAuthOK | L7145–7155, L8700–8710 | MOD-03 (AuthOK is kernel Authorized), MOD-04 (BudgetOK is dual gate) | D-08 (marked restatement — canonical statement R-CAP-06, MOD-03) |
| R-EFFECT-03 | Frozen 16-step request sequence | L37891–37908 | MOD-03 (steps 5..7), MOD-04 (steps 8..10, 13), MOD-11 (step 14 durable issuance), MOD-07 (step 15 Pending status), MOD-09 (step 16 host invocation), MOD-01 (refines external-effect chain (D-12)) | D-12 (canonical statement) |
| R-EFFECT-04 | Denial short-circuits all subsequent gates | L24003–24045 | MOD-03 (gate not called), MOD-04 (budget unchanged), MOD-11 (log unchanged), MOD-09 (host never called) | — |
| R-EFFECT-05 | complete_max affordability at issuance | L25799–25825 | MOD-04 (escrow partition arithmetic), MOD-11 (escrow must be durable) | — |
| R-EFFECT-06 | Receipt validates ID + digest; mismatch ⇒ ReplayCorruption, no resume | L23949–24002, L25952–25970 | MOD-09 (receipt produced by host/replay), MOD-10 (bytes underlying both digests), MOD-11 (journal integrity M017) | — |
| R-EFFECT-07 | Completion accounting (charge complete, release reservation, log, resume) | L23949–24002 | MOD-04 (charge/release/refund), MOD-11 (EffectCompleted record appended), MOD-05 (continuation resume) | — |
| R-EFFECT-08 | Receipt-result admission: recursive contains_capability over the result payload at any nesting depth; no capability, no closure; data-domain only; host error via declared closed fault mapping only | addendum (SEC-001) | — | — |

### MOD-09 — HOST (6 obligations)

| Obligation | Short text (from `spec/03`) | Provenance | Cross-references | Duplication |
|---|---|---|---|---|
| R-HOST-01 | Host independently validates OS authority (defense in depth) | L8560–8580, L10168–10172 | MOD-08 (gate 11 is fail-early twin), MOD-01 (chain conjunct) | — |
| R-HOST-02 | Host performs only issued effects; partially trusted | L41823–41841, L27644 | MOD-08 (only issued effects escape), MOD-11 (durable issuance precedes) | — |
| R-HOST-03 | Ordered ReplayHost; ID+digest per entry; no unordered map | L25972–25996, L37985–38000 | MOD-11 (trace sourced from durable journal), MOD-10 (digests recomputed/validated), MOD-12 (replay used by recovery checks) | — |
| R-HOST-04 | Replay correspondence (machine replay valid; real-world replay per effect class) | L3947–3958, L26249–26262 | MOD-12 (recovery is replay over durable records), MOD-15 (live-vs-replay differential), MOD-13 (end-to-end replay with recorded proposal) | — |
| R-HOST-05 | Replay validates trace, not just final state | L38278–38300 | MOD-15 (trace comparison obligation) | — |
| R-HOST-06 | Durable receipt results representable: EffectCompleted {id, digest, result_digest, result: CanonicalData}; replay verifies ResultDigest(result) = result_digest before resumption — third identity conjunct; no ad-hoc result records (C-90 resolved; M029) | addendum (SEC-011) | — | — |

### MOD-10 — SERIALIZATION (13 obligations)

| Obligation | Short text (from `spec/03`) | Provenance | Cross-references | Duplication |
|---|---|---|---|---|
| R-CANON-01 | Serialization independent of Rust layout/serializers | L28185–28228, L28453–28465 | MOD-11 (no secondary serialization), MOD-06 (marshalling uses this format) | — |
| R-CANON-02 | Universal envelope (version/tag/len/payload) | L30532–30543, L33290–33347 | — | — |
| R-CANON-03 | Frozen standalone type tags (0x00, 0x20, 0x30, 0x40, 0x41) | L33087–33154 | — | — |
| R-CANON-04 | Value discriminants + nested-complete-envelope rule | L30544–30552, L33155–33265 | — | — |
| R-CANON-05 | Primitive payloads (Symbol/CapRef/ActorId/EffectId) | L33087–33154 | — | — |
| R-CANON-06 | Collections: count-prefixed; maps semantically ordered; duplicate keys rejected | L30566–30573, L34987–35024, L38164–38172 | — | — |
| R-CANON-07 | Strict decoder contract (5 checks; explicit discriminants; CanonicalError set) | L30575–30586, L32948–33049 | — | — |
| R-CANON-08 | Checked arithmetic; no attacker preallocation; bounded nested cursors; fallible envelope | L30574–30578, L32948–33265 | — | — |
| R-CANON-09 | Digest rules + when-to-compare-bytes rule | L28185–28228, L30588–30590 | MOD-08 (EffectDigest identity), MOD-11 (state_digest / checksums), MOD-09 (replay validation) | — |
| R-CANON-10 | Injectivity as structural property + scoped evidence claim | L30592–30598, L35068 | MOD-15 (evidence scoped to generated distribution), MOD-17 (claim discipline) | — |
| R-CANON-11 | Golden vectors as normative fixtures | L30599–30646, L31948–32010, L33266–33286 | MOD-17 (M1 gate consumes vectors) | — |
| R-CANON-12 | Data decoder rejects capability payloads: 0x05 and standalone 0x30 yield CanonicalError::CapabilityInData; only the kernel-mediated codec path produces or consumes capability payloads; unmarshal runs contains_capability — symmetric boundary (C-14/U-02 security direction; C-78 resolved) | addendum (SEC-003) | — | — |
| R-CANON-13 | One canonical grammar: 15A BE envelope sole; LE revised grammar superseded in-source; single TAG_* namespace (X-50/X-54 resolved); all digests defined over 15A; bidirectional byte-exact golden vectors; LE variants rejected (C-92 resolved; M031) | addendum (SEC-017) | — | — |

### MOD-11 — PERSISTENCE (14 obligations)

| Obligation | Short text (from `spec/03`) | Provenance | Cross-references | Duplication |
|---|---|---|---|---|
| R-DUR-01 | HostInvoked ⇒ DurableIssued | L35150–35156, L37910 | MOD-01 (central restatement R-CORE-06 (D-03)), MOD-08 (steps 14/16), MOD-09 (invocation precondition) | D-03 (canonical statement) |
| R-DUR-02 | Issuance transaction order (7 steps, 2 fsyncs) | L35150–35158 | MOD-08 (transaction sits inside the request sequence), MOD-10 (record payloads are 15A bytes) | — |
| R-DUR-03 | Causal effect protocol (Issued⇒Prepared; Completed⇒Issued; Reconciled⇒Issued; ID+digest identity) | L35111–35144, L37953–37965 | MOD-08 (receipt digests continue the chain), MOD-12 (journal reconstructed and causality-checked) | — |
| R-DUR-04 | Prepared∧¬Issued⇒Discard; Issued∧¬Completed⇒Indeterminate (never NotExecuted) | L35159–35176, L37968–37981 | MOD-12 (classification applied at T1..T4), MOD-08 (escrow semantics at issuance) | — |
| R-DUR-05 | Escrow survives crash | L35210–35215 | MOD-04 (escrow partition owner), MOD-12 (post-recovery invariant check) | — |
| R-PERSIST-01 | Persistence = recording, not a semantic machine; no secondary serialization | L33757–33790, L35078–35087 | MOD-10 (payloads strictly 15A) | — |
| R-PERSIST-02 | Two-level framing; WalFrame checksum; 8 rejection classes | L33802–33830, L35088–35110 | MOD-10 (payload layer is 15A), MOD-12 (rejections surface at recovery) | — |
| R-PERSIST-03 | Record taxonomy; EventEnvelope monotonic sequence | L33861–33900, L35111–35144 | MOD-07 (ActorSelected et al. are envelope events), MOD-17 (EventSequence vs WalSequence open - U-16) | — |
| R-PERSIST-04 | Snapshot content (include/exclude lists) | L26293–26330 | MOD-05 (EvalState/continuation content), MOD-06 (actor state content), MOD-03 (capability contexts durable), MOD-07 (runnable queue content), MOD-10 (machine-state encoding unfrozen - U-02) | — |
| R-PERSIST-05 | Atomic snapshot protocol; ValidSnapshot iff commit+digest | L26216–26240, L35177–35188 | MOD-12 (recovery ignores invalid snapshots), MOD-10 (digest over canonical bytes) | — |
| R-PERSIST-06 | WAL sequence continuity; gaps rejected | L35088–35110, L35189–35208 | MOD-12 (gap detected during recovery) | — |
| R-PERSIST-07 | Durable authority lattice: snapshot carries the AuthorityNode set, revocation_set and generation counters; WAL event kinds CapabilityGranted/Derived/Revoked; recovery reconstructs the arena, replays capability events, faults on dangling or generation-mismatched CapRef; revocation monotonic across crashes (RECOVERY-REVOCATION-DURABLE) | addendum (SEC-004) | — | — |
| R-PERSIST-08 | Storage integrity rewinding resistance: chained checksums (checksum_n = H(checksum_{n−1} ‖ frame_n)); snapshot commit covers state digest + last WAL sequence; keyed chain if storage adversarial, else trust-table records the trusted-writable assumption; consistently-forged negative tests (C-88 resolved) | addendum (SEC-009) | — | — |
| R-TRUST-05 | Crate DAG carries the R-DUR-02 hinge edge ror-runtime → ror-persistence (inverted trait superseded); ror-core → ror-kernel forbidden; forbidden-edge list checked against Cargo.toml; crate-separation rule (C-85 resolved) | addendum (SEC-022) | — | — |

### MOD-12 — RECOVERY (8 obligations)

| Obligation | Short text (from `spec/03`) | Provenance | Cross-references | Duplication |
|---|---|---|---|---|
| R-RECOV-01 | D = ⟨S,L,H⟩; Recover = Replay | L26122–26140 | MOD-11 (D components durable), MOD-15 (recovery differential compares) | — |
| R-RECOV-02 | Normative crash matrix T0–T6 | L35159–35176, L28467–28493 | MOD-11 (rows mirror journal causality), MOD-17 (M10 gate executes the matrix) | D-06 (canonical statement) |
| R-RECOV-03 | Recovery algorithm (12 steps) | L35189–35208, L26272–26300 | MOD-10 (decode via 15A), MOD-07 (queue reconstruction), MOD-04 (conservation re-validated) | D-06 (marked restatement — canonical statement R-RECOV-02, MOD-12) |
| R-RECOV-04 | Independent recovery implementation | L35189–35195, L38858–38890 | MOD-14 (independent recovery oracle), MOD-17 (anti-oracle-collapse review) | — |
| R-RECOV-05 | Invalid(D) ⇒ RecoveryFault; never silently repair | L35196–35208, L38254–38272 | MOD-11 (detection points), MOD-01 (central restatement R-CORE-10 (D-07)) | D-07 (canonical statement) |
| R-RECOV-06 | Budget partition invariant survives crash | L35210–35215 | MOD-04 (invariant statement), MOD-11 (escrow records carry it over) | — |
| R-RECOV-07 | Reconciliation is the only resolution path for Indeterminate | L35111–35144, L26249–26262 | MOD-09 (authoritative host reconciliation protocol), MOD-11 (EffectReconciled record), MOD-17 (outcome variants open - U-15) | — |
| R-RECOV-08 | Reconciliation frozen: I2 holds on every host path incl. supervisor; never re-executes (idempotent query at most); compensations are ordinary gated requests; NotExecuted gated behind authoritative evidence; supervisor allocates lifecycle, not effects (C-89 resolved; M028) | addendum (SEC-010) | — | — |

### MOD-13 — AGENT (7 obligations)

| Obligation | Short text (from `spec/03`) | Provenance | Cross-references | Duplication |
|---|---|---|---|---|
| R-PLANNER-01 | PlanProposal {observation_sequence, block, metadata}; LLMOutput ∈ Data | L27176–27198 | MOD-02 (block enters compile pipeline), MOD-01 (LLMOutput is Data) | — |
| R-PLANNER-02 | Planner cannot allocate/authorize/modify/invoke/bypass | L27271–27285, L37781–37790 | MOD-03 (cannot allocate/authorize), MOD-04 (cannot modify budgets), MOD-07 (cannot touch scheduler), MOD-06 (cannot allocate actors), MOD-09 (cannot invoke host), MOD-02 (cannot bypass compilation), MOD-11 (cannot bypass persistence) | — |
| R-PLANNER-03 | Staleness check; StalePlan rejection, no state mutation | L27199–27236, L28373 | MOD-02 (checked before compilation), MOD-11 (epoch compared against durable log state) | — |
| R-PLANNER-04 | Planner need not be deterministic; PlannerAccepted recording for replay | L27392–27414 | MOD-11 (PlannerAccepted recorded durably), MOD-09 (replay consumes recorded proposal), MOD-07 (determinism theorem term) | — |
| R-PLANNER-05 | LLM outer-loop conformance (3 test obligations) | L27920–27931, L28513–28521 | MOD-17 (harness side (ror-testkit)), MOD-09 (ReplayHost for end-to-end replay), MOD-02 (compiler rejection case 1) | — |
| R-PLANNER-06 | Staleness is exact equality: observation_sequence = current_planning_epoch; either-direction mismatch ⇒ StalePlan with zero state mutation; less-than-only reading superseded; future-tagged proposals mandatory rejection test (C-86 resolved; M026) | addendum (SEC-007) | — | — |
| R-PLANNER-07 | Observation channel capability-opaque: CapabilitySummary frozen as non-referential projection (counts, classes, ceilings); EffectIssued carries {id, actor, digest} only, cap-bearing log shape superseded; Capability ∉ Observables(LLM) (C-87 resolved; M027) | addendum (SEC-008) | — | — |

### MOD-14 — REFERENCE (5 obligations)

| Obligation | Short text (from `spec/03`) | Provenance | Cross-references | Duplication |
|---|---|---|---|---|
| R-REF-01 | Observe_P = Observe_R (+ recovery equivalence); evidence, not proof | L35281–35310, L38935–38953 | MOD-15 (gate executed here), MOD-12 (recovery equivalence conjunct), MOD-17 (acceptance R-TEST-11) | — |
| R-REF-02 | Independence boundary (10 forbidden production deps) | L35330–35375, L37696–37721 | MOD-05 (forbidden dep), MOD-03 (forbidden dep), MOD-04 (forbidden dep), MOD-07 (forbidden dep), MOD-10 (forbidden dep), MOD-11 (forbidden dep), MOD-09 (forbidden dep), MOD-17 (dependency review) | D-10 (canonical statement) |
| R-REF-03 | Reference models all 12 semantic areas; clarity over speed | L41848–41866, L35281–35322, L35341 | MOD-05 (CEK modeled), MOD-03 (algebra modeled), MOD-04 (budgets modeled), MOD-06 (actors/marshalling modeled), MOD-07 (scheduler modeled), MOD-08 (effects modeled), MOD-11 (persistence modeled), MOD-12 (recovery modeled) | — |
| R-REF-04 | Reference non-goals | L35326–35339 | MOD-17 (non-goals bound claims) | — |
| R-SCOPE-04 | Zero shared core logic production/reference | L37696–37721 | MOD-15 (fixtures may be shared, transitions never) | D-10 (marked restatement — canonical statement R-REF-02, MOD-14) |

### MOD-15 — DIFFERENTIAL (5 obligations)

| Obligation | Short text (from `spec/03`) | Provenance | Cross-references | Duplication |
|---|---|---|---|---|
| R-REF-05 | Normalized observations; first divergence; no final-value-only comparison | L38420–38470 (§16), L41869–41906 | MOD-14 (reference emits normalized Observation), MOD-17 (first divergence feeds adjudication) | — |
| R-TEST-01 | Three execution modes + frozen baselines; time ≠ semantics | L38587–38715, L37251–37268 | MOD-17 (CI cadence consumes modes (R-TEST-10)) | — |
| R-TEST-02 | Reproducible counterexample artifact (16 fields) | L38891–38920, L37293–37315 | MOD-17 (artifact consumed by adjudication) | — |
| R-TEST-03 | Shrinking protocol (10 ordered priorities) | L38441–38463 | — | — |
| R-TEST-07 | Semantic coverage by obligation tags; metrics ≠ oracle | L38523–38560, L37402–37414 | MOD-16 (mutation coverage tagged), MOD-17 (coverage report consumed in CI) | — |

### MOD-16 — MUTATION (3 obligations)

| Obligation | Short text (from `spec/03`) | Provenance | Cross-references | Duplication |
|---|---|---|---|---|
| R-TEST-04 | Baseline mutation registry M001–M018; additive | L38473–38492 | MOD-05 (M001..M003), MOD-03 (M004..M006), MOD-04 (M007/M009), MOD-11 (M008/M015/M016), MOD-08 (M010/M017/M018), MOD-07 (M011/M012), MOD-06 (M013), MOD-10 (M014) | — |
| R-TEST-05 | 100% kill rate (non-equivalent); adjudication for equivalents | L38494–38500, L37390–37400 | MOD-17 (release-blocking rule), MOD-15 (kill evidence gathered differentially) | — |
| R-TEST-06 | Mutation validation (verification system tested) | L38515–38540 | MOD-17 (framework self-test infrastructure), MOD-15 (oracle used to prove kills) | — |

### MOD-17 — VERIFICATION (18 obligations)

| Obligation | Short text (from `spec/03`) | Provenance | Cross-references | Duplication |
|---|---|---|---|---|
| R-CLAIM-01 | Scoped conformance claim (frozen wording) | L38913–38917, L42191–42265 | — | — |
| R-CLAIM-02 | 16 prohibited shortcuts | L38858–38890, L42144–42188 | — | — |
| R-CLAIM-03 | Engineering response format; CONFLICT reporting | L38808–38846 | — | — |
| R-CLAIM-04 | Start condition (no new semantic phase; reference alongside) | L38921–38928 | — | — |
| R-ORDER-01 | 20-step implementation order; tests before dependents; reference early | L37793–37812, L42108–42142 | — | — |
| R-ORDER-02 | M0–M11 acceptance criteria | L40763–41100, L42165–42190 | — | — |
| R-ORDER-03 | First security gate (Block ⇏ ExecutablePlan; 7-form differential) | L41155–41195 | MOD-02 (Block =/> ExecutablePlan), MOD-03 (CapRef =/> AuthorityInspection), MOD-06 (capability =/> ordinary transfer), MOD-11 (host after durable issuance) | — |
| R-ORDER-04 | Sprint 1 task set ROR-001…ROR-016 | L41091–41112 | — | — |
| R-ORDER-05 | Definition of done (7 components) | L41124–41142 | — | — |
| R-REF-06 | PanicHost / MockKernel boundary enforcement | L27891–27902 | MOD-08 (gates mocked/asserted), MOD-03 (exactly-once kernel calls asserted), MOD-15 (doubles run inside differential harness) | — |
| R-REPO-01 | Workspace layout; boundaries frozen, names flexible | L39140–39195 | — | — |
| R-REPO-02 | Ten crate contracts (contents + prohibitions) | L39196–40762 | MOD-01 (ror-core contract), MOD-02 (ror-compiler contract), MOD-03 (ror-kernel contract), MOD-05 (ror-runtime contract), MOD-11 (ror-persistence contract), MOD-09 (ror-host contract), MOD-13 (ror-agent contract), MOD-14 (ror-reference contract), MOD-15 (ror-differential contract), MOD-16 (ror-testkit / mutations registry) | — |
| R-REPO-03 | Boundaries enforced structurally (deps, visibility, types, traits, tests) | L41223–41273 | — | — |
| R-SCOPE-03 | STOP-and-report on ambiguity; no silent semantic modification | L37664–37686 | MOD-01 (applies to all frozen semantics; adjudication enforces it (R-TEST-09, this module)) | — |
| R-TEST-08 | Crash-injection matrix T0–T6 | L38831–38846, L35216–35236 | MOD-12 (classification semantics), MOD-11 (crash points T0..T6 defined at issuance) | — |
| R-TEST-09 | Fault adjudication (4-way classification) | L38848–38862, L37404–37414 | MOD-15 (divergences originate here), MOD-01 (specification ambiguity reopens frozen text (R-SCOPE-03)) | — |
| R-TEST-10 | CI gates (PR / nightly / release) | L38864–38890, L37287–37292 | MOD-16 (mutation gate stage), MOD-15 (differential suites staged) | — |
| R-TEST-11 | Final acceptance condition (3 conjuncts) | L38885–38911, L41196–41210 | MOD-15 (oracle equality conjunct), MOD-16 (kill-rate conjunct), MOD-12 (recovery-equivalence conjunct) | — |

**Partition check:** 173 obligations across 17 modules (expected 148).

## 2. Atomic-record partition (545)

| Module | Records | Ranges |
|---|---|---|
| MOD-01 CORE | 58 | REQ-ARCH-001…006; REQ-CALC-001…020; REQ-CORE-001…016; REQ-SCOPE-001…007; REQ-TRUST-001…009 |
| MOD-02 COMPILER | 14 | REQ-COMPILE-001…014 |
| MOD-03 CAPABILITY | 35 | REQ-CAP-001…026; REQ-KERN-001…009 |
| MOD-04 BUDGET | 32 | REQ-BUDGET-001…032 |
| MOD-05 EVALUATOR | 24 | REQ-CEK-001…024 |
| MOD-06 ACTOR | 37 | REQ-ACTOR-001…009; REQ-ACTOR-017…030; REQ-ACTOR-032…035; REQ-MARSHAL-001…010 |
| MOD-07 SCHEDULER | 8 | REQ-ACTOR-010…016; REQ-ACTOR-031 |
| MOD-08 EFFECT | 40 | REQ-EFFECT-001…040 |
| MOD-09 HOST | 14 | REQ-HOST-001…014 |
| MOD-10 SERIALIZATION | 37 | REQ-CANON-001…037 |
| MOD-11 PERSISTENCE | 37 | REQ-DUR-001…014; REQ-PERSIST-001…023 |
| MOD-12 RECOVERY | 22 | REQ-RECOV-001…022 |
| MOD-13 AGENT | 23 | REQ-PLANNER-001…022; REQ-TEST-051 |
| MOD-14 REFERENCE | 36 | REQ-REF-001…009; REQ-REF-017…034; REQ-SCOPE-011…012; REQ-TEST-032; REQ-TEST-045…048; REQ-TEST-052; REQ-TEST-056 |
| MOD-15 DIFFERENTIAL | 33 | REQ-REF-010…013; REQ-REF-035…036; REQ-TEST-001…011; REQ-TEST-020…021; REQ-TEST-033…041; REQ-TEST-043; REQ-TEST-049…050; REQ-TEST-057…058 |
| MOD-16 MUTATION | 9 | REQ-TEST-012…019; REQ-TEST-053 |
| MOD-17 VERIFICATION | 86 | REQ-CLAIM-001…022; REQ-ORDER-001…025; REQ-REF-014…016; REQ-REPO-001…019; REQ-SCOPE-008…010; REQ-TEST-022…031; REQ-TEST-042; REQ-TEST-044; REQ-TEST-054…055 |
| **total** | **545** | |

Placement rule for the 16 records whose registry SOURCE cites zero or two parent
obligations: explicit assignment in `_ownership.py` (REQ_OVERRIDE) with rationale in the
receiving module's REQUIREMENTS section; all other records follow their parent obligation.

## 3. Explicit duplication / overlap register (D-01…D-12)

Pairs/triples where the frozen source states the same content more than once. One endpoint
is the canonical statement; each other endpoint is an explicitly **marked** restatement.
No normative text exists in two owner's modules unmarked (rule 4, `mod/00-overview.md` §2).

| ID | Kind | Endpoints | Canonical statement | Note |
|---|---|---|---|---|
| D-01 | central | R-CORE-04 ⇄ R-CAP-05 | R-CAP-05 (MOD-03 CAPABILITY) | No authority amplification stated centrally (README thesis) and in the algebra v0.2; algebraic statement is canonical. |
| D-02 | central | R-CORE-05 ⇄ R-BUDGET-05 | R-BUDGET-05 (MOD-04 BUDGET) | Budget partition conservation stated centrally and in the budget model; budget-model statement is canonical. |
| D-03 | central | R-CORE-06 ⇄ R-DUR-01 | R-DUR-01 (MOD-11 PERSISTENCE) | HostInvoked => DurableIssued stated centrally and at the durability boundary; boundary statement is canonical. |
| D-04 | central | R-CORE-07 ⇄ R-MARSHAL-01 | R-MARSHAL-01 (MOD-06 ACTOR) | Raw-capability marshal rejection stated centrally and at the actor marshalling boundary; marshalling statement is canonical. |
| D-05 | central | R-CORE-08 ⇄ R-ACTOR-07 | R-ACTOR-07 (MOD-07 SCHEDULER) | Deterministic-concurrency theorem stated centrally and at Phase 13; Phase 13 theorem is canonical. |
| D-06 | central | R-CORE-09 ⇄ R-RECOV-02 ⇄ R-RECOV-03 | R-RECOV-02 (MOD-12 RECOVERY) | Qualified crash-recovery theorem stated centrally; the T0..T6 matrix + algorithm are the canonical operative form. |
| D-07 | central | R-CORE-10 ⇄ R-RECOV-05 | R-RECOV-05 (MOD-12 RECOVERY) | No-silent-repair rule stated centrally and at recovery; recovery statement is canonical. |
| D-08 | distribution | R-CORE-03 ⇄ R-CAP-06 ⇄ R-EFFECT-02 | R-CAP-06 (MOD-03 CAPABILITY) | No unauthorized effects: canonical predicate in the algebra, enforced by the gated transition form and gate 6. |
| D-09 | central | R-TRUST-03 ⇄ R-KERN-03 | R-KERN-03 (MOD-03 CAPABILITY) | No hidden authority stated as trust rule and as kernel visibility rule; kernel visibility statement is canonical. |
| D-10 | verbatim | R-SCOPE-04 ⇄ R-REF-02 | R-REF-02 (MOD-14 REFERENCE) | Zero shared core logic stated in master prompt 1.2 and as the 15C.3 independence boundary; the boundary enumeration is canonical. Intra-module (both MOD-14). |
| D-11 | distribution | R-ARCH-03 ⇄ R-COMPILE-01 ⇄ R-COMPILE-05 | R-COMPILE-01 (MOD-02 COMPILER) | Block has no path into step(): architectural statement vs compiler constructor privacy; compiler statement is canonical. |
| D-12 | refinement | R-CORE-02 ⇄ R-EFFECT-03 | R-EFFECT-03 (MOD-08 EFFECT) | 7-conjunct external-effect chain vs frozen 16-step request sequence (conjuncts realized by gates 5..16); the sequence is canonical. |

## 4. Verification-obligation tag homes (frozen tag set, `spec/08` §1)

Tags are verified *by* the module whose obligations they cover; coverage attribution and
reporting is MOD-15's (R-TEST-07), CI consumption MOD-17's (R-TEST-10).

| Tag | Verifying module | Obligations covered (per `spec/08`) |
|---|---|---|
| `BUDGET-CONSUMPTION-CONSERVATION` | MOD-04 BUDGET | R-BUDGET-05, R-CORE-05 |
| `BUDGET-ESCROW-CONSERVATION` | MOD-11 PERSISTENCE | R-EFFECT-05, R-DUR-05 |
| `CAP-DERIVE-NO-AMPLIFICATION` | MOD-03 CAPABILITY | R-CAP-05, R-CORE-04 |
| `CAP-REVOCATION-ANCESTOR` | MOD-03 CAPABILITY | R-CAP-07 |
| `CEK-CALL-ARGS-LTR` | MOD-05 EVALUATOR | R-CEK-05 |
| `CEK-CALL-ARITY-PRECHECK` | MOD-05 EVALUATOR | R-CEK-05 |
| `CEK-CLOSURE-LEXICAL-CAPTURE` | MOD-05 EVALUATOR | R-CEK-03, R-CEK-04 |
| `EFFECT-ISSUE-DURABLE-BEFORE-HOST` | MOD-11 PERSISTENCE | R-DUR-01, R-CORE-06 |
| `EFFECT-RECEIPT-DIGEST-VALIDATION` | MOD-08 EFFECT | R-EFFECT-06 |
| `MARSHAL-NO-RAW-CAPABILITY` | MOD-06 ACTOR | R-MARSHAL-01, R-CORE-07 |
| `RECOVERY-ISSUED-INDETERMINATE` | MOD-12 RECOVERY | R-DUR-04, R-RECOV-02 |
| `SCHED-BLOCKED-NOT-SCHEDULED` | MOD-07 SCHEDULER | R-ACTOR-04 |
| `SCHED-FIFO` | MOD-07 SCHEDULER | R-ACTOR-04 |
| `SNAPSHOT-COMMIT-INTEGRITY` | MOD-11 PERSISTENCE | R-PERSIST-05 |
| `WAL-GAP-REJECT` | MOD-11 PERSISTENCE | R-PERSIST-06 |
| `WAL-SEQUENCE-CONTINUITY` | MOD-11 PERSISTENCE | R-PERSIST-06 |

## 5. Mutation registry map (M001–M018, baseline frozen; registry owned by MOD-16)

| Mutant | Injected defect (per `spec/08`) | Targets | Semantics owner module |
|---|---|---|---|
| M001 | reverse argument evaluation | R-CEK-05 (LTR) | MOD-05 EVALUATOR |
| M002 | skip arity precheck | R-CEK-05 | MOD-05 EVALUATOR |
| M003 | allow non-function application | R-CEK-05 | MOD-05 EVALUATOR |
| M004 | accept revoked capability | R-CAP-07, R-CORE-03 | MOD-03 CAPABILITY |
| M005 | omit capability ceiling | R-CAP-06 (cost ≤ R_A conjunct) | MOD-03 CAPABILITY |
| M006 | permit capability amplification | R-CAP-05, R-CORE-04 | MOD-03 CAPABILITY |
| M007 | omit budget gate | R-BUDGET-04, R-BUDGET-08 | MOD-04 BUDGET |
| M008 | release indeterminate escrow | R-DUR-05 | MOD-11 PERSISTENCE |
| M009 | permit negative resources | R-BUDGET-02 | MOD-04 BUDGET |
| M010 | allocate EffectId before authorization | R-EFFECT-03/04 (gate ordering) | MOD-08 EFFECT |
| M011 | schedule blocked actor | R-ACTOR-04 | MOD-07 SCHEDULER |
| M012 | duplicate runnable queue entry | R-ACTOR-04 (at-most-once) | MOD-07 SCHEDULER |
| M013 | break mailbox FIFO | R-ACTOR-06 | MOD-06 ACTOR |
| M014 | accept duplicate canonical map key | R-CANON-06 | MOD-10 SERIALIZATION |
| M015 | ignore WAL sequence gap | R-PERSIST-06 | MOD-11 PERSISTENCE |
| M016 | ignore checksum mismatch | R-PERSIST-02 | MOD-11 PERSISTENCE |
| M017 | accept mismatched EffectDigest | R-EFFECT-06, R-DUR-03 | MOD-08 EFFECT |
| M018 | resume after corrupted receipt | R-EFFECT-06 | MOD-08 EFFECT |

## 6. Milestone evidence-gate map (M0–M11; acceptance owned by MOD-17, R-ORDER-02)

| Milestone | Required evidence (per `spec/08` §4) | Modules whose gates bind |
|---|---|---|
| M0 | workspace bootstrap: `cargo check/test/fmt/clippy` pass (spec/07 §4) | MOD-17 VERIFICATION |
| M1 | golden vectors pass; round-trip pass; malformed reject; duplicate keys reject; bytes deterministic | MOD-10 SERIALIZATION |
| M2 | differential equivalence (production vs reference) for Value/Var/Let/Seq/If | MOD-05 EVALUATOR, MOD-14 REFERENCE, MOD-15 DIFFERENTIAL |
| M3 | tags CEK-CALL-ARITY-PRECHECK, CEK-CALL-ARGS-LTR, CEK-CLOSURE-LEXICAL-CAPTURE + deep-call stress | MOD-05 EVALUATOR |
| M4 | CAP-DERIVE-NO-AMPLIFICATION + revocation/expiration/lexical binding + independent reference algebra | MOD-03 CAPABILITY, MOD-14 REFERENCE |
| M5 | authorization, budget gates, deadline, host policy, EffectId/Digest, durable issuance, receipt validation | MOD-08 EFFECT, MOD-11 PERSISTENCE, MOD-09 HOST |
| M6 | FIFO scheduler, FIFO mailbox, spawn isolation, send/receive, delegation, blocked/wakeup | MOD-06 ACTOR, MOD-07 SCHEDULER |
| M7 | WAL, snapshot, effect journal, checksum, sequence continuity, recovery | MOD-11 PERSISTENCE, MOD-12 RECOVERY |
| M8 | generated programs, reference execution, production execution, normalized comparison, first-divergence reporting, shrinking | MOD-15 DIFFERENTIAL, MOD-14 REFERENCE |
| M9 | MutationKillRate = 100% (registered non-equivalent) | MOD-16 MUTATION |
| M10 | T0–T6 exact classifications | MOD-12 RECOVERY, MOD-17 VERIFICATION |
| M11 | exhaustive + property + mutation + differential + crash + stress + determinism + serialization + security all green | MOD-17 VERIFICATION |

