# M3 Implementation Review

**Operation:** M3 IMPLEMENTATION REVIEW & EVIDENCE RECONCILIATION  
**Do not implement M4. Do not redesign M3. Do not promote R-REG. Do not resolve OADs.**

---

## 1. Review identity

| Field | Value | Class |
|---|---|---|
| Branch | `arena/01a06993-red-on-rust` | FACT |
| Review HEAD (pre-report) | `c224bb852937cc172ab84d389e0393040a2735f2` | FACT |
| Working tree | clean at review start | FACT |
| Remote tip | `c224bb8` (matches HEAD) | FACT |
| Operation type | review only — no CEK semantic edits | AUTHORIZATION |

## 2. Implementation commit

```text
087c28903c818f36330cfe0a3db98f131419163c
feat: implement M3 lambda and call semantics
```

**FACT** — sole M3 CEK implementation tip under review.

## 3. Preflight commit

```text
759fb2649c558a9bb4e42bdcc9e13d98738e4cc1
preflight: authorize M3 implementation scope
```

Decision: `GREEN WITH DISCLOSED LIMITATIONS — IMPLEMENTATION AUTHORIZED`.

## 4. Control-addendum commit

```text
c224bb852937cc172ab84d389e0393040a2735f2
docs(m3): record arity-order gate and source-of-truth lookup
```

Documents `ARITY-ORDER GATE = PASS` (docs only; no CEK change).

## 5. Repository state

| Check | Result |
|---|---|
| `087c289`, `c224bb8`, `759fb26` present | PASS |
| `docs/bootstrap/M3-PROGRESS.md` present | PASS |
| `docs/bootstrap/M3-PREFLIGHT.md` present | PASS |
| No silent history rewrite | PASS |
| `implementation commit ≠ review commit` | PASS (087c289 vs this review) |

---

## 6. Canonical M3 scope

| Authority | Scope text | Class |
|---|---|---|
| R-ORDER-02 | M3 Lambda/Call — closure capture, application LTR, arity precheck | FACT |
| R-CEK-04 | Lambda → FunctionValue + lexical capture + value-return | FACT |
| R-CEK-05 | Call LTR; arity precheck; bind in closure env; body | FACT |
| final/04 | tags CEK-CALL-ARITY-PRECHECK, CEK-CALL-ARGS-LTR, CEK-CLOSURE-LEXICAL-CAPTURE | FACT |
| M3-PREFLIGHT | `M2 ∪ { Lambda, Call }` | FACT |

**Out of scope (confirmed absent as semantics):** effects, host, actors, frame codecs, R-REG promotion.

**Diff `759fb26..087c289` classification:** AUTHORIZED M3 (runtime/reference/core Fault/diff) + DOCUMENTATION (M3-PROGRESS). No UNAUTHORIZED paths.

---

## 7. Source-of-truth lookup

### 7.1 Arity ordering

| Field | Content |
|---|---|
| **Question** | Arity before or after argument evaluation? |
| **Requirement** | **R-CEK-05**; R-ORDER-02 |
| **Obligation** | **REQ-CEK-014**: mismatch after function eval and **BEFORE any argument evaluation** |
| **Section** | `final/01` R-CEK-05; `req/01` REQ-CEK-014; `final/04` `CEK-CALL-ARITY-PRECHECK` |
| **OAD** | N/A |
| **Interpretation** | **Arity before args** (CANONICALLY ESTABLISHED) |
| **Note** | R-CEK-05 numbered list places “(2) args LTR (3) arity”; parenthetical + REQ-CEK-014 + verification tag fix order to **arity before arg eval / before CallArgument frames**. **ESTABLISHED BY CROSS-REFERENCE** to REQ-CEK-014 — not a residual conflict. |
| **Implementation** | `resume_call_function` / ref `WaitingOp` |
| **Tests** | `arity_mismatch_before_arg_eval`; `m3::arity_before_arg_eval` |

### 7.2 Lambda

| Field | Content |
|---|---|
| **Question** | What does Lambda produce; when is body run; what env is captured? |
| **Requirement** | **R-CEK-04** |
| **Obligations** | REQ-CEK-009…012 |
| **Interpretation** | Pure; capture current lexical env; `FunctionValue{params,body,env}`; ordinary value-return (no immediate Halt) |
| **Implementation** | `enter_lambda` → `continue_with_value` |
| **Tests** | `lambda_produces_function_and_halts`; `lambda_under_let_does_not_halt_early`; differential |

### 7.3 Call / binding / lexical

