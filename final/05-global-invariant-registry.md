# FINAL1 — 05. Global Invariant Registry

The single canonical registry for the machine's global invariants, in three families: `GI-SEC` (security), `GI-DET` (determinism), `GI-REC` (recovery/persistence). **No invariant is defined here**: each row names its *definitional home* — the requirement whose text is the canonical statement — and supplies the formal metadata FINAL1 requires (variables, domains, quantifiers, applicable state/transition context). Other sections reference invariants by these stable IDs. The `formula` line in each block is an *identification quote* of the home row's statement, marked as such — the normative content governs only in the home row.

Registry IDs are additive compilation-layer IDs (like `T-`/`N-`/`X-`/`D-`/`V-` before them); they renumber nothing and resolve nothing: where the home row records a preserved limitation or open item, the registry row inherits it verbatim as a note.

## 1. The registry

### Security invariants (FINAL1 §23)

#### GI-SEC-01 — No authority crosses to effect

- **Canonical formula (identification quote; normative home below):** `LLMOutput ∧ UntrustedInput ↛ ExternalEffect`
- **Definitional home (single canonical definition):** `R-CORE-01` (FINAL1 §02)
- **Cross-references (reference-by-ID; no restatement):** `R-CORE-02`, `R-TRUST-01`, `R-TRUST-02`, `R-PLANNER-02`, `R-CLAIM-01`
- **Variables:** `LLMOutput` — any planner output object; `UntrustedInput` — any `Block` data; `E` — any host-visible effect event
- **Domains:** over all runs of the machine; `E` ranges over host-visible effect events
- **Quantification:** ∀ run, ∀ E: `LLMOutput ∧ UntrustedInput ⇒ ¬ExternalEffect(E)` absent the §02 chain
- **Applicable state/transition context:** machine-wide, every transition sequence; the central *negative* guarantee
- **Preservation notes / carried limitations:** Negative guarantee: MUST NOT be weakened for textual simplification; the authority audit's `SEC-001` class found it non-holding at specification level and the frozen addenda remediated at the normative layer — the guarantee stands as specified, unproven (no implementation).

#### GI-SEC-02 — External-effect chain (7 conjuncts)

- **Canonical formula (identification quote; normative home below):** `ExternalEffect(E) ⇒ ValidatedRequest(E) ∧ Authorized(E,κ,t) ∧ CapabilityWithinCeiling(E) ∧ BudgetAvailable(E) ∧ DeadlineValid(E,t) ∧ HostPolicyOK(E) ∧ Issued(E)`
- **Definitional home (single canonical definition):** `R-CORE-02` (FINAL1 §02)
- **Cross-references (reference-by-ID; no restatement):** `R-CORE-11`, `R-EFFECT-01`, `R-EFFECT-03`, `R-CORE-14`, `R-DUR-02`, `R-TEST-09`
- **Variables:** `E` — effect; `plan(E)` — the plan that produced `E`; `κ` — holder capability map; `t` — `LogicalTime`
- **Domains:** `E` all host-bound effects; predicates per their canonical signatures
- **Quantification:** invariant over every transition (not a per-phase gate): the chain must hold for every observed `ExternalEffect`
- **Applicable state/transition context:** request-transition composition, gates 1–16 (`R-EFFECT-01`/`R-CORE-14` ordering)
- **Preservation notes / carried limitations:** Canonical predicate signatures are frozen by R-CORE-11: `ValidatedRequest(E) ⇒ ValidatedPlan(plan(E))` and holder-first `Authorized(holder, c, E, t)`; plan-time-only or authority-first readings MUST NOT be substituted (differential adjudication R-TEST-09 binds to this form).

#### GI-SEC-03 — No unauthorized effects

- **Canonical formula (identification quote; normative home below):** `¬Authorized(A,E,t) ⇒ ¬ExternalEffect(E)`
- **Definitional home (single canonical definition):** `R-CORE-03` (FINAL1 §02)
- **Cross-references (reference-by-ID; no restatement):** `R-CAP-06`, `R-EFFECT-02`
- **Variables:** `A` — exercising authority per the canonical holder-possession form (R-CORE-11/R-KERN-04)
- **Domains:** all effect requests
- **Quantification:** ∀ E at every time `t`
- **Applicable state/transition context:** authorization gate; equivalently `¬Authorized ⇒ ¬Request` operationally
- **Preservation notes / carried limitations:** mod/18 D-08: canonical algebraic predicate in R-CAP-06; the machine-level oblation is this row. Both homes kept; no restatement elsewhere.

#### GI-SEC-04 — No authority amplification

- **Canonical formula (identification quote; normative home below):** `derive(A,C) ≼ A`
- **Definitional home (single canonical definition):** `R-CAP-05` (FINAL1 §06)
- **Cross-references (reference-by-ID; no restatement):** `R-CORE-04`, `R-ACTOR-09`, `R-CAP-03`
- **Variables:** `A` — authority (`{(o,⟨S,Q,R,T⟩)}`); `C` — `Constraint`/`AdmissibleConstraint`
- **Domains:** ∀ A, ∀ admissible C; ill-formed C ⇒ derivation undefined (R-CAP-10 totality clause)
- **Quantification:** ∀ A, C: the meet law holds pointwise per operation
- **Applicable state/transition context:** kernel derivation; every attenuation at spawn/delegation sites
- **Preservation notes / carried limitations:** mod/18 D-01 canonicalized this invariant at the algebraic home (R-CAP-05); the spawn strictness `Authority(child) ≺ Authority(parent)` (R-ACTOR-09) is a *separate* strengthening, not this row; `≼` vs `≺` are distinct relations — do not conflate.

#### GI-SEC-05 — Revocation lineage

- **Canonical formula (identification quote; normative home below):** `Valid(c,t) ⇔ Live(c) ∧ t ∈ Lifetime(c) ∧ ∀a ∈ Ancestors(c): Live(a)`
- **Definitional home (single canonical definition):** `R-CAP-07` (FINAL1 §06)
- **Cross-references (reference-by-ID; no restatement):** `R-PERSIST-07`, `R-CAP-09`, `R-KERN-02`
- **Variables:** `c` — `CapRef`; ancestor chain in the kernel arena
- **Domains:** every capability with lineage depth d; check is O(d) lazy
- **Quantification:** ∀ c live-checked at gate time and at recovery
- **Applicable state/transition context:** authorization gate; recovery revalidation (`RECOVERY-REVOCATION-DURABLE`)
- **Preservation notes / carried limitations:** Lifetime is logical (`LogicalTime`, half-open `[start, end)`) per R-CAP-11 (addendum IX resolved U-36). Revocation monotonic across crashes — a revoked capability never revalidates without a new explicit grant.

#### GI-SEC-06 — Budget conservation (no teleportation)

