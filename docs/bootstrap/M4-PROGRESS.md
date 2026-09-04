# M4 Progress

**Operation type:** M4 IMPLEMENTATION  
**Preflight:** `1e1eccb` — GREEN WITH DISCLOSED LIMITATIONS  
**Classification:** `COMPLETE WITH DISCLOSED EVIDENCE LIMITATIONS`

Evidence labels: **FACT** | **DERIVED** | **DISCLOSED LIMITATION** | **IMPLEMENTED** | **TESTED**

---

## 1. Implementation commit

Recorded at completion commit (this document lands with the implementation).  
Ancestry: `1e1eccb` (M4 preflight) → **this commit**.

## 2. Final implementation commit

See git HEAD after `feat: implement M4 capability attenuation`.

## 3. Canonical M4 scope

| Source | Scope |
|---|---|
| R-ORDER-02 | Capability / Attenuation — CapRef opacity, derive, partial order, revocation cascade |
| final/04 | `CAP-DERIVE-NO-AMPLIFICATION` + revocation/expiration/lexical binding + independent reference algebra |

**Not implemented (correctly deferred):** Request/effects (M5), actors (M6), WAL/durable grants (M7), compiler admissibility suite, U-02 codecs, OAD closes, R-REG promotion.

## 4. Requirements / atomic obligations implemented

| ID | Status |
|---|---|
| R-CAP-01…05, R-CAP-07…11 | IMPLEMENTED (algebra + Valid/Lifetime) |
| R-CAP-06 | Algebra pure `authorized` fn TESTED; Request CEK DEFERRED (M5) |
| R-CAP-10 | Runtime admissibility IMPLEMENTED; compiler half DEFERRED |
| R-KERN-01…03 | IMPLEMENTED |
| R-KERN-04/05 | Thin `CapabilityContext` + optional holder in `authorize_algebra` |
| R-KERN-06 | Thin `grant_root` only; durable WAL DEFERRED |
| REQ-CAP-012…018, 022, 023, 025, 026 | IMPLEMENTED / TESTED |
| REQ-CAP-024 | Registry still AMBIGUOUS; **R-CAP-10 frozen law governs** |
| REQ-KERN-001…009 | IMPLEMENTED (authorize effect path thin) |
| REQ-REF-023/024 | IMPLEMENTED in `ror-reference` |
| R-CALC-02 Attenuate `{cap, constraint}` | CEK IMPLEMENTED (no invented body/name) |
| R-CORE-04 / CAP-DERIVE-NO-AMPLIFICATION | TESTED |
| CAP-REVOCATION-ANCESTOR | TESTED |

## 5. CapabilityKernel implementation

**Crate:** `ror-kernel`  
**API:** `grant_root` / `grant_root_always`, `derive`, `revoke`, `valid` / `valid_result`, `authority_snapshot` (test/property), `authorize_algebra`, `parent_of`.  
**Storage:** generational slot vec + `BTreeSet` revocation set; `AuthorityNode` private.  
**Deps:** `ror-core` only.

## 6. CapRef opacity

- Fields `index` / `generation` **private** (R-KERN-01).
- Constructors: `CapRef::from_kernel_parts` (kernel + kernel-mediated codec only).
- Accessors: `index()`, `generation()` for identity/equality/codec — **not** authority inspection.
- Forged bits do not validate in an empty kernel (TESTED).

## 7. Derivation

`CapabilityKernel::derive(parent, constraint, t)`:

1. `Valid(parent, t)`
2. `AdmissibleConstraint` wrt parent (R-CAP-10)
3. Meet authority on `O_A ∩ O_C`
4. Insert child with parent lineage link  
Atomic from evaluator POV (single call — REQ-CAP-025).

## 8. No-amplification

- Meet construction ⇒ `derived ≼ parent` by definition (R-CAP-05).
- Property tests + differential algebra pairs.
- Amplification attempts (extra op, higher resource ceiling) ⇒ `InvalidConstraint`.

## 9. Constraint admissibility

R-CAP-10 runtime:

- Nonempty op set
- Ops ⊆ parent ops
- Scope ⊆ parent scope
- Params ≼ parent params
- Resources ≼ parent resources
- Lifetime satisfiable and intersects parent  

Empty / foreign-op / over-ceiling constraints fault. **⊤-default forbidden** (M030 intent).

## 10. Partial order

`Authority::leq` / `RefAuthority::leq` implement R-CAP-03 (op ⊆ + per-op S/Q/R/T).  
Deterministic `BTreeMap` keys. Reflexivity and derive⇒order covered by tests.

## 11. Revocation

`revoke` sets `live=false` and records revocation set membership (REQ-CAP-014).

## 12. Revocation cascade

Lazy ancestor walk in `Valid` (REQ-CAP-015). Distinguishing fixture:

```text
root
 ├── child ──► grandchild   (invalid after revoke(child))
 └── sibling               (still valid)
```

## 13. Validity

`Valid(c,t) ⇔ Live(c) ∧ t ∈ Lifetime(c) ∧ ∀ ancestors Live(a)` (R-CAP-07).  
Lifetime half-open `[start,end)` logical time only (R-CAP-11). No wall-clock.

## 14. Attenuate CEK

**Expr (R-CALC-02):** `{ cap, constraint }` — no body/name.  
**Order:** eval `cap` → require `Value::Capability` → eval `constraint` → require `Value::Constraint` → `kernel.derive` → value-return `Value::Capability(child)`.  
**Frames (in-memory, U-02):** `AttenuateCap`, `AttenuateConstraint`.  
**Lexical binding:** composition via existing Let/Lambda (preflight §8).  
**Denied:** `CapabilityRevoked` or `InvalidConstraint` (provisional labels).  
**δ_t:** 0 (R-BUDGET-16; no budget debit in M4 harness).

## 15. Fault handling

Evaluator-local additions (U-08 **OPEN**):

- `Fault::CapabilityRevoked`
- `Fault::InvalidConstraint`

Not a claim that R-CALC-06 / R-CORE-13 is closed.

## 16. Reference algebra

`ror-reference::cap_algebra`:

- `RefAuthority`, `RefOpAuthority`, `RefCapabilityStore`
- Independent derive / valid / revoke / leq  
**Forbidden deps absent:** no `ror-kernel`, no `ror-runtime`.

## 17. Differential testing

`ror-differential::m4`: success, revoked deny, invalid constraint, amplify deny, Let composition, type error, algebra properties, cascade, expiration, M2/M3 regression spot-check.

## 18. Property testing

- derive ⇒ ≼ parent (multiple target/unit pairs)
- constraint monotonicity (kernel unit test)
- lifetime half-open
- P≡R on seeded arenas

## 19. Mutation testing (intent / kill)

| Intent | Kill evidence |
|---|---|
| M006 amplify | residual scope/resources strict; extra op rejected |
| M030 ⊤-default | empty/inadmissible ⇒ InvalidConstraint, no CapRef |
| M004 accept revoked | revoke ⇒ ¬Valid; derive fails |
| CapRef public mint bypass | forged bits ¬Valid |
| Reference coupled to production | Cargo independence + separate store types |

Not M9 100% kill-rate claim.

## 20. Security audit

| Invariant | Status |
|---|---|
| derive ≼ parent | enforced |
| CapRef ⇏ AuthorityInspection | private node; evaluator holds CapRef only |
| No wall-clock | LogicalTime only |
| No effects/host | Request still unsupported |
| Bits ≠ authority | TESTED |
| `#![forbid(unsafe_code)]` | preserved |

## 21. Determinism audit

- `BTreeMap` / `BTreeSet` only for semantic maps/sets
- No HashMap iteration dependence for decisions
- No wall-clock / RNG / addresses in semantics
- Seeded grant order ⇒ equal CapRef indices across P/R

## 22. Dependency audit

| Edge | Class |
|---|---|
| `ror-kernel → ror-core` | REQUIRED |
| `ror-runtime → ror-kernel` | REQUIRED (Attenuate) |
| `ror-reference → ror-core` only | REQUIRED |
| `ror-differential → ror-kernel` | ALLOWED (harness observation) |
| `ror-reference → ror-kernel` | FORBIDDEN — absent |
| `ror-kernel → ror-runtime` | FORBIDDEN — absent |

