# Red-on-Rust
 
**A deterministic, capability-scoped, resource-bounded, crash-recoverable execution machine for probabilistically generated programs.**
 
Red-on-Rust is a Rust-based execution substrate for a family of homoiconic, dialect-oriented languages inspired by the compositional model of the REBOL/Red lineage.
 
Its purpose is not merely to execute generated programs safely.
 
Its purpose is to establish a **small, explicit, deterministic machine boundary** between probabilistic program generation and consequential computation.
  
## Status
 `Architecture:       FROZEN Specification:      FROZEN Verification:       FROZEN Repository:         BOOTSTRAP Implementation:     IN PROGRESS ` 
 
**Frozen specification ≠ verified implementation.**
 
 
The architecture defines required behavior. Independent reference execution, differential testing, mutation testing, crash injection, stress testing, and security review provide the evidence that an implementation conforms to that specification.
  
## Canonical Specification Document Set

The frozen source (`Red-on-Rust.md`) has been canonicalized into the document set in `spec/`:

- `spec/00-overview.md` — method, status ladder (`SPECIFIED → IMPLEMENTED → TESTED → VERIFIED → PROVEN`), identifier scheme
- `spec/01-canonical-specification.md` — cleaned normative specification (24 sections, `S-01`…`S-24`)
- `spec/02-section-hierarchy.md` — stable section index with provenance and supersession records
- `spec/03-obligation-matrix.md` — 148 stable requirement IDs (`R-…`) with status and provenance
- `spec/04-dependency-graph.md` — section, object, and verification dependency graphs
- `spec/05-terminology.md` — glossary and normalization rules
- `spec/06-contradictions-ambiguities.md` — 64 consistency findings in 65 rows (`C-01`…`C-65`; C-46…C-65 added by the terminology pass, C-08 re-graded MINOR → MAJOR by it, and C-54 rewritten by its declaration sweep after the first version of that row was filed on a false premise)
- `spec/07-implementation-mapping.md` — obligations → crate/module mapping; actual repository state
- `spec/08-verification-mapping.md` — obligations → conformance tests and evidence status
- `spec/09-unresolved-decisions.md` — 23 items (`U-…`) requiring explicit architectural decisions (U-23…U-25 added by the terminology pass and U-26…U-29 by its declaration sweep; U-08 corrected and U-14 escalated to blocking by its fault-taxonomy audit)
- `spec/10-index.json` — machine-readable cross-index

A second organization, `mod/`, splits the same specification into **17 semantic
modules** (`MOD-01 CORE` … `MOD-17 VERIFICATION`) by architectural responsibility
rather than document structure: one canonical owner per obligation, explicit
cross-references for requirements that span components, and a marked-duplication
register (`D-01`…`D-12`). Each module file carries SECTION-ID, TITLE, PURPOSE,
NORMATIVE-CONTENT, NON-NORMATIVE-CONTENT, INPUTS, OUTPUTS, DEPENDENCIES, INVARIANTS,
REQUIREMENTS, SECURITY-BOUNDARY, VERIFICATION-OBLIGATIONS, SOURCE-PROVENANCE, and
CROSS-REFERENCES. Normative text remains single-homed in `spec/01`/`req/`;
`mod/18-ownership-matrix.md` and `mod/19-index.json` are generated
(`python3 mod/_build.py --write`; checked with `python3 mod/_build.py`).

A third organization, `dep/`, is the **dependency graph** derived from the other two:
four layers (10 crates / 15 crate edges, 17 modules / 137 typed module edges, 545 atomic
records / 927 requirement edges, 24 sections / 34 section edges), each edge typed
`TYPE_ | SEMANTIC_ | SECURITY_ | SERIALIZATION_ | PERSISTENCE_ | VERIFICATION_ |
RUNTIME_DEPENDENCY` and read as **`A -> B` = B depends on A**. It reports roots, leaves,
strongly connected components, circular dependencies requiring architectural review,
hidden dependencies (`HD-1`…`HD-6`), invalid dependency directions, requirements
referenced before definition, and the violations of architectural independence
(the findings register `V-…`). For the four findings that block a build order it also
measures what each possible answer would cost — crate DAG, hidden dependencies, build
order — without applying any of them (`dep/05` §7). All seven files in `dep/` are
generated: `dep/00-overview.md` …
`dep/05-violations.md` plus `dep/10-graph.json`; regenerate with
`python3 dep/_graph.py --write` and check with `python3 dep/_graph.py`.

