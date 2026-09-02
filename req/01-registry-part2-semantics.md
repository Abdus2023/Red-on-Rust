# Atomic Requirement Registry — Part 2: Language and Machine Semantics (S-07 … S-10)

Areas: `CALC` (20), `CEK` (24), `CAP` (26), `KERN` (9) — 79 atomic units.
Records marked **(v0.3 rules)** come from the frozen v0.3 transition-rule set at `Red-on-Rust.md` L8700–8800 (turn `[16]`), which `spec/03` does not carry as separate obligations; they are extracted here because they are normative source text, not inference.

---

## S-07 Core calculus

### REQ-CALC-001
- REQ-ID: REQ-CALC-001
- CATEGORY: calculus
- SOURCE: Red-on-Rust.md L12283–12312([21]); spec/01 S-07 R-CALC-01
- NORMATIVE-LEVEL: IS
- STATEMENT: The machine value domain is `v ::= Unit | Bool(bool) | Integer(i64) | Bytes(Vec<u8>) | Symbol(Symbol) | String(String) | List(Vec<Value>) | Tuple(Vec<Value>) | Function(FunctionValue) | Capability(CapRef) | Actor(ActorId)`.
- PRECONDITIONS: —
- POSTCONDITIONS: —
- INVARIANTS: — (closed 11-variant set)
- DEPENDENCIES: REQ-CANON-009 (name collision with the 15A canonical `Value`); U-09
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: type review; exhaustive value-domain conformance
- EVIDENCE-STATUS: SPECIFIED

### REQ-CALC-002
- REQ-ID: REQ-CALC-002
- CATEGORY: security-invariant
- SOURCE: Red-on-Rust.md L12290–12312([21]); L19153–19175([27]); spec/01 S-07 R-CALC-01
- NORMATIVE-LEVEL: MUST NOT
- STATEMENT: `Value::Capability(CapRef)` does not grant the evaluator inspection rights; the evaluator may only pass the opaque reference back to the kernel.
- PRECONDITIONS: evaluator holds `Value::Capability`
- POSTCONDITIONS: no field of the authority is readable
- INVARIANTS: `CapRef ⇏ AuthorityInspection`
- DEPENDENCIES: REQ-KERN-001, REQ-TRUST-009
- SECURITY-IMPACT: critical ; AMB-21
- VERIFICATION-METHOD: visibility review; first security gate property 2
- EVIDENCE-STATUS: SPECIFIED

### REQ-CALC-003
- REQ-ID: REQ-CALC-003
- CATEGORY: calculus
- SOURCE: Red-on-Rust.md L12145–12200([21]); spec/01 S-07 R-CALC-02
- NORMATIVE-LEVEL: IS
- STATEMENT: The frozen `Expr` AST has exactly the constructors `Value | Var | Let{name,value,body} | Seq{first,second} | If{condition,then,else} | Call{function,args} | Lambda{params,body} | Attenuate{capability,constraint,body} | Request{capability,operation,target,params} | Spawn{body,budget} | Send{target,value} | Receive`.
- PRECONDITIONS: —
- POSTCONDITIONS: —
- INVARIANTS: — (closed 12-constructor set)
- DEPENDENCIES: U-04 (`await` retraction not re-declared), U-05 (isolation ladder), AMB-11 (`Expr::Delegate`)
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: AST surface review; exhaustive expression-depth baseline
- EVIDENCE-STATUS: SPECIFIED

### REQ-CALC-004
- REQ-ID: REQ-CALC-004
- CATEGORY: security-invariant
- SOURCE: Red-on-Rust.md L12132–12142([21]); spec/01 S-07 R-CALC-02
- NORMATIVE-LEVEL: MUST NOT
- STATEMENT: Host effects MUST NOT be placed directly into the AST as executable Rust callbacks; the AST contains only declarative operations.
- PRECONDITIONS: AST definition
- POSTCONDITIONS: no callable host code inside `Expr`
- INVARIANTS: —
- DEPENDENCIES: REQ-COMPILE-001, REQ-CLAIM-002
- SECURITY-IMPACT: critical (an AST callback would bypass the whole gate chain)
- VERIFICATION-METHOD: AST type review
- EVIDENCE-STATUS: SPECIFIED

### REQ-CALC-005
- REQ-ID: REQ-CALC-005
- CATEGORY: calculus
- SOURCE: Red-on-Rust.md L12250–12270([21]); L12283–12301([21]); spec/01 S-07 R-CALC-03
- NORMATIVE-LEVEL: MUST
- STATEMENT: Runtime variable identity is `Symbol(u32)`, not `String`.
- PRECONDITIONS: —
- POSTCONDITIONS: environments are keyed by `Symbol`
- INVARIANTS: —
- DEPENDENCIES: REQ-CALC-006
- SECURITY-IMPACT: medium
- VERIFICATION-METHOD: type review
- EVIDENCE-STATUS: SPECIFIED

### REQ-CALC-006
- REQ-ID: REQ-CALC-006
- CATEGORY: calculus
- SOURCE: Red-on-Rust.md L12250–12270([21]); spec/01 S-07 R-CALC-03
- NORMATIVE-LEVEL: MUST
- STATEMENT: The compiler maintains the name→`Symbol` mapping; the evaluator operates entirely on symbols.
- PRECONDITIONS: compilation and evaluation
- POSTCONDITIONS: no string-based name resolution at runtime
- INVARIANTS: —
- DEPENDENCIES: REQ-CALC-005
- SECURITY-IMPACT: medium
- VERIFICATION-METHOD: runtime API review; symbol-interning conformance test
- EVIDENCE-STATUS: SPECIFIED

### REQ-CALC-007
- REQ-ID: REQ-CALC-007
- CATEGORY: effect-protocol
- SOURCE: Red-on-Rust.md L23726–23772([30]); L9297([17] early form, superseded); spec/01 S-07 R-CALC-04
- NORMATIVE-LEVEL: IS
- STATEMENT: An effect is immutable data: `Effect { capability: CapRef, operation: Op, target: Target, params: Params, cost: EffectCost }`.
- PRECONDITIONS: —
- POSTCONDITIONS: —
- INVARIANTS: effect immutability
- DEPENDENCIES: U-21 (`Op`/`Target`/`Params` domains undefined)
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: type review; immutability review
- EVIDENCE-STATUS: SPECIFIED

### REQ-CALC-008
- REQ-ID: REQ-CALC-008
- CATEGORY: effect-protocol
- SOURCE: Red-on-Rust.md L23738–23745([30]); L10186([18]); spec/01 S-07 R-CALC-04
- NORMATIVE-LEVEL: MUST
- STATEMENT: Effect identity is canonical: `EffectDigest = SHA-256(canonical_bytes(effect))`.
- PRECONDITIONS: an effect is constructed
- POSTCONDITIONS: its digest is the SHA-256 of its canonical encoding
- INVARIANTS: `Canonical(x) = Canonical(y) ⇒ Digest(x) = Digest(y)`
- DEPENDENCIES: REQ-CANON-001, REQ-CANON-021; U-21
- SECURITY-IMPACT: critical (digest is the causal identity used by the journal)
- VERIFICATION-METHOD: `EFFECT-RECEIPT-DIGEST-VALIDATION`; digest property tests
- EVIDENCE-STATUS: SPECIFIED

### REQ-CALC-009
- REQ-ID: REQ-CALC-009
- CATEGORY: effect-protocol
- SOURCE: Red-on-Rust.md L23748–23772([30]); L38052–38060([54] §8); spec/01 S-07 R-CALC-04
- NORMATIVE-LEVEL: MUST
- STATEMENT: `EffectId` (monotonic u64 allocator counter) and `EffectDigest` (semantic identity) serve different purposes and both MUST be validated on receipt.
- PRECONDITIONS: a receipt arrives
- POSTCONDITIONS: both fields checked against the pending effect
- INVARIANTS: —
- DEPENDENCIES: REQ-EFFECT-019, REQ-EFFECT-020
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: `EFFECT-RECEIPT-DIGEST-VALIDATION`; mutations M017, M018
- EVIDENCE-STATUS: SPECIFIED

