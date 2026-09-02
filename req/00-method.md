# Requirements Extraction — Method, Field Semantics, and Provenance Verification

**Role:** Requirements Extraction Agent for Red-on-Rust.
**Input:** the frozen Red-on-Rust technical specification — `Red-on-Rust.md` (42,312 lines, turns `[1]`–`[60]`), `README.md` (turn `[60]` orientation), and the canonicalized document set `spec/00`…`spec/10`.
**Output of this extraction:** `req/01-registry-*.md` (atomic requirement registry), `req/02-compound-not-split.md`, `req/03-ambiguous.md`, `req/04-verification-undefined.md`, `req/registry.json` (machine-readable), `req/_validate.py` (checker).

This extraction is **additive**. It does not modify `spec/`. Where this extraction and `spec/01` disagree about *where* a requirement lives in the source, the disagreement is recorded in §5 below with the command evidence, and the corrected citation is the one used in the registry.

---

## 1. Extraction rules applied

| # | Rule | How it was applied |
|---|---|---|
| 1 | Do not rewrite meaning | Statements quote the source's own formulae, identifiers, and constants verbatim (`derive(A,C) ≼ A`, `s_{n+1} = s_n + 1`, `0x30`, `complete_max`, …). Where wording is compressed, no quantifier, negation, ordering, or constant is altered. |
| 2 | Do not invent requirements | Every record traces to a `spec/01` obligation ID and to at least one `Red-on-Rust.md` line range. No requirement was added to "complete" an area; gaps are recorded as AMBIGUOUS (output 3), never filled. |
| 3 | Preserve exact mathematical invariants | Invariants are copied, not paraphrased, into `INVARIANTS`. Superseded forms (e.g. pre-fix `BudgetOK`, `⟨F,M,C,I,W⟩`) are **not** carried as requirements. |
| 4 | Preserve MUST / MUST NOT / SHOULD / MAY | `NORMATIVE-LEVEL` uses exactly: `MUST`, `MUST NOT`, `SHOULD`, `MAY`, `IS` (frozen definition/data shape), `NON-NORMATIVE`, `AMBIGUOUS`. Source hedges ("should be operational") are recorded as `SHOULD`, not upgraded to `MUST`. |
| 5 | Separate compound requirements | Split whenever each part has its **own** falsification target — a distinct observable event, a distinct gate, a distinct mutation, a distinct golden vector, or a distinct rejection class. Enumerations of prohibitions (planner MUST NOTs, short-circuit assertions, WAL rejection classes, crash points T0–T6, prohibited shortcuts) are split item by item. |
| 6 | Keep inseparable invariants together | A single formula whose meaning is destroyed by splitting stays one record: boxed theorems, biconditional definitions (`Authorized(…) ⇔ 5 conjuncts`), **closed sets** (the 15A tag table, the frozen `Expr`/`Frame`/`Fault` enumerations, the 10 forbidden reference-model dependencies, the M001–M018 baseline registry), and **ordered** sequences (16-step request sequence, issuance transaction, recovery algorithm, shrinking order, 20-step build order). Each is listed with its reason in output 2. |
| 7 | Preserve source provenance | Every record's `SOURCE` gives `Red-on-Rust.md` line range(s) + turn/section, then the `spec/01` section and obligation ID. Provenance was re-verified against the source in this pass; corrections in §5. |
| 8 | Mark explanatory text NON-NORMATIVE | Examples, golden-vector commentary, illustrative operation tables, and design rationale are recorded with `NORMATIVE-LEVEL: NON-NORMATIVE` and are excluded from the obligation count. |
| 9 | Mark unresolved statements AMBIGUOUS | Anything the source leaves under-determined, self-contradictory, or dependent on a decision that was never issued is `AMBIGUOUS`, cross-linked to the `U-…` item. Ambiguities are **not** resolved here. |
| 10 | Never infer implementation evidence from specification text | Rust code blocks inside `Red-on-Rust.md` are *specification text*. They are not repository code. `EVIDENCE-STATUS` is never raised on the strength of a code sketch. |

