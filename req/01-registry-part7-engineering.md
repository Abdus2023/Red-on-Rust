# Atomic Requirement Registry — Part 7: Engineering, Order, and Claims (S-22 … S-24)

Areas: `REPO` (19), `ORDER` (25), `CLAIM` (22) — 66 atomic units.

---

## S-22 Repository structure and crate responsibilities

### REQ-REPO-001
- REQ-ID: REQ-REPO-001
- CATEGORY: repository-structure
- SOURCE: Red-on-Rust.md L39140–39195([58]); L41161–41200([58] §39); spec/01 S-22 R-REPO-01
- NORMATIVE-LEVEL: MUST
- STATEMENT: The workspace separates the pipeline untrusted language data → compiler → trusted executable representation → machine → authority/resources → durable effects → host.
- PRECONDITIONS: workspace layout
- POSTCONDITIONS: each stage is a distinct unit
- INVARIANTS: —
- DEPENDENCIES: REQ-ARCH-001
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: layout review
- EVIDENCE-STATUS: SPECIFIED

### REQ-REPO-002
- REQ-ID: REQ-REPO-002
- CATEGORY: repository-structure
- SOURCE: Red-on-Rust.md L41205–41215([58] §39); L41406–41424([60]); spec/01 S-22 R-REPO-01
- NORMATIVE-LEVEL: MUST
- STATEMENT: The workspace independently maintains the Production ↔ Observation ↔ Reference axis.
- PRECONDITIONS: workspace layout
- POSTCONDITIONS: the verification axis is separate from the production pipeline
- INVARIANTS: —
- DEPENDENCIES: REQ-ARCH-002
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: layout review
- EVIDENCE-STATUS: SPECIFIED

### REQ-REPO-003
- REQ-ID: REQ-REPO-003
- CATEGORY: repository-structure
- SOURCE: Red-on-Rust.md L39140–39195([58]); spec/01 S-22 R-REPO-01
- NORMATIVE-LEVEL: MAY
- STATEMENT: Top-level names may change for organizational reasons.
- PRECONDITIONS: renaming for organization
- POSTCONDITIONS: —
- INVARIANTS: —
- DEPENDENCIES: REQ-REPO-004
- SECURITY-IMPACT: low
- VERIFICATION-METHOD: not applicable (permission)
- EVIDENCE-STATUS: SPECIFIED

### REQ-REPO-004
- REQ-ID: REQ-REPO-004
- CATEGORY: repository-structure
- SOURCE: Red-on-Rust.md L39140–39195([58]); spec/01 S-22 R-REPO-01
- NORMATIVE-LEVEL: MUST NOT
- STATEMENT: Dependency and trust boundaries must not change.
- PRECONDITIONS: any reorganization
- POSTCONDITIONS: boundaries are preserved
- INVARIANTS: —
- DEPENDENCIES: REQ-ARCH-006, REQ-REPO-017
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: Cargo dependency review
- EVIDENCE-STATUS: SPECIFIED

### REQ-REPO-005
- REQ-ID: REQ-REPO-005
- CATEGORY: repository-structure
- SOURCE: Red-on-Rust.md L39140–39195([58]); spec/01 S-22 R-REPO-01
- NORMATIVE-LEVEL: SHOULD
- STATEMENT: The frozen-intent layout is `crates/{ror-core, ror-compiler, ror-kernel, ror-runtime, ror-persistence, ror-host, ror-agent, ror-reference, ror-differential, ror-testkit}`, `tests/{conformance, exhaustive, property, mutation, crash, stress}`, `vectors/{canonical, persistence, effects}`, `mutations/registry.toml`, `docs/{architecture, semantics, verification, security}`, `scripts/`.
- PRECONDITIONS: workspace creation
- POSTCONDITIONS: the directories exist
- INVARIANTS: —
- DEPENDENCIES: REQ-ORDER-023
- SECURITY-IMPACT: medium
- VERIFICATION-METHOD: layout review (M0)
- EVIDENCE-STATUS: SPECIFIED

### REQ-REPO-006
- REQ-ID: REQ-REPO-006
- CATEGORY: repository-structure
- SOURCE: Red-on-Rust.md L39196–39260([58]); spec/01 S-22 R-REPO-02
- NORMATIVE-LEVEL: MUST
- STATEMENT: `ror-core` holds the lowest-level semantic domain (`Symbol`, `ActorId`, `CapRef`, `EffectId`, `EventSequence`, `LogicalTime`, `Expr`, `Value`, `FunctionValue`, `Environment`, `Constraint`, `Effect`, `EffectCost`, `Budget`, `Consumable`, `Reserved`, `Fault`, `MachineEvent`) and depends on std only.
- PRECONDITIONS: crate layout
- POSTCONDITIONS: no non-std dependencies
- INVARIANTS: —
- DEPENDENCIES: REQ-REPO-007
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: Cargo dependency review
- EVIDENCE-STATUS: SPECIFIED

### REQ-REPO-007
- REQ-ID: REQ-REPO-007
- CATEGORY: repository-structure
- SOURCE: Red-on-Rust.md L39196–39260([58]); spec/01 S-22 R-REPO-02
- NORMATIVE-LEVEL: MUST NOT
- STATEMENT: `ror-core` MUST NOT contain host calls, filesystem access, networking, scheduler, persistence, capability authority storage, or LLM integration.
- PRECONDITIONS: `ror-core` implementation
- POSTCONDITIONS: none of the seven is present
- INVARIANTS: —
- DEPENDENCIES: REQ-REPO-006
- SECURITY-IMPACT: critical (a core crate with host access would be an unbounded TCB)
- VERIFICATION-METHOD: dependency review; code review
- EVIDENCE-STATUS: SPECIFIED

### REQ-REPO-008
- REQ-ID: REQ-REPO-008
- CATEGORY: repository-structure
- SOURCE: Red-on-Rust.md L39253–39320([58]); spec/01 S-22 R-REPO-02
- NORMATIVE-LEVEL: MUST
- STATEMENT: `ror-compiler` performs `Block → parse → NormalizedAST → ValidatedPlan → PlanIR → capability analysis → resource analysis → ExecutablePlan`, with `ExecutablePlan` constructors private.
- PRECONDITIONS: crate layout
- POSTCONDITIONS: the pipeline and privacy hold
- INVARIANTS: —
- DEPENDENCIES: REQ-COMPILE-004, REQ-COMPILE-013
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: visibility review
- EVIDENCE-STATUS: SPECIFIED

