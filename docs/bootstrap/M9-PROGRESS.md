# M9 IMPLEMENTATION PROGRESS

**Operation ID:** `RATF-M9-IMPLEMENT-001`  
**Operation:** M9 IMPLEMENTATION ONLY  
**Authority:** M9 PREFLIGHT @ `docs/bootstrap/M9-PREFLIGHT.md` — GREEN WITH DISCLOSED LIMITATIONS — IMPLEMENTATION AUTHORIZED  
**Base HEAD (start):** `5a9615e32850040b604e81050489e9ef29dbe7f2`  
**Branch:** `arena/01a06993-red-on-rust`

```text
M9 IMPLEMENTATION = COMPLETE WITH DISCLOSED EVIDENCE LIMITATIONS
NEXT = M9 IMPLEMENTATION REVIEW
```

---

## 1. Identity

| Item | Value |
|---|---|
| Preflight | `5a9615e` — GREEN WITH DISCLOSED LIMITATIONS; IMPLEMENTATION AUTHORIZED |
| M8 review | `abdfb55` ACCEPTED WITH DISCLOSED |
| M8 impl | `85304c4` |
| Toolchain | `ror-stable` rustc/cargo 1.88.0 |
| Working tree after impl | mutated only via isolated scratch; live tree unmutated |

---

## 2. Canonical authority

| Source | Role |
|---|---|
| R-ORDER-02 M9 | Milestone: MutationKillRate gate |
| final/04 §2 | Registry M001–M042 (authoritative defect map) |
| R-TEST-04 | Baseline + additive registry |
| R-TEST-05 | 100% kill over non-equivalent |
| R-TEST-06 | inject → build → targeted → differential → assert killed |
| MOD-16 | Owns mutation gate; home `mutations/registry.toml` + `ror-testkit` |

Derived consumer only: `mutations/registry.toml` (not authority).

---

## 3. Mutation registry summary

| Field | Value |
|---|---|
| Registered | **42** (M001–M042) |
| Machine mutants | 41 |
| Document mutant | M036 (U-38 / checker gate) |
| Canonical equivalents | **0** (none adjudicated equivalent in registry) |
| Non-equivalent denominator | **42** |
| Unique IDs | PASS (testkit validation) |
| Present & ordered | PASS |

---

## 4. Infrastructure delivered

| Artifact | Role |
|---|---|
| `mutations/registry.toml` | Derived machine-readable registry |
| `crates/ror-testkit` | Registry parse, kill-rate arithmetic, taxonomy, integrity tests |
| `scripts/m9_mutation_run.py` | Isolated inject → build → targeted → differential → classify |
| `mutations/m9-results.json` | Machine-readable run evidence |
| `mutations/m9-matrix.md` | Human matrix |
| Thin M9 surfaces | `ror-agent` planner epoch/CapRef gates (M026/M027); host `verify_result_digest` (M029); env walk / marshal (M032) |

**Isolation model:** each mutant applied in a temp scratch copy of the repo; scratch destroyed after classification. Live tree remains unmutated.

**Production ↛ mutation harness:** no production crate depends on mutation engine semantics.

**Reference independence:** `ror-reference` still depends only on `ror-core`. Differential suite mutates production only.

---

## 5. M001–M042 execution matrix

Full matrix: `mutations/m9-matrix.md`  
JSON: `mutations/m9-results.json`

**Summary:** all **42/42 KILLED**; 0 SURVIVED; 0 EQUIVALENT; 0 NOT-RUN; 0 INCONCLUSIVE.

Differential leg executed where registry marked `differential=true` (and for several CEK/actor/persist mutants): M001–M004, M006, M012–M013, M028 (+ others as configured) recorded `differential_tests_failed` as kill evidence when applicable.

---

## 6. Classification

| State | Count |
|---|---|
| KILLED | 42 |
| SURVIVED | 0 |
| EQUIVALENT | 0 |
| NOT-RUN | 0 |
| INCONCLUSIVE | 0 |

Taxonomy preserved: NOT-RUN ≠ KILLED; SURVIVED ≠ KILLED; INCONCLUSIVE ≠ KILLED (harness unit tests lock arithmetic).

---

## 7. Kill-rate calculation

```text
non_equivalent = registered − canonical_equivalent = 42 − 0 = 42
killed_non_equivalent = 42
MutationKillRate = 42/42 × 100 = 100%
```

Gate R-TEST-05 **satisfied as mutation evidence** (not a formal proof; R-CLAIM-01).

---

## 8. Equivalent-mutant treatment

No registered mutant carries a canonical equivalent disposition.  
`equiv = false` for all 42 rows. Denominator = full registered set.

---

## 9. Survivor records

**None.** No survivor reports required.

---

## 10. Critical mutation results

Security-flagged mutants (registry `security=true`) include M004–M010, M015–M025, M026–M030, M032, M034–M035, M037–M039, M041 (and others per toml).

| Check | Result |
|---|---|
| Critical survived | **NO** |
| Security kills | 30 security-flagged rows KILLED (JSON) |

---

## 11. M5 hinge results

```text
HostInvoked(E) ⇒ DurableIssued(E)
```

