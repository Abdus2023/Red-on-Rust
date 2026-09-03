# Atomic Requirement Registry — Part 8: Phase 15C Reference Model and Differential Harness

Areas: `REF` (19), `TEST` (25) — 44 atomic units.
Phase 15C (turn `[48]`, `Red-on-Rust.md` L35272–37168) is the frozen specification of the independent reference model and the differential harness. The turn-`[54]` master prompt restates these obligations compactly in §15–§22; the records below carry the primary 15C text and its line ranges, which the earlier parts did not cite.

---

### REQ-REF-018
- REQ-ID: REQ-REF-018
- CATEGORY: verification
- SOURCE: Red-on-Rust.md L35326–35346([48] 15C.2 Non-Goals); spec/01 S-20 R-REF-04
- NORMATIVE-LEVEL: MUST NOT
- STATEMENT: Phase 15C MUST NOT redefine language semantics, change capability, budget, actor-scheduling, or persistence semantics, or introduce a second canonical serialization format.
- PRECONDITIONS: reference-model work
- POSTCONDITIONS: none of the six occurs
- INVARIANTS: —
- DEPENDENCIES: REQ-REF-009, REQ-SCOPE-008
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: scope review against the frozen surface
- EVIDENCE-STATUS: SPECIFIED

### REQ-REF-019
- REQ-ID: REQ-REF-019
- CATEGORY: verification
- SOURCE: Red-on-Rust.md L35440–35483([48] 15C.4 Reference Value Model); spec/01 S-20 R-REF-03
- NORMATIVE-LEVEL: IS
- STATEMENT: The reference model defines its own value domain `RefValue` rather than reusing the production `Value`.
- PRECONDITIONS: reference-model construction
- POSTCONDITIONS: an independent value domain exists
- INVARIANTS: —
- DEPENDENCIES: REQ-REF-004, REQ-CALC-001
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: dependency review; type review
- EVIDENCE-STATUS: SPECIFIED

### REQ-REF-020
- REQ-ID: REQ-REF-020
- CATEGORY: verification
- SOURCE: Red-on-Rust.md L35484–35513([48] 15C.5 Reference Environment); spec/01 S-20 R-REF-03
- NORMATIVE-LEVEL: MUST
- STATEMENT: The reference environment `RefEnv` binds symbols directly, looks up from the newest binding toward the oldest, and creates a new environment on extension.
- PRECONDITIONS: reference evaluation
- POSTCONDITIONS: lexical lookup order holds
- INVARIANTS: —
- DEPENDENCIES: REQ-CALC-014, REQ-CEK-016
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: lexical-capture differential; `CEK-CLOSURE-LEXICAL-CAPTURE`
- EVIDENCE-STATUS: SPECIFIED

### REQ-REF-021
- REQ-ID: REQ-REF-021
- CATEGORY: verification
- SOURCE: Red-on-Rust.md L35514–35619([48] 15C.6 Reference CEK Machine); spec/01 S-20 R-REF-03
- NORMATIVE-LEVEL: IS
- STATEMENT: The reference machine state is `RefState { expr, env, continuation }` with the continuation represented directly as a vector of `RefFrame`.
- PRECONDITIONS: reference evaluation
- POSTCONDITIONS: —
- INVARIANTS: —
- DEPENDENCIES: REQ-CEK-001, REQ-CEK-007
- SECURITY-IMPACT: medium
- VERIFICATION-METHOD: state-shape review
- EVIDENCE-STATUS: SPECIFIED

### REQ-REF-022
- REQ-ID: REQ-REF-022
- CATEGORY: verification
- SOURCE: Red-on-Rust.md L35620–35690([48] 15C.7 Reference CEK Transition Rules); spec/01 S-20 R-REF-03
- NORMATIVE-LEVEL: MUST
- STATEMENT: The reference machine implements the frozen Phase 10 transition rules; a value terminates only when the continuation is empty, and the machine never invokes itself recursively.
- PRECONDITIONS: reference evaluation
- POSTCONDITIONS: halt and recursion rules hold
- INVARIANTS: —
- DEPENDENCIES: REQ-CEK-002, REQ-REF-008
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: differential agreement on the pure subset; recursion review
- EVIDENCE-STATUS: SPECIFIED

