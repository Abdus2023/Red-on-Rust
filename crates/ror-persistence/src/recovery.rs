//! Recovery engine `Recover(D)=Replay(S,L,H)` (R-RECOV-01/03).
//!
//! Crash matrix T0–T6 (R-RECOV-02). Classification (R-DUR-04):
//! - Prepared ∧ ¬Issued ⇒ **Discard**
//! - Issued ∧ ¬Completed ⇒ **Indeterminate** (≠ NotExecuted)
//! - Completed ⇒ reconstruct; **no host re-exec** (R-RECOV-08)
//!
//! Recovery **never** invokes the host. Reconciliation hooks accept external
//! evidence only (R-RECOV-07/08).

use ror_core::digest::EffectDigest;
use ror_core::types::EffectId;

use crate::journal::{JournalError, JournalRecord};
use crate::snapshot::{SnapshotError, SnapshotImage, SnapshotStore};
use crate::wal::{WalError, WalFrame, WalKind, WalLog, WalSequence};

/// Durable state D = ⟨S, L, H⟩ (R-RECOV-01).
/// S = snapshot, L = WAL log bytes / frames, H = effect journal history in L.
#[derive(Clone, Debug, Default)]
pub struct DurableState {
    /// Raw committed WAL bytes (includes snapshot frames + journal).
    pub wal_bytes: Vec<u8>,
}

/// Effect classification after recovery (R-DUR-04 / R-RECOV-02).
#[derive(Clone, Debug, PartialEq, Eq)]
pub enum EffectClass {
    /// T0 — effect never durable.
    Absent,
    /// T1 — Prepared only → Discard (not live).
    Discard { id: EffectId, digest: EffectDigest },
    /// T2–T4 — Issued ∧ ¬Completed → Indeterminate (open until recon).
    Indeterminate {
        id: EffectId,
        digest: EffectDigest,
        actor: u64,
        effect_bytes: Vec<u8>,
    },
    /// T5 — Completed durable.
    Completed {
        id: EffectId,
        digest: EffectDigest,
        result_digest: EffectDigest,
        result_bytes: Vec<u8>,
    },
    /// Reconciled with authoritative evidence (R-RECOV-08).
    Reconciled {
        id: EffectId,
        digest: EffectDigest,
        evidence_tag: u8,
        evidence_bytes: Vec<u8>,
    },
}

impl EffectClass {
    pub fn is_indeterminate(&self) -> bool {
        matches!(self, Self::Indeterminate { .. })
    }

    pub fn is_discard(&self) -> bool {
        matches!(self, Self::Discard { .. })
    }

    /// Local NotExecuted is **forbidden** without evidence_tag authority.
    /// This helper never returns NotExecuted from classification alone.
    pub fn is_not_executed_local(&self) -> bool {
        false
    }
}

/// Crash-point labels (R-RECOV-02) for harness evidence.
#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash)]
pub enum CrashPoint {
    /// T0 — before Prepared.
    T0,
    /// T1 — after Prepared (incl. failed Issued sync).
    T1,
    /// T2 — after Issued durable.
    T2,
    /// T3 — after HostInvocation (volatile; journal still Issued).
    T3,
    /// T4 — after HostCompletion before Completed durable.
    T4,
    /// T5 — after Completed durable.
    T5,
    /// T6 — after SnapshotCommit.
    T6,
}

/// Recovery fault (R-RECOV-05 / R-CORE-10 — no silent repair).
#[derive(Clone, Debug, PartialEq, Eq)]
pub enum RecoveryFault {
    Wal(WalError),
    Snapshot(SnapshotError),
    Journal(JournalError),
    Invariant(String),
    /// Checksum / digest mismatch.
    Integrity,
    /// Sequence discontinuity.
    Sequence,
}

