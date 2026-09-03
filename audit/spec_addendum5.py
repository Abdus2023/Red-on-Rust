#!/usr/bin/env python3
"""spec_addendum5.py — final frozen-addendum applier (SEC-013/014/015/019/021).

Freezes the last five findings (audit report §6 item 8) as additive normative
text, closing the register (23/23):

  spec/01  + R-ARCH-05  (SEC-013: isolation posture decided — ladder retired,
                         residual risk recorded, out-of-process host where
                         host code is not fully trusted)
           + R-CAP-10   (SEC-014: AdmissibleConstraint defined — fault never
                         identity, compile-time validation)
           + R-KERN-06  (SEC-015: root-grant protocol; Supervisor.host;
                         planner-I/O crate separation)
           + R-ACTOR-10 (SEC-019: mailbox resource admission, payload-
                         proportional cost, constructed-size bound)
           + R-BUDGET-09 (SEC-021: escrow disposition totality incl. live
                         faults and the logical-time bound)
  spec/03  + 5 rows, Total 168 -> 173
  spec/06  + C-93..C-97 (MAJOR, resolved-by-addendum)
  spec/08  + mutations M030, M033, M035 (registry complete: M001–M035)
  records  scope note extended to addendum V
  README   173 IDs
  spec/_build_index.py  inline dataset extended
  req/_validate.py      register expectation C-rows 92 -> 97 (recorded growth)

Default: DRY RUN — git-archive sandbox of HEAD + edits + the full verification
stack (spec_check, _build_index, req/_validate).  --apply: in place.
Exit 0 proof; 1 verification failed; 2 safety abort.
"""

from __future__ import annotations

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
RECORDS = REPO / "spec" / "normative-normalization-records.md"
README = REPO / "README.md"
CHECKER = REPO / "audit" / "spec_check.py"
BUILDIDX = REPO / "spec" / "_build_index.py"
VALIDATE = REPO / "req" / "_validate.py"

NEW_IDS = ["R-ARCH-05", "R-ACTOR-10", "R-BUDGET-09", "R-CAP-10", "R-KERN-06"]
MARKERS = NEW_IDS + ["C-93", "C-94", "C-95", "C-96", "C-97",
                     "M030", "M033", "M035"]

ADD_ARCH5 = "**R-ARCH-05 (isolation posture — frozen addendum).** The isolation ladder (U-05) is RETIRED by decision: the frozen minimum posture is in-process structural isolation (type safety, `#![forbid(unsafe_code)]`, the crate DAG, panic-free machine paths per R-CORE-12), and the residual risk — host compromise is machine compromise: same address space, memory adjacency to `GlobalState`, the kernel arena, and the revocation set — MUST be recorded in the trust model as accepted, not implied away by behavioral containment claims. For any deployment where host code is not fully trusted, the out-of-process host adapter is the REQUIRED mode: effects and receipts cross as canonical bytes only (the wire format already frozen, R-CANON-13). In-process `Box<dyn HostExecutor>` is testkit-only in production configurations (`PanicHost`/`MockKernel` doubles); production `ror-host` MUST NOT link `ror-runtime` internals beyond the adapter trait — a hard dependency/visibility gate. An untrusted agent's isolation level may never be weaker than its spawner's own. *(Frozen addendum — post-audit remediation SEC-013; additive per R-SCOPE-03; extends R-ARCH-03/R-TRUST-01/R-CORE-12; resolves C-93, retiring U-05; no source transcription.)*"

ADD_CAP10 = "**R-CAP-10 (`AdmissibleConstraint` defined — frozen addendum).** `AdmissibleConstraint` is DEFINED: decidable well-formedness per semantic domain — operation set `O` nonempty and within the parent's interpretation, scope constraint `S` interpretable, predicate `Q` closed over params, resource ceiling `R` within the parent's, lifetime `T` a satisfiable interval. The derivation law is total on admissible inputs only: `¬AdmissibleConstraint(C) ⇒ ¬∃c'. derive(A,C) = c'` — `derive(A, C)` MUST fault (`Fault::InvalidConstraint`, in the R-CORE-13 closed enumeration; the `Invalid`-variant drift C-56 is resolved there), never identity: the ⊤-default reading (inadmissible constraint silently ignored, `derive(A, C_garbage) = A`) is FORBIDDEN. Constraints are attacker-authored (authored inside untrusted `Block`s: `Attenuate`, spawn manifests per R-ACTOR-09, `Delegate` per R-MARSHAL-05): the compiler MUST validate constraint admissibility at compile time (extends R-COMPILE-02/03) before any kernel call. Property: `derive` with an inadmissible constraint never returns a CapRef, across the full generated constraint space. *(Frozen addendum — post-audit remediation SEC-014; additive per R-SCOPE-03; extends R-CAP-04/R-CAP-05/R-COMPILE-06; resolves C-94, closing AMB-12/U-09's admissibility clause; mutation M030; no source transcription.)*"

