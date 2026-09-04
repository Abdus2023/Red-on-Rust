# M2 Preflight

**Operation type:** preflight / implementation authorization only.  
**M2 implementation in this operation:** **NOT STARTED** (FACT).  
**Report commit:** accompanies this file on `arena/01a06993-red-on-rust`.

Evidence category legend used below:

| Label | Meaning |
|---|---|
| **FACT** | Directly observed in repository or command output |
| **DERIVED** | Follows from canonical authorities by explicit citation |
| **DISCLOSED GAP** | Known incompleteness; does not by itself block pure-subset work |
| **BLOCKER** | Would make *any* M2 implementation unauthorized |
| **AUTHORIZATION** | Decision bound by this preflight |

---

## Repository state

| Item | Value | Class |
|---|---|---|
| Branch | `arena/01a06993-red-on-rust` | FACT |
| HEAD at preflight execution | `8d845118efca54ae4b57cf6f444e7a84d164597d` | FACT |
| Toolchain | `rustc 1.88.0` / `cargo 1.88.0` / `RUSTUP_TOOLCHAIN=ror-stable` | FACT |
| Working tree (pre-report) | clean | FACT |
| M2 CEK / evaluator code in `crates/` | **absent** (skeletons only outside `ror-core` M1 codec) | FACT |
| Silent M2 implementation detected | **NO** | FACT |

---

## M0/M1 prerequisite evidence

| Artifact | Present | Salient record | Class |
|---|---|---|---|
| `docs/bootstrap/M0-A-RECONCILIATION.md` | yes | M0-A GREEN; M0-B authorized | FACT |
| `docs/bootstrap/M0-B-VALIDATION.md` | yes | M0-B GREEN; M0 GREEN; M1 AUTHORIZED | FACT |
| `docs/bootstrap/M1-PROGRESS.md` | yes | progress note; ladder wording corrected by review | FACT |
| `docs/bootstrap/M1-REVIEW.md` | yes | see classification below | FACT |

### M1 review classification (authoritative bootstrap record)

```text
M1 FROZEN SUBSET = ACCEPTED WITH DISCLOSED EVIDENCE LIMITATIONS   (FACT — M1-REVIEW §13)
M1 full milestone = NOT COMPLETE                                  (FACT)
M2 = AUTHORIZED                                                   (FACT — review decision)
```

M1 review does **not** promote R-REG rows and does **not** resolve OADs (FACT — M1-REVIEW §12).

### M1 boundary this preflight preserves (DERIVED from M1-REVIEW + R-CANON)

- 15A BE envelope grammar; nested complete envelopes; map order; `DuplicateMapKey`
- Data-path capability ban (R-CANON-12); CapRef kernel path separate
- Digest = SHA-256 over canonical bytes (R-CANON-09)
- Independent R-CANON-11 vectors; supplemental vectors non-normative alone
- Data-domain `ror_core::Value` remains **provisional / not machine Value** (U-09)
- No second encoding; no M1 semantic rewrite smuggled as M2

If an M2 sprint needs to change those: **stop** and open an M1 change — not M2 scope (AUTHORIZATION rule).

---

## Canonical M2 scope derivation

### Milestone text (canonical)

| Source | Text | Class |
|---|---|---|
| `final/01` R-ORDER-02 | **M2 Pure CEK** — `Expr/Value/CEK step, environment, lexical capture, stackless frame invariants pass` | FACT |
| `final/04` milestone table | **M2** — `differential equivalence (production vs reference) for Value/Var/Let/Seq/If` | FACT |
| `mod/05-evaluator.md` | Conformance: **M2 pure-subset differential (Value/Var/Let/Seq/If)**; M3 = tag trio + Lambda/Call | FACT |
| `README.md` milestones | `M2 Pure CEK` then `M3 Lambda / Call` | FACT |

### Separation M2 vs M3 (DERIVED)

