//! M7 differential: production recovery vs independent reference recovery.
//!
//! Production: `ror_persistence::recover`
//! Reference: `ror_reference::ref_recover` (core-only; no persistence import)
//!
//! Agreement: Canonical effect classes + counters + snapshot fields (R-RECOV-04).

use ror_core::digest::EffectDigest;
use ror_core::effect::EffectCost;
use ror_core::types::{ActorId, EffectId};
use ror_persistence::{
    recover, ActorSnap, CrashHarness, DurableState, EffectClass, JournalRecord, RecoveryResult,
    SnapshotImage,
};
use ror_reference::{ref_recover, RefEffectClass, RefRecoveryObservation};

/// Canonical recovery observation shared by both sides for equality.
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct RecoveryObservation {
    pub logical_time: u64,
    pub next_effect_id: u64,
    pub next_actor_id: u64,
    pub budget_units: u64,
    pub escrow_units: u64,
    pub runnable: Vec<u64>,
    /// Per-effect: (id, class_label)
    pub effect_labels: Vec<(u64, String)>,
    pub snapshot_present: bool,
    pub complete: bool,
}

fn prod_to_obs(r: &RecoveryResult) -> RecoveryObservation {
    let effect_labels = r
        .effects
        .iter()
        .map(|e| match e {
            EffectClass::Discard { id, .. } => (id.0, "discard".to_string()),
            EffectClass::Indeterminate { id, .. } => (id.0, "indeterminate".to_string()),
            EffectClass::Completed { id, .. } => (id.0, "completed".to_string()),
            EffectClass::Reconciled { id, .. } => (id.0, "reconciled".to_string()),
            EffectClass::Absent => (u64::MAX, "absent".to_string()),
        })
        .collect();
    RecoveryObservation {
        logical_time: r.logical_time,
        next_effect_id: r.next_effect_id,
        next_actor_id: r.next_actor_id,
        budget_units: r.budget_units,
        escrow_units: r.escrow_units,
        runnable: r.runnable.clone(),
        effect_labels,
        snapshot_present: r.snapshot_seq.is_some(),
        complete: r.complete,
    }
}

fn ref_to_obs(r: &RefRecoveryObservation) -> RecoveryObservation {
    let effect_labels = r
        .effects
        .iter()
        .map(|e| match e {
            RefEffectClass::Discard { id, .. } => (*id, "discard".to_string()),
            RefEffectClass::Indeterminate { id, .. } => (*id, "indeterminate".to_string()),
            RefEffectClass::Completed { id, .. } => (*id, "completed".to_string()),
            RefEffectClass::Reconciled { id, .. } => (*id, "reconciled".to_string()),
        })
        .collect();
    RecoveryObservation {
        logical_time: r.logical_time,
        next_effect_id: r.next_effect_id,
        next_actor_id: r.next_actor_id,
        budget_units: r.budget_units,
        escrow_units: r.escrow_units,
        runnable: r.runnable.clone(),
        effect_labels,
        snapshot_present: r.snapshot_present,
        complete: r.complete,
    }
}

/// Observe production recovery over durable WAL bytes.
pub fn observe_production_m7(wal_bytes: &[u8]) -> Result<RecoveryObservation, String> {
    let r = recover(&DurableState {
        wal_bytes: wal_bytes.to_vec(),
    })
    .map_err(|e| format!("prod recover: {e:?}"))?;
    Ok(prod_to_obs(&r))
}

/// Observe reference recovery over the same bytes.
pub fn observe_reference_m7(wal_bytes: &[u8]) -> Result<RecoveryObservation, String> {
    let r = ref_recover(wal_bytes).map_err(|e| format!("ref recover: {e:?}"))?;
    Ok(ref_to_obs(&r))
}

/// Compare production vs reference recovery observations.
pub fn compare_m7(wal_bytes: &[u8]) -> Result<(), Box<(RecoveryObservation, RecoveryObservation)>> {
    let p = observe_production_m7(wal_bytes).expect("prod");
    let r = observe_reference_m7(wal_bytes).expect("ref");
    if p == r {
        Ok(())
    } else {
        Err(Box::new((p, r)))
    }
}

