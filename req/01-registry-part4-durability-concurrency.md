# Atomic Requirement Registry — Part 4: Durability, Host, Concurrency (S-13 … S-16)

Areas: `DUR` (14), `HOST` (14), `ACTOR` (35), `MARSHAL` (10) — 73 atomic units.

---

## S-13 Transactional issuance and durability boundary

### REQ-DUR-001
- REQ-ID: REQ-DUR-001
- CATEGORY: durability
- SOURCE: Red-on-Rust.md L38050([54] §8); L35147–35156([47]); L38217–38221([54] §12); L41612–L41616([60] restated [60]); L34035–L34041([46] issuance boundary); spec/01 S-13 R-DUR-01
- NORMATIVE-LEVEL: MUST NOT
- STATEMENT: `HostInvoked(E) ⇒ DurableIssued(E)`; the machine MUST NEVER invoke the host before the durable issuance boundary.
- PRECONDITIONS: any host invocation
- POSTCONDITIONS: the `Issued` record for `E` is durable first
- INVARIANTS: `HostInvoked(E) ⇒ DurableIssued(E)`
- DEPENDENCIES: REQ-DUR-002, REQ-CORE-007
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: `EFFECT-ISSUE-DURABLE-BEFORE-HOST`; `PanicHost`; crash points T0–T4
- EVIDENCE-STATUS: SPECIFIED

### REQ-DUR-002
- REQ-ID: REQ-DUR-002
- CATEGORY: durability
- SOURCE: Red-on-Rust.md L35150–35158([47]); spec/01 S-13 R-DUR-02
- NORMATIVE-LEVEL: MUST
- STATEMENT: The issuance transaction occurs in this strict order: (1) pure validation/authorization/budget checks; (2) `persistence.append(EffectPrepared { id, actor, digest })`; (3) `persistence.sync()`; (4) `persistence.append(EffectIssued { id, actor, digest })`; (5) `persistence.sync()`; (6) machine transitions actor to `Pending`; (7) host adapter receives `EffectRequest`.
- PRECONDITIONS: an effect passes all gates
- POSTCONDITIONS: the seven steps occur in order
- INVARIANTS: — (ordered transaction; kept whole per rule 6)
- DEPENDENCIES: REQ-DUR-003, REQ-DUR-004, REQ-EFFECT-016, REQ-EFFECT-017
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: crash harness T0–T4
- EVIDENCE-STATUS: SPECIFIED

### REQ-DUR-003
- REQ-ID: REQ-DUR-003
- CATEGORY: durability
- SOURCE: Red-on-Rust.md L35152–35153([47]); L1377–1382([4]); spec/01 S-13 R-DUR-02
- NORMATIVE-LEVEL: MUST
- STATEMENT: `EffectPrepared` is fsynced before `EffectIssued` is appended.
- PRECONDITIONS: step 2 completed
- POSTCONDITIONS: the `Prepared` record is on stable storage
- INVARIANTS: —
- DEPENDENCIES: REQ-DUR-002
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: crash point T1 (after `Prepared`)
- EVIDENCE-STATUS: SPECIFIED

### REQ-DUR-004
- REQ-ID: REQ-DUR-004
- CATEGORY: durability
- SOURCE: Red-on-Rust.md L35154–35155([47]); L1697–1705([4]); spec/01 S-13 R-DUR-02
- NORMATIVE-LEVEL: MUST
- STATEMENT: `EffectIssued` is fsynced before the actor becomes `Pending` and before any host call.
- PRECONDITIONS: step 4 completed
- POSTCONDITIONS: the `Issued` record is on stable storage
- INVARIANTS: `HostInvoked(E) ⇒ DurableIssued(E)`
- DEPENDENCIES: REQ-DUR-002, REQ-DUR-001
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: crash points T2–T4
- EVIDENCE-STATUS: SPECIFIED

### REQ-DUR-005
- REQ-ID: REQ-DUR-005
- CATEGORY: durability
- SOURCE: Red-on-Rust.md L38203–38207([54] §12); L35111–35144([47]); L33979([46] causal chain); spec/01 S-13 R-DUR-03
- NORMATIVE-LEVEL: MUST
- STATEMENT: `Issued(E) ⇒ Prepared(E)`.
- PRECONDITIONS: an `Issued` record exists
- POSTCONDITIONS: a `Prepared` record for the same effect exists
- INVARIANTS: `Issued(E) ⇒ Prepared(E)`
- DEPENDENCIES: REQ-DUR-002
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: journal validator; mutation M017-class
- EVIDENCE-STATUS: SPECIFIED

### REQ-DUR-006
- REQ-ID: REQ-DUR-006
- CATEGORY: durability
- SOURCE: Red-on-Rust.md L38209–38211([54] §12); L35111–35144([47]); L26156–26170([33]); L33983([46] causal chain); spec/01 S-13 R-DUR-03; spec/06 C-44
- NORMATIVE-LEVEL: MUST
- STATEMENT: `Completed(E) ⇒ Issued(E)`.
- PRECONDITIONS: a `Completed` record exists
- POSTCONDITIONS: an `Issued` record for the same effect exists
- INVARIANTS: `Completed(E) ⇒ Issued(E)`
- DEPENDENCIES: REQ-EFFECT-034
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: journal causal-chain validation
- EVIDENCE-STATUS: SPECIFIED

### REQ-DUR-007
- REQ-ID: REQ-DUR-007
- CATEGORY: durability
- SOURCE: Red-on-Rust.md L38213–38215([54] §12); L35111–35144([47]); L33987([46] causal chain); spec/01 S-13 R-DUR-03
- NORMATIVE-LEVEL: MUST
- STATEMENT: `Reconciled(E) ⇒ Issued(E)`.
- PRECONDITIONS: an `EffectReconciled` record exists
- POSTCONDITIONS: an `Issued` record for the same effect exists
- INVARIANTS: `Reconciled(E) ⇒ Issued(E)`
- DEPENDENCIES: REQ-RECOV-015
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: journal causal-chain validation
- EVIDENCE-STATUS: SPECIFIED

### REQ-DUR-008
- REQ-ID: REQ-DUR-008
- CATEGORY: durability
- SOURCE: Red-on-Rust.md L35140–35144([47]); L26156–26170([33]); spec/01 S-13 R-DUR-03
- NORMATIVE-LEVEL: MUST
- STATEMENT: Every subsequent record for an effect MUST carry the identical `EffectId` and `EffectDigest`.
- PRECONDITIONS: any `Prepared`/`Issued`/`Completed`/`Reconciled` record
- POSTCONDITIONS: both identifiers equal those of the originating effect
- INVARIANTS: —
- DEPENDENCIES: REQ-CALC-008, REQ-DUR-009
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: journal validator; mutation M017
- EVIDENCE-STATUS: SPECIFIED

### REQ-DUR-009
- REQ-ID: REQ-DUR-009
- CATEGORY: durability
- SOURCE: Red-on-Rust.md L35140–35144([47]); spec/01 S-13 R-DUR-03
- NORMATIVE-LEVEL: MUST
- STATEMENT: A digest mismatch is `EffectJournalCorruption`, not a different effect.
- PRECONDITIONS: a journal record's digest does not match the effect's
- POSTCONDITIONS: corruption is reported; the record is not reinterpreted
- INVARIANTS: —
- DEPENDENCIES: REQ-DUR-008; AMB-08 (`EffectJournalCorruption` is not a variant of the frozen `Fault` enum)
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: journal corruption negative tests
- EVIDENCE-STATUS: SPECIFIED