## 2. Field semantics

- **REQ-ID** — `REQ-<AREA>-<NNN>`, stable, dense per area. `AREA` mirrors the canonical obligation area so `REQ-EFFECT-014` and `R-EFFECT-04` are relatable.
- **CATEGORY** — one of: `scope`, `process`, `security-invariant`, `trust-model`, `architecture`, `planner-boundary`, `compilation`, `calculus`, `machine-semantics`, `capability-authority`, `capability-kernel`, `budget`, `effect-protocol`, `durability`, `host-boundary`, `concurrency`, `marshalling`, `serialization`, `persistence`, `recovery`, `verification`, `test-infrastructure`, `repository-structure`, `engineering-claims`.
- **SOURCE** — `Red-on-Rust.md L<a>–L<b> (<turn>/<section>)` then `spec/01 S-NN R-AREA-NN`. Multiple ranges when the source states the requirement more than once; the latest frozen text is listed first.
- **NORMATIVE-LEVEL** — see rule 4. `MUST` includes invariants the source states as always-true (`always holds`, `is immutable`, boxed theorems).
- **STATEMENT** — the requirement, as close to source wording as possible.
- **PRECONDITIONS** — what must hold for the requirement to be applicable (state, actor, phase, input class). `—` when the requirement is unconditional/universal.
- **POSTCONDITIONS** — the observable state change or refusal that must hold after the relevant operation.
- **INVARIANTS** — the mathematical property that must hold at every relevant point, copied verbatim where the source gives a formula.
- **DEPENDENCIES** — other `REQ-…` IDs that must hold for this one to be meaningful, plus `U-…` items that block it.
- **SECURITY-IMPACT** — `critical` (defeats the external-effect chain or authority attenuation), `high` (defeats determinism, durability, or isolation), `medium` (defeats a bounded resource or a verification gate), `low` (structural/engineering), or `none (descriptive)`.
- **VERIFICATION-METHOD** — the conformance obligation the frozen source attaches: verification-obligation tag, mutation ID, crash point, golden vector, differential comparison, visibility/dependency review, or `UNDEFINED` (see output 4).
- **EVIDENCE-STATUS** — `SPECIFIED` | `IMPLEMENTED` | `TESTED` | `VERIFIED` | `PROVEN` | `UNKNOWN`.

## 3. Evidence discipline (binding)

Repository state was re-checked in this pass:

```
Red-on-Rust/
├── README.md          ← orientation document
├── Red-on-Rust.md     ← frozen source (60-turn transcript)
├── spec/              ← canonicalization document set
└── req/               ← this extraction (documents only)
```

No Cargo workspace, no crate, no Rust source file, no test file, no vector file, no CI configuration, no proof artifact exists. Therefore:

- **Every record in this registry is `EVIDENCE-STATUS: SPECIFIED`.** No record is `IMPLEMENTED`, `TESTED`, `VERIFIED`, or `PROVEN`.
- No theorem in the source has a mechanized proof; all theorem-bearing records stay `SPECIFIED` and say so.
- `UNKNOWN` is reserved for statements whose normative status itself cannot be determined from the frozen text (used only where the source neither freezes nor retracts a statement). It is **not** used as a weaker form of `SPECIFIED`.
- Promotion is evidence-gated and requires a repository artifact cited in the record: `SPECIFIED → IMPLEMENTED → TESTED → VERIFIED → PROVEN`.

## 4. Decomposition policy (split vs. keep)

A compound obligation was **split** when the source itself gives each part a separate falsification target. Examples actually applied:

- `R-EFFECT-04` (denial short-circuit) → 5 records, because the source's Track C obligation is *five assertions per gate* (subsequent gates untouched / ID not incremented / budget unchanged / log unchanged / host never called).
- `R-RECOV-02` (crash matrix) → 7 records (T0…T6), each with its own crash-injection point and expected classification.
- `R-PLANNER-02` → 8 records, one per prohibited planner action.
- `R-PERSIST-02` → 1 framing record + 9 records, one per mandated rejection class.
- `R-CLAIM-02` → 16 records, one per prohibited shortcut.
- `R-BUDGET-05` → 4 conservation laws + 3 partition-transfer records.

A compound obligation was **kept** when it is a single formula, a closed set, or an ordered sequence (rule 6). All such records are enumerated with their reason in `req/02-compound-not-split.md`.

## 5. Provenance verification and corrections

Method: every `Red-on-Rust.md` line range cited by `spec/01-canonical-specification.md` was re-located in the source by searching for the signature text of the requirement. The master prompt (turn `[54]`, L37638–38968) was re-mapped section by section:

| § | Title | Actual lines |
|---|---|---|
| 1.1 | Frozen means frozen | 37664–37691 |
| 1.2 | Production/reference independence | 37696–37720 |
| 1.3 | No hidden authority | 37722–37744 |
| 2 | Required trust boundary | 37746–37798 |
| 3 | Implementation order | 37800–37834 |
| 4 | CEK machine requirements | 37836–37887 |
| 5 | Lambda / call requirements | 37889–37927 |
| 6 | Capability kernel requirements | 37929–37962 |
| 7 | Budget requirements | 37964–38020 |
| 8 | Effect request requirements | 38022–38072 |
| 9 | Actor requirements | 38074–38106 |
| 10 | Marshalling requirements | 38108–38136 |
| 11 | Canonical serialization requirements | 38138–38183 |
| 12 | Persistence requirements | 38185–38248 |
| 13 | Snapshot requirements | 38250–38276 |
| 14 | Replay requirements | 38278–38302 |
| 15 | Reference model requirements | 38304–38344 |
| 16 | Differential observation | 38346–38388 |
| 17 | Test generation | 38390–38437 |
| 18 | Shrinking | 38439–38465 |
| 19 | Mutation testing | 38467–38513 |
| 20 | Mutation validation | 38515–38542 |
| 21 | Coverage | 38544–38583 |
| 22 | Execution modes | 38585–38651 |
| 23 | Crash-injection matrix | 38653–38690 |
| 24 | Fault adjudication | 38692–38712 |
| 25 | Required counterexample artifact | 38714–38745 |
| 26 | CI gates | 38747–38806 |
| 27 | Engineering response format | 38808–38852 |
| 28 | Prohibited shortcuts | 38854–38875 |
| 29 | Final acceptance condition | 38877–38919 |
| 30 | Start condition | 38921–38968 |

Bootstrap pack (turn `[58]`): §32 Mutation registry 40657–40719 · §33 Counterexample storage 40720–40760 · §34 Bootstrap milestones 40761–41005 (M0 40763, M1 40785, M2 40804, M3 40825, M4 40844, M5 40864, M6 40886, M7 40906, M8 40926, M9 40946, M10 40958, M11 40981) · §35 First sprint 41006–41037 · §36 First security gate 41038–41083 · §37 First differential gate 41084–41123 · §38 Definition of done 41124–41160 · §39 Final repository invariant 41161–41239 · §40 Bootstrap completion 41240–41273.

### 5.1 Corrections (citations in `spec/01`/`spec/03` that point at the wrong source text)

Each row was established by reading the cited range and the correct range in `Red-on-Rust.md`.