/// Build a crash-harness WAL for differential fixtures.
pub fn fixture_issued_indeterminate() -> Vec<u8> {
    let d = EffectDigest::of_bytes(b"e");
    let c = EffectCost::zero();
    let mut h = CrashHarness::new();
    h.push(JournalRecord::EffectPrepared {
        id: EffectId(0),
        actor: ActorId(0),
        digest: d,
        effect_bytes: b"e".to_vec(),
        cost: c,
    });
    h.push(JournalRecord::EffectIssued {
        id: EffectId(0),
        actor: ActorId(0),
        digest: d,
        effect_bytes: b"e".to_vec(),
        cost: c,
    });
    h.sync_all_pending();
    h.durable_state().unwrap().wal_bytes
}

pub fn fixture_prepared_discard() -> Vec<u8> {
    let d = EffectDigest::of_bytes(b"e");
    let c = EffectCost::zero();
    let mut h = CrashHarness::new();
    h.push(JournalRecord::EffectPrepared {
        id: EffectId(0),
        actor: ActorId(0),
        digest: d,
        effect_bytes: b"e".to_vec(),
        cost: c,
    });
    h.sync_all_pending();
    h.durable_state().unwrap().wal_bytes
}

pub fn fixture_completed() -> Vec<u8> {
    let d = EffectDigest::of_bytes(b"e");
    let c = EffectCost::zero();
    let mut h = CrashHarness::new();
    h.push(JournalRecord::EffectPrepared {
        id: EffectId(0),
        actor: ActorId(0),
        digest: d,
        effect_bytes: b"e".to_vec(),
        cost: c,
    });
    h.push(JournalRecord::EffectIssued {
        id: EffectId(0),
        actor: ActorId(0),
        digest: d,
        effect_bytes: b"e".to_vec(),
        cost: c,
    });
    h.push(JournalRecord::EffectCompleted {
        id: EffectId(0),
        digest: d,
        result_digest: EffectDigest::of_bytes(b"r"),
        result_bytes: b"r".to_vec(),
    });
    h.sync_all_pending();
    h.durable_state().unwrap().wal_bytes
}

pub fn fixture_snapshot_t6() -> Vec<u8> {
    let d = EffectDigest::of_bytes(b"e");
    let c = EffectCost::zero();
    let mut h = CrashHarness::new();
    h.push(JournalRecord::EffectPrepared {
        id: EffectId(0),
        actor: ActorId(0),
        digest: d,
        effect_bytes: b"e".to_vec(),
        cost: c,
    });
    h.push(JournalRecord::EffectIssued {
        id: EffectId(0),
        actor: ActorId(0),
        digest: d,
        effect_bytes: b"e".to_vec(),
        cost: c,
    });
    h.sync_all_pending();
    h.snapshot = Some(SnapshotImage {
        logical_time: 3,
        next_actor_id: 2,
        next_effect_id: 1,
        wal_seq_covered: 0,
        budget_units: 20,
        escrow_units: 4,
        actors: vec![
            ActorSnap {
                id: 0,
                status: 0,
                pending_effect: u64::MAX,
                mailbox: vec![],
            },
            ActorSnap {
                id: 1,
                status: 2,
                pending_effect: 0,
                mailbox: b"m".to_vec(),
            },
        ],
        authority_blob: b"a".to_vec(),
        machine_blob: vec![],
    });
    h.snapshot_committed = true;
    h.durable_state().unwrap().wal_bytes
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn diff_t1_discard() {
        let bytes = fixture_prepared_discard();
        compare_m7(&bytes).expect("T1 discard agree");
        let o = observe_production_m7(&bytes).unwrap();
        assert_eq!(o.effect_labels, vec![(0, "discard".into())]);
    }

    #[test]
    fn diff_t2_indeterminate() {
        let bytes = fixture_issued_indeterminate();
        compare_m7(&bytes).expect("T2 indeterminate agree");
        let o = observe_production_m7(&bytes).unwrap();
        assert_eq!(o.effect_labels, vec![(0, "indeterminate".into())]);
    }

    #[test]
    fn diff_t5_completed() {
        let bytes = fixture_completed();
        compare_m7(&bytes).expect("T5 completed agree");
    }

    #[test]
    fn diff_t6_snapshot() {
        let bytes = fixture_snapshot_t6();
        compare_m7(&bytes).expect("T6 snapshot agree");
        let o = observe_production_m7(&bytes).unwrap();
        assert!(o.snapshot_present);
        assert_eq!(o.logical_time, 3);
        assert_eq!(o.budget_units, 20);
        assert_eq!(o.escrow_units, 4);
        assert_eq!(o.runnable, vec![0]);
    }

    #[test]
    fn diff_empty() {
        compare_m7(&[]).expect("empty agree");
    }
}