### REQ-REF-023
- REQ-ID: REQ-REF-023
- CATEGORY: verification
- SOURCE: Red-on-Rust.md L35691–35764([48] 15C.8 Reference Capability Algebra); spec/01 S-20 R-REF-03
- NORMATIVE-LEVEL: MUST
- STATEMENT: The reference capability algebra independently implements the frozen Phase 11 algebra over `RefAuthority` and `RefOperationAuthority`.
- PRECONDITIONS: reference authorization
- POSTCONDITIONS: no production algebra code is reused
- INVARIANTS: —
- DEPENDENCIES: REQ-REF-006, REQ-CAP-012
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: dependency review; algebra property differential
- EVIDENCE-STATUS: SPECIFIED

### REQ-REF-024
- REQ-ID: REQ-REF-024
- CATEGORY: verification
- SOURCE: Red-on-Rust.md L35765–35800([48] 15C.9 Reference Capability State); spec/01 S-20 R-REF-03
- NORMATIVE-LEVEL: IS
- STATEMENT: The reference capability store `RefCapabilityStore` holds authorities, parent links, generations, and a live set.
- PRECONDITIONS: reference authorization
- POSTCONDITIONS: —
- INVARIANTS: —
- DEPENDENCIES: REQ-KERN-001, REQ-CAP-013
- SECURITY-IMPACT: medium
- VERIFICATION-METHOD: state-shape review
- EVIDENCE-STATUS: SPECIFIED

### REQ-REF-025
- REQ-ID: REQ-REF-025
- CATEGORY: verification
- SOURCE: Red-on-Rust.md L35801–35847([48] 15C.10 Reference Budget Model); spec/01 S-20 R-REF-03
- NORMATIVE-LEVEL: MUST
- STATEMENT: The reference budget model is independent of production arithmetic and defines its own `RefConsumable` and `RefReserved`.
- PRECONDITIONS: reference budgeting
- POSTCONDITIONS: no production budget code is reused
- INVARIANTS: —
- DEPENDENCIES: REQ-REF-004, REQ-BUDGET-002
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: dependency review; budget differential
- EVIDENCE-STATUS: SPECIFIED

### REQ-REF-026
- REQ-ID: REQ-REF-026
- CATEGORY: verification
- SOURCE: Red-on-Rust.md L35848–35892([48] 15C.11 Reference Effect Protocol); spec/01 S-20 R-REF-03
- NORMATIVE-LEVEL: MUST
- STATEMENT: The reference effect model implements the frozen Phase 12 issuance sequence in the same order.
- PRECONDITIONS: reference effect execution
- POSTCONDITIONS: the sequence matches the frozen order
- INVARIANTS: —
- DEPENDENCIES: REQ-EFFECT-005
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: effect-trace differential
- EVIDENCE-STATUS: SPECIFIED

### REQ-REF-027
- REQ-ID: REQ-REF-027
- CATEGORY: verification
- SOURCE: Red-on-Rust.md L35893–35926([48] 15C.12 Reference Actor Model); spec/01 S-20 R-REF-03
- NORMATIVE-LEVEL: IS
- STATEMENT: The reference actor state `RefActor` is independently defined with its own `RefRunState`.
- PRECONDITIONS: reference concurrency
- POSTCONDITIONS: —
- INVARIANTS: —
- DEPENDENCIES: REQ-ACTOR-004, REQ-ACTOR-035
- SECURITY-IMPACT: medium
- VERIFICATION-METHOD: state-shape review
- EVIDENCE-STATUS: SPECIFIED

### REQ-REF-028
- REQ-ID: REQ-REF-028
- CATEGORY: verification
- SOURCE: Red-on-Rust.md L35927–35972([48] 15C.13 Reference Scheduler); spec/01 S-20 R-REF-03
- NORMATIVE-LEVEL: MUST
- STATEMENT: The reference scheduler is deterministic FIFO over a `RefScheduler` runnable deque.
- PRECONDITIONS: reference scheduling
- POSTCONDITIONS: selection order matches production
- INVARIANTS: ∀a: count_queue(a) ≤ 1
- DEPENDENCIES: REQ-ACTOR-010, REQ-ACTOR-011
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: `SCHED-FIFO` differential
- EVIDENCE-STATUS: SPECIFIED