- **Canonical formula (identification quote; normative home below):** `C_available + C_escrowed + C_consumed = C_initial` (global form `Σ_actors C_consumable + Σ_escrow C_escrow + Σ_issued C_issue = C_global_initial`)
- **Definitional home (single canonical definition):** `R-BUDGET-05` (FINAL1 §07)
- **Cross-references (reference-by-ID; no restatement):** `R-CORE-05`, `R-ACTOR-08`, `R-BUDGET-11`, `R-RECOV-06`
- **Variables:** `C_*` — per-actor consumable partitions; root budget minted once at init
- **Domains:** every reachable state, every partition transition
- **Quantification:** invariant: after every step; across crashes (GI-REC-05) it must survive identically
- **Applicable state/transition context:** every budget debit/escrow/refund transition (Op-01…Op-22 per R-BUDGET-10)
- **Preservation notes / carried limitations:** mod/18 D-02 canonical home is R-BUDGET-05. `audit/_conservation_checker.py` passing is a structural gate on the *rules*, not machine evidence; promotion forbidden (R-CORE-05 row stays SPECIFIED).

#### GI-SEC-07 — Durable-before-host

- **Canonical formula (identification quote; normative home below):** `HostInvoked(E) ⇒ DurableIssued(E)`
- **Definitional home (single canonical definition):** `R-DUR-01` (FINAL1 §11)
- **Cross-references (reference-by-ID; no restatement):** `R-CORE-06`, `R-DUR-02`, `R-DUR-06`, `R-DUR-07`, `R-CORE-14`
- **Variables:** `E` — effect; `DurableIssued` — durable `Issued` record under 15A framing
- **Domains:** every host invocation path, including supervisor/reconciliation (R-RECOV-08: no exception)
- **Quantification:** ∀ E: host call without durable `Issued` is a conformance failure
- **Applicable state/transition context:** issuance transaction steps 1–7 (R-DUR-02), journal-driven commit (R-DUR-07)
- **Preservation notes / carried limitations:** mod/18 D-03 canonical home is R-DUR-01; an in-memory object never satisfies `Issued` (R-CORE-06). The crate-DAG carrying of this hinge is frozen structurally by R-TRUST-05.

#### GI-SEC-08 — No raw capability transfer

- **Canonical formula (identification quote; normative home below):** `marshal_value(v) ⇒ Err(MarshalFault::CapabilityRequiresDelegation)` if `contains_capability(v)`; `OrdinaryMarshal(Value::Capability) ⇒ Rejected`
- **Definitional home (single canonical definition):** `R-MARSHAL-01` (FINAL1 §13)
- **Cross-references (reference-by-ID; no restatement):** `R-CORE-07`, `R-MARSHAL-02`, `R-MARSHAL-04`, `R-MARSHAL-05`, `R-MARSHAL-06`, `R-CANON-12`
- **Variables:** `v` — any value crossing an actor/machine boundary (messages, receipts, snapshots, replay)
- **Domains:** unbounded structural depth incl. `FunctionValue.env` captured environments
- **Quantification:** ∀ crossings; exclusion only for kernel-sealed delegation envelopes
- **Applicable state/transition context:** `Send`/`marshal`/`unmarshal`, decode-side admission, mailbox and snapshot byte paths
- **Preservation notes / carried limitations:** mod/18 D-04 canonical home is R-MARSHAL-01. Boundary invariant is stated over reachability (`marshal(v)=Ok ⇒ ¬∃c. Reachable(env_of(v), c)`, R-MARSHAL-06); the decode side (R-CANON-12) makes the boundary symmetric.

#### GI-SEC-09 — Receipt causality

- **Canonical formula (identification quote; normative home below):** `Resume ⇒ id = id_pending ∧ effect_digest = digest_pending ∧ (R-HOST-06) result_digest = ResultDigest(result)`
- **Definitional home (single canonical definition):** `R-EFFECT-06` (FINAL1 §11)
- **Cross-references (reference-by-ID; no restatement):** `R-EFFECT-07`, `R-EFFECT-08`, `R-HOST-03`, `R-HOST-06`, `R-HOST-04`
- **Variables:** `EffectReceipt {id, effect_digest, result}` (+ durable `result_digest` conjunct)
- **Domains:** every receipt on live and replay paths; result payload ∈ canonical data domain
- **Quantification:** ∀ receipts: mismatch ⇒ `ReplayCorruption`-family fault, no resume, no release
- **Applicable state/transition context:** completion transition; replay step consumption
- **Preservation notes / carried limitations:** R-EFFECT-08: a receipt completes an effect, it never confers authority — capability/closure payload admission faults before resumption.

#### GI-SEC-10 — Gate short-circuit atomicity

- **Canonical formula (identification quote; normative home below):** denial at any gate ⇒ subsequent gates not called, `next_effect_id` unchanged, budget unchanged, event log unchanged, `HostExecutor::execute` never invoked
- **Definitional home (single canonical definition):** `R-EFFECT-04` (FINAL1 §11)
- **Cross-references (reference-by-ID; no restatement):** `R-CORE-12`, `R-CORE-14`, `R-BUDGET-10`, `R-DUR-07`
- **Variables:** the five assertions of R-EFFECT-04 evaluated per gate 1–16
- **Domains:** every denial, including persistence-failure denials (R-DUR-07) and mailbox admission (R-ACTOR-10 sender-fault path)
- **Quantification:** ∀ denial events: Σ′ = Σ with the declared fault observable
- **Applicable state/transition context:** request transition; live journal failure path (pre-s12 rollback)
- **Preservation notes / carried limitations:** Faults are data (never panics, R-CORE-12); resource-state atomicity is the resource-level refinement (R-BUDGET-10). The post-issuance host-failure path is the one declared exception shape (`c_issue` stays consumed).

#### GI-SEC-11 — Planner observation opacity

- **Canonical formula (identification quote; normative home below):** `contains_capability(Observation) = false` (recursive, events included); `Capability ∉ Observables(LLM)`; planner-visible `EffectIssued` carries `{id, actor, digest}` only
- **Definitional home (single canonical definition):** `R-PLANNER-07` (FINAL1 §16)
- **Cross-references (reference-by-ID; no restatement):** `R-KERN-03`, `R-MARSHAL-06`, `R-PLANNER-01`
- **Variables:** `Observation` — planner-facing projection; `CapabilitySummary` — non-referential projection
- **Domains:** every machine state and observation emission; canonical encodings of planner-facing data
- **Quantification:** ∀ states, ∀ emissions
- **Applicable state/transition context:** agent loop (ror-agent); observation projection rule
- **Preservation notes / carried limitations:** 0x30/0x05 payloads absent from planner-facing encodings by property, not by convention; negative golden vectors are normative fixtures (R-CANON-11/12).

#### GI-SEC-12 — LLM non-authority

