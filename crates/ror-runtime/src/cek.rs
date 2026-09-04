//! Explicit Control–Environment–Continuation machine (R-CEK-01).
//!
//! **M2:** Value / Var / Let / Seq / If.
//! **M3:** Lambda / Call (R-CEK-04/05, REQ-CEK-008…017).
//!
//! No recursive evaluator calls for nesting depth (REQ-CEK-002): nesting lives
//! in [`Continuation`]. Frames are in-memory only (U-02 OPEN).

use ror_core::machine::{Environment, Expr, Fault, FunctionValue, Value};
use ror_core::Symbol;

/// Default fuel for [`evaluate`]. Not a semantic budget (MOD-04 deferred).
pub const CEK_MAX_STEPS_DEFAULT: u64 = 1_000_000;

/// Pure-subset continuation frames (R-CEK-03): M2 frames + M3 Call* frames.
///
/// Not a wire type (U-02 OPEN). Treat layout as provisional.
#[derive(Clone, Debug, PartialEq, Eq)]
pub enum PureFrame {
    LetValue {
        name: Symbol,
        body: Expr,
        env: Environment,
    },
    Seq {
        second: Expr,
        env: Environment,
    },
    If {
        then_branch: Expr,
        else_branch: Expr,
        env: Environment,
    },
    /// After pushing: evaluate `func`; on resume: arity check then args.
    /// `env` is the **call-site** environment (R-CEK-03).
    CallFunction {
        args: Vec<Expr>,
        env: Environment,
    },
    /// Evaluating arguments left-to-right under `caller_env`.
    /// `function` carries the **closure** lexical env (≠ caller_env).
    CallArgument {
        function: FunctionValue,
        evaluated: Vec<Value>,
        remaining: Vec<Expr>,
        caller_env: Environment,
    },
}

/// Frame type alias. Provisional; not a wire ABI (U-02).
pub type Frame = PureFrame;

/// Explicit continuation stack (R-CEK-01).
#[derive(Clone, Debug, PartialEq, Eq, Default)]
pub struct Continuation {
    frames: Vec<PureFrame>,
}

impl Continuation {
    pub fn empty() -> Self {
        Self { frames: Vec::new() }
    }

    pub fn push(&mut self, frame: PureFrame) {
        self.frames.push(frame);
    }

    pub fn pop(&mut self) -> Option<PureFrame> {
        self.frames.pop()
    }

    pub fn is_empty(&self) -> bool {
        self.frames.is_empty()
    }

    pub fn len(&self) -> usize {
        self.frames.len()
    }
}

/// Local CEK control state (R-CEK-01).
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct EvalState {
    pub expr: Expr,
    pub env: Environment,
    pub continuation: Continuation,
}

impl EvalState {
    pub fn new(expr: Expr) -> Self {
        Self {
            expr,
            env: Environment::empty(),
            continuation: Continuation::empty(),
        }
    }

    pub fn with_env(expr: Expr, env: Environment) -> Self {
        Self {
            expr,
            env,
            continuation: Continuation::empty(),
        }
    }
}

/// Provisional step outcome (U-26 OPEN).
#[derive(Clone, Debug, PartialEq, Eq)]
pub enum StepResult {
    Continue,
    Halted(Value),
    Fault(Fault),
}

/// One pure CEK transition. Stack depth is O(1) in program nesting.
pub fn step(state: &mut EvalState) -> StepResult {
    let expr = std::mem::replace(&mut state.expr, Expr::Value(Value::Unit));
    match expr {
        Expr::Value(v) => continue_with_value(state, v),
        Expr::Var(symbol) => lookup_variable(state, symbol),
        Expr::Let { name, value, body } => enter_let(state, name, *value, *body),
        Expr::Seq { first, second } => enter_seq(state, *first, *second),
        Expr::If {
            condition,
            then_branch,
            else_branch,
        } => enter_if(state, *condition, *then_branch, *else_branch),
        Expr::Lambda { params, body } => enter_lambda(state, params, *body),
        Expr::Call { func, args } => enter_call(state, *func, args),
        Expr::Attenuate { .. } => StepResult::Fault(Fault::UnsupportedInM2 { form: "Attenuate" }),
        Expr::Request { .. } => StepResult::Fault(Fault::UnsupportedInM2 { form: "Request" }),
        Expr::Spawn { .. } => StepResult::Fault(Fault::UnsupportedInM2 { form: "Spawn" }),
        Expr::Send { .. } => StepResult::Fault(Fault::UnsupportedInM2 { form: "Send" }),
        Expr::Receive => StepResult::Fault(Fault::UnsupportedInM2 { form: "Receive" }),
        Expr::Yield => StepResult::Fault(Fault::UnsupportedInM2 { form: "Yield" }),
        Expr::Halt => StepResult::Fault(Fault::UnsupportedInM2 { form: "Halt" }),
    }
}