### REQ-REPO-009
- REQ-ID: REQ-REPO-009
- CATEGORY: repository-structure
- SOURCE: Red-on-Rust.md L39370–39410([58]); spec/01 S-22 R-REPO-02
- NORMATIVE-LEVEL: MUST
- STATEMENT: `ror-kernel` holds `CapabilityKernel`, `AuthorityNode`, derivation, revocation, authorization, budget primitives, and logical-time validation; `AuthorityNode` is invisible to evaluator and runtime.
- PRECONDITIONS: crate layout
- POSTCONDITIONS: authority state is unreachable outside the kernel
- INVARIANTS: `CapRef ⇏ AuthorityInspection`
- DEPENDENCIES: REQ-KERN-006
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: Rust visibility review
- EVIDENCE-STATUS: SPECIFIED

### REQ-REPO-010
- REQ-ID: REQ-REPO-010
- CATEGORY: repository-structure
- SOURCE: Red-on-Rust.md L39196–40762([58]); spec/01 S-22 R-REPO-02
- NORMATIVE-LEVEL: MUST
- STATEMENT: `ror-runtime` holds the CEK machine, actors, scheduler, and effects.
- PRECONDITIONS: crate layout
- POSTCONDITIONS: —
- INVARIANTS: —
- DEPENDENCIES: REQ-ARCH-006
- SECURITY-IMPACT: medium
- VERIFICATION-METHOD: layout review
- EVIDENCE-STATUS: SPECIFIED

### REQ-REPO-011
- REQ-ID: REQ-REPO-011
- CATEGORY: repository-structure
- SOURCE: Red-on-Rust.md L39196–40762([58]); spec/01 S-22 R-REPO-02
- NORMATIVE-LEVEL: MUST
- STATEMENT: `ror-persistence` holds the WAL, snapshots, effect journal, and recovery.
- PRECONDITIONS: crate layout
- POSTCONDITIONS: —
- INVARIANTS: —
- DEPENDENCIES: REQ-PERSIST-001
- SECURITY-IMPACT: medium
- VERIFICATION-METHOD: layout review
- EVIDENCE-STATUS: SPECIFIED

### REQ-REPO-012
- REQ-ID: REQ-REPO-012
- CATEGORY: repository-structure
- SOURCE: Red-on-Rust.md L39196–40762([58]); spec/01 S-22 R-REPO-02
- NORMATIVE-LEVEL: MUST
- STATEMENT: `ror-host` holds the host execution and replay boundaries.
- PRECONDITIONS: crate layout
- POSTCONDITIONS: —
- INVARIANTS: —
- DEPENDENCIES: REQ-HOST-004
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: layout review
- EVIDENCE-STATUS: SPECIFIED

### REQ-REPO-013
- REQ-ID: REQ-REPO-013
- CATEGORY: repository-structure
- SOURCE: Red-on-Rust.md L39196–40762([58]); spec/01 S-22 R-REPO-02
- NORMATIVE-LEVEL: MUST
- STATEMENT: `ror-agent` holds planner, observation, and supervisor integration.
- PRECONDITIONS: crate layout
- POSTCONDITIONS: —
- INVARIANTS: —
- DEPENDENCIES: REQ-PLANNER-002
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: layout review
- EVIDENCE-STATUS: SPECIFIED

### REQ-REPO-014
- REQ-ID: REQ-REPO-014
- CATEGORY: repository-structure
- SOURCE: Red-on-Rust.md L39196–40762([58]); spec/01 S-22 R-REPO-02
- NORMATIVE-LEVEL: MUST
- STATEMENT: `ror-reference` is the independent executable semantic model with no production dependencies.
- PRECONDITIONS: crate layout
- POSTCONDITIONS: no production crate is a dependency
- INVARIANTS: —
- DEPENDENCIES: REQ-REF-004
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: Cargo dependency review
- EVIDENCE-STATUS: SPECIFIED

### REQ-REPO-015
- REQ-ID: REQ-REPO-015
- CATEGORY: repository-structure
- SOURCE: Red-on-Rust.md L39196–40762([58]); spec/01 S-22 R-REPO-02
- NORMATIVE-LEVEL: MUST
- STATEMENT: `ror-differential` holds the generator, runner, comparator, and shrinker.
- PRECONDITIONS: crate layout
- POSTCONDITIONS: —
- INVARIANTS: —
- DEPENDENCIES: REQ-REF-012, REQ-TEST-009
- SECURITY-IMPACT: medium
- VERIFICATION-METHOD: layout review
- EVIDENCE-STATUS: SPECIFIED

### REQ-REPO-016
- REQ-ID: REQ-REPO-016
- CATEGORY: repository-structure
- SOURCE: Red-on-Rust.md L39196–40762([58]); spec/01 S-22 R-REPO-02
- NORMATIVE-LEVEL: MUST
- STATEMENT: `ror-testkit` holds test infrastructure and controlled doubles.
- PRECONDITIONS: crate layout
- POSTCONDITIONS: —
- INVARIANTS: —
- DEPENDENCIES: REQ-REF-014, REQ-REF-015
- SECURITY-IMPACT: medium
- VERIFICATION-METHOD: layout review
- EVIDENCE-STATUS: SPECIFIED

### REQ-REPO-017
- REQ-ID: REQ-REPO-017
- CATEGORY: repository-structure
- SOURCE: Red-on-Rust.md L41223–41239([58] §39); spec/01 S-22 R-REPO-03
- NORMATIVE-LEVEL: MUST
- STATEMENT: The repository MUST make the boundaries hard to violate accidentally.
- PRECONDITIONS: any implementation activity
- POSTCONDITIONS: violations fail the build or a test, not review
- INVARIANTS: —
- DEPENDENCIES: REQ-REPO-018
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: boundary violation attempts must fail
- EVIDENCE-STATUS: SPECIFIED

