#![forbid(unsafe_code)]

//! Independent reference model (MOD-14).
//!
//! Covers M2–M6 observation mirrors plus M7 independent recovery (R-RECOV-04).
//!
//! Transition code is authored here independently — it does **not** call
//! `ror-runtime`, `ror-kernel`, or `ror-persistence` (R-REF-02 / R-SCOPE-04).
//! Shared fixtures/types come from `ror-core` only.

pub mod actor_model;
pub mod cap_algebra;
pub mod effect_model;
pub mod pure_cek;
pub mod recovery_model;

pub use actor_model::{
    ref_admit_delegation, ref_contains_capability, ref_issue_delegation, ref_marshal,
    ref_receive_or_block, ref_run_until_quiescent, ref_scheduler_turn, ref_send,
    ref_send_delegation, ref_spawn_child, RefActor, RefActorStatus, RefGlobal, RefGlobalStep,
    RefMachineEvent, RefMailbox, RefRunnable, RefSpawnBudget,
};
pub use cap_algebra::{RefAuthority, RefCapabilityStore, RefOpAuthority};
pub use effect_model::{
    ref_default_cost, ref_effect_from_values, ref_run_pipeline, RefHost, RefJournal, RefMockHost,
    RefPanicHost, RefRequestOutcome, REF_DELTA_T_REQUEST,
};
pub use pure_cek::{
    evaluate, evaluate_request_ref, evaluate_with_store, step, step_with_effects,
    RefEffectServices, RefKont, RefOutcome, RefState, REF_MAX_STEPS_DEFAULT,
};
pub use recovery_model::{
    ref_digest_of, ref_effect_id, ref_recover, RefEffectClass, RefRecoveryFault,
    RefRecoveryObservation,
};
