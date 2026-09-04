//! Independent reference recovery model (R-RECOV-04 / R-REF-02).
//!
//! **Does not** import `ror-persistence`, `ror-runtime`, `ror-kernel`, or
//! `ror-host`. Reimplements WAL verify + T0–T6 classification over the same
//! provisional byte layout so differential tests can compare
//! `Canonical(Recover_P(D)) = Canonical(Recover_R(D))`.
//!
//! Layout must stay byte-compatible with production provisional codecs
//! (U-32/U-02 disclosed; OADs not closed).

use ror_core::digest::{sha256, EffectDigest, StateDigest};
use ror_core::types::EffectId;

/// Reference WAL magic / version — match production provisional constants.
const WAL_MAGIC: &[u8; 4] = b"RORW";
const WAL_VERSION: u8 = 1;
const CHECKSUM_SEED: [u8; 32] = [0u8; 32];

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
#[repr(u8)]
enum RefWalKind {
    Event = 1,
    EffectPrepared = 2,
    EffectIssued = 3,
    EffectCompleted = 4,
    EffectReconciled = 5,
    SnapshotCommit = 6,
    CapGranted = 7,
    CapDerived = 8,
    CapRevoked = 9,
    SnapshotBody = 10,
}

impl RefWalKind {
    fn from_u8(v: u8) -> Option<Self> {
        match v {
            1 => Some(Self::Event),
            2 => Some(Self::EffectPrepared),
            3 => Some(Self::EffectIssued),
            4 => Some(Self::EffectCompleted),
            5 => Some(Self::EffectReconciled),
            6 => Some(Self::SnapshotCommit),
            7 => Some(Self::CapGranted),
            8 => Some(Self::CapDerived),
            9 => Some(Self::CapRevoked),
            10 => Some(Self::SnapshotBody),
            _ => None,
        }
    }
}

fn frame_checksum(prev: &[u8; 32], seq: u64, kind: u8, payload: &[u8]) -> [u8; 32] {
    let mut buf = Vec::with_capacity(32 + 8 + 1 + payload.len());
    buf.extend_from_slice(prev);
    buf.extend_from_slice(&seq.to_be_bytes());
    buf.push(kind);
    buf.extend_from_slice(payload);
    sha256(&buf)
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub enum RefRecoveryFault {
    Truncated,
    BadMagic,
    BadVersion,
    BadKind,
    ChecksumMismatch,
    SequenceGap,
    SequenceRegression,
    DigestMismatch,
    IncompleteSnapshot,
    Invariant,
}

#[derive(Clone, Debug, PartialEq, Eq)]
struct RefFrame {
    seq: u64,
    kind: RefWalKind,
    payload: Vec<u8>,
    checksum: [u8; 32],
}

fn parse_frames(bytes: &[u8]) -> Result<Vec<RefFrame>, RefRecoveryFault> {
    let mut rest = bytes;
    let mut frames = Vec::new();
    let mut prev = CHECKSUM_SEED;
    let mut expect = 1u64;
    while !rest.is_empty() {
        if rest.len() < 4 + 1 + 8 + 1 + 4 + 32 {
            return Err(RefRecoveryFault::Truncated);
        }
        if &rest[0..4] != WAL_MAGIC {
            return Err(RefRecoveryFault::BadMagic);
        }
        if rest[4] != WAL_VERSION {
            return Err(RefRecoveryFault::BadVersion);
        }
        let seq = u64::from_be_bytes(rest[5..13].try_into().unwrap());
        let kind_b = rest[13];
        let kind = RefWalKind::from_u8(kind_b).ok_or(RefRecoveryFault::BadKind)?;
        let plen = u32::from_be_bytes(rest[14..18].try_into().unwrap()) as usize;
        let need = 18 + plen + 32;
        if rest.len() < need {
            return Err(RefRecoveryFault::Truncated);
        }
        let payload = rest[18..18 + plen].to_vec();
        let mut checksum = [0u8; 32];
        checksum.copy_from_slice(&rest[18 + plen..18 + plen + 32]);
        let expect_cs = frame_checksum(&prev, seq, kind_b, &payload);
        if expect_cs != checksum {
            return Err(RefRecoveryFault::ChecksumMismatch);
        }
        if seq != expect {
            if seq < expect {
                return Err(RefRecoveryFault::SequenceRegression);
            }
            return Err(RefRecoveryFault::SequenceGap);
        }
        prev = checksum;
        expect = seq + 1;
        frames.push(RefFrame {
            seq,
            kind,
            payload,
            checksum,
        });
        rest = &rest[need..];
    }
    Ok(frames)
}

/// Reference effect classification (independent of production enum).
#[derive(Clone, Debug, PartialEq, Eq)]
pub enum RefEffectClass {
    Discard {
        id: u64,
        digest: [u8; 32],
    },
    Indeterminate {
        id: u64,
        digest: [u8; 32],
        actor: u64,
    },
    Completed {
        id: u64,
        digest: [u8; 32],
        result_digest: [u8; 32],
        result_bytes: Vec<u8>,
    },
    Reconciled {
        id: u64,
        digest: [u8; 32],
        evidence_tag: u8,
    },
}

impl RefEffectClass {
    pub fn label(&self) -> &'static str {
        match self {
            Self::Discard { .. } => "discard",
            Self::Indeterminate { .. } => "indeterminate",
            Self::Completed { .. } => "completed",
            Self::Reconciled { .. } => "reconciled",
        }
    }
}

