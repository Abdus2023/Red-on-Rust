//! Independent reference capability algebra (REQ-REF-023 / REQ-REF-024).
//!
//! **R-SCOPE-04 / R-REF-02:** this module does **not** import `ror-kernel` or
//! `ror-runtime`. It reimplements derive / valid / revoke / ≼ over its own
//! `RefAuthority` types. Shared shells from `ror-core` (Op, Scope, …) are the
//! semantic domain vocabulary — algorithms are authored here independently.

use std::collections::{BTreeMap, BTreeSet};

use ror_core::capability::{
    admissible_constraint_wrt_parent, Authority, Constraint, Lifetime, LogicalTime, Op,
    OpAuthority, ParamConstraint, ResourceLimit, Scope,
};
use ror_core::machine::Fault;
use ror_core::types::CapRef;

/// Reference operation authority (REQ-REF-023). Parallel to production OpAuthority.
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct RefOpAuthority {
    pub scope: Scope,
    pub params: ParamConstraint,
    pub resources: ResourceLimit,
    pub lifetime: Lifetime,
}

impl RefOpAuthority {
    pub fn from_core(o: &OpAuthority) -> Self {
        Self {
            scope: o.scope.clone(),
            params: o.params,
            resources: o.resources,
            lifetime: o.lifetime,
        }
    }

    pub fn to_core(&self) -> OpAuthority {
        OpAuthority {
            scope: self.scope.clone(),
            params: self.params,
            resources: self.resources,
            lifetime: self.lifetime,
        }
    }

    fn leq(&self, other: &Self) -> bool {
        self.scope.leq(&other.scope)
            && self.params.leq(&other.params)
            && self.resources.leq(&other.resources)
            && self.lifetime.leq(&other.lifetime)
    }

    fn meet(&self, other: &Self) -> Option<Self> {
        let lifetime = self.lifetime.meet(&other.lifetime)?;
        Some(Self {
            scope: self.scope.meet(&other.scope),
            params: self.params.meet(&other.params),
            resources: self.resources.meet(&other.resources),
            lifetime,
        })
    }
}

/// Reference authority map (REQ-REF-023).
#[derive(Clone, Debug, PartialEq, Eq, Default)]
pub struct RefAuthority {
    ops: BTreeMap<Op, RefOpAuthority>,
}

impl RefAuthority {
    pub fn empty() -> Self {
        Self {
            ops: BTreeMap::new(),
        }
    }

    pub fn from_core(a: &Authority) -> Self {
        let mut ops = BTreeMap::new();
        for (op, oa) in a.ops() {
            ops.insert(*op, RefOpAuthority::from_core(oa));
        }
        Self { ops }
    }

    pub fn to_core(&self) -> Authority {
        let mut a = Authority::empty();
        for (op, oa) in &self.ops {
            a.insert(*op, oa.to_core());
        }
        a
    }

    pub fn insert(&mut self, op: Op, auth: RefOpAuthority) {
        self.ops.insert(op, auth);
    }

    pub fn get(&self, op: Op) -> Option<&RefOpAuthority> {
        self.ops.get(&op)
    }

    /// Independent ≼ (R-CAP-03).
    pub fn leq(&self, other: &Self) -> bool {
        self.ops
            .iter()
            .all(|(op, a)| other.ops.get(op).map(|b| a.leq(b)).unwrap_or(false))
    }

    /// Independent derive meet (R-CAP-05).
    pub fn derive_meet(&self, constraint: &Constraint) -> RefAuthority {
        let mut out = BTreeMap::new();
        for (op, a_op) in &self.ops {
            if let Some(c_op) = constraint.ops.get(op) {
                let c_ref = RefOpAuthority::from_core(c_op);
                if let Some(m) = a_op.meet(&c_ref) {
                    out.insert(*op, m);
                }
            }
        }
        RefAuthority { ops: out }
    }
}

struct RefNode {
    authority: RefAuthority,
    parent: Option<CapRef>,
    generation: u32,
    live: bool,
    lifetime: Lifetime,
}

/// Reference capability store (REQ-REF-024).
pub struct RefCapabilityStore {
    slots: Vec<Option<RefNode>>,
    next_generation: Vec<u32>,
    revocation_set: BTreeSet<(u32, u32)>,
    free: Vec<u32>,
}

impl Default for RefCapabilityStore {
    fn default() -> Self {
        Self::new()
    }
}

impl RefCapabilityStore {
    pub fn new() -> Self {
        Self {
            slots: Vec::new(),
            next_generation: Vec::new(),
            revocation_set: BTreeSet::new(),
            free: Vec::new(),
        }
    }

    pub fn grant_root(&mut self, authority: RefAuthority, lifetime: Lifetime) -> CapRef {
        self.insert(RefNode {
            authority,
            parent: None,
            generation: 0,
            live: true,
            lifetime,
        })
    }

    pub fn grant_root_from_core(&mut self, authority: &Authority, lifetime: Lifetime) -> CapRef {
        self.grant_root(RefAuthority::from_core(authority), lifetime)
    }

    fn insert(&mut self, mut node: RefNode) -> CapRef {
        let index = if let Some(i) = self.free.pop() {
            i
        } else {
            let i = self.slots.len() as u32;
            self.slots.push(None);
            self.next_generation.push(0);
            i
        };
        let gen = self.next_generation[index as usize];
        node.generation = gen;
        self.slots[index as usize] = Some(node);
        CapRef::from_kernel_parts(index, gen)
    }