### REQ-REPO-018
- REQ-ID: REQ-REPO-018
- CATEGORY: repository-structure
- SOURCE: Red-on-Rust.md L41223–41239([58] §39); spec/01 S-22 R-REPO-03
- NORMATIVE-LEVEL: MUST
- STATEMENT: Boundaries are enforced by Cargo dependencies, Rust visibility, type construction, trait boundaries, module structure, tests, mutation testing, and differential testing — rather than relying solely on developer discipline.
- PRECONDITIONS: repository structure
- POSTCONDITIONS: all eight enforcement mechanisms are in use
- INVARIANTS: —
- DEPENDENCIES: REQ-REPO-004, REQ-REPO-019
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: enforcement-mechanism review
- EVIDENCE-STATUS: SPECIFIED

### REQ-REPO-019
- REQ-ID: REQ-REPO-019
- CATEGORY: repository-structure
- SOURCE: Red-on-Rust.md L41217–41239([58] §39); spec/01 S-22 R-REPO-03
- NORMATIVE-LEVEL: MUST
- STATEMENT: The repository is successful when the architecture is visible in its structure and the boundaries are mechanically enforced.
- PRECONDITIONS: repository completion
- POSTCONDITIONS: structure and enforcement both hold
- INVARIANTS: —
- DEPENDENCIES: REQ-REPO-017, REQ-REPO-018
- SECURITY-IMPACT: medium
- VERIFICATION-METHOD: repository review
- EVIDENCE-STATUS: SPECIFIED

---

## S-23 Milestones and implementation order

### REQ-ORDER-001
- REQ-ID: REQ-ORDER-001
- CATEGORY: process
- SOURCE: Red-on-Rust.md L37800–37834([54] §3); L42108–42142([60]); spec/01 S-23 R-ORDER-01
- NORMATIVE-LEVEL: MUST
- STATEMENT: Implementation proceeds in dependency order: 01 core domain types → 02 canonical serialization → 03 compiler artifacts → 04 capability kernel → 05 budget algebra → 06 CEK evaluator → 07 lambda/call → 08 attenuation → 09 effects → 10 actors → 11 scheduler → 12 marshalling/delegation → 13 persistence → 14 crash recovery → 15 LLM boundary → 16 reference model → 17 differential harness → 18 mutation framework → 19 CI → 20 stress/security validation.
- PRECONDITIONS: implementation planning
- POSTCONDITIONS: stages are executed in this order
- INVARIANTS: — (ordered list; kept whole per rule 6)
- DEPENDENCIES: REQ-ORDER-002, REQ-ORDER-003
- SECURITY-IMPACT: medium
- VERIFICATION-METHOD: milestone review
- EVIDENCE-STATUS: SPECIFIED

### REQ-ORDER-002
- REQ-ID: REQ-ORDER-002
- CATEGORY: process
- SOURCE: Red-on-Rust.md L37800–37834([54] §3); spec/01 S-23 R-ORDER-01
- NORMATIVE-LEVEL: MUST
- STATEMENT: Every stage must have tests before the next dependent stage is considered complete.
- PRECONDITIONS: stage completion
- POSTCONDITIONS: tests exist and pass for the completed stage
- INVARIANTS: —
- DEPENDENCIES: REQ-ORDER-025
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: milestone gate review
- EVIDENCE-STATUS: SPECIFIED

### REQ-ORDER-003
- REQ-ID: REQ-ORDER-003
- CATEGORY: process
- SOURCE: Red-on-Rust.md L37800–37834([54] §3); L38921–38928([54] §30); spec/01 S-23 R-ORDER-01
- NORMATIVE-LEVEL: MUST
- STATEMENT: The reference model and differential infrastructure MUST be established as early as practical, not postponed.
- PRECONDITIONS: implementation planning
- POSTCONDITIONS: the reference and harness exist alongside production from the start
- INVARIANTS: —
- DEPENDENCIES: REQ-ORDER-022, REQ-CLAIM-021
- SECURITY-IMPACT: high (late differential testing hides accumulated divergence)
- VERIFICATION-METHOD: milestone review; first differential gate
- EVIDENCE-STATUS: SPECIFIED

### REQ-ORDER-004
- REQ-ID: REQ-ORDER-004
- CATEGORY: process
- SOURCE: Red-on-Rust.md L40763–40784([58] M0); spec/01 S-23 R-ORDER-02
- NORMATIVE-LEVEL: MUST
- STATEMENT: **M0 Workspace** acceptance: `cargo check`, `cargo test`, `cargo fmt`, `cargo clippy` pass; no semantic functionality required.
- PRECONDITIONS: workspace created
- POSTCONDITIONS: all four commands pass
- INVARIANTS: —
- DEPENDENCIES: REQ-REPO-005
- SECURITY-IMPACT: low
- VERIFICATION-METHOD: M0 gate
- EVIDENCE-STATUS: SPECIFIED

### REQ-ORDER-005
- REQ-ID: REQ-ORDER-005
- CATEGORY: process
- SOURCE: Red-on-Rust.md L40785–40803([58] M1); spec/01 S-23 R-ORDER-02
- NORMATIVE-LEVEL: MUST
- STATEMENT: **M1 Canonical serialization** acceptance: golden vectors pass; round-trips pass; malformed inputs reject; duplicate keys reject; canonical bytes are deterministic.
- PRECONDITIONS: codec implemented
- POSTCONDITIONS: all five checks pass
- INVARIANTS: —
- DEPENDENCIES: REQ-CANON-037, REQ-CANON-018, REQ-CANON-025
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: M1 gate
- EVIDENCE-STATUS: SPECIFIED

### REQ-ORDER-006
- REQ-ID: REQ-ORDER-006
- CATEGORY: process
- SOURCE: Red-on-Rust.md L40804–40824([58] M2); spec/01 S-23 R-ORDER-02
- NORMATIVE-LEVEL: MUST
- STATEMENT: **M2 Pure CEK** acceptance: differential equivalence for `Value`, `Var`, `Let`, `Seq`, `If`.
- PRECONDITIONS: pure CEK subset implemented
- POSTCONDITIONS: differential equivalence holds for the five forms
- INVARIANTS: —
- DEPENDENCIES: REQ-REF-001
- SECURITY-IMPACT: medium
- VERIFICATION-METHOD: M2 gate
- EVIDENCE-STATUS: SPECIFIED

