# U-01 / Duration–Time semantics — scoping pass (2026-09-03)

**Status:** SCOPING ONLY. No normative layer, register, or generated witness is
changed by this document (R-SCOPE-03: audits identify; only a future addendum
adoption makes correction normative). **U-38 is out of scope.** No finding row
is filed here; the candidate findings below (C-112…C-115) are listed for the
D-semantics pass to file together with their adoption, exactly as the
request-pipeline audit filed C-103…C-109 alongside its addendum.

**Adopted 2026-09-03 by addendum IX:** the D1–D8 recommendations in this
document are the frozen semantics (`R-CAP-11`, `R-BUDGET-15`, `R-BUDGET-16`;
U-01/U-07/U-36 resolved; C-100/C-112…C-115 re-graded). This document remains the
scoping record; its wording is quoted, not rewritten (R-SCOPE-03).

**Scope:** the semantic cluster U-01 exposes — what `D` measures, when `D` is
debited, what `δ_t` is per transition, how logical time advances, the deadline
predicate, and the Yield / async-wait / EffectRequest interaction — including
the frozen `t + δ_t(req) ≤ W` predicate's operands (not its form, which
R-CORE-14 already froze: C-104 / U-40 resolved).

**Feedback loop already on record:** U-01 (spec/09), U-07 (spec/09, amended by
DET-008), U-36 (spec/09; `audit/u36-u37-proposals.md` §U-36), U-40's resolution
explicitly says the δ_t table and the Lifetime interaction must be decided
"in the same pass" as the operands become evaluable; U-45's adoption folded
R-BUDGET-12 (the resource-accounting audit's D-advancement rule) into U-01.

---

## 1. What is already frozen (no re-opening)

| # | Frozen fact | Anchor |
|---|---|---|
| F1 | `B = ⟨C, R, W⟩`; `C = ⟨F, I, D⟩` (fuel, I/O, **duration**); `R = ⟨M, S⟩`; `W ∈ ℕ ∪ {∞}` absolute logical-time deadline; `Deadline(None)` = ∞ | spec/01 R-BUDGET-01; src L8671–8673, L8892–8894, L9140, L10204, L10689 |
| F2 | Consumables strictly decreasing, never returned | R-BUDGET-01; src L7414, L7138–7139 |
| F3 | Deadline checked against logical time, not wall-clock; host clock never read | R-BUDGET-01; R-CAP-09; src L6437, L5853; R-CLAIM-02 |
| F4 | Every transition has `δ_t(c) ∈ ℕ`; pure `δ_t = 0`; host interactions and scheduler steps `δ_t > 0`; valid only if `t + δ_t(c) ≤ W` | R-BUDGET-06; src L8692–8700, L8915–8916 (TimeOK), L7662–7693 ([15] fix) |
| F5 | Step-10 (issuance) predicate is the post-advance form `t + δ_t(req) ≤ W`; the pre-advance `t ≤ W` reading is SUPERSEDED (C-104); `R-EFFECT-01` step (7) and REQ-EFFECT-012 still present the superseded form | R-CORE-14; spec/06 C-104; spec/09 U-40 resolution |
| F6 | `HostInvoked(E) ⇒ DurableIssued(E)`; 16-step master-prompt order governs | R-CORE-14, R-EFFECT-01/03 |
| F7 | Logically time-advancing faults preserve budgets; no partial debit | R-BUDGET-08; src L7352, L8948 |
| F8 | `W` and D are **distinct bounds**: `Deadline` (W) vs duration (D); the letter `D` is never used for a deadline (N-18; X-12 overload with durable state `D` recorded, prose must disambiguate) | term/02 X-12 (§L597), N-18 |
| F9 | `LogicalTime(pub u64)`; `Deadline(pub Option<LogicalTime>)`; global `logical_time` in `GlobalConfig`/`MachineState`; per-actor `budget.deadline` | src L9137, L9140, L9497, L10377, L10931, L9175, L10242, L10717 |
| F10 | Blocked receive / pending effect: `δ_t = 0` while blocked, "no budget is consumed while blocked" (E-ReceiveBlocked note); actor not requeued while `Pending`/`Blocked`; `step_global` returns `GlobalStep::Deadlock` when no runnable actor exists | src L8796, L8978 (receipt δ_t>0), L25566–25579, L10387–10388 |
| F11 | Fault surface includes `DeadlineExceeded` (`Fault::DeadlineExceeded`; `BudgetError::DeadlineExceeded`) but no rule pins *where it fires* | R-CALC-06, R-BUDGET-02; R-CALC-06 (src L23784–23819); R-BUDGET-02 (src L9207–9245) |
| F12 | R-BUDGET-09 liveness bound: `Pending` effect whose `W` expires (or a **frozen per-effect logical timeout** — undefined) → `Indeterminate` + reconciliation | R-BUDGET-09 (addendum V; C-97) |
| F13 | `RessourceLimits.max_duration: std::time::Duration` inside `ResourceLimits`; `Lifetime {start,end}` annotated `// Unix timestamp` five times, consumed by `auth.lifetime.contains(t: LogicalTime)` at gate 6 (two call sites L3577/L6558) | src L5399, L3571–3573, L4959–4961, L5403–5405, L5244, L11881–11889, L6558; U-36 |

## 2. The open questions (the subtree)

```
U-01  DURATION semantics
 ├─ D1  what D measures                          (AMB-01 readings a/b; [15] #4; Option B)
 ├─ D2  when D is debited / ΔD value+derivation  (VU-02; R-BUDGET-12; L8835 vs L8967 vs L8796)
 ├─ D3  δ_t per-transition table                 (U-07; DET-008 minimal table exists as audit rec.)
 ├─ D4  δ_t(req) value (operand of frozen F5)    (U-40 resolution leaves operands open)
 ├─ D5  logical-time advancement model           ([15] #3: "one model must be chosen"; rec. scheduler/host time)
 ├─ D6  deadline predicate machinery             (where DeadlineExceeded fires; late-receipt rule; E-Receipt premise L8978)
 ├─ D7  Yield / async wait / EffectRequest       (Pending vs Blocked; quiescence clock; per-effect timeout)
 └─ D8  Lifetime & max_duration interaction      (U-36; U-40: same pass; u36-u37-proposals §U-36)
```

Also in the loop (consumers, not re-opened): U-35 (SchedulerTrace shapes carry
`logical_time` — trace semantics need a frozen clock rate), U-02 (canonical
state digest includes `LogicalTime`), U-37 (widths: `LogicalTime(u64)` fine),
U-03/U-08/U-09/U-38 out of scope.

## 3. Evidence inventory (verified this session)

**Source (`Red-on-Rust.md`):**
- L6753–6790: v0.1 cost algebra `ΔB = ⟨ΔF,ΔM,ΔC,ΔI,ΔW⟩` (5-dim; `W` as delta) — historical, superseded (C-06).
- L7119–7144: v0.2 `C=⟨F,I,D⟩`, `R=⟨M,S⟩`, `W ∈ ℕ∪{∞}`, `t ≤ W` (L7141).
- L7130, L7303, L7414: the consumables triple; "strictly consumed, never returned".
- L7650–7704 (**[15] item 3**): time never advanced → "deadline currently decorative" (L7662); fix: `δ_t(c) ∈ ℕ`, `t' = t + δ_t(c)`, boxed `t + δ_t(c) ≤ W`; example `E-Let: t' = t+1` **or** pure `δ_t = 0` + host/scheduler advances; "Either is valid. **But one model must be chosen.**" (L7697); recommendation: logical time = explicit scheduler/host time, *not* one unit per VM instruction ("fuel already accounts for computation. Otherwise fuel and time become redundant." L7698–7701).
- L7706–7750 (**[15] item 4**): "Duration `D` currently has no operational semantics" (no rule consumes it; rules consume `⟨1,0,0⟩`). **Option A** remove D (`C=⟨F,I⟩`); **Option B** retain D: `D' = D − Δt` (L7739); recommendation: retain to distinguish computational fuel / I/O volume / duration; "absolute deadline" (W) listed separately.
- L8632 ([15] freeze table): "Explicit logical time ✅ Freeze, but define advancement"; "Duration `D` 🔧 Give operational meaning".
- L8679, L8904: `cost_C(E) = ⟨ΔF, ΔI, ΔD⟩` — **D appears as a component of per-effect cost**.
- L8692–8700 (v0.3): `δ_t(c) ∈ ℕ`; pure 0; host/scheduler >0; validity `t + δ_t(c) ≤ W` (the R-BUDGET-06 source).
- L8707–8796 (v0.3 rules): E-Let/E-Seq/E-If/E-Call/E-Attenuate(`t + δ_t(att)`), E-Request `t + δ_t(req) ≤ W` (L8734) and `t ← t + δ_t(req)` (L8741); E-Receipt (L8978): `δ_t > 0`, `t + δ_t ≤ W`, `C - cost_io(receipt.result)`; E-ReceiveBlocked (L8796 note): `δ_t = 0`, no budget consumed while blocked; E-Send/E-Spawn/E-Receive with `δ_t` (8783–8792).
- L8835 (**[15] #4 resolution**): "`D` is part of `C`. Host/scheduler transitions consume `ΔD`, giving it operational meaning." (no value/derivation → VU-02).
- L8915–8916: restated time rule + `TimeOK(t, δ_t, W) ⇔ t + δ_t ≤ W`.
- L8967: v0.3 restatement of E-Request: "Duration `D` is consumed from `C` here **as the effect is initiated**" (i.e., via `cost_C(E)`'s ΔD at issuance).
- L9140/L10204/L10689: `Deadline(pub Option<LogicalTime>)`; L9137 `LogicalTime(pub u64)`.
- L10056–10075 ("final formal adjustment"): the source itself lists the **unstated laws**: `δ_t`, `HostPolicyOK`, `marshal`, `AdmissibleConstraint`, `cost_C`, `cost_R`, **and the scheduler transition relation** — interface contracts, not design holes.
- L10152: `fn delta_t(&self) -> u64;` (TimeAdvancement contract).
- L10414–10415: `machine.logical_time.0 += actor.expr.delta_t();`; L10974–10976: `if machine.logical_time > deadline { ... }`; L11072: step-8 check.
- L21852–21870: deadline freeze: `t_now ≤ W` before issuance; **recommended only if trustworthy**: `t_now + Δt_expected ≤ W`; otherwise "enforce request-time deadline and treat an overlong host completion as a completion-time deadline violation"; "Do not pretend an untrusted host duration prediction is deterministic."
- L25566–25579: scheduler: one machine transition per turn; `None => Ok(GlobalStep::Deadlock)` when **no runnable actors**; Pending actors not requeued (L25591–25595).
- L2354: "Budget monotonicity does not by itself guarantee termination … unless every transition has a strictly positive well-founded cost **and external waits are separately bounded**."
- L3030–3095: well-founded measure `M(Σ) = ⟨B_fuel, B_host, B_msg, B_io, B_mem, B_time, N_pending⟩`; "suspended states are not executable transitions"; "`receive` can wait forever for a message" ⇒ only **finite active computation**.
- L2322/L4037 (A3): receive-on-empty options — block/suspend, fault, or **timeout parameter**; each "has different implications for the budget model" (the timeout option was not taken; the frozen choice is block).
- L5399: `ResourceLimits.max_duration: Duration` (std::time) — declared-duration-bearing ceiling; L5403–5409 `Lifetime` with second annotation; L5424? prose "e.g., Unix timestamps" L5244.
- L3571–3573, L4959–4961: `Lifetime` Unix annotations; L3577 `contains(&self, time: u64)`; L11881–11889 (gate 6 use); L6558 second call site.

**Terms / records / findings:**
- X-12 (`D` overload: durable state vs duration consumable — MAJOR, sees U-01); X-42 (`LogicalTime` glossed "a logical clock or deterministic timestamp" — forbidden prose; canonical = "logical time"; R-CAP-09; R-CLAIM-02); N-18 (deadline vs duration distinct; `t + δ_t ≤ W` named THE deadline check).
- U-01 (open, BLOCKING for budget semantics — mod/04); U-07 (open, "the actual delta values are not enumerated"; amended by DET-008: do **not** take the "any consistent assignment" escape (R-CORE-08→per-implementation, R-REF-01 breakage); `t` read by gate 8 and gate 6; R-BUDGET-09 liveness now rests on an unfrozen clock rate; minimal defensible table: pure CEK 0, +1 scheduler turn, +1 host round-trip, 0 spawn/send/receive, **every** transition kind enumerated).
- U-36 (open; BLOCKING; retype Lifetime → LogicalTime, half-open `[start,end)`, five annotations quoted-superseded; `max_duration` must be resolved **together with U-01**; drafted proposal `audit/u36-u37-proposals.md` §U-36, NOT adopted; second call site L6558).
- AMB-01 (req/03): two readings — (a) fixed per-effect budget with frozen ΔD, (b) caller-specified ΔD policy parameter; **no value or derivation for ΔD**; blocking: yes (exhaustion not testable).
- VU-02 (req/04): REQ-BUDGET-008 — no ΔD value/derivation, exhaustion behavior undefined; blocks deadline-exhaustion tests; "no mutation targets it".
- REQ-BUDGET-004 (W absolute deadline; `Deadline(None)` = ∞), REQ-BUDGET-007 (deadline vs logical time, not wall clock), REQ-BUDGET-008 (AMBIGUOUS D), REQ-BUDGET-021 (`∀ active steps i: t_i ≤ W`; L7408–7425), REQ-EFFECT-012 (`t ≤ W`, superseded reading), REQ-EFFECT-037 (deadline validation; AMB-01-affected).
- C-06 (dimension drift, resolved-by-later-text), C-104 (step-10 predicate, resolved-by-addendum → R-CORE-14), C-97 (escrow totality, resolved-by-addendum → R-BUDGET-09).
- spec/09 U-40 resolution: "The per-transition δ_t table remains open (U-07) — the predicate is now decided, its operands are not."
- Resource-accounting audit R-BUDGET-12 (proposal, NOT frozen; folded into U-01 by addendum VIII): "Scheduled yield steps and async waiting steps advance logical time `t_{i+1} = t_i + δ_t` and debit `D ← D − δ_t`."

## 4. Candidate findings for the D-semantics pass (unfiled)

- **C-112 — quiescence clock hole.** `step_global` returns `Deadlock` when no runnable actor exists (L25579); Pending/Blocked actors are not requeued; `logical_time` advances only when some actor is stepped (L10414–10415). Therefore in a quiescent live machine a `Pending` effect's `W` **can never expire** — R-BUDGET-09's "deadline `W` expires ⇒ `Indeterminate` + reconciliation" bound is unreachable via `t` alone, and its "frozen per-effect logical timeout" is undefined. Severity: MAJOR — arguably **BLOCKING**: R-BUDGET-09's own liveness claim rests on the bound; C-97-adjacent but not recorded.
- **C-113 — late-receipt rule gap.** `E-Receipt` requires `t + δ_t ≤ W` (L8978); a receipt arriving after the deadline makes the rule inapplicable — undefined transition (neither fault, nor acceptance, nor reconciliation). The frozen R-BUDGET-09/R-RECOV-08 shape suggests the settlement should proceed via reconciliation regardless of `t`; no text says so. Severity: MAJOR.
- **C-114 — three inconsistent D models.** (i) [15] #4 (L8835): host/scheduler transitions consume ΔD; (ii) v0.3 E-Request note (L8967): D is consumed at effect initiation as part of `cost_C(E)`'s ΔD; (iii) E-ReceiveBlocked note (L8796) + R-BUDGET-12 proposal: blocked waits advance time and debit D yet "no budget is consumed while blocked" / δ_t = 0. No single model is derivable; ΔD has no value or derivation (VU-02). Severity: MAJOR (or the pass may re-grade as one AMB-01 family note instead of a contradiction; adjudicate at filing).
- **C-115 — DeadlineExceeded firing point unfrozen** (or folded into F11): the fault variant exists (R-CALC-06/R-BUDGET-02), the frozen precedence chain (CapabilityViolation > BudgetExhausted > HostPolicyViolation) omits it, and the `[30]`-era step lists disagree about whether the deadline gate precedes host policy. Severity: MINOR/MAJOR at filing.

## 5. Decision framework (recommendations)

| DP | Options | Evidence | Recommendation |
|---|---|---|---|
| **D1 what D measures** | (a) remaining per-actor logical-time budget (rate 1:1 with δ_t; Option B, [15] #4, R-BUDGET-12) — risk: redundant with `W − t` if W is per-actor and the rate is 1; (b) per-effect declared duration balance (sum of effect ΔD's, AMB-01 (a)); (c) caller-specified policy ΔD (AMB-01 (b)); (d) retract D (Option A; `C = ⟨F,I⟩`) | L7706–7750 (source explicitly offers A/B and **recommends retaining** D to distinguish fuel/I/O/duration); N-18 (W ≠ D) | **Retain D, per-actor, as duration-budget**; its role distinct from W: `D` bounds the actor's own time-advancing activity (its budget share), `W` is the absolute gate. The redundancy concern is resolved by the per-actor/per-effect calibration of ΔD (D2) rather than by retraction. **Reject (b) as the machine debit model** for host effects: untrusted declared durations (L21870). |
| **D2 ΔD value/derivation** | ΔD := δ_t for every δ_t>0 transition (host round trip, scheduler turn); ΔD := 0 for pure/blocked; per-effect ΔD in `cost_C(E)` is the SAME quantity, charged once (at the effect's host-boundary transition), never twice | L8835, L7739, R-BUDGET-12, L8679/L8967, VU-02 | **ΔD := δ_t** (one clock rate, one unit); explicitly forbid double-charging: `cost_C(E)`'s ΔD component is *diagnostic/declared* for the optional predicted-completion check (L21863), while the machine debit follows the transition's δ_t. Freeze "D is amended only by ΔD = δ_t of time-advancing transitions; no other path debits D". |
| **D3 δ_t table (U-07)** | (i) DET-008 minimal table; (ii) any-consistent-assignment escape (rejected by DET-008 — breaks R-CORE-08/R-REF-01) | U-07 amendment | Adopt the DET-008 table with the *complete* kind enumeration: pure CEK (let/seq/if/call/attenuate/attenuate-denied/request-denied/send/receive/receipt-mismatch) 0; E-Request (issuance, host boundary) 1; E-Receipt (host completion) 1; E-Spawn 0; E-ReceiveBlocked 0; **scheduler global turn +1**; **quiescence/deadlock tick** — see D7. Every kind enumerated; unknown kinds are a checker error, not a default. |
| **D4 δ_t(req)** | 1 (host round-trip, charged at issuance per F5); ΔD_declared (rejected: untrusted); 0-at-issue + 1-at-receipt (changes F5's operand semantics — not allowed without reopening C-104) | L8734–8741, L21863–21870 | **δ_t(req) := 1** (frozen constant; one host-boundary transition). Receipt separately +1. Keep F5 form untouched. |
| **D5 clock model** | per-instruction ticks (rejected by [15] recommendation: fuel redundancy); scheduler/host time (chosen) | L7697–7701 | Confirm **scheduler/host time model** (already the read of R-BUDGET-06 + DET-008); no per-instruction counting in any obligation. |
| **D6 deadline machinery** | where DeadlineExceeded fires; late receipt | F11, C-113, L8978, R-BUDGET-09 | (a) Any transition attempting `t + δ_t > W` faults `DeadlineExceeded` with budgets preserved (extends R-BUDGET-08's shape; makes VU-02 testable); pin its precedence slot (between budget and host policy, per the 16-step order: budget gates → deadline → host policy). (b) Receipt after W does **not** make the rule undefined: settlement proceeds via reconciliation (R-RECOV-08 admissibility); `t + δ_t ≤ W` at E-Receipt is SUPERSEDED as a hard premise (quoted, not deleted) and replaced by "receipt evidence is admitted; post-deadline settlement classified per R-RECOV-08". |
| **D7 Yield/async/EffectRequest** | blocked-wait clocking; quiescence | F10, C-112, L2322 (A3), L2354, L25579, R-BUDGET-09 | (a) Blocked/Pending holds do **not** tick the global clock by themselves (F10 stands). (b) **Quiescence is the reconciliation trigger**: when `step_global` yields `Deadlock` and any effect is `Pending`, every such effect transitions to `Indeterminate` + reconciliation (deterministic, wall-clock-free, revisits R-RECOV-08's live-fault path); this is the "frozen per-effect logical timeout" R-BUDGET-09 promised — defined as *quiescence* rather than a wall-clock countdown. (c) A `Pending` effect with a non-quiescent machine keeps its W-bound (F12); host never answering while other work continues → W/δ_t bound still applies to the actor's progress? — decide at adoption: per-actor D exhaustion (D ≤ next δ_t) also faults DeadlineExceeded for that actor, giving a budget-based bound independent of global progress. |
| **D8 Lifetime/max_duration (U-36 fold)** | retype the Unix-timestamp annotations to LogicalTime; max_duration as machine-readable | U-36; u36-u37 §U-36; L5399, L5244 | Adopt `audit/u36-u37-proposals.md` §U-36 as submitted (retype `Lifetime` to `LogicalTime`, half-open `[start,end)`, five annotations quoted-superseded, second call site L6558 recorded); **R-BUDGET-12's D rule and `max_duration` semantics are decided here**; `max_duration` becomes the per-effect *declared* duration used only for the optional predicted-completion info (non-normative per L21870) — never a machine authorization debit. |

## 6. Expected pass/register shape (preview; not authoritative)

- Addendum IX freezes **R-BUDGET-15** (duration consumable semantics: D meaning, ΔD := δ_t, no-double-charge, D-exhaustion fault) and **R-BUDGET-16** (logical-time delta table: the complete kind enumeration + quiescence/reconciliation trigger + late-receipt settlement); candidates: also an R-DUR-08/R-RECOV-10 touch for receipt-after-W, or fold that into R-BUDGET-16 — name at drafting.
- Resolves **U-01, U-07, U-36** (the lifetime half, per U-40's "same pass" note); U-37, U-35, U-02, U-03, U-08, U-09, U-38 untouched.
- Folds **R-BUDGET-12** (audit proposal) into the adopted text and marks it resolved-in-place in `audit/resource-accounting-audit.md` (still no R-BUDGET-12 ID frozen).
- Files **C-112…C-115** (open → resolved-by-addendum where adopted), updates AMB-01/VU-02 (or supersedes them with the adopted rule), spec/06 addendum paragraph, README, mod/04, `_ownership.py`, registers.
- New mutations (candidate M040 δ_t table violation, M041 late-receipt misclassification, M042 D double-charge) + harness shapes (K22…); new tags (candidates `TIME-DELTA-ENUMERATED`, `DURATION-NO-DOUBLE-CHARGE`, `QUIESCENCE-RECONCILES-PENDING`); new sub-question pins in req/_validate if counts change.
- **U-38 remains untouched**; no checker-policy wiring in this pass.

## 7. Non-goals

U-38 (severity wiring); U-02 canonical machine-state encodings (consumes only `LogicalTime`'s width, already `u64`); U-35 trace-equality full pass (must *consume* the frozen δ_t table but is not decided here); U-37 widths; U-03 spawn budget allocation; R-BUDGET-14 (resource-family vector); the option of reopening C-104/R-CORE-14's predicate form (explicitly out — form frozen, operands only).

## 8. Next steps

1. Owner review of the D1–D8 recommendations (esp. D7's quiescence-trigger and D2's no-double-charge rule).
2. Write `audit/duration-semantics-audit.md` (evidence matrix, C-112…C-115 rows with per-row cells, GAP-style operation sweep over every time-advancing transition kind) + a remediation draft, both non-normative.
3. Addendum IX applier (exact-once precheck, git-archive dry run, `--apply`), freeze accepted D1–D8, file/resolve the C-rows and U-01/U-07/U-36, register mutations/tags, regenerate witnesses, run `check.py` + harness, commit, push.
