# Output 3 — Ambiguous Requirements

Every entry below is text in `Red-on-Rust.md` that admits more than one reading, or that the source itself leaves open. **None is resolved here.** Each entry records both readings, the source evidence for each, the registry records affected, the linked upstream finding (`C-…` in `spec/06`, `U-…` in `spec/09`), and whether it blocks verification.

Rules applied: extraction rule 9 (mark unresolved statements AMBIGUOUS rather than resolving them) and rule 3 (do not invent missing requirements). Where the frozen source *does* decide between two texts, that is recorded as a contradiction with a frozen resolution in §2 — not as an ambiguity — and the affected record carries `NON-NORMATIVE` for the superseded text.

---

## §1 Open ambiguities

### AMB-01 — Magnitude of duration `D`
- **Statement:** `Lifetime = [start, end]` where "`D` is part of `C`. Host/scheduler transitions consume `ΔD`" (L8834, v0.3 resolution 4). `Deadline = (logical_time, duration)`.
- **Two readings:** (a) `D` is a fixed per-effect budget consumed by a frozen `ΔD`; (b) `D` is caller-specified and `ΔD` is a policy parameter. The source states the consumption rule but never a value or a derivation for `ΔD`.
- **Evidence:** L10074 (lifetime form); L10114–10126 (deadline form); L8834 (consumption rule); L38108–38137 (deadline validation requires only `t ≤ t_deadline`).
- **Affected records:** REQ-BUDGET-008 (`NORMATIVE-LEVEL: AMBIGUOUS`), REQ-CAP-019, REQ-CALC-020, REQ-CEK-022, REQ-EFFECT-037, REQ-EFFECT-039.
- **Linked:** U-01 (partly answered by resolution 4 — see `req/00-method.md` §5.2), VU-02.
- **Blocking:** yes. `DeadlineValid(E,t)` is testable as written (REQ-EFFECT-016), but exhaustion behavior is not, and no mutation targets it.

### AMB-02 — Canonical encoding of machine state
- **Statement:** "Machine state, including environments, continuations, actor state, pending effects, and authority metadata, will require canonical encoding. **The exact encoding is not yet frozen**" (L37610–37614).
- **Two readings:** (a) the S-17 `Value` codec is reused recursively for these structures; (b) a separate frozen encoding is added by addendum.
- **Evidence:** L37610–37614; L33416 ("The same encoding principles apply to machine state, continuation frames, actor state, effect receipts, and WAL records" — a principle, not a format); L37480–37495 (differential observation normalizes rather than compares encodings).
- **Affected records:** REQ-CEK-003, REQ-ACTOR-006, REQ-PERSIST-016, REQ-PERSIST-004, REQ-RECOV-010, REQ-CANON-035 (Track A).
- **Linked:** U-02, C-19.
- **Blocking:** yes for Track A differential testing and for snapshot digest stability; no for Track B.

### AMB-03 — Spawn budget allocation policy
- **Statement:** "Each spawned actor receives a budget allocation carved from the spawning actor's budget. The total budget across parent and children is conserved" (L10158–10160).
- **Two readings:** (a) the language supplies the split explicitly; (b) the scheduler applies a frozen split policy. Neither is given.
- **Evidence:** L10158–10160; L25624 `execute_spawn` escrow steps; L25931 `Spawn { body, budget }` (a field exists but its origin is unstated).
- **Affected records:** REQ-ACTOR-018 (`AMBIGUOUS`), REQ-BUDGET-024, REQ-BUDGET-030, REQ-ACTOR-017.
- **Linked:** C-33, U-12, U-03, VU-03.
- **Blocking:** yes for conservation testing — the conservation *law* is testable (REQ-BUDGET-024); the allocation *function* is not.

### AMB-04 — `trust_level` in the spawn rule
- **Statement:** v0.3 `E-Spawn` premise `attenuated_context(κ_parent, trust_level)` (L8780).
- **Two readings:** (a) a per-spawn argument supplied by the program; (b) a static property of the spawn site. The term has no counterpart in the frozen `Spawn { body, budget }` or in the capability algebra.
- **Evidence:** L8780; L25931; L25624 (no `trust_level` parameter).
- **Affected records:** REQ-ACTOR-024 (`AMBIGUOUS`), REQ-ACTOR-020.
- **Linked:** U-18.
- **Blocking:** yes for `E-Spawn` conformance.

