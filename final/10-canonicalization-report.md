# FINAL1 — 10. Canonicalization Report

What the compiler merged, normalized, re-homed, preserved, and — explicitly — did not touch. This is the audit trail of the canonicalization operation itself.

## 1. Merged duplicates

- S-15 split across §09 (Actors) and §10 (Scheduler) instead of repeating actor text in a scheduler section; the mod/18 duplication register (D-01…D-12) is honored: every central restatement has exactly one canonical home and every other section references it by ID.
- The two governing invariants carried 'into every section' by spec/00 §4 are stated once (their R-CORE homes) and referenced from §23/§24 via GI IDs; no section restates the boxed formulas.
- Section intros, alias tables and registry tables were generated from the registers; no type definition is restated in a second section (`final/02` §4 Type Definition Homes is an index of homes, not a definition).
- The '15 Core Invariants' table with 10 rows (C-20) is not re-rendered: the GI registry is the consolidation and its rows are ID-linked, so the numbering artifact never propagates.
- R-TEST-01's three execution modes are defined once (§20); §21/§22 reference them; §19–§22 hold exactly their own obligations (R-TEST-02/03, R-TEST-04…06).

## 2. Normalized terminology

- Modal vocabulary: MUST / MUST NOT / SHOULD / SHOULD NOT / MAY / INFORMATIVE as already normalized by spec/01 (examples stay marked Non-normative; golden vectors stay 'normative fixtures, not behavioral rules').
- Terminology adopted from term/ unchanged (T-01…T-86 canonical names; forbidden variants avoided in all compilation-authored prose); no rename of any frozen API/type/symbol/field anywhere in FINAL1 output.
- Cross-reference style unified in compilation-authored text to full IDs (`R-`, `C-`, `U-`, `X-`, `N-`, `T-`, `V-`, `GI-`, `FA-`, `M0NN`, tags); transcribed rows keep their original wording verbatim (their `S-nn`/bare-file references resolve through `final/02`'s alias tables).
- `# Part …` structural headers of spec/01 removed (structure replaced by the 29-section canonical order); zero content deleted — every chunk re-homed.

## 3. Resolved references

- All 184 `R-` tokens appearing anywhere in final/ resolve to exactly one home section (computed each build).
- All `S-nn` references inside transcribed text resolve through the S→§ alias table in `final/02` §2 (the cleaned sections remain the normative homes of their chunks; the alias table makes that resolution mechanical).
- Bare register-file references in transcribed text (`06`, `08`, `09`, …) resolve to the `spec/` document set by the convention declared in `final/01` §01; prefixed forms (`spec/01`, `mod/04`, `term/02`, `dep/05`, `req/03`, `audit/…`) are verified to name existing files.
- Every `C-nn` cited by a requirement resolves in `spec/06`; every `U-nn` in `spec/09` (U-90 excluded — harness fixture, recorded); every `X-nn` in the term index; every `N-nn` law; every `V-nn` in `dep/05`; every mutation `M0NN` within the M001–M042 registry; every obligation tag within the union of the spec/08 frozen + post-audit tag lists.
- Dangling-identifier scan found: none introduced by FINAL1. `NormalizedAST`, `PlanIR`, `Form`, `GlobalEvent`, `CapabilitySummary`, `BudgetSummary`, the seven `Observed*` types and `Expr::Delegate` remain source-undeclared names — recorded as such (term/ rule 13), never given invented definitions.

## 4. Preserved ambiguities (nothing adjudicated)

- 28 open `U-` rows (of 39); 41 open `C-` rows; 87 `X-` collisions (4 BLOCKING); the 12 `F-INFL` guards and 11 REF1 findings at their dispositions; the persistence-audit residual (AMB-27/REQ-RECOV-021); the U-05/C-19 register staleness; the V-05/index disagreement; 10 new `FA-nn` symbol-reuse records. All carried in `final/09`/`final/01` §29.
- Conditional audit verdicts: `REF1-CONDITIONAL`, `V1-CONDITIONAL` (§28/`final/08`) — the two statuses the FINAL1 instruction names as must-not-strengthen; both intact.
- Directional closures are *not* register closures: U-03 (security direction), U-06/U-15, U-08/U-14, U-22 keep their open rows; the addenda quote that scope and so does this report.

## 5. Superseded formulations (traceability)

- 18 `SUPERSEDED` citations preserved verbatim inside their defining rows (index: `final/02` §3); the frozen-source supersession history stays in `spec/02`/`spec/06`. Nothing superseded was resurrected; nothing superseded was deleted.

## 6. Changes made solely for canonicalization

- Re-homed the 24 cleaned sections into the mandated 29-section canonical order; 0 unnumbered normative/note blocks kept attached to their preceding rows.
- Removed the eight `# Part …` structural headers (structure → 29-section order); content identity machine-proven (`final/07` §3 chunk-multiset gate).
- Added compilation-layer registries: `GI-*` (36 invariants; §23–25 index + final/05 formal metadata), `FA-01…FA-10`, type-home index (final/02 §4), symbol table (final/05 §2), per-section canonical-home lists, provenance HTML comments per row.
- Whitespace normalization only inside transcribed chunks (trailing spaces, >2 blank line runs); zero word changed — enforced by the §3 identity gate, which normalizes both sides identically.
- Registries re-emitted from their canonical files (spec/03, spec/08, spec/09 status scan, term/10-index, dep/05, req/registry, mod/18) rather than retyped; governance: this generator registered as a `check.py` gate; `README.md` gained one orientation paragraph for `final/` (additive).
- Section 22 (Stress Testing) intentionally carries a regime index only: its normative content is the R-TEST-01 stress baseline in §20; duplicating it would violate the single-home rule the same instruction imposes.

## 7. Claims deliberately NOT upgraded

| Claim | Would-be upgrade | Why not |
|---|---|---|
| REF1-CONDITIONAL | → REF1-PASS | prohibited by the REF1 audit itself and V1 F-INFL-02; no new evidence exists |
| V1-CONDITIONAL | → V1-PASS | the audit lists material non-blocking gaps as precisely the reason for CONDITIONAL; nothing in the inputs closes them |
| `python3 check.py` ALL PASS (13 checkers) | → semantic VERIFIED for any R-… | the checkers are structural gates over registers; none is defined as a proof method (R-CLAIM-01; spec/07 §1; V1 F-INFL-01) |
| `audit/_conservation_checker.py` PASS | → R-CORE-05/R-BUDGET-05 VERIFIED or PROVEN | it validates the *rules and harness contract* over Op-01…Op-22, not an executing machine; the addendum text itself cites it as gate evidence for a rule shape, not as machine evidence |
| persistence audit “satisfies the requested crash-consistency property” | → R-RECOV-* VERIFIED | conditional on the addenda being normative and at specification level only; carried as audit verdict, statuses unchanged |
| request-pipeline audit “realizable through R-DUR-01/R-CORE-06/PanicHost/R-TRUST-05” | → provable/VERIFIED | the audit's own verdict line was “not provable as frozen on four counts”; addendum VII froze remediations (specification changes), not verification evidence |
| README “Implementation: IN PROGRESS / READY” | → IMPLEMENTED | orientation, not repository evidence (C-09; spec/07 §1); every obligation remains SPECIFIED |
| frozen addenda “resolves C-xx / closes U-xx in the security direction” | → register rows silently re-graded wholesale | only the rows the addenda explicitly re-graded read `resolved-by-addendum`; the directional closures (U-03/U-06/U-08/U-14/U-22) stay OPEN in their own rows; U-05/C-19 staleness preserved |
| golden vectors, `spec/08` conformance tables, mutation registry M001–M042, `ROR-001…016` sprint tasks, `crates/ror-*` layout | → existence of any code/test artifact | all are normative *fixtures/contracts* inside the specification; the repository contains none of them (spec/07 §1) |
| R-CAP-08 theorems' proof sketches | → PROVEN | R-CAP-08's own text states PROVEN is NOT claimed; no mechanized proof exists |

## 8. FINAL VALIDATION checklist (results: `final/07`)

| # | Validation | Result |
|---|---|---|
| 1 | all required sections exist (29 + global-invariant block) | final/07 §1 |
| 2 | section ordering is correct | final/07 §1 (ascending 01…29, machine-checked) |
| 3 | all requirement IDs unique | final/07 §2 (184/184) |
| 4 | all cross-references resolve | final/07 §4, §6 |
| 5 | all canonical types have one definition | final/02 §4 homes + final/07 §5c |
| 6 | mathematical symbols have canonical meanings | final/05 §2–3; reuse preserved as FA records, not reinterpreted |
| 7 | global invariants consolidated | final/05 (GI registry), indexed in §23–25 |
| 8 | security boundaries explicit | final/07 §10; §03/§06/§13/§23 rows verbatim |
| 9 | trust boundaries explicit | §02 (R-ARCH-05 posture incl. recorded residual risk), §03, R-TRUST-04/05 |
| 10 | effect ordering intact | final/07 §10; §11/§13 verbatim R-DUR-02/03/04; R-CORE-14 |
| 11 | persistence/recovery semantics intact | §14/§15/§25 verbatim; T0–T6 matrix byte-identical |
| 12 | reference-model independence constraints intact | §17 + GI-SEC-19; REF1-CONDITIONAL guard final/07 §10b |
| 13 | verification states evidence-based | final/08; §12b (every row SPECIFIED) |
| 14–17 | no unsupported implementation/testing/verification/proof claims | final/07 §9, §11 + §28/08 texts |
| 18 | unresolved decisions visible | final/07 §14; §29; final/09 |
| 19 | generated registries/indexes internally consistent | final/07 §12 |
| 20 | repository governance checks remain valid | final/07 §13 + full `check.py` run |

## 9. Compiler status

`FINAL1` reports no condition preventing the canonicalization itself; the conditions on the *verification* side (BOOTSTRAP repository; REF1/V1 conditional verdicts; U-02 encoding gap; U-35 unfalsifiable theorem; U-08/U-14 fault-surface work; the deferred budget items) are reported in §29/`final/09` rather than absorbed. Final status — **RED-ON-RUST / ARCHITECTURE FROZEN / IMPLEMENTATION READY** — per `final/01` §01 preamble, with its explicit non-meanings; the input evidence demonstrates no condition against that status (and it asserts none above SPECIFIED).
