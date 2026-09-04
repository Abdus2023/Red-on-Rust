# M8 Implementation Review — Differential System

**Operation ID:** `RATF-M8-REVIEW-001`  
**Operation type:** M8 IMPLEMENTATION REVIEW ONLY — no M9; no semantic repair; no OAD/R-REG promotion.  
**Repository:** `Abdus2023/Red-on-Rust`  
**Branch:** `arena/01a06993-red-on-rust`  
**Implementation under review:** `85304c4a875fa6276cb547970fad83ffc9002d04`  
**Authorized preflight:** `184538c4171909c116c76db66286961b74c64295`  
**M7 review baseline:** `2b565180b3d21699c4e4bcc49b70df704f4736da`  

```text
M8 IMPLEMENTATION REVIEW = ACCEPTED WITH DISCLOSED EVIDENCE LIMITATIONS
```

```text
NEXT = M9 PREFLIGHT
```

Evidence labels: **PASS** | **PASS-DISCLOSED** | **FAIL-*** | **BLOCK-***

---

## 1. Identity and lineage

| Item | Value | Status |
|---|---|---|
| `git rev-parse HEAD` | `85304c4a875fa6276cb547970fad83ffc9002d04` | FACT |
| Exact match to impl under review | **YES** (`HEAD == 85304c4`) | FACT |
| Post-`85304c4` semantic commits | **none** | FACT |
| Working tree | clean at review tip | FACT |
| `184538c` ancestor | YES | FACT |
| `2b56518` / `5a04630` / `61a9e57` ancestors | YES | FACT |
| `final/` `reg/` `dep/` `mod/` `spec/` vs preflight | **empty diff** (`184538c..85304c4`) | FACT |

**Lineage:**

```text
61a9e57  M7 PREFLIGHT
    ↓
5a04630  M7 IMPLEMENTATION
    ↓
2b56518  M7 REVIEW
    ↓
184538c  M8 PREFLIGHT
    ↓
85304c4  M8 IMPLEMENTATION  = HEAD under review
```

**R0 = PASS.**

---

## 2. Canonical authority

| Authority | Role |
|---|---|
| R-ORDER-02 | M8 acceptance: `Observe(P) == Observe(R)` |
| final/04 M8 row | generated programs, ref/prod exec, normalized comparison, first-divergence, shrinking |
| R-REF-01…06 | observe equality, independence, 12 areas, non-goals, normalize+first-div, PanicHost |
| R-TEST-02 | 16-field counterexample artifact (list + registry row) |
| R-TEST-03 | 10-priority shrink order |
| R-TEST-07 / R-TEST-12 | obligation tags; metrics ≠ oracle |
| R-TEST-01 / R-TEST-09 | modes / adjudication (supporting) |
| MOD-14 / MOD-15 | reference + differential homes |
| dep/10-graph.json | verification edges; forbidden reference edges |
| final/09 | U-02/U-17/U-32/U-35 OPEN; F-04 UNKNOWN in final/01 |

Historical Red-on-Rust.md “Phase 8” CEK material is **not** treated as M8 authority.

**R1 = PASS.**

---

## 3. Gate board (summary)

| Gate | Title | Status |
|---|---|---|
| R0 | Identity / lineage | **PASS** |
| R1 | Canonical authority | **PASS** |
| R2 | M8 scope surfaces | **PASS** |
| R3 | 16-field artifact | **PASS-DISCLOSED** |
| R4 | Generator determinism | **PASS** |
| R5 | Generator domain disclosure | **PASS-DISCLOSED** |
| R6 | Reference runner independence | **PASS** |
| R7 | Production runner | **PASS** |
| R8 | Observation normalization | **PASS-DISCLOSED** |
| R9 | Observation equality | **PASS** |
| R10 | First divergence | **PASS** |
| R11 | Shrinker | **PASS** |
| R12 | Shrink-predicate correctness | **PASS** |
| R13 | Coverage / evidence | **PASS** |
| R14 | M2–M7 integration | **PASS-DISCLOSED** |
| R15 | M5 security hinge | **PASS** |
| R16 | M7 recovery regression | **PASS** |
| R17 | Reference independence | **PASS** |
| R18 | Determinism | **PASS** |
| R19 | Differential test suite | **PASS** |
| R20 | Controlled divergence | **PASS** |
| R21 | Negative / fault agreement | **PASS** |
| R22 | Counterexample reproducibility | **PASS-DISCLOSED** |
| R23 | Harness integrity mutations | **PASS-DISCLOSED** |
| R24 | M9 boundary | **PASS** |
| R25 | M10/M11 boundary | **PASS** |
| R26 | OAD / F-04 governance | **PASS** |
| R27 | R-REG | **PASS** |
| R28 | Dependency authority | **PASS** |
| R29 | Unsafe / external effects | **PASS** |
| R30 | Workspace gates | **PASS** |
| R31 | M1–M7 regression | **PASS** |
| R32 | Documentation / non-claims | **PASS** |

