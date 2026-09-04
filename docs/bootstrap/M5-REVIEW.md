# M5 Implementation Review

**Operation type:** M5 IMPLEMENTATION REVIEW (evidence reconciliation + security-boundary audit).  
**Primary classification:** **ACCEPTED WITH DISCLOSED EVIDENCE LIMITATIONS**  
**Next authorized operation:** **M6 PREFLIGHT** (do **not** implement M6 in this operation).

Evidence labels: **FACT** | **DERIVED** | **DISCLOSED LIMITATION** | **TEST** | **PASS** | **PASS WITH LIMITATION**

---

## 1. Review identity

| Item | Value | Class |
|---|---|---|
| Branch | `arena/01a06993-red-on-rust` | FACT |
| HEAD at review start | `f1785629d745da176b30de8e5dc5c7c9562701e1` | FACT |
| Subject | `feat: implement M5 request effects and host boundary` | FACT |
| Working tree | clean (pre-review-report) | FACT |
| Toolchain | `ror-stable` rustc **1.88.0** | FACT |
| Reviewer posture | Review only — no M5 reimplementation; no M6/M7; no OAD/R-REG mutation | FACT |

Identity gate **PASS**.

---

## 2. Reviewed commit

| Item | Value | Class |
|---|---|---|
| M5 implementation | **`f178562`** | FACT |
| M5 preflight | **`b64fb9a`** (`docs/bootstrap/M5-PREFLIGHT.md`) | FACT |
| M4 review | **`96ce46e`** | FACT |
| Transition | `b64fb9a` → `f178562` (15 files, +3170/−32) | FACT |
| Progress artifact | `docs/bootstrap/M5-PROGRESS.md` @ `f178562` | FACT |

No other tip was reviewed as M5. **PASS**.

---

## 3. Authority sources

| Source | Role |
|---|---|
| `final/01` | Normative homes: **R-CORE-14**, R-CORE-06, R-EFFECT-*, R-DUR-*, R-HOST-*, R-CALC-04/05, R-CEK-03, R-CANON-09, R-TRUST-05, R-ORDER-02 |
| `final/03` | Requirement registry rows (SPECIFIED) |
| `final/04` | Verification tags: `EFFECT-ISSUE-DURABLE-BEFORE-HOST`, `REQUEST-ARGS-LTR`, `REQUEST-NON-CAP-SHORT-CIRCUIT`; M5 milestone row |
| `final/05` | **GI-SEC-07** `HostInvoked(E) ⇒ DurableIssued(E)` (definitional home R-DUR-01) |
| `final/08` | Evidence ceiling 184 × SPECIFIED |
| `final/09` | OADs: U-39…U-44 RESOLVED; U-02/U-08/U-09/U-21/U-31 OPEN |
| `dep/10-graph.json` | Dependency integrity / findings |
| `mod/18-ownership-matrix.md` | MOD-08 EFFECT, MOD-09 HOST, MOD-11 PERSISTENCE ownership + crate edges |
| `reg/requirements.json` / `status-transitions.json` / `R-REG-VERDICT.md` | R-REG ladder |
| `docs/bootstrap/M5-PREFLIGHT.md` / `M5-PROGRESS.md` / `M4-REVIEW.md` | Prior boundary + disclosures |

**Source-of-truth procedure:** requirement → verification tag → invariant → OAD → ownership → dep graph → implementation. Code/tests are **not** authority.

**Governing protocol (FACT — R-CORE-14 SUPERSEDES historical R-EFFECT-01 host-before-Issued listing):**

```text
(1) eval capability → (2) eval target → (3) args LTR → (4) Effect+Digest
→ (5) Valid → (6) Authorize → (7) ceiling → (8) budget → (9) reservation
→ (10) deadline t+δ_t(req)≤W → (11) host policy → (12) EffectId
→ (13) commit issue/reserve → (14) durable issuance → (15) Pending
→ (16) host
HostInvoked(E) ⇒ DurableIssued(E)   # no ordering exception
```

---

## 4. M5 scope

