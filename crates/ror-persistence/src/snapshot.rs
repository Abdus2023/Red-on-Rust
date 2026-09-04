//! Atomic snapshot protocol (R-PERSIST-04/05).
//!
//! **U-02 OPEN:** machine-state byte codec is **provisional**.
//! **U-17 OPEN:** runnable queue is reconstructed from actor statuses by default
//! (not a mandatory persisted field) — disclosed provisional choice.

use ror_core::digest::{sha256, StateDigest};

use crate::journal::JournalError;
use crate::wal::{WalError, WalKind, WalLog, WalSequence};

/// Snapshot begin/commit markers (R-PERSIST-05).
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum SnapshotPhase {
    /// Incomplete begin — crash leaves garbage (not ValidSnapshot).
    Begin,
    /// Commit recorded with state_digest — ValidSnapshot.
    Commit,
}

/// Thin durable machine image (R-PERSIST-04 content obligations; U-02 codec).
///
/// Fields required for resumption; encodings provisional.
#[derive(Clone, Debug, PartialEq, Eq, Default)]
pub struct SnapshotImage {
    /// Logical time.
    pub logical_time: u64,
    /// Next ActorId counter (R-ACTOR-03 / R-RECOV-09).
    pub next_actor_id: u64,
    /// Next EffectId counter (R-RECOV-09).
    pub next_effect_id: u64,
    /// WAL sequence covered by this snapshot (exclusive upper: replay after).
    pub wal_seq_covered: u64,
    /// Budget remaining (thin units partition; R-RECOV-06).
    pub budget_units: u64,
    /// Escrow reserved units (R-DUR-05 survival).
    pub escrow_units: u64,
    /// Actor table: (actor_id, status_tag, pending_effect_id_or_u64_max, mailbox_blob).
    /// status_tag: 0=Runnable, 1=Blocked, 2=Pending, 3=Terminal.
    pub actors: Vec<ActorSnap>,
    /// Capability arena blob (U-31/U-02 provisional opaque bytes).
    pub authority_blob: Vec<u8>,
    /// Extra opaque machine blob (U-02).
    pub machine_blob: Vec<u8>,
}

/// Per-actor snapshot row (U-27/U-30 provisional).
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct ActorSnap {
    pub id: u64,
    /// 0 Runnable, 1 Blocked, 2 Pending, 3 Terminal.
    pub status: u8,
    /// Bound effect id when Pending; else u64::MAX.
    pub pending_effect: u64,
    pub mailbox: Vec<u8>,
}

impl SnapshotImage {
    /// Provisional encode (U-02).
    pub fn encode(&self) -> Vec<u8> {
        let mut o = Vec::new();
        o.extend_from_slice(&self.logical_time.to_be_bytes());
        o.extend_from_slice(&self.next_actor_id.to_be_bytes());
        o.extend_from_slice(&self.next_effect_id.to_be_bytes());
        o.extend_from_slice(&self.wal_seq_covered.to_be_bytes());
        o.extend_from_slice(&self.budget_units.to_be_bytes());
        o.extend_from_slice(&self.escrow_units.to_be_bytes());
        o.extend_from_slice(&(self.actors.len() as u32).to_be_bytes());
        for a in &self.actors {
            o.extend_from_slice(&a.id.to_be_bytes());
            o.push(a.status);
            o.extend_from_slice(&a.pending_effect.to_be_bytes());
            o.extend_from_slice(&(a.mailbox.len() as u32).to_be_bytes());
            o.extend_from_slice(&a.mailbox);
        }
        o.extend_from_slice(&(self.authority_blob.len() as u32).to_be_bytes());
        o.extend_from_slice(&self.authority_blob);
        o.extend_from_slice(&(self.machine_blob.len() as u32).to_be_bytes());
        o.extend_from_slice(&self.machine_blob);
        o
    }

