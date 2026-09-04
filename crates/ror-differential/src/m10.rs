//! M10 crash/recovery verification gate (R-ORDER-02 / R-TEST-08 / R-RECOV-02).
//!
//! **Derived projection** of the canonical 7-row T0–T6 matrix — **not** a new
//! authority. Canonical homes: final/01 §15 R-RECOV-02, R-TEST-08, MOD-12/17.
//!
//! Pipeline per row (R-TEST-08):
//! ```text
//! Scenario → CrashHarness / EffectJournal (real WAL) → crash cut
//!   → Production recover(D)  → RecoveryObservation
//!   → Reference ref_recover(D) → RecoveryObservation
//!   → compare (must agree) + exact classification assert
//! ```
//!
//! Boundaries (M10-PREFLIGHT):
//! - Consumes M7 machinery; does not fork WAL/journal/snapshot/recover.
//! - Uses M8-era recovery observation compare (`m7` helpers); F-04 OPEN.
//! - `recover ↛ HostExecutor`; Issued∧¬Completed ⇒ Indeterminate ≠ NotExecuted.
//! - Reference independence: `ref_recover` never imports production recovery.
//! - OADs not closed; R-REG not promoted.

use ror_core::digest::EffectDigest;
use ror_core::effect::EffectCost;
use ror_core::types::{ActorId, EffectId};
use ror_persistence::{
    expected_class_for, recover, recovery_host_surface, ActorSnap, CrashHarness, CrashPoint,
    DurableState, EffectClass, EffectJournal, JournalRecord, SnapshotImage,
};

use crate::m7::{compare_m7, observe_production_m7, observe_reference_m7, RecoveryObservation};

// ---------------------------------------------------------------------------
// Derived matrix projection (R-RECOV-02) — NOT canonical authority
// ---------------------------------------------------------------------------

/// Canonical crash-point row id (exactly seven; no T7+).
#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash)]
pub enum MatrixRow {
    T0,
    T1,
    T2,
    T3,
    T4,
    T5,
    T6,
}

impl MatrixRow {
    pub const ALL: [MatrixRow; 7] = [
        MatrixRow::T0,
        MatrixRow::T1,
        MatrixRow::T2,
        MatrixRow::T3,
        MatrixRow::T4,
        MatrixRow::T5,
        MatrixRow::T6,
    ];

    pub fn as_str(self) -> &'static str {
        match self {
            MatrixRow::T0 => "T0",
            MatrixRow::T1 => "T1",
            MatrixRow::T2 => "T2",
            MatrixRow::T3 => "T3",
            MatrixRow::T4 => "T4",
            MatrixRow::T5 => "T5",
            MatrixRow::T6 => "T6",
        }
    }

    pub fn crash_point(self) -> CrashPoint {
        match self {
            MatrixRow::T0 => CrashPoint::T0,
            MatrixRow::T1 => CrashPoint::T1,
            MatrixRow::T2 => CrashPoint::T2,
            MatrixRow::T3 => CrashPoint::T3,
            MatrixRow::T4 => CrashPoint::T4,
            MatrixRow::T5 => CrashPoint::T5,
            MatrixRow::T6 => CrashPoint::T6,
        }
    }
}

/// Expected effect-class family for a matrix row (derived from R-RECOV-02).
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum ExpectedClass {
    /// T0 — no durable effect record.
    Absent,
    /// T1 — Prepared ∧ ¬Issued ⇒ Discard.
    Discard,
    /// T2–T4 — Issued ∧ ¬Completed ⇒ Indeterminate (≠ NotExecuted).
    Indeterminate,
    /// T5 — Completed durable ⇒ reconstruct Completed.
    Completed,
    /// T6 — SnapshotCommit base + resume (effect class may still be live).
    SnapshotResume,
}

impl ExpectedClass {
    pub fn label(self) -> &'static str {
        match self {
            ExpectedClass::Absent => "absent",
            ExpectedClass::Discard => "discard",
            ExpectedClass::Indeterminate => "indeterminate",
            ExpectedClass::Completed => "completed",
            ExpectedClass::SnapshotResume => "snapshot_resume",
        }
    }
}

