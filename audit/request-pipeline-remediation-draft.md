# Addendum VII draft — request-pipeline remediation (2026-09-03)

Status: **DRAFT — NOT ADOPTED.** This file is the decision record for
`spec/09` U-39…U-45 and the review record for `spec/06` C-103…C-109, filed by
`audit/request-pipeline-proof-obligation-matrix.md` (GAP-01…GAP-18). It issues no
frozen text; per R-SCOPE-03 nothing here may be cited as authority until applied
by the same mechanism as `audit/spec_addendum5.py` and verified by the full checker
stack. Proposed IDs are provisional and will be renumbered at application.

## 1. Why this pass exists

The matrix traced every path from `Expr::Request` to a host-visible effect through the
frozen 16-step sequence and proved the gate order itself sound while finding that the
invariant `HostInvoked(E) ⇒ DurableIssued(E)` is **not provable as specified** on four
counts:

1. **C-105 / U-41:** the durable `Prepared`/`Issued` records carry `{id, actor, digest}`
   only — no effect, no cost — so escrow survival (R-DUR-05), T1's budget restoration
   (REQ-DUR-010) and T2–T4 reconciliation identity have no durable source of truth.
2. **C-106 / U-42:** a live journal/fsync failure at step 14 has no semantics — no
   declared fault, no rollback, R-EFFECT-04's five assertions impossible after steps
   12–13, and no record kind makes R-CORE-12's "journal-driven commit" realizable.
3. **C-104 / U-40:** the step-10 deadline is pinned weak (`t ≤ W`) while the formal
   rules require `t + δ_t(req) ≤ W`; a host call can follow an over-deadline issuance.
4. **C-103 / U-39:** `spec/01` S-12 still publishes the turn-[21] 16-step protocol with
   host emission before the durable `Issued` write — the exact inversion the invariant
   forbids.

Plus two boundary-precision items (C-107, C-109 → U-43), a verification-register gap
(U-44) and the orphaned resource-accounting addendum (C-108 → U-45).

## 2. What this freezes (proposed)

| Proposed ID | Freezes | Resolves / extends |
|---|---|---|
| **R-CORE-14** | One canonical request protocol; deterministic deadline premise; atomic s12–s14b section; completion-boundary order | C-103 (U-39), C-104 (U-40), C-109 (U-43); extends R-EFFECT-03/05, R-BUDGET-06, R-DUR-02, R-CORE-06/12 |
| **R-DUR-06** | Durable issuance record payload: `EffectPrepared`/`EffectIssued` carry effect digest **and** the canonical effect bytes and cost triples; escrow/reservation amounts durably recorded | C-105 (U-41); extends R-DUR-02/05, R-PERSIST-03, R-BUDGET-05 |
| **R-DUR-07** | Live journal/fsync failure at issuance: single atomic journal-driven commit; `Fault::PersistenceError` declared and closed; failure ⇒ pre-s12 state | C-106 (U-42); extends R-DUR-02, R-EFFECT-04, R-CORE-12/13, R-PERSIST-02/03 |
| **R-RECOV-09** | Recovery reconstruction authority: no `SnapshotCommit` inside the issuance section; `next_effect_id` from max replayed `Issued` ID; `EffectCompleted` fsync precedes accounting/resume | C-107, C-109 (U-43); extends R-PERSIST-05/06, R-RECOV-02/03/07 |
| **R-TEST-12** | Request-frame obligation tags `REQUEST-ARGS-LTR` and `REQUEST-NON-CAP-SHORT-CIRCUIT` in the frozen tag list | U-44; extends R-TEST-07 |

(Deliberately **not** proposed here: R-BUDGET-10…14 adoption — U-45 owns that
decision, and this draft does not pre-empt its escrow-path reconciliation.)

## 3. Proposed exact normative texts

