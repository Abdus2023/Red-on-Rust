//! WAL framing, sequence continuity, chained checksums (R-PERSIST-02/06/08).
//!
//! **U-32 OPEN:** frame field layout is **provisional** (5-field shape with
//! explicit `payload_len`). This does **not** close OAD U-32.

use ror_core::digest::sha256;

/// Monotonic WAL sequence number (R-PERSIST-02/06).
#[derive(Clone, Copy, Debug, PartialEq, Eq, PartialOrd, Ord, Hash, Default)]
pub struct WalSequence(pub u64);

impl WalSequence {
    pub const ZERO: Self = WalSequence(0);

    pub fn next(self) -> Self {
        WalSequence(self.0.saturating_add(1))
    }
}

/// WAL record kind tag (R-PERSIST-03 taxonomy; provisional numeric tags).
#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash)]
#[repr(u8)]
pub enum WalKind {
    Event = 1,
    EffectPrepared = 2,
    EffectIssued = 3,
    EffectCompleted = 4,
    EffectReconciled = 5,
    SnapshotCommit = 6,
    CapGranted = 7,
    CapDerived = 8,
    CapRevoked = 9,
    /// Snapshot payload body (paired with SnapshotCommit).
    SnapshotBody = 10,
}

impl WalKind {
    pub fn from_u8(v: u8) -> Option<Self> {
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

    pub fn as_u8(self) -> u8 {
        self as u8
    }
}

/// Provisional magic / version (U-32 / U-24 disclose).
pub const WAL_MAGIC: &[u8; 4] = b"RORW";
pub const WAL_VERSION: u8 = 1;

/// Chained checksum domain: `SHA-256(prev || seq_be || kind || payload)`.
/// Provisional under U-32 (checksum domain disputed in OAD).
pub fn frame_checksum(
    prev: &[u8; 32],
    seq: WalSequence,
    kind: WalKind,
    payload: &[u8],
) -> [u8; 32] {
    let mut buf = Vec::with_capacity(32 + 8 + 1 + payload.len());
    buf.extend_from_slice(prev);
    buf.extend_from_slice(&seq.0.to_be_bytes());
    buf.push(kind.as_u8());
    buf.extend_from_slice(payload);
    sha256(&buf)
}

/// Zero checksum seed (start of chain).
pub const CHECKSUM_SEED: [u8; 32] = [0u8; 32];

/// One WAL frame (R-PERSIST-02). Provisional 5-field layout (U-32).
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct WalFrame {
    pub sequence: WalSequence,
    pub kind: WalKind,
    pub payload: Vec<u8>,
    pub checksum: [u8; 32],
}

impl WalFrame {
    /// Build a frame with correct chained checksum.
    pub fn new(
        prev_checksum: &[u8; 32],
        sequence: WalSequence,
        kind: WalKind,
        payload: Vec<u8>,
    ) -> Self {
        let checksum = frame_checksum(prev_checksum, sequence, kind, &payload);
        Self {
            sequence,
            kind,
            payload,
            checksum,
        }
    }

    /// Encode frame bytes (provisional U-32 layout).
    ///
    /// ```text
    /// magic[4] | version[1] | seq[8 BE] | kind[1] | payload_len[4 BE] | payload | checksum[32]
    /// ```
    pub fn encode(&self) -> Vec<u8> {
        let mut out = Vec::with_capacity(4 + 1 + 8 + 1 + 4 + self.payload.len() + 32);
        out.extend_from_slice(WAL_MAGIC);
        out.push(WAL_VERSION);
        out.extend_from_slice(&self.sequence.0.to_be_bytes());
        out.push(self.kind.as_u8());
        let len = self.payload.len() as u32;
        out.extend_from_slice(&len.to_be_bytes());
        out.extend_from_slice(&self.payload);
        out.extend_from_slice(&self.checksum);
        out
    }

