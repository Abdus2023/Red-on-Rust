# Red-on-Rust — Frozen Specification: Canonicalization Overview

**Document set:** `spec/00` … `spec/10`
**Source of record:** `Red-on-Rust.md` (42,312 lines; 60-turn design conversation, turns [1]–[60]) and `README.md` (the repository orientation document produced in turn [60]).
**Source state:** The source is a **frozen technical specification** carried inside a conversation transcript. It is *not* a clean specification document: it contains iterative drafts (capability algebra v0.1 → v0.2 → v0.3, operational semantics v0.2 → v0.3, canonical format 15A draft → revised → final frozen), explicit corrections that supersede earlier text, informal commentary, and Rust code sketches that alternate between normative and illustrative.

This document set splits the source into stable, independently addressable sections, normalizes its language, assigns stable identifiers to every normative unit, and separates claims by evidence status.

---

## 1. Method

1. **Acquisition.** The complete source was read in full coverage of its normative content (turns [1]–[60]).
2. **Version resolution.** Where the transcript revises itself, the **latest explicitly frozen or corrected text governs**. Superseded drafts are not deleted from the record; they are flagged in `06-contradictions-ambiguities.md` and marked `superseded` there. Nothing was silently dropped.
3. **Splitting.** The specification was divided into 24 sections (`S-01`…`S-24`) grouped into 8 parts. No mathematical invariant, theorem, API contract, or type definition was split across unrelated sections.
4. **Cleaning.** Terminology was normalized (see `05-terminology.md`, and — for the full normalization of record, with per-term `CANONICAL_TERM`/`FORBIDDEN_VARIANTS`/`DEFINITION`/`TYPE`/`OWNER`/`FIRST_DEFINITION`/`DEPENDENTS` and the complete collision register — `../term/00-overview.md`), modal language was made explicit (MUST / MUST NOT / SHOULD / informative), repetition was collapsed, and examples were isolated from normative text (informative examples are explicitly marked **Non-normative**).
5. **Obligation extraction.** Every normative requirement, invariant, theorem, API contract, serialization rule, persistence rule, and verification obligation received a stable ID (`R-…`). Provenance (turn number + line range in `Red-on-Rust.md`) is recorded per requirement in `03-obligation-matrix.md`.
6. **Consistency check.** Cross-references were checked; duplicates, contradictions, undefined terms, circular dependencies, and missing pre/postconditions were recorded in `06-contradictions-ambiguities.md` (IDs `C-…`). Items that require an explicit architectural decision were extracted to `09-unresolved-decisions.md` (IDs `U-…`). **Terminology collisions** — one name with two denotations, two names for one thing with neither retracted, a name used as a type but never declared, and a citation that does not point at the text it claims — are recorded separately in `../term/02-collisions.md` (IDs `X-…`), because the one resolution that is prohibited is renaming a frozen API, type, mathematical symbol or protocol field to make the collision disappear.
7. **Status discipline.** Every claim is labeled on the ladder below. **No claim was promoted beyond the evidence present in this repository.**

## 2. Status ladder (evidence discipline)

| Status | Meaning | Evidence required |
|---|---|---|
| `SPECIFIED` | Normative requirement exists in the frozen source. | Cite to `Red-on-Rust.md` (turn + line range). |
| `IMPLEMENTED` | Code in this repository realizes the requirement. | Source file(s) in this repository, mapped in `07-implementation-mapping.md`. |
| `TESTED` | A conformance/exercise test for the requirement exists and passes. | Test file + passing run, mapped in `08-verification-mapping.md`. |
| `VERIFIED` | Independent evidence (differential agreement, mutation kill, crash matrix) establishes conformance. | Verification artifact per `08-verification-mapping.md`. |
| `PROVEN` | A formal (mechanized) proof of the statement exists in the repository. | Proof artifact (e.g., mechanized theorem). |

Promotion is strictly evidence-gated: `SPECIFIED → IMPLEMENTED → TESTED → VERIFIED → PROVEN`. A specification requirement never confers `IMPLEMENTED` or higher.

**Current repository state:** this repository contains **no implementation, no tests, and no proof artifacts**. Its contents are specification and governance only: the frozen source (`Red-on-Rust.md`); this `spec/` register set; the terminology registers (`term/`); the obligation ownership and dependency registers (`mod/`, `dep/`); the atomic and compiled requirement registries (`req/`, `reg/`); the immutable historical audit snapshots (`audit/`); the derived canonical projections (`final/`); the disposition registry and repository-state projection (`state/`); and the single consistency-gate entrypoint (`check.py`). No Rust code, crate or workspace exists. Therefore **every obligation in this specification is at status `SPECIFIED` and no higher**. The README's "Implementation: IN PROGRESS / READY" wording is an orientation claim, not repository evidence, and is not treated as such here (see `C-09`). A `check.py` PASS is repository-integrity evidence only, never semantic verification of any obligation.

