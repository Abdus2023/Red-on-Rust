# M9 PREFLIGHT

**Operation ID:** `RATF-M9-PREFLIGHT-001`  
**Operation type:** M9 PREFLIGHT ONLY — read-only authorization; no mutation operators; no OAD/R-REG promotion; no M9/M10/M11 implementation.  
**Repository:** `Abdus2023/Red-on-Rust`  
**Branch:** `arena/01a06993-red-on-rust`  

```text
M9 PREFLIGHT = GREEN WITH DISCLOSED LIMITATIONS
IMPLEMENTATION AUTHORIZATION = AUTHORIZED
M9 IMPLEMENTATION = NOT STARTED
NEXT = M9 IMPLEMENTATION
```

Evidence labels: **FACT** | **DERIVED** | **DISCLOSED LIMITATION** | **PASS** | **PASS-DISCLOSED** | **BLOCK-***

---

## 1. Identity and Lineage

| Item | Value | Class |
|---|---|---|
| HEAD | `abdfb5579d7b90f1143be84e28c561ddcdebde1a` | FACT |
| Working tree at start | clean (only this report added) | FACT |
| M8 review commit | `abdfb55` | FACT |
| M8 implementation | `85304c4` | FACT |
| M8 preflight | `184538c` | FACT |
| M7 review | `2b56518` | FACT |
| M7 implementation | `5a04630` | FACT |
| M7 preflight | `61a9e57` | FACT |
| All expected SHAs ancestors of HEAD | YES | FACT |
| HEAD == `abdfb55` | YES | FACT |
| Toolchain | `ror-stable` rustc/cargo 1.88.0 | FACT |

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
85304c4  M8 IMPLEMENTATION
    ↓
