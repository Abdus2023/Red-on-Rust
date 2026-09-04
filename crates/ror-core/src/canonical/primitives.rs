//! Standalone primitive codecs (R-CANON-03/05).
//!
//! Note on bool / i64 / String standalone tags (`0x10` / `0x11` / `0x13`):
//! R-CANON-03 marks the "revised grammar" listing of these as *stale* for
//! standalone envelopes of `Value`. They remain the payload-helper tags used
//! *inside* a `Value` envelope (and match the frozen Phase-15A sketch). They
//! are never advertised as standalone Value tags.

use super::codec::{
    checked_length, CanonicalDecode, CanonicalEncode, CanonicalPayload, ReadCursor,
};
use super::error::CanonicalError;
use crate::types::{ActorId, CapRef, EffectId, Symbol};

/// Standalone envelope tags (R-CANON-03) — the single `TAG_*` namespace (R-CANON-13).
pub const TAG_VALUE: u8 = 0x00;
pub const TAG_SYMBOL: u8 = 0x20;
pub const TAG_CAP_REF: u8 = 0x30;
pub const TAG_ACTOR_ID: u8 = 0x40;
pub const TAG_EFFECT_ID: u8 = 0x41;

// --- bool (Value-internal helper tag 0x10; not a standalone Value tag) ---

impl CanonicalPayload for bool {
    const TYPE_TAG: u8 = 0x10;

    fn encode_payload(&self, out: &mut Vec<u8>) -> Result<(), CanonicalError> {
        out.push(if *self { 0x01 } else { 0x00 });
        Ok(())
    }

    fn decode_payload(cursor: &mut ReadCursor<'_>) -> Result<Self, CanonicalError> {
        match cursor.read_byte()? {
            0x00 => Ok(false),
            0x01 => Ok(true),
            found => Err(CanonicalError::InvalidBoolValue { found }),
        }
    }
}
impl CanonicalEncode for bool {}
impl CanonicalDecode for bool {}

// --- i64 (Value-internal helper tag 0x11) ---

impl CanonicalPayload for i64 {
    const TYPE_TAG: u8 = 0x11;

    fn encode_payload(&self, out: &mut Vec<u8>) -> Result<(), CanonicalError> {
        out.extend_from_slice(&self.to_be_bytes());
        Ok(())
    }

    fn decode_payload(cursor: &mut ReadCursor<'_>) -> Result<Self, CanonicalError> {
        cursor.read_i64_be()
    }
}
impl CanonicalEncode for i64 {}
impl CanonicalDecode for i64 {}

// --- String (Value-internal helper tag 0x13) ---

impl CanonicalPayload for String {
    const TYPE_TAG: u8 = 0x13;

    fn encode_payload(&self, out: &mut Vec<u8>) -> Result<(), CanonicalError> {
        let len = checked_length(self.len())?;
        out.extend_from_slice(&len.to_be_bytes());
        out.extend_from_slice(self.as_bytes());
        Ok(())
    }

    fn decode_payload(cursor: &mut ReadCursor<'_>) -> Result<Self, CanonicalError> {
        let str_len = cursor.read_u32_be()? as usize;
        let str_bytes = cursor.read_bytes(str_len)?;
        String::from_utf8(str_bytes.to_vec()).map_err(|_| CanonicalError::InvalidUtf8)
    }
}
impl CanonicalEncode for String {}
impl CanonicalDecode for String {}

// --- Symbol (standalone tag 0x20) ---

impl CanonicalPayload for Symbol {
    const TYPE_TAG: u8 = TAG_SYMBOL;

    fn encode_payload(&self, out: &mut Vec<u8>) -> Result<(), CanonicalError> {
        out.extend_from_slice(&self.0.to_be_bytes());
        Ok(())
    }

    fn decode_payload(cursor: &mut ReadCursor<'_>) -> Result<Self, CanonicalError> {
        Ok(Symbol(cursor.read_u32_be()?))
    }
}
impl CanonicalEncode for Symbol {}
impl CanonicalDecode for Symbol {}

// --- ActorId (standalone tag 0x40) ---

impl CanonicalPayload for ActorId {
    const TYPE_TAG: u8 = TAG_ACTOR_ID;

    fn encode_payload(&self, out: &mut Vec<u8>) -> Result<(), CanonicalError> {
        out.extend_from_slice(&self.0.to_be_bytes());
        Ok(())
    }

    fn decode_payload(cursor: &mut ReadCursor<'_>) -> Result<Self, CanonicalError> {
        Ok(ActorId(cursor.read_u64_be()?))
    }
}
impl CanonicalEncode for ActorId {}
impl CanonicalDecode for ActorId {}

// --- EffectId (standalone tag 0x41) ---

impl CanonicalPayload for EffectId {
    const TYPE_TAG: u8 = TAG_EFFECT_ID;

    fn encode_payload(&self, out: &mut Vec<u8>) -> Result<(), CanonicalError> {
        out.extend_from_slice(&self.0.to_be_bytes());
        Ok(())
    }

    fn decode_payload(cursor: &mut ReadCursor<'_>) -> Result<Self, CanonicalError> {
        Ok(EffectId(cursor.read_u64_be()?))
    }
}
impl CanonicalEncode for EffectId {}
impl CanonicalDecode for EffectId {}

// --- CapRef (standalone tag 0x30) ---
//
// Kernel-mediated codec path only. The data decoder rejects this tag
// (R-CANON-12). The payload layout itself is frozen by R-CANON-05.

impl CanonicalPayload for CapRef {
    const TYPE_TAG: u8 = TAG_CAP_REF;

    fn encode_payload(&self, out: &mut Vec<u8>) -> Result<(), CanonicalError> {
        out.extend_from_slice(&self.index().to_be_bytes());
        out.extend_from_slice(&self.generation().to_be_bytes());
        Ok(())
    }

    fn decode_payload(cursor: &mut ReadCursor<'_>) -> Result<Self, CanonicalError> {
        let index = cursor.read_u32_be()?;
        let generation = cursor.read_u32_be()?;
        // Kernel-mediated path only (R-CANON-12 / R-KERN-01). Bits ≠ authority.
        Ok(CapRef::from_kernel_parts(index, generation))
    }
}
impl CanonicalEncode for CapRef {}
impl CanonicalDecode for CapRef {}
