# MOD-02 — COMPILER: Compilation boundary (Block → ExecutablePlan)

> Owns the only gate through which untrusted program text becomes executable
> authority-carrying structure. Nothing reaches the machine except through it.

## SECTION-ID

`MOD-02` (domain `COMPILER`). Owner module file for the `COMPILE` obligation area.

## TITLE

Compilation boundary: parse, normalize, validate, lower, capability and resource
analysis — the transformation of untrusted `Block` data into a validated,
immutable `ExecutablePlan`.

## PURPOSE

Guarantee that `Block ≠ ExecutablePlan`: untrusted homoiconic data proposed by the
planner (or any other source) can enter the trusted machine **only** as the output of
the complete compilation pipeline. The compiler *establishes executable invariants*
(trust level Yes, R-TRUST-01) — every later module may rely on a plan that is
well-formed, well-typed, capability-analyzed, and statically bounded.

## NORMATIVE-CONTENT

Normative text home: `spec/01` S-06; atomic renderings
`req/01-registry-part1-foundations.md` (COMPILE block). This module owns:

- **Boundary integrity, operative form** (R-COMPILE-01): `Block ≠ ExecutablePlan`;
  a `Block` never implicitly becomes a plan; the only path is compilation. (Central
  architectural restatement R-ARCH-03 stays in MOD-01 — marked duplication D-11.)
- **The frozen pipeline** (R-COMPILE-02): parse → normalize → validate → lower →
  capability analysis → resource analysis; any failed stage yields
  `fault(F_compilation)`; no bypass path exists.
- **Combined static judgment** (R-COMPILE-03): `Γ; κ_static ⊢ e : τ ! F @ B` — type,
  possible-effect set `F` (conservative over-approximation; pure terms give
  `F = ∅`), capability requirements, and a static budget upper bound; worst-case cost
  beyond the bound fails compilation.
- **Plan immutability / temporal integrity** (R-COMPILE-04): an `ExecutablePlan` is
  immutable; new authority at `t₁` can only arrive through a new validated
  compilation; a plan authorized at `t₀` never silently gains authority.
- **Constructor privacy** (R-COMPILE-05): `ExecutablePlan` constructors are private
  to the compiler crate; no other component can forge a plan.

Crate contract: `ror-compiler` (R-REPO-02) — `Block → parse → NormalizedAST →
ValidatedPlan → PlanIR → capability analysis → resource analysis → ExecutablePlan`
(normative text in `spec/01` S-22; not restated here).

## NON-NORMATIVE-CONTENT

- **Correction (X-40):** this bullet previously asserted that pipeline stage names are stage labels,
  "not artifacts in their own right", citing the `spec/05` terminology note on `ExecutablePlan`. Two of
  the three *are* declared artifacts with their own fields, private to this crate:
  `ValidatedPlan { ir: PlanIR, effects: EffectSet }` (L865) and
  `CapabilityCheckedPlan { ir: PlanIR, required_caps: CapSet }` (L866). They are canonical terms in
  their own right (`term/` T-04, T-05), not aliases of `ExecutablePlan` (T-06). `NormalizedAST` (T-07)
  and `PlanIR` (T-08) are *not* artifacts — but for the opposite reason: the source never declares them
  at all (X-29, X-30). `spec/05` row 13 is corrected on the same finding.
- **The crate-contract pipeline above is one of three orderings (X-02, X-41).** It reproduces the
  turn-[58] diagram (L39265–39280) faithfully, and `spec/01` L479 reproduces the same one. The frozen
  struct declarations order the stages differently: `NormalizedAST` is the *content* of `ParsedBlock`
  (L864), not a stage before `ValidatedPlan`, and `PlanIR` is the *content* of `ValidatedPlan` (L865),
  not a stage after it. Two declared stages — `ParsedBlock` and `CapabilityCheckedPlan` — do not appear
  in the rendering at all. Nothing here is renamed or reordered; the collision is in the source and is
  filed rather than resolved. An implementer must not treat the rendering as the stage list.
- **`ValidatedPlan` is also a predicate (X-01, BLOCKING).** The central theorem is
  `ExternalEffect(E) ⇒ ValidatedPlan(P) ∧ …` (`spec/01` L25, R-CORE-02), where `ValidatedPlan(·)` is a
  proposition, while `ValidatedPlan` in this crate is a struct. The two are not interchangeable and the
  source never relates them.
- Superseded judgment forms J1–J4 (v1, L1953–1981) kept for traceability; the
  combined judgment supersedes them (C-35).
- The compilation theorem of v1 (L1930–1960) is a superseded statement form; its
  content survives as the pipeline + combined judgment.

## INPUTS

- `PlanProposal.block` — untrusted `Block` data from MOD-13 (admitted only after the
  staleness check R-PLANNER-03 is satisfied at the machine boundary).
- Frozen `Expr` surface and `Symbol` mapping target (MOD-01: R-CALC-02, R-CALC-03).
- `Constraint` semantic domain for capability analysis (MOD-03: R-CAP-01/04).
- `CostModel` contract for static resource analysis (MOD-04: R-BUDGET-07).

## OUTPUTS

- `ExecutablePlan` — opaque, immutable, privately constructed; the **only** legal
  input to the evaluator (MOD-05) and the only thing runtime state is built from.
- `fault(F_compilation)` on any failed stage (consumed as a normal machine-visible
  outcome; no state mutation beyond the fault).
- Name→`Symbol(u32)` table (compilation-scoped; the runtime never re-derives it).

## DEPENDENCIES

