# FINAL1 — 08. Evidence-Status Matrix

Material-claim evidence states as the FINAL1 set must carry them. The status ladder is canonically defined in `final/01` §28; this file assigns every material claim class to a rung. Sources: `spec/00` §2, `spec/07` §1, `spec/08`, `req/` (545 records), and the two conditional audits (`audit/reference-independence-differential-audit.md`, `audit/v1-evidence-integrity-audit.md`). Promotion of any row requires the evidence the ladder names — never this document.

## 1. Obligation classes

| Claim class | Rows | Asserted / evidence-supported status | Repository evidence | Notes |
|---|---|---|---|---|
| All normative requirements (R-*) | 184 | **SPECIFIED** | none (no code, tests, vectors, CI, proofs — spec/07 §1) | promotion requires repo artifacts per spec/00 §2 |
| Atomic requirement records (req/) | 545 | **SPECIFIED** | none | EVIDENCE-STATUS field is per-record and unanimous |
| Source code blocks in the frozen transcript | — | specification text (15A is *frozen to byte level as specification*) | not implementations | spec/07 §1: normative as spec, not implemented |
| Theorems of R-CAP-08 | 3 | **SPECIFIED** (proof sketches in source) | no mechanized proof in repository | R-CAP-08: “PROVEN is NOT claimed” |
| Canonical injectivity (R-CANON-10) | 1 | **SPECIFIED**, scoped claim | none | round-trip/differential evidence *expected*, absent |
| Verification tags (spec/08 §1) | 16 frozen + 9 post-audit (derived from the spec/08 tables; 1 documented alias, MARSHAL-CAPABILITY-REJECT, not indexed) | required, **none satisfied** | NONE (every row) | spec/08 evidence rule: tag satisfied only by a passing test artifact |
| Mutation registry | 42 (M001–M042) | defined; **executed: none** | no kill rate claimable | R-TEST-05 100 % gate is an acceptance requirement |
| Milestones M0–M11 | 12 | **not satisfied** (M0 needs a `cargo check`-clean workspace; none exists) | none | spec/08 §4 “Current state” |
| Crash matrix T0–T6, replay, escrow-survival properties | — | contract (R-DUR/R-RECOV rows) | audit-level review only | persistence audit verdict conditions on addenda being normative; specification-level |

## 2. Audit-verdict and gate rows (the special statuses)

| Row | Status carried | Meaning / prohibition |
|---|---|---|
| REF1-CONDITIONAL | **CONDITIONAL** | MUST NOT be represented as REF1-PASS anywhere without new evidence satisfying F-INFL-02's conditions (independent encoder, declared comparison domain, `ror-core` clause operationalized, crate-edge obligations registered, mutation 100 %, crash harness, differential agreement). — full rule in §3. |
| V1-CONDITIONAL | **CONDITIONAL** | Carried at CONDITIONAL (no input evidence establishes a stronger status). — full rule in §3. |
| `python3 check.py` | PASS (16 structural checkers, 7 classified non-checkers; inventory derived from the `check.py` registration by `final/_build.py` and independently re-derived by `state/_project.py`. Historical inventory counts — 13 at FINAL1 compilation, 15 before the V-08 state gate — are retained as history only) | repository-integrity evidence only; MUST NOT be represented as proof/verification of any R-… claim unless a checker is explicitly defined as the proof method — none is (V1 F-INFL-01) |
| README “Implementation: IN PROGRESS / READY” | orientation claim | not repository evidence (C-09); statuses above unchanged |
| V1 §8 residual claims (F-01 semantics, F-05 record identity, F-04 Observed* domain, REF1-vs-build import) | **UNKNOWN** | genuinely ambiguous evidence, preserved UNKNOWN; absence of implementation never downgrades a SPECIFIED claim |

## 3. The exact conditional texts (quoted)

### REF1-CONDITIONAL — source: `audit/reference-independence-differential-audit.md` §14

> `REF1-CONDITIONAL`. … Not REF1-PASS: multiple required independence properties are UNVERIFIED (observation-equivalence, recovery-equivalence, no-production-semantics-via-`ror-core`, crate-edge enforcement) and several findings (F-01…F-05, F-09, F-11) remain open. … Not REF1-FAIL: no finding is a confirmed BLOCKING coupling … Not REF1-INDETERMINATE: the repository does contain sufficient evidence to determine what the potentially blocking coupling vectors are.

**Carried rule:** MUST NOT be represented as REF1-PASS anywhere without new evidence satisfying F-INFL-02's conditions (independent encoder, declared comparison domain, `ror-core` clause operationalized, crate-edge obligations registered, mutation 100 %, crash harness, differential agreement). The independent reference model remains an architectural contract; FINAL1 does not manufacture a reference implementation from the specification.

### V1-CONDITIONAL — source: `audit/v1-evidence-integrity-audit.md` §10