| Obligation | Cited in `spec/01` | Cited range actually contains | Correct range (used in this registry) |
|---|---|---|---|
| R-EFFECT-03 (16-step sequence) | L37891–37908 | §5 Lambda/Call text | **L38022–38050** ("The Request sequence is immutable:" L38024; steps L38030–38045) |
| R-EFFECT-04 (short-circuit) | L37891–37908 | §5 Lambda/Call text | **L38022–38050** + Track C L24003–24045 |
| R-EFFECT-06 (receipt validation) | L37910–37922 | §5 Lambda/Call text | **L38052–38072** ("Receipt must validate both:") |
| R-DUR-01 (durable-before-host) | L37910 | §5 Lambda/Call text | **L38050** + invariant L38052–38058; also §12 L38217–38221 |
| R-CEK-01 (explicit machine) | L37800–37812 | §3 Implementation order | **L37836–37854** |
| R-CEK-02 (value-return) | L37826–37838 | §3 Implementation order | **L37857–37886** ("A value is terminal only when the continuation is empty" L37857) |
| R-CEK-05 (call) | L37840–37862 | §4 CEK machine | **L37889–37927** |
| R-KERN-02 (kernel API) | L37870–37886 | §4 CEK machine | **L37929–37962** |
| R-BUDGET-02 (checked arithmetic) | L38044–38046 | §8 16-step list | **L38002–38004** ("Never use saturating subtraction." / "Use checked arithmetic.") |
| R-ACTOR-04 (FIFO scheduler) | L37924–37937 | §5/§6 boundary | **L38074–38106** |
| R-ACTOR-05 / R-ACTOR-06 | L37941–37951 | §6 Capability kernel | **L38074–38106** |
| R-MARSHAL-01 / R-MARSHAL-02 | L37946–37959 | §6 Capability kernel | **L38108–38136** |
| R-DUR-03 (causal protocol) | L37953–37965 | §6 Capability kernel | **L38203–38215** |
| R-DUR-04 (crash classification) | L37968–37981 | §7 Budget | **L38222–38248** |
| R-HOST-03 (ordered ReplayHost) | L37985–38000 | §7 Budget | **L38278–38302** ("next trace entry" L38296; "Do not use an unordered map…" L38298) |
| R-REF-05 (normalized observation) | L38420–38470 (labelled §16) | §17 Test generation | **L38346–38388** (§16) |
| R-TEST-02 (artifact) | L38891–38920 | §29 Final acceptance | **L38714–38745** (§25; "runnable locally" L38745) |
| R-TEST-07 (coverage tags) | L38523–38560 | §20 Mutation validation | **L38544–38583** (§21) |
| R-TEST-08 / R-RECOV-02 (crash matrix) | L38831–38846 | §27 Conflict format | **L38653–38690** (§23) |
| R-TEST-09 (adjudication) | L38848–38862 | §27 Conflict format | **L38692–38712** (§24) |
| R-TEST-10 (CI gates) | L38864–38890 | §28 Prohibited shortcuts | **L38747–38806** (§26) |
| R-TEST-11 (final acceptance) | L38885–38911 | §29 (starts L38877) | **L38877–38919** |
| R-ORDER-01 (20-step order) | L37793–37812 | §2 tail | **L37800–37834** (§3); bootstrap restatement L41016 area |
| R-ORDER-03 (first security gate) | L41155–41195 | §38/§39 region | **L41038–41083** (§36) + **L41084–41123** (§37) |
| R-ORDER-04 (first sprint) | L41091–41112 | §37/§38 region | **L41006–41037** (§35; ROR-001…ROR-016 at L41014–41029) |
| R-SCOPE-03 (STOP rule) | L37664–37686 | §1.1 list only | **L37664–37691** (the STOP sentence is L37690) |

### 5.2 Content corrections (claims in `spec/` that the source contradicts)

