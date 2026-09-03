#![forbid(unsafe_code)]

//! Red-on-Rust core crate.
//!
//! M1 scope: frozen Phase-15A canonical serialization (R-CANON-01…13) over the
//! data-domain types that the wire format names. Machine-state encodings (U-02),
//! full machine `Value` domains beyond the canonical data domain (U-09), and
//! kernel-mediated capability codec paths remain out of scope.

pub mod canonical;
pub mod digest;
pub mod types;

pub use canonical::{
    checked_length, contains_capability, decode_cap_ref_kernel, decode_data_value,
    encode_cap_ref_kernel, encode_data, encode_data_value, envelope, round_trip_data,
    CanonicalDecode, CanonicalEncode, CanonicalError, CanonicalPayload, ReadCursor,
    CANONICAL_VERSION, TAG_ACTOR_ID, TAG_CAP_REF, TAG_EFFECT_ID, TAG_SYMBOL, TAG_VALUE,
};
pub use digest::{sha256, Digest, EffectDigest, StateDigest};
pub use types::{ActorId, CapRef, EffectId, Symbol, Value};
