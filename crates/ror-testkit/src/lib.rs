#![forbid(unsafe_code)]

//! M9 mutation framework (MOD-16 / R-TEST-04/05/06).
//!
//! **Authority:** registry text is derived from `final/04` §2; this crate is a
//! **consumer**, never an authority. Kill evidence is produced by the isolated
//! runner (`scripts/m9_mutation_run.py`) which injects → builds → targeted tests
//! → differential tests → classifies.
//!
//! Production crates MUST NOT depend on this crate for semantics.

pub mod registry;
pub mod report;

pub use registry::{
    expected_ids, load_registry_from_str, MutantRecord, Registry, RegistryError, EXPECTED_COUNT,
};
pub use report::{Classification, KillRate, MutantResult, RunSummary};