| Claim in `spec/` | Source evidence | Effect on this extraction |
|---|---|---|
| `spec/01` L334 (R-MARSHAL-02): `Expr::Delegate` appears "in the Phase 13 text (L25700, L25931; master prompt L37959)" and "no frozen document defines its fields" | L25700 does state it; **L25931 is `fn execute_spawn(`**; **L37959 is a blank line inside §6**; and the fields *are* defined at L25989–25992 (`Expr::Delegate { capability: Box<Expr>, constraint: Constraint }`) | Two of the three cites are wrong and the "no frozen document defines its fields" claim is false. The **fields are source text**; what is missing is that `Delegate` is absent from the frozen turn-`[21]` 12-constructor `Expr`. Recorded as AMBIGUOUS (two inconsistent frozen AST surfaces). See `req/03-ambiguous.md` AMB-11. |
| `C-30`/`U-09`: `AdmissibleConstraint` "defined once (L10171); never referenced again" | `AdmissibleConstraint` also occurs at L7858, L8717, L8721, L8837, L10068 — including as the **premise of the E-Attenuate transition rule** (L8717) and its fault rule (L8721) | The attenuation transition's well-formedness premise is extracted as a requirement (REQ-CAP-024) with its provenance; the "orphaned trait" finding is recorded as an open ambiguity (AMB-12), not resolved. |
| `spec/01` R-ORDER-03 lists only `Block ⇏ ExecutablePlan` for the first security gate | §36 (L41038–41083) boxes **four** properties: `Block ⇏ ExecutablePlan`, `CapRef ⇏ AuthorityInspection`, `Value::Capability ⇏ OrdinaryMessageTransfer`, `HostInvocation ⇒ DurableIssued` | All four are extracted as atomic gate obligations (REQ-ORDER-017…020), cross-referenced to the requirements that enforce them. |
| `U-15`: the `ReconciliationOutcome` variant list "is not specified" | `Red-on-Rust.md` L26593–26597 declares `pub enum ReconciliationOutcome { Completed(EffectReceipt), NotExecuted, Indeterminate }` — a closed three-variant set matching §12's three classifications (L38211, L38232, L38243); the token `Replayed` occurs nowhere in L1–42312 | Treated as **not ambiguous**: REQ-DUR-010/REQ-DUR-012/REQ-RECOV-019 cite the declaration. `req/03-ambiguous.md` AMB-15 is withdrawn and says so. |
| `spec/09` describes `EventSequence` as a generic monotonic sequence type | L31697 and L32060 both declare `pub struct EventSequence(pub u64);` | Registry cites the newtype declaration; AMB-14 concerns its relation to `WalFrame.sequence`, not its shape. |
| *new finding (not in `spec/06`)*: the recovery procedure is stated twice with different granularity | §15B.7 L35193–35204 gives **12** ordered steps; §15B.11 L34344–34364 gives **19** ordered steps for the same algorithm | Both are extracted (REQ-RECOV-010 for the operative 12-step list, REQ-RECOV-021 for the 19-step list); the discrepancy is recorded as AMB-27 and **not** resolved. |
| *understated in this extraction until re-checked*: the `Value` domain collision | machine domain L12283–12301 has 11 variants including `Bytes`, `Tuple`, `Function`, `Actor`; the canonical codec L33155–33265 encodes 8 including `Map`, which is not a machine variant | AMB-21 rewritten to state the incompatible variant sets (per `spec/06` C-03/C-45) rather than a mere name collision. |

| `spec/01` R-TEST-02 lists the artifact fields as `snake_case` | §25 (L38720–38741) lists them space-separated ("generator version", "test-case version", …) | Statement preserved in source wording; field naming is not a frozen identifier set (recorded, not resolved). |

### 5.3 Provenance carried forward unchanged

Citations whose range was checked and found to contain the requirement's signature text are used as-is, e.g. `PlanProposal` L27175; frozen `Expr` L12145–12200; machine `Value` L12283–12312; `Fault` L23806; `Frame` L16943/L23830; `derive` L6397–6404; `Authorized` L6406–6421; `Valid(c,t)` L6434–6445; budget `ReserveOK` L7525/L8686; `execute_spawn` L25624/L25931; `Deadlock` L25579; `ActorSelected` L25567/L25582; "without consuming fuel" L25738; `MarshalFault` L25685–25694; `WalFrame` L35099; `WalRecord` L35127; crash matrix L35159–35176; `GlobalSnapshot` L35181; `CanonicalError` L32959/L34994; duplicate-key patch L34987–35024; `AuthorityNode` L39373; `ReconciliationOutcome` declared L26593–26597 (used in `WalRecord::EffectReconciled` L35132); `PanicHost` L27901; `StalePlan` L27236/L28373; `PlannerAccepted` L27411; M001–M018 L40657–40719; `MutationKillRate` L38506/L38895; definition of done L41124.

