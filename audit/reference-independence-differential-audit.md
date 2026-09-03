# Reference Independence & Differential-Coupling Audit

**Status:** AUDIT — verification, gap classification, and dependency register only.
No new frozen text is issued (R-SCOPE-03). This document audits whether the frozen
independent reference model (`Ref`/MOD-14, Phase 15C in `Red-on-Rust.md`) is
specified to be semantically independent of production, whether the two differential
properties (`Observe(Production(X)) = Observe(Reference(X))` and
`Canonical(Recover_P(D)) = Canonical(Recover_R(D))`) are well-posed and checkable, and
**reports every dependency — specification-layer or enforcement-layer — that could
invalidate differential testing.**

**Scope boundary.** This repository is at the state the frozen source itself calls
**BOOTSTRAP** (`spec/07` §1): there is **no Cargo workspace, no crate, no Rust source,
no test, no CI**. Every requirement is `SPECIFIED`; none is `IMPLEMENTED`. The Rust
blocks in `Red-on-Rust.md` are normative specification artifacts, not repository code.
Consequently this audit is of the **specification and of the machinery that would
enforce it** (the typed dependency graph, the registry checks, the conservation
checker). It cannot execute `Observe_P = Observe_R` — neither side exists — and it does
**not** claim the differential property holds. It reports where the specification
leaves the boundary leak-prone and where the enforcement gates do not actually gate.

**Primary anchors:** `Red-on-Rust.md` L35272–37168 (frozen Phase 15C), §10
L39645–39651, §14 L39807–39828; `spec/01` S-20 (R-REF-01/02/03/04) and S-21
(R-REF-05, R-TEST-*); `spec/07` §2/§6 (crate map + dependency direction);
`spec/10-index.json`; `req/01-registry-part6-verification.md` (REQ-REF-001…009/017),
`req/01-registry-part8-reference-15C.md` (15C.1–15C.46); `mod/14-reference.md`,
`mod/15-differential.md`; `dep/05-violations.md` (RI-1…4, HD-5, HD-6, V-02); and
`term/02-collisions.md` (X-06, X-29, X-84).

**Mechanical gate.** `dep/_graph.py` (run by `check.py`) already asserts, at the
**module/graph layer**, that no implementable-kind edge joins MOD-14 to a production
module (RI-1…RI-4) and that no production module takes an implementable dependency on a
verification node. It is a **specification-graph** check; it is **not** a `Cargo.toml`
check (no Cargo exists) and it does **not** audit the soft `ror-reference → ror-core`
clause that this audit flags. `audit/_conservation_checker.py` independently re-derives
budget-conservation transitions in Python; it is part of the background, not a check on
this boundary (see F-10).

---

## 0. Decision keys used in this audit

| Term | Meaning used here |
|---|---|
| **production** | The ten `Production*` surfaces + the frozen crate DAG `ror-core/compiler/kernel/runtime/persistence/host/agent` that implement them. |
| **reference** | The independent model in Phase 15C — `RefValue`, `RefEnv`, `RefState`, `RefCapabilityStore`, `RefBudget`, `RefActor`, `RefScheduler`, `RefGlobalState`, `RefHost`, `RefRecoveryResult`, with identifiers `RefCapId`/`RefActorId`/`RefEffectId` (`ror-reference`). |
| **shared at the external test boundary** | The one sanctioned place the reference may share *code and semantic constants* with production (15C.3 opening: "only where unavoidable at the external test boundary"). |
| **coupling** | Any dependency — a Cargo edge, a type name, a helper function, a normalization/classification rule, a record/error type, a shared computation — that makes the reference's answer a *function of* production's answer rather than of the frozen semantics. |
| **oracle collapse** | The case where the same bug, or the same implementation body, sits behind both sides of the comparison, so disagreement can never be observed. |
| **verification layer** | MOD-14…MOD-17 (`ror-reference`, `ror-differential`, `ror-testkit`, `tests/`). |

Two distinctions drive the findings:

1. **A specification dependency is legal; an implementation dependency is not.**
   The reference *must* re-model the frozen semantics (SEMANTIC_DEPENDENCY, rule
   R3-reference-mirror), so the 12 edges `MOD-14 → MOD-01…MOD-12` are expected. The
   question is whether any of them can *become* a code/type/serializer dependency.
