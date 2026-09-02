# Atomic Requirement Registry — Part 6: Reference Model and Test Infrastructure (S-20, S-21)

Areas: `REF` (17), `TEST` (32) — 49 atomic units.

---

## S-20 Independent reference model and differential verification

### REQ-REF-001
- REQ-ID: REQ-REF-001
- CATEGORY: verification
- SOURCE: Red-on-Rust.md L35281–35310([48]); L38877–38895([54] §29); spec/01 S-20 R-REF-01
- NORMATIVE-LEVEL: MUST
- STATEMENT: `Observe(Production(X)) = Observe(Reference(X))` for every generated input `X` in the comparison domain.
- PRECONDITIONS: a generated input in the comparison domain
- POSTCONDITIONS: the normalized observations are equal
- INVARIANTS: `Observe_P(X) = Observe_R(X)`
- DEPENDENCIES: REQ-REF-010, REQ-REF-012
- SECURITY-IMPACT: critical (this is the primary conformance oracle)
- VERIFICATION-METHOD: 15C differential suite
- EVIDENCE-STATUS: SPECIFIED

### REQ-REF-002
- REQ-ID: REQ-REF-002
- CATEGORY: verification
- SOURCE: Red-on-Rust.md L35281–35310([48]); L38901–38907([54] §29); spec/01 S-20 R-REF-01
- NORMATIVE-LEVEL: MUST
- STATEMENT: For persistence, `Canonical(Recover_P(D)) = Canonical(Recover_R(D))`, subject to the frozen reconciliation rules.
- PRECONDITIONS: durable state `D` in the tested persistence state space
- POSTCONDITIONS: production and reference recovery produce identical canonical bytes
- INVARIANTS: `Canonical(Recover_P(D)) = Canonical(Recover_R(D))`
- DEPENDENCIES: REQ-RECOV-002, REQ-RECOV-014
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: recovery differential
- EVIDENCE-STATUS: SPECIFIED

### REQ-REF-003
- REQ-ID: REQ-REF-003
- CATEGORY: verification
- SOURCE: Red-on-Rust.md L38935–38953([54] §30 region); L28247–28268([35]); spec/01 S-20 R-REF-01
- NORMATIVE-LEVEL: MUST
- STATEMENT: Differential agreement is machine-checked **evidence**, not a formal proof.
- PRECONDITIONS: any conformance claim based on differential testing
- POSTCONDITIONS: the claim is scoped to the tested state space
- INVARIANTS: —
- DEPENDENCIES: REQ-CLAIM-017
- SECURITY-IMPACT: medium (claim discipline)
- VERIFICATION-METHOD: report review
- EVIDENCE-STATUS: SPECIFIED

### REQ-REF-004
- REQ-ID: REQ-REF-004
- CATEGORY: verification
- SOURCE: Red-on-Rust.md L35330–35375([48]); L37696–37720([54] §1.2); spec/01 S-20 R-REF-02
- NORMATIVE-LEVEL: MUST NOT
- STATEMENT: The reference model MUST NOT call `ProductionEvaluator`, `ProductionContinuation`, `ProductionCapabilityKernel`, `ProductionBudget`, `ProductionScheduler`, `ProductionSerializer`, `ProductionRecovery`, `ProductionPersistence`, `ProductionReplayHost`, or `ProductionTransition`.
- PRECONDITIONS: reference implementation
- POSTCONDITIONS: none of the ten production entry points is reachable
- INVARIANTS: — (closed prohibition list; kept whole per rule 6)
- DEPENDENCIES: REQ-SCOPE-011
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: dependency-graph review; ROR-012 crate review
- EVIDENCE-STATUS: SPECIFIED

### REQ-REF-005
- REQ-ID: REQ-REF-005
- CATEGORY: verification
- SOURCE: Red-on-Rust.md L35330–35375([48]); L37696–37720([54] §1.2); spec/01 S-20 R-REF-02
- NORMATIVE-LEVEL: MAY
- STATEMENT: The reference model may consume test inputs/fixtures and emit reference observations/traces.
- PRECONDITIONS: differential harness operation
- POSTCONDITIONS: only fixture inputs and observation outputs cross the boundary
- INVARIANTS: —
- DEPENDENCIES: REQ-SCOPE-012
- SECURITY-IMPACT: low
- VERIFICATION-METHOD: dependency review
- EVIDENCE-STATUS: SPECIFIED

### REQ-REF-006
- REQ-ID: REQ-REF-006
- CATEGORY: verification
- SOURCE: Red-on-Rust.md L35281–35322([48]); L41848–41866([60]); spec/01 S-20 R-REF-03
- NORMATIVE-LEVEL: MUST
- STATEMENT: The reference implementation independently models: CEK evaluation, lexical environments, closures, calls, capability derivation, revocation, budgets, actors, scheduling, effects, persistence, and recovery.
- PRECONDITIONS: reference model scope
- POSTCONDITIONS: all twelve areas are modelled
- INVARIANTS: — (closed area list; kept whole per rule 6)
- DEPENDENCIES: REQ-REF-004
- SECURITY-IMPACT: critical (an unmodelled area is an unverified area)
- VERIFICATION-METHOD: reference-model scope review
- EVIDENCE-STATUS: SPECIFIED