### REQ-REF-029
- REQ-ID: REQ-REF-029
- CATEGORY: verification
- SOURCE: Red-on-Rust.md L35973–36004([48] 15C.14 Reference Send / Receive); spec/01 S-20 R-REF-03
- NORMATIVE-LEVEL: MUST
- STATEMENT: Reference `Send` evaluates target, then value, then marshalling, then recipient validation, then mailbox insertion; ordinary capability-containing values are rejected.
- PRECONDITIONS: reference messaging
- POSTCONDITIONS: the five steps occur in order and raw capabilities are refused
- INVARIANTS: —
- DEPENDENCIES: REQ-ACTOR-026, REQ-MARSHAL-001
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: messaging differential; `MARSHAL-NO-RAW-CAPABILITY`
- EVIDENCE-STATUS: SPECIFIED

### REQ-REF-030
- REQ-ID: REQ-REF-030
- CATEGORY: verification
- SOURCE: Red-on-Rust.md L36005–36031([48] 15C.15 Reference Marshalling); spec/01 S-20 R-REF-03
- NORMATIVE-LEVEL: MUST
- STATEMENT: The reference marshaller is independent of the production marshaller and satisfies `unmarshal(marshal(v)) = v` for all marshalable values; nested capabilities are rejected.
- PRECONDITIONS: reference messaging
- POSTCONDITIONS: round-trip holds on the marshalable domain
- INVARIANTS: unmarshal(marshal(v)) = v
- DEPENDENCIES: REQ-MARSHAL-008, REQ-REF-004
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: Track B round-trip differential
- EVIDENCE-STATUS: SPECIFIED

### REQ-REF-031
- REQ-ID: REQ-REF-031
- CATEGORY: verification
- SOURCE: Red-on-Rust.md L36032–36056([48] 15C.16 Reference Global State); spec/01 S-20 R-REF-03
- NORMATIVE-LEVEL: IS
- STATEMENT: The reference global state `RefGlobalState` holds actors, logical time, the runnable scheduler, event log, and ID counters.
- PRECONDITIONS: reference execution
- POSTCONDITIONS: —
- INVARIANTS: —
- DEPENDENCIES: REQ-ACTOR-006, REQ-CALC-017
- SECURITY-IMPACT: medium
- VERIFICATION-METHOD: state-shape review
- EVIDENCE-STATUS: SPECIFIED

### REQ-REF-032
- REQ-ID: REQ-REF-032
- CATEGORY: verification
- SOURCE: Red-on-Rust.md L36057–36107([48] 15C.17 Reference Persistence Model); spec/01 S-20 R-REF-03
- NORMATIVE-LEVEL: MUST
- STATEMENT: The reference persistence model does not reuse production persistence code; it consumes abstract `Snapshot`, `WAL`, and `EffectJournal` records and performs its own recovery steps.
- PRECONDITIONS: reference recovery
- POSTCONDITIONS: no production persistence dependency exists
- INVARIANTS: —
- DEPENDENCIES: REQ-RECOV-014, REQ-REF-004
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: dependency-graph review
- EVIDENCE-STATUS: SPECIFIED

### REQ-REF-033
- REQ-ID: REQ-REF-033
- CATEGORY: verification
- SOURCE: Red-on-Rust.md L36108–36125([48] 15C.18 Reference Crash Semantics); spec/01 S-20 R-REF-03
- NORMATIVE-LEVEL: MUST
- STATEMENT: The reference model implements the frozen T0–T6 crash matrix, including `Prepared ∧ ¬Issued ⇒ Discard` and `Issued ∧ ¬Completed ⇒ Indeterminate`.
- PRECONDITIONS: reference recovery
- POSTCONDITIONS: the classifications match the frozen matrix
- INVARIANTS: Prepared ∧ ¬Issued ⇒ Discard
- DEPENDENCIES: REQ-RECOV-003, REQ-DUR-010
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: crash-matrix differential
- EVIDENCE-STATUS: SPECIFIED

### REQ-REF-034
- REQ-ID: REQ-REF-034
- CATEGORY: verification
- SOURCE: Red-on-Rust.md L36126–36159([48] 15C.19 Reference Host Model); spec/01 S-20 R-REF-03
- NORMATIVE-LEVEL: MUST
- STATEMENT: The reference host `RefHost` is a pure trace consumer over an ordered `RefReceipt` vector and validates each receipt before resuming.
- PRECONDITIONS: reference host boundary
- POSTCONDITIONS: no host side effect originates in the reference
- INVARIANTS: —
- DEPENDENCIES: REQ-HOST-006, REQ-EFFECT-027
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: receipt-validation differential
- EVIDENCE-STATUS: SPECIFIED