| Surface | Review status | Verdict |
|---|---|---|
| `Expr::Request` | REQUIRED | **PASS** (R-CALC-02 frozen AST) |
| Request CEK frames | REQUIRED | **PASS WITH LIMITATION** (extra `RequestOperation`; see §9) |
| Argument ordering LTR | REQUIRED | **PASS** |
| Non-cap short-circuit | REQUIRED | **PASS** |
| Capability authorization | REQUIRED | **PASS** (M4 algebra consumed) |
| Effect / EffectCost / Digest / Id | REQUIRED | **PASS WITH LIMITATION** (U-21 provisional bytes) |
| Effect gates 5–16 | REQUIRED | **PASS WITH LIMITATION** (thin ceiling/Pending/completion) |
| Prepared / Issued / issuance API | REQUIRED | **PASS WITH LIMITATION** (MemoryJournal test double) |
| HostExecutor / HostPolicy / adapters | REQUIRED | **PASS** |
| Receipts / completion | REQUIRED | **PASS WITH LIMITATION** (thin completion journal) |
| Failure semantics | REQUIRED | **PASS WITH LIMITATION** (U-08 provisional labels) |
| Reference + differential + mutation | REQUIRED | **PASS** |
| M1–M4 regression | REQUIRED | **PASS** |
| Actors / scheduler / full WAL / snapshots / T0–T6 recovery | FORBIDDEN | **ABSENT** (comments only) |
| OAD close / R-REG promotion / PROVEN | FORBIDDEN | **ABSENT** |

Canonical M5 name (R-ORDER-02): **Effects** — 16-step request, issuance, receipts, host mock. **PASS**.

---

## 5. Baseline gates

Reproduced this review @ `f178562` / `ror-stable` 1.88.0:

| Command | Result | Class |
|---|---|---|
| `cargo fmt --check` | **PASS** (exit 0) | FACT |
| `cargo check --workspace` | **PASS** | FACT |
| `cargo test --workspace` | **PASS** — **160** passed, **0** failed | FACT |
| `cargo clippy --workspace --all-targets --all-features -- -D warnings` | **PASS** | FACT |
| `#![forbid(unsafe_code)]` all crates; no `unsafe` bodies | **PASS** | FACT |
| No crates.io deps (path-only workspace) | **PASS** | FACT |
| Reference independence (`use ror_{runtime,kernel,host,persistence}` absent in `ror-reference`) | **PASS** | FACT |
| R-REG | **184 × SPECIFIED**; `status-transitions.transitions` length **0** | FACT |

Progress claim of 160 tests / green gates **confirmed**. **PASS**.

Package spot-checks: `ror-differential` 57 (incl. m2–m5); `ror-runtime` 51; `ror-core` 30; `ror-kernel` 8; `ror-reference` 9; `ror-host` 3; `ror-persistence` 2 — all green.

---

## 6. Diff classification (`b64fb9a..f178562`)

| Path | Class |
|---|---|
| `crates/ror-core/src/effect.rs` (new) | **M5-required** domain types |
| `crates/ror-core/src/{lib,machine}.rs` | **M5-required** exports / Fault / sugar::request |
| `crates/ror-runtime/src/{cek,effects,lib}.rs` | **M5-required** Request CEK + gate pipeline |
| `crates/ror-persistence/src/lib.rs` | **M5-required** issuance journal API |
| `crates/ror-host/src/lib.rs` | **M5-required** host adapters |
| `crates/ror-reference/src/{effect_model,pure_cek,lib}.rs` | **M5-required** independent model |
| `crates/ror-differential/src/m5.rs` + lib/Cargo | **test-only** / harness |
| `docs/bootstrap/M5-PROGRESS.md` | **documentation** |

No unexplained M6 actor scheduler, no WAL recovery engine, no snapshot protocol implementation. T0–T6 appears only as “not M7” documentation. **PASS**.

---

## 7. Core effect types

