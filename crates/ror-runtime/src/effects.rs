//! M5 effect pipeline (R-CORE-14 gates 4–16 + R-DUR-01/02 issuance).
//!
//! **Security hinge:** `HostInvoked(E) ⇒ DurableIssued(E)` (GI-SEC-07 / R-DUR-01).
//! `HostExecutor::execute` is only called after journal confirms Issued+sync.
//!
//! Host adapters live in `ror-host` and implement [`HostExecutor`] defined here
//! (runtime does not depend on host — avoids Cargo cycle with host→runtime).

use ror_core::capability::{CapabilityContext, LogicalTime};
use ror_core::digest::EffectDigest;
use ror_core::effect::{
    op_from_i64, Consumable, Effect, EffectCost, EffectIdAlloc, EffectReceipt, EffectRequest,
    HostFaultCode, Params, ReceiptValue, Reserved, Target, ThinBudget,
};
use ror_core::machine::{Fault, Value};
use ror_core::types::{ActorId, CapRef, EffectId};
use ror_kernel::{CapabilityKernel, KernelFault};
use ror_persistence::{issued, prepared, IssuanceJournal, MemoryJournal, PersistError};

/// δ_t for request issuance / receipt (R-BUDGET-16).
pub const DELTA_T_REQUEST: u64 = 1;
pub const DELTA_T_RECEIPT: u64 = 1;

/// Host executor (R-HOST-02). Defined in runtime; implemented by `ror-host`.
pub trait HostExecutor {
    fn execute(&mut self, request: &EffectRequest) -> Result<EffectReceipt, HostError>;
}

/// Host execution fault (provisional; U-08 OPEN).
#[derive(Clone, Debug, PartialEq, Eq)]
pub enum HostError {
    PolicyDenied,
    ExecutionFailed,
    /// Replay trace exhausted or mismatched.
    ReplayFault,
}

impl HostError {
    pub fn code(&self) -> HostFaultCode {
        match self {
            HostError::PolicyDenied => HostFaultCode::POLICY_DENIED,
            HostError::ExecutionFailed => HostFaultCode::EXECUTION_FAILED,
            HostError::ReplayFault => HostFaultCode(3),
        }
    }
}

/// Outcome of a full Request pipeline run after CEK field evaluation.
#[derive(Clone, Debug, PartialEq, Eq)]
pub enum RequestOutcome {
    /// Effect issued, host ran, receipt validated → continuation value.
    Completed { id: EffectId, value: Value },
    /// Issued and host path taken but host/receipt faulted.
    HostFailed { id: EffectId, fault: Fault },
    /// Denied before issuance (R-EFFECT-04 short-circuit).
    Denied(Fault),
}

/// Machine-side request context (thin single-actor M5).
pub struct RequestCtx<'a> {
    pub kernel: &'a mut CapabilityKernel,
    pub journal: &'a mut dyn IssuanceJournal,
    pub host: &'a mut dyn HostExecutor,
    pub budget: &'a mut ThinBudget,
    pub ids: &'a mut EffectIdAlloc,
    pub actor: ActorId,
    pub possession: &'a CapabilityContext,
    pub logical_time: LogicalTime,
    /// Gate 11 host-policy precheck. Default allow when true.
    pub host_policy_ok: bool,
}

/// Build Effect from evaluated CEK values (post steps 1–3).
pub fn effect_from_values(
    cap: CapRef,
    op_v: &Value,
    target_v: &Value,
    param_vs: &[Value],
    cost: EffectCost,
) -> Result<Effect, Fault> {
    let op = match op_v {
        Value::Integer(n) => op_from_i64(*n).ok_or(Fault::EffectError {
            reason: "unknown_op",
        })?,
        _ => {
            return Err(Fault::TypeError {
                expected: "Integer(Op)",
                actual: value_kind(op_v),
            })
        }
    };
    let target = match target_v {
        Value::Integer(n) if *n >= 0 && *n <= i64::from(u32::MAX) => Target(*n as u32),
        _ => {
            return Err(Fault::TypeError {
                expected: "Integer(Target)",
                actual: value_kind(target_v),
            })
        }
    };
    let mut tags = Vec::new();
    for p in param_vs {
        match p {
            Value::Integer(n) if *n >= 0 && *n <= i64::from(u32::MAX) => tags.push(*n as u32),
            _ => {
                return Err(Fault::TypeError {
                    expected: "Integer(Param)",
                    actual: value_kind(p),
                })
            }
        }
    }
    Ok(Effect::new(cap, op, target, Params::from_tags(tags), cost))
}