| Field | Content |
|---|---|
| **Question** | LTR order; env for args; env for body; free vars |
| **Requirement** | **R-CEK-05**, R-CEK-03 Call* frames |
| **Obligations** | REQ-CEK-008, 013, 015, 016, 017 |
| **Interpretation** | func first; args under **caller_env**; apply `ρ'=ρ_closure[xi↦vi]`; free vars not from caller |
| **Implementation** | `enter_call` / `resume_call_*` / `apply_function`; ref `WaitingOp`/`WaitingArg`/`install_body` |
| **Tests** | capture, shadow, nested, LTR multi-arg, caller-env args |

### 7.4 Non-callable / faults

| Field | Content |
|---|---|
| **Question** | Fault for non-Function operator / unbound arg / body |
| **Authority** | R-CEK-05 premises; sketches TypeError; UnboundVariable from M2 |
| **Interpretation** | TypeError expected Function; Unbound on arg/body; ArityMismatch on count |
| **OAD** | Fault spelling `ArityMismatch` for `F_arity` — DISCLOSED (preflight), shared P/R |

---

## 8. Arity-order gate verification

```text
M3 ARITY-ORDER GATE = PASS  (reconfirmed)
```

| Step | Production | Reference | Class |
|---|---|---|---|
| Enter Call | push CallFunction; expr←func | push WaitingOp; expr←func | PASS |
| After FunctionValue | arity check **before** CallArgument | arity check **before** WaitingArg | PASS |
| Mismatch | immediate `ArityMismatch` | same | PASS |
| Match + args | CallArgument LTR under caller_env | WaitingArg LTR | PASS |

**Distinguishing pair (FACT — tests PASS this review):**

| Expr | Expected | Observed |
|---|---|---|
| `call(λ().1, [var(99)])` arity 0≠1 | `ArityMismatch` | PASS (not Unbound) |
| `call(λ(x).x, [var(99)])` arity OK | `UnboundVariable(99)` | PASS |

Reversal (eval arg then arity) would fail the first test.

---

## 9. Lambda audit

| Property | Result | Class |
|---|---|---|
| Produces FunctionValue | yes | PASS |
| Body not run at creation | yes (value-return only) | PASS |
| Captures `state.env.clone()` | yes | PASS |
| Under Let continues via K | yes | PASS |
| No host/authority capture | yes | PASS |
| C-75 Snapshot vs Environment | in-memory `Environment` (immutable assoc list); no wire snapshot | DISCLOSED — observable capture semantics hold |

---

## 10. Call audit

| Path | Result | Class |
|---|---|---|
| Success identity / 0-arg / multi-arg | PASS | TESTED |
| Nested call / λ returning λ | PASS | TESTED |
| Too few / too many args | ArityMismatch | PASS |
| Non-callable | TypeError Function | PASS |
| Operator unbound | UnboundVariable | PASS |
| Arg unbound (arity OK) | UnboundVariable | PASS |
| Body unbound | UnboundVariable | PASS |
| Untaken If branch with Call | not evaluated | PASS |

---

## 11. Closure-capture audit

| Case | Result |
|---|---|
| Outer x=1; f=λ().x; x=2; f() → 1 | PASS (CEK-CLOSURE-LEXICAL-CAPTURE) |
| Param shadows capture | PASS |
| Two closures isolated | PASS |
| Dynamic scope (body in caller env) | **not** implemented | PASS |

---

## 12. Evaluation-order audit

| Property | Evidence | Class |
|---|---|---|
| Operator before args | step-level CallFunction before CallArgument | PASS |
| Args LTR | `remaining.remove(0)` / ref `rest.remove(0)` | PASS |
| No HashMap order | env = Vec assoc list | PASS |
| Multi-arg LTR values | differential `ltr_multi_arg_with_lets` | PASS |

**Note:** No pure “arg₁ side-effect before arg₂” oracle without effects; LTR is structural + multi-arg binding tests. **DISCLOSED LIMITATION** on observational richness (tags allow trace; terminal Eq still holds).

---

## 13. Parameter-binding audit

| Property | Result |
|---|---|
| zip params↔args LTR | PASS |
| Bind into **cloned closure env** | PASS (`function.env`, not caller) |
| M2 Let unchanged | PASS (regression) |
| Caller env restored via residual frames only | PASS |

---

## 14. CEK-machine audit

