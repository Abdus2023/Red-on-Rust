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
//! **M2 vs M3.** [`Expr`] declares the full frozen surface (R-CALC-02).
//! M2 evaluation: `Value` / `Var` / `Let` / `Seq` / `If`.
//! M3 evaluation adds: `Lambda` / `Call` (R-CEK-04/05).
//! Later constructors remain AST-only until later milestones.

use crate::capability::Constraint;
use crate::types::{CapRef, Symbol};

/// Opaque delegated-capability handle (R-CALC-01 / R-MARSHAL-05).
///
/// Construction authority is the marshaller / kernel-adjacent runtime path;
/// pure CEK never constructs it. Representation is an implementation choice
/// (U-09/U-30 open) — not a wire ABI.
///
/// Carries the derived child CapRef bits and the intended recipient ActorId.
/// Ordinary Send rejects this via marshal; only the dedicated delegation
/// admission path may register it into a recipient context.
#[derive(Clone, Debug, PartialEq, Eq, Hash)]
pub struct DelegatedCapability {
    pub(crate) index: u32,
    pub(crate) generation: u32,
    /// Intended recipient (data ActorId). Revalidated at receive.
    pub(crate) target_actor: u64,
}

impl DelegatedCapability {
    /// Test/kernel-adjacent constructor. Not a public authority mint.
    #[doc(hidden)]
    pub fn provisional(index: u32, generation: u32) -> Self {
        Self {
            index,
            generation,
            target_actor: 0,
        }
    }

    /// Kernel-constructed envelope from a derived child CapRef (R-MARSHAL-05).
    pub fn from_derived(child: CapRef, target_actor: u64) -> Self {
        Self {
            index: child.index(),
            generation: child.generation(),
            target_actor,
        }
    }

    pub fn child_cap(&self) -> CapRef {
        CapRef::from_kernel_parts(self.index, self.generation)
    }

    pub fn target_actor(&self) -> u64 {
        self.target_actor
    }

    pub fn index(&self) -> u32 {
        self.index
    }