| Type | Ownership | Fields / invariants | Verdict |
|---|---|---|---|
| `Effect` | MOD-01 shells / MOD-08 use | `CapRef, Op, Target, Params, EffectCost` (R-CALC-04) | **PASS** (U-21 provisional Op/Target/Params) |
| `EffectCost` | R-CALC-05 | `issue, complete_max, reserve` | **PASS** |
| `EffectDigest` | R-CANON-09 | `SHA-256(canonical_bytes(effect))` via in-tree `digest.rs` | **PASS WITH LIMITATION** — bytes are fixed BE layout, not full 15A `CanonicalEncode(Effect)` envelope (**DISCLOSE** U-21 / L-M5-ENC) |
| `EffectId` / `EffectIdAlloc` | R-EFFECT-03 | monotonic `u64`; no wall-clock/RNG | **PASS** |
| `EffectRequest` | host-facing | id, actor, digest, effect_bytes, cost, effect — **no Authority** | **PASS** |
| `IssuanceRecord::{Prepared,Issued,Completed}` | R-DUR-06 | carries effect_bytes + cost triple | **PASS** |
| `EffectReceipt` / `ReceiptValue` | R-EFFECT-06/08 | id+digest; data-only variants | **PASS WITH LIMITATION** — admission by construction of enum; no recursive `contains_capability` over nested machine Values beyond ReceiptValue surface |

Constructor visibility: domain constructors public for tests/fixtures; authority mint remains kernel-side. CapRef forgery still possible at type level (`from_kernel_parts` public — **M4 carry**) but Valid+possession gates bind. **PASS WITH LIMITATION**.

No second semantic serializer (JSON/Debug-as-identity) found on the effect path. **PASS**.

---

## 8. Request CEK

| Check | Evidence | Verdict |
|---|---|---|
| Frozen AST `Request { capability, operation, target, params }` | `machine.rs` | **PASS** |
| Enter: evaluate capability first | `enter_request` → `RequestCapability` frame | **PASS** |
| Non-cap → `TypeError` before target/params | `resume_request_capability` | **PASS** |
| Params one-per-step LTR | `RequestArgument` remaining queue | **PASS** |
| Without `EffectServices` → Unsupported | `finish_request` | **PASS** (pure evaluate path) |
| M3 Call arity-before-args unchanged | Call path intact; m3 differential green | **PASS** |

Frames are in-memory only (U-02 OPEN). **PASS**.

---

## 9. Request ordering

### 9.1 Capability-first / non-cap short-circuit

| Case | Expected (REQUEST-NON-CAP-SHORT-CIRCUIT) | Observed | Verdict |
|---|---|---|---|
| Non-cap capability position | Fault before target/params; no EffectId/budget/log/host | `non_cap_short_circuit_agrees` (P+R); journal empty; host calls empty | **PASS** |
| Cap OK + unbound first param | Fault on param LTR; no host/journal | `args_ltr_fault_stops_before_later_params` | **PASS** |

### 9.2 Operation expression vs R-CORE-14 step list

- **R-CORE-14** lists steps (1) capability (2) target (3) arguments — does not name “evaluate operation”.
- **R-CALC-02** freezes `operation: Box<Expr>`.
- **R-CEK-03** frames: `RequestCapability { operation, target, params, env }`, `RequestTarget { capability, operation, params, … }` (operation already a **value** at RequestTarget), `RequestArgument { … }`.
- **M5-PREFLIGHT D-M5-03:** DERIVED authorization to evaluate operation Expr → Op (U-21).

**Implementation:** capability → **operation** → target → params LTR (`RequestOperation` frame is an extra name relative to the three frozen R-CEK-03 Request* frames).

**Verdict:** **PASS WITH LIMITATION** — not a STOP conflict given preflight D-M5-03 and R-CEK-03 implying operation-as-value before target; disclosed as frame-set extension under U-02/U-21. Does not reorder host-before-Issued or non-cap SC.

### 9.3 Args LTR

Distinguished by first-param unbound vs later-param unevaluated (`args_ltr_fault_stops_before_later_params`). **PASS**.

---

## 10. Capability authorization

```text
CapRef
  → kernel.valid_result (gate 5)
  → possession (CapabilityContext.contains)
  → authorize_algebra → authorized(Authority, EffectDesc, t)  # R-CAP-06
```

- Consumes **M4** kernel algebra; no second authority model.
- `CapRef ≠ AuthorityNode`; bits ≠ authority (m4 `capref_bits_are_not_authority` still green).
- `CapRef::from_kernel_parts` remains **public** — **carry M4 disclosure**; not silently tightened or claimed closed.
- Host/persistence do not mint CapRefs.

**PASS** (with CapRef visibility disclosure).

---

## 11. Effect gate ordering (canonical vs implementation)

