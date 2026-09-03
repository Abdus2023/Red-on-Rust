# MOD-11 — PERSISTENCE: Durable WAL, snapshots, effect journal (15B)

> Owns everything that survives a crash: the write-ahead log, atomic snapshots, the
> causal effect journal, and the durable issuance transaction.

## SECTION-ID

`MOD-11` (domain `PERSISTENCE`). Owner module file for the `PERSIST` and `DUR`
obligation areas.

## TITLE

Persistence protocol and the durability boundary — recording (not re-computing) the
machine; two-level framing (15A payload inside checksummed, sequence-checked WAL
frames); the unified effect journal; atomic snapshot protocol; WAL gap rejection;
and the durable-issuance-before-host-invocation transaction.

## PURPOSE

Provide durability *without becoming a second machine*: persistence records and
reconstructs the existing machine's state; it neither interprets semantics nor
maintains a shadow serialization. It is also the custodian of causality for external
effects — the journal entries (`Prepared`/`Issued`/`Completed`/`Reconciled`) are the
only admissible evidence of what may have happened in the world before a crash.

## NORMATIVE-CONTENT

Normative text home: `spec/01` S-18 (protocol) and S-13 (durability boundary, whose
mechanics are persistence's architectural responsibility — placement rationale in
`mod/00-overview.md` §3); atomic renderings
`req/01-registry-part5-persistence.md`. This module owns:

- **Separation** (R-PERSIST-01): persistence is recording, not a semantic machine;
  no secondary serialization — every record payload is strictly 15A output (MOD-10).
