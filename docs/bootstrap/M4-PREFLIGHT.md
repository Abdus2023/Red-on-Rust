# M4 Preflight

**Operation type:** M4 PREFLIGHT / implementation authorization only.  
**M4 implementation in this operation:** **NOT STARTED** (FACT).  
**Do not implement CapabilityKernel / Attenuate / CapRef opacity changes in this commit.**

Evidence labels: **FACT** | **DERIVED** | **DISCLOSED LIMITATION** | **BLOCKER** | **AUTHORIZATION**

---

## 1. Reviewed repository state

| Item | Value | Class |
|---|---|---|
| Branch | `arena/01a06993-red-on-rust` | FACT |
| HEAD | `ddc4138fb97119105229b05200b8438ebe36bc6d` | FACT |
| Subject | `review: reconcile M3 implementation evidence` | FACT |
| M3 implementation commit | `087c28903c818f36330cfe0a3db98f131419163c` | FACT |
| M3 control-addendum (arity SoT) | `c224bb852937cc172ab84d389e0393040a2735f2` | FACT |
| M3 review commit | `ddc4138` (= HEAD) | FACT |
| Remote `refs/heads/arena/01a06993-red-on-rust` | `ddc4138` (matches HEAD) | FACT |
| Working tree | clean (preflight report is the sole pending artifact) | FACT |
| `docs/bootstrap/M3-REVIEW.md` | present; classification ACCEPTED WITH DISCLOSED EVIDENCE LIMITATIONS | FACT |
| Ancestry | `759fb26` → `087c289` → `c224bb8` → `ddc4138` | FACT |

No silent reset/rebase/merge. No repository-state discrepancy that invalidates M3 evidence. This preflight does **not** re-open M3 semantic verification.

---

## 2. M3 baseline

From `docs/bootstrap/M3-REVIEW.md` (not reinterpreted):

```text
M3 IMPLEMENTATION          = ACCEPTED WITH DISCLOSED EVIDENCE LIMITATIONS
M3 semantic verification   = NOT CLAIMED
R-REG                      = 184 × SPECIFIED
U-02                       = OPEN
U-09                       = OPEN
```

| Prerequisite | Status | Class |
|---|---|---|
| M3 preflight GREEN WITH DISCLOSED LIMITATIONS | yes @ `759fb26` | FACT |
| M3 Lambda/Call + arity/LTR/closure | implemented @ `087c289` | FACT |
| M3 review accepted-with-limitations | `ddc4138` | FACT |
| Production + reference + differential M2/M3 | present | FACT |
| Attenuate still unsupported | both CEKs fault `UnsupportedInM2 { "Attenuate" }` | FACT |
| `ror-kernel` | stub crate (`lib.rs` skeleton only); depends on `ror-core` | FACT |
| M3 disclosed limitations preserved | yes (listed §20) | AUTHORIZATION |

**Frozen M3 surface carried into M4 (FACT — do not regress):**

```text
M2 ∪ { Lambda { params, body }, Call { func, args } }
  with CEK-CALL-ARITY-PRECHECK, CEK-CALL-ARGS-LTR, CEK-CLOSURE-LEXICAL-CAPTURE
```

---

## 3. Canonical M4 scope

### Milestone acceptance (canonical)

| Source | Text | Class |
|---|---|---|
| `final/01` **R-ORDER-02** | **M4 Capability / Attenuation** — `CapRef opacity, derive, partial order, revocation cascade pass` | FACT |
| `final/04` milestone row | **M4** — `CAP-DERIVE-NO-AMPLIFICATION` + revocation/expiration/lexical binding + **independent reference algebra** | FACT |
| `mod/03-capability.md` | M4 gate = same tags + MOD-14 independent algebra; mutations M004/M005/M006/M030 | FACT |

**Canonical M4 name (FACT):** Capability / Attenuation — **not** Effects/Request, **not** Actors, **not** Persistence.

### Primary requirements (authority spine)