## 3. Identifier scheme

| Prefix | Meaning | Defined in |
|---|---|---|
| `S-NN` | Specification section (01…24) | `02-section-hierarchy.md` |
| `R-AREA-NN` | Normative requirement / obligation | `03-obligation-matrix.md` |
| `C-NN` | Contradiction / ambiguity / inconsistency finding | `06-contradictions-ambiguities.md` |
| `U-NN` | Unresolved item requiring an explicit architectural decision | `09-unresolved-decisions.md` |
| `M-NN` | Milestone (M0…M11, as defined in source) | `02` (S-23), `08` §4 |
| `TAG-NAME` | Source's own verification-obligation tags (e.g., `CEK-CALL-ARITY-PRECHECK`) | `08-verification-mapping.md` |
| `ROR-NNN` | Source's first-sprint task IDs (ROR-001…) | `07-implementation-mapping.md` |
| `M0NN` | Mutation-registry IDs (M001…M042: M001–M018 baseline; M019…M035 added by frozen addenda I–V; M036 the U-38 gate adoption; M037–M042 added by addenda VII–IX) | `08-verification-mapping.md` |
| `T-NN` | Canonical terminology entry (T-01…T-86) | `../term/01-dictionary.md` |
| `N-NN` | Non-conflation law: two terms that must never be used for each other (N-01…N-33) | `../term/03-laws.md` |
| `X-NN` | Terminology collision, cited to a frozen-source line (X-01…X-87) | `../term/02-collisions.md` |

`T-`/`N-`/`X-` are **additive**: they were introduced by the terminology normalization pass and renumber nothing above. An `X-NN` entry is the terminology-layer counterpart of a `C-NN` entry — where an `X-` finding extends or corrects an existing `C-`/`U-`/`AMB-` record it says so in its *Previously registered as* field, and the earlier record is left in place. `term/_check.py` re-greps every `X-` citation against `Red-on-Rust.md` and fails on drift.

## 4. The two governing invariants (carried into every section)

**Trust model.** The evaluator/runtime is the security boundary. The Red-like language (its `Block` data) is **not** a security boundary. The LLM is a probabilistic proposal engine and **never an authority**:

```
LLMOutput ∧ UntrustedInput ↛ ExternalEffect
```

**External-effect chain.** An external effect requires the complete chain of validation, authority, resource, policy, durability, and issuance checks:

```
ExternalEffect(E) ⇒ ValidatedRequest(E)
                  ∧ Authorized(E, κ, t)
                  ∧ CapabilityWithinCeiling(E)
                  ∧ BudgetAvailable(E)
                  ∧ DeadlineValid(E, t)
                  ∧ HostPolicyOK(E)
                  ∧ Issued(E)
```

(Provenance: `Red-on-Rust.md` L27485–27517 (turn [33] §23), restated in `README.md` "Core Thesis" and turn [60]. First conjunct per the frozen addendum R-CORE-11 — `ValidatedRequest(E)` is the canonical first predicate and subsumes `ValidatedPlan(plan(E))`; the source's `ValidatedPlan(P)` first conjunct at those lines is superseded by R-CORE-11, quoted not deleted.)

## 5. How to use this document set

1. **Read `01-canonical-specification.md`** for the cleaned normative text, organized by section with inline requirement IDs.
2. **Track a requirement** via its `R-…` ID: definition in `01`, dependencies in `04`, implementation home in `07`, test/evidence mapping in `08`.
3. **Check risk** via `06` (contradictions/ambiguities) and `09` (unresolved decisions). These are the items where implementation MUST stop and seek an explicit specification decision (per the frozen "STOP and report" rule, source L37690).
4. **Machine processing** uses `10-index.json`, which is the authoritative cross-index of sections, requirements, findings, unresolved items, and status.
5. **Architectural view** uses `../mod/`: the same obligations partitioned into 17 semantic modules (`MOD-01`…`MOD-17`) by architectural responsibility, with one canonical owner per obligation, explicit cross-references, and a marked-duplication register (`D-01`…`D-12`). Normative text stays here in `01`; `mod/` registers ownership and contracts and never restates it.

## 6. Normative conventions used in this document set

- MUST / MUST NOT / SHOULD follow RFC 2119.
- Text marked **Non-normative** (examples, golden vectors, sketches) is explanatory. Golden vectors are **test fixtures**, not behavioral definitions, except where the source explicitly freezes a byte-level grammar (S-17).
- `≻` ordering of source versions: later frozen text supersedes earlier draft text; supersession is always recorded in `06`.
- Math symbols keep the source's notation: `≼` (authority order), `⊓` (meet), `κ` (capability map), `Σ` (machine configuration), `G` (global state), `B`/`C`/`R`/`W` (budget), `t` (logical time).