ADD_KERN6 = "**R-KERN-06 (root-grant protocol — frozen addendum).** Authority enters the machine ONLY through the frozen grant protocol: `Grant(source, authority, ceiling, t)` MUST produce a durable `CapabilityGranted` record (the R-PERSIST-07 event kind) and the authority MUST stay `≼` the deployment ceiling; root authority is minted exactly once, at machine initialization, by the deployment — no runtime minting path exists. `Supervisor.host` is REMOVED from the `Supervisor` struct, or typed as an issued-effect-only handle: R-HOST-02 (host performs only issued effects) binds EVERY host caller, not only the machine — `HostInvoked ⇒ DurableIssued` with no exception for supervisor or integration code. Planner-facing I/O MUST be structurally separated from supervisor/runtime/compiler handles (the `ror-planner-io` split: the untrusted side emits `PlanProposal` data only, no compiler/runtime edges) — no crate containing LLM/planner I/O may depend on `ror-compiler` or `ror-runtime`. Audit test: every live root authority in a recovered arena traces to a durable `CapabilityGranted` record. *(Frozen addendum — post-audit remediation SEC-015; additive per R-SCOPE-03; extends R-KERN-01/R-HOST-02/R-PLANNER-02/R-TRUST-05; resolves C-95; no source transcription.)*"

ADD_ACTOR10 = "**R-ACTOR-10 (mailbox resource admission — frozen addendum).** Mailbox admission is resource-gated: `Enqueue(v, target)` requires available recipient mailbox capacity — capacity is part of the recipient's `M` reservation — and on denial the SENDER faults with `ReservedCapacityExceeded` (sender pays; never silent growth). The send cost MUST be payload-proportional: `cost_C(send) ≥ f(canonical_len(v))` for a frozen monotone `f` bounded away from zero per byte (deterministic over canonical bytes, replay-stable). Constructed value size is bounded against the constructing actor's `M` reservation (allocation is the resource the reservation exists for). Invariant: for any reachable state, the total mailbox footprint is bounded by total reserved `M` at every step — the resource-bounded thesis holds in the heap, not only in the algebra. *(Frozen addendum — post-audit remediation SEC-019; additive per R-SCOPE-03; extends R-ACTOR-06/R-BUDGET-01/R-EFFECT-04; resolves C-96, closing the U-03/U-07 resource-admission direction; mutation M033; no source transcription.)*"

ADD_BUDGET9 = "**R-BUDGET-09 (escrow disposition totality — frozen addendum).** Escrow disposition is TOTAL: every unit entering the escrowed partition eventually leaves via exactly one frozen path — `Completed` (actual ≤ `complete_max` charged, remainder released), host-failure consumption (the C-23 rule), or durable `Reconciled` (R-RECOV-08). Held-forever-in-a-live-machine is NOT a disposition. Live faults unify with crash reconciliation: an actor fatal fault with an open effect enters the same reconciliation protocol as post-crash `Indeterminate`, and the supervisor fatal-fault policy MUST reference it. A logical-time bound moves stalled effects to reconciliation: a `Pending` effect whose deadline `W` expires (or a frozen per-effect logical timeout elapses) transitions to `Indeterminate` + reconciliation — machine state only, no wall clock (R-CAP-09), determinism preserved. Invariant: no reachable quiescent machine state contains escrow that no frozen rule can move; `C_available` shrinks only via `consumed` or durable `Reconciled`, never by strand. *(Frozen addendum — post-audit remediation SEC-021; additive per R-SCOPE-03; extends R-DUR-05/R-EFFECT-05/R-RECOV-08; resolves C-97; mutation M035; no source transcription.)*"

ROW_ARCH5 = "| R-ARCH-05 | Isolation posture decided: ladder retired — in-process structural isolation is the frozen minimum with residual risk (host compromise = machine compromise) recorded; out-of-process host adapter (canonical-bytes effects/receipts) required where host not fully trusted; in-process executor testkit-only (C-93 resolved) | addendum (SEC-013) | SPECIFIED | ror-host | dependency/visibility hard gate; dual-host-mode differential |"
ROW_CAP10 = "| R-CAP-10 | AdmissibleConstraint defined: decidable well-formedness per semantic domain (O/S/Q/R/T); inadmissible constraint faults (InvalidConstraint), never identity/top-default; compile-time validation of attacker-authored constraints (C-94 resolved; M030) | addendum (SEC-014) | SPECIFIED | ror-kernel, ror-compiler | M030, compiler negative suite |"
ROW_KERN6 = "| R-KERN-06 | Root-grant protocol frozen: Grant(source, authority, ceiling, t) with durable CapabilityGranted record, authority ≼ deployment ceiling, root minted once at initialization; Supervisor.host removed or issued-effect-only (R-HOST-02 binds all callers); planner I/O crate-separated (C-95 resolved) | addendum (SEC-015) | SPECIFIED | ror-kernel, ror-agent | PanicHost-wraps-all-handles conformance; grant audit test |"
ROW_ACTOR10 = "| R-ACTOR-10 | Mailbox resource admission: enqueue requires recipient capacity (M reservation; ReservedCapacityExceeded faults the sender, sender pays); payload-proportional send cost over canonical length; constructed value size bounded against constructor's M; footprint bounded by reserved M (C-96 resolved; M033) | addendum (SEC-019) | SPECIFIED | ror-runtime | M033, sender-flood stress, footprint-bounded property |"
ROW_BUDGET9 = "| R-BUDGET-09 | Escrow disposition totality: every escrowed unit leaves via exactly one frozen path (Completed / host-failure consumption / durable Reconciled); live faults unified with crash reconciliation; logical-time deadline bound to Indeterminate; no quiescent strand (C-97 resolved; M035) | addendum (SEC-021) | SPECIFIED | ror-runtime, ror-persistence | M035, ledger liveness, mixed crash+live harness |"