### AMB-05 — `RunState` vs `ActorStatus`
- **Statement:** `ActorStatus = {Pending, Running, Blocked, Terminated}` (L37838–37841); `Actor { status: RunState }` (L37848–37852) with `RunState = {Active, Blocked, Terminated, Dead}` (L10140–10142).
- **Two readings:** (a) two coexisting enums with an implicit mapping; (b) one enum whose authoritative name and variant set are undecided. `Pending`↔`Active` correspondence is plausible but unstated.
- **Evidence:** both passages; no mapping is given anywhere in L1–42312.
- **Affected records:** REQ-ACTOR-035 (`AMBIGUOUS`), REQ-ACTOR-004, REQ-ACTOR-029, REQ-RECOV-017, REQ-PERSIST-016.
- **Linked:** U-08, VU-04.
- **Blocking:** yes for snapshot round-trip and for `SCHED-BLOCKED-NOT-SCHEDULED`.

### AMB-06 — Scope of the marshal round-trip law
- **Statement:** `∀v : marshal(unmarshal(marshal(v))) = marshal(v)` (L10165–10167).
- **Two readings:** (a) universally quantified over the whole `Value` domain including `Value::Capability`, in which case the law is vacuous or contradicted by the rejection rule; (b) quantified over the marshalable subset only, whose boundary is not enumerated.
- **Evidence:** L10165–10167; L25685 `MarshalFault::CapabilityNotMarshalable` (a rejection exists, so the universal reading cannot hold).
- **Affected records:** REQ-MARSHAL-008 (`AMBIGUOUS`), REQ-MARSHAL-001.
- **Linked:** U-09, VU-05.
- **Blocking:** partially — the property is testable on any explicitly enumerated subset; the subset is not frozen.

### AMB-07 — `CapRef` "never serialized" vs the frozen `CapRef` tag
- **Statement:** "never serialized, never transmitted, never persisted" (L12128, comment on `CapRef`) vs the frozen wire format's `CapRef = 0x30` standalone tag (L33185–33190).
- **Two readings:** (a) the prohibition is about *message payloads and authority data* only; (b) the comment is stale relative to turn [50] and `CapRef` is serializable wherever the codec is applied.
- **Evidence:** L12126–12131; L33185–33190; `Value::Capability(CapRef)` is a machine value (L12283–12294) and the codec covers all 11 variants (L33122–33183).
- **Affected records:** REQ-CANON-014 (`AMBIGUOUS`), REQ-MARSHAL-001, REQ-CORE-009, REQ-ACTOR-032.
- **Linked:** U-10.
- **Blocking:** no for behavior (the marshal rejection is unambiguous); yes for any claim that `CapRef` never appears in bytes.

### AMB-08 — Fault taxonomy vs v0.3 fault names
- **Statement:** the frozen `Fault` enum (L23806) lists `Capability(…)`, `BudgetExhausted`, `DeadlineExceeded`, `HostPolicyDenied`, `EffectCanonicalization`, `Host`, `ReplayCorruption`, `InvalidReceipt`, `StalePlan`. The v0.3 rules conclude `Fault(CapabilityRevoked)` (L8721), `Fault(IsolationBreach)` (L8766), `Fault(CapabilityViolation)` and `Fault(HostPolicyViolation)` (L8748–8757).
- **Two readings:** (a) these names are aliases/legacy names for frozen variants (`CapabilityRevoked`/`CapabilityViolation` → `Fault::Capability(reason)`; `HostPolicyViolation` → `HostPolicyDenied`; `IsolationBreach` → a `Capability` reason); (b) they are additional variants, in which case the frozen enum is incomplete. The source never states either.
- **Evidence:** L23806–23824; L8721; L8748–8757; L8766. Also `spec/06` C-01 (naming) and C-03 (classification).
- **Affected records (10):** REQ-CALC-013, REQ-COMPILE-005, REQ-CAP-023, REQ-EFFECT-025, REQ-EFFECT-036, REQ-EFFECT-038, REQ-EFFECT-040, REQ-DUR-009, REQ-HOST-008, REQ-RECOV-013.
- **Linked:** C-01, C-03, C-04, C-16, U-17.
- **Blocking:** yes — the differential observer compares fault *identity* (REQ-REF-010), so the vocabulary must be closed and agreed before Track A runs. This is the single most blocking ambiguity in the set.

