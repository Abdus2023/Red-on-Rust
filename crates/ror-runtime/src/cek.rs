//! Explicit Control–Environment–Continuation machine (R-CEK-01).
//!
//! Pure M2 subset only. No recursive evaluator calls for nesting depth
//! (R-CEK-02 / REQ-CEK-002): nesting lives in [`Continuation`].

use ror_core::machine::{Environment, Expr, Fault, Value};
use ror_core::Symbol;

/// Default fuel for [`evaluate`] when the caller does not supply a bound.
/// Prevents runaway loops in tests; not a semantic budget (MOD-04 deferred).
pub const CEK_MAX_STEPS_DEFAULT: u64 = 1_000_000;

/// Pure-subset continuation frames implemented in M2 (R-CEK-03 subset).
///
/// Full frozen set also includes Call*/Attenuate/Request* (M3+). Those are
/// not constructed by this evaluator.
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
}

/// Frame type alias — M2 only pushes [`PureFrame`] variants.
///
/// Not a wire type (U-02 OPEN). `pub(crate)`-stable for the runtime crate;
/// external consumers should treat layout as provisional.
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

/// Local CEK control state (R-CEK-01): `EvalState { expr, env, continuation }`.
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

/// Provisional step outcome (U-26 OPEN — local name, not frozen ABI).
#[derive(Clone, Debug, PartialEq, Eq)]
pub enum StepResult {
    /// Machine needs another step (non-terminal transition completed).
    Continue,
    /// Terminal value with empty continuation (R-CEK-02).
    Halted(Value),
    /// Semantic fault.
    Fault(Fault),
}

/// One pure CEK transition. Stack depth is O(1) in program nesting.
///
/// Pure transitions change continuation length by exactly +1 (entry) or −1
/// (resume) when they push/pop (R-CEK-06). Terminal Halt does not pop.
///
/// Takes ownership of the current expression via `mem::replace` so deep ASTs
/// are not recursively cloned on every step (stackless driver discipline).
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
        Expr::Lambda { .. } => StepResult::Fault(Fault::UnsupportedInM2 { form: "Lambda" }),
        Expr::Call { .. } => StepResult::Fault(Fault::UnsupportedInM2 { form: "Call" }),
        Expr::Attenuate { .. } => StepResult::Fault(Fault::UnsupportedInM2 { form: "Attenuate" }),
        Expr::Request { .. } => StepResult::Fault(Fault::UnsupportedInM2 { form: "Request" }),
        Expr::Spawn { .. } => StepResult::Fault(Fault::UnsupportedInM2 { form: "Spawn" }),
        Expr::Send { .. } => StepResult::Fault(Fault::UnsupportedInM2 { form: "Send" }),
        Expr::Receive => StepResult::Fault(Fault::UnsupportedInM2 { form: "Receive" }),
        Expr::Yield => StepResult::Fault(Fault::UnsupportedInM2 { form: "Yield" }),
        Expr::Halt => StepResult::Fault(Fault::UnsupportedInM2 { form: "Halt" }),
    }
}

/// Drive the machine to a terminal Halt or Fault.
///
/// Returns `Fault(UnsupportedInM2 { form: "step_limit" })` if `max_steps` is
/// exhausted — an implementation safety bound, not a semantic budget debit.
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

