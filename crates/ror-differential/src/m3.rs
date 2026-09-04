//! M3 differential observations: Lambda / Call (R-CEK-04/05).
//!
//! Reuses terminal observation normalization from [`crate::m2`].

#[cfg(test)]
mod tests {
    use crate::m2::{compare_m2, observe_production, observe_reference, Observation};
    use ror_core::machine::sugar::{bool_v, call, if_, int, lambda, let_, seq, var};
    use ror_core::machine::{Expr, Fault, Value};

    fn assert_agree(expr: Expr) {
        compare_m2(expr).expect("M3 production/reference divergence");
    }

    #[test]
    fn simple_lambda_halts_as_function() {
        let e = lambda(&[1], var(1));
        let p = observe_production(e.clone());
        let r = observe_reference(e);
        assert_eq!(p, r);
        assert!(matches!(p, Observation::Halted(Value::Function(_))));
    }

    #[test]
    fn simple_call_identity() {
        assert_agree(call(lambda(&[1], var(1)), vec![int(42)]));
    }

    #[test]
    fn zero_arg_call() {
        assert_agree(call(lambda(&[], int(7)), vec![]));
    }

    #[test]
    fn multi_arg_binding() {
        assert_agree(call(lambda(&[1, 2], var(1)), vec![int(10), int(20)]));
        assert_agree(call(lambda(&[1, 2], var(2)), vec![int(10), int(20)]));
    }

    #[test]
    fn closure_capture_not_caller() {
        let e = let_(
            1,
            int(1),
            let_(
                2,
                lambda(&[], var(1)),
                let_(1, int(2), call(var(2), vec![])),
            ),
        );
        assert_agree(e);
        assert_eq!(
            observe_production(let_(
                1,
                int(1),
                let_(
                    2,
                    lambda(&[], var(1)),
                    let_(1, int(2), call(var(2), vec![])),
                ),
            )),
            Observation::Halted(Value::Integer(1))
        );
    }

    #[test]
    fn closure_shadowing_param() {
        assert_agree(let_(1, int(1), call(lambda(&[1], var(1)), vec![int(9)])));
    }

    #[test]
    fn nested_closure_return() {
        let e = call(
            call(lambda(&[1], lambda(&[2], var(1))), vec![int(3)]),
            vec![int(4)],
        );
        assert_agree(e);
    }

    #[test]
    fn arity_too_few() {
        assert_agree(call(lambda(&[1, 2], var(1)), vec![int(1)]));
        assert_eq!(
            observe_production(call(lambda(&[1, 2], var(1)), vec![int(1)])),
            Observation::Fault(Fault::ArityMismatch {
                expected: 2,
                actual: 1
            })
        );
    }

    #[test]
    fn arity_too_many() {
        assert_agree(call(lambda(&[1], var(1)), vec![int(1), int(2)]));
    }

    #[test]
    fn arity_before_arg_eval() {
        let e = call(lambda(&[], int(1)), vec![var(99)]);
        assert_agree(e.clone());
        assert_eq!(
            observe_production(e),
            Observation::Fault(Fault::ArityMismatch {
                expected: 0,
                actual: 1
            })
        );
    }

    #[test]
    fn non_callable() {
        assert_agree(call(int(1), vec![int(2)]));
        assert_eq!(
            observe_production(call(int(1), vec![])),
            Observation::Fault(Fault::TypeError {
                expected: "Function",
                actual: "Integer",
            })
        );
    }

    #[test]
    fn argument_fault() {
        assert_agree(call(lambda(&[1], var(1)), vec![var(99)]));
    }

    #[test]
    fn body_fault() {
        assert_agree(call(lambda(&[], var(99)), vec![]));
    }

    #[test]
    fn operator_fault() {
        assert_agree(call(var(99), vec![int(1)]));
    }

    #[test]
    fn nested_calls() {
        let e = call(
            lambda(&[10], call(var(10), vec![int(1)])),
            vec![lambda(&[1], var(1))],
        );
        assert_agree(e);
    }

    #[test]
    fn args_in_caller_env() {
        assert_agree(let_(1, int(5), call(lambda(&[2], var(2)), vec![var(1)])));
    }

    #[test]
    fn if_untaken_call() {
        assert_agree(if_(bool_v(false), call(var(99), vec![]), int(1)));
    }

    #[test]
    fn lambda_under_let_and_seq() {
        assert_agree(let_(
            1,
            lambda(&[2], var(2)),
            seq(int(0), call(var(1), vec![int(8)])),
        ));
    }

    #[test]
    fn two_closures_isolated() {
        let f = let_(1, int(1), lambda(&[], var(1)));
        let g = let_(1, int(2), lambda(&[], var(1)));
        assert_agree(let_(
            10,
            f,
            let_(11, g, seq(call(var(10), vec![]), call(var(11), vec![]))),
        ));
    }

    #[test]
    fn m3_determinism() {
        let e = call(lambda(&[1], let_(2, var(1), var(2))), vec![int(4)]);
        let a = observe_production(e.clone());
        let b = observe_production(e.clone());
        let c = observe_reference(e);
        assert_eq!(a, b);
        assert_eq!(a, c);
        assert_eq!(a, Observation::Halted(Value::Integer(4)));
    }

    #[test]
    fn ltr_multi_arg_with_lets() {
        let e = call(
            lambda(&[1, 2], seq(var(1), var(2))),
            vec![let_(9, int(1), var(9)), let_(9, int(2), var(9))],
        );
        assert_agree(e);
    }
}
