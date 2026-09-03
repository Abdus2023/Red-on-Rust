# MOD-16 — MUTATION: Mutation registry and kill-rate gate

> Owns deliberate corruption: the frozen registry of known semantic defects, the
> 100% kill-rate gate, and the obligation to prove the verification system can
> detect what it claims to detect.

## SECTION-ID

`MOD-16` (domain `MUTATION`). Owner module file for the mutation obligations of
`TEST` (R-TEST-04, R-TEST-05, R-TEST-06).

## TITLE

Mutation testing — baseline registry M001–M018 (additive), kill-rate gate
(100% of registered non-equivalent mutants), survivor adjudication, and
self-validation of the verification system per registered mutation.

## PURPOSE

Keep the safety net honest. The frozen mutation registry encodes the historically
identified ways this machine's semantics can be *silently* wrong (reordered
evaluation, skipped prechecks, accepted revoked capabilities, omitted budget gates,
released escrow, doubled queue entries, tolerated gaps/checksums/digest mismatches).
Every such defect, once registered, becomes a permanent regression tripwire: the
verification machinery (MOD-14/15) must demonstrably kill all of them, and the
mutation framework must first prove it can kill them at all.

## NORMATIVE-CONTENT

Normative text home: `spec/01` S-21 (mutation portion); atomic renderings
`req/01-registry-part6-verification.md`. This module owns:

- **Baseline registry** (R-TEST-04): the versioned, frozen M001–M018 set (verbatim
  list in `spec/08` §2 and in `spec/01` R-TEST-04 — the registry statement is a closed
  set and is **not split** per `req/02-compound-not-split.md` discipline; per-mutant
  target modules are mapped, not re-authored, in `18-ownership-matrix.md` §5). The
  registry is **additive**: a previously killed mutant remains a regression
  requirement forever.
- **Kill-rate gate** (R-TEST-05): `MutationKillRate = 100%` for all registered
  non-equivalent mutations; any surviving non-equivalent mutant blocks verification;
  equivalent mutants require explicit adjudication and documentation; survivors are
  release-blocking defects (scope per C-32).
- **Self-validation** (R-TEST-06): the verification system itself is tested — for
  each mutation: inject, build, run targeted test, run differential suite, assert the
  mutant is *killed*; do not merely run the framework (15C.43 deliberate
  fault-injection validation, REQ-TEST-053).

Repository home (mirrored by pointer): `mutations/registry.toml` (+ `ror-testkit`
injection infrastructure; R-REPO-02/R-REPO-01).

## NON-NORMATIVE-CONTENT

- The README's 11-item example list (no IDs) is a non-exhaustive rendering (C-10);
  the numbered M001–M018 list is canonical.
- The turn-[49] category grouping is superseded presentation; IDs are the stable
  handles.
- "Kill rate" arithmetic is defined over the *registered non-equivalent* set;
  equivalent mutants are documented, not silently dropped (adjudicated per MOD-17's
  R-TEST-09 discipline).

## INPUTS

