# Atomic Requirement Registry — Part 3: Resources and Effects (S-11, S-12)

Areas: `BUDGET` (32), `EFFECT` (40) — 72 atomic units.
The v0.3 budget/transition text (`Red-on-Rust.md` L8643–9050, turn `[16]`) is frozen per `spec/02` S-11 provenance; its transition rules are extracted here as **(v0.3 rules)**.

---

## S-11 Budget model

### REQ-BUDGET-001
- REQ-ID: REQ-BUDGET-001
- CATEGORY: budget
- SOURCE: Red-on-Rust.md L8683–8690([16] v0.3 frozen); L9172–9180([17]); L41537–41560([60]); spec/01 S-11 R-BUDGET-01; spec/06 C-06
- NORMATIVE-LEVEL: IS
- STATEMENT: Budget `B = ⟨C, R, W⟩`.
- PRECONDITIONS: —
- POSTCONDITIONS: —
- INVARIANTS: —
- DEPENDENCIES: REQ-BUDGET-002…REQ-BUDGET-004
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: type review; snapshot content review
- EVIDENCE-STATUS: SPECIFIED

### REQ-BUDGET-002
- REQ-ID: REQ-BUDGET-002
- CATEGORY: budget
- SOURCE: Red-on-Rust.md L8683–8690([16]); L37966–37978([54] §7); spec/01 S-11 R-BUDGET-01
- NORMATIVE-LEVEL: IS
- STATEMENT: `C = ⟨F, I, D⟩` — consumables: fuel, I/O, duration.
- PRECONDITIONS: —
- POSTCONDITIONS: —
- INVARIANTS: —
- DEPENDENCIES: REQ-BUDGET-005, REQ-BUDGET-008; U-01
- SECURITY-IMPACT: high ; AMB-22
- VERIFICATION-METHOD: budget dimension coverage in property generation
- EVIDENCE-STATUS: SPECIFIED

### REQ-BUDGET-003
- REQ-ID: REQ-BUDGET-003
- CATEGORY: budget
- SOURCE: Red-on-Rust.md L8683–8690([16]); L37980–37990([54] §7); spec/01 S-11 R-BUDGET-01
- NORMATIVE-LEVEL: IS
- STATEMENT: `R = ⟨M, S⟩` — reserved: memory bytes, concurrency slots.
- PRECONDITIONS: —
- POSTCONDITIONS: —
- INVARIANTS: —
- DEPENDENCIES: REQ-BUDGET-006, REQ-BUDGET-009
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: reservation property tests
- EVIDENCE-STATUS: SPECIFIED

### REQ-BUDGET-004
- REQ-ID: REQ-BUDGET-004
- CATEGORY: budget
- SOURCE: Red-on-Rust.md L8683–8700([16]); L10199 ([18]) ([18] `Deadline(Option<LogicalTime>)`); spec/01 S-11 R-BUDGET-01
- NORMATIVE-LEVEL: IS
- STATEMENT: `W ∈ ℕ ∪ {∞}` is an absolute logical-time deadline; `Deadline(None)` = infinity.
- PRECONDITIONS: —
- POSTCONDITIONS: —
- INVARIANTS: —
- DEPENDENCIES: REQ-BUDGET-021
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: deadline conformance tests (finite and infinite)
- EVIDENCE-STATUS: SPECIFIED

### REQ-BUDGET-005
- REQ-ID: REQ-BUDGET-005
- CATEGORY: budget
- SOURCE: Red-on-Rust.md L8683–8700([16]); spec/01 S-11 R-BUDGET-01
- NORMATIVE-LEVEL: MUST
- STATEMENT: Consumables are strictly decreasing and never returned.
- PRECONDITIONS: any transition
- POSTCONDITIONS: `C` never increases
- INVARIANTS: `C_n + Σ cost_cons(c_i) = C_0`
- DEPENDENCIES: REQ-BUDGET-019
- SECURITY-IMPACT: high (a refund of consumables would allow unbounded execution)
- VERIFICATION-METHOD: `BUDGET-CONSUMPTION-CONSERVATION`; mutation M007
- EVIDENCE-STATUS: SPECIFIED

### REQ-BUDGET-006
- REQ-ID: REQ-BUDGET-006
- CATEGORY: budget
- SOURCE: Red-on-Rust.md L8683–8700([16]); spec/01 S-11 R-BUDGET-01
- NORMATIVE-LEVEL: MUST
- STATEMENT: Reserved capacities are held for a scope then released.
- PRECONDITIONS: a reservation is taken
- POSTCONDITIONS: it is released when the scope ends
- INVARIANTS: `R_n + Σ release_i = R_0 + Σ reserve_i`
- DEPENDENCIES: REQ-BUDGET-009, REQ-BUDGET-010, REQ-BUDGET-020
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: reservation property tests
- EVIDENCE-STATUS: SPECIFIED

### REQ-BUDGET-007
- REQ-ID: REQ-BUDGET-007
- CATEGORY: budget
- SOURCE: Red-on-Rust.md L8698–8700([16]); spec/01 S-11 R-BUDGET-01
- NORMATIVE-LEVEL: MUST
- STATEMENT: The deadline is checked against logical time, not wall-clock.
- PRECONDITIONS: any transition with a deadline
- POSTCONDITIONS: comparison uses `t`
- INVARIANTS: —
- DEPENDENCIES: REQ-CAP-021, REQ-BUDGET-021
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: determinism differential; code review
- EVIDENCE-STATUS: SPECIFIED

### REQ-BUDGET-008
- REQ-ID: REQ-BUDGET-008
- CATEGORY: budget
- SOURCE: Red-on-Rust.md L8834([16] v0.3 resolution 4); L8683–8690([16]) — **(v0.3 rules)**; spec/09 U-01
- NORMATIVE-LEVEL: AMBIGUOUS
- STATEMENT: The v0.3 resolution states "`D` is part of `C`. Host/scheduler transitions consume `ΔD`, giving it operational meaning", but no frozen text fixes the `ΔD` values or `D`'s interaction with `t`/`W`. `U-01` records `D` as never given an operational meaning; the two readings differ.
- PRECONDITIONS: a host or scheduler transition
- POSTCONDITIONS: `D` decreases by `ΔD` (magnitude unspecified)
- INVARIANTS: —
- DEPENDENCIES: U-01, U-07, AMB-01
- SECURITY-IMPACT: high (implementations could legitimately differ in every budgeting decision)
- VERIFICATION-METHOD: UNDEFINED until `ΔD` is frozen (req/04, VU-02)
- EVIDENCE-STATUS: SPECIFIED

### REQ-BUDGET-009
- REQ-ID: REQ-BUDGET-009
- CATEGORY: budget
- SOURCE: Red-on-Rust.md L7525([15] correction); L8686–8690([16] v0.3 adopts); spec/01 S-11 R-BUDGET-03
- NORMATIVE-LEVEL: MUST
- STATEMENT: `ReserveOK(r, R, R_max) ⇔ R + r ≤ R_max`.
- PRECONDITIONS: a reservation of `r` is requested
- POSTCONDITIONS: reservation allowed iff the predicate holds
- INVARIANTS: `ReserveOK(r,R,R_max) ⇔ R + r ≤ R_max`
- DEPENDENCIES: REQ-BUDGET-011; supersedes the pre-fix `BudgetOK` direction error (C-07)
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: reservation property tests
- EVIDENCE-STATUS: SPECIFIED

