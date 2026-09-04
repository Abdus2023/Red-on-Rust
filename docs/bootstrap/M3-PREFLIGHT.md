# M3 Preflight

**Operation type:** M3 PREFLIGHT / implementation authorization only.  
**M3 implementation in this operation:** **NOT STARTED** (FACT).  
**Do not implement Lambda/Call in this commit.**

Evidence labels: **FACT** | **DERIVED** | **DISCLOSED LIMITATION** | **BLOCKER** | **AUTHORIZATION**

---

## 1. Reviewed repository state

| Item | Value | Class |
|---|---|---|
| Branch | `arena/01a06993-red-on-rust` | FACT |
| HEAD | `711ddbd6331623f4a350fcc2492547199f6b95e8` | FACT |
| Subject | `review: reconcile M2 implementation evidence` | FACT |
| M2 implementation commit | `d57d8aabd128bc1735ecfbe14be1bdeaa0652e0c` | FACT |
| Remote `refs/heads/arena/01a06993-red-on-rust` | `711ddbd` (matches HEAD) | FACT |
| Working tree | clean | FACT |
| `docs/bootstrap/M2-REVIEW.md` | present | FACT |
| Fetch | `git fetch origin arena/01a06993-red-on-rust` — tip identical | FACT |

No silent reset/rebase/merge. No repository-state discrepancy that invalidates M2 evidence.

---

## 2. M2 baseline

From `docs/bootstrap/M2-REVIEW.md` (not reinterpreted):

```text
M2 IMPLEMENTATION          = ACCEPTED WITH DISCLOSED EVIDENCE LIMITATIONS
M2 semantic verification   = NOT CLAIMED
R-REG                      = 184 × SPECIFIED
U-02                       = OPEN
U-09                       = OPEN
```

| Prerequisite | Status | Class |
|---|---|---|
| M2 preflight GREEN WITH DISCLOSED LIMITATIONS | yes | FACT |
| M2 pure CEK Value/Var/Let/Seq/If | implemented @ `d57d8aa` | FACT |
| M2 review accepted-with-limitations | `711ddbd` | FACT |
| Production reference + differential | present | FACT |
| M1 regression green under current gates | yes (this preflight) | FACT |
| M2 disclosed limitations preserved | yes (listed §20) | AUTHORIZATION |

---

## 3. Canonical M3 scope

### Milestone acceptance (canonical)

| Source | Text | Class |
|---|---|---|
| `final/01` **R-ORDER-02** | **M3 Lambda / Call** — `closure capture, application LTR, arity precheck pass` | FACT |
| `final/04` milestone row | **M3** — tags `CEK-CALL-ARITY-PRECHECK`, `CEK-CALL-ARGS-LTR`, `CEK-CLOSURE-LEXICAL-CAPTURE` + deep-call stress | FACT |
| `mod/05-evaluator.md` | M3 = tag trio + Lambda/Call; deep-call stress | FACT |

### Primary requirements

| ID | Statement (short) | Owner crate | Class |
|---|---|---|---|
| **R-CEK-04** | Lambda pure/deterministic; capture lexical env; `FunctionValue { params, body, env }`; ordinary value-return (no immediate Halt) | `ror-runtime` | FACT |
| **R-CEK-05** | Call LTR: (1) eval `func` → FunctionValue; (2) args LTR; (3) arity precheck **before** any arg eval → `fault(F_arity)`; (4) bind params in fresh child of **closure** env; (5) push return path / eval body | `ror-runtime` | FACT |
| **R-CEK-03** (Call frames) | `CallFunction { args, env }`, `CallArgument { function, evaluated, remaining, caller_env }`; **closure env ≠ caller_env** | `ror-runtime` | FACT |
| R-CEK-01/02/06/07 | Explicit CEK, value-return, ±1 K on pure steps, progress/preservation (extend to call pure steps) | runtime | DERIVED extend |
| R-CALC-01 | `Function(FunctionValue)` in machine Value | `ror-core` | FACT (type already present) |
| R-CALC-02 | `Lambda` / `Call` constructors | `ror-core` | FACT (AST already present) |
| R-CALC-03 | Symbol identity | core | FACT |
| R-BUDGET-16 | pure CEK **call** has `δ_t = 0` | — | FACT |
| R-REF-02 | Independent reference model | `ror-reference` | FACT |
| R-ORDER-03 | *Later* security gate: full Value…Call differential before effects — **not** M3 entry gate | process | DERIVED (post-M3 / pre-effects) |

