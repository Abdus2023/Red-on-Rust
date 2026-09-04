# M4 Implementation Review

**Operation:** M4 IMPLEMENTATION REVIEW & EVIDENCE RECONCILIATION  
**Do not implement M5. Do not redesign M4. Do not promote R-REG. Do not resolve OADs.**

Evidence labels: **FACT** | **DERIVED** | **DISCLOSED LIMITATION** | **PASS** | **FAIL** | **NOT APPLICABLE** | **AUTHORIZATION**

---

## 1. Review identity

| Field | Value | Class |
|---|---|---|
| Branch | `arena/01a06993-red-on-rust` | FACT |
| Review HEAD (pre-report) | `958790a8042b47705aba1e162cd608e93db757b1` | FACT |
| Working tree | clean at review start | FACT |
| Remote tip | matches HEAD at review start | FACT |
| Operation type | review only — no CEK / kernel semantic edits | AUTHORIZATION |

## 2. Reviewed commit

```text
958790a8042b47705aba1e162cd608e93db757b1
feat: implement M4 capability attenuation
```

**FACT** — sole M4 implementation tip under review (17 files; +2167/−102).

## 3. Authority sources

| Source | Use in this review |
|---|---|
| `final/01` R-ORDER-02, R-CAP-01…11, R-KERN-01…06, R-CALC-02, R-CEK-03, R-CORE-04, R-BUDGET-16 | Normative homes |
| `final/03` registry rows | SPECIFIED status spine |
| `final/04` M4 gate + `CAP-DERIVE-NO-AMPLIFICATION` / `CAP-REVOCATION-ANCESTOR` | Verification obligations |
| `final/05` GI-SEC-04/05/16/19 | Global invariants (by ID) |
| `final/08` evidence matrix | 184 × SPECIFIED ceiling; Theorems not PROVEN |
| `final/09` U-02/U-08/U-09/U-21/U-31 OPEN; U-36 RESOLVED | OAD dispositions |
| `dep/01-graph.md` / `dep/10-graph.json` | Edge authority |
| `mod/18-ownership-matrix.md` / `mod/03-capability.md` | MOD-03 ownership |
| `reg/requirements.json` | **184 × SPECIFIED** (computed) |
| `reg/status-transitions.json` | Promotion rules (not exercised) |
| `R-REG-VERDICT.md` | Evidence ceiling confirmation |
| `docs/bootstrap/M4-PREFLIGHT.md` @ `1e1eccb` | Authorized MAY/MUST NOT |
| `docs/bootstrap/M4-PROGRESS.md` @ `958790a` | Implementation claims under audit |
| `docs/bootstrap/M3-REVIEW.md` @ `ddc4138` | Prior baseline |

**Source-of-truth procedure applied:** claim → R-*/REQ-* → verification tag → OAD → dep/mod → code @ `958790a` → tests → classification. Tests and comments are **not** normative authority.

## 4. Scope table (review surface)

| Area | Review | Result |
|---|---|---|
| CapRef opacity | REQUIRED | PASS with disclosure (§6) |
| CapabilityKernel | REQUIRED | PASS |
| Derivation | REQUIRED | PASS |
| Constraint admissibility (R-CAP-10) | REQUIRED | PASS |
| Partial order / ≼ | REQUIRED | PASS |
| No-amplification | REQUIRED | PASS |
| Revocation cascade | REQUIRED | PASS |
| Validity / logical expiration | REQUIRED | PASS |
| `Expr::Attenuate` | REQUIRED | PASS |
| CEK Attenuate | REQUIRED | PASS |
| Lexical via Value/Let | REQUIRED | PASS |
| Reference algebra | REQUIRED | PASS with disclosure (§12) |
| Differential | REQUIRED | PASS |
| Property / mutation-intent | REQUIRED | PASS with coverage disclosure |
| Security boundary | REQUIRED | PASS |
| Determinism | REQUIRED | PASS |
| M1/M2/M3 regression | REQUIRED | PASS |
| Dependency graph | REQUIRED | PASS |
| R-REG ceiling | REQUIRED | PASS (unchanged) |
| U-08 / U-21 / U-31 / U-02 | DISCLOSE | OPEN / provisional preserved |
| REQ-CAP-024 / AMB-12 | DISCLOSE | registry AMBIGUOUS; R-CAP-10 governs |
| M5–M7 / OAD close / R-REG promote / PROVEN | OUT / FORBIDDEN | absent |

