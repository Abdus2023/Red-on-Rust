//! Phase 15A canonical serialization (R-CANON-01…13).
//!
//! One grammar only (R-CANON-13): big-endian universal envelope
//! `version u8 / type_tag u8 / payload_length u32 BE / payload`.
//! Nested values are complete envelopes (R-CANON-04).
//!
//! Open decisions deliberately *not* closed here (M0-A PARTIALLY IMPLEMENTABLE):
//! U-02 (machine-state encodings), U-09 (machine vs data `Value`), U-24/U-25
//! (already resolved in the security direction by R-CANON-13; constants follow
//! the 15A TAG_* namespace), U-29 (error shape — unit/struct variants taken from
//! the frozen Phase-15A sketch plus `DuplicateMapKey` and `CapabilityInData`),
//! U-37 (integer widths — wire widths are frozen; Rust field widths follow the
//! sketch's `u32`/`u64`/`i64`).

mod codec;
mod data_decode;
mod error;
mod primitives;
mod value;

#[cfg(test)]
mod vectors_test;

pub use codec::{
    checked_length, envelope, CanonicalDecode, CanonicalEncode, CanonicalPayload, ReadCursor,
    CANONICAL_VERSION,
};
pub use data_decode::{
    decode_cap_ref_kernel, decode_data_value, encode_cap_ref_kernel, encode_data, round_trip_data,
};
pub use error::CanonicalError;
pub use primitives::{TAG_ACTOR_ID, TAG_CAP_REF, TAG_EFFECT_ID, TAG_SYMBOL, TAG_VALUE};
pub use value::{contains_capability, encode_data_value};
