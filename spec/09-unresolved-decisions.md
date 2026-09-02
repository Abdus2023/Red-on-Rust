# 09 — Unresolved Items Requiring Explicit Architectural Decisions

Per the frozen rule (R-SCOPE-03): *"If implementation difficulty exposes an ambiguity, STOP and report it. Do not resolve semantic ambiguity by inventing behavior."* Each item below is a point where the frozen source text is genuinely under-determined or self-contradictory **after** all internal supersessions were applied. Each requires an explicit specification decision (a new frozen addendum) before the affected component may be implemented. **None of these may be "solved" by a test adjustment or an implementation choice** (R-TEST-09).

Status: all **OPEN**. Owner: specification authority (the party who can issue a frozen addendum).

---

## Blocking (must be decided before the affected component is implemented)

### U-01 — Operational meaning of the `duration` consumable (D)
- **Where:** R-BUDGET-01 (C-06).
- **State of source:** `D` is a consumable dimension (fuel, I/O, **duration**). The [15] freeze table explicitly left it "🔧 give operational meaning". The v0.3 text (L8683) keeps `D` but never states *how* `D` advances. `W` (deadline) is checked against logical time `t`; the relationship between `D` (a per-actor consumable) and `t`/`W` (global logical time + deadline) is unstated. Is `D` a count of steps-with-duration, decremented per transition by `δ`? Is it redundant with the deadline?
- **Decision needed:** a precise rule for `D` advancement and its interaction with `t`/`W`, or an explicit retraction of `D` as a distinct consumable. Until decided, implementations could legitimately differ in every budgeting decision.

### U-02 — Canonical encoding of machine (non-data) state is not frozen
- **Where:** R-PERSIST-04, R-RECOV-03, R-CANON-02 (C-14, C-15, C-16).
- **State of source:** 15A freezes byte-level grammar **only** for the data-value domain (`Value`, `Symbol`, `CapRef`, `ActorId`, `EffectId`). But a snapshot MUST durably encode `GlobalState` including `EvalState` (Expr, Environment, Continuation frames), `CapabilityContext`, `Authority` (the kernel-private grant behind each CapRef), heap, budget, mailbox, and scheduler state. **No byte-level encoding for any of these is specified**, yet:
  - R-PERSIST-05 requires a `state_digest` over the canonical snapshot (uncomputable without a canonical form);
  - R-RECOV-03 step (3) decodes the snapshot via 15A `CanonicalDecode`;
  - determinism/replay (R-CORE-08) requires byte-stable state.
  Additionally, the CapRef comment "never serialized directly" (C-14) contradicts the frozen CapRef tag and snapshot content on its face.
- **Decision needed:** freeze the canonical encodings (type tags + payload layouts) for `Expr`, `Frame`, `Environment`, `Constraint`, `Authority`/`AuthorityNode`, `CapabilityContext`, `Budget`, `Mailbox`, `SchedulerState`, `GlobalState` — or an explicit rule that these are derived deterministically from the frozen data-domain grammar plus stated ordering rules. Also freeze the **`Expr::Delegate` node itself**: the frozen Phase 13 delegation semantics (L25700, L25931, L37959) require a separate AST node, but the frozen `Expr` (L12145–12200) has no such constructor and no document defines its fields (its apparent shape `⟨capability, constraint⟩` is inference, not source text). Also resolve the CapRef "never serialized" comment (likely: never via *ordinary marshalling*; allowed for *persistence* — confirm).

### U-03 — Spawn budget-allocation policy (who decides `B_alloc`, and its bounds)
- **Where:** R-ACTOR-05 (C-24, source ambiguity A2).
- **State of source:** `Expr::Spawn { body, budget: BudgetAllocationSpec }` and `execute_spawn` call `budget_alloc.validate_and_escrow(&mut parent.budget)`. The *rules* of `validate_and_escrow` — maximum child share, minimum parent retention, whether the parent or the host/kernel chooses, how it interacts with the `R` reservation caps — are never stated. Source A2 warned: "If the parent chooses, a malicious parent could starve the child."
- **Decision needed:** the exact validation semantics of `BudgetAllocationSpec` (bounds, who supplies it, what faults on violation).

### U-04 — `await` constructor: formal retraction record
- **Where:** R-CALC-02 (C-04, source ambiguity A5).
- **State of source:** the v2 calculus lists `await(e)` as a constructor but gives it **no transition rule** and flags it as needing clarification (A5, L2326). Turn [10] §5 (L2718–2751) then explicitly decides: “Remove `await` from the Core Calculus” (redundant with `invoke`; the core becomes 11 constructors). The frozen `Expr` AST (turn [21]) is consistent with that decision — it omits `await` — and the constructor’s apparent roles (suspend on receipt / wait for message) are covered by effect `Pending` and blocking `Receive`. What is missing: **no frozen-phase document re-declares the elimination**; the retraction exists only in the turn-[10] exchange, not in any FROZEN section.
- **Decision needed:** a one-line frozen addendum formally recording the retraction (confirming the turn-[10] elimination as part of the frozen surface, per R-SCOPE-03’s no-silent-reinterpretation rule) — or a transition rule for `await` if it is to be retained. This is a documentation-confirmation item, not an open design question.

