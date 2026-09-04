//! M4 differential: Attenuate / capability algebra observations.
//!
//! Production uses `ror-kernel`; reference uses independent `RefCapabilityStore`.
//! CapRefs compare by (index, generation) when both arenas are seeded identically.

use ror_core::capability::LogicalTime;
use ror_core::machine::Expr;
use ror_kernel::CapabilityKernel;
use ror_reference::{evaluate_with_store, RefCapabilityStore, REF_MAX_STEPS_DEFAULT};
use ror_runtime::{evaluate_with_kernel, CEK_MAX_STEPS_DEFAULT};

use crate::m2::Observation;

pub fn observe_production_m4(
    expr: Expr,
    kernel: &mut CapabilityKernel,
    t: LogicalTime,
) -> Observation {
    match evaluate_with_kernel(expr, CEK_MAX_STEPS_DEFAULT, kernel, t) {
        Ok(v) => Observation::Halted(v),
        Err(f) => Observation::Fault(f),
    }
}

pub fn observe_reference_m4(
    expr: Expr,
    store: &mut RefCapabilityStore,
    t: LogicalTime,
) -> Observation {
    match evaluate_with_store(expr, REF_MAX_STEPS_DEFAULT, store, t) {
        Ok(v) => Observation::Halted(v),
        Err(f) => Observation::Fault(f),
    }
}