| Concern | Milestone | Primary requirements |
|---|---|---|
| CEK machine shell; Value/Var/Let/Seq/If steps; Env; frames `LetValue`/`Seq`/`If`; value-return; ±1 continuation on pure steps | **M2** | R-CEK-01, R-CEK-02, R-CEK-06 (pure), R-CEK-07 (pure subset), R-CALC-02 (constructors used), R-CALC-03, REQ-CALC-020, REQ-CEK-001…006, partial REQ-CEK-007 |
| Lambda, Call LTR, arity precheck, closure env ≠ caller env, Call* frames | **M3** | R-CEK-03 (Call* frames), R-CEK-04, R-CEK-05, tags `CEK-CALL-*`, M001–M003 |
| Attenuate / Request* frames; effects; actors | **M4+** | out of M2 |

**DERIVED authorized expression surface for M2 implementation sprints:**

```text
Expr ⊆ { Value(v), Var(s), Let{name,value,body}, Seq{first,second}, If{cond,then,else} }
```

Full `Expr` enum may be *declared* per R-CALC-02 with other constructors as **unimplemented stubs that fault** — but M2 must not implement Lambda/Call/Attenuate/Request/Spawn/Send/Receive/Yield semantics (those are later milestones). Prefer stubbing with an explicit `UnsupportedInM2` / phase-gate rather than partial wrong semantics (AUTHORIZATION).

### “Lexical capture” on M2 acceptance (DISCLOSED GAP / clarification)

M2 acceptance text includes “lexical capture” while Lambda is M3.

**DERIVED reading (not an OAD resolution):**

- **M2:** environment extension for `Let` (bind name → value in child env); `Var` lookup in env chain — *binding* lexical structure without closures.
- **M3:** `FunctionValue` capture of env at `Lambda` creation (R-CEK-04); free-var resolution in closure env (tag `CEK-CLOSURE-LEXICAL-CAPTURE`).

M2 must **not** implement `Lambda`/`FunctionValue` under a M2 label.

### Chain

```text
M2 scope (R-ORDER-02 + final/04 + mod/05)
    ↓
R-CEK-01..02, R-CEK-06 (pure), R-CEK-07 (pure), R-CALC-02/03, REQ-CALC-020, REQ-CEK-001..007 (subset)
    ↓
atomic: REQ-CEK-001..007, REQ-CALC-020 (+ supporting CALC type obligations as needed)
    ↓
module: MOD-05 EVALUATOR (owner); MOD-01 CORE (domain types); MOD-14/15 (diff later)
    ↓
crate: ror-runtime (CEK); ror-core (Expr/Value/Env/Symbol types — std only);
       ror-reference (independent pure-subset mirror — verification, not production dep)
    ↓
deps: ror-core → ror-runtime (REQUIRED TYPE); ror-reference ↛ production;
      ror-kernel/persistence edges exist in workspace but MUST NOT be exercised by pure M2 steps
    ↓
evidence: unit + structural + (for milestone close) differential Value/Var/Let/Seq/If
    ↓
authorized surface: in-memory pure CEK only; no host/FS/net; no capability authority calls
```

---

## Requirement mapping

| Requirement | M2 role | Status (registry) | Class |
|---|---|---|---|
| R-ORDER-02 | Defines M2 acceptance | SPECIFIED | FACT |
| R-CEK-01 | Explicit `EvalState`; no recursive host eval | SPECIFIED | FACT |
| R-CEK-02 | Value-return iff K empty / else Resume | SPECIFIED | FACT |
| R-CEK-03 | Frozen frame set (M2 uses **LetValue, Seq, If** only) | SPECIFIED | DERIVED subset |
| R-CEK-04 | Lambda — **M3**, not M2 implement | SPECIFIED | DERIVED out-of-scope |
| R-CEK-05 | Call LTR / arity — **M3** | SPECIFIED | DERIVED out-of-scope |
| R-CEK-06 | Pure transitions \|K\| ±1 | SPECIFIED | FACT |
| R-CEK-07 | Progress/preservation (pure configs) | SPECIFIED | DERIVED subset |
| R-CALC-01 | Machine Value domain (11 variants) | SPECIFIED | FACT — **U-09 open** |
| R-CALC-02 | Frozen Expr AST | SPECIFIED | FACT |
| R-CALC-03 | `Symbol(u32)` only in evaluator | SPECIFIED | FACT |
| R-CALC-08 | Σ / local config (as needed for EvalState) | SPECIFIED | DERIVED partial |
| REQ-CALC-020 | E-Let/E-Seq/E-If: δ_t=0, budget charge shape | SPECIFIED | FACT |
| R-BUDGET-06 / R-BUDGET-16 | pure CEK δ_t = 0 | SPECIFIED | DERIVED (time delta only; full budget algebra not M2 gate) |
| R-ARCH-03 / R-COMPILE-01 | `Block` ↛ `step()`; only ExecutablePlan | SPECIFIED | boundary: M2 `step` must not accept `Block` |
| R-CANON-* | M1 frozen; M2 consumes values, does not redefine bytes | SPECIFIED | FACT (M1 review) |
| R-REF-01/02 | Reference independence; optional parallel pure subset | SPECIFIED | DERIVED |

