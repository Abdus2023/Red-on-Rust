# Red-on-Rust — Terminology Normalization: Overview

**Document set:** `term/00` … `term/10`
**Source of record:** `Red-on-Rust.md` (42,312 lines; 60-turn design conversation, turns [1]–[60]) and `README.md` (the turn-[60] orientation document).
**Data of record:** `term/_terms.py`. Every markdown file in this directory except this one is **generated** from it by `term/_dict.py` and re-verified against the frozen source by `term/_check.py`.
**Relationship to `spec/05-terminology.md`:** `spec/05` is the glossary the canonical specification carries. This directory is the *normalization* of it — a superset that adds the seven required fields per term, the non-conflation laws, and a complete collision register. Where the two disagree, the disagreement is itself filed as a collision (see §6) and `spec/05` is corrected with provenance rather than silently overwritten.

| File | Contents | Status |
|---|---|---|
| `00-overview.md` | this document — method, guarantees, how to read an entry | hand-written |
| `01-dictionary.md` | the 81 canonical terms, with all seven required fields | generated |
| `02-collisions.md` | the 75-entry collision register, each cited to a frozen line | generated |
| `03-laws.md` | the 31 non-conflation laws the required distinctions imply | generated |
| `10-index.json` | machine-readable index of all three | generated |
| `_terms.py` | the data of record | hand-written |
| `_dict.py` | generator: `_terms.py` → markdown + JSON | hand-written |
| `_check.py` | checker: re-derives every fact from `Red-on-Rust.md` | hand-written |

---

## 1. What was asked for, and what this delivers

The request was to normalize terminology across Red-on-Rust, to build a canonical dictionary in which **every** term carries

> `CANONICAL_TERM`, `FORBIDDEN_VARIANTS`, `DEFINITION`, `TYPE`, `OWNER`, `FIRST_DEFINITION`, `DEPENDENTS`

under one hard constraint —

> **Do not silently rename an API, type, mathematical symbol, or protocol field.**

— to enforce nine distinctions as separate canonical terms, to name 26 required terms, and to **report every terminology collision**.

All seven fields are present on all 81 terms. All nine distinctions are enforced as laws (§4) and, where the source itself conflates them, filed as collisions (§5). 86 collisions are reported, including 4 that block work.

**The request lists 25 required names; the dictionary realizes them as 26 canonical terms.** `Observation` maps to two — `Observation (planner-facing)` (T-54) and `Observation (differential)` (T-57) — because the frozen source declares two incompatible structs under that one name: `{sequence, actor, value, events, faults, available_capabilities, budget}` at L27156 and `{terminal_states, event_trace, effects, budgets, scheduler_trace, faults, …}` at L36170. Covering the name with a single entry would have been exactly the conflation the request asks to be reported, so it is split and the split is filed as X-06 with the law N-22 beside it. `term/_check.py` verifies the mapping both ways: every one of the 25 names maps to at least one term, each mapped term's canonical name contains the request name, the union is exactly the 26 required terms, and no term is claimed by two names. The remaining 24 names map one-to-one:

| Required name | Term | | Required name | Term |
|---|---|---|---|---|
| Block | T-01 | | LogicalTime | T-28 |
| PlanProposal | T-02 | | ActorId | T-34 |
| ParsedBlock | T-03 | | ActorStatus | T-35 |
| ValidatedPlan | T-04 | | WAL | T-45 |
| CapabilityCheckedPlan | T-05 | | Snapshot | T-48 |
| ExecutablePlan | T-06 | | EffectJournal | T-23 |
| CapRef | T-09 | | ReplayHost | T-42 |
| Authority | T-10 | | HostPolicy | T-41 |
| Effect | T-16 | | Budget | T-24 |
| EffectRequest | T-17 | | Consumable | T-25 |
| EffectIssued | T-18 | | Reserved | T-26 |
| EffectReceipt | T-19 | | **Observation** | **T-54 + T-57** |
| EffectId | T-20 | | | |

The other 55 terms are not required by name but are load-bearing: the ones the required terms are defined in terms of (`EffectDigest` T-21, `Constraint` T-12, `CapabilityKernel` T-13, `CapabilityError` T-72), the ones a required distinction needs (`LLMOutput` T-56, `ReferenceModel` T-58, `Implementation` T-65, `Verification` T-66, `Proof` T-67, `EvidenceStatus` T-68, `Frozen` T-69), and the ones the collisions turn on (`Value` T-31, `Expr` T-30, `Frame` T-33, `GlobalState` T-38, `WalRecord` T-47, `CanonicalEnvelope` T-62, `CanonicalPayload` T-63, the five fault-taxonomy types added by the fault audit — `Fault` T-70, `GlobalFault` T-71, `MarshalFault` T-73, `HostFault` T-74 — and the four type families the declaration sweep found with no term of record at all: `MachineEvent` T-75, `CanonicalError` T-76, `StepResult` T-77 and `ControlFrame` T-78).

The hard constraint shaped the whole method: **a canonical term is a name an author must use, never a new identifier to introduce.** No entry in this dictionary coins a replacement for a frozen API, type, symbol or protocol field. Where the source froze two names for one thing, both are recorded; where it froze one name for two things, both denotations are recorded; where a name is used but never declared, that is reported rather than filled in.

## 2. Method

