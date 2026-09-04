#![forbid(unsafe_code)]

//! Persistence / WAL / snapshot / recovery (MOD-11/12) — M7.
//!
//! ## M5 hinge (immutable)
//! `IssuanceJournal` + `MemoryJournal` remain the thin durable-before-host API
//! used by `ror-runtime` (`HostInvoked ⇒ DurableIssued`, R-DUR-01 / GI-SEC-07).
//!
//! ## M7 surfaces
//! - WAL framing, sequence continuity, chained checksums (R-PERSIST-02/06/08)
//! - Unified journal kinds (R-PERSIST-03; R-DUR-06)
//! - Atomic snapshot protocol (R-PERSIST-04/05)
//! - Recovery `Recover(D)=Replay(S,L,H)` + T0–T6 (R-RECOV-01…09)
//!
//! ## Disclosed provisional codecs (OADs not closed)
//! - **U-32** WalFrame layout (5-field + payload_len)
//! - **U-02** snapshot / machine-state bytes
//! - **U-17** runnable queue reconstructed from actor statuses
//!
//! Recovery **never** calls the host and **never** re-executes effects
//! (R-RECOV-08). Prepared∧¬Issued⇒Discard; Issued∧¬Completed⇒Indeterminate
//! (≠ NotExecuted).

pub mod journal;
pub mod recovery;
pub mod snapshot;
pub mod wal;

pub use journal::{completed, reconciled, EffectJournal, JournalError, JournalRecord};
pub use recovery::{
    admit_recon_evidence, expected_class_for, recover, recovery_host_surface, CrashHarness,
    CrashPoint, DurableState, EffectClass, ReconEvidence, RecoveryFault, RecoveryResult,
};
pub use snapshot::{
    ActorSnap, CommittedSnapshot, SnapshotError, SnapshotImage, SnapshotPhase, SnapshotStore,
};
pub use wal::{
    frame_checksum, WalError, WalFrame, WalKind, WalLog, WalSequence, CHECKSUM_SEED, WAL_MAGIC,
    WAL_VERSION,
};

use ror_core::digest::EffectDigest;
use ror_core::effect::{EffectCost, IssuanceRecord};
use ror_core::types::{ActorId, EffectId};

/// Persistence fault (R-DUR-07). Provisional under U-08.
#[derive(Clone, Debug, PartialEq, Eq)]
pub enum PersistError {
    /// Append or sync failed.
    Io,
    /// Digest mismatch on record (R-DUR-06).
    JournalCorruption,
    /// Invalid causal order (e.g. Issued without Prepared).
    CausalViolation,
}

/// Issuance journal API (M5 hinge — preserved).
pub trait IssuanceJournal {
    fn append(&mut self, record: IssuanceRecord) -> Result<(), PersistError>;
    fn sync(&mut self) -> Result<(), PersistError>;
}

/// In-memory test journal: durable after successful sync of pending appends.
///
/// M5 hinge double. For full WAL-backed durability use [`EffectJournal`].
#[derive(Clone, Debug, Default)]
pub struct MemoryJournal {
    /// Records committed by the last successful sync barrier.
    durable: Vec<IssuanceRecord>,
    /// Appended but not yet synced.
    pending: Vec<IssuanceRecord>,
    /// If set, next append/sync fails once (live-failure tests).
    fail_next_append: bool,
    fail_next_sync: bool,
}

impl MemoryJournal {
    pub fn new() -> Self {
        Self::default()
    }

    pub fn fail_next_append(&mut self) {
        self.fail_next_append = true;
    }

    pub fn fail_next_sync(&mut self) {
        self.fail_next_sync = true;
    }

    pub fn durable_records(&self) -> &[IssuanceRecord] {
        &self.durable
    }

    pub fn pending_records(&self) -> &[IssuanceRecord] {
        &self.pending
    }

    /// True iff an Issued record for `id` is durable.
    pub fn is_durably_issued(&self, id: EffectId) -> bool {
        self.durable.iter().any(|r| match r {
            IssuanceRecord::Issued { id: i, .. } => *i == id,
            _ => false,
        })
    }