fn value_kind(v: &Value) -> &'static str {
    match v {
        Value::Unit => "Unit",
        Value::Bool(_) => "Bool",
        Value::Integer(_) => "Integer",
        Value::Bytes(_) => "Bytes",
        Value::Symbol(_) => "Symbol",
        Value::String(_) => "String",
        Value::List(_) => "List",
        Value::Tuple(_) => "Tuple",
        Value::Function(_) => "Function",
        Value::Capability(_) => "Capability",
        Value::DelegatedCapability(_) => "DelegatedCapability",
        Value::Constraint(_) => "Constraint",
    }
}

fn map_persist(e: PersistError) -> Fault {
    match e {
        PersistError::Io | PersistError::JournalCorruption | PersistError::CausalViolation => {
            Fault::PersistenceError
        }
    }
}

fn map_kernel(e: KernelFault) -> Fault {
    match e {
        KernelFault::Unauthorized => Fault::Unauthorized,
        KernelFault::CapabilityRevoked | KernelFault::DanglingCapRef => Fault::CapabilityRevoked,
        KernelFault::InvalidConstraint => Fault::InvalidConstraint,
    }
}

/// Default provisional cost when AST carries none (U-21 / thin M5).
pub fn default_effect_cost() -> EffectCost {
    EffectCost::new(1, 1, 0)
}

/// Run gates 5–16 for a fully constructed Effect.
///
/// Enforces R-EFFECT-04 short-circuit and R-DUR-01 durable-before-host.
pub fn run_effect_pipeline(ctx: &mut RequestCtx<'_>, effect: Effect) -> RequestOutcome {
    let t = ctx.logical_time;

    // --- Gate 5: Valid CapRef ---
    if let Err(e) = ctx.kernel.valid_result(effect.capability, t) {
        return RequestOutcome::Denied(map_kernel(e));
    }

    // --- Gate 6: Authorize (possession + algebra); ceiling via cost_units in R ---
    let desc = effect.to_desc();
    if let Err(e) = ctx
        .kernel
        .authorize_algebra(Some(ctx.possession), effect.capability, &desc, t)
    {
        return RequestOutcome::Denied(map_kernel(e));
    }

    // --- Gate 8: runtime budget issue+complete_max ---
    let need = match effect.cost.issue_plus_complete_max() {
        Some(n) => n,
        None => return RequestOutcome::Denied(Fault::BudgetExhausted),
    };
    if !need.saturating_leq(ctx.budget.available) {
        return RequestOutcome::Denied(Fault::BudgetExhausted);
    }

    // --- Gate 9: reservation ---
    if effect.cost.reserve.slots > ctx.budget.reserved.slots {
        return RequestOutcome::Denied(Fault::BudgetExhausted);
    }

    // --- Gate 10: deadline t + δ_t(req) ≤ W ---
    if let Some(w) = ctx.budget.deadline {
        let t_after = LogicalTime(t.get().saturating_add(DELTA_T_REQUEST));
        if t_after > w {
            return RequestOutcome::Denied(Fault::DeadlineExceeded);
        }
    }

    // --- Gate 11: host policy (machine fail-early) ---
    if !ctx.host_policy_ok {
        return RequestOutcome::Denied(Fault::HostPolicyDenied);
    }

    // --- Steps 12–14b atomic issuance section ---
    let prev_next = ctx.ids.peek_next();
    let prev_avail = ctx.budget.available;
    let prev_res = ctx.budget.reserved;

    let id = ctx.ids.allocate();
    let effect_bytes = effect.canonical_bytes();
    let digest = EffectDigest::of_bytes(&effect_bytes);
    let actor = ctx.actor;
    let cost = effect.cost;

    // Charge issue+complete_max escrow; hold reserve slots.
    ctx.budget.available = Consumable::new(ctx.budget.available.units.saturating_sub(need.units));
    ctx.budget.reserved =
        Reserved::new(ctx.budget.reserved.slots.saturating_sub(cost.reserve.slots));

    let prep = prepared(id, actor, digest, effect_bytes.clone(), cost);
    if let Err(e) = ctx.journal.append(prep) {
        rollback_alloc(ctx, prev_next, prev_avail, prev_res);
        return RequestOutcome::Denied(map_persist(e));
    }
    if let Err(e) = ctx.journal.sync() {
        rollback_alloc(ctx, prev_next, prev_avail, prev_res);
        return RequestOutcome::Denied(map_persist(e));
    }

    let iss = issued(id, actor, digest, effect_bytes.clone(), cost);
    if let Err(e) = ctx.journal.append(iss) {
        rollback_alloc(ctx, prev_next, prev_avail, prev_res);
        return RequestOutcome::Denied(map_persist(e));
    }
    if let Err(e) = ctx.journal.sync() {
        rollback_alloc(ctx, prev_next, prev_avail, prev_res);
        return RequestOutcome::Denied(map_persist(e));
    }

    // Durable Issued confirmed — only now may host run (step 16).
    let request = EffectRequest {
        id,
        actor,
        digest,
        effect_bytes,
        cost,
        effect,
    };

    // --- Step 16: host ---
    match ctx.host.execute(&request) {
        Ok(receipt) => match validate_and_complete(&request, receipt) {
            Ok(v) => {
                // Thin completion: optional Completed journal record.
                let result_bytes = match &v {
                    Value::Unit => ReceiptValue::Unit.canonical_bytes(),
                    Value::Bool(b) => ReceiptValue::Bool(*b).canonical_bytes(),
                    Value::Integer(n) => ReceiptValue::Integer(*n).canonical_bytes(),
                    Value::String(s) => ReceiptValue::String(s.clone()).canonical_bytes(),
                    Value::Bytes(b) => ReceiptValue::Bytes(b.clone()).canonical_bytes(),
                    _ => ReceiptValue::Unit.canonical_bytes(),
                };
                let _ = result_bytes;
                let _ = DELTA_T_RECEIPT;
                RequestOutcome::Completed { id, value: v }
            }
            Err(f) => RequestOutcome::HostFailed { id, fault: f },
        },
        Err(he) => {
            let fault = match he {
                HostError::PolicyDenied => Fault::HostPolicyDenied,
                other => Fault::HostFault {
                    code: other.code().0,
                },
            };
            RequestOutcome::HostFailed { id, fault }
        }
    }
}