    /// Decode one frame from the front of `bytes`; returns frame + bytes consumed.
    pub fn decode_prefix(bytes: &[u8]) -> Result<(Self, usize), WalError> {
        if bytes.len() < 4 + 1 + 8 + 1 + 4 + 32 {
            return Err(WalError::Truncated);
        }
        if &bytes[0..4] != WAL_MAGIC {
            return Err(WalError::BadMagic);
        }
        if bytes[4] != WAL_VERSION {
            return Err(WalError::BadVersion);
        }
        let seq = u64::from_be_bytes(bytes[5..13].try_into().unwrap());
        let kind = WalKind::from_u8(bytes[13]).ok_or(WalError::BadKind)?;
        let plen = u32::from_be_bytes(bytes[14..18].try_into().unwrap()) as usize;
        let header: usize = 18;
        let need = header
            .checked_add(plen)
            .and_then(|n| n.checked_add(32))
            .ok_or(WalError::Overflow)?;
        if bytes.len() < need {
            return Err(WalError::Truncated);
        }
        let payload = bytes[header..header + plen].to_vec();
        let mut checksum = [0u8; 32];
        checksum.copy_from_slice(&bytes[header + plen..header + plen + 32]);
        Ok((
            Self {
                sequence: WalSequence(seq),
                kind,
                payload,
                checksum,
            },
            need,
        ))
    }

    /// Verify this frame's checksum against the previous chain value.
    pub fn verify_checksum(&self, prev: &[u8; 32]) -> Result<(), WalError> {
        let expect = frame_checksum(prev, self.sequence, self.kind, &self.payload);
        if expect != self.checksum {
            return Err(WalError::ChecksumMismatch);
        }
        Ok(())
    }
}

/// WAL / framing faults (R-PERSIST-02/06/08; R-CORE-10 — no silent repair).
#[derive(Clone, Debug, PartialEq, Eq)]
pub enum WalError {
    Truncated,
    BadMagic,
    BadVersion,
    BadKind,
    ChecksumMismatch,
    SequenceGap {
        expected: WalSequence,
        got: WalSequence,
    },
    SequenceRegression {
        last: WalSequence,
        got: WalSequence,
    },
    Overflow,
    Io,
}

/// In-memory WAL log with append + sync barrier (R-PERSIST-01 recording only).
#[derive(Clone, Debug)]
pub struct WalLog {
    /// Committed (synced) frames.
    frames: Vec<WalFrame>,
    /// Appended but not yet synced.
    pending: Vec<WalFrame>,
    /// Last committed checksum (or seed).
    last_checksum: [u8; 32],
    /// Checksum after last pending frame (for chaining pending).
    tip_checksum: [u8; 32],
    /// Next sequence to assign (1-based; first frame is 1).
    next_seq: WalSequence,
    fail_next_append: bool,
    fail_next_sync: bool,
}

impl Default for WalLog {
    fn default() -> Self {
        Self::new()
    }
}

impl WalLog {
    pub fn new() -> Self {
        Self {
            frames: Vec::new(),
            pending: Vec::new(),
            last_checksum: CHECKSUM_SEED,
            tip_checksum: CHECKSUM_SEED,
            next_seq: WalSequence(1),
            fail_next_append: false,
            fail_next_sync: false,
        }
    }

    pub fn fail_next_append(&mut self) {
        self.fail_next_append = true;
    }

    pub fn fail_next_sync(&mut self) {
        self.fail_next_sync = true;
    }

    pub fn committed_frames(&self) -> &[WalFrame] {
        &self.frames
    }

    pub fn pending_frames(&self) -> &[WalFrame] {
        &self.pending
    }

    pub fn last_committed_seq(&self) -> Option<WalSequence> {
        self.frames.last().map(|f| f.sequence)
    }

    pub fn tip_checksum(&self) -> [u8; 32] {
        self.tip_checksum
    }

    pub fn last_checksum(&self) -> [u8; 32] {
        self.last_checksum
    }

    /// Append a framed record. Sequence assigned monotonically.
    pub fn append(&mut self, kind: WalKind, payload: Vec<u8>) -> Result<WalSequence, WalError> {
        if self.fail_next_append {
            self.fail_next_append = false;
            return Err(WalError::Io);
        }
        let seq = self.next_seq;
        let frame = WalFrame::new(&self.tip_checksum, seq, kind, payload);
        self.tip_checksum = frame.checksum;
        self.next_seq = seq.next();
        self.pending.push(frame);
        Ok(seq)
    }

    /// Sync barrier: commit pending frames (R-DUR-02 style).
    pub fn sync(&mut self) -> Result<(), WalError> {
        if self.fail_next_sync {
            self.fail_next_sync = false;
            return Err(WalError::Io);
        }
        if let Some(last) = self.pending.last() {
            self.last_checksum = last.checksum;
        }
        self.frames.append(&mut self.pending);
        Ok(())
    }