/// Drive the machine to Halt or Fault.
pub fn evaluate(expr: Expr, max_steps: u64) -> Result<Value, Fault> {
    let mut state = EvalState::new(expr);
    for _ in 0..max_steps {
        match step(&mut state) {
            StepResult::Continue => continue,
            StepResult::Halted(v) => return Ok(v),
            StepResult::Fault(f) => return Err(f),
        }
    }
    Err(Fault::UnsupportedInM2 { form: "step_limit" })
}

/// R-CEK-02 value-return: sole path that pops a frame or halts (REQ-CEK-023).
fn continue_with_value(state: &mut EvalState, value: Value) -> StepResult {
    match state.continuation.pop() {
        None => StepResult::Halted(value),
        Some(frame) => resume_frame(state, frame, value),
    }
}

fn resume_frame(state: &mut EvalState, frame: PureFrame, value: Value) -> StepResult {
    match frame {
        PureFrame::LetValue { name, body, env } => {
            state.env = env.extend(name, value);
            state.expr = body;
            StepResult::Continue
        }
        PureFrame::Seq { second, env } => {
            state.env = env;
            state.expr = second;
            StepResult::Continue
        }
        PureFrame::If {
            then_branch,
            else_branch,
            env,
        } => resume_if(state, then_branch, else_branch, env, value),
        PureFrame::CallFunction { args, env } => resume_call_function(state, args, env, value),
        PureFrame::CallArgument {
            function,
            evaluated,
            remaining,
            caller_env,
        } => resume_call_argument(state, function, evaluated, remaining, caller_env, value),
    }
}

// --- M2 entry / resume -------------------------------------------------------

fn enter_let(state: &mut EvalState, name: Symbol, value: Expr, body: Expr) -> StepResult {
    let env = state.env.clone();
    state.continuation.push(PureFrame::LetValue {
        name,
        body,
        env: env.clone(),
    });
    state.expr = value;
    StepResult::Continue
}

fn enter_seq(state: &mut EvalState, first: Expr, second: Expr) -> StepResult {
    let env = state.env.clone();
    state.continuation.push(PureFrame::Seq {
        second,
        env: env.clone(),
    });
    state.expr = first;
    StepResult::Continue
}

fn enter_if(
    state: &mut EvalState,
    condition: Expr,
    then_branch: Expr,
    else_branch: Expr,
) -> StepResult {
    let env = state.env.clone();
    state.continuation.push(PureFrame::If {
        then_branch,
        else_branch,
        env: env.clone(),
    });
    state.expr = condition;
    StepResult::Continue
}

fn resume_if(
    state: &mut EvalState,
    then_branch: Expr,
    else_branch: Expr,
    env: Environment,
    value: Value,
) -> StepResult {
    let condition = match value {
        Value::Bool(b) => b,
        other => {
            return StepResult::Fault(Fault::TypeError {
                expected: "Bool",
                actual: value_kind(&other),
            });
        }
    };
    state.env = env;
    state.expr = if condition { then_branch } else { else_branch };
    StepResult::Continue
}

fn lookup_variable(state: &mut EvalState, symbol: Symbol) -> StepResult {
    match state.env.lookup(symbol) {
        Some(value) => {
            let v = value.clone();
            continue_with_value(state, v)
        }
        None => StepResult::Fault(Fault::UnboundVariable(symbol)),
    }
}

// --- M3 Lambda (R-CEK-04) ----------------------------------------------------

/// Lambda: capture current env; produce FunctionValue; ordinary value-return.
fn enter_lambda(state: &mut EvalState, params: Vec<Symbol>, body: Expr) -> StepResult {
    let closure = Value::Function(FunctionValue {
        params,
        body: Box::new(body),
        env: state.env.clone(),
    });
    // Does not halt immediately — goes through value-return (REQ-CEK-012).
    continue_with_value(state, closure)
}

// --- M3 Call (R-CEK-05) ------------------------------------------------------

