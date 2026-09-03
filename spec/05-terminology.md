# 05 — Terminology Normalization (Glossary)

Canonical terms used in `01-canonical-specification.md`, with the aliases observed in the source and the resolution rule. Where the source uses one term in an early draft and another in the frozen text, **the frozen term is canonical**; the alias is retained for traceability.

## 1. Core objects

| Canonical term | Definition (normative) | Aliases observed in source | Resolution |
|---|---|---|---|
| **LLM / planner** | Probabilistic proposal engine; untrusted; `LLMOutput ∈ Data` | "the model", "Planner", "probabilistic planner", "LLM/planner" | Frozen: "LLM / planner" (S-05) |
| **PlanProposal** | Planner output: `{ observation_sequence, block, planner_metadata }` | "proposal", "planner response" | Frozen: `PlanProposal` (L27175) |
| **PlannerAccepted** | Recorded accepted proposal for replay | "recorded proposal" | Frozen: `PlannerAccepted` (L27411) |
| **Block** | Homoiconic untrusted program data (language surface) | "program", "source", "raw Block" | Frozen: `Block`; never a security boundary |
| **ExecutablePlan** | Validated compiler artifact; the only machine input | "executable plan"; obsolete: "Plan" (early [2] "really interesting primitive") | The final artifact is `ExecutablePlan` (R-ARCH-01). **Correction (X-40):** this row's alias column previously read `"ValidatedPlan", "CapabilityCheckedPlan", "PlanIR", "executable plan"` and its resolution asserted that the pipeline names are **stage names** and "not artifacts in their own right". Two of the three are declared artifacts with their own fields — `ValidatedPlan { ir, effects }` (L865) and `CapabilityCheckedPlan { ir, required_caps }` (L866), both private to `mod compiler` — and are separate canonical terms (`term/` T-04, T-05), not aliases of `ExecutablePlan`. `PlanIR` (T-08) and `NormalizedAST` (T-07) are names the source never declares (X-29, X-30). `ValidatedPlan` is *also* the predicate of the central theorem, which is a type-vs-proposition collision (X-01, BLOCKING). The pipeline itself is written with three different stage sequences (X-02). |
| **Effect** | Immutable effect data `{op, target, params, cost}` | "Effect descriptor", "canonical Effect" | Frozen: `Effect` (L9297, S-12). **Correction (X-39):** this row previously gave the field set as `{capability, operation, target, params, cost}`, which no declaration in L1–42312 has. The frozen form is `{op, target, params, cost}`; the only form with a capability field is the superseded turn-[3] `{kind, cap_ref, target}` (L1169). `operation` is a field of `Expr::Request`, not of `Effect`. The field set matters because `EffectDigest = SHA-256(canonical_bytes(effect))`: hashing a `CapRef` into the digest would make replay fail on a valid trace. |
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
| **Canonical encoding / CanonicalSerialize** | 15A semantic byte format | "canonical serialization", "wire format" | **Correction (X-51):** this cell previously read "Traits: `CanonicalPayload` / `CanonicalEncode` / `CanonicalDecode` (S-17)". Four traits are declared, not three — `CanonicalPayload` (L29979, `TYPE_TAG: u8`), the fallible pair `CanonicalEncode`/`CanonicalDecode` (L29178/L29183), and the earlier **infallible** `CanonicalSerialize` (L27685, re-declared L28296), whose doc comment is the site of the X-50 format contradiction. `CanonicalSerialize` also appears as a *mathematical function* symbol in the state-digest formula `D_S = H(CanonicalSerialize(GlobalState))` (L27061). Which family is frozen decides whether decode failures are representable at all (R-PERSIST-02); the source's own checklist notes `CanonicalDecode` "is declared but not implemented" (L29601). |
| **Envelope** | `version ‖ type_tag  payload_length ‖ payload` | "canonical envelope" | Frozen form: `version: u8 \| type_tag: u8 \| payload_length: u32 BE \| payload` (L38147–38150, L33816). **Contradiction (X-50, BLOCKING):** the `CanonicalSerialize` doc comment specifies `[format_version: u8][type_tag: u32 LE][length: u32 LE]` (L28298) — a different field *name*, tag *width* and *endianness*. Both are recorded verbatim; neither is renamed. Envelope type tags (`Value 0x00`, `Symbol 0x20`, `CapRef 0x30`, `ActorId 0x40`, `EffectId 0x41`) and `Value` variant discriminants (`0x00`–`0x07`) are two disjoint namespaces that the frozen const blocks both spell `TAG_*` (X-54, BLOCKING; X-56). |
| **WAL / WalFrame / WalRecord** | 15B persistence framing + record taxonomy | "persistence log", "record" | "Event Log" (machine-level, in-memory) ≠ "WAL" (durable). `EventLog` = in-memory append log of `EventEnvelope`; `WAL` = its durable framing. See U-16. |
| **Effect journal** | Durable causal effect record (Prepared/Issued/Completed/Reconciled) | "journal", "H" | In 15B the journal records live **inside the WAL** as record kinds (C-39); "separate journal" (Phase 14) is superseded wording |
| **Snapshot / GlobalSnapshot** | Committed state image + digest | "S" | |
| **Crash matrix T0–T6** | Normative crash points | "crash points" | |
| **Indeterminate** | Effect state `Issued ∧ ¬Completed` (pre-reconciliation) | "interrupted effect" | Never `NotExecuted` (R-DUR-04) |
| **Reconciliation / ReconciliationOutcome** | Authoritative host-side resolution of Indeterminate | "reconcile" | **Correction (X-61):** the variant set *is* enumerated — `pub enum ReconciliationOutcome { Completed(EffectReceipt), NotExecuted, Indeterminate }` (L26593–26597), a closed three-variant set matching the three turn-[54] crash classifications (L38211, L38232, L38243). Only a host protocol capable of answering authoritatively may produce `NotExecuted` or `Completed` (L26601). `Replayed` is **not** a variant: the token occurs nowhere in L1–42312. U-15 is narrowed accordingly; AMB-15 was withdrawn on the same grounds. |
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
11. **A canonical term is a name an author must *use*, never a new identifier to introduce.** No entry in `../term/` renames a frozen API, type, mathematical symbol or protocol field. Where the source froze two names for one thing, both are recorded and the governing one is named; where it froze one name for two things, both denotations are recorded and the conflict is filed as `X-NN` in `../term/02-collisions.md`.
12. Envelope **type tags** (`Value 0x00`, `Symbol 0x20`, `CapRef 0x30`, `ActorId 0x40`, `EffectId 0x41`) and `Value` **variant discriminants** (`0x00`–`0x07`) are disjoint namespaces. The frozen const blocks spell both `TAG_*`, so prose citing a tag byte MUST name its layer (X-54, X-56).
13. A name the source uses as a type but never declares is entered as `UNDECLARED-TYPE` and given **no** invented definition (X-29, X-30): `NormalizedAST`, `PlanIR`, `Form`, `GlobalEvent`, `CapabilitySummary`, `BudgetSummary`, the seven `Observed*` types and the AST node `Expr::Delegate`.
14. "Reference machine" (turns [18]–[24]: the first deliberately boring production milestone) and "reference model" (15C onward: the independent comparator that must share zero core logic with production) are **opposite** in the one respect that matters. Canonical for the 15C oracle: *reference model* (X-48).