2. **A shared *type* is as coupling as a shared *function*.** The frozen text bans
   "calls" (`Production*` and `reference_*() → production_*()`), which is a **call-edge**
   prohibition. It does **not** by itself ban shared *types*, shared *schemata*, or
   shared *records* — which is where the silent coupling lives.

---

## 1. The four requested verifications

### 1.1 The independence boundary (ten forbidden production surfaces) — **PARTIALLY SATISFIED**

The ten enumerated call surfaces are prohibited at both the requirement level and the
anti-oracle-collapse level:

| Forbidden surface | Where prohibited | Enforced? |
|---|---|---|
| `ProductionEvaluator` | 15C.3; R-REF-02; REQ-REF-004; REQ-TEST-048 | graph RI-2 (SEMANTIC only) |
| `ProductionContinuation` | 15C.3; R-REF-02; REQ-REF-004 | graph RI-2 |
| `ProductionCapabilityKernel` | 15C.3, 15C.8 ("never called"); R-REF-02; REQ-REF-004 | graph RI-2 |
| `ProductionBudget` | 15C.3, 15C.10; R-REF-02; REQ-REF-004 | graph RI-2 |
| `ProductionScheduler` | 15C.3, 15C.13; R-REF-02; REQ-REF-004 | graph RI-2 |
| `ProductionSerializer` | 15C.3, 15C.15; R-REF-02; REQ-REF-004 | graph RI-2 |
| `ProductionRecovery` | 15C.3, 15C.17 ("must not call Recover/Replay/CanonicalDecode"); R-REF-02; REQ-REF-004 | graph RI-2 |
| `ProductionPersistence` | 15C.3, 15C.17; R-REF-02; REQ-REF-004 | graph RI-2 |
| `ProductionReplayHost` | 15C.3, 15C.19 ("no connection to the production `ReplayHost`"); R-REF-02; REQ-REF-004 | graph RI-2 |
| `ProductionTransition` | 15C.3; R-REF-02; REQ-REF-004; REQ-TEST-048 | graph RI-2 |

**PASS at the call-edge level, FAIL at the type/edge level.** The function-call
prohibition is closed and tracked (REQ-REF-004, REQ-TEST-048). But the **crate-edge**
prohibition has a hole (F-01) and the reference is **allowed** to depend on `ror-core`
(F-01, F-03). See §3.

### 1.2 Distinct identifiers `RefCapId` / `RefActorId` / `RefEffectId` — **SATISFIED with a duplication hazard**

The reference identifiers are declared as distinct newtypes from the production
identifiers and the conversion is explicitly banned:

- Reference: `pub struct RefCapId(pub u64); pub struct RefActorId(pub u64);
  pub struct RefEffectId(pub u64);` (15C.4, `Red-on-Rust.md` L35471–35473).
- Production: `CapRef` (R-KERN-01; a struct, in places `{index, generation}`),
  `ActorId(pub u64)` (R-ACTOR-03), `EffectId(pub u64)` (R-CALC-04).
- 15C.4: "No conversion from a production `CapRef` into `RefCapId` is permitted inside
  the reference semantics. Identifiers are mapped only at the harness boundary when
  constructing equivalent initial states."

**Caveat — duplicated declaration (F-08):** the same three `Ref*Id` structs are declared
**twice** in the frozen source: L35471–35473 (15C.4) and L39664–39666 (§10 crate
contract). Both must stay identical; nothing links them, so they can drift. The value
and reference models satisfy the *spirit*, but the duplication is exactly the kind of
unmarked restatement the ownership register (D-01…D-12) warns about, and it is **not**
registered (no D-entry).

### 1.3 `Observe(Production(X)) = Observe(Reference(X))` — **SPECIFIED, NOT VERIFIED, with a schema hole**

The property is normative (15C.1 boxed; REQ-REF-001, 15C.45 REQ-TEST-055; R-REF-01).
Checkability rests on:
- Both sides emit a *normalized* `Observation` (REQ-REF-035) — a **test** representation,
  explicitly "not a runtime serialization format" and "must not become a third semantic
  wire protocol" (15C.20).