| ID | Statement (short) | Owner | Class |
|---|---|---|---|
| **R-CAP-01** | Authority `A = {(o, ⟨S,Q,R,T⟩)}`; CapRef opaque; `κ(c) → Authority` | `ror-kernel` | FACT |
| **R-CAP-02** | Operation-indexed authority (no cross-op contamination) | kernel | FACT |
| **R-CAP-03** | Partial order `A₁ ≼ A₂` (O ⊆ + per-op S/Q/R/T) | kernel | FACT |
| **R-CAP-04** | `Constraint` ≠ `Authority` (narrowing request) | kernel | FACT |
| **R-CAP-05** | `derive(A,C)` = per-op meet; **invariant** `derive(A,C) ≼ A` | kernel | FACT |
| **R-CAP-06** | `Authorized(A,E,t)` five conjuncts | kernel algebra; **effect path = M5** | FACT / boundary |
| **R-CAP-07** | `Valid(c,t) ⇔ Live(c) ∧ t ∈ Lifetime(c) ∧ ∀a∈Ancestors(c). Live(a)`; lazy revoke | kernel | FACT |
| **R-CAP-08** | Theorems 1–3 SPECIFIED (not PROVEN) | tests | FACT |
| **R-CAP-09** | Logical time `t` explicit machine state; no wall-clock | core/runtime | FACT |
| **R-CAP-10** | `AdmissibleConstraint` DEFINED; inadmissible ⇒ `Fault::InvalidConstraint`, never ⊤/identity; M030 | kernel (+ compiler later) | FACT |
| **R-CAP-11** | `Lifetime` = logical half-open `[start,end)`; U-36 RESOLVED | core/kernel | FACT |
| **R-KERN-01** | `CapRef {index, generation}` opaque; **fields private**; **kernel-only construction** | core + kernel | FACT |
| **R-KERN-02** | `CapabilityKernel` owns `arena`, `revocation_set`; `derive`/`revoke` kernel ops | kernel | FACT |
| **R-KERN-03** | `AuthorityNode` + internals `pub(crate)` / inaccessible to evaluator | kernel | FACT |
| **R-KERN-04** | Possession-gated authorize (holder + context) | kernel; **full actor wiring later** | FACT / thin-dep |
| **R-KERN-05** | Real `CapabilityContext` type (unit sketch superseded) | kernel; snapshot = M7 | FACT / thin-dep |
| **R-KERN-06** | Root-grant protocol + durable `CapabilityGranted` | kernel; **durable path = M7** | FACT / thin-dep |
| **R-CORE-04** | No amplification (central restatement of R-CAP-05) | kernel | FACT |
| **R-CALC-02** | `Expr::Attenuate { cap, constraint }` | core (AST present) | FACT |
| **R-CEK-03** | Frame set includes `Attenuate { name, body, env }` | runtime | FACT (shape tension §20) |
| **R-BUDGET-16** | pure CEK attenuate / attenuate-denied `δ_t = 0` | runtime | FACT |
| **R-REF-02 / REQ-REF-023/024** | Independent reference algebra + `RefCapabilityStore` | `ror-reference` | FACT |
| **R-SCOPE-04** | Production ⇏ reference shared transition/algebra code | process | FACT |

### Atomic REQ mapping (M4 sprint targets)

| Obligation | Statement (short) | M4 sprint? |
|---|---|---|
| REQ-CAP-001…006 | Domains O/S/Q/R/T + representation MAY | **YES** (provisional reps under U-21) |
| REQ-CAP-007 | `≼` partial order | **YES** |
| REQ-CAP-008 | Operation-indexed authority | **YES** |
| REQ-CAP-009 | Constraint ≠ Authority | **YES** |
| REQ-CAP-010/011 | `Authorized` 5-conjunct + dual-gate cost note | **ALGEBRA YES** / **effect path NO (M5)** |
| REQ-CAP-012 | `derive` per-op meet | **YES** |
| REQ-CAP-013…015 | `Valid` + parent revoke + lazy ancestor walk | **YES** |
| REQ-CAP-016…018 | Theorems 1–3 as property tests (not PROVEN) | **YES** |
| REQ-CAP-019…021 | Explicit logical `t`; no wall-clock | **YES** (test/harness clock) |
| REQ-CAP-022 | `E-Attenuate`: `Valid` ∧ `AdmissibleConstraint` → `derive`; bind `c'` | **YES** (κ/budget thin — §8) |
| REQ-CAP-023 | `E-AttenuateDenied` → fault (name tension §20) | **YES** |
| REQ-CAP-024 | AdmissibleConstraint AMBIGUOUS in `req/` | **SUPERSEDED by R-CAP-10** for impl (§20) |
| REQ-CAP-025 | Atomic derive from evaluator POV (one kernel call) | **YES** |
| REQ-CAP-026 | Constraint monotonicity of derive | **YES** |
| REQ-KERN-001…003 | CapRef opaque / private / kernel-only | **YES** |
| REQ-KERN-004…005 | Kernel API: authorize/derive/valid signatures | **YES** (authorize algebra; effect gate M5) |
| REQ-KERN-006/009 | No authority inspection by evaluator | **YES** |
| REQ-KERN-007/008 | `valid(cap,t)`; every decision takes `t` | **YES** |
| REQ-REF-023/024 | Independent `RefAuthority` algebra + store | **YES** |
| R-KERN-04 possession conjunct | holder ∈ context | **PARTIAL** — API shape YES; live actors NO |
| R-KERN-05 context durability | snapshots carry context | **NO** (M7) — type MAY exist |
| R-KERN-06 durable root grant | WAL `CapabilityGranted` | **NO** (M7) — test mint MAY |
| R-CAP-10 compiler half | compile-time constraint validation | **NO** (compiler milestone) |
| R-CANON-12 / codec CapRef | data decoder rejects caps | already M1 direction; opacity fix must not break | **CARE** |