abdfb55  M8 REVIEW  = HEAD
```

**No production/canonical semantic files modified by this preflight** (sole artifact: this report).

---

## 2. M8 Accepted Baseline

| Check | Result |
|---|---|
| M8 review classification | **ACCEPTED WITH DISCLOSED EVIDENCE LIMITATIONS** (`docs/bootstrap/M8-REVIEW.md`) |
| M8 NEXT | M9 PREFLIGHT |
| BLOCK-* / FAIL-* on M8 | **none** |
| M9 implemented inside M8 | **no** |
| M10/M11 touched by M8 | **no** |
| F-04 | remains **OPEN/UNKNOWN** |
| OADs U-02/U-17/U-32/U-35 | remain **OPEN** |
| R-REG | **184 × SPECIFIED** |

**Carried M8 disclosures (not resolved):**

- pure-CEK generator domain (M4–M7 pairwise)
- provisional `Observed*` / F-04
- thin R-TEST-02 context fields on pure-CEK artifacts
- 16-vs-17 artifact wording residual
- differential agreement = evidence, not proof

**G-M8-BASELINE = PASS.**

---

## 3. Canonical M9 Authority

| Source | Statement | Class |
|---|---|---|
| **R-ORDER-02** / `final/01` milestone table | **M9 Mutation gate** — acceptance: baseline mutation registry kill rate target satisfied | **CANONICAL** |
| **final/04** verification registry | **M9** \| `MutationKillRate = 100%` (registered non-equivalent) | **CANONICAL** |
| **mod/18-ownership-matrix.md** | M9 → **MOD-16 MUTATION** | **CANONICAL** |
| **mod/16-mutation.md** | Owns R-TEST-04/05/06; M9 gate; registry; kill evidence via MOD-15 | **CANONICAL** |
| **R-TEST-04** | Baseline registry M001–M018; additive through M042 | **CANONICAL** |
| **R-TEST-05** | `MutationKillRate = 100%` non-equivalent; survivors release-blocking; equivalents adjudicated | **CANONICAL** |
| **R-TEST-06** | Per mutant: inject → build → targeted test → differential → assert killed | **CANONICAL** |
| **R-TEST-11** (M11 conjunct) | kill-rate is one of three final acceptance conjuncts — **not** sole M9 deliverable for M11 | **CANONICAL** (boundary) |
| final/04 evidence note | Registry SPECIFIED; **no machine mutant executed/killed yet**; 100% is target not current fact | **CANONICAL** (baseline fact) |
| Historical phase numbering | — | **HISTORICAL** / non-authority for M9 |

**What M9 is (frozen):**

```text
M9 — Mutation gate
Acceptance: MutationKillRate = 100% over registered non-equivalent mutants
(with equivalent-mutant adjudication documented)
```

**Primary homes:** MOD-16 (`mutations/` registry pointer + `ror-testkit` injection); kill evidence via MOD-15 differential; CI/adjudication hooks MOD-17 (process).

---

## 4. Canonical M9 Requirements

| ID | Obligation (short) | Home | M9 role |
|---|---|---|---|
| R-TEST-04 | Versioned baseline M001–M018; additive; killed mutants remain regression | MOD-16 | **registry authority** |
| R-TEST-05 | Kill rate 100% non-equivalent; survivors block; equivalents adjudicate | MOD-16 / M9 gate | **acceptance** |
| R-TEST-06 | Inject/build/targeted+differential assert kill; do not only “run framework” | MOD-16 + testkit | **method** |
| R-ORDER-02 | M9 row in milestone acceptance | process | **milestone name** |
| R-REPO-02/03 | testkit / mutations contract; structural boundary enforcement | workspace | **placement** |
| R-CLAIM-01/02 | Do not claim kill-rate without evidence; no prohibited shortcuts | governance | **discipline** |
| R-TEST-07 | Obligation tags; metrics ≠ oracle (mutation coverage attaches tags) | MOD-15 | **evidence tagging** |
| R-TEST-09 | 4-way adjudication (incl. equivalents / ambiguity) | MOD-17 | **survivor/equiv process** |
| R-TEST-10 | Nightly/release stages include mutation registry | MOD-17 | **CI staging** (thin local runner OK for M9 code) |

Supporting regression targets (not redefinition of M9): obligations each mutant **violates** live in target modules (CEK, cap, budget, effect, actor, persist, …) — listed in final/04 §2 and mod/18 §5.

---

## 5. Canonical M9 Mutation Obligations

### 5.1 Authority state: **A — Canonical mutation registry exists**

Frozen content in `final/01` R-TEST-04 and `final/04` §2 (M001–M042).  
Repository pointer: `mutations/registry.toml` (**file not present yet** — SPECIFIED content, implementation N/YI).

### 5.2 Baseline frozen set (R-TEST-04) — M001–M018

| ID | Defect (canonical short) | Primary obligation tags / targets |
|---|---|---|
| M001 | reverse argument evaluation | R-CEK-05 LTR |
| M002 | skip arity precheck | R-CEK-05 |
| M003 | allow non-function application | R-CEK-05 |
| M004 | accept revoked capability | R-CAP-07, R-CORE-03 |
| M005 | omit capability ceiling | R-CAP-06 |
| M006 | permit capability amplification | R-CAP-05, R-CORE-04 |
| M007 | omit budget gate | R-BUDGET-04/08 |
| M008 | release indeterminate escrow | R-DUR-05 |
| M009 | permit negative resources | R-BUDGET-02 |
| M010 | allocate EffectId before authorization | R-EFFECT-03/04 (**hinge-adjacent**) |
| M011 | schedule blocked actor | R-ACTOR-04 |
| M012 | duplicate runnable queue entry | R-ACTOR-04 |
| M013 | break mailbox FIFO | R-ACTOR-06 |
| M014 | accept duplicate canonical map key | R-CANON-06 |
| M015 | ignore WAL sequence gap | R-PERSIST-06 |
| M016 | ignore checksum mismatch | R-PERSIST-02 |
| M017 | accept mismatched EffectDigest | R-EFFECT-06, R-DUR-03 |
| M018 | resume after corrupted receipt | R-EFFECT-06 |

### 5.3 Additive post-audit set (still registry content) — M019–M042

Includes (non-exhaustive listing for preflight; full table in final/04 §2):  
M019–M023 (receipt authority, unmarshal, recovery revocation), M024–M025 (marshal/spawn), M026–M029 (planner/recon/host digest), M030–M035 (constraint, mailbox, core-12, escrow), M036 (document-layer detector — tooling), M037–M038 (durability/issuance), M039–M042 (budget/time/quiescence).

**M9 implementation MUST treat the full registered non-equivalent set as the kill-rate denominator** once machine injection exists — not only M001–M018 — unless a canonical adjudication carves equivalents. Baseline freeze does **not** exclude additives from R-TEST-05.

**Document mutant M036** is measurable under repository checker gates (final/04); **machine mutants** are the M9 code-path obligation (currently unmeasured).

### 5.4 Registry rules

- **Additive:** previously killed mutant remains permanent regression (R-TEST-04).  
- **IDs stable** in final/04 map.  
- Implementation MUST NOT invent normative IDs outside governance addenda.

---

## 6. M9 Scope

| Area | M9 status | Authority |
|---|---|---|
| Mutation-testing framework (inject/build/run/assert) | **IN** | R-TEST-06; mod/16 |
| Mutation target registry materialization | **IN** (from frozen SPECIFIED text) | R-TEST-04; final/04 |
| Kill-rate computation over non-equivalent registered set | **IN** | R-TEST-05 |
| Security-/invariant-critical mutants (incl. hinge-class) | **IN** | registry + GI-SEC / R-DUR-01 |
| Kill evidence via differential + targeted tests | **IN** | R-TEST-06; MOD-15 |
| M1–M8 regression as harness substrate | **IN** (must stay green) | R-TEST-04 additive; prior milestones |
| Equivalence adjudication documentation | **IN** | R-TEST-05; R-TEST-09 |
| `ror-testkit` injection infrastructure | **IN** | R-REPO-02; mod/16 |
| Thin local runner / evidence artifacts | **IN** | DERIVED from R-TEST-06 |

---

## 7. M9 Non-Scope

| Area | Disposition | Authority |
|---|---|---|
| **M10** crash-injection **gate** (T0–T6 acceptance as milestone) | **OUT** | R-ORDER-02 M10; R-TEST-08 |
| Crash/process-kill harness as M10 product | **OUT** of M9 milestone (mutants *about* recovery code may still be injected as **code mutants**, not a crash-matrix campaign) | R-ORDER-02 separation |
| **M11** RC / full acceptance triad | **OUT** | R-ORDER-02 M11; R-TEST-11 |
| OAD closure | **OUT** | governance |
| R-REG promotion to IMPLEMENTED/TESTED/VERIFIED/PROVEN | **OUT** | final/08; R-CLAIM |
| Canonical specification edits | **FORBIDDEN** | authority hierarchy |
| Redesign M5/M6/M7/M8 production semantics | **OUT** | upstream accepted |
| Claiming formal proof from kills | **OUT** | R-REF-01 / evidence model |
| Weakening reference independence to kill mutants | **FORBIDDEN** | R-REF-02 |
| Inventing unregistered normative mutants | **OUT** (additives only via governance) | R-TEST-04 |

---

## 8. Mutation Result Taxonomy

Canonical language (R-TEST-05/06 + final/04 practice):

| State | Meaning | Must not collapse into |
|---|---|---|
| **Intended / Registered** | ID in frozen registry | — |
| **Generated / Injected** | mutant applied to build | — |
| **Executed** | targeted + differential suites run | — |
| **Killed** | tests detect defect; assert fails on mutant / oracle catches | — |
| **Survived** | non-equivalent mutant not detected | ≠ Not-Run |
| **Equivalent** | behavior same as original under adjudication | ≠ Killed without docs |
| **Not-Run** | not injected or suites not executed | ≠ Killed |
| **Inconclusive** | build/infra failure, ambiguous oracle | ≠ Killed |

```text
NOT-RUN ≠ KILLED
SURVIVED ≠ NOT-RUN
EQUIVALENT ≠ KILLED
INCONCLUSIVE ≠ KILLED
```

**M9 MUST record these distinctions in evidence artifacts.**

---

## 9. Critical Mutation Rules

| Class | Examples (registry) | Disposition if survives (non-equivalent) |
|---|---|---|
| Security / trust-boundary | M004–M006, M010, M017–M023, M028, M037 | **BLOCK verification / release-blocking** (R-TEST-05) |
| M5 hinge-class | M010 (EffectId before auth); any host-before-Issued style | **CRITICAL** — must kill; preserve `HostInvoked ⇒ DurableIssued` |
| Recovery integrity | M015, M016, M023, M028, M029 | **CRITICAL** — no silent repair / no Indeterminate→NotExecuted local |
| Determinism / scheduler | M011–M013 | mandatory kill |
| Durability payload | M038 | mandatory kill |

```text
Surviving non-equivalent registered mutant ⇒ verification blocked (R-TEST-05)
```

Do **not** weaken because injection is hard. Do **not** treat survival as documentation-only.

---

## 10. M5 Security Hinge

```text
HostInvoked(E) ⇒ DurableIssued(E)     (R-DUR-01 / GI-SEC-07 / R-CORE-06)
```

| Rule for M9 | Status |
|---|---|
| Must not redesign M5 pipeline | required |
| Mutants must not introduce alternate host path that becomes “accepted” | required |
| M010 and related gate-order mutants must be killed | required |
| Baseline M5 tests remain green under unmutated tree | verified this preflight (effects 9/9) |

**G-M5-HINGE = PASS** (baseline intact; M9 must preserve).

---

## 11. M7 Recovery Boundary

| Item | Disposition |
|---|---|
| M7 production recovery semantics | **upstream input** — do not redesign |
| Mutants targeting persist/recovery (M015/M016/M023/M028/…) | **IN M9** as registry obligations |
| M10 crash-matrix **milestone gate** | **OUT of M9** |
| Indeterminate ≠ NotExecuted | preserved; M028 must kill silent local NotExecuted |
| Recovery ↛ original effect re-exec | preserved |

**G-M7-BOUNDARY = PASS.**

---

## 12. M8 Differential Boundary

| Item | Disposition |
|---|---|
| M8 system + pairwise diffs | **kill-evidence substrate** (R-TEST-06) |
| Production ≠ Reference | mandatory |
| Must not patch reference to kill mutant | forbidden (R-TEST-09 / R-REF-02) |
| Pure-CEK generator domain limitation | **carried disclosure** — may require targeted tests beyond generator for full registry |

**G-M8-BOUNDARY = PASS-DISCLOSED.**

---

## 13. Reference Independence

| Edge | Required | Observed |
|---|---|---|
| `ror-reference ↛ ror-runtime` | forbidden | absent |
| `ror-reference ↛ ror-kernel` | forbidden | absent |
| `ror-reference ↛ ror-persistence` | forbidden | absent |
| `ror-reference ↛ ror-host` | forbidden | absent |
| `ror-reference ↛ ror-agent` | forbidden | absent |
| `ror-reference → ror-core` | required | present |

M9 injection must target **production** (or isolated mutant builds), not fold production transitions into reference.

**G-REF = PASS.**

---

## 14. Dependency Validation

| Concern | Classification |
|---|---|
| MOD-16 → MOD-15 (kill evidence) | VERIFICATION — allowed |
| MOD-16 → MOD-17 (testkit/CI) | VERIFICATION — allowed |
| `ror-testkit` injection home | REQUIRED by mod/16 pointer |
| `mutations/registry.toml` | SPECIFIED home; **absent file** = M9 impl gap, not preflight block |
| New production semantic edges | not required for M9 |
| Forbidden reference edges | must remain absent |

**Convention:** provider → consumer means consumer depends on provider.

**G-DEP = PASS** (no forbidden edge proposed).

---

## 15. Determinism

| Requirement | Source | M9 duty |
|---|---|---|
| Stable mutant ID | R-TEST-04 | use registry IDs |
| Reproducible inject + run | R-TEST-06; R-CORE-08 spirit | seed/config recorded |
| No wall-clock mutation selection | DERIVED | ordered registry iteration |
| Stable evidence artifacts | DERIVED | deterministic serialization |
| U-35 | OPEN | operational det. only; no theorem claim |

**G-DET = PASS-DISCLOSED** (U-35).

---

## 16. Mutation Identity

| Rule | Authority |
|---|---|
| IDs M001–M042 stable in final/04 | FACT |
| Unique per defect definition | R-TEST-04 |
| Additive: do not reuse ID for changed semantics without governance | R-TEST-04 / R-SCOPE-03 |
| Do not invent IDs in impl | preflight rule |

**G-ID = PASS.**

---

## 17. Evidence Model

| Class | M9 produces? |
|---|---|
| Implementation evidence | framework + registry materialization |
| Test evidence | targeted kills |
| Differential evidence | R-TEST-06 differential leg |
| Mutation evidence | kill/survive/equiv/not-run records |
| Crash-matrix evidence | **M10** (not M9 gate) |
| Proof evidence | **no** |

```text
Kill ≠ VERIFIED ≠ PROVEN
R-REG remains SPECIFIED unless separate governance promotes
```

final/08: repository evidence NONE at compilation time for machine mutants — M9 **creates** mutation evidence without auto-promoting R-REG.

**G-EVIDENCE = PASS.**

---

## 18. M10 Boundary

| Activity | M9? | M10? |
|---|---|---|
| Code mutant: ignore WAL gap (M015) | **YES** (inject mutant) | — |
| Full T0–T6 crash-injection **gate** | **NO** | **YES** (R-ORDER-02 / R-TEST-08) |
| Process kill / crash harness product | **NO** | **YES** |
| Recovery classification exactness campaign | **NO** as milestone | **YES** |

**G-M10 = PASS.**

---

## 19. M11 Boundary

M9 MUST NOT declare RC readiness, production readiness, close OADs, promote R-REG, or claim R-TEST-11 complete (needs Observe equality **and** kill-rate **and** recovery equality).

**G-M11 = PASS.**

---

## 20. OAD State

| ID | Status | M9 impact |
|---|---|---|
| F-04 Observed* | OPEN/UNKNOWN | differential kill leg may use provisional observe — do not close |
| U-02 / U-17 / U-32 | OPEN | persist mutants use M7 provisional codecs |
| U-35 | OPEN | det. operational only |
| U-08 / U-09 / U-21 / U-31 | OPEN as applicable | fault/label/encode residuals — do not close |
| Others | per final/09 | no silent closure |

**If impl requires OAD freeze:** would be **BLOCK-GOVERNANCE** — preflight forbids.

**G-OAD = PASS.**

---

## 21. R-REG State

```text
requirement_count = 184
status = 184 × SPECIFIED
```

Sources: `reg/requirements.json`; `final/08-evidence-status-matrix.md`.

**No promotions in this preflight.**

**G-RREG = PASS.**

---

## 22. Baseline Test Results

| Command | Exit | Notes |
|---|---|---|
| `cargo fmt --all -- --check` | **0** | |
| `cargo check --workspace` | **0** | |
| `cargo test --workspace --lib` | **0** | all member crates |
| `cargo clippy --workspace --all-targets -- -D warnings` | **0** | canonical gate used by prior milestones (all-features not required by historical M0–M8 gates) |

**Lib totals (representative):** core 30 · differential **90** · host 3 · kernel 8 · persistence **34** · reference 14 · runtime **96**.

**G-BASELINE = PASS.**

---

## 23. M1–M8 Regression

| Milestone | Evidence this preflight | Result |
|---|---|---|
| M1 | core lib 30 | PASS |
| M2–M8 | differential 90 (includes system 15 + m2–m7) | PASS |
| M5 hinge | `effects::` 9/9 | PASS |
| M7 | persistence 34 | PASS |
| M8 review claims | HEAD abdfb55 | PASS |

**G-REGRESSION = PASS.**

---

## 24. Unsafe / External-Effect Check

| Check | Result |
|---|---|
| `#![forbid(unsafe_code)]` on differential/reference/persistence/runtime | present |
| M9 must not introduce unauthorized fs/net/process as authority | required constraint for impl |
| Current scan (pre-impl) | no M9 operators yet |

