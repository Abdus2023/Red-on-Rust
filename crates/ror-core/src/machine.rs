//! Machine-domain types for the CEK evaluator (R-CALC-01/02/03, R-CEK-*).
//!
//! **U-09 boundary.** These types are *not* the Phase-15A data-domain
//! [`crate::types::Value`]. The public name collision is intentional and
//! provisional: machine values live under [`crate::machine`]; data-domain
//! values remain under [`crate::types`] / the crate root re-export.
//! There is **no** `From`/`Into` bridge that collapses the two domains.
//!
//! **U-02 boundary.** No byte codecs, wire tags, or snapshot encodings are
//! defined here for frames, environments, or machine values.
//!
//! **M2 vs M3.** [`Expr`] declares the full frozen surface (R-CALC-02). M2
//! evaluation implements only `Value` / `Var` / `Let` / `Seq` / `If`.
//! `Lambda` / `Call` and later constructors are present as AST nodes so the
//! type matches the frozen surface; their CEK transitions are **M3+** and
//! must fault as unsupported in pure M2 evaluators.

use crate::types::{CapRef, Symbol};

/// Opaque delegated-capability handle (R-CALC-01).
///
/// Construction authority is the marshaller; M2 pure CEK never constructs it.
/// Representation is an implementation choice (U-09/U-30 open) — not a wire ABI.
#[derive(Clone, Debug, PartialEq, Eq, Hash)]
pub struct DelegatedCapability {
    pub(crate) index: u32,
    pub(crate) generation: u32,
}

impl DelegatedCapability {
    /// Test/kernel-adjacent constructor. Not a public authority mint.
    #[doc(hidden)]
    pub fn provisional(index: u32, generation: u32) -> Self {
        Self { index, generation }
    }
}

/// Closure value shape (R-CEK-04). Present for the R-CALC-01 domain; **M3**
/// creates these via `Lambda`. M2 does not evaluate `Lambda`/`Call`.
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct FunctionValue {
    pub params: Vec<Symbol>,
    pub body: Box<Expr>,
    /// Lexical environment captured at lambda creation (R-CEK-04).
    pub env: Environment,
}

/// Machine value domain (R-CALC-01).
///
/// Distinct from [`crate::types::Value`] (15A data domain, U-09 OPEN).
#[derive(Clone, Debug, PartialEq, Eq)]
pub enum Value {
    Unit,
    Bool(bool),
    Integer(i64),
    Bytes(Vec<u8>),
    Symbol(Symbol),
    String(String),
    List(Vec<Value>),
    Tuple(Vec<Value>),
    Function(FunctionValue),
    /// Opaque capability reference. Evaluator must not inspect authority.
    Capability(CapRef),
    DelegatedCapability(DelegatedCapability),
}

/// Frozen expression AST (R-CALC-02).
///
/// M2 pure-subset evaluators implement: `Value`, `Var`, `Let`, `Seq`, `If`.
/// Remaining constructors are declared for surface completeness and must not
/// receive production CEK semantics under an M2 label.
#[derive(Clone, Debug, PartialEq, Eq)]
pub enum Expr {
    Value(Value),
    Var(Symbol),
    Let {
        name: Symbol,
        value: Box<Expr>,
        body: Box<Expr>,
    },
    Seq {
        first: Box<Expr>,
        second: Box<Expr>,
    },
    If {
        condition: Box<Expr>,
        then_branch: Box<Expr>,
        else_branch: Box<Expr>,
    },
    /// M3 — not evaluated in M2.
    Lambda {
        params: Vec<Symbol>,
        body: Box<Expr>,
    },
    /// M3 — not evaluated in M2.
    Call {
        func: Box<Expr>,
        args: Vec<Expr>,
    },
    /// M4+ — not evaluated in M2.
    Attenuate {
        cap: Box<Expr>,
        constraint: Box<Expr>,
    },
    /// M4+ — not evaluated in M2.
    Request {
        capability: Box<Expr>,
        operation: Box<Expr>,
        target: Box<Expr>,
        params: Vec<Expr>,
    },
    /// Later milestone — not evaluated in M2.
    Spawn {
        expr: Box<Expr>,
        initial_budget: Box<Expr>,
        capabilities: Vec<Expr>,
    },
    /// Later milestone — not evaluated in M2.
    Send {
        target: Box<Expr>,
        message: Box<Expr>,
    },
    /// Later milestone — not evaluated in M2.
    Receive,
    /// Later milestone — not evaluated in M2.
    Yield,
    /// Later milestone — not evaluated in M2.
    Halt,
}

