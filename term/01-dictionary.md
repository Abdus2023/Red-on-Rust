<!-- GENERATED FILE — DO NOT EDIT BY HAND. -->
<!-- Source of truth: `term/_terms.py`.  Regenerate: `python3 term/_dict.py --write`. -->
<!-- Every line citation below is re-grepped against `Red-on-Rust.md` by `python3 term/_check.py`. -->

# 01 — Canonical Terminology Dictionary

78 canonical terms. Each entry states the seven fields the normalization request requires — **CANONICAL_TERM**, **FORBIDDEN_VARIANTS**, **DEFINITION**, **TYPE**, **OWNER**, **FIRST_DEFINITION**, **DEPENDENTS** — plus the frozen shape, any superseded declarations, the obligations that use the term, and the collisions it participates in.

**Hard constraint honoured throughout:** no API, type, mathematical symbol or protocol field is renamed anywhere in this dictionary. Where the frozen source uses two names for one thing, or one name for two things, both are recorded verbatim and the conflict is filed in `02-collisions.md`; the canonical term is the one an author must *use*, never a new identifier to *introduce*. Names the source froze are listed under **PROTECTED (do not rename)**.

## Index
| ID | CANONICAL_TERM | TYPE | DOMAIN | OWNER | FIRST_DEFINITION | Collisions |
|---|---|---|---|---|---|---|
| [T-01](#t-01-block) | `Block` ★ | RUST-STRUCT | PLAN-PIPELINE | MOD-02 | `L855` | 5 |
| [T-02](#t-02-planproposal) | `PlanProposal` ★ | RUST-STRUCT | PLAN-PIPELINE | MOD-13 | `L27175` | 6 |
| [T-03](#t-03-parsedblock) | `ParsedBlock` ★ | RUST-STRUCT | PLAN-PIPELINE | MOD-02 | `L864` | 5 |
| [T-04](#t-04-validatedplan) | `ValidatedPlan` ★ | RUST-STRUCT | PLAN-PIPELINE | MOD-02 | `L865` | 7 |
| [T-05](#t-05-capabilitycheckedplan) | `CapabilityCheckedPlan` ★ | RUST-STRUCT | PLAN-PIPELINE | MOD-02 | `L866` | 3 |
| [T-06](#t-06-executableplan) | `ExecutablePlan` ★ | RUST-STRUCT | PLAN-PIPELINE | MOD-02 | `L869` | 8 |
| [T-07](#t-07-normalizedast) | `NormalizedAST` | UNDECLARED-TYPE | PLAN-PIPELINE | MOD-02 | `L864` | 4 |
| [T-08](#t-08-planir) | `PlanIR` | UNDECLARED-TYPE | PLAN-PIPELINE | MOD-02 | `L865` | 9 |
| [T-09](#t-09-capref) | `CapRef` ★ | RUST-STRUCT | AUTHORITY | MOD-03 | `L915` | 8 |
| [T-10](#t-10-authority) | `Authority` ★ | MATH-SYMBOL | AUTHORITY | MOD-03 | `L488` | 13 |
| [T-11](#t-11-authoritynode) | `AuthorityNode` | RUST-STRUCT | AUTHORITY | MOD-03 | `L39373` | 1 |
| [T-12](#t-12-constraint) | `Constraint` | RUST-STRUCT | AUTHORITY | MOD-03 | `L6536` | 4 |
| [T-13](#t-13-capabilitykernel) | `CapabilityKernel` | COMPONENT | AUTHORITY | MOD-03 | `L6680` | 6 |
| [T-14](#t-14-capabilitycontext) | `CapabilityContext` | RUST-STRUCT | AUTHORITY | MOD-06 | `L25548` | 2 |
| [T-15](#t-15-delegatedcapability) | `DelegatedCapability` | RUST-VARIANT | AUTHORITY | MOD-06 | `L25989` | 2 |
| [T-16](#t-16-effect) | `Effect` ★ | RUST-STRUCT | EFFECT | MOD-08 | `L1166` | 9 |
| [T-17](#t-17-effectrequest) | `EffectRequest` ★ | RUST-STRUCT | EFFECT | MOD-08 | `L1447` | 6 |
| [T-18](#t-18-effectissued) | `EffectIssued` ★ | STATE-VS-RECORD | EFFECT | MOD-11 | `L1377` | 4 |
| [T-19](#t-19-effectreceipt) | `EffectReceipt` ★ | RUST-STRUCT | EFFECT | MOD-08 | `L1454` | 3 |
| [T-20](#t-20-effectid) | `EffectId` ★ | RUST-NEWTYPE | EFFECT | MOD-08 | `L9128` | 5 |
| [T-21](#t-21-effectdigest) | `EffectDigest` | RUST-NEWTYPE | EFFECT | MOD-08 | `L9343` | 4 |
| [T-22](#t-22-effectcost) | `EffectCost` | RUST-STRUCT | EFFECT | MOD-08 | `L21390` | 2 |
| [T-23](#t-23-effectjournal) | `EffectJournal` ★ | CONCEPT | PERSISTENCE | MOD-11 | `L26134` | 3 |
| [T-24](#t-24-budget) | `Budget` ★ | RUST-STRUCT | RESOURCE | MOD-04 | `L1788` | 6 |
| [T-25](#t-25-consumable) | `Consumable` ★ | RUST-STRUCT | RESOURCE | MOD-04 | `L7130` | 6 |
| [T-26](#t-26-reserved) | `Reserved` ★ | RUST-STRUCT | RESOURCE | MOD-04 | `L7131` | 10 |
| [T-27](#t-27-deadline) | `Deadline` | RUST-NEWTYPE | RESOURCE | MOD-04 | `L6748` | 3 |
| [T-28](#t-28-logicaltime) | `LogicalTime` ★ | RUST-NEWTYPE | RESOURCE | MOD-04 | `L6437` | 1 |
| [T-29](#t-29-costmodel) | `CostModel` | RUST-TRAIT | RESOURCE | MOD-04 | `L10168` | 2 |
| [T-30](#t-30-expr) | `Expr` | RUST-ENUM | MACHINE | MOD-01 | `L12145` | 5 |
| [T-31](#t-31-value) | `Value` | RUST-ENUM | MACHINE | MOD-01 | `L12283` | 9 |
| [T-32](#t-32-evalstate) | `EvalState` | RUST-STRUCT | MACHINE | MOD-05 | `L12655` | 5 |
| [T-33](#t-33-frame) | `Frame` | RUST-ENUM | MACHINE | MOD-05 | `L12453` | 2 |
| [T-34](#t-34-actorid) | `ActorId` ★ | RUST-NEWTYPE | CONCURRENCY | MOD-06 | `L9127` | 1 |
| [T-35](#t-35-actorstatus) | `ActorStatus` ★ | RUST-ENUM | CONCURRENCY | MOD-06 | `L9411` | 9 |
| [T-36](#t-36-runstate) | `RunState` | RUST-ENUM | SCHEDULING | MOD-07 | `L24299` | 5 |
| [T-37](#t-37-actorstate) | `ActorState` | RUST-STRUCT | CONCURRENCY | MOD-06 | `L8111` | 4 |
| [T-38](#t-38-globalstate) | `GlobalState` | RUST-STRUCT | MACHINE | MOD-05 | `L24156` | 2 |
| [T-39](#t-39-mailbox) | `Mailbox` | CONCEPT | CONCURRENCY | MOD-06 | `L8666` | 1 |
| [T-40](#t-40-runnablequeue) | `RunnableQueue` | CONCEPT | SCHEDULING | MOD-07 | `L25538` | 0 |
| [T-41](#t-41-hostpolicy) | `HostPolicy` ★ | RUST-TRAIT | HOST | MOD-09 | `L10163` | 5 |
| [T-42](#t-42-replayhost) | `ReplayHost` ★ | RUST-STRUCT | HOST | MOD-09 | `L1234` | 2 |
| [T-43](#t-43-livehost) | `LiveHost` | RUST-STRUCT | HOST | MOD-09 | `L1191` | 0 |
| [T-44](#t-44-hostexecutor) | `HostExecutor` | RUST-TRAIT | HOST | MOD-09 | `L1187` | 1 |
| [T-45](#t-45-wal) | `WAL` ★ | CONCEPT | PERSISTENCE | MOD-11 | `L27716` | 10 |
| [T-46](#t-46-walframe) | `WalFrame` | RUST-STRUCT | PERSISTENCE | MOD-11 | `L34237` | 3 |
| [T-47](#t-47-walrecord) | `WalRecord` | RUST-ENUM | PERSISTENCE | MOD-11 | `L27724` | 9 |
| [T-48](#t-48-snapshot) | `Snapshot` ★ | CONCEPT | PERSISTENCE | MOD-11 | `L26132` | 4 |
| [T-49](#t-49-eventlog) | `EventLog` | RUST-STRUCT | PERSISTENCE | MOD-11 | `L1086` | 3 |
| [T-50](#t-50-indeterminate) | `Indeterminate` | STATE | RECOVERY | MOD-12 | `L26576` | 0 |
| [T-51](#t-51-reconciliationoutcome) | `ReconciliationOutcome` | RUST-ENUM | RECOVERY | MOD-12 | `L26244` | 1 |
| [T-52](#t-52-recoveryfault) | `RecoveryFault` | RUST-STRUCT | RECOVERY | MOD-12 | `L26506` | 5 |
| [T-53](#t-53-supervisor) | `Supervisor` | COMPONENT | RECOVERY | MOD-12 | `L3136` | 0 |
| [T-54](#t-54-observation-planner-facing) | `Observation (planner-facing)` ★ | RUST-STRUCT | AGENT | MOD-13 | `L27156` | 2 |
| [T-55](#t-55-planneraccepted) | `PlannerAccepted` | RUST-STRUCT | AGENT | MOD-13 | `L27411` | 1 |
| [T-56](#t-56-llmoutput) | `LLMOutput` | MATH-SYMBOL | AGENT | MOD-13 | `L27253` | 1 |
| [T-57](#t-57-observation-differential) | `Observation (differential)` ★ | RUST-STRUCT | VERIFICATION | MOD-15 | `L36170` | 2 |
| [T-58](#t-58-referencemodel) | `ReferenceModel` | COMPONENT | VERIFICATION | MOD-14 | `L11436` | 3 |
| [T-59](#t-59-firstdivergence) | `FirstDivergence` | CONCEPT | VERIFICATION | MOD-15 | `L36655` | 0 |
| [T-60](#t-60-mutation) | `Mutation` | CONCEPT | VERIFICATION | MOD-16 | `L37187` | 1 |
| [T-61](#t-61-mutationkillrate) | `MutationKillRate` | MATH-PREDICATE | VERIFICATION | MOD-16 | `L38506` | 0 |
| [T-62](#t-62-canonicalenvelope) | `CanonicalEnvelope` | PROTOCOL-FORMAT | PERSISTENCE | MOD-10 | `L28298` | 8 |
| [T-63](#t-63-canonicalpayload) | `CanonicalPayload` | RUST-TRAIT | PERSISTENCE | MOD-10 | `L27685` | 6 |
| [T-64](#t-64-specification) | `Specification` | CONCEPT | CLAIM | MOD-17 | `L38936` | 4 |
| [T-65](#t-65-implementation) | `Implementation` | CONCEPT | CLAIM | MOD-17 | `L38939` | 4 |
| [T-66](#t-66-verification) | `Verification` | CONCEPT | CLAIM | MOD-17 | `L38938` | 1 |
| [T-67](#t-67-proof) | `Proof` | CONCEPT | CLAIM | MOD-17 | `L28263` | 1 |
| [T-68](#t-68-evidencestatus) | `EvidenceStatus` | CLAIM-STATUS | CLAIM | MOD-17 | `spec/00-overview.md:L25` | 3 |
| [T-69](#t-69-frozen) | `Frozen` | CONCEPT | CLAIM | MOD-17 | `L38935` | 2 |
| [T-70](#t-70-fault) | `Fault` | RUST-ENUM | MACHINE | MOD-01 | `L1009` | 12 |
| [T-71](#t-71-globalfault) | `GlobalFault` | RUST-ENUM | MACHINE | MOD-05 | `L25576` | 1 |
| [T-72](#t-72-capabilityerror) | `CapabilityError` | RUST-ENUM | AUTHORITY | MOD-03 | `L9736` | 4 |
| [T-73](#t-73-marshalfault) | `MarshalFault` | RUST-ENUM | CONCURRENCY | MOD-06 | `L10846` | 2 |
| [T-74](#t-74-hostfault) | `HostFault` | RUST-ENUM | HOST | MOD-09 | `L10820` | 4 |
| [T-75](#t-75-machineevent) | `MachineEvent` | RUST-ENUM | MACHINE | MOD-05 | `L14697` | 1 |
| [T-76](#t-76-canonicalerror) | `CanonicalError` | RUST-ENUM | PERSISTENCE | MOD-10 | `L29188` | 2 |
| [T-77](#t-77-stepresult) | `StepResult` | RUST-ENUM | MACHINE | MOD-05 | `L1006` | 2 |
| [T-78](#t-78-controlframe) | `ControlFrame` | RUST-ENUM | MACHINE | MOD-05 | `L985` | 1 |

★ = one of the 26 terms the normalization request explicitly requires.

---

## PLAN-PIPELINE — Untrusted input to machine input
Owning module: **MOD-02**.

### T-01 — `Block`
*Required term.*

- **CANONICAL_TERM:** `Block`
- **TYPE:** RUST-STRUCT — a Rust `struct` declaration (nominal type)
- **OWNER:** MOD-02 (`ror-compiler (consumer); produced by ror-agent`)
- **DEFINITION:** Homoiconic untrusted program data at the language surface: the form the LLM/planner emits and the only thing an untrusted producer may supply. `Block` carries no authority, no validation verdict, and no resource bound. It is never a security boundary (R-TRUST-01) and has no path into `step()` (R-ARCH-03).
- **FIRST_DEFINITION:** `L855`, turn [3] — `pub struct Block(pub Vec<Value>);`
- **FROZEN_AT:** `L13484`, turn [21] — `pub struct Block {`
- **DEPENDENTS:** T-02 `PlanProposal`, T-03 `ParsedBlock`, T-06 `ExecutablePlan`, T-30 `Expr`
- **FORBIDDEN_VARIANTS:**
    - `program` — as a synonym for Block
    - `source` — as a synonym for Block
    - `raw plan`
    - `plan` — the obsolete turn-[2] primitive; see X-02
- **PROTECTED (do not rename):**
    - `Block` — frozen Rust type name; also the trust-table row name (L41828)
    - `B` — mathematical symbol for a block in turn [1] (L132); superseded by the typed name but never renamed in that text
- **FROZEN SHAPE:** `pub struct Block { pub forms: Vec<Form> }   // L13484, turn [21]`
- **SUPERSEDES (recorded, not deleted):**
    - `pub struct Block(pub Vec<Value>);  // L855, turn [3]`
- **OBLIGATIONS:** `R-COMPILE-01`, `R-COMPILE-02`, `R-TRUST-01`, `R-ARCH-03`
- **SECTIONS:** `S-06`
- **COLLISIONS:** [X-02](02-collisions.md#x-02), [X-15](02-collisions.md#x-15), [X-28](02-collisions.md#x-28), [X-29](02-collisions.md#x-29), [X-62](02-collisions.md#x-62)
- **LAWS:** [N-01](03-laws.md#n-01)
- **NOTE:** Two incompatible declarations exist (X-28) and the later one is typed over `Form`, which the source never declares (X-29 family). Neither form is renamed here; both are recorded and the difference is reported.

### T-02 — `PlanProposal`
*Required term.*

- **CANONICAL_TERM:** `PlanProposal`
- **TYPE:** RUST-STRUCT — a Rust `struct` declaration (nominal type)
- **OWNER:** MOD-13 (`ror-agent`)
- **DEFINITION:** The complete output of the untrusted LLM/planner: `{ observation_sequence, block, planner_metadata }`. `LLMOutput ∈ Data`: a proposal is data to be validated, never authority, never a plan, and never machine input. A proposal whose `observation_sequence` is behind the current sequence is `StalePlan` and is rejected without state mutation.
- **FIRST_DEFINITION:** `L27175`, turn [33] — `pub struct PlanProposal {`
- **DEPENDENTS:** T-01 `Block`, T-55 `PlannerAccepted`, T-56 `LLMOutput`
- **FORBIDDEN_VARIANTS:**
    - `plan` — a PlanProposal is not a plan
    - `proposal plan`
    - `planner output plan`
    - `draft ExecutablePlan`
- **PROTECTED (do not rename):**
    - `PlanProposal` — frozen Rust type name (single declaration; no variant forms)
    - `observation_sequence` — frozen protocol field
    - `planner_metadata` — frozen protocol field (content undefined, U-13)
    - `StalePlan` — frozen fault/rejection name
- **FROZEN SHAPE:** `pub struct PlanProposal { ... }   // L27175, turn [33]`
- **OBLIGATIONS:** `R-PLANNER-01`, `R-PLANNER-03`, `R-PLANNER-04`, `R-CORE-01`
- **SECTIONS:** `S-05`
- **COLLISIONS:** [X-04](02-collisions.md#x-04), [X-06](02-collisions.md#x-06), [X-34](02-collisions.md#x-34), [X-62](02-collisions.md#x-62), [X-64](02-collisions.md#x-64), [X-69](02-collisions.md#x-69)
- **LAWS:** [N-02](03-laws.md#n-02)
- **NOTE:** Distinct from `PlannerAccepted` (T-55), which is the *recorded* accepted proposal used for replay, and from `Plan` (obsolete, turn [2]).

### T-03 — `ParsedBlock`
*Required term.*

- **CANONICAL_TERM:** `ParsedBlock`
- **TYPE:** RUST-STRUCT — a Rust `struct` declaration (nominal type)
- **OWNER:** MOD-02 (`ror-compiler`)
- **DEFINITION:** Compiler stage 1 artifact: a `Block` whose syntax has been validated against the dialect grammar and normalized — `{ ast: NormalizedAST }`. It carries no effect set, no capability verdict, and no resource bound. Judgment 11 of turn [3]: `Γ ⊢_syntax B ⇒ P_parsed`.
- **FIRST_DEFINITION:** `L864`, turn [3] — `pub struct ParsedBlock { ast: NormalizedAST }`
- **DEPENDENTS:** T-01 `Block`, T-04 `ValidatedPlan`, T-07 `NormalizedAST`
- **FORBIDDEN_VARIANTS:**
    - `parsed program`
    - `syntax tree` — as a synonym for ParsedBlock
- **PROTECTED (do not rename):**
    - `ParsedBlock` — frozen Rust type name; declared private to `mod compiler`
    - `ast` — frozen field name
    - `P_parsed` — the turn-[3] judgment's symbol for this stage
- **FROZEN SHAPE:** `pub struct ParsedBlock { ast: NormalizedAST }   // L864, turn [3]`
- **OBLIGATIONS:** `R-COMPILE-02`, `R-COMPILE-03`, `R-COMPILE-05`
- **SECTIONS:** `S-06`
- **COLLISIONS:** [X-01](02-collisions.md#x-01), [X-02](02-collisions.md#x-02), [X-28](02-collisions.md#x-28), [X-29](02-collisions.md#x-29), [X-41](02-collisions.md#x-41)
- **LAWS:** [N-10](03-laws.md#n-10)
- **NOTE:** Declared once (L864). Later pipeline renderings (L13595, L39267) keep the stage; L39271 replaces it with `NormalizedAST` as the stage name (X-02). Its field type `NormalizedAST` is never declared (X-29).

### T-04 — `ValidatedPlan`
*Required term.*

- **CANONICAL_TERM:** `ValidatedPlan`
- **TYPE:** RUST-STRUCT — a Rust `struct` declaration (nominal type)
- **OWNER:** MOD-02 (`ror-compiler`)
- **DEFINITION:** Compiler stage 2 artifact: a `ParsedBlock` annotated with its statically extracted effect set — `{ ir: PlanIR, effects: EffectSet }`. It has NOT been capability-checked and NOT been resource-bounded, so it is not machine input. Judgment 12 of turn [3]: `P_parsed ⊢_effects F`.
- **FIRST_DEFINITION:** `L865`, turn [3] — `pub struct ValidatedPlan { ir: PlanIR, effects: EffectSet }`
- **FROZEN_AT:** `L13488`, turn [21] — `pub struct ValidatedPlan {`
- **DEPENDENTS:** T-03 `ParsedBlock`, T-05 `CapabilityCheckedPlan`, T-08 `PlanIR`
- **FORBIDDEN_VARIANTS:**
    - `ExecutablePlan` — a ValidatedPlan is pre-capability-analysis
    - `validated executable plan`
    - `approved plan`
    - `safe plan`
- **PROTECTED (do not rename):**
    - `ValidatedPlan` — frozen Rust type name AND a frozen mathematical predicate symbol — see X-01; neither use may be renamed
    - `ValidatedPlan(P)` — the first conjunct of the central external-effect theorem (L27494, L41338); a predicate over the plan P
    - `ir` — frozen field name
    - `effects` — frozen field name
    - `P_valid` — the turn-[3] judgment's symbol for this stage
- **FROZEN SHAPE:** `pub struct ValidatedPlan { ir: PlanIR, effects: EffectSet }   // L865, L13488`
- **OBLIGATIONS:** `R-COMPILE-02`, `R-COMPILE-03`, `R-CORE-02`
- **SECTIONS:** `S-06`, `S-02`
- **COLLISIONS:** [X-01](02-collisions.md#x-01), [X-02](02-collisions.md#x-02), [X-04](02-collisions.md#x-04), [X-34](02-collisions.md#x-34), [X-40](02-collisions.md#x-40), [X-41](02-collisions.md#x-41), [X-64](02-collisions.md#x-64)
- **LAWS:** [N-10](03-laws.md#n-10), [N-11](03-laws.md#n-11)
- **NOTE:** HOMONYM (X-01): `ValidatedPlan` denotes (a) this struct — an intermediate stage that has not been capability-checked — and (b) the predicate `ValidatedPlan(P)` in the central theorem, whose argument P is the plan that enters the machine (i.e. an `ExecutablePlan`). spec/05 recorded (b) as an *alias* of `ExecutablePlan`; that is the defect reported as X-40. Both uses are frozen identifiers and neither is renamed here.

### T-05 — `CapabilityCheckedPlan`
*Required term.*

- **CANONICAL_TERM:** `CapabilityCheckedPlan`
- **TYPE:** RUST-STRUCT — a Rust `struct` declaration (nominal type)
- **OWNER:** MOD-02 (`ror-compiler`)
- **DEFINITION:** Compiler stage 3 artifact: a `ValidatedPlan` for which the required authority has been computed and checked against ambient authority — `{ ir: PlanIR, required_caps: CapSet }`, with `κ_req ⪯ κ_ambient`. It has NOT been resource-bounded, so it is still not machine input. Judgment 13 of turn [3].
- **FIRST_DEFINITION:** `L866`, turn [3] — `pub struct CapabilityCheckedPlan { ir: PlanIR, required_caps: CapSet }`
- **DEPENDENTS:** T-04 `ValidatedPlan`, T-06 `ExecutablePlan`, T-09 `CapRef`
- **FORBIDDEN_VARIANTS:**
    - `authorized plan` — capability checking is static; runtime authorization is the kernel's `Authorized` decision
    - `ExecutablePlan`
    - `capability plan`
- **PROTECTED (do not rename):**
    - `CapabilityCheckedPlan` — frozen Rust type name; declared private to `mod compiler`
    - `required_caps` — frozen field name
    - `CapSet` — the field's type name, used only here
    - `P_cap` — the turn-[3] judgment's symbol for this stage
- **FROZEN SHAPE:** `pub struct CapabilityCheckedPlan { ir: PlanIR, required_caps: CapSet }   // L866`
- **OBLIGATIONS:** `R-COMPILE-03`, `R-COMPILE-05`, `R-CAP-04`
- **SECTIONS:** `S-06`
- **COLLISIONS:** [X-01](02-collisions.md#x-01), [X-02](02-collisions.md#x-02), [X-40](02-collisions.md#x-40)
- **LAWS:** [N-11](03-laws.md#n-11), [N-12](03-laws.md#n-12)
- **NOTE:** Declared once (L866) and named in two of the three pipeline renderings (L567, L9106); omitted from the third (L39265-39280) and from the turn-[21] rendering (X-02). Static capability *analysis* is not the runtime `Authorized(A_c, E, t)` gate (N-03).

### T-06 — `ExecutablePlan`
*Required term.*

- **CANONICAL_TERM:** `ExecutablePlan`
- **TYPE:** RUST-STRUCT — a Rust `struct` declaration (nominal type)
- **OWNER:** MOD-02 (`ror-compiler`)
- **DEFINITION:** Compiler stage 4 artifact and the ONLY legal input to the machine: an immutable, resource-bounded plan whose constructors are private to the compiler (`_sealed: Sealed`), so no component outside `ror-compiler` can forge one. `Block ≠ ExecutablePlan`; the transition requires the whole parse → validate → capability → resource pipeline.
- **FIRST_DEFINITION:** `L869`, turn [3] — `pub struct ExecutablePlan {`
- **FROZEN_AT:** `L14103`, turn [22] — `pub struct ExecutablePlan {`
- **DEPENDENTS:** T-05 `CapabilityCheckedPlan`, T-30 `Expr`, T-32 `EvalState`, T-37 `ActorState`
- **FORBIDDEN_VARIANTS:**
    - `Block` — as a synonym
    - `compiled block`
    - `plan` — unqualified
    - `validated plan` — unqualified — see X-01
    - `runnable program`
- **PROTECTED (do not rename):**
    - `ExecutablePlan` — frozen Rust type name
    - `_sealed` — frozen private marker field; the constructor-privacy mechanism
    - `Sealed` — frozen zero-sized private type
    - `bounds` — frozen field name
    - `expr` — frozen payload field name in the turn-[21]/[22] declarations
    - `ir` — frozen payload field name in the turn-[3]/[58] declarations — see X-03; not renamed
    - `P_exec` — the turn-[3] judgment's symbol for this stage
- **FROZEN SHAPE:** `pub struct ExecutablePlan { pub(crate) expr: Expr, pub(crate) bounds: ResourceBounds, _sealed: Sealed }   // L14103, L14487`
- **SUPERSEDES (recorded, not deleted):**
    - `pub struct ExecutablePlan { ir: PlanIR, bounds: ResourceBounds, _sealed: Sealed }   // L869 (turn [3]) and L39972 (turn [58]) — payload field `ir: PlanIR``
- **OBLIGATIONS:** `R-COMPILE-01`, `R-COMPILE-04`, `R-COMPILE-05`, `R-ARCH-03`, `R-ORDER-03`
- **SECTIONS:** `S-06`, `S-04`
- **COLLISIONS:** [X-01](02-collisions.md#x-01), [X-02](02-collisions.md#x-02), [X-03](02-collisions.md#x-03), [X-30](02-collisions.md#x-30), [X-34](02-collisions.md#x-34), [X-40](02-collisions.md#x-40), [X-41](02-collisions.md#x-41), [X-62](02-collisions.md#x-62)
- **LAWS:** [N-01](03-laws.md#n-01), [N-02](03-laws.md#n-02), [N-12](03-laws.md#n-12)
- **NOTE:** FIVE declarations with two payload field names (`expr: Expr` at L13493, L14103, L14487; `ir: PlanIR` at L869 and L39972). X-03 reports this. The turn-[58] form reverts to `ir: PlanIR`, whose type is never declared and whose variants are superseded (X-30), so the dictionary records the collision and requires an explicit decision rather than picking a winner.

### T-07 — `NormalizedAST`

- **CANONICAL_TERM:** `NormalizedAST`
- **TYPE:** UNDECLARED-TYPE — a name used as a type in frozen declarations but never declared anywhere
- **OWNER:** MOD-02 (`ror-compiler`)
- **DEFINITION:** The normalized syntax artifact carried by `ParsedBlock.ast`. Used as a field type at L864 and as a pipeline stage name at L39271; the source never declares it, never gives it a variant set, and never states its relationship to the frozen `Expr` AST.
- **FIRST_DEFINITION:** `L864`, turn [3] — `pub struct ParsedBlock { ast: NormalizedAST }`
- **DEPENDENTS:** T-03 `ParsedBlock`, T-30 `Expr`
- **FORBIDDEN_VARIANTS:**
    - `normalized expression`
    - `canonical AST` — as a synonym
- **PROTECTED (do not rename):**
    - `NormalizedAST` — name used in frozen source text; not renamed
- **OBLIGATIONS:** `R-COMPILE-02`, `R-COMPILE-03`
- **SECTIONS:** `S-06`
- **COLLISIONS:** [X-02](02-collisions.md#x-02), [X-29](02-collisions.md#x-29), [X-40](02-collisions.md#x-40), [X-41](02-collisions.md#x-41)
- **NOTE:** Exactly two occurrences in 42,312 lines (L864, L39271). UNDEFINED-TYPE: this entry records the name and its usage, and reports the gap; it does not invent a declaration.

### T-08 — `PlanIR`

- **CANONICAL_TERM:** `PlanIR`
- **TYPE:** UNDECLARED-TYPE — a name used as a type in frozen declarations but never declared anywhere
- **OWNER:** MOD-02 (`ror-compiler`)
- **DEFINITION:** The intermediate representation carried by `ValidatedPlan.ir`, `CapabilityCheckedPlan.ir`, and (in two of five declarations) `ExecutablePlan.ir`. Used with variants `PlanIR::Value`, `PlanIR::Invoke`, `PlanIR::Spawn { plan, trust_level }` at L1037-L1051, but never declared as an enum.
- **FIRST_DEFINITION:** `L865`, turn [3] — `pub struct ValidatedPlan { ir: PlanIR, effects: EffectSet }`
- **DEPENDENTS:** T-04 `ValidatedPlan`, T-05 `CapabilityCheckedPlan`, T-06 `ExecutablePlan`, T-30 `Expr`
- **FORBIDDEN_VARIANTS:**
    - `IR` — unqualified
    - `plan representation`
    - `lowered block`
- **PROTECTED (do not rename):**
    - `PlanIR` — name used in frozen source text; not renamed
    - `PlanIR::Invoke` — superseded variant name — the frozen AST constructor is `Expr::Request` (C-17); retained for traceability
    - `trust_level` — superseded field of `PlanIR::Spawn`; the frozen `Expr::Spawn` has no isolation field (U-05)
- **OBLIGATIONS:** `R-COMPILE-02`, `R-COMPILE-03`
- **SECTIONS:** `S-06`
- **COLLISIONS:** [X-02](02-collisions.md#x-02), [X-03](02-collisions.md#x-03), [X-16](02-collisions.md#x-16), [X-30](02-collisions.md#x-30), [X-34](02-collisions.md#x-34), [X-40](02-collisions.md#x-40), [X-41](02-collisions.md#x-41), [X-62](02-collisions.md#x-62), [X-75](02-collisions.md#x-75)
- **NOTE:** Two pipeline renderings place `PlanIR` AFTER `ValidatedPlan` as a distinct stage (L13603, L39275), while the frozen structs make it the *content* of `ValidatedPlan` (L865) — X-02. Its variant set uses `Invoke` and `trust_level`, both superseded (C-17, U-05) — X-30.

---

## AUTHORITY — Capability algebra, kernel, delegation
Owning module: **MOD-03**.

### T-09 — `CapRef`
*Required term.*

- **CANONICAL_TERM:** `CapRef`
- **TYPE:** RUST-STRUCT — a Rust `struct` declaration (nominal type)
- **OWNER:** MOD-03 (`ror-kernel`)
- **DEFINITION:** An opaque, generation-safe capability REFERENCE: `{ index: u32, generation: u32 }`, fields private, no public constructor from arbitrary integers. A `CapRef` is a name the machine can pass around and the evaluator can hold; it is NOT authority. The authority it denotes is `κ(c)` = `Authority(c)` = `A_c`, which is kernel-private. Ordinary marshalling rejects raw capabilities; authority crosses actor boundaries only by explicit delegation.
- **FIRST_DEFINITION:** `L915`, turn [3] — `pub struct CapRef(pub(crate) u64);`
- **FROZEN_AT:** `L9131`, turn [17] — `pub struct CapRef {`
- **DEPENDENTS:** T-10 `Authority`, T-11 `AuthorityNode`, T-12 `Constraint`, T-15 `DelegatedCapability`, T-17 `EffectRequest`
- **FORBIDDEN_VARIANTS:**
    - `capability` — unqualified — denotes the grant, not the reference
    - `capability token`
    - `authority handle`
    - `capability handle` — the obsolete v0.3 `handle`/`h` wording
- **PROTECTED (do not rename):**
    - `CapRef` — frozen Rust type name; also 15A standalone tag `0x30`
    - `index` — frozen field name
    - `generation` — frozen field name
    - `c` — frozen mathematical symbol for a CapRef (e.g. `Valid(c,t)`)
    - `Value::Capability` — frozen machine-value variant that *carries* a CapRef
- **FROZEN SHAPE:** `pub struct CapRef { index: u32, generation: u32 }   // L9131, turn [17]`
- **SUPERSEDES (recorded, not deleted):**
    - `pub struct CapRef(pub(crate) u64);   // L915, L3646, L5034, L5949`
- **OBLIGATIONS:** `R-CAP-01`, `R-CAP-05`, `R-KERN-03`, `R-MARSHAL-01`, `R-CORE-07`
- **SECTIONS:** `S-09`, `S-10`, `S-16`
- **COLLISIONS:** [X-05](02-collisions.md#x-05), [X-25](02-collisions.md#x-25), [X-26](02-collisions.md#x-26), [X-27](02-collisions.md#x-27), [X-36](02-collisions.md#x-36), [X-38](02-collisions.md#x-38), [X-59](02-collisions.md#x-59), [X-66](02-collisions.md#x-66)
- **LAWS:** [N-03](03-laws.md#n-03)
- **NOTE:** The single-`u64` form cannot express generational reuse safety and is superseded by the frozen `{index, generation}` form (X-25). N-03 (`CapRef ≠ Authority`) is the load-bearing distinction of the trust model.

### T-10 — `Authority`
*Required term.*

- **CANONICAL_TERM:** `Authority`
- **TYPE:** MATH-SYMBOL — a mathematical symbol in a frozen formula
- **OWNER:** MOD-03 (`ror-kernel`)
- **DEFINITION:** The operation-indexed grant set behind a capability: `A = { (o, A_o) | o ∈ O_granted }` with `A_o = ⟨S, Q, R, T⟩` (scope, parameter constraint, resource limit, lifetime). Ordered by `⪯` (`A_1 ⪯ A_2` = A_1 grants no more authority than A_2); derivation satisfies `derive(A,C) ⪯ A`. Authority is kernel-private: the evaluator sees only `CapRef`s and can never inspect it.
- **FIRST_DEFINITION:** `L488`, turn [2] — `struct Authority {`
- **FROZEN_AT:** `L6375`, turn [11] — `$$A_o = \langle S, Q, R, T \rangle$$`
- **DEPENDENTS:** T-09 `CapRef`, T-11 `AuthorityNode`, T-12 `Constraint`, T-13 `CapabilityKernel`
- **FORBIDDEN_VARIANTS:**
    - `CapRef` — as a synonym
    - `capability reference`
    - `permission set`
    - `rights`
    - `token`
- **PROTECTED (do not rename):**
    - `Authority` — frozen mathematical name AND a frozen Rust generic type name (`Authority<S,Q,R,L>`, L6501) — both retained
    - `A` — frozen mathematical symbol
    - `A_o` — frozen symbol for the per-operation authority
    - `A_c` — frozen symbol for `Authority(c)`, the authority behind CapRef c
    - `κ(c)` — frozen notation for the same object via the capability map
    - `Authority(c)` — frozen notation; `AuthOK(c,E,t) ⇔ Valid(c,t) ∧ Authorized(Authority(c),E,t)` (L7323)
    - `S` — the scope component symbol — collides with Slots and Snapshot (X-10)
    - `Q` — the parameter-constraint component symbol
    - `R` — the resource-limit component symbol — collides with Reserved (X-09)
    - `T` — the lifetime component symbol in the frozen math (L6375)
    - `L` — the lifetime type parameter in the frozen Rust sketch (L6501) — X-17
    - `O_granted` — frozen symbol for the granted operation set
    - `⪯` — frozen authority partial order
    - `⊓` — frozen meet operator used by `derive_op`
- **FROZEN SHAPE:** `A_o = ⟨S, Q, R, T⟩   // L6375, turn [11]
A = { (o, A_o) | o ∈ O_granted }   // L6378, turn [11]`
- **OBLIGATIONS:** `R-CAP-01`, `R-CAP-02`, `R-CAP-03`, `R-CORE-04`, `R-KERN-03`
- **SECTIONS:** `S-09`, `S-10`
- **COLLISIONS:** [X-05](02-collisions.md#x-05), [X-08](02-collisions.md#x-08), [X-09](02-collisions.md#x-09), [X-10](02-collisions.md#x-10), [X-11](02-collisions.md#x-11), [X-13](02-collisions.md#x-13), [X-17](02-collisions.md#x-17), [X-25](02-collisions.md#x-25), [X-36](02-collisions.md#x-36), [X-37](02-collisions.md#x-37), [X-38](02-collisions.md#x-38), [X-59](02-collisions.md#x-59), [X-70](02-collisions.md#x-70)
- **LAWS:** [N-03](03-laws.md#n-03), [N-09](03-laws.md#n-09), [N-25](03-laws.md#n-25), [N-28](03-laws.md#n-28)
- **NOTE:** The Rust sketch in the SAME turn parameterizes it as `Authority<S,Q,R,L>` with `lifetime: L` (L6497, L6501) while the frozen math writes `T` for that component (X-17). Both symbols are recorded; neither is renamed, because renaming a mathematical symbol would silently alter the frozen algebra. `Authority` is a concept/math object plus a generic Rust type; the kernel-private node is `AuthorityNode` (T-11).

### T-11 — `AuthorityNode`

- **CANONICAL_TERM:** `AuthorityNode`
- **TYPE:** RUST-STRUCT — a Rust `struct` declaration (nominal type)
- **OWNER:** MOD-03 (`ror-kernel`)
- **DEFINITION:** The kernel-private per-capability node holding the authority grant and its lineage. Declared `pub(crate) struct AuthorityNode { ... }` with fields elided; it MUST remain inaccessible to evaluator/runtime consumers, and the public capability API exposes only opaque `CapRef` handles.
- **FIRST_DEFINITION:** `L39373`, turn [58] — `pub(crate) struct AuthorityNode { ... }`
- **DEPENDENTS:** T-09 `CapRef`, T-10 `Authority`
- **FORBIDDEN_VARIANTS:**
    - `capability record`
    - `authority struct`
    - `cap entry`
- **PROTECTED (do not rename):**
    - `AuthorityNode` — frozen Rust type name (fields elided in source)
- **OBLIGATIONS:** `R-KERN-03`, `R-TRUST-03`, `R-CAP-05`
- **SECTIONS:** `S-10`
- **COLLISIONS:** [X-37](02-collisions.md#x-37)
- **NOTE:** Structure never given (fields elided at L39373). AMB-26 records that `Authority`/`AuthorityNode`/`CapabilityKernel` are used interchangeably in places; this dictionary separates them: `Authority` is the grant (T-10), `AuthorityNode` the kernel-private holder, `CapabilityKernel` the component.

### T-12 — `Constraint`

- **CANONICAL_TERM:** `Constraint`
- **TYPE:** RUST-STRUCT — a Rust `struct` declaration (nominal type)
- **OWNER:** MOD-03 (`ror-kernel`)
- **DEFINITION:** A narrowing REQUEST: the argument of `derive`. `Constraint` is not authority and cannot widen it — `derive(A,C) ⪯ A` and `derive_op(⟨S,Q,R,T⟩, ⟨S_c,Q_c,R_c,T_c⟩) = ⟨S⊓S_c, Q⊓Q_c, R⊓R_c, T⊓T_c⟩`. Well-formedness is gated by `AdmissibleConstraint`.
- **FIRST_DEFINITION:** `L6536`, turn [11] — `pub struct Constraint<S, Q, R, L> {`
- **DEPENDENTS:** T-10 `Authority`, T-09 `CapRef`, T-15 `DelegatedCapability`
- **FORBIDDEN_VARIANTS:**
    - `authority`
    - `capability`
    - `permission`
    - `scope` — unqualified
- **PROTECTED (do not rename):**
    - `Constraint` — frozen Rust type name and frozen algebra object
    - `C` — the frozen symbol for a Constraint in `derive(A,C)` — collides with Consumable `C` (X-08); both retained
    - `C_req` — frozen symbol for the required constraint in E-Attenuate (L8717)
    - `σ` — frozen symbol for a constraint in the turn-[5] attenuate rule (L2247)
    - `AdmissibleConstraint` — frozen trait name (status ambiguous, U-09/AMB-12)
- **OBLIGATIONS:** `R-CAP-04`, `R-CAP-02`, `R-CORE-04`
- **SECTIONS:** `S-09`
- **COLLISIONS:** [X-08](02-collisions.md#x-08), [X-16](02-collisions.md#x-16), [X-17](02-collisions.md#x-17), [X-70](02-collisions.md#x-70)
- **LAWS:** [N-28](03-laws.md#n-28), [N-29](03-laws.md#n-29)
- **NOTE:** No canonical byte encoding exists for `Constraint` in the frozen 15A tag set, although `Expr::Attenuate` embeds one as an immediate (C-16, U-02).

### T-13 — `CapabilityKernel`

- **CANONICAL_TERM:** `CapabilityKernel`
- **TYPE:** COMPONENT — an architectural component / trusted layer
- **OWNER:** MOD-03 (`ror-kernel`)
- **DEFINITION:** The trusted authority-decision layer: allocation, derivation, revocation, validity and the `Authorized` decision. It is the only component that may inspect `Authority`; the evaluator asks it and receives a verdict. Trusted per the trust table (R-TRUST-01).
- **FIRST_DEFINITION:** `L6680`, turn [11] — `pub struct CapRef {`
- **DEPENDENTS:** T-09 `CapRef`, T-10 `Authority`, T-11 `AuthorityNode`, T-12 `Constraint`
- **FORBIDDEN_VARIANTS:**
    - `kernel` — unqualified, where the CEK machine is meant
    - `authority manager`
    - `cap manager`
- **PROTECTED (do not rename):**
    - `CapabilityKernel` — frozen component name; trust-table row
    - `kernel` — used in the source's own prose for this component
    - `kernel.derive` — frozen operation name in the E-Attenuate rule (L8717)
- **OBLIGATIONS:** `R-KERN-01`, `R-KERN-02`, `R-KERN-03`, `R-TRUST-03`
- **SECTIONS:** `S-10`
- **COLLISIONS:** [X-05](02-collisions.md#x-05), [X-36](02-collisions.md#x-36), [X-37](02-collisions.md#x-37), [X-55](02-collisions.md#x-55), [X-66](02-collisions.md#x-66), [X-70](02-collisions.md#x-70)
- **NOTE:** `kernel` is context-dependent in the source (capability kernel vs the CEK machine's core); the qualified name is canonical in prose. AMB-26 records the interchange.

### T-14 — `CapabilityContext`

- **CANONICAL_TERM:** `CapabilityContext`
- **TYPE:** RUST-STRUCT — a Rust `struct` declaration (nominal type)
- **OWNER:** MOD-06 (`ror-runtime`)
- **DEFINITION:** An actor-local binding of names to `CapRef`s — the actor's `κ`. It is part of `ActorState` (`capabilities: CapabilityContext`) and MUST be included in snapshots. It holds references only, never `Authority`.
- **FIRST_DEFINITION:** `L25548`, turn [32] — `pub capabilities: CapabilityContext,`
- **DEPENDENTS:** T-09 `CapRef`, T-37 `ActorState`, T-48 `Snapshot`
- **FORBIDDEN_VARIANTS:**
    - `actor capability set`
    - `capability table`
    - `κ` — as a type name
- **PROTECTED (do not rename):**
    - `CapabilityContext` — frozen Rust type name
    - `capabilities` — frozen `ActorState` field name
    - `κ` — frozen mathematical symbol for the capability map (`κ(c)` lookup)
    - `ρ` — the environment symbol — distinct from κ; never conflated
- **OBLIGATIONS:** `R-ACTOR-01`, `R-ACTOR-02`, `R-PERSIST-04`
- **SECTIONS:** `S-15`, `S-18`
- **COLLISIONS:** [X-37](02-collisions.md#x-37), [X-57](02-collisions.md#x-57)
- **NOTE:** No canonical byte encoding is frozen for `CapabilityContext` (C-15, U-02).

### T-15 — `DelegatedCapability`

- **CANONICAL_TERM:** `DelegatedCapability`
- **TYPE:** RUST-VARIANT — an enum variant (not a type in its own right)
- **OWNER:** MOD-06 (`ror-runtime`)
- **DEFINITION:** The marshaller-accepted envelope that carries authority across an actor boundary by EXPLICIT delegation. Ordinary marshalling recursively rejects `Value::Capability`; only `Value::DelegatedCapability` is accepted, and only through the capability kernel. Delegation never amplifies: the derived authority is `⪯` the delegator's.
- **FIRST_DEFINITION:** `L25989`, turn [32] — `Delegate`
- **DEPENDENTS:** T-09 `CapRef`, T-12 `Constraint`, T-39 `Mailbox`
- **FORBIDDEN_VARIANTS:**
    - `capability transfer`
    - `capability copy`
    - `raw capability passing`
    - `marshalled capability`
- **PROTECTED (do not rename):**
    - `DelegatedCapability` — frozen `Value` variant name
    - `Expr::Delegate` — frozen AST constructor `{ capability: Box<Expr>, constraint: Constraint }` (L25989-25992); absent from the turn-[21] 12-constructor `Expr` (AMB-11)
    - `delegate` — frozen operation name for cross-actor authority transfer
    - `attenuate` — frozen operation name for in-actor narrowing — NOT a synonym for delegate
    - `derive` — frozen algebra operation — NOT a synonym for either
- **OBLIGATIONS:** `R-MARSHAL-01`, `R-MARSHAL-02`, `R-CORE-07`, `R-CAP-04`
- **SECTIONS:** `S-16`
- **COLLISIONS:** [X-29](02-collisions.md#x-29), [X-70](02-collisions.md#x-70)
- **LAWS:** [N-29](03-laws.md#n-29)
- **NOTE:** spec/05 §1 separates `derive` (algebra op) / `attenuate` (machine operation) / `delegate` (cross-actor transfer); that separation is retained and made a law (N-12) because the source uses the three loosely.

### T-72 — `CapabilityError`

- **CANONICAL_TERM:** `CapabilityError`
- **TYPE:** RUST-ENUM — a Rust `enum` declaration (closed variant set)
- **OWNER:** MOD-03 (`ror-kernel`)
- **DEFINITION:** The structured reason carried by the frozen `Fault::Capability(CapabilityError)` variant and returned by the `CapabilityKernelView` API (`derive`/`revoke`/`…  -> Result<…, CapabilityError>`). Declared once, with an explicit elision; one variant used in the source is never declared.
- **FIRST_DEFINITION:** `L9736`, turn [17] — `) -> Result<&Authority, CapabilityError>;`
- **FROZEN_AT:** `L20408`, turn [28] — `pub enum CapabilityError {`
- **DEPENDENTS:** T-13 `CapabilityKernel`, T-09 `CapRef`, T-10 `Authority`, T-70 `Fault`
- **FORBIDDEN_VARIANTS:**
    - `CapabilityFault`
    - `capability error` — unqualified
- **PROTECTED (do not rename):**
    - `CapabilityError` — frozen Rust enum name — the ONLY declaration (L20408)
    - `Revoked` — declared L20409; used 3× as `CapabilityError::Revoked` (L20527, L20538, L20941) — a fourth apparent hit at L21022 is `RefCapabilityError::Revoked`, the reference model's separate type, and is commented out
    - `Expired` — declared L20410 — never used; the used form `ExpiredOrRevoked` belongs to `RefCapabilityError` (L20619)
    - `InvalidConstraint` — declared L20411; used L20451 as the `derive` fallback
    - `Invalid` — USED at L20835 as the `derive` fallback — NEVER declared (X-66)
    - `// ...` — verbatim elision marker at L20412
    - `RefCapabilityError` — the reference model's separate error type (L19628, L20617) — not this enum
- **FROZEN SHAPE:** `pub enum CapabilityError { Revoked, Expired, InvalidConstraint, /* … */ }`
- **OBLIGATIONS:** `R-CAP-01`, `R-CAP-02`
- **SECTIONS:** `S-07`, `S-09`
- **COLLISIONS:** [X-38](02-collisions.md#x-38), [X-59](02-collisions.md#x-59), [X-66](02-collisions.md#x-66), [X-68](02-collisions.md#x-68)
- **NOTE:** spec/05 L112 and U-08 both claim these variants are “not enumerated”; they are, at L20408–20413, behind an elision (X-59).

---

## EFFECT — Effect model and request/issuance protocol
Owning module: **MOD-08**.

### T-16 — `Effect`
*Required term.*

- **CANONICAL_TERM:** `Effect`
- **TYPE:** RUST-STRUCT — a Rust `struct` declaration (nominal type)
- **OWNER:** MOD-08 (`ror-core (type); ror-runtime (protocol)`)
- **DEFINITION:** Immutable canonical effect DATA: `{ op: Op, target: Target, params: Params, cost: Cost }`. An `Effect` is a description, not a request, not an issuance, and not an invocation. Its canonical bytes are hashed into `EffectDigest`, which is the effect's semantic identity across the issuance/receipt/recovery protocol.
- **FIRST_DEFINITION:** `L1166`, turn [3] — `pub struct Effect {`
- **FROZEN_AT:** `L9297`, turn [17] — `pub struct Effect {`
- **DEPENDENTS:** T-17 `EffectRequest`, T-21 `EffectDigest`, T-22 `EffectCost`
- **FORBIDDEN_VARIANTS:**
    - `side effect` — as a type name
    - `effect request` — an Effect is the payload of an EffectRequest
    - `host call`
    - `operation` — unqualified — `op` is one field of an Effect
    - `external effect` — that is the theorem-level event `ExternalEffect(E)`, which additionally requires issuance
- **PROTECTED (do not rename):**
    - `Effect` — frozen Rust type name
    - `op` — frozen field name
    - `target` — frozen field name
    - `params` — frozen field name
    - `cost` — frozen field name
    - `Op` — frozen field type (finite enumerable set; U-21)
    - `Target` — frozen field type (domain undefined; U-21)
    - `Params` — frozen field type (domain undefined; U-21)
    - `Cost` — frozen field type in the turn-[17]/[18] declarations
    - `ResourceUsage` — the turn-[11] name of the same field's type (L6541) — superseded, retained for traceability (X-26)
    - `cap_ref` — field of the turn-[3] `Effect` (L1166) — the frozen form has NO capability field; retained, not renamed (X-26)
    - `kind` — field of the turn-[3] `Effect` (L1166) — superseded by `op`
    - `E` — frozen mathematical symbol for an effect
- **FROZEN SHAPE:** `pub struct Effect { pub op: Op, pub target: Target, pub params: Params, pub cost: Cost }`
- **SUPERSEDES (recorded, not deleted):**
    - `pub struct Effect { kind: EffectKind, cap_ref: CapRef, target: Target }   // L1166`
    - `pub struct Effect { op, target, params, cost: ResourceUsage }   // L6541`
- **OBLIGATIONS:** `R-CALC-04`, `R-CALC-05`, `R-EFFECT-01`
- **SECTIONS:** `S-07`, `S-12`
- **COLLISIONS:** [X-04](02-collisions.md#x-04), [X-05](02-collisions.md#x-05), [X-20](02-collisions.md#x-20), [X-26](02-collisions.md#x-26), [X-27](02-collisions.md#x-27), [X-35](02-collisions.md#x-35), [X-36](02-collisions.md#x-36), [X-39](02-collisions.md#x-39), [X-44](02-collisions.md#x-44)
- **LAWS:** [N-13](03-laws.md#n-13)
- **NOTE:** spec/05 defines `Effect` as `{capability, operation, target, params, cost}`. No declaration in the source has that field set: the frozen form (L9297) has no capability field, and the only form with one is the superseded turn-[3] `cap_ref`. Because `EffectDigest = SHA-256(canonical_bytes(effect))`, adding a capability field would bind the digest to a `CapRef` and change digest semantics. Reported as X-39; the frozen field set is authoritative.

### T-17 — `EffectRequest`
*Required term.*

- **CANONICAL_TERM:** `EffectRequest`
- **TYPE:** RUST-STRUCT — a Rust `struct` declaration (nominal type)
- **OWNER:** MOD-08 (`ror-runtime`)
- **DEFINITION:** The TRANSIENT machine→host message: `{ id: EffectId, effect: Effect }`. It exists in memory only; its existence is never evidence of issuance. The frozen form deliberately carries no `CapRef`: the host adapter never receives authority, only the effect description and an id.
- **FIRST_DEFINITION:** `L1447`, turn [4] — `pub struct EffectRequest {`
- **FROZEN_AT:** `L23758`, turn [30] — `pub struct EffectRequest {`
- **DEPENDENTS:** T-16 `Effect`, T-20 `EffectId`, T-18 `EffectIssued`, T-42 `ReplayHost`
- **FORBIDDEN_VARIANTS:**
    - `effect` — as a synonym for the request
    - `issued effect`
    - `host invocation`
    - `external effect`
    - `pending effect` — that is `ActorStatus::Pending` / `PendingEffect`
- **PROTECTED (do not rename):**
    - `EffectRequest` — frozen Rust type name
    - `id` — frozen field name
    - `effect` — frozen field name
    - `cap` — field of the turn-[4]/[17]/[18] forms (L1449, L9317, L10325, L10809) — dropped by the frozen form; retained, not renamed (X-27)
- **FROZEN SHAPE:** `pub struct EffectRequest { pub id: EffectId, pub effect: Effect }   // L23758`
- **SUPERSEDES (recorded, not deleted):**
    - `pub struct EffectRequest { id: EffectId, cap: CapRef }   // L1447 (no effect field)`
    - `pub struct EffectRequest { id, effect, cap: CapRef }   // L9314, L10322, L10806`
- **OBLIGATIONS:** `R-EFFECT-01`, `R-EFFECT-03`, `R-DUR-01`
- **SECTIONS:** `S-12`, `S-13`
- **COLLISIONS:** [X-04](02-collisions.md#x-04), [X-27](02-collisions.md#x-27), [X-35](02-collisions.md#x-35), [X-57](02-collisions.md#x-57), [X-73](02-collisions.md#x-73), [X-74](02-collisions.md#x-74)
- **LAWS:** [N-04](03-laws.md#n-04), [N-13](03-laws.md#n-13)
- **NOTE:** N-04 (`EffectRequest ≠ EffectIssued`) is a durability law, not a naming preference.

### T-18 — `EffectIssued`
*Required term.*

- **CANONICAL_TERM:** `EffectIssued`
- **TYPE:** STATE-VS-RECORD — one name shared by a lifecycle state, a record kind and a struct
- **OWNER:** MOD-11 (`ror-persistence (record); ror-runtime (protocol step)`)
- **DEFINITION:** The DURABLE commitment fact that an effect may now be invoked: as a record `{ id: EffectId, actor: ActorId, effect_digest: EffectDigest, logical_time: LogicalTime, issue_cost: Consumable, reservation: Reserved }`; as a WAL record kind `WalRecord::EffectIssued { id, actor, digest }`; as a lifecycle predicate `Issued(E)`. `HostInvoked(E) ⇒ DurableIssued(E)`: the host is never invoked before this record is durable. Issuance is NOT completion.
- **FIRST_DEFINITION:** `L1377`, turn [4] — `EffectIssued {`
- **FROZEN_AT:** `L23765`, turn [30] — `pub struct EffectIssued {`
- **DEPENDENTS:** T-17 `EffectRequest`, T-20 `EffectId`, T-21 `EffectDigest`, T-47 `WalRecord`, T-23 `EffectJournal`
- **FORBIDDEN_VARIANTS:**
    - `completed effect`
    - `executed effect`
    - `finished effect`
    - `successful effect`
    - `issued` — as a synonym for the transient request
- **PROTECTED (do not rename):**
    - `EffectIssued` — frozen Rust struct name AND frozen `WalRecord` variant name AND frozen `EffectJournalEntry::Issued` variant — all three retained (X-07)
    - `Issued(E)` — frozen lifecycle predicate (`Completed(E) ⇒ Issued(E)`)
    - `DurableIssued(E)` — frozen predicate in the durability invariant
    - `effect_digest` — frozen field name of the struct form
    - `digest` — frozen field name of the WAL/journal variant forms — a DIFFERENT field name for the same value; not renamed (X-07)
    - `logical_time` — frozen field name (absent from the WAL variant)
    - `issue_cost` — frozen field name (absent from the WAL variant)
    - `reservation` — frozen field name (absent from the WAL variant)
    - `effect_id` — field name of the turn-[3] prose form (L1378) — superseded by `id`
- **FROZEN SHAPE:** `pub struct EffectIssued { id, actor, effect_digest, logical_time, issue_cost, reservation }   // L23765
WalRecord::EffectIssued { id: EffectId, actor: ActorId, digest: EffectDigest }   // L35130`
- **SUPERSEDES (recorded, not deleted):**
    - `EffectIssued { effect_id, capability, effect, target }   // L1377 (turn [3] prose)`
    - `ℒ ⊕ EffectIssued(E.id, c, E)   // L2254 (event-log entry carrying the CapRef)`
- **OBLIGATIONS:** `R-DUR-01`, `R-DUR-02`, `R-DUR-03`, `R-EFFECT-03`, `R-CORE-06`
- **SECTIONS:** `S-13`, `S-18`
- **COLLISIONS:** [X-07](02-collisions.md#x-07), [X-24](02-collisions.md#x-24), [X-32](02-collisions.md#x-32), [X-57](02-collisions.md#x-57)
- **LAWS:** [N-04](03-laws.md#n-04), [N-05](03-laws.md#n-05), [N-14](03-laws.md#n-14)
- **NOTE:** The struct and the WAL variant are NOT the same payload: the variant omits `logical_time`, `issue_cost` and `reservation` and renames `effect_digest` to `digest`. Since escrow release on completion needs the reservation, the divergence is substantive (X-07) and is reported, not reconciled by renaming either field.

### T-19 — `EffectReceipt`
*Required term.*

- **CANONICAL_TERM:** `EffectReceipt`
- **TYPE:** RUST-STRUCT — a Rust `struct` declaration (nominal type)
- **OWNER:** MOD-08 (`ror-runtime (validation); ror-host (production)`)
- **DEFINITION:** The host→machine RESULT of an invoked effect: `{ id: EffectId, effect_digest: EffectDigest, result: Result<Value, HostFault> }`. A receipt is accepted only if BOTH its id and its digest match the issued record; a mismatch is `ReplayCorruption`/`InvalidReceipt`, never a silent accept. A receipt is not proof the effect happened — the durable issued record is.
- **FIRST_DEFINITION:** `L1454`, turn [4] — `pub struct EffectReceipt {`
- **FROZEN_AT:** `L23775`, turn [30] — `pub struct EffectReceipt {`
- **DEPENDENTS:** T-18 `EffectIssued`, T-20 `EffectId`, T-21 `EffectDigest`, T-42 `ReplayHost`
- **FORBIDDEN_VARIANTS:**
    - `result` — unqualified
    - `response`
    - `completion record` — the durable completion is `WalRecord::EffectCompleted`
    - `acknowledgement`
- **PROTECTED (do not rename):**
    - `EffectReceipt` — frozen Rust type name
    - `id` — frozen field name
    - `effect_digest` — frozen field name
    - `result` — frozen field name
    - `HostFault` — frozen error type carried in `result` (variants undefined, U-14)
    - `ResultDigest` — frozen newtype for the digest of a result in `WalRecord::EffectCompleted` — distinct from `EffectDigest`
    - `R` — frozen mathematical symbol for a receipt in the receipt rules (L2021, L7381)
- **FROZEN SHAPE:** `pub struct EffectReceipt { pub id: EffectId, pub effect_digest: EffectDigest, pub result: Result<Value, HostFault> }`
- **OBLIGATIONS:** `R-EFFECT-06`, `R-HOST-03`, `R-DUR-03`
- **SECTIONS:** `S-12`, `S-14`
- **COLLISIONS:** [X-09](02-collisions.md#x-09), [X-43](02-collisions.md#x-43), [X-61](02-collisions.md#x-61)
- **LAWS:** [N-05](03-laws.md#n-05), [N-14](03-laws.md#n-14)
- **NOTE:** `R` as the receipt symbol (L2021, L7381) collides with `R` = Reserved and `R` = the authority resource-limit component (X-09).

### T-20 — `EffectId`
*Required term.*

- **CANONICAL_TERM:** `EffectId`
- **TYPE:** RUST-NEWTYPE — a Rust single-field tuple `struct` wrapper
- **OWNER:** MOD-08 (`ror-core (type); ror-runtime (allocation)`)
- **DEFINITION:** The monotonic allocation counter value identifying an effect instance: `pub struct EffectId(pub u64)`, allocated as `h = N_h; N_h' = N_h + 1`, carried by `GlobalState.next_effect_id`, and given 15A standalone tag `0x41`. An id is an ALLOCATION identity, not semantic identity: semantic identity is `EffectDigest`. On a denied request the id is not incremented.
- **FIRST_DEFINITION:** `L9128`, turn [17] — `pub type EffectId = u64;`
- **FROZEN_AT:** `L23735`, turn [30] — `pub struct EffectId(pub u64);`
- **DEPENDENTS:** T-17 `EffectRequest`, T-18 `EffectIssued`, T-19 `EffectReceipt`, T-21 `EffectDigest`
- **FORBIDDEN_VARIANTS:**
    - `handle` — the obsolete v0.3 `h` wording as a current name
    - `effect handle`
    - `effect digest` — as a synonym — id and digest have different roles
    - `effect key`
- **PROTECTED (do not rename):**
    - `EffectId` — frozen type name; 15A standalone tag `0x41`
    - `h` — the frozen mathematical symbol for an allocated effect id in the v0.3 transition rules (`Pending(h, E, K)`, L8740) — retained in those rules; not a current prose name
    - `N_h` — frozen symbol for the id allocation counter
    - `next_effect_id` — frozen `GlobalState` field name
    - `id` — frozen field name wherever an `EffectId` is carried
    - `effect_id` — frozen field name in `ActorStatus::Pending` and `PendingEffect` — a different spelling of the same value (X-22); not renamed
- **FROZEN SHAPE:** `pub struct EffectId(pub u64);   // L9342, L23735`
- **SUPERSEDES (recorded, not deleted):**
    - `pub type EffectId = u64;   // L9128 (turn [17], earlier in the same turn)`
- **OBLIGATIONS:** `R-CALC-04`, `R-EFFECT-02`, `R-EFFECT-04`, `R-DUR-03`
- **SECTIONS:** `S-07`, `S-12`
- **COLLISIONS:** [X-07](02-collisions.md#x-07), [X-22](02-collisions.md#x-22), [X-24](02-collisions.md#x-24), [X-43](02-collisions.md#x-43), [X-61](02-collisions.md#x-61)
- **LAWS:** [N-23](03-laws.md#n-23)
- **NOTE:** `pub type EffectId = u64` and `pub struct EffectId(pub u64)` both appear in turn [17] (L9128 and L9342). An alias cannot carry a distinct 15A tag, and 15A gives `EffectId` tag `0x41` distinct from `ActorId` `0x40`, so the newtype is the only form consistent with the frozen wire format (X-24). Both are recorded; neither is renamed.

### T-21 — `EffectDigest`

- **CANONICAL_TERM:** `EffectDigest`
- **TYPE:** RUST-NEWTYPE — a Rust single-field tuple `struct` wrapper
- **OWNER:** MOD-08 (`ror-core (type); ror-persistence (validation)`)
- **DEFINITION:** `SHA-256(canonical_bytes(effect))` — the SEMANTIC identity of an effect. Every subsequent record for an effect must carry the identical `EffectId` AND `EffectDigest`; a digest mismatch is `EffectJournalCorruption`, not a different effect. The ReplayHost validates ordered id + digest.
- **FIRST_DEFINITION:** `L9343`, turn [17] — `pub struct EffectDigest([u8; 32]);`
- **FROZEN_AT:** `L23738`, turn [30] — `pub struct EffectDigest(pub [u8; 32]);`
- **DEPENDENTS:** T-16 `Effect`, T-18 `EffectIssued`, T-19 `EffectReceipt`, T-42 `ReplayHost`
- **FORBIDDEN_VARIANTS:**
    - `effect hash`
    - `effect checksum`
    - `effect id` — as a synonym
- **PROTECTED (do not rename):**
    - `EffectDigest` — frozen type name
    - `digest` — frozen field name in `WalRecord`/`EffectJournalEntry` variants
    - `effect_digest` — frozen field name in the `EffectIssued`/`EffectReceipt` structs
    - `ResultDigest` — frozen distinct newtype for a result's digest
    - `StateDigest` — frozen distinct newtype for a snapshot's digest
    - `ProposalDigest` — frozen distinct name for a proposal's digest (U-13)
- **OBLIGATIONS:** `R-CALC-04`, `R-DUR-03`, `R-HOST-03`, `R-EFFECT-06`
- **SECTIONS:** `S-07`, `S-13`, `S-14`
- **COLLISIONS:** [X-07](02-collisions.md#x-07), [X-26](02-collisions.md#x-26), [X-39](02-collisions.md#x-39), [X-50](02-collisions.md#x-50)
- **LAWS:** [N-23](03-laws.md#n-23)
- **NOTE:** Three digest newtypes coexist (`EffectDigest`, `ResultDigest`, `StateDigest`) plus `ProposalDigest`; they are distinct and must not be interchanged. Field spelling differs by carrier (`digest` vs `effect_digest`) — recorded, not normalized.

### T-22 — `EffectCost`

- **CANONICAL_TERM:** `EffectCost`
- **TYPE:** RUST-STRUCT — a Rust `struct` declaration (nominal type)
- **OWNER:** MOD-08 (`ror-core`)
- **DEFINITION:** The split cost model of an effect: `{ issue: Consumable, complete_max: Consumable, reserve: Reserved }`. `issue` is charged at issuance, `reserve` is escrowed for the reservation, and `complete_max` is the ABSOLUTE MAXIMUM chargeable at receipt time — escrowing it up front is what makes guaranteed completion accounting conserve budget.
- **FIRST_DEFINITION:** `L21390`, turn [29] — `pub struct EffectCost {`
- **FROZEN_AT:** `L25806`, turn [32] — `pub struct EffectCost {`
- **DEPENDENTS:** T-16 `Effect`, T-24 `Budget`, T-25 `Consumable`, T-26 `Reserved`
- **FORBIDDEN_VARIANTS:**
    - `cost` — unqualified, where `Cost` the budget pair is meant
    - `price`
    - `effect budget`
- **PROTECTED (do not rename):**
    - `EffectCost` — frozen Rust type name
    - `issue` — frozen field name
    - `complete_max` — frozen field name (renamed from `complete` by the Phase 13 correction; `complete_max` is canonical, C-23)
    - `complete` — the superseded turn-[29] field name — retained for traceability; it under-escrows and is a fixed vulnerability
    - `reserve` — frozen field name
    - `Cost` — frozen DISTINCT type `{consumable, reserved}` used by `Effect.cost` (L9182) — not a synonym for `EffectCost`
- **OBLIGATIONS:** `R-CALC-05`, `R-EFFECT-05`, `R-BUDGET-07`
- **SECTIONS:** `S-07`, `S-12`
- **COLLISIONS:** [X-26](02-collisions.md#x-26), [X-44](02-collisions.md#x-44)
- **NOTE:** `Cost` (the `Effect.cost` pair) and `EffectCost` (the split issue/complete/reserve model) are different types with overlapping purpose; AMB-23 records the field-order ambiguity of `EffectCost`.

---

## RESOURCE — Budget algebra and logical time
Owning module: **MOD-04**.

### T-24 — `Budget`
*Required term.*

- **CANONICAL_TERM:** `Budget`
- **TYPE:** RUST-STRUCT — a Rust `struct` declaration (nominal type)
- **OWNER:** MOD-04 (`ror-core (algebra); gates in ror-runtime/ror-kernel`)
- **DEFINITION:** The resource bound of an actor/plan: `B = ⟨C, R, W⟩` = `{ consumable: Consumable, reserved: Reserved, deadline: Deadline }`. Conservation is explicit and checked: `C_available + C_escrowed + C_consumed = C_initial`. Checked arithmetic is required; saturating subtraction is prohibited for semantic accounting.
- **FIRST_DEFINITION:** `L1788`, turn [4] — `\operatorname{WithinBudget}(e,B)`
- **FROZEN_AT:** `L9172`, turn [17] — `pub struct Budget {`
- **DEPENDENTS:** T-25 `Consumable`, T-26 `Reserved`, T-27 `Deadline`, T-28 `LogicalTime`, T-29 `CostModel`
- **FORBIDDEN_VARIANTS:**
    - `resource limit` — unqualified — that is the authority component `R_A`
    - `quota`
    - `allowance`
    - `gas`
    - `fuel` — that is one dimension of `Consumable`
- **PROTECTED (do not rename):**
    - `Budget` — frozen Rust type name and trust-table row
    - `B` — frozen mathematical symbol — also used for a block in turn [1] (X-15)
    - `B_max` — frozen symbol for a static budget bound in the judgments
    - `B_f` — frozen symbol for a closure's budget annotation
    - `B_child` — frozen symbol for a spawned actor's budget
    - `B_alloc` — frozen symbol for the allocated spawn budget (U-03)
    - `R_B` — frozen symbol for the dynamic execution budget (L6420)
    - `BudgetAllocationSpec` — frozen `Expr::Spawn` field type (validation rules never stated, U-03)
- **FROZEN SHAPE:** `pub struct Budget { pub consumable: Consumable, pub reserved: Reserved, pub deadline: Deadline }`
- **SUPERSEDES (recorded, not deleted):**
    - `6-dimension budget ⟨fuel, mem, msgs, calls, io, time⟩   // L1960 (v1)`
    - `5-dimension cost algebra ⟨F, M, C, I, W⟩   // L6730 (v0.1)`
- **OBLIGATIONS:** `R-BUDGET-01`, `R-BUDGET-02`, `R-BUDGET-05`, `R-CORE-05`
- **SECTIONS:** `S-11`
- **COLLISIONS:** [X-08](02-collisions.md#x-08), [X-09](02-collisions.md#x-09), [X-15](02-collisions.md#x-15), [X-19](02-collisions.md#x-19), [X-44](02-collisions.md#x-44), [X-69](02-collisions.md#x-69)
- **LAWS:** [N-16](03-laws.md#n-16)
- **NOTE:** Dimension drift across v1 → v0.1 → v0.2/v0.3 is recorded as C-06 (resolved-by-later-text); the frozen form is `⟨C,R,W⟩`. The operational meaning of the `duration` dimension is still undecided (U-01).

### T-25 — `Consumable`
*Required term.*

- **CANONICAL_TERM:** `Consumable`
- **TYPE:** RUST-STRUCT — a Rust `struct` declaration (nominal type)
- **OWNER:** MOD-04 (`ror-core`)
- **DEFINITION:** The strictly-decreasing budget component `C = ⟨F, I, D⟩` = `{ fuel: u64, io: u64, duration: u64 }`. Consumables are SPENT and never returned; escrow moves a quantity from `available` to `escrowed` and settlement moves it to `consumed`. Dimensions are named fields, not tuple positions.
- **FIRST_DEFINITION:** `L7130`, turn [13] — `$C = \langle F, I, D \rangle$`
- **FROZEN_AT:** `L9159`, turn [17] — `pub struct Consumable {`
- **DEPENDENTS:** T-24 `Budget`, T-22 `EffectCost`, T-29 `CostModel`
- **FORBIDDEN_VARIANTS:**
    - `spendable resources`
    - `fuel` — as a synonym for the whole vector
    - `consumables` — as a distinct type from `Consumable`
- **PROTECTED (do not rename):**
    - `Consumable` — frozen Rust type name
    - `C` — frozen mathematical symbol — ALSO the Constraint of `derive(A,C)` (X-08)
    - `fuel` — frozen field name
    - `io` — frozen field name
    - `duration` — frozen field name (operational meaning undecided, U-01)
    - `F` — frozen symbol for the fuel dimension — ALSO the effect set and the replay-tuple 'effect invoked' (X-16)
    - `I` — frozen symbol for the I/O dimension
    - `D` — frozen symbol for the duration dimension — ALSO the durable state `D = ⟨S,L,H⟩` (X-12)
    - `φ` — the turn-[2] symbol for remaining fuel (L718, L725) — superseded by `F`/`fuel`, retained in that text
    - `C_available` — frozen partition symbol
    - `C_escrowed` — frozen partition symbol
    - `C_consumed` — frozen partition symbol
    - `C_initial` — frozen partition symbol
- **FROZEN SHAPE:** `pub struct Consumable { pub fuel: u64, pub io: u64, pub duration: u64 }`
- **OBLIGATIONS:** `R-BUDGET-01`, `R-BUDGET-03`, `R-BUDGET-05`, `R-CORE-05`
- **SECTIONS:** `S-11`
- **COLLISIONS:** [X-08](02-collisions.md#x-08), [X-12](02-collisions.md#x-12), [X-16](02-collisions.md#x-16), [X-18](02-collisions.md#x-18), [X-19](02-collisions.md#x-19), [X-44](02-collisions.md#x-44)
- **LAWS:** [N-16](03-laws.md#n-16), [N-17](03-laws.md#n-17)
- **NOTE:** The three accounting partitions `available`/`escrowed`/`consumed` are frozen; the source's informal `held`/`spent`/`remaining` are prose variants and are forbidden as substitutes (spec/05 §2).

### T-26 — `Reserved`
*Required term.*

- **CANONICAL_TERM:** `Reserved`
- **TYPE:** RUST-STRUCT — a Rust `struct` declaration (nominal type)
- **OWNER:** MOD-04 (`ror-core`)
- **DEFINITION:** The held-then-released budget component `R = ⟨M, S⟩` = `{ memory: u64, slots: u64 }`. Reservations are checked by `ReserveOK(r,R) ⇔ R + r ≤ R_max` and released by `ReleaseOK(r,R) ⇔ r ≤ R`. An indeterminate effect's reservation is NEVER silently released.
- **FIRST_DEFINITION:** `L7131`, turn [13] — `$R = \langle M, S \rangle$`
- **FROZEN_AT:** `L9166`, turn [17] — `pub struct Reserved {`
- **DEPENDENTS:** T-24 `Budget`, T-22 `EffectCost`
- **FORBIDDEN_VARIANTS:**
    - `reserved capacity` — as a distinct type
    - `reservation` — as a synonym for the vector — a reservation is one held quantity
    - `escrow` — escrow is a partition of `Consumable` accounting
- **PROTECTED (do not rename):**
    - `Reserved` — frozen Rust type name
    - `R` — frozen mathematical symbol — ALSO the authority resource-limit component and the receipt symbol (X-09)
    - `memory` — frozen field name
    - `slots` — frozen field name
    - `M` — frozen symbol for the memory dimension — ALSO the replay-tuple component and the milestone/mutation id prefixes (X-16)
    - `S` — frozen symbol for concurrency slots — ALSO Scope and Snapshot (X-10)
    - `R_max` — frozen symbol for the reservation ceiling
    - `R_A` — frozen symbol for a capability's resource ceiling — a DIFFERENT object from the actor's `R`; L6420 states the distinction
    - `ReserveOK` — frozen predicate name ([15] correction)
    - `ReleaseOK` — frozen predicate name ([15] correction)
    - `reservation` — frozen field name in `EffectIssued` and `ActorStatus::Pending`
- **FROZEN SHAPE:** `pub struct Reserved { pub memory: u64, pub slots: u64 }`
- **SUPERSEDES (recorded, not deleted):**
    - `(C ≥ ΔC) ∧ (R + ΔR ≥ 0)   // L7314 — wrong reservation direction (C-07)`
- **OBLIGATIONS:** `R-BUDGET-01`, `R-BUDGET-03`, `R-BUDGET-04`, `R-CORE-05`
- **SECTIONS:** `S-11`
- **COLLISIONS:** [X-07](02-collisions.md#x-07), [X-09](02-collisions.md#x-09), [X-10](02-collisions.md#x-10), [X-16](02-collisions.md#x-16), [X-19](02-collisions.md#x-19), [X-21](02-collisions.md#x-21), [X-22](02-collisions.md#x-22), [X-44](02-collisions.md#x-44), [X-49](02-collisions.md#x-49), [X-74](02-collisions.md#x-74)
- **LAWS:** [N-17](03-laws.md#n-17)
- **NOTE:** The direction error of the pre-[15] `BudgetOK` is C-07; `ReserveOK`/`ReleaseOK` are the frozen forms.

### T-27 — `Deadline`

- **CANONICAL_TERM:** `Deadline`
- **TYPE:** RUST-NEWTYPE — a Rust single-field tuple `struct` wrapper
- **OWNER:** MOD-04 (`ror-core`)
- **DEFINITION:** An ABSOLUTE logical-time bound `W ∈ ℕ ∪ {∞}`: `pub struct Deadline(pub Option<LogicalTime>)`, where `Deadline(None)` means ∞. A deadline is checked, not spent: validity is `t + δ_t ≤ W`. It is never a wall-clock time.
- **FIRST_DEFINITION:** `L6748`, turn [11] — `3. **Deadline ($W$):**`
- **FROZEN_AT:** `L9140`, turn [17] — `pub struct Deadline(pub Option<LogicalTime>);`
- **DEPENDENTS:** T-24 `Budget`, T-28 `LogicalTime`
- **FORBIDDEN_VARIANTS:**
    - `timeout` — a timeout implies wall-clock measurement
    - `time limit`
    - `duration` — that is the `D` consumable dimension
    - `expiry` — used for capability lifetime `T`, a different bound
- **PROTECTED (do not rename):**
    - `Deadline` — frozen Rust type name
    - `W` — frozen mathematical symbol
    - `DeadlineValid(E,t)` — frozen predicate in the central theorem
    - `DeadlineExceeded` — frozen `Fault` variant
- **OBLIGATIONS:** `R-BUDGET-01`, `R-BUDGET-06`, `R-CAP-09`
- **SECTIONS:** `S-11`
- **COLLISIONS:** [X-12](02-collisions.md#x-12), [X-42](02-collisions.md#x-42), [X-69](02-collisions.md#x-69)
- **LAWS:** [N-18](03-laws.md#n-18)
- **NOTE:** `W` (deadline) vs `D` (duration consumable) vs `T` (capability lifetime) are three distinct bounds.

### T-28 — `LogicalTime`
*Required term.*

- **CANONICAL_TERM:** `LogicalTime`
- **TYPE:** RUST-NEWTYPE — a Rust single-field tuple `struct` wrapper
- **OWNER:** MOD-04 (`ror-core (type); ror-runtime (advance)`)
- **DEFINITION:** The explicit deterministic time of the machine: `pub struct LogicalTime(pub u64)`, held once in `GlobalState.logical_time` and advanced only by transitions with `δ_t > 0` (host/scheduler steps; pure steps have `δ_t = 0`). It is a component of machine state, never fetched from the host OS, and never wall-clock.
- **FIRST_DEFINITION:** `L6437`, turn [11] — `It is an explicit component of the machine state`
- **FROZEN_AT:** `L9137`, turn [17] — `pub struct LogicalTime(pub u64);`
- **DEPENDENTS:** T-27 `Deadline`, T-38 `GlobalState`, T-18 `EffectIssued`
- **FORBIDDEN_VARIANTS:**
    - `wall-clock time`
    - `system time`
    - `timestamp` — unqualified — the source's 'deterministic timestamp' means logical time
    - `clock`
    - `real time`
    - `now`
- **PROTECTED (do not rename):**
    - `LogicalTime` — frozen Rust type name
    - `t` — frozen mathematical symbol for the current logical time
    - `δ_t` — frozen symbol for a per-transition time delta (values not enumerated, U-07)
    - `logical_time` — frozen field name in `GlobalState` and `EffectIssued`
- **OBLIGATIONS:** `R-BUDGET-06`, `R-CAP-09`, `R-CORE-08`
- **SECTIONS:** `S-11`, `S-09`
- **COLLISIONS:** [X-42](02-collisions.md#x-42)
- **LAWS:** [N-18](03-laws.md#n-18)
- **NOTE:** R-CAP-09 prohibits wall-clock time as semantic machine state. The per-transition `δ_t` values are not frozen (U-07), so `LogicalTime` is defined but its advancement schedule is not.

### T-29 — `CostModel`

- **CANONICAL_TERM:** `CostModel`
- **TYPE:** RUST-TRAIT — a Rust `trait` (API contract)
- **OWNER:** MOD-04 (`ror-core`)
- **DEFINITION:** The op→cost mapping contract: `fn cost_c(&self, op: &Op) -> Consumable` and `fn cost_r(&self, op: &Op) -> Reserved`. It prices operations; it does not decide admissibility (that is the budget gate) and it does not price the effect lifecycle split (that is `EffectCost`).
- **FIRST_DEFINITION:** `L10168`, turn [18] — `pub trait CostModel {`
- **DEPENDENTS:** T-25 `Consumable`, T-26 `Reserved`, T-22 `EffectCost`, T-16 `Effect`
- **FORBIDDEN_VARIANTS:**
    - `cost function` — as a type name
    - `pricer`
    - `meter`
- **PROTECTED (do not rename):**
    - `CostModel` — frozen trait name
    - `cost_c` — frozen method name
    - `cost_r` — frozen method name
    - `Cost` — frozen struct `{consumable, reserved}` — the `Effect.cost` type
    - `cost_C` — frozen symbol for the consumable cost function in the v0.3 rules
    - `cost_io` — frozen symbol in the receipt rule (L7381)
    - `cost_res` — frozen symbol in the receipt rule (L7381)
- **OBLIGATIONS:** `R-BUDGET-07`
- **SECTIONS:** `S-11`
- **COLLISIONS:** [X-19](02-collisions.md#x-19), [X-44](02-collisions.md#x-44)
- **NOTE:** `dep/05` §7 records what the cost model does NOT price; that statement is not a terminology source.

---

## MACHINE — Calculus, CEK machine, values, frames
Owning module: **MOD-05**.

### T-30 — `Expr`

- **CANONICAL_TERM:** `Expr`
- **TYPE:** RUST-ENUM — a Rust `enum` declaration (closed variant set)
- **OWNER:** MOD-01 (`ror-core`)
- **DEFINITION:** The frozen core-calculus AST: a closed set of 12 declarative constructors (`Value, Var, Let, Seq, If, Call, Lambda, Attenuate, Request, Spawn, Send, Receive`). `Expr` is what an `ExecutablePlan` carries into the machine; it is not the language surface (`Block`) and not an intermediate stage (`PlanIR`).
- **FIRST_DEFINITION:** `L12145`, turn [21] — `pub enum Expr {`
- **DEPENDENTS:** T-06 `ExecutablePlan`, T-31 `Value`, T-32 `EvalState`, T-33 `Frame`
- **FORBIDDEN_VARIANTS:**
    - `AST` — unqualified — `NormalizedAST` is a different, undeclared name
    - `expression tree`
    - `PlanIR` — a superseded/undeclared IR name
    - `code`
- **PROTECTED (do not rename):**
    - `Expr` — frozen Rust enum name
    - `Expr::Request` — frozen constructor `{ capability: Box<Expr>, operation: Op, target: TargetExpr, params: Vec<Expr> }` (L12183)
    - `Expr::Attenuate` — frozen constructor `{ capability, constraint: Constraint, body }`
    - `Expr::Spawn` — frozen constructor `{ body, budget: BudgetAllocationSpec }`
    - `Expr::Delegate` — frozen constructor at L25989 — ABSENT from the turn-[21] 12-constructor set (AMB-11); not removed by this dictionary
    - `invoke` — the superseded v1/v2 surface name for `Request` (C-17); retained in supersession notes only
    - `await` — the retracted constructor (U-04); retained for traceability
    - `e` — frozen mathematical symbol for an expression
- **FROZEN SHAPE:** `pub enum Expr { Value(Value), Var(Symbol), Let{..}, Seq{..}, If{..}, Call{..}, Lambda{..}, Attenuate{..}, Request{..}, Spawn{..}, Send{..}, Receive }`
- **OBLIGATIONS:** `R-CALC-02`, `R-CALC-03`, `R-COMPILE-01`
- **SECTIONS:** `S-07`
- **COLLISIONS:** [X-03](02-collisions.md#x-03), [X-30](02-collisions.md#x-30), [X-35](02-collisions.md#x-35), [X-39](02-collisions.md#x-39), [X-70](02-collisions.md#x-70)
- **NOTE:** `Expr::Request` has two frozen field sets: `{cap, args}` (L10420, turn [18]) and `{capability, operation, target, params}` (L12183, turn [21]) — X-35.

### T-31 — `Value`

- **CANONICAL_TERM:** `Value`
- **TYPE:** RUST-ENUM — a Rust `enum` declaration (closed variant set)
- **OWNER:** MOD-01 (`ror-core (machine); ror-core/15A (canonical)`)
- **DEFINITION:** AMBIGUOUS BY SOURCE DECREE — two incompatible frozen domains share this name: the machine value domain (11 variants: `Unit, Bool, Integer, Bytes, Symbol, String, List, Tuple, Function, Capability, Actor`) and the 15A canonical data domain (8 variants: `Unit, Bool, Integer, String, Symbol, Capability, List, Map`). This dictionary records both and defers the naming decision to U-09; it does not rename either.
- **FIRST_DEFINITION:** `L12283`, turn [21] — `pub enum Value {`
- **DEPENDENTS:** T-01 `Block`, T-30 `Expr`, T-39 `Mailbox`, T-46 `WalFrame`
- **FORBIDDEN_VARIANTS:**
    - `data` — unqualified — `Data` is proposed but NOT frozen as the canonical-domain name
    - `term`
    - `object`
- **PROTECTED (do not rename):**
    - `Value` — frozen name of BOTH domains; neither may be renamed without an explicit decision (U-09)
    - `Value::Capability` — frozen machine-domain variant carrying a `CapRef`
    - `Value::Function` — frozen machine-domain variant
    - `Value::Map` — frozen canonical-domain variant (absent from the machine domain)
    - `FunctionValue` — frozen type `{params, body, env}`; `env: EnvironmentSnapshot` (X-33)
    - `Value::Null` — source-used spelling L1027 (turn [3]) — every declared `Value` set has `Unit`, not `Null` (X-75)
    - `Value::DelegatedCapability` — source-used path L25995/L26000 (turn [32]) — in no `Value` declaration; the declared capability variant is `Capability(Box<CapabilityToken>)` (X-70, X-75)
- **OBLIGATIONS:** `R-CALC-01`, `R-CANON-04`, `R-MARSHAL-03`
- **SECTIONS:** `S-07`, `S-17`
- **COLLISIONS:** [X-28](02-collisions.md#x-28), [X-33](02-collisions.md#x-33), [X-45](02-collisions.md#x-45), [X-54](02-collisions.md#x-54), [X-55](02-collisions.md#x-55), [X-56](02-collisions.md#x-56), [X-70](02-collisions.md#x-70), [X-72](02-collisions.md#x-72), [X-75](02-collisions.md#x-75)
- **NOTE:** Registered upstream as C-03, C-45, U-09, AMB-21. Restated here so the dictionary is complete.

### T-32 — `EvalState`

- **CANONICAL_TERM:** `EvalState`
- **TYPE:** RUST-STRUCT — a Rust `struct` declaration (nominal type)
- **OWNER:** MOD-05 (`ror-runtime`)
- **DEFINITION:** The per-actor evaluation triple `{ expr: Expr, env: Environment, continuation: Continuation }` — the explicit C/E/K state. A value is terminal only when its continuation is empty. The evaluator does not use recursive host-language calls for semantic call-stack management.
- **FIRST_DEFINITION:** `L12655`, turn [21] — `pub struct EvalState {`
- **DEPENDENTS:** T-30 `Expr`, T-33 `Frame`, T-37 `ActorState`
- **FORBIDDEN_VARIANTS:**
    - `eval state` — as prose
    - `stack frame` — that is `Frame`
    - `CEK` — the machine, not the state
- **PROTECTED (do not rename):**
    - `EvalState` — frozen Rust type name
    - `expr` — frozen field name
    - `env` — frozen field name
    - `continuation` — frozen field name
    - `eval` — frozen `ActorState` field name (`actor.eval.continuation`)
    - `CEK` — frozen name of the machine (Control/Environment/Continuation)
- **OBLIGATIONS:** `R-CEK-01`, `R-CEK-02`, `R-ACTOR-02`
- **SECTIONS:** `S-08`
- **COLLISIONS:** [X-18](02-collisions.md#x-18), [X-21](02-collisions.md#x-21), [X-22](02-collisions.md#x-22), [X-57](02-collisions.md#x-57), [X-74](02-collisions.md#x-74)
- **NOTE:** No canonical byte encoding is frozen for `EvalState` (C-15, U-02).

### T-33 — `Frame`

- **CANONICAL_TERM:** `Frame`
- **TYPE:** RUST-ENUM — a Rust `enum` declaration (closed variant set)
- **OWNER:** MOD-05 (`ror-runtime`)
- **DEFINITION:** A continuation frame — an element of the frozen frame set (R-CEK-03). A `Continuation` is a stack of `Frame`s. The set is closed; adding a frame kind is a specification change, not an implementation choice.
- **FIRST_DEFINITION:** `L12453`, turn [21] — `pub enum Frame {`
- **FROZEN_AT:** `L16943`, turn [25] — `pub enum Frame {`
- **DEPENDENTS:** T-32 `EvalState`
- **FORBIDDEN_VARIANTS:**
    - `stack frame` — unqualified
    - `continuation` — as a synonym for one frame
    - `EvalFrame`
    - `ContinuationFrame`
- **PROTECTED (do not rename):**
    - `Frame` — frozen Rust enum name — declared ELEVEN times (AMB-26); all declarations are retained
    - `Continuation` — frozen distinct type (a stack of frames, L12517)
    - `K` — frozen mathematical symbol for a continuation
- **OBLIGATIONS:** `R-CEK-03`
- **SECTIONS:** `S-08`
- **COLLISIONS:** [X-33](02-collisions.md#x-33), [X-37](02-collisions.md#x-37)
- **NOTE:** AMB-26 records the eleven `pub enum Frame` declarations and notes that no type named `EvalFrame` or `ContinuationFrame` exists in the source; those names are therefore forbidden as invented identifiers.

### T-38 — `GlobalState`

- **CANONICAL_TERM:** `GlobalState`
- **TYPE:** RUST-STRUCT — a Rust `struct` declaration (nominal type)
- **OWNER:** MOD-05 (`ror-runtime`)
- **DEFINITION:** The frozen global machine configuration: `{ actors: BTreeMap<ActorId, ActorState>, logical_time: LogicalTime, runnable: RunnableQueue, event_log: EventLog, next_effect_id: EffectId, next_actor_id: ActorId }`. It is the object transitions act on (`G --a,c--> G'`) and the object a snapshot commits.
- **FIRST_DEFINITION:** `L24156`, turn [31] — `pub struct GlobalState {`
- **FROZEN_AT:** `L25535`, turn [32] — `pub struct GlobalState {`
- **DEPENDENTS:** T-34 `ActorId`, T-37 `ActorState`, T-28 `LogicalTime`, T-40 `RunnableQueue`, T-49 `EventLog`, T-48 `Snapshot`
- **FORBIDDEN_VARIANTS:**
    - `GlobalConfig` — the obsolete v0.3 name; C-42
    - `machine state` — unqualified — `Σ` and the 7-tuple also claim it, X-18
    - `world state`
    - `global config`
- **PROTECTED (do not rename):**
    - `GlobalState` — frozen Rust type name
    - `G` — frozen mathematical symbol (turn [15]/[16] transition rules)
    - `GlobalConfig` — the v0.3 name (L8653, L11061) — superseded, retained in supersession notes (C-42)
    - `Σ` — the turn-[2] machine-configuration symbol `⟨P,ρ,κ,ℋ,φ,𝓔⟩` (L718) — superseded, retained (X-18)
    - `actors` — frozen field name
    - `logical_time` — frozen field name
    - `runnable` — frozen field name
    - `event_log` — frozen field name
    - `SchedulerState` — a component named in the source whose shape is never given (U-02)
- **FROZEN SHAPE:** `pub struct GlobalState { actors, logical_time, runnable, event_log, next_effect_id, next_actor_id }`
- **OBLIGATIONS:** `R-ACTOR-02`, `R-PERSIST-04`, `R-CORE-08`
- **SECTIONS:** `S-15`, `S-18`
- **COLLISIONS:** [X-18](02-collisions.md#x-18), [X-46](02-collisions.md#x-46)
- **NOTE:** No canonical byte encoding is frozen for `GlobalState` (C-15, U-02), yet R-PERSIST-04/05 require one.

### T-70 — `Fault`

- **CANONICAL_TERM:** `Fault`
- **TYPE:** RUST-ENUM — a Rust `enum` declaration (closed variant set)
- **OWNER:** MOD-01 (`ror-core`)
- **DEFINITION:** The machine-visible fault taxonomy: the payload of `StepResult::Fault(Fault)`, `ActorStatus::Fault(Fault)` and `MachineEvent::Fault(Fault)`, and the value the differential observer compares (R-REF-05). `pub enum Fault` is declared seven times across the 60 turns with differing variant sets; the frozen turn-[30] form names eight variants behind an explicit `// ... (previous faults)` elision, so the source never closes the set. Distinct from `GlobalFault` (the parallel global-machine taxonomy), `RecoveryFault`, `HostFault`, `MarshalFault` and `ObservedFault` (the 15C.46 differential record).
- **FIRST_DEFINITION:** `L1009`, turn [3] — `Fault(Fault),         // Unhandled Fault (Rule 15)`
- **FROZEN_AT:** `L23806`, turn [30] — `pub enum Fault {`
- **DEPENDENTS:** T-35 `ActorStatus`, T-36 `RunState`, T-71 `GlobalFault`, T-72 `CapabilityError`, T-73 `MarshalFault`, T-74 `HostFault`
- **FORBIDDEN_VARIANTS:**
    - `fault` — lowercase — the `fault(…)` form C-08 cites occurs nowhere
    - `Faulted` — that is the `RunState` variant, X-23
    - `error / failure` — unqualified — four distinct `*Error`/`*Fault` types exist
    - `GlobalFault` — parallel taxonomy for the global machine, T-71
- **PROTECTED (do not rename):**
    - `Fault` — frozen Rust enum name — SEVEN declarations (L10882, L17788, L18125, L22415, L23319, L23806, L26865)
    - `// ... (previous faults)` — verbatim elision marker at L23807 — the frozen block does not restate earlier variants
    - `Capability` — frozen variant L23808 (turn [30]); also L22430 (turn [29])
    - `CapabilityError` — variant NAME at L20389/L20790/L20538 (turn [28]) — renamed to `Capability` by turn [29] without retraction
    - `CapabilityDenied` — variant name at L26870 (turn [33]) actor-local `Fault`
    - `CapabilityViolation` — denial name L94/L133/L267/L463/L1042/L10456 and v0.3 L8758
    - `CapabilityRevoked` — denial name L937 (with a `CapRef` payload), L3667 (no payload), v0.3 L8721
    - `CapViolation` — v1 fault-grammar name L1949 — distinct from `CapabilityViolation`
    - `Revoked` — v1 fault-grammar name L1949 — distinct from `CapabilityError::Revoked`
    - `AuthorizationFailed` — v0.3 denial name L7374
    - `ScopeViolation` — v1 denial name L944/L1949 — no later counterpart
    - `BudgetExhausted` — frozen variant L23809; also in the v1 grammar L1949
    - `DeadlineExceeded` — frozen variant L23810
    - `HostPolicyDenied` — frozen variant L23811 — payload type split (X-58)
    - `HostPolicyViolation` — variant name L10885 (turn [18]) and v0.3 L8758
    - `EffectCanonicalization` — frozen variant L23812
    - `Host` — frozen variant L23813, carrying `HostFault` (T-74)
    - `ReplayCorruption` — frozen variant L23814 — also a `HostFault` path (X-67)
    - `InvalidReceipt` — frozen variant L23815
    - `IsolationBreach` — v1 grammar L1949 and receipt-mismatch conclusion L2024/L7223/L8766
    - `StalePlan` — source-used fault name: `Fault::StalePlan` at L28373 (turn [36]) and a bare token at L27236 (turn [33]) — declared by none of the seven `Fault` enums (X-64, X-69)
    - `AuthoritySuspended` — source-used `Fault::` path L941 (turn [3]) — in no declaration (X-69)
    - `FuelExhausted` — source-used `Fault::` path L1018 (turn [3]) — the declared name is `BudgetExhausted` (X-69)
    - `AncestorRevoked` — source-used `Fault::` path L6705 (turn [11]) — near-synonym of `Revoked` in the same list (X-69)
    - `Unauthorized` — source-used `Fault::` path L6706 (turn [11]) — a third name for the same denial (X-69)
    - `ReservedCapacityExceeded` — source-used `Fault::` path L10466-10467 (turn [18]) — in no declaration (X-69)
    - `NoSuchActor` — source-used `Fault::` path L25714 (turn [32]) — in no declaration (X-69)
    - `UnknownActor` — source-used `Fault::` path L26017 (turn [32]) — a second name for `NoSuchActor`, 303 lines later (X-69)
- **FROZEN SHAPE:** `pub enum Fault {
    // ... (previous faults)
    Capability(CapabilityError),
    BudgetExhausted,
    DeadlineExceeded,
    HostPolicyDenied(HostPolicyError),
    EffectCanonicalization(EffectError),
    Host(HostFault),
    ReplayCorruption, // ID or Digest mismatch
    InvalidReceipt,
}`
- **SUPERSEDES (recorded, not deleted):**
    - `pub enum Fault { …, HostPolicyViolation, … }   // L10882 (turn [18]) — `HostPolicyViolation`, no payload`
    - `let fault = Fault::CapabilityError(error);   // L20389/L20790 (turn [28]) — variant named `CapabilityError``
    - `pub enum Fault { …, CapabilityDenied, MarshalFault(...), HostFault(...), … }   // L26865 (turn [33]) — actor-local set`
- **OBLIGATIONS:** `R-CALC-06`, `R-ACTOR-02`, `R-ACTOR-04`
- **SECTIONS:** `S-07`, `S-15`
- **COLLISIONS:** [X-23](02-collisions.md#x-23), [X-38](02-collisions.md#x-38), [X-58](02-collisions.md#x-58), [X-59](02-collisions.md#x-59), [X-64](02-collisions.md#x-64), [X-65](02-collisions.md#x-65), [X-66](02-collisions.md#x-66), [X-67](02-collisions.md#x-67), [X-68](02-collisions.md#x-68), [X-69](02-collisions.md#x-69), [X-71](02-collisions.md#x-71), [X-73](02-collisions.md#x-73)
- **NOTE:** Nine distinct names are used for capability denial across eras (`CapViolation`, `CapabilityViolation`, `Revoked`, `CapabilityRevoked`, `ScopeViolation`, `AuthorizationFailed`, `Fault::CapabilityError`, `Fault::Capability(CapabilityError)`, `CapabilityDenied`) — X-38. The set is never closed by the source; U-08/U-14 remain open on their merits.

### T-71 — `GlobalFault`

- **CANONICAL_TERM:** `GlobalFault`
- **TYPE:** RUST-ENUM — a Rust `enum` declaration (closed variant set)
- **OWNER:** MOD-05 (`ror-runtime`)
- **DEFINITION:** The fault taxonomy of the GLOBAL machine step, parallel to `Fault`: `global_step(…) -> Result<GlobalStep, GlobalFault>`. Its eight variants cover durable state (`SnapshotCorruption`, `EventLogCorruption`, `EventSequenceGap`, `InvalidRecoveredState`, `EffectReconciliationFailure`, `PersistenceFailure`) and the actor table and scheduler (`ActorTableCorruption`, `SchedulerInvariantViolation`). None of the eight appears in any `Fault` declaration. It is named by no obligation, module or requirement record: R-CALC-06 describes “the frozen `Fault` taxonomy” without it (spec/01 L138, spec/03 L52, mod/01 L155, mod/18 L68), and the only canonicalization-layer mention it has is the one this pass added when it linked the term from `req/03` AMB-08.
- **FIRST_DEFINITION:** `L25576`, turn [32] — `) -> Result<GlobalStep, GlobalFault> {`
- **FROZEN_AT:** `L26885`, turn [33] — `pub enum GlobalFault {`
- **DEPENDENTS:** T-38 `GlobalState`, T-48 `Snapshot`, T-45 `WAL`, T-52 `RecoveryFault`
- **FORBIDDEN_VARIANTS:**
    - `Fault` — as a synonym — disjoint variant sets
    - `global error`
- **PROTECTED (do not rename):**
    - `GlobalFault` — frozen Rust enum name
    - `SnapshotCorruption` — frozen variant L26886
    - `EventLogCorruption` — frozen variant L26887
    - `EventSequenceGap` — frozen variant L26888
    - `InvalidRecoveredState` — frozen variant L26889
    - `EffectReconciliationFailure` — frozen variant L26890
    - `PersistenceFailure` — frozen variant L26891
    - `ActorTableCorruption` — frozen variant L26892
    - `SchedulerInvariantViolation` — frozen variant L26893
- **FROZEN SHAPE:** `pub enum GlobalFault { SnapshotCorruption, EventLogCorruption, EventSequenceGap, InvalidRecoveredState, EffectReconciliationFailure, PersistenceFailure, ActorTableCorruption, SchedulerInvariantViolation }   // L26885-26894, all eight`
- **OBLIGATIONS:** `R-CALC-06`
- **SECTIONS:** `S-07`
- **COLLISIONS:** [X-58](02-collisions.md#x-58)
- **NOTE:** R-CALC-06 (spec/01 L138, spec/03 L52, mod/01 L155, mod/18 L68) describes “the frozen `Fault` taxonomy” without mentioning that a second, disjoint eight-variant taxonomy governs the global machine step.

### T-75 — `MachineEvent`

- **CANONICAL_TERM:** `MachineEvent`
- **TYPE:** RUST-ENUM — a Rust `enum` declaration (closed variant set)
- **OWNER:** MOD-05 (`ror-runtime`)
- **DEFINITION:** The machine's transition-event stream: what a step emits for the trace, and the vocabulary the differential observer and the WAL are built on. Declared eight times with materially different variant sets, three of them behind a `// ...` elision, and used with eight further variant paths that appear in no declaration.
- **FIRST_DEFINITION:** `L14697`, turn [23] — `pub enum MachineEvent {`
- **FROZEN_AT:** `L22002`, turn [29] — `pub enum MachineEvent {`
- **DEPENDENTS:** T-47 `WalRecord`, T-45 `WAL`, T-70 `Fault`, T-35 `ActorStatus`, T-38 `GlobalState`
- **FORBIDDEN_VARIANTS:**
    - `event` — unqualified
    - `GlobalEvent` — a different, also undeclared name
    - `MachineEvents`
- **PROTECTED (do not rename):**
    - `MachineEvent` — frozen Rust enum name — EIGHT declarations (L14697, L15958, L17588, L18104, L18631, L20318, L20724, L22002)
    - `EnterSeq` — declared variant (L14697 onward)
    - `EnterIf` — declared variant
    - `EnterCall` — declared variant (from L15958)
    - `EnterLambda` — declared variant from L15963 (turn [24]) onward
    - `ApplyFunction` — declared variant (from L17588)
    - `PushFrame` — declared variant
    - `PopFrame` — declared variant
    - `Block` — declared variant (L14697) — a `MachineEvent`, not the untrusted `Block` of T-01
    - `EnterAttenuate` — declared variant (L20318, L20724)
    - `DeriveCapability` — declared variant (L20318, L20724); constructed at L20386
    - `Fault` — declared variant; constructed at L20391/L20792 carrying a `Fault`
    - `EffectIssued` — declared variant (L22005) with `{ id, digest }`
    - `EffectCompleted` — declared variant (L22010) with `{ id, digest }`
    - `// ...` — verbatim elision marker at L22003 — the frozen block does not restate earlier variants
    - `EnterRequest` — USED L21483, L23380 — never declared (X-71)
    - `BeginRequestTarget` — USED L21536, L23398 — never declared (X-71)
    - `BeginRequestArgument` — USED L21645, L23426 — never declared (X-71)
    - `Blocked` — USED L25740, L26038 — never declared; the declared name is `Block` (X-71)
    - `Spawned` — USED L25668 — never declared (X-71)
    - `ActorSpawned` — USED L25966 with `{ parent, child }` — never declared; a SECOND name for `Spawned` (X-71)
    - `Sent` — USED L25728 — never declared (X-71)
    - `MessageSent` — USED L26027 with `{ from, to }` — never declared; a SECOND name for `Sent` (X-71)
    - `EnterLet` — declared variant L14698 (turn [23]) and in every later declaration, carrying a `Symbol`
    - `EvaluateValue` — declared variant L14701, carrying a `Value` — ALSO constructed in prose at L17575
    - `Lookup` — declared variant L14702, carrying a `Symbol`
    - `Halt` — declared variant L14705, carrying a `Value` — the same name as `StepResult::Halt` in a different enum (X-73)
    - `BeginArgument` — declared variant from L17596 (turn [25]), carrying a `usize`
    - `EndArgument` — declared variant from L17597 (turn [25]), carrying a `usize`
    - `// ... (Previous events)` — verbatim elision marker at L20319 (turn [28]) — one of three elided declarations
    - `// ... (previous variants)` — verbatim elision marker at L20725 (turn [28]) — note the different capitalisation and noun
- **FROZEN SHAPE:** `pub enum MachineEvent { /* ... */ EffectIssued { id: EffectId, digest: EffectDigest }, EffectCompleted { id: EffectId, digest: EffectDigest } }   // L22002-22014, elided head`
- **OBLIGATIONS:** `R-CORE-08`, `R-ACTOR-07`
- **SECTIONS:** `S-07`, `S-15`
- **COLLISIONS:** [X-71](02-collisions.md#x-71)
- **NOTE:** Absent from the dictionary until the declaration sweep: the event vocabulary that the trace, the WAL and the differential comparison are all built on had no term of record, and no register entry counted its declarations.

### T-77 — `StepResult`

- **CANONICAL_TERM:** `StepResult`
- **TYPE:** RUST-ENUM — a Rust `enum` declaration (closed variant set)
- **OWNER:** MOD-05 (`ror-runtime`)
- **DEFINITION:** TWO DISJOINT ENUMS SHARE THIS NAME. (1) The CEK machine's single-step outcome (L1006, turn [3]): `Continue | Halt(Value) | Fault(Fault) | YieldToHost(Effect)` — one actor, one reduction, no identity carried. (2) The actor scheduler's step outcome (L9586, turn [17], restated L10397 and L10947): `Progressed | Blocked(ActorId) | Pending(ActorId, EffectRequest) | Halted(ActorId, Value) | Faulted(ActorId, Fault) | NoRunnableActors` — every variant carries an `ActorId`. They are not two versions of one type: they belong to different layers and have no variant in common.
- **FIRST_DEFINITION:** `L1006`, turn [3] — `pub enum StepResult {`
- **FROZEN_AT:** `L9586`, turn [17] — `pub enum StepResult {`
- **DEPENDENTS:** T-70 `Fault`, T-35 `ActorStatus`, T-36 `RunState`, T-34 `ActorId`, T-32 `EvalState`
- **FORBIDDEN_VARIANTS:**
    - `step result` — unqualified — two disjoint enums exist
    - `StepOutcome`
    - ``using the scheduler's `Faulted`` — ActorId, Fault)` where the machine's `Fault(Fault)` is meant (X-23, X-73
- **PROTECTED (do not rename):**
    - `StepResult` — frozen Rust enum name — FOUR declarations (L1006, L9586, L10397, L10947) in two disjoint families
    - `Continue` — machine variant L1007
    - `Halt` — machine variant L1008, carrying a `Value`
    - `Fault` — machine variant L1009, carrying a `Fault`
    - `YieldToHost` — machine variant L1010, carrying an `Effect`
    - `Progressed` — scheduler variant L9587
    - `Blocked` — scheduler variant L9588, carrying an `ActorId` — ALSO an `ActorStatus` and a `RunState` variant (X-21)
    - `Pending` — scheduler variant L9589, carrying `(ActorId, EffectRequest)`
    - `Halted` — scheduler variant L9590, carrying `(ActorId, Value)`
    - `Faulted` — scheduler variant L9591, carrying `(ActorId, Fault)` — ALSO a `RunState` variant (X-23)
    - `NoRunnableActors` — scheduler variant L9592
- **FROZEN SHAPE:** `pub enum StepResult { Continue, Halt(Value), Fault(Fault), YieldToHost(Effect) }   // L1006, machine
pub enum StepResult { Progressed, Blocked(ActorId), Pending(ActorId, EffectRequest), Halted(ActorId, Value), Faulted(ActorId, Fault), NoRunnableActors }   // L9586, scheduler`
- **OBLIGATIONS:** `R-CEK-01`, `R-ACTOR-04`
- **SECTIONS:** `S-07`, `S-15`
- **COLLISIONS:** [X-73](02-collisions.md#x-73), [X-74](02-collisions.md#x-74)
- **NOTE:** The machine/scheduler split is the same shape as the `Observation` split (X-06), which the request's own term list forced into two canonical terms; here the source gives no second name, so both are recorded under one entry with the homonymy filed as X-73 rather than resolved by renaming.

### T-78 — `ControlFrame`

- **CANONICAL_TERM:** `ControlFrame`
- **TYPE:** RUST-ENUM — a Rust `enum` declaration (closed variant set)
- **OWNER:** MOD-05 (`ror-runtime`)
- **DEFINITION:** The CEK machine's control stack frame: what `self.control` holds between reductions. Declared once, behind an elision, with three visible variants — and used with two variant paths that appear in no declaration. Its declared variants reference `PlanIR`, `FuncRef` and `EffectSignature`, none of which is declared anywhere either.
- **FIRST_DEFINITION:** `L985`, turn [3] — `pub enum ControlFrame {`
- **DEPENDENTS:** T-32 `EvalState`, T-30 `Expr`, T-31 `Value`, T-77 `StepResult`
- **FORBIDDEN_VARIANTS:**
    - `control frame` — unqualified
    - `ControlStack`
    - `Frame` — that is T-33, a distinct declared enum
- **PROTECTED (do not rename):**
    - `ControlFrame` — frozen Rust enum name — the ONLY declaration (L985, turn [3])
    - `EvaluateSequence` — declared variant L986, carrying `{ remaining: Vec<PlanIR> }`
    - `AwaitInvoke` — declared variant L987, carrying `{ func: FuncRef, args: Vec<Value> }`
    - `AwaitHostFFI` — declared variant L988, carrying `{ effect: EffectSignature }`
    - `// ...` — verbatim elision marker at L989
    - `ReduceIR` — USED L1031 and matched at L1035 — never declared (X-75)
    - `ResumeWithResult` — USED L1282 — never declared (X-75)
- **FROZEN SHAPE:** `pub enum ControlFrame { EvaluateSequence { remaining: Vec<PlanIR> }, AwaitInvoke { func: FuncRef, args: Vec<Value> }, AwaitHostFFI { effect: EffectSignature }, /* ... */ }   // L985-990`
- **OBLIGATIONS:** `R-CEK-01`
- **SECTIONS:** `S-07`
- **COLLISIONS:** [X-75](02-collisions.md#x-75)
- **NOTE:** Distinct from `Frame` (T-33), which is declared eleven times and is the evaluation frame of the frozen turn-[30] machine; the two names are not interchangeable and the source uses both.

---

## CONCURRENCY — Actors, status, mailboxes, marshalling
Owning module: **MOD-06**.

### T-34 — `ActorId`
*Required term.*

- **CANONICAL_TERM:** `ActorId`
- **TYPE:** RUST-NEWTYPE — a Rust single-field tuple `struct` wrapper
- **OWNER:** MOD-06 (`ror-core (type); ror-runtime (allocation)`)
- **DEFINITION:** The identity of an actor: `pub struct ActorId(pub u64)`, allocated from `GlobalState.next_actor_id`, given 15A standalone tag `0x40`, and used as the ordering key for deterministic snapshot serialization. An `ActorId` is a name, not an actor: the actor is `ActorState`.
- **FIRST_DEFINITION:** `L9127`, turn [17] — `pub type ActorId = u64;`
- **FROZEN_AT:** `L10669`, turn [18] — `pub struct ActorId(pub u64);`
- **DEPENDENTS:** T-37 `ActorState`, T-38 `GlobalState`, T-35 `ActorStatus`
- **FORBIDDEN_VARIANTS:**
    - `actor handle`
    - `actor reference` — that is `ActorRef`, a value
    - `pid`
    - `agent id`
- **PROTECTED (do not rename):**
    - `ActorId` — frozen type name; 15A standalone tag `0x40`
    - `N_a` — frozen mathematical symbol for the actor-id counter (L24249)
    - `next_actor_id` — frozen `GlobalState` field name
    - `a` — frozen mathematical symbol for the acting actor in `G --a,c--> G'`
    - `ActorRef` — frozen `Value` variant / spawn result type — distinct from `ActorId`
- **FROZEN SHAPE:** `pub struct ActorId(pub u64);`
- **SUPERSEDES (recorded, not deleted):**
    - `pub type ActorId = u64;   // L9127 (turn [17]), L10184 (turn [18])`
- **OBLIGATIONS:** `R-ACTOR-01`, `R-ACTOR-02`, `R-CANON-04`
- **SECTIONS:** `S-15`, `S-17`
- **COLLISIONS:** [X-24](02-collisions.md#x-24)
- **NOTE:** Same alias-vs-newtype collision as `EffectId`; 15A tag `0x40` requires nominal distinctness (X-24).

### T-35 — `ActorStatus`
*Required term.*

- **CANONICAL_TERM:** `ActorStatus`
- **TYPE:** RUST-ENUM — a Rust `enum` declaration (closed variant set)
- **OWNER:** MOD-06 (`ror-runtime`)
- **DEFINITION:** The MACHINE-visible status of an actor: `Running | Pending | Blocked | Halted | Fault`. In the frozen turn-[30] form `Pending` carries `{ effect_id, effect, reservation }` and the continuation stays in `actor.eval.continuation`; `Blocked` is a unit variant meaning blocked on `Receive`. `ActorStatus` is NOT `RunState`: the scheduler never sees `Runnable` here.
- **FIRST_DEFINITION:** `L9411`, turn [17] — `pub enum ActorStatus {`
- **FROZEN_AT:** `L23793`, turn [30] — `pub enum ActorStatus {`
- **DEPENDENTS:** T-36 `RunState`, T-37 `ActorState`, T-18 `EffectIssued`, T-26 `Reserved`
- **FORBIDDEN_VARIANTS:**
    - `status` — unqualified — two distinct enums exist
    - `RunState` — as a synonym
    - `actor state` — that is `ActorState`, the whole record
    - `run state`
- **PROTECTED (do not rename):**
    - `ActorStatus` — frozen Rust enum name
    - `status` — frozen `ActorState`/`A_a` field name carrying an `ActorStatus`
    - `Running` — frozen variant
    - `Pending` — frozen variant — ALSO a `RunState` variant (distinct enum)
    - `Blocked` — frozen variant — ALSO a `RunState` variant
    - `Halted` — frozen variant — ALSO a `RunState` variant
    - `Fault` — frozen `ActorStatus` variant (carries a `Fault`)
    - `PendingEffect` — frozen turn-[17] struct `{id, effect, continuation}` — superseded payload of `Pending` (X-22)
    - `reservation` — frozen field of the turn-[30] `Pending` variant
- **FROZEN SHAPE:** `pub enum ActorStatus { Running, Pending { effect_id, effect, reservation }, Blocked, Halted(Value), Fault(Fault) }`
- **SUPERSEDES (recorded, not deleted):**
    - `pub enum ActorStatus { Running, Pending(PendingEffect), Blocked(Continuation), Halted(Value), Fault(Fault) }   // L9411 (turn [17])`
- **OBLIGATIONS:** `R-ACTOR-02`, `R-ACTOR-04`, `R-CALC-06`
- **SECTIONS:** `S-15`, `S-07`
- **COLLISIONS:** [X-21](02-collisions.md#x-21), [X-22](02-collisions.md#x-22), [X-23](02-collisions.md#x-23), [X-38](02-collisions.md#x-38), [X-58](02-collisions.md#x-58), [X-65](02-collisions.md#x-65), [X-71](02-collisions.md#x-71), [X-73](02-collisions.md#x-73), [X-74](02-collisions.md#x-74)
- **LAWS:** [N-15](03-laws.md#n-15)
- **NOTE:** SEVEN declarations in THREE shapes (X-74), not the two X-21 records. Shape (i) L9411/L10346 (turns [17]/[18]): `Pending(PendingEffect), Blocked(Continuation)` — the continuation inside `Blocked`. Shape (ii) L21234 (turn [29]): `Pending { effect: EffectRequest, continuation: Continuation, reservation: ReservedCapacity }, Blocked(Continuation)` — the continuation in BOTH variants. Shape (iii) L23306/L23793 (turn [30]): `Pending { effect: EffectRequest, reservation: ReservedCapacity }, Blocked` — the continuation in NEITHER, which is the form the frozen turn-[30] machine assumes when it keeps the continuation in `actor.eval.continuation` (T-37, T-32). X-21 covers the `Running`/`Active` naming split, X-74 the shape split and the seven-declaration count; C-18/AMB-05 cover `ActorStatus` vs `RunState`, not either split.

### T-37 — `ActorState`

- **CANONICAL_TERM:** `ActorState`
- **TYPE:** RUST-STRUCT — a Rust `struct` declaration (nominal type)
- **OWNER:** MOD-06 (`ror-runtime`)
- **DEFINITION:** The actor-local state record: `{ id: ActorId, run_state: RunState, eval: EvalState, capabilities: CapabilityContext, budget: Budget, mailbox: Mailbox, status: ActorStatus, ... }`. Actors isolate environments, continuations, heaps, mailboxes, budgets and capability contexts. Mathematically `A_a = ⟨e, ρ, κ, ℋ, C, R, W, mailbox, status⟩`.
- **FIRST_DEFINITION:** `L8111`, turn [15] — `ActorState=`
- **FROZEN_AT:** `L25544`, turn [32] — `pub struct ActorState {`
- **DEPENDENTS:** T-34 `ActorId`, T-35 `ActorStatus`, T-36 `RunState`, T-32 `EvalState`, T-14 `CapabilityContext`, T-24 `Budget`, T-39 `Mailbox`
- **FORBIDDEN_VARIANTS:**
    - `agent state`
    - `actor`
    - `A` — unqualified — `A` is Authority
- **PROTECTED (do not rename):**
    - `ActorState` — frozen Rust type name
    - `A_a` — frozen mathematical symbol for actor a's state (L8666)
    - `A_A` — the turn-[1] notation for actor A's state (L340) — superseded
    - `id` — frozen field name
    - `run_state` — frozen field name
    - `eval` — frozen field name
    - `capabilities` — frozen field name
    - `budget` — frozen field name
    - `mailbox` — frozen field name
    - `ℋ` — frozen symbol for the actor's isolated heap/arena
- **FROZEN SHAPE:** `A_a = ⟨e, ρ, κ, ℋ, C, R, W, mailbox, status⟩   // L8666, turn [16]`
- **OBLIGATIONS:** `R-ACTOR-01`, `R-ACTOR-02`, `R-ACTOR-03`, `R-PERSIST-04`
- **SECTIONS:** `S-15`
- **COLLISIONS:** [X-11](02-collisions.md#x-11), [X-14](02-collisions.md#x-14), [X-18](02-collisions.md#x-18), [X-74](02-collisions.md#x-74)
- **NOTE:** In `A_a`'s own definition the symbols `C` and `R` are the BUDGET components, while `A` elsewhere is AUTHORITY (X-11, X-08, X-09). The dictionary requires qualified prose: 'the actor state A_a' vs 'the authority A'.

### T-39 — `Mailbox`

- **CANONICAL_TERM:** `Mailbox`
- **TYPE:** CONCEPT — a defined architectural concept with no single declaration
- **OWNER:** MOD-06 (`ror-runtime`)
- **DEFINITION:** The per-actor FIFO of `MarshalledValue`s. A `Send` is asynchronous and enqueues; a `Receive` blocks the actor when the mailbox is empty. Ordinary marshalling recursively rejects capabilities, so a mailbox can never carry raw authority.
- **FIRST_DEFINITION:** `L8666`, turn [16] — `mailbox`
- **DEPENDENTS:** T-37 `ActorState`, T-15 `DelegatedCapability`, T-36 `RunState`
- **FORBIDDEN_VARIANTS:**
    - `queue` — unqualified — `RunnableQueue` is a different FIFO
    - `inbox`
    - `message buffer`
- **PROTECTED (do not rename):**
    - `Mailbox` — frozen name
    - `mailbox` — frozen `ActorState` field name and `A_a` component symbol
    - `MarshalledValue` — frozen element type (canonical bytes transport)
    - `RunnableQueue` — frozen DISTINCT FIFO — the scheduler's queue, not a mailbox
    - `Deadlock` — frozen condition detected when all actors block (L25579)
- **OBLIGATIONS:** `R-ACTOR-03`, `R-ACTOR-06`, `R-MARSHAL-01`, `R-MARSHAL-03`
- **SECTIONS:** `S-15`, `S-16`
- **COLLISIONS:** [X-45](02-collisions.md#x-45)
- **LAWS:** [N-30](03-laws.md#n-30)
- **NOTE:** No canonical byte encoding is frozen for `Mailbox` (C-15, U-02).

### T-73 — `MarshalFault`

- **CANONICAL_TERM:** `MarshalFault`
- **TYPE:** RUST-ENUM — a Rust `enum` declaration (closed variant set)
- **OWNER:** MOD-06 (`ror-runtime`)
- **DEFINITION:** The fault produced when marshalling a value across an actor boundary fails. Declared twice with COMPLETELY DISJOINT variant sets, and used as an elided `Fault` payload (`MarshalFault(...)`) in the turn-[33] actor-local taxonomy.
- **FIRST_DEFINITION:** `L10846`, turn [18] — `pub enum MarshalFault {`
- **FROZEN_AT:** `L25983`, turn [32] — `pub enum MarshalFault {`
- **DEPENDENTS:** T-35 `ActorStatus`, T-70 `Fault`
- **FORBIDDEN_VARIANTS:**
    - `marshalling error`
    - `MarshalError`
- **PROTECTED (do not rename):**
    - `MarshalFault` — frozen Rust enum name — TWO declarations
    - `CapabilityNotTransferable` — variant of the turn-[18] declaration (L10847)
    - `InvalidFormat` — variant of the turn-[18] declaration (L10848)
    - `CapabilityRequiresDelegation` — variant of the turn-[32] declaration (L25984) — the one mod/06 L62/L103 and REQ-MARSHAL cite
    - `SerializationError` — variant of the turn-[32] declaration (L25985)
    - `CorruptedPayload` — source-used `MarshalFault::` path L25694 (turn [32]) — in neither declaration (X-65, X-75)
- **FROZEN SHAPE:** `pub enum MarshalFault { CapabilityRequiresDelegation, SerializationError }   // L25983 (turn [32])`
- **SUPERSEDES (recorded, not deleted):**
    - `pub enum MarshalFault { CapabilityNotTransferable, InvalidFormat }   // L10846 (turn [18])`
- **OBLIGATIONS:** `R-MARSHAL-01`, `R-MARSHAL-02`
- **SECTIONS:** `S-16`
- **COLLISIONS:** [X-65](02-collisions.md#x-65), [X-75](02-collisions.md#x-75)
- **NOTE:** Zero variants are shared between the two declarations (X-65).

---

## SCHEDULING — Deterministic scheduling state
Owning module: **MOD-07**.

### T-36 — `RunState`

- **CANONICAL_TERM:** `RunState`
- **TYPE:** RUST-ENUM — a Rust `enum` declaration (closed variant set)
- **OWNER:** MOD-07 (`ror-runtime`)
- **DEFINITION:** The SCHEDULER-visible run state of an actor: `Runnable | Running | Pending | Blocked | Halted | Faulted`, held as `ActorState.run_state`. `Runnable` means membership in the `RunnableQueue` (at-most-once). `RunState` is not `ActorStatus`; the mapping between them is implied by the source but never tabulated (C-18).
- **FIRST_DEFINITION:** `L24299`, turn [31] — `pub enum RunState {`
- **FROZEN_AT:** `L25526`, turn [32] — `pub enum RunState {`
- **DEPENDENTS:** T-35 `ActorStatus`, T-37 `ActorState`, T-40 `RunnableQueue`
- **FORBIDDEN_VARIANTS:**
    - `status` — unqualified
    - `ActorStatus` — as a synonym
    - `scheduler state` — that is `SchedulerState`, U-02
- **PROTECTED (do not rename):**
    - `RunState` — frozen Rust enum name
    - `run_state` — frozen `ActorState` field name
    - `Runnable` — frozen variant — exists ONLY here, not in `ActorStatus`
    - `Faulted` — frozen variant — note the spelling differs from `ActorStatus::Fault` (X-23); neither is renamed
    - `NotRunnable` — declared variant L24300 (turn [31]) — silently absent from the L25526 (turn [32]) re-declaration, no supersession note (X-75)
- **OBLIGATIONS:** `R-ACTOR-02`, `R-ACTOR-04`, `R-ACTOR-07`
- **SECTIONS:** `S-15`
- **COLLISIONS:** [X-21](02-collisions.md#x-21), [X-23](02-collisions.md#x-23), [X-58](02-collisions.md#x-58), [X-73](02-collisions.md#x-73), [X-75](02-collisions.md#x-75)
- **LAWS:** [N-15](03-laws.md#n-15)
- **NOTE:** Both enums are kept by the frozen text (C-18, INFO). The dictionary separates their ownership: ACTOR vs SCHEDULER.

### T-40 — `RunnableQueue`

- **CANONICAL_TERM:** `RunnableQueue`
- **TYPE:** CONCEPT — a defined architectural concept with no single declaration
- **OWNER:** MOD-07 (`ror-runtime`)
- **DEFINITION:** The scheduler's FIFO of runnable actors with at-most-once membership: an actor is enqueued when it becomes `Runnable` and a duplicate runnable entry is a defect (mutation M014). The baseline scheduler grants one CEK transition per actor turn; blocked actors are never scheduled.
- **FIRST_DEFINITION:** `L25538`, turn [32] — `pub runnable: RunnableQueue,`
- **DEPENDENTS:** T-36 `RunState`, T-38 `GlobalState`
- **FORBIDDEN_VARIANTS:**
    - `run queue`
    - `scheduler queue` — acceptable prose, not a type name
    - `mailbox`
    - `ready set`
- **PROTECTED (do not rename):**
    - `RunnableQueue` — frozen Rust type name
    - `runnable` — frozen `GlobalState` field name
    - `Runnable` — frozen `RunState` variant
    - `ActorSelected` — frozen event name for a turn grant (L25567)
    - `Scheduler` — frozen component name; trust-table row 'Deterministic interleaving' (C-37)
- **OBLIGATIONS:** `R-ACTOR-04`, `R-ACTOR-07`, `R-CORE-08`
- **SECTIONS:** `S-15`
- **COLLISIONS:** —
- **LAWS:** [N-30](03-laws.md#n-30)
- **NOTE:** The snapshot is said to contain the runnable queue while recovery reconstructs it from actor states (C-26, U-17): which is authoritative on mismatch is undecided.

---

## HOST — Live host gate and ordered replay
Owning module: **MOD-09**.

### T-41 — `HostPolicy`
*Required term.*

- **CANONICAL_TERM:** `HostPolicy`
- **TYPE:** RUST-TRAIT — a Rust `trait` (API contract)
- **OWNER:** MOD-09 (`ror-host`)
- **DEFINITION:** The host-side policy gate, deliberately separate from the capability kernel: an independent defence-in-depth check that the concrete host is willing to perform this effect. Machine step 11 fails early on it (`HostPolicyOK(E)`), and the host's own check remains authoritative. A denial is `Fault::HostPolicyDenied(HostPolicyError)`.
- **FIRST_DEFINITION:** `L10163`, turn [18] — `pub trait HostPolicy {`
- **FROZEN_AT:** `L21893`, turn [29] — `pub trait HostPolicy {`
- **DEPENDENTS:** T-16 `Effect`, T-17 `EffectRequest`, T-43 `LiveHost`
- **FORBIDDEN_VARIANTS:**
    - `capability check` — that is the kernel's `Authorized`
    - `authorization` — unqualified — `Authorized` is the kernel predicate
    - `permission check`
    - `security policy`
- **PROTECTED (do not rename):**
    - `HostPolicy` — frozen trait name
    - `is_permitted` — frozen method of the turn-[18] form, `-> bool` (L10164)
    - `authorize` — frozen method of the turn-[29] form, `-> Result<(), HostPolicyError>` (L21894) — see X-20
    - `HostPolicyOK(E)` — frozen predicate, Gate 3 of E-Request (L8733) and a conjunct of the central theorem
    - `HostPolicyError` — frozen error type (variants never enumerated, U-14)
    - `HostPolicyDenied` — frozen `Fault` variant (L23811)
    - `HostPolicyViolation` — the v0.3 rule's fault name (L8748-8757, L8925) — unreconciled with `HostPolicyDenied` (AMB-08)
    - `HostAuthorized(E)` — the turn-[7]/[13] predicate name for the same gate (L3297, L7103)
- **FROZEN SHAPE:** `pub trait HostPolicy { fn authorize(&self, effect: &Effect) -> Result<(), HostPolicyError> }`
- **SUPERSEDES (recorded, not deleted):**
    - `pub trait HostPolicy { fn is_permitted(&self, effect: &Effect) -> bool }   // L10163`
- **OBLIGATIONS:** `R-HOST-01`, `R-CORE-02`, `R-EFFECT-03`
- **SECTIONS:** `S-14`, `S-12`
- **COLLISIONS:** [X-20](02-collisions.md#x-20), [X-38](02-collisions.md#x-38), [X-58](02-collisions.md#x-58), [X-59](02-collisions.md#x-59), [X-67](02-collisions.md#x-67)
- **LAWS:** [N-25](03-laws.md#n-25)
- **NOTE:** The two forms are not equivalent: `-> bool` cannot distinguish 'denied' from 'policy error', so it cannot produce `HostPolicyError`. X-20 reports this; the dictionary records both and requires an explicit decision.

### T-42 — `ReplayHost`
*Required term.*

- **CANONICAL_TERM:** `ReplayHost`
- **TYPE:** RUST-STRUCT — a Rust `struct` declaration (nominal type)
- **OWNER:** MOD-09 (`ror-host`)
- **DEFINITION:** The recorded-effect host: an ordered trace of `EffectReceipt`s consumed by a cursor, which NEVER touches the external world and validates each request's id and digest against the next trace entry. Trusted (R-TRUST-01). An unordered map is explicitly not the normative replay mechanism.
- **FIRST_DEFINITION:** `L1234`, turn [3] — `pub struct ReplayHost {`
- **FROZEN_AT:** `L34498`, turn [46] — `pub struct ReplayHost {`
- **DEPENDENTS:** T-19 `EffectReceipt`, T-17 `EffectRequest`, T-21 `EffectDigest`, T-44 `HostExecutor`
- **FORBIDDEN_VARIANTS:**
    - `recorded host`
    - `mock host` — that is `PanicHost`/test doubles, a different object
    - `replay cache`
    - `receipt map`
- **PROTECTED (do not rename):**
    - `ReplayHost` — frozen Rust type name; trust-table row
    - `trace` — frozen field name of the ordered form
    - `cursor` — frozen field name
    - `recorded_receipts` — field name of the superseded `HashMap` form (L24012) — retained, not renamed (C-22)
    - `HostFault::ReplayTraceExhausted` — frozen fault variant
    - `ReplayCorruption` — frozen `Fault` variant for id/digest mismatch
- **FROZEN SHAPE:** `pub struct ReplayHost { trace: Vec<EffectReceipt>, cursor: usize }`
- **SUPERSEDES (recorded, not deleted):**
    - `pub struct ReplayHost { recorded_receipts: HashMap<EffectId, EffectReceipt>, cursor: usize }   // L24011 (turn [30]) — C-22`
- **OBLIGATIONS:** `R-HOST-03`, `R-HOST-04`, `R-EFFECT-06`
- **SECTIONS:** `S-14`
- **COLLISIONS:** [X-43](02-collisions.md#x-43), [X-67](02-collisions.md#x-67)
- **LAWS:** [N-26](03-laws.md#n-26)
- **NOTE:** C-22 resolves HashMap→ordered; X-43 records that the field name also changed (`recorded_receipts`→`trace`).

### T-43 — `LiveHost`

- **CANONICAL_TERM:** `LiveHost`
- **TYPE:** RUST-STRUCT — a Rust `struct` declaration (nominal type)
- **OWNER:** MOD-09 (`ror-host`)
- **DEFINITION:** The external-world host adapter that actually invokes the OS/network. It is PARTIALLY trusted (R-TRUST-01): it may perform the effect, but it never decides authorization, never sees `Authority`, and is invoked only after durable issuance.
- **FIRST_DEFINITION:** `L1191`, turn [3] — `pub struct LiveHost {`
- **DEPENDENTS:** T-17 `EffectRequest`, T-19 `EffectReceipt`, T-41 `HostPolicy`, T-44 `HostExecutor`
- **FORBIDDEN_VARIANTS:**
    - `host` — unqualified — three hosts exist
    - `OS adapter`
    - `syscall layer`
    - `real host`
- **PROTECTED (do not rename):**
    - `LiveHost` — frozen Rust type name; trust-table row 'Live host / Partial'
    - `HostExecutor` — frozen trait both hosts implement
    - `Host` — frozen `Fault` variant carrying a `HostFault`
    - `HostFault` — frozen error type (variants undefined, U-14)
    - `HostInvoked(E)` — frozen predicate in the durability invariant
- **OBLIGATIONS:** `R-HOST-01`, `R-HOST-02`, `R-CORE-06`, `R-TRUST-01`
- **SECTIONS:** `S-14`
- **COLLISIONS:** —
- **LAWS:** [N-26](03-laws.md#n-26)
- **NOTE:** Three hosts must never be conflated: `LiveHost` (external world, partial trust), `ReplayHost` (recorded, trusted), and the test doubles `PanicHost`/`MockKernel` (infrastructure, MOD-17).

### T-44 — `HostExecutor`

- **CANONICAL_TERM:** `HostExecutor`
- **TYPE:** RUST-TRAIT — a Rust `trait` (API contract)
- **OWNER:** MOD-09 (`ror-host`)
- **DEFINITION:** The host boundary contract: `fn execute(&mut self, request: &EffectRequest) -> Result<EffectReceipt, HostFault>`. It is the single seam at which the machine meets the external world, and therefore the seam the live/replay distinction is drawn across.
- **FIRST_DEFINITION:** `L1187`, turn [3] — `pub trait HostExecutor {`
- **DEPENDENTS:** T-17 `EffectRequest`, T-19 `EffectReceipt`, T-42 `ReplayHost`, T-43 `LiveHost`
- **FORBIDDEN_VARIANTS:**
    - `host trait`
    - `host interface`
    - `FFI boundary`
- **PROTECTED (do not rename):**
    - `HostExecutor` — frozen trait name
    - `execute` — frozen method name
- **OBLIGATIONS:** `R-HOST-01`, `R-HOST-02`, `R-HOST-03`
- **SECTIONS:** `S-14`
- **COLLISIONS:** [X-67](02-collisions.md#x-67)

### T-74 — `HostFault`

- **CANONICAL_TERM:** `HostFault`
- **TYPE:** RUST-ENUM — a Rust `enum` declaration (closed variant set)
- **OWNER:** MOD-09 (`ror-host`)
- **DEFINITION:** The error type of the host boundary and of ordered replay: the payload of the frozen `Fault::Host(HostFault)` variant and the `Err` arm of `HostExecutor::execute`/`ReplayHost`. Declared ONCE, with two variants, while eight distinct variant paths are used in the source — six of them on the frozen replay path that R-HOST-03/04/05 and REQ-HOST-008 depend on.
- **FIRST_DEFINITION:** `L10820`, turn [18] — `pub enum HostFault {`
- **DEPENDENTS:** T-42 `ReplayHost`, T-44 `HostExecutor`, T-41 `HostPolicy`, T-70 `Fault`
- **FORBIDDEN_VARIANTS:**
    - `HostError`
    - `host fault` — unqualified
    - `HostFault as a fault NAME` — the v1 grammar L1949 uses `HostFault` as a member of `F`, i.e. as a fault, not as a type — X-68
- **PROTECTED (do not rename):**
    - `HostFault` — frozen Rust enum name — the ONLY declaration (L10820, turn [18])
    - `IoError(String)` — declared variant L10821
    - `PolicyViolation(String)` — declared variant L10822
    - `Io` — USED L1210/L1216 — never declared; near-miss of `IoError` (X-67)
    - `ConcreteScopeViolation` — USED L1208/L1214 — never declared (X-67)
    - `UnboundCapability` — USED L1203 — never declared (X-67)
    - `ReplayTraceExhausted` — USED 6× (L1245, L24020, L25496, L25838, L34519, L35225) — never declared (X-67)
    - `ReplayCorruption` — USED 6× (L25500, L25841, L34522, L34528, L35226, L35227) — never declared; ALSO a `Fault` variant (L23814) (X-67)
    - `TraceExhausted` — USED L10546 — never declared; a third name for the same condition (X-67)
    - `ReplayIdMismatch` — USED L10550 — never declared (X-67)
    - `ReplayDigestMismatch` — USED L10553 — never declared (X-67)
- **FROZEN SHAPE:** `pub enum HostFault { IoError(String), PolicyViolation(String) }   // L10820 — the only declaration`
- **OBLIGATIONS:** `R-HOST-03`, `R-HOST-04`, `R-HOST-05`
- **SECTIONS:** `S-14`
- **COLLISIONS:** [X-58](02-collisions.md#x-58), [X-59](02-collisions.md#x-59), [X-67](02-collisions.md#x-67), [X-68](02-collisions.md#x-68)
- **NOTE:** Not one of the eight used variant paths is declared. `ReplayCorruption` is simultaneously a `HostFault` path and a `Fault` variant (L23814), so the same name denotes faults at two different levels of the taxonomy.

---

## PERSISTENCE — Canonical encoding, WAL, snapshots, journal
Owning module: **MOD-11**.

### T-23 — `EffectJournal`
*Required term.*

- **CANONICAL_TERM:** `EffectJournal`
- **TYPE:** CONCEPT — a defined architectural concept with no single declaration
- **OWNER:** MOD-11 (`ror-persistence`)
- **DEFINITION:** The durable CAUSAL record of effect lifecycle: Prepared → Issued → Completed, or Issued → Reconciled, with the causal laws `Issued(E) ⇒ Prepared(E)`, `Completed(E) ⇒ Issued(E)`, `Reconciled(E) ⇒ Issued(E)`. In the frozen 15B model the journal is NOT a separate structure: its records are `WalRecord` kinds inside the WAL. A prepared-but-never-issued effect is discarded; an issued-but-not-completed effect is `Indeterminate`.
- **FIRST_DEFINITION:** `L26134`, turn [33] — `- \(H\) = durable host-effect journal.`
- **FROZEN_AT:** `L35127`, turn [47] — `pub enum WalRecord {`
- **DEPENDENTS:** T-18 `EffectIssued`, T-45 `WAL`, T-47 `WalRecord`, T-50 `Indeterminate`, T-51 `ReconciliationOutcome`
- **FORBIDDEN_VARIANTS:**
    - `separate effect journal` — superseded: 15B unifies it into the WAL
    - `effect log`
    - `transaction log`
    - `audit log`
    - `event log` — that is `EventLog`, the in-memory machine log
- **PROTECTED (do not rename):**
    - `EffectJournal` — frozen name in the boxed recovery theorem (L28427, L28577)
    - `H` — frozen mathematical symbol for the journal in `D = ⟨S,L,H⟩` (L26134)
    - `EffectJournalEntry` — frozen turn-[33] enum name for journal records (L26222) — superseded by `WalRecord` kinds
    - `EffectJournalCorruption` — frozen fault name for a digest mismatch (L35143)
    - `EffectPrepared` — frozen `WalRecord` variant
    - `EffectCompleted` — frozen `WalRecord` variant
    - `EffectReconciled` — frozen `WalRecord` variant
- **OBLIGATIONS:** `R-DUR-02`, `R-DUR-03`, `R-DUR-04`, `R-PERSIST-03`, `R-RECOV-02`
- **SECTIONS:** `S-13`, `S-18`, `S-19`
- **COLLISIONS:** [X-07](02-collisions.md#x-07), [X-14](02-collisions.md#x-14), [X-32](02-collisions.md#x-32)
- **LAWS:** [N-20](03-laws.md#n-20)
- **NOTE:** The boxed recovery theorem names THREE durable components (`CommittedSnapshot + DurableLog + EffectJournal`, L28427) while 15B freezes TWO durable structures (snapshot + WAL, journal as record kinds). C-25 records the unification but not the theorem site; X-32 reports it.

### T-45 — `WAL`
*Required term.*

- **CANONICAL_TERM:** `WAL`
- **TYPE:** CONCEPT — a defined architectural concept with no single declaration
- **OWNER:** MOD-11 (`ror-persistence`)
- **DEFINITION:** The Write-Ahead Log: the DURABLE, strictly ordered, gap-checked append log that makes `HostInvoked(E) ⇒ DurableIssued(E)` enforceable. Framed by `WalFrame`, populated by `WalRecord`, sequenced by `WalSequence`. The WAL is not the in-memory `EventLog`, and in the frozen 15B model it also carries the effect-journal record kinds.
- **FIRST_DEFINITION:** `L27716`, turn [34] — `strict Write-Ahead Log (WAL) ordering`
- **FROZEN_AT:** `L35099`, turn [47] — `pub struct WalFrame {`
- **DEPENDENTS:** T-46 `WalFrame`, T-47 `WalRecord`, T-49 `EventLog`, T-23 `EffectJournal`, T-48 `Snapshot`
- **FORBIDDEN_VARIANTS:**
    - `event log` — that is `EventLog`, in-memory
    - `journal` — unqualified — `EffectJournal` is a record-kind family inside the WAL
    - `log` — unqualified
    - `transaction log`
    - `persistence log`
- **PROTECTED (do not rename):**
    - `WAL` — frozen abbreviation; first token at L27706, defined at L27716
    - `Write-Ahead Log` — frozen expansion
    - `L` — frozen mathematical symbol for the durable log in `D = ⟨S,L,H⟩` (L26133)
    - `DurableLog` — frozen name in the boxed recovery theorem (L28427)
    - `WalFrame` — frozen framing type
    - `WalRecord` — frozen record-kind enum
    - `WalSequence` — frozen sequence newtype
    - `WalRecordKind` — frozen u8 discriminant type of `WalFrame.kind`
    - `WAL-GAP-REJECT` — frozen verification-obligation tag
    - `WAL-SEQUENCE-CONTINUITY` — frozen verification-obligation tag
- **OBLIGATIONS:** `R-PERSIST-01`, `R-PERSIST-02`, `R-PERSIST-03`, `R-DUR-01`, `R-CORE-06`
- **SECTIONS:** `S-18`, `S-13`
- **COLLISIONS:** [X-13](02-collisions.md#x-13), [X-14](02-collisions.md#x-14), [X-17](02-collisions.md#x-17), [X-31](02-collisions.md#x-31), [X-32](02-collisions.md#x-32), [X-47](02-collisions.md#x-47), [X-54](02-collisions.md#x-54), [X-57](02-collisions.md#x-57), [X-61](02-collisions.md#x-61), [X-71](02-collisions.md#x-71)
- **LAWS:** [N-19](03-laws.md#n-19), [N-20](03-laws.md#n-20), [N-21](03-laws.md#n-21)
- **NOTE:** Five names denote this one durable structure (`WAL`, `Write-Ahead Log`, `L`, `DurableLog`, 'append-only durable event log'), and a sixth (`EventLog`) denotes a DIFFERENT in-memory one. U-16/AMB-14 concern the `EventSequence`/`WalSequence` relationship; X-31 records the naming spread.

### T-46 — `WalFrame`

- **CANONICAL_TERM:** `WalFrame`
- **TYPE:** RUST-STRUCT — a Rust `struct` declaration (nominal type)
- **OWNER:** MOD-11 (`ror-persistence`)
- **DEFINITION:** The frozen durable frame: `{ sequence: WalSequence, kind: WalRecordKind, payload_length: u32, payload: Vec<u8>, checksum: [u8;32] }` with `checksum = SHA-256(sequence ‖ kind ‖ payload_length ‖ payload)`. The parser MUST reject truncated headers/payloads, impossible lengths, checksum mismatches, invalid record kinds, sequence regressions, sequence gaps, malformed canonical payloads, and trailing bytes.
- **FIRST_DEFINITION:** `L34237`, turn [46] — `pub struct WalFrame {`
- **FROZEN_AT:** `L35099`, turn [47] — `pub struct WalFrame {`
- **DEPENDENTS:** T-45 `WAL`, T-47 `WalRecord`
- **FORBIDDEN_VARIANTS:**
    - `log frame`
    - `record frame`
    - `WAL entry` — ambiguous: frame vs record
- **PROTECTED (do not rename):**
    - `WalFrame` — frozen Rust type name
    - `sequence` — frozen field name
    - `kind` — frozen field name
    - `payload_length` — frozen field name
    - `payload` — frozen field name
    - `checksum` — frozen field name
    - `s_{n+1} = s_n + 1` — frozen gap-check formula
- **FROZEN SHAPE:** `pub struct WalFrame { sequence, kind, payload_length, payload, checksum }`
- **OBLIGATIONS:** `R-PERSIST-01`, `R-PERSIST-02`
- **SECTIONS:** `S-18`
- **COLLISIONS:** [X-31](02-collisions.md#x-31), [X-47](02-collisions.md#x-47), [X-50](02-collisions.md#x-50)
- **NOTE:** `WalFrame.kind` is a `WalRecordKind` u8 discriminant, distinct from the 15A envelope `type_tag`.

### T-47 — `WalRecord`

- **CANONICAL_TERM:** `WalRecord`
- **TYPE:** RUST-ENUM — a Rust `enum` declaration (closed variant set)
- **OWNER:** MOD-11 (`ror-persistence`)
- **DEFINITION:** The frozen WAL record taxonomy: `Event(EventEnvelope) | EffectPrepared{id,actor,digest} | EffectIssued{id,actor,digest} | EffectCompleted{id,digest,result_digest} | EffectReconciled{id,digest,outcome} | SnapshotCommit{event_sequence,snapshot_version,state_digest}`. The causal laws `Issued(E) ⇒ Prepared(E)`, `Completed(E) ⇒ Issued(E)`, `Reconciled(E) ⇒ Issued(E)` are read off these kinds.
- **FIRST_DEFINITION:** `L27724`, turn [34] — `pub enum WalRecord {`
- **FROZEN_AT:** `L35127`, turn [47] — `pub enum WalRecord {`
- **DEPENDENTS:** T-45 `WAL`, T-46 `WalFrame`, T-18 `EffectIssued`, T-23 `EffectJournal`, T-48 `Snapshot`, T-51 `ReconciliationOutcome`
- **FORBIDDEN_VARIANTS:**
    - `WAL entry`
    - `log record`
    - `journal entry` — the superseded `EffectJournalEntry`
- **PROTECTED (do not rename):**
    - `WalRecord` — frozen Rust enum name
    - `Event` — frozen variant
    - `EffectPrepared` — frozen variant
    - `EffectIssued` — frozen variant — same name as the T-18 struct (X-07)
    - `EffectCompleted` — frozen variant
    - `EffectReconciled` — frozen variant
    - `SnapshotCommit` — frozen variant
    - `digest` — frozen field name in the effect variants (vs `effect_digest` in the structs — X-07)
    - `result_digest` — frozen field name
    - `outcome` — frozen field name
    - `event_sequence` — frozen field name
    - `snapshot_version` — frozen field name
    - `state_digest` — frozen field name
- **FROZEN SHAPE:** `pub enum WalRecord { Event(EventEnvelope), EffectPrepared{..}, EffectIssued{..}, EffectCompleted{..}, EffectReconciled{..}, SnapshotCommit{..} }`
- **SUPERSEDES (recorded, not deleted):**
    - `pub enum EffectJournalEntry { Prepared{..}, Issued{..}, Completed{..}, Reconciled{..} }   // L26222 (turn [33]) — unified into WalRecord by 15B (C-25)`
- **OBLIGATIONS:** `R-PERSIST-03`, `R-DUR-02`, `R-DUR-03`, `R-DUR-04`
- **SECTIONS:** `S-18`, `S-13`
- **COLLISIONS:** [X-07](02-collisions.md#x-07), [X-24](02-collisions.md#x-24), [X-31](02-collisions.md#x-31), [X-32](02-collisions.md#x-32), [X-33](02-collisions.md#x-33), [X-47](02-collisions.md#x-47), [X-61](02-collisions.md#x-61), [X-71](02-collisions.md#x-71), [X-72](02-collisions.md#x-72)
- **NOTE:** Variant names are `Effect`-prefixed here but unprefixed in the superseded `EffectJournalEntry`. Both spellings are frozen in their own era; neither is renamed (X-07).

### T-48 — `Snapshot`
*Required term.*

- **CANONICAL_TERM:** `Snapshot`
- **TYPE:** CONCEPT — a defined architectural concept with no single declaration
- **OWNER:** MOD-11 (`ror-persistence`)
- **DEFINITION:** A committed, self-consistent, canonically encoded image of `GlobalState` with a version and a state digest. The frozen type is `GlobalSnapshot`; the commit fact is the `WalRecord::SnapshotCommit` record; the integrity property is `CommittedSnapshot(S) ⇒ S is self-consistent`. A corrupted or incomplete snapshot is IGNORED, never repaired. Snapshots MUST include actors' capability contexts.
- **FIRST_DEFINITION:** `L26132`, turn [33] — `- \(S\) = persisted `GlobalState` snapshot,`
- **FROZEN_AT:** `L26301`, turn [33] — `pub struct GlobalSnapshot {`
- **DEPENDENTS:** T-38 `GlobalState`, T-14 `CapabilityContext`, T-47 `WalRecord`, T-45 `WAL`, T-52 `RecoveryFault`
- **FORBIDDEN_VARIANTS:**
    - `checkpoint` — unqualified — the source's 'compare against checkpoint' is a recovery step, not the type
    - `state dump`
    - `image`
    - `EnvironmentSnapshot` — a closure-environment capture, unrelated to persistence
- **PROTECTED (do not rename):**
    - `Snapshot` — frozen concept name; trust-table row 'Persistence'
    - `GlobalSnapshot` — frozen Rust type name
    - `S` — frozen mathematical symbol for the snapshot in `D = ⟨S,L,H⟩` (L26127, glossed L26132) — collides with Scope and Slots (X-10)
    - `CommittedSnapshot(S)` — frozen predicate
    - `SnapshotCommit` — frozen `WalRecord` variant
    - `SnapshotVersion` — frozen field type of `GlobalSnapshot.version`
    - `StateDigest` — frozen newtype for the snapshot digest
    - `version` — frozen field name
    - `state_digest` — frozen field name
    - `EnvironmentSnapshot` — frozen but UNDEFINED type used once, as `FunctionValue.env` (L12357) — X-33
    - `SNAPSHOT-COMMIT-INTEGRITY` — frozen verification-obligation tag
- **FROZEN SHAPE:** `pub struct GlobalSnapshot { version: SnapshotVersion, ... }   // L26301, L34122`
- **OBLIGATIONS:** `R-PERSIST-04`, `R-PERSIST-05`, `R-PERSIST-06`, `R-RECOV-03`
- **SECTIONS:** `S-18`, `S-19`
- **COLLISIONS:** [X-10](02-collisions.md#x-10), [X-33](02-collisions.md#x-33), [X-45](02-collisions.md#x-45), [X-51](02-collisions.md#x-51)
- **LAWS:** [N-21](03-laws.md#n-21)
- **NOTE:** `Snapshot` is a concept whose frozen type name is `GlobalSnapshot`; `EnvironmentSnapshot` shares the word and denotes something unrelated (X-33). The runnable queue's authority at recovery is undecided (U-17).

### T-49 — `EventLog`

- **CANONICAL_TERM:** `EventLog`
- **TYPE:** RUST-STRUCT — a Rust `struct` declaration (nominal type)
- **OWNER:** MOD-11 (`ror-runtime (log); ror-persistence (durable framing)`)
- **DEFINITION:** The IN-MEMORY, strictly append-only machine event log held in `GlobalState.event_log`, whose elements are `EventEnvelope`s with an `EventSequence`. It is not durable by itself: durability comes from the WAL, into which events are written as `WalRecord::Event`. Snapshot serialization records its LENGTH, not its contents.
- **FIRST_DEFINITION:** `L1086`, turn [3] — `pub struct EventLog {`
- **FROZEN_AT:** `L26427`, turn [33] — `pub struct EventEnvelope {`
- **DEPENDENTS:** T-38 `GlobalState`, T-45 `WAL`, T-47 `WalRecord`
- **FORBIDDEN_VARIANTS:**
    - `WAL` — as a synonym — the WAL is the durable framing
    - `journal` — as a synonym
    - `audit log`
    - `trace` — unqualified — `scheduler_trace`/`host_trace` are different traces
- **PROTECTED (do not rename):**
    - `EventLog` — frozen Rust type name
    - `event_log` — frozen `GlobalState` field name
    - `EventEnvelope` — frozen element type
    - `EventSequence` — frozen sequence newtype `pub struct EventSequence(pub u64)`
    - `𝓔` — the turn-[2] symbol for the replay/event log in `Σ` (L718) — superseded
    - `𝓛` — the turn-[5]/[13] symbol for the log in the transition tuples (L2254)
- **OBLIGATIONS:** `R-PERSIST-03`, `R-PERSIST-06`, `R-ACTOR-02`
- **SECTIONS:** `S-18`
- **COLLISIONS:** [X-13](02-collisions.md#x-13), [X-31](02-collisions.md#x-31), [X-47](02-collisions.md#x-47)
- **LAWS:** [N-19](03-laws.md#n-19)
- **NOTE:** U-16/AMB-14: the relationship between `EventSequence` and `WalSequence` is never stated. spec/05 §4 records `EventLog` ≠ `WAL`; that separation is retained here as the canonical reading.

### T-62 — `CanonicalEnvelope`

> **Label, not an identifier.** `CanonicalEnvelope` does not occur verbatim in the frozen source. It is a descriptive name this dictionary uses to address one denotation unambiguously; the frozen identifier(s) it labels are listed under **PROTECTED (do not rename)** below. Introducing `CanonicalEnvelope` into code, a protocol or a formula would be a rename and is prohibited.

- **CANONICAL_TERM:** `CanonicalEnvelope`
- **TYPE:** PROTOCOL-FORMAT — a frozen byte-level format
- **OWNER:** MOD-10 (`ror-core (+ vectors/canonical)`)
- **DEFINITION:** The frozen 15A semantic byte format: `version: u8 | type_tag: u8 | payload_length: u32 BE | payload`, the ONLY semantic representation. Rust struct layout is prohibited and `bincode` is explicitly not the canonical format (it may implement it). Duplicate map keys, trailing bytes and non-canonical encodings are rejected.
- **FIRST_DEFINITION:** `L28298`, turn [36] — `[format_version: u8] [type_tag: u32 LE] [length: u32 LE]`
- **FROZEN_AT:** `L38148`, turn [54] — `version: u8`
- **DEPENDENTS:** T-31 `Value`, T-46 `WalFrame`, T-63 `CanonicalPayload`, T-21 `EffectDigest`
- **FORBIDDEN_VARIANTS:**
    - `wire format` — unqualified — the WAL frame is also a wire format
    - `serialization format`
    - `bincode` — explicitly NOT the canonical format
    - `encoding` — unqualified
- **PROTECTED (do not rename):**
    - `version` — frozen field name (the superseded form spells it `format_version`)
    - `type_tag` — frozen field name — `u8` in the frozen form, `u32 LE` in the superseded trait doc comment (X-50); neither is renamed
    - `payload_length` — frozen field name — `u32 BE`; the superseded form names it `length: u32 LE` (X-50)
    - `payload` — frozen field name
    - `format_version` — superseded field name (L28298) — retained for traceability
    - `length` — superseded field name (L28298) — retained for traceability
    - `CANONICAL_VERSION` — frozen constant name
    - `0x00` — frozen `Value` envelope tag
    - `0x20` — frozen `Symbol` tag
    - `0x30` — frozen `CapRef` tag
    - `0x40` — frozen `ActorId` tag
    - `0x41` — frozen `EffectId` tag
- **FROZEN SHAPE:** `version: u8 | type_tag: u8 | payload_length: u32 BE | payload   // L38147-38150`
- **SUPERSEDES (recorded, not deleted):**
    - `[format_version: u8] [type_tag: u32 LE] [length: u32 LE] [payload]   // L28298 (turn [36])`
- **OBLIGATIONS:** `R-CANON-01`, `R-CANON-02`, `R-CANON-03`, `R-CANON-04`, `R-CANON-06`
- **SECTIONS:** `S-17`
- **COLLISIONS:** [X-24](02-collisions.md#x-24), [X-45](02-collisions.md#x-45), [X-50](02-collisions.md#x-50), [X-51](02-collisions.md#x-51), [X-54](02-collisions.md#x-54), [X-55](02-collisions.md#x-55), [X-56](02-collisions.md#x-56), [X-72](02-collisions.md#x-72)
- **NOTE:** The superseded form differs in field NAME, tag WIDTH and ENDIANNESS. An encoder built from the `CanonicalSerialize` doc comment at L28298 would be wire-incompatible with the frozen format, breaking every digest (`EffectDigest`, `StateDigest`) and the WAL checksum. X-50; the frozen form governs, and the superseded text is retained verbatim.

### T-63 — `CanonicalPayload`

- **CANONICAL_TERM:** `CanonicalPayload`
- **TYPE:** RUST-TRAIT — a Rust `trait` (API contract)
- **OWNER:** MOD-10 (`ror-core`)
- **DEFINITION:** The frozen canonical-codec trait family: `CanonicalPayload` (a type that has a canonical byte form, `TYPE_TAG: u8`), `CanonicalEncode` and `CanonicalDecode` (the fallible codec pair). `CanonicalSerialize` is the earlier, infallible form whose doc comment carries the superseded envelope specification.
- **FIRST_DEFINITION:** `L27685`, turn [34] — `pub trait CanonicalSerialize {`
- **FROZEN_AT:** `L29979`, turn [41] — `pub trait CanonicalPayload: Sized {`
- **DEPENDENTS:** T-62 `CanonicalEnvelope`, T-31 `Value`, T-48 `Snapshot`
- **FORBIDDEN_VARIANTS:**
    - `serializer` — unqualified
    - `codec` — unqualified
    - `marshaller` — that is the actor boundary
- **PROTECTED (do not rename):**
    - `CanonicalPayload` — frozen trait name
    - `CanonicalEncode` — frozen trait name
    - `CanonicalDecode` — frozen trait name — declared but not implemented in the source's own checklist (L29601)
    - `CanonicalSerialize` — frozen EARLIER trait name (L27685, L28296) and a frozen math function symbol `D_S = H(CanonicalSerialize(GlobalState))` (L27061) — retained, not renamed
    - `TYPE_TAG` — frozen associated constant
    - `CanonicalError` — frozen error type
    - `ReadCursor` — frozen decode-cursor type
    - `encode_envelope` — frozen free function
- **OBLIGATIONS:** `R-CANON-02`, `R-CANON-05`, `R-CANON-07`, `R-CANON-08`
- **SECTIONS:** `S-17`
- **COLLISIONS:** [X-50](02-collisions.md#x-50), [X-51](02-collisions.md#x-51), [X-54](02-collisions.md#x-54), [X-55](02-collisions.md#x-55), [X-56](02-collisions.md#x-56), [X-72](02-collisions.md#x-72)
- **NOTE:** spec/05 §4 lists the traits as `CanonicalPayload / CanonicalEncode / CanonicalDecode` and omits `CanonicalSerialize`, which is the name the source's persistence-era trait actually bears. X-51.

### T-76 — `CanonicalError`

- **CANONICAL_TERM:** `CanonicalError`
- **TYPE:** RUST-ENUM — a Rust `enum` declaration (closed variant set)
- **OWNER:** MOD-10 (`ror-core (+ vectors/canonical)`)
- **DEFINITION:** The error type of canonical encoding and decoding — the `Err` arm of every `canonical_serialize` / `canonical_deserialize`, and therefore the type that reports every violation of the frozen envelope and payload rules. Declared seven times in four materially different shapes: unit variants, a differently-spelled set, payload-bearing struct variants for the same names, and an elided block adding one new variant.
- **FIRST_DEFINITION:** `L29188`, turn [38] — `pub enum CanonicalError {`
- **FROZEN_AT:** `L30661`, turn [41] — `pub enum CanonicalError {`
- **DEPENDENTS:** T-62 `CanonicalEnvelope`, T-63 `CanonicalPayload`, T-47 `WalRecord`, T-45 `WAL`, T-31 `Value`
- **FORBIDDEN_VARIANTS:**
    - `CanonicalizationError`
    - `EncodeError`
    - `DecodeError`
    - `canonical error` — unqualified
- **PROTECTED (do not rename):**
    - `CanonicalError` — frozen Rust enum name — SEVEN declarations (L29188, L29968, L30661, L32083, L32959, L33299, L34994)
    - `InvalidVersion` — declared as a UNIT variant (L29189, L29970) and as a STRUCT variant `{ expected: u8, found: u8 }` (L30662) — same name, two arities (X-72)
    - `InvalidTypeTag` — unit (L29190, L29971) and struct `{ expected: u8, found: u8 }` (L30663) (X-72)
    - `LengthMismatch` — unit (L29191) and struct `{ expected: u32, found: usize }` (L30664); ABSENT from the L29968 set (X-72)
    - `LengthOverflow` — declared from L29968 onward; ABSENT from the first declaration L29188 (X-72)
    - `InvalidUtf8` — unit (L29192, L30666)
    - `Utf8Error` — a SECOND name for the same condition, only in the L29968 set (X-72)
    - `UnexpectedEof` — unit (L29193, L30667); ABSENT from the L29968 set, which has `PayloadTooShort` instead (X-72)
    - `PayloadTooShort` — only in the L29968 set (X-72)
    - `InvalidDiscriminant` — unit (L29972) and struct `{ found: u8 }` (L30669) (X-72)
    - `TrailingBytes` — unit (L29975) and struct `{ count: usize }` (L30668) (X-72)
    - `InvalidBoolValue` — struct `{ found: u8 }` (L30670), only in the L30661 set
    - `DuplicateMapKey` — added at L34996 behind a `// ... previous variants` elision — 'NEW: Enforces strict injectivity'
    - `// ... previous variants` — verbatim elision marker at L34995
- **FROZEN SHAPE:** `pub enum CanonicalError { InvalidVersion { expected: u8, found: u8 }, InvalidTypeTag { expected: u8, found: u8 }, LengthMismatch { expected: u32, found: usize }, LengthOverflow, InvalidUtf8, UnexpectedEof, TrailingBytes { count: usize }, InvalidDiscriminant { found: u8 }, InvalidBoolValue { found: u8 } }   // L30661-30671`
- **SUPERSEDES (recorded, not deleted):**
    - `pub enum CanonicalError { InvalidVersion, InvalidTypeTag, LengthMismatch, InvalidUtf8, UnexpectedEof }   // L29188 (turn [38])`
    - `pub enum CanonicalError { LengthOverflow, InvalidVersion, InvalidTypeTag, InvalidDiscriminant, PayloadTooShort, TrailingBytes, Utf8Error }   // L29968`
- **OBLIGATIONS:** `R-CANON-01`, `R-CANON-02`
- **SECTIONS:** `S-17`
- **COLLISIONS:** [X-72](02-collisions.md#x-72), [X-75](02-collisions.md#x-75)
- **NOTE:** Sits directly on the canonical-encoding path where X-50 (the envelope wire format) is already BLOCKING: which `CanonicalError` governs determines what a decoder may report, and the four shapes do not agree on names, spellings or arities.

---

## RECOVERY — Crash classification and reconciliation
Owning module: **MOD-12**.

### T-50 — `Indeterminate`

- **CANONICAL_TERM:** `Indeterminate`
- **TYPE:** STATE — a lifecycle state of a machine object
- **OWNER:** MOD-12 (`ror-persistence`)
- **DEFINITION:** The classification of an effect that is `Issued(E) ∧ ¬Completed(E)` before reconciliation. An indeterminate effect's escrow is NEVER released and it is NEVER inferred to be `NotExecuted`: the system does not conclude 'did not happen' from a missing completion record.
- **FIRST_DEFINITION:** `L26576`, turn [33] — `Issued(E)\land\neg Completed(E)`
- **FROZEN_AT:** `L26714`, turn [33] — `### Indeterminate`
- **DEPENDENTS:** T-18 `EffectIssued`, T-23 `EffectJournal`, T-51 `ReconciliationOutcome`, T-52 `RecoveryFault`
- **FORBIDDEN_VARIANTS:**
    - `failed effect`
    - `not executed`
    - `unknown effect`
    - `interrupted effect` — acceptable prose, not the classification name
    - `orphaned effect`
- **PROTECTED (do not rename):**
    - `Indeterminate` — frozen classification name and `ReconciliationOutcome` variant
    - `EffectRecoveryClass` — frozen enum of effect classes (Replayable/Idempotent/Reversible/Indeterminate, L26669)
    - `RECOVERY-ISSUED-INDETERMINATE` — frozen verification-obligation tag
- **OBLIGATIONS:** `R-DUR-04`, `R-RECOV-02`, `R-CORE-09`, `R-CLAIM-02`
- **SECTIONS:** `S-19`, `S-13`
- **COLLISIONS:** —
- **LAWS:** [N-24](03-laws.md#n-24)
- **NOTE:** Releasing an indeterminate effect's escrow is mutation M012 — a registered defect, not a design option.

### T-51 — `ReconciliationOutcome`

- **CANONICAL_TERM:** `ReconciliationOutcome`
- **TYPE:** RUST-ENUM — a Rust `enum` declaration (closed variant set)
- **OWNER:** MOD-12 (`ror-persistence (+ ror-host protocol)`)
- **DEFINITION:** The closed result set of authoritative host-side resolution of an indeterminate effect: `pub enum ReconciliationOutcome { Completed(EffectReceipt), NotExecuted, Indeterminate }`. It is carried by `WalRecord::EffectReconciled.outcome`. `NotExecuted` here is an AUTHORITATIVE host statement, not an inference from a missing record.
- **FIRST_DEFINITION:** `L26244`, turn [33] — `outcome: ReconciliationOutcome,`
- **FROZEN_AT:** `L26593`, turn [33] — `pub enum ReconciliationOutcome {`
- **DEPENDENTS:** T-50 `Indeterminate`, T-19 `EffectReceipt`, T-47 `WalRecord`
- **FORBIDDEN_VARIANTS:**
    - `recovery result`
    - `resolution`
    - `outcome` — unqualified
- **PROTECTED (do not rename):**
    - `ReconciliationOutcome` — frozen Rust enum name
    - `Completed` — frozen variant (carries an `EffectReceipt`)
    - `NotExecuted` — frozen variant — reachable ONLY via authoritative reconciliation
    - `Indeterminate` — frozen variant
    - `outcome` — frozen field name
    - `Replayed` — NOT a variant: the token occurs nowhere in L1-42312 (req/00-method §5.2); AMB-15 withdrawn
- **OBLIGATIONS:** `R-RECOV-07`, `R-DUR-04`
- **SECTIONS:** `S-19`
- **COLLISIONS:** [X-61](02-collisions.md#x-61)
- **LAWS:** [N-24](03-laws.md#n-24)
- **NOTE:** spec/09 U-15 states the variant set 'is never enumerated'; req/00-method §5.2 corrects this — the declaration exists at L26593-26597. This dictionary follows the corrected finding and records the disagreement rather than silently adopting either text.

### T-52 — `RecoveryFault`

- **CANONICAL_TERM:** `RecoveryFault`
- **TYPE:** RUST-STRUCT — a Rust `struct` declaration (nominal type)
- **OWNER:** MOD-12 (`ror-persistence`)
- **DEFINITION:** The explicit outcome of invalid persistence state. Recovery either returns a `GlobalState` or a `RecoveryFault`; it never silently repairs state by mutation. `Recover(D) = State_before_crash` holds only under the frozen qualification (every interrupted effect reconciled, idempotent, or classified indeterminate).
- **FIRST_DEFINITION:** `L26506`, turn [33] — `) -> Result<GlobalState, RecoveryFault> {`
- **DEPENDENTS:** T-48 `Snapshot`, T-45 `WAL`, T-23 `EffectJournal`, T-50 `Indeterminate`
- **FORBIDDEN_VARIANTS:**
    - `recovery error`
    - `recovery failure` — as a type name
    - `corruption` — unqualified
- **PROTECTED (do not rename):**
    - `RecoveryFault` — frozen Rust type name
    - `EffectJournalCorruption` — frozen distinct fault for a digest mismatch (L35143)
    - `Recover(D)` — frozen function symbol
    - `Replay(S,L,H)` — frozen function symbol
    - `D` — frozen symbol for the durable state `⟨S,L,H⟩` — collides with the duration consumable (X-12)
- **OBLIGATIONS:** `R-RECOV-01`, `R-RECOV-03`, `R-CORE-09`, `R-CORE-10`
- **SECTIONS:** `S-19`
- **COLLISIONS:** [X-12](02-collisions.md#x-12), [X-13](02-collisions.md#x-13), [X-32](02-collisions.md#x-32), [X-58](02-collisions.md#x-58), [X-67](02-collisions.md#x-67)
- **NOTE:** Two recovery step lists exist (12 steps L35193-35204; 19 steps L34344-34364) — AMB-27.

### T-53 — `Supervisor`

- **CANONICAL_TERM:** `Supervisor`
- **TYPE:** COMPONENT — an architectural component / trusted layer
- **OWNER:** MOD-12 (`ror-persistence (+ ror-runtime lifecycle)`)
- **DEFINITION:** The trusted lifecycle and recovery authority: it enforces WAL ordering, commits snapshots, initiates recovery, and owns reconciliation. It is trusted (R-TRUST-01) and is not the planner, not the host, and not the scheduler.
- **FIRST_DEFINITION:** `L3136`, turn [6] — `Supervisor observes behavior.`
- **FROZEN_AT:** `L26799`, turn [33] — `# 11. Supervisor`
- **DEPENDENTS:** T-45 `WAL`, T-48 `Snapshot`, T-52 `RecoveryFault`
- **FORBIDDEN_VARIANTS:**
    - `monitor`
    - `watchdog`
    - `orchestrator`
    - `manager`
- **PROTECTED (do not rename):**
    - `Supervisor` — frozen component name; trust-table row
- **OBLIGATIONS:** `R-PERSIST-01`, `R-RECOV-01`, `R-TRUST-01`
- **SECTIONS:** `S-18`, `S-19`
- **COLLISIONS:** —

---

## AGENT — LLM/planner boundary and observations
Owning module: **MOD-13**.

### T-54 — `Observation (planner-facing)`
*Required term.*

> **Label, not an identifier.** `Observation (planner-facing)` does not occur verbatim in the frozen source. It is a descriptive name this dictionary uses to address one denotation unambiguously; the frozen identifier(s) it labels are listed under **PROTECTED (do not rename)** below. Introducing `Observation (planner-facing)` into code, a protocol or a formula would be a rename and is prohibited.

- **CANONICAL_TERM:** `Observation (planner-facing)`
- **TYPE:** RUST-STRUCT — a Rust `struct` declaration (nominal type)
- **OWNER:** MOD-13 (`ror-agent`)
- **DEFINITION:** The sanitized machine-state summary handed to the untrusted planner: `{ sequence: EventSequence, actor: ActorId, value: Option<Value>, events: Vec<GlobalEvent>, faults: Vec<Fault>, available_capabilities: CapabilitySummary, budget: BudgetSummary }`. It is the input half of the LLM outer loop and the basis of the staleness check; it exposes capability SUMMARIES, never `CapRef`s or `Authority`.
- **FIRST_DEFINITION:** `L27156`, turn [33] — `pub struct Observation {`
- **DEPENDENTS:** T-02 `PlanProposal`, T-56 `LLMOutput`, T-49 `EventLog`
- **FORBIDDEN_VARIANTS:**
    - `Observation` — unqualified — two frozen types share the name, X-06
    - `telemetry`
    - `state dump`
    - `normalized observation` — that is the differential type, T-57
- **PROTECTED (do not rename):**
    - `Observation` — frozen Rust type name — shared with T-57; NOT renamed here because renaming a frozen type requires an explicit decision
    - `sequence` — frozen field name
    - `actor` — frozen field name
    - `value` — frozen field name
    - `events` — frozen field name
    - `faults` — frozen field name
    - `available_capabilities` — frozen field name
    - `budget` — frozen field name
    - `GlobalEvent` — frozen field type — never declared (X-33 family)
    - `CapabilitySummary` — frozen field type — never declared
    - `BudgetSummary` — frozen field type — never declared
    - `observation_sequence` — frozen `PlanProposal` field matched against this observation's sequence
- **FROZEN SHAPE:** `pub struct Observation { sequence, actor, value, events, faults, available_capabilities, budget }   // L27156`
- **OBLIGATIONS:** `R-PLANNER-01`, `R-PLANNER-03`, `R-PLANNER-05`
- **SECTIONS:** `S-05`
- **COLLISIONS:** [X-06](02-collisions.md#x-06), [X-29](02-collisions.md#x-29)
- **LAWS:** [N-22](03-laws.md#n-22)
- **NOTE:** The parenthetical qualifier is a DICTIONARY qualification for prose, not a rename: the Rust identifier in the source is bare `Observation`. X-06 requires an explicit decision on distinct type names.

### T-55 — `PlannerAccepted`

- **CANONICAL_TERM:** `PlannerAccepted`
- **TYPE:** RUST-STRUCT — a Rust `struct` declaration (nominal type)
- **OWNER:** MOD-13 (`ror-agent`)
- **DEFINITION:** The recorded accepted proposal, written so a run can be replayed without re-querying the (non-deterministic) planner. The planner need not be deterministic; the RECORD of what it returned is what makes replay deterministic.
- **FIRST_DEFINITION:** `L27411`, turn [33] — `pub struct PlannerAccepted {`
- **DEPENDENTS:** T-02 `PlanProposal`, T-56 `LLMOutput`
- **FORBIDDEN_VARIANTS:**
    - `recorded proposal` — as a type name
    - `accepted plan`
    - `proposal log entry`
- **PROTECTED (do not rename):**
    - `PlannerAccepted` — frozen Rust type name
    - `ProposalDigest` — frozen field type — canonical form unspecified (U-13)
    - `PlannerMetadata` — frozen `PlanProposal` field type — fields never defined (U-13)
- **OBLIGATIONS:** `R-PLANNER-04`, `R-PLANNER-05`
- **SECTIONS:** `S-05`
- **COLLISIONS:** [X-62](02-collisions.md#x-62)
- **NOTE:** U-13 leaves `PlannerMetadata`/`ProposalDigest` and the exact staleness predicate undecided (C-38).

### T-56 — `LLMOutput`

- **CANONICAL_TERM:** `LLMOutput`
- **TYPE:** MATH-SYMBOL — a mathematical symbol in a frozen formula
- **OWNER:** MOD-13 (`ror-agent`)
- **DEFINITION:** The probabilistic producer's output, treated as DATA: `LLMOutput ∈ Data`. The LLM/planner proposes; it holds no authority and cannot allocate capabilities, authorize effects, modify budgets or scheduler state, allocate actors, invoke the host, bypass compilation, or bypass persistence. `LLMOutput ∧ UntrustedInput ↛ ExternalEffect`.
- **FIRST_DEFINITION:** `L27253`, turn [33] — `LLMOutput\in Data`
- **DEPENDENTS:** T-02 `PlanProposal`, T-01 `Block`, T-54 `Observation (planner-facing)`
- **FORBIDDEN_VARIANTS:**
    - `authority`
    - `trusted input`
    - `agent decision`
    - `the model's plan`
    - `instruction`
- **PROTECTED (do not rename):**
    - `LLMOutput` — frozen mathematical symbol in the central invariant
    - `LLM / planner` — frozen component name; trust-table row 'No'
    - `Planner` — frozen alternate capitalization in source prose
    - `UntrustedInput` — frozen symbol
    - `Data` — frozen symbol in `LLMOutput ∈ Data`
    - `R-CORE-01` — the obligation that states this
- **OBLIGATIONS:** `R-CORE-01`, `R-PLANNER-01`, `R-PLANNER-02`, `R-TRUST-01`, `R-TRUST-02`
- **SECTIONS:** `S-02`, `S-05`, `S-03`
- **COLLISIONS:** [X-69](02-collisions.md#x-69)
- **LAWS:** [N-09](03-laws.md#n-09)
- **NOTE:** N-09 (`LLM output ≠ Authority`) is the thesis-level law; R-PLANNER-02 enumerates its eight prohibitions.

---

## VERIFICATION — Reference model, differential, mutation
Owning module: **MOD-15**.

### T-57 — `Observation (differential)`
*Required term.*

> **Label, not an identifier.** `Observation (differential)` does not occur verbatim in the frozen source. It is a descriptive name this dictionary uses to address one denotation unambiguously; the frozen identifier(s) it labels are listed under **PROTECTED (do not rename)** below. Introducing `Observation (differential)` into code, a protocol or a formula would be a rename and is prohibited.

- **CANONICAL_TERM:** `Observation (differential)`
- **TYPE:** RUST-STRUCT — a Rust `struct` declaration (nominal type)
- **OWNER:** MOD-15 (`ror-differential (comparator); emitted by ror-runtime and ror-reference`)
- **DEFINITION:** The normalized semantic observation both implementations emit for comparison: `{ terminal_states: Vec<ObservedActor>, event_trace: Vec<ObservedEvent>, effects: Vec<ObservedEffect>, budgets: Vec<ObservedBudget>, scheduler_trace: Vec<ObservedSchedulerStep>, faults: Vec<ObservedFault>, state_digest: Option<ObservedDigest> }`. It is a TEST representation and must not become a third semantic wire protocol. `Observe(Production(X)) = Observe(Reference(X))` is the principal oracle.
- **FIRST_DEFINITION:** `L36170`, turn [48] — `pub struct Observation {`
- **DEPENDENTS:** T-58 `ReferenceModel`, T-59 `FirstDivergence`, T-31 `Value`
- **FORBIDDEN_VARIANTS:**
    - `Observation` — unqualified — two frozen types share the name, X-06
    - `semantic observation` — informal; acceptable only as prose for this type
    - `oracle` — that is the reference model in its oracle role
    - `trace` — unqualified
    - `final value` — comparison is never final-value-only
- **PROTECTED (do not rename):**
    - `Observation` — frozen Rust type name — shared with T-54; NOT renamed here
    - `Observe` — frozen function symbol in the oracle equation
    - `terminal_states` — frozen field name
    - `event_trace` — frozen field name
    - `effects` — frozen field name
    - `budgets` — frozen field name
    - `scheduler_trace` — frozen field name
    - `faults` — frozen field name
    - `state_digest` — frozen field name
    - `ObservedActor` — frozen field type
    - `ObservedEvent` — frozen field type
    - `ObservedEffect` — frozen field type
    - `ObservedBudget` — frozen field type
    - `ObservedSchedulerStep` — frozen field type
    - `ObservedFault` — frozen field type
    - `ObservedDigest` — frozen field type
- **FROZEN SHAPE:** `pub struct Observation { terminal_states, event_trace, effects, budgets, scheduler_trace, faults, state_digest }   // L36170`
- **OBLIGATIONS:** `R-REF-05`, `R-TEST-02`, `R-TEST-03`, `R-ARCH-02`
- **SECTIONS:** `S-20`
- **COLLISIONS:** [X-06](02-collisions.md#x-06), [X-29](02-collisions.md#x-29)
- **LAWS:** [N-22](03-laws.md#n-22)
- **NOTE:** The seven `Observed*` element types are named but never declared; that gap is recorded, not filled. spec/05 §5 lists only this sense under 'Normalized observation' and never mentions the planner-facing `Observation` (T-54) — X-06.

### T-58 — `ReferenceModel`

> **Label, not an identifier.** `ReferenceModel` does not occur verbatim in the frozen source. It is a descriptive name this dictionary uses to address one denotation unambiguously; the frozen identifier(s) it labels are listed under **PROTECTED (do not rename)** below. Introducing `ReferenceModel` into code, a protocol or a formula would be a rename and is prohibited.

- **CANONICAL_TERM:** `ReferenceModel`
- **TYPE:** COMPONENT — an architectural component / trusted layer
- **OWNER:** MOD-14 (`ror-reference`)
- **DEFINITION:** The independently implemented executable model of the frozen semantics, sharing ZERO core transition logic with production (R-SCOPE-04, R-REF-02). It is an oracle by comparison, not by construction: it does not make production correct, and agreement over the tested state space is evidence, not proof.
- **FIRST_DEFINITION:** `L11436`, turn [20] — `an independent reference model`
- **FROZEN_AT:** `L35283`, turn [48] — `Phase 15C defines an independently implemented executable reference model`
- **DEPENDENTS:** T-57 `Observation (differential)`, T-59 `FirstDivergence`, T-64 `Specification`, T-66 `Verification`
- **FORBIDDEN_VARIANTS:**
    - `reference implementation` — acceptable prose, not the canonical name
    - `oracle` — informal; the reference model in its oracle role
    - `golden model`
    - `second implementation`
    - `specification` — a reference model is an implementation of the specification
- **PROTECTED (do not rename):**
    - `reference model` — frozen prose name
    - `executable reference model` — frozen prose name (15C heading)
    - `ror-reference` — frozen crate name
    - `Reference` — the axis endpoint in `Production → Observation → Reference`
    - `PanicHost` — frozen test double (MOD-17), not part of the reference model
    - `MockKernel` — frozen test double (MOD-17)
- **OBLIGATIONS:** `R-REF-01`, `R-REF-02`, `R-REF-03`, `R-REF-04`, `R-SCOPE-04`
- **SECTIONS:** `S-20`
- **COLLISIONS:** [X-06](02-collisions.md#x-06), [X-48](02-collisions.md#x-48), [X-60](02-collisions.md#x-60)
- **LAWS:** [N-27](03-laws.md#n-27)
- **NOTE:** The source also calls it 'the reference machine' (L10128, L15871, L16403) in the pre-15C era, where it meant the first boring milestone implementation — a DIFFERENT object from the 15C independent reference model. X-48.

### T-59 — `FirstDivergence`

> **Label, not an identifier.** `FirstDivergence` does not occur verbatim in the frozen source. It is a descriptive name this dictionary uses to address one denotation unambiguously; the frozen identifier(s) it labels are listed under **PROTECTED (do not rename)** below. Introducing `FirstDivergence` into code, a protocol or a formula would be a rename and is prohibited.

- **CANONICAL_TERM:** `FirstDivergence`
- **TYPE:** CONCEPT — a defined architectural concept with no single declaration
- **OWNER:** MOD-15 (`ror-differential`)
- **DEFINITION:** The earliest point at which production and reference observations differ, reported by the comparator instead of a bare pass/fail. Divergences are adjudicated four ways: production defect, reference defect, harness defect, specification ambiguity — and specification ambiguity must be resolved explicitly, never hidden in a test adjustment.
- **FIRST_DEFINITION:** `L36655`, turn [48] — `First divergence`
- **FROZEN_AT:** `L36666`, turn [48] — `# 15C.32 First-Divergence Algorithm`
- **DEPENDENTS:** T-57 `Observation (differential)`, T-58 `ReferenceModel`, T-60 `Mutation`
- **FORBIDDEN_VARIANTS:**
    - `first failure`
    - `mismatch point`
    - `diff`
- **PROTECTED (do not rename):**
    - `first divergence` — frozen prose name
    - `first_divergence` — frozen counterexample-artifact field
    - `Adjudication` — frozen 4-way classification name
    - `production defect` — frozen classification
    - `reference defect` — frozen classification
    - `harness defect` — frozen classification
    - `specification ambiguity` — frozen classification
- **OBLIGATIONS:** `R-REF-05`, `R-TEST-02`, `R-TEST-09`
- **SECTIONS:** `S-20`, `S-21`
- **COLLISIONS:** —

### T-60 — `Mutation`

- **CANONICAL_TERM:** `Mutation`
- **TYPE:** CONCEPT — a defined architectural concept with no single declaration
- **OWNER:** MOD-16 (`mutations/registry.toml (+ ror-testkit)`)
- **DEFINITION:** A deliberately injected known semantic defect (the registry entry) and its instance in a run (the mutant). The frozen baseline registry is M001-M018; an equivalent mutant is behaviorally indistinguishable and must be adjudicated and documented, never counted as a miss.
- **FIRST_DEFINITION:** `L37187`, turn [49] — `### The Critical Gate: Deliberate Fault-Injection Validation (Mutation Testing)`
- **FROZEN_AT:** `L38477`, turn [54] — `M001`
- **DEPENDENTS:** T-61 `MutationKillRate`, T-59 `FirstDivergence`
- **FORBIDDEN_VARIANTS:**
    - `fault injection` — unqualified — crash injection is a different suite
    - `bug`
    - `defect` — unqualified
- **PROTECTED (do not rename):**
    - `Mutation` — frozen name
    - `mutant` — frozen name for an instance
    - `M001…M018` — frozen baseline mutation-registry IDs
    - `equivalent mutant` — frozen classification
    - `non-equivalent mutation` — frozen scope of the 100% target
    - `mutations/registry.toml` — frozen file path
- **OBLIGATIONS:** `R-TEST-04`, `R-TEST-05`, `R-TEST-06`
- **SECTIONS:** `S-21`
- **COLLISIONS:** [X-49](02-collisions.md#x-49)
- **NOTE:** `M0NN` mutation IDs share the letter M with milestones `M0`-`M11` and with the memory symbol `M`; X-49 records the three namespaces.

### T-61 — `MutationKillRate`

- **CANONICAL_TERM:** `MutationKillRate`
- **TYPE:** MATH-PREDICATE — a mathematical predicate in a frozen formula/theorem
- **OWNER:** MOD-16 (`mutations/registry.toml`)
- **DEFINITION:** `MutationKillRate = 100%` over all REGISTERED NON-EQUIVALENT mutations. The denominator is the registry, not all possible mutants; coverage metrics are evidence and never replace differential agreement.
- **FIRST_DEFINITION:** `L38506`, turn [54] — `\boxed{MutationKillRate=100\%}`
- **DEPENDENTS:** T-60 `Mutation`, T-59 `FirstDivergence`
- **FORBIDDEN_VARIANTS:**
    - `mutation score`
    - `kill rate` — unqualified, without the scope
    - `coverage` — that is a different metric
- **PROTECTED (do not rename):**
    - `MutationKillRate` — frozen symbol
    - `100% kill rate` — frozen target wording
    - `kill rate` — frozen informal wording — scope must be stated (C-32)
- **OBLIGATIONS:** `R-TEST-05`, `R-TEST-06`
- **SECTIONS:** `S-21`
- **COLLISIONS:** —
- **NOTE:** C-32 fixes the scope as registered non-equivalent mutants.

---

## CLAIM — Evidence ladder and conformance claims
Owning module: **MOD-17**.

### T-64 — `Specification`

- **CANONICAL_TERM:** `Specification`
- **TYPE:** CONCEPT — a defined architectural concept with no single declaration
- **OWNER:** MOD-17 (`spec/ + req/ (documents)`)
- **DEFINITION:** The frozen statement of REQUIRED behavior: what the machine must do. A specification is evidence of nothing but itself. `SPECIFICATION: FROZEN` means the requirement text is stable; it never means the behavior has been implemented, tested, verified, or proven.
- **FIRST_DEFINITION:** `L38936`, turn [54] — `SPECIFICATION: FROZEN`
- **DEPENDENTS:** T-65 `Implementation`, T-66 `Verification`, T-67 `Proof`, T-69 `Frozen`
- **FORBIDDEN_VARIANTS:**
    - `design`
    - `contract` — unqualified — 'reference contract' and 'verification contract' are distinct frozen items
    - `proof`
    - `guarantee`
    - `implementation plan`
- **PROTECTED (do not rename):**
    - `SPECIFICATION: FROZEN` — frozen status line
    - `ARCHITECTURE: FROZEN` — frozen status line
    - `REFERENCE CONTRACT: FROZEN` — frozen status line
    - `VERIFICATION CONTRACT: FROZEN` — frozen status line
    - `S-NN` — frozen section identifier scheme
    - `R-AREA-NN` — frozen obligation identifier scheme
- **OBLIGATIONS:** `R-SCOPE-01`, `R-SCOPE-02`, `R-CLAIM-01`
- **SECTIONS:** `S-01`, `S-24`
- **COLLISIONS:** [X-52](02-collisions.md#x-52), [X-53](02-collisions.md#x-53), [X-60](02-collisions.md#x-60), [X-63](02-collisions.md#x-63)
- **LAWS:** [N-06](03-laws.md#n-06)
- **NOTE:** N-06 (`Specification ≠ Implementation`) is enforced by the evidence ladder: text never confers `IMPLEMENTED`.

### T-65 — `Implementation`

- **CANONICAL_TERM:** `Implementation`
- **TYPE:** CONCEPT — a defined architectural concept with no single declaration
- **OWNER:** MOD-17 (`crates/ (absent at this commit)`)
- **DEFINITION:** Repository code that realizes a requirement. `IMPLEMENTED` requires source files in this repository mapped in spec/07 — a Rust code block inside `Red-on-Rust.md` is SPECIFICATION TEXT, not repository code, and never raises evidence status.
- **FIRST_DEFINITION:** `L38939`, turn [54] — `IMPLEMENTATION: READY`
- **DEPENDENTS:** T-64 `Specification`, T-66 `Verification`, T-68 `EvidenceStatus`
- **FORBIDDEN_VARIANTS:**
    - `verification`
    - `proof`
    - `conformance`
    - `the reference model` — that is one implementation among two
- **PROTECTED (do not rename):**
    - `IMPLEMENTATION: READY` — frozen status line (turn [54]/[58])
    - `IMPLEMENTATION: IN PROGRESS` — the README's other status line — the two disagree (C-09); both retained
    - `ror-core…ror-testkit` — frozen crate names
    - `ROR-NNN` — frozen first-sprint task identifier scheme
- **OBLIGATIONS:** `R-SCOPE-02`, `R-REPO-01`, `R-REPO-02`, `R-CLAIM-01`
- **SECTIONS:** `S-01`, `S-22`, `S-24`
- **COLLISIONS:** [X-48](02-collisions.md#x-48), [X-52](02-collisions.md#x-52), [X-53](02-collisions.md#x-53), [X-63](02-collisions.md#x-63)
- **LAWS:** [N-06](03-laws.md#n-06), [N-07](03-laws.md#n-07), [N-27](03-laws.md#n-27)
- **NOTE:** This repository contains no implementation at this commit, so every obligation is `SPECIFIED` and no higher (spec/00 §2). The README's 'IN PROGRESS'/'READY' wording is orientation, not evidence (C-09).

### T-66 — `Verification`

- **CANONICAL_TERM:** `Verification`
- **TYPE:** CONCEPT — a defined architectural concept with no single declaration
- **OWNER:** MOD-17 (`tests/ + scripts/`)
- **DEFINITION:** Independent evidence that an implementation conforms: differential agreement against the reference model, exhaustive/property coverage, mutation kills, crash-matrix classification. `VERIFICATION CONTRACT: FROZEN` means the CONTRACT is frozen, not that verification has been performed. Verification is evidence over a tested state space.
- **FIRST_DEFINITION:** `L38938`, turn [54] — `VERIFICATION CONTRACT: FROZEN`
- **DEPENDENTS:** T-58 `ReferenceModel`, T-57 `Observation (differential)`, T-60 `Mutation`, T-61 `MutationKillRate`, T-67 `Proof`
- **FORBIDDEN_VARIANTS:**
    - `proof`
    - `testing` — unqualified — testing is a means; verification is the evidence claim
    - `validation` — unqualified
    - `certification`
- **PROTECTED (do not rename):**
    - `VERIFICATION: FROZEN` — the README's status line — means the contract is frozen (spec/05 §6.10)
    - `VERIFICATION CONTRACT: FROZEN` — frozen status line (turn [54])
    - `VERIFIED` — frozen ladder rung
    - `machine-checked evidence` — frozen claim wording (R-CLAIM-01)
    - `TAG-NAME` — frozen verification-obligation tag scheme
- **OBLIGATIONS:** `R-CLAIM-01`, `R-TEST-07`, `R-TEST-11`, `R-SCOPE-02`
- **SECTIONS:** `S-20`, `S-21`, `S-24`
- **COLLISIONS:** [X-52](02-collisions.md#x-52)
- **LAWS:** [N-07](03-laws.md#n-07), [N-08](03-laws.md#n-08), [N-31](03-laws.md#n-31)
- **NOTE:** 'The property tests prove the code obeys the calculus' violates R-CLAIM-01 (C-34); the frozen wording is machine-checked evidence of refinement over the tested state space.

### T-67 — `Proof`

- **CANONICAL_TERM:** `Proof`
- **TYPE:** CONCEPT — a defined architectural concept with no single declaration
- **OWNER:** MOD-17 (`(none; no proof artifact exists)`)
- **DEFINITION:** A formal, mechanized artifact establishing a statement. `PROVEN` requires a proof artifact in the repository. NO theorem in the frozen source has a mechanized proof: Theorems 1-6 carry proof SKETCHES only, so all remain `SPECIFIED`. The project deliberately does not claim test execution constitutes a mathematical proof of the calculus.
- **FIRST_DEFINITION:** `L28263`, turn [35] — `formal proof obligations remain separately identified`
- **DEPENDENTS:** T-66 `Verification`, T-68 `EvidenceStatus`
- **FORBIDDEN_VARIANTS:**
    - `verification` — as a synonym for proof
    - `guarantee`
    - `established fact`
    - `proven` — as a status for any current obligation
- **PROTECTED (do not rename):**
    - `PROVEN` — frozen ladder rung
    - `proof sketch` — frozen description of Theorems 1-6
    - `formal mechanization` — frozen future-work wording
    - `Theorem 1…Theorem 6` — frozen theorem numbering
- **OBLIGATIONS:** `R-CLAIM-01`, `R-CLAIM-03`, `R-SCOPE-02`
- **SECTIONS:** `S-24`, `S-01`
- **COLLISIONS:** [X-52](02-collisions.md#x-52)
- **LAWS:** [N-08](03-laws.md#n-08)
- **NOTE:** C-43 records that all six theorems have proof sketches only; N-08 (`Verification ≠ Proof`) is the law.

### T-68 — `EvidenceStatus`

> **Label, not an identifier.** `EvidenceStatus` does not occur verbatim in the frozen source. It is a descriptive name this dictionary uses to address one denotation unambiguously; the frozen identifier(s) it labels are listed under **PROTECTED (do not rename)** below. Introducing `EvidenceStatus` into code, a protocol or a formula would be a rename and is prohibited.

- **CANONICAL_TERM:** `EvidenceStatus`
- **TYPE:** CLAIM-STATUS — a rung of the evidence ladder
- **OWNER:** MOD-17 (`spec/00 §2 (vocabulary); artifacts in crates/, tests/, vectors/`)
- **DEFINITION:** The strictly evidence-gated ladder `SPECIFIED → IMPLEMENTED → TESTED → VERIFIED → PROVEN`. Promotion requires a repository artifact; a specification requirement never confers `IMPLEMENTED` or higher. At this commit every obligation is `SPECIFIED`.
- **FIRST_DEFINITION:** `spec/00-overview.md:25` — `| `SPECIFIED` | Normative requirement exists in the frozen source.`
- **DEPENDENTS:** T-64 `Specification`, T-65 `Implementation`, T-66 `Verification`, T-67 `Proof`
- **FORBIDDEN_VARIANTS:**
    - `maturity level`
    - `completion percentage`
    - `confidence`
    - `DONE`
- **PROTECTED (do not rename):**
    - `SPECIFIED` — frozen rung
    - `IMPLEMENTED` — frozen rung
    - `TESTED` — frozen rung
    - `VERIFIED` — frozen rung
    - `PROVEN` — frozen rung
    - `UNKNOWN` — frozen extra state in req/ — reserved for statements whose normative status cannot be determined; NOT a weaker SPECIFIED
    - `EVIDENCE-STATUS` — frozen req/ record field name
- **OBLIGATIONS:** `R-SCOPE-02`, `R-CLAIM-01`
- **SECTIONS:** `S-01`
- **COLLISIONS:** [X-52](02-collisions.md#x-52), [X-53](02-collisions.md#x-53), [X-63](02-collisions.md#x-63)
- **NOTE:** The ladder VOCABULARY is a canonicalization-layer construct (spec/00 §2); the underlying discipline is source text ('machine-checked evidence', L28263; 'frozen means frozen', L38929-38942). FIRST_DEFINITION therefore cites `spec/00-overview.md`, not the source — recorded explicitly rather than back-dated into the frozen transcript.

### T-69 — `Frozen`

- **CANONICAL_TERM:** `Frozen`
- **TYPE:** CONCEPT — a defined architectural concept with no single declaration
- **OWNER:** MOD-17 (`spec/ (documents)`)
- **DEFINITION:** 'Requirements are stable and may not be changed by implementation convenience.' Frozen NEVER means verified, correct, complete, or unambiguous: a frozen specification can still contain open contradictions (spec/06) and undecided items (spec/09). Where implementation difficulty exposes an ambiguity, STOP and report it; do not resolve semantic ambiguity by inventing behavior.
- **FIRST_DEFINITION:** `L38935`, turn [54] — `ARCHITECTURE: FROZEN`
- **DEPENDENTS:** T-64 `Specification`, T-66 `Verification`, T-68 `EvidenceStatus`
- **FORBIDDEN_VARIANTS:**
    - `verified`
    - `final`
    - `complete`
    - `correct`
    - `closed`
- **PROTECTED (do not rename):**
    - `FROZEN` — frozen status word
    - `STOP and report` — frozen rule wording (R-SCOPE-03, L37690)
    - `frozen addendum` — the only legal mechanism for changing frozen text
    - `superseded` — frozen marker for obsolete text retained for traceability
- **OBLIGATIONS:** `R-SCOPE-02`, `R-SCOPE-03`, `R-TEST-09`
- **SECTIONS:** `S-01`
- **COLLISIONS:** [X-52](02-collisions.md#x-52), [X-63](02-collisions.md#x-63)
- **LAWS:** [N-31](03-laws.md#n-31)
- **NOTE:** spec/05 §6.9-6.10 states the same rule; this entry is the dictionary's term of record for it.
