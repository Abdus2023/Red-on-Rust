# Output 2 — Compound Requirements That Could Not Safely Be Split

A compound obligation was kept as one atomic unit when splitting it would change what the source requires. Five reasons apply; each entry below names its reason and the loss that splitting would cause. **42 entries (CN-01…CN-42), covering 117 registry records** — some entries group several records that share one indivisible reason (e.g. CN-41 covers the eleven milestone-gate records REQ-ORDER-005…REQ-ORDER-015).

---

## A. Single formula / biconditional definition (splitting destroys the connective)

| ID | Record | Compound content | Why it cannot be split |
|---|---|---|---|
| CN-01 | REQ-CORE-002 | `ExternalEffect(E) ⇒ ValidatedPlan(P) ∧ Authorized(E,κ,t) ∧ CapabilityWithinCeiling(E) ∧ BudgetAvailable(E) ∧ DeadlineValid(E,t) ∧ HostPolicyOK(E) ∧ Issued(E)` | The source states one boxed implication with seven conjuncts (L27491–27509). Splitting into seven independent implications would assert each alone and lose the claim that **all** are required together; the per-gate obligations are separately extracted as REQ-EFFECT-006…REQ-EFFECT-018 and cross-referenced. |
| CN-02 | REQ-CORE-013 | `Recover(Snapshot, EventLog, EffectJournal) ≡ PreCrashMachineState` **provided** (a) durably reconciled, (b) safely idempotent/replayable, or (c) classified `Indeterminate` | The proviso is part of the theorem. The unqualified form (L26133) was explicitly superseded because "without it, 'transparent crash recovery' would be too strong a claim" (L27551–27569). Detaching the proviso would restate the claim the source retracted. |
| CN-03 | REQ-CAP-007 | `A₁ ≼ A₂` iff `O₁ ⊆ O₂` and ∀o: `S₁ ≼_S S₂ ∧ Q₁ ≼_Q Q₂ ∧ R₁ ≤ R₂ ∧ T₁ ⊆ T₂` | A biconditional definition. Splitting yields four one-directional implications and no longer defines the order. |
| CN-04 | REQ-CAP-010 | `Authorized(A,E,t) ⇔ op ∈ O_A ∧ target ∈ ⟦A_op.S⟧ ∧ A_op.Q(params) ∧ cost ≤ A_op.R ∧ t ∈ A_op.T` | The canonical authorization predicate is a five-conjunct biconditional (L6406–6421). The "only if" direction is what makes an omission a security defect (mutation M005 targets one conjunct); splitting loses it. |
| CN-05 | REQ-CAP-012 | `derive(A,C) = { (o, derive_op(A_o,C_o)) \| o ∈ O_A ∩ O_C }`, `derive_op = ⟨S⊓S_c, Q⊓Q_c, R⊓R_c, T⊓T_c⟩` | One definition over four components; the meet is what makes `derive(A,C) ≼ A` hold (REQ-CORE-004). |
| CN-06 | REQ-CAP-013 | `Valid(c,t) ⇔ Live(c) ∧ t ∈ Lifetime(c) ∧ ∀a ∈ Ancestors(c). Live(a)` | Biconditional validity definition; the ancestor quantifier is inseparable from the liveness clause. |
| CN-07 | REQ-BUDGET-014 | `WithinBudget(E,C,R,R_A) ⇔ cost_C(E) ≤ C ∧ ReserveOK(cost_R(E),R,R_max) ∧ cost(E) ≤ R_A` | The dual gate is defined by three conjuncts; the source added the third conjunct specifically to fix an unsound earlier form (L8833, resolution 2). |
| CN-08 | REQ-COMPILE-007 | `Γ; κ_static ⊢ e : τ ! F @ B` | A single judgment form threading four components; the frozen text replaces four separate judgments (J1–J4) with this one (L3874–3905), so re-splitting would restore the superseded form. |
| CN-09 | REQ-HOST-010 | Replay correspondence theorem with its three per-step verification conditions | The theorem's conclusion holds only under the stated per-step conditions; separating them changes it from a conditional theorem to an unconditional one. |
| CN-10 | REQ-ACTOR-031 | `InitialState + SchedulerTrace + HostTrace ⇒ UniqueMachineTrace` with its three stated causes (FIFO scheduler, monotonic IDs, deterministic CEK) | The source states the theorem together with its grounds; the grounds are the justification, not separate obligations (they are separately extracted as REQ-ACTOR-010, REQ-ACTOR-008, REQ-CEK-001). |
| CN-11 | REQ-TEST-030 | 3-conjunct final acceptance condition | Conformance is defined as the conjunction; any single conjunct alone is explicitly declared insufficient (L38879). |
| CN-12 | REQ-PERSIST-019 | `ValidSnapshot(S) ⇔ Commit(S) ∧ Digest(Canonical(S)) = RecordedDigest(S)` | Biconditional; the commit clause and the digest clause are jointly necessary and sufficient. |
| CN-13 | REQ-RECOV-002 | `Recover(D) = Replay(S, L, H)` | Definitional equation over the triple `⟨S,L,H⟩`. |

