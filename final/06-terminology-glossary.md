# FINAL1 — 06. Terminology Glossary (Canonical)

The canonical terminology layer of the FINAL1 set. Full definitions remain single-homed in `term/01-dictionary.md` (the normalization of record, T-01…T-86 with FORBIDDEN_VARIANTS, DEFINITION, OWNER, FIRST_DEFINITION, DEPENDENTS); this file is the glossary **index** plus the verbatim cleaned glossary tables (`spec/05`) — no definition is re-authored. Canonical terms are names an author must *use*, never new identifiers to introduce (term/ rule 11): FINAL1 renamed no API, type, mathematical symbol, or protocol field.

## 1. The nine required distinctions (bridges in the frozen source)

These are the distinctions the FINAL1 order explicitly requires to be preserved — including production↔reference pairs:

| Distinction | Law | Bridge in the frozen source |
|---|---|---|
| `Block ≠ ExecutablePlan` | N-01 | `ExecutablePlan` carries `_sealed: Sealed` and is private to `mod compiler`; a raw `Block` has no path into `step()` (L9115) |
| `PlanProposal ≠ ExecutablePlan` | N-02 | `PlanProposal` *contains* a `Block` (L27175); the planner cannot bypass compilation (L27271-27285) |
| `CapRef ≠ Authority` | N-03 | `AuthOK(c,E,t) ⇔ Valid(c,t) ∧ Authorized(Authority(c),E,t)` (L7323) — authority is obtained *from* the ref, it is not the ref |
| `EffectRequest ≠ EffectIssued` | N-04 | `EffectRequest` is transient, `EffectIssued` is the durable fact of commitment (L23756-23772); `WalRecord::EffectPrepared` precedes `WalRecord::EffectIssued` |
| `EffectIssued ≠ EffectCompleted` | N-05 | `Completed(E) ⇒ Issued(E)` and `Issued(E) ⇒ Prepared(E)` (L35139-35142); distinct WAL kinds with distinct payloads |
| `Specification ≠ Implementation` | N-06 | status ladder `SPECIFIED → IMPLEMENTED`; this repository has no implementation, so nothing is above `SPECIFIED` |
| `Implementation ≠ Verification` | N-07 | R-SCOPE-04 zero shared core logic (L37696); "testing an implementation against its own buggy logic merely proves consistency, not correctness" (L11779) |
| `Verification ≠ Proof` | N-08 | "machine-checked evidence of refinement … formal proof obligations remain separately identified" (L28263) |
| `LLM output ≠ Authority` | N-09 | `LLMOutput ∈ Data`, **not** `LLMOutput ∈ Authority` (L27253-27260) |

**Production ↔ reference identity pairs (canonical, never collapsed):** production `Value` (R-CALC-01) vs reference-model values (`RefValue` family, 15C); production `CapRef` (R-KERN-01) vs `RefCapId`; production `ActorId` (R-ACTOR-03) vs `RefActorId`; production `EffectId` (R-EFFECT-03) vs `RefEffectId` — declared at 15C.4 L35471–35473 with the conversion ban ("Identifiers are mapped only at the harness boundary when constructing equivalent initial states", 15C.21). The declaration duplication is recorded at REF1 F-08; the `ror-core` import allowance tension is F-01/F-11 — both open, both carried.

## 2. Cleaned glossary (verbatim from `spec/05`, incl. its §6 normalization rules and §7 undefined-terms extraction)


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

## 3. Non-conflation laws (N-01…N-33, canonical home `term/03-laws.md`)

