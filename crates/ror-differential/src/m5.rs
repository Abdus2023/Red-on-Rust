//! M5 differential: Request / effects / durable-before-host observations.
//!
//! Production uses runtime+kernel+persistence+host.
//! Reference uses independent effect_model + RefCapabilityStore (R-REF-02).

use ror_core::capability::{CapabilityContext, LogicalTime};
use ror_core::effect::{EffectIdAlloc, ThinBudget};
use ror_core::machine::Expr;
use ror_core::types::ActorId;
use ror_host::MockHost;
use ror_kernel::CapabilityKernel;
use ror_persistence::MemoryJournal;
use ror_reference::{
    evaluate_request_ref, RefCapabilityStore, RefEffectServices, RefJournal, RefMockHost,
    REF_MAX_STEPS_DEFAULT,
};
use ror_runtime::{evaluate_request, EffectServices, CEK_MAX_STEPS_DEFAULT};

use crate::m2::Observation;

/// Production observation of a Request program with shared services.
#[allow(clippy::too_many_arguments)]
pub fn observe_production_m5(
    expr: Expr,
    kernel: &mut CapabilityKernel,
    t: LogicalTime,
    journal: &mut MemoryJournal,
    host: &mut MockHost,
    budget: &mut ThinBudget,
    ids: &mut EffectIdAlloc,
    possession: &CapabilityContext,
    host_policy_ok: bool,
) -> Observation {
    let mut services = EffectServices {
        journal,
        host,
        budget,
        ids,
        actor: ActorId(0),
        possession,
        host_policy_ok,
    };
    match evaluate_request(expr, CEK_MAX_STEPS_DEFAULT, kernel, t, &mut services) {
        Ok(v) => Observation::Halted(v),
        Err(f) => Observation::Fault(f),
    }
}

/// Reference observation of the same program.
#[allow(clippy::too_many_arguments)]
pub fn observe_reference_m5(
    expr: Expr,
    store: &mut RefCapabilityStore,
    t: LogicalTime,
    journal: &mut RefJournal,
    host: &mut RefMockHost,
    budget: &mut ThinBudget,
    ids: &mut EffectIdAlloc,
    possession: &CapabilityContext,
    host_policy_ok: bool,
) -> Observation {
    let mut services = RefEffectServices {
        journal,
        host,
        budget,
        ids,
        actor: ActorId(0),
        possession,
        host_policy_ok,
    };
    match evaluate_request_ref(expr, REF_MAX_STEPS_DEFAULT, store, t, &mut services) {
        Ok(v) => Observation::Halted(v),
        Err(f) => Observation::Fault(f),
    }
}

