#!/usr/bin/env python3
"""spec_addendum8.py — resource-accounting adoption applier (U-45; C-108).

Addendum VIII freezes the adopted part of `audit/resource-accounting-audit.md`
§4 (R-BUDGET-10…14) and reconciles the three-vs-five escrow-path divergence.

Owner decision (2026-09-03, recorded in audit/spec-addendum8-draft.md):

  R-BUDGET-10  ADOPTED  (resource-state atomicity; strengthens the gate matrix)
  R-BUDGET-11  ADOPTED, RECONCILED  (escrow disposition normal form: R-BUDGET-09's
               three paths are the totality; the five leaves are its complete
               refinement; `Remains-Indeterminate` is a BOUNDED transient, never
               a terminal disposition -- totality and the quiescent-strand
               invariant of R-BUDGET-09 are preserved)
  R-BUDGET-13  ADOPTED  (persistent-capacity accounting as a separate dimension)
  R-BUDGET-12  NOT ADOPTED here -- its D-advancement/debit rule decides U-01,
               which is a separate open item; stays folded into U-01.
  R-BUDGET-14  NOT ADOPTED here -- deferred to a resource-family pass
               (tagged X-vector mechanism beyond the gate-matrix scope).

This follows the audit's own recommendation (U-45 decision-needed text): adopt
R-BUDGET-10 and R-BUDGET-13 as they strengthen the gate matrix, and fold
R-BUDGET-11's extra paths into R-BUDGET-09's three as refinements rather than
competitors.

Registers: C-108 -> resolved-by-addendum; U-45 -> resolved;
spec/03 Total 178 -> 181 (148 + 33 post-audit addenda);
mutations 38 -> 39 (M039); verification tags 21 -> 23;
manual registers: README, spec/06, spec/08, spec/09, records, mod/04,
mod/_ownership, req/_validate comment, resource-accounting-audit.md status
note, spec/_build_index.py, audit/_checker_mutations.py (K21).

U-38 is NOT touched (separate checker-policy decision).
Same discipline as addenda I-VII; see spec_addendum7.py.
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
MOD04 = REPO / "mod" / "04-budget.md"
HARNESS = REPO / "audit" / "_checker_mutations.py"
RAAUDIT = REPO / "audit" / "resource-accounting-audit.md"
DRAFT = REPO / "audit" / "spec-addendum8-draft.md"

NEW_IDS = ["R-BUDGET-10", "R-BUDGET-11", "R-BUDGET-13"]
MARKERS = NEW_IDS + ["M039", "BUDGET-ESCROW-DISPOSITION-TOTALITY",
                     "PERSISTENT-CAPACITY-ACCOUNTING", "addendum VIII",
                     "R-BUDGET-12"
                     " stays with U-01"]

# ---------------------------------------------------------------------------
# frozen addendum texts (single-line bodies, matching the spec/01 style;
# adopted wording is quoted from the audit per R-SCOPE-03; R-BUDGET-11 is the
# reconciled decision wording)
# ---------------------------------------------------------------------------

ADD_BUDGET10 = ("**R-BUDGET-10 (resource-state atomicity — frozen addendum).** All resource "
 "mutations belonging to an operational transition occur transactionally: a failed precondition "
 "produces zero state drift and zero partial debit — `Precondition failure ⇒ Σ' = Σ` — except for "
 "post-issuance host-failure transitions, where `c_issue` remains consumed and the escrow is disposed "
 "via host-failure consumption/refund (R-DUR-07, R-BUDGET-11). This is the resource-level refinement "
 "of R-CORE-12's transition atomicity and R-CORE-14's s12–s14b atomic section: every Op-01…Op-22 "
 "transition is a single atomic resource mutation, and the `audit/_conservation_checker.py` "
 "randomized-transition harness is the gate evidence. *(Frozen addendum VIII — resource-accounting "
 "audit, owner decision 2026-09-03; additive per R-SCOPE-03; extends R-CORE-05/12, R-DUR-07; "
 "resolves C-108, decision U-45; no source transcription.)*")

ADD_BUDGET11 = ("**R-BUDGET-11 (escrow disposition normal form — frozen addendum).** R-BUDGET-09's "
 "three paths are the escrow-disposition totality: every escrowed amount terminates via `Completed`, "
 "host-failure consumption, or durable `Reconciled`; the five-path normal form (`Consumed`, `Refunded`, `Transferred`, `Disposed-with-explicit-sink`, `Remains-Indeterminate`) is the complete "
 "fine structure OF that totality, not a fifth terminal path. `Consumed` (`C_consumed`) and "
 "`Refunded` (`C_available`) are the two leaves of `Completed` and of host-failure consumption "
 "(`actual ≤ complete_max` charged, remainder refunded; R-DUR-07). `Transferred` (child available "
 "partition) and `Disposed-with-explicit-sink` (`C_disposed` / `C_supervisor`) are the reconciled-outcome "
 "leaves selected per the R-RECOV-08 admissible-outcome table. `Remains-Indeterminate` (awaiting "
 "authoritative reconciliation) is a BOUNDED transient, not a disposition: it MUST reach reconciliation "
 "by the R-BUDGET-09 logical-time bound (machine state only, R-CAP-09) and then terminate via one of "
 "the four terminal leaves. No escrow may remain in any leaf indefinitely — the R-BUDGET-09 "
 "quiescent-strand invariant holds, and `C_available + C_escrowed + C_consumed + C_disposed = "
 "C_initial` at every reachable point. *(Frozen addendum VIII — resource-accounting audit, owner "
 "decision 2026-09-03; additive per R-SCOPE-03; extends R-BUDGET-09, R-DUR-05/07, R-EFFECT-05, "
 "R-RECOV-08/09; resolves C-108, decision U-45; mutation M039; no source transcription.)*")

ADD_BUDGET13 = ("**R-BUDGET-13 (persistent-capacity accounting — frozen addendum).** Volatile RAM "
 "(`MEMORY` `M`) is kept strictly distinct from persistent storage capacity (`PERSISTENT_STORAGE` "
 "`M_storage`): RAM is released on scope exit or actor halt, while durable storage is retained across "
 "actor halts and managed via snapshot compaction (R-PERSIST-05/07, R-BUDGET-03 reservation "
 "predicates apply to each dimension separately). Persistent capacity MUST be accounted per WAL frame "
 "and per snapshot artifact; a snapshot that would exceed `M_storage` MUST fault, never silently "
 "truncate. *(Frozen addendum VIII — resource-accounting audit, owner decision 2026-09-03; additive "
 "per R-SCOPE-03; extends R-BUDGET-03/05, R-PERSIST-04/05/07; resolves C-108, decision U-45; no source "
 "transcription.)*")

# ---------------------------------------------------------------------------
# spec/03 rows (6 cells)
# ---------------------------------------------------------------------------
ROW_10 = "| R-BUDGET-10 | Resource-state atomicity: every Op transition is one transactional resource mutation; precondition failure ⇒ `Σ' = Σ` (zero drift, zero partial debit); post-issuance host-failure caveat (C-108 resolved; U-45) | addendum (resource-accounting) | SPECIFIED | ror-runtime, ror-persistence | Op-01…Op-22 atomicity harness (conservation checker) |"
ROW_11 = "| R-BUDGET-11 | Escrow disposition normal form (RECONCILED): R-BUDGET-09's three paths are the totality; Consumed/Refunded are its completion leaves, Transferred/Disposed-with-explicit-sink its reconciled leaves; `Remains-Indeterminate` is a bounded transient, never terminal (C-108 resolved; U-45) | addendum (resource-accounting) | SPECIFIED | ror-runtime (classification), ror-persistence (records) | M039, ledger liveness, T0–T6 |"
ROW_13 = "| R-BUDGET-13 | Persistent-capacity accounting: volatile RAM distinct from persistent storage; RAM released on scope exit/halt; durable storage retained and snapshot-compacted; overflow faults (C-108 resolved; U-45) | addendum (resource-accounting) | SPECIFIED | ror-persistence | M7 snapshot-capacity tests |"

TOTAL_OLD = ("**Total: 178 obligations** (148 transcribed from the frozen source + 30 post-audit frozen "
 "addenda: R-ARCH-05, R-ACTOR-09, R-ACTOR-10, R-BUDGET-09, R-CANON-12, R-CANON-13, R-CAP-10, "
 "R-COMPILE-06, R-CORE-11, R-CORE-12, R-CORE-13, R-CORE-14, R-DUR-06, R-DUR-07, R-EFFECT-08, "
 "R-HOST-06, R-KERN-04, R-KERN-05, R-KERN-06, R-MARSHAL-05, R-MARSHAL-06, R-PERSIST-07, R-PERSIST-08, "
 "R-PLANNER-06, R-PLANNER-07, R-RECOV-08, R-RECOV-09, R-TEST-12, R-TRUST-04, R-TRUST-05).")
TOTAL_NEW = ("**Total: 181 obligations** (148 transcribed from the frozen source + 33 post-audit frozen "
 "addenda: R-ARCH-05, R-ACTOR-09, R-ACTOR-10, R-BUDGET-09, R-BUDGET-10, R-BUDGET-11, R-BUDGET-13, "
 "R-CANON-12, R-CANON-13, R-CAP-10, R-COMPILE-06, R-CORE-11, R-CORE-12, R-CORE-13, R-CORE-14, "
 "R-DUR-06, R-DUR-07, R-EFFECT-08, R-HOST-06, R-KERN-04, R-KERN-05, R-KERN-06, R-MARSHAL-05, "
 "R-MARSHAL-06, R-PERSIST-07, R-PERSIST-08, R-PLANNER-06, R-PLANNER-07, R-RECOV-08, R-RECOV-09, "
 "R-TEST-12, R-TRUST-04, R-TRUST-05).")

# ---------------------------------------------------------------------------
# spec/06: C-108 status cell + the addendum-block paragraph tail
# ---------------------------------------------------------------------------
C108_OLD = ("R-BUDGET-09 (three escrow paths) vs R-BUDGET-11 (five paths incl. Transferred and "
 "Disposed) | corrected-in-place (provenance recorded) |")
C108_NEW = ("R-BUDGET-09 (three escrow paths) vs R-BUDGET-11 (five paths incl. Transferred and "
 "Disposed) | **resolved-by-addendum** → `R-BUDGET-10/11/13` (U-45) |")

C06_TAIL_OLD = ("C-108 remains **corrected-in-place** and U-45 is explicitly DEFERRED to a dedicated "
 "pass (candidate addendum VIII): addendum VII does not pre-empt the R-BUDGET-10…14 adoption or the "
 "three-vs-five escrow-path reconciliation.")
C06_TAIL_NEW = ("C-108 was then re-graded **`resolved-by-addendum`** by addendum VIII (owner decision "
 "2026-09-03, `audit/spec-addendum8-draft.md`): R-BUDGET-10 (resource-state atomicity), R-BUDGET-11 "
 "(escrow disposition normal form, reconciled as the five-leaf refinement of R-BUDGET-09's three-path "
 "totality — `Remains-Indeterminate` is a bounded transient, never a terminal disposition) and "
 "R-BUDGET-13 (persistent-capacity accounting) are frozen; R-BUDGET-12 stays as a proposal folded into "
 "U-01 and R-BUDGET-14 is deferred to a resource-family pass.")

# ---------------------------------------------------------------------------
# spec/09 U-45 resolution bullet + process note 11
# ---------------------------------------------------------------------------
U45_RESOLVE = ("- **Resolved (addendum VIII, 2026-09-03):** `R-BUDGET-10` (resource-state atomicity), "
 "`R-BUDGET-11` (escrow disposition normal form, RECONCILED: R-BUDGET-09's three paths are the "
 "totality; `Consumed`/`Refunded` are its completion leaves, `Transferred`/`Disposed-with-explicit-sink` "
 "its reconciled leaves; `Remains-Indeterminate` is a bounded transient, never a terminal disposition) "
 "and `R-BUDGET-13` (persistent-capacity accounting) are frozen as addendum VIII; `spec/06` C-108 "
 "re-graded `resolved-by-addendum`. Per this item's own recommendation, R-BUDGET-11's extra paths are "
 "refinements of the three-path totality, not competitors. **R-BUDGET-12 is deliberately NOT frozen "
 "here** — its D-advancement/debit rule decides U-01, which stays a separate open item; "
 "**R-BUDGET-14 is deferred** to a resource-family pass.")

NOTE11 = ("11. **Addendum VIII adopted 2026-09-03** (U-45 / C-108): R-BUDGET-10, R-BUDGET-11 "
 "(reconciled) and R-BUDGET-13 are frozen as addendum VIII — three obligations, Total 178 → 181, "
 "mutation M039 and tags `BUDGET-ESCROW-DISPOSITION-TOTALITY`/`PERSISTENT-CAPACITY-ACCOUNTING` "
 "registered, C-108 re-graded `resolved-by-addendum`. R-BUDGET-12 remains a proposal folded into U-01; "
 "R-BUDGET-14 is deferred to a resource-family pass. Decision record: `audit/spec-addendum8-draft.md`.")

# ---------------------------------------------------------------------------
# edit table
# ---------------------------------------------------------------------------
EDITS: list[tuple[Path, str, str]] = [
    # ------------------------------ spec/01 --------------------------------
    (SPEC01, "*(Frozen addendum — post-audit remediation SEC-021; additive per R-SCOPE-03; extends R-DUR-05/R-EFFECT-05/R-RECOV-08; resolves C-97; mutation M035; no source transcription.)*",
             "*(Frozen addendum — post-audit remediation SEC-021; additive per R-SCOPE-03; extends R-DUR-05/R-EFFECT-05/R-RECOV-08; resolves C-97; mutation M035; no source transcription.)*\n\n" + ADD_BUDGET10 + "\n\n" + ADD_BUDGET11 + "\n\n" + ADD_BUDGET13),
    # ------------------------------ spec/03 --------------------------------
    (MATRIX, "| R-BUDGET-09 | Escrow disposition totality: every escrowed unit leaves via exactly one frozen path (Completed / host-failure consumption / durable Reconciled); live faults unified with crash reconciliation; logical-time deadline bound to Indeterminate; no quiescent strand (C-97 resolved; M035) | addendum (SEC-021) | SPECIFIED | ror-runtime, ror-persistence | M035, ledger liveness, mixed crash+live harness |",
             "| R-BUDGET-09 | Escrow disposition totality: every escrowed unit leaves via exactly one frozen path (Completed / host-failure consumption / durable Reconciled); live faults unified with crash reconciliation; logical-time deadline bound to Indeterminate; no quiescent strand (C-97 resolved; M035) | addendum (SEC-021) | SPECIFIED | ror-runtime, ror-persistence | M035, ledger liveness, mixed crash+live harness |\n" + ROW_10 + "\n" + ROW_11 + "\n" + ROW_13),
    (MATRIX, TOTAL_OLD, TOTAL_NEW),
    # ------------------------------ spec/06 --------------------------------
    (CONTRA, C108_OLD, C108_NEW),
    (CONTRA, C06_TAIL_OLD, C06_TAIL_NEW),
    # ------------------------------ spec/08 --------------------------------
    (VMAP, "## 2. Mutation registry → obligation map (M001–M038, R-TEST-04)",
           "## 2. Mutation registry → obligation map (M001–M039, R-TEST-04)"),
    (VMAP, "| M038 | issuance records carry `{id, actor, digest}` only (loss of the escrow/effect source of truth) | R-DUR-06 |",
           "| M038 | issuance records carry `{id, actor, digest}` only (loss of the escrow/effect source of truth) | R-DUR-06 |\n"
           "| M039 | `Remains-Indeterminate` treated as a terminal disposition (stranded escrow survives the logical-time bound) | R-BUDGET-11 |"),
    (VMAP, "(not part of the frozen source set; added by remediations SEC-001/SEC-004 and addendum VII):",
           "(not part of the frozen source set; added by remediations SEC-001/SEC-004 and addenda VII/VIII):"),
    (VMAP, "| `RECOVERY-REVOCATION-DURABLE` | R-PERSIST-07 (post-audit addendum) | Revocation survives crash: crash matrix T0–T6 with revocation committed before the crash point; revoked caps stay revoked; dangling/generation-mismatched CapRefs ⇒ `RecoveryFault` (mutation M023) | NONE |",
           "| `RECOVERY-REVOCATION-DURABLE` | R-PERSIST-07 (post-audit addendum) | Revocation survives crash: crash matrix T0–T6 with revocation committed before the crash point; revoked caps stay revoked; dangling/generation-mismatched CapRefs ⇒ `RecoveryFault` (mutation M023) | NONE |\n"
           "| `BUDGET-ESCROW-DISPOSITION-TOTALITY` | R-BUDGET-09, R-BUDGET-11 (addendum VIII), R-EFFECT-05 | Every escrowed amount terminates: R-BUDGET-09's three-path totality with the five-leaf normal form as fine structure; `Remains-Indeterminate` bounded by the logical-time bound (mutation M039) | NONE |\n"
           "| `PERSISTENT-CAPACITY-ACCOUNTING` | R-BUDGET-13 (addendum VIII), R-PERSIST-04 | Volatile RAM distinct from persistent storage; durable capacity accounted per WAL frame/snapshot artifact; overflow faults | NONE |"),
    (VMAP, "**Evidence status:** registry is `SPECIFIED` (frozen content). No mutant is registered, injected, or killed in this repository; `MutationKillRate` is **not measured** (nothing to measure). 100% is a target, not a current claim (R-CLAIM-01). M037/M038 (addendum VII) are registered the same way — machine mutants, unmeasurable in BOOTSTRAP; their document-mutant shapes are exercised by `audit/_checker_mutations.py` K19/K20. M036 remains the one measurable document mutant.",
           "**Evidence status:** registry is `SPECIFIED` (frozen content). No mutant is registered, injected, or killed in this repository; `MutationKillRate` is **not measured** (nothing to measure). 100% is a target, not a current claim (R-CLAIM-01). M037/M038 (addendum VII) and M039 (addendum VIII) are registered the same way — machine mutants, unmeasurable in BOOTSTRAP; their document-mutant shapes are exercised by `audit/_checker_mutations.py` K19/K20/K21. M036 remains the one measurable document mutant."),
    # ------------------------------ spec/09 --------------------------------
    (UNRES, "- **Decision (2026-09-03, addendum VII):** DEFERRED to a dedicated pass (candidate addendum VIII). Addendum VII does not pre-empt the R-BUDGET-10…14 adoption or the three-vs-five escrow-path reconciliation; `spec/06` C-108 stays **corrected-in-place** and this item remains OPEN.",
            "- **Decision (2026-09-03, addendum VII):** DEFERRED to a dedicated pass (candidate addendum VIII). Addendum VII does not pre-empt the R-BUDGET-10…14 adoption or the three-vs-five escrow-path reconciliation; `spec/06` C-108 stays **corrected-in-place** and this item remains OPEN.\n" + U45_RESOLVE),
    (UNRES, "the decision record is `audit/spec-addendum7-draft.md`.",
            "the decision record is `audit/spec-addendum7-draft.md`.\n\n" + NOTE11),
    # ------------------------------ records --------------------------------
    (RECORDS, "The same holds for the five addendum-VII obligations (`R-CORE-14`, `R-DUR-06`, `R-DUR-07`, `R-RECOV-09`, `R-TEST-12`; request-pipeline remediation) — each is its own original, no substitution.",
              "The same holds for the five addendum-VII obligations (`R-CORE-14`, `R-DUR-06`, `R-DUR-07`, `R-RECOV-09`, `R-TEST-12`; request-pipeline remediation) — each is its own original, no substitution. The same holds for the three addendum-VIII obligations (`R-BUDGET-10`, `R-BUDGET-11`, `R-BUDGET-13`; resource-accounting remediation) — each is its own original, no substitution."),
    # ------------------------------ README --------------------------------
    (README, "spec/03-obligation-matrix.md` — 178 stable requirement IDs (`R-…`; 148 from the frozen source + 30 post-audit frozen addenda, incl. the five addendum-VII obligations) with status and provenance",
             "spec/03-obligation-matrix.md` — 181 stable requirement IDs (`R-…`; 148 from the frozen source + 33 post-audit frozen addenda, incl. the five addendum-VII and three addendum-VIII obligations) with status and provenance"),
    (README, "C-103…C-107/C-109 `resolved-by-addendum` under addendum VII, C-108 corrected in place with U-45 deferred;",
             "C-103…C-107/C-109 `resolved-by-addendum` under addendum VII and C-108 under addendum VIII;"),
    (README, "U-39…U-44 resolved by addendum VII and U-45 deferred; U-08 corrected",
             "U-39…U-44 resolved by addendum VII and U-45 by addendum VIII; U-08 corrected"),
    # ------------------------------ mod/04 --------------------------------
    (MOD04, "| R-BUDGET-09 | Escrow disposition totality: every escrowed unit leaves via exactly one frozen path (Completed / host-failure consumption / durable Reconciled); live faults unified with crash reconciliation; logical-time deadline bound to Indeterminate; no quiescent strand (C-97 resolved; M035) | addendum V (SEC-021) | M035, ledger liveness, mixed crash+live harness |",
            "| R-BUDGET-09 | Escrow disposition totality: every escrowed unit leaves via exactly one frozen path (Completed / host-failure consumption / durable Reconciled); live faults unified with crash reconciliation; logical-time deadline bound to Indeterminate; no quiescent strand (C-97 resolved; M035) | addendum V (SEC-021) | M035, ledger liveness, mixed crash+live harness |\n"
            "| R-BUDGET-10 | Resource-state atomicity: every Op transition is one transactional resource mutation; precondition failure ⇒ `Σ' = Σ` (C-108 resolved) | addendum VIII (resource-accounting) | Op-01…Op-22 atomicity harness |\n"
            "| R-BUDGET-11 | Escrow disposition normal form (RECONCILED): R-BUDGET-09's three paths are the totality; Consumed/Refunded are its completion leaves; Transferred/Disposed-with-explicit-sink its reconciled leaves; `Remains-Indeterminate` is a bounded transient (C-108 resolved) | addendum VIII (resource-accounting) | M039, ledger liveness, T0–T6 |\n"
            "| R-BUDGET-13 | Persistent-capacity accounting: volatile RAM distinct from persistent storage; RAM released on scope exit/halt; durable storage retained and snapshot-compacted; overflow faults | addendum VIII (resource-accounting) | M7 snapshot-capacity tests |"),
    (MOD04, "(adoption of the R-BUDGET-10…14 resource-accounting proposal — `spec/06` C-108;\n  its five-path escrow normal form conflicts with this module's R-BUDGET-09 totality).",
            "(resolved by addendum VIII 2026-09-03: R-BUDGET-10/11/13 frozen; R-BUDGET-11\n  reconciled as the five-leaf refinement of the three-path totality; R-BUDGET-12 stays\n  with U-01; R-BUDGET-14 deferred to a resource-family pass)."),
    (MOD04, "U-45 (R-BUDGET-10…14 adoption, audit proposal — not normative until decided).",
            "U-45 resolved by addendum VIII (R-BUDGET-10/11/13 frozen; R-BUDGET-11 reconciled;\nR-BUDGET-12 stays with U-01; R-BUDGET-14 deferred to a resource-family pass)."),
    (MOD04, "Canonical text: `spec/01` S-11; addendum V. All 9 obligations `SPECIFIED`.",
            "Canonical text: `spec/01` S-11; addenda V, VIII. All 12 obligations `SPECIFIED`."),
    (MOD04, "**9 obligations / 32 records.**", "**12 obligations / 32 records.**"),
    # ------------------------------ ownership -----------------------------
    (OWNERSHIP, "_own(\"MOD-04\", \"BUDGET\",  range(1, 10))   # +BUDGET-09 escrow totality (addendum V)",
                "_own(\"MOD-04\", \"BUDGET\",  [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 13])   # +BUDGET-09 (addendum V); +BUDGET-10/11/13 (addendum VIII); BUDGET-12 stays with U-01"),
    (OWNERSHIP, "    \"R-CORE-05\": [(\"MOD-04\", \"operative owner (D-02)\"), (\"MOD-12\", \"survives crash (R-RECOV-06)\"), (\"MOD-06\", \"spawn transfer, not creation\")],",
                "    \"R-CORE-05\": [(\"MOD-04\", \"operative owner (D-02)\"), (\"MOD-12\", \"survives crash (R-RECOV-06)\"), (\"MOD-06\", \"spawn transfer, not creation\")],\n"
                "    \"R-BUDGET-10\": [(\"MOD-08\", \"issuance section atomicity R-DUR-07\"), (\"MOD-01\", \"R-CORE-12 transition atomicity\"), (\"MOD-11\", \"journal append/fsync\"), (\"MOD-12\", \"host-failure recovery\")],\n"
                "    \"R-BUDGET-11\": [(\"MOD-08\", \"escrow at issuance R-EFFECT-05\"), (\"MOD-12\", \"R-RECOV-08/09 admissibility\"), (\"MOD-01\", \"conservation R-CORE-05\"), (\"MOD-06\", \"spawn/transfer partition\")],\n"
                "    \"R-BUDGET-13\": [(\"MOD-11\", \"WAL/snapshot capacity\"), (\"MOD-12\", \"snapshot compaction recovery\"), (\"MOD-10\", \"15A artifact sizes\")],"),
    # ------------------------------ req/_validate comment ------------------
    (VALIDATE, "    # corrected-in-place with U-45 deferred to a dedicated pass.",
               "    # corrected-in-place with U-45 deferred to a dedicated pass.  Addendum VIII\n"
               "    # (2026-09-03) then froze R-BUDGET-10/11/13 and re-graded C-108 resolved-by-addendum;\n"
               "    # R-BUDGET-12 stays with U-01 and R-BUDGET-14 is deferred.  Counts unchanged."),
    # ------------------------------ resource-accounting-audit --------------
    (RAAUDIT, "> **STATUS NOTE (2026-09-03, per `spec/06` C-108):** the five obligations below are a\n> **proposal owned by this audit**, not frozen normative text. They appear in no\n> normative layer: `spec/01` S-11 ends at R-BUDGET-09, `mod/04` lists nine obligations,\n> `spec/03` has no R-BUDGET-10+ row, and the atomic registry stops at REQ-BUDGET-032.\n> R-BUDGET-11's five escrow paths also diverge from the frozen R-BUDGET-09 three-path\n> totality. The adoption decision (freeze some or all of R-BUDGET-10…14, and reconcile\n> three vs five escrow paths) is filed as `spec/09` **U-45**; until then, no checker or\n> implementation may cite these IDs as obligations. The wording above is quoted, not\n> rewritten (R-SCOPE-03).",
              "> **STATUS (2026-09-03, adopted by addendum VIII, per `spec/09` U-45 / `spec/06` C-108):**\n> **R-BUDGET-10, R-BUDGET-11 (reconciled) and R-BUDGET-13 ARE FROZEN** — `spec/01` S-11,\n> `spec/03`, `mod/04`, the index and the registers now carry them (Total 178 → 181). The\n> reconciliation: R-BUDGET-09's three paths remain the totality, and the five-path normal\n> form is that totality's complete fine structure — `Remains-Indeterminate` is a BOUNDED\n> transient (logical-time bound → reconciliation), never a terminal disposition, so no\n> divergence remains. **R-BUDGET-12 is NOT adopted** (its D-advancement/debit rule decides\n> `spec/09` U-01, a separate open item) and **R-BUDGET-14 is deferred** to a resource-family\n> pass; both remain non-normative proposals here. The adopted wording above is quoted, not\n> rewritten (R-SCOPE-03), except R-BUDGET-11 which carries the reconciled owner decision."),
    # ------------------------------ mutation harness -----------------------
    (HARNESS,
     "def m_m036_under_allowlist(root: Path) -> bool:",
     "def m039_indeterminate_terminal(root: Path) -> bool:\n"
     "    \"\"\"M039 (spec/08 registry): `Remains-Indeterminate` treated as a terminal\n"
     "    disposition (stranded escrow survives the logical-time bound). Document\n"
     "    mutant of the addendum-VIII R-BUDGET-11 body; D3-detectable, survives the\n"
     "    default wiring (U-38) and dies under --allowlist.\n"
     "    \"\"\"\n"
     "    p = root / \"spec/01-canonical-specification.md\"\n"
     "    txt = p.read_text(encoding=\"utf-8\")\n"
     "    m = re.search(r\"^\\*\\*R-BUDGET-11 \\(.*$\", txt, re.M)\n"
     "    if not m:\n"
     "        return False\n"
     "    mutant = (\"**R-BUDGET-11 (escrow disposition normal form — frozen addendum).** \"\n"
     "              \"`Remains-Indeterminate` is a permanent parking state: pending ledger \"\n"
     "              \"truth is sampled once, cached forever, and the escrow basket is sealed \"\n"
     "              \"with wax, guarded by three sentinels, and never reopened. Stranded \"\n"
     "              \"units accumulate silently into the vault; the nightly audit sweep \"\n"
     "              \"skips them entirely; the ledger keeps no tombstone; cursor ordering \"\n"
     "              \"is irrelevant; checksums are decorative.\")\n"
     "    p.write_text(txt[:m.start()] + mutant + txt[m.end():], encoding=\"utf-8\")\n"
     "    return True\n\n\n"
     "def m_m036_under_allowlist(root: Path) -> bool:"),
    (HARNESS,
     "             extra_checkers=[(\"spec/_check.py\", [\"--allowlist\"])]),\n]",
     "             extra_checkers=[(\"spec/_check.py\", [\"--allowlist\"])]),\n"
     "    Mutation(\"K21\", \"Remains-Indeterminate treated as terminal (M039)\",\n"
     "             \"The M039 shape rendered as a document mutant of the addendum-VIII body. \"\n"
     "             \"Survives the default wiring (U-38) and dies under option (b), keeping the \"\n"
     "             \"totality/refinement reconciliation testable against the frozen text.\",\n"
     "             m039_indeterminate_terminal,\n"
     "             regression_for=\"M039 / R-BUDGET-11 disposition totality\",\n"
     "             tags=[\"normative\", \"allowlist\"],\n"
     "             extra_checkers=[(\"spec/_check.py\", [\"--allowlist\"])]),\n]"),
]

# ---------------------------------------------------------------------------
# spec/_build_index.py edits
# ---------------------------------------------------------------------------
IDX_EDITS: list[tuple[str, str]] = [
    # section S-11
    ('"R-BUDGET-08","R-BUDGET-09"],prov("8653-9050","9140-9245","28203-28240"),"U-01;U-07"),',
     '"R-BUDGET-08","R-BUDGET-09","R-BUDGET-10","R-BUDGET-11","R-BUDGET-13"],prov("8653-9050","9140-9245","28203-28240"),"U-01;U-07"),'),
    # requirement rows
    ('("R-BUDGET-09","S-11","Escrow disposition totality incl. live faults (frozen addendum)","addendum",SPEC,[],["ror-runtime","ror-persistence"],["M035","ledger liveness","mixed crash+live harness"],["C-97"]),',
     '("R-BUDGET-09","S-11","Escrow disposition totality incl. live faults (frozen addendum)","addendum",SPEC,[],["ror-runtime","ror-persistence"],["M035","ledger liveness","mixed crash+live harness"],["C-97"]),\n'
     '("R-BUDGET-10","S-11","Resource-state atomicity (frozen addendum)","addendum",SPEC,[],["ror-runtime","ror-persistence"],["Op-01..Op-22 atomicity harness"],["C-108"]),\n'
     '("R-BUDGET-11","S-11","Escrow disposition normal form, reconciled (frozen addendum)","addendum",SPEC,[],["ror-runtime","ror-persistence"],["M039","ledger liveness","T0-T6"],["C-108"]),\n'
     '("R-BUDGET-13","S-11","Persistent-capacity accounting (frozen addendum)","addendum",SPEC,[],["ror-persistence"],["M7 snapshot-capacity tests"],["C-108"]),'),
    # mutations
    ('("M038","issuance records carry id/actor/digest only (loss of the escrow/effect source of truth)",["R-DUR-06"]),',
     '("M038","issuance records carry id/actor/digest only (loss of the escrow/effect source of truth)",["R-DUR-06"]),\n'
     '("M039","Remains-Indeterminate treated as a terminal disposition (stranded escrow survives the logical-time bound)",["R-BUDGET-11"]),'),
    # tags
    ('("REQUEST-NON-CAP-SHORT-CIRCUIT",["R-EFFECT-04","R-TEST-12"],"M5 (addendum VII)"),\n]',
     '("REQUEST-NON-CAP-SHORT-CIRCUIT",["R-EFFECT-04","R-TEST-12"],"M5 (addendum VII)"),\n'
     '("BUDGET-ESCROW-DISPOSITION-TOTALITY",["R-BUDGET-09","R-BUDGET-11","R-EFFECT-05"],"M5;M10 (addendum VIII)"),\n'
     '("PERSISTENT-CAPACITY-ACCOUNTING",["R-BUDGET-13","R-PERSIST-04"],"M7 (addendum VIII)"),\n]'),
    # meta
    ('"R-AREA-NN": "normative requirement/obligation (178; 148 source-transcribed + 30 post-audit frozen addenda)"',
     '"R-AREA-NN": "normative requirement/obligation (181; 148 source-transcribed + 33 post-audit frozen addenda)"'),
    ('"TAG": "source verification-obligation tags (21; 17 frozen-source + 4 post-audit addenda)"',
     '"TAG": "source verification-obligation tags (23; 17 frozen-source + 6 post-audit addenda)"'),
    ('"M0NN": "baseline mutation registry (38; 18 baseline + 20 post-audit: M019–M038; M036 is registered and currently SURVIVING — see spec/08 §2 and U-38)"',
     '"M0NN": "baseline mutation registry (39; 18 baseline + 21 post-audit: M019–M039; M036 is registered and currently SURVIVING — see spec/08 §2 and U-38)"'),
    # milestones
    ('"R-DUR-07","R-RECOV-09","R-TEST-12"]),',
     '"R-DUR-07","R-RECOV-09","R-TEST-12","R-BUDGET-10","R-BUDGET-11"]),'),
    ('"R-PERSIST-07","R-PERSIST-08"]),',
     '"R-PERSIST-07","R-PERSIST-08","R-BUDGET-13"]),'),
    ('"R-PERSIST-07","R-RECOV-08","R-RECOV-09"]),',
     '"R-PERSIST-07","R-RECOV-08","R-RECOV-09","R-BUDGET-11"]),'),
    # crates
    ('"R-ARCH-05","R-DUR-07"],["ror-core","ror-kernel","ror-persistence"]),',
     '"R-ARCH-05","R-DUR-07","R-BUDGET-10","R-BUDGET-11"],["ror-core","ror-kernel","ror-persistence"]),'),
    ('"R-HOST-06","R-RECOV-08","R-RECOV-09"],["ror-core"]),',
     '"R-HOST-06","R-RECOV-08","R-RECOV-09","R-BUDGET-10","R-BUDGET-11","R-BUDGET-13"],["ror-core"]),'),
]

# ---------------------------------------------------------------------------
# draft/decision record
# ---------------------------------------------------------------------------
DRAFT_TEXT = (
 "# Addendum VIII — Resource-accounting adoption (ADOPTED 2026-09-03)\n\n"
 "**Status:** APPLIED by `audit/spec_addendum8.py` (same discipline as addenda I–VII).\n"
 "U-38 is deliberately NOT touched — checker-policy wiring stays separate from normative\n"
 "resource-accounting changes.\n\n"
 "**Owner decision (U-45 / C-108):**\n\n"
 "1. **R-BUDGET-10 ADOPTED** — resource-state atomicity (every Op transition is one\n"
 "   transactional resource mutation; `Precondition failure ⇒ Σ' = Σ`, with the explicit\n"
 "   post-issuance host-failure caveat). Strengthens the gate matrix.\n"
 "2. **R-BUDGET-11 ADOPTED, RECONCILED** — the escrow disposition normal form. R-BUDGET-09's\n"
 "   three paths REMAIN the totality; `Consumed`/`Refunded` are its completion leaves;\n"
 "   `Transferred`/`Disposed-with-explicit-sink` its reconciled leaves; `Remains-Indeterminate`\n"
 "   is a BOUNDED transient (logical-time bound → reconciliation), never a terminal disposition.\n"
 "   No divergence from R-BUDGET-09 remains and no amendment to it is required.\n"
 "3. **R-BUDGET-13 ADOPTED** — persistent-capacity accounting as a dimension separate from\n"
 "   volatile RAM (release on scope exit/halt; durable storage retained and snapshot-compacted;\n"
 "   overflow faults).\n"
 "4. **R-BUDGET-12 NOT ADOPTED** — its D-advancement/debit rule decides `spec/09` U-01, a\n"
 "   separate open item; folded into U-01. Remains a non-normative proposal here.\n"
 "5. **R-BUDGET-14 NOT ADOPTED** — deferred to a resource-family pass (tagged X-vector\n"
 "   mechanism beyond the gate-matrix scope). Remains a non-normative proposal here.\n\n"
"**Register arithmetic:** 178 → 181 obligations (+3: R-BUDGET-10/11/13); findings 108 / rows\n"
"109 unchanged; U- items unchanged at 39 (U-45 resolved ≠ deleted); mutations 38 → 39 (M039);\n"
 "verification tags 21 → 23 (`BUDGET-ESCROW-DISPOSITION-TOTALITY`, `PERSISTENT-CAPACITY-ACCOUNTING`).\n\n"
 "**Frozen text** (spec/01, each its own original — no substitution):\n\n"
 + ADD_BUDGET10 + "\n\n" + ADD_BUDGET11 + "\n\n" + ADD_BUDGET13 + "\n\n")


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
    for want, got, what in ((181, len(reqs), "requirements"), (108, findings, "findings"),
                            (39, unresolved, "unresolved"), (39, muts, "mutations"),
                            (23, tags, "tags"), (24, sections, "sections")):
        if got != want:
            print(f"  FAIL: {what}={got}, want {want}"); ok = False
    for rid in NEW_IDS:
        if rid not in reqs:
            print(f"  FAIL: {rid} not indexed"); ok = False
    for m in ("M039",):
        if m not in blob:
            print(f"  FAIL: {m} not in index"); ok = False
    for tag in ("BUDGET-ESCROW-DISPOSITION-TOTALITY", "PERSISTENT-CAPACITY-ACCOUNTING"):
        if tag not in blob:
            print(f"  FAIL: {tag} not in index"); ok = False
    resolved = sorted(f["id"] for f in idx["findings"]
                      if f["id"].startswith("C-10") and f.get("status") == "resolved-by-addendum")
    if resolved != ["C-103", "C-104", "C-105", "C-106", "C-107", "C-108", "C-109"]:
        print(f"  FAIL: resolved-by-addendum C rows = {resolved}"); ok = False
    if any(f["id"] == "C-108" and f.get("resolved_into") != "U-45" for f in idx["findings"]):
        print("  FAIL: C-108 resolved_into not U-45"); ok = False

    p = subprocess.run([sys.executable, "spec/_check.py", "--verbose"], cwd=root,
                       capture_output=True, text=True, timeout=600)
    new_flags = [ln.strip() for ln in (p.stdout + p.stderr).splitlines()
                 if re.search(r"\[D[23]\] (R-BUDGET-10|R-BUDGET-11|R-BUDGET-13)\b", ln)]
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
    if len(ids) != 181:
        print(f"  FAIL: spec/01 obligation markers = {len(ids)}, want 181"); ok = False
    for rid in NEW_IDS:
        if rid not in ids:
            print(f"  FAIL: spec/01 missing {rid}"); ok = False
    if "**Total: 181 obligations**" not in (root / "spec/03-obligation-matrix.md").read_text(encoding="utf-8"):
        print("  FAIL: spec/03 Total not 181"); ok = False
    return ok


def main() -> int:
    apply_mode = "--apply" in sys.argv
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