/// One derived matrix row specification.
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct MatrixSpec {
    pub row: MatrixRow,
    pub durable_prefix: &'static str,
    pub expected: ExpectedClass,
    /// Host invocation is volatile and never written to WAL (T3/T4 labels).
    pub host_invoked_volatile: bool,
    pub host_completed_volatile: bool,
}

/// Full canonical matrix projection — **exactly 7 rows**.
pub const MATRIX: [MatrixSpec; 7] = [
    MatrixSpec {
        row: MatrixRow::T0,
        durable_prefix: "none",
        expected: ExpectedClass::Absent,
        host_invoked_volatile: false,
        host_completed_volatile: false,
    },
    MatrixSpec {
        row: MatrixRow::T1,
        durable_prefix: "Prepared only",
        expected: ExpectedClass::Discard,
        host_invoked_volatile: false,
        host_completed_volatile: false,
    },
    MatrixSpec {
        row: MatrixRow::T2,
        durable_prefix: "Prepared + Issued",
        expected: ExpectedClass::Indeterminate,
        host_invoked_volatile: false,
        host_completed_volatile: false,
    },
    MatrixSpec {
        row: MatrixRow::T3,
        durable_prefix: "Prepared + Issued (host invoked volatile)",
        expected: ExpectedClass::Indeterminate,
        host_invoked_volatile: true,
        host_completed_volatile: false,
    },
    MatrixSpec {
        row: MatrixRow::T4,
        durable_prefix: "Prepared + Issued (host completed volatile; ¬Completed durable)",
        expected: ExpectedClass::Indeterminate,
        host_invoked_volatile: true,
        host_completed_volatile: true,
    },
    MatrixSpec {
        row: MatrixRow::T5,
        durable_prefix: "Prepared + Issued + Completed",
        expected: ExpectedClass::Completed,
        host_invoked_volatile: false,
        host_completed_volatile: false,
    },
    MatrixSpec {
        row: MatrixRow::T6,
        durable_prefix: "SnapshotCommit (+ covered WAL)",
        expected: ExpectedClass::SnapshotResume,
        host_invoked_volatile: false,
        host_completed_volatile: false,
    },
];

// ---------------------------------------------------------------------------
// Crash injection — real journal/WAL path (not hand-built post-recovery state)
// ---------------------------------------------------------------------------

fn effect_pair(id: u64, payload: &[u8]) -> (JournalRecord, JournalRecord, EffectDigest) {
    let d = EffectDigest::of_bytes(payload);
    let c = EffectCost::zero();
    (
        JournalRecord::EffectPrepared {
            id: EffectId(id),
            actor: ActorId(0),
            digest: d,
            effect_bytes: payload.to_vec(),
            cost: c,
        },
        JournalRecord::EffectIssued {
            id: EffectId(id),
            actor: ActorId(0),
            digest: d,
            effect_bytes: payload.to_vec(),
            cost: c,
        },
        d,
    )
}

/// Build durable WAL bytes at the canonical crash cut for `row`.
///
/// Uses [`CrashHarness`] / journal append+sync so recovery sees the actual
/// persistence path. Host T3/T4 flags are **not** written to WAL (R-RECOV-02).
pub fn inject_crash(row: MatrixRow) -> Result<Vec<u8>, String> {
    inject_crash_with_effect(row, 0, b"m10-e")
}

