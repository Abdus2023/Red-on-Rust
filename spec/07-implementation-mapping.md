# 07 — Implementation Mapping

Maps every obligation to its **normative implementation home** (the crate/module the frozen repository design assigns) and to the **actual state in this repository**.

## 1. Actual repository state (evidence)

```
/home/user/Red-on-Rust/
├── .git/
├── README.md          ← orientation document (turn [60] output)
├── Red-on-Rust.md     ← frozen source (60-turn transcript)
└── spec/              ← this document set
```

**No Cargo workspace, no crate, no Rust source, no tests, no vectors, no CI configuration exists in this repository.** The repository is at the state the source itself calls **BOOTSTRAP** (R-SCOPE-02). Consequently:

- Every obligation is `SPECIFIED` (see `03`).
- **No obligation is `IMPLEMENTED`**, despite the README's "Implementation: IN PROGRESS/READY" wording — that wording is orientation, not evidence (C-09).
- The Rust code blocks inside `Red-on-Rust.md` are **specification artifacts** (frozen API contracts, frozen implementations for 15A), not repository code. They are normative *as specification text* (especially 15A, which is declared frozen down to byte level) but are not "implemented" until present and tested in the workspace.

## 2. Obligation → crate/module mapping

| Crate (frozen, R-REPO-02) | Responsibility (frozen) | Obligations realized here |
|---|---|---|
| `ror-core` | Semantic domain types; std-only; no host/FS/net/scheduler/persistence/authority/LLM | R-CALC-01…08, R-BUDGET-01…08, R-KERN-01 (CapRef type), R-CANON-01…11 (traits + data-domain encodings), R-CAP-01 (domain trait definitions), R-ARCH-04 |
| `ror-compiler` | Block → parse → normalize → validate → lower → capability/resource analysis → ExecutablePlan; plan constructors private | R-COMPILE-01…05, R-ARCH-03, R-PLANNER-02 (compiler-side rejection), R-ORDER-03 |
| `ror-kernel` | CapabilityKernel: derive/authorize/validate/revocation; authority storage; budget primitives | R-CAP-02…09, R-KERN-01…03, R-TRUST-03 |
| `ror-runtime` | CEK machine, actors, scheduler, effects, marshalling | R-CEK-01…07, R-EFFECT-01…07, R-ACTOR-01…08, R-MARSHAL-01…04, R-ARCH-01 (machine stages), R-CORE-08 |
| `ror-persistence` | WAL, snapshots, effect journal, recovery | R-DUR-01…05, R-PERSIST-01…06, R-RECOV-01…07 |
| `ror-host` | Host execution and replay boundaries | R-HOST-01…05 |
| `ror-agent` | Planner/observation/supervisor integration | R-PLANNER-01…05, R-ARCH-01 (planner stages) |
| `ror-reference` | Independent executable semantic model (zero shared core logic) | R-REF-01…06 (reference side) |
| `ror-differential` | Generator, runner, comparator, shrinking | R-REF-01, R-REF-05, R-TEST-02, R-TEST-03, R-TEST-07 |
| `ror-testkit` | Test infrastructure and controlled doubles | R-REF-06 (PanicHost, MockKernel), R-TEST-06, R-TEST-08 (crash harness), R-PLANNER-05 (harness side) |
| `tests/{conformance,exhaustive,property,mutation,crash,stress}` | Frozen test topology | R-TEST-01…11 |
| `vectors/canonical`, `vectors/persistence`, `vectors/effects` | Normative fixtures | R-CANON-11, R-PERSIST-02 fixtures |
| `mutations/registry.toml` | Additive mutation registry | R-TEST-04, R-TEST-05 |
| `scripts/` | CI entrypoints | R-TEST-10 |

## 3. Obligation → module-level detail (selected critical mappings)

| Obligation | File/module home (normative) | Notes |
|---|---|---|
| R-CANON-02…08 (15A format) | `ror-core/src/canonical/*` (source blueprint: `src/canonical/mod.rs` split into cursor, envelope, domain types, value, errors) | The source provides a **frozen reference implementation** (625-line Rust block at L30647, corrected at L33290). An implementation is conformant only if it reproduces the frozen golden vectors byte-for-byte (R-CANON-11). |
| R-EFFECT-03 (16-step sequence) | `ror-runtime` request finalization (source blueprint `finalize_request`, L23857) | Must be the *only* path to `ActorStatus::Pending`; any reordering is a bug (R-EFFECT-03). |
| R-DUR-02 (issuance transaction) | `ror-persistence` append+sync API called from `ror-runtime` | The 2×fsync ordering is the security-critical part. |
| R-RECOV-03/04 (recovery) | `ror-persistence` (production) + `ror-reference` (independent recovery oracle) | Independence is structural: two implementations, one contract. |
| R-PLANNER-03 (staleness) | `ror-agent` proposal intake + `ror-runtime` boundary check | The check lives at the machine boundary, not in the LLM integration. |
| R-ARCH-03 (plan constructors private) | `ExecutablePlan` homed in `ror-core` behind `PlanSeal`; `finalize` compiler-only (addendum VI, `dep/05` V-01 resolved) | Seal = clippy `disallowed-methods` on the token constructor everywhere except `ror-compiler` (Track-B); no new crate edge — `ror-runtime` already depends on `ror-core`. |
| R-BUDGET-01…09 (budget crate home) | algebra + operand types in `ror-core`; gate calls in `ror-runtime`; `ror-kernel` consumes core types (addendum VI, `dep/05` V-09 resolved) | `ror-core → ror-kernel` is forbidden by §14's frozen list, so shared types must be core-resident. |
| R-KERN-03 (authority privacy) | `ror-kernel` visibility (`pub(crate) AuthorityNode`) | Enforced by Rust visibility + dependency direction (kernel cannot depend on runtime). |

