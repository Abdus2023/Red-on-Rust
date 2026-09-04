//! Reference pure CEK (M2 + M3 + M4 Attenuate + M5 Request).
//!
//! Independently authored transition relation (R-REF-02). Does not import or
//! call `ror_runtime` / `ror_kernel`. Shared domain types only from `ror-core`.
//! M4 attenuation uses [`crate::cap_algebra::RefCapabilityStore`].
//! M5 Request uses [`crate::effect_model`] (independent journal/host).
//!
//! M2: Value/Var/Let/Seq/If.
//! M3: Lambda/Call — lexical capture, LTR args, arity-before-args.
//! M4: Attenuate via independent reference store.
//! M5: Request — capability first, non-cap SC, params LTR, gates + Issued.

use ror_core::capability::{CapabilityContext, LogicalTime};
use ror_core::effect::{EffectIdAlloc, ThinBudget};
use ror_core::machine::{Environment, Expr, Fault, FunctionValue, Value};
use ror_core::types::{ActorId, CapRef};
use ror_core::Symbol;

use crate::cap_algebra::RefCapabilityStore;
use crate::effect_model::{
    ref_default_cost, ref_effect_from_values, ref_run_pipeline, RefHost, RefJournal,
    RefRequestOutcome,
};

pub const REF_MAX_STEPS_DEFAULT: u64 = 1_000_000;

/// Reference effect services bundle (independent of production EffectServices).
pub struct RefEffectServices<'a> {
    pub journal: &'a mut RefJournal,
    pub host: &'a mut dyn RefHost,
    pub budget: &'a mut ThinBudget,
    pub ids: &'a mut EffectIdAlloc,
    pub actor: ActorId,
    pub possession: &'a CapabilityContext,
    pub host_policy_ok: bool,
}