No requirement invented. Unknown non-goals stay UNKNOWN and out of sprint.

---

## Atomic obligation mapping

| Obligation | Statement (short) | M2 sprint? | Notes |
|---|---|---|---|
| REQ-CEK-001 | `EvalState { expr, env, continuation }` | **YES** | in-memory |
| REQ-CEK-002 | no recursive host-stack evaluator | **YES** | loop/`step` API |
| REQ-CEK-003 | continuation serializable/recoverable | **DEFER** | depends **U-02** byte encoding of frames — DISCLOSED; in-memory OK |
| REQ-CEK-004 | `Value ∧ K=ε ⇒ Halt` | **YES** | |
| REQ-CEK-005 | `Value ∧ K≠ε ⇒ Resume` | **YES** | |
| REQ-CEK-006 | no bare `Value ⇒ Halt` without K check | **YES** | negative/mutation later |
| REQ-CEK-007 | frozen frame set (nine frames) | **PARTIAL** | declare set; **implement** LetValue/Seq/If only |
| REQ-CEK-008…021 | Lambda/Call/Request paths | **NO** | M3+ |
| REQ-CEK-022 | E-Call budget premises | **NO** | M3 |
| REQ-CEK-023 | single pop path | **YES** (pure resumes) | |
| REQ-CEK-024 | only `RequestEffect` side-effect vocabulary | **YES** | pure M2: **zero** side-effect steps |
| REQ-CALC-020 | E-Let/E-Seq/E-If δ_t=0 + cost_C | **YES** with limitation | exact `cost_C(rule)` table may be minimal/zero until budget module lands — DISCLOSED |
| REQ-CALC-001… | domain types | **YES** as needed | machine Value **≠** M1 data Value |

---

## Module ownership

| Module | Crate home | M2 ownership |
|---|---|---|
| MOD-05 EVALUATOR | `ror-runtime` | **primary implementer** of `step` / EvalState |
| MOD-01 CORE | `ror-core` | Expr (pure ctors), machine Value, Symbol, Environment, Fault (minimal), frame types as data |
| MOD-03 CAPABILITY | `ror-kernel` | **not called** by pure M2 steps |
| MOD-04 BUDGET | co-located / runtime | δ_t=0 only; full algebra optional DISCLOSED |
| MOD-10 SERIALIZATION | `ror-core` | **unchanged** M1; CEK must not redefine |
| MOD-14 REFERENCE | `ror-reference` | independent pure-subset mirror when differential starts |
| MOD-15 DIFFERENTIAL | `ror-differential` | black-box SUT observation; not required on day-1 unit tests |
| MOD-02 COMPILER | `ror-compiler` | not required to feed M2 unit tests (construct `Expr` in Rust tests) |

---

## Dependency resolution

Convention (FACT — `dep/10-graph.json`): `A → B` means **B depends on A** (provider → consumer).

### Proposed M2 edges

| Proposed Cargo edge (consumer depends on provider) | Canonical edge | Classification | Decision |
|---|---|---|---|
| `ror-runtime` depends on `ror-core` | `ror-core → ror-runtime` TYPE | **REQUIRED** | proceed |
| `ror-runtime` depends on `ror-kernel` | `ror-kernel → ror-runtime` SECURITY | **REQUIRED** for full machine; **not required to call** in pure M2 | edge may remain as today; **no authorize/derive in pure steps** |
| `ror-runtime` depends on `ror-persistence` | `ror-persistence → ror-runtime` PERSISTENCE | **REQUIRED** for issuance hinge; **not required** for pure M2 | edge may remain; **no journal calls in pure steps** |
| `ror-runtime` depends on `ror-reference` | forbidden (R-REF / §14) | **FORBIDDEN** | **BLOCK if introduced** |
| `ror-core` depends on `ror-runtime` | forbidden direction | **FORBIDDEN** | **BLOCK** |
| `ror-core` depends on `ror-reference` | forbidden | **FORBIDDEN** | **BLOCK** |
| `ror-reference` depends on production runtime/kernel/… | forbidden | **FORBIDDEN** | **BLOCK** |
| `ror-differential` depends on `ror-runtime` (path) | VERIFICATION SUT | **ALLOWED** (verification) | tests only |