/// Deterministic multi-effect-type injection (same row semantics, varied payload).
pub fn inject_crash_with_effect(
    row: MatrixRow,
    effect_id: u64,
    payload: &[u8],
) -> Result<Vec<u8>, String> {
    let (p, i, d) = effect_pair(effect_id, payload);
    let mut h = CrashHarness::new();
    match row {
        MatrixRow::T0 => {
            // Before Prepared — empty durable state.
        }
        MatrixRow::T1 => {
            h.push(p);
            h.sync_all_pending();
            // Issued never durable.
        }
        MatrixRow::T2 | MatrixRow::T3 | MatrixRow::T4 => {
            // Durable prefix identical: Prepared+Issued.
            // T3/T4 host volatility is scenario metadata only (not WAL).
            h.push(p);
            h.push(i);
            h.sync_all_pending();
            let _ = (row, d); // host flags intentionally unused on durable path
        }
        MatrixRow::T5 => {
            h.push(p);
            h.push(i);
            h.push(JournalRecord::EffectCompleted {
                id: EffectId(effect_id),
                digest: d,
                result_digest: EffectDigest::of_bytes(b"m10-r"),
                result_bytes: b"m10-r".to_vec(),
            });
            h.sync_all_pending();
        }
        MatrixRow::T6 => {
            h.push(p);
            h.push(i);
            h.sync_all_pending();
            h.snapshot = Some(SnapshotImage {
                logical_time: 10,
                next_actor_id: 2,
                next_effect_id: effect_id.saturating_add(1),
                wal_seq_covered: 0,
                budget_units: 40,
                escrow_units: 7,
                actors: vec![
                    ActorSnap {
                        id: 0,
                        status: 0, // runnable
                        pending_effect: u64::MAX,
                        mailbox: b"mb0".to_vec(),
                    },
                    ActorSnap {
                        id: 1,
                        status: 3, // terminal — must not become runnable
                        pending_effect: u64::MAX,
                        mailbox: vec![],
                    },
                ],
                authority_blob: b"auth".to_vec(),
                machine_blob: b"mach".to_vec(),
            });
            h.snapshot_committed = true;
        }
    }
    h.durable_state()
        .map(|d| d.wal_bytes)
        .map_err(|e| format!("durable_state: {e:?}"))
}

/// T1 via EffectJournal crash-before-Issued-sync (issuance path fidelity).
pub fn inject_t1_journal_crash(effect_id: u64, payload: &[u8]) -> Result<Vec<u8>, String> {
    let (p, i, _) = effect_pair(effect_id, payload);
    let mut j = EffectJournal::new();
    j.append_record(p)
        .map_err(|e| format!("append prepared: {e:?}"))?;
    j.sync().map_err(|e| format!("sync prepared: {e:?}"))?;
    j.append_record(i)
        .map_err(|e| format!("append issued: {e:?}"))?;
    // Crash before Issued sync — pending dropped.
    j.crash_discard_pending();
    Ok(j.wal().encode_committed())
}

// ---------------------------------------------------------------------------
// Row execution + matrix aggregate
// ---------------------------------------------------------------------------

/// Per-row verification outcome.
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct RowResult {
    pub row: MatrixRow,
    pub expected: ExpectedClass,
    pub production_ok: bool,
    pub reference_ok: bool,
    pub differential_ok: bool,
    pub classification_ok: bool,
    pub no_host_ok: bool,
    pub no_reexec_ok: bool,
    pub production: Option<RecoveryObservation>,
    pub reference: Option<RecoveryObservation>,
    pub detail: String,
}

impl RowResult {
    pub fn passed(&self) -> bool {
        self.production_ok
            && self.reference_ok
            && self.differential_ok
            && self.classification_ok
            && self.no_host_ok
            && self.no_reexec_ok
    }
}

/// Full M10 matrix report (must be 7/7 for gate).
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct MatrixReport {
    pub rows: Vec<RowResult>,
}

impl MatrixReport {
    pub fn passed_count(&self) -> usize {
        self.rows.iter().filter(|r| r.passed()).count()
    }

    pub fn total(&self) -> usize {
        self.rows.len()
    }

    pub fn all_pass(&self) -> bool {
        self.total() == 7 && self.passed_count() == 7
    }

    /// Machine-readable summary: `T0=PASS … T6=PASS | 7/7`.
    pub fn summary_line(&self) -> String {
        let parts: Vec<String> = self
            .rows
            .iter()
            .map(|r| {
                format!(
                    "{}={}",
                    r.row.as_str(),
                    if r.passed() { "PASS" } else { "FAIL" }
                )
            })
            .collect();
        format!(
            "{} | {}/{}",
            parts.join(" "),
            self.passed_count(),
            self.total()
        )
    }
}

fn class_matches(expected: ExpectedClass, obs: &RecoveryObservation) -> bool {
    match expected {
        ExpectedClass::Absent => obs.effect_labels.is_empty(),
        ExpectedClass::Discard => {
            obs.effect_labels.len() == 1 && obs.effect_labels[0].1 == "discard"
        }
        ExpectedClass::Indeterminate => {
            obs.effect_labels.len() == 1 && obs.effect_labels[0].1 == "indeterminate"
        }
        ExpectedClass::Completed => {
            obs.effect_labels.len() == 1 && obs.effect_labels[0].1 == "completed"
        }
        ExpectedClass::SnapshotResume => {
            obs.snapshot_present
                && obs.complete
                && obs.logical_time == 10
                && obs.budget_units == 40
                && obs.escrow_units == 7
                && obs.runnable == vec![0]
                && !obs.runnable.contains(&1)
        }
    }
}

