//! Effect domain types (R-CALC-04/05) — M5 surface.
//!
//! **U-21 OPEN:** `Op`/`Target`/`Params` use provisional representations.
//! **U-08 OPEN:** host/persistence fault labels used by callers are provisional.
//!
//! Canonical identity: `EffectDigest = SHA-256(canonical_bytes(effect))` (R-CANON-09).

use crate::capability::{LogicalTime, Op};
use crate::digest::EffectDigest;
use crate::types::{ActorId, CapRef, EffectId};

/// Consumable resource vector component (R-BUDGET thin / R-CALC-05).
#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash, Default)]
pub struct Consumable {
    pub units: u64,
}

impl Consumable {
    pub const ZERO: Consumable = Consumable { units: 0 };

    pub fn new(units: u64) -> Self {
        Self { units }
    }

    pub fn checked_add(self, other: Self) -> Option<Self> {
        self.units.checked_add(other.units).map(Consumable::new)
    }

    pub fn saturating_leq(self, other: Self) -> bool {
        self.units <= other.units
    }
}

/// Reserved capacity component (R-CALC-05).
#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash, Default)]
pub struct Reserved {
    pub slots: u64,
}

impl Reserved {
    pub const ZERO: Reserved = Reserved { slots: 0 };

    pub fn new(slots: u64) -> Self {
        Self { slots }
    }
}

/// Effect cost triple (R-CALC-05).
#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash)]
pub struct EffectCost {
    pub issue: Consumable,
    pub complete_max: Consumable,
    pub reserve: Reserved,
}

impl EffectCost {
    pub fn new(issue: u64, complete_max: u64, reserve: u64) -> Self {
        Self {
            issue: Consumable::new(issue),
            complete_max: Consumable::new(complete_max),
            reserve: Reserved::new(reserve),
        }
    }

    pub fn zero() -> Self {
        Self::new(0, 0, 0)
    }

    /// Gate-8 affordability: issue + complete_max (R-EFFECT-05).
    pub fn issue_plus_complete_max(&self) -> Option<Consumable> {
        self.issue.checked_add(self.complete_max)
    }
}

/// Provisional target (U-21): finite target id.
#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash, Ord, PartialOrd)]
pub struct Target(pub u32);

/// Provisional params (U-21): ordered param tags.
#[derive(Clone, Debug, PartialEq, Eq, Hash, Default)]
pub struct Params(pub Vec<u32>);

impl Params {
    pub fn empty() -> Self {
        Self(Vec::new())
    }

    pub fn from_tags(tags: Vec<u32>) -> Self {
        Self(tags)
    }

    pub fn tags(&self) -> &[u32] {
        &self.0
    }

    pub fn primary_tag(&self) -> u32 {
        self.0.first().copied().unwrap_or(0)
    }
}

/// Immutable effect descriptor (R-CALC-04).
#[derive(Clone, Debug, PartialEq, Eq, Hash)]
pub struct Effect {
    pub capability: CapRef,
    pub operation: Op,
    pub target: Target,
    pub params: Params,
    pub cost: EffectCost,
}

impl Effect {
    pub fn new(
        capability: CapRef,
        operation: Op,
        target: Target,
        params: Params,
        cost: EffectCost,
    ) -> Self {
        Self {
            capability,
            operation,
            target,
            params,
            cost,
        }
    }

    /// Canonical effect bytes (deterministic; not full 15A envelope — M5 fixed layout).
    ///
    /// Layout (big-endian):
    /// `cap.index u32 | cap.generation u32 | op u8 | target u32 |
    ///  param_count u32 | params… u32 | issue u64 | complete_max u64 | reserve u64`
    ///
    /// Single grammar for digest/journal (R-CANON-13 direction). Not an alternate
    /// host codec — host receives the same bytes.
    pub fn canonical_bytes(&self) -> Vec<u8> {
        let mut out = Vec::with_capacity(48 + self.params.0.len() * 4);
        out.extend_from_slice(&self.capability.index().to_be_bytes());
        out.extend_from_slice(&self.capability.generation().to_be_bytes());
        out.push(op_tag(self.operation));
        out.extend_from_slice(&self.target.0.to_be_bytes());
        out.extend_from_slice(&(self.params.0.len() as u32).to_be_bytes());
        for t in &self.params.0 {
            out.extend_from_slice(&t.to_be_bytes());
        }
        out.extend_from_slice(&self.cost.issue.units.to_be_bytes());
        out.extend_from_slice(&self.cost.complete_max.units.to_be_bytes());
        out.extend_from_slice(&self.cost.reserve.slots.to_be_bytes());
        out
    }

    pub fn digest(&self) -> EffectDigest {
        EffectDigest::of_bytes(&self.canonical_bytes())
    }

    /// Map to capability algebra effect descriptor (R-CAP-06).
    pub fn to_desc(&self) -> crate::capability::EffectDesc {
        crate::capability::EffectDesc {
            op: self.operation,
            target: self.target.0,
            param_tag: self.params.primary_tag(),
            cost_units: self
                .cost
                .issue
                .units
                .saturating_add(self.cost.complete_max.units),
        }
    }
}

fn op_tag(op: Op) -> u8 {
    match op {
        Op::FileRead => 0,
        Op::NetSend => 1,
        Op::FileWrite => 2,
    }
}