- The mutant definitions (frozen registry text) and their target requirements (per
  `18-ownership-matrix.md` §5: e.g. M001–M003 → MOD-05's R-CEK-05).
- Build/injection plumbing from MOD-17's infrastructure; the differential oracle from
  MOD-15.

## OUTPUTS

- Kill evidence per mutant (targeted test + differential assertion), survivor
  reports (release-blocking), equivalence adjudications (documented, with reasons).
- `MutationKillRate` measurement feeding M9 and the second conjunct of final
  acceptance R-TEST-11 (MOD-17).

## DEPENDENCIES

- Module dependencies: MOD-14 (oracle), MOD-15 (differential execution + kill
  evidence), MOD-17 (adjudication, CI staging, release blocking), plus every module
  whose obligations the registry targets (M001–M018 target table in the matrix).
- Consumers: MOD-17 (M9/M11 gates).
- Blocking open items: none originated here; blocked transitively by the open items
  of targeted modules (e.g. U-01 leaves duration-exhaustion behavior without a
  mutation target — AMB-01 notes "no mutation targets it").

## INVARIANTS

- Registry closure: M001–M018 frozen; additive only (R-TEST-04).
- `MutationKillRate = 100%` over registered non-equivalent mutants; survivors block
  release (R-TEST-05).
- Every registered mutation is injected, built, killed, and the kill asserted —
  before the *framework itself* is trusted (R-TEST-06).
- A killed mutant stays killed (regression permanence, R-TEST-04 additive rule).

## REQUIREMENTS

Canonical text: `spec/01` S-21. All 3 obligations `SPECIFIED`.

| ID | Obligation (short) | Provenance (`Red-on-Rust.md`) | Verification |
|---|---|---|---|
| R-TEST-04 | Baseline mutation registry M001–M018; additive | L38467–38513 (§19), L37239–37249 | registry review |
| R-TEST-05 | 100% kill rate (non-equivalent); adjudication for equivalents | L38494–38500, L37390–37400 | M9 gate |
| R-TEST-06 | Mutation validation (verification system tested) | L38515–38542 (§20) | framework tests; 15C.43 |

Atomic registry records under this module: REQ-TEST-012…019; REQ-TEST-053.
**3 obligations / 9 records.**

## SECURITY-BOUNDARY

Mutation testing guards the *guardians*: every registered mutant is a plausible
defect that observation alone might miss (e.g. M010 — allocate `EffectId` before
authorization — looks harmless until you notice the ID ordering is a causality
guarantee). The trust failure this module exists to detect is **vacuous testing**:
passing suites with no fault-detection power. Hence the gate is on *kills*, not on
coverage or suite size.

## VERIFICATION-OBLIGATIONS

- Owns the M9 gate: `MutationKillRate = 100%` for registered non-equivalent mutants;
  release-blocking survivor rule feeds R-TEST-10/R-TEST-11 (MOD-17).
- Per-mutant verification definitions and obligations live with the targeted module
  (each module file lists its mutations; the consolidated M001–M018 → module map is
  generated at `18-ownership-matrix.md` §5).
- Self-validation order (frozen rule): the framework proves kills against the
  differential oracle before any production-trust conclusions are drawn
  (R-TEST-06; anti-oracle-collapse linkage via MOD-14's REQ-TEST-048).
- Registry review mechanics (adding mutants = additive governance, R-CLAIM-02 #14
  adjacency).

## SOURCE-PROVENANCE

- Frozen registry + kill-rate + self-validation: [54] §19–§20 (L38467–38542);
  bootstrap registry restatement [58] (L40657–40719); 15D clarifications [49]
  (L37169–37338); 15C.43 fault-injection validation [48] (L37022–37053).
- Canonical set: `spec/02` S-21; `req/01-registry-part6-verification.md`.

## CROSS-REFERENCES

Owned here, binding elsewhere:

- R-TEST-04 → target modules: MOD-05 (M001–M003), MOD-03 (M004–M006), MOD-04
  (M007/M009), MOD-11 (M008/M015/M016), MOD-08 (M010/M017/M018), MOD-07 (M011/M012),
  MOD-06 (M013), MOD-10 (M014). The *defect definitions* are owned here; the
  *correct behavior* each mutant violates is owned by the target module — this module
  never re-states those behaviors (ids and reasons only, per no-duplication rule 4
  in `mod/00-overview.md`).
- R-TEST-05 → MOD-17 (survivors block release; equivalents adjudicated),
  MOD-15 (kill evidence production).
- R-TEST-06 → MOD-17 (`ror-testkit` injection infrastructure), MOD-14/15 (oracle).

Owned elsewhere, binding MUTATION: R-CLAIM-02 (MOD-17 — the prohibited-shortcut list
is the conceptual source pool for future mutants), R-TEST-10 (MOD-17 — the nightly/
release CI stages run this registry), R-TEST-07 (MOD-15 — mutation coverage attaches
to obligation tags). Open items: none owned; see dependency note re AMB-01.