### REQ-CALC-010
- REQ-ID: REQ-CALC-010
- CATEGORY: effect-protocol
- SOURCE: Red-on-Rust.md L25808–25825([32] correction); L23726–23740([30] pre-correction, superseded); spec/01 S-07 R-CALC-05
- NORMATIVE-LEVEL: IS
- STATEMENT: `EffectCost { issue: Consumable, complete_max: Consumable, reserve: Reserved }`.
- PRECONDITIONS: —
- POSTCONDITIONS: —
- INVARIANTS: —
- DEPENDENCIES: REQ-EFFECT-016, REQ-BUDGET-001
- SECURITY-IMPACT: high ; AMB-23
- VERIFICATION-METHOD: `BUDGET-ESCROW-CONSERVATION`
- EVIDENCE-STATUS: SPECIFIED

### REQ-CALC-011
- REQ-ID: REQ-CALC-011
- CATEGORY: effect-protocol
- SOURCE: Red-on-Rust.md L25808–25825([32]); spec/01 S-07 R-CALC-05
- NORMATIVE-LEVEL: MUST
- STATEMENT: `issue` is charged at request time.
- PRECONDITIONS: request passes the budget gate
- POSTCONDITIONS: `issue` moves from `available` to `consumed`
- INVARIANTS: `C_available + C_escrowed + C_consumed = C_initial`
- DEPENDENCIES: REQ-BUDGET-021
- SECURITY-IMPACT: high ; AMB-17
- VERIFICATION-METHOD: budget conservation test at request time
- EVIDENCE-STATUS: SPECIFIED

### REQ-CALC-012
- REQ-ID: REQ-CALC-012
- CATEGORY: effect-protocol
- SOURCE: Red-on-Rust.md L25808–25825([32]); L23949–24002([30]); spec/01 S-07 R-CALC-05
- NORMATIVE-LEVEL: MUST
- STATEMENT: `reserve` is reserved at request and released at receipt.
- PRECONDITIONS: request passes the reservation gate; a valid receipt later arrives
- POSTCONDITIONS: reservation held between request and receipt, then released
- INVARIANTS: `R_n + Σ release_i = R_0 + Σ reserve_i`
- DEPENDENCIES: REQ-BUDGET-009, REQ-EFFECT-024
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: reservation property tests; conservation tests
- EVIDENCE-STATUS: SPECIFIED

### REQ-CALC-013
- REQ-ID: REQ-CALC-013
- CATEGORY: calculus
- SOURCE: Red-on-Rust.md L23806–23819([30]); L27236([33]); spec/01 S-07 R-CALC-06
- NORMATIVE-LEVEL: IS
- STATEMENT: The frozen fault taxonomy is `Fault::Capability(CapabilityError) | BudgetExhausted | DeadlineExceeded | HostPolicyDenied(HostPolicyError) | EffectCanonicalization(EffectError) | Host(HostFault) | ReplayCorruption | InvalidReceipt`, plus `StalePlan` at the planner boundary.
- PRECONDITIONS: —
- POSTCONDITIONS: —
- INVARIANTS: — (closed set; inner variants not enumerated in the source — see AMB-08)
- DEPENDENCIES: U-08, U-14
- SECURITY-IMPACT: high (fault names are compared by the differential observer)
- VERIFICATION-METHOD: fault-coverage metric; differential fault comparison
- EVIDENCE-STATUS: SPECIFIED

### REQ-CALC-014
- REQ-ID: REQ-CALC-014
- CATEGORY: calculus
- SOURCE: Red-on-Rust.md L27236([33]); L28373([36]); spec/01 S-07 R-CALC-06
- NORMATIVE-LEVEL: MUST
- STATEMENT: `StalePlan` is a member of the fault taxonomy at the planner boundary.
- PRECONDITIONS: stale proposal rejected
- POSTCONDITIONS: `Fault::StalePlan` produced
- INVARIANTS: —
- DEPENDENCIES: REQ-PLANNER-014, REQ-PLANNER-015
- SECURITY-IMPACT: medium
- VERIFICATION-METHOD: stale-proposal test
- EVIDENCE-STATUS: SPECIFIED

### REQ-CALC-015
- REQ-ID: REQ-CALC-015
- CATEGORY: effect-protocol
- SOURCE: Red-on-Rust.md L26249–26262([33]); L3858–3873([7]); spec/01 S-07 R-CALC-07
- NORMATIVE-LEVEL: MUST
- STATEMENT: Effect semantics carry replayability/reversibility/idempotence properties; an effect's *machine result* can be replayed even when the real-world operation cannot.
- PRECONDITIONS: replay of a recorded effect
- POSTCONDITIONS: machine state is reconstructed from the recorded result without re-executing the real-world operation
- INVARIANTS: —
- DEPENDENCIES: REQ-HOST-012; U-06 (effect classes not defined)
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: replay correspondence test; `ReplayHost` trace validation
- EVIDENCE-STATUS: SPECIFIED

### REQ-CALC-016
- REQ-ID: REQ-CALC-016
- CATEGORY: effect-protocol
- SOURCE: Red-on-Rust.md L2141–2156([5] v1); L3858–3873([7] v2); spec/01 S-07 R-CALC-07
- NORMATIVE-LEVEL: NON-NORMATIVE
- STATEMENT: The per-operation property table (`FileRead`/`FileWrite`/`NetGet`/`NetSend`/`SpawnProcess` with `yes`/`no`/`sometimes`/`depends` entries, and cells containing `n/a`, `usually`, `generally no`, `difficult`) is an illustrative example, not a frozen operation table.
- PRECONDITIONS: —
- POSTCONDITIONS: —
- INVARIANTS: —
- DEPENDENCIES: U-06, C-05
- SECURITY-IMPACT: none (descriptive)
- VERIFICATION-METHOD: not applicable
- EVIDENCE-STATUS: SPECIFIED

### REQ-CALC-017
- REQ-ID: REQ-CALC-017
- CATEGORY: machine-semantics
- SOURCE: Red-on-Rust.md L7119–7144([13]); L8653–8682([16]); spec/01 S-07 R-CALC-08
- NORMATIVE-LEVEL: IS
- STATEMENT: Machine configuration `Σ = ⟨e, ρ, κ, B, t, H, L⟩` — current term, local environment, capability kernel, budget, logical time, isolated heap, append-only event log.
- PRECONDITIONS: —
- POSTCONDITIONS: —
- INVARIANTS: —
- DEPENDENCIES: REQ-CALC-019
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: state-shape review; snapshot content review
- EVIDENCE-STATUS: SPECIFIED

### REQ-CALC-018
- REQ-ID: REQ-CALC-018
- CATEGORY: machine-semantics
- SOURCE: Red-on-Rust.md L8653–8682([16]); L24156–24163([31]); spec/01 S-07 R-CALC-08
- NORMATIVE-LEVEL: IS
- STATEMENT: Global configuration `G = ⟨A, t, L, N_h, N_a⟩` — actors, logical time, event log, effect-ID allocator, actor-ID allocator.
- PRECONDITIONS: —
- POSTCONDITIONS: —
- INVARIANTS: —
- DEPENDENCIES: REQ-ACTOR-008, REQ-ACTOR-009
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: state-shape review
- EVIDENCE-STATUS: SPECIFIED

### REQ-CALC-019
- REQ-ID: REQ-CALC-019
- CATEGORY: machine-semantics
- SOURCE: Red-on-Rust.md L24148–24163([31]); L8653–8682([16]); spec/01 S-07 R-CALC-08
- NORMATIVE-LEVEL: MUST
- STATEMENT: Logical time, ID allocation, and the event log are strictly global; actors hold only isolated execution state.
- PRECONDITIONS: any actor transition
- POSTCONDITIONS: no actor-local copy of time, ID counters, or the log
- INVARIANTS: —
- DEPENDENCIES: REQ-ACTOR-008, REQ-CAP-019
- SECURITY-IMPACT: high (per-actor time would break determinism)
- VERIFICATION-METHOD: state-shape review; determinism differential
- EVIDENCE-STATUS: SPECIFIED

### REQ-CALC-020
- REQ-ID: REQ-CALC-020
- CATEGORY: machine-semantics
- SOURCE: Red-on-Rust.md L8706–8712([16] v0.3 E-Let/E-Seq/E-If) — **(v0.3 rules)**; L7590–7600([15])
- NORMATIVE-LEVEL: MUST
- STATEMENT: Pure local computation rules `E-Let`/`E-Seq`/`E-If` require `δ_t = 0`, `t + δ_t ≤ W`, and `C' = C − cost_C(rule)`; the successor configuration substitutes the evaluated subterm, charges `cost_C`, and keeps status `Running`.
- PRECONDITIONS: the rule's subterm has been evaluated
- POSTCONDITIONS: budget charged, time unchanged, no authority consulted
- INVARIANTS: `t + δ_t ≤ W`
- DEPENDENCIES: REQ-BUDGET-017, REQ-BUDGET-021
- SECURITY-IMPACT: medium
- VERIFICATION-METHOD: exhaustive small-state differential for `Let`/`Seq`/`If`
- EVIDENCE-STATUS: SPECIFIED