### REQ-REF-007
- REQ-ID: REQ-REF-007
- CATEGORY: verification
- SOURCE: Red-on-Rust.md L35313–35322([48]); L35341([48]); spec/01 S-20 R-REF-03
- NORMATIVE-LEVEL: SHOULD
- STATEMENT: The reference model is intentionally small, direct, explicit, deterministic, independently structured, and slow where clarity demands.
- PRECONDITIONS: reference implementation style
- POSTCONDITIONS: clarity is preferred over cleverness
- INVARIANTS: —
- DEPENDENCIES: REQ-REF-008
- SECURITY-IMPACT: medium
- VERIFICATION-METHOD: independent authoring and review (anti-oracle-collapse)
- EVIDENCE-STATUS: SPECIFIED

### REQ-REF-008
- REQ-ID: REQ-REF-008
- CATEGORY: verification
- SOURCE: Red-on-Rust.md L35341([48]); spec/01 S-20 R-REF-03
- NORMATIVE-LEVEL: MUST
- STATEMENT: Performance is explicitly secondary to transparency in the reference model.
- PRECONDITIONS: reference implementation decisions
- POSTCONDITIONS: no optimization that obscures semantics
- INVARIANTS: —
- DEPENDENCIES: REQ-REF-007
- SECURITY-IMPACT: low
- VERIFICATION-METHOD: review
- EVIDENCE-STATUS: SPECIFIED

### REQ-REF-009
- REQ-ID: REQ-REF-009
- CATEGORY: verification
- SOURCE: Red-on-Rust.md L35326–35339([48]); spec/01 S-20 R-REF-04
- NORMATIVE-LEVEL: MUST NOT
- STATEMENT: The reference model does not redefine semantics, introduce a second serialization format, reproduce host implementation details, prove correctness mathematically, share production transition code, or optimize.
- PRECONDITIONS: reference implementation
- POSTCONDITIONS: none of the six occurs
- INVARIANTS: — (closed scope-exclusion list; kept whole — see req/02 CN-14)
- DEPENDENCIES: REQ-REF-004, REQ-PERSIST-002
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: reference-model review; dependency review
- EVIDENCE-STATUS: SPECIFIED

### REQ-REF-010
- REQ-ID: REQ-REF-010
- CATEGORY: verification
- SOURCE: Red-on-Rust.md L38350–38364([54] §16); L41869–41906([60]); spec/01 S-20 R-REF-05
- NORMATIVE-LEVEL: MUST
- STATEMENT: Differential comparison uses normalized observations, not internal structure: terminal states, event trace, effect trace, resource partitions, authority outcomes, scheduler trace, faults, recovered state.
- PRECONDITIONS: any differential comparison
- POSTCONDITIONS: all eight observation channels are compared
- INVARIANTS: — (closed observation list; kept whole per rule 6)
- DEPENDENCIES: REQ-REF-012
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: comparator review
- EVIDENCE-STATUS: SPECIFIED

### REQ-REF-011
- REQ-ID: REQ-REF-011
- CATEGORY: verification
- SOURCE: Red-on-Rust.md L38366–38380([54] §16); spec/01 S-20 R-REF-05
- NORMATIVE-LEVEL: MUST
- STATEMENT: Internal details are excluded from comparison unless explicitly semantic: addresses, pointers, allocator behavior, Rust enum layout, OS handles, host object identity.
- PRECONDITIONS: any differential comparison
- POSTCONDITIONS: none of these is compared
- INVARIANTS: —
- DEPENDENCIES: REQ-REF-010, REQ-CANON-003
- SECURITY-IMPACT: high (comparing layout would produce false divergences and mask real ones)
- VERIFICATION-METHOD: comparator review
- EVIDENCE-STATUS: SPECIFIED

### REQ-REF-012
- REQ-ID: REQ-REF-012
- CATEGORY: verification
- SOURCE: Red-on-Rust.md L38384([54] §16); L41869–41906([60]); spec/01 S-20 R-REF-05
- NORMATIVE-LEVEL: MUST
- STATEMENT: The comparator MUST report the FIRST divergence.
- PRECONDITIONS: a divergence exists
- POSTCONDITIONS: the earliest divergent step is reported, not an aggregate
- INVARIANTS: —
- DEPENDENCIES: REQ-TEST-007
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: first-divergence reporting (M8 gate)
- EVIDENCE-STATUS: SPECIFIED

### REQ-REF-013
- REQ-ID: REQ-REF-013
- CATEGORY: verification
- SOURCE: Red-on-Rust.md L38346–38350([54] §16); L38868([54] §28); spec/01 S-20 R-REF-05
- NORMATIVE-LEVEL: MUST NOT
- STATEMENT: Comparing only final return values is forbidden.
- PRECONDITIONS: any differential comparison
- POSTCONDITIONS: the full observation set is compared
- INVARIANTS: —
- DEPENDENCIES: REQ-CLAIM-013, REQ-HOST-014
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: comparator review
- EVIDENCE-STATUS: SPECIFIED

