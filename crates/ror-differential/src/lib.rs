#![forbid(unsafe_code)]

//! Differential harness (MOD-15): black-box observation of production vs reference.
//!
//! - **M2:** Value / Var / Let / Seq / If
//! - **M3:** Lambda / Call

pub mod m2;
pub mod m3;

pub use m2::{compare_m2, observe_production, observe_reference, Observation, M2_DIFF_MAX_STEPS};
