# SEC-001 / SEC-002 frozen-addendum draft — receipt-result admission + holder-possession binding

**Status: DRAFT FOR SPECIFICATION-OWNER ADOPTION — not applied.** No frozen or
canonical text is changed by this file. The exact edit set lives in
`audit/spec_addendum.py` (this draft is generated from its constants, so the two
cannot drift); `python3 audit/spec_addendum.py` proves it on temporary copies,
`--apply` executes it in place. Rollback after apply: `git revert` of the
adoption commit (the addendum is additive and quoted-not-deleted throughout).

## 1. What this freezes (audit report §6 item 2)

The two remaining CRITICAL findings are *specification-level* absences: the
central thesis `LLMOutput ∧ UntrustedInput ↛ ExternalEffect` is falsifiable by
a conforming implementation because (SEC-001) the host receipt-result channel
injects unrestricted values — including `Value::Capability` — into actor
continuations, and (SEC-002) the authoritative authorization gate resolves
CapRefs in a global arena with no holder-possession check, so known/guessed
CapRef bits suffice to exercise foreign authority. Four additive obligations,
one registered-and-resolved conflict, three registered mutations, and one
conformance tag freeze the fixes:

| Addendum | Freezes | Replaces/extends |
|---|---|---|
| `R-EFFECT-08` | SEC-001: receipt-result admission rule (data-domain only, no capability/closure at any depth, declared fault mapping for host errors) | extends R-EFFECT-06/07 (ID+digest validated; payload now constrained) |
| `R-KERN-04` | SEC-002: possession as a conjunct of the gated authorization predicate; holder-parameterized kernel `authorize` | supersedes the global-arena no-holder form; extends R-CAP-06/R-KERN-02; resolves C-77 |
| `R-KERN-05` | SEC-002: `CapabilityContext` a real frozen possession type, carried by snapshots, reconstructed before gate authorization | supersedes the `pub type CapabilityContext = ();` sketch |
| `R-COMPILE-06` | SEC-002: capability literals in a `Block` must be plan-bound; foreign/garbage/undeclared literals are compilation faults | extends R-COMPILE-02/03; closes U-22 in the security direction |
| `C-77` (spec/06) | registers the previously unregistered v0.3 `Authorized(κ(c),E,t)` vs global-arena conflict | new resolution status `resolved-by-addendum` |
| `M019/M020/M021` (spec/08) | mutations that must be killed (capability-result resume, closure-result resume, authorize-without-possession) | registry M001–M018 → M001–M021 |
| `EFFECT-RECEIPT-RESULT-NO-AUTHORITY` (spec/08) | conformance tag for R-EFFECT-08 | tag set 17 → 18 |

## 2. Exact normative texts (spec/01 insertions)

**R-COMPILE-06 (capability literals must be plan-bound — frozen addendum).** A `Block` MUST NOT carry a `Value::Capability` literal that is not plan-bound: compilation MUST fault on any embedded capability literal — foreign, garbage-generation, or own-but-undeclared — unless the compiler itself substituted it from the plan's declared capability set. Undecided capability-analysis depth (U-22) MUST NOT leave embedded authority literals unconstrained; this closes the U-22 gap in the security direction. *(Frozen addendum — post-audit remediation SEC-002 item 3; additive per R-SCOPE-03; extends R-COMPILE-02/R-COMPILE-03; no source transcription.)*

**R-KERN-04 (holder-possession binding at the gate — frozen addendum).** Authority exercise at the machine's authorization gate MUST be possession-gated: `Authorized_gated(actor, c, E, t) ⇔ c ∈ CapabilityContext(actor) ∧ Valid(c, t) ∧ Authorized(κ(c), E, t)` — possession is a conjunct of the gated authorization predicate, not a marshalling courtesy. The kernel `authorize` API MUST be holder-parameterized (`authorize(holder, cap, effect, t)`) and MUST resolve the `CapRef` through the requesting actor's capability context; the global-arena no-holder form (`authorize(cap, effect, t)`) is SUPERSEDED (quoted, not deleted). `CapRef` bits MUST NOT suffice to exercise authority — `CapRef ≠ authority ownership` is a kernel-side possession rule. This binds the per-actor reading of the v0.3 formal rules (`Authorized(κ(c), E, t)`) over the kernel-substrate global arena (conflict C-77, resolved by this addendum). *(Frozen addendum — post-audit remediation SEC-002 items 1 and 4; additive per R-SCOPE-03; extends R-CAP-06/R-KERN-02; no source transcription.)*

