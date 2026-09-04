#![forbid(unsafe_code)]

//! Production runtime — M2 pure CEK evaluator (MOD-05).
//!
//! Implements the authorized M2 surface: `Value` / `Var` / `Let` / `Seq` / `If`
//! with an explicit stackless CEK machine (R-CEK-01…03, R-CEK-06 pure subset).
//!
//! **Out of scope (M3+):** `Lambda` / `Call` (R-CEK-04/05), effects, actors,
//! host, persistence, capability authorization.
//!
//! **U-02:** frames are in-memory only — no canonical byte encoding.
//! **U-09:** uses [`ror_core::machine::Value`], never data-domain `ror_core::Value`.
//! **U-26:** [`StepResult`] is a provisional local outcome type, not a frozen ABI.
//!
//! Kernel and persistence remain workspace dependencies for later milestones;
//! pure M2 evaluation paths do not call them.

pub mod cek;

pub use cek::{
    evaluate, step, Continuation, EvalState, Frame, PureFrame, StepResult, CEK_MAX_STEPS_DEFAULT,
};