## 7. Undefined or under-specified terms (extracted to `09`)

| Term | Where used | Issue | ID |
|---|---|---|---|
| `PlannerMetadata` | PlanProposal | Fields never defined | U-13 |
| `ProposalDigest` | PlannerAccepted | Defined by usage (digest of proposal) but canonical form unspecified | U-13 |
| `CapabilityError`, `HostPolicyError`, `EffectError`, `HostFault` variants | Fault taxonomy | Enum variants not enumerated — **corrected in place (X-59, X-66, X-67):** the wording to the left is kept as superseded. `CapabilityError` **is** declared (L20408: `Revoked`, `Expired`, `InvalidConstraint`, `// ...`) and so is `HostFault` (L10820: `IoError(String)`, `PolicyViolation(String)`); only `HostPolicyError` and `EffectError` have no declaration. The real defects are narrower and worse: `CapabilityError::Invalid` (L20835) is used where the declared sibling is `InvalidConstraint` (L20451); and `HostFault` is used with **eight undeclared** variant paths (`ReplayTraceExhausted`, `ReplayCorruption`, `Io`, `ConcreteScopeViolation`, `UnboundCapability`, `TraceExhausted`, `ReplayIdMismatch`, `ReplayDigestMismatch`), neither declared variant being used at all — see C-56, C-57 (BLOCKING), `term/` T-72, T-74 | U-14 (escalated) |
| ~~`ReconciliationOutcome`~~ | EffectReconciled | **Removed (X-61):** the variants *are* enumerated at L26593–26597 (`Completed(EffectReceipt)`, `NotExecuted`, `Indeterminate`). The row is struck rather than deleted so the earlier claim stays traceable. What remains open under U-15 is per-class admissibility (U-06), not the variant set. | U-15 (narrowed) |
| `BudgetAllocationSpec` | Spawn | Validation rules (caps, parent share) not frozen | U-03 |
| `Constraint` (data-level structure inside Expr) | Expr::Attenuate/Delegate | Canonical encoding of Constraint not in 15A frozen tag set | U-02 |
| `SchedulerState` | GlobalState | Shape not specified | U-02 |
| `Target` / `TargetExpr` / `Params` / `Op` | Effect | `Op` = finite enumerable set (informative examples FileRead…); `Target`/`Params` domain undefined beyond scope/param-constraint interpretation | U-21 |
| `Duration` (consumable D) | Budget | Operational meaning (advancement) not frozen | U-01 |
| `EventSequence` vs `WalSequence` | Persistence | Relationship between the two sequence numbers not specified | U-16 |
| `FunctionValue` | Machine Value | Shape is `{params, body, env}` (informative in R-CEK-04); canonical encoding for snapshots undefined | U-02 |
| `AdmissibleConstraint` trait | [18] contracts | Mentioned once; never re-referenced in frozen text; status ambiguous | U-09 |

## 8. Normalization of record

This glossary lists the canonical terms used by `01-canonical-specification.md`. The **full terminology normalization** — 78 canonical terms each carrying `CANONICAL_TERM`, `FORBIDDEN_VARIANTS`, `DEFINITION`, `TYPE`, `OWNER`, `FIRST_DEFINITION` and `DEPENDENTS`; 31 non-conflation laws; and a 68-entry collision register (4 of them BLOCKING) in which every finding is cited to a frozen-source line and re-grepped by a checker — lives in `../term/`:

| File | Contents |
|---|---|
| `../term/00-overview.md` | method, guarantees, how to read an entry, corrections made outside `term/` |
| `../term/01-dictionary.md` | the 86 canonical terms (`T-01`…`T-86`) |
| `../term/02-collisions.md` | the collision register (`X-01`…`X-86`) |
| `../term/03-laws.md` | the non-conflation laws (`N-01`…`N-31`) |

Where this glossary and `../term/` disagree, the disagreement is itself filed as a collision and the correction is applied here with its `X-` id cited — see rows marked **Correction** in §1 and §4 above (X-39, X-40, X-51, X-61). Nothing in `../term/` overrides the normative text in `01` or the obligations in `03`; it normalizes the *names* those documents use.