**R-CORE-14 (canonical request protocol and transaction boundary — frozen addendum).**
The request sequence is exactly the 16-step master-prompt form
(`Red-on-Rust.md` L38024–38045): evaluate capability, evaluate target, evaluate
arguments left-to-right, construct canonical `Effect` + `EffectDigest`, validate
CapRef, authorize exact effect, capability ceiling, runtime budget, runtime
reservation, deadline, host policy, allocate `EffectId`, commit issue
budget/reservation, durable issuance, actor `Pending`, host invocation. The
turn-[21] 16-step form — in which the host emission precedes the durable `Issued`
record — is SUPERSEDED (quoted, not deleted): `HostInvoked(E) ⇒ DurableIssued(E)`
holds with no ordering exception, and `spec/01` R-EFFECT-01 MUST publish this
master-prompt form. The step-10 deadline premise MUST be the post-advance form
`t + δ_t(req) ≤ W`; the pre-advance `t ≤ W` reading is SUPERSEDED. Steps 12–14b form
one atomic section: no `SnapshotCommit`, no scheduler yield, no observable event MAY
occur between allocation of the `EffectId` and the second fsync of `Issued`. On
completion, `append(EffectCompleted)` MUST precede `sync()`, which MUST precede the
charge/release accounting and the continuation resume. *(Draft — post-audit
remediation proposal for C-103/C-104/C-109; additive per R-SCOPE-03; no source
transcription.)*

**R-DUR-06 (durable issuance payload — frozen addendum).** `EffectPrepared { id,
actor, digest, effect_bytes, issue, complete_max, reserve }` and `EffectIssued
{ id, actor, digest, effect_bytes, issue, complete_max, reserve }` — the canonical
bytes of the effect, its `EffectDigest`, and the cost triple MUST be recorded with
every issuance record; the `{id, actor, digest}` shapes are SUPERSEDED (quoted, not
deleted) and `{id, actor, digest}` remains valid only for the planner-visible
observation projection (R-PLANNER-07), never as the persistence payload. The
escrowed `complete_max` and the reservation are thereby reconstructible at every
T0–T6 point; T1 discard restores from the record; reconciliation at T2–T4 carries
the effect it must query about; T5 resumes with the recorded result byte-exactly.
Record payload MUST NOT carry raw capability values (R-CORE-07/R-CANON-12: the
kernel-mediated codec path governs), and the record's `effect_bytes` MUST verify
`EffectDigest(effect_bytes) = digest` at append and at recovery — a mismatch is
`EffectJournalCorruption`. *(Draft — proposal for C-105/U-41; extends R-DUR-02/05,
R-PERSIST-03; no source transcription.)*

