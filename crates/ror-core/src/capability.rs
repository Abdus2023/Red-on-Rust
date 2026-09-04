//! Capability algebra **domain types** (MOD-01 / R-CAP-*).
//!
//! These are semantic shells shared by production kernel and (via independent
//! reimplementation) the reference model. **Authority storage and minting live
//! only in `ror-kernel`** (R-KERN-01…03). This module does **not** mint CapRefs.
//!
//! **Provisional representations (U-21 / U-31 OPEN):** concrete `Op`, scope,
//! param, and resource field sets are test-domain enums sufficient to exercise
//! meet/order/Valid/derive. Not a claim that U-21 or U-31 is closed.
//!
//! **AdmissibleConstraint:** runtime law is **R-CAP-10** (frozen). REQ-CAP-024 /
//! AMB-12 remain registry-ambiguous; frozen addendum governs implementation.

use std::collections::BTreeMap;

use crate::types::CapRef;

/// Explicit logical time (R-CAP-09 / R-CAP-11). Never wall-clock.
#[derive(Clone, Copy, Debug, PartialEq, Eq, PartialOrd, Ord, Hash, Default)]
pub struct LogicalTime(pub u64);

impl LogicalTime {
    pub const ZERO: LogicalTime = LogicalTime(0);

    pub fn new(t: u64) -> Self {
        LogicalTime(t)
    }

    pub fn get(self) -> u64 {
        self.0
    }
}

/// Lifetime interval over logical time (R-CAP-11): half-open `[start, end)`.
#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash)]
pub struct Lifetime {
    pub start: LogicalTime,
    pub end: LogicalTime,
}

impl Lifetime {
    pub fn new(start: LogicalTime, end: LogicalTime) -> Self {
        Self { start, end }
    }

    /// Unbounded-from-zero placeholder for tests: `[0, u64::MAX)`.
    pub fn always() -> Self {
        Self {
            start: LogicalTime(0),
            end: LogicalTime(u64::MAX),
        }
    }

    /// `contains(t) ⇔ start ≤ t ∧ t < end` (R-CAP-11).
    pub fn contains(&self, t: LogicalTime) -> bool {
        self.start <= t && t < self.end
    }

    /// Subset order: `T₁ ≼ T₂ ⇔ T₁ ⊆ T₂` as intervals (REQ-CAP-005).
    pub fn leq(&self, other: &Self) -> bool {
        self.start >= other.start && self.end <= other.end
    }

    /// Interval intersection meet. Empty meet ⇒ `None` (unsatisfiable).
    pub fn meet(&self, other: &Self) -> Option<Self> {
        let start = self.start.max(other.start);
        let end = self.end.min(other.end);
        if start < end {
            Some(Self { start, end })
        } else {
            None
        }
    }
}

/// Provisional operation identity (U-21 OPEN). Finite enumerable set (REQ-CAP-001).
#[derive(Clone, Copy, Debug, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub enum Op {
    /// Illustrative FileRead-class op (REQ-CAP-001 examples are non-normative labels).
    FileRead,
    /// Illustrative NetSend-class op.
    NetSend,
    /// Illustrative FileWrite-class op.
    FileWrite,
}

/// Provisional scope: finite set of target tags (U-21).
///
/// Order: `S₁ ≼ S₂ ⇔ ⟦S₁⟧ ⊆ ⟦S₂⟧` (REQ-CAP-002).
#[derive(Clone, Debug, PartialEq, Eq, Hash)]
pub struct Scope {
    /// Sorted unique target ids for determinism.
    targets: Vec<u32>,
}

impl Scope {
    pub fn empty() -> Self {
        Self {
            targets: Vec::new(),
        }
    }

    pub fn from_targets(mut targets: Vec<u32>) -> Self {
        targets.sort_unstable();
        targets.dedup();
        Self { targets }
    }

    pub fn targets(&self) -> &[u32] {
        &self.targets
    }

    pub fn contains_target(&self, t: u32) -> bool {
        self.targets.binary_search(&t).is_ok()
    }

    pub fn leq(&self, other: &Self) -> bool {
        self.targets
            .iter()
            .all(|t| other.targets.binary_search(t).is_ok())
    }

    pub fn meet(&self, other: &Self) -> Self {
        let mut out = Vec::new();
        for t in &self.targets {
            if other.targets.binary_search(t).is_ok() {
                out.push(*t);
            }
        }
        Self { targets: out }
    }
}

/// Provisional param predicate (U-21): max allowed param tag, inclusive.
///
/// Order by implication: narrower max is stronger (REQ-CAP-003).
/// `Q₁ ≼ Q₂ ⇔ ∀p. Q₁(p) ⇒ Q₂(p)` ≈ `max₁ ≤ max₂`.
#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash)]
pub struct ParamConstraint {
    pub max_tag: u32,
}

impl ParamConstraint {
    pub fn any() -> Self {
        Self { max_tag: u32::MAX }
    }

    pub fn at_most(max_tag: u32) -> Self {
        Self { max_tag }
    }

    pub fn satisfies(&self, tag: u32) -> bool {
        tag <= self.max_tag
    }