A fourth organization, `term/`, is the **terminology normalization**: 78 canonical terms
(`T-01`…`T-78`), each carrying `CANONICAL_TERM`, `FORBIDDEN_VARIANTS`, `DEFINITION`, `TYPE`,
`OWNER`, `FIRST_DEFINITION` and `DEPENDENTS`; 31 non-conflation laws (`N-01`…`N-31`) enforcing
the distinctions the specification depends on — `Block ≠ ExecutablePlan`, `PlanProposal ≠
ExecutablePlan`, `CapRef ≠ Authority`, `EffectRequest ≠ EffectIssued`, `EffectIssued ≠
EffectCompleted`, `Specification ≠ Implementation`, `Implementation ≠ Verification`,
`Verification ≠ Proof`, `LLM output ≠ Authority`; and a **75-entry collision register**
(`X-01`…`X-75`, of which 4 are BLOCKING) reporting every terminology collision found in the
frozen source *and* in this repository's own documents. Its governing constraint is that a
canonical term is a name an author must **use**, never a new identifier to **introduce**: no
API, type, mathematical symbol or protocol field is renamed anywhere in `term/`. Where the
source froze two names for one thing, both are quoted; where it froze one name for two things,
both denotations are quoted; where a name is used but never declared, that is reported rather
than filled in. `term/01-dictionary.md`, `term/02-collisions.md`, `term/03-laws.md` and
`term/10-index.json` are generated from `term/_terms.py` (`python3 term/_dict.py --write`);
`python3 term/_check.py` re-greps all 803 citations against `Red-on-Rust.md`, verifies every
turn attribution from the source's own `## [n]` markers, checks all 301 term↔collision links in
both directions, and fails on drift. Twelve collisions (X-39…X-41, X-51, X-59…X-64, X-66, X-68)
are defects in `spec/`, `mod/`, `req/` or this README, wholly or in part; each is corrected in
place with its `X-` id cited and the superseded wording quoted rather than deleted. Two claims an
earlier revision of this pass had written were found to be false on re-reading the cited lines
and are **withdrawn** — quoted, not silently overwritten (R-SCOPE-03): the C-08 assertion that
`CapabilityError` never occurs as a `Fault` variant (withdrawn in `spec/06` C-08 and X-59), and
the X-64 assertion that “`Fault::StalePlan` occurs nowhere in L1–42312”, on which four documents
were amended and which the declaration sweep showed false at L28373 — all four are reverted, and
X-64 is refiled from `PHANTOM-IDENTIFIER` to `UNDECLARED-VARIANT`. See `term/00-overview.md` §6 for the full correction table.

**Status discipline:** the repository currently contains no implementation, tests, or proofs; every obligation is therefore `SPECIFIED`, and no claim has been promoted beyond that level. Where the canonicalized text and `Red-on-Rust.md` differ, the source's latest frozen text governs.

# Core Thesis
 
 
**Red-on-Rust is a deterministic, capability-scoped, resource-bounded, crash-recoverable execution machine for probabilistically generated programs.**
 
 
The central security boundary is the machine, not the language surface and not the model generating the program.
 
The fundamental property is:
 
[ \boxed{ LLMOutput\land UntrustedInput\not\Rightarrow ExternalEffect } ]
 
An external effect requires the complete chain of validation, authority, resource, policy, durability, and issuance checks.
 
[ \boxed{ ExternalEffect(E) \Rightarrow ValidatedPlan(P) \land Authorized(E,\kappa,t) \land CapabilityWithinCeiling(E) \land BudgetAvailable(E) \land DeadlineValid(E,t) \land HostPolicyOK(E) \land Issued(E) } ]
  
