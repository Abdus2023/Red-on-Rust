# REF1 — Reference Model Independence & Differential-Coupling Audit

**Status:** AUDIT — verification, gap classification, and dependency register only.
No new frozen text is issued (R-SCOPE-03). This is the **REF1 — Reference Model
Independence Auditor** deliverable, governed by the base REF1 prompt and its addendum
(PASS/FAIL/UNVERIFIED criteria, finding-record format, severity scheme, evidence
capture, final-verdict scheme).

This document audits whether the frozen independent reference model (`Ref`/MOD-14,
Phase 15C in `Red-on-Rust.md`) is semantically independent of production, whether the
two differential properties

    Observe(Production(X)) = Observe(Reference(X))
    Canonical(Recover_P(D)) = Canonical(Recover_R(D))

(subject to explicit external-effect reconciliation) are well-posed and checkable, and
**reports every dependency — specification-layer or enforcement-layer — that could
invalidate differential testing.**

**Finding-identifier continuity.** This document's findings were previously recorded as
`F-01 … F-11`. Per the REF1 addendum, those identifiers are preserved unchanged across
this revision; no numeric identifier is reused or renumbered, and no new finding was
added that would require a `REF1-F-0NN` identifier. New findings, should any arise in a
later audit, will use the next unused `REF1-F-0NN` identifier.

**Scope boundary.** This repository is at the state the frozen source itself calls
**BOOTSTRAP** (`spec/07` §1): there is **no Cargo workspace, no crate, no Rust source,
no test, no CI**. Every requirement is `SPECIFIED`; none is `IMPLEMENTED`. The Rust
blocks in `Red-on-Rust.md` are normative specification artifacts, not repository code.
Consequently this audit is of the **specification and of the machinery that would
enforce it** (the typed dependency graph, the registry checks, the conservation
checker). It cannot execute `Observe_P = Observe_R` — neither side exists — and it does
**not** claim either differential property holds. It reports where the specification
leaves the boundary leak-prone and where the enforcement gates do not actually gate. This
fact drives the PASS/FAIL/UNVERIFIED classification below (see §13): no independence
property that requires an implementation to demonstrate (no reuse, no indirect
dependency, an actually-built independent encoder) can be PASSed on execution evidence in
a repository with no code, and none can be FAILed on evidence of an actual violation,
because no violation is executed. The audit therefore returns **REF1-CONDITIONAL**, not
REF1-PASS and not REF1-FAIL, and assigns no **BLOCKING** severity (no identified
execution path exists).

**Primary anchors.** `Red-on-Rust.md` L35272–37168 (frozen Phase 15C), §10
L39645–39651, §14 L39807–39828; `spec/01` S-20 (R-REF-01/02/03/04) and S-21
(R-REF-05, R-TEST-*); `spec/07` §2/§6 (crate map + dependency direction);
`spec/10-index.json`; `req/01-registry-part6-verification.md` (REQ-REF-001…009/017),
`req/01-registry-part8-reference-15C.md` (15C.1–15C.46, REQ-TEST-…); `mod/14-reference.md`,
`mod/15-differential.md`; `dep/05-violations.md` (RI-1…4, HD-5, HD-6, V-02, V-05); and
`term/02-collisions.md` (X-06, X-29, X-84).

**Mechanical gate.** `audit/_reference_independence_checker.py` (run by `check.py`)
re-derives the independence *contract* from the frozen source and asserts the hard
structural presence predicates (the ten forbidden surfaces, the five `ror-reference`
crate-edge forbiddens, the distinct `Ref*` identifiers, the two differential-property
statements, the anti-oracle-collapse rule, and the twelve modelled areas) and **reports**
(without failing on) the advisory coupling vectors F-01…F-09. `dep/_graph.py` (also run
by `check.py`) asserts at the **module/graph layer** that no implementable-kind edge joins
MOD-14 to a production module (RI-1…RI-4). Both are specification-graph / presence checks;
they are **not** `Cargo.toml` checks (no Cargo exists) and they do **not** audit the soft
`ror-reference → ror-core` clause that this audit flags. `audit/_conservation_checker.py`
independently re-derives budget-conservation transitions in Python; it is part of the
background, not a check on this boundary (see F-10). **Gate status:** `python3 check.py`
was green before this integration and is green after it (see §13); the checker does not
consume this audit document, so the document restructure neither fakes nor breaks the
gate.

---

## 1. Scope

This audit answers the REF1 question: **is the Red-on-Rust reference model semantically
independent enough to serve as an oracle for differential testing, and what every
dependency is that could invalidate that independence?**

In scope:
- The frozen Phase 15C reference-model specification (`Red-on-Rust.md` L35272–37168;
  registry part 8), as the source of truth for the reference model.
- The frozen crate and module boundaries: `ror-reference`/MOD-14 vs. the production
  crates `ror-core/compiler/kernel/runtime/persistence/host/agent` and MOD-01…MOD-12.
- The ten `Production*` forbidden surfaces and the ten §10/§14 crate-edge forbiddens.
- The distinct reference identifiers `RefCapId`, `RefActorId`, `RefEffectId`.
- The two differential properties and their comparison domains.
- The recovery / canonicalization rules and external-effect reconciliation.
- The repository's own audit and checker machinery (`dep/_graph.py`, the registry and
  term checkers, `audit/_reference_independence_checker.py`,
  `audit/_conservation_checker.py`).

Out of scope (explicitly, per REF1 governance):
- Redesigning the reference model. No normative text is issued and no frozen
  requirement is changed. Findings carry a disposition for an **owner decision**; none is
  resolved here.
- Verifying production semantics themselves beyond what is needed to establish the
  boundary (production is treated as the black-box side of the differential test).
- Re-auditing the reference *correctness* against the semantics (that is the
  differential test's own job); this audit is about the boundary between the two sides.

## 2. Source-of-truth material

The frozen specification and the registered requirement/ownership/verification records
are the authorities. Every claim below is anchored to one or more of:

| Authority | Role |
|---|---|
| `Red-on-Rust.md` L35272–37168 | **Frozen Phase 15C reference specification** (15C.1–15C.46). |
| `Red-on-Rust.md` §10 L39645–39651 | `ror-reference` crate contract ("must NOT depend on …"; the soft `ror-core` clause). |
| `Red-on-Rust.md` §14 L39807–39828 | Forbidden dependency edges (Cargo level). |
| `spec/01` S-20 | R-REF-01/02/03/04 (independence, differential, canonical-recovery). |
| `spec/01` S-21 | R-REF-05, R-TEST-* (observation/trace/comparator). |
| `spec/07` §2/§6 | Crate map + dependency direction. |
| `spec/10-index.json` | Machine-readable crate graph (including the `ror-reference.depends_on` string). |
| `req/01-registry-part6-verification.md` | REQ-REF-001…009/017. |
| `req/01-registry-part8-reference-15C.md` | 15C.1–15C.46, REQ-REF-018…036, REQ-TEST-001…056. |
| `mod/14-reference.md`, `mod/15-differential.md`, `mod/18-ownership-matrix.md` | Module ownership + differential module. |
| `dep/05-violations.md` | RI-1…4, HD-5, HD-6, V-02, V-05 (typed-graph violations). |
| `term/02-collisions.md` | X-06 (Observation homonym), X-29/X-84 (undeclared types incl. the `Observed*` element types and reference vocabulary). |
| `audit/_reference_independence_checker.py` | Mechanical gate for the hard presence predicates + advisory reports. |

Requirement IDs cited in findings were verified present in the registry (e.g.
REQ-REF-001…036, REQ-TEST-044/045/046/048). Where a finding has no direct frozen
authority it states `NO-DIRECT-FROZEN-AUTHORITY` explicitly.

## 3. Reference-model boundary

**What the frozen text defines as "reference".** The independent model in Phase 15C —
`RefValue`, `RefEnv`, `RefState`, `RefCapabilityStore`, `RefBudget`, `RefActor`,
`RefScheduler`, `RefGlobalState`, `RefHost`, `RefRecoveryResult`, with identifiers
`RefCapId`/`RefActorId`/`RefEffectId` — homed in crate `ror-reference` / MOD-14. The
frozen text says it "does not reuse production persistence code" (15C.17), is "intentionally
separate from production runtime" (§10), must not call any `Production*` surface (15C.3,
R-REF-02, REQ-REF-004, REQ-TEST-048), must not depend on
`ror-runtime/kernel/persistence/host/agent` (§10/§14), and that its recovery engine must
not call production `Recover`/`Replay`/`CanonicalDecode`/persistence validators (15C.17).