## B. Closed sets (the absence of members is normative)

| ID | Record | Closed set | Why it cannot be split |
|---|---|---|---|
| CN-14 | REQ-CANON-005 | Standalone tags `0x00/0x20/0x30/0x40/0x41` | The set is closed: the *absence* of standalone tags for bool/integer/string is what makes the stale §1.3 text non-conforming (C-02). Splitting into per-tag records loses the closure. |
| CN-15 | REQ-CANON-008 | `Value` discriminants `0x00`–`0x07` | Same closure argument; an extra discriminant is a format violation. |
| CN-16 | REQ-CANON-025 | Ten `CanonicalError` variants | A closed error vocabulary; the differential observer compares fault identity, so the set must be complete. |
| CN-17 | REQ-CALC-001 | 11 machine `Value` variants | Closed variant set; a 12th variant is a semantic change requiring an addendum. |
| CN-18 | REQ-CALC-003 | 12 frozen `Expr` constructors | Closed AST surface; adding `Delegate`/`await` is precisely the open question (AMB-11, AMB-17). |
| CN-19 | REQ-CEK-007 | 9 continuation frames | Closed frame set; the continuation-length invariant (REQ-CEK-018) is only checkable against a closed set. |
| CN-20 | REQ-CALC-013 | `Fault` taxonomy + `StalePlan` | Closed fault vocabulary; its incompleteness is recorded as AMB-08 rather than filled in. |
| CN-21 | REQ-BUDGET-015 | 4 `BudgetError` variants | Closed error set. |
| CN-22 | REQ-PERSIST-014 | 6 `WalRecord` kinds | Closed record taxonomy; the journal validator rejects anything else. |
| CN-23 | REQ-REF-004 | 10 forbidden production entry points | A closed prohibition list; splitting it into ten records would invite treating an unlisted production dependency as permitted. |
| CN-24 | REQ-REF-006 | 12 modelled semantic areas | Completeness is the requirement: an unmodelled area is an unverified area. |
| CN-25 | REQ-REF-009 | 6 reference-model non-goals | A scope-exclusion set with no independent verification target per item; splitting adds no falsification power. |
| CN-26 | REQ-REF-010 | 8 normalized observation channels | The comparator's contract is the whole set; comparing seven of eight is the defect REQ-REF-013 prohibits. |
| CN-27 | REQ-REF-011 | 6 excluded internal details | Closed exclusion list, qualified by "unless explicitly semantic". |
| CN-28 | REQ-TEST-012 | Baseline mutation registry M001–M018 | Frozen additive baseline; the per-mutant obligations are carried in the `VERIFICATION-METHOD` of the records each mutant targets (e.g. M002 → REQ-CEK-014). |
| CN-29 | REQ-TEST-020 | 15 frozen coverage tags | The tag list is the coverage contract; a partial list under-reports. |
| CN-30 | REQ-REPO-006 / REQ-REPO-007 | `ror-core` domain contents; 7 prohibitions | The prohibition list is closed ("MUST NOT contain host calls, filesystem, networking, scheduler, persistence, capability authority storage, LLM integration"). |
| CN-31 | REQ-SCOPE-008 | 21-item frozen-semantics surface | One prohibition over an enumerated surface; splitting would suggest the unlisted items are modifiable. |
| CN-32 | REQ-CORE-016 | 3 named silent-repair prohibitions | Illustrative-but-closed enumeration attached to one prohibition; the general rule and its instances are inseparable. |
| CN-33 | REQ-ACTOR-006 / REQ-CALC-017 / REQ-CALC-018 | `GlobalState`, `Σ`, `G` shapes | Structural definitions; their components are not independently assertable obligations. |
| CN-34 | REQ-PERSIST-016 / REQ-PERSIST-017 | Snapshot inclusion and exclusion lists | Both are closed lists; the exclusion list's items are individually unverifiable (their absence is the property). |
| CN-35 | REQ-TEST-007 | 16-field counterexample artifact | The schema is the requirement; a partial artifact fails it as a whole. |
| CN-36 | REQ-CLAIM-020 | 9 report components | Checklist with one review gate. |
| CN-37 | REQ-REPO-018 | 8 enforcement mechanisms | The requirement is that all are in use "rather than relying solely on developer discipline"; a subset defeats the purpose. |
| CN-38 | REQ-REPO-005 | Workspace layout | Frozen-intent directory set. |
| CN-39 | REQ-TEST-026 / REQ-TEST-027 / REQ-TEST-028 | PR / nightly / release-candidate gate contents | Each gate is one CI obligation with a conjunctive content list. |
| CN-40 | REQ-TEST-001 / REQ-TEST-002 / REQ-TEST-003 | Three execution modes with their baselines | Each mode's baseline (depth ≤ 4 / layer order / 50k–100k, 100+ actors) is part of the mode's definition. |
| CN-41 | REQ-ORDER-005 … REQ-ORDER-015 | M1–M11 acceptance criteria | Each milestone is one gate whose content is a conjunctive checklist; the per-item obligations are extracted separately where they are behavioral (e.g. M1 items → REQ-CANON-037, REQ-CANON-018, REQ-CANON-025). |
| CN-42 | REQ-ORDER-023 | ROR-001…ROR-016 sprint task set | Closed task list ("exactly these tasks"); REQ-ORDER-024 states what must be absent. |

