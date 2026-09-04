# M2 Progress

**Operation:** M2 IMPLEMENTATION SPRINT  
**Preflight authority:** `docs/bootstrap/M2-PREFLIGHT.md`  
**Preflight decision:** `GREEN WITH DISCLOSED LIMITATIONS`  
**Branch:** `arena/01a06993-red-on-rust`

---

## Authorized scope

From R-ORDER-02, final/04, mod/05, and M2-PREFLIGHT:

| In scope (M2) | Out of scope |
|---|---|
| Machine `Expr` / `Value` / `Environment` | Lambda / Call (M3; R-CEK-04/05) |
| Explicit CEK `EvalState` + `step` | Effects, host, FS/net/process |
| Frames `LetValue` / `Seq` / `If` | Actors, scheduler, persistence |
| Lexical env extend/lookup (Let/Var) | Capability authorize/derive |
| Value-return Halt/Resume (R-CEK-02) | Frame byte codecs (U-02) |
| Independent reference pure CEK | R-REG status promotion |
| Differential Value/Var/Let/Seq/If | OAD resolutions |

**Expression surface evaluated:**

```text
Expr ⊆ { Value(v), Var(s), Let{…}, Seq{…}, If{…} }
```

Full R-CALC-02 constructors are *declared* on `Expr`; non-M2 forms fault as `Fault::UnsupportedInM2`.

---

## Implemented semantic surface

| Form | Production | Reference | Classification |
|---|---|---|---|
| `Value` terminal | yes | yes | **IMPLEMENTED** / **TESTED** |
| `Var` lookup / unbound | yes | yes | **IMPLEMENTED** / **TESTED** |
| `Let` bind + body | yes | yes | **IMPLEMENTED** / **TESTED** |
| `Let` shadowing | yes | yes | **IMPLEMENTED** / **TESTED** |
| `Seq` first→second | yes | yes | **IMPLEMENTED** / **TESTED** |
| `If` Bool branches | yes | yes | **IMPLEMENTED** / **TESTED** |
| `If` non-Bool type error | yes | yes | **IMPLEMENTED** / **TESTED** |
| Stackless continuation ±1 | yes | yes (kont vec) | **IMPLEMENTED** / **TESTED** |
| Lambda / Call | fault only | fault only | **DEFERRED** (M3) — scaffolding fault path only |
| Frame serialization | — | — | **NOT IMPLEMENTED** (U-02) |
| Budget `cost_C` algebra | δ_t conceptually 0; no debit API | same | **DISCLOSED LIMITATION** |

---

## Canonical requirement mapping

| Requirement | Role in M2 | Evidence |
|---|---|---|
| R-ORDER-02 | Milestone definition | this report + code |
| R-CEK-01 | `EvalState` + non-recursive step | `ror-runtime::cek` |
| R-CEK-02 | Halt iff K empty; else Resume | unit + structural tests |
| R-CEK-03 | Pure frames only | `PureFrame` / `RefKont` |
| R-CEK-04/05 | **out of scope** | fault `UnsupportedInM2` |
| R-CEK-06 | ±1 K on pure entry/resume | structural tests |
| R-CEK-07 | progress (pure subset) | evaluate to Halt/Fault |
| R-CALC-01 | machine Value | `ror_core::machine::Value` |
| R-CALC-02 | Expr surface | `ror_core::machine::Expr` |
| R-CALC-03 | `Symbol(u32)` | shared `Symbol` |
| REQ-CALC-020 | pure local rules shape | Let/Seq/If transitions |
| R-REF-02 | reference independence | no runtime→reference; reference does not call production |
| R-CANON-* | M1 unchanged | 21 prior + 3 new core tests green |

**R-REG status:** all remain **SPECIFIED** — **no promotion**.

---

## Atomic obligation mapping