### REQ-DUR-010
- REQ-ID: REQ-DUR-010
- CATEGORY: durability
- SOURCE: Red-on-Rust.md L38222–38226([54] §12); L35159–35176([47]); L26592–26598([33]); L41736([60] restated [60]); spec/01 S-13 R-DUR-04
- NORMATIVE-LEVEL: MUST
- STATEMENT: `Prepared ∧ ¬Issued ⇒ Discard`; incomplete preparation is rolled back and the budget restored.
- PRECONDITIONS: recovery finds `Prepared` with no `Issued`
- POSTCONDITIONS: the preparation is discarded; budget restored; execution resumes normally
- INVARIANTS: `Prepared ∧ ¬Issued ⇒ Discard`
- DEPENDENCIES: REQ-RECOV-004
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: crash point T1; `RECOVERY-ISSUED-INDETERMINATE` suite
- EVIDENCE-STATUS: SPECIFIED

### REQ-DUR-011
- REQ-ID: REQ-DUR-011
- CATEGORY: durability
- SOURCE: Red-on-Rust.md L38228–38240([54] §12); L35159–35176([47]); spec/01 S-13 R-DUR-04
- NORMATIVE-LEVEL: MUST
- STATEMENT: `Issued ∧ ¬Completed ⇒ Indeterminate`.
- PRECONDITIONS: recovery finds `Issued` with no durable `Completed`
- POSTCONDITIONS: the effect is classified `Indeterminate` and routed to reconciliation
- INVARIANTS: `Issued ∧ ¬Completed ⇒ Indeterminate`
- DEPENDENCIES: REQ-CORE-014, REQ-RECOV-015
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: `RECOVERY-ISSUED-INDETERMINATE`; crash points T2–T4
- EVIDENCE-STATUS: SPECIFIED

### REQ-DUR-012
- REQ-ID: REQ-DUR-012
- CATEGORY: durability
- SOURCE: Red-on-Rust.md L38241–38248([54] §12); L37968–37981([54] master prompt); L41751([60] restated [60]); spec/01 S-13 R-DUR-04
- NORMATIVE-LEVEL: MUST NOT
- STATEMENT: An `Issued ∧ ¬Completed` effect is NEVER automatically classified `NotExecuted`; the host may have executed it.
- PRECONDITIONS: recovery or reconciliation considers an interrupted effect
- POSTCONDITIONS: no automatic "not executed" resolution
- INVARIANTS: —
- DEPENDENCIES: REQ-CORE-014, REQ-CLAIM-009
- SECURITY-IMPACT: critical (re-issuing an executed effect duplicates a real-world side effect)
- VERIFICATION-METHOD: crash points T2–T4 with exact classification
- EVIDENCE-STATUS: SPECIFIED

### REQ-DUR-013
- REQ-ID: REQ-DUR-013
- CATEGORY: durability
- SOURCE: Red-on-Rust.md L35210–35215([47]); spec/01 S-13 R-DUR-05
- NORMATIVE-LEVEL: MUST
- STATEMENT: An `Issued` effect with no durable completion retains its `completion_maximum` in the `escrowed` partition until reconciliation determines the outcome.
- PRECONDITIONS: an effect is `Issued` and not completed
- POSTCONDITIONS: the escrow remains allocated
- INVARIANTS: `C_available + C_escrowed + C_consumed = C_initial`
- DEPENDENCIES: REQ-BUDGET-024, REQ-RECOV-013
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: `BUDGET-ESCROW-CONSERVATION`; mutation M008
- EVIDENCE-STATUS: SPECIFIED

### REQ-DUR-014
- REQ-ID: REQ-DUR-014
- CATEGORY: durability
- SOURCE: Red-on-Rust.md L35210–35215([47]); spec/01 S-13 R-DUR-05
- NORMATIVE-LEVEL: MUST NOT
- STATEMENT: Escrow does not vanish on crash.
- PRECONDITIONS: crash before completion
- POSTCONDITIONS: the escrowed amount is present after recovery
- INVARIANTS: `C_available + C_escrowed + C_consumed = C_initial`
- DEPENDENCIES: REQ-RECOV-013
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: mutation M008 (release indeterminate escrow); post-recovery invariant check
- EVIDENCE-STATUS: SPECIFIED

---

## S-14 Host boundary and replay

### REQ-HOST-001
- REQ-ID: REQ-HOST-001
- CATEGORY: host-boundary
- SOURCE: Red-on-Rust.md L8560–8580([15]); L10160–10165([18] `HostPolicy`); spec/01 S-14 R-HOST-01
- NORMATIVE-LEVEL: MUST
- STATEMENT: The live host independently validates concrete OS-level authority/policy for each effect (`HostPolicyOK`).
- PRECONDITIONS: an issued effect reaches the host
- POSTCONDITIONS: an independent policy decision is made before execution
- INVARIANTS: —
- DEPENDENCIES: REQ-HOST-002, REQ-HOST-003
- SECURITY-IMPACT: critical (defense in depth)
- VERIFICATION-METHOD: host policy tests
- EVIDENCE-STATUS: SPECIFIED

### REQ-HOST-002
- REQ-ID: REQ-HOST-002
- CATEGORY: host-boundary
- SOURCE: Red-on-Rust.md L8560–8580([15]); L8836([16] resolution 7); spec/01 S-14 R-HOST-01
- NORMATIVE-LEVEL: MUST
- STATEMENT: `¬HostPolicyOK(E) ⇒ ¬ExternalEffect(E)`.
- PRECONDITIONS: host policy denies
- POSTCONDITIONS: the effect is not executed
- INVARIANTS: `¬HostPolicyOK(E) ⇒ ¬ExternalEffect(E)`
- DEPENDENCIES: REQ-CORE-002
- SECURITY-IMPACT: critical ; AMB-18
- VERIFICATION-METHOD: host policy denial tests
- EVIDENCE-STATUS: SPECIFIED

### REQ-HOST-003
- REQ-ID: REQ-HOST-003
- CATEGORY: host-boundary
- SOURCE: Red-on-Rust.md L38039([54] §8 step 11); L8560–8580([15]); L11069([18]); spec/01 S-14 R-HOST-01; see C-27
- NORMATIVE-LEVEL: MUST
- STATEMENT: The machine's gate-11 host-policy check is fail-early; the host's own check is authoritative.
- PRECONDITIONS: any effect request
- POSTCONDITIONS: both checks occur; the host's decision is final
- INVARIANTS: —
- DEPENDENCIES: REQ-EFFECT-013, REQ-HOST-001
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: defense-in-depth review; host policy tests
- EVIDENCE-STATUS: SPECIFIED

### REQ-HOST-004
- REQ-ID: REQ-HOST-004
- CATEGORY: host-boundary
- SOURCE: Red-on-Rust.md L27644([33]); L41823–41841([60]); spec/01 S-14 R-HOST-02
- NORMATIVE-LEVEL: MUST
- STATEMENT: The host performs only issued effects.
- PRECONDITIONS: any host execution
- POSTCONDITIONS: an `Issued` record exists for it
- INVARIANTS: `HostInvoked(E) ⇒ DurableIssued(E)`
- DEPENDENCIES: REQ-DUR-001
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: `PanicHost` harness; journal cross-check
- EVIDENCE-STATUS: SPECIFIED