### REQ-BUDGET-010
- REQ-ID: REQ-BUDGET-010
- CATEGORY: budget
- SOURCE: Red-on-Rust.md L7525–7535([15]); L8686–8690([16]); spec/01 S-11 R-BUDGET-03
- NORMATIVE-LEVEL: MUST
- STATEMENT: `ReleaseOK(r, R) ⇔ r ≤ R`.
- PRECONDITIONS: a release of `r` is requested
- POSTCONDITIONS: release allowed iff the predicate holds; underflow is impossible
- INVARIANTS: `ReleaseOK(r,R) ⇔ r ≤ R`
- DEPENDENCIES: REQ-BUDGET-011, REQ-BUDGET-015
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: reservation property tests; mutation M009-class
- EVIDENCE-STATUS: SPECIFIED

### REQ-BUDGET-011
- REQ-ID: REQ-BUDGET-011
- CATEGORY: budget
- SOURCE: Red-on-Rust.md L7525–7540([15]); L8686–8696([16]); spec/01 S-11 R-BUDGET-03
- NORMATIVE-LEVEL: MUST
- STATEMENT: Reservation updates are `R' = R + r` (reserve) and `R' = R − r` (release).
- PRECONDITIONS: the corresponding predicate holds
- POSTCONDITIONS: `R` updated exactly
- INVARIANTS: `R_n + Σ release_i = R_0 + Σ reserve_i`
- DEPENDENCIES: REQ-BUDGET-020
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: reservation property tests
- EVIDENCE-STATUS: SPECIFIED

### REQ-BUDGET-012
- REQ-ID: REQ-BUDGET-012
- CATEGORY: budget
- SOURCE: Red-on-Rust.md L38002–38004([54] §7); L9211–9245([17]); L10213([18]); spec/01 S-11 R-BUDGET-02
- NORMATIVE-LEVEL: MUST
- STATEMENT: Budget operations MUST use checked arithmetic and expose failure.
- PRECONDITIONS: any budget arithmetic
- POSTCONDITIONS: overflow/underflow surfaces as an explicit error
- INVARIANTS: —
- DEPENDENCIES: REQ-BUDGET-013, REQ-BUDGET-015
- SECURITY-IMPACT: high ; AMB-19
- VERIFICATION-METHOD: mutation M009 (permit negative resources); boundary-value tests
- EVIDENCE-STATUS: SPECIFIED

### REQ-BUDGET-013
- REQ-ID: REQ-BUDGET-013
- CATEGORY: budget
- SOURCE: Red-on-Rust.md L38002([54] §7); L38864([54] §28); L9219([17] "not saturating"); L41572([60] restated [60]); spec/01 S-11 R-BUDGET-02
- NORMATIVE-LEVEL: MUST NOT
- STATEMENT: `saturating_sub` MUST NOT be used for semantic accounting; saturating budget arithmetic is a prohibited shortcut.
- PRECONDITIONS: any budget subtraction
- POSTCONDITIONS: exhaustion faults instead of clamping to zero
- INVARIANTS: —
- DEPENDENCIES: REQ-CLAIM-007
- SECURITY-IMPACT: high (silent clamping hides exhaustion and breaks conservation)
- VERIFICATION-METHOD: code review; mutation M009
- EVIDENCE-STATUS: SPECIFIED

### REQ-BUDGET-014
- REQ-ID: REQ-BUDGET-014
- CATEGORY: budget
- SOURCE: Red-on-Rust.md L8692–8696([16]); L7428–7440([13]); L8833([16] resolution 2); spec/01 S-11 R-BUDGET-04
- NORMATIVE-LEVEL: MUST
- STATEMENT: `WithinBudget(E, C, R, R_A) ⇔ cost_C(E) ≤ C ∧ ReserveOK(cost_R(E), R, R_max) ∧ cost(E) ≤ R_A` — the effect cost must be within both the runtime budget and the capability ceiling.
- PRECONDITIONS: an effect is being gated
- POSTCONDITIONS: all three conjuncts checked
- INVARIANTS: the 3-conjunct definition (kept whole per rule 6)
- DEPENDENCIES: REQ-CAP-011, REQ-BUDGET-009
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: Track C short-circuit; mutation M007
- EVIDENCE-STATUS: SPECIFIED

### REQ-BUDGET-015
- REQ-ID: REQ-BUDGET-015
- CATEGORY: budget
- SOURCE: Red-on-Rust.md L9233–9245([17]); L10246([18]); spec/01 S-11 R-BUDGET-02
- NORMATIVE-LEVEL: MUST
- STATEMENT: Budget failures are exposed as `BudgetError { ConsumableExhausted, ReservedCapacityExceeded, ReservedCapacityUnderflow, DeadlineExceeded }`.
- PRECONDITIONS: a budget operation fails
- POSTCONDITIONS: one of these variants is returned
- INVARIANTS: — (closed set)
- DEPENDENCIES: REQ-BUDGET-012
- SECURITY-IMPACT: medium
- VERIFICATION-METHOD: negative budget tests per variant
- EVIDENCE-STATUS: SPECIFIED

### REQ-BUDGET-016
- REQ-ID: REQ-BUDGET-016
- CATEGORY: budget
- SOURCE: Red-on-Rust.md L10166–10171([18]); L9155–9205([17]); spec/01 S-11 R-BUDGET-07
- NORMATIVE-LEVEL: MUST
- STATEMENT: A `CostModel` maps operations to `Cost { consumable: Consumable, reserved: Reserved }`.
- PRECONDITIONS: any operation is costed
- POSTCONDITIONS: both components are produced
- INVARIANTS: —
- DEPENDENCIES: REQ-BUDGET-018
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: cost-model conformance tests
- EVIDENCE-STATUS: SPECIFIED

### REQ-BUDGET-017
- REQ-ID: REQ-BUDGET-017
- CATEGORY: budget
- SOURCE: Red-on-Rust.md L9155–9205([17]); L10171–10177([18]); spec/01 S-11 R-BUDGET-07
- NORMATIVE-LEVEL: MUST
- STATEMENT: The operation→cost mapping is a configurable semantic contract, not hardcoded per-dimension anonymous tuples.
- PRECONDITIONS: cost model implementation
- POSTCONDITIONS: costs are supplied through the contract
- INVARIANTS: —
- DEPENDENCIES: REQ-BUDGET-016
- SECURITY-IMPACT: medium
- VERIFICATION-METHOD: API review
- EVIDENCE-STATUS: SPECIFIED

### REQ-BUDGET-018
- REQ-ID: REQ-BUDGET-018
- CATEGORY: budget
- SOURCE: Red-on-Rust.md L10171–10177([18]); spec/01 S-11 R-BUDGET-07
- NORMATIVE-LEVEL: MUST
- STATEMENT: `Consumable ≠ Reserved` at the type level.
- PRECONDITIONS: —
- POSTCONDITIONS: the two are not interchangeable in code
- INVARIANTS: —
- DEPENDENCIES: REQ-BUDGET-002, REQ-BUDGET-003
- SECURITY-IMPACT: high (mixing them would let a consumable pay for a reservation)
- VERIFICATION-METHOD: type review
- EVIDENCE-STATUS: SPECIFIED

