# Addendum IV — MEDIUM freeze (SEC-007 / 008 / 009 / 010 / 011 / 012 / 017)

**Status: APPLIED** via `audit/spec_addendum4.py --apply` (adoption commit on
`arena/01a063c4-red-on-rust`; post-apply verification on the real tree:
168 obligations / 168 matrix rows / 148 records, `spec/_check.py` D1=0 exit 0,
index rebuilt at 168/91/32/19, `req/_validate.py` exit 0 / ERRORS 0, applier
idempotency guard armed). This file is retained as the review record of
exactly what was adopted and why; rollback is `git revert` of the adoption
commit. The exact edit set lives in `audit/spec_addendum4.py` (this draft was
generated from its constants, so the two cannot drift); its dry run is
full-fidelity — a `git archive` sandbox of HEAD receives the edits and the
entire verification stack (`audit/spec_check.py`, `spec/_build_index.py`,
`req/_validate.py`) runs there.

## 1. What this freezes (report §6 items 6-7)

| Addendum | Freezes | Extends / resolves |
|---|---|---|
| `R-PLANNER-06` | SEC-007: staleness is **exact equality** — `observation_sequence = current_planning_epoch`; either-direction mismatch ⇒ `StalePlan` + zero state mutation; `<`-only reading superseded; future-tagged proposals a mandatory rejection test; C-38's description corrected | extends R-PLANNER-03/05; resolves C-86; M026 |
| `R-PLANNER-07` | SEC-008: observation channel capability-opaque — `CapabilitySummary` frozen as a non-referential projection; `EffectIssued` = `{id, actor, digest}` only (cap-bearing log shape superseded); observation projection rule; `Capability ∉ Observables(LLM)` | extends R-PLANNER-01/R-KERN-01; resolves C-87; M027 |
| `R-PERSIST-08` | SEC-009: storage rewinding-resistance — chained checksums (`checksum_n = H(checksum_{n−1} ‖ frame_n)`); snapshot commit covers state digest + last WAL sequence; keyed chain iff storage adversarial, else the trusted-writable assumption recorded in the trust table; consistently-forged negative tests | extends R-PERSIST-02/05; resolves C-88 |
| `R-RECOV-08` | SEC-010: reconciliation frozen — I2 holds on every host path incl. supervisor; never re-executes (idempotent query at most); compensations are ordinary gated requests; `NotExecuted` gated behind authoritative evidence; supervisor allocates lifecycle, not effects | extends R-DUR-04/05, R-RECOV-07; resolves C-89 (U-06/U-15 direction); M028 |
| `R-HOST-06` | SEC-011: durable receipts representable — `EffectCompleted {id, digest, result_digest, result: CanonicalData}`; replay verifies `ResultDigest(result) = result_digest` (third identity conjunct); no ad-hoc result records | extends R-EFFECT-06/08, R-HOST-03/04; resolves C-90; M029 |
| `R-CORE-13` | SEC-012: closed declared fault surface — six replay-path variants, `StalePlan`, unified `MarshalFault`, `InternalInvariant` declared; no debug-formatted external error text in machine values; resume-vs-fault pinned per variant | extends R-SCOPE-03/R-REF-05/R-EFFECT-08; resolves C-91 (U-08/U-14 direction) |
| `R-CANON-13` | SEC-017: one canonical grammar — 15A BE sole; LE revised grammar superseded in-source; one `TAG_*` namespace (X-50/X-54 resolved); all digests over 15A; bidirectional byte-exact golden vectors, LE variants rejected | extends R-CANON-01/11, R-PERSIST-01; resolves C-92; M031 |
| `C-86…C-92` (spec/06) | security consequences registered (MAJOR ×3, BLOCKING ×4), all `resolved-by-addendum` | rows after C-85 |
| `M026–M029`, `M031` (spec/08) | kill targets for the above | registry → M001–M029, M031, M032, M034 |

## 2. Exact normative texts (spec/01 insertions)

**R-PLANNER-06 (staleness is exact equality — frozen addendum).** `AcceptProposal(p) ⇔ p.observation_sequence = current_planning_epoch` — EXACT EQUALITY. A proposal whose `observation_sequence` differs from the current planning epoch in EITHER direction MUST be rejected with `Fault::StalePlan` and zero state mutation; the strictly-less-only reading (reject only when `< current`, thereby accepting future-tagged proposals) is SUPERSEDED (quoted, not deleted). The epoch check is the exact planner-boundary check: a proposal is causally bound to the machine state it was generated from, in both directions. Future-epoch proposals are a mandatory rejection test (`obs_seq ∈ {current−1, current, current+1, current+10⁹}`: accept only `current`, zero state mutation on both rejections). C-38's canonical description is corrected hereby: the two phrasings define different acceptance sets, not one check stated twice. *(Frozen addendum — post-audit remediation SEC-007; additive per R-SCOPE-03; extends R-PLANNER-03/R-PLANNER-05; resolves C-86; mutation M026; no source transcription.)*

