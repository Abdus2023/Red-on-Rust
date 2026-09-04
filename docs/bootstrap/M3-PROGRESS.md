# M3 Progress

**Operation:** M3 IMPLEMENTATION SPRINT  
**Preflight authority:** `docs/bootstrap/M3-PREFLIGHT.md` (`759fb26`)  
**Preflight decision:** `GREEN WITH DISCLOSED LIMITATIONS — IMPLEMENTATION AUTHORIZED`

---

## 1. Starting commit

```text
759fb2649c558a9bb4e42bdcc9e13d98738e4cc1
preflight: authorize M3 implementation scope
```

## 2. Final implementation commit

**Commit:** `190244707ea57b86c4e3419c8759d090c7873044`

## 3. M3 scope

Authorized surface (from R-ORDER-02, R-CEK-04/05, M3-PREFLIGHT):

```text
M2 ∪ { Lambda { params, body }, Call { func, args } }
```

| In scope | Out of scope |
|---|---|
| Lambda → FunctionValue + lexical capture | Attenuate / Request / effects |
| Call LTR; arity before args | Actors / scheduler / host |
| CallFunction / CallArgument frames | Frame byte codecs (U-02) |
| Apply in closure env | R-REG promotion |
| Independent reference + differential | M4+ |

---

## 4. Canonical requirement / obligation mapping

| Authority | Implementation |
|---|---|
| R-ORDER-02 M3 | closure capture, LTR, arity precheck |
| R-CEK-04 | `enter_lambda` → FunctionValue + value-return |
| R-CEK-05 | `enter_call` / `resume_call_*` / `apply_function` |
| R-CEK-03 Call* | `PureFrame::CallFunction`, `CallArgument` |
| REQ-CEK-008 | closure env on FunctionValue; caller_env on frames |
| REQ-CEK-009…012 | pure Lambda, capture, FunctionValue shape, no early Halt |
| REQ-CEK-013 | function → args LTR → apply |
| REQ-CEK-014 | arity before any arg eval → `Fault::ArityMismatch` |
| REQ-CEK-015…017 | apply in `ρ_closure[xi↦vi]`; free vars not from caller |
| REQ-CEK-018/019/023 | ±1 K push/pop; single pop via `continue_with_value` |
| R-BUDGET-16 | call `δ_t = 0` (no time advance; cost_C not wired) |
| R-REF-02 | independent `ror-reference` transitions |

**R-REG:** still **184 × SPECIFIED** — no promotion.

---

## 5. Production CEK changes

| Path | Change |
|---|---|
| `crates/ror-runtime/src/cek.rs` | Lambda/Call transitions; Call* frames |
| `crates/ror-runtime/src/lib.rs` | docs M2+M3 |
| `crates/ror-core/src/machine.rs` | `Fault::ArityMismatch`; sugar `lambda`/`call` |

---

## 6. Lambda implementation

- `enter_lambda`: clone current `Environment` into `FunctionValue.env` (immutable assoc-list capture; C-75: in-memory Environment, not wire snapshot).
- Produce `Value::Function(...)`.
- Deliver via `continue_with_value` (REQ-CEK-012) — never immediate Halt.

## 7. Call implementation

1. `enter_call`: push `CallFunction { args, env: caller }`; control ← func.  
2. `resume_call_function`: require Function; **arity check**; if args empty → apply; else push `CallArgument`, eval first arg under caller_env.  
3. `resume_call_argument`: collect LTR; when done → apply.  
4. `apply_function`: `ρ' = ρ_closure.extend(params, args)`; control ← body under residual K.

## 8. Closure capture

Lexical at Lambda creation. Verified: caller rebind of free var does not affect closure body (`CEK-CLOSURE-LEXICAL-CAPTURE`).

## 9. Evaluation order

```text
function → arg₀ → … → argₙ → apply
```

State-step test confirms CallFunction before arg evaluation.

## 10. Arity behavior

`args.len() != params.len()` → `Fault::ArityMismatch { expected, actual }` **before** any arg step. Wrong-arity + unbound arg still yields ArityMismatch (not Unbound).

## 11. Parameter binding

`zip(params, args)` left-to-right into cloned closure env. Param shadows captured binding. Outer env restored only via residual frames (not mutated in place beyond state.env assignment).

## 12. Fault behavior

| Case | Fault |
|---|---|
| Unbound | `UnboundVariable` |
| If non-Bool / call non-Function | `TypeError` |
| Arity | `ArityMismatch` |
| M4+ forms | `UnsupportedInM2 { form }` |
| Fuel | `UnsupportedInM2 { step_limit }` |

