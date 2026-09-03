# Addendum IX — Duration-semantics adoption (ADOPTED 2026-09-03)

**Status:** APPLIED by `audit/spec_addendum9.py` (same discipline as addenda I–VIII).
U-38 is deliberately NOT touched — checker-policy wiring stays separate from normative
duration-semantics changes.

**Owner decision (D1–D3/D3a, D6–D8; audit `audit/duration-semantics-audit.md`):**

1. **D1 ADOPTED** — `D` is the per-actor remaining execution-duration budget; `W` remains
   the absolute logical-time deadline; distinct, not collapsed (N-18).
2. **D2 ADOPTED** — `ΔD := δ_t` for every logical-time-advancing transition; exactly ONE
   duration debit per advance (explicit no-double-charge invariant); `cost_C(E)`'s duration
   component is DECLARED/DIAGNOSTIC only, never a second debit authority.
3. **D3 + D3a ADOPTED** — exhaustive δ_t table: pure CEK 0; issuance +1; receipt +1;
   spawn/send/receive/blocked 0; the scheduler turn carries the executed transition's δ_t
   (no extra turn charge); reconciliation 0; per host round trip = +2 (two crossings).
4. **D6 ADOPTED** — deterministic `DeadlineExceeded` placement/precedence with atomic failure
   (zero mutation): `CapabilityViolation → BudgetExhausted → DeadlineExceeded →
   HostPolicyDenied`; late receipts use R-RECOV-08 reconciliation, never the normal deadline gate.
5. **D7 ADOPTED (AUDITED MINIMAL RULE — §5(c))** — `Deadlock ∧ ∃Pending` ⇒ a SEPARATE
   deterministic driver transition `QuiescenceReconcile` (δ_t = 0, ΔD = 0, no W check, no
   budget mutation); each pending effect → `Indeterminate` + R-RECOV-08. NOT unconditional
   quiescence reconciliation; `GlobalStep::Deadlock` itself is NOT the reconciliation
   transition; Blocked-only quiescence admits none. This is the weakest rule making
   R-BUDGET-09's liveness bound reachable — no clock, no timer, no per-effect counter.
6. **D8 ADOPTED** — `Lifetime` → `LogicalTime` (half-open `[start, end)`, five Unix
   annotations and the prose superseded-quoted, second call site L6558 recorded);
   `max_duration` declared-info only, never a machine debit; `Deadline` stays
   `Option<LogicalTime>` in all three declarations — no retype there.

**Frozen as three obligations** (spec/01: S-09 R-CAP-11; S-11 R-BUDGET-15/16):

**R-CAP-11 (`Lifetime` is logical time — frozen addendum).** `Lifetime`'s bounds are `LogicalTime`, not wall-clock: `Lifetime { start: LogicalTime, end: LogicalTime }` with a half-open validity interval `[start, end)` — `contains(t) ⇔ start ≤ t ∧ t < end` — and every call site passes the machine's logical time (the three `contains` declarations and both authorization paths, incl. the second call site at the `op_auth.lifetime.contains(logical_time)` path — the full evidence table is in `audit/u36-u37-proposals.md` §U-36 and `term/02-collisions.md` X-42). The five `// Unix timestamp` annotations and the `"e.g., Unix timestamps"` prose are SUPERSEDED (quoted, not deleted, per R-SCOPE-03); lifetime validity is machine-state only and never a wall-clock reading (R-CAP-09, R-CLAIM-02, term/ X-42). `ResourceLimits.max_duration` is DECLARED-duration information only: it describes the ceiling an author/planner may declare for an effect's predicted duration, never a machine debit and never an authorization gate — the machine's duration authority is the per-actor `D` budget under R-BUDGET-15. `Deadline` remains `Option<LogicalTime>` (`Deadline(None)` = ∞) in all three declarations — no retype. *(Frozen addendum IX — duration-semantics audit, owner decision 2026-09-03; additive per R-SCOPE-03; extends R-CAP-06/R-CAP-09/R-CLAIM-02, term/ X-42; resolves C-100, decision U-36; no source transcription.)*