C_ROWS = [
 "| C-93 | C-19/U-05 record the isolation ladder (in-process / WASM / OS-process) as an open *surface* question; the security consequence — the frozen architecture gives a misbehaving host memory adjacency to the entire machine (same process, same address space; \"Partial\" trust is enforced by no structure at all), and the ladder is neither implemented nor retired — is absent from the register (audit SEC-013) | MAJOR | L1292–1313, L1297, C-19/U-05 | **resolved-by-addendum** → `R-ARCH-05` | A single compromised host operation reads the kernel arena, flips `revocation_set` entries, or corrupts a pending continuation — no gate is involved (gates run before host invocation): every \"Partial trust\" assumption degrades to full trust in every byte of host code, and all host-mediated findings lose their structural backstop. `R-ARCH-05` retires the ladder: the in-process minimum with the residual risk recorded in the trust model, the out-of-process adapter (canonical-bytes crossing) required where host code is not fully trusted, in-process executors testkit-only in production. Cross-ref: U-05, C-19, R-TRUST-01, SEC-001/009. |",
 "| C-94 | AMB-12/U-09 record `AdmissibleConstraint` as a named-but-undefined premise of every attenuation transition (L8717–8723, orphaned trait L10171), with `Constraint` authored inside untrusted `Block`s (L12177–12181) and the `Invalid`/`InvalidConstraint` fault drift (C-56); the security consequence — under the ⊤-default an inadmissible constraint silently does nothing, so spawn/delegate recipients hold *unattenuated* parent authority while the event log records a narrowed derivation (authority laundering with a clean audit trail), and the fault path is equally undefined — is absent (audit SEC-014) | MAJOR | L8717–8723, L7858, L10068, L10171, L12177–12181; AMB-12/U-09/C-56 | **resolved-by-addendum** → `R-CAP-10` | The meet-semantics law bounds amplification, not attenuation fidelity: `derive(A, C_garbage) = A` is legal, and three observable behaviors (accept-and-ignore, panic, reject) are all \"conformant\" — also a differential fault bug per the now-frozen R-CORE-13. `R-CAP-10` defines decidable well-formedness per domain, makes inadmissible ⇒ fault-never-identity, and moves validation to compile time (mutation M030). Cross-ref: R-CAP-04/05, R-COMPILE-02/03, U-21 domain freezing. |",
 "| C-95 | No frozen protocol says who may call authority construction, with what policy, under what ceiling, or how a grant is recorded (L3118–3160 names \"an enclosing supervisor, policy engine, or fresh delegation event\" — the channel itself is unspecified); `Supervisor` holds a bare `host: Box<dyn HostExecutor>` (L26807–26812); and the crate hosting untrusted planner I/O (`ror-agent`) links compiler and runtime directly — the trust boundary is drawn through the middle of a crate (audit SEC-015) | MAJOR | L3118–3160, L263, L26807–26812; spec/07 §6; MOD-13 | **resolved-by-addendum** → `R-KERN-06` | A flaw in planner-facing code runs with full in-process access: it can construct `ExecutablePlan`s (skipping staleness and `PlannerAccepted` recording), allocate actors, and call `host.execute` directly — `HostInvoked` without `DurableIssued`, violating R-DUR-01 with no gate ever seeing the request; every eight-prohibitions test passes because the machine-side boundary is intact. `R-KERN-06` freezes the auditable grant protocol (durable `CapabilityGranted`, deployment ceiling, root minted once at initialization), binds R-HOST-02 to every host caller, and mandates the `ror-planner-io` structural split. Cross-ref: R-KERN-01, R-HOST-02, R-DUR-01, R-TRUST-05, SEC-022. |",
 "| C-96 | The frozen send transition debits only the sender's consumables and never checks or reserves the recipient's memory at enqueue (`push_back` unconditional; no mailbox capacity field exists in the corpus); no rule makes send cost payload-proportional while `Value` includes unbounded `Bytes`/`String`; a never-`Receive`ing child retains its `M` reservation while its mailbox grows uncharged — the machine conserves budget while its actual memory footprint is unbounded relative to every frozen dimension (audit SEC-019) | MAJOR | L8780–8786, L25702–25730, L26007–26030, L10168+, L2066, L25573–25615 | **resolved-by-addendum** → `R-ACTOR-10` | Sender-flood with zombie recipients grows durable state (mailboxes are snapshotted — the growth also inflates every snapshot/WAL cycle) without violating any frozen invariant: availability collapse with a clean audit trail, amplified into a persistence DoS. `R-ACTOR-10` freezes enqueue-time recipient capacity (sender faults, sender pays), the payload-proportional cost term over canonical length, the constructed-size bound, and the footprint-bounded-by-reserved-M invariant (mutation M033). Cross-ref: R-BUDGET-01, R-ACTOR-06, U-03/U-07, MOD-04/MOD-15. |",
 "| C-97 | Escrow disposition rules exist only for completion, host-failure receipts, crash-recovery reconciliation, and T1 discard; no rule anywhere disposes of escrow for `{Issued, ¬Completed}` in a live machine whose actor faulted, was halted by the (unfrozen) fatal-fault policy, or whose partial-trust host simply never answers — never answering is inside the host's declared behavior envelope, and the mismatch-fault variant is attacker-reachable via corrupted receipts (audit SEC-021) | MAJOR | L23546–23552, L23574–23580, L25486–25490, L35159–35176, L41823–41841, L26807–26817 | **resolved-by-addendum** → `R-BUDGET-09` | Conservation is an accounting invariant — satisfied equally by escrow held forever: `C_available` and `S` slots shrink monotonically while every frozen invariant holds verbatim, ending in `Deadlock` on an empty runnable queue with escrow full; one injected bad receipt strands one effect's escrow permanently. `R-BUDGET-09` freezes disposition totality (exactly one frozen exit per escrowed unit), unifies live faults with crash reconciliation, and adds the logical-time deadline bound (machine state only) — mutation M035 kills the silent-reclaim mirror image. Cross-ref: R-DUR-05, R-EFFECT-05, R-RECOV-08, SEC-010. |",
]