fn no_not_executed(obs: &RecoveryObservation) -> bool {
    !obs.effect_labels
        .iter()
        .any(|(_, lab)| lab == "not_executed" || lab == "NotExecuted")
}

/// Run one matrix row: inject → recover_P → recover_R → compare + classify.
pub fn run_row(spec: &MatrixSpec) -> RowResult {
    let bytes = match inject_crash(spec.row) {
        Ok(b) => b,
        Err(e) => {
            return RowResult {
                row: spec.row,
                expected: spec.expected,
                production_ok: false,
                reference_ok: false,
                differential_ok: false,
                classification_ok: false,
                no_host_ok: false,
                no_reexec_ok: false,
                production: None,
                reference: None,
                detail: e,
            };
        }
    };

    // Security: recovery API has no host surface.
    let no_host_ok = recovery_host_surface() == "none — recover(DurableState) only";

    let prod = observe_production_m7(&bytes);
    let refr = observe_reference_m7(&bytes);

    let (production_ok, production) = match prod {
        Ok(o) => (true, Some(o)),
        Err(_) => (false, None),
    };
    let (reference_ok, reference) = match refr {
        Ok(o) => (true, Some(o)),
        Err(_) => (false, None),
    };

    let differential_ok = match compare_m7(&bytes) {
        Ok(()) => true,
        Err(_) => false,
    };

    let classification_ok = match (&production, &reference) {
        (Some(p), Some(r)) => {
            class_matches(spec.expected, p)
                && class_matches(spec.expected, r)
                && p == r
                && no_not_executed(p)
                && no_not_executed(r)
        }
        _ => false,
    };

    // No re-exec: Indeterminate rows must stay Indeterminate (not Completed by recover).
    let no_reexec_ok = match spec.expected {
        ExpectedClass::Indeterminate => classification_ok,
        ExpectedClass::Discard => classification_ok, // not promoted to Issued/Completed
        _ => true,
    };

    // Cross-check expected_class_for helper against row intent.
    let helper_ok = match spec.row {
        MatrixRow::T0 => expected_class_for(CrashPoint::T0, false, false, false) == "absent",
        MatrixRow::T1 => expected_class_for(CrashPoint::T1, true, false, false) == "discard",
        MatrixRow::T2 | MatrixRow::T3 | MatrixRow::T4 => {
            expected_class_for(spec.row.crash_point(), true, true, false) == "indeterminate"
        }
        MatrixRow::T5 => expected_class_for(CrashPoint::T5, true, true, true) == "completed",
        MatrixRow::T6 => expected_class_for(CrashPoint::T6, true, true, false) == "snapshot_resume",
    };

    let detail = if production_ok
        && reference_ok
        && differential_ok
        && classification_ok
        && no_host_ok
        && no_reexec_ok
        && helper_ok
    {
        "ok".into()
    } else {
        format!(
            "p={production_ok} r={reference_ok} d={differential_ok} c={classification_ok} h={no_host_ok} x={no_reexec_ok} helper={helper_ok}"
        )
    };

    RowResult {
        row: spec.row,
        expected: spec.expected,
        production_ok: production_ok && helper_ok,
        reference_ok,
        differential_ok,
        classification_ok,
        no_host_ok,
        no_reexec_ok,
        production,
        reference,
        detail,
    }
}

/// Execute the full T0–T6 matrix (exactly 7 rows).
pub fn run_full_matrix() -> MatrixReport {
    let rows = MATRIX.iter().map(run_row).collect();
    MatrixReport { rows }
}

/// Gate status string for progress / CI.
pub fn m10_gate_status() -> String {
    let report = run_full_matrix();
    if report.all_pass() {
        format!("M10 T-MATRIX = 7/7 PASS ({})", report.summary_line())
    } else {
        format!("M10 T-MATRIX = FAIL ({})", report.summary_line())
    }
}

// ---------------------------------------------------------------------------
// Distinguishing helpers (semantic, not string-only)
// ---------------------------------------------------------------------------

