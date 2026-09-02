# 05 — Terminology Normalization (Glossary)

Canonical terms used in `01-canonical-specification.md`, with the aliases observed in the source and the resolution rule. Where the source uses one term in an early draft and another in the frozen text, **the frozen term is canonical**; the alias is retained for traceability.

## 1. Core objects

| Canonical term | Definition (normative) | Aliases observed in source | Resolution |
|---|---|---|---|
| **LLM / planner** | Probabilistic proposal engine; untrusted; `LLMOutput ∈ Data` | "the model", "Planner", "probabilistic planner", "LLM/planner" | Frozen: "LLM / planner" (S-05) |
| **PlanProposal** | Planner output: `{ observation_sequence, block, planner_metadata }` | "proposal", "planner response" | Frozen: `PlanProposal` (L27175) |
| **PlannerAccepted** | Recorded accepted proposal for replay | "recorded proposal" | Frozen: `PlannerAccepted` (L27411) |
| **Block** | Homoiconic untrusted program data (language surface) | "program", "source", "raw Block" | Frozen: `Block`; never a security boundary |
| **ExecutablePlan** | Validated compiler artifact; the only machine input | "ValidatedPlan", "CapabilityCheckedPlan", "PlanIR", "executable plan" | Pipeline names (`NormalizedAST`, `ValidatedPlan`, `PlanIR`) are **stage names**; the final artifact is `ExecutablePlan` (R-ARCH-01). "Plan" (early [2] "really interesting primitive") is obsolete. |
| **Effect** | Immutable effect data `{capability, operation, target, params, cost}` | "Effect descriptor", "canonical Effect" | Frozen: `Effect` (S-12) |
| **EffectRequest** | Transient machine→host message `{id, effect}` | "request", "host message" | Frozen: `EffectRequest` (L23758) |
| **EffectIssued** | Durable commitment fact `{id, actor, effect_digest, logical_time, issue_cost, reservation}` | "issued record" | Frozen: `EffectIssued` (L23765) |
| **EffectReceipt** | Host→machine result `{id, effect_digest, result}` | "receipt", "result" | Frozen: `EffectReceipt` |
| **EffectId** | Monotonic u64 allocation counter value | "handle", "h", "effect handle" | "handle" is obsolete (v0.3 used `h`); `EffectId` is canonical |
| **EffectDigest** | `SHA-256(canonical_bytes(effect))`; semantic identity | "digest" | Frozen: `EffectDigest` (L23738) |
| **EffectCost** | `{issue, complete_max, reserve}` | `Cost` (v1: anonymous consumable/reserved pair) | `complete` renamed to `complete_max` in the Phase 13 correction; `complete_max` is canonical (C-29 resolved) |
| **CapRef** | Opaque generation-safe capability reference `{index, generation}` | "capability reference", "capability handle", "c" | Frozen: `CapRef` |
| **Authority** | Operation-indexed grant set `A = {(o, ⟨S,Q,R,T⟩)}` | "authority map", "κ(c)" | Frozen: `Authority` (algebra v0.2) |
| **Constraint** | Narrowing request (≠ Authority) | "σ", "attenuation constraint", "spawn constraint" | Frozen: `Constraint` (R-CAP-04) |
| **CapabilityKernel** | Trusted authority decision layer | "kernel", "capability kernel" | Frozen: `CapabilityKernel` |
| **CapabilityContext** | Actor-local name→CapRef binding | "actor capability set" | Frozen: `CapabilityContext` (L25548) |
| **derive / attenuation** | `derive(A,C)`; runtime operation `attenuate` | "derivation", "delegate" (delegation is the cross-actor form) | `derive` = algebra op; `attenuate` = machine operation; `delegate` = cross-actor authority transfer (R-MARSHAL-02) |
| **DelegatedCapability** | Marshaller-accepted envelope for explicit delegation | "delegated capability" | Frozen: `Value::DelegatedCapability` (L25995) |

## 2. Budget & time