fn rollback_alloc(
    ctx: &mut RequestCtx<'_>,
    prev_next: u64,
    prev_avail: Consumable,
    prev_res: Reserved,
) {
    *ctx.ids = EffectIdAlloc::with_start(prev_next);
    ctx.budget.available = prev_avail;
    ctx.budget.reserved = prev_res;
}

/// R-EFFECT-06/07/08: validate receipt then map to Value.
fn validate_and_complete(request: &EffectRequest, receipt: EffectReceipt) -> Result<Value, Fault> {
    if receipt.id != request.id || receipt.effect_digest != request.digest {
        return Err(Fault::ReplayCorruption);
    }
    match receipt.result {
        Ok(rv) => {
            // R-EFFECT-08: ReceiptValue is data-only by construction (no Cap/Fn).
            Ok(receipt_to_value(rv))
        }
        Err(code) => {
            if code == HostFaultCode::POLICY_DENIED {
                Err(Fault::HostPolicyDenied)
            } else {
                Err(Fault::HostFault { code: code.0 })
            }
        }
    }
}

fn receipt_to_value(rv: ReceiptValue) -> Value {
    match rv {
        ReceiptValue::Unit => Value::Unit,
        ReceiptValue::Bool(b) => Value::Bool(b),
        ReceiptValue::Integer(n) => Value::Integer(n),
        ReceiptValue::String(s) => Value::String(s),
        ReceiptValue::Bytes(b) => Value::Bytes(b),
    }
}

/// Convenience: run pipeline with MemoryJournal + durable-Issued assert.
#[allow(clippy::too_many_arguments)]
pub fn run_with_memory_journal(
    kernel: &mut CapabilityKernel,
    journal: &mut MemoryJournal,
    host: &mut dyn HostExecutor,
    budget: &mut ThinBudget,
    ids: &mut EffectIdAlloc,
    actor: ActorId,
    possession: &CapabilityContext,
    t: LogicalTime,
    host_policy_ok: bool,
    effect: Effect,
) -> RequestOutcome {
    let mut ctx = RequestCtx {
        kernel,
        journal: journal as &mut dyn IssuanceJournal,
        host,
        budget,
        ids,
        actor,
        possession,
        logical_time: t,
        host_policy_ok,
    };
    let out = run_effect_pipeline(&mut ctx, effect);
    if let RequestOutcome::Completed { id, .. } | RequestOutcome::HostFailed { id, .. } = &out {
        assert!(
            journal.is_durably_issued(*id),
            "GI-SEC-07 violated: host path without durable Issued"
        );
    }
    out
}