### Out of M3 scope (DERIVED)

| Concern | Milestone |
|---|---|
| Attenuate / Request* / effects / host | M4+ |
| Actors / scheduler / spawn/send/receive | M6-ish |
| Frame/GlobalState byte codecs | U-02 — not M3 acceptance |
| R-REG promotion | never in implementation sprint alone |

**Authorized M3 expression evaluation surface (DERIVED):**

```text
M2 surface ∪ { Lambda { params, body }, Call { func, args } }
```

---

## 4. Requirement / obligation mapping

| Obligation | Statement (short) | M3 sprint? |
|---|---|---|
| REQ-CEK-008 | closure env ≠ caller_env | **YES** |
| REQ-CEK-009 | Lambda pure/deterministic | **YES** |
| REQ-CEK-010 | Lambda captures lexical env at creation | **YES** |
| REQ-CEK-011 | produces `FunctionValue { params, body, env }` | **YES** |
| REQ-CEK-012 | Lambda via value-return (not immediate Halt) | **YES** |
| REQ-CEK-013 | Call order function → args LTR → apply | **YES** |
| REQ-CEK-014 | Arity after function, **before** any arg eval | **YES** |
| REQ-CEK-015/016 | Apply in closure env; `ρ' = ρ_closure[xi↦vi]` | **YES** |
| REQ-CEK-017 | Caller env MUST NOT resolve free vars in body | **YES** |
| REQ-CEK-018/019/023 | ±1 K; no silent discard; single pop path | **YES** (extend) |
| REQ-CEK-020/021 | Progress/preservation | pure-subset claim only |
| REQ-CEK-001…007 | EvalState, value-return, pure frames | already M2; keep |
| REQ-CEK-022 | E-Call budget `cost_C` / `B_f` | **PARTIAL** — δ_t=0 required; full cost algebra may lag (**DISCLOSED**) |
| REQ-CEK-024 | no FS/net; side-effect vocab only RequestEffect | **YES** — M3 still pure (no Request) |

Verification tags (final/04): `CEK-CALL-ARITY-PRECHECK`, `CEK-CALL-ARGS-LTR`, `CEK-CLOSURE-LEXICAL-CAPTURE`; mutations M001, M002, M003 (registry MOD-16 — kill targets for later gate, not day-1 blockers).

---

## 5. M2 boundary verification

Mechanical search @ `711ddbd`:

| Probe | Result | Class |
|---|---|---|
| `enter_lambda` / `enter_call` / `resume_call` / `apply_function` | **absent** | FACT |
| `FunctionValue {` construction in evaluators | **absent** (type decl only in `machine.rs`) | FACT |
| `Expr::Lambda` / `Call` in runtime/reference | **only** `UnsupportedInM2` fault arms + tests | FACT |
| M2 supported surface | Value/Var/Let/Seq/If | FACT |

**No M3 semantic leakage from M2.** Type names and unsupported markers are not implementation.

---

## 6. M3 semantic readiness

