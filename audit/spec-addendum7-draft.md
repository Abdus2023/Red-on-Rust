# Addendum VII — Request-pipeline remediation (ADOPTED 2026-09-03)

**Status:** APPLIED by `audit/spec_addendum7.py` (same discipline as addenda I–VI).

**Owner decisions** (recommendations of `audit/request-pipeline-proof-obligation-matrix.md` §5):

1. **U-39** — the master-prompt 16-step order is the one canonical request protocol; the
   turn-[21] host-before-Issued order is SUPERSEDED (quoted, not deleted) → `R-CORE-14`.
2. **U-40** — the step-10 premise is `t + δ_t(req) ≤ W`; the weak `t ≤ W` reading is SUPERSEDED
   → `R-CORE-14`. (The per-transition δ_t operands stay under U-07.)
3. **U-41** — durable issuance payloads carry `effect_bytes` + `EffectCost` triple
   → `R-DUR-06`.
4. **U-42** — live issuance failure is a declared `Fault::PersistenceError` with journal-driven
   commit, pre-s12 rollback, and `Prepared ∧ ¬Issued ⇒ Discard` → `R-DUR-07`.
5. **U-43** — recovery reconstruction authority: `next_effect_id` from replayed `Issued`,
   s12–s14b snapshot exclusion, completion order append→sync→charge→resume → `R-RECOV-09`.
6. **U-44** — verification tags `REQUEST-ARGS-LTR` and `REQUEST-NON-CAP-SHORT-CIRCUIT` join the
   R-TEST-07 obligation-tagged list → `R-TEST-12`.
7. **U-45 — DEFERRED** to a dedicated pass (candidate addendum VIII): the R-BUDGET-10…14
   adoption and the three-vs-five escrow-path reconciliation are NOT pre-empted here; C-108
   stays **corrected-in-place** and U-45 remains **open**.

**Re-graded:** `spec/06` C-103…C-107, C-109 → `resolved-by-addendum` (map: C-103/C-104 →
R-CORE-14; C-105 → R-DUR-06; C-106 → R-DUR-07; C-107/C-109 → R-RECOV-09).

**Registered:** `spec/08` mutations M037 (in-memory s12–s13 before journal append → R-DUR-07)
and M038 (`{id, actor, digest}`-only payload → R-DUR-06); tags `REQUEST-ARGS-LTR` and
`REQUEST-NON-CAP-SHORT-CIRCUIT`; harness mutants K19/K20 render both shapes against the frozen
text (D3-detectable, killed under the U-38 allow-list mode, documented as surviving the default
wiring while U-38 remains open).

**Register arithmetic:** 173 → 178 obligations (148 source + 30 post-audit addenda); 108
findings / 109 rows unchanged; 39 U- items unchanged (resolved ≠ deleted); mutations 36 → 38;
verification tags 19 → 21.

**Frozen text** (spec/01, each its own original — no substitution, `Original = Normalized`):

**R-CORE-14 (canonical request protocol and transaction boundary — frozen addendum).** The request sequence is exactly the 16-step master-prompt form: (1) evaluate capability; (2) evaluate target; (3) evaluate arguments left-to-right; (4) construct the canonical `Effect` and `EffectDigest`; (5) validate the CapRef; (6) authorize the exact effect; (7) capability ceiling; (8) runtime budget; (9) runtime reservation; (10) deadline; (11) host policy; (12) allocate the `EffectId`; (13) commit issue budget/reservation; (14) durable issuance; (15) actor `Pending`; (16) host invocation. The turn-[21] 16-step form — in which the host emission precedes the durable `Issued` record — is SUPERSEDED (quoted, not deleted): `HostInvoked(E) ⇒ DurableIssued(E)` holds with no ordering exception, and the S-12 presentment of that earlier order is read only as the superseded historical text (C-103). The step-10 deadline premise MUST be the post-advance form `t + δ_t(req) ≤ W`; the pre-advance `t ≤ W` reading is SUPERSEDED (C-104). Steps 12–14b form ONE atomic section: between allocation of the `EffectId` and the second fsync of the `Issued` record no `SnapshotCommit`, no scheduler yield and no observable event MAY occur. Live-failure semantics of that section are R-DUR-07; the recovery boundary (snapshot cadence, `next_effect_id` reconstruction, completion order) is R-RECOV-09. *(Frozen addendum VII — request-pipeline remediation, owner decision 2026-09-03; additive per R-SCOPE-03; extends R-EFFECT-01/03, R-BUDGET-06, R-DUR-02, R-CORE-06/12; resolves C-103/C-104, decisions U-39/U-40; no source transcription.)*

