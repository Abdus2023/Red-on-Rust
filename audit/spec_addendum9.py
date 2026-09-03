#!/usr/bin/env python3
"""spec_addendum9.py — duration-semantics adoption applier (U-01/U-07/U-36; C-100, C-112…C-115).

Addendum IX freezes the audited duration semantics from
`audit/duration-semantics-audit.md` (§2 sweep, §5 D7 analysis, §6 preview) per the
owner decision of 2026-09-03 (recorded in audit/spec-addendum9-draft.md):

  D1  ADOPTED  — D is per-actor remaining execution-duration budget; W remains the
               absolute logical-time deadline; distinct, not collapsed.
  D2  ADOPTED  — ΔD := δ_t for every logical-time-advancing transition, exactly one
               duration debit per advance (no double charge); `cost_C(E)`'s duration
               component is DECLARED/DIAGNOSTIC only, never a second debit authority.
  D3+D3a ADOPTED — exhaustive δ_t table (pure CEK 0; issuance +1; receipt +1;
               spawn/send/receive/blocked 0; the scheduler turn carries the executed
               transition's δ_t; reconciliation 0; per host round trip = +2).
  D6  ADOPTED  — deterministic `DeadlineExceeded` placement/precedence with atomic
               failure (zero mutation): CapabilityViolation → BudgetExhausted →
               DeadlineExceeded → HostPolicyDenied; late receipts settle via
               R-RECOV-08 reconciliation, never the normal deadline gate.
  D7  ADOPTED (AUDITED MINIMAL RULE) — the audit's §5(c): `Deadlock ∧ ∃Pending` ⇒ a
               SEPARATE deterministic driver transition `QuiescenceReconcile`
               (δ_t = 0, ΔD = 0, no W check, no budget mutation), each pending effect
               → `Indeterminate` + R-RECOV-08. NOT unconditional quiescence
               reconciliation; `GlobalStep::Deadlock` itself is NOT the reconciliation
               transition; Blocked-only quiescence admits no reconciliation.
  D8  ADOPTED  — `Lifetime` → `LogicalTime` (half-open `[start, end)`, five
               annotations superseded-quoted, second call site L6558 recorded);
               `max_duration` declared-info only, never a machine debit; `Deadline`
               stays `Option<LogicalTime>` in all three declarations.

Frozen as three obligations: R-BUDGET-15, R-BUDGET-16 (S-11) and R-CAP-11 (S-09).
R-BUDGET-12's duration rule is FOLDED into R-BUDGET-15/16 (still no R-BUDGET-12 ID;
R-BUDGET-14 stays deferred). Resolves U-01, U-07, U-36; re-grades C-100 and
C-112…C-115 resolved-by-addendum; AMB-01/VU-02 notes; registers M040–M042 and
tags TIME-DELTA-ENUMERATED / DURATION-NO-DOUBLE-CHARGE / QUIESCENCE-RECONCILES-PENDING.

Register arithmetic: 181 → 184 obligations (+3); findings 112 / rows 113 unchanged
(resolved ≠ deleted); unresolved 39 unchanged (resolved ≠ deleted); mutations
39 → 42 (M040–M042); verification tags 23 → 26.
U-38 is deliberately NOT touched (separate checker-policy decision; no PR until U-38).
Same discipline as spec_addendum7.py / spec_addendum8.py.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SPEC01 = REPO / "spec" / "01-canonical-specification.md"
MATRIX = REPO / "spec" / "03-obligation-matrix.md"
CONTRA = REPO / "spec" / "06-contradictions-ambiguities.md"
VMAP = REPO / "spec" / "08-verification-mapping.md"
UNRES = REPO / "spec" / "09-unresolved-decisions.md"
RECORDS = REPO / "spec" / "normative-normalization-records.md"
README = REPO / "README.md"
BUILDIDX = REPO / "spec" / "_build_index.py"
VALIDATE = REPO / "req" / "_validate.py"
OWNERSHIP = REPO / "mod" / "_ownership.py"
MOD03 = REPO / "mod" / "03-capability.md"
MOD04 = REPO / "mod" / "04-budget.md"
HARNESS = REPO / "audit" / "_checker_mutations.py"
RAAUDIT = REPO / "audit" / "resource-accounting-audit.md"
DURAUDIT = REPO / "audit" / "duration-semantics-audit.md"
U01SCOPING = REPO / "audit" / "u01-duration-scoping.md"
U36PROP = REPO / "audit" / "u36-u37-proposals.md"
DRAFT = REPO / "audit" / "spec-addendum9-draft.md"

BASELINE = "1b9420a"
NEW_IDS = ["R-CAP-11", "R-BUDGET-15", "R-BUDGET-16"]
MARKERS = NEW_IDS + ["M040", "M041", "M042", "TIME-DELTA-ENUMERATED",
                     "DURATION-NO-DOUBLE-CHARGE", "QUIESCENCE-RECONCILES-PENDING",
                     "addendum IX"]
RESOLVED_SET = ["C-100", "C-103", "C-104", "C-105", "C-106", "C-107", "C-108",
                "C-109", "C-112", "C-113", "C-114", "C-115"]

# ---------------------------------------------------------------------------
# frozen addendum texts (single-line bodies, matching the spec/01 style;
# adopted wording is quoted from the audit per R-SCOPE-03)
# ---------------------------------------------------------------------------

ADD_CAP11 = ("**R-CAP-11 (`Lifetime` is logical time — frozen addendum).** `Lifetime`'s bounds "
 "are `LogicalTime`, not wall-clock: `Lifetime { start: LogicalTime, end: LogicalTime }` with a "
 "half-open validity interval `[start, end)` — `contains(t) ⇔ start ≤ t ∧ t < end` — and every "
 "call site passes the machine's logical time (the three `contains` declarations and both "
 "authorization paths, incl. the second call site at the `op_auth.lifetime.contains(logical_time)` "
 "path — the full evidence table is in `audit/u36-u37-proposals.md` §U-36 and `term/02-collisions.md` "
 "X-42). The five `// Unix timestamp` annotations and the `\"e.g., Unix "
 "timestamps\"` prose are SUPERSEDED (quoted, not deleted, per R-SCOPE-03); lifetime validity is "
 "machine-state only and never a wall-clock reading (R-CAP-09, R-CLAIM-02, term/ X-42). "
 "`ResourceLimits.max_duration` is DECLARED-duration information only: it describes the ceiling an "
 "author/planner may declare for an effect's predicted duration, never a machine debit and never an "
 "authorization gate — the machine's duration authority is the per-actor `D` budget under "
 "R-BUDGET-15. `Deadline` remains `Option<LogicalTime>` (`Deadline(None)` = ∞) in all three "
 "declarations — no retype. *(Frozen addendum IX — duration-semantics audit, owner decision "
 "2026-09-03; additive per R-SCOPE-03; extends R-CAP-06/R-CAP-09/R-CLAIM-02, term/ X-42; resolves "
 "C-100, decision U-36; no source transcription.)*")

ADD_BUDGET15 = ("**R-BUDGET-15 (duration consumable semantics — frozen addendum).** `D` is the "
 "actor's REMAINING execution-duration budget, a per-actor consumable dimension strictly distinct "
 "from the absolute logical-time deadline `W` (`Deadline`; N-18). For every logical-time-advancing "
 "transition `ΔD := δ_t` — exactly ONE duration debit per time advance, `D ← D − δ_t` — and no "
 "other operation debits `D` (no double charge): `cost_C(E)`'s duration component is a "
 "DECLARED/DIAGNOSTIC prediction only (predicted-completion information), never a second debit "
 "authority. When the next time-advancing transition of an actor would make `δ_t > D`, that "
 "transition faults `DeadlineExceeded` for that actor with ZERO mutation — no budget, capability, "
 "escrow, reservation or time change (atomic failure, R-BUDGET-08 shape). The deadline/precedence "
 "order is `CapabilityViolation → BudgetExhausted → DeadlineExceeded → HostPolicyDenied`; every "
 "such fault preserves budgets. Mailbox-blocked and pending-effect waits charge nothing "
 "(δ_t = 0, ΔD = 0); `D` is never returned or refunded (R-BUDGET-01). *(Frozen addendum IX — "
 "duration-semantics audit, owner decision 2026-09-03; additive per R-SCOPE-03; extends "
 "R-BUDGET-01/06/08, R-CORE-05; resolves C-114/C-115, decisions U-01/U-07; mutation M042; no "
 "source transcription.)*")

ADD_BUDGET16 = ("**R-BUDGET-16 (logical-time delta table — frozen addendum).** `δ_t` is enumerated "
 "exhaustively per transition kind: pure CEK transitions (let/seq/if/call/attenuate/"
 "attenuate-denied/request-denied/marshal-fault) 0; `E-Request` issuance (host-boundary crossing "
 "#1) 1; `E-Receipt` completion (crossing #2) 1; spawn 0; send 0; receive (dequeue) 0; "
 "receive-blocked / pending hold 0; the scheduler turn carries the executed transition's δ_t — NO "
 "additional turn charge; a host round trip is two crossings, so per-effect elapsed logical cost is "
 "2; snapshot commit, WAL append/fsync, recovery replay, reconciliation and host-failure "
 "consumption/refund 0 (see the audit's 16-row sweep). Unknown transition kinds are a checker "
 "error, never a default. On every global time advance, each `Pending` effect's `W ≤ t'` is "
 "evaluated; expiry binds that effect to `Indeterminate` + R-RECOV-08. A post-deadline "
 "`EffectReceipt` is ADMITTED — the frozen `E-Receipt` premise `t + δ_t ≤ W` is SUPERSEDED (quoted, "
 "not deleted) and the receipt is settled via R-RECOV-08 classification, never the normal deadline "
 "gate. Stable quiescence (`GlobalStep::Deadlock` ∧ ∃`Pending`) is a deterministic driver "
 "transition `QuiescenceReconcile`: δ_t = 0, ΔD = 0, no `W` check, no budget mutation — "
 "`GlobalStep::Deadlock` itself is NOT the reconciliation transition; every `Pending` effect is "
 "recorded `Indeterminate` and bound to the R-RECOV-08 admissible-outcome protocol (never "
 "re-executed; a later receipt settles via R-RECOV-08 + R-HOST-06 + R-DUR-06). `Deadlock` without "
 "`Pending` (Blocked-only quiescence) admits NO reconciliation transition. This is the weakest rule "
 "making R-BUDGET-09's liveness bound reachable — no clock, no timer, no per-effect counter. "
 "*(Frozen addendum IX — duration-semantics audit, owner decision 2026-09-03; additive per "
 "R-SCOPE-03; extends R-BUDGET-06/09, R-RECOV-08, R-CORE-08; resolves C-112/C-113, decisions "
 "U-01/U-07; mutations M040/M041; tags TIME-DELTA-ENUMERATED, QUIESCENCE-RECONCILES-PENDING; no "
 "source transcription.)*")

# ---------------------------------------------------------------------------
# spec/03 rows (6 cells)
# ---------------------------------------------------------------------------
ROW_CAP11 = "| R-CAP-11 | Lifetime is logical time: half-open `[start, end)` validity, call sites pass logical time, five Unix annotations superseded-quoted; `max_duration` declared-info only; `Deadline` stays `Option<LogicalTime>` (C-100 resolved; U-36) | addendum (duration-semantics) | SPECIFIED | ror-core, ror-kernel | M4 expiration/authorization gate tests |"
ROW_15 = "| R-BUDGET-15 | Duration consumable semantics: per-actor D; `ΔD := δ_t` exactly once per time advance; no double charge (`cost_C(E)` duration declared/diagnostic only); `δ_t > D` ⇒ `DeadlineExceeded` zero-mutation; precedence `CapabilityViolation → BudgetExhausted → DeadlineExceeded → HostPolicyDenied` (C-114/C-115 resolved; U-01/U-07) | addendum (duration-semantics) | SPECIFIED | ror-core, ror-runtime | M042, budget-gate tests |"
ROW_16 = "| R-BUDGET-16 | Exhaustive δ_t table (pure 0; issuance +1; receipt +1; spawn/send/receive/blocked 0; turn carries the executed δ_t; per host round trip = 2; reconciliation 0); Pending W-eligibility on each advance; late receipts settle via R-RECOV-08 (`t+δ_t ≤ W` superseded-quoted); stable quiescence `Deadlock ∧ ∃Pending` ⇒ driver `QuiescenceReconcile` δ_t=0/ΔD=0, each pending → `Indeterminate` + R-RECOV-08 (C-112/C-113 resolved; U-01/U-07) | addendum (duration-semantics) | SPECIFIED | ror-runtime | M040, M041, QUIESCENCE-RECONCILES-PENDING, ledger liveness |"

TOTAL_OLD = ("**Total: 181 obligations** (148 transcribed from the frozen source + 33 post-audit frozen "
 "addenda: R-ARCH-05, R-ACTOR-09, R-ACTOR-10, R-BUDGET-09, R-BUDGET-10, R-BUDGET-11, R-BUDGET-13, "
 "R-CANON-12, R-CANON-13, R-CAP-10, R-COMPILE-06, R-CORE-11, R-CORE-12, R-CORE-13, R-CORE-14, "
 "R-DUR-06, R-DUR-07, R-EFFECT-08, R-HOST-06, R-KERN-04, R-KERN-05, R-KERN-06, R-MARSHAL-05, "
 "R-MARSHAL-06, R-PERSIST-07, R-PERSIST-08, R-PLANNER-06, R-PLANNER-07, R-RECOV-08, R-RECOV-09, "
 "R-TEST-12, R-TRUST-04, R-TRUST-05). All `SPECIFIED`. None may be promoted without repository "
 "evidence per `00-overview.md` §2.")
TOTAL_NEW = ("**Total: 184 obligations** (148 transcribed from the frozen source + 36 post-audit frozen "
 "addenda: R-ARCH-05, R-ACTOR-09, R-ACTOR-10, R-BUDGET-09, R-BUDGET-10, R-BUDGET-11, R-BUDGET-13, "
 "R-BUDGET-15, R-BUDGET-16, R-CANON-12, R-CANON-13, R-CAP-10, R-CAP-11, R-COMPILE-06, R-CORE-11, "
 "R-CORE-12, R-CORE-13, R-CORE-14, R-DUR-06, R-DUR-07, R-EFFECT-08, R-HOST-06, R-KERN-04, "
 "R-KERN-05, R-KERN-06, R-MARSHAL-05, R-MARSHAL-06, R-PERSIST-07, R-PERSIST-08, R-PLANNER-06, "
 "R-PLANNER-07, R-RECOV-08, R-RECOV-09, R-TEST-12, R-TRUST-04, R-TRUST-05). All `SPECIFIED`. None "
 "may be promoted without repository evidence per `00-overview.md` §2.")

# ---------------------------------------------------------------------------
# spec/06: status cells + the addendum-block paragraph tail
# ---------------------------------------------------------------------------
C100_OLD = "| **open** → U-36 |"
C100_NEW = "| **resolved-by-addendum** → R-CAP-11 (U-36) |"
C112_OLD = "**open** → U-01 (U-07)"
C112_NEW = "**resolved-by-addendum** → R-BUDGET-16 (U-01/U-07)"
C113_OLD = "**open** → U-01 | A host that completes after"
C113_NEW = "**resolved-by-addendum** → R-BUDGET-16 (U-01) | A host that completes after"
C114_OLD = "**open** → U-01 | The three models cannot all hold:"
C114_NEW = "**resolved-by-addendum** → R-BUDGET-15 (U-01) | The three models cannot all hold:"
C115_OLD = "**open** → U-01 | With the predicate fixed post-advance (C-104 resolved)"
C115_NEW = "**resolved-by-addendum** → R-BUDGET-15 (U-01) | With the predicate fixed post-advance (C-104 resolved)"

C06_TAIL_OLD = ("The audit itself issued no frozen text (R-SCOPE-03); the remediation becomes normative "
 "only by Addendum IX.")
C06_TAIL_NEW = ("The audit itself issued no frozen text (R-SCOPE-03); the remediation becomes normative "
 "only by Addendum IX.\n\n"
 "**Addendum IX adopted 2026-09-03** (owner decision, `audit/spec-addendum9-draft.md`): "
 "**R-CAP-11** (`Lifetime` → `LogicalTime`, half-open `[start, end)`, five Unix annotations "
 "superseded-quoted, second call site L6558 recorded, `max_duration` declared-info only, `Deadline` "
 "confirmed `Option<LogicalTime>`), **R-BUDGET-15** (per-actor `D`, `ΔD := δ_t`, no double charge, "
 "`cost_C(E)` duration declared/diagnostic only, exhaustion ⇒ `DeadlineExceeded` zero-mutation, "
 "precedence `CapabilityViolation → BudgetExhausted → DeadlineExceeded → HostPolicyDenied`) and "
 "**R-BUDGET-16** (D3a-exhaustive δ_t table, Pending W-eligibility on each global advance, "
 "late-receipt settlement via R-RECOV-08 with the frozen `t + δ_t ≤ W` premise quoted superseded, "
 "and the minimal audited quiescence rule — `Deadlock ∧ ∃Pending` ⇒ driver `QuiescenceReconcile`, "
 "δ_t = 0/ΔD = 0, each pending → `Indeterminate` + R-RECOV-08; `GlobalStep::Deadlock` itself is NOT "
 "the reconciliation transition and Blocked-only quiescence admits none) are frozen; R-BUDGET-12's "
 "duration rule is folded into R-BUDGET-15/16 (still no R-BUDGET-12 ID) and R-BUDGET-14 stays "
 "deferred. **C-100 and C-112…C-115 are re-graded `resolved-by-addendum`** (C-100 → R-CAP-11 / "
 "U-36; C-112 → R-BUDGET-16 / U-01, U-07; C-113 → R-BUDGET-16 / U-01; C-114/C-115 → R-BUDGET-15 / "
 "U-01), resolving U-01, U-07 and U-36; counts — 112 findings in 113 rows — are unchanged by the "
 "re-grading. Rows are re-graded, not deleted (R-SCOPE-03); the filed text above is quoted as "
 "authored. Mutations M040–M042 and tags `TIME-DELTA-ENUMERATED`/`DURATION-NO-DOUBLE-CHARGE`/"
 "`QUIESCENCE-RECONCILES-PENDING` are registered; U-35/U-37/U-02/U-03/U-08/U-09/U-38 untouched.")

# ---------------------------------------------------------------------------
# spec/09 resolution bullets + process note 12
# ---------------------------------------------------------------------------
U01_RESOLVE = ("- **Resolved (addendum IX, 2026-09-03):** `R-BUDGET-15` (per-actor remaining "
 "execution-duration budget `D` distinct from absolute deadline `W`; `ΔD := δ_t` for every "
 "logical-time-advancing transition, exactly one debit per advance, no double charge; `cost_C(E)`'s "
 "duration component declared/diagnostic only; `δ_t > D` ⇒ `DeadlineExceeded` with zero mutation; "
 "precedence `CapabilityViolation → BudgetExhausted → DeadlineExceeded → HostPolicyDenied`) and "
 "`R-BUDGET-16` (exhaustive δ_t table per D3a — pure 0, issuance +1, receipt +1, "
 "spawn/send/receive/blocked 0, scheduler turn carries the executed transition's δ_t, per host round "
 "trip = 2, reconciliation/quiescence-driver 0; Pending W-eligibility evaluated on each global "
 "advance; post-deadline receipts admitted and settled via R-RECOV-08, the frozen `t + δ_t ≤ W` "
 "premise quoted superseded) are frozen; `R-CAP-11` settles the lifetime interaction (D8). **The "
 "D7 condition is discharged:** the audit (§5) established that `Pending` survives "
 "`GlobalStep::Deadlock`, that progress-after-quiescence is otherwise undefined, and that the "
 "weakest rule making R-BUDGET-09's liveness bound reachable is the separate deterministic driver "
 "transition `QuiescenceReconcile` (`Deadlock ∧ ∃Pending`, δ_t = 0, ΔD = 0, each pending → "
 "`Indeterminate` + R-RECOV-08) — the addendum freezes exactly that minimal rule, not unconditional "
 "quiescence reconciliation, and `GlobalStep::Deadlock` itself is not the reconciliation "
 "transition. `spec/06` C-112…C-115 re-graded `resolved-by-addendum`; R-BUDGET-12's duration rule "
 "is folded into R-BUDGET-15/16 (no R-BUDGET-12 ID is frozen); R-BUDGET-14 stays deferred; "
 "U-35/U-37/U-02/U-03/U-08/U-09/U-38 untouched.")

U07_RESOLVE = ("- **Resolved (addendum IX, 2026-09-03):** `R-BUDGET-16` freezes the exhaustive δ_t "
 "table — pure CEK 0, issuance +1, receipt +1, spawn/send/receive/blocked 0, scheduler-turn charge "
 "= the executed transition's δ_t (no extra turn charge), per host round trip = 2, "
 "snapshot/WAL/recovery/reconciliation 0 — with unknown kinds a checker error, never a default, so "
 "every logical-time advance has exactly one defined δ_t and exactly one duration debit "
 "(R-BUDGET-15's `ΔD := δ_t`). C-112/C-113 re-graded `resolved-by-addendum`.")

U36_RESOLVE = ("- **Resolved (addendum IX, 2026-09-03):** `R-CAP-11` retypes `Lifetime` to "
 "`LogicalTime` with half-open `[start, end)` validity, records the second authorization call site "
 "(`op_auth.lifetime.contains(logical_time)`), quotes the five `// Unix timestamp` annotations and "
 "the `\"e.g., Unix timestamps\"` prose as superseded (R-SCOPE-03), resolves `max_duration` as "
 "declared-duration information only — never a machine debit, never an authorization gate — and "
 "confirms `Deadline` stays `Option<LogicalTime>` (`Deadline(None)` = ∞) in all three declarations. "
 "The proposal in `audit/u36-u37-proposals.md` §U-36 is adopted as submitted; `spec/06` C-100 "
 "re-graded `resolved-by-addendum`.")

NOTE12 = ("12. **Addendum IX adopted 2026-09-03** (U-01 / U-07 / U-36, C-100 / C-112…C-115): "
 "R-CAP-11, R-BUDGET-15 and R-BUDGET-16 are frozen as addendum IX — three obligations, Total "
 "181 → 184, mutations M040–M042 and tags `TIME-DELTA-ENUMERATED`/`DURATION-NO-DOUBLE-CHARGE`/"
 "`QUIESCENCE-RECONCILES-PENDING` registered, C-100 and C-112…C-115 re-graded "
 "`resolved-by-addendum`. R-BUDGET-12's rule is folded into R-BUDGET-15/16 (still no R-BUDGET-12 "
 "ID); R-BUDGET-14 remains deferred. Decision record: `audit/spec-addendum9-draft.md`.")

# ---------------------------------------------------------------------------
# audit status notes
# ---------------------------------------------------------------------------
DURAUDIT_NOTE = ("\n\n**Adopted 2026-09-03 by addendum IX** (owner decision, "
 "`audit/spec-addendum9-draft.md`): D1–D3/D3a/D6/D8 frozen as R-CAP-11, R-BUDGET-15, R-BUDGET-16; "
 "D7's §5(c) minimal rule frozen exactly as stated (separate `QuiescenceReconcile` driver "
 "transition, scoped to `Deadlock ∧ ∃Pending`; unconditional quiescence reconciliation rejected); "
 "C-100 and C-112…C-115 re-graded `resolved-by-addendum`; U-01/U-07/U-36 resolved; the §2 sweep's "
 "rows now carry their adopted δ_t values as frozen text. U-38 untouched.")

U01_NOTE = ("\n\n**Adopted 2026-09-03 by addendum IX:** the D1–D8 recommendations in this\n"
 "document are the frozen semantics (`R-CAP-11`, `R-BUDGET-15`, `R-BUDGET-16`;\n"
 "U-01/U-07/U-36 resolved; C-100/C-112…C-115 re-graded). This document remains the\n"
 "scoping record; its wording is quoted, not rewritten (R-SCOPE-03).")

U36_NOTE = ("\n\n**ADOPTED 2026-09-03 by addendum IX:** §U-36 below is adopted as submitted as "
 "`R-CAP-11` (half-open `[start, end)`, five superseded annotations quoted, second call site "
 "recorded; `max_duration` resolved as declared-info only in `R-BUDGET-15`). This file remains the "
 "proposal record; its wording above is quoted, not rewritten (R-SCOPE-03). **§U-37 is NOT "
 "adopted** — it stays a proposal; U-37 remains open.")

# ---------------------------------------------------------------------------
# edit table
# ---------------------------------------------------------------------------
EDITS: list[tuple[Path, str, str]] = [
    # ------------------------------ spec/01 --------------------------------
    (SPEC01, "*(Frozen addendum — post-audit remediation SEC-014; additive per R-SCOPE-03; extends R-CAP-04/R-CAP-05/R-COMPILE-06; resolves C-94, closing AMB-12/U-09's admissibility clause; mutation M030; no source transcription.)*",
             "*(Frozen addendum — post-audit remediation SEC-014; additive per R-SCOPE-03; extends R-CAP-04/R-CAP-05/R-COMPILE-06; resolves C-94, closing AMB-12/U-09's admissibility clause; mutation M030; no source transcription.)*\n\n" + ADD_CAP11),
    (SPEC01, "*(Frozen addendum VIII — resource-accounting audit, owner decision 2026-09-03; additive per R-SCOPE-03; extends R-BUDGET-03/05, R-PERSIST-04/05/07; resolves C-108, decision U-45; no source transcription.)*",
             "*(Frozen addendum VIII — resource-accounting audit, owner decision 2026-09-03; additive per R-SCOPE-03; extends R-BUDGET-03/05, R-PERSIST-04/05/07; resolves C-108, decision U-45; no source transcription.)*\n\n" + ADD_BUDGET15 + "\n\n" + ADD_BUDGET16),
    # ------------------------------ spec/03 --------------------------------
    (MATRIX, "| R-CAP-10 | AdmissibleConstraint defined: decidable well-formedness per semantic domain (O/S/Q/R/T); inadmissible constraint faults (InvalidConstraint), never identity/top-default; compile-time validation of attacker-authored constraints (C-94 resolved; M030) | addendum (SEC-014) | SPECIFIED | ror-kernel, ror-compiler | M030, compiler negative suite |",
             "| R-CAP-10 | AdmissibleConstraint defined: decidable well-formedness per semantic domain (O/S/Q/R/T); inadmissible constraint faults (InvalidConstraint), never identity/top-default; compile-time validation of attacker-authored constraints (C-94 resolved; M030) | addendum (SEC-014) | SPECIFIED | ror-kernel, ror-compiler | M030, compiler negative suite |\n" + ROW_CAP11),
    (MATRIX, "| R-BUDGET-13 | Persistent-capacity accounting: volatile RAM distinct from persistent storage; RAM released on scope exit/halt; durable storage retained and snapshot-compacted; overflow faults (C-108 resolved; U-45) | addendum (resource-accounting) | SPECIFIED | ror-persistence | M7 snapshot-capacity tests |",
             "| R-BUDGET-13 | Persistent-capacity accounting: volatile RAM distinct from persistent storage; RAM released on scope exit/halt; durable storage retained and snapshot-compacted; overflow faults (C-108 resolved; U-45) | addendum (resource-accounting) | SPECIFIED | ror-persistence | M7 snapshot-capacity tests |\n" + ROW_15 + "\n" + ROW_16),
    (MATRIX, TOTAL_OLD, TOTAL_NEW),
    # ------------------------------ spec/06 --------------------------------
    (CONTRA, C100_OLD, C100_NEW),
    (CONTRA, C112_OLD, C112_NEW),
    (CONTRA, C113_OLD, C113_NEW),
    (CONTRA, C114_OLD, C114_NEW),
    (CONTRA, C115_OLD, C115_NEW),
    (CONTRA, C06_TAIL_OLD, C06_TAIL_NEW),
    # ------------------------------ spec/08 --------------------------------
    (VMAP, "## 2. Mutation registry → obligation map (M001–M039, R-TEST-04)",
           "## 2. Mutation registry → obligation map (M001–M042, R-TEST-04)"),
    (VMAP, "| M039 | `Remains-Indeterminate` treated as a terminal disposition (stranded escrow survives the logical-time bound) | R-BUDGET-11 |",
           "| M039 | `Remains-Indeterminate` treated as a terminal disposition (stranded escrow survives the logical-time bound) | R-BUDGET-11 |\n"
           "| M040 | δ_t table violation: a time-capable transition kind advances logical time without its frozen δ_t (e.g., a scheduler turn charged +1 on top of the executed transition, or a kind omitted from the enumeration) | R-BUDGET-16 |\n"
           "| M041 | post-deadline `EffectReceipt` routed through the normal deadline gate (rejected) instead of R-RECOV-08 settlement | R-BUDGET-16, R-RECOV-08 |\n"
           "| M042 | `cost_C(E)`'s duration component debits `D` in addition to the transition's `ΔD := δ_t` (double charge) | R-BUDGET-15 |"),
    (VMAP, "(not part of the frozen source set; added by remediations SEC-001/SEC-004 and addenda VII/VIII):",
           "(not part of the frozen source set; added by remediations SEC-001/SEC-004 and addenda VII/VIII/IX):"),
    (VMAP, "| `PERSISTENT-CAPACITY-ACCOUNTING` | R-BUDGET-13 (addendum VIII), R-PERSIST-04 | Volatile RAM distinct from persistent storage; durable capacity accounted per WAL frame/snapshot artifact; overflow faults | NONE |",
           "| `PERSISTENT-CAPACITY-ACCOUNTING` | R-BUDGET-13 (addendum VIII), R-PERSIST-04 | Volatile RAM distinct from persistent storage; durable capacity accounted per WAL frame/snapshot artifact; overflow faults | NONE |\n"
           "| `TIME-DELTA-ENUMERATED` | R-BUDGET-16 (addendum IX), R-BUDGET-06 | every time-capable transition kind carries its frozen δ_t; per host round trip = 2; the scheduler turn is the executed transition's δ_t (mutation M040) | NONE |\n"
           "| `DURATION-NO-DOUBLE-CHARGE` | R-BUDGET-15 (addendum IX), R-BUDGET-01 | exactly one duration debit per logical-time advance; `cost_C(E)`'s duration component is declared/diagnostic only, never a machine debit (mutation M042) | NONE |\n"
           "| `QUIESCENCE-RECONCILES-PENDING` | R-BUDGET-16 (addendum IX), R-BUDGET-09, R-RECOV-08 | stable quiescence with any `Pending` effect deterministically records `Indeterminate` per effect and binds to R-RECOV-08; Blocked-only quiescence does not (mutation M041) | NONE |"),
    (VMAP, "M037/M038 (addendum VII) and M039 (addendum VIII) are registered the same way — machine mutants, unmeasurable in BOOTSTRAP; their document-mutant shapes are exercised by `audit/_checker_mutations.py` K19/K20/K21. M036 remains the one measurable document mutant.",
           "M037/M038 (addendum VII), M039 (addendum VIII) and M040–M042 (addendum IX) are registered the same way — machine mutants, unmeasurable in BOOTSTRAP; their document-mutant shapes are exercised by `audit/_checker_mutations.py` K19/K20/K21/K22-K24. M036 remains the one measurable document mutant."),
    # ------------------------------ spec/09 --------------------------------
    (UNRES, "the addendum freezes it only after the owner confirms this conclusion.",
            "the addendum freezes it only after the owner confirms this conclusion.\n" + U01_RESOLVE),
    (UNRES, "A minimal defensible table: `δ_t = 0` for all pure CEK transitions, `+1` per scheduler turn, `+1` per host round-trip, `0` for spawn/send/receive (charging them makes deadlines a function of message volume). Whatever is chosen, every transition kind must be enumerated — a partial table reopens the gap.",
            "A minimal defensible table: `δ_t = 0` for all pure CEK transitions, `+1` per scheduler turn, `+1` per host round-trip, `0` for spawn/send/receive (charging them makes deadlines a function of message volume). Whatever is chosen, every transition kind must be enumerated — a partial table reopens the gap.\n" + U07_RESOLVE),
    (UNRES, "- **Linked:** C-100, U-01, U-07, T-27/T-28, R-CAP-06/09, R-CLAIM-02, DET-006.",
            "- **Linked:** C-100, U-01, U-07, T-27/T-28, R-CAP-06/09, R-CLAIM-02, DET-006.\n" + U36_RESOLVE),
    (UNRES, "Decision record: `audit/spec-addendum8-draft.md`.",
            "Decision record: `audit/spec-addendum8-draft.md`.\n\n" + NOTE12),
    # ------------------------------ records --------------------------------
    (RECORDS, "The same holds for the three addendum-VIII obligations (`R-BUDGET-10`, `R-BUDGET-11`, `R-BUDGET-13`; resource-accounting remediation) — each is its own original, no substitution.",
              "The same holds for the three addendum-VIII obligations (`R-BUDGET-10`, `R-BUDGET-11`, `R-BUDGET-13`; resource-accounting remediation) — each is its own original, no substitution. The same holds for the three addendum-IX obligations (`R-CAP-11`, `R-BUDGET-15`, `R-BUDGET-16`; duration-semantics remediation) — each is its own original, no substitution."),
    # ------------------------------ README --------------------------------
    (README, "spec/03-obligation-matrix.md` — 181 stable requirement IDs (`R-…`; 148 from the frozen source + 33 post-audit frozen addenda, incl. the five addendum-VII and three addendum-VIII obligations) with status and provenance",
             "spec/03-obligation-matrix.md` — 184 stable requirement IDs (`R-…`; 148 from the frozen source + 36 post-audit frozen addenda, incl. the five addendum-VII, three addendum-VIII and three addendum-IX obligations) with status and provenance"),
    (README, "C-103…C-107/C-109 `resolved-by-addendum` under addendum VII and C-108 under addendum VIII;",
             "C-103…C-107/C-109 `resolved-by-addendum` under addendum VII, C-108 under addendum VIII and C-100/C-112…C-115 under addendum IX;"),
    (README, "U-39…U-44 resolved by addendum VII and U-45 by addendum VIII; U-08 corrected",
             "U-39…U-44 resolved by addendum VII, U-45 by addendum VIII and U-01/U-07/U-36 by addendum IX; U-08 corrected"),
    (README, "(R-SCOPE-03). Three passes are complete:",
             "(R-SCOPE-03). Four passes are complete:"),
    (README, "exist only as a draft (`audit/request-pipeline-remediation-draft.md`, NOT ADOPTED).",
             "exist only as a draft (`audit/request-pipeline-remediation-draft.md`, NOT ADOPTED).\n"
             "- `audit/duration-semantics-audit.md` — **what `D` measures and how logical time advances**\n"
             "  (U-01/U-07/U-36; the audit filed C-112…C-115 and scoped the cluster into D1–D8; pre-adoption\n"
             "  owner decisions D1–D3/D6/D8 approved with D7 conditional on its own §5 evidence). Verdict:\n"
             "  the invariant \"every logical-time advance has exactly one duration debit, and every\n"
             "  deadline-sensitive transition has a deterministic pre-state/post-state rule\" fails in three\n"
             "  places — the quiescence clock hole (a `Pending` effect freezes `t`, so R-BUDGET-09's\n"
             "  liveness bound is unreachable), the missing post-deadline receipt rule, and three mutually\n"
             "  inconsistent `D` debit models — plus the unfrozen `DeadlineExceeded` firing point. Its\n"
             "  remediation is addendum IX (`R-CAP-11`, `R-BUDGET-15/16`): C-100/C-112…C-115 re-graded\n"
             "  `resolved-by-addendum`, U-01/U-07/U-36 resolved, R-BUDGET-12 folded, U-38 untouched."),
    # ------------------------------ mod/03 --------------------------------
    (MOD03, "- Blocking open items: **U-36** (is `Lifetime` wall-clock or logical time? The frozen\n  `Lifetime { start, end }` is annotated \"Unix timestamp\" three times yet is compared\n  against `LogicalTime` inside `authorizes` — R-CAP-06's fifth conjunct, computed at\n  gate 6 — contradicting R-CAP-09/R-CLAIM-02; `spec/06` C-100, audit DET-006),\n  **U-09**",
            "- Blocking open items: **U-36** (resolved by addendum IX 2026-09-03: `R-CAP-11` retypes\n  `Lifetime` to `LogicalTime`, half-open `[start, end)`, five Unix annotations\n  superseded-quoted, second call site L6558 recorded; `max_duration` declared-info only;\n  `Deadline` stays `Option<LogicalTime>`; `spec/06` C-100 re-graded),\n  **U-09**"),
    (MOD03, "| R-CAP-10 | AdmissibleConstraint defined: decidable well-formedness per semantic domain (O/S/Q/R/T); inadmissible constraint faults (InvalidConstraint), never identity/top-default; compile-time validation of attacker-authored constraints (C-94 resolved; M030) | addendum V (SEC-014) | M030, compiler negative suite |",
             "| R-CAP-10 | AdmissibleConstraint defined: decidable well-formedness per semantic domain (O/S/Q/R/T); inadmissible constraint faults (InvalidConstraint), never identity/top-default; compile-time validation of attacker-authored constraints (C-94 resolved; M030) | addendum V (SEC-014) | M030, compiler negative suite |\n"
             "| R-CAP-11 | Lifetime is logical time: half-open `[start, end)`; call sites pass logical time; five Unix annotations superseded-quoted; `max_duration` declared-info only; `Deadline` stays `Option<LogicalTime>` (C-100 resolved) | addendum IX (duration-semantics) | M4 expiration/authorization gate tests |"),
    (MOD03, "Canonical text: `spec/01` S-09/S-10; addenda I, V. All 16 obligations `SPECIFIED`.",
            "Canonical text: `spec/01` S-09/S-10; addenda I, V, IX. All 17 obligations `SPECIFIED`."),
    (MOD03, "**16 obligations / 35 records.**", "**17 obligations / 35 records.**"),
    # ------------------------------ mod/04 --------------------------------
    (MOD04, "- Blocking open items: **U-01** (operational meaning of the `D` consumable — AMB-01;\n  exhaustion behavior is not testable until decided), **U-07** (per-transition `δ_t`\n  values — AMB-19), **U-03**",
            "- Blocking open items: **U-01** (resolved by addendum IX 2026-09-03: `R-BUDGET-15` —\n  per-actor D, `ΔD := δ_t`, no double charge, exhaustion ⇒ `DeadlineExceeded`),\n  **U-07** (resolved by addendum IX: `R-BUDGET-16` — exhaustive δ_t table,\n  per host round trip = 2), **U-03**"),
    (MOD04, "| R-BUDGET-01 | `B = ⟨C=⟨F,I,D⟩, R=⟨M,S⟩, W⟩` semantics | L8683–8700, L9161–9175 | U-01 (D semantics) blocking |",
             "| R-BUDGET-01 | `B = ⟨C=⟨F,I,D⟩, R=⟨M,S⟩, W⟩` semantics | L8683–8700, L9161–9175 | R-BUDGET-15 (addendum IX) |"),
    (MOD04, "| R-BUDGET-06 | Time advancement `δ_t` (pure=0, host/scheduler>0, `t+δ_t ≤ W`) | L8698–8700, L10164–10168 | U-07 open |",
             "| R-BUDGET-06 | Time advancement `δ_t` (pure=0, host/scheduler>0, `t+δ_t ≤ W`) | L8698–8700, L10164–10168 | R-BUDGET-16 (addendum IX) |"),
    (MOD04, "| R-BUDGET-13 | Persistent-capacity accounting: volatile RAM distinct from persistent storage; RAM released on scope exit/halt; durable storage retained and snapshot-compacted; overflow faults | addendum VIII (resource-accounting) | M7 snapshot-capacity tests |",
             "| R-BUDGET-13 | Persistent-capacity accounting: volatile RAM distinct from persistent storage; RAM released on scope exit/halt; durable storage retained and snapshot-compacted; overflow faults | addendum VIII (resource-accounting) | M7 snapshot-capacity tests |\n"
             "| R-BUDGET-15 | Duration consumable: per-actor D; `ΔD := δ_t` exactly once per advance; no double charge; `cost_C(E)` duration declared/diagnostic only; `δ_t > D` ⇒ `DeadlineExceeded` zero-mutation; precedence `CapabilityViolation → BudgetExhausted → DeadlineExceeded → HostPolicyDenied` (C-114/C-115 resolved) | addendum IX (duration-semantics) | M042, budget-gate tests |\n"
             "| R-BUDGET-16 | Exhaustive δ_t table (pure 0; issuance +1; receipt +1; spawn/send/receive/blocked 0; turn carries the executed δ_t; per host round trip = 2; reconciliation 0); Pending W-eligibility on each advance; late receipts settle via R-RECOV-08; stable quiescence `Deadlock ∧ ∃Pending` ⇒ driver `QuiescenceReconcile`, each pending → `Indeterminate` + R-RECOV-08 (C-112/C-113 resolved) | addendum IX (duration-semantics) | M040, M041, QUIESCENCE-RECONCILES-PENDING, ledger liveness |"),
    (MOD04, "placed audit records REQ-BUDGET-008 (`D` operational meaning; AMB-01/U-01) and",
            "placed audit records REQ-BUDGET-008 (`D` operational meaning; resolved by addendum IX\nwith R-BUDGET-15/16) and"),
    (MOD04, "Canonical text: `spec/01` S-11; addenda V, VIII. All 12 obligations `SPECIFIED`.",
            "Canonical text: `spec/01` S-11; addenda V, VIII, IX. All 14 obligations `SPECIFIED`."),
    (MOD04, "**12 obligations / 32 records.**", "**14 obligations / 32 records.**"),
    (MOD04, "API surface). Open items: U-01, U-07 (this module, blocking), U-03 (with MOD-06),\nU-13 (epoch/timestamps, MOD-13-side), U-40 (deadline predicate, MOD-08-side),\nU-45 resolved by addendum VIII (R-BUDGET-10/11/13 frozen; R-BUDGET-11 reconciled;\nR-BUDGET-12 stays with U-01; R-BUDGET-14 deferred to a resource-family pass).",
            "API surface). Resolved: U-01/U-07 (addendum IX: R-BUDGET-15/16),\nU-45 (addendum VIII). Open items: U-03 (with MOD-06),\nU-13 (epoch/timestamps, MOD-13-side), U-40 (deadline predicate, MOD-08-side),\nR-BUDGET-14 deferred to a resource-family pass; R-BUDGET-12 folded into R-BUDGET-15/16 (no own ID)."),
    # ------------------------------ ownership -----------------------------
    (OWNERSHIP, "_own(\"MOD-03\", \"CAP\",     range(1, 11))   # +CAP-10 AdmissibleConstraint (addendum V)",
                "_own(\"MOD-03\", \"CAP\",     range(1, 12))   # +CAP-10 (addendum V); +CAP-11 Lifetime logical time (addendum IX)"),
    (OWNERSHIP, "_own(\"MOD-04\", \"BUDGET\",  [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 13])   # +BUDGET-09 (addendum V); +BUDGET-10/11/13 (addendum VIII); BUDGET-12 stays with U-01",
                "_own(\"MOD-04\", \"BUDGET\",  [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 13, 15, 16])   # +BUDGET-09 (addendum V); +BUDGET-10/11/13 (addendum VIII); +BUDGET-15/16 (addendum IX); BUDGET-12 folded into 15/16"),
    (OWNERSHIP, "(\"MOD-17\", \"D semantics open - U-01\")",
                "(\"MOD-17\", \"D semantics per R-BUDGET-15 (addendum IX)\")"),
    (OWNERSHIP, "(\"MOD-17\", \"per-transition deltas open - U-07\")",
                "(\"MOD-17\", \"delta_t table per R-BUDGET-16 (addendum IX)\")"),
    (OWNERSHIP, "    \"R-BUDGET-13\": [(\"MOD-11\", \"WAL/snapshot capacity\"), (\"MOD-12\", \"snapshot compaction recovery\"), (\"MOD-10\", \"15A artifact sizes\")],",
                "    \"R-BUDGET-13\": [(\"MOD-11\", \"WAL/snapshot capacity\"), (\"MOD-12\", \"snapshot compaction recovery\"), (\"MOD-10\", \"15A artifact sizes\")],\n"
                "    \"R-CAP-11\": [(\"MOD-08\", \"gate-6 authorization computes with logical time\"), (\"MOD-04\", \"duration/deadline boundary R-BUDGET-15\"), (\"MOD-10\", \"LogicalTime canonical u64\")],\n"
                "    \"R-BUDGET-15\": [(\"MOD-08\", \"issuance/receipt side effects\"), (\"MOD-12\", \"R-RECOV-08 classification\"), (\"MOD-03\", \"max_duration declared-info boundary\")],\n"
                "    \"R-BUDGET-16\": [(\"MOD-07\", \"scheduler turn carries the executed delta_t\"), (\"MOD-09\", \"host round trip = two crossings\"), (\"MOD-12\", \"quiescence reconciliation R-RECOV-08\"), (\"MOD-11\", \"WAL/snapshot/replay delta_t = 0\")],"),
    # ------------------------------ req/_validate comment ------------------
    (VALIDATE, "    # audit (2026-09-03) then filed C-112...C-115 (open, vs U-01/U-07) -- 109 -> 113 rows;\n    # all four are re-graded by Addendum IX; no U- register change.",
               "    # audit (2026-09-03) then filed C-112...C-115 (open, vs U-01/U-07) -- 109 -> 113 rows;\n    # all five were re-graded by Addendum IX (2026-09-03): C-100 -> R-CAP-11 (U-36) and\n    # C-112...C-115 -> R-BUDGET-15/16 (U-01/U-07), resolving U-01/U-07/U-36.  The pinned\n    # counts are unchanged by a re-grading; findings are resolved, never deleted."),
    # ------------------------------ resource-accounting-audit --------------
    (RAAUDIT, "> pass; both remain non-normative proposals here. The adopted wording above is quoted, not",
              "> pass; both remain non-normative proposals here.\n>\n> **Folded (2026-09-03, addendum IX):** R-BUDGET-12's duration rule is adopted as part of\n> **R-BUDGET-15**/**R-BUDGET-16** (per-actor `D`, `\\Delta D := \\delta_t`, no double charge;\n> exhaustive `\\delta_t` table) — it still has no own ID here and this section is not a\n> normative layer. R-BUDGET-14 stays deferred. The adopted wording above is quoted, not"),
    # ------------------------------ audit status notes ---------------------
    (DURAUDIT, "(C-110/C-111 are the mutation harness's K01/K02 fixtures — reserved, unavailable).",
               "(C-110/C-111 are the mutation harness's K01/K02 fixtures — reserved, unavailable).\n" + DURAUDIT_NOTE),


    (U01SCOPING, "request-pipeline audit filed C-103…C-109 alongside its addendum.",
                 "request-pipeline audit filed C-103…C-109 alongside its addendum." + U01_NOTE),
    (U36PROP, "and only then do C-100 / C-102 move off `open` (R-SCOPE-03).",
              "and only then do C-100 / C-102 move off `open` (R-SCOPE-03)." + U36_NOTE),
    # ------------------------------ mutation harness -----------------------
    (HARNESS,
     "def m039_indeterminate_terminal(root: Path) -> bool:",
     "def m040_delta_table_violation(root: Path) -> bool:\n"
     "    \"\"\"M040 (spec/08 registry): delta_t table violation — a time-capable\n"
     "    transition kind advances logical time without its frozen delta_t (here:\n"
     "    scheduler turn double-charged). Document mutant of the addendum-IX\n"
     "    R-BUDGET-16 body; D3-detectable, survives the default wiring (U-38)\n"
     "    and dies under --allowlist.\n"
     "    \"\"\"\n"
     "    p = root / \"spec/01-canonical-specification.md\"\n"
     "    txt = p.read_text(encoding=\"utf-8\")\n"
     "    m = re.search(r\"^\\*\\*R-BUDGET-16 \\(.*$\", txt, re.M)\n"
     "    if not m:\n"
     "        return False\n"
     "    mutant = (\"**R-BUDGET-16 (logical-time delta table — frozen addendum).** \"\n"
     "              \"The lunar dial governs: every full moon the chronicle gains one day, \"\n"
     "              \"the harvest basket gains twelve grains, and the bell tower chimes twice \"\n"
     "              \"for good luck. Solstices double the tally; eclipses pause the gnomon; \"\n"
     "              \"the cartwheel spins freely in the courtyard while the comet watches.\")\n"
     "    p.write_text(txt[:m.start()] + mutant + txt[m.end():], encoding=\"utf-8\")\n"
     "    return True\n\n\n"
     "def m041_late_receipt_misclassified(root: Path) -> bool:\n"
     "    \"\"\"M041 (spec/08 registry): post-deadline receipt routed through the\n"
     "    normal deadline gate. Document mutant of the addendum-IX R-BUDGET-16\n"
     "    body; D3-detectable, survives the default wiring (U-38) and dies under\n"
     "    --allowlist.\n"
     "    \"\"\"\n"
     "    p = root / \"spec/01-canonical-specification.md\"\n"
     "    txt = p.read_text(encoding=\"utf-8\")\n"
     "    m = re.search(r\"^\\*\\*R-BUDGET-16 \\(.*$\", txt, re.M)\n"
     "    if not m:\n"
     "        return False\n"
     "    mutant = (\"**R-BUDGET-16 (logical-time delta table — frozen addendum).** \"\n"
     "              \"A courier who arrives after sunset is turned away at the garden gate; \"\n"
     "              \"his parcel rots in the rain; the mailbox swallows its own key; the \"\n"
     "              \"watchman naps on the porch and the ledger keeps no entry for the night.\")\n"
     "    p.write_text(txt[:m.start()] + mutant + txt[m.end():], encoding=\"utf-8\")\n"
     "    return True\n\n\n"
     "def m042_duration_double_charge(root: Path) -> bool:\n"
     "    \"\"\"M042 (spec/08 registry): cost_C(E)'s duration component debits D on\n"
     "    top of the transition's ΔD := δ_t. Document mutant of the addendum-IX\n"
     "    R-BUDGET-15 body; D3-detectable, survives the default wiring (U-38)\n"
     "    and dies under --allowlist.\n"
     "    \"\"\"\n"
     "    p = root / \"spec/01-canonical-specification.md\"\n"
     "    txt = p.read_text(encoding=\"utf-8\")\n"
     "    m = re.search(r\"^\\*\\*R-BUDGET-15 \\(.*$\", txt, re.M)\n"
     "    if not m:\n"
     "        return False\n"
     "    mutant = (\"**R-BUDGET-15 (duration consumable semantics — frozen addendum).** \"\n"
     "              \"Every bill is engraved on a copper plate: the grocer debits it at the \"\n"
     "              \"counter, the courier debits it again at the doorstep, and the two stamps \"\n"
     "              \"are the honest price of a journey. The vaultkeeper stamps twice on feast \"\n"
     "              \"days and the abacus never errs.\")\n"
     "    p.write_text(txt[:m.start()] + mutant + txt[m.end():], encoding=\"utf-8\")\n"
     "    return True\n\n\n"
     "def m039_indeterminate_terminal(root: Path) -> bool:"),
    (HARNESS,
     "    Mutation(\"K21\", \"Remains-Indeterminate treated as terminal (M039)\",\n"
     "             \"The M039 shape rendered as a document mutant of the addendum-VIII body. \"\n"
     "             \"Survives the default wiring (U-38) and dies under option (b), keeping the \"\n"
     "             \"totality/refinement reconciliation testable against the frozen text.\",\n"
     "             m039_indeterminate_terminal,\n"
     "             regression_for=\"M039 / R-BUDGET-11 disposition totality\",\n"
     "             tags=[\"normative\", \"allowlist\"],\n"
     "             extra_checkers=[(\"spec/_check.py\", [\"--allowlist\"])]),\n]",
     "    Mutation(\"K21\", \"Remains-Indeterminate treated as terminal (M039)\",\n"
     "             \"The M039 shape rendered as a document mutant of the addendum-VIII body. \"\n"
     "             \"Survives the default wiring (U-38) and dies under option (b), keeping the \"\n"
     "             \"totality/refinement reconciliation testable against the frozen text.\",\n"
     "             m039_indeterminate_terminal,\n"
     "             regression_for=\"M039 / R-BUDGET-11 disposition totality\",\n"
     "             tags=[\"normative\", \"allowlist\"],\n"
     "             extra_checkers=[(\"spec/_check.py\", [\"--allowlist\"])]),\n"
     "    Mutation(\"K22\", \"delta_t table violation (M040)\",\n"
     "             \"The M040 shape rendered as a document mutant of the addendum-IX body. \"\n"
     "             \"Survives the default wiring (U-38) and dies under option (b), keeping the \"\n"
     "             \"exhaustive delta_t enumeration testable against the frozen text.\",\n"
     "             m040_delta_table_violation,\n"
     "             regression_for=\"M040 / R-BUDGET-16 delta_t table\",\n"
     "             tags=[\"normative\", \"allowlist\"],\n"
     "             extra_checkers=[(\"spec/_check.py\", [\"--allowlist\"])]),\n"
     "    Mutation(\"K23\", \"post-deadline receipt misclassified (M041)\",\n"
     "             \"The M041 shape rendered as a document mutant of the addendum-IX body. \"\n"
     "             \"Survives the default wiring (U-38) and dies under option (b), keeping the \"\n"
     "             \"late-receipt settlement rule testable against the frozen text.\",\n"
     "             m041_late_receipt_misclassified,\n"
     "             regression_for=\"M041 / R-BUDGET-16 late-receipt settlement\",\n"
     "             tags=[\"normative\", \"allowlist\"],\n"
     "             extra_checkers=[(\"spec/_check.py\", [\"--allowlist\"])]),\n"
     "    Mutation(\"K24\", \"duration double charge (M042)\",\n"
     "             \"The M042 shape rendered as a document mutant of the addendum-IX body. \"\n"
     "             \"Survives the default wiring (U-38) and dies under option (b), keeping the \"\n"
     "             \"no-double-charge invariant testable against the frozen text.\",\n"
     "             m042_duration_double_charge,\n"
     "             regression_for=\"M042 / R-BUDGET-15 no-double-charge\",\n"
     "             tags=[\"normative\", \"allowlist\"],\n"
     "             extra_checkers=[(\"spec/_check.py\", [\"--allowlist\"])]),\n]"),
]

# ---------------------------------------------------------------------------
# spec/_build_index.py edits
# ---------------------------------------------------------------------------
IDX_EDITS: list[tuple[str, str]] = [
    # sections S-09 / S-11
    ('"R-CAP-09","R-CAP-10"],prov("6344-6671","6672-6815"),None),',
     '"R-CAP-09","R-CAP-10","R-CAP-11"],prov("6344-6671","6672-6815"),None),'),
    ('"R-BUDGET-11","R-BUDGET-13"],prov("8653-9050","9140-9245","28203-28240"),"U-01;U-07"),',
     '"R-BUDGET-11","R-BUDGET-13","R-BUDGET-15","R-BUDGET-16"],prov("8653-9050","9140-9245","28203-28240"),"U-01;U-07"),'),
    # requirement rows
    ('("R-CAP-10","S-09","AdmissibleConstraint defined; fault never identity (frozen addendum)","addendum",SPEC,[],["ror-kernel","ror-compiler"],["M030","compiler negative suite"],["C-94"]),',
     '("R-CAP-10","S-09","AdmissibleConstraint defined; fault never identity (frozen addendum)","addendum",SPEC,[],["ror-kernel","ror-compiler"],["M030","compiler negative suite"],["C-94"]),\n'
     '("R-CAP-11","S-09","Lifetime logical time; half-open; max_duration declared-info (frozen addendum)","addendum",SPEC,[],["ror-core","ror-kernel"],["M4 expiration/authorization gate tests"],["C-100"]),'),
    ('("R-BUDGET-13","S-11","Persistent-capacity accounting (frozen addendum)","addendum",SPEC,[],["ror-persistence"],["M7 snapshot-capacity tests"],["C-108"]),',
     '("R-BUDGET-13","S-11","Persistent-capacity accounting (frozen addendum)","addendum",SPEC,[],["ror-persistence"],["M7 snapshot-capacity tests"],["C-108"]),\n'
     '("R-BUDGET-15","S-11","Duration consumable semantics; delta_D = delta_t; no double charge (frozen addendum)","addendum",SPEC,[],["ror-core","ror-runtime"],["M042","budget-gate tests"],["C-114","C-115"]),\n'
     '("R-BUDGET-16","S-11","Exhaustive delta_t table; late-receipt settlement; quiescence reconciliation (frozen addendum)","addendum",SPEC,[],["ror-runtime"],["M040","M041","QUIESCENCE-RECONCILES-PENDING","ledger liveness"],["C-112","C-113"]),'),
    # mutations
    ('("M039","Remains-Indeterminate treated as a terminal disposition (stranded escrow survives the logical-time bound)",["R-BUDGET-11"]),',
     '("M039","Remains-Indeterminate treated as a terminal disposition (stranded escrow survives the logical-time bound)",["R-BUDGET-11"]),\n'
     '("M040","delta_t table violation: a time-capable transition kind advances logical time without its frozen delta_t",["R-BUDGET-16"]),\n'
     '("M041","post-deadline EffectReceipt routed through the normal deadline gate instead of R-RECOV-08 settlement",["R-BUDGET-16","R-RECOV-08"]),\n'
     '("M042","cost_C(E) duration component debits D in addition to the transition delta_D = delta_t",["R-BUDGET-15"]),'),
    # tags
    ('("PERSISTENT-CAPACITY-ACCOUNTING",["R-BUDGET-13","R-PERSIST-04"],"M7 (addendum VIII)"),\n]',
     '("PERSISTENT-CAPACITY-ACCOUNTING",["R-BUDGET-13","R-PERSIST-04"],"M7 (addendum VIII)"),\n'
     '("TIME-DELTA-ENUMERATED",["R-BUDGET-16","R-BUDGET-06"],"M5 (addendum IX)"),\n'
     '("DURATION-NO-DOUBLE-CHARGE",["R-BUDGET-15","R-BUDGET-01"],"M5 (addendum IX)"),\n'
     '("QUIESCENCE-RECONCILES-PENDING",["R-BUDGET-16","R-BUDGET-09","R-RECOV-08"],"M5;M10 (addendum IX)"),\n]'),
    # meta
    ('"R-AREA-NN": "normative requirement/obligation (181; 148 source-transcribed + 33 post-audit frozen addenda)"',
     '"R-AREA-NN": "normative requirement/obligation (184; 148 source-transcribed + 36 post-audit frozen addenda)"'),
    ('"TAG": "source verification-obligation tags (23; 17 frozen-source + 6 post-audit addenda)"',
     '"TAG": "source verification-obligation tags (26; 17 frozen-source + 9 post-audit addenda)"'),
    ('"M0NN": "baseline mutation registry (39; 18 baseline + 21 post-audit: M019–M039; M036 is registered and currently SURVIVING — see spec/08 §2 and U-38)"',
     '"M0NN": "baseline mutation registry (42; 18 baseline + 24 post-audit: M019–M042; M036 is registered and currently SURVIVING — see spec/08 §2 and U-38)"'),
    # milestones
    ('"R-CAP-10","R-MARSHAL-05"]),',
     '"R-CAP-10","R-CAP-11","R-MARSHAL-05"]),'),
    ('"R-BUDGET-10","R-BUDGET-11"]),',
     '"R-BUDGET-10","R-BUDGET-11","R-BUDGET-15","R-BUDGET-16"]),'),
    ('"R-RECOV-09","R-BUDGET-11"]),',
     '"R-RECOV-09","R-BUDGET-11","R-BUDGET-16"]),'),
    # crates
    ('"R-CANON-12","R-CANON-13"],[]),',
     '"R-CANON-12","R-CANON-13","R-CAP-11","R-BUDGET-15"],[]),'),
    ('"R-CAP-10","R-PERSIST-07","R-CORE-11","R-TRUST-03"],["ror-core"]),',
     '"R-CAP-10","R-CAP-11","R-PERSIST-07","R-CORE-11","R-TRUST-03"],["ror-core"]),'),
    ('"R-BUDGET-10","R-BUDGET-11"],["ror-core","ror-kernel","ror-persistence"]),',
     '"R-BUDGET-10","R-BUDGET-11","R-BUDGET-15","R-BUDGET-16"],["ror-core","ror-kernel","ror-persistence"]),'),
]

# ---------------------------------------------------------------------------
# draft/decision record
# ---------------------------------------------------------------------------
DRAFT_TEXT = (
 "# Addendum IX — Duration-semantics adoption (ADOPTED 2026-09-03)\n\n"
 "**Status:** APPLIED by `audit/spec_addendum9.py` (same discipline as addenda I–VIII).\n"
 "U-38 is deliberately NOT touched — checker-policy wiring stays separate from normative\n"
 "duration-semantics changes.\n\n"
 "**Owner decision (D1–D3/D3a, D6–D8; audit `audit/duration-semantics-audit.md`):**\n\n"
 "1. **D1 ADOPTED** — `D` is the per-actor remaining execution-duration budget; `W` remains\n"
 "   the absolute logical-time deadline; distinct, not collapsed (N-18).\n"
 "2. **D2 ADOPTED** — `ΔD := δ_t` for every logical-time-advancing transition; exactly ONE\n"
 "   duration debit per advance (explicit no-double-charge invariant); `cost_C(E)`'s duration\n"
 "   component is DECLARED/DIAGNOSTIC only, never a second debit authority.\n"
 "3. **D3 + D3a ADOPTED** — exhaustive δ_t table: pure CEK 0; issuance +1; receipt +1;\n"
 "   spawn/send/receive/blocked 0; the scheduler turn carries the executed transition's δ_t\n"
 "   (no extra turn charge); reconciliation 0; per host round trip = +2 (two crossings).\n"
 "4. **D6 ADOPTED** — deterministic `DeadlineExceeded` placement/precedence with atomic failure\n"
 "   (zero mutation): `CapabilityViolation → BudgetExhausted → DeadlineExceeded →\n"
 "   HostPolicyDenied`; late receipts use R-RECOV-08 reconciliation, never the normal deadline gate.\n"
 "5. **D7 ADOPTED (AUDITED MINIMAL RULE — §5(c))** — `Deadlock ∧ ∃Pending` ⇒ a SEPARATE\n"
 "   deterministic driver transition `QuiescenceReconcile` (δ_t = 0, ΔD = 0, no W check, no\n"
 "   budget mutation); each pending effect → `Indeterminate` + R-RECOV-08. NOT unconditional\n"
 "   quiescence reconciliation; `GlobalStep::Deadlock` itself is NOT the reconciliation\n"
 "   transition; Blocked-only quiescence admits none. This is the weakest rule making\n"
 "   R-BUDGET-09's liveness bound reachable — no clock, no timer, no per-effect counter.\n"
 "6. **D8 ADOPTED** — `Lifetime` → `LogicalTime` (half-open `[start, end)`, five Unix\n"
 "   annotations and the prose superseded-quoted, second call site L6558 recorded);\n"
 "   `max_duration` declared-info only, never a machine debit; `Deadline` stays\n"
 "   `Option<LogicalTime>` in all three declarations — no retype there.\n\n"
 "**Frozen as three obligations** (spec/01: S-09 R-CAP-11; S-11 R-BUDGET-15/16):\n\n"
 + ADD_CAP11 + "\n\n" + ADD_BUDGET15 + "\n\n" + ADD_BUDGET16 + "\n\n"
 "**Register arithmetic:** 181 → 184 obligations (+3: R-CAP-11, R-BUDGET-15, R-BUDGET-16);\n"
 "findings 112 / rows 113 unchanged (C-100, C-112…C-115 re-graded `resolved-by-addendum`,\n"
 "not deleted); U- items unchanged at 39 (U-01/U-07/U-36 resolved ≠ deleted); mutations\n"
 "39 → 42 (M040–M042); verification tags 23 → 26. R-BUDGET-12's duration rule is folded into\n"
 "R-BUDGET-15/16 (still no R-BUDGET-12 ID); R-BUDGET-14 stays deferred. U-35/U-37/U-02/U-03/\n"
 "U-08/U-09/U-38 untouched.\n\n"
 "**Acceptance invariant (asserted by the applier/verifier):** every logical-time advance has\n"
 "exactly one duration debit; every deadline-sensitive transition has a deterministic\n"
 "pre-state/post-state rule; quiescent pending effects have a deterministic wall-clock-free\n"
 "reconciliation path.\n")


def apply_edits(files: dict[Path, str]) -> dict[Path, str]:
    for path, find, repl in EDITS:
        if files[path].count(find) != 1:
            print(f"ABORT: anchor x{files[path].count(find)} (need 1) in {path.name}: {find[:80]!r}")
            sys.exit(2)
        files[path] = files[path].replace(find, repl, 1)
    build = files[BUILDIDX]
    for find, repl in IDX_EDITS:
        if build.count(find) != 1:
            print(f"ABORT: index anchor x{build.count(find)} (need 1): {find[:80]!r}")
            sys.exit(2)
        build = build.replace(find, repl, 1)
    files[BUILDIDX] = build
    files[DRAFT] = DRAFT_TEXT
    return files


def _write_regen(root: Path) -> list[str]:
    fails = []
    steps = [
        ("term/_reanchor.py", ["--write"]),
        ("spec/_build_index.py", []),
        ("mod/_build.py", ["--write"]),
        ("dep/_graph.py", ["--write"]),
    ]
    for rel, args in steps:
        p = subprocess.run([sys.executable, rel, *args], cwd=root,
                           capture_output=True, text=True, timeout=900)
        tail = (p.stdout + p.stderr).strip().splitlines()[-3:]
        print(f"  [{rel}] exit {p.returncode}: {tail}")
        if p.returncode != 0:
            fails.append(rel)
    return fails


def verify_tree(root: Path, label: str) -> bool:
    ok = True
    print(f"== {label}: regenerate ==")
    ok = _write_regen(root) == [] and ok
    print(f"== {label}: check.py (full suite incl. mutation harness) ==")
    p = subprocess.run([sys.executable, "check.py", "-q"], cwd=root,
                       capture_output=True, text=True, timeout=1800)
    print("  check.py exit", p.returncode)
    if p.returncode != 0:
        ok = False
        print("  " + "\n  ".join((p.stdout + p.stderr).strip().splitlines()[-25:]))

    idx = json.loads((root / "spec/10-index.json").read_text(encoding="utf-8"))
    blob = json.dumps(idx)
    reqs = {r["id"] for r in idx["requirements"]}
    muts = len(idx.get("mutations", []))
    tags = len(idx.get("verification_tags", []))
    findings = len(idx.get("findings", []))
    unresolved = len(idx.get("unresolved", []))
    sections = len(idx.get("sections", []))
    print(f"  index: requirements={len(reqs)} findings={findings} unresolved={unresolved} "
          f"mutations={muts} tags={tags} sections={sections}")
    for want, got, what in ((184, len(reqs), "requirements"), (112, findings, "findings"),
                            (39, unresolved, "unresolved"), (42, muts, "mutations"),
                            (26, tags, "tags"), (24, sections, "sections")):
        if got != want:
            print(f"  FAIL: {what}={got}, want {want}"); ok = False
    for rid in NEW_IDS:
        if rid not in reqs:
            print(f"  FAIL: {rid} not indexed"); ok = False
    for m in ("M040", "M041", "M042"):
        if m not in blob:
            print(f"  FAIL: {m} not in index"); ok = False
    for tag in ("TIME-DELTA-ENUMERATED", "DURATION-NO-DOUBLE-CHARGE",
                "QUIESCENCE-RECONCILES-PENDING"):
        if tag not in blob:
            print(f"  FAIL: {tag} not in index"); ok = False
    resolved = sorted(f["id"] for f in idx["findings"]
                      if f["id"] in RESOLVED_SET and f.get("status") == "resolved-by-addendum")
    if resolved != RESOLVED_SET:
        print(f"  FAIL: resolved-by-addendum C rows = {resolved}"); ok = False
    for cid, want in (("C-100", "U-36"), ("C-112", "U-01;U-07"), ("C-113", "U-01"),
                      ("C-114", "U-01"), ("C-115", "U-01")):
        got = next((f.get("resolved_into") for f in idx["findings"] if f["id"] == cid), None)
        if got != want:
            print(f"  FAIL: {cid} resolved_into = {got}, want {want}"); ok = False

    p = subprocess.run([sys.executable, "spec/_check.py", "--verbose"], cwd=root,
                       capture_output=True, text=True, timeout=600)
    new_flags = [ln.strip() for ln in (p.stdout + p.stderr).splitlines()
                 if re.search(r"\[D[23]\] (R-CAP-11|R-BUDGET-15|R-BUDGET-16)\b", ln)]
    print(f"  spec/_check.py: new-ID D2/D3 flags = {len(new_flags)} "
          f"(exit {p.returncode}, D1 hard gate)")
    if p.returncode != 0:
        print("  FAIL: spec/_check.py D1 gate"); ok = False
    if new_flags:
        for ln in new_flags[:5]:
            print("  FAIL: " + ln)
        ok = False

    spec01 = (root / "spec/01-canonical-specification.md").read_text(encoding="utf-8")
    ids = sorted(set(re.findall(r"\*\*(R-[A-Z]+-\d+)", spec01)))
    if len(ids) != 184:
        print(f"  FAIL: spec/01 obligation markers = {len(ids)}, want 184"); ok = False
    for rid in NEW_IDS:
        if rid not in ids:
            print(f"  FAIL: spec/01 missing {rid}"); ok = False
    if "**Total: 184 obligations**" not in (root / "spec/03-obligation-matrix.md").read_text(encoding="utf-8"):
        print("  FAIL: spec/03 Total not 184"); ok = False

    # acceptance invariant (as stated in audit/duration-semantics-audit.md §1)
    def _body(rid: str) -> str:
        m = re.search(r"^\*\*" + re.escape(rid) + r" .*$", spec01, re.M)
        if not m:
            print(f"  FAIL: cannot locate {rid} body")
            return ""
        return m.group(0)
    b15, b16, b11 = _body("R-BUDGET-15"), _body("R-BUDGET-16"), _body("R-CAP-11")
    invariant = [("ΔD := δ_t" in b15, "R-BUDGET-15: ΔD := δ_t"),
                 ("exactly ONE duration debit" in b15 or "exactly one duration debit" in b15,
                  "R-BUDGET-15: exactly one debit"),
                 ("no double charge" in b15.lower(), "R-BUDGET-15: no double charge"),
                 ("δ_t = 0" in b16 and "ΔD = 0" in b16, "R-BUDGET-16: quiescence driver δ_t=0/ΔD=0"),
                 ("QuiescenceReconcile" in b16, "R-BUDGET-16: QuiescenceReconcile"),
                 ("R-RECOV-08" in b16 and "Indeterminate" in b16, "R-BUDGET-16: pending -> Indeterminate + R-RECOV-08"),
                 ("superseded" in b16.lower() and "t + δ_t ≤ W" in b16, "R-BUDGET-16: late-receipt premise quoted superseded"),
                 ("start, end" in b11 and "start ≤ t ∧ t < end" in b11, "R-CAP-11: half-open [start,end)"),
                 ("Option<LogicalTime>" in b11, "R-CAP-11: Deadline stays Option<LogicalTime>"),
                 ("declared" in b11.lower() and "never a machine debit" in b11.lower(),
                  "R-CAP-11/R-BUDGET-15: max_duration declared-info only"),
                 ("GlobalStep::Deadlock" in b16 and "∧" in b16 and "`Pending`" in b16,
                  "R-BUDGET-16: rule scoped to Deadlock ∧ ∃Pending"),
                 ("Blocked-only quiescence admits NO" in b16 or "admits NO reconciliation" in b16,
                  "R-BUDGET-16: no unconditional quiescence reconciliation")]
    for good, what in invariant:
        if not good:
            print(f"  FAIL: acceptance invariant — {what}"); ok = False
    return ok


def main() -> int:
    apply_mode = "--apply" in sys.argv
    head = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=REPO,
                          capture_output=True, text=True).stdout.strip()
    if not head.startswith(BASELINE):
        print(f"ABORT: baseline assert — HEAD {head!r} is not {BASELINE!r}")
        return 2
    contra = (REPO / "spec/06-contradictions-ambiguities.md").read_text(encoding="utf-8")
    for cid, must in (("C-112", True), ("C-115", True), ("C-110", False), ("C-111", False)):
        present = re.search(r"^\| " + re.escape(cid) + r" \|", contra, re.M) is not None
        if present != must:
            print(f"ABORT: baseline assert — spec/06 row C-{cid} present={present}, want {must}")
            return 2
    print(f"baseline ok: HEAD {head}; C-112…C-115 present; C-110/C-111 reserved fixtures absent")

    targets = sorted({p for p, _, _ in EDITS} | {BUILDIDX, DRAFT})
    real = {}
    for p in targets:
        if p == DRAFT and not p.exists():
            real[p] = ""
        else:
            real[p] = p.read_text(encoding="utf-8")

    conflicts, anchors = [], []
    for rid in NEW_IDS:
        if rid in real[SPEC01]:
            conflicts.append(rid)
    for path, find, _ in EDITS:
        if real[path].count(find) != 1:
            anchors.append((path.name, find[:70]))
    for find, _ in IDX_EDITS:
        if real[BUILDIDX].count(find) != 1:
            anchors.append(("_build_index.py", find[:70]))
    if conflicts or anchors:
        if conflicts:
            print(f"ABORT: addendum already applied (spec/01: {conflicts})")
        else:
            print(f"ABORT: {len(anchors)} anchor(s) not exactly-met; tree changed?")
            for name, f in anchors[:15]:
                print(f"  {name}: {f!r}")
        return 2
    print(f"precheck ok: addendum absent; {len(EDITS) + len(IDX_EDITS)} anchors exact")

    files = apply_edits({p: real[p] for p in targets})

    if not apply_mode:
        with tempfile.TemporaryDirectory() as td:
            box = Path(td) / "repo"
            box.mkdir()
            subprocess.run(f"git archive HEAD | tar -x -C '{box}'", shell=True,
                           cwd=REPO, check=True)
            for p in targets:
                (box / p.relative_to(REPO)).write_text(files[p], encoding="utf-8")
            ok = verify_tree(box, "DRY-RUN")
            print("\nDRY RUN: " + ("PROOF COMPLETE — addendum verifies clean"
                                   if ok else "VERIFICATION FAILED"))
            return 0 if ok else 1

    for p in targets:
        p.write_text(files[p], encoding="utf-8")
    print(f"applied: {len(EDITS) + len(IDX_EDITS)} edits + draft across {len(targets)} files")
    ok = verify_tree(REPO, "POST-APPLY")
    print("\nAPPLY: " + ("VERIFIED" if ok else "VERIFICATION FAILED — inspect git diff"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