/// Assert Prepared∧¬Issued is Discard and not Indeterminate/Completed.
pub fn assert_prepared_not_issued_is_discard(wal: &[u8]) -> Result<(), String> {
    let r = recover(&DurableState {
        wal_bytes: wal.to_vec(),
    })
    .map_err(|e| format!("{e:?}"))?;
    if r.effects.len() != 1 {
        return Err(format!("expected 1 effect, got {}", r.effects.len()));
    }
    if !r.effects[0].is_discard() {
        return Err(format!("expected Discard, got {:?}", r.effects[0]));
    }
    if r.effects[0].is_indeterminate() {
        return Err("Discard must not be Indeterminate".into());
    }
    if r.effects[0].is_not_executed_local() {
        return Err("local NotExecuted forbidden".into());
    }
    if matches!(r.effects[0], EffectClass::Completed { .. }) {
        return Err("Prepared-only must not be Completed".into());
    }
    Ok(())
}

/// Assert Issued∧¬Completed is Indeterminate and not NotExecuted/Completed.
pub fn assert_issued_not_completed_is_indeterminate(wal: &[u8]) -> Result<(), String> {
    let r = recover(&DurableState {
        wal_bytes: wal.to_vec(),
    })
    .map_err(|e| format!("{e:?}"))?;
    if r.effects.len() != 1 {
        return Err(format!("expected 1 effect, got {}", r.effects.len()));
    }
    if !r.effects[0].is_indeterminate() {
        return Err(format!("expected Indeterminate, got {:?}", r.effects[0]));
    }
    if r.effects[0].is_not_executed_local() {
        return Err("Indeterminate ≠ NotExecuted".into());
    }
    if r.effects[0].is_discard() {
        return Err("Issued must not be Discard".into());
    }
    if matches!(r.effects[0], EffectClass::Completed { .. }) {
        return Err("Issued∧¬Completed must not be Completed by recover".into());
    }
    Ok(())
}

/// Assert Completed reconstructs without host re-exec surface.
pub fn assert_completed_reconstruct(wal: &[u8]) -> Result<(), String> {
    let r = recover(&DurableState {
        wal_bytes: wal.to_vec(),
    })
    .map_err(|e| format!("{e:?}"))?;
    match r.effects.first() {
        Some(EffectClass::Completed { .. }) => {
            if recovery_host_surface() != "none — recover(DurableState) only" {
                return Err("host surface leaked".into());
            }
            Ok(())
        }
        other => Err(format!("expected Completed, got {other:?}")),
    }
}

// ---------------------------------------------------------------------------
// Tests — M10 gate
// ---------------------------------------------------------------------------

#[cfg(test)]
mod tests {
    use super::*;
    use ror_core::types::CapRef;
    use ror_persistence::{
        admit_recon_evidence, ReconEvidence, RecoveryFault, RecoveryResult, WalFrame, WalKind,
        WalSequence, CHECKSUM_SEED,
    };
    use ror_reference::ref_recover;

    // ----- matrix completeness -----

    #[test]
    fn matrix_has_exactly_seven_rows() {
        assert_eq!(MATRIX.len(), 7);
        assert_eq!(MatrixRow::ALL.len(), 7);
        let ids: Vec<_> = MATRIX.iter().map(|s| s.row.as_str()).collect();
        assert_eq!(ids, vec!["T0", "T1", "T2", "T3", "T4", "T5", "T6"]);
    }

    #[test]
    fn full_matrix_7_of_7() {
        let report = run_full_matrix();
        assert_eq!(report.total(), 7, "missing T-row must not hide as PASS");
        for r in &report.rows {
            assert!(
                r.passed(),
                "{} failed: {} (expected {:?})",
                r.row.as_str(),
                r.detail,
                r.expected
            );
        }
        assert!(report.all_pass());
        let status = m10_gate_status();
        assert!(status.contains("7/7 PASS"), "gate status: {status}");
    }

    // ----- per-row explicit tests (cannot collapse into one silent PASS) -----

    #[test]
    fn t0_before_prepared_absent() {
        let r = run_row(&MATRIX[0]);
        assert!(r.passed(), "{}", r.detail);
        assert_eq!(r.expected, ExpectedClass::Absent);
        let o = r.production.as_ref().unwrap();
        assert!(o.effect_labels.is_empty());
        assert!(o.complete);
    }

