# Red-on-Rust — FINAL1 Canonical Specification

**Compiled:** 2026-09-03 (FINAL1 specification-compiler pass).
**Method:** canonicalization of the cleaned Red-on-Rust sections, requirements,
invariants, dependencies, terminology, security constraints, persistence rules,
effect semantics, recovery rules, reference-model constraints, and verification
obligations into ONE canonical specification in the FINAL1-mandated 29-section
order, with global invariants consolidated (`GI-*`, registry `final/05`), one
stable ID per normative requirement (registry `final/03`), and evidence states
carried at exactly their support (`final/08`).
**Rule (inherited verbatim from the cleaned authority):** where any rendering and
the frozen source differ, the source's latest frozen text governs; discrepancies
are recorded (spec/00 §1), never silently corrected. FINAL1 performed no
architectural design, adjudicated no unresolved finding, converted no audit
recommendation into a requirement, and reopened neither Addenda VII–IX nor U-38.

Every requirement row below is transcribed **verbatim** (whitespace-normalized)
from `spec/01` (the cleaned normative text); requirement IDs are never
renumbered, reused, or reinterpreted. Each row retains its cleaned-provenance
annotation (source line ranges / addendum records); provenance to the frozen
transcript is reconstructible through `spec/03`/`req/` (`source → cleaned
authority → canonical definition → requirement → verification state`).

**Reading conventions.** `R-…`, `C-…`, `U-…`, `X-…`, `N-…`, `T-…`, `V-…`,
`GI-…`, `FA-…`, `M0NN`, and obligation tags are stable IDs resolvable as
described in §01.4. References of the form `S-nn` (cleaned section) or bare
`NN` (a `spec/` file) inside transcribed rows resolve through the tables of
`final/02`; they are frozen text and were not rewritten.


**FINAL1 compilation status.**

```
RED-ON-RUST
ARCHITECTURE FROZEN
IMPLEMENTATION READY
```

`IMPLEMENTATION READY` means this specification is sufficiently canonicalized and
internally structured to guide implementation. It explicitly does **not** mean
`IMPLEMENTED`, `TESTED`, `VERIFIED`, `PROVEN`, or `PRODUCTION READY`, and no such
stronger meaning may be inferred from this document or anywhere else in the
repository. The repository remains at the source-defined `BOOTSTRAP` state
(R-SCOPE-02): no Cargo workspace, no crate, no Rust source, no executed tests, no
golden-vector runs, no mutation runs, no crash-harness runs, no CI configuration,
no proof artifacts (spec/07 §1). The Rust code blocks inside the frozen source are
*specification artifacts* — normative as text, not implementations.

Conditions reported rather than absorbed (each carried in §29 / `final/09`, none
silently resolved by this compilation): `REF1-CONDITIONAL`; `V1-CONDITIONAL`;
machine-state canonical encodings (U-02); the determinism theorem's undefined
terms (U-35); the open fault-surface work (U-08/U-14); the remaining
28 open architectural-decision rows as computed in `final/09`.



---

## §01 Scope

### §01.0 Status, scope of this compilation, and conventions (canonicalization front matter)

This section is the compilation's own framing. The normative scope rows
(R-SCOPE-01…04) follow verbatim. Four conventions bind every section:

1. **Artifact classes.** `SPECIFICATION ≠ IMPLEMENTATION ≠ TEST ≠ VERIFICATION ≠
   PROOF` (laws N-06…N-08). This document is a specification compilation. It
   contains, and may only contain, specification text, registries, and evidence
   *accounting*. §28 states the exact status of every claim class.
2. **Status ladder.** `SPECIFIED → IMPLEMENTED → TESTED → VERIFIED → PROVEN`,
   promotion only by explicit repository evidence (defined canonically in §28;
   identical to spec/00 §2). UNKNOWN is reserved for genuinely ambiguous
   contract-level evidence (V1 §8), never for merely-missing implementation.
3. **Reference resolution.** `S-nn` → cleaned section (alias map, `final/02`
   §2); bare numeric `NN` → `spec/NN` cleaned-document set; prefixed
   `spec/NN`, `mod/NN`, `req/NN`, `dep/NN`, `term/NN`, `audit/name` → repository
   files (all verified to exist by `final/_build.py`); `crates/ror-*` and
   `tests/…`/`vectors/…` paths are *frozen design intent* (R-REPO-01) and are
   never claimed to exist in this repository (spec/07 §1).
4. **Invariants.** Global machine-wide invariants carry `GI-…` IDs (§23–§25
   index; `final/05` formal registry: canonical statement home, variables,
   domains, quantifiers, state/transition context). Invariant definitions are
   single-homed; every other mention is a reference by ID. Mathematical symbols
   have exactly one canonical meaning per `final/05` §2; source-frozen symbol
   reuse is recorded as `FA-01…FA-10` (§29) rather than silently reinterpreted.


Canonical scope obligations: the thesis sentence, the freeze/evidence discipline, the STOP-and-report process rule, and the production↔reference separation. Supersedes nothing: these four requirements are quoted verbatim from the cleaned authority (`spec/01` S-01). The document-status and governance rule of the cleaned set is restated here as §01.0 below; the status ladder itself is canonically defined in §28 (Evidence Model).

**Canonical homes transcribed in this section (4):** `R-SCOPE-01`, `R-SCOPE-02`, `R-SCOPE-03`, `R-SCOPE-04`.

**R-SCOPE-01.** Red-on-Rust MUST be a deterministic, capability-scoped, resource-bounded, crash-recoverable execution machine for probabilistically generated programs. It MUST serve as a Rust-based execution substrate for a family of homoiconic, dialect-oriented languages inspired by the REBOL/Red lineage. [INFORMATIVE: "deterministic" is explicitly defined in S-02 / R-CORE-08 as InitialState + SchedulerTrace + HostTrace ⇒ UniqueMachineTrace]. *(Provenance: turn [60]/README "Core Thesis"; L41293–41300.)*

<!-- FINAL1: R-SCOPE-01 canonical home; cleaned authority spec/01 S-01; registry row final/03; status SPECIFIED -->

**R-SCOPE-02.** The architecture, specification, reference contract, and verification contract MUST be maintained as FROZEN. The repository MUST remain in BOOTSTRAP state until implementation evidence is provided. A frozen specification MUST NOT be construed as a verified implementation; frozen status MUST indicate requirement stability without asserting evidence of conformance. *(L38929–38942, L41297–41315.)*

<!-- FINAL1: R-SCOPE-02 canonical home; cleaned authority spec/01 S-01; registry row final/03; status SPECIFIED -->

**R-SCOPE-03 (normative process rule).** The implementer MUST NOT redesign, reinterpret, simplify away, or silently modify frozen semantics (CEK semantics, evaluation order, lexical scoping, closure semantics, capability algebra, attenuation, revocation, budget algebra, effect authorization, effect issuance protocol, actor isolation, deterministic scheduling, marshalling rules, delegation semantics, canonical serialization, persistence protocol, crash matrix, recovery classification, LLM trust boundary, reference-model independence, differential-testing contract). If implementation difficulty exposes an ambiguity, the implementer MUST STOP and report it; semantic ambiguity MUST NOT be resolved by inventing behavior. [INFORMATIVE: "deterministic scheduling" is explicitly defined in S-15 / R-ACTOR-07]. *(L37664–37686.)*

<!-- FINAL1: R-SCOPE-03 canonical home; cleaned authority spec/01 S-01; registry row final/03; status SPECIFIED -->

**R-SCOPE-04.** The production implementation and the executable reference model MUST share zero core implementation logic (no `reference_* → production_*` calls for step, authorize, budget, recover, encode, scheduler). Shared semantic test fixtures MAY be used; shared transition implementations MUST NOT be used. *(L37696–37721.)*

<!-- FINAL1: R-SCOPE-04 canonical home; cleaned authority spec/01 S-01; registry row final/03; status SPECIFIED -->


---

## §02 Architectural Thesis

The architectural thesis: the central negative invariant, the seven-conjunct external-effect chain, the cross-cutting core invariants (including the frozen post-audit addenda R-CORE-11…R-CORE-14), the component architecture, and the repository/crate structure with its frozen addendum-VI placement decisions. Global invariants defined in this section carry canonical `GI-` IDs registered in `final/05` and indexed in §23–§25; their normative text is defined here, exactly once, and referenced from elsewhere by ID.

**Canonical homes transcribed in this section (22):** `R-CORE-01`, `R-CORE-02`, `R-CORE-03`, `R-CORE-04`, `R-CORE-05`, `R-CORE-06`, `R-CORE-07`, `R-CORE-08`, `R-CORE-09`, `R-CORE-10`, `R-CORE-11`, `R-CORE-12`, `R-CORE-13`, `R-CORE-14`, `R-ARCH-01`, `R-ARCH-02`, `R-ARCH-03`, `R-ARCH-04`, `R-ARCH-05`, `R-REPO-01`, `R-REPO-02`, `R-REPO-03`.

**R-CORE-01 (central external-effect invariant).** The machine MUST enforce the central external-effect invariant: `LLMOutput ∧ UntrustedInput ↛ ExternalEffect`. The central security boundary MUST be the machine; neither the language surface nor the model generating the program MUST be treated as a security boundary. *(L41320–41335; L27505–27513.)*

<!-- FINAL1: R-CORE-01 canonical home; cleaned authority spec/01 S-02; registry row final/03; status SPECIFIED -->

**R-CORE-02 (external-effect chain).** An ExternalEffect(E) MUST NOT occur unless the complete validation chain holds invariant: `ExternalEffect(E) ⇒ ValidatedRequest(E) ∧ Authorized(E,κ,t) ∧ CapabilityWithinCeiling(E) ∧ BudgetAvailable(E) ∧ DeadlineValid(E,t) ∧ HostPolicyOK(E) ∧ Issued(E)` — the first conjunct and the predicate signatures are those frozen by R-CORE-11, which establishes `ValidatedRequest(E)` (request-time validation inside the 16 gates) as the canonical first predicate with the subsumption `ValidatedRequest(E) ⇒ ValidatedPlan(plan(E))`; the source's earlier `ValidatedPlan(P)` first-conjunct form is superseded by R-CORE-11 (quoted there, not deleted), and the chain is stated once, over R-CORE-11's exact signatures.
*(L41337–41351; L27491–27509.)*

<!-- FINAL1: R-CORE-02 canonical home; cleaned authority spec/01 S-02; registry row final/03; status SPECIFIED -->

**R-CORE-03 (no unauthorized effects).** If an effect E is not authorized, the machine MUST NOT produce an ExternalEffect: `¬Authorized(A,E,t) ⇒ ¬ExternalEffect(E)` (equivalently `¬Authorized ⇒ ¬Request` at the operational level). *(L42056–42064; L7413–7419.)*

<!-- FINAL1: R-CORE-03 canonical home; cleaned authority spec/01 S-02; registry row final/03; status SPECIFIED -->

**R-CORE-04 (no authority amplification).** Capability derivation MUST NOT amplify authority: `derive(A,C) ≼ A` MUST hold invariant for all authorities A and constraints C. *(L42066–42072; L6399–6406.)*

<!-- FINAL1: R-CORE-04 canonical home; cleaned authority spec/01 S-02; registry row final/03; status SPECIFIED -->

**R-CORE-05 (no budget teleportation).** Budget accounting MUST maintain the partition invariant `C_available + C_escrowed + C_consumed = C_initial`; actor spawn MUST be executed as a budget ownership transfer, MUST NOT create new budget, and MUST NOT consume budget. *(L42074–42080; L28203–28240.)*

<!-- FINAL1: R-CORE-05 canonical home; cleaned authority spec/01 S-02; registry row final/03; status SPECIFIED -->

**R-CORE-06 (no host-before-durability).** The host MUST NOT be invoked for an effect E before durable issuance is committed: `HostInvoked(E) ⇒ DurableIssued(E)`. An effect MUST NOT be treated as issued merely because an in-memory object exists; durable issuance MUST require a durable `Issued` record. *(L42082–42088; L35150–35156.)*

<!-- FINAL1: R-CORE-06 canonical home; cleaned authority spec/01 S-02; registry row final/03; status SPECIFIED -->

**R-CORE-07 (no raw capability transfer).** Ordinary marshalling of raw capability values MUST be rejected: `OrdinaryMarshal(Value::Capability) ⇒ Rejected`. Authority MUST NOT cross actor boundaries except via explicit delegation. *(L42090–42098; L25972–26001.)*

<!-- FINAL1: R-CORE-07 canonical home; cleaned authority spec/01 S-02; registry row final/03; status SPECIFIED -->

**R-CORE-08 (determinism).** Machine execution MUST satisfy the determinism theorem: `InitialState + SchedulerTrace + HostTrace ⇒ UniqueMachineTrace` (with an accepted planner trace for end-to-end runs). The LLM's stochasticity MUST remain strictly above the machine boundary and MUST NOT influence machine state transitions. [INFORMATIVE: "deterministic" is explicitly defined by this state-transition theorem]. *(L41623–41646; L27518–27547.)*

<!-- FINAL1: R-CORE-08 canonical home; cleaned authority spec/01 S-02; registry row final/03; status SPECIFIED -->

**R-CORE-09 (causal crash recovery).** Crash recovery MUST restore pre-crash state according to `Recover(Snapshot, EventLog, EffectJournal) ≡ PreCrashMachineState` for every crash at a defined persistence boundary, provided every interrupted external effect is (a) durably reconciled, (b) verified idempotent or replayable via recorded receipt, or (c) explicitly classified `Indeterminate` and prevented from silent continuation. The system MUST NOT infer "not executed" from a missing completion record. *(L27551–27569; L35159–35176.)*

<!-- FINAL1: R-CORE-09 canonical home; cleaned authority spec/01 S-02; registry row final/03; status SPECIFIED -->

**R-CORE-10 (no silent recovery corruption).** Invalid persistence state MUST produce an explicit `RecoveryFault`. Persistence corruption MUST NOT be silently repaired by mutation (the recovery engine MUST NOT drop duplicate runnable actors, MUST NOT adjust budget mismatches, MUST NOT ignore sequence gaps, and MUST NOT ignore checksum failures). *(L42100–42105; L35196–35208.)*

<!-- FINAL1: R-CORE-10 canonical home; cleaned authority spec/01 S-02; registry row final/03; status SPECIFIED -->

**R-CORE-11 (I2 predicate signatures, canonical form — frozen addendum).** The central theorem's predicates each have ONE canonical signature; all other frozen signatures are SUPERSEDED (quoted, not deleted). First conjunct: `ValidatedRequest(E)` — request-time validation inside the 16 gates — with the subsumption `ValidatedRequest(E) ⇒ ValidatedPlan(plan(E))`; the `ValidatedPlan` compiler-struct homonym (X-01) is disambiguated by qualification — `ValidatedPlan_pred` vs `ValidatedPlan_struct` — adopted repository-wide. Authorization: `Authorized(holder, c, E, t) ⇔ c ∈ κ_holder ∧ Valid(c, t) ∧ Authorized(κ_holder(c), E, t)` — holder first, possession a conjunct (formalizing R-KERN-04); the authority-first reading `Authorized(A, E, t)` is SUPERSEDED (quoted, not deleted). The 7-conjunct chain (R-CORE-02) is stated once, over these exact signatures; differential adjudication (R-TEST-09) MUST adjudicate against this form — weaker plan-time-only or authority-first readings MUST NOT satisfy the chain. *(Frozen addendum — post-audit remediation SEC-016; additive per R-SCOPE-03; extends R-CORE-02/R-KERN-04; resolves C-80 and, at the normative layer, term/ X-01/X-04/X-05; no source transcription.)*

<!-- FINAL1: R-CORE-11 canonical home; cleaned authority spec/01 S-02; registry row final/03; status SPECIFIED -->

**R-CORE-12 (fault totality and transition atomicity — frozen addendum).** Machine code (evaluator, kernel, budget, persistence, runtime transitions) MUST be panic-free on non-test paths: every fallible operation returns `Result`, and every failure maps to a declared `Fault` — `unwrap`/`expect`/`unreachable!`/`panic!` are FORBIDDEN outside test doubles (the `#![forbid(unsafe_code)]` policy extended with the panic clause). Check/commit drift MUST fault, not panic: a declared internal-consistency fault (`Fault::InternalInvariant` family) MUST exist, observable and differentially comparable. Transition atomicity: a transition either completes (all durable effects appended) or faults with R-EFFECT-04's five assertions — there is no third died-mid-transition outcome inside the trusted boundary. Durable appends MUST precede irreversible in-memory mutations where feasible, or the commit MUST be journal-driven — the mid-transition window is removed, not merely its panic failure mode. Machine crates MUST compile under `clippy::unwrap_used`/`clippy::expect_used` denial (R-REPO-03 structural enforcement). *(Frozen addendum — post-audit remediation SEC-020; additive per R-SCOPE-03; extends R-EFFECT-04/R-BUDGET-02/R-REPO-03; resolves C-83; mutation M034; no source transcription.)*

<!-- FINAL1: R-CORE-12 canonical home; cleaned authority spec/01 S-02; registry row final/03; status SPECIFIED -->

**R-CORE-13 (closed declared fault surface — frozen addendum).** The fault surface on every trust-boundary crossing (host→machine, storage→recovery, planner→machine) MUST be closed and declared: the full fault/error enumeration is frozen, including the six undeclared replay-path variants (`ReplayTraceExhausted`, the `ReplayCorruption` family), `StalePlan`, the unified `MarshalFault` (R-MARSHAL-05), and the `InternalInvariant` family (R-CORE-12); the two-variant `HostFault` declaration is SUPERSEDED (quoted, not deleted). Host faults map onto a closed machine-fault set; `format!("{:?}")` debug text of external errors MUST NOT enter machine values — opaque error codes or digests only (extends R-EFFECT-08 item 4). Resume-vs-fault behavior is pinned per variant: which faults resume continuations, which park actors, the budget effect, and the event-log delta — security-critical semantics, not cosmetics; differential fault comparison (R-REF-05) compares these four, not just labels. *(Frozen addendum — post-audit remediation SEC-012; additive per R-SCOPE-03; extends R-SCOPE-03/R-REF-05/R-EFFECT-08; resolves C-91, closing U-08/U-14 in the security direction; no source transcription.)*

<!-- FINAL1: R-CORE-13 canonical home; cleaned authority spec/01 S-02; registry row final/03; status SPECIFIED -->

**R-CORE-14 (canonical request protocol and transaction boundary — frozen addendum).** The request sequence is exactly the 16-step master-prompt form: (1) evaluate capability; (2) evaluate target; (3) evaluate arguments left-to-right; (4) construct the canonical `Effect` and `EffectDigest`; (5) validate the CapRef; (6) authorize the exact effect; (7) capability ceiling; (8) runtime budget; (9) runtime reservation; (10) deadline; (11) host policy; (12) allocate the `EffectId`; (13) commit issue budget/reservation; (14) durable issuance; (15) actor `Pending`; (16) host invocation. The turn-[21] 16-step form — in which the host emission precedes the durable `Issued` record — is SUPERSEDED (quoted, not deleted): `HostInvoked(E) ⇒ DurableIssued(E)` holds with no ordering exception, and the S-12 presentment of that earlier order is read only as the superseded historical text (C-103). The step-10 deadline premise MUST be the post-advance form `t + δ_t(req) ≤ W`; the pre-advance `t ≤ W` reading is SUPERSEDED (C-104). Steps 12–14b form ONE atomic section: between allocation of the `EffectId` and the second fsync of the `Issued` record no `SnapshotCommit`, no scheduler yield and no observable event MAY occur. Live-failure semantics of that section are R-DUR-07; the recovery boundary (snapshot cadence, `next_effect_id` reconstruction, completion order) is R-RECOV-09. *(Frozen addendum VII — request-pipeline remediation, owner decision 2026-09-03; additive per R-SCOPE-03; extends R-EFFECT-01/03, R-BUDGET-06, R-DUR-02, R-CORE-06/12; resolves C-103/C-104, decisions U-39/U-40; no source transcription.)*

<!-- FINAL1: R-CORE-14 canonical home; cleaned authority spec/01 S-02; registry row final/03; status SPECIFIED -->

**R-ARCH-01 (pipeline).** The normative end-to-end execution path MUST strictly follow the pipeline sequence:

```
LLM/Planner → PlanProposal → staleness validation → Block
→ parse → normalize → validate → lower → capability analysis → resource bounds
→ ExecutablePlan → CEK Machine → Capability Kernel / Budget System
→ Effect Issuance → Durable Boundary → Host
```

*(L37750–37780; L27287–27310.)*

<!-- FINAL1: R-ARCH-01 canonical home; cleaned authority spec/01 S-04; registry row final/03; status SPECIFIED -->

**R-ARCH-02.** The verification architecture MUST maintain an independent and co-equal structure:

```
Production → Observation (normalized) → Reference
```

The production implementation and executable reference model MUST NOT share core transition logic. *(L41406–41424; L37696.)*

<!-- FINAL1: R-ARCH-02 canonical home; cleaned authority spec/01 S-04; registry row final/03; status SPECIFIED -->

**R-ARCH-03 (boundary integrity).** The boundaries among compiler, capability kernel, evaluator, runtime, persistence, host, and reference model MUST remain intact: a raw `Block` MUST NOT have any path into `step()`; `ExecutablePlan` constructors MUST remain private to the compiler; the production runtime MUST only ever receive an `ExecutablePlan`. *(L9086–9097; L39296–39318.)*

<!-- FINAL1: R-ARCH-03 canonical home; cleaned authority spec/01 S-04; registry row final/03; status SPECIFIED -->

**R-ARCH-04.** Architectural dependencies MUST strictly adhere to the linear direction: capability algebra → capability kernel → effect/cost & revocation → executable plan → actor state → global config → scheduler → host executor / replay host. *(L9059–9085.)*

<!-- FINAL1: R-ARCH-04 canonical home; cleaned authority spec/01 S-04; registry row final/03; status SPECIFIED -->

**R-ARCH-05 (isolation posture — frozen addendum).** The isolation ladder (U-05) is RETIRED by decision: the frozen minimum posture is in-process structural isolation (type safety, `#![forbid(unsafe_code)]`, the crate DAG, panic-free machine paths per R-CORE-12), and the residual risk — host compromise is machine compromise: same address space, memory adjacency to `GlobalState`, the kernel arena, and the revocation set — MUST be recorded in the trust model as accepted, not implied away by behavioral containment claims. For any deployment where host code is not fully trusted, the out-of-process host adapter is the REQUIRED mode: effects and receipts cross as canonical bytes only (the wire format already frozen, R-CANON-13). In-process `Box<dyn HostExecutor>` is testkit-only in production configurations (`PanicHost`/`MockKernel` doubles); production `ror-host` MUST NOT link `ror-runtime` internals beyond the adapter trait — a hard dependency/visibility gate. An untrusted agent's isolation level may never be weaker than its spawner's own. *(Frozen addendum — post-audit remediation SEC-013; additive per R-SCOPE-03; extends R-ARCH-03/R-TRUST-01/R-CORE-12; resolves C-93, retiring U-05; no source transcription.)*

*(Frozen addendum VI — owner decision 2026-09-03, resolving `dep/05` V-01; additive per R-SCOPE-03; refines R-ARCH-03/R-REPO-02; no source transcription.)*

**ExecutablePlan crate home and seal (normative refinement).** The `ExecutablePlan` type and its `Sealed` marker MUST be defined in `ror-core`. Construction MUST remain compiler-only (R-ARCH-03 unchanged): `finalize` requires a `PlanSeal` token whose sole constructor is `pub` in `ror-core` and denied by the workspace clippy `disallowed-methods` configuration in every crate except `ror-compiler` (R-REPO-03 structural enforcement — the same mechanism class as R-CORE-12's `unwrap`/`expect` denial; Track-B). The source's `pub(crate) fn finalize` phrasing (L39947-39950 §16) is per-crate visibility and cannot express this cross-crate privacy; that reading is SUPERSEDED (quoted, not deleted — `dep/05` V-01). No new crate edge results: `ror-runtime` already depends on `ror-core` (`spec/07` §6), which is why the type home moves rather than the edge.

<!-- FINAL1: R-ARCH-05 canonical home; cleaned authority spec/01 S-04; registry row final/03; status SPECIFIED -->

**R-REPO-01 (workspace layout, frozen boundaries).** The workspace MUST separate untrusted language data → compiler → trusted executable representation → machine → authority/resources → durable effects → host, and MUST independently maintain production ↔ observations ↔ reference. Top-level names MAY change for organizational reasons; dependency and trust boundaries MUST NOT change. The layout MUST follow (frozen intent): `crates/{ror-core, ror-compiler, ror-kernel, ror-runtime, ror-persistence, ror-host, ror-agent, ror-reference, ror-differential, ror-testkit}`. *(L39140–39195; L41406–41424.)*

<!-- FINAL1: R-REPO-01 canonical home; cleaned authority spec/01 S-22; registry row final/03; status SPECIFIED -->

**R-REPO-02 (crate contracts, normative).** Crate contracts MUST strictly conform to responsibilities:
- `ror-core`: lowest-level semantic domain (Symbol, ActorId, CapRef, EffectId, EventSequence, LogicalTime, Expr, Value, FunctionValue, Environment, Constraint, Effect, EffectCost, Budget, Consumable, Reserved, Fault, MachineEvent). Depends on std only. MUST NOT contain host calls, filesystem, networking, scheduler, persistence, capability authority storage, or LLM integration.
- `ror-compiler`: Block → parse → NormalizedAST → ValidatedPlan → PlanIR → capability analysis → resource analysis → ExecutablePlan. `ExecutablePlan` constructors private.
- `ror-kernel`: CapabilityKernel, AuthorityNode, derivation, revocation, authorization, budget primitives, logical-time validation. `AuthorityNode` invisible to evaluator/runtime.
- `ror-runtime`: CEK machine, actors, scheduler, effects.
- `ror-persistence`: WAL, snapshots, effect journal, recovery.
- `ror-host`: host execution and replay boundaries.
- `ror-agent`: planner/observation/supervisor integration.
- `ror-reference`: independent executable semantic model.
- `ror-differential`: generator, runner, comparator, shrinking.
- `ror-testkit`: test infrastructure and controlled doubles.
*(L39196–40762 (responsibility detail); L41806–41846 (summary table).)*

*(Non-normative note, added by the terminology pass — the normative bullet above is unchanged.)*
*The `ror-compiler` pipeline in R-REPO-02 reproduces the turn-[58] diagram (L39265–39280) faithfully, and it is reproduced here unchanged. It is **one of three** stage sequences in the frozen source, and the frozen struct declarations contradict its ordering: `NormalizedAST` is the **content** of `ParsedBlock` (L864), not a stage before `ValidatedPlan`, and `PlanIR` is the **content** of `ValidatedPlan` (L865), not a stage after it. Two declared stages — `ParsedBlock` (L864) and `CapabilityCheckedPlan` (L866) — do not appear in it at all, and `NormalizedAST` and `PlanIR` are never declared anywhere (L1–42312). An implementer MUST NOT treat this rendering as the stage list. Filed as `term/02-collisions.md` X-02, X-41, X-29, X-30 and `spec/06` C-52; `mod/02-compiler.md` carries the same note. Nothing here is renamed or reordered, because the collision is in the frozen source and resolving it by editing either side would be a silent semantic change (R-SCOPE-03).*

*(Frozen addendum VI — owner decision 2026-09-03, resolving `dep/05` V-09; additive per R-SCOPE-03; refines R-REPO-02/R-BUDGET-01…09; no source transcription.)*

**Budget crate home made explicit (normative refinement).** The R-REPO-02 `ror-kernel` bullet's "budget primitives" MUST be read as: the kernel CONSUMES the budget operand types defined in `ror-core`; no budget algebra, operand type or per-transition gate lives in `ror-kernel`. The shared ceiling/operand types MUST live in `ror-core` (`ror-core → ror-kernel` is forbidden by §14's frozen list, upheld by R-TRUST-05); per-transition gate CALLS live in `ror-runtime` (`spec/07` §2 already splits the R-BUDGET obligations across `ror-core` and the runtime gates). MOD-04 BUDGET keeps one module with an explicit two-crate home — algebra + operand types in `ror-core`, gate calls in `ror-runtime` (`mod/04` DEPENDENCIES states it).