### REQ-HOST-005
- REQ-ID: REQ-HOST-005
- CATEGORY: host-boundary
- SOURCE: Red-on-Rust.md L38280–38296([54] §14); L24011–24020([30]); L22333([29] §24 ReplayHost); L23234([29]); spec/01 S-14 R-HOST-03
- NORMATIVE-LEVEL: MUST NOT
- STATEMENT: `ReplayHost` reconstructs recorded effects and NEVER touches the external world.
- PRECONDITIONS: a replay run
- POSTCONDITIONS: no OS/network call occurs
- INVARIANTS: —
- DEPENDENCIES: REQ-HOST-006
- SECURITY-IMPACT: critical (a replay that performs real effects duplicates side effects)
- VERIFICATION-METHOD: replay determinism differential; sandboxed replay assertions
- EVIDENCE-STATUS: SPECIFIED

### REQ-HOST-006
- REQ-ID: REQ-HOST-006
- CATEGORY: host-boundary
- SOURCE: Red-on-Rust.md L38290–38296([54] §14); L25972–25996([32] correction); L1226([3]); spec/01 S-14 R-HOST-03
- NORMATIVE-LEVEL: MUST
- STATEMENT: `ReplayHost` is ordered: for every request it consumes the next trace entry.
- PRECONDITIONS: a request is served during replay
- POSTCONDITIONS: the next entry in sequence is consumed
- INVARIANTS: —
- DEPENDENCIES: REQ-HOST-007
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: replay property tests; replay-vs-live trace equality
- EVIDENCE-STATUS: SPECIFIED

### REQ-HOST-007
- REQ-ID: REQ-HOST-007
- CATEGORY: host-boundary
- SOURCE: Red-on-Rust.md L38290–38296([54] §14); L25972–25996([32]); L1226([3]); spec/01 S-14 R-HOST-03
- NORMATIVE-LEVEL: MUST
- STATEMENT: `ReplayHost` validates both `EffectId` and `EffectDigest` sequentially for each entry.
- PRECONDITIONS: each replayed request
- POSTCONDITIONS: both identifiers match the recorded entry
- INVARIANTS: —
- DEPENDENCIES: REQ-EFFECT-027, REQ-CALC-009
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: replay corruption tests
- EVIDENCE-STATUS: SPECIFIED

### REQ-HOST-008
- REQ-ID: REQ-HOST-008
- CATEGORY: host-boundary
- SOURCE: Red-on-Rust.md L24020([30]); L34519([46]); L35225([47]); L7380–7386([13]); spec/01 S-14 R-HOST-03
- NORMATIVE-LEVEL: MUST
- STATEMENT: A mismatch or an exhausted trace yields `ReplayCorruption` / `ReplayTraceExhausted`.
- PRECONDITIONS: replay validation fails or the trace ends early
- POSTCONDITIONS: an explicit fault is produced; replay does not continue with fabricated results
- INVARIANTS: —
- DEPENDENCIES: REQ-HOST-007; AMB-08 (`ReplayTraceExhausted` is not a variant of the frozen `Fault` enum)
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: replay fault tests
- EVIDENCE-STATUS: SPECIFIED

### REQ-HOST-009
- REQ-ID: REQ-HOST-009
- CATEGORY: host-boundary
- SOURCE: Red-on-Rust.md L38298([54] §14); L24003–24030([30] `HashMap` form, superseded); spec/01 S-14 R-HOST-03; see C-22
- NORMATIVE-LEVEL: MUST NOT
- STATEMENT: An unordered map MUST NOT be used as the normative replay mechanism.
- PRECONDITIONS: replay host implementation
- POSTCONDITIONS: replay ordering is total and observable
- INVARIANTS: —
- DEPENDENCIES: REQ-HOST-006
- SECURITY-IMPACT: high (unordered replay would break trace determinism)
- VERIFICATION-METHOD: implementation review; replay order tests
- EVIDENCE-STATUS: SPECIFIED

### REQ-HOST-010
- REQ-ID: REQ-HOST-010
- CATEGORY: host-boundary
- SOURCE: Red-on-Rust.md L3947–3958([7] v2 Theorem 4); L26249–26262([33]); L1377–1387([4]); spec/01 S-14 R-HOST-04
- NORMATIVE-LEVEL: MUST
- STATEMENT: Replay correspondence: if `LiveRun(Σ₀)` produces trace `T` of (`EffectIssued`, `EffectCompleted`) pairs, then `ReplayRun(Σ₀, T)` produces the same final configuration, provided replay verifies for each step `E_replay,k = E_recorded,k`, `R_replay,k.id = R_recorded,k.id`, and matching digests.
- PRECONDITIONS: a recorded trace and the same initial state; per-step verification holds
- POSTCONDITIONS: identical final configuration
- INVARIANTS: replay correspondence (kept whole per rule 6)
- DEPENDENCIES: REQ-HOST-007, REQ-CORE-011
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: recovery/replay differential
- EVIDENCE-STATUS: SPECIFIED

### REQ-HOST-011
- REQ-ID: REQ-HOST-011
- CATEGORY: host-boundary
- SOURCE: Red-on-Rust.md L3947–3958([7]); L26249–26262([33]); spec/01 S-14 R-HOST-04
- NORMATIVE-LEVEL: MUST
- STATEMENT: Machine-state replay is always valid.
- PRECONDITIONS: replay of machine state
- POSTCONDITIONS: reconstruction succeeds from recorded data alone
- INVARIANTS: —
- DEPENDENCIES: REQ-HOST-010
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: replay differential
- EVIDENCE-STATUS: SPECIFIED

### REQ-HOST-012
- REQ-ID: REQ-HOST-012
- CATEGORY: host-boundary
- SOURCE: Red-on-Rust.md L26249–26262([33]); spec/01 S-14 R-HOST-04
- NORMATIVE-LEVEL: MUST
- STATEMENT: Real-world replay is valid only for reversible/idempotent effects.
- PRECONDITIONS: replay of an effect with real-world consequences
- POSTCONDITIONS: irreversible effects are not re-executed
- INVARIANTS: —
- DEPENDENCIES: REQ-CALC-015; U-06 (effect classes undefined)
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: replay policy tests per effect class
- EVIDENCE-STATUS: SPECIFIED

### REQ-HOST-013
- REQ-ID: REQ-HOST-013
- CATEGORY: host-boundary
- SOURCE: Red-on-Rust.md L26249–26262([33]); spec/01 S-14 R-HOST-04
- NORMATIVE-LEVEL: MUST
- STATEMENT: The replay host refuses to re-execute irreversible effects and returns the recorded result.
- PRECONDITIONS: an irreversible effect is replayed
- POSTCONDITIONS: no external call; the recorded result is returned
- INVARIANTS: —
- DEPENDENCIES: REQ-HOST-012, REQ-HOST-005
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: replay refusal tests
- EVIDENCE-STATUS: SPECIFIED

### REQ-HOST-014
- REQ-ID: REQ-HOST-014
- CATEGORY: host-boundary
- SOURCE: Red-on-Rust.md L38278–38300([54] §14); spec/01 S-14 R-HOST-05
- NORMATIVE-LEVEL: MUST
- STATEMENT: Replay MUST validate the trace, not merely load the final state.
- PRECONDITIONS: a replay run
- POSTCONDITIONS: per-step trace comparison occurs
- INVARIANTS: —
- DEPENDENCIES: REQ-REF-011
- SECURITY-IMPACT: high (final-state-only comparison can mask divergent traces)
- VERIFICATION-METHOD: trace comparison in the differential comparator
- EVIDENCE-STATUS: SPECIFIED

