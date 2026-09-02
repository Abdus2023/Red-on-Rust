# MOD-15 — DIFFERENTIAL: Generation, comparison, shrinking

> Owns the comparison machinery: how test cases are generated, executed on both
> implementations, normalized, compared to first divergence, shrunk, and recorded
> as reproducible counterexamples.

## SECTION-ID

`MOD-15` (domain `DIFFERENTIAL`). Owner module file for the differential-harness
obligations of `TEST` (R-TEST-01, 02, 03, 07) and the comparator contract
(R-REF-05).

## TITLE

Differential harness — three execution modes with frozen baselines, reproducible
16-field counterexample artifacts, the ordered shrinking protocol, per-tag semantic
coverage with metrics-never-oracle discipline, and the comparator contract
(normalized observations, first divergence, never final-value-only).

## PURPOSE

Turn the reference model (MOD-14) into usable evidence: drive *the same* generated
semantic input through production and reference, normalize both sides into the
comparison domain, and report the **first** divergence — with artifacts reproducible
from seed and shrinkable to a minimal case. Coverage is reported per frozen
obligation tag and is evidence about test strength, never a substitute for the
oracle.

## NORMATIVE-CONTENT

Normative text home: `spec/01` S-20 (differential half) + S-21 (modes, artifacts,
shrinking, coverage); atomic renderings `req/01-registry-part6-verification.md` and
`req/01-registry-part8-reference-15C.md` (15C.22–15C.46 harness half). This module
owns:

- **Execution modes + frozen baselines** (R-TEST-01 — placed here per architectural
  responsibility: 15C.39 defines these as *differential* execution modes, and
  `ror-differential` is the generator/runner; `mod/00-overview.md` §3): exhaustive
  small-state (baseline `expression depth ≤ 4, actors ≤ 2, capabilities ≤ 2`, every
  commit); property-generated (layered generation: structure → type validity →
  capabilities → budgets → actor topology → effects → persistence corruption,
  nightly); stress (`50k–100k` call depth, `100+` actors, long mailboxes, large WAL
  traces, repeated crash/recovery; weekly / release candidates). The CI time target
  is a performance budget, **never** a semantic constraint; coverage is partitioned/
  sharded/cached, never reduced (C-11 fixed; C-29 range adopted; C-31 wording
  variance recorded).
- **Reproducible counterexamples** (R-TEST-02): every generated case reproducible;
  every failure saves the structured artifact (seed, generator_version,
  semantic_version, test_case_version, program, initial state, capabilities, budgets,
  actor topology, scheduler_trace, host_trace, persistence image, crash_trace,
  production_observation, reference_observation, first_divergence, minimized case);
  the artifact MUST run locally; same seed/state/traces twice ⇒ identical run
  (REQ-TEST-050).
- **Shrinking protocol** (R-TEST-03): ordered priorities (1) actor count,
  (2) expression depth, (3) call arity, (4) bindings, (5) mailbox messages,
  (6) capability scope, (7) budget dimensions, (8) WAL records, (9) effect count,
  (10) crash position; the shrinker preserves the failure predicate; every failure
  yields a minimal artifact.
- **Semantic coverage** (R-TEST-07): coverage tracked per stable verification-
  obligation tag (the frozen tag set — see each owning module); metamorphic
  transformations, negative differentials, gated-stage markers and the reference
  property suite are harness obligations (REQ-TEST-035/036/037/043); the four-track
  Phase 13 verification set and the 35-property minimum acceptance suite are recorded
  here as harness obligation sets (REQ-TEST-057/058). Coverage metrics are evidence
  and **never** a substitute for the differential oracle.