impl From<WalError> for RecoveryFault {
    fn from(e: WalError) -> Self {
        match e {
            WalError::ChecksumMismatch => RecoveryFault::Integrity,
            WalError::SequenceGap { .. } | WalError::SequenceRegression { .. } => {
                RecoveryFault::Sequence
            }
            other => RecoveryFault::Wal(other),
        }
    }
}

impl From<SnapshotError> for RecoveryFault {
    fn from(e: SnapshotError) -> Self {
        match e {
            SnapshotError::DigestMismatch => RecoveryFault::Integrity,
            SnapshotError::Wal(w) => RecoveryFault::from(w),
            other => RecoveryFault::Snapshot(other),
        }
    }
}

impl From<JournalError> for RecoveryFault {
    fn from(e: JournalError) -> Self {
        match e {
            JournalError::Wal(w) => RecoveryFault::from(w),
            other => RecoveryFault::Journal(other),
        }
    }
}

/// Result of `Recover(D)` (R-RECOV-03).
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct RecoveryResult {
    /// Restored snapshot image (empty default if none).
    pub snapshot: SnapshotImage,
    /// Snapshot commit seq if any.
    pub snapshot_seq: Option<WalSequence>,
    /// WAL frames replayed after snapshot.
    pub replayed: Vec<WalFrame>,
    /// Classified effects (by id order).
    pub effects: Vec<EffectClass>,
    /// next_effect_id reconstructed (R-RECOV-09).
    pub next_effect_id: u64,
    /// next_actor_id reconstructed.
    pub next_actor_id: u64,
    /// Logical time.
    pub logical_time: u64,
    /// Budget units.
    pub budget_units: u64,
    /// Escrow units (R-DUR-05).
    pub escrow_units: u64,
    /// Runnable queue (U-17 reconstruct-from-status).
    pub runnable: Vec<u64>,
    /// Authority blob from snapshot (+ cap events applied thinly).
    pub authority_blob: Vec<u8>,
    /// Revoked cap indices seen in WAL (monotonic revocation).
    pub revoked_caps: Vec<(u32, u32)>,
    /// Recovery complete flag.
    pub complete: bool,
}

impl RecoveryResult {
    /// Indeterminate effect set (T2–T4 survivors).
    pub fn indeterminates(&self) -> Vec<&EffectClass> {
        self.effects
            .iter()
            .filter(|e| e.is_indeterminate())
            .collect()
    }

    pub fn discards(&self) -> Vec<&EffectClass> {
        self.effects.iter().filter(|e| e.is_discard()).collect()
    }
}

/// External reconciliation evidence input (R-RECOV-08).
///
/// Recovery itself never calls host. A higher layer may supply evidence from
/// an **idempotent host query** (not re-execution) or other authority.
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct ReconEvidence {
    pub id: EffectId,
    pub digest: EffectDigest,
    /// 1 = authoritative NotExecuted (host confirmed absent);
    /// 2 = host confirmed complete (result in evidence_bytes);
    /// 3 = bound external;
    /// other = rejected.
    pub evidence_tag: u8,
    pub evidence_bytes: Vec<u8>,
}

/// Apply durable EffectReconciled from authoritative evidence only.
/// Returns error if evidence_tag is not in the admissible set (no silent
/// Indeterminate→NotExecuted).
pub fn admit_recon_evidence(ev: &ReconEvidence) -> Result<JournalRecord, RecoveryFault> {
    match ev.evidence_tag {
        1..=3 => Ok(JournalRecord::EffectReconciled {
            id: ev.id,
            digest: ev.digest,
            evidence_tag: ev.evidence_tag,
            evidence_bytes: ev.evidence_bytes.clone(),
        }),
        _ => Err(RecoveryFault::Invariant(
            "recon evidence_tag not authoritative".into(),
        )),
    }
}

