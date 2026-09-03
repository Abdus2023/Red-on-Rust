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
- `spec/03-obligation-matrix.md` — 184 stable requirement IDs (`R-…`; 148 from the frozen source + 36 post-audit frozen addenda, incl. the five addendum-VII, three addendum-VIII and three addendum-IX obligations) with status and provenance
- `spec/04-dependency-graph.md` — section, object, and verification dependency graphs
- `spec/05-terminology.md` — glossary and normalization rules
- `spec/06-contradictions-ambiguities.md` — 112 consistency findings in 113 rows (`C-01`…`C-115`, C-39 a pointer row; C-98…C-102 added by the semantic-nondeterminism audit, C-103…C-109 by the request-pipeline proof-obligation audit and C-112…C-115 by the duration-semantics audit, C-103…C-107/C-109 `resolved-by-addendum` under addendum VII, C-108 under addendum VIII and C-100/C-112…C-115 under addendum IX; C-46…C-76 added by the terminology pass and C-77…C-97 by the post-audit frozen addenda I–V; C-08 re-graded MINOR → MAJOR, and C-54 rewritten by its declaration sweep after the first version of that row was filed on a false premise)
- `spec/07-implementation-mapping.md` — obligations → crate/module mapping; actual repository state
- `spec/08-verification-mapping.md` — obligations → conformance tests and evidence status
- `spec/09-unresolved-decisions.md` — 39 items (`U-…`) requiring explicit architectural decisions (U-23…U-25 added by the terminology pass, U-26…U-29 by its declaration sweep, U-30…U-34 by its struct-field sweep, U-35…U-38 by the semantic-nondeterminism audit (U-38 by its checker-mutation pass) and U-39…U-45 by the request-pipeline proof-obligation audit, U-39…U-44 resolved by addendum VII, U-45 by addendum VIII, U-01/U-07/U-36 by addendum IX and U-38 by the repository-gate adoption of option (b) (2026-09-03); U-08 corrected and U-14 escalated to blocking by its fault-taxonomy audit)
- `spec/10-index.json` — machine-readable cross-index

A fifth directory, `audit/`, holds **adversarial audits of the frozen specification**.
These are review artifacts, not normative text: an audit may file register rows
(`C-…`, `U-…`) and propose remediation, but it never issues frozen semantics
(R-SCOPE-03). Five passes are complete:

- `audit/authority-trust-external-effect-audit.md` — **authority, trust-boundary and
  external-effect gating** (`SEC-001`…`SEC-023`: 3 CRITICAL, 5 HIGH, 3 MEDIUM-HIGH,
  9 MEDIUM, 2 LOW/MEDIUM, 1 LOW). Verdict: the invariants `LLMOutput ∧ UntrustedInput
  ↛ ExternalEffect` and the 7-conjunct effect chain do **not** hold at specification
  level. Its findings were remediated by the 25 frozen addenda now in `spec/01`
  (`R-CORE-11`…`R-CORE-13`, `R-EFFECT-08`, `R-HOST-06`, `R-CAP-10`, `R-KERN-06`,
  `R-PERSIST-07/08`, `R-ACTOR-09/10`, `R-BUDGET-09`, `R-RECOV-08`, `R-CANON-12/13`, …),
  which is why `C-77`…`C-97` read `resolved-by-addendum`.
- `audit/semantic-nondeterminism-audit.md` — **semantic nondeterminism** (`DET-001`…
  `DET-018`: 2 CRITICAL, 5 HIGH, 6 MEDIUM, 3 LOW-MEDIUM, 2 CLEAN), auditing the
  determinism theorem `InitialState + SchedulerTrace + HostTrace ⇒ UniqueMachineTrace`
  across fifteen categories. Verdict: **NOT VERIFIED**, on two independent grounds.
  (1) The theorem is *ill-formed* — `SchedulerTrace`, `HostTrace`, `InitialState` and
  `UniqueMachineTrace` are undefined in all 42,312 source lines and in all five
  canonical organizations; all 13 occurrences of `SchedulerTrace` sit inside the boxed
  formula, so the claim is currently unfalsifiable. (2) Under the charitable reading the
  transition function reads **eleven inputs the theorem does not name** — among them
  per-process hash-seed randomization, a wall-clock `Lifetime` compared against
  `LogicalTime` inside authorization gate 6, the kernel arena's residence outside
  `GlobalState`, and filesystem-order-dependent snapshot selection. Two categories are
  **clean** and recorded as such so the negative results are auditable: floating-point
  dependence (zero `f32`/`f64`) and implicit environment variables (zero `std::env`).
  This pass issued no addendum: its rows `C-98`…`C-102` and decisions `U-35`…`U-37` are
  all `open`, and `U-02`/`U-07` gained appended amendment notes rather than rewrites.

  Its §5.4 states the replay claim in the only form the corpus supports: **replay proves
  machine-state/event reproduction subject to explicit external-effect reconciliation —
  it does not reproduce the external world.** A receipt records what the machine was
  told, not what happened; the `Indeterminate` class (L26714) is irreducible, and
  R-DUR-04/R-RECOV-08 forbid any component resolving it on local policy.
