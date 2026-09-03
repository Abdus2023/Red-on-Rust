# MOD-14 — REFERENCE: Independent executable reference model

> Owns the second, independent implementation of the machine's semantics — the
> oracle that must not be a copy.

## SECTION-ID

`MOD-14` (domain `REFERENCE`). Owner module file for the reference-model obligations
of `REF` (R-REF-01…04) plus the zero-shared-logic rule (R-SCOPE-04).

## TITLE

Independent executable semantic model — purpose and evidence character, the
independence boundary (ten forbidden production dependencies), full semantic scope
(clarity over speed), and non-goals.

## PURPOSE

Provide machine-checked *evidence* of conformance by re-deriving the semantics
independently: an executable model that covers all twelve semantic areas of the
frozen specification, written for transparency rather than speed, and sharing **zero
core transition logic** with production. If production and reference agree under
normalized observation, each implementation is corroborated; if the reference were
derived from production, agreement would prove nothing.

## NORMATIVE-CONTENT

Normative text home: `spec/01` S-20 (reference half); atomic renderings
`req/01-registry-part6-verification.md` and `req/01-registry-part8-reference-15C.md`
(the full Phase 15C text, 45 sections, is registry part 8). This module owns:

- **Purpose & evidence character** (R-REF-01): an independently implemented
  executable reference model provides machine-checked evidence that production
  conforms: `Observe(Production(X)) = Observe(Reference(X))` over the comparison
  domain, and `Canonical(Recover_P(D)) = Canonical(Recover_R(D))` for persistence.
  This is differential verification **evidence, not a formal proof**. (Execution of
  the gate belongs to MOD-15; acceptance composition to MOD-17.)
- **Independence boundary** (R-REF-02): the reference model MUST NOT call any of the
  ten enumerated production surfaces (`ProductionEvaluator, ProductionContinuation,
  ProductionCapabilityKernel, ProductionBudget, ProductionScheduler,
  ProductionSerializer, ProductionRecovery, ProductionPersistence,
  ProductionReplayHost, ProductionTransition`). It may consume test inputs/fixtures
  and emit observations/traces. Shared transition implementations forbidden; shared
  semantic fixtures allowed.
- **Zero shared core logic** (R-SCOPE-04 — placed here because it constrains exactly
  this boundary): no `reference_* → production_*` calls for step, authorize, budget,
  recover, encode, scheduler. Marked duplication D-10: R-REF-02 is the canonical
  enumeration, R-SCOPE-04 its master-prompt statement; both owned here.
- **Scope of modeling** (R-REF-03): the reference independently models CEK
  evaluation, lexical environments, closures, calls, capability derivation,
  revocation, budgets, actors, scheduling, effects, persistence, recovery (the 15C.4
  –15C.19 component models: `RefValue`, `RefEnv`, `RefState`, frozen transition
  rules, `RefCapabilityStore`, budget model, effect protocol, `RefActor`,
  `RefScheduler`, send/receive, marshalling, `RefGlobalState`, persistence model,
  crash semantics, `RefHost`); intentionally small, direct, explicit, deterministic,
  independently structured; performance explicitly secondary to transparency.
- **Non-goals** (R-REF-04): the reference does not redefine semantics, introduce a
  second serialization format, reproduce host implementation details, prove
  correctness mathematically, share production transition code, or optimize.

Crate contract (mirrored by pointer): `ror-reference` — independent executable
semantic model with no production dependencies (R-REPO-02).

## NON-NORMATIVE-CONTENT

- The turn-[35] "minimal Python / distinct language" suggestion is superseded by the
  frozen Rust-crate contract (C-33); *independence*, not the language, is normative.
- "Clarity over speed" stylings are rationale; the normative content is the modeling
  scope + independence + evidence character.
- Reference-side struct sketches (`RefState`, …) are specification artifacts (15C).

## INPUTS

- Frozen semantics only: the specifications of MOD-01…MOD-12 (domain types, CEK
  frames, algebra, budget law, request sequence, actor rules, scheduler rules,
  journal/matrix).
- Shared test inputs/fixtures from MOD-15/17 (allowed explicitly).
- Recorded persistence images and crash scenarios for the recovery oracle side
  (REQ-TEST-045: the reference recovery engine MUST NOT consume production snapshot
  *decoders*).

## OUTPUTS

- Reference observations/traces in the normalized observation domain (shared schema
  with MOD-15: terminal states, event/effect traces, partitions, authority outcomes,
  scheduler trace, faults, recovered state); per REQ-REF-035 both implementations
  emit `Observation`.
- An independent classification of crash scenarios (recovery oracle) and an
  independent canonical-actor-identity mapping per 15C.21 (REQ-REF-036 comparator
  support, MOD-15-side).

## DEPENDENCIES

- Module dependencies (semantic): MOD-01…MOD-12 as *specification* dependencies;
  no implementation dependencies on any production module (R-REF-02).
- Consumers: MOD-15 (the comparator's second input), MOD-16 (kill determination over
  the differential), MOD-17 (acceptance).
- Crate edge: `ror-reference →` frozen semantics only; explicitly none of
  `ror-runtime/ror-kernel/ror-persistence/ror-host` for core logic (`spec/07` §6).