**G-UNSAFE = PASS** (baseline); M9 impl must preserve.

---

## 25. Repository Integrity

| Path | Modified by preflight? |
|---|---|
| `final/` `reg/` `dep/` `mod/` `spec/` `req/` `term/` | **NO** |
| Production/reference/test source | **NO** |
| Sole intended artifact | `docs/bootstrap/M9-PREFLIGHT.md` |

**G-INTEGRITY = PASS.**

---

## 26. Disclosed Limitations

| ID | Limitation |
|---|---|
| L-M9-NYI | No `mutations/registry.toml` file; no machine injection yet (expected) |
| L-M9-TESTKIT-THIN | `ror-testkit` skeleton only |
| L-M9-KILLRATE-ZERO | MutationKillRate not measurable until impl (final/04 FACT) |
| L-M9-M8-DOMAIN | M8 pure-CEK generator may not exercise all mutant surfaces — targeted suites required |
| L-M9-M036 | Document mutant vs machine mutant split — both registered; M9 focuses machine path + may cite tooling M036 separately |
| F-04 / U-* | Carried OPEN from M8/M7 |
| L-M9-NO-CLAIM | Preflight does not claim any mutant killed |
| U-35 | Determinism theorem open |

---

## 27. Final Preflight Classification

### Gate board