| Step | Canonical (R-CORE-14) | Implementation | Test evidence | Verdict |
|---|---|---|---|---|
| 1 | Evaluate capability | CEK `RequestCapability` | non-cap SC | **PASS** |
| 2 | Evaluate target | After operation value; `RequestTarget` | CEK | **PASS WITH LIMITATION** (§9.2) |
| 3 | Args LTR | `RequestArgument` | m5 LTR fault | **PASS** |
| 4 | Construct Effect + Digest | `effect_from_values` + `canonical_bytes` + SHA-256 | digest tests | **PASS WITH LIMITATION** (BE layout) |
| 5 | Valid CapRef | `valid_result` | unauthorized/revoked paths | **PASS** |
| 6 | Authorize exact effect + possession | `authorize_algebra(Some(possession),…)` | unauthorized_no_host | **PASS** |
| 7 | Capability ceiling | Folded into authorize `cost_units ≤ R` (R-CAP-06) | algebra ceiling tests M4; **no dedicated M5 outside-ceiling Request case** | **PASS WITH LIMITATION** |
| 8 | Runtime budget issue+complete_max | `issue_plus_complete_max` vs `ThinBudget.available` | budget_deny_no_host | **PASS** (thin) |
| 9 | Runtime reservation | reserve slots check | code path | **PASS** (thin; limited dedicated cases) |
| 10 | Deadline `t+δ_t(req)≤W` | `DELTA_T_REQUEST=1`; LogicalTime only | `deny_deadline_never_hosts` | **PASS** |
| 11 | Host policy | `host_policy_ok` fail-early | host_policy_deny_no_host | **PASS** |
| 12 | Allocate EffectId | `EffectIdAlloc::allocate` after gates 5–11 | monotonic tests; deny paths do not allocate | **PASS** |
| 13 | Commit issue/reserve escrow | debit available + reserved | rollback on persist fail | **PASS WITH LIMITATION** (see §17 R-DUR-07 order) |
| 14 | Durable Prepared→Issued + 2 syncs | append+sync ×2 via `IssuanceJournal` | happy_path; persist_fail | **PASS** (MemoryJournal durability model) |
| 15 | Actor Pending | **thin / absent multi-actor state** | harness only | **PASS WITH LIMITATION** (M6) |
| 16 | Host invocation | `HostExecutor::execute` **only after** step 14 | hinge tests §18 | **PASS** |

No unexplained reorder of host before Issued. Historical R-EFFECT-01 host-before-Issued form correctly **not** implemented (R-CORE-14 wins). **PASS WITH LIMITATION** overall.

---

## 12. Effect ceiling

- Canonical: R-CAP-06 / gate 7 — cost within authority resource ceiling.
- Implementation: `EffectDesc.cost_units = issue+complete_max` checked inside `authorized`.
- Runtime budget (gate 8) is a **separate** consumable pool (`ThinBudget`).
- Dedicated Request-level “outside ceiling but within ThinBudget” differential case: **not present** (M4 resource amplify rejected at derive; effect-path ceiling relies on authorize).

**PASS WITH LIMITATION** — dual-gate intent present; dedicated M5 ceiling kill case thin (preflight noted M005 primarily M5; residual evidence gap).

---

## 13. Budget / reservation

| Aspect | Status |
|---|---|
| `EffectCost` triple | Canonical shape **PASS** |
| Gate 8 affordability | `issue+complete_max` **PASS** |
| Gate 9 reservation | slot compare **PASS** (thin) |
| Escrow debit | saturating sub on thin counters **PASS WITH LIMITATION** |
| Default cost `EffectCost::new(1,1,0)` when AST has no cost | **DISCLOSED** (L-M5-01 / progress) |
| Full MOD-04 conservation harness | **DEFERRED** / thin |

No second cost model. **PASS WITH LIMITATION**.

---

## 14. Deadline

- Predicate: `t + δ_t(req) ≤ W` with `δ_t=1` (R-BUDGET-16 / R-CORE-14).
- Type: `LogicalTime` only.
- Search of M5 path: **no** `SystemTime` / `Instant::now` / `UNIX_EPOCH` / `thread_rng`.

**PASS**.

---

## 15. Host policy

