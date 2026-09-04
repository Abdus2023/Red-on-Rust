//! M2 pure-subset differential observations (Value/Var/Let/Seq/If).
//!
//! M3 cases live in [`crate::m3`].

use ror_core::machine::{Expr, Fault, Value};
use ror_reference::{evaluate as ref_eval, REF_MAX_STEPS_DEFAULT};
use ror_runtime::{evaluate as prod_eval, CEK_MAX_STEPS_DEFAULT};

pub const M2_DIFF_MAX_STEPS: u64 = CEK_MAX_STEPS_DEFAULT;

/// Normalized terminal observation for differential comparison.
#[derive(Clone, Debug, PartialEq, Eq)]
pub enum Observation {
    Halted(Value),
    Fault(Fault),
}

pub fn observe_production(expr: Expr) -> Observation {
    match prod_eval(expr, CEK_MAX_STEPS_DEFAULT) {
        Ok(v) => Observation::Halted(v),
        Err(f) => Observation::Fault(f),
    }
}

pub fn observe_reference(expr: Expr) -> Observation {
    match ref_eval(expr, REF_MAX_STEPS_DEFAULT) {
        Ok(v) => Observation::Halted(v),
        Err(f) => Observation::Fault(f),
    }
}

/// Compare production vs reference. `Ok(())` on agreement; `Err` carries both sides.
pub fn compare_m2(expr: Expr) -> Result<(), (Observation, Observation)> {
    let p = observe_production(expr.clone());
    let r = observe_reference(expr);
    if p == r {
        Ok(())
    } else {
        Err((p, r))
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use ror_core::machine::sugar::{bool_v, if_, int, let_, seq, unit, var};

    fn assert_agree(expr: Expr) {
        compare_m2(expr).expect("production/reference divergence");
    }

    #[test]
    fn terminals() {
        assert_agree(unit());
        assert_agree(int(0));
        assert_agree(bool_v(true));
        assert_agree(Expr::Value(Value::String("hi".into())));
    }

    #[test]
    fn var_and_unbound() {
        assert_agree(let_(1, int(3), var(1)));
        assert_agree(var(42));
    }

    #[test]
    fn nested_let_shadowing() {
        assert_agree(let_(1, int(1), let_(1, int(2), var(1))));
        assert_agree(let_(1, int(1), let_(2, var(1), var(2))));
    }

    #[test]
    fn seq_family() {
        assert_agree(seq(int(1), int(2)));
        assert_agree(seq(seq(int(1), int(2)), int(3)));
        assert_agree(seq(let_(1, int(9), var(1)), int(0)));
    }

    #[test]
    fn if_family() {
        assert_agree(if_(bool_v(true), int(1), int(0)));
        assert_agree(if_(bool_v(false), int(1), int(0)));
        assert_agree(if_(int(1), int(2), int(3)));
    }

    #[test]
    fn combinations() {
        assert_agree(let_(
            1,
            bool_v(true),
            if_(var(1), seq(int(1), int(10)), int(20)),
        ));
        assert_agree(let_(
            1,
            int(5),
            let_(2, if_(bool_v(true), var(1), int(0)), seq(var(2), var(1))),
        ));
    }

    #[test]
    fn determinism_of_observations() {
        let e = let_(1, int(2), if_(bool_v(true), var(1), int(0)));
        let a = observe_production(e.clone());
        let b = observe_production(e.clone());
        let c = observe_reference(e);
        assert_eq!(a, b);
        assert_eq!(a, c);
    }

    #[test]
    fn if_untaken_branch_not_evaluated() {
        assert_agree(if_(bool_v(true), int(1), var(99)));
        assert_agree(if_(bool_v(false), var(99), int(2)));
    }

    #[test]
    fn let_value_in_outer_env_and_shadow_restore() {
        assert_agree(let_(1, var(1), int(1)));
        assert_agree(let_(1, int(1), seq(let_(1, int(2), var(1)), var(1))));
    }

    #[test]
    fn harness_calls_distinct_evaluators() {
        let e = int(123);
        let p = observe_production(e.clone());
        let r = observe_reference(e);
        assert_eq!(p, Observation::Halted(Value::Integer(123)));
        assert_eq!(r, Observation::Halted(Value::Integer(123)));
        assert_eq!(p, r);
    }
}
