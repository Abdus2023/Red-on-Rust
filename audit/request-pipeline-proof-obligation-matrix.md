# Request-Pipeline Proof-Obligation Matrix

**From `Expr::Request` to a host-visible effect — every path, every gate, every error path.**

> Scope: trace all paths from an `Expr::Request` (the *only* way an effect intent exists,
> R-EFFECT-01 / REQ-CEK-024) through the frozen 16-step request sequence to a
> `HostExecutor::execute` call that can produce an external effect, and enumerate the
> proof obligation at each gate plus the behavior of every error path.
>
> Canonical sequence: master prompt [54] §8, `Red-on-Rust.md` L38024–38045 (the
> "16 lines" block). REQ-EFFECT-005 declares this form canonical — "Any deviation is a
> bug. The sequence is immutable." C-01 resolves numbering conflicts to this form.
>
> Status: repository-wide, all obligations are `SPECIFIED`; there is **no implementation
> evidence** in this repository (spec/03 preamble, R-SCOPE-02: frozen ≠ verified). Every
> proof obligation below is therefore an *obligation*, not a claim. Blocking open items
> (U-02, U-06, U-07, U-08, U-14, U-15, U-21, U-36, AMB-08, X-67) are cited where they
> make an obligation currently unprovable.

---

## 0. Path enumeration: how an expression can reach the host

### 0.1 The complete path graph

```
ExecutablePlan (MOD-02; the only legal input — R-ARCH-03)
   └─ CEK evaluates Expr::Request (MOD-05)
        ├─ frame RequestCapability      → evaluate capability   (step 1, G1)
        ├─ frame RequestTarget          → evaluate target       (step 2, G2)
        ├─ frame RequestArgument (×n)   → evaluate params LTR   (step 3, G3)
        └─ finalize_request
             └─ 16-step sequence (steps 4–16, G4–G15)
                  └─ step 16: EffectRequest → HostExecutor::execute  (G15)
                       └─ world-visible effect
```

### 0.2 Host-reachable paths (exhaustive by construction)

| Path | Host call | External effect possible? | Binding obligation |
|---|---|---|---|
| **P1** Live issuance: steps 1–16 | `execute(EffectRequest)` at step 16 only | Yes (subject to R-HOST-01 authoritative recheck) | R-EFFECT-01/03/17, REQ-EFFECT-005/016/017/018, R-DUR-01/02 |
| **P2** Host authoritative policy check (defense in depth) | inside P1, at the host | No unless `HostPolicyOK(E)` **and** machine gates passed | R-HOST-01 (`¬HostPolicyOK(E) ⇒ ¬ExternalEffect(E)`); C-27 |
| **P3** Reconciliation / supervisor / retry / compensation | supervisor's host handle | Yes — must re-enter P1 in full | R-RECOV-08 (`Reconcile(E) ⇒ Issued(E) ∧ outcome ∈ AdmissibleOutcomes(class(E))`; compensation = ordinary `Request` through gates 1–16; supervisor.host only via issuance boundary), R-KERN-06, R-HOST-02 |
| **P4** Replay (`ReplayHost`) | consumes recorded trace | **No** — never touches the world | R-HOST-03/04/05, R-HOST-06; unordered map forbidden (C-22) |
| **P5** (must be provably impossible) Raw `Block` → `step()` | — | — | R-ARCH-03, R-COMPILE-01/05, R-ORDER-03 |
| **P6** (must be provably impossible) Planner/supervisor direct host call outside P1/P3 | `execute` without issuance | Yes | R-PLANNER-02, R-KERN-06, R-TRUST-05 (=SEC-022/SEC-015 remediation), R-ARCH-05 |
| **P7** (must be provably impossible) Receipt-forged resumption | (no host call; resumes actor) | No direct host effect, but can mint a false completion | R-EFFECT-06/08, R-HOST-06, M017/M018/M019/M020/M029 |

