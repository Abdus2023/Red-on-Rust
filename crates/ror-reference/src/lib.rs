#![forbid(unsafe_code)]

//! Independent reference model (MOD-14).
//!
//! M2+M3 pure CEK + M4 capability algebra mirror for differential comparison.
//! Transition code is authored here independently — it does **not** call
//! `ror-runtime` or `ror-kernel` (R-REF-02 / R-SCOPE-04).
//! Shared fixtures/types come from `ror-core` only.

pub mod cap_algebra;
pub mod pure_cek;

pub use cap_algebra::{RefAuthority, RefCapabilityStore, RefOpAuthority};
pub use pure_cek::{
    evaluate, evaluate_with_store, step, RefKont, RefOutcome, RefState, REF_MAX_STEPS_DEFAULT,
};