**R-PLANNER-07 (observation channel is capability-opaque — frozen addendum).** The untrusted observation channel MUST be capability-opaque by construction: `Observation` carries capability *summaries* — counts, operation classes, ceilings — NEVER references; `CapabilitySummary` is frozen as a non-referential projection (defining the phantom); `Capability ∉ Observables(LLM)` is the dual of `LLMOutput ∈ Data`. The `EffectIssued` log/event shape carries `{id, actor, digest}` ONLY — the `EffectRequest`-with-`cap` shape in the log is SUPERSEDED (quoted, not deleted; the v0.3 rule-5 shape governs), and the `EffectRequest.cap` shape conflict is registered. Events visible to the planner are filtered/redacted by a frozen observation projection rule. Property: for every machine state and observation emission, `contains_capability(Observation) = false` (recursive, events included); no `0x30`/`0x05` payloads appear in planner-facing canonical encodings. *(Frozen addendum — post-audit remediation SEC-008; additive per R-SCOPE-03; extends R-PLANNER-01/R-KERN-01; resolves C-87; mutation M027; no source transcription.)*

**R-PERSIST-08 (storage integrity rewinding-resistance — frozen addendum).** Persistence integrity MUST gain rewinding resistance: WAL checksums MUST be chained (`checksum_n = H(checksum_{n−1} ‖ frame_n)`) so rewrite or truncation of any prefix breaks every later frame; the snapshot commit record MUST cover the state digest and the last WAL sequence. If the storage medium is adversarial, the chain MUST be keyed (MAC or signature over the sequence-linked chain; key-epoch mismatch ⇒ `RecoveryFault`); if the storage medium is trusted-writable, that assumption MUST be recorded in the trust table as such — keyless chaining detects corruption and rewinding but does not authenticate, and the accepted risk is documented explicitly. Consistently forged records (recomputed checksums, contiguous sequences, balanced budget) are the mandatory negative test class. `Durable(D) ⇒ Authentic(D)` where keyed; the effect evidence chain (`Prepared → Issued → Completed → Reconciled`) must be unforgeable, not merely well-ordered. *(Frozen addendum — post-audit remediation SEC-009; additive per R-SCOPE-03; extends R-PERSIST-02/R-PERSIST-05; resolves C-88; no source transcription.)*

**R-RECOV-08 (reconciliation protocol — frozen addendum).** Reconciliation is frozen: I2 (the 7-conjunct chain) holds for EVERY host invocation path including supervisor/reconciliation ones — `Reconcile(E) ⇒ Issued(E) ∧ outcome ∈ AdmissibleOutcomes(class(E))`, with per-effect-class admissible outcome variants (closing U-06/U-15 in the security direction). Reconciliation NEVER re-executes an effect: an idempotent host query at most; any compensating or retry action is itself an ordinary `Request` through gates 1–16. `NotExecuted` as a durable resolution is gated behind authoritative host-reconciliation evidence — no component, trusted or not, may resolve `Indeterminate → NotExecuted` on local policy (R-DUR-04); `Completed(EffectReceipt)` inherits the R-EFFECT-08 result-admission rule and R-HOST-06 result-digest verification. The Supervisor allocates lifecycle decisions, not effects: `Supervisor.host` is reachable only through the issuance boundary. Escrow moves only per the frozen admissibility table. *(Frozen addendum — post-audit remediation SEC-010; additive per R-SCOPE-03; extends R-DUR-04/R-DUR-05/R-RECOV-07; resolves C-89; mutation M028; no source transcription.)*

**R-HOST-06 (durable receipt results — frozen addendum).** Durable receipt results MUST be representable under a frozen contract: `EffectCompleted` carries `{id, digest, result_digest, result: CanonicalData}` — `result` scoped to the canonical data domain (R-CANON-12 / the R-EFFECT-08 admission rule). Replay MUST verify `ResultDigest(result) = result_digest` before the receipt may resume anything: a third identity conjunct extending R-EFFECT-06 (id, effect digest, result digest). Tampering `result` while keeping the digest-pair ⇒ `ReplayCorruption`. No ad-hoc result-bearing record kind may exist outside this contract (the unfrozen-record channel is closed); T5 recovery resumes the continuation with the recorded result byte-exactly. *(Frozen addendum — post-audit remediation SEC-011; additive per R-SCOPE-03; extends R-EFFECT-06/R-EFFECT-08/R-HOST-03/R-HOST-04; resolves C-90; mutation M029; no source transcription.)*