| Check | Verdict |
|---|---|
| Gate 11 fail-early before EffectId/journal/host | **PASS** (`host_policy_ok == false` → Denied; PanicHost never invoked) |
| Host ≠ AuthorityIssuer | **PASS** (no kernel grant/derive in host crate) |
| Host cannot broaden capability | **PASS** (no authority APIs) |
| DenyHost after Issued still possible (defense in depth) | **PASS** (`host_deny_after_issued` → HostFailed **with** durable Issued) |

**PASS**.

---

## 16. EffectId

| Check | Verdict |
|---|---|
| Monotonic 0,1,2 successive successes | **PASS** (runtime + m5) |
| No wall-clock / random IDs | **PASS** |
| Deny before step 12 does not allocate | **PASS** (R-EFFECT-04; unauthorized/budget/policy tests; `peek_next` rollback on persist fail restores pre-s12) |
| Untrusted Request cannot supply EffectId | **PASS** (allocator machine-side only) |

**PASS**.

---

## 17. Prepared / Issued

### 17.1 Causal order (R-DUR-02/03)

```text
append(Prepared) → sync → append(Issued) → sync → host
Issued ⇒ Prepared   # MemoryJournal causal check
```

Payloads include `effect_bytes` + `EffectCost` (R-DUR-06). **PASS**.

### 17.2 Durability model

`MemoryJournal`: pending until `sync`; `is_durably_issued` inspects **durable** vector only — not a lone `issued: bool` flag without barrier. Acceptable as **authorized M5 test double** (preflight); not a disk fsync. **PASS WITH LIMITATION**.

### 17.3 R-DUR-07 live failure vs strict journal-driven order

Canonical (R-DUR-07): in-memory s12–s13 mutations **MUST NOT** occur before Prepared append+sync Ok (C-106); on failure → pre-s12 state; host never called.

**Implementation:** allocates id + debits budget **then** append/sync; on error **rolls back** id/budget and returns `PersistenceError`; host not called (`persist_fail_no_host`).

| Property | Status |
|---|---|
| Host never on persist fail | **PASS** (GI-SEC-07 intact) |
| Observable pre-s12 restoration after fail | **PASS** (rollback; id peek 0) |
| Strict “no in-memory s12–13 before first sync Ok” | **PASS WITH LIMITATION** — temporary in-memory mutation then rollback, not journal-first commit |

Not classified as GI-SEC-07 violation. Disclosed as **L-M5-DUR07-ORDER**. Second-sync failure API exists (`fail_next_sync`); runtime unit coverage emphasizes `fail_next_append` — residual evidence gap.

No M7 recovery engine. **PASS WITH LIMITATION**.

---

## 18. HARD GATE — Durable Issued before Host (GI-SEC-07 / R-DUR-01)

### 18.1 Call graph (production)

```text
evaluate_request / step_with_effects
  → finish_request
    → EffectServices::run
      → run_effect_pipeline
          gates 5–11 (deny → return; no host)
          allocate id; escrow
          journal.append(Prepared); journal.sync()
          journal.append(Issued); journal.sync()
          ctx.host.execute(&request)     # sole production HostExecutor call
          validate_and_complete
```

`HostExecutor::execute` production call sites:

| Site | Role |
|---|---|
| `effects.rs` `run_effect_pipeline` after Issued sync | **sole production path** |
| `illegal_host_before_issued` | **test-only** negative helper |
| `ror-host` adapter impls | implementations, not callers |
| unit/differential tests | harness |

No CEK → host bypass; no host on gate deny; no host on persist fail.

### 18.2 Adversarial evidence

| Scenario | HostInvoked | DurableIssued | Evidence |
|---|---|---|---|
| Happy path | true | true | `happy_path_issued_before_host`; m5 `happy_path_agrees`; post-assert `is_durably_issued` |
| Unauthorized / budget / deadline / host-policy deny | false | false | PanicHost `invoked==false`; empty journal |
| Persist append fail | false | false | `persist_fail_no_host` + PanicHost |
| Illegal direct execute without Issued | panics | n/a | `mutation_intent_host_before_issued_killed` (`should_panic` GI-SEC-07) |
| Host deny **after** Issued | true (execute entered) | true | `host_deny_after_issued` |

Structural Cargo: `ror-runtime → ror-persistence` (R-TRUST-05); `ror-host → ror-runtime` (mod/18 MOD-09→MOD-08). Host does not own the journal.