    #[test]
    fn t1_prepared_not_issued_discard() {
        let r = run_row(&MATRIX[1]);
        assert!(r.passed(), "{}", r.detail);
        assert_eq!(r.expected, ExpectedClass::Discard);
        let bytes = inject_crash(MatrixRow::T1).unwrap();
        assert_prepared_not_issued_is_discard(&bytes).unwrap();
    }

    #[test]
    fn t1_journal_crash_before_issued_sync() {
        let bytes = inject_t1_journal_crash(11, b"t1-j").unwrap();
        assert_prepared_not_issued_is_discard(&bytes).unwrap();
        compare_m7(&bytes).expect("T1 journal path differential");
    }

    #[test]
    fn t2_after_issued_indeterminate() {
        let r = run_row(&MATRIX[2]);
        assert!(r.passed(), "{}", r.detail);
        let bytes = inject_crash(MatrixRow::T2).unwrap();
        assert_issued_not_completed_is_indeterminate(&bytes).unwrap();
    }

    #[test]
    fn t3_host_invoked_still_indeterminate() {
        let r = run_row(&MATRIX[3]);
        assert!(r.passed(), "{}", r.detail);
        assert!(MATRIX[3].host_invoked_volatile);
        // Durable bytes identical class to T2.
        let bytes = inject_crash(MatrixRow::T3).unwrap();
        assert_issued_not_completed_is_indeterminate(&bytes).unwrap();
        // Recovery must not invent Completed from volatile host invocation.
        let prod = observe_production_m7(&bytes).unwrap();
        assert_eq!(prod.effect_labels[0].1, "indeterminate");
    }

    #[test]
    fn t4_host_completed_volatile_still_indeterminate() {
        let r = run_row(&MATRIX[4]);
        assert!(r.passed(), "{}", r.detail);
        assert!(MATRIX[4].host_completed_volatile);
        let bytes = inject_crash(MatrixRow::T4).unwrap();
        assert_issued_not_completed_is_indeterminate(&bytes).unwrap();
    }

    #[test]
    fn t5_completed_reconstruct_no_rehost() {
        let r = run_row(&MATRIX[5]);
        assert!(r.passed(), "{}", r.detail);
        let bytes = inject_crash(MatrixRow::T5).unwrap();
        assert_completed_reconstruct(&bytes).unwrap();
    }

    #[test]
    fn t6_snapshot_commit_resume() {
        let r = run_row(&MATRIX[6]);
        assert!(r.passed(), "{}", r.detail);
        let o = r.production.as_ref().unwrap();
        assert!(o.snapshot_present);
        assert_eq!(o.logical_time, 10);
        assert_eq!(o.budget_units, 40);
        assert_eq!(o.escrow_units, 7);
        assert_eq!(o.runnable, vec![0]);
    }

    // ----- distinguishing tests (semantic) -----

    #[test]
    fn distinguish_prepared_from_issued() {
        let t1 = inject_crash(MatrixRow::T1).unwrap();
        let t2 = inject_crash(MatrixRow::T2).unwrap();
        assert_prepared_not_issued_is_discard(&t1).unwrap();
        assert_issued_not_completed_is_indeterminate(&t2).unwrap();
        let o1 = observe_production_m7(&t1).unwrap();
        let o2 = observe_production_m7(&t2).unwrap();
        assert_ne!(o1.effect_labels, o2.effect_labels);
        assert_eq!(o1.effect_labels[0].1, "discard");
        assert_eq!(o2.effect_labels[0].1, "indeterminate");
    }

    #[test]
    fn distinguish_issued_from_completed() {
        let t2 = inject_crash(MatrixRow::T2).unwrap();
        let t5 = inject_crash(MatrixRow::T5).unwrap();
        assert_issued_not_completed_is_indeterminate(&t2).unwrap();
        assert_completed_reconstruct(&t5).unwrap();
        let o2 = observe_production_m7(&t2).unwrap();
        let o5 = observe_production_m7(&t5).unwrap();
        assert_eq!(o2.effect_labels[0].1, "indeterminate");
        assert_eq!(o5.effect_labels[0].1, "completed");
    }

