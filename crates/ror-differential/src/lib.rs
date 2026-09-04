#![forbid(unsafe_code)]

//! Differential harness (MOD-15): black-box observation of production vs reference.
//!
//! - **M2:** Value / Var / Let / Seq / If
//! - **M3:** Lambda / Call
//! - **M4:** Attenuate / capability algebra (independent reference store)

pub mod m2;
pub mod m3;
pub mod m4;

pub use m2::{compare_m2, observe_production, observe_reference, Observation, M2_DIFF_MAX_STEPS};
pub use m4::{compare_m4, observe_production_m4, observe_reference_m4};
