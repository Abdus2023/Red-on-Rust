# Output 4 — Requirements Whose Verification Method Is Currently Undefined

Four distinct kinds of gap are reported. Only §1 is a true "undefined verification method"; §§2–4 are recorded so that no record is silently passed over as verified.

Global note: **all 497 registry records carry `EVIDENCE-STATUS: SPECIFIED`.** The repository contains no Cargo workspace, no Rust source, no tests, no golden vectors, no mutation registry, and no CI configuration (`git ls-files` returns only `README.md`, `Red-on-Rust.md`, `spec/00`–`spec/10`, and `req/*`). No record may be promoted to `IMPLEMENTED`, `TESTED`, `VERIFIED`, or `PROVEN` on the strength of specification text (extraction rules 10 and the "do not promote evidence states" constraint).

---

## §1 Verification method undefined pending a specification decision — 8 records

| # | Record | Requirement (short) | What is missing | Blocks | Linked |
|---|---|---|---|---|---|
| VU-01 | REQ-SCOPE-005 | Implementation in memory-safe Rust; no unsafe without documented justification; no host-specific extensions to the calculus | No criterion exists for what would falsify "memory-safe substrate" — a Rust implementation satisfies it by construction, so the requirement has no observable failure mode as written. Either it needs restating as a concrete prohibition set or it is a scope statement, not a requirement | Nothing downstream | `spec/09` (scope) |
| VU-02 | REQ-BUDGET-008 | Duration `D` is part of the capability; host/scheduler transitions consume `ΔD` | No value or derivation for `ΔD`; exhaustion behavior undefined | Deadline-exhaustion tests; `DeadlineValid` is testable, exhaustion is not | AMB-01, U-01 |
| VU-03 | REQ-ACTOR-018 | Spawn budget allocation conserves parent+child budget | The allocation *function* is not frozen, so the conserved split cannot be predicted | Budget-conservation test oracles for spawn | AMB-03, U-03 |
| VU-04 | REQ-ACTOR-035 | Actor status transitions | `RunState`↔`ActorStatus` mapping is absent, so the expected post-transition status is indeterminate | `SCHED-BLOCKED-NOT-SCHEDULED`; snapshot round-trip of actor status | AMB-05, U-08 |
| VU-05 | REQ-MARSHAL-008 | Marshal round-trip idempotence law | The law's quantification domain (marshalable subset) is not enumerated | Track B round-trip property test | AMB-06, U-09 |
| VU-06 | REQ-PLANNER-013 | Stale plan rejection | The staleness predicate is explicitly unfrozen | `Fault::StalePlan` negative tests | AMB-10, U-13 |
| VU-07 | REQ-CAP-024 | `AdmissibleConstraint` premise of attenuation | No definition of admissibility | `E-Attenuate`/`E-AttenuateDenied` tests; `CAP-DERIVE-NO-AMPLIFICATION` negative branch | AMB-12, C-30/U-09 (as stated, incorrect) |
| VU-08 | REQ-EFFECT-036 | Host fault propagation into the machine | No mapping from `HostFault` variants to the frozen `Fault` enum | Host-fault differential comparison | AMB-08, U-17 |
| VU-09 | REQ-RECOV-018 | Runnable-queue reconstruction after replay | Snapshot-queue vs reconstructed-queue precedence is undecided | Crash matrix T4/T5 expected runnable set | AMB-09, U-14 |

Three further records have a verification method that is *defined but not closed*, and are flagged here rather than in §4:

| Record | Method as written | Gap |
|---|---|---|
| REQ-BUDGET-012 | per-transition `δ_t` consumption | the `δ_t` table does not exist (AMB-19) |
| REQ-CALC-011 | blocking-receive state transitions | `await`/retraction semantics absent (AMB-17) |
| REQ-EFFECT-002 | effect-class authorization | closed `Op` set disputed (AMB-16, AMB-20) |

## §2 No verification obligation — the record is NON-NORMATIVE (4)

| Record | Content | Why no verification obligation |
|---|---|---|
| REQ-CALC-016 | Turn-[54] §23 property table (properties of the calculus as described) | Explanatory restatement of obligations extracted elsewhere; marked `NON-NORMATIVE` per rule 8 |
| REQ-CANON-006 | Stale §1.3 standalone primitive tags `0x10/0x11/0x13` | Superseded by the frozen turn-[50] format (C-02); kept for provenance only |
| REQ-CANON-033 | "Equal digests imply equal inputs" reverse direction | Digest equality is not collision-resistant by statement; the source offers it as commentary, not obligation |
| REQ-COMPILE-014 | Observation that no pipeline stage is named as producing the effect set `F` | A gap report, not a requirement (AMB-13, U-22) |