| Law | Distinction | Mandated by | Enforced by |
|---|---|---|---|
| `N-01` | `Block ≠ ExecutablePlan` | request §Special rule; frozen source L3834, L41440-41452 | R-COMPILE-01, R-COMPILE-05, R-ARCH-03, R-ORDER-03 gate property 1 |
| `N-02` | `PlanProposal ≠ ExecutablePlan` | request §Special rule | R-PLANNER-01, R-PLANNER-02, R-CORE-01, R-COMPILE-02 |
| `N-03` | `CapRef ≠ Authority` | request §Special rule; frozen source L7323, L41052 | R-CAP-01, R-CAP-05, R-KERN-03, R-TRUST-03, R-ORDER-03 gate property 2 |
| `N-04` | `EffectRequest ≠ EffectIssued` | request §Special rule; frozen source L23726-23772 | R-DUR-01, R-DUR-02, R-EFFECT-03 step 14, R-CORE-06 |
| `N-05` | `EffectIssued ≠ EffectCompleted` | request §Special rule; frozen source L26576, L35140 | R-DUR-03, R-DUR-04, R-RECOV-02, R-CORE-09, RECOVERY-ISSUED-INDETERMINATE |
| `N-06` | `Specification ≠ Implementation` | request §Special rule | R-SCOPE-02, R-CLAIM-01, spec/00 §2 ladder |
| `N-07` | `Implementation ≠ Verification` | request §Special rule | R-SCOPE-04, R-REF-02, R-CLAIM-01, R-TEST-09 |
| `N-08` | `Verification ≠ Proof` | request §Special rule; frozen source L28263, L37444-37452 | R-CLAIM-01, R-CLAIM-03, spec/00 §2 `PROVEN` rung |
| `N-09` | `LLM output ≠ Authority` | request §Special rule; frozen source L27271-27285 | R-CORE-01, R-PLANNER-01, R-PLANNER-02, R-TRUST-01, R-TRUST-02 |
| `N-10` | `ParsedBlock ≠ ValidatedPlan` | request §Required distinctions | R-COMPILE-02, R-COMPILE-03 |
| `N-11` | `ValidatedPlan ≠ CapabilityCheckedPlan` | request §Required distinctions | R-COMPILE-03, R-CAP-04 |
| `N-12` | `CapabilityCheckedPlan ≠ ExecutablePlan` | request §Required distinctions | R-COMPILE-03, R-COMPILE-05, R-BUDGET-01 |
| `N-13` | `Effect ≠ EffectRequest` | request §Required distinctions | R-CALC-04, R-EFFECT-01, R-EFFECT-06 |
| `N-14` | `EffectIssued ≠ EffectReceipt` | request §Required distinctions | R-EFFECT-06, R-DUR-03, R-HOST-03, EFFECT-RECEIPT-DIGEST-VALIDATION |
| `N-15` | `ActorStatus ≠ RunState` | request §Required distinctions; C-18 | R-ACTOR-02, R-ACTOR-04, SCHED-BLOCKED-NOT-SCHEDULED |
| `N-16` | `Budget ≠ Consumable` | request §Required distinctions | R-BUDGET-01, R-CORE-05, BUDGET-CONSUMPTION-CONSERVATION |
| `N-17` | `Consumable ≠ Reserved` | request §Required distinctions; C-07 | R-BUDGET-03, R-BUDGET-04, BUDGET-ESCROW-CONSERVATION |
| `N-18` | `LogicalTime ≠ Deadline` | request §Required distinctions | R-BUDGET-06, R-CAP-09, R-CORE-08 |
| `N-19` | `WAL ≠ EventLog` | request §Required distinctions; U-16 | R-PERSIST-01, R-PERSIST-03, R-DUR-01, WAL-GAP-REJECT |
| `N-20` | `WAL ≠ EffectJournal` as STRUCTURES, but the journal is not a separate durable file either: in the frozen 15B model the journal's records ARE `WalRecord` kinds | request §Required distinctions; C-25 | R-DUR-02, R-DUR-03, R-PERSIST-03 |
| `N-21` | `Snapshot ≠ WAL` | request §Required distinctions | R-PERSIST-04, R-PERSIST-05, R-RECOV-01, R-RECOV-03, SNAPSHOT-COMMIT-INTEGRITY |
| `N-22` | `Observation (planner-facing) ≠ Observation (differential)` | request §Required distinctions; X-06 | R-PLANNER-01, R-REF-05, R-TEST-03 |
| `N-23` | `EffectId ≠ EffectDigest` | request §Required distinctions | R-CALC-04, R-DUR-03, R-EFFECT-06, R-HOST-03 |
| `N-24` | `Indeterminate ≠ NotExecuted` | request §Required distinctions | R-DUR-04, R-RECOV-02, R-RECOV-07, R-CORE-09, R-CLAIM-02 |
| `N-25` | `HostPolicy ≠ Authority` | request §Required distinctions | R-HOST-01, R-CORE-02, R-TRUST-01 |
| `N-26` | `ReplayHost ≠ LiveHost` | request §Required distinctions; C-22 | R-HOST-02, R-HOST-03, R-HOST-04, R-CORE-08 |
| `N-27` | `ReferenceModel ≠ Production implementation` | request §Required distinctions | R-SCOPE-04, R-REF-01, R-REF-02, R-REF-04 |
| `N-28` | `Constraint ≠ Authority` | request §Required distinctions | R-CAP-02, R-CAP-04, R-CORE-04, CAP-DERIVE-NO-AMPLIFICATION |
| `N-29` | `delegate ≠ attenuate ≠ derive` | spec/05 §1 (derive/attenuate/delegate row) | R-MARSHAL-01, R-MARSHAL-02, R-CAP-04, R-CORE-07 |
| `N-30` | `Mailbox ≠ RunnableQueue` | request §Required distinctions | R-ACTOR-03, R-ACTOR-04, R-ACTOR-07, SCHED-FIFO |
| `N-31` | `Frozen ≠ Verified` | spec/05 §6.9-6.10; request §Special rule (by implication) | R-SCOPE-02, R-SCOPE-03, R-TEST-09 |
| `N-32` | `SchedulerTrace ≠ EventLog` | spec/06 C-98; spec/09 U-35 | R-CORE-08, R-ACTOR-04 |
| `N-33` | `Lifetime ≠ WallClockInterval` | spec/06 C-100; spec/09 U-36 | R-CAP-09, R-CORE-08 |