---

## S-15 Actors and deterministic scheduling

### REQ-ACTOR-001
- REQ-ID: REQ-ACTOR-001
- CATEGORY: concurrency
- SOURCE: Red-on-Rust.md L24268–24290([31]); L41623–41641([60]); spec/01 S-15 R-ACTOR-01
- NORMATIVE-LEVEL: MUST
- STATEMENT: Actors have isolated environments, continuations, heaps, mailboxes, budgets, and capability contexts.
- PRECONDITIONS: two or more actors exist
- POSTCONDITIONS: none of these structures is shared
- INVARIANTS: —
- DEPENDENCIES: REQ-ACTOR-002, REQ-ACTOR-003, REQ-ACTOR-004
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: Track D isolation property tests
- EVIDENCE-STATUS: SPECIFIED

### REQ-ACTOR-002
- REQ-ID: REQ-ACTOR-002
- CATEGORY: concurrency
- SOURCE: Red-on-Rust.md L24268–24290([31]); L25884–25900([32] Theorem 4); spec/01 S-15 R-ACTOR-01
- NORMATIVE-LEVEL: MUST
- STATEMENT: For `a ≠ b`: `Heap(a) ∩ Heap(b) = ∅`.
- PRECONDITIONS: two distinct actors
- POSTCONDITIONS: no heap location is reachable from both
- INVARIANTS: `Heap(a) ∩ Heap(b) = ∅`
- DEPENDENCIES: REQ-ACTOR-001
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: isolation property tests
- EVIDENCE-STATUS: SPECIFIED

### REQ-ACTOR-003
- REQ-ID: REQ-ACTOR-003
- CATEGORY: concurrency
- SOURCE: Red-on-Rust.md L24268–24290([31]); L25884–25900([32]); spec/01 S-15 R-ACTOR-01
- NORMATIVE-LEVEL: MUST
- STATEMENT: For `a ≠ b`: `Env(a) ∩ Env(b) = ∅`.
- PRECONDITIONS: two distinct actors
- POSTCONDITIONS: no binding is shared
- INVARIANTS: `Env(a) ∩ Env(b) = ∅`
- DEPENDENCIES: REQ-ACTOR-001
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: isolation property tests
- EVIDENCE-STATUS: SPECIFIED

### REQ-ACTOR-004
- REQ-ID: REQ-ACTOR-004
- CATEGORY: concurrency
- SOURCE: Red-on-Rust.md L24215–24222([31]); L24268–24290([31]); spec/01 S-15 R-ACTOR-01
- NORMATIVE-LEVEL: MUST NOT
- STATEMENT: No actor mutates another actor's heap, environment, or continuation.
- PRECONDITIONS: any actor transition
- POSTCONDITIONS: only the acting actor's state changes
- INVARIANTS: —
- DEPENDENCIES: REQ-ACTOR-001
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: Track D isolation tests; mutation of isolation must be killed
- EVIDENCE-STATUS: SPECIFIED

### REQ-ACTOR-005
- REQ-ID: REQ-ACTOR-005
- CATEGORY: concurrency
- SOURCE: Red-on-Rust.md L25884–25900([32]); L25616–25673([32]); spec/01 S-15 R-ACTOR-01
- NORMATIVE-LEVEL: MUST
- STATEMENT: Actors are instantiated with fresh arenas and `Environment::empty()`; there is no implicit environment inheritance.
- PRECONDITIONS: an actor is spawned
- POSTCONDITIONS: its environment starts empty and its heap is fresh
- INVARIANTS: `Env(a) ∩ Env(b) = ∅`
- DEPENDENCIES: REQ-ACTOR-022
- SECURITY-IMPACT: critical (implicit inheritance would leak parent bindings)
- VERIFICATION-METHOD: spawn isolation tests
- EVIDENCE-STATUS: SPECIFIED

### REQ-ACTOR-006
- REQ-ID: REQ-ACTOR-006
- CATEGORY: concurrency
- SOURCE: Red-on-Rust.md L24156–24163([31]); L25535–25546([32]); spec/01 S-15 R-ACTOR-02
- NORMATIVE-LEVEL: IS
- STATEMENT: `GlobalState { actors: BTreeMap<ActorId, ActorState>, logical_time: LogicalTime, runnable: RunnableQueue, event_log: EventLog, next_effect_id: EffectId, next_actor_id: ActorId, scheduler: SchedulerState }`.
- PRECONDITIONS: —
- POSTCONDITIONS: —
- INVARIANTS: —
- DEPENDENCIES: REQ-CALC-018; U-02 (no frozen canonical encoding)
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: snapshot content review
- EVIDENCE-STATUS: SPECIFIED

### REQ-ACTOR-007
- REQ-ID: REQ-ACTOR-007
- CATEGORY: concurrency
- SOURCE: Red-on-Rust.md L25514–25546([32]); spec/01 S-15 R-ACTOR-02
- NORMATIVE-LEVEL: MUST
- STATEMENT: Logical time is global; an actor observes `global.logical_time` at the instant its transition executes.
- PRECONDITIONS: any actor transition
- POSTCONDITIONS: the observed time is the global value at that instant
- INVARIANTS: —
- DEPENDENCIES: REQ-CALC-019
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: logical-time trace comparison
- EVIDENCE-STATUS: SPECIFIED

### REQ-ACTOR-008
- REQ-ID: REQ-ACTOR-008
- CATEGORY: concurrency
- SOURCE: Red-on-Rust.md L24226–24245([31]); L8844([16] resolution 14); spec/01 S-15 R-ACTOR-03
- NORMATIVE-LEVEL: MUST
- STATEMENT: `ActorId` and `EffectId` are allocated by global monotonic counters (`N' = N + 1`, ID = `N` before increment).
- PRECONDITIONS: any ID allocation
- POSTCONDITIONS: IDs are strictly increasing and deterministic
- INVARIANTS: `N' = N + 1`
- DEPENDENCIES: REQ-CALC-019
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: determinism tests
- EVIDENCE-STATUS: SPECIFIED

### REQ-ACTOR-009
- REQ-ID: REQ-ACTOR-009
- CATEGORY: security-invariant
- SOURCE: Red-on-Rust.md L24226–24245([31]); L24260([31]); L38863([54] §28); spec/01 S-15 R-ACTOR-03
- NORMATIVE-LEVEL: MUST NOT
- STATEMENT: Actor identity MUST NEVER be derived from memory addresses, OS PIDs, random UUIDs, thread IDs, or wall-clock timestamps.
- PRECONDITIONS: any ID construction
- POSTCONDITIONS: identity comes only from the deterministic counters
- INVARIANTS: —
- DEPENDENCIES: REQ-ACTOR-008, REQ-CAP-021
- SECURITY-IMPACT: critical (address-derived identity breaks replay and can leak layout)
- VERIFICATION-METHOD: determinism differential; code review
- EVIDENCE-STATUS: SPECIFIED

### REQ-ACTOR-010
- REQ-ID: REQ-ACTOR-010
- CATEGORY: concurrency
- SOURCE: Red-on-Rust.md L25558–25615([32]); L25886([32]); L38074–38084([54] §9); spec/01 S-15 R-ACTOR-04; spec/06 C-37
- NORMATIVE-LEVEL: MUST
- STATEMENT: The scheduler is strictly FIFO.
- PRECONDITIONS: the runnable queue is non-empty
- POSTCONDITIONS: the head of the queue is selected
- INVARIANTS: —
- DEPENDENCIES: REQ-ACTOR-012
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: `SCHED-FIFO`; mutation M012
- EVIDENCE-STATUS: SPECIFIED