<!-- FINAL1: R-REPO-02 canonical home; cleaned authority spec/01 S-22; registry row final/03; status SPECIFIED -->

**R-REPO-03 (boundary enforcement).** The repository MUST make boundaries hard to violate accidentally, enforced by Cargo dependencies, Rust visibility, type construction, trait boundaries, module structure, tests, mutation testing, and CI. Production crates MUST NOT depend on reference crates. *(L41223–41273.)*

<!-- FINAL1: R-REPO-03 canonical home; cleaned authority spec/01 S-22; registry row final/03; status SPECIFIED -->


---

## §03 Trust Model

The trust table, TCB composition, the no-hidden-authority rule, and the frozen addenda fixing trust-table completeness (R-TRUST-04) and the structural carriability of the durability hinge (R-TRUST-05). The isolation-posture decision (R-ARCH-05, §02) belongs to this boundary; residual accepted risk is recorded there, not softened.

**Canonical homes transcribed in this section (5):** `R-TRUST-01`, `R-TRUST-02`, `R-TRUST-03`, `R-TRUST-04`, `R-TRUST-05`.

**R-TRUST-01.** The system MUST adhere to the following normative trust assignments:

| Component | Trust | Role |
|---|---|---|
| LLM / planner | **No** | Proposal generation |
| `Block` (language data) | **No** | Untrusted program data |
| Compiler | Yes | Establishes executable invariants |
| Capability kernel | Yes | Authority decisions |
| CEK machine | Yes | Deterministic execution |
| Scheduler | Yes | Deterministic interleaving |
| Budget system | Yes | Resource conservation |
| Persistence / effect journal | Yes | Durable machine state, causal effect state |
| ReplayHost | Yes | Recorded-effect reconstruction |
| Live host | **Partial** | External-world execution (capability + policy constrained) |
| Supervisor | Yes | Lifecycle and recovery |

[INFORMATIVE: "deterministic" is explicitly defined in S-02 / R-CORE-08 and S-15 / R-ACTOR-07]. *(L41823–41841; L27611–27624.)*

<!-- FINAL1: R-TRUST-01 canonical home; cleaned authority spec/01 S-03; registry row final/03; status SPECIFIED -->

**R-TRUST-02.** LLM output MUST NOT be included in TCB authority (`LLM output ∉ TCB authority`). The TCB MUST consist strictly of: CEK machine, capability kernel, budget algebra, deterministic scheduler, canonical serializer, WAL/recovery state machine, and effect boundary. [INFORMATIVE: "deterministic" is explicitly defined in S-15 / R-ACTOR-07]. *(L28178–28230.)*

<!-- FINAL1: R-TRUST-02 canonical home; cleaned authority spec/01 S-03; registry row final/03; status SPECIFIED -->

**R-TRUST-03 (no hidden authority).** The LLM, AST, evaluator, scheduler, host adapter, or ordinary `Value` representation MUST never manufacture authority. Capabilities MUST be treated as opaque handles; only the capability kernel MUST decide authority. The evaluator MAY call `derive(capability, constraint, logical_time)` and `authorize(capability, effect, logical_time)`; it MUST NOT inspect authority internals. *(L37722–37748; L19153–19175.)*

<!-- FINAL1: R-TRUST-03 canonical home; cleaned authority spec/01 S-03; registry row final/03; status SPECIFIED -->

**R-TRUST-04 (one complete trust table; the planner is never a provider — frozen addendum).** The trust table exists exactly once and MUST be complete over every module that enforces a security boundary: rows for MOD-06 (marshalling and delegation boundary), MOD-08 (the effect gate sequence), and MOD-10 (the canonical codec) are frozen here as authoritative machine boundary (trust: Yes); the 11-row earlier table is SUPERSEDED (quoted, not deleted). The planner module (MOD-13 / `ror-agent`) MUST NOT appear as the provider of any `SECURITY_DEPENDENCY` or `RUNTIME_DEPENDENCY` edge: its records are prohibitions — negative contracts homed at their enforcing modules (MOD-03/06/08); security obligations MUST NOT be discharged inside any LLM-facing crate. Verification: `dep/` regenerated with SC-1/2/3 promoted from advisory rows to hard failures. *(Frozen addendum — post-audit remediation SEC-022 (V-03/V-11); additive per R-SCOPE-03; extends R-TRUST-01/R-SCOPE-04; resolves C-84; no source transcription.)*

<!-- FINAL1: R-TRUST-04 canonical home; cleaned authority spec/01 S-03; registry row final/03; status SPECIFIED -->

**R-TRUST-05 (structural carriability of the durability hinge — frozen addendum).** The frozen crate DAG MUST carry the R-DUR-02 hinge edge `ror-runtime → ror-persistence` (the step-14 durable append that `HostInvoked ⇒ DurableIssued` hangs on) — decided here in the direct direction; the inverted-trait alternative is SUPERSEDED (quoted, not deleted). The `ror-core → ror-kernel` implication is resolved per the frozen edge list's intent (forbidden; V-10b): authority storage stays kernel-side. The forbidden-edge list MUST be checked mechanically against the actual `Cargo.toml` DAG, and the crate-separation rule — no LLM-facing code in a crate holding runtime/compiler/persistence handles — is part of R-REPO-03's structural review. A build in which the durability call is structurally orphaned (a local journal shim) is a conformance failure. *(Frozen addendum — post-audit remediation SEC-022 (V-10) + the SEC-015 crate rule; additive per R-SCOPE-03; extends R-REPO-02/R-REPO-03/R-DUR-02; resolves C-85; no source transcription.)*

<!-- FINAL1: R-TRUST-05 canonical home; cleaned authority spec/01 S-03; registry row final/03; status SPECIFIED -->


---

## §04 Semantic Domain

