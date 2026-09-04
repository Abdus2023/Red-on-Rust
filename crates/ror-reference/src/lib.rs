#![forbid(unsafe_code)]

//! Independent reference model (MOD-14).
//!
//! M2 pure-subset CEK mirror for differential comparison against production.
//! Transition code is authored here independently — it does **not** call
//! `ror-runtime` (R-REF-02). Shared fixtures/types come from `ror-core` only.
//!
//! **M3 boundary:** Lambda/Call are not implemented.

pub mod pure_cek;

pub use pure_cek::{evaluate, step, RefKont, RefOutcome, RefState, REF_MAX_STEPS_DEFAULT};