Verification tags (`final/04`): `CAP-DERIVE-NO-AMPLIFICATION`, `CAP-REVOCATION-ANCESTOR`; mutations **M004** (accept revoked), **M006** (amplify), **M030** (inadmissible as ⊤). **M005** (omit ceiling) is R-CAP-06 effect-ceiling — primarily **M5** kill target; algebra-level ceiling conjunct MAY be unit-tested early (**DERIVED**).

### Out of M4 scope (DERIVED)

| Concern | Milestone |
|---|---|
| `Expr::Request` / 16-step effect pipeline / host | **M5** |
| Spawn / send / receive / scheduler / delegation envelopes | **M6** |
| WAL / snapshot of arena / `CapabilityGranted` durability | **M7** |
| Full compiler pipeline + embedded-cap literal battery | compiler track |
| Frame/GlobalState **byte** codecs | **U-02** — not M4 acceptance |
| R-REG promotion / OAD close-by-fiat | never in impl sprint alone |
| Mechanized PROVEN of Theorems 1–3 | not claimed (R-CAP-08) |

**Authorized M4 expression + kernel surface (DERIVED):**

```text
M3 surface
  ∪ kernel: CapabilityKernel { derive, revoke, valid, (algebra) authorize, leq }
  ∪ CEK: Expr::Attenuate { cap, constraint }  →  E-Attenuate | E-AttenuateDenied
  ∪ CapRef opacity (R-KERN-01)
  ∪ independent reference algebra (REQ-REF-023/024)
  ∪ differential M4 cases
```

---

## 4. Requirement / obligation mapping (acceptance checklist)

| R-ORDER-02 acceptance element | Normative homes | M4 evidence target |
|---|---|---|
| **CapRef opacity** | R-KERN-01/03, REQ-KERN-001…003/006/009, R-TRUST-03 | private fields; no public int ctor; evaluator holds only `Value::Capability(CapRef)`; no authority fields on CapRef |
| **derive** | R-CAP-05/10/12, REQ-CAP-012/025, REQ-KERN-005 | `derive(A,C) ≼ A`; inadmissible faults; atomic evaluator-visible call |
| **partial order** | R-CAP-03, REQ-CAP-007 | decidable `leq`; property tests |
| **revocation cascade** | R-CAP-07, REQ-CAP-013…015 | parent `Live=false`; descendant `Valid` fails via ancestor walk |
| **+ expiration** (`final/04`) | R-CAP-11, REQ-CAP-005/013 | `t ∉ [start,end)` ⇒ ¬Valid |
| **+ lexical binding** (`final/04`) | R-CEK-03 Attenuate frame; source Let-symmetry sketches; M3 closure discipline | derived `CapRef` as ordinary value composable with Let/Lambda (**reading §8/§20**) |
| **+ independent reference algebra** | REQ-REF-023/024, R-SCOPE-04 | `ror-reference` algebra/store; zero production kernel import |

---

## 5. M3 boundary verification

Mechanical posture @ `ddc4138` (FACT):

| Probe | Result | Class |
|---|---|---|
| `Expr::Attenuate` in production CEK | `Fault::UnsupportedInM2 { form: "Attenuate" }` | FACT |
| `Expr::Attenuate` in reference CEK | same unsupported fault | FACT |
| `PureFrame` variants | Let/Seq/If/CallFunction/CallArgument only — **no Attenuate frame yet** | FACT |
| `ror-kernel/src/lib.rs` | skeleton; no arena/derive | FACT |
| `CapRef` fields | `pub index` / `pub generation` — **violates R-KERN-01** as written | FACT (M4 debt) |
| CapRef free construction | tests/codecs construct `CapRef { .. }` freely | FACT (M4 debt) |
| M3 Lambda/Call paths | present; must remain green | FACT |
| Machine `Fault` | UnboundVariable / TypeError / ArityMismatch / UnsupportedInM2 — no cap faults yet | FACT |
| Effects / actors | still unsupported | FACT |

**Boundary hold (AUTHORIZATION):** M4 MUST NOT regress M2/M3 pure CEK, differential tags, or M1 codec golden behavior except where CapRef opacity **requires** controlled API migration (kernel-mediated construction + test helpers). Any CapRef visibility change MUST keep R-CANON-05 payload layout and R-CANON-12 data-path rejection intact.

---

## 6. M4 semantic readiness