**What the frozen text defines as "production".** The ten `Production*` surfaces plus the
frozen crate DAG `ror-core/compiler/kernel/runtime/persistence/host/agent` that implement
them. `ror-core` hosts `Value` (R-CALC-01), `CapRef` (R-KERN-01), `ActorId` (R-ACTOR-03),
`EffectId` (R-CALC-04), the budget operand types (R-BUDGET-*), and the 15A canonical
serializer/codec (R-CANON-*).

**The two sanctioned sharing points.** 15C.3 permits the reference to share *code and
semantic constants* with production **"only where unavoidable at the external test
boundary"**, i.e. the frozen-semantics constant set and the test harness. §10 permits a
dependency on **`ror-core`** "only where doing so does not accidentally import production
semantics." Both qualifiers are prose and, as established below, are the two places the
boundary is leak-prone.

## 4. Production/reference dependency analysis

### 4.1 The module-layer graph

`MOD-14 → MOD-01…MOD-12` (twelve specification edges) are **SEMANTIC_DEPENDENCY** by rule
R3-reference-mirror: the reference *must* re-model the frozen semantics independently.
`dep/_graph.py` RI-1…RI-4 assert there is **no implementable-kind** edge joining MOD-14 to
a production module, and no production module takes an implementable dependency on a
verification node. This is a **specification-graph labeling** result, not a proof that a
real Cargo build cannot cross the boundary.

### 4.2 The crate-layer graph

Two authoritative crate sources exist and disagree (`dep/05` V-05):
- `spec/07` §6 draws the production DAG.
- `spec/10-index.json` gives `ror-reference.depends_on = ['frozen semantics only (no
  production core deps)']` — a **prose string**, not a crate name, and one that claims to
  forbid precisely the `ror-core` edge that the frozen §10 **permits** and that §14 does
  **not** forbid. `dep/05` V-05 (L104) and the audit register this disagreement.

Net crate-layer fact: the only production crate the frozen text would let `ror-reference`
reach is **`ror-core`** (§10 permissive clause, §14 omits it from the forbidden list), and
that allowance is exactly where the production `Value`/identity/budget/codec objects live.
This is the highest-leverage boundary fact and is reported as **F-01** and its enabling
clause **F-11**.

### 4.3 Shared-code-risk register

The following are the categories of dependency the REF1 prompt asked to be searched. Each
is elaborated in §9 and resolved to a finding:

| Coupling category | Resolved by finding(s) |
|---|---|
| Shared helpers | F-10 (conservation checker), F-03 |
| Shared transition functions | F-03 |
| Shared serializers / canonicalization | F-01, F-02, F-03 |
| Shared normalization | F-04 |
| Shared state machines | F-05 |
| Shared authority/capability logic | F-01 (via `ror-core` `CapRef`), otherwise satisfied (REQ-REF-023) |
| Shared resource/budget logic | F-01 (via `ror-core` budget operands) |
| Shared scheduling logic | satisfied in text (RefScheduler); no independent finding beyond F-01 |
| Shared persistence/recovery logic | F-02, F-05 |
| Shared replay logic | F-05 (recovery replay over production-named records) |
| Shared production data structures | F-01, F-04, F-05 |
| Shared error semantics | F-06 |
| Shared verification / oracle logic | F-07 (comparator co-residence) |
| Distinct-identity integrity | F-08 (duplicated declarations), F-01 |
| Enforcement / tooling | F-09, F-03, F-11 |

No coupling category in the sweep is left unexamined; each is assigned to a finding in §9
and given a full finding record in §10.

## 5. Forbidden production-surface analysis

The ten enumerated call surfaces are prohibited at both the requirement level and the
anti-oracle-collapse level:

| Forbidden surface | Where prohibited | Hard predicate enforced by gate? |
|---|---|---|
| `ProductionEvaluator` | 15C.3; R-REF-02; REQ-REF-004; REQ-TEST-048 | ✓ presence in text (checker §1) |
| `ProductionContinuation` | 15C.3; R-REF-02; REQ-REF-004 | ✓ presence |
| `ProductionCapabilityKernel` | 15C.3, 15C.8 ("never called"); R-REF-02; REQ-REF-004 | ✓ presence |
| `ProductionBudget` | 15C.3, 15C.10; R-REF-02; REQ-REF-004 | ✓ presence |
| `ProductionScheduler` | 15C.3, 15C.13; R-REF-02; REQ-REF-004 | ✓ presence |
| `ProductionSerializer` | 15C.3, 15C.15; R-REF-02; REQ-REF-004 | ✓ presence |
| `ProductionRecovery` | 15C.3, 15C.17; R-REF-02; REQ-REF-004 | ✓ presence |
| `ProductionPersistence` | 15C.3, 15C.17; R-REF-02; REQ-REF-004 | ✓ presence |
| `ProductionReplayHost` | 15C.3, 15C.19; R-REF-02; REQ-REF-004 | ✓ presence |
| `ProductionTransition` | 15C.3; R-REF-02; REQ-REF-004; REQ-TEST-048 | ✓ presence |

**Verdict: the call-edge prohibition is closed and tracked; the crate/type/edge level is
not** (F-01, F-09, F-11). The frozen text bans **calls** (`Production*` and
`reference_*() → production_*()`). It does **not** by itself ban shared *types*, shared
*schemata*, or shared *records*, and it affirmatively permits the one crate edge that
would smuggle production semantics in. See §1.1-equivalent analysis under §5/§9 and the
dependency register.

## 6. Distinct-identifier verification

**Required:** `RefCapId`, `RefActorId`, `RefEffectId` genuinely distinct reference-side
identities that cannot silently collapse into production identities.

**Reference (frozen):** `Red-on-Rust.md` L35471–35473 (15C.4) and again L39664–39666
(§10):
```rust
pub struct RefCapId(pub u64);
pub struct RefActorId(pub u64);
pub struct RefEffectId(pub u64);
```
**Production:** `CapRef` (R-KERN-01, a struct; in places `{index, generation}`),
`ActorId(pub u64)` (R-ACTOR-03), `EffectId(pub u64)` (R-CALC-04). 15C.4: "No conversion
from a production `CapRef` into `RefCapId` is permitted inside the reference semantics.
Identifiers are mapped only at the harness boundary when constructing equivalent initial
states."

**Result of the mechanical checks** (run by the gate, §5 of the checker):
- Each `pub struct RefCapId`/`RefActorId`/`RefEffectId` is present in the source.
- Production `CapRef`/`ActorId`/`EffectId` are present and are *different type names*.
- The conversion ban is stated (15C.4); the harness boundary mapping is 15C.21 /
  REQ-REF-036.
- No alias `type RefCapId = CapRef`, no shared constructor, no `From<CapRef> for
  RefCapId`, and no production-backed representation is declared in the frozen source.

**Caveats that keep this from a clean PASS (see F-01, F-08):**
- **Duplicated authoritative declaration (F-08):** the same three `Ref*Id` structs are
  declared **twice** (L35471–35473 and L39664–39666) with no linkage and no ownership
  register (D-) entry; they can drift.
- **The `ror-core` allowance (F-01):** §10 permits `ror-reference` to depend on
  `ror-core`, which **hosts** `CapRef`/`ActorId`/`EffectId`. Distinct *names* do not stop
  an implementer from importing those production types under the permissive clause.

## 7. Observation-equivalence analysis

Property: `Observe(Production(X)) = Observe(Reference(X))`.