### REQ-REF-014
- REQ-ID: REQ-REF-014
- CATEGORY: verification
- SOURCE: Red-on-Rust.md L27901([34]); spec/01 S-20 R-REF-06
- NORMATIVE-LEVEL: MUST
- STATEMENT: The harness MUST include a `PanicHost` that panics if `execute()` is called before all gates pass.
- PRECONDITIONS: a test run using the harness
- POSTCONDITIONS: a premature host call aborts the test
- INVARIANTS: —
- DEPENDENCIES: REQ-EFFECT-023, REQ-DUR-001
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: harness self-test
- EVIDENCE-STATUS: SPECIFIED

### REQ-REF-015
- REQ-ID: REQ-REF-015
- CATEGORY: verification
- SOURCE: Red-on-Rust.md L27891–27902([34]); spec/01 S-20 R-REF-06
- NORMATIVE-LEVEL: MUST
- STATEMENT: The harness MUST include a `MockKernel` asserting exactly one `authorize`/`derive` call with the exact expected parameters.
- PRECONDITIONS: a test run using the harness
- POSTCONDITIONS: extra, missing, or differently-parameterized kernel calls fail the test
- INVARIANTS: —
- DEPENDENCIES: REQ-KERN-004, REQ-KERN-005
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: harness self-test; Track B
- EVIDENCE-STATUS: SPECIFIED

### REQ-REF-016
- REQ-ID: REQ-REF-016
- CATEGORY: verification
- SOURCE: Red-on-Rust.md L27891–27902([34]); spec/01 S-20 R-REF-06
- NORMATIVE-LEVEL: MUST
- STATEMENT: The production/reference boundary is a first-class test subject.
- PRECONDITIONS: test planning
- POSTCONDITIONS: boundary enforcement has its own tests
- INVARIANTS: —
- DEPENDENCIES: REQ-REF-014, REQ-REF-015, REQ-ARCH-002
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: boundary tests
- EVIDENCE-STATUS: SPECIFIED

---

## S-21 Test infrastructure, mutation, and CI

### REQ-REF-017
- REQ-ID: REQ-REF-017
- CATEGORY: verification
- SOURCE: Red-on-Rust.md L12363–12367([21] §13); spec/01 S-20 R-REF-03
- NORMATIVE-LEVEL: MAY
- STATEMENT: The reference interpreter may copy an immutable environment snapshot; the optimized runtime may later replace this with heap references.
- PRECONDITIONS: reference-model implementation
- POSTCONDITIONS: environment copying is permitted and does not affect observable semantics
- INVARIANTS: —
- DEPENDENCIES: REQ-REF-006, REQ-CALC-014
- SECURITY-IMPACT: low
- VERIFICATION-METHOD: not applicable (permission, not obligation)
- EVIDENCE-STATUS: SPECIFIED
### REQ-TEST-001
- REQ-ID: REQ-TEST-001
- CATEGORY: test-infrastructure
- SOURCE: Red-on-Rust.md L38587–38624([54] §22 Exhaustive); L37253([49] "all valid/invalid programs up to depth 4"); spec/01 S-21 R-TEST-01; spec/06 C-31
- NORMATIVE-LEVEL: MUST
- STATEMENT: The exhaustive (small-state) mode enumerates bounded state with baseline `expression depth ≤ 4, actors ≤ 2, capabilities ≤ 2`, and runs on every commit.
- PRECONDITIONS: CI on commit
- POSTCONDITIONS: the enumeration completes over the baseline
- INVARIANTS: —
- DEPENDENCIES: REQ-TEST-004
- SECURITY-IMPACT: medium
- VERIFICATION-METHOD: CI gate (pull request)
- EVIDENCE-STATUS: SPECIFIED

### REQ-TEST-002
- REQ-ID: REQ-TEST-002
- CATEGORY: test-infrastructure
- SOURCE: Red-on-Rust.md L38625–38630([54] §22 Property-generated); L38390–38437([54] §17); spec/01 S-21 R-TEST-01
- NORMATIVE-LEVEL: MUST
- STATEMENT: The property-generated mode performs randomized layered generation (structure → type validity → capabilities → budgets → actor topology → effects → persistence corruption) with aggressive shrinking, and runs nightly.
- PRECONDITIONS: nightly CI
- POSTCONDITIONS: generation covers the layer order stated
- INVARIANTS: —
- DEPENDENCIES: REQ-TEST-009
- SECURITY-IMPACT: medium
- VERIFICATION-METHOD: CI gate (nightly)
- EVIDENCE-STATUS: SPECIFIED

