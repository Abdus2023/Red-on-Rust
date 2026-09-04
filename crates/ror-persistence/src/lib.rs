#![forbid(unsafe_code)]

//! Issuance journal (M5 thin) — R-DUR-01/02/06/07.
//!
//! **Not M7:** no WAL framing, snapshot, crash recovery, or T0–T6 engine.
//! Provides append + sync for Prepared/Issued/Completed semantic records so
//! `HostInvoked ⇒ DurableIssued` is enforceable (R-TRUST-05 hinge).

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

/// Issuance journal API (M5).
pub trait IssuanceJournal {
    fn append(&mut self, record: IssuanceRecord) -> Result<(), PersistError>;
    fn sync(&mut self) -> Result<(), PersistError>;
}

/// In-memory test journal: durable after successful sync of pending appends.
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
}
