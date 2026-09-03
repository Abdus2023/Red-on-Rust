# FINAL1 — 07. Dependency / Reference Integrity Report

Computed on every `final/_build.py` run (check mode = `check.py`; the whole battery also gates the repository). Verdicts below are machine results over the FINAL1 corpus and its cleaned authorities — they are **structural** checks. Per R-SCOPE-02 and the V1 audit: a passing structural checker is repository-integrity evidence, never semantic verification or proof of any obligation.

## 1. Results (FINAL VALIDATION battery 1–20 mapping)

```
OK   §1  section order 01…29 canonical: 1…29, 29 heads, strictly ascending
OK   §2  requirement IDs: 184 transcribed, 184 unique, exactly the cleaned 184
OK   §3  chunk-multiset identity vs `spec/01`: 184 chunks (184 requirements + 0 orphan/note blocks) match verbatim (whitespace-normalized); zero additions, zero deletions in transcribed material
OK   §4  cross-reference resolution over the whole FINAL1 corpus: all tokens resolve; R:186, S:24, C:94, U:44, X:87, N:33, T:86, V:11, D:12, HD:3, MOD:17, REQ:1, M:42, GI:36, FA:10, F:6, F-INFL:3, GAP:2, DET:3, SECn:23, AMB:4, VU:2, CN:2, ROR:4; documented never-frozen/withdrawn IDs quoted, never defined (gap numbers not reused): R:['R-BUDGET-12', 'R-BUDGET-14'], U:['U-10', 'U-12', 'U-18', 'U-20']
OK   §5  global-invariant registry: 36 rows, every definitional home is a real requirement row; SEC/DET/REC = 22/7/7
OK   §5b GI cross-reference lists resolve (R/U/C/N/M/T/X/HD/V/D/tag/file-path forms only)
OK   §5c no two GI rows share a definitional home (single-home per invariant)
OK   §6  dangling identifiers: declared-undeclared-name scan of FINAL1 corpus: every use of `NormalizedAST`, `PlanIR`, `Form`, `GlobalEvent`, `CapabilitySummary`, `BudgetSummary`, `Expr::Delegate` occurs only in recorded-gap context (undeclared-name lists, U/X rows); `Observed*` mentions: 1 (all inside carried records F-04/term-rule-13/§17-18 gap notes). No FINAL1 text defines them. `U-90` appears exactly once as a recorded fixture note (spec/09 process note 9).
OK   §7  circularity: inherited from `dep/03`/`dep/05` (spec/10 `cycles_detected` field: []); the 16-section SCC and the requirement-layer cycles are the dep/ register's reported architectural-review items — the compilation re-homed rows without adding or removing any edge; FINAL1 introduced no new definitional cycles (each § references homes, no §-level cycles are declared in final/*).
OK   §8  stale references in the cleaned inputs (carried, not edited): U-05/C-19 rows read `open` while R-ARCH-05 records the retirement decision — preserved disagreement (final/09 §C). `req/04` header prose: “all 497 registry records” vs registry.json record_count = 545; “§1 … 8 records” vs 9 VU rows (VU-01…VU-09) — stale prose in the input, recorded not edited. `spec/05` §8: “78 canonical terms / 31 non-conflation laws / X-01…X-86 / N-01…N-31” vs term/10-index counts 86/33/87/X-01…X-87 — stale prose in the input (the file itself was later amended by the term pass; the §8 line lags). `README.md` collision-register line — recomputed from `term/10-index.json` (86 terms / 33 laws / 87 collisions, 4 BLOCKING: X-01, X-50, X-54, X-67) and agrees; kept as orientation prose. `spec/06` C-39 is a pointer row (113 rendered rows, 112 indexed findings) — matches spec/10 findings count 112; no dangling pointer.
OK   §9  implementation-artifact references: 3 occurrences / 1 unique design-path strings (crates/tests/vectors/mutations/scripts — R-REPO-01 frozen layout as *planned* structure; spec/07 §1 records they do not exist); existence-claim phrases: 0
OK   §10 boundary integrity: all six boxed core formulas present verbatim; effect causality clauses present; 122 negative-guarantee tokens preserved across the corpus (every transcribed MUST NOT/MUST/↛/⇏ rides verbatim — weakening is structurally impossible without breaking §3)
OK   §10b reference-independence constraint: REF1-CONDITIONAL present in every context that names a status; every `REF1-PASS` occurrence in the corpus appears only inside a prohibition/negation line (guard for V1 F-INFL-02)
OK   §11 evidence-state discipline: 3 ladder-status phrases matched, 0 outside negation/definition context; all 184 registry rows SPECIFIED; promotion vocabulary appears only inside definitions/negations
OK   §12 registry consistency: final/03 rows 184; final/01 §26 rows 184; both == 184
OK   §12b every registry row status is SPECIFIED (184/184)
OK   §13 governance: `final/_build.py` registered in `check.py` CHECKERS (runs in every `python3 check.py`, check-mode ⇒ drift fails the repository gate); `final/_parse.py` and `final/_content.py` classified NON_CHECKERS (data modules)
OK   §14 open items remain visible: 28 OPEN U-rows (incl. the U-05 stale row) all listed in final/09 and §29 carries the index; 41 open C-rows carried
OK   §15 findings universe: spec/06 rows parsed = 113 (README: 112 findings in 113 rows, C-39 pointer); open = 41
§1  = FINAL VALIDATION 1,2   · §2  = 3   · §3,§12 = 4,9,19   · §4,§6 = 4,6,7 (ref resolution, dangling, symbol meanings via final/05 §2/§3)
§5 = 7,10,12 (invariants consolidated; effect ordering, independence carried by §10/§10b)   · §8,§9 = 2 (order/structure)   · §10 = 8,9,10,11,12   · §11 = 13   · §9 = 14,15,16,17 (no unsupported claims; §9+§11)   · §14 = 18   · §15 = 19   · §13 = 20 (governance)
```