### REQ-TEST-003
- REQ-ID: REQ-TEST-003
- CATEGORY: test-infrastructure
- SOURCE: Red-on-Rust.md L38631–38651([54] §22 Stress); spec/01 S-21 R-TEST-01; spec/06 C-29
- NORMATIVE-LEVEL: MUST
- STATEMENT: The stress mode exercises `50k–100k` call depth, `100+` actors, long mailboxes, large WAL traces, repeated crash/recovery, and large continuation states; it runs weekly and on release candidates.
- PRECONDITIONS: weekly / release-candidate CI
- POSTCONDITIONS: all six stress dimensions are exercised
- INVARIANTS: —
- DEPENDENCIES: REQ-CEK-002
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: CI gate (release candidate)
- EVIDENCE-STATUS: SPECIFIED

### REQ-TEST-004
- REQ-ID: REQ-TEST-004
- CATEGORY: test-infrastructure
- SOURCE: Red-on-Rust.md L38633([54] §22); L37381–37386([50]); spec/01 S-21 R-TEST-01; spec/06 C-11
- NORMATIVE-LEVEL: MUST
- STATEMENT: The CI time target is a performance budget, **not** a semantic constraint; if the state space grows, the suite is partitioned, sharded, or cached.
- PRECONDITIONS: the suite exceeds its time budget
- POSTCONDITIONS: the response is engineering, not reduced coverage
- INVARIANTS: —
- DEPENDENCIES: REQ-TEST-005
- SECURITY-IMPACT: medium
- VERIFICATION-METHOD: CI configuration review
- EVIDENCE-STATUS: SPECIFIED

### REQ-TEST-005
- REQ-ID: REQ-TEST-005
- CATEGORY: test-infrastructure
- SOURCE: Red-on-Rust.md L38633([54] §22); L38870([54] §28); spec/01 S-21 R-TEST-01
- NORMATIVE-LEVEL: MUST NOT
- STATEMENT: Semantic coverage MUST NOT be reduced to preserve a time target.
- PRECONDITIONS: CI timing pressure
- POSTCONDITIONS: coverage is unchanged
- INVARIANTS: —
- DEPENDENCIES: REQ-CLAIM-014
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: semantic coverage report comparison
- EVIDENCE-STATUS: SPECIFIED

### REQ-TEST-006
- REQ-ID: REQ-TEST-006
- CATEGORY: test-infrastructure
- SOURCE: Red-on-Rust.md L38392([54] §17); L38716([54] §25); spec/01 S-21 R-TEST-02
- NORMATIVE-LEVEL: MUST
- STATEMENT: Every generated test case MUST be reproducible.
- PRECONDITIONS: any generated case
- POSTCONDITIONS: the same seed and versions reproduce it
- INVARIANTS: —
- DEPENDENCIES: REQ-TEST-007
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: reproducibility check on failure artifacts
- EVIDENCE-STATUS: SPECIFIED

### REQ-TEST-007
- REQ-ID: REQ-TEST-007
- CATEGORY: test-infrastructure
- SOURCE: Red-on-Rust.md L38716–38741([54] §25); L38401([54] §17); spec/01 S-21 R-TEST-02
- NORMATIVE-LEVEL: MUST
- STATEMENT: Every failure MUST save the structured artifact containing: seed; generator version; semantic version; test-case version; program; initial state; capabilities; budgets; actor topology; scheduler trace; host trace; persistence image; crash trace; production observation; reference observation; first divergence; minimized case.
- PRECONDITIONS: a test fails
- POSTCONDITIONS: the artifact with all fields is written
- INVARIANTS: — (closed field list; kept whole per rule 6)
- DEPENDENCIES: REQ-REF-012, REQ-TEST-011
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: artifact schema check
- EVIDENCE-STATUS: SPECIFIED

### REQ-TEST-008
- REQ-ID: REQ-TEST-008
- CATEGORY: test-infrastructure
- SOURCE: Red-on-Rust.md L38745([54] §25); spec/01 S-21 R-TEST-02
- NORMATIVE-LEVEL: MUST
- STATEMENT: The counterexample artifact MUST be runnable locally.
- PRECONDITIONS: an artifact exists
- POSTCONDITIONS: it can be replayed outside CI
- INVARIANTS: —
- DEPENDENCIES: REQ-TEST-007
- SECURITY-IMPACT: medium
- VERIFICATION-METHOD: local replay of a saved artifact
- EVIDENCE-STATUS: SPECIFIED

### REQ-TEST-009
- REQ-ID: REQ-TEST-009
- CATEGORY: test-infrastructure
- SOURCE: Red-on-Rust.md L38447–38463([54] §18); spec/01 S-21 R-TEST-03
- NORMATIVE-LEVEL: MUST
- STATEMENT: Shrinking follows the ordered priorities: (1) actor count, (2) expression depth, (3) call arity, (4) bindings, (5) mailbox messages, (6) capability scope, (7) budget dimensions, (8) WAL records, (9) effect count, (10) crash position.
- PRECONDITIONS: a failing case is shrunk
- POSTCONDITIONS: the priorities are applied in this order
- INVARIANTS: — (ordered list; kept whole per rule 6)
- DEPENDENCIES: REQ-TEST-010
- SECURITY-IMPACT: medium
- VERIFICATION-METHOD: shrinking tests
- EVIDENCE-STATUS: SPECIFIED