### AMB-09 — Authority for the runnable queue at recovery
- **Statement:** recovery reconstructs "the runnable queue in deterministic order" (L35323–35330, step 10), and the snapshot itself carries "runnable actors and mailbox queues" (L26301–26307).
- **Two readings:** (a) the snapshot queue is discarded and the queue is rebuilt from the replayed event stream; (b) the snapshot queue is authoritative and step 10 merely orders it. Step 10 says "reconstruct", which fits (a); the snapshot content says the data is stored, which fits (b).
- **Evidence:** L26301–26307; L35181–35193; L35323–35330.
- **Affected records:** REQ-RECOV-018 (`AMBIGUOUS`), REQ-PERSIST-016, REQ-RECOV-017, REQ-ACTOR-011.
- **Linked:** U-14, VU-09.
- **Blocking:** yes for the crash matrix at T4/T5 (the expected runnable set differs between readings when a `Blocked` transition follows the snapshot).

### AMB-10 — Planner staleness predicate and `PlannerMetadata`
- **Statement:** "A plan is considered stale if underlying capability state changed since proposal. **The exact staleness predicate is not yet frozen**" (L37929–37961).
- **Two readings:** (a) any authority mutation invalidates; (b) only mutations touching constraints the plan depends on invalidate.
- **Evidence:** L37929–37961; L27236/L28373 (`StalePlan`); L27411 (`PlannerAccepted`, which carries `PlannerMetadata` with `ProposalDigest` — the digest's construction is unstated).
- **Affected records:** REQ-PLANNER-013 (`AMBIGUOUS`, `UNDEFINED` verification), REQ-PLANNER-018, REQ-CORE-015.
- **Linked:** U-13, VU-06.
- **Blocking:** yes for `StalePlan` rejection testing.

### AMB-11 — `Expr::Delegate` is absent from the frozen AST
- **Statement:** turn [32] declares, under the comment "// In the AST, delegation is an explicit operation:", the constructor `Expr::Delegate { capability: Box<Expr>, constraint: Constraint }` (L25989–25992). The frozen `Expr` enum (L12145–12200) has 12 constructors and no `Delegate`.
- **Two readings:** (a) `Delegate` is a 13th constructor and the turn-[21] list is incomplete; (b) the turn-[32] block is illustrative and delegation is not a language-level form. The source never reconciles them.
- **Evidence:** L12145–12200 (frozen 12 constructors); L25989–25992 (`Expr::Delegate`); L8924 (marshal-time wrapper `Delegate(c, constraint, a_target)` — **three** arguments, not two); L9905–9912 and L10836–10842 (`MarshalResult::Delegated { value, capability }`); L2876 (`DelegatedCapabilityToken`); L24062 (prose "explicit `Delegate` operations").
- **Affected records:** REQ-CALC-003, REQ-MARSHAL-003 (`AMBIGUOUS`).
- **Linked:** U-20, C-13, C-16. **Correction to `spec/09` U-20:** its claim that the ⟨capability, constraint⟩ shape "is inference, not source text" is false — the shape is source text at L25989–25992. The real gap is the constructor's absence from the frozen AST and the disagreement between the two-argument AST form and the three-argument marshal wrapper.
- **Blocking:** no for the frozen surface (12 constructors remain the conformance baseline); yes before any delegation conformance can be claimed.

### AMB-12 — `AdmissibleConstraint` is undefined
- **Statement:** `AdmissibleConstraint(C)` is the premise of v0.3 `E-Attenuate` (L8717–8721) and appears at L7858, L8837, L10068. No definition of admissibility exists.
- **Two readings:** (a) admissible = the meet is non-empty (each component's meet is satisfiable); (b) admissible = a syntactic well-formedness predicate on `C`. Note: `spec/09` U-09/`spec/06` C-30 assert this type is "defined once at L10171 and never referenced again" — that assertion is **false** (five occurrences). The open question is its *definition*, not its usage.
- **Evidence:** L7858; L8717–8721; L8837; L10068; L10171.
- **Affected records:** REQ-CAP-024 (`AMBIGUOUS`, `UNDEFINED` verification), REQ-CAP-022, REQ-CAP-007.
- **Linked:** U-09 (as stated, incorrect), C-30 (as stated, incorrect), VU-07.
- **Blocking:** yes — `E-AttenuateDenied` cannot be tested without it.

### AMB-13 — No effect-set inference stage in the pipeline
- **Statement:** the judgment `Γ; κ ⊢ e : τ ! F @ B` yields an effect set `F` (L3874–3905), but the frozen six-stage pipeline (L37964–38021) is parse → normalize → validate → capability analysis → resource analysis → finalize. No stage is named as producing `F`.
- **Two readings:** (a) `F` is produced inside capability analysis; (b) inside resource analysis; (c) a seventh stage is implied.
- **Evidence:** L37964–38021; L3874–3905.
- **Affected records:** REQ-COMPILE-014 (`NON-NORMATIVE` observation), REQ-COMPILE-004, REQ-COMPILE-008.
- **Linked:** U-22, C-14.
- **Blocking:** no for conformance (the pipeline stages are what is verified); yes for compiler-internal review completeness.

### AMB-14 — `EventSequence` vs `WalSequence`
- **Statement:** `pub struct EventSequence(pub u64)` is declared twice, at L31697 and L32060; `WalFrame { sequence: u64 }` with `e_i.sequence < e_{i+1}.sequence` (L35099–35113, L35140).
- **Two readings:** (a) one counter shared by machine events and WAL frames; (b) two counters (machine event sequence and durable record sequence) that happen to be monotone independently. `WalRecord` and `MachineEvent` are distinct types, which suggests (b), but nothing states whether they advance together.
- **Evidence:** L31697; L32060; L35099–35113; L35127–35138. (An earlier draft of this entry described `EventSequence` as `MonotonicSequence<u64>`; no such type exists in the source.)
- **Affected records:** REQ-CALC-005, REQ-PERSIST-004, REQ-PERSIST-005, REQ-RECOV-016.
- **Linked:** U-16.
- **Blocking:** partially — `WAL-SEQUENCE-CONTINUITY` is testable on WAL frames alone; the cross-counter relation is not.

### AMB-15 — *withdrawn: `ReconciliationOutcome` is a closed set*
- **Statement as first recorded:** reconciliation outcomes were said to include a `Replayed` classification and the outcome type's variant list was said to be unspecified.
- **What the source says:** `pub enum ReconciliationOutcome { Completed(EffectReceipt), NotExecuted, Indeterminate }` (L26593–26597) — a closed three-variant set, exactly matching the three classifications named in §12 (L38211, L38232, L38243). The token `Replayed` does not occur anywhere in L1–42312.
- **Correction:** this entry was an extraction error on my part, not an ambiguity in the specification. `spec/09` U-15's claim that the variants are unspecified is likewise false. The requirement stands unambiguously as REQ-DUR-010/REQ-DUR-012/REQ-RECOV-019, which now cite L26592–26598.
- **Linked:** U-15 (incorrect), C-… none.

### AMB-16 — Domains of `Op`, `Target`, `Params`
- **Statement:** `Effect = { op: Op, target: Target, params: Params, cost: EffectCost, capability_required: CapabilityRef }` (L10052–10062); `Op` is given as `{Read, Write, Execute, External}` in one place and `{Read, Write, External}` in another.
- **Evidence:** L10052–10062 and the effect-class listings at L6380–6400 and L38074–38107.
- **Affected records:** REQ-CALC-007, REQ-EFFECT-002, REQ-EFFECT-017.
- **Linked:** U-21, U-06.
- **Blocking:** partially — authorization is testable per declared `op`; the closed set is needed for exhaustive host-policy testing.

### AMB-17 — `await` / retraction semantics
- **Statement:** `await` appears in discussion of blocking receive (L25579 `Deadlock`, L25624 spawn) but is not among the frozen constructors, and no retraction rule exists for a pending receive when the actor is terminated.
- **Evidence:** L12145–12160; L25579; L25685.
- **Affected records:** REQ-CALC-011, REQ-EFFECT-004, REQ-ACTOR-028.
- **Linked:** U-04.
- **Blocking:** no for the frozen surface; yes before any `await`-bearing program can be claimed conformant.

### AMB-18 — Isolation ladder
- **Statement:** process/VM/hardware isolation levels are mentioned as deployment options with no mapping to capability ceilings.
- **Evidence:** L41406–41424 (orientation), L26301 (global state).
- **Affected records:** REQ-ARCH-004, REQ-HOST-002.
- **Linked:** U-05.
- **Blocking:** no — no requirement depends on it.

### AMB-19 — Per-transition `δ_t` values
- **Statement:** logical time advances by `δ_t` per transition; no table of `δ_t` values is given.
- **Evidence:** L8834 (resolution 4); L38108–38137.
- **Affected records:** REQ-BUDGET-012, REQ-BUDGET-026, REQ-CAP-021.
- **Linked:** U-07.
- **Blocking:** yes for time-consumption tests; no for `DeadlineValid` itself.

### AMB-20 — Effect class set completeness
- **Statement:** `Read/Write/External` in the frozen effect protocol vs `Read/Write/Execute/External` elsewhere.
- **Evidence:** L6380–6400; L38074–38107.
- **Affected records:** REQ-EFFECT-002, REQ-EFFECT-017.
- **Linked:** U-06, C-06.
- **Blocking:** partially; see AMB-16.

### AMB-21 — Two incompatible `Value` domains share one name
- **Statement:** the machine domain (L12283–12301) has 11 variants — `Unit, Bool, Integer, Bytes, Symbol, String, List, Tuple, Function, Capability, Actor`; the canonical codec (L33155–33265) encodes 8 — `Unit, Bool, Integer, String, Symbol, Capability, List, Map`.
- **Two readings:** (a) two distinct types sharing a name; (b) one type with an unfrozen variant set. The source never states which.
- **Consequence:** `Value::Map` is encoded but is not a machine variant; `Bytes`, `Tuple`, `Function`, and `Actor` are machine variants with no codec branch. The marshal round-trip law (AMB-06) is stated for "all pure values" across exactly this gap.
- **Affected records:** REQ-CALC-001, REQ-CALC-002, REQ-CANON-008, REQ-MARSHAL-008.
- **Linked:** C-03, C-45, U-09.
- **Blocking:** yes for Track B round-trip tests over the full machine domain.

### AMB-22 — Budget type naming
- **Statement:** `Budget`, `BudgetAllocationSpec`, `BudgetAllocation`, and `B = ⟨C, R, W⟩` all appear.
- **Evidence:** L10076–10100; L37929–37961.
- **Affected records:** REQ-BUDGET-001, REQ-BUDGET-002, REQ-ACTOR-018.
- **Linked:** C-05.
- **Blocking:** no.

### AMB-23 — `EffectCost` field order
- **Statement:** `⟨cost_r, cost_c⟩` in one listing, `⟨cost_c, cost_r⟩` in another; the resource gate consumes `cost_R` and the computational gate consumes `cost_C`.
- **Evidence:** L10062; L8833.
- **Affected records:** REQ-CALC-010, REQ-BUDGET-014.
- **Linked:** C-07.
- **Blocking:** no — the gate semantics are unambiguous; only the tuple's presentation order differs.

### AMB-24 — Project status contradiction
- **Statement:** README states both "specification frozen / implementation not started" (L22–28) and wording implying partial implementation (L656–661).
- **Evidence:** `README.md` L22–28 vs L656–661; the repository contains no Rust sources.
- **Affected records:** REQ-SCOPE-007 (`NON-NORMATIVE` for the README wording).
- **Linked:** C-09.
- **Blocking:** no.

### AMB-25 — Planner state naming
- **Statement:** `Plan`, `PlanProposal`, `PlanIR`, `ExecutablePlan`, `PlannerState` are used with overlapping meanings.
- **Evidence:** L27175 (`PlanProposal`); L37964–38021 (`PlanIR`, `ExecutablePlan`).
- **Affected records:** REQ-PLANNER-002, REQ-PLANNER-014, REQ-COMPILE-004.
- **Linked:** C-12, C-11.
- **Blocking:** no.

### AMB-26 — Authority/frame naming
- **Statement:** `Authority`/`AuthorityNode`/`CapabilityKernel` are used interchangeably, and `pub enum Frame` is declared **eleven** times (L12453, L14047, L14430, L16943, L18650, L19429, L20307, L20713, L21181, L23339, L23830) with `pub struct Continuation` alongside it (L12517).
- **Evidence:** L39373 (`AuthorityNode`); the eleven `pub enum Frame` lines above; L12517 (`Continuation`). No type named `EvalFrame` or `ContinuationFrame` exists in the source.
- **Affected records:** REQ-KERN-001, REQ-KERN-002, REQ-CEK-007.
- **Linked:** C-06, C-08.
- **Blocking:** no.

### AMB-27 — Two recovery step lists: 12 steps vs 19 steps
- **Statement:** §15B.7 (L35193–35204, turn [47]) gives a 12-step recovery algorithm; §15B.11 (L34344–34364, turn [46]) gives a 19-step procedure for the same algorithm.
- **Difference:** the 19-step list separates steps the 12-step list fuses (snapshot framing vs checksum; WAL framing vs per-record checksum; effect-journal reconstruction vs causal-chain validation; digest computation vs checkpoint comparison; `RecoveryComplete` vs scheduler resume) and adds "validate global invariants" and "compare against checkpoint/digest **where applicable**".
- **Two readings:** (a) the later 12-step list is the operative procedure and the 19-step list is a finer-grained restatement of it; (b) the 19-step list adds obligations (notably the "where applicable" checkpoint comparison) that the 12-step list drops.
- **Affected records:** REQ-RECOV-010 (12-step, cited as the operative list), REQ-RECOV-019, REQ-RECOV-021 (the 19-step list).
- **Linked:** not recorded in `spec/06` — this is a new finding of this extraction.
- **Blocking:** no for the 12-step conformance tests; yes for any claim that the recovery procedure is fully specified.

---

## §2 Contradictions with a frozen resolution (recorded, not treated as ambiguous)

| ID | Superseded text | Frozen text | Resolution basis | Registry record |
|---|---|---|---|---|
| C-02 | §1.3 standalone primitive tags `0x10` bool, `0x11` int, `0x13` string | `Value` envelope discriminants `0x00`–`0x07`; standalone tags only for `Value/Symbol/CapRef/ActorId/EffectId` | Later turn [50] freezes the wire format; the tag sets are mutually exclusive | REQ-CANON-006 (`NON-NORMATIVE`), REQ-CANON-005, REQ-CANON-008 |
| C-29 | "transparent crash recovery" unqualified | Recovery theorem with the three-part proviso | Turn [35] explicitly retracts the unqualified claim | REQ-CORE-013, REQ-RECOV-011 |
| C-31 | Reference model may reuse production serialization | Reference model must not depend on any production crate | Turn [54] §19–§21 prohibition list | REQ-REF-004, REQ-CLAIM-012 |
| C-32 | `derive` may widen under explicit escalation | `derive(A,C) ≼ A` with no escalation path | Monotonicity is a boxed security invariant in the frozen calculus | REQ-CORE-004, REQ-CAP-012 |

These four are contradictions the source itself settles by a later frozen statement; the registry records the superseded text as `NON-NORMATIVE` and the surviving text as its own requirement. They are **not** listed as AMBIGUOUS because no reading choice remains open.

## §3 Counts

- Open ambiguities: **26** (AMB-01 … AMB-27, less the withdrawn AMB-15).
- Registry records carrying `NORMATIVE-LEVEL: AMBIGUOUS`: **8** — REQ-BUDGET-008 (AMB-01), REQ-ACTOR-018 (AMB-03), REQ-ACTOR-024 (AMB-04), REQ-ACTOR-035 (AMB-05), REQ-MARSHAL-008 (AMB-06), REQ-CANON-014 (AMB-07), REQ-CAP-024 (AMB-12), REQ-RECOV-018 (AMB-09).
- Records whose verification method is `UNDEFINED` because of an open ambiguity: **8** — see `req/04-verification-undefined.md` §1.
- Verification-blocking ambiguities: AMB-01, AMB-02, AMB-03, AMB-04, AMB-05, AMB-08, AMB-09, AMB-10, AMB-12, AMB-19, AMB-21.