# Architecture
 `                    UNTRUSTED                        │                 ┌──────▼──────┐                 │ LLM /       │                 │ Planner     │                 └──────┬──────┘                        │                   PlanProposal                        │                 ┌──────▼──────┐                 │ Compiler    │                 │ parse       │                 │ validate    │                 │ lower       │                 └──────┬──────┘                        │                  ExecutablePlan                        │                 ┌──────▼──────┐                 │ CEK Machine │                 └───┬─────┬───┘                     │     │              ┌──────▼┐   ┌▼────────┐              │Capability│ │ Budget │              │ Kernel   │ │ System │              └──────┬──┘ └───┬────┘                     │        │                     └────┬───┘                          │                   Effect Issuance                          │                   Durable Boundary                          │                     ┌────▼────┐                     │  Host   │                     └─────────┘ ` 
The verification architecture is independent:
 `             Production                   │                   ▼             Observation                   ▲                   │              Reference ` 
The production implementation and executable reference model do not share core transition logic.
  
# Design Principles
 
## 1. The LLM is untrusted
 
The planner generates proposals.
 
It does not possess authority.
 
It cannot directly:
 
 
- allocate capabilities;
 
- authorize effects;
 
- modify budgets;
 
- modify scheduler state;
 
- allocate actors;
 
- invoke the host;
 
- bypass compilation;
 
- bypass persistence.
 

 
The machine evaluates the proposal after validation.
  
## 2. `Block` is not executable authority
 
The language representation is untrusted data.
 
The compiler transforms it through:
 `Block   ↓ parse   ↓ normalize   ↓ validate   ↓ lower   ↓ capability analysis   ↓ resource analysis   ↓ ExecutablePlan ` 
Critically:
 `Block ≠ ExecutablePlan ` 
Only validated executable plans enter the trusted machine.
  
## 3. Explicit CEK execution
 
Evaluation uses an explicit CEK-style machine:
 `Control Environment Continuation ` 
The evaluator does not depend on recursive host-language calls for semantic call-stack management.
 
This makes continuation state explicit, serializable, replayable, and recoverable.
 
A value is terminal only when its continuation is empty.
  
## 4. Capability-based authority
 
Authority is represented by opaque capability references.
 
The evaluator cannot inspect authority internals.
 
Capabilities can be:
 
 
- attenuated;
 
- constrained;
 
- revoked;
 
- expired;
 
- scoped to operations;
 
- scoped to targets;
 
- constrained by parameters;
 
- bounded by resources;
 
- bounded by lifetime.
 

 
Derivation satisfies:
 
[ \boxed{ derive(A,C)\preceq A } ]
 
No authority amplification is permitted.
  
## 5. Resource-bounded execution
 
Execution is bounded by multiple dimensions.
 
Consumables:
 
[ C=\langle F,I,D\rangle ]
 
where:
 
 
- F = fuel;
 
- I = I/O units;
 
- D = duration budget.
 

 
Reserved resources:
 
[ R=\langle M,S\rangle ]
 
where:
 
 
- M = memory;
 
- S = concurrency slots.
 

 
A deadline is an absolute logical-time bound.
 
Budget conservation is explicit:
 
[ C_{available}+C_{escrowed}+C_{consumed}=C_{initial} ]
 
Checked arithmetic is required.
 
Saturating subtraction is not used for semantic accounting.
  
## 6. Effects are explicit and transactional
 
External effects are represented as canonical effect descriptions.
 
A request passes through:
 `capability evaluation         ↓ target evaluation         ↓ argument evaluation         ↓ canonical Effect         ↓ capability authorization         ↓ resource checks         ↓ deadline check         ↓ host policy         ↓ durable issuance         ↓ host invocation ` 
The critical durability invariant is:
 
[ \boxed{ HostInvoked(E)\Rightarrow DurableIssued(E) } ]
 
An effect is not considered merely "issued" because an in-memory object exists.
  
