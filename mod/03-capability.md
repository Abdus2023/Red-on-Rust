# MOD-03 — CAPABILITY: Capability algebra and capability kernel

> Owns all authority: what it is, how it is ordered and narrowed, how it is
> checked, and how it is kept invisible. "Evaluator knows references; kernel knows
> authority."

## SECTION-ID

`MOD-03` (domain `CAPABILITY`). Owner module file for the `CAP` and `KERN`
obligation areas.

## TITLE

Capability algebra (five semantic domains, partial order, derivation by meet) and the
capability kernel (opaque references, lineage, authorization predicate) — the sole
authority decision layer of the machine.

## PURPOSE

Define authority as data with an algebra (v0.2): operation-indexed grants over scope,
parameter, resource, and lifetime domains, ordered by `≼` and narrowed by
per-operation meets, so that derivation **cannot amplify** (`derive(A,C) ≼ A` by
construction). Provide the kernel as the only component that can construct, inspect,
or decide authority; everyone else holds opaque, generation-safe `CapRef` handles.

## NORMATIVE-CONTENT

Normative text home: `spec/01` S-09, S-10; atomic renderings
`req/01-registry-part2-semantics.md` (CAP, KERN blocks). This module owns:

- **Semantic domains** (R-CAP-01): operations `O`; scope `S` with interpretation
  `⟦·⟧ ⊆ Target`; parameter constraints `Q` ordered by implication; resource limits
  `R` with component-wise order; lifetimes `T` as intervals. The algebra operates on
  semantic interpretations, not representations.
- **Operation-indexed authority** (R-CAP-02): `A = { (o, ⟨S,Q,R,T⟩) | o ∈ O_granted }`
  — authority cannot contaminate across operations.
- **Partial order** (R-CAP-03) and **constraint ≠ authority** (R-CAP-04).
- **Derivation** (R-CAP-05): `derive(A,C) = { (o, derive_op(A_o, C_o)) }`, per-op meet
  `⟨S ⊓ S_c, Q ⊓ Q_c, R ⊓ R_c, T ⊓ T_c⟩`; `derive(A,C) ≼ A` **by definition of meet**
  — canonical statement of the no-amplification invariant (central restatement
  R-CORE-04 in MOD-01 — marked duplication D-01).
- **Canonical authorization predicate** (R-CAP-06): `Authorized(A,E,t) ⇔ op ∈ O_A ∧
  target ∈ ⟦A_op.S⟧ ∧ A_op.Q(params) ∧ cost ≤ A_op.R ∧ t ∈ A_op.T` (5 conjuncts) —
  canonical predicate for the central `¬Authorized ⇒ ¬ExternalEffect` (distribution
  pair D-08 with MOD-01/MOD-08).
- **Revocation/lineage** (R-CAP-07): `Valid(c,t) ⇔ Live(c) ∧ t ∈ Lifetime(c) ∧
  ∀a ∈ Ancestors(c). Live(a)`; lazy O(depth) ancestor walk.
- **Algebra theorems** (R-CAP-08): attenuation soundness, monotonicity, corollary —
  `SPECIFIED` statements with proof sketches; **not** `PROVEN`.
- **Logical time** (R-CAP-09): `t` is explicit machine state; wall-clock forbidden.
- **Kernel substrate** (R-KERN-01…03): `CapRef {index, generation}` opaque,
  generation-safe, kernel-constructed only; API `authorize/derive/attenuate/valid`
  taking logical time; authority internals (`AuthorityNode`) `pub(crate)`,
  inaccessible to evaluator and runtime (canonical statement of no-hidden-authority;
  central restatement R-TRUST-03 in MOD-01 — D-09).

Crate contract: `ror-kernel` (R-REPO-02) — CapabilityKernel, AuthorityNode,
derivation, revocation, authorization, budget primitives, logical-time validation;
`AuthorityNode` invisible outside (normative text in `spec/01` S-22).

## NON-NORMATIVE-CONTENT

- Representation sketches (globs, CIDR ranges, …) are explicitly permitted
  implementations of the semantic domains, not the domains themselves (R-CAP-01).
- Proof sketches for Theorems 1–3 are informative argument, not evidence (C-43).
- Superseded algebra drafts v0.1 (L4756–5501) and the [10] corrections folded into
  v0.2 (L5502–6343) are traceability, not requirements.
- `AdmissibleConstraint` trait occurrence history is unresolved context (AMB-12,
  U-09), not a frozen contract.

## INPUTS

