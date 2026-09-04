# M9 IMPLEMENTATION PROGRESS

**Operation ID:** `RATF-M9-IMPLEMENT-001`  
**Operation:** M9 IMPLEMENTATION ONLY  
**Authority:** M9 PREFLIGHT @ `docs/bootstrap/M9-PREFLIGHT.md` — GREEN WITH DISCLOSED LIMITATIONS — IMPLEMENTATION AUTHORIZED  
**Base HEAD (start):** `5a9615e32850040b604e81050489e9ef29dbe7f2`  
**Implementation commit (prior):** `2e92bf4`  
**Branch:** `arena/01a06993-red-on-rust`

```text
M9 IMPLEMENTATION = COMPLETE WITH DISCLOSED EVIDENCE LIMITATIONS
NEXT = M9 IMPLEMENTATION REVIEW
```

---

## Identity

| Item | Value |
|---|---|
| Preflight | `5a9615e` — GREEN WITH DISCLOSED LIMITATIONS; IMPLEMENTATION AUTHORIZED |
| M8 review | `abdfb55` ACCEPTED WITH DISCLOSED |
| Campaign baseline revision | recorded in `mutations/m9-results.json` → `baseline_revision` |
| Toolchain | `ror-stable` rustc/cargo 1.88.0 |
| Evidence schema | `m9-campaign-v2` |

---

## Canonical authority

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

## Harness Implementation Status

**Domain A — mutation-system implementation** (does **not** enter kill-rate).

| Component | Role | Status |
|---|---|---|
| `mutations/registry.toml` | Derived machine-readable registry (M001–M042) | present |
| `crates/ror-testkit` | Registry parse, ID validation, kill-rate arithmetic, taxonomy | present |
| `scripts/m9_mutation_run.py` | Deterministic campaign runner | present |
| Workflow | LOAD→BASELINE→MATERIALIZE→VERIFY→BUILD→TARGETED→DIFF→CLASSIFY→RECORD→CLEAN→NEXT | implemented |
| Isolation | Per-mutant temp scratch; destroyed after each mutant | implemented |
| VERIFY-MUTATION | Fingerprint delta + `MUTANT Mxxx` marker (doc path special-cased) | implemented |
| Classification rules | Build fail ⇒ INCONCLUSIVE (never auto-KILLED); mat fail ⇒ NOT-RUN | implemented |
| Evidence domains | Harness (A) vs Campaign (B) separated in JSON + report | implemented |
| Production ↛ harness | No production semantic dep on mutation engine | PASS |
| Reference independence | `ror-reference` → `ror-core` only; mutants target production | PASS |

Thin obligation surfaces (registered targets, not harness):

- `ror-agent` planner epoch / CapRef observation (M026/M027)
- `ror-host::verify_result_digest` (M029)
- Function env walk in marshal (M032)

---

## Harness Test Results

**Domain A evidence only.** These answer: *does the mutation-testing system correctly execute and classify campaigns?*  
They **MUST NOT** be counted as evidence that a production mutant is killed.

| Check | Result |
|---|---|
| `cargo test -p ror-testkit --lib` | PASS (registry load, expected IDs, kill-rate math, taxonomy distinctness) |
| Registry order M001…M042 unique count 42 | PASS (runner + testkit) |
| Inline classification purity (build≠KILLED, mat-fail=NOT-RUN, detect=KILLED, nodetect=SURVIVED) | PASS |
| **Harness overall** | **PASS** (`mutations/m9-results.json` → `harness.pass`) |

```text
Harness correctness ≠ Mutation kill evidence
Harness tests PASS ∧ 42 mutants processed  ⇏  M9 PASS
```

M9 gate uses **only** domain B terminal states (next sections).

---

## Registered Mutation Campaign

**Domain B — mutant-execution evidence** (sole kill-rate input).

### Deterministic workflow (every Mxxx)