### REQ-BUDGET-019
- REQ-ID: REQ-BUDGET-019
- CATEGORY: security-invariant
- SOURCE: Red-on-Rust.md L7408–7425([13]); L28203–28240([35]); L38006–38010([54] §7); spec/01 S-11 R-BUDGET-05
- NORMATIVE-LEVEL: MUST
- STATEMENT: Consumables conservation: `C_n + Σ cost_cons(c_i) = C_0` (strictly depleted; never returned).
- PRECONDITIONS: any sequence of transitions
- POSTCONDITIONS: the equality holds after every step
- INVARIANTS: `C_n + Σ cost_cons(c_i) = C_0`
- DEPENDENCIES: REQ-BUDGET-005, REQ-CORE-005
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: `BUDGET-CONSUMPTION-CONSERVATION`; mutation M007
- EVIDENCE-STATUS: SPECIFIED

### REQ-BUDGET-020
- REQ-ID: REQ-BUDGET-020
- CATEGORY: security-invariant
- SOURCE: Red-on-Rust.md L7408–7425([13]); L38012–38016([54] §7); spec/01 S-11 R-BUDGET-05
- NORMATIVE-LEVEL: MUST
- STATEMENT: Reserved conservation: `R_n + Σ release_i = R_0 + Σ reserve_i`.
- PRECONDITIONS: any sequence of reserve/release operations
- POSTCONDITIONS: the equality holds
- INVARIANTS: `R_n + Σ release_i = R_0 + Σ reserve_i`
- DEPENDENCIES: REQ-BUDGET-011
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: reservation property tests; conservation tests
- EVIDENCE-STATUS: SPECIFIED

### REQ-BUDGET-021
- REQ-ID: REQ-BUDGET-021
- CATEGORY: security-invariant
- SOURCE: Red-on-Rust.md L7408–7425([13]); L8707–8711([16]); L8832([16] resolution 3); spec/01 S-11 R-BUDGET-05
- NORMATIVE-LEVEL: MUST
- STATEMENT: Deadline conservation: `∀ active steps i: t_i ≤ W`.
- PRECONDITIONS: any active transition
- POSTCONDITIONS: logical time never exceeds the deadline
- INVARIANTS: `∀ active steps i: t_i ≤ W`
- DEPENDENCIES: REQ-BUDGET-029
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: deadline exhaustion tests
- EVIDENCE-STATUS: SPECIFIED

### REQ-BUDGET-022
- REQ-ID: REQ-BUDGET-022
- CATEGORY: security-invariant
- SOURCE: Red-on-Rust.md L28203–28240([35]); L38006–38010([54] §7); L35210–35215([47]); spec/01 S-11 R-BUDGET-05
- NORMATIVE-LEVEL: MUST
- STATEMENT: Global partition conservation: `C_available + C_escrowed + C_consumed = C_initial`.
- PRECONDITIONS: any budget state
- POSTCONDITIONS: the three-way sum is invariant
- INVARIANTS: `C_available + C_escrowed + C_consumed = C_initial`
- DEPENDENCIES: REQ-CORE-005, REQ-BUDGET-023…REQ-BUDGET-025, REQ-RECOV-013
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: `BUDGET-CONSUMPTION-CONSERVATION`; teleportation test
- EVIDENCE-STATUS: SPECIFIED

### REQ-BUDGET-023
- REQ-ID: REQ-BUDGET-023
- CATEGORY: budget
- SOURCE: Red-on-Rust.md L28203–28240([35]); L25931–25945([32]); spec/01 S-11 R-BUDGET-05
- NORMATIVE-LEVEL: MUST
- STATEMENT: Spawn moves parent `available` → child `available` (ownership transfer, not consumption).
- PRECONDITIONS: `Spawn` executes
- POSTCONDITIONS: the same amount leaves the parent partition and enters the child partition
- INVARIANTS: `C_available + C_escrowed + C_consumed = C_initial`
- DEPENDENCIES: REQ-CORE-006, REQ-ACTOR-017
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: teleportation test over the actor tree
- EVIDENCE-STATUS: SPECIFIED

### REQ-BUDGET-024
- REQ-ID: REQ-BUDGET-024
- CATEGORY: budget
- SOURCE: Red-on-Rust.md L28203–28240([35]); L25808–25825([32]); spec/01 S-11 R-BUDGET-05
- NORMATIVE-LEVEL: MUST
- STATEMENT: Effect issuance moves the `issue` cost → `consumed` and `complete_max` → `escrowed`.
- PRECONDITIONS: an effect is durably issued
- POSTCONDITIONS: both transfers occur atomically with issuance
- INVARIANTS: `C_available + C_escrowed + C_consumed = C_initial`
- DEPENDENCIES: REQ-EFFECT-024, REQ-DUR-013
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: `BUDGET-ESCROW-CONSERVATION`
- EVIDENCE-STATUS: SPECIFIED

### REQ-BUDGET-025
- REQ-ID: REQ-BUDGET-025
- CATEGORY: budget
- SOURCE: Red-on-Rust.md L28203–28240([35]); L25799–25825([32]); spec/01 S-11 R-BUDGET-05
- NORMATIVE-LEVEL: MUST
- STATEMENT: Completion moves the actual cost → `consumed` and refunds the remainder of the escrow → `available`.
- PRECONDITIONS: a valid receipt is processed
- POSTCONDITIONS: `consumed` increases by the actual cost; `available` increases by `complete_max − actual`
- INVARIANTS: `C_available + C_escrowed + C_consumed = C_initial`
- DEPENDENCIES: REQ-EFFECT-032, REQ-EFFECT-026
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: completion accounting conservation tests
- EVIDENCE-STATUS: SPECIFIED

### REQ-BUDGET-026
- REQ-ID: REQ-BUDGET-026
- CATEGORY: budget
- SOURCE: Red-on-Rust.md L8698–8700([16]); L10164–10168([18]); L8832([16] resolution 3); spec/01 S-11 R-BUDGET-06
- NORMATIVE-LEVEL: MUST
- STATEMENT: Every transition has a logical-time delta `δ_t(c) ∈ ℕ`.
- PRECONDITIONS: any transition
- POSTCONDITIONS: a delta is defined for it
- INVARIANTS: —
- DEPENDENCIES: REQ-BUDGET-027, REQ-BUDGET-028, REQ-BUDGET-029; U-07
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: per-transition delta table review
- EVIDENCE-STATUS: SPECIFIED

### REQ-BUDGET-027
- REQ-ID: REQ-BUDGET-027
- CATEGORY: budget
- SOURCE: Red-on-Rust.md L8698–8700([16]); L8706([16] E-Let `δ_t = 0`); spec/01 S-11 R-BUDGET-06
- NORMATIVE-LEVEL: MUST
- STATEMENT: Pure computation has `δ_t = 0`.
- PRECONDITIONS: a pure transition
- POSTCONDITIONS: logical time does not advance
- INVARIANTS: `δ_t(pure) = 0`
- DEPENDENCIES: REQ-BUDGET-026
- SECURITY-IMPACT: medium
- VERIFICATION-METHOD: logical-time trace comparison in the differential
- EVIDENCE-STATUS: SPECIFIED

### REQ-BUDGET-028
- REQ-ID: REQ-BUDGET-028
- CATEGORY: budget
- SOURCE: Red-on-Rust.md L8698–8700([16]); spec/01 S-11 R-BUDGET-06
- NORMATIVE-LEVEL: MUST
- STATEMENT: Host interactions and scheduler steps have `δ_t > 0`.
- PRECONDITIONS: a host or scheduler transition
- POSTCONDITIONS: logical time strictly advances
- INVARIANTS: `δ_t(host/scheduler) > 0`
- DEPENDENCIES: REQ-BUDGET-026; U-07
- SECURITY-IMPACT: medium
- VERIFICATION-METHOD: logical-time trace comparison
- EVIDENCE-STATUS: SPECIFIED