| Area | Ready? | Notes | Class |
|---|---|---|---|
| Algebra domains + meet/order | YES with provisional reps | U-21 OPEN — abstract/test enums permitted (REQ-CAP-006 MAY) | DISCLOSED LIMITATION |
| Authority vs Constraint types | YES provisional | U-31 OPEN — field sets follow R-CAP-01/04/05 semantics | DISCLOSED LIMITATION |
| `derive` + no-amplification | YES | R-CAP-05 / R-CORE-04 frozen | FACT |
| `AdmissibleConstraint` | YES per **R-CAP-10** | `req/` REQ-CAP-024 still AMBIGUOUS — registry lag, not missing law | DISCLOSED LIMITATION |
| `Valid` + revoke cascade | YES | R-CAP-07 frozen | FACT |
| Lifetime logical | YES | R-CAP-11 / U-36 RESOLVED | FACT |
| CapRef opacity | YES (must change types.rs) | breaks current `pub` fields by design | FACT |
| Kernel crate | YES empty home | MOD-03 → `ror-kernel` → `ror-core` only | FACT |
| E-Attenuate CEK | YES with shape reading | Expr frozen `{cap,constraint}`; frame name/body tension §20 | DISCLOSED LIMITATION |
| Reference algebra | YES empty | must not import `ror-kernel` | FACT |
| Full Request authorize path | NO | M5 | FACT |
| Actor possession / durable grant | NO full | thin test stubs only | DISCLOSED LIMITATION |
| Compiler admissibility gate | NO | R-CAP-10 compiler half deferred | FACT |

---

## 7. Capability algebra preflight

| Rule | Authority | M4 obligation |
|---|---|---|
| Five domains O,S,Q,R,T | R-CAP-01, REQ-CAP-001…005 | Implement semantic ops: order, meet, interpret |
| Op-indexed grants | R-CAP-02, REQ-CAP-008 | No cross-op bleed |
| `A₁ ≼ A₂` | R-CAP-03, REQ-CAP-007 | Total on represented authorities |
| Constraint is narrowing request | R-CAP-04, REQ-CAP-009 | Kernel APIs take `Constraint`, not raw Authority injection from evaluator |
| `derive = meet on O_A ∩ O_C` | R-CAP-05, REQ-CAP-012 | Construction-side ≼ |
| Inadmissible ⇒ fault, never identity | R-CAP-10, M030 | Kill ⊤-default |
| Theorems 1–3 | R-CAP-08, REQ-CAP-016…018 | Property tests; **PROVEN not claimed** |
| Constraint monotonicity | REQ-CAP-026 | Property tests |
| No wall-clock in algebra | R-CAP-09/11 | `LogicalTime` only |

**Representation choice (AUTHORIZATION under U-21/U-31):** M4 MAY introduce **test-domain** enums/structs (`Op`, scope predicates, resource ceilings, lifetime intervals) sufficient to exercise meet/order/Valid/derive. M4 MUST NOT claim U-21 or U-31 closed. M4 MUST NOT encode host/OS authority.

---

## 8. Attenuation / CEK preflight

### Expr (frozen)

```text
Expr::Attenuate { cap: Box<Expr>, constraint: Box<Expr> }   # R-CALC-02 / current ror-core
```

### Transition obligations

| Rule | ID | M4 |
|---|---|---|
| Premises `Valid(c,t) ∧ AdmissibleConstraint(C)` → `c' = derive(c,C)` | REQ-CAP-022, R-CAP-10 | **YES** |
| Security by `derive ≼`, not by `Authorized` on attenuate | REQ-CAP-022 | **YES** |
| Denied → fault; no CapRef minted | REQ-CAP-023 | **YES** |
| Evaluator observes **one** kernel derive (no TOCTOU split) | REQ-CAP-025 | **YES** |
| `δ_t(attenuate)=0`, `δ_t(attenuate-denied)=0` | R-BUDGET-16 | **YES** (clock stub ok) |
| Add `c'` to actor `κ`; charge `cost_C(att)` | REQ-CAP-022 | **PARTIAL** — see thin deps |

### Frame / lexical-binding reading (DISCLOSED)

| Source | Shape |
|---|---|
| R-CALC-02 (Expr) | `{ cap, constraint }` — **no** `name`/`body` |
| R-CEK-03 (Frame) | `Attenuate { name, body, env }` |
| Informative sketches (`Red-on-Rust.md`) | Let-like `attenuate cap as child under C in body`; frame `{ name, constraint, body, env }` |

**Authorized implementation reading (DERIVED — not an OAD close):**

1. **MUST** evaluate per frozen **Expr** `{cap, constraint}` (R-CALC-02). Do **not** add `body`/`name` fields to `Expr` without a frozen addendum.
2. **MAY** introduce evaluator-local continuation frame(s) to evaluate `cap` then `constraint` then call kernel (Call-style multi-frame is the M3 precedent). Aligning residual frame fields with R-CEK-03's `{name, body, env}` is **blocked** unless a frozen binding form supplies `name`/`body`.
3. **Lexical binding** evidence for `final/04` is satisfied by: derived `Value::Capability(c')` returning through ordinary value-return / `Let` / closure capture (M3 surface), preserving environment restoration symmetry — **not** by inventing a non-frozen AST binder.
4. If implementation discovers R-CEK-03 frame fields are load-bearing beyond (3), **STOP** and report (R-SCOPE-03) — do not silently extend Expr.

### Thin dependencies (authorized stubs only)

