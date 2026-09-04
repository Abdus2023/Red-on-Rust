#![forbid(unsafe_code)]

//! Capability kernel (MOD-03 / R-KERN-*).
//!
//! Sole authority storage and CapRef mint path. Evaluator holds only opaque
//! [`CapRef`] handles (REQ-KERN-006/009).
//!
//! **M4 surface:** derive, revoke, valid, leq-via-authority, root grant for
//! tests/deployment init. No Request CEK, no WAL, no actors (M5–M7).

use std::collections::BTreeSet;

use ror_core::capability::{
    admissible_constraint_wrt_parent, authorized, Authority, CapabilityContext, Constraint,
    EffectDesc, LogicalTime, OpAuthority,
};
use ror_core::types::CapRef;

/// Kernel-local fault labels (U-08 OPEN — provisional, not R-CALC-06 closure).
#[derive(Clone, Debug, PartialEq, Eq)]
pub enum KernelFault {
    /// Parent not valid at `t` (revoked / expired / dangling / ancestor).
    /// Maps to evaluator-local `CapabilityRevoked` (REQ-CAP-023 name tension).
    CapabilityRevoked,
    /// R-CAP-10 inadmissible constraint.
    InvalidConstraint,
    /// Generation / index mismatch (dangling).
    DanglingCapRef,
    /// Algebra authorize failed (M4 unit tests only; effect path is M5).
    Unauthorized,
}

/// Arena node: authority + lineage (R-KERN-02/03). Not visible outside crate.
struct AuthorityNode {
    authority: Authority,
    parent: Option<CapRef>,
    /// Slot generation at insert time (matches CapRef.generation).
    generation: u32,
    live: bool,
    /// Node-level lifetime envelope used by Valid (union/meet residual tracked
    /// in authority ops; envelope is the tightest bound for Valid's lifetime
    /// conjunct when ops share a common lifetime — we store the grant lifetime
    /// separately for Valid).
    lifetime: ror_core::capability::Lifetime,
}

/// Capability kernel (R-KERN-02).
pub struct CapabilityKernel {
    /// Generational slots: index → node. Empty slots keep generation counters.
    slots: Vec<Option<AuthorityNode>>,
    /// Next generation to assign when reusing a freed index (monotonic per slot).
    next_generation: Vec<u32>,
    /// Revocation set (R-KERN-02). Membership-only; iteration order irrelevant.
    revocation_set: BTreeSet<(u32, u32)>,
    /// Free list of slot indices for reuse (deterministic LIFO of frees is fine;
    /// we use sorted free list for determinism).
    free: Vec<u32>,
}

impl Default for CapabilityKernel {
    fn default() -> Self {
        Self::new()
    }
}

impl CapabilityKernel {
    pub fn new() -> Self {
        Self {
            slots: Vec::new(),
            next_generation: Vec::new(),
            revocation_set: BTreeSet::new(),
            free: Vec::new(),
        }
    }

    /// Root / deployment grant (R-KERN-06 thin half). Not durable (M7 deferred).
    ///
    /// Mints a live CapRef with the given authority. No parent. Lifetime is the
    /// meet of all op lifetimes if present, else `Lifetime::always()`.
    pub fn grant_root(
        &mut self,
        authority: Authority,
        lifetime: ror_core::capability::Lifetime,
    ) -> CapRef {
        self.insert_node(AuthorityNode {
            authority,
            parent: None,
            generation: 0, // overwritten in insert
            live: true,
            lifetime,
        })
    }

    /// Test/deployment helper: grant with always-lifetime.
    pub fn grant_root_always(&mut self, authority: Authority) -> CapRef {
        self.grant_root(authority, ror_core::capability::Lifetime::always())
    }