---

## S-08 CEK machine

### REQ-CEK-001
- REQ-ID: REQ-CEK-001
- CATEGORY: machine-semantics
- SOURCE: Red-on-Rust.md L37838–37854([54] §4); L41484–41499([60]); spec/01 S-08 R-CEK-01
- NORMATIVE-LEVEL: MUST
- STATEMENT: Evaluation uses an explicit CEK-style machine with state `EvalState { expr: Expr, env: Environment, continuation: Continuation }`.
- PRECONDITIONS: any evaluation
- POSTCONDITIONS: control state is a value of this type
- INVARIANTS: —
- DEPENDENCIES: REQ-CEK-002
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: deep-call stress (50k–100k); differential equivalence
- EVIDENCE-STATUS: SPECIFIED

### REQ-CEK-002
- REQ-ID: REQ-CEK-002
- CATEGORY: machine-semantics
- SOURCE: Red-on-Rust.md L37840([54] §4); L38858([54] §28); L41503([60] restated [60]); L14314([22] No Recursive Evaluator Dependence); spec/01 S-08 R-CEK-01
- NORMATIVE-LEVEL: MUST NOT
- STATEMENT: The evaluator MUST NOT depend on recursive host-language calls for call-stack management; recursive evaluation is a prohibited shortcut.
- PRECONDITIONS: any nested call
- POSTCONDITIONS: nesting depth is bounded by machine state, not by the Rust stack
- INVARIANTS: —
- DEPENDENCIES: REQ-CLAIM-001
- SECURITY-IMPACT: high (host stack overflow is an uncontrolled abort)
- VERIFICATION-METHOD: deep-call stress at 50k–100k depth
- EVIDENCE-STATUS: SPECIFIED

### REQ-CEK-003
- REQ-ID: REQ-CEK-003
- CATEGORY: machine-semantics
- SOURCE: Red-on-Rust.md L41484–41499([60]); L37838–37854([54] §4); L17846([25] continuation frames); L18009([25] continuation serialization); L14318([22] Explicit Suspension); spec/01 S-08 R-CEK-01
- NORMATIVE-LEVEL: MUST
- STATEMENT: Continuation state is explicit, serializable, replayable, and recoverable.
- PRECONDITIONS: any continuation exists
- POSTCONDITIONS: it can be encoded canonically and reconstructed
- INVARIANTS: —
- DEPENDENCIES: REQ-PERSIST-007; U-02 (no frozen byte encoding for `Frame`)
- SECURITY-IMPACT: high ; AMB-02
- VERIFICATION-METHOD: snapshot round-trip; recovery differential
- EVIDENCE-STATUS: SPECIFIED

### REQ-CEK-004
- REQ-ID: REQ-CEK-004
- CATEGORY: machine-semantics
- SOURCE: Red-on-Rust.md L37857–37886([54] §4); L16878–16905([25]); spec/01 S-08 R-CEK-02
- NORMATIVE-LEVEL: MUST
- STATEMENT: A value is terminal only when its continuation is empty: `Value ∧ K = ε ⇒ Halt`.
- PRECONDITIONS: the machine reaches a value
- POSTCONDITIONS: the machine halts with that value
- INVARIANTS: `Value ∧ K = ε ⇒ Halt`
- DEPENDENCIES: REQ-CEK-005
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: structural invariant tests; differential equivalence
- EVIDENCE-STATUS: SPECIFIED

### REQ-CEK-005
- REQ-ID: REQ-CEK-005
- CATEGORY: machine-semantics
- SOURCE: Red-on-Rust.md L37857–37886([54] §4); L16878–16905([25]); L37826–37838([54] master-prompt restatement); spec/01 S-08 R-CEK-02
- NORMATIVE-LEVEL: MUST
- STATEMENT: `Value ∧ K ≠ ε ⇒ Resume(K, Value)`.
- PRECONDITIONS: the machine reaches a value with a non-empty continuation
- POSTCONDITIONS: the top frame is resumed with the value
- INVARIANTS: `Value ∧ K ≠ ε ⇒ Resume(K, Value)`
- DEPENDENCIES: REQ-CEK-004
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: structural invariant tests; exhaustive small-state differential
- EVIDENCE-STATUS: SPECIFIED

### REQ-CEK-006
- REQ-ID: REQ-CEK-006
- CATEGORY: machine-semantics
- SOURCE: Red-on-Rust.md L37859–37869([54] §4, anti-pattern); L17379–17412([25] correction); spec/01 S-08 R-CEK-02
- NORMATIVE-LEVEL: MUST NOT
- STATEMENT: The pattern `Expr::Value(v) => Halt(v)` without first checking the continuation is a violation.
- PRECONDITIONS: any value case in the transition function
- POSTCONDITIONS: the continuation is inspected before halting
- INVARIANTS: —
- DEPENDENCIES: REQ-CEK-004, REQ-CEK-005
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: code review; mutation of the value case must be killed
- EVIDENCE-STATUS: SPECIFIED

### REQ-CEK-007
- REQ-ID: REQ-CEK-007
- CATEGORY: machine-semantics
- SOURCE: Red-on-Rust.md L16943–16958([25]); L23830–23856([30]); spec/01 S-08 R-CEK-03
- NORMATIVE-LEVEL: IS
- STATEMENT: The frozen continuation frame set is `LetValue{name,body,env} | Seq{second,env} | If{then,else,env} | CallFunction{args,env} | CallArgument{function,evaluated,remaining,caller_env} | Attenuate{name,body,env} | RequestCapability{operation,target,params,env} | RequestTarget{capability,operation,params,caller_env} | RequestArgument{capability,operation,target,evaluated,remaining,caller_env}`.
- PRECONDITIONS: —
- POSTCONDITIONS: —
- INVARIANTS: — (closed 9-frame set)
- DEPENDENCIES: U-02 (no frozen canonical encoding for frames)
- SECURITY-IMPACT: high ; AMB-26
- VERIFICATION-METHOD: frame-set review; continuation-length invariant tests
- EVIDENCE-STATUS: SPECIFIED

### REQ-CEK-008
- REQ-ID: REQ-CEK-008
- CATEGORY: security-invariant
- SOURCE: Red-on-Rust.md L16928–16958([25]); L23821–23856([30]); spec/01 S-08 R-CEK-03
- NORMATIVE-LEVEL: MUST NOT
- STATEMENT: `function.env` (closure lexical environment) and `caller_env` (call-site environment) are semantically different and MUST never be conflated.
- PRECONDITIONS: any call transition
- POSTCONDITIONS: each is used only for its own purpose
- INVARIANTS: closure environment ≠ caller environment
- DEPENDENCIES: REQ-CEK-016, REQ-CEK-017
- SECURITY-IMPACT: high (conflation breaks lexical scoping and capability binding)
- VERIFICATION-METHOD: `CEK-CLOSURE-LEXICAL-CAPTURE` including the shadowing case
- EVIDENCE-STATUS: SPECIFIED

### REQ-CEK-009
- REQ-ID: REQ-CEK-009
- CATEGORY: machine-semantics
- SOURCE: Red-on-Rust.md L16971–16995([25]); spec/01 S-08 R-CEK-04
- NORMATIVE-LEVEL: MUST
- STATEMENT: Lambda creation is pure and deterministic.
- PRECONDITIONS: a `Lambda` term is evaluated
- POSTCONDITIONS: no side effects, no authority or budget interaction beyond the transition's own cost
- INVARIANTS: —
- DEPENDENCIES: REQ-CEK-010
- SECURITY-IMPACT: medium
- VERIFICATION-METHOD: differential equivalence for `Lambda`
- EVIDENCE-STATUS: SPECIFIED

### REQ-CEK-010
- REQ-ID: REQ-CEK-010
- CATEGORY: machine-semantics
- SOURCE: Red-on-Rust.md L16971–16995([25]); L37889–37892([54] §5); spec/01 S-08 R-CEK-04
- NORMATIVE-LEVEL: MUST
- STATEMENT: Lambda captures the lexical environment at creation.
- PRECONDITIONS: a `Lambda` term is evaluated
- POSTCONDITIONS: the captured environment is the one in scope at creation
- INVARIANTS: —
- DEPENDENCIES: REQ-CEK-016
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: `CEK-CLOSURE-LEXICAL-CAPTURE`
- EVIDENCE-STATUS: SPECIFIED