    /// Discard unsynced pending (crash simulation: only durable survives).
    pub fn crash_discard_pending(&mut self) {
        self.pending.clear();
        self.tip_checksum = self.last_checksum;
        // next_seq stays — recovery reconstructs from durable frames.
        if let Some(last) = self.frames.last() {
            self.next_seq = last.sequence.next();
            self.tip_checksum = last.checksum;
            self.last_checksum = last.checksum;
        } else {
            self.next_seq = WalSequence(1);
            self.tip_checksum = CHECKSUM_SEED;
            self.last_checksum = CHECKSUM_SEED;
        }
    }

    /// Encode all committed frames to a byte stream.
    pub fn encode_committed(&self) -> Vec<u8> {
        let mut out = Vec::new();
        for f in &self.frames {
            out.extend_from_slice(&f.encode());
        }
        out
    }

    /// Parse and verify a committed byte stream (full integrity check).
    pub fn parse_and_verify(bytes: &[u8]) -> Result<Vec<WalFrame>, WalError> {
        let mut rest = bytes;
        let mut frames = Vec::new();
        let mut prev = CHECKSUM_SEED;
        let mut expect_seq = WalSequence(1);
        while !rest.is_empty() {
            let (frame, n) = WalFrame::decode_prefix(rest)?;
            frame.verify_checksum(&prev)?;
            if frame.sequence != expect_seq {
                if frame.sequence.0 < expect_seq.0 {
                    return Err(WalError::SequenceRegression {
                        last: WalSequence(expect_seq.0.saturating_sub(1)),
                        got: frame.sequence,
                    });
                }
                return Err(WalError::SequenceGap {
                    expected: expect_seq,
                    got: frame.sequence,
                });
            }
            prev = frame.checksum;
            expect_seq = frame.sequence.next();
            frames.push(frame);
            rest = &rest[n..];
        }
        Ok(frames)
    }

    /// Rebuild WalLog state from verified committed frames.
    pub fn from_verified_frames(frames: Vec<WalFrame>) -> Self {
        let mut log = Self::new();
        if let Some(last) = frames.last() {
            log.last_checksum = last.checksum;
            log.tip_checksum = last.checksum;
            log.next_seq = last.sequence.next();
        }
        log.frames = frames;
        log
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn frame_round_trip() {
        let f = WalFrame::new(
            &CHECKSUM_SEED,
            WalSequence(1),
            WalKind::Event,
            b"hello".to_vec(),
        );
        let enc = f.encode();
        let (dec, n) = WalFrame::decode_prefix(&enc).unwrap();
        assert_eq!(n, enc.len());
        assert_eq!(dec, f);
        dec.verify_checksum(&CHECKSUM_SEED).unwrap();
    }

    #[test]
    fn chain_and_gap_detection() {
        let mut log = WalLog::new();
        log.append(WalKind::Event, b"a".to_vec()).unwrap();
        log.append(WalKind::Event, b"b".to_vec()).unwrap();
        log.sync().unwrap();
        let bytes = log.encode_committed();
        let frames = WalLog::parse_and_verify(&bytes).unwrap();
        assert_eq!(frames.len(), 2);

        // Corrupt checksum
        let mut bad = bytes.clone();
        let last = bad.len() - 1;
        bad[last] ^= 0xff;
        assert_eq!(
            WalLog::parse_and_verify(&bad).unwrap_err(),
            WalError::ChecksumMismatch
        );
    }

    #[test]
    fn sequence_regression_rejected() {
        let f1 = WalFrame::new(
            &CHECKSUM_SEED,
            WalSequence(1),
            WalKind::Event,
            b"a".to_vec(),
        );
        let f2 = WalFrame::new(&f1.checksum, WalSequence(1), WalKind::Event, b"b".to_vec()); // same seq
        let mut bytes = f1.encode();
        bytes.extend_from_slice(&f2.encode());
        let err = WalLog::parse_and_verify(&bytes).unwrap_err();
        assert!(matches!(
            err,
            WalError::SequenceRegression { .. } | WalError::SequenceGap { .. }
        ));
    }

    #[test]
    fn verify_checksum_detects_tamper() {
        // M016 oracle: tampered checksum must fail verify_checksum.
        let f = WalFrame::new(
            &CHECKSUM_SEED,
            WalSequence(1),
            WalKind::Event,
            b"x".to_vec(),
        );
        assert!(f.verify_checksum(&CHECKSUM_SEED).is_ok());
        let mut bad = f.clone();
        bad.checksum[0] ^= 0xff;
        assert!(bad.verify_checksum(&CHECKSUM_SEED).is_err());
    }
}