- Module dependencies: MOD-01 (AST/domain types), MOD-03 (constraint semantics;
  ceiling data for the resource judgment), MOD-04 (cost model).
- Consumers: MOD-05 (primary), transitively all runtime modules.
- Crate edge: `ror-compiler → ror-core` only (`spec/07` §6).
- Blocking open item: **U-22** (effect-set inference stage J2 not re-specified in the
  frozen pipeline — affects what "validate"/"capability analysis" must produce; C-35;
  AMB-13). Until decided, the conservative-over-approximation requirement stands and
  the *placement* of effect-set inference is undecided.

## INVARIANTS

- `Block ≠ ExecutablePlan` (R-COMPILE-01). No raw `Block` reaches execution; any
  failed stage is a compilation fault (R-COMPILE-02).
- `Γ; κ_static ⊢ e : τ ! F @ B` with `F` conservative: `F_actual(e) ⊆ F_static` and
  pure terms yield `F = ∅` (R-COMPILE-03); worst-case cost `≤ B` or compilation fails.
- Temporal integrity: `Plan(t₀)` authorized ⇒ no new authority at `t₁` without a new
  validated compilation (R-COMPILE-04).
- Constructor privacy: outside `ror-compiler`, `ExecutablePlan` values are
  unconstructible and read-only (R-COMPILE-05).

## REQUIREMENTS

Canonical text: `spec/01` S-06; addendum I. All 6 obligations `SPECIFIED`.

| ID | Obligation (short) | Provenance (`Red-on-Rust.md`) | Verification |
|---|---|---|---|
| R-COMPILE-01 | `Block ≠ ExecutablePlan` (D-11 canonical) | L41440–41452, L3834–3838 | R-ORDER-03 gate property 1 |
| R-COMPILE-02 | Pipeline stages; any failure ⇒ fault, no bypass | L39253–39267 | malformed-`Block` rejection suite |
| R-COMPILE-03 | Combined static judgment (type, effects, capability req, budget bound) | L3874–3905 | U-22 (J2 re-spec gap) |
| R-COMPILE-04 | Plan immutability / temporal integrity | L1722–1745, L2052–2070 | — |
| R-COMPILE-05 | `ExecutablePlan` constructors private to compiler | L39296–39318 | visibility review |
| R-COMPILE-06 | Embedded Value::Capability literals must be plan-bound: foreign/garbage/undeclared capability literal is a compilation fault (U-22 security-direction closure) | addendum I (SEC-002) | compiler conformance: embedded-literal battery |

Atomic registry records under this module: REQ-COMPILE-001…014 (incl. REQ-COMPILE-014,
the U-22 gap note, explicitly placed here from the audit passes).
**6 obligations / 14 records.**

## SECURITY-BOUNDARY

This is the **first security gate** of the machine (R-ORDER-03 property 1 of 4).
Trust assignment: compiler = Yes (R-TRUST-01) precisely because it is the point where
untrusted data is denied executable standing. The boundary is structural
(constructor privacy + type opacity), not a runtime check: a successfully forged plan
*type* is impossible outside the crate, and a successfully compiled plan has already
passed every static gate. Any weakness here voids the external-effect chain upstream
of all runtime gates.

## VERIFICATION-OBLIGATIONS

- Conformance: R-PLANNER-05(1) untrusted-input rejection (with MOD-13's harness);
  malformed-`Block` rejection suite (R-COMPILE-02).
- First security gate (R-ORDER-03, evidence owned by MOD-17): `Block ⇏
  ExecutablePlan` plus production/reference differential agreement over the 7 pure
  forms incl. faults — must pass **before** external effects are implemented.
- Mutation adjacency: no dedicated M0nn targets the compiler; its guarantees are
  probed by the gate suite and by differential faults (M2 pure-subset agreement).
- Milestone gates binding: M2 (pure CEK differential presumes compiled pure plans),
  M3 (Lambda/Call), the R-ORDER-03 gate itself.
- Structural: constructor privacy verified by visibility review (R-REPO-03
  mechanisms, MOD-17).

## SOURCE-PROVENANCE

- Frozen pipeline + constructor privacy: [54] §2 (L37746–37798), [58] (L39253–39318);
  boundary statement [17] (L9086–9097).
- Judgments: v1 [5] (L1953–1981, superseded form), combined judgment [9]
  (L3874–3905); compilation-theorem provenance L1722–1745, L2052–2070.
- Canonical set: `spec/02` S-06; `req/01-registry-part1-foundations.md` (COMPILE).

## CROSS-REFERENCES

Owned here, binding elsewhere:

- R-COMPILE-01/05 → MOD-05 (the evaluator's only input), MOD-01 (central restatement
  R-ARCH-03, D-11).
- R-COMPILE-03 → MOD-04 (`CostModel` for the static bound), MOD-03 (capability
  requirement descriptors consume the `Constraint` domain).
- R-COMPILE-04 → MOD-13 (planner lifecycle: observation → planner → Block₂ →
  compiler → plan₂, R-PLANNER-03/04).

Owned elsewhere, binding COMPILER: R-PLANNER-02 (MOD-13; planner cannot bypass
compilation — enforcement on this boundary), R-ORDER-03 (MOD-17; gate evidence),
R-SCOPE-03 (MOD-17; STOP-and-report on pipeline ambiguity, currently live for U-22).
Open items affecting this module: U-22 (blocking, this module), U-02 (Delegate
surface, with MOD-06/10), U-13 (proposal digest inputs, MOD-13-side).