**Out of M4 (confirmed absent as production semantics):** Request CEK, HostExecutor, actors, WAL, durable grants, frame codecs, wall-clock authority.

---

## 5. Baseline gates

Commands @ review (toolchain `ror-stable` 1.88.0):

| Command | Result |
|---|---|
| `cargo fmt --check` | **PASS** |
| `cargo check --workspace` | **PASS** |
| `cargo test --workspace` | **PASS** (lib suites: core 27, differential 45, kernel 8, reference 7, runtime 42; others 0) |
| `cargo clippy --workspace --all-targets --all-features -- -D warnings` | **PASS** |

Repository-specific:

| Gate | Result | Evidence |
|---|---|---|
| Dependency direction | **PASS** | `cargo tree -p ror-reference` → `ror-core` only; kernel → core only; runtime → kernel present (REQUIRED) |
| Reference independence | **PASS** | Cargo.toml forbids kernel/runtime; tree confirms |
| Unsafe code | **PASS** | `#![forbid(unsafe_code)]`; no `unsafe` in M4 paths |
| Semantic leakage (effects/host) | **PASS** | no FS/net/clock/HostExecutor in M4 crates under audit |
| Canonical-state / R-REG | **PASS** | `reg/requirements.json` status map `{SPECIFIED: 184}` |

**No baseline regression STOP.**

---

## 6. CapRef review

**Authority:** R-KERN-01, REQ-KERN-001…003, R-CALC-01, GI-SEC-16 (`CapRef ≠ authority ownership`).

| Probe | Observation @ `958790a` | Class |
|---|---|---|
| Fields | `index` / `generation` **private** | PASS |
| Struct literal free form | unavailable outside crate | PASS |
| `From`/`Into`/`transmute` | none found | PASS |
| `CapRef → AuthorityNode` collapse | none; `AuthorityNode` private in kernel | PASS |
| Kernel mint | `CapabilityKernel::insert_node` → `from_kernel_parts` | PASS |
| Codec path | `CanonicalPayload::decode` → `from_kernel_parts` (R-CANON-12 kernel-mediated) | PASS |
| Bits ≠ authority | forged `from_kernel_parts(0,0)` fails `valid` (m4 test) | PASS |
| `pub fn from_kernel_parts` | **public** bit-pattern constructor | **DISCLOSED LIMITATION** |

**Interpretation:** R-KERN-01 text requires no public constructor from arbitrary integers. The shipped API exposes `from_kernel_parts` for kernel + codec + fixtures. **Semantic safety** is preserved because authority is arena-gated (`valid` / `derive`), not bit-gated — matching preflight and GI-SEC-16. This is **not** classified SECURITY BLOCKER (bits do not exercise authority), but it is a **residual API-opacity gap** vs the strictest reading of “no public constructor.”

**Invariant hold:** `CapRef ≠ AuthorityNode`; evaluator holds `Value::Capability(CapRef)` only.

---

## 7. CapabilityKernel review

**Authority:** R-KERN-02/03, MOD-03, REQ-KERN-004…008.

| API | Present | Notes |
|---|---|---|
| `grant_root` / `grant_root_always` | yes | thin R-KERN-06; not durable |
| `derive` | yes | Valid ∧ Admissible ⇒ meet + lineage |
| `revoke` | yes | Live=false + revocation_set |
| `valid` / `valid_result` | yes | R-CAP-07 lazy ancestors + Lifetime |
| `authorize_algebra` | yes | pure R-CAP-06 + optional possession; **not** Request CEK |
| `authority_snapshot` | yes | property/test inspection — **not** evaluator path |
| `AuthorityNode` | `struct` private | R-KERN-03 |

No alternate authority mint path in runtime CEK beyond kernel `derive`/`grant_*`.

---

## 8. Derivation / no-amplification review

**Authority:** R-CAP-05, R-CORE-04, GI-SEC-04, `CAP-DERIVE-NO-AMPLIFICATION`, M006.

Trace (production):

```text
Valid(parent,t) → admissible_constraint_wrt_parent(C, A)
  → A.derive_authority(C)  // meet on O_A ∩ O_C
  → insert child with parent link
```