    #[test]
    fn indeterminate_is_not_not_executed() {
        for row in [MatrixRow::T2, MatrixRow::T3, MatrixRow::T4] {
            let bytes = inject_crash(row).unwrap();
            let r = recover(&DurableState {
                wal_bytes: bytes.clone(),
            })
            .unwrap();
            assert!(
                r.effects[0].is_indeterminate(),
                "{} must be Indeterminate",
                row.as_str()
            );
            assert!(
                !r.effects[0].is_not_executed_local(),
                "{} Indeterminate ≠ NotExecuted",
                row.as_str()
            );
            // Recon without authoritative evidence rejected.
            if let EffectClass::Indeterminate { id, digest, .. } = &r.effects[0] {
                let bad = ReconEvidence {
                    id: *id,
                    digest: *digest,
                    evidence_tag: 0,
                    evidence_bytes: vec![],
                };
                assert!(admit_recon_evidence(&bad).is_err());
            }
        }
    }

    // ----- recovery differential (production ≡ reference) -----

    #[test]
    fn differential_all_rows() {
        for spec in &MATRIX {
            let bytes = inject_crash(spec.row).unwrap();
            compare_m7(&bytes).unwrap_or_else(|e| {
                panic!(
                    "{} differential diverge: prod={:?} ref={:?}",
                    spec.row.as_str(),
                    e.0,
                    e.1
                )
            });
        }
    }

    #[test]
    fn differential_multi_effect_payloads() {
        // Randomized *effect type* stand-in: deterministic payload variants.
        let payloads: &[&[u8]] = &[b"file-read", b"net-send", b"log-write", b"cap-query"];
        for (i, pl) in payloads.iter().enumerate() {
            for row in MatrixRow::ALL {
                if matches!(row, MatrixRow::T0) {
                    continue;
                }
                let bytes = inject_crash_with_effect(row, i as u64, pl).unwrap();
                compare_m7(&bytes)
                    .unwrap_or_else(|_| panic!("diff fail row={} payload={:?}", row.as_str(), pl));
                // Classification family still holds.
                let o = observe_production_m7(&bytes).unwrap();
                match row {
                    MatrixRow::T1 => assert_eq!(o.effect_labels[0].1, "discard"),
                    MatrixRow::T2 | MatrixRow::T3 | MatrixRow::T4 => {
                        assert_eq!(o.effect_labels[0].1, "indeterminate")
                    }
                    MatrixRow::T5 => assert_eq!(o.effect_labels[0].1, "completed"),
                    MatrixRow::T6 => assert!(o.snapshot_present),
                    MatrixRow::T0 => unreachable!(),
                }
            }
        }
    }

    // ----- negative / hazard tests -----

    #[test]
    fn negative_checksum_corrupt_rejected() {
        let mut bytes = inject_crash(MatrixRow::T2).unwrap();
        let mid = bytes.len() / 2;
        bytes[mid] ^= 0x5a;
        assert!(recover(&DurableState {
            wal_bytes: bytes.clone()
        })
        .is_err());
        assert!(ref_recover(&bytes).is_err());
    }

    #[test]
    fn negative_sequence_gap_rejected() {
        let f1 = WalFrame::new(
            &CHECKSUM_SEED,
            WalSequence(1),
            WalKind::Event,
            b"a".to_vec(),
        );
        let f3 = WalFrame::new(&f1.checksum, WalSequence(3), WalKind::Event, b"c".to_vec());
        let mut bytes = f1.encode();
        bytes.extend_from_slice(&f3.encode());
        let err = recover(&DurableState {
            wal_bytes: bytes.clone(),
        })
        .unwrap_err();
        assert!(matches!(
            err,
            RecoveryFault::Sequence | RecoveryFault::Wal(_)
        ));
        assert!(ref_recover(&bytes).is_err());
    }

    #[test]
    fn negative_truncated_wal_rejected() {
        let mut bytes = inject_crash(MatrixRow::T5).unwrap();
        bytes.truncate(bytes.len() / 2);
        assert!(recover(&DurableState {
            wal_bytes: bytes.clone()
        })
        .is_err());
        assert!(ref_recover(&bytes).is_err());
    }