MUT_ROWS5 = ("| M030 | inadmissible constraint treated as ⊤ | R-CAP-10 |\n"
             "| M033 | enqueue without recipient capacity check | R-ACTOR-10 |\n"
             "| M035 | stranded escrow silently reclaimed to `available` without reconciliation | R-BUDGET-09 |")

RECORDS_NOTE5 = " The same holds for the five addendum-V obligations (`R-ARCH-05`, `R-ACTOR-10`, `R-BUDGET-09`, `R-CAP-10`, `R-KERN-06`; remediations SEC-013/014/015/019/021)."

IDX_ARCH5 = ' ("R-ARCH-05","S-04","Isolation posture decided; ladder retired (frozen addendum)","addendum",SPEC,[],["ror-host"],["dependency/visibility hard gate","dual-host-mode differential"],["C-93"]),'
IDX_CAP10 = ' ("R-CAP-10","S-09","AdmissibleConstraint defined; fault never identity (frozen addendum)","addendum",SPEC,[],["ror-kernel","ror-compiler"],["M030","compiler negative suite"],["C-94"]),'
IDX_KERN6 = ' ("R-KERN-06","S-10","Root-grant protocol; Supervisor.host; planner-I/O separation (frozen addendum)","addendum",SPEC,[],["ror-kernel","ror-agent"],["PanicHost-wraps-all-handles conformance","grant audit test"],["C-95"]),'
IDX_ACTOR10 = ' ("R-ACTOR-10","S-15","Mailbox resource admission; payload-proportional cost (frozen addendum)","addendum",SPEC,[],["ror-runtime"],["M033","sender-flood stress","footprint-bounded property"],["C-96"]),'
IDX_BUDGET9 = ' ("R-BUDGET-09","S-11","Escrow disposition totality incl. live faults (frozen addendum)","addendum",SPEC,[],["ror-runtime","ror-persistence"],["M035","ledger liveness","mixed crash+live harness"],["C-97"]),'
IDX_MUTS5 = (' ("M030","inadmissible constraint treated as top",["R-CAP-10"]),\n'
             ' ("M033","enqueue without recipient capacity check",["R-ACTOR-10"]),\n'
             ' ("M035","stranded escrow silently reclaimed without reconciliation",["R-BUDGET-09"]),')