- Comparison levels / trace normalization / first-divergence (R-REF-05, REQ-TEST-033/034,
  REQ-TEST-042).

**Hole — the comparison domain is undeclared (F-04):** `pub struct Observation` (15C.20,
L36170) is built from **seven `Observed*` element types** (`ObservedActor`,
`ObservedEvent`, `ObservedEffect`, `ObservedBudget`, `ObservedSchedulerStep`,
`ObservedFault`, `ObservedDigest`) **none of which is declared anywhere** in the frozen
source (`term/02-collisions.md` X-29; `term/_structs.py --undeclared` returns 69 names,
of which X-29/X-84 record these). The exact comparison domain — what a "terminal state",
an "event", an "effect", a "budget", a "fault", a "digest" *is* — is therefore **not
closed**. A reference that fills in a different `ObservedFault`/`ObservedEvent` shape
than production *will* produce a false divergence (or, with a lax comparator, a false
agreement). X-06 (`term/02-collisions.md` L437–460) records that a **second, incompatible
`Observation` struct** (the planner-facing one, L27156) shares the same name; the
dictionary disambiguates in prose only (T-54 vs T-57) and `spec/05` §5 lists only the
differential sense (a gap X-06 itself flags). Both are called `Observation` conceptually
"the oracle shape" is unspecified — see F-04.

### 1.4 `Canonical(Recover_P(D)) = Canonical(Recover_R(D))` subject to external-effect reconciliation — **SPECIFIED, NOT VERIFIED, with a shared-serializer dependency**

The property is normative (15C.1 boxed; REQ-REF-002; REQ-TEST-044; R-RECOV-01/04).
"Subject to explicit external-effect reconciliation" is realized by R-RECOV-07/08
(reconciliation is the only resolver of `Indeterminate`; never auto-`NotExecuted`) and by
R-DUR-04 (the `Prepared ∧ ¬Issued ⇒ Discard` / `Issued ∧ ¬Completed ⇒ Indeterminate`
critical rule). Both are present (the crash-consistency audit gate verifies them).

**Hole — `Canonical` is production's serializer and the reference is allowed to reach it
(F-01, F-03):**
- `Canonical` is the frozen 15A canonical codec, homed in **`ror-core`** (`spec/07` §2:
  R-CANON-01…11), i.e. it is *production* serialization.
- The reference is forbidden to *call* `ProductionSerializer` (R-REF-02) yet must
  **reproduce** the same canonical bytes. REQ-TEST-046 makes the independent-encoder
  requirement **conditional**: "where an independent reference encoder exists for the test
  domain, `Canonical_P(v) = Canonical_R(v)` is required." The **"where"** is the gap — if
  no independent encoder is built, byte-level agreement can only be asserted against the
  *production* 15A codec, which is precisely the shared-serializer coupling the boundary
  forbids, and the reference is then not independently canonicalized.
- The reference recovery engine consumes "abstract records representing `Snapshot`, `WAL`,
  `EffectJournal`" (15C.17, L36061) — **production-named** records, with **no `Ref*`
  prefix**, in a model that renames *every other* domain (`RefValue`, `RefEnv`, `RefState`,
  `RefCapabilityStore`, `RefBudget`, `RefActor`, `RefScheduler`, `RefGlobalState`,
  `RefHost`, `RefReceipt`). This is a concrete "shared production object" vector (F-05).

---

## 2. Semantic-coupling sweep — every category the audit was asked to search

> The frozen 15C.3 and 15C.38 texts *state* the prohibitions; the question is whether the
> *types, records, schemata and machinery* let the prohibitions be bypassed. Each row below
> reports what is shared and what it invalidates.

### 2.1 **Shared helpers** — F-10

`audit/_conservation_checker.py` is an **executable** encoding of the budget/resource
transition semantics (Op-01…Op-22: `op_01_pure_ast_step`, `op_12_atomic_mailbox_enqueue`,
`op_13_receive_dequeue`, `op_14_yield`, `op_15_actor_halt`, `op_16_effect_request`,
`op_18_effect_completion`, `op_19_host_failure`), with its own `Consumables`, `Reserved`,
`PersistentStorage`, `TaggedExplicitResources`, `ActorBudgetState` and a conservation
verifier. It does **not** share code with anything (it is standalone), so it is not itself
a coupling. But it is an **independent executable semantic model of the budget/transition
rules that lives outside the frozen `ror-reference` contract** and outside R-REF-02's
forbidden list. Status and relationships:
- It is registered as a *checker* (`check.py`) and documents itself as a
  "Meta-Checker for Op-01...Op-22", i.e. a **test harness**, not the `ror-reference` oracle.