pub fn op_from_tag(tag: u8) -> Option<Op> {
    match tag {
        0 => Some(Op::FileRead),
        1 => Some(Op::NetSend),
        2 => Some(Op::FileWrite),
        _ => None,
    }
}

pub fn op_from_i64(n: i64) -> Option<Op> {
    if !(0..=255).contains(&n) {
        return None;
    }
    op_from_tag(n as u8)
}

/// Thin runtime budget for Request gates (R-BUDGET thin M5).
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct ThinBudget {
    pub available: Consumable,
    pub reserved: Reserved,
    /// Absolute logical deadline `W` (`None` = ∞).
    pub deadline: Option<LogicalTime>,
}

impl ThinBudget {
    pub fn generous() -> Self {
        Self {
            available: Consumable::new(u64::MAX / 4),
            reserved: Reserved::new(u64::MAX / 4),
            deadline: None,
        }
    }

    pub fn with_available(units: u64) -> Self {
        Self {
            available: Consumable::new(units),
            reserved: Reserved::new(1024),
            deadline: None,
        }
    }
}

/// Host-facing issued effect request (R-DUR-02 step 7). No Authority internals.
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct EffectRequest {
    pub id: EffectId,
    pub actor: ActorId,
    pub digest: EffectDigest,
    pub effect_bytes: Vec<u8>,
    pub cost: EffectCost,
    pub effect: Effect,
}

/// Durable issuance record kinds (R-DUR-06) — semantic, not full WAL framing.
#[derive(Clone, Debug, PartialEq, Eq)]
pub enum IssuanceRecord {
    Prepared {
        id: EffectId,
        actor: ActorId,
        digest: EffectDigest,
        effect_bytes: Vec<u8>,
        cost: EffectCost,
    },
    Issued {
        id: EffectId,
        actor: ActorId,
        digest: EffectDigest,
        effect_bytes: Vec<u8>,
        cost: EffectCost,
    },
    Completed {
        id: EffectId,
        digest: EffectDigest,
        result_digest: EffectDigest,
        /// Canonical data-domain result encoded as bytes (or empty on unit).
        result_bytes: Vec<u8>,
    },
}

/// Effect receipt from host (R-EFFECT-06 shape, thin).
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct EffectReceipt {
    pub id: EffectId,
    pub effect_digest: EffectDigest,
    pub result: Result<ReceiptValue, HostFaultCode>,
}

/// Admitted receipt payload — data only (R-EFFECT-08). No Capability/Function.
#[derive(Clone, Debug, PartialEq, Eq)]
pub enum ReceiptValue {
    Unit,
    Bool(bool),
    Integer(i64),
    String(String),
    Bytes(Vec<u8>),
}

impl ReceiptValue {
    pub fn canonical_bytes(&self) -> Vec<u8> {
        match self {
            ReceiptValue::Unit => vec![0x00],
            ReceiptValue::Bool(b) => vec![0x01, if *b { 1 } else { 0 }],
            ReceiptValue::Integer(n) => {
                let mut v = vec![0x02];
                v.extend_from_slice(&n.to_be_bytes());
                v
            }
            ReceiptValue::String(s) => {
                let mut v = vec![0x03];
                v.extend_from_slice(&(s.len() as u32).to_be_bytes());
                v.extend_from_slice(s.as_bytes());
                v
            }
            ReceiptValue::Bytes(b) => {
                let mut v = vec![0x04];
                v.extend_from_slice(&(b.len() as u32).to_be_bytes());
                v.extend_from_slice(b);
                v
            }
        }
    }

    pub fn digest(&self) -> EffectDigest {
        EffectDigest::of_bytes(&self.canonical_bytes())
    }
}

/// Opaque host fault code (R-CORE-13: no debug text in machine values).
#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash)]
pub struct HostFaultCode(pub u32);

impl HostFaultCode {
    pub const POLICY_DENIED: HostFaultCode = HostFaultCode(1);
    pub const EXECUTION_FAILED: HostFaultCode = HostFaultCode(2);
}

/// Monotonic EffectId allocator (R-EFFECT-03).
#[derive(Clone, Debug, Default)]
pub struct EffectIdAlloc {
    next: u64,
}

impl EffectIdAlloc {
    pub fn new() -> Self {
        Self { next: 0 }
    }

    pub fn with_start(start: u64) -> Self {
        Self { next: start }
    }

    pub fn allocate(&mut self) -> EffectId {
        let id = EffectId(self.next);
        self.next = self.next.saturating_add(1);
        id
    }

    pub fn peek_next(&self) -> u64 {
        self.next
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::types::CapRef;

    #[test]
    fn digest_deterministic() {
        let e = Effect::new(
            CapRef::from_kernel_parts(1, 0),
            Op::FileRead,
            Target(7),
            Params::from_tags(vec![1, 2]),
            EffectCost::new(1, 2, 0),
        );
        assert_eq!(e.digest(), e.digest());
        let mut e2 = e.clone();
        e2.target = Target(8);
        assert_ne!(e.digest(), e2.digest());
    }

    #[test]
    fn effect_id_monotonic() {
        let mut a = EffectIdAlloc::new();
        assert_eq!(a.allocate(), EffectId(0));
        assert_eq!(a.allocate(), EffectId(1));
        assert_eq!(a.allocate(), EffectId(2));
    }

    #[test]
    fn issue_plus_complete() {
        let c = EffectCost::new(3, 5, 0);
        assert_eq!(c.issue_plus_complete_max().unwrap().units, 8);
    }
}