| Topic | Sufficiently specified? | Authority |
|---|---|---|
| Lambda → FunctionValue + capture | **YES** | R-CEK-04, REQ-CEK-009…012 |
| Value-return for Lambda | **YES** | R-CEK-02 + REQ-CEK-012 |
| Call LTR + frames | **YES** | R-CEK-05, R-CEK-03, REQ-CEK-013 |
| Arity before args | **YES** | REQ-CEK-014, tag CEK-CALL-ARITY-PRECHECK |
| Closure vs caller env | **YES** | REQ-CEK-008/015/016/017, tag CEK-CLOSURE-LEXICAL-CAPTURE |
| δ_t(call)=0 | **YES** | R-BUDGET-16 |
| Exact `Fault` variant spelling for arity | **implementation choice** among sketches (`ArityMismatch` / `F_arity`) — must be deterministic & shared P/R | DISCLOSED LIMITATION (not OPEN OAD blocking transitions) |
| “Push return frame” wording vs frozen 9-frame set | **DERIVED:** no separate Return frame in R-CEK-03; body runs under residual K after Call* frames complete; value-return is R-CEK-02 | PASS (not blocker) |
| Full `cost_C(call)+cost_C(B_f)` | table not required for M3 acceptance text | DISCLOSED (same class as M2 cost_C) |
| FunctionValue.env Snapshot vs Environment (C-75) | See §11 | DISCLOSED — in-memory capture of immutable `Environment` aligns with R-CEK-04 + later source comments |

**No STOP — M3 SCOPE UNRESOLVED.**

---

## 7. Lambda preflight

| Question | Canonical answer | Class |
|---|---|---|
| How Lambda evaluates | Produce `FunctionValue { params, body, env }` with `env` = current lexical environment | R-CEK-04 |
| What value | Machine `Value::Function(...)` | R-CALC-01 |
| Capture | Lexical env **at creation** (clone of current `Environment` under M2 env model) | REQ-CEK-010 |
| Immediate Halt? | **MUST NOT** — ordinary value-return | REQ-CEK-012 |
| Side effects | Pure; no authorize/host | REQ-CEK-009 |
| Closure identity observability | Structural `PartialEq` on FunctionValue components is an **impl/test** choice; semantics care about capture+apply behavior, not pointer identity | DISCLOSED |
| Capability in captured env | CapRef may appear as machine values; evaluator must not inspect authority (R-TRUST-03). Marshal of closures is **out of M3** (R-MARSHAL-06 at boundary later) | DERIVED |
| Determinism | Same env+params+body → same FunctionValue structure; R-CORE-08 operational | REQ-CEK-009 |

---

## 8. Call preflight

| Step | Canonical rule | Class |
|---|---|---|
| 1 | Eval `func` first under **caller** env; expect `FunctionValue` else type fault | R-CEK-05 (1) |
| 2 | Frame `CallFunction { args, env: caller_env }` while evaluating func | R-CEK-03 |
| 3 | On function value: **arity check** vs `params.len()` **before** any arg eval | REQ-CEK-014 |
| 4 | If arity OK and args non-empty: push `CallArgument { function, evaluated, remaining, caller_env }`; eval next arg under **caller_env** | R-CEK-05 (2), REQ-CEK-013 |
| 5 | Args left-to-right until none remain | CEK-CALL-ARGS-LTR |
| 6 | Apply: `ρ' = ρ_closure[xi↦vi]`; eval body in `ρ'` | REQ-CEK-016 |
| 7 | Free vars in body resolve in closure env only | REQ-CEK-017 |
| 8 | Result via ordinary value-return / residual K | R-CEK-02 |
| Non-function | Type fault (deterministic identity) | sketches + R-CEK-05 premise |
| Zero args | Arity 0 match → apply immediately with empty arg list | DERIVED from R-CEK-05 |

---

## 9. Evaluation-order preflight

Canonical order is **explicit** (not inferred from Rust):

```text
function  →  arg₀  →  arg₁  → … →  argₙ  →  apply
```