/// Canonical observation of recovery for differential compare.
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct RefRecoveryObservation {
    pub logical_time: u64,
    pub next_effect_id: u64,
    pub next_actor_id: u64,
    pub budget_units: u64,
    pub escrow_units: u64,
    pub runnable: Vec<u64>,
    pub effects: Vec<RefEffectClass>,
    pub revoked_caps: Vec<(u32, u32)>,
    pub snapshot_present: bool,
    pub complete: bool,
}

/// Independent recover over durable WAL bytes (R-RECOV-04).
pub fn ref_recover(wal_bytes: &[u8]) -> Result<RefRecoveryObservation, RefRecoveryFault> {
    let frames = parse_frames(wal_bytes)?;

    // Newest valid snapshot
    let mut snap_cover = 0u64;
    let mut logical_time = 0u64;
    let mut next_actor_id = 0u64;
    let mut next_effect_id = 0u64;
    let mut budget_units = 0u64;
    let mut escrow_units = 0u64;
    let mut actors: Vec<(u64, u8, u64)> = Vec::new(); // id, status, pending
    let mut snapshot_present = false;
    let mut pending_body: Option<Vec<u8>> = None;

    for f in &frames {
        match f.kind {
            RefWalKind::SnapshotBody => pending_body = Some(f.payload.clone()),
            RefWalKind::SnapshotCommit => {
                let body = pending_body
                    .take()
                    .ok_or(RefRecoveryFault::IncompleteSnapshot)?;
                if f.payload.len() < 40 {
                    return Err(RefRecoveryFault::Truncated);
                }
                let mut dig = [0u8; 32];
                dig.copy_from_slice(&f.payload[0..32]);
                if sha256(&body) != dig {
                    return Err(RefRecoveryFault::DigestMismatch);
                }
                let img = decode_snapshot(&body)?;
                logical_time = img.logical_time;
                next_actor_id = img.next_actor_id;
                next_effect_id = img.next_effect_id;
                snap_cover = img.wal_seq_covered;
                budget_units = img.budget_units;
                escrow_units = img.escrow_units;
                actors = img.actors;
                snapshot_present = true;
                let _ = StateDigest(dig); // documented
            }
            _ => {}
        }
    }

    // Classify all effect records (full journal)
    use std::collections::BTreeMap;
    #[derive(Default)]
    struct Acc {
        prepared: Option<([u8; 32], u64)>,
        issued: Option<([u8; 32], u64)>,
        completed: Option<([u8; 32], [u8; 32], Vec<u8>)>,
        reconciled: Option<([u8; 32], u8)>,
    }
    let mut map: BTreeMap<u64, Acc> = BTreeMap::new();
    let mut revoked = Vec::new();

    let mut max_actor_from_journal = 0u64;
    for f in &frames {
        match f.kind {
            RefWalKind::EffectPrepared => {
                let (id, actor, dig) = read_prep_iss(&f.payload)?;
                map.entry(id).or_default().prepared = Some((dig, actor));
                let next_a = actor.saturating_add(1);
                if next_a > max_actor_from_journal {
                    max_actor_from_journal = next_a;
                }
            }
            RefWalKind::EffectIssued => {
                let (id, actor, dig) = read_prep_iss(&f.payload)?;
                map.entry(id).or_default().issued = Some((dig, actor));
                let next_a = actor.saturating_add(1);
                if next_a > max_actor_from_journal {
                    max_actor_from_journal = next_a;
                }
            }
            RefWalKind::EffectCompleted => {
                let c = read_completed(&f.payload)?;
                map.entry(c.id).or_default().completed =
                    Some((c.digest, c.result_digest, c.result_bytes));
            }
            RefWalKind::EffectReconciled => {
                let (id, dig, tag) = read_reconciled(&f.payload)?;
                map.entry(id).or_default().reconciled = Some((dig, tag));
            }
            RefWalKind::CapGranted | RefWalKind::CapDerived => {
                // actor id at end of payload — best-effort bump
                if f.payload.len() >= 8 {
                    let actor =
                        u64::from_be_bytes(f.payload[f.payload.len() - 8..].try_into().unwrap());
                    let next_a = actor.saturating_add(1);
                    if next_a > max_actor_from_journal {
                        max_actor_from_journal = next_a;
                    }
                }
            }
            RefWalKind::CapRevoked => {
                if f.payload.len() >= 8 {
                    let idx = u32::from_be_bytes(f.payload[0..4].try_into().unwrap());
                    let gen = u32::from_be_bytes(f.payload[4..8].try_into().unwrap());
                    revoked.push((idx, gen));
                }
            }
            _ => {}
        }
        let _ = snap_cover; // coverage used when extending replay; classification is full-journal
    }
    if max_actor_from_journal > next_actor_id {
        next_actor_id = max_actor_from_journal;
    }

    let mut effects = Vec::new();
    for (id, acc) in map {
        if let Some((d, tag)) = acc.reconciled {
            effects.push(RefEffectClass::Reconciled {
                id,
                digest: d,
                evidence_tag: tag,
            });
            continue;
        }
        if let Some((d, rd, rb)) = acc.completed {
            effects.push(RefEffectClass::Completed {
                id,
                digest: d,
                result_digest: rd,
                result_bytes: rb,
            });
            continue;
        }
        if let Some((d, actor)) = acc.issued {
            effects.push(RefEffectClass::Indeterminate {
                id,
                digest: d,
                actor,
            });
            continue;
        }
        if let Some((d, _)) = acc.prepared {
            effects.push(RefEffectClass::Discard { id, digest: d });
        }
    }

    // Reconstruct counters
    for e in &effects {
        let id = match e {
            RefEffectClass::Discard { id, .. }
            | RefEffectClass::Indeterminate { id, .. }
            | RefEffectClass::Completed { id, .. }
            | RefEffectClass::Reconciled { id, .. } => *id,
        };
        let next = id.saturating_add(1);
        if next > next_effect_id {
            next_effect_id = next;
        }
    }
    for (aid, _, _) in &actors {
        let next = aid.saturating_add(1);
        if next > next_actor_id {
            next_actor_id = next;
        }
    }

    let mut runnable: Vec<u64> = actors
        .iter()
        .filter(|(_, st, _)| *st == 0)
        .map(|(id, _, _)| *id)
        .collect();
    runnable.sort_unstable();

    Ok(RefRecoveryObservation {
        logical_time,
        next_effect_id,
        next_actor_id,
        budget_units,
        escrow_units,
        runnable,
        effects,
        revoked_caps: revoked,
        snapshot_present,
        complete: true,
    })
}

