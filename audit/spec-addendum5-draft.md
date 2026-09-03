# Addendum V — final freeze (SEC-013 / 014 / 015 / 019 / 021) — register closed

**Status: APPLIED** via `audit/spec_addendum5.py --apply` (adoption commit on
`arena/01a063c4-red-on-rust`; post-apply verification on the real tree:
173 obligations / 173 matrix rows / 148 records, `spec/_check.py` D1=0 exit 0
(warnings identical to the pre-apply set), index rebuilt at 173/96/35/19,
`req/_validate.py` exit 0 / ERRORS 0, applier idempotency guard armed). With
adoption, **all 23 audit findings are frozen at the specification level**.
This file is retained as the review record of exactly what was adopted and
why; rollback is `git revert` of the adoption commit. The exact edit set
lives in `audit/spec_addendum5.py` (this draft was generated from its
constants, so the two cannot drift); its dry run is full-fidelity — a
`git archive` sandbox of HEAD receives the edits and the entire verification
stack (`audit/spec_check.py`, `spec/_build_index.py`, `req/_validate.py`)
runs there.

## 1. What this freezes (report §6 item 8)

| Addendum | Freezes | Extends / resolves |
|---|---|---|
| `R-ARCH-05` | SEC-013: isolation posture decided — ladder retired (U-05); in-process structural isolation the frozen minimum with the residual risk (host compromise = machine compromise) recorded in the trust model; out-of-process host adapter (canonical-bytes crossing) required where host code is not fully trusted; in-process executors testkit-only in production | extends R-ARCH-03/R-TRUST-01/R-CORE-12; resolves C-93 |
| `R-CAP-10` | SEC-014: `AdmissibleConstraint` defined — decidable well-formedness per domain (O/S/Q/R/T); `¬AdmissibleConstraint(C) ⇒ fault`, never identity (⊤-default forbidden); compile-time validation of attacker-authored constraints; `InvalidConstraint` in the closed enumeration | extends R-CAP-04/05, R-COMPILE-02/03/06; resolves C-94 (AMB-12/U-09 admissibility); M030 |
| `R-KERN-06` | SEC-015: root-grant protocol — `Grant(source, authority, ceiling, t)` with a durable `CapabilityGranted` record under the deployment ceiling; root minted once at initialization; `Supervisor.host` removed or issued-effect-only (R-HOST-02 binds every caller); planner I/O structurally crate-separated | extends R-KERN-01/R-HOST-02/R-PLANNER-02/R-TRUST-05; resolves C-95 |
| `R-ACTOR-10` | SEC-019: mailbox resource admission — enqueue requires recipient capacity (M reservation; `ReservedCapacityExceeded` faults the sender, sender pays); payload-proportional send cost over canonical length; constructed-size bound; footprint ≤ reserved M | extends R-ACTOR-06/R-BUDGET-01/R-EFFECT-04; resolves C-96 (U-03/U-07 direction); M033 |
| `R-BUDGET-09` | SEC-021: escrow disposition totality — every escrowed unit exits via exactly one frozen path; live faults unified with crash reconciliation; logical-time deadline bound ⇒ `Indeterminate` + reconciliation (machine state only); no quiescent strand | extends R-DUR-05/R-EFFECT-05/R-RECOV-08; resolves C-97; M035 |
| `C-93…C-97` (spec/06) | security consequences registered (MAJOR ×5), all `resolved-by-addendum` | rows after C-92 |
| `M030`, `M033`, `M035` (spec/08) | kill targets; registry now complete M001–M035 | title updated |

## 2. Exact normative texts (spec/01 insertions)

**R-ARCH-05 (isolation posture — frozen addendum).** The isolation ladder (U-05) is RETIRED by decision: the frozen minimum posture is in-process structural isolation (type safety, `#![forbid(unsafe_code)]`, the crate DAG, panic-free machine paths per R-CORE-12), and the residual risk — host compromise is machine compromise: same address space, memory adjacency to `GlobalState`, the kernel arena, and the revocation set — MUST be recorded in the trust model as accepted, not implied away by behavioral containment claims. For any deployment where host code is not fully trusted, the out-of-process host adapter is the REQUIRED mode: effects and receipts cross as canonical bytes only (the wire format already frozen, R-CANON-13). In-process `Box<dyn HostExecutor>` is testkit-only in production configurations (`PanicHost`/`MockKernel` doubles); production `ror-host` MUST NOT link `ror-runtime` internals beyond the adapter trait — a hard dependency/visibility gate. An untrusted agent's isolation level may never be weaker than its spawner's own. *(Frozen addendum — post-audit remediation SEC-013; additive per R-SCOPE-03; extends R-ARCH-03/R-TRUST-01/R-CORE-12; resolves C-93, retiring U-05; no source transcription.)*

