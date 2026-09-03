//! Canonical decode/encode errors (R-CANON-07, R-CANON-06, R-CANON-12).
//!
//! **Provisional shape (U-29 OPEN).** R-CANON-07 names the required rejection
//! *set*; several source sketches disagree on unit vs struct variants and on
//! exact payload fields. This enum follows the final Phase-15A sketch plus the
//! addendum variants `DuplicateMapKey` and `CapabilityInData`. It is **not** a
//! resolution of U-29's broader fault-surface question and may be reshaped
//! when that decision closes—callers must match on semantics, not treat the
//! Rust shape as a frozen ABI.

/// Explicit rejection outcomes for the 15A decoder/encoder (provisional ABI).
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