### REQ-ORDER-007
- REQ-ID: REQ-ORDER-007
- CATEGORY: process
- SOURCE: Red-on-Rust.md L40825–40843([58] M3); spec/01 S-23 R-ORDER-02
- NORMATIVE-LEVEL: MUST
- STATEMENT: **M3 Lambda/Call** acceptance: `CEK-CALL-ARITY-PRECHECK`, `CEK-CALL-ARGS-LTR`, `CEK-CLOSURE-LEXICAL-CAPTURE`, plus deep-call stress.
- PRECONDITIONS: lambda/call implemented
- POSTCONDITIONS: all three tags satisfied and stress passes
- INVARIANTS: —
- DEPENDENCIES: REQ-CEK-013, REQ-CEK-014, REQ-CEK-016
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: M3 gate
- EVIDENCE-STATUS: SPECIFIED

### REQ-ORDER-008
- REQ-ID: REQ-ORDER-008
- CATEGORY: process
- SOURCE: Red-on-Rust.md L40844–40863([58] M4); spec/01 S-23 R-ORDER-02
- NORMATIVE-LEVEL: MUST
- STATEMENT: **M4 Capability/Attenuation** acceptance: `CAP-DERIVE-NO-AMPLIFICATION`, revocation, expiration, lexical capability binding, plus an independent reference algebra.
- PRECONDITIONS: kernel implemented
- POSTCONDITIONS: all four checks plus the reference algebra exist
- INVARIANTS: `derive(A,C) ≼ A`
- DEPENDENCIES: REQ-CAP-012, REQ-CAP-013, REQ-REF-006
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: M4 gate
- EVIDENCE-STATUS: SPECIFIED

### REQ-ORDER-009
- REQ-ID: REQ-ORDER-009
- CATEGORY: process
- SOURCE: Red-on-Rust.md L40864–40885([58] M5); spec/01 S-23 R-ORDER-02
- NORMATIVE-LEVEL: MUST
- STATEMENT: **M5 Effects** acceptance: authorization, budget gates, deadline, host policy, `EffectId`, `EffectDigest`, durable issuance, receipt validation.
- PRECONDITIONS: effect path implemented
- POSTCONDITIONS: all eight checks pass
- INVARIANTS: `HostInvoked(E) ⇒ DurableIssued(E)`
- DEPENDENCIES: REQ-EFFECT-005, REQ-DUR-002, REQ-EFFECT-027
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: M5 gate
- EVIDENCE-STATUS: SPECIFIED

### REQ-ORDER-010
- REQ-ID: REQ-ORDER-010
- CATEGORY: process
- SOURCE: Red-on-Rust.md L40886–40905([58] M6); spec/01 S-23 R-ORDER-02
- NORMATIVE-LEVEL: MUST
- STATEMENT: **M6 Actors** acceptance: FIFO scheduler, FIFO mailbox, spawn isolation, send/receive, delegation, blocked/wakeup.
- PRECONDITIONS: actors implemented
- POSTCONDITIONS: all six checks pass
- INVARIANTS: —
- DEPENDENCIES: REQ-ACTOR-010, REQ-ACTOR-030, REQ-MARSHAL-003
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: M6 gate
- EVIDENCE-STATUS: SPECIFIED

### REQ-ORDER-011
- REQ-ID: REQ-ORDER-011
- CATEGORY: process
- SOURCE: Red-on-Rust.md L40906–40925([58] M7); spec/01 S-23 R-ORDER-02
- NORMATIVE-LEVEL: MUST
- STATEMENT: **M7 Persistence** acceptance: WAL, snapshot, effect journal, checksum, sequence continuity, recovery.
- PRECONDITIONS: persistence implemented
- POSTCONDITIONS: all six checks pass
- INVARIANTS: `s_{n+1} = s_n + 1`
- DEPENDENCIES: REQ-PERSIST-004, REQ-PERSIST-021, REQ-RECOV-010
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: M7 gate
- EVIDENCE-STATUS: SPECIFIED

### REQ-ORDER-012
- REQ-ID: REQ-ORDER-012
- CATEGORY: process
- SOURCE: Red-on-Rust.md L40926–40945([58] M8); spec/01 S-23 R-ORDER-02
- NORMATIVE-LEVEL: MUST
- STATEMENT: **M8 Differential system** acceptance: generated programs, reference execution, production execution, normalized comparison, first-divergence reporting, shrinking.
- PRECONDITIONS: differential harness implemented
- POSTCONDITIONS: all six capabilities exist
- INVARIANTS: —
- DEPENDENCIES: REQ-REF-010, REQ-REF-012, REQ-TEST-009
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: M8 gate
- EVIDENCE-STATUS: SPECIFIED

### REQ-ORDER-013
- REQ-ID: REQ-ORDER-013
- CATEGORY: process
- SOURCE: Red-on-Rust.md L40946–40957([58] M9); spec/01 S-23 R-ORDER-02
- NORMATIVE-LEVEL: MUST
- STATEMENT: **M9 Mutation gate** acceptance: `MutationKillRate = 100%` for all registered non-equivalent mutants.
- PRECONDITIONS: mutation framework implemented
- POSTCONDITIONS: the kill rate is 100%
- INVARIANTS: `MutationKillRate = 100%`
- DEPENDENCIES: REQ-TEST-014
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: M9 gate
- EVIDENCE-STATUS: SPECIFIED

### REQ-ORDER-014
- REQ-ID: REQ-ORDER-014
- CATEGORY: process
- SOURCE: Red-on-Rust.md L40958–40980([58] M10); spec/01 S-23 R-ORDER-02
- NORMATIVE-LEVEL: MUST
- STATEMENT: **M10 Crash/recovery gate** acceptance: T0–T6 all produce the frozen expected classification.
- PRECONDITIONS: crash harness implemented
- POSTCONDITIONS: all seven classifications match
- INVARIANTS: —
- DEPENDENCIES: REQ-RECOV-003…REQ-RECOV-009, REQ-TEST-022
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: M10 gate
- EVIDENCE-STATUS: SPECIFIED