| Item | M4 treatment |
|---|---|
| Actor `κ` / `CapabilityContext` | Type + test harness map MAY exist (R-KERN-05 direction); live multi-actor possession **NO** |
| `cost_C(att)` / budget debit | MAY no-op or record zero under pure M4 harness (**DISCLOSED**, same class as M3 `cost_C` lag) |
| Root grant | Test/deployment mint API returning CapRef **MAY**; durable `CapabilityGranted` WAL **NO** (M7 / R-KERN-06 durable half) |
| `authorize(holder, cap, E, t)` | Algebra + optional holder parameter **MAY**; Request CEK **NO** |

---

## 9. Kernel / CapRef opacity preflight

| Obligation | Current | M4 action |
|---|---|---|
| Fields private | `pub` on both fields | Make private; crate-local or kernel accessors |
| No public arbitrary-int ctor | free struct literal | Remove; `pub` ctor only via kernel (tests: `kernel.grant_for_test` / similar) |
| Kernel-only CapRef mint | any crate | `CapabilityKernel` sole mint path |
| `AuthorityNode` hidden | N/A | `pub(crate)` inside `ror-kernel` |
| Evaluator sees only CapRef | Value::Capability already | Keep; no Authority on Value |
| Codec payload | R-CANON-05 u32/u32 | Preserve wire layout; kernel-mediated encode path |
| Data decode rejects caps | R-CANON-12 | Preserve |
| `ror-runtime → ror-kernel` | already in Cargo.toml | Use for derive/valid only |
| `ror-reference` ↛ kernel | Cargo forbids | Keep; independent algebra |
| `ror-kernel` ↛ runtime | dep graph forbids | Keep |

**M1 interaction (DISCLOSED LIMITATION):** CapRef privacy will require updating `ror-core` canonical helpers and tests that currently struct-literal CapRefs. That is **in-scope M4 engineering**, not a scope expansion into “finish M1.” Golden vector **bytes** for cap payloads must remain stable.

---

## 10. Revocation / expiration / Valid preflight

| Case | Expected | Tag/mutation |
|---|---|---|
| Live, in-lifetime, ancestors live | `Valid = true` | REQ-CAP-013 |
| Parent revoked | descendant `Valid = false` (lazy walk) | `CAP-REVOCATION-ANCESTOR`, M004 |
| `t` outside `[start,end)` | `Valid = false` | R-CAP-11 expiration |
| Generation mismatch / dangling | not Valid / fault path | R-KERN-01 generation safety |
| Revoke is monotone | no resurrection without new grant | R-CAP-07 direction (durable half M7) |

---

## 11. U-02 assessment

| Item | Status |
|---|---|
| U-02 | **OPEN** |
| M4 frames | **in-memory only** (M3 precedent) |
| AuthorityNode snapshot bytes | **NOT M4** (R-PERSIST-07 / U-02) |
| CapRef wire payload | already specified; opacity ≠ new codec project |

**AUTHORIZATION:** M4 MUST NOT implement frame/arena byte codecs. M4 MUST NOT claim U-02 resolved.

---

## 12. U-09 / AdmissibleConstraint assessment

| Item | Status | M4 reading |
|---|---|---|
| U-09 Value domain collision | **OPEN** | Machine Value vs 15A data Value remain split (M1–M3 posture) |
| AMB-12 / REQ-CAP-024 | `req/` still AMBIGUOUS | **Normative definition is R-CAP-10** (frozen addendum SEC-014; closes AMB-12 admissibility clause per `final/01`) |
| AdmissibleConstraint law | R-CAP-10 | O nonempty ⊆ parent; S interpretable; Q closed; R ≤ parent; T satisfiable interval; else `InvalidConstraint` |
| Compiler validate half | R-CAP-10 | **DEFERRED** (no `ror-compiler` M4 gate) |
| Runtime/kernel enforce | R-CAP-10 | **MUST** — derive never returns on inadmissible |

**AUTHORIZATION:** Implement admissibility **as R-CAP-10**. Do not wait for `req/` re-grade. Do not claim AMB-12/U-09 registry rows closed. Do not implement ⊤-default.

---

## 13. U-21 / U-31 / fault OAD assessment

| OAD | Status | M4 posture |
|---|---|---|
| **U-21** Op/Target/Params domains | OPEN | Provisional test domains; no claim of frozen host ontology |
| **U-31** Authority vs Constraint fields + arena holder | OPEN | Fields mirror R-CAP-01/04/05; arena owned by `CapabilityKernel` (R-KERN-02) |
| **U-08 / U-14** fault taxonomy | OPEN (R-CORE-13 security direction noted) | Evaluator-local Fault **MAY** grow provisional variants |
| **U-36** Lifetime clock | **RESOLVED** (R-CAP-11) | Use logical time only |
| Fault name `CapabilityRevoked` | REQ-CAP-023 vs R-CALC-06 / AMB-08 | Provisional evaluator fault label OK; **not** a claim that U-08 is closed |
| Fault name `InvalidConstraint` | R-CAP-10 cites R-CORE-13 | Provisional evaluator/kernel fault OK |

**AUTHORIZATION:** Same pattern as M3 `ArityMismatch` — local, deterministic labels shared by P and R; full trust-boundary enum remains open.