**R-KERN-05 (CapabilityContext is a real possession type — frozen addendum).** `CapabilityContext` MUST be a real frozen type: the per-actor possession structure mapping the actor's capability slots to live `CapRef`s. The unit-type sketch (`pub type CapabilityContext = ();`) is SUPERSEDED (quoted, not deleted). Snapshots MUST carry the capability context, and recovery MUST reconstruct each actor's possession set before any gate authorization — a possession gate that does not survive recovery enforces nothing. *(Frozen addendum — post-audit remediation SEC-002 item 2; additive per R-SCOPE-03; extends R-KERN-02/R-KERN-04; no source transcription.)*

**R-EFFECT-08 (receipt-result admission — frozen addendum).** A receipt may complete an effect; it MUST NOT confer authority. Before any continuation is resumed, the machine MUST run the recursive `contains_capability` predicate over the receipt's result payload at every nesting depth (`List`/`Map`/`Tuple` included) and MUST fault (`Fault::InvalidReceipt` family) on any `Value::Capability` and on any host `Function`/closure value. An admitted result MUST lie in the canonical data-domain (the 8-variant codec value set); host error results MUST enter machine values only through a declared, closed fault mapping — raw debug-formatted host text MUST NOT. This extends R-EFFECT-06 (causal validation of `id` and digest) from the receipt's identity to its payload: every value-crossing — messages, receipts, snapshots, replay traces — is subject to the no-raw-capability-transfer rule (R-CORE-07). *(Frozen addendum — post-audit remediation SEC-001 items 1–4; additive per R-SCOPE-03; extends R-EFFECT-06/R-EFFECT-07; no source transcription.)*

(Each ends with an explicit *frozen addendum* marker and no source-line
citation: addenda are new normative content, not transcriptions, so the
cross-layer checker's D2 source-agreement check correctly does not apply; D1
does not apply because each addendum is its own original — see the records
scope note below.)

## 3. Companion edits

- **spec/03-obligation-matrix.md** — four rows (provenance `addendum (SEC-00x)`,
  status SPECIFIED) and `Total: 152 obligations (148 transcribed + 4 addenda)`.
- **spec/06-contradictions-ambiguities.md** — resolution status
  `resolved-by-addendum` added to the header list; row **C-77** registering the
  v0.3-vs-global-arena authorization conflict (BLOCKING, resolved by R-KERN-04).
- **spec/08-verification-mapping.md** — tag row
  `EFFECT-RECEIPT-RESULT-NO-AUTHORITY` (marked post-audit, outside the frozen
  source set); mutations M019/M020/M021; registry title M001–M018 → M001–M021.
- **spec/normative-normalization-records.md** — scope note: the four addenda
  postdate the normalization pass and have no record (each is its own original,
  `Original = Normalized` by construction). The pass's "148 requirements" header
  remains true for the pass.
- **spec/_build_index.py** — the index builder's inline dataset carries the
  addendum (4 requirement rows with `addendum` provenance serialized as
  `{file: 01-canonical-specification.md, line_ranges: [], note: post-audit frozen addendum}`;
  section lists S-06/S-10/S-12; milestone maps M4/M5; crate maps; mutation/tag
  lists; `_status` learns `resolved-by-addendum`; id-scheme counts). Without
  this, regenerating `spec/10-index.json` would silently drop the addendum —
  the exact cross-layer drift class (SEC-023) this repository now gates against.
- **README.md** — "148 stable requirement IDs" → "152 (148 + 4 post-audit
  frozen addenda)".

## 4. Verification record (this draft's proof, before any apply)

- Precheck on the real tree: addendum ABSENT (all markers missing), 34 anchors
  intact — the absence *is* the finding (SEC-001/SEC-002 unfrozen).
- Dry run (temporary copies): 152 obligations / 152 matrix rows / 148 records;
  `audit/spec_check.py` parses 148/152/152 (non-vacuous), D1=0, no FAIL, and
  **zero warnings on the four new obligations**; the 36 warnings are the
  pre-existing adjudicated terse-body/label set, unchanged.
- New-row body↔matrix agreement (D3 overlap): R-COMPILE-06 0.78, R-EFFECT-08
  0.87, R-KERN-04 0.88, R-KERN-05 0.92 (threshold 0.25).
- Sandboxed `spec/_build_index.py` rebuild: `requirements=152 findings=76
  mutations=21 tags=18 sections=24`; JSON carries all new IDs, C-77 with
  status `resolved-by-addendum`, M021, and the addendum tag.

## 5. Adoption procedure

1. `python3 audit/spec_addendum.py` — re-run the dry-run proof on the current tree.
2. `python3 audit/spec_addendum.py --apply` — applies 34 edits across 7 files, re-runs every check on the real tree, and regenerates `spec/10-index.json` (verified in-step).
3. `python3 spec/_check.py` — the promoted gate must still exit 0 (D1=0).
4. Single adoption commit (git-reversible); re-run `req/_validate.py` as an
   unrelated-tree sanity check.

Generated from `audit/spec_addendum.py` constants — 2026-09-02.