**R-DUR-06 (durable issuance payload — frozen addendum).** The issuance records MUST carry the effect and its cost: `EffectPrepared { id, actor, digest, effect_bytes, issue, complete_max, reserve }` and `EffectIssued { id, actor, digest, effect_bytes, issue, complete_max, reserve }` MUST be the persistence payloads — the canonical bytes of the effect, its `EffectDigest`, and the `EffectCost { issue, complete_max, reserve }`. The `{id, actor, digest}` shapes are SUPERSEDED as persistence payloads (quoted, not deleted); `{id, actor, digest}` remains valid only as the planner-visible observation projection (R-PLANNER-07). The escrowed `complete_max` and the reservation MUST thereby be reconstructible at every T0–T6 point: T1 discard restores from the record, T2–T4 classification and reconciliation carry the effect they must query about, and T5 resumption is byte-exact from the record. `effect_bytes` MUST verify `EffectDigest(effect_bytes) = digest` at append and at recovery — a mismatch is `EffectJournalCorruption` (C-105). The records MUST NOT contain raw capability values (R-CORE-07/R-CANON-12: the kernel-mediated codec governs). *(Frozen addendum VII — request-pipeline remediation, owner decision 2026-09-03; additive per R-SCOPE-03; extends R-DUR-02/05, R-PERSIST-03, R-EFFECT-05, R-RECOV-06; resolves C-105, decision U-41; mutation M038; no source transcription.)*

**R-DUR-07 (live issuance failure — frozen addendum).** Persistence failures on the issuance path are data, never panics (R-CORE-12), and MUST fault with the declared `Fault::PersistenceError`, added to the R-CORE-13 closed declaration by this addendum. The commit is journal-driven: `persistence.append(EffectPrepared …)` per R-DUR-06 followed by `persistence.sync()` is the ONE durable mutation that also journals the ID allocation and the budget/reservation/escrow commit; the in-memory mutations of steps 12–13 MUST NOT occur before that append+fsync returns Ok (C-106). On any append or sync error: the transition faults, `next_effect_id`, budget, reservations and escrow are at their pre-s12 values, the event log gains no entry, and `HostExecutor::execute` is NEVER invoked — R-EFFECT-04's five assertions hold on this path. A failure of the second `sync()` (the `Issued` record's fsync) is likewise `Fault::PersistenceError`, with the machine rolled back to the `Prepared`-durable state and the journal classifying the effect `Prepared ∧ ¬Issued ⇒ Discard` at recovery (R-DUR-04, R-RECOV-02 T1). No `InternalInvariant` classification is permitted for a storage error — this is the single declared fault family for the issuance path. *(Frozen addendum VII — request-pipeline remediation, owner decision 2026-09-03; additive per R-SCOPE-03; extends R-DUR-02/04, R-EFFECT-04, R-CORE-12/13, R-PERSIST-02/03; resolves C-106, decision U-42; mutation M037; no source transcription.)*

**R-RECOV-09 (recovery reconstruction authority — frozen addendum).** Recovery MUST reconstruct `next_effect_id = max({id ∈ replayed EffectIssued}) + 1`; a snapshot counter less than the journal maximum is stale and MUST be advanced (recorded, never silently repaired). A snapshot counter GREATER than the journal maximum is a `RecoveryFault`. No `SnapshotCommit` MAY exist with its last-effect sequence inside an issuance section (steps 12–14b) — the recovery of such a snapshot, if ever found, is a `RecoveryFault`, and the snapshot-taker MUST serialize against the section (C-107). The completion order is frozen: `append(EffectCompleted)`, then `sync()`, then the charge/release accounting, then the continuation resume (R-EFFECT-07) — a crash after the host returns but before that fsync is T4 (`Indeterminate`), and byte-exact resumption (T5) requires the fsync to precede the resume (C-109). *(Frozen addendum VII — request-pipeline remediation, owner decision 2026-09-03; additive per R-SCOPE-03; extends R-PERSIST-04/05/06, R-RECOV-02/03/07, R-EFFECT-07; resolves C-107/C-109, decision U-43; no source transcription.)*

**R-TEST-12 (request-frame verification tags — frozen addendum).** The R-TEST-07 obligation-tagged coverage list MUST additionally include `REQUEST-ARGS-LTR` (request arguments evaluated strictly left-to-right, exactly one per CEK step; step 3 of the frozen sequence, R-EFFECT-01) and `REQUEST-NON-CAP-SHORT-CIRCUIT` (a non-capability capability expression faults before any target/parameter evaluation and before any step 4–16 runs, with no `EffectId`, budget or log mutation and no host invocation; R-EFFECT-04). Both tags MUST be covered by the request-path Track A suite, registered in `spec/08`, and tracked in `mod/05`/`mod/08`. Coverage of these tags MUST NOT substitute for the differential oracle (R-TEST-07). *(Frozen addendum VII — request-pipeline remediation, owner decision 2026-09-03; additive per R-SCOPE-03; extends R-TEST-07; resolves decision U-44; no source transcription.)*

