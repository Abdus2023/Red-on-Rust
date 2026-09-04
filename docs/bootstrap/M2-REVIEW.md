# M2 Implementation Review

**Operation:** M2 IMPLEMENTATION REVIEW & EVIDENCE RECONCILIATION  
**Do not implement M3. Do not promote R-REG. Do not resolve OADs.**

---

## Reviewed commit

| Field | Value | Class |
|---|---|---|
| Branch | `arena/01a06993-red-on-rust` | FACT |
| Reviewed implementation tip | `d57d8aabd128bc1735ecfbe14be1bdeaa0652e0c` | FACT |
| Subject | `feat(m2): pure CEK subset (Value/Var/Let/Seq/If) + reference differential` | FACT |
| Preflight | `b2ab309` → `docs/bootstrap/M2-PREFLIGHT.md` | FACT |
| Parent M1 review | `8d84511` | FACT |
| Review corrections (this op) | test-strengthening only (see §Corrections) | FACT |

**Session note (FACT):** At review start the local working tree had been reset behind `origin` (HEAD `1b62944` with untracked M2 tree). Local branch was realigned to `origin/arena/01a06993-red-on-rust` @ `d57d8aa` before audit. No canonical files were altered by that realignment.

---

## Starting state

Verified against bootstrap artifacts and R-REG:

```text
M0                         GREEN                          (M0-B-VALIDATION)
M1 frozen subset           ACCEPTED WITH DISCLOSED
                           EVIDENCE LIMITATIONS           (M1-REVIEW)
M1 full                    NOT COMPLETE                   (M1-REVIEW)
M2 preflight               GREEN WITH DISCLOSED LIMITATIONS (M2-PREFLIGHT)
M2 implementation          IMPLEMENTED / TESTED           (M2-PROGRESS @ d57d8aa)
M2 review                  PENDING → this document
M2 semantic verification   NOT CLAIMED
M3                         NOT STARTED
R-REG                      184 × SPECIFIED                (reg/requirements.json)
```

---

## Authority hierarchy

Applied in order:

1. `final/01` (R-ORDER-02, R-CEK-*, R-CALC-01…03, R-REF-*)  
2. `reg/requirements.json` / `final/03`  
3. `final/04` / `final/08` evidence model  
4. `final/09` OADs  
5. `dep/10-graph.json`, `mod/05`, `mod/18`  
6. `state/repository-state.json` (projection; known BOOTSTRAP drift)  
7. `docs/bootstrap/M2-PREFLIGHT.md`  
8. `docs/bootstrap/M2-PROGRESS.md`  
9. Implementation under `crates/`

No case was found where implementation was allowed to redefine canonical semantics.

---

## Canonical M2 scope

| Authority | M2 surface | Class |
|---|---|---|
| R-ORDER-02 | Pure CEK: Expr/Value/step/env/lexical binding/stackless frames | FACT |
| final/04 | Differential Value/Var/Let/Seq/If | FACT |
| mod/05 | M2 pure-subset; M3 = Lambda/Call tags | FACT |
| M2-PREFLIGHT | Authorized constructors only | FACT |

**Implemented evaluation surface (FACT):** `Value`, `Var`, `Let`, `Seq`, `If` only.  
**M3 forms (FACT):** `Lambda`/`Call` (and later) → `Fault::UnsupportedInM2` — no transition bodies, no `FunctionValue` construction by evaluation.

**Diff classification (`8d84511..d57d8aa` + review tests):**

| Path | Classification |
|---|---|
| `crates/ror-core/src/machine.rs` | **AUTHORIZED M2** (domain types) |
| `crates/ror-core/src/lib.rs` | **AUTHORIZED M2** (module export; data `Value` root re-export preserved) |
| `crates/ror-runtime/src/cek.rs` | **AUTHORIZED M2** (production CEK) |
| `crates/ror-runtime/src/lib.rs` | **AUTHORIZED M2** |
| `crates/ror-reference/src/pure_cek.rs` + Cargo.toml | **AUTHORIZED M2** (independent reference) |
| `crates/ror-differential/src/m2.rs` + Cargo.toml | **AUTHORIZED M2** / **TEST INFRASTRUCTURE** |
| `docs/bootstrap/M2-PREFLIGHT.md` | **DOCUMENTATION** (prior op) |
| `docs/bootstrap/M2-PROGRESS.md` | **DOCUMENTATION** |
| Review-added unit/diff tests | **TEST INFRASTRUCTURE** (audit correction) |
| `final/`, `reg/requirements.json`, OAD dispositions | **unchanged** |