- **What `X` contains:** a `GeneratedCase` — the same generated semantic input executed
  against both sides (15C.22); the input domain is produced from `TestInput`,
  `Canonicalized Test Fixtures`, `Generated Programs/Capabilities/Budgets/Event
  Traces/Persistence Images` (15C.3) at the shared external test boundary.
- **What `Observe` observes:** a *normalized* `Observation` per side (15C.20,
  REQ-REF-035): `terminal_states`, `event_trace`, `effects`, `budgets`,
  `scheduler_trace`, `faults`, `state_digest`. The frozen text states this is a **test
  representation**, not a runtime serialization format, and "must not become a third
  semantic wire protocol."
- **Comparison / normalization rules:** first-divergence and trace normalization levels
  (R-REF-05, REQ-TEST-033/034/042) distinguish an included set
  (`ActorSelected`, `ActorSpawned`, `CapabilityDerived`, `Send`, `Receive`, `Blocked`,
  `Woken`) from excluded implementation detail. Identity correspondence is 15C.21 /
  REQ-REF-036.
- **Can either side influence the other's observation?** Not in the frozen data flow —
  each side emits its own `Observation_P`/`Observation_R`. But a **shared schema** is the
  one sanctioned shared object at the boundary, and it is **undeclared** (F-04) and
  homonymous (X-06), so the exact comparison domain is not closed. `ObservedActor`,
  `ObservedEvent`, `ObservedEffect`, `ObservedBudget`, `ObservedSchedulerStep`,
  `ObservedFault`, `ObservedDigest` are referenced at L36170 (15C.20) but **declared
  nowhere** (`term/_structs.py --undeclared`; X-29/X-84).
- **Is the comparison independently meaningful?** It is **not yet falsifiable**: with no
  declared `Observed*` domain there is no closed definition of what gets normalized or in
  what order, so a reference that fills in a different `ObservedFault`/`ObservedEvent`
  shape will produce a false divergence (or, with a lax comparator, a false agreement).

**Status: UNVERIFIED.** The property is normative and well-stated, but the comparison
domain is unspecified (undeclared `Observed*` types; homonymous `Observation`), and no
implementation exists to establish the PASS condition "no indirect dependency causes
production semantics to determine the reference observation." See F-04, F-06.

## 8. Recovery-equivalence analysis

Property: `Canonical(Recover_P(D)) = Canonical(Recover_R(D))` subject to explicit
external-effect reconciliation.

- **What durable input `D` contains:** abstract records representing `Snapshot`, `WAL`,
  `EffectJournal` (15C.17, L36061) that both recovery procedures consume.
- **Do both procedures consume equivalent input?** By design yes — the *same* `D` is
  canonicalized and fed to both sides. But the records are **production-named** with no
  `Ref*` prefix in a model that renames every other domain (F-05), so the type of `D` at
  the reference side is ambiguous between an abstract semantic record and the production
  record types.
- **Is canonicalization independent?** `Canonical` is the frozen 15A canonical codec,
  homed in `ror-core` (R-CANON-01…11) — i.e. *production* serialization. The reference is
  forbidden to *call* `ProductionSerializer` (R-REF-02) yet must reproduce the same
  canonical bytes. REQ-TEST-046 makes the independent-encoder requirement
  **conditional**: "where an independent reference encoder exists for the test domain,
  `Canonical_P(v) = Canonical_R(v)` is required" (F-02). If no independent encoder is
  built, agreement can only be asserted against the *production* 15A codec.
- **Does either implementation reuse production persistence/recovery logic?**
  Prohibited in text (15C.17; REQ-TEST-045), but the "independent test-side decoder" is
  an `ror-core` code path (ROR-008 of R-CANON-07) in the one crate the reference may
  import (F-05).
- **How are external effects reconciled?** R-RECOV-07/08 make reconciliation the only
  resolver of `Indeterminate` (never auto-`NotExecuted`); R-DUR-04 gives the
  `Prepared ∧ ¬Issued ⇒ Discard` / `Issued ∧ ¬Completed ⇒ Indeterminate` rule; 15C.18
  implements the T0–T6 matrix and does not infer host execution from absent completion.
  These are present (the crash-consistency gate verifies them).
- **Can reconciliation hide a semantic divergence?** Yes in principle: reconciliation is
  the one place where an `Indeterminate` outcome may legitimately differ and be resolved
  asynchronously; a reconciliation rule shared with production (or a production-backed
  decoder) could absorb a genuine recovery divergence into an "awaiting reconciliation"
  state. This is subsumed by F-05 (shared decoder) and F-02 (shared canonical codec).

**Status: UNVERIFIED.** The property is normative and the reconciliation semantics are
specified, but its evaluation depends on an independent reference 15A encoder that is
only conditionally required (F-02) and on `ror-core`-bound records/decoder that the
reference may import (F-01, F-05). No implementation exists to demonstrate independence.

## 9. Coupling-vector analysis

This section sweeps every coupling category the REF1 prompt and addendum require be
searched, gives the dependency path for each, and names the finding. Detailed finding
records (with claim, authority, mechanism, consequence, evidence, counter-evidence,
status, disposition) are in §10.

### 9.1 Shared helpers — F-10, F-03
`audit/_conservation_checker.py` is an **executable** encoding of budget/resource
transition semantics (Op-01…Op-22: `op_01_pure_ast_step`, `op_12_atomic_mailbox_enqueue`,
`op_13_receive_dequeue`, `op_14_yield`, `op_15_actor_halt`, `op_16_effect_request`,
`op_18_effect_completion`, `op_19_host_failure`) with its own `Consumables`, `Reserved`,
`PersistentStorage`, `TaggedExplicitResources`, `ActorBudgetState`. It is **standalone**
(it shares code with neither side), so it is not itself a coupling — but it is a third,
un-coupled executable semantic model of the budget/transition rules living outside the
frozen `ror-reference` contract and outside R-REF-02's forbidden list. If ever adopted as,
or copied into, the reference oracle, its arithmetic (Python `int`, `sys.exit` on
underflow vs. the frozen `checked_sub` / no-saturating R-BUDGET-02) is unaudited for
exactness against the frozen rules. F-03 additionally covers the risk that the *frozen
production implementation* Rust blocks are copied into the reference as "shared helpers."