No panic/unwrap on eval paths.

## 13. Reference implementation

`crates/ror-reference/src/pure_cek.rs`: independent kont names (`WaitingOp` / `WaitingArg`), independent `deliver` / `install_body`. Deps: **ror-core only**.

## 14. Differential tests

| Module | Cases |
|---|---|
| `m2` | prior M2 suite (10 tests) — still PASS |
| `m3` | 21 tests: Lambda, Call, capture, shadow, nested, arity ±, non-callable, faults, LTR, isolation, determinism |

Terminal observation Eq on `Halted(Value)` / `Fault(Fault)`.

## 15. Mutation coverage (test intent)

| Mutation | Caught by |
|---|---|
| Skip arity / arity after args | `arity_before_arg_eval` |
| Reverse arg order / wrong bind | multi-arg + LTR tests |
| Capture caller env | `closure_capture_not_caller` |
| Body in caller env | same + nested closure |
| Non-callable as callable | `non_callable` |
| Swallow arg/body fault | argument/body fault tests |

Full MOD-16 mutation runner not required for this sprint; unit/diff encode kill conditions.

## 16. M1 regression

`ror-core`: **24 PASS** (goldens, SHA-256, capability ban, U-09 isolation).

## 17. M2 regression

All M2 unit tests retained and PASS; M2 differential PASS.

## 18. Security audit

| Check | Result |
|---|---|
| Lambda/Call → host/FS/net/process | none |
| authorize/derive/journal | not called |
| Cap mint via Function | none |
| Domain collapse machine↔data | none |

## 19. Determinism audit

Repeated evaluate / observations agree. Env = ordered vec (no HashMap iteration).

## 20. Dependency audit

| Edge | Status |
|---|---|
| Forbidden list | **0 hits** |
| `ror-reference` → `ror-core` only | FACT |
| No new Cargo edges beyond existing graph | FACT |

## 21. U-02 status

```text
U-02 = OPEN
frame serialization = NOT IMPLEMENTED
```

## 22. U-09 status

```text
U-09 = OPEN
machine::Value ≠ types::Value
Function remains machine-domain only
```

## 23. Toolchain

`rustc`/`cargo` **1.88.0**, `RUSTUP_TOOLCHAIN=ror-stable`.

## 24. Repository gates

| Gate | Result |
|---|---|
| `cargo fmt --check` | PASS |
| `cargo check --workspace` | PASS |
| `cargo test --workspace` | PASS (24 core + 42 runtime + 5 ref + 31 differential) |
| `cargo clippy … -D warnings` | PASS |
| Forbidden deps | PASS |
| Unsafe | none |
| Host effects in CEK | none |

## 25. Discrepancies

| Item | Class |
|---|---|
| cost_C / REQ-CEK-022 not wired | DISCLOSED LIMITATION |
| Deep-call stress N=64 nested identities (not 50k) | DISCLOSED LIMITATION |
| C-75 Environment vs Snapshot — in-memory Environment used | DISCLOSED (preflight) |
| state/ BOOTSTRAP drift | pre-existing |
| check.py S7 | pre-existing tooling |

No blocker-class discrepancy.

## 26. Corrections

Deep-call test rewritten from exponential thunk-chain to nested identity applications (test-only; semantics unchanged).

## 27. Evidence classification

| Kind | Label |
|---|---|
| Implementation | **IMPLEMENTED** (repository) |
| Unit / differential tests | **TESTED** (repository) |
| R-REG VERIFIED / PROVEN | **NOT CLAIMED** |
| M3 semantic verification | **NOT CLAIMED** |
| R-REG statuses | **184 × SPECIFIED** |

## 28. Final implementation state

```text
M0                         GREEN
M1 frozen subset           ACCEPTED WITH DISCLOSED EVIDENCE LIMITATIONS
M1 full                    NOT COMPLETE
M2 preflight               GREEN WITH DISCLOSED LIMITATIONS
M2 implementation          ACCEPTED WITH DISCLOSED EVIDENCE LIMITATIONS
M2 semantic verification   NOT CLAIMED
M3 preflight               GREEN WITH DISCLOSED LIMITATIONS
M3 implementation          COMPLETE WITH DISCLOSED EVIDENCE LIMITATIONS
M3 semantic verification   NOT CLAIMED
R-REG                      184 × SPECIFIED
```

## 29. Next authorized operation

```text
NEXT = M3 IMPLEMENTATION REVIEW
```

Not M4. Do not promote R-REG. Do not resolve U-02/U-09.