### REQ-BUDGET-029
- REQ-ID: REQ-BUDGET-029
- CATEGORY: security-invariant
- SOURCE: Red-on-Rust.md L8698–8700([16]); L8707([16] E-Let premise); L8832([16] resolution 3); spec/01 S-11 R-BUDGET-06
- NORMATIVE-LEVEL: MUST
- STATEMENT: A transition is valid only if `t + δ_t(c) ≤ W`.
- PRECONDITIONS: any transition
- POSTCONDITIONS: an invalid transition does not occur
- INVARIANTS: `t + δ_t(c) ≤ W`
- DEPENDENCIES: REQ-BUDGET-021, REQ-BUDGET-026
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: deadline boundary tests
- EVIDENCE-STATUS: SPECIFIED

### REQ-BUDGET-030
- REQ-ID: REQ-BUDGET-030
- CATEGORY: budget
- SOURCE: Red-on-Rust.md L7345–7352([13]); L7410–7419([13]); L7753–7760([15] self-retraction of `⟨0,0,0⟩`); spec/01 S-11 R-BUDGET-08; spec/06 C-28
- NORMATIVE-LEVEL: MUST
- STATEMENT: If `¬BudgetOK` (any gate fails), the transition is replaced by `fault(BudgetExhausted)`.
- PRECONDITIONS: a budget gate fails
- POSTCONDITIONS: the actor faults; the intended transition does not occur
- INVARIANTS: —
- DEPENDENCIES: REQ-BUDGET-031, REQ-CALC-013
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: Track C budget-gate test; mutation M007
- EVIDENCE-STATUS: SPECIFIED

### REQ-BUDGET-031
- REQ-ID: REQ-BUDGET-031
- CATEGORY: budget
- SOURCE: Red-on-Rust.md L7410–7419([13]); L8756([16] E-RequestDenied note); spec/01 S-11 R-BUDGET-08
- NORMATIVE-LEVEL: MUST NOT
- STATEMENT: No partial debit occurs on a budget fault.
- PRECONDITIONS: a budget gate fails
- POSTCONDITIONS: budget state is unchanged by the failed attempt
- INVARIANTS: —
- DEPENDENCIES: REQ-BUDGET-032, REQ-EFFECT-021
- SECURITY-IMPACT: high (partial debits break conservation)
- VERIFICATION-METHOD: gate short-circuit assertion "budget unchanged"
- EVIDENCE-STATUS: SPECIFIED

### REQ-BUDGET-032
- REQ-ID: REQ-BUDGET-032
- CATEGORY: budget
- SOURCE: Red-on-Rust.md L8756([16] E-RequestDenied); L8835([16] resolution 5) — **(v0.3 rules)**; L7351–7352([13] `⟨0,0,0⟩` draft), L7753–7760([15] self-retraction); spec/06 C-28
- NORMATIVE-LEVEL: MUST
- STATEMENT: Fault transitions preserve `C` and `R`; no consumption occurs on failure.
- PRECONDITIONS: any fault transition
- POSTCONDITIONS: consumables and reservations are unchanged
- INVARIANTS: `C_available + C_escrowed + C_consumed = C_initial`
- DEPENDENCIES: REQ-BUDGET-031
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: conservation assertion across fault-injection tests
- EVIDENCE-STATUS: SPECIFIED

---

## S-12 Effect model and request sequence

### REQ-EFFECT-001
- REQ-ID: REQ-EFFECT-001
- CATEGORY: effect-protocol
- SOURCE: Red-on-Rust.md L12177–12194([21]); L9652([17]); L10509–10512([18]); spec/01 S-12 R-EFFECT-01
- NORMATIVE-LEVEL: MUST
- STATEMENT: `Expr::Request` means: construct Effect → authorize → account → log → Pending → yield `EffectRequest`.
- PRECONDITIONS: a `Request` term is evaluated
- POSTCONDITIONS: the six stages occur in this order
- INVARIANTS: — (ordered chain)
- DEPENDENCIES: REQ-EFFECT-005
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: gate short-circuit matrix
- EVIDENCE-STATUS: SPECIFIED

### REQ-EFFECT-002
- REQ-ID: REQ-EFFECT-002
- CATEGORY: effect-protocol
- SOURCE: Red-on-Rust.md L12177–12194([21]); L12132–12142([21]); L9652([17]); spec/01 S-12 R-EFFECT-01
- NORMATIVE-LEVEL: MUST NOT
- STATEMENT: `Expr::Request` does not mean execute the effect in the AST or evaluator.
- PRECONDITIONS: a `Request` term is evaluated
- POSTCONDITIONS: the evaluator never performs the external operation
- INVARIANTS: —
- DEPENDENCIES: REQ-CALC-004, REQ-DUR-001
- SECURITY-IMPACT: critical ; AMB-16, AMB-20
- VERIFICATION-METHOD: `PanicHost` harness; code review
- EVIDENCE-STATUS: SPECIFIED

### REQ-EFFECT-003
- REQ-ID: REQ-EFFECT-003
- CATEGORY: effect-protocol
- SOURCE: Red-on-Rust.md L7145–7155([13]); L8700–8710([16]); spec/01 S-12 R-EFFECT-02
- NORMATIVE-LEVEL: MUST
- STATEMENT: Every active transition takes the canonical gated form `Pre(c, Σ) ∧ BudgetOK(c, Σ) ∧ AuthOK(c, Σ) ⊢ Σ →_c Σ'`.
- PRECONDITIONS: any active transition
- POSTCONDITIONS: all applicable gates are evaluated before the state change
- INVARIANTS: gated transition shape
- DEPENDENCIES: REQ-EFFECT-004, REQ-BUDGET-014, REQ-CAP-010
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: gate short-circuit matrix
- EVIDENCE-STATUS: SPECIFIED

### REQ-EFFECT-004
- REQ-ID: REQ-EFFECT-004
- CATEGORY: effect-protocol
- SOURCE: Red-on-Rust.md L7145–7155([13]); spec/01 S-12 R-EFFECT-02
- NORMATIVE-LEVEL: MUST
- STATEMENT: `AuthOK` applies only to authority-requiring transitions.
- PRECONDITIONS: a transition that requires no authority
- POSTCONDITIONS: no authorization check is performed or required
- INVARIANTS: —
- DEPENDENCIES: REQ-EFFECT-003
- SECURITY-IMPACT: medium
- VERIFICATION-METHOD: pure-transition conformance tests
- EVIDENCE-STATUS: SPECIFIED