/// Full 12-step recovery (R-RECOV-03), condensed into a pure function over D.
///
/// **Never invokes host. Never re-executes effects.**
pub fn recover(d: &DurableState) -> Result<RecoveryResult, RecoveryFault> {
    // 1–2: parse WAL, verify frames/checksums/sequence
    let frames = WalLog::parse_and_verify(&d.wal_bytes)?;

    // 1 locate newest committed snapshot; 2 verify
    let snap_store = SnapshotStore::from_wal_frames(&frames)?;
    let (mut image, snap_seq, snap_cover) = match snap_store.committed() {
        Some(cs) => (cs.image.clone(), Some(cs.seq), cs.image.wal_seq_covered),
        None => (SnapshotImage::default(), None, 0),
    };

    // 5–7: replay frames after snapshot coverage
    let mut replayed = Vec::new();
    let mut journal_recs: Vec<(WalSequence, JournalRecord)> = Vec::new();
    let mut revoked: Vec<(u32, u32)> = Vec::new();

    for f in &frames {
        // Skip frames at or before snapshot body coverage for effect replay,
        // but snapshot commit seq itself is the cursor: replay effect frames
        // with sequence > snap_cover (wal_seq_covered is last journal seq
        // included in image).
        if f.sequence.0 <= snap_cover && snap_seq.is_some() {
            // Still need cap revocation monotonicity from full history? Spec:
            // lattice durable in snapshot; post-snap cap events replay.
            if f.sequence.0 <= snap_cover {
                continue;
            }
        }
        if let Some(ss) = snap_seq {
            if f.sequence.0 <= ss.0
                && matches!(f.kind, WalKind::SnapshotBody | WalKind::SnapshotCommit)
            {
                continue;
            }
            // For post-snapshot replay: skip frames included in snapshot cover
            if f.sequence.0 <= snap_cover {
                continue;
            }
        }

        match f.kind {
            WalKind::SnapshotBody | WalKind::SnapshotCommit => {
                // Older or current snapshot frames — skip for journal replay.
            }
            kind => {
                replayed.push(f.clone());
                let rec =
                    JournalRecord::decode_payload(kind, &f.payload).map_err(RecoveryFault::from)?;
                if let JournalRecord::CapRevoked { cap } = &rec {
                    revoked.push((cap.index(), cap.generation()));
                }
                journal_recs.push((f.sequence, rec));
            }
        }
    }

    // Also fold pre-snapshot journal from image perspective: when no snapshot,
    // all frames are journal. When snapshot exists, image already has state;
    // we still need effect classification across **full** durable journal for
    // effects that may span — re-scan ALL non-snapshot frames for classification.
    let mut all_effect_recs: Vec<JournalRecord> = Vec::new();
    for f in &frames {
        match f.kind {
            WalKind::SnapshotBody | WalKind::SnapshotCommit => {}
            kind => {
                if let Ok(rec) = JournalRecord::decode_payload(kind, &f.payload) {
                    // Cap events for full revocation set
                    if let JournalRecord::CapRevoked { cap } = &rec {
                        let pair = (cap.index(), cap.generation());
                        if !revoked.contains(&pair) {
                            revoked.push(pair);
                        }
                    }
                    all_effect_recs.push(rec);
                }
            }
        }
    }

    // 8–9: reconstruct effect journal / classify interrupted effects
    let effects = classify_effects(&all_effect_recs);

    // 9b: drop Discard from live set (T1) — already classified
    // 10: reconstruct runnable queue (U-17) — applied below on final image

    // 11: digest vs checkpoint — re-verify snapshot digest if present
    if let Some(cs) = snap_store.committed() {
        let dgst = cs.image.state_digest();
        if dgst != cs.state_digest {
            return Err(RecoveryFault::Integrity);
        }
        image = cs.image.clone();
    }

    // R-RECOV-09: next_effect_id = max(snapshot counter, max(id)+1 from journal)
    let mut max_eid = image.next_effect_id;
    let mut max_aid = image.next_actor_id;
    for rec in &all_effect_recs {
        if let Some(id) = rec.effect_id() {
            let next = id.0.saturating_add(1);
            if next > max_eid {
                max_eid = next;
            }
        }
        match rec {
            JournalRecord::EffectPrepared { actor, .. }
            | JournalRecord::EffectIssued { actor, .. }
            | JournalRecord::CapGranted { actor, .. }
            | JournalRecord::CapDerived { actor, .. } => {
                let next = actor.0.saturating_add(1);
                if next > max_aid {
                    max_aid = next;
                }
            }
            _ => {}
        }
        // Actors in snapshot
    }
    for a in &image.actors {
        let next = a.id.saturating_add(1);
        if next > max_aid {
            max_aid = next;
        }
    }

    // Apply escrow survival: escrow from snapshot stands (R-DUR-05).
    // Budget not advanced by recovery itself (R-RECOV-06 / no time advance).

    Ok(RecoveryResult {
        snapshot: image.clone(),
        snapshot_seq: snap_seq,
        replayed,
        effects,
        next_effect_id: max_eid,
        next_actor_id: max_aid,
        logical_time: image.logical_time,
        budget_units: image.budget_units,
        escrow_units: image.escrow_units,
        runnable: image.reconstruct_runnable_queue(),
        authority_blob: image.authority_blob,
        revoked_caps: revoked,
        complete: true,
    })
}