| Property | Specified? |
|---|---|
| Operator before arguments | **YES** (R-CEK-05) |
| Arguments LTR | **YES** (REQ-CEK-013) |
| Args under caller_env | **YES** (CallArgument.caller_env) |
| Body under closure env + params | **YES** (REQ-CEK-016) |
| Arity fault short-circuits args | **YES** (REQ-CEK-014) — 0 arg evals, 0 host, 0 budget mutations on mismatch (tag) |
| Fault propagation from func/args | via normal step Fault | DERIVED from CEK |

---

## 10. U-02 assessment

| Question | Answer | Class |
|---|---|---|
| Does M3 acceptance require frame/closure **byte** codecs? | **NO** — R-ORDER-02 M3 is capture/LTR/arity | DERIVED |
| Does Call introduce new frames needing wire tags? | CallFunction/CallArgument are in-memory only under U-02 OPEN | FACT/DERIVED |
| C-75 recovery encoding of FunctionValue.env | OPEN concern for **persistence/recovery**, not pure M3 step | DISCLOSED |
| M3 blocked by U-02? | **NO** if sprint stays in-memory (same rule as M2) | AUTHORIZATION |

```text
U-02 = OPEN
M3 frame/closure serialization = NOT REQUIRED FOR M3 AUTHORIZATION
```

If an M3 sprint claims snapshot/WAL of closures: **STOP — M3 BLOCKED BY U-02**.

---

## 11. U-09 assessment

| Question | Answer | Class |
|---|---|---|
| Machine vs data Value still distinct? | **YES** @ HEAD | FACT |
| From/Into collapse? | **none** | FACT |
| Does FunctionValue pressure merge domains? | Function is **machine-only** (R-CALC-01); 15A data domain has no Function | FACT |
| Serialization reuse of Function through data codec? | **FORBIDDEN** for M3 — would violate U-09/R-CANON domain split | AUTHORIZATION |
| M3 blocked by U-09? | **NO** if Function stays in `machine::Value` only | AUTHORIZATION |

```text
U-09 = OPEN
machine::Value ≠ types::Value  (preserved)
```

---

## 12. Reference-model independence

| Constraint | Status |
|---|---|
| `ror-reference` → `ror-core` only today | FACT |
| Forbidden: reference → runtime/kernel/persistence/host/agent | absent | FACT |
| M3 may add independent Lambda/Call transitions in `pure_cek` (or sibling module) | AUTHORIZATION |
| Must not import production CEK helpers | R-REF-02 | AUTHORIZATION |
| Shared fixtures/types from `ror-core` | ALLOWED | FACT |

**Reference independence can be maintained** for M3.

---

## 13. Differential-testing readiness

Minimum M3 differential surface (**DERIVED** from R-ORDER-02 / final/04 / tags):

| Case family | Tags / reqs |
|---|---|
| Lambda → FunctionValue; value-return under Let | R-CEK-04, REQ-CEK-012 |
| Closure free-var vs caller shadow | CEK-CLOSURE-LEXICAL-CAPTURE |
| Call 0-arg / N-arg LTR | CEK-CALL-ARGS-LTR |
| Arity mismatch: 0 arg steps | CEK-CALL-ARITY-PRECHECK |
| Nested call / nested lambda | R-CEK-05 |
| Non-function call fault | type fault |
| Body result propagation | R-CEK-02 |
| Deep-call stress (depth) | final/04 M3; R-CEK-01 method |

Observation: terminal Halted/Fault (extend M2 harness); optional trace events for LTR/arity **when** needed to make order observable (tag allows trace) — impl choice for observation richness, not new semantics.

Harness: `ror-differential` black-box both SUTs — **ready** to extend; no design blocker.

---

## 14. Security assessment