### REQ-EFFECT-005
- REQ-ID: REQ-EFFECT-005
- CATEGORY: effect-protocol
- SOURCE: Red-on-Rust.md L38024–38045([54] §8); L23857–23948([30] 14-gate form, superseded numbering); L11053–11090([18] 14-step form, superseded numbering); L21542([29] §22 region); L22472–22480([29] gate-order rationale); spec/01 S-12 R-EFFECT-03; see C-01
- NORMATIVE-LEVEL: MUST
- STATEMENT: The evaluator MUST follow the 16-step request sequence exactly (1 evaluate capability; 2 evaluate target; 3 evaluate arguments left-to-right; 4 construct canonical Effect; 5 validate capability; 6 authorize exact effect; 7 capability ceiling; 8 runtime budget; 9 runtime reservation; 10 deadline; 11 host policy; 12 allocate EffectId; 13 commit issue budget/reservation; 14 durable issuance; 15 Pending; 16 host invocation). Any deviation is a bug. The sequence is immutable.
- PRECONDITIONS: a `Request` reaches finalization
- POSTCONDITIONS: the steps occur in this order with none skipped or reordered
- INVARIANTS: — (ordered sequence; kept whole per rule 6)
- DEPENDENCIES: REQ-EFFECT-006…REQ-EFFECT-018
- SECURITY-IMPACT: critical (reordering, e.g. allocating an `EffectId` before authorization, is mutation M010)
- VERIFICATION-METHOD: gate short-circuit matrix; mutation M010
- EVIDENCE-STATUS: SPECIFIED

### REQ-EFFECT-006
- REQ-ID: REQ-EFFECT-006
- CATEGORY: effect-protocol
- SOURCE: Red-on-Rust.md L38032([54] §8 step 4); L23726–23745([30]); spec/01 S-12 R-EFFECT-03
- NORMATIVE-LEVEL: MUST
- STATEMENT: Step 4 constructs the canonical `Effect` together with its `EffectDigest`.
- PRECONDITIONS: capability, target, and arguments evaluated
- POSTCONDITIONS: an immutable `Effect` and its digest exist before any gate runs
- INVARIANTS: `EffectDigest = SHA-256(canonical_bytes(effect))`
- DEPENDENCIES: REQ-CALC-008
- SECURITY-IMPACT: critical (the digest is the causal identity for the journal and replay)
- VERIFICATION-METHOD: `EFFECT-RECEIPT-DIGEST-VALIDATION`
- EVIDENCE-STATUS: SPECIFIED

### REQ-EFFECT-007
- REQ-ID: REQ-EFFECT-007
- CATEGORY: effect-protocol
- SOURCE: Red-on-Rust.md L38033([54] §8 step 5); L6434–6445([11]); spec/01 S-12 R-EFFECT-03
- NORMATIVE-LEVEL: MUST
- STATEMENT: Step 5 validates the capability (lineage liveness).
- PRECONDITIONS: the effect is constructed
- POSTCONDITIONS: `Valid(c,t)` is established before authorization
- INVARIANTS: `Valid(c, t) ⇔ Live(c) ∧ t ∈ Lifetime(c) ∧ ∀a ∈ Ancestors(c). Live(a)`
- DEPENDENCIES: REQ-CAP-013
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: `CAP-REVOCATION-ANCESTOR`; mutation M004
- EVIDENCE-STATUS: SPECIFIED

### REQ-EFFECT-008
- REQ-ID: REQ-EFFECT-008
- CATEGORY: effect-protocol
- SOURCE: Red-on-Rust.md L38034([54] §8 step 6); L6406–6421([11]); L37937–37948([54] §6); spec/01 S-12 R-EFFECT-03
- NORMATIVE-LEVEL: MUST
- STATEMENT: Step 6 authorizes the exact effect via `kernel.authorize` with `LogicalTime`.
- PRECONDITIONS: capability validated
- POSTCONDITIONS: `Authorized(A,E,t)` established for this exact effect
- INVARIANTS: the 5-conjunct authorization predicate
- DEPENDENCIES: REQ-CAP-010, REQ-KERN-004
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: Track B mock-kernel exactly-one-call; mutation M005
- EVIDENCE-STATUS: SPECIFIED

### REQ-EFFECT-009
- REQ-ID: REQ-EFFECT-009
- CATEGORY: effect-protocol
- SOURCE: Red-on-Rust.md L38035([54] §8 step 7); L8692–8696([16]); spec/01 S-12 R-EFFECT-03
- NORMATIVE-LEVEL: MUST
- STATEMENT: Step 7 performs the capability resource ceiling check.
- PRECONDITIONS: effect authorized
- POSTCONDITIONS: `cost(E) ≤ R_A` established
- INVARIANTS: —
- DEPENDENCIES: REQ-BUDGET-014, REQ-CAP-011
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: mutation M005 (omit capability ceiling)
- EVIDENCE-STATUS: SPECIFIED

### REQ-EFFECT-010
- REQ-ID: REQ-EFFECT-010
- CATEGORY: effect-protocol
- SOURCE: Red-on-Rust.md L38036([54] §8 step 8); L25799–25825([32]); spec/01 S-12 R-EFFECT-03
- NORMATIVE-LEVEL: MUST
- STATEMENT: Step 8 performs the runtime consumable budget check `can_consume(issue + complete_max)`.
- PRECONDITIONS: ceiling check passed
- POSTCONDITIONS: the actor can afford issuance plus the maximum completion cost
- INVARIANTS: —
- DEPENDENCIES: REQ-EFFECT-024, REQ-EFFECT-026
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: `BUDGET-ESCROW-CONSERVATION`; mutation M007
- EVIDENCE-STATUS: SPECIFIED

### REQ-EFFECT-011
- REQ-ID: REQ-EFFECT-011
- CATEGORY: effect-protocol
- SOURCE: Red-on-Rust.md L38037([54] §8 step 9); L8686–8690([16]); L9256–9262([17]); spec/01 S-12 R-EFFECT-03
- NORMATIVE-LEVEL: MUST
- STATEMENT: Step 9 performs the runtime reservation capacity check (`can_reserve`).
- PRECONDITIONS: consumable check passed
- POSTCONDITIONS: `ReserveOK(cost_R(E), R, R_max)` established
- INVARIANTS: `ReserveOK(r,R,R_max) ⇔ R + r ≤ R_max`
- DEPENDENCIES: REQ-BUDGET-009
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: reservation gate tests
- EVIDENCE-STATUS: SPECIFIED

### REQ-EFFECT-012
- REQ-ID: REQ-EFFECT-012
- CATEGORY: effect-protocol
- SOURCE: Red-on-Rust.md L38038([54] §8 step 10); spec/01 S-12 R-EFFECT-03
- NORMATIVE-LEVEL: MUST
- STATEMENT: Step 10 performs the deadline check (`logical_time ≤ deadline`).
- PRECONDITIONS: reservation check passed
- POSTCONDITIONS: the deadline is not exceeded at issuance
- INVARIANTS: `t ≤ W`
- DEPENDENCIES: REQ-BUDGET-021
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: deadline gate test
- EVIDENCE-STATUS: SPECIFIED

### REQ-EFFECT-013
- REQ-ID: REQ-EFFECT-013
- CATEGORY: effect-protocol
- SOURCE: Red-on-Rust.md L38039([54] §8 step 11); L11069([18] "spec allows early fail"); L8560–8580([15]); spec/01 S-12 R-EFFECT-03; see C-27
- NORMATIVE-LEVEL: MUST
- STATEMENT: Step 11 performs the host policy check as a fail-early gate inside the machine; the host re-checks authoritatively.
- PRECONDITIONS: deadline check passed
- POSTCONDITIONS: `HostPolicyOK(E)` established or the request is denied
- INVARIANTS: —
- DEPENDENCIES: REQ-HOST-003
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: host policy gate tests; defense-in-depth review
- EVIDENCE-STATUS: SPECIFIED