- **Canonical formula (identification quote; normative home below):** `LLMOutput ∈ Data`; `LLM output ∉ TCB authority`; planner MUST NOT allocate/authorize/modify/invoke
- **Definitional home (single canonical definition):** `R-PLANNER-02` (FINAL1 §16)
- **Cross-references (reference-by-ID; no restatement):** `R-TRUST-01`, `R-TRUST-02`, `R-PLANNER-01`, `R-KERN-06`, `R-ARCH-01`
- **Variables:** planner — probabilistic proposal engine
- **Domains:** all planner outputs, all loop iterations
- **Quantification:** ∀ planner interaction
- **Applicable state/transition context:** agent loop entry to the ordinary compile path only
- **Preservation notes / carried limitations:** Negative guarantee, preserved at full strength: the R-TRUST-04 addendum also bars the planner module from *providing* any security/runtime dependency — security obligations are never discharged inside LLM-facing crates.

#### GI-SEC-13 — Proposal staleness is exact-equality causal binding

- **Canonical formula (identification quote; normative home below):** `AcceptProposal(p) ⇔ p.observation_sequence = current_planning_epoch` (either-direction mismatch ⇒ `Fault::StalePlan`, zero mutation)
- **Definitional home (single canonical definition):** `R-PLANNER-06` (FINAL1 §16)
- **Cross-references (reference-by-ID; no restatement):** `R-PLANNER-03`, `R-PLANNER-05`, `R-CORE-12`
- **Variables:** `p.observation_sequence`, `current_planning_epoch`
- **Domains:** every proposal acceptance; future-tagged proposals included
- **Quantification:** ∀ p
- **Applicable state/transition context:** planner boundary, pre-compilation
- **Preservation notes / carried limitations:** Superseded strictly-less reading is quoted, not deleted; the C-38 single-check description is corrected by this addendum — recorded.

#### GI-SEC-14 — Fault totality and transition atomicity

- **Canonical formula (identification quote; normative home below):** `Σ →_c Σ'` either completes (all durable effects appended) or faults with the five R-EFFECT-04 assertions; no died-mid-transition outcome; every fallible op returns `Result`; `unwrap`/`expect`/`panic!` forbidden on machine paths
- **Definitional home (single canonical definition):** `R-CORE-12` (FINAL1 §02)
- **Cross-references (reference-by-ID; no restatement):** `R-EFFECT-04`, `R-BUDGET-02`, `R-REPO-03`, `audit/_conservation_checker.py`
- **Variables:** every machine transition; `Fault::InternalInvariant` family for check/commit drift
- **Domains:** evaluator, kernel, budget, persistence, runtime transitions (non-test paths)
- **Quantification:** ∀ transitions, ∀ failure modes
- **Applicable state/transition context:** trusted boundary
- **Preservation notes / carried limitations:** The mid-transition window is removed, not merely its panic failure mode (journal-driven commit). Mutation M034 registered; no execution evidence — stays SPECIFIED.

#### GI-SEC-15 — Closed declared fault surface

- **Canonical formula (identification quote; normative home below):** every trust-boundary crossing's fault set is frozen and declared; opaque codes/digests only for external error text; resume-vs-fault/budget/log effects pinned per variant
- **Definitional home (single canonical definition):** `R-CORE-13` (FINAL1 §02)
- **Cross-references (reference-by-ID; no restatement):** `R-CALC-06`, `R-EFFECT-08`, `R-REF-05`, `R-DUR-07`
- **Variables:** machine-fault enumeration incl. replay-path variants, `StalePlan`, unified `MarshalFault`, `InternalInvariant` family
- **Domains:** host→machine, storage→recovery, planner→machine crossings
- **Quantification:** ∀ crossing, ∀ fault variant
- **Applicable state/transition context:** fault construction and differential fault comparison
- **Preservation notes / carried limitations:** U-08/U-14 remain OPEN (declared-surface work continues); the closed-set *rule* is frozen while the enumeration work is tracked — the addendum closes them only `in the security direction`, and this row preserves that distinction (no upgrade of the register rows).

#### GI-SEC-16 — Kernel possession gate

- **Canonical formula (identification quote; normative home below):** `Authorized_gated(actor, c, E, t) ⇔ c ∈ CapabilityContext(actor) ∧ Valid(c,t) ∧ Authorized(κ(c), E, t)`; `CapRef ≠ authority ownership`
- **Definitional home (single canonical definition):** `R-KERN-04` (FINAL1 §06)
- **Cross-references (reference-by-ID; no restatement):** `R-KERN-01`, `R-KERN-02`, `R-KERN-03`, `R-KERN-05`, `R-KERN-06`, `R-CAP-06`
- **Variables:** `CapRef {index, generation}`; per-actor possession structure
- **Domains:** every authorization call; recovery must reconstruct possession sets first
- **Quantification:** ∀ authorize/derive calls
- **Applicable state/transition context:** authorization gate 2–4 region; kernel API contract
- **Preservation notes / carried limitations:** Root grant protocol (R-KERN-06): authority enters only via durable `CapabilityGranted`; no runtime minting path — audit of every recovered root authority to its durable record is the verification obligation.

#### GI-SEC-17 — Spawn transfers no authority by default

- **Canonical formula (identification quote; normative home below):** `Expr::Spawn` child authority = ∅ unless an explicit, compiler-checked, strictly attenuated manifest derivation; `Authority(child) ≺ Authority(parent)`
- **Definitional home (single canonical definition):** `R-ACTOR-09` (FINAL1 §09)
- **Cross-references (reference-by-ID; no restatement):** `R-ACTOR-05`, `R-COMPILE-06`, `R-MARSHAL-05`, `R-CORE-04`
- **Variables:** spawn manifest entries; `BudgetAllocationSpec::validate_and_escrow` bounds (U-03 direction, security only)
- **Domains:** all spawn transitions from any (incl. LLM-authored) plan
- **Quantification:** ∀ spawn
- **Applicable state/transition context:** spawn transaction, step 3 (capability derivation)
- **Preservation notes / carried limitations:** Wholesale copying is FORBIDDEN (the `derive(A,⊤)=A` identity path is not spawn); the v0.3 `trust_level` form is superseded-quoted. U-03 stays open for the allocation-policy half — preserved in §29.

#### GI-SEC-18 — Trust table completeness and structural carriability

- **Canonical formula (identification quote; normative home below):** one frozen trust table covering every boundary-enforcing module; crate DAG carries `ror-runtime → ror-persistence`; `ror-core → ror-kernel` forbidden; no security dependency provided by the planner
- **Definitional home (single canonical definition):** `R-TRUST-04` (FINAL1 §03)
- **Cross-references (reference-by-ID; no restatement):** `R-TRUST-01`, `R-TRUST-05`, `R-REPO-02`, `R-REPO-03`, `R-ARCH-05`
- **Variables:** module rows; crate edges; `SECURITY_DEPENDENCY`/`RUNTIME_DEPENDENCY` edges
- **Domains:** repository structure (Cargo DAG, visibility, clippy gates)
- **Quantification:** structural invariant — re-checkable by `dep/_graph.py` (SC-1/2/3 hard gates)
- **Applicable state/transition context:** build-order and review
- **Preservation notes / carried limitations:** Verified *structurally* in this repository only; structural repository integrity is not semantic verification (R-SCOPE-02 discipline).

