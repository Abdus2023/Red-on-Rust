//! Unified effect journal record kinds (R-PERSIST-03; R-DUR-06 payloads).
//!
//! Extends the M5 `IssuanceRecord` surface with Reconciled + Event kinds used
//! by recovery. Encoding is provisional (U-02 / U-24 disclose).

use ror_core::digest::EffectDigest;
use ror_core::effect::{EffectCost, IssuanceRecord};
use ror_core::types::{ActorId, CapRef, EffectId};

use crate::wal::{WalError, WalKind, WalLog, WalSequence};

/// Journal-level record (R-PERSIST-03 + R-DUR-06).
#[derive(Clone, Debug, PartialEq, Eq)]
pub enum JournalRecord {
    Event {
        tag: u32,
        bytes: Vec<u8>,
    },
    EffectPrepared {
        id: EffectId,
        actor: ActorId,
        digest: EffectDigest,
        effect_bytes: Vec<u8>,
        cost: EffectCost,
    },
    EffectIssued {
        id: EffectId,
        actor: ActorId,
        digest: EffectDigest,
        effect_bytes: Vec<u8>,
        cost: EffectCost,
    },
    EffectCompleted {
        id: EffectId,
        digest: EffectDigest,
        result_digest: EffectDigest,
        result_bytes: Vec<u8>,
    },
    /// Durable reconciliation outcome (R-RECOV-07/08). Never local NotExecuted
    /// without authoritative evidence — evidence_tag carries the class.
    EffectReconciled {
        id: EffectId,
        digest: EffectDigest,
        /// Provisional evidence tag (U-06 residual). 1 = host-confirmed-absent
        /// (NotExecuted only with auth evidence); 2 = host-confirmed-complete;
        /// 3 = external-bound; 0 = unspecified/open.
        evidence_tag: u8,
        evidence_bytes: Vec<u8>,
    },
    CapGranted {
        cap: CapRef,
        actor: ActorId,
    },
    CapDerived {
        parent: CapRef,
        child: CapRef,
        actor: ActorId,
    },
    CapRevoked {
        cap: CapRef,
    },
}

impl JournalRecord {
    pub fn from_issuance(r: &IssuanceRecord) -> Self {
        match r {
            IssuanceRecord::Prepared {
                id,
                actor,
                digest,
                effect_bytes,
                cost,
            } => Self::EffectPrepared {
                id: *id,
                actor: *actor,
                digest: *digest,
                effect_bytes: effect_bytes.clone(),
                cost: *cost,
            },
            IssuanceRecord::Issued {
                id,
                actor,
                digest,
                effect_bytes,
                cost,
            } => Self::EffectIssued {
                id: *id,
                actor: *actor,
                digest: *digest,
                effect_bytes: effect_bytes.clone(),
                cost: *cost,
            },
            IssuanceRecord::Completed {
                id,
                digest,
                result_digest,
                result_bytes,
            } => Self::EffectCompleted {
                id: *id,
                digest: *digest,
                result_digest: *result_digest,
                result_bytes: result_bytes.clone(),
            },
        }
    }

    pub fn wal_kind(&self) -> WalKind {
        match self {
            Self::Event { .. } => WalKind::Event,
            Self::EffectPrepared { .. } => WalKind::EffectPrepared,
            Self::EffectIssued { .. } => WalKind::EffectIssued,
            Self::EffectCompleted { .. } => WalKind::EffectCompleted,
            Self::EffectReconciled { .. } => WalKind::EffectReconciled,
            Self::CapGranted { .. } => WalKind::CapGranted,
            Self::CapDerived { .. } => WalKind::CapDerived,
            Self::CapRevoked { .. } => WalKind::CapRevoked,
        }
    }

    pub fn effect_id(&self) -> Option<EffectId> {
        match self {
            Self::EffectPrepared { id, .. }
            | Self::EffectIssued { id, .. }
            | Self::EffectCompleted { id, .. }
            | Self::EffectReconciled { id, .. } => Some(*id),
            _ => None,
        }
    }