The semantic domain proper: machine value domain, frozen expression AST, symbol identity, the effect descriptor and cost, the frozen fault taxonomy, effect recovery properties, and the Σ/G configuration structures. Every production type defined here has exactly one canonical definition, cited as the single home (see `final/02` §4, Type Definition Homes). Reference-model value domains (`RefValue`, `RefCapId`, `RefActorId`, RefEffectId`) are *distinct* abstractions — see §17; they are never collapsible with the production types defined here (N-27 discipline).

**Canonical homes transcribed in this section (8):** `R-CALC-01`, `R-CALC-02`, `R-CALC-03`, `R-CALC-04`, `R-CALC-05`, `R-CALC-06`, `R-CALC-07`, `R-CALC-08`.

**R-CALC-01 (value domain, machine).** The machine value domain MUST strictly consist of: `v ::= Unit | Bool(bool) | Integer(i64) | Bytes(Vec<u8>) | Symbol(Symbol) | String(String) | List(Vec<Value>) | Tuple(Vec<Value>) | Function(FunctionValue) | Capability(CapRef) | DelegatedCapability(DelegatedCapability)`. Raw capabilities MAY only be constructed by the capability kernel and MUST NOT be constructed by untrusted code. Delegated capabilities MAY only be constructed by the marshaller.

*(L12290–12312 (turn [21]); L19153–19175.)*

<!-- FINAL1: R-CALC-01 canonical home; cleaned authority spec/01 S-07; registry row final/03; status SPECIFIED -->

**R-CALC-02 (expression domain, frozen surface).** The frozen `Expr` AST MUST consist strictly of declarative constructors: `Value(Value) | Var(Symbol) | Let { name, value, body } | Seq { first, second } | If { condition, then_branch, else_body } | Lambda { params, body } | Call { func, args } | Attenuate { cap, constraint } | Request { capability, operation, target, params } | Spawn { expr, initial_budget, capabilities } | Send { target, message } | Receive | Yield | Halt`. Expressions MUST NOT embed host callbacks.

*(L12132–12170 (turn [21]).)*

<!-- FINAL1: R-CALC-02 canonical home; cleaned authority spec/01 S-07; registry row final/03; status SPECIFIED -->

**R-CALC-03 (symbols).** Runtime variable identity MUST be `Symbol(u32)` and MUST NOT use `String`. The compiler MUST maintain the name→Symbol mapping; the evaluator MUST operate entirely on symbols. *(L12250–12270.)*

<!-- FINAL1: R-CALC-03 canonical home; cleaned authority spec/01 S-07; registry row final/03; status SPECIFIED -->

**R-CALC-04 (effect descriptor).** An effect MUST be immutable data: `Effect { capability: CapRef, operation: Op, target: Target, params: Params, cost: EffectCost }`. Effect identity MUST be canonical according to `EffectDigest = SHA-256(canonical_bytes(effect))`. *(L9288–9348 (early form, capability carried in `EffectRequest.cap`, superseded); L23726–23772 (frozen form).)*

<!-- FINAL1: R-CALC-04 canonical home; cleaned authority spec/01 S-07; registry row final/03; status SPECIFIED -->

**R-CALC-05 (effect cost, frozen form).** Effect cost MUST be structured as `EffectCost { issue: Consumable, complete_max: Consumable, reserve: Reserved }`. `issue` MUST be charged at request time; `complete_max` MUST be escrowed at issuance so completion accounting MUST NOT fail; `reserve` MUST hold capacity until completion. *(L25799–25825 (Phase 12 correction); L23726–23772 (pre-correction form, superseded).)*

<!-- FINAL1: R-CALC-05 canonical home; cleaned authority spec/01 S-07; registry row final/03; status SPECIFIED -->

**R-CALC-06 (fault taxonomy).** The fault taxonomy MUST strictly correspond to the frozen Rust `Fault` enum: `Capability(CapabilityError) | BudgetExhausted | DeadlineExceeded | HostPolicyDenied(HostPolicyError) | EffectCanonicalization(EffectError) | Host(HostFault) | ReplayCorruption | InvalidReceipt` (plus `StalePlan` at the planner boundary). The frozen fault taxonomy is the Rust `Fault` enum. *(L23784–23819; L27236. See C-08 for naming inconsistencies in earlier drafts.)* **Non-normative annotation (X-64, X-67, X-68, X-69, C-54, C-57, C-58; the normative sentence above is unchanged and governs):** the parenthetical is **source-supported** — L28373 (turn [36]) states that a stale proposal “is rejected with `Fault::StalePlan`”, and L27236 (turn [33]) gives `StalePlan` as a bare token. It is nevertheless not a variant of the declaration this obligation cites: none of the seven `pub enum Fault` declarations (L10882, L17788, L18125, L22415, L23319, L23806, L26865) contains `StalePlan`, and L23807 carries an explicit `// ... (previous faults)` elision, so the eight enumerated variants do not close the set. `StalePlan` is one of **twelve** `Fault::` paths the source uses but never declares (X-69). The payload type `HostFault` in `Host(HostFault)` is declared once with two variants while eight undeclared `HostFault::` paths are used, six on the frozen replay path (C-57, **blocking**); and `HostFault` and `Revoked` additionally denote *members of the v1 fault grammar* `F` at L1949 — a different level of the taxonomy than the flat variant list stated here (C-58). **An earlier revision of this annotation asserted that `Fault::StalePlan` “occurs nowhere in L1–42312”; that claim was false and is withdrawn here rather than silently overwritten (R-SCOPE-03).** Which variants the taxonomy finally contains is U-08's decision.

<!-- FINAL1: R-CALC-06 canonical home; cleaned authority spec/01 S-07; registry row final/03; status SPECIFIED -->

**R-CALC-07 (effect properties).** Effect semantics MUST maintain replayability, reversibility, and idempotence properties; an effect's *machine result* MAY be replayed even when the real-world operation cannot. [INFORMATIVE: the per-operation classification table in the source is non-normative]. *(L2141–2156 (v1) / L3858–3873 (v2) (declared domain + illustrative table); L26669–26735 (Phase 14 effect classes).)*

<!-- FINAL1: R-CALC-07 canonical home; cleaned authority spec/01 S-07; registry row final/03; status SPECIFIED -->

**R-CALC-08 (configuration).** Local machine configuration MUST be structured as `Σ = ⟨e, ρ, κ, B, t, H, L⟩` (current term, local environment, capability kernel, budget, logical time, isolated heap, append-only event log); global configuration MUST be structured as `G = ⟨A, t, L, R, E_journal⟩`. *(L7119–7144; L8653–8682; L24148–24163.)*

<!-- FINAL1: R-CALC-08 canonical home; cleaned authority spec/01 S-07; registry row final/03; status SPECIFIED -->


---

## §05 Compilation Pipeline

The compilation boundary from untrusted `Block` data to trusted `ExecutablePlan`: pipeline, static judgment, plan temporal integrity, constructor privacy, and the frozen capability-literal rule (R-COMPILE-06). The effect-set-inference gap is carried forward verbatim as a non-normative gap note (U-22) — it is a recorded absence, not a resolved item.

**Canonical homes transcribed in this section (6):** `R-COMPILE-01`, `R-COMPILE-02`, `R-COMPILE-03`, `R-COMPILE-04`, `R-COMPILE-05`, `R-COMPILE-06`.

**R-COMPILE-01.** The compiler MUST enforce `Block ≠ ExecutablePlan`. Only validated executable plans MUST enter the trusted machine; no `Block` MUST bypass compilation. *(L41440–41452; L3834–3838.)*

<!-- FINAL1: R-COMPILE-01 canonical home; cleaned authority spec/01 S-06; registry row final/03; status SPECIFIED -->

**R-COMPILE-02 (pipeline).** Compilation MUST pass the stages: parse → normalize → validate → lower → capability analysis → resource analysis. Any failed stage MUST yield `fault(F_compilation)`; no raw `Block` MUST reach execution. *(L1930–1960 (J1–J4 and compilation theorem, superseded form); L39253–39267 (frozen pipeline).)*

<!-- FINAL1: R-COMPILE-02 canonical home; cleaned authority spec/01 S-06; registry row final/03; status SPECIFIED -->

**R-COMPILE-03 (static checks, frozen intent).** The static compilation judgment `Γ; κ_static ⊢ e : τ ! F @ B` MUST thread type, possible-effect set `F` (conservative over-approximation; pure terms MUST yield `F = ∅`), capability requirements, and static budget upper bound `B`. If a term's worst-case cost exceeds `B_max`, compilation MUST fail. *(L3874–3905 (v2 form); L1953–1980 (v1 J1–J4, superseded form).)*

<!-- FINAL1: R-COMPILE-03 canonical home; cleaned authority spec/01 S-06; registry row final/03; status SPECIFIED -->

**R-COMPILE-04 (plan immutability / temporal integrity).** An `ExecutablePlan` MUST be immutable; a new plan MAY only be produced by another validated compilation transition (plan₁ → execution/observation → planner → Block₂ → compiler → plan₂). A plan authorized at `t₀` MUST NOT silently acquire new authority at `t₁`. *(L1722–1745; L2052–2070 (v1 Theorem 6).)*

<!-- FINAL1: R-COMPILE-04 canonical home; cleaned authority spec/01 S-06; registry row final/03; status SPECIFIED -->

**R-COMPILE-05.** `ExecutablePlan` constructors MUST remain private to the compiler crate.  [INFORMATIVE (gap): The detailed effect-set inference (v1 judgment J2, `Γ ⊢ e ↝ Φ`) is not re-specified]. *(L39296–39318.)*

<!-- FINAL1: R-COMPILE-05 canonical home; cleaned authority spec/01 S-06; registry row final/03; status SPECIFIED -->

**R-COMPILE-06 (capability literals must be plan-bound — frozen addendum).** A `Block` MUST NOT carry a `Value::Capability` literal that is not plan-bound: compilation MUST fault on any embedded capability literal — foreign, garbage-generation, or own-but-undeclared — unless the compiler itself substituted it from the plan's declared capability set. Undecided capability-analysis depth (U-22) MUST NOT leave embedded authority literals unconstrained; this closes the U-22 gap in the security direction. *(Frozen addendum — post-audit remediation SEC-002 item 3; additive per R-SCOPE-03; extends R-COMPILE-02/R-COMPILE-03; no source transcription.)*

**Non-normative (gap).** The detailed effect-set inference (v1 judgment J2, `Γ ⊢ e ↝ Φ`) is not re-specified in the frozen pipeline stages; see `U-22` in `09-unresolved-decisions.md`.

---

<!-- FINAL1: R-COMPILE-06 canonical home; cleaned authority spec/01 S-06; registry row final/03; status SPECIFIED -->


---

## §06 Capability Model

The capability algebra (semantic domains, partial order, derivation, authorization predicate, revocation/lineage, the three frozen theorems, logical time, admissibility, lifetime retyping) and the capability kernel (opaque generation-safe `CapRef`, authority storage, substrate privacy, the possession gate, the `CapabilityContext` possession type, and the root-grant protocol). Theorem status stays `SPECIFIED` with source proof sketches; no mechanized proof exists and none is claimed (R-CAP-08 explicitly records this).

**Canonical homes transcribed in this section (17):** `R-CAP-01`, `R-CAP-02`, `R-CAP-03`, `R-CAP-04`, `R-CAP-05`, `R-CAP-06`, `R-CAP-07`, `R-CAP-08`, `R-CAP-09`, `R-CAP-10`, `R-CAP-11`, `R-KERN-01`, `R-KERN-02`, `R-KERN-03`, `R-KERN-04`, `R-KERN-05`, `R-KERN-06`.

**R-CAP-01 (semantic domains, v0.2).** Authority MUST be defined as `A = {(o, ⟨S,Q,R,T⟩)}` mapping operation `o` to scope `S`, param predicate `Q`, resource limit `R`, and lifetime `T`. `CapRef` MUST be an opaque handle. Capability resolution MUST map `κ(c) → Authority`.

*(L6354–6379.)*

<!-- FINAL1: R-CAP-01 canonical home; cleaned authority spec/01 S-09; registry row final/03; status SPECIFIED -->

**R-CAP-02 (operation-indexed authority).** Authority is indexed by operation to prevent cross-operation contamination: `A = { (o, A_o) | o ∈ O_granted }` with `A_o = ⟨S, Q, R, T⟩`.

<!-- FINAL1: R-CAP-02 canonical home; cleaned authority spec/01 S-09; registry row final/03; status SPECIFIED -->

**R-CAP-03 (partial order).** `A₁ ≼ A₂` iff `O₁ ⊆ O₂` and for all `o ∈ O₁`: `S₁ ≼_S S₂ ∧ Q₁ ≼_Q Q₂ ∧ R₁ ≤ R₂ ∧ T₁ ⊆ T₂`.

<!-- FINAL1: R-CAP-03 canonical home; cleaned authority spec/01 S-09; registry row final/03; status SPECIFIED -->

**R-CAP-04 (constraint vs authority).** A `Constraint` is a *request to narrow* an existing grant, conceptually distinct from `Authority`.

<!-- FINAL1: R-CAP-04 canonical home; cleaned authority spec/01 S-09; registry row final/03; status SPECIFIED -->

**R-CAP-05 (derivation).** `derive(A, C) = { (o, derive_op(A_o, C_o)) | o ∈ O_A ∩ O_C }` where `derive_op(⟨S,Q,R,T⟩, ⟨S_c,Q_c,R_c,T_c⟩) = ⟨S ⊓ S_c, Q ⊓ Q_c, R ⊓ R_c, T ⊓ T_c⟩`. **Invariant:** `derive(A,C) ≼ A` holds by definition of meet.

<!-- FINAL1: R-CAP-05 canonical home; cleaned authority spec/01 S-09; registry row final/03; status SPECIFIED -->

**R-CAP-06 (canonical authorization predicate).** For effect `E = ⟨op, target, params, cost⟩` at logical time `t`: `Authorized(A, E, t) ⇔ op ∈ O_A ∧ target ∈ ⟦A_op.S⟧ ∧ A_op.Q(params) ∧ cost ≤ A_op.R ∧ t ∈ A_op.T`. The `cost` here is the effect's static resource requirement checked against the capability ceiling `R_A`; the dynamic execution budget is checked separately (dual gate). *(L6406–6421; L6647–6656.)*

<!-- FINAL1: R-CAP-06 canonical home; cleaned authority spec/01 S-09; registry row final/03; status SPECIFIED -->

**R-CAP-07 (revocation / lineage).** `Valid(c, t) ⇔ Live(c) ∧ t ∈ Lifetime(c) ∧ ∀a ∈ Ancestors(c). Live(a)`. Revoking a parent sets `Live(parent) = false`; descendants are invalidated lazily by walking the ancestor chain during the `Valid` check (O(d), d = lineage depth). **No authority amplification** and **ancestor revocation** are frozen obligations (tags `CAP-DERIVE-NO-AMPLIFICATION`, `CAP-REVOCATION-ANCESTOR`).

<!-- FINAL1: R-CAP-07 canonical home; cleaned authority spec/01 S-09; registry row final/03; status SPECIFIED -->

**R-CAP-08 (algebra theorems, frozen statements).** - Theorem 1 (Attenuation soundness): `derive(A,C) ≼ A`. - Theorem 2 (Authority monotonicity): `A' ≼ A ∧ Authorized(A',E,t) ⇒ Authorized(A,E,t)`. - Theorem 3 (Attenuation corollary): assuming `Authorized(A,E,t)`, `Authorized(derive(A,C),E,t) ⇔ Satisfies(C,E,t)`. These are `SPECIFIED` statements with proof sketches in the source; no mechanized proof exists in the repository (`PROVEN` is NOT claimed). *(L6422–6433; L6657–6671.)*

<!-- FINAL1: R-CAP-08 canonical home; cleaned authority spec/01 S-09; registry row final/03; status SPECIFIED -->

**R-CAP-09 (time).** Logical time `t` MUST NOT be fetched from the host OS; time `t` MUST be an explicit component of machine state (logical clock / deterministic timestamp) to ensure replay determinism. Wall-clock time MUST NOT be used as semantic machine state. [INFORMATIVE: "deterministic" is explicitly defined in S-02 / R-CORE-08]. *(L6434–6436; L38858–38890.)*

<!-- FINAL1: R-CAP-09 canonical home; cleaned authority spec/01 S-09; registry row final/03; status SPECIFIED -->

**R-CAP-10 (`AdmissibleConstraint` defined — frozen addendum).** `AdmissibleConstraint` is DEFINED: decidable well-formedness per semantic domain — operation set `O` nonempty and within the parent's interpretation, scope constraint `S` interpretable, predicate `Q` closed over params, resource ceiling `R` within the parent's, lifetime `T` a satisfiable interval. The derivation law is total on admissible inputs only: `¬AdmissibleConstraint(C) ⇒ ¬∃c'. derive(A,C) = c'` — `derive(A, C)` MUST fault (`Fault::InvalidConstraint`, in the R-CORE-13 closed enumeration; the `Invalid`-variant drift C-56 is resolved there), never identity: the ⊤-default reading (inadmissible constraint silently ignored, `derive(A, C_garbage) = A`) is FORBIDDEN. Constraints are attacker-authored (authored inside untrusted `Block`s: `Attenuate`, spawn manifests per R-ACTOR-09, `Delegate` per R-MARSHAL-05): the compiler MUST validate constraint admissibility at compile time (extends R-COMPILE-02/03) before any kernel call. Property: `derive` with an inadmissible constraint never returns a CapRef, across the full generated constraint space. *(Frozen addendum — post-audit remediation SEC-014; additive per R-SCOPE-03; extends R-CAP-04/R-CAP-05/R-COMPILE-06; resolves C-94, closing AMB-12/U-09's admissibility clause; mutation M030; no source transcription.)*

<!-- FINAL1: R-CAP-10 canonical home; cleaned authority spec/01 S-09; registry row final/03; status SPECIFIED -->

**R-CAP-11 (`Lifetime` is logical time — frozen addendum).** `Lifetime`'s bounds are `LogicalTime`, not wall-clock: `Lifetime { start: LogicalTime, end: LogicalTime }` with a half-open validity interval `[start, end)` — `contains(t) ⇔ start ≤ t ∧ t < end` — and every call site passes the machine's logical time (the three `contains` declarations and both authorization paths, incl. the second call site at the `op_auth.lifetime.contains(logical_time)` path — the full evidence table is in `audit/u36-u37-proposals.md` §U-36 and `term/02-collisions.md` X-42). The five `// Unix timestamp` annotations and the `"e.g., Unix timestamps"` prose are SUPERSEDED (quoted, not deleted, per R-SCOPE-03); lifetime validity is machine-state only and never a wall-clock reading (R-CAP-09, R-CLAIM-02, term/ X-42). `ResourceLimits.max_duration` is DECLARED-duration information only: it describes the ceiling an author/planner may declare for an effect's predicted duration, never a machine debit and never an authorization gate — the machine's duration authority is the per-actor `D` budget under R-BUDGET-15. `Deadline` remains `Option<LogicalTime>` (`Deadline(None)` = ∞) in all three declarations — no retype. *(Frozen addendum IX — duration-semantics audit, owner decision 2026-09-03; additive per R-SCOPE-03; extends R-CAP-06/R-CAP-09/R-CLAIM-02, term/ X-42; resolves C-100, decision U-36; no source transcription.)*

<!-- FINAL1: R-CAP-11 canonical home; cleaned authority spec/01 S-09; registry row final/03; status SPECIFIED -->

**R-KERN-01 (opaque references).** `CapRef { index: u32, generation: u32 }` MUST be opaque and generation-safe; fields MUST be private; public constructors from arbitrary integers MUST NOT exist; `CapRef`s MUST be constructed strictly by the capability kernel. [INFORMATIVE: generation safety is defined by generation-number mismatch checks preventing dangling reference reuse]. *(L9127–9133; L10178–10208.)*

<!-- FINAL1: R-KERN-01 canonical home; cleaned authority spec/01 S-10; registry row final/03; status SPECIFIED -->

**R-KERN-02 (API contract).** `CapabilityKernel` MUST own authority storage: `arena: GenerationalArena<AuthorityNode>`, `revocation_set: HashSet<CapRef>`. `derive()` and `revoke()` MUST be kernel operations.

*(L6672–6728; L19153–19175; L37870–37886.)*

<!-- FINAL1: R-KERN-02 canonical home; cleaned authority spec/01 S-10; registry row final/03; status SPECIFIED -->

**R-KERN-03 (substrate privacy).** `AuthorityNode` and all authority internals MUST remain `pub(crate)`/inaccessible to evaluator and runtime consumers. No hidden authority inspection.

<!-- FINAL1: R-KERN-03 canonical home; cleaned authority spec/01 S-10; registry row final/03; status SPECIFIED -->

**R-KERN-04 (holder-possession binding at the gate — frozen addendum).** Authority exercise at the machine's authorization gate MUST be possession-gated: `Authorized_gated(actor, c, E, t) ⇔ c ∈ CapabilityContext(actor) ∧ Valid(c, t) ∧ Authorized(κ(c), E, t)` — possession is a conjunct of the gated authorization predicate, not a marshalling courtesy. The kernel `authorize` API MUST be holder-parameterized (`authorize(holder, cap, effect, t)`) and MUST resolve the `CapRef` through the requesting actor's capability context; the global-arena no-holder form (`authorize(cap, effect, t)`) is SUPERSEDED (quoted, not deleted). `CapRef` bits MUST NOT suffice to exercise authority — `CapRef ≠ authority ownership` is a kernel-side possession rule. This binds the per-actor reading of the v0.3 formal rules (`Authorized(κ(c), E, t)`) over the kernel-substrate global arena (conflict C-77, resolved by this addendum). *(Frozen addendum — post-audit remediation SEC-002 items 1 and 4; additive per R-SCOPE-03; extends R-CAP-06/R-KERN-02; no source transcription.)*

<!-- FINAL1: R-KERN-04 canonical home; cleaned authority spec/01 S-10; registry row final/03; status SPECIFIED -->

**R-KERN-05 (CapabilityContext is a real possession type — frozen addendum).** `CapabilityContext` MUST be a real frozen type: the per-actor possession structure mapping the actor's capability slots to live `CapRef`s. The unit-type sketch (`pub type CapabilityContext = ();`) is SUPERSEDED (quoted, not deleted). Snapshots MUST carry the capability context, and recovery MUST reconstruct each actor's possession set before any gate authorization — a possession gate that does not survive recovery enforces nothing. *(Frozen addendum — post-audit remediation SEC-002 item 2; additive per R-SCOPE-03; extends R-KERN-02/R-KERN-04; no source transcription.)*

<!-- FINAL1: R-KERN-05 canonical home; cleaned authority spec/01 S-10; registry row final/03; status SPECIFIED -->

**R-KERN-06 (root-grant protocol — frozen addendum).** Authority enters the machine ONLY through the frozen grant protocol: `Grant(source, authority, ceiling, t)` MUST produce a durable `CapabilityGranted` record (the R-PERSIST-07 event kind) and the authority MUST stay `≼` the deployment ceiling; root authority is minted exactly once, at machine initialization, by the deployment — no runtime minting path exists. `Supervisor.host` is REMOVED from the `Supervisor` struct, or typed as an issued-effect-only handle: R-HOST-02 (host performs only issued effects) binds EVERY host caller, not only the machine — `HostInvoked ⇒ DurableIssued` with no exception for supervisor or integration code. Planner-facing I/O MUST be structurally separated from supervisor/runtime/compiler handles (the `ror-planner-io` split: the untrusted side emits `PlanProposal` data only, no compiler/runtime edges) — no crate containing LLM/planner I/O may depend on `ror-compiler` or `ror-runtime`. Audit test: every live root authority in a recovered arena traces to a durable `CapabilityGranted` record. *(Frozen addendum — post-audit remediation SEC-015; additive per R-SCOPE-03; extends R-KERN-01/R-HOST-02/R-PLANNER-02/R-TRUST-05; resolves C-95; no source transcription.)*

<!-- FINAL1: R-KERN-06 canonical home; cleaned authority spec/01 S-10; registry row final/03; status SPECIFIED -->


---

## §07 Budget Model

The budget model: structure, checked arithmetic, reservation predicates, the dual gate, conservation, time advancement, the cost model, the fault rule, and the frozen addenda (escrow-disposition totality R-BUDGET-09, resource-state atomicity R-BUDGET-10, disposition normal form R-BUDGET-11, persistent capacity R-BUDGET-13, duration semantics R-BUDGET-15, the exhaustive δ_t table R-BUDGET-16). `R-BUDGET-12` was never frozen (its rule is folded into R-BUDGET-15/16) and `R-BUDGET-14` remains deferred — the ID gaps are deliberate and MUST NOT be re-used (§10 report).

**Canonical homes transcribed in this section (14):** `R-BUDGET-01`, `R-BUDGET-02`, `R-BUDGET-03`, `R-BUDGET-04`, `R-BUDGET-05`, `R-BUDGET-06`, `R-BUDGET-07`, `R-BUDGET-08`, `R-BUDGET-09`, `R-BUDGET-10`, `R-BUDGET-11`, `R-BUDGET-13`, `R-BUDGET-15`, `R-BUDGET-16`.

**R-BUDGET-01 (structure).** Budget `B = ⟨C, R, W⟩` where `C = ⟨F, I, D⟩` (consumables: fuel, I/O, duration), `R = ⟨M, S⟩` (reserved: memory bytes, concurrency slots), `W ∈ ℕ ∪ {∞}` (absolute logical-time deadline; `Deadline(None)` = infinity). Consumables are strictly decreasing and never returned; reserved capacities are held for a scope then released; the deadline is checked against logical time, not wall-clock.

<!-- FINAL1: R-BUDGET-01 canonical home; cleaned authority spec/01 S-11; registry row final/03; status SPECIFIED -->

**R-BUDGET-02 (checked arithmetic).** Budget operations MUST use checked arithmetic and expose failure (`BudgetError { ConsumableExhausted, ReservedCapacityExceeded, ReservedCapacityUnderflow, DeadlineExceeded }`). `saturating_sub` MUST NOT be used for semantic accounting.

<!-- FINAL1: R-BUDGET-02 canonical home; cleaned authority spec/01 S-11; registry row final/03; status SPECIFIED -->

**R-BUDGET-03 (reservation predicates).** `ReserveOK(r, R, R_max) ⇔ R + r ≤ R_max`; `ReleaseOK(r, R) ⇔ r ≤ R`; updates `R' = R + r` / `R' = R − r`. (Supersedes the earlier single `BudgetOK` that mixed directions — see `C-07`. )

<!-- FINAL1: R-BUDGET-03 canonical home; cleaned authority spec/01 S-11; registry row final/03; status SPECIFIED -->

**R-BUDGET-04 (dual-gate within-budget).** `WithinBudget(E, C, R, R_A) ⇔ cost_C(E) ≤ C ∧ ReserveOK(cost_R(E), R, R_max) ∧ cost(E) ≤ R_A` (effect cost within both runtime budget and capability ceiling).

<!-- FINAL1: R-BUDGET-04 canonical home; cleaned authority spec/01 S-11; registry row final/03; status SPECIFIED -->

**R-BUDGET-05 (conservation).** Effect issuance MUST escrow `complete_max` from consumable budget `C`. Effect completion MUST refund `complete_max - complete_actual` to `C_available`. Escrow conservation MUST hold invariant: `C_available + C_escrowed + C_consumed = C_initial`.

*(L7408–7425; L28203–28240 (frozen partition); L35210–35215.)*

<!-- FINAL1: R-BUDGET-05 canonical home; cleaned authority spec/01 S-11; registry row final/03; status SPECIFIED -->

**R-BUDGET-06 (time advancement).** Every transition has a logical-time delta `δ_t(c) ∈ ℕ`: pure computation `δ_t = 0`; host interactions and scheduler steps `δ_t > 0`. A transition is valid only if `t + δ_t(c) ≤ W`.

<!-- FINAL1: R-BUDGET-06 canonical home; cleaned authority spec/01 S-11; registry row final/03; status SPECIFIED -->

**R-BUDGET-07 (cost model).** Cost model `CostModel` MUST map operations to costs `Cost { consumable, reserved }`. Evaluator transitions MUST charge fuel cost before executing small-step transitions. *(L9155–9205; L10171–10177.)*

<!-- FINAL1: R-BUDGET-07 canonical home; cleaned authority spec/01 S-11; registry row final/03; status SPECIFIED -->

**R-BUDGET-08 (budget fault).** If `¬BudgetOK` (any gate fails), the transition is replaced by `fault(BudgetExhausted)`; no partial debit occurs.

<!-- FINAL1: R-BUDGET-08 canonical home; cleaned authority spec/01 S-11; registry row final/03; status SPECIFIED -->

**R-BUDGET-09 (escrow disposition totality — frozen addendum).** Escrow disposition is TOTAL: every unit entering the escrowed partition eventually leaves via exactly one frozen path — `Completed` (actual ≤ `complete_max` charged, remainder released), host-failure consumption (the C-23 rule), or durable `Reconciled` (R-RECOV-08). Held-forever-in-a-live-machine is NOT a disposition. Live faults unify with crash reconciliation: an actor fatal fault with an open effect enters the same reconciliation protocol as post-crash `Indeterminate`, and the supervisor fatal-fault policy MUST reference it. A logical-time bound moves stalled effects to reconciliation: a `Pending` effect whose deadline `W` expires (or a frozen per-effect logical timeout elapses) transitions to `Indeterminate` + reconciliation — machine state only, no wall clock (R-CAP-09), determinism preserved. Invariant: no reachable quiescent machine state contains escrow that no frozen rule can move; `C_available` shrinks only via `consumed` or durable `Reconciled`, never by strand. *(Frozen addendum — post-audit remediation SEC-021; additive per R-SCOPE-03; extends R-DUR-05/R-EFFECT-05/R-RECOV-08; resolves C-97; mutation M035; no source transcription.)*

<!-- FINAL1: R-BUDGET-09 canonical home; cleaned authority spec/01 S-11; registry row final/03; status SPECIFIED -->

**R-BUDGET-10 (resource-state atomicity — frozen addendum).** All resource mutations belonging to an operational transition occur transactionally: a failed precondition produces zero state drift and zero partial debit — `Precondition failure ⇒ Σ' = Σ` — except for post-issuance host-failure transitions, where `c_issue` remains consumed and the escrow is disposed via host-failure consumption/refund (R-DUR-07, R-BUDGET-11). This is the resource-level refinement of R-CORE-12's transition atomicity and R-CORE-14's s12–s14b atomic section: every Op-01…Op-22 transition is a single atomic resource mutation, and the `audit/_conservation_checker.py` randomized-transition harness is the gate evidence. *(Frozen addendum VIII — resource-accounting audit, owner decision 2026-09-03; additive per R-SCOPE-03; extends R-CORE-05/12, R-DUR-07; resolves C-108, decision U-45; no source transcription.)*

<!-- FINAL1: R-BUDGET-10 canonical home; cleaned authority spec/01 S-11; registry row final/03; status SPECIFIED -->

**R-BUDGET-11 (escrow disposition normal form — frozen addendum).** R-BUDGET-09's three paths are the escrow-disposition totality: every escrowed amount terminates via `Completed`, host-failure consumption, or durable `Reconciled`; the five-path normal form (`Consumed`, `Refunded`, `Transferred`, `Disposed-with-explicit-sink`, `Remains-Indeterminate`) is the complete fine structure OF that totality, not a fifth terminal path. `Consumed` (`C_consumed`) and `Refunded` (`C_available`) are the two leaves of `Completed` and of host-failure consumption (`actual ≤ complete_max` charged, remainder refunded; R-DUR-07). `Transferred` (child available partition) and `Disposed-with-explicit-sink` (`C_disposed` / `C_supervisor`) are the reconciled-outcome leaves selected per the R-RECOV-08 admissible-outcome table. `Remains-Indeterminate` (awaiting authoritative reconciliation) is a BOUNDED transient, not a disposition: it MUST reach reconciliation by the R-BUDGET-09 logical-time bound (machine state only, R-CAP-09) and then terminate via one of the four terminal leaves. No escrow may remain in any leaf indefinitely — the R-BUDGET-09 quiescent-strand invariant holds, and `C_available + C_escrowed + C_consumed + C_disposed = C_initial` at every reachable point. *(Frozen addendum VIII — resource-accounting audit, owner decision 2026-09-03; additive per R-SCOPE-03; extends R-BUDGET-09, R-DUR-05/07, R-EFFECT-05, R-RECOV-08/09; resolves C-108, decision U-45; mutation M039; no source transcription.)*

<!-- FINAL1: R-BUDGET-11 canonical home; cleaned authority spec/01 S-11; registry row final/03; status SPECIFIED -->

**R-BUDGET-13 (persistent-capacity accounting — frozen addendum).** Volatile RAM (`MEMORY` `M`) is kept strictly distinct from persistent storage capacity (`PERSISTENT_STORAGE` `M_storage`): RAM is released on scope exit or actor halt, while durable storage is retained across actor halts and managed via snapshot compaction (R-PERSIST-05/07, R-BUDGET-03 reservation predicates apply to each dimension separately). Persistent capacity MUST be accounted per WAL frame and per snapshot artifact; a snapshot that would exceed `M_storage` MUST fault, never silently truncate. *(Frozen addendum VIII — resource-accounting audit, owner decision 2026-09-03; additive per R-SCOPE-03; extends R-BUDGET-03/05, R-PERSIST-04/05/07; resolves C-108, decision U-45; no source transcription.)*

<!-- FINAL1: R-BUDGET-13 canonical home; cleaned authority spec/01 S-11; registry row final/03; status SPECIFIED -->

**R-BUDGET-15 (duration consumable semantics — frozen addendum).** `D` is the actor's REMAINING execution-duration budget, a per-actor consumable dimension strictly distinct from the absolute logical-time deadline `W` (`Deadline`; N-18). For every logical-time-advancing transition `ΔD := δ_t` — exactly ONE duration debit per time advance, `D ← D − δ_t` — and no other operation debits `D` (no double charge): `cost_C(E)`'s duration component is a DECLARED/DIAGNOSTIC prediction only (predicted-completion information), never a second debit authority. When the next time-advancing transition of an actor would make `δ_t > D`, that transition faults `DeadlineExceeded` for that actor with ZERO mutation — no budget, capability, escrow, reservation or time change (atomic failure, R-BUDGET-08 shape). The deadline/precedence order is `CapabilityViolation → BudgetExhausted → DeadlineExceeded → HostPolicyDenied`; every such fault preserves budgets. Mailbox-blocked and pending-effect waits charge nothing (δ_t = 0, ΔD = 0); `D` is never returned or refunded (R-BUDGET-01). *(Frozen addendum IX — duration-semantics audit, owner decision 2026-09-03; additive per R-SCOPE-03; extends R-BUDGET-01/06/08, R-CORE-05; resolves C-114/C-115, decisions U-01/U-07; mutation M042; no source transcription.)*

<!-- FINAL1: R-BUDGET-15 canonical home; cleaned authority spec/01 S-11; registry row final/03; status SPECIFIED -->

**R-BUDGET-16 (logical-time delta table — frozen addendum).** `δ_t` is enumerated exhaustively per transition kind: pure CEK transitions (let/seq/if/call/attenuate/attenuate-denied/request-denied/marshal-fault) 0; `E-Request` issuance (host-boundary crossing #1) 1; `E-Receipt` completion (crossing #2) 1; spawn 0; send 0; receive (dequeue) 0; receive-blocked / pending hold 0; the scheduler turn carries the executed transition's δ_t — NO additional turn charge; a host round trip is two crossings, so per-effect elapsed logical cost is 2; snapshot commit, WAL append/fsync, recovery replay, reconciliation and host-failure consumption/refund 0 (see the audit's 16-row sweep). Unknown transition kinds are a checker error, never a default. On every global time advance, each `Pending` effect's `W ≤ t'` is evaluated; expiry binds that effect to `Indeterminate` + R-RECOV-08. A post-deadline `EffectReceipt` is ADMITTED — the frozen `E-Receipt` premise `t + δ_t ≤ W` is SUPERSEDED (quoted, not deleted) and the receipt is settled via R-RECOV-08 classification, never the normal deadline gate. Stable quiescence (`GlobalStep::Deadlock` ∧ ∃`Pending`) is a deterministic driver transition `QuiescenceReconcile`: δ_t = 0, ΔD = 0, no `W` check, no budget mutation — `GlobalStep::Deadlock` itself is NOT the reconciliation transition; every `Pending` effect is recorded `Indeterminate` and bound to the R-RECOV-08 admissible-outcome protocol (never re-executed; a later receipt settles via R-RECOV-08 + R-HOST-06 + R-DUR-06). `Deadlock` without `Pending` (Blocked-only quiescence) admits NO reconciliation transition. This is the weakest rule making R-BUDGET-09's liveness bound reachable — no clock, no timer, no per-effect counter. *(Frozen addendum IX — duration-semantics audit, owner decision 2026-09-03; additive per R-SCOPE-03; extends R-BUDGET-06/09, R-RECOV-08, R-CORE-08; resolves C-112/C-113, decisions U-01/U-07; mutations M040/M041; tags TIME-DELTA-ENUMERATED, QUIESCENCE-RECONCILES-PENDING; no source transcription.)*

<!-- FINAL1: R-BUDGET-16 canonical home; cleaned authority spec/01 S-11; registry row final/03; status SPECIFIED -->


---

## §08 CEK Evaluator

The explicit CEK machine: state, the value-return invariant, the frozen continuation-frame set (closure env ≠ caller env), lambda capture, call ordering with arity precheck, continuation preservation, and progress/preservation. No recursion into host-stack calls (N-15-adjacent; prohibited shortcut list, R-CLAIM-02).

**Canonical homes transcribed in this section (7):** `R-CEK-01`, `R-CEK-02`, `R-CEK-03`, `R-CEK-04`, `R-CEK-05`, `R-CEK-06`, `R-CEK-07`.

**R-CEK-01 (explicit machine).** Evaluation MUST use an explicit CEK-style machine: state `EvalState { expr: Expr, env: Environment, continuation: Continuation }`. The evaluator MUST NOT depend on recursive host-language calls for call-stack depth. *(L41484–41499; L37800–37812.)*

<!-- FINAL1: R-CEK-01 canonical home; cleaned authority spec/01 S-08; registry row final/03; status SPECIFIED -->

**R-CEK-02 (value-return invariant, hard).** A value MUST be terminal if and only if its continuation is empty: `Value ∧ K = ε ⇒ Halt`; `Value ∧ K ≠ ε ⇒ Resume(K, Value)`. Evaluator steps MUST NOT return `Halt(v)` for `Expr::Value(v)` when `K ≠ ε`.

*(L16878–16905 (frozen); L17379–17412 (correction, same rule); L37826–37838.)*

<!-- FINAL1: R-CEK-02 canonical home; cleaned authority spec/01 S-08; registry row final/03; status SPECIFIED -->

**R-CEK-03 (continuation frames).** The frozen frame set is: `LetValue { name, body, env } | Seq { second, env } | If { then, else, env } | CallFunction { args, env } | CallArgument { function, evaluated, remaining, caller_env } | Attenuate { name, body, env } | RequestCapability { operation, target, params, env } | RequestTarget { capability, operation, params, caller_env } | RequestArgument { capability, operation, target, evaluated, remaining, caller_env }`. `function.env` (closure lexical environment) and `caller_env` (call-site environment) are semantically different and MUST never be conflated. *(L16928–16958; L23821–23856.)*

<!-- FINAL1: R-CEK-03 canonical home; cleaned authority spec/01 S-08; registry row final/03; status SPECIFIED -->

**R-CEK-04 (lambda).** Lambda creation MUST be pure and deterministic: it MUST capture the lexical environment at creation and MUST produce `FunctionValue { params, body, env }`; the resulting value MUST pass through the ordinary value-return mechanism and MUST NOT halt the machine immediately. [INFORMATIVE: "deterministic" is explicitly defined in S-02 / R-CORE-08]. *(L16971–16995; L19095–19110 (attenuate/lexical invariant context).)*

<!-- FINAL1: R-CEK-04 canonical home; cleaned authority spec/01 S-08; registry row final/03; status SPECIFIED -->

**R-CEK-05 (call).** Function application MUST proceed left-to-right: (1) evaluate `func` to `FunctionValue`; (2) evaluate arguments left-to-right (`CEK-CALL-ARGS-LTR`); (3) pre-check arity (`CEK-CALL-ARITY-PRECHECK`) — mismatch MUST produce `fault(F_arity)` before frame stack allocation; (4) bind parameters in a fresh child environment inheriting captured bindings; (5) push return frame and evaluate body. *(L16878–16905 (frozen); L37840–37862; L18723–18851.)*

<!-- FINAL1: R-CEK-05 canonical home; cleaned authority spec/01 S-08; registry row final/03; status SPECIFIED -->

**R-CEK-06 (continuation preservation).** For pure transitions the continuation length changes by exactly +1 on entry or −1 on resume; no transition silently discards or duplicates frames.

<!-- FINAL1: R-CEK-06 canonical home; cleaned authority spec/01 S-08; registry row final/03; status SPECIFIED -->

**R-CEK-07 (progress & preservation).** A well-typed, well-budgeted configuration is either a value, a fault, pending an effect, blocked on a message, or can take a step; every transition preserves well-typedness and well-budgetness.

<!-- FINAL1: R-CEK-07 canonical home; cleaned authority spec/01 S-08; registry row final/03; status SPECIFIED -->


---

## §09 Actors

Actor isolation, global state, deterministic identity allocation, spawn transactionality, messaging, the no-amplification/no-teleportation pair, and the frozen spawn-authority (R-ACTOR-09) and mailbox-admission (R-ACTOR-10) obligations. The scheduler-visible obligations R-ACTOR-04 and R-ACTOR-07 are homed in §10; they are actors-adjacent but the canonical FIFO/at-most-once and scheduling-theorem statements are scheduler material (cleaned source S-15 split — see `final/02`).

**Canonical homes transcribed in this section (8):** `R-ACTOR-01`, `R-ACTOR-02`, `R-ACTOR-03`, `R-ACTOR-05`, `R-ACTOR-06`, `R-ACTOR-08`, `R-ACTOR-09`, `R-ACTOR-10`.

**R-ACTOR-01 (isolation).** Actors have isolated environments, continuations, heaps, mailboxes, budgets, and capability contexts. For `a ≠ b`: `Heap(a) ∩ Heap(b) = ∅ ∧ Env(a) ∩ Env(b) = ∅`. No actor mutates another actor's heap, environment, or continuation. Actors are instantiated with fresh arenas and `Environment::empty()` (no implicit environment inheritance).

<!-- FINAL1: R-ACTOR-01 canonical home; cleaned authority spec/01 S-15; registry row final/03; status SPECIFIED -->

**R-ACTOR-02 (global state).** Global state MUST manage actors in a `BTreeMap<ActorId, ActorState>`. Global time `LogicalTime` MUST advance monotonically on scheduler steps. *(L24148–24163; L25514–25546.)*

<!-- FINAL1: R-ACTOR-02 canonical home; cleaned authority spec/01 S-15; registry row final/03; status SPECIFIED -->

**R-ACTOR-03 (deterministic IDs).** `ActorId` and `EffectId` MUST be allocated by global monotonic counters (`N' = N + 1`). Actor identity MUST NOT be derived from memory addresses, OS PIDs, random UUIDs, thread IDs, or wall-clock timestamps. [INFORMATIVE: "deterministic" allocation is defined by monotonic integer counters]. *(L24226–24245.)*

<!-- FINAL1: R-ACTOR-03 canonical home; cleaned authority spec/01 S-15; registry row final/03; status SPECIFIED -->

**R-ACTOR-05 (spawn).** Spawn MUST be a deterministic, transactional machine operation: (1) validate and escrow budget (`BudgetAllocationSpec` → `validate_and_escrow`); (2) allocate child `ActorId`; (3) derive child capabilities via `kernel.derive(parent_cap, constraint, t)`; wholesale capability copying/cloning MUST NOT occur; (4) construct isolated child state; (5) enqueue child into runnable queue deterministically; (6) log `ActorSpawned`. [INFORMATIVE: "deterministic" is explicitly defined in S-02 / R-CORE-08]. *(L25573–25615; L25616–25673; L37941–37951.)*

<!-- FINAL1: R-ACTOR-05 canonical home; cleaned authority spec/01 S-15; registry row final/03; status SPECIFIED -->

**R-ACTOR-06 (send/receive).** `Send` MUST be asynchronous: marshal the value, enqueue into target mailbox, log `MessageSent`, and deterministically wake a `Blocked` target exactly once. `Receive` MUST dequeue (unmarshal) or, on empty mailbox, block without consuming fuel (`Blocked` MUST be a suspension state, yielding to scheduler). Mailboxes MUST be FIFO. *(L25702–25749; L25674–25701; L37941–37951.)*

<!-- FINAL1: R-ACTOR-06 canonical home; cleaned authority spec/01 S-15; registry row final/03; status SPECIFIED -->

**R-ACTOR-08 (no amplification / no teleportation theorems).** `Authority_after ≼ Authority_before ∪ ExplicitlyDelegatedAuthority` (ordinary `Send` passes through `marshal()`, which rejects raw capabilities). `Σ_actors C_consumable + Σ_escrow C_escrow + Σ_issued C_issue = C_global_initial` (budget is created only at root initialization; spawn escrows; send carries no budget).

<!-- FINAL1: R-ACTOR-08 canonical home; cleaned authority spec/01 S-15; registry row final/03; status SPECIFIED -->

**R-ACTOR-09 (spawn authority rule — frozen addendum).** `Expr::Spawn` MUST NOT transfer parent capabilities by default: a spawned child's initial authority context is empty, and delegation (R-MARSHAL-05) is the only default transfer path. Any spawn-time authority transfer MUST be explicit: the plan declares a capability manifest plus constraint, compiler-checked against the plan's declared capability set (the R-COMPILE-06 discipline), and the kernel derives each manifest entry strictly attenuated (constraint ≠ ⊤ — identity derivation is not spawn). The spawn security theorem is strict: `Authority(child) ≺ Authority(parent)` — `≼` is reserved for delegation; wholesale capability copying (iterating the parent context under one constraint) is FORBIDDEN: the engineering rule binds the default case, not only explicit cloning. The v0.3 `trust_level`/`attenuated_context(κ_parent, trust_level)` form is SUPERSEDED (quoted, not deleted; the AMB-04 phantom is resolved by retraction). `BudgetAllocationSpec::validate_and_escrow` MUST be bounded: maximum child share, minimum parent retention, fault on violation (closes U-03 in the security direction). *(Frozen addendum — post-audit remediation SEC-006; additive per R-SCOPE-03; extends R-ACTOR-05/R-COMPILE-06/R-MARSHAL-05; resolves C-82; mutation M025; no source transcription.)*

<!-- FINAL1: R-ACTOR-09 canonical home; cleaned authority spec/01 S-15; registry row final/03; status SPECIFIED -->

**R-ACTOR-10 (mailbox resource admission — frozen addendum).** Mailbox admission is resource-gated: `Enqueue(v, target)` requires available recipient mailbox capacity — capacity is part of the recipient's `M` reservation — and on denial the SENDER faults with `ReservedCapacityExceeded` (sender pays; never silent growth). The send cost MUST be payload-proportional: `cost_C(send) ≥ f(canonical_len(v))` for a frozen monotone `f` bounded away from zero per byte (deterministic over canonical bytes, replay-stable). Constructed value size is bounded against the constructing actor's `M` reservation (allocation is the resource the reservation exists for). Invariant: for any reachable state, the total mailbox footprint is bounded by total reserved `M` at every step — the resource-bounded thesis holds in the heap, not only in the algebra. *(Frozen addendum — post-audit remediation SEC-019; additive per R-SCOPE-03; extends R-ACTOR-06/R-BUDGET-01/R-EFFECT-04; resolves C-96, closing the U-03/U-07 resource-admission direction; mutation M033; no source transcription.)*

<!-- FINAL1: R-ACTOR-10 canonical home; cleaned authority spec/01 S-15; registry row final/03; status SPECIFIED -->


---

## §10 Scheduler

The deterministic scheduler: FIFO order with at-most-once runnable membership (R-ACTOR-04) and the deterministic-concurrency theorem (R-ACTOR-07, the canonical Phase-13 form of the determinism invariant per the `mod/18` duplication register D-05). The theorem inherits the recorded U-35 limitation: its parameters `SchedulerTrace`/`HostTrace`/`InitialState`/`UniqueMachineTrace` remain undefined in the corpus, which makes the unqualified theorem form currently unfalsifiable — carried forward, not quietly fixed (GI-DET-01 note).

**Canonical homes transcribed in this section (2):** `R-ACTOR-04`, `R-ACTOR-07`.

**R-ACTOR-04 (FIFO scheduler).** Scheduler queue `RunnableQueue` MUST enforce FIFO order and at-most-once membership for runnable actors. Duplicate runnable queue entries MUST NOT exist. *(L25558–25615 (frozen with at-most-once invariant); L24165–24224; L37924–37937.)*

<!-- FINAL1: R-ACTOR-04 canonical home; cleaned authority spec/01 S-15; registry row final/03; status SPECIFIED -->

**R-ACTOR-07 (deterministic concurrency theorem).** Concurrency MUST satisfy the deterministic scheduling theorem: `InitialState + SchedulerTrace + HostTrace ⇒ UniqueMachineTrace` — scheduler MUST be strictly FIFO, IDs MUST be monotonic, CEK machine MUST be deterministic; hence global state transitions MUST be uniquely determined given identical initial state and external observations. [INFORMATIVE: "deterministic" is explicitly defined by this theorem]. *(L25759–25766 (Theorem 1).)*

<!-- FINAL1: R-ACTOR-07 canonical home; cleaned authority spec/01 S-15; registry row final/03; status SPECIFIED -->


---

## §11 Effects

The effect pipeline as one frozen sequence: the request protocol (R-CORE-14 canonical 16-step order over the 16 obligations here), the gated transition shape, short-circuit denial, guaranteed completion accounting, receipt causality, completion accounting, receipt-result admission, and the transactional issuance boundary (R-DUR-01…07). Effect ordering is *frozen* material: `Prepared → Issued → HostInvoked → Completed/Reconciled` and the durable-before-host hinge are restated nowhere in this document except via GI references (GI-SEC-07, GI-SEC-09, GI-SEC-10, GI-REC-01).

**Canonical homes transcribed in this section (15):** `R-EFFECT-01`, `R-EFFECT-02`, `R-EFFECT-03`, `R-EFFECT-04`, `R-EFFECT-05`, `R-EFFECT-06`, `R-EFFECT-07`, `R-EFFECT-08`, `R-DUR-01`, `R-DUR-02`, `R-DUR-03`, `R-DUR-04`, `R-DUR-05`, `R-DUR-06`, `R-DUR-07`.

**R-EFFECT-01 (request semantics).** Effect requests MUST proceed through the 16-step protocol: (1) evaluate `Request` expression; (2) resolve `CapRef`; (3) verify capability valid and unrevoked; (4) verify authorization `Authorized(c, e, t)`; (5) verify capability within ceiling; (6) verify budget available for `issue + complete_max`; (7) verify deadline `t ≤ W`; (8) verify host policy; (9) charge `issue` cost; (10) escrow `complete_max` cost; (11) reserve capacity; (12) allocate monotonic `EffectId`; (13) construct canonical `Effect`; (14) write durable `Prepared` log record; (15) emit `EffectRequest` to host; (16) write durable `Issued` record before host execution completes. *(L12177–12194.)*

<!-- FINAL1: R-EFFECT-01 canonical home; cleaned authority spec/01 S-12; registry row final/03; status SPECIFIED -->

**R-EFFECT-02 (gated transition shape).** Every active transition takes the canonical gated form: `Pre(c, Σ) ∧ BudgetOK(c, Σ) ∧ AuthOK(c, Σ) ⊢ Σ →_c Σ'`. `AuthOK` applies only to authority-requiring transitions.

<!-- FINAL1: R-EFFECT-02 canonical home; cleaned authority spec/01 S-12; registry row final/03; status SPECIFIED -->

**R-EFFECT-03 (frozen 16-step request sequence, canonical).** `EffectId` MUST be allocated from a global monotonic counter (`N' = N + 1`). `EffectId` MUST NOT be derived from wall-clock timestamps, memory addresses, or random generators. [INFORMATIVE: "deterministic" allocation is defined by monotonic integer counters].

*(L37891–37908 (master-prompt 16-step, latest frozen form); L23857–23948 (14-gate machine-internal form, gates 1–14, superseded numbering — see `C-01`); L11053–11090 (14-step `step_request` form, superseded numbering).)*

<!-- FINAL1: R-EFFECT-03 canonical home; cleaned authority spec/01 S-12; registry row final/03; status SPECIFIED -->

**R-EFFECT-04 (short-circuit).** A denial at any gate MUST short-circuit: subsequent gates are not called, `next_effect_id` is not incremented, the actor budget is unchanged, the event log gains no new entries, and `HostExecutor::execute` is never invoked.

<!-- FINAL1: R-EFFECT-04 canonical home; cleaned authority spec/01 S-12; registry row final/03; status SPECIFIED -->

**R-EFFECT-05 (guaranteed completion accounting).** At issuance the machine MUST guarantee the maximum possible completion cost is affordable: gate 8 checks `can_consume(issue.checked_add(complete_max))` (overflow ⇒ `Fault::ArithmeticOverflow`/budget fault). The remaining budget is then mathematically guaranteed ≥ `complete_max`.

<!-- FINAL1: R-EFFECT-05 canonical home; cleaned authority spec/01 S-12; registry row final/03; status SPECIFIED -->

**R-EFFECT-06 (causal receipt validation).** A receipt MUST be validated against **both** `EffectId` and `EffectDigest` of the pending effect before resumption: mismatch ⇒ `fault(ReplayCorruption)`, continuation is NOT resumed, reservation is NOT released. `EffectReceipt { id, effect_digest, result: Result<Value, HostFault> }`.

<!-- FINAL1: R-EFFECT-06 canonical home; cleaned authority spec/01 S-12; registry row final/03; status SPECIFIED -->

**R-EFFECT-07 (completion accounting).** On valid receipt: charge `complete` (≤ `complete_max`) from consumables, release the reservation, append `EffectCompleted { id, digest, result }` to the event log, resume the continuation with the receipt's value (host faults map to the fault/value mapping defined by the machine).

<!-- FINAL1: R-EFFECT-07 canonical home; cleaned authority spec/01 S-12; registry row final/03; status SPECIFIED -->

**R-EFFECT-08 (receipt-result admission — frozen addendum).** A receipt may complete an effect; it MUST NOT confer authority. Before any continuation is resumed, the machine MUST run the recursive `contains_capability` predicate over the receipt's result payload at every nesting depth (`List`/`Map`/`Tuple` included) and MUST fault (`Fault::InvalidReceipt` family) on any `Value::Capability` and on any host `Function`/closure value. An admitted result MUST lie in the canonical data-domain (the 8-variant codec value set); host error results MUST enter machine values only through a declared, closed fault mapping — raw debug-formatted host text MUST NOT. This extends R-EFFECT-06 (causal validation of `id` and digest) from the receipt's identity to its payload: every value-crossing — messages, receipts, snapshots, replay traces — is subject to the no-raw-capability-transfer rule (R-CORE-07). *(Frozen addendum — post-audit remediation SEC-001 items 1–4; additive per R-SCOPE-03; extends R-EFFECT-06/R-EFFECT-07; no source transcription.)*

<!-- FINAL1: R-EFFECT-08 canonical home; cleaned authority spec/01 S-12; registry row final/03; status SPECIFIED -->

**R-DUR-01.** `HostInvoked(E) ⇒ DurableIssued(E)`. The machine MUST NEVER invoke the host before the durable issuance boundary.

<!-- FINAL1: R-DUR-01 canonical home; cleaned authority spec/01 S-13; registry row final/03; status SPECIFIED -->

**R-DUR-02 (issuance transaction, strict order).** 1. Pure validation / authorization / budget checks; 2. `persistence.append(EffectPrepared { id, actor, digest })`; 3. `persistence.sync()` (fsync); 4. `persistence.append(EffectIssued { id, actor, digest })`; 5. `persistence.sync()` (fsync); 6. machine transitions actor to `Pending`; 7. host adapter receives `EffectRequest`. *(L35150–35158.)*

<!-- FINAL1: R-DUR-02 canonical home; cleaned authority spec/01 S-13; registry row final/03; status SPECIFIED -->

**R-DUR-03 (causal effect protocol).** `Issued(E) ⇒ Prepared(E)`; `Completed(E) ⇒ Issued(E)`; `Reconciled(E) ⇒ Issued(E)`. Every subsequent record for an effect MUST carry the identical `EffectId` and `EffectDigest`; a digest mismatch is `EffectJournalCorruption`, not a different effect.

<!-- FINAL1: R-DUR-03 canonical home; cleaned authority spec/01 S-13; registry row final/03; status SPECIFIED -->

**R-DUR-04 (crash classification of effects).** Effect state transitions MUST strictly follow `Prepared → Issued → Completed` or `Issued → Reconciled`. A prepared-but-never-issued effect MUST be discarded during recovery. An issued-but-not-completed effect MUST be classified as `Indeterminate` unless authoritative host reconciliation establishes its outcome. *(L35159–35176; L37968–37981.)*

<!-- FINAL1: R-DUR-04 canonical home; cleaned authority spec/01 S-13; registry row final/03; status SPECIFIED -->

**R-DUR-05 (escrow survives crash).** An `Issued` effect with no durable completion retains its `completion_maximum` in the `escrowed` partition until reconciliation determines the outcome. Escrow does not vanish on crash.

<!-- FINAL1: R-DUR-05 canonical home; cleaned authority spec/01 S-13; registry row final/03; status SPECIFIED -->

**R-DUR-06 (durable issuance payload — frozen addendum).** The issuance records MUST carry the effect and its cost: `EffectPrepared { id, actor, digest, effect_bytes, issue, complete_max, reserve }` and `EffectIssued { id, actor, digest, effect_bytes, issue, complete_max, reserve }` MUST be the persistence payloads — the canonical bytes of the effect, its `EffectDigest`, and the `EffectCost { issue, complete_max, reserve }`. The `{id, actor, digest}` shapes are SUPERSEDED as persistence payloads (quoted, not deleted); `{id, actor, digest}` remains valid only as the planner-visible observation projection (R-PLANNER-07). The escrowed `complete_max` and the reservation MUST thereby be reconstructible at every T0–T6 point: T1 discard restores from the record, T2–T4 classification and reconciliation carry the effect they must query about, and T5 resumption is byte-exact from the record. `effect_bytes` MUST verify `EffectDigest(effect_bytes) = digest` at append and at recovery — a mismatch is `EffectJournalCorruption` (C-105). The records MUST NOT contain raw capability values (R-CORE-07/R-CANON-12: the kernel-mediated codec governs). *(Frozen addendum VII — request-pipeline remediation, owner decision 2026-09-03; additive per R-SCOPE-03; extends R-DUR-02/05, R-PERSIST-03, R-EFFECT-05, R-RECOV-06; resolves C-105, decision U-41; mutation M038; no source transcription.)*

<!-- FINAL1: R-DUR-06 canonical home; cleaned authority spec/01 S-13; registry row final/03; status SPECIFIED -->

**R-DUR-07 (live issuance failure — frozen addendum).** Persistence failures on the issuance path are data, never panics (R-CORE-12), and MUST fault with the declared `Fault::PersistenceError`, added to the R-CORE-13 closed declaration by this addendum. The commit is journal-driven: `persistence.append(EffectPrepared …)` per R-DUR-06 followed by `persistence.sync()` is the ONE durable mutation that also journals the ID allocation and the budget/reservation/escrow commit; the in-memory mutations of steps 12–13 MUST NOT occur before that append+fsync returns Ok (C-106). On any append or sync error: the transition faults, `next_effect_id`, budget, reservations and escrow are at their pre-s12 values, the event log gains no entry, and `HostExecutor::execute` is NEVER invoked — R-EFFECT-04's five assertions hold on this path. A failure of the second `sync()` (the `Issued` record's fsync) is likewise `Fault::PersistenceError`, with the machine rolled back to the `Prepared`-durable state and the journal classifying the effect `Prepared ∧ ¬Issued ⇒ Discard` at recovery (R-DUR-04, R-RECOV-02 T1). No `InternalInvariant` classification is permitted for a storage error — this is the single declared fault family for the issuance path. *(Frozen addendum VII — request-pipeline remediation, owner decision 2026-09-03; additive per R-SCOPE-03; extends R-DUR-02/04, R-EFFECT-04, R-CORE-12/13, R-PERSIST-02/03; resolves C-106, decision U-42; mutation M037; no source transcription.)*

<!-- FINAL1: R-DUR-07 canonical home; cleaned authority spec/01 S-13; registry row final/03; status SPECIFIED -->


---

## §12 Host Policy

The host gate, adapter scope, the ordered replay host, the replay correspondence theorem, trace validation, and the durable receipt-result contract (R-HOST-06). The host is partially trusted; the negative guarantees (no host before durable issuance; replay never touches the external world) are carried at full strength.

**Canonical homes transcribed in this section (6):** `R-HOST-01`, `R-HOST-02`, `R-HOST-03`, `R-HOST-04`, `R-HOST-05`, `R-HOST-06`.

**R-HOST-01 (host gate, defense in depth).** The live host independently validates concrete OS-level authority/policy for each effect (`HostPolicyOK`); `¬HostPolicyOK(E) ⇒ ¬ExternalEffect(E)`. The machine's gate-11 check is fail-early; the host check is authoritative.

<!-- FINAL1: R-HOST-01 canonical home; cleaned authority spec/01 S-14; registry row final/03; status SPECIFIED -->

**R-HOST-02 (host adapter scope).** The host performs **only issued effects**. It is partially trusted.

<!-- FINAL1: R-HOST-02 canonical home; cleaned authority spec/01 S-14; registry row final/03; status SPECIFIED -->

**R-HOST-03 (replay host).** `ReplayHost` reconstructs recorded effects; it NEVER touches the external world. It is **ordered**: for every request it consumes the next trace entry and validates both `EffectId` and `EffectDigest` sequentially; a mismatch or exhausted trace ⇒ `ReplayCorruption`/`ReplayTraceExhausted`. An unordered map MUST NOT be used as the normative replay mechanism.

<!-- FINAL1: R-HOST-03 canonical home; cleaned authority spec/01 S-14; registry row final/03; status SPECIFIED -->

**R-HOST-04 (replay correspondence theorem).** If `LiveRun(Σ₀)` produces trace `T` of (EffectIssued, EffectCompleted) pairs, `ReplayRun(Σ₀, T)` produces the same final configuration, provided replay verifies for each step `E_replay,k = E_recorded,k` and `R_replay,k.id = R_recorded,k.id` (and, in the frozen form, matching digests). Machine-state replay is always valid; real-world replay is only valid for reversible/idempotent effects — the replay host refuses to re-execute irreversible effects and returns the recorded result.

<!-- FINAL1: R-HOST-04 canonical home; cleaned authority spec/01 S-14; registry row final/03; status SPECIFIED -->

**R-HOST-05 (replay validates trace, not just final state).** Replay MUST validate the trace, not merely load the final state.

<!-- FINAL1: R-HOST-05 canonical home; cleaned authority spec/01 S-14; registry row final/03; status SPECIFIED -->

**R-HOST-06 (durable receipt results — frozen addendum).** Durable receipt results MUST be representable under a frozen contract: `EffectCompleted` carries `{id, digest, result_digest, result: CanonicalData}` — `result` scoped to the canonical data domain (R-CANON-12 / the R-EFFECT-08 admission rule). Replay MUST verify `ResultDigest(result) = result_digest` before the receipt may resume anything: a third identity conjunct extending R-EFFECT-06 (id, effect digest, result digest). Tampering `result` while keeping the digest-pair ⇒ `ReplayCorruption`. No ad-hoc result-bearing record kind may exist outside this contract (the unfrozen-record channel is closed); T5 recovery resumes the continuation with the recorded result byte-exactly. *(Frozen addendum — post-audit remediation SEC-011; additive per R-SCOPE-03; extends R-EFFECT-06/R-EFFECT-08/R-HOST-03/R-HOST-04; resolves C-90; mutation M029; no source transcription.)*

<!-- FINAL1: R-HOST-06 canonical home; cleaned authority spec/01 S-14; registry row final/03; status SPECIFIED -->


---

## §13 Serialization

Canonical serialization (Phase 15A wire format) and the marshalling/delegation boundary. This is the single home of: the universal envelope, the frozen tag namespaces, collection encodings, the strict decoder contract, checked arithmetic, the digest rules, the scoped injectivity claim, golden vectors as normative fixtures, the decode-side authority-minting ban (R-CANON-12), the one-grammar decision (R-CANON-13), recursive capability rejection (R-MARSHAL-01/02/06), the explicit delegation envelope (R-MARSHAL-05), and `MarshalledValue` as the canonical transport. Production `CapRef`/`ActorId`/`EffectId` encodings live here; the reference model's distinct `Ref*Id` identifiers are defined in §17 and are not re-typed here.

**Canonical homes transcribed in this section (19):** `R-MARSHAL-01`, `R-MARSHAL-02`, `R-MARSHAL-03`, `R-MARSHAL-04`, `R-MARSHAL-05`, `R-MARSHAL-06`, `R-CANON-01`, `R-CANON-02`, `R-CANON-03`, `R-CANON-04`, `R-CANON-05`, `R-CANON-06`, `R-CANON-07`, `R-CANON-08`, `R-CANON-09`, `R-CANON-10`, `R-CANON-11`, `R-CANON-12`, `R-CANON-13`.

**R-MARSHAL-01 (capability rejection, recursive).** Ordinary data marshalling MUST reject capabilities recursively — including capabilities nested inside lists, tuples, functions, or any nested structure. Raw `CapRef` transfer through ordinary messages is forbidden: `marshal_value(v) ⇒ Err(MarshalFault::CapabilityRequiresDelegation)` if `contains_capability(v)`.

<!-- FINAL1: R-MARSHAL-01 canonical home; cleaned authority spec/01 S-16; registry row final/03; status SPECIFIED -->

**R-MARSHAL-02 (explicit delegation).** Raw capability references `Value::Capability(CapRef)` MUST NOT be transferred through ordinary messages; ordinary marshalling MUST reject raw capabilities with `MarshalFault`. Delegation of authority MUST require explicit `Value::DelegatedCapability(DelegatedCapability)` envelopes. *(L25972–26001; L37953–37959.)*

<!-- FINAL1: R-MARSHAL-02 canonical home; cleaned authority spec/01 S-16; registry row final/03; status SPECIFIED -->

**R-MARSHAL-03 (canonical transport).** `MarshalledValue` is the canonical serialized byte representation (`canonical_serialize(v)`); `unmarshal(marshal(v)) = v` for all pure values.

<!-- FINAL1: R-MARSHAL-03 canonical home; cleaned authority spec/01 S-16; registry row final/03; status SPECIFIED -->

**R-MARSHAL-04 (semantic marshalling rule).** `marshal(v)` traverses `v`; by default `CapRef ∉ marshal(v)`; authority transfer requires the explicit `delegate(c, C, target_actor)` operation.

<!-- FINAL1: R-MARSHAL-04 canonical home; cleaned authority spec/01 S-16; registry row final/03; status SPECIFIED -->

**R-MARSHAL-05 (delegation surface constructible and revalidated — frozen addendum).** The sanctioned authority-transfer channel MUST be constructible as frozen: `Expr::Delegate { capability, constraint }` evaluates by calling `kernel.derive` with the declared constraint and produces a kernel-constructed delegation envelope — NOT a plain `Value` variant; `Value::DelegatedCapability` as a data variant is forbidden. Envelope admission at `Receive`: `register(envelope, recipient)` MUST be preceded by kernel revalidation — liveness, lineage (`DelegatedAuthority ≼ ParentAuthority`), target binding, and generation — against an existing kernel derivation record `d` with `envelope.cap = d.child ∧ d.parent ∈ sender.context`; any failure MUST fault with the recipient's `CapabilityContext` byte-identical (no partial registration). `MarshalledValue` is the checked-bytes form (R-MARSHAL-03): mailbox bytes MUST NOT exist as a `Value`, snapshots storing mailboxes store the checked form, and the private-constructor-wrapper reading is SUPERSEDED (quoted, not deleted). `MarshalFault` has ONE unified closed variant set. *(Frozen addendum — post-audit remediation SEC-005; additive per R-SCOPE-03; extends R-MARSHAL-02/R-MARSHAL-04; resolves C-79 and, at the normative layer, term/ X-65; no source transcription.)*

<!-- FINAL1: R-MARSHAL-05 canonical home; cleaned authority spec/01 S-16; registry row final/03; status SPECIFIED -->

**R-MARSHAL-06 (contains_capability is a frozen total predicate — frozen addendum).** `contains_capability(v)` MUST be a total predicate with an explicitly closed traversal domain: it MUST descend recursively, at unbounded structural depth, into `List`, `Map` (keys and values), `Tuple` elements, and — the load-bearing case — `FunctionValue.env` (captured closure environments, recursively: environments bind names to `Value`, and a closure whose environment binds a capability carries authority). Kernel-sealed delegation envelopes (R-MARSHAL-05) are the sole exclusion, and then only sealed by the kernel. `Bytes` are data — the decode-side rule (R-CANON-12) governs their rehydration. The boundary invariant is stated over reachability, not one value domain: `marshal(v) = Ok ⇒ ¬∃c. Reachable(env_of(v), c)` outside kernel-sealed envelopes. Closure-carrying values whose environments bind capabilities MUST fault at `marshal`, never round-trip. *(Frozen addendum — post-audit remediation SEC-018; additive per R-SCOPE-03; extends R-CORE-07/R-MARSHAL-01; resolves C-81; no source transcription.)*

<!-- FINAL1: R-MARSHAL-06 canonical home; cleaned authority spec/01 S-16; registry row final/03; status SPECIFIED -->

**R-CANON-01 (purpose & independence).** Semantic serialization is explicit and independent of Rust memory layout and of any Rust serializer. `bincode` may *implement* the format but MUST NOT *define* it. Canonical encoding defines semantic identity; it is not based on struct layout, pointer addresses, allocator behavior, or platform-specific representation.

<!-- FINAL1: R-CANON-01 canonical home; cleaned authority spec/01 S-17; registry row final/03; status SPECIFIED -->

**R-CANON-02 (universal envelope, frozen).** ``` Envelope := version: u8            (currently 0x01) + type_tag: u8           (stable explicit constant per type) + payload_length: u32 BE (checked) + payload: bytes[payload_length] ``` *(L30532–30543; L33290–33347 (final frozen).)*

<!-- FINAL1: R-CANON-02 canonical home; cleaned authority spec/01 S-17; registry row final/03; status SPECIFIED -->

**R-CANON-03 (type tags, frozen).** Standalone envelope tags: `Value` = `0x00`; `Symbol` = `0x20`; `CapRef` = `0x30`; `ActorId` = `0x40`; `EffectId` = `0x41`. **Non-normative note:** the "revised grammar" §1.3 text listing Boolean `0x10` / Integer `0x11` / String `0x13` as standalone tags is stale and contradicted by the golden vectors and the final frozen implementation (see `C-02`); bool/integer/string exist only as `Value` discriminants.

<!-- FINAL1: R-CANON-03 canonical home; cleaned authority spec/01 S-17; registry row final/03; status SPECIFIED -->

**R-CANON-04 (Value encoding, frozen).** Collection encodings (List, Tuple, Map) MUST prefix element counts as `u32` length headers. Decoders MUST verify payload byte availability before allocating collection memory. *(L30544–30552 (correction); L33155–33265 (final).)*

<!-- FINAL1: R-CANON-04 canonical home; cleaned authority spec/01 S-17; registry row final/03; status SPECIFIED -->

**R-CANON-05 (primitives, frozen).** `Symbol(u32)` payload = 4 bytes BE; `CapRef` payload = `[index u32 BE][generation u32 BE]`; `ActorId`/`EffectId` payloads = 8 bytes u64 BE.

<!-- FINAL1: R-CANON-05 canonical home; cleaned authority spec/01 S-17; registry row final/03; status SPECIFIED -->

**R-CANON-06 (collections, frozen).** `List = [count u32 BE][element₁]…[elementₙ]`, each element a complete envelope. `Map = [count u32 BE][key₁][val₁]…`, entries ordered by the **semantic `Ord` relation on keys** (for `BTreeMap<u32, Value>`: numeric u32 order). Map decoding MUST reject duplicate keys (`CanonicalError::DuplicateMapKey`) to preserve injectivity.

<!-- FINAL1: R-CANON-06 canonical home; cleaned authority spec/01 S-17; registry row final/03; status SPECIFIED -->

**R-CANON-07 (decoder contract, frozen).** `CanonicalDecode` is a strict parser enforcing, in order: (1) version = `0x01`; (2) type tag matches expected; (3) exact length (payload is exactly `payload_length` bytes); (4) internal payload well-formedness; (5) EOF/trailing-byte rejection. All discriminants are explicit stable constants (source-order changes MUST NOT change the wire format). Malformed encodings are rejected with explicit `CanonicalError` values (`InvalidVersion, InvalidTypeTag, LengthMismatch, LengthOverflow, InvalidUtf8, UnexpectedEof, TrailingBytes, InvalidDiscriminant, InvalidBoolValue, DuplicateMapKey`).

<!-- FINAL1: R-CANON-07 canonical home; cleaned authority spec/01 S-17; registry row final/03; status SPECIFIED -->

**R-CANON-08 (checked arithmetic).** All length/pointer arithmetic is checked. A collection exceeding `u32::MAX` yields `LengthOverflow`. Encoded collection counts MUST NOT authorize attacker-controlled preallocation (collections grow organically from `Vec::new()`, no `with_capacity` on untrusted input). Nested decoding uses bounded cursors (`read_envelope_payload` returns only the payload slice; payload decoding uses a fresh bounded cursor). Envelope construction is fallible (no panics).

<!-- FINAL1: R-CANON-08 canonical home; cleaned authority spec/01 S-17; registry row final/03; status SPECIFIED -->

**R-CANON-09 (digests).** `StateDigest = SHA-256(canonical_bytes)`; `EffectDigest = SHA-256(canonical_bytes(effect))`. Mechanically: `Canonical(x) = Canonical(y) ⇒ Digest(x) = Digest(y)`. The reverse direction holds only as an operational integrity assumption under cryptographic collision resistance. When both states are available, compare canonical bytes directly; use digests for persistence integrity, causal identity, and compact checkpoints.

<!-- FINAL1: R-CANON-09 canonical home; cleaned authority spec/01 S-17; registry row final/03; status SPECIFIED -->

**R-CANON-10 (injectivity, scoped claim).** Injectivity (`Canonical(x) = Canonical(y) ⇒ x = y`) is a **structural specification property** of the encoding design; the conformance suite provides machine-checked evidence via round-trip and differential testing over the generated distribution. It is NOT claimed as a mathematical proof of arbitrary Rust programs.

<!-- FINAL1: R-CANON-10 canonical home; cleaned authority spec/01 S-17; registry row final/03; status SPECIFIED -->

**R-CANON-11 (golden vectors, normative fixtures).** The frozen golden vectors (e.g., `Value::Integer(42)` ⇒ `01 00 00 00 00 09 02 00 00 00 00 00 00 00 2A`; `CapRef{5,2}` ⇒ `01 30 00 00 00 08 00 00 00 05 00 00 00 02`) are normative **test fixtures** for the format, not additional behavioral rules.

<!-- FINAL1: R-CANON-11 canonical home; cleaned authority spec/01 S-17; registry row final/03; status SPECIFIED -->

**R-CANON-12 (decode-side authority minting forbidden — frozen addendum).** The data codec — the decoder for messages, receipt results, plan literals, and mailbox/snapshot value payloads — MUST reject capability payloads on decode: discriminant `0x05` (`TAG_CAPABILITY`) and standalone `0x30` (`CapRef::TYPE_TAG`) MUST yield `CanonicalError::CapabilityInData`, not a `Value::Capability`. Only the kernel-mediated codec path — persistence of kernel authority state and kernel-sealed delegation envelopes (R-MARSHAL-05) — may produce or consume capability payloads. `unmarshal` MUST run `contains_capability` (R-MARSHAL-06) over the decoded value regardless of provenance, making the marshalling boundary symmetric with `marshal`. Property: for all bytes `b`, `contains_capability(unmarshal_data(b)) = false ∨ unmarshal_data(b) = Err`. Resolves C-14/U-02 in the direction of the design rule (a serialized capability must go through explicit delegation); negative golden vectors (capability bytes, nested-at-depth, standalone envelope) are normative fixtures. *(Frozen addendum — post-audit remediation SEC-003; additive per R-SCOPE-03; extends R-CANON-11/R-MARSHAL-03; resolves C-78; no source transcription.)*

<!-- FINAL1: R-CANON-12 canonical home; cleaned authority spec/01 S-17; registry row final/03; status SPECIFIED -->

**R-CANON-13 (one canonical grammar — frozen addendum).** Exactly ONE canonical byte grammar is frozen: Phase 15A — universal envelope `version u8 / type_tag u8 / payload_length u32 BE`, length prefixes `u32 BE`, `CapRef [index u32 BE][generation u32 BE]`. The revised-grammar Little-Endian sections are SUPERSEDED in-source (quoted, not deleted); field names are the 15A names (`payload_length`); the `TAG_*` constants denote ONE namespace (the 15A tags; the revised-grammar tag set is superseded) — resolving term/ X-50/X-54. All integrity predicates (`EffectDigest`, `StateDigest`, `ResultDigest`, WAL checksum inputs) are defined over 15A bytes alone; cross-implementation digest equality is meaningful by construction (R-CANON-01: canonical encoding defines semantic identity). Golden vectors are asserted byte-exact bidirectionally for production, reference, and the persistence payload writer; LE-encoded variants of every golden vector MUST be rejected by all three. *(Frozen addendum — post-audit remediation SEC-017; additive per R-SCOPE-03; extends R-CANON-01/R-CANON-11/R-PERSIST-01; resolves C-92; mutation M031; no source transcription.)*

<!-- FINAL1: R-CANON-13 canonical home; cleaned authority spec/01 S-17; registry row final/03; status SPECIFIED -->


---

## §14 Persistence

The persistence protocol (Phase 15B): the non-semantic-machine rule, two-level framing, the record taxonomy, snapshot content and atomic commit, sequence continuity, and the frozen authority-lattice (R-PERSIST-07) and rewinding-resistance (R-PERSIST-08) obligations. The open encoding gap for machine state (U-02) is *not* closed here; it is listed in §29 and carried in `final/09`.

**Canonical homes transcribed in this section (8):** `R-PERSIST-01`, `R-PERSIST-02`, `R-PERSIST-03`, `R-PERSIST-04`, `R-PERSIST-05`, `R-PERSIST-06`, `R-PERSIST-07`, `R-PERSIST-08`.

**R-PERSIST-01 (separation).** The persistence layer is not a semantic machine; it records and reconstructs the existing machine. **No secondary serialization:** the payload of every persistence record is strictly the byte output of Phase 15A `CanonicalEncode`.

<!-- FINAL1: R-PERSIST-01 canonical home; cleaned authority spec/01 S-18; registry row final/03; status SPECIFIED -->

**R-PERSIST-02 (two-level framing).** WAL append operations MUST write `WalFrame` records with incrementing `WalSequence` counters. Sequence gaps MUST NOT be permitted. *(L33802–33830; L35088–35110.)*

<!-- FINAL1: R-PERSIST-02 canonical home; cleaned authority spec/01 S-18; registry row final/03; status SPECIFIED -->

**R-PERSIST-03 (record taxonomy).** `WalRecord ::= Event(EventEnvelope) | EffectPrepared { id, actor, digest } | EffectIssued { id, actor, digest } | EffectCompleted { id, digest, result_digest } | EffectReconciled { id, digest, outcome } | SnapshotCommit { event_sequence, snapshot_version, state_digest }`. `EventEnvelope { sequence: EventSequence, logical_time: LogicalTime, event: GlobalEvent }` with `e_i.sequence < e_{i+1}.sequence` (total ordering).

<!-- FINAL1: R-PERSIST-03 canonical home; cleaned authority spec/01 S-18; registry row final/03; status SPECIFIED -->

**R-PERSIST-04 (snapshot content).** Global snapshots MUST capture complete machine state necessary for resumption: logical_time, ID counters, runnable queue, actor states, capability arena, budget state, effect journal cursor. Snapshots MUST be canonical 15A encoded. *(L26293–26330.)*

<!-- FINAL1: R-PERSIST-04 canonical home; cleaned authority spec/01 S-18; registry row final/03; status SPECIFIED -->

**R-PERSIST-05 (atomic snapshot protocol).** Snapshot creation MUST follow atomic protocol: (1) write `SnapshotBegin` marker; (2) write canonical `GlobalSnapshot` payload; (3) fsync payload; (4) write `SnapshotCommit` record with `state_digest`. Incomplete snapshots MUST be discarded during recovery. *(L26216–26240; L35177–35188.)*

<!-- FINAL1: R-PERSIST-05 canonical home; cleaned authority spec/01 S-18; registry row final/03; status SPECIFIED -->

**R-PERSIST-06 (sequence continuity).** WAL sequence continuity MUST hold (`s_{n+1} = s_n + 1`); gaps MUST be rejected (obligation tag `WAL-GAP-REJECT` / `WAL-SEQUENCE-CONTINUITY`). *(L35088–35110; L35189–35208.)*

<!-- FINAL1: R-PERSIST-06 canonical home; cleaned authority spec/01 S-18; registry row final/03; status SPECIFIED -->

**R-PERSIST-07 (durable authority lattice — frozen addendum).** The kernel authority image — `AuthorityNode` set with parent links, the `revocation_set`, and generation counters — MUST be durable: snapshots MUST contain it (the invariant is frozen here; byte encoding remains U-02 scope), and the WAL MUST carry `CapabilityGranted`, `CapabilityDerived`, and `CapabilityRevoked` event kinds (freezing the event set in the security direction). Recovery MUST reconstruct the kernel arena, replay capability events after the snapshot sequence, and reject with `RecoveryFault` — never silently repair (R-RECOV-05, R-CORE-10) — any CapRef (in contexts, heaps, frames, mailboxes) that does not resolve with matching generation. Post-recovery, every actor capability MUST be revalidated: `∀ a, ∀ c ∈ caps(a): Valid(c, t_recovered)`; revocation MUST be monotonic across crashes — a revoked capability MUST NOT become valid again without a new explicit grant. `Recover(D) ≡ PreCrashMachineState` includes the authority lattice. *(Frozen addendum — post-audit remediation SEC-004; additive per R-SCOPE-03; extends R-PERSIST-04/R-CAP-07/R-CORE-09; tag `RECOVERY-REVOCATION-DURABLE`; no source transcription.)*

<!-- FINAL1: R-PERSIST-07 canonical home; cleaned authority spec/01 S-18; registry row final/03; status SPECIFIED -->

**R-PERSIST-08 (storage integrity rewinding-resistance — frozen addendum).** Persistence integrity MUST gain rewinding resistance: WAL checksums MUST be chained (`checksum_n = H(checksum_{n−1} ‖ frame_n)`) so rewrite or truncation of any prefix breaks every later frame; the snapshot commit record MUST cover the state digest and the last WAL sequence. If the storage medium is adversarial, the chain MUST be keyed (MAC or signature over the sequence-linked chain; key-epoch mismatch ⇒ `RecoveryFault`); if the storage medium is trusted-writable, that assumption MUST be recorded in the trust table as such — keyless chaining detects corruption and rewinding but does not authenticate, and the accepted risk is documented explicitly. Consistently forged records (recomputed checksums, contiguous sequences, balanced budget) are the mandatory negative test class. `Durable(D) ⇒ Authentic(D)` where keyed; the effect evidence chain (`Prepared → Issued → Completed → Reconciled`) must be unforgeable, not merely well-ordered. *(Frozen addendum — post-audit remediation SEC-009; additive per R-SCOPE-03; extends R-PERSIST-02/R-PERSIST-05; resolves C-88; no source transcription.)*

<!-- FINAL1: R-PERSIST-08 canonical home; cleaned authority spec/01 S-18; registry row final/03; status SPECIFIED -->


---

## §15 Crash Recovery

Crash recovery: durable-state definition, the T0–T6 matrix, the 12-step recovery algorithm, independent recovery, strict validation (no silent repair), the budget recovery invariant, reconciliation, the frozen reconciliation protocol (R-RECOV-08) and reconstruction authority (R-RECOV-09). The irreducibility of `Indeterminate` and the `Indeterminate ≠ NotExecuted` law (N-24) bind every clause of this section.

**Canonical homes transcribed in this section (9):** `R-RECOV-01`, `R-RECOV-02`, `R-RECOV-03`, `R-RECOV-04`, `R-RECOV-05`, `R-RECOV-06`, `R-RECOV-07`, `R-RECOV-08`, `R-RECOV-09`.

**R-RECOV-01 (durable state).** Durable state `D = ⟨S, L, H⟩` MUST consist of latest committed snapshot S, durable event log L, and durable effect journal H. Recovery MUST satisfy `Recover(D) = Replay(S, L, H)`. *(L26122–26140.)*

<!-- FINAL1: R-RECOV-01 canonical home; cleaned authority spec/01 S-19; registry row final/03; status SPECIFIED -->

**R-RECOV-02 (normative crash matrix T0–T6).** The crash recovery matrix MUST adhere strictly to T0–T6 classifications:

| Crash point | Durable state | Required recovery result |
|---|---|---|
| T0: before `Prepared` | none | Effect does not exist; no budget mutation; resume normal small-step CEK machine execution without host reconciliation |
| T1: after `Prepared` | `Prepared` only | Discard incomplete preparation; resume normal small-step CEK machine execution without host reconciliation |
| T2: after `Issued` | `Issued` | Reconstruct effect state as `Indeterminate`; await host reconciliation |
| T3: after HostInvocation | `Issued` | Reconstruct effect state as `Indeterminate`; await host reconciliation |
| T4: after HostCompletion | `Issued` | Reconstruct effect state as `Indeterminate`; await host reconciliation |
| T5: after `Completed` | `Completed` | Effect complete; state durable; resume execution |
| T6: after `SnapshotCommit` | `SnapshotCommit` | Clean state; resume execution |

*(L35159–35176 (frozen); L28467–28493 (same matrix, restated); L38831–38846.)*

<!-- FINAL1: R-RECOV-02 canonical home; cleaned authority spec/01 S-19; registry row final/03; status SPECIFIED -->

**R-RECOV-03 (recovery algorithm).** Recovery MUST execute the 12-step algorithm: (1) locate newest committed snapshot; (2) verify framing/checksum; (3) decode via 15A `CanonicalDecode`; (4) validate recovered `GlobalState` invariants (budget conservation, no duplicate runnable actors); (5) open WAL, verify framing/checksums; (6) verify sequence continuity, reject gaps; (7) replay records sequentially after snapshot sequence; (8) reconstruct effect journal, validate causal chains; (9) classify interrupted effects (`Indeterminate` vs `Completed`); (10) reconstruct runnable queue; (11) compute final state digest vs trailing checkpoint; (12) enter `RecoveryComplete`, resume deterministic scheduler. [INFORMATIVE: "deterministic" is explicitly defined in S-15 / R-ACTOR-07]. *(L35189–35208; L26272–26300.)*

<!-- FINAL1: R-RECOV-03 canonical home; cleaned authority spec/01 S-19; registry row final/03; status SPECIFIED -->

**R-RECOV-04 (independent recovery).** The recovery engine MUST be an **independent implementation** from the normal execution path (anti-oracle-collapse). Production recovery MUST NOT be used as the reference recovery oracle. *(L35189–35195; L38858–38890.)*

<!-- FINAL1: R-RECOV-04 canonical home; cleaned authority spec/01 S-19; registry row final/03; status SPECIFIED -->

**R-RECOV-05 (strict validation rule).** `Invalid(D) ⇒ RecoveryFault`. The recovery engine MUST NEVER silently repair corruption (the recovery engine MUST NOT drop duplicate runnable actors, MUST NOT adjust budget mismatches, and MUST NOT ignore gaps, checksums, or causality violations). *(L35196–35208; L38254–38272.)*

<!-- FINAL1: R-RECOV-05 canonical home; cleaned authority spec/01 S-19; registry row final/03; status SPECIFIED -->

**R-RECOV-06 (budget recovery invariant).** The three-way budget accounting `C_available + C_escrowed + C_consumed = C_initial` MUST survive crashes identically without discrepancy. *(L35210–35215.)*

<!-- FINAL1: R-RECOV-06 canonical home; cleaned authority spec/01 S-19; registry row final/03; status SPECIFIED -->

**R-RECOV-07 (reconciliation).** `Issued ∧ ¬Completed` effects MUST be handed to the supervisor's reconciliation policy; `Reconciled(E) ⇒ Issued(E)` MUST hold; outcomes MUST be recorded durably (`EffectReconciled`). Reconciliation MUST be the only path by which an `Indeterminate` effect becomes resolved; the system MUST NOT auto-resolve to "not executed". *(L35111–35144; L26249–26262.)*

<!-- FINAL1: R-RECOV-07 canonical home; cleaned authority spec/01 S-19; registry row final/03; status SPECIFIED -->

**R-RECOV-08 (reconciliation protocol — frozen addendum).** Reconciliation is frozen: I2 (the 7-conjunct chain) holds for EVERY host invocation path including supervisor/reconciliation ones — `Reconcile(E) ⇒ Issued(E) ∧ outcome ∈ AdmissibleOutcomes(class(E))`, with per-effect-class admissible outcome variants (closing U-06/U-15 in the security direction). Reconciliation NEVER re-executes an effect: an idempotent host query at most; any compensating or retry action is itself an ordinary `Request` through gates 1–16. `NotExecuted` as a durable resolution is gated behind authoritative host-reconciliation evidence — no component, trusted or not, may resolve `Indeterminate → NotExecuted` on local policy (R-DUR-04); `Completed(EffectReceipt)` inherits the R-EFFECT-08 result-admission rule and R-HOST-06 result-digest verification. The Supervisor allocates lifecycle decisions, not effects: `Supervisor.host` is reachable only through the issuance boundary. Escrow moves only per the frozen admissibility table. *(Frozen addendum — post-audit remediation SEC-010; additive per R-SCOPE-03; extends R-DUR-04/R-DUR-05/R-RECOV-07; resolves C-89; mutation M028; no source transcription.)*

<!-- FINAL1: R-RECOV-08 canonical home; cleaned authority spec/01 S-19; registry row final/03; status SPECIFIED -->

**R-RECOV-09 (recovery reconstruction authority — frozen addendum).** Recovery MUST reconstruct `next_effect_id = max({id ∈ replayed EffectIssued}) + 1`; a snapshot counter less than the journal maximum is stale and MUST be advanced (recorded, never silently repaired). A snapshot counter GREATER than the journal maximum is a `RecoveryFault`. No `SnapshotCommit` MAY exist with its last-effect sequence inside an issuance section (steps 12–14b) — the recovery of such a snapshot, if ever found, is a `RecoveryFault`, and the snapshot-taker MUST serialize against the section (C-107). The completion order is frozen: `append(EffectCompleted)`, then `sync()`, then the charge/release accounting, then the continuation resume (R-EFFECT-07) — a crash after the host returns but before that fsync is T4 (`Indeterminate`), and byte-exact resumption (T5) requires the fsync to precede the resume (C-109). *(Frozen addendum VII — request-pipeline remediation, owner decision 2026-09-03; additive per R-SCOPE-03; extends R-PERSIST-04/05/06, R-RECOV-02/03/07, R-EFFECT-07; resolves C-107/C-109, decision U-43; no source transcription.)*

---

<!-- FINAL1: R-RECOV-09 canonical home; cleaned authority spec/01 S-19; registry row final/03; status SPECIFIED -->


---

## §16 Agent/LLM Loop

The agent/LLM loop: proposal as data, the planner's absolute incapacities, causal binding by exact-epoch staleness (R-PLANNER-06), planner determinism is *not required* of the model but *is* required of the machine through recorded proposals (R-PLANNER-04), the outer-loop conformance obligations, and the capability-opaque observation channel (R-PLANNER-07). LLM non-authority is a negative guarantee and is stated at full strength (GI-SEC-12).

**Canonical homes transcribed in this section (7):** `R-PLANNER-01`, `R-PLANNER-02`, `R-PLANNER-03`, `R-PLANNER-04`, `R-PLANNER-05`, `R-PLANNER-06`, `R-PLANNER-07`.

**R-PLANNER-01 (proposal data).** The planner MUST return proposals as `PlanProposal { observation_sequence: EventSequence, block: Block, planner_metadata }`. LLM output MUST be treated as data (`LLMOutput ∈ Data`) and MUST NOT confer authority. *(L27176–27198.)*

<!-- FINAL1: R-PLANNER-01 canonical home; cleaned authority spec/01 S-05; registry row final/03; status SPECIFIED -->

**R-PLANNER-02 (cannot).** The model MUST NOT: allocate capabilities; authorize effects; modify budgets; modify the event log; allocate actors directly; invoke the host; bypass validation; alter scheduler state. It MAY only propose a `Block`, which enters the ordinary compiler pipeline. *(L27271–27285; L37781–37790.)*

<!-- FINAL1: R-PLANNER-02 canonical home; cleaned authority spec/01 S-05; registry row final/03; status SPECIFIED -->

**R-PLANNER-03 (staleness).** A proposal MUST be causally bound to the machine state from which it was generated. The machine MUST verify `proposal.observation_sequence = current_planning_epoch` and MUST otherwise reject it as `StalePlan` — a normal machine-visible outcome without state mutation. *(L27199–27236; L28373.)*

<!-- FINAL1: R-PLANNER-03 canonical home; cleaned authority spec/01 S-05; registry row final/03; status SPECIFIED -->

**R-PLANNER-04 (planner determinism).** The LLM MAY be non-deterministic. The machine MUST satisfy the determinism theorem: `InitialState + Plan + SchedulerTrace + HostTrace ⇒ UniqueMachineTrace`. For exact end-to-end replay, the machine MUST record a `PlannerAccepted { observation_sequence, proposal_digest, block }` record, and replay MUST consume the recorded proposal without querying the LLM. [INFORMATIVE: "deterministic" is explicitly defined by this state-transition theorem]. *(L27392–27414.)*

<!-- FINAL1: R-PLANNER-04 canonical home; cleaned authority spec/01 S-05; registry row final/03; status SPECIFIED -->

**R-PLANNER-05 (LLM outer-loop conformance, normative test obligation).** The conformance suite MUST include: (1) untrusted-input rejection — raw/malformed/malicious `Block` data fed directly to the runtime MUST be rejected at the compiler boundary; (2) stale-proposal rejection — advanced machine state + old proposal MUST yield rejection without state mutation; (3) end-to-end replay — live session vs replay with recorded proposal + `ReplayHost` MUST yield byte-for-byte identical final `GlobalState` and `EventLog`. *(L27920–27931; L28513–28521.)*

<!-- FINAL1: R-PLANNER-05 canonical home; cleaned authority spec/01 S-05; registry row final/03; status SPECIFIED -->

**R-PLANNER-06 (staleness is exact equality — frozen addendum).** `AcceptProposal(p) ⇔ p.observation_sequence = current_planning_epoch` — EXACT EQUALITY. A proposal whose `observation_sequence` differs from the current planning epoch in EITHER direction MUST be rejected with `Fault::StalePlan` and zero state mutation; the strictly-less-only reading (reject only when `< current`, thereby accepting future-tagged proposals) is SUPERSEDED (quoted, not deleted). The epoch check is the exact planner-boundary check: a proposal is causally bound to the machine state it was generated from, in both directions. Future-epoch proposals are a mandatory rejection test (`obs_seq ∈ {current−1, current, current+1, current+10⁹}`: accept only `current`, zero state mutation on both rejections). C-38's canonical description is corrected hereby: the two phrasings define different acceptance sets, not one check stated twice. *(Frozen addendum — post-audit remediation SEC-007; additive per R-SCOPE-03; extends R-PLANNER-03/R-PLANNER-05; resolves C-86; mutation M026; no source transcription.)*

<!-- FINAL1: R-PLANNER-06 canonical home; cleaned authority spec/01 S-05; registry row final/03; status SPECIFIED -->

**R-PLANNER-07 (observation channel is capability-opaque — frozen addendum).** The untrusted observation channel MUST be capability-opaque by construction: `Observation` carries capability *summaries* — counts, operation classes, ceilings — NEVER references; `CapabilitySummary` is frozen as a non-referential projection (defining the phantom); `Capability ∉ Observables(LLM)` is the dual of `LLMOutput ∈ Data`. The `EffectIssued` log/event shape carries `{id, actor, digest}` ONLY — the `EffectRequest`-with-`cap` shape in the log is SUPERSEDED (quoted, not deleted; the v0.3 rule-5 shape governs), and the `EffectRequest.cap` shape conflict is registered. Events visible to the planner are filtered/redacted by a frozen observation projection rule. Property: for every machine state and observation emission, `contains_capability(Observation) = false` (recursive, events included); no `0x30`/`0x05` payloads appear in planner-facing canonical encodings. *(Frozen addendum — post-audit remediation SEC-008; additive per R-SCOPE-03; extends R-PLANNER-01/R-KERN-01; resolves C-87; mutation M027; no source transcription.)*

<!-- FINAL1: R-PLANNER-07 canonical home; cleaned authority spec/01 S-05; registry row final/03; status SPECIFIED -->


---

## §17 Independent Reference Model

The independent reference model as an architectural contract. No reference implementation exists in this repository; nothing here manufactures one. The independence boundary, scope, non-goals, and the differential purpose are the contract text. Identity separation is normative: production `Value`/`CapRef`/`ActorId`/`EffectId` (defined in §04/§13) are *not* the reference-model `RefValue`/`RefCapId`/`RefActorId`/`RefEffectId` (15C.4, L35471–35473; no conversion is permitted inside reference semantics — harness-boundary mapping only, 15C.21). The independence audit's verdict `REF1-CONDITIONAL` is the current verification state of this contract (see `final/08`); it MUST NOT be represented as `REF1-PASS`.

**Canonical homes transcribed in this section (4):** `R-REF-01`, `R-REF-02`, `R-REF-03`, `R-REF-04`.

**R-REF-01 (purpose).** An independently implemented executable reference model MUST provide machine-checked evidence that the production implementation conforms to specified semantics: `Observe(Production(X)) = Observe(Reference(X))` MUST hold for every generated input `X` in the comparison domain; for persistence: `Canonical(Recover_P(D)) = Canonical(Recover_R(D))` MUST hold, subject to frozen reconciliation rules. This MUST be treated as differential verification evidence, not a formal proof. *(L35281–35310; L38935–38953.)*

<!-- FINAL1: R-REF-01 canonical home; cleaned authority spec/01 S-20; registry row final/03; status SPECIFIED -->

**R-REF-02 (independence boundary).** The reference model MUST NOT call: `ProductionEvaluator, ProductionContinuation, ProductionCapabilityKernel, ProductionBudget, ProductionScheduler, ProductionSerializer, ProductionRecovery, ProductionPersistence, ProductionReplayHost, ProductionTransition`. It MAY consume test inputs/fixtures and emit reference observations/traces. Shared transition implementations MUST NOT be used; shared semantic test fixtures MAY be used. *(L35330–35375; L37696–37721; L28590+ (key rule).)*

<!-- FINAL1: R-REF-02 canonical home; cleaned authority spec/01 S-20; registry row final/03; status SPECIFIED -->

**R-REF-03 (reference model scope).** The reference implementation MUST independently model: CEK evaluation, lexical environments, closures, calls, capability derivation, revocation, budgets, actors, scheduling, effects, persistence, and recovery. It MUST be intentionally small, direct, explicit, deterministic, independently structured, and slow where clarity demands. Performance MUST be explicitly secondary to transparency. [INFORMATIVE: "deterministic" is explicitly defined in S-02 / R-CORE-08]. *(L41848–41866; L35281–35310; L35313–35322; L35341.)*

<!-- FINAL1: R-REF-03 canonical home; cleaned authority spec/01 S-20; registry row final/03; status SPECIFIED -->

**R-REF-04 (non-goals).** The reference model MUST NOT redefine semantics, MUST NOT introduce a second serialization format, MUST NOT reproduce host implementation details, MUST NOT claim to prove correctness mathematically, MUST NOT share production transition code, and MUST NOT optimize. *(L35326–35339.)*

<!-- FINAL1: R-REF-04 canonical home; cleaned authority spec/01 S-20; registry row final/03; status SPECIFIED -->


---

## §18 Differential Testing

Differential verification: normalized observations (R-REF-05), the harness boundary enforcement (R-REF-06), obligation-tagged semantic coverage (R-TEST-07), the crash-injection matrix (R-TEST-08), divergence adjudication (R-TEST-09), CI gates (R-TEST-10), final acceptance (R-TEST-11), and the request-frame tags (R-TEST-12). All of these are verification *contracts*. None has repository evidence: the comparison domain types (`Observed*`) remain undeclared (recorded, F-04/UNKNOWN), and coverage metrics never substitute for the differential oracle.

**Canonical homes transcribed in this section (8):** `R-REF-05`, `R-REF-06`, `R-TEST-07`, `R-TEST-08`, `R-TEST-09`, `R-TEST-10`, `R-TEST-11`, `R-TEST-12`.

**R-REF-05 (normalized observation).** Differential comparison MUST use normalized observations, not internal structure: terminal states, event trace, effect trace, resource partitions, authority outcomes, scheduler trace, faults, recovered state. Internal details (addresses, pointers, allocator behavior, Rust enum layout, OS handles, host object identity) MUST be excluded unless explicitly semantic. The comparator MUST report the **first divergence**. Comparing only final return values MUST NOT be permitted. *(L38420–38470 (§16); L38935; L41869–41906.)*

<!-- FINAL1: R-REF-05 canonical home; cleaned authority spec/01 S-20; registry row final/03; status SPECIFIED -->

**R-REF-06 (harness enforcement).** The harness MUST include mocked boundary enforcement: a `PanicHost` that panics if `execute()` is called before all gates pass; a `MockKernel` asserting exactly one `authorize`/`derive` call with the exact expected parameters. The production/reference boundary MUST be treated as a first-class test subject. *(L27891–27902.)*

<!-- FINAL1: R-REF-06 canonical home; cleaned authority spec/01 S-20; registry row final/03; status SPECIFIED -->

**R-TEST-07 (semantic coverage, obligation-tagged).** Coverage MUST be tracked per stable verification-obligation tag (e.g., `CEK-CALL-ARITY-PRECHECK, CEK-CALL-ARGS-LTR, CEK-CLOSURE-LEXICAL-CAPTURE, CAP-DERIVE-NO-AMPLIFICATION, CAP-REVOCATION-ANCESTOR, BUDGET-CONSUMPTION-CONSERVATION, BUDGET-ESCROW-CONSERVATION, EFFECT-ISSUE-DURABLE-BEFORE-HOST, EFFECT-RECEIPT-DIGEST-VALIDATION, SCHED-FIFO, SCHED-BLOCKED-NOT-SCHEDULED, MARSHAL-NO-RAW-CAPABILITY, WAL-SEQUENCE-CONTINUITY, RECOVERY-ISSUED-INDETERMINATE, SNAPSHOT-COMMIT-INTEGRITY`). Coverage metrics MUST be treated as evidence and MUST NOT serve as a substitute for the differential oracle. *(L38523–38560; L37402–37414.)*

<!-- FINAL1: R-TEST-07 canonical home; cleaned authority spec/01 S-21; registry row final/03; status SPECIFIED -->

**R-TEST-08 (crash-injection matrix).** The crash harness MUST exercise all T0–T6 crash points and MUST verify the exact expected classification, especially `Issued ∧ ¬Completed ⇒ Indeterminate` and `Prepared ∧ ¬Issued ⇒ Discard`. *(L38831–38846; L35216–35236 (crash harness).)*

<!-- FINAL1: R-TEST-08 canonical home; cleaned authority spec/01 S-21; registry row final/03; status SPECIFIED -->

**R-TEST-09 (fault adjudication).** Every production/reference divergence MUST be classified as one of: production defect | reference defect | harness defect | specification ambiguity. Testers MUST NEVER patch the oracle merely to make a test pass. Specification ambiguity MUST require an explicit specification decision before implementation proceeds. *(L38848–38862; L37404–37414.)*

<!-- FINAL1: R-TEST-09 canonical home; cleaned authority spec/01 S-21; registry row final/03; status SPECIFIED -->

**R-TEST-10 (CI gates, frozen).** The CI pipeline MUST enforce frozen gates:
- **Pull request:** format, lint, unit tests, exhaustive small-state, core differential tests, serialization conformance.
- **Nightly:** property generation, mutation registry, full differential suite, persistence fuzzing, crash injection, semantic coverage report.
- **Release candidate:** all nightly suites, stress tests, full crash matrix, `MutationKillRate = 100%`, determinism checks, recovery differential tests, security regression suite.
No release MUST be accepted with an unexplained differential mismatch or surviving non-equivalent mutation. [INFORMATIVE: "determinism" is explicitly defined in S-02 / R-CORE-08]. *(L38864–38890; L37287–37292.)*

<!-- FINAL1: R-TEST-10 canonical home; cleaned authority spec/01 S-21; registry row final/03; status SPECIFIED -->

**R-TEST-11 (final acceptance condition).** The implementation MUST be conformant only when `Observe_P(X) = Observe_R(X)` over the tested state space **and** `MutationKillRate = 100%` for all non-equivalent registered mutations **and** `Canonical(Recover_P(D)) = Canonical(Recover_R(D))` over the tested persistence state space (subject to authoritative external-effect reconciliation). 'Code compiles', 'unit tests pass', and 'coverage is high' MUST NOT be treated as completion. *(L38885–38911; L41196–41210.)*

<!-- FINAL1: R-TEST-11 canonical home; cleaned authority spec/01 S-21; registry row final/03; status SPECIFIED -->

**R-TEST-12 (request-frame verification tags — frozen addendum).** The R-TEST-07 obligation-tagged coverage list MUST additionally include `REQUEST-ARGS-LTR` (request arguments evaluated strictly left-to-right, exactly one per CEK step; step 3 of the frozen sequence, R-EFFECT-01) and `REQUEST-NON-CAP-SHORT-CIRCUIT` (a non-capability capability expression faults before any target/parameter evaluation and before any step 4–16 runs, with no `EffectId`, budget or log mutation and no host invocation; R-EFFECT-04). Both tags MUST be covered by the request-path Track A suite, registered in `spec/08`, and tracked in `mod/05`/`mod/08`. Coverage of these tags MUST NOT substitute for the differential oracle (R-TEST-07). *(Frozen addendum VII — request-pipeline remediation, owner decision 2026-09-03; additive per R-SCOPE-03; extends R-TEST-07; resolves decision U-44; no source transcription.)*

---

<!-- FINAL1: R-TEST-12 canonical home; cleaned authority spec/01 S-21; registry row final/03; status SPECIFIED -->


---

## §19 Mutation Testing

The mutation-testing regime: the frozen baseline registry M001–M018 plus the additive post-audit mutants (registry currently defined through M042), the 100 % kill-rate gate for non-equivalent mutants, and mutation-validation-of-the-verifier. The registry is a *specification artifact* in this repository: mutants are defined; none has been executed (no kill-rate may be claimed, R-TEST-05/06 remain SPECIFIED).

**Canonical homes transcribed in this section (3):** `R-TEST-04`, `R-TEST-05`, `R-TEST-06`.

**R-TEST-04 (mutation registry, baseline frozen).** The versioned baseline mutation registry MUST include:
`M001` reverse argument evaluation; `M002` skip arity precheck; `M003` allow non-function application; `M004` accept revoked capability; `M005` omit capability ceiling; `M006` permit capability amplification; `M007` omit budget gate; `M008` release indeterminate escrow; `M009` permit negative resources; `M010` allocate EffectId before authorization; `M011` schedule blocked actor; `M012` duplicate runnable queue entry; `M013` break mailbox FIFO; `M014` accept duplicate canonical map key; `M015` ignore WAL sequence gap; `M016` ignore checksum mismatch; `M017` accept mismatched EffectDigest; `M018` resume after corrupted receipt.
The registry MUST be additive: a previously killed mutant MUST remain a regression requirement. *(L38473–38492; L37239–37249 (categorization).)*

<!-- FINAL1: R-TEST-04 canonical home; cleaned authority spec/01 S-21; registry row final/03; status SPECIFIED -->

**R-TEST-05 (kill rate).** The target MUST be `MutationKillRate = 100%` for all registered **non-equivalent** mutations. Any surviving non-equivalent mutant MUST block verification. Equivalent mutants MUST require explicit adjudication and documentation. Mutation survivors MUST be treated as release-blocking defects. *(L38494–38500; L37390–37400.)*

<!-- FINAL1: R-TEST-05 canonical home; cleaned authority spec/01 S-21; registry row final/03; status SPECIFIED -->

**R-TEST-06 (mutation validation).** The verification system itself MUST be tested: for each mutation — inject, build, run targeted test, run differential suite, assert mutant killed. Testers MUST NOT merely run the framework without asserting mutant kills. *(L38515–38540.)*

<!-- FINAL1: R-TEST-06 canonical home; cleaned authority spec/01 S-21; registry row final/03; status SPECIFIED -->


---

## §20 Exhaustive Testing

The exhaustive small-state baseline (bounded enumeration at every commit; the CI time target is a performance budget, never a semantic constraint — coverage MUST NOT be reduced to meet it). R-TEST-01 canonically defines all three execution-mode baselines including the stress floors cited by §22.

**Canonical homes transcribed in this section (1):** `R-TEST-01`.

**R-TEST-01 (execution modes, frozen baselines).** The test suite MUST support three execution modes:
- **Exhaustive (small-state):** enumeration over bounded state; baseline `expression depth ≤ 4, actors ≤ 2, capabilities ≤ 2`; MUST run on every commit. The CI time target MUST be treated as a performance budget, **not** a semantic constraint; if state space grows, the runner MUST partition, shard, or cache — and MUST NOT reduce semantic coverage to preserve a time target.
- **Property-generated:** randomized layered generation (structure → type validity → capabilities → budgets → actor topology → effects → persistence corruption), aggressive shrinking; MUST run nightly.
- **Stress:** `50k–100k` call depth, `100+` actors, long mailboxes, large WAL traces, repeated crash/recovery, large continuation states; MUST run weekly and on release candidates.
*(L38587–38715; L37251–37268 (pre-correction `<2 min` wording superseded — `C-11`).)*

<!-- FINAL1: R-TEST-01 canonical home; cleaned authority spec/01 S-21; registry row final/03; status SPECIFIED -->


---

## §21 Property Testing

The property-testing regime: layered randomized generation with reproducible counterexample artifacts and the ten-step shrinking order. R-TEST-02/03 are homed here as the property-suite mechanics; the mode baselines are §20's canonical text.

**Canonical homes transcribed in this section (2):** `R-TEST-02`, `R-TEST-03`.

**R-TEST-02 (reproducible counterexamples).** Every generated test case MUST be reproducible. Every failure MUST save the structured artifact: `seed, generator_version, semantic_version, test_case_version, program, initial state, capabilities, budgets, actor topology, scheduler_trace, host_trace, persistence image, crash_trace, production_observation, reference_observation, first_divergence, minimized case`. The artifact MUST be runnable locally. *(L38891–38920; L37293–37315; L38587–38624.)*

<!-- FINAL1: R-TEST-02 canonical home; cleaned authority spec/01 S-21; registry row final/03; status SPECIFIED -->

**R-TEST-03 (shrinking protocol).** Shrinking order MUST proceed as: (1) actor count, (2) expression depth, (3) call arity, (4) bindings, (5) mailbox messages, (6) capability scope, (7) budget dimensions, (8) WAL records, (9) effect count, (10) crash position. The shrinker MUST preserve the failure predicate; every failure MUST yield a minimal reproducible artifact. *(L38441–38463.)*

<!-- FINAL1: R-TEST-03 canonical home; cleaned authority spec/01 S-21; registry row final/03; status SPECIFIED -->


---

## §22 Stress Testing

Stress testing. The canonical requirements (depth 50k–100k, 100+ actors, long mailboxes, large WAL traces, repeated crash/recovery, large continuation states) are defined once, inside R-TEST-01's **Stress** baseline (§20); this section is the regime index required by the FINAL1 canonical order and deliberately contains no restatement — the definitions above are single-homed and referenced by ID.


---

## §23 Security Invariants

Global security invariants — the canonical consolidation of the machine's invariant layer. Each `GI-SEC-nn` row below is a *registry* entry: the normative statement lives in its defining requirement (single home); this table supplies the stable ID other sections reference, and `final/05` supplies variables, domains, quantifiers, and state/transition context. No invariant is redefined here; no negative guarantee is weakened.


**Global security invariants (registry: `final/05` — definitional homes hold the normative text; the full formal metadata — variables, domains, quantifiers, state/transition context — is registered there):**

| Invariant ID | Name | Canonical definition (single home) | Referenced from |
|---|---|---|---|
| `GI-SEC-01` | No authority crosses to effect | `R-CORE-01` (§02) | `R-CORE-02`, `R-TRUST-01`, `R-TRUST-02`, `R-PLANNER-02`, `R-CLAIM-01` |
| `GI-SEC-02` | External-effect chain (7 conjuncts) | `R-CORE-02` (§02) | `R-CORE-11`, `R-EFFECT-01`, `R-EFFECT-03`, `R-CORE-14`, `R-DUR-02`, `R-TEST-09` |
| `GI-SEC-03` | No unauthorized effects | `R-CORE-03` (§02) | `R-CAP-06`, `R-EFFECT-02` |
| `GI-SEC-04` | No authority amplification | `R-CAP-05` (§06) | `R-CORE-04`, `R-ACTOR-09`, `R-CAP-03` |
| `GI-SEC-05` | Revocation lineage | `R-CAP-07` (§06) | `R-PERSIST-07`, `R-CAP-09`, `R-KERN-02` |
| `GI-SEC-06` | Budget conservation (no teleportation) | `R-BUDGET-05` (§07) | `R-CORE-05`, `R-ACTOR-08`, `R-BUDGET-11`, `R-RECOV-06` |
| `GI-SEC-07` | Durable-before-host | `R-DUR-01` (§11) | `R-CORE-06`, `R-DUR-02`, `R-DUR-06`, `R-DUR-07`, `R-CORE-14` |
| `GI-SEC-08` | No raw capability transfer | `R-MARSHAL-01` (§13) | `R-CORE-07`, `R-MARSHAL-02`, `R-MARSHAL-04`, `R-MARSHAL-05`, `R-MARSHAL-06`, `R-CANON-12` |
| `GI-SEC-09` | Receipt causality | `R-EFFECT-06` (§11) | `R-EFFECT-07`, `R-EFFECT-08`, `R-HOST-03`, `R-HOST-06`, `R-HOST-04` |
| `GI-SEC-10` | Gate short-circuit atomicity | `R-EFFECT-04` (§11) | `R-CORE-12`, `R-CORE-14`, `R-BUDGET-10`, `R-DUR-07` |
| `GI-SEC-11` | Planner observation opacity | `R-PLANNER-07` (§16) | `R-KERN-03`, `R-MARSHAL-06`, `R-PLANNER-01` |
| `GI-SEC-12` | LLM non-authority | `R-PLANNER-02` (§16) | `R-TRUST-01`, `R-TRUST-02`, `R-PLANNER-01`, `R-KERN-06`, `R-ARCH-01` |
| `GI-SEC-13` | Proposal staleness is exact-equality causal binding | `R-PLANNER-06` (§16) | `R-PLANNER-03`, `R-PLANNER-05`, `R-CORE-12` |
| `GI-SEC-14` | Fault totality and transition atomicity | `R-CORE-12` (§02) | `R-EFFECT-04`, `R-BUDGET-02`, `R-REPO-03`, `audit/_conservation_checker.py` |
| `GI-SEC-15` | Closed declared fault surface | `R-CORE-13` (§02) | `R-CALC-06`, `R-EFFECT-08`, `R-REF-05`, `R-DUR-07` |
| `GI-SEC-16` | Kernel possession gate | `R-KERN-04` (§06) | `R-KERN-01`, `R-KERN-02`, `R-KERN-03`, `R-KERN-05`, `R-KERN-06`, `R-CAP-06` |
| `GI-SEC-17` | Spawn transfers no authority by default | `R-ACTOR-09` (§09) | `R-ACTOR-05`, `R-COMPILE-06`, `R-MARSHAL-05`, `R-CORE-04` |
| `GI-SEC-18` | Trust table completeness and structural carriability | `R-TRUST-04` (§03) | `R-TRUST-01`, `R-TRUST-05`, `R-REPO-02`, `R-REPO-03`, `R-ARCH-05` |
| `GI-SEC-19` | Reference-model independence | `R-SCOPE-04` (§01) | `R-REF-02`, `R-REF-04`, `R-RECOV-04`, `R-ARCH-02` |
| `GI-SEC-20` | Actor isolation | `R-ACTOR-01` (§09) | `R-ACTOR-02`, `R-ACTOR-10`, `R-CALC-02` |
| `GI-SEC-21` | No unconstrained embedded capability literals | `R-COMPILE-06` (§05) | `R-COMPILE-02`, `R-COMPILE-03`, `R-CAP-10`, `U-22` |
| `GI-SEC-22` | Rewinding-resistant persistence | `R-PERSIST-08` (§14) | `R-PERSIST-02`, `R-PERSIST-05`, `R-CORE-13` |

Invariant *statements* live only in their defining requirements above; this table and `final/05` are registry/index material referencing them by stable ID (no restatement, no weakening of negative guarantees).


---

## §24 Determinism Invariants

Global determinism invariants, consolidated under stable `GI-DET-nn` IDs with `final/05` as their formal registry. The determinism theorem carries its recorded limitation (U-35: unfalsifiable as stated) verbatim; the δ_t/duration laws are the addendum-IX frozen forms.


**Global determinism invariants (registry: `final/05` — definitional homes hold the normative text; the full formal metadata — variables, domains, quantifiers, state/transition context — is registered there):**

| Invariant ID | Name | Canonical definition (single home) | Referenced from |
|---|---|---|---|
| `GI-DET-01` | Determinism theorem | `R-CORE-08` (§02) | `R-ACTOR-07`, `R-TEST-10`, `N-32` |
| `GI-DET-02` | Deterministic identity allocation | `R-ACTOR-03` (§09) | `R-EFFECT-03`, `R-CALC-03` |
| `GI-DET-03` | FIFO scheduler, at-most-once runnable | `R-ACTOR-04` (§10) | `R-ACTOR-06`, `R-ACTOR-07`, `SCHED-FIFO`, `SCHED-BLOCKED-NOT-SCHEDULED` |
| `GI-DET-04` | Logical time only | `R-CAP-09` (§06) | `R-BUDGET-06`, `R-CAP-11`, `R-BUDGET-15`, `R-BUDGET-16`, `N-18`, `N-33` |
| `GI-DET-05` | One δ_t, one duration debit; quiescence rule | `R-BUDGET-16` (§07) | `R-BUDGET-06`, `R-BUDGET-15`, `R-BUDGET-09`, `R-RECOV-08`, `R-CAP-09` |
| `GI-DET-06` | One canonical encoding grammar | `R-CANON-13` (§13) | `R-CANON-01`, `R-CANON-02`, `R-CANON-09`, `R-CANON-10`, `R-PERSIST-01` |
| `GI-DET-07` | Replay correspondence | `R-HOST-04` (§12) | `R-HOST-03`, `R-HOST-05`, `R-PLANNER-04`, `R-EFFECT-06`, `R-HOST-06` |

Invariant *statements* live only in their defining requirements above; this table and `final/05` are registry/index material referencing them by stable ID (no restatement, no weakening of negative guarantees).


---

## §25 Recovery Invariants

Global recovery and persistence invariants, consolidated under stable `GI-REC-nn` IDs with `final/05` as their formal registry. The crash classification lattice and the no-silent-repair rule are referenced here, defined in §14/§15. `Indeterminate` is irreducible: no row below, and no document, may represent it as resolvable by local policy.


**Global recovery/persistence invariants (registry: `final/05` — definitional homes hold the normative text; the full formal metadata — variables, domains, quantifiers, state/transition context — is registered there):**

| Invariant ID | Name | Canonical definition (single home) | Referenced from |
|---|---|---|---|
| `GI-REC-01` | Effect journal causality | `R-DUR-03` (§11) | `R-DUR-04`, `R-RECOV-02`, `N-05`, `N-24`, `audit/_crash_consistency_checker.py` |
| `GI-REC-02` | Crash recovery equivalence (qualified) | `R-CORE-09` (§02) | `R-RECOV-01`, `R-RECOV-02`, `R-RECOV-03`, `R-RECOV-08`, `R-REF-01` |
| `GI-REC-03` | No silent repair | `R-RECOV-05` (§15) | `R-CORE-10`, `R-PERSIST-06`, `R-PERSIST-08`, `R-RECOV-09` |
| `GI-REC-04` | Escrow survives crash; disposition total | `R-DUR-05` (§11) | `R-BUDGET-09`, `R-BUDGET-11`, `R-DUR-06`, `R-BUDGET-16`, `R-RECOV-08` |
| `GI-REC-05` | Budget and counter restoration | `R-RECOV-06` (§15) | `R-RECOV-09`, `R-BUDGET-05`, `R-RECOV-03` |
| `GI-REC-06` | Indeterminate irreducibility | `R-RECOV-08` (§15) | `R-DUR-04`, `R-RECOV-07`, `R-CORE-09`, `N-24`, `R-CLAIM-02` |
| `GI-REC-07` | Sequence continuity and snapshot atomicity | `R-PERSIST-06` (§14) | `R-PERSIST-01`, `R-PERSIST-02`, `R-PERSIST-05`, `R-DUR-07` |

Invariant *statements* live only in their defining requirements above; this table and `final/05` are registry/index material referencing them by stable ID (no restatement, no weakening of negative guarantees).


---

## §26 Requirement Registry


**Canonical requirement registry (184 stable IDs; identical table body as `final/03`, which adds the registry governance rules):**

| R-ID | Obligation (short) | Provenance | Status | Impl→ | Verify→ | Home § | Cleaned § |
|---|---|---|---|---|---|---|---|
| R-SCOPE-01 | Thesis: deterministic, capability-scoped, resource-bounded, crash-recoverable machine | L41293–41300 | SPECIFIED | — | — | §01 | S-01 |
| R-SCOPE-02 | Architecture/spec/verification FROZEN; frozen ≠ verified | L38929–38942, L41297–41315 | SPECIFIED | — | — | §01 | S-01 |
| R-SCOPE-03 | STOP-and-report on ambiguity; no silent semantic modification | L37664–37686 | SPECIFIED | all | R-TEST-09 | §01 | S-01 |
| R-SCOPE-04 | Zero shared core logic production/reference | L37696–37721 | SPECIFIED | ror-reference, ror-differential | R-REF-02, dependency-graph review | §01 | S-01 |
| R-CORE-01 | LLMOutput ∧ UntrustedInput ↛ ExternalEffect | L41320–41335, L27505–27513 | SPECIFIED | all | R-PLANNER-05, mutation M004–M008 | §02 | S-02 |
| R-CORE-02 | ExternalEffect chain (7 conjuncts) | L41337–41351, L27491–27509 | SPECIFIED | all | R-TEST-07 tags | §02 | S-02 |
| R-CORE-03 | ¬Authorized ⇒ ¬ExternalEffect | L42056–42064, L7413–7419 | SPECIFIED | ror-kernel, ror-runtime | M004, M005 | §02 | S-02 |
| R-CORE-04 | derive(A,C) ≼ A (no amplification) | L42066–42072, L6399–6406 | SPECIFIED | ror-kernel | CAP-DERIVE-NO-AMPLIFICATION, M006 | §02 | S-02 |
| R-CORE-05 | Budget partition conservation (no teleportation) | L42074–42080, L28203–28240 | SPECIFIED | ror-core, ror-runtime | BUDGET-CONSUMPTION-CONSERVATION, BUDGET-ESCROW-CONSERVATION, M007, M009 | §02 | S-02 |
| R-CORE-06 | HostInvoked ⇒ DurableIssued | L42082–42088, L35150–35156 | SPECIFIED | ror-runtime, ror-persistence, ror-host | EFFECT-ISSUE-DURABLE-BEFORE-HOST | §02 | S-02 |
| R-CORE-07 | Ordinary marshal rejects raw capabilities | L42090–42098, L25972–26001 | SPECIFIED | ror-runtime | MARSHAL-NO-RAW-CAPABILITY (source tag MARSHAL-CAPABILITY-REJECT), M006-class | §02 | S-02 |
| R-CORE-08 | Determinism: state+traces ⇒ unique machine trace | L41623–41646, L27518–27547 | SPECIFIED | ror-runtime | SCHED-FIFO, R-REF-05 | §02 | S-02 |
| R-CORE-09 | Causal crash recovery (qualified theorem) | L27551–27569, L35159–35176 | SPECIFIED | ror-persistence | R-RECOV-02 T0–T6 | §02 | S-02 |
| R-CORE-10 | No silent recovery corruption | L42100–42105, L35196–35208 | SPECIFIED | ror-persistence | M015, M016, negative recovery tests | §02 | S-02 |
| R-CORE-11 | One canonical signature per I2 predicate: ValidatedRequest(E) request-time subsuming ValidatedPlan(plan(E)); Authorized(holder, c, E, t) possession conjunct (formalizes R-KERN-04); ValidatedPlan_pred vs ValidatedPlan_struct; chain stated once (X-01/X-04/X-05; C-80 resolved) | addendum (SEC-016) | SPECIFIED | ror-kernel, ror-runtime | R-TEST-09 differential adjudication | §02 | S-02 |
| R-CORE-12 | Fault totality on machine paths: panic-free non-test code, failures map to declared Fault (InternalInvariant family); transition atomicity — complete or fault, no died-mid-transition; durable append precedes in-memory mutation; clippy unwrap/expect denial (C-83 resolved; M034) | addendum (SEC-020) | SPECIFIED | all machine crates | M034, panic-catching fuzz harness | §02 | S-02 |
| R-CORE-13 | Closed declared fault surface on every trust-boundary crossing: six replay-path variants, StalePlan, unified MarshalFault, InternalInvariant declared; no debug-formatted external error text in machine values; resume-vs-fault pinned per variant (C-91 resolved) | addendum (SEC-012) | SPECIFIED | all machine crates | fault-coverage lint, differential fault matrix | §02 | S-02 |
| R-CORE-14 | Canonical request protocol and transaction boundary: master-prompt 16-step order governs, turn-[21] host-before-Issued order superseded; step-10 premise `t + δ_t(req) ≤ W`; steps 12–14b one atomic section (C-103/C-104 resolved) | addendum (request-pipeline) | SPECIFIED | ror-runtime | M037/M038, gate short-circuit matrix | §02 | S-02 |
| R-TRUST-01 | Trust table (LLM/Block No; host Partial; rest Yes) | L41823–41841, L27611–27624 | SPECIFIED | — | — | §03 | S-03 |
| R-TRUST-02 | TCB composition; LLM output ∉ TCB authority | L28178–28230 | SPECIFIED | — | — | §03 | S-03 |
| R-TRUST-03 | No hidden authority; evaluator sees refs only | L37722–37748, L19153–19175 | SPECIFIED | ror-kernel, ror-runtime | Track B (mock kernel), visibility checks | §03 | S-03 |
| R-TRUST-04 | One complete trust table: MOD-06/08/10 rows frozen (authoritative machine boundary); 11-row table superseded; planner never a security/runtime provider — prohibitions homed at enforcing modules; dep/ SC-1/2/3 hard failures (C-84 resolved) | addendum (SEC-022) | SPECIFIED | — | dep/ regeneration with SC-1/2/3 hard-gated | §03 | S-03 |
| R-TRUST-05 | Crate DAG carries the R-DUR-02 hinge edge ror-runtime → ror-persistence (inverted trait superseded); ror-core → ror-kernel forbidden; forbidden-edge list checked against Cargo.toml; crate-separation rule (C-85 resolved) | addendum (SEC-022) | SPECIFIED | ror-runtime, ror-persistence | Cargo.toml DAG mechanical check | §03 | S-03 |
| R-ARCH-01 | End-to-end pipeline (16 stages, LLM→host) | L37750–37780, L27287–27310 | SPECIFIED | ror-agent, ror-compiler, ror-runtime | — | §02 | S-04 |
| R-ARCH-02 | Independent verification architecture | L41406–41424 | SPECIFIED | ror-differential | R-REF-01 | §02 | S-04 |
| R-ARCH-03 | Block has no path into step(); plan constructors private | L9086–9097, L39296–39318 | SPECIFIED | ror-compiler, ror-runtime | R-ORDER-03 (first security gate) | §02 | S-04 |
| R-ARCH-04 | Dependency direction (algebra→kernel→plan→actor→global→scheduler→host) | L9059–9085 | SPECIFIED | all | Cargo dependency review | §02 | S-04 |
| R-ARCH-05 | Isolation posture decided: ladder retired — in-process structural isolation is the frozen minimum with residual risk (host compromise = machine compromise) recorded; out-of-process host adapter (canonical-bytes effects/receipts) required where host not fully trusted; in-process executor testkit-only (C-93 resolved) | addendum (SEC-013) | SPECIFIED | ror-host | dependency/visibility hard gate; dual-host-mode differential | §02 | S-04 |
| R-PLANNER-01 | PlanProposal {observation_sequence, block, metadata}; LLMOutput ∈ Data | L27176–27198 | SPECIFIED | ror-agent | — | §16 | S-05 |
| R-PLANNER-02 | Planner cannot allocate/authorize/modify/invoke/bypass | L27271–27285, L37781–37790 | SPECIFIED | ror-agent | R-PLANNER-05(1) | §16 | S-05 |
| R-PLANNER-03 | Staleness check; StalePlan rejection, no state mutation | L27199–27236, L28373 | SPECIFIED | ror-agent, ror-runtime | R-PLANNER-05(2) | §16 | S-05 |
| R-PLANNER-04 | Planner need not be deterministic; PlannerAccepted recording for replay | L27392–27414 | SPECIFIED | ror-agent | R-PLANNER-05(3) | §16 | S-05 |
| R-PLANNER-05 | LLM outer-loop conformance (3 test obligations) | L27920–27931, L28513–28521 | SPECIFIED | ror-agent, ror-testkit | 15E suite | §16 | S-05 |
| R-PLANNER-06 | Staleness is exact equality: observation_sequence = current_planning_epoch; either-direction mismatch ⇒ StalePlan with zero state mutation; less-than-only reading superseded; future-tagged proposals mandatory rejection test (C-86 resolved; M026) | addendum (SEC-007) | SPECIFIED | ror-agent, ror-runtime | M026, epoch-boundary conformance | §16 | S-05 |
| R-PLANNER-07 | Observation channel capability-opaque: CapabilitySummary frozen as non-referential projection (counts, classes, ceilings); EffectIssued carries {id, actor, digest} only, cap-bearing log shape superseded; Capability ∉ Observables(LLM) (C-87 resolved; M027) | addendum (SEC-008) | SPECIFIED | ror-agent | M027, observation-opacity property | §16 | S-05 |
| R-COMPILE-01 | Block ≠ ExecutablePlan | L41440–41452, L3834–3838 | SPECIFIED | ror-compiler | R-ORDER-03 | §05 | S-06 |
| R-COMPILE-02 | Pipeline stages; any failure ⇒ fault, no bypass | L39253–39267 | SPECIFIED | ror-compiler | malformed-Block rejection | §05 | S-06 |
| R-COMPILE-03 | Combined static judgment (type, effects, capability req, budget bound) | L3874–3905 | SPECIFIED | ror-compiler | U-22 (J2 re-spec gap) | §05 | S-06 |
| R-COMPILE-04 | Plan immutability / temporal integrity | L1722–1745, L2052–2070 | SPECIFIED | ror-compiler | — | §05 | S-06 |
| R-COMPILE-05 | ExecutablePlan constructors private to compiler | L39296–39318 | SPECIFIED | ror-compiler | visibility review | §05 | S-06 |
| R-COMPILE-06 | Embedded Value::Capability literals must be plan-bound: foreign/garbage/undeclared capability literal is a compilation fault (U-22 security-direction closure) | addendum (SEC-002) | SPECIFIED | ror-compiler | compiler conformance: embedded-literal battery | §05 | S-06 |
| R-CALC-01 | Machine Value domain (11 variants); Capability is opaque data | L12290–12312 | SPECIFIED | ror-core | — | §04 | S-07 |
| R-CALC-02 | Frozen Expr AST (12 constructors, declarative only) | L12132–12170 | SPECIFIED | ror-core | — | §04 | S-07 |
| R-CALC-03 | Symbol(u32) runtime identity; compiler maps names | L12250–12270 | SPECIFIED | ror-core, ror-compiler | — | §04 | S-07 |
| R-CALC-04 | Effect = immutable data; EffectDigest = SHA-256(canonical); ID vs digest roles | L9288–9348, L23726–23772 | SPECIFIED | ror-core | EFFECT-RECEIPT-DIGEST-VALIDATION | §04 | S-07 |
| R-CALC-05 | EffectCost {issue, complete_max, reserve} | L25799–25825 | SPECIFIED | ror-core | R-EFFECT-05 | §04 | S-07 |
| R-CALC-06 | Frozen Fault taxonomy | L23784–23819, L27236 | SPECIFIED | ror-core | fault-coverage metric | §04 | S-07 |
| R-CALC-07 | Effect replayability/reversibility/idempotence (properties; table illustrative) | L2141–2156, L3858–3873, L26669–26735 | SPECIFIED | ror-core | U-06 | §04 | S-07 |
| R-CALC-08 | Σ and G configurations; global vs local state split | L7119–7144, L8653–8682, L24148–24163 | SPECIFIED | ror-core, ror-runtime | — | §04 | S-07 |
| R-CEK-01 | Explicit CEK; no recursive evaluation | L41484–41499, L37800–37812 | SPECIFIED | ror-runtime | deep-call stress, R-TEST-01 | §08 | S-08 |
| R-CEK-02 | Value-return invariant (terminal iff continuation empty) | L16878–16905, L37826–37838 | SPECIFIED | ror-runtime, ror-reference | push/pop structural invariants (L14632) | §08 | S-08 |
| R-CEK-03 | Frozen frame set; closure env ≠ caller env | L16928–16958, L23821–23856 | SPECIFIED | ror-runtime | CEK-CLOSURE-LEXICAL-CAPTURE | §08 | S-08 |
| R-CEK-04 | Lambda: lexical capture, pure, value-return path | L16971–16995 | SPECIFIED | ror-runtime | CEK-CLOSURE-LEXICAL-CAPTURE | §08 | S-08 |
| R-CEK-05 | Call: LTR evaluation; arity precheck before args; closure-env application | L16878–16905, L37840–37862 | SPECIFIED | ror-runtime | CEK-CALL-ARITY-PRECHECK, CEK-CALL-ARGS-LTR, M001, M002, M003 | §08 | S-08 |
| R-CEK-06 | Continuation preservation (+1/−1 per entry/resume) | L14632–14642 | SPECIFIED | ror-runtime | structural invariant tests | §08 | S-08 |
| R-CEK-07 | Progress & preservation | L7273–7277, L8850 | SPECIFIED | ror-runtime | differential equivalence | §08 | S-08 |
| R-CAP-01 | Five semantic domains (O, S, Q, R, T) with orders/meets | L6354–6379 | SPECIFIED | ror-core, ror-kernel | algebra property tests | §06 | S-09 |
| R-CAP-02 | Operation-indexed authority | L6370–6380 | SPECIFIED | ror-kernel | cross-op contamination tests | §06 | S-09 |
| R-CAP-03 | Authority partial order ≼ | L6381–6390 | SPECIFIED | ror-kernel | monotonicity property | §06 | S-09 |
| R-CAP-04 | Constraint ≠ Authority (narrowing request) | L6391–6396, L6406 | SPECIFIED | ror-core, ror-kernel | — | §06 | S-09 |
| R-CAP-05 | derive = per-op meet; derive(A,C) ≼ A | L6397–6404 | SPECIFIED | ror-kernel | CAP-DERIVE-NO-AMPLIFICATION, M006 | §06 | S-09 |
| R-CAP-06 | Canonical Authorized(A,E,t) predicate (5 conjuncts) | L6406–6421, L6647–6656 | SPECIFIED | ror-kernel | Track B mock-kernel tests | §06 | S-09 |
| R-CAP-07 | Valid(c,t) incl. ancestor liveness; lazy revocation | L6434–6445, L6647–6656 | SPECIFIED | ror-kernel | CAP-REVOCATION-ANCESTOR, M004 | §06 | S-09 |
| R-CAP-08 | Algebra theorems 1–3 (stated, proof-sketch only) | L6422–6433, L6657–6671 | SPECIFIED | ror-kernel | property tests (NOT PROVEN) | §06 | S-09 |
| R-CAP-09 | Explicit logical time; no wall-clock | L6434–6436, L38858–38890 | SPECIFIED | ror-core, ror-runtime | determinism tests | §06 | S-09 |
| R-CAP-10 | AdmissibleConstraint defined: decidable well-formedness per semantic domain (O/S/Q/R/T); inadmissible constraint faults (InvalidConstraint), never identity/top-default; compile-time validation of attacker-authored constraints (C-94 resolved; M030) | addendum (SEC-014) | SPECIFIED | ror-kernel, ror-compiler | M030, compiler negative suite | §06 | S-09 |
| R-CAP-11 | Lifetime is logical time: half-open `[start, end)` validity, call sites pass logical time, five Unix annotations superseded-quoted; `max_duration` declared-info only; `Deadline` stays `Option<LogicalTime>` (C-100 resolved; U-36) | addendum (duration-semantics) | SPECIFIED | ror-core, ror-kernel | M4 expiration/authorization gate tests | §06 | S-09 |
| R-KERN-01 | CapRef opaque, generation-safe, private fields, kernel-only construction | L9127–9133, L10178–10208 | SPECIFIED | ror-core, ror-kernel | visibility review | §06 | S-10 |
| R-KERN-02 | Kernel API: authorize/derive/validate with logical time | L6672–6728, L19153–19175 | SPECIFIED | ror-kernel | exactly-one-call mock tests | §06 | S-10 |
| R-KERN-03 | Authority internals pub(crate)/inaccessible | L39397–39407 | SPECIFIED | ror-kernel | visibility + mutation M005-class | §06 | S-10 |
| R-KERN-04 | Possession-gated authorization: authorize(holder, cap, effect, t) resolves the CapRef through the actor capability context; global-arena no-holder authorize superseded; CapRef bits never suffice (C-77 resolved) | addendum (SEC-002) | SPECIFIED | ror-kernel | M021, brute-force CapRef exhaustion from a non-holder | §06 | S-10 |
| R-KERN-05 | CapabilityContext real frozen possession type; unit-type sketch superseded; snapshots carry capability context; recovery reconstructs possession before gate authorization | addendum (SEC-002) | SPECIFIED | ror-kernel, ror-persistence | snapshot/recovery round-trip of possession sets | §06 | S-10 |
| R-KERN-06 | Root-grant protocol frozen: Grant(source, authority, ceiling, t) with durable CapabilityGranted record, authority ≼ deployment ceiling, root minted once at initialization; Supervisor.host removed or issued-effect-only (R-HOST-02 binds all callers); planner I/O crate-separated (C-95 resolved) | addendum (SEC-015) | SPECIFIED | ror-kernel, ror-agent | PanicHost-wraps-all-handles conformance; grant audit test | §06 | S-10 |
| R-BUDGET-01 | B = ⟨C=⟨F,I,D⟩, R=⟨M,S⟩, W⟩ semantics | L8683–8700, L9161–9175 | SPECIFIED | ror-core | U-01 (D semantics) | §07 | S-11 |
| R-BUDGET-02 | Checked arithmetic; no saturating_sub | L9207–9245, L38044–38046 | SPECIFIED | ror-core | M007, M009 | §07 | S-11 |
| R-BUDGET-03 | ReserveOK / ReleaseOK predicates | L7487–7520, L8692–8696 | SPECIFIED | ror-core | reservation property tests | §07 | S-11 |
| R-BUDGET-04 | WithinBudget dual gate (runtime + capability ceiling) | L8692–8696 | SPECIFIED | ror-runtime, ror-kernel | short-circuit Track C | §07 | S-11 |
| R-BUDGET-05 | Conservation (consumables, reserved, deadline, global partition) | L7408–7425, L28203–28240, L35210–35215 | SPECIFIED | ror-core, ror-runtime | BUDGET-*-CONSERVATION tags, teleportation test | §07 | S-11 |
| R-BUDGET-06 | Time advancement δ_t (pure=0, host/scheduler>0, t+δ_t ≤ W) | L8698–8700, L10164–10168 | SPECIFIED | ror-runtime | U-07 | §07 | S-11 |
| R-BUDGET-07 | CostModel contract; Consumable ≠ Reserved typing | L9155–9205, L10171–10177 | SPECIFIED | ror-core | — | §07 | S-11 |
| R-BUDGET-08 | ¬BudgetOK ⇒ fault(BudgetExhausted), no partial debit | L7345–7352, L7410–7419 | SPECIFIED | ror-runtime | Track C budget-gate test | §07 | S-11 |
| R-BUDGET-09 | Escrow disposition totality: every escrowed unit leaves via exactly one frozen path (Completed / host-failure consumption / durable Reconciled); live faults unified with crash reconciliation; logical-time deadline bound to Indeterminate; no quiescent strand (C-97 resolved; M035) | addendum (SEC-021) | SPECIFIED | ror-runtime, ror-persistence | M035, ledger liveness, mixed crash+live harness | §07 | S-11 |
| R-BUDGET-10 | Resource-state atomicity: every Op transition is one transactional resource mutation; precondition failure ⇒ `Σ' = Σ` (zero drift, zero partial debit); post-issuance host-failure caveat (C-108 resolved; U-45) | addendum (resource-accounting) | SPECIFIED | ror-runtime, ror-persistence | Op-01…Op-22 atomicity harness (conservation checker) | §07 | S-11 |
| R-BUDGET-11 | Escrow disposition normal form (RECONCILED): R-BUDGET-09's three paths are the totality; Consumed/Refunded are its completion leaves, Transferred/Disposed-with-explicit-sink its reconciled leaves; `Remains-Indeterminate` is a bounded transient, never terminal (C-108 resolved; U-45) | addendum (resource-accounting) | SPECIFIED | ror-runtime (classification), ror-persistence (records) | M039, ledger liveness, T0–T6 | §07 | S-11 |
| R-BUDGET-13 | Persistent-capacity accounting: volatile RAM distinct from persistent storage; RAM released on scope exit/halt; durable storage retained and snapshot-compacted; overflow faults (C-108 resolved; U-45) | addendum (resource-accounting) | SPECIFIED | ror-persistence | M7 snapshot-capacity tests | §07 | S-11 |
| R-BUDGET-15 | Duration consumable semantics: per-actor D; `ΔD := δ_t` exactly once per time advance; no double charge (`cost_C(E)` duration declared/diagnostic only); `δ_t > D` ⇒ `DeadlineExceeded` zero-mutation; precedence `CapabilityViolation → BudgetExhausted → DeadlineExceeded → HostPolicyDenied` (C-114/C-115 resolved; U-01/U-07) | addendum (duration-semantics) | SPECIFIED | ror-core, ror-runtime | M042, budget-gate tests | §07 | S-11 |
| R-BUDGET-16 | Exhaustive δ_t table (pure 0; issuance +1; receipt +1; spawn/send/receive/blocked 0; turn carries the executed δ_t; per host round trip = 2; reconciliation 0); Pending W-eligibility on each advance; late receipts settle via R-RECOV-08 (`t+δ_t ≤ W` superseded-quoted); stable quiescence `Deadlock ∧ ∃Pending` ⇒ driver `QuiescenceReconcile` δ_t=0/ΔD=0, each pending → `Indeterminate` + R-RECOV-08 (C-112/C-113 resolved; U-01/U-07) | addendum (duration-semantics) | SPECIFIED | ror-runtime | M040, M041, QUIESCENCE-RECONCILES-PENDING, ledger liveness | §07 | S-11 |
| R-EFFECT-01 | Request = construct→authorize→account→log→Pending→yield | L12177–12194 | SPECIFIED | ror-runtime | — | §11 | S-12 |
| R-EFFECT-02 | Gated transition shape Pre∧BudgetOKAuthOK | L7145–7155, L8700–8710 | SPECIFIED | ror-runtime | — | §11 | S-12 |
| R-EFFECT-03 | Frozen 16-step request sequence | L37891–37908 | SPECIFIED | ror-runtime, ror-persistence | gate short-circuit matrix | §11 | S-12 |
| R-EFFECT-04 | Denial short-circuits all subsequent gates | L24003–24045 | SPECIFIED | ror-runtime | Track C (5 assertions per gate) | §11 | S-12 |
| R-EFFECT-05 | complete_max affordability at issuance | L25799–25825 | SPECIFIED | ror-runtime | budget escrow tests | §11 | S-12 |
| R-EFFECT-06 | Receipt validates ID + digest; mismatch ⇒ ReplayCorruption, no resume | L23949–24002, L25952–25970 | SPECIFIED | ror-runtime | EFFECT-RECEIPT-DIGEST-VALIDATION, M017, M018 | §11 | S-12 |
| R-EFFECT-07 | Completion accounting (charge complete, release reservation, log, resume) | L23949–24002 | SPECIFIED | ror-runtime | conservation tests | §11 | S-12 |
| R-EFFECT-08 | Receipt-result admission: recursive contains_capability over the result payload at any nesting depth; no capability, no closure; data-domain only; host error via declared closed fault mapping only | addendum (SEC-001) | SPECIFIED | ror-runtime | EFFECT-RECEIPT-RESULT-NO-AUTHORITY, M019, M020 | §11 | S-12 |
| R-DUR-01 | HostInvoked ⇒ DurableIssued | L35150–35156, L37910 | SPECIFIED | ror-runtime, ror-persistence | EFFECT-ISSUE-DURABLE-BEFORE-HOST | §11 | S-13 |
| R-DUR-02 | Issuance transaction order (7 steps, 2 fsyncs) | L35150–35158 | SPECIFIED | ror-persistence | crash harness T0–T4 | §11 | S-13 |
| R-DUR-03 | Causal effect protocol (Issued⇒Prepared; Completed⇒Issued; Reconciled⇒Issued; ID+digest identity) | L35111–35144, L37953–37965 | SPECIFIED | ror-persistence | journal validator, M017 | §11 | S-13 |
| R-DUR-04 | Prepared∧¬Issued⇒Discard; Issued∧¬Completed⇒Indeterminate (never NotExecuted) | L35159–35176, L37968–37981 | SPECIFIED | ror-persistence | RECOVERY-ISSUED-INDETERMINATE, crash harness | §11 | S-13 |
| R-DUR-05 | Escrow survives crash | L35210–35215 | SPECIFIED | ror-persistence | post-recovery invariant check, M008 | §11 | S-13 |
| R-DUR-06 | Durable issuance payload: `Prepared`/`Issued` carry `effect_bytes` + `EffectCost` triple; `{id, actor, digest}` superseded as persistence payload; digest re-verified at append/recovery (C-105 resolved) | addendum (request-pipeline) | SPECIFIED | ror-persistence | M038, T1/T2–T5 reconstruction harness | §11 | S-13 |
| R-DUR-07 | Live issuance failure: journal-driven commit; declared `Fault::PersistenceError`; append/sync error ⇒ pre-s12 state and R-EFFECT-04 five assertions; second-sync failure ⇒ `Prepared ∧ ¬Issued ⇒ Discard` (C-106 resolved) | addendum (request-pipeline) | SPECIFIED | ror-runtime, ror-persistence | M037, live-fault harness, T0–T1 | §11 | S-13 |
| R-HOST-01 | Host independently validates OS authority (defense in depth) | L8560–8580, L10168–10172 | SPECIFIED | ror-host | host policy tests | §12 | S-14 |
| R-HOST-02 | Host performs only issued effects; partially trusted | L41823–41841, L27644 | SPECIFIED | ror-host | PanicHost harness | §12 | S-14 |
| R-HOST-03 | Ordered ReplayHost; ID+digest per entry; no unordered map | L25972–25996, L37985–38000 | SPECIFIED | ror-host, ror-reference | replay property tests | §12 | S-14 |
| R-HOST-04 | Replay correspondence (machine replay valid; real-world replay per effect class) | L3947–3958, L26249–26262 | SPECIFIED | ror-host, ror-reference | R-REF-01 recovery equivalence | §12 | S-14 |
| R-HOST-05 | Replay validates trace, not just final state | L38278–38300 | SPECIFIED | ror-host | trace comparison | §12 | S-14 |
| R-HOST-06 | Durable receipt results representable: EffectCompleted {id, digest, result_digest, result: CanonicalData}; replay verifies ResultDigest(result) = result_digest before resumption — third identity conjunct; no ad-hoc result records (C-90 resolved; M029) | addendum (SEC-011) | SPECIFIED | ror-persistence, ror-runtime | M029, T5 byte-exact resumption | §12 | S-14 |
| R-ACTOR-01 | Actor isolation (heaps, envs, continuations, mailboxes, budgets, caps) | L41623–41641, L24268–24290 | SPECIFIED | ror-runtime | Track D, isolation properties | §09 | S-15 |
| R-ACTOR-02 | GlobalState shape; logical time global | L24148–24163, L25514–25546 | SPECIFIED | ror-runtime | — | §09 | S-15 |
| R-ACTOR-03 | Deterministic ID allocation; no address/PID/UUID/wall-clock identity | L24226–24245 | SPECIFIED | ror-runtime | determinism tests | §09 | S-15 |
| R-ACTOR-04 | FIFO scheduler; at-most-once membership; 1 transition/turn; blocked/pending/terminal never scheduled | L25558–25615, L37924–37937 | SPECIFIED | ror-runtime | SCHED-FIFO, SCHED-BLOCKED-NOT-SCHEDULED, M011, M012, M013, starvation test | §10 | S-15 |
| R-ACTOR-05 | Spawn: escrow + derived capabilities only; no wholesale clone | L25573–25615, L37941–37951 | SPECIFIED | ror-runtime, ror-kernel | Track D, amplification test, U-03 | §09 | S-15 |
| R-ACTOR-06 | Send async + deterministic wakeup; Receive blocks without fuel; FIFO mailbox | L25702–25749, L37941–37951 | SPECIFIED | ror-runtime | Track D, M013 | §09 | S-15 |
| R-ACTOR-07 | Deterministic concurrency theorem | L25759–25766 | SPECIFIED | ror-runtime | global differential (Track D) | §10 | S-15 |
| R-ACTOR-08 | No amplification / no teleportation theorems | L26048–26070 | SPECIFIED | ror-runtime | teleportation test, amplification test | §09 | S-15 |
| R-ACTOR-09 | Spawn transfers no capabilities by default (delegation is the only default path); explicit manifest + constraint compiler-checked, strictly attenuated; Authority(child) ≺ parent; trust_level phantom retracted; BudgetAllocationSpec bounds (C-82 resolved; M025) | addendum (SEC-006) | SPECIFIED | ror-runtime, ror-kernel | M025, spawn fan-out amplification tests | §09 | S-15 |
| R-ACTOR-10 | Mailbox resource admission: enqueue requires recipient capacity (M reservation; ReservedCapacityExceeded faults the sender, sender pays); payload-proportional send cost over canonical length; constructed value size bounded against constructor's M; footprint bounded by reserved M (C-96 resolved; M033) | addendum (SEC-019) | SPECIFIED | ror-runtime | M033, sender-flood stress, footprint-bounded property | §09 | S-15 |
| R-MARSHAL-01 | Recursive capability rejection in ordinary marshal | L41647–41658, L25674–25701, L37946–37951 | SPECIFIED | ror-runtime | MARSHAL-NO-RAW-CAPABILITY | §13 | S-16 |
| R-MARSHAL-02 | Explicit delegation only; DelegatedCapability envelope; ≼ parent | L25972–26001, L37953–37959 | SPECIFIED | ror-runtime, ror-kernel | Track C (delegation) | §13 | S-16 |
| R-MARSHAL-03 | MarshalledValue = canonical bytes; unmarshal(marshal(v)) = v | L25674–25701 | SPECIFIED | ror-runtime | Track B (marshalling) | §13 | S-16 |
| R-MARSHAL-04 | Semantic marshalling rule (CapRef ∉ marshal(v)) | L8695–8698 | SPECIFIED | ror-runtime | Track B | §13 | S-16 |
| R-MARSHAL-05 | Delegation constructible: Expr::Delegate calls kernel.derive and yields a kernel-constructed envelope, never a plain Value variant; receive-side revalidation (liveness, lineage, target, generation) before registration, faults leave the recipient CapabilityContext byte-identical; MarshalledValue is the checked-bytes form; MarshalFault unified (X-65; C-79 resolved) | addendum (SEC-005) | SPECIFIED | ror-runtime, ror-kernel | M024, delegation negative suite | §13 | S-16 |
| R-MARSHAL-06 | contains_capability is a frozen total predicate: closed traversal domain descending into List, Map, Tuple at any depth and FunctionValue.env recursively; sole exclusion kernel-sealed delegation envelopes; Bytes are data; marshal Ok implies no reachable capability (C-81 resolved) | addendum (SEC-018) | SPECIFIED | ror-runtime | M032, closure-smuggling corpus | §13 | S-16 |
| R-CANON-01 | Serialization independent of Rust layout/serializers | L28185–28228, L28453–28465 | SPECIFIED | ror-core | format review | §13 | S-17 |
| R-CANON-02 | Universal envelope (version/tag/len/payload) | L30532–30543, L33290–33347 | SPECIFIED | ror-core | golden vectors | §13 | S-17 |
| R-CANON-03 | Frozen standalone type tags (0x00, 0x20, 0x30, 0x40, 0x41) | L33087–33154 | SPECIFIED | ror-core | golden vectors; C-02 | §13 | S-17 |
| R-CANON-04 | Value discriminants + nested-complete-envelope rule | L30544–30552, L33155–33265 | SPECIFIED | ror-core | golden vectors, round-trip | §13 | S-17 |
| R-CANON-05 | Primitive payloads (Symbol/CapRef/ActorId/EffectId) | L33087–33154 | SPECIFIED | ror-core | golden vectors | §13 | S-17 |
| R-CANON-06 | Collections: count-prefixed; maps semantically ordered; duplicate keys rejected | L30566–30573, L34987–35024, L38164–38172 | SPECIFIED | ror-core | M014, duplicate-key regression (ROR-011) | §13 | S-17 |
| R-CANON-07 | Strict decoder contract (5 checks; explicit discriminants; CanonicalError set) | L30575–30586, L32948–33049 | SPECIFIED | ror-core | malformed-input suite (ROR-010) | §13 | S-17 |
| R-CANON-08 | Checked arithmetic; no attacker preallocation; bounded nested cursors; fallible envelope | L30574–30578, L32948–33265 | SPECIFIED | ror-core | hostile-input property tests | §13 | S-17 |
| R-CANON-09 | Digest rules + when-to-compare-bytes rule | L28185–28228, L30588–30590 | SPECIFIED | ror-core | digest property tests | §13 | S-17 |
| R-CANON-10 | Injectivity as structural property + scoped evidence claim | L30592–30598, L35068 | SPECIFIED | ror-core | round-trip + differential | §13 | S-17 |
| R-CANON-11 | Golden vectors as normative fixtures | L30599–30646, L31948–32010, L33266–33286 | SPECIFIED | ror-core (vectors/) | M1 acceptance | §13 | S-17 |
| R-CANON-12 | Data decoder rejects capability payloads: 0x05 and standalone 0x30 yield CanonicalError::CapabilityInData; only the kernel-mediated codec path produces or consumes capability payloads; unmarshal runs contains_capability — symmetric boundary (C-14/U-02 security direction; C-78 resolved) | addendum (SEC-003) | SPECIFIED | ror-core | M022, negative golden vectors | §13 | S-17 |
| R-CANON-13 | One canonical grammar: 15A BE envelope sole; LE revised grammar superseded in-source; single TAG_* namespace (X-50/X-54 resolved); all digests defined over 15A; bidirectional byte-exact golden vectors; LE variants rejected (C-92 resolved; M031) | addendum (SEC-017) | SPECIFIED | ror-core | M031, bidirectional golden vectors | §13 | S-17 |
| R-PERSIST-01 | Persistence = recording, not a semantic machine; no secondary serialization | L33757–33790, L35078–35087 | SPECIFIED | ror-persistence | dependency review (15B acceptance matrix) | §14 | S-18 |
| R-PERSIST-02 | Two-level framing; WalFrame checksum; 8 rejection classes | L33802–33830, L35088–35110 | SPECIFIED | ror-persistence | negative parsing tests, M016 | §14 | S-18 |
| R-PERSIST-03 | Record taxonomy; EventEnvelope monotonic sequence | L33861–33900, L35111–35144 | SPECIFIED | ror-persistence | sequence property | §14 | S-18 |
| R-PERSIST-04 | Snapshot content (include/exclude lists) | L26293–26330 | SPECIFIED | ror-persistence | snapshot review, U-02 | §14 | S-18 |
| R-PERSIST-05 | Atomic snapshot protocol; ValidSnapshot iff commit+digest | L26216–26240, L35177–35188 | SPECIFIED | ror-persistence | SNAPSHOT-COMMIT-INTEGRITY, crash harness T6 | §14 | S-18 |
| R-PERSIST-06 | WAL sequence continuity; gaps rejected | L35088–35110, L35189–35208 | SPECIFIED | ror-persistence | WAL-SEQUENCE-CONTINUITY, WAL-GAP-REJECT, M015 | §14 | S-18 |
| R-PERSIST-07 | Durable authority lattice: snapshot carries the AuthorityNode set, revocation_set and generation counters; WAL event kinds CapabilityGranted/Derived/Revoked; recovery reconstructs the arena, replays capability events, faults on dangling or generation-mismatched CapRef; revocation monotonic across crashes (RECOVERY-REVOCATION-DURABLE) | addendum (SEC-004) | SPECIFIED | ror-persistence, ror-kernel | RECOVERY-REVOCATION-DURABLE, M023, crash matrix T0–T6 with pre-crash revocation | §14 | S-18 |
| R-PERSIST-08 | Storage integrity rewinding resistance: chained checksums (checksum_n = H(checksum_{n−1} ‖ frame_n)); snapshot commit covers state digest + last WAL sequence; keyed chain if storage adversarial, else trust-table records the trusted-writable assumption; consistently-forged negative tests (C-88 resolved) | addendum (SEC-009) | SPECIFIED | ror-persistence | tamper-at-every-T matrix, forged-record negatives | §14 | S-18 |
| R-RECOV-01 | D = ⟨S,L,H⟩; Recover = Replay | L26122–26140 | SPECIFIED | ror-persistence | recovery differential | §15 | S-19 |
| R-RECOV-02 | Normative crash matrix T0–T6 | L35159–35176, L28467–28493 | SPECIFIED | ror-persistence | crash harness, M10 | §15 | S-19 |
| R-RECOV-03 | Recovery algorithm (12 steps) | L35189–35208, L26272–26300 | SPECIFIED | ror-persistence | recovery differential (R-REF-01) | §15 | S-19 |
| R-RECOV-04 | Independent recovery implementation | L35189–35195, L38858–38890 | SPECIFIED | ror-persistence, ror-reference | dependency review | §15 | S-19 |
| R-RECOV-05 | Invalid(D) ⇒ RecoveryFault; never silently repair | L35196–35208, L38254–38272 | SPECIFIED | ror-persistence | negative corruption tests | §15 | S-19 |
| R-RECOV-06 | Budget partition invariant survives crash | L35210–35215 | SPECIFIED | ror-persistence | post-recovery invariant | §15 | S-19 |
| R-RECOV-07 | Reconciliation is the only resolution path for Indeterminate | L35111–35144, L26249–26262 | SPECIFIED | ror-persistence, ror-host | U-15, reconciliation tests | §15 | S-19 |
| R-RECOV-08 | Reconciliation frozen: I2 holds on every host path incl. supervisor; never re-executes (idempotent query at most); compensations are ordinary gated requests; NotExecuted gated behind authoritative evidence; supervisor allocates lifecycle, not effects (C-89 resolved; M028) | addendum (SEC-010) | SPECIFIED | ror-agent (policy), ror-persistence (record contract) | M028, T2/T3/T4 admissibility table | §15 | S-19 |
| R-RECOV-09 | Recovery reconstruction authority: `next_effect_id` from max replayed `Issued`; no `SnapshotCommit` in s12–s14b (`RecoveryFault`); completion order append→sync→charge→resume (C-107/C-109 resolved) | addendum (request-pipeline) | SPECIFIED | ror-persistence, ror-reference | M10, crash matrix T4/T5, snapshot-cadence tests | §15 | S-19 |
| R-REF-01 | Observe_P = Observe_R (+ recovery equivalence); evidence, not proof | L35281–35310, L38935–38953 | SPECIFIED | ror-differential | the gate itself | §17 | S-20 |
| R-REF-02 | Independence boundary (10 forbidden production deps) | L35330–35375, L37696–37721 | SPECIFIED | ror-reference | dependency graph review | §17 | S-20 |
| R-REF-03 | Reference models all 12 semantic areas; clarity over speed | L41848–41866, L35281–35322, L35341 | SPECIFIED | ror-reference | — | §17 | S-20 |
| R-REF-04 | Reference non-goals | L35326–35339 | SPECIFIED | ror-reference | — | §17 | S-20 |
| R-REF-05 | Normalized observations; first divergence; no final-value-only comparison | L38420–38470 (§16), L41869–41906 | SPECIFIED | ror-differential | comparator review | §18 | S-20 |
| R-REF-06 | PanicHost / MockKernel boundary enforcement | L27891–27902 | SPECIFIED | ror-testkit | harness tests | §18 | S-20 |
| R-TEST-01 | Three execution modes + frozen baselines; time ≠ semantics | L38587–38715, L37251–37268 | SPECIFIED | tests/ | CI | §20 | S-21 |
| R-TEST-02 | Reproducible counterexample artifact (16 fields) | L38891–38920, L37293–37315 | SPECIFIED | ror-differential | artifact schema | §21 | S-21 |
| R-TEST-03 | Shrinking protocol (10 ordered priorities) | L38441–38463 | SPECIFIED | ror-differential | shrinking tests | §21 | S-21 |
| R-TEST-04 | Baseline mutation registry M001–M018; additive | L38473–38492 | SPECIFIED | mutations/ | registry review | §19 | S-21 |
| R-TEST-05 | 100% kill rate (non-equivalent); adjudication for equivalents | L38494–38500, L37390–37400 | SPECIFIED | — | M9 gate | §19 | S-21 |
| R-TEST-06 | Mutation validation (verification system tested) | L38515–38540 | SPECIFIED | ror-testkit | framework tests | §19 | S-21 |
| R-TEST-07 | Semantic coverage by obligation tags; metrics ≠ oracle | L38523–38560, L37402–37414 | SPECIFIED | ror-differential | coverage report | §18 | S-21 |
| R-TEST-08 | Crash-injection matrix T0–T6 | L38831–38846, L35216–35236 | SPECIFIED | ror-testkit | M10 gate | §18 | S-21 |
| R-TEST-09 | Fault adjudication (4-way classification) | L38848–38862, L37404–37414 | SPECIFIED | process | R-SCOPE-03 | §18 | S-21 |
| R-TEST-10 | CI gates (PR / nightly / release) | L38864–38890, L37287–37292 | SPECIFIED | CI | gates | §18 | S-21 |
| R-TEST-11 | Final acceptance condition (3 conjuncts) | L38885–38911, L41196–41210 | SPECIFIED | — | M11 | §18 | S-21 |
| R-TEST-12 | Request-frame verification tags: `REQUEST-ARGS-LTR` and `REQUEST-NON-CAP-SHORT-CIRCUIT` added to R-TEST-07's obligation-tagged coverage list; Track A coverage (U-44 resolved) | addendum (request-pipeline) | SPECIFIED | tests/ | Track A request suite | §18 | S-21 |
| R-REPO-01 | Workspace layout; boundaries frozen, names flexible | L39140–39195 | SPECIFIED | workspace | R-ARCH-02 | §02 | S-22 |
| R-REPO-02 | Ten crate contracts (contents + prohibitions) | L39196–40762 | SPECIFIED | crates/ | dependency + visibility review | §02 | S-22 |
| R-REPO-03 | Boundaries enforced structurally (deps, visibility, types, traits, tests) | L41223–41273 | SPECIFIED | workspace | mutation + differential | §02 | S-22 |
| R-ORDER-01 | 20-step implementation order; tests before dependents; reference early | L37793–37812, L42108–42142 | SPECIFIED | process | — | §27 | S-23 |
| R-ORDER-02 | M0–M11 acceptance criteria | L40763–41100, L42165–42190 | SPECIFIED | process | milestones | §27 | S-23 |
| R-ORDER-03 | First security gate (Block ⇏ ExecutablePlan; 7-form differential) | L41155–41195 | SPECIFIED | ror-compiler, ror-runtime | gate | §27 | S-23 |
| R-ORDER-04 | Sprint 1 task set ROR-001…ROR-016 | L41091–41112 | SPECIFIED | process | — | §27 | S-23 |
| R-ORDER-05 | Definition of done (7 components) | L41124–41142 | SPECIFIED | process | — | §27 | S-23 |
| R-CLAIM-01 | Scoped conformance claim (frozen wording) | L38913–38917, L42191–42265 | SPECIFIED | — | — | §28 | S-24 |
| R-CLAIM-02 | 16 prohibited shortcuts | L38858–38890, L42144–42188 | SPECIFIED | all | mutation + review | §28 | S-24 |
| R-CLAIM-03 | Engineering response format; CONFLICT reporting | L38808–38846 | SPECIFIED | process | — | §28 | S-24 |
| R-CLAIM-04 | Start condition (no new semantic phase; reference alongside) | L38921–38928 | SPECIFIED | process | — | §28 | S-24 |


---

## §27 Verification Registry

The verification registry: every obligation tag, mutation, conformance suite entry, milestone gate, and claim-ladder row, with repository evidence state. Canonical home: `final/04-verification-registry.md` (re-emitted from `spec/08`, which is the cleaned authority). The implementation-order obligations R-ORDER-01…05 are homed here because their acceptance criteria are verification gates; the crate-structure obligations R-REPO-01…03 are homed in §02 (architecture).

**Canonical homes transcribed in this section (5):** `R-ORDER-01`, `R-ORDER-02`, `R-ORDER-03`, `R-ORDER-04`, `R-ORDER-05`.

**R-ORDER-01 (implementation order, frozen).** Implementation MUST proceed in strict dependency order: 01 core domain types → 02 canonical serialization → 03 compiler artifacts → 04 capability kernel → 05 budget algebra → 06 CEK evaluator → 07 lambda/call → 08 attenuation → 09 effects → 10 actors → 11 scheduler → 12 marshalling/delegation → 13 persistence → 14 crash recovery → 15 LLM boundary → 16 reference model → 17 differential harness → 18 mutation framework → 19 CI → 20 stress/security validation. *(L37793–37812 (§3); L42108–42142.)*

<!-- FINAL1: R-ORDER-01 canonical home; cleaned authority spec/01 S-23; registry row final/03; status SPECIFIED -->

**R-ORDER-02 (milestones, frozen acceptance).** Milestones MUST satisfy frozen acceptance criteria:

| Milestone | Acceptance |
|---|---|
| M0 Workspace | `cargo check/test/fmt/clippy` pass; no semantic functionality required |
| M1 Canonical serialization | golden vectors pass; round-trips pass; malformed inputs reject; duplicate keys reject; canonical bytes deterministic |
| M2 Pure CEK | Expr/Value/CEK step, environment, lexical capture, stackless frame invariants pass |
| M3 Lambda / Call | closure capture, application LTR, arity precheck pass |
| M4 Capability / Attenuation | CapRef opacity, derive, partial order, revocation cascade pass |
| M5 Effects | 16-step request sequence, issuance, receipts, host mock pass |
| M6 Actors | spawn, mailbox FIFO, async send, blocking receive, scheduler pass |
| M7 Persistence | WAL frame encoding, sequence continuity, snapshot commit pass |
| M8 Differential verification | reference model agreement `Observe(P) == Observe(R)` passes |
| M9 Mutation gate | baseline mutation registry kill rate target satisfied |
| M10 Crash/recovery gate | T0–T6 crash matrix and recovery differential tests pass |
| M11 Release candidate | full test suite, stress, security review, zero open high defects pass |

[INFORMATIVE: "deterministic" in M1 acceptance is explicitly defined in S-17 / R-CANON-05]. *(L40763–41100; L42165–42190.)*

<!-- FINAL1: R-ORDER-02 canonical home; cleaned authority spec/01 S-23; registry row final/03; status SPECIFIED -->

**R-ORDER-03 (first security gate).** Before implementing external effects, the implementer MUST demonstrate `Block ⇏ ExecutablePlan` and production/reference differential agreement for Value/Var/Let/Seq/If/Lambda/Call (including faults); the differential harness MUST be operational before Phase 09 effects. *(L41155–41195.)*

<!-- FINAL1: R-ORDER-03 canonical home; cleaned authority spec/01 S-23; registry row final/03; status SPECIFIED -->

**R-ORDER-04 (first sprint, frozen task set).** First sprint execution MUST complete frozen tasks ROR-001 … ROR-016 (workspace, toolchain, core types, canonical cursor/envelope/primitives/Value, golden vectors, malformed-input suite, duplicate-map-key regression, reference crate, differential observation types, harness stub). *(L41091–41112.)*

<!-- FINAL1: R-ORDER-04 canonical home; cleaned authority spec/01 S-23; registry row final/03; status SPECIFIED -->

**R-ORDER-05 (definition of done).** A component MUST be treated as complete if and only if implementation + unit tests + reference semantics + differential tests + obligation mapping + mutation coverage + documentation (where applicable) are present and verified. *(L41124–41142.)*

<!-- FINAL1: R-ORDER-05 canonical home; cleaned authority spec/01 S-23; registry row final/03; status SPECIFIED -->


**Canonical verification registry summary.** Full registry: `final/04` (re-emitted verbatim from `spec/08`, the cleaned verification authority).

- Verification-obligation tags: **25** canonical indexed rows (16 frozen-source + 9 post-audit addenda, derived from spec/08 §1's two tables and gated against `spec/10` by `spec/_build_index.py`); 1 further documented alias — `MARSHAL-CAPABILITY-REJECT` ≙ `MARSHAL-NO-RAW-CAPABILITY` (spec/08 §1 normalization note) — is *not* an indexed tag. Repository evidence for every one: **NONE** (the suites they mandate do not exist in this repository and are therefore `SPECIFIED`, never `TESTED`).
- Mutation registry: **M001–M042** (42 entries indexed; defined by specification, executed by nothing — no kill rate may be claimed, R-TEST-05/06).
- Conformance-suite obligations, milestone gates M0–M11, and the claim ladder for every theorem are carried in `final/04`; all states are `SPECIFIED` (repo evidence: none).
- The crash-injection, differential, property, mutation, exhaustive and stress regimes (§18–§22) are contracts. No row may be read as executed, passing, or verified.
- `REF1-CONDITIONAL` and `V1-CONDITIONAL` bind the reference/differential contract rows of §17–§18 (§28; `final/08`).


---

## §28 Evidence Model

**Canonical homes transcribed in this section (4):** `R-CLAIM-01`, `R-CLAIM-02`, `R-CLAIM-03`, `R-CLAIM-04`.

**R-CLAIM-01 (scoped conformance claim, frozen wording).** The scoped engineering claim MUST strictly state: *"The independent reference model, exhaustive/property-based tests, mutation testing, and crash-injection suite provide machine-checked evidence that the implementation conforms to the frozen calculus over the tested state space."* Implementers MUST NOT claim that test execution constitutes a mathematical proof of the entire calculus. *(L38913–38917; L42191–42265; L28247–28268.)*

<!-- FINAL1: R-CLAIM-01 canonical home; cleaned authority spec/01 S-24; registry row final/03; status SPECIFIED -->

**R-CLAIM-02 (prohibited shortcuts, frozen).** Prohibited shortcuts MUST NOT be used. Never: use recursive evaluation; trust AST shape as a security boundary; expose authority internals; clone capabilities wholesale during spawn; transfer raw capability references through ordinary messages; use wall-clock time for deterministic semantics; use saturating budget arithmetic; invoke host before durable issuance; infer external-effect nonexecution from missing completion; silently repair persistence corruption; use production recovery/serialization as the reference oracle; compare only final return values; accept surviving mutations without adjudication; reduce semantic coverage to satisfy CI timing; weaken tests because implementation is inconvenient. [INFORMATIVE: "deterministic semantics" is explicitly defined in S-02 / R-CORE-08]. *(L38858–38890; L42144–42188.)*

<!-- FINAL1: R-CLAIM-02 canonical home; cleaned authority spec/01 S-24; registry row final/03; status SPECIFIED -->

**R-CLAIM-03 (engineering response format).** Implementation reports MUST include: component implemented, frozen invariants exercised, production/reference boundary, tests added, differential tests added, mutation tests affected, coverage obligations satisfied, open issues/ambiguities. *(L38808–38846.)*

<!-- FINAL1: R-CLAIM-03 canonical home; cleaned authority spec/01 S-24; registry row final/03; status SPECIFIED -->

**R-CLAIM-04 (start condition).** Implementers MUST NOT propose another semantic phase. Implementation MUST begin from the lowest dependency layer, with the independent reference model alongside production, keeping the differential harness operational as the semantic baseline. *(L38921–38928.)*

---

<!-- FINAL1: R-CLAIM-04 canonical home; cleaned authority spec/01 S-24; registry row final/03; status SPECIFIED -->


**Canonicalization governance chain.** `Red-on-Rust.md` (frozen source, 42,312
lines, turns [1]–[60]) → cleaned authorities (`spec/` document set incl. the 25
frozen post-audit addenda I–V and addenda VI–IX owner decisions) → **this FINAL1
canonical compilation** (a mechanical, ID-preserving reorganization; it adds no
semantics). Where any rendering and the frozen source differ, the source's latest
frozen text governs (spec/01 rule, restated by R-SCOPE-02/03); `final/_build.py`
byte-verifies that every requirement row rendered here is identical (whitespace-
normalized) to its `spec/01` home, so the chain cannot drift silently.

**Artifact classes (distinction preserved at full strength).** `SPECIFICATION ≠
IMPLEMENTATION ≠ TEST ≠ VERIFICATION ≠ PROOF` (non-conflation laws N-06, N-07,
N-08; term/00 §4 bridges). Consequences for this document: (1) no specification-
only artifact (this file, `spec/01`, `req/`, `mod/`, the source code blocks) is
described as an implementation; (2) `python3 check.py` PASS is a *repository
integrity* result — structural presence/ordering/regex/ledger gates — and is
never represented as semantic verification or proof of any `R-…` obligation;
(3) no absent test is described as executed; every verification tag/mutant/
conformance row shows repository evidence `NONE`; (4) no conditional audit verdict
is rendered as PASS (see below).

**Promotion ledger (nothing was upgraded by this compilation).** SPECIFIED→
IMPLEMENTED, IMPLEMENTED→TESTED, TESTED→VERIFIED, VERIFIED→PROVEN: each requires
explicit repository-evidence per `spec/00` §2; none exists; none was granted. The
`audit/` verdicts are carried at their exact conditional wording.

**Status ladder (canonical home in the FINAL1 set; identical to `spec/00` §2):**


**Artifact classes as they stand in this repository (evidence-status matrix: `final/08`):**

| Class | What exists here | What may NOT be said |
|---|---|---|
| SPECIFICATION | this document; `spec/01`; `spec/03`; `req/` registry; frozen source normative text and code sketches | normative as specification text; not implementation evidence |
| IMPLEMENTATION | none in repository | every obligation SPECIFIED and no higher |
| TEST | none executed; test *contracts* only (R-TEST-*, vectors, mutation registry M001–M042 defined-not-run) | no absent test may be described as executed |
| VERIFICATION | structural gates only: `check.py` 16 checkers PASS (count derived from the check.py registration; repository integrity); audit gates (conservation/crash-consistency/reference-independence/checker-mutations) | a passing repository checker MUST NOT be represented as proof unless that checker is explicitly and sufficiently defined as the proof method — none is; the gates check presence/structure, not machine semantics |
| PROOF | none; source proof sketches exist for R-CAP-08 theorems | PROVEN is explicitly NOT claimed (R-CAP-08; R-CLAIM-01: tests are never proof of the entire calculus) |

**Conditional verdicts carried at full limitation strength:**

- **REF1-CONDITIONAL** (`audit/reference-independence-differential-audit.md` §14). Preserved quote: `REF1-CONDITIONAL`. … Not REF1-PASS: multiple required independence properties are UNVERIFIED (observation-equivalence, recovery-equivalence, no-production-semantics-via-`ror-core`, crate-edge enforcement) and several findings (F-01…F-05, F-09, F-11) remain open. … Not REF1-FAIL: no finding is a confirmed BLOCKING coupling … Not REF1-INDETERMINATE: the repository does contain sufficient evidence to determine what the potentially blocking coupling vectors are.
  Rule carried: MUST NOT be represented as REF1-PASS anywhere without new evidence satisfying F-INFL-02's conditions (independent encoder, declared comparison domain, `ror-core` clause operationalized, crate-edge obligations registered, mutation 100 %, crash harness, differential agreement). The independent reference model remains an architectural contract; FINAL1 does not manufacture a reference implementation from the specification.
- **V1-CONDITIONAL** (`audit/v1-evidence-integrity-audit.md` §10). Preserved quote: **V1-CONDITIONAL** … The verification-state model is coherent, accurate, and fully preserved. … However, material non-blocking evidence gaps remain — indeed, they define the BOOTSTRAP state — including missing implementation, missing execution tests, missing independent encoder, undeclared comparison domain, missing crash harness, missing mutation execution, missing security execution, unregistered enforcement obligations, and an unresolved registry disagreement. These gaps are fully documented in findings F-INFL-01 through F-INFL-12 and in the REF1 audit (F-01…F-11; REF1-CONDITIONAL). They prevent V1-PASS … but do not cause V1-FAIL …
  Rule carried: Carried at CONDITIONAL (no input evidence establishes a stronger status). Preserved UNKNOWN claims (V1 §8: F-01 `ror-core`-dependence semantics, F-05 snapshot/WAL/journal record identity, F-04 `Observed*` comparison domain, REF1-vs-build import question) remain UNKNOWN — recorded ambiguity, not absent evidence. F-INFL-01 (checker-gate inflation) and F-INFL-02 (REF1→PASS inflation) are BLOCKING-if-they-occur guards: this compilation asserts neither is occurring; `final/07` re-checks the REF1-PASS representation rule.

**UNKNOWN (V1 §8, preserved):** F-01 `ror-core`-dependence semantics; F-05 snapshot/WAL/journal record identity; F-04 `Observed*` comparison domain; REF1-vs-build import question. These stay `UNKNOWN` (genuinely ambiguous contract-level evidence); no SPECIFIED claim is downgraded for absent implementation.


---

## §29 Open Architectural Decisions

Every unresolved item is listed in `final/09-open-architectural-decisions.md` with its stable identity preserved (U-…, C-…, X-…, V-…, F-01…F-11, F-INFL-01…12, AMB-27/REQ-RECOV-021) plus the FINAL1-level symbol-reuse records `FA-01…FA-10`. FINAL1 resolved none of them. Addenda VII–IX and U-38 are not reopened (no owner authorization to reopen accompanies this compilation). Where two authoritative sources conflict and no owner decision exists, the conflict is recorded here rather than adjudicated.


**Status.** `spec/09` registers **39** decision items under `U-01…U-45`; the register's numbering contains gaps (e.g. `U-10…U-12`, `U-18…U-20`) that FINAL1 neither fills, renumbers, nor reuses; at compilation: **28 OPEN** (`U-02`, `U-03`, `U-04`, `U-05`, `U-06`, `U-08`, `U-09`, `U-13`, `U-14`, `U-15`, `U-16`, `U-17`, `U-21`, `U-22`, `U-23`, `U-24`, `U-25`, `U-26`, `U-27`, `U-28`, `U-29`, `U-30`, `U-31`, `U-32`, `U-33`, `U-34`, `U-35`, `U-37`), the remainder resolved by frozen addenda VII–IX or by the recorded U-38 governance adoption. `spec/06` carries **41 open** contradiction/ambiguity rows (`final/09` §A/§B, computed each build — this sentence is generated from both registers).

| OPEN U-item | Title | Blocking signal (row text) |
|---|---|---|
| `U-02` | Canonical encoding of machine (non-data) state is not frozen | — |
| `U-03` | Spawn budget-allocation policy (who decides `B_alloc`, and its bounds) | — |
| `U-04` | `await` constructor: formal retraction record | — |
| `U-05` | Isolation ladder (WASM / OS-process modes): retired or deferred? | — |
| `U-06` | Effect replayability/reversibility/idempotence: semantics of non-boolean values and link to effect classes | — |
| `U-08` | Fault taxonomy unification | — |
| `U-09` | `Value` domain collision + orphaned `AdmissibleConstraint` | — |
| `U-13` | `PlannerMetadata` / `ProposalDigest` definitions + staleness check exactness | — |
| `U-14` | Error-variant enumeration (subset of U-08) | — |
| `U-15` | `ReconciliationOutcome` variants | — |
| `U-16` | `EventSequence` vs `WalSequence` | — |
| `U-17` | Runnable queue: snapshot field vs recovery reconstruction | — |
| `U-21` | `Op` / `Target` / `Params` domains | — |
| `U-22` | Static effect-set inference (J2) not present in the frozen pipeline | — |
| `U-23` | Is `ValidatedPlan` a type, a predicate, or both? | yes |
| `U-24` | Which canonical envelope is frozen? | yes |
| `U-25` | Two tag namespaces share the `TAG_*` prefix; which constants may an implementation import? | yes |
| `U-26` | Which layer owns the name `StepResult`? | yes |
| `U-27` | Which `ActorStatus` shape governs, and where does shape (iii)'s continuation live? | yes |
| `U-28` | Which `MachineEvent` names govern, and are the eight undeclared paths declared or struck? | yes |
| `U-29` | Which `CanonicalError` shape governs, and do the unit variants survive? | yes |
| `U-30` | Which payload does `MarshalledValue` carry — `Value` or canonical `Vec<u8>`? | yes |
| `U-31` | Which field set is `Authority`'s, which is `Constraint`'s, and what holds the kernel's arena? | yes |
| `U-32` | Does the durable `WalFrame` carry `payload_length`, and what is its checksum's input domain? | yes |
| `U-33` | Which reference-model declarations govern, and are its undeclared types declared or struck? | yes |
| `U-34` | Which turn-[31]/turn-[32] state structs govern — `run_state`, `members` and `scheduler`? | yes |
| `U-35` | The determinism theorem's own parameters are undefined | yes |
| `U-37` | Fixed integer widths for semantic and serialized quantities (`usize` elimination) | — |

**Retired-by-decision-but-register-stale:** U-05 (see `final/09` §C; preserved disagreement).

**Deferred / never-frozen IDs (must not be reused or back-filled):** `R-BUDGET-12` (rule folded into R-BUDGET-15/16; no ID frozen), `R-BUDGET-14` (deferred to a resource-family pass), `U-90` (mutation-harness fixture ID, not a decision row — recorded so it is never mistaken for a dangling reference).

**FINAL1-level ambiguity records (this compilation; no U-nn created):**

| FA-ID | Symbol | Overloading preserved | Disambiguation rule |
|---|---|---|---|
| `FA-01` | `A` | authority tuple (R-CAP-01, source L6354–6379) vs the actor map component of `G = ⟨A, t, L, R, E_journal⟩` (R-CALC-08, L24148–24163) | Within FINAL1 rendering, `A` alone = authority; the actor map appears only inside the named tuple `G`. No renaming of the source formulas is performed. |
| `FA-02` | `D` | duration consumable (R-BUDGET-01, frozen semantics R-BUDGET-15) vs durable-state `D = ⟨S, L, H⟩` / `Recover(D)` (R-RECOV-01) | Budget contexts read `D` as the consumable; recovery contexts read `D` as the durable triple. R-BUDGET-15 disambiguates the *semantics* of the budget side (addendum IX) but the letter collision itself is a frozen-notation fact and stays recorded. |
| `FA-03` | `H` | isolated heap component of `Σ` (R-CALC-08) vs durable effect journal `H` (R-RECOV-01) | Disambiguated by tuple membership; never used bare outside a named configuration. |
| `FA-04` | `R` | reserved-capacity vector `⟨M,S⟩` (R-BUDGET-01) vs capability resource ceiling `R`/`R_A` (R-CAP-01/06) vs the `G` component `R` (R-CALC-08) | Subscripts (`R_A`, `R_max`) and tuple membership are the disambiguators; the ceiling conjunct of the authorization predicate is always cited as `cost ≤ A_op.R`. |
| `FA-05` | `S` | reserved slots `R=⟨M,S⟩` (R-BUDGET-01) vs scope domain `S` in `⟨S,Q,R,T⟩` (R-CAP-01) vs snapshot component `S` (R-RECOV-01) | Tuple membership disambiguates; `⟦A_op.S⟧` marks the scope reading explicitly. |
| `FA-06` | `F` | fuel dimension of `C=⟨F,I,D⟩` (R-BUDGET-01) vs possible-effects set in the compilation judgment (R-COMPILE-03) vs the v1 fault grammar `F` (source L1949; recorded at C-58) | FINAL1 text uses the long names (`fuel`, `possible-effects set`, `fault grammar`) outside formula quotes. C-58 already records the grammar-level homonymy; this row adds the budget/judgment overload. No symbol is renamed. |
| `FA-07` | `C` | consumables vector (R-BUDGET-01) vs the `Constraint` argument in `derive(A, C)` (R-CAP-05) | `C` bare = constraint only inside algebra formulas (`derive`, `Satisfies`); budget partitions always carry subscripts (`C_available`, …). |
| `FA-08` | `e` | current term of `Σ` (R-CALC-08) vs effect instance in `Authorized(c, e, t)` (R-EFFECT-01 step 4) | Canonical effect symbol is `E`; the step-4 `e` is transcribed verbatim from the cleaned authority and is *not* silently corrected. |
| `FA-09` | `B` | dynamic actor budget (R-BUDGET-01) vs static plan-time upper bound `@ B`, `B_max` (R-COMPILE-03) | Named forms (`B_max`) are used for the static bound; the judgment `Γ; κ_static ⊢ e : τ ! F @ B` is quoted as frozen notation. |
| `FA-10` | `T` | lifetime component of `⟨S,Q,R,T⟩` (R-CAP-01, retyped logical by R-CAP-11) vs crash-point labels `T0…T6` (R-RECOV-02) | Bare `T` = lifetime; `T<i>` subscripts = crash points. Noted as benign; recorded for completeness of the one-meaning audit. |

Full registry with provenance and carry-forward groups: `final/09`. Nothing above was adjudicated; the only content of this section is the *record* of non-adjudication, per FINAL1's mandate and R-SCOPE-03.


---

# End of FINAL1 canonical specification

*Compiled by `final/_build.py`; every transcribed row is byte-verified against `spec/01`; registries are byte-verified against `spec/03`/`spec/08`. See `final/07` for the integrity report and `final/10` for the canonicalization report.*