### REQ-EFFECT-014
- REQ-ID: REQ-EFFECT-014
- CATEGORY: effect-protocol
- SOURCE: Red-on-Rust.md L38040([54] §8 step 12); L8733–8734([16] E-Request `h = N_h, N_h' = N_h + 1`); spec/01 S-12 R-EFFECT-03
- NORMATIVE-LEVEL: MUST
- STATEMENT: Step 12 allocates a deterministic `EffectId` from the global monotonic counter, after all gates have passed.
- PRECONDITIONS: gates 1–11 passed
- POSTCONDITIONS: `next_effect_id` increments exactly once
- INVARIANTS: `h = N_h`, `N_h' = N_h + 1`
- DEPENDENCIES: REQ-ACTOR-009, REQ-EFFECT-020
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: mutation M010 (allocate `EffectId` before authorization)
- EVIDENCE-STATUS: SPECIFIED

### REQ-EFFECT-015
- REQ-ID: REQ-EFFECT-015
- CATEGORY: effect-protocol
- SOURCE: Red-on-Rust.md L38041([54] §8 step 13); spec/01 S-12 R-EFFECT-03
- NORMATIVE-LEVEL: MUST
- STATEMENT: Step 13 commits the issue budget and reservation transactionally; the commit cannot fail after gate 8.
- PRECONDITIONS: gate 8 succeeded
- POSTCONDITIONS: the debit and reservation are applied atomically
- INVARIANTS: —
- DEPENDENCIES: REQ-EFFECT-024, REQ-BUDGET-031
- SECURITY-IMPACT: high (a fallible commit after the gate would break the completion guarantee)
- VERIFICATION-METHOD: issuance accounting tests; fault injection at commit
- EVIDENCE-STATUS: SPECIFIED

### REQ-EFFECT-016
- REQ-ID: REQ-EFFECT-016
- CATEGORY: effect-protocol
- SOURCE: Red-on-Rust.md L38043([54] §8 step 15); L8743 ([16]) ([16] E-Request `status ← Pending(h, E, K)`); L10500–10510([18]); spec/01 S-12 R-EFFECT-03
- NORMATIVE-LEVEL: MUST
- STATEMENT: Step 15 puts the actor into `Pending`. This is the only path to `ActorStatus::Pending`.
- PRECONDITIONS: durable issuance completed
- POSTCONDITIONS: actor status is `Pending(h, E, K)`
- INVARIANTS: —
- DEPENDENCIES: REQ-DUR-002, REQ-ACTOR-011
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: status-transition conformance tests; `SCHED-BLOCKED-NOT-SCHEDULED`
- EVIDENCE-STATUS: SPECIFIED

### REQ-EFFECT-017
- REQ-ID: REQ-EFFECT-017
- CATEGORY: effect-protocol
- SOURCE: Red-on-Rust.md L38044([54] §8 step 16); L10509–10512([18]); spec/01 S-12 R-EFFECT-03
- NORMATIVE-LEVEL: MUST
- STATEMENT: Step 16 invokes the host by yielding `EffectRequest` to the host adapter, and is the last step.
- PRECONDITIONS: durable issuance completed and actor `Pending`
- POSTCONDITIONS: the host adapter receives the request
- INVARIANTS: `HostInvoked(E) ⇒ DurableIssued(E)`
- DEPENDENCIES: REQ-DUR-001
- SECURITY-IMPACT: critical ; AMB-16, AMB-20
- VERIFICATION-METHOD: `EFFECT-ISSUE-DURABLE-BEFORE-HOST`; `PanicHost`
- EVIDENCE-STATUS: SPECIFIED

### REQ-EFFECT-018
- REQ-ID: REQ-EFFECT-018
- CATEGORY: effect-protocol
- SOURCE: Red-on-Rust.md L38026([54] §8 preamble); L35147([47]); spec/01 S-12 R-EFFECT-03
- NORMATIVE-LEVEL: MUST NOT
- STATEMENT: No host interaction occurs before the durable issuance boundary.
- PRECONDITIONS: any point before step 14
- POSTCONDITIONS: no host call has occurred
- INVARIANTS: `HostInvoked(E) ⇒ DurableIssued(E)`
- DEPENDENCIES: REQ-DUR-001, REQ-CORE-007
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: `EFFECT-ISSUE-DURABLE-BEFORE-HOST`; crash points T0–T4
- EVIDENCE-STATUS: SPECIFIED

### REQ-EFFECT-019
- REQ-ID: REQ-EFFECT-019
- CATEGORY: effect-protocol
- SOURCE: Red-on-Rust.md L24003–24045([30] Track C); L38024–38045([54] §8); spec/01 S-12 R-EFFECT-04
- NORMATIVE-LEVEL: MUST NOT
- STATEMENT: On a denial at any gate, subsequent gates are not called.
- PRECONDITIONS: a gate denies
- POSTCONDITIONS: no later gate executes
- INVARIANTS: —
- DEPENDENCIES: REQ-EFFECT-005
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: Track C 5-assertion matrix per gate
- EVIDENCE-STATUS: SPECIFIED

### REQ-EFFECT-020
- REQ-ID: REQ-EFFECT-020
- CATEGORY: effect-protocol
- SOURCE: Red-on-Rust.md L24003–24045([30] Track C); spec/01 S-12 R-EFFECT-04
- NORMATIVE-LEVEL: MUST NOT
- STATEMENT: On a denial, `next_effect_id` is not incremented.
- PRECONDITIONS: a gate denies
- POSTCONDITIONS: the ID counter is unchanged
- INVARIANTS: —
- DEPENDENCIES: REQ-EFFECT-014
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: Track C assertion; mutation M010
- EVIDENCE-STATUS: SPECIFIED

### REQ-EFFECT-021
- REQ-ID: REQ-EFFECT-021
- CATEGORY: effect-protocol
- SOURCE: Red-on-Rust.md L24003–24045([30] Track C); L8756([16]); spec/01 S-12 R-EFFECT-04
- NORMATIVE-LEVEL: MUST NOT
- STATEMENT: On a denial, the actor budget is unchanged.
- PRECONDITIONS: a gate denies
- POSTCONDITIONS: no debit, no reservation, no escrow
- INVARIANTS: `C_available + C_escrowed + C_consumed = C_initial`
- DEPENDENCIES: REQ-BUDGET-031
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: Track C assertion
- EVIDENCE-STATUS: SPECIFIED

### REQ-EFFECT-022
- REQ-ID: REQ-EFFECT-022
- CATEGORY: effect-protocol
- SOURCE: Red-on-Rust.md L24003–24045([30] Track C); spec/01 S-12 R-EFFECT-04
- NORMATIVE-LEVEL: MUST NOT
- STATEMENT: On a denial, the event log gains no new entries.
- PRECONDITIONS: a gate denies
- POSTCONDITIONS: the log is unchanged
- INVARIANTS: log is append-only and unmodified by a denial
- DEPENDENCIES: REQ-PERSIST-006
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: Track C assertion
- EVIDENCE-STATUS: SPECIFIED

### REQ-EFFECT-023
- REQ-ID: REQ-EFFECT-023
- CATEGORY: effect-protocol
- SOURCE: Red-on-Rust.md L24003–24045([30] Track C); L38050([54] §8); spec/01 S-12 R-EFFECT-04
- NORMATIVE-LEVEL: MUST NOT
- STATEMENT: On a denial, `HostExecutor::execute` is never invoked.
- PRECONDITIONS: a gate denies
- POSTCONDITIONS: no host call
- INVARIANTS: `HostInvoked(E) ⇒ DurableIssued(E)`
- DEPENDENCIES: REQ-DUR-001, REQ-REF-014
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: `PanicHost` panics if `execute()` is called before all gates pass
- EVIDENCE-STATUS: SPECIFIED