| Risk | M3 pure handling | Class |
|---|---|---|
| Closure captures CapRef | Allowed as opaque machine data; no kernel authorize in pure Call | DERIVED |
| Cap amplification via apply | No — apply only binds values; no derive/grant | DERIVED |
| Ordinary data path minting authority | Still forbidden (R-CANON-12 / R-MARSHAL) — out of pure CEK | FACT |
| `Untrusted Input ↛ Authority ↛ External Effect` | Held: Lambda/Call add **no** host/effect edge | AUTHORIZATION |
| R-MARSHAL-06 on FunctionValue.env | Applies at **marshal** boundary (later); M3 pure need not marshal | DISCLOSED scope split |

**No STOP — SECURITY SEMANTICS REQUIRE SEPARATE AUTHORIZATION** for pure M3 Lambda/Call.

---

## 15. Determinism assessment

| Source | M3 risk | Mitigation |
|---|---|---|
| Env capture | clone association list — order stable | already M2 |
| Arg evaluation order | frozen LTR | tests + frames |
| HashMap | **forbid** in env/closure | same as M2 |
| Function pointer identity | do not use addresses as semantic identity | AUTHORIZATION |
| Error ordering | arity before args removes order ambiguity | REQ-CEK-014 |
| U-35 theorem | still OPEN — no VERIFIED claim | DISCLOSED |

---

## 16. Dependency / module assessment

| Edge | Classification | M3 need |
|---|---|---|
| `ror-core` → `ror-runtime` (TYPE) | **REQUIRED** | already present |
| `ror-core` → `ror-reference` | types | already present |
| runtime → reference | **FORBIDDEN** | must not add |
| reference → runtime | **FORBIDDEN** | must not add |
| runtime → kernel/persistence | present; pure M3 **must not call** | DISCLOSED (same as M2) |

Ownership: **MOD-05** / `ror-runtime` implements CEK; **MOD-01** / `ror-core` holds FunctionValue/Expr; **MOD-14** reference; **MOD-15** differential.

No UNCLASSIFIED edge required for M3 pure subset.

---

## 17. API / visibility assessment

| Item | Guidance |
|---|---|
| CallFunction / CallArgument frames | Prefer non-public or `pub(crate)`; provisional under U-02 |
| `FunctionValue` | Already pub in machine module — keep provisional docs |
| `step` / `evaluate` | May remain pub for harness |
| New constructors | No host callbacks in Expr (R-CALC-02) |
| Default visibility | private → pub(crate) → pub only if required |

Do not freeze Call frames as wire ABI.

---

## 18. Toolchain and repository gates

Executed this preflight (`rustc`/`cargo` **1.88.0**, `RUSTUP_TOOLCHAIN=ror-stable`):

| Gate | Result |
|---|---|
| `cargo fmt --check` | **PASS** |
| `cargo check --workspace` | **PASS** |
| `cargo test --workspace` | **PASS** (24 core + 21 runtime + 2 ref + 11 diff) |
| `cargo clippy … -D warnings` | **PASS** |
| Forbidden deps | **0** |
| `unsafe` in crates | **none** |
| R-REG statuses | **184 × SPECIFIED** unchanged |

Gates = tooling/regression evidence, **not** M3 semantic verification.

---

## 19. Evidence-model reconciliation

| Item | Status |
|---|---|
| R-REG | **184 × SPECIFIED** — no promotion |
| M2 semantic verification | **NOT CLAIMED** (preserved) |
| M3 preflight | readiness only |
| Future M3 tests | repository evidence until authorized ledger transition |
| `state/` BOOTSTRAP drift | pre-existing **DERIVED-STATE DRIFT** |
| `check.py` S7 | pre-existing tooling FAIL (workspace vs pipeline) |

```text
cargo test PASS  ⇏  R-REG VERIFIED
M3 PREFLIGHT GREEN  ⇏  M3 semantically verified
```

---

## 20. Discrepancies