- It implements resource arithmetic that **differs** from the frozen Rust model in
  principle (Python `int`, `sys.exit` on underflow vs. the frozen `checked_sub`,
  no-saturating law R-BUDGET-02) and is **not** differential-tested against either side.
- **Risk to differential testing:** if this file is ever adopted as the reference oracle
  for budget/conservation (or its constants are copied into the reference), it becomes a
  *third* semantic model that is neither production nor the sanctioned reference, and its
  arithmetic is un-audited for exactness against the frozen rules. For the differential
  property this is a **governance** gap: the repo already contains "semantics in Python"
  that the frozen boundary does not govern. **Severity: MEDIUM.**

### 2.2 **Shared transition functions** — F-03 / inherent to a shared specification

15C.6/15C.7 require the reference to "implement the **frozen Phase 10 rules**", and
15C.8 the "frozen Phase 11 algebra", 15C.11 the "frozen Phase 12 issuance sequence".
That is correct — both sides implement the *same specification*. The hazard is that the
frozen source also contains single **frozen production implementation** Rust blocks — the
"Phase 10 Frozen Implementation (Lambda / Call)" (`Red-on-Rust.md` L18091), the "Phase 12
Frozen Implementation … `finalize_request`" (L23248/L23870), and the 15A canonical codec
("Corrected Rust Implementation", L30647). If the reference is implemented by
copying/adapting one of these blocks, the "reference" is production.
This is prohibited by 15C.38 ("copying production implementation bodies into the
reference module", "generated code shared between production and reference transitions"),
but it is a **manual-review** prohibition — there is no automated code-similarity gate, and
REQ-TEST-048's verification method ("dependency review; code-similarity review") is
carried by MOD-17 with no registered instrument. **Severity: HIGH (enforcement gap).**

### 2.3 **Shared serializers** — F-01, F-03

- `ror-reference → ror-core` is **permitted** by §10 and **not forbidden** by §14.
  `ror-core` hosts **R-CANON-01…11** (the 15A canonical serializer, the codec, the
  golden vectors), **R-KERN-01** (`CapRef` type), **R-CALC-01** (`Value` domain),
  **R-BUDGET-01…08** (budget operand types). A reference that imports `ror-core` gets the
  production serializer + production identity types + production value domain in one edge.
- The reference **serializer for actor messaging** (15C.15) and the reference
  **marshaller** both round-trip through the **same canonical 15A bytes** (`R-MARSHAL-03`:
  `MarshalledValue = canonical bytes`; `unmarshal(marshal(v)) = v`). "Independent
  marshaller" therefore means *independent code implementing the same byte format* — the
  format itself is genuinely shared. That is acceptable at the boundary, but only if the
  reference has its **own** 15A encoder/decoder; REQ-TEST-046's ability to assert
  `Canonical_P(v) = Canonical_R(v)` depends on one existing, and it is **not** mandated.
- `spec/10-index.json` says `ror-reference.depends_on = ["frozen semantics only (no
  production core deps)"]` — a **prose string** that claims to forbid precisely the
  `ror-core` edge that the frozen §10 **permits**, so two authoritative sources disagree
  about whether the reference may reach `ror-core` (dep/05 V-05 / ID-4). **Severity: HIGH.**

### 2.4 **Shared normalization** — F-04

Two normalization steps exist and are distinct in principle:
1. Each implementation emits a normalized `Observation` (15C.20; REQ-REF-035).
2. The comparator further normalizes both for comparison (R-REF-05; REQ-TEST-034 trace
   normalization distinguishes the included set `ActorSelected`, `ActorSpawned`,
   `CapabilityDerived`, `Send`, `Receive`, `Blocked`, `Woken` from excluded
   implementation detail).

The coupling risk is **the shared `Observation`/`Observed*` schema** (F-04): because the
`Observed*` element types are undeclared, there is no closed definition of what gets
normalized or in what order. The "normalized observation domain (shared schema with
MOD-15)" (`mod/14-reference.md` line 84) is a shared schema by design — that is the one
sanctioned boundary — but an **undeclared** shared schema means there is nothing to
confirm both sides are actually producing, and the comparator comparing, the *same*
channels. **Severity: HIGH.**

