//! Independent M5 effect / Request observation model (R-REF-02).
//!
//! Does **not** import `ror-runtime`, `ror-kernel`, `ror-host`, or
//! `ror-persistence`. Reimplements gate ordering + mock journal/host for
//! differential comparison against production observations.

use ror_core::capability::{authorized, CapabilityContext, EffectDesc, LogicalTime, Op};
use ror_core::digest::EffectDigest;
use ror_core::effect::{
    op_from_i64, Consumable, Effect, EffectCost, EffectIdAlloc, EffectReceipt, EffectRequest,
    HostFaultCode, IssuanceRecord, Params, ReceiptValue, Reserved, Target, ThinBudget,
};
use ror_core::machine::{Fault, Value};
use ror_core::types::{ActorId, CapRef, EffectId};

use crate::cap_algebra::RefCapabilityStore;

pub const REF_DELTA_T_REQUEST: u64 = 1;

/// Independent journal double (not production MemoryJournal).
#[derive(Clone, Debug, Default)]
pub struct RefJournal {
    durable: Vec<IssuanceRecord>,
    pending: Vec<IssuanceRecord>,
    fail_next_append: bool,
    fail_next_sync: bool,
}

impl RefJournal {
    pub fn new() -> Self {
        Self::default()
    }

    pub fn fail_next_append(&mut self) {
        self.fail_next_append = true;
    }

    pub fn durable_records(&self) -> &[IssuanceRecord] {
        &self.durable
    }

    pub fn is_durably_issued(&self, id: EffectId) -> bool {
        self.durable.iter().any(|r| match r {
            IssuanceRecord::Issued { id: i, .. } => *i == id,
            _ => false,
        })
    }

    fn append(&mut self, record: IssuanceRecord) -> Result<(), Fault> {
        if self.fail_next_append {
            self.fail_next_append = false;
            return Err(Fault::PersistenceError);
        }
        if let IssuanceRecord::Issued { id, digest, .. } = &record {
            let ok = self
                .pending
                .iter()
                .chain(self.durable.iter())
                .any(|r| matches!(r, IssuanceRecord::Prepared { id: i, digest: d, .. } if i == id && d == digest));
            if !ok {
                return Err(Fault::PersistenceError);
            }
        }
        self.pending.push(record);
        Ok(())
    }

    fn sync(&mut self) -> Result<(), Fault> {
        if self.fail_next_sync {
            self.fail_next_sync = false;
            return Err(Fault::PersistenceError);
        }
        self.durable.append(&mut self.pending);
        Ok(())
    }
}

/// Independent host double.
pub trait RefHost {
    fn execute(&mut self, request: &EffectRequest) -> Result<EffectReceipt, Fault>;
}

#[derive(Clone, Debug, Default)]
pub struct RefMockHost {
    pub calls: Vec<EffectId>,
}

impl RefHost for RefMockHost {
    fn execute(&mut self, request: &EffectRequest) -> Result<EffectReceipt, Fault> {
        self.calls.push(request.id);
        Ok(EffectReceipt {
            id: request.id,
            effect_digest: request.digest,
            result: Ok(ReceiptValue::Unit),
        })
    }
}

#[derive(Clone, Debug, Default)]
pub struct RefPanicHost {
    pub invoked: bool,
}

impl RefHost for RefPanicHost {
    fn execute(&mut self, request: &EffectRequest) -> Result<EffectReceipt, Fault> {
        self.invoked = true;
        panic!(
            "RefPanicHost: execute without Issued (id={:?}) — GI-SEC-07",
            request.id
        );
    }
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub enum RefRequestOutcome {
    Completed { id: EffectId, value: Value },
    HostFailed { id: EffectId, fault: Fault },
    Denied(Fault),
}

/// Independent authorize using reference store (possession + Valid + algebra).
fn ref_authorize(
    store: &RefCapabilityStore,
    possession: &CapabilityContext,
    cap: CapRef,
    effect: &Effect,
    t: LogicalTime,
) -> Result<(), Fault> {
    if !possession.contains(cap) {
        return Err(Fault::Unauthorized);
    }
    store.valid_result(cap, t)?;
    let auth = store
        .authority_snapshot(cap)
        .ok_or(Fault::CapabilityRevoked)?;
    let core_auth = auth.to_core();
    let desc = EffectDesc {
        op: effect.operation,
        target: effect.target.0,
        param_tag: effect.params.primary_tag(),
        cost_units: effect
            .cost
            .issue
            .units
            .saturating_add(effect.cost.complete_max.units),
    };
    if authorized(&core_auth, &desc, t) {
        Ok(())
    } else {
        Err(Fault::Unauthorized)
    }
}

pub fn ref_effect_from_values(
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
                actual: "non-int",
            })
        }
    };
    let target = match target_v {
        Value::Integer(n) if *n >= 0 && *n <= i64::from(u32::MAX) => Target(*n as u32),
        _ => {
            return Err(Fault::TypeError {
                expected: "Integer(Target)",
                actual: "bad",
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
                    actual: "bad",
                })
            }
        }
    }
    Ok(Effect::new(cap, op, target, Params::from_tags(tags), cost))
}