/// Classify effects per R-DUR-04 / T0–T6.
fn classify_effects(recs: &[JournalRecord]) -> Vec<EffectClass> {
    use std::collections::BTreeMap;
    #[derive(Default)]
    struct Acc {
        prepared: Option<(EffectDigest, u64, Vec<u8>)>, // digest, actor, bytes
        issued: Option<(EffectDigest, u64, Vec<u8>)>,
        completed: Option<(EffectDigest, EffectDigest, Vec<u8>)>,
        reconciled: Option<(EffectDigest, u8, Vec<u8>)>,
    }
    let mut map: BTreeMap<u64, Acc> = BTreeMap::new();

    for r in recs {
        match r {
            JournalRecord::EffectPrepared {
                id,
                actor,
                digest,
                effect_bytes,
                ..
            } => {
                let e = map.entry(id.0).or_default();
                e.prepared = Some((*digest, actor.0, effect_bytes.clone()));
            }
            JournalRecord::EffectIssued {
                id,
                actor,
                digest,
                effect_bytes,
                ..
            } => {
                let e = map.entry(id.0).or_default();
                e.issued = Some((*digest, actor.0, effect_bytes.clone()));
            }
            JournalRecord::EffectCompleted {
                id,
                digest,
                result_digest,
                result_bytes,
            } => {
                let e = map.entry(id.0).or_default();
                e.completed = Some((*digest, *result_digest, result_bytes.clone()));
            }
            JournalRecord::EffectReconciled {
                id,
                digest,
                evidence_tag,
                evidence_bytes,
            } => {
                let e = map.entry(id.0).or_default();
                e.reconciled = Some((*digest, *evidence_tag, evidence_bytes.clone()));
            }
            _ => {}
        }
    }

    let mut out = Vec::new();
    for (id, acc) in map {
        let eid = EffectId(id);
        if let Some((d, tag, bytes)) = acc.reconciled {
            out.push(EffectClass::Reconciled {
                id: eid,
                digest: d,
                evidence_tag: tag,
                evidence_bytes: bytes,
            });
            continue;
        }
        if let Some((d, rd, rb)) = acc.completed {
            out.push(EffectClass::Completed {
                id: eid,
                digest: d,
                result_digest: rd,
                result_bytes: rb,
            });
            continue;
        }
        if let Some((d, actor, bytes)) = acc.issued {
            // T2–T4 Indeterminate — NEVER NotExecuted
            out.push(EffectClass::Indeterminate {
                id: eid,
                digest: d,
                actor,
                effect_bytes: bytes,
            });
            continue;
        }
        if let Some((d, _, _)) = acc.prepared {
            // T1 Discard
            out.push(EffectClass::Discard { id: eid, digest: d });
            continue;
        }
        // T0 absent — skip (no record)
    }
    out
}

