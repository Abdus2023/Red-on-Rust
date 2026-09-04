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

---

## 30. Control addendum — arity-order gate & source-of-truth (post-implementation audit)

This section records the **M3 IMPLEMENTATION CONTROL ADDENDUM** lookup against canonical authority.
It does **not** change CEK semantics. Implementation commit `087c289` was verified to already
implement the canonically established ordering.

### 30.1 M3 ARITY-ORDER GATE

```text
M3 ARITY-ORDER GATE
```

| Field | Record |
|---|---|
| **Canonical ordering** | After operator evaluates to `FunctionValue`, arity is checked **BEFORE any argument expression is evaluated**. On mismatch: `fault(F_arity)` / `Fault::ArityMismatch`; **0** argument evaluations. |
| **Outcome** | **ARITY ORDER = CANONICALLY ESTABLISHED** (Outcome 1) |
| **Evidence** | See SOURCE-OF-TRUTH RECORD below |
| **Requirement IDs** | R-CEK-05; R-ORDER-02 (M3 acceptance includes arity precheck) |
| **Atomic obligation IDs** | **REQ-CEK-014** (primary); REQ-CEK-013 (LTR sequence constrained by 014); tag `CEK-CALL-ARITY-PRECHECK` |
| **OAD interaction** | **NOT APPLICABLE** — no open OAD decides arity-vs-args order |
| **Implementation consequence** | In `resume_call_function` / reference `WaitingOp` delivery: compare `args.len()` to `params.len()` **before** pushing `CallArgument` / `WaitingArg` or stepping any arg expr |
| **Differentiating test** | `call(lambda(&[], int(1)), vec![var(99)])` → `ArityMismatch{expected:0,actual:1}` **not** `UnboundVariable(99)`. Companion: correct arity + unbound arg → `UnboundVariable`. Production: `arity_mismatch_before_arg_eval` + `arity_ok_then_arg_fault`. Differential: `m3::arity_before_arg_eval`. |

```text
ARITY-ORDER GATE = PASS
```

### 30.2 SOURCE-OF-TRUTH RECORD — arity ordering

| Field | Content |
|---|---|
| **Question** | When a `Call` has an arity mismatch, are argument expressions evaluated before the arity mismatch is produced, or is arity checked before argument evaluation? |
| **Canonical requirement(s)** | **R-CEK-05** (`final/01` S-08): steps (1) eval func; (2) args LTR; (3) pre-check arity — mismatch ⇒ `fault(F_arity)` **before frame stack allocation**; (4) bind; (5) body. Reading: arity gate sits after function value is known and **before** argument evaluation / CallArgument frames. |
| **Atomic obligation(s)** | **REQ-CEK-014**: “Arity mismatch is detected immediately after function evaluation and **BEFORE any argument evaluation**.” Postcondition: “mismatch faults before any argument is evaluated.” Verification: `CEK-CALL-ARITY-PRECHECK`; mutation M002. **REQ-CEK-013**: LTR `function → arg₀ → … → apply` — depends on REQ-CEK-014 (arity does not reorder past the precheck). |
| **Canonical section** | `final/01` R-CEK-05; `req/01-registry-part2-semantics.md` REQ-CEK-013/014; `final/04` tag `CEK-CALL-ARITY-PRECHECK`: “Arity mismatch after function eval, **before any arg eval**; 0 arg evals, 0 host calls, 0 budget mutations on mismatch”. |
| **Relevant OAD** | None OPEN that selects arity order. |
| **Relevant invariant** | Security: evaluating args first could later trigger effects/budget on a call that cannot proceed (REQ-CEK-014 SECURITY-IMPACT). Pure M3 has no effects yet; ordering still frozen. |
| **Relevant dependency authority** | MOD-05 / `ror-runtime`; no new edges. |
| **Authoritative interpretation** | **Arity check BEFORE argument evaluation.** Sequence of separable events: (a) operator evaluation → FunctionValue; (b) arity determination; (c) iff match, argument evaluation LTR; (d) parameter binding in closure env; (e) body evaluation; (f) result via value-return. |
| **Implementation consequence** | Already present in `087c289` production + reference; no edit required. |
| **Test consequence** | Distinguishing tests already present (see gate table). Reversal (eval unbound arg then arity) would fail those tests. |
| **Evidence limitation** | Fault label `ArityMismatch` is deterministic shared P/R spelling for `F_arity` (preflight disclosure); not an OAD resolution. Full M002 mutation harness may run in a later gate. |

### 30.3 Event separation (implemented)

| Event | Production locus | Reference locus |
|---|---|---|
| Operator evaluation | `enter_call` → eval func under caller env | `Call` → `WaitingOp` |
| Arity determination | `resume_call_function` before any arg | `WaitingOp` + Function branch before arg kont |
| Argument evaluation | `CallArgument` frames, LTR | `WaitingArg` |
| Parameter binding | `apply_function` extends closure env | `install_body` |
| Body evaluation | `state.expr = body` | `state.expr = body` |
| Result propagation | `continue_with_value` / residual K | `deliver` / residual kont |

### 30.4 Pre-edit checklist status (audit against addendum)

Completed as **post-facto verification** that `087c289` was authorized by M3-PREFLIGHT and matches canonical arity order. Blocking items:

| Item | Status |
|---|---|
| Repository identity / start from `759fb26` preflight | **PASS** (impl parent) |
| M3-PREFLIGHT / M2-REVIEW / M2-PROGRESS read | **PASS** |
| R-ORDER-02, R-CEK-04/05, REQ-CEK-008…017 located | **PASS** |
| Arity-ordering resolved (canonical) | **PASS** |
| U-02 / U-09 OPEN preserved | **PASS** |
| Reference independence | **PASS** |
| No OAD silent resolve / no R-REG promotion / no canonical edit | **PASS** |
| Security pure / M4 excluded | **PASS** |
| Distinguishing arity tests | **PASS** |
| Toolchain 1.88.0 ror-stable | **PASS** |

```text
PRE-EDIT AUTHORIZATION = GRANTED
(authorization basis: M3-PREFLIGHT GREEN WITH DISCLOSED LIMITATIONS @ 759fb26;
 arity-order gate PASS against REQ-CEK-014 / R-CEK-05 / CEK-CALL-ARITY-PRECHECK;
 implementation 087c289 conforms — no semantic repair required)
```

### 30.5 Non-negotiable rule compliance

```text
CANONICAL DECISION EXISTS (arity before args)
        ↓
IMPLEMENT IT  — done in 087c289; verified by this audit
```

No canonical decision was invented. No CEK change in this control-addendum commit.