/// Independent 16-step gate pipeline (mirrors production order; separate code).
#[allow(clippy::too_many_arguments)]
pub fn ref_run_pipeline(
    store: &RefCapabilityStore,
    journal: &mut RefJournal,
    host: &mut dyn RefHost,
    budget: &mut ThinBudget,
    ids: &mut EffectIdAlloc,
    actor: ActorId,
    possession: &CapabilityContext,
    t: LogicalTime,
    host_policy_ok: bool,
    effect: Effect,
) -> RefRequestOutcome {
    // Gate 5
    if let Err(e) = store.valid_result(effect.capability, t) {
        return RefRequestOutcome::Denied(e);
    }
    // Gate 6
    if let Err(e) = ref_authorize(store, possession, effect.capability, &effect, t) {
        return RefRequestOutcome::Denied(e);
    }
    // Gate 8
    let need = match effect.cost.issue_plus_complete_max() {
        Some(n) => n,
        None => return RefRequestOutcome::Denied(Fault::BudgetExhausted),
    };
    if !need.saturating_leq(budget.available) {
        return RefRequestOutcome::Denied(Fault::BudgetExhausted);
    }
    // Gate 9
    if effect.cost.reserve.slots > budget.reserved.slots {
        return RefRequestOutcome::Denied(Fault::BudgetExhausted);
    }
    // Gate 10
    if let Some(w) = budget.deadline {
        let t_after = LogicalTime(t.get().saturating_add(REF_DELTA_T_REQUEST));
        if t_after > w {
            return RefRequestOutcome::Denied(Fault::DeadlineExceeded);
        }
    }
    // Gate 11
    if !host_policy_ok {
        return RefRequestOutcome::Denied(Fault::HostPolicyDenied);
    }

    let prev_next = ids.peek_next();
    let prev_avail = budget.available;
    let prev_res = budget.reserved;

    let id = ids.allocate();
    let effect_bytes = effect.canonical_bytes();
    let digest = EffectDigest::of_bytes(&effect_bytes);
    let cost = effect.cost;

    budget.available = Consumable::new(budget.available.units.saturating_sub(need.units));
    budget.reserved = Reserved::new(budget.reserved.slots.saturating_sub(cost.reserve.slots));

    let prep = IssuanceRecord::Prepared {
        id,
        actor,
        digest,
        effect_bytes: effect_bytes.clone(),
        cost,
    };
    if let Err(e) = journal.append(prep) {
        *ids = EffectIdAlloc::with_start(prev_next);
        budget.available = prev_avail;
        budget.reserved = prev_res;
        return RefRequestOutcome::Denied(e);
    }
    if let Err(e) = journal.sync() {
        *ids = EffectIdAlloc::with_start(prev_next);
        budget.available = prev_avail;
        budget.reserved = prev_res;
        return RefRequestOutcome::Denied(e);
    }
    let iss = IssuanceRecord::Issued {
        id,
        actor,
        digest,
        effect_bytes: effect_bytes.clone(),
        cost,
    };
    if let Err(e) = journal.append(iss) {
        *ids = EffectIdAlloc::with_start(prev_next);
        budget.available = prev_avail;
        budget.reserved = prev_res;
        return RefRequestOutcome::Denied(e);
    }
    if let Err(e) = journal.sync() {
        *ids = EffectIdAlloc::with_start(prev_next);
        budget.available = prev_avail;
        budget.reserved = prev_res;
        return RefRequestOutcome::Denied(e);
    }

    assert!(
        journal.is_durably_issued(id),
        "ref GI-SEC-07: Issued before host"
    );

    let request = EffectRequest {
        id,
        actor,
        digest,
        effect_bytes,
        cost,
        effect,
    };

    match host.execute(&request) {
        Ok(receipt) => {
            if receipt.id != request.id || receipt.effect_digest != request.digest {
                return RefRequestOutcome::HostFailed {
                    id,
                    fault: Fault::ReplayCorruption,
                };
            }
            match receipt.result {
                Ok(rv) => RefRequestOutcome::Completed {
                    id,
                    value: match rv {
                        ReceiptValue::Unit => Value::Unit,
                        ReceiptValue::Bool(b) => Value::Bool(b),
                        ReceiptValue::Integer(n) => Value::Integer(n),
                        ReceiptValue::String(s) => Value::String(s),
                        ReceiptValue::Bytes(b) => Value::Bytes(b),
                    },
                },
                Err(code) if code == HostFaultCode::POLICY_DENIED => {
                    RefRequestOutcome::HostFailed {
                        id,
                        fault: Fault::HostPolicyDenied,
                    }
                }
                Err(code) => RefRequestOutcome::HostFailed {
                    id,
                    fault: Fault::HostFault { code: code.0 },
                },
            }
        }
        Err(f) => RefRequestOutcome::HostFailed { id, fault: f },
    }
}

