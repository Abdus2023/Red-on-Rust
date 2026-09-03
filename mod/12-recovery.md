# MOD-12 — RECOVERY: Crash recovery and effect classification

> Owns the resurrection contract: from durable artifacts alone, reconstruct exactly
> the pre-crash machine — and never lie about an effect that may already have
> happened.

## SECTION-ID

`MOD-12` (domain `RECOVERY`). Owner module file for the `RECOV` obligation area.

## TITLE

Crash recovery — `Recover(D) = Replay(S, L, H)`; the normative T0–T6 crash matrix;
the 12-step recovery algorithm; recovery-engine independence; strict no-repair
validation; budget-conservation survival; and reconciliation as the only resolution
path for indeterminate effects.

## PURPOSE

Make crash semantics causal, not wishful. Recovery properties follow from *durable
fact ordering*, never from absence of records: a missing completion record never
implies "not executed" (the host may have executed it). Recovery is an independent
implementation — the production execution path is never its own oracle — and any
invalid durable state is an explicit `RecoveryFault`, never a silent repair.

## NORMATIVE-CONTENT

Normative text home: `spec/01` S-19; atomic renderings
`req/01-registry-part5-persistence.md` (RECOV block). This module owns:

- **Durable state and recovery-as-replay** (R-RECOV-01): `D = ⟨S, L, H⟩` (latest
  committed snapshot, durable event log after it, durable effect journal);
  `Recover(D) = Replay(S, L, H)`; and `CommittedSnapshot + ValidWAL +
  ValidEffectJournal + ReconciledEffects ⇒ UniqueRecoveredMachineState`
  (REQ-RECOV-022).
- **Normative crash matrix** (R-RECOV-02) — canonical operative form of the central
  qualified recovery theorem (central restatement R-CORE-09 in MOD-01 — D-06):

  | Point | Durable state | Required result |
  |---|---|---|
  | T0 before `Prepared` | none | effect does not exist; no budget mutation; resume |
  | T1 after `Prepared` | `Prepared` only | discard incomplete preparation; resume |
  | T2 after `Issued` | `Prepared + Issued` | **Indeterminate**; reconciliation required |
  | T3 host invoked | `Prepared + Issued` | **Indeterminate** (host may have executed) |
  | T4 host completed (not durable) | `Prepared + Issued` | **Indeterminate** (completion not durable) |
  | T5 after `Completed` | `Completed` durable | reconstruct completed effect; resume continuation |
  | T6 after `SnapshotCommit` | snapshot + WAL | recover snapshot base; replay subsequent records |

- **Recovery algorithm** (R-RECOV-03, 12 steps): locate newest committed snapshot →
  verify framing/checksum → decode 15A (MOD-10) → validate `GlobalState` invariants
  (budget conservation, no duplicate runnable actors) → verify WAL framing/checksums
  → verify sequence continuity, reject gaps → replay records after snapshot sequence →
  reconstruct effect journal, validate causal chains → classify interrupted effects
  → reconstruct runnable queue → compare final digest against trailing checkpoint →
  enter `RecoveryComplete`, resume the deterministic scheduler (MOD-07). (A 19-step
  granularity variant exists in the source; discrepancy open — AMB-27.)