| Check | Result |
|---|---|
| Meet construction ⇒ residual ≼ parent | PASS (by definition + `debug_assert` + tests) |
| Extra op in C | InvalidConstraint | PASS |
| Resource ceiling > parent | InvalidConstraint | PASS |
| Empty C | InvalidConstraint | PASS |
| Revoked parent | CapabilityRevoked | PASS |
| Atomic evaluator call | single `kernel.derive` | PASS (REQ-CAP-025) |
| ⊤-default | absent | PASS (M030 intent) |

Tests: kernel unit (8), differential m4 amplification/mutation-intent, property pairs.

**No SECURITY BLOCKER** (no successful amplification observed).

---

## 9. Constraint / partial-order review

**Authority:** R-CAP-03/04/10, REQ-CAP-007/009/012.

| Item | Production | Reference |
|---|---|---|
| `Authority::leq` | R-CAP-03 | — |
| `RefAuthority::leq` | — | independent |
| Meet | `derive_authority` | `derive_meet` (independent) |
| Constraint ≠ Authority | distinct types | same shells via core |
| Admissibility | R-CAP-10 runtime | same **core helper** (see §12 disclosure) |

U-21/U-31 field sets remain **provisional** test-domain enums (`Op`, `Scope`, …) — OAD not closed.

---

## 10. Revocation / validity review

**Authority:** R-CAP-07/11, REQ-CAP-013…015, `CAP-REVOCATION-ANCESTOR`, M004; R-CAP-09 (no wall-clock).

| Property | Evidence |
|---|---|
| Revoke sets Live=false | `revoke` + set membership |
| Lazy ancestor walk | `valid_result` while-loop on `parent` |
| Cascade child/grandchild | kernel + m4 `revoke_cascade_both_sides` |
| Sibling preserved | same fixtures |
| Lifetime half-open `[start,end)` | `Lifetime::contains`; expiration tests |
| Logical time only | `LogicalTime`; no `SystemTime`/`Instant` in M4 paths |
| No WAL/persistence | absent |

**PASS.**

---

## 11. CEK Attenuate review

**Authority:** R-CALC-02, REQ-CAP-022/023, R-CEK-01/02, M4-PREFLIGHT §8 (Expr wins; no invented body/name).

| Check | Result |
|---|---|
| AST `{ cap, constraint }` | FACT — matches R-CALC-02 |
| No `body`/`name` on Expr | PASS |
| Order: cap → constraint → derive | `AttenuateCap` then `AttenuateConstraint` | PASS |
| Type errors non-cap / non-constraint | PASS (differential) |
| Success → `Value::Capability(child)` value-return | PASS |
| Denied → provisional faults | `CapabilityRevoked` / `InvalidConstraint` | PASS |
| Lexical composition | `let_(…, attenuate(…), var)` | PASS |
| Frames in-memory only | U-02 OPEN preserved | PASS |
| R-CEK-03 binder frame unused | intentional per preflight | DISCLOSED (not a defect) |
| Request/Spawn still unsupported | PASS |

**M3 arity-order gate:** untouched; runtime arity tests still green (42 runtime tests PASS).

---

## 12. Reference independence review

**Authority:** R-SCOPE-04, R-REF-02, REQ-REF-023/024, GI-SEC-19, dep FORBIDDEN edges.

| Check | Result |
|---|---|
| `ror-reference → ror-kernel` | **absent** (Cargo + tree) |
| `ror-reference → ror-runtime` | **absent** |
| Independent store | `RefCapabilityStore` / `RefAuthority` | PASS |
| Independent meet/leq algorithms | `derive_meet` / `leq` authored in reference | PASS |
| Shared `ror-core` shells | Op/Scope/Constraint/LogicalTime — **ALLOWED** | PASS |
| Shared `admissible_constraint_wrt_parent` | both call **core** helper | **DISCLOSED LIMITATION** |

**Disclosure detail:** Production and reference do **not** share kernel/runtime transition code. They **do** share the R-CAP-10 admissibility **predicate function** living in `ror-core` (domain vocabulary crate). Meet/order/arena logic remains dual-implemented. This is weaker than “zero shared algebra helpers” but does **not** violate FORBIDDEN crate edges or import production kernel. Classified as evidence/independence **depth** limitation, not REFERENCE INDEPENDENCE FAILURE STOP.

`ror-differential → ror-kernel` is a **verification observation** edge (ALLOWED; black-box SUT), not a semantic dependency of reference.