    pub fn leq(&self, other: &Self) -> bool {
        self.max_tag <= other.max_tag
    }

    pub fn meet(&self, other: &Self) -> Self {
        Self {
            max_tag: self.max_tag.min(other.max_tag),
        }
    }
}

/// Provisional resource ceiling (U-21): single consumable units (REQ-CAP-004).
#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash)]
pub struct ResourceLimit {
    pub units: u64,
}

impl ResourceLimit {
    pub fn new(units: u64) -> Self {
        Self { units }
    }

    pub fn leq(&self, other: &Self) -> bool {
        self.units <= other.units
    }

    pub fn meet(&self, other: &Self) -> Self {
        Self {
            units: self.units.min(other.units),
        }
    }
}

/// Per-operation authority component `⟨S, Q, R, T⟩` (R-CAP-01/02).
#[derive(Clone, Debug, PartialEq, Eq, Hash)]
pub struct OpAuthority {
    pub scope: Scope,
    pub params: ParamConstraint,
    pub resources: ResourceLimit,
    pub lifetime: Lifetime,
}

impl OpAuthority {
    pub fn leq(&self, other: &Self) -> bool {
        self.scope.leq(&other.scope)
            && self.params.leq(&other.params)
            && self.resources.leq(&other.resources)
            && self.lifetime.leq(&other.lifetime)
    }

    /// Meet of two op-authorities. Unsatisfiable lifetime ⇒ `None`.
    pub fn meet(&self, other: &Self) -> Option<Self> {
        let lifetime = self.lifetime.meet(&other.lifetime)?;
        Some(Self {
            scope: self.scope.meet(&other.scope),
            params: self.params.meet(&other.params),
            resources: self.resources.meet(&other.resources),
            lifetime,
        })
    }
}

/// Operation-indexed authority (R-CAP-02). Deterministic map: `BTreeMap`.
#[derive(Clone, Debug, PartialEq, Eq, Hash, Default)]
pub struct Authority {
    ops: BTreeMap<Op, OpAuthority>,
}

impl Authority {
    pub fn empty() -> Self {
        Self {
            ops: BTreeMap::new(),
        }
    }

    pub fn from_ops(ops: BTreeMap<Op, OpAuthority>) -> Self {
        Self { ops }
    }

    pub fn insert(&mut self, op: Op, auth: OpAuthority) {
        self.ops.insert(op, auth);
    }

    pub fn get(&self, op: Op) -> Option<&OpAuthority> {
        self.ops.get(&op)
    }

    pub fn ops(&self) -> &BTreeMap<Op, OpAuthority> {
        &self.ops
    }

    /// `A₁ ≼ A₂` (R-CAP-03 / REQ-CAP-007).
    pub fn leq(&self, other: &Self) -> bool {
        self.ops
            .iter()
            .all(|(op, a)| other.ops.get(op).map(|b| a.leq(b)).unwrap_or(false))
    }

    /// Algebraic derive on authorities (R-CAP-05): meet on `O_A ∩ O_C`.
    ///
    /// Returns `None` if every op meet is empty (no residual authority). Empty
    /// residual is still a valid mathematical result as empty Authority — use
    /// [`derive_authority`] which always yields an Authority (possibly empty).
    pub fn derive_authority(&self, constraint: &Constraint) -> Authority {
        let mut out = BTreeMap::new();
        for (op, a_op) in &self.ops {
            if let Some(c_op) = constraint.ops.get(op) {
                if let Some(m) = a_op.meet(c_op) {
                    // Scope may be empty after meet — still a valid residual grant
                    // for that op (authorize will fail on targets). Keep the op.
                    out.insert(*op, m);
                }
            }
        }
        Authority { ops: out }
    }
}

/// Constraint: request to narrow a grant (R-CAP-04). Distinct from Authority.
#[derive(Clone, Debug, PartialEq, Eq, Hash, Default)]
pub struct Constraint {
    pub ops: BTreeMap<Op, OpAuthority>,
}

impl Constraint {
    pub fn empty() -> Self {
        Self {
            ops: BTreeMap::new(),
        }
    }

    pub fn from_ops(ops: BTreeMap<Op, OpAuthority>) -> Self {
        Self { ops }
    }

    pub fn insert(&mut self, op: Op, auth: OpAuthority) {
        self.ops.insert(op, auth);
    }

    /// Constraint order for monotonicity tests (REQ-CAP-026):
    /// `C₁ ≼ C₂` when C₁ is pointwise ≤ C₂ on shared ops and ops(C₁) ⊆ ops(C₂).
    pub fn leq(&self, other: &Self) -> bool {
        self.ops
            .iter()
            .all(|(op, a)| other.ops.get(op).map(|b| a.leq(b)).unwrap_or(false))
    }
}

/// R-CAP-10 `AdmissibleConstraint`: decidable well-formedness.
///
/// - `O` nonempty
/// - each `O` entry's scope is interpretable (always true for our finite sets)
/// - `Q` closed over params (always true for max_tag form)
/// - resource ceiling present (always)
/// - lifetime is a satisfiable interval (`start < end`)
///
/// Parent-relative checks (O within parent, R within parent, …) are applied at
/// derive time against the parent authority (R-CAP-10 "within the parent's").
pub fn admissible_constraint_shape(c: &Constraint) -> bool {
    if c.ops.is_empty() {
        return false;
    }
    for op_auth in c.ops.values() {
        if op_auth.lifetime.start >= op_auth.lifetime.end {
            return false;
        }
        // Scope interpretable: finite target list always ok.
        // Q closed: max_tag form always closed.
    }
    true
}