## 7. Actors provide concurrency, not semantic nondeterminism
 
Actors have isolated:
 
 
- environments;
 
- continuations;
 
- heaps;
 
- mailboxes;
 
- budgets;
 
- capability contexts.
 

 
The scheduler is deterministic.
 
The baseline scheduler is FIFO with one CEK transition per actor turn.
 
Therefore:
 
[ InitialState + SchedulerTrace + HostTrace \Rightarrow UniqueMachineTrace ]
  
## 8. Authority does not cross ordinary message boundaries
 
Ordinary marshalling recursively rejects capabilities.
 
Raw capability references cannot simply be copied from one actor to another.
 
Authority transfer requires explicit delegation through the capability kernel.
 
Thus ordinary data transfer does not amplify receiver authority.
  
## 9. Canonical serialization
 
Semantic serialization is explicit and independent of Rust memory layout.
 
The canonical envelope is:
 `version:        u8 type_tag:       u8 payload_length: u32 BE payload:        bytes ` 
Canonical encoding defines semantic identity.
 
It is not based on `bincode`, struct layout, pointer addresses, allocator behavior, or platform-specific representation.
 
Malformed encodings are rejected.
 
Duplicate map keys are rejected.
 
Trailing bytes are rejected.
 
Encoded collection counts do not authorize attacker-controlled preallocation.
  
## 10. Crash recovery is causal
 
Persistence consists of:
 `Snapshot    + WAL    + Effect Journal ` 
Effect lifecycle:
 `Prepared    ↓ Issued    ↓ Completed ` 
or:
 `Issued    ↓ Reconciled ` 
A prepared-but-never-issued effect is discarded.
 
An issued-but-not-completed effect is:
 `Indeterminate ` 
unless an authoritative host reconciliation protocol establishes its outcome.
 
The system never infers "not executed" merely because a completion record is missing.
  
# Repository Structure
 `red-on-rust/ ├── Cargo.toml ├── Cargo.lock ├── rust-toolchain.toml │ ├── crates/ │   ├── ror-core/ │   ├── ror-compiler/ │   ├── ror-kernel/ │   ├── ror-runtime/ │   ├── ror-persistence/ │   ├── ror-host/ │   ├── ror-agent/ │   │ │   ├── ror-reference/ │   ├── ror-differential/ │   └── ror-testkit/ │ ├── tests/ │   ├── conformance/ │   ├── exhaustive/ │   ├── property/ │   ├── mutation/ │   ├── crash/ │   └── stress/ │ ├── vectors/ │   ├── canonical/ │   ├── persistence/ │   └── effects/ │ ├── mutations/ │   └── registry.toml │ ├── docs/ │   ├── architecture/ │   ├── semantics/ │   ├── verification/ │   └── security/ │ └── scripts/ ` 
### Crates
 
  
 
Crate
 
Responsibility
 
   
 
`ror-core`
 
Semantic domain types and foundational interfaces
 
 
 
`ror-compiler`
 
Parse, validate, lower, capability/resource analysis
 
 
 
`ror-kernel`
 
Capability authority, revocation, authorization, resource decisions
 
 
 
`ror-runtime`
 
CEK machine, actors, scheduler, effects
 
 
 
`ror-persistence`
 
WAL, snapshots, effect journal, recovery
 
 
 
`ror-host`
 
Host execution and replay boundaries
 
 
 
`ror-agent`
 
Planner/observation/supervisor integration
 
 
 
`ror-reference`
 
Independent executable semantic model
 
 
 
`ror-differential`
 
Generator, runner, comparator, shrinking
 
 
 
`ror-testkit`
 
Test infrastructure and controlled doubles
 
  
  
# Trust Model
 
  
 
Component
 
Trust
 
Role
 
   
 
LLM / planner
 
No
 
Proposal generation
 
 
 
`Block`
 
No
 
Untrusted program data
 
 
 
Compiler
 
Yes
 
Executable invariants
 
 
 
Capability kernel
 
Yes
 