### REQ-REF-035
- REQ-ID: REQ-REF-035
- CATEGORY: verification
- SOURCE: Red-on-Rust.md L36160–36188([48] 15C.20 Reference Observations); spec/01 S-20 R-REF-05
- NORMATIVE-LEVEL: IS
- STATEMENT: Both implementations emit a normalized `Observation` (terminal states, event trace, effects, budgets, and the remaining frozen channels) instead of exposing internal structure.
- PRECONDITIONS: differential comparison
- POSTCONDITIONS: the observation boundary is defined
- INVARIANTS: —
- DEPENDENCIES: REQ-REF-010, REQ-REF-013
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: comparator review
- EVIDENCE-STATUS: SPECIFIED

### REQ-REF-036
- REQ-ID: REQ-REF-036
- CATEGORY: verification
- SOURCE: Red-on-Rust.md L36189–36214([48] 15C.21 Canonical Actor Identity Mapping); spec/01 S-20 R-REF-05
- NORMATIVE-LEVEL: MUST
- STATEMENT: The harness establishes a deterministic correspondence between production and reference identifiers: it asserts numeric equality when identifiers are expected to be identical, and otherwise compares normalized identity allocation order.
- PRECONDITIONS: differential comparison
- POSTCONDITIONS: identifier correspondence is deterministic and asserted
- INVARIANTS: —
- DEPENDENCIES: REQ-ACTOR-008, REQ-EFFECT-024
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: identity-mapping tests
- EVIDENCE-STATUS: SPECIFIED

### REQ-TEST-032
- REQ-ID: REQ-TEST-032
- CATEGORY: test-infrastructure
- SOURCE: Red-on-Rust.md L36215–36249([48] 15C.22 Differential Harness); spec/01 S-20 R-REF-01
- NORMATIVE-LEVEL: MUST
- STATEMENT: The differential harness executes the same generated semantic input against the production and the reference implementation and compares their normalized observations.
- PRECONDITIONS: any differential run
- POSTCONDITIONS: both implementations run on identical input
- INVARIANTS: —
- DEPENDENCIES: REQ-REF-012, REQ-TEST-006
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: harness review; differential run
- EVIDENCE-STATUS: SPECIFIED

### REQ-TEST-033
- REQ-ID: REQ-TEST-033
- CATEGORY: test-infrastructure
- SOURCE: Red-on-Rust.md L36250–36310([48] 15C.23 Differential Comparison Levels); spec/01 S-20 R-REF-05
- NORMATIVE-LEVEL: MUST
- STATEMENT: Comparison proceeds through progressively stronger levels: terminal semantics, then event semantics, then the remaining frozen levels.
- PRECONDITIONS: any differential comparison
- POSTCONDITIONS: each level is compared before the comparison passes
- INVARIANTS: —
- DEPENDENCIES: REQ-REF-013, REQ-TEST-007
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: comparator review; level-coverage assertions
- EVIDENCE-STATUS: SPECIFIED

### REQ-TEST-034
- REQ-ID: REQ-TEST-034
- CATEGORY: test-infrastructure
- SOURCE: Red-on-Rust.md L36311–36358([48] 15C.24 Trace Normalization); spec/01 S-20 R-REF-05
- NORMATIVE-LEVEL: MUST
- STATEMENT: Trace comparison distinguishes semantic from implementation-specific events: the included set is `ActorSelected`, `ActorSpawned`, `CapabilityDerived`, `Send`, `Receive`, `Blocked`, `Woken`, and the excluded set is implementation detail.
- PRECONDITIONS: any trace comparison
- POSTCONDITIONS: only semantic events are compared
- INVARIANTS: —
- DEPENDENCIES: REQ-REF-011, REQ-REF-010
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: normalizer review; trace-diff tests
- EVIDENCE-STATUS: SPECIFIED

### REQ-TEST-035
- REQ-ID: REQ-TEST-035
- CATEGORY: test-infrastructure
- SOURCE: Red-on-Rust.md L36359–36399([48] 15C.25 Negative Differential Testing); spec/01 S-21 R-TEST-07
- NORMATIVE-LEVEL: MUST
- STATEMENT: The harness deliberately generates cases in which production is expected to reject an operation, covering invalid capability, expired capability, revoked ancestor, insufficient scope, parameter-constraint failure, resource-ceiling violation, and runtime budget exhaustion.
- PRECONDITIONS: negative differential testing
- POSTCONDITIONS: each rejection class is generated and compared
- INVARIANTS: —
- DEPENDENCIES: REQ-EFFECT-019, REQ-CAP-013
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: negative-case differential
- EVIDENCE-STATUS: SPECIFIED