| Obligation | Status |
|---|---|
| REQ-CEK-001 EvalState shape | **IMPLEMENTED** |
| REQ-CEK-002 no recursive host eval | **IMPLEMENTED** (loop + explicit K) |
| REQ-CEK-003 serializable continuation | **DEFERRED** (U-02; in-memory only) |
| REQ-CEK-004/005/006 value-return | **IMPLEMENTED** / **TESTED** |
| REQ-CEK-007 full nine frames | **PARTIAL** — pure three implemented |
| REQ-CEK-008+ Lambda/Call… | **DEFERRED** M3+ |
| REQ-CALC-020 E-Let/Seq/If | **IMPLEMENTED** (cost_C table not fully wired) |

---

## Production CEK

| Item | Location |
|---|---|
| Crate | `crates/ror-runtime` |
| Module | `src/cek.rs` |
| Types | `EvalState`, `Continuation`, `PureFrame`, `StepResult` |
| API | `step`, `evaluate` |
| Domain types | `ror_core::machine::{Expr, Value, Environment, Fault}` |

**Implementation notes (not canonical decisions):**

- Environment = association list, reverse scan (deterministic).
- `step` takes ownership of current expr via `mem::replace` (avoids deep clone).
- `StepResult` is provisional (U-26).
- Kernel/persistence remain Cargo deps but are unused on pure paths.

---

## Reference CEK

| Item | Location |
|---|---|
| Crate | `crates/ror-reference` |
| Module | `src/pure_cek.rs` |
| Types | `RefState`, `RefKont`, `RefOutcome` |
| API | `step`, `evaluate` |
| Deps | **`ror-core` only** (types/fixtures) |

Transition logic is independently authored (distinct kont enum names and control flow). No import of `ror_runtime`.

---

## Differential tests

| Harness | `crates/ror-differential/src/m2.rs` |
|---|---|
| Surface | Value / Var / Let / Seq / If (+ shared M3-fault agreement) |
| Observation | terminal `Halted(Value)` or `Fault(Fault)` only |
| Result | **8 tests PASS** — production ≡ reference |

---

## Negative tests

| Case | Production | Differential |
|---|---|---|
| Unbound variable | PASS | PASS |
| If non-Bool | PASS | PASS |
| Seq first unbound | PASS | covered |
| Lambda/Call under M2 | `UnsupportedInM2` | both agree |

---

## Determinism tests

| Case | Result |
|---|---|
| Repeated `evaluate` same expr | PASS (`ror-runtime`) |
| Repeated observations P/R | PASS (`ror-differential`) |
| No HashMap in env | FACT (vec assoc list) |

U-35 determinism *theorem* still **OPEN** — no VERIFIED claim.

---

## M1 regression status

| Suite | Result |
|---|---|
| `ror-core` M1 codec + digest + U-09 isolation | **24 tests PASS** (21 M1 + 3 machine/env) |
| Data-domain `Value` public re-export preserved | FACT |
| No machine↔data `From` bridge | FACT |

---

## OAD boundaries preserved

| OAD | Handling |
|---|---|
| **U-09** | `machine::Value` ≠ `types::Value`; documented; no collapse |
| **U-02** | no frame/value machine codecs |
| **U-21** | no effect codecs |
| **U-26** | `StepResult` provisional |
| **U-35** | no theorem claim |
| **U-04** | no await |

No OAD marked resolved.

---

## Dependency boundary

```text
ror-core → ror-runtime          REQUIRED TYPE     present
ror-core → ror-reference        types only        present (not forbidden)
ror-runtime ↛ ror-reference     FORBIDDEN         absent
ror-reference ↛ ror-runtime     FORBIDDEN         absent
ror-reference ↛ kernel/host/…   FORBIDDEN         absent
ror-core ↛ ror-runtime          FORBIDDEN         absent
```

`cargo metadata` forbidden-edge scan: **0 violations**.

New edge: `ror-core → ror-differential` (fixture types for harness) — verification-side, consistent with SUT observation.

---

## Reference independence