| Mutant class | Result |
|---|---|
| M010 EffectId-before-auth | **KILLED** (`deny_path_effect_id_not_consumed`) |
| M007 omit budget | **KILLED** |
| M021 no possession | **KILLED** |
| M037 pre-durability host | **KILLED** (`host_invoked_exactly_once_on_success`) |
| Baseline effects suite | green (16 tests) |

**M5 HINGE = INTACT**

---

## 12. M7 mutation results

| Mutant | Result |
|---|---|
| M015 WAL gap | KILLED |
| M016 checksum | KILLED |
| M023 revocation resurrection | KILLED |
| M028 Indeterminate→Discard | KILLED (+ differential) |
| M038 issuance cost SoT | KILLED |

**M7 RECOVERY BOUNDARY = INTACT** (M10 crash campaign not run).

---

## 13. Differential results

Where configured, differential package tests failed under mutant (production diverged or production tests inside differential crate failed). Reference crate was **not** mutated.

**REFERENCE INDEPENDENCE = PASS**

---

## 14. Determinism evidence

| Property | Evidence |
|---|---|
| Stable IDs M001…M042 | registry + testkit |
| Ordered execution | runner iterates registry order |
| No wall-clock selection | sequential deterministic loop |
| Reproducible classification | re-run campaign → 42/42 KILLED |
| Scratch isolation | no leftover mutants in live tree |

U-35 remains OPEN (no theorem claim).

---

## 15. Regression results

| Gate | Result |
|---|---|
| `cargo fmt --all -- --check` | exit 0 |
| `cargo check --workspace` | exit 0 |
| `cargo test --workspace --lib` | exit 0 |
| `cargo clippy --workspace --all-targets -- -D warnings` | exit 0 |
| M1–M8 surfaces | preserved (core/runtime/persistence/differential green) |
| `ror-testkit` integrity tests | 8 passed |

Representative lib counts remain green including differential system, runtime CEK/effects/actors, persistence recovery.

---

## 16. Security findings

- No surviving non-equivalent mutant.
- No surviving critical mutant.
- Hinge-class M010 killed.
- Capability/receipt/recovery security mutants killed.

```text
BLOCK-SECURITY = not raised
```

---

## 17. Disclosed limitations

| ID | Limitation |
|---|---|
| L-M9-INJECT-STYLE | Operators are source-level textual injections of the registered defect intent, not a general AST mutator framework |
| L-M9-TARGETED-FILTER | Kill oracles use cargo test name filters + package suites; not an exhaustive obligation-tag runner |
| L-M9-DIFF-SUBSET | Differential leg runs for registry-marked / configured mutants; pure-CEK M8 domain limitation carried |
| L-M9-M036-DOC | M036 killed via document/checker gate (U-38), not machine CEK injection |
| L-M9-THIN-AGENT | M026/M027 use thin planner surface added for registered obligations — not full LLM agent |
| L-M9-NO-PROOF | 42/42 kills are mutation evidence, not VERIFIED/PROVEN/R-REG promotion |
| F-04 / U-* | OADs remain OPEN; not closed by M9 |
| U-35 | Determinism theorem open |

---

## 18. Harness self-integrity (R-TEST-06)

`ror-testkit` tests cover:

- registry count/uniqueness/expected IDs
- load of repo `mutations/registry.toml`
- kill-rate arithmetic (100%, survivor blocks, NOT-RUN ≠ KILLED, equivalent excluded)
- taxonomy label distinctness

Runner refuses wrong registry count/order (`BLOCK-CANONICAL` path).

---

## 19. R-REG / OAD / M10 / M11

| Item | State |
|---|---|
| R-REG | **184 × SPECIFIED** (unchanged) |
| OADs | OPEN (F-04 UNKNOWN; U-02/U-08/U-09/U-17/U-21/U-31/U-35 and residuals) |
| M10 | NOT STARTED |
| M11 | NOT STARTED |
| Canonical `final/` `reg/` `dep/` `mod/` `spec/` | not modified for mutation semantics |

---

## 20. Final M9 status

```text
M9 IMPLEMENTATION = COMPLETE WITH DISCLOSED EVIDENCE LIMITATIONS

REGISTERED MUTANTS = 42

NON-EQUIVALENT MUTANTS = 42

KILLED = 42

SURVIVED = 0

EQUIVALENT = 0

NOT-RUN = 0

INCONCLUSIVE = 0

MUTATION KILL RATE = 100%

CRITICAL MUTANTS SURVIVED = NO

M5 HINGE = INTACT

M7 RECOVERY BOUNDARY = INTACT

REFERENCE INDEPENDENCE = PASS

R-REG = 184 × SPECIFIED

OADs = OPEN (F-04 UNKNOWN; U-02/U-08/U-09/U-17/U-21/U-31/U-35 and applicable residuals OPEN)

M10 = NOT STARTED

M11 = NOT STARTED

NEXT = M9 IMPLEMENTATION REVIEW
```

### Absolute non-claims

- Not formal proof / semantic proof / complete verification  
- Not production readiness  
- Not OAD closure / R-REG promotion  
- Not M10/M11 completion  
- Reference correctness not proven merely by differential kills  
- Harness integrity ≠ completeness of all possible faults  

Even **42/42 killed** is **mutation evidence**, not a mathematical proof of the calculus (R-CLAIM-01).

---

*End of M9 IMPLEMENTATION. Do not perform M9 review in this operation.*