| Gate | Status |
|---|---|
| Identity / lineage | **PASS** |
| M8 accepted baseline | **PASS** |
| Canonical M9 discovery | **PASS** |
| Registry authority (M001–M042) | **PASS** |
| Scope / non-scope | **PASS** |
| Result taxonomy | **PASS** |
| Critical mutation rules | **PASS** |
| M5 hinge baseline | **PASS** |
| M7 / M8 / M10 / M11 boundaries | **PASS** / **PASS-DISCLOSED** (M8 domain) |
| Reference independence | **PASS** |
| Dependencies | **PASS** |
| Determinism constraints | **PASS-DISCLOSED** |
| Evidence / R-REG / OAD | **PASS** |
| Baseline + regression tests | **PASS** |
| Repo integrity | **PASS** |

**BLOCKS = 0.**

### Authorization criteria

```text
canonical M9 scope established
∧ M8 accepted
∧ baseline valid
∧ dependencies valid
∧ reference independence valid
∧ determinism constraints established
∧ security boundaries preserved
∧ OAD boundaries preserved
∧ R-REG unchanged
∧ M10/M11 boundaries established
∧ no blocking canonical ambiguity
```

All hold (with disclosed non-blocking limitations).

```text
M9 PREFLIGHT = GREEN WITH DISCLOSED LIMITATIONS
IMPLEMENTATION AUTHORIZATION = AUTHORIZED
```