- `Effect` values to authorize (from MOD-08's sequence, step 6/7).
- `Constraint` values from `Expr::Attenuate` / spawn / delegation (MOD-05, MOD-06).
- Logical time `t` (global state, MOD-06; never the host clock — R-CAP-09).
- `EffectCost` for the `cost ≤ A_op.R` ceiling conjunct (MOD-01 type; MOD-08 use).

## OUTPUTS

- Authorization verdicts: `Ok(())` or `Revoked` / `AncestorRevoked` / `Unauthorized`
  faults (frozen fault surface, MOD-01 R-CALC-06).
- New derived `CapRef` handles (arena nodes with lineage parent links).
- `Valid(c,t)` verdicts for attenuation/delegation premises.

## DEPENDENCIES

- Module dependencies: MOD-01 (types: `Effect`, `CapRef` shell, `Fault`, time).
- Consumers: MOD-05 (evaluator calls `derive`/`authorize`), MOD-06 (spawn/delegation
  derivation), MOD-08 (gate 6/7), MOD-14 (independent re-modeling of the algebra).
- Crate edge: `ror-kernel → ror-core`; the kernel never references runtime state
  (one-directional, `spec/04` §B).
- Blocking open items: **U-09** (`AdmissibleConstraint` vs `Constraint` data form;
  AMB-12), **U-21** (`Op`/`Target`/`Params` domains), **U-02** (canonical encoding of
  `Authority`/`Constraint`, with MOD-10/11), **U-01** affects the lifetime/deadline
  interaction (with MOD-04).

## INVARIANTS

- `derive(A,C) ≼ A` — canonical statement (R-CAP-05; central restatement R-CORE-04 —
  D-01). Attenuation removes and never adds.
- `A₁ ≼ A₂ ⇔ O₁ ⊆ O₂ ∧ ∀o ∈ O₁: S₁≼S S₂ ∧ Q₁≼Q Q₂ ∧ R₁ ≤ R₂ ∧ T₁ ⊆ T₂` (R-CAP-03).
- `Authorized(A,E,t) ⇔ op ∈ O_A ∧ target ∈ ⟦A_op.S⟧ ∧ A_op.Q(params) ∧
  cost ≤ A_op.R ∧ t ∈ A_op.T` (R-CAP-06).
- `Valid(c,t) ⇔ Live(c) ∧ t ∈ Lifetime(c) ∧ ∀a ∈ Ancestors(c). Live(a)` (R-CAP-07).
- `A' ≼ A ∧ Authorized(A',E,t) ⇒ Authorized(A,E,t)` (Theorem 2, R-CAP-08).
- Constraint well-formedness is a *premise* of attenuation transitions
  (`AdmissibleConstraint`, REQ-CAP-024) — status formally open (AMB-12).
- Constraint monotonicity `C₁ ≼ C₂ ⇒ derive(A,C₁) ≼ derive(A,C₂)` (REQ-CAP-025).

## REQUIREMENTS

Canonical text: `spec/01` S-09/S-10; addenda I, V. All 16 obligations `SPECIFIED`.

| ID | Obligation (short) | Provenance (`Red-on-Rust.md`) | Verification |
|---|---|---|---|
| R-CAP-01 | Five semantic domains (O, S, Q, R, T) with orders/meets | L6354–6379 | algebra property tests |
| R-CAP-02 | Operation-indexed authority | L6370–6380 | cross-op contamination tests |
| R-CAP-03 | Authority partial order ≼ | L6381–6390 | monotonicity property |
| R-CAP-04 | Constraint ≠ Authority (narrowing request) | L6391–6396, L6406 | — |
| R-CAP-05 | derive = per-op meet; derive(A,C) ≼ A (D-01 canonical) | L6397–6404 | `CAP-DERIVE-NO-AMPLIFICATION`, M006 |
| R-CAP-06 | Canonical Authorized(A,E,t) predicate (5 conjuncts) (D-08 canonical) | L6406–6421, L6647–6656 | Track B mock-kernel tests; M005 |
| R-CAP-07 | Valid(c,t) incl. ancestor liveness; lazy revocation | L6434–6445, L6647–6656 | `CAP-REVOCATION-ANCESTOR`, M004 |
| R-CAP-08 | Algebra theorems 1–3 (stated, proof-sketch only) | L6422–6433, L6657–6671 | property tests (NOT PROVEN) |
| R-CAP-09 | Explicit logical time; no wall-clock | L6434–6436, L38858–38890 | determinism tests |
| R-CAP-10 | AdmissibleConstraint defined: decidable well-formedness per semantic domain (O/S/Q/R/T); inadmissible constraint faults (InvalidConstraint), never identity/top-default; compile-time validation of attacker-authored constraints (C-94 resolved; M030) | addendum V (SEC-014) | M030, compiler negative suite |
| R-KERN-01 | CapRef opaque, generation-safe, private, kernel-only | L9127–9133, L10178–10208 | visibility review |
| R-KERN-02 | Kernel API: authorize/derive/validate with logical time | L6672–6728, L19153–19175 | exactly-one-call mock tests |
| R-KERN-03 | Authority internals pub(crate)/inaccessible (D-09 canonical) | L39397–39407 | visibility + mutation M005-class |
| R-KERN-04 | Possession-gated authorization: authorize(holder, cap, effect, t) resolves the CapRef through the actor capability context; global-arena no-holder authorize superseded; CapRef bits never suffice (C-77 resolved) | addendum I (SEC-002) | M021, brute-force CapRef exhaustion from a non-holder |
| R-KERN-05 | CapabilityContext real frozen possession type; unit-type sketch superseded; snapshots carry capability context; recovery reconstructs possession before gate authorization | addendum I (SEC-002) | snapshot/recovery round-trip of possession sets |
| R-KERN-06 | Root-grant protocol frozen: Grant(source, authority, ceiling, t) with durable CapabilityGranted record, authority ≼ deployment ceiling, root minted once at initialization; Supervisor.host removed or issued-effect-only (R-HOST-02 binds all callers); planner I/O crate-separated (C-95 resolved) | addendum V (SEC-015) | PanicHost-wraps-all-handles conformance; grant audit test |

Atomic registry records under this module: REQ-CAP-001…026; REQ-KERN-001…009 —
incl. explicitly placed audit records REQ-CAP-022/023 (v0.3 E-Attenuate /
E-AttenuateDenied rules), REQ-CAP-024 (`AdmissibleConstraint` premise), REQ-KERN-006
(parents R-KERN-02+R-KERN-03, one module) and REQ-KERN-009 (evaluator exclusion set:
never receives `Authority`/`Scope`/`Rights`/`Parent`/revocation state; second parent
R-TRUST-03 stays central in MOD-01 — cross-reference only).
**16 obligations / 35 records.**

## SECURITY-BOUNDARY

This module **is** the authority boundary. Trust: kernel = Yes; evaluator and
scheduler may *hold* references but never inspect internals (R-KERN-03, R-TRUST-03).
Every amplification path in the machine terminates here: spawn (MOD-06), delegation
(MOD-06), attenuation (MOD-05), and authorization at the effect gates (MOD-08) all
bottom out in this algebra, so `derive(A,C) ≼ A` and the lazy-revocation lineage walk
are the two properties the whole authority story reduces to.

## VERIFICATION-OBLIGATIONS

- Tags: `CAP-DERIVE-NO-AMPLIFICATION` (R-CAP-05), `CAP-REVOCATION-ANCESTOR`
  (R-CAP-07).
- Mutations targeting this module: M004 (accept revoked), M005 (omit ceiling
  conjunct of R-CAP-06), M006 (permit amplification) — all must kill
  (registry M001–M018 owned by MOD-16).
- Conformance: Track B mock-kernel tests — exactly one `authorize`/`derive` call with
  exact expected parameters (R-REF-06 doubles run by MOD-17's infrastructure);
  algebra property tests over generated authorities; monotonicity property.
- Milestone gates: M4 (`CAP-DERIVE-NO-AMPLIFICATION` + revocation/expiration/lexical
  binding + **independent reference algebra**, MOD-14).
- Reference obligations: reference capability algebra + store modeled independently
  (REQ-REF-023/024 in MOD-14).

## SOURCE-PROVENANCE

- Algebra v0.2 frozen: [11] (L6344–6671); API v0.2 + cost algebra [16]
  (L6672–6729); derivation/lineage detail [27] (L19077–20277); v0.3 attenuation rules
  [16] (L8717–8723), `AdmissibleConstraint` occurrences L7858/L8717/L10068/L10171.
- Kernel privacy: [58] (L39370–39410), master prompt §1.3 (L37722–37744), [17]
  (L9119–9135).
- Canonical set: `spec/02` S-09/S-10; `req/01-registry-part2-semantics.md`.

## CROSS-REFERENCES

Owned here, binding elsewhere:

- R-CAP-06 → MOD-08 (realized as gate 6/7 of the 16-step sequence, R-EFFECT-03) and
  MOD-04 (the `cost ≤ R_A` conjunct is one half of the dual gate R-BUDGET-04).
- R-CAP-07 → MOD-06 (delegated envelopes carry lineage; revocation propagates).
- R-CAP-09 → MOD-06 (logical time is global state, R-ACTOR-02), MOD-04 (deadline
  checks), MOD-07 (scheduler steps advance t).
- R-KERN-01 → MOD-10 (canonical `CapRef` payload exists for persistence/delegation
  only — see U-02/C-14; the algebra-side comment "never serialized directly" is about
  ordinary marshalling, MOD-06).

Owned elsewhere, binding CAPABILITY: R-CORE-04/R-TRUST-03 (MOD-01 central
restatements, D-01/D-09); R-EFFECT-06 receipt paths re-enter `Valid` checks
(MOD-08); R-ORDER-03 property 2 `CapRef ⇏ AuthorityInspection` gate evidence
(MOD-17); spawn derive discipline R-ACTOR-05 (MOD-06).