- **Comparator contract** (R-REF-05 — the comparator is `ror-differential`'s frozen
  responsibility, so its contract is owned here; placement rationale in
  `mod/00-overview.md` §3): comparison over normalized observations (terminal states,
  event trace, effect trace, resource partitions, authority outcomes, scheduler
  trace, faults, recovered state); internal details (addresses, allocator behavior,
  Rust layout, OS handles, host object identity) excluded unless explicitly semantic;
  comparison at progressively stronger levels (terminal → event → …, REQ-TEST-033);
  trace normalization distinguishes semantic from implementation-specific events
  (REQ-TEST-034); a deterministic identity correspondence maps production↔reference
  IDs (REQ-REF-036); the comparator MUST report the **first** divergence; comparing
  only final return values is forbidden.

Crate contract (mirrored by pointer): `ror-differential` — generator, runner,
comparator, shrinking (R-REPO-02).

## NON-NORMATIVE-CONTENT

- Example metamorphic rewrites (`let x = v in …` forms) and the generated-grammar
  catalogue are harness engineering detail; their *contract* (metamorphic
  supplementation; bounded initial grammar) is what's frozen.
- The README's tag example list is non-exhaustive (C-10); the frozen tag set lives in
  the master prompt §21 (see `spec/08` §1).
- "Must complete in <2 minutes" is superseded wording (C-11); time is a performance
  budget only.

## INPUTS

- Production observations (MOD-05…13) and reference `Observation`s (MOD-14), both in
  the normalized schema (REQ-REF-035).
- Seeds and generator metadata (recorded per case), frozen baselines, the tag set.
- Crash scenarios/persistence images (with MOD-11/12) for differential persistence
  testing (REQ-TEST-044: inject crash, recover both, compare canonical outcomes).

## OUTPUTS

- First-divergence reports (REQ-TEST-042: index + both events + classification
  candidate), reproducible counterexample artifacts, shrunk minimal cases.
- Coverage reports per obligation tag; metamorphic/negative differential suites;
  Track-A scheduler-order and Track-D global-trace equivalence outputs.
- Inputs to adjudication (MOD-17, R-TEST-09): never auto-classify a divergence by
  changing the oracle.

## DEPENDENCIES

- Module dependencies: MOD-14 (reference side), MOD-01…MOD-12 as systems under test
  via observation interfaces (black-box), MOD-17 (infrastructure: `ror-testkit`
  doubles, CI scheduling).
- Consumers: MOD-16 (kill evidence), MOD-17 (adjudication, CI gates, acceptance).
- Crate edges: `ror-differential → ror-reference, ror-runtime (black-box SUT),
  ror-testkit` (`spec/07` §6).
- Blocking open items: **U-08/U-14** (fault-variant comparability), **U-09**
  (value-domain correspondence), **U-02** (Track A snapshot comparison blocks on
  machine-state encodings — AMB-02).

## INVARIANTS

- Same input both sides; normalized comparison; **first divergence** reported; final-
  value-only comparison forbidden (R-REF-05; REQ-REF-010…013).
- Reproducibility: seed + versions ⇒ identical run; artifact complete and locally
  runnable (R-TEST-02; REQ-TEST-050).
- Shrinking preserves the failure predicate; minimal artifact per failure
  (R-TEST-03).
- Coverage tracked per tag; metrics never substitute for the oracle (R-TEST-07;
  REQ-TEST-021).
- Baseline coverage floor: `depth ≤ 4, actors ≤ 2, capabilities ≤ 2` exhaustive
  enumeration; semantic coverage is inviolable under time pressure (R-TEST-01).

## REQUIREMENTS

Canonical text: `spec/01` S-20/S-21. All 5 obligations `SPECIFIED`.