**BLOCKS = 0. FAILS = 0.**  
≥1 **PASS-DISCLOSED** ⇒ final class below.

---

## 4. Scope (R2)

| Surface | Location | Present? |
|---|---|---|
| Generator | `system::generate` | YES |
| Reference runner | `system::run_reference` → m2 → `ror_reference::evaluate` | YES |
| Production runner | `system::run_production` → m2 → `ror_runtime::evaluate` | YES |
| Normalization | `NormalizedObservation` + `normalize` | YES |
| Comparator | `system::compare` | YES |
| First divergence | `DiffPath` / `FirstDivergence` / `first_divergence_report` | YES |
| Shrinker | `system::shrink` | YES |
| Counterexample artifact | `CounterexampleArtifact` | YES |
| Coverage/evidence | `CoverageEvidence` | YES |

**Not claimed / not present as M8 authority:** M9 kill-rate, M10 crash gate, M11 RC, OAD closure, R-REG promotion, production redesign.

**R2 = PASS.**

---

## 5. R-TEST-02 artifact verification (R3)

### Canonical list (final/01 R-TEST-02)

Comma-separated sentence yields **17** named slots including `minimized case`. Registry row labels the requirement **“16 fields”**. Implementation documents both: `canonical_field_names()` length **16** (through `first_divergence`) plus companion `minimized_case`.

| # | Canonical name | Impl field | Type | Population path | Notes |
|---|---|---|---|---|---|
| 1 | seed | `seed` | `u64` | `from_divergence` / gen | populated |
| 2 | generator_version | `generator_version` | `String` | const stamp | populated |
| 3 | semantic_version | `semantic_version` | `String` | provisional stamp | populated |
| 4 | test_case_version | `test_case_version` | `String` | const stamp | populated |
| 5 | program | `program` | `DiffProgram` | fd.program | populated |
| 6 | initial state | `initial_state` | `String` | empty default | **thin** pure-CEK |
| 7 | capabilities | `capabilities` | `String` | empty | thin |
| 8 | budgets | `budgets` | `String` | empty | thin |
| 9 | actor topology | `actor_topology` | `String` | empty | thin |
| 10 | scheduler_trace | `scheduler_trace` | `String` | empty | thin |
| 11 | host_trace | `host_trace` | `String` | empty | thin |
| 12 | persistence image | `persistence_image` | `Vec<u8>` | empty | thin |
| 13 | crash_trace | `crash_trace` | `String` | empty | thin |
| 14 | production_observation | `production_observation` | `NormalizedObservation` | fd | populated |
| 15 | reference_observation | `reference_observation` | `NormalizedObservation` | fd | populated |
| 16 | first_divergence | `first_divergence` | `Option<Difference>` | fd | populated |
| 17 | minimized case | `minimized_case` | `Option<DiffProgram>` | shrink result | populated when shrunk |

**No missing names. No invented substitutes.** Empty middle fields are **honest thin encodings** for pure-CEK cases (N/A domains), not silent omission of the schema.

**Counting ambiguity (16 registry vs 17 list items including minimized)** is a **canonical wording residual**, not an impl defect — all listed content is present on the struct.

**R3 = PASS-DISCLOSED.**

---

## 6. Generator (R4 / R5)