**R-CORE-13 (closed declared fault surface — frozen addendum).** The fault surface on every trust-boundary crossing (host→machine, storage→recovery, planner→machine) MUST be closed and declared: the full fault/error enumeration is frozen, including the six undeclared replay-path variants (`ReplayTraceExhausted`, the `ReplayCorruption` family), `StalePlan`, the unified `MarshalFault` (R-MARSHAL-05), and the `InternalInvariant` family (R-CORE-12); the two-variant `HostFault` declaration is SUPERSEDED (quoted, not deleted). Host faults map onto a closed machine-fault set; `format!("{:?}")` debug text of external errors MUST NOT enter machine values — opaque error codes or digests only (extends R-EFFECT-08 item 4). Resume-vs-fault behavior is pinned per variant: which faults resume continuations, which park actors, the budget effect, and the event-log delta — security-critical semantics, not cosmetics; differential fault comparison (R-REF-05) compares these four, not just labels. *(Frozen addendum — post-audit remediation SEC-012; additive per R-SCOPE-03; extends R-SCOPE-03/R-REF-05/R-EFFECT-08; resolves C-91, closing U-08/U-14 in the security direction; no source transcription.)*

**R-CANON-13 (one canonical grammar — frozen addendum).** Exactly ONE canonical byte grammar is frozen: Phase 15A — universal envelope `version u8 / type_tag u8 / payload_length u32 BE`, length prefixes `u32 BE`, `CapRef [index u32 BE][generation u32 BE]`. The revised-grammar Little-Endian sections are SUPERSEDED in-source (quoted, not deleted); field names are the 15A names (`payload_length`); the `TAG_*` constants denote ONE namespace (the 15A tags; the revised-grammar tag set is superseded) — resolving term/ X-50/X-54. All integrity predicates (`EffectDigest`, `StateDigest`, `ResultDigest`, WAL checksum inputs) are defined over 15A bytes alone; cross-implementation digest equality is meaningful by construction (R-CANON-01: canonical encoding defines semantic identity). Golden vectors are asserted byte-exact bidirectionally for production, reference, and the persistence payload writer; LE-encoded variants of every golden vector MUST be rejected by all three. *(Frozen addendum — post-audit remediation SEC-017; additive per R-SCOPE-03; extends R-CANON-01/R-CANON-11/R-PERSIST-01; resolves C-92; mutation M031; no source transcription.)*

## 3. Companion edits

spec/03 (+7 rows, Total **168** = 148 + 20 addenda), spec/06 (+C-86…C-92),
spec/08 (+5 mutation rows, registry title), records scope note, README (168
IDs), `spec/_build_index.py` (sections S-02/05/14/17/18/19, rows, mutations,
milestones M1/M5/M7/M10, crates core/persistence/runtime/agent, id-scheme
counts 168/32), `req/_validate.py` (recorded register growth 85 → 92 raw
C-rows).

## 4. Verification record (pre-apply, full-repo sandbox)

- Precheck: addendum ABSENT (all 12 markers), 48 anchors intact.
- Sandbox (git archive of HEAD + edits): obligations/matrix/records =
  168/168/148; `spec_check` parses 148/168/168, D1=0, no FAIL, zero warnings
  on the seven new obligations; index rebuild
  `requirements=168 findings=91 mutations=32 tags=19`;
  `req/_validate.py` exit 0, ERRORS 0.
- Checker warnings moved 36 → 35: the delta is exactly the pre-existing
  R-RECOV-07 D2 warning (0.21). Attribution: the body-capture parser was
  absorbing the trailing `--- / # Part VII` separator into R-RECOV-07's body
  (that separator noise *was* its sub-threshold score); with R-RECOV-08
  inserted as S-19's new last obligation, the separator rides in R-RECOV-08's
  parsed body (no citations, D3 passes) and R-RECOV-07 measures clean. A
  parsing artifact relocated, not a content change — diff-verified warning
  line by warning line.
- New-row body↔matrix D3 overlaps: R-PLANNER-06 0.76, R-PLANNER-07 0.90,
  R-PERSIST-08 0.76, R-RECOV-08 0.82, R-HOST-06 0.85, R-CORE-13 0.90,
  R-CANON-13 0.73.

## 5. Adoption procedure

1. `python3 audit/spec_addendum4.py` — re-run the full-sandbox proof.
2. `python3 audit/spec_addendum4.py --apply` — 48 edits across 8 files; every check re-runs on the real tree in-step.
3. `python3 spec/_check.py` — gate must exit 0; `git revert` is the rollback.

Generated from `audit/spec_addendum4.py` constants — 2026-09-03.