---

## 14. Reference-model independence

| Rule | M4 requirement |
|---|---|
| R-SCOPE-04 / R-REF-02 | Reference MUST NOT call production kernel/runtime |
| REQ-REF-023 | Independent `RefAuthority` / `RefOperationAuthority` algebra |
| REQ-REF-024 | `RefCapabilityStore` (authorities, parents, generations, live set) |
| Differential | Compare observations (values/faults/Valid outcomes), not shared code paths |
| Mock-kernel track | Production CEK may be tested against a **mock** kernel API (exact one-call assertions) **independently** of reference algebra tests (oracle split; informative source architecture) |

`ror-reference` Cargo.toml already excludes kernel — **preserve**.

---

## 15. Differential-testing readiness

| Surface | Plan |
|---|---|
| Existing M2/M3 | Must stay green |
| New M4 | Attenuate success/deny; revoke cascade; expiration; no-amplification fixtures |
| Fault comparison | Labels + four R-REF-05 dimensions when available; at minimum stable fault identity P≡R |
| Algebra properties | Prefer shared **fixtures**, not shared **implementations** |
| Tag orientation | `CAP-DERIVE-NO-AMPLIFICATION`, `CAP-REVOCATION-ANCESTOR`; expiration + lexical composition cases |

M9 mutation kill-rate 100% is **not** an M4 day-1 acceptance gate (M9 milestone). M4 SHOULD land kill tests for M004/M006/M030 as readiness, without claiming M9.

---

## 16. Security assessment

| Invariant | M4 duty |
|---|---|
| `derive(A,C) ≼ A` (GI-SEC-04 / R-CORE-04) | **MUST** enforce + test |
| CapRef ⇏ AuthorityInspection | **MUST** (visibility + API) |
| No ⊤-default inadmissible constraint (M030) | **MUST** |
| Ancestor revocation | **MUST** |
| No wall-clock semantics | **MUST** |
| Evaluator cannot mint authority | **MUST** (kernel grant only; test mint is harness-privileged) |
| Possession gate R-KERN-04 | API direction **MUST NOT** reintroduce global authorize-without-holder as the long-term API; full actor context **MAY** lag |
| Root grant durability R-KERN-06 | **MUST NOT** claim recovery audit complete |
| Effects still impossible | Request remains unsupported — preserves M3 pure boundary |

---

## 17. Determinism assessment

| Concern | M4 rule |
|---|---|
| Logical time | Explicit parameter / machine field; never `SystemTime` |
| Arena indices | Deterministic allocation order for same grant/derive sequence |
| HashSet revocation | Iteration MUST NOT affect semantic Valid (set membership only) |
| Property tests | Seeded RNG only; record seeds in failures |
| δ_t | attenuate paths 0 (R-BUDGET-16) |
| Encoding | CapRef payload endianness unchanged |

---

## 18. Dependency / module assessment

| Edge | Status | M4 |
|---|---|---|
| `ror-kernel → ror-core` | present | implement here |
| `ror-runtime → ror-kernel` | present (unused) | wire derive/valid for Attenuate |
| `ror-reference → ror-core` only | present | add ref algebra modules |
| `ror-kernel → ror-runtime` | **FORBIDDEN** | keep |
| `ror-reference → ror-kernel` | **FORBIDDEN** | keep |
| MOD-03 ownership | algebra + kernel | FACT |
| MOD-05 evaluator | calls kernel; holds CapRef only | FACT |
| MOD-14 reference | independent algebra | FACT |

No new crates.io dependencies (network still unreliable; M0–M3 posture). No `unsafe`. No `HashMap` iteration–dependent semantics for authority decisions if avoidable; if `HashSet` used for revocation, membership-only.

---

## 19. API / visibility assessment

| API | Visibility rule |
|---|---|
| `CapRef` fields | private |
| `CapRef` construction | kernel (and carefully scoped `ror-core` codec internals if required for kernel-mediated path) |
| `Authority` / `AuthorityNode` | not public to runtime consumers |
| `Constraint` | public enough for Expr evaluation to build values **or** constraint-as-Value decoding path — must not expose Authority internals |
| `CapabilityKernel::derive/revoke/valid` | public to runtime |
| Test grant | `#[cfg(test)]` or `test-util` feature — not a production mint free-for-all |
| Reference types | `Ref*` prefix; no re-exports of kernel types |

---

## 20. Discrepancies (open, disclosed — not silent fixes)