```text
1. LOAD           Read canonical mutant definition Mxxx from derived registry
2. BASELINE       Verify unmutated baseline green (shared once per campaign)
3. MATERIALIZE    Isolated scratch workspace + apply operator
4. VERIFY-MUTATION  Prove intended mutation applied (fingerprint + marker)
5. BUILD          Build mutated target package
6. TARGETED       Canonical targeted tests
7. DIFFERENTIAL   Canonical differential tests when registry requires
8. CLASSIFY       Exactly one terminal state
9. RECORD         Persist stage outcomes + terminal + evidence
10. CLEAN         Destroy isolated mutant workspace
11. NEXT          Deterministic next registry ID
```

### Determinism locks

| Axis | Mechanism |
|---|---|
| Mutation ordering | Registry order M001…M042 only |
| Mutation identity | Stable IDs; runner rejects wrong count/order |
| Baseline revision | `git rev-parse HEAD` recorded in results JSON |
| Test selection | `TARGETED` / `DIFFERENTIAL` maps keyed by ID |
| Result classification | `classify_terminal` pure function |
| Evidence serialization | JSON schema `m9-campaign-v2` + matrix markdown |

### Campaign run parameters

| Field | Value |
|---|---|
| Schema | `m9-campaign-v2` |
| Baseline | PASS (`baseline_ok: true`) |
| Harness | PASS (separate) |
| Artifacts | `mutations/m9-results.json`, `mutations/m9-matrix.md` |

---

## Per-Mutant Results

Full stage matrix: **`mutations/m9-matrix.md`**  
Machine-readable: **`mutations/m9-results.json`** → `results[]`

Each row records:

```text
Mxxx
Canonical target / defect
Materialization = PASS
Mutation verification = PASS
Build = PASS
Targeted execution = FAIL   (detection)
Differential execution = FAIL | PASS | N-A
Terminal mutation result = KILLED
Evidence = targeted_detection[+differential_detection] | gate evidence
```

**Aggregate stage facts (all 42):**

| Stage | Outcome |
|---|---|
| LOAD | PASS × 42 |
| BASELINE | PASS (shared) |
| MATERIALIZE | PASS × 42 |
| VERIFY-MUTATION | PASS × 42 |
| BUILD | PASS × 42 |
| TARGETED | FAIL × 42 (detection fired) |
| Terminal | **KILLED × 42** |

No mutant terminated as SURVIVED, EQUIVALENT, INCONCLUSIVE, or NOT-RUN.

### Terminal state rules applied

| Rule | Enforced |
|---|---|
| KILLED only if applied ∧ verification PASS ∧ detection observed | yes |
| SURVIVED if applied ∧ executed ∧ no detection | yes (0 cases) |
| EQUIVALENT only if canonical disposition | yes (0 registry equiv) |
| INCONCLUSIVE for build fail / verify fail / incomplete | yes (0 cases) |
| NOT-RUN if not materialized / baseline red | yes (0 cases) |
| Build failure ≠ automatically KILLED | yes (classifier unit-checked) |
| States mutually exclusive | yes |

---

## Critical Mutation Results

Security-flagged registry rows (`security=true`) include hinge, capability, receipt, recovery, and planner authority mutants (see registry.toml).

| Check | Result |
|---|---|
| Critical SURVIVED | **NO** |
| M010 EffectId-before-auth | **KILLED** |
| M004/M005/M006 capability | **KILLED** |
| M015/M016/M023/M028 recovery/persist | **KILLED** |
| M017/M018/M019/M020 receipt | **KILLED** |
| M037 pre-durability host | **KILLED** |

```text
HostInvoked(E) ⇒ DurableIssued(E)   M5 HINGE = INTACT
```

---

## Kill-Rate Calculation

**Computed only from domain B terminal states of registered non-equivalent mutants.**

```text
N = registered non-equivalent = 42 − 0 equivalent = 42
K = classified KILLED           = 42
MutationKillRate = K / N × 100  = 100%
```

Gate conditions:

| Condition | Status |
|---|---|
| K = N | PASS |
| No non-equivalent SURVIVED | PASS |
| No non-equivalent INCONCLUSIVE | PASS |
| No non-equivalent NOT-RUN | PASS |
| No critical SURVIVED | PASS |
| Harness folded into K or N? | **NO** |

```text
gate_ok = true   (mutations/m9-results.json)
```

---

## Survivors / Inconclusives / Not-Run

| Class | Count | Records |
|---|---|---|
| SURVIVED | 0 | none |
| INCONCLUSIVE | 0 | none |
| NOT-RUN | 0 | none |
| EQUIVALENT | 0 | none (no canonical equiv disposition) |

No survivor reports required.

---

## Regression Results

| Gate | Result |
|---|---|
| Baseline `cargo test --workspace --lib` (campaign step 2) | PASS |
| `cargo fmt --all -- --check` | PASS |
| `cargo check --workspace` | PASS |
| `cargo clippy --workspace --all-targets -- -D warnings` | PASS |
| M1–M8 surfaces | green under unmutated tree |
| Live tree contamination | none (scratch-only mutants) |

---

## Security Results

| Finding | Status |
|---|---|
| Surviving non-equivalent mutant | none |
| Surviving critical mutant | none |
| M5 hinge violated under baseline | no |
| BLOCK-SECURITY | not raised |
| Reference mutated to force kills | no |

---

## Mutation registry summary

| Field | Value |
|---|---|
| Registered | **42** (M001–M042) |
| Machine mutants | 41 |
| Document mutant | M036 (U-38 / checker gate) |
| Canonical equivalents | **0** |
| Non-equivalent denominator | **42** |

---

## Differential results

Where `differential=true` (or configured), differential package execution ran.  
Kill evidence may include `differential_detection` when the differential suite failed under the mutant.  
Reference crate was **not** mutated.

**REFERENCE INDEPENDENCE = PASS**

---

## Determinism evidence

| Property | Evidence |
|---|---|
| Stable IDs | registry + testkit + runner BLOCK-CANONICAL on mismatch |
| Ordered execution | sequential M001…M042 |
| Baseline revision pinned | JSON field |
| VERIFY before BUILD | enforced |
| CLEAN after each | `shutil.rmtree` in `finally` |
| Re-run campaign | 42/42 KILLED under same rules |

U-35 remains OPEN (no theorem claim).

---

## Disclosed limitations

| ID | Limitation |
|---|---|
| L-M9-INJECT-STYLE | Source-level textual operators of registered defect intent; not a general AST mutator |
| L-M9-TARGETED-FILTER | Cargo test name filters + package suites; not a full obligation-tag scheduler |
| L-M9-DIFF-SUBSET | Differential leg per registry/config; M8 pure-CEK domain limitation carried |
| L-M9-M036-DOC | M036 killed via document/checker gate (U-38), not machine CEK injection |
| L-M9-THIN-AGENT | M026/M027 thin planner surface — not full LLM agent |
| L-M9-NO-PROOF | 42/42 kills are mutation evidence, not VERIFIED/PROVEN/R-REG promotion |
| F-04 / U-* | OADs remain OPEN |
| U-35 | Determinism theorem open |

---

## R-REG / OAD / M10 / M11

| Item | State |
|---|---|
| R-REG | **184 × SPECIFIED** (unchanged) |
| OADs | OPEN (F-04 UNKNOWN; U-02/U-08/U-09/U-17/U-21/U-31/U-35 and residuals) |
| M10 | NOT STARTED |
| M11 | NOT STARTED |
| Canonical `final/` `reg/` `dep/` `mod/` `spec/` | not modified as mutation authority |

---

## Final M9 status

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

HARNESS DOMAIN A = PASS (separate; not in kill-rate)

CAMPAIGN DOMAIN B = 42/42 KILLED

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
- **Harness tests PASS ≠ MutationKillRate = 100%** (rate is domain B only)  

Even **42/42 killed** is **mutation evidence**, not a mathematical proof of the calculus (R-CLAIM-01).

---

*End of M9 IMPLEMENTATION. Do not perform M9 review in this operation.*
