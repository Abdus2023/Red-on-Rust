# Persistence Crash-Consistency Audit — effect causality, T0–T6 matrix, recovery discipline

**Status:** AUDIT — verification and gap classification only. No new frozen text is
issued here (R-SCOPE-03). This document verifies the existing frozen/addendum
contract against the requested audit criteria and records where the frozen text
already answers each question, where it requires a *reading* (AMB-27), and where a
residual open item still blocks an implementation claim.

**Scope:** `Prepared → Issued → Completed / Reconciled` causality, the durable
issuance boundary (R-DUR-01/02/06/07), the normative crash matrix T0–T6
(R-RECOV-02), the classification primitives (R-DUR-04), the no-silent-corruption
rule (R-RECOV-05/R-CORE-10), and recovery replay order (R-RECOV-03 + R-RECOV-09).
Out of scope: the whole fault-taxonomy declaration problem (`term/` X-67/AMB-33,
U-08), machine-state canonical encodings (U-02), and runnable-queue authority
(U-17), except where they prevent a claim from being *implementable* rather than
*stated*.

**Primary anchors:** `mod/11-persistence.md`, `mod/12-recovery.md`,
`mod/08-effect.md`, `mod/09-host.md`, `req/01-registry-part4-durability-concurrency.md`
(S-13/S-14), `req/01-registry-part5-persistence.md` (S-19), frozen Phase 15B
(`Red-on-Rust.md` L35078–35258, L38185–38276), and frozen addenda VII
(`audit/spec-addendum7-draft.md`) — R-CORE-14, R-DUR-06, R-DUR-07, R-RECOV-09.

**Mechanical gate.** These properties are also checked by
`audit/_crash_consistency_checker.py` (registered in `check.py`). It verifies the
presence of the normative clauses listed here in the canonical registry/spec/module
text, so an edit that weakens the causal ordering, the T0–T6 rows, the
never-`NotExecuted` rule, or the no-silent-repair rule causes `check.py` to fail.
It is a presence/clause gate, not a semantic verifier of the addenda wording, and
it does not replace the manual reading of this document.

---

## 0. Decision keys used in the matrix

| Term | Meaning used here |
|---|---|
| **recoverable** | The durable state is valid and sufficient to *produce* a recovered machine state (possibly with `Indeterminate` effects that must be reconciled). Not the same as "transparent". |
| **replayable** | Recovery can deterministically replay the requested causal sequence from the newest committed snapshot + WAL + effect journal, without re-executing the real world. |
| **indeterminate** | At least one effect has durable `Issued` and no durable `Completed`; the machine cannot know from its own records whether the host executed it. |
| **must reconcile** | An `Indeterminate` effect has been handed to the reconciliation protocol (R-RECOV-07/08); it must not be auto-resolved to `NotExecuted`. |
| **must reject** | The durable state is *invalid* and must raise `RecoveryFault` (frame, checksum, gap/regression, digest, causality, invariant mismatch). A *valid* T-row is never "rejected" merely because it is `Indeterminate`. |
| **must resume** | After validation/replay/classification/reconciliation (or, for completed work, after byte-exact reconstruction), deterministic scheduling restarts. A continuation that depends on an `Indeterminate` effect is **not resumed** until reconciliation. |

These two distinctions are the spine of the audit:

1. *Indeterminate is a valid durable state*, not corruption. `must reconcile` yes;
   `must reject` no.
2. *Invalid durable state is always a fault*. `must reject` yes; `must reconcile`
   no meaningful reconciliation happens off a corrupt base.

---

## 1. Causal ordering audit — requested direction

| Requested | Verified by | Status | Detailed evidence / qualifier |
|---|---|---|---|
| `Issued(E) ⇒ Prepared(E)` | REQ-DUR-005; R-DUR-03; Phase 15B causal protocol; journal validator (M017-class) | **PASS** | Every `EffectIssued` record must be preceded by an `EffectPrepared` for the same `(id, actor, digest)`. A bare `Issued` record with no `Prepared` is a causality violation → invalid durable state → `RecoveryFault`. |
| `Completed(E) ⇒ Issued(E)` | REQ-DUR-006; R-DUR-03; R-EFFECT-07 | **PASS** | `Completed` is write-only after durable issuance. A `Completed` with no `Issued` is a causality violation → `RecoveryFault`, never reinterpreted as a completion of a non-issued effect. |
| `Reconciled(E) ⇒ Issued(E)` | REQ-DUR-007; R-DUR-03; R-RECOV-07/08 | **PASS** | `Reconciled` is admissible only for effects that were durably issued and are (or were) `Indeterminate`. A `Reconciled` with no `Issued` is a causality violation → `RecoveryFault`. |
| Same-effect `id` + digest across `Prepared/Issued/Completed/Reconciled` | REQ-DUR-008/009; R-DUR-06 | **PASS (with a fault-surface caveat)** | A digest/ID mismatch is `EffectJournalCorruption`, not "a different effect". Residual: `EffectJournalCorruption` is not a member of the closed `Fault` enumeration (AMB-08; `req/01-registry-part4-durability-concurrency.md` row 126). This does not weaken crash *classification*, but it does block an exact closed error-surface claim until U-08/AMB-08 is resolved. |