/// Default cost matching production thin default.
pub fn ref_default_cost() -> EffectCost {
    EffectCost::new(1, 1, 0)
}

/// FileRead op tag as Integer value (production/ref Op tag 0).
pub fn op_fileread_value() -> Value {
    Value::Integer(Op::FileRead as u8 as i64)
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::cap_algebra::{RefAuthority, RefCapabilityStore, RefOpAuthority};
    use ror_core::capability::{Lifetime, Op, ParamConstraint, ResourceLimit, Scope};

    fn seed(store: &mut RefCapabilityStore) -> (CapRef, CapabilityContext) {
        let mut a = RefAuthority::empty();
        a.insert(
            Op::FileRead,
            RefOpAuthority {
                scope: Scope::from_targets(vec![1, 2, 3]),
                params: ParamConstraint::any(),
                resources: ResourceLimit::new(100),
                lifetime: Lifetime::always(),
            },
        );
        let cap = store.grant_root(a, Lifetime::always());
        let mut ctx = CapabilityContext::empty();
        ctx.insert(cap);
        (cap, ctx)
    }

    #[test]
    fn ref_happy_path() {
        let mut store = RefCapabilityStore::new();
        let (cap, possession) = seed(&mut store);
        let mut j = RefJournal::new();
        let mut h = RefMockHost::default();
        let mut budget = ThinBudget::generous();
        let mut ids = EffectIdAlloc::new();
        let effect = Effect::new(
            cap,
            Op::FileRead,
            Target(1),
            Params::from_tags(vec![0]),
            ref_default_cost(),
        );
        let out = ref_run_pipeline(
            &store,
            &mut j,
            &mut h,
            &mut budget,
            &mut ids,
            ActorId(0),
            &possession,
            LogicalTime::ZERO,
            true,
            effect,
        );
        assert!(matches!(out, RefRequestOutcome::Completed { .. }));
        assert_eq!(h.calls.len(), 1);
    }

    #[test]
    fn ref_deny_no_host() {
        let mut store = RefCapabilityStore::new();
        let (cap, _) = seed(&mut store);
        let empty = CapabilityContext::empty();
        let mut j = RefJournal::new();
        let mut h = RefPanicHost::default();
        let mut budget = ThinBudget::generous();
        let mut ids = EffectIdAlloc::new();
        let effect = Effect::new(
            cap,
            Op::FileRead,
            Target(1),
            Params::empty(),
            ref_default_cost(),
        );
        let out = ref_run_pipeline(
            &store,
            &mut j,
            &mut h,
            &mut budget,
            &mut ids,
            ActorId(0),
            &empty,
            LogicalTime::ZERO,
            true,
            effect,
        );
        assert!(matches!(
            out,
            RefRequestOutcome::Denied(Fault::Unauthorized)
        ));
        assert!(!h.invoked);
    }
}