| Canonical term | Definition | Aliases | Resolution |
|---|---|---|---|
| **Budget** | `B = ⟨C, R, W⟩` | "budget vector", "B" | Frozen v0.3 (S-11) |
| **Consumable** | `⟨fuel, io, duration⟩` strictly decreasing | "C", "consumables" | `C` is the vector; dimensions are named, not tuple positions |
| **Reserved** | `⟨memory, slots⟩` held then released | "R", "reserved capacity" | |
| **Deadline** | Absolute logical bound `W ∈ ℕ∪{∞}`; `Deadline(None)` = ∞ | "W", "deadline" | |
| **LogicalTime** | Explicit deterministic time `t`; global | "logical clock", "t", "deterministic timestamp" | Never wall-clock (R-CAP-09) |
| **escrowed / consumed / available** | The three budget accounting partitions | "held", "spent", "remaining" | Frozen partition (L28355–28359); `C_available + C_escrowed + C_consumed = C_initial` |
| **Cost / CostModel** | `Cost {consumable, reserved}`; op→cost mapping contract | "cost function", "ΔB" | Frozen: `CostModel` trait + `Cost` (R-BUDGET-07) |

## 3. Machine & actors

| Canonical term | Definition | Aliases | Resolution |
|---|---|---|---|
| **CEK machine** | Explicit continuation evaluator | "evaluator", "transition engine", "small-step machine" | Frozen: CEK machine (S-08) |
| **EvalState** | `{expr, env, continuation}` | "eval state", "actor.eval" | |
| **Frame** | Continuation frame (frozen set, R-CEK-03) | "continuation frame" | |
| **GlobalState** | Frozen global configuration (R-ACTOR-02) | "G", "GlobalConfig" (v0.3 used `GlobalConfig`; the frozen Rust name is `GlobalState`) | **`GlobalState` canonical**; `GlobalConfig` obsolete (C-42) |
| **ActorState** | Actor-local state (R-ACTOR-02) | "A_a", "local actor state" | |
| **RunState** | `Runnable/Running/Pending/Blocked/Halted/Faulted` | "status" (partially) | **Two distinct notions, do not conflate**: `RunState` (scheduler-visible) vs `ActorStatus` (machine-visible: `Running/Pending/Blocked/Halted/Fault`). The source uses both enums (L25514–25557, L23784); the frozen text keeps both. See C-18. |
| **RunnableQueue** | FIFO, at-most-once membership | "runnable", "scheduler queue" | |
| **Scheduler** | Deterministic FIFO turn-granting | "scheduling" | |
| **Spawn** | Actor creation with escrow + attenuation | "spawn", "E-Spawn" | |
| **Send / Receive** | Asynchronous send; blocking receive | "message passing" | |
| **Mailbox** | Per-actor FIFO of `MarshalledValue` | "queue of marshalled values" | |
| **MarshalledValue** | Canonical bytes transport | "marshalled data" | |

## 4. Persistence & recovery

| Canonical term | Definition | Aliases | Resolution |
|---|---|---|---|
| **Canonical encoding / CanonicalSerialize** | 15A semantic byte format | "canonical serialization", "wire format" | Traits: `CanonicalPayload` / `CanonicalEncode` / `CanonicalDecode` (S-17) |
| **Envelope** | `version ‖ type_tag  payload_length ‖ payload` | "canonical envelope" | |
| **WAL / WalFrame / WalRecord** | 15B persistence framing + record taxonomy | "persistence log", "record" | "Event Log" (machine-level, in-memory) ≠ "WAL" (durable). `EventLog` = in-memory append log of `EventEnvelope`; `WAL` = its durable framing. See U-16. |
| **Effect journal** | Durable causal effect record (Prepared/Issued/Completed/Reconciled) | "journal", "H" | In 15B the journal records live **inside the WAL** as record kinds (C-39); "separate journal" (Phase 14) is superseded wording |
| **Snapshot / GlobalSnapshot** | Committed state image + digest | "S" | |
| **Crash matrix T0–T6** | Normative crash points | "crash points" | |
| **Indeterminate** | Effect state `Issued ∧ ¬Completed` (pre-reconciliation) | "interrupted effect" | Never `NotExecuted` (R-DUR-04) |
| **Reconciliation / ReconciliationOutcome** | Authoritative host-side resolution of Indeterminate | "reconcile" | Outcome variants undefined — U-15 |
| **RecoveryFault** | Explicit invalid-persistence outcome | "recovery error" | |
| **ReplayHost** | Ordered recorded-effect host | "replay host", "recorded host" | |
| **Supervisor** | Lifecycle/recovery authority (trusted) | "supervisor process" | |

