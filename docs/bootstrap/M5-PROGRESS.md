# M5 Implementation Progress

**Operation type:** M5 IMPLEMENTATION (Request / effects / durable issuance / host boundary).  
**Claim:** `M5 IMPLEMENTATION = COMPLETE WITH DISCLOSED EVIDENCE LIMITATIONS`  
**Next:** `M5 IMPLEMENTATION REVIEW`  
**Preflight baseline:** `b64fb9a` (`docs/bootstrap/M5-PREFLIGHT.md` — GREEN WITH DISCLOSED LIMITATIONS)

Evidence labels: **FACT** | **DERIVED** | **DISCLOSED LIMITATION** | **TEST**

---

## 1. Identity

| Item | Value | Class |
|---|---|---|
| Branch | `arena/01a06993-red-on-rust` | FACT |
| Preflight HEAD | `b64fb9a` | FACT |
| Toolchain | `ror-stable` rustc 1.88.0 | FACT |
| Scope | R-CORE-14 16-step Request; R-DUR-01/02 issuance; R-HOST mock; receipts | FACT |
| Out of scope | M6 actors/scheduler; M7 WAL/snapshot/T0–T6 recovery; R-REG/OAD close | FACT |

---

## 2. Deliverables by crate

| Crate | Surface | Authority |
|---|---|---|
| `ror-core` | `effect::{Effect, EffectCost, Consumable, Reserved, Target, Params, EffectDigest path, EffectIdAlloc, EffectRequest, IssuanceRecord, EffectReceipt, ReceiptValue, ThinBudget, HostFaultCode}`; M5 `Fault` variants; `sugar::request` | R-CALC-04/05; R-CANON-09; U-08/U-21 provisional |
| `ror-runtime` | Request CEK frames (`RequestCapability` / `RequestOperation` / `RequestTarget` / `RequestArgument`); LTR params; non-cap short-circuit; `effects` pipeline gates 5–16; `HostExecutor` trait; `evaluate_request` | R-CORE-14; R-CEK-03; R-EFFECT-04; REQUEST-ARGS-LTR / NON-CAP-SHORT-CIRCUIT |
| `ror-persistence` | `IssuanceJournal` + `MemoryJournal`; Prepared→Issued causal append+sync | R-DUR-01/02/06/07 (issuance only; **not** M7 recovery) |
| `ror-host` | `MockHost`, `DenyHost`, `ReplayHost`, `PanicHost` implementing runtime `HostExecutor` | R-HOST-01/02/03 |
| `ror-kernel` | Unchanged M4 algebra; authorize_algebra + valid used by gates 5–6 | R-CAP-06/07; R-KERN-04 |
| `ror-reference` | Independent `effect_model` + Request CEK konts; `RefJournal` / `RefMockHost` / `RefPanicHost` | R-REF-02 / R-SCOPE-04 |
| `ror-differential` | `m5` observations: accept/deny, non-cap SC, LTR, EffectId, digest, journal Issued, host count, host-before-Issued mutation | final/04 M5 |

---

## 3. Hard hinge — `HostInvoked ⇒ DurableIssued`

| Mechanism | Evidence | Class |
|---|---|---|
| Structural order | `run_effect_pipeline` only calls `host.execute` after Prepared sync + Issued sync succeed | FACT |
| Cargo edge | `ror-runtime → ror-persistence`; host does not own journal; runtime does not depend on host (trait in runtime; adapters in host) | FACT |
| Assert | `run_with_memory_journal` asserts `journal.is_durably_issued(id)` on host path outcomes | FACT |
| Deny paths | Unauthorized / budget / deadline / host-policy / persist-fail use `PanicHost` — never invoke | FACT (unit + differential) |
| Mutation intent | `illegal_host_before_issued` + `PanicHost` panics with `GI-SEC-07`; skip-auth path leaves journal empty | FACT |
| Tag | `EFFECT-ISSUE-DURABLE-BEFORE-HOST` intent covered by tests above | DERIVED |

**No host-before-Issued production path exists** in the Request pipeline.

---

## 4. Gate matrix (R-CORE-14)

| Step | Implementation | Short-circuit |
|---|---|---|
| 1–3 CEK | capability → non-cap TypeError; operation; target; params LTR | FACT |
| 4 Effect+digest | `Effect::canonical_bytes` + SHA-256 `EffectDigest` (in-tree) | FACT |
| 5 Valid | `kernel.valid_result` | FACT |
| 6 Authorize + possession | `authorize_algebra(Some(possession), …)` | FACT |
| 7 Ceiling | via `EffectDesc.cost_units` vs authority R in authorize | FACT (thin dual with gate 8) |
| 8 Budget | `issue + complete_max ≤ available` | FACT |
| 9 Reservation | `reserve.slots ≤ budget.reserved` | FACT |
| 10 Deadline | `t + δ_t(req=1) ≤ W` | FACT |
| 11 Host policy | `host_policy_ok` fail-early | FACT |
| 12 EffectId | monotonic `EffectIdAlloc` | FACT |
| 13 Escrow | debit available + reserved; rollback on persist fail | FACT |
| 14 Durable | Prepared append+sync; Issued append+sync | FACT |
| 15 Pending | thin single-actor (no multi-actor state machine) | DISCLOSED |
| 16 Host | after Issued only | FACT |
| Receipt | id+digest match; `ReceiptValue` data-only | FACT |

