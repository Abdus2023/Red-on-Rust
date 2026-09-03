# MOD-01 — CORE: Core semantics, central invariants, trust model

> Owns the machine's self-definition: what Red-on-Rust is, the central invariants
> every other module must preserve, the trust model, the frozen semantic domain
> types, and the architecture of the whole pipeline.

## SECTION-ID

`MOD-01` (domain `CORE`). Owner module file for the `SCOPE`(01–02) / `CORE` /
`TRUST` / `ARCH` / `CALC` obligation areas.

## TITLE

Core semantics, central invariants, and the trust model — the definition of the
machine boundary itself.

## PURPOSE

Discharge the responsibilities that belong to the machine *as a machine* rather than
to any one component: (a) the core thesis and the central invariants
(`LLMOutput ∧ UntrustedInput ↛ ExternalEffect`, the 7-conjunct effect chain, and the
seven security invariants); (b) the trust model and TCB composition; (c) the overall
pipeline architecture and dependency direction; (d) the frozen semantic domain types
(`Value`, `Expr`, `Symbol`, `Effect`, `EffectCost`, `Fault`, `Σ`/`G` configurations)
that all other modules consume. CORE defines; other modules enforce.

## NORMATIVE-CONTENT

Normative text home: `spec/01` S-01, S-02, S-03, S-04, S-07; atomic renderings
`req/01-registry-part1-foundations.md` and `req/01-registry-part2-semantics.md`
(CALC block). This module owns:

- **Scope/status statements** (R-SCOPE-01…02): the machine thesis and the
  frozen-≠-verified discipline.
- **Central invariants** (R-CORE-01…10): the cross-component security invariants.
  Seven are *central restatements* of invariants whose operative statement lives in a
  downstream module; those pairs are marked duplications D-01…D-08, D-12 (register:
  `18-ownership-matrix.md` §3). CORE remains their canonical **central statement**
  home (its provenance is the thesis text, turns [33]/[60]).
- **Trust model** (R-TRUST-01…03): trust assignment table, TCB composition, and the
  no-hidden-authority rule (central statement; operative visibility statement is
  R-KERN-03 in MOD-03, marked D-09).
- **Architecture** (R-ARCH-01…04): the end-to-end pipeline, the independent
  production/reference architecture, boundary integrity (operative constructors
  statement in MOD-02, marked D-11), dependency direction.
- **Core calculus / semantic domain types** (R-CALC-01…08): frozen `Expr` AST
  (12 constructors), machine `Value` domain (11 variants), `Symbol(u32)` identity,
  `Effect` descriptor + `EffectDigest`, `EffectCost`, frozen `Fault` taxonomy, effect
  property declarations (replayable/reversible/idempotent — classes only), machine
  `Σ` and global `G` configuration shapes.

Crate contract: `ror-core` (R-REPO-02) — semantic domain types; std-only; MUST NOT
contain host calls, filesystem, networking, scheduler, persistence, capability
authority storage, or LLM integration (normative text in `spec/01` S-22; not restated here).

## NON-NORMATIVE-CONTENT

