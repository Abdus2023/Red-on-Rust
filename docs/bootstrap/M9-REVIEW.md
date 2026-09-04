# M9 IMPLEMENTATION REVIEW

**Operation ID:** `RATF-M9-REVIEW-001`  
**Operation type:** M9 IMPLEMENTATION REVIEW ONLY  
**Repository:** `Abdus2023/Red-on-Rust`  
**Branch:** `arena/01a06993-red-on-rust`  

```text
M9 IMPLEMENTATION REVIEW = ACCEPTED WITH DISCLOSED EVIDENCE LIMITATIONS
M9 IMPLEMENTATION = COMPLETE
NEXT = M10 PREFLIGHT
```

Evidence labels: **FACT** | **DERIVED** | **PASS** | **PASS-DISCLOSED** | **FAIL-*** | **BLOCK-***

---

## 1. Identity and Lineage

| Item | Value | Class |
|---|---|---|
| Review HEAD | `b5563db8cd8c0d34aa3b4175e0207d210f31f439` | FACT |
| HEAD == `b5563db` | **YES** | FACT |
| M9 workflow / evidence-separation revision | `b5563db` | FACT |
| M9 implementation baseline | `2e92bf4` | FACT |
| M9 preflight | `5a9615e` | FACT |
| M8 review | `abdfb55` | FACT |
| Working tree at review start | clean | FACT |

**Lineage (ancestors of HEAD):**

```text
5a9615e  M9 PREFLIGHT
    ↓
2e92bf4  M9 IMPLEMENTATION (registry, runner, campaign 42/42)
    ↓
b5563db  M9 workflow VERIFY + harness/campaign split + campaign rerun  = HEAD
```

All expected SHAs are ancestors of HEAD (**FACT**).

**`b5563db` contents (verified via `git show --stat`):** workflow/VERIFY revision, terminal taxonomy + separation, campaign artifact updates, `M9-PROGRESS.md` rewrite — **PASS**.

**Evidence Record: R-ID**

- **Gate:** Identity / lineage  
- **Status:** PASS  
- **Canonical authority:** review charter RATF-M9-REVIEW-001  
- **Observed:** HEAD exact `b5563db`; ancestry `5a9615e→2e92bf4→b5563db`  
- **Conclusion:** Authorization identity matches; review proceeds.

---

## 2. Canonical Authority

| Source | Role | Review use |
|---|---|---|
| R-ORDER-02 / final/01 M9 row | Milestone name + gate | MutationKillRate acceptance |
| final/04 §2 | **Authoritative** M001–M042 defect map | Registry completeness |
| R-TEST-04 | Baseline + additive registry | Completeness / permanence |
| R-TEST-05 | 100% over non-equivalent | Kill-rate arithmetic |
| R-TEST-06 | inject→build→targeted→diff→assert kill | Lifecycle |
| MOD-16 | Owns M9; points `mutations/registry.toml` + `ror-testkit` | Homes |

**Derived consumer check:** `mutations/registry.toml` is labeled derived of final/04. All 42 IDs present once, ordered M001…M042. Defect strings match final/04 modulo markdown-backtick stripping only (10 cosmetic diffs, no semantic ID/defect swap) — **PASS-DISCLOSED**.

`mutations/registry.toml` is **not** treated as independent authority.

**Evidence Record: R-AUTH**

- **Status:** PASS-DISCLOSED  
- **Canonical authority:** final/04 §2; R-TEST-04/05/06; MOD-16  
- **Evidence limitation:** derived TOML omits backticks in defect prose  
- **Conclusion:** No BLOCK-CANONICAL divergence of IDs or defect intent.

---

## 3. M9 Scope

| In scope (reviewed) | Out of scope |
|---|---|
| Mutation registry consumption | M10 crash-matrix gate |
| Operators + isolated materialization | M11 RC triad |
| VERIFY-MUTATION, classify, kill-rate | OAD closure |
| Campaign M001–M042 | R-REG promotion |
| Harness/campaign separation | Canonical `final/`/`reg/` edits |

No M10/M11 work in this review. No implementation repairs.

---

## 4. Harness Implementation Review

**Domain A** — `crates/ror-testkit`, `scripts/m9_mutation_run.py`.