- Blocking open items: inherits the open semantic items of the modules it mirrors
  (U-01…U-09, U-15…) — a reference cannot model undecided semantics; per R-SCOPE-03
  work stops at those points.

## INVARIANTS

- `Observe(Production(X)) = Observe(Reference(X))` for every input `X` in the
  comparison domain; `Canonical(Recover_P(D)) = Canonical(Recover_R(D))` (R-REF-01).
- The ten forbidden production calls (R-REF-02; canonical) ↔ zero shared core logic
  (R-SCOPE-04; marked duplication D-10).
- Anti-oracle-collapse: production recovery/serializer are never the reference oracle
  (R-REF-04 + REQ-TEST-047/048; with MOD-12's R-RECOV-04).
- Divergences are evidence, adjudicated 4-way before any oracle change
  (R-TEST-09 owned by MOD-17 — the reference may be the defective side).

## REQUIREMENTS

Canonical text: `spec/01` S-20. All 5 obligations `SPECIFIED`.

| ID | Obligation (short) | Provenance (`Red-on-Rust.md`) | Verification |
|---|---|---|---|
| R-REF-01 | Observe_P = Observe_R (+ recovery equivalence); evidence, not proof | L35281–35310, L38935–38953 | the gate itself (MOD-15 executes) |
| R-REF-02 | Independence boundary (10 forbidden production deps) (D-10 canonical) | L35330–35375, L37696–37721 | dependency-graph review |
| R-REF-03 | Reference models all 12 semantic areas; clarity over speed | L41848–41866, L35281–35322, L35341 | 15C.42 completeness criteria |
| R-REF-04 | Reference non-goals | L35326–35339 | — |
| R-SCOPE-04 | Zero shared core logic production/reference (D-10) | L37696–37721 | R-REF-02 + dependency-graph review |

Atomic registry records under this module: REQ-REF-001…009, REQ-REF-017…034;
REQ-SCOPE-011, REQ-SCOPE-012 (parent R-SCOPE-04); REQ-TEST-032 (harness executes
same input on both — parent R-REF-01), REQ-TEST-045…048 (recovery independence,
canonical boundary, oracle hierarchy, anti-oracle-collapse — parent R-REF-02),
REQ-TEST-052 (15C completeness — parent R-REF-02), REQ-TEST-056 (15C phase boundary
— parent R-REF-01). **5 obligations / 36 records.**

## SECURITY-BOUNDARY

The reference model is trusted *as an oracle*, which is why its only security content
is its own incorruptibility-by-construction: sharing transition logic with production
would let one bug ratify itself (oracle collapse). The boundary is maintained by
mechanism (Cargo edges, code review, dependency-graph review) and re-proven by
deliberate fault injection (MOD-16's self-validation, REQ-TEST-053).

## VERIFICATION-OBLIGATIONS

- 15C.42 acceptance (REQ-TEST-052): reference CEK, capability algebra, budget
  accounting, scheduler, … complete and independent.
- 15C.38 anti-oracle-collapse (REQ-TEST-048); 15C.35 recovery independence
  (REQ-TEST-045); 15C.37 oracle hierarchy (REQ-TEST-047).
- Reference property suite (REQ-TEST-037, comparator-side in MOD-15); reference
  algebra participates in M4 (`independent reference algebra` clause).
- Milestone gates: M2/M3 (pure CEK + call differential need the reference), M4,
  M8 (differential system), M10 (recovery differential), M11.

## SOURCE-PROVENANCE

- Phase 15C frozen text: [48] (L35272–37168; full section map in
  `req/00-method.md` §5.4); master prompt §15 (L38304–38344, re-anchored); trust
  table/TCB [35] (L28178–28230), [60] (L41848–41866).
- Canonical set: `spec/02` S-20; `req/01-registry-part6-verification.md` +
  `req/01-registry-part8-reference-15C.md` (15C.1–15C.21 side).

## CROSS-REFERENCES

Owned here, binding elsewhere:

- R-REF-02 → every production module (MOD-02…MOD-12): the forbidden dependency list
  is a rule *about them* as much as about this crate; enforcement reviewed by MOD-17
  (dependency-graph review, R-REPO-03 mechanism).
- R-REF-01 → MOD-15 (runs the gate and reports first divergence per R-REF-05),
  MOD-12 (recovery-equivalence conjunct), MOD-17 (acceptance R-TEST-11).
- R-REF-03 → MOD-05/03/04/06/07/08/11/12: each owns the semantics this module
  re-models (the mirror obligations live there; this module owns the *re-modeling*
  contract).
- R-SCOPE-04 ↔ R-REF-02 (D-10, intra-module duplication, marked).

Owned elsewhere, binding REFERENCE: R-ARCH-02 (MOD-01 — the independent architecture
statement), R-REF-05 (MOD-15 — observations must be normalized to be comparable),
R-TEST-06 (MOD-16 — deliberate faults validate the harness/oracle), R-TEST-09
(MOD-17 — reference defect is one adjudication outcome; never auto-patch),
R-ORDER-01 (MOD-17 — reference established early, not postponed), R-ORDER-03
(MOD-17 — gate needs this side operational early). Open items: inherits all blocking
U-items of mirrored modules; none new originate here.