/// Reference continuation cell — distinct type from production frames.
#[derive(Clone, Debug, PartialEq, Eq)]
pub enum RefKont {
    AfterLet {
        name: Symbol,
        body: Expr,
        saved_env: Environment,
    },
    AfterFirst {
        second: Expr,
        saved_env: Environment,
    },
    AfterCond {
        then_branch: Expr,
        else_branch: Expr,
        saved_env: Environment,
    },
    /// Waiting for operator value of a Call.
    WaitingOp {
        arg_exprs: Vec<Expr>,
        caller_env: Environment,
    },
    /// Waiting for the next argument value (LTR).
    WaitingArg {
        function: FunctionValue,
        got: Vec<Value>,
        rest: Vec<Expr>,
        caller_env: Environment,
    },
    /// M4: waiting for capability value of Attenuate.
    WaitingAttCap {
        constraint: Expr,
        saved_env: Environment,
    },
    /// M4: waiting for constraint value; then derive.
    WaitingAttConstraint {
        parent: CapRef,
        saved_env: Environment,
    },
    /// M5: waiting for capability of Request (non-cap short-circuit).
    WaitingReqCap {
        operation: Expr,
        target: Expr,
        params: Vec<Expr>,
        saved_env: Environment,
    },
    WaitingReqOp {
        capability: CapRef,
        target: Expr,
        params: Vec<Expr>,
        caller_env: Environment,
    },
    WaitingReqTarget {
        capability: CapRef,
        operation: Value,
        params: Vec<Expr>,
        caller_env: Environment,
    },
    WaitingReqArg {
        capability: CapRef,
        operation: Value,
        target: Value,
        got: Vec<Value>,
        rest: Vec<Expr>,
        caller_env: Environment,
    },
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub enum RefOutcome {
    Running,
    Halted(Value),
    Fault(Fault),
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct RefState {
    pub expr: Expr,
    pub env: Environment,
    pub kont: Vec<RefKont>,
    pub outcome: RefOutcome,
    pub logical_time: LogicalTime,
}

impl RefState {
    pub fn new(expr: Expr) -> Self {
        Self {
            expr,
            env: Environment::empty(),
            kont: Vec::new(),
            outcome: RefOutcome::Running,
            logical_time: LogicalTime::ZERO,
        }
    }

    pub fn at_time(mut self, t: LogicalTime) -> Self {
        self.logical_time = t;
        self
    }
}

/// One reference transition. Returns false when already terminal.
pub fn step(state: &mut RefState, store: &mut RefCapabilityStore) -> bool {
    step_with_effects(state, store, None)
}

/// Reference transition with optional M5 effect services.
pub fn step_with_effects(
    state: &mut RefState,
    store: &mut RefCapabilityStore,
    effects: Option<&mut RefEffectServices<'_>>,
) -> bool {
    if !matches!(state.outcome, RefOutcome::Running) {
        return false;
    }

    let expr = std::mem::replace(&mut state.expr, Expr::Value(Value::Unit));
    match expr {
        Expr::Value(v) => deliver(state, v, store, effects),
        Expr::Var(sym) => match state.env.lookup(sym) {
            Some(v) => {
                let v = v.clone();
                deliver(state, v, store, effects);
            }
            None => {
                state.outcome = RefOutcome::Fault(Fault::UnboundVariable(sym));
            }
        },
        Expr::Let { name, value, body } => {
            let saved = state.env.clone();
            state.kont.push(RefKont::AfterLet {
                name,
                body: *body,
                saved_env: saved,
            });
            state.expr = *value;
        }
        Expr::Seq { first, second } => {
            let saved = state.env.clone();
            state.kont.push(RefKont::AfterFirst {
                second: *second,
                saved_env: saved,
            });
            state.expr = *first;
        }
        Expr::If {
            condition,
            then_branch,
            else_branch,
        } => {
            let saved = state.env.clone();
            state.kont.push(RefKont::AfterCond {
                then_branch: *then_branch,
                else_branch: *else_branch,
                saved_env: saved,
            });
            state.expr = *condition;
        }
        Expr::Lambda { params, body } => {
            let f = Value::Function(FunctionValue {
                params,
                body,
                env: state.env.clone(),
            });
            deliver(state, f, store, effects);
        }
        Expr::Call { func, args } => {
            let caller = state.env.clone();
            state.kont.push(RefKont::WaitingOp {
                arg_exprs: args,
                caller_env: caller,
            });
            state.expr = *func;
        }
        Expr::Attenuate { cap, constraint } => {
            let saved = state.env.clone();
            state.kont.push(RefKont::WaitingAttCap {
                constraint: *constraint,
                saved_env: saved,
            });
            state.expr = *cap;
        }
        Expr::Request {
            capability,
            operation,
            target,
            params,
        } => {
            let saved = state.env.clone();
            state.kont.push(RefKont::WaitingReqCap {
                operation: *operation,
                target: *target,
                params,
                saved_env: saved,
            });
            state.expr = *capability;
        }
        Expr::Spawn { .. } => {
            state.outcome = RefOutcome::Fault(Fault::UnsupportedInM2 { form: "Spawn" });
        }
        Expr::Send { .. } => {
            state.outcome = RefOutcome::Fault(Fault::UnsupportedInM2 { form: "Send" });
        }
        Expr::Receive => {
            state.outcome = RefOutcome::Fault(Fault::UnsupportedInM2 { form: "Receive" });
        }
        Expr::Delegate { .. } => {
            state.outcome = RefOutcome::Fault(Fault::UnsupportedInM2 { form: "Delegate" });
        }
        Expr::Yield => {
            state.outcome = RefOutcome::Fault(Fault::UnsupportedInM2 { form: "Yield" });
        }
        Expr::Halt => {
            state.outcome = RefOutcome::Fault(Fault::UnsupportedInM2 { form: "Halt" });
        }
    }
    true
}

/// Deliver a value to the top kont or halt (reference value-return).
fn deliver(
    state: &mut RefState,
    value: Value,
    store: &mut RefCapabilityStore,
    effects: Option<&mut RefEffectServices<'_>>,
) {
    match state.kont.pop() {
        None => {
            state.outcome = RefOutcome::Halted(value);
        }
        Some(RefKont::AfterLet {
            name,
            body,
            saved_env,
        }) => {
            state.env = saved_env.extend(name, value);
            state.expr = body;
        }
        Some(RefKont::AfterFirst { second, saved_env }) => {
            let _ = value;
            state.env = saved_env;
            state.expr = second;
        }
        Some(RefKont::AfterCond {
            then_branch,
            else_branch,
            saved_env,
        }) => match value {
            Value::Bool(true) => {
                state.env = saved_env;
                state.expr = then_branch;
            }
            Value::Bool(false) => {
                state.env = saved_env;
                state.expr = else_branch;
            }
            other => {
                state.outcome = RefOutcome::Fault(Fault::TypeError {
                    expected: "Bool",
                    actual: kind_of(&other),
                });
            }
        },
        Some(RefKont::WaitingOp {
            arg_exprs,
            caller_env,
        }) => {
            let function = match value {
                Value::Function(f) => f,
                other => {
                    state.outcome = RefOutcome::Fault(Fault::TypeError {
                        expected: "Function",
                        actual: kind_of(&other),
                    });
                    return;
                }
            };
            if arg_exprs.len() != function.params.len() {
                state.outcome = RefOutcome::Fault(Fault::ArityMismatch {
                    expected: function.params.len(),
                    actual: arg_exprs.len(),
                });
                return;
            }
            if arg_exprs.is_empty() {
                install_body(state, function, Vec::new());
                return;
            }
            let mut rest = arg_exprs;
            let first = rest.remove(0);
            state.kont.push(RefKont::WaitingArg {
                function,
                got: Vec::new(),
                rest,
                caller_env: caller_env.clone(),
            });
            state.env = caller_env;
            state.expr = first;
        }
        Some(RefKont::WaitingArg {
            function,
            mut got,
            mut rest,
            caller_env,
        }) => {
            got.push(value);
            if rest.is_empty() {
                install_body(state, function, got);
                return;
            }
            let next = rest.remove(0);
            state.kont.push(RefKont::WaitingArg {
                function,
                got,
                rest,
                caller_env: caller_env.clone(),
            });
            state.env = caller_env;
            state.expr = next;
        }
        Some(RefKont::WaitingAttCap {
            constraint,
            saved_env,
        }) => {
            let parent = match value {
                Value::Capability(c) => c,
                other => {
                    state.outcome = RefOutcome::Fault(Fault::TypeError {
                        expected: "Capability",
                        actual: kind_of(&other),
                    });
                    return;
                }
            };
            state.kont.push(RefKont::WaitingAttConstraint {
                parent,
                saved_env: saved_env.clone(),
            });
            state.env = saved_env;
            state.expr = constraint;
        }
        Some(RefKont::WaitingAttConstraint { parent, saved_env }) => {
            let constraint = match value {
                Value::Constraint(c) => c,
                other => {
                    state.outcome = RefOutcome::Fault(Fault::TypeError {
                        expected: "Constraint",
                        actual: kind_of(&other),
                    });
                    return;
                }
            };
            match store.derive(parent, &constraint, state.logical_time) {
                Ok(child) => {
                    state.env = saved_env;
                    deliver(state, Value::Capability(child), store, effects);
                }
                Err(f) => {
                    state.outcome = RefOutcome::Fault(f);
                }
            }
        }
        Some(RefKont::WaitingReqCap {
            operation,
            target,
            params,
            saved_env,
        }) => {
            let cap = match value {
                Value::Capability(c) => c,
                other => {
                    state.outcome = RefOutcome::Fault(Fault::TypeError {
                        expected: "Capability",
                        actual: kind_of(&other),
                    });
                    return;
                }
            };
            state.kont.push(RefKont::WaitingReqOp {
                capability: cap,
                target,
                params,
                caller_env: saved_env.clone(),
            });
            state.env = saved_env;
            state.expr = operation;
        }
        Some(RefKont::WaitingReqOp {
            capability,
            target,
            params,
            caller_env,
        }) => {
            state.kont.push(RefKont::WaitingReqTarget {
                capability,
                operation: value,
                params,
                caller_env: caller_env.clone(),
            });
            state.env = caller_env;
            state.expr = target;
        }
        Some(RefKont::WaitingReqTarget {
            capability,
            operation,
            params,
            caller_env,
        }) => {
            let mut rest = params;
            if rest.is_empty() {
                finish_ref_request(
                    state,
                    store,
                    effects,
                    capability,
                    operation,
                    value,
                    Vec::new(),
                );
                return;
            }
            let first = rest.remove(0);
            state.kont.push(RefKont::WaitingReqArg {
                capability,
                operation,
                target: value,
                got: Vec::new(),
                rest,
                caller_env: caller_env.clone(),
            });
            state.env = caller_env;
            state.expr = first;
        }
        Some(RefKont::WaitingReqArg {
            capability,
            operation,
            target,
            mut got,
            mut rest,
            caller_env,
        }) => {
            got.push(value);
            if rest.is_empty() {
                finish_ref_request(state, store, effects, capability, operation, target, got);
                return;
            }
            let next = rest.remove(0);
            state.kont.push(RefKont::WaitingReqArg {
                capability,
                operation,
                target,
                got,
                rest,
                caller_env: caller_env.clone(),
            });
            state.env = caller_env;
            state.expr = next;
        }
    }
}

fn finish_ref_request(
    state: &mut RefState,
    store: &mut RefCapabilityStore,
    effects: Option<&mut RefEffectServices<'_>>,
    capability: CapRef,
    operation: Value,
    target: Value,
    params: Vec<Value>,
) {
    let effects = match effects {
        Some(e) => e,
        None => {
            state.outcome = RefOutcome::Fault(Fault::UnsupportedInM2 { form: "Request" });
            return;
        }
    };
    let effect = match ref_effect_from_values(
        capability,
        &operation,
        &target,
        &params,
        ref_default_cost(),
    ) {
        Ok(e) => e,
        Err(f) => {
            state.outcome = RefOutcome::Fault(f);
            return;
        }
    };
    match ref_run_pipeline(
        store,
        effects.journal,
        effects.host,
        effects.budget,
        effects.ids,
        effects.actor,
        effects.possession,
        state.logical_time,
        effects.host_policy_ok,
        effect,
    ) {
        RefRequestOutcome::Completed { value, .. } => {
            deliver(state, value, store, Some(effects));
        }
        RefRequestOutcome::HostFailed { fault, .. } | RefRequestOutcome::Denied(fault) => {
            state.outcome = RefOutcome::Fault(fault);
        }
    }
}

/// ρ' = ρ_closure[xi↦vi]; set body as control (lexical apply).
fn install_body(state: &mut RefState, function: FunctionValue, args: Vec<Value>) {
    let mut env = function.env;
    for (p, v) in function.params.into_iter().zip(args.into_iter()) {
        env = env.extend(p, v);
    }
    state.env = env;
    state.expr = *function.body;
}

fn kind_of(v: &Value) -> &'static str {
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

pub fn evaluate(expr: Expr, max_steps: u64) -> Result<Value, Fault> {
    let mut store = RefCapabilityStore::new();
    evaluate_with_store(expr, max_steps, &mut store, LogicalTime::ZERO)
}

pub fn evaluate_with_store(
    expr: Expr,
    max_steps: u64,
    store: &mut RefCapabilityStore,
    t: LogicalTime,
) -> Result<Value, Fault> {
    let mut state = RefState::new(expr).at_time(t);
    for _ in 0..max_steps {
        if !matches!(state.outcome, RefOutcome::Running) {
            break;
        }
        step(&mut state, store);
    }
    match state.outcome {
        RefOutcome::Halted(v) => Ok(v),
        RefOutcome::Fault(f) => Err(f),
        RefOutcome::Running => Err(Fault::UnsupportedInM2 { form: "step_limit" }),
    }
}

/// M5-aware reference evaluate with effect services.
pub fn evaluate_request_ref(
    expr: Expr,
    max_steps: u64,
    store: &mut RefCapabilityStore,
    t: LogicalTime,
    effects: &mut RefEffectServices<'_>,
) -> Result<Value, Fault> {
    let mut state = RefState::new(expr).at_time(t);
    for _ in 0..max_steps {
        if !matches!(state.outcome, RefOutcome::Running) {
            break;
        }
        step_with_effects(&mut state, store, Some(effects));
    }
    match state.outcome {
        RefOutcome::Halted(v) => Ok(v),
        RefOutcome::Fault(f) => Err(f),
        RefOutcome::Running => Err(Fault::UnsupportedInM2 { form: "step_limit" }),
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use ror_core::machine::sugar::{bool_v, call, if_, int, lambda, let_, seq, var};

    #[test]
    fn basic_let_seq_if() {
        assert_eq!(
            evaluate(let_(1, int(5), var(1)), REF_MAX_STEPS_DEFAULT),
            Ok(Value::Integer(5))
        );
        assert_eq!(
            evaluate(seq(int(1), int(2)), REF_MAX_STEPS_DEFAULT),
            Ok(Value::Integer(2))
        );
        assert_eq!(
            evaluate(if_(bool_v(false), int(1), int(9)), REF_MAX_STEPS_DEFAULT),
            Ok(Value::Integer(9))
        );
    }

    #[test]
    fn unbound() {
        assert_eq!(
            evaluate(var(3), REF_MAX_STEPS_DEFAULT),
            Err(Fault::UnboundVariable(Symbol(3)))
        );
    }

    #[test]
    fn lambda_call_identity() {
        assert_eq!(
            evaluate(
                call(lambda(&[1], var(1)), vec![int(42)]),
                REF_MAX_STEPS_DEFAULT
            ),
            Ok(Value::Integer(42))
        );
    }

    #[test]
    fn closure_lexical() {
        let e = let_(
            1,
            int(1),
            let_(
                2,
                lambda(&[], var(1)),
                let_(1, int(2), call(var(2), vec![])),
            ),
        );
        assert_eq!(evaluate(e, REF_MAX_STEPS_DEFAULT), Ok(Value::Integer(1)));
    }

    #[test]
    fn arity_mismatch() {
        assert_eq!(
            evaluate(call(lambda(&[1], var(1)), vec![]), REF_MAX_STEPS_DEFAULT),
            Err(Fault::ArityMismatch {
                expected: 1,
                actual: 0
            })
        );
    }
}