## 5. Verification

| Canonical term | Definition | Aliases | Resolution |
|---|---|---|---|
| **Reference model** | Independent executable semantic model | "reference implementation", "executable reference model", "oracle" | "oracle" is informal; canonical: reference model |
| **Differential (test/harness)** | Production vs reference comparison of normalized observations | "differential verification" | |
| **Normalized observation** | The comparison domain (terminal states, traces, partitions, …) | "semantic observation" | Frozen list in R-REF-05 |
| **First divergence** | Comparator reports earliest mismatch | "divergence" | |
| **Mutation / mutant** | Injected deliberate fault / its instance | "known semantic defect" | |
| **Kill rate** | Killed non-equivalent mutants / registered non-equivalent mutants | "mutation kill rate" | Target 100% |
| **Equivalent mutant** | Behaviorally indistinguishable mutant (adjudicated, documented) | "equivalent mutation" | |
| **Obligation tag** | Source's stable verification identifiers (`CEK-CALL-ARITY-PRECHECK`, …) | "coverage ID" | See `08` §3 for the canonical tag list |
| **Counterexample artifact** | 16-field reproducible failure record | "failure record" | |
| **Adjudication** | 4-way classification of divergences | "fault classification" | |

## 6. Normalization rules applied in `01`

1. `invoke` (v1/v2 calculus) ≙ `request` (frozen surface). The frozen AST uses `Expr::Request`; the calculator-level `invoke(e_eff, e_cap)` wording is retained only in supersession notes.
2. `handle`/`h` ≙ `EffectId`.
3. `GlobalConfig` ≙ `GlobalState`.
4. `complete` ≙ `complete_max` (EffectCost).
5. "15 transition rules" ≙ the frozen transition system as expressed through the 16-step request sequence + pure/actor rules (C-01: numbering is a presentation artifact; the gated rule *content* is what is frozen).
6. "Journal" (separate) ≙ WAL record kinds (15B unified).
7. `Bincode` is explicitly **not** the canonical format (R-CANON-01); it may implement it.
8. `surjectivity (within domain)` (source L28465) is a misnomer for **injectivity**; `01` uses "injectivity" throughout (C-12).
9. "Frozen" always means "requirements stable"; it never means "verified" (R-SCOPE-02).
10. "Verification: FROZEN" in status blocks means *the verification contract* is frozen, not that verification has been performed.

## 7. Undefined or under-specified terms (extracted to `09`)

| Term | Where used | Issue | ID |
|---|---|---|---|
| `PlannerMetadata` | PlanProposal | Fields never defined | U-13 |
| `ProposalDigest` | PlannerAccepted | Defined by usage (digest of proposal) but canonical form unspecified | U-13 |
| `CapabilityError`, `HostPolicyError`, `EffectError`, `HostFault` variants | Fault taxonomy | Enum variants not enumerated | U-14 |
| `ReconciliationOutcome` | EffectReconciled | Variants not enumerated (beyond `Indeterminate` classification) | U-15 |
| `BudgetAllocationSpec` | Spawn | Validation rules (caps, parent share) not frozen | U-03 |
| `Constraint` (data-level structure inside Expr) | Expr::Attenuate/Delegate | Canonical encoding of Constraint not in 15A frozen tag set | U-02 |
| `SchedulerState` | GlobalState | Shape not specified | U-02 |
| `Target` / `TargetExpr` / `Params` / `Op` | Effect | `Op` = finite enumerable set (informative examples FileRead…); `Target`/`Params` domain undefined beyond scope/param-constraint interpretation | U-21 |
| `Duration` (consumable D) | Budget | Operational meaning (advancement) not frozen | U-01 |
| `EventSequence` vs `WalSequence` | Persistence | Relationship between the two sequence numbers not specified | U-16 |
| `FunctionValue` | Machine Value | Shape is `{params, body, env}` (informative in R-CEK-04); canonical encoding for snapshots undefined | U-02 |
| `AdmissibleConstraint` trait | [18] contracts | Mentioned once; never re-referenced in frozen text; status ambiguous | U-09 |
