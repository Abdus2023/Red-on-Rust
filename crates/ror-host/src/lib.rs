#![forbid(unsafe_code)]

//! Host adapter (MOD-09) — M5 mock / replay / panic hosts.
//!
//! **R-HOST-02:** host performs only issued effects. Host is **not** an
//! AuthorityIssuer. Callers must enforce `DurableIssued` before `execute`
//! (GI-SEC-07); [`PanicHost`] fails closed if invoked without the gate.
//!
//! Implements [`ror_runtime::HostExecutor`] (trait owned by runtime to avoid
//! Cargo cycles).

use ror_core::effect::{EffectReceipt, EffectRequest, ReceiptValue};
use ror_core::types::EffectId;
use ror_runtime::{HostError, HostExecutor};
use std::collections::VecDeque;

/// Always succeeds with Unit (test mock).
#[derive(Clone, Debug, Default)]
pub struct MockHost {
    pub calls: Vec<EffectId>,
}

impl MockHost {
    pub fn new() -> Self {
        Self::default()
    }
}

impl HostExecutor for MockHost {
    fn execute(&mut self, request: &EffectRequest) -> Result<EffectReceipt, HostError> {
        self.calls.push(request.id);
        Ok(EffectReceipt {
            id: request.id,
            effect_digest: request.digest,
            result: Ok(ReceiptValue::Unit),
        })
    }
}

/// Always denies at host policy (R-HOST-01 defense-in-depth path).
#[derive(Clone, Debug, Default)]
pub struct DenyHost;

impl HostExecutor for DenyHost {
    fn execute(&mut self, request: &EffectRequest) -> Result<EffectReceipt, HostError> {
        let _ = request;
        Err(HostError::PolicyDenied)
    }
}

/// Ordered replay host (R-HOST-03): returns scripted receipts in order.
#[derive(Clone, Debug, Default)]
pub struct ReplayHost {
    queue: VecDeque<Result<EffectReceipt, HostError>>,
    pub calls: Vec<EffectId>,
}

impl ReplayHost {
    pub fn new() -> Self {
        Self::default()
    }

    pub fn push(&mut self, r: Result<EffectReceipt, HostError>) {
        self.queue.push_back(r);
    }
}

impl HostExecutor for ReplayHost {
    fn execute(&mut self, request: &EffectRequest) -> Result<EffectReceipt, HostError> {
        self.calls.push(request.id);
        match self.queue.pop_front() {
            Some(Ok(mut rec)) => {
                // Bind identity to requested effect (R-HOST-03 ID+digest discipline).
                rec.id = request.id;
                rec.effect_digest = request.digest;
                Ok(rec)
            }
            Some(Err(e)) => Err(e),
            None => Err(HostError::ReplayFault),
        }
    }
}

/// PanicHost: any execute is a test failure (R-HOST-02 harness).
///
/// Used to prove host is never reached on deny / pre-Issued paths.
#[derive(Clone, Debug, Default)]
pub struct PanicHost {
    pub invoked: bool,
}

impl PanicHost {
    pub fn new() -> Self {
        Self::default()
    }
}

impl HostExecutor for PanicHost {
    fn execute(&mut self, request: &EffectRequest) -> Result<EffectReceipt, HostError> {
        self.invoked = true;
        panic!(
            "PanicHost: HostExecutor::execute invoked without durable Issued (id={:?}) — GI-SEC-07",
            request.id
        );
    }
}

/// Map host error to machine-facing code (no debug strings).
pub fn host_error_code(e: &HostError) -> ror_core::effect::HostFaultCode {
    e.code()
}

#[cfg(test)]
mod tests {
    use super::*;
    use ror_core::capability::Op;
    use ror_core::digest::EffectDigest;
    use ror_core::effect::{Effect, EffectCost, Params, Target};
    use ror_core::types::{ActorId, CapRef, EffectId};

    fn sample_req() -> EffectRequest {
        let effect = Effect::new(
            CapRef::from_kernel_parts(0, 0),
            Op::FileRead,
            Target(1),
            Params::empty(),
            EffectCost::zero(),
        );
        let bytes = effect.canonical_bytes();
        let digest = EffectDigest::of_bytes(&bytes);
        EffectRequest {
            id: EffectId(0),
            actor: ActorId(0),
            digest,
            effect_bytes: bytes,
            cost: EffectCost::zero(),
            effect,
        }
    }

    #[test]
    fn mock_host_records_call() {
        let mut h = MockHost::new();
        let r = h.execute(&sample_req()).unwrap();
        assert_eq!(r.id, EffectId(0));
        assert_eq!(h.calls, vec![EffectId(0)]);
    }

    #[test]
    #[should_panic(expected = "GI-SEC-07")]
    fn panic_host_panics() {
        let mut h = PanicHost::new();
        let _ = h.execute(&sample_req());
    }

    #[test]
    fn replay_host_ordered() {
        let mut h = ReplayHost::new();
        h.push(Ok(EffectReceipt {
            id: EffectId(99),
            effect_digest: EffectDigest::of_bytes(b"x"),
            result: Ok(ReceiptValue::Integer(7)),
        }));
        let r = h.execute(&sample_req()).unwrap();
        assert_eq!(r.id, EffectId(0));
        assert_eq!(r.result, Ok(ReceiptValue::Integer(7)));
    }
}