/// Enter Call: push CallFunction, evaluate operator first (REQ-CEK-013).
fn enter_call(state: &mut EvalState, func: Expr, args: Vec<Expr>) -> StepResult {
    let env = state.env.clone();
    state
        .continuation
        .push(PureFrame::CallFunction { args, env });
    state.expr = func;
    StepResult::Continue
}

/// After operator value: type-check Function, arity **before** any arg eval
/// (REQ-CEK-014 / CEK-CALL-ARITY-PRECHECK), then args LTR or apply.
fn resume_call_function(
    state: &mut EvalState,
    args: Vec<Expr>,
    caller_env: Environment,
    value: Value,
) -> StepResult {
    let function = match value {
        Value::Function(f) => f,
        other => {
            return StepResult::Fault(Fault::TypeError {
                expected: "Function",
                actual: value_kind(&other),
            });
        }
    };

    // Arity precheck BEFORE any argument evaluation (REQ-CEK-014).
    if args.len() != function.params.len() {
        return StepResult::Fault(Fault::ArityMismatch {
            expected: function.params.len(),
            actual: args.len(),
        });
    }

    let mut remaining = args;
    if remaining.is_empty() {
        return apply_function(state, function, Vec::new());
    }

    let first = remaining.remove(0);
    state.continuation.push(PureFrame::CallArgument {
        function,
        evaluated: Vec::new(),
        remaining,
        caller_env: caller_env.clone(),
    });
    state.env = caller_env;
    state.expr = first;
    StepResult::Continue
}

/// After one argument value: collect LTR; apply when done (REQ-CEK-013).
fn resume_call_argument(
    state: &mut EvalState,
    function: FunctionValue,
    mut evaluated: Vec<Value>,
    mut remaining: Vec<Expr>,
    caller_env: Environment,
    value: Value,
) -> StepResult {
    evaluated.push(value);

    if remaining.is_empty() {
        return apply_function(state, function, evaluated);
    }

    let next = remaining.remove(0);
    state.continuation.push(PureFrame::CallArgument {
        function,
        evaluated,
        remaining,
        caller_env: caller_env.clone(),
    });
    state.env = caller_env;
    state.expr = next;
    StepResult::Continue
}

