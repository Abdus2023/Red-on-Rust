//! Envelope framing, cursor, and encode/decode traits (R-CANON-02/07/08).

use super::error::CanonicalError;

/// Envelope version byte (R-CANON-02 / R-CANON-13). Currently `0x01`.
pub const CANONICAL_VERSION: u8 = 0x01;

/// How a type interprets its payload bytes (no framing).
pub trait CanonicalPayload: Sized {
    /// Standalone envelope type tag for this type (R-CANON-03).
    const TYPE_TAG: u8;

    fn encode_payload(&self, out: &mut Vec<u8>) -> Result<(), CanonicalError>;

    fn decode_payload(cursor: &mut ReadCursor<'_>) -> Result<Self, CanonicalError>;
}

/// Wraps a payload in a canonical envelope (R-CANON-02).
pub trait CanonicalEncode: CanonicalPayload {
    fn encode_canonical(&self) -> Result<Vec<u8>, CanonicalError> {
        let mut payload = Vec::new();
        self.encode_payload(&mut payload)?;
        envelope(Self::TYPE_TAG, &payload)
    }
}

/// Validates envelope framing, then decodes the payload (R-CANON-07).
pub trait CanonicalDecode: CanonicalPayload {
    fn decode_canonical(bytes: &[u8]) -> Result<Self, CanonicalError> {
        let mut cursor = ReadCursor::new(bytes);

        // (1)(2)(3) version / tag / exact length via read_envelope_payload
        let payload_slice = cursor.read_envelope_payload(Self::TYPE_TAG)?;
        // (5) trailing-byte rejection after the outer envelope
        cursor.expect_eof()?;

        // (4) payload well-formedness on a fresh bounded cursor
        let mut payload_cursor = ReadCursor::new(payload_slice);
        let val = Self::decode_payload(&mut payload_cursor)?;
        payload_cursor.expect_eof()?;

        Ok(val)
    }
}

/// Bounded read cursor over a byte slice (R-CANON-08).
#[derive(Debug)]
pub struct ReadCursor<'a> {
    bytes: &'a [u8],
    pos: usize,
}

impl<'a> ReadCursor<'a> {
    pub fn new(bytes: &'a [u8]) -> Self {
        Self { bytes, pos: 0 }
    }

    pub fn remaining(&self) -> usize {
        self.bytes.len().saturating_sub(self.pos)
    }

    pub fn position(&self) -> usize {
        self.pos
    }

    pub fn read_byte(&mut self) -> Result<u8, CanonicalError> {
        if self.pos >= self.bytes.len() {
            return Err(CanonicalError::UnexpectedEof);
        }
        let b = self.bytes[self.pos];
        self.pos += 1;
        Ok(b)
    }

    pub fn read_bytes(&mut self, n: usize) -> Result<&'a [u8], CanonicalError> {
        let end = self
            .pos
            .checked_add(n)
            .ok_or(CanonicalError::UnexpectedEof)?;
        if end > self.bytes.len() {
            return Err(CanonicalError::UnexpectedEof);
        }
        let slice = &self.bytes[self.pos..end];
        self.pos = end;
        Ok(slice)
    }

    pub fn read_u32_be(&mut self) -> Result<u32, CanonicalError> {
        let bytes = self.read_bytes(4)?;
        Ok(u32::from_be_bytes([bytes[0], bytes[1], bytes[2], bytes[3]]))
    }

    pub fn read_u64_be(&mut self) -> Result<u64, CanonicalError> {
        let bytes = self.read_bytes(8)?;
        Ok(u64::from_be_bytes([
            bytes[0], bytes[1], bytes[2], bytes[3], bytes[4], bytes[5], bytes[6], bytes[7],
        ]))
    }

    pub fn read_i64_be(&mut self) -> Result<i64, CanonicalError> {
        let bytes = self.read_bytes(8)?;
        Ok(i64::from_be_bytes([
            bytes[0], bytes[1], bytes[2], bytes[3], bytes[4], bytes[5], bytes[6], bytes[7],
        ]))
    }

    /// Consume `version | tag | length | payload` and return the payload slice.
    /// Leaves the cursor positioned immediately after the payload.
    pub fn read_envelope_payload(&mut self, expected_tag: u8) -> Result<&'a [u8], CanonicalError> {
        let version = self.read_byte()?;
        if version != CANONICAL_VERSION {
            return Err(CanonicalError::InvalidVersion {
                expected: CANONICAL_VERSION,
                found: version,
            });
        }

        let tag = self.read_byte()?;
        if tag != expected_tag {
            return Err(CanonicalError::InvalidTypeTag {
                expected: expected_tag,
                found: tag,
            });
        }

        let length = self.read_u32_be()? as usize;
        self.read_bytes(length)
    }

    /// Peek the next type tag without consuming (used by data-decode to reject
    /// standalone CapRef envelopes under R-CANON-12).
    pub fn peek_byte(&self) -> Result<u8, CanonicalError> {
        if self.pos >= self.bytes.len() {
            return Err(CanonicalError::UnexpectedEof);
        }
        Ok(self.bytes[self.pos])
    }

    pub fn expect_eof(&self) -> Result<(), CanonicalError> {
        if self.pos < self.bytes.len() {
            Err(CanonicalError::TrailingBytes {
                count: self.bytes.len() - self.pos,
            })
        } else {
            Ok(())
        }
    }
}

/// Build a complete envelope: `version | tag | len_be | payload` (R-CANON-02/08).
pub fn envelope(type_tag: u8, payload: &[u8]) -> Result<Vec<u8>, CanonicalError> {
    let length = u32::try_from(payload.len()).map_err(|_| CanonicalError::LengthOverflow)?;
    let capacity = 6usize
        .checked_add(payload.len())
        .ok_or(CanonicalError::LengthOverflow)?;

    let mut bytes = Vec::with_capacity(capacity);
    bytes.push(CANONICAL_VERSION);
    bytes.push(type_tag);
    bytes.extend_from_slice(&length.to_be_bytes());
    bytes.extend_from_slice(payload);
    Ok(bytes)
}

/// Checked `usize → u32` for collection/string lengths (R-CANON-08).
pub fn checked_length(len: usize) -> Result<u32, CanonicalError> {
    u32::try_from(len).map_err(|_| CanonicalError::LengthOverflow)
}