> **V1-CONDITIONAL** … The verification-state model is coherent, accurate, and fully preserved. … However, material non-blocking evidence gaps remain — indeed, they define the BOOTSTRAP state — including missing implementation, missing execution tests, missing independent encoder, undeclared comparison domain, missing crash harness, missing mutation execution, missing security execution, unregistered enforcement obligations, and an unresolved registry disagreement. These gaps are fully documented in findings F-INFL-01 through F-INFL-12 and in the REF1 audit (F-01…F-11; REF1-CONDITIONAL). They prevent V1-PASS … but do not cause V1-FAIL …

**Carried rule:** Carried at CONDITIONAL (no input evidence establishes a stronger status). Preserved UNKNOWN claims (V1 §8: F-01 `ror-core`-dependence semantics, F-05 snapshot/WAL/journal record identity, F-04 `Observed*` comparison domain, REF1-vs-build import question) remain UNKNOWN — recorded ambiguity, not absent evidence. F-INFL-01 (checker-gate inflation) and F-INFL-02 (REF1→PASS inflation) are BLOCKING-if-they-occur guards: this compilation asserts neither is occurring; `final/07` re-checks the REF1-PASS representation rule.

## 4. Claims deliberately NOT upgraded by FINAL1 (full list with reasons: `final/10` §6)

| Candidate upgrade | Blocked because |
|---|---|
| REF1-CONDITIONAL → → REF1-PASS | prohibited by the REF1 audit itself and V1 F-INFL-02; no new evidence exists |
| V1-CONDITIONAL → → V1-PASS | the audit lists material non-blocking gaps as precisely the reason for CONDITIONAL; nothing in the inputs closes them |
| `python3 check.py` ALL PASS (16 checkers) → → semantic VERIFIED for any R-… | the checkers are structural gates over registers; none is defined as a proof method (R-CLAIM-01; spec/07 §1; V1 F-INFL-01) |
| `audit/_conservation_checker.py` PASS → → R-CORE-05/R-BUDGET-05 VERIFIED or PROVEN | it validates the *rules and harness contract* over Op-01…Op-22, not an executing machine; the addendum text itself cites it as gate evidence for a rule shape, not as machine evidence |
| persistence audit “satisfies the requested crash-consistency property” → → R-RECOV-* VERIFIED | conditional on the addenda being normative and at specification level only; carried as audit verdict, statuses unchanged |
| request-pipeline audit “realizable through R-DUR-01/R-CORE-06/PanicHost/R-TRUST-05” → → provable/VERIFIED | the audit's own verdict line was “not provable as frozen on four counts”; addendum VII froze remediations (specification changes), not verification evidence |
| README “Implementation: IN PROGRESS / READY” → → IMPLEMENTED | orientation, not repository evidence (C-09; spec/07 §1); every obligation remains SPECIFIED |
| frozen addenda “resolves C-xx / closes U-xx in the security direction” → → register rows silently re-graded wholesale | only the rows the addenda explicitly re-graded read `resolved-by-addendum`; the directional closures (U-03/U-06/U-08/U-14/U-22) stay OPEN in their own rows; U-05/C-19 staleness preserved |
| golden vectors, `spec/08` conformance tables, mutation registry M001–M042, `ROR-001…016` sprint tasks, `crates/ror-*` layout → → existence of any code/test artifact | all are normative *fixtures/contracts* inside the specification; the repository contains none of them (spec/07 §1) |
| R-CAP-08 theorems' proof sketches → → PROVEN | R-CAP-08's own text states PROVEN is NOT claimed; no mechanized proof exists |

## 5. Per-area status table (uniformity proof)

| Area | rows | statuses present |
|---|---|---|
| R-ACTOR | 10 | SPECIFIED |
| R-ARCH | 5 | SPECIFIED |
| R-BUDGET | 14 | SPECIFIED |
| R-CALC | 8 | SPECIFIED |
| R-CANON | 13 | SPECIFIED |
| R-CAP | 11 | SPECIFIED |
| R-CEK | 7 | SPECIFIED |
| R-CLAIM | 4 | SPECIFIED |
| R-COMPILE | 6 | SPECIFIED |
| R-CORE | 14 | SPECIFIED |
| R-DUR | 7 | SPECIFIED |
| R-EFFECT | 8 | SPECIFIED |
| R-HOST | 6 | SPECIFIED |
| R-KERN | 6 | SPECIFIED |
| R-MARSHAL | 6 | SPECIFIED |
| R-ORDER | 5 | SPECIFIED |
| R-PERSIST | 8 | SPECIFIED |
| R-PLANNER | 7 | SPECIFIED |
| R-RECOV | 9 | SPECIFIED |
| R-REF | 6 | SPECIFIED |
| R-REPO | 3 | SPECIFIED |
| R-SCOPE | 4 | SPECIFIED |
| R-TEST | 12 | SPECIFIED |
| R-TRUST | 5 | SPECIFIED |

Every set is `{SPECIFIED}`: no area contains a stronger status, so no promotion is concealed in the registry.