### REQ-TEST-010
- REQ-ID: REQ-TEST-010
- CATEGORY: test-infrastructure
- SOURCE: Red-on-Rust.md L38439–38465([54] §18); spec/01 S-21 R-TEST-03
- NORMATIVE-LEVEL: MUST
- STATEMENT: The shrinker MUST preserve the failure predicate.
- PRECONDITIONS: any shrink step
- POSTCONDITIONS: the shrunk case still fails
- INVARIANTS: —
- DEPENDENCIES: REQ-TEST-009
- SECURITY-IMPACT: high (shrinking away the bug destroys the evidence)
- VERIFICATION-METHOD: shrinking tests
- EVIDENCE-STATUS: SPECIFIED

### REQ-TEST-011
- REQ-ID: REQ-TEST-011
- CATEGORY: test-infrastructure
- SOURCE: Red-on-Rust.md L38439–38465([54] §18); spec/01 S-21 R-TEST-03
- NORMATIVE-LEVEL: MUST
- STATEMENT: Every failure yields a minimal reproducible artifact.
- PRECONDITIONS: a failure occurs
- POSTCONDITIONS: the minimized case is included in the artifact
- INVARIANTS: —
- DEPENDENCIES: REQ-TEST-007
- SECURITY-IMPACT: medium
- VERIFICATION-METHOD: artifact schema check
- EVIDENCE-STATUS: SPECIFIED

### REQ-TEST-012
- REQ-ID: REQ-TEST-012
- CATEGORY: test-infrastructure
- SOURCE: Red-on-Rust.md L40657–40719([58] §32); L38467–38513([54] §19); spec/01 S-21 R-TEST-04; spec/06 C-10
- NORMATIVE-LEVEL: MUST
- STATEMENT: The versioned baseline mutation registry MUST include `M001` reverse argument evaluation; `M002` skip arity precheck; `M003` allow non-function application; `M004` accept revoked capability; `M005` omit capability ceiling; `M006` permit capability amplification; `M007` omit budget gate; `M008` release indeterminate escrow; `M009` permit negative resources; `M010` allocate `EffectId` before authorization; `M011` schedule blocked actor; `M012` duplicate runnable queue entry; `M013` break mailbox FIFO; `M014` accept duplicate canonical map key; `M015` ignore WAL sequence gap; `M016` ignore checksum mismatch; `M017` accept mismatched `EffectDigest`; `M018` resume after corrupted receipt.
- PRECONDITIONS: mutation framework in place
- POSTCONDITIONS: all eighteen mutants are registered
- INVARIANTS: — (closed baseline set; kept whole per rule 6 — see req/02 CN-15)
- DEPENDENCIES: REQ-TEST-014, REQ-TEST-018
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: registry review; M9 gate
- EVIDENCE-STATUS: SPECIFIED

### REQ-TEST-013
- REQ-ID: REQ-TEST-013
- CATEGORY: test-infrastructure
- SOURCE: Red-on-Rust.md L38467–38513([54] §19); spec/01 S-21 R-TEST-04
- NORMATIVE-LEVEL: MUST
- STATEMENT: The mutation registry is additive: a previously killed mutant remains a regression requirement.
- PRECONDITIONS: the registry evolves
- POSTCONDITIONS: no mutant is removed
- INVARIANTS: —
- DEPENDENCIES: REQ-TEST-012
- SECURITY-IMPACT: medium
- VERIFICATION-METHOD: registry history review
- EVIDENCE-STATUS: SPECIFIED

### REQ-TEST-014
- REQ-ID: REQ-TEST-014
- CATEGORY: test-infrastructure
- SOURCE: Red-on-Rust.md L38506([54] §19); L38895([54] §29); L40951([58] M9); L41935–L41939([60] restated [60]); spec/01 S-21 R-TEST-05; spec/06 C-32
- NORMATIVE-LEVEL: MUST
- STATEMENT: `MutationKillRate = 100%` for all registered **non-equivalent** mutations.
- PRECONDITIONS: the mutation suite has run
- POSTCONDITIONS: no non-equivalent mutant survives
- INVARIANTS: `MutationKillRate = 100%`
- DEPENDENCIES: REQ-TEST-012, REQ-TEST-016
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: M9 mutation gate
- EVIDENCE-STATUS: SPECIFIED

### REQ-TEST-015
- REQ-ID: REQ-TEST-015
- CATEGORY: test-infrastructure
- SOURCE: Red-on-Rust.md L38494–38506([54] §19); spec/01 S-21 R-TEST-05
- NORMATIVE-LEVEL: MUST
- STATEMENT: Any surviving non-equivalent mutant blocks verification.
- PRECONDITIONS: a non-equivalent mutant survives
- POSTCONDITIONS: verification is not declared
- INVARIANTS: —
- DEPENDENCIES: REQ-TEST-014, REQ-TEST-017
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: gate enforcement
- EVIDENCE-STATUS: SPECIFIED