### REQ-ORDER-015
- REQ-ID: REQ-ORDER-015
- CATEGORY: process
- SOURCE: Red-on-Rust.md L40981–41005([58] M11); spec/01 S-23 R-ORDER-02
- NORMATIVE-LEVEL: MUST
- STATEMENT: **M11 Release candidate** acceptance: exhaustive, property, mutation, differential, crash, stress, determinism, serialization, and security suites all green.
- PRECONDITIONS: all prior milestones complete
- POSTCONDITIONS: all nine suites pass
- INVARIANTS: —
- DEPENDENCIES: REQ-TEST-028, REQ-TEST-030
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: M11 gate
- EVIDENCE-STATUS: SPECIFIED

### REQ-ORDER-016
- REQ-ID: REQ-ORDER-016
- CATEGORY: process
- SOURCE: Red-on-Rust.md L40763–41005([58] §34); L42165–42190([60]); spec/01 S-23 R-ORDER-02
- NORMATIVE-LEVEL: MUST
- STATEMENT: A milestone is complete only when its corresponding verification obligations are satisfied.
- PRECONDITIONS: milestone completion is claimed
- POSTCONDITIONS: the obligations are evidenced
- INVARIANTS: —
- DEPENDENCIES: REQ-ORDER-004…REQ-ORDER-015
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: milestone gate review
- EVIDENCE-STATUS: SPECIFIED

### REQ-ORDER-017
- REQ-ID: REQ-ORDER-017
- CATEGORY: security-invariant
- SOURCE: Red-on-Rust.md L41040–41050([58] §36); spec/01 S-23 R-ORDER-03 (partial — see req/00 §5.2)
- NORMATIVE-LEVEL: MUST
- STATEMENT: First security gate property 1: `Block ⇏ ExecutablePlan`, demonstrated before external effects are implemented. This is a repository-level architectural property, not merely a test case.
- PRECONDITIONS: before effect implementation
- POSTCONDITIONS: the property is demonstrated at repository level
- INVARIANTS: `Block ⇏ ExecutablePlan`
- DEPENDENCIES: REQ-COMPILE-001, REQ-ARCH-003
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: first security gate
- EVIDENCE-STATUS: SPECIFIED

### REQ-ORDER-018
- REQ-ID: REQ-ORDER-018
- CATEGORY: security-invariant
- SOURCE: Red-on-Rust.md L41052–41062([58] §36); spec/01 S-23 R-ORDER-03 (omitted there — see req/00 §5.2)
- NORMATIVE-LEVEL: MUST
- STATEMENT: First security gate property 2: `CapRef ⇏ AuthorityInspection`.
- PRECONDITIONS: before effect implementation
- POSTCONDITIONS: no path from a `CapRef` to authority internals
- INVARIANTS: `CapRef ⇏ AuthorityInspection`
- DEPENDENCIES: REQ-KERN-006, REQ-CALC-002, REQ-TRUST-009
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: first security gate; visibility review
- EVIDENCE-STATUS: SPECIFIED

### REQ-ORDER-019
- REQ-ID: REQ-ORDER-019
- CATEGORY: security-invariant
- SOURCE: Red-on-Rust.md L41064–41074([58] §36); spec/01 S-23 R-ORDER-03 (omitted there)
- NORMATIVE-LEVEL: MUST
- STATEMENT: First security gate property 3: `Value::Capability ⇏ OrdinaryMessageTransfer`.
- PRECONDITIONS: before effect implementation
- POSTCONDITIONS: a raw capability cannot cross an ordinary message
- INVARIANTS: `Value::Capability ⇏ OrdinaryMessageTransfer`
- DEPENDENCIES: REQ-CORE-009, REQ-MARSHAL-001
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: first security gate; `MARSHAL-NO-RAW-CAPABILITY`
- EVIDENCE-STATUS: SPECIFIED

### REQ-ORDER-020
- REQ-ID: REQ-ORDER-020
- CATEGORY: security-invariant
- SOURCE: Red-on-Rust.md L41076–41082([58] §36); spec/01 S-23 R-ORDER-03 (omitted there)
- NORMATIVE-LEVEL: MUST
- STATEMENT: First security gate property 4: `HostInvocation ⇒ DurableIssued`.
- PRECONDITIONS: before effect implementation
- POSTCONDITIONS: no host call without durable issuance
- INVARIANTS: `HostInvocation ⇒ DurableIssued`
- DEPENDENCIES: REQ-DUR-001, REQ-CORE-007
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: first security gate; `EFFECT-ISSUE-DURABLE-BEFORE-HOST`
- EVIDENCE-STATUS: SPECIFIED

### REQ-ORDER-021
- REQ-ID: REQ-ORDER-021
- CATEGORY: process
- SOURCE: Red-on-Rust.md L41084–41122([58] §37); spec/01 S-23 R-ORDER-03
- NORMATIVE-LEVEL: MUST
- STATEMENT: First differential gate: before actors or effects exist, Production CEK → normalized observation ← Reference CEK must agree for `Value`, `Var`, `Let`, `Seq`, `If`, `Lambda`, `Call`, including faults.
- PRECONDITIONS: before actor/effect implementation
- POSTCONDITIONS: agreement holds for the seven forms including fault behavior
- INVARIANTS: —
- DEPENDENCIES: REQ-REF-001, REQ-ORDER-006
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: first differential gate
- EVIDENCE-STATUS: SPECIFIED

### REQ-ORDER-022
- REQ-ID: REQ-ORDER-022
- CATEGORY: process
- SOURCE: Red-on-Rust.md L41122([58] §37); spec/01 S-23 R-ORDER-03
- NORMATIVE-LEVEL: SHOULD
- STATEMENT: The differential harness should be operational before the production CEK becomes large.
- PRECONDITIONS: CEK implementation growth
- POSTCONDITIONS: the harness is in place early
- INVARIANTS: —
- DEPENDENCIES: REQ-ORDER-003
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: milestone review
- EVIDENCE-STATUS: SPECIFIED