No **UNAUTHORIZED** semantic change detected.

---

## Source-to-spec traceability

| Canonical | Obligation (atomic) | Implementation | Tests | Reference | Differential |
|---|---|---|---|---|---|
| R-ORDER-02 | M2 pure CEK milestone | runtime+core+ref | unit+diff | pure_cek | m2 harness |
| R-CEK-01 | EvalState {expr,env,K} | `EvalState` | structural | `RefState` | terminal obs |
| R-CEK-02 | Halt iff K=ε else Resume | `continue_with_value` | value_with_nonempty_k; ±1 K | `apply_value` | agree |
| R-CEK-03 (pure) | LetValue/Seq/If frames | `PureFrame` | enter/resume | `RefKont` | — |
| R-CEK-04/05 | Lambda/Call | **not implemented** | UnsupportedInM2 | same | both fault |
| R-CEK-06 | \|K\| ±1 pure | push/pop only on enter/resume | ±1 tests | kont push/pop | — |
| R-CALC-01 | machine Value | `machine::Value` | U-09 isolation | shared type | Halted(Value) |
| R-CALC-02 | Expr AST | `machine::Expr` | constructors | shared | fixtures |
| R-CALC-03 | Symbol(u32) | `Symbol` | env tests | shared | — |
| REQ-CALC-020 | E-Let/Seq/If pure | enter/resume_* | Let/Seq/If suite | same rules | agree |
| R-REF-02 | reference independence | no runtime dep | — | core-only dep | black-box |

No component found with **NO CANONICAL BASIS** inside the authorized surface.  
`Fault::UnsupportedInM2` and `step_limit` are **implementation bookkeeping** labels for phase-gate / fuel — documented as non-registry faults (**DISCLOSED LIMITATION**).

---

## CEK state audit

| Component | Semantic? | Notes | Class |
|---|---|---|---|
| `EvalState.{expr,env,continuation}` | **yes** | matches R-CEK-01 | PASS |
| `PureFrame::{LetValue,Seq,If}` | **yes** | R-CEK-03 subset | PASS |
| `Environment` bindings list | **yes** (layout = impl choice) | lexical reverse scan | PASS |
| `StepResult` | outcome | U-26 provisional | DISCLOSED LIMITATION |
| `CEK_MAX_STEPS_DEFAULT` | bookkeeping | not MOD-04 budget | DISCLOSED LIMITATION |
| `mem::replace` Unit placeholder | bookkeeping | avoids deep clone | PASS |
| Global mutable state | **none** | FACT | PASS |
| HashMap / RNG / time in step | **none** | FACT | PASS |
| Hidden host recursion for nesting | **none** in `step` | flat match + K vector | PASS |

---

## Stackless audit

| Claim | Evidence | Class |
|---|---|---|
| Semantic nesting in `PureFrame` / `Continuation` | FACT — enter_* pushes; resume pops | PASS |
| `step` is non-recursive | FACT — no self-call; driver loop in `evaluate` | PASS |
| Deep Let nest test | N=512 nested Lets → Halt(N); PASS | TESTED |
| Wide Seq chain | N=256 nested Seq → Halt(N); PASS | TESTED |
| Arbitrary depth / 50k–100k | **not evidenced** (host `Drop` on nested `Box<Expr>`; test depth reduced intentionally) | DISCLOSED LIMITATION |
| Progress report wording | correctly discloses Drop limit | PASS |

**Conclusion:** Machine-frame stacklessness for the pure subset is **structurally PASS**. Host-stack safety at extreme AST depth is **not** claimed as proven.

---

## Var / Environment audit

| Case | Production | Reference | Diff | Class |
|---|---|---|---|---|
| Bound lookup | PASS | PASS | PASS | TESTED |
| Unbound | `UnboundVariable` | same | agree | TESTED |
| Shadowing innermost | PASS | PASS | PASS | TESTED |
| `extend` non-mutating parent | PASS (review test) | shared `Environment` | — | TESTED |
| Dynamic scoping | **not present** | — | — | PASS |

Lexical rule: reverse scan of association list (implementation choice consistent with frozen sketches).

---

## Let audit

| Step | Behavior | Class |
|---|---|---|
| 1. Enter | push `LetValue{name,body,env}`; control ← value expr | PASS |
| 2. Value under **saved outer env** | review test: outer `x=7`; `let x=x in x` → 7; bare `let x=x in 1` → unbound | TESTED |
| 3. Resume | `env = saved.extend(name,v)`; control ← body | PASS |
| 4. Shadow restore via Seq | `let x=1 in seq(let x=2 in x, x)` → 1 | TESTED |