**R-BUDGET-15 (duration consumable semantics — frozen addendum).** `D` is the actor's REMAINING execution-duration budget, a per-actor consumable dimension strictly distinct from the absolute logical-time deadline `W` (`Deadline`; N-18). For every logical-time-advancing transition `ΔD := δ_t` — exactly ONE duration debit per time advance, `D ← D − δ_t` — and no other operation debits `D` (no double charge): `cost_C(E)`'s duration component is a DECLARED/DIAGNOSTIC prediction only (predicted-completion information), never a second debit authority. When the next time-advancing transition of an actor would make `δ_t > D`, that transition faults `DeadlineExceeded` for that actor with ZERO mutation — no budget, capability, escrow, reservation or time change (atomic failure, R-BUDGET-08 shape). The deadline/precedence order is `CapabilityViolation → BudgetExhausted → DeadlineExceeded → HostPolicyDenied`; every such fault preserves budgets. Mailbox-blocked and pending-effect waits charge nothing (δ_t = 0, ΔD = 0); `D` is never returned or refunded (R-BUDGET-01). *(Frozen addendum IX — duration-semantics audit, owner decision 2026-09-03; additive per R-SCOPE-03; extends R-BUDGET-01/06/08, R-CORE-05; resolves C-114/C-115, decisions U-01/U-07; mutation M042; no source transcription.)*

**R-BUDGET-16 (logical-time delta table — frozen addendum).** `δ_t` is enumerated exhaustively per transition kind: pure CEK transitions (let/seq/if/call/attenuate/attenuate-denied/request-denied/marshal-fault) 0; `E-Request` issuance (host-boundary crossing #1) 1; `E-Receipt` completion (crossing #2) 1; spawn 0; send 0; receive (dequeue) 0; receive-blocked / pending hold 0; the scheduler turn carries the executed transition's δ_t — NO additional turn charge; a host round trip is two crossings, so per-effect elapsed logical cost is 2; snapshot commit, WAL append/fsync, recovery replay, reconciliation and host-failure consumption/refund 0 (see the audit's 16-row sweep). Unknown transition kinds are a checker error, never a default. On every global time advance, each `Pending` effect's `W ≤ t'` is evaluated; expiry binds that effect to `Indeterminate` + R-RECOV-08. A post-deadline `EffectReceipt` is ADMITTED — the frozen `E-Receipt` premise `t + δ_t ≤ W` is SUPERSEDED (quoted, not deleted) and the receipt is settled via R-RECOV-08 classification, never the normal deadline gate. Stable quiescence (`GlobalStep::Deadlock` ∧ ∃`Pending`) is a deterministic driver transition `QuiescenceReconcile`: δ_t = 0, ΔD = 0, no `W` check, no budget mutation — `GlobalStep::Deadlock` itself is NOT the reconciliation transition; every `Pending` effect is recorded `Indeterminate` and bound to the R-RECOV-08 admissible-outcome protocol (never re-executed; a later receipt settles via R-RECOV-08 + R-HOST-06 + R-DUR-06). `Deadlock` without `Pending` (Blocked-only quiescence) admits NO reconciliation transition. This is the weakest rule making R-BUDGET-09's liveness bound reachable — no clock, no timer, no per-effect counter. *(Frozen addendum IX — duration-semantics audit, owner decision 2026-09-03; additive per R-SCOPE-03; extends R-BUDGET-06/09, R-RECOV-08, R-CORE-08; resolves C-112/C-113, decisions U-01/U-07; mutations M040/M041; tags TIME-DELTA-ENUMERATED, QUIESCENCE-RECONCILES-PENDING; no source transcription.)*

**Register arithmetic:** 181 → 184 obligations (+3: R-CAP-11, R-BUDGET-15, R-BUDGET-16);
findings 112 / rows 113 unchanged (C-100, C-112…C-115 re-graded `resolved-by-addendum`,
not deleted); U- items unchanged at 39 (U-01/U-07/U-36 resolved ≠ deleted); mutations
39 → 42 (M040–M042); verification tags 23 → 26. R-BUDGET-12's duration rule is folded into
R-BUDGET-15/16 (still no R-BUDGET-12 ID); R-BUDGET-14 stays deferred. U-35/U-37/U-02/U-03/
U-08/U-09/U-38 untouched.

**Acceptance invariant (asserted by the applier/verifier):** every logical-time advance has
exactly one duration debit; every deadline-sensitive transition has a deterministic
pre-state/post-state rule; quiescent pending effects have a deterministic wall-clock-free
reconciliation path.