### REQ-ORDER-023
- REQ-ID: REQ-ORDER-023
- CATEGORY: process
- SOURCE: Red-on-Rust.md L41006–41037([58] §35); spec/01 S-23 R-ORDER-04
- NORMATIVE-LEVEL: MUST
- STATEMENT: The first implementation sprint contains exactly these tasks: ROR-001 create Cargo workspace; ROR-002 pin Rust toolchain; ROR-003 create `ror-core` domain types; ROR-004 implement canonical cursor; ROR-005 implement canonical envelope; ROR-006 implement primitive canonical types; ROR-007 implement `Value` canonical encoding; ROR-008 implement independent `Value` canonical decoding; ROR-009 add canonical golden vectors; ROR-010 add malformed-input suite; ROR-011 add duplicate-map-key regression; ROR-012 create reference-model crate; ROR-013 create differential observation API; ROR-014 implement pure reference CEK; ROR-015 implement pure production CEK; ROR-016 add first production/reference differential tests.
- PRECONDITIONS: sprint 1 planning
- POSTCONDITIONS: exactly these sixteen tasks
- INVARIANTS: — (closed task set; kept whole per rule 6)
- DEPENDENCIES: REQ-ORDER-003
- SECURITY-IMPACT: medium
- VERIFICATION-METHOD: sprint review
- EVIDENCE-STATUS: SPECIFIED

### REQ-ORDER-024
- REQ-ID: REQ-ORDER-024
- CATEGORY: process
- SOURCE: Red-on-Rust.md L41030–41037([58] §35); spec/01 S-23 R-ORDER-04
- NORMATIVE-LEVEL: MUST NOT
- STATEMENT: Sprint 1 contains no actors, external effects, persistence, or LLM integration.
- PRECONDITIONS: sprint 1 scope
- POSTCONDITIONS: none of the four areas is implemented
- INVARIANTS: —
- DEPENDENCIES: REQ-ORDER-023
- SECURITY-IMPACT: medium
- VERIFICATION-METHOD: sprint review
- EVIDENCE-STATUS: SPECIFIED

### REQ-ORDER-025
- REQ-ID: REQ-ORDER-025
- CATEGORY: process
- SOURCE: Red-on-Rust.md L41124–41160([58] §38); spec/01 S-23 R-ORDER-05
- NORMATIVE-LEVEL: MUST
- STATEMENT: A component is complete only when implementation, unit tests, reference semantics, differential tests, obligation mapping, mutation coverage, and documentation (where applicable) are all present.
- PRECONDITIONS: component completion is claimed
- POSTCONDITIONS: all seven artifacts exist
- INVARIANTS: —
- DEPENDENCIES: REQ-ORDER-002
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: definition-of-done review
- EVIDENCE-STATUS: SPECIFIED

---

## S-24 Conformance claims and prohibited shortcuts

### REQ-CLAIM-001
- REQ-ID: REQ-CLAIM-001
- CATEGORY: engineering-claims
- SOURCE: Red-on-Rust.md L38858([54] §28); L42146([60]); spec/01 S-24 R-CLAIM-02
- NORMATIVE-LEVEL: MUST NOT
- STATEMENT: Never use recursive evaluation.
- PRECONDITIONS: evaluator implementation
- POSTCONDITIONS: recursion is not used for control flow
- INVARIANTS: —
- DEPENDENCIES: REQ-CEK-002
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: code review; deep-call stress
- EVIDENCE-STATUS: SPECIFIED

### REQ-CLAIM-002
- REQ-ID: REQ-CLAIM-002
- CATEGORY: engineering-claims
- SOURCE: Red-on-Rust.md L38859([54] §28); spec/01 S-24 R-CLAIM-02
- NORMATIVE-LEVEL: MUST NOT
- STATEMENT: Never trust AST shape as a security boundary.
- PRECONDITIONS: any security decision
- POSTCONDITIONS: decisions rest on validated plans and kernel authority
- INVARIANTS: —
- DEPENDENCIES: REQ-TRUST-002, REQ-CALC-004
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: review; malformed-`Block` rejection
- EVIDENCE-STATUS: SPECIFIED

### REQ-CLAIM-003
- REQ-ID: REQ-CLAIM-003
- CATEGORY: engineering-claims
- SOURCE: Red-on-Rust.md L38860([54] §28); spec/01 S-24 R-CLAIM-02
- NORMATIVE-LEVEL: MUST NOT
- STATEMENT: Never expose authority internals.
- PRECONDITIONS: any API surface
- POSTCONDITIONS: authority state is inaccessible outside the kernel
- INVARIANTS: `CapRef ⇏ AuthorityInspection`
- DEPENDENCIES: REQ-KERN-006
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: visibility review
- EVIDENCE-STATUS: SPECIFIED

### REQ-CLAIM-004
- REQ-ID: REQ-CLAIM-004
- CATEGORY: engineering-claims
- SOURCE: Red-on-Rust.md L38861([54] §28); spec/01 S-24 R-CLAIM-02
- NORMATIVE-LEVEL: MUST NOT
- STATEMENT: Never clone capabilities wholesale during spawn.
- PRECONDITIONS: spawn implementation
- POSTCONDITIONS: only explicit derivation occurs
- INVARIANTS: `Authority_child ≼ Authority_parent`
- DEPENDENCIES: REQ-ACTOR-020
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: amplification test
- EVIDENCE-STATUS: SPECIFIED

### REQ-CLAIM-005
- REQ-ID: REQ-CLAIM-005
- CATEGORY: engineering-claims
- SOURCE: Red-on-Rust.md L38862([54] §28); spec/01 S-24 R-CLAIM-02
- NORMATIVE-LEVEL: MUST NOT
- STATEMENT: Never transfer raw capability references through ordinary messages.
- PRECONDITIONS: any message send
- POSTCONDITIONS: raw `CapRef` never crosses
- INVARIANTS: `CapRef ∉ marshal(v)`
- DEPENDENCIES: REQ-CORE-009, REQ-MARSHAL-001
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: `MARSHAL-NO-RAW-CAPABILITY`
- EVIDENCE-STATUS: SPECIFIED