| ID | Discrepancy | Preflight resolution |
|---|---|---|
| D-M4-01 | REQ-CAP-024 / AMB-12 still AMBIGUOUS vs **R-CAP-10** DEFINED | Implement R-CAP-10; disclose registry lag; no `req/` edit in impl sprint without separate docs commit policy |
| D-M4-02 | R-CALC-02 Attenuate `{cap,constraint}` vs R-CEK-03 frame `{name,body,env}` vs sketches with `body` on Expr | Expr wins for AST; lexical binding via value-return composition; no invented AST fields (§8) |
| D-M4-03 | REQ-CAP-023 `Fault::CapabilityRevoked` ∉ closed R-CALC-06 list / U-08 OPEN | Provisional evaluator fault; disclose |
| D-M4-04 | R-CAP-10 `Fault::InvalidConstraint` vs local Fault enum | Same provisional pattern |
| D-M4-05 | CapRef `pub` fields vs R-KERN-01 | M4 MUST fix; codec/test churn expected |
| D-M4-06 | R-CAP-06 full Authorized vs M4 acceptance (no Request) | Algebra function YES; effect pipeline NO |
| D-M4-07 | R-KERN-04/05/06 actor possession + durable grant vs pure M4 | Types/API stubs YES; actors/WAL NO |
| D-M4-08 | REQ-CAP-022 `κ` + `cost_C` | Thin no-op/harness; disclose like M3 cost lag |
| D-M4-09 | U-21/U-31 concrete field sets | Provisional; disclose |
| D-M4-10 | MOD-03 non-normative still cites AMB-12 open | Stale module prose vs R-CAP-10; R-CAP-10 governs |
| D-M4-11 | `UnsupportedInM2` name for M4 forms | Cosmetic; may rename later; not blockers |

**None of D-M4-01…11 is classified BLOCKER for starting implementation under disclosed limitations** — each has an authorized reading consistent with frozen `final/01` and M3 preflight precedent.

---

## 21. Evidence-model reconciliation

| Claim | Status |
|---|---|
| R-REG row promotions | **FORBIDDEN** in this preflight and in M4 impl alone |
| VERIFIED / PROVEN | **NOT claimed** |
| Theorems 1–3 | SPECIFIED + tests ≠ PROVEN (R-CAP-08) |
| M3 semantic verification | still **NOT CLAIMED** |
| M4 preflight | authorization artifact only |
| Mutation kill 100% | M9, not M4 entry |

```text
R-REG = 184 × SPECIFIED   (unchanged)
```

---

## 22. Toolchain and repository gates

| Gate | Expectation |
|---|---|
| Toolchain | `ror-stable` 1.88.0 posture from M0–M3 |
| `cargo fmt` / `check` / `test` / `clippy` | must remain green after M4; baseline green at M3 review |
| Network / crates.io | still treated as unavailable — **no new registry deps** |
| `Cargo.lock` / `target/` | do not commit |

This preflight does not re-run full gates as a claim of M4 readiness code (no M4 code exists). Baseline remains the M3 review green set.

---

## 23. Corrections

No correction to M3 classification. No correction to R-ORDER-02 milestone identity.  
Correction relative to stale `req/` / `mod/03` prose: **AdmissibleConstraint is defined by R-CAP-10** for implementation purposes; AMB-12 remains a **registry hygiene** debt, not an implementation STOP under R-SCOPE-03 when a frozen addendum already supplies the law.

---

## 24. Authorization decision

```text
M4 PREFLIGHT = GREEN WITH DISCLOSED LIMITATIONS — IMPLEMENTATION AUTHORIZED
```

**Meaning (AUTHORIZATION):**

- Canonical M4 scope is determined: **Capability / Attenuation** — CapRef opacity, derive, partial order, revocation cascade, plus `final/04` expiration, lexical-binding composition, and independent reference algebra (R-ORDER-02, R-CAP-01…11, R-KERN-01…03, REQ-CAP/KERN spine, REQ-REF-023/024).
- M3 baseline accepted-with-limitations @ `ddc4138`; pure Lambda/Call surface must not regress.
- Implementation may proceed in a **separate M4 IMPLEMENTATION SPRINT** only within the MAY surface below.
- M4 implementation remains **NOT STARTED** by this commit.
- Disclosed limitations (§20, §25) must be respected.
- Open OADs (U-02, U-09 residual, U-21, U-31, U-08/U-14) are **not** resolved by this preflight.

**Not authorized without new preflight/addendum:** Request/effects host path, actors/scheduler/delegation production path, arena WAL/snapshot durability, compiler admissibility suite as M4 gate, OAD closes, R-REG promotion, production↔reference algebra coupling, inventing `Expr::Attenuate` body/name fields against R-CALC-02, claiming Theorems PROVEN, claiming M3/M4 semantic verification complete.

---

## 25. Explicit MAY / MUST NOT / DEFERRED boundary

### MAY (authorized in M4 implementation sprint)

- Implement `CapabilityKernel` in `ror-kernel`: generational arena, parent links, `revocation_set`, `derive`, `revoke`, `valid`, `leq`, admissibility check per R-CAP-10.
- Provisional `Authority` / `Constraint` / domain types under U-21/U-31 semantic shapes.
- CapRef opacity migration (private fields, kernel mint, test grant hook).
- Evaluator-local faults: e.g. `InvalidConstraint`, capability-revoked/denied style labels (provisional).
- CEK `E-Attenuate` / `E-AttenuateDenied` on frozen `Expr::Attenuate { cap, constraint }` in `ror-runtime`.
- In-memory attenuate continuation frames (no codecs).
- Logical-time parameter plumbing for kernel calls (harness/machine stub).
- Independent reference algebra + store in `ror-reference`.
- Differential M4 fixtures; property tests for ≼ / derive / revoke / expire / M030.
- Mock-kernel interaction tests for single-call derive atomicity (REQ-CAP-025).
- Thin `CapabilityContext` type and test possession maps **without** multi-actor runtime.
- Algebra-level `Authorized` pure function for property tests (not Request CEK).