### 2.5 **Shared state machines** — F-05

- Reference actor/scheduler/global-state are `RefActor`, `RefScheduler`,
  `RefGlobalState` (distinct `Ref*` types) — good. The FIFO order, at-most-once
  membership, one-transition-per-turn rules (15C.13) mirror production R-ACTOR-04 but are
  independently re-stated.
- The one place the reference consumes **production-named state records** is the
  persistence boundary: `Snapshot`, `WAL`, `EffectJournal` (15C.17). The reference
  recovery operates on records that are **not** `Ref*`-prefixed. If those records are the
  production `Snapshot`/`WalRecord`/`EffectJournal` types (rather than an abstract
  test-side semantic record), the reference's recovered state is *derived from production
  record types*, i.e. shared production objects. 15C.17 says "abstract records", and
  REQ-TEST-045 requires the reference recovery to receive "semantic records from an
  independent test-side decoder" — but it does **not** give those records a distinct
  `Ref*` type or guarantee the test-side decoder is outside `ror-core` (ROR-008 is an
  "independent code path" of R-CANON-07, i.e. **inside** `ror-core`, in a crate the
  reference may depend on). **Severity: HIGH.**

### 2.6 **Shared production objects** — F-01, F-05, F-04

- The reference is allowed to depend on `ror-core`, which **is** the home of the
  production domain objects (`Value`, `CapRef`, `EffectId`, `ActorId`, `EffectCost`,
  `Consumable`, `Fault`) and the canonical codec. This is the largest single
  shared-production-object vector.
- The reference consumes production-named persistence records (`Snapshot`/`WAL`/
  `EffectJournal`).
- Both sides emit the **same** (`Observation`/@`Observed*`) test object — a shared object
  at the comparison boundary (sanctioned, but undeclared).
- The reference and production **marshal both through the same 15A bytes** (`MarshalledValue`
  is canonical bytes).

### 2.7 **Shared error handling** — F-06

- The reference defines its **own** error types where it mattered: `RefCapabilityError`
   (`term/02-collisions.md` "the reference model's separate error type"),
  `RefRecoveryFault` (15C.17), while production uses `CapabilityError`, `RecoveryFault`,
  `HostFault` (R-CALC-06). Good — the *internal* fault vocabularies are distinct.
- But the **comparison** carries `faults: Vec<ObservedFault>` (15C.20), and `ObservedFault`
  is **undeclared** (F-04). The underlying production `Fault` taxonomy (R-CALC-06) is
  **open** — `spec/09` U-08/U-14 record that `Fault`/`RecoveryFault`/`HostFault` variant
  sets are not closed (the term collision even notes `EffectJournalCorruption` is not a
  closed `Fault` member). So the "shared error surface" at the comparison boundary has no
  closed vocabulary, and a reference that classifies a fault differently (or produces a
  production `Fault` value where the reference side is supposed to be independent) is
  exactly the "shared error handling" coupling. **Severity: MEDIUM-HIGH.**

---

## 3. Consolidated dependency register — every dependency that could invalidate differential testing