/// Decoded snapshot counters + actor rows (id, status, pending_effect).
struct RefSnapDecoded {
    logical_time: u64,
    next_actor_id: u64,
    next_effect_id: u64,
    wal_seq_covered: u64,
    budget_units: u64,
    escrow_units: u64,
    actors: Vec<(u64, u8, u64)>,
}

/// Snapshot decode: matches production SnapshotImage::encode layout.
fn decode_snapshot(bytes: &[u8]) -> Result<RefSnapDecoded, RefRecoveryFault> {
    let mut off = 0usize;
    let take = |n: usize, off: &mut usize, bytes: &[u8]| -> Result<Vec<u8>, RefRecoveryFault> {
        if *off + n > bytes.len() {
            return Err(RefRecoveryFault::Truncated);
        }
        let s = bytes[*off..*off + n].to_vec();
        *off += n;
        Ok(s)
    };
    let logical_time = u64::from_be_bytes(take(8, &mut off, bytes)?.try_into().unwrap());
    let next_actor_id = u64::from_be_bytes(take(8, &mut off, bytes)?.try_into().unwrap());
    let next_effect_id = u64::from_be_bytes(take(8, &mut off, bytes)?.try_into().unwrap());
    let wal_seq_covered = u64::from_be_bytes(take(8, &mut off, bytes)?.try_into().unwrap());
    let budget_units = u64::from_be_bytes(take(8, &mut off, bytes)?.try_into().unwrap());
    let escrow_units = u64::from_be_bytes(take(8, &mut off, bytes)?.try_into().unwrap());
    let n = u32::from_be_bytes(take(4, &mut off, bytes)?.try_into().unwrap()) as usize;
    let mut actors = Vec::with_capacity(n);
    for _ in 0..n {
        let id = u64::from_be_bytes(take(8, &mut off, bytes)?.try_into().unwrap());
        let status = take(1, &mut off, bytes)?[0];
        let pending = u64::from_be_bytes(take(8, &mut off, bytes)?.try_into().unwrap());
        let mlen = u32::from_be_bytes(take(4, &mut off, bytes)?.try_into().unwrap()) as usize;
        let _ = take(mlen, &mut off, bytes)?;
        actors.push((id, status, pending));
    }
    // authority + machine blobs skipped for observation
    Ok(RefSnapDecoded {
        logical_time,
        next_actor_id,
        next_effect_id,
        wal_seq_covered,
        budget_units,
        escrow_units,
        actors,
    })
}