### REQ-EFFECT-024
- REQ-ID: REQ-EFFECT-024
- CATEGORY: effect-protocol
- SOURCE: Red-on-Rust.md L25808–25825([32] correction); L38036([54] §8 step 8); spec/01 S-12 R-EFFECT-05
- NORMATIVE-LEVEL: MUST
- STATEMENT: At issuance the machine MUST guarantee the maximum possible completion cost is affordable: gate 8 checks `can_consume(issue.checked_add(complete_max))`.
- PRECONDITIONS: issuance gate 8
- POSTCONDITIONS: the check uses the checked sum of `issue` and `complete_max`
- INVARIANTS: —
- DEPENDENCIES: REQ-CALC-010, REQ-BUDGET-012
- SECURITY-IMPACT: critical (the pre-correction form under-escrowed — a real vulnerability fixed in `[31]`)
- VERIFICATION-METHOD: `BUDGET-ESCROW-CONSERVATION`; escrow tests
- EVIDENCE-STATUS: SPECIFIED

### REQ-EFFECT-025
- REQ-ID: REQ-EFFECT-025
- CATEGORY: effect-protocol
- SOURCE: Red-on-Rust.md L25808–25825([32]); spec/01 S-12 R-EFFECT-05
- NORMATIVE-LEVEL: MUST
- STATEMENT: Overflow in the affordability check yields `Fault::ArithmeticOverflow`/a budget fault, never a wrapped value.
- PRECONDITIONS: `issue + complete_max` overflows
- POSTCONDITIONS: an explicit fault is produced
- INVARIANTS: —
- DEPENDENCIES: REQ-BUDGET-012; AMB-08 (`ArithmeticOverflow` is not in the frozen `Fault` enum)
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: overflow boundary test
- EVIDENCE-STATUS: SPECIFIED

### REQ-EFFECT-026
- REQ-ID: REQ-EFFECT-026
- CATEGORY: security-invariant
- SOURCE: Red-on-Rust.md L25808–25825([32]); L38018([54] §7); spec/01 S-12 R-EFFECT-05
- NORMATIVE-LEVEL: MUST
- STATEMENT: After the affordability check the remaining budget is mathematically guaranteed ≥ `complete_max`, so completion accounting cannot fail.
- PRECONDITIONS: gate 8 passed
- POSTCONDITIONS: completion can always be charged
- INVARIANTS: `remaining ≥ complete_max`
- DEPENDENCIES: REQ-EFFECT-024, REQ-BUDGET-025
- SECURITY-IMPACT: critical (a failed completion would leave an effect `Indeterminate` by construction)
- VERIFICATION-METHOD: `BUDGET-ESCROW-CONSERVATION`
- EVIDENCE-STATUS: SPECIFIED

### REQ-EFFECT-027
- REQ-ID: REQ-EFFECT-027
- CATEGORY: effect-protocol
- SOURCE: Red-on-Rust.md L38052–38060([54] §8); L23949–24002([30]); L25952–25970([32]); L9325–9335([17]); spec/01 S-12 R-EFFECT-06
- NORMATIVE-LEVEL: MUST
- STATEMENT: A receipt MUST be validated against **both** the `EffectId` and the `EffectDigest` of the pending effect before resumption.
- PRECONDITIONS: a receipt arrives for a `Pending` actor
- POSTCONDITIONS: both fields match the pending effect before the continuation resumes
- INVARIANTS: `R.id = pending.id ∧ R.effect_digest = pending.digest`
- DEPENDENCIES: REQ-CALC-009
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: `EFFECT-RECEIPT-DIGEST-VALIDATION`; mutations M017, M018
- EVIDENCE-STATUS: SPECIFIED

### REQ-EFFECT-028
- REQ-ID: REQ-EFFECT-028
- CATEGORY: effect-protocol
- SOURCE: Red-on-Rust.md L23949–24002([30]); L25952–25970([32]); spec/01 S-12 R-EFFECT-06
- NORMATIVE-LEVEL: MUST
- STATEMENT: A receipt mismatch yields `fault(ReplayCorruption)`.
- PRECONDITIONS: `EffectId` or `EffectDigest` does not match
- POSTCONDITIONS: the actor faults with `ReplayCorruption`
- INVARIANTS: —
- DEPENDENCIES: REQ-CALC-013
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: tampered-receipt test; mutation M017
- EVIDENCE-STATUS: SPECIFIED

### REQ-EFFECT-029
- REQ-ID: REQ-EFFECT-029
- CATEGORY: effect-protocol
- SOURCE: Red-on-Rust.md L23949–24002([30]); L38070([54] §8); spec/01 S-12 R-EFFECT-06
- NORMATIVE-LEVEL: MUST NOT
- STATEMENT: On receipt mismatch the continuation is NOT resumed.
- PRECONDITIONS: mismatch detected
- POSTCONDITIONS: the continuation remains unexecuted
- INVARIANTS: —
- DEPENDENCIES: REQ-EFFECT-028
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: mutation M018 (resume after corrupted receipt)
- EVIDENCE-STATUS: SPECIFIED

### REQ-EFFECT-030
- REQ-ID: REQ-EFFECT-030
- CATEGORY: effect-protocol
- SOURCE: Red-on-Rust.md L23949–24002([30]); L25952–25970([32]); spec/01 S-12 R-EFFECT-06
- NORMATIVE-LEVEL: MUST NOT
- STATEMENT: On receipt mismatch the reservation is NOT released.
- PRECONDITIONS: mismatch detected
- POSTCONDITIONS: the reservation stays held pending adjudication
- INVARIANTS: `R_n + Σ release_i = R_0 + Σ reserve_i`
- DEPENDENCIES: REQ-EFFECT-028, REQ-BUDGET-010
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: causal replay integrity test
- EVIDENCE-STATUS: SPECIFIED

### REQ-EFFECT-031
- REQ-ID: REQ-EFFECT-031
- CATEGORY: effect-protocol
- SOURCE: Red-on-Rust.md L23775–23782([30]); L10329([18]); spec/01 S-12 R-EFFECT-06
- NORMATIVE-LEVEL: IS
- STATEMENT: `EffectReceipt { id, effect_digest, result: Result<Value, HostFault> }`.
- PRECONDITIONS: —
- POSTCONDITIONS: —
- INVARIANTS: —
- DEPENDENCIES: REQ-EFFECT-027
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: type review; receipt round-trip tests
- EVIDENCE-STATUS: SPECIFIED

### REQ-EFFECT-032
- REQ-ID: REQ-EFFECT-032
- CATEGORY: effect-protocol
- SOURCE: Red-on-Rust.md L23949–24002([30]); L25799–25825([32]); spec/01 S-12 R-EFFECT-07
- NORMATIVE-LEVEL: MUST
- STATEMENT: On a valid receipt the machine charges `complete` (≤ `complete_max`) from consumables.
- PRECONDITIONS: receipt validated
- POSTCONDITIONS: `consumed` increases by the actual cost; escrow decreases accordingly
- INVARIANTS: `C_available + C_escrowed + C_consumed = C_initial`
- DEPENDENCIES: REQ-BUDGET-025, REQ-EFFECT-026
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: completion accounting conservation tests
- EVIDENCE-STATUS: SPECIFIED