## 23. M3 regression

All prior M2/M3 CEK, reference, and differential tests green. Lambda/Call/arity/LTR/closure unchanged in semantics.

## 24. Repository gates

| Gate | Result |
|---|---|
| `cargo fmt --check` | PASS |
| `cargo check --workspace` | PASS |
| `cargo test --workspace` | PASS |
| `cargo clippy … -D warnings` | PASS |
| unsafe forbid | PASS |
| reference independence | PASS |

## 25. OAD status

| OAD | Status |
|---|---|
| U-02 | **OPEN** (frames in-memory only) |
| U-08 | **OPEN** (provisional fault labels) |
| U-09 | **OPEN** (domain split preserved; Constraint on machine Value is M4 shell) |
| U-21 | **OPEN** — provisional Op/Scope/Params/Resource reps |
| U-31 | **OPEN** — provisional Authority/Constraint field sets; arena in kernel |
| U-36 | RESOLVED (R-CAP-11) — used |

No OAD silently closed.

## 26. Disclosed limitations

1. REQ-CAP-024 / AMB-12 registry still AMBIGUOUS; R-CAP-10 governs.
2. U-21/U-31 representations provisional (test-domain enums).
3. Fault labels provisional (U-08).
4. R-KERN-06 durable grant / R-PERSIST-07 not implemented.
5. R-KERN-04 live multi-actor possession not implemented.
6. R-CAP-06 effect Request path not implemented (algebra only).
7. Compiler AdmissibleConstraint half deferred.
8. `Value::Constraint` is an evaluator shell for R-CALC-02 `constraint: Box<Expr>`; not a claim U-09 closed.
9. R-CEK-03 frame `{name,body,env}` not used; preflight authorized Call-style frames + Let composition.
10. Theorems 1–3 TESTED ≠ PROVEN.
11. R-REG remains 184 × SPECIFIED — no promotion.

## 27. Evidence classification

```text
IMPLEMENTED + TESTED  (repository evidence)
VERIFIED / PROVEN     NOT CLAIMED
R-REG                 184 × SPECIFIED
M4 semantic verification  NOT CLAIMED
```

## 28. Semantic matrix

| Semantic operation | Canonical authority | Production | Reference | Differential | Property | Mutation |
|---|---|---|---|---|---|---|
| derive | R-CAP-05, REQ-CAP-012 | IMPLEMENTED | IMPLEMENTED | TESTED | TESTED | TESTED |
| admissibility | R-CAP-10 | IMPLEMENTED | IMPLEMENTED | TESTED | TESTED | TESTED |
| ≼ | R-CAP-03 | IMPLEMENTED | IMPLEMENTED | TESTED | TESTED | TESTED |
| revoke | R-CAP-07, REQ-CAP-014 | IMPLEMENTED | IMPLEMENTED | TESTED | — | TESTED |
| valid | R-CAP-07/11 | IMPLEMENTED | IMPLEMENTED | TESTED | TESTED | TESTED |
| Attenuate | REQ-CAP-022/023, R-CALC-02 | IMPLEMENTED | IMPLEMENTED | TESTED | — | TESTED |
| Authorized (algebra) | R-CAP-06 | IMPLEMENTED (fn) | N/A algebra via Valid | — | unit | — |
| Request CEK | M5 | NOT IMPLEMENTED | NOT IMPLEMENTED | DEFERRED | DEFERRED | DEFERRED |

## 29. Final implementation state

```text
M4 IMPLEMENTATION = COMPLETE WITH DISCLOSED EVIDENCE LIMITATIONS
```

## 30. Next authorized operation

```text
NEXT = M4 IMPLEMENTATION REVIEW
```

Do **not** begin M5.

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
M4 implementation          COMPLETE WITH DISCLOSED EVIDENCE LIMITATIONS
R-REG                      184 × SPECIFIED
M5                         NOT STARTED
M6                         NOT STARTED
M7                         NOT STARTED
```