`req/_validate.py` re-checks every `SOURCE` line range for bounds and re-runs the signature check for the anchors listed in `req/_anchors.py`, so the provenance claim is re-runnable rather than asserted.

## 6. Validation of this registry

`req/_validate.py` (with `req/_anchors.py`) re-derives everything from the source rather than trusting this document:

| # | Check | Demonstrated to fire |
|---|---|---|
| 1 | All 12 fields present, in the required order | yes — dropping `CATEGORY` from one record reported the field-list mismatch |
| 2 | Unique IDs; header and `REQ-ID` field agree; area numbering gap-free | yes — renaming a header reported the disagreement, the gap, and the resulting dangling dependency |
| 3 | `NORMATIVE-LEVEL` in the frozen vocabulary; `EVIDENCE-STATUS` in the allowed set and never above `SPECIFIED` | yes — `MIGHT` and `TESTED` were both rejected |
| 4 | Every cited line inside 1..42312; every cited range carries a `[turn]` marker | yes — an out-of-bounds range and a stripped marker were both reported |
| 5 | Cited lines really are inside the turn the `SOURCE` claims | yes — relabelling turn `[58]` as `[57]` was reported |
| 6 | Every parent obligation cited exists in `spec/01`, and all 148 are cited | yes — an invented `R-REPO-99` and the removal of the only `R-REPO-03` citation were both reported |
| 7 | `DEPENDENCIES` and `CN-`/`AMB-`/`VU-` references resolve | yes — `REQ-REPO-999` and `AMB-27` (before it existed) were both reported |
| 8 | Every backticked identifier in `STATEMENT`/`INVARIANTS` occurs inside a cited range | yes — `FrobnicatorId` was reported with its (absent) first occurrence |
| 9 | Frozen anchors in `_anchors.py` re-grepped against the source | yes — three stale anchors were reported and corrected |
| 10 | Part-file header counts match the parsed records | yes — an inflated header count was reported |
| 11 | Every `C-nn` / `U-nn` cross-reference exists in `spec/06` / `spec/09` (45 and 16 items respectively) | yes — a stale unresolved-decision reference was reported; this check is what exposed that four of the unresolved-decision ids cited earlier in this extraction do not exist in `spec/09` (which has exactly 16 items) and that several contradiction links pointed at the wrong finding |

`req/_coverage.py` runs the complementary omission audit: it inverts the citation map and reports normative-marker lines (`MUST`, `never`, `always`, `required`, boxed formulae, …) in the requirement-dense regions that **no** record cites. Its scope is deliberately limited to the three regions where requirements are stated as requirements — the turn-`[54]` master prompt (L37638–38968), the turn-`[58]` bootstrap pack (L40600–41273), and the closing turns `[59]`–`[60]` (L41274–42312); the earlier design turns are cited from the location where each requirement was frozen, not from every place it was discussed. First run found 15 uncited lines; all 15 proved to be second statements of requirements already extracted, so each was added as an additional citation rather than a new record. Current result: **74/74 normative-marker lines cited, 0 uncited**.

This pass found and fixed, by that mechanism: three identifiers I had invented (`B_max`, `f_specific` as a literal token, `BudgetAllocationSpec::validate_and_escrow`), 83 `[turn]` labels that disagreed with the lines they annotated, 56 `SOURCE` fields with no turn marker at all, three stale anchors, and six statements whose wording did not match the source (`Value` tag constants, canonical map key type, hostile-allocation wording, `Expr::Delegate` line range, `EventSequence` shape, `ReconciliationOutcome` variants).