```text
M9 IMPLEMENTATION = NOT STARTED
NEXT = M9 IMPLEMENTATION
```

---

## 28. Authorization

### Authorized when M9 implementation begins

1. Materialize registry from **canonical** M001–M042 text (no invented IDs).  
2. Build injection + run harness per R-TEST-06 (targeted + differential assert kill).  
3. Compute kill-rate over **non-equivalent** registered set; adjudicate equivalents explicitly.  
4. Preserve M5 hinge, M7 recovery classification, M8 independence, no host bypass.  
5. Keep R-REG SPECIFIED; keep OADs/F-04 open; no M10/M11 claims.  
6. Record Intended/Injected/Executed/Killed/Survived/Equivalent/Not-Run/Inconclusive honestly.

### Explicit non-claims (this preflight)

```text
Mutation verification is not complete.
Mutation kill-rate has not been achieved.
M9 implementation does not exist.
No machine mutant has been killed by this operation.
OADs are not closed.
R-REG is not VERIFIED or PROVEN.
M10 is not complete.
M11 is not complete.
No production readiness.
No formal proof.
Baseline tests ≠ mutation evidence.
```

### Final output block

```text
M9 PREFLIGHT = GREEN WITH DISCLOSED LIMITATIONS

IMPLEMENTATION AUTHORIZATION = AUTHORIZED

M9 IMPLEMENTATION = NOT STARTED

R-REG = 184 × SPECIFIED

OADs = OPEN (F-04 UNKNOWN; U-02/U-17/U-32/U-35 and applicable residuals OPEN)

M8 REVIEW = ACCEPTED WITH DISCLOSED EVIDENCE LIMITATIONS

NEXT = M9 IMPLEMENTATION
```

### Final state board

```text
M0–M7                      prior accepted (disclosed where noted)
M8                         ACCEPTED WITH DISCLOSED EVIDENCE LIMITATIONS
M9 preflight               GREEN WITH DISCLOSED LIMITATIONS — IMPLEMENTATION AUTHORIZED
M9 implementation          NOT STARTED
R-REG                      184 × SPECIFIED
NEXT                       M9 IMPLEMENTATION
```

---

*End of M9 PREFLIGHT. Do not begin M9 implementation in this operation.*