    fn insert_node(&mut self, mut node: AuthorityNode) -> CapRef {
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

    fn resolve(&self, cap: CapRef) -> Result<&AuthorityNode, KernelFault> {
        let idx = cap.index() as usize;
        let node = self
            .slots
            .get(idx)
            .and_then(|s| s.as_ref())
            .ok_or(KernelFault::DanglingCapRef)?;
        if node.generation != cap.generation() {
            return Err(KernelFault::DanglingCapRef);
        }
        Ok(node)
    }

    /// `Valid(c,t)` (R-CAP-07 / REQ-CAP-013): Live ∧ t∈Lifetime ∧ ∀ancestors Live.
    pub fn valid(&self, cap: CapRef, t: LogicalTime) -> bool {
        match self.valid_result(cap, t) {
            Ok(()) => true,
            Err(_) => false,
        }
    }

    pub fn valid_result(&self, cap: CapRef, t: LogicalTime) -> Result<(), KernelFault> {
        let node = self.resolve(cap)?;
        if !node.live
            || self
                .revocation_set
                .contains(&(cap.index(), cap.generation()))
        {
            return Err(KernelFault::CapabilityRevoked);
        }
        if !node.lifetime.contains(t) {
            return Err(KernelFault::CapabilityRevoked);
        }
        // Lazy ancestor walk (REQ-CAP-015).
        let mut parent = node.parent;
        while let Some(p) = parent {
            let pnode = match self.resolve(p) {
                Ok(n) => n,
                Err(_) => return Err(KernelFault::CapabilityRevoked),
            };
            if !pnode.live || self.revocation_set.contains(&(p.index(), p.generation())) {
                return Err(KernelFault::CapabilityRevoked);
            }
            // Ancestor lifetime: Valid requires Live only on ancestors per
            // R-CAP-07 formula (lifetime is on c itself). Do not require
            // ancestor lifetime contains t beyond Live.
            parent = pnode.parent;
        }
        Ok(())
    }

    /// Revoke: set Live(parent)=false (REQ-CAP-014). Descendants invalidated lazily.
    pub fn revoke(&mut self, cap: CapRef) -> Result<(), KernelFault> {
        let idx = cap.index() as usize;
        let node = self
            .slots
            .get_mut(idx)
            .and_then(|s| s.as_mut())
            .ok_or(KernelFault::DanglingCapRef)?;
        if node.generation != cap.generation() {
            return Err(KernelFault::DanglingCapRef);
        }
        node.live = false;
        self.revocation_set.insert((cap.index(), cap.generation()));
        Ok(())
    }

    /// Atomic derive (REQ-KERN-005, REQ-CAP-025, R-CAP-05/10).
    ///
    /// Premises: Valid(parent,t) ∧ AdmissibleConstraint(C).
    /// Result: new CapRef with meet authority, lineage parent link.
    /// Invariant: derived ≼ parent (CAP-DERIVE-NO-AMPLIFICATION).
    pub fn derive(
        &mut self,
        parent: CapRef,
        constraint: &Constraint,
        t: LogicalTime,
    ) -> Result<CapRef, KernelFault> {
        // Validate parent first (atomic from evaluator POV — single call).
        self.valid_result(parent, t)?;

        let parent_node = self.resolve(parent)?;
        let parent_auth = parent_node.authority.clone();
        let parent_lifetime = parent_node.lifetime;

        if !admissible_constraint_wrt_parent(constraint, &parent_auth) {
            return Err(KernelFault::InvalidConstraint);
        }

        let child_auth = parent_auth.derive_authority(constraint);
        // CAP-DERIVE-NO-AMPLIFICATION by construction of meet.
        debug_assert!(child_auth.leq(&parent_auth));

        // Child lifetime: meet of parent envelope with constraint op lifetimes.
        let mut child_lt = parent_lifetime;
        for c_op in constraint.ops.values() {
            match child_lt.meet(&c_op.lifetime) {
                Some(m) => child_lt = m,
                None => return Err(KernelFault::InvalidConstraint),
            }
        }
        // Also tighten by residual authority ops if any.
        for a_op in child_auth.ops().values() {
            if let Some(m) = child_lt.meet(&a_op.lifetime) {
                child_lt = m;
            }
        }

        if !child_lt.contains(t) {
            // Derived would be immediately invalid — treat as denied.
            return Err(KernelFault::CapabilityRevoked);
        }

        Ok(self.insert_node(AuthorityNode {
            authority: child_auth,
            parent: Some(parent),
            generation: 0,
            live: true,
            lifetime: child_lt,
        }))
    }

    /// Inspect authority for property tests only — **not** evaluator API.
    /// Returns None if dangling. Does not check Valid.
    pub fn authority_snapshot(&self, cap: CapRef) -> Option<Authority> {
        self.resolve(cap).ok().map(|n| n.authority.clone())
    }

    /// Algebra-level authorize (R-CAP-06) with optional possession gate.
    /// Effect CEK is M5; this is the pure predicate + Valid + thin possession.
    pub fn authorize_algebra(
        &self,
        holder: Option<&CapabilityContext>,
        cap: CapRef,
        effect: &EffectDesc,
        t: LogicalTime,
    ) -> Result<(), KernelFault> {
        if let Some(ctx) = holder {
            if !ctx.contains(cap) {
                return Err(KernelFault::Unauthorized);
            }
        }
        self.valid_result(cap, t)?;
        let node = self.resolve(cap)?;
        if authorized(&node.authority, effect, t) {
            Ok(())
        } else {
            Err(KernelFault::Unauthorized)
        }
    }

    /// Parent linkage for cascade tests (does not expose Authority).
    pub fn parent_of(&self, cap: CapRef) -> Option<CapRef> {
        self.resolve(cap).ok().and_then(|n| n.parent)
    }
}

/// Map kernel fault → evaluator-local Fault (shared labels; U-08 OPEN).
pub fn kernel_fault_to_eval(f: KernelFault) -> ror_core::machine::Fault {
    use ror_core::machine::Fault;
    match f {
        KernelFault::CapabilityRevoked | KernelFault::DanglingCapRef => Fault::CapabilityRevoked,
        KernelFault::InvalidConstraint => Fault::InvalidConstraint,
        KernelFault::Unauthorized => Fault::CapabilityRevoked,
    }
}

/// Build a simple single-op authority for tests/fixtures.
pub fn single_op_authority(
    op: ror_core::capability::Op,
    targets: Vec<u32>,
    units: u64,
    lifetime: ror_core::capability::Lifetime,
) -> Authority {
    let mut a = Authority::empty();
    a.insert(
        op,
        OpAuthority {
            scope: ror_core::capability::Scope::from_targets(targets),
            params: ror_core::capability::ParamConstraint::any(),
            resources: ror_core::capability::ResourceLimit::new(units),
            lifetime,
        },
    );
    a
}

/// Narrowing constraint over one op.
pub fn single_op_constraint(
    op: ror_core::capability::Op,
    targets: Vec<u32>,
    units: u64,
    lifetime: ror_core::capability::Lifetime,
) -> Constraint {
    let mut c = Constraint::empty();
    c.insert(
        op,
        OpAuthority {
            scope: ror_core::capability::Scope::from_targets(targets),
            params: ror_core::capability::ParamConstraint::any(),
            resources: ror_core::capability::ResourceLimit::new(units),
            lifetime,
        },
    );
    c
}

#[cfg(test)]
mod tests {
    use super::*;
    use ror_core::capability::{Lifetime, LogicalTime, Op, Scope};

