# MOD-05 — EVALUATOR: Explicit CEK evaluation machine

> Owns semantic execution: the explicit Control–Environment–Continuation machine
> whose transitions are the only definition of what programs *do*.

## SECTION-ID

`MOD-05` (domain `EVALUATOR`). Owner module file for the `CEK` obligation area.

## TITLE

Explicit CEK machine — explicit continuation state, value-return invariant, frozen
frame set, lexical closures, strict left-to-right call evaluation with arity
precheck, continuation preservation, progress and preservation.

## PURPOSE

Provide a small-step evaluator whose *entire* control state is explicit data — never
the host language's call stack — so that machine state is serializable, replayable,
and recoverable, and so that evaluation order, closure capture, and fault behavior
are specified transition-by-transition rather than inherited from Rust.

## NORMATIVE-CONTENT

Normative text home: `spec/01` S-08; atomic renderings
`req/01-registry-part2-semantics.md` (CEK block). This module owns:

- **Explicit machine** (R-CEK-01): `EvalState { expr, env, continuation }`; no
  recursive host-language evaluation for call-stack management; continuation state is
  explicit, serializable, replayable, recoverable.
- **Value-return invariant** (R-CEK-02): `Value ∧ K = ε ⇒ Halt`;
  `Value ∧ K ≠ ε ⇒ Resume(K, Value)`. Terminal only on empty continuation —
  `Expr::Value(v) => Halt(v)` without checking the continuation is a violation.
- **Frozen frame set** (R-CEK-03): the nine frozen frames (`LetValue`, `Seq`, `If`,
  `CallFunction`, `CallArgument{function, evaluated, remaining, caller_env}`,
  `Attenuate`, `RequestCapability`, `RequestTarget`, `RequestArgument{…caller_env}`);
  closure env and caller env are semantically distinct and never conflated.
- **Lambda** (R-CEK-04): pure, deterministic; captures the *lexical* environment at
  creation; result flows through the ordinary value-return mechanism.
- **Call** (R-CEK-05): function → arg₀ → … → argₙ → apply, strictly left-to-right;
  arity mismatch detected **immediately after function evaluation, before any
  argument evaluation**; application binds parameters in the captured closure
  environment `ρ' = ρ_closure[xᵢ↦vᵢ]`.
- **Continuation preservation** (R-CEK-06): pure transitions change continuation
  length by exactly +1 (entry) / −1 (resume); frames are never silently discarded or
  duplicated; `continue_with_value` is the only frame-popping path and every
  `enter_*` pushes exactly one frame or returns a terminal step (REQ-CEK-023).
- **Progress & preservation** (R-CEK-07): a well-typed, well-budgeted configuration
  is a value, a fault, effect-pending, receive-blocked, or can step; every transition
  preserves well-typedness and well-budgetness.

Also owned here (explicit placement): REQ-CEK-022 (v0.3 `E-Call` premises:
`t + δ_t(call) ≤ W`, consumption at call) — budget cross-reference to MOD-04; and
REQ-CEK-024 (the evaluator's only side-effect vocabulary is `EvalStep::RequestEffect`;
zero host dependencies).

Crate contract (mirrored by pointer): CEK machine lives in `ror-runtime` (R-REPO-02,
normative text in `spec/01` S-22).

## NON-NORMATIVE-CONTENT

- Rust code sketches of `EvalState`, frames, and step loops in the frozen source are
  specification artifacts (turn [25] frozen text), not repository code.
- The v0.3 transition-rule presentation (E-Let/E-Seq/E-If/E-Call, [16]) is an
  alternative rule-shaped statement of the same semantics (C-01 records numbering as
  presentation); the CEK table of turn [25] is the operative frozen form.
- "Value-return path" commentary and the deep-recursion motivation are explanatory.

## INPUTS

- `ExecutablePlan` — validated, immutable plans from MOD-02 (the only legal input;
  a `Block` has no path into `step()`, R-ARCH-03).
- `CapRef` handles and kernel verdicts via `authorize`/`derive` (MOD-03; the
  evaluator never sees `Authority`, `Scope`, `Rights`, parents, or revocation state —
  REQ-KERN-009).
- Budget gate verdicts and charges (MOD-04).
- Receipts for effect resumption and mailbox values for `Receive` (MOD-06/08/09).

## OUTPUTS

- Configuration transitions (`Σ → Σ'`), terminal values, and faults.
- `EvalStep::RequestEffect` intents (to MOD-08's request sequence — the *only* way an
  effect request exists).
