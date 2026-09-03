# MOD-17 — VERIFICATION: Evidence discipline, test infrastructure, CI, claims

> Owns the rules about evidence itself: what may be claimed, what must gate what,
> how divergences are adjudicated, and the repository mechanics that make module
> boundaries enforceable.

## SECTION-ID

`MOD-17` (domain `VERIFICATION`). Owner module file for the evidence/process areas:
`TEST` (08–11), `SCOPE` (03), `REF` (06), `REPO`, `ORDER`, `CLAIM`.

## TITLE

Verification contract and engineering governance — the cage of process that keeps a
frozen specification honest: STOP-and-report discipline, harness boundary doubles,
crash-matrix test obligation, fault adjudication, CI gates, final acceptance,
workspace/crate boundary enforcement, implementation order and milestones,
conformance-claim scope, and prohibited shortcuts.

## PURPOSE

Everything in this repository eventually answers one question — *what evidence
permits which claim?* This module owns the rules of that game: the status ladder
(`SPECIFIED → IMPLEMENTED → TESTED → VERIFIED → PROVEN`, evidence-gated), the
adjudication procedure for divergences, the CI gate structure, the milestone
acceptance criteria, the definition of done, the scoped conformance claim, and the
structural enforcement of the module/crate boundaries themselves (the rules that
make this 17-module split the *operating* architecture rather than documentation).

## NORMATIVE-CONTENT

Normative text home: `spec/01` S-21 (adjudication/CI/acceptance), S-22 (repository),
S-23 (milestones/order), S-24 (claims); atomic renderings
`req/01-registry-part6-verification.md`, `req/01-registry-part7-engineering.md`,
plus `spec/00` §2 (status ladder). This module owns:

- **STOP-and-report process rule** (R-SCOPE-03 — placed here as conformance process;
  central scope statement of it is this very rule's content): frozen semantics are
  never redesigned, reinterpreted, simplified away, or silently modified; exposed
  ambiguity ⇒ STOP and report; ambiguity is never resolved by inventing behavior.
- **Harness boundary doubles** (R-REF-06 — test infrastructure): `PanicHost` panics
  if `execute()` precedes the gates; `MockKernel` asserts exactly one
  `authorize`/`derive` call with exact expected parameters; the production/reference
  boundary is a first-class test subject (these *enforce* MOD-08/MOD-03 boundaries;
  owner placement per `mod/00-overview.md` §3).
- **Crash-injection test obligation** (R-TEST-08): exercise all T0–T6 points; verify
  exact classifications (matrix semantics owned by MOD-12 R-RECOV-02).
- **Fault adjudication** (R-TEST-09): every production/reference divergence is
  classified — production defect | reference defect | harness defect | specification
  ambiguity; never patch the oracle to make a test pass; ambiguity reopens the frozen
  spec explicitly (implements R-SCOPE-03; evidence classification levels per
  15C.44, REQ-TEST-054).
- **CI gates** (R-TEST-10): PR gate (format, lint, unit, exhaustive small-state, core
  differential, serialization conformance); nightly (property generation, mutation
  registry, full differential, persistence fuzzing, crash injection, coverage
  report); release candidate (all nightly + stress + full crash matrix + kill rate
  100% + determinism + recovery differential + security regression). No release with
  unexplained differential mismatch or surviving non-equivalent mutation.
- **Final acceptance** (R-TEST-11): conformance ⇔ `Observe_P(X) = Observe_R(X)` over
  the tested state space **and** `MutationKillRate = 100%` (non-equivalent
  registered) **and** `Canonical(Recover_P(D)) = Canonical(Recover_R(D))` over the
  tested persistence state space; "compiles / unit tests pass / coverage high" is not
  completion.
- **Repository structure** (R-REPO-01…03): frozen boundary layout (`crates/ror-*`,
  `tests/{conformance,exhaustive,property,mutation,crash,stress}`,
  `vectors/…`, `mutations/registry.toml`, `scripts/`); the ten crate contracts;
  boundaries enforced structurally (Cargo dependencies, visibility, types, traits,
  tests, mutation, differential). This split mirrors those crates: each module file
  references its crate contract by pointer (no duplicated contract text).
- **Implementation order & milestones** (R-ORDER-01…05): the 20-step order (tests
  before dependents; reference model early); M0–M11 acceptance criteria; the first
  security gate (four boxed properties per §36, not one: `Block ⇏ ExecutablePlan`,
  `CapRef ⇏ AuthorityInspection`, `Value::Capability ⇏ OrdinaryMessageTransfer`,
  `HostInvocation ⇒ DurableIssued` — registry correction per `req/00-method.md`
  §5.2); first sprint ROR-001…016; the 7-part definition of done.
- **Claims & prohibitions** (R-CLAIM-01…04): the scoped conformance claim
  (machine-checked evidence over the tested state space; never a proof claim);
  the 16 prohibited shortcuts (each semantically owned upstream — per-shortcut map in
  CROSS-REFERENCES below); the engineering response/CONFLICT format; the start
  condition (no new semantic phase; reference alongside production from the start).

## NON-NORMATIVE-CONTENT

- The README's two contradictory status blocks ("IN PROGRESS" vs READY) are the
  C-09 record; neither is repository evidence — the ladder in `spec/00` §2 governs.
- Overlapping work-numbering systems (phases 1–15D, milestones M0–M11, 20-step order,
  ROR-tasks) are presentation; the crosswalk lives in `spec/07` §4 and `spec/08` §4
  (C-21).
- Meeting-time targets ("<2 minutes") are engineering budgets (C-11).
- Process forms (CONFLICT format, response template) are frozen *formats*, not
  semantic content.

## INPUTS

- Evidence artifacts from every module: tag results, kill reports (MOD-16), first-
  divergence reports and counterexample artifacts (MOD-15), crash-matrix results
  (MOD-12 + crash harness), coverage reports (MOD-15).
- Dependency/visibility structure of the workspace (for R-REPO-03 enforcement
  reviews).

## OUTPUTS

- Gate verdicts (PR / nightly / release; milestone M0–M11 acceptance), adjudication
  records, conformance claims bounded by R-CLAIM-01, and CONFLICT reports that reopen
  frozen text where ambiguity appears.

## DEPENDENCIES

- Module dependencies: consumes everything (verification is co-equal with the
  machine, R-ARCH-02); depended on by nothing at runtime.
- Repository homes: `tests/`, `scripts/`, `mutations/registry.toml`, `vectors/`,
  and the workspace skeleton itself.
- Blocking open items: none originate here; every other module's U-items are *this*
  module's concern (they are "stop and report" points). **U-44** is the one item that
  does originate here: whether R-TEST-07's frozen tag set gains the request-frame
  obligation tags `REQUEST-ARGS-LTR` and `REQUEST-NON-CAP-SHORT-CIRCUIT` is a
  verification-register decision (audit GAP-06; with MOD-05/08; coverage, not
  blocking).

## INVARIANTS

- Evidence-gated promotion: `SPECIFIED → IMPLEMENTED → TESTED → VERIFIED → PROVEN`;
  a requirement never confers implementation status (spec/00 §2).
- Acceptance conjunction of R-TEST-11 (three conjuncts; shortcuts enumerated as
  failures, not as partial credit).
- Four-way adjudication with oracle protection (R-TEST-09).
- No silent semantic modification, ever (R-SCOPE-03).
- No release with unexplained differential mismatch or surviving non-equivalent
  mutant (R-TEST-10).
- A milestone is complete only when its verification obligations are satisfied
  (R-ORDER-02).

## REQUIREMENTS

Canonical text: `spec/01` S-21…S-24; addendum VII. All 19 obligations `SPECIFIED`.

| ID | Obligation (short) | Provenance (`Red-on-Rust.md`) | Verification |
|---|---|---|---|
| R-SCOPE-03 | STOP-and-report on ambiguity; no silent semantic modification | L37664–37691 | R-TEST-09 adjudication |
| R-REF-06 | PanicHost / MockKernel boundary enforcement | L27891–27902 | harness tests |
| R-TEST-08 | Crash-injection matrix T0–T6 | L38653–38690 (§23), L35216–35236 | M10 gate |
| R-TEST-09 | Fault adjudication (4-way classification) | L38692–38712 (§24), L37404–37414 | R-SCOPE-03 |
| R-TEST-10 | CI gates (PR / nightly / release) | L38747–38806 (§26), L37287–37292 | gates |
| R-TEST-11 | Final acceptance condition (3 conjuncts) | L38877–38919 (§29), L41196–41210 | M11 |
| R-TEST-12 | Request-frame verification tags: `REQUEST-ARGS-LTR`, `REQUEST-NON-CAP-SHORT-CIRCUIT` added to R-TEST-07's obligation-tagged list; Track A coverage (U-44 resolved) | addendum VII (request-pipeline) | Track A request suite |
| R-REPO-01 | Workspace layout; boundaries frozen, names flexible | L39140–39195 | R-ARCH-02 |
| R-REPO-02 | Ten crate contracts (contents + prohibitions) | L39196–40762 | dependency + visibility review |
| R-REPO-03 | Boundaries enforced structurally (deps, visibility, types, traits, tests) | L41223–41273 | mutation + differential |
| R-ORDER-01 | 20-step implementation order; tests before dependents; reference early | L37800–37834, L42108–42142 | — |
| R-ORDER-02 | M0–M11 acceptance criteria | L40763–41100, L42165–42190 | milestones |
| R-ORDER-03 | First security gate (4 boxed properties + 7-form differential) | L41038–41083, L41084–41123 | gate evidence |
| R-ORDER-04 | Sprint 1 task set ROR-001…ROR-016 | L41006–41037 | — |
| R-ORDER-05 | Definition of done (7 components) | L41124–41142 | — |
| R-CLAIM-01 | Scoped conformance claim (frozen wording) | L38913–38917, L42191–42265 | — |
| R-CLAIM-02 | 16 prohibited shortcuts | L38854–38875, L42144–42188 | mutation + review |
| R-CLAIM-03 | Engineering response format; CONFLICT reporting | L38808–38852 | — |
| R-CLAIM-04 | Start condition (no new semantic phase; reference alongside) | L38921–38928 | — |

Atomic registry records under this module: REQ-SCOPE-008…010; REQ-REF-014…016;
REQ-REPO-001…019; REQ-ORDER-001…025; REQ-CLAIM-001…022; REQ-TEST-022…031;
REQ-TEST-042 (first-divergence algorithm — parent R-TEST-09; comparator machinery
cross-referenced to MOD-15), REQ-TEST-044 (differential persistence testing — parent
R-TEST-08; cross-referenced to MOD-12/MOD-15), REQ-TEST-054 (evidence classification),
REQ-TEST-055 (15C.45 final verification theorem — parent R-TEST-11).
**19 obligations / 86 records.**

## SECURITY-BOUNDARY

This module protects the *epistemics*: the frozen spec's guarantees are only as real
as the discipline that separates "specified" from "verified". Its security content is
the prohibition list and the gates that refuse self-deception (no oracle patching, no
coverage-as-proof, no silent repair, no skipped stages for timing). R-CLAIM-02's 16
prohibited shortcuts are owned here as a list; each shortcut's *substance* is owned
by the module whose semantics it violates:

| Shortcut (prohibited) | Semantic owner module |
|---|---|
| recursive evaluator implementation | MOD-05 |
| trusting AST shape as security boundary | MOD-02 |
| exposing authority internals | MOD-03 |
| wholesale capability cloning at spawn | MOD-06 |
| raw capability transfer in messages | MOD-06 |
| wall-clock time as machine state | MOD-03 (logical time) / MOD-04 |
| saturating budget arithmetic | MOD-04 |
| host invocation before durable issuance | MOD-11 (mechanism) / MOD-08 (order) |
| treating incomplete effects as unexecuted | MOD-11/12 (classification) |
| silent persistence repair | MOD-12 |
| unordered replay | MOD-09 |
| production/reference logic reuse | MOD-14 |
| comparing only final return values | MOD-15 |
| surviving mutations without adjudication | MOD-16 |
| reducing semantic coverage for CI timing | MOD-15 (modes) / MOD-17 (gates) |
| weakening tests for implementation convenience | MOD-17 (this module) |

## VERIFICATION-OBLIGATIONS

- Owns the gate machinery: R-ORDER-02 milestone acceptances (M0–M11 — per-milestone
  evidence owners in `18-ownership-matrix.md` §6), R-TEST-10 CI stages, R-TEST-11
  final acceptance.
- Owns adjudication (R-TEST-09) and its 15C.44 evidence classification
  (REQ-TEST-054); the 15C.45 final verification theorem statement (REQ-TEST-055).
- Owns the crash-matrix *test* obligation (R-TEST-08); the *matrix semantics* stay in
  MOD-12 (obligations are never moved for tidiness — R-TEST-08 is a testing
  obligation and belongs with test governance).
- Structural reviews: dependency-direction review (R-ARCH-04), crate-contract review
  (R-REPO-02/03), constructor/visibility checks (MOD-02/03), mutation + differential
  boundary proofs.
- Self-check obligations: this module's machinery is itself subject to MOD-16's
  R-TEST-06 (the verification system must be tested).

## SOURCE-PROVENANCE

- Master prompt §23–§30 ([54], anchors per `req/00-method.md` §5.1); 15C.44–46
  ([48] L37054–37168); 15D + closure clarifications ([49] L37169–37338; [50]
  L37339–37459); bootstrap pack and milestones ([58] L39036–41273); closing status
  ([60] L41274–42312).
- Canonical set: `spec/02` S-21…S-24; `req/01-registry-part6-verification.md`,
  `req/01-registry-part7-engineering.md`.

## CROSS-REFERENCES

Owned here, binding elsewhere:

- R-REPO-02 → every module: each module file carries a *pointer* to its crate
  contract (single normative home in `spec/01` S-22); the per-crate contents are not
  duplicated into module files.
- R-ORDER-03 → MOD-02 (property 1), MOD-03 (property 2), MOD-06 (property 3),
  MOD-11 (property 4), MOD-14/15 (7-form differential evidence).
- R-TEST-08 → MOD-12 (matrix semantics), MOD-11 (T-point definitions at issuance).
- R-TEST-11 → MOD-15 (oracle equality conjunct), MOD-16 (kill-rate conjunct),
  MOD-12 (recovery-equivalence conjunct).
- R-ORDER-01/04/05 → all modules (build order, first sprint, definition of done).
- R-CLAIM-01 → all modules (nothing may claim beyond evidence).
- R-SCOPE-03 → all modules (any ambiguity STOPs the affected component; the open
  item sets per module are listed in each file's DEPENDENCIES).

Owned elsewhere, binding VERIFICATION: R-TEST-01/02/03/07 (MOD-15 — the modes,
artifacts, and coverage this module's CI consumes), R-TEST-04/05/06 (MOD-16 —
registry the gates execute), R-REF-01…04 (MOD-14 — the oracle), R-ARCH-02 (MOD-01 —
co-equal verification architecture), R-SCOPE-02 (MOD-01 — the frozen status this
module polices). Duplication note: none (this module owns no cross-level invariant
restatements).