| ID | Dependency | Where it lives | Coupling kind | Invalidates differential testing because | Severity |
|---|---|---|---|---|---|
| **F-01** | `ror-reference → ror-core` **permitted** (§10) / **not forbidden** (§14). `ror-core` = production `Value` (R-CALC-01), `CapRef` (R-KERN-01), `ActorId`/`EffectId`, `Consumable`/budget operands (R-BUDGET-*), and the **15A codec** (R-CANON-*). | `Red-on-Rust.md` L39645–39651 (§10); L39807–39828 (§14 omits `ror-core`) | shared production objects + shared serializer + shared types | Imports `Value`/`CapRef`/`ActorId`/`EffectId`/`Fault` and the codec — defeats `RefValue`/`RefCapId`/`RefActorId`/`RefEffectId` and the `ProductionSerializer` prohibition in one edge. RI-2 "PASS" because the graph types `MOD-14 → MOD-01` as SEMANTIC, not because it's forbidden. | **HIGH** |
| **F-02** | The **conditional** independent encoder of REQ-TEST-046 ("where an independent reference encoder exists"). | `req/01-registry-part8-reference-15C.md` REQ-TEST-046; 15C.1 | shared serializer | If no independent encoder is built, `Canonical(Recover_P)=Canonical(Recover_R)` can only be checked against the **production** codec — a reference that is not independently canonicalized. | **HIGH** |
| **F-03** | The **frozen production implementation** blocks that the reference is told to re-implement — the "Phase 10 Frozen Implementation (Lambda / Call)" (L18091), the "Phase 12 Frozen Implementation … finalize_request" (L23248 / L23870), and the 15A canonical codec ("Corrected Rust Implementation", L30647) — with 15C.38 forbidding copying them but nothing enforcing it. | 15C.6/7; 15C.38; L18091/L30647; REQ-TEST-048 | shared transition functions + shared serializer | A "reference" that adapts a frozen production block is production; the differential then proves nothing (oracle collapse). Enforcement is manual code-similarity review only. | **HIGH** |
| **F-04** | The **undeclared** `Observation`/`Observed*` schema (X-29), and the **homonymous** planner `Observation` (X-06) sharing the name. | 15C.20 L36170; L27156; `term/02-collisions.md` X-06/X-29; `term/_structs.py --undeclared` | shared normalization + shared production objects | The comparison domain (terminal states, events, effects, budgets, faults, digest) is **not closed**; whether both sides are reporting the same channels cannot be confirmed, and a reference filling in a different `Observed*` shape yields false divergence or false agreement. | **HIGH** |
| **F-05** | Reference recovery consumes **production-named** records `Snapshot`/`WAL`/`EffectJournal` — no `Ref*` prefix, unlike every other reference domain. | 15C.17 L36061; REQ-REF-032 | shared state machine + shared production objects | The reference's recovered state is derived from production record types; the "independent test-side decoder" is an `ror-core` code path (ROR-008), so independence is not guaranteed outside the crate the reference may import. | **HIGH** |
| **F-06** | `ObservedFault` (undeclared) over an **open** production `Fault` taxonomy (U-08/U-14). | 15C.20; R-CALC-06; `spec/09` U-08/U-14 | shared error handling | The comparison fault vocabulary is not closed; a reference that produces a production `Fault` value (or classifies differently) is coupled and cannot be distinguished from a genuine divergence. | **MEDIUM-HIGH** |
| **F-07** | `ror-differential` co-resides with `ror-runtime` (the black-box SUT) **and** `ror-reference` in **one dependency closure**; if it ever imports `ror-runtime` internals behind the observation boundary, oracle independence becomes a build-graph fact. | `spec/07` §6; `spec/10-index.json`; dep/05 **HD-6** ("the only place the production machine and `ror-reference` co-reside") | shared normalization (comparator) | The comparator is the one place production and reference meet; a wrong import there couples them. HD-6 explicitly warns: "keep every one of these dev-dependency-only and behind the observation interface (R-REF-05), or the independence of the differential oracle becomes a build-graph fact instead of a semantic one." | **MEDIUM-HIGH** |
| **F-08** | `RefCapId`/`RefActorId`/`RefEffectId` declared **twice** (L35471–73 and L39664–66), not linked, no D-entry. | 15C.4; §10 | shared production objects (identity) | Two authoritative declarations can drift; a reference built from one and a differential scrutinee read from the other breaks the identity correspondence REQ-REF-036 needs. | **MEDIUM** |
| **F-09** | The five `ror-reference ↛ {runtime,kernel,persistence,host,agent}` **crate-edge** forbiddens have **no tracked obligation/atomic record** (HD-5, V-02); the R-REF-02 *call* prohibition is tracked (REQ-REF-004) but the *crate-edge* layer is untracked. Also five of the ten frozen §14 forbiddens are untracked. | `dep/05` HD-5, V-02; §14 L39807–39828 | enforcement gap | The "dependency review" mapped to R-ARCH-04 has no enumerated checklist for the exact edges that carry the independence; nothing fails the gate if `ror-reference/Cargo.toml` grows a runtime/persistence/host dependency. | **HIGH** |
| **F-10** | `audit/_conservation_checker.py` — an executable budget/transition model (Op-01…Op-22) outside the frozen `ror-reference` contract; arithmetic not exact-matched to R-BUDGET-02 and not differentially tested. | `audit/_conservation_checker.py`; `check.py` | shared helpers (governance) | If adopted as, or copied into, the reference oracle, it becomes a third un-coupled model whose arithmetic is unaudited → potential falsenegative oracle. | **MEDIUM** |
| **F-11** | "May depend on the frozen primitive/domain definitions from `ror-core` **only where doing so does not accidentally import production semantics**" — an untestable, prose-only qualifier that no check enforces. | §10 L39645–39651; `spec/10-index.json` | shared types (untestable) | The one sentence that would allow `ror-core` deps is guarded by a subjective judgment ("does not accidentally import"), not by an obligation or a check. This is the mechanism that makes F-01 possible. | **HIGH** |