| Stage | Present | Notes |
|---|---|---|
| LOAD | yes | `parse_registry`; BLOCK-CANONICAL on count≠42 or order mismatch |
| BASELINE | yes | `cargo test --workspace --lib` once; failure ⇒ all NOT-RUN |
| MATERIALIZE | yes | scratch `copy_tree` + `apply_mutant` |
| VERIFY-MUTATION | yes | fingerprint delta + `MUTANT Mxxx` marker (M036 special-case) |
| BUILD | yes | `cargo test -p PKG --lib --no-run` / fallback check |
| TARGETED | yes | `TARGETED` map filters |
| DIFFERENTIAL | yes | when `differential=true` |
| CLASSIFY | yes | `classify_terminal` pure mapping |
| RECORD | yes | JSON `m9-campaign-v2` + matrix |
| CLEAN | yes | `finally: shutil.rmtree(scratch)` |
| NEXT | yes | sequential registry order |

**Production ↛ harness:** `ror-testkit` depends on `ror-core` only; production crates do not depend on mutation engine for semantics.

**No path** `if harness_pass: mutant_killed = true` in kill-rate path. Kill rate uses only `results[].classification` (**FACT**, source review of `main()` aggregate).

**Evidence Record: R-HARNESS-IMPL**

- **Status:** PASS  
- **Implementation location:** `scripts/m9_mutation_run.py`, `crates/ror-testkit`  
- **Conclusion:** Lifecycle implemented; domain A does not enter K/N.

---

## 5. Harness Test Evidence

```text
Command: cargo test -p ror-testkit --lib -- --test-threads=1
Working tree / revision: b5563db
Exit status: 0
Tests: 10 passed
Result: PASS
```

Covered classes (test names):

| Class | Test |
|---|---|
| Registry IDs / load | `expected_ids_stable`, `loads_repo_registry_toml`, `parse_one_row` |
| Kill-rate math | `kill_rate_100`, `survivor_blocks_100`, `equivalent_excluded_from_denominator` |
| NOT-RUN ≠ KILLED | `not_run_not_killed` |
| INCONCLUSIVE ≠ 100% | `build_failure_is_not_killed` |
| Harness ≠ kill-rate | `harness_pass_does_not_imply_kill_rate` |
| Taxonomy distinct | `taxonomy_labels_distinct` |

Runner also embeds inline `classify_terminal` purity checks in `run_harness_tests()` (build→INCONCLUSIVE, mat-fail→NOT-RUN, detect→KILLED, nodetect→SURVIVED).

**These results are Domain A only and are not added to K.**

**Evidence Record: R-HARNESS-TEST**

- **Status:** PASS  
- **Security relevance:** MEDIUM (gate integrity)  
- **Evidence class:** TEST  
- **Conclusion:** Harness self-tests green; separated from campaign.

---

## 6. Campaign Evidence

### Independent executions (review)

```text
Command: python3 scripts/m9_mutation_run.py \
  -o /tmp/m9-review-runA-results.json --matrix /tmp/m9-review-runA-matrix.md
Revision: b5563db
Exit status: 0
```

```text
Command: python3 scripts/m9_mutation_run.py \
  -o /tmp/m9-review-runB-results.json --matrix /tmp/m9-review-runB-matrix.md
Revision: b5563db
Exit status: 0
```

(CLI confirmed via `--help`: full campaign = default invocation without `-k`; **not** an invented `--all`.)

### Independent recomputation (Domain B only)

| Run | Registered | N non-eq | KILLED | SURVIVED | EQ | INC | NOT-RUN | Rate | gate_ok | harness.pass |
|---|---|---|---|---|---|---|---|---|---|---|
| A | 42 | 42 | 42 | 0 | 0 | 0 | 0 | 100 | true | true |
| B | 42 | 42 | 42 | 0 | 0 | 0 | 0 | 100 | true | true |
| Committed JSON | 42 | 42 | 42 | 0 | 0 | 0 | 0 | 100 | true | true |

```text
N = registered − equivalent = 42 − 0 = 42
K = KILLED = 42
MutationKillRate = K/N×100 = 100%
```

Stored `kill_rate_percent` matched recomputation on all three artifacts.

**A == B** on (mid, classification, materialization, verification, targeted, differential, evidence) for all 42 rows — **PASS**.

