#![forbid(unsafe_code)]

//! Differential harness (MOD-15): black-box observation of production vs reference.
//!
//! M2 surface: Value / Var / Let / Seq / If (final/04).
//! Compares terminal observations only — not internal frame layouts (R-REF-05 spirit).

pub mod m2;

pub use m2::{compare_m2, observe_production, observe_reference, Observation, M2_DIFF_MAX_STEPS};