    pub fn decode(bytes: &[u8]) -> Result<Self, SnapshotError> {
        let mut p = SnapReader::new(bytes);
        let logical_time = p.u64()?;
        let next_actor_id = p.u64()?;
        let next_effect_id = p.u64()?;
        let wal_seq_covered = p.u64()?;
        let budget_units = p.u64()?;
        let escrow_units = p.u64()?;
        let n = p.u32()? as usize;
        let mut actors = Vec::with_capacity(n);
        for _ in 0..n {
            let id = p.u64()?;
            let status = p.u8()?;
            let pending_effect = p.u64()?;
            let mlen = p.u32()? as usize;
            let mailbox = p.take(mlen)?.to_vec();
            actors.push(ActorSnap {
                id,
                status,
                pending_effect,
                mailbox,
            });
        }
        let alen = p.u32()? as usize;
        let authority_blob = p.take(alen)?.to_vec();
        let mblen = p.u32()? as usize;
        let machine_blob = p.take(mblen)?.to_vec();
        Ok(Self {
            logical_time,
            next_actor_id,
            next_effect_id,
            wal_seq_covered,
            budget_units,
            escrow_units,
            actors,
            authority_blob,
            machine_blob,
        })
    }

    pub fn state_digest(&self) -> StateDigest {
        StateDigest::of_bytes(&self.encode())
    }

    /// Reconstruct runnable actor ids from statuses (U-17 provisional choice).
    pub fn reconstruct_runnable_queue(&self) -> Vec<u64> {
        let mut q: Vec<u64> = self
            .actors
            .iter()
            .filter(|a| a.status == 0) // Runnable
            .map(|a| a.id)
            .collect();
        q.sort_unstable(); // deterministic (R-RECOV-03 §10)
        q
    }
}

struct SnapReader<'a> {
    data: &'a [u8],
    off: usize,
}

impl<'a> SnapReader<'a> {
    fn new(data: &'a [u8]) -> Self {
        Self { data, off: 0 }
    }
    fn take(&mut self, n: usize) -> Result<&'a [u8], SnapshotError> {
        if self.off + n > self.data.len() {
            return Err(SnapshotError::Truncated);
        }
        let s = &self.data[self.off..self.off + n];
        self.off += n;
        Ok(s)
    }
    fn u8(&mut self) -> Result<u8, SnapshotError> {
        Ok(self.take(1)?[0])
    }
    fn u32(&mut self) -> Result<u32, SnapshotError> {
        Ok(u32::from_be_bytes(self.take(4)?.try_into().unwrap()))
    }
    fn u64(&mut self) -> Result<u64, SnapshotError> {
        Ok(u64::from_be_bytes(self.take(8)?.try_into().unwrap()))
    }
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub enum SnapshotError {
    Truncated,
    Incomplete,
    DigestMismatch,
    Io,
    Wal(WalError),
    Journal(JournalError),
}

impl From<WalError> for SnapshotError {
    fn from(e: WalError) -> Self {
        SnapshotError::Wal(e)
    }
}

/// Valid committed snapshot handle.
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct CommittedSnapshot {
    pub seq: WalSequence,
    pub image: SnapshotImage,
    pub state_digest: StateDigest,
}

/// Snapshot store protocol over WAL (R-PERSIST-05).
///
/// Protocol: Begin (body frame) → fsync → Commit+state_digest.
/// Incomplete begin without commit = garbage (not ValidSnapshot).
#[derive(Clone, Debug, Default)]
pub struct SnapshotStore {
    /// Last valid committed snapshot, if any.
    committed: Option<CommittedSnapshot>,
    /// In-progress begin body (not yet committed).
    begin_pending: Option<SnapshotImage>,
}

impl SnapshotStore {
    pub fn new() -> Self {
        Self::default()
    }

    pub fn committed(&self) -> Option<&CommittedSnapshot> {
        self.committed.as_ref()
    }

    /// Begin snapshot: stage image (not valid until commit+sync).
    pub fn begin(&mut self, image: SnapshotImage) {
        self.begin_pending = Some(image);
    }

