#![forbid(unsafe_code)]

//! Red-on-Rust core crate.
//!
//! M1 scope: frozen Phase-15A *data-domain* canonical serialization
//! (R-CANON-01…13) over the types the wire format names.
//!
//! **Not closed here:** machine-state encodings (U-02), unified machine vs
//! data `Value` (U-09), `Op`/`Target`/`Params` (U-21), and provisional ABI
//! questions U-29/U-30/U-37. Public items that touch those OADs are documented
//! as provisional—do not treat them as milestone-stable API.

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
