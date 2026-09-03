#!/usr/bin/env python3
"""spec_addendum7.py — request-pipeline remediation applier (U-39..U-44; C-103..C-109).

Freezes the request-pipeline remediation as additive normative text (addendum VII):

  spec/01  + R-CORE-14  (canonical request protocol; turn-[21] order superseded;
                         step-10 premise t + d_t(req) <= W; s12-s14b atomic)
           + R-DUR-06   (durable issuance payload: effect_bytes + cost triple;
                         {id, actor, digest} superseded as persistence payload)
           + R-DUR-07   (live issuance failure: journal-driven commit,
                         Fault::PersistenceError, pre-s12 rollback,
                         Prepared AND NOT Issued => Discard)
           + R-RECOV-09 (recovery reconstruction authority: next_effect_id,
                         no SnapshotCommit in s12-s14b, completion order)
           + R-TEST-12  (REQUEST-ARGS-LTR / REQUEST-NON-CAP-SHORT-CIRCUIT
                         added to the R-TEST-07 obligation-tagged list)
  spec/03  5 rows; Total 173 -> 178 (148 + 30 post-audit addenda)
  spec/06  C-103..C-107, C-109 -> resolved-by-addendum (C-108 corrected-in-place,
           U-45 deliberately deferred)
  spec/08  tags REQUEST-ARGS-LTR / REQUEST-NON-CAP-SHORT-CIRCUIT;
           mutations M037/M038 registered (M001-M038)
  spec/09  U-39..U-44 resolved bullets; U-45 deferral note; process note 10
  records  normalization-records header extended to addendum VII
  mod/_ownership.py + mod/01,11,12,17  ownership and module tables
  spec/_build_index.py  sections, requirements, tags, mutations, meta, milestones,
                        crates
  req/_validate.py  comment only (count pins unchanged: 109 C, 39 U)
  README   counts and audit bullet (same-line edits; no line shifts)
  audit/_checker_mutations.py  K19/K20: M037/M038 document-mutant shapes

Owner decision (2026-09-03, recorded in audit/spec-addendum7-draft.md):
U-39..U-44 resolved; U-45 (R-BUDGET-10..14 adoption, C-108) DEFERRED to a
dedicated pass (candidate addendum VIII) and remains OPEN.

Same discipline as addenda I-VI: exact-count anchors (abort on ambiguity),
nothing deleted (superseded wording quoted at the superseding site), marker
precheck for idempotency, and full verification in a git-archive sandbox.

Exit 0 proof; 1 verification failed; 2 safety abort.
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
MATRIX_AUDIT = REPO / "audit" / "request-pipeline-proof-obligation-matrix.md"
MOD01 = REPO / "mod" / "01-core.md"
MOD11 = REPO / "mod" / "11-persistence.md"
MOD12 = REPO / "mod" / "12-recovery.md"
MOD17 = REPO / "mod" / "17-verification.md"
HARNESS = REPO / "audit" / "_checker_mutations.py"
DRAFT = REPO / "audit" / "spec-addendum7-draft.md"

NEW_IDS = ["R-CORE-14", "R-DUR-06", "R-DUR-07", "R-RECOV-09", "R-TEST-12"]
MARKERS = NEW_IDS + ["M037", "M038", "REQUEST-ARGS-LTR",
                     "REQUEST-NON-CAP-SHORT-CIRCUIT", "addendum VII"]

# ---------------------------------------------------------------------------
# frozen addendum texts (single-line bodies, matching the spec/01 style)
# ---------------------------------------------------------------------------

ADD_CORE14 = ("**R-CORE-14 (canonical request protocol and transaction boundary — frozen addendum).** "
 "The request sequence is exactly the 16-step master-prompt form: (1) evaluate capability; (2) evaluate "
 "target; (3) evaluate arguments left-to-right; (4) construct the canonical `Effect` and `EffectDigest`; "
 "(5) validate the CapRef; (6) authorize the exact effect; (7) capability ceiling; (8) runtime budget; "
 "(9) runtime reservation; (10) deadline; (11) host policy; (12) allocate the `EffectId`; (13) commit "
 "issue budget/reservation; (14) durable issuance; (15) actor `Pending`; (16) host invocation. The "
 "turn-[21] 16-step form — in which the host emission precedes the durable `Issued` record — is "
 "SUPERSEDED (quoted, not deleted): `HostInvoked(E) ⇒ DurableIssued(E)` holds with no ordering "
 "exception, and the S-12 presentment of that earlier order is read only as the superseded historical "
 "text (C-103). The step-10 deadline premise MUST be the post-advance form `t + δ_t(req) ≤ W`; the "
 "pre-advance `t ≤ W` reading is SUPERSEDED (C-104). Steps 12–14b form ONE atomic section: between "
 "allocation of the `EffectId` and the second fsync of the `Issued` record no `SnapshotCommit`, no "
 "scheduler yield and no observable event MAY occur. Live-failure semantics of that section are "
 "R-DUR-07; the recovery boundary (snapshot cadence, `next_effect_id` reconstruction, completion order) "
 "is R-RECOV-09. *(Frozen addendum VII — request-pipeline remediation, owner decision 2026-09-03; "
 "additive per R-SCOPE-03; extends R-EFFECT-01/03, R-BUDGET-06, R-DUR-02, R-CORE-06/12; resolves "
 "C-103/C-104, decisions U-39/U-40; no source transcription.)*")

ADD_DUR06 = ("**R-DUR-06 (durable issuance payload — frozen addendum).** The issuance records MUST "
 "carry the effect and its cost: `EffectPrepared { id, actor, digest, effect_bytes, issue, "
 "complete_max, reserve }` and `EffectIssued { id, actor, digest, effect_bytes, issue, complete_max, "
 "reserve }` MUST be the persistence payloads — the canonical bytes of the effect, its `EffectDigest`, "
 "and the `EffectCost { issue, complete_max, reserve }`. The `{id, actor, digest}` shapes are "
 "SUPERSEDED as persistence payloads (quoted, not deleted); `{id, actor, digest}` remains valid only as "
 "the planner-visible observation projection (R-PLANNER-07). The escrowed `complete_max` and the "
 "reservation MUST thereby be reconstructible at every T0–T6 point: T1 discard restores from the "
 "record, T2–T4 classification and reconciliation carry the effect they must query about, and T5 "
 "resumption is byte-exact from the record. `effect_bytes` MUST verify `EffectDigest(effect_bytes) = "
 "digest` at append and at recovery — a mismatch is `EffectJournalCorruption` (C-105). The records MUST "
 "NOT contain raw capability values (R-CORE-07/R-CANON-12: the kernel-mediated codec governs). "
 "*(Frozen addendum VII — request-pipeline remediation, owner decision 2026-09-03; additive per "
 "R-SCOPE-03; extends R-DUR-02/05, R-PERSIST-03, R-EFFECT-05, R-RECOV-06; resolves C-105, decision "
 "U-41; mutation M038; no source transcription.)*")

ADD_DUR07 = ("**R-DUR-07 (live issuance failure — frozen addendum).** Persistence failures on the "
 "issuance path are data, never panics (R-CORE-12), and MUST fault with the declared "
 "`Fault::PersistenceError`, added to the R-CORE-13 closed declaration by this addendum. The commit is "
 "journal-driven: `persistence.append(EffectPrepared …)` per R-DUR-06 followed by `persistence.sync()` "
 "is the ONE durable mutation that also journals the ID allocation and the budget/reservation/escrow "
 "commit; the in-memory mutations of steps 12–13 MUST NOT occur before that append+fsync returns Ok "
 "(C-106). On any append or sync error: the transition faults, `next_effect_id`, budget, reservations "
 "and escrow are at their pre-s12 values, the event log gains no entry, and `HostExecutor::execute` is "
 "NEVER invoked — R-EFFECT-04's five assertions hold on this path. A failure of the second `sync()` "
 "(the `Issued` record's fsync) is likewise `Fault::PersistenceError`, with the machine rolled back to "
 "the `Prepared`-durable state and the journal classifying the effect `Prepared ∧ ¬Issued ⇒ Discard` at "
 "recovery (R-DUR-04, R-RECOV-02 T1). No `InternalInvariant` classification is permitted for a storage "
 "error — this is the single declared fault family for the issuance path. *(Frozen addendum VII — "
 "request-pipeline remediation, owner decision 2026-09-03; additive per R-SCOPE-03; extends R-DUR-02/04, "
 "R-EFFECT-04, R-CORE-12/13, R-PERSIST-02/03; resolves C-106, decision U-42; mutation M037; no source "
 "transcription.)*")

ADD_RECOV9 = ("**R-RECOV-09 (recovery reconstruction authority — frozen addendum).** Recovery MUST "
 "reconstruct `next_effect_id = max({id ∈ replayed EffectIssued}) + 1`; a snapshot counter less than the "
 "journal maximum is stale and MUST be advanced (recorded, never silently repaired). A snapshot counter "
 "GREATER than the journal maximum is a `RecoveryFault`. No `SnapshotCommit` MAY exist with its "
 "last-effect sequence inside an issuance section (steps 12–14b) — the recovery of such a snapshot, if "
 "ever found, is a `RecoveryFault`, and the snapshot-taker MUST serialize against the section (C-107). "
 "The completion order is frozen: `append(EffectCompleted)`, then `sync()`, then the charge/release "
 "accounting, then the continuation resume (R-EFFECT-07) — a crash after the host returns but before "
 "that fsync is T4 (`Indeterminate`), and byte-exact resumption (T5) requires the fsync to precede the "
 "resume (C-109). *(Frozen addendum VII — request-pipeline remediation, owner decision 2026-09-03; "
 "additive per R-SCOPE-03; extends R-PERSIST-04/05/06, R-RECOV-02/03/07, R-EFFECT-07; resolves "
 "C-107/C-109, decision U-43; no source transcription.)*")

ADD_TEST12 = ("**R-TEST-12 (request-frame verification tags — frozen addendum).** The R-TEST-07 "
 "obligation-tagged coverage list MUST additionally include `REQUEST-ARGS-LTR` (request arguments "
 "evaluated strictly left-to-right, exactly one per CEK step; step 3 of the frozen sequence, "
 "R-EFFECT-01) and `REQUEST-NON-CAP-SHORT-CIRCUIT` (a non-capability capability expression faults "
 "before any target/parameter evaluation and before any step 4–16 runs, with no `EffectId`, budget or "
 "log mutation and no host invocation; R-EFFECT-04). Both tags MUST be covered by the request-path "
 "Track A suite, registered in `spec/08`, and tracked in `mod/05`/`mod/08`. Coverage of these tags "
 "MUST NOT substitute for the differential oracle (R-TEST-07). *(Frozen addendum VII — request-pipeline "
 "remediation, owner decision 2026-09-03; additive per R-SCOPE-03; extends R-TEST-07; resolves "
 "decision U-44; no source transcription.)*")

# ---------------------------------------------------------------------------
# spec/03 rows (6 cells)
# ---------------------------------------------------------------------------
ROW_CORE14 = "| R-CORE-14 | Canonical request protocol and transaction boundary: master-prompt 16-step order governs, turn-[21] host-before-Issued order superseded; step-10 premise `t + δ_t(req) ≤ W`; steps 12–14b one atomic section (C-103/C-104 resolved) | addendum (request-pipeline) | SPECIFIED | ror-runtime | M037/M038, gate short-circuit matrix |"
ROW_DUR06 = "| R-DUR-06 | Durable issuance payload: `Prepared`/`Issued` carry `effect_bytes` + `EffectCost` triple; `{id, actor, digest}` superseded as persistence payload; digest re-verified at append/recovery (C-105 resolved) | addendum (request-pipeline) | SPECIFIED | ror-persistence | M038, T1/T2–T5 reconstruction harness |"
ROW_DUR07 = "| R-DUR-07 | Live issuance failure: journal-driven commit; declared `Fault::PersistenceError`; append/sync error ⇒ pre-s12 state and R-EFFECT-04 five assertions; second-sync failure ⇒ `Prepared ∧ ¬Issued ⇒ Discard` (C-106 resolved) | addendum (request-pipeline) | SPECIFIED | ror-runtime, ror-persistence | M037, live-fault harness, T0–T1 |"
ROW_RECOV9 = "| R-RECOV-09 | Recovery reconstruction authority: `next_effect_id` from max replayed `Issued`; no `SnapshotCommit` in s12–s14b (`RecoveryFault`); completion order append→sync→charge→resume (C-107/C-109 resolved) | addendum (request-pipeline) | SPECIFIED | ror-persistence, ror-reference | M10, crash matrix T4/T5, snapshot-cadence tests |"
ROW_TEST12 = "| R-TEST-12 | Request-frame verification tags: `REQUEST-ARGS-LTR` and `REQUEST-NON-CAP-SHORT-CIRCUIT` added to R-TEST-07's obligation-tagged coverage list; Track A coverage (U-44 resolved) | addendum (request-pipeline) | SPECIFIED | tests/ | Track A request suite |"

# ---------------------------------------------------------------------------
# TOTAL line constants
# ---------------------------------------------------------------------------
TOTAL_OLD = ("**Total: 173 obligations** (148 transcribed from the frozen source + 25 post-audit frozen "
 "addenda: R-ARCH-05, R-ACTOR-09, R-ACTOR-10, R-BUDGET-09, R-CANON-12, R-CANON-13, R-CAP-10, "
 "R-COMPILE-06, R-CORE-11, R-CORE-12, R-CORE-13, R-EFFECT-08, R-HOST-06, R-KERN-04, R-KERN-05, "
 "R-KERN-06, R-MARSHAL-05, R-MARSHAL-06, R-PERSIST-07, R-PERSIST-08, R-PLANNER-06, R-PLANNER-07, "
 "R-RECOV-08, R-TRUST-04, R-TRUST-05).")
TOTAL_NEW = ("**Total: 178 obligations** (148 transcribed from the frozen source + 30 post-audit frozen "
 "addenda: R-ARCH-05, R-ACTOR-09, R-ACTOR-10, R-BUDGET-09, R-CANON-12, R-CANON-13, R-CAP-10, "
 "R-COMPILE-06, R-CORE-11, R-CORE-12, R-CORE-13, R-CORE-14, R-DUR-06, R-DUR-07, R-EFFECT-08, "
 "R-HOST-06, R-KERN-04, R-KERN-05, R-KERN-06, R-MARSHAL-05, R-MARSHAL-06, R-PERSIST-07, R-PERSIST-08, "
 "R-PLANNER-06, R-PLANNER-07, R-RECOV-08, R-RECOV-09, R-TEST-12, R-TRUST-04, R-TRUST-05).")

# ---------------------------------------------------------------------------
# spec/06 addendum-block tail paragraph and status cell replacements
# ---------------------------------------------------------------------------
C06_OLD = ("Each is **open** against the new decisions U-39…U-43, U-45 except C-108, which is corrected "
 "in place with its adoption question filed as U-45. That pass audited the path from `Expr::Request` "
 "to host-visible effect and issued no frozen text (R-SCOPE-03), so no row here is graded "
 "`resolved-by-addendum`; the audit's recommendations exist as a draft "
 "(`audit/request-pipeline-remediation-draft.md`) and are not authority.")
C06_NEW = ("Each was **open** against the new decisions U-39…U-43, U-45 except C-108, which is corrected "
 "in place with its adoption question filed as U-45, until addendum VII (owner decision 2026-09-03, "
 "`audit/spec-addendum7-draft.md`) re-graded C-103…C-107 and C-109 **`resolved-by-addendum`** "
 "(C-103/C-104 → `R-CORE-14`; C-105 → `R-DUR-06`; C-106 → `R-DUR-07`; C-107/C-109 → `R-RECOV-09`), "
 "closing U-39…U-43 and resolving U-44 via `R-TEST-12`. C-108 remains **corrected-in-place** and U-45 "
 "is explicitly DEFERRED to a dedicated pass (candidate addendum VIII): addendum VII does not pre-empt "
 "the R-BUDGET-10…14 adoption or the three-vs-five escrow-path reconciliation. The audit itself issued "
 "no frozen text (R-SCOPE-03); the remedial text is the addendum, and this file's counts — 108 findings "
 "in 109 rows — are unchanged by the re-grading.")

# ---------------------------------------------------------------------------
# U-39..U-45 resolution bullets (appended after each entry's Linked line)
# ---------------------------------------------------------------------------
U_RESOLVE = {
 "U-39": f"- **Resolved (addendum VII):** `R-CORE-14` freezes the master-prompt 16-step order as the only canonical protocol and SUPERSEDES the turn-[21] host-before-Issued order (quoted, not deleted); `spec/06` C-103 re-graded `resolved-by-addendum`.",
 "U-40": f"- **Resolved (addendum VII):** `R-CORE-14` freezes the step-10 premise as `t + δ_t(req) ≤ W`; the weak `t ≤ W` reading is SUPERSEDED; `spec/06` C-104 re-graded `resolved-by-addendum`. The per-transition δ_t table remains open (U-07) — the predicate is now decided, its operands are not.",
 "U-41": f"- **Resolved (addendum VII):** `R-DUR-06` freezes the durable issuance payload (`effect_bytes` + `EffectCost` triple); `spec/06` C-105 re-graded `resolved-by-addendum`. Machine-state encodings (U-02) still bind byte-level evidence of `effect_bytes`.",
 "U-42": f"- **Resolved (addendum VII):** `R-DUR-07` freezes journal-driven commit, the declared `Fault::PersistenceError` family, pre-s12 rollback, and the `Prepared ∧ ¬Issued ⇒ Discard` live classification; `spec/06` C-106 re-graded `resolved-by-addendum`; mutation M037 registered. It joins U-08/U-14's declared-surface work via the R-CORE-13 enumeration it extends.",
 "U-43": f"- **Resolved (addendum VII):** `R-RECOV-09` freezes `next_effect_id` reconstruction, the s12–s14b snapshot exclusion, and the completion order append→sync→charge→resume; `spec/06` C-107/C-109 re-graded `resolved-by-addendum`.",
 "U-44": f"- **Resolved (addendum VII):** `R-TEST-12` adds `REQUEST-ARGS-LTR` and `REQUEST-NON-CAP-SHORT-CIRCUIT` to the R-TEST-07 obligation-tagged coverage list; both are registered in `spec/08` and tracked in `mod/05`/`mod/08`. No C-row exists for this item by design (a verification-register gap, not a source contradiction).",
 "U-45": f"- **Decision (2026-09-03, addendum VII):** DEFERRED to a dedicated pass (candidate addendum VIII). Addendum VII does not pre-empt the R-BUDGET-10…14 adoption or the three-vs-five escrow-path reconciliation; `spec/06` C-108 stays **corrected-in-place** and this item remains OPEN.",
}

# ---------------------------------------------------------------------------
# edit table — every (path, old, new) verified against the working tree
# ---------------------------------------------------------------------------
EDITS: list[tuple[Path, str, str]] = [
    # ------------------------------ spec/01 --------------------------------
    (SPEC01, "resolves C-91, closing U-08/U-14 in the security direction; no source transcription.)*",
             "resolves C-91, closing U-08/U-14 in the security direction; no source transcription.)*\n\n" + ADD_CORE14),
    (SPEC01, "Escrow does not vanish on crash.",
             "Escrow does not vanish on crash.\n\n" + ADD_DUR06 + "\n\n" + ADD_DUR07),
    (SPEC01, "resolves C-89; mutation M028; no source transcription.)*",
             "resolves C-89; mutation M028; no source transcription.)*\n\n" + ADD_RECOV9),
    (SPEC01, "*(L38885–38911; L41196–41210.)*",
             "*(L38885–38911; L41196–41210.)*\n\n" + ADD_TEST12),
    # ------------------------------ spec/03 --------------------------------
    (MATRIX, "| R-CORE-13 | Closed declared fault surface on every trust-boundary crossing: six replay-path variants, StalePlan, unified MarshalFault, InternalInvariant declared; no debug-formatted external error text in machine values; resume-vs-fault pinned per variant (C-91 resolved) | addendum (SEC-012) | SPECIFIED | all machine crates | fault-coverage lint, differential fault matrix |",
             "| R-CORE-13 | Closed declared fault surface on every trust-boundary crossing: six replay-path variants, StalePlan, unified MarshalFault, InternalInvariant declared; no debug-formatted external error text in machine values; resume-vs-fault pinned per variant (C-91 resolved) | addendum (SEC-012) | SPECIFIED | all machine crates | fault-coverage lint, differential fault matrix |\n" + ROW_CORE14),
    (MATRIX, "| R-DUR-05 | Escrow survives crash | L35210–35215 | SPECIFIED | ror-persistence | post-recovery invariant check, M008 |",
             "| R-DUR-05 | Escrow survives crash | L35210–35215 | SPECIFIED | ror-persistence | post-recovery invariant check, M008 |\n" + ROW_DUR06 + "\n" + ROW_DUR07),
    (MATRIX, "| R-RECOV-08 | Reconciliation frozen: I2 holds on every host path incl. supervisor; never re-executes (idempotent query at most); compensations are ordinary gated requests; NotExecuted gated behind authoritative evidence; supervisor allocates lifecycle, not effects (C-89 resolved; M028) | addendum (SEC-010) | SPECIFIED | ror-agent (policy), ror-persistence (record contract) | M028, T2/T3/T4 admissibility table |",
             "| R-RECOV-08 | Reconciliation frozen: I2 holds on every host path incl. supervisor; never re-executes (idempotent query at most); compensations are ordinary gated requests; NotExecuted gated behind authoritative evidence; supervisor allocates lifecycle, not effects (C-89 resolved; M028) | addendum (SEC-010) | SPECIFIED | ror-agent (policy), ror-persistence (record contract) | M028, T2/T3/T4 admissibility table |\n" + ROW_RECOV9),
    (MATRIX, "| R-TEST-11 | Final acceptance condition (3 conjuncts) | L38885–38911, L41196–41210 | SPECIFIED | — | M11 |",
             "| R-TEST-11 | Final acceptance condition (3 conjuncts) | L38885–38911, L41196–41210 | SPECIFIED | — | M11 |\n" + ROW_TEST12),
    (MATRIX, TOTAL_OLD, TOTAL_NEW),
    # ------------------------------ spec/06 --------------------------------
    (CONTRA, "| **open** → U-39 |", "| **resolved-by-addendum** → `R-CORE-14` (U-39) |"),
    (CONTRA, "| **open** → U-40 |", "| **resolved-by-addendum** → `R-CORE-14` (U-40) |"),
    (CONTRA, "| **open** → U-41 |", "| **resolved-by-addendum** → `R-DUR-06` (U-41) |"),
    (CONTRA, "| **open** → U-42 |", "| **resolved-by-addendum** → `R-DUR-07` (U-42) |"),
    (CONTRA, "U-02 (encodings) | **open** → U-43 |",
             "U-02 (encodings) | **resolved-by-addendum** → `R-RECOV-09` (U-43) |"),
    (CONTRA, "in-memory append, charge before durability) | **open** → U-43 |",
             "in-memory append, charge before durability) | **resolved-by-addendum** → `R-RECOV-09` (U-43) |"),
    (CONTRA, C06_OLD, C06_NEW),
    # ------------------------------ spec/08 --------------------------------
    (VMAP, "## 2. Mutation registry → obligation map (M001–M036, R-TEST-04)",
           "## 2. Mutation registry → obligation map (M001–M038, R-TEST-04)"),
    (VMAP, "| M036 | rotate one `spec/01` obligation body onto adjacent content (IDs left in place) | R-SCOPE-03, R-CLAIM-02 — the SEC-023 normative-layer class; detector `spec/_check.py` |",
           "| M036 | rotate one `spec/01` obligation body onto adjacent content (IDs left in place) | R-SCOPE-03, R-CLAIM-02 — the SEC-023 normative-layer class; detector `spec/_check.py` |\n"
           "| M037 | in-memory s12–s13 mutations committed before the journal-driven append+fsync (host-visible pre-durability) | R-DUR-07 |\n"
           "| M038 | issuance records carry `{id, actor, digest}` only (loss of the escrow/effect source of truth) | R-DUR-06 |"),
    (VMAP, "(not part of the frozen source set; added by remediations SEC-001 and SEC-004):",
           "(not part of the frozen source set; added by remediations SEC-001/SEC-004 and addendum VII):"),
    (VMAP, "| `RECOVERY-REVOCATION-DURABLE` | R-PERSIST-07 (post-audit addendum) | Revocation survives crash: crash matrix T0–T6 with revocation committed before the crash point; revoked caps stay revoked; dangling/generation-mismatched CapRefs ⇒ `RecoveryFault` (mutation M023) | NONE |",
           "| `RECOVERY-REVOCATION-DURABLE` | R-PERSIST-07 (post-audit addendum) | Revocation survives crash: crash matrix T0–T6 with revocation committed before the crash point; revoked caps stay revoked; dangling/generation-mismatched CapRefs ⇒ `RecoveryFault` (mutation M023) | NONE |\n"
           "| `REQUEST-ARGS-LTR` | R-TEST-12 (addendum VII), R-EFFECT-01 | Request arguments evaluated strictly left-to-right, exactly one per CEK step (step 3 of the frozen sequence); Track A request-suite coverage | NONE |\n"
           "| `REQUEST-NON-CAP-SHORT-CIRCUIT` | R-TEST-12 (addendum VII), R-EFFECT-04 | A non-capability capability expression faults before any target/parameter evaluation and before steps 4–16; no `EffectId`, budget or log mutation; `HostExecutor` never invoked | NONE |"),
    (VMAP, "**Evidence status:** registry is `SPECIFIED` (frozen content). No mutant is registered, injected, or killed in this repository; `MutationKillRate` is **not measured** (nothing to measure). 100% is a target, not a current claim (R-CLAIM-01).",
           "**Evidence status:** registry is `SPECIFIED` (frozen content). No mutant is registered, injected, or killed in this repository; `MutationKillRate` is **not measured** (nothing to measure). 100% is a target, not a current claim (R-CLAIM-01). M037/M038 (addendum VII) are registered the same way — machine mutants, unmeasurable in BOOTSTRAP; their document-mutant shapes are exercised by `audit/_checker_mutations.py` K19/K20. M036 remains the one measurable document mutant."),
    # ------------------------------ spec/09 --------------------------------
    (UNRES, "- **Linked:** C-01, C-103, REQ-EFFECT-005/017/018, R-DUR-01/02, R-CORE-06.",
            "- **Linked:** C-01, C-103, REQ-EFFECT-005/017/018, R-DUR-01/02, R-CORE-06.\n" + U_RESOLVE["U-39"]),
    (UNRES, "- **Linked:** C-104, U-07, U-36, REQ-BUDGET-021, R-CORE-02, R-CLAIM-02.",
            "- **Linked:** C-104, U-07, U-36, REQ-BUDGET-021, R-CORE-02, R-CLAIM-02.\n" + U_RESOLVE["U-40"]),
    (UNRES, "- **Linked:** C-105, U-43, REQ-DUR-008…014, R-RECOV-013, R-BUDGET-09, R-PLANNER-07.",
            "- **Linked:** C-105, U-43, REQ-DUR-008…014, R-RECOV-013, R-BUDGET-09, R-PLANNER-07.\n" + U_RESOLVE["U-41"]),
    (UNRES, "- **Linked:** C-106, U-41, U-08, REQ-DUR-001…004, REQ-EFFECT-015/019…023, R-CORE-12/13.",
            "- **Linked:** C-106, U-41, U-08, REQ-DUR-001…004, REQ-EFFECT-015/019…023, R-CORE-12/13.\n" + U_RESOLVE["U-42"]),
    (UNRES, "- **Linked:** C-107, C-109, U-41, U-02, U-17, U-34, R-PERSIST-05, R-RECOV-03, R-EFFECT-07.",
            "- **Linked:** C-107, C-109, U-41, U-02, U-17, U-34, R-PERSIST-05, R-RECOV-03, R-EFFECT-07.\n" + U_RESOLVE["U-43"]),
    (UNRES, "- **Linked:** R-TEST-07, R-REF-05, M001…M003, GAP-06.",
            "- **Linked:** R-TEST-07, R-REF-05, M001…M003, GAP-06.\n" + U_RESOLVE["U-44"]),
    (UNRES, "- **Linked:** C-108, R-BUDGET-09, R-CORE-05, R-DUR-05, `audit/resource-accounting-audit.md`.",
            "- **Linked:** C-108, R-BUDGET-09, R-CORE-05, R-DUR-05, `audit/resource-accounting-audit.md`.\n" + U_RESOLVE["U-45"]),
    (UNRES, "so K01/K02/K04 keep exercising their named pins.",
            "so K01/K02/K04 keep exercising their named pins.\n\n10. **Addendum VII adopted 2026-09-03** (the owner decision this audit filed): U-39…U-44 are RESOLVED — `R-CORE-14` (U-39/U-40), `R-DUR-06` (U-41), `R-DUR-07` (U-42), `R-RECOV-09` (U-43), `R-TEST-12` (U-44) — each with a resolution bullet appended above; `spec/06` C-103…C-107/C-109 are re-graded `resolved-by-addendum`. **U-45 is explicitly DEFERRED** to a dedicated pass (candidate addendum VIII): addendum VII does not pre-empt the R-BUDGET-10…14 adoption or the three-vs-five escrow-path reconciliation, so C-108 stays corrected-in-place and U-45 remains open. M037/M038 are registered; the decision record is `audit/spec-addendum7-draft.md`."),
    # ------------------------------ records --------------------------------
    (RECORDS, "The same holds for the five addendum-V obligations (`R-ARCH-05`, `R-ACTOR-10`, `R-BUDGET-09`, `R-CAP-10`, `R-KERN-06`; remediations SEC-013/014/015/019/021).",
              "The same holds for the five addendum-V obligations (`R-ARCH-05`, `R-ACTOR-10`, `R-BUDGET-09`, `R-CAP-10`, `R-KERN-06`; remediations SEC-013/014/015/019/021). The same holds for the five addendum-VII obligations (`R-CORE-14`, `R-DUR-06`, `R-DUR-07`, `R-RECOV-09`, `R-TEST-12`; request-pipeline remediation) — each is its own original, no substitution."),
    # ------------------------------ README --------------------------------
    (README, "spec/03-obligation-matrix.md` — 173 stable requirement IDs (`R-…`; 148 from the frozen source + 25 post-audit frozen addenda) with status and provenance",
             "spec/03-obligation-matrix.md` — 178 stable requirement IDs (`R-…`; 148 from the frozen source + 30 post-audit frozen addenda, incl. the five addendum-VII obligations) with status and provenance"),
    (README, "C-103…C-109 by the request-pipeline proof-obligation audit, all `open` except C-108 corrected in place with its decision at U-45;",
             "C-103…C-109 by the request-pipeline proof-obligation audit, C-103…C-107/C-109 `resolved-by-addendum` under addendum VII, C-108 corrected in place with U-45 deferred;"),
    (README, "U-39…U-45 by the request-pipeline proof-obligation audit, all `open`; U-08 corrected",
             "U-39…U-45 by the request-pipeline proof-obligation audit, U-39…U-44 resolved by addendum VII and U-45 deferred; U-08 corrected"),
    # ------------------------------ ownership -----------------------------
    (OWNERSHIP, "_own(\"MOD-01\", \"CORE\",    range(1, 14))   # +CORE-11/12/13 (addenda II/III/IV)",
                "_own(\"MOD-01\", \"CORE\",    range(1, 15))   # +CORE-11/12/13 (addenda II/III/IV), +CORE-14 (addendum VII)"),
    (OWNERSHIP, "_own(\"MOD-11\", \"DUR\",     range(1, 6))",
                "_own(\"MOD-11\", \"DUR\",     range(1, 8))    # +DUR-06/07 (addendum VII)"),
    (OWNERSHIP, "_own(\"MOD-12\", \"RECOV\",   range(1, 9))    # +RECOV-08 reconciliation frozen (addendum IV)",
                "_own(\"MOD-12\", \"RECOV\",   range(1, 10))   # +RECOV-08 (addendum IV), +RECOV-09 (addendum VII)"),
    (OWNERSHIP, "_own(\"MOD-17\", \"TEST\",    [8, 9, 10, 11])",
                "_own(\"MOD-17\", \"TEST\",    [8, 9, 10, 11, 12])   # +TEST-12 request-frame tags (addendum VII)"),
    (OWNERSHIP, "    \"R-DUR-05\": [(\"MOD-04\", \"escrow partition owner\"), (\"MOD-12\", \"post-recovery invariant check\")],",
                "    \"R-DUR-05\": [(\"MOD-04\", \"escrow partition owner\"), (\"MOD-12\", \"post-recovery invariant check\")],\n"
                "    \"R-CORE-14\": [(\"MOD-08\", \"16-step sequence statement R-EFFECT-01/03\"), (\"MOD-04\", \"deadline premise R-BUDGET-06\"), (\"MOD-11\", \"s12–s14b durable section R-DUR-02\"), (\"MOD-12\", \"recovery boundary R-RECOV-09\"), (\"MOD-17\", \"completion-boundary evidence\")],\n"
                "    \"R-DUR-06\": [(\"MOD-08\", \"escrow at issuance R-EFFECT-05\"), (\"MOD-04\", \"escrow partition\"), (\"MOD-10\", \"canonical bytes/digest\"), (\"MOD-12\", \"T1 restore / T2–T5 reconstruction\")],\n"
                "    \"R-DUR-07\": [(\"MOD-08\", \"R-EFFECT-04 five assertions\"), (\"MOD-01\", \"R-CORE-12/13 fault surface\"), (\"MOD-12\", \"Prepared ∧ ¬Issued ⇒ Discard\")],\n"
                "    \"R-RECOV-09\": [(\"MOD-11\", \"snapshot atomic protocol R-PERSIST-05\"), (\"MOD-08\", \"completion order R-EFFECT-07\"), (\"MOD-06\", \"counter restoration R-ACTOR-03\"), (\"MOD-17\", \"M10 gate\")],\n"
                "    \"R-TEST-12\": [(\"MOD-05\", \"request-frame LTR\"), (\"MOD-08\", \"short-circuit gate\"), (\"MOD-15\", \"R-TEST-07 tag-list owner\")],"),
    # ------------------------------ mod files -----------------------------
    (MOD01, "| R-CORE-13 | Closed declared fault surface on every trust-boundary crossing: six replay-path variants, StalePlan, unified MarshalFault, InternalInvariant declared; no debug-formatted external error text in machine values; resume-vs-fault pinned per variant (C-91 resolved) | addendum IV (SEC-012) | fault-coverage lint, differential fault matrix |",
            "| R-CORE-13 | Closed declared fault surface on every trust-boundary crossing: six replay-path variants, StalePlan, unified MarshalFault, InternalInvariant declared; no debug-formatted external error text in machine values; resume-vs-fault pinned per variant (C-91 resolved) | addendum IV (SEC-012) | fault-coverage lint, differential fault matrix |\n"
            "| R-CORE-14 | Canonical request protocol and transaction boundary: master-prompt 16-step order governs; turn-[21] host-before-Issued order superseded; step-10 premise `t + δ_t(req) ≤ W`; steps 12–14b one atomic section (C-103/C-104 resolved) | addendum VII (request-pipeline) | M037, M038, gate short-circuit matrix |"),
    (MOD01, "Canonical text: `spec/01` S-01…S-04, S-07; addenda II–V. All 32 obligations `SPECIFIED`.",
            "Canonical text: `spec/01` S-01…S-04, S-07; addenda II–V, VII. All 33 obligations `SPECIFIED`."),
    (MOD01, "**32 obligations / 58 records.**", "**33 obligations / 58 records.**"),
    (MOD11, "| R-DUR-05 | Escrow survives crash | L35210–35215 | post-recovery invariant check, M008 |",
            "| R-DUR-05 | Escrow survives crash | L35210–35215 | post-recovery invariant check, M008 |\n"
            "| R-DUR-06 | Durable issuance payload: `Prepared`/`Issued` carry `effect_bytes` + `EffectCost` triple; `{id, actor, digest}` superseded as persistence payload; digest re-verified (C-105 resolved) | addendum VII (request-pipeline) | M038, T1/T2–T5 reconstruction |\n"
            "| R-DUR-07 | Live issuance failure: journal-driven commit; declared `Fault::PersistenceError`; append/sync error ⇒ pre-s12 state; second-sync failure ⇒ `Prepared ∧ ¬Issued ⇒ Discard` (C-106 resolved) | addendum VII (request-pipeline) | M037, live-fault harness |"),
    (MOD11, "Canonical text: `spec/01` S-18 + S-13; addenda II–IV. All 14 obligations `SPECIFIED`.",
            "Canonical text: `spec/01` S-18 + S-13; addenda II–IV, VII. All 16 obligations `SPECIFIED`."),
    (MOD11, "**14 obligations / 37 records.**", "**16 obligations / 37 records.**"),
    (MOD12, "| R-RECOV-08 | Reconciliation frozen: I2 holds on every host path incl. supervisor; never re-executes (idempotent query at most); compensations are ordinary gated requests; NotExecuted gated behind authoritative evidence; supervisor allocates lifecycle, not effects (C-89 resolved; M028) | addendum IV (SEC-010) | M028, T2/T3/T4 admissibility table |",
            "| R-RECOV-08 | Reconciliation frozen: I2 holds on every host path incl. supervisor; never re-executes (idempotent query at most); compensations are ordinary gated requests; NotExecuted gated behind authoritative evidence; supervisor allocates lifecycle, not effects (C-89 resolved; M028) | addendum IV (SEC-010) | M028, T2/T3/T4 admissibility table |\n"
            "| R-RECOV-09 | Recovery reconstruction authority: `next_effect_id` from max replayed `Issued`; no `SnapshotCommit` in s12–s14b (`RecoveryFault`); completion order append→sync→charge→resume (C-107/C-109 resolved) | addendum VII (request-pipeline) | M10, T4/T5, snapshot-cadence tests |"),
    (MOD12, "Canonical text: `spec/01` S-19; addendum IV. All 8 obligations `SPECIFIED`.",
            "Canonical text: `spec/01` S-19; addenda IV, VII. All 9 obligations `SPECIFIED`."),
    (MOD12, "**8 obligations / 22 records.**", "**9 obligations / 22 records.**"),
    (MOD17, "| R-TEST-11 | Final acceptance condition (3 conjuncts) | L38877–38919 (§29), L41196–41210 | M11 |",
            "| R-TEST-11 | Final acceptance condition (3 conjuncts) | L38877–38919 (§29), L41196–41210 | M11 |\n"
            "| R-TEST-12 | Request-frame verification tags: `REQUEST-ARGS-LTR`, `REQUEST-NON-CAP-SHORT-CIRCUIT` added to R-TEST-07's obligation-tagged list; Track A coverage (U-44 resolved) | addendum VII (request-pipeline) | Track A request suite |"),
    (MOD17, "Canonical text: `spec/01` S-21…S-24. All 18 obligations `SPECIFIED`.",
            "Canonical text: `spec/01` S-21…S-24; addendum VII. All 19 obligations `SPECIFIED`."),
    (MOD17, "**18 obligations / 86 records.**", "**19 obligations / 86 records.**"),
    # ------------------------------ req/_validate comment ------------------
    (VALIDATE, "    # row (a register gap, not a frozen-source contradiction).",
               "    # row (a register gap, not a frozen-source contradiction).  Addendum VII\n"
               "    # (2026-09-03) then re-graded C-103...C-107/C-109 resolved-by-addendum and resolved\n"
               "    # U-39...U-44; the counts pinned here are unchanged by a re-grading, and C-108 stays\n"
               "    # corrected-in-place with U-45 deferred to a dedicated pass."),
    # ------------------------------ audit matrix ---------------------------
    (MATRIX_AUDIT, "and are not authority.",
                   "and are not authority; the owner decision recorded in `audit/spec-addendum7-draft.md` was adopted 2026-09-03 as addendum VII — `R-CORE-14`, `R-DUR-06/07`, `R-RECOV-09`, `R-TEST-12`, mutations M037/M038 — re-grading C-103…C-107/C-109 `resolved-by-addendum` and closing U-39…U-44; U-45 was explicitly deferred."),
    # ------------------------------ mutation harness -----------------------
    (HARNESS,
     "def m_m036_under_allowlist(root: Path) -> bool:",
     "def m037_live_commit_before_append(root: Path) -> bool:\n"
     "    \"\"\"M037 (spec/08 registry): the in-memory s12-s13 mutations committed before\n"
     "    the journal-driven append+fsync. Rendered as a document mutant of the frozen\n"
     "    addendum-VII body: the invariant becomes live-unsafe text while the spec/03\n"
     "    row still describes the journal-driven order. Detectable by spec/_check.py\n"
     "    D3; survives the default wiring (U-38 open) and dies under --allowlist.\n"
     "    \"\"\"\n"
     "    p = root / \"spec/01-canonical-specification.md\"\n"
     "    txt = p.read_text(encoding=\"utf-8\")\n"
     "    m = re.search(r\"^\\*\\*R-DUR-07 \\(.*$\", txt, re.M)\n"
     "    if not m:\n"
     "        return False\n"
     "    mutant = (\"**R-DUR-07 (live issuance failure — frozen addendum).** \"\n"
     "              \"Persistence failures MUST commit the in-memory s12-s13 mutations \"\n"
     "              \"before the journal append and MUST invoke the host.\")\n"
     "    p.write_text(txt[:m.start()] + mutant + txt[m.end():], encoding=\"utf-8\")\n"
     "    return True\n\n\n"
     "def m038_payload_id_digest_only(root: Path) -> bool:\n"
     "    \"\"\"M038 (spec/08 registry): issuance records carry `{id, actor, digest}` only.\n"
     "    Same treatment as M037: a document mutant of the R-DUR-06 body that the\n"
     "    spec/03 row contradicts. D3-detectable; known to survive the default wiring\n"
     "    (U-38) and to die under --allowlist.\n"
     "    \"\"\"\n"
     "    p = root / \"spec/01-canonical-specification.md\"\n"
     "    txt = p.read_text(encoding=\"utf-8\")\n"
     "    m = re.search(r\"^\\*\\*R-DUR-06 \\(.*$\", txt, re.M)\n"
     "    if not m:\n"
     "        return False\n"
     "    mutant = (\"**R-DUR-06 (durable issuance payload — frozen addendum).** \"\n"
     "              \"All journal entries are free-form text with no effect, digest or cost.\")\n"
     "    p.write_text(txt[:m.start()] + mutant + txt[m.end():], encoding=\"utf-8\")\n"
     "    return True\n\n\n"
     "def m_m036_under_allowlist(root: Path) -> bool:"),
    (HARNESS,
     "             extra_checkers=[(\"spec/_check.py\", [\"--allowlist\"])]),\n]",
     "             extra_checkers=[(\"spec/_check.py\", [\"--allowlist\"])]),\n"
     "    Mutation(\"K19\", \"in-memory s12-s13 mutations before the journal append (M037)\",\n"
     "             \"The M037 shape rendered as a document mutant of the addendum-VII body. \"\n"
     "             \"Survives the default wiring (U-38 is still open) and dies under option (b), \"\n"
     "             \"the M036/K18 contrast that keeps the claim testable for the new text.\",\n"
     "             m037_live_commit_before_append,\n"
     "             regression_for=\"M037 / R-DUR-07 journal-driven commit\",\n"
     "             tags=[\"normative\", \"allowlist\"],\n"
     "             extra_checkers=[(\"spec/_check.py\", [\"--allowlist\"])]),\n"
     "    Mutation(\"K20\", \"issuance records carry {id, actor, digest} only (M038)\",\n"
     "             \"The M038 shape rendered as a document mutant of the addendum-VII body. \"\n"
     "             \"Survives the default wiring (U-38) and dies under option (b).\",\n"
     "             m038_payload_id_digest_only,\n"
     "             regression_for=\"M038 / R-DUR-06 issuance payload\",\n"
     "             tags=[\"normative\", \"allowlist\"],\n"
     "             extra_checkers=[(\"spec/_check.py\", [\"--allowlist\"])]),\n]"),
]


# ---------------------------------------------------------------------------
# spec/_build_index.py edits
# ---------------------------------------------------------------------------
IDX_EDITS: list[tuple[str, str]] = [
    # sections
    ('"R-CORE-11","R-CORE-12","R-CORE-13"],prov("27485-27654","41320-41770"),None),',
     '"R-CORE-11","R-CORE-12","R-CORE-13","R-CORE-14"],prov("27485-27654","41320-41770"),None),'),
    ('"R-DUR-01","R-DUR-02","R-DUR-03","R-DUR-04","R-DUR-05"],prov("35078-35258","37908-37981"),None),',
     '"R-DUR-01","R-DUR-02","R-DUR-03","R-DUR-04","R-DUR-05","R-DUR-06","R-DUR-07"],prov("35078-35258","37908-37981"),None),'),
    ('"R-RECOV-07","R-RECOV-08"],prov("35159-35258","26109-27484"),"U-15;U-17"),',
     '"R-RECOV-07","R-RECOV-08","R-RECOV-09"],prov("35159-35258","26109-27484"),"U-15;U-17"),'),
    ('"R-TEST-10","R-TEST-11"],prov("38587-38970","37169-37338","37339-37459"),None),',
     '"R-TEST-10","R-TEST-11","R-TEST-12"],prov("38587-38970","37169-37338","37339-37459"),None),'),
    # requirement rows
    ('("R-CORE-13","S-02","Closed declared fault surface (frozen addendum)","addendum",SPEC,[],[],["fault-coverage lint","differential fault matrix"],["C-91"]),',
     '("R-CORE-13","S-02","Closed declared fault surface (frozen addendum)","addendum",SPEC,[],[],["fault-coverage lint","differential fault matrix"],["C-91"]),\n'
     '("R-CORE-14","S-02","Canonical request protocol and transaction boundary (frozen addendum)","addendum",SPEC,[],["ror-runtime"],["M037","M038","gate short-circuit matrix"],["C-103","C-104"]),'),
    ('("R-DUR-05","S-13","Escrow survives crash","35210-35215",SPEC,[],["ror-persistence"],["post-recovery invariant check","M008"],[]),',
     '("R-DUR-05","S-13","Escrow survives crash","35210-35215",SPEC,[],["ror-persistence"],["post-recovery invariant check","M008"],[]),\n'
     '("R-DUR-06","S-13","Durable issuance payload: effect bytes + cost triple (frozen addendum)","addendum",SPEC,[],["ror-persistence"],["M038","T1/T2-T5 reconstruction harness"],["C-105"]),\n'
     '("R-DUR-07","S-13","Live issuance failure: journal-driven commit (frozen addendum)","addendum",SPEC,[],["ror-runtime","ror-persistence"],["M037","live-fault harness","T0-T1"],["C-106"]),'),
    ('("R-RECOV-08","S-19","Reconciliation protocol frozen (frozen addendum)","addendum",SPEC,[],["ror-agent","ror-persistence"],["M028","T2/T3/T4 admissibility table"],["C-89"]),',
     '("R-RECOV-08","S-19","Reconciliation protocol frozen (frozen addendum)","addendum",SPEC,[],["ror-agent","ror-persistence"],["M028","T2/T3/T4 admissibility table"],["C-89"]),\n'
     '("R-RECOV-09","S-19","Recovery reconstruction authority (frozen addendum)","addendum",SPEC,[],["ror-persistence","ror-reference"],["M10","crash matrix T4/T5","snapshot-cadence tests"],["C-107","C-109"]),'),
    ('("R-TEST-11","S-21","Final acceptance condition (3 conjuncts)","38885-38911;41196-41210",SPEC,[],[],["M11"],["C-34"]),',
     '("R-TEST-11","S-21","Final acceptance condition (3 conjuncts)","38885-38911;41196-41210",SPEC,[],[],["M11"],["C-34"]),\n'
     '("R-TEST-12","S-21","Request-frame verification tags (frozen addendum)","addendum",SPEC,[],["tests/"],["Track A request suite"],["U-44"]),'),
    # mutations
    ('("M036","rotate one spec/01 obligation body onto adjacent content (IDs left in place)",["R-SCOPE-03","R-CLAIM-02"]),',
     '("M036","rotate one spec/01 obligation body onto adjacent content (IDs left in place)",["R-SCOPE-03","R-CLAIM-02"]),\n'
     '("M037","in-memory s12-s13 mutations committed before the journal-driven append+fsync (host-visible pre-durability)",["R-DUR-07"]),\n'
     '("M038","issuance records carry id/actor/digest only (loss of the escrow/effect source of truth)",["R-DUR-06"]),'),
    # tags
    ('("RECOVERY-REVOCATION-DURABLE",["R-PERSIST-07"],"M10 (post-audit addendum)"),\n]',
     '("RECOVERY-REVOCATION-DURABLE",["R-PERSIST-07"],"M10 (post-audit addendum)"),\n'
     '("REQUEST-ARGS-LTR",["R-EFFECT-01","R-TEST-12"],"M5 (addendum VII)"),\n'
     '("REQUEST-NON-CAP-SHORT-CIRCUIT",["R-EFFECT-04","R-TEST-12"],"M5 (addendum VII)"),\n]'),
    # meta
    ('"R-AREA-NN": "normative requirement/obligation (173; 148 source-transcribed + 25 post-audit frozen addenda)"',
     '"R-AREA-NN": "normative requirement/obligation (178; 148 source-transcribed + 30 post-audit frozen addenda)"'),
    ('"TAG": "source verification-obligation tags (19; 17 frozen-source + 2 post-audit addenda)"',
     '"TAG": "source verification-obligation tags (21; 17 frozen-source + 4 post-audit addenda)"'),
    ('"M0NN": "baseline mutation registry (36; 18 baseline + 18 post-audit: M019–M036; M036 is registered and currently SURVIVING — see spec/08 §2 and U-38)"',
     '"M0NN": "baseline mutation registry (38; 18 baseline + 20 post-audit: M019–M038; M036 is registered and currently SURVIVING — see spec/08 §2 and U-38)"'),
    # milestones
    ('"R-HOST-06","R-CORE-13","R-BUDGET-09"]),',
     '"R-HOST-06","R-CORE-13","R-BUDGET-09","R-CORE-14","R-DUR-06","R-DUR-07","R-RECOV-09","R-TEST-12"]),'),
    ('"R-RECOV-02","R-TEST-08","R-DUR-04","R-PERSIST-07","R-RECOV-08"]),',
     '"R-RECOV-02","R-TEST-08","R-DUR-04","R-PERSIST-07","R-RECOV-08","R-RECOV-09"]),'),
    # crates
    ('\"R-CORE-13\",\"R-HOST-06\",\"R-ACTOR-10\",\"R-BUDGET-09\",\"R-ARCH-05\"],[\"ror-core\",\"ror-kernel\",\"ror-persistence\"]),',
     '\"R-CORE-13\",\"R-CORE-14\",\"R-HOST-06\",\"R-ACTOR-10\",\"R-BUDGET-09\",\"R-ARCH-05\",\"R-DUR-07\"],[\"ror-core\",\"ror-kernel\",\"ror-persistence\"]),'),
    ('\"R-DUR-01\",\"R-DUR-02\",\"R-DUR-03\",\"R-DUR-04\",\"R-DUR-05\",\"R-PERSIST-01\",\"R-PERSIST-02\",\"R-PERSIST-03\",\"R-PERSIST-04\",\"R-PERSIST-05\",\"R-PERSIST-06\",\"R-RECOV-01\",\"R-RECOV-02\",\"R-RECOV-03\",\"R-RECOV-04\",\"R-RECOV-05\",\"R-RECOV-06\",\"R-RECOV-07\",\"R-KERN-05\",\"R-PERSIST-07\",\"R-TRUST-05\",\"R-PERSIST-08\",\"R-HOST-06\",\"R-RECOV-08\"],[\"ror-core\"]),',
     '\"R-DUR-01\",\"R-DUR-02\",\"R-DUR-03\",\"R-DUR-04\",\"R-DUR-05\",\"R-DUR-06\",\"R-DUR-07\",\"R-PERSIST-01\",\"R-PERSIST-02\",\"R-PERSIST-03\",\"R-PERSIST-04\",\"R-PERSIST-05\",\"R-PERSIST-06\",\"R-RECOV-01\",\"R-RECOV-02\",\"R-RECOV-03\",\"R-RECOV-04\",\"R-RECOV-05\",\"R-RECOV-06\",\"R-RECOV-07\",\"R-KERN-05\",\"R-PERSIST-07\",\"R-TRUST-05\",\"R-PERSIST-08\",\"R-HOST-06\",\"R-RECOV-08\",\"R-RECOV-09\"],[\"ror-core\"]),'),
    ('"R-REF-01","R-REF-02","R-REF-03","R-REF-04"],["frozen semantics only (no production core deps)"]),',
     '"R-REF-01","R-REF-02","R-REF-03","R-REF-04","R-RECOV-09"],["frozen semantics only (no production core deps)"]),'),
]


# ---------------------------------------------------------------------------
# draft/decision record
# ---------------------------------------------------------------------------
DRAFT_TEXT = (
 "# Addendum VII — Request-pipeline remediation (ADOPTED 2026-09-03)\n\n"
 "**Status:** APPLIED by `audit/spec_addendum7.py` (same discipline as addenda I–VI).\n\n"
 "**Owner decisions** (recommendations of `audit/request-pipeline-proof-obligation-matrix.md` §5):\n\n"
 "1. **U-39** — the master-prompt 16-step order is the one canonical request protocol; the\n"
 "   turn-[21] host-before-Issued order is SUPERSEDED (quoted, not deleted) → `R-CORE-14`.\n"
 "2. **U-40** — the step-10 premise is `t + δ_t(req) ≤ W`; the weak `t ≤ W` reading is SUPERSEDED\n"
 "   → `R-CORE-14`. (The per-transition δ_t operands stay under U-07.)\n"
 "3. **U-41** — durable issuance payloads carry `effect_bytes` + `EffectCost` triple\n"
 "   → `R-DUR-06`.\n"
 "4. **U-42** — live issuance failure is a declared `Fault::PersistenceError` with journal-driven\n"
 "   commit, pre-s12 rollback, and `Prepared ∧ ¬Issued ⇒ Discard` → `R-DUR-07`.\n"
 "5. **U-43** — recovery reconstruction authority: `next_effect_id` from replayed `Issued`,\n"
 "   s12–s14b snapshot exclusion, completion order append→sync→charge→resume → `R-RECOV-09`.\n"
 "6. **U-44** — verification tags `REQUEST-ARGS-LTR` and `REQUEST-NON-CAP-SHORT-CIRCUIT` join the\n"
 "   R-TEST-07 obligation-tagged list → `R-TEST-12`.\n"
 "7. **U-45 — DEFERRED** to a dedicated pass (candidate addendum VIII): the R-BUDGET-10…14\n"
 "   adoption and the three-vs-five escrow-path reconciliation are NOT pre-empted here; C-108\n"
 "   stays **corrected-in-place** and U-45 remains **open**.\n\n"
 "**Re-graded:** `spec/06` C-103…C-107, C-109 → `resolved-by-addendum` (map: C-103/C-104 →\n"
 "R-CORE-14; C-105 → R-DUR-06; C-106 → R-DUR-07; C-107/C-109 → R-RECOV-09).\n\n"
 "**Registered:** `spec/08` mutations M037 (in-memory s12–s13 before journal append → R-DUR-07)\n"
 "and M038 (`{id, actor, digest}`-only payload → R-DUR-06); tags `REQUEST-ARGS-LTR` and\n"
 "`REQUEST-NON-CAP-SHORT-CIRCUIT`; harness mutants K19/K20 render both shapes against the frozen\n"
 "text (D3-detectable, killed under the U-38 allow-list mode, documented as surviving the default\n"
 "wiring while U-38 remains open).\n\n"
 "**Register arithmetic:** 173 → 178 obligations (148 source + 30 post-audit addenda); 108\n"
 "findings / 109 rows unchanged; 39 U- items unchanged (resolved ≠ deleted); mutations 36 → 38;\n"
 "verification tags 19 → 21.\n\n"
 "**Frozen text** (spec/01, each its own original — no substitution, `Original = Normalized`):\n\n"
 + ADD_CORE14 + "\n\n" + ADD_DUR06 + "\n\n" + ADD_DUR07 + "\n\n" + ADD_RECOV9 + "\n\n"
 + ADD_TEST12 + "\n\n")


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
    """Run the write-mode generators in the canonical order; return failures."""
    fails = []
    steps = [
        ("term/_reanchor.py", ["--write"]),     # fixes doc_site anchors, then _dict + _check
        ("spec/_build_index.py", []),           # writes spec/10-index.json
        ("mod/_build.py", ["--write"]),         # writes mod/18, mod/19
        ("dep/_graph.py", ["--write"]),         # writes dep/00..05, dep/10-graph.json
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

    # direct assertions that the adoption actually landed
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
    for want, got, what in ((178, len(reqs), "requirements"), (108, findings, "findings"),
                            (39, unresolved, "unresolved"), (38, muts, "mutations"),
                            (21, tags, "tags"), (24, sections, "sections")):
        if got != want:
            print(f"  FAIL: {what}={got}, want {want}"); ok = False
    for rid in NEW_IDS:
        if rid not in reqs:
            print(f"  FAIL: {rid} not indexed"); ok = False
    for m in ("M037", "M038"):
        if m not in blob:
            print(f"  FAIL: {m} not in index"); ok = False
    for tag in ("REQUEST-ARGS-LTR", "REQUEST-NON-CAP-SHORT-CIRCUIT"):
        if tag not in blob:
            print(f"  FAIL: {tag} not in index"); ok = False
    resolved = [f for f in idx["findings"] if f["id"].startswith("C-10")
                and f.get("status") == "resolved-by-addendum"]
    got_ids = sorted(f["id"] for f in resolved)
    if got_ids != ["C-103", "C-104", "C-105", "C-106", "C-107", "C-109"]:
        print(f"  FAIL: resolved-by-addendum C rows = {got_ids}"); ok = False

    # D3 sanity for the new addenda bodies vs their matrix rows
    p = subprocess.run([sys.executable, "spec/_check.py", "--verbose"], cwd=root,
                       capture_output=True, text=True, timeout=600)
    new_flags = [ln.strip() for ln in (p.stdout + p.stderr).splitlines()
                 if re.search(r"\[D[23]\] (R-CORE-14|R-DUR-06|R-DUR-07|R-RECOV-09|R-TEST-12)\b", ln)]
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
    if len(ids) != 178:
        print(f"  FAIL: spec/01 obligation markers = {len(ids)}, want 178"); ok = False
    for rid in NEW_IDS:
        if rid not in ids:
            print(f"  FAIL: spec/01 missing {rid}"); ok = False
    if "**Total: 178 obligations**" not in (root / "spec/03-obligation-matrix.md").read_text(encoding="utf-8"):
        print("  FAIL: spec/03 Total not 178"); ok = False
    return ok


def main() -> int:
    apply_mode = "--apply" in sys.argv
    targets = sorted({p for p, _, _ in EDITS} | {BUILDIDX, DRAFT})
    real = {}
    for p in targets:
        if p == DRAFT and not p.exists():
            real[p] = ""  # the draft does not exist yet; the applier creates it
        else:
            real[p] = p.read_text(encoding="utf-8")

    # precheck: idempotency (nothing applied yet) + anchors intact
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
