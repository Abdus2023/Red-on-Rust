#![forbid(unsafe_code)]

//! Thin planner boundary (MOD-13) — M9 surfaces for R-PLANNER-06/07.
//!
//! **Not** a full LLM agent. Provides the exact epoch-equality gate and
//! CapRef-free observation sanitization required by registered mutants
//! M026/M027. Does not close OADs; does not confer authority on LLM data.

use ror_core::types::CapRef;

/// Machine-facing planner fault (R-CORE-13 / R-PLANNER-03). Provisional label.
#[derive(Clone, Debug, PartialEq, Eq)]
pub enum PlannerFault {
    /// Observation sequence ≠ current planning epoch (either direction).
    StalePlan,
    /// Observation payload contained authority (CapRef).
    ObservationAuthority,
}

/// Thin plan proposal (R-PLANNER-01 shape, reduced).
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct PlanProposal {
    pub observation_sequence: u64,
    /// Opaque plan bytes (data only — not executable authority).
    pub block: Vec<u8>,
}

/// Accept proposal iff `observation_sequence == current_planning_epoch`
/// (R-PLANNER-06 exact equality; M026 must kill less-than-only / future-accept).
pub fn accept_proposal(
    proposal: &PlanProposal,
    current_planning_epoch: u64,
) -> Result<(), PlannerFault> {
    if proposal.observation_sequence != current_planning_epoch {
        return Err(PlannerFault::StalePlan);
    }
    Ok(())
}

/// Observation record for planner (R-PLANNER-07): must not carry CapRef.
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct ObservationRecord {
    pub sequence: u64,
    pub payload: ObservationPayload,
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub enum ObservationPayload {
    Data(Vec<u8>),
    /// Forbidden in planner observations (M027).
    Capability(CapRef),
}

/// Sanitize / admit observation: CapRef payloads are rejected (R-PLANNER-07).
pub fn admit_observation(obs: &ObservationRecord) -> Result<(), PlannerFault> {
    match &obs.payload {
        ObservationPayload::Data(_) => Ok(()),
        ObservationPayload::Capability(_) => Err(PlannerFault::ObservationAuthority),
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use ror_core::types::CapRef;

    #[test]
    fn accept_current_only() {
        let p = PlanProposal {
            observation_sequence: 5,
            block: vec![1],
        };
        assert!(accept_proposal(&p, 5).is_ok());
        assert_eq!(accept_proposal(&p, 4), Err(PlannerFault::StalePlan));
        assert_eq!(accept_proposal(&p, 6), Err(PlannerFault::StalePlan));
        // Future-tagged (M026 target): must reject.
        let future = PlanProposal {
            observation_sequence: 5 + 1_000_000_000,
            block: vec![],
        };
        assert_eq!(accept_proposal(&future, 5), Err(PlannerFault::StalePlan));
    }

    #[test]
    fn observation_rejects_capref() {
        let ok = ObservationRecord {
            sequence: 1,
            payload: ObservationPayload::Data(b"x".to_vec()),
        };
        assert!(admit_observation(&ok).is_ok());
        let bad = ObservationRecord {
            sequence: 1,
            payload: ObservationPayload::Capability(CapRef::from_kernel_parts(0, 0)),
        };
        assert_eq!(
            admit_observation(&bad),
            Err(PlannerFault::ObservationAuthority)
        );
    }
}