- Spawn/Send/Receive intentions (to MOD-06), frame pushes/pops observable in traces
  (consumed by MOD-15's normalized observations).

## DEPENDENCIES

- Module dependencies: MOD-01 (`Expr`/`Value`/`Fault`/`Σ`), MOD-02 (input type),
  MOD-03 (kernel API), MOD-04 (gated transitions).
- Consumers: MOD-06 (actors are per-actor CEK states), MOD-08 (effect requests),
  MOD-14 (independent re-modeling), MOD-15 (observation source).
- Crate edge: `ror-runtime → ror-core, ror-kernel` (`spec/07` §6).
- Blocking open items: **U-04** (formal `await` retraction affects the frozen
  surface; with MOD-01), **U-02** (canonical encoding of frames/environments for
  snapshots blocks serializability evidence; with MOD-10/11), **U-01/U-07** (budget
  premises of call/request transitions), **U-40** (step-10 deadline predicate of
  request transitions — R-BUDGET-06's post-advance form vs REQ-EFFECT-012's weak
  form, `spec/06` C-104; with MOD-04/08).

## INVARIANTS

- Terminal iff continuation empty: `Value ∧ K = ε ⇒ Halt`; `Value ∧ K ≠ ε ⇒
  Resume(K, Value)` (R-CEK-02).
- Lexical capture: application resolves free variables in `ρ_closure`, never in
  `caller_env` (R-CEK-03/04/05).
- Left-to-right argument evaluation; arity prechecked before **any** argument
  evaluation (R-CEK-05).
- `|K'| − |K| ∈ {+1,−1}` per pure transition; no silent frame loss or duplication
  (R-CEK-06); continuation serialization must preserve the unevaluated suffix exactly
  (REQ-CEK-003, with MOD-11).
- Progress/preservation over well-typed, well-budgeted configurations (R-CEK-07).
- The evaluator has no host dependencies; its single side-effect vocabulary is
  `EvalStep::RequestEffect` (REQ-CEK-024).

## REQUIREMENTS

Canonical text: `spec/01` S-08. All 7 obligations `SPECIFIED`.

| ID | Obligation (short) | Provenance (`Red-on-Rust.md`) | Verification |
|---|---|---|---|
| R-CEK-01 | Explicit CEK; no recursive evaluation | L41484–41499, L37836–37854 | deep-call stress, R-TEST-01 |
| R-CEK-02 | Value-return invariant (terminal iff continuation empty) | L16878–16905, L37857–37886 | push/pop structural invariants |
| R-CEK-03 | Frozen frame set; closure env ≠ caller env | L16928–16958, L23821–23856 | `CEK-CLOSURE-LEXICAL-CAPTURE` |
| R-CEK-04 | Lambda: lexical capture, pure, value-return path | L16971–16995 | `CEK-CLOSURE-LEXICAL-CAPTURE` |
| R-CEK-05 | Call: LTR evaluation; arity precheck before args; closure-env application | L16878–16905, L37889–37927 | `CEK-CALL-ARITY-PRECHECK`, `CEK-CALL-ARGS-LTR`, M001, M002, M003 |
| R-CEK-06 | Continuation preservation (+1/−1 per entry/resume) | L14632–14642 | structural invariant tests |
| R-CEK-07 | Progress & preservation | L7273–7277, L8850 | differential equivalence |

Atomic registry records under this module: REQ-CEK-001…024 (incl. REQ-CEK-022 v0.3
E-Call budget premises, REQ-CEK-023 single pop path, REQ-CEK-024 zero host
dependencies — placed explicitly from the audit passes).
**7 obligations / 24 records.**

## SECURITY-BOUNDARY

The evaluator is a TCB member (R-TRUST-01) with a deliberately *narrow* authority:
it decides nothing about authority (MOD-03), resources (MOD-04), or the world
(MOD-09); it may only thread opaque handles through well-formed transitions. The
frozen traps are exactly the mutations that test its boundary: reversed evaluation
order (M001), skipped arity precheck (M002), and application of non-functions (M003)
each shift observable semantics without any type error; host-recursive stacks would
make continuation state unrecoverable (prohibited shortcut, R-CLAIM-02 #1).

## VERIFICATION-OBLIGATIONS

- Tags: `CEK-CALL-ARITY-PRECHECK` (0 arg evals / 0 host calls / 0 budget mutations on
  mismatch), `CEK-CALL-ARGS-LTR` (order observable in trace),
  `CEK-CLOSURE-LEXICAL-CAPTURE` (free vars in closure env; shadowing case).
- Mutations: M001, M002, M003 (registry owned by MOD-16).
- Conformance: M2 pure-subset differential (Value/Var/Let/Seq/If), M3 tag trio +
  deep-call stress (50k–100k), structural continuation invariants, progress/
  preservation exercised differentially (R-CEK-07 with MOD-15).
- Tracks: Track A includes scheduler-visible CEK step accounting; 15C comparison
  starts at terminal/event semantics over CEK traces (MOD-15).
- Milestone gates: M2, M3, and the first security gate R-ORDER-03 (7-form
  differential incl. faults, with MOD-02 and MOD-14/15).

## SOURCE-PROVENANCE

- Frozen CEK: [25] (L16861–18084), frame/value restatement [30] (L23821–23856),
  master prompt §4/§5 (L37836–37927, anchors corrected per `req/00-method.md` §5.1),
  continuation discipline [23] (L14632–14642), evaluator invariants [22]
  (L14313–14318).
- Canonical set: `spec/02` S-08; `req/01-registry-part2-semantics.md` (CEK block).

## CROSS-REFERENCES

Owned here, binding elsewhere:

- R-CEK-01/06 → MOD-11 (continuations must be snapshot-serializable; encoding gap
  U-02), MOD-17 (recursive-evaluator prohibition enforced by review, R-CLAIM-02).
- R-CEK-02/05 → MOD-14 (reference CEK must reproduce these exactly), MOD-15 (fault
  observations include premature-halt and order-of-arguments cases).
- R-CEK-02 value-return → MOD-08 (Pending is a *suspension*, not a terminal state —
  the request sequence's step 15 relies on this).

Owned elsewhere, binding EVALUATOR: R-ARCH-03 (MOD-01 central; operative
R-COMPILE-01/05 in MOD-02 — only `ExecutablePlan` enters), R-TRUST-03 (MOD-01
central; operative R-KERN-03 in MOD-03 — references only, no authority internals),
R-CALC-01/02/03/08 (MOD-01 — the term and configuration types), R-EFFECT-02 (MOD-08 —
every active transition is gated), R-BUDGET-06/08 (MOD-04 — time deltas and fault
replacement on gate failure). Open items: U-04 (with MOD-01), U-02 (machine-state
encoding, SERIALIZATION-side), U-07 (δ_t values, BUDGET-side), U-44 (request-frame
verification tags — REQUEST-ARGS-LTR / REQUEST-NON-CAP-SHORT-CIRCUIT are untagged;
MOD-08/17-side).