    /// Provisional payload codec (U-02/U-24). Length-prefixed fields, BE ints.
    pub fn encode_payload(&self) -> Vec<u8> {
        let mut o = Vec::new();
        match self {
            Self::Event { tag, bytes } => {
                o.extend_from_slice(&tag.to_be_bytes());
                push_bytes(&mut o, bytes);
            }
            Self::EffectPrepared {
                id,
                actor,
                digest,
                effect_bytes,
                cost,
            }
            | Self::EffectIssued {
                id,
                actor,
                digest,
                effect_bytes,
                cost,
            } => {
                o.extend_from_slice(&id.0.to_be_bytes());
                o.extend_from_slice(&actor.0.to_be_bytes());
                o.extend_from_slice(&digest.0);
                push_bytes(&mut o, effect_bytes);
                push_cost(&mut o, cost);
            }
            Self::EffectCompleted {
                id,
                digest,
                result_digest,
                result_bytes,
            } => {
                o.extend_from_slice(&id.0.to_be_bytes());
                o.extend_from_slice(&digest.0);
                o.extend_from_slice(&result_digest.0);
                push_bytes(&mut o, result_bytes);
            }
            Self::EffectReconciled {
                id,
                digest,
                evidence_tag,
                evidence_bytes,
            } => {
                o.extend_from_slice(&id.0.to_be_bytes());
                o.extend_from_slice(&digest.0);
                o.push(*evidence_tag);
                push_bytes(&mut o, evidence_bytes);
            }
            Self::CapGranted { cap, actor } => {
                push_cap(&mut o, cap);
                o.extend_from_slice(&actor.0.to_be_bytes());
            }
            Self::CapDerived {
                parent,
                child,
                actor,
            } => {
                push_cap(&mut o, parent);
                push_cap(&mut o, child);
                o.extend_from_slice(&actor.0.to_be_bytes());
            }
            Self::CapRevoked { cap } => {
                push_cap(&mut o, cap);
            }
        }
        o
    }

    pub fn decode_payload(kind: WalKind, payload: &[u8]) -> Result<Self, JournalError> {
        let mut p = PayloadReader::new(payload);
        match kind {
            WalKind::Event => {
                let tag = p.u32()?;
                let bytes = p.bytes()?.to_vec();
                Ok(Self::Event { tag, bytes })
            }
            WalKind::EffectPrepared => {
                let id = EffectId(p.u64()?);
                let actor = ActorId(p.u64()?);
                let digest = EffectDigest(p.digest32()?);
                let effect_bytes = p.bytes()?.to_vec();
                let cost = p.cost()?;
                Ok(Self::EffectPrepared {
                    id,
                    actor,
                    digest,
                    effect_bytes,
                    cost,
                })
            }
            WalKind::EffectIssued => {
                let id = EffectId(p.u64()?);
                let actor = ActorId(p.u64()?);
                let digest = EffectDigest(p.digest32()?);
                let effect_bytes = p.bytes()?.to_vec();
                let cost = p.cost()?;
                Ok(Self::EffectIssued {
                    id,
                    actor,
                    digest,
                    effect_bytes,
                    cost,
                })
            }
            WalKind::EffectCompleted => {
                let id = EffectId(p.u64()?);
                let digest = EffectDigest(p.digest32()?);
                let result_digest = EffectDigest(p.digest32()?);
                let result_bytes = p.bytes()?.to_vec();
                Ok(Self::EffectCompleted {
                    id,
                    digest,
                    result_digest,
                    result_bytes,
                })
            }
            WalKind::EffectReconciled => {
                let id = EffectId(p.u64()?);
                let digest = EffectDigest(p.digest32()?);
                let evidence_tag = p.u8()?;
                let evidence_bytes = p.bytes()?.to_vec();
                Ok(Self::EffectReconciled {
                    id,
                    digest,
                    evidence_tag,
                    evidence_bytes,
                })
            }
            WalKind::CapGranted => {
                let cap = p.cap()?;
                let actor = ActorId(p.u64()?);
                Ok(Self::CapGranted { cap, actor })
            }
            WalKind::CapDerived => {
                let parent = p.cap()?;
                let child = p.cap()?;
                let actor = ActorId(p.u64()?);
                Ok(Self::CapDerived {
                    parent,
                    child,
                    actor,
                })
            }
            WalKind::CapRevoked => {
                let cap = p.cap()?;
                Ok(Self::CapRevoked { cap })
            }
            WalKind::SnapshotCommit | WalKind::SnapshotBody => Err(JournalError::WrongKind),
        }
    }
}

fn push_bytes(o: &mut Vec<u8>, b: &[u8]) {
    o.extend_from_slice(&(b.len() as u32).to_be_bytes());
    o.extend_from_slice(b);
}

fn push_cost(o: &mut Vec<u8>, c: &EffectCost) {
    o.extend_from_slice(&c.issue.units.to_be_bytes());
    o.extend_from_slice(&c.complete_max.units.to_be_bytes());
    o.extend_from_slice(&c.reserve.slots.to_be_bytes());
}