### U-05 — Isolation ladder (WASM / OS-process modes): retired or deferred?
- **Where:** R-CALC-02 / R-ACTOR-05 (C-19, C-36, source ambiguity A4).
- **State of source:** early design (turn [3], L1292–1313) and A4 specify spawn *isolation-level selection* (in-process / WASM / container) with capability gating ("an untrusted agent should not be able to spawn a child with weaker isolation than its own"). Every later frozen phase (12–15D) describes a purely **in-process** actor machine with the marshalling boundary, and the frozen `Spawn` has no isolation field. The ladder is never explicitly retired.
- **Decision needed:** an explicit addendum either (a) retiring the isolation ladder for the frozen machine (all actors in-process; marshalling is the isolation boundary), or (b) deferring it as a non-normative extension. This determines whether `Expr::Spawn` is complete as frozen.

### U-06 — Effect replayability/reversibility/idempotence: semantics of non-boolean values and link to effect classes
- **Where:** R-CALC-07, R-HOST-04 (C-05).
- **State of source:** the property table (v1 L2141–2156; v2 L3858–3873) declares a 4-valued domain `{yes, no, sometimes, depends}` and then fills cells with `n/a`, `usually`, `generally no`, `difficult` (none of which have defined operational meaning). Phase 14 later introduces *effect classes* (`EffectRecoveryClass`, L26669–26735: Replayable / Idempotent / Reversible / Indeterminate) which the recovery/replay rules actually use, but the mapping from the property table to the classes is never given, and it is never stated whether the table is normative.
- **Decision needed:** (1) is the per-operation property table normative or illustrative (this spec currently treats it as illustrative)? (2) the precise definition of the effect classes and how an effect's class is determined (static op table vs per-effect annotation); (3) the rule the ReplayHost and recovery use to decide "refuse to re-execute; return recorded result" vs "safe to re-issue".

## Required before the affected sub-component is complete (non-blocking for overall start)

### U-07 — Per-transition logical-time deltas
- **Where:** R-BUDGET-06.
- **State of source:** the rule is `δ_t(pure) = 0`, `δ_t(host/scheduler) > 0`, validity `t + δ_t ≤ W`. The *actual* delta values (is each scheduler turn `+1`? is each host round-trip `+1` or more? does spawning advance time?) are not enumerated in any frozen table.
- **Decision needed:** a frozen table of `δ_t` per transition kind (or a rule that any consistent assignment satisfying the stated constraints is conformant — which would need to be stated, since it changes what "deterministic" means for deadlines).

### U-08 — Fault taxonomy unification
- **Where:** R-CALC-06 (C-08).
- **State of source:** the same denial outcome is named `CapabilityViolation`, `CapabilityRevoked`, `AuthorizationFailed`, and `Capability(CapabilityError)` in different frozen-era texts; `ScopeViolation` (v1) has no successor; the inner `CapabilityError` / `HostPolicyError` / `EffectError` / `HostFault` variants are not enumerated. **Corrected in place (X-38, X-59, X-66, C-54…C-58):** the sentence above is kept verbatim as the superseded wording and is wrong on three counts. (1) The denial outcome carries **nine** verified names, not four — add `CapViolation` and `Revoked` (v1 fault grammar L1949), `Fault::CapabilityError` (L20389/L20790, asserted by a property test at L20538) and `CapabilityDenied` (L26870, turn [33], declared *after* the frozen L23806); the rename `CapabilityError`→`Capability` between turns [28] and [29] was never retracted. (2) Two of the four inner enums **are** declared: `pub enum CapabilityError` at L20408 (`Revoked`, `Expired`, `InvalidConstraint`, then `// ...`) and `pub enum HostFault` at L10820 (`IoError(String)`, `PolicyViolation(String)`); only `HostPolicyError` and `EffectError` have no declaration anywhere. (3) The frozen `Fault` set is **not** closed — L23807 is an explicit `// ... (previous faults)` elision — and `StalePlan`, asserted as a member by `spec/01` L138, REQ-CALC-014 and AMB-08, is in none of the seven `pub enum Fault` declarations (C-54 / X-64). Two further defects surfaced by the same audit and are folded into this decision: `CapabilityError::Invalid` (L20835) is used where the declared sibling is `InvalidConstraint` (L20451), for the same `derive` fallback in the same turn (C-56 / X-66); and `HostFault` is used with eight undeclared variant paths, six on the frozen replay path (C-57 / X-67, **BLOCKING**). `MarshalFault` has two disjoint declarations (C-55 / X-65).
- **Decision needed:** the exact `Fault`/error-variant set (names + when each is produced), so that differential observation (which compares faults, R-REF-05) is well-defined.