### REQ-CLAIM-006
- REQ-ID: REQ-CLAIM-006
- CATEGORY: engineering-claims
- SOURCE: Red-on-Rust.md L38863([54] §28); L42154([60]); spec/01 S-24 R-CLAIM-02
- NORMATIVE-LEVEL: MUST NOT
- STATEMENT: Never use wall-clock time for deterministic semantics.
- PRECONDITIONS: any semantic decision
- POSTCONDITIONS: only logical time is used
- INVARIANTS: —
- DEPENDENCIES: REQ-CAP-021
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: code review; determinism differential
- EVIDENCE-STATUS: SPECIFIED

### REQ-CLAIM-007
- REQ-ID: REQ-CLAIM-007
- CATEGORY: engineering-claims
- SOURCE: Red-on-Rust.md L38864([54] §28); L40523([58]); spec/01 S-24 R-CLAIM-02
- NORMATIVE-LEVEL: MUST NOT
- STATEMENT: Never use saturating budget arithmetic.
- PRECONDITIONS: budget arithmetic
- POSTCONDITIONS: checked arithmetic only
- INVARIANTS: —
- DEPENDENCIES: REQ-BUDGET-013
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: code review; mutation M009
- EVIDENCE-STATUS: SPECIFIED

### REQ-CLAIM-008
- REQ-ID: REQ-CLAIM-008
- CATEGORY: engineering-claims
- SOURCE: Red-on-Rust.md L38865([54] §28); L42155([60]); spec/01 S-24 R-CLAIM-02
- NORMATIVE-LEVEL: MUST NOT
- STATEMENT: Never invoke the host before durable issuance.
- PRECONDITIONS: any host call
- POSTCONDITIONS: durable `Issued` exists first
- INVARIANTS: `HostInvoked(E) ⇒ DurableIssued(E)`
- DEPENDENCIES: REQ-DUR-001
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: `EFFECT-ISSUE-DURABLE-BEFORE-HOST`
- EVIDENCE-STATUS: SPECIFIED

### REQ-CLAIM-009
- REQ-ID: REQ-CLAIM-009
- CATEGORY: engineering-claims
- SOURCE: Red-on-Rust.md L38866([54] §28); L38241–38248([54] §12); spec/01 S-24 R-CLAIM-02
- NORMATIVE-LEVEL: MUST NOT
- STATEMENT: Never infer external-effect nonexecution from a missing completion.
- PRECONDITIONS: recovery or reconciliation
- POSTCONDITIONS: the effect stays `Indeterminate`
- INVARIANTS: —
- DEPENDENCIES: REQ-DUR-012, REQ-CORE-014
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: `RECOVERY-ISSUED-INDETERMINATE`
- EVIDENCE-STATUS: SPECIFIED

### REQ-CLAIM-010
- REQ-ID: REQ-CLAIM-010
- CATEGORY: engineering-claims
- SOURCE: Red-on-Rust.md L38867([54] §28); L38254–38272([54] §13); spec/01 S-24 R-CLAIM-02
- NORMATIVE-LEVEL: MUST NOT
- STATEMENT: Never silently repair persistence corruption.
- PRECONDITIONS: corruption detected
- POSTCONDITIONS: an explicit fault is raised
- INVARIANTS: `Invalid(D) ⇒ RecoveryFault`
- DEPENDENCIES: REQ-RECOV-012
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: negative recovery tests
- EVIDENCE-STATUS: SPECIFIED

### REQ-CLAIM-011
- REQ-ID: REQ-CLAIM-011
- CATEGORY: engineering-claims
- SOURCE: Red-on-Rust.md L38868([54] §28, "use production recovery as the reference recovery oracle"); spec/01 S-24 R-CLAIM-02
- NORMATIVE-LEVEL: MUST NOT
- STATEMENT: Never use production recovery as the reference recovery oracle.
- PRECONDITIONS: recovery verification
- POSTCONDITIONS: the oracle is independent
- INVARIANTS: —
- DEPENDENCIES: REQ-RECOV-015
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: dependency review
- EVIDENCE-STATUS: SPECIFIED

### REQ-CLAIM-012
- REQ-ID: REQ-CLAIM-012
- CATEGORY: engineering-claims
- SOURCE: Red-on-Rust.md L38869([54] §28, "use production serialization as the reference serialization oracle"); spec/01 S-24 R-CLAIM-02
- NORMATIVE-LEVEL: MUST NOT
- STATEMENT: Never use production serialization as the reference serialization oracle.
- PRECONDITIONS: serialization verification
- POSTCONDITIONS: the oracle is independent
- INVARIANTS: —
- DEPENDENCIES: REQ-SCOPE-011, REQ-CANON-037
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: dependency review; independent decoding path (ROR-008)
- EVIDENCE-STATUS: SPECIFIED

### REQ-CLAIM-013
- REQ-ID: REQ-CLAIM-013
- CATEGORY: engineering-claims
- SOURCE: Red-on-Rust.md L38870([54] §28); spec/01 S-24 R-CLAIM-02
- NORMATIVE-LEVEL: MUST NOT
- STATEMENT: Never compare only final return values.
- PRECONDITIONS: differential comparison
- POSTCONDITIONS: the full normalized observation set is compared
- INVARIANTS: —
- DEPENDENCIES: REQ-REF-013
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: comparator review
- EVIDENCE-STATUS: SPECIFIED

### REQ-CLAIM-014
- REQ-ID: REQ-CLAIM-014
- CATEGORY: engineering-claims
- SOURCE: Red-on-Rust.md L38871([54] §28); spec/01 S-24 R-CLAIM-02
- NORMATIVE-LEVEL: MUST NOT
- STATEMENT: Never reduce semantic coverage to satisfy CI timing.
- PRECONDITIONS: CI timing pressure
- POSTCONDITIONS: coverage is unchanged
- INVARIANTS: —
- DEPENDENCIES: REQ-TEST-005
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: coverage report comparison
- EVIDENCE-STATUS: SPECIFIED