**Ordering:** M001…M042 exact.

**Per-row stage invariants (A/B):** materialization=PASS, mutation_verification=PASS, build=PASS, targeted_execution=FAIL (detection), classification=KILLED.

**Harness PASS ≠ kill-rate:** JSON note + separate `harness` object; K counted only from classifications — **PASS**.

**Evidence Record: R-CAMPAIGN**

- **Status:** PASS  
- **Evidence class:** MUTATION  
- **Test / evidence:** `/tmp/m9-review-runA-results.json`, runB, `mutations/m9-results.json`  
- **Conclusion:** Independent dual campaign reproduces 42/42 KILLED.

---

## 7. Per-Mutant Classification

Terminal states used: **KILLED** only (campaign).  
Mutual exclusivity of the five-state enum enforced in schema assert + classifier.

| Rule checked | Result |
|---|---|
| KILLED ⇒ applied ∧ verified ∧ detection | PASS (all 42) |
| Build failure ⇒ INCONCLUSIVE not KILLED | PASS (classifier + harness unit) |
| Mat failure ⇒ NOT-RUN | PASS (classifier) |
| Verify failure ⇒ INCONCLUSIVE | PASS (classifier) |
| EQUIVALENT only if `meta.equiv` | PASS (registry all `equiv=false`) |
| No silent ID skip | PASS (42 terminal rows, unique) |

**Evidence Record: R-STATE-MACHINE**

- **Status:** PASS  
- **Canonical rule:** R-TEST-05/06; M9 preflight taxonomy  
- **Conclusion:** No illegal collapse of NOT-RUN/INCONCLUSIVE into KILLED observed.

---

## 8. VERIFY-MUTATION Review

**Claimed rule:** fingerprint(pre) ≠ fingerprint(post) **and** marker `MUTANT Mxxx` present (M036 document special-case).

| Check | Result |
|---|---|
| Fingerprint over crates/mutations/final/scripts sources | PASS (implementation) |
| Unchanged tree ⇒ verify FAIL | PASS (code) |
| Verify before build/test classify | PASS (`execute_one` order) |
| Verify FAIL ⇒ INCONCLUSIVE, never KILLED | PASS |
| Marker ID-specific (`MUTANT M{id}`) | PASS |
| Fresh scratch per mutant (no stale marker leak) | PASS (isolation) |
| M036 constrained to document rotation in scratch `final/04` | PASS-DISCLOSED |
| Bypass: report verified without transform? | No path if fingerprint unchanged; marker alone insufficient | PASS |

**Disclosed residual:** M036 may accept `document_fingerprint_delta` if table-swap string match fails but any fingerprint change occurred — weaker than machine marker path; still requires actual tree mutation in scratch, not live tree. Campaign kills M036 via checker gate after rotation — **PASS-DISCLOSED**.

**Evidence Record: R-VERIFY**

- **Status:** PASS-DISCLOSED  
- **Security relevance:** HIGH  
- **Conclusion:** No BLOCK-SECURITY bypass of “verified without apply” for machine mutants; M036 special-case disclosed.

---

## 9. Scratch Isolation

| Property | Observed |
|---|---|
| Live tree ≠ mutant workspace | temp `m9-Mxxx-*` under `/tmp` |
| CLEAN in `finally` | yes |
| Live `MUTANT M0*` markers after campaigns | **0 lines** (`rg` over crates/final) |
| Cross-mutant contamination | prevented by per-mutant scratch |
| Campaign not run on pre-mutated live tree | baseline on REPO first |

**Evidence Record: R-ISOLATION**

- **Status:** PASS  
- **Conclusion:** No residual mutants; no BLOCK-REGRESSION contamination.

---

## 10. Kill-Oracle Review

Oracles are behavioral tests (deny paths, digest mismatch, escrow conservation, env walk, etc.). Comments may cite `Mxxx` as documentation of intent; assertions bind to **semantic outcomes**, not marker presence.

Spot-check (critical / previously corrected):