fn read_prep_iss(p: &[u8]) -> Result<(u64, u64, [u8; 32]), RefRecoveryFault> {
    if p.len() < 8 + 8 + 32 + 4 {
        return Err(RefRecoveryFault::Truncated);
    }
    let id = u64::from_be_bytes(p[0..8].try_into().unwrap());
    let actor = u64::from_be_bytes(p[8..16].try_into().unwrap());
    let mut dig = [0u8; 32];
    dig.copy_from_slice(&p[16..48]);
    Ok((id, actor, dig))
}

struct RefCompletedParts {
    id: u64,
    digest: [u8; 32],
    result_digest: [u8; 32],
    result_bytes: Vec<u8>,
}

fn read_completed(p: &[u8]) -> Result<RefCompletedParts, RefRecoveryFault> {
    if p.len() < 8 + 32 + 32 + 4 {
        return Err(RefRecoveryFault::Truncated);
    }
    let id = u64::from_be_bytes(p[0..8].try_into().unwrap());
    let mut dig = [0u8; 32];
    dig.copy_from_slice(&p[8..40]);
    let mut rdig = [0u8; 32];
    rdig.copy_from_slice(&p[40..72]);
    let blen = u32::from_be_bytes(p[72..76].try_into().unwrap()) as usize;
    if p.len() < 76 + blen {
        return Err(RefRecoveryFault::Truncated);
    }
    Ok(RefCompletedParts {
        id,
        digest: dig,
        result_digest: rdig,
        result_bytes: p[76..76 + blen].to_vec(),
    })
}

fn read_reconciled(p: &[u8]) -> Result<(u64, [u8; 32], u8), RefRecoveryFault> {
    if p.len() < 8 + 32 + 1 {
        return Err(RefRecoveryFault::Truncated);
    }
    let id = u64::from_be_bytes(p[0..8].try_into().unwrap());
    let mut dig = [0u8; 32];
    dig.copy_from_slice(&p[8..40]);
    let tag = p[40];
    Ok((id, dig, tag))
}

/// Helper: build EffectDigest observation id (for tests).
pub fn ref_effect_id(id: u64) -> EffectId {
    EffectId(id)
}

/// Helper digest.
pub fn ref_digest_of(bytes: &[u8]) -> EffectDigest {
    EffectDigest::of_bytes(bytes)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn empty_recover() {
        let r = ref_recover(&[]).unwrap();
        assert!(r.effects.is_empty());
        assert!(r.complete);
    }
}