    #[test]
    fn grant_derive_no_amplification() {
        let mut k = CapabilityKernel::new();
        let auth = single_op_authority(Op::FileRead, vec![1, 2, 3], 100, Lifetime::always());
        let parent = k.grant_root_always(auth.clone());
        let c = single_op_constraint(Op::FileRead, vec![1], 10, Lifetime::always());
        let child = k.derive(parent, &c, LogicalTime::ZERO).unwrap();
        let ca = k.authority_snapshot(child).unwrap();
        let pa = k.authority_snapshot(parent).unwrap();
        assert!(ca.leq(&pa));
        assert_eq!(
            ca.get(Op::FileRead).unwrap().scope.targets(),
            Scope::from_targets(vec![1]).targets()
        );
    }

    #[test]
    fn revoke_cascades_to_descendant() {
        let mut k = CapabilityKernel::new();
        let auth = single_op_authority(Op::FileRead, vec![1], 10, Lifetime::always());
        let root = k.grant_root_always(auth.clone());
        let c = single_op_constraint(Op::FileRead, vec![1], 5, Lifetime::always());
        let child = k.derive(root, &c, LogicalTime::ZERO).unwrap();
        let grand = k.derive(child, &c, LogicalTime::ZERO).unwrap();
        // sibling under root
        let sib = k.derive(root, &c, LogicalTime::ZERO).unwrap();
        assert!(k.valid(grand, LogicalTime::ZERO));
        assert!(k.valid(sib, LogicalTime::ZERO));
        k.revoke(child).unwrap();
        assert!(!k.valid(child, LogicalTime::ZERO));
        assert!(!k.valid(grand, LogicalTime::ZERO)); // cascade
        assert!(k.valid(sib, LogicalTime::ZERO)); // sibling preserved
        assert!(k.valid(root, LogicalTime::ZERO));
    }