impl Expr {
    /// True when the expression is in the M2 pure differential surface
    /// (constructors only; does not walk nested out-of-subset forms).
    pub fn is_m2_constructor(&self) -> bool {
        matches!(
            self,
            Expr::Value(_) | Expr::Var(_) | Expr::Let { .. } | Expr::Seq { .. } | Expr::If { .. }
        )
    }
}

/// Lexical environment (R-CALC-03 / CEK env).
///
/// Implementation choice: ordered association list; lookup scans from the
/// newest binding (innermost shadows outer). Deterministic; no hashing.
#[derive(Clone, Debug, PartialEq, Eq, Default)]
pub struct Environment {
    bindings: Vec<(Symbol, Value)>,
}

impl Environment {
    pub fn empty() -> Self {
        Self {
            bindings: Vec::new(),
        }
    }

    /// Extend with a binding. Does not mutate `self`.
    pub fn extend(&self, name: Symbol, value: Value) -> Self {
        let mut bindings = self.bindings.clone();
        bindings.push((name, value));
        Self { bindings }
    }

    /// Lexical lookup: innermost binding wins.
    pub fn lookup(&self, name: Symbol) -> Option<&Value> {
        self.bindings
            .iter()
            .rev()
            .find(|(symbol, _)| *symbol == name)
            .map(|(_, value)| value)
    }

    pub fn len(&self) -> usize {
        self.bindings.len()
    }

    pub fn is_empty(&self) -> bool {
        self.bindings.is_empty()
    }
}

/// Machine-local fault identity for pure CEK (M2 subset).
///
/// Full trust-boundary fault taxonomy (R-CORE-13) is broader; this enum is the
/// **evaluator-local** surface needed by pure transitions. Provisional under
/// open fault OADs — not a claim that U-08 is closed.
#[derive(Clone, Debug, PartialEq, Eq)]
pub enum Fault {
    UnboundVariable(Symbol),
    TypeError {
        expected: &'static str,
        actual: &'static str,
    },
    /// Expression or frame outside the M2 pure-subset evaluator.
    UnsupportedInM2 {
        form: &'static str,
    },
}

/// Helpers for building pure-subset expressions in tests and fixtures.
pub mod sugar {
    use super::{Expr, Symbol, Value};

    pub fn unit() -> Expr {
        Expr::Value(Value::Unit)
    }

    pub fn bool_v(b: bool) -> Expr {
        Expr::Value(Value::Bool(b))
    }

    pub fn int(n: i64) -> Expr {
        Expr::Value(Value::Integer(n))
    }

    pub fn var(id: u32) -> Expr {
        Expr::Var(Symbol(id))
    }

    pub fn let_(name: u32, value: Expr, body: Expr) -> Expr {
        Expr::Let {
            name: Symbol(name),
            value: Box::new(value),
            body: Box::new(body),
        }
    }

    pub fn seq(first: Expr, second: Expr) -> Expr {
        Expr::Seq {
            first: Box::new(first),
            second: Box::new(second),
        }
    }

    pub fn if_(condition: Expr, then_branch: Expr, else_branch: Expr) -> Expr {
        Expr::If {
            condition: Box::new(condition),
            then_branch: Box::new(then_branch),
            else_branch: Box::new(else_branch),
        }
    }
}

/// Marker: machine Value is not data-domain Value (compile-time documentation).
#[cfg(test)]
mod u09_isolation_tests {
    use super::*;
    use crate::types;

    #[test]
    fn machine_and_data_value_are_distinct_types() {
        let m = Value::Integer(1);
        let d = types::Value::Integer(1);
        // Distinct types: no equality, no silent coerce.
        assert_eq!(m, Value::Integer(1));
        assert_eq!(d, types::Value::Integer(1));
        let _ = (m, d);
    }

    #[test]
    fn env_shadowing_is_lexical_innermost() {
        let e = Environment::empty()
            .extend(Symbol(1), Value::Integer(10))
            .extend(Symbol(1), Value::Integer(20));
        assert_eq!(e.lookup(Symbol(1)), Some(&Value::Integer(20)));
    }

    #[test]
    fn env_lookup_miss_is_none() {
        assert!(Environment::empty().lookup(Symbol(0)).is_none());
    }
}