---

## 5. Verification gates (this sprint)

| Command | Result | Class |
|---|---|---|
| `cargo fmt --check` | **PASS** | FACT |
| `cargo check --workspace` | **PASS** | FACT |
| `cargo test --workspace` | **PASS** (160 tests; 0 failed) | FACT |
| `cargo clippy --workspace --all-targets -- -D warnings` | **PASS** | FACT |
| `unsafe` in crates | none (all `forbid(unsafe_code)`) | FACT |
| crates.io new deps | none (path-only workspace) | FACT |
| Reference independence | no `use ror_{runtime,kernel,host,persistence}` in `ror-reference` | FACT |
| R-REG | **184 × SPECIFIED** (unchanged; no promotions) | FACT |

---

## 6. Test coverage (selected)

| Case | Location |
|---|---|
| Happy path Issued before host | `ror-runtime` effects; differential m5 |
| Unauthorized / budget / deadline / host-policy deny → no host | runtime effects + m5 |
| Persist append fail → PersistenceError, id rollback, no host | runtime effects |
| Non-cap short-circuit before target/params | CEK + m5 |
| Args LTR: first unbound param faults; no journal | m5 |
| EffectId monotonic 0,1,2 | runtime + m5 |
| Digest deterministic / field-sensitive | core effect |
| Host deny after Issued → HostFailed + durable Issued | runtime |
| PanicHost on illegal pre-Issued | host + m5 mutation |
| Journal Issued without Prepared → CausalViolation | persistence |
| ReplayHost ordered ID+digest bind | host |
| M1–M4 regressions | existing suites green under workspace test |

---

## 7. Disclosed limitations (carried + new)

| ID | Limitation | Class |
|---|---|---|
| U-02 | Request frames in-memory only; no frame codecs | OPEN |
| U-08 | Provisional Fault / HostFault labels | OPEN |
| U-09 | Machine vs data Value split retained | OPEN |
| U-21 | Op/Target/Params provisional; Effect canonical layout fixed BE for M5 | OPEN |
| U-31 | Authority field provisional continues | OPEN |
| D-M5-04 | Thin Pending / single-actor harness — full multi-actor = M6 | DISCLOSED |
| D-M5-05 | Thin `ThinBudget` — full MOD-04 algebra depth may lag | DISCLOSED |
| D-M5-06 | Issuance journal API only — not M7 recovery engine | DISCLOSED |
| D-M5-09 | `CapRef::from_kernel_parts` still public (M4 carry); Valid+possession bind | DISCLOSED |
| D-M5-10 | Shared `admissible_constraint_wrt_parent` in core (M4 carry); no shared effect CEK | DISCLOSED |
| L-M5-01 | Default `EffectCost::new(1,1,0)` when AST has no cost field | DISCLOSED |
| L-M5-02 | Operation evaluated as `Integer` op-tag (U-21) | DISCLOSED |
| L-M5-03 | Completion journal `Completed` record optional/thin (receipt validate yes) | DISCLOSED |
| L-M5-04 | HostExecutor trait lives in `ror-runtime` to avoid host↔runtime Cargo cycle; adapters in `ror-host` | DISCLOSED |
| Evidence | Differential + unit tests ≠ SEMANTICALLY VERIFIED / PROVEN | DISCLOSED |

---

## 8. Explicit non-claims

- **Not** SEMANTICALLY VERIFIED or PROVEN.
- **Not** M6 actors / scheduler.
- **Not** M7 WAL framing, snapshot, crash recovery, T0–T6.
- **Not** R-REG promotion or OAD resolution.
- **Not** live OS host adapters beyond mock/replay/panic.
- **Not** alternate effect codecs or non-SHA-256 digests.

---

## 9. Security posture (summary)

```text
Untrusted Expr::Request
  → CEK eval (cap-first, non-cap SC, LTR)
  → gates 5–11
  → EffectId + escrow
  → Prepared+sync → Issued+sync
  → HostExecutor::execute
  → receipt validate → Value
```

GI-SEC-07 hinge enforced structurally and by tests. No Expr→host bypass.

---

## 10. Final board

```text
M0                         GREEN
M1–M4                      ACCEPTED WITH DISCLOSED EVIDENCE LIMITATIONS (prior)
M5 preflight               GREEN WITH DISCLOSED LIMITATIONS @ b64fb9a
M5 implementation          COMPLETE WITH DISCLOSED EVIDENCE LIMITATIONS
M5 semantic verification   NOT CLAIMED
R-REG                      184 × SPECIFIED
M6                         NOT STARTED
M7                         NOT STARTED
NEXT                       M5 IMPLEMENTATION REVIEW
```

---

*End of M5-PROGRESS. Review is the next authorized operation.*