pub fn compare_m4(
    expr: Expr,
    kernel: &mut CapabilityKernel,
    store: &mut RefCapabilityStore,
    t: LogicalTime,
) -> Result<(), (Observation, Observation)> {
    let p = observe_production_m4(expr.clone(), kernel, t);
    let r = observe_reference_m4(expr, store, t);
    if p == r {
        Ok(())
    } else {
        Err((p, r))
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use ror_core::capability::{Authority, Constraint, Lifetime, Op};
    use ror_core::machine::sugar::{attenuate, capability_v, constraint_v, int, let_, var};
    use ror_core::machine::{Fault, Value};
    use ror_core::types::CapRef;
    use ror_kernel::{single_op_authority, single_op_constraint, CapabilityKernel, KernelFault};
    use ror_reference::RefCapabilityStore;

    fn auth(targets: Vec<u32>, units: u64) -> Authority {
        single_op_authority(Op::FileRead, targets, units, Lifetime::always())
    }

    fn cons(targets: Vec<u32>, units: u64) -> Constraint {
        single_op_constraint(Op::FileRead, targets, units, Lifetime::always())
    }

    fn seed_root(k: &mut CapabilityKernel, s: &mut RefCapabilityStore) -> CapRef {
        let a = auth(vec![1, 2, 3], 100);
        let p = k.grant_root_always(a.clone());
        let pr = s.grant_root_from_core(&a, Lifetime::always());
        assert_eq!(
            p, pr,
            "seeded CapRefs must agree under identical grant order"
        );
        p
    }

    #[test]
    fn attenuate_success_agrees() {
        let mut k = CapabilityKernel::new();
        let mut s = RefCapabilityStore::new();
        let parent = seed_root(&mut k, &mut s);
        let e = attenuate(capability_v(parent), constraint_v(cons(vec![1], 10)));
        let p = observe_production_m4(e.clone(), &mut k, LogicalTime::ZERO);
        let r = observe_reference_m4(e, &mut s, LogicalTime::ZERO);
        assert_eq!(p, r);
        match p {
            Observation::Halted(Value::Capability(c)) => {
                assert_ne!(c, parent);
                assert!(k.valid(c, LogicalTime::ZERO));
                assert!(s.valid(c, LogicalTime::ZERO));
            }
            other => panic!("expected capability, got {other:?}"),
        }
    }

    #[test]
    fn attenuate_denied_revoked_agrees() {
        let mut k = CapabilityKernel::new();
        let mut s = RefCapabilityStore::new();
        let parent = seed_root(&mut k, &mut s);
        k.revoke(parent).unwrap();
        s.revoke(parent).unwrap();
        let e = attenuate(capability_v(parent), constraint_v(cons(vec![1], 10)));
        compare_m4(e, &mut k, &mut s, LogicalTime::ZERO).expect("m4 divergence");
    }

    #[test]
    fn attenuate_invalid_constraint_agrees() {
        let mut k = CapabilityKernel::new();
        let mut s = RefCapabilityStore::new();
        let parent = seed_root(&mut k, &mut s);
        let e = attenuate(capability_v(parent), constraint_v(Constraint::empty()));
        let p = observe_production_m4(e.clone(), &mut k, LogicalTime::ZERO);
        let r = observe_reference_m4(e, &mut s, LogicalTime::ZERO);
        assert_eq!(p, r);
        assert_eq!(p, Observation::Fault(Fault::InvalidConstraint));
    }

    #[test]
    fn attenuate_amplify_op_denied() {
        let mut k = CapabilityKernel::new();
        let mut s = RefCapabilityStore::new();
        let parent = seed_root(&mut k, &mut s);
        let c = single_op_constraint(Op::NetSend, vec![1], 10, Lifetime::always());
        let e = attenuate(capability_v(parent), constraint_v(c));
        let p = observe_production_m4(e.clone(), &mut k, LogicalTime::ZERO);
        let r = observe_reference_m4(e, &mut s, LogicalTime::ZERO);
        assert_eq!(p, r);
        assert_eq!(p, Observation::Fault(Fault::InvalidConstraint));
    }

    #[test]
    fn attenuate_under_let_composition() {
        let mut k = CapabilityKernel::new();
        let mut s = RefCapabilityStore::new();
        let parent = seed_root(&mut k, &mut s);
        let e = let_(
            1,
            attenuate(capability_v(parent), constraint_v(cons(vec![2], 20))),
            var(1),
        );
        let p = observe_production_m4(e.clone(), &mut k, LogicalTime::ZERO);
        let r = observe_reference_m4(e, &mut s, LogicalTime::ZERO);
        assert_eq!(p, r);
        assert!(matches!(p, Observation::Halted(Value::Capability(_))));
    }

    #[test]
    fn type_error_non_cap_agrees() {
        let mut k = CapabilityKernel::new();
        let mut s = RefCapabilityStore::new();
        let e = attenuate(int(1), constraint_v(cons(vec![1], 1)));
        assert_eq!(
            observe_production_m4(e.clone(), &mut k, LogicalTime::ZERO),
            observe_reference_m4(e, &mut s, LogicalTime::ZERO)
        );
    }

    #[test]
    fn algebra_no_amplification_property_both_sides() {
        let targets_sets = [vec![1u32], vec![1, 2], vec![2, 3]];
        let units = [1u64, 10, 50];
        for ts in &targets_sets {
            for &u in &units {
                let mut k = CapabilityKernel::new();
                let mut s = RefCapabilityStore::new();
                let parent = seed_root(&mut k, &mut s);
                let c = cons(ts.clone(), u);
                if !ror_core::capability::admissible_constraint_wrt_parent(
                    &c,
                    &k.authority_snapshot(parent).unwrap(),
                ) {
                    continue;
                }
                let child_k = k.derive(parent, &c, LogicalTime::ZERO).unwrap();
                let child_s = s.derive(parent, &c, LogicalTime::ZERO).unwrap();
                assert_eq!(child_k, child_s);
                let ak = k.authority_snapshot(child_k).unwrap();
                let as_ = s.authority_snapshot(child_s).unwrap();
                let pk = k.authority_snapshot(parent).unwrap();
                let ps = s.authority_snapshot(parent).unwrap();
                assert!(ak.leq(&pk));
                assert!(as_.leq(&ps));
            }
        }
    }

    #[test]
    fn revoke_cascade_both_sides() {
        let mut k = CapabilityKernel::new();
        let mut s = RefCapabilityStore::new();
        let root = seed_root(&mut k, &mut s);
        let c = cons(vec![1], 5);
        let child = k.derive(root, &c, LogicalTime::ZERO).unwrap();
        assert_eq!(child, s.derive(root, &c, LogicalTime::ZERO).unwrap());
        let grand = k.derive(child, &c, LogicalTime::ZERO).unwrap();
        assert_eq!(grand, s.derive(child, &c, LogicalTime::ZERO).unwrap());
        k.revoke(child).unwrap();
        s.revoke(child).unwrap();
        assert_eq!(
            k.valid(grand, LogicalTime::ZERO),
            s.valid(grand, LogicalTime::ZERO)
        );
        assert!(!k.valid(grand, LogicalTime::ZERO));
    }

    #[test]
    fn expiration_both_sides() {
        let lt = Lifetime::new(LogicalTime(0), LogicalTime(5));
        let a = single_op_authority(Op::FileRead, vec![1], 10, lt);
        let mut k = CapabilityKernel::new();
        let mut s = RefCapabilityStore::new();
        let p = k.grant_root(a.clone(), lt);
        let pr = s.grant_root_from_core(&a, lt);
        assert_eq!(p, pr);
        assert_eq!(k.valid(p, LogicalTime(4)), s.valid(pr, LogicalTime(4)));
        assert_eq!(k.valid(p, LogicalTime(5)), s.valid(pr, LogicalTime(5)));
        assert!(!k.valid(p, LogicalTime(5)));
    }

    #[test]
    fn mutation_intent_amplification_killed() {
        let mut k = CapabilityKernel::new();
        let parent = k.grant_root_always(auth(vec![1], 10));
        let c = cons(vec![1], 5);
        let child = k.derive(parent, &c, LogicalTime::ZERO).unwrap();
        let ca = k.authority_snapshot(child).unwrap();
        assert_eq!(ca.get(Op::FileRead).unwrap().scope.targets(), &[1]);
        assert_eq!(ca.get(Op::FileRead).unwrap().resources.units, 5);
        assert!(ca.get(Op::NetSend).is_none());
    }

    #[test]
    fn mutation_intent_skip_admissibility_killed() {
        let mut k = CapabilityKernel::new();
        let parent = k.grant_root_always(auth(vec![1], 10));
        let c = cons(vec![1], 100);
        assert_eq!(
            k.derive(parent, &c, LogicalTime::ZERO),
            Err(KernelFault::InvalidConstraint)
        );
    }

    #[test]
    fn mutation_intent_accept_revoked_killed() {
        let mut k = CapabilityKernel::new();
        let parent = k.grant_root_always(auth(vec![1], 10));
        k.revoke(parent).unwrap();
        assert!(!k.valid(parent, LogicalTime::ZERO));
        assert!(k
            .derive(parent, &cons(vec![1], 5), LogicalTime::ZERO)
            .is_err());
    }

    #[test]
    fn capref_bits_are_not_authority() {
        let k = CapabilityKernel::new();
        let forged = CapRef::from_kernel_parts(0, 0);
        assert!(!k.valid(forged, LogicalTime::ZERO));
    }

    #[test]
    fn m2_m3_regression_still_agree_without_caps() {
        use crate::m2::compare_m2;
        use ror_core::machine::sugar::{call, int, lambda, let_, var};
        compare_m2(let_(1, int(1), call(lambda(&[1], var(1)), vec![int(9)]))).unwrap();
    }
}