Evaluation order matches canonical CEK enter/resume (not Red/REBOL inference).

---

## Seq audit

| Property | Evidence | Class |
|---|---|---|
| First then second | step-level order test | TESTED |
| Result = second value | unit + diff | TESTED |
| First fault aborts | `seq(unbound, 2)` | TESTED |
| Explicit frame | `PureFrame::Seq` | PASS |
| Nested seq | diff `seq_family` | COVERED |

No short-circuit that skips first evaluation.

---

## If audit

| Property | Evidence | Class |
|---|---|---|
| Bool true/false select | unit + diff | TESTED |
| Non-Bool → TypeError | unit + diff | TESTED |
| Untaken branch not evaluated | `if true then 1 else unbound` (review) | TESTED |
| No Red/REBOL truthiness | only `Value::Bool` | PASS |

---

## Evaluation-order audit

Combinations exercised:

- `Let` + `If` + `Seq` + `Var` (runtime determinism test; differential combinations)  
- Let value in outer env (review)  
- Seq order via intermediate `EvalState.expr` (runtime)

Production and reference share terminal results; production exposes intermediate control via unit tests. **PASS** for authorized surface.

---

## Fault audit

| Condition | Fault | panic/unwrap in eval? | Diff |
|---|---|---|---|
| Unbound var | `UnboundVariable(Symbol)` | no | agree |
| If non-Bool | `TypeError{expected:Bool,…}` | no | agree |
| M3+ constructor | `UnsupportedInM2{form}` | no | agree |
| Step fuel exhausted | `UnsupportedInM2{step_limit}` | no | both |

`expect` appears only in differential **test** helper (`assert_agree`) — not in evaluator paths (**FACT**).

Fault enum is **evaluator-local / provisional** (not full R-CORE-13 surface) — **DISCLOSED LIMITATION**, not silent U-08 close.

---

## U-09 Value-domain audit

| Check | Result | Class |
|---|---|---|
| `types::Value` (15A data) vs `machine::Value` | distinct enums | FACT |
| Crate root `Value` re-export | **data-domain only**; machine via `machine::Value` | FACT |
| `From`/`Into` between domains | **none** | PASS |
| Type alias collapsing domains | **none** | PASS |
| Serialization traits on machine Value | **none** | PASS |
| Isolation unit test | PASS | TESTED |
| OAD U-09 register status | still **OPEN** (final/09) | FACT |
| Silently resolved? | **NO** | PASS |

---

## U-02 frame-serialization audit

| Search | Result |
|---|---|
| Serialize/Deserialize on frames/EvalState | none |
| encode/decode/byte tags for frames | none |
| Persistence of CEK state | none |

```text
U-02 = OPEN
frame serialization = NOT IMPLEMENTED
```

`Debug` on frames is non-canonical (**FACT**).

---

## Reference independence

| Layer | Result | Class |
|---|---|---|
| Cargo: `ror-reference` → `ror-core` only | FACT | PASS |
| Cargo: no `ror-runtime` / kernel / host / … | FACT | PASS |
| Production ↛ reference | FACT | PASS |
| Shared transition helpers | **none** (distinct fn sets; kont type names differ) | PASS |
| Long identical lines | trivial (imports, value_kind arms, mem::replace pattern) — not a shared engine | NON-BLOCKING DISCLOSURE |
| Algorithm structure | independently structured (`apply_value` vs `continue_with_value`/`resume_*`) | PASS |

Conceptual chain holds: canonical → independent reference → production → differential.

---

## Differential harness

| Property | Evidence | Class |
|---|---|---|
| Calls `ror_runtime::evaluate` and `ror_reference::evaluate` separately | FACT | PASS |
| Not self-comparison | distinct crates | PASS |
| Observation = Halted(Value) \| Fault(Fault) | FACT | PASS |
| Normalization erasing divergence? | Eq on full Value/Fault — no scrubbing | PASS |
| First divergence returned | `Err((p,r))` | PASS |

---

## Differential coverage

| Family | Classification |
|---|---|
| Value terminals | **COVERED** |
| Var bound / unbound | **COVERED** |
| Let nested / shadowing | **COVERED** |
| Seq nested / Let-in-Seq | **COVERED** |
| If both branches / type error | **COVERED** |
| Untaken branch | **COVERED** (review) |
| Let value outer env / shadow restore | **COVERED** (review) |
| Let+If+Seq combinations | **COVERED** |
| Multi-binding environments beyond 2-deep | **PARTIALLY COVERED** |
| Trace-level (event) differential | **NOT COVERED** (terminal only; allowed for M2) |
| Lambda/Call success paths | **NOT APPLICABLE** (M3) |