## 4. Canonical term index (T-01…T-86 — definitions at the cited homes)

| ID | Canonical term | Type | Owner | Domain | Collisions filed against it |
|---|---|---|---|---|---|
| T-01 | `Block` | RUST-STRUCT | MOD-02 | PLAN-PIPELINE | `X-02`, `X-15`, `X-28`, `X-29`, `X-62` |
| T-02 | `PlanProposal` | RUST-STRUCT | MOD-13 | PLAN-PIPELINE | `X-04`, `X-06`, `X-34`, `X-62`, `X-64`, `X-69` |
| T-03 | `ParsedBlock` | RUST-STRUCT | MOD-02 | PLAN-PIPELINE | `X-01`, `X-02`, `X-28`, `X-29`, `X-41` |
| T-04 | `ValidatedPlan` | RUST-STRUCT | MOD-02 | PLAN-PIPELINE | `X-01`, `X-02`, `X-04`, `X-34`, `X-40`, `X-41`, `X-64` |
| T-05 | `CapabilityCheckedPlan` | RUST-STRUCT | MOD-02 | PLAN-PIPELINE | `X-01`, `X-02`, `X-40` |
| T-06 | `ExecutablePlan` | RUST-STRUCT | MOD-02 | PLAN-PIPELINE | `X-01`, `X-02`, `X-03`, `X-30`, `X-34`, `X-40`, `X-41`, `X-62` |
| T-07 | `NormalizedAST` | UNDECLARED-TYPE | MOD-02 | PLAN-PIPELINE | `X-02`, `X-29`, `X-40`, `X-41` |
| T-08 | `PlanIR` | UNDECLARED-TYPE | MOD-02 | PLAN-PIPELINE | `X-02`, `X-03`, `X-16`, `X-30`, `X-34`, `X-40`, `X-41`, `X-62`, `X-75` |
| T-09 | `CapRef` | RUST-STRUCT | MOD-03 | AUTHORITY | `X-05`, `X-25`, `X-26`, `X-27`, `X-36`, `X-38`, `X-59`, `X-66`, `X-77`, `X-82` |
| T-10 | `Authority` | MATH-SYMBOL | MOD-03 | AUTHORITY | `X-05`, `X-08`, `X-09`, `X-10`, `X-11`, `X-13`, `X-17`, `X-25`, `X-36`, `X-37`, `X-38`, `X-59`, `X-70`, `X-77`, `X-78`, `X-82`, `X-84` |
| T-11 | `AuthorityNode` | RUST-STRUCT | MOD-03 | AUTHORITY | `X-37`, `X-77`, `X-82`, `X-84` |
| T-12 | `Constraint` | RUST-STRUCT | MOD-03 | AUTHORITY | `X-08`, `X-16`, `X-17`, `X-70`, `X-77`, `X-78`, `X-84` |
| T-13 | `CapabilityKernel` | COMPONENT | MOD-03 | AUTHORITY | `X-05`, `X-36`, `X-37`, `X-55`, `X-66`, `X-70`, `X-77`, `X-82` |
| T-14 | `CapabilityContext` | RUST-STRUCT | MOD-06 | AUTHORITY | `X-37`, `X-57`, `X-82` |
| T-15 | `DelegatedCapability` | RUST-VARIANT | MOD-06 | AUTHORITY | `X-29`, `X-70`, `X-77`, `X-78` |
| T-16 | `Effect` | RUST-STRUCT | MOD-08 | EFFECT | `X-04`, `X-05`, `X-20`, `X-26`, `X-27`, `X-35`, `X-36`, `X-39`, `X-44` |
| T-17 | `EffectRequest` | RUST-STRUCT | MOD-08 | EFFECT | `X-04`, `X-27`, `X-35`, `X-57`, `X-73`, `X-74`, `X-86` |
| T-18 | `EffectIssued` | STATE-VS-RECORD | MOD-11 | EFFECT | `X-07`, `X-24`, `X-32`, `X-57`, `X-81` |
| T-19 | `EffectReceipt` | RUST-STRUCT | MOD-08 | EFFECT | `X-09`, `X-43`, `X-61`, `X-81` |
| T-20 | `EffectId` | RUST-NEWTYPE | MOD-08 | EFFECT | `X-07`, `X-22`, `X-24`, `X-43`, `X-61`, `X-81` |
| T-21 | `EffectDigest` | RUST-NEWTYPE | MOD-08 | EFFECT | `X-07`, `X-26`, `X-39`, `X-50` |
| T-22 | `EffectCost` | RUST-STRUCT | MOD-08 | EFFECT | `X-26`, `X-44` |
| T-23 | `EffectJournal` | CONCEPT | MOD-11 | PERSISTENCE | `X-07`, `X-14`, `X-32` |
| T-24 | `Budget` | RUST-STRUCT | MOD-04 | RESOURCE | `X-08`, `X-09`, `X-15`, `X-19`, `X-44`, `X-69` |
| T-25 | `Consumable` | RUST-STRUCT | MOD-04 | RESOURCE | `X-08`, `X-12`, `X-16`, `X-18`, `X-19`, `X-44` |
| T-26 | `Reserved` | RUST-STRUCT | MOD-04 | RESOURCE | `X-07`, `X-09`, `X-10`, `X-16`, `X-19`, `X-21`, `X-22`, `X-44`, `X-49`, `X-74` |
| T-27 | `Deadline` | RUST-NEWTYPE | MOD-04 | RESOURCE | `X-12`, `X-42`, `X-69` |
| T-28 | `LogicalTime` | RUST-NEWTYPE | MOD-04 | RESOURCE | `X-42` |
| T-29 | `CostModel` | RUST-TRAIT | MOD-04 | RESOURCE | `X-19`, `X-44` |
| T-30 | `Expr` | RUST-ENUM | MOD-01 | MACHINE | `X-03`, `X-30`, `X-35`, `X-39`, `X-70`, `X-79`, `X-85`, `X-86` |
| T-31 | `Value` | RUST-ENUM | MOD-01 | MACHINE | `X-28`, `X-33`, `X-45`, `X-54`, `X-55`, `X-56`, `X-70`, `X-72`, `X-75`, `X-76`, `X-85` |
| T-32 | `EvalState` | RUST-STRUCT | MOD-05 | MACHINE | `X-18`, `X-21`, `X-22`, `X-57`, `X-74`, `X-79`, `X-85`, `X-86` |
| T-33 | `Frame` | RUST-ENUM | MOD-05 | MACHINE | `X-33`, `X-37`, `X-79`, `X-85`, `X-86` |
| T-34 | `ActorId` | RUST-NEWTYPE | MOD-06 | CONCURRENCY | `X-24` |
| T-35 | `ActorStatus` | RUST-ENUM | MOD-06 | CONCURRENCY | `X-21`, `X-22`, `X-23`, `X-38`, `X-58`, `X-65`, `X-71`, `X-73`, `X-74`, `X-83` |
| T-36 | `RunState` | RUST-ENUM | MOD-07 | SCHEDULING | `X-21`, `X-23`, `X-58`, `X-73`, `X-75`, `X-83` |
| T-37 | `ActorState` | RUST-STRUCT | MOD-06 | CONCURRENCY | `X-11`, `X-14`, `X-18`, `X-74`, `X-76`, `X-83` |
| T-38 | `GlobalState` | RUST-STRUCT | MOD-05 | MACHINE | `X-18`, `X-46`, `X-83` |
| T-39 | `Mailbox` | CONCEPT | MOD-06 | CONCURRENCY | `X-45`, `X-76`, `X-83` |
| T-40 | `RunnableQueue` | CONCEPT | MOD-07 | SCHEDULING | `X-83` |
| T-41 | `HostPolicy` | RUST-TRAIT | MOD-09 | HOST | `X-20`, `X-38`, `X-58`, `X-59`, `X-67` |
| T-42 | `ReplayHost` | RUST-STRUCT | MOD-09 | HOST | `X-43`, `X-67`, `X-81`, `X-84` |
| T-43 | `LiveHost` | RUST-STRUCT | MOD-09 | HOST | — |
| T-44 | `HostExecutor` | RUST-TRAIT | MOD-09 | HOST | `X-67` |
| T-45 | `WAL` | CONCEPT | MOD-11 | PERSISTENCE | `X-13`, `X-14`, `X-17`, `X-31`, `X-32`, `X-47`, `X-54`, `X-57`, `X-61`, `X-71`, `X-80` |
| T-46 | `WalFrame` | RUST-STRUCT | MOD-11 | PERSISTENCE | `X-31`, `X-47`, `X-50`, `X-80`, `X-84` |
| T-47 | `WalRecord` | RUST-ENUM | MOD-11 | PERSISTENCE | `X-07`, `X-24`, `X-31`, `X-32`, `X-33`, `X-47`, `X-61`, `X-71`, `X-72`, `X-80`, `X-84` |
| T-48 | `Snapshot` | CONCEPT | MOD-11 | PERSISTENCE | `X-10`, `X-33`, `X-45`, `X-51`, `X-83`, `X-85` |
| T-49 | `EventLog` | RUST-STRUCT | MOD-11 | PERSISTENCE | `X-13`, `X-31`, `X-47`, `X-80` |
| T-50 | `Indeterminate` | STATE | MOD-12 | RECOVERY | — |
| T-51 | `ReconciliationOutcome` | RUST-ENUM | MOD-12 | RECOVERY | `X-61` |
| T-52 | `RecoveryFault` | RUST-STRUCT | MOD-12 | RECOVERY | `X-12`, `X-13`, `X-32`, `X-58`, `X-67` |
| T-53 | `Supervisor` | COMPONENT | MOD-12 | RECOVERY | — |
| T-54 | `Observation (planner-facing)` | RUST-STRUCT | MOD-13 | AGENT | `X-06`, `X-29` |
| T-55 | `PlannerAccepted` | RUST-STRUCT | MOD-13 | AGENT | `X-62` |
| T-56 | `LLMOutput` | MATH-SYMBOL | MOD-13 | AGENT | `X-69` |
| T-57 | `Observation (differential)` | RUST-STRUCT | MOD-15 | VERIFICATION | `X-06`, `X-29` |
| T-58 | `ReferenceModel` | COMPONENT | MOD-14 | VERIFICATION | `X-06`, `X-48`, `X-60`, `X-78`, `X-79`, `X-84`, `X-85` |
| T-59 | `FirstDivergence` | CONCEPT | MOD-15 | VERIFICATION | — |
| T-60 | `Mutation` | CONCEPT | MOD-16 | VERIFICATION | `X-49` |
| T-61 | `MutationKillRate` | MATH-PREDICATE | MOD-16 | VERIFICATION | — |
| T-62 | `CanonicalEnvelope` | PROTOCOL-FORMAT | MOD-10 | PERSISTENCE | `X-24`, `X-45`, `X-50`, `X-51`, `X-54`, `X-55`, `X-56`, `X-72`, `X-76`, `X-80` |
| T-63 | `CanonicalPayload` | RUST-TRAIT | MOD-10 | PERSISTENCE | `X-50`, `X-51`, `X-54`, `X-55`, `X-56`, `X-72` |
| T-64 | `Specification` | CONCEPT | MOD-17 | CLAIM | `X-52`, `X-53`, `X-60`, `X-63` |
| T-65 | `Implementation` | CONCEPT | MOD-17 | CLAIM | `X-48`, `X-52`, `X-53`, `X-63` |
| T-66 | `Verification` | CONCEPT | MOD-17 | CLAIM | `X-52` |
| T-67 | `Proof` | CONCEPT | MOD-17 | CLAIM | `X-52` |
| T-68 | `EvidenceStatus` | CLAIM-STATUS | MOD-17 | CLAIM | `X-52`, `X-53`, `X-63` |
| T-69 | `Frozen` | CONCEPT | MOD-17 | CLAIM | `X-52`, `X-63` |
| T-70 | `Fault` | RUST-ENUM | MOD-01 | MACHINE | `X-23`, `X-38`, `X-58`, `X-59`, `X-64`, `X-65`, `X-66`, `X-67`, `X-68`, `X-69`, `X-71`, `X-73`, `X-81` |
| T-71 | `GlobalFault` | RUST-ENUM | MOD-05 | MACHINE | `X-58` |
| T-72 | `CapabilityError` | RUST-ENUM | MOD-03 | AUTHORITY | `X-38`, `X-59`, `X-66`, `X-68` |
| T-73 | `MarshalFault` | RUST-ENUM | MOD-06 | CONCURRENCY | `X-65`, `X-75`, `X-76` |
| T-74 | `HostFault` | RUST-ENUM | MOD-09 | HOST | `X-58`, `X-59`, `X-67`, `X-68` |
| T-75 | `MachineEvent` | RUST-ENUM | MOD-05 | MACHINE | `X-71` |
| T-76 | `CanonicalError` | RUST-ENUM | MOD-10 | PERSISTENCE | `X-72`, `X-75` |
| T-77 | `StepResult` | RUST-ENUM | MOD-05 | MACHINE | `X-73`, `X-74` |
| T-78 | `ControlFrame` | RUST-ENUM | MOD-05 | MACHINE | `X-75` |
| T-79 | `MarshalledValue` | RUST-NEWTYPE | MOD-06 | CONCURRENCY | `X-76`, `X-83` |
| T-80 | `RefState` | RUST-STRUCT | MOD-14 | VERIFICATION | `X-78`, `X-79`, `X-84`, `X-86` |
| T-81 | `RefAuthority` | RUST-STRUCT | MOD-14 | AUTHORITY | `X-77`, `X-78`, `X-79`, `X-84` |
| T-82 | `SchedulerTrace` | UNDECLARED-TYPE | MOD-07 | SCHEDULING | — |
| T-83 | `HostTrace` | UNDECLARED-TYPE | MOD-09 | HOST | `X-87` |
| T-84 | `InitialState` | UNDECLARED-TYPE | MOD-01 | MACHINE | `X-87` |
| T-85 | `UniqueMachineTrace` | UNDECLARED-TYPE | MOD-01 | MACHINE | `X-87` |
| T-86 | `Lifetime` | RUST-STRUCT | MOD-03 | AUTHORITY | — |

## 5. Collision register status (carried, not resolved)

- **87** collisions filed in `term/02-collisions.md` (severities: {'BLOCKING': 4, 'MAJOR': 63, 'MINOR': 19, 'INFO': 1}); 4 are BLOCKING (`X-01`, `X-50`, `X-54`, `X-67`). FINAL1 carries them all into §29/`final/09`; it resolved none (the one prohibited resolution — renaming a frozen API/type/symbol/field — is also prohibited by inheritance).
- Terminology-layer corrections already applied by the cleaned set (X-39…X-87 lineage, the withdrawn claims at C-08/X-59 and X-64, the struck U-15/AMB-15 wording) are preserved quoted-not-deleted where they appear in transcribed rows.
