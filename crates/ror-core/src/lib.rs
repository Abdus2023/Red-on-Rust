#![forbid(unsafe_code)]

//! Red-on-Rust core crate.
//!
//! - **M1:** Phase-15A *data-domain* canonical serialization (R-CANON-01…13).
//! - **M2:** machine-domain types for pure CEK ([`machine`]) — R-CALC-01/02/03.
//!
//! **U-09:** [`types::Value`] (data domain) and [`machine::Value`] (machine domain)
//! are deliberately distinct. There is no collapsing conversion.
//!
//! **Not closed:** machine-state encodings (U-02), unified Value (U-09),
//! `Op`/`Target`/`Params` (U-21), provisional ABI U-29/U-30/U-37.

pub mod canonical;
pub mod digest;
pub mod machine;
pub mod types;

pub use canonical::{
    checked_length, contains_capability, decode_cap_ref_kernel, decode_data_value,
    encode_cap_ref_kernel, encode_data, encode_data_value, envelope, round_trip_data,
    CanonicalDecode, CanonicalEncode, CanonicalError, CanonicalPayload, ReadCursor,
    CANONICAL_VERSION, TAG_ACTOR_ID, TAG_CAP_REF, TAG_EFFECT_ID, TAG_SYMBOL, TAG_VALUE,
};
pub use digest::{sha256, Digest, EffectDigest, StateDigest};
pub use machine::{Environment, Expr, Fault, FunctionValue};
/// Data-domain `Value` (Phase 15A). For machine values use [`machine::Value`].
pub use types::{ActorId, CapRef, EffectId, Symbol, Value};