1. **Attestation before definition.** Every term was located in `Red-on-Rust.md` by case-sensitive search, then read in context at each declaration site. No `FIRST_DEFINITION` is a raw first grep hit: each was confirmed by reading the line. `term/_check.py` re-greps all 803 citations on every run and fails if a quoted token is not on the line it is cited to.
2. **Turn attribution from the source's own markers.** Turns are derived from the `## [n] USER` / `## [n] CHATGPT` headings in `Red-on-Rust.md`, not assumed. The checker verifies that an anchor's claimed turn really contains its line.
3. **Version resolution.** Where the transcript revises itself, the **latest explicitly frozen or corrected text governs** — the same rule `spec/00` §1.2 applies. Superseded forms are *recorded*, never deleted: each term carries a `SUPERSEDES` list quoting the earlier declaration verbatim with its line numbers.
4. **No invention.** A name that is used as a type but never declared is entered with `TYPE: UNDECLARED-TYPE` and given **no** invented definition. The checker fails if a `PROTECTED` name occurs in neither the frozen source nor the canonicalization layer, so the dictionary cannot protect an identifier it made up.
5. **Bidirectional linking.** `Term.collisions` and `Collision.affects` are checked against each other in both directions; 369 links, zero asymmetries, zero dangling `T-`/`N-`/`X-` references.
6. **Collisions are reported, not resolved.** Each carries a **Disposition** saying what the canonicalization layer does — usually "record both, name the governing text" — and a **Decision needed** field where the source does not settle the question. Nothing is merged, renamed or dropped to make a collision disappear.
7. **The canonicalization layer is in scope.** Five collisions (X-39…X-41, X-59…X-63) are defects in *this repository's own documents* — a wrong field list in `spec/05`, an alias claim the source does not support, four citations in `spec/06` that point at unrelated text, a phantom identifier in `req/03`, and a false heading claim in `req/00-method`. These are cited by `file:line` in a separate evidence table so a reader can check the claim against the document rather than the transcript.

## 3. How to read a dictionary entry

