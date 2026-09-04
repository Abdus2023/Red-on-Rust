#![forbid(unsafe_code)]

//! Differential harness (MOD-15): black-box observation of production vs reference.
//!
//! - **M2:** Value / Var / Let / Seq / If
//! - **M3:** Lambda / Call
//! - **M4:** Attenuate / capability algebra (independent reference store)
//! - **M5:** Request / effects / durable-before-host
//! - **M6:** Actors / mailbox FIFO / scheduler / quiescence
//! - **M7:** WAL / snapshot / recovery classification (R-RECOV-04)
//! - **M8:** Differential **system** — generator, runners, normalize, compare,
//!   first-divergence, shrinker, R-TEST-02 artifacts, coverage evidence
//!   (R-REF-01…06, R-TEST-02/03/07).
//! - **M10:** Crash/recovery verification gate — T0–T6 matrix + recovery
//!   differential (R-ORDER-02 / R-TEST-08 / R-RECOV-02). Consumes M7; does not
//!   redesign persistence. F-04 / OADs remain open; R-REG not promoted.
//!
//! **F-04:** observation schema in [`system`] is provisional; OAD/UNKNOWN not closed.
//! This crate orchestrates; it is not a second runtime.

pub mod m10;
pub mod m2;
pub mod m3;
pub mod m4;
pub mod m5;
pub mod m6;
pub mod m7;
pub mod system;

pub use m10::{
    assert_completed_reconstruct, assert_issued_not_completed_is_indeterminate,
    assert_prepared_not_issued_is_discard, inject_crash, inject_crash_with_effect,
    inject_t1_journal_crash, m10_gate_status, run_full_matrix, run_row, ExpectedClass,
    MatrixReport, MatrixRow, MatrixSpec, RowResult, MATRIX,
};
pub use m2::{compare_m2, observe_production, observe_reference, Observation, M2_DIFF_MAX_STEPS};
pub use m4::{compare_m4, observe_production_m4, observe_reference_m4};
pub use m5::{compare_m5, observe_production_m5, observe_reference_m5};
pub use m6::{
    compare_m6, observe_production_m6, observe_reference_m6, ActorObservation, StatusLabel,
    TerminalLabel,
};
pub use m7::{
    compare_m7, fixture_completed, fixture_issued_indeterminate, fixture_prepared_discard,
    fixture_snapshot_t6, observe_production_m7, observe_reference_m7, RecoveryObservation,
};
pub use system::{
    compare, default_divergence_pred, execute_seeded, exhaustive_small_state,
    first_divergence_report, generate, run_case, run_production, run_reference, shrink,
    CompareResult, CounterexampleArtifact, CoverageEvidence, DiffPath, DiffProgram, Difference,
    ExecutionInput, FirstDivergence, GenConfig, GeneratedProgram, NormalizedObservation,
    ObservationSide, ShrinkResult, GENERATOR_VERSION, SEMANTIC_VERSION, TEST_CASE_VERSION,
};