### REQ-TEST-016
- REQ-ID: REQ-TEST-016
- CATEGORY: test-infrastructure
- SOURCE: Red-on-Rust.md L38494–38506([54] §19); L37390–37400([50]); spec/01 S-21 R-TEST-05
- NORMATIVE-LEVEL: MUST
- STATEMENT: Equivalent mutants require explicit adjudication and documentation.
- PRECONDITIONS: a mutant is judged equivalent
- POSTCONDITIONS: the adjudication is recorded
- INVARIANTS: —
- DEPENDENCIES: REQ-TEST-023
- SECURITY-IMPACT: medium
- VERIFICATION-METHOD: adjudication record review
- EVIDENCE-STATUS: SPECIFIED

### REQ-TEST-017
- REQ-ID: REQ-TEST-017
- CATEGORY: test-infrastructure
- SOURCE: Red-on-Rust.md L38494–38506([54] §19); spec/01 S-21 R-TEST-05
- NORMATIVE-LEVEL: MUST
- STATEMENT: Mutation survivors are release-blocking defects.
- PRECONDITIONS: a release candidate
- POSTCONDITIONS: a surviving non-equivalent mutant blocks release
- INVARIANTS: —
- DEPENDENCIES: REQ-TEST-029
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: release gate
- EVIDENCE-STATUS: SPECIFIED

### REQ-TEST-018
- REQ-ID: REQ-TEST-018
- CATEGORY: test-infrastructure
- SOURCE: Red-on-Rust.md L38515–38542([54] §20); spec/01 S-21 R-TEST-06
- NORMATIVE-LEVEL: MUST
- STATEMENT: The verification system itself MUST be tested: for each mutation — inject, build, run the targeted test, run the differential suite, and assert the mutant is killed.
- PRECONDITIONS: each registered mutation
- POSTCONDITIONS: all five steps are performed and recorded
- INVARIANTS: —
- DEPENDENCIES: REQ-TEST-012
- SECURITY-IMPACT: high (an unvalidated mutation framework proves nothing)
- VERIFICATION-METHOD: mutation validation run
- EVIDENCE-STATUS: SPECIFIED

### REQ-TEST-019
- REQ-ID: REQ-TEST-019
- CATEGORY: test-infrastructure
- SOURCE: Red-on-Rust.md L38515–38542([54] §20); spec/01 S-21 R-TEST-06
- NORMATIVE-LEVEL: MUST NOT
- STATEMENT: Do not merely run the framework; the mutants must actually be killed.
- PRECONDITIONS: mutation validation
- POSTCONDITIONS: kill evidence exists per mutant
- INVARIANTS: —
- DEPENDENCIES: REQ-TEST-018
- SECURITY-IMPACT: medium
- VERIFICATION-METHOD: kill-evidence review
- EVIDENCE-STATUS: SPECIFIED

### REQ-TEST-020
- REQ-ID: REQ-TEST-020
- CATEGORY: test-infrastructure
- SOURCE: Red-on-Rust.md L38544–38578([54] §21); spec/01 S-21 R-TEST-07
- NORMATIVE-LEVEL: MUST
- STATEMENT: Coverage is tracked per stable verification-obligation tag: `CEK-CALL-ARITY-PRECHECK`, `CEK-CALL-ARGS-LTR`, `CEK-CLOSURE-LEXICAL-CAPTURE`, `CAP-DERIVE-NO-AMPLIFICATION`, `CAP-REVOCATION-ANCESTOR`, `BUDGET-CONSUMPTION-CONSERVATION`, `BUDGET-ESCROW-CONSERVATION`, `EFFECT-ISSUE-DURABLE-BEFORE-HOST`, `EFFECT-RECEIPT-DIGEST-VALIDATION`, `SCHED-FIFO`, `SCHED-BLOCKED-NOT-SCHEDULED`, `MARSHAL-NO-RAW-CAPABILITY`, `WAL-SEQUENCE-CONTINUITY`, `RECOVERY-ISSUED-INDETERMINATE`, `SNAPSHOT-COMMIT-INTEGRITY`.
- PRECONDITIONS: coverage reporting
- POSTCONDITIONS: every tag has a coverage entry
- INVARIANTS: — (frozen tag set)
- DEPENDENCIES: REQ-TEST-021
- SECURITY-IMPACT: medium
- VERIFICATION-METHOD: coverage report (nightly)
- EVIDENCE-STATUS: SPECIFIED

### REQ-TEST-021
- REQ-ID: REQ-TEST-021
- CATEGORY: test-infrastructure
- SOURCE: Red-on-Rust.md L38580–38582([54] §21); spec/01 S-21 R-TEST-07
- NORMATIVE-LEVEL: MUST NOT
- STATEMENT: Coverage metrics are evidence and are never a substitute for the differential oracle.
- PRECONDITIONS: any conformance claim
- POSTCONDITIONS: the differential oracle remains primary
- INVARIANTS: —
- DEPENDENCIES: REQ-REF-001
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: claim review
- EVIDENCE-STATUS: SPECIFIED