Authority decisions
 
 
 
CEK machine
 
Yes
 
Deterministic execution
 
 
 
Scheduler
 
Yes
 
Deterministic interleaving
 
 
 
Budget system
 
Yes
 
Resource conservation
 
 
 
Persistence
 
Yes
 
Durable machine state
 
 
 
Effect journal
 
Yes
 
Causal effect state
 
 
 
Replay host
 
Yes
 
Recorded-effect reconstruction
 
 
 
Live host
 
Partial
 
External-world execution
 
 
 
Supervisor
 
Yes
 
Lifecycle and recovery
 
  
 
The trusted computing base is intentionally explicit.
  
# Verification Strategy
 
Red-on-Rust does not rely on a single testing technique.
 
## Independent reference model
 
The reference implementation independently models:
 
 
- CEK evaluation;
 
- lexical environments;
 
- closures;
 
- calls;
 
- capability derivation;
 
- revocation;
 
- budgets;
 
- actors;
 
- scheduling;
 
- effects;
 
- persistence;
 
- recovery.
 

 
Production and reference implementations are compared through normalized semantic observations.
  
## Differential testing
 
The principal semantic oracle is:
 
# [ \boxed{ Observe(Production(X))
 
Observe(Reference(X)) } ]
 
The comparator reports the first divergence.
 
Internal implementation details such as memory addresses and Rust layout are excluded unless semantically relevant.
  
## Exhaustive testing
 
Small-state enumeration covers the frozen calculus over bounded state spaces.
 
Baseline targets include:
 `expression depth ≤ 4 actors ≤ 2 capabilities ≤ 2 ` 
CI performance limits are treated as engineering budgets, not reasons to reduce semantic coverage.
  
## Property-based testing
 
Randomized tests exercise larger generated state spaces.
 
Every test is reproducible from an explicit seed and versioned generator metadata.
  
## Mutation testing
 
Known semantic defects are deliberately injected.
 
Examples include:
 
 
- reversing argument evaluation order;
 
- skipping arity checks;
 
- accepting revoked capabilities;
 
- amplifying authority;
 
- omitting budget gates;
 
- releasing indeterminate effect escrow;
 
- scheduling blocked actors;
 
- accepting duplicate runnable entries;
 
- ignoring WAL gaps;
 
- accepting checksum failures;
 
- accepting mismatched effect digests.
 

 
The target is:
 
[ \boxed{ MutationKillRate=100% } ]
 
for all registered non-equivalent mutations.
  
## Crash testing
 
The effect protocol is tested at:
 `T0 BeforePrepared T1 AfterPrepared T2 AfterIssued T3 AfterHostInvocation T4 AfterHostCompletion T5 AfterCompleted T6 AfterSnapshotCommit ` 
Recovery must preserve the frozen causal semantics at every crash point.
  
# Verification Contract
 
Every frozen requirement receives a stable obligation ID.
 
Examples:
 `CEK-CALL-ARITY-PRECHECK CEK-CALL-ARGS-LTR CEK-CLOSURE-LEXICAL-CAPTURE  CAP-DERIVE-NO-AMPLIFICATION CAP-REVOCATION-ANCESTOR  BUDGET-ESCROW-CONSERVATION  EFFECT-ISSUE-DURABLE-BEFORE-HOST EFFECT-RECEIPT-DIGEST-VALIDATION  SCHED-FIFO SCHED-BLOCKED-NOT-SCHEDULED  MARSHAL-CAPABILITY-REJECT  WAL-GAP-REJECT RECOVERY-ISSUED-INDETERMINATE ` 
Coverage metrics are evidence.
 
They do not replace differential agreement.
  
# Reproducible Counterexamples
 
A failed generated case records:
 `seed generator_version semantic_version test_case_version accepted_plan_trace scheduler_trace host_trace crash_trace minimized_input production_observation reference_observation first_divergence ` 
Every failure should be reproducible locally.
 
Divergences are classified as:
 `production defect reference defect harness defect specification ambiguity ` 
