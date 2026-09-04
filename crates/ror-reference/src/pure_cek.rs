//! Reference pure CEK (M2: Value/Var/Let/Seq/If).
//!
//! Deliberately boring, independently written transition relation.
//! Does not import or call `ror_runtime` helpers (R-REF-02).

use ror_core::machine::{Environment, Expr, Fault, Value};
use ror_core::Symbol;

pub const REF_MAX_STEPS_DEFAULT: u64 = 1_000_000;

/// Reference continuation cell — independent representation from production frames.
///
/// Same semantic roles as R-CEK-03 pure frames; distinct Rust type so production
/// and reference cannot share transition helpers by accident.
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
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub enum RefOutcome {
    Running,
    Halted(Value),
    Fault(Fault),
}

/// Reference machine state (independent of production `EvalState`).
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct RefState {
    pub expr: Expr,
    pub env: Environment,
    pub kont: Vec<RefKont>,
    pub outcome: RefOutcome,
}

impl RefState {
    pub fn new(expr: Expr) -> Self {
        Self {
            expr,
            env: Environment::empty(),
            kont: Vec::new(),
            outcome: RefOutcome::Running,
        }
    }
}

/// One reference transition. Returns false when already terminal.
pub fn step(state: &mut RefState) -> bool {
    if !matches!(state.outcome, RefOutcome::Running) {
        return false;
    }

    let expr = std::mem::replace(&mut state.expr, Expr::Value(Value::Unit));
    match expr {
        Expr::Value(v) => {
            apply_value(state, v);
        }
        Expr::Var(sym) => match state.env.lookup(sym) {
            Some(v) => {
                let v = v.clone();
                apply_value(state, v);
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
        Expr::Lambda { .. } => {
            state.outcome = RefOutcome::Fault(Fault::UnsupportedInM2 { form: "Lambda" });
        }
        Expr::Call { .. } => {
            state.outcome = RefOutcome::Fault(Fault::UnsupportedInM2 { form: "Call" });
        }
        Expr::Attenuate { .. } => {
            state.outcome = RefOutcome::Fault(Fault::UnsupportedInM2 { form: "Attenuate" });
        }
        Expr::Request { .. } => {
            state.outcome = RefOutcome::Fault(Fault::UnsupportedInM2 { form: "Request" });
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
        Expr::Yield => {
            state.outcome = RefOutcome::Fault(Fault::UnsupportedInM2 { form: "Yield" });
        }
        Expr::Halt => {
            state.outcome = RefOutcome::Fault(Fault::UnsupportedInM2 { form: "Halt" });
        }
    }
    true
}

fn apply_value(state: &mut RefState, value: Value) {
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
            // First value discarded; restore env and evaluate second.
            let _discarded = value;
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
    }
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
    }
}

pub fn evaluate(expr: Expr, max_steps: u64) -> Result<Value, Fault> {
    let mut state = RefState::new(expr);
    for _ in 0..max_steps {
        if !matches!(state.outcome, RefOutcome::Running) {
            break;
        }
        step(&mut state);
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
    use ror_core::machine::sugar::{bool_v, if_, int, let_, seq, var};

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
}