---

## M1 regression

| Suite | Result | Class |
|---|---|---|
| `ror-core` tests | **24 PASS** (21 M1-era + 3 machine/env) | FACT |
| Golden unit/bool/int/map/capref | PASS | FACT |
| Capability encode ban / decode reject | PASS | FACT |
| SHA-256 KATs | PASS | FACT |
| Machine Value in 15A codec path | **not introduced** | PASS |

---

## Security boundary

| Probe | Result |
|---|---|
| `std::fs` / `std::net` / `std::process` in CEK crates | none |
| HostExecutor / authorize / journal in step | none |
| Effect path from pure Expr | none (`UnsupportedInM2` for Request/…) |
| `Untrusted Input ↛ Authority ↛ External Effect` | held for M2 pure surface |

**PASS**

---

## Dependency audit

Convention: Cargo `dependent → dependency`; registry edges provider→consumer.

| Edge | Classification | Class |
|---|---|---|
| runtime → core | **REQUIRED** TYPE | PASS |
| reference → core | types only; **not** forbidden | PASS |
| differential → runtime, reference, core, testkit | verification | PASS |
| runtime → kernel, persistence | pre-existing workspace; **unused** on pure paths | DISCLOSED LIMITATION |
| Forbidden list scan | **0 hits** | PASS |

---

## Unsafe audit

```text
#![forbid(unsafe_code)] on M2 crates
rg \bunsafe\b crates → none
```

**PASS**

---

## Public API audit

| Item | Visibility | Justification | OAD |
|---|---|---|---|
| `machine::{Expr,Value,Environment,Fault}` | pub | MOD-01 domain | U-09 provisional Value name |
| `FunctionValue` | pub | R-CALC-01 shape; unused by M2 eval | M3 field |
| `EvalState`, `step`, `evaluate` | pub | MOD-05 entry | U-26 StepResult |
| `PureFrame` / `Frame` alias | pub | CEK frames | **U-02** — must not be treated as wire ABI |
| `Continuation` | pub | R-CEK-01 | U-02 |
| `sugar::*` | pub | test/fixture helpers | non-normative |

**DISCLOSED LIMITATION:** several CEK types are `pub` for harness access; they are **not** frozen public contracts. No OAD closed by publication.

---

## Determinism audit

| Check | Result |
|---|---|
| Repeated production evaluate | PASS |
| Repeated P/R observations | PASS |
| Env without HashMap | FACT |
| No wall clock / RNG / threads in step | FACT |

Operational determinism **TESTED**. GI-DET / U-35 theorem **NOT CLAIMED**.

---

## Test-quality audit

| Concern | Finding | Action |
|---|---|---|
| Count ≠ coverage | addressed by family matrix above | documented |
| Missing untaken-branch | gap at `d57d8aa` | **fixed in review** |
| Missing Let outer-env | gap | **fixed in review** |
| Missing shadow-restore via Seq | gap | **fixed in review** |
| Diff only terminal | acceptable M2; traces deferred | DISCLOSED |
| Deep nest reduced vs 5k | Drop limit honest | DISCLOSED |
| `assert_agree` uses expect | test-only | OK |
| Vacuous tests | not found on core CEK paths | PASS |
| Shared P/R engine | not found | PASS |

Post-review counts (FACT): core 24, runtime **21**, reference 2, differential **11**.

---

## Repository gates

Executed this review with `rustc`/`cargo` **1.88.0** (`RUSTUP_TOOLCHAIN=ror-stable`):

| Gate | Result |
|---|---|
| `cargo fmt --check` | **PASS** |
| `cargo check --workspace` | **PASS** |
| `cargo test --workspace` | **PASS** |
| `cargo clippy … -D warnings` | **PASS** |
| Forbidden dependency edges | **PASS** (0) |
| Unsafe | **PASS** |
| M1 regression | **PASS** |
| M2 differential | **PASS** |
| `python3 check.py` S7 | **FAIL** pre-existing (rejects workspace Cargo.toml) — tooling drift, not M2 semantic fail |

---

## Evidence reconciliation