| Mutant | Operator intent | Oracle / detection | Aligns with final/04? |
|---|---|---|---|
| M001 | reverse arg bind | CEK LTR + differential | yes |
| M004 | skip revoked check | kernel revoke cascade | yes |
| M010 | EffectId before auth | `deny_path_effect_id_not_consumed` | yes |
| M017 | accept bad EffectDigest | `mismatched_receipt_digest_is_corruption` | yes |
| M018 | skip receipt validation | same family | yes |
| M022 | accept Cap on data decode | `golden_capref_kernel_only` | yes |
| M028 | Indeterminate→Discard | `t2_issued_indeterminate` + diff | yes (class wrong vs NotExecuted label; still wrong recovery class) |
| M032 | skip Function env walk | `machine_contains_capability_walks_function_env` | yes |
| M036 | doc body rotation | checker/gate | yes (document mutant) |
| M037 | host before durable sync | `host_invoked_exactly_once_on_success` | yes |
| M042 | double duration charge | `budget_charge_matches_issue_plus_complete_max_only` | yes |

**Disclosed:** operators are source-level textual injections of registered defect intent (not a general AST mutator). Oracles are suite filters, not full obligation-tag scheduler.

**Evidence Record: R-ORACLE**

- **Status:** PASS-DISCLOSED  
- **Evidence class:** TEST + MUTATION  
- **Conclusion:** No self-fulfilling “assert marker exists” kill path found for machine mutants.

---

## 11. Differential Review

| Check | Result |
|---|---|
| Differential runs production vs reference | PASS (existing M8 crate) |
| Reference mutated by harness? | **NO** — operators target production/core/persist/agent/host/doc only |
| `ror-reference` Cargo deps | `ror-core` only |
| Forbidden edges runtime/kernel/persistence/host/agent | absent |
| M8 system tests | 90 passed |

**Evidence Record: R-DIFF**

- **Status:** PASS  
- **Canonical authority:** R-REF-02; R-TEST-06 differential leg  
- **Conclusion:** No BLOCK-INDEPENDENCE.

---

## 12. Critical Mutation Review

Registry `security=true` rows: **30** in campaign JSON; all **KILLED**.  
`critical_survived=false` on runs A/B/committed.

Critical classes exercised and killed include: capability revoke/ceiling/amplify, budget/escrow, EffectId order (M010), receipt integrity, WAL gap/checksum, recovery revocation/Indeterminate, host pre-durability (M037), planner epoch/CapRef, marshal env, etc.

**CRITICAL SURVIVED = NO**

**Evidence Record: R-CRIT**

- **Status:** PASS  
- **Security relevance:** CRITICAL  
- **Conclusion:** No BLOCK-SECURITY.

---

## 13. M5 Hinge

```text
HostInvoked(E) ⇒ DurableIssued(E)
```

| Evidence | Result |
|---|---|
| Baseline `effects::` 16 tests | PASS |
| M010 kill (ID before auth) | KILLED |
| M037 kill (host before sync) | KILLED |
| Deny paths never host | baseline tests PASS |

**M5 HINGE = INTACT**

**Evidence Record: R-M5**

- **Status:** PASS  
- **Command:** `cargo test -p ror-runtime --lib effects:: -- --test-threads=1` → exit 0, 16 passed  
- **Conclusion:** Hinge preserved; hinge-class mutants killed.

---

## 14. M7 Boundary

| Check | Result |
|---|---|
| M9 ran recovery **code** mutants (M015/016/023/028/…) | yes, as registry |
| Full T0–T6 **M10 crash campaign** | **not** absorbed / not run as M10 gate |
| Indeterminate ≠ NotExecuted under baseline | tests green; M028 killed when class flipped |

**M7 RECOVERY BOUNDARY = INTACT** (M10 still NOT STARTED)

**Evidence Record: R-M7**

- **Status:** PASS  
- **Conclusion:** M9 did not claim M10.

---

## 15. M8 Boundary

| Surface | Status |
|---|---|
| Differential system tests | 90 PASS |
| F-04 | remains OPEN (progress/review non-claims) |
| Generator/compare/shrink semantics redesigned in M9? | no evidence of redesign |

**M8 DIFFERENTIAL = INTACT**

**Evidence Record: R-M8**

- **Status:** PASS  
- **Conclusion:** M9 consumes M8; does not silently close F-04.

---

## 16. Determinism

| Axis | A vs B |
|---|---|
| Mutation IDs / order | identical M001…M042 |
| Terminal states | identical KILLED×42 |
| Kill-rate | 100% both |
| Critical flag | false both |
| Stage outcomes | identical rows |