    fn resolve(&self, cap: CapRef) -> Result<&RefNode, Fault> {
        let idx = cap.index() as usize;
        let node = self
            .slots
            .get(idx)
            .and_then(|s| s.as_ref())
            .ok_or(Fault::CapabilityRevoked)?;
        if node.generation != cap.generation() {
            return Err(Fault::CapabilityRevoked);
        }
        Ok(node)
    }

    pub fn valid(&self, cap: CapRef, t: LogicalTime) -> bool {
        self.valid_result(cap, t).is_ok()
    }

    pub fn valid_result(&self, cap: CapRef, t: LogicalTime) -> Result<(), Fault> {
        let node = self.resolve(cap)?;
        if !node.live
            || self
                .revocation_set
                .contains(&(cap.index(), cap.generation()))
        {
            return Err(Fault::CapabilityRevoked);
        }
        if !node.lifetime.contains(t) {
            return Err(Fault::CapabilityRevoked);
        }
        let mut parent = node.parent;
        while let Some(p) = parent {
            let pnode = self.resolve(p)?;
            if !pnode.live || self.revocation_set.contains(&(p.index(), p.generation())) {
                return Err(Fault::CapabilityRevoked);
            }
            parent = pnode.parent;
        }
        Ok(())
    }

    pub fn revoke(&mut self, cap: CapRef) -> Result<(), Fault> {
        let idx = cap.index() as usize;
        let node = self
            .slots
            .get_mut(idx)
            .and_then(|s| s.as_mut())
            .ok_or(Fault::CapabilityRevoked)?;
        if node.generation != cap.generation() {
            return Err(Fault::CapabilityRevoked);
        }
        node.live = false;
        self.revocation_set.insert((cap.index(), cap.generation()));
        Ok(())
    }

    pub fn derive(
        &mut self,
        parent: CapRef,
        constraint: &Constraint,
        t: LogicalTime,
    ) -> Result<CapRef, Fault> {
        self.valid_result(parent, t)?;
        let parent_node = self.resolve(parent)?;
        let parent_auth_core = parent_node.authority.to_core();
        let parent_lifetime = parent_node.lifetime;
        let parent_auth = parent_node.authority.clone();

        if !admissible_constraint_wrt_parent(constraint, &parent_auth_core) {
            return Err(Fault::InvalidConstraint);
        }

        let child_auth = parent_auth.derive_meet(constraint);
        debug_assert!(child_auth.leq(&parent_auth));

        let mut child_lt = parent_lifetime;
        for c_op in constraint.ops.values() {
            match child_lt.meet(&c_op.lifetime) {
                Some(m) => child_lt = m,
                None => return Err(Fault::InvalidConstraint),
            }
        }
        for a_op in child_auth.ops.values() {
            if let Some(m) = child_lt.meet(&a_op.lifetime) {
                child_lt = m;
            }
        }
        if !child_lt.contains(t) {
            return Err(Fault::CapabilityRevoked);
        }

        Ok(self.insert(RefNode {
            authority: child_auth,
            parent: Some(parent),
            generation: 0,
            live: true,
            lifetime: child_lt,
        }))
    }

    pub fn authority_snapshot(&self, cap: CapRef) -> Option<RefAuthority> {
        self.resolve(cap).ok().map(|n| n.authority.clone())
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use ror_core::capability::{Lifetime, LogicalTime, Op};

    fn auth_file(targets: Vec<u32>, units: u64) -> RefAuthority {
        let mut a = RefAuthority::empty();
        a.insert(
            Op::FileRead,
            RefOpAuthority {
                scope: Scope::from_targets(targets),
                params: ParamConstraint::any(),
                resources: ResourceLimit::new(units),
                lifetime: Lifetime::always(),
            },
        );
        a
    }

    fn cons_file(targets: Vec<u32>, units: u64) -> Constraint {
        let mut c = Constraint::empty();
        c.insert(
            Op::FileRead,
            OpAuthority {
                scope: Scope::from_targets(targets),
                params: ParamConstraint::any(),
                resources: ResourceLimit::new(units),
                lifetime: Lifetime::always(),
            },
        );
        c
    }

    #[test]
    fn ref_no_amplification() {
        let mut s = RefCapabilityStore::new();
        let p = s.grant_root(auth_file(vec![1, 2, 3], 100), Lifetime::always());
        let child = s
            .derive(p, &cons_file(vec![1], 10), LogicalTime::ZERO)
            .unwrap();
        let ca = s.authority_snapshot(child).unwrap();
        let pa = s.authority_snapshot(p).unwrap();
        assert!(ca.leq(&pa));
    }

    #[test]
    fn ref_revoke_cascade() {
        let mut s = RefCapabilityStore::new();
        let root = s.grant_root(auth_file(vec![1], 10), Lifetime::always());
        let c = cons_file(vec![1], 5);
        let child = s.derive(root, &c, LogicalTime::ZERO).unwrap();
        let grand = s.derive(child, &c, LogicalTime::ZERO).unwrap();
        let sib = s.derive(root, &c, LogicalTime::ZERO).unwrap();
        s.revoke(child).unwrap();
        assert!(!s.valid(grand, LogicalTime::ZERO));
        assert!(s.valid(sib, LogicalTime::ZERO));
    }
}