### REQ-CEK-011
- REQ-ID: REQ-CEK-011
- CATEGORY: machine-semantics
- SOURCE: Red-on-Rust.md L16971–16995([25]); L12354([21]); spec/01 S-08 R-CEK-04
- NORMATIVE-LEVEL: MUST
- STATEMENT: Lambda produces `FunctionValue { params, body, env }`.
- PRECONDITIONS: a `Lambda` term is evaluated
- POSTCONDITIONS: the resulting value has exactly these components
- INVARIANTS: —
- DEPENDENCIES: REQ-CALC-001
- SECURITY-IMPACT: medium
- VERIFICATION-METHOD: type review; differential equivalence
- EVIDENCE-STATUS: SPECIFIED

### REQ-CEK-012
- REQ-ID: REQ-CEK-012
- CATEGORY: machine-semantics
- SOURCE: Red-on-Rust.md L16971–16995([25]); spec/01 S-08 R-CEK-04
- NORMATIVE-LEVEL: MUST
- STATEMENT: Lambda creation goes through the ordinary value-return mechanism; it does not immediately halt the machine.
- PRECONDITIONS: a `Lambda` is evaluated inside a larger term
- POSTCONDITIONS: evaluation continues with the enclosing continuation
- INVARIANTS: `Value ∧ K ≠ ε ⇒ Resume(K, Value)`
- DEPENDENCIES: REQ-CEK-005
- SECURITY-IMPACT: medium
- VERIFICATION-METHOD: exhaustive small-state differential
- EVIDENCE-STATUS: SPECIFIED

### REQ-CEK-013
- REQ-ID: REQ-CEK-013
- CATEGORY: machine-semantics
- SOURCE: Red-on-Rust.md L37889–37906([54] §5); L16878–16905([25]); L14317([22] Deterministic Evaluation Order); spec/01 S-08 R-CEK-05
- NORMATIVE-LEVEL: MUST
- STATEMENT: Calls evaluate strictly `function → argument 0 → argument 1 → … → argument N → apply`, i.e. left-to-right.
- PRECONDITIONS: a `Call` term is evaluated
- POSTCONDITIONS: evaluation order is observable in the trace and is left-to-right
- INVARIANTS: —
- DEPENDENCIES: REQ-CEK-014
- SECURITY-IMPACT: medium (order affects effect ordering and budget)
- VERIFICATION-METHOD: `CEK-CALL-ARGS-LTR`; mutation M001
- EVIDENCE-STATUS: SPECIFIED

### REQ-CEK-014
- REQ-ID: REQ-CEK-014
- CATEGORY: machine-semantics
- SOURCE: Red-on-Rust.md L37908–37910([54] §5); L16878–16905([25]); L37840–37862([54] master-prompt restatement); spec/01 S-08 R-CEK-05
- NORMATIVE-LEVEL: MUST
- STATEMENT: Arity mismatch is detected immediately after function evaluation and BEFORE any argument evaluation.
- PRECONDITIONS: the function value has been evaluated
- POSTCONDITIONS: mismatch faults before any argument is evaluated
- INVARIANTS: —
- DEPENDENCIES: REQ-CEK-013
- SECURITY-IMPACT: high (evaluating arguments first can trigger effects and budget spend on a call that cannot proceed)
- VERIFICATION-METHOD: `CEK-CALL-ARITY-PRECHECK`; mutation M002
- EVIDENCE-STATUS: SPECIFIED

### REQ-CEK-015
- REQ-ID: REQ-CEK-015
- CATEGORY: machine-semantics
- SOURCE: Red-on-Rust.md L37840–37862([54] §4/§5 boundary); spec/01 S-08 R-CEK-05
- NORMATIVE-LEVEL: MUST
- STATEMENT: Application uses the captured closure environment.
- PRECONDITIONS: a call is applied
- POSTCONDITIONS: parameter binding occurs in the closure environment
- INVARIANTS: —
- DEPENDENCIES: REQ-CEK-016
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: `CEK-CLOSURE-LEXICAL-CAPTURE`
- EVIDENCE-STATUS: SPECIFIED

### REQ-CEK-016
- REQ-ID: REQ-CEK-016
- CATEGORY: machine-semantics
- SOURCE: Red-on-Rust.md L18723–18851([26]); L37922–37926([54] §5); spec/01 S-08 R-CEK-05
- NORMATIVE-LEVEL: MUST
- STATEMENT: Application binds parameters in the captured closure environment: `ρ' = ρ_closure[x₁↦v₁, …, xₙ↦vₙ]`.
- PRECONDITIONS: function and all arguments evaluated, arity matches
- POSTCONDITIONS: the body evaluates in `ρ'`
- INVARIANTS: `ρ' = ρ_closure[x₁↦v₁, …, xₙ↦vₙ]`
- DEPENDENCIES: REQ-CEK-008, REQ-CEK-010
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: `CEK-CLOSURE-LEXICAL-CAPTURE`; mutation M003-class
- EVIDENCE-STATUS: SPECIFIED

### REQ-CEK-017
- REQ-ID: REQ-CEK-017
- CATEGORY: security-invariant
- SOURCE: Red-on-Rust.md L18723–18851([26]); spec/01 S-08 R-CEK-05
- NORMATIVE-LEVEL: MUST NOT
- STATEMENT: The caller's environment is not used to resolve free variables in the body (lexical-closure invariant).
- PRECONDITIONS: a closure body is evaluated
- POSTCONDITIONS: free variables resolve in the closure environment or fault
- INVARIANTS: —
- DEPENDENCIES: REQ-CEK-008, REQ-CEK-016
- SECURITY-IMPACT: high (dynamic capture would leak bindings across trust boundaries)
- VERIFICATION-METHOD: `CEK-CLOSURE-LEXICAL-CAPTURE` shadowing case
- EVIDENCE-STATUS: SPECIFIED

### REQ-CEK-018
- REQ-ID: REQ-CEK-018
- CATEGORY: machine-semantics
- SOURCE: Red-on-Rust.md L14632–14642([22]); L13655–L13663([21] continuation discipline); L13765–L13830([21] illustrative let/resume trace); spec/01 S-08 R-CEK-06
- NORMATIVE-LEVEL: MUST
- STATEMENT: For pure transitions the continuation length changes by exactly +1 on entry or −1 on resume.
- PRECONDITIONS: a pure transition occurs
- POSTCONDITIONS: `|K'| = |K| + 1` or `|K'| = |K| − 1`
- INVARIANTS: `|K'| − |K| ∈ {+1, −1}` for pure transitions
- DEPENDENCIES: REQ-CEK-019
- SECURITY-IMPACT: medium
- VERIFICATION-METHOD: structural push/pop invariant tests
- EVIDENCE-STATUS: SPECIFIED

### REQ-CEK-019
- REQ-ID: REQ-CEK-019
- CATEGORY: machine-semantics
- SOURCE: Red-on-Rust.md L14632–14642([22]); L13663–L13665([21] continuation discipline); L13001([21] consumed by exactly one frame); spec/01 S-08 R-CEK-06
- NORMATIVE-LEVEL: MUST NOT
- STATEMENT: No transition silently discards or duplicates continuation frames.
- PRECONDITIONS: any transition
- POSTCONDITIONS: frame multiset changes only as specified by the rule
- INVARIANTS: —
- DEPENDENCIES: REQ-CEK-018
- SECURITY-IMPACT: high (a dropped frame loses a pending effect or a capability binding)
- VERIFICATION-METHOD: structural invariant tests; mutation of frame handling must be killed
- EVIDENCE-STATUS: SPECIFIED

### REQ-CEK-020
- REQ-ID: REQ-CEK-020
- CATEGORY: machine-semantics
- SOURCE: Red-on-Rust.md L7273–7277([13]); L8850([16] v0.3 theorems); spec/01 S-08 R-CEK-07
- NORMATIVE-LEVEL: MUST
- STATEMENT: Progress: a well-typed, well-budgeted configuration is either a value, a fault, pending an effect, blocked on a message, or can take a step.
- PRECONDITIONS: configuration is well-typed and well-budgeted
- POSTCONDITIONS: one of the five outcomes holds
- INVARIANTS: progress property
- DEPENDENCIES: REQ-CEK-021
- SECURITY-IMPACT: medium
- VERIFICATION-METHOD: exhaustive small-state coverage; differential equivalence
- EVIDENCE-STATUS: SPECIFIED