#[allow(clippy::too_many_arguments)]
pub fn compare_m5(
    expr: Expr,
    kernel: &mut CapabilityKernel,
    store: &mut RefCapabilityStore,
    t: LogicalTime,
    p_journal: &mut MemoryJournal,
    r_journal: &mut RefJournal,
    p_host: &mut MockHost,
    r_host: &mut RefMockHost,
    p_budget: &mut ThinBudget,
    r_budget: &mut ThinBudget,
    p_ids: &mut EffectIdAlloc,
    r_ids: &mut EffectIdAlloc,
    possession: &CapabilityContext,
    host_policy_ok: bool,
) -> Result<(), (Observation, Observation)> {
    let p = observe_production_m5(
        expr.clone(),
        kernel,
        t,
        p_journal,
        p_host,
        p_budget,
        p_ids,
        possession,
        host_policy_ok,
    );
    let r = observe_reference_m5(
        expr,
        store,
        t,
        r_journal,
        r_host,
        r_budget,
        r_ids,
        possession,
        host_policy_ok,
    );
    if p == r {
        Ok(())
    } else {
        Err((p, r))
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use ror_core::capability::{Lifetime, Op};
    use ror_core::effect::{Effect, EffectCost, Params, Target};
    use ror_core::machine::sugar::{capability_v, int, request};
    use ror_core::machine::{Fault, Value};
    use ror_core::types::{CapRef, EffectId};
    use ror_core::Symbol;
    use ror_host::PanicHost;
    use ror_kernel::single_op_authority;
    use ror_runtime::{illegal_host_before_issued, run_with_memory_journal, RequestOutcome};

    fn seed(k: &mut CapabilityKernel, s: &mut RefCapabilityStore) -> (CapRef, CapabilityContext) {
        let auth = single_op_authority(Op::FileRead, vec![1, 2, 3], 100, Lifetime::always());
        let p = k.grant_root_always(auth.clone());
        let pr = s.grant_root_from_core(&auth, Lifetime::always());
        assert_eq!(p, pr);
        let mut ctx = CapabilityContext::empty();
        ctx.insert(p);
        (p, ctx)
    }

    /// Request(cap, FileRead=0, target=1, params=[0])
    fn req_expr(cap: CapRef) -> Expr {
        request(capability_v(cap), int(0), int(1), vec![int(0)])
    }

    #[test]
    fn happy_path_agrees() {
        let mut k = CapabilityKernel::new();
        let mut s = RefCapabilityStore::new();
        let (cap, possession) = seed(&mut k, &mut s);
        let mut pj = MemoryJournal::new();
        let mut rj = RefJournal::new();
        let mut ph = MockHost::new();
        let mut rh = RefMockHost::default();
        let mut pb = ThinBudget::generous();
        let mut rb = ThinBudget::generous();
        let mut pi = EffectIdAlloc::new();
        let mut ri = EffectIdAlloc::new();
        compare_m5(
            req_expr(cap),
            &mut k,
            &mut s,
            LogicalTime::ZERO,
            &mut pj,
            &mut rj,
            &mut ph,
            &mut rh,
            &mut pb,
            &mut rb,
            &mut pi,
            &mut ri,
            &possession,
            true,
        )
        .expect("m5 divergence");
        assert_eq!(ph.calls.len(), 1);
        assert_eq!(rh.calls.len(), 1);
        assert!(pj.is_durably_issued(EffectId(0)));
        assert!(rj.is_durably_issued(EffectId(0)));
    }

    #[test]
    fn non_cap_short_circuit_agrees() {
        let mut k = CapabilityKernel::new();
        let mut s = RefCapabilityStore::new();
        let (_, possession) = seed(&mut k, &mut s);
        let e = request(int(1), int(0), int(1), vec![]);
        let mut pj = MemoryJournal::new();
        let mut rj = RefJournal::new();
        let mut ph = MockHost::new();
        let mut rh = RefMockHost::default();
        let mut pb = ThinBudget::generous();
        let mut rb = ThinBudget::generous();
        let mut pi = EffectIdAlloc::new();
        let mut ri = EffectIdAlloc::new();
        let p = observe_production_m5(
            e.clone(),
            &mut k,
            LogicalTime::ZERO,
            &mut pj,
            &mut ph,
            &mut pb,
            &mut pi,
            &possession,
            true,
        );
        let r = observe_reference_m5(
            e,
            &mut s,
            LogicalTime::ZERO,
            &mut rj,
            &mut rh,
            &mut rb,
            &mut ri,
            &possession,
            true,
        );
        assert_eq!(p, r);
        assert!(matches!(
            p,
            Observation::Fault(Fault::TypeError {
                expected: "Capability",
                ..
            })
        ));
        assert!(ph.calls.is_empty());
        assert!(rh.calls.is_empty());
        assert!(pj.durable_records().is_empty());
        assert!(rj.durable_records().is_empty());
    }

    #[test]
    fn unauthorized_no_host_agrees() {
        let mut k = CapabilityKernel::new();
        let mut s = RefCapabilityStore::new();
        let (cap, _) = seed(&mut k, &mut s);
        let empty = CapabilityContext::empty();
        let mut pj = MemoryJournal::new();
        let mut rj = RefJournal::new();
        let mut ph = MockHost::new();
        let mut rh = RefMockHost::default();
        let mut pb = ThinBudget::generous();
        let mut rb = ThinBudget::generous();
        let mut pi = EffectIdAlloc::new();
        let mut ri = EffectIdAlloc::new();
        let p = observe_production_m5(
            req_expr(cap),
            &mut k,
            LogicalTime::ZERO,
            &mut pj,
            &mut ph,
            &mut pb,
            &mut pi,
            &empty,
            true,
        );
        let r = observe_reference_m5(
            req_expr(cap),
            &mut s,
            LogicalTime::ZERO,
            &mut rj,
            &mut rh,
            &mut rb,
            &mut ri,
            &empty,
            true,
        );
        assert_eq!(p, r);
        assert_eq!(p, Observation::Fault(Fault::Unauthorized));
        assert!(ph.calls.is_empty());
        assert!(rh.calls.is_empty());
    }

    #[test]
    fn budget_deny_no_host() {
        let mut k = CapabilityKernel::new();
        let mut s = RefCapabilityStore::new();
        let (cap, possession) = seed(&mut k, &mut s);
        let mut pj = MemoryJournal::new();
        let mut rj = RefJournal::new();
        let mut ph = MockHost::new();
        let mut rh = RefMockHost::default();
        let mut pb = ThinBudget::with_available(0);
        let mut rb = ThinBudget::with_available(0);
        let mut pi = EffectIdAlloc::new();
        let mut ri = EffectIdAlloc::new();
        compare_m5(
            req_expr(cap),
            &mut k,
            &mut s,
            LogicalTime::ZERO,
            &mut pj,
            &mut rj,
            &mut ph,
            &mut rh,
            &mut pb,
            &mut rb,
            &mut pi,
            &mut ri,
            &possession,
            true,
        )
        .expect("m5 budget divergence");
        assert!(ph.calls.is_empty());
        assert!(rh.calls.is_empty());
    }

    #[test]
    fn host_policy_deny_no_host() {
        let mut k = CapabilityKernel::new();
        let mut s = RefCapabilityStore::new();
        let (cap, possession) = seed(&mut k, &mut s);
        let mut pj = MemoryJournal::new();
        let mut rj = RefJournal::new();
        let mut ph = MockHost::new();
        let mut rh = RefMockHost::default();
        let mut pb = ThinBudget::generous();
        let mut rb = ThinBudget::generous();
        let mut pi = EffectIdAlloc::new();
        let mut ri = EffectIdAlloc::new();
        let p = observe_production_m5(
            req_expr(cap),
            &mut k,
            LogicalTime::ZERO,
            &mut pj,
            &mut ph,
            &mut pb,
            &mut pi,
            &possession,
            false,
        );
        let r = observe_reference_m5(
            req_expr(cap),
            &mut s,
            LogicalTime::ZERO,
            &mut rj,
            &mut rh,
            &mut rb,
            &mut ri,
            &possession,
            false,
        );
        assert_eq!(p, r);
        assert_eq!(p, Observation::Fault(Fault::HostPolicyDenied));
        assert!(ph.calls.is_empty());
    }

    #[test]
    fn effect_id_monotonic_both_sides() {
        let mut k = CapabilityKernel::new();
        let mut s = RefCapabilityStore::new();
        let (cap, possession) = seed(&mut k, &mut s);
        let mut pj = MemoryJournal::new();
        let mut rj = RefJournal::new();
        let mut ph = MockHost::new();
        let mut rh = RefMockHost::default();
        let mut pb = ThinBudget::generous();
        let mut rb = ThinBudget::generous();
        let mut pi = EffectIdAlloc::new();
        let mut ri = EffectIdAlloc::new();
        for i in 0..3u64 {
            compare_m5(
                req_expr(cap),
                &mut k,
                &mut s,
                LogicalTime::ZERO,
                &mut pj,
                &mut rj,
                &mut ph,
                &mut rh,
                &mut pb,
                &mut rb,
                &mut pi,
                &mut ri,
                &possession,
                true,
            )
            .unwrap();
            assert_eq!(ph.calls[i as usize], EffectId(i));
            assert_eq!(rh.calls[i as usize], EffectId(i));
        }
    }

    #[test]
    fn digest_equality_both_sides() {
        let mut k = CapabilityKernel::new();
        let mut s = RefCapabilityStore::new();
        let (cap, _) = seed(&mut k, &mut s);
        let e = Effect::new(
            cap,
            Op::FileRead,
            Target(1),
            Params::from_tags(vec![0]),
            EffectCost::new(1, 1, 0),
        );
        // Same canonical bytes → same digest (shared Effect type).
        assert_eq!(e.digest(), e.digest());
        let bytes = e.canonical_bytes();
        assert_eq!(ror_core::digest::EffectDigest::of_bytes(&bytes), e.digest());
    }

    /// Mutation intent: host-before-Issued must be killable.
    /// Calling host without journal Issued is the illegal path — PanicHost panics.
    #[test]
    #[should_panic(expected = "GI-SEC-07")]
    fn mutation_intent_host_before_issued_killed() {
        let mut host = PanicHost::new();
        let effect = Effect::new(
            CapRef::from_kernel_parts(0, 0),
            Op::FileRead,
            Target(1),
            Params::empty(),
            EffectCost::zero(),
        );
        let bytes = effect.canonical_bytes();
        let digest = ror_core::digest::EffectDigest::of_bytes(&bytes);
        let req = ror_core::effect::EffectRequest {
            id: EffectId(0),
            actor: ActorId(0),
            digest,
            effect_bytes: bytes,
            cost: EffectCost::zero(),
            effect,
        };
        // Illegal: host without durable Issued.
        let _ = illegal_host_before_issued(&mut host, &req);
    }

    /// Pipeline never reaches host on unauthorized (PanicHost).
    #[test]
    fn mutation_intent_skip_auth_killed() {
        let mut k = CapabilityKernel::new();
        let auth = single_op_authority(Op::FileRead, vec![1], 10, Lifetime::always());
        let cap = k.grant_root_always(auth);
        let empty = CapabilityContext::empty();
        let mut journal = MemoryJournal::new();
        let mut host = PanicHost::new();
        let mut budget = ThinBudget::generous();
        let mut ids = EffectIdAlloc::new();
        let effect = Effect::new(
            cap,
            Op::FileRead,
            Target(1),
            Params::empty(),
            EffectCost::new(1, 1, 0),
        );
        let out = run_with_memory_journal(
            &mut k,
            &mut journal,
            &mut host,
            &mut budget,
            &mut ids,
            ActorId(0),
            &empty,
            LogicalTime::ZERO,
            true,
            effect,
        );
        assert!(matches!(out, RequestOutcome::Denied(Fault::Unauthorized)));
        assert!(!host.invoked);
        assert!(journal.durable_records().is_empty());
    }

    #[test]
    fn m4_regression_still_agrees() {
        use crate::m4::compare_m4;
        use ror_core::machine::sugar::{attenuate, capability_v, constraint_v};
        use ror_kernel::single_op_constraint;
        let mut k = CapabilityKernel::new();
        let mut s = RefCapabilityStore::new();
        let (parent, _) = seed(&mut k, &mut s);
        let c = single_op_constraint(Op::FileRead, vec![1], 10, Lifetime::always());
        let e = attenuate(capability_v(parent), constraint_v(c));
        compare_m4(e, &mut k, &mut s, LogicalTime::ZERO).expect("m4 regression");
    }

    #[test]
    fn happy_halts_unit() {
        let mut k = CapabilityKernel::new();
        let mut s = RefCapabilityStore::new();
        let (cap, possession) = seed(&mut k, &mut s);
        let mut pj = MemoryJournal::new();
        let mut ph = MockHost::new();
        let mut pb = ThinBudget::generous();
        let mut pi = EffectIdAlloc::new();
        let p = observe_production_m5(
            req_expr(cap),
            &mut k,
            LogicalTime::ZERO,
            &mut pj,
            &mut ph,
            &mut pb,
            &mut pi,
            &possession,
            true,
        );
        assert_eq!(p, Observation::Halted(Value::Unit));
        let _ = s;
    }

    #[test]
    fn args_ltr_fault_stops_before_later_params() {
        // Request(cap, op, target, [unbound, int(0)]) — first param faults LTR.
        let mut k = CapabilityKernel::new();
        let mut s = RefCapabilityStore::new();
        let (cap, possession) = seed(&mut k, &mut s);
        use ror_core::machine::sugar::var;
        let e = request(capability_v(cap), int(0), int(1), vec![var(99), int(0)]);
        let mut pj = MemoryJournal::new();
        let mut rj = RefJournal::new();
        let mut ph = MockHost::new();
        let mut rh = RefMockHost::default();
        let mut pb = ThinBudget::generous();
        let mut rb = ThinBudget::generous();
        let mut pi = EffectIdAlloc::new();
        let mut ri = EffectIdAlloc::new();
        let p = observe_production_m5(
            e.clone(),
            &mut k,
            LogicalTime::ZERO,
            &mut pj,
            &mut ph,
            &mut pb,
            &mut pi,
            &possession,
            true,
        );
        let r = observe_reference_m5(
            e,
            &mut s,
            LogicalTime::ZERO,
            &mut rj,
            &mut rh,
            &mut rb,
            &mut ri,
            &possession,
            true,
        );
        assert_eq!(p, r);
        assert_eq!(p, Observation::Fault(Fault::UnboundVariable(Symbol(99))));
        assert!(ph.calls.is_empty());
        assert!(pj.durable_records().is_empty());
    }
}
