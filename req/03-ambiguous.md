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
- **Linked:** U-02, C-15 ("15A frozen tag set does not cover machine-state types").
- **Blocking:** yes for Track A differential testing and for snapshot digest stability; no for Track B.

### AMB-03 — Spawn budget allocation policy
- **Statement:** "Each spawned actor receives a budget allocation carved from the spawning actor's budget. The total budget across parent and children is conserved" (L10158–10160).
- **Two readings:** (a) the language supplies the split explicitly; (b) the scheduler applies a frozen split policy. Neither is given.
- **Evidence:** L10158–10160; L25624 `execute_spawn` escrow steps; L25931 `Spawn { body, budget }` (a field exists but its origin is unstated).
- **Affected records:** REQ-ACTOR-018 (`AMBIGUOUS`), REQ-BUDGET-024, REQ-BUDGET-030, REQ-ACTOR-017.
- **Linked:** C-24 ("Spawn budget-split policy (A2) never closed"), U-03, VU-03.
- **Blocking:** yes for conservation testing — the conservation *law* is testable (REQ-BUDGET-024); the allocation *function* is not.

### AMB-04 — `trust_level` in the spawn rule
- **Statement:** v0.3 `E-Spawn` premise `attenuated_context(κ_parent, trust_level)` (L8780).
- **Two readings:** (a) a per-spawn argument supplied by the program; (b) a static property of the spawn site. The term has no counterpart in the frozen `Spawn { body, budget }` or in the capability algebra.
- **Evidence:** L8780; L25931; L25624 (no `trust_level` parameter).
- **Affected records:** REQ-ACTOR-024 (`AMBIGUOUS`), REQ-ACTOR-020.
- **Linked:** C-36 ("`Spawn` isolation/trust parameter vs budget parameter"), C-04 ("`await` elimination and isolation-level `spawn`: not re-declared"), U-05 for the isolation ladder. No `spec/09` item covers `trust_level` itself — new finding of this extraction.
- **Blocking:** yes for `E-Spawn` conformance.

### AMB-05 — `RunState` vs `ActorStatus`
- **Statement:** `ActorStatus = {Pending, Running, Blocked, Terminated}` (L37838–37841); `Actor { status: RunState }` (L37848–37852) with `RunState = {Active, Blocked, Terminated, Dead}` (L10140–10142).
- **Two readings:** (a) two coexisting enums with an implicit mapping; (b) one enum whose authoritative name and variant set are undecided. `Pending`↔`Active` correspondence is plausible but unstated.
- **Evidence:** both passages; no mapping is given anywhere in L1–42312.
- **Affected records:** REQ-ACTOR-035 (`AMBIGUOUS`), REQ-ACTOR-004, REQ-ACTOR-029, REQ-RECOV-017, REQ-PERSIST-016.
- **Linked:** C-18 ("`RunState` vs `ActorStatus` double enum"), VU-04.
- **Blocking:** yes for snapshot round-trip and for `SCHED-BLOCKED-NOT-SCHEDULED`.

### AMB-06 — Scope of the marshal round-trip law
- **Statement:** `∀v : marshal(unmarshal(marshal(v))) = marshal(v)` (L10165–10167).
- **Two readings:** (a) universally quantified over the whole `Value` domain including `Value::Capability`, in which case the law is vacuous or contradicted by the rejection rule; (b) quantified over the marshalable subset only, whose boundary is not enumerated.
- **Evidence:** L10165–10167; L25685 `MarshalFault::CapabilityNotMarshalable` (a rejection exists, so the universal reading cannot hold).
- **Affected records:** REQ-MARSHAL-008 (`AMBIGUOUS`), REQ-MARSHAL-001.
- **Linked:** C-45 (which `spec/06` itself ties to U-09), VU-05.
- **Blocking:** partially — the property is testable on any explicitly enumerated subset; the subset is not frozen.

### AMB-07 — `CapRef` "never serialized" vs the frozen `CapRef` tag
- **Statement:** "never serialized, never transmitted, never persisted" (L12128, comment on `CapRef`) vs the frozen wire format's `CapRef = 0x30` standalone tag (L33185–33190).
- **Two readings:** (a) the prohibition is about *message payloads and authority data* only; (b) the comment is stale relative to turn [50] and `CapRef` is serializable wherever the codec is applied.
- **Evidence:** L12126–12131; L33185–33190; `Value::Capability(CapRef)` is a machine value (L12283–12294) and the codec covers all 11 variants (L33122–33183).
- **Affected records:** REQ-CANON-014 (`AMBIGUOUS`), REQ-MARSHAL-001, REQ-CORE-009, REQ-ACTOR-032.
- **Linked:** C-14 ("CapRef 'never serialized' comment vs 15A CapRef encoding vs snapshot content").
- **Blocking:** no for behavior (the marshal rejection is unambiguous); yes for any claim that `CapRef` never appears in bytes.