Specification ambiguity must be resolved explicitly rather than hidden in a test adjustment.
  
# Security Invariants
 
The implementation is designed around several non-negotiable invariants.
 
### No unauthorized external effects
 
[ \boxed{ \neg Authorized(E,\kappa,t) \Rightarrow \neg ExternalEffect(E) } ]
 
### No authority amplification
 
[ \boxed{ derive(A,C)\preceq A } ]
 
### No budget teleportation
 
[ \boxed{ C_{available}+C_{escrowed}+C_{consumed}=C_{initial} } ]
 
### No host-before-durability
 
[ \boxed{ HostInvoked(E)\Rightarrow DurableIssued(E) } ]
 
### No raw capability transfer
 
# [ \boxed{ OrdinaryMarshal(Value::Capability)
 
Rejected } ]
 
### No silent recovery corruption
 
Invalid persistence state produces an explicit recovery fault.
 
It is never silently repaired by mutation.
  
# Development Sequence
 
Implementation proceeds in dependency order:
 `01. Core domain types 02. Canonical serialization 03. Compiler artifacts 04. Capability kernel 05. Budget algebra 06. CEK evaluator 07. Lambda / Call 08. Attenuation 09. Effects 10. Actors 11. Scheduler 12. Marshalling / delegation 13. Persistence 14. Crash recovery 15. LLM boundary 16. Reference model 17. Differential harness 18. Mutation framework 19. CI 20. Stress / security validation ` 
The independent reference model and differential infrastructure should be established as early as practical rather than postponed until the production runtime is complete.
  
# Engineering Rules
 
The following shortcuts are prohibited:
 
 
- recursive evaluator implementation;
 
- hidden authority inspection;
 
- implicit capability creation;
 
- wholesale capability copying;
 
- raw capability transfer through ordinary messages;
 
- saturating resource subtraction;
 
- wall-clock time as semantic machine state;
 
- host invocation before durable issuance;
 
- treating incomplete effects as automatically unexecuted;
 
- silent persistence repair;
 
- unordered replay;
 
- production/reference implementation reuse;
 
- comparing only final return values;
 
- weakening tests to accommodate implementation convenience.
 

  
# Current Milestones
 `M0  Workspace bootstrap M1  Canonical serialization M2  Pure CEK M3  Lambda / Call M4  Capability / Attenuation M5  Effects M6  Actors M7  Persistence M8  Differential verification M9  Mutation gate M10 Crash/recovery gate M11 Release candidate ` 
A milestone is complete only when its corresponding verification obligations are satisfied.
  
# Conformance Claim
 
The project deliberately avoids claiming that test execution constitutes a mathematical proof of the entire calculus.
 
The appropriate engineering claim is:
 
 
**The independent reference model, exhaustive/property-based tests, mutation testing, and crash-injection suite provide machine-checked evidence that the implementation conforms to the frozen calculus over the tested state space.**
 
 
Formal mechanization may provide stronger guarantees in the future, but it is not required to begin implementation.
  
# Why Red-on-Rust?
 
Probabilistic systems can generate useful programs.
 
They should not receive implicit authority merely because those programs look plausible.
 
Red-on-Rust therefore separates:
 `generation from validation  validation from execution  execution from authority  authority from resources  resources from external effects  external effects from durability  durability from recovery ` 
The resulting machine is intended to make consequential computation:
 `explicit bounded authorized deterministic observable recoverable ` 
while retaining a highly compositional, homoiconic programming model above the substrate.
  
# Project Status
 
**RED-ON-RUST**
 `Architecture       FROZEN Semantics          FROZEN Trust Model        FROZEN Verification       FROZEN Repository         BOOTSTRAP Implementation     READY ` 
The architecture is closed.
 
The remaining work is engineering:
 `implementation testing benchmarking mutation validation crash validation security review formal mechanization where desired ` 
 
**The machine is the security boundary.**
 
**The LLM is a proposal engine, not an authority.**
 
**The specification is frozen; implementation evidence now determines conformance.**