EDITS: list[tuple[Path, str, str]] = [
    # spec/01
    (SPEC01, "*(L9059–9085.)*", "*(L9059–9085.)*\n\n" + ADD_ARCH5),
    (SPEC01, "*(L6434–6436; L38858–38890.)*", "*(L6434–6436; L38858–38890.)*\n\n" + ADD_CAP10),
    (SPEC01, "extends R-KERN-02/R-KERN-04; no source transcription.)*",
     "extends R-KERN-02/R-KERN-04; no source transcription.)*\n\n" + ADD_KERN6),
    (SPEC01, "no partial debit occurs.", "no partial debit occurs.\n\n" + ADD_BUDGET9),
    (SPEC01, "resolves C-82; mutation M025; no source transcription.)*",
     "resolves C-82; mutation M025; no source transcription.)*\n\n" + ADD_ACTOR10),
    # spec/03 — rows + total
    (MATRIX,
     "| R-ARCH-04 | Dependency direction (algebra→kernel→plan→actor→global→scheduler→host) | L9059–9085 | SPECIFIED | all | Cargo dependency review |",
     "| R-ARCH-04 | Dependency direction (algebra→kernel→plan→actor→global→scheduler→host) | L9059–9085 | SPECIFIED | all | Cargo dependency review |\n" + ROW_ARCH5),
    (MATRIX,
     "| R-CAP-09 | Explicit logical time; no wall-clock | L6434–6436, L38858–38890 | SPECIFIED | ror-core, ror-runtime | determinism tests |",
     "| R-CAP-09 | Explicit logical time; no wall-clock | L6434–6436, L38858–38890 | SPECIFIED | ror-core, ror-runtime | determinism tests |\n" + ROW_CAP10),
    (MATRIX,
     "| R-KERN-05 | CapabilityContext real frozen possession type; unit-type sketch superseded; snapshots carry capability context; recovery reconstructs possession before gate authorization | addendum (SEC-002) | SPECIFIED | ror-kernel, ror-persistence | snapshot/recovery round-trip of possession sets |",
     "| R-KERN-05 | CapabilityContext real frozen possession type; unit-type sketch superseded; snapshots carry capability context; recovery reconstructs possession before gate authorization | addendum (SEC-002) | SPECIFIED | ror-kernel, ror-persistence | snapshot/recovery round-trip of possession sets |\n" + ROW_KERN6),
    (MATRIX,
     "| R-BUDGET-08 | ¬BudgetOK ⇒ fault(BudgetExhausted), no partial debit | L7345–7352, L7410–7419 | SPECIFIED | ror-runtime | Track C budget-gate test |",
     "| R-BUDGET-08 | ¬BudgetOK ⇒ fault(BudgetExhausted), no partial debit | L7345–7352, L7410–7419 | SPECIFIED | ror-runtime | Track C budget-gate test |\n" + ROW_BUDGET9),
    (MATRIX,
     "| R-ACTOR-09 | Spawn transfers no capabilities by default (delegation is the only default path); explicit manifest + constraint compiler-checked, strictly attenuated; Authority(child) ≺ parent; trust_level phantom retracted; BudgetAllocationSpec bounds (C-82 resolved; M025) | addendum (SEC-006) | SPECIFIED | ror-runtime, ror-kernel | M025, spawn fan-out amplification tests |",
     "| R-ACTOR-09 | Spawn transfers no capabilities by default (delegation is the only default path); explicit manifest + constraint compiler-checked, strictly attenuated; Authority(child) ≺ parent; trust_level phantom retracted; BudgetAllocationSpec bounds (C-82 resolved; M025) | addendum (SEC-006) | SPECIFIED | ror-runtime, ror-kernel | M025, spawn fan-out amplification tests |\n" + ROW_ACTOR10),
    (MATRIX,
     "**Total: 168 obligations** (148 transcribed from the frozen source + 20 post-audit frozen addenda: R-ACTOR-09, R-CANON-12, R-CANON-13, R-COMPILE-06, R-CORE-11, R-CORE-12, R-CORE-13, R-EFFECT-08, R-HOST-06, R-KERN-04, R-KERN-05, R-MARSHAL-05, R-MARSHAL-06, R-PERSIST-07, R-PERSIST-08, R-PLANNER-06, R-PLANNER-07, R-RECOV-08, R-TRUST-04, R-TRUST-05).",
     "**Total: 173 obligations** (148 transcribed from the frozen source + 25 post-audit frozen addenda: R-ARCH-05, R-ACTOR-09, R-ACTOR-10, R-BUDGET-09, R-CANON-12, R-CANON-13, R-CAP-10, R-COMPILE-06, R-CORE-11, R-CORE-12, R-CORE-13, R-EFFECT-08, R-HOST-06, R-KERN-04, R-KERN-05, R-KERN-06, R-MARSHAL-05, R-MARSHAL-06, R-PERSIST-07, R-PERSIST-08, R-PLANNER-06, R-PLANNER-07, R-RECOV-08, R-TRUST-04, R-TRUST-05)."),
    # spec/08 — mutations + title
    (VMAP,
     "| M034 | release failure silently ignored (`unwrap` → `let _`) | R-CORE-12 |",
     "| M034 | release failure silently ignored (`unwrap` → `let _`) | R-CORE-12 |\n" + MUT_ROWS5),
    (VMAP,
     "## 2. Mutation registry → obligation map (M001–M029, M031, M032, M034, R-TEST-04)",
     "## 2. Mutation registry → obligation map (M001–M035, R-TEST-04)"),
    # records — scope note extension
    (RECORDS,
     "(`R-CANON-13`, `R-CORE-13`, `R-HOST-06`, `R-PERSIST-08`, `R-PLANNER-06`, `R-PLANNER-07`, `R-RECOV-08`; remediations SEC-007/008/009/010/011/012/017).",
     "(`R-CANON-13`, `R-CORE-13`, `R-HOST-06`, `R-PERSIST-08`, `R-PLANNER-06`, `R-PLANNER-07`, `R-RECOV-08`; remediations SEC-007/008/009/010/011/012/017)." + RECORDS_NOTE5),
    # README — count
    (README,
     "- `spec/03-obligation-matrix.md` — 168 stable requirement IDs (`R-…`; 148 from the frozen source + 20 post-audit frozen addenda) with status and provenance",
     "- `spec/03-obligation-matrix.md` — 173 stable requirement IDs (`R-…`; 148 from the frozen source + 25 post-audit frozen addenda) with status and provenance"),
    # req/_validate.py — recorded register growth
    (VALIDATE,
     "    # C-77 (SEC-001/SEC-002 remediation, addendum I), C-78…C-81\n    # (SEC-003/004/005/016/018, addendum II), C-82…C-85 (SEC-006/020/022,\n    # addendum III), and C-86…C-92 (SEC-007/008/009/010/011/012/017,\n    # addendum IV) — 76 -> 81 -> 85 -> 92, recorded for the same reason\n    # (raw rows incl. the C-39 pointer; the index excludes it).\n    if len(c_ids) != 92:\n        err(f\"expected 92 C- rows in spec/06, found {len(c_ids)}\")",
     "    # C-77 (addendum I), C-78…C-81 (addendum II), C-82…C-85 (addendum III),\n    # C-86…C-92 (addendum IV), and C-93…C-97 (SEC-013/014/015/019/021,\n    # addendum V) — 76 -> 81 -> 85 -> 92 -> 97, recorded for the same reason\n    # (raw rows incl. the C-39 pointer; the index excludes it).\n    if len(c_ids) != 97:\n        err(f\"expected 97 C- rows in spec/06, found {len(c_ids)}\")"),
    # spec/_build_index.py — sections
    (BUILDIDX, '"R-ARCH-03","R-ARCH-04"],prov("37750-37790"', '"R-ARCH-03","R-ARCH-04","R-ARCH-05"],prov("37750-37790"'),
    (BUILDIDX, '"R-CAP-08","R-CAP-09"],prov("6344-6671"', '"R-CAP-08","R-CAP-09","R-CAP-10"],prov("6344-6671"'),
    (BUILDIDX, '"R-KERN-04","R-KERN-05"],prov("6672-6729"', '"R-KERN-04","R-KERN-05","R-KERN-06"],prov("6672-6729"'),
    (BUILDIDX, '"R-BUDGET-07","R-BUDGET-08"],prov("8653-9050"', '"R-BUDGET-07","R-BUDGET-08","R-BUDGET-09"],prov("8653-9050"'),
    (BUILDIDX, '"R-ACTOR-08","R-ACTOR-09"],prov("25457-26108"', '"R-ACTOR-08","R-ACTOR-09","R-ACTOR-10"],prov("25457-26108"'),
    # spec/_build_index.py — requirement rows
    (BUILDIDX,
     ' ("R-ARCH-04","S-04","Dependency direction (algebra to kernel to plan to actor to global to scheduler to host)","9059-9085",SPEC,[],["all"],["Cargo dependency review"],[]),',
     ' ("R-ARCH-04","S-04","Dependency direction (algebra to kernel to plan to actor to global to scheduler to host)","9059-9085",SPEC,[],["all"],["Cargo dependency review"],[]),\n' + IDX_ARCH5),
    (BUILDIDX,
     ' ("R-CAP-09","S-09","Explicit logical time; no wall-clock","6434-6436;38858-38890",SPEC,[],["ror-core","ror-runtime"],["determinism tests"],["U-07"]),',
     ' ("R-CAP-09","S-09","Explicit logical time; no wall-clock","6434-6436;38858-38890",SPEC,[],["ror-core","ror-runtime"],["determinism tests"],["U-07"]),\n' + IDX_CAP10),
    (BUILDIDX,
     ' ("R-KERN-05","S-10","CapabilityContext real possession type; snapshots carry it (frozen addendum)","addendum",SPEC,[],["ror-kernel","ror-persistence"],["snapshot/recovery round-trip of possession sets"],["C-77"]),',
     ' ("R-KERN-05","S-10","CapabilityContext real possession type; snapshots carry it (frozen addendum)","addendum",SPEC,[],["ror-kernel","ror-persistence"],["snapshot/recovery round-trip of possession sets"],["C-77"]),\n' + IDX_KERN6),
    (BUILDIDX,
     ' ("R-BUDGET-08","S-11","NOT BudgetOK implies fault(BudgetExhausted); no partial debit","7345-7352;7410-7419",SPEC,[],["ror-runtime"],["Track C budget-gate test"],[]),',
     ' ("R-BUDGET-08","S-11","NOT BudgetOK implies fault(BudgetExhausted); no partial debit","7345-7352;7410-7419",SPEC,[],["ror-runtime"],["Track C budget-gate test"],[]),\n' + IDX_BUDGET9),
    (BUILDIDX,
     ' ("R-ACTOR-09","S-15","Spawn authority rule: no default transfer, strict attenuation (frozen addendum)","addendum",SPEC,[],["ror-runtime","ror-kernel"],["M025","spawn fan-out amplification tests"],["C-82"]),',
     ' ("R-ACTOR-09","S-15","Spawn authority rule: no default transfer, strict attenuation (frozen addendum)","addendum",SPEC,[],["ror-runtime","ror-kernel"],["M025","spawn fan-out amplification tests"],["C-82"]),\n' + IDX_ACTOR10),
    # spec/_build_index.py — mutations
    (BUILDIDX,
     ' ("M034","release failure silently ignored (unwrap to let _)",["R-CORE-12"]),',
     ' ("M034","release failure silently ignored (unwrap to let _)",["R-CORE-12"]),\n' + IDX_MUTS5),
    # spec/_build_index.py — milestone maps
    (BUILDIDX, '"R-KERN-04","R-KERN-05","R-MARSHAL-05"]),', '"R-KERN-04","R-KERN-05","R-KERN-06","R-CAP-10","R-MARSHAL-05"]),'),
    (BUILDIDX, '"R-HOST-06","R-CORE-13"]),', '"R-HOST-06","R-CORE-13","R-BUDGET-09"]),'),
    (BUILDIDX, '"R-MARSHAL-04","R-MARSHAL-06","R-ACTOR-09"]),', '"R-MARSHAL-04","R-MARSHAL-06","R-ACTOR-09","R-ACTOR-10","R-ARCH-05"]),'),
    # spec/_build_index.py — crate maps
    (BUILDIDX, '"R-KERN-05","R-PERSIST-07","R-CORE-11","R-TRUST-03"]', '"R-KERN-05","R-KERN-06","R-CAP-10","R-PERSIST-07","R-CORE-11","R-TRUST-03"]'),
    (BUILDIDX, '"R-CORE-12","R-CORE-13","R-HOST-06"],["ror-core","ror-kernel"]),', '"R-CORE-12","R-CORE-13","R-HOST-06","R-ACTOR-10","R-BUDGET-09","R-ARCH-05"],["ror-core","ror-kernel"]),'),
    (BUILDIDX, '"R-PLANNER-07","R-RECOV-08"],["ror-core","ror-compiler","ror-runtime"]),', '"R-PLANNER-07","R-RECOV-08","R-KERN-06"],["ror-core","ror-compiler","ror-runtime"]),'),
    # spec/_build_index.py — id-scheme counts
    (BUILDIDX,
     '"R-AREA-NN": "normative requirement/obligation (168; 148 source-transcribed + 20 post-audit frozen addenda)"',
     '"R-AREA-NN": "normative requirement/obligation (173; 148 source-transcribed + 25 post-audit frozen addenda)"'),
    (BUILDIDX,
     '"M0NN": "baseline mutation registry (32; 18 baseline + 14 post-audit: M019–M029, M031, M032, M034)"',
     '"M0NN": "baseline mutation registry (35; 18 baseline + 17 post-audit: M019–M035)"'),
]