### REQ-CEK-021
- REQ-ID: REQ-CEK-021
- CATEGORY: machine-semantics
- SOURCE: Red-on-Rust.md L7273–7277([13]); L8850([16]); spec/01 S-08 R-CEK-07
- NORMATIVE-LEVEL: MUST
- STATEMENT: Preservation: every transition preserves well-typedness and well-budgetness.
- PRECONDITIONS: any transition from a well-typed, well-budgeted configuration
- POSTCONDITIONS: the successor is well-typed and well-budgeted
- INVARIANTS: preservation property
- DEPENDENCIES: REQ-CEK-020, REQ-BUDGET-025
- SECURITY-IMPACT: medium
- VERIFICATION-METHOD: property-based testing; differential equivalence
- EVIDENCE-STATUS: SPECIFIED

### REQ-CEK-022
- REQ-ID: REQ-CEK-022
- CATEGORY: machine-semantics
- SOURCE: Red-on-Rust.md L8714–8716([16] v0.3 E-Call) — **(v0.3 rules)**; L2405–2410([6])
- NORMATIVE-LEVEL: MUST
- STATEMENT: `E-Call` requires `t + δ_t(call) ≤ W` and charges `C' = C − cost_C(call) − cost_C(B_f)`, where `B_f` is the fixed computational cost of the function, not a full budget escrow, preserving the caller's budget context.
- PRECONDITIONS: the callee is a lambda value with static cost `B_f`
- POSTCONDITIONS: both costs charged to the caller; no escrow created
- INVARIANTS: `t + δ_t ≤ W`
- DEPENDENCIES: REQ-BUDGET-021, REQ-COMPILE-007
- SECURITY-IMPACT: medium
- VERIFICATION-METHOD: budget conservation over call-heavy programs
- EVIDENCE-STATUS: SPECIFIED

---

## S-09 Capability algebra

### REQ-CAP-001
- REQ-ID: REQ-CAP-001
- CATEGORY: capability-authority
- SOURCE: Red-on-Rust.md L6354–6362([11] v0.2 frozen); spec/01 S-09 R-CAP-01
- NORMATIVE-LEVEL: IS
- STATEMENT: **Operations** `O` is a finite, enumerable set of atomic actions (e.g. `FileRead`, `NetSend` — examples illustrative).
- PRECONDITIONS: —
- POSTCONDITIONS: —
- INVARIANTS: `O` finite and enumerable
- DEPENDENCIES: U-21
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: algebra property tests
- EVIDENCE-STATUS: SPECIFIED

### REQ-CAP-002
- REQ-ID: REQ-CAP-002
- CATEGORY: capability-authority
- SOURCE: Red-on-Rust.md L6363–6370([11]); spec/01 S-09 R-CAP-01
- NORMATIVE-LEVEL: IS
- STATEMENT: **Scope** `S` has interpretation `⟦S⟧ ⊆ Target`, order `S₁ ≼_S S₂ ⇔ ⟦S₁⟧ ⊆ ⟦S₂⟧`, and meet `S₁ ⊓ S₂` with `⟦S₁ ⊓ S₂⟧ = ⟦S₁⟧ ∩ ⟦S₂⟧`.
- PRECONDITIONS: —
- POSTCONDITIONS: —
- INVARIANTS: `⟦S₁ ⊓ S₂⟧ = ⟦S₁⟧ ∩ ⟦S₂⟧`
- DEPENDENCIES: REQ-CAP-012
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: algebra property tests (meet/order laws)
- EVIDENCE-STATUS: SPECIFIED

### REQ-CAP-003
- REQ-ID: REQ-CAP-003
- CATEGORY: capability-authority
- SOURCE: Red-on-Rust.md L6363–6370([11]); spec/01 S-09 R-CAP-01
- NORMATIVE-LEVEL: IS
- STATEMENT: **Parameter constraint** `Q` is a predicate `Params → Bool`, ordered by implication `Q₁ ≼_Q Q₂ ⇔ ∀p. Q₁(p) ⇒ Q₂(p)`, with meet by conjunction.
- PRECONDITIONS: —
- POSTCONDITIONS: —
- INVARIANTS: `Q₁ ≼_Q Q₂ ⇔ ∀p. Q₁(p) ⇒ Q₂(p)`
- DEPENDENCIES: REQ-CAP-012
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: algebra property tests
- EVIDENCE-STATUS: SPECIFIED

### REQ-CAP-004
- REQ-ID: REQ-CAP-004
- CATEGORY: capability-authority
- SOURCE: Red-on-Rust.md L6363–6370([11]); spec/01 S-09 R-CAP-01
- NORMATIVE-LEVEL: IS
- STATEMENT: **Resource limit** `R` is a set of resource ceilings with component-wise order `≤` and meet (component-wise minimum).
- PRECONDITIONS: —
- POSTCONDITIONS: —
- INVARIANTS: component-wise meet
- DEPENDENCIES: REQ-CAP-012, REQ-CAP-010
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: algebra property tests
- EVIDENCE-STATUS: SPECIFIED

### REQ-CAP-005
- REQ-ID: REQ-CAP-005
- CATEGORY: capability-authority
- SOURCE: Red-on-Rust.md L6363–6379([11]); spec/01 S-09 R-CAP-01
- NORMATIVE-LEVEL: IS
- STATEMENT: **Lifetime** `T` is a set of temporal intervals `[t_start, t_end]`, ordered by subset, with meet by interval intersection.
- PRECONDITIONS: —
- POSTCONDITIONS: —
- INVARIANTS: meet by interval intersection
- DEPENDENCIES: REQ-CAP-010, REQ-CAP-013
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: algebra property tests; expiration conformance tests
- EVIDENCE-STATUS: SPECIFIED

### REQ-CAP-006
- REQ-ID: REQ-CAP-006
- CATEGORY: capability-authority
- SOURCE: Red-on-Rust.md L6371–6379([11]); spec/01 S-09 R-CAP-01
- NORMATIVE-LEVEL: MAY
- STATEMENT: The implementation may use various representations (globs, CIDR, …) but the algebra operates on semantic interpretations.
- PRECONDITIONS: representation choice
- POSTCONDITIONS: order and meet are defined on interpretations, not on syntax
- INVARIANTS: —
- DEPENDENCIES: REQ-CAP-002
- SECURITY-IMPACT: high (syntactic ordering would admit unsound attenuation)
- VERIFICATION-METHOD: algebra property tests over representation variants
- EVIDENCE-STATUS: SPECIFIED

### REQ-CAP-007
- REQ-ID: REQ-CAP-007
- CATEGORY: capability-authority
- SOURCE: Red-on-Rust.md L6381–6390([11]); spec/01 S-09 R-CAP-03
- NORMATIVE-LEVEL: IS
- STATEMENT: `A₁ ≼ A₂` iff `O₁ ⊆ O₂` and for all `o ∈ O₁`: `S₁ ≼_S S₂ ∧ Q₁ ≼_Q Q₂ ∧ R₁ ≤ R₂ ∧ T₁ ⊆ T₂`.
- PRECONDITIONS: two authorities
- POSTCONDITIONS: the order relation is decidable per this definition
- INVARIANTS: the 4-conjunct definition (kept whole per rule 6)
- DEPENDENCIES: REQ-CAP-002…REQ-CAP-005
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: monotonicity property test
- EVIDENCE-STATUS: SPECIFIED

### REQ-CAP-008
- REQ-ID: REQ-CAP-008
- CATEGORY: capability-authority
- SOURCE: Red-on-Rust.md L6370–6380([11]); spec/01 S-09 R-CAP-02
- NORMATIVE-LEVEL: MUST
- STATEMENT: Authority is indexed by operation to prevent cross-operation contamination: `A = { (o, A_o) | o ∈ O_granted }` with `A_o = ⟨S, Q, R, T⟩`.
- PRECONDITIONS: any authority grant
- POSTCONDITIONS: no grant is usable for an operation outside `O_granted`
- INVARIANTS: `op ∈ O_A` is a conjunct of authorization
- DEPENDENCIES: REQ-CAP-010
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: cross-operation contamination tests
- EVIDENCE-STATUS: SPECIFIED