**Verdict:** the requested causal order is normative and mechanically checkable.
No ordering violation exists in the frozen/addendum text. The only "ordering
escape" that was present historically — the turn-[21] host-before-`Issued`
16-step form — was resolved as superseded by R-CORE-14 (addendum VII; C-103).

---

## 2. The T0–T6 crash matrix, in the requested dimensions

"DP" = durable prefix as seen by recovery after power loss / process crash. Process
memory and in-flight host work are **not** evidence.

### T0 — before `Prepared` (nothing durable for this effect)

| Question | Answer |
|---|---|
| recoverable? | **YES** (from the newest committed snapshot / earlier WAL; no effect state exists) |
| replayable? | **YES** (nothing new in the causal chain) |
| indeterminate? | **NO** |
| must reconcile? | **NO** |
| must reject? | **NO** (unless unrelated durable state is corrupt — then yes, as a general rule) |
| must resume? | **YES** (normal deterministic execution) |

Contract: REQ-RECOV-003; R-DUR-07 (failure before the journal-driven `Prepared`
append = pre-issuance → no ID/budget/event mutation). With R-DUR-06/07 the
pre-s12 in-memory state and the durable state both show "no effect". Without the
addendum there was a snapshot-cadence hole (C-107) where a snapshot after an
in-memory step-13 commit could look like T0 while budget was already mutated; this
is now closed by R-DUR-07 (journal-driven commit) + R-RECOV-09 (no `SnapshotCommit`
inside steps 12–14b).

### T1 — after `Prepared`, before `Issued` (`Prepared` only, durable)

| Question | Answer |
|---|---|
| recoverable? | **YES** |
| replayable? | **YES** (replay stops at a discarded partial transaction) |
| indeterminate? | **NO** |
| must reconcile? | **NO** |
| must reject? | **NO** (valid durable record) |
| must resume? | **YES**, after discard + budget restore |

Contract: REQ-RECOV-004; R-DUR-04 (`Prepared ∧ ¬Issued ⇒ Discard`); R-DUR-06
(record carries `effect_bytes` + `issue/complete_max/reserve`, so the discard can
actually restore amounts); R-DUR-07 (a failure of the **second** `sync()` leaves
exactly this state). Important nuance: T1 is **recoverable** and **not
indeterminate** because the world was never touched — by construction,
`HostInvoked(E) ⇒ DurableIssued(E)` and there is no `Issued`, so the host was
never invoked (R-DUR-01). This is not an inference from absence of completion; it
is an inference from absence of *issuance*, which the frozen guarantee permits.

### T2 — after `Issued`, before host completion (`Prepared + Issued`)

| Question | Answer |
|---|---|
| recoverable? | **YES** (valid Durable prefix; actor stays `Pending`) |
| replayable? | **YES** (causal sequence intact; no real-world re-execution) |
| indeterminate? | **YES** |
| must reconcile? | **YES** |
| must reject? | **NO** |
| must resume? | **Partial**: the deterministic scheduler resumes, but the actor remains `Pending` and its continuation is **not** resumed until authoritative reconciliation. |

Contract: REQ-RECOV-005; REQ-DUR-011/012; R-DUR-04; R-RECOV-07/08;
R-DUR-05/RECOV-06 (escrow stays allocated). The **critical rule** applies at its
strongest: `Issued ∧ ¬Completed = Indeterminate`, never auto-`NotExecuted`.

### T3 — host invoked (`Prepared + Issued`, same durable facts)

| Question | Answer |
|---|---|
| recoverable? | **YES** |
| replayable? | **YES** (of the *machine*; no real-world execution) |
| indeterminate? | **YES** |
| must reconcile? | **YES** |
| must reject? | **NO** |
| must resume? | **Partial**: scheduler yes; the effect's continuation no until reconciliation. |