**Current workspace edges (FACT — `cargo metadata`):** match M0-B graph; `ror-reference` has **no** production deps; production does not depend on reference.

**No canonical dependency authority conflict with this prompt.**

### Budget / kernel without calls

Skeleton already lists kernel + persistence on `ror-runtime`. Pure M2 **AUTHORIZATION:** do not use those crates’ APIs in pure evaluation paths; introducing *new* forbidden edges remains blocked.

---

## OAD boundary

| OAD | Register | M2 classification | Rule for implementers |
|---|---|---|---|
| **U-02** | OPEN | **OUT OF M2 SCOPE** for byte codecs of frames/GlobalState; **CONDITIONALLY OPEN** if sprint claims snapshot round-trip | In-memory frames only; no Frame 15A encoding |
| **U-04** | OPEN | **OUT OF M2 SCOPE** | No `await` |
| **U-09** | OPEN | **CONDITIONALLY OPEN** — machine vs data `Value` | **Must not** expand M1 `ror_core::Value` into R-CALC-01. Introduce distinctly named machine value type (e.g. `machine::Value` / `cek::MValue`) or module path. Silent unify = **BLOCKED — OPEN OAD** |
| **U-21** | OPEN | **OUT OF M2 SCOPE** | No Effect codec |
| **U-24/U-25/U-29** | OPEN (register) / grammar frozen by R-CANON-13 | **OUT OF M2 SCOPE** | Do not touch M1 codec ABI |
| **U-26** | OPEN | **CONDITIONALLY OPEN** | Step-outcome type name/shape provisional; local enum OK; do not publish as frozen `StepResult` ABI |
| **U-27** | OPEN | **OUT OF M2 SCOPE** | No actor status |
| **U-30** | OPEN | **OUT OF M2 SCOPE** | No MarshalledValue |
| **U-35** | OPEN | **OUT OF M2 SCOPE** for theorem claims | Do not claim determinism theorem VERIFIED; local step determinism still required operationally |
| **U-37** | OPEN | **ISOLATED** | Prefer fixed widths from R-CALC/R-CANON; no new usize wire |

**Semantic behavior frozen vs representation open (DERIVED):**

| Topic | Semantic frozen? | Representation open? | M2 may implement? |
|---|---|---|---|
| Pure Let/Seq/If/Var/Value transitions | yes (R-CEK, REQ-CALC-020, CEK tables) | env/frame Rust layout | **YES** (in-memory) |
| Machine Value variant set | yes (R-CALC-01 list) | shared name with 15A Value (U-09) | **YES** only as **separate type** |
| Frame byte encoding | required eventually (REQ-CEK-003) | U-02 | **NO** bytes; yes RAM |
| Lambda/Call | yes for M3 | — | **NO** in M2 |
| StepResult name | behavior of Halt/Resume/Fault | U-26 | provisional local type only |

---

## Security boundary

| M2 target | Authority | Caps | Actors | Effects | Budgets | Time | Persist | Host | Agent | Sched | Serial | Trust |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Pure CEK step | no | no* | no | no | δ_t=0 only | logical t optional hold | no | no | no | no | consume values only | TCB member (CEK) |

\* `Value::Capability` bits may appear as **data** in machine values per R-CALC-01 but pure M2 must **not** interpret them as authority (R-TRUST-03 / R-KERN: evaluator sees refs only; no arena inspection). Prefer pure-subset tests that never construct Capability.

### Invariants governing M2