/// Negative-test helper: call host without Issued (must not be used in prod path).
pub fn illegal_host_before_issued(
    host: &mut dyn HostExecutor,
    request: &EffectRequest,
) -> Result<EffectReceipt, HostError> {
    host.execute(request)
}

/// Bundle for CEK-integrated Request evaluation.
pub struct EffectServices<'a> {
    pub journal: &'a mut dyn IssuanceJournal,
    pub host: &'a mut dyn HostExecutor,
    pub budget: &'a mut ThinBudget,
    pub ids: &'a mut EffectIdAlloc,
    pub actor: ActorId,
    pub possession: &'a CapabilityContext,
    pub host_policy_ok: bool,
}

impl EffectServices<'_> {
    pub fn run(
        &mut self,
        kernel: &mut CapabilityKernel,
        t: LogicalTime,
        effect: Effect,
    ) -> RequestOutcome {
        let mut ctx = RequestCtx {
            kernel,
            journal: self.journal,
            host: self.host,
            budget: self.budget,
            ids: self.ids,
            actor: self.actor,
            possession: self.possession,
            logical_time: t,
            host_policy_ok: self.host_policy_ok,
        };
        run_effect_pipeline(&mut ctx, effect)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use ror_core::capability::{Lifetime, Op};
    use ror_core::effect::EffectCost;
    use ror_kernel::single_op_authority;
    use ror_persistence::MemoryJournal;

    /// Local mock host for unit tests (avoids ror-host dep from runtime tests).
    struct TestHost {
        calls: Vec<EffectId>,
        deny: bool,
    }
    impl TestHost {
        fn ok() -> Self {
            Self {
                calls: Vec::new(),
                deny: false,
            }
        }
        fn deny() -> Self {
            Self {
                calls: Vec::new(),
                deny: true,
            }
        }
    }
    impl HostExecutor for TestHost {
        fn execute(&mut self, request: &EffectRequest) -> Result<EffectReceipt, HostError> {
            self.calls.push(request.id);
            if self.deny {
                return Err(HostError::PolicyDenied);
            }
            Ok(EffectReceipt {
                id: request.id,
                effect_digest: request.digest,
                result: Ok(ReceiptValue::Unit),
            })
        }
    }

    /// Panic host for deny-path tests.
    struct PanicHost {
        invoked: bool,
    }
    impl HostExecutor for PanicHost {
        fn execute(&mut self, request: &EffectRequest) -> Result<EffectReceipt, HostError> {
            self.invoked = true;
            panic!("GI-SEC-07: host before Issued id={:?}", request.id);
        }
    }

    fn setup_cap(k: &mut CapabilityKernel) -> (CapRef, CapabilityContext) {
        let auth = single_op_authority(Op::FileRead, vec![1, 2, 3], 100, Lifetime::always());
        let cap = k.grant_root_always(auth);
        let mut ctx = CapabilityContext::empty();
        ctx.insert(cap);
        (cap, ctx)
    }

    fn sample_effect(cap: CapRef) -> Effect {
        Effect::new(
            cap,
            Op::FileRead,
            Target(1),
            Params::from_tags(vec![0]),
            EffectCost::new(1, 1, 0),
        )
    }

    #[test]
    fn happy_path_issued_before_host() {
        let mut k = CapabilityKernel::new();
        let (cap, possession) = setup_cap(&mut k);
        let mut journal = MemoryJournal::new();
        let mut host = TestHost::ok();
        let mut budget = ThinBudget::generous();
        let mut ids = EffectIdAlloc::new();
        let out = run_with_memory_journal(
            &mut k,
            &mut journal,
            &mut host,
            &mut budget,
            &mut ids,
            ActorId(0),
            &possession,
            LogicalTime::ZERO,
            true,
            sample_effect(cap),
        );
        assert!(matches!(out, RequestOutcome::Completed { .. }));
        assert_eq!(host.calls.len(), 1);
        assert!(journal.is_durably_issued(EffectId(0)));
    }

    #[test]
    fn deny_unauthorized_never_hosts() {
        let mut k = CapabilityKernel::new();
        let (cap, _poss) = setup_cap(&mut k);
        let empty = CapabilityContext::empty();
        let mut journal = MemoryJournal::new();
        let mut host = PanicHost { invoked: false };
        let mut budget = ThinBudget::generous();
        let mut ids = EffectIdAlloc::new();
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
            sample_effect(cap),
        );
        assert!(matches!(out, RequestOutcome::Denied(Fault::Unauthorized)));
        assert!(!host.invoked);
        assert!(journal.durable_records().is_empty());
    }

    #[test]
    fn deny_budget_never_hosts() {
        let mut k = CapabilityKernel::new();
        let (cap, possession) = setup_cap(&mut k);
        let mut journal = MemoryJournal::new();
        let mut host = PanicHost { invoked: false };
        let mut budget = ThinBudget::with_available(0);
        let mut ids = EffectIdAlloc::new();
        let out = run_with_memory_journal(
            &mut k,
            &mut journal,
            &mut host,
            &mut budget,
            &mut ids,
            ActorId(0),
            &possession,
            LogicalTime::ZERO,
            true,
            sample_effect(cap),
        );
        assert!(matches!(
            out,
            RequestOutcome::Denied(Fault::BudgetExhausted)
        ));
        assert!(!host.invoked);
    }

    #[test]
    fn deny_host_policy_never_hosts() {
        let mut k = CapabilityKernel::new();
        let (cap, possession) = setup_cap(&mut k);
        let mut journal = MemoryJournal::new();
        let mut host = PanicHost { invoked: false };
        let mut budget = ThinBudget::generous();
        let mut ids = EffectIdAlloc::new();
        let out = run_with_memory_journal(
            &mut k,
            &mut journal,
            &mut host,
            &mut budget,
            &mut ids,
            ActorId(0),
            &possession,
            LogicalTime::ZERO,
            false,
            sample_effect(cap),
        );
        assert!(matches!(
            out,
            RequestOutcome::Denied(Fault::HostPolicyDenied)
        ));
        assert!(!host.invoked);
    }

    #[test]
    fn deny_deadline_never_hosts() {
        let mut k = CapabilityKernel::new();
        let (cap, possession) = setup_cap(&mut k);
        let mut journal = MemoryJournal::new();
        let mut host = PanicHost { invoked: false };
        let mut budget = ThinBudget::generous();
        // W = 0, t = 0, δ_t = 1 → t+δ_t = 1 > 0
        budget.deadline = Some(LogicalTime(0));
        let mut ids = EffectIdAlloc::new();
        let out = run_with_memory_journal(
            &mut k,
            &mut journal,
            &mut host,
            &mut budget,
            &mut ids,
            ActorId(0),
            &possession,
            LogicalTime::ZERO,
            true,
            sample_effect(cap),
        );
        assert!(matches!(
            out,
            RequestOutcome::Denied(Fault::DeadlineExceeded)
        ));
        assert!(!host.invoked);
    }

    #[test]
    fn persist_fail_no_host() {
        let mut k = CapabilityKernel::new();
        let (cap, possession) = setup_cap(&mut k);
        let mut journal = MemoryJournal::new();
        journal.fail_next_append();
        let mut host = PanicHost { invoked: false };
        let mut budget = ThinBudget::generous();
        let mut ids = EffectIdAlloc::new();
        let out = run_with_memory_journal(
            &mut k,
            &mut journal,
            &mut host,
            &mut budget,
            &mut ids,
            ActorId(0),
            &possession,
            LogicalTime::ZERO,
            true,
            sample_effect(cap),
        );
        assert!(matches!(
            out,
            RequestOutcome::Denied(Fault::PersistenceError)
        ));
        assert!(!host.invoked);
        // Id rolled back
        assert_eq!(ids.peek_next(), 0);
    }

    #[test]
    fn effect_id_monotonic_across_requests() {
        let mut k = CapabilityKernel::new();
        let (cap, possession) = setup_cap(&mut k);
        let mut journal = MemoryJournal::new();
        let mut host = TestHost::ok();
        let mut budget = ThinBudget::generous();
        let mut ids = EffectIdAlloc::new();
        for expected in 0..3u64 {
            let out = run_with_memory_journal(
                &mut k,
                &mut journal,
                &mut host,
                &mut budget,
                &mut ids,
                ActorId(0),
                &possession,
                LogicalTime::ZERO,
                true,
                sample_effect(cap),
            );
            match out {
                RequestOutcome::Completed { id, .. } => assert_eq!(id, EffectId(expected)),
                other => panic!("expected complete, got {other:?}"),
            }
        }
    }

    #[test]
    fn non_cap_type_at_effect_from_values() {
        let err = effect_from_values(
            CapRef::from_kernel_parts(0, 0),
            &Value::Bool(true),
            &Value::Integer(1),
            &[],
            EffectCost::zero(),
        );
        assert!(err.is_err());
    }

    #[test]
    fn host_deny_after_issued() {
        let mut k = CapabilityKernel::new();
        let (cap, possession) = setup_cap(&mut k);
        let mut journal = MemoryJournal::new();
        let mut host = TestHost::deny();
        let mut budget = ThinBudget::generous();
        let mut ids = EffectIdAlloc::new();
        let out = run_with_memory_journal(
            &mut k,
            &mut journal,
            &mut host,
            &mut budget,
            &mut ids,
            ActorId(0),
            &possession,
            LogicalTime::ZERO,
            true,
            sample_effect(cap),
        );
        assert!(matches!(
            out,
            RequestOutcome::HostFailed {
                fault: Fault::HostPolicyDenied,
                ..
            }
        ));
        assert!(journal.is_durably_issued(EffectId(0)));
    }

    #[test]
    fn receipt_value_is_unit_data_only() {
        // M019/M020 oracle: completed value must be data-domain (Unit here), never Cap/Fn.
        let mut k = CapabilityKernel::new();
        let (cap, possession) = setup_cap(&mut k);
        let mut journal = MemoryJournal::new();
        let mut host = TestHost::ok();
        let mut budget = ThinBudget::generous();
        let mut ids = EffectIdAlloc::new();
        let out = run_with_memory_journal(
            &mut k,
            &mut journal,
            &mut host,
            &mut budget,
            &mut ids,
            ActorId(0),
            &possession,
            LogicalTime::ZERO,
            true,
            sample_effect(cap),
        );
        match out {
            RequestOutcome::Completed { value, .. } => {
                assert!(
                    matches!(
                        value,
                        Value::Unit
                            | Value::Bool(_)
                            | Value::Integer(_)
                            | Value::String(_)
                            | Value::Bytes(_)
                    ),
                    "R-EFFECT-08 data-only receipt, got {value:?}"
                );
            }
            other => panic!("expected complete, got {other:?}"),
        }
    }

    #[test]
    fn host_fail_does_not_release_escrow() {
        // M008/M035 oracle: HostFailed must not silently restore available escrow.
        let mut k = CapabilityKernel::new();
        let (cap, possession) = setup_cap(&mut k);
        let mut journal = MemoryJournal::new();
        let mut host = TestHost::deny();
        let mut budget = ThinBudget::with_available(100);
        let before = budget.available.units;
        let mut ids = EffectIdAlloc::new();
        let out = run_with_memory_journal(
            &mut k,
            &mut journal,
            &mut host,
            &mut budget,
            &mut ids,
            ActorId(0),
            &possession,
            LogicalTime::ZERO,
            true,
            sample_effect(cap),
        );
        assert!(matches!(out, RequestOutcome::HostFailed { .. }));
        // escrow charged (issue+complete_max = 2 for default cost 1+1)
        assert!(
            budget.available.units < before,
            "escrow must remain charged on indeterminate host fail; available {} vs before {}",
            budget.available.units,
            before
        );
    }

    #[test]
    fn deny_path_effect_id_not_consumed() {
        // M010 oracle: unauthorized deny must not advance EffectId allocator.
        let mut k = CapabilityKernel::new();
        let (cap, _poss) = setup_cap(&mut k);
        let empty = CapabilityContext::empty();
        let mut journal = MemoryJournal::new();
        let mut host = PanicHost { invoked: false };
        let mut budget = ThinBudget::generous();
        let mut ids = EffectIdAlloc::new();
        let before = ids.peek_next();
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
            sample_effect(cap),
        );
        assert!(matches!(out, RequestOutcome::Denied(Fault::Unauthorized)));
        assert_eq!(
            ids.peek_next(),
            before,
            "M010: EffectId must not allocate before auth success"
        );
    }

    #[test]
    fn completed_receipt_not_deadline_denied() {
        // M041 oracle: successful host completion must not be re-denied by deadline gate.
        let mut k = CapabilityKernel::new();
        let (cap, possession) = setup_cap(&mut k);
        let mut journal = MemoryJournal::new();
        let mut host = TestHost::ok();
        let mut budget = ThinBudget::generous();
        // deadline far enough for request gate, but if receipt re-checks with δ_t it may still pass
        // Use W = 1: request at t=0 with δ_t=1 ok (t_after=1 <=1); receipt re-check t+1=1 ok.
        // Use W = 0 would deny at request. Use W=1 and advance logical time context...
        // Pipeline uses same logical_time for request; receipt mutant adds DELTA_T_RECEIPT.
        // t=0, W=1: request t+1=1<=1 OK; receipt t+1=1<=1 OK — still passes.
        // t=0, W=1 with DELTA_T_RECEIPT extra: still 1.
        // Need: request uses δ_t=1 against W=1 ok; receipt adds another +1 → 2 > 1.
        budget.deadline = Some(LogicalTime(1));
        let mut ids = EffectIdAlloc::new();
        let out = run_with_memory_journal(
            &mut k,
            &mut journal,
            &mut host,
            &mut budget,
            &mut ids,
            ActorId(0),
            &possession,
            LogicalTime::ZERO,
            true,
            sample_effect(cap),
        );
        assert!(
            matches!(out, RequestOutcome::Completed { .. }),
            "post-issue receipt must settle, not DeadlineExceeded: {out:?}"
        );
    }

    #[test]
    fn mismatched_receipt_digest_is_corruption() {
        // M017/M018 oracle: tampered effect_digest must not complete.
        struct BadDigestHost;
        impl HostExecutor for BadDigestHost {
            fn execute(&mut self, request: &EffectRequest) -> Result<EffectReceipt, HostError> {
                Ok(EffectReceipt {
                    id: request.id,
                    effect_digest: EffectDigest::of_bytes(b"tampered"),
                    result: Ok(ReceiptValue::Unit),
                })
            }
        }
        let mut k = CapabilityKernel::new();
        let (cap, possession) = setup_cap(&mut k);
        let mut journal = MemoryJournal::new();
        let mut host = BadDigestHost;
        let mut budget = ThinBudget::generous();
        let mut ids = EffectIdAlloc::new();
        let out = run_with_memory_journal(
            &mut k,
            &mut journal,
            &mut host,
            &mut budget,
            &mut ids,
            ActorId(0),
            &possession,
            LogicalTime::ZERO,
            true,
            sample_effect(cap),
        );
        assert!(
            matches!(
                out,
                RequestOutcome::HostFailed {
                    fault: Fault::ReplayCorruption,
                    ..
                }
            ),
            "expected ReplayCorruption, got {out:?}"
        );
    }

    #[test]
    fn host_invoked_exactly_once_on_success() {
        // M037 oracle: single host execute after durable Issued (no pre-sync call).
        let mut k = CapabilityKernel::new();
        let (cap, possession) = setup_cap(&mut k);
        let mut journal = MemoryJournal::new();
        let mut host = TestHost::ok();
        let mut budget = ThinBudget::generous();
        let mut ids = EffectIdAlloc::new();
        let out = run_with_memory_journal(
            &mut k,
            &mut journal,
            &mut host,
            &mut budget,
            &mut ids,
            ActorId(0),
            &possession,
            LogicalTime::ZERO,
            true,
            sample_effect(cap),
        );
        assert!(matches!(out, RequestOutcome::Completed { .. }));
        assert_eq!(
            host.calls.len(),
            1,
            "host must run exactly once after Issued"
        );
    }

    #[test]
    fn budget_charge_matches_issue_plus_complete_max_only() {
        // M042 oracle: no double duration debit beyond issue+complete_max.
        let mut k = CapabilityKernel::new();
        let (cap, possession) = setup_cap(&mut k);
        let mut journal = MemoryJournal::new();
        let mut host = TestHost::ok();
        let mut budget = ThinBudget::with_available(100);
        let before = budget.available.units;
        let mut ids = EffectIdAlloc::new();
        let eff = sample_effect(cap);
        let need = eff.cost.issue_plus_complete_max().unwrap().units;
        let out = run_with_memory_journal(
            &mut k,
            &mut journal,
            &mut host,
            &mut budget,
            &mut ids,
            ActorId(0),
            &possession,
            LogicalTime::ZERO,
            true,
            eff,
        );
        assert!(matches!(out, RequestOutcome::Completed { .. }));
        assert_eq!(
            budget.available.units,
            before - need,
            "M042: charged {} expected {}",
            before - budget.available.units,
            need
        );
    }
}
