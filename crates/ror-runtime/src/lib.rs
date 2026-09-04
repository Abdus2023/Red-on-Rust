#![forbid(unsafe_code)]

//! Production runtime — CEK evaluator (MOD-05) + M5 effect pipeline.
//!
//! - **M2:** `Value` / `Var` / `Let` / `Seq` / `If`
//! - **M3:** `Lambda` / `Call` (R-CEK-04/05)
//! - **M4:** `Attenuate` via `ror-kernel` derive (R-CAP-*, REQ-CAP-022/023)
//! - **M5:** `Request` CEK frames + durable issuance + host boundary (R-CORE-14)
//!
//! **Out of scope:** multi-actor scheduler (M6), full WAL recovery (M7).
//!
//! **U-02:** frames are in-memory only — no canonical byte encoding.
//! **U-09:** uses [`ror_core::machine::Value`], never data-domain `ror_core::Value`.
//! **U-26:** [`StepResult`] is provisional.

pub mod cek;
pub mod effects;

pub use cek::{
    evaluate, evaluate_request, evaluate_with_kernel, step, step_with_effects, Continuation,
    EvalState, Frame, PureFrame, StepResult, CEK_MAX_STEPS_DEFAULT,
};
pub use effects::{
    default_effect_cost, effect_from_values, illegal_host_before_issued, run_effect_pipeline,
    run_with_memory_journal, EffectServices, HostError, HostExecutor, RequestCtx, RequestOutcome,
    DELTA_T_RECEIPT, DELTA_T_REQUEST,
};