    pub fn clear_pending(&mut self) {
        self.pending.clear();
    }
}

impl IssuanceJournal for MemoryJournal {
    fn append(&mut self, record: IssuanceRecord) -> Result<(), PersistError> {
        if self.fail_next_append {
            self.fail_next_append = false;
            return Err(PersistError::Io);
        }
        // Causal: Issued requires prior Prepared (pending or durable) with same id+digest.
        if let IssuanceRecord::Issued { id, digest, .. } = &record {
            let prepared_ok = self
                .pending
                .iter()
                .chain(self.durable.iter())
                .any(|r| matches!(r, IssuanceRecord::Prepared { id: i, digest: d, .. } if i == id && d == digest));
            if !prepared_ok {
                return Err(PersistError::CausalViolation);
            }
        }
        self.pending.push(record);
        Ok(())
    }

    fn sync(&mut self) -> Result<(), PersistError> {
        if self.fail_next_sync {
            self.fail_next_sync = false;
            return Err(PersistError::Io);
        }
        self.durable.append(&mut self.pending);
        Ok(())
    }
}

/// Build Prepared record (R-DUR-06).
pub fn prepared(
    id: EffectId,
    actor: ActorId,
    digest: EffectDigest,
    effect_bytes: Vec<u8>,
    cost: EffectCost,
) -> IssuanceRecord {
    IssuanceRecord::Prepared {
        id,
        actor,
        digest,
        effect_bytes,
        cost,
    }
}

