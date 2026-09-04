#![forbid(unsafe_code)]

//! Production runtime — pure CEK evaluator (MOD-05).
//!
//! - **M2:** `Value` / `Var` / `Let` / `Seq` / `If`
//! - **M3:** `Lambda` / `Call` (R-CEK-04/05)
//! - **M4:** `Attenuate` via `ror-kernel` derive (R-CAP-*, REQ-CAP-022/023)
//!
//! **Out of scope (M5+):** Request/effects, actors, host, persistence.
//!
//! **U-02:** frames are in-memory only — no canonical byte encoding.
//! **U-09:** uses [`ror_core::machine::Value`], never data-domain `ror_core::Value`.
//! **U-26:** [`StepResult`] is provisional.

pub mod cek;

pub use cek::{
    evaluate, evaluate_with_kernel, step, Continuation, EvalState, Frame, PureFrame, StepResult,
    CEK_MAX_STEPS_DEFAULT,
};
