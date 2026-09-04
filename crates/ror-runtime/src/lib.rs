#![forbid(unsafe_code)]

//! Production runtime — pure CEK evaluator (MOD-05).
//!
//! - **M2:** `Value` / `Var` / `Let` / `Seq` / `If`
//! - **M3:** `Lambda` / `Call` (R-CEK-04/05)
//!
//! **Out of scope (M4+):** effects, actors, host, persistence, capability authorize.
//!
//! **U-02:** frames are in-memory only — no canonical byte encoding.
//! **U-09:** uses [`ror_core::machine::Value`], never data-domain `ror_core::Value`.
//! **U-26:** [`StepResult`] is provisional.
//!
//! Kernel and persistence remain workspace dependencies for later milestones;
//! pure evaluation paths do not call them.

pub mod cek;

pub use cek::{
    evaluate, step, Continuation, EvalState, Frame, PureFrame, StepResult, CEK_MAX_STEPS_DEFAULT,
};