## §3 No verification obligation — the record is a permission (4)

| Record | Permission |
|---|---|
| REQ-PLANNER-016 | Planner MAY propose multiple candidate plans |
| REQ-REPO-003 | Top-level crate names MAY change for organizational reasons |
| REQ-CLAIM-019 | Formal mechanization MAY be added later; it is not required to begin |
| REQ-REF-017 | Reference interpreter MAY copy an immutable environment snapshot |

Four further `MAY` records do carry a review or test method and are therefore not gaps: REQ-SCOPE-012, REQ-TRUST-008, REQ-CAP-006, REQ-REF-005.

## §4 Verification method defined only as human review — 96 records

These have a stated method, but the frozen source attaches no executable obligation (no conformance tag, no mutation, no gate, no vector) to them. They are verifiable only by inspection of the future repository. Grouped by what the review inspects:

- **Dependency/visibility review (35):** REQ-SCOPE-011, REQ-SCOPE-012, REQ-TRUST-004, REQ-ARCH-005, REQ-ARCH-006, REQ-COMPILE-010, REQ-COMPILE-011, REQ-CAP-009, REQ-KERN-002, REQ-BUDGET-017, REQ-BUDGET-026, REQ-PERSIST-001, REQ-RECOV-014, REQ-RECOV-021, REQ-REF-004, REQ-REF-005, REQ-REF-007, REQ-REF-008, REQ-TEST-004, REQ-TEST-013, REQ-TEST-021, REQ-REPO-004, REQ-REPO-006, REQ-REPO-007, REQ-REPO-008, REQ-REPO-009, REQ-REPO-014, REQ-REPO-018, REQ-REPO-019, REQ-CLAIM-003, REQ-CLAIM-011, REQ-REF-018, REQ-REF-032, REQ-TEST-045, REQ-TEST-048.
- **Type/state-shape review (15):** REQ-CALC-004, REQ-CALC-005, REQ-CALC-007, REQ-CALC-017, REQ-CALC-018, REQ-KERN-009, REQ-BUDGET-001, REQ-BUDGET-018, REQ-ACTOR-006, REQ-PERSIST-017, REQ-REF-019, REQ-REF-021, REQ-REF-024, REQ-REF-027, REQ-REF-031.
- **Layout/structure review (9):** REQ-REPO-001, REQ-REPO-002, REQ-REPO-005, REQ-REPO-010, REQ-REPO-011, REQ-REPO-012, REQ-REPO-013, REQ-REPO-015, REQ-REPO-016.
- **Comparator/reference-model review (9):** REQ-CANON-034, REQ-REF-006, REQ-REF-009, REQ-REF-010, REQ-REF-011, REQ-REF-013, REQ-CLAIM-013, REQ-REF-035, REQ-TEST-047.
- **Process/milestone review (12):** REQ-SCOPE-006, REQ-TEST-025, REQ-ORDER-001, REQ-ORDER-002, REQ-ORDER-016, REQ-ORDER-022, REQ-ORDER-023, REQ-ORDER-024, REQ-ORDER-025, REQ-CLAIM-022, REQ-TEST-052, REQ-TEST-056.
- **Record/report review (14):** REQ-SCOPE-007, REQ-CANON-036, REQ-REF-003, REQ-TEST-016, REQ-TEST-019, REQ-TEST-023, REQ-TEST-024, REQ-TEST-031, REQ-CLAIM-015, REQ-CLAIM-017, REQ-CLAIM-018, REQ-CLAIM-020, REQ-CLAIM-021, REQ-TEST-054.
- **Generator review (2):** REQ-TEST-038, REQ-TEST-039.
Recommendation (non-normative, not part of the extraction): the dependency/visibility group and the layout group are mechanically checkable with `cargo tree`/`cargo deny` and a directory assertion, and the comparator group is checkable by asserting the comparator consumes all eight normalized channels. The adjudication group cannot be mechanized — it is inherently a human record.

## §5 Counts

| Category | Count |
|---|---|
| §1 `UNDEFINED` verification method | 8 (+3 defined-but-not-closed) |
| §2 `NON-NORMATIVE` | 4 |
| §3 `MAY` permission with no obligation | 4 |
| §4 review-only | 96 |
| All other records (executable method stated: conformance tag, mutation M0xx, milestone gate, crash matrix, golden vector, property test, or differential test) | 430 |
| **Total registry records** | **542** |
