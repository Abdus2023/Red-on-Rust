//! Canonical decode/encode errors (R-CANON-07, R-CANON-06, R-CANON-12).
//!
//! The frozen Phase-15A sketch enumerates the structural set. Two later
//! addenda extend it without reopening U-29's broader fault-surface question:
//! - `DuplicateMapKey` (R-CANON-06 injectivity patch)
//! - `CapabilityInData` (R-CANON-12 decode-side authority ban)

/// Explicit rejection outcomes for the 15A decoder/encoder.
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum CanonicalError {
    InvalidVersion {
        expected: u8,
        found: u8,
    },
    InvalidTypeTag {
        expected: u8,
        found: u8,
    },
    /// Payload byte count did not match the envelope length header, or an
    /// internal length field was inconsistent with available bytes.
    LengthMismatch {
        expected: usize,
        found: usize,
    },
    LengthOverflow,
    InvalidUtf8,
    UnexpectedEof,
    TrailingBytes {
        count: usize,
    },
    InvalidDiscriminant {
        found: u8,
    },
    InvalidBoolValue {
        found: u8,
    },
    /// Map decode saw the same key twice (R-CANON-06).
    DuplicateMapKey,
    /// Data codec saw a capability payload (R-CANON-12).
    CapabilityInData,
}
