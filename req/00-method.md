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
- **NORMATIVE-LEVEL** — see rule 4. `MUST` includes invariants the source states as always-true (`always holds`, `is immutable`, boxed theorems), and obligations the frozen text states declaratively or as a necessary condition — `The reference machine implements the frozen Phase 10 rules`, `The harness establishes a deterministic correspondence`, `Three modes are required`, `Phase 15C is complete only when`, `A test case passes only when all required observational properties match` — which is the same convention parts 1–7 already apply (e.g. REQ-REF-006, REQ-REF-008, REQ-REF-009, REQ-REF-014). `IS` is reserved for definitional content that obligates nothing (a struct's fields, a phase-boundary description); `NON-NORMATIVE` for text the source itself marks explanatory.
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

### 5.4 Phase 15C line map (turn `[48]`, L35272–37168)

Phase 15C — the frozen specification of the independent reference model and the differential harness — is a single turn of 45 numbered sections. The turn-`[54]` master prompt restates these obligations compactly in §15–§22, which is where parts 6 and 7 cited them; only three of the 45 sections had any cited line before this pass, which extracted the primary text as `req/01-registry-part8-reference-15C.md` (44 records: REQ-REF-018…036, REQ-TEST-032…056).

| 15C | Lines | Records citing it | Cited lines |
|---|---|---|---|
| 15C.2 Non-Goals | 35326–35346 | REQ-SCOPE-011, REQ-REF-004, REQ-REF-005, REQ-REF-007, REQ-REF-008, REQ-REF-009, REQ-REF-018 | 21 |
| 15C.3 Independence Boundary | 35347–35439 | REQ-SCOPE-011, REQ-REF-004, REQ-REF-005 | 29 |
| 15C.4 Reference Value Model | 35440–35483 | REQ-REF-019 | 44 |
| 15C.5 Reference Environment | 35484–35513 | REQ-REF-020 | 30 |
| 15C.6 Reference CEK Machine | 35514–35619 | REQ-REF-021 | 106 |
| 15C.7 Reference CEK Transition Rules | 35620–35690 | REQ-REF-022 | 71 |
| 15C.8 Reference Capability Algebra | 35691–35764 | REQ-REF-023 | 74 |
| 15C.9 Reference Capability State | 35765–35800 | REQ-REF-024 | 36 |
| 15C.10 Reference Budget Model | 35801–35847 | REQ-REF-025 | 47 |
| 15C.11 Reference Effect Protocol | 35848–35892 | REQ-REF-026 | 45 |
| 15C.12 Reference Actor Model | 35893–35926 | REQ-REF-027 | 34 |
| 15C.13 Reference Scheduler | 35927–35972 | REQ-REF-028 | 46 |
| 15C.14 Reference Send / Receive | 35973–36004 | REQ-REF-029 | 32 |
| 15C.15 Reference Marshalling | 36005–36031 | REQ-REF-030 | 27 |
| 15C.16 Reference Global State | 36032–36056 | REQ-REF-031 | 25 |
| 15C.17 Reference Persistence Model | 36057–36107 | REQ-REF-032 | 51 |
| 15C.18 Reference Crash Semantics | 36108–36125 | REQ-REF-033 | 18 |
| 15C.19 Reference Host Model | 36126–36159 | REQ-REF-034 | 34 |
| 15C.20 Reference Observations | 36160–36188 | REQ-REF-035 | 29 |
| 15C.21 Canonical Actor Identity Mapping | 36189–36214 | REQ-REF-036 | 26 |
| 15C.22 Differential Harness | 36215–36249 | REQ-TEST-032 | 35 |
| 15C.23 Differential Comparison Levels | 36250–36310 | REQ-TEST-033 | 61 |
| 15C.24 Trace Normalization | 36311–36358 | REQ-TEST-034 | 48 |
| 15C.25 Negative Differential Testing | 36359–36399 | REQ-TEST-035 | 41 |
| 15C.26 Short-Circuit Differential Tests | 36400–36440 | REQ-TEST-036 | 41 |
| 15C.27 Reference Property Suite | 36441–36506 | REQ-ACTOR-011, REQ-TEST-037 | 66 |
| 15C.28 Generated Program Grammar | 36507–36565 | REQ-TEST-038 | 59 |
| 15C.29 Generator Strategy | 36566–36609 | REQ-TEST-039 | 44 |
| 15C.30 Shrinking | 36610–36634 | REQ-TEST-040 | 25 |
| 15C.31 Counterexample Format | 36635–36665 | REQ-TEST-041 | 31 |
| 15C.32 First-Divergence Algorithm | 36666–36689 | REQ-TEST-042 | 24 |
| 15C.33 Metamorphic Testing | 36690–36731 | REQ-TEST-043 | 42 |
| 15C.34 Differential Persistence Testing | 36732–36780 | REQ-TEST-044 | 49 |
| 15C.35 Reference Recovery Independence | 36781–36808 | REQ-TEST-045 | 28 |
| 15C.36 Canonical Serialization Differential Boundary | 36809–36834 | REQ-TEST-046 | 26 |
| 15C.37 Oracle Hierarchy | 36835–36860 | REQ-TEST-047 | 26 |
| 15C.38 Anti-Oracle-Collapse Rules | 36861–36891 | REQ-TEST-048 | 31 |
| 15C.39 Differential Test Execution Modes | 36892–36934 | REQ-TEST-049 | 43 |
| 15C.40 Determinism Requirement | 36935–36976 | REQ-TEST-050 | 42 |
| 15C.41 LLM Boundary Testing | 36977–36996 | REQ-TEST-051 | 20 |
| 15C.42 Acceptance Criteria | 36997–37021 | REQ-TEST-052 | 25 |
| 15C.43 Deliberate Fault-Injection Validation | 37022–37053 | REQ-TEST-053 | 32 |
| 15C.44 Evidence Classification | 37054–37089 | REQ-TEST-054 | 36 |
| 15C.45 Final Verification Theorem | 37090–37150 | REQ-TEST-055 | 61 |
| 15C.46 Phase Boundary | 37151–37168 | REQ-TEST-056 | 18 |

The turn is numbered 15C.2…15C.46 — there is no `# 15C.1` heading; L35272–35325 is an unnumbered preamble, of which L35281–35310 is cited by REQ-REF-001, REQ-REF-002 and REQ-REF-006. All 45 now carry at least one cited line. Measured against the 497-record registry, only three did: 15C.2 (21 of 21 lines, by REQ-SCOPE-011 and REQ-REF-004/005/007/008/009, whose range L35330–35375 straddles the 15C.2/15C.3 boundary), 15C.3 (29 of 93) and 15C.27 (1 of 66) — the other 42 had none. The "Cited lines" column counts distinct lines of the section inside some record's cited range, so overlapping citations are counted once per section.



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
| 10 | Part-file header counts match the records parsed **from that file** — per area, per declared total, and every area present in the file must be declared | yes — dropping `COMPILE` from the part-1 header reported `contains 14 COMPILE records but the header declares no COMPILE count`; declaring `REF (18)` in part 8 reported the mismatch against the 19 parsed |
| 11 | Every `C-nn` / `U-nn` cross-reference exists in `spec/06` / `spec/09` (45 and 16 items respectively) | yes — a stale unresolved-decision reference was reported; this check is what exposed that four of the unresolved-decision ids cited earlier in this extraction do not exist in `spec/09` (which has exactly 16 items) and that several contradiction links pointed at the wrong finding |
| 12 | The counts printed in `04-verification-undefined.md` §5 match the records (undefined, non-normative, permissions, review-only, other, total) | yes — it reported `reviewonly=79` against a registry count of 80 the moment four new records were added |

`req/_coverage.py` runs the complementary omission audit: it inverts the citation map and reports normative-marker lines (`MUST`, `never`, `always`, `required`, boxed formulae, …) in the requirement-dense regions that **no** record cites. Its scope is deliberately limited to the three regions where requirements are stated as requirements — the turn-`[54]` master prompt (L37638–38968), the turn-`[58]` bootstrap pack (L40600–41273), and the closing turns `[59]`–`[60]` (L41274–42312); the earlier design turns are cited from the location where each requirement was frozen, not from every place it was discussed. First run found 15 uncited lines; all 15 proved to be second statements of requirements already extracted, so each was added as an additional citation rather than a new record — **74/74 normative-marker lines cited, 0 uncited**.

Run with `--all-turns` the audit covers all 60 turns. The early and middle turns are design dialogue whose superseded drafts are deliberately not cited (the registry cites each requirement where it was frozen), so their uncited counts are expected; the frozen-content turns were triaged line by line and four requirements that the first pass had missed were recovered: the evaluator-input exclusion set (`Authority`/`Scope`/`Rights`/`Parent`/`Revocation state`, L13267–13281) as REQ-KERN-009; `Committed(D) ⇒ Canonical(D) ∧ IntegrityVerified(D)` (L33731–33738) as REQ-PERSIST-023; `CommittedSnapshot + ValidWAL + ValidEffectJournal + ReconciledEffects ⇒ UniqueRecoveredMachineState` (L34801–34812) as REQ-RECOV-022; and the reference interpreter's environment-copy permission (L12363–12367) as REQ-REF-017. The residue in those turns is LaTeX continuation lines (`\boxed{`, `\Rightarrow`), code comments, and commentary prose — no further requirement.

Two further passes followed. The formula-fragment scan found two capability requirements the frozen turn `[27]` states and no record covered: derivation atomicity from the evaluator's perspective (L19484–19498) as REQ-CAP-025, and constraint monotonicity `C₁ ≼ C₂ ⇒ derive(A,C₁) ≼ derive(A,C₂)` (L20027–20037) as REQ-CAP-026. The per-section citation audit then found the largest single omission: Phase 15C (turn `[48]`), whose 45 numbered sections had 42 uncited in their entirety — the reference value model, environment, CEK machine, transition rules, capability algebra and store, budget model, effect protocol, actor, scheduler, send/receive, marshalling, global state, persistence, crash semantics and host (15C.4–15C.19), the normalized observation and canonical actor-identity mapping (15C.20–15C.21), and the whole harness half — comparison levels, trace normalization, negative differential testing, short-circuit stage markers, the reference property suite, grammar, generator, shrinking, counterexample format, first-divergence, metamorphic testing, differential persistence, recovery independence, the canonical boundary, oracle hierarchy, anti-oracle-collapse, execution modes, determinism, LLM boundary, acceptance criteria, fault-injection validation, evidence classification and the final theorem (15C.23–15C.46). These were extracted as `req/01-registry-part8-reference-15C.md` (44 records), taking the registry from 497 to **541**; measured by re-running the audit with and without the new part file, the uncited count fell from 549 to **515** of 736 candidate lines, and cited sections rose from 3/45 to 45/45. The remaining uncited lines are early-turn superseded drafts and LaTeX continuation lines; they are candidates for judgement, not a claim of completeness.

A third pass triaged the prose-like residue of turns `[8]`, `[10]`, `[29]`, `[31]` and `[33]` line by line. It produced one new record — REQ-TEST-057, the 35-property minimum Phase 13 acceptance suite at L25223–25275 (`# 26. Phase 13 property suite`), kept whole because its items are one closed acceptance set — and ten second-location citations for requirements already extracted but stated earlier: capability gate precedes target and arguments (L21542, L22472–22480 → REQ-EFFECT-005); `ReplayHost` never executes the external effect again (L22333, L23234 → REQ-HOST-005); one transition per scheduler turn (L24345–24361 → REQ-ACTOR-012); `Send(v) ∧ v contains no delegation ⇒ Authority_{receiver}' = Authority_{receiver}` (L25294–25302 → REQ-CORE-010, whose INVARIANTS now carries both forms); attenuation removes and never adds (L4472 → REQ-CAP-016); generation-safe `CapRef` against arena reuse (L5958 → REQ-KERN-001); no inference of non-execution from a missing completion (L26186–26196 → REQ-CORE-014); no transparent recovery claimed for `Indeterminate` (L26736 → REQ-RECOV-017); no silent repair by the supervisor (L26931 → REQ-RECOV-012); and the LLM outside the trusted execution mechanism (L27102 → REQ-TRUST-005). Registry 541 → **542**.

This pass found and fixed, by that mechanism: three identifiers I had invented (`B_max`, `f_specific` as a literal token, `BudgetAllocationSpec::validate_and_escrow`), 83 `[turn]` labels that disagreed with the lines they annotated, 56 `SOURCE` fields with no turn marker at all, three stale anchors, and six statements whose wording did not match the source (`Value` tag constants, canonical map key type, hostile-allocation wording, `Expr::Delegate` line range, `EventSequence` shape, `ReconciliationOutcome` variants).