U-35 theorem remains OPEN — operational reproducibility only.

**Evidence Record: R-DET**

- **Status:** PASS-DISCLOSED  
- **Evidence limitation:** U-35 OPEN  
- **Conclusion:** Campaign reproducible under review procedure.

---

## 17. M1–M8 Regression

```text
Command: cargo test --workspace --lib -- --test-threads=1
Revision: b5563db
Exit status: 0
```

Representative package results (from log):

| Surface | Lib tests |
|---|---|
| ror-core | 31 |
| ror-differential | 90 |
| ror-runtime | 106 |
| ror-persistence | 36 |
| ror-reference | 14 |
| ror-kernel | 8 |
| ror-host | 4 |
| ror-testkit | 10 |
| ror-agent | 2 |

No separate milestone binaries required; workspace lib suite covers M1–M8 modules (**FACT**).

**Evidence Record: R-REGRESSION**

- **Status:** PASS  
- **Conclusion:** M1–M8 green; no hidden filter disablement observed.

---

## 18. Dependency / Independence

| Edge / rule | Status |
|---|---|
| MOD-16 → testkit / mutations home | matches ownership matrix |
| `ror-testkit → ror-core` | allowed |
| `ror-differential → ror-testkit` | verification coupling (existing) |
| Production → mutation-engine | absent |
| Reference forbidden deps | absent |

**REFERENCE INDEPENDENCE = PASS**

**Evidence Record: R-DEP**

- **Status:** PASS  
- **Canonical authority:** dep/10-graph.json; mod/18; R-REF-02  
- **Conclusion:** No BLOCK-DEPENDENCY / BLOCK-INDEPENDENCE.

---

## 19. Unsafe / External Effects

| Check | Result |
|---|---|
| `#![forbid(unsafe_code)]` on machine crates + testkit | present |
| Campaign network | not required for mutant runs |
| Scratch FS only under /tmp | yes |
| Live tree residual mutants | none |

**Evidence Record: R-UNSAFE**

- **Status:** PASS  

---

## 20. Canonical Integrity

| Path | Modified by review? |
|---|---|
| `Red-on-Rust.md` `spec/` `final/` `reg/` `dep/` `mod/` `req/` `term/` | **NO** (review-only) |
| Production/mutation impl during review | **NO** |
| Sole review artifact | `docs/bootstrap/M9-REVIEW.md` |

| State | Value |
|---|---|
| R-REG | **184 × SPECIFIED** (`reg/requirements.json` count) |
| OADs | OPEN (final/09: 28 OPEN including U-02/U-08/U-09/U-17/U-21/U-35 …) |
| F-04 | OPEN / UNKNOWN (carried) |

**Evidence Record: R-CANON-INT**

- **Status:** PASS  

---

## 21. Evidence Limitations

| ID | Limitation |
|---|---|
| L-REV-INJECT | Operators are textual defect injections, not exhaustive AST mutation |
| L-REV-ORACLE | Targeted filters / package suites; not full R-TEST-07 tag scheduler |
| L-REV-DIFF-SUBSET | Differential leg subset per registry flags; M8 pure-CEK domain carried |
| L-REV-M036 | Document mutant + slightly weaker verify fallback path |
| L-REV-NO-PROOF | 42/42 is mutation evidence, not VERIFIED/PROVEN |
| L-REV-U35 | Determinism theorem OPEN |
| L-REV-HARNESS-SCOPE | Harness self-tests cover classification arithmetic & registry; not every conceivable contamination class as separate named tests |

None of the above are BLOCK-* under the acceptance bar for “mutation evidence with disclosed limitations.”

---

## 22. Non-Claims

This review **does not** claim:

- formal or semantic proof  
- VERIFIED / PROVEN / production readiness  
- OAD closure or R-REG promotion  
- M10 or M11 completion  
- that harness PASS alone implies MutationKillRate  
- that reference correctness is proven by differential kills  

```text
42/42 killed = mutation evidence (R-CLAIM-01), not mathematical proof of the calculus.
```

---

## 23. Final Classification

### Gate board