## C. Ordered sequences and transactions (order is the requirement)

| Record | Sequence | Why it cannot be split |
|---|---|---|
| REQ-EFFECT-005 | 16-step request sequence | "The Request sequence is immutable" (L38024). The obligation is the order; per-step content is extracted separately (REQ-EFFECT-006…018) and cross-referenced. |
| REQ-DUR-002 | 7-step issuance transaction | The two fsync positions are only meaningful relative to the appends and the `Pending` transition. |
| REQ-PERSIST-018 | 5-step atomic snapshot protocol | Same argument; the commit marker's position defines validity. |
| REQ-RECOV-010 | 12-step recovery algorithm | Steps are mutually dependent (e.g. sequence-continuity check before replay; digest comparison after replay). |
| REQ-ACTOR-017 | 6-step spawn transaction | Escrow before ID allocation before derivation before enqueue; reordering breaks conservation. |
| REQ-COMPILE-004 | 6-stage compilation pipeline | Stage order is the boundary guarantee. |
| REQ-ARCH-001 / REQ-ARCH-006 | End-to-end pipeline; dependency direction | Ordered chains. |
| REQ-ORDER-001 | 20-step implementation order | Explicit dependency order. |
| REQ-TEST-009 | 10-priority shrinking order | The priorities are the protocol. |
| REQ-RECOV-021 | 19-step recovery procedure (§15B.11) | An ordered procedure; the ordering is the content, and its relation to the frozen 12-step list is AMB-27. |
| REQ-CLAIM-… | — | The 16 prohibited shortcuts **were** split (REQ-CLAIM-001…016): each has its own falsification target, unlike the sequences above. |

## D. Transition rules with conjoined premises and conjoined effects

| Record | Rule | Why it cannot be split |
|---|---|---|
| REQ-EFFECT-037 | v0.3 `E-Request` (6 premises → 5 simultaneous state effects) | The rule's meaning is that *all* premises license *all* effects atomically. |
| REQ-EFFECT-038 | v0.3 `E-RequestDenied` (three-way precedence) | Precedence is the requirement. |
| REQ-EFFECT-039 | v0.3 `E-Receipt` (2 identity premises → resume + charge + advance + log) | Same. |
| REQ-ACTOR-024 | v0.3 `E-Spawn` (2 escrow premises + ID + attenuation → parent/child updates + log) | Same. |
| REQ-CAP-022 | v0.3 `E-Attenuate` (`Valid` + `AdmissibleConstraint` → derive, bind, register, charge, advance) | Same. |
| REQ-CALC-020 / REQ-CEK-022 | v0.3 `E-Let`/`E-Seq`/`E-If`, `E-Call` cost rules | The charge and the deadline premise are one rule. |