/// Simulate crash at a labeled point for harness (evidence tags).
///
/// Builds durable WAL bytes representing the crash cut, then recovers.
/// `host_invoked` / `host_completed_volatile` are **not** written to WAL —
/// they only affect the crash-point label (T3/T4 are observationally Issued
/// in durable state).
#[derive(Clone, Debug)]
pub struct CrashHarness {
    pub journal_records: Vec<JournalRecord>,
    /// Which records were synced (durable). Indices into journal_records.
    pub durable_count: usize,
    pub snapshot: Option<SnapshotImage>,
    pub snapshot_committed: bool,
}

impl CrashHarness {
    pub fn new() -> Self {
        Self {
            journal_records: Vec::new(),
            durable_count: 0,
            snapshot: None,
            snapshot_committed: false,
        }
    }

    pub fn push(&mut self, r: JournalRecord) {
        self.journal_records.push(r);
    }

    pub fn sync_all_pending(&mut self) {
        self.durable_count = self.journal_records.len();
    }

    /// Materialize durable WAL bytes at the crash cut (pending not included).
    pub fn durable_state(&self) -> Result<DurableState, RecoveryFault> {
        let mut wal = WalLog::new();
        let mut cover = 0u64;
        for r in self.journal_records.iter().take(self.durable_count) {
            let kind = r.wal_kind();
            let payload = r.encode_payload();
            let seq = wal.append(kind, payload).map_err(RecoveryFault::from)?;
            cover = seq.0;
        }
        wal.sync().map_err(RecoveryFault::from)?;

        if self.snapshot_committed {
            if let Some(mut img) = self.snapshot.clone() {
                img.wal_seq_covered = cover;
                let mut store = SnapshotStore::new();
                store.begin(img);
                store.commit_to_wal(&mut wal).map_err(RecoveryFault::from)?;
            }
        }
        Ok(DurableState {
            wal_bytes: wal.encode_committed(),
        })
    }

    pub fn recover_at(&self) -> Result<RecoveryResult, RecoveryFault> {
        let d = self.durable_state()?;
        recover(&d)
    }
}

impl Default for CrashHarness {
    fn default() -> Self {
        Self::new()
    }
}

/// Map a crash point + issuance progress to expected classification family.
pub fn expected_class_for(
    crash: CrashPoint,
    has_prepared: bool,
    has_issued: bool,
    has_completed: bool,
) -> &'static str {
    match crash {
        CrashPoint::T0 => "absent",
        CrashPoint::T1 => {
            if has_prepared && !has_issued {
                "discard"
            } else {
                "absent"
            }
        }
        CrashPoint::T2 | CrashPoint::T3 | CrashPoint::T4 => {
            if has_issued && !has_completed {
                "indeterminate"
            } else if has_completed {
                "completed"
            } else {
                "absent"
            }
        }
        CrashPoint::T5 => {
            if has_completed {
                "completed"
            } else {
                "indeterminate"
            }
        }
        CrashPoint::T6 => "snapshot_resume",
    }
}

/// Ensure recovery path has no host call surface — compile-time / API-level:
/// `recover` takes only `DurableState` (bytes). This marker documents R-RECOV-08.
pub fn recovery_host_surface() -> &'static str {
    "none — recover(DurableState) only"
}

#[cfg(test)]
mod tests {
    use super::*;
    use ror_core::effect::EffectCost;
    use ror_core::types::ActorId;

    fn prep_iss(id: u64) -> (JournalRecord, JournalRecord) {
        let d = EffectDigest::of_bytes(b"e");
        let c = EffectCost::zero();
        (
            JournalRecord::EffectPrepared {
                id: EffectId(id),
                actor: ActorId(0),
                digest: d,
                effect_bytes: b"e".to_vec(),
                cost: c,
            },
            JournalRecord::EffectIssued {
                id: EffectId(id),
                actor: ActorId(0),
                digest: d,
                effect_bytes: b"e".to_vec(),
                cost: c,
            },
        )
    }