| Property | Result | Class |
|---|---|---|
| Stackless nesting in Continuation/kont | PASS | FACT |
| `step` non-recursive | PASS | FACT |
| Single pop path `continue_with_value` / `deliver` | PASS | REQ-CEK-023 |
| ±1 K on pure entry/resume | structural M2 tests retained | PASS |
| No separate Return frame | residual K (R-CEK-03 set) | PASS (preflight derivation) |
| Deep nested identity calls N=64 | PASS | DISCLOSED (not 50k) |

---

## 15. Fault audit

| Condition | Fault | Order |
|---|---|---|
| Arity mismatch | ArityMismatch | before args |
| Non-function | TypeError | after op value, before arity/args |
| Unbound op/arg/body | UnboundVariable | at lookup |
| M4+ | UnsupportedInM2 | — |

No panic/unwrap on eval paths. Precedence not invented beyond REQ-CEK-014 short-circuit.

---

## 16. Reference-independence audit

| Check | Result | Class |
|---|---|---|
| Cargo: reference → core only | FACT | PASS |
| No runtime/kernel/host/… | FACT | PASS |
| Shared transition helpers | **none** (fn name intersection empty) | PASS |
| Distinct kont types | WaitingOp/WaitingArg vs CallFunction/CallArgument | PASS |
| Algorithm structure | deliver/install_body vs resume_*/apply_function | PASS |

---

## 17. Differential-testing audit

| Surface | Module | Result |
|---|---|---|
| M2 Value/Var/Let/Seq/If | `m2` | PASS (10) |
| M3 Lambda/Call families | `m3` | PASS (21) |
| Compare P vs R (not P vs hardcoded alone) | `compare_m2` | PASS |
| Arity distinguishing case | `arity_before_arg_eval` | PASS |
| Capture / nested / faults | covered | PASS |

---

## 18. Mutation/testing audit

| Mutation intent | Coverage |
|---|---|
| Arity after args / skip arity | distinguishing tests |
| Capture caller env | closure_capture_not_caller |
| Reverse bind | multi-arg binding |
| Non-callable success | non_callable |
| Swallow faults | arg/body/op fault tests |

Full MOD-16 M001–M003 runner: **not executed** this review — **DISCLOSED LIMITATION** (kill conditions present in unit/diff).

---

## 19. U-02 audit

```text
U-02 = OPEN
frame serialization = NOT IMPLEMENTED
```

No Serialize/encode/WAL for frames. Debug only. **PASS**

---

## 20. U-09 audit

```text
U-09 = OPEN
machine::Value ≠ types::Value
```

| Check | Result |
|---|---|
| From/Into collapse | none |
| Function in machine domain only | FACT |
| Crate root Value = data domain | FACT |

**PASS** — no silent resolve.

---

## 21. Security audit

| Probe | Result |
|---|---|
| FS/net/process in CEK | none |
| HostExecutor / authorize / journal calls | none |
| Lambda/Call mint authority | no |
| `Untrusted ↛ Authority ↛ Effect` | held for pure M3 |

**PASS**

---

## 22. Determinism audit

Repeated evaluate/observations agree. Ordered env. No address identity as semantic Function id beyond structural Eq.

U-35 theorem still OPEN — **NOT CLAIMED**.

---

## 23. Dependency audit

| Edge | Class |
|---|---|
| runtime → core | REQUIRED | PASS |
| reference → core | ALLOWED (types) | PASS |
| differential → runtime, reference | verification | PASS |
| runtime → kernel, persistence | pre-existing; **unused** on pure paths | DISCLOSED |
| Forbidden list | **0 hits** | PASS |

---

## 24. API / visibility audit

| Item | Notes |
|---|---|
| `PureFrame` / Call* | pub provisional — **not** wire ABI (U-02) |
| `FunctionValue` | pub machine type |
| `step` / `evaluate` | pub for harness |
| Internals enter_*/resume_* | private | PASS |

No new public host surface.

---

## 25. Unsafe-code audit

```text
#![forbid(unsafe_code)]
rg \bunsafe\b crates → none
```

**PASS**

---

## 26. M1 regression

| Suite | Result |
|---|---|
| ror-core 24 tests | PASS |
| Goldens / SHA-256 / capability ban | PASS |

---

## 27. M2 regression

| Suite | Result |
|---|---|
| M2 CEK unit tests retained | PASS |
| M2 differential | PASS |
| Stackless Let/Seq stress | PASS |

---

## 28. Repository gates

Executed this review (`rustc`/`cargo` 1.88.0, `ror-stable`):

