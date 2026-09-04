#![forbid(unsafe_code)]

//! Differential harness (MOD-15): black-box observation of production vs reference.
//!
//! - **M2:** Value / Var / Let / Seq / If
//! - **M3:** Lambda / Call
//! - **M4:** Attenuate / capability algebra (independent reference store)
//! - **M5:** Request / effects / durable-before-host
//! - **M6:** Actors / mailbox FIFO / scheduler / quiescence

pub mod m2;
pub mod m3;
pub mod m4;
pub mod m5;
pub mod m6;

pub use m2::{compare_m2, observe_production, observe_reference, Observation, M2_DIFF_MAX_STEPS};
pub use m4::{compare_m4, observe_production_m4, observe_reference_m4};
pub use m5::{compare_m5, observe_production_m5, observe_reference_m5};
pub use m6::{
    compare_m6, observe_production_m6, observe_reference_m6, ActorObservation, StatusLabel,
    TerminalLabel,
};