```
### T-09 — `CapRef`
*Required term.*                                     ← one of the 26 the request names

- CANONICAL_TERM:  CapRef                            ← the name an author must use
- TYPE:            RUST-STRUCT                       ← what kind of thing it is (19 kinds)
- OWNER:           MOD-03 (ror-kernel)               ← module and crate that own it
- DEFINITION:      …                                 ← normative prose, no invented content
- FIRST_DEFINITION: `L915`, turn [3] — `pub struct CapRef(pub(crate) u64);`
- FROZEN_AT:        `L9131`, turn [17] — `pub struct CapRef {`
- DEPENDENTS:      T-10 `Authority`, T-11 `AuthorityNode`, …
- FORBIDDEN_VARIANTS:                                ← names that must NOT be used for it
    - `capability token`
    - `authority handle`
- PROTECTED (do not rename):                         ← frozen identifiers, verbatim
    - `CapRef` — frozen Rust type name; also 15A standalone tag `0x30`
    - `index` — frozen field name
- FROZEN SHAPE:    pub struct CapRef { index: u32, generation: u32 }
- SUPERSEDES:      pub struct CapRef(pub(crate) u64);   // L915, L3646, L5034, L5949
- OBLIGATIONS:     R-CAP-01, R-CAP-05, R-KERN-03, R-MARSHAL-01, R-CORE-07
- COLLISIONS:      X-05, X-25, X-26, X-27, X-36, X-38
- LAWS:            N-03
- NOTE:            …
```

`FIRST_DEFINITION` is where the term first appears in the frozen source; `FROZEN_AT` is where the form that governs today appears. They differ for 39 terms, and the difference is the version history — `CapRef` was a single `u64` in turn [3] and a `{index, generation}` pair from turn [17]. Both are quoted; neither is renamed.

`FORBIDDEN_VARIANTS` has two kinds of entry, and the dictionary does not blur them:

- **Attested** variants the source itself used and later superseded (`capability handle`, `GlobalConfig`, `PlanIR` as an alias of `ExecutablePlan`). These are real collision risks — a reader will meet them in the transcript.
- **Prophylactic** variants that occur nowhere (`price` for `Cost`, `inbox` for `Mailbox`, `watchdog` for the recovery sweeper). These forbid a *future* drift. `term/_check.py` reports each of the 11 as a warning so the two kinds stay distinguishable.

**Six canonical terms are labels, not identifiers.** `Observation (planner-facing)` (T-54), `Observation (differential)` (T-57), `ReferenceModel` (T-58), `FirstDivergence` (T-59), `CanonicalEnvelope` (T-62) and `EvidenceStatus` (T-68) do not occur verbatim in the frozen source: the source has two structs both named `Observation`, prose about "the reference model" and "the first-divergence algorithm", a byte format it never names with one token, and a record field it writes `EVIDENCE-STATUS`. Each of the six is rendered under an explicit banner saying so, naming the frozen identifier it labels, and stating that introducing the label into code, a protocol or a formula would itself be a prohibited rename. `term/_check.py` warns on exactly these six and no others.

## 4. The nine required distinctions

Each is enforced as a law in `03-laws.md`, and each has a **bridge** — a frozen formula or record kind that makes the distinction checkable rather than merely lexical.

| Distinction | Law | Bridge in the frozen source |
|---|---|---|
| `Block ≠ ExecutablePlan` | N-01 | `ExecutablePlan` carries `_sealed: Sealed` and is private to `mod compiler`; a raw `Block` has no path into `step()` (L9115) |
| `PlanProposal ≠ ExecutablePlan` | N-02 | `PlanProposal` *contains* a `Block` (L27175); the planner cannot bypass compilation (L27271-27285) |
| `CapRef ≠ Authority` | N-03 | `AuthOK(c,E,t) ⇔ Valid(c,t) ∧ Authorized(Authority(c),E,t)` (L7323) — authority is obtained *from* the ref, it is not the ref |
| `EffectRequest ≠ EffectIssued` | N-04 | `EffectRequest` is transient, `EffectIssued` is the durable fact of commitment (L23756-23772); `WalRecord::EffectPrepared` precedes `WalRecord::EffectIssued` |
| `EffectIssued ≠ EffectCompleted` | N-05 | `Completed(E) ⇒ Issued(E)` and `Issued(E) ⇒ Prepared(E)` (L35139-35142); distinct WAL kinds with distinct payloads |
| `Specification ≠ Implementation` | N-06 | status ladder `SPECIFIED → IMPLEMENTED`; this repository has no implementation, so nothing is above `SPECIFIED` |
| `Implementation ≠ Verification` | N-07 | R-SCOPE-04 zero shared core logic (L37696); "testing an implementation against its own buggy logic merely proves consistency, not correctness" (L11779) |
| `Verification ≠ Proof` | N-08 | "machine-checked evidence of refinement … formal proof obligations remain separately identified" (L28263) |
| `LLM output ≠ Authority` | N-09 | `LLMOutput ∈ Data`, **not** `LLMOutput ∈ Authority` (L27253-27260) |

N-10…N-31 extend the same discipline to the 26 required terms and to the pairs the source itself separates but never names: `Observation (planner-facing) ≠ Observation (differential)`, `EffectJournal ≠ WAL ≠ EventLog`, `LogicalTime ≠ wall-clock time`, `Frozen ≠ Verified`.

## 5. The collision register

86 collisions: **4 BLOCKING**, 62 MAJOR, 19 MINOR, 1 INFO. 83 are new findings; 3 extend or correct an existing `C-`/`U-`/`AMB-` entry and say so. X-64…X-68 come from a fault-taxonomy audit that re-read every `Fault`-family declaration, X-69…X-75 from the enum-variant sweep, and **X-76…X-86 from the exhaustive struct-field sweep** that `term/_structs.py` now re-derives mechanically: 272 struct declarations across 90 names, of which **22 names carry more than one non-elided field set**, and 108 enum declarations across 39 names, of which **11 carry more than one variant set**. Eight of the 22 divergent struct names were already filed (`Block` X-28, `CapRef` X-25, `Effect` X-26, `EffectRequest` X-27, `ExecutablePlan` X-03, `Observation` X-06, `ReplayHost` X-43, `ValidatedPlan` X-01) and ten of the 11 divergent enums were already filed; the remainder are X-76…X-86. One divergence was deliberately **not** filed: `EffectCost.complete` versus `complete_max` (L21390 versus L25477) is already resolved by `spec/01` R-CALC-05's Phase 12 correction, so filing it again would duplicate a resolved row. The same sweep **corrected six existing entries** in place — X-26, X-37, X-43, X-46, X-47 and X-72 (§6) — two of which were wrong: X-37's `AuthorityNode` is declared three times, not once, and is not always elided; X-72's four shapes are four variant sets but five payload shapes.

**The four blocking collisions** must be decided before the work they gate can start:

| ID | Collision | Blocks |
|---|---|---|
| X-01 | `ValidatedPlan` is a declared stage **type** *and* the predicate of the central theorem `ExternalEffect(E) ⇒ ValidatedPlan(P) ∧ …` — a type used where a proposition is required | the statement of R-CORE-02; any mechanization of the external-effect chain |
| X-50 | the canonical envelope is specified twice with different field names, tag widths and endiannesses: `[format_version:u8][type_tag:u32 LE][length:u32 LE]` (L28298, inside the `CanonicalSerialize` doc comment) vs the frozen `version:u8 \| type_tag:u8 \| payload_length:u32 BE \| payload` (L38147–38150, L33816) | milestone M1 — every digest, golden vector and WAL frame |
| X-54 | `TAG_BOOL`/`TAG_INTEGER`/`TAG_STRING`/`TAG_SYMBOL` are envelope type tags (0x10/0x11/0x12/0x20) in turn [41] and `Value` variant discriminants (0x01/0x02/0x03/0x04) in turns [43]–[45]; one function needs both (L33194-33195) | milestone M1 — the two const blocks cannot coexist unqualified |
| X-67 | `pub enum HostFault` is declared **once** (L10820, turn [18]) with two variants — `IoError(String)`, `PolicyViolation(String)` — while **eight undeclared** `HostFault::` paths are used and neither declared variant is ever used. Six of the uses are on the frozen 15C.42 `ReplayHost` (L35225–35227, turn [47]) that R-HOST-03/04/05 and REQ-HOST-007/008 are written against | MOD-09 host gate, ordered replay, `term/` T-42 `ReplayHost`, T-44, T-74; `req/03` AMB-33; U-14 |

X-50 and X-54 are adjacent and neither is covered by the existing `C-02`, which concerns stale *primitive* tags in one section. X-50 is a contradiction **inside an API contract comment**, which is the first place an implementer looks; X-54 makes two frozen const blocks mutually uncompilable. X-67 is blocking for a different reason: it is not a choice between two frozen texts but the absence of any frozen declaration for the error type the replay path returns, so the host error enum cannot be written at all without inventing variants — which R-SCOPE-03 prohibits. `ReplayCorruption` compounds it by denoting a fault at two levels at once (a declared `Fault` variant at L23814 *and* an undeclared `HostFault` path used six times).

The register's fifteen kinds are: `TYPE-HOMONYM`, `TYPE-ROLE-HOMONYM`, `FIELD-SET`, `SYMBOL-OVERLOAD`, `PREDICATE-SIGNATURE`, `STAGE-ORDER`, `STATE-VS-RECORD`, `UNDEFINED-TYPE`, `METHOD-SIGNATURE`, `ALIAS-DEFECT`, `SCOPE-DRIFT`, `PROVENANCE-DEFECT`, `PHANTOM-IDENTIFIER`, and two added by the declaration sweep — `UNDECLARED-VARIANT` (an `Enum::Variant` path used in the frozen source but present in no declaration of that enum) and `DIVERGENT-SHAPE` (one type name declared repeatedly with materially different variant or field shapes).

Five collisions are about **this repository's own documents** rather than the transcript — `ALIAS-DEFECT` and `PROVENANCE-DEFECT` entries whose evidence tables cite `spec/`, `mod/`, `req/` and `README.md` by file and line. They are listed in §6 because each one required a correction to a document outside `term/`.

## 6. Corrections made outside `term/`

Supersession is never silent (R-SCOPE-03). Every correction below is **additive**: the superseded wording is quoted in place rather than deleted, the `X-` id that justifies the change is cited in the document itself, and no obligation ID is renumbered, no requirement re-homed, and no source identifier renamed. Line numbers cited by `term/`'s own evidence tables were preserved wherever possible; where a document legitimately grew, the affected `doc_site` was updated in `term/_terms.py` and the checker re-verified it (`req/00-method.md` 219→220, `README.md` 708→729).

| Document | What changed | Why |
|---|---|---|
| `spec/00-overview.md` §1.4, §1.6, §3 | `T-NN`/`N-NN`/`X-NN` added to the identifier scheme as **additive** prefixes; the method's cleaning and consistency-check steps now point at `term/` and explain why terminology collisions are registered separately from `C-` findings | this document set |
| `spec/05-terminology.md` L13 | the `ExecutablePlan` row no longer lists `ValidatedPlan`, `CapabilityCheckedPlan` and `PlanIR` as aliases, and no longer calls the pipeline names "stage names"; the superseded wording is quoted inside the correction | X-40 |
| `spec/05-terminology.md` L14 | `Effect`'s field set corrected from `{capability, operation, target, params, cost}` to the frozen `{op, target, params, cost}` (L9297) | X-39 |
| `spec/05-terminology.md` L62 | the trait cell now names all four declared traits and records that `CanonicalSerialize` is also a mathematical function symbol | X-51 |
| `spec/05-terminology.md` L63 | the `Envelope` row states the frozen form and the contradicting doc-comment form side by side, and separates envelope type tags from `Value` discriminants | X-50, X-54, X-56 |
| `spec/05-terminology.md` L69, L109 | `ReconciliationOutcome`'s variants are stated as enumerated (L26593–26597); the §7 row is struck, not deleted, and U-15 is marked narrowed | X-61 |
| `spec/05-terminology.md` §6.11–6.14, §8 | four normalization rules added (label-vs-identifier, tag namespaces, undeclared types, reference machine vs reference model) and a new §8 names `term/` as the normalization of record | X-48, X-54, X-29 |
| `spec/01-canonical-specification.md` after R-REPO-02 | a **non-normative** note added beside the crate-contract pipeline; the normative bullet at L479 is unchanged | X-02, X-41 |
| `mod/02-compiler.md` NON-NORMATIVE-CONTENT | the bullet claiming stage names are "not artifacts in their own right" is corrected, with the two declared stage structs quoted; two bullets added on the three pipeline orderings and on `ValidatedPlan` as a predicate | X-40, X-41, X-02, X-01 |
| `spec/06-contradictions-ambiguities.md` | **twenty** rows added, **C-46…C-65** (4 BLOCKING, 15 MAJOR, 1 MINOR), each cross-referenced to its `X-` entry. The C-09 row carries an annotation (X-59). The **C-08 row was rewritten**: its severity is raised MINOR → MAJOR, its four citations are corrected to the verified sites, its “four names” count is corrected to nine, its false “inner `CapabilityError` variants are undefined” gloss is corrected — and a claim an earlier revision of *this pass* had added to that row is **withdrawn** (see below). The **C-54 row was rewritten a second time**: first filed as a phantom-identifier finding on the false claim that `Fault::StalePlan` occurs nowhere, now filed as a used-but-undeclared variant with the false claim quoted. **C-59…C-65** come from the declaration sweep; C-60 is deliberately framed as an extension of X-29/AMB-11/C-16 rather than a new finding, because the declaration gap was already recorded and only its consequence for Theorem 2 was not | X-38, X-58, X-59, X-64…X-75 |
| `spec/09-unresolved-decisions.md` | U-15's false premise corrected in place and the decision narrowed to per-class admissibility; **U-23, U-24, U-25** added in their own section; **U-26, U-27, U-28, U-29** added in their own section by the declaration sweep (`StepResult` name ownership, `ActorStatus` governing shape and continuation location, `MachineEvent` vocabulary, `CanonicalError` governing shape), with a process note recording that all four are blocking for a conformance test rather than for a milestone gate; **U-08's “State of source” corrected in place** (four denial names → nine; “the inner `CapabilityError` / `HostPolicyError` / `EffectError` / `HostFault` variants are not enumerated” → only `HostPolicyError` and `EffectError` lack a declaration); **U-14 escalated** from a cosmetic enumeration task to blocking for `HostFault` | X-38, X-59, X-61, X-64…X-68 |
| `req/00-method.md` §5.4 | "there is no `# 15C.1` heading" corrected and quoted; the missing **15C.1 row** added to the coverage table; the section count corrected 45 → 46 | X-60 |
| `req/03-ambiguous.md` | AMB-24's README citations corrected to L12 and L735 — they were first corrected to L708, which this pass invalidated by adding the README's `term/` paragraph, and then to L732, which the declaration sweep invalidated by extending that same paragraph, so the block is now cited by its `# Project Status` heading (L732) as well as by line — with the defective ranges kept; AMB-25's phantom `PlannerState` struck and quoted; **AMB-08 corrected in place** (`StalePlan` removed from the list of the L23806 enum's variants — it is in none of the seven declarations — but recorded as a source-used fault name at L28373/L27236 rather than as a phantom, the earlier “struck as phantom” wording being itself qualified and quoted; the v0.3 name citation moved from L8748–8757 to L8758; the `IsolationBreach` → “a `Capability` reason” mapping withdrawn; the evidence range L23806–23824 narrowed to L23806–23816); **AMB-30, AMB-31, AMB-32** added, then **AMB-33 (blocking), AMB-34, AMB-35** added by the fault-taxonomy audit, with **AMB-34 then rewritten** by the declaration sweep from “asserted but undeclared phantom” to “used by the source, declared by none of the seven `Fault` enums”; **AMB-36, AMB-37, AMB-38, AMB-39** added by the declaration sweep (`MachineEvent`, `CanonicalError`, `StepResult`, `ActorStatus` shapes); §3 counts updated 28 → 31 → 34 → **38** ambiguities and 45/16 → 53/19 → 65/19 → **65/23** cross-references | X-59, X-62…X-69 |
| `req/_validate.py` | the expected register sizes updated **45 → 53 → 58 → 65** `C-` rows and **16 → 19 → 23** `U-` headings, with a comment naming the pass, the audit and the sweep that grew them, so the change is recorded and not silent drift. This checker also caught the pass introducing three identifiers (`Revoked`, `Expired`, `InvalidConstraint`) into REQ-CALC-013's INVARIANTS that were outside its cited ranges; the record's SOURCE line was extended to L20408–20413, L20451 and L20835 rather than the tokens being dropped | X-59, X-66, X-69…X-75 |
| `README.md` | L29 and L32 counts and the `term/` paragraph (L61–L86) updated (64 findings in 65 rows; 23 open decisions; 38 open ambiguities; 78 canonical terms; 75 collisions; 803 citations re-grepped) and a `term/` paragraph added after the `dep/` paragraph describing the four generated files, the nine enforced distinctions and the standing verifier | X-52, X-53, X-63, X-69…X-75 |
| `spec/01-canonical-specification.md L138 (R-CALC-06)` | a **non-normative annotation** appended to the same line, **first written on a false premise and then corrected**: it now records that `StalePlan` is in none of the seven `pub enum Fault` declarations *but is used by the source* (`Fault::StalePlan`, L28373), so the parenthetical “plus `StalePlan` at the planner boundary” is **source-supported and stands**; the earlier wording asserted that `Fault::StalePlan` “occurs nowhere”, which is false, and is quoted as withdrawn. The annotation also records that the frozen set is not closed (L23807 is an explicit `// ... (previous faults)` elision) and that `HostFault` in `Host(HostFault)` is the type with the eight-undeclared-variant gap. **The normative sentence is unchanged and still governs** | X-64, X-67, X-68, X-69 |
| `spec/05-terminology.md L112` | the U-14 row corrected in place: `CapabilityError` **is** declared (L20408) and so is `HostFault` (L10820); only `HostPolicyError` and `EffectError` lack a declaration. The real defects are narrower and worse — `CapabilityError::Invalid` (L20835) vs the declared `InvalidConstraint` (L20451), and eight undeclared `HostFault` paths | X-59, X-66, X-67 |
| `spec/08-verification-mapping.md L63` | the marshalling-isolation test row's status cell changed from `NONE` to “NONE — **blocked**”, naming the two disjoint `MarshalFault` declarations, so a test that cannot yet assert a determined fault value is not presented as unblocked | X-65 |
| `spec/_build_index.py L203` | the generated index's C-08 row corrected: severity `MINOR` → `MAJOR` and the line list `1995;7363;7435;23784` → the verified `1042;937;7374;23806-23816`, with the re-grading and the citation defect named in the row's own text; `spec/10-index.json` regenerated | X-38, X-59 |
| `req/01-registry-part2-semantics.md L181, L186, L197, L199` | REQ-CALC-013's INVARIANTS corrected in place (“closed set; inner variants not enumerated” is false on both halves) and its SOURCE extended to the `CapabilityError` declaration and both contradictory use sites; **REQ-CALC-014's STATEMENT (L197) and POSTCONDITIONS (L199) were first rewritten and withdrawn on the false premise that `Fault::StalePlan` occurs nowhere, and are now restored** — the statement is source-supported at L28373 and stands as written, with the withdrawn wording quoted in each field and the real defect (the variant is declared by none of the seven `Fault` enums) recorded beside it | X-59, X-64, X-66, X-69 |
| `req/01-registry-part1-foundations.md L301` | the REQ-MARSHAL postcondition annotated to record that it cites only the turn-[32] `MarshalFault` declaration and that a disjoint turn-[18] declaration exists with no stated supersession | X-65 |
| `req/01-registry-part4-durability-concurrency.md L316` | REQ-HOST-008's dependency note corrected in place: it attributed the missing `ReplayTraceExhausted` variant to the frozen `Fault` enum, when it is a `HostFault` path and the gap is eight variants wide | X-67 |
| `mod/06-actor.md OUTPUTS, mod/09-host.md R-HOST-03` | a note appended to each bullet (no existing line altered): `mod/06` records the two disjoint `MarshalFault` declarations and the elided `MarshalFault(...)` payload at L26871; `mod/09` records that `ReplayCorruption`/`ReplayTraceExhausted` are `HostFault` paths and that `pub enum HostFault` declares neither | X-65, X-67 |
| `term/_terms.py T-70…T-74` | five terms the first pass missed entirely, all in the `Fault` family: `Fault`, `GlobalFault` (a second, disjoint taxonomy for the global machine step, mentioned nowhere in the canonicalization layer), `CapabilityError`, `MarshalFault`, `HostFault`. X-58's and X-59's `affects` lists were also repaired — they pointed at `Frame` and `ActorId` because no `Fault` term existed to point at | X-58, X-59, X-64…X-68 |
| `term/_terms.py T-75…T-78` | four type families the declaration sweep found with **no term of record at all**: `MachineEvent` (eight declarations; the event vocabulary the trace, the WAL and the differential comparison are built on), `CanonicalError` (seven declarations in four shapes, on the same path where X-50 is blocking), `StepResult` (two disjoint enums — the CEK machine's and the actor scheduler's — sharing one name, with no variant in common), and `ControlFrame` (the control stack, whose three declared variants reference `PlanIR`, `FuncRef` and `EffectSignature`, none of which is declared either) | X-71…X-75 |
| `term/_terms.py X-29, T-31, T-35, T-36, T-70, T-73` | X-29 gains the two `Expr::Delegate` use sites AMB-11 did not list (L26058, in Theorem 2's proof; L26078, property-test matrix row C); T-35's note is rewritten from “two incompatible declarations” to **seven declarations in three shapes**, with the movement of the `Continuation` payload traced; seven undeclared `Fault::` paths are added to T-70's `PROTECTED`, `Value::Null` and `Value::DelegatedCapability` to T-31's, `NotRunnable` (declared L24300, silently dropped at L25526) to T-36's, and `CorruptedPayload` to T-73's — every one as a *source-used spelling*, none normalized away | X-69, X-70, X-74, X-75 |

| `term/_structs.py` | **new checker** (this pass): re-derives every `struct` and `enum` declaration in `Red-on-Rust.md` — 272 struct declarations across 90 names, 108 enum declarations across 39 names — keying a shape on the SET of `(field name, field type)` pairs with visibility, module paths and field order normalised out and elided bodies (`{ ... }`, `/* ... */`, `// ... other fields`) bucketed separately, so no visibility-only or path-only difference is ever reported as a field-set divergence. Three modes: default (struct field sets), `--enums` (variant sets), `--undeclared` (type names used in field positions that are declared nowhere) | every "declared *n* times in *m* shapes" claim in the register was previously eyeballed; two were wrong, and the checker's first version was wrong twice more (it merged `Authority`'s L4360/L4979 declarations because it keyed on field NAMES only, and it lost fields whenever a prose comment contained a comma) |
| `term/_terms.py X-26, X-37, X-43, X-46, X-47, X-72` | six existing entries extended or corrected **in place**, each saying so in its own text: X-26's three `Effect` field sets are five, in ten declarations, and the capability reference disappears after turn [3] and returns as `capability` at turn [29]; X-37's "`AuthorityNode` once with its fields elided" is three declarations — L9702 with four fields, L39373 and L39940 elided, the latter showing `pub` immediately above the prose "must NOT be public" — and its seven `Authority` declarations carry six field sets; X-43's two `ReplayHost` forms are six, with three field names and four element types, and its severity is raised MINOR → MAJOR; X-46 gains the actor table's three container types (`ActorTable`, `HashMap`, `BTreeMap`); X-47 gains `EffectSequence`, an undeclared third sequence name one letter from the declared `EventSequence` and sitting beside it in `GlobalSnapshot`; X-72's four shapes are four variant sets but five payload shapes — `LengthMismatch.expected` is `u32` at L30664 and `usize` at L32086/L32962/L33302 | supersession is never silent (R-SCOPE-03): the superseded wording is quoted rather than deleted, each correction names the checker that produced it, and no count was lowered — X-43's severity went UP |
| `term/_terms.py T-79…T-81, N-28` | three terms the sweeps found with **no term of record at all**: `MarshalledValue` (T-79 — the isolation boundary's payload, five declarations, two payloads, and frozen API on both sides), `RefState` (T-80) and `RefAuthority` (T-81), the differential oracle's state and authority. N-28 gains four evidence sites: L6535's doc comment "Constraint: distinct from Authority", L6501's body which L6536 duplicates character for character, L6686's five-field `Constraint`, and L485's use of `Constraint` in turn [2] nine turns before its declaration | a required distinction the request names explicitly (`Constraint ≠ Authority`, enforced as N-28) is contradicted by the frozen declarations themselves; the law and the contradicting evidence now sit in one view |
| `spec/06-contradictions-ambiguities.md` | **eleven** rows added, **C-66…C-76** (10 MAJOR, 1 MINOR), one per new `X-` entry and cross-referenced to it (C-66↔X-76 … C-76↔X-86); the summary-count line rewritten to 74 findings in 76 rows, 31 open | the contradictions register is where a reader looks first; a finding filed only in `term/` would be invisible to that reader |
| `spec/09-unresolved-decisions.md` | **U-30…U-34** added in their own section before the process notes: `MarshalledValue`'s payload; `Authority`'s and `Constraint`'s field sets and the kernel's arena; `WalFrame`'s `payload_length` and checksum domain; the reference model's governing declarations and its twelve undeclared `Ref*` types; the turn-[31]/[32] state structs | five of the eleven new findings cannot be closed by reading more text — they need an architectural ruling, and each names what it blocks |
| `req/_validate.py` | the expected register sizes updated **65 → 76** `C-` rows and **23 → 28** `U-` headings, with the comment naming the sweeps that added them | as before: changing a checker's expectation is the kind of edit that can hide drift, so it is done in the open with the reason in a comment |
| `README.md`, `spec/00-overview.md`, `spec/05-terminology.md`, `term/_dict.py` | counts updated to 81 terms / 86 collisions / 1008 citations / 369 links, 74 findings in 76 rows and 28 open decisions. The README's `term/` paragraph keeps its exact line budget (745 lines) so the `# Project Status` blocks at L12 and L735 do not move — AMB-24, C-09 and two `X-` doc-sites cite those line numbers, and this pass added the `_structs.py` mention without spending a line on it | a documentation pass that invalidates its own citations is the failure mode the previous pass recorded at L158; the line budget is held deliberately |

| `spec/_build_index.py`, `spec/10-index.json` | the index now **derives** every register row it does not curate: C-46…C-76 are parsed from `spec/06`'s table (severity, status, `U-`/`X-` cross-references and source line ranges, dropping cites that name another document, since `provenance.file` says `Red-on-Rust.md`), and U-23…U-34 from `spec/09`'s `**Where:**` and `**Blocking:**` bullets — expanding `R-CAP-01…R-CAP-04` ranges, and taking the section from the requirements named when the bullet names none. A completeness gate fails the build if a `C-` row or `U-` heading is missing from the index, or if an indexed finding has no row. `findings` 44 → 75, `unresolved` 16 → 28, and the four self-describing `meta` strings are computed instead of written. The curated C-01…C-45 / U-01…U-22 tuples are untouched: they carry hand-graded values (`MAJOR (historical)` folded to MAJOR, C-09's `info-superseded`, C-35's `U-22 (gap)`) that a mechanical read cannot reproduce | `spec/00-overview.md` L80 calls this file "the authoritative cross-index of sections, requirements, findings, unresolved items, and status", yet it stopped at C-45 and U-22 — 31 findings and 12 decisions were invisible to any machine reader. Earlier passes opened that gap and this one widened it; deriving closes it permanently, and the gate is verified by a negative control (deleting C-08's row makes the build exit 1 and name it) |
| `spec/06` C-56, C-58, C-60, C-70; `req/02` CN-05; `req/_validate.py` | five table rows carried **unescaped `\|` characters inside cells**: a closure body `unwrap_or_else(\|\| Err(…))`, the v1 fault grammar `F ::= CapViolation \| BudgetExhausted \| … \| IsolationBreach`, a quoted property-test matrix row, the WAL checksum comment `SHA-256(sequence \|\| kind \|\| payload_length \|\| payload)`, and a set builder `{ (o, derive_op(A_o,C_o)) \| o ∈ O_A ∩ O_C }`. Each split its row into as many as thirteen columns and corrupted the rendered register; all now use `\|`, the convention C-47 already followed. `req/_validate.py` gains check **7d**: every markdown table row in `spec/`, `req/`, `term/` and `README.md` must carry its header's cell count, counting only unescaped separators | C-70 is a row **this pass added**, so the defect was being reproduced rather than merely inherited. The repo's tables are its primary artefact — a register that renders wrong is a register nobody reads |

Three of these deserve emphasis. `req/_validate.py` is a **checker**, and changing a checker's expectation is the kind of edit that can hide drift; it is done here in the open, with the reason in a comment beside the number — and the same checker then caught this pass writing three identifiers into REQ-CALC-013 that its own citation did not cover, which was fixed by widening the citation rather than by deleting the words. Second, `spec/01` L138 is **normative text**: it was annotated, not amended, because the repository's rule is that the frozen spec text governs and that a defect in the canonicalization layer is recorded beside it. Third, and least comfortably: **this pass wrote false claims of its own — twice.** An earlier revision of the C-08 annotation asserted that `CapabilityError` “exists only as a `Result` error type (L9736/L9743/L9749/L19212), never as a `Fault` variant”. That is wrong — `Capability(CapabilityError)` is a `Fault` variant at L22430 and L23808, and `Fault::CapabilityError(error)` is constructed at L20389 and L20790. The claim is withdrawn in the C-08 row, in X-59's disposition and here, with the withdrawn wording quoted rather than silently overwritten, because a normalization pass that quietly repairs its own errors is doing exactly what R-SCOPE-03 forbids. It was found by re-reading the cited lines instead of trusting the register — the same method that found X-59 in the first place. The second is worse because it was acted on. The fault audit filed X-64 as a `PHANTOM-IDENTIFIER` on the assertion that “`Fault::StalePlan` occurs nowhere in L1–42312”, and four documents were amended on that premise: `spec/01` L138 gained an annotation calling the parenthetical a canonicalization-layer addition, REQ-CALC-014's STATEMENT was rewritten and its POSTCONDITIONS withdrawn, AMB-08's list was struck, and `spec/06` C-54 and `req/03` AMB-34 were both filed as phantom findings. The assertion is false — `Fault::StalePlan` occurs verbatim at L28373 (turn [36]) — and REQ-CALC-014's own SOURCE line had cited L28373 all along, so the withdrawal contradicted the record's own provenance. All four documents are reverted with the withdrawn wording quoted in place, X-64 is refiled as `UNDECLARED-VARIANT` (the variant is used by the source and declared by none of the seven `Fault` enums — one of twelve such paths, X-69), and C-54 and AMB-34 are rewritten. A canonicalization layer that retracts correct normative text on a misread search is a worse defect than the one it set out to fix, which is why the retraction is recorded here and in each affected document rather than quietly undone. It was found by the declaration sweep re-reading the cited lines — the same method, applied to this pass's own output.

## 7. Guarantees the checker enforces

`python3 term/_check.py` fails (exit 1) unless all of the following hold. It is the repository's standing rule that a generated file must have a checker that re-derives its facts from `Red-on-Rust.md`.

1. every TERM, LAW and COLLISION uses a controlled `TYPE` / `DOMAIN` / `OWNER` / kind / severity / mandate value;
2. `T-`, `N-` and `X-` numbering is unique and gap-free;
3. all 26 required terms are present, anchored, defined, unique by canonical name, and each declares at least one forbidden variant;
4. **every collision site token really occurs at the cited line** of `Red-on-Rust.md` (a citation to a deliberately blank line must be blank);
5. **every doc-site token really occurs at the cited line** of the cited `spec/` / `mod/` / `req/` / `README.md` file;
6. every term anchor's signature occurs at its cited line **and** the cited turn really contains that line;
7. every law evidence line is in range and carries content;
8. all line numbers lie within `1..SOURCE_MAX_LINE`;
9. `Term.collisions` and `Collision.affects` agree in both directions, with no dangling reference;
10. every `C-`/`U-`/`AMB-`/`MOD-`/`S-`/`R-`/`M` reference resolves in the register that owns it;
11. no `PROTECTED` name is unattested in both layers unless its gloss marks it as a guard;
12. every `OWNER` resolves in `mod/00-overview.md`;
13. the generated markdown and JSON match the data (no drift).

Current run: **1008 citations re-grepped, 369 links verified in both directions, 0 errors, 41 warnings** — 13 intentional domain/owner divergences (e.g. `CanonicalEnvelope` sits in `PERSISTENCE` but is owned by MOD-10; `Fault` sits in `MACHINE` but is owned by MOD-01, which is where R-CALC-06 lives), 18 forbidden variants that are attested nowhere and are kept as guards against future invention, and 6 canonical names that are descriptive labels rather than identifiers (T-54, T-57, T-58, T-59, T-62, T-68) and so cannot be attested verbatim. Warnings are reviewed, not suppressed; the count is part of the checker's output so that a change in it is visible.

## 8. Running it

```
python3 term/_dict.py --write   # regenerate 01/02/03/10 from _terms.py
python3 term/_check.py          # validate everything, including generated-file drift
python3 term/_structs.py        # every struct field set: 22 names with >1 shape
python3 term/_structs.py --enums      # every enum variant set: 11 names with >1
python3 term/_structs.py --undeclared # field types declared nowhere: 69 names
python3 term/_structs.py --struct Authority   # one name, all declarations
```

`_structs.py` is a report, not a gate: it re-derives the declaration facts the register cites
(272 struct declarations, 108 enum declarations, 69 undeclared field types) so that a count in
`_terms.py` can be checked instead of trusted. It deliberately does NOT fail the build, because
the frozen source is allowed to disagree with itself — that disagreement is the finding.

The four pre-existing checkers must keep passing alongside it:

```
python3 mod/_build.py && python3 dep/_graph.py && python3 req/_validate.py && python3 spec/_build_index.py
```