### REQ-CLAIM-015
- REQ-ID: REQ-CLAIM-015
- CATEGORY: engineering-claims
- SOURCE: Red-on-Rust.md L38872([54] §28); spec/01 S-24 R-CLAIM-02
- NORMATIVE-LEVEL: MUST NOT
- STATEMENT: Never accept surviving mutations without adjudication.
- PRECONDITIONS: a mutant survives
- POSTCONDITIONS: an adjudication is recorded
- INVARIANTS: —
- DEPENDENCIES: REQ-TEST-016
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: adjudication review
- EVIDENCE-STATUS: SPECIFIED

### REQ-CLAIM-016
- REQ-ID: REQ-CLAIM-016
- CATEGORY: engineering-claims
- SOURCE: Red-on-Rust.md L38873([54] §28); spec/01 S-24 R-CLAIM-02
- NORMATIVE-LEVEL: MUST NOT
- STATEMENT: Never weaken tests because implementation is inconvenient.
- PRECONDITIONS: a test obstructs implementation
- POSTCONDITIONS: the test is unchanged; the conflict is reported
- INVARIANTS: —
- DEPENDENCIES: REQ-TEST-024, REQ-CLAIM-020
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: test-diff review; conflict reports
- EVIDENCE-STATUS: SPECIFIED

### REQ-CLAIM-017
- REQ-ID: REQ-CLAIM-017
- CATEGORY: engineering-claims
- SOURCE: Red-on-Rust.md L38913–38917([54] §29); L42191–42265([60]); L28247–28268([35]); spec/01 S-24 R-CLAIM-01
- NORMATIVE-LEVEL: MUST
- STATEMENT: The appropriate engineering claim is: "The independent reference model, exhaustive/property-based tests, mutation testing, and crash-injection suite provide machine-checked evidence that the implementation conforms to the frozen calculus over the tested state space." Do not claim more than the evidence establishes.
- PRECONDITIONS: any conformance claim
- POSTCONDITIONS: the claim uses this scope and wording
- INVARIANTS: —
- DEPENDENCIES: REQ-TEST-031, REQ-CANON-036, REQ-REF-003
- SECURITY-IMPACT: high (claim discipline)
- VERIFICATION-METHOD: report review
- EVIDENCE-STATUS: SPECIFIED

### REQ-CLAIM-018
- REQ-ID: REQ-CLAIM-018
- CATEGORY: engineering-claims
- SOURCE: Red-on-Rust.md L38917–38919([54] §29); L37444–37452([50]); spec/01 S-24 R-CLAIM-01
- NORMATIVE-LEVEL: MUST NOT
- STATEMENT: The project MUST NOT claim that test execution constitutes a mathematical proof of the entire calculus.
- PRECONDITIONS: any claim about guarantees
- POSTCONDITIONS: the claim stays at machine-checked-evidence level
- INVARIANTS: —
- DEPENDENCIES: REQ-CLAIM-017; C-34, C-43
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: report review
- EVIDENCE-STATUS: SPECIFIED

### REQ-CLAIM-019
- REQ-ID: REQ-CLAIM-019
- CATEGORY: engineering-claims
- SOURCE: Red-on-Rust.md L38919([54] §29); L42191–42265([60]); spec/01 S-24 R-CLAIM-01
- NORMATIVE-LEVEL: MAY
- STATEMENT: Formal mechanization may provide stronger guarantees later but is not required to begin implementation.
- PRECONDITIONS: implementation start
- POSTCONDITIONS: no proof obligation blocks the start
- INVARIANTS: —
- DEPENDENCIES: REQ-CLAIM-018
- SECURITY-IMPACT: low
- VERIFICATION-METHOD: not applicable (permission)
- EVIDENCE-STATUS: SPECIFIED

### REQ-CLAIM-020
- REQ-ID: REQ-CLAIM-020
- CATEGORY: engineering-claims
- SOURCE: Red-on-Rust.md L38808–38846([54] §27); spec/01 S-24 R-CLAIM-03
- NORMATIVE-LEVEL: MUST
- STATEMENT: Implementation reports MUST include: component implemented; frozen invariants exercised; production/reference boundary; tests added; differential tests added; mutation tests affected; coverage obligations satisfied; known limitations; remaining work.
- PRECONDITIONS: an implementation report is produced
- POSTCONDITIONS: all nine components are present
- INVARIANTS: —
- DEPENDENCIES: REQ-ORDER-025
- SECURITY-IMPACT: medium
- VERIFICATION-METHOD: report review
- EVIDENCE-STATUS: SPECIFIED

### REQ-CLAIM-021
- REQ-ID: REQ-CLAIM-021
- CATEGORY: engineering-claims
- SOURCE: Red-on-Rust.md L38828–38846([54] §27); spec/01 S-24 R-CLAIM-03
- NORMATIVE-LEVEL: MUST
- STATEMENT: Conflicts MUST be reported in the `CONFLICT / FROZEN REQUIREMENT / AFFECTED COMPONENT / RECOMMENDED ACTION` format, never silently resolved.
- PRECONDITIONS: a requirement conflicts with existing code
- POSTCONDITIONS: the four-part report is issued
- INVARIANTS: —
- DEPENDENCIES: REQ-SCOPE-009, REQ-TEST-024
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: conflict-report review
- EVIDENCE-STATUS: SPECIFIED

### REQ-CLAIM-022
- REQ-ID: REQ-CLAIM-022
- CATEGORY: engineering-claims
- SOURCE: Red-on-Rust.md L38921–38928([54] §30); spec/01 S-24 R-CLAIM-04
- NORMATIVE-LEVEL: MUST
- STATEMENT: Do not propose another semantic phase; begin implementation from the lowest dependency layer, with the independent reference model alongside production, keeping the differential harness operational as early as possible.
- PRECONDITIONS: project start
- POSTCONDITIONS: implementation begins at the lowest layer with the reference alongside
- INVARIANTS: —
- DEPENDENCIES: REQ-SCOPE-006, REQ-ORDER-001, REQ-ORDER-003
- SECURITY-IMPACT: medium
- VERIFICATION-METHOD: process review
- EVIDENCE-STATUS: SPECIFIED
