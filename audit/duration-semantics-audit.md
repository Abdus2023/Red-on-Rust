# Duration–Time Semantics Audit (U-01 / U-07 / U-36) — evidence matrix (2026-09-03)

**Status:** AUDIT — identification only. No frozen text is issued here
(R-SCOPE-03); every recommendation is a proposal until Addendum IX freezes it.
Companion: `audit/u01-duration-scoping.md` (scoping; D1–D8), `audit/u36-u37-proposals.md`
§U-36 (Lifetime retype draft), `audit/resource-accounting-audit.md` (R-BUDGET-12 proposal).
**U-38 is completely out of scope.** Registers: this pass files **C-112…C-115**
(C-110/C-111 are the mutation harness's K01/K02 fixtures — reserved, unavailable).


**Adopted 2026-09-03 by addendum IX** (owner decision, `audit/spec-addendum9-draft.md`): D1–D3/D3a/D6/D8 frozen as R-CAP-11, R-BUDGET-15, R-BUDGET-16; D7's §5(c) minimal rule frozen exactly as stated (separate `QuiescenceReconcile` driver transition, scoped to `Deadlock ∧ ∃Pending`; unconditional quiescence reconciliation rejected); C-100 and C-112…C-115 re-graded `resolved-by-addendum`; U-01/U-07/U-36 resolved; the §2 sweep's rows now carry their adopted δ_t values as frozen text. U-38 untouched.

**Owner pre-adoption decisions (2026-09-03), recorded here:** D1 APPROVED
(per-actor remaining execution-duration budget distinct from absolute deadline W);
D2 APPROVED (ΔD := δ_t for time-advancing transitions; explicit no-double-charge;
`cost_C(E)`'s duration component is declared/diagnostic, never a second debit
authority); D3 APPROVED (DET-008 minimal table, exhaustive enumeration — refined in
§3 as D3a); D6 APPROVED (DeadlineExceeded with zero mutation; explicit precedence;
late receipt follows reconciliation, not the normal deadline gate); D7 **CONDITIONAL**
(the audit must establish the Deadlock semantics first — §5; nothing frozen);
D8 APPROVED (fold U-36 `Lifetime → LogicalTime` retype, half-open; resolve
`max_duration` in the same pass; no broader temporal-model changes).

---

## 1. The invariant the sweep proves

> **(I1)** Every logical-time advance has exactly **one** duration debit
> (`ΔD = δ_t > 0`), and no other operation debits `D`.
> **(I2)** Every deadline-sensitive transition has a deterministic
> pre-state/post-state rule (including its failure and recovery consequences).

Today the sweep finds every row satisfying I1 *except* the rows whose δ_t is
unfrozen (issuance/receipt values), and **three** undefined rule families
violating I2: deadline-eligibility evaluation of `Pending` effects (row 8),
quiescence semantics (row 11), and late-receipt settlement (row 9). These are
exactly the addendum's content (D3a/D4/D6/D7).

## 2. Time-capable transition sweep (GAP style)

Columns: **δ_t** (proposed/adopted value) · **ΔD debit** · **t advance** ·
**W check** · **failure atomicity** · **recovery consequence**.

| # | Transition kind | δ_t | ΔD | t advance | W check | Failure atomicity | Recovery consequence | Anchors |
|---|---|---|---|---|---|---|---|---|
| 1 | Pure CEK: E-Let / E-Seq / E-If / E-Call / E-Attenuate / E-AttenuateDenied | 0 | 0 | none | n/a (t invariant preserved) | n/a (no host boundary) | none (in-memory) | L8707–8717, L8933–8975, DET-008 |
| 2 | E-RequestDenied (auth–budget–host denial) | 0 | 0 | none | n/a | budgets preserved per [15]#5/R-BUDGET-08; adjacent fuel-charge tension in v0.3 rule 9 (`C − ⟨1,0,0⟩`) noted, NOT in D scope | nothing journaled (T0 shape) | L8948–8975; R-BUDGET-08; REQ-BUDGET-032 |
| 3 | E-Send | 0 | 0 | none | n/a | n/a (marshal fault preserves) | message in mailbox/snapshot (U-02) | L8789–8791, L26004 |
| 4 | E-Receive (dequeue) | 0 | 0 | none | n/a | n/a | dequeue reflected in snapshot/L | L8792–8795 |
| 5 | E-ReceiveBlocked → `Blocked(K)` | 0 | 0 | none | n/a | not a transition (terminal local state) | Blocked status restored from snapshot | L8796, L8843, L7245, L25598–25600 |
| 6 | E-Spawn | 0 | 0 | none | n/a | escrow per AMB-03/U-03 (separate) | child state/invariants in snapshot | L8780–8787; R-ACTOR-05; C-24 |
| 7 | **E-Request (issuance; host-boundary crossing #1)** | **1** | **1** | `t ← t + 1` | **`t + 1 ≤ W`** (post-advance, F5) | `t + δ_t > W` ⇒ `DeadlineExceeded`, **zero** budget/capability/escrow/reservation mutation (D6); other gates keep their precedence | success = s12–s14b atomic section (R-DUR-06/07); failure before s12 = T0 (nothing durable) | L8734–8741, L8904–8975; R-CORE-14; R-BUDGET-06/08 |
| 8 | **Pending hold / async wait (effect outstanding)** | — | 0 | none (by the actor) | **driver eligibility rule missing**: no frozen text re-evaluates each `Pending` effect's `W ≤ t` on other actors' time advances | n/a (not a transition) | durable `Issued` classifies T2/T3; W-eligibility on recovery undefined (row 14) | L25590–25594, L8978, L23462–23520; R-BUDGET-09 |
| 9 | **E-Receipt (host completion; crossing #2)** | **1** | **1** | `t ← t + 1` | **superseded as hard premise** (D6: receipt admitted; late settlement via R-RECOV-08; `t + δ_t ≤ W` quoted, not deleted) | mismatch ⇒ `ReplayCorruption`, budgets preserved (L8971–8975, R-EFFECT-06); success: charge actual, release reservation, log, resume (R-EFFECT-07) | durable completion per R-DUR-06/R-RECOV-09 order (append→sync→charge→resume) | L8763, L8978–8981; R-DUR-06/07; R-RECOV-09 |
| 10 | **Scheduler global turn** (ActorSelected) | carries the executed transition's δ_t (**no extra +1** — D3a) | same (row's ΔD) | same | same (row's check) | n/a | trace-visible (SchedulerEvent); U-35 consumes | L25560–25610, L8931 |
| 11 | **Quiescence / `GlobalStep::Deadlock` (driver event)** | **0 (proposed)** | **0** | none | none (no advance) | n/a — machine state unchanged by the Deadlock return | **frozen rule to be adopted (D7, conditional): `Deadlock ∧ ∃Pending` ⇒ deterministic driver reconciliation transition; per-Pending `Indeterminate` binding to R-RECOV-08; δ_t = 0, ΔD = 0** | L25579 (only occurrence); §5 |
| 12 | Snapshot commit (R-PERSIST-05) | 0 | 0 | no advance; **carries** `logical_time` as state | restored t re-checked on recovery (row 14 — undefined) | snapshot validity per R-PERSIST-05 (commit+digest) | restore base = snapshot t; U-02 binds encoding | L10931–10976, L26303, R-PERSIST-05 |
| 13 | WAL append / fsync (R-DUR-02/06/07) | 0 | 0 | no advance; **records carry no δ_t** | n/a | append/sync error ⇒ R-DUR-07 (pre-s12 rollback / Discard) | replay cannot reconstruct elapsed deltas — t derives from snapshot only (flagged; fold into U-07/U-02 scope) | R-DUR-06/07; L35099–35105 |
| 14 | Recovery replay (R-RECOV-03/09) | 0 | 0 | `t` := snapshot's `logical_time`; no journal deltas | `t ≤ W` revalidation on restored state undefined | no partial repair (R-RECOV-03; supervisor may not silently mutate — L26931) | next_effect_id reconstruction (R-RECOV-09); D restored with machine state (U-02) | L27742, L28345, R-RECOV-03/09 |
| 15 | Reconciliation (R-RECOV-08, R-RECOV-09; live and recovery) | 0 | 0 | none | n/a | no re-execution; per-class admissible outcomes; escrow only per admissibility table | durable outcome record (`EffectReconciled` L35132) | R-RECOV-08/09; L26241, L26751, L33926 |
| 16 | Host-failure consumption/refund (C-23 rule, Op-19) | 0 | 0 | none (host ceased; no boundary crossing) | n/a | escrow moves per R-BUDGET-10/11, conservation holds | durable record per R-DUR-06/R-RECOV-08 | R-BUDGET-10/11; C-23; L25808–25825 |

**D3a — refinement of DET-008's wording (required for coherence):** DET-008's
"`+1` per scheduler turn" and "`+1` per host round-trip" cannot both be literal:
a turn executes exactly one transition whose own δ_t is the charge (L8931,
L25560–25610), and a host round trip is **two** boundary crossings (issuance
dispatch, completion receipt — each `δ_t > 0` per L8734 and L8978; DET-008's
round-trip shorthand is read as *per crossing*). The frozen table therefore
reads: pure CEK 0 · issuance +1 · receipt +1 · spawn/send/receive 0 ·
blocked-holds 0 · scheduler-turn charge = the executed transition's δ_t ·
reconciliation/quiescence-driver 0. Total per host round trip = +2 logical
ticks, and per-effect elapsed logical cost = `δ_t(req) + δ_t(receipt) = 2`.

## 3. Findings (filed with this pass in `spec/06`)

### C-112 — quiescence clock hole (BLOCKING)
"The frozen liveness bound of R-BUDGET-09 is unreachable in a quiescent live
machine: `step_global` returns `GlobalStep::Deadlock` when the runnable queue
is empty, `Pending` actors are not requeued, and `logical_time` advances only
while an actor steps — a single outstanding `Pending` effect freezes `t`, so
`W` can never expire as the bound requires." Evidence: L25566–25579,
L25590–25594, L10414–10415, L8978; `GlobalStep` never declared; no frozen
driver rule consumes the `Deadlock` return; R-CAP-09 forbids the wall-clock
fallback. BLOCKING per the owner's conditional — the audit confirms there is
no other trigger.

### C-113 — late-receipt rule gap (MAJOR)
"A post-deadline `EffectReceipt` makes the frozen `E-Receipt` rule
inapplicable: the premise `t + δ_t ≤ W` (L8978) has no defined failure — neither
fault, admission, nor reconciliation." Evidence: L8978 vs E-ReceiptMismatch
(L8971–8975); anticipated by L21868 (completion-time violation); R-BUDGET-09 /
R-RECOV-08 / R-DUR-06 shape the late-settlement reading.

### C-114 — three inconsistent `D` debit models (MAJOR)
"[15]-#4 (host/scheduler transitions consume `ΔD`), v0.3 E-Request (D consumed
at effect initiation via `cost_C(E)`'s `ΔD`), and the E-ReceiveBlocked note (no
budget while blocked) against the R-BUDGET-12 proposal (async waits debit `D ←
D − δ_t`) — with no value or derivation for `ΔD` (VU-02; AMB-01 blocking)."
The adopted model: ΔD := δ_t, exactly one debit per advance, mailbox-blocked
waits charge nothing (deadlines must not become a function of message volume).

### C-115 — `DeadlineExceeded` firing/precedence unfrozen (MINOR)
"The variant exists in the closed fault surface (R-CALC-06, R-BUDGET-02) but no
rule pins where it fires or its precedence relative to budget insufficiency and
host-policy denial." Adopted: fires on any transition that would establish
`t + δ_t > W`, zero mutation, precedence ordered
`CapabilityViolation → BudgetExhausted → DeadlineExceeded → HostPolicyDenied`
(after the auth/ceiling gates; the [15]#13 chain gains the deadline member).

## 4. The invariant under the adopted rules

Rows 7 and 9 (the only δ_t > 0 rows) each carry exactly one ΔD = δ_t debit
(I1), and rows 1–6, 10 (as D3a), 12–16 are δ_t = 0 with zero D mutation.
I2 holds if the addendum freezes: (a) `DeadlineExceeded` with zero mutation +
precedence (row 7/2); (b) **deadline-eligibility evaluation** — on every global
time advance, each `Pending` effect's `W ≤ t'` is evaluated and expiry binds it
to `Indeterminate` + R-RECOV-08 (row 8 — new driver rule); (c) **late receipt
settlement** — admission + R-RECOV-08 classification, `t + δ_t ≤ W` quoted
superseded (row 9); (d) **quiescence reconciliation** — §5 (row 11);
(e) **D-exhaustion** — when the next time-advancing transition of an actor
would make `ΔD > D`, the transition faults `DeadlineExceeded` for that actor
with zero mutation (D-backed per-actor bound, independent of global progress).

## 5. D7 — the `Deadlock` semantics, established by this audit

**Q1. Can `Pending(E)` survive `GlobalStep::Deadlock`? — YES.** The
`Deadlock` return occurs before any state mutation (L25579 returns from an
empty-queue match); the actor remains in `GlobalState.actors` with
`ActorStatus::Pending` (L25535–25556). Quiescence is a *state*, not a
destruction.

**Q2. Can external completion subsequently make progress? — NOT DEFINED.**
No frozen text consumes the `Deadlock` return: `GlobalStep`'s declaration is
absent from L1–42312, no driver loop is shown (only the outline at L10391 and
L11094 — "outer loop calls host.execute" — and the actor-level resume path
L20356), and the machinery sits inside the unfrozen GlobalState-shape family
(C-73/U-34, and shapes L9497/L10377/L10931/L22035/L23138/L23293 which U-02
binds). So "no runnable actor" is **not necessarily terminal deadlock**: intent
allows a later receipt to resume the actor, but the driver protocol is
unfrozen.

**Q3. Which reconciliation trigger is the minimal one?**

- (a) *Unconditional at quiescence* — total and deterministic, but wider than
  needed: it would also fire on Blocked-only quiescence (no escrow at stake)
  and races a host that is about to complete. Safe under R-RECOV-08 (the
  receipt then settles a reconciled effect) but not the weakest.
- (b) *Only for deadline-eligible effects* — **does not work**: with `t`
  frozen at quiescence no expiry is computable, so the bound remains
  unreachable. Rejected by this audit on the evidence in C-112.
- (c) *A separate deterministic driver transition* — the recommended shape:
  `deadlock ∧ ∃Pending ⇒ QuiescenceReconcile`, a driver-owned transition with
  `δ_t = 0`, `ΔD = 0`, no W check, no budget mutation, which for every
  `Pending` effect records `Indeterminate` and binds it to the R-RECOV-08
  admissible-outcome protocol (never re-executes; late receipt evidence later
  settles via R-RECOV-08 + R-HOST-06 + R-DUR-06). This is the **weakest rule
  that makes R-BUDGET-09's liveness bound reachable**: it adds no clock, no
  timer, no per-effect counter, and it fires only where the machine would
  otherwise strand escrow.

**Conclusion (to freeze only after owner confirmation):** adopt (c), scoped to
`Pending`-bearing quiescence, worded as *stable quiescence* (not "terminal
deadlock"), and record that the driver's receipt-resumption path is a separate
frozen protocol matter (runs alongside, still in U-01's scope note but not part
of this rule).

## 6. Addendum IX preview (non-authoritative)

Freeze **R-BUDGET-15** (duration consumable semantics: per-actor D, ΔD := δ_t,
no-double-charge, exhaustion ⇒ DeadlineExceeded, `cost_C(E)` duration component
declared/diagnostic only), **R-BUDGET-16** (logical-time delta table: D3a
enumeration + deadline-eligibility evaluation + late-receipt settlement +
quiescence reconciliation per §5(c)), and **R-CAP-11** (Lifetime → LogicalTime,
half-open, five annotations superseded-quoted per `audit/u36-u37-proposals.md`
§U-36; `max_duration` declared-duration information only, never a machine
debit; `Deadline` confirmed `Option<LogicalTime>` in all three declarations —
no retype needed there). Resolves U-01, U-07, U-36 (lifetime half); folds
R-BUDGET-12's rule into R-BUDGET-15/16 (still no R-BUDGET-12 ID); files
C-112…C-115 open → re-grades to resolved-by-addendum at adoption; updates
AMB-01/VU-02; U-37/U-35/U-02/U-03/U-08/U-09/U-38 untouched; mutations M040–M042
and tags as scoped in `u01-duration-scoping.md` §6.

## 7. Non-goals

U-38 (severity wiring) · U-02 (canonical machine-state encodings; consumes only
`LogicalTime`'s `u64` width) · U-35 (trace equality; consumes the frozen table)
· U-37 (widths) · U-03 (spawn allocation) · U-31/U-34 (Authority/GlobalState
shape selection) · reopening C-104/R-CORE-14's predicate form · any wall-clock
temporal model (R-CAP-09; R-CLAIM-02) · R-BUDGET-14.