# C-93..C-97 rows: line-based, inserted after C-92's row
CONTRA_C92_PREFIX = "| C-92 |"


def apply_edits(files: dict[Path, str]) -> dict[Path, str]:
    for path, find, repl in EDITS:
        n = files[path].count(find)
        if n != 1:
            print(f"ABORT: anchor x{n} (need exactly 1) in {path.name}: {find[:70]!r}")
            sys.exit(2)
        files[path] = files[path].replace(find, repl, 1)
    lines = files[CONTRA].splitlines(keepends=True)
    idx = [i for i, ln in enumerate(lines) if ln.startswith(CONTRA_C92_PREFIX)]
    if len(idx) != 1:
        print(f"ABORT: C-92 anchor rows = {len(idx)} (need 1)")
        sys.exit(2)
    for row in reversed(C_ROWS):
        lines.insert(idx[0] + 1, row + "\n")
    files[CONTRA] = "".join(lines)
    return files


def check_tree(root: Path, label: str) -> bool:
    import json as _json
    ok = True
    spec01, matrix, records = (root / p for p in
        ("spec/01-canonical-specification.md", "spec/03-obligation-matrix.md",
         "spec/normative-normalization-records.md"))
    contra, vmap = root / "spec/06-contradictions-ambiguities.md", root / "spec/08-verification-mapping.md"
    extra = contra.read_text(encoding="utf-8") + vmap.read_text(encoding="utf-8")
    t01, t03, trec = (p.read_text(encoding="utf-8") for p in (spec01, matrix, records))
    n_ob = len(re.findall(r"\*\*(R-[A-Z]+-\d+)[^\n]*?\*\*", t01))
    n_mx = len(re.findall(r"^\|\s*R-[A-Z]+-\d+\s*\|", t03, re.M))
    n_rc = len(re.findall(r"^### (R-[A-Z]+-\d+)\s*$", trec, re.M))
    print(f"[{label}] obligations={n_ob} matrix_rows={n_mx} records={n_rc}")
    for want, got, what in ((173, n_ob, "obligations"), (173, n_mx, "matrix rows"), (148, n_rc, "records")):
        if got != want:
            print(f"  FAIL: {what} = {got}, expected {want}")
            ok = False
    for m in MARKERS:
        if m not in t01 and m not in t03 and m not in extra:
            print(f"  FAIL: marker {m!r} absent from addendum targets")
            ok = False
    out = subprocess.run(
        [sys.executable, str(CHECKER), "--records", str(records),
         "--spec01", str(spec01), "--matrix", str(matrix)],
        capture_output=True, text=True, check=False).stdout
    first = out.splitlines()[0] if out else ""
    print(f"[{label}] checker: {first}")
    if "173 spec/01 obligations, 173 matrix rows" not in first or "148 records" not in first:
        print("  FAIL: checker parse counts unexpected (vacuous-run guard)")
        ok = False
    bad = [ln for ln in out.splitlines() if re.search(r"\[D\d\] (" + "|".join(NEW_IDS) + r")\b", ln)]
    for ln in bad:
        print(f"  FAIL: new addendum obligation flagged: {ln.strip()}")
        ok = False
    if "FAIL:" in out:
        print("  FAIL: checker hard-failed (D1 class)")
        ok = False
    print(f"[{label}] checker warnings: {len(re.findall(r'WARN ', out))}")
    r = subprocess.run([sys.executable, str(root / "spec" / "_build_index.py")], cwd=root,
                       capture_output=True, text=True, check=False)
    counts = next((ln for ln in r.stdout.splitlines() if "requirements=" in ln), "")
    print(f"[{label}] index rebuild: {counts or r.stdout[-200:] or r.stderr[-200:]}")
    for want in ("requirements=173", "findings=96", "mutations=35", "tags=19", "sections=24"):
        if want not in counts:
            print(f"  FAIL: index counts missing {want!r}")
            ok = False
    data = _json.loads((root / "spec" / "10-index.json").read_text(encoding="utf-8"))
    blob = _json.dumps(data)
    for m in NEW_IDS + ["C-93", "C-97", "M030", "M035", "resolved-by-addendum"]:
        if m not in blob:
            print(f"  FAIL: 10-index.json missing {m!r}")
            ok = False
    v = subprocess.run([sys.executable, str(root / "req" / "_validate.py")], cwd=root,
                       capture_output=True, text=True, check=False)
    vtail = [ln for ln in v.stdout.splitlines() if "ERRORS" in ln or "ERROR " in ln]
    print(f"[{label}] req/_validate exit={v.returncode}: {vtail[:2]}")
    if v.returncode != 0:
        ok = False
    return ok