/// Parent-relative admissibility (R-CAP-10): O ⊆ parent ops interpretation,
/// R within parent ceilings, etc. Shape must already hold.
pub fn admissible_constraint_wrt_parent(c: &Constraint, parent: &Authority) -> bool {
    if !admissible_constraint_shape(c) {
        return false;
    }
    for (op, c_op) in &c.ops {
        let Some(p_op) = parent.get(*op) else {
            // Op outside parent interpretation ⇒ inadmissible (cannot amplify
            // by inventing ops — intersection would drop them, but R-CAP-10
            // requires O within parent's interpretation).
            return false;
        };
        // Resource ceiling within parent.
        if !c_op.resources.leq(&p_op.resources) {
            // Constraint may request a *narrower* R (leq parent) — that's fine.
            // "within the parent's" means C.R should not exceed parent.R.
            // leq means c.units <= p.units — if false, C asks for more units → inadmissible.
            return false;
        }
        // Lifetime must be a sub-interval of parent for admissibility intent.
        // R-CAP-10: T a satisfiable interval; meet handles residual. We require
        // C.T intersects parent.T so derive is defined on something live.
        if c_op.lifetime.meet(&p_op.lifetime).is_none() {
            return false;
        }
        // Scope: C.S should be ⊆ parent.S (interpretable under parent).
        if !c_op.scope.leq(&p_op.scope) {
            return false;
        }
        // Params: C.Q should imply under parent (narrower or equal).
        if !c_op.params.leq(&p_op.params) {
            return false;
        }
    }
    true
}

/// Static effect descriptor fragment for algebra-level `Authorized` tests (R-CAP-06).
/// Full Effect CEK is M5 — this is the pure predicate only.
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct EffectDesc {
    pub op: Op,
    pub target: u32,
    pub param_tag: u32,
    pub cost_units: u64,
}

/// Canonical authorization predicate (R-CAP-06) — algebra only, not Request CEK.
pub fn authorized(authority: &Authority, effect: &EffectDesc, t: LogicalTime) -> bool {
    let Some(op_auth) = authority.get(effect.op) else {
        return false;
    };
    op_auth.scope.contains_target(effect.target)
        && op_auth.params.satisfies(effect.param_tag)
        && effect.cost_units <= op_auth.resources.units
        && op_auth.lifetime.contains(t)
}

/// Thin possession map (R-KERN-05 direction). Not durable; not multi-actor runtime.
#[derive(Clone, Debug, PartialEq, Eq, Default)]
pub struct CapabilityContext {
    /// Ordered slots for determinism.
    slots: Vec<CapRef>,
}

impl CapabilityContext {
    pub fn empty() -> Self {
        Self { slots: Vec::new() }
    }

    pub fn insert(&mut self, cap: CapRef) {
        if !self.slots.iter().any(|c| c == &cap) {
            self.slots.push(cap);
        }
    }

    pub fn contains(&self, cap: CapRef) -> bool {
        self.slots.contains(&cap)
    }

    pub fn slots(&self) -> &[CapRef] {
        &self.slots
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn full_op(op: Op, targets: Vec<u32>, units: u64) -> (Op, OpAuthority) {
        (
            op,
            OpAuthority {
                scope: Scope::from_targets(targets),
                params: ParamConstraint::any(),
                resources: ResourceLimit::new(units),
                lifetime: Lifetime::always(),
            },
        )
    }

    #[test]
    fn lifetime_half_open() {
        let lt = Lifetime::new(LogicalTime(10), LogicalTime(20));
        assert!(lt.contains(LogicalTime(10)));
        assert!(lt.contains(LogicalTime(19)));
        assert!(!lt.contains(LogicalTime(20)));
        assert!(!lt.contains(LogicalTime(9)));
    }

    #[test]
    fn derive_no_amplification() {
        let mut a = Authority::empty();
        let (op, auth) = full_op(Op::FileRead, vec![1, 2, 3], 100);
        a.insert(op, auth);
        let mut c = Constraint::empty();
        c.insert(
            Op::FileRead,
            OpAuthority {
                scope: Scope::from_targets(vec![1]),
                params: ParamConstraint::at_most(5),
                resources: ResourceLimit::new(10),
                lifetime: Lifetime::always(),
            },
        );
        let d = a.derive_authority(&c);
        assert!(d.leq(&a));
        assert!(!a.leq(&d) || a == d); // derived is strictly smaller usually
        let d_op = d.get(Op::FileRead).unwrap();
        assert_eq!(d_op.scope.targets(), &[1]);
        assert_eq!(d_op.resources.units, 10);
    }

    #[test]
    fn empty_constraint_not_admissible() {
        assert!(!admissible_constraint_shape(&Constraint::empty()));
    }
}