| ID | Obligation (short) | Provenance (`Red-on-Rust.md`) | Verification |
|---|---|---|---|
| R-TEST-01 | Three execution modes + frozen baselines; time ≠ semantics | L38587–38715 (§22), L37251–37268 | CI (modes run by MOD-17's gates) |
| R-TEST-02 | Reproducible counterexample artifact (16 fields) | L38714–38745 (§25), L37293–37315 | artifact schema |
| R-TEST-03 | Shrinking protocol (10 ordered priorities) | L38439–38465 (§18) | shrinking tests |
| R-TEST-07 | Semantic coverage by obligation tags; metrics ≠ oracle | L38544–38583 (§21), L37402–37414 | coverage report |
| R-REF-05 | Normalized observations; first divergence; no final-value-only comparison | L38346–38388 (§16), L41869–41906 | comparator review |

Atomic registry records under this module: REQ-REF-010…013 (comparator clauses),
REQ-REF-035…036 (normalized observation + identity correspondence, parent R-REF-05);
REQ-TEST-001…011 (modes, artifacts, shrinking), REQ-TEST-020…021 (coverage),
REQ-TEST-033…041 (comparison levels, normalization, negative/short-circuit suites,
property suite, grammar, generator, shrinking, counterexample format),
REQ-TEST-043 (metamorphic), REQ-TEST-049 (15C modes), REQ-TEST-050 (determinism of
harness), REQ-TEST-057…058 (35-property suite, four-track set).
**5 obligations / 33 records.**

## SECURITY-BOUNDARY

The harness is trusted infrastructure: its adversarial content is *itself* — a weak
generator explores nothing, a sloppy comparator hides drift, and an unreproducible
failure is unfalsifiable. The protection rules are frozen: seeded reproducibility,
first-divergence reporting, mandatory shrinking with predicate preservation, and the
explicit ban on comparing only final values (the cheapest way to fake agreement).

## VERIFICATION-OBLIGATIONS

- Owns the execution machinery behind *every* module's tag evidence; tag definitions
  stay with their modules (see `18-ownership-matrix.md` §4).
- 15C harness obligations: comparison levels (15C.23), normalization (15C.24),
  negative differential (15C.25), short-circuit stage markers (15C.26), property
  suite (15C.27), grammar/generator (15C.28/29), shrinking (15C.30), counterexample
  format (15C.31), first divergence (15C.32), metamorphic (15C.33), differential
  persistence (15C.34), execution modes (15C.39), determinism (15C.40).
- Milestone gates: M2 (first differential), M8 (full differential system:
  generation, both executions, normalized comparison, first-divergence reporting,
  shrinking), contributes to M9/M10/M11 evidence.

## SOURCE-PROVENANCE

- 15C harness half: [48] (L36215–37168; map in `req/00-method.md` §5.4); master
  prompt §16–§22 (L38346–38651, anchors corrected per §5.1); 15D clarifications
  [49]/[50] (L37169–37459).
- Canonical set: `spec/02` S-20/S-21; `req/01-registry-part6-verification.md` and
  `req/01-registry-part8-reference-15C.md`.

## CROSS-REFERENCES

Owned here, binding elsewhere:

- R-REF-05 → MOD-14 (reference must emit normalized `Observation`), MOD-17 (first
  divergence feeds adjudication R-TEST-09; acceptance R-TEST-11 evaluates oracle
  equality), MOD-01…12 (each module's traces/observations are comparator inputs).
- R-TEST-01 → MOD-17 (CI cadence R-TEST-10 schedules these modes; the *modes* are
  this module's), all SUT modules (the generated distribution must cover their
  obligations).
- R-TEST-02 → MOD-17 (artifacts are adjudication input), MOD-16 (mutant kill
  evidence uses the same reproducibility machinery).
- R-TEST-07 → MOD-16 (mutation coverage attribution), MOD-17 (coverage report
  consumed at nightly/release gates).

Owned elsewhere, binding DIFFERENTIAL: R-REF-01/02 (MOD-14 — the gate's purpose and
its independence boundary; fixtures may be shared, transitions never),
R-PLANNER-05(3)/REQ-TEST-051 (MOD-13 — LLM input generation rules), R-TEST-08
(MOD-17 — crash-matrix harness obligation; differential persistence testing
REQ-TEST-044 straddles MOD-12 — cross-reference), R-TEST-09 (MOD-17 — divergence
outcomes are adjudicated there, not here). Open items: U-02/U-08/U-09 as above.