**R-DUR-07 (live issuance failure — frozen addendum).** Persistence failures on the
issuance path are data, never panics (R-CORE-12) and MUST fault with the declared
`Fault::PersistenceError` added to the R-CORE-13 closed enumeration. The commit is
journal-driven: `append(EffectPrepared …)` (extended per R-DUR-06) followed by
`sync()` is the ONE durable mutation that also journals the ID allocation and the
budget/reservation/escrow commit; the in-memory mutations of steps 12–13 MAY NOT
occur before that append+fsync returns Ok. On any append or sync error: the
transition faults, `next_effect_id`, budget, reservations and escrow are at their
pre-s12 values, the event log gains no entry, and `HostExecutor::execute` is never
invoked — R-EFFECT-04's five assertions hold for this path. A failure of the second
`sync()` (the `Issued` record's fsync) is likewise a declared `Fault::PersistenceError`
with the machine rolled back to the `Prepared`-durable state and the journal
classifying the effect `Prepared ∧ ¬Issued ⇒ Discard` at recovery (R-DUR-04). The
audit's `Fault::PersistenceError` (Op-17) is thereby the single declared fault for
this family; no alternative `InternalInvariant` classification is permitted for a
storage error. *(Draft — proposal for C-106/U-42; extends R-DUR-02, R-EFFECT-04,
R-CORE-12/13, R-PERSIST-02/03; mutation M037; no source transcription.)*

**R-RECOV-09 (recovery reconstruction authority — frozen addendum).** Recovery MUST
reconstruct `next_effect_id = max({id ∈ replayed EffectIssued}) + 1`; a snapshot
counter less than that is stale and MUST be advanced (recorded, never silently
fixed: a snapshot counter GREATER than the journal maximum is a
`RecoveryFault`). A `SnapshotCommit` MAY NOT exist with its `last_effect_sequence`
inside an issuance section (s12–s14b); the recovery of such a snapshot, if ever
found, is a `RecoveryFault`, and the snapshot-taker MUST serialize against the
section. The completion order is frozen: `append(EffectCompleted)`, then `sync()`,
then charge/release, then resume (R-CORE-14); a crash after the host returns but
before the fsync is T4 (`Indeterminate`), and T5 requires the fsync to precede the
resume. *(Draft — proposal for C-107/C-109/U-43; extends R-PERSIST-04/05/06,
R-RECOV-02/03/07; no source transcription.)*

**R-TEST-12 (request-frame verification tags — frozen addendum).** The R-TEST-07
obligation-tagged coverage list MUST additionally include `REQUEST-ARGS-LTR`
(request arguments evaluated strictly left-to-right, exactly one per CEK step;
G3) and `REQUEST-NON-CAP-SHORT-CIRCUIT` (a non-capability capability expression
faults before any target/parameter evaluation and before any gate 4–16 runs;
G1). Both tags MUST be covered by Track A, registered in `spec/08`, and tracked in
`mod/05`/`mod/08`. *(Draft — proposal for U-44; extends R-TEST-07; no source
transcription.)*

## 4. Edit set at application (provisional)

| Artifact | Edit |
|---|---|
| `spec/01` S-02, S-11…S-14, S-18, S-19, S-21 | Append the five obligations in §3; restate R-EFFECT-01 to the master-prompt protocol |
| `spec/03` | Add rows R-CORE-14, R-DUR-06, R-DUR-07, R-RECOV-09, R-TEST-12 (SPECIFIED) |
| `req/registry` | Atomic records REQ-DUR-015…REQ-DUR-0xx, REQ-RECOV-023…, REQ-TEST-0xx; SOURCE lines to this draft and the resolved C/U rows |
| `mod/01-core.md`, `mod/04-budget.md`, `mod/08-effect.md`, `mod/11-persistence.md`, `mod/12-recovery.md`, `mod/17-verification.md` | Ownership: add R-CORE-14 (MOD-01), R-DUR-06/07 (MOD-11), R-RECOV-09 (MOD-12), R-TEST-12 (MOD-17) |
| `spec/03` mutation registry (`spec/08` §2) | M037 = journal-driven commit reordered after in-memory mutation (host-visible pre-durability); M038 = `{id, actor, digest}` issuance payload (loss of escrow source of truth) |
| `spec/06` rows C-103…C-109 | Re-grade `resolved-by-addendum` (except C-108, which stays corrected-in-place with U-45 open) |
| `spec/09` U-39…U-43 | Mark resolved with the addendum as the decision; U-44/U-45 remain open for the tag/draft-adoption decisions the addenda themselves do not take |

## 5. Verification at application

- `python3 check.py` green (11 checkers, incl. the register-size pins updated to
  109 C-rows / 39 U-headings and the prose-count gate at "108 findings in 109 rows").
- `spec/_build_index.py` regenerates `spec/10-index.json` with 108 indexed findings /
  39 unresolved; `mod/_build.py` and `dep/_graph.py` idempotent.
- New obligations enter the differential and mutation suites: M037/M038 must be
  registered in `spec/08` before adoption is declared, and R-DUR-06/07 evidence is
  consumed by the existing tags `EFFECT-ISSUE-DURABLE-BEFORE-HOST`,
  `BUDGET-ESCROW-CONSERVATION`, `RECOVERY-ISSUED-INDETERMINATE` and the T0–T6 crash
  matrix at M10.
- The draft is applied only by a scripted, dry-run-verified mechanism
  (`spec_addendum*.py` pattern) so the exact edit set is reviewable and the
  idempotency guard armed.

## 6. Open after this draft

- U-44 (tag-adoption) and U-45 (R-BUDGET-10…14 adoption + escrow-path reconciliation)
  are decisions this draft identifies but does not take.
- U-02 (machine-state encodings) and U-07 (δ_t values) remain the blockers for
  byte-level evidence of R-DUR-06/R-CORE-14; U-36 (Lifetime timebase) remains the
  blocker for the G5/G6 gates; U-08/U-14 (fault enumeration) gates the declared
  `Fault::PersistenceError` addition the draft proposes.
- U-35 (determinism-theorem parameters) remains upstream of any trace-level proof;
  R-CORE-14's atomic-section rule is exactly the shape of fact the theorem's
  `SchedulerTrace` needs from the effect boundary.