### REQ-CAP-009
- REQ-ID: REQ-CAP-009
- CATEGORY: capability-authority
- SOURCE: Red-on-Rust.md L6391–6396([11]); L6406 ([11]); spec/01 S-09 R-CAP-04
- NORMATIVE-LEVEL: IS
- STATEMENT: A `Constraint` is a request to narrow an existing grant, conceptually distinct from `Authority`.
- PRECONDITIONS: —
- POSTCONDITIONS: —
- INVARIANTS: —
- DEPENDENCIES: REQ-CAP-012, REQ-KERN-005
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: API review (kernel takes `Constraint`, never `Authority`)
- EVIDENCE-STATUS: SPECIFIED

### REQ-CAP-010
- REQ-ID: REQ-CAP-010
- CATEGORY: security-invariant
- SOURCE: Red-on-Rust.md L6406–6421([11]); L6647–6656([11]); L37937–37948([54] §6); spec/01 S-09 R-CAP-06
- NORMATIVE-LEVEL: MUST
- STATEMENT: For effect `E = ⟨op, target, params, cost⟩` at logical time `t`: `Authorized(A, E, t) ⇔ op ∈ O_A ∧ target ∈ ⟦A_op.S⟧ ∧ A_op.Q(params) ∧ cost ≤ A_op.R ∧ t ∈ A_op.T`.
- PRECONDITIONS: an effect is presented for authorization at logical time `t`
- POSTCONDITIONS: authorization succeeds iff all five conjuncts hold
- INVARIANTS: the 5-conjunct biconditional (kept whole per rule 6)
- DEPENDENCIES: REQ-CAP-008, REQ-CAP-013
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: Track B mock-kernel tests; mutation M005 (omit capability ceiling)
- EVIDENCE-STATUS: SPECIFIED

### REQ-CAP-011
- REQ-ID: REQ-CAP-011
- CATEGORY: capability-authority
- SOURCE: Red-on-Rust.md L6406–6421([11]); L8692–8696([16]); spec/01 S-09 R-CAP-06
- NORMATIVE-LEVEL: MUST
- STATEMENT: The `cost` in `Authorized` is the effect's static resource requirement checked against the capability ceiling `R_A`; the dynamic execution budget is checked separately (dual gate).
- PRECONDITIONS: an effect is authorized
- POSTCONDITIONS: both the ceiling check and the runtime budget check occur
- INVARIANTS: —
- DEPENDENCIES: REQ-BUDGET-014
- SECURITY-IMPACT: critical (conflating the two would let a rich budget override a narrow grant)
- VERIFICATION-METHOD: short-circuit Track C; mutation M005
- EVIDENCE-STATUS: SPECIFIED

### REQ-CAP-012
- REQ-ID: REQ-CAP-012
- CATEGORY: capability-authority
- SOURCE: Red-on-Rust.md L6397–6404([11]); L6657–6661([11] Theorem 1); L37931–37935([54] §6); spec/01 S-09 R-CAP-05
- NORMATIVE-LEVEL: IS
- STATEMENT: `derive(A, C) = { (o, derive_op(A_o, C_o)) | o ∈ O_A ∩ O_C }` where `derive_op(⟨S,Q,R,T⟩, ⟨S_c,Q_c,R_c,T_c⟩) = ⟨S ⊓ S_c, Q ⊓ Q_c, R ⊓ R_c, T ⊓ T_c⟩`.
- PRECONDITIONS: an authority and a constraint
- POSTCONDITIONS: the derived authority is defined per operation on the intersection of granted and constrained operations
- INVARIANTS: per-operation meet definition (kept whole per rule 6)
- DEPENDENCIES: REQ-CAP-002…REQ-CAP-005, REQ-CORE-004
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: `CAP-DERIVE-NO-AMPLIFICATION`; property tests
- EVIDENCE-STATUS: SPECIFIED

### REQ-CAP-013
- REQ-ID: REQ-CAP-013
- CATEGORY: security-invariant
- SOURCE: Red-on-Rust.md L6434–6445([11]); L6647–6656([11]); L20042–20060([27] §17 revocation visible to attenuation); spec/01 S-09 R-CAP-07
- NORMATIVE-LEVEL: MUST
- STATEMENT: `Valid(c, t) ⇔ Live(c) ∧ t ∈ Lifetime(c) ∧ ∀a ∈ Ancestors(c). Live(a)`.
- PRECONDITIONS: a capability reference is validated at logical time `t`
- POSTCONDITIONS: validity holds iff the reference is live, unexpired, and all ancestors are live
- INVARIANTS: the 3-conjunct biconditional (kept whole per rule 6)
- DEPENDENCIES: REQ-CAP-014, REQ-CAP-015
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: `CAP-REVOCATION-ANCESTOR`; mutation M004
- EVIDENCE-STATUS: SPECIFIED

### REQ-CAP-014
- REQ-ID: REQ-CAP-014
- CATEGORY: security-invariant
- SOURCE: Red-on-Rust.md L6434–6445([11]); L37955–37957([54] §6); spec/01 S-09 R-CAP-07
- NORMATIVE-LEVEL: MUST
- STATEMENT: Revoking a parent sets `Live(parent) = false`.
- PRECONDITIONS: a revocation is performed
- POSTCONDITIONS: the parent node is marked not live
- INVARIANTS: —
- DEPENDENCIES: REQ-CAP-013
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: revocation conformance tests; mutation M004
- EVIDENCE-STATUS: SPECIFIED

### REQ-CAP-015
- REQ-ID: REQ-CAP-015
- CATEGORY: security-invariant
- SOURCE: Red-on-Rust.md L6434–6445([11]); spec/01 S-09 R-CAP-07
- NORMATIVE-LEVEL: MUST
- STATEMENT: Descendants are invalidated lazily by walking the ancestor chain during the `Valid` check, in `O(d)` where `d` is lineage depth.
- PRECONDITIONS: a `Valid` check runs on a descendant
- POSTCONDITIONS: a revoked ancestor causes invalidity
- INVARIANTS: —
- DEPENDENCIES: REQ-CAP-013
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: `CAP-REVOCATION-ANCESTOR`
- EVIDENCE-STATUS: SPECIFIED

### REQ-CAP-016
- REQ-ID: REQ-CAP-016
- CATEGORY: security-invariant
- SOURCE: Red-on-Rust.md L6422–6426([11] Theorem 1); L6657–6661([11]); L4472([8] security interpretation); spec/01 S-09 R-CAP-08
- NORMATIVE-LEVEL: MUST
- STATEMENT: Theorem 1 (attenuation soundness): `derive(A,C) ≼ A`.
- PRECONDITIONS: any derivation
- POSTCONDITIONS: the property holds
- INVARIANTS: `derive(A,C) ≼ A`
- DEPENDENCIES: REQ-CAP-012, REQ-CAP-007
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: property tests (proof sketch only in source; **not** `PROVEN`)
- EVIDENCE-STATUS: SPECIFIED

### REQ-CAP-017
- REQ-ID: REQ-CAP-017
- CATEGORY: security-invariant
- SOURCE: Red-on-Rust.md L6427–6430([11] Theorem 2); L6662–6666([11]); spec/01 S-09 R-CAP-08
- NORMATIVE-LEVEL: MUST
- STATEMENT: Theorem 2 (authority monotonicity): `A' ≼ A ∧ Authorized(A',E,t) ⇒ Authorized(A,E,t)`.
- PRECONDITIONS: `A' ≼ A` and `A'` authorizes `E` at `t`
- POSTCONDITIONS: `A` authorizes `E` at `t`
- INVARIANTS: `A' ≼ A ∧ Authorized(A',E,t) ⇒ Authorized(A,E,t)`
- DEPENDENCIES: REQ-CAP-007, REQ-CAP-010
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: property tests (not `PROVEN`)
- EVIDENCE-STATUS: SPECIFIED

### REQ-CAP-018
- REQ-ID: REQ-CAP-018
- CATEGORY: security-invariant
- SOURCE: Red-on-Rust.md L6431–6433([11] Theorem 3); L6667–6671([11]); spec/01 S-09 R-CAP-08
- NORMATIVE-LEVEL: MUST
- STATEMENT: Theorem 3 (attenuation corollary): assuming `Authorized(A,E,t)`, `Authorized(derive(A,C),E,t) ⇔ Satisfies(C,E,t)`.
- PRECONDITIONS: `Authorized(A,E,t)`
- POSTCONDITIONS: the derived authority authorizes exactly the effects satisfying `C`
- INVARIANTS: `Authorized(derive(A,C),E,t) ⇔ Satisfies(C,E,t)`
- DEPENDENCIES: REQ-CAP-012, REQ-CAP-010
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: property tests (not `PROVEN`)
- EVIDENCE-STATUS: SPECIFIED