| Invariant | Binding |
|---|---|
| `Untrusted Input ↛ Authority ↛ External Effect` | R-CORE-01/02/03 — pure M2 emits **no** external effect |
| `Block ↛ step()` | R-ARCH-03 — public step API accepts only machine Expr / plan types, never raw Block |
| `CapRef ↛ AuthorityNode` | R-TRUST-03 / R-KERN-03 — no kernel introspection from evaluator |
| `Value::Capability ↛ ordinary data transfer` as authority | R-MARSHAL / R-CANON-12 — M1 data path; machine values still must not mint authority |
| `unissued effect ↛ host` | R-DUR / R-HOST — pure M2 has no issue path (REQ-CEK-024) |

**No convenience API** may accept host callbacks inside Expr (R-CALC-02).

---

## Semantic leakage audit

### Proposed M2 surface (not yet implemented) — constraints

| Crate | Forbidden in pure M2 | Allowed |
|---|---|---|
| `ror-runtime` | `std::fs` / `std::net` / `std::process`; host executor calls; LLM APIs; WAL append; kernel authorize/derive; scheduler fair-queue policies beyond single-threaded step | explicit CEK `step`; env; frames; faults as data |
| `ror-core` | host/FS/net; capability arena; scheduler; persistence; LLM | types + M1 codec only |
| `ror-reference` | depending on production crates | independent re-implementation of pure rules |

### Existing tree (FACT)

- No CEK modules yet; `ror-runtime` is doc-only skeleton.
- M1 `ror-core` has no FS/net/process.
- `#![forbid(unsafe_code)]` on crate roots (M0-B / M1).

### Feature flags

No crate features defined today (FACT). **AUTHORIZATION:** future flags must not change pure CEK transition relation (BLOCKED — SEMANTIC FEATURE VARIANCE if they do).

---

## Reference-model impact

```text
REFERENCE IMPACT = REQUIRED FOR M2 MILESTONE CLOSE
REFERENCE IMPACT FOR DAY-1 UNIT SPRINT = OPTIONAL
```

| Phase | Production | Reference | Differential |
|---|---|---|---|
| M2 implementation sprint (unit) | pure CEK in `ror-runtime` | may lag | not required to land code |
| M2 milestone acceptance (R-ORDER-02 + final/04) | pure CEK | **independent** pure subset in `ror-reference` | `Observe(P)==Observe(R)` for Value/Var/Let/Seq/If |

**Rules (DERIVED — R-REF-02, R-ORDER-03 spirit):**

- Do **not** copy production source into reference.
- Do **not** make `ror-runtime` depend on `ror-reference`.
- Differential uses both as black boxes (`ror-differential`).

R-ORDER-03 full 7-form (incl. Lambda/Call) is **pre-effects gate**, not solely M2 close — DISCLOSED.

---

## Determinism audit

| Risk source | Pure M2 exposure | Canonical rule |
|---|---|---|
| HashMap iteration | **forbid** in env/maps for semantics | use ordered structures (`BTreeMap`) or vec assoc lists with defined lookup |
| FS / env / locale / RNG / threads / wall clock | **forbid** in step | R-CORE-08 / CEK purity; R-BUDGET-16 δ_t=0 for pure |
| float | **forbid** | audit CLEAN category |
| Encoding order | N/A if no encode in step | M1 map order already fixed |

Operational determinism of `step` (same state → same successor) is **required** for tests. Claiming GI-DET / R-CORE-08 **VERIFIED** remains **BLOCKED** by U-35 (DISCLOSED).

---

## Test/evidence plan

| Class | M2 pure-subset examples | Evidence kind (R-REG) | Milestone necessity |
|---|---|---|---|
| unit | Var bind/lookup; Let body; Seq; If true/false; Halt on empty K; Resume on non-empty K | `test` | day-1 |
| negative | unbound var fault; If non-bool; Value halt without K check killed | `test` | day-1 |
| structural | \|K\| ±1 on Let entry/resume; no recursive stack growth deep Let nest | `test` | day-1 |
| determinism | repeated step same bytes/state | `test` | day-1 |
| differential | P vs R on Value/Var/Let/Seq/If | `differential` | **M2 close** |
| mutation | value-case Halt without K (REQ-CEK-006); (Call mutants M001–M003 are **M3**) | `mutation` | later / M3 for call |
| golden-vector | N/A new; may use M1 values inside `Expr::Value` | — | optional |
| crash/recovery | frame encode | — | **not M2** (U-02) |
| security | step rejects Block; no host | boundary | day-1 API review |