### 18.3 Mutation intent

| Mutation target | Result | Killed by |
|---|---|---|
| Remove durable-Issued requirement / call host early | PanicHost / should_panic | `mutation_intent_host_before_issued_killed` |
| Skip authorization then host | Denied + `!invoked` + empty journal | `mutation_intent_skip_auth_killed` |

**No global mutation kill rate claimed.**

### 18.4 Hinge verdict

**PASS** — no reviewed execution path yields `HostInvoked(E)` without prior durable Issued barrier on the production pipeline. MemoryJournal is a disclosed durability substrate limitation, not a host-before-Issued hole.

---

## 19. Host adapters

| Adapter | Before Issued? | Mints authority? | External I/O? | Determinism | Verdict |
|---|---|---|---|---|---|
| MockHost | only if caller violates hinge | no | no | yes | **PASS** |
| DenyHost | same | no | no | yes | **PASS** |
| ReplayHost | same; ordered queue; rebinds id+digest | no | no (trace only) | yes | **PASS** (R-HOST-03) |
| PanicHost | any execute panics | no | no | harness | **PASS** |

Replay does not become a live external-effect path. **PASS**.

**HostExecutor trait location:** defined in `ror-runtime`, implemented in `ror-host` to avoid Cargo cycle while preserving `ror-host → ror-runtime` (mod/18). **PASS WITH LIMITATION** (L-M5-04 ownership packaging disclosure — not a forbidden reverse edge).

---

## 20. Receipts

| Check | Implementation | Tests | Verdict |
|---|---|---|---|
| Validate id + digest (R-EFFECT-06) | `validate_and_complete` → `ReplayCorruption` | code path; **no dedicated wrong-id unit test** | **PASS WITH LIMITATION** |
| Data-only result (R-EFFECT-08) | `ReceiptValue` enum excludes Cap/Fn | by construction | **PASS WITH LIMITATION** |
| Host fault mapping | PolicyDenied / HostFault codes; no debug strings in values | host_deny_after_issued | **PASS** |

**PASS WITH LIMITATION**.

---

## 21. Completion / failure accounting

| Class | Distinct fault/outcome | Host? | Issued? |
|---|---|---|---|
| Unauthorized / invalid cap | `Unauthorized` / `CapabilityRevoked` | no | no |
| Budget / reserve | `BudgetExhausted` | no | no |
| Deadline | `DeadlineExceeded` | no | no |
| Host policy (gate 11) | `HostPolicyDenied` | no | no |
| Persistence | `PersistenceError` | no | no (rollback) |
| Host fail after Issued | `HostFailed` / `HostPolicyDenied` / `HostFault` | yes | **yes** |
| Success | `Completed` + Value | yes | yes |
| Receipt mismatch | `ReplayCorruption` | (host returned) | yes |

Thin completion: no full `EffectCompleted` append+sync charge sequence (R-EFFECT-07 / R-RECOV-09 completion order) — **DISCLOSED** L-M5-03; full depth aligns with later persistence work. Does not retroactively erase Issued. **PASS WITH LIMITATION**.

---

## 22. Reference independence

| Rule | Evidence | Verdict |
|---|---|---|
| No prod runtime/kernel/host/persistence imports | mechanical `rg` clean | **PASS** |
| Independent gate pipeline | `effect_model::ref_run_pipeline` | **PASS** |
| Independent Request CEK konts | `pure_cek` WaitingReq* | **PASS** |
| Shared `ror-core` types only | Cargo.toml | **PASS** |
| Shared `admissible_constraint_wrt_parent` | M4 carry in cap_algebra | **DISCLOSED** (not expanded to shared effect CEK) |

**PASS**.

---

## 23. Differential tests

`ror-differential` m5 covers: accept, non-cap SC, unauthorized, budget deny, host-policy deny, EffectId monotonicity, digest equality, args LTR fault, host-before-Issued mutation, skip-auth mutation, M4 regression hook.

Harness compares black-box `Observation` (halt/fault values), not internal frame pointers.

**PASS** (receipt wrong-id / second-sync-fail / dedicated ceiling-out differential cases remain thin — disclosed).

---

## 24. Security