- `audit/request-pipeline-proof-obligation-matrix.md` — **every path from `Expr::Request`
  to a host-visible effect** (GAP-01…GAP-18: 2 CRITICAL, 2 BLOCKING, 6 HIGH incl. one
  historical/resolved-in-principle, 1 MAJOR, 6 MEDIUM, 1 LOW/MEDIUM, 1 INFO).
  Verdict: the 16-step gate sequence is sound and `HostInvoked(E) ⇒ DurableIssued(E)`
  is *realizable* through R-DUR-01/R-CORE-06/PanicHost/R-TRUST-05, but it is **not
  provable as frozen** on four counts — `spec/01` S-12 still publishes the superseded
  host-before-Issued 16-step order, live journal/fsync failure at step 14 is unpinned
  (no fault, no rollback, R-EFFECT-04's five assertions unsatisfiable), the durable
  `Prepared`/`Issued` records carry no effect or cost so escrow survival and T1 budget
  restoration have no source of truth, and the step-10 deadline premise is pinned weak
  against the formal `t + δ_t(req) ≤ W`. This pass issued no addendum — at filing
  (2026-09-03, historical snapshot) its rows `C-103`…`C-109` and decisions
  `U-39`…`U-45` were all `open`; its recommendations exist only as a draft
  (`audit/request-pipeline-remediation-draft.md`, NOT ADOPTED). Addenda VII and VIII
  subsequently resolved U-39…U-44 (re-grading C-103…C-107/C-109) and U-45 (C-108);
  current per-row state is canonical in `spec/06`/`spec/09`, and the historical/current
  disposition is projected in `state/`.
- `audit/duration-semantics-audit.md` — **what `D` measures and how logical time advances**
  (U-01/U-07/U-36; the audit filed C-112…C-115 and scoped the cluster into D1–D8; pre-adoption
  owner decisions D1–D3/D6/D8 approved with D7 conditional on its own §5 evidence). Verdict:
  the invariant "every logical-time advance has exactly one duration debit, and every
  deadline-sensitive transition has a deterministic pre-state/post-state rule" fails in three
  places — the quiescence clock hole (a `Pending` effect freezes `t`, so R-BUDGET-09's
  liveness bound is unreachable), the missing post-deadline receipt rule, and three mutually
  inconsistent `D` debit models — plus the unfrozen `DeadlineExceeded` firing point. Its
  remediation is addendum IX (`R-CAP-11`, `R-BUDGET-15/16`): C-100/C-112…C-115 re-graded
  `resolved-by-addendum`, U-01/U-07/U-36 resolved, R-BUDGET-12 folded, U-38 untouched.
- `audit/persistence-crash-consistency-audit.md` — **effect causality and the T0–T6
  crash matrix** (`Issued ⇒ Prepared`, `Completed ⇒ Issued`, `Reconciled ⇒ Issued`;
  `HostInvoked ⇒ DurableIssued`; `Prepared ∧ ¬Issued ⇒ Discard`;
  `Issued ∧ ¬Completed ⇒ Indeterminate`, never auto-`NotExecuted`;
  `Invalid(D) ⇒ RecoveryFault`, no silent repair). Verdict: **the persistence
  contract satisfies the requested crash-consistency property**, provided the frozen
  addenda are treated as normative (R-DUR-06/07, R-RECOV-09, R-HOST-06 make T1/T2–T4/T5
  implementable). The only substantive residual is the existing recovery-step
  granularity discrepancy AMB-27/REQ-RECOV-021 (reconciliation inside `Recover(D)`
  vs after `RecoveryComplete`). This pass filed no new `C-`/`U-` rows; it added
  `audit/_crash_consistency_checker.py` as a mechanical gate so a future weakening of
  any verified clause fails `check.py`.

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
four layers (10 crates / 17 crate edges, 17 modules / 134 typed module edges, 545 atomic
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

**Running the checks.** `python3 check.py` runs every checker in the repository in
dependency order and exits non-zero if any fails. It also fails when a `*/_*.py`
executable is neither run nor explicitly classified as a data module or
write-mode generator, so a new gate cannot sit unattended: `term/_structs.py`
did exactly that, and a `ReplayHost` shape count it disproves stood wrong in five
documents until it was finally run. `python3 check.py --list` shows the inventory.
Generators run in check mode, so a generator whose output would change is a
failure rather than a silent fix.

A fourth organization, `term/`, is the **terminology normalization**: 86 canonical terms
(`T-01`…`T-86`), each carrying `CANONICAL_TERM`, `FORBIDDEN_VARIANTS`, `DEFINITION`, `TYPE`,
`OWNER`, `FIRST_DEFINITION` and `DEPENDENTS`; 33 non-conflation laws (`N-01`…`N-33`) enforcing
the distinctions the specification depends on — `Block ≠ ExecutablePlan`, `PlanProposal ≠
ExecutablePlan`, `CapRef ≠ Authority`, `EffectRequest ≠ EffectIssued`, `EffectIssued ≠
EffectCompleted`, `Specification ≠ Implementation`, `Implementation ≠ Verification`,
`Verification ≠ Proof`, `LLM output ≠ Authority`; and an **86-entry collision register**
(`X-01`…`X-87`, of which 4 are BLOCKING) reporting every terminology collision found in the
frozen source *and* in this repository's own documents. Its governing constraint is that a
canonical term is a name an author must **use**, never a new identifier to **introduce**: no
API, type, mathematical symbol or protocol field is renamed anywhere in `term/`. Where the
source froze two names for one thing, both are quoted; where it froze one name for two things,
both denotations are quoted; where a name is used but never declared, that is reported rather
than filled in. `term/01-dictionary.md`, `term/02-collisions.md`, `term/03-laws.md` and
`term/10-index.json` are generated from `term/_terms.py` (`python3 term/_dict.py --write`);
`python3 term/_check.py` re-greps all 1025 citations against `Red-on-Rust.md`, verifies every
turn attribution from the source's own `## [n]` markers, checks all 372 term↔collision links in
both directions, and fails on drift; `python3 term/_structs.py` re-derives every declaration. Twelve collisions (X-39…X-41, X-51, X-59…X-64, X-66, X-68)
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
 
[ \boxed{ ExternalEffect(E) \Rightarrow ValidatedRequest(E) \land Authorized(E,\kappa,t) \land CapabilityWithinCeiling(E) \land BudgetAvailable(E) \land DeadlineValid(E,t) \land HostPolicyOK(E) \land Issued(E) } ]
  
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
**FINAL1 compilation (`final/`).** A sixth organization compiles the five above into ONE canonical
specification in the FINAL1-mandated 29-section order: `final/01-canonical-specification.md`
re-homes every normative row of `spec/01` **verbatim** (whitespace-normalized, chunk-multiset
identity enforced by the generator) with the consolidated global-invariant index (§23–§25) and the
full requirement registry (§26, table body identical to `final/03`); `final/00` explains the set;
`final/02` is the section index; `final/04` carries the verification registry (`spec/08` body,
binding); `final/05` is the global-invariant registry (36 `GI-…` rows over the existing `R-…` homes —
additive IDs only, no restated semantics); `final/06` is the terminology glossary (`spec/05` plus the
`term/` registers); `final/07` is the computed dependency/reference integrity report; `final/08` the
evidence-status matrix; `final/09` the open-architectural-decisions ledger (all statuses computed from
`spec/09`/`spec/06`); `final/10` the canonicalization report and final-validation checklist. Nothing is
renumbered, promoted, or adjudicated: `REF1-CONDITIONAL`/`V1-CONDITIONAL`, every `SPECIFIED` status,
and every open `U-`/`C-` row are carried as they stand. Generated by `python3 final/_build.py --write`;
`python3 final/_build.py` (check mode) is registered in `check.py` and fails the repository gate on any
drift, and the same run re-executes the structural battery whose results are printed in `final/07` —
integrity evidence only, never semantic verification (R-SCOPE-02). Where `final/` and `Red-on-Rust.md`
differ, the source's latest frozen text governs, as everywhere in this repository. This paragraph is
appended after the *Project Status* block (line-anchored citations above, `README.md` L12/L148/L815,
are exact-position and forbid inserting ahead of them); it adds no normative content.

**R-REG machine-readable registry (`reg/`).** `reg/requirements.json` compiles the canonical requirement
registry (`final/03` ← `spec/03`) and the canonical statements (`spec/01`, re-homed verbatim in `final/01`)
into one JSON record per requirement (184/184 identity, schema in `reg/requirements.schema.json`), with
the compilation, identity/diff, status-transition, provenance, dependency-integrity, evidence-coverage,
security-relevance and determinism/hash reports beside it (`reg/00`–`08`). It is a **derived artifact**:
statuses, mappings and statements are copied from the authorities, every derivation rule is recorded in
the record (`*_basis` / `*_source`), and `python3 reg/_compile.py` (check mode, registered in `check.py`)
fails on any drift or on any disagreement with the canonical registry rather than choosing a value. It
promotes nothing: all 184 remain `SPECIFIED`, `implementation_targets`/`test_targets` are registered
contracts (no crate or test exists here), `evidence` is empty for every row, `REF1-CONDITIONAL` and
`V1-CONDITIONAL` stay conditional, and a green `check.py` is repository-integrity evidence only.
Status changes are admitted solely through the append-only `reg/status-transitions.json` ledger.

**Repository-state projection and disposition registry (`state/`).** A seventh organization holds
the historical/current disposition machinery and the single repository-state projection, created by
the 2026-09-03 canonicalization repair pass. `state/dispositions.json` (authored) binds each
finding or finding-family to the governance action that resolved or carried it — historical audit
content stays immutable — and sha256-pins the **12 protected historical audit snapshots**: editing a
protected audit is a provenance violation until its disposition record is deliberately updated.
`state/repository-state.json`, `state/01-repository-state.md` and `state/02-dispositions.md`
(generated by `python3 state/_project.py --write`) project the current state and nothing else:
U-registry counts (39 registered = 28 open + 11 resolved, numeric max U-45 — the numbering gaps are
gaps in numbering, never missing records), checker inventory (18 checkers + 7 classified
non-checkers, derived from the `check.py` registration), the canonical tag set (25 indexed = 16
frozen + 9 addendum; 1 documented alias not indexed), the R-CORE-02⇔R-CORE-11 predicate agreement,
mutation registry (42, none executed), and the conditional statuses (`REF1-CONDITIONAL`,
`V1-CONDITIONAL`). Every figure is **derived** from the authoritative registers — none is
hard-coded to make a gate pass — and the projection itself declares it is not a normative source:
where a projection and an authority differ, the authority governs and the gate fails. Check mode is
registered in `check.py` and runs the fail-closed cross-artifact battery (registry ≠ projection,
registered cardinality ≠ numeric identifier maximum, indexed tag set = the authority's tables,
alias ≠ indexed, five-authority requirement identity, disposition coverage and hash verification,
zero claims). Like every generated set it promotes nothing and verifies nothing: a green
projection is repository-integrity evidence only, never semantic verification.


# Specification Pipeline (S0–S7)

The repository's specification is now also a *processed* one: `scripts/spec/pipeline.py` turns the
frozen seed source into a deterministic, provenance-bearing artifact set without ever becoming an
authority. It exists because the same failure kept recurring in this repository's history — a figure
hand-copied into a summary, a register that agreed with itself and nothing else, a checker nobody
ran. A projector that cannot invent is the only kind of generator that is safe next to a
specification this large: 42,312 lines, 184 requirements, 545 atomic obligations, 112 findings, 39
open decisions.

    python3 scripts/spec/pipeline.py Red-on-Rust.md          # render -> build/spec/ (gitignored)
    python3 scripts/spec/pipeline.py --check                 # prove the build set is current
    python3 scripts/spec/pipeline.py --report                # print the transformation report
    python3 scripts/spec/pipeline.py --publish-derived       # rewrite spec/0*-*/, PIPELINE.md, report
    python3 scripts/spec/_gate.py                            # determinism + idempotence + freshness
    python3 tests/spec/_pipeline_mutations.py                # deliberate drifts; all must be caught
    python3 scripts/spec/pipeline.py --list                  # stages and their contracts

Stages: S0 SNAPSHOT (hash the source, read-only) → S1 EXTRACT (candidates, normative class) →
S2 SPLIT (lossless sections, `spec/02` order) → S3 NORMALIZE (terminology and predicate registration,
never a rewrite) → S4 AUDIT (sixteen categories, integrity scans) → S5 CANONICALIZE (a
*reconstruction* whose chunk multiset must equal `spec/01`'s) → S6 REGISTER → S6b VECTORS →
S7 VERIFY (forty cross-artifact checks over every projection). The distinction the whole design rests
on is preserved at every hop: `SOURCE ≠ PROPOSAL ≠ DERIVED ARTIFACT ≠ CANONICAL AUTHORITY`. An LLM (or
a generator, or a human) may propose; only deterministic validators adjudicate, and they adjudicate
*agreement with the registers*, never machine conformance.

Consequences worth stating plainly:

- **It cannot add a requirement.** `Canonicalize(X) ⊆ NormativeContent(X)` is enforced by chunk-multiset
  equality against `spec/01`; an unregistered identity aborts the run (§14: fail closed).
- **It cannot promote a status.** Every row leaves `S5` at `SPECIFIED`. The ceiling is the repository's
  evidence ceiling, not a default: no generated artifact claims implemented, tested, verified or proven.
- **It cannot repair history silently.** The twelve `audit/*.md` snapshots are sha256-pinned in
  `state/dispositions.json`; a dangling citation is emitted as a *candidate* finding with a suggested id
  and `candidate_findings_filed_by_this_run: 0`. Nothing is auto-fixed, because an auto-fix is a guess
  wearing a check mark.
- **It cannot go stale unnoticed.** Every committed derived file (`spec/00-source/`…`spec/05-vectors/`,
  `spec/PIPELINE.md`, `TRANSFORMATION-REPORT.md`) is re-rendered and byte-compared by
  `scripts/spec/_gate.py`, which is registered in `check.py`; `build/spec/` is gitignored because it is
  reproducible, and it is never read back as input — a derived artifact feeding a generator is how a
  projection becomes a second authority.
- **It proves its own teeth.** `tests/spec/_pipeline_mutations.py` injects deliberate drift into a
  scratch copy — source edit, silent deletion, renumbering, duplicate row, promotion, authority-text
  drift, provenance strip, invented requirement, dropped section, deleted finding, falsely-resolved
  decision, broken register shape, edited history, hand-edited pointer, stale build set, injected
  timestamp, opened proposal intake, an ignored failure, a register that contradicts itself — and fails
  if any of it goes unnoticed. A survivor is a hard failure of the battery and therefore of
  `python3 check.py`, so this is an enforced invariant, not a remembered score.
- **Determinism is measured across processes, not asserted inside one.** The same battery renders the
  whole pipeline in separate interpreters under `PYTHONHASHSEED` variants (including `random`),
  `LC_ALL=C`, a Turkish-locale case-fold, a foreign timezone and a different working directory, and
  requires one content address. That section is what found a real defect here: the environment report
  echoed `PYTHONHASHSEED` into `verification.json`, so one render had several addresses — a host value
  in a content-addressed artifact is the same mistake as a timestamp, and the report now names what it
  ignores instead of recording values.
- **A failure cannot become decoration.** Stage rows come in two kinds, and S7 aborts a run in which a
  *conformance* row reported False while publication continued; *disclosures* (an open finding touching
  canonical material, a dangling citation inside an authority) print as `NOTE`, are counted, and are
  never presented as passes — because a check that fails harmlessly trains its reader to ignore checks.

What it does *not* do: it is not a second governance system (§20 — `spec/01`, `spec/03`, `spec/06`,
`spec/09` and the frozen source stay the single homes of their content; the `spec/0N-*/` directories are
pointer indices that say so on their first line), it starts nothing (M0 remains `NOT STARTED`, and the
gate fails if a `.rs` file or `Cargo.toml` appears anywhere), and a green run is repository-integrity
evidence only — never verification of an obligation.