**R-CAP-10 (`AdmissibleConstraint` defined — frozen addendum).** `AdmissibleConstraint` is DEFINED: decidable well-formedness per semantic domain — operation set `O` nonempty and within the parent's interpretation, scope constraint `S` interpretable, predicate `Q` closed over params, resource ceiling `R` within the parent's, lifetime `T` a satisfiable interval. The derivation law is total on admissible inputs only: `¬AdmissibleConstraint(C) ⇒ ¬∃c'. derive(A,C) = c'` — `derive(A, C)` MUST fault (`Fault::InvalidConstraint`, in the R-CORE-13 closed enumeration; the `Invalid`-variant drift C-56 is resolved there), never identity: the ⊤-default reading (inadmissible constraint silently ignored, `derive(A, C_garbage) = A`) is FORBIDDEN. Constraints are attacker-authored (authored inside untrusted `Block`s: `Attenuate`, spawn manifests per R-ACTOR-09, `Delegate` per R-MARSHAL-05): the compiler MUST validate constraint admissibility at compile time (extends R-COMPILE-02/03) before any kernel call. Property: `derive` with an inadmissible constraint never returns a CapRef, across the full generated constraint space. *(Frozen addendum — post-audit remediation SEC-014; additive per R-SCOPE-03; extends R-CAP-04/R-CAP-05/R-COMPILE-06; resolves C-94, closing AMB-12/U-09's admissibility clause; mutation M030; no source transcription.)*

**R-KERN-06 (root-grant protocol — frozen addendum).** Authority enters the machine ONLY through the frozen grant protocol: `Grant(source, authority, ceiling, t)` MUST produce a durable `CapabilityGranted` record (the R-PERSIST-07 event kind) and the authority MUST stay `≼` the deployment ceiling; root authority is minted exactly once, at machine initialization, by the deployment — no runtime minting path exists. `Supervisor.host` is REMOVED from the `Supervisor` struct, or typed as an issued-effect-only handle: R-HOST-02 (host performs only issued effects) binds EVERY host caller, not only the machine — `HostInvoked ⇒ DurableIssued` with no exception for supervisor or integration code. Planner-facing I/O MUST be structurally separated from supervisor/runtime/compiler handles (the `ror-planner-io` split: the untrusted side emits `PlanProposal` data only, no compiler/runtime edges) — no crate containing LLM/planner I/O may depend on `ror-compiler` or `ror-runtime`. Audit test: every live root authority in a recovered arena traces to a durable `CapabilityGranted` record. *(Frozen addendum — post-audit remediation SEC-015; additive per R-SCOPE-03; extends R-KERN-01/R-HOST-02/R-PLANNER-02/R-TRUST-05; resolves C-95; no source transcription.)*

**R-ACTOR-10 (mailbox resource admission — frozen addendum).** Mailbox admission is resource-gated: `Enqueue(v, target)` requires available recipient mailbox capacity — capacity is part of the recipient's `M` reservation — and on denial the SENDER faults with `ReservedCapacityExceeded` (sender pays; never silent growth). The send cost MUST be payload-proportional: `cost_C(send) ≥ f(canonical_len(v))` for a frozen monotone `f` bounded away from zero per byte (deterministic over canonical bytes, replay-stable). Constructed value size is bounded against the constructing actor's `M` reservation (allocation is the resource the reservation exists for). Invariant: for any reachable state, the total mailbox footprint is bounded by total reserved `M` at every step — the resource-bounded thesis holds in the heap, not only in the algebra. *(Frozen addendum — post-audit remediation SEC-019; additive per R-SCOPE-03; extends R-ACTOR-06/R-BUDGET-01/R-EFFECT-04; resolves C-96, closing the U-03/U-07 resource-admission direction; mutation M033; no source transcription.)*

**R-BUDGET-09 (escrow disposition totality — frozen addendum).** Escrow disposition is TOTAL: every unit entering the escrowed partition eventually leaves via exactly one frozen path — `Completed` (actual ≤ `complete_max` charged, remainder released), host-failure consumption (the C-23 rule), or durable `Reconciled` (R-RECOV-08). Held-forever-in-a-live-machine is NOT a disposition. Live faults unify with crash reconciliation: an actor fatal fault with an open effect enters the same reconciliation protocol as post-crash `Indeterminate`, and the supervisor fatal-fault policy MUST reference it. A logical-time bound moves stalled effects to reconciliation: a `Pending` effect whose deadline `W` expires (or a frozen per-effect logical timeout elapses) transitions to `Indeterminate` + reconciliation — machine state only, no wall clock (R-CAP-09), determinism preserved. Invariant: no reachable quiescent machine state contains escrow that no frozen rule can move; `C_available` shrinks only via `consumed` or durable `Reconciled`, never by strand. *(Frozen addendum — post-audit remediation SEC-021; additive per R-SCOPE-03; extends R-DUR-05/R-EFFECT-05/R-RECOV-08; resolves C-97; mutation M035; no source transcription.)*

## 3. Companion edits

spec/03 (+5 rows, Total **173** = 148 + 25 addenda), spec/06 (+C-93…C-97),
spec/08 (+3 mutation rows; registry title M001–M035), records scope note,
README (173 IDs), `spec/_build_index.py` (sections S-04/09/10/11/15, rows,
mutations, milestones M4/M5/M6, crates kernel/runtime/agent, id-scheme counts
173/35), `req/_validate.py` (recorded register growth 92 → 97 raw C-rows).

## 4. Verification record (pre-apply, full-repo sandbox)

- Precheck: addendum ABSENT (all 8 markers), 40 anchors intact.
- Sandbox (git archive of HEAD + edits): obligations/matrix/records =
  173/173/148; `spec_check` parses 148/173/173, D1=0, no FAIL, zero warnings
  on the five new obligations; warning count identical to HEAD (35 — no
  relocation artifacts this time); index rebuild
  `requirements=173 findings=96 mutations=35 tags=19`;
  `req/_validate.py` exit 0, ERRORS 0.
- New-row body↔matrix D3 overlaps: R-ARCH-05 0.82, R-CAP-10 0.89, R-KERN-06
  0.78, R-ACTOR-10 0.88, R-BUDGET-09 0.88.

## 5. Adoption procedure

1. `python3 audit/spec_addendum5.py` — re-run the full-sandbox proof.
2. `python3 audit/spec_addendum5.py --apply` — 40 edits across 8 files; every check re-runs on the real tree in-step.
3. `python3 spec/_check.py` — gate must exit 0; `git revert` is the rollback.

Generated from `audit/spec_addendum5.py` constants — 2026-09-03.