### REQ-ACTOR-011
- REQ-ID: REQ-ACTOR-011
- CATEGORY: concurrency
- SOURCE: Red-on-Rust.md L24287([31]); L25894([32] `members: BTreeSet<ActorId>`); L36476([48]); spec/01 S-15 R-ACTOR-04
- NORMATIVE-LEVEL: MUST
- STATEMENT: One actor appears in the runnable queue at most once (membership-enforced).
- PRECONDITIONS: any enqueue
- POSTCONDITIONS: a duplicate membership is impossible
- INVARIANTS: `ActorId occurs at most once in RunnableQueue`
- DEPENDENCIES: REQ-ACTOR-010
- SECURITY-IMPACT: high (duplication would double-execute a transition)
- VERIFICATION-METHOD: mutation M012 (duplicate runnable queue entry)
- EVIDENCE-STATUS: SPECIFIED

### REQ-ACTOR-012
- REQ-ID: REQ-ACTOR-012
- CATEGORY: concurrency
- SOURCE: Red-on-Rust.md L25558–25615([32]); L37924–37937([54] §9); L24345–24361([31]); spec/01 S-15 R-ACTOR-04
- NORMATIVE-LEVEL: MUST
- STATEMENT: Exactly one actor performs exactly one CEK transition per scheduler turn.
- PRECONDITIONS: a scheduler turn
- POSTCONDITIONS: one transition occurs
- INVARIANTS: —
- DEPENDENCIES: REQ-ACTOR-010, REQ-CORE-011
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: `SCHED-FIFO`; starvation test with 100 actors
- EVIDENCE-STATUS: SPECIFIED

### REQ-ACTOR-013
- REQ-ID: REQ-ACTOR-013
- CATEGORY: concurrency
- SOURCE: Red-on-Rust.md L25558–25615([32]); L25702–25749([32]); spec/01 S-15 R-ACTOR-04
- NORMATIVE-LEVEL: MUST
- STATEMENT: Wakeups (receipts, messages) enqueue the woken actor at the back of the runnable queue.
- PRECONDITIONS: an actor is woken
- POSTCONDITIONS: it is appended at the back, deterministically
- INVARIANTS: —
- DEPENDENCIES: REQ-ACTOR-010, REQ-ACTOR-027
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: `SCHED-FIFO`; deterministic wakeup tests
- EVIDENCE-STATUS: SPECIFIED

### REQ-ACTOR-014
- REQ-ID: REQ-ACTOR-014
- CATEGORY: concurrency
- SOURCE: Red-on-Rust.md L25558–25615([32]); L38086–38096([54] §9); spec/01 S-15 R-ACTOR-04
- NORMATIVE-LEVEL: MUST NOT
- STATEMENT: `Pending`, `Blocked`, `Halted`, and `Faulted` actors are never scheduled.
- PRECONDITIONS: any scheduler selection
- POSTCONDITIONS: only runnable actors are selected
- INVARIANTS: —
- DEPENDENCIES: REQ-ACTOR-010
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: `SCHED-BLOCKED-NOT-SCHEDULED`; mutation M011
- EVIDENCE-STATUS: SPECIFIED

### REQ-ACTOR-015
- REQ-ID: REQ-ACTOR-015
- CATEGORY: concurrency
- SOURCE: Red-on-Rust.md L25567–25582([32]); L24433([31]); spec/01 S-15 R-ACTOR-04
- NORMATIVE-LEVEL: MUST
- STATEMENT: `ActorSelected` is logged.
- PRECONDITIONS: the scheduler selects an actor
- POSTCONDITIONS: the event is appended to the event log
- INVARIANTS: —
- DEPENDENCIES: REQ-PERSIST-006
- SECURITY-IMPACT: medium (the scheduler trace is part of the differential observation)
- VERIFICATION-METHOD: scheduler-trace comparison
- EVIDENCE-STATUS: SPECIFIED

### REQ-ACTOR-016
- REQ-ID: REQ-ACTOR-016
- CATEGORY: concurrency
- SOURCE: Red-on-Rust.md L25579([32]); spec/01 S-15 R-ACTOR-04
- NORMATIVE-LEVEL: MUST
- STATEMENT: An empty runnable queue yields a `Deadlock` outcome.
- PRECONDITIONS: the runnable queue is empty and work remains unfinished
- POSTCONDITIONS: the machine reports `Deadlock` rather than spinning or silently halting
- INVARIANTS: —
- DEPENDENCIES: REQ-ACTOR-010
- SECURITY-IMPACT: medium
- VERIFICATION-METHOD: deadlock detection test
- EVIDENCE-STATUS: SPECIFIED

### REQ-ACTOR-017
- REQ-ID: REQ-ACTOR-017
- CATEGORY: concurrency
- SOURCE: Red-on-Rust.md L25573–25615([32] `execute_spawn`); L25931–25960([32]); L38098–38106([54] §9); L1050–1058([3]); spec/01 S-15 R-ACTOR-05
- NORMATIVE-LEVEL: MUST
- STATEMENT: Spawn is a deterministic, transactional machine operation with the ordered steps: (1) validate and escrow budget; (2) allocate child `ActorId`; (3) derive child capabilities; (4) construct isolated child state; (5) enqueue deterministically; (6) log `ActorSpawned`.
- PRECONDITIONS: a `Spawn` term is evaluated
- POSTCONDITIONS: the six steps occur in order, or the spawn does not occur
- INVARIANTS: — (ordered transaction; kept whole per rule 6)
- DEPENDENCIES: REQ-ACTOR-018…REQ-ACTOR-024
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: Track D spawn tests; amplification test
- EVIDENCE-STATUS: SPECIFIED

### REQ-ACTOR-018
- REQ-ID: REQ-ACTOR-018
- CATEGORY: concurrency
- SOURCE: Red-on-Rust.md L25935–25945([32] `budget_alloc.validate_and_escrow`); L12192([21] `BudgetAllocationSpec`); spec/01 S-15 R-ACTOR-05
- NORMATIVE-LEVEL: AMBIGUOUS
- STATEMENT: Spawn MUST validate and escrow the child budget via `budget_alloc.validate_and_escrow(&mut parent.budget)`, and spawn is budget transfer, not budget creation — but the validation rules of `BudgetAllocationSpec` (maximum child share, minimum parent retention, who supplies it, interaction with `R` caps, faults on violation) are never stated.
- PRECONDITIONS: a `Spawn` with a budget allocation spec
- POSTCONDITIONS: escrow occurs and conservation holds
- INVARIANTS: `C_parent' = C_parent − C_a − cost_C(spawn)`
- DEPENDENCIES: U-03, AMB-03
- SECURITY-IMPACT: critical (a malicious parent could starve the child; the source itself warns of this)
- VERIFICATION-METHOD: UNDEFINED until the allocation policy is frozen (req/04, VU-03)
- EVIDENCE-STATUS: SPECIFIED