### REQ-TEST-022
- REQ-ID: REQ-TEST-022
- CATEGORY: test-infrastructure
- SOURCE: Red-on-Rust.md L38653–38690([54] §23); L35216–35236([47]); spec/01 S-21 R-TEST-08
- NORMATIVE-LEVEL: MUST
- STATEMENT: All T0–T6 crash points are exercised, and the exact expected classification is verified — especially `Issued ∧ ¬Completed ⇒ Indeterminate` and `Prepared ∧ ¬Issued ⇒ Discard`.
- PRECONDITIONS: crash-injection suite
- POSTCONDITIONS: each crash point produces its frozen classification
- INVARIANTS: —
- DEPENDENCIES: REQ-RECOV-003…REQ-RECOV-009
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: M10 crash/recovery gate
- EVIDENCE-STATUS: SPECIFIED

### REQ-TEST-023
- REQ-ID: REQ-TEST-023
- CATEGORY: test-infrastructure
- SOURCE: Red-on-Rust.md L38692–38712([54] §24); spec/01 S-21 R-TEST-09
- NORMATIVE-LEVEL: MUST
- STATEMENT: Every production/reference divergence MUST be classified as one of: production defect | reference defect | harness defect | specification ambiguity.
- PRECONDITIONS: a divergence is observed
- POSTCONDITIONS: a classification is recorded before any change
- INVARIANTS: —
- DEPENDENCIES: REQ-TEST-024, REQ-TEST-025
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: adjudication record review
- EVIDENCE-STATUS: SPECIFIED

### REQ-TEST-024
- REQ-ID: REQ-TEST-024
- CATEGORY: test-infrastructure
- SOURCE: Red-on-Rust.md L38692–38712([54] §24); spec/01 S-21 R-TEST-09
- NORMATIVE-LEVEL: MUST NOT
- STATEMENT: Never patch the oracle merely to make a test pass.
- PRECONDITIONS: a divergence is observed
- POSTCONDITIONS: the oracle is changed only on adjudicated grounds
- INVARIANTS: —
- DEPENDENCIES: REQ-TEST-023, REQ-CLAIM-015
- SECURITY-IMPACT: critical (silently weakening the oracle destroys the evidence base)
- VERIFICATION-METHOD: adjudication record review
- EVIDENCE-STATUS: SPECIFIED

### REQ-TEST-025
- REQ-ID: REQ-TEST-025
- CATEGORY: test-infrastructure
- SOURCE: Red-on-Rust.md L38692–38712([54] §24); L37690([54] §1.1); spec/01 S-21 R-TEST-09
- NORMATIVE-LEVEL: MUST
- STATEMENT: A divergence classified as specification ambiguity requires an explicit specification decision before implementation proceeds.
- PRECONDITIONS: classification is "specification ambiguity"
- POSTCONDITIONS: work halts pending a frozen addendum
- INVARIANTS: —
- DEPENDENCIES: REQ-SCOPE-009, REQ-SCOPE-010
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: process review
- EVIDENCE-STATUS: SPECIFIED

### REQ-TEST-026
- REQ-ID: REQ-TEST-026
- CATEGORY: test-infrastructure
- SOURCE: Red-on-Rust.md L38749–38766([54] §26 Pull request); spec/01 S-21 R-TEST-10
- NORMATIVE-LEVEL: MUST
- STATEMENT: The pull-request CI gate runs: format, lint, unit tests, exhaustive small-state, core differential tests, serialization conformance.
- PRECONDITIONS: a pull request
- POSTCONDITIONS: all six checks pass
- INVARIANTS: —
- DEPENDENCIES: REQ-TEST-001
- SECURITY-IMPACT: medium
- VERIFICATION-METHOD: CI configuration
- EVIDENCE-STATUS: SPECIFIED

### REQ-TEST-027
- REQ-ID: REQ-TEST-027
- CATEGORY: test-infrastructure
- SOURCE: Red-on-Rust.md L38767–38784([54] §26 Nightly); spec/01 S-21 R-TEST-10
- NORMATIVE-LEVEL: MUST
- STATEMENT: The nightly CI gate runs: property generation, mutation registry, full differential suite, persistence fuzzing, crash injection, semantic coverage report.
- PRECONDITIONS: nightly schedule
- POSTCONDITIONS: all six checks run
- INVARIANTS: —
- DEPENDENCIES: REQ-TEST-002, REQ-TEST-020
- SECURITY-IMPACT: medium
- VERIFICATION-METHOD: CI configuration
- EVIDENCE-STATUS: SPECIFIED