### U-09 — `Value` domain collision + orphaned `AdmissibleConstraint`
- **Where:** R-CALC-01 / R-CANON-04 / R-MARSHAL-03 (C-03, C-45, C-30).
- **State of source:** the machine `Value` (11 variants incl. `Function`, `Actor`, `Tuple`, `Bytes`) and the 15A canonical `Value` (8 variants incl. `Map`) share a name with incompatible variant sets; marshalling round-trip is stated for "all pure values" without saying which domain. Separately, the `AdmissibleConstraint` trait (L10171) appears once and is never referenced again.
- **Decision needed:** (1) name + relationship of the two value domains (e.g., `Value` = machine domain; `Data`/`BlockData` = canonical data domain), which one `marshal`/`15A` operate on, and the canonical encoding of machine-only variants if they must be persisted; (2) whether `AdmissibleConstraint` is part of the kernel contract or retired.

### U-13 — `PlannerMetadata` / `ProposalDigest` definitions + staleness check exactness
- **Where:** R-PLANNER-01, R-PLANNER-03, R-PLANNER-04 (C-38).
- **State of source:** `PlannerMetadata` fields are never defined; `ProposalDigest`'s canonical form (over what bytes?) is implied, not stated; the staleness check appears as both "verify `observation_sequence = current_planning_epoch`" (exact match) and "reject when `observation_sequence < current_sequence`" (inequality). These differ on edge cases.
- **Decision needed:** the `PlannerMetadata`/`ProposalDigest` definitions and the exact staleness predicate.

### U-14 — Error-variant enumeration (subset of U-08)
- **Where:** R-CALC-06.
- **Decision needed:** fold into U-08's outcome (listed separately for traceability). **Escalated by the terminology-normalization pass (X-65, X-66, X-67, C-55…C-57):** this is no longer a cosmetic enumeration task. `HostFault` is declared once (L10820, two variants) while eight undeclared variant paths are used, six of them on the frozen 15C.42 `ReplayHost` that R-HOST-03/04/05 and REQ-HOST-007/008 are written against, so the host error type cannot be written at all without inventing variants — **blocking** for Track A. `CapabilityError` is declared (L20408) but contradicted by its own use sites (`Invalid` L20835 vs `InvalidConstraint` L20451), and `MarshalFault` has two disjoint declarations (L10846 vs L25983). Only `HostPolicyError` and `EffectError` genuinely have no declaration.

### U-15 — `ReconciliationOutcome` variants
- **Where:** R-RECOV-07.
- **State of source (corrected — X-61):** this entry previously read: "`EffectReconciled { outcome: ReconciliationOutcome }` is a frozen record kind, but the variant set of `ReconciliationOutcome` is never enumerated (beyond the classification of interrupted effects as `Indeterminate`)." **That premise is false.** The variant set is enumerated at L26593–26597 as a closed three-variant set — `pub enum ReconciliationOutcome { Completed(EffectReceipt), NotExecuted, Indeterminate }` — and it matches exactly the three classifications the turn-[54] recovery text names (L38211 `Completed ⇒ Issued`, L38232 `Indeterminate`, L38243 `NotExecuted`). The variants this entry proposed (`Executed(result)`, `PartiallyExecuted`) do not exist in the frozen set, and implementing to them would widen a closed enum and break `WalRecord::EffectReconciled` (L35132) decoding against recorded traces. `req/03` AMB-15 withdrew the identical claim on the identical evidence and noted that this entry was wrong; `spec/09` had not absorbed the withdrawal. The earlier wording is quoted above rather than deleted so the supersession is not silent.
- **What remains open (narrowed):** *per-class admissibility*, not the variant set. Which effect classes (U-06) may legitimately yield `Completed` vs `NotExecuted` vs `Indeterminate`, given the frozen constraint that "only a host protocol capable of answering authoritatively may produce `NotExecuted` or `Completed`" (L26601) — i.e. what a non-authoritative protocol must return instead, and whether that is `Indeterminate` by obligation or a recovery fault.
- **Decision needed:** per-class admissibility of the three frozen variants. **Not** the variant set (closed, L26593–26597).
- **Linked:** `req/03` AMB-15 (withdrawn), U-06, `term/` T-51 `ReconciliationOutcome`, X-61, N-24.