| Kind | Status |
|---|---|
| Implementation evidence | repository code @ `d57d8aa` + review tests |
| Test evidence | cargo unit/diff PASS |
| Verification evidence (R-REG VERIFIED) | **none claimed** |
| Proof evidence | **none** |
| Registry status | **184 × SPECIFIED** (FACT) |
| `reg/status-transitions.json` `transitions` | **empty array** (FACT) |
| `state/` claims implemented/tested/verified | **all 0**; `implementation_state: BOOTSTRAP` | DERIVED-STATE DRIFT (pre-existing) |
| final/08 ceiling | SPECIFIED aligned |

```text
cargo test PASS  ⇏  R-REG VERIFIED
M2 ACCEPTED      ⇏  semantic verification complete
M2 ACCEPTED      ⇏  M3 authorized for implementation
```

---

## OAD audit

| OAD | Before | M2 interaction | After | Silently resolved? |
|---|---|---|---|---|
| U-02 | OPEN | in-memory frames only | OPEN | **NO** |
| U-09 | OPEN | separate `machine::Value` | OPEN | **NO** |
| U-21 | OPEN | no effect codec | OPEN | **NO** |
| U-26 | OPEN | provisional `StepResult` | OPEN | **NO** |
| U-04 | OPEN | no await | OPEN | **NO** |
| U-35 | OPEN | no theorem claim | OPEN | **NO** |
| U-24/25/29/30/37 | OPEN/register | M1 codec untouched | unchanged | **NO** |

---

## M3 containment

| Search | Result |
|---|---|
| `enter_lambda` / `enter_call` / `resume_call` | **absent** |
| `FunctionValue {` constructed in eval | **absent** |
| R-CEK-04/05 transition logic | **absent** |
| `UnsupportedInM2` boundary | present only |

```text
Lambda = NOT IMPLEMENTED
Call   = NOT IMPLEMENTED
M3     = NOT STARTED
```

---

## Disclosed limitations

1. R-REG remains SPECIFIED — no ledger promotion.  
2. U-02 frame bytes not implemented.  
3. U-09 domains distinct but OAD still OPEN.  
4. Stackless stress bounded (512/256); not 50k deep-call evidence.  
5. Budget `cost_C` / MOD-04 not wired.  
6. Fault surface evaluator-local vs R-CORE-13.  
7. Differential is terminal-only (no event traces).  
8. Public CEK types provisional.  
9. `state/` and `check.py` S7 drift pre-existing.  
10. runtime still links kernel/persistence unused on pure paths.  
11. `FunctionValue` type exists for domain completeness without M2 construction.  
12. Semantic **VERIFICATION** / **PROOF** not claimed.

---

## Review classification

```text
M2 IMPLEMENTATION = ACCEPTED WITH DISCLOSED EVIDENCE LIMITATIONS
```

**Rationale:** Authorized pure-subset CEK is present, tested, differentially agreed, boundary-clean (U-02/U-09/M3/deps/unsafe/security), without silent OAD or R-REG mutation. Residual gaps are evidence/depth/tooling limitations, not material semantic defects.

**Not used:** `ACCEPTED` (unqualified) — stack depth, cost_C, terminal-only diff, registry/projection drift warrant disclosure.  
**Not used:** `BLOCKED` — no blocker-class defect found.

---

## Final state

```text
M0                         GREEN
M1 frozen subset           ACCEPTED WITH DISCLOSED EVIDENCE LIMITATIONS
M1 full                    NOT COMPLETE
M2 preflight               GREEN WITH DISCLOSED LIMITATIONS
M2 implementation          ACCEPTED WITH DISCLOSED EVIDENCE LIMITATIONS
M2 semantic verification   NOT CLAIMED
M3                         NOT STARTED
R-REG                      184 × SPECIFIED
```

---

## Corrections

| Change | Kind | Semantic? |
|---|---|---|
| Runtime tests: untaken If branch; Let outer env; shadow restore; env parent isolation | test-strengthening | **no** |
| Differential tests: same families + harness API sanity | test-strengthening | **no** |
| This review document | documentation | **no** |

No CEK transition logic, deps, registries, or OADs modified.

---

## Next permitted operation

```text
NEXT = M3 PREFLIGHT
```

M3 preflight is a **separate** operation. It is **not** M3 implementation authorization by itself. Do not implement Lambda/Call until M3 preflight authorizes an implementation sprint.

---

## Commit decision (rule C)

All commit-permitted conjuncts hold:

1–12 satisfied (scope canonical; no final/reg/OAD mutation; no M3/U-02/U-09 violations; reference independent; gates green; review exists; classification accepted-with-limitations; commit contents = review + authorized test corrections).

```text
COMMIT = PERMITTED
```