### REQ-TEST-036
- REQ-ID: REQ-TEST-036
- CATEGORY: test-infrastructure
- SOURCE: Red-on-Rust.md L36400–36440([48] 15C.26 Short-Circuit Differential Tests); spec/01 S-21 R-TEST-07
- NORMATIVE-LEVEL: MUST
- STATEMENT: For gated operations, generated tests attach observable markers to every stage — capability evaluation, target evaluation, argument 0, argument 1, authorization, budget, deadline, host policy — so that short-circuiting is observable: if capability validation fails the expected trace ends before target evaluation, and if authorization fails the expected trace is target + arguments evaluated, authorization attempted, budget/deadline/host gates not executed.
- PRECONDITIONS: gated-operation testing
- POSTCONDITIONS: per-stage markers are emitted and compared; the harness detects accidental evaluation or authorization reordering
- INVARIANTS: —
- DEPENDENCIES: REQ-EFFECT-019, REQ-TEST-008
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: short-circuit differential
- EVIDENCE-STATUS: SPECIFIED

### REQ-TEST-037
- REQ-ID: REQ-TEST-037
- CATEGORY: test-infrastructure
- SOURCE: Red-on-Rust.md L36441–36506([48] 15C.27 Reference Property Suite); spec/01 S-21 R-TEST-07
- NORMATIVE-LEVEL: MUST
- STATEMENT: The reference property suite asserts the enumerated per-area properties, beginning with the CEK set: values halt only with empty continuation; lambda captures the lexical environment; function evaluates before arguments; arguments evaluate left-to-right; arity mismatch precedes argument evaluation; non-function application faults; caller environment stays distinct from closure environment; parameter bindings occur in declared order.
- PRECONDITIONS: reference property testing
- POSTCONDITIONS: each enumerated property is asserted
- INVARIANTS: —
- DEPENDENCIES: REQ-CEK-013, REQ-CEK-014, REQ-CEK-016
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: property suite; per-property test identities
- EVIDENCE-STATUS: SPECIFIED

### REQ-TEST-038
- REQ-ID: REQ-TEST-038
- CATEGORY: test-infrastructure
- SOURCE: Red-on-Rust.md L36507–36565([48] 15C.28 Generated Program Grammar); spec/01 S-21 R-TEST-01
- NORMATIVE-LEVEL: SHOULD
- STATEMENT: The generator initially targets a deliberately bounded grammar over `Value`, `Var`, `Let`, `Seq`, `If`, `Lambda`, and `Call`.
- PRECONDITIONS: program generation
- POSTCONDITIONS: generated programs stay within the bounded grammar
- INVARIANTS: —
- DEPENDENCIES: REQ-TEST-006
- SECURITY-IMPACT: medium
- VERIFICATION-METHOD: generator grammar review
- EVIDENCE-STATUS: SPECIFIED

### REQ-TEST-039
- REQ-ID: REQ-TEST-039
- CATEGORY: test-infrastructure
- SOURCE: Red-on-Rust.md L36566–36609([48] 15C.29 Generator Strategy); spec/01 S-21 R-TEST-01
- NORMATIVE-LEVEL: SHOULD
- STATEMENT: Generation is layered — seed, structure, type/environment-aware, capability — rather than unrestricted random syntax, and each generator records the assumptions it used.
- PRECONDITIONS: program generation
- POSTCONDITIONS: each layer is applied in order
- INVARIANTS: —
- DEPENDENCIES: REQ-TEST-006
- SECURITY-IMPACT: medium
- VERIFICATION-METHOD: generator review
- EVIDENCE-STATUS: SPECIFIED

### REQ-TEST-040
- REQ-ID: REQ-TEST-040
- CATEGORY: test-infrastructure
- SOURCE: Red-on-Rust.md L36610–36634([48] 15C.30 Shrinking); spec/01 S-21 R-TEST-03
- NORMATIVE-LEVEL: MUST
- STATEMENT: Every differential failure is shrinkable, in the order: actor count, expression depth, call arity, list/tuple size, unnecessary bindings, capability operations, capability scopes.
- PRECONDITIONS: a differential failure occurs
- POSTCONDITIONS: a smaller reproducing case is produced
- INVARIANTS: —
- DEPENDENCIES: REQ-TEST-009
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: shrinker tests; shrink-order assertions
- EVIDENCE-STATUS: SPECIFIED