    pub fn generation(&self) -> u32 {
        self.generation
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
    /// Constraint value for `Expr::Attenuate { constraint: Box<Expr> }` (R-CALC-02).
    /// Not an authority; narrowing request only (R-CAP-04). M4 surface.
    Constraint(Constraint),
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
    /// M6 — spawn child actor (R-ACTOR-05/09).
    Spawn {
        expr: Box<Expr>,
        initial_budget: Box<Expr>,
        capabilities: Vec<Expr>,
    },
    /// M6 — async send (R-ACTOR-06).
    Send {
        target: Box<Expr>,
        message: Box<Expr>,
    },
    /// M6 — blocking receive (R-ACTOR-06).
    Receive,
    /// M6 — explicit capability delegation (R-MARSHAL-05 addendum; L-M6-DELEG-AST).
    ///
    /// Evaluates by `kernel.derive` and yields a kernel-constructed
    /// [`DelegatedCapability`] envelope — never a plain `Value::Capability`
    /// transferable by ordinary Send.
    Delegate {
        capability: Box<Expr>,
        constraint: Box<Expr>,
        /// Target actor identity (data id; not authority).
        target: Box<Expr>,
    },
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

/// Machine-local fault identity for pure CEK (M2/M3/M4 subset).
///
/// Full trust-boundary fault taxonomy (R-CORE-13) is broader; this enum is the
/// **evaluator-local** surface needed by pure transitions. Provisional under
/// open fault OADs — **U-08 remains OPEN**. Not a claim that R-CALC-06 is closed.
///
/// `ArityMismatch` realises R-CEK-05 / REQ-CEK-014 `fault(F_arity)`.
/// `CapabilityRevoked` / `InvalidConstraint` are M4 provisional labels
/// (REQ-CAP-023 / R-CAP-10 name tension with AMB-08).
#[derive(Clone, Debug, PartialEq, Eq)]
pub enum Fault {
    UnboundVariable(Symbol),
    TypeError {
        expected: &'static str,
        actual: &'static str,
    },
    /// Call arity mismatch (R-CEK-05 / REQ-CEK-014). Raised **before** any
    /// argument evaluation.
    ArityMismatch {
        expected: usize,
        actual: usize,
    },
    /// E-AttenuateDenied when ¬Valid (REQ-CAP-023). Provisional label; U-08 OPEN.
    CapabilityRevoked,
    /// Inadmissible constraint (R-CAP-10). Provisional label; U-08 OPEN.
    InvalidConstraint,
    /// Authorization failed (R-CAP-06 / gate 6). Provisional; U-08 OPEN.
    Unauthorized,
    /// Budget gate failed (R-BUDGET-08 shape). Provisional; U-08 OPEN.
    BudgetExhausted,
    /// Deadline gate failed. Provisional; U-08 OPEN.
    DeadlineExceeded,
    /// Host policy denied (R-HOST-01). Provisional; U-08 OPEN.
    HostPolicyDenied,
    /// Persistence append/sync failure (R-DUR-07). Provisional; U-08 OPEN.
    PersistenceError,
    /// Receipt causal mismatch (R-EFFECT-06). Provisional; U-08 OPEN.
    ReplayCorruption,
    /// Receipt payload admission failed (R-EFFECT-08). Provisional; U-08 OPEN.
    InvalidReceipt,
    /// Host execution failed (mapped code). Provisional; U-08 OPEN.
    HostFault {
        code: u32,
    },
    /// Effect canonicalization / domain error. Provisional; U-08 OPEN.
    EffectError {
        reason: &'static str,
    },
    /// Ordinary marshal rejected capability-bearing payload (R-MARSHAL-01). U-08 OPEN.
    MarshalCapabilityRejected,
    /// Mailbox capacity admission failed (R-ACTOR-10). Sender pays. U-08 OPEN.
    ReservedCapacityExceeded,
    /// Send target is not a live actor. Provisional; U-08 / L-M6-TERM.
    ActorNotFound,
    /// Expression outside the current evaluator surface (M7+ forms, fuel).
    /// Name retained from M2; does not mean M3–M6 forms are unsupported.
    UnsupportedInM2 {
        form: &'static str,
    },
}

/// Helpers for building pure-subset expressions in tests and fixtures.
pub mod sugar {
    use super::{Expr, Symbol, Value};
    use crate::types::CapRef;

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

    pub fn lambda(params: &[u32], body: Expr) -> Expr {
        Expr::Lambda {
            params: params.iter().copied().map(Symbol).collect(),
            body: Box::new(body),
        }
    }

    pub fn call(func: Expr, args: Vec<Expr>) -> Expr {
        Expr::Call {
            func: Box::new(func),
            args,
        }
    }

    /// `Expr::Attenuate { cap, constraint }` (R-CALC-02). No body/name fields.
    pub fn attenuate(cap: Expr, constraint: Expr) -> Expr {
        Expr::Attenuate {
            cap: Box::new(cap),
            constraint: Box::new(constraint),
        }
    }

    pub fn constraint_v(c: super::Constraint) -> Expr {
        Expr::Value(Value::Constraint(c))
    }

    pub fn capability_v(cap: CapRef) -> Expr {
        Expr::Value(Value::Capability(cap))
    }

    pub fn request(capability: Expr, operation: Expr, target: Expr, params: Vec<Expr>) -> Expr {
        Expr::Request {
            capability: Box::new(capability),
            operation: Box::new(operation),
            target: Box::new(target),
            params,
        }
    }

    pub fn spawn(expr: Expr, initial_budget: Expr, capabilities: Vec<Expr>) -> Expr {
        Expr::Spawn {
            expr: Box::new(expr),
            initial_budget: Box::new(initial_budget),
            capabilities,
        }
    }

    pub fn send(target: Expr, message: Expr) -> Expr {
        Expr::Send {
            target: Box::new(target),
            message: Box::new(message),
        }
    }

    pub fn receive() -> Expr {
        Expr::Receive
    }

    pub fn actor_id_v(id: u64) -> Expr {
        Expr::Value(Value::Integer(id as i64))
    }

    pub fn delegate(capability: Expr, constraint: Expr, target: Expr) -> Expr {
        Expr::Delegate {
            capability: Box::new(capability),
            constraint: Box::new(constraint),
            target: Box::new(target),
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