### REQ-ACTOR-019
- REQ-ID: REQ-ACTOR-019
- CATEGORY: security-invariant
- SOURCE: Red-on-Rust.md L25573–25615([32]); L38098–38106([54] §9); spec/01 S-15 R-ACTOR-05
- NORMATIVE-LEVEL: MUST
- STATEMENT: The child receives explicitly derived (attenuated) capabilities only, via `kernel.derive(parent_cap, constraint, t)`.
- PRECONDITIONS: a child actor is created
- POSTCONDITIONS: every capability in the child context is a derivation of a parent capability
- INVARIANTS: `Authority_child ≼ Authority_parent`
- DEPENDENCIES: REQ-CAP-012, REQ-ACTOR-020
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: Track D; amplification test
- EVIDENCE-STATUS: SPECIFIED

### REQ-ACTOR-020
- REQ-ID: REQ-ACTOR-020
- CATEGORY: security-invariant
- SOURCE: Red-on-Rust.md L25573–25615([32]); L38861([54] §28); spec/01 S-15 R-ACTOR-05
- NORMATIVE-LEVEL: MUST NOT
- STATEMENT: Wholesale capability copying/cloning during spawn is forbidden.
- PRECONDITIONS: spawn implementation
- POSTCONDITIONS: no bulk copy of the parent context
- INVARIANTS: —
- DEPENDENCIES: REQ-CLAIM-004
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: code review; amplification test
- EVIDENCE-STATUS: SPECIFIED

### REQ-ACTOR-021
- REQ-ID: REQ-ACTOR-021
- CATEGORY: concurrency
- SOURCE: Red-on-Rust.md L25616–25673([32]); L25884–25900([32]); spec/01 S-15 R-ACTOR-05
- NORMATIVE-LEVEL: MUST
- STATEMENT: Spawn constructs isolated child state (fresh heap, empty environment, own mailbox, own budget, own capability context).
- PRECONDITIONS: spawn step 4
- POSTCONDITIONS: the child shares nothing mutable with the parent
- INVARIANTS: `Heap(a) ∩ Heap(b) = ∅ ∧ Env(a) ∩ Env(b) = ∅`
- DEPENDENCIES: REQ-ACTOR-005
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: spawn isolation tests (Track D)
- EVIDENCE-STATUS: SPECIFIED

### REQ-ACTOR-022
- REQ-ID: REQ-ACTOR-022
- CATEGORY: concurrency
- SOURCE: Red-on-Rust.md L25616–25673 ([32]) ([32] `global.runnable.enqueue(child_id)`); spec/01 S-15 R-ACTOR-05
- NORMATIVE-LEVEL: MUST
- STATEMENT: The child is enqueued deterministically.
- PRECONDITIONS: spawn step 5
- POSTCONDITIONS: enqueue position is a deterministic function of machine state
- INVARIANTS: —
- DEPENDENCIES: REQ-ACTOR-010
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: determinism differential
- EVIDENCE-STATUS: SPECIFIED

### REQ-ACTOR-023
- REQ-ID: REQ-ACTOR-023
- CATEGORY: concurrency
- SOURCE: Red-on-Rust.md L25660–25673([32] `MachineEvent::ActorSpawned`); spec/01 S-15 R-ACTOR-05
- NORMATIVE-LEVEL: MUST
- STATEMENT: Spawn logs `ActorSpawned`.
- PRECONDITIONS: spawn step 6
- POSTCONDITIONS: the event is appended to the event log
- INVARIANTS: —
- DEPENDENCIES: REQ-PERSIST-006
- SECURITY-IMPACT: medium
- VERIFICATION-METHOD: event-trace comparison
- EVIDENCE-STATUS: SPECIFIED

### REQ-ACTOR-024
- REQ-ID: REQ-ACTOR-024
- CATEGORY: concurrency
- SOURCE: Red-on-Rust.md L8770–8786([16] v0.3 E-Spawn) — **(v0.3 rules)**
- NORMATIVE-LEVEL: MUST
- STATEMENT: `E-Spawn` requires `C_a + cost_C(spawn) ≤ C_parent` and `R_a + cost_R(spawn) ≤ R_parent` (via `ReserveOK`), allocates `a_new = N_a` with `N_a' = N_a + 1`, sets the child context to `attenuated_context(κ_parent, trust_level)`, updates the parent to `C ← C_parent − C_a − cost_C(spawn)` and `R ← R_parent − R_a`, advances `t` by `δ_t(spawn)`, and appends `ActorSpawned(a_new)`.
- PRECONDITIONS: both escrow predicates hold
- POSTCONDITIONS: as stated
- INVARIANTS: `C_parent' = C_parent − C_a − cost_C(spawn)`
- DEPENDENCIES: REQ-ACTOR-018, REQ-BUDGET-009, REQ-ACTOR-019; AMB-04 (`trust_level` has no counterpart in the frozen `Spawn` AST)
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: Track D spawn tests; teleportation test
- EVIDENCE-STATUS: SPECIFIED

### REQ-ACTOR-025
- REQ-ID: REQ-ACTOR-025
- CATEGORY: concurrency
- SOURCE: Red-on-Rust.md L25702–25749([32]); L38074–38090([54] §9); spec/01 S-15 R-ACTOR-06
- NORMATIVE-LEVEL: MUST
- STATEMENT: `Send` is asynchronous: marshal the value, enqueue it into the target's mailbox, and log `MessageSent`.
- PRECONDITIONS: a `Send` term is evaluated
- POSTCONDITIONS: the value is marshalled, enqueued, and logged; the sender continues
- INVARIANTS: —
- DEPENDENCIES: REQ-MARSHAL-007, REQ-ACTOR-031
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: Track D send/receive tests
- EVIDENCE-STATUS: SPECIFIED

### REQ-ACTOR-026
- REQ-ID: REQ-ACTOR-026
- CATEGORY: concurrency
- SOURCE: Red-on-Rust.md L25702–25749([32]); L8788–8790([16] E-Send); spec/01 S-15 R-ACTOR-06
- NORMATIVE-LEVEL: MUST
- STATEMENT: `Send` deterministically wakes a `Blocked` target exactly once.
- PRECONDITIONS: the target is `Blocked` on receive
- POSTCONDITIONS: exactly one wakeup is enqueued
- INVARIANTS: —
- DEPENDENCIES: REQ-ACTOR-013
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: deterministic wakeup tests; mutation M013-class
- EVIDENCE-STATUS: SPECIFIED

### REQ-ACTOR-027
- REQ-ID: REQ-ACTOR-027
- CATEGORY: concurrency
- SOURCE: Red-on-Rust.md L25702–25749([32]); L8792–8794([16] E-Receive); spec/01 S-15 R-ACTOR-06
- NORMATIVE-LEVEL: MUST
- STATEMENT: `Receive` dequeues a value from the mailbox and unmarshals it.
- PRECONDITIONS: the mailbox is non-empty
- POSTCONDITIONS: the value becomes the current term; the mailbox loses it; status returns to `Running`
- INVARIANTS: —
- DEPENDENCIES: REQ-MARSHAL-007
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: Track D send/receive tests
- EVIDENCE-STATUS: SPECIFIED