**Path-total proof obligation (PO-PATH):** every call site of any host executor
(live, replay, supervisor, reconciliation, integration code) satisfies
`DurableIssued(E)` **before** the call — R-HOST-02 binds *every* caller ("host performs
only issued effects"), reinforced by R-KERN-06 and R-RECOV-08; enforced by
`PanicHost` wrapping *all* host handles (R-REF-06, R-KERN-06 conformance) and by the
structural crate hinge `ror-runtime → ror-persistence` (R-TRUST-05, SEC-022 V-10).

---

## 1. Gate-by-gate proof obligation matrix

Mapping: **G1–G15** = the requested gates; **s1–s16** = canonical spec steps
(L38024–38045). G13 subsumes spec steps 13 **and** 14 (see 1.13).

Used in every row:

- **Denial = 5 assertions** (R-EFFECT-04, REQ-EFFECT-019…023): after a denial —
  (a) no later gate runs, (b) `next_effect_id` unchanged, (c) actor budget unchanged,
  (d) event log unchanged, (e) `HostExecutor::execute` never invoked.
- Gate numbers below are canonical-step numbers. Caveat (C-01 residual, **GAP-01**):
  the source never explicitly maps old "gate N" numbering onto step numbers; the
  resource-accounting audit (Op-16) uses a *different* numbering (it calls the ceiling
  "Gate 10" and the deadline "Gate 11"); the 14-gate [30] sketch uses yet another.
- Fault **names** are quoted as frozen where pinned, with the U-08 naming storm noted.

### G1 ⊢ s1 — Evaluate capability
| | |
|---|---|
| Operation | CEK evaluates the `Request` capability expr (frame `RequestCapability`; L21473–21525; R-CEK-03). |
| Invariant established | The value is a `Value::Capability(CapRef)`; capability evaluation strictly precedes target/params; a non-capability short-circuits before any target/arg evaluation (Track A, L24035). |
| Error path | (a) pure evaluator fault inside the capability expr (ordinary CEK faults, e.g. `TypeError`, arity) — no gate has run, no durable state, no host call; (b) evaluated value is not `Value::Capability` ⇒ `Fault::TypeError { expected: "Capability", actual: "non-capability" }`, `ActorStatus::Fault`, `MachineEvent::Fault` (L21500–21525). **Defect:** `Fault::TypeError` is a *twelfth* style of used-but-undeclared `Fault::` path (X-69, U-08) — it is not in the frozen R-CALC-06 enumeration. |
| Proof obligation | `PO-G1`: ∀ Σ: `eval(cap)` faults or returns non-capability ⇒ ¬(target evaluated) ∧ ¬(params evaluated) ∧ ¬any gate 4–16 runs ∧ ¬(host invoked) ∧ ¬(ID/budget/log mutated). Also: `eval(cap)` is deterministic and journalable (R-CEK-01/06, R-CORE-08) and performs no host dependency (REQ-CEK-024). |
| Normative anchor | R-CEK-03/05, REQ-EFFECT-005, Track A; R-CALC-02 (`Request{capability, operation, target, params}`); R-ARCH-03. |
| Verification | CEK frames / Track A; no obligation **tag** exists for request-capability short-circuit (see GAP-06). |

### G2 ⊢ s2 — Evaluate target
| | |
|---|---|
| Operation | CEK evaluates the target expr (frame `RequestTarget`; L21526–21559). |
| Invariant established | Target value produced; strictly after capability, before first param. |
| Error path | Pure evaluator fault only. **There is no target-domain validation gate**: `resume_request_target` performs no type/shape check on the evaluated target (L21530–21557). Target validity only surfaces later: canonical-encodability (G4) or scope membership `target ∈ ⟦A_op.S⟧` (G6). The `Target` domain itself is open (U-21). |
| Proof obligation | `PO-G2`: order determinism; target eval has zero host/budget side effects; a target that cannot be *authorized* yields a G6 denial, never a host call; target bytes are part of the canonical `Effect` (G4) so no un-canonical target reaches G6. |
| Normative anchor | R-CEK-03/05, REQ-EFFECT-005; R-CAP-01/R-CAP-06 (`⟦S⟧ ⊆ Target`); U-21. |
| Verification | Track A; **no dedicated tag** (GAP-06); U-21 blocks domain tests (GAP-02). |

### G3 ⊢ s3 — Evaluate parameters left-to-right
| | |
|---|---|
| Operation | One argument per CEK step (frame `RequestArgument`; L21559–21660). Invariant: exactly one arg removed from `remaining` per evaluation (L21646–21660); order is strict LTR. |
| Invariant established | `evaluated = [v₁,…,vₖ]` in source order; no arg evaluated after a prior arg faults; no param evaluated before target/capability. |
| Error path | (a) pure evaluator fault in any param expr — no host call, no budget/ID mutation; (b) **no Op-arity/type check exists**: the Op signature is part of U-21, so arity mismatch is not a frozen request error; it surfaces at G4 (canonicalization) if at all. (c) the frozen helper uses `continuation.pop().expect("request frame")` — a panic magnet (C-83; → R-CORE-12: must be `InternalInvariant`, never panic). |
| Proof obligation | `PO-G3`: ∀ k: exactly k args evaluated iff params 1..k succeeded; evaluation order is deterministic and trace-observable; params affect the `Effect` only via the canonical `Params` value; no host/budget side effects. |
| Normative anchor | R-CEK-05 (LTR), REQ-EFFECT-005, R-CORE-12, R-BUDGET-06. |
| Verification | Track A; `CEK-CALL-ARGS-LTR` covers **call** args only — request args have no frozen tag (GAP-06); U-21 blocks param-domain tests. |

### G4 ⊢ s4 — Construct canonical `Effect` (+ digest)
| | |
|---|---|
| Operation | `canonicalize_effect(capability, operation, target, evaluated)` ⇒ immutable `Effect { capability, operation, target, params, cost }`; `EffectDigest = SHA-256(canonical_bytes(effect))` (L23863–23873 sketch; R-CALC-04, REQ-EFFECT-006, REQ-CALC-008). |
| Invariant established | The exact effect object that is later authorized == the exact object that is journaled == the exact object the host receives; digest is the causal identity for journal, receipt, replay (R-DUR-03/08, R-HOST-06). |
| Error path | **Serialization failure (the primary one):** `Err(e) ⇒ fault_actor(Fault::EffectCanonicalization(e))`, short-circuit before any gate (L23863–23867). **Defects:** (i) `EffectError` has **no declaration anywhere** (U-14/X-67 class; only `CapabilityError` and `HostFault` are declared — U-08); (ii) the canonical encoding of `Op`/`Target`/`Params` is **not in the 15A tag set** (U-21, U-02) — so digest construction is not implementable byte-deterministically today; (iii) R-MARSHAL-05/R-CORE-13 declare ONE unified `MarshalFault` while R-CALC-06 keeps `EffectCanonicalization(EffectError)` — the mapping of a `CanonicalError` on this path is **ambiguous** (GAP-03); (iv) the **cost term** is part of `Effect` (R-CALC-05) but the frozen sequence never states *where* cost is computed (CostModel per R-BUDGET-07; static bound per R-COMPILE-03) or what faults if it overflows on construction (GAP-04). |
| Proof obligation | `PO-G4`: construction is total-on-admissible and fallible only by declared fault; `digest(E)` is deterministic across production/reference (R-CANON-09/13); `E` is immutable and cannot be re-constructed differently on the authorization vs journal vs host path; no capability-expansion during construction (R-CORE-07). |
| Normative anchor | R-CALC-04/05, REQ-EFFECT-006, REQ-CALC-008, R-CANON-01…13, R-BUDGET-02/07. |
| Verification | `EFFECT-RECEIPT-DIGEST-VALIDATION`; golden vectors (R-CANON-11); U-02/U-21 blocking. |

### G5 ⊢ s5 — Validate CapRef (lineage/liveness)
| | |
|---|---|
| Operation | Kernel `valid(c,t)`: `Valid(c,t) ⇔ Live(c) ∧ t ∈ Lifetime(c) ∧ ∀a ∈ Ancestors(c). Live(a)` (R-CAP-07, REQ-CAP-013, REQ-EFFECT-007). Possession-gated form: `c ∈ CapabilityContext(actor)` is a conjunct (R-KERN-04, R-CORE-11). |
| Invariant established | The reference is live and fully valid **before** authorization; revoked/expired/dangling refs never reach G6. |
| Error path | `Revoked` / `AncestorRevoked` / `Expired` ⇒ `Fault::Capability(CapabilityError)` (declared inner set: `Revoked`, `Expired`, `InvalidConstraint`, elided — L20408; **declared-vs-used conflicts**: `CapabilityError::Invalid` used undeclared at L20835, C-56; nine historical names for this outcome — C-08 → U-08; v0.3 calls it `CapabilityViolation`, REQ-EFFECT-038). Denial = 5 assertions; M004 (accept revoked). |
| Proof obligation | `PO-G5`: `valid` is pure over kernel state + logical time `t`; ancestor walk is O(depth) and deterministic; generation mismatch cannot validate (R-KERN-01); **possession set survives recovery before gate authorization** (R-KERN-05, R-PERSIST-07: `∀a ∀c∈caps(a): Valid(c,t_recovered)`; M023); revocation monotonic across crashes. |
| Normative anchor | R-CAP-07/09, R-KERN-01/04/05, REQ-CAP-013, REQ-EFFECT-007, R-PERSIST-07 (SEC-004 remediation). |
| Verification | `CAP-REVOCATION-ANCESTOR`, M004, M023; `RECOVERY-REVOCATION-DURABLE`. |
| Open/blocking | **U-36**: `Lifetime {start,end}` is annotated "Unix timestamp" three times yet compared against `LogicalTime` at this gate — wall-clock-vs-logical-time is **unresolved and blocks the gate's provability** (DET-006, C-100). U-02 (CapRef/authority encoding) blocks R-PERSIST-07 byte-level evidence. |

### G6 ⊢ s6 — Authorize the exact effect
| | |
|---|---|
| Operation | `Authorized(holder, c, E, t) ⇔ c ∈ κ_holder ∧ Valid(c,t) ∧ Authorized(κ(c), E, t)` (R-CORE-11 canonical signature; R-KERN-04) where the kernel conjunct is the 5-conjunct predicate: `op ∈ O_A ∧ target ∈ ⟦A_op.S⟧ ∧ A_op.Q(params) ∧ cost ≤ A_op.R ∧ t ∈ A_op.T` (R-CAP-06, REQ-CAP-010, REQ-EFFECT-008). **Exactly one** `authorize` call (Track B). |
| Invariant established | The *exact* canonical `Effect` (same object, same digest) is authorized at logical time `t`; the authority's operation, scope, param predicate, **resource ceiling**, and lifetime all hold. |
| Error path | `Unauthorized` / authority denial ⇒ `Fault::Capability(CapabilityError)` family (names: `CapabilityViolation`, `CapabilityRevoked`, `AuthorizationFailed`, `CapabilityDenied`, `CapabilityError`, `Capability(CapabilityError)`… — C-08 → U-08). Denial = 5 assertions; M005 (omit ceiling); M004 (revoked at auth). Note the [30] sketch folds G5+G6 into one `kernel.authorize` call and gates 4–7 comments (L23874–23888) — the canonical 16-step form keeps them separate. |
| Proof obligation | `PO-G6`: `Authorized(holder,c,E,t)` iff all 5 conjuncts **and** possession hold; the authorized object is byte-identical (`EffectDigest`) to the G4 artifact; no re-authorization of a different effect; logical time only (R-CAP-09) — no wall clock (U-36); target scope and param constraint cannot be satisfied by a widened representation (U-21). |
| Normative anchor | R-CAP-06, R-KERN-04, R-CORE-11, REQ-CAP-010, REQ-EFFECT-008; R-TRUST-03 (evaluator never sees authority internals). |
| Verification | Track B mock-kernel exactly-one-call; M004/M005; R-KERN-04 test (`M021` brute-force CapRef exhaustion from non-holder). |
| Open | U-21 (Q/params domain), U-36 (lifetime), U-02 (constraint encoding), AMB-12/U-09 (admissibility — resolved in security direction by R-CAP-10/M030 but only for `Attenuate`/derive, not for request params). |

### G7 ⊢ s7 — Enforce capability resource ceiling
| | |
|---|---|
| Operation | `cost(E) ≤ A_op.R` (capability ceiling `R_A`), the resource conjunct separated from the runtime budget (dual gate): REQ-EFFECT-009, REQ-CAP-011, R-BUDGET-04 (`WithinBudget`'s third conjunct). |
| Invariant established | The effect's static cost cannot exceed the *capability's* ceiling, independent of how much runtime budget the actor holds (REQ-CAP-011: conflating → a rich budget overrides a narrow grant — a bug). |
| Error path | Ceiling violation ⇒ authority-shaped denial: `Fault::Capability(CapabilityError)` in the [30] composite form; if implemented as a separate check the frozen name is ambiguous (the sketch says "explicitly checked here if separated", L23879–23883). Denial = 5 assertions; M005 if omitted. |
| Proof obligation | `PO-G7`: `cost(E) ≤ R_A` is evaluated **before** any budget debit; the static cost is the *same* `cost(E)` authorized at G6 (no cost inflation between G6 and G7); ceiling is per-operation (`R` component of `A_op`; R-CAP-02). |
| Normative anchor | R-BUDGET-04, R-CAP-06/11, REQ-EFFECT-009, REQ-CAP-011. |
| Verification | Track C short-circuit; M005. |

### G8 ⊢ s8 — Runtime consumable budget (issue + complete_max)
| | |
|---|---|
| Operation | `can_consume(issue.checked_add(complete_max))` (REQ-EFFECT-010/024, R-EFFECT-05, REQ-CALC-011). |
| Invariant established | Worst-case completion is affordable — `remaining ≥ complete_max` **after issuance**, so completion accounting cannot fail (REQ-EFFECT-026; the C-23 fix: the pre-correction form checked only `issue` and charged `complete` at receipt, which could fail — L25479–25492/L25799–25825; the [30] sketch L23892–23896 still shows the *pre-fix* form and is superseded by C-01/C-23). |
| Error path | `BudgetExhausted` (R-BUDGET-08, REQ-BUDGET-032: no partial debit, `Σ' = Σ`); **overflow** ⇒ `Fault::ArithmeticOverflow`/budget fault (REQ-EFFECT-025) — **`ArithmeticOverflow` is not in the frozen `Fault` enum** (AMB-08, U-01/U-08) — GAP-04. |
| Proof obligation | `PO-G8`: `checked_add` never wraps; gate 8 denial precedes ANY debit and satisfies the 5 assertions; given gate 8 success, charged+escrowed ≤ C; the `D` consumable dimension's semantics are pinned before the gate is testable (U-01 → AMB-01). |
| Normative anchor | R-BUDGET-02/05/08, REQ-BUDGET-012/025, REQ-EFFECT-010/024/025/026, REQ-CALC-010/011. |
| Verification | `BUDGET-ESCROW-CONSERVATION`; M007 (omit budget gate); M009 (negative resources); overflow boundary test. |
| Open | U-01 (operational meaning of `D`) — "exhaustion behavior is not testable until decided" (MOD-04). |

### G9 ⊢ s9 — Reserve runtime resources
| | |
|---|---|
| Operation | `ReserveOK(cost_R(E), R, R_max) ⇔ R + cost_R(E) ≤ R_max` (R-BUDGET-03, REQ-BUDGET-009, REQ-EFFECT-011; REQ-CALC-012). |
| Invariant established | Reservation amounts are within capacity and reversible: `R_n + Σ release_i = R_0 + Σ reserve_i`; `ReleaseOK(r,R) ⇔ r ≤ R` (frozen correction of the pre-fix mixed-direction `BudgetOK`, C-07). |
| Error path | `ReservedCapacityExceeded` (a `BudgetError`, R-BUDGET-02) ⇒ machine fault `Fault::BudgetExhausted` per R-BUDGET-08 ("any failed gate ⇒ `fault(BudgetExhausted)`"); the [30] sketch implements exactly this (L23897–23900). Denial = 5 assertions; no partial reservation. |
| Proof obligation | `PO-G9`: checked add `R + r` never overflows; denial leaves `R` unchanged; the reserved capacity is released exactly once on receipt (R-EFFECT-033) and **not** released on receipt mismatch (REQ-EFFECT-030), and survives crash for Indeterminate effects (R-DUR-05/RECOV — escrow/reservation durability gap, see 1.13/GAP-07). |
| Normative anchor | R-BUDGET-02/03/05, REQ-BUDGET-009/010, REQ-EFFECT-011, REQ-CALC-012. |
| Verification | reservation property tests; conservation tests; M009. |

### G10 ⊢ s10 — Validate deadline
| | |
|---|---|
| Operation | Deadline check at logical time `t` (REQ-EFFECT-012 records `t ≤ W`; R-CAP-09: logical time only). |
| Invariant established | The machine does not issue at/after deadline; `∀ active steps i: t_i ≤ W` (REQ-BUDGET-021). |
| Error path | `Fault::DeadlineExceeded` ([30] sketch L23901–23905; declared in R-CALC-06). Denial = 5 assertions. |
| Proof obligation | `PO-G10`: **predicate discrepancy — GAP-05.** Three frozen readings exist: (a) REQ-EFFECT-012 pins `t ≤ W` (pre-advance); (b) R-BUDGET-06 / REQ-BUDGET-021 / v0.3 `E-Request` premise require `t + δ_t(req) ≤ W` (post-advance); (c) the [30] sketch implements the **weaker** reading (`now > w`). The weak reading permits issuing an effect whose own transition pushes time past `W`, then invoking the host after deadline — a deadline-violation path. The stronger reading must govern: `t + δ_t(req) ≤ W`. Also: `δ_t(req)` values are **open** (U-07 → AMB-19), so the gate is not currently evaluable; and deadline-vs-`Lifetime` interaction is open (U-01/U-36). |
| Normative anchor | R-BUDGET-06, REQ-BUDGET-021, REQ-EFFECT-012, R-CAP-09, v0.3 E-Request (REQ-EFFECT-037). |
| Verification | deadline gate test; deadline-exhaustion tests; U-07 blocks. |

### G11 ⊢ s11 — Validate HostPolicy (fail-early)
| | |
|---|---|
| Operation | Machine-side `HostPolicyOK(E)` as a **fail-early** gate (REQ-EFFECT-013, R-HOST-01, C-27); authoritative re-check happens at the host (P2) — machine check ⊂ host check. |
| Invariant established | `HostPolicyOK(E)` holds at issuance; last machine-side barrier before authorization-free commit. |
| Error path | Machine gate denial ⇒ `Fault::HostPolicyDenied(HostPolicyError)` ([30] L23906–23909; R-CALC-06) — **`HostPolicyError` has no declaration** (U-14; only `CapabilityError`, `HostFault` declared — U-08/C-57); v0.3 names it `HostPolicyViolation` (REQ-EFFECT-038, AMB-08). Denial = 5 assertions. **Distinct error path:** the **host's authoritative** denial after step 16 is NOT a gate denial: the machine has already durably issued, grown escrow, and parked the actor; the host returns `Err(HostFault::PolicyViolation(String))` — R-HOST-01's `¬HostPolicyOK(E) ⇒ ¬ExternalEffect(E)` still holds (no world effect), but the machine has an Issued-not-Executed effect that must be resolved via the host-failure receipt path (Op-19: escrow disposed by host-failure consumption, `c_host_fail ≤ complete_max`, remainder refunded; R-BUDGET-09 "C-23 rule"; reservation released per R-EFFECT-07) — and **R-EFFECT-07's "host faults map to the fault/value mapping defined by the machine" is marked AMBIGUOUS (REQ-EFFECT-036 → U-08/AMB-08)**; partially closed in the security direction by R-CORE-13 (closed set, no debug text) but the variant set is not enumerated (GAP-08). |
| Proof obligation | `PO-G11`: machine fail-early check is a pure predicate over the canonical `E`; denial satisfies the 5 assertions; the host re-validates OS-level authority independently even though the machine gate passed; a machine-side policy bug alone cannot yield an unauthorized external effect (MOD-09 security boundary). |
| Normative anchor | R-HOST-01/02, REQ-EFFECT-013, REQ-HOST-001/002/003, C-27; R-CORE-13 (SEC-012). |
| Verification | host policy tests; defense-in-depth review; U-14/X-67 blocks the host error type (BLOCKING per U-08/U-14). |

### G12 ⊢ s12 — Allocate deterministic EffectId
| | |
|---|---|
| Operation | `h = N_h; N_h' = N_h + 1` — global monotonic counter (REQ-EFFECT-014, R-ACTOR-03, REQ-CALC-009); never wall-clock/memory-address/random (R-EFFECT-03). |
| Invariant established | Deterministic, collision-free, monotone ID; allocated **after** all gates 1–11 pass. |
| Error path | None (allocation is infallible by construction). Two unpinned edges: (a) counter **overflow** (u64) — no frozen rule (GAP-04, U-37 fixed-width decision open); (b) counter **reconstruction after crash**: snapshots carry ID counters (R-PERSIST-04), but no recovery step is pinned to advance `next_effect_id` from replayed `Issued` records — a crash between s12 and s14 rewinds the counter if only snapshots carry it (safe), yet if a snapshot is taken *after* s12 with no journal record, recovery needs an explicit reconcile rule (GAP-09). |
| Proof obligation | `PO-G12`: ID is not allocated before authorization (M010); denial at any earlier gate leaves `next_effect_id` unchanged (REQ-EFFECT-020); ID equality across journal records (R-DUR-08); ID stream gap-free-after-issuance and deterministic across live/replay (R-ACTOR-03, R-CORE-08). |
| Normative anchor | R-EFFECT-03, REQ-EFFECT-014/020, R-ACTOR-03, REQ-CALC-009; M010. |
| Verification | Track C assertion; M010. |

### G13 ⊢ s13 + s14 — Commit budget/reservation, then durable issuance
**This is the invariant-critical gate. It is TWO commits: step 13 (in-memory
budget/reservation) and step 14 (durable `Prepared`→fsync→`Issued`→fsync).**
The ordering — in-memory commit **before** durable append — is frozen, and is the
root of the journal-failure hazard (1.13.3, GAP-07).

#### 1.13.1 Step 13 — transactionally commit issue budget + reservation
| | |
|---|---|
| Operation | `budget.consume(issue)`, `budget.reserve(reserve, …)`, escrow `complete_max` (REQ-EFFECT-015, REQ-CALC-011/012, R-CALC-05, R-BUDGET-05). |
| Invariant established | Atomically: `C_available − (issue+complete_max)`, `C_consumed + issue`, `C_escrowed + complete_max`, `R + reserve`. |
| Error path | REQ-EFFECT-015: "the commit cannot fail after gate 8" — enforced by checked arithmetic, **not by unwrap**: [30] sketch uses `.unwrap()` (L23905–23920) — the C-83 panic magnet, resolved by R-CORE-12 (any check/commit drift ⇒ `Fault::InternalInvariant` family, observable + differentially comparable; panic-free machine paths). A drift *is* a bug; the obligation is that it faults rather than panics. |
| Proof obligation | `PO-G13a`: gate-8/gate-9 success ⇒ commit is infallible (checked arithmetic); if it ever faults, `InternalInvariant`, 5-assertion-clean. |

#### 1.13.2 Step 14 — durable issuance (R-DUR-02 strict 7-step form)
| | |
|---|---|
| Operation | 1. (gates already done) 2. `append(EffectPrepared {id, actor, digest})` 3. `sync()` (fsync) 4. `append(EffectIssued {id, actor, digest})` 5. `sync()` (fsync) 6. **next is step 15** 7. **next is step 16** (REQ-DUR-002; REQ-DUR-003/004: Prepared fsynced before Issued; Issued fsynced before Pending and before any host call). |
| Invariant established | `DurableIssued(E)` — the `Issued` record is on stable storage **before** the actor becomes Pending (s15) and before any host call (s16). This is the whole `HostInvoked ⇒ DurableIssued` hinge (R-DUR-01/04, R-CORE-06). |
| Error path | **Journal failure (the critical one) — GAP-07:** an `append` or `sync` error between s13 and s14b has **no frozen live-failure semantics**: (i) resource-accounting Op-17 says "storage write failure yields `Fault::PersistenceError`. Actor paused/parked" — **`Fault::PersistenceError` is not in the frozen R-CALC-06 enumeration nor in R-CORE-13's explicit additions** (U-08); (ii) a live fault at this point CANNOT satisfy R-EFFECT-04's 5 assertions — steps 12–13 already mutated `next_effect_id`, budget, reservations in memory; (iii) R-CORE-12 requires "durable appends MUST precede irreversible in-memory mutations where feasible, **or the commit MUST be journal-driven**" — but **no budget/reservation journal record kind exists** (R-PERSIST-03 defines only six `WalRecord` kinds: Event, EffectPrepared, EffectIssued, EffectCompleted, EffectReconciled, SnapshotCommit), so "journal-driven commit" is **unimplementable per the frozen taxonomy**; (iv) the second `sync()` failing (record may or may not be on disk) has no live-handling rule (retry / park / classify) — only the crash-matrix conservatism covers *crashes*, not live storage errors. |
| Proof obligation | `PO-G13b`: (1) if step 14 returns Ok, `DurableIssued(E)` is true at the s15 boundary; (2) if step 14 returns Err: host is **never** invoked, the transition faults with a *declared* fault, and the machine state after the fault is either rolled back to the s11 state or journal-driven — one of the two must be specified and is **not**; (3) no code path can construct the `EffectRequest` handed to the host without passing the `sync()` boundary (object graph + call-graph proof, PanicHost double, R-TRUST-05 crate-edge proof). |
| Normative anchor | R-DUR-01/02/03/04/05, REQ-DUR-001…014, R-CORE-06/12, R-EFFECT-05 (REQ-EFFECT-024), R-PERSIST-02/03/08, R-TRUST-05. |
| Verification | `EFFECT-ISSUE-DURABLE-BEFORE-HOST`; `PanicHost`; crash harness T0–T4 (R-TEST-08); M015/M016 (WAL gap/checksum); M034 (panic-free); SEC-020 crash-extension test. |

#### 1.13.3 Journal record payload gap
`EffectPrepared { id, actor, digest }` and `EffectIssued { id, actor, digest }` carry **no
effect payload and no cost** (R-PERSIST-03, spec/01 S-18; by contrast, the [30] sketch's
in-memory log entry carried `issue_cost` + `reservation` — L23863–23873 — and the v0.3
formal rule's log entry carried the full effect `EffectIssued(h, Hash(E), E)` — L8743;
both were dropped from the frozen durable taxonomy, and R-PLANNER-07 froze the
`{id, actor, digest}` shape for the planner-visible log). Consequences (**GAP-07b**):
- At T2–T4, `D = ⟨S,L,H⟩` cannot reconstruct `E` (digest is a hash, not invertible), and
  reconciliation ("did the host execute E?") has only `id + digest` identity. Works only
  if the host keeps its own correspondence; the frozen protocol does not state it
  (R-RECOV-08's "idempotent host query at most" needs an id base).
- R-DUR-013/014 + REQ-RECOV-013 require the escrowed `complete_max` to survive crash
  **identically**, but the durable records carry **no cost** and there is **no
  budget-journal record kind**: the escrow is recoverable only if a committed snapshot
  happens to contain it. Snapshot timing is **not frozen** (no trigger/interval rule in
  R-PERSIST-04/05 or anywhere in the persistence registry) — crash-window dependence,
  GAP-10.
- T1's "discard; budget restored" (REQ-DUR-010, REQ-RECOV-004) has no mechanism
  statement (what durable fact identifies the amounts to restore, and via which record?).

### G14 ⊢ s15 — Transition actor to Pending
| | |
|---|---|
| Operation | `status ← Pending(h, E, K)` — **the only path to `ActorStatus::Pending`** (REQ-EFFECT-016; [30] L23922–23928; v0.3 E-Request). |
| Invariant established | Pending holds `{effect_id, effect, continuation, reservation}`; scheduler never selects Pending (`SCHED-BLOCKED-NOT-SCHEDULED`; MOD-07; REQ-ACTOR-011); receipts only discharge Pending. |
| Error path | None (infallible in-memory transition). Crash **between s14 and s15** = T2 (`Issued ∧ ¬Completed ⇒ Indeterminate`); crash **between s15 and s16** = T2/T3 (same classification; host may or may not have been invoked). **GAP-11:** the continuation `K` and the effect `E` live only in actor state; no frozen record carries them; T5's "reconstruct completed effect; **resume continuation**" (REQ-RECOV-008) and T2's later `Completed`-path resumption therefore depend on a snapshot having captured the post-request actor state — unstated, and U-02 (machine-state encoding incl. EvalState/continuations) is blocking (MOD-05 open items, R-PERSIST-04 content list). |
| Proof obligation | `PO-G14`: `Pending` implies `DurableIssued(E)` (step order); Pending ⇒ not runnable; no path sets Pending with a different E or K; at T2/T5 the durable artifacts plus snapshot suffice to reconstruct `{E, K}` — **currently unprovable**. |
| Normative anchor | REQ-EFFECT-016, R-EFFECT-03, MOD-06/07, R-ACTOR-07; U-27/U-34/U-02. |
| Verification | status-transition conformance; `SCHED-BLOCKED-NOT-SCHEDULED`; crash T2/T5 harness. |

### G15 ⊢ s16 — Invoke host
| | |
|---|---|
| Operation | Yield `EffectRequest` to the host adapter — the **last** step; the only host call on P1 (REQ-EFFECT-017, R-EFFECT-03, R-DUR-02 step 7). |
| Invariant established | `HostInvoked(E) ⇒ DurableIssued(E)`; host performs **only** issued effects (R-HOST-02). |
| Error path | Host errors are post-issuance (not gate denials): valid receipt with `Err(HostFault)` ⇒ host-failure accounting (Op-19, R-BUDGET-09) and resume/fault mapping (REQ-EFFECT-036 AMBIGUOUS → R-CORE-13 partial closure, GAP-08); host policy refusal ⇒ `¬ExternalEffect` (R-HOST-01) but effect remains Issued-not-Executed; host **executes then crashes before returning** ⇒ T4 `Indeterminate`. |
| Proof obligation | `PO-G15`: every `execute` call site is preceded by durable issuance (trace/PanicHost/crate-edge evidence); the host cannot fabricate a receipt that resumes an actor (R-EFFECT-06/08, R-HOST-06, M017/M018/M019/M020/M029); the host's world action is constrained to the exact issued canonical `E` (adapters accept canonical bytes; R-ARCH-05 out-of-process mode). |
| Normative anchor | REQ-EFFECT-017/018/023, R-HOST-01/02/04, R-DUR-01/04, R-CORE-06, R-KERN-06. |
| Verification | `EFFECT-ISSUE-DURABLE-BEFORE-HOST`; `PanicHost`; replay property tests; live-vs-replay differential (MOD-15). |

---

## 2. The critical invariant — proof sketch and its obligations

**Theorem (spec-level target):** `HostInvoked(E) ⇒ DurableIssued(E)` (R-DUR-01,
R-CORE-06, REQ-DUR-001).

Derivation chain (each implication is an obligation):

```
HostInvoked(E)
  ⇔ step 16 executed for E                    [REQ-EFFECT-017: s16 is the only host call on P1; PO-PATH for P3]
  ⇒ Pending(E) at the time of the call        [REQ-EFFECT-016: only path to Pending; s15 precedes s16]
  ⇒ append(EffectIssued{E}) returned Ok
     ∧ sync() (2nd) returned Ok                [REQ-DUR-004: Issued fsynced before Pending/host]
  ⇒ DurableIssued(E)                           [definition: durable = append + fsync complete; R-DUR-02]
```

The load-bearing obligations:

| # | Obligation | Status / blocker |
|---|---|---|
| OBJ-1 | **Ordering:** s12–s16 are executed in frozen order; no reorder/skip; M010 (EffectId before authorization) must kill. | SPECIFIED (REQ-EFFECT-005); C-01 residual numbering (GAP-01). |
| OBJ-2 | **Atomicity:** s12–s16 are one runtime transition (no scheduler yield between s14b and s16 that could expose half-state). | **Implicit** — R-CORE-12 transition atomicity + R-EFFECT-04 five assertions; not stated as an inter-step property of the 16-step sequence. GAP-12. |
| OBJ-3 | **Durability semantics:** `sync()` completes = record on stable storage; two fsyncs at REQ-DUR-003/004; WAL framing/checksum/sequence rules (R-PERSIST-02/06/08) make `DurableIssued` meaningful. | SPECIFIED; R-PERSIST-08 (chained checksums, keyed if adversarial) resolves C-88. |
| OBJ-4 | **No alternate host path:** every host handle passes through the issuance boundary (supervisor removed/typed, R-KERN-06; reconciliation re-enters gates, R-RECOV-08; replay never touches world, R-HOST-03; out-of-process adapter, R-ARCH-05; crate hinge `ror-runtime → ror-persistence`, R-TRUST-05). | SPECIFIED; PanicHost-wraps-all-handles conformance + Cargo.toml DAG mechanical check. |
| OBJ-5 | **Identity chain:** `Issued ⇒ Prepared`, `Completed ⇒ Issued`, `Reconciled ⇒ Issued`, identical id+digest per effect (R-DUR-03/08); mismatch = `EffectJournalCorruption` (REQ-DUR-009) — naming conflict: REQ-DUR-009 vs R-RECOV-05's `RecoveryFault` for invalid durable state, vs U-08 (GAP-13). | SPECIFIED; ENUM named-only. |
| OBJ-6 | **Crash induction:** at every crash point T0–T6, recovered classification matches the durable prefix exactly; no classification contradicts the journal (SEC-020 test, M10). | SPECIFIED; GAP-07/GAP-10/GAP-11 above block T1/T2/T5 *reconstruction* (as opposed to classification). |
| OBJ-7 | **No early emission:** the `EffectRequest` object is constructed only at s16; nothing observes a pre-issuance request (evaluator's only side-effect vocabulary is `EvalStep::RequestEffect`, REQ-CEK-024). | SPECIFIED; code-graph review (R-CLAIM-02 #10). |

---

## 3. Error-path matrix (requested classes)

Columns: class → gate(s) where it can occur → frozen/actual fault names → short-circuit
behavior → state deltas on denial → crash classification → verification → open item.

| Error class | Occurs at | Fault (frozen as declared) | Fault (as used/historical — U-08) | Short-circuit | State delta | Crash class | Verification | Open |
|---|---|---|---|---|---|---|---|---|
| **Capability failure** | G1 (bad *value*), G5 (bad *reference*) | G5: `Fault::Capability(CapabilityError)`; G1: values must type-check | `CapabilityViolation`, `CapabilityRevoked`(±payload), `AuthorizationFailed`, `CapabilityDenied`, `Fault::CapabilityError`, `TypeError` (G1, undeclared), v1 `CapViolation`/`Revoked` | G1: no target/params eval (Track A). G5: 5 assertions | G1: actor `Fault` status only. G5: none | T0 (pre-durable) | M004; `CAP-REVOCATION-ANCESTOR`; M021; M023 | **U-36** lifetime vs logical time; C-08 nine names; CapabilityError self-conflict C-56 |
| **Target failure** | G2 (eval fault), G4 (unencodable), G6 (out of scope) | G4: `EffectCanonicalization(EffectError)`; G6: `Capability(CapabilityError)` | — | G2: no params/gates. G4/G6: 5 assertions | none until s13 | T0 | Track A | **No target-domain gate exists** (only eval fault); U-21 open (GAP-02) |
| **Parameter failure** | G3 (eval fault), G4 (unencodable), G6 (`Q(params)` fails) | G4/G6 as above; G3: pure CEK faults | — | G3: later params unevaluated; gates not reached | none | T0 | Track A; **no obligation tag** | No Op-arity/type gate; U-21 open (GAP-02, GAP-06) |
| **Authorization failure** | G6 | `Fault::Capability(CapabilityError)` | 9 names (C-08) incl. `CapabilityViolation`, `AuthorizationFailed`, `CapabilityDenied` | 5 assertions | none | T0 | Track B exactly-one-call; M004/M005/M021; R-CORE-11 | R-KERN-04 possession; U-02 authority encoding; U-21 |
| **Budget failure** | G8 (consumable) | `Fault::BudgetExhausted` | v0.3 `BudgetExhausted` (matches) | 5 assertions; **no partial debit** (REQ-BUDGET-032) | none | T0 | M007; `BUDGET-ESCROW-CONSERVATION` | U-01 (`D` semantics); overflow fault name AMB-08 (GAP-04) |
| **Reservation failure** | G9 | `Fault::BudgetExhausted` (R-BUDGET-08) | `BudgetError::ReservedCapacityExceeded` (data error type; mapping to Fault pinned only by behavior, not by name rule) | 5 assertions; no partial reservation | none | T0 | reservation property tests; M009 | R-BUDGET-10 (audit addendum) **not adopted** — dangling (GAP-14) |
| **Deadline failure** | G10 | `Fault::DeadlineExceeded` | — | 5 assertions | none | T0 | deadline gate test | **GAP-05** weak predicate (`t≤W` vs `t+δ_t≤W`); U-07 δ_t values |
| **Host-policy failure** | G11 (fail-early) | `Fault::HostPolicyDenied(HostPolicyError)` | v0.3 `HostPolicyViolation`; host-side `HostFault::PolicyViolation(String)` | 5 assertions (machine) | none (machine) | T0 (machine denial) | host policy tests | `HostPolicyError` **undeclared** (U-14); host-fault mapping REQ-EFFECT-036 AMBIGUOUS → R-CORE-13 partial (GAP-08); **host-side denial is post-issuance** → Indeterminate-shaped (Op-19) |
| **Serialization failure** | G4 (construct/digest) | `Fault::EffectCanonicalization(EffectError)` | (R-MARSHAL-05 unified `MarshalFault` may govern the same path — ambiguous) | `fault_actor`, no gate runs; 5 assertions hold (nothing mutated yet) | actor Fault only | T0 | negative encode tests; golden vectors | `EffectError` undeclared; U-21/U-02 (GAP-03) |
| **Journal failure** | s13/s14 (append/sync), live storage error | **none declared** — audit says `Fault::PersistenceError` (Op-17), R-CORE-12 says `InternalInvariant` family | — | **cannot satisfy 5 assertions as frozen** (s12/s13 already mutated) | budget/ID mutated in memory, no durable record | T0/T1/T2 by durable prefix (crash case only) | M015/M016; M034; SEC-020 crash-extension; `EFFECT-ISSUE-DURABLE-BEFORE-HOST` | **GAP-07** — no live error semantics; no budget journal record kind (GAP-09); `PersistenceError` undeclared |
| **Crash between gates** | all inter-step boundaries | see §4 | — | n/a | n/a | T0–T6 matrix | crash harness T0–T6 (R-TEST-08, M10) | **GAP-10/GAP-11** — snapshot-timing dependence; escrow/K reconstruction unproven; U-02/U-17 |

---

## 4. Crash-between-gates (the fine-grained matrix)

Frozen crash points (R-RECOV-02, REQ-RECOV-003…008): T0 before `Prepared`;
T1 after `Prepared`; T2 after `Issued`; T3 after host invocation; T4 after host
completion (not durable); T5 after durable `Completed`; T6 after `SnapshotCommit`.

Inter-gate boundaries inside the request sequence:

| Boundary (crash at) | Durable state | Required recovery result | Verdict |
|---|---|---|---|
| during G1–G3 (evaluation) | no issuance records (no `Prepared`/`Issued`; whether per-step CEK steps are journaled at all is U-28-open) | T0: effect does not exist; no budget mutation; resume — machine rewinds to last snapshot; deterministic re-execution reproduces (R-CORE-08, REQ-CEK-024: evaluator has zero host dependencies; pure steps δ_t=0 so no deadline drift) | **Sound**, provided determinism + pure-evaluation hold. |
| after s4 (construct) before s5 | none | T0 | Sound. |
| after G5–G11 (any gate denial already handled as fault, not crash) | none (denial ⇒ fault transition, no durability) | T0 | Sound (5 assertions). |
| after s12 (ID allocated) before s13 | none | T0: no ID leak. **If a snapshot commits after s12** with no journal record, recovery must reconcile `next_effect_id` — no frozen rule (GAP-09). | Classification sound; counter repair unpinned. |
| **after s13 (budget/reservation committed) before s14a (`Prepared` append)** | none (no record kind for the budget commit; records don't carry cost) | T0 text says "no budget mutation" — true **only if** no snapshot contains the s13 state. **Snapshot timing unfrozen** ⇒ a snapshot window here breaks the row (budget mutated + no effect + no host call = states T0's postcondition false). | **GAP-10.** Fix options: (i) prohibit snapshots inside s12–s16 (atomic section), (ii) journal the s13 commit, or (iii) add a T0.5 row. None is frozen. |
| **after s14a (`Prepared` fsynced) before s14b (`Issued`)** | `Prepared` only | T1: discard; **budget restored** (REQ-DUR-010, REQ-RECOV-004). | Classification sound. **Mechanism gap:** which durable fact carries the amounts to restore? No record kind (GAP-07b). Same snapshot-window caveat. |
| after s14b (`Issued` fsynced) before s15 (Pending) | `Prepared + Issued` | T2: `Indeterminate` + reconciliation. | Classification sound. **Reconstruction gap:** escrow amounts not in records (GAP-07b); actor continuation not durable (GAP-11); effect not in records (reconciliation identity = id+digest only). |
| after s15 (Pending) before s16 (host) | `Prepared + Issued` | T2 (host not yet invoked) / T3 (invoked) — **both classify `Indeterminate`**; the host-may-have-executed ambiguity is treated conservatively at T2 too (no "not executed" inference — R-DUR-12). | Sound (conservative; the host receives reconciliation for an effect that *probably* never ran — R-DUR-12 explicitly accepts this). |
| after s16 (host invoked) before host returns | `Prepared + Issued` | T3/T4: `Indeterminate`. | Sound. |
| after host returns, before `EffectCompleted` append/fsync | `Prepared + Issued` | T4: `Indeterminate` (completion not durable). | Sound. Note: **no frozen fsync requirement/step for `EffectCompleted`** (REQ-EFFECT-034 says "made durable per S-18" but S-18/R-PERSIST-02 has no completion-sync sub-step; R-HOST-06 freezes the record *content*, not its sync point) — a crash in the append/fsync window then classifies T4, which is safe but means the completed host effect requires reconciliation — acceptable, but the boundary is under-specified (GAP-15). |
| after `EffectCompleted` durable | `Completed` | T5: reconstruct completed effect; resume continuation **byte-exactly with the recorded result** (R-HOST-06, REQ-RECOV-008). | **GAP-11:** resumption needs `K` + actor state — not in any record; only snapshots carry them; U-02 blocks. Also `Completed` carries `{id, digest, result_digest, result}` — no continuation. |
| after `SnapshotCommit` while an effect is in flight | snapshot + WAL/journal | T6: recover base, replay; in-flight effects classified per the durable prefix. | Sound in principle; U-17 (queue authority), U-34 (state shapes), U-02 block byte-level conformance. |

**Crash-matrix meta-observation:** classification (what the effect *is*) is fully
frozen and provable. **Reconstruction** (what state the machine resumes with — actor
continuation, budget partitions, capability arena) depends on snapshot timing and on
machine-state encodings that are open (U-02) or unfrozen (snapshot cadence); and the
escrow/budget amounts needed at T1–T4 are not in the frozen record taxonomy. The M10
gate cannot pass on reconstruction evidence today.

---

## 5. Findings (blocking / major / gaps)

| ID | Severity | Finding | Evidence (normative anchors) |
|---|---|---|---|
| GAP-01 | MAJOR | Two different frozen "16-step" sequences coexist: `spec/01` R-EFFECT-01 publishes the **turn-[21] form** (L12177–12194: construct at step 13 **after** ID allocation; **host emit at step 15 before `Issued` at step 16** — literally violating `HostInvoked ⇒ DurableIssued` if read as ordering) while REQ-EFFECT-005/R-EFFECT-03/C-01 adopt the **master-prompt form** (L38024–38045: construct s4; durable issuance s14; Pending s15; host s16). C-01's resolution does **not** mention the L12177–12194 form at all; spec/01 R-EFFECT-01 remains normative-text. | spec/01 L257 vs L38024–38045; REQ-EFFECT-005; C-01 |
| GAP-02 | BLOCKING | No frozen `Target`/`Params`/`Op` domains, no Op-arity check, no target/param validation gate — G2/G3 are evaluation-only; target/param "failure" is real only as G4/G6 failure. U-21 is open and blocks digest construction. | U-21; R-CALC-02/04; REQ-EFFECT-006 (U-21 dependency), R-CAP-01 |
| GAP-03 | BLOCKING | Serialization-failure fault lane is ambiguous and undeclared: `EffectError` has **no declaration**; `EffectCanonicalization(EffectError)` (R-CALC-06) vs unified `MarshalFault` (R-MARSHAL-05, R-CORE-13) — same encode path, two fault families. | U-08/U-14; R-MARSHAL-05; REQ-CALC-013 |
| GAP-04 | HIGH | Overflow fault naming: `Fault::ArithmeticOverflow` (REQ-EFFECT-025) is **not in the frozen `Fault` enum** (AMB-08); counter overflow (G12) unpinned (U-37). | REQ-EFFECT-025 AMB-08; U-37 |
| GAP-05 | HIGH | Deadline predicate discrepancy: REQ-EFFECT-012 records `t ≤ W`; R-BUDGET-06/REQ-BUDGET-021/v0.3 `E-Request` require `t + δ_t(req) ≤ W`; the [30] sketch implements the weak reading; U-07 (δ_t values) open. A host invocation can occur after the deadline under the weak reading. | REQ-EFFECT-012 vs REQ-BUDGET-021 / REQ-EFFECT-037 / R-BUDGET-06; C-01; U-07 |
| GAP-06 | MEDIUM | No stable obligation tag for request-capability/target/params LTR + non-capability short-circuit: R-TEST-07's frozen tag list has `CEK-CALL-ARGS-LTR` (call args only); Track A's request-frame properties are untagged. | R-TEST-07 list; MOD-05 verification; MOD-08 Track A |
| GAP-07 | **CRITICAL** | **Journal failure (live) is unpinned**: (i) `Fault::PersistenceError` (audit Op-17) not in the closed enum; (ii) 5-assertion short-circuit impossible after s12/s13 mutations; (iii) no rollback rule; (iv) R-CORE-12's "journal-driven commit" alternative unimplementable — no budget/reservation journal record kind in R-PERSIST-03; (v) second-fsync failure has no live-failure rule. | Op-17 (audit only); R-CORE-12; R-PERSIST-03; REQ-EFFECT-015/019–023; U-08 |
| GAP-07b | CRITICAL | Durable issuance records (`Prepared`/`Issued` `{id, actor, digest}`) carry **no effect payload and no cost**; "escrow survives crash" (R-DUR-05/REQ-DUR-013/014) and T1 "budget restored" (REQ-DUR-010) have **no durable source of truth**; reconciliation at T2–T4 holds only id+digest identity. The [30] log shape carried costs (and the v0.3 rule the full effect) — dropped in the frozen taxonomy. | R-PERSIST-03 vs L23863–23873/L8743; R-PLANNER-07; REQ-DUR-010/013/014 |
| GAP-08 | HIGH | Host-fault → machine outcome mapping: REQ-EFFECT-036 AMBIGUOUS; R-CORE-13 closes it "in the security direction" (closed enum, no debug text) but enumerates no variants; `HostFault` declared with 2 variants, 8 paths used (X-67 **BLOCKING**); `HostPolicyError` undeclared. | REQ-EFFECT-036; R-CORE-13; U-14/X-67; C-57 |
| GAP-09 | MEDIUM | `next_effect_id` recovery reconstruction and overflow unpinned; snapshot-window dependence for the counter. | R-PERSIST-04; R-RECOV-03 (no counter step); U-37 |
| GAP-10 | HIGH | Snapshot cadence vs T-points unfrozen: no rule prevents a snapshot between s12–s14 (or anywhere), and no T-row accounts for a snapshot containing s13 state with no journal record. T0/T1 postconditions ("no budget mutation", "budget restored") can be false under such a snapshot. | R-PERSIST-04/05 (no trigger); REQ-RECOV-003/004; REQ-DUR-010 |
| GAP-11 | HIGH | Actor continuation `K` + pending `E` are not durable in any record; T5 "resume continuation" (and T2→later `Completed` path) requires them; U-02 (machine-state encoding) blocking; snapshot timing again decisive. | REQ-RECOV-008; R-HOST-06; R-PERSIST-04; U-02; MOD-05 open items |
| GAP-12 | MEDIUM | Atomicity window s12–s16 is implicit (R-CORE-12 "transition atomicity") but not stated as a property of the 16-step sequence; no frozen statement that no scheduler yield/host-visible event can observe the half-committed state. | REQ-EFFECT-005 (order only); R-CORE-12 |
| GAP-13 | MEDIUM | Journal-causality fault name: `EffectJournalCorruption` (REQ-DUR-009) vs `RecoveryFault` (R-RECOV-05) vs `ReplayCorruption` (R-EFFECT-06) vs v0.3 `IsolationBreach` (REQ-EFFECT-040) — four names for related corruption outcomes; all subject to U-08. | REQ-DUR-009; R-RECOV-05; REQ-EFFECT-028/040; AMB-08 |
| GAP-14 | MEDIUM | Dangling proof-obligation IDs: resource-accounting audit's "frozen addendum" R-BUDGET-10…14 (atomicity, escrow normal form, duration, persistent capacity, tagged resources) appears **only** in `audit/resource-accounting-audit.md`; not in spec/01 (S-11 ends at R-BUDGET-09), not in mod/04, not in the registry — its "proof/test obligation" columns cite non-normative IDs; its five-path escrow normal form also **diverges** from R-BUDGET-09's three paths. | audit/resource-accounting-audit.md L75–88 vs spec/01 R-BUDGET-09 |
| GAP-15 | LOW/MEDIUM | No fsync sub-step/row for `EffectCompleted` (R-EFFECT-07/REQ-EFFECT-034 say "durable per S-18"; S-18 has no completion-sync step; where `Completed` syncs relative to charge/release/resume is unpinned — the [30] sketch appends to the *in-memory* event log and charges before any durability). | R-EFFECT-07, REQ-EFFECT-034, S-18, R-HOST-06 |
| GAP-16 | HIGH (historical, resolved in principle) | Authority-lattice durability at gate 5 (G): SEC-004's resurrection-of-revoked-capability attack is resolved by R-PERSIST-07 (durable arena + `CapabilityGranted/Derived/Revoked` events, post-recovery revalidation) — **normatively fixed**; byte encoding (U-02) and C-14/U-02 CapRef serialization still block evidence; M023 + `RECOVERY-REVOCATION-DURABLE` required. | SEC-004; R-PERSIST-07; U-02; M023 |
| GAP-17 | INFO | Gate numbering skew: resource-audit Op-16 (Gate 10 = ceiling, Gate 11 = deadline), [30] 14-gate, v0.3 3-gate, [54] 16-step — C-01's residual (no explicit gate↔step mapping) persists; the resource audit's numbers do not match the canonical form. | C-01; Op-16 |
| GAP-18 | MEDIUM | `Fault::TypeError` used on the G1 non-capability path (and throughout CEK) is outside the frozen R-CALC-06 enum; R-CORE-13 "closed declared fault surface" does not list it. Same defect class as X-69. | L21500–21525; R-CALC-06; R-CORE-13; U-08 |

---

## 6. Verification mapping (what proves the matrix)

| Obligation class | Tag / mutation / harness |
|---|---|
| Gate order + immutability | Track C short-circuit matrix (5 assertions per gate); **M010** (ID before auth); gate short-circuit matrix M5 |
| Evaluation order (G1–G3) | Track A; `CEK-CALL-ARGS-LTR`, `CEK-CALL-ARITY-PRECHECK` (call args); **no request-arg tag** (GAP-06); M001/M002/M003 |
| Capability validity (G5) | `CAP-REVOCATION-ANCESTOR`, M004, M021, M023, `RECOVERY-REVOCATION-DURABLE` |
| Exact authorization (G6) | Track B exactly-one-call mock kernel; R-KERN-04 brute-force test; M005 |
| Ceiling vs runtime dual gate (G7/G8/G9) | `BUDGET-ESCROW-CONSERVATION`, `BUDGET-CONSUMPTION-CONSERVATION`, M005/M007/M009; overflow boundary |
| Deadline (G10) | deadline gate test; deadline-exhaustion tests; **blocked by U-07** |
| Host policy (G11) | host policy tests; defense-in-depth review; U-14/X-67 |
| Durable-before-host (G13–G15) | `EFFECT-ISSUE-DURABLE-BEFORE-HOST`; `PanicHost` (R-REF-06) at **all** handles incl. supervisor (R-KERN-06); crate-DAG check (R-TRUST-05); M034 panic-free |
| Crash classification (all T) | crash harness T0–T6 (R-TEST-08, M10); `RECOVERY-ISSUED-INDETERMINATE`; negative corruption tests M015/M016; M008 (escrow) |
| Receipt integrity (post-issuance) | `EFFECT-RECEIPT-DIGEST-VALIDATION`, M017/M018/M019/M020/M029; replay property tests (R-HOST-03/05/06) |
| Overall acceptance | R-TEST-11: `Observe_P = Observe_R` ∧ `MutationKillRate = 100%` ∧ `Canonical(Recover_P(D)) = Canonical(Recover_R(D))` |

---

## 7. Bottom line

1. **The frozen gate order itself is sound and matches the requested order exactly**
   (with G13 = spec steps 13+14, the in-memory commit followed by the durable
   issuance transaction). Every denial point is specified to short-circuit with five
   assertions, and `HostInvoked ⇒ DurableIssued` is structurally realizable
   (R-DUR-01/02, R-CORE-06, R-TRUST-05 hinge).
2. **Four defect classes currently make the invariant unprovable as specified:**
   - **GAP-07 (CRITICAL):** live journal-failure (append/sync error) has no declared
     fault, no rollback, and no journal record kind to make R-CORE-12's atomicity
     realizable after s12/s13 mutations.
   - **GAP-07b (CRITICAL):** the durable issuance records carry no effect, no cost;
     escrow survival (R-DUR-05/013/014) and T1 budget restoration (REQ-DUR-010) have
     no durable source of truth; reconciliation holds only id+digest.
   - **GAP-05 (HIGH):** the deadline gate is specified weakly (`t ≤ W`) while the formal
     rules require `t + δ_t(req) ≤ W`; a host call may follow an over-deadline issuance.
   - **GAP-01 (MAJOR):** a second, contradictory 16-step sequence (host emit before
     `Issued`) still sits in normative text (spec/01 R-EFFECT-01).
3. **U-blockers at the gates themselves:** U-36 (lifetime timebase) blocks G5/G6;
   U-21 blocks G2–G4/G6 domain checks and `EffectDigest`; U-02 blocks G4/G5/G13–G15
   byte-level evidence; U-07 blocks G10; U-08/U-14/X-67 block every fault *name* on
   the error paths; U-01 blocks G8's `D` dimension; U-15/U-06 block reconciliation
   (P3), hence the T2–T4 end of the story.
4. **Snapshot timing is the hidden dependency of the whole crash story:** T0–T6
   classifications are durable-prefix-sound, but reconstruction (budget partitions,
   `next_effect_id`, actor continuation `K`, pending `E`) is not derivable from the
   frozen records and depends on unstated snapshot cadence (GAP-09/10/11).

*Matrix author-verified against: `Red-on-Rust.md` L38024–38045, L12177–12194,
L23857–24045, L35147–35176, L35210–35215; `spec/01` S-07, S-09…S-19;
`req/01-registry-part2/-part3/-part4/-part5`; `mod/03,04,05,06,07,08,09,10,11,12,17`;
`spec/03`, `spec/06` C-01/C-23/C-27/C-83, `spec/09` U-01/U-02/U-06/U-07/U-08/U-14/
U-15/U-21/U-36; `audit/resource-accounting-audit.md` Op-16…19;
`audit/authority-trust-external-effect-audit.md` SEC-001/004/010/011/012/020/022.*