/// Apply: ρ' = ρ_closure[xi ↦ vi]; evaluate body (REQ-CEK-015/016/017).
/// Body runs under residual continuation (R-CEK-02 value-return); no separate
/// Return frame in the frozen R-CEK-03 set (M3 preflight derivation).
fn apply_function(state: &mut EvalState, function: FunctionValue, args: Vec<Value>) -> StepResult {
    debug_assert_eq!(function.params.len(), args.len());
    let mut env = function.env;
    for (name, val) in function.params.into_iter().zip(args.into_iter()) {
        env = env.extend(name, val);
    }
    state.env = env;
    state.expr = *function.body;
    StepResult::Continue
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
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use ror_core::machine::sugar::{bool_v, call, if_, int, lambda, let_, seq, unit, var};
    use ror_core::machine::Value as MValue;

    fn run(expr: Expr) -> Result<MValue, Fault> {
        evaluate(expr, CEK_MAX_STEPS_DEFAULT)
    }

    // ----- M2 regression -----------------------------------------------------

    #[test]
    fn value_halts_on_empty_continuation() {
        assert_eq!(run(int(42)), Ok(MValue::Integer(42)));
        assert_eq!(run(unit()), Ok(MValue::Unit));
        assert_eq!(run(bool_v(true)), Ok(MValue::Bool(true)));
    }

    #[test]
    fn var_lookup_and_unbound() {
        let mut st = EvalState::with_env(
            var(1),
            Environment::empty().extend(Symbol(1), MValue::Integer(7)),
        );
        assert_eq!(step(&mut st), StepResult::Halted(MValue::Integer(7)));
        assert_eq!(run(var(99)), Err(Fault::UnboundVariable(Symbol(99))));
    }

    #[test]
    fn let_binds_and_body_sees_binding() {
        assert_eq!(run(let_(1, int(1), var(1))), Ok(MValue::Integer(1)));
    }

    #[test]
    fn let_shadowing() {
        assert_eq!(
            run(let_(1, int(1), let_(1, int(2), var(1)))),
            Ok(MValue::Integer(2))
        );
    }

    #[test]
    fn seq_evaluates_first_then_second() {
        assert_eq!(run(seq(int(1), int(2))), Ok(MValue::Integer(2)));
    }

    #[test]
    fn seq_order_observable_via_state() {
        let mut st = EvalState::new(seq(int(1), int(2)));
        assert_eq!(step(&mut st), StepResult::Continue);
        assert_eq!(st.expr, int(1));
        assert_eq!(st.continuation.len(), 1);
        assert_eq!(step(&mut st), StepResult::Continue);
        assert_eq!(st.expr, int(2));
        assert_eq!(st.continuation.len(), 0);
        assert_eq!(step(&mut st), StepResult::Halted(MValue::Integer(2)));
    }

    #[test]
    fn if_true_and_false_branches() {
        assert_eq!(
            run(if_(bool_v(true), int(1), int(0))),
            Ok(MValue::Integer(1))
        );
        assert_eq!(
            run(if_(bool_v(false), int(1), int(0))),
            Ok(MValue::Integer(0))
        );
    }

    #[test]
    fn if_non_bool_is_type_error() {
        assert_eq!(
            run(if_(int(1), int(2), int(3))),
            Err(Fault::TypeError {
                expected: "Bool",
                actual: "Integer",
            })
        );
    }

    #[test]
    fn nested_let_if() {
        let e = let_(1, bool_v(true), if_(var(1), int(10), int(20)));
        assert_eq!(run(e), Ok(MValue::Integer(10)));
    }

    #[test]
    fn continuation_plus_one_on_let_entry() {
        let mut st = EvalState::new(let_(1, int(1), var(1)));
        let before = st.continuation.len();
        assert_eq!(step(&mut st), StepResult::Continue);
        assert_eq!(st.continuation.len(), before + 1);
    }

    #[test]
    fn continuation_minus_one_on_resume() {
        let mut st = EvalState::new(let_(1, int(1), var(1)));
        step(&mut st);
        let before = st.continuation.len();
        assert_eq!(step(&mut st), StepResult::Continue);
        assert_eq!(st.continuation.len(), before - 1);
    }

    #[test]
    fn value_with_nonempty_k_does_not_halt() {
        let mut st = EvalState::new(int(5));
        st.continuation.push(PureFrame::Seq {
            second: int(9),
            env: Environment::empty(),
        });
        assert_eq!(step(&mut st), StepResult::Continue);
        assert_eq!(st.expr, int(9));
        assert!(st.continuation.is_empty());
        assert_eq!(step(&mut st), StepResult::Halted(MValue::Integer(9)));
    }

    #[test]
    fn deep_let_nest_is_stackless() {
        const N: u32 = 512;
        let mut e = var(N);
        for i in (1..=N).rev() {
            e = let_(i, int(i as i64), e);
        }
        assert_eq!(run(e), Ok(MValue::Integer(N as i64)));
    }

    #[test]
    fn wide_seq_chain_is_stackless() {
        const N: u32 = 256;
        let mut e = int(N as i64);
        for i in (0..N).rev() {
            e = seq(int(i as i64), e);
        }
        assert_eq!(run(e), Ok(MValue::Integer(N as i64)));
    }

    #[test]
    fn determinism_repeated_eval() {
        let e = let_(
            1,
            int(3),
            if_(bool_v(true), seq(var(1), let_(1, int(4), var(1))), int(0)),
        );
        let a = run(e.clone());
        let b = run(e.clone());
        let c = run(e);
        assert_eq!(a, b);
        assert_eq!(b, c);
        assert_eq!(a, Ok(MValue::Integer(4)));
    }

    #[test]
    fn seq_first_fault_propagates() {
        assert_eq!(
            run(seq(var(1), int(2))),
            Err(Fault::UnboundVariable(Symbol(1)))
        );
    }

    #[test]
    fn if_untaken_branch_not_evaluated() {
        assert_eq!(
            run(if_(bool_v(true), int(1), var(99))),
            Ok(MValue::Integer(1))
        );
        assert_eq!(
            run(if_(bool_v(false), var(99), int(2))),
            Ok(MValue::Integer(2))
        );
    }

    #[test]
    fn let_value_evaluated_in_outer_env() {
        let mut st = EvalState::with_env(
            let_(1, var(1), var(1)),
            Environment::empty().extend(Symbol(1), MValue::Integer(7)),
        );
        assert_eq!(
            evaluate_state(&mut st, CEK_MAX_STEPS_DEFAULT),
            Ok(MValue::Integer(7))
        );
        assert_eq!(
            run(let_(1, var(1), int(1))),
            Err(Fault::UnboundVariable(Symbol(1)))
        );
    }

    #[test]
    fn let_shadow_does_not_leak_past_inner_body() {
        let e = let_(1, int(1), seq(let_(1, int(2), var(1)), var(1)));
        assert_eq!(run(e), Ok(MValue::Integer(1)));
    }

    #[test]
    fn env_extend_preserves_parent() {
        let parent = Environment::empty().extend(Symbol(1), MValue::Integer(1));
        let child = parent.extend(Symbol(2), MValue::Integer(2));
        assert_eq!(parent.lookup(Symbol(2)), None);
        assert_eq!(child.lookup(Symbol(2)), Some(&MValue::Integer(2)));
        assert_eq!(parent.lookup(Symbol(1)), Some(&MValue::Integer(1)));
    }

    // ----- M3 Lambda / Call --------------------------------------------------

    #[test]
    fn lambda_produces_function_and_halts() {
        // λ(). 1
        let e = lambda(&[], int(1));
        match run(e).unwrap() {
            MValue::Function(f) => {
                assert!(f.params.is_empty());
                assert_eq!(*f.body, int(1));
                assert!(f.env.is_empty());
            }
            other => panic!("expected Function, got {other:?}"),
        }
    }

    #[test]
    fn lambda_under_let_does_not_halt_early() {
        // let f = λ(x). x in f  → Function (value-return through Let)
        let e = let_(1, lambda(&[2], var(2)), var(1));
        assert!(matches!(run(e), Ok(MValue::Function(_))));
    }

    #[test]
    fn call_identity() {
        // (λ(x). x)(42)
        let e = call(lambda(&[1], var(1)), vec![int(42)]);
        assert_eq!(run(e), Ok(MValue::Integer(42)));
    }

    #[test]
    fn call_zero_args() {
        let e = call(lambda(&[], int(7)), vec![]);
        assert_eq!(run(e), Ok(MValue::Integer(7)));
    }

    #[test]
    fn call_two_args_ltr_binding() {
        // (λ(a,b). b)(1, 2) → 2
        let e = call(lambda(&[1, 2], var(2)), vec![int(1), int(2)]);
        assert_eq!(run(e), Ok(MValue::Integer(2)));
    }

    #[test]
    fn arity_too_few() {
        let e = call(lambda(&[1, 2], var(1)), vec![int(1)]);
        assert_eq!(
            run(e),
            Err(Fault::ArityMismatch {
                expected: 2,
                actual: 1
            })
        );
    }

    #[test]
    fn arity_too_many() {
        let e = call(lambda(&[1], var(1)), vec![int(1), int(2)]);
        assert_eq!(
            run(e),
            Err(Fault::ArityMismatch {
                expected: 1,
                actual: 2
            })
        );
    }

    #[test]
    fn arity_mismatch_before_arg_eval() {
        // (λ(x). x)(unbound) with wrong arity 0-params + 1 arg:
        // arity fails before evaluating unbound arg.
        let e = call(lambda(&[], int(1)), vec![var(99)]);
        assert_eq!(
            run(e),
            Err(Fault::ArityMismatch {
                expected: 0,
                actual: 1
            })
        );
    }

    #[test]
    fn arity_ok_then_arg_fault() {
        // correct arity; arg is unbound
        let e = call(lambda(&[1], var(1)), vec![var(99)]);
        assert_eq!(run(e), Err(Fault::UnboundVariable(Symbol(99))));
    }

    #[test]
    fn non_function_call() {
        let e = call(int(1), vec![int(2)]);
        assert_eq!(
            run(e),
            Err(Fault::TypeError {
                expected: "Function",
                actual: "Integer",
            })
        );
    }

    #[test]
    fn closure_captures_lexical_not_caller() {
        // let x = 1 in
        //   let f = λ(). x in
        //     let x = 2 in
        //       f()
        // → 1 (closure env), not 2 (caller)
        let e = let_(
            1,
            int(1),
            let_(
                2,
                lambda(&[], var(1)),
                let_(1, int(2), call(var(2), vec![])),
            ),
        );
        assert_eq!(run(e), Ok(MValue::Integer(1)));
    }

    #[test]
    fn param_shadows_captured_binding() {
        // let x = 1 in (λ(x). x)(9) → 9
        let e = let_(1, int(1), call(lambda(&[1], var(1)), vec![int(9)]));
        assert_eq!(run(e), Ok(MValue::Integer(9)));
    }

    #[test]
    fn nested_lambda_return_and_apply() {
        // (λ(x). λ(y). x)(3)(4) → 3
        let inner = lambda(&[2], var(1));
        let outer = lambda(&[1], inner);
        let e = call(call(outer, vec![int(3)]), vec![int(4)]);
        assert_eq!(run(e), Ok(MValue::Integer(3)));
    }

    #[test]
    fn call_args_evaluated_in_caller_env() {
        // let x = 5 in (λ(a). a)(x) → 5
        let e = let_(1, int(5), call(lambda(&[2], var(2)), vec![var(1)]));
        assert_eq!(run(e), Ok(MValue::Integer(5)));
    }

    #[test]
    fn call_order_func_before_args_via_state() {
        let mut st = EvalState::new(call(lambda(&[1], var(1)), vec![int(42)]));
        // enter Call → CallFunction frame, expr = lambda
        assert_eq!(step(&mut st), StepResult::Continue);
        assert!(matches!(st.expr, Expr::Lambda { .. }));
        assert_eq!(st.continuation.len(), 1);
        // lambda → Function value → resume CallFunction → arity OK → CallArgument
        assert_eq!(step(&mut st), StepResult::Continue);
        // now either applying 0-step into arg eval
        assert_eq!(st.continuation.len(), 1);
        assert!(matches!(
            st.continuation.frames.last(),
            Some(PureFrame::CallArgument { .. })
        ));
        assert_eq!(st.expr, int(42));
    }

    #[test]
    fn if_untaken_call_not_evaluated() {
        // if false then (unbound-call) else 1
        let bad = call(var(99), vec![]);
        assert_eq!(run(if_(bool_v(false), bad, int(1))), Ok(MValue::Integer(1)));
    }

    #[test]
    fn body_fault_propagates() {
        // (λ(). unbound)()
        let e = call(lambda(&[], var(99)), vec![]);
        assert_eq!(run(e), Err(Fault::UnboundVariable(Symbol(99))));
    }

    #[test]
    fn operator_fault_propagates() {
        // (unbound)(1)
        let e = call(var(99), vec![int(1)]);
        assert_eq!(run(e), Err(Fault::UnboundVariable(Symbol(99))));
    }

    #[test]
    fn closure_env_isolation() {
        // two closures capturing different x
        // let f = (let x = 1 in λ(). x) in
        // let g = (let x = 2 in λ(). x) in
        // seq(f(), g())
        let f = let_(1, int(1), lambda(&[], var(1)));
        let g = let_(1, int(2), lambda(&[], var(1)));
        let e = let_(
            10,
            f,
            let_(11, g, seq(call(var(10), vec![]), call(var(11), vec![]))),
        );
        assert_eq!(run(e), Ok(MValue::Integer(2)));
        // also f alone
        assert_eq!(
            run(let_(
                10,
                let_(1, int(1), lambda(&[], var(1))),
                call(var(10), vec![])
            )),
            Ok(MValue::Integer(1))
        );
    }

    #[test]
    fn deep_call_chain_stackless() {
        // Nested identity applications: (λ(x).x)(...(λ(x).x)(7)...)
        // Stresses Call frames without exponential closure-env growth from
        // chaining thunks that each capture prior bindings.
        const N: u32 = 64;
        let mut e = int(7);
        for _ in 0..N {
            e = call(lambda(&[1], var(1)), vec![e]);
        }
        assert_eq!(run(e), Ok(MValue::Integer(7)));
    }

    #[test]
    fn m3_determinism() {
        let e = let_(
            1,
            int(3),
            call(lambda(&[2], seq(var(2), var(1))), vec![int(9)]),
        );
        // body: seq(9, 3) → 3 (x captured)
        let a = run(e.clone());
        let b = run(e);
        assert_eq!(a, b);
        assert_eq!(a, Ok(MValue::Integer(3)));
    }

    #[test]
    fn later_forms_still_unsupported() {
        assert_eq!(
            run(Expr::Receive),
            Err(Fault::UnsupportedInM2 { form: "Receive" })
        );
    }

    fn evaluate_state(state: &mut EvalState, max_steps: u64) -> Result<MValue, Fault> {
        for _ in 0..max_steps {
            match step(state) {
                StepResult::Continue => continue,
                StepResult::Halted(v) => return Ok(v),
                StepResult::Fault(f) => return Err(f),
            }
        }
        Err(Fault::UnsupportedInM2 { form: "step_limit" })
    }
}