### REQ-TEST-041
- REQ-ID: REQ-TEST-041
- CATEGORY: test-infrastructure
- SOURCE: Red-on-Rust.md L36635–36665([48] 15C.31 Counterexample Format); L36606([48] 15C.29 Generator Strategy); spec/01 S-21 R-TEST-02
- NORMATIVE-LEVEL: MUST
- STATEMENT: Every failure produces the counterexample record: seed, generated program, initial machine state, capability state, initial budgets, actor topology, scheduler configuration, and host trace.
- PRECONDITIONS: a differential failure occurs
- POSTCONDITIONS: the record is complete and rerunnable
- INVARIANTS: —
- DEPENDENCIES: REQ-TEST-007
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: counterexample completeness assertions
- EVIDENCE-STATUS: SPECIFIED

### REQ-TEST-042
- REQ-ID: REQ-TEST-042
- CATEGORY: test-infrastructure
- SOURCE: Red-on-Rust.md L36666–36689([48] 15C.32 First-Divergence Algorithm); spec/01 S-21 R-TEST-09
- NORMATIVE-LEVEL: SHOULD
- STATEMENT: The comparator compares traces event-by-event, reports the first divergence index and both events, and stops before comparing terminal and resource state.
- PRECONDITIONS: a trace mismatch occurs
- POSTCONDITIONS: exactly one divergence is reported
- INVARIANTS: —
- DEPENDENCIES: REQ-REF-012
- SECURITY-IMPACT: medium
- VERIFICATION-METHOD: first-divergence tests
- EVIDENCE-STATUS: SPECIFIED

### REQ-TEST-043
- REQ-ID: REQ-TEST-043
- CATEGORY: test-infrastructure
- SOURCE: Red-on-Rust.md L36690–36731([48] 15C.33 Metamorphic Testing); spec/01 S-21 R-TEST-07
- NORMATIVE-LEVEL: SHOULD
- STATEMENT: Differential testing is supplemented by metamorphic semantic transformations, such as `let x = v in x` equalling `v` for closed pure expressions.
- PRECONDITIONS: property testing
- POSTCONDITIONS: each metamorphic relation is asserted
- INVARIANTS: —
- DEPENDENCIES: REQ-TEST-005
- SECURITY-IMPACT: medium
- VERIFICATION-METHOD: metamorphic property tests
- EVIDENCE-STATUS: SPECIFIED

### REQ-TEST-044
- REQ-ID: REQ-TEST-044
- CATEGORY: test-infrastructure
- SOURCE: Red-on-Rust.md L36732–36780([48] 15C.34 Differential Persistence Testing); spec/01 S-21 R-TEST-08
- NORMATIVE-LEVEL: MUST
- STATEMENT: Each generated persistence scenario runs, injects a crash, persists the image, recovers through both implementations, and compares the recovered observations.
- PRECONDITIONS: differential persistence testing
- POSTCONDITIONS: recovery agreement is asserted per scenario
- INVARIANTS: —
- DEPENDENCIES: REQ-RECOV-015, REQ-TEST-022
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: crash differential
- EVIDENCE-STATUS: SPECIFIED

### REQ-TEST-045
- REQ-ID: REQ-TEST-045
- CATEGORY: test-infrastructure
- SOURCE: Red-on-Rust.md L36781–36808([48] 15C.35 Reference Recovery Independence); spec/01 S-20 R-REF-02
- NORMATIVE-LEVEL: MUST NOT
- STATEMENT: The reference recovery engine MUST NOT consume the production snapshot decoder or production WAL parser; it receives semantic records from an independent test-side decoder, and byte-format conformance is verified separately from semantic recovery conformance.
- PRECONDITIONS: reference recovery
- POSTCONDITIONS: the two conformance questions stay separate
- INVARIANTS: —
- DEPENDENCIES: REQ-RECOV-014, REQ-CLAIM-011
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: dependency-graph review
- EVIDENCE-STATUS: SPECIFIED

### REQ-TEST-046
- REQ-ID: REQ-TEST-046
- CATEGORY: test-infrastructure
- SOURCE: Red-on-Rust.md L36809–36834([48] 15C.36 Canonical Serialization Differential Boundary); spec/01 S-20 R-REF-02
- NORMATIVE-LEVEL: MUST
- STATEMENT: The 15C harness may treat canonical bytes as opaque inputs and outputs, but the reference semantic machine MUST NOT implement the canonical format; where an independent reference encoder exists for the test domain, `Canonical_P(v) = Canonical_R(v)` is required.
- PRECONDITIONS: canonical differential testing
- POSTCONDITIONS: byte-level agreement is asserted only against an independent encoder
- INVARIANTS: Canonical_P(v) = Canonical_R(v)
- DEPENDENCIES: REQ-CANON-037, REQ-CLAIM-012
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: byte-level differential
- EVIDENCE-STATUS: SPECIFIED