---

## 4. Enforcement-gap table — the gates that are supposed to gate

| Gate | What it actually checks | What it does **not** check | Consequence for differential testing |
|---|---|---|---|
| `dep/_graph.py` RI-1…RI-4 | The **specification module graph** has no implementable-kind edge into/out of MOD-14; no production→verification implementable edge. | No `Cargo.toml` (none exists); **does not** inspect the soft `ror-reference → ror-core` clause; treats `MOD-14 → MOD-01` as SEMANTIC by rule R3, not by proof. | The independence "PASS" is a graph-labeling result, not an enforcement of the type/edge boundary. |
| `spec/07` §6 dependency direction | Prose crate DAG. | `ror-reference → ror-core` is only stated as "frozen semantics only" — no crate edge, no obligation, no check. | The one dangerous edge is neither drawn nor forbidden. |
| REQ-REF-004 / REQ-TEST-048 | **Call-edge** prohibition (function-level). Verification = "dependency-graph review; code-similarity review." | Nothing automates the crate-edge or code-similarity review (F-03, F-09). | Oracle collapse through copied transition code, or a forbidden crate dep, is not caught by the gate. |
| REQ-TEST-045 | Reference recovery must not consume production snapshot/WAL decoders. | The "independent test-side decoder" is an `ror-core` code path (ROR-008) in a crate the reference may import (F-05). | Recovery independence is not guaranteed outside `ror-core`. |
| `term/_structs.py --undeclared` | Reports undeclared type names (catches X-29/X-84). | It reports; nothing **requires** the `Observed*` type declarations. | The comparison domain stays open (F-04). |
| `_conservation_checker.py` | Re-derives conservation/atomicity over Op-01…Op-22. | Not a differential oracle; not governed by R-REF-02; arithmetic not proven equal to the frozen rules. | A third, ungoverned semantic model exists in-repo (F-10). |

---

## 5. Verdict