| ID | Classification | Notes |
|---|---|---|
| C-75 EnvironmentSnapshot vs Environment | **NON-BLOCKING DISCLOSURE** | Pure M3 uses immutable `Environment` capture (R-CEK-04); recovery encoding stays U-02 |
| REQ-CEK-022 full cost_C | **NON-BLOCKING DISCLOSURE** | δ_t=0 fixed; debit algebra may stub |
| Arity fault variant spelling | **NON-BLOCKING DISCLOSURE** | Choose one deterministic label; share P/R |
| Deep-call 50k–100k vs host Drop | **NON-BLOCKING DISCLOSURE** | Plan stress; may need arena Expr later — not preflight blocker |
| state/ + check.py S7 | **DERIVED-STATE DRIFT** / **TEST/TOOLING DEFECT** | pre-existing |
| R-ORDER-03 full gate | **NON-BLOCKING** | After M3 close / before effects — not M3 entry |

**No BLOCKER** for pure M3 authorization.

---

## 21. Corrections

None. Preflight is documentation-only. No code, registry, OAD, or semantic edits.

---

## 22. Authorization decision

```text
M3 PREFLIGHT = GREEN WITH DISCLOSED LIMITATIONS — IMPLEMENTATION AUTHORIZED
```

**Meaning (AUTHORIZATION):**

- Canonical M3 scope is determined: **Lambda + Call** with closure capture, LTR application, arity precheck (R-ORDER-02, R-CEK-04/05, REQ-CEK-008…017).
- M2 baseline accepted; boundaries (U-02 in-memory, U-09 domain split, reference independence, pure/no effects) hold.
- Implementation may proceed in a **separate M3 IMPLEMENTATION SPRINT** only within this surface.
- M3 implementation remains **NOT STARTED** by this commit.
- Disclosed limitations must be respected (no frame codecs, no Value collapse, no R-REG promotion, cost_C may lag, deep-call evidence may be bounded).

**Not authorized without new preflight/addendum:** effects, attenuate, actors, frame byte codecs, OAD closes, registry promotion, production↔reference coupling.

---

## 23. Commit decision

All §21 commit conjuncts hold (preflight-only artifact; no M3 code; no M2 behavior change; no OAD/R-REG/canonical mutation; gates green; report complete; decision authorized-with-limitations).

```text
COMMIT = PERMITTED
```

---

## 24. Next authorized operation

```text
NEXT = M3 IMPLEMENTATION
```

Separate sprint. Deliverables (example, not exhaustive):

- `ror-runtime`: Lambda enter; CallFunction/CallArgument; arity precheck; apply in closure env  
- `ror-core`: Fault arity variant if needed; no domain collapse  
- `ror-reference`: independent Lambda/Call transitions  
- `ror-differential`: M3 cases + tag-oriented tests  
- unit/structural/negative/determinism; preserve M2 suite  
- **no** M4 effects; **no** U-02 codecs; **no** R-REG edits  

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
M3 implementation          NOT STARTED
R-REG                      184 × SPECIFIED
```

---

## Implementation boundary summary (for the next sprint)

| M3 target | Authority | Crate | OAD constraint | Auth |
|---|---|---|---|---|
| Lambda → FunctionValue + capture | R-CEK-04, REQ-CEK-009…012 | runtime + core types | U-09 machine only | **YES** |
| Call LTR + Call* frames | R-CEK-05, R-CEK-03, REQ-CEK-013…017 | runtime | U-02 in-memory frames | **YES** |
| Arity precheck | REQ-CEK-014, CEK-CALL-ARITY-PRECHECK | runtime | — | **YES** |
| Lexical free vars | CEK-CLOSURE-LEXICAL-CAPTURE | runtime + ref | — | **YES** |
| Reference Lambda/Call | R-REF-02 | ror-reference | no prod import | **YES** |
| Differential M3 surface | final/04 M3 | ror-differential | — | **YES** |
| Frame/closure bytes | REQ-CEK-003 / U-02 | — | **U-02 OPEN** | **NO** |
| Effects / Attenuate | M4+ | — | — | **NO** |
| R-REG promotion | reg model | — | — | **NO** |