| Gate | Result |
|---|---|
| `cargo fmt --check` | **PASS** |
| `cargo check --workspace` | **PASS** |
| `cargo test --workspace` | **PASS** (24+42+5+31) |
| `cargo clippy … -D warnings` | **PASS** |
| Forbidden deps | **PASS** |
| Unsafe | **PASS** |
| check.py S7 | pre-existing FAIL (tooling drift) |

Gates ≠ semantic VERIFIED.

---

## 29. Evidence reconciliation

| Kind | Status |
|---|---|
| Implementation @ 087c289 | repository IMPLEMENTED |
| Unit + differential | repository TESTED |
| R-REG VERIFIED/PROVEN | **NOT CLAIMED** |
| M3 semantic verification | **NOT CLAIMED** |
| R-REG statuses | **184 × SPECIFIED** (FACT) |
| status-transitions ledger | empty transitions (unchanged) |

```text
cargo test PASS  ⇏  R-REG VERIFIED
M3 ACCEPTED      ⇏  formal verification
M3 ACCEPTED      ⇏  M4 authorized for implementation
```

---

## 30. OAD status

| OAD / item | Before | After review | Silently resolved? |
|---|---|---|---|
| U-02 | OPEN | OPEN | **NO** |
| U-09 | OPEN | OPEN | **NO** |
| U-26 StepResult | OPEN | OPEN provisional | **NO** |
| U-35 | OPEN | OPEN | **NO** |
| C-75 capture rep | open/disclosed | in-memory Environment | **NO** (semantics OK) |
| cost_C / REQ-CEK-022 | disclosed lag | lag remains | **NO** |
| deep-call depth | disclosed | N=64 stress | **NO** |
| state/S7 drift | pre-existing | unchanged | **NO** |

---

## 31. Discrepancies

| ID | Classification | Notes |
|---|---|---|
| R-CEK-05 list order vs REQ-CEK-014 | **NON-BLOCKING** | reconciled by REQ-CEK-014 + tag (control addendum) |
| cost_C not wired | **DISCLOSED LIMITATION** | δ_t=0 holds |
| Deep-call not 50k–100k | **DISCLOSED LIMITATION** | stackless structure holds |
| M001–M003 runner not run | **DISCLOSED LIMITATION** | unit/diff kill conditions present |
| LTR without effect traces | **DISCLOSED LIMITATION** | structural + binding tests |
| Public provisional frames | **DISCLOSED LIMITATION** | U-02 |
| state/ + check.py S7 | **DERIVED-STATE DRIFT** / tooling | pre-existing |

**No BLOCKER.**

---

## 32. Corrections

None affecting CEK semantics. This review adds **documentation only** (`M3-REVIEW.md`).

---

## 33. Final classification

```text
M3 IMPLEMENTATION = ACCEPTED WITH DISCLOSED EVIDENCE LIMITATIONS
```

**Rationale:** Canonical M3 Lambda/Call surface conforms (R-CEK-04/05, REQ-CEK-008…017); arity-before-args verified; lexical capture verified; reference independent; differential agrees; M1/M2 green; U-02/U-09 untouched; security pure. Residual gaps are evidence depth/tooling/budget algebra — not semantic defects.

Not unqualified `ACCEPTED` (disclosures material to evidence ceiling).  
Not `BLOCKED` (no conformance failure).

**M3 semantic verification = NOT CLAIMED.**

---

## 34. Commit decision

All §33 commit conjuncts hold (implementation reviewed; gates green; arity PASS; boundaries hold; report complete; classification accepted-with-limitations; commit = review artifact only).

```text
COMMIT = PERMITTED
```

---

## 35. Next authorized operation

```text
NEXT = M4 PREFLIGHT
```

**M4 IMPLEMENTATION = NOT AUTHORIZED** by this review. M4 preflight is a separate operation.

---

## Final state board

```text
M0                         GREEN
M1 frozen subset           ACCEPTED WITH DISCLOSED EVIDENCE LIMITATIONS
M1 full                    NOT COMPLETE
M2 preflight               GREEN WITH DISCLOSED LIMITATIONS
M2 implementation          ACCEPTED WITH DISCLOSED EVIDENCE LIMITATIONS
M2 semantic verification   NOT CLAIMED
M3 preflight               GREEN WITH DISCLOSED LIMITATIONS
M3 implementation          ACCEPTED WITH DISCLOSED EVIDENCE LIMITATIONS
M3 semantic verification   NOT CLAIMED
R-REG                      184 × SPECIFIED
M4                         NOT STARTED
```