### REQ-TEST-047
- REQ-ID: REQ-TEST-047
- CATEGORY: test-infrastructure
- SOURCE: Red-on-Rust.md L36835–36860([48] 15C.37 Oracle Hierarchy); spec/01 S-20 R-REF-02
- NORMATIVE-LEVEL: SHOULD
- STATEMENT: The verification system keeps six independent oracles — CEK, capability, budget, scheduler, persistence recovery, and an independent canonical-format decoder — rather than fusing them into one implementation.
- PRECONDITIONS: verification design
- POSTCONDITIONS: the oracles remain separate
- INVARIANTS: —
- DEPENDENCIES: REQ-REF-007, REQ-REF-004
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: oracle-separation review
- EVIDENCE-STATUS: SPECIFIED

### REQ-TEST-048
- REQ-ID: REQ-TEST-048
- CATEGORY: test-infrastructure
- SOURCE: Red-on-Rust.md L36861–36891([48] 15C.38 Anti-Oracle-Collapse Rules); spec/01 S-20 R-REF-02
- NORMATIVE-LEVEL: MUST NOT
- STATEMENT: The reference MUST NOT call `production_step`, `production_kernel.authorize`, `production_budget`, `production_recover`, `production_encode`, or `production_scheduler`, and production implementation bodies MUST NOT be copied into the reference module.
- PRECONDITIONS: reference implementation
- POSTCONDITIONS: no oracle collapse occurs
- INVARIANTS: —
- DEPENDENCIES: REQ-REF-004, REQ-REF-007
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: dependency review; code-similarity review
- EVIDENCE-STATUS: SPECIFIED

### REQ-TEST-049
- REQ-ID: REQ-TEST-049
- CATEGORY: test-infrastructure
- SOURCE: Red-on-Rust.md L36892–36934([48] 15C.39 Differential Test Execution Modes); spec/01 S-21 R-TEST-01
- NORMATIVE-LEVEL: MUST
- STATEMENT: Three differential execution modes are required: exhaustive small-state, property-generated, and stress.
- PRECONDITIONS: differential execution
- POSTCONDITIONS: all three modes exist and run
- INVARIANTS: —
- DEPENDENCIES: REQ-TEST-001, REQ-TEST-002, REQ-TEST-003
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: mode-coverage review; CI gate
- EVIDENCE-STATUS: SPECIFIED

### REQ-TEST-050
- REQ-ID: REQ-TEST-050
- CATEGORY: test-infrastructure
- SOURCE: Red-on-Rust.md L36935–36976([48] 15C.40 Determinism Requirement); L36595–36601([48] 15C.29 Generator Strategy); spec/01 S-21 R-TEST-02
- NORMATIVE-LEVEL: MUST
- STATEMENT: Running the same differential case twice with the same seed, initial state, accepted planner trace, scheduler policy, host trace, and crash trace produces byte-identical test observations.
- PRECONDITIONS: any differential run
- POSTCONDITIONS: observations are byte-identical across runs
- INVARIANTS: —
- DEPENDENCIES: REQ-CORE-011, REQ-TEST-029
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: repeat-run determinism test
- EVIDENCE-STATUS: SPECIFIED

### REQ-TEST-051
- REQ-ID: REQ-TEST-051
- CATEGORY: test-infrastructure
- SOURCE: Red-on-Rust.md L36977–36996([48] 15C.41 LLM Boundary Testing); spec/01 S-05 R-PLANNER-05
- NORMATIVE-LEVEL: MUST
- STATEMENT: The LLM appears in the harness only as an input generator; generated `PlanProposal` values are untrusted data, and tests MUST verify that malformed or adversarial proposals cannot create capabilities, bypass compilation, mutate budgets, allocate actors outside the machine, invoke hosts, or alter scheduler state.
- PRECONDITIONS: LLM-boundary testing
- POSTCONDITIONS: all six escalations are refused
- INVARIANTS: —
- DEPENDENCIES: REQ-PLANNER-003, REQ-SCOPE-004
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: adversarial-proposal tests
- EVIDENCE-STATUS: SPECIFIED