### U-16 — `EventSequence` vs `WalSequence`
- **Where:** R-PERSIST-03, R-PERSIST-06.
- **State of source:** `EventEnvelope.sequence: EventSequence` (machine-level, in-memory log) and `WalFrame.sequence: WalSequence` (durable, "strictly monotonic", gap-checked as `s_{n+1} = s_n + 1`) both exist. Do effect records (Prepared/Issued/Completed/Reconciled) and SnapshotCommit consume the *same* sequence as events? If the WAL interleaves event records and effect records, is `WalSequence` a single total order across both, with `EventEnvelope.sequence` a projection? Unstated.
- **Decision needed:** the exact relationship (single WAL total order recommended by the source's own gap-check rule — confirm) and whether `EventEnvelope.sequence` equals the WAL sequence of its record.

### U-17 — Runnable queue: snapshot field vs recovery reconstruction
- **Where:** R-PERSIST-04 / R-RECOV-03 (C-26).
- **State of source:** the snapshot is said to contain the runnable queue, and recovery step 10 says "reconstruct runnable queue from actor states". Which is authoritative if they disagree? (Reconstruct-then-validate is the safer reading but is not stated.)
- **Decision needed:** one sentence: the snapshot's queue is the base; reconstruction is a validation cross-check, mismatch ⇒ `RecoveryFault`.

### U-21 — `Op` / `Target` / `Params` domains
- **Where:** R-CALC-04, R-CAP-01.
- **State of source:** `O` is "a finite, enumerable set of atomic actions (e.g., `FileRead`, `NetSend`)" — the examples are explicitly illustrative. `Target` and `Params` have no domain definition beyond "scope interpretation" and "predicate domain" in the algebra. The canonical encoding of `Op`/`Target`/`Params` (needed for `EffectDigest`, R-CALC-04) is not in the 15A tag set (also U-02).
- **Decision needed:** the canonical representation of `Op` (enum? interned symbol?), `Target`, `Params` (typed record? key-value?), and their canonical encoding.

### U-22 — Static effect-set inference (J2) not present in the frozen pipeline
- **Where:** R-COMPILE-03 (C-35).
- **State of source:** v1 defined judgment J2 (effect inference `Γ ⊢ e ↝ Φ`, conservative over-approximation) and the compilation theorem used it. The frozen compiler pipeline (parse → normalize → validate → lower → **capability analysis** → **resource analysis**) has no explicit "effect-set inference" stage, and the combined judgment's `F` component is not re-derived in any pipeline stage.
- **Decision needed:** confirm whether effect-set inference is part of "validate" or "capability analysis" (and what it must produce), or retracted as an optimization — this affects what the compiler must guarantee at the boundary.

---

## Blocking decisions added by the terminology-normalization pass

Three BLOCKING terminology collisions require an explicit architectural decision and were not previously in this register. They are numbered on from U-22 and filed here rather than in the sections above so that the line numbers cited by existing records (notably U-15, corrected at X-61) do not move. Each carries its `term/02-collisions.md` `X-` id and its `spec/06` row; per process note 1, a resolution must be recorded as a numbered frozen addendum so the supersession is not silent.

### U-23 — Is `ValidatedPlan` a type, a predicate, or both?
- **Where:** R-CORE-02 (`spec/01` L25), the second of the two governing invariants; S-06; S-22.
- **State of source:** `pub struct ValidatedPlan { ir: PlanIR, effects: EffectSet }` (L865, turn [3]) is a stage artifact private to `mod compiler`. The central theorem is boxed as `ExternalEffect(E) ⇒ ValidatedPlan(P) ∧ Authorized(E,κ,t) ∧ …` (L41337–41351, L27491–27509), where `ValidatedPlan(·)` is a **predicate over `P`**. No predicate of that name is defined anywhere, and no rule states when the struct satisfies it. `spec/01` L27 (R-CORE-03) uses a different arity again for `Authorized`.
- **Decision needed:** either (a) define `ValidatedPlan(P)` as a predicate — over what domain, with what witness — and state its relationship to the struct, or (b) restate R-CORE-02 with a predicate name the source does not already use as a type. Option (b) changes a boxed invariant, so it is a frozen-addendum decision, not an editorial one. Neither the struct nor the theorem may be silently renamed.
- **Linked:** C-46, `term/` X-01 (BLOCKING), X-04, X-05, T-04, N-01, N-06.
- **Blocking:** yes — for any mechanization or conformance test of the external-effect chain.

### U-24 — Which canonical envelope is frozen?
- **Where:** R-CANON-01…R-CANON-08 (S-17), R-PERSIST-05, milestone M1.
- **State of source:** two incompatible specifications. The `CanonicalSerialize` doc comment gives `[format_version: u8] [type_tag: u32 LE] [length: u32 LE] [payload]` (L28298, turn [36]). The 15A grammar, the 15B frame and the turn-[54] master prompt give `version: u8 | type_tag: u8 | payload_length: u32 BE | payload` (L38147–38150, L33816, L29905, L35102). They differ in field *name*, tag *width* and *endianness*.
- **Decision needed:** confirm that the big-endian `u8`-tag form governs and that the L28298 doc comment is superseded — then record it as a frozen addendum, because the contradiction sits inside an API contract comment rather than in narrative prose, and an implementer will read the comment first. Every digest in the system (`EffectDigest`, `StateDigest`, `ResultDigest`, WAL frame checksums, snapshot determinism) hashes these bytes.
- **Linked:** C-47, `term/` X-50 (BLOCKING), X-51, T-62, T-63. Distinct from C-02, which concerns stale *primitive* tags in one section.
- **Blocking:** yes — for milestone M1 and for any golden vector.

### U-25 — Two tag namespaces share the `TAG_*` prefix; which constants may an implementation import?
- **Where:** R-CANON-03, R-CANON-04, 15C.36 (canonical-serialization differential boundary), milestone M1.
- **State of source:** envelope type tags `TAG_VALUE 0x00`, `TAG_BOOL 0x10`, `TAG_INTEGER 0x11`, `TAG_STRING 0x12`, `TAG_SYMBOL 0x20`, `TAG_CAPREF 0x30`, `TAG_VEC 0x40`, `TAG_BTREEMAP 0x41` (L29951–29958, turn [41]); `Value` variant discriminants `TAG_BOOL 0x01`, `TAG_INTEGER 0x02`, `TAG_STRING 0x03`, `TAG_SYMBOL 0x04`, `TAG_CAPABILITY 0x05`, `TAG_LIST 0x06`, `TAG_MAP 0x07` (L32364–32371 turn [43]; L33171–33173 and L33591–33594 turn [45]). Four names carry two values each. Turn [41] used the prefix `DISC_` for discriminants (L29961–29965) and gave `Capability` the byte `0x0A`, contradicting `0x05`; its table headed "(Frozen)" also omits `Symbol`, `List` and `Map` entirely. The frozen `Value::Symbol` decoder needs both namespaces in one function (L33194–33195).
- **Decision needed:** the module paths under which each namespace is imported, and confirmation that the dense `0x00`–`0x07` discriminant set governs. No constant may be renamed: both sets are frozen identifiers, and renaming either changes a byte value that digests depend on.
- **Linked:** C-48, C-49, `term/` X-54 (BLOCKING), X-55, X-56, T-31, T-62, T-63; extends C-02 and C-15.
- **Blocking:** yes — for milestone M1.
---

## Decisions added by the declaration sweep

Four further decisions come from the sweep that checked every `Enum::Variant` path in `Red-on-Rust.md` L1–42312 against every declaration of that enum (`term/` X-69…X-75, `spec/06` C-59…C-65). Like U-23…U-25 they are filed in their own section so that the line numbers cited by existing records do not move. None is settled by the source, and none can be settled by renaming: every identifier below is frozen.

### U-26 — Which layer owns the name `StepResult`?
- **Where:** R-CEK-01 (S-07), R-ACTOR-04 (S-15); `term/` T-77.
- **State of source:** two disjoint enums share the name and have no variant in common. L1006 (turn [3]) is the CEK machine's step outcome — `Continue`, `Halt(Value)`, `Fault(Fault)`, `YieldToHost(Effect)` — and carries no identity. L9586 (turn [17]), restated at L10397 and L10947 (turn [18]), is the actor scheduler's — `Progressed`, `Blocked(ActorId)`, `Pending(ActorId, EffectRequest)`, `Halted(ActorId, Value)`, `Faulted(ActorId, Fault)`, `NoRunnableActors` — and every variant carries an `ActorId`. Neither declaration mentions the other, and the source offers no second name for either.
- **Decision needed:** which layer keeps `StepResult` and what the other layer's step outcome is to be called — this cannot be settled by citation because no alternative name exists in the source; and whether prose must distinguish the machine's `Fault(Fault)` from the scheduler's `Faulted(ActorId, Fault)` by layer or by name, given that X-23 already records the same `Faulted`/`Fault` split inside `RunState`.
- **Linked:** C-63, `term/` X-73, X-23, T-77, T-70, T-35, T-36.
- **Blocking:** yes — for any conformance test that asserts on a step outcome. The two enums do not compile against each other, so a fixture written from one turn fails against an implementation written from another.

### U-27 — Which `ActorStatus` shape governs, and where does shape (iii)'s continuation live?
- **Where:** R-ACTOR-02, R-ACTOR-04 (S-15); `term/` T-35.
- **State of source:** seven declarations in three shapes. (i) L9411 (turn [17]) and L10346 (turn [18]): `Pending(PendingEffect), Blocked(Continuation)` — the continuation inside `Blocked`. (ii) L21234 (turn [29]): `Pending { effect: EffectRequest, continuation: Continuation, reservation: ReservedCapacity }, Blocked(Continuation)` — the continuation in both variants. (iii) L23306 and L23793 (turn [30]): `Pending { effect: EffectRequest, reservation: ReservedCapacity }, Blocked` — the continuation in neither, which is the form the frozen turn-[30] machine assumes when it keeps the continuation in `actor.eval.continuation`. X-21 separately records the `Running`/`Active` naming split; this decision is about shape, not naming.
- **Decision needed:** which shape governs, and — under shape (iii) — where the continuation is held and how it is persisted, since an actor in `Pending { effect, reservation }` cannot be resumed from its own status. Whether it lives in the actor table, the WAL or a `ContinuationFrame` determines what a snapshot must contain (U-17 is adjacent) and what recovery must reconstruct.
- **Linked:** C-64, `term/` X-74, X-21, X-22, T-35, T-37, T-32, T-45; adjacent to U-17.
- **Blocking:** yes — for replay and recovery conformance, and for any test that resumes a blocked actor.

### U-28 — Which `MachineEvent` names govern, and are the eight undeclared paths declared or struck?
- **Where:** R-CORE-08, R-ACTOR-07, R-REF-05; `term/` T-75, T-47, T-45.
- **State of source:** eight declarations — L14697 (turn [23]), L15958 (turn [24]), L17588 (turn [25]), L18104 and L18631 (turn [26]), L20318 and L20724 (turn [28]), L22002 (turn [29]) — three of which elide their heads (`// ... (Previous events)` L20319, `// ... (previous variants)` L20725, `// ...` L22003), and none of which carries a supersession note. Eight further variant paths are used and declared by none: `EnterRequest` (L21483, L23380), `BeginRequestTarget` (L21536, L23398), `BeginRequestArgument` (L21645, L23426), `Blocked` (L25740, L26038), `Spawned` (L25668), `ActorSpawned` (L25966), `Sent` (L25728), `MessageSent` (L26027). Three of them are second names for an event the source also names another way: `Blocked` against the declared `Block`, and `Spawned`/`ActorSpawned`, `Sent`/`MessageSent` as pairs; the three `*Request*` events resemble the declared `BeginArgument`/`EndArgument` pair without matching it.
- **Decision needed:** whether the event vocabulary is the union of all eight declarations or only the last; one name for each duplicate pair; and whether the three request events and the four actor/message events are to be declared or struck. The choice is observable: `MachineEvent` is what the WAL records and what the differential observer compares, so two implementations that pick different names report a divergence that is a naming artifact rather than a semantic one.
- **Linked:** C-61, `term/` X-71, T-75, T-47, T-45, T-70; extends the U-02 family (machine-state encodings).
- **Blocking:** yes — for trace-equality, WAL-format and differential tests.

### U-29 — Which `CanonicalError` shape governs, and do the unit variants survive?
- **Where:** R-CANON-01, R-CANON-02 (S-17); `term/` T-76, T-62, T-63.
- **State of source:** seven declarations in four materially different shapes — L29188 (turn [38], five unit variants), L29968 (turn [41], seven variants with `Utf8Error` and `PayloadTooShort` where the others say `InvalidUtf8` and `UnexpectedEof`, plus `LengthOverflow` which the first lacks), L30661 (turn [41], nine payload-bearing struct variants such as `InvalidVersion { expected: u8, found: u8 }` and `LengthMismatch { expected: u32, found: usize }`), L32083 (turn [43]), L32959 and L33299 (turn [45]), and L34994 (turn [47], head elided as `// ... previous variants`, adding `DuplicateMapKey` — “NEW: Enforces strict injectivity”). The same variant name therefore occurs as a unit variant and as a struct variant with different arities.
- **Decision needed:** which shape governs; whether the payload-bearing forms supersede the unit forms or both remain legal; which spelling governs each respelled pair; and whether `LengthOverflow` and `DuplicateMapKey` are in the governing set — `DuplicateMapKey` is the only variant that enforces map injectivity, so whether canonical encoding rejects duplicate keys at all currently depends on which declaration an implementer reads.
- **Linked:** C-62, U-24, U-25, `term/` X-72, X-50, T-76, T-62, T-63; extends U-14 (error-variant enumeration).
- **Blocking:** yes — for milestone M1 and for any golden vector, on the same path as U-24 and U-25.
---


### U-30 — Which payload does `MarshalledValue` carry — `Value` or canonical `Vec<u8>`?
- **Where:** R-MARSHAL-01, R-MARSHAL-02, R-MARSHAL-03, R-ACTOR-03 (S-15…S-17); `term/` T-79, T-39, T-31.
- **State of source:** five declarations in two payloads — `MarshalledValue(Value)` at L9925 (turn [17]), L10828 (turn [18], with `new(v: Value)` at L10831 and `into_inner(self) -> Value` at L10832) and L24765 (turn [31]); `MarshalledValue(pub Vec<u8>)` at L25683 and `MarshalledValue(Vec<u8>)` at L25981 (turn [32]), built by `canonical_serialize` at L25690 and called 'an opaque, canonical byte representation' at L25980. No supersession note connects them.
- **Decision needed:** which payload governs; whether the frozen `new`/`into_inner` API survives (it cannot type-check over bytes) or the `canonical_serialize` constructor does; whether the payload is `pub` (L25683) or private/opaque (L25980–25981); and, if bytes, which canonical encoding — U-02 records that no canonical byte encoding is frozen for machine state, and C-15 that none is frozen for `Mailbox`.
- **Linked:** C-66, C-15, U-02, `term/` X-76, X-50, X-65, T-79, T-39.
- **Blocking:** yes — for milestone M1's actor-isolation path and for any golden vector that encodes a mailbox.
---

### U-31 — Which field set is `Authority`'s, which is `Constraint`'s, and what holds the kernel's arena?
- **Where:** R-CAP-01…R-CAP-04, R-KERN-01…R-KERN-03 (S-09, S-10); law N-28; `term/` T-10, T-11, T-12, T-13.
- **State of source:** `Authority` is declared seven times in six field sets (L488, L918 — a revocation node; L3591, L4360, L4979 — a permission set; L5368 — the two merged; L6501 — a map to `OpAuthority`), and `Constraint` twice in the same turn: L6536 with a body character-for-character identical to L6501's under the comment 'Constraint: distinct from Authority', and L6686 with the five-field shape `Authority` has at L4360. The kernel's arena holds `Authority` (L927, L5430), `RuntimeAuthority` (L3657, L5044) or `AuthorityNode` (L6696) in `SlotMap` or `GenerationalArena`; `revocation_set` is `HashSet<DefaultKey>` (L928, L5431), `HashSet<CapRef>` (L6697) or absent (L3656, L5044), with the in-source comment 'Or epoch-based generation tracking'; `children` exists only at L5432.
- **Decision needed:** which `Authority` field set governs and which `Constraint` field set governs, given that N-28's required distinction is contradicted by L6536's body; whether the revocation node is `Authority`, `RuntimeAuthority` or `AuthorityNode` and whether it carries `generation`; which container and value type the kernel's arena has; whether revocation is tracked by a set of slot keys, a set of `CapRef`s, or epoch-based generations; and whether `children` (cascading revocation) exists.
- **Linked:** C-67, C-72, C-25, U-02, `term/` X-77, X-82, X-37, X-25, N-28, T-10, T-11, T-12, T-13.
- **Blocking:** yes — for the capability algebra's milestone gate and for `CAP-DERIVE-NO-AMPLIFICATION` (M006), which has no type-level support while the two types are structurally identical.
---

### U-32 — Does the durable `WalFrame` carry `payload_length`, and what is its checksum's input domain?
- **Where:** R-PERSIST-01, R-PERSIST-02 (S-18); `term/` T-45, T-46, T-47.
- **State of source:** L34237–34242 (turn [46]) declares four fields — `sequence`, `kind`, `payload`, `checksum` — with no stated checksum domain; L35099–35105 (turn [47]) declares five, adding `payload_length: u32` marked 'Big-endian, checked', and fixes the checksum as `SHA-256(sequence || kind || payload_length || payload)`. The turn-[47] parser rule at L35109 requires rejection of 'truncated headers, truncated payloads, impossible lengths', which presumes a length field. `kind`'s type `WalRecordKind` is declared nowhere, and `GlobalSnapshot.last_effect_sequence: EffectSequence` (L26305, L34126) uses a third sequence name that is also undeclared.
- **Decision needed:** whether the frame carries `payload_length`; whether the checksum covers it (so every turn-[46] digest is invalid) or the four-field concatenation; whether the header is big-endian while the canonical envelope is little-endian (U-24, C-47) and where that boundary falls; what `WalRecordKind`'s variants are; and whether `EffectSequence` is a third sequence domain or a misspelling of `EventSequence`.
- **Linked:** C-70, C-47, U-16, U-24, `term/` X-80, X-31, X-47, X-50, X-84, T-46.
- **Blocking:** yes — for any recovery test and for every golden WAL vector; a format whose checksum domain is undecided cannot be written or verified.
---

### U-33 — Which reference-model declarations govern, and are its undeclared types declared or struck?
- **Where:** R-REF-01…R-REF-06 (S-20); `term/` T-58, T-80, T-81.
- **State of source:** `RefState` is `{ expr: Expr, env: Environment, kont: Vec<Frame>, outcome: RefOutcome }` at L14728, L15985, L16423 (turns [23], [24]) and `{ expr: RefExpr, env: RefEnv, continuation: Vec<RefFrame> }` at L35522 (turn [48]). `RefAuthority` has four declarations in three shapes (L11572 `ops: HashSet<Op>`; L19603 `operations: BTreeMap<Op, RefOperationAuthority>`; L20851 `operations: BTreeSet<Op>` plus four `Ref*` components; L35699 `operations: BTreeMap<RefOp, RefOperationAuthority>`), and the frozen `reference_derive` body at L11579–11583 reads `.ops` and calls `.intersection()`. Twelve `Ref*` type names are used in these declarations and declared nowhere: `RefExpr`, `RefOp`, `RefScope`, `RefConstraint`, `RefResources`, `RefLifetime`, `RefFunction`, `RefEvent`, `RefHeap`, `RefMessage`, `RefCapabilityContext`, `RefRecoveryFault`.
- **Decision needed:** which `RefState` shape the differential observer compares — the production-typed form C-33 forbids, or the independent form whose `RefExpr` is undeclared — and whether it carries `outcome`; which `RefAuthority` shape `reference_derive` is written against, given that its frozen body only type-checks against the turn-[20] set form; whether the reference model's key type is the production `Op` or `RefOp`; and whether the twelve undeclared `Ref*` types are to be declared in `ror-reference` or struck in favour of production types (which C-33 forbids).
- **Linked:** C-68, C-69, C-74, C-33, `term/` X-78, X-79, X-84, X-22, T-80, T-81.
- **Blocking:** yes — R-REF-05's differential observer is the project's central verification instrument and has no fixed left-hand side until this is ruled.
---

### U-34 — Which turn-[31]/turn-[32] state structs govern — `run_state`, `members` and `scheduler`?
- **Where:** R-ACTOR-01…R-ACTOR-07, R-PERSIST-04, R-CORE-08 (S-15, S-18); `term/` T-36, T-37, T-38, T-39, T-40.
- **State of source:** `GlobalState` carries `scheduler: SchedulerState` at L24168 (turn [31]) and not at L25535 or L25862 (turn [32]). `ActorState` gains `run_state: RunState` at L25546 (turn [32]) while keeping `status: ActorStatus` at L25552, and the same turn's other declaration (L25871) has `status` only. `RunnableQueue` is `{ queue: VecDeque<ActorId> }` at L24275 (turn [31]) and adds `members: BTreeSet<ActorId>, // Enforces "at most once" invariant` at L25894 (turn [32]). `ActorState.mailbox` is `Mailbox` at L9438 (turn [17]), `VecDeque<MarshalledValue>` at L10360 (turn [18]) and `Mailbox` again at L10892.
- **Decision needed:** whether `GlobalState` carries `scheduler` (and therefore whether `GlobalSnapshot.machine_state` persists scheduler state, which U-17's recovery question turns on); whether `ActorState` carries `run_state`, `status`, or both, and which one governs a blocked actor; whether `RunnableQueue` carries `members`, and if not how R-ACTOR-04's at-most-once invariant — mutation M012's target — is enforced; and whether `mailbox` is the abstract `Mailbox` or an inline `VecDeque<MarshalledValue>` (which U-30's payload question then decides the element type of).
- **Linked:** C-73, C-65, C-66, U-17, `term/` X-83, X-75, X-76, X-23, T-37, T-38, T-40.
- **Blocking:** yes — for the scheduler's milestone gate, for M012, and for any snapshot/recovery test.
---

## Process notes

1. Each resolution must be recorded as a **numbered frozen addendum** appended to the canonical spec (this document set), with a new requirement ID range, so that supersession is never silent (R-SCOPE-03, 00 §1).
2. U-01…U-06 are **blocking** for their components: U-01 (M5 budgeting of duration), U-02 (M7 persistence), U-03 (M6 spawn), U-04/U-05 (M2–M3 surface freeze confirmation), U-06 (M5 effect classes / M7 reconciliation).
3. The rest may be resolved incrementally before the corresponding milestone's evidence gate (M9/M10/M11) is declared.
5. U-23, U-24 and U-25 were added by the terminology-normalization pass (`term/`). All three are **blocking**: U-23 for any mechanization of the external-effect chain, U-24 and U-25 for milestone M1. They are filed in their own section so that the line numbers cited by existing records do not move; U-15 above was corrected in place on the same pass (X-61).
6. U-26, U-27, U-28 and U-29 were added by the same pass's **declaration sweep**, which checked every `Enum::Variant` path in the frozen source against every declaration of that enum. All four are blocking for a conformance test rather than for a milestone gate: U-26 and U-27 for any test that asserts on a step outcome or resumes a blocked actor, U-28 for trace-equality and differential tests, U-29 for milestone M1 alongside U-24 and U-25. They are filed in their own section for the same reason as U-23…U-25 — so that the line numbers cited by existing records do not move.
4. A decision that *weakens* a security guarantee (e.g., allowing `NotExecuted` inference, unordered replay, saturating arithmetic) is out of scope for these items — those are prohibited outright (R-CLAIM-02).