    #[test]
    fn expiration_invalidates() {
        let mut k = CapabilityKernel::new();
        let lt = Lifetime::new(LogicalTime(0), LogicalTime(10));
        let auth = single_op_authority(Op::NetSend, vec![1], 1, lt);
        let cap = k.grant_root(auth, lt);
        assert!(k.valid(cap, LogicalTime(5)));
        assert!(!k.valid(cap, LogicalTime(10)));
        assert!(!k.valid(cap, LogicalTime(100)));
    }

    #[test]
    fn inadmissible_empty_constraint() {
        let mut k = CapabilityKernel::new();
        let auth = single_op_authority(Op::FileRead, vec![1], 10, Lifetime::always());
        let p = k.grant_root_always(auth);
        let err = k
            .derive(p, &Constraint::empty(), LogicalTime::ZERO)
            .unwrap_err();
        assert_eq!(err, KernelFault::InvalidConstraint);
    }

    #[test]
    fn amplify_attempt_via_extra_op_rejected() {
        let mut k = CapabilityKernel::new();
        let auth = single_op_authority(Op::FileRead, vec![1], 10, Lifetime::always());
        let p = k.grant_root_always(auth);
        // Constraint mentions NetSend which parent lacks → inadmissible.
        let c = single_op_constraint(Op::NetSend, vec![1], 10, Lifetime::always());
        let err = k.derive(p, &c, LogicalTime::ZERO).unwrap_err();
        assert_eq!(err, KernelFault::InvalidConstraint);
    }

    #[test]
    fn amplify_resource_ceiling_rejected() {
        let mut k = CapabilityKernel::new();
        let auth = single_op_authority(Op::FileRead, vec![1], 10, Lifetime::always());
        let p = k.grant_root_always(auth);
        let c = single_op_constraint(Op::FileRead, vec![1], 100, Lifetime::always()); // 100 > 10
        let err = k.derive(p, &c, LogicalTime::ZERO).unwrap_err();
        assert_eq!(err, KernelFault::InvalidConstraint);
    }

    #[test]
    fn revoked_parent_cannot_derive() {
        let mut k = CapabilityKernel::new();
        let auth = single_op_authority(Op::FileRead, vec![1], 10, Lifetime::always());
        let p = k.grant_root_always(auth);
        k.revoke(p).unwrap();
        let c = single_op_constraint(Op::FileRead, vec![1], 5, Lifetime::always());
        let err = k.derive(p, &c, LogicalTime::ZERO).unwrap_err();
        assert_eq!(err, KernelFault::CapabilityRevoked);
    }

    #[test]
    fn constraint_monotonicity_property() {
        let mut k = CapabilityKernel::new();
        let auth = single_op_authority(Op::FileRead, vec![1, 2, 3], 100, Lifetime::always());
        let p = k.grant_root_always(auth);
        let c_wide = single_op_constraint(Op::FileRead, vec![1, 2], 50, Lifetime::always());
        let c_narrow = single_op_constraint(Op::FileRead, vec![1], 10, Lifetime::always());
        assert!(c_narrow.leq(&c_wide));
        let d1 = k.derive(p, &c_narrow, LogicalTime::ZERO).unwrap();
        let d2 = k.derive(p, &c_wide, LogicalTime::ZERO).unwrap();
        let a1 = k.authority_snapshot(d1).unwrap();
        let a2 = k.authority_snapshot(d2).unwrap();
        assert!(a1.leq(&a2));
    }
}
