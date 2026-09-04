#![forbid(unsafe_code)]

//! Independent reference model (MOD-14).
//!
//! M2+M3 pure CEK + M4 capability algebra + M5 effect/request mirror.
//! Transition code is authored here independently — it does **not** call
//! `ror-runtime` or `ror-kernel` (R-REF-02 / R-SCOPE-04).
//! Shared fixtures/types come from `ror-core` only.

pub mod cap_algebra;
pub mod effect_model;
pub mod pure_cek;

pub use cap_algebra::{RefAuthority, RefCapabilityStore, RefOpAuthority};
pub use effect_model::{
    ref_default_cost, ref_effect_from_values, ref_run_pipeline, RefHost, RefJournal, RefMockHost,
    RefPanicHost, RefRequestOutcome, REF_DELTA_T_REQUEST,
};
pub use pure_cek::{
    evaluate, evaluate_request_ref, evaluate_with_store, step, step_with_effects,
    RefEffectServices, RefKont, RefOutcome, RefState, REF_MAX_STEPS_DEFAULT,
};
