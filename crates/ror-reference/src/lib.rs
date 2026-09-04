#![forbid(unsafe_code)]

//! Independent reference model (MOD-14).
//!
//! M2+M3 pure CEK mirror for differential comparison. Transition code is
//! authored here independently — it does **not** call `ror-runtime` (R-REF-02).
//! Shared fixtures/types come from `ror-core` only.

pub mod pure_cek;

pub use pure_cek::{evaluate, step, RefKont, RefOutcome, RefState, REF_MAX_STEPS_DEFAULT};