### REQ-CAP-019
- REQ-ID: REQ-CAP-019
- CATEGORY: capability-authority
- SOURCE: Red-on-Rust.md L6434–6436([11]); L37948–37950([54] §6); spec/01 S-09 R-CAP-09
- NORMATIVE-LEVEL: MUST
- STATEMENT: Authorization is evaluated at an explicit logical time; time `t` is never fetched from the host OS.
- PRECONDITIONS: any `Authorized`/`Valid` evaluation
- POSTCONDITIONS: `t` is supplied by machine state
- INVARIANTS: —
- DEPENDENCIES: REQ-CAP-021, REQ-CALC-019
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: determinism tests; code review for OS time calls
- EVIDENCE-STATUS: SPECIFIED

### REQ-CAP-020
- REQ-ID: REQ-CAP-020
- CATEGORY: capability-authority
- SOURCE: Red-on-Rust.md L6434–6436([11]); spec/01 S-09 R-CAP-09
- NORMATIVE-LEVEL: MUST
- STATEMENT: Time is an explicit component of machine state (logical clock / deterministic timestamp), ensuring replay determinism.
- PRECONDITIONS: —
- POSTCONDITIONS: time is part of the serialized machine state
- INVARIANTS: —
- DEPENDENCIES: REQ-CALC-017, REQ-CALC-019
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: snapshot content review; replay determinism
- EVIDENCE-STATUS: SPECIFIED

### REQ-CAP-021
- REQ-ID: REQ-CAP-021
- CATEGORY: security-invariant
- SOURCE: Red-on-Rust.md L38863([54] §28); L24260([31]); spec/01 S-09 R-CAP-09
- NORMATIVE-LEVEL: MUST NOT
- STATEMENT: Wall-clock time is forbidden as semantic machine state.
- PRECONDITIONS: any machine-state component or transition decision
- POSTCONDITIONS: no wall-clock value influences semantics
- INVARIANTS: —
- DEPENDENCIES: REQ-CLAIM-006
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: code review; determinism differential across wall-clock variation
- EVIDENCE-STATUS: SPECIFIED

### REQ-CAP-022
- REQ-ID: REQ-CAP-022
- CATEGORY: capability-authority
- SOURCE: Red-on-Rust.md L8717–8719([16] v0.3 E-Attenuate); L8837([16] resolution 6) — **(v0.3 rules)**
- NORMATIVE-LEVEL: MUST
- STATEMENT: `E-Attenuate` requires premises `Valid(c, t)` and `AdmissibleConstraint(C_req)` and produces `c' = kernel.derive(c, C_req)`; it uses `AdmissibleConstraint`, not `Authorized` — security is guaranteed by `derive(A, C) ≼ A`. The transition binds `cap(c')` into the term, adds `c'` to the actor context `κ`, charges `cost_C(att)`, and advances `t` by `δ_t(att)`.
- PRECONDITIONS: `Valid(c,t)` and `AdmissibleConstraint(C_req)`
- POSTCONDITIONS: new capability registered in the actor's context; budget charged; time advanced
- INVARIANTS: `derive(A,C) ≼ A`
- DEPENDENCIES: REQ-CAP-012, REQ-CAP-013, REQ-CAP-023; AMB-12 (`AdmissibleConstraint` status)
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: attenuation conformance tests; independent reference algebra (M4 gate)
- EVIDENCE-STATUS: SPECIFIED

### REQ-CAP-023
- REQ-ID: REQ-CAP-023
- CATEGORY: capability-authority
- SOURCE: Red-on-Rust.md L8721–8722([16] v0.3 E-AttenuateDenied) — **(v0.3 rules)**
- NORMATIVE-LEVEL: MUST
- STATEMENT: `E-AttenuateDenied`: `¬Valid(c, t) ∨ ¬AdmissibleConstraint(C_req)` transitions the actor to `Fault(CapabilityRevoked)`.
- PRECONDITIONS: either premise of `E-Attenuate` fails
- POSTCONDITIONS: actor faults; no capability is created
- INVARIANTS: —
- DEPENDENCIES: REQ-CALC-013 (the name `CapabilityRevoked` is not a variant of the frozen `Fault` enum — AMB-08)
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: revocation/expiration negative tests; differential fault comparison
- EVIDENCE-STATUS: SPECIFIED

### REQ-CAP-024
- REQ-ID: REQ-CAP-024
- CATEGORY: capability-authority
- SOURCE: Red-on-Rust.md L7858 ([15]), L8717 ([16]), L10068 ([17]), L10171([18]); spec/06 C-30; spec/09 U-09
- NORMATIVE-LEVEL: AMBIGUOUS
- STATEMENT: `AdmissibleConstraint` is used as a premise of the frozen v0.3 attenuation rules and appears in the `[18]` contract list, but no frozen text defines what makes a constraint admissible, and `spec/06` C-30 records it as orphaned. Its normative status and definition are unresolved.
- PRECONDITIONS: attenuation requested
- POSTCONDITIONS: — (undefined)
- INVARIANTS: —
- DEPENDENCIES: U-09, AMB-12
- SECURITY-IMPACT: high (an unconstrained `Constraint` could be malformed in ways `derive` does not neutralize)
- VERIFICATION-METHOD: UNDEFINED until decided (req/04, VU-07)
- EVIDENCE-STATUS: SPECIFIED

---

## S-10 Capability kernel

### REQ-CAP-025
- REQ-ID: REQ-CAP-025
- CATEGORY: capability-kernel
- SOURCE: Red-on-Rust.md L19484–19498([27] §7); L19655–19665([27] §15); spec/01 S-10 R-KERN-02
- NORMATIVE-LEVEL: MUST NOT
- STATEMENT: Capability derivation is atomic from the evaluator's perspective: `validate(parent)` / `derive(parent)` / `validate(child)` MUST NOT be exposed as three independently observable semantic operations.
- PRECONDITIONS: any attenuation
- POSTCONDITIONS: the evaluator observes one kernel call, not a sequence
- INVARIANTS: —
- DEPENDENCIES: REQ-KERN-002, REQ-CAP-012, REQ-CAP-013
- SECURITY-IMPACT: critical (an observable intermediate state is a time-of-check/time-of-use window)
- VERIFICATION-METHOD: mock-kernel exactly-one-call assertions; API-surface review
- EVIDENCE-STATUS: SPECIFIED

### REQ-CAP-026
- REQ-ID: REQ-CAP-026
- CATEGORY: capability-authority
- SOURCE: Red-on-Rust.md L20027–20037([27] §16 Monotonicity); L6425–6432([11]); spec/01 S-09 R-CAP-08
- NORMATIVE-LEVEL: MUST
- STATEMENT: Derivation is monotone in the constraint: `C_1 ≼ C_2 ⇒ derive(A, C_1) ≼ derive(A, C_2)`.
- PRECONDITIONS: two constraints over the same authority
- POSTCONDITIONS: the narrower constraint yields the narrower derived authority
- INVARIANTS: `C_1 ≼ C_2 ⇒ derive(A, C_1) ≼ derive(A, C_2)`
- DEPENDENCIES: REQ-CAP-007, REQ-CAP-012, REQ-CORE-004
- SECURITY-IMPACT: high (the source names this an explicit property-test target for the capability algebra)
- VERIFICATION-METHOD: algebra property tests over constraint pairs
- EVIDENCE-STATUS: SPECIFIED
### REQ-KERN-001
- REQ-ID: REQ-KERN-001
- CATEGORY: capability-kernel
- SOURCE: Red-on-Rust.md L10188–10196([18]); L9127–9133([17]); L5958([10] generation-safety property); spec/01 S-10 R-KERN-01
- NORMATIVE-LEVEL: IS
- STATEMENT: `CapRef { index: u32, generation: u32 }` is an opaque, generation-safe capability reference.
- PRECONDITIONS: —
- POSTCONDITIONS: —
- INVARIANTS: —
- DEPENDENCIES: REQ-KERN-002
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: type review; generation-reuse negative tests
- EVIDENCE-STATUS: SPECIFIED

### REQ-KERN-002
- REQ-ID: REQ-KERN-002
- CATEGORY: capability-kernel
- SOURCE: Red-on-Rust.md L10188–10196([18]); spec/01 S-10 R-KERN-01
- NORMATIVE-LEVEL: MUST
- STATEMENT: `CapRef` fields are private.
- PRECONDITIONS: any crate outside the kernel
- POSTCONDITIONS: fields are unreadable and unwritable
- INVARIANTS: —
- DEPENDENCIES: REQ-KERN-003
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: Rust visibility review
- EVIDENCE-STATUS: SPECIFIED

