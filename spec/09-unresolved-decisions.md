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
- **State of source:** the same denial outcome is named `CapabilityViolation`, `CapabilityRevoked`, `AuthorizationFailed`, and `Capability(CapabilityError)` in different frozen-era texts; `ScopeViolation` (v1) has no successor; the inner `CapabilityError` / `HostPolicyError` / `EffectError` / `HostFault` variants are not enumerated.
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
- **Decision needed:** fold into U-08's outcome (listed separately for traceability).

### U-15 — `ReconciliationOutcome` variants
- **Where:** R-RECOV-07.
- **State of source:** `EffectReconciled { outcome: ReconciliationOutcome }` is a frozen record kind, but the variant set of `ReconciliationOutcome` is never enumerated (beyond the classification of interrupted effects as `Indeterminate`). What outcomes can a host reconciliation legitimately produce (`Executed(result)`, `NotExecuted`, `PartiallyExecuted`…), and which are allowed per effect class (U-06)?
- **Decision needed:** the variant set + per-class admissibility.

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

## Process notes

1. Each resolution must be recorded as a **numbered frozen addendum** appended to the canonical spec (this document set), with a new requirement ID range, so that supersession is never silent (R-SCOPE-03, 00 §1).
2. U-01…U-06 are **blocking** for their components: U-01 (M5 budgeting of duration), U-02 (M7 persistence), U-03 (M6 spawn), U-04/U-05 (M2–M3 surface freeze confirmation), U-06 (M5 effect classes / M7 reconciliation).
3. The rest may be resolved incrementally before the corresponding milestone's evidence gate (M9/M10/M11) is declared.
4. A decision that *weakens* a security guarantee (e.g., allowing `NotExecuted` inference, unordered replay, saturating arithmetic) is out of scope for these items — those are prohibited outright (R-CLAIM-02).