Do **not** label unit PASS as R-REG TESTED/VERIFIED without ledger (M1 lesson).

---

## Existing repository gates

Executed this preflight (FACT):

| Gate | Exit | Note |
|---|---|---|
| `cargo fmt --check` | 0 | PASS |
| `cargo check --workspace` | 0 | PASS |
| `cargo test --workspace` | 0 | PASS (21 `ror-core` tests; others empty) |
| `cargo clippy --workspace --all-targets -- -D warnings` | 0 | PASS |
| `cargo clippy --workspace --all-targets --all-features -- -D warnings` | 0 | PASS |
| `cargo metadata` dependency edges | — | reference independence held |
| `unsafe` in `crates/**/*.rs` | none found | PASS |
| `python3 check.py` | **partial FAIL** | see drift |

### check.py drift (DISCLOSED GAP — pre-existing, not introduced by M2)

| Checker | Result | Interpretation |
|---|---|---|
| `scripts/spec/_gate.py` | FAIL | S7 still asserts “no `Cargo.toml` / no implementation” — predates M0-B workspace; **pipeline gate stale vs bootstrap** |
| `tests/spec/_pipeline_mutations.py` | FAIL | same red baseline |
| `reg/_compile.py`, `final/_build.py`, `state/_project.py`, reference independence, etc. | PASS | |

**AUTHORIZATION:** do **not** “fix” by deleting the workspace. Record as **CANONICAL TOOLING DRIFT**. Repair is a separate governed operation (update S7 accept bootstrap crates, or scope gate to `scripts/`). Not an M2 semantic blocker.

### state/ projection drift (DISCLOSED GAP)

`state/repository-state.json` still reports:

- `implementation_state: BOOTSTRAP`
- `milestone_state.M0: NOT STARTED`
- `evidence_ceiling: SPECIFIED` (aligned)
- `claims: all 0`

**CANONICAL STATE DRIFT** relative to M0 GREEN + M1 code.  
**AUTHORIZATION:** do not hand-edit JSON to advertise M2. Regeneration/`state/_project.py` inputs must be updated under existing projection rules in a dedicated state-repair operation.

---

## Unresolved blockers

### Hard blockers to *any* M2 code

**None identified** for an in-memory pure-subset sprint that obeys the tables above.

### Blockers if scope is over-claimed

| Claim | Blocker |
|---|---|
| Unify M1 `Value` with R-CALC-01 machine Value under one public type | **BLOCKED — OPEN OAD U-09** |
| Implement Lambda/Call as “M2” | **BLOCKED — milestone boundary M3** |
| Frame/GlobalState canonical bytes in M2 | **BLOCKED — OPEN OAD U-02** |
| `ror-runtime` → `ror-reference` | **BLOCKED — FORBIDDEN edge** |
| Promote R-CEK-* to IMPLEMENTED in reg/ | **BLOCKED — no authorized registry op** |
| Feature flag flips CEK rules | **BLOCKED — SEMANTIC FEATURE VARIANCE** |
| Treat check.py S7 FAIL as M2 failure | incorrect; tooling drift |

### Disclosed limitations (non-blocking for pure subset)

1. U-09 separate machine value type required.  
2. REQ-CEK-003 serialization deferred.  
3. Full budget algebra / exact cost_C table may be stubbed with δ_t=0 and documented zero/minimal fuel until MOD-04 sprint.  
4. Differential reference lag allowed until milestone close.  
5. U-26 provisional step outcome names.  
6. state/ and scripts/spec S7 drift.  
7. R-REG remains 184× SPECIFIED.  
8. “Lexical capture” on M2 banner ≠ M3 closure capture.

---

## Authorization decision

```text
M2 PREFLIGHT = GREEN WITH DISCLOSED LIMITATIONS
```

**Meaning (AUTHORIZATION):**

- Canonical M2 scope is sufficiently determined: **pure CEK subset Value/Var/Let/Seq/If** in `ror-runtime` + domain types in `ror-core`, independent reference later.
- Implementation may proceed **without** resolving open OADs **if and only if** it respects the OAD boundary table (especially U-09 type separation and U-02 no frame bytes).
- M2 **implementation is NOT STARTED** by this commit.
- Next operation must be a separately authorized **M2 IMPLEMENTATION SPRINT** whose task list is a subset of this preflight’s authorized surface.