/// R-CEK-02 value-return: sole path that pops a frame or halts.
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
    }
}

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
            let actual = value_kind(&other);
            return StepResult::Fault(Fault::TypeError {
                expected: "Bool",
                actual,
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
    use ror_core::machine::sugar::{bool_v, if_, int, let_, seq, unit, var};
    use ror_core::machine::Value as MValue;

    fn run(expr: Expr) -> Result<MValue, Fault> {
        evaluate(expr, CEK_MAX_STEPS_DEFAULT)
    }

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
        // let x = 1 in x
        let e = let_(1, int(1), var(1));
        assert_eq!(run(e), Ok(MValue::Integer(1)));
    }

    #[test]
    fn let_shadowing() {
        // let x = 1 in let x = 2 in x  → 2
        let e = let_(1, int(1), let_(1, int(2), var(1)));
        assert_eq!(run(e), Ok(MValue::Integer(2)));
    }

    #[test]
    fn seq_evaluates_first_then_second() {
        // Seq discards first value, returns second.
        let e = seq(int(1), int(2));
        assert_eq!(run(e), Ok(MValue::Integer(2)));
    }

    #[test]
    fn seq_order_observable_via_state() {
        let mut st = EvalState::new(seq(int(1), int(2)));
        // enter Seq → push frame, expr = first
        assert_eq!(step(&mut st), StepResult::Continue);
        assert_eq!(st.expr, int(1));
        assert_eq!(st.continuation.len(), 1);
        // Value 1 → resume Seq → expr = second
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
        // let x = true in if x then 10 else 20
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
        step(&mut st); // enter let
        let before = st.continuation.len();
        assert_eq!(step(&mut st), StepResult::Continue); // value → resume let
        assert_eq!(st.continuation.len(), before - 1);
    }

    #[test]
    fn value_with_nonempty_k_does_not_halt() {
        // Manually: Value under a Seq frame must resume, not halt.
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
    fn lambda_and_call_unsupported_in_m2() {
        let lam = Expr::Lambda {
            params: vec![Symbol(0)],
            body: Box::new(var(0)),
        };
        assert_eq!(run(lam), Err(Fault::UnsupportedInM2 { form: "Lambda" }));
        let call = Expr::Call {
            func: Box::new(int(1)),
            args: vec![],
        };
        assert_eq!(run(call), Err(Fault::UnsupportedInM2 { form: "Call" }));
    }

    #[test]
    fn deep_let_nest_is_stackless() {
        // Nested lets stress continuation depth. Depth is capped so recursive
        // `Drop` of the residual AST (host limitation on nested `Box`) does not
        // abort the process; the evaluator itself never recurses on nesting.
        const N: u32 = 512;
        let mut e = var(N);
        for i in (1..=N).rev() {
            e = let_(i, int(i as i64), e);
        }
        // let 1 = 1 in let 2 = 2 in ... let N = N in var(N) → N
        assert_eq!(run(e), Ok(MValue::Integer(N as i64)));
    }

    #[test]
    fn wide_seq_chain_is_stackless() {
        // Many sequential frames via nested Seq — continuation grows then shrinks.
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

    /// Untaken `If` branch must not be evaluated (canonical branch selection).
    #[test]
    fn if_untaken_branch_not_evaluated() {
        // if true then 1 else <unbound>  → 1 (else never stepped)
        assert_eq!(
            run(if_(bool_v(true), int(1), var(99))),
            Ok(MValue::Integer(1))
        );
        // if false then <unbound> else 2 → 2
        assert_eq!(
            run(if_(bool_v(false), var(99), int(2))),
            Ok(MValue::Integer(2))
        );
    }

    /// Let value is evaluated under the *outer* environment (before binding).
    #[test]
    fn let_value_evaluated_in_outer_env() {
        // outer x=7; let x = x in x  → value-expr sees outer 7, body sees 7
        let mut st = EvalState::with_env(
            let_(1, var(1), var(1)),
            Environment::empty().extend(Symbol(1), MValue::Integer(7)),
        );
        assert_eq!(
            evaluate_state(&mut st, CEK_MAX_STEPS_DEFAULT),
            Ok(MValue::Integer(7))
        );

        // no outer x: let x = x in 1 → unbound while evaluating value
        assert_eq!(
            run(let_(1, var(1), int(1))),
            Err(Fault::UnboundVariable(Symbol(1)))
        );
    }

    /// Shadowing restores outer binding for expressions after the inner let completes
    /// only via Seq/continuation structure (body of outer sees outer after inner finishes
    /// is N/A for single-result Let). Check: outer body after nested let uses outer.
    /// `let x=1 in seq(let x=2 in x, x)` → second x is outer 1.
    #[test]
    fn let_shadow_does_not_leak_past_inner_body() {
        let e = let_(1, int(1), seq(let_(1, int(2), var(1)), var(1)));
        assert_eq!(run(e), Ok(MValue::Integer(1)));
    }

    /// Environment::extend does not mutate the parent (lexical isolation).
    #[test]
    fn env_extend_preserves_parent() {
        let parent = Environment::empty().extend(Symbol(1), MValue::Integer(1));
        let child = parent.extend(Symbol(2), MValue::Integer(2));
        assert_eq!(parent.lookup(Symbol(2)), None);
        assert_eq!(child.lookup(Symbol(2)), Some(&MValue::Integer(2)));
        assert_eq!(parent.lookup(Symbol(1)), Some(&MValue::Integer(1)));
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