---

## 13. Differential review

**Module:** `crates/ror-differential/src/m4.rs` (14 tests @ review).

Pipeline:

```text
evaluate_with_kernel(P)  vs  evaluate_with_store(R)
        → Observation { Halted | Fault }
```

Covered: success, revoked deny, invalid constraint, amplify-op deny, Let composition, type error, algebra no-amp pairs, cascade, expiration, CapRef bits, M2/M3 spot regression, mutation-intent kills.

**PASS** — no P/R divergence under seeded arenas. Normalization is identity on machine `Value`/`Fault` (no semantic hiding).

---

## 14. Property / mutation-intent review

| Intent | Kill mechanism | Status |
|---|---|---|
| Amplification (M006) | residual scope/resources; extra op reject | KILLED |
| Skip admissibility (M030) | empty/over-ceiling → InvalidConstraint | KILLED |
| Accept revoked (M004) | ¬Valid; derive fails | KILLED |
| CapRef public bits as authority | ¬valid forged | KILLED |
| Cascade break | grandchild invalid / sibling live | KILLED |
| Invert ≼ | property `derived.leq(parent)` | covered |
| Couple ref→kernel | Cargo/tree | KILLED structurally |

**DISCLOSE — COVERAGE GAP (non-blocking):** no separate mutation-injection harness (M9); coverage is **intent tests**, not MutationKillRate=100%. Theorems 1–3 remain SPECIFIED ≠ PROVEN (`final/08`).

---

## 15. Security review

| Invariant | Hold? |
|---|---|
| GI-SEC-04 derive ≼ | yes |
| GI-SEC-05 revocation lineage | yes |
| GI-SEC-16 CapRef ≠ ownership | yes (arena gate) |
| GI-SEC-19 reference independence | yes with §12 disclosure |
| Untrusted expr ↛ host effect | Request unsupported |
| No FS/net/process/WAL/clock in M4 | yes |
| Evaluator authority inspection | AuthorityNode private; CEK uses CapRef only |

**PASS** — no SECURITY BLOCKER.

---

## 16. Determinism review

| Probe | Result |
|---|---|
| `SystemTime` / `Instant` / `thread_rng` in M4 paths | none |
| Authority maps | `BTreeMap` / `BTreeSet` only |
| CapRef allocation | deterministic index/gen sequence |
| Logical time | explicit parameter |

**PASS.**

---

## 17. M1 / M2 / M3 regression

| Suite | Result |
|---|---|
| M1 core (canonical + digest + machine isolation) | 27 PASS |
| M2/M3 differential | included in 45 differential PASS |
| M3 runtime CEK (arity/LTR/closure) | 42 PASS |
| M4 does not alter M3 arity-before-args | confirmed (code path + tests) |
| U-09 machine vs data Value split | preserved |
| R-CANON-12 capability-in-data ban | preserved (codec tests) |

**PASS** — no M1/M2/M3 semantic regression.

---

## 18. Dependency review

| Edge | Classification | Hold? |
|---|---|---|
| `ror-kernel → ror-core` | REQUIRED | yes |
| `ror-runtime → ror-kernel` | REQUIRED (MOD-05→03) | yes |
| `ror-reference → ror-core` | REQUIRED | yes |
| `ror-differential → {runtime,reference,kernel,core}` | VERIFICATION | yes |
| `ror-reference → ror-kernel` | **FORBIDDEN** | absent |
| `ror-reference → ror-runtime` | **FORBIDDEN** | absent |
| `ror-kernel → ror-runtime` | **FORBIDDEN** | absent |
| `ror-core → ror-kernel` | **FORBIDDEN** | absent |

**No FORBIDDEN or UNCLASSIFIED required edge. PASS.**

Ownership: MOD-03 algebra+kernel in `ror-kernel`; domain shells in `ror-core` — consistent with `mod/18`.

---

## 19. OAD reconciliation

| OAD | Pre-M4 | Post-M4 review | Closed? |
|---|---|---|---|
| U-02 | OPEN | OPEN (in-memory frames) | **No** |
| U-08 | OPEN | OPEN (provisional fault labels) | **No** |
| U-09 | OPEN | OPEN (`Value::Constraint` shell disclosed) | **No** |
| U-21 | OPEN | OPEN (provisional Op/Scope/…) | **No** |
| U-31 | OPEN | OPEN (provisional fields; arena in kernel) | **No** |
| U-36 | RESOLVED | used (R-CAP-11) | n/a |
| AMB-12 / REQ-CAP-024 | AMBIGUOUS in `req/` | still AMBIGUOUS; **R-CAP-10 governs** | **No** registry edit |