| Threat | Control | Verdict |
|---|---|---|
| Expr → host bypass | CEK + 16-step only | **PASS** |
| Host before Issued | structural order + tests | **PASS** |
| Capability amplification via Request | authorize uses M4 algebra; Request does not mint | **PASS** |
| CapRef forgery | Valid + possession | **PASS** (bits public — disclosure) |
| Host mints authority | no kernel APIs in host | **PASS** |
| Receipt injects authority | ReceiptValue data-only | **PASS WITH LIMITATION** |
| Effect identity collision | monotonic id + digest pair | **PASS** |
| Wall-clock EffectId | absent | **PASS** |

Central chain preserved:

```text
Untrusted Request ↛ Authority
Untrusted Request ↛ Host
HostInvoked(E) ⇒ DurableIssued(E)
HostExecutor ≠ AuthorityIssuer
```

**PASS**.

---

## 25. Determinism

EffectId counter, EffectDigest SHA-256 over fixed bytes, LogicalTime deadline, ordered ReplayHost, BTree/Vec structures, no HashMap gate order, reference observations agree on seeded arenas.

**PASS**.

---

## 26. Dependency authority

| Edge | Canonical | Cargo | Verdict |
|---|---|---|---|
| runtime → core | REQUIRED | yes | **PASS** |
| runtime → kernel | REQUIRED (gates 5–7) | yes | **PASS** |
| runtime → persistence | **R-TRUST-05 hinge** | yes | **PASS** |
| host → core | REQUIRED | yes | **PASS** |
| host → runtime | MOD-09 → MOD-08 | yes | **PASS** |
| persistence → core | REQUIRED | yes | **PASS** |
| reference ↛ {runtime,kernel,host,persistence} | FORBIDDEN | absent | **PASS** |
| HostExecutor trait in runtime | packaging under host→runtime | yes | **PASS WITH LIMITATION** (§19) |

No forbidden production reverse edge introduced. **PASS**.

---

## 27. M4 regression

Differential m4 suite green (derive, no-amp, revoke cascade, validity, attenuation, expiration, capref bits, mutations). Kernel unit tests green. CapRef opacity / machine≠data Value unchanged.

**PASS**.

---

## 28. M1–M3 regression

- M1: core canonical + SHA-256 KATs still in workspace (30 core tests green).
- M2/M3: differential m2/m3 green; runtime CEK suite green; arity-before-args preserved.

**PASS**.

---

## 29. OAD reconciliation

| OAD | Status | M5 review |
|---|---|---|
| U-39…U-44 | RESOLVED (addendum VII) | Used; not re-opened |
| U-02 | OPEN | Frames in-memory; extra RequestOperation name disclosed |
| U-08 / U-14 | OPEN | Provisional Fault labels |
| U-09 | OPEN | Domains split retained |
| U-21 | OPEN | Op/Target/Params + BE effect bytes provisional |
| U-31 | OPEN | Authority fields unchanged |
| AMB-12 / REQ-CAP-024 | registry AMBIGUOUS | R-CAP-10 still governs attenuate; Request uses Authorized |

**No silent OAD resolution.** **PASS**.

---

## 30. R-REG reconciliation

```text
reg/requirements.json → 184 × SPECIFIED   (computed this review)
status-transitions.transitions → 0
```

No status promotion in this milestone. Implementation + tests **≠** VERIFIED/PROVEN. **PASS**.

---

## 31. Disclosed limitations

| ID | Limitation | Class |
|---|---|---|
| U-02 | Request frames in-memory; RequestOperation extra vs three frozen Request* names | OPEN |
| U-08 | Provisional Fault / HostFault labels | OPEN |
| U-09 | Machine vs data Value | OPEN |
| U-21 | Op/Target/Params; fixed BE `Effect::canonical_bytes` ≠ full 15A Effect envelope | OPEN |
| U-31 | Authority field provisional | OPEN |
| D-M4-CapRef | `CapRef::from_kernel_parts` public | CARRY |
| D-M4-Admiss | Shared core admissibility helper | CARRY |
| D-M5-04 | Thin Pending — multi-actor = M6 | DISCLOSED |
| D-M5-05 | Thin budget algebra | DISCLOSED |
| D-M5-06 | Issuance API only — not M7 recovery | DISCLOSED |
| L-M5-01 | Default EffectCost (1,1,0) | DISCLOSED |
| L-M5-03 | Thin completion journal / R-EFFECT-07 depth | DISCLOSED |
| L-M5-04 | HostExecutor trait packaged in runtime | DISCLOSED |
| L-M5-DUR07-ORDER | Id/budget mutate then rollback on persist fail (not strict journal-first) | DISCLOSED |
| L-M5-CEIL-TEST | Dedicated outside-ceiling Request differential thin | DISCLOSED |
| L-M5-RCPT-TEST | Wrong id/digest receipt unit tests thin | DISCLOSED |
| L-M5-SYNC2-TEST | Second-sync failure path less covered than append fail | DISCLOSED |
| Evidence | Tests ≠ SEMANTICALLY VERIFIED / PROVEN | DISCLOSED |