### MUST NOT

- Implement `Expr::Request` / host effects / 16-step issuance (M5).
- Implement spawn/send/receive/scheduler/delegation production semantics (M6).
- Persist arena / WAL capability events / recovery replay (M7).
- Import production kernel into reference (or share derive implementation).
- Resolve or “close” OADs by prose in code comments claiming frozen status.
- Promote any R-REG row to VERIFIED/PROVEN.
- Treat inadmissible constraints as identity/⊤.
- Allow evaluator construction or inspection of Authority.
- Use wall-clock for Lifetime/Valid.
- Expand Expr Attenuate with non-frozen `body`/`name` fields.
- Regress M2/M3 CEK or differential tags.
- Add crates.io dependencies.
- Commit `Cargo.lock` / `target/`.

### DEFERRED (explicit)

| Item | Until |
|---|---|
| Request CEK + R-CAP-06 effect gate wiring | M5 |
| M005 ceiling kill in full effect path | M5 |
| Actor possession live gate + mailbox caps | M6 |
| Durable root grant + snapshot context | M7 / R-PERSIST-07 |
| Compiler AdmissibleConstraint battery | compiler track |
| Frame/arena byte codecs | U-02 resolution |
| Full Fault enum closure | U-08/U-14 |
| U-21 host ontology / U-31 final field freeze | OAD resolution |
| REQ-CAP-024 / AMB-12 registry re-grade | docs/registry hygiene sprint |
| Theorems PROVEN | mechanized proof effort (out of band) |
| M9 100% mutation kill | M9 |

---

## 26. Commit decision

All preflight conjuncts hold: preflight-only artifact; no M4 code; no M3 behavior change; no OAD/R-REG/canonical mutation; report complete; decision authorized-with-limitations.

```text
COMMIT = PERMITTED
```

---

## 27. Next authorized operation

```text
NEXT = M4 IMPLEMENTATION
```

Separate sprint. Deliverables (example, not exhaustive):

- `ror-kernel`: `CapabilityKernel`, arena, derive/revoke/valid/leq, AdmissibleConstraint, test grant  
- `ror-core`: CapRef opacity; provisional Fault variants; LogicalTime/Lifetime if missing  
- `ror-runtime`: Attenuate CEK transitions + frames; kernel calls; preserve M3  
- `ror-reference`: independent algebra + store + attenuate transitions  
- `ror-differential`: M4 cases  
- unit / property / negative (revoke, expire, inadmissible, amplify-attempt) / determinism  
- **no** Request; **no** actors production path; **no** U-02 codecs; **no** R-REG edits  

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
M4 preflight               GREEN WITH DISCLOSED LIMITATIONS
M4 implementation          NOT STARTED
R-REG                      184 × SPECIFIED
```

---

## Implementation boundary summary (for the next sprint)

| M4 target | Authority | Crate | OAD constraint | Auth |
|---|---|---|---|---|
| CapabilityKernel derive/revoke/valid | R-CAP-05/07/10, R-KERN-02 | `ror-kernel` | U-31 provisional fields | **YES** |
| Partial order `leq` | R-CAP-03 | kernel + ref | U-21 domains | **YES** |
| CapRef opacity | R-KERN-01 | `ror-core` + kernel | codec churn OK | **YES** |
| AdmissibleConstraint runtime | R-CAP-10 | kernel | req/ AMB lag disclosed | **YES** |
| E-Attenuate / Denied | REQ-CAP-022/023 | runtime + ref | Expr shape frozen; frame reading §8 | **YES** |
| Revocation cascade + expiration | R-CAP-07/11 | kernel + tests | — | **YES** |
| Reference algebra + store | REQ-REF-023/024 | `ror-reference` | no kernel import | **YES** |
| Differential M4 | final/04 M4 row | `ror-differential` | — | **YES** |
| Algebra `Authorized` pure fn | R-CAP-06 | kernel (unit) | — | **YES** |
| Request / effects | M5 | — | — | **NO** |
| Live actors / delegation | M6 | — | — | **NO** |
| Arena WAL / recovery | M7 | — | U-02 | **NO** |
| Compiler admissibility suite | R-CAP-10 compiler | — | — | **NO** |
| Frame/arena bytes | U-02 | — | **U-02 OPEN** | **NO** |
| R-REG promotion / OAD close | process | — | — | **NO** |

---

*End of M4 PREFLIGHT. Implementation is authorized only under the boundary above.*