- **Independence** (R-RECOV-04): the recovery engine is an independent implementation
  from the normal execution path; production recovery is never the reference recovery
  oracle (anti-oracle-collapse, with MOD-14's R-REF-02 and REQ-TEST-045).
- **Strict validation** (R-RECOV-05): `Invalid(D) ⇒ RecoveryFault`; never silent
  repair (no dropping duplicate runnable actors, no fixing budget mismatches, no
  ignoring gaps/checksums/causality violations) — canonical operative statement of
  the central no-silent-corruption invariant (central restatement R-CORE-10 in
  MOD-01 — D-07).
- **Budget survival** (R-RECOV-06): `C_available + C_escrowed + C_consumed =
  C_initial` survives crashes identically (post-recovery revalidation of MOD-04's
  law — D-02 partner, not a duplication: the crash-time survival clause).
- **Reconciliation** (R-RECOV-07): `Issued ∧ ¬Completed` effects go to the
  supervisor's reconciliation policy; `Reconciled(E) ⇒ Issued(E)`; outcomes are
  durable (`EffectReconciled`); reconciliation is the **only** path by which an
  Indeterminate effect resolves; the system never auto-resolves to "not executed";
  no transparent recovery is claimed for indeterminate effects (REQ-RECOV-017).

Crate contract (mirrored by pointer): recovery engine in `ror-persistence`; the
independent recovery oracle in `ror-reference` (R-REPO-02).

## NON-NORMATIVE-CONTENT

- The 19-step recovery enumeration (L34344–34364) vs the operative 12-step list
  (L35193–35204) — open granularity discrepancy (AMB-27); both recorded, neither
  silently merged.
- The unqualified `Recover(D) = pre-crash state` phrasing of Phase 14 §1 is
  superseded by the qualified theorem (C-40; qualification kept verbatim in MOD-01's
  R-CORE-09).
- Reconciliation policy sketches (supervisor behavior) are outside the frozen machine
  core; only the record contract is frozen.

## INPUTS

- `D = ⟨S, L, H⟩` — durable artifacts from MOD-11 (snapshots, WAL, journal).
- Canonical decode + digest services from MOD-10.
- Host reconciliation outcomes (authoritative, per effect class — MOD-09 side;
  outcome variant set open under U-15).
- The determinism discipline to re-enter scheduling (MOD-07).

## OUTPUTS

- A recovered `GlobalState` (`RecoveryComplete`) or `RecoveryFault` (explicit,
  never silently "fixed").
- Durable `EffectReconciled { id, digest, outcome }` records (through MOD-11).
- Post-recovery invariant certifications consumed by MOD-17's M10 gate.

## DEPENDENCIES

- Module dependencies: MOD-11 (everything durable), MOD-10 (decode/digests),
  MOD-06 (state shapes to reconstruct), MOD-07 (queue + scheduler re-entry),
  MOD-04 (conservation revalidation), MOD-14 (independent oracle implementation).
- Consumers: MOD-17 (M10 evidence), MOD-15 (recovery differential), MOD-13
  (supervisor triggers reconciliation policy).
- Crate edges: production engine `ror-persistence`; independent engine
  `ror-reference` (no production deps — R-RECOV-04, REQ-TEST-045).
- Blocking open items: **U-15** (reconciliation outcome variants — `ReconciliationOutcome`
  is declared as a closed three-variant set at L26593–26597 per the registry
  correction; its admissibility per effect class remains open with U-06), **U-02**
  (snapshot decode depends on unfrozen machine-state encodings), **U-17** (queue
  authority), **U-06** (effect classes gate reconciliation behavior).

## INVARIANTS

- `Recover(D) = Replay(S, L, H)` (R-RECOV-01); uniqueness:
  `CommittedSnapshot + ValidWAL + ValidEffectJournal + ReconciledEffects ⇒
  UniqueRecoveredMachineState` (REQ-RECOV-022).
- The T0–T6 classification table above (R-RECOV-02) — normative, exact rows.
- Classification primitives (statements canonical in MOD-11): `Prepared ∧ ¬Issued ⇒
  Discard`; `Issued ∧ ¬Completed ⇒ Indeterminate`; applied here, never weakened
  (R-DUR-04 cross-reference).
- `Invalid(D) ⇒ RecoveryFault`; no silent repair (R-RECOV-05; canonical — central
  restatement R-CORE-10, D-07).
- `C_available + C_escrowed + C_consumed = C_initial` holds after recovery exactly as
  before the crash (R-RECOV-06).
- `Reconciled(E) ⇒ Issued(E)`; reconciliation is the only resolution path for
  Indeterminate (R-RECOV-07).

## REQUIREMENTS

Canonical text: `spec/01` S-19; addendum IV. All 8 obligations `SPECIFIED`.

| ID | Obligation (short) | Provenance (`Red-on-Rust.md`) | Verification |
|---|---|---|---|
| R-RECOV-01 | `D = ⟨S,L,H⟩`; Recover = Replay | L26122–26140 | recovery differential |
| R-RECOV-02 | Normative crash matrix T0–T6 (D-06 canonical) | L35159–35176, L28467–28493 | crash harness, M10 |
| R-RECOV-03 | Recovery algorithm (12 steps) | L35189–35208, L26272–26300 | recovery differential (R-REF-01) |
| R-RECOV-04 | Independent recovery implementation | L35189–35195, L38858–38890 | dependency review |
| R-RECOV-05 | Invalid(D) ⇒ RecoveryFault; never silently repair (D-07 canonical) | L35196–35208, L38254–38272 | negative corruption tests |
| R-RECOV-06 | Budget partition invariant survives crash | L35210–35215 | post-recovery invariant |
| R-RECOV-07 | Reconciliation is the only resolution path for Indeterminate | L35111–35144, L26249–26262 | reconciliation tests; U-15 |
| R-RECOV-08 | Reconciliation frozen: I2 holds on every host path incl. supervisor; never re-executes (idempotent query at most); compensations are ordinary gated requests; NotExecuted gated behind authoritative evidence; supervisor allocates lifecycle, not effects (C-89 resolved; M028) | addendum IV (SEC-010) | M028, T2/T3/T4 admissibility table |

Atomic registry records under this module: REQ-RECOV-001…022.
**8 obligations / 22 records.**

## SECURITY-BOUNDARY

Recovery is where the machine proves it means "recoverable": the guarantee to uphold
is **no silent corruption and no invented history**. Accepting a gap, a checksum
mismatch, a digest mismatch, or a duplicate runnable actor — and continuing — would
manufacture a false post-crash world; inferring `NotExecuted` from a missing
completion double-executes real-world effects. Both are loaded weapons, which is why
the mutations aimed here (M008, M015, M016, M017) target exactly these silent
failures, and why this module's engine must be *independent* code.

## VERIFICATION-OBLIGATIONS

- Tag: `RECOVERY-ISSUED-INDETERMINATE` (T2/T3/T4 ⇒ Indeterminate; never
  NotExecuted) — verifying module; classification statements cross-checked against
  MOD-11's R-DUR-04.
- Crash matrix execution: the M10 gate requires T0–T6 to produce the frozen expected
  classifications for randomized effect types (harness obligation R-TEST-08 owned by
  MOD-17, semantics here).
- Recovery differential: `Canonical(Recover_P(D)) = Canonical(Recover_R(D))` over the
  tested persistence state space — the third conjunct of final acceptance R-TEST-11
  (MOD-17), executed by MOD-15.
- Negative corruption tests (gaps, checksums, causality violations, duplicate
  runnable actors) must each yield `RecoveryFault` (R-RECOV-05).
- Post-recovery invariant certification (R-RECOV-06 with MOD-04/11).
- Milestone gates: M7 (recovery), M10 (classifications exact).

## SOURCE-PROVENANCE

- Frozen matrix + algorithm: [47] (L35159–35208); Phase 14 recovery contracts [33]
  (L26109–27484); 12-step list L35193–35204 vs 19-step list L34344–34364 (AMB-27);
  uniqueness theorem L34801–34812 (REQ-RECOV-022); independence statement [47]/
  master prompt §23 (L38653–38690); reconciliation outcome declaration
  L26593–26597.
- Canonical set: `spec/02` S-19; `req/01-registry-part5-persistence.md` (RECOV block).

## CROSS-REFERENCES

Owned here, binding elsewhere:

- R-RECOV-02 → MOD-11 (rows are projections of journal causality R-DUR-03/04),
  MOD-08 (T3/T4 depend on host-invocation semantics), MOD-17 (M10 gate consumes the
  matrix; harness obligation R-TEST-08 there).
- R-RECOV-03 steps → MOD-10 (decode), MOD-07 (queue reconstruction + scheduler
  re-entry), MOD-06 (actor invariants), MOD-04 (conservation revalidation).
- R-RECOV-04 → MOD-14 (independent recovery oracle in the reference model),
  MOD-17 (anti-oracle-collapse review).
- R-RECOV-07 → MOD-09 (authoritative host reconciliation protocol), MOD-11
  (`EffectReconciled` record kind), MOD-13 (supervisor policy trigger).

Owned elsewhere, binding RECOVERY: R-CORE-09/10 (MOD-01 central restatements —
D-06/D-07), R-PERSIST-02/05/06 (MOD-11 detection points that raise `RecoveryFault`
here), R-DUR-04/05 (MOD-11 classification and escrow statements this module applies),
R-HOST-03/04 (MOD-09 replay ordering underlies recovery replay), R-TEST-08/R-TEST-11
(MOD-17 harness + acceptance). Open items: U-15, U-06 (this module, blocking M7/M10),
U-17, U-02, AMB-09, AMB-27.