/// Build Issued record (R-DUR-06).
pub fn issued(
    id: EffectId,
    actor: ActorId,
    digest: EffectDigest,
    effect_bytes: Vec<u8>,
    cost: EffectCost,
) -> IssuanceRecord {
    IssuanceRecord::Issued {
        id,
        actor,
        digest,
        effect_bytes,
        cost,
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use ror_core::digest::EffectDigest;
    use ror_core::effect::EffectCost;
    use ror_core::types::{ActorId, EffectId};

    #[test]
    fn prepared_then_issued_sync() {
        let mut j = MemoryJournal::new();
        let id = EffectId(0);
        let d = EffectDigest::of_bytes(b"e");
        let c = EffectCost::zero();
        j.append(prepared(id, ActorId(0), d, b"e".to_vec(), c))
            .unwrap();
        j.sync().unwrap();
        j.append(issued(id, ActorId(0), d, b"e".to_vec(), c))
            .unwrap();
        j.sync().unwrap();
        assert!(j.is_durably_issued(id));
    }

    #[test]
    fn issued_without_prepared_fails() {
        let mut j = MemoryJournal::new();
        let id = EffectId(0);
        let d = EffectDigest::of_bytes(b"e");
        let err = j
            .append(issued(id, ActorId(0), d, b"e".to_vec(), EffectCost::zero()))
            .unwrap_err();
        assert_eq!(err, PersistError::CausalViolation);
    }

    #[test]
    fn effect_journal_implements_issuance_journal() {
        let mut j = EffectJournal::new();
        let id = EffectId(0);
        let d = EffectDigest::of_bytes(b"e");
        let c = EffectCost::zero();
        <EffectJournal as IssuanceJournal>::append(
            &mut j,
            prepared(id, ActorId(0), d, b"e".to_vec(), c),
        )
        .unwrap();
        <EffectJournal as IssuanceJournal>::sync(&mut j).unwrap();
        <EffectJournal as IssuanceJournal>::append(
            &mut j,
            issued(id, ActorId(0), d, b"e".to_vec(), c),
        )
        .unwrap();
        <EffectJournal as IssuanceJournal>::sync(&mut j).unwrap();
        assert!(j.is_durably_issued(id));
    }
}

#[cfg(test)]
mod crash_matrix_tests {
    //! T0–T6 crash harness + security mutations (P05–P12, P16–P20, P36).

    use super::*;
    use ror_core::digest::EffectDigest;
    use ror_core::effect::EffectCost;
    use ror_core::types::{ActorId, CapRef, EffectId};

    fn pair(id: u64) -> (JournalRecord, JournalRecord, EffectDigest) {
        let d = EffectDigest::of_bytes(&[id as u8, b'e']);
        let c = EffectCost::zero();
        (
            JournalRecord::EffectPrepared {
                id: EffectId(id),
                actor: ActorId(0),
                digest: d,
                effect_bytes: vec![id as u8],
                cost: c,
            },
            JournalRecord::EffectIssued {
                id: EffectId(id),
                actor: ActorId(0),
                digest: d,
                effect_bytes: vec![id as u8],
                cost: c,
            },
            d,
        )
    }

    #[test]
    fn t0_before_prepared_absent() {
        assert_eq!(
            expected_class_for(CrashPoint::T0, false, false, false),
            "absent"
        );
        let h = CrashHarness::new();
        let r = h.recover_at().unwrap();
        assert!(r.effects.is_empty());
        assert_eq!(r.next_effect_id, 0);
    }

    #[test]
    fn t1_prepared_not_issued_discard() {
        let (p, _, _) = pair(0);
        let mut h = CrashHarness::new();
        h.push(p);
        h.sync_all_pending();
        // Simulate failed Issued sync: only Prepared durable
        let r = h.recover_at().unwrap();
        assert_eq!(r.effects.len(), 1);
        assert!(matches!(&r.effects[0], EffectClass::Discard { id, .. } if id.0 == 0));
        // Must not be Indeterminate or NotExecuted
        assert!(!r.effects[0].is_indeterminate());
        assert!(!r.effects[0].is_not_executed_local());
    }

    #[test]
    fn t1_issued_sync_failure_still_discard() {
        // Prepared durable, Issued only pending → crash drops Issued → Discard
        let (p, i, _) = pair(1);
        let mut j = EffectJournal::new();
        j.append_record(p).unwrap();
        j.sync().unwrap();
        j.append_record(i).unwrap();
        // crash before Issued sync
        j.crash_discard_pending();
        let bytes = j.wal().encode_committed();
        let r = recover(&DurableState { wal_bytes: bytes }).unwrap();
        assert!(matches!(&r.effects[0], EffectClass::Discard { id, .. } if id.0 == 1));
    }

    #[test]
    fn t2_after_issued_indeterminate() {
        let (p, i, _) = pair(2);
        let mut h = CrashHarness::new();
        h.push(p);
        h.push(i);
        h.sync_all_pending();
        let r = h.recover_at().unwrap();
        assert!(matches!(
            &r.effects[0],
            EffectClass::Indeterminate { id, .. } if id.0 == 2
        ));
        // CRITICAL: Indeterminate ≠ NotExecuted
        assert!(!r.effects[0].is_not_executed_local());
    }

    #[test]
    fn t3_after_host_invocation_still_indeterminate() {
        // Host invocation is volatile — durable journal still Issued only.
        let (p, i, _) = pair(3);
        let mut h = CrashHarness::new();
        h.push(p);
        h.push(i);
        h.sync_all_pending();
        let r = h.recover_at().unwrap();
        assert!(r.effects[0].is_indeterminate());
        // Recovery must not invent Completed or NotExecuted
        assert!(!matches!(r.effects[0], EffectClass::Completed { .. }));
    }

    #[test]
    fn t4_host_complete_before_durable_completed_indeterminate() {
        // Result may exist only in volatile memory — durable = Issued.
        let (p, i, _) = pair(4);
        let mut h = CrashHarness::new();
        h.push(p);
        h.push(i);
        h.sync_all_pending();
        let r = h.recover_at().unwrap();
        assert!(r.effects[0].is_indeterminate());
    }

    #[test]
    fn t5_completed_reconstruct_no_rehost() {
        let (p, i, d) = pair(5);
        let rd = EffectDigest::of_bytes(b"result");
        let mut h = CrashHarness::new();
        h.push(p);
        h.push(i);
        h.push(JournalRecord::EffectCompleted {
            id: EffectId(5),
            digest: d,
            result_digest: rd,
            result_bytes: b"result".to_vec(),
        });
        h.sync_all_pending();
        let r = h.recover_at().unwrap();
        match &r.effects[0] {
            EffectClass::Completed {
                id, result_bytes, ..
            } => {
                assert_eq!(id.0, 5);
                assert_eq!(result_bytes, b"result");
            }
            other => panic!("expected Completed, got {other:?}"),
        }
        assert_eq!(r.next_effect_id, 6);
        // recover API has no host parameter
        assert_eq!(recovery_host_surface(), "none — recover(DurableState) only");
    }

    #[test]
    fn t6_snapshot_commit_resume() {
        let (p, i, _) = pair(6);
        let mut h = CrashHarness::new();
        h.push(p);
        h.push(i);
        h.sync_all_pending();
        h.snapshot = Some(SnapshotImage {
            logical_time: 42,
            next_actor_id: 3,
            next_effect_id: 7,
            wal_seq_covered: 0,
            budget_units: 99,
            escrow_units: 11,
            actors: vec![
                ActorSnap {
                    id: 0,
                    status: 0, // runnable
                    pending_effect: u64::MAX,
                    mailbox: b"a".to_vec(),
                },
                ActorSnap {
                    id: 1,
                    status: 2, // pending
                    pending_effect: 6,
                    mailbox: vec![],
                },
                ActorSnap {
                    id: 2,
                    status: 3, // terminal — must not become runnable
                    pending_effect: u64::MAX,
                    mailbox: vec![],
                },
            ],
            authority_blob: b"lattice".to_vec(),
            machine_blob: b"m".to_vec(),
        });
        h.snapshot_committed = true;
        let r = h.recover_at().unwrap();
        assert_eq!(r.logical_time, 42);
        assert_eq!(r.budget_units, 99);
        assert_eq!(r.escrow_units, 11);
        assert_eq!(r.runnable, vec![0]); // only status=0
        assert!(!r.runnable.contains(&2)); // terminal not runnable
        assert_eq!(r.authority_blob, b"lattice");
        assert!(r.snapshot_seq.is_some());
        // Pending actor binding preserved in snapshot image
        let pending = r.snapshot.actors.iter().find(|a| a.id == 1).unwrap();
        assert_eq!(pending.status, 2);
        assert_eq!(pending.pending_effect, 6);
    }

    #[test]
    fn mutation_checksum_corrupt_kills() {
        let (p, i, _) = pair(0);
        let mut h = CrashHarness::new();
        h.push(p);
        h.push(i);
        h.sync_all_pending();
        let mut d = h.durable_state().unwrap();
        let mid = d.wal_bytes.len() / 2;
        d.wal_bytes[mid] ^= 0xa5;
        assert!(recover(&d).is_err());
    }

    #[test]
    fn mutation_sequence_gap_kills() {
        let f1 = WalFrame::new(
            &CHECKSUM_SEED,
            WalSequence(1),
            WalKind::Event,
            b"a".to_vec(),
        );
        let f3 = WalFrame::new(&f1.checksum, WalSequence(3), WalKind::Event, b"c".to_vec());
        let mut bytes = f1.encode();
        bytes.extend_from_slice(&f3.encode());
        let err = recover(&DurableState { wal_bytes: bytes }).unwrap_err();
        assert!(matches!(
            err,
            RecoveryFault::Sequence | RecoveryFault::Wal(_)
        ));
    }

    #[test]
    fn mutation_indeterminate_not_silently_not_executed() {
        let (p, i, d) = pair(9);
        let mut h = CrashHarness::new();
        h.push(p);
        h.push(i);
        h.sync_all_pending();
        let r = h.recover_at().unwrap();
        assert!(r.effects[0].is_indeterminate());
        // Attempt local NotExecuted without evidence — rejected
        let bad = ReconEvidence {
            id: EffectId(9),
            digest: d,
            evidence_tag: 0,
            evidence_bytes: vec![],
        };
        assert!(admit_recon_evidence(&bad).is_err());
        // Authoritative evidence admitted
        let good = ReconEvidence {
            id: EffectId(9),
            digest: d,
            evidence_tag: 1,
            evidence_bytes: b"host-absent".to_vec(),
        };
        let rec = admit_recon_evidence(&good).unwrap();
        assert!(matches!(
            rec,
            JournalRecord::EffectReconciled {
                evidence_tag: 1,
                ..
            }
        ));
    }

    #[test]
    fn mutation_cap_revocation_monotonic() {
        let mut h = CrashHarness::new();
        h.push(JournalRecord::CapGranted {
            cap: CapRef::from_kernel_parts(1, 0),
            actor: ActorId(0),
        });
        h.push(JournalRecord::CapRevoked {
            cap: CapRef::from_kernel_parts(1, 0),
        });
        h.sync_all_pending();
        let r = h.recover_at().unwrap();
        assert!(r.revoked_caps.contains(&(1, 0)));
    }

    #[test]
    fn mutation_id_reuse_next_effect_advances() {
        let (p, i, d) = pair(0);
        let mut h = CrashHarness::new();
        h.push(p);
        h.push(i);
        h.push(JournalRecord::EffectCompleted {
            id: EffectId(0),
            digest: d,
            result_digest: EffectDigest::of_bytes(b"r"),
            result_bytes: b"r".to_vec(),
        });
        h.sync_all_pending();
        let r = h.recover_at().unwrap();
        assert_eq!(r.next_effect_id, 1);
        // Allocator must start at reconstructed next — never reuse 0
    }

    #[test]
    fn recovery_determinism() {
        let (p, i, _) = pair(0);
        let mut h = CrashHarness::new();
        h.push(p);
        h.push(i);
        h.sync_all_pending();
        h.snapshot = Some(SnapshotImage {
            logical_time: 1,
            next_actor_id: 1,
            next_effect_id: 1,
            wal_seq_covered: 0,
            budget_units: 10,
            escrow_units: 0,
            actors: vec![ActorSnap {
                id: 0,
                status: 0,
                pending_effect: u64::MAX,
                mailbox: vec![],
            }],
            authority_blob: vec![],
            machine_blob: vec![],
        });
        h.snapshot_committed = true;
        let r1 = h.recover_at().unwrap();
        let r2 = h.recover_at().unwrap();
        assert_eq!(r1, r2);
    }

    #[test]
    fn budget_and_time_not_advanced_on_recover() {
        let mut h = CrashHarness::new();
        h.snapshot = Some(SnapshotImage {
            logical_time: 5,
            next_actor_id: 0,
            next_effect_id: 0,
            wal_seq_covered: 0,
            budget_units: 77,
            escrow_units: 3,
            actors: vec![],
            authority_blob: vec![],
            machine_blob: vec![],
        });
        h.snapshot_committed = true;
        let r = h.recover_at().unwrap();
        assert_eq!(r.logical_time, 5);
        assert_eq!(r.budget_units, 77);
        assert_eq!(r.escrow_units, 3);
    }

    #[test]
    fn partial_truncated_wal_rejected() {
        let (p, _, _) = pair(0);
        let mut h = CrashHarness::new();
        h.push(p);
        h.sync_all_pending();
        let mut d = h.durable_state().unwrap();
        d.wal_bytes.truncate(d.wal_bytes.len() / 2);
        assert!(recover(&d).is_err());
    }

    #[test]
    fn effect_journal_hinge_compatible() {
        // EffectJournal as IssuanceJournal — M5 path still works
        let mut j = EffectJournal::new();
        let id = EffectId(0);
        let d = EffectDigest::of_bytes(b"e");
        let c = EffectCost::zero();
        j.append(prepared(id, ActorId(0), d, b"e".to_vec(), c))
            .unwrap();
        j.sync().unwrap();
        j.append(issued(id, ActorId(0), d, b"e".to_vec(), c))
            .unwrap();
        j.sync().unwrap();
        assert!(j.is_durably_issued(id));
        // Crash after Issued: Indeterminate
        let bytes = j.wal().encode_committed();
        let r = recover(&DurableState { wal_bytes: bytes }).unwrap();
        assert!(r.effects[0].is_indeterminate());
    }
}