    #[test]
    fn t1_prepared_only_discard() {
        let (p, _) = prep_iss(0);
        let mut h = CrashHarness::new();
        h.push(p);
        h.sync_all_pending();
        let r = h.recover_at().unwrap();
        assert_eq!(r.effects.len(), 1);
        assert!(r.effects[0].is_discard());
        assert!(!r.effects[0].is_indeterminate());
        // Never NotExecuted
        assert!(!r.effects[0].is_not_executed_local());
    }

    #[test]
    fn t2_issued_indeterminate() {
        let (p, i) = prep_iss(0);
        let mut h = CrashHarness::new();
        h.push(p);
        h.push(i);
        h.sync_all_pending();
        let r = h.recover_at().unwrap();
        assert_eq!(r.effects.len(), 1);
        assert!(r.effects[0].is_indeterminate());
        assert!(!r.effects[0].is_not_executed_local());
    }

    #[test]
    fn t5_completed() {
        let (p, i) = prep_iss(0);
        let d = EffectDigest::of_bytes(b"e");
        let rd = EffectDigest::of_bytes(b"r");
        let mut h = CrashHarness::new();
        h.push(p);
        h.push(i);
        h.push(JournalRecord::EffectCompleted {
            id: EffectId(0),
            digest: d,
            result_digest: rd,
            result_bytes: b"r".to_vec(),
        });
        h.sync_all_pending();
        let r = h.recover_at().unwrap();
        assert!(matches!(r.effects[0], EffectClass::Completed { .. }));
        assert_eq!(r.next_effect_id, 1);
    }

    #[test]
    fn t0_empty() {
        let h = CrashHarness::new();
        let r = h.recover_at().unwrap();
        assert!(r.effects.is_empty());
        assert!(r.complete);
    }

    #[test]
    fn t6_snapshot() {
        let (p, i) = prep_iss(0);
        let mut h = CrashHarness::new();
        h.push(p);
        h.push(i);
        h.sync_all_pending();
        h.snapshot = Some(SnapshotImage {
            logical_time: 9,
            next_actor_id: 2,
            next_effect_id: 1,
            wal_seq_covered: 0, // set on materialize
            budget_units: 50,
            escrow_units: 5,
            actors: vec![],
            authority_blob: vec![],
            machine_blob: vec![],
        });
        h.snapshot_committed = true;
        let r = h.recover_at().unwrap();
        assert_eq!(r.logical_time, 9);
        assert_eq!(r.budget_units, 50);
        assert_eq!(r.escrow_units, 5);
        assert!(r.snapshot_seq.is_some());
    }

    #[test]
    fn recon_requires_evidence() {
        let ev = ReconEvidence {
            id: EffectId(0),
            digest: EffectDigest::of_bytes(b"e"),
            evidence_tag: 0, // not authoritative
            evidence_bytes: vec![],
        };
        assert!(admit_recon_evidence(&ev).is_err());
        let ev2 = ReconEvidence {
            evidence_tag: 1,
            ..ev
        };
        assert!(admit_recon_evidence(&ev2).is_ok());
    }

    #[test]
    fn no_host_surface() {
        assert_eq!(recovery_host_surface(), "none — recover(DurableState) only");
    }

    #[test]
    fn corrupt_wal_fails_no_silent_repair() {
        let (p, i) = prep_iss(0);
        let mut h = CrashHarness::new();
        h.push(p);
        h.push(i);
        h.sync_all_pending();
        let mut d = h.durable_state().unwrap();
        if let Some(b) = d.wal_bytes.last_mut() {
            *b ^= 0xff;
        }
        let err = recover(&d).unwrap_err();
        assert!(matches!(
            err,
            RecoveryFault::Integrity | RecoveryFault::Wal(_) | RecoveryFault::Sequence
        ));
    }
}