| Requirement | Verdict |
|---|---|
| Reference defines its own value domain `RefValue` (REQ-REF-019) | **SATISFIED** (distinct `RefValue`; no production `Value` reuse). |
| Reference environment `RefEnv` independent (REQ-REF-020) | **SATISFIED**, with an explicit "must not reuse production `Environment`" (15C.5). |
| Reference CEK/transition rules re-implement frozen rules, never recursive (REQ-REF-022) | **SPECIFIED**; enforcement of "no shared body" is manual only (F-03). |
| Reference capability algebra independent; kernel never called (REQ-REF-023) | **SATISFIED** at call level; `RefCapabilityStore`/`RefAuthority` distinct. |
| Reference budget independent of production arithmetic (REQ-REF-025) | **SATISFIED** for `RefConsumable`/`RefBudget`; undermined by the `ror-core` allowance (F-01) which hosts the shared budget operand types. |
| Reference effect protocol order (REQ-REF-026) | **SATISFIED** (implements the frozen Phase 12 issuance sequence order; emits per-gate events for short-circuit detection). |
| Reference persistence/recovery independent (REQ-REF-032, REQ-TEST-045) | **PARTIALLY** — distinct `RefGlobalState`/`RefRecoveryResult`, but consumes **production-named** records and the test-side decoder is an `ror-core` path (F-05). |
| Reference marshaller independent (REQ-REF-030) | **PARTIALLY** — distinct code, genuinely shared 15A byte format (F-01/F-03). |
| Reference host has no connection to production `ReplayHost` (REQ-REF-034) | **SATISFIED** (`RefHost`, `RefReceipt`). |
| Distinct identifiers `RefCapId`/`RefActorId`/`RefEffectId` | **SATISFIED**, with a duplicated-declaration hazard (F-08) and the `ror-core` type-import risk (F-01). |
| `Observe(Production(X)) = Observe(Reference(X))` (R-REF-01) | **SPECIFIED, NOT VERIFIED**; comparison domain `Observed*` undeclared (F-04). |
| `Canonical(Recover_P(D)) = Canonical(Recover_R(D))` (R-REF-01) | **SPECIFIED, NOT VERIFIED**; dependent on an independent encoder that is only conditional (F-02) and on `ror-core`-bound records/decoder (F-01, F-05). |
| Anti-oracle-collapse rules (15C.38, REQ-TEST-048) | **STATEMENT SATISFIED**; enforcement by machine is absent (F-03, F-09). |
| No forbidden crate edge (RI-1) | **PASS** *at the specification layer*; **`ror-reference → ror-core` is the un-forbidden exception** (F-01). |

**Bottom line.** The frozen Phase 15C *states* the independence boundary and the two
differential properties with a level of care unusual for a specification — the `Ref*`
renaming discipline, `RefCapabilityError`/`RefRecoveryFault`, the explicit "no conversion
from `CapRef` to `RefCapId`", the anti-oracle-collapse rules, and the four-track oracle
separation are all present and internally consistent **at the call-edge level**.

**The boundary is leak-prone at the type/edge level, and the leak is concentrated in one
place: `ror-core`.** §10 says the reference *may* depend on `ror-core` **only** "where
doing so does not accidentally import production semantics" (an untestable, prose-only
qualifier), and §14's forbidden-edge list **omits `ror-core` entirely**. `ror-core` is the crate that
holds the production `Value` domain, `CapRef`, `ActorId`/`EffectId`, the budget operand
types, and — decisively — the **15A canonical serializer and codec**. So the single
highest-severity finding is **F-01**: unless a reference is constrained to depend on zero
production crates (including `ror-core`) *for core semantics*, the distinct types, the
independent serializer, and the independent recovery all collapse into a shared
`ror-core` dependency that the current gates label "SEMANTIC" and let pass.

The second cluster is **the undeclared comparison domain** (F-04/F-06): `Observation` and
its seven `Observed*` element types are **never declared**, and a homonymous
planner-facing `Observation` shares the name. Until those are closed and the comparison
schema is actually a type, `Observe(Production(X)) = Observe(Reference(X))` is
unfalsifiable in exactly the way the semantic-nondeterminism audit found the
`UniqueMachineTrace` theorem to be.

The third cluster is **enforcement** (F-09, F-03, F-11): the crate-edge and code-similarity
reviews are manual, the forbidden crate edges are untracked by any obligation, and the
"only where it does not accidentally import production semantics" clause is not
machine-checked. `check.py` passes today; none of those passes asserts the reference is
actually independent.

**Recommended disposition (for the owner; not issued here, R-SCOPE-03):** (1) close the
`ror-core` hole by making `ror-reference` depend on *zero* production crates for core
semantics (forbid `ror-core`, or split a genuinely semantics-free `ror-semantics` types
crate), and track it as a registered prohibition; (2) declare the `Observed*` element
types and disambiguate the `Observation` homonym (resolve X-06/X-29); (3) declare the
test-side persistence records as `Ref*` and the test-side decoder outside `ror-core`;
(4) require an independent reference 15A encoder (remove the conditional in REQ-TEST-046);
(5) record the five untracked `ror-reference` crate-edge forbiddens (HD-5), and (6) add an
automated code-similarity / forbidden-import gate. None of these silently changes
semantics; all of them make the differential property *checkable*.
