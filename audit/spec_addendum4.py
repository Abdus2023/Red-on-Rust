#!/usr/bin/env python3
"""spec_addendum4.py — MEDIUM frozen-addendum applier (SEC-007/008/009/010/011/012/017).

Freezes the seven MEDIUM remediations (audit report §6 items 6-7) as additive
normative text:

  spec/01  + R-PLANNER-06 (SEC-007: staleness is exact equality)
           + R-PLANNER-07 (SEC-008: observation channel capability-opaque)
           + R-PERSIST-08 (SEC-009: storage integrity rewinding-resistance)
           + R-RECOV-08   (SEC-010: reconciliation protocol frozen)
           + R-HOST-06    (SEC-011: durable receipt results representable)
           + R-CORE-13    (SEC-012: closed declared fault surface)
           + R-CANON-13   (SEC-017: one canonical grammar, 15A BE)
  spec/03  + 7 rows, Total 161 -> 168
  spec/06  + C-86..C-92 (registered security consequences; resolved-by-addendum)
  spec/08  + mutations M026, M027, M028, M029, M031
  records  scope note extended to addendum IV
  README   161 -> 168 IDs
  spec/_build_index.py  inline dataset extended
  req/_validate.py      register expectation C-rows 85 -> 92 (recorded growth)

Default: DRY RUN — git-archive sandbox of HEAD + edits + the full verification
stack (spec_check, _build_index, req/_validate) runs there.  --apply: in
place, same checks on the real tree.  Exit 0 proof; 1 verification failed;
2 safety abort (already applied / anchor mismatch).
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

NEW_IDS = ["R-CANON-13", "R-CORE-13", "R-HOST-06", "R-PERSIST-08",
           "R-PLANNER-06", "R-PLANNER-07", "R-RECOV-08"]
MARKERS = NEW_IDS + ["C-86", "C-87", "C-88", "C-89", "C-90", "C-91", "C-92",
                     "M026", "M027", "M028", "M029", "M031"]

ADD_PLANNER6 = "**R-PLANNER-06 (staleness is exact equality — frozen addendum).** `AcceptProposal(p) ⇔ p.observation_sequence = current_planning_epoch` — EXACT EQUALITY. A proposal whose `observation_sequence` differs from the current planning epoch in EITHER direction MUST be rejected with `Fault::StalePlan` and zero state mutation; the strictly-less-only reading (reject only when `< current`, thereby accepting future-tagged proposals) is SUPERSEDED (quoted, not deleted). The epoch check is the exact planner-boundary check: a proposal is causally bound to the machine state it was generated from, in both directions. Future-epoch proposals are a mandatory rejection test (`obs_seq ∈ {current−1, current, current+1, current+10⁹}`: accept only `current`, zero state mutation on both rejections). C-38's canonical description is corrected hereby: the two phrasings define different acceptance sets, not one check stated twice. *(Frozen addendum — post-audit remediation SEC-007; additive per R-SCOPE-03; extends R-PLANNER-03/R-PLANNER-05; resolves C-86; mutation M026; no source transcription.)*"

ADD_PLANNER7 = "**R-PLANNER-07 (observation channel is capability-opaque — frozen addendum).** The untrusted observation channel MUST be capability-opaque by construction: `Observation` carries capability *summaries* — counts, operation classes, ceilings — NEVER references; `CapabilitySummary` is frozen as a non-referential projection (defining the phantom); `Capability ∉ Observables(LLM)` is the dual of `LLMOutput ∈ Data`. The `EffectIssued` log/event shape carries `{id, actor, digest}` ONLY — the `EffectRequest`-with-`cap` shape in the log is SUPERSEDED (quoted, not deleted; the v0.3 rule-5 shape governs), and the `EffectRequest.cap` shape conflict is registered. Events visible to the planner are filtered/redacted by a frozen observation projection rule. Property: for every machine state and observation emission, `contains_capability(Observation) = false` (recursive, events included); no `0x30`/`0x05` payloads appear in planner-facing canonical encodings. *(Frozen addendum — post-audit remediation SEC-008; additive per R-SCOPE-03; extends R-PLANNER-01/R-KERN-01; resolves C-87; mutation M027; no source transcription.)*"

ADD_PERSIST8 = "**R-PERSIST-08 (storage integrity rewinding-resistance — frozen addendum).** Persistence integrity MUST gain rewinding resistance: WAL checksums MUST be chained (`checksum_n = H(checksum_{n−1} ‖ frame_n)`) so rewrite or truncation of any prefix breaks every later frame; the snapshot commit record MUST cover the state digest and the last WAL sequence. If the storage medium is adversarial, the chain MUST be keyed (MAC or signature over the sequence-linked chain; key-epoch mismatch ⇒ `RecoveryFault`); if the storage medium is trusted-writable, that assumption MUST be recorded in the trust table as such — keyless chaining detects corruption and rewinding but does not authenticate, and the accepted risk is documented explicitly. Consistently forged records (recomputed checksums, contiguous sequences, balanced budget) are the mandatory negative test class. `Durable(D) ⇒ Authentic(D)` where keyed; the effect evidence chain (`Prepared → Issued → Completed → Reconciled`) must be unforgeable, not merely well-ordered. *(Frozen addendum — post-audit remediation SEC-009; additive per R-SCOPE-03; extends R-PERSIST-02/R-PERSIST-05; resolves C-88; no source transcription.)*"

ADD_RECOV8 = "**R-RECOV-08 (reconciliation protocol — frozen addendum).** Reconciliation is frozen: I2 (the 7-conjunct chain) holds for EVERY host invocation path including supervisor/reconciliation ones — `Reconcile(E) ⇒ Issued(E) ∧ outcome ∈ AdmissibleOutcomes(class(E))`, with per-effect-class admissible outcome variants (closing U-06/U-15 in the security direction). Reconciliation NEVER re-executes an effect: an idempotent host query at most; any compensating or retry action is itself an ordinary `Request` through gates 1–16. `NotExecuted` as a durable resolution is gated behind authoritative host-reconciliation evidence — no component, trusted or not, may resolve `Indeterminate → NotExecuted` on local policy (R-DUR-04); `Completed(EffectReceipt)` inherits the R-EFFECT-08 result-admission rule and R-HOST-06 result-digest verification. The Supervisor allocates lifecycle decisions, not effects: `Supervisor.host` is reachable only through the issuance boundary. Escrow moves only per the frozen admissibility table. *(Frozen addendum — post-audit remediation SEC-010; additive per R-SCOPE-03; extends R-DUR-04/R-DUR-05/R-RECOV-07; resolves C-89; mutation M028; no source transcription.)*"

ADD_HOST6 = "**R-HOST-06 (durable receipt results — frozen addendum).** Durable receipt results MUST be representable under a frozen contract: `EffectCompleted` carries `{id, digest, result_digest, result: CanonicalData}` — `result` scoped to the canonical data domain (R-CANON-12 / the R-EFFECT-08 admission rule). Replay MUST verify `ResultDigest(result) = result_digest` before the receipt may resume anything: a third identity conjunct extending R-EFFECT-06 (id, effect digest, result digest). Tampering `result` while keeping the digest-pair ⇒ `ReplayCorruption`. No ad-hoc result-bearing record kind may exist outside this contract (the unfrozen-record channel is closed); T5 recovery resumes the continuation with the recorded result byte-exactly. *(Frozen addendum — post-audit remediation SEC-011; additive per R-SCOPE-03; extends R-EFFECT-06/R-EFFECT-08/R-HOST-03/R-HOST-04; resolves C-90; mutation M029; no source transcription.)*"

ADD_CORE13 = "**R-CORE-13 (closed declared fault surface — frozen addendum).** The fault surface on every trust-boundary crossing (host→machine, storage→recovery, planner→machine) MUST be closed and declared: the full fault/error enumeration is frozen, including the six undeclared replay-path variants (`ReplayTraceExhausted`, the `ReplayCorruption` family), `StalePlan`, the unified `MarshalFault` (R-MARSHAL-05), and the `InternalInvariant` family (R-CORE-12); the two-variant `HostFault` declaration is SUPERSEDED (quoted, not deleted). Host faults map onto a closed machine-fault set; `format!(\"{:?}\")` debug text of external errors MUST NOT enter machine values — opaque error codes or digests only (extends R-EFFECT-08 item 4). Resume-vs-fault behavior is pinned per variant: which faults resume continuations, which park actors, the budget effect, and the event-log delta — security-critical semantics, not cosmetics; differential fault comparison (R-REF-05) compares these four, not just labels. *(Frozen addendum — post-audit remediation SEC-012; additive per R-SCOPE-03; extends R-SCOPE-03/R-REF-05/R-EFFECT-08; resolves C-91, closing U-08/U-14 in the security direction; no source transcription.)*"

ADD_CANON13 = "**R-CANON-13 (one canonical grammar — frozen addendum).** Exactly ONE canonical byte grammar is frozen: Phase 15A — universal envelope `version u8 / type_tag u8 / payload_length u32 BE`, length prefixes `u32 BE`, `CapRef [index u32 BE][generation u32 BE]`. The revised-grammar Little-Endian sections are SUPERSEDED in-source (quoted, not deleted); field names are the 15A names (`payload_length`); the `TAG_*` constants denote ONE namespace (the 15A tags; the revised-grammar tag set is superseded) — resolving term/ X-50/X-54. All integrity predicates (`EffectDigest`, `StateDigest`, `ResultDigest`, WAL checksum inputs) are defined over 15A bytes alone; cross-implementation digest equality is meaningful by construction (R-CANON-01: canonical encoding defines semantic identity). Golden vectors are asserted byte-exact bidirectionally for production, reference, and the persistence payload writer; LE-encoded variants of every golden vector MUST be rejected by all three. *(Frozen addendum — post-audit remediation SEC-017; additive per R-SCOPE-03; extends R-CANON-01/R-CANON-11/R-PERSIST-01; resolves C-92; mutation M031; no source transcription.)*"

ROW_PLANNER6 = "| R-PLANNER-06 | Staleness is exact equality: observation_sequence = current_planning_epoch; either-direction mismatch ⇒ StalePlan with zero state mutation; less-than-only reading superseded; future-tagged proposals mandatory rejection test (C-86 resolved; M026) | addendum (SEC-007) | SPECIFIED | ror-agent, ror-runtime | M026, epoch-boundary conformance |"
ROW_PLANNER7 = "| R-PLANNER-07 | Observation channel capability-opaque: CapabilitySummary frozen as non-referential projection (counts, classes, ceilings); EffectIssued carries {id, actor, digest} only, cap-bearing log shape superseded; Capability ∉ Observables(LLM) (C-87 resolved; M027) | addendum (SEC-008) | SPECIFIED | ror-agent | M027, observation-opacity property |"
ROW_PERSIST8 = "| R-PERSIST-08 | Storage integrity rewinding resistance: chained checksums (checksum_n = H(checksum_{n−1} ‖ frame_n)); snapshot commit covers state digest + last WAL sequence; keyed chain if storage adversarial, else trust-table records the trusted-writable assumption; consistently-forged negative tests (C-88 resolved) | addendum (SEC-009) | SPECIFIED | ror-persistence | tamper-at-every-T matrix, forged-record negatives |"
ROW_RECOV8 = "| R-RECOV-08 | Reconciliation frozen: I2 holds on every host path incl. supervisor; never re-executes (idempotent query at most); compensations are ordinary gated requests; NotExecuted gated behind authoritative evidence; supervisor allocates lifecycle, not effects (C-89 resolved; M028) | addendum (SEC-010) | SPECIFIED | ror-agent (policy), ror-persistence (record contract) | M028, T2/T3/T4 admissibility table |"
ROW_HOST6 = "| R-HOST-06 | Durable receipt results representable: EffectCompleted {id, digest, result_digest, result: CanonicalData}; replay verifies ResultDigest(result) = result_digest before resumption — third identity conjunct; no ad-hoc result records (C-90 resolved; M029) | addendum (SEC-011) | SPECIFIED | ror-persistence, ror-runtime | M029, T5 byte-exact resumption |"
ROW_CORE13 = "| R-CORE-13 | Closed declared fault surface on every trust-boundary crossing: six replay-path variants, StalePlan, unified MarshalFault, InternalInvariant declared; no debug-formatted external error text in machine values; resume-vs-fault pinned per variant (C-91 resolved) | addendum (SEC-012) | SPECIFIED | all machine crates | fault-coverage lint, differential fault matrix |"
ROW_CANON13 = "| R-CANON-13 | One canonical grammar: 15A BE envelope sole; LE revised grammar superseded in-source; single TAG_* namespace (X-50/X-54 resolved); all digests defined over 15A; bidirectional byte-exact golden vectors; LE variants rejected (C-92 resolved; M031) | addendum (SEC-017) | SPECIFIED | ror-core | M031, bidirectional golden vectors |"

C_ROWS = [
 "| C-86 | C-38/U-13 record the staleness predicate as \"two phrasings of one check\" (MINOR); the equality form (L27208–27212) and the strictly-less form (L27918/L28373/L28517) define **different acceptance sets** — under the canonical `<`-only reading a future-tagged proposal is not stale and must be accepted, breaking the planning-epoch trust boundary in the forward direction and end-to-end replay equivalence (audit SEC-007) | MAJOR | L27208–27212 vs L27918, L28373, L28517; C-38/U-13 | **resolved-by-addendum** → `R-PLANNER-06` | An untrusted planner can pre-stage plans for epochs that have not yet occurred, hoard accepted-but-future plans, and poison `PlannerAccepted` replay records; determinism evidence then fails or gets \"fixed\" by weakening the replay check — laundering the boundary break into the verification stack. `R-PLANNER-06` freezes exact equality with zero state mutation on either-direction rejection and makes the future-tagged case a mandatory rejection test (mutation M026). Cross-ref: C-38, U-13, R-PLANNER-05(2). |",
 "| C-87 | `CapabilitySummary` occurs exactly once in the corpus and is never defined (unregistered); four frozen `EffectRequest` declarations carry `pub cap: CapRef` while later forms drop it (unregistered shape conflict); `LogEntry::EffectIssued` embeds the full request — capability included — in the event log that planner-facing observations read; nothing freezes what the untrusted side may observe (audit SEC-008) | BLOCKING | L27151–27163, L9314–9317, L10322–10325, L10806–10809, L1447–1452, L10912–10915, L26459 | **resolved-by-addendum** → `R-PLANNER-07` | Combined with no possession check at exercise time (SEC-002, now R-KERN-04), observing CapRef bits was *sufficient* to exercise authority: opacity was the only thing between the planner and foreign authority, and the spec leaked it by default — the L127 rule (\"unrestricted reflection is a security leak\") institutionalized. `R-PLANNER-07` freezes the non-referential `CapabilitySummary`, the `{id, actor, digest}` log shape, the observation projection rule, and the `contains_capability(Observation) = false` property (mutation M027). Cross-ref: R-KERN-01, R-KERN-04, SEC-002. |",
 "| C-88 | Every persistence integrity mechanism is an unkeyed hash over attacker-writable data (frame checksum, `state_digest`); the nine rejection classes are consistency checks, so an attacker with storage write access can construct fully consistent forged records — snapshots that mint authority, WAL histories that never happened, `EffectCompleted` for effects the host never performed — and the no-silent-repair invariants are all satisfied by the forgery; the storage-channel threat model is stated nowhere (audit SEC-009) | MAJOR | L33802–33830, L26303–26309, L35196–35208 | **resolved-by-addendum** → `R-PERSIST-08` | Recovery — and the differential/reference architecture that consumes `D` as ground truth — ratifies the forgery: the verification architecture itself becomes a laundering device. `R-PERSIST-08` freezes chained checksums (keyless rewinding resistance), the keyed chain with key-epoch rejection where the medium is adversarial, the trust-table recording duty for the trusted-writable assumption, and the consistently-forged negative test class. Cross-ref: R-PERSIST-02/05, SEC-003/004, R-CORE-10. |",
 "| C-89 | Reconciliation is the only exit from `Indeterminate`, releases `complete_max` escrow, and writes durable `EffectReconciled` records, yet its protocol, authorization rules, and outcome admissibility are unfrozen and live in a trusted component above the machine; the frozen variant set already contains `NotExecuted` (the durable resolution the machine side is forbidden to infer) and `Completed(EffectReceipt)` embeds unconstrained result values; I2 is not stated to apply to reconciliation-driven actions (audit SEC-010) | BLOCKING | L26249–26262, L26593–26597, L27742, L26799–26842; U-06/U-15 | **resolved-by-addendum** → `R-RECOV-08` | A \"helpful\" supervisor policy may retry an irreversible effect (double-spend) or resolve `Indeterminate → NotExecuted` on its own policy and release escrow — machine-certified history that diverges from the real world, exactly the \"lying about the world\" failure MOD-11 exists to prevent, one unfrozen policy away from an R-DUR-04 violation. `R-RECOV-08` freezes per-class admissibility, never-re-execute, gated `NotExecuted`, gated compensations, and the supervisor lifecycle-not-effects contract (mutation M028). Cross-ref: R-DUR-04/05, U-06, U-15, SEC-001/011. |",
 "| C-90 | The durable taxonomy stores only `result_digest` (L33917–33923, L35131) while `ReplayHost::execute` returns full `EffectReceipt` results and `resume_from_receipt` needs the result `Value` — either replay correspondence is unimplementable from frozen records, or implementations add an unfrozen result-bearing record with no validation contract (`result_digest` is re-checked by no frozen rule at replay time), the exact channel SEC-001 restricts (audit SEC-011) | MAJOR | L33917–33923, L35131, L35220–35230, L26448–26459; R-HOST-03/04 | **resolved-by-addendum** → `R-HOST-06` | A tampered result with a correct digest-pair silently alters resumed values — machine state after recovery is attacker-influenced with zero detectable inconsistency; the gap also drags the unresolved machine-vs-canonical `Value` collision (U-09) onto the replay-critical path. `R-HOST-06` freezes `EffectCompleted {id, digest, result_digest, result: CanonicalData}` with the `ResultDigest(result) = result_digest` replay conjunct, data-domain scoping, and the closure of ad-hoc result records (mutation M029). Cross-ref: R-EFFECT-06/08, U-09, SEC-003. |",
 "| C-91 | term/ X-67 (BLOCKING, U-14): the frozen `HostFault` has two never-used variants while `ReplayHost` uses `ReplayTraceExhausted`/`ReplayCorruption` — undeclared; six of eight undeclared fault paths sit on the frozen replay path; `StalePlan` is in no `pub enum Fault`; `format!(\"{:?}\")` of host errors flows into machine values — the security consequence (error-path ambiguity launders authority-relevant divergences: resume-vs-fault on receipt mismatch is unconstrained, so differential fault comparison is ill-defined) is absent from the register (audit SEC-012) | BLOCKING | L10818–10821, L35224–35228, L26871, L23997; X-67/X-64/X-65, U-08/U-14, C-54/C-55/C-56/C-57 | **resolved-by-addendum** → `R-CORE-13` | Implementation A maps `ReplayCorruption`-class failures to a resumable fault, B faults the actor — both \"conforming\"; a tampered trace replays cleanly on A while the harness records a mere label mismatch adjudicated as a harness defect: the error-path ambiguity becomes the cover for the authority injection. `R-CORE-13` freezes the closed enumeration (incl. the six replay-path variants), prohibits debug-formatted external text in machine values, and pins resume-vs-fault per variant with the four-way differential comparison. Cross-ref: SEC-001/020, R-CORE-12, R-REF-05. |",
 "| C-92 | term/ X-50/X-54 (BLOCKING): two complete canonical grammars (revised-grammar LE vs Phase 15A BE; two field names, two tag widths, two endiannesses) coexist in frozen text without in-source supersession — C-02 marks the revised tags stale but the consequence the registers never draw is that every integrity chain (EffectDigest, StateDigest, WAL checksums, the differential oracle itself) inherits the ambiguity: a wrong-grammar implementer is internally correct and passes its own golden vectors while computing digests that match nothing (audit SEC-017) | BLOCKING | L28308, L28735 vs L29830, L29905, L29909, L30542; X-50/X-54, C-02 | **resolved-by-addendum** → `R-CANON-13` | The pressure path is comparator weakening: a mixed-grammar system fails all differential runs, and \"fixing\" the comparator (normalizing digests, comparing post-decode values) is precisely what R-REF-05 forbids — the weakened comparator then misses real receipt-substitution divergences. `R-CANON-13` freezes 15A as the sole grammar with in-source supersession of the LE text, one `TAG_*` namespace, digests defined over 15A alone, and bidirectional byte-exact golden vectors with LE-rejection (mutation M031). Cross-ref: C-02, R-CANON-01/11, R-REF-05, R-PERSIST-01. |",
]

MUT_ROWS4 = ("| M026 | accept future-tagged proposal | R-PLANNER-06 |\n"
             "| M027 | observation includes CapRef | R-PLANNER-07 |\n"
             "| M028 | reconciliation resolves Indeterminate as NotExecuted / releases escrow without admissible outcome | R-RECOV-08 |\n"
             "| M029 | replay skips result-digest verification | R-HOST-06 |\n"
             "| M031 | component uses the superseded LE grammar | R-CANON-13 |")

RECORDS_NOTE4 = " The same holds for the seven addendum-IV obligations (`R-CANON-13`, `R-CORE-13`, `R-HOST-06`, `R-PERSIST-08`, `R-PLANNER-06`, `R-PLANNER-07`, `R-RECOV-08`; remediations SEC-007/008/009/010/011/012/017)."

IDX_PLANNER6 = ' ("R-PLANNER-06","S-05","Staleness is exact equality (frozen addendum)","addendum",SPEC,[],["ror-agent","ror-runtime"],["M026","epoch-boundary conformance"],["C-86"]),'
IDX_PLANNER7 = ' ("R-PLANNER-07","S-05","Observation channel capability-opaque (frozen addendum)","addendum",SPEC,[],["ror-agent"],["M027","observation-opacity property"],["C-87"]),'
IDX_PERSIST8 = ' ("R-PERSIST-08","S-18","Storage integrity rewinding-resistance (frozen addendum)","addendum",SPEC,[],["ror-persistence"],["tamper-at-every-T matrix","forged-record negatives"],["C-88"]),'
IDX_RECOV8 = ' ("R-RECOV-08","S-19","Reconciliation protocol frozen (frozen addendum)","addendum",SPEC,[],["ror-agent","ror-persistence"],["M028","T2/T3/T4 admissibility table"],["C-89"]),'
IDX_HOST6 = ' ("R-HOST-06","S-14","Durable receipt results, ResultDigest replay conjunct (frozen addendum)","addendum",SPEC,[],["ror-persistence","ror-runtime"],["M029","T5 byte-exact resumption"],["C-90"]),'
IDX_CORE13 = ' ("R-CORE-13","S-02","Closed declared fault surface (frozen addendum)","addendum",SPEC,[],[],["fault-coverage lint","differential fault matrix"],["C-91"]),'
IDX_CANON13 = ' ("R-CANON-13","S-17","One canonical grammar, 15A BE sole (frozen addendum)","addendum",SPEC,[],["ror-core"],["M031","bidirectional golden vectors"],["C-92"]),'
IDX_MUTS4 = (' ("M026","accept future-tagged proposal",["R-PLANNER-06"]),\n'
             ' ("M027","observation includes CapRef",["R-PLANNER-07"]),\n'
             ' ("M028","reconciliation resolves Indeterminate as NotExecuted without admissible outcome",["R-RECOV-08"]),\n'
             ' ("M029","replay skips result-digest verification",["R-HOST-06"]),\n'
             ' ("M031","component uses the superseded LE grammar",["R-CANON-13"]),')

EDITS: list[tuple[Path, str, str]] = [
    # spec/01 — one cluster per section
    (SPEC01, "*(L27920–27931; L28513–28521.)*",
     "*(L27920–27931; L28513–28521.)*\n\n" + ADD_PLANNER6 + "\n\n" + ADD_PLANNER7),
    (SPEC01, "resolves C-83; mutation M034; no source transcription.)*",
     "resolves C-83; mutation M034; no source transcription.)*\n\n" + ADD_CORE13),
    (SPEC01, "Replay MUST validate the trace, not merely load the final state.",
     "Replay MUST validate the trace, not merely load the final state.\n\n" + ADD_HOST6),
    (SPEC01, "resolves C-78; no source transcription.)*",
     "resolves C-78; no source transcription.)*\n\n" + ADD_CANON13),
    (SPEC01, "tag `RECOVERY-REVOCATION-DURABLE`; no source transcription.)*",
     "tag `RECOVERY-REVOCATION-DURABLE`; no source transcription.)*\n\n" + ADD_PERSIST8),
    (SPEC01, "*(L35111–35144; L26249–26262.)*",
     "*(L35111–35144; L26249–26262.)*\n\n" + ADD_RECOV8),
    # spec/03 — rows + total
    (MATRIX,
     "| R-PLANNER-05 | LLM outer-loop conformance (3 test obligations) | L27920–27931, L28513–28521 | SPECIFIED | ror-agent, ror-testkit | 15E suite |",
     "| R-PLANNER-05 | LLM outer-loop conformance (3 test obligations) | L27920–27931, L28513–28521 | SPECIFIED | ror-agent, ror-testkit | 15E suite |\n" + ROW_PLANNER6 + "\n" + ROW_PLANNER7),
    (MATRIX,
     "| R-CORE-12 | Fault totality on machine paths: panic-free non-test code, failures map to declared Fault (InternalInvariant family); transition atomicity — complete or fault, no died-mid-transition; durable append precedes in-memory mutation; clippy unwrap/expect denial (C-83 resolved; M034) | addendum (SEC-020) | SPECIFIED | all machine crates | M034, panic-catching fuzz harness |",
     "| R-CORE-12 | Fault totality on machine paths: panic-free non-test code, failures map to declared Fault (InternalInvariant family); transition atomicity — complete or fault, no died-mid-transition; durable append precedes in-memory mutation; clippy unwrap/expect denial (C-83 resolved; M034) | addendum (SEC-020) | SPECIFIED | all machine crates | M034, panic-catching fuzz harness |\n" + ROW_CORE13),
    (MATRIX,
     "| R-HOST-05 | Replay validates trace, not just final state | L38278–38300 | SPECIFIED | ror-host | trace comparison |",
     "| R-HOST-05 | Replay validates trace, not just final state | L38278–38300 | SPECIFIED | ror-host | trace comparison |\n" + ROW_HOST6),
    (MATRIX,
     "| R-CANON-12 | Data decoder rejects capability payloads: 0x05 and standalone 0x30 yield CanonicalError::CapabilityInData; only the kernel-mediated codec path produces or consumes capability payloads; unmarshal runs contains_capability — symmetric boundary (C-14/U-02 security direction; C-78 resolved) | addendum (SEC-003) | SPECIFIED | ror-core | M022, negative golden vectors |",
     "| R-CANON-12 | Data decoder rejects capability payloads: 0x05 and standalone 0x30 yield CanonicalError::CapabilityInData; only the kernel-mediated codec path produces or consumes capability payloads; unmarshal runs contains_capability — symmetric boundary (C-14/U-02 security direction; C-78 resolved) | addendum (SEC-003) | SPECIFIED | ror-core | M022, negative golden vectors |\n" + ROW_CANON13),
    (MATRIX,
     "| R-PERSIST-07 | Durable authority lattice: snapshot carries the AuthorityNode set, revocation_set and generation counters; WAL event kinds CapabilityGranted/Derived/Revoked; recovery reconstructs the arena, replays capability events, faults on dangling or generation-mismatched CapRef; revocation monotonic across crashes (RECOVERY-REVOCATION-DURABLE) | addendum (SEC-004) | SPECIFIED | ror-persistence, ror-kernel | RECOVERY-REVOCATION-DURABLE, M023, crash matrix T0–T6 with pre-crash revocation |",
     "| R-PERSIST-07 | Durable authority lattice: snapshot carries the AuthorityNode set, revocation_set and generation counters; WAL event kinds CapabilityGranted/Derived/Revoked; recovery reconstructs the arena, replays capability events, faults on dangling or generation-mismatched CapRef; revocation monotonic across crashes (RECOVERY-REVOCATION-DURABLE) | addendum (SEC-004) | SPECIFIED | ror-persistence, ror-kernel | RECOVERY-REVOCATION-DURABLE, M023, crash matrix T0–T6 with pre-crash revocation |\n" + ROW_PERSIST8),
    (MATRIX,
     "| R-RECOV-07 | Reconciliation is the only resolution path for Indeterminate | L35111–35144, L26249–26262 | SPECIFIED | ror-persistence, ror-host | U-15, reconciliation tests |",
     "| R-RECOV-07 | Reconciliation is the only resolution path for Indeterminate | L35111–35144, L26249–26262 | SPECIFIED | ror-persistence, ror-host | U-15, reconciliation tests |\n" + ROW_RECOV8),
    (MATRIX,
     "**Total: 161 obligations** (148 transcribed from the frozen source + 13 post-audit frozen addenda: R-COMPILE-06, R-CORE-11, R-CORE-12, R-KERN-04, R-KERN-05, R-EFFECT-08, R-MARSHAL-05, R-MARSHAL-06, R-CANON-12, R-PERSIST-07, R-ACTOR-09, R-TRUST-04, R-TRUST-05).",
     "**Total: 168 obligations** (148 transcribed from the frozen source + 20 post-audit frozen addenda: R-ACTOR-09, R-CANON-12, R-CANON-13, R-COMPILE-06, R-CORE-11, R-CORE-12, R-CORE-13, R-EFFECT-08, R-HOST-06, R-KERN-04, R-KERN-05, R-MARSHAL-05, R-MARSHAL-06, R-PERSIST-07, R-PERSIST-08, R-PLANNER-06, R-PLANNER-07, R-RECOV-08, R-TRUST-04, R-TRUST-05)."),
    # spec/08 — mutations + title
    (VMAP,
     "| M034 | release failure silently ignored (`unwrap` → `let _`) | R-CORE-12 |",
     "| M034 | release failure silently ignored (`unwrap` → `let _`) | R-CORE-12 |\n" + MUT_ROWS4),
    (VMAP,
     "## 2. Mutation registry → obligation map (M001–M025, M032, M034, R-TEST-04)",
     "## 2. Mutation registry → obligation map (M001–M029, M031, M032, M034, R-TEST-04)"),
    # records — scope note extension
    (RECORDS,
     "(`R-ACTOR-09`, `R-CORE-12`, `R-TRUST-04`, `R-TRUST-05`; remediations SEC-006/020/022).",
     "(`R-ACTOR-09`, `R-CORE-12`, `R-TRUST-04`, `R-TRUST-05`; remediations SEC-006/020/022)." + RECORDS_NOTE4),
    # README — count
    (README,
     "- `spec/03-obligation-matrix.md` — 161 stable requirement IDs (`R-…`; 148 from the frozen source + 13 post-audit frozen addenda) with status and provenance",
     "- `spec/03-obligation-matrix.md` — 168 stable requirement IDs (`R-…`; 148 from the frozen source + 20 post-audit frozen addenda) with status and provenance"),
    # req/_validate.py — recorded register growth
    (VALIDATE,
     "    # C-77 (SEC-001/SEC-002 remediation, addendum I), C-78…C-81\n    # (SEC-003/004/005/016/018, addendum II), and C-82…C-85 (SEC-006/020/022,\n    # addendum III) — 76 -> 81 -> 85, recorded here for the same reason\n    # (raw rows incl. the C-39 pointer; the index excludes it).\n    if len(c_ids) != 85:\n        err(f\"expected 85 C- rows in spec/06, found {len(c_ids)}\")",
     "    # C-77 (SEC-001/SEC-002 remediation, addendum I), C-78…C-81\n    # (SEC-003/004/005/016/018, addendum II), C-82…C-85 (SEC-006/020/022,\n    # addendum III), and C-86…C-92 (SEC-007/008/009/010/011/012/017,\n    # addendum IV) — 76 -> 81 -> 85 -> 92, recorded for the same reason\n    # (raw rows incl. the C-39 pointer; the index excludes it).\n    if len(c_ids) != 92:\n        err(f\"expected 92 C- rows in spec/06, found {len(c_ids)}\")"),
    # spec/_build_index.py — sections
    (BUILDIDX,
     '"R-PLANNER-01","R-PLANNER-02","R-PLANNER-03","R-PLANNER-04","R-PLANNER-05"],prov("27150-27480"',
     '"R-PLANNER-01","R-PLANNER-02","R-PLANNER-03","R-PLANNER-04","R-PLANNER-05","R-PLANNER-06","R-PLANNER-07"],prov("27150-27480"'),
    (BUILDIDX,
     '"R-CORE-10","R-CORE-11","R-CORE-12"],prov("27485-27654"',
     '"R-CORE-10","R-CORE-11","R-CORE-12","R-CORE-13"],prov("27485-27654"'),
    (BUILDIDX,
     '"R-HOST-04","R-HOST-05"],prov("25972-25996"',
     '"R-HOST-04","R-HOST-05","R-HOST-06"],prov("25972-25996"'),
    (BUILDIDX,
     '"R-CANON-10","R-CANON-11","R-CANON-12"],prov(',
     '"R-CANON-10","R-CANON-11","R-CANON-12","R-CANON-13"],prov('),
    (BUILDIDX,
     '"R-PERSIST-05","R-PERSIST-06","R-PERSIST-07"],prov(',
     '"R-PERSIST-05","R-PERSIST-06","R-PERSIST-07","R-PERSIST-08"],prov('),
    (BUILDIDX,
     '"R-RECOV-06","R-RECOV-07"],prov("35159-35258"',
     '"R-RECOV-06","R-RECOV-07","R-RECOV-08"],prov("35159-35258"'),
    # spec/_build_index.py — requirement rows
    (BUILDIDX,
     ' ("R-PLANNER-05","S-05","LLM outer-loop conformance (3 test obligations)","27920-27931;28513-28521",SPEC,[],["ror-agent","ror-testkit"],["15E suite"],[]),',
     ' ("R-PLANNER-05","S-05","LLM outer-loop conformance (3 test obligations)","27920-27931;28513-28521",SPEC,[],["ror-agent","ror-testkit"],["15E suite"],[]),\n' + IDX_PLANNER6 + '\n' + IDX_PLANNER7),
    (BUILDIDX,
     ' ("R-CORE-12","S-02","Fault totality and transition atomicity on machine paths (frozen addendum)","addendum",SPEC,[],[],["M034","panic-catching fuzz harness"],["C-83"]),',
     ' ("R-CORE-12","S-02","Fault totality and transition atomicity on machine paths (frozen addendum)","addendum",SPEC,[],[],["M034","panic-catching fuzz harness"],["C-83"]),\n' + IDX_CORE13),
    (BUILDIDX,
     ' ("R-HOST-05","S-14","Replay validates trace, not just final state","38278-38300",SPEC,[],["ror-host"],["trace comparison"],[]),',
     ' ("R-HOST-05","S-14","Replay validates trace, not just final state","38278-38300",SPEC,[],["ror-host"],["trace comparison"],[]),\n' + IDX_HOST6),
    (BUILDIDX,
     ' ("R-CANON-12","S-17","Data decoder rejects capability payloads (frozen addendum)","addendum",SPEC,[],["ror-core"],["M022","negative golden vectors"],["C-78"]),',
     ' ("R-CANON-12","S-17","Data decoder rejects capability payloads (frozen addendum)","addendum",SPEC,[],["ror-core"],["M022","negative golden vectors"],["C-78"]),\n' + IDX_CANON13),
    (BUILDIDX,
     ' ("R-PERSIST-07","S-18","Durable authority lattice; revocation survives crash (frozen addendum)","addendum",SPEC,[],["ror-persistence","ror-kernel"],["RECOVERY-REVOCATION-DURABLE","M023"],[]),',
     ' ("R-PERSIST-07","S-18","Durable authority lattice; revocation survives crash (frozen addendum)","addendum",SPEC,[],["ror-persistence","ror-kernel"],["RECOVERY-REVOCATION-DURABLE","M023"],[]),\n' + IDX_PERSIST8),
    (BUILDIDX,
     ' ("R-RECOV-07","S-19","Reconciliation is the only resolution path for Indeterminate","35111-35144;26249-26262",SPEC,[],["ror-persistence","ror-host"],["U-15","reconciliation tests"],["U-06","U-15"]),',
     ' ("R-RECOV-07","S-19","Reconciliation is the only resolution path for Indeterminate","35111-35144;26249-26262",SPEC,[],["ror-persistence","ror-host"],["U-15","reconciliation tests"],["U-06","U-15"]),\n' + IDX_RECOV8),
    # spec/_build_index.py — mutations
    (BUILDIDX,
     ' ("M034","release failure silently ignored (unwrap to let _)",["R-CORE-12"]),',
     ' ("M034","release failure silently ignored (unwrap to let _)",["R-CORE-12"]),\n' + IDX_MUTS4),
    # spec/_build_index.py — milestone maps
    (BUILDIDX, '"R-CANON-10","R-CANON-11","R-CANON-12"]),', '"R-CANON-10","R-CANON-11","R-CANON-12","R-CANON-13"]),'),
    (BUILDIDX, '"R-HOST-05","R-EFFECT-08","R-CORE-11","R-CORE-12"]),', '"R-HOST-05","R-EFFECT-08","R-CORE-11","R-CORE-12","R-HOST-06","R-CORE-13"]),'),
    (BUILDIDX, '"R-RECOV-06","R-PERSIST-07"]),', '"R-RECOV-06","R-PERSIST-07","R-PERSIST-08"]),'),
    (BUILDIDX, '["R-RECOV-02","R-TEST-08","R-DUR-04","R-PERSIST-07"]),', '["R-RECOV-02","R-TEST-08","R-DUR-04","R-PERSIST-07","R-RECOV-08"]),'),
    # spec/_build_index.py — crate maps
    (BUILDIDX,
     '"R-PLANNER-01","R-PLANNER-02","R-PLANNER-03","R-PLANNER-04","R-PLANNER-05"],["ror-core","ror-compiler","ror-runtime"]),',
     '"R-PLANNER-01","R-PLANNER-02","R-PLANNER-03","R-PLANNER-04","R-PLANNER-05","R-PLANNER-06","R-PLANNER-07","R-RECOV-08"],["ror-core","ror-compiler","ror-runtime"]),'),
    (BUILDIDX, '"R-CANON-10","R-CANON-11","R-CANON-12"],[]),', '"R-CANON-10","R-CANON-11","R-CANON-12","R-CANON-13"],[]),'),
    (BUILDIDX,
     '"R-RECOV-07","R-KERN-05","R-PERSIST-07","R-TRUST-05"],["ror-core"]),',
     '"R-RECOV-07","R-KERN-05","R-PERSIST-07","R-TRUST-05","R-PERSIST-08","R-HOST-06","R-RECOV-08"],["ror-core"]),'),
    (BUILDIDX,
     '"R-MARSHAL-05","R-MARSHAL-06","R-CORE-11","R-ACTOR-09","R-CORE-12"],["ror-core","ror-kernel"]),',
     '"R-MARSHAL-05","R-MARSHAL-06","R-CORE-11","R-ACTOR-09","R-CORE-12","R-CORE-13","R-HOST-06"],["ror-core","ror-kernel"]),'),
    # spec/_build_index.py — id-scheme counts
    (BUILDIDX,
     '"R-AREA-NN": "normative requirement/obligation (161; 148 source-transcribed + 13 post-audit frozen addenda)"',
     '"R-AREA-NN": "normative requirement/obligation (168; 148 source-transcribed + 20 post-audit frozen addenda)"'),
    (BUILDIDX,
     '"M0NN": "baseline mutation registry (27; 18 baseline + 9 post-audit: M019–M025, M032, M034)"',
     '"M0NN": "baseline mutation registry (32; 18 baseline + 14 post-audit: M019–M029, M031, M032, M034)"'),
]

# C-86..C-92 rows: line-based, inserted after C-85's row
CONTRA_C85_PREFIX = "| C-85 |"


def apply_edits(files: dict[Path, str]) -> dict[Path, str]:
    for path, find, repl in EDITS:
        n = files[path].count(find)
        if n != 1:
            print(f"ABORT: anchor x{n} (need exactly 1) in {path.name}: {find[:70]!r}")
            sys.exit(2)
        files[path] = files[path].replace(find, repl, 1)
    lines = files[CONTRA].splitlines(keepends=True)
    idx = [i for i, ln in enumerate(lines) if ln.startswith(CONTRA_C85_PREFIX)]
    if len(idx) != 1:
        print(f"ABORT: C-85 anchor rows = {len(idx)} (need 1)")
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
    for want, got, what in ((168, n_ob, "obligations"), (168, n_mx, "matrix rows"), (148, n_rc, "records")):
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
    if "168 spec/01 obligations, 168 matrix rows" not in first or "148 records" not in first:
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
    for want in ("requirements=168", "findings=91", "mutations=32", "tags=19", "sections=24"):
        if want not in counts:
            print(f"  FAIL: index counts missing {want!r}")
            ok = False
    data = _json.loads((root / "spec" / "10-index.json").read_text(encoding="utf-8"))
    blob = _json.dumps(data)
    for m in NEW_IDS + ["C-86", "C-92", "M026", "M031", "resolved-by-addendum"]:
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
          f"SEC-007/008/009/010/011/012/017 unfrozen (this absence is the finding); "
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