| Check | Result |
|---|---|
| same seed → same program | PASS (`same_seed_same_program`) |
| Explicit seed / LCG | PASS — no wall-clock / env / HashMap order |
| Domain | M2/M3 pure CEK (Value/Var/Let/Seq/If/Lambda/Call) |
| Generator as authority | NO — test mechanism only |

**Domain vs M8 mandate:** R-ORDER-02 requires Observe equality; final/04 requires generation + both executions + compare + first-div + shrink. R-TEST-01 exhaustive baseline is `depth≤4, actors≤2, caps≤2` — pure-CEK generation within depth bounds is a **canonically sufficient bounded domain**. M4–M7 remain pairwise modules (honest disclosure). Broader generation is desirable, not a hidden mandatory gap that converts disclosure into FAIL.

**R4 = PASS. R5 = PASS-DISCLOSED.**

---

## 7. Runners (R6 / R7)

| Side | Path | Independence |
|---|---|---|
| Reference | `run_reference` → `observe_reference` → `ror_reference::evaluate` | `ror-reference` → `ror-core` only |
| Production | `run_production` → `observe_production` → `ror_runtime::evaluate` | real production CEK |

No second CEK inside differential. No production transition shared into reference.

Forbidden edges absent (`present: false` in dep graph; import scan clean).

**R6 = PASS. R7 = PASS. R17 = PASS.**

---

## 8. Normalization / F-04 (R8)

| Rule | Class |
|---|---|
| Terminal Halted/Fault only for pure-CEK system observe | **PROVISIONAL** (F-04) |
| Exclude addresses / allocator / OS handles | **CANONICAL** (R-REF-05) |
| Do not claim Observed\* freeze | **PASS** (module docs + progress) |
| Side label on observation | implementation metadata; compare uses `terminal` |

Normalization does **not** collapse Halted↔Fault or distinct values/faults into Equal.

**R8 = PASS-DISCLOSED. F-04 remains OPEN / UNKNOWN.**

---

## 9. Comparator & first divergence (R9 / R10 / R20)

| Case | Result |
|---|---|
| equal observations → Equal | PASS |
| Halted value mismatch → Diverged `HaltedValue` | PASS |
| Halted vs Fault → Diverged `TerminalKind` **before** payload | PASS |
| Fault mismatch → Diverged `Fault` | PASS |
| Stable labels (not raw Debug addresses) | PASS (`value_label` / `fault_label`) |
| Controlled fixture divergence without prod bug | PASS (observation fixtures) |

**R9 = PASS. R10 = PASS. R20 = PASS.**

---

## 10. Shrinker (R11 / R12)

| Check | Result |
|---|---|
| Predicate must hold to retain | PASS |
| Complexity decreases when progress | PASS |
| Deterministic re-shrink | PASS |
| pred fails → `preserved_divergence=false` | PASS |
| Termination bound (64 iters) | PASS |
| No uncontrolled randomness | PASS |

R-TEST-03 priorities **1,5–10** (actors, mailbox, caps, budget, WAL, effects, crash) are **no-ops** on pure-CEK programs — disclosed mapping of (2)(3)(4) to structural expr shrink.

**R11 = PASS. R12 = PASS** (with domain-mapped priorities as disclosure under R5/R14).

---

## 11. Coverage / evidence (R13)

`CoverageEvidence` tracks generated / reference_executed / production_executed / equal / divergent / shrunk / failed / not_run / tags.

Docs state metrics ≠ proof / ≠ oracle (R-TEST-07). No “formal equivalence proven” claim in progress.

**R13 = PASS.**

---

## 12. M2–M7 integration (R14)

| Layer | Role |
|---|---|
| `system` | Common orchestration for **generated pure-CEK** pipeline |
| `m2`…`m7` | Unchanged pairwise milestone diffs (still executed) |

M8 does **not** rewrite M4–M7 into the generator. Integration = coexistence + regression green + m2 observe reuse for runners — **not** a single mega-generator over all domains.

Compatible with preflight “unify under system APIs without altering pairwise semantics.”

**R14 = PASS-DISCLOSED.**

---

## 13. Security: M5 hinge & host surface (R15)