**Not authorized in that sprint without a new preflight addendum:**

- Lambda/Call (M3)
- Effects/host/persistence/scheduler/actors
- Registry status promotion
- M1 codec changes
- Production ↔ reference coupling
- OAD resolutions

---

## Evidence ceiling

```text
R-REG: 184 × SPECIFIED          (FACT — reg/06, final/08, state claims)
EVIDENCE CEILING: SPECIFIED     (FACT)
status-transitions.json: empty  (FACT)
```

M2 code and tests, when added, are **repository artifacts** only until an authorized ledger transition exists (same discipline as M1-REVIEW).

---

## Next permitted operation

```text
M2 IMPLEMENTATION SPRINT (separately authorized)
  scope ⊆ this preflight authorized surface
  deliverables example:
    - ror-core: machine Value + Expr pure ctors + Environment + Fault⊇unbound
    - ror-runtime: EvalState, Continuation{LetValue,Seq,If}, step loop
    - unit/structural/negative tests
    - forbid(unsafe); no new forbidden deps
  non-deliverables: Lambda/Call, registry edits, OAD closes, M1 rewrites
```

After unit-green: optional parallel `ror-reference` pure subset + differential observations (still no production dependency).

---

## Final state board

```text
M0                         GREEN
M1 frozen subset           ACCEPTED WITH DISCLOSED EVIDENCE LIMITATIONS
M1 full milestone          NOT COMPLETE
M2 preflight               GREEN WITH DISCLOSED LIMITATIONS
M2 implementation          AUTHORIZED
M2 implementation          NOT STARTED
R-REG                      184 × SPECIFIED
```

---

## Implementation boundary table (summary)

| M2 target | Canonical authority | Requirement IDs | Obligation IDs | Owning crate | Dependencies | OADs | Evidence required | Authorization |
|---|---|---|---|---|---|---|---|---|
| EvalState + explicit step | R-CEK-01 | R-CEK-01 | REQ-CEK-001,002 | ror-runtime | ror-core REQUIRED | — | unit; deep-nest stress later | **YES** |
| Value-return Halt/Resume | R-CEK-02 | R-CEK-02 | REQ-CEK-004,005,006 | ror-runtime | ror-core | U-26 provisional outcome type | structural unit | **YES** |
| Frames LetValue/Seq/If | R-CEK-03 subset | R-CEK-03 | REQ-CEK-007 partial | ror-core types + runtime | ror-core | U-02 no bytes | structural ±1 K | **YES** |
| Expr Value/Var/Let/Seq/If | R-CALC-02 | R-CALC-02 | — | ror-core | std | — | unit | **YES** |
| Machine Value (pure needs) | R-CALC-01 | R-CALC-01 | — | ror-core | std | **U-09 separate type** | unit | **YES with U-09 isolation** |
| Environment + Symbol | R-CALC-03 | R-CALC-03 | — | ror-core | std | — | unit | **YES** |
| E-Let/E-Seq/E-If rules | REQ-CALC-020; R-BUDGET-16 δ_t=0 | R-CEK-*; R-BUDGET-16 | REQ-CALC-020 | ror-runtime | ror-core | cost_C table DISCLOSED | unit; diff at close | **YES** |
| Continuation ±1 pure | R-CEK-06 | R-CEK-06 | REQ-CEK-023 | ror-runtime | — | — | structural | **YES** |
| Lambda/Call | R-CEK-04/05 | R-CEK-04/05 | REQ-CEK-008+ | — | — | — | — | **NO (M3)** |
| Frame canonical encode | REQ-CEK-003 | R-CEK-01 | REQ-CEK-003 | — | — | **U-02** | — | **NO** |
| Reference pure subset | R-REF-*; final/04 M2 | R-REF-01/02 | — | ror-reference | **none production** | — | differential | **YES independent** |
| Differential harness | final/04 M2; MOD-15 | R-TEST-* | — | ror-differential | verification edges only | — | differential | **YES at close** |
| Kernel authorize in step | R-KERN-* | — | — | — | — | — | — | **NO pure M2** |
| R-REG promotion | reg/03 | — | — | — | — | — | ledger | **NO** |