| Gate | Status |
|---|---|
| Identity / lineage | **PASS** |
| Canonical authority / derived registry | **PASS-DISCLOSED** |
| Harness implementation | **PASS** |
| Harness tests (Domain A) | **PASS** |
| Campaign dual run (Domain B) | **PASS** |
| State machine / kill-rate arithmetic | **PASS** |
| VERIFY-MUTATION | **PASS-DISCLOSED** |
| Scratch isolation | **PASS** |
| Kill oracles | **PASS-DISCLOSED** |
| Differential / reference independence | **PASS** |
| Critical mutants | **PASS** |
| M5 hinge | **PASS** |
| M7 / M8 boundaries | **PASS** |
| Determinism (operational) | **PASS-DISCLOSED** |
| M1–M8 regression | **PASS** |
| Workspace fmt/check/test/clippy | **PASS** |
| Dependencies | **PASS** |
| Unsafe / effects | **PASS** |
| Canonical integrity / R-REG / OAD | **PASS** |
| Documentation separation | **PASS** |

**BLOCKS = 0. Unresolved FAIL-* = 0.**

### Workspace commands (provenance)

```text
Command: cargo fmt --all -- --check
Revision: b5563db
Exit status: 0

Command: cargo check --workspace
Exit status: 0

Command: cargo test --workspace --lib -- --test-threads=1
Exit status: 0

Command: cargo clippy --workspace --all-targets -- -D warnings
Exit status: 0

Command: cargo clippy --workspace --all-targets --all-features -- -D warnings
Exit status: 0
```

(Historical M0–M8 gates used clippy without requiring separate feature matrices; both forms green.)

### Acceptance predicate

```text
no BLOCK-*
∧ no unresolved FAIL-*
∧ all registered non-equivalent mutants killed
∧ critical mutants all killed
∧ harness/campaign evidence separated
∧ reference independence intact
∧ M5 hinge intact
∧ M7 boundary intact
∧ M1–M8 regression green
∧ canonical state unchanged by review
```

**All hold** (with disclosed non-blocking limitations).

```text
M9 IMPLEMENTATION REVIEW = ACCEPTED WITH DISCLOSED EVIDENCE LIMITATIONS
```

---

## 24. Next State

```text
NEXT = M10 PREFLIGHT
```

**M10 is NOT started by this operation.**

---

## DELIVERABLE CHECKLIST

| ID | Deliverable | Status |
|---|---|---|
| D-01 | Identity evidence | **PASS** |
| D-02 | Canonical authority evidence | **PASS-DISCLOSED** |
| D-03 | Harness review | **PASS** |
| D-04 | Harness-test evidence | **PASS** |
| D-05 | Campaign evidence M001–M042 | **PASS** |
| D-06 | Kill-rate evidence (recomputed) | **PASS** |
| D-07 | Critical mutation evidence | **PASS** |
| D-08 | Security-hinge evidence | **PASS** |
| D-09 | Reference/differential evidence | **PASS** |
| D-10 | Determinism (dual campaign) | **PASS-DISCLOSED** |
| D-11 | M1–M8 regression | **PASS** |
| D-12 | Workspace gates | **PASS** |
| D-13 | Repository integrity | **PASS** |
| D-14 | Documentation evidence | **PASS** |
| D-15 | Final review report | **PASS** (this file) |

---

## Final state board

```text
M9 IMPLEMENTATION REVIEW = ACCEPTED WITH DISCLOSED EVIDENCE LIMITATIONS

M9 IMPLEMENTATION = COMPLETE

REGISTERED MUTANTS = 42

NON-EQUIVALENT = 42

KILLED = 42

SURVIVED = 0

EQUIVALENT = 0

INCONCLUSIVE = 0

NOT-RUN = 0

MUTATION KILL RATE = 100%

CRITICAL SURVIVED = NO

M5 HINGE = INTACT

M7 RECOVERY BOUNDARY = INTACT

M8 DIFFERENTIAL = INTACT

HARNESS / CAMPAIGN EVIDENCE SEPARATION = PASS

REFERENCE INDEPENDENCE = PASS

R-REG = 184 × SPECIFIED

OADs = OPEN

F-04 = OPEN

M10 = NOT STARTED

M11 = NOT STARTED

NEXT = M10 PREFLIGHT
```

---

*End of M9 IMPLEMENTATION REVIEW. Review-only artifact. No implementation changes. Do not start M10 in this operation.*