### REQ-KERN-003
- REQ-ID: REQ-KERN-003
- CATEGORY: capability-kernel
- SOURCE: Red-on-Rust.md L10190–10196([18] "constructed ONLY by CapabilityKernel"); spec/01 S-10 R-KERN-01
- NORMATIVE-LEVEL: MUST NOT
- STATEMENT: There is no public constructor from arbitrary integers; `CapRef`s are constructed only by the kernel.
- PRECONDITIONS: any crate outside the kernel
- POSTCONDITIONS: no forgery of a capability reference is possible
- INVARIANTS: —
- DEPENDENCIES: REQ-TRUST-007
- SECURITY-IMPACT: critical (a forgeable reference defeats the entire authority model)
- VERIFICATION-METHOD: API-surface review; negative construction test
- EVIDENCE-STATUS: SPECIFIED

### REQ-KERN-004
- REQ-ID: REQ-KERN-004
- CATEGORY: capability-kernel
- SOURCE: Red-on-Rust.md L6672–6700([11] API v0.2); L19153–19175([27]); L37929–37962([54] §6); L6700–6710([11]); spec/01 S-10 R-KERN-02
- NORMATIVE-LEVEL: MUST
- STATEMENT: `authorize(cap: CapRef, effect: &Effect, t: u64) -> Result<(), Fault>` resolves the reference, checks liveness, ancestor liveness, and the canonical authorization predicate, returning `Revoked` / `AncestorRevoked` / `Unauthorized` faults.
- PRECONDITIONS: a `CapRef` and an effect at logical time `t`
- POSTCONDITIONS: `Ok(())` iff `Valid` and `Authorized`; otherwise the specific fault
- INVARIANTS: —
- DEPENDENCIES: REQ-CAP-010, REQ-CAP-013; AMB-08 (fault variant names)
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: Track B mock-kernel exactly-one-call assertions
- EVIDENCE-STATUS: SPECIFIED

### REQ-KERN-005
- REQ-ID: REQ-KERN-005
- CATEGORY: capability-kernel
- SOURCE: Red-on-Rust.md L6672–6700([11]); L19153–19175([27]); spec/01 S-10 R-KERN-02
- NORMATIVE-LEVEL: MUST
- STATEMENT: `attenuate/derive(parent: CapRef, constraint: Constraint, t) -> Result<CapRef, Fault>` takes a `Constraint` (not an `Authority`) and inserts a new arena node with a lineage parent link.
- PRECONDITIONS: a parent `CapRef` and a `Constraint`
- POSTCONDITIONS: a new `CapRef` whose authority is the meet with the constraint, linked to the parent
- INVARIANTS: `derive(A,C) ≼ A`
- DEPENDENCIES: REQ-CAP-009, REQ-CAP-012
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: `CAP-DERIVE-NO-AMPLIFICATION`; `CAP-REVOCATION-ANCESTOR`
- EVIDENCE-STATUS: SPECIFIED

### REQ-KERN-006
- REQ-ID: REQ-KERN-006
- CATEGORY: capability-kernel
- SOURCE: Red-on-Rust.md L19153–19175([27]); L39397–39407([58]); L37722–37744([54] §1.3); spec/01 S-10 R-KERN-02/R-KERN-03
- NORMATIVE-LEVEL: MUST NOT
- STATEMENT: `AuthorityNode` and all authority internals MUST remain `pub(crate)`/inaccessible to evaluator and runtime consumers; the evaluator sees only `Value::Capability(CapRef)` — "Evaluator knows references; Kernel knows authority."
- PRECONDITIONS: workspace build
- POSTCONDITIONS: no read path from evaluator/runtime to authority state
- INVARIANTS: `CapRef ⇏ AuthorityInspection`
- DEPENDENCIES: REQ-TRUST-006, REQ-TRUST-009
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: Rust visibility review; dependency direction (kernel cannot depend on runtime); first security gate property 2
- EVIDENCE-STATUS: SPECIFIED

### REQ-KERN-007
- REQ-ID: REQ-KERN-007
- CATEGORY: capability-kernel
- SOURCE: Red-on-Rust.md L6672–6728([11]); L19153–19175([27]); spec/01 S-10 R-KERN-02
- NORMATIVE-LEVEL: MUST
- STATEMENT: `valid/validate(cap, t)` performs lineage validation and is the validation entry point used by attenuation.
- PRECONDITIONS: a `CapRef` and logical time
- POSTCONDITIONS: validity determined per `Valid(c,t)`
- INVARIANTS: `Valid(c, t) ⇔ Live(c) ∧ t ∈ Lifetime(c) ∧ ∀a ∈ Ancestors(c). Live(a)`
- DEPENDENCIES: REQ-CAP-013
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: revocation/expiration conformance tests
- EVIDENCE-STATUS: SPECIFIED

### REQ-KERN-008
- REQ-ID: REQ-KERN-008
- CATEGORY: capability-kernel
- SOURCE: Red-on-Rust.md L37937–37950([54] §6); spec/01 S-10 R-KERN-02
- NORMATIVE-LEVEL: MUST
- STATEMENT: Every kernel authority decision takes an explicit logical time parameter.
- PRECONDITIONS: any `authorize`/`derive`/`validate` call
- POSTCONDITIONS: `t` is passed by the caller from machine state
- INVARIANTS: —
- DEPENDENCIES: REQ-CAP-019
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: API review; mock-kernel parameter assertions
- EVIDENCE-STATUS: SPECIFIED

### REQ-KERN-009
- REQ-ID: REQ-KERN-009
- CATEGORY: capability-kernel
- SOURCE: Red-on-Rust.md L13267–13281([21] §17); L37931–37935([54] §6); L14316([22] Capability Opacity); spec/01 S-03 R-TRUST-03; spec/01 S-10 R-KERN-01
- NORMATIVE-LEVEL: MUST NOT
- STATEMENT: The evaluator never receives `Authority`, `Scope`, `Rights`, `Parent`, or `Revocation state`; only the opaque reference crosses the kernel/evaluator boundary.
- PRECONDITIONS: any evaluator step
- POSTCONDITIONS: none of the five appears in evaluator-visible state
- INVARIANTS: `CapRef ⇏ AuthorityInspection`
- DEPENDENCIES: REQ-KERN-006, REQ-CALC-002, REQ-TRUST-009
- SECURITY-IMPACT: critical (a capability carrying its own authority would be forgeable and amplifiable)
- VERIFICATION-METHOD: evaluator input-domain review; type review of the kernel/evaluator boundary
- EVIDENCE-STATUS: SPECIFIED

---

### REQ-CEK-023
- REQ-ID: REQ-CEK-023
- CATEGORY: machine-semantics
- SOURCE: Red-on-Rust.md L14313([22] Continuation Preservation); spec/01 S-08 R-CEK-06
- NORMATIVE-LEVEL: MUST
- STATEMENT: `continue_with_value` is the only path that pops a continuation frame; every `enter_*` function pushes exactly one frame or returns a terminal `EvalStep`, so no transition silently discards state.
- PRECONDITIONS: any evaluator transition
- POSTCONDITIONS: frame count changes only through `continue_with_value` (pop) or an `enter_*` push
- INVARIANTS: —
- DEPENDENCIES: REQ-CEK-019, REQ-CEK-007
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: frame-discipline property test; `CEK-CONTINUATION-NO-LOSS` differential
- EVIDENCE-STATUS: SPECIFIED

### REQ-CEK-024
- REQ-ID: REQ-CEK-024
- CATEGORY: machine-semantics
- SOURCE: Red-on-Rust.md L14315([22] No Direct Host Access); spec/01 S-08 R-CEK-01
- NORMATIVE-LEVEL: MUST
- STATEMENT: The `eval` module has zero dependencies on `std::fs`, `std::net` or equivalent host facilities; its only vocabulary for side effects is returning `EvalStep::RequestEffect`.
- PRECONDITIONS: —
- POSTCONDITIONS: no host facility is reachable from the evaluator; side effects exist only as machine requests
- INVARIANTS: —
- DEPENDENCIES: REQ-CORE-001, REQ-EFFECT-005, REQ-KERN-009
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: dependency review of the evaluator crate; `EVAL-NO-DIRECT-HOST-ACCESS` assertion
- EVIDENCE-STATUS: SPECIFIED