fn push_cap(o: &mut Vec<u8>, c: &CapRef) {
    o.extend_from_slice(&c.index().to_be_bytes());
    o.extend_from_slice(&c.generation().to_be_bytes());
}

struct PayloadReader<'a> {
    data: &'a [u8],
    off: usize,
}

impl<'a> PayloadReader<'a> {
    fn new(data: &'a [u8]) -> Self {
        Self { data, off: 0 }
    }

    fn take(&mut self, n: usize) -> Result<&'a [u8], JournalError> {
        if self.off + n > self.data.len() {
            return Err(JournalError::Truncated);
        }
        let s = &self.data[self.off..self.off + n];
        self.off += n;
        Ok(s)
    }

    fn u8(&mut self) -> Result<u8, JournalError> {
        Ok(self.take(1)?[0])
    }

    fn u32(&mut self) -> Result<u32, JournalError> {
        Ok(u32::from_be_bytes(self.take(4)?.try_into().unwrap()))
    }

    fn u64(&mut self) -> Result<u64, JournalError> {
        Ok(u64::from_be_bytes(self.take(8)?.try_into().unwrap()))
    }

    fn digest32(&mut self) -> Result<[u8; 32], JournalError> {
        let s = self.take(32)?;
        let mut a = [0u8; 32];
        a.copy_from_slice(s);
        Ok(a)
    }

    fn bytes(&mut self) -> Result<&'a [u8], JournalError> {
        let n = self.u32()? as usize;
        self.take(n)
    }

    fn cost(&mut self) -> Result<EffectCost, JournalError> {
        let issue = self.u64()?;
        let complete_max = self.u64()?;
        let reserve = self.u64()?;
        Ok(EffectCost::new(issue, complete_max, reserve))
    }

    fn cap(&mut self) -> Result<CapRef, JournalError> {
        let index = self.u32()?;
        let generation = self.u32()?;
        Ok(CapRef::from_kernel_parts(index, generation))
    }
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub enum JournalError {
    Truncated,
    WrongKind,
    CausalViolation,
    Io,
    Wal(WalError),
}

impl From<WalError> for JournalError {
    fn from(e: WalError) -> Self {
        JournalError::Wal(e)
    }
}

/// Effect journal over a WAL (R-DUR-03 causal journal).
#[derive(Clone, Debug, Default)]
pub struct EffectJournal {
    wal: WalLog,
    /// Decoded durable journal records in order (synced only).
    durable: Vec<(WalSequence, JournalRecord)>,
    /// Pending decoded records awaiting sync.
    pending: Vec<(WalSequence, JournalRecord)>,
}

impl EffectJournal {
    pub fn new() -> Self {
        Self::default()
    }

    pub fn wal(&self) -> &WalLog {
        &self.wal
    }

    pub fn wal_mut(&mut self) -> &mut WalLog {
        &mut self.wal
    }

    pub fn durable_records(&self) -> &[(WalSequence, JournalRecord)] {
        &self.durable
    }

    pub fn pending_records(&self) -> &[(WalSequence, JournalRecord)] {
        &self.pending
    }

    pub fn append_record(&mut self, record: JournalRecord) -> Result<WalSequence, JournalError> {
        // Causal: Issued requires prior Prepared with same id+digest.
        if let JournalRecord::EffectIssued { id, digest, .. } = &record {
            let ok = self
                .pending
                .iter()
                .chain(self.durable.iter())
                .any(|(_, r)| {
                    matches!(
                        r,
                        JournalRecord::EffectPrepared { id: i, digest: d, .. }
                            if i == id && d == digest
                    )
                });
            if !ok {
                return Err(JournalError::CausalViolation);
            }
        }
        // Completed requires prior Issued.
        if let JournalRecord::EffectCompleted { id, digest, .. } = &record {
            let ok = self
                .pending
                .iter()
                .chain(self.durable.iter())
                .any(|(_, r)| {
                    matches!(
                        r,
                        JournalRecord::EffectIssued { id: i, digest: d, .. }
                            if i == id && d == digest
                    )
                });
            if !ok {
                return Err(JournalError::CausalViolation);
            }
        }
        let kind = record.wal_kind();
        let payload = record.encode_payload();
        let seq = self.wal.append(kind, payload)?;
        self.pending.push((seq, record));
        Ok(seq)
    }

    pub fn sync(&mut self) -> Result<(), JournalError> {
        self.wal.sync()?;
        self.durable.append(&mut self.pending);
        Ok(())
    }