def main() -> int:
    apply_mode = "--apply" in sys.argv

    targets = [SPEC01, MATRIX, CONTRA, VMAP, RECORDS, README, BUILDIDX, VALIDATE]
    real = {p: p.read_text(encoding="utf-8") for p in targets}

    present = [m for m in MARKERS if any(m in real[p] for p in targets)]
    anchor_fail = []
    for path, find, _ in EDITS:
        if real[path].count(find) != 1:
            anchor_fail.append((path.name, find[:60]))
    if present or anchor_fail:
        if present:
            print(f"ABORT: addendum already applied (markers present: {present})")
        else:
            print("ABORT: anchors unexpectedly absent — tree changed?")
            for name, f in anchor_fail:
                print(f"  missing/duplicated anchor in {name}: {f!r}")
        return 2
    print(f"precheck: addendum ABSENT on real tree (no markers found) — "
          f"SEC-013/014/015/019/021 unfrozen (this absence is the finding); "
          f"{len(EDITS) + len(C_ROWS)} anchors intact")

    files = apply_edits({p: real[p] for p in targets})

    if not apply_mode:
        with tempfile.TemporaryDirectory() as td:
            box = Path(td) / "repo"
            box.mkdir()
            subprocess.run(f"git archive HEAD | tar -x -C '{box}'", shell=True,
                           cwd=REPO, check=True)
            for p in targets:
                (box / p.relative_to(REPO)).write_text(files[p], encoding="utf-8")
            ok = check_tree(box, "dry-run")
            print("\nDRY RUN: " + ("PROOF COMPLETE — addendum verifies clean"
                                   if ok else "VERIFICATION FAILED"))
            return 0 if ok else 1

    for p in targets:
        p.write_text(files[p], encoding="utf-8")
    print(f"applied: {len(EDITS) + len(C_ROWS)} edits across {len(targets)} files")
    ok = check_tree(REPO, "post-apply")
    print("\nAPPLY: " + ("VERIFIED" if ok else "VERIFICATION FAILED — inspect git diff"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