## 2. Dependency-graph facts carried from `dep/` (unchanged by the compilation)

- **crate graph** — `**0 non-trivial SCCs.** The frozen crate graph is a DAG. That is what makes the independence checks of `dep/05` §1 meaningful: the prohibitions are satisfiable.`
- **module graph** — `11 SCCs, **3 non-trivial**. All of them are inside a single crate, so the crate DAG stays acyclic; they are still real mutual imports within that crate.`
- **requirement graph** — `**63 non-trivial SCCs** among 384 components (224 of 545 records sit inside a cycle). Families, classified by the areas involved:`
- **section graph** — `9 SCCs, **1 non-trivial**.`

Edge convention (as in `dep/00`): `A -> B` = **B depends on A**; `mod/18` publishes the opposite convention (V-06, open). The compilation adds only registry/index edges in `final/02`/`final/05`, never machine-dependency claims; it is excluded from `dep/`'s generated graph by design (the graph consumes spec/·mod/·req/ only).

## 3. Open findings carried (summary; full table `final/09`)

- `dep/05` V-findings still open/re-scoped: V-02 (re-scoped), V-04 (resolved in part), V-05, V-06, V-07, V-08 open, V-11 (re-scoped). Resolved: V-01, V-03, V-09, V-10 (addenda III/VI).
- `spec/06`: 41 open rows; `spec/09`: 28 OPEN items — see `final/09`.
- REF1 F-01…F-11 (OWNER-DECISION/TRACK, verdict REF1-CONDITIONAL); V1 F-INFL-01…12 (verdict V1-CONDITIONAL) — carried, statuses unchanged.

## 4. What this report proves and does not prove

It proves: canonical order, ID uniqueness and full coverage, verbatim transcription, reference resolution, registry consistency, single-home invariant/type discipline, evidence-status discipline as expressible in structure, governance registration. It proves nothing about machine behavior: there is no machine in this repository to verify (spec/07 §1). Conformance of any future implementation remains governed by §17–§22's contracts, the status ladder (§28), and the conditional audit verdicts.