    /// Crash: drop unsynced pending (only durable survives).
    pub fn crash_discard_pending(&mut self) {
        self.pending.clear();
        self.wal.crash_discard_pending();
    }

    pub fn is_durably_issued(&self, id: EffectId) -> bool {
        self.durable
            .iter()
            .any(|(_, r)| matches!(r, JournalRecord::EffectIssued { id: i, .. } if *i == id))
    }

    pub fn is_durably_completed(&self, id: EffectId) -> bool {
        self.durable
            .iter()
            .any(|(_, r)| matches!(r, JournalRecord::EffectCompleted { id: i, .. } if *i == id))
    }

    pub fn is_durably_reconciled(&self, id: EffectId) -> bool {
        self.durable
            .iter()
            .any(|(_, r)| matches!(r, JournalRecord::EffectReconciled { id: i, .. } if *i == id))
    }

    /// Rebuild journal from a verified WAL byte stream (no silent repair).
    pub fn recover_from_wal_bytes(bytes: &[u8]) -> Result<Self, JournalError> {
        let frames = WalLog::parse_and_verify(bytes)?;
        let mut durable = Vec::new();
        for f in &frames {
            // Snapshot frames handled by snapshot module; skip body/commit here
            // when rebuilding pure effect journal views — recovery engine owns
            // the full pipeline. Still decode effect kinds.
            match f.kind {
                WalKind::SnapshotBody | WalKind::SnapshotCommit => continue,
                k => {
                    let rec = JournalRecord::decode_payload(k, &f.payload)?;
                    durable.push((f.sequence, rec));
                }
            }
        }
        let wal = WalLog::from_verified_frames(frames);
        Ok(Self {
            wal,
            durable,
            pending: Vec::new(),
        })
    }
}

/// Bridge: `IssuanceJournal` over `EffectJournal` (preserves M5 hinge API).
impl crate::IssuanceJournal for EffectJournal {
    fn append(&mut self, record: IssuanceRecord) -> Result<(), crate::PersistError> {
        self.append_record(JournalRecord::from_issuance(&record))
            .map(|_| ())
            .map_err(|e| match e {
                JournalError::Io | JournalError::Wal(WalError::Io) => crate::PersistError::Io,
                JournalError::CausalViolation => crate::PersistError::CausalViolation,
                _ => crate::PersistError::JournalCorruption,
            })
    }

    fn sync(&mut self) -> Result<(), crate::PersistError> {
        self.sync().map_err(|e| match e {
            JournalError::Io | JournalError::Wal(WalError::Io) => crate::PersistError::Io,
            _ => crate::PersistError::JournalCorruption,
        })
    }
}

/// Helpers for Completed / Reconciled construction.
pub fn completed(
    id: EffectId,
    digest: EffectDigest,
    result_digest: EffectDigest,
    result_bytes: Vec<u8>,
) -> JournalRecord {
    JournalRecord::EffectCompleted {
        id,
        digest,
        result_digest,
        result_bytes,
    }
}

pub fn reconciled(
    id: EffectId,
    digest: EffectDigest,
    evidence_tag: u8,
    evidence_bytes: Vec<u8>,
) -> JournalRecord {
    JournalRecord::EffectReconciled {
        id,
        digest,
        evidence_tag,
        evidence_bytes,
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use ror_core::effect::EffectCost;

    #[test]
    fn prepared_issued_completed_roundtrip() {
        let mut j = EffectJournal::new();
        let id = EffectId(0);
        let d = EffectDigest::of_bytes(b"e");
        let c = EffectCost::zero();
        j.append_record(JournalRecord::EffectPrepared {
            id,
            actor: ActorId(1),
            digest: d,
            effect_bytes: b"e".to_vec(),
            cost: c,
        })
        .unwrap();
        j.sync().unwrap();
        j.append_record(JournalRecord::EffectIssued {
            id,
            actor: ActorId(1),
            digest: d,
            effect_bytes: b"e".to_vec(),
            cost: c,
        })
        .unwrap();
        j.sync().unwrap();
        assert!(j.is_durably_issued(id));
        let rd = EffectDigest::of_bytes(b"r");
        j.append_record(completed(id, d, rd, b"r".to_vec()))
            .unwrap();
        j.sync().unwrap();
        assert!(j.is_durably_completed(id));

        let bytes = j.wal().encode_committed();
        let j2 = EffectJournal::recover_from_wal_bytes(&bytes).unwrap();
        assert!(j2.is_durably_issued(id));
        assert!(j2.is_durably_completed(id));
    }
}