**No silent OAD resolution. PASS.**

---

## 20. R-REG reconciliation

| Check | Result |
|---|---|
| `reg/requirements.json` statuses | **184 × SPECIFIED** (computed this review) |
| `final/08` matrix | all R-* SPECIFIED; CAP theorems not PROVEN |
| Status transitions applied | **none** |
| Review claims VERIFIED/PROVEN | **none** |

```text
R-REG = 184 × SPECIFIED
tests pass ≠ semantic verification ≠ proof
```

**PASS.**

---

## 21. Disclosed limitations

1. **`CapRef::from_kernel_parts` is public** — strictest R-KERN-01 constructor reading not met; bits still ≠ authority (tested).
2. **Shared core admissibility helper** — P and R both call `ror_core::admissible_constraint_wrt_parent`; meet/arena remain dual.
3. **`authority_snapshot` public** — test/property inspection API; not CEK path.
4. **U-21/U-31 provisional representations** — not frozen host ontology.
5. **U-08 provisional faults** — `CapabilityRevoked` / `InvalidConstraint` evaluator-local.
6. **U-02 frames** — no codecs; R-CEK-03 `{name,body,env}` not used (preflight-authorized).
7. **R-KERN-04/05/06 thin only** — no live actors, no durable grant/WAL.
8. **R-CAP-06 Request path** — algebra fn only; effect CEK = M5.
9. **R-CAP-10 compiler half** — deferred.
10. **REQ-CAP-024 registry lag** — AMBIGUOUS row remains; R-CAP-10 is frozen law.
11. **Mutation coverage** — intent tests, not M9 kill-rate.
12. **Theorems 1–3** — TESTED properties ≠ PROVEN.
13. **Evidence ceiling** — IMPLEMENTED/TESTED repository evidence only; R-REG unpromoted.
14. **M4 semantic verification** — **NOT CLAIMED**.

---

## 22. Corrections

None affecting M4 semantics. This review adds **documentation only** (`M4-REVIEW.md`).

No code, OAD, R-REG, or dependency edits.

---

## 23. Final classification

```text
M4 IMPLEMENTATION = ACCEPTED WITH DISCLOSED EVIDENCE LIMITATIONS
```

**Rationale:** Canonical M4 Capability/Attenuation surface at `958790a` conforms to R-ORDER-02 / R-CAP / R-KERN spine and M4-PREFLIGHT boundary: CapRef opacity (with constructor disclosure), kernel derive/revoke/valid, R-CAP-10 admissibility, no-amplification, cascade, logical expiration, Attenuate CEK on frozen AST, independent reference store (with shared-core-admissibility disclosure), differential/property/mutation-intent evidence, pure security/determinism, green gates, M1–M3 regression hold. Residual gaps are evidence depth, provisional OADs, and API strictness — not conformance failures.

- Not unqualified `ACCEPTED` (disclosures material to opacity API, independence depth, evidence ceiling).  
- Not `BLOCKED` (no security/cascade/amp/forbidden-dep/regression failure).  

```text
M4 semantic verification = NOT CLAIMED
M4 formal verification / PROVEN = NOT CLAIMED
```

---

## 24. Commit decision

Review conjuncts hold: implementation reviewed at exact `958790a`; gates green; scope hold; OADs untouched; R-REG untouched; report complete; classification accepted-with-limitations; commit = review artifact only.

```text
COMMIT = PERMITTED
```

---

## 25. Next authorized operation

```text
NEXT = M5 PREFLIGHT
```

**M5 IMPLEMENTATION = NOT AUTHORIZED** by this review. Effects/Request require a separate M5 preflight.

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
M4 implementation          ACCEPTED WITH DISCLOSED EVIDENCE LIMITATIONS
M4 semantic verification   NOT CLAIMED
R-REG                      184 × SPECIFIED
M5                         NOT STARTED
M6                         NOT STARTED
M7                         NOT STARTED
```

---

*End of M4 IMPLEMENTATION REVIEW. Implementation commit remains `958790a`.*