### REQ-EFFECT-033
- REQ-ID: REQ-EFFECT-033
- CATEGORY: effect-protocol
- SOURCE: Red-on-Rust.md L23949–24002([30]); spec/01 S-12 R-EFFECT-07
- NORMATIVE-LEVEL: MUST
- STATEMENT: On a valid receipt the reservation is released.
- PRECONDITIONS: receipt validated
- POSTCONDITIONS: `ReleaseOK` holds and `R` is reduced
- INVARIANTS: `R_n + Σ release_i = R_0 + Σ reserve_i`
- DEPENDENCIES: REQ-BUDGET-010, REQ-CALC-012
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: reservation conservation tests
- EVIDENCE-STATUS: SPECIFIED

### REQ-EFFECT-034
- REQ-ID: REQ-EFFECT-034
- CATEGORY: effect-protocol
- SOURCE: Red-on-Rust.md L23949–24002([30]); L35132([47]); spec/01 S-12 R-EFFECT-07
- NORMATIVE-LEVEL: MUST
- STATEMENT: On a valid receipt `EffectCompleted { id, digest, result }` is appended to the event log.
- PRECONDITIONS: receipt validated
- POSTCONDITIONS: the record is appended (and made durable per S-18)
- INVARIANTS: `Completed(E) ⇒ Issued(E)`
- DEPENDENCIES: REQ-DUR-006, REQ-PERSIST-005
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: journal validator; crash point T5
- EVIDENCE-STATUS: SPECIFIED

### REQ-EFFECT-035
- REQ-ID: REQ-EFFECT-035
- CATEGORY: effect-protocol
- SOURCE: Red-on-Rust.md L23949–24002([30]); L8761–8763([16] E-Receipt); spec/01 S-12 R-EFFECT-07
- NORMATIVE-LEVEL: MUST
- STATEMENT: On a valid receipt the continuation is resumed with the receipt's value.
- PRECONDITIONS: receipt validated
- POSTCONDITIONS: `K[result]` becomes the current term; status returns to `Running`
- INVARIANTS: —
- DEPENDENCIES: REQ-CEK-005
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: effect round-trip conformance tests
- EVIDENCE-STATUS: SPECIFIED

### REQ-EFFECT-036
- REQ-ID: REQ-EFFECT-036
- CATEGORY: effect-protocol
- SOURCE: Red-on-Rust.md L23949–24002([30]); spec/01 S-12 R-EFFECT-07
- NORMATIVE-LEVEL: AMBIGUOUS
- STATEMENT: Host faults are mapped to values/faults "by the mapping defined by the machine", but no frozen text enumerates that mapping (`HostFault` → `Fault`/`Value`).
- PRECONDITIONS: a receipt carries a host fault
- POSTCONDITIONS: — (undefined)
- INVARIANTS: —
- DEPENDENCIES: U-08, AMB-08
- SECURITY-IMPACT: high (the differential observer compares faults; an undefined mapping is not comparable)
- VERIFICATION-METHOD: UNDEFINED until the mapping is frozen (req/04, VU-08)
- EVIDENCE-STATUS: SPECIFIED

### REQ-EFFECT-037
- REQ-ID: REQ-EFFECT-037
- CATEGORY: effect-protocol
- SOURCE: Red-on-Rust.md L8726–8746([16] v0.3 E-Request success) — **(v0.3 rules)**
- NORMATIVE-LEVEL: MUST
- STATEMENT: `E-Request` succeeds only with premises `Valid(c,t)`, `Authorized(κ(c), E, t)` (Gate 1: capability), `WithinBudget(E, C, R, κ(c).R)` (Gate 2: runtime budget), `HostPolicyOK(E)` (Gate 3: host policy), `t + δ_t(req) ≤ W`, and `h = N_h`, `N_h' = N_h + 1`; the successor sets `status ← Pending(h, E, K)`, `C ← C − cost_C(req)`, `t ← t + δ_t(req)`, `N_h ← N_h'`, and appends `EffectIssued(h, Hash(E), E)` to the log.
- PRECONDITIONS: all six premises hold
- POSTCONDITIONS: as stated
- INVARIANTS: `h = N_h`, `N_h' = N_h + 1`
- DEPENDENCIES: REQ-EFFECT-005, REQ-CAP-010, REQ-BUDGET-014, REQ-HOST-001
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: gate short-circuit matrix; independent reference execution
- EVIDENCE-STATUS: SPECIFIED

### REQ-EFFECT-038
- REQ-ID: REQ-EFFECT-038
- CATEGORY: effect-protocol
- SOURCE: Red-on-Rust.md L8748–8758([16] v0.3 E-RequestDenied); L8841([16] resolution 13) — **(v0.3 rules)**
- NORMATIVE-LEVEL: MUST
- STATEMENT: `E-RequestDenied` has deterministic fault precedence: capability first, then budget, then host policy; the fault of the first failing gate (written $f_{\text{specific}}$ in the source) is `CapabilityViolation`, `BudgetExhausted`, or `HostPolicyViolation` based on the first failing gate; budget `C` is preserved and no consumption occurs on fault.
- PRECONDITIONS: at least one gate fails
- POSTCONDITIONS: the fault names the first failing gate in the order Auth → Budget → Host
- INVARIANTS: —
- DEPENDENCIES: REQ-BUDGET-032; AMB-08 (`CapabilityViolation`/`HostPolicyViolation` are not variants of the frozen `Fault` enum)
- SECURITY-IMPACT: critical (fault identity is compared by the differential oracle)
- VERIFICATION-METHOD: per-gate denial tests asserting the exact fault; differential fault comparison
- EVIDENCE-STATUS: SPECIFIED

### REQ-EFFECT-039
- REQ-ID: REQ-EFFECT-039
- CATEGORY: effect-protocol
- SOURCE: Red-on-Rust.md L8761–8763([16] v0.3 E-Receipt); L8839([16] resolution 8) — **(v0.3 rules)**
- NORMATIVE-LEVEL: MUST
- STATEMENT: `E-Receipt` requires `R.h = h ∧ R.effect_id = Hash(E)`; on success the continuation resumes with `R.result`, `cost_C(receipt)` is charged, `t` advances by `δ_t(receipt)`, and `EffectCompleted(h, R.result)` is appended.
- PRECONDITIONS: both identity checks pass
- POSTCONDITIONS: as stated
- INVARIANTS: `R.h = h ∧ R.effect_id = Hash(E)`
- DEPENDENCIES: REQ-EFFECT-027, REQ-EFFECT-032, REQ-EFFECT-034
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: `EFFECT-RECEIPT-DIGEST-VALIDATION`
- EVIDENCE-STATUS: SPECIFIED

### REQ-EFFECT-040
- REQ-ID: REQ-EFFECT-040
- CATEGORY: effect-protocol
- SOURCE: Red-on-Rust.md L8765–8766([16] v0.3 E-ReceiptMismatch) — **(v0.3 rules)**
- NORMATIVE-LEVEL: MUST
- STATEMENT: `E-ReceiptMismatch`: `R.h ≠ h ∨ R.effect_id ≠ Hash(E)` transitions the actor to `Fault(IsolationBreach)`.
- PRECONDITIONS: either identity check fails
- POSTCONDITIONS: the actor faults; no resumption
- INVARIANTS: —
- DEPENDENCIES: REQ-EFFECT-028 (the frozen taxonomy names this outcome `ReplayCorruption`; `IsolationBreach` has no counterpart — AMB-08)
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: tampered-receipt test; mutation M017
- EVIDENCE-STATUS: SPECIFIED