Contract: REQ-RECOV-006; REQ-DUR-011/012; R-DUR-04; R-RECOV-08. Key insight: the
fact "host was invoked" is **not separately durable**. `HostInvoked(E) ⇒
DurableIssued(E)` is one-directional; there is no `HostInvoked` WAL record. The
durable prefix for T2 and T3 is therefore **identical**, and the recovery
classification is identical. The implementation must not introduce a process-local
"invoked" boolean as if it were durable evidence. T3's only difference from T2 is
semantic (the host may actually have begun/executed), which is exactly why the
state is `Indeterminate` and why reconciliation must be authoritative.

### T4 — host completed, completion not durable (`Prepared + Issued`)

| Question | Answer |
|---|---|
| recoverable? | **YES** |
| replayable? | **YES** (the durable trace is replayed; the lost in-memory receipt is not reconstructed) |
| indeterminate? | **YES** |
| must reconcile? | **YES** |
| must reject? | **NO** |
| must resume? | **Partial**: scheduler yes; continuation no until reconciliation. |

Contract: REQ-RECOV-007; REQ-DUR-011/012; R-RECOV-09 (frozen completion order:
`append(EffectCompleted)` → `sync()` → charge/release → resume). The hard fact for
this row is **completion is not durable**. A process-local receipt can be lost; it
must never be treated as evidence after the crash. `Issued ∧ ¬Completed` is
`Indeterminate`, even though the host "completed" in-process. This is the
text-book case for the critical rule: the effect is **not** absent, and the
machine must not re-issue it, must not treat it as a no-op, and must not release
escrow on assumption.

### T5 — after `Completed`, durable (`Prepared + Issued + Completed`)

| Question | Answer |
|---|---|
| recoverable? | **YES** |
| replayable? | **YES** |
| indeterminate? | **NO** |
| must reconcile? | **NO** |
| must reject? | **NO** (valid records) |
| must resume? | **YES**, and byte-exactly from the recorded receipt. |

Contract: REQ-RECOV-008; R-DUR-03 (`Completed ⇒ Issued`); R-HOST-06
(`EffectCompleted { id, digest, result_digest, result: CanonicalData }` +
`ResultDigest(result) = result_digest` before resumption); R-RECOV-09
(completion order boundary). **Critical dependency:** byte-exact T5 resumption is
only implementable if R-HOST-06 is normative (the frozen Phase 15B `EffectCompleted`
shape alone has only `result_digest` and cannot resume a continuation). This was
the C-90/SEC-011 hole; it is closed by addendum IV / R-HOST-06. If a
conformance target reads only the 15B body and not the addenda, T5 will be
recoverable but **not** resumable byte-exactly.

### T6 — after `SnapshotCommit` (snapshot + WAL present)

| Question | Answer |
|---|---|
| recoverable? | **YES** (newest committed snapshot + post-snapshot WAL is the recovery base) |
| replayable? | **YES** (only post-snapshot records are replayed; R-PERSIST-06, R-RECOV-02 T6) |
| indeterminate? | **Depends on the effect prefix inside the snapshot/WAL** — if any `Issued` without `Completed` survives, yes; otherwise no. T6 is not itself a per-effect classification. |
| must reconcile? | **Yes iff** an `Issued ∧ ¬Completed` effect survives; otherwise no. |
| must reject? | **Definitely** if snapshot is partial/invalid, digest mismatch, WAL gap/regression, checksum/causality failure, or (R-RECOV-09) a snapshot's last-effect sequence is inside an issuance section. **No** just because it is a snapshot point. |
| must resume? | **YES** after replay *and* after reconciliation of any surviving Indeterminate effects. |

Contract: R-PERSIST-05 (`ValidSnapshot ⇔ Commit ∧ Digest`); R-PERSIST-06
(`s_{n+1} = s_n + 1`); R-PERSIST-08 (chained checksums, snapshot commit covers
state digest + last WAL sequence); REQ-RECOV-009; R-RECOV-03; R-RECOV-09
(snapshot cadence + `next_effect_id` reconstruction authority). T6 does **not**
get a blanket `Indeterminate`; it is the boundary at which replay begins. The
recovery must carry over any issued-but-incomplete effects into reconciliation.

---

## 3. Validation-order and recovery-algorithm cross-check

The user requested a 10-step recovery sequence. The frozen spec contains a
**12-step** list (R-RECOV-03 / REQ-RECOV-010) and a **19-step** granularity
variant (REQ-RECOV-021; AMB-27). The requested sequence is a reasonable
projection; the mapping is:

| Requested step | Frozen 12-step equivalent | Conformance note |
|---|---|---|
| 1. load newest committed snapshot | 1 (`locate newest committed snapshot`) | `R-PERSIST-04` / `R-PERSIST-05` |
| 2. verify integrity | 2–3 (verify framing/checksum, decode 15A) + `R-PERSIST-08` | checksum, canonical decode, digest; never repaired |
| 3. replay subsequent WAL | 7 (replay records after snapshot sequence) | ordered sequential replay |
| 4. verify sequence continuity | 6 (`verify sequence continuity and reject gaps`) | before replay, not after it |
| 5. reconstruct machine state | 7 (replay) + 4 (validate recovered `GlobalState`) | this is the union of replay + validation |
| 6. reconcile effect journal | 8–9 (reconstruct effect journal, validate causal chains, classify interrupted effects) **+ post-recovery R-RECOV-07** | **discrepancy**: the 12-step list does *not* perform reconciliation *inside* `Recover(D)`; it classifies and hands off. The 19-step variant *does* list reconciliation before queue reconstruction (AMB-27). |
| 7. rebuild runnable queue | 10 (reconstruct runnable queue from actor states) | U-17 still open on snapshot-queue vs reconstruction authority |
| 8. validate invariants | 4 (initial `GlobalState`) + 11 (final digest vs checkpoint) + R-RECOV-06 (budget) | validation is both early and terminal |
| 9. enter recovery mode | 12 (`RecoveryComplete` + resume deterministic scheduler) | `RecoveryComplete` after all validation, classification, and reconciliation hand-off |
| 10. resume deterministic execution | 12 (resume scheduler) | Pending/Indeterminate continuations are not resumed until reconciliation |

**Audit finding F-01 (consistency, not correctness):** a recovery implementation
that reads the requested "step 6 = reconcile effect journal" literally and
resolves the journal *before* `RecoveryComplete` would match the 19-step variant
(REQ-RECOV-021) but not the canonical 12-step list (REQ-RECOV-010), which keeps
reconciliation outside `Recover(D)`. Both lists are frozen text; AMB-27 is open as
a granularity discrepancy. **The safe, already-normative reading is:** inside
`Recover(D)` you reconstruct, validate, and *classify* the effect journal; you do
**not** resolve `Indeterminate` effects (R-RECOV-07/08 say the only resolver is
the reconciliation protocol); you then reach `RecoveryComplete` and only then do
reconciliation/supervisor work drive continuation resumption. If the owner wants
the requested 10-step wording to be normative, it should be frozen as an
addendum (resolving AMB-27), not inferred.

**Audit finding F-02 (critical rule / no-silent-reinterpretation):** PASS.
`Issued ∧ ¬Completed ⇒ Indeterminate` and "never automatically `NotExecuted`" are
normative in R-DUR-04, REQ-DUR-011/012, R-RECOV-07, R-RECOV-08 (SEC-010/C-89),
and the frozen Phase 15B "Crucial Rule". An "incomplete issued" effect is never
reinterpreted as absent. It is held as `Indeterminate`, escrow remains allocated
(R-DUR-05/RECOV-06), and only authoritative reconciliation resolves it.

**Audit finding F-03 (corruption):** PASS at the contract level.
`Invalid(D) ⇒ RecoveryFault`; `R-RECOV-05` explicitly forbids dropping duplicate
runnable actors, fixing budget mismatches, ignoring gaps/checksums/causality
violations; `R-PERSIST-08` adds chained checksums + snapshot cover + rewritten-forgery
negative tests (SEC-009/C-88); credit-checker mutations M015/M016/M017 and
recovery mutations are targeted at these silent failures. This is exactly the
"never silently repair" requirement.

---

## 4. Implementation-critical details (already required by frozen text)

1. **Durable issuance payload.** `EffectPrepared`/`EffectIssued` MUST carry
   `effect_bytes` + `(issue, complete_max, reserve)` (R-DUR-06; M038). Without
   this, T1 cannot restore amounts, T2–T4 cannot query the effect
   authoritatively, and T5 cannot resume byte-exactly. The `{id, actor, digest}`
   shape is superseded *as a persistence payload* and remains only as the
   planner-visible observation projection (R-PLANNER-07).

2. **Journal-driven commit.** Steps 12–14b are one atomic section; no
   `SnapshotCommit`, no scheduler yield, no observable event inside it
   (R-CORE-14). `Prepared` append + fsync is the single durable mutation that also
   journals ID allocation and budget/escrow/reservation commit (R-DUR-07; M037).
   Failing that means pre-s12 state and a `Fault::PersistenceError`, never a
   panic and never an unclassified storage failure.