### REQ-TEST-028
- REQ-ID: REQ-TEST-028
- CATEGORY: test-infrastructure
- SOURCE: Red-on-Rust.md L38785–38806([54] §26 Release candidate); spec/01 S-21 R-TEST-10
- NORMATIVE-LEVEL: MUST
- STATEMENT: The release-candidate CI gate runs: all nightly suites, stress tests, full crash matrix, `MutationKillRate = 100%`, determinism checks, recovery differential tests, security regression suite.
- PRECONDITIONS: a release candidate
- POSTCONDITIONS: all checks pass
- INVARIANTS: `MutationKillRate = 100%`
- DEPENDENCIES: REQ-TEST-003, REQ-TEST-014, REQ-TEST-022
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: CI configuration; M11 gate
- EVIDENCE-STATUS: SPECIFIED

### REQ-TEST-029
- REQ-ID: REQ-TEST-029
- CATEGORY: test-infrastructure
- SOURCE: Red-on-Rust.md L38804–38806([54] §26); spec/01 S-21 R-TEST-10
- NORMATIVE-LEVEL: MUST NOT
- STATEMENT: No release is accepted with an unexplained differential mismatch or a surviving non-equivalent mutation.
- PRECONDITIONS: release acceptance
- POSTCONDITIONS: both conditions are clean or the release is blocked
- INVARIANTS: —
- DEPENDENCIES: REQ-TEST-017, REQ-TEST-023
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: release gate
- EVIDENCE-STATUS: SPECIFIED

### REQ-TEST-030
- REQ-ID: REQ-TEST-030
- CATEGORY: test-infrastructure
- SOURCE: Red-on-Rust.md L38877–38911([54] §29); L41196–41210([58]); spec/01 S-21 R-TEST-11
- NORMATIVE-LEVEL: MUST
- STATEMENT: The implementation is conformant only when `Observe_P(X) = Observe_R(X)` over the tested state space **and** `MutationKillRate = 100%` for all non-equivalent registered mutations **and** `Canonical(Recover_P(D)) = Canonical(Recover_R(D))` over the tested persistence state space, subject to authoritative external-effect reconciliation.
- PRECONDITIONS: conformance is being declared
- POSTCONDITIONS: all three conjuncts hold
- INVARIANTS: the 3-conjunct acceptance condition (kept whole per rule 6)
- DEPENDENCIES: REQ-REF-001, REQ-REF-002, REQ-TEST-014
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: M11 release-candidate gate
- EVIDENCE-STATUS: SPECIFIED

### REQ-TEST-031
- REQ-ID: REQ-TEST-031
- CATEGORY: test-infrastructure
- SOURCE: Red-on-Rust.md L38879([54] §29); spec/01 S-21 R-TEST-11
- NORMATIVE-LEVEL: MUST NOT
- STATEMENT: "Code compiles", "unit tests pass", and "coverage is high" are not completion.
- PRECONDITIONS: any completion or conformance claim
- POSTCONDITIONS: the claim cites the three acceptance conjuncts
- INVARIANTS: —
- DEPENDENCIES: REQ-TEST-030, REQ-CLAIM-017
- SECURITY-IMPACT: medium (claim discipline)
- VERIFICATION-METHOD: report review
- EVIDENCE-STATUS: SPECIFIED

---

### REQ-TEST-057
- REQ-ID: REQ-TEST-057
- CATEGORY: test-infrastructure
- SOURCE: Red-on-Rust.md L25223–25275([31] §26 Phase 13 property suite); spec/01 S-21 R-TEST-07
- NORMATIVE-LEVEL: SHOULD
- STATEMENT: The minimum Phase 13 acceptance suite includes the 35 enumerated properties — Scheduler (one transition per actor turn; FIFO runnable order; actor appears at most once in queue; pending, blocked and halted actors are never scheduled; receipt wakeup is deterministic; scheduler trace reproduces exactly), Spawn (fresh deterministic `ActorId`; parent budget escrowed exactly once; failed spawn leaves parent unchanged; empty environment, fresh heap, empty mailbox; attenuated child capabilities; child enqueued exactly once), Send (target actor exists; value evaluated before enqueue; value marshalled exactly once; raw capability cannot be copied; FIFO arrival; sender does not mutate recipient state directly; blocked recipient becomes runnable exactly once), Receive (empty mailbox blocks; blocking preserves continuation; nonempty mailbox dequeues exactly one message; FIFO ordering preserved; unmarshal failure becomes a machine fault; successful receive resumes continuation exactly once), and Delegation (delegated capability derived through kernel; exactly one derivation; exact constraint forwarded; child capability no more powerful than parent; raw `CapRef` transfer impossible through ordinary marshalling; revoked parent cannot delegate).
- PRECONDITIONS: Phase 13 (actors) is implemented
- POSTCONDITIONS: every enumerated property has a passing test in the acceptance suite
- INVARIANTS: —
- DEPENDENCIES: REQ-ACTOR-010, REQ-ACTOR-011, REQ-ACTOR-012, REQ-ACTOR-032, REQ-ORDER-010
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: acceptance suite with one named test per enumerated property (35)
- EVIDENCE-STATUS: SPECIFIED