## 4. Milestone → obligation → crate crosswalk

| Milestone | Obligations | Primary crate(s) |
|---|---|---|
| M0 Workspace | R-REPO-01…03, R-ORDER-04 (ROR-001…002) | workspace |
| M1 Canonical serialization | R-CANON-01…11 | ror-core (+ vectors/canonical) |
| M2 Pure CEK | R-CEK-01…07 (Value/Var/Let/Seq/If subset), R-REF-01…05 (pure subset) | ror-runtime, ror-reference, ror-differential |
| M3 Lambda/Call | R-CEK-03…05 (tags CEK-CALL-ARITY-PRECHECK, CEK-CALL-ARGS-LTR, CEK-CLOSURE-LEXICAL-CAPTURE) | ror-runtime, ror-reference |
| M4 Capability/Attenuation | R-CAP-01…09, R-KERN-01…03 | ror-kernel, ror-reference |
| M5 Effects | R-EFFECT-01…07, R-DUR-01…05, R-HOST-01…05 | ror-runtime, ror-persistence, ror-host |
| M6 Actors | R-ACTOR-01…08, R-MARSHAL-01…04 | ror-runtime |
| M7 Persistence | R-PERSIST-01…06, R-RECOV-01…07 | ror-persistence |
| M8 Differential system | R-REF-01…06, R-TEST-02…03, R-TEST-07 | ror-differential, ror-reference |
| M9 Mutation gate | R-TEST-04…06 | mutations/, ror-testkit |
| M10 Crash/recovery gate | R-RECOV-02, R-TEST-08 | ror-persistence, ror-testkit |
| M11 Release candidate | R-TEST-10, R-TEST-11, R-CLAIM-01 | all |

## 5. First-sprint task → obligation map (ROR-001…ROR-016)

| Task | Obligation(s) |
|---|---|
| ROR-001 Create Cargo workspace | R-REPO-01 |
| ROR-002 Pin Rust toolchain | R-REPO-01 |
| ROR-003 Create ror-core domain types | R-CALC-01…04, R-BUDGET-01, R-KERN-01 |
| ROR-004 Implement canonical cursor | R-CANON-07, R-CANON-08 |
| ROR-005 Implement canonical envelope | R-CANON-02, R-CANON-08 |
| ROR-006 Implement primitive canonical types | R-CANON-05 |
| ROR-007 Implement Value canonical encoding | R-CANON-04, R-CANON-06 |
| ROR-008 Implement independent Value canonical decoding | R-CANON-07 (independent code path) |
| ROR-009 Add canonical golden vectors | R-CANON-11 |
| ROR-010 Add malformed-input suite | R-CANON-07 |
| ROR-011 Add duplicate-map-key regression | R-CANON-06 (M014) |
| ROR-012 Create reference-model crate | R-REF-02, R-REF-03 |
| ROR-013 Create differential observation API | R-REF-05 |
| ROR-014 Implement pure reference CEK | R-REF-03 (pure subset) |
| ROR-015 Implement pure production CEK | R-CEK-01…02 (pure subset) |
| ROR-016 Add first production/reference differential tests | R-REF-01 (pure subset) |

## 6. Dependency-direction rules to enforce at implementation (structural, from R-REPO-02/03)

```
ror-core ── (std only)
ror-compiler → ror-core
ror-kernel → ror-core
ror-runtime → ror-core, ror-kernel, ror-persistence
ror-persistence → ror-core
ror-host → ror-core, ror-runtime (adapter boundary)
ror-agent → ror-core, ror-compiler, ror-runtime, ror-persistence
ror-reference → (frozen semantics only; NO ror-runtime/ror-kernel/ror-persistence/ror-host deps for core logic)
ror-differential → ror-reference, ror-runtime (as black-box SUT), ror-testkit
ror-testkit → ror-core (+ test-only deps)
```

Addendum III (R-TRUST-05; spec/06 C-85): `ror-runtime` gains `ror-persistence` —
request step 14's durable append/sync is the hinge of R-DUR-02 (`HostInvoked ⇒
DurableIssued`, no external effect before the journal is durable). This is the
only edge §14's frozen list does not forbid in either direction.

Owner decision (addendum VI, `dep/05` V-10c applied): `ror-agent` gains `ror-persistence` — the `PlannerAccepted` durable recording (R-PLANNER-04, REQ-PLANNER-018).

Forbidden edges (R-SCOPE-04, R-REF-02): any `ror-reference → {production step/authorize/budget/recover/encode/scheduler}` core-logic call.
