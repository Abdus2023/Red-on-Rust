//! Frozen data-domain types for Phase 15A canonical serialization.
//!
//! These are the types named by R-CANON-03/05 and the frozen `Value` enum of
//! Phase 15A. They are deliberately the *canonical data domain*, not the full
//! machine `Value` domain (U-09 remains open for machine-side extensions).

use std::collections::BTreeMap;

/// Runtime symbol identity (`R-CALC-03` / R-CANON-05): `u32`, big-endian on the wire.
#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash, Ord, PartialOrd)]
pub struct Symbol(pub u32);

/// Opaque capability reference payload shape (R-CANON-05).
///
/// Standalone envelope tag `0x30`. The *data* decoder rejects this tag
/// (R-CANON-12); only the kernel-mediated codec path may produce or consume it.
#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash)]
pub struct CapRef {
    pub index: u32,
    pub generation: u32,
}

/// Actor identity payload: `u64` big-endian (R-CANON-05), tag `0x40`.
#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash, Ord, PartialOrd)]
pub struct ActorId(pub u64);

/// Effect identity payload: `u64` big-endian (R-CANON-05), tag `0x41`.
#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash, Ord, PartialOrd)]
pub struct EffectId(pub u64);

/// Canonical data-domain `Value` (Phase 15A frozen enum).
///
/// Discriminants (R-CANON-04):
/// `Unit 0x00`, `Bool 0x01`, `Integer 0x02`, `String 0x03`,
/// `Symbol 0x04`, `Capability 0x05`, `List 0x06`, `Map 0x07`.
///
/// The data codec path rejects `Capability` on decode (R-CANON-12). Encoding of
/// `Capability` is retained only so the kernel-mediated path can share the
/// payload layout; callers of the data codec must not emit it.
#[derive(Clone, Debug, PartialEq, Eq)]
pub enum Value {
    Unit,
    Bool(bool),
    Integer(i64),
    String(String),
    Symbol(Symbol),
    Capability(CapRef),
    List(Vec<Value>),
    Map(BTreeMap<Symbol, Value>),
}

impl Value {
    /// Value-payload discriminants (explicit stable constants; R-CANON-04/07).
    pub const TAG_UNIT: u8 = 0x00;
    pub const TAG_BOOL: u8 = 0x01;
    pub const TAG_INTEGER: u8 = 0x02;
    pub const TAG_STRING: u8 = 0x03;
    pub const TAG_SYMBOL: u8 = 0x04;
    pub const TAG_CAPABILITY: u8 = 0x05;
    pub const TAG_LIST: u8 = 0x06;
    pub const TAG_MAP: u8 = 0x07;
}