### REQ-TEST-052
- REQ-ID: REQ-TEST-052
- CATEGORY: test-infrastructure
- SOURCE: Red-on-Rust.md L36997–37021([48] 15C.42 Acceptance Criteria); spec/01 S-20 R-REF-02
- NORMATIVE-LEVEL: MUST
- STATEMENT: Phase 15C is complete only when the reference CEK, capability algebra, budget accounting, scheduler, actor semantics, and persistence recovery are each independently implemented, the reference host consumes its own ordered trace, and production/reference observations have a defined comparison boundary.
- PRECONDITIONS: phase completion is claimed
- POSTCONDITIONS: all eight conditions hold
- INVARIANTS: —
- DEPENDENCIES: REQ-REF-004, REQ-ORDER-025
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: phase-acceptance review
- EVIDENCE-STATUS: SPECIFIED

### REQ-TEST-053
- REQ-ID: REQ-TEST-053
- CATEGORY: test-infrastructure
- SOURCE: Red-on-Rust.md L37022–37053([48] 15C.43 Deliberate Fault-Injection Validation); spec/01 S-21 R-TEST-06
- NORMATIVE-LEVEL: MUST
- STATEMENT: Before the harness is trusted, known defects are deliberately introduced into a temporary production build — reversed argument order, skipped arity precheck, accepted revoked capability, omitted budget gate, `EffectId` allocated before authorization, escrow released after an indeterminate effect, dropped mailbox FIFO ordering — and the harness must detect each.
- PRECONDITIONS: harness validation
- POSTCONDITIONS: every injected defect is detected
- INVARIANTS: —
- DEPENDENCIES: REQ-TEST-012, REQ-TEST-014
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: fault-injection validation run
- EVIDENCE-STATUS: SPECIFIED

### REQ-TEST-054
- REQ-ID: REQ-TEST-054
- CATEGORY: test-infrastructure
- SOURCE: Red-on-Rust.md L37054–37089([48] 15C.44 Evidence Classification); spec/01 S-21 R-TEST-09
- NORMATIVE-LEVEL: SHOULD
- STATEMENT: Results are classified explicitly into strong evidence (exhaustive small-state agreement, broad generated agreement, successful deliberate-fault detection, crash-boundary agreement, independent byte-level conformance, repeated deterministic reproduction) and supporting evidence.
- PRECONDITIONS: reporting results
- POSTCONDITIONS: the classification is stated
- INVARIANTS: —
- DEPENDENCIES: REQ-CLAIM-017, REQ-TEST-031
- SECURITY-IMPACT: medium
- VERIFICATION-METHOD: report review
- EVIDENCE-STATUS: SPECIFIED

### REQ-TEST-055
- REQ-ID: REQ-TEST-055
- CATEGORY: test-infrastructure
- SOURCE: Red-on-Rust.md L37090–37150([48] 15C.45 Final Verification Theorem); spec/01 S-21 R-TEST-11
- NORMATIVE-LEVEL: MUST
- STATEMENT: The principal Phase 15C property is `Observe_P(X) = Observe_R(X)` for every tested execution input `X`, with the corresponding recovery property for durable inputs.
- PRECONDITIONS: differential testing
- POSTCONDITIONS: observations agree over the tested space
- INVARIANTS: Observe_P(X) = Observe_R(X)
- DEPENDENCIES: REQ-REF-013, REQ-RECOV-015
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: differential suite; acceptance gate
- EVIDENCE-STATUS: SPECIFIED

### REQ-TEST-056
- REQ-ID: REQ-TEST-056
- CATEGORY: test-infrastructure
- SOURCE: Red-on-Rust.md L37151–37168([48] 15C.46 Phase Boundary); spec/01 S-20 R-REF-01
- NORMATIVE-LEVEL: IS
- STATEMENT: At completion of Phase 15C the semantic definitions remain frozen, production remains authoritative for execution, the reference is authoritative only as a test oracle, the differential harness is the primary regression mechanism, persistence recovery is tested against an independent implementation, and deliberate mutation testing validates oracle sensitivity.
- PRECONDITIONS: phase boundary
- POSTCONDITIONS: the authority roles are as stated
- INVARIANTS: —
- DEPENDENCIES: REQ-SCOPE-006, REQ-REF-003
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: phase-boundary review
- EVIDENCE-STATUS: SPECIFIED