### REQ-ACTOR-028
- REQ-ID: REQ-ACTOR-028
- CATEGORY: concurrency
- SOURCE: Red-on-Rust.md L25738([32] "blocks without consuming fuel"); L26004([32]); L8796–8799([16] E-ReceiveBlocked); spec/01 S-15 R-ACTOR-06
- NORMATIVE-LEVEL: MUST
- STATEMENT: On an empty mailbox `Receive` blocks **without consuming fuel**.
- PRECONDITIONS: the mailbox is empty
- POSTCONDITIONS: `δ_t = 0` and no budget is consumed
- INVARIANTS: —
- DEPENDENCIES: REQ-ACTOR-029
- SECURITY-IMPACT: high (charging for blocking would let a peer exhaust a victim's budget)
- VERIFICATION-METHOD: blocked-actor budget assertion
- EVIDENCE-STATUS: SPECIFIED

### REQ-ACTOR-029
- REQ-ID: REQ-ACTOR-029
- CATEGORY: concurrency
- SOURCE: Red-on-Rust.md L8796–8799([16] E-ReceiveBlocked); L8843([16] resolution 12); spec/01 S-15 R-ACTOR-06
- NORMATIVE-LEVEL: MUST
- STATEMENT: `Blocked` is a suspension state, not an active transition; the blocked actor yields to the global scheduler as a terminal `Blocked(K)` state.
- PRECONDITIONS: the mailbox is empty
- POSTCONDITIONS: the scheduler continues with other actors
- INVARIANTS: —
- DEPENDENCIES: REQ-ACTOR-014
- SECURITY-IMPACT: medium
- VERIFICATION-METHOD: `SCHED-BLOCKED-NOT-SCHEDULED`
- EVIDENCE-STATUS: SPECIFIED

### REQ-ACTOR-030
- REQ-ID: REQ-ACTOR-030
- CATEGORY: concurrency
- SOURCE: Red-on-Rust.md L25702–25749([32]); L25674–25701([32]); L38092–38096([54] §9); spec/01 S-15 R-ACTOR-06
- NORMATIVE-LEVEL: MUST
- STATEMENT: Mailboxes are FIFO.
- PRECONDITIONS: messages are enqueued and dequeued
- POSTCONDITIONS: delivery order equals send order per sender/target pair
- INVARIANTS: —
- DEPENDENCIES: REQ-ACTOR-025, REQ-ACTOR-027
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: mutation M013 (break mailbox FIFO)
- EVIDENCE-STATUS: SPECIFIED

### REQ-ACTOR-031
- REQ-ID: REQ-ACTOR-031
- CATEGORY: security-invariant
- SOURCE: Red-on-Rust.md L25759–25766([32] Theorem 1); spec/01 S-15 R-ACTOR-07
- NORMATIVE-LEVEL: MUST
- STATEMENT: Deterministic concurrency: `InitialState + SchedulerTrace + HostTrace ⇒ UniqueMachineTrace` — the scheduler is strictly FIFO, IDs are monotonic, and the CEK machine is deterministic, so global state transitions are uniquely determined by the same initial state and the same external observations.
- PRECONDITIONS: identical initial state and traces
- POSTCONDITIONS: a unique global trace
- INVARIANTS: `InitialState + SchedulerTrace + HostTrace ⇒ UniqueMachineTrace`
- DEPENDENCIES: REQ-ACTOR-010, REQ-ACTOR-008, REQ-CORE-011
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: global differential (Track D)
- EVIDENCE-STATUS: SPECIFIED

### REQ-ACTOR-032
- REQ-ID: REQ-ACTOR-032
- CATEGORY: security-invariant
- SOURCE: Red-on-Rust.md L26048–26060([32] Theorem 2); spec/01 S-15 R-ACTOR-08
- NORMATIVE-LEVEL: MUST
- STATEMENT: No amplification: `Authority_after ≼ Authority_before ∪ ExplicitlyDelegatedAuthority`; ordinary `Send` passes through `marshal()`, which rejects raw capabilities.
- PRECONDITIONS: any sequence of actor operations
- POSTCONDITIONS: no actor's authority exceeds its prior authority plus explicitly delegated authority
- INVARIANTS: `Authority_after ≼ Authority_before ∪ ExplicitlyDelegatedAuthority`
- DEPENDENCIES: REQ-MARSHAL-001, REQ-MARSHAL-003
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: amplification test (forced `CapRef` through `Send` ⇒ fault, context unchanged)
- EVIDENCE-STATUS: SPECIFIED

### REQ-ACTOR-033
- REQ-ID: REQ-ACTOR-033
- CATEGORY: security-invariant
- SOURCE: Red-on-Rust.md L26062–26070([32] Theorem 3); L26082–26090([32] The Teleportation Test); spec/01 S-15 R-ACTOR-08
- NORMATIVE-LEVEL: MUST
- STATEMENT: No teleportation: `Σ_actors C_consumable + Σ_escrow C_escrow + Σ_issued C_issue = C_global_initial`.
- PRECONDITIONS: any actor tree at any time
- POSTCONDITIONS: the global sum equals the initial budget
- INVARIANTS: `Σ_actors C_consumable + Σ_escrow C_escrow + Σ_issued C_issue = C_global_initial`
- DEPENDENCIES: REQ-CORE-005, REQ-BUDGET-022
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: teleportation test over the actor tree
- EVIDENCE-STATUS: SPECIFIED

### REQ-ACTOR-034
- REQ-ID: REQ-ACTOR-034
- CATEGORY: concurrency
- SOURCE: Red-on-Rust.md L26062–26070([32]); spec/01 S-15 R-ACTOR-08
- NORMATIVE-LEVEL: MUST
- STATEMENT: Budget is created only at root initialization; spawn escrows; `Send` carries no budget.
- PRECONDITIONS: any actor operation
- POSTCONDITIONS: no operation other than root initialization creates budget
- INVARIANTS: —
- DEPENDENCIES: REQ-ACTOR-033, REQ-ACTOR-024
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: teleportation test; randomized Spawn/Request/Complete sequences
- EVIDENCE-STATUS: SPECIFIED

### REQ-ACTOR-035
- REQ-ID: REQ-ACTOR-035
- CATEGORY: concurrency
- SOURCE: Red-on-Rust.md L25514–25557([32] `RunState`); L23806([30] `ActorStatus`); spec/06 C-18
- NORMATIVE-LEVEL: AMBIGUOUS
- STATEMENT: Two enums describe actor liveness — scheduler-visible `RunState` (`Runnable/Running/Pending/Blocked/Halted/Faulted`) and machine-visible `ActorStatus` (`Running/Pending/Blocked/Halted/Fault`). The mapping between them is implied but never stated as a table, and the frozen text keeps both.
- PRECONDITIONS: scheduler selection and status transitions
- POSTCONDITIONS: — (mapping undefined)
- INVARIANTS: —
- DEPENDENCIES: AMB-05, REQ-ACTOR-014
- SECURITY-IMPACT: high (a wrong mapping schedules a blocked actor — mutation M011's target)
- VERIFICATION-METHOD: UNDEFINED until the mapping is frozen (req/04, VU-04)
- EVIDENCE-STATUS: SPECIFIED

---

## S-16 Marshalling and delegation

### REQ-MARSHAL-001
- REQ-ID: REQ-MARSHAL-001
- CATEGORY: marshalling
- SOURCE: Red-on-Rust.md L41647–41658([60]); L25674–25701([32]); L38110–38120([54] §10); spec/01 S-16 R-MARSHAL-01
- NORMATIVE-LEVEL: MUST
- STATEMENT: Ordinary data marshalling MUST reject capabilities recursively, including capabilities nested inside lists, tuples, functions, or any nested structure.
- PRECONDITIONS: `marshal(v)` where `v` contains a capability at any depth
- POSTCONDITIONS: marshalling fails
- INVARIANTS: —
- DEPENDENCIES: REQ-MARSHAL-002
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: `MARSHAL-NO-RAW-CAPABILITY`; nested-capability tests
- EVIDENCE-STATUS: SPECIFIED

### REQ-MARSHAL-002
- REQ-ID: REQ-MARSHAL-002
- CATEGORY: marshalling
- SOURCE: Red-on-Rust.md L25685–25700([32] `MarshalFault`); L38110–38120([54] §10); spec/01 S-16 R-MARSHAL-01
- NORMATIVE-LEVEL: MUST
- STATEMENT: `marshal_value(v) ⇒ Err(MarshalFault::CapabilityRequiresDelegation)` if `contains_capability(v)`.
- PRECONDITIONS: `v` contains a capability
- POSTCONDITIONS: the specified fault is returned; the recipient context is unchanged
- INVARIANTS: `CapRef ∉ marshal(v)`
- DEPENDENCIES: REQ-MARSHAL-009
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: marshalling authority isolation test (embedded `CapRef` in `List` ⇒ `MarshalFault`)
- EVIDENCE-STATUS: SPECIFIED

### REQ-MARSHAL-003
- REQ-ID: REQ-MARSHAL-003
- CATEGORY: marshalling
- SOURCE: Red-on-Rust.md L25700([32] §4); L25931([32]); L38124–38130([54] §10); spec/01 S-16 R-MARSHAL-02
- NORMATIVE-LEVEL: MUST
- STATEMENT: Authority crosses actor boundaries only through explicit delegation, expressed as a separate explicit AST node `Expr::Delegate`.
- PRECONDITIONS: authority must reach another actor
- POSTCONDITIONS: the delegation node is the only path
- INVARIANTS: —
- DEPENDENCIES: REQ-CORE-010; AMB-11 (`Expr::Delegate` is declared at L25989–25992 but absent from the frozen 12-constructor `Expr`)
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: Track C delegation tests
- EVIDENCE-STATUS: SPECIFIED

### REQ-MARSHAL-004
- REQ-ID: REQ-MARSHAL-004
- CATEGORY: marshalling
- SOURCE: Red-on-Rust.md L25984–25995([32] §4); L38124–38130([54] §10); spec/01 S-16 R-MARSHAL-02
- NORMATIVE-LEVEL: MUST
- STATEMENT: Delegation invokes the capability kernel and wraps the resulting `CapRef` in a `DelegatedCapability` envelope (`Value::DelegatedCapability(CapRef)`) that the marshaller accepts, serialized alongside the constraint.
- PRECONDITIONS: a delegation is performed
- POSTCONDITIONS: the envelope crosses the boundary; a raw `Value::Capability` does not
- INVARIANTS: —
- DEPENDENCIES: REQ-MARSHAL-002, REQ-KERN-005
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: Track C delegation tests
- EVIDENCE-STATUS: SPECIFIED

### REQ-MARSHAL-005
- REQ-ID: REQ-MARSHAL-005
- CATEGORY: security-invariant
- SOURCE: Red-on-Rust.md L25972–26001([32]); L37955–37960([54] §6); L38131–L38133([54] §10); spec/01 S-16 R-MARSHAL-02
- NORMATIVE-LEVEL: MUST
- STATEMENT: `DelegatedAuthority ≼ ParentAuthority`.
- PRECONDITIONS: any delegation
- POSTCONDITIONS: the delegated grant is no stronger than the parent's
- INVARIANTS: `DelegatedAuthority ≼ ParentAuthority`
- DEPENDENCIES: REQ-CAP-012, REQ-ACTOR-032
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: Track C delegation; `CAP-DERIVE-NO-AMPLIFICATION`
- EVIDENCE-STATUS: SPECIFIED

### REQ-MARSHAL-006
- REQ-ID: REQ-MARSHAL-006
- CATEGORY: marshalling
- SOURCE: Red-on-Rust.md L26000–26001([32]); spec/01 S-16 R-MARSHAL-02
- NORMATIVE-LEVEL: MUST
- STATEMENT: On receive, the recipient's kernel registers the new capability in its local context.
- PRECONDITIONS: a `DelegatedCapability` is received
- POSTCONDITIONS: the recipient's `CapabilityContext` gains the capability
- INVARIANTS: —
- DEPENDENCIES: REQ-MARSHAL-004
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: Track C delegation tests
- EVIDENCE-STATUS: SPECIFIED

### REQ-MARSHAL-007
- REQ-ID: REQ-MARSHAL-007
- CATEGORY: marshalling
- SOURCE: Red-on-Rust.md L25680–25690 ([32]) ([32] `MarshalledValue(Vec<u8>)`); L26072–26079([32] Track B); spec/01 S-16 R-MARSHAL-03
- NORMATIVE-LEVEL: MUST
- STATEMENT: `MarshalledValue` is the canonical serialized byte representation (`canonical_serialize(v)`).
- PRECONDITIONS: a value is marshalled
- POSTCONDITIONS: the bytes are the Phase 15A canonical encoding
- INVARIANTS: —
- DEPENDENCIES: REQ-CANON-001, REQ-PERSIST-002
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: Track B marshalling tests
- EVIDENCE-STATUS: SPECIFIED

### REQ-MARSHAL-008
- REQ-ID: REQ-MARSHAL-008
- CATEGORY: marshalling
- SOURCE: Red-on-Rust.md L25674–25701([32]); L26072–26079([32] Track B); L33160–33170([45]); spec/01 S-16 R-MARSHAL-03; spec/06 C-45
- NORMATIVE-LEVEL: AMBIGUOUS
- STATEMENT: `unmarshal(marshal(v)) = v` for all pure values — but the source has two incompatible `Value` domains (machine 11-variant, canonical 8-variant with `Map`), and the round-trip is not stated for a specific domain.
- PRECONDITIONS: a pure value is marshalled and unmarshalled
- POSTCONDITIONS: the original value is recovered
- INVARIANTS: `unmarshal(marshal(v)) = v`
- DEPENDENCIES: U-09, AMB-06, REQ-CANON-009
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: Track B round-trip tests (domain scope undefined — req/04, VU-05)
- EVIDENCE-STATUS: SPECIFIED

### REQ-MARSHAL-009
- REQ-ID: REQ-MARSHAL-009
- CATEGORY: marshalling
- SOURCE: Red-on-Rust.md L8695–8698([16]); L8842([16] resolution 11); spec/01 S-16 R-MARSHAL-04
- NORMATIVE-LEVEL: MUST
- STATEMENT: `marshal(v)` traverses `v`; by default `CapRef ∉ marshal(v)`.
- PRECONDITIONS: any marshalling
- POSTCONDITIONS: no capability reference appears in the output
- INVARIANTS: `CapRef ∉ marshal(v)`
- DEPENDENCIES: REQ-MARSHAL-001
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: `MARSHAL-NO-RAW-CAPABILITY`
- EVIDENCE-STATUS: SPECIFIED

### REQ-MARSHAL-010
- REQ-ID: REQ-MARSHAL-010
- CATEGORY: marshalling
- SOURCE: Red-on-Rust.md L8695–8698([16]); L25700([32]); spec/01 S-16 R-MARSHAL-04
- NORMATIVE-LEVEL: MUST
- STATEMENT: Authority transfer requires the explicit `delegate(c, C, target_actor)` operation.
- PRECONDITIONS: authority must be transferred
- POSTCONDITIONS: the explicit operation is used
- INVARIANTS: —
- DEPENDENCIES: REQ-MARSHAL-003, REQ-MARSHAL-005
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: Track C delegation tests
- EVIDENCE-STATUS: SPECIFIED