| Check | Result |
|---|---|
| Production does not depend on reference | PASS |
| Reference does not depend on production evaluator | PASS |
| Shared transition implementation | **none** |
| `audit/_reference_independence_checker.py` | reports only pre-existing F-* notes (no new coupling from M2 CEK) |

---

## Unsafe-code status

```text
#![forbid(unsafe_code)] on ror-core, ror-runtime, ror-reference, ror-differential
rg \bunsafe\b crates/**/*.rs → none
```

**PASS**

---

## Repository gates

| Gate | Result |
|---|---|
| `cargo fmt --check` | **PASS** |
| `cargo check --workspace` | **PASS** |
| `cargo test --workspace` | **PASS** (24 core + 17 runtime + 2 reference + 8 differential) |
| `cargo clippy --workspace --all-targets --all-features -- -D warnings` | **PASS** |
| Dependency / forbidden edges | **PASS** |
| Reference independence (no forbidden edges) | **PASS** |
| Unsafe gate | **PASS** |
| M1 regression | **PASS** |
| M2 differential | **PASS** |
| `python3 check.py` S7 pipeline | **FAIL** (pre-existing: rejects any workspace `Cargo.toml`) — **DISCLOSED LIMITATION**, not introduced by M2 |

---

## Evidence limitations

1. R-REG remains 184× **SPECIFIED** — implementation evidence is repository-only.
2. REQ-CEK-003 snapshot round-trip **not** claimed (U-02).
3. Full nine-frame set **not** implemented (Call*/Request* deferred).
4. Budget `cost_C` / MOD-04 algebra not wired; pure steps do not debit.
5. Deep-nest stress limited to 512 lets / 256 seq (host `Drop` recursion on nested `Box<Expr>`); evaluator step is non-recursive.
6. No claim of semantic **VERIFIED** / **PROVEN**.
7. `state/` projection still BOOTSTRAP (pre-existing drift).
8. Kernel/persistence linked to runtime crate but unused in pure M2 paths.

---

## Deferred M3 surface

```text
M3 (NOT STARTED):
  Lambda
  Call
  R-CEK-04
  R-CEK-05
  tags CEK-CALL-ARITY-PRECHECK, CEK-CALL-ARGS-LTR, CEK-CLOSURE-LEXICAL-CAPTURE
  frames CallFunction / CallArgument
  FunctionValue creation via Lambda evaluation
```

M2 only *faults* these forms. `FunctionValue` exists on the machine value domain for R-CALC-01 completeness but is never constructed by M2 evaluation.

---

## Remaining M2 work

| Item | Priority |
|---|---|
| Optional deeper stress (arena-allocated Expr to avoid Drop recursion) | low |
| Wire minimal fuel/cost_C once MOD-04 lands | later |
| Broader differential corpus / property tests | optional |
| M2 review / acceptance operation | next governance step |
| R-ORDER-03 full 7-form (needs M3) | after M3 |

No blockers identified for treating the **authorized pure-subset implementation** as code-complete under preflight limits.

---

## Current state

```text
M0                         GREEN
M1 frozen subset           ACCEPTED WITH DISCLOSED EVIDENCE LIMITATIONS
M1 full                    NOT COMPLETE
M2 preflight               GREEN WITH DISCLOSED LIMITATIONS
M2 implementation          IMPLEMENTED / TESTED
M2 semantic verification   NOT CLAIMED
M3                         NOT STARTED
R-REG                      184 × SPECIFIED
```

### Classification summary

| Claim | Label |
|---|---|
| Pure CEK production | **IMPLEMENTED** |
| Pure CEK reference | **IMPLEMENTED** |
| Unit / structural / negative / determinism | **TESTED** |
| Differential M2 surface | **TESTED** |
| Milestone semantically VERIFIED | **NOT CLAIMED** |
| Lambda/Call | **DEFERRED** (M3) |
| Frame codecs | **NOT IMPLEMENTED** (U-02) |
| Registry promotion | **NOT DONE** |