| Check | Result |
|---|---|
| `HostInvoked ⇒ DurableIssued` | M5 `effects::` 9/9 including `persist_fail_no_host` |
| Host-before-Issued panic | m5 differential should-panic still green |
| Generator → Host | **none** |
| Reference → Host | **none** |
| Comparator / shrinker → Host | **none** |
| `system` host API | no Host parameters (`no_host_surface_in_system_api`) |

**R15 = PASS** (CRITICAL).

---

## 14. M7 recovery regression (R16)

`m7::` differential 5/5: T1 Discard, T2 Indeterminate, T5 Completed, T6 snapshot, empty.  
Persistence crash matrix remains green (34 tests). M8 did not alter recovery semantics.

**R16 = PASS.**

---

## 15. Determinism (R18)

| Check | Result |
|---|---|
| seed → program | PASS |
| program → observations | PASS (prod/ref CEK deterministic) |
| observations → compare | PASS |
| shrink repeat | PASS |
| `determinism_full_pipeline` | PASS |

**R18 = PASS.**

---

## 16. Test suite execution (R19 / R30 / R31)

| Command | Result |
|---|---|
| `cargo fmt --all -- --check` | exit **0** |
| `cargo check --workspace` | exit **0** |
| `cargo test --workspace --lib` | exit **0** |
| `cargo clippy --workspace --all-targets -- -D warnings` | exit **0** |
| `system::` tests | **15 passed / 0 failed / 0 ignored** |
| differential crate | **90 passed** |
| runtime lib | **96 passed** (M5 hinge subset 9/9) |
| persistence lib | **34 passed** |
| m5 differential | **12 passed** |
| m7 differential | **5 passed** |

Progress-doc counts **independently reproduced**. No NOT-RUN counted as PASS.

**R19 = PASS. R30 = PASS. R31 = PASS.**

---

## 17. Negative / fault agreement (R21)

| Case | Result |
|---|---|
| Unbound variable both sides | `negative_unbound_agrees` PASS |
| Fault labels structured | `fault_label` discriminants |
| M5 unauthorized / budget deny agree | m5 suite PASS |

**R21 = PASS.**

---

## 18. Counterexample reproducibility (R22)

Artifact carries seed, program, both observations, first_divergence, optional minimized_case.  
Reproduction path: re-run `run_case` on `program` / re-`generate(seed)` for seeded cases.

Thin empty context fields do not block pure-CEK reproduction of terminal divergence. Full multi-domain artifact round-trip (WAL image, actor topology, …) **not** exercised end-to-end in M8 tests — disclosed.

**R22 = PASS-DISCLOSED.**

---

## 19. Harness integrity mutations (R23)

| Intent | Result |
|---|---|
| Alter one observation | **KILLED** (`harness_mutation_intent_alter_observation_detected`) |
| Shrink without pred | **KILLED** (`shrink_does_not_claim_success_if_pred_fails`) |
| Full M9 registry campaign | **NOT-RUN** (out of scope) |

**R23 = PASS-DISCLOSED.**

---

## 20. Milestone boundaries (R24 / R25)

```text
M9 = NOT STARTED
M10 = NOT STARTED
M11 = NOT STARTED
```

No global mutation kill-rate gate; no new crash-consistency framework; no RC framework.

**R24 = PASS. R25 = PASS.**

---

## 21. OAD / F-04 / R-REG (R26 / R27)

| Item | Status |
|---|---|
| F-04 Observed* | **OPEN/UNKNOWN** — provisional schema only |
| U-02 / U-17 / U-32 / U-35 | **OPEN** (final/09) |
| R-REG | **184 × SPECIFIED** (`reg/requirements.json`) |
| final/reg/dep/mod/spec edits by M8 | **none** |

**R26 = PASS. R27 = PASS.**

---

## 22. Dependencies / unsafe (R28 / R29)

| Check | Result |
|---|---|
| reference → core only | PASS |
| differential verification edges | PASS (pre-existing) |
| forbidden reference→prod edges | absent |
| `#![forbid(unsafe_code)]` | present on differential + reference |
| fs/net/process/Command | **none** in M8 paths |

**R28 = PASS. R29 = PASS.**

---

## 23. Documentation honesty (R32)

`M8-PROGRESS.md` states COMPLETE WITH DISCLOSED EVIDENCE LIMITATIONS, lists non-claims (no formal proof, OADs open, M9–M11 not started). No “proven equivalence” or “OAD resolved” claims.

