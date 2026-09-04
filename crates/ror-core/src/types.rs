//! Phase 15A *data-domain* types for canonical serialization.
//!
//! **Provisional public surface (U-09).** The name `Value` here denotes the
//! 15A canonical data-domain enum (8 variants incl. `Map`), **not** the machine
//! value domain of R-CALC-01 (11 variants incl. `Function`/`Tuple`/`Bytes`).
//! U-09 remains OPEN: this type must not be treated as the final unified
//! machine/canonical value identity. Downstream crates should prefer the
//! explicit data-codec entry points (`encode_data` / `decode_data_value`) over
//! assuming a stable cross-domain `Value` API.
//!
//! Wire layouts for `Symbol` / `CapRef` / `ActorId` / `EffectId` follow
//! R-CANON-03/05 (frozen). Integer field widths on the wire are `u32`/`u64`/`i64`
//! as named by those requirements; U-37 remains OPEN for *semantic* quantities
//! outside this codec.
//!
//! **M4 CapRef opacity (R-KERN-01):** fields are private. Forming a bit-pattern
//! does not grant authority — only a live arena entry validated by the kernel
//! does. The sole constructors are kernel mint and the kernel-mediated codec.

use std::collections::BTreeMap;

/// Runtime symbol identity (`R-CALC-03` / R-CANON-05): `u32`, big-endian on the wire.
#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash, Ord, PartialOrd)]
pub struct Symbol(pub u32);

/// Opaque capability reference (R-KERN-01 / R-CANON-05).
///
/// Standalone envelope tag `0x30`. The *data* decoder rejects this tag
/// (R-CANON-12); only the kernel-mediated codec path may produce or consume it.
///
/// Fields are **private**. There is no public free constructor for untrusted
/// code. Kernel mint uses [`CapRef::from_kernel_parts`]; the codec uses the
/// same path (kernel-mediated). Bits alone never imply authority.
#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash)]
pub struct CapRef {
    index: u32,
    generation: u32,
}

impl CapRef {
    /// Kernel / kernel-mediated codec construction (R-KERN-01, R-CANON-12).
    ///
    /// **Not** an untrusted mint API: forming bits does not create authority.
    /// Ordinary evaluation must obtain CapRefs only via kernel `grant`/`derive`.
    pub fn from_kernel_parts(index: u32, generation: u32) -> Self {
        Self { index, generation }
    }

    pub fn index(&self) -> u32 {
        self.index
    }

    pub fn generation(&self) -> u32 {
        self.generation
    }
}

/// Actor identity payload: `u64` big-endian (R-CANON-05), tag `0x40`.
///
/// **R-ACTOR-03:** allocated by monotonic counter only. Bits ≠ authority.
/// **No reuse** of terminated ids (M6 preflight: do not implement recycling).
#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash, Ord, PartialOrd)]
pub struct ActorId(pub u64);

/// Monotonic ActorId allocator (R-ACTOR-03). No wall-clock / random / reuse.
#[derive(Clone, Debug, Default)]
pub struct ActorIdAlloc {
    next: u64,
}

impl ActorIdAlloc {
    pub fn new() -> Self {
        Self { next: 0 }
    }

    pub fn with_start(start: u64) -> Self {
        Self { next: start }
    }

    pub fn allocate(&mut self) -> ActorId {
        let id = ActorId(self.next);
        self.next = self.next.saturating_add(1);
        id
    }

    pub fn peek_next(&self) -> u64 {
        self.next
    }
}

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