### AMB-08 — Fault taxonomy vs v0.3 fault names
- **Statement:** the frozen `Fault` enum (L23806–23816) lists `Capability(…)`, `BudgetExhausted`, `DeadlineExceeded`, `HostPolicyDenied`, `EffectCanonicalization`, `Host`, `ReplayCorruption`, `InvalidReceipt` — **eight** variants, behind an explicit `// ... (previous faults)` elision at L23807, so the set is *not* closed. The v0.3 rules conclude `Fault(CapabilityRevoked)` (L8721), `Fault(IsolationBreach)` (L8766), and `Fault(f_specific)` (L8756) where L8758 names `f_specific` as `CapabilityViolation`, `BudgetExhausted` or `HostPolicyViolation`. **Corrected in place (X-64, X-38, X-69):** this entry previously listed a ninth frozen variant, `StalePlan`, and cited L8748–8757 for the last two names. `StalePlan` is in none of the seven `pub enum Fault` declarations, so it does not belong in a list of the L23806 enum's variants — but it is *not* an invention: the source names `Fault::StalePlan` in prose at L28373 (turn [36]) and gives `StalePlan` as a bare token at L27236 (turn [33]), which makes it a used-but-undeclared variant and one of twelve such `Fault::` paths (X-69). An earlier revision of this pass struck it as a phantom identifier; that strike was itself wrong and is qualified here rather than silently removed (R-SCOPE-03). The names are at L8758, one line outside the range previously cited. The verified count of capability-denial names is **nine**, not four: `CapViolation` and `Revoked` (v1 grammar L1949), `Fault::CapabilityError` (L20389/L20790, asserted by a property test at L20538) and `CapabilityDenied` (L26870, turn [33] — *after* the frozen declaration) were all missing.
- **Two readings:** (a) these names are aliases/legacy names for frozen variants (`CapabilityRevoked`/`CapabilityViolation` → `Fault::Capability(reason)`; `HostPolicyViolation` → `HostPolicyDenied`); (b) they are additional variants, in which case the frozen enum is incomplete. The source never states either. **Corrected in place (X-68):** reading (a) previously also mapped `IsolationBreach` → “a `Capability` reason”. That mapping is withdrawn: the source uses `IsolationBreach` only as the conclusion of the *receipt-mismatch* rule (L2024, L7223, L8766 `E-ReceiptMismatch`), never for capability denial, and it appears in no `Fault` declaration. `HostFault` and `Revoked` are additionally members of the v1 fault grammar `F` at L1949, i.e. *faults*, while from turn [18] and turn [28] respectively they denote a *type* and a *variant of a type* (X-68).
- **Evidence:** L23806–23816 (the frozen enum including its closing brace — the range previously cited, L23806–23824, ran past it into the unrelated heading “## 3. Request Continuation Frames” at L23821); L8721; L8747–8758; L8766; L1949 (the v1 fault grammar); L20389/L20790/L20538 (`Fault::CapabilityError`, the pre-rename variant name, and the property test that asserts it); L26870 (`CapabilityDenied`); L22430/L23808 (`Capability(CapabilityError)`, the frozen rename); L20408–20413 (`pub enum CapabilityError` — declared, contra U-08 and `spec/05` L112); L10820–10823 (`pub enum HostFault` — two variants declared, eight undeclared paths used, X-67). Also `spec/06` C-01 (naming) and C-03 (classification).
- **Affected records (12):** REQ-CALC-013, REQ-CALC-014, REQ-COMPILE-005, REQ-CAP-023, REQ-EFFECT-025, REQ-EFFECT-036, REQ-EFFECT-038, REQ-EFFECT-040, REQ-DUR-009, REQ-HOST-008, REQ-RECOV-013, REQ-MARSHAL-008. REQ-CALC-014 was added by X-64 (its postcondition asserts the phantom `Fault::StalePlan`); REQ-MARSHAL-008 by X-65 (`MarshalFault` has two disjoint declarations).
- **Linked:** C-08 (“Fault naming inconsistency for capability denial” — severity raised MINOR → MAJOR by X-38), C-50, C-54, C-55, C-56, C-57, C-58, C-59 (the twelve undeclared `Fault::` paths), U-08 (“Fault taxonomy unification”), U-14 (“Error-variant enumeration”, subset of U-08 — now blocking for `HostFault`), and `term/` X-38, X-58, X-59, X-64, X-65, X-66, X-67 (BLOCKING), X-68, X-69 with T-70 `Fault`, T-71 `GlobalFault`, T-72 `CapabilityError`, T-73 `MarshalFault`, T-74 `HostFault`.
- **Blocking:** yes — the differential observer compares fault *identity* (REQ-REF-010), so the vocabulary must be closed and agreed before Track A runs. This is the single most blocking ambiguity in the set, and X-67 adds a second blocking fault defect beside it: `HostFault` is declared once with two variants while eight undeclared variant paths are used, six of them on the frozen 15C.42 `ReplayHost` that R-HOST-03/04/05 and REQ-HOST-008 are written against.

### AMB-09 — Authority for the runnable queue at recovery
- **Statement:** recovery reconstructs "the runnable queue in deterministic order" (L35323–35330, step 10), and the snapshot itself carries "runnable actors and mailbox queues" (L26301–26307).
- **Two readings:** (a) the snapshot queue is discarded and the queue is rebuilt from the replayed event stream; (b) the snapshot queue is authoritative and step 10 merely orders it. Step 10 says "reconstruct", which fits (a); the snapshot content says the data is stored, which fits (b).
- **Evidence:** L26301–26307; L35181–35193; L35323–35330.
- **Affected records:** REQ-RECOV-018 (`AMBIGUOUS`), REQ-PERSIST-016, REQ-RECOV-017, REQ-ACTOR-011.
- **Linked:** U-17 ("Runnable queue: snapshot field vs recovery reconstruction"), C-26, VU-09.
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
- **Linked:** C-16 ("`Constraint` appears in the AST but has no frozen data encoding", whose evidence column also records that the frozen `Expr` has no `Delegate` constructor), U-02 (part of).
- **Correction to `spec/01` R-MARSHAL-02 (`spec/01` L334):** that row states the node appears "in the Phase 13 text (L25700, L25931; master prompt L37959)" and that "no frozen document defines its fields". L25700 does state it ("**Explicit Delegation** is handled as a separate, explicit AST node (`Expr::Delegate`)"); **L25931 is `fn execute_spawn(`** and **L37959 is a blank line inside §6**, so two of the three cites are wrong; and the fields *are* defined, at L25989–25992.
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
- **Linked:** U-22 ("Static effect-set inference (J2) not present in the frozen pipeline"). No `spec/06` item covers it.
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
- **Linked:** U-05, C-19 ("Isolation ladder (WASM/OS) dropped without retraction").
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
- **Linked:** U-06, C-05 ("Effect property values outside the declared domain").
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
- **Linked:** no `spec/06` item covers this naming set — new finding of this extraction.
- **Blocking:** no.

### AMB-23 — `EffectCost` field order
- **Statement:** `⟨cost_r, cost_c⟩` in one listing, `⟨cost_c, cost_r⟩` in another; the resource gate consumes `cost_R` and the computational gate consumes `cost_C`.
- **Evidence:** L10062; L8833.
- **Affected records:** REQ-CALC-010, REQ-BUDGET-014.
- **Linked:** C-23 ("`EffectCost` field evolution: `complete` → `complete_max`").
- **Blocking:** no — the gate semantics are unambiguous; only the tuple's presentation order differs.

### AMB-24 — Project status contradiction
- **Statement (citations corrected — X-63, C-53):** the README states the implementation status twice and the two statements disagree. The previously cited ranges were wrong: the status blocks are at `README.md` **L12** ("Implementation:     IN PROGRESS") and **L735** ("Implementation     READY", under the `# Project Status` heading at L732); L22–28 and L656–661 contain no status text, and the README is 745 lines long, so no line in the 42092–42100 range exists in it. The second block was at L708 when this was first recorded, moved to L732 because the terminology-normalization pass added its `term/` paragraph to the README, and moved again to L735 when the declaration sweep extended that same paragraph; the heading is cited beside the line so that the citation survives further growth. The in-source contradiction is between L38939 / L39053 (`READY`, turn [54]) and L41307 (`IN PROGRESS`, turn [58] — the later text, which governs).
- **Evidence (as first recorded, superseded):** `README.md` L22–28 vs L656–661; the repository contains no Rust sources.  **Evidence (verified):** `README.md` L12 vs L735 (`# Project Status`, L732); `Red-on-Rust.md` L38939, L39053, L41307; the repository contains no Rust sources, so neither statement is repository evidence and every obligation stays at `SPECIFIED` (`spec/00-overview.md` §2). The superseded citation is kept above the verified one so the correction is not silent.
- **Affected records:** REQ-SCOPE-007 (`NON-NORMATIVE` for the README wording).
- **Linked:** C-09 (whose citations are corrected in place on the same finding), `term/` X-63, X-53, C-53, T-64, T-65, T-68.
- **Blocking:** no.

### AMB-25 — Planner state naming
- **Statement (corrected — X-62, C-53):** `Plan`, `PlanProposal`, `PlanIR` and `ExecutablePlan` are used with overlapping meanings. This entry previously listed a fifth name, `PlannerState`, which **occurs nowhere in `Red-on-Rust.md` (L1–42312)** — not as a type, field, function, variant or prose term. It was a phantom introduced by this register, and the role it gestures at is occupied by `PlanProposal` (L27175) and, for the accepted-proposal record, `PlannerAccepted` (L27411). The name is struck rather than silently deleted, and `term/` records it as a FORBIDDEN variant that must not be introduced.
- **Evidence:** L27175 (`PlanProposal`); L37964–38021 (`PlanIR`, `ExecutablePlan`).
- **Affected records:** REQ-PLANNER-002, REQ-PLANNER-014, REQ-COMPILE-004.
- **Linked:** C-52, C-53; `term/` X-62 (the phantom), X-34 (the plan family), X-30 (`PlanIR` never declared), X-29 (`NormalizedAST` never declared), X-40 (`spec/05` and `mod/02` called three of these names *aliases* of `ExecutablePlan`), T-01, T-02, T-06, T-08, T-55. No `spec/06` item covered the planner-state naming set when this entry was first written; C-52 now does.
- **Blocking:** no.

### AMB-26 — Authority/frame naming
- **Statement:** `Authority`/`AuthorityNode`/`CapabilityKernel` are used interchangeably, and `pub enum Frame` is declared **eleven** times (L12453, L14047, L14430, L16943, L18650, L19429, L20307, L20713, L21181, L23339, L23830) with `pub struct Continuation` alongside it (L12517).
- **Evidence:** L39373 (`AuthorityNode`); the eleven `pub enum Frame` lines above; L12517 (`Continuation`). No type named `EvalFrame` or `ContinuationFrame` exists in the source.
- **Affected records:** REQ-KERN-001, REQ-KERN-002, REQ-CEK-007.
- **Linked:** C-42 ("`GlobalState` vs `GlobalConfig` naming"), C-17 ("`invoke` vs `request` naming").
- **Blocking:** no.

### AMB-27 — Two recovery step lists: 12 steps vs 19 steps
- **Statement:** §15B.7 (L35193–35204, turn [47]) gives a 12-step recovery algorithm; §15B.11 (L34344–34364, turn [46]) gives a 19-step procedure for the same algorithm.
- **Difference:** the 19-step list separates steps the 12-step list fuses (snapshot framing vs checksum; WAL framing vs per-record checksum; effect-journal reconstruction vs causal-chain validation; digest computation vs checkpoint comparison; `RecoveryComplete` vs scheduler resume) and adds "validate global invariants" and "compare against checkpoint/digest **where applicable**".
- **Two readings:** (a) the later 12-step list is the operative procedure and the 19-step list is a finer-grained restatement of it; (b) the 19-step list adds obligations (notably the "where applicable" checkpoint comparison) that the 12-step list drops.
- **Affected records:** REQ-RECOV-010 (12-step, cited as the operative list), REQ-RECOV-019, REQ-RECOV-021 (the 19-step list).
- **Linked:** not recorded in `spec/06` — this is a new finding of this extraction.
- **Blocking:** no for the 12-step conformance tests; yes for any claim that the recovery procedure is fully specified.

### AMB-28 — `Constraint` has no frozen data encoding
- **Statement:** `Expr::Attenuate { capability, constraint: Constraint, body }` embeds a `Constraint` as an immediate value rather than as an `Expr` (L12177–12181). The frozen 15A tag set (L33087–33265) has tags for `Value`, `Symbol`, `CapRef`, `ActorId`, and `EffectId` only — there is no tag for `Constraint`, and the capability algebra defines it semantically ("an operation-indexed narrowing request", L6395–6398) rather than structurally.
- **Two readings:** (a) `Constraint` is encoded via a `Value`-shaped payload whose layout is yet to be frozen; (b) a new standalone tag is added by addendum.
- **Consequence:** any snapshot, WAL record, or plan that must carry an attenuation constraint has no frozen encoding — this is the concrete instance of AMB-02 for the one AST immediate that is not an `Expr`.
- **Affected records:** REQ-CAP-001, REQ-CAP-007, REQ-CANON-005, REQ-CEK-003, REQ-PERSIST-016.
- **Linked:** C-16, U-02 (part of).
- **Blocking:** yes for snapshot/WAL encoding of attenuation state.

### AMB-29 — "The 15 Core Invariants" table lists ten
- **Statement:** the property-test matrix is titled "The 15 Core Invariants" (L27904) but the table contains exactly ten rows (L27909–27918). The five unlisted invariants are never enumerated anywhere in L1–42312.
- **Two readings:** (a) the title is a stale count and ten is the complete set; (b) five invariants were intended and never written down.
- **What is *not* missing:** each of the ten listed invariants is extracted by name in this registry — 1 Authority Monotonicity (REQ-CORE-004, REQ-CAP-012), 2 No Authority Amplification (REQ-MARSHAL-001), 3 Budget Conservation (REQ-BUDGET-024), 4 Strict Left-to-Right Eval (REQ-CEK-014), 5 Arity Short-Circuit (REQ-CEK-013), 6 Causal Receipt Validation (REQ-EFFECT-027), 7 Deterministic Scheduling (REQ-ACTOR-010, REQ-ACTOR-031), 8 Crash Recovery Equivalence (REQ-RECOV-015), 9 Indeterminate Effect Handling (REQ-DUR-012, REQ-RECOV-005), 10 Stale Planner Rejection (REQ-PLANNER-013). No requirement was invented to reach fifteen (rule 2).
- **Affected records:** REQ-TEST-005, REQ-TEST-007.
- **Linked:** C-20.
- **Blocking:** no for the ten; yes for any claim that the property-test matrix is complete as titled.

### AMB-30 — Two frozen specifications of the canonical envelope
- **Statement:** the canonical byte envelope is specified twice, incompatibly, and both specifications claim authority. The `CanonicalSerialize` doc comment gives `[format_version: u8] [type_tag: u32 LE] [length: u32 LE] [payload]` (L28298, turn [36]); the 15A grammar, the 15B frame and the turn-[54] master prompt give `version: u8 | type_tag: u8 | payload_length: u32 BE | payload` (L38147–38150, L33816, L29905, L35102). They differ in field *name*, tag *width* and *endianness*.
- **Why it is not merely historical:** the contradiction sits inside an **API contract comment**, which is the first thing an implementer reads, and nothing retracts it. Every digest in the system — `EffectDigest`, `StateDigest`, `ResultDigest`, WAL frame checksums, snapshot determinism (R-PERSIST-05) — hashes these bytes, so an encoder built from the comment diverges in the first six bytes of every object.
- **Affected records:** REQ-CANON-001…REQ-CANON-008, REQ-PERSIST-005, every golden-vector obligation.
- **Linked:** C-47, `spec/09` U-24, `term/` X-50 (BLOCKING), X-51, T-62, T-63. Distinct from C-02 (stale *primitive* tags in one section) and from C-15 (tag-set coverage).
- **Blocking:** yes — milestone M1 and any golden vector.

### AMB-31 — Envelope type tags and `Value` discriminants share the `TAG_*` prefix
- **Statement:** four Rust constant names carry two different values in two blocks that are both labeled frozen. Turn [41] declares envelope type tags `TAG_BOOL 0x10`, `TAG_INTEGER 0x11`, `TAG_STRING 0x12`, `TAG_SYMBOL 0x20` (L29952–29956); turns [43] and [45] declare `Value` variant discriminants `TAG_BOOL 0x01`, `TAG_INTEGER 0x02`, `TAG_STRING 0x03`, `TAG_SYMBOL 0x04` (L32364–32371, L33171–33173, L33591–33594). Turn [41] used `DISC_` for discriminants (L29961–29965) and gave `Capability` the byte `0x0A` against turn [43]/[45]'s `0x05`; its table headed "(Frozen)" also omits `Symbol`, `List` and `Map`, so three of eight variants are unencodable under it.
- **Why it matters:** the frozen `Value::Symbol` decoder needs both namespaces in one function — `Self::TAG_SYMBOL` (0x04) at L33194 and `Symbol::TYPE_TAG` (0x20) at L33195. A module importing both const blocks does not compile; keeping one silently re-tags the other layer.
- **Affected records:** REQ-CANON-005, REQ-CANON-006, REQ-CANON-008, REQ-REF-* (15C.36 canonical-serialization differential boundary).
- **Linked:** C-48, C-49, `spec/09` U-25, `term/` X-54 (BLOCKING), X-55, X-56, T-31, T-62, T-63; extends C-02.
- **Blocking:** yes — milestone M1.

### AMB-32 — `ValidatedPlan` is a struct in the compiler and a predicate in the central theorem
- **Statement:** `pub struct ValidatedPlan { ir: PlanIR, effects: EffectSet }` (L865) is a stage artifact private to `mod compiler`, while the boxed central theorem reads `ExternalEffect(E) ⇒ ValidatedPlan(P) ∧ Authorized(E,κ,t) ∧ …` (L41337–41351, L27491–27509; `spec/01` L25, R-CORE-02), where `ValidatedPlan(·)` is a proposition over `P`. No predicate of that name is defined and no rule states when the struct satisfies it. R-CORE-03 (`spec/01` L27) uses a different arity again for `Authorized`.
- **Two readings:** (a) `ValidatedPlan(P)` is shorthand for "`P` is a `ValidatedPlan`", i.e. a type test — which makes the theorem's first conjunct trivially true of any compiled plan and does no normative work; (b) it is a distinct judgment the compiler must discharge, in which case it needs a definition, a domain and a witness.
- **Affected records:** REQ-CORE-002, REQ-CORE-003, REQ-COMPILE-001…REQ-COMPILE-005.
- **Linked:** C-46, `spec/09` U-23, `term/` X-01 (BLOCKING), X-04, X-05, T-04, T-06, N-01, N-06.
- **Blocking:** yes — for any mechanization or conformance test of the external-effect chain.

### AMB-33 — `HostFault` is declared with two variants and used with eight (BLOCKING)
- **Statement:** `pub enum HostFault` is declared exactly once, at L10820 (turn [18]), as `{ IoError(String), PolicyViolation(String) }`. The source then uses eight `HostFault::` paths, none of which is declared: `UnboundCapability` (L1203), `ConcreteScopeViolation` (L1208, L1214), `Io` (L1210, L1216), `ReplayTraceExhausted` (L1245, L24020, L25496, L25838, L34519, L35225), `ReplayCorruption` (L25500, L25841, L34522, L34528, L35226, L35227), `TraceExhausted` (L10546), `ReplayIdMismatch` (L10550), `ReplayDigestMismatch` (L10553). Neither declared variant is ever used.
- **Two readings:** (a) the L10820 declaration is stale and the real variant set is the eight used paths, in which case no frozen declaration of `HostFault` exists; (b) the declaration governs and every use site is a defect. The source never states either, and the two readings produce incompatible host error types.
- **Compounding facts:** two names denote the exhausted-trace condition (`ReplayTraceExhausted` six times, `TraceExhausted` once) and three denote a replay mismatch (`ReplayCorruption`, `ReplayIdMismatch`, `ReplayDigestMismatch`); `ReplayCorruption` is *also* a declared `Fault` variant (L23814), so the same identifier denotes a fault at two levels of the taxonomy; and `HostFault` is the payload of the frozen `Fault::Host(HostFault)` (L23813), so the gap reaches the machine-visible fault vocabulary compared under R-REF-05.
- **Affected records:** REQ-HOST-007, REQ-HOST-008, REQ-RECOV-013, REQ-CALC-013.
- **Linked:** C-57, `spec/09` U-14 (error-variant enumeration), `term/` X-67 (BLOCKING), X-68, T-74, T-42 `ReplayHost`, T-44 `HostExecutor`, T-70 `Fault`. AMB-08's dependency note on REQ-HOST-008 noticed one instance of this and attributed it to the `Fault` enum; it is a `HostFault` declaration gap and it is eight variants wide.
- **Blocking:** yes — `ReplayHost` is one of the 25 terms the normalization request names explicitly, and ordered replay is what makes the differential observer's host side deterministic. The host error type cannot be written without inventing variants, which R-SCOPE-03 prohibits.

### AMB-34 — `Fault::StalePlan` is used by the source but declared by none of the seven `Fault` enums
- **Statement:** the frozen source names `Fault::StalePlan` once, in prose at L28373 (turn [36]: “A `PlanProposal` with `observation_sequence < current_sequence` is rejected with `Fault::StalePlan`”), and gives `StalePlan` as a bare token at L27236 (turn [33], the sole content of a one-line ```text block). No `pub enum Fault` declaration — L10882, L17788, L18125, L22415, L23319, L23806, L26865 — contains the variant, and the frozen L23806 block elides its own head with `// ... (previous faults)` at L23807.
- **Two readings:** (a) `StalePlan` is a real `Fault` variant hidden by the L23807 elision, so the frozen enum is incomplete rather than wrong; or (b) staleness rejection produces some other fault and the prose at L28373 is loose. The source states neither, and the seven declarations disagree among themselves anyway (X-58).
- **Not a register defect:** `spec/01` L138 (“plus `StalePlan` at the planner boundary”), REQ-CALC-014 and AMB-08 all record it, and all three are **source-supported** — REQ-CALC-014's own SOURCE line already cited L28373. An earlier revision of this pass filed this row as a canonicalization-layer phantom on the claim that `Fault::StalePlan` “occurs nowhere in L1–42312”; the claim is false, and the four amendments made on it (`spec/01` L138, REQ-CALC-014's statement and postcondition, AMB-08's list) are reverted with the withdrawn wording quoted (R-SCOPE-03).
- **Affected records:** REQ-CALC-013, REQ-CALC-014, REQ-PLANNER-006, REQ-PLANNER-008.
- **Linked:** C-54, C-59, `spec/09` U-08, U-13, `spec/06` C-38 (the `observation_sequence` check at L27236), `term/` X-64, X-69, T-70, T-02.
- **Blocking:** no — but it is one of twelve undeclared `Fault::` variant paths, and `Fault` identity is compared by the differential observer (REQ-REF-010), so the set has to be closed by U-08 before Track A runs.

### AMB-35 — `MarshalFault` has two disjoint declarations and `CapabilityError::Invalid` is never declared
- **Statement:** `pub enum MarshalFault` is declared twice with **zero** shared variants: L10846 (turn [18]) as `{ CapabilityNotTransferable, InvalidFormat }` and L25983 (turn [32]) as `{ CapabilityRequiresDelegation, SerializationError }`. No supersession is stated, and the canonicalization layer cites only the turn-[32] form (`mod/06-actor` L62/L103, REQ-MARSHAL postconditions at `req/01-part1` L301, `spec/08` L63). Separately, `pub enum CapabilityError` is declared once (L20408, turn [28]) as `{ Revoked, Expired, InvalidConstraint, // ... }`, but the `CapabilityKernelView::derive` empty-queue fallback is written twice in the same turn with different values: L20451 uses the declared `Err(CapabilityError::InvalidConstraint)` and L20835 uses `Err(CapabilityError::Invalid)`, which is never declared.
- **Two readings:** for `MarshalFault`, (a) turn [32] supersedes turn [18] and `CapabilityNotTransferable` has no successor — the same gap C-08 records for `ScopeViolation`; or (b) both sets are live and denote different conditions (non-transferable vs requires-delegation are not aliases). For `CapabilityError`, (a) `Invalid` is a typo for `InvalidConstraint`, or (b) it is a distinct elided variant. The source states neither.
- **Affected records:** REQ-MARSHAL-001…REQ-MARSHAL-008, REQ-CAP-012, REQ-CAP-024, REQ-CALC-013.
- **Linked:** C-55, C-56, `spec/09` U-14, `spec/05` L112, `term/` X-65, X-66, X-59, T-72, T-73, T-70.
- **Blocking:** no for `MarshalFault` on its own, but yes in combination with AMB-33: R-MARSHAL-01…04 make capability rejection at the marshalling boundary a security property, and `MarshalFault(...)` is itself a payload of the turn-[33] `Fault` (L26871), so the contested set reaches the machine-visible taxonomy.


### AMB-36 — `MachineEvent` is declared eight times and used with eight variant paths no declaration admits
- **Statement:** eight declarations — L14697 (turn [23]), L15958 (turn [24]), L17588 (turn [25]), L18104 and L18631 (turn [26]), L20318 and L20724 (turn [28]), L22002 (turn [29]) — three of which elide their heads (`// ... (Previous events)` L20319, `// ... (previous variants)` L20725, `// ...` L22003), none of which carries a supersession note. Eight further variant paths are used and declared by none of them: `EnterRequest` (L21483, L23380), `BeginRequestTarget` (L21536, L23398), `BeginRequestArgument` (L21645, L23426), `Blocked` (L25740, L26038), `Spawned` (L25668), `ActorSpawned` (L25966), `Sent` (L25728), `MessageSent` (L26027).
- **Two readings:** (a) the declarations are additive — the union of all eight is the event vocabulary and the undeclared paths are members hidden by the three elisions; or (b) each declaration is the vocabulary of its own turn and the later ones retract the earlier, in which case the eight undeclared paths are prose errors to be remapped. No declaration states which, and the drift is not monotone: `BeginArgument(usize)`/`EndArgument(usize)` appear at L17596–17597 and the three `*Request*` events resemble them without matching them.
- **Why the duplicate names decide it:** `Blocked` against the declared `Block`, and `Spawned`/`ActorSpawned` and `Sent`/`MessageSent` as pairs used in different turns of the same document. Whichever reading is adopted, one name from each pair has to be chosen, and the choice is observable — `MachineEvent` is what the WAL records and what the differential observer compares (REQ-REF-010), so two implementations picking different names report a divergence that is a naming artifact, not a semantic one.
- **Affected records:** REQ-CORE-008, REQ-ACTOR-007, REQ-REF-010, REQ-PERSIST-001.
- **Linked:** C-61, `spec/09` U-28, U-02 (family), `term/` X-71, T-75, T-47, T-45, T-70.
- **Blocking:** no for the frozen surface, yes before any trace-equality, WAL-format or differential test can be written.

### AMB-37 — `CanonicalError` is declared seven times in four shapes, and the same variant names carry different arities
- **Statement:** L29188 (turn [38]) declares five unit variants; L29968 (turn [41]) declares seven and respells two of them (`Utf8Error` for `InvalidUtf8`, `PayloadTooShort` for `UnexpectedEof`) while adding `LengthOverflow`, which L29188 lacks; L30661 (turn [41]) turns six of the same names into payload-bearing struct variants (`InvalidVersion { expected: u8, found: u8 }`, `InvalidTypeTag { expected: u8, found: u8 }`, `LengthMismatch { expected: u32, found: usize }`, `TrailingBytes { count: usize }`, `InvalidDiscriminant { found: u8 }`, `InvalidBoolValue { found: u8 }`); L32083 (turn [43]), L32959 and L33299 (turn [45]) restate; L34994 (turn [47]) elides its head as `// ... previous variants` and adds `DuplicateMapKey` — “NEW: Enforces strict injectivity”.
- **Two readings:** (a) the payload-bearing shape (iii) supersedes the unit shapes, so `InvalidVersion` carries `expected`/`found` and a decoder must report them; or (b) all four shapes are live and the unit variants remain legal, in which case the same condition has two arities and two spellings. The source states neither, and no declaration carries a supersession note.
- **Why it is not cosmetic:** `InvalidVersion` as a unit variant cannot carry the expected and found version bytes, so a decoder written against L29188 loses the diagnostic L30661 requires and a test written against L30661 does not compile against L29188. Two spellings for one condition means a fixture matching one silently passes on the other — and canonicalization is where a silent pass becomes a consensus fork, because two nodes that disagree on which errors are fatal disagree on the digest. `DuplicateMapKey` is the only variant enforcing map injectivity, so whether canonical encoding rejects duplicate keys at all depends on which declaration is read.
- **Affected records:** REQ-CANON-001, REQ-CANON-002, REQ-PERSIST-001.
- **Linked:** C-62, `spec/09` U-29, U-24, U-25, U-14, `term/` X-72, X-50, T-76, T-62, T-63.
- **Blocking:** yes — for milestone M1 and any golden vector, on the same path as AMB-31/AMB-32 (U-24, U-25).

### AMB-38 — `StepResult` names two disjoint enums, the CEK machine's and the actor scheduler's
- **Statement:** L1006 (turn [3]) declares `Continue | Halt(Value) | Fault(Fault) | YieldToHost(Effect)` — one reduction of one actor, no identity carried. L9586 (turn [17]), restated at L10397 and L10947 (turn [18]), declares `Progressed | Blocked(ActorId) | Pending(ActorId, EffectRequest) | Halted(ActorId, Value) | Faulted(ActorId, Fault) | NoRunnableActors` — every variant carries an `ActorId`. The two have no variant in common and neither declaration mentions the other.
- **Two readings:** (a) one name, two layers, and prose must disambiguate by context; or (b) the scheduler's enum is the successor and the machine's is superseded — but the machine's variants are still used in turn-[3] reduction semantics and the scheduler's in turn-[17] scheduling, so neither reading removes the other. The source offers **no second name** for either, unlike `Observation`/`HostObservation`, where it did.
- **Why it matters here:** both are returned by a method an implementer will call `step`. Turn [3] says a step yields `YieldToHost(Effect)`; turn [17] says it yields `Pending(ActorId, EffectRequest)` — and `Effect` versus `EffectRequest` is one of the distinctions this normalization is required to keep separate, so the homonymy puts that distinction at risk from the type name itself. Prose saying “the step returned Blocked” is ambiguous between three enums (`StepResult`, `ActorStatus`, `RunState`).
- **Affected records:** REQ-CEK-001, REQ-ACTOR-004, REQ-ACTOR-007, REQ-REF-010.
- **Linked:** C-63, `spec/09` U-26, `term/` X-73, X-23, T-77, T-70, T-35, T-36.
- **Blocking:** yes — a fixture written from one turn does not compile against an implementation written from the other.

### AMB-39 — `ActorStatus` is declared seven times in three shapes, and shape (iii) carries no continuation
- **Statement:** (i) L9411 (turn [17]) and L10346 (turn [18]): `Pending(PendingEffect), Blocked(Continuation)` — the continuation inside `Blocked`. (ii) L21234 (turn [29]): `Pending { effect: EffectRequest, continuation: Continuation, reservation: ReservedCapacity }, Blocked(Continuation)` — the continuation in both variants. (iii) L23306 and L23793 (turn [30]): `Pending { effect: EffectRequest, reservation: ReservedCapacity }, Blocked` — the continuation in neither. L10866 (turn [18]) restates shape (i).
- **Two readings:** (a) shape (iii) is the frozen form and the continuation lives outside the status, in `actor.eval.continuation` as the turn-[30] machine assumes — in which case a `Pending` actor cannot be resumed from its own status and something else must persist the continuation; or (b) shape (ii) is the frozen form and shape (iii) is an abridged restatement. The source states neither, and no declaration carries a supersession note.
- **Not the same question as AMB-05 or X-21:** AMB-05 and C-18 concern `ActorStatus` versus `RunState` (two distinct enums), and X-21 concerns the `Running`/`Active` naming split. This is about which *shape* of one enum governs, and — under reading (a) — where the continuation is held and how it is persisted, which determines what a snapshot must contain (U-17 is adjacent) and what recovery must reconstruct.
- **Affected records:** REQ-ACTOR-002, REQ-ACTOR-004, REQ-DUR-001, REQ-RECOV-001.
- **Linked:** C-64, `spec/09` U-27, U-17, `term/` X-74, X-21, X-22, T-35, T-37, T-32, T-45.
- **Blocking:** yes — for replay and recovery conformance and for any test that resumes a blocked actor.
---

## §2 Contradictions with a frozen resolution (recorded, not treated as ambiguous)

| ID | Superseded text | Frozen text | Resolution basis | Registry record |
|---|---|---|---|---|
| C-02 | §1.3 standalone primitive tags `0x10` bool, `0x11` int, `0x13` string | `Value` envelope discriminants `0x00`–`0x07`; standalone tags only for `Value/Symbol/CapRef/ActorId/EffectId` | Later turn [50] freezes the wire format; the tag sets are mutually exclusive | REQ-CANON-006 (`NON-NORMATIVE`), REQ-CANON-005, REQ-CANON-008 |
| C-40 | "transparent crash recovery" unqualified | Recovery theorem with the three-part proviso | Turn [35] explicitly retracts the unqualified claim | REQ-CORE-013, REQ-RECOV-011 |
| C-33 | Reference model may reuse production serialization | Reference model must not depend on any production crate | Turn [54] §19–§21 prohibition list | REQ-REF-004, REQ-CLAIM-012 |
| — | `derive` may widen under explicit escalation | `derive(A,C) ≼ A` with no escalation path | Monotonicity is a boxed security invariant in the frozen calculus | REQ-CORE-004, REQ-CAP-012 |

These four are contradictions the source itself settles by a later frozen statement; the registry records the superseded text as `NON-NORMATIVE` and the surviving text as its own requirement. They are **not** listed as AMBIGUOUS because no reading choice remains open.

## §3 Counts

- Open ambiguities: **38** (AMB-01 … AMB-39, less the withdrawn AMB-15). AMB-30, AMB-31 and AMB-32 were added by the terminology-normalization pass and are all **blocking**; AMB-33 (blocking), AMB-34 and AMB-35 were added by the same pass's fault-taxonomy audit and cover the `HostFault` declaration gap, `Fault::StalePlan` and the `MarshalFault`/`CapabilityError` splits (X-67, X-64, X-65, X-66); **AMB-34 was then rewritten** by the declaration sweep, which showed that the audit had filed it on a false premise — `Fault::StalePlan` does occur, at L28373 — so the row now records a variant the source *uses* and no `Fault` declaration admits, one of twelve such paths (X-69), with the withdrawn wording quoted. **AMB-36, AMB-37, AMB-38 and AMB-39** were then added by the same pass's declaration sweep and cover `MachineEvent` (eight declarations, eight undeclared paths), `CanonicalError` (seven declarations in four shapes), `StepResult` (two disjoint enums under one name) and `ActorStatus` (seven declarations in three shapes) — X-71, X-72, X-73, X-74; all four are blocking for a conformance test and each has its own `spec/09` decision (U-28, U-29, U-26, U-27). AMB-08, AMB-24 and AMB-25 were corrected in place on the same pass (a variant that is in none of the seven `Fault` declarations, and a wrong citation range, in AMB-08 — X-64, X-69, X-68; a citation defect and a phantom identifier in AMB-24/AMB-25 — X-63, X-62) with their superseded wording kept rather than deleted.
- Registry records carrying `NORMATIVE-LEVEL: AMBIGUOUS`: **8** — REQ-BUDGET-008 (AMB-01), REQ-ACTOR-018 (AMB-03), REQ-ACTOR-024 (AMB-04), REQ-ACTOR-035 (AMB-05), REQ-MARSHAL-008 (AMB-06), REQ-CANON-014 (AMB-07), REQ-CAP-024 (AMB-12), REQ-RECOV-018 (AMB-09).
- Records whose verification method is `UNDEFINED` because of an open ambiguity: **8** — see `req/04-verification-undefined.md` §1.
- Cross-reference completeness: all 65 `spec/06` contradictions and all 23 `spec/09` unresolved decisions are referenced by this document or by the registry; `req/_validate.py` fails the build if any referenced id does not exist in those files. The counts moved from 45 and 16 when the terminology-normalization pass added C-46…C-53 and U-23…U-25, and from 53 to 58 when its fault-taxonomy audit added C-54…C-58; the validator's expectations were updated in the same commit each time, explicitly and not silently.
- Verification-blocking ambiguities: AMB-01, AMB-02, AMB-03, AMB-04, AMB-05, AMB-08, AMB-09, AMB-10, AMB-12, AMB-19, AMB-21, and AMB-30, AMB-31, AMB-32, AMB-33 (added by `term/`; each also blocks a milestone, not only verification). AMB-33 is the second blocking fault-taxonomy defect beside AMB-08: `HostFault` is declared once with two variants while eight undeclared variant paths are used, six of them on the frozen 15C.42 `ReplayHost`.