**R32 = PASS.**

---

## 24. Critical invariant summary

| Invariant | Result |
|---|---|
| `Observe(P) == Observe(R)` (implemented acceptance relation) | **PASS** on pure-CEK generated domain + pairwise M2–M7 |
| Production Semantics ≠ Reference Implementation | **PASS** |
| `HostInvoked(E) ⇒ DurableIssued(E)` | **PASS** |
| Recovery ↛ original-effect re-execution | **PASS** |
| Generator ↛ Authority | **PASS** |
| Differential ↛ Host bypass | **PASS** |
| F-04 remains OPEN | **PASS** |

---

## 25. Selected evidence records

### Evidence Record: R0

- **Gate:** Identity / lineage  
- **Status:** PASS  
- **Canonical authority:** process lineage  
- **Implementation location:** git `85304c4`  
- **Observed result:** HEAD exact; ancestors OK; no post-impl drift  
- **Security relevance:** HIGH  
- **Evidence class:** OTHER  
- **Evidence limitation:** NONE  
- **OAD impact:** NONE  
- **R-REG impact:** NONE — remains SPECIFIED  
- **Reviewer conclusion:** Authorized implementation tip confirmed.

### Evidence Record: R3

- **Gate:** R-TEST-02 counterexample artifact  
- **Status:** PASS-DISCLOSED  
- **Canonical authority:** final/01 R-TEST-02; final/03 row “16 fields”  
- **Canonical rule:** structured reproducible artifact with listed slots  
- **Implementation location:** `CounterexampleArtifact`  
- **Implementation behavior:** all list names present; minimized companion; thin empty N/A fields for pure-CEK  
- **Test / evidence:** `artifact_has_sixteen_canonical_names`, `artifact_from_divergence_fills_fields`  
- **Observed result:** schema complete; population thin on context fields  
- **Security relevance:** MEDIUM  
- **Evidence class:** IMPLEMENTATION + TEST  
- **Evidence limitation:** 16-vs-17 wording residual; pure-CEK empty traces  
- **OAD impact:** F-04 / domain thinness  
- **R-REG impact:** NONE  
- **Reviewer conclusion:** Conforms with disclosed thin encodings; not FAIL.

### Evidence Record: R5

- **Gate:** Generator domain  
- **Status:** PASS-DISCLOSED  
- **Canonical authority:** R-ORDER-02; R-TEST-01 exhaustive bounds; final/04  
- **Canonical rule:** generation + Observe equality; bounded exhaustive OK  
- **Implementation location:** `generate` pure CEK  
- **Observed result:** M2/M3 domain; M4–M7 pairwise retained  
- **Security relevance:** LOW  
- **Evidence class:** IMPLEMENTATION  
- **Evidence limitation:** not a full multi-domain generator  
- **OAD impact:** NONE  
- **R-REG impact:** NONE  
- **Reviewer conclusion:** Canonically sufficient bounded domain; disclosure honest.

### Evidence Record: R8

- **Gate:** Normalization / F-04  
- **Status:** PASS-DISCLOSED  
- **Canonical authority:** R-REF-05; F-04 UNKNOWN  
- **Canonical rule:** normalized observations; domain types undeclared  
- **Implementation location:** `NormalizedObservation`  
- **Observed result:** provisional terminal schema; F-04 not claimed closed  
- **Security relevance:** HIGH  
- **Evidence class:** IMPLEMENTATION  
- **Evidence limitation:** F-04 OPEN  
- **OAD impact:** F-04  
- **R-REG impact:** NONE  
- **Reviewer conclusion:** Conservative provisional path; governance intact.

### Evidence Record: R15

- **Gate:** M5 hinge  
- **Status:** PASS  
- **Canonical authority:** R-DUR-01; GI-SEC-07; R-REF-06  
- **Canonical rule:** Host only after DurableIssued  
- **Implementation location:** M5 pipeline; M8 system has no host  
- **Test / evidence:** runtime effects 9/9; m5 host-before-Issued panic  
- **Observed result:** hinge intact; no M8 bypass  
- **Security relevance:** CRITICAL  
- **Evidence class:** TEST  
- **Evidence limitation:** NONE on hinge  
- **OAD impact:** NONE  
- **R-REG impact:** NONE  
- **Reviewer conclusion:** No BLOCK-SECURITY.