#### GI-SEC-19 — Reference-model independence

- **Canonical formula (identification quote; normative home below):** zero shared core implementation logic: no `reference_* → production_*` calls for step/authorize/budget/recover/encode/scheduler; shared fixtures MAY be used, shared transitions MUST NOT
- **Definitional home (single canonical definition):** `R-SCOPE-04` (FINAL1 §01)
- **Cross-references (reference-by-ID; no restatement):** `R-REF-02`, `R-REF-04`, `R-RECOV-04`, `R-ARCH-02`
- **Variables:** production↔reference boundary at crate, call, type-identity (`Ref*Id`) levels
- **Domains:** the whole verification architecture
- **Quantification:** ∀ differential comparison
- **Applicable state/transition context:** build structure; harness
- **Preservation notes / carried limitations:** Current state: `REF1-CONDITIONAL` (audit verdict) — several independence properties UNVERIFIED (F-01…F-11), no BLOCKING failure; MUST NOT be rendered PASS (F-INFL-02, BLOCKING-if-converted). The reference model remains an architectural contract: no reference implementation exists and none is manufactured from this specification.

#### GI-SEC-20 — Actor isolation

- **Canonical formula (identification quote; normative home below):** `a ≠ b ⇒ Heap(a) ∩ Heap(b) = ∅ ∧ Env(a) ∩ Env(b) = ∅`; no cross-actor mutation; fresh arenas, `Environment::empty()` (no implicit environment inheritance)
- **Definitional home (single canonical definition):** `R-ACTOR-01` (FINAL1 §09)
- **Cross-references (reference-by-ID; no restatement):** `R-ACTOR-02`, `R-ACTOR-10`, `R-CALC-02`
- **Variables:** actors; heaps; environments; continuations; mailboxes
- **Domains:** every reachable global state
- **Quantification:** ∀ distinct actor pairs
- **Applicable state/transition context:** instantiation, execution, messaging
- **Preservation notes / carried limitations:** Mailbox footprint bounded by reserved `M` (R-ACTOR-10) extends the isolation claim into the heap; the resource-bounded thesis holds at every step.

#### GI-SEC-21 — No unconstrained embedded capability literals

- **Canonical formula (identification quote; normative home below):** compilation faults on any `Value::Capability` literal not substituted by the compiler from the plan's declared capability set
- **Definitional home (single canonical definition):** `R-COMPILE-06` (FINAL1 §05)
- **Cross-references (reference-by-ID; no restatement):** `R-COMPILE-02`, `R-COMPILE-03`, `R-CAP-10`, `U-22`
- **Variables:** `Block` literals; plan capability manifest
- **Domains:** all compilation
- **Quantification:** ∀ plans, ∀ embedded capability values
- **Applicable state/transition context:** compiler capability analysis
- **Preservation notes / carried limitations:** Closes U-22 `in the security direction` only — the J2 effect-set-inference re-spec gap (U-22) stays open (§29).

#### GI-SEC-22 — Rewinding-resistant persistence

- **Canonical formula (identification quote; normative home below):** chained WAL checksums `checksum_n = H(checksum_{n−1} ‖ frame_n)`; snapshot commit covers state digest and last WAL sequence; keyed (MAC/signature) if storage adversarial; `Durable(D) ⇒ Authentic(D)` where keyed
- **Definitional home (single canonical definition):** `R-PERSIST-08` (FINAL1 §14)
- **Cross-references (reference-by-ID; no restatement):** `R-PERSIST-02`, `R-PERSIST-05`, `R-CORE-13`
- **Variables:** WAL frames; snapshot commit records
- **Domains:** all durable artifacts; key-epoch mismatch ⇒ `RecoveryFault`
- **Quantification:** ∀ frames, ∀ snapshots
- **Applicable state/transition context:** append, sync, recovery verification
- **Preservation notes / carried limitations:** Keyless chaining detects corruption/rewinding but does not authenticate — the trust-table assumption is recorded explicitly, not softened.

### Determinism invariants (FINAL1 §24)

#### GI-DET-01 — Determinism theorem

- **Canonical formula (identification quote; normative home below):** `InitialState + SchedulerTrace + HostTrace ⇒ UniqueMachineTrace` (machine level; with a `PlannerAccepted` trace for end-to-end runs, R-PLANNER-04)
- **Definitional home (single canonical definition):** `R-CORE-08` (FINAL1 §02)
- **Cross-references (reference-by-ID; no restatement):** `R-ACTOR-07`, `R-TEST-10`, `N-32`
- **Variables:** the four boxed terms; stochasticity confined above the machine boundary
- **Domains:** all machine executions under identical inputs
- **Quantification:** uniqueness over full traces, not final states only
- **Applicable state/transition context:** state-transition semantics; scheduler; host observation
- **Preservation notes / carried limitations:** PRESERVED LIMITATION (U-35, C-98/C-99, open): the four terms are undefined in all 42,312 source lines and in all five canonical organizations — the unqualified theorem is currently *ill-formed/unfalsifiable*. The compilation records this and does not fix it by defining the terms (R-SCOPE-03). U-36 (Lifetime) is resolved by R-CAP-11; U-37 (fixed integer widths) stays open.

#### GI-DET-02 — Deterministic identity allocation

- **Canonical formula (identification quote; normative home below):** `ActorId`/`EffectId` from global monotonic counters (`N' = N + 1`); never wall-clock, address, UUID, PID, thread-id, or RNG
- **Definitional home (single canonical definition):** `R-ACTOR-03` (FINAL1 §09)
- **Cross-references (reference-by-ID; no restatement):** `R-EFFECT-03`, `R-CALC-03`
- **Variables:** `N` counters; `Symbol(u32)` interned identity
- **Domains:** every allocation site (spawn, request)
- **Quantification:** ∀ allocations, deterministically ordered
- **Applicable state/transition context:** global-state transitions
- **Preservation notes / carried limitations:** `Symbol` interning is the compiler-side half (R-CALC-03); runtime identity never uses `String` keys.

#### GI-DET-03 — FIFO scheduler, at-most-once runnable

- **Canonical formula (identification quote; normative home below):** runnable queue is FIFO with at-most-once membership; `Blocked/Pending/Halted/Faulted` actors are never scheduled; deterministic wake-exactly-once
- **Definitional home (single canonical definition):** `R-ACTOR-04` (FINAL1 §10)
- **Cross-references (reference-by-ID; no restatement):** `R-ACTOR-06`, `R-ACTOR-07`, `SCHED-FIFO`, `SCHED-BLOCKED-NOT-SCHEDULED`
- **Variables:** `RunnableQueue`; actor run-states
- **Domains:** every scheduler turn
- **Quantification:** ∀ turns
- **Applicable state/transition context:** global step
- **Preservation notes / carried limitations:** At-most-once and wake-exactly-once are the mutation-tested shadows (M011/M012). Duplicate runnable entries MUST NOT exist.