    /// Write begin body + commit to WAL and sync. Returns committed snapshot.
    ///
    /// Cadence note (R-RECOV-09): caller must not invoke inside issuance
    /// section s12–s14b — enforced by higher layers / tests, not here.
    pub fn commit_to_wal(&mut self, wal: &mut WalLog) -> Result<CommittedSnapshot, SnapshotError> {
        let image = self.begin_pending.take().ok_or(SnapshotError::Incomplete)?;
        let body = image.encode();
        let digest = StateDigest::of_bytes(&body);
        // Body frame
        wal.append(WalKind::SnapshotBody, body)?;
        // Commit frame: wal_seq_covered already in image; payload = digest bytes
        let mut commit_payload = Vec::with_capacity(32 + 8);
        commit_payload.extend_from_slice(&digest.0);
        commit_payload.extend_from_slice(&image.wal_seq_covered.to_be_bytes());
        let seq = wal.append(WalKind::SnapshotCommit, commit_payload)?;
        wal.sync()?;
        let cs = CommittedSnapshot {
            seq,
            image,
            state_digest: digest,
        };
        self.committed = Some(cs.clone());
        Ok(cs)
    }

    /// Crash: drop incomplete begin (garbage).
    pub fn crash_discard_begin(&mut self) {
        self.begin_pending = None;
    }

    /// Locate newest ValidSnapshot from WAL frames (R-RECOV-03 step 1–2).
    pub fn from_wal_frames(frames: &[crate::wal::WalFrame]) -> Result<Self, SnapshotError> {
        let mut store = Self::new();
        let mut pending_body: Option<Vec<u8>> = None;
        for f in frames {
            match f.kind {
                WalKind::SnapshotBody => {
                    pending_body = Some(f.payload.clone());
                }
                WalKind::SnapshotCommit => {
                    let body = match pending_body.take() {
                        Some(b) => b,
                        None => return Err(SnapshotError::Incomplete),
                    };
                    if f.payload.len() < 40 {
                        return Err(SnapshotError::Truncated);
                    }
                    let mut dig = [0u8; 32];
                    dig.copy_from_slice(&f.payload[0..32]);
                    let expect = sha256(&body);
                    if expect != dig {
                        return Err(SnapshotError::DigestMismatch);
                    }
                    let image = SnapshotImage::decode(&body)?;
                    store.committed = Some(CommittedSnapshot {
                        seq: f.sequence,
                        image,
                        state_digest: StateDigest(dig),
                    });
                }
                _ => {}
            }
        }
        // Trailing body without commit = garbage, ignored (not ValidSnapshot).
        Ok(store)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn commit_and_recover_snapshot() {
        let mut wal = WalLog::new();
        let mut store = SnapshotStore::new();
        let image = SnapshotImage {
            logical_time: 7,
            next_actor_id: 3,
            next_effect_id: 5,
            wal_seq_covered: 0,
            budget_units: 100,
            escrow_units: 10,
            actors: vec![ActorSnap {
                id: 0,
                status: 0,
                pending_effect: u64::MAX,
                mailbox: b"m".to_vec(),
            }],
            authority_blob: b"auth".to_vec(),
            machine_blob: vec![],
        };
        store.begin(image.clone());
        let cs = store.commit_to_wal(&mut wal).unwrap();
        assert_eq!(cs.image.logical_time, 7);
        assert_eq!(cs.state_digest, image.state_digest());

        let frames = WalLog::parse_and_verify(&wal.encode_committed()).unwrap();
        let store2 = SnapshotStore::from_wal_frames(&frames).unwrap();
        let c2 = store2.committed().unwrap();
        assert_eq!(c2.image, image);
        assert_eq!(c2.image.reconstruct_runnable_queue(), vec![0]);
    }

    #[test]
    fn incomplete_begin_is_garbage() {
        let mut wal = WalLog::new();
        // Only body, no commit
        let image = SnapshotImage {
            logical_time: 1,
            ..SnapshotImage::default()
        };
        wal.append(WalKind::SnapshotBody, image.encode()).unwrap();
        wal.sync().unwrap();
        let frames = WalLog::parse_and_verify(&wal.encode_committed()).unwrap();
        let store = SnapshotStore::from_wal_frames(&frames).unwrap();
        assert!(store.committed().is_none());
    }
}