### Evidence Record: R17

- **Gate:** Reference independence  
- **Status:** PASS  
- **Canonical authority:** R-REF-02; R-SCOPE-04; dep forbidden edges  
- **Implementation location:** `ror-reference` Cargo + runners  
- **Observed result:** core-only; separate evaluate  
- **Security relevance:** CRITICAL  
- **Evidence class:** IMPLEMENTATION  
- **Evidence limitation:** NONE  
- **OAD impact:** NONE  
- **R-REG impact:** NONE  
- **Reviewer conclusion:** No BLOCK-INDEPENDENCE.

### Evidence Record: R30

- **Gate:** Workspace gates  
- **Status:** PASS  
- **Observed result:** fmt/check/test/clippy all exit 0; system 15/15; differential 90  
- **Security relevance:** MEDIUM  
- **Evidence class:** TEST  
- **Evidence limitation:** NONE  
- **OAD impact:** NONE  
- **R-REG impact:** NONE  
- **Reviewer conclusion:** Gates independently reproduced.

---

## 26. Evidence limitations (aggregate)

| ID | Limitation |
|---|---|
| F-04 | Observed* UNKNOWN — provisional `NormalizedObservation` |
| L-M8-PURE-GEN | Generator is pure-CEK; M4–M7 pairwise not generated |
| L-M8-ARTIFACT-THIN | Context/trace/image fields empty on pure-CEK artifacts |
| L-M8-SHRINK-MAP | R-TEST-03 actor/WAL/crash priorities no-op on pure expr |
| L-M8-16-VS-17 | Registry “16 fields” vs comma list including minimized (17 tokens) |
| L-M8-NO-PROOF | Agreement is evidence, not formal proof |
| L-M8-HARNESS-MUT | Only local integrity mutations; not M9 campaign |
| U-02/U-17/U-32/U-35 | Carry OPEN |
| M5–M7 carry | prior disclosures remain |

---

## 27. Defects found

| ID | Severity | Disposition |
|---|---|---|
| — | — | **No FAIL-IMPLEMENTATION or FAIL-TEST** |
| — | — | **No BLOCK-*** |

No silent semantic repairs performed. Review-only documentation added.

---

## 28. Explicit non-claims

```text
Observe equality is not formally proven.
F-04 is not resolved.
OADs are not closed.
R-REG remains 184 × SPECIFIED.
Generator domain is not full multi-milestone generation.
Differential agreement is evidence, not proof.
M9 mutation kill-rate is not started.
M10 / M11 are not started.
M8 review does not implement M9.
```

---

## 29. Final classification

### Aggregation

- BLOCK-* = **0**  
- FAIL-* = **0**  
- PASS-DISCLOSED ≥ 1 →  

```text
M8 IMPLEMENTATION REVIEW = ACCEPTED WITH DISCLOSED EVIDENCE LIMITATIONS
```

### Next operation

Mandatory security/authority gates (R0, R6, R15, R17, R26, R27, R28, R29) are **PASS**. Disclosures are domain/schema/evidence-depth limitations, not blocks.

```text
NEXT = M9 PREFLIGHT
```

### Final state board

```text
M0–M4                      prior accepted
M5                         ACCEPTED WITH DISCLOSED EVIDENCE LIMITATIONS
M6                         ACCEPTED WITH DISCLOSED EVIDENCE LIMITATIONS
M7                         ACCEPTED WITH DISCLOSED EVIDENCE LIMITATIONS
M8 preflight               GREEN WITH DISCLOSED LIMITATIONS — IMPLEMENTATION AUTHORIZED
M8 implementation          85304c4 COMPLETE WITH DISCLOSED EVIDENCE LIMITATIONS
M8 implementation review   ACCEPTED WITH DISCLOSED EVIDENCE LIMITATIONS
R-REG                      184 × SPECIFIED
NEXT                       M9 PREFLIGHT
```

---

*End of M8 IMPLEMENTATION REVIEW. Do not begin M9 in this operation.*