### 9.2 Shared transition functions — F-03
15C.6/15C.7 require the reference to "implement the **frozen Phase 10 rules**", 15C.8 the
"frozen Phase 11 algebra", 15C.11 the "frozen Phase 12 issuance sequence". That is correct
— both sides implement the *same specification*. The hazard is that the frozen source also
contains single **frozen production implementation** Rust blocks the reference is told to
re-implement: the "Phase 10 Frozen Implementation (Lambda / Call)" (`Red-on-Rust.md`
L18091), the "Phase 12 Frozen Implementation … finalize_request" (L23248/L23870), and the
15A canonical codec ("Corrected Rust Implementation", L30647). If the reference is
implemented by copying/adapting one of these, the "reference" *is* production.
15C.38 (L36881–36882) forbids "copying production implementation bodies into the
reference module" and "generated code shared between production and reference
transitions", but enforcement is a manual code-similarity review with no registered
instrument (REQ-TEST-048's verification method is "dependency-graph review;
code-similarity review", carried by MOD-17).

### 9.3 Shared serializers / canonicalization — F-01, F-02, F-03
`ror-reference → ror-core` is **permitted** by §10 and **not forbidden** by §14.
`ror-core` hosts R-CANON-01…11 (the 15A canonical serializer, the codec, the golden
vectors), R-KERN-01 (`CapRef`), R-CALC-01 (`Value`), R-BUDGET-01…08. A reference that
imports `ror-core` gets production serializer + identity + value + budget operands in one
edge. The reference serializer for actor messaging (15C.15) and the reference marshaller
round-trip through the same canonical 15A bytes (R-MARSHAL-03: `MarshalledValue = canonical
bytes`), so "independent marshaller" means *independent code implementing the same byte
format* — the format is genuinely shared. That is acceptable **only if** the reference has
its own 15A encoder/decoder; REQ-TEST-046 does not mandate one (F-02). `spec/10-index.json`
(`ror-reference.depends_on = 'frozen semantics only (no production core deps)'`) disagrees
with §10's permissive `ror-core` clause (V-05), so two authoritative sources disagree about
whether the reference may reach `ror-core`.

### 9.4 Shared normalization — F-04
The shared, sanctioned boundary object is the normalized `Observation` (15C.20;
REQ-REF-035) and its comparator-time re-normalization (R-REF-05; REQ-TEST-034). The
coupling risk is that the **shared `Observation`/`Observed*` schema is undeclared**
(X-29/X-84): there is no closed definition of what gets normalized or in what order, so
there is nothing to confirm both sides produce — and the comparator compares — the same
channels.

### 9.5 Shared state machines / shared state records — F-05
Reference actor/scheduler/global-state are distinct `RefActor`/`RefScheduler`/
`RefGlobalState` — good. The one place the reference consumes **production-named state
records** is the persistence boundary: `Snapshot`, `WAL`, `EffectJournal` (15C.17). The
reference recovery operates on records that are not `Ref*`-prefixed. If those records are
the production types rather than an abstract test-side semantic record, the reference's
recovered state is *derived from production record types* — shared production objects.
15C.17 says "abstract records"; REQ-TEST-045 requires semantic records from an independent
test-side decoder but gives them no distinct `Ref*` type and does not guarantee the
decoder is outside `ror-core` (ROR-008 is inside `ror-core`).

### 9.6 Shared production objects — F-01, F-04, F-05
`ror-core` is the home of the production domain objects (`Value`, `CapRef`, `EffectId`,
`ActorId`, `EffectCost`, `Consumable`, `Fault`) and the canonical codec — reachable via the
permitted edge (F-01). The reference consumes production-named persistence records
(F-05). Both sides emit the same (undeclared) `Observation`/`Observed*` test object
(F-04). Production and reference marshal through the same 15A bytes.

### 9.7 Shared authority/capability, resource/budget, scheduling — F-01
Reference capability algebra, budget, and scheduler are distinct (`RefCapabilityStore`,
`RefAuthority`, `RefConsumable`, `RefBudget`, `RefScheduler`) and independently re-stated
(REQ-REF-023/025/026). The residual coupling for all three is the single `ror-core`
allowance (F-01), which hosts the production `CapRef`, budget operands, and value domain
they are supposed to avoid. No *additional* shared-function vector is found for these
domains.

### 9.8 Shared replay logic — F-05
The reference recovery replay (15C.17 steps 5–6: "validate WAL sequence; replay records")
runs over the production-named `WAL`/`Snapshot` records; the reference host (15C.19) is a
pure trace consumer with no connection to the production `ReplayHost` (REQ-REF-034
satisfied). Replay coupling is therefore concentrated in the record/decoder boundary
(F-05) rather than in the host.

### 9.9 Shared error handling — F-06
The reference defines its **own** internal error types where it mattered —
`RefCapabilityError` (`term/02-collisions.md`: "the reference model's separate error
type"), `RefRecoveryFault` (15C.17) — while production uses `CapabilityError`,
`RecoveryFault`, `HostFault` (R-CALC-06). Good. But the **comparison** carries
`faults: Vec<ObservedFault>` (15C.20), and `ObservedFault` is undeclared (F-04); the
underlying production `Fault` taxonomy is **open** (`spec/09` U-08/U-14 record that the
`Fault`/`RecoveryFault`/`HostFault` variant sets are not closed). The "shared error
surface" at the comparison boundary therefore has no closed vocabulary: a reference that
classifies a fault differently (or emits a production `Fault` value where the reference
side is required to be independent) is exactly the "shared error handling" coupling, and
cannot be distinguished from a genuine divergence.

### 9.10 Shared verification / oracle logic — F-07
`ror-differential` co-resides with `ror-runtime` (the black-box SUT) **and** `ror-reference`
in one dependency closure (`spec/07` §6; `spec/10-index.json`; `dep/05` **HD-6** — "the
only place the production machine and `ror-reference` co-reside"). The comparator is the
one place production and reference meet; a wrong import of `ror-runtime` internals behind
the observation boundary would make oracle independence a build-graph fact instead of a
semantic one. HD-6 warns: "keep every one of these dev-dependency-only and behind the
observation interface (R-REF-05)."

### 9.11 Enforcement / tooling — F-09, F-03, F-11
The five §10 `ror-reference` crate-edge forbiddens
(`{runtime, kernel, persistence, host, agent}`) and the §14 list are present in the frozen
text but have **no tracked obligation/atomic record** (`dep/05` HD-5, V-02): "five of the
ten prohibitions … have no verification obligation at all, so the 'Cargo dependency
review' mapped to R-ARCH-04 has no enumerated checklist." The R-REF-02 *call* prohibition
is tracked (REQ-REF-004), but the *crate-edge* layer is not. Nothing fails the gate if
`ror-reference/Cargo.toml` grows a runtime/persistence/host dependency — and there is no
`Cargo.toml` to check in BOOTSTRAP. The soft `ror-core` clause (F-11) is untestable prose
that no check enforces.

---

## 10. Findings

Each finding uses the REF1 finding-record format. `Status` is the PASS/FAIL/UNVERIFIED
status of the *independence property the finding touches* (FAIL = evidence establishes an
actual violation; UNVERIFIED = the frozen contract or the repository does not contain
enough evidence to establish independence; PASS = the property is verified with no
unresolved finding). Because the repository is at BOOTSTRAP with no implemented code, no
finding here is graded BLOCKING or CRITICAL and none is FAIL: each graded severity below
reflects the demonstrated *consequence of the contract-level gap* (breadth of the
differential domain it can invalidate if exercised) rather than an executed contamination
path, and each carries `Disposition: OWNER-DECISION` or `TRACK` — none is resolved here.
`Evidence status` is a separate axis (CONFIRMED / PARTIAL / INSUFFICIENT) describing
confidence in the evidence for the claim.

### Finding: F-01
Severity: MAJOR
Category: DEPENDENCY (secondary: SERIALIZATION, TYPE-BOUNDARY, STRUCTURAL)
Status: UNVERIFIED

Claim: The frozen contract permits `ror-reference → ror-core` (and does not forbid it in
§14), and `ror-core` hosts the production `Value` domain (R-CALC-01), `CapRef`
(R-KERN-01), `ActorId`/`EffectId`, the budget operand types (R-BUDGET-*), and the 15A
canonical serializer/codec (R-CANON-*). An implementer who exercises that allowance
imports production identity/value/serializer/budget semantics in a single Cargo edge,
collapsing the distinct `RefValue`/`RefCapId`/`RefActorId`/`RefEffectId` and the
`ProductionSerializer` prohibition.

Frozen authority: `Red-on-Rust.md` §10 L39645–39651 (permissive `ror-core` clause);
§14 L39807–39828 (list omits `ror-core`); `spec/01` S-20 R-REF-02; REQ-REF-004;
REQ-TEST-048; `spec/10-index.json` (V-05 disagreement).

Reference component: `ror-reference` (MOD-14).
Production component: `ror-core` (MOD-01) — `Value`, `CapRef`, `ActorId`, `EffectId`,
`EffectCost`, `Consumable`, `Fault`, R-CANON-* 15A codec.

Dependency path: `ror-reference` → [`ror-core` — permitted by §10, un-forbidden by §14] →
production serializer + identity + value + budget + fault objects.

Coupling mechanism: §10's "may depend on the frozen primitive/domain definitions from
`ror-core` only where doing so does not accidentally import production semantics" is
prose and untestable (see F-11); §14's Cargo forbidden list omits `ror-core`; the RI-2
"PASS" is a graph-labeling result that types `MOD-14 → MOD-01` as SEMANTIC, not a
proof of type/edge independence. If an implementation imports `ror-core`, then
`ror-reference::X` calls/reuses `ror-core`'s `CapRef`, `Value`, and `CanonicalEncoder`,
which are defined by the production component `ror-core`; therefore a defect in that
production component directly determines the reference result. Two authoritative sources
disagree (`spec/10-index.json` says "no production core deps"; §10 permits `ror-core`) —
`dep/05` V-05.

Differential consequence: both — `Observe(Production(X)) = Observe(Reference(X))` (shared
value/identity/budget domains mean a reference that emits a production `Value`/`CapRef`
reproduces a production defect) and `Canonical(Recover_P(D)) = Canonical(Recover_R(D))`
(shared 15A codec in `ror-core` is the canonical encoder on both sides).

Evidence: `Red-on-Rust.md` §10 L39645–39651 and §14 L39807–39828 (verified: list contains
`ror-runtime/kernel/persistence/host` forbiddens but no `ror-core`); `spec/01` S-20;
`spec/07` §2 (R-CANON-01…11, R-CALC-01, R-KERN-01, R-BUDGET-* homed in ror-core);
`spec/10-index.json` `ror-reference.depends_on` string; `dep/05` V-05; RI-2 reasoning in
`dep/05`. Reproduction: `grep -n "ror-core" Red-on-Rust.md §10/§14`; gate
`audit/_reference_independence_checker.py` §6 REPORT F-01.

Counter-evidence: §10's clause intends to permit only *frozen primitive/domain
definitions*, not semantics; 15C.3 and REQ-REF-004/R-REF-02 do forbid calling
`Production*`; distinct `Ref*` types are *named* for the identity and value domains, and
the frozen text repeatedly instructs "where semantic independence is important, define
distinct reference types." So the coupling is permitted-but-not-required: it materializes
only if the implementer imports the wrong (semantic) subset of `ror-core`. That
dependence on an unbuilt decision is why this is MAJOR/UNVERIFIED rather than BLOCKING or
CRITICAL.

Evidence status: CONFIRMED (the permissive text, the §14 omission, and the V-05
disagreement are directly verified).

Disposition: OWNER-DECISION.

### Finding: F-02
Severity: MAJOR
Category: SERIALIZATION (secondary: RECOVERY, VERIFICATION)
Status: UNVERIFIED

Claim: REQ-TEST-046 requires `Canonical_P(v) = Canonical_R(v)` only **"where an
independent reference encoder exists for the test domain"**. The independent-encoder
requirement is conditional; if no independent encoder is built, canonical agreement can
only be asserted against the production 15A codec, and the reference is not independently
canonicalized.

Frozen authority: `req/01-registry-part8-reference-15C.md` REQ-TEST-046 (verified text);
`Red-on-Rust.md` L36809–36834 (15C.36 Canonical Serialization Differential Boundary);
`spec/01` S-20 R-REF-02; REQ-REF-002; REQ-TEST-044.

Reference component: `ror-reference` canonical encoder (independent-reference-encoder
obligation).
Production component: 15A canonical codec in `ror-core` (R-CANON-*).

Dependency path: reference canonicalization → [no mandated independent encoder] → falls
back to asserting against production `ror-core` R-CANON codec.

Coupling mechanism: the differential recovery property is evaluated by comparing
canonical bytes; `Canonical` *is* production serialization (homed in `ror-core`). Because
the requirement is conditional on an encoder that is not mandated to exist, a compliant
harness may compare reference canonical output against the production codec, so a defect
in the production codec (or in the reference's copied byte logic) is shared by both sides
and cannot be observed.

Differential consequence: `Canonical(Recover_P(D)) = Canonical(Recover_R(D))` — a false
differential PASS on the canonical-recovery domain when both sides use the same encoder.

Evidence: `grep -n -A6 "REQ-TEST-046" req/01-registry-part8-reference-15C.md` (verified
the "where an independent reference encoder exists" wording); 15C.36; R-CANON-01…11 homed
in `ror-core`. Gate §10 REPORT F-02.

Counter-evidence: REQ-TEST-044 and R-RECOV-01/04 and REQ-TEST-045 do require the reference
recovery to consume *semantic* (not production-decoded) records, so recovery *semantics*
independence is separately mandated even if byte conformance is not. The gap is therefore
bounded to the canonical-byte conformance assertion, not to recovery semantics.

Evidence status: CONFIRMED (the conditional wording is directly verified).

Disposition: OWNER-DECISION.

### Finding: F-03
Severity: MAJOR
Category: SEMANTIC (secondary: VERIFICATION, TOOLING)
Status: UNVERIFIED

Claim: The frozen source contains single **frozen production implementation** Rust blocks
(the "Phase 10 Frozen Implementation (Lambda / Call)" L18091, the "Phase 12 Frozen
Implementation … finalize_request" L23248/L23870, and the 15A codec "Corrected Rust
Implementation" L30647) that 15C.6/7/8/11 tell the reference to re-implement; 15C.38 and
REQ-TEST-048 forbid copying them into the reference, but nothing enforces it — the
verification method is a manual code-similarity review with no registered instrument.

Frozen authority: `Red-on-Rust.md` 15C.6/7/8/11, 15C.38 (L36881–36882), REQ-TEST-048;
R-REF-02.

Reference component: `ror-reference` transition / CEK / marshaller bodies.
Production component: the frozen production implementation blocks in `Red-on-Rust.md`.

Dependency path: reference transition body → (copy/adapt of) frozen production
implementation block → production semantics.

Coupling mechanism: a "reference" that adapts a frozen production block is, semantically,
production; the differential then compares two runs of the same transition machinery and
can never expose a divergence (oracle collapse). The prohibition is real in text (15C.38:
"copying production implementation bodies into the reference module", "generated code
shared between production and reference transitions") but is enforced only by a manual
code-similarity review — no registered gate measures similarity.

Differential consequence: both properties, for every transition class covered by a copied
block — a production defect in the copied transition reproduces identically in the
reference.

Evidence: `grep -n "Frozen Implementation" Red-on-Rust.md` → L18091/L20282/L23248/L30647
(verified); 15C.38 L36861–36891; REQ-TEST-048 (verified text); no code-similarity
instrument registered in `mod/17-verification.md`.

Counter-evidence: the reference is *required* to implement the same frozen semantics, so
any two conforming implementations will be *behaviorally* identical on conforming inputs;
the risk is specifically *body/type* sharing, which the text does prohibit. It is an
enforcement gap (MAJOR/UNVERIFIED), not a demonstrated shared body.

Evidence status: CONFIRMED (the blocks and the prohibition text are directly verified; the
absence of an enforcement instrument is confirmed by the gate and registry sweep).

Disposition: OWNER-DECISION.

### Finding: F-04
Severity: MAJOR
Category: NORMALIZATION (secondary: VERIFICATION, STRUCTURAL)
Status: UNVERIFIED

Claim: The comparison domain of `Observe(Production(X)) = Observe(Reference(X))` is not
closed: `pub struct Observation` (15C.20, L36170) is built from seven `Observed*` element
types (`ObservedActor`, `ObservedEvent`, `ObservedEffect`, `ObservedBudget`,
`ObservedSchedulerStep`, `ObservedFault`, `ObservedDigest`), **none of which is declared
anywhere** in the frozen source (`term/02-collisions.md` X-29/X-84;
`term/_structs.py --undeclared`), and a second, incompatible planner-facing `Observation`
shares the same name (X-06).

Frozen authority: `Red-on-Rust.md` 15C.20 L36170; `req/01-registry-part6` REQ-REF-035;
R-REF-05; REQ-TEST-033/034/042; `term/02-collisions.md` X-06, X-29, X-84
(UNDEFINED-TYPE, unresolved). No frozen requirement closes the `Observed*` domain;
`NO-DIRECT-FROZEN-AUTHORITY` for a closed schema.

Reference component: `ror-reference/observation.rs` (Observation + Observed* emission);
`ror-differential` comparator.
Production component: production `Observation` emission + the (planner-facing) homonymous
`Observation`.

Dependency path: reference observation → shared `Observation`/`Observed*` schema (the one
sanctioned boundary object) → production observation — with the schema undeclared.

Coupling mechanism: the comparison domain — what a terminal state, event, effect, budget,
fault, and digest *are* — is not closed. There is nothing to confirm both sides report,
and the comparator compares, the *same* channels. A reference that fills in a different
`ObservedFault`/`ObservedEvent` shape than production yields a false divergence (or, with
a lax comparator, a false agreement). The homonymous planner `Observation` (X-06) leaves
"the oracle shape" ambiguous.

Differential consequence: `Observe(Production(X)) = Observe(Reference(X))` is not
falsifiable because its comparison domain is undefined.

Evidence: `sed -n '36160,36172p' Red-on-Rust.md` (Observation struct, verified); repository
grep for `struct ObservedActor` etc. returns nothing (verified); `term/02-collisions.md`
X-29/X-84 (verified: "the seven `Observed*` element types … declared nowhere"); X-06
(verified); `python3 term/_structs.py --undeclared`. Gate §7 REPORT F-04.

Counter-evidence: the *intent* is explicit — `Observation` is a test representation, "not a
runtime serialization format", and "must not become a third semantic wire protocol"
(15C.20). The shared schema is the one sanctioned boundary object. The finding is that the
schema is *undeclared*, not that sharing it is impermissible.

Evidence status: CONFIRMED (the undeclared types and the homonym are directly verified).

Disposition: OWNER-DECISION.

### Finding: F-05
Severity: MAJOR
Category: RECOVERY (secondary: TYPE-BOUNDARY, SERIALIZATION)
Status: UNVERIFIED

Claim: Reference recovery consumes **production-named** records `Snapshot`, `WAL`,
`EffectJournal` (15C.17, L36061) with **no `Ref*` prefix** — unlike every other reference
domain — and the "independent test-side decoder" that REQ-TEST-045 requires is an
`ror-core` code path (ROR-008 of R-CANON-07) in the one crate the reference may import.

Frozen authority: `Red-on-Rust.md` 15C.17 L36057–36110, 15C.19; REQ-REF-032;
REQ-TEST-045 (verified text); R-RECOV-01/04; R-DUR-04.

Reference component: `ror-reference` recovery (`RefGlobalState`, `RefRecoveryResult`).
Production component: `Snapshot`/`WalRecord`/`EffectJournal` + the ROR-008 test-side
decoder in `ror-core`.

Dependency path: reference recovery → production-named `Snapshot`/`WAL`/`EffectJournal`
records → (independent test-side decoder, ROR-008) → `ror-core` R-CANON codec path.

Coupling mechanism: the reference's recovered state is described as derived from records
that carry production names and, at least in one reading, production types; the decoder
that turns the durable byte image into the semantic records the reference consumes is an
`ror-core` code path in a crate the reference may import (F-01). If the decoder is
production, a production decoding defect propagates into the reference's recovered state
before any recovery logic runs.

Differential consequence: `Canonical(Recover_P(D)) = Canonical(Recover_R(D))` — recovery
independence is not guaranteed outside `ror-core`; a shared decoder can make both sides
recover the same (incorrect) state.

Evidence: `sed -n '36057,36110p' Red-on-Rust.md` (verified: "consumes abstract records
representing: Snapshot, WAL, EffectJournal"); REQ-TEST-045 (verified); ROR-008 as the
R-CANON-07 independent code path; gate §8 REPORT F-05.

Counter-evidence: 15C.17 says "abstract records" and REQ-TEST-045 *requires* the reference
recovery to receive "semantic records from an independent test-side decoder" and NOT to
consume "the production snapshot decoder or production WAL parser". The production *names*
may denote abstract semantic records (concepts T-48 `Snapshot`, etc.) rather than the
production types. The finding is that the records/decoder are not given a distinct `Ref*`
type nor guaranteed to live outside the importable crate.

Evidence status: PARTIAL (the production-named records are directly verified; whether they
denote production types or abstract records is itself the unresolved ambiguity).

Disposition: OWNER-DECISION.

### Finding: F-06
Severity: MINOR
Category: SEMANTIC (secondary: NORMALIZATION, VERIFICATION)
Status: UNVERIFIED

Claim: `ObservedFault` (undeclared; F-04) sits over an **open** production `Fault`
taxonomy (R-CALC-06; `spec/09` U-08/U-14 record that the `Fault`/`RecoveryFault`/
`HostFault` variant sets are not closed). The comparison fault vocabulary is not closed, so
shared error semantics at the comparison boundary cannot be excluded.

Frozen authority: `Red-on-Rust.md` 15C.20; R-CALC-06; `spec/09` U-08/U-14;
`term/02-collisions.md` X-29/X-84. No frozen requirement closes the `Fault`/`ObservedFault`
vocabulary; `NO-DIRECT-FROZEN-AUTHORITY` for a closed fault domain.

Reference component: reference fault classification into `ObservedFault`.
Production component: `Fault`/`RecoveryFault`/`HostFault` (R-CALC-06), open taxonomy.

Dependency path: reference fault emission → `ObservedFault` → production `Fault`
taxonomy (open) → comparator.

Coupling mechanism: with no closed fault vocabulary, a reference that emits a production
`Fault` value (or classifies an interruption differently than production) is a shared-error
coupling that the comparator cannot distinguish from a genuine divergence.

Differential consequence: `Observe(Production(X)) = Observe(Reference(X))` over the `faults`
channel.

Evidence: `term/02-collisions.md` (RefCapabilityError is the reference's separate error
type — good; the *comparison* `ObservedFault` is undeclared); `spec/09` U-08/U-14; R-CALC-06.
Gate §7 REPORT F-04 (ObservedFault undeclared).

Counter-evidence: the reference defines its own *internal* fault types where it matters
(`RefCapabilityError`, `RefRecoveryFault`), and the audit finds no production error *type*
is reused inside the reference semantics. The residual risk is confined to the comparison
`faults` channel and is largely a consequence of F-04's undeclared schema — hence MINOR,
not MAJOR.

Evidence status: PARTIAL (internal error types are distinct — verified; the comparison
vocabulary is open — verified; an actual shared error *value* is not demonstrated).

Disposition: TRACK.

### Finding: F-07
Severity: MINOR
Category: VERIFICATION (secondary: TOOLING, STRUCTURAL)
Status: UNVERIFIED

Claim: `ror-differential` co-resides with `ror-runtime` (the black-box SUT) and
`ror-reference` in one dependency closure; if it ever imports `ror-runtime` internals
behind the observation boundary, oracle independence becomes a build-graph fact.

Frozen authority: `spec/07` §6; `spec/10-index.json`; `dep/05` HD-6 ("the only place the
production machine and `ror-reference` co-reside"); R-REF-05. HD-6 is a recorded
violation, not a resolved decision.

Reference component: `ror-differential` comparator / harness.
Production component: `ror-runtime` (black-box SUT) internals.

Dependency path: `ror-differential` → (potential import of) `ror-runtime` internals →
production.

Coupling mechanism: the comparator is the one place the two sides meet. If it imports
`ror-runtime` internals rather than reading only the emitted `Observation_R`, a defect
inside the SUT reaches the comparator and can normalize both sides onto the production
answer, collapsing the oracle at the build-graph level. HD-6 requires these edges stay
dev-dependency-only and behind the observation interface (R-REF-05).

Differential consequence: both — any wrong import in the comparator couples the
comparison itself to production internals.

Evidence: `dep/05` HD-6; `spec/07` §6; `spec/10-index.json`
(`ror-differential.depends_on = 'ror-runtime (black box)'`); no current import of
`ror-runtime` internals in any Rust source (none exists).

Counter-evidence: the frozen text and HD-6 explicitly constrain the comparator to the
observation interface; there is currently no code to violate that, so the finding is a
guarded, conditional risk.

Evidence status: CONFIRMED for the co-residence build-graph fact; INSUFFICIENT for any
actual wrong import (no code exists).

Disposition: TRACK.

### Finding: F-08
Severity: MINOR
Category: TYPE-BOUNDARY (secondary: STRUCTURAL, GOVERNANCE)
Status: UNVERIFIED

Claim: `RefCapId`/`RefActorId`/`RefEffectId` are declared **twice** in the frozen source
(L35471–35473, 15C.4 and L39664–39666, §10), with no linkage and no ownership-register
(D-) entry; two authoritative declarations can drift and break the identity correspondence
REQ-REF-036 needs.

Frozen authority: `Red-on-Rust.md` 15C.4 L35471–35473; §10 L39664–39666; REQ-REF-036.
The unmarked duplication itself is an ownership-register gap (D-01…D-12) with
`NO-DIRECT-FROZEN-AUTHORITY` for the linkage.

Reference component: the three `Ref*Id` newtypes (two declaration sites).
Production component: none directly — this is internal to the reference identity
declarations.

Dependency path: reference identity declaration (15C.4) vs. reference identity declaration
(§10) — a duplicate-authority path internal to the reference, with no link.

Coupling mechanism: a reference built from one declaration and a differential scrutinee
read from the other can disagree about the identity representation (e.g. one gains a field),
breaking the deterministic identity correspondence the harness relies on. It is a drift
risk, not a current aliasing of `Ref*Id` to a production identity type.

Differential consequence: `Observe(Production(X)) = Observe(Reference(X))` via the identity
allocation/correspondence channel (REQ-REF-036).

Evidence: `grep -n "pub struct RefCapId" Red-on-Rust.md` → L35471 and L39664 (verified:
two identical declarations); both currently identical; no D-entry. Gate §9 REPORT F-08
("pub struct RefCapId appears 2x").

Counter-evidence: both declarations are currently byte-identical, so there is no present
divergence; the gate confirms exactly two occurrences and both match.

Evidence status: CONFIRMED (duplication verified); the *consequence* (drift) is a future
risk, hence MINOR.

Disposition: TRACK.

### Finding: F-09
Severity: MAJOR
Category: TOOLING (secondary: GOVERNANCE, VERIFICATION)
Status: UNVERIFIED

Claim: The `ror-reference` crate-edge forbiddens (the five in §10 —
`ror-runtime/kernel/persistence/host/agent` — and the four in §14's Cargo block) have **no
tracked obligation/atomic record**; the R-REF-02 *call* prohibition is tracked
(REQ-REF-004) but the *crate-edge* layer is not. Nothing fails the gate if
`ror-reference/Cargo.toml` grows a runtime/persistence/host dependency.

Frozen authority: `Red-on-Rust.md` §10 L39645–39651; §14 L39807–39828; R-ARCH-04;
`dep/05` HD-5, V-02 (verified text: "five of the ten prohibitions … have no verification
obligation at all"). These edges are hard structural predicates in the frozen text; the
missing obligation is the enforcement gap.

Reference component: `ror-reference` crate boundary.
Production component: `ror-runtime`, `ror-kernel`, `ror-persistence`, `ror-host`,
`ror-agent`.

Dependency path: (future) `ror-reference/Cargo.toml` → a forbidden production crate — not
prevented by any tracked obligation or gate.

Coupling mechanism: the dependency review mapped to R-ARCH-04 has no enumerated checklist
for the exact edges that carry the independence; the five §10 forbiddens are present in
prose but not carried by a REQ-* record with a verification method, so a build that adds a
forbidden edge would not trip a requirement-level gate.

Differential consequence: both — a forbidden edge is the structural precondition for the
couplings in F-01/F-05.

Evidence: `dep/05` HD-5, V-02 (verified); `grep` over `req/` for records citing
L39807–39828 finds none (gate §11 REPORT F-09 confirms the §14 line range is cited by no
REQ-* record).

Counter-evidence: the frozen *text* does forbid the edges (§10/§14) and REQ-REPO-014
("ror-reference … with no production dependencies") carries part of the prohibition
(`dep/05` L84); the gap is that the enumerated edge list is not itself an obligation with
a mechanical check — enforcement, not norm, is missing.

Evidence status: CONFIRMED (absence of obligation records and gate coverage is directly
verified).

Disposition: OWNER-DECISION.

### Finding: F-10
Severity: MINOR
Category: GOVERNANCE (secondary: VERIFICATION)
Status: UNVERIFIED

Claim: `audit/_conservation_checker.py` is an executable budget/transition model
(Op-01…Op-22) that lives **outside the frozen `ror-reference` contract** and outside
R-REF-02's forbidden list; its arithmetic is not exact-matched to R-BUDGET-02 and it is not
differentially tested against either side.

Frozen authority: none of the frozen §15C text governs this Python file; it is registered
as a *checker* (`check.py`) and self-describes as a meta-checker for Op-01…Op-22. It is not
part of the reference model and R-REF-02 does not govern it —
`NO-DIRECT-FROZEN-AUTHORITY` for its status as an oracle.

Reference component: none (standalone file) — risk is to the *future* reference oracle.
Production component: the budget/transition rules (Op-01…Op-22) it models.

Dependency path: `audit/_conservation_checker.py` → (if adopted/copied as the reference
oracle) → production-influenced budget semantics — currently no edge.

Coupling mechanism: it is a *third* semantic model, neither production nor the sanctioned
reference, using Python `int` and `sys.exit` on underflow vs. the frozen `checked_sub` /
no-saturating R-BUDGET-02. If adopted as the reference oracle (or its constants copied in),
it becomes an un-governed oracle whose arithmetic is unaudited for exactness → potential
false-negative differential oracle.

Differential consequence: if adopted, both properties' budget/conservation channels are
evaluated by a model of unknown fidelity.

Evidence: `audit/_conservation_checker.py` header and `check.py` registration; R-BUDGET-02
(`checked_sub`, no saturation) differs from Python `int`/`sys.exit` behavior.

Counter-evidence: it shares code with nothing and is not currently a coupling; the risk is
entirely contingent on future adoption. Hence MINOR/UNVERIFIED rather than a confirmed
defect.

Evidence status: CONFIRMED for the file's existence and standalone status; the coupling
scenario is hypothetical (PARTIAL for consequence).

Disposition: TRACK.

### Finding: F-11
Severity: MAJOR
Category: TYPE-BOUNDARY (secondary: DEPENDENCY, GOVERNANCE)
Status: UNVERIFIED

Claim: "May depend on the frozen primitive/domain definitions from `ror-core` **only where
doing so does not accidentally import production semantics**" is an untestable,
prose-only qualifier that no check enforces; it is the mechanism that makes F-01 possible.

Frozen authority: `Red-on-Rust.md` §10 L39645–39651 (verified wording); `spec/10-index.json`
(the `'frozen semantics only (no production core deps)'` string, which V-05 notes is not
even a crate name). No frozen requirement operationalizes "accidentally."

Reference component: `ror-reference` dependency decision.
Production component: `ror-core` domain/primitive definitions.

Dependency path: `ror-reference` → [subjective "does not accidentally import" judgment] →
`ror-core` production semantics.

Coupling mechanism: the qualifier is a judgment, not a predicate; no obligation or checker
decides, for any concrete import, whether it "accidentally imports production semantics."
Two authoritative sources disagree about whether the edge is allowed at all (V-05). This
subjective gate is what lets the F-01 coupling through without tripping a requirement.

Differential consequence: both — enabling F-01's shared value/identity/serializer coupling.

Evidence: `sed -n '39645,39651p' Red-on-Rust.md` (verified wording); `spec/10-index.json`;
`dep/05` V-05; gate does not check this clause (RI-1…4 operate on the typed module graph
only).

Counter-evidence: the phrase expresses a real intent to permit only semantics-free
primitive/domain definitions and to keep the reference's semantic machinery independent;
15C.3/R-REF-02/REQ-REF-004 carry the call prohibitions. The gap is that intent is not
operationalized.

Evidence status: CONFIRMED (the untestable wording and the V-05 disagreement are directly
verified).

Disposition: OWNER-DECISION.

---

## 11. Differential-testing impact

If any of F-01…F-11 materializes, the differential test can produce a **false PASS** (the
same defect on both sides because of shared machinery) or become **unfalsifiable** (an
undeclared comparison domain). The impact is concentrated in three clusters:

1. **The `ror-core` cluster (F-01, F-02, F-11).** If `ror-reference` may reach `ror-core`
   for value/identity/budget/canonical-codec semantics, the distinct-identity guarantee and
   the shared-serializer prohibition collapse in one Cargo edge; canonical recovery
   equality then cannot be evaluated independently (the canonical encoder is conditional).
   This is the largest single threat to **both** differential properties.
2. **The undeclared-domain cluster (F-04, F-06).** `Observation` and its seven `Observed*`
   element types are never declared and the name is homonymous (X-06); the fault vocabulary
   is open. `Observe(Production(X)) = Observe(Reference(X))` is unfalsifiable until the
   comparison domain is a closed, declared type.
3. **The enforcement cluster (F-03, F-09, F-07, F-05, F-08, F-10).** The crate-edge and
   code-similarity reviews are manual; the forbidden crate edges are untracked by any
   obligation; the comparator co-resides with the SUT; recovery consumes production-named
   records; the identity newtypes are duplicated; a third semantic model exists in-repo.
   `check.py` passing today does **not** assert the reference is independent.

No finding here, taken alone, is graded BLOCKING because none demonstrates an *executed*
contamination path in a repository with no implementation; but the union of F-01/F-02/F-04
is sufficient, if left open through implementation, to invalidate both differential
properties.

## 12. Residual uncertainties

1. **BOOTSTRAP state.** No code, no Cargo workspace, no tests. All coupling assessments
   are of the *contract*, not of a build. The audit cannot observe whether the reference
   "actually" imports `ror-core` or shares a body, because neither exists.
2. **The `ror-core` allowance semantics.** Whether "frozen primitive/domain definitions"
   from `ror-core` includes the 15A codec / `CapRef` / `Value` is unresolved by the frozen
   text; the two authoritative sources disagree (V-05).
3. **The `Snapshot`/`WAL`/`EffectJournal` record identity.** Whether 15C.17's production
   names denote abstract test-side semantic records or the production types is the open
   ambiguity behind F-05.
4. **Closedness of `Fault` and `Observed*`.** The comparison domain and fault vocabulary
   are not closed (F-04, F-06); whether a later addendum declares them (resolving X-06/
   X-29/X-84) is outside this audit's authority.
5. **Reconciliation hiding divergence.** Whether external-effect reconciliation can absorb
   a genuine recovery divergence into `AwaitingReconciliation` is only partially bounded by
   R-RECOV-07/08; the crash-consistency gate verifies the rule set, not the independence of
   the reconciliation oracle.

## 13. Verification status

### 13.1 Per-property PASS/FAIL/UNVERIFIED

The statuses below apply the REF1 addendum PASS/FAIL/UNVERIFIED criteria. PASS requires
*all eight* listed conditions including demonstrated no-reuse/no-indirect-dependency and
concrete repository evidence; FAIL requires evidence of an *actual* violation. A textual
assertion of independence is not PASS evidence.

| Independence property | Frozen authority | Status | Basis |
|---|---|---|---|
| Call-edge prohibition of the ten `Production*` surfaces | 15C.3; R-REF-02; REQ-REF-004; REQ-TEST-048 | **PASS** (call-edge layer) | Hard predicates present in text + gate-verified; no reference code exists to call them. |
| No forbidden `ror-reference` crate edge (runtime/kernel/persistence/host/agent) | §10 L39645; §14 L39807 | **PASS** at text layer; **UNVERIFIED** at enforcement layer | Text forbids them (gate-verified); but no tracked obligation/gate would catch a violation (F-09) and no Cargo exists. |
| `ror-reference` does not acquire production semantics via `ror-core` | §10 (permissive clause) | **UNVERIFIED** | Edge permitted + §14 omits it + clause untestable (F-01, F-11); V-05 disagreement. |
| Distinct identifiers `RefCapId`/`RefActorId`/`RefEffectId` genuinely distinct | 15C.4; §10; REQ-REF-036 | **PASS** with advisory drift risk | Distinct names, conversion banned, no alias/shared constructor found (F-08 advisory). |
| `Observe(Production(X)) = Observe(Reference(X))` well-defined & independent | 15C.1/20/22; R-REF-01/05; REQ-REF-001/035 | **UNVERIFIED** | Comparison domain undeclared + homonym (F-04, F-06); no implementation. |
| `Canonical(Recover_P(D)) = Canonical(Recover_R(D))` well-defined & independent | 15C.1/17/35/36; R-REF-01; REQ-REF-002; REQ-TEST-044/045/046 | **UNVERIFIED** | Independent encoder conditional (F-02); records/decoder `ror-core`-bound (F-01, F-05); no implementation. |
| Anti-oracle-collapse rules stated | 15C.38; REQ-TEST-048 | **PASS** (statement); **UNVERIFIED** (enforcement) | Text present (gate-verified); enforcement manual only (F-03). |

### 13.2 Gate evidence

`python3 check.py` was run **before** this audit integration and is green (13 checkers
PASS, incl. `audit/_reference_independence_checker.py`, `dep/_graph.py`, all registry /
term / conservation gates), and was run **after** the integration and remains green. No
existing gate was weakened to obtain a passing result. The checker does not consume this
audit document, so the document restructure neither produces nor masks a gate outcome. A
green gate verifies the hard *presence/structural* predicates; it is **not** by itself
proof of semantic independence (each advisory coupling vector F-01…F-09 is reported by the
gate without failing, because none is a resolved decision).

## 14. Final audit verdict

**Verdict: `REF1-CONDITIONAL`.**

Rationale, derived from the individual findings (not from a count):
- **Not REF1-PASS:** multiple required independence properties are UNVERIFIED
  (observation-equivalence, recovery-equivalence, no-production-semantics-via-`ror-core`,
  crate-edge enforcement) and several findings (F-01…F-05, F-09, F-11) remain open. The
  PASS conditions — "no indirect dependency that can cause production semantics to
  determine reference behavior," "the differential property has a defined comparison
  domain," "no unresolved finding remains that could invalidate the property" — are not
  met, and in a BOOTSTRAP repository they cannot be demonstrated.
- **Not REF1-FAIL:** no finding is a **confirmed BLOCKING** coupling demonstrating oracle
  contamination. FAIL requires evidence that the reference actually reuses a prohibited
  production component or that an indirect dependency actually determines the reference
  result; no such executed dependency exists because no code exists. The coupling vectors
  are *permitted-or-unspecified by the contract*, not *present in a build*. Per the
  addendum, UNVERIFIED is not converted into FAIL without evidence of an actual violation,
  and none is established.
- **Not REF1-INDETERMINATE:** the repository does contain sufficient evidence to determine
  *what* the potentially blocking coupling vectors are (F-01/F-02/F-04 are concrete,
  located, and mechanism-specified). The uncertainty is about whether they *materialize*
  under an unbuilt implementation, which is a CONDITIONAL-class gap, not a state of
  insufficient evidence to identify the couplings.

The frozen Phase 15C *states* the independence boundary and the two differential
properties carefully — the `Ref*` renaming discipline, the distinct reference error types,
the explicit "no conversion from `CapRef` to `RefCapId`", the anti-oracle-collapse rules,
and the four-track oracle separation are internally consistent **at the call-edge level**.
But the boundary is leak-prone at the type/edge level and is concentrated in `ror-core`
(F-01/F-11), and the two differential properties are not yet *falsifiable* because their
comparison domain is undeclared (F-04/F-06) and the independent canonical encoder is only
conditional (F-02). Therefore the reference model is **not yet demonstrably independent
enough to serve as an oracle**, and the couplings that could invalidate differential
testing are fully reported above and preserved for owner decision. No normative change is
issued by this audit (R-SCOPE-03).