3. **Completion order.** `append(EffectCompleted)` → `sync()` → charge/release → resume
   (R-RECOV-09). A crash after host return but before that sync is T4
   (`Indeterminate`). A crash after the sync is T5 (`Completed`; resume
   byte-exactly).

4. **Recovery reconstruction authority.** `next_effect_id = max(replayed
   `Issued`) + 1`; snapshot counter less than journal max is advanced (recorded,
   never silently repaired); greater than journal max is a `RecoveryFault`
   (R-RECOV-09). Any `SnapshotCommit` whose last-effect sequence is inside the
   issuance section is a `RecoveryFault`.

5. **Escrow.** An issued-but-incomplete effect keeps `complete_max` in the escrowed
   partition through crash and recovery (R-DUR-05, R-RECOV-06). It is released
   only by completion accounting or a reconciliation outcome per the frozen
   admissible-outcome table (R-RECOV-08; R-BUDGET-09/10/11).

6. **Independent recovery engine.** Production recovery is never its own
   reference/replay oracle; two implementations are required
   (R-RECOV-04/05, R-REF-02, REQ-TEST-045; `ror-reference` for the independent
   oracle).

---

## 5. Residual open items that touch this audit

| Item | Impact | Owner |
|---|---|---|
| **AMB-27 / REQ-RECOV-021** | Exact order of "reconcile interrupted effects" vs queue/validation is a 12-step vs 19-step granularity discrepancy. Matters if an implementation asserts the *requested* 10-step list verbatim. | MOD-12 → addendum / owner decision |
| **U-02 / U-34** | Machine-state canonical encodings must be stable before T5/T6 byte-exact byte-stability can be proven (snapshot decode + result/value encodings). | MOD-10/11; blocks M7/M10 byte-level claims |
| **U-17** | Snapshot-carried runnable queue vs reconstruction authority is unspecified (REQ-RECOV-018, C-26, AMB-09); a mismatch is high-severity (double-scheduling). | MOD-12/07 |
| **U-08 / AMB-08 / AMB-33** | `EffectJournalCorruption` and replay/host fault names are not closed in the frozen `Fault`/`HostFault` enumerations. Does not change crash classification; blocks an exact error-surface contract. | `spec/09` U-08/U-14 |
| **U-06 / U-15** | Per-effect-class reconciliation outcomes and their admissibility are partly frozen (R-RECOV-08) but class semantics remain open for the host query policy. | MOD-01/09/12/13 |

None of these make the crash matrix *unanswerable*; they make specific *byte-level
implementation claims* (T5/T6) and *closed error-vocabulary claims* depend on
still-open decisions.

---

## 6. Verdict

| Requirement | Verdict |
|---|---|
| `Issued ⇒ Prepared` | **SATISFIED** |
| `Completed ⇒ Issued` | **SATISFIED** |
| `Reconciled ⇒ Issued` | **SATISFIED** |
| Required issuance order (`HostInvoked ⇒ DurableIssued`) | **SATISFIED** (R-DUR-01/02/06/07; C-103/R-CORE-14 closes the historical inversion) |
| Crash matrix T0–T6 | **SATISFIED** as a classification contract; all rows are *recoverable*; T0/T1/T5/T6 are clean, T2/T3/T4 are `Indeterminate` + reconcile, T5 *must resume*, T6 *must replay* |
| "Issued but incomplete ≠ Not Executed" | **SATISFIED** and enforced by R-DUR-04/REQ-DUR-012/R-RECOV-07/08 |
| Recovery load snapshot → integrity → WAL → continuity → reconstruct → classify/reconcile → queue → invariants → recovery mode → resume | **SATISFIED in spirit**, with exactly one normative-order discrepancy (F-01: reconciliation-vs-RecoveryComplete) recorded under AMB-27 |
| Corruption never silently repaired | **SATISFIED** (R-PERSIST-05/06/08, R-RECOV-05, R-CORE-10; M015/M016/M017) |

**Bottom line:** the persistence contract in `Red-on-Rust` already satisfies the
requested crash-consistency property *if* the frozen addenda (R-DUR-06/07,
R-RECOV-09, R-HOST-06, R-PERSIST-08) are treated as normative — they are the
parts that make T1/T2–T4/T5 reconstruction actually implementable. The only
substantive audit flag is the recovery-step ordering discrepancy (AMB-27),
which should be resolved by freezing one normative step list (or by explicitly
declaring reconciliation a post-`RecoveryComplete` activity, which is the
canonical 12-step reading).