- README architecture diagram and status blocks (orientation; the "Implementation:
  IN PROGRESS/READY" wording is explicitly not evidence — C-09, AMB-24).
- The effect *per-operation property table* (FileRead/NetSend… yes/no/sometimes) is
  illustrative only (R-CALC-07 marks it; C-05, U-06, AMB-20).
- Superseded drafts kept for traceability: 14-constructor calculus and the
  12-constructor calculus *including* `await` (C-04), v1 judgment forms J1–J4 wording
  (C-35), early `Effect` form carrying the capability inside `EffectRequest`
  (superseded per R-CALC-04 provenance), `GlobalConfig` naming (C-42), `invoke` naming
  (C-17), the "15 Core Invariants" table that lists ten rows (C-20, AMB-29).
- Rust struct sketches inside the frozen source for `Expr`, `Value`, `Fault`,
  `GlobalState` are specification artifacts, not repository code (rule per
  `req/00-method.md` rule 10).

## INPUTS

- Nothing: CORE is a definitional foundation. Its *consumers* supply it nothing at
  runtime; at specification time it consumes the frozen source decisions recorded in
  provenance below.

## OUTPUTS

- Frozen domain types consumed by every module: `Expr`, `Value`, `Symbol`, `CapRef`
  (type shell; authority behind it is MOD-03), `ActorId`, `EffectId`, `Effect`,
  `EffectCost`, `Fault`, `LogicalTime`, `EventSequence`, `Σ`/`G` shapes.
- The central invariant set that VERIFICATION (MOD-17) turns into adjudication
  criteria and MUTATION (MOD-16) turns into injection targets.
- The trust table and dependency direction consumed by R-REPO-03 boundary enforcement.

## DEPENDENCIES

- Module dependencies: none upward; every module depends on MOD-01 for types.
- Crate edge: `ror-core` → std only (`spec/07` §6).
- Open decision items affecting CORE: **U-35** (determinism-theorem terms undefined —
  R-CORE-08's own statement; with MOD-07), **U-04** (`await` formal retraction record),
  **U-08/U-14** (`Fault`/error-variant enumeration), **U-09** (machine `Value` vs
  canonical `Value` domain collision; `AdmissibleConstraint` status), **U-21**
  (`Op`/`Target`/`Params` domains), **U-05** (isolation ladder status, with MOD-06).
  Related ambiguity register: AMB-17, AMB-21, AMB-22, AMB-23, AMB-24, AMB-29.

## INVARIANTS

Owned (verbatim from source; provenance per row in REQUIREMENTS):

- `LLMOutput ∧ UntrustedInput ↛ ExternalEffect` (R-CORE-01).
- `ExternalEffect(E) ⇒ ValidatedPlan(P) ∧ Authorized(E,κ,t) ∧ CapabilityWithinCeiling(E)
  ∧ BudgetAvailable(E) ∧ DeadlineValid(E,t) ∧ HostPolicyOK(E) ∧ Issued(E)` (R-CORE-02;
  marked refinement pair D-12 with the 16-step sequence in MOD-08).
- `¬Authorized(A,E,t) ⇒ ¬ExternalEffect(E)` (R-CORE-03; operative predicate
  `Authorized` owned by MOD-03 as R-CAP-06 — marked distribution D-08).
- `derive(A,C) ≼ A` (R-CORE-04; canonical operative statement is R-CAP-05 in MOD-03 —
  marked duplication D-01).
- `C_available + C_escrowed + C_consumed = C_initial` (R-CORE-05; canonical operative
  statement R-BUDGET-05 in MOD-04 — D-02).
- `HostInvoked(E) ⇒ DurableIssued(E)` (R-CORE-06; canonical operative statement
  R-DUR-01 in MOD-11 — D-03).
- `OrdinaryMarshal(Value::Capability) ⇒ Rejected` (R-CORE-07; canonical operative
  statement R-MARSHAL-01 in MOD-06 — D-04).
- `InitialState + SchedulerTrace + HostTrace ⇒ UniqueMachineTrace` (R-CORE-08;
  canonical operative theorem R-ACTOR-07 in MOD-07 — D-05). **U-35 (blocking):** the
  four terms are undefined and trace equality is unspecified, so this invariant is not
  yet well-formed; the audit also records eleven inputs the transition function reads
  that the theorem does not name (`spec/06` C-98…C-102; audit DET-001, §5.1).
- `Recover(Snapshot, EventLog, EffectJournal) ≡ PreCrashMachineState`, qualified by
  the indeterminate-effect proviso (R-CORE-09; canonical operative form is the T0–T6
  matrix + recovery algorithm in MOD-12 — D-06). The system MUST NOT infer
  "not executed" from a missing completion record.
- `Invalid(D) ⇒ RecoveryFault`; never silent repair (R-CORE-10; canonical operative
  statement R-RECOV-05 in MOD-12 — D-07).
- Trust-model invariants (R-TRUST-01…03): component trust assignment as frozen;
  `LLM output ∉ TCB authority`; no component outside the kernel manufactures authority.

## REQUIREMENTS

Canonical text: `spec/01` S-01…S-04, S-07; addenda II–V. All 32 obligations `SPECIFIED`.

| ID | Obligation (short) | Provenance (`Red-on-Rust.md`) | Verification |
|---|---|---|---|
| R-SCOPE-01 | Thesis: deterministic, capability-scoped, resource-bounded, crash-recoverable machine | L41293–41300 | — |
| R-SCOPE-02 | Architecture/spec/verification FROZEN; frozen ≠ verified | L38929–38942, L41297–41315 | — |
| R-CORE-01 | `LLMOutput ∧ UntrustedInput ↛ ExternalEffect` | L41320–41335, L27505–27513 | R-PLANNER-05(1); mutations M004–M008 |
| R-CORE-02 | ExternalEffect chain (7 conjuncts) | L41337–41351, L27491–27509 | R-TEST-07 tags across modules |
| R-CORE-03 | ¬Authorized ⇒ ¬ExternalEffect (D-08) | L42056–42064, L7413–7419 | M004, M005 |
| R-CORE-04 | derive(A,C) ≼ A (D-01) | L42066–42072, L6399–6406 | `CAP-DERIVE-NO-AMPLIFICATION`, M006 |
| R-CORE-05 | Budget partition conservation (D-02) | L42074–42080, L28203–28240 | `BUDGET-CONSUMPTION-CONSERVATION`, `BUDGET-ESCROW-CONSERVATION`, M007, M009 |
| R-CORE-06 | HostInvoked ⇒ DurableIssued (D-03) | L42082–42088, L35150–35156 | `EFFECT-ISSUE-DURABLE-BEFORE-HOST` |
| R-CORE-07 | Ordinary marshal rejects raw capabilities (D-04) | L42090–42098, L25972–26001 | `MARSHAL-NO-RAW-CAPABILITY`, M006-class |
| R-CORE-08 | state+traces ⇒ unique machine trace (D-05) | L41623–41646, L27518–27547 | `SCHED-FIFO`, determinism differential |
| R-CORE-09 | Causal crash recovery, qualified (D-06) | L27551–27569, L35159–35176 | R-RECOV-02 T0–T6 (MOD-12) |
| R-CORE-10 | No silent recovery corruption (D-07) | L42100–42105, L35196–35208 | M015, M016, negative recovery tests |
| R-CORE-11 | One canonical signature per I2 predicate: ValidatedRequest(E) request-time subsuming ValidatedPlan(plan(E)); Authorized(holder, c, E, t) possession conjunct (formalizes R-KERN-04); ValidatedPlan_pred vs ValidatedPlan_struct; chain stated once (X-01/X-04/X-05; C-80 resolved) | addendum II (SEC-016) | R-TEST-09 differential adjudication |
| R-CORE-12 | Fault totality on machine paths: panic-free non-test code, failures map to declared Fault (InternalInvariant family); transition atomicity — complete or fault, no died-mid-transition; durable append precedes in-memory mutation; clippy unwrap/expect denial (C-83 resolved; M034) | addendum III (SEC-020) | M034, panic-catching fuzz harness |
| R-CORE-13 | Closed declared fault surface on every trust-boundary crossing: six replay-path variants, StalePlan, unified MarshalFault, InternalInvariant declared; no debug-formatted external error text in machine values; resume-vs-fault pinned per variant (C-91 resolved) | addendum IV (SEC-012) | fault-coverage lint, differential fault matrix |
| R-TRUST-01 | Trust table (LLM/`Block` No; live host Partial; rest Yes) | L41823–41841, L27611–27624 | — |
| R-TRUST-02 | TCB composition; LLM output ∉ TCB authority | L28178–28230 | — |
| R-TRUST-03 | No hidden authority; evaluator sees refs only (D-09) | L37722–37748, L19153–19175 | Track B (mock kernel), visibility checks |
| R-TRUST-04 | One complete trust table: MOD-06/08/10 rows frozen (authoritative machine boundary); 11-row table superseded; planner never a security/runtime provider — prohibitions homed at enforcing modules; dep/ SC-1/2/3 hard failures (C-84 resolved) | addendum III (SEC-022) | dep/ regeneration with SC-1/2/3 hard-gated |
| R-ARCH-01 | End-to-end pipeline (LLM→…→host) | L37750–37780, L27287–27310 | — |
| R-ARCH-02 | Independent verification architecture | L41406–41424 | R-REF-01 (gate) |
| R-ARCH-03 | `Block` has no path into `step()`; plan constructors private (D-11) | L9086–9097, L39296–39318 | R-ORDER-03 first security gate |
| R-ARCH-04 | Dependency direction (algebra→kernel→plan→actor→global→scheduler→host) | L9059–9085 | Cargo dependency review |
| R-ARCH-05 | Isolation posture decided: ladder retired — in-process structural isolation is the frozen minimum with residual risk (host compromise = machine compromise) recorded; out-of-process host adapter (canonical-bytes effects/receipts) required where host not fully trusted; in-process executor testkit-only (C-93 resolved) | addendum V (SEC-013) | dependency/visibility hard gate; dual-host-mode differential |
| R-CALC-01 | Machine `Value` domain (11 variants); `Capability` is opaque data | L12283–12312 | U-09 open |
| R-CALC-02 | Frozen `Expr` AST (12 constructors, declarative only) | L12132–12170 | U-04, U-05 open |
| R-CALC-03 | `Symbol(u32)` runtime identity; compiler maps names | L12250–12270 | — |
| R-CALC-04 | `Effect` immutable data; `EffectDigest = SHA-256(canonical)`; ID vs digest roles | L9288–9348, L23726–23772 | `EFFECT-RECEIPT-DIGEST-VALIDATION` |
| R-CALC-05 | `EffectCost {issue, complete_max, reserve}` | L25799–25825 | R-EFFECT-05 obligations |
| R-CALC-06 | Frozen `Fault` taxonomy | L23784–23819, L27236 | fault-coverage metric; U-08/U-14 open |
| R-CALC-07 | Effect properties (classes frozen; table illustrative) | L2141–2156, L3858–3873, L26669–26735 | U-06 open |
| R-CALC-08 | `Σ` and `G` configurations; global vs local split | L7119–7144, L8653–8682, L24148–24163 | — |

Atomic registry records under this module (from `req/`, ownership by parent):
REQ-SCOPE-001…007; REQ-CORE-001…016; REQ-TRUST-001…009; REQ-ARCH-001…006;
REQ-CALC-001…020 (incl. REQ-CALC-020 — v0.3 pure E-Let/E-Seq/E-If rules with
`δ_t = 0` premises, placed here explicitly because the registry's own area is CALC;
cross-referenced to MOD-05/MOD-04). **32 obligations / 58 records.**

## SECURITY-BOUNDARY

CORE states *where* the boundary is: the machine itself, never the language surface,
never the model. `Block` and LLM output are untrusted data (R-TRUST-01); the TCB is
exactly the enumerated trusted set (R-TRUST-02). CORE also freezes the two governing
invariants carried into every module (`spec/00` §4). CORE cannot enforce a gate by
itself — every boundary mechanism it declares is owned downstream (cross-references
below), which is why the duplication register exists.

## VERIFICATION-OBLIGATIONS

- Verification tags owned: none directly (CORE invariants are *verified through* the
  operative modules' tags; see D-01…D-08 rows in REQUIREMENTS).
- Conformance obligations feeding CORE claims: global determinism /
  live-vs-replay final-state digest equality (with MOD-07/09); first security gate
  R-ORDER-03 property 1 (`Block ⇏ ExecutablePlan`, with MOD-02).
- Mutation obligations: M004–M009 (with CAPABILITY/BUDGET/EFFECT owners), M015/M016
  (PERSISTENCE) guard CORE invariants C-03…C-06-level.
- Milestone gates binding: M2 (differential agreement over pure calculus), M11.
- Claim discipline: proofs are NOT claimed for the theorems CORE states (C-43);
  every theorem remains `SPECIFIED` with proof-sketch provenance only.

## SOURCE-PROVENANCE

- Central thesis/invariants/trust: turns [33] (L27485–27654), [35] (L28178–28230),
  [60]/README (L41280–41770, L41823–41866, L42056–42105).
- Architecture: [54] §2 (L37746–37798), [17] (L9059–9118), [58] (L39036–39195).
- Core calculus: [20] (L12075–12195), [9] (L3368–4062, superseded v2), [30]
  (L23726–23820), [16] (L8653–8707); supersession trail C-04/C-05/C-06/C-17/C-42.
- Canonical set: `spec/02` Part I rows S-01…S-04, S-07; `req/` part 1 (SCOPE/CORE/
  TRUST/ARCH) and part 2 (CALC block, rows 001…020).

## CROSS-REFERENCES

Owned here, binding elsewhere (enforcement pointers):

- R-CORE-01 → MOD-13 (planner prohibitions R-PLANNER-02), MOD-02 (R-COMPILE-01),
  MOD-08 (gated request sequence R-EFFECT-03).
- R-CORE-02 → gates across MOD-03 (`Authorized`), MOD-04 (budget),
  MOD-08 (sequence), MOD-09 (`HostPolicyOK`), MOD-11 (`Issued`).
- R-CORE-03…10 → operative owners MOD-03/04/06/07/11/12 (D-01…D-07 register).
- R-TRUST-03 → MOD-03 (R-KERN-03, D-09), MOD-05 (evaluator exclusion set,
  REQ-KERN-009 is owned by MOD-03).
- R-ARCH-03 → MOD-02 (R-COMPILE-01/05, D-11), MOD-05 (no `Block` in `step()`).
- R-ARCH-02 → MOD-14/MOD-15 (independent verification architecture).
- R-CALC-01/02/04/05 → consumed by MOD-05, MOD-08, MOD-10 (domain collisions U-09,
  encoding gaps U-02 are decision items, not owned).

Owned elsewhere, binding CORE: R-TEST-09/R-SCOPE-03 (MOD-17) — any ambiguity in
CORE-owned text stops implementation and reopens the frozen spec; R-REPO-02/03
(MOD-17) — `ror-core` crate contract and its structural enforcement.