- **Two-level framing** (R-PERSIST-02): level 1 semantic envelope answers "what
  object"; level 2 `WalFrame { sequence (u64, strictly monotonic), kind (u8),
  payload_length (u32 BE checked), payload (15A bytes), checksum = SHA-256(sequence ‖
  kind ‖ payload_length ‖ payload) }` answers "where and intact". Nine mandated
  rejection classes (truncated headers/payloads, impossible lengths, checksum
  mismatch, invalid kinds, sequence regression, sequence gaps, malformed canonical
  payload, trailing bytes).
- **Record taxonomy** (R-PERSIST-03): `WalRecord ::= Event(EventEnvelope) |
  EffectPrepared | EffectIssued | EffectCompleted | EffectReconciled |
  SnapshotCommit`; `EventEnvelope` sequences strictly increase (journal/event unifi-
  cation per C-25/C-39; `EventSequence` vs `WalSequence` relationship open — U-16).
- **Snapshot content** (R-PERSIST-04): everything needed to continue (logical time,
  ID counters, runnable queue, per-actor run state/EvalState/capabilities/heap/
  budget/mailbox/status, scheduler state) plus `version`, `last_event_sequence`,
  `last_effect_sequence`, `state_digest`; host implementation state (OS handles,
  sockets, threads, unvalidated host objects) MUST NOT be serialized.
- **Atomic snapshot protocol** (R-PERSIST-05): begin marker → 15A payload → fsync →
  commit record (with `state_digest`) → fsync; `ValidSnapshot(S) ⇔ Commit(S) ∧
  Digest(Canonical(S)) = RecordedDigest(S)`; partial snapshots are garbage.
- **Sequence continuity** (R-PERSIST-06): `s_{n+1} = s_n + 1`; gaps and regressions
  rejected; also `Committed(D) ⇒ Canonical(D) ∧ IntegrityVerified(D)`
  (REQ-PERSIST-023).
- **Durability boundary, canonical statements** (R-DUR-01…05): `HostInvoked(E) ⇒
  DurableIssued(E)` (central restatement R-CORE-06 in MOD-01 — D-03); the strict
  7-step issuance transaction (validate → `append(EffectPrepared)` → fsync →
  `append(EffectIssued)` → fsync → actor `Pending` → host receives request); the
  causal journal protocol `Issued(E) ⇒ Prepared(E)`, `Completed(E) ⇒ Issued(E)`,
  `Reconciled(E) ⇒ Issued(E)` with identical ID+digest across an effect's records
  (mismatch ⇒ `EffectJournalCorruption`); crash classifications
  `Prepared ∧ ¬Issued ⇒ Discard` and `Issued ∧ ¬Completed ⇒ Indeterminate` — never
  `NotExecuted` by inference; and escrow durability: an issued-but-incomplete effect
  retains `complete_max` in the escrowed partition until reconciliation.

Crate contract (mirrored by pointer): `ror-persistence` — WAL, snapshots, effect
journal, recovery engine housing (R-REPO-02).

## NON-NORMATIVE-CONTENT

- The Phase 14 "separate durable effect journal" wording is superseded by unified
  WAL record kinds (C-25/C-39); logical separation is preserved by `kind`.
- The 19-step recovery listing (L34344–34364) vs the operative 12-step list is an
  open granularity discrepancy (AMB-27; ownership of recovery *semantics* is MOD-12).
- The v1 digest-overstatement ("same digest ⇒ byte-identical") is superseded by the
  collision-resistance-qualified claim (C-13, MOD-10's R-CANON-09).
- File-layout sketches (segment naming, checkpoint files) are engineering detail, not
  frozen.

## INPUTS

- Records to append: machine events (`ActorSelected`, `ActorSpawned`, `MessageSent`,
  `EffectCompleted`, `PlannerAccepted`, …) from MOD-05/06/07/08/13; effect journal
  records from MOD-08's step 14 path; snapshot images of `GlobalState` (MOD-06 owns
  the state, this module owns its durable image).
- Canonical bytes from MOD-10; digests from MOD-10's rules.

## OUTPUTS

- Durable artifacts: WAL segments, committed snapshots, journal records — the entire
  recovery substrate for MOD-12 (`D = ⟨S, L, H⟩`).
- `sync()` completion boundaries that make `DurableIssued` *true* (the fact MOD-08's
  step 16 and MOD-09 rely on).
- Rejection faults on framing/sequence/checksum violations (surfaced at recovery as
  `RecoveryFault` via MOD-12, never repaired here).

## DEPENDENCIES

- Module dependencies: MOD-01 (types), MOD-10 (payloads/digests — hard dependency per
  `spec/04` §A: S-13 depends on S-17).
- Producers of content: MOD-05…09, MOD-13; consumer of everything, decider of
  nothing semantic.
- Crate edge: `ror-persistence → ror-core` (no runtime/kernel edges, `spec/07` §6).
- Blocking open items: **U-02** (machine-state canonical encodings block snapshot
  byte-stability — with MOD-10), **U-16** (sequence relationship), **U-17**
  (snapshot queue vs reconstruction, with MOD-12/07), **U-15** (reconciliation record
  outcome variants, MOD-12-side).

## INVARIANTS

- `HostInvoked(E) ⇒ DurableIssued(E)` (R-DUR-01; canonical — central restatement
  R-CORE-06, D-03).
- Issuance transaction order with two fsync boundaries (R-DUR-02, 7 steps);
  crash harness points T0–T4 defined against it.
- `Issued(E) ⇒ Prepared(E)`; `Completed(E) ⇒ Issued(E)`; `Reconciled(E) ⇒ Issued(E)`;
  per-effect ID+digest identity chain (R-DUR-03).
- `Prepared ∧ ¬Issued ⇒ Discard`; `Issued ∧ ¬Completed ⇒ Indeterminate`
  (never `NotExecuted` by inference) (R-DUR-04).
- Escrow survival: issued-and-incomplete effects keep `complete_max` escrowed until
  reconciliation (R-DUR-05) — the durable face of budget conservation (D-02 partner).
- `ValidSnapshot(S) ⇔ Commit(S) ∧ Digest(Canonical(S)) = RecordedDigest(S)`
  (R-PERSIST-05); `s_{n+1} = s_n + 1` (R-PERSIST-06); `Committed(D) ⇒ Canonical(D) ∧
  IntegrityVerified(D)` (REQ-PERSIST-023).
- No secondary serialization: payload bytes are exactly MOD-10's output
  (R-PERSIST-01/02).

## REQUIREMENTS

Canonical text: `spec/01` S-18 + S-13; addenda II–IV. All 14 obligations `SPECIFIED`.

| ID | Obligation (short) | Provenance (`Red-on-Rust.md`) | Verification |
|---|---|---|---|
| R-PERSIST-01 | Persistence = recording, not a semantic machine; no secondary serialization | L33757–33790, L35078–35087 | dependency review (15B acceptance) |
| R-PERSIST-02 | Two-level framing; WalFrame checksum; rejection classes | L33802–33830, L35088–35110 | negative parsing tests, M016 |
| R-PERSIST-03 | Record taxonomy; EventEnvelope monotonic sequence | L33861–33900, L35111–35144 | sequence property; U-16 open |
| R-PERSIST-04 | Snapshot content (include/exclude lists) | L26293–26330 | snapshot review, U-02 blocking |
| R-PERSIST-05 | Atomic snapshot protocol; ValidSnapshot iff commit+digest | L26216–26240, L35177–35188 | `SNAPSHOT-COMMIT-INTEGRITY`, crash T6 |
| R-PERSIST-06 | WAL sequence continuity; gaps rejected | L35088–35110, L35189–35208 | `WAL-SEQUENCE-CONTINUITY`, `WAL-GAP-REJECT`, M015 |
| R-PERSIST-07 | Durable authority lattice: snapshot carries the AuthorityNode set, revocation_set and generation counters; WAL event kinds CapabilityGranted/Derived/Revoked; recovery reconstructs the arena, replays capability events, faults on dangling or generation-mismatched CapRef; revocation monotonic across crashes (RECOVERY-REVOCATION-DURABLE) | addendum II (SEC-004) | RECOVERY-REVOCATION-DURABLE, M023, crash matrix T0–T6 with pre-crash revocation |
| R-PERSIST-08 | Storage integrity rewinding resistance: chained checksums (checksum_n = H(checksum_{n−1} ‖ frame_n)); snapshot commit covers state digest + last WAL sequence; keyed chain if storage adversarial, else trust-table records the trusted-writable assumption; consistently-forged negative tests (C-88 resolved) | addendum IV (SEC-009) | tamper-at-every-T matrix, forged-record negatives |
| R-DUR-01 | HostInvoked ⇒ DurableIssued (D-03 canonical) | L35150–35156, L38050 | `EFFECT-ISSUE-DURABLE-BEFORE-HOST` |
| R-DUR-02 | Issuance transaction order (7 steps, 2 fsyncs) | L35150–35158 | crash harness T0–T4 |
| R-DUR-03 | Causal effect protocol (ID+digest identity chain) | L35111–35144, L38203–38215 | journal validator, M017 |
| R-DUR-04 | Prepared∧¬Issued⇒Discard; Issued∧¬Completed⇒Indeterminate | L35159–35176, L38222–38248 | `RECOVERY-ISSUED-INDETERMINATE` (MOD-12) |
| R-DUR-05 | Escrow survives crash | L35210–35215 | post-recovery invariant check, M008 |
| R-TRUST-05 | Crate DAG carries the R-DUR-02 hinge edge ror-runtime → ror-persistence (inverted trait superseded); ror-core → ror-kernel forbidden; forbidden-edge list checked against Cargo.toml; crate-separation rule (C-85 resolved) | addendum III (SEC-022) | Cargo.toml DAG mechanical check |

Atomic registry records under this module: REQ-PERSIST-001…023; REQ-DUR-001…014.
**14 obligations / 37 records.**

## SECURITY-BOUNDARY

Trust: persistence = Yes (R-TRUST-01) — it is where "the machine said so" becomes
*evidence*. The two sharpest attacks it must refuse are (a) host-before-durability
(reordering step 14 after step 16 turns crash recovery into lying about the world)
and (b) tolerance of corrupted WAL state (a parser that "repairs" gaps or checksums
launders corruption into trusted state — forbidden outright; detection points here,
classification in MOD-12). Mutations M015/M016/M008 exist precisely because these are
silent-failure magnets.

## VERIFICATION-OBLIGATIONS

- Tags: `WAL-SEQUENCE-CONTINUITY` / `WAL-GAP-REJECT` (R-PERSIST-06, M015),
  `SNAPSHOT-COMMIT-INTEGRITY` (R-PERSIST-05, T6), `EFFECT-ISSUE-DURABLE-BEFORE-HOST`
  (R-DUR-01, with MOD-08/09), `BUDGET-ESCROW-CONSERVATION` crash half (R-DUR-05, with
  MOD-04/08).
- Mutations: M008 (release indeterminate escrow), M015 (ignore WAL gap), M016
  (ignore checksum); M017 cross-owns with MOD-08 (digest mismatch on the journal
  chain R-DUR-03).
- Conformance: negative parsing suite per rejection class (R-PERSIST-02); journal
  causality validator; crash harness T0–T6 participation (matrix owned by MOD-12);
  post-recovery conservation invariant check (with MOD-12).
- Milestone gates: M7 (WAL, snapshot, journal, checksum, sequence continuity,
  recovery), M5 (durable issuance inside effects), M10 (crash classifications rely on
  these records).

## SOURCE-PROVENANCE

- 15B frozen: [47] (L35078–35258); architecture framing [46] (L33757–34916);
  superseded sketches [33] §2–5 (L26178–26270, C-39); master prompt §12/§13
  (L38185–38276, anchors corrected per `req/00-method.md` §5.1); snapshot content
  [33] (L26293–26330).
- Canonical set: `spec/02` S-13/S-18; `req/01-registry-part5-persistence.md`.

## CROSS-REFERENCES

Owned here, binding elsewhere:

- R-DUR-01/02 → MOD-08 (steps 14/16 of the request sequence invoke this boundary;
  the *sequence* is MOD-08's), MOD-09 (host invocation precondition), MOD-01
  (central restatement R-CORE-06 — D-03).
- R-DUR-04/05 → MOD-12 (applies the classifications at T1–T4 and re-checks the
  invariant), MOD-04 (escrow partition law).
- R-DUR-03 → MOD-08 (receipt digests continue the chain), MOD-12 (reconstruction).
- R-PERSIST-04 content list → MOD-05 (EvalState/frames), MOD-06 (actor state),
  MOD-03 (capability contexts), MOD-07 (runnable queue) — each module's state must be
  encodable (blocking via U-02, MOD-10).
- R-PERSIST-06 → MOD-12 (gap detection point during recovery).

Owned elsewhere, binding PERSISTENCE: R-CANON-01/02/09 (MOD-10 — payloads, checksums,
digests), R-EFFECT-03 step 14 (MOD-08), R-RECOV-01…07 (MOD-12 — consumes `D = ⟨S, L,
H⟩` produced here), R-PLANNER-02 (MOD-13 — planner cannot bypass persistence),
R-ORDER-03 property 4 (MOD-17 — host-after-durability gate evidence). Open items:
U-02, U-16, U-17, U-15 (MOD-12-side), AMB-02/09/14/27.