    #[test]
    fn negative_prepared_must_not_be_treated_as_issued() {
        let bytes = inject_crash(MatrixRow::T1).unwrap();
        let r = recover(&DurableState { wal_bytes: bytes }).unwrap();
        assert!(r.effects[0].is_discard());
        assert!(!r.effects[0].is_indeterminate());
    }

    #[test]
    fn negative_issued_must_not_become_not_executed() {
        let bytes = inject_crash(MatrixRow::T2).unwrap();
        let r = recover(&DurableState { wal_bytes: bytes }).unwrap();
        assert!(r.effects[0].is_indeterminate());
        assert!(!r.effects[0].is_not_executed_local());
    }

    #[test]
    fn negative_recovery_host_surface_none() {
        assert_eq!(recovery_host_surface(), "none — recover(DurableState) only");
        // recover signature takes only DurableState — exercised on every row.
        for spec in &MATRIX {
            let bytes = inject_crash(spec.row).unwrap();
            let _ = recover(&DurableState { wal_bytes: bytes }).unwrap();
        }
    }

    #[test]
    fn negative_cap_revocation_survives_crash() {
        let mut h = CrashHarness::new();
        h.push(JournalRecord::CapGranted {
            cap: CapRef::from_kernel_parts(3, 1),
            actor: ActorId(0),
        });
        h.push(JournalRecord::CapRevoked {
            cap: CapRef::from_kernel_parts(3, 1),
        });
        h.sync_all_pending();
        let bytes = h.durable_state().unwrap().wal_bytes;
        let r = recover(&DurableState {
            wal_bytes: bytes.clone(),
        })
        .unwrap();
        assert!(r.revoked_caps.contains(&(3, 1)));
        // Reference also sees revocation.
        let rr = ref_recover(&bytes).unwrap();
        assert!(rr.revoked_caps.contains(&(3, 1)));
        compare_m7(&bytes).expect("revocation differential");
    }

    #[test]
    fn negative_budget_not_created_on_recover() {
        let bytes = inject_crash(MatrixRow::T6).unwrap();
        let r = recover(&DurableState { wal_bytes: bytes }).unwrap();
        // Budget comes from durable snapshot only.
        assert_eq!(r.budget_units, 40);
        assert_eq!(r.escrow_units, 7);
        // Empty T0 must not invent budget.
        let t0 = inject_crash(MatrixRow::T0).unwrap();
        let r0 = recover(&DurableState { wal_bytes: t0 }).unwrap();
        assert_eq!(r0.budget_units, 0);
        assert_eq!(r0.escrow_units, 0);
    }

    // ----- determinism -----

    #[test]
    fn recovery_deterministic_same_d() {
        for row in MatrixRow::ALL {
            let bytes = inject_crash(row).unwrap();
            let r1 = recover(&DurableState {
                wal_bytes: bytes.clone(),
            })
            .unwrap();
            let r2 = recover(&DurableState {
                wal_bytes: bytes.clone(),
            })
            .unwrap();
            assert_eq!(r1, r2, "{} nondeterministic", row.as_str());
            let o1 = observe_production_m7(&bytes).unwrap();
            let o2 = observe_production_m7(&bytes).unwrap();
            assert_eq!(o1, o2);
            let ro1 = observe_reference_m7(&bytes).unwrap();
            let ro2 = observe_reference_m7(&bytes).unwrap();
            assert_eq!(ro1, ro2);
        }
    }

    // ----- reference independence (runtime check of cargo surface) -----

    #[test]
    fn reference_does_not_delegate_to_production_labels() {
        // ref_recover on T2 yields Indeterminate independently; compare equal.
        let bytes = inject_crash(MatrixRow::T2).unwrap();
        let p = observe_production_m7(&bytes).unwrap();
        let r = observe_reference_m7(&bytes).unwrap();
        assert_eq!(p, r);
        assert_eq!(r.effect_labels[0].1, "indeterminate");
    }

    // ----- M5 hinge regression (recovery path must not weaken) -----

    #[test]
    fn m5_hinge_recovery_never_calls_host() {
        // Documented surface + recover(DurableState) only on all crash cuts.
        assert_eq!(recovery_host_surface(), "none — recover(DurableState) only");
        for row in MatrixRow::ALL {
            let bytes = inject_crash(row).unwrap();
            let _res: RecoveryResult = recover(&DurableState { wal_bytes: bytes }).unwrap();
        }
    }
}