---

## 32. Corrections

Review-only artifact: this file. **No** semantic code changes, **no** OAD/R-REG/canonical edits, **no** amend of `f178562`.

Progress report gate counts were **reproduced** and match (160 tests). No stale-hash correction required.

---

## 33. Final classification

```text
M5 IMPLEMENTATION REVIEW = ACCEPTED WITH DISCLOSED EVIDENCE LIMITATIONS
```

**Rationale:**

- Canonical M5 scope delivered under R-CORE-14 / R-ORDER-02.
- **GI-SEC-07 / R-DUR-01 hinge holds** on the production call graph, failure paths, and adversarial/mutation tests — the primary review question answers **no**: there is no reviewed path to `HostInvoked(E)` before `DurableIssued(E)`.
- Capability authorization reuses M4; reference independence holds; dependencies match ownership; M1–M4 green; R-REG unpromoted; OADs unclosed.
- Residual gaps are **disclosed evidence/depth limitations** (thin budget/Pending/completion, provisional encodings, R-DUR-07 strict journal-first nuance, some test matrix holes) — not host-before-Issued or authority-bypass blockers.

**Not** unqualified `ACCEPTED` (disclosures material).  
**Not** `BLOCKED` (no GI-SEC-07 failure, no reference coupling, no M7 scope grab, no silent OAD/R-REG).

**M5 semantic verification / PROVEN: NOT CLAIMED.**

---

## 34. Next authorized operation

```text
NEXT = M6 PREFLIGHT
```

**Do not implement M6** (actors/scheduler/mailboxes) in the review commit. M6 requires its own preflight against R-ORDER-02 and actor-section authority.

---

## Final state board

```text
M0                         GREEN
M1 frozen subset           ACCEPTED WITH DISCLOSED EVIDENCE LIMITATIONS
M1 full                    NOT COMPLETE
M2 implementation          ACCEPTED WITH DISCLOSED EVIDENCE LIMITATIONS
M2 semantic verification   NOT CLAIMED
M3 implementation          ACCEPTED WITH DISCLOSED EVIDENCE LIMITATIONS
M3 semantic verification   NOT CLAIMED
M4 implementation          ACCEPTED WITH DISCLOSED EVIDENCE LIMITATIONS
M4 review                  ACCEPTED WITH DISCLOSED EVIDENCE LIMITATIONS
M5 preflight               GREEN WITH DISCLOSED LIMITATIONS
M5 implementation          ACCEPTED WITH DISCLOSED EVIDENCE LIMITATIONS
M5 semantic verification   NOT CLAIMED
R-REG                      184 × SPECIFIED
M6                         NOT STARTED
M7                         NOT STARTED
```

---

## Hinge proof summary (executive)

```text
Question: Can any execution path cause HostInvoked(E) before DurableIssued(E)?
Answer:   NO — on the production Request pipeline (FACT from call-graph audit).

Evidence:
  1. Single production execute() after Issued+sync in run_effect_pipeline
  2. All gate/persist denies return before execute; PanicHost proves non-invocation
  3. Mutation calling host without Issued panics (GI-SEC-07)
  4. runtime→persistence Cargo edge carries R-TRUST-05
  5. MemoryJournal durability is sync-barrier based (disclosed substrate)

Limitations do not punch the hinge: thin Pending, provisional codecs, and
rollback-style R-DUR-07 ordering affect evidence depth, not host-before-Issued.
```

---

*End of M5-REVIEW. Next authorized operation: M6 PREFLIGHT only.*