#### GI-DET-04 — Logical time only

- **Canonical formula (identification quote; normative home below):** `t` ∈ machine state (logical clock); wall-clock MUST NOT be semantic machine state
- **Definitional home (single canonical definition):** `R-CAP-09` (FINAL1 §06)
- **Cross-references (reference-by-ID; no restatement):** `R-BUDGET-06`, `R-CAP-11`, `R-BUDGET-15`, `R-BUDGET-16`, `N-18`, `N-33`
- **Variables:** `t`, `δ_t`, `W`, `D`, `Lifetime` (logical, half-open per R-CAP-11)
- **Domains:** every time-consuming predicate (authorization `T`, deadline `W`, liveness bound)
- **Quantification:** ∀ transitions
- **Applicable state/transition context:** machine-wide
- **Preservation notes / carried limitations:** The wall-clock `Lifetime` compared inside gate 6 was a determinism defect (DET-002/C-100) — resolved in the logical direction by R-CAP-11 (addendum IX); `LogicalTime ≠ Deadline` and `Lifetime ≠ WallClockInterval` are laws N-18/N-33.

#### GI-DET-05 — One δ_t, one duration debit; quiescence rule

- **Canonical formula (identification quote; normative home below):** every logical-time advance has exactly one `δ_t` (frozen enumeration) and exactly one `ΔD := δ_t` debit; `Deadlock ∧ ∃Pending ⇒ QuiescenceReconcile (δ_t = 0, ΔD = 0)`
- **Definitional home (single canonical definition):** `R-BUDGET-16` (FINAL1 §07)
- **Cross-references (reference-by-ID; no restatement):** `R-BUDGET-06`, `R-BUDGET-15`, `R-BUDGET-09`, `R-RECOV-08`, `R-CAP-09`
- **Variables:** transition kinds; `Pending` effects; `GlobalStep::Deadlock`
- **Domains:** every transition kind; unknown kinds are a checker error, never a default
- **Quantification:** ∀ transitions, ∀ global advances
- **Applicable state/transition context:** scheduler; liveness bound reachability
- **Preservation notes / carried limitations:** Addendum-IX frozen form (D7 condition discharged per the duration audit's §5 evidence). Post-deadline receipts admitted and settled via R-RECOV-08 — the old `t + δ_t ≤ W` receipt premise is superseded-quoted. Blocked-only quiescence admits NO reconciliation.

#### GI-DET-06 — One canonical encoding grammar

- **Canonical formula (identification quote; normative home below):** exactly one byte grammar (Phase 15A BE envelope); all digests/checksums over 15A bytes alone; `Canonical(x) = Canonical(y) ⇒ Digest(x) = Digest(y)`
- **Definitional home (single canonical definition):** `R-CANON-13` (FINAL1 §13)
- **Cross-references (reference-by-ID; no restatement):** `R-CANON-01`, `R-CANON-02`, `R-CANON-09`, `R-CANON-10`, `R-PERSIST-01`
- **Variables:** envelope fields; `TAG_*` single namespace; digest functions
- **Domains:** all serialized payloads (values, effects, records, snapshots, journal)
- **Quantification:** ∀ encoders (production, reference, persistence writer) — golden vectors byte-exact, LE variants rejected
- **Applicable state/transition context:** serialization; persistence framing; differential comparison
- **Preservation notes / carried limitations:** Injectivity is a *scoped structural* claim with machine-checked evidence expected (R-CANON-10) — not a mathematical proof; reverse digest direction holds only under collision-resistance assumption (C-13). The machine-state encodings (U-02) remain UNFROZEN: byte-level determinism of `GlobalState` is an open item, not a closure (it also blocks StateDigest operationalization; U-02 amended by the nondeterminism audit).

#### GI-DET-07 — Replay correspondence

- **Canonical formula (identification quote; normative home below):** `LiveRun(Σ₀) ⇒ T ⇒ ReplayRun(Σ₀, T)` produces the same final configuration, per-step `E_replay,k = E_recorded,k ∧ R_replay,k.id = R_recorded,k.id` (digests in the frozen form)
- **Definitional home (single canonical definition):** `R-HOST-04` (FINAL1 §12)
- **Cross-references (reference-by-ID; no restatement):** `R-HOST-03`, `R-HOST-05`, `R-PLANNER-04`, `R-EFFECT-06`, `R-HOST-06`
- **Variables:** `T` — ordered trace of (EffectIssued, EffectCompleted) pairs; `ReplayHost` consumption
- **Domains:** machine-state replay always; real-world replay only for reversible/idempotent classes
- **Quantification:** ∀ recorded runs
- **Applicable state/transition context:** replay; conformance suite end-to-end replay
- **Preservation notes / carried limitations:** Replay proves machine-state/event reproduction subject to explicit external-effect reconciliation — it does NOT reproduce the external world (nondeterminism audit §5.4, preserved). Unordered-map replay is superseded (R-HOST-03).

### Recovery/persistence invariants (FINAL1 §25)

#### GI-REC-01 — Effect journal causality

- **Canonical formula (identification quote; normative home below):** `Issued ⇒ Prepared`; `Completed ⇒ Issued`; `Reconciled ⇒ Issued`; `Prepared ∧ ¬Issued ⇒ Discard`; `Issued ∧ ¬Completed ⇒ Indeterminate`
- **Definitional home (single canonical definition):** `R-DUR-03` (FINAL1 §11)
- **Cross-references (reference-by-ID; no restatement):** `R-DUR-04`, `R-RECOV-02`, `N-05`, `N-24`, `audit/_crash_consistency_checker.py`
- **Variables:** journal record kinds; identical `(EffectId, EffectDigest)` per effect
- **Domains:** every durable effect record and recovery classification
- **Quantification:** ∀ effects, ∀ crash points T0–T6
- **Applicable state/transition context:** issuance transaction; recovery
- **Preservation notes / carried limitations:** Digest mismatch on a subsequent record is `EffectJournalCorruption`, never a different effect. The persistence audit verified the *contract* (specification-level causal ordering) — that is audit verdict language, not VERIFIED status.

#### GI-REC-02 — Crash recovery equivalence (qualified)

- **Canonical formula (identification quote; normative home below):** `Recover(Snapshot, EventLog, EffectJournal) ≡ PreCrashMachineState` at every defined persistence boundary, PROVIDED every interrupted effect is (a) durably reconciled, (b) idempotent/replayable via recorded receipt, or (c) explicitly `Indeterminate` and prevented from silent continuation
- **Definitional home (single canonical definition):** `R-CORE-09` (FINAL1 §02)
- **Cross-references (reference-by-ID; no restatement):** `R-RECOV-01`, `R-RECOV-02`, `R-RECOV-03`, `R-RECOV-08`, `R-REF-01`
- **Variables:** `D = ⟨S,L,H⟩`; replay; classification lattice
- **Domains:** crashes at defined boundaries only (T0–T6)
- **Quantification:** ∀ defined crash points
- **Applicable state/transition context:** recovery algorithm steps 1–12
- **Preservation notes / carried limitations:** `MUST NOT infer "not executed" from a missing completion record` is part of the invariant (R-CORE-09/R-DUR-04/R-RECOV-07). The recovery-step granularity discrepancy (AMB-27/REQ-RECOV-021: reconciliation inside `Recover(D)` vs after `RecoveryComplete`) is recorded open (§29; persistence audit residual).

#### GI-REC-03 — No silent repair

- **Canonical formula (identification quote; normative home below):** `Invalid(D) ⇒ RecoveryFault`; recovery MUST NOT drop duplicate runnable actors, adjust budget mismatches, ignore sequence gaps, or ignore checksum failures
- **Definitional home (single canonical definition):** `R-RECOV-05` (FINAL1 §15)
- **Cross-references (reference-by-ID; no restatement):** `R-CORE-10`, `R-PERSIST-06`, `R-PERSIST-08`, `R-RECOV-09`
- **Variables:** corruption classes; stale-counter reconstruction
- **Domains:** every recovery run; counter *advancement* is recorded, never silent (R-RECOV-09)
- **Quantification:** ∀ invalid durable states
- **Applicable state/transition context:** recovery validation steps
- **Preservation notes / carried limitations:** mod/18 D-07 canonical home R-RECOV-05. A snapshot counter greater than the journal maximum is a fault; `SnapshotCommit` inside the s12–14b section is a fault.

#### GI-REC-04 — Escrow survives crash; disposition total

- **Canonical formula (identification quote; normative home below):** `Issued ∧ ¬Completed ⇒ escrowed complete_max retained until durable reconciliation`; every escrowed unit leaves via exactly one frozen path (`Completed` / host-failure consumption / durable `Reconciled`); `Remains-Indeterminate` is a bounded transient
- **Definitional home (single canonical definition):** `R-DUR-05` (FINAL1 §11)
- **Cross-references (reference-by-ID; no restatement):** `R-BUDGET-09`, `R-BUDGET-11`, `R-DUR-06`, `R-BUDGET-16`, `R-RECOV-08`
- **Variables:** `C_escrowed`; per-effect `EffectCost` reconstructed from durable payload
- **Domains:** all crash points; live faults unify with crash reconciliation
- **Quantification:** ∀ escrow entries; quiescent states contain no un-movable escrow
- **Applicable state/transition context:** issuance; recovery; quiescence driver
- **Preservation notes / carried limitations:** R-DUR-06 (durable payload with cost) is what makes survival reconstructible at every T0–T6 point — before addendum VII the persistence audit called escrow survival *realizable but unprovable-as-frozen*; that history is preserved in the C-103…C-109 lineage, and current status remains SPECIFIED.

#### GI-REC-05 — Budget and counter restoration

- **Canonical formula (identification quote; normative home below):** three-way partition invariant survives crashes identically; `next_effect_id = max({id ∈ replayed EffectIssued}) + 1` (stale counter advanced and recorded; greater-than-journal ⇒ `RecoveryFault`)
- **Definitional home (single canonical definition):** `R-RECOV-06` (FINAL1 §15)
- **Cross-references (reference-by-ID; no restatement):** `R-RECOV-09`, `R-BUDGET-05`, `R-RECOV-03`
- **Variables:** budget partitions; effect-ID counter
- **Domains:** every recovery
- **Quantification:** ∀ recovered states
- **Applicable state/transition context:** recovery steps 4/11
- **Preservation notes / carried limitations:** T1 discard restores from the record (R-DUR-06); no budget discrepancy may be silently adjusted; restoration has a source of truth (pre-addendum-VII it had none — recorded in C-105 lineage).

#### GI-REC-06 — Indeterminate irreducibility

- **Canonical formula (identification quote; normative home below):** `Indeterminate` is resolvable ONLY by authoritative host reconciliation evidence; no component (trusted or not) may resolve `Indeterminate ⇒ NotExecuted` (or ⇒ `Completed`) on local policy
- **Definitional home (single canonical definition):** `R-RECOV-08` (FINAL1 §15)
- **Cross-references (reference-by-ID; no restatement):** `R-DUR-04`, `R-RECOV-07`, `R-CORE-09`, `N-24`, `R-CLAIM-02`
- **Variables:** `ReconciliationOutcome {Completed(EffectReceipt), NotExecuted, Indeterminate}` (closed set, L26593–26597; per-class admissibility = U-15's remaining question)
- **Domains:** interrupted effects; supervisor policy
- **Quantification:** ∀ outcomes
- **Applicable state/transition context:** reconciliation protocol
- **Preservation notes / carried limitations:** Receipts recorded what the machine was TOLD, not what happened; the Indeterminate class is irreducible (nondeterminism audit §5.4). R-RECOV-08 freezes never-re-execute, idempotent-query-at-most, and `NotExecuted` gated behind authoritative evidence.

#### GI-REC-07 — Sequence continuity and snapshot atomicity

- **Canonical formula (identification quote; normative home below):** `s_{n+1} = s_n + 1` (gap ⇒ reject); snapshot atomic protocol `Begin → payload → fsync → Commit(state_digest)`; incomplete snapshots discarded; WAL payload is *only* 15A bytes
- **Definitional home (single canonical definition):** `R-PERSIST-06` (FINAL1 §14)
- **Cross-references (reference-by-ID; no restatement):** `R-PERSIST-01`, `R-PERSIST-02`, `R-PERSIST-05`, `R-DUR-07`
- **Variables:** `WalSequence`; snapshot markers; `state_digest`
- **Domains:** all durable writes; the persistence layer records and reconstructs; it is not a semantic machine
- **Quantification:** ∀ frames, ∀ snapshots
- **Applicable state/transition context:** append path; recovery scan
- **Preservation notes / carried limitations:** `No secondary serialization` (R-PERSIST-01) plus U-02: until machine-state encodings are frozen, `state_digest` is required but uncomputable per the register — recorded open, both facts stand.

## 2. Mathematical symbols — one canonical meaning per use-context

The compilation adopts the cleaned set's convention that math symbols keep the source's notation (`spec/00` §6); FINAL1 does not rename anything frozen. The table assigns exactly one canonical meaning per symbol **use**; where the frozen source itself reuses a letter, the reuse is recorded as an `FA-nn` ambiguity row (§3) rather than silently reinterpreted.

| Symbol | Canonical meaning | Defined in | Notes |
|---|---|---|---|
| `E` | a single effect (request/issued/completed lifecycle object) | R-CALC-04; R-CORE-02 | — |
| `P` | the executable plan under which an effect was requested | R-CORE-02 (homonym resolved by R-CORE-11) | FA-10 pointer: `ValidatedPlan` type-vs-predicate split lives at X-01/C-46, not here |
| `Σ`, `Σ′`, `Σ₀` | local configuration `⟨e, ρ, κ, B, t, H, L⟩` (and post-state/initial) | R-CALC-08 | — |
| `G` | global configuration `⟨A, t, L, R, E_journal⟩` | R-CALC-08 | overloaded `A`/`L`/`R` uses resolved per FA-01/FA-04 |
| `D` (budget) | the duration consumable: per-actor remaining execution-duration budget | R-BUDGET-01/15 | FA-02: `D = ⟨S,L,H⟩` (durable state, R-RECOV-01) is a different object reusing the letter |
| `D` (durable) | durable recovery input `⟨S, L, H⟩` | R-RECOV-01 | FA-02 |
| `B` | the actor budget `⟨C, R, W⟩` | R-BUDGET-01 | FA-09: static bound `@ B`/`B_max` in the compilation judgment (R-COMPILE-03) is the plan-time upper bound, not the dynamic `B` |
| `C` (budget) | the consumable vector `⟨F, I, D⟩` and its partitions `C_available/C_escrowed/C_consumed` | R-BUDGET-01/05/11 | FA-07: bare `C` is ALSO the `Constraint` argument of `derive(A,C)` (R-CAP-05) |
| `R` (budget) | the reserved-capacity vector `⟨M, S⟩` | R-BUDGET-01 | FA-04: `R_A` is the capability resource ceiling (R-CAP-06); `R` is the third component of `G` (R-CALC-08) |
| `W` | absolute logical-time deadline, `ℕ ∪ {∞}`; `Deadline(None)` = ∞ | R-BUDGET-01; N-18 | — |
| `M`, `S` (budget) | reserved memory bytes; reserved concurrency slots | R-BUDGET-01 | FA-05: `S` is also the scope domain (R-CAP-01) and the snapshot component (R-RECOV-01) |
| `t` | logical time (machine state, never wall clock) | R-CAP-09 | — |
| `δ_t(c)` | the frozen logical-time delta of transition `c` (exhaustive table) | R-BUDGET-06/16 | — |
| `ΔD` | the duration debit for a logical-time advance (`ΔD := δ_t`, exactly one) | R-BUDGET-15 | — |
| `κ` | the holder's capability context map (`κ_holder(c) → Authority`) | R-CORE-02; R-KERN-02; canonical signature by R-CORE-11 | — |
| `ρ` | local environment (name → value bindings) | R-CALC-08; R-CEK-03/04 | — |
| `A` (algebra) | authority `= {(o, ⟨S,Q,R,T⟩)}`, operation-indexed | R-CAP-01/02 | FA-01: `A` in `G = ⟨A, …⟩` is the actor map — same letter, different object |
| `O` | the finite enumerable operation set (`O_granted ⊆ O`) | R-CAP-01/02 | — |
| `S` (scope), `Q`, `T` | scope domain with interpretation `⟦A_op.S⟧`; parameter predicate; logical lifetime interval | R-CAP-01/06; R-CAP-11 (half-open) | FA-05; FA-10 (T0–T6 crash labels are subscripts, distinct from lifetime `T`) |
| `≼` | authority partial order (per-operation meet comparison) | R-CAP-03 | — |
| `≺` | strict authority order (spawn security theorem only) | R-ACTOR-09 | `≼` is reserved for delegation — the two are NOT interchangeable |
| `⊓` | meet within a semantic domain | R-CAP-05 | — |
| `⇒`, `⇔`, `∧`, `¬`, `∀`, `∃` / `□` | implication; equivalence; conjunction; negation; quantifiers; `□` = “invariant over all reachable states” (used in this registry only) | final/05 notation | — |
| `↛`, `⇏` | does not (entail / imply): the negative guarantees | R-CORE-01; R-COMPILE-01 (`Block ⇏ ExecutablePlan`) | — |
| `≻` | version-supersession ordering of source texts (editorial notation only; not machine semantics) | spec/00 §6 | — |
| `ε` | the empty continuation (`Value ∧ K = ε ⇒ Halt`) | R-CEK-02 | — |
| `K` | continuation | R-CEK-01/02/03 | — |
| `c` | a capability reference/`CapRef` handle when bounded by possession (gate form) | R-KERN-04; R-CORE-11 | also the transition label in `Σ →_c Σ'` (R-EFFECT-02); context decides |
| `e` | the current term under evaluation in `Σ` | R-CALC-08 | FA-08: `Authorized(c, e, t)` (R-EFFECT-01 step 4) uses `e` for the effect; canonical effect symbol is `E` |
| `V`, `v` | value-domain element of the machine (11 variants) | R-CALC-01 | — |
| `derive`, `attenuate`, `delegate` | algebra operation; machine CEK operation; cross-actor authority transfer | R-CAP-05; R-CEK-03; R-MARSHAL-02/05; N-29 | three names, three distinct operations — never conflated |
| `marshal` / `unmarshal` | boundary crossing with capability rejection / admission revalidation | R-MARSHAL-01/03/06 | — |
| `contains_capability(v)` | the frozen total predicate over reachability | R-MARSHAL-06 | — |
| `Canonical(x)`, `StateDigest`, `EffectDigest`, `ResultDigest` | 15A bytes; SHA-256 digests over canonical bytes | R-CANON-09/13; R-HOST-06 | — |
| `ExternalEffect`, `HostInvoked`, `DurableIssued`, `Prepared`, `Issued`, `Completed`, `Reconciled` | event/record predicates with exactly the signatures defined in §02/§11/§13/§15 | R-CORE-02/11; R-DUR-03; R-EFFECT-* | — |
| `ValidatedRequest(E)`, `ValidatedPlan_pred(P)` | request-time validation predicate; disambiguated plan-predicate reading | R-CORE-11 | type homonym `ValidatedPlan_struct` is X-01/U-23 — predicate and struct never interchangeable |
| `Authorized(...)`, `Authorized_gated(...)` | canonical authorization forms (holder-first) | R-CORE-11; R-KERN-04 | authority-first `Authorized(A,E,t)` reading SUPERSEDED (quoted in R-CORE-11) |
| `Live(c)`, `Ancestors(c)` | kernel liveness; lineage chain | R-CAP-07 | — |
| `Recover(D)`, `Replay(S,L,H)`, `LiveRun`, `ReplayRun` | recovery/replay functions | R-RECOV-01; R-HOST-04 | — |
| `N` | the monotonic allocation counter (`N' = N + 1`) | R-EFFECT-03; R-ACTOR-03 | — |
| `f` | the frozen monotone per-byte send-cost lower bound | R-ACTOR-10 | — |
| `Γ` | typing context in the compilation judgment | R-COMPILE-03 | — |
| `F` (judgment) | the possible-effects set (conservative over-approximation; pure ⇒ `F = ∅`) | R-COMPILE-03 | FA-06: also `F` = fuel dimension (R-BUDGET-01) and v1 fault grammar `F` (C-58) |
| `⟦·⟧` | scope interpretation | R-CAP-06 | — |

## 3. Preserved symbol reuse (FINAL1 `FA-nn` records)

| ID | Symbol | Reuse in frozen notation | Disambiguation rule | Status |
|---|---|---|---|---|
| `FA-01` | `A` | authority tuple (R-CAP-01, source L6354–6379) vs the actor map component of `G = ⟨A, t, L, R, E_journal⟩` (R-CALC-08, L24148–24163) | Within FINAL1 rendering, `A` alone = authority; the actor map appears only inside the named tuple `G`. No renaming of the source formulas is performed. | preserved; notation-level, owner may fold into a future editorial pass |
| `FA-02` | `D` | duration consumable (R-BUDGET-01, frozen semantics R-BUDGET-15) vs durable-state `D = ⟨S, L, H⟩` / `Recover(D)` (R-RECOV-01) | Budget contexts read `D` as the consumable; recovery contexts read `D` as the durable triple. R-BUDGET-15 disambiguates the *semantics* of the budget side (addendum IX) but the letter collision itself is a frozen-notation fact and stays recorded. | preserved |
| `FA-03` | `H` | isolated heap component of `Σ` (R-CALC-08) vs durable effect journal `H` (R-RECOV-01) | Disambiguated by tuple membership; never used bare outside a named configuration. | preserved |
| `FA-04` | `R` | reserved-capacity vector `⟨M,S⟩` (R-BUDGET-01) vs capability resource ceiling `R`/`R_A` (R-CAP-01/06) vs the `G` component `R` (R-CALC-08) | Subscripts (`R_A`, `R_max`) and tuple membership are the disambiguators; the ceiling conjunct of the authorization predicate is always cited as `cost ≤ A_op.R`. | preserved |
| `FA-05` | `S` | reserved slots `R=⟨M,S⟩` (R-BUDGET-01) vs scope domain `S` in `⟨S,Q,R,T⟩` (R-CAP-01) vs snapshot component `S` (R-RECOV-01) | Tuple membership disambiguates; `⟦A_op.S⟧` marks the scope reading explicitly. | preserved |
| `FA-06` | `F` | fuel dimension of `C=⟨F,I,D⟩` (R-BUDGET-01) vs possible-effects set in the compilation judgment (R-COMPILE-03) vs the v1 fault grammar `F` (source L1949; recorded at C-58) | FINAL1 text uses the long names (`fuel`, `possible-effects set`, `fault grammar`) outside formula quotes. C-58 already records the grammar-level homonymy; this row adds the budget/judgment overload. No symbol is renamed. | preserved; C-58 (X-68) remains the authoritative record for the taxonomy level |
| `FA-07` | `C` | consumables vector (R-BUDGET-01) vs the `Constraint` argument in `derive(A, C)` (R-CAP-05) | `C` bare = constraint only inside algebra formulas (`derive`, `Satisfies`); budget partitions always carry subscripts (`C_available`, …). | preserved |
| `FA-08` | `e` | current term of `Σ` (R-CALC-08) vs effect instance in `Authorized(c, e, t)` (R-EFFECT-01 step 4) | Canonical effect symbol is `E`; the step-4 `e` is transcribed verbatim from the cleaned authority and is *not* silently corrected. | preserved |
| `FA-09` | `B` | dynamic actor budget (R-BUDGET-01) vs static plan-time upper bound `@ B`, `B_max` (R-COMPILE-03) | Named forms (`B_max`) are used for the static bound; the judgment `Γ; κ_static ⊢ e : τ ! F @ B` is quoted as frozen notation. | preserved |
| `FA-10` | `T` | lifetime component of `⟨S,Q,R,T⟩` (R-CAP-01, retyped logical by R-CAP-11) vs crash-point labels `T0…T6` (R-RECOV-02) | Bare `T` = lifetime; `T<i>` subscripts = crash points. Noted as benign; recorded for completeness of the one-meaning audit. | preserved; benign-by-context, no action requested |

These are **not** `U-nn` decisions (FINAL1 creates none): they are compilation-level ambiguity records in the sense the FINAL1 instruction requires — conflicts preserved, not chosen between. Owners of `spec/06`/`spec/09` may choose to promote them to register rows; nothing here assumes that has happened.

## 4. Single-home discipline (inherited duplication register)

The cleaned set already resolved cross-section duplication: `mod/18`'s marked-duplication register assigns each central invariant exactly one canonical home. FINAL1 honors it and is the canonical *index* of that resolution:

| D-ID | Kind | Members | Canonical home (per `mod/18`) |
|---|---|---|---|
| D-01 | central | R-CORE-04 ⇄ R-CAP-05 | R-CAP-05 (MOD-03 CAPABILITY) |
| D-02 | central | R-CORE-05 ⇄ R-BUDGET-05 | R-BUDGET-05 (MOD-04 BUDGET) |
| D-03 | central | R-CORE-06 ⇄ R-DUR-01 | R-DUR-01 (MOD-11 PERSISTENCE) |
| D-04 | central | R-CORE-07 ⇄ R-MARSHAL-01 | R-MARSHAL-01 (MOD-06 ACTOR) |
| D-05 | central | R-CORE-08 ⇄ R-ACTOR-07 | R-ACTOR-07 (MOD-07 SCHEDULER) |
| D-06 | central | R-CORE-09 ⇄ R-RECOV-02 ⇄ R-RECOV-03 | R-RECOV-02 (MOD-12 RECOVERY) |
| D-07 | central | R-CORE-10 ⇄ R-RECOV-05 | R-RECOV-05 (MOD-12 RECOVERY) |
| D-08 | distribution | R-CORE-03 ⇄ R-CAP-06 ⇄ R-EFFECT-02 | R-CAP-06 (MOD-03 CAPABILITY) |
| D-09 | central | R-TRUST-03 ⇄ R-KERN-03 | R-KERN-03 (MOD-03 CAPABILITY) |
| D-10 | verbatim | R-SCOPE-04 ⇄ R-REF-02 | R-REF-02 (MOD-14 REFERENCE) |
| D-11 | distribution | R-ARCH-03 ⇄ R-COMPILE-01 ⇄ R-COMPILE-05 | R-COMPILE-01 (MOD-02 COMPILER) |
| D-12 | refinement | R-CORE-02 ⇄ R-EFFECT-03 | R-EFFECT-03 (MOD-08 EFFECT) |

Where a `D-` row and a `GI-` row cover the same invariant (D-01…D-12 vs GI-SEC-02/03/04/06/07/08/19, GI-DET-01, GI-REC-02/03), the *home* is identical — `final/05` adds formal metadata; it does not relocate or restate the definition.
