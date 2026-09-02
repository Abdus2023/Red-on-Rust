<!-- GENERATED FILE — DO NOT EDIT BY HAND. -->
<!-- Source of truth: `term/_terms.py`.  Regenerate: `python3 term/_dict.py --write`. -->
<!-- Every line citation below is re-grepped against `Red-on-Rust.md` by `python3 term/_check.py`. -->

# 02 — Terminology Collision Register

**75 collisions.** Every terminology collision found in the frozen source and in the canonicalization layer is reported here; none is silently resolved. Severity: BLOCKING 4, MAJOR 51, MINOR 19, INFO 1. 72 are new findings not previously registered in `spec/06` or `req/03`; the remainder extend or correct an existing `C-`/`U-`/`AMB-` entry, which is named in **Previously registered as**.

A collision is filed when the source (or a document derived from it) uses one name for two incompatible things, two names for one thing without retracting either, a name for something never declared, or a citation for text that is not there. **Nothing is renamed to make a collision disappear.** The disposition states what the canonicalization layer does instead: record both, name the governing text, and escalate the decision where the source does not settle it.

## Kinds
| Kind | Meaning | Count |
|---|---|---|
| `SYMBOL-OVERLOAD` | one mathematical symbol, two or more denotations | 14 |
| `TYPE-HOMONYM` | one name, two or more incompatible type declarations | 14 |
| `FIELD-SET` | same type name, different field sets or field names | 10 |
| `SCOPE-DRIFT` | a name's scope changed between frozen eras without retraction | 8 |
| `UNDECLARED-VARIANT` | an `Enum::Variant` path is used in the frozen source but appears in no declaration of that enum | 7 |
| `ALIAS-DEFECT` | the canonicalization layer states an alias/definition the source does not support | 4 |
| `PREDICATE-SIGNATURE` | one predicate name, several arities/argument orders | 4 |
| `PROVENANCE-DEFECT` | a citation in the canonicalization layer does not point at the text it claims | 4 |
| `DIVERGENT-SHAPE` | the same type name is declared repeatedly with materially different variant or field shapes | 2 |
| `TYPE-ROLE-HOMONYM` | one name used as both a type and a predicate/symbol | 2 |
| `UNDEFINED-TYPE` | a name is used as a type but never declared | 2 |
| `METHOD-SIGNATURE` | one trait name, incompatible method names/returns | 1 |
| `PHANTOM-IDENTIFIER` | a register names an identifier that occurs nowhere in the frozen source | 1 |
| `STAGE-ORDER` | the same pipeline is written with different stage sequences | 1 |
| `STATE-VS-RECORD` | a lifecycle state, a record kind and a struct share a name | 1 |

## Summary
| ID | Collision | Kind | Severity | Terms | Previously | Decision needed |
|---|---|---|---|---|---|---|
| [X-01](#x-01) | `ValidatedPlan` is both a compiler stage type and a theorem predicate | TYPE-ROLE-HOMONYM | **BLOCKING** | 4 | — | YES |
| [X-50](#x-50) | The canonical envelope is specified with two field names, two tag widths and two endiannesses | FIELD-SET | **BLOCKING** | 4 | C-02 | YES |
| [X-54](#x-54) | Four `TAG_*` constant names denote two disjoint tag namespaces with different values | SYMBOL-OVERLOAD | **BLOCKING** | 4 | C-02 | YES |
| [X-67](#x-67) | `HostFault` is declared once with two variants, and eight different undeclared variant paths are used — six of them on the frozen replay path | UNDECLARED-VARIANT | **BLOCKING** | 6 | AMB-08, U-14, C-50 | YES |
| [X-02](#x-02) | The compilation pipeline is written with three different stage sequences | STAGE-ORDER | **MAJOR** | 7 | U-22 | no |
| [X-03](#x-03) | `ExecutablePlan`'s payload field is `ir: PlanIR` in two declarations and `expr: Expr` in three | FIELD-SET | **MAJOR** | 3 | — | YES |
| [X-04](#x-04) | The central theorem's first conjunct is `ValidatedRequest(E)` in one frozen statement and `ValidatedPlan(P)` in two | PREDICATE-SIGNATURE | **MAJOR** | 4 | — | YES |
| [X-05](#x-05) | `Authorized` has six incompatible signatures, including both orders in the governing invariant | PREDICATE-SIGNATURE | **MAJOR** | 4 | — | YES |
| [X-06](#x-06) | Two incompatible frozen `Observation` structs share one name | TYPE-HOMONYM | **MAJOR** | 4 | — | YES |
| [X-07](#x-07) | `EffectIssued` denotes a struct, a `WalRecord` variant and an `EffectJournalEntry` variant, with different payloads and field names | STATE-VS-RECORD | **MAJOR** | 6 | C-25 | YES |
| [X-08](#x-08) | The symbol `C` denotes the Consumable vector, the Constraint of `derive`, and a required-capability set | SYMBOL-OVERLOAD | **MAJOR** | 4 | — | no |
| [X-09](#x-09) | The symbol `R` denotes Reserved resources, the authority resource limit, a capability ceiling, a dynamic budget, a receipt, and the revocation set | SYMBOL-OVERLOAD | **MAJOR** | 4 | — | no |
| [X-10](#x-10) | The symbol `S` denotes the Snapshot, the authority Scope component, and concurrency Slots | SYMBOL-OVERLOAD | **MAJOR** | 3 | — | no |
| [X-12](#x-12) | The symbol `D` denotes the durable machine state and the duration consumable | SYMBOL-OVERLOAD | **MAJOR** | 3 | U-01 | no |
| [X-13](#x-13) | The symbol `L` denotes the durable WAL, the Lifetime authority component, and the transition-tuple log | SYMBOL-OVERLOAD | **MAJOR** | 4 | — | no |
| [X-16](#x-16) | `F` denotes fuel, the effect set, and 'effect invoked'; `M` denotes memory and a replay-tuple component | SYMBOL-OVERLOAD | **MAJOR** | 4 | U-22 | no |
| [X-17](#x-17) | Authority's fourth component is `T` in the frozen math and `L` in the frozen Rust sketch of the same turn | SYMBOL-OVERLOAD | **MAJOR** | 3 | — | no |
| [X-18](#x-18) | The machine configuration is written three ways: `Σ` (6 components), an unnamed 7-tuple, and `G`/`A_a` (9 components) | SCOPE-DRIFT | **MAJOR** | 4 | C-42, U-02 | no |
| [X-19](#x-19) | The budget gate is named `BudgetOK`, `WithinBudget`, `BudgetAvailable`, `ReserveOK`, `ReleaseOK` with six signatures | PREDICATE-SIGNATURE | **MAJOR** | 4 | C-07 | YES |
| [X-20](#x-20) | `HostPolicy` is declared with two incompatible methods: `is_permitted(…) -> bool` and `authorize(…) -> Result<(), HostPolicyError>` | METHOD-SIGNATURE | **MAJOR** | 2 | U-14, AMB-08 | YES |
| [X-21](#x-21) | `ActorStatus` is declared twice with incompatible variant payloads | TYPE-HOMONYM | **MAJOR** | 4 | C-18, AMB-05 | YES |
| [X-22](#x-22) | `PendingEffect.id` vs `ActorStatus::Pending.effect_id`: two spellings of one field, and `continuation` vs `reservation` | FIELD-SET | **MAJOR** | 4 | — | YES |
| [X-24](#x-24) | `ActorId` and `EffectId` are declared both as `pub type X = u64` and as `pub struct X(pub u64)` | TYPE-HOMONYM | **MAJOR** | 5 | — | YES |
| [X-25](#x-25) | `CapRef` is declared as `CapRef(pub(crate) u64)` and as `CapRef { index: u32, generation: u32 }` | FIELD-SET | **MAJOR** | 2 | — | no |
| [X-26](#x-26) | `Effect` is declared three times with three different field sets | FIELD-SET | **MAJOR** | 4 | — | no |
| [X-27](#x-27) | `EffectRequest` is declared three times; the frozen form drops the `cap: CapRef` field | FIELD-SET | **MAJOR** | 3 | — | no |
| [X-28](#x-28) | `Block` is declared as `Block(pub Vec<Value>)` and as `Block { forms: Vec<Form> }` | FIELD-SET | **MAJOR** | 3 | — | YES |
| [X-29](#x-29) | Names used as field types, stage names and AST nodes that are never declared | UNDEFINED-TYPE | **MAJOR** | 6 | U-02 | YES |
| [X-30](#x-30) | `PlanIR` is used with variants but never declared, and its variants use two superseded names | UNDEFINED-TYPE | **MAJOR** | 3 | C-17, U-05, AMB-25 | YES |
| [X-31](#x-31) | The durable log has five names, and a sixth name denotes a different in-memory object | SCOPE-DRIFT | **MAJOR** | 4 | U-16, AMB-14 | no |
| [X-32](#x-32) | `EffectJournal`: a separate durable structure, a superseded enum, and WAL record kinds — and a boxed theorem that counts it as a third component | SCOPE-DRIFT | **MAJOR** | 5 | C-25 | YES |
| [X-33](#x-33) | `Snapshot` denotes a persistence concept, `GlobalSnapshot` a type, and `EnvironmentSnapshot` an unrelated closure capture | TYPE-HOMONYM | **MAJOR** | 4 | U-02 | no |
| [X-34](#x-34) | The plan family: `Plan`, `PlanProposal`, `PlanIR`, `ExecutablePlan` overlap — and AMB-25 adds a fifth name that does not exist | SCOPE-DRIFT | **MAJOR** | 4 | AMB-25 | no |
| [X-35](#x-35) | `Expr::Request` is declared with two different field sets | FIELD-SET | **MAJOR** | 3 | C-17 | no |
| [X-36](#x-36) | Capability liveness and coverage are named three ways each, with different arguments | PREDICATE-SIGNATURE | **MAJOR** | 4 | — | YES |
| [X-38](#x-38) | Capability denial carries NINE names across eras (C-08 reports four), host-policy denial two, and two variants have split payload types | TYPE-HOMONYM | **MAJOR** | 6 | C-08, U-08, U-14, AMB-08 | YES |
| [X-39](#x-39) | spec/05 defines `Effect` with a `capability` field that no frozen declaration has | ALIAS-DEFECT | **MAJOR** | 3 | — | no |
| [X-40](#x-40) | spec/05 and mod/02 treat `ValidatedPlan`, `CapabilityCheckedPlan` and `PlanIR` as aliases of `ExecutablePlan` | ALIAS-DEFECT | **MAJOR** | 5 | — | no |
| [X-45](#x-45) | Two incompatible `Value` domains share one name | TYPE-HOMONYM | **MAJOR** | 4 | C-03, C-45, U-09, AMB-21 | YES |
| [X-47](#x-47) | `EventSequence` and `WalSequence` are separate newtypes with no stated relationship | TYPE-HOMONYM | **MAJOR** | 4 | U-16, AMB-14 | YES |
| [X-52](#x-52) | 'FROZEN' is applied to four different objects, and the README applies it to a fifth | SCOPE-DRIFT | **MAJOR** | 6 | — | no |
| [X-55](#x-55) | Turn [41]'s '(Frozen)' `Value` discriminant table lists 5 of 8 variants and contradicts turns [43]/[45] on `Capability` | FIELD-SET | **MAJOR** | 4 | C-02 | no |
| [X-57](#x-57) | `Request` denotes an `Expr` variant, a redex form, a theorem predicate, an implementation phase and a struct stem | SYMBOL-OVERLOAD | **MAJOR** | 5 | AMB-13, C-01 | no |
| [X-58](#x-58) | `Fault` is declared seven times and `HostPolicyDenied` carries two different payload types | TYPE-HOMONYM | **MAJOR** | 7 | AMB-08, C-08, U-08 | no |
| [X-59](#x-59) | C-08's provenance for the `Fault` taxonomy is wrong in three of its four citations and its fourth mis-describes the text it points at; U-08, spec/05 and REQ-CALC-013 repeat the error | PROVENANCE-DEFECT | **MAJOR** | 6 | C-08, U-08, U-14, AMB-08, C-53 | YES |
| [X-64](#x-64) | `Fault::StalePlan` is used by the frozen source at L28373 but is a variant of none of the seven `Fault` declarations | UNDECLARED-VARIANT | **MAJOR** | 3 | C-54, C-38, U-13, AMB-08, AMB-34, X-62, X-69 | YES |
| [X-65](#x-65) | `MarshalFault` is declared twice with completely disjoint variant sets, and is used as an elided `Fault` payload | TYPE-HOMONYM | **MAJOR** | 3 | AMB-08, U-14 | YES |
| [X-66](#x-66) | `CapabilityError::Invalid` is used as the `derive` fallback but never declared; the declared sibling `InvalidConstraint` is used for the same fallback in the same turn | UNDECLARED-VARIANT | **MAJOR** | 4 | U-14, U-08, X-59 | YES |
| [X-68](#x-68) | `HostFault` denotes a fault NAME in the v1 grammar and a Rust TYPE from turn [18]; `Revoked` denotes a fault name and a `CapabilityError` variant | TYPE-ROLE-HOMONYM | **MAJOR** | 3 | AMB-08, U-08, X-57, X-01 | YES |
| [X-69](#x-69) | Twelve `Fault::` variant paths are used in the frozen source and declared by no `Fault` enum | UNDECLARED-VARIANT | **MAJOR** | 5 | C-08, C-58, AMB-08, U-08, U-13 | YES |
| [X-70](#x-70) | Theorem 2's proof and the property-test matrix both depend on `Expr::Delegate`, which no `enum Expr` declaration admits | UNDECLARED-VARIANT | **MAJOR** | 6 | C-60, X-29, AMB-11, C-16, U-02 | YES |
| [X-71](#x-71) | `MachineEvent` is declared eight times and used with eight variant paths declared by none of them | UNDECLARED-VARIANT | **MAJOR** | 5 | U-28 | YES |
| [X-72](#x-72) | `CanonicalError` is declared seven times in four shapes, with the same variant names at different arities | DIVERGENT-SHAPE | **MAJOR** | 5 | C-47, C-48, C-49, U-29, U-14 | YES |
| [X-73](#x-73) | `StepResult` is two disjoint enums — the CEK machine's and the actor scheduler's — sharing one name | TYPE-HOMONYM | **MAJOR** | 5 | C-63, X-23, U-26 | YES |
| [X-74](#x-74) | `ActorStatus` is declared seven times in three shapes; X-21 records only two declarations | DIVERGENT-SHAPE | **MAJOR** | 6 | C-64, X-21, U-27 | YES |
| [X-11](#x-11) | The symbol `A` denotes Authority and, subscripted, an actor's state | SYMBOL-OVERLOAD | **MINOR** | 2 | — | no |
| [X-14](#x-14) | The symbol `H` denotes the effect journal while calligraphic `ℋ` denotes the heap | SYMBOL-OVERLOAD | **MINOR** | 3 | — | no |
| [X-15](#x-15) | The symbol `B` denotes the Budget and, in turn [1], a Block | SYMBOL-OVERLOAD | **MINOR** | 2 | — | no |
| [X-23](#x-23) | `RunState::Faulted` vs `ActorStatus::Fault`: near-homonym variants of two distinct enums | TYPE-HOMONYM | **MINOR** | 3 | C-18, AMB-05 | no |
| [X-37](#x-37) | `Authority` is declared seven times and `Frame` eleven times, with an elided `AuthorityNode` between them | TYPE-HOMONYM | **MINOR** | 5 | AMB-26, U-02 | YES |
| [X-41](#x-41) | spec/01 and mod/02 reproduce one of three pipeline orderings, in an order the frozen structs contradict | ALIAS-DEFECT | **MINOR** | 5 | — | no |
| [X-42](#x-42) | `LogicalTime` is glossed in the source as 'a logical clock or deterministic timestamp' | SCOPE-DRIFT | **MINOR** | 2 | — | no |
| [X-43](#x-43) | `ReplayHost`'s trace field is `recorded_receipts` in one frozen form and `trace` in the other | FIELD-SET | **MINOR** | 3 | C-22 | no |
| [X-44](#x-44) | Three cost types and five cost functions: `Cost`, `EffectCost`, `ResourceUsage`, `CostModel`, `cost_C`/`cost_io`/`cost_res` | TYPE-HOMONYM | **MINOR** | 6 | AMB-23 | no |
| [X-46](#x-46) | `GlobalState` vs `GlobalConfig` | TYPE-HOMONYM | **MINOR** | 1 | C-42 | no |
| [X-48](#x-48) | 'Reference machine' (pre-15C) and 'reference model' (15C) denote different objects | SCOPE-DRIFT | **MINOR** | 2 | C-33 | no |
| [X-49](#x-49) | Three identifier namespaces begin with `M`: milestones `M0`-`M11`, mutations `M001`-`M018`, and the memory symbol `M` | SYMBOL-OVERLOAD | **MINOR** | 2 | — | no |
| [X-51](#x-51) | spec/05's trait list omits `CanonicalSerialize`, the trait that carries the format | ALIAS-DEFECT | **MINOR** | 3 | — | no |
| [X-56](#x-56) | The byte 0x00 carries four distinct meanings across four encoding layers | SYMBOL-OVERLOAD | **MINOR** | 3 | C-02 | no |
| [X-60](#x-60) | req/00-method §5.4 asserts there is no `15C.1` heading; there is one, and 15C spans two heading levels | PROVENANCE-DEFECT | **MINOR** | 2 | — | no |
| [X-61](#x-61) | spec/09 U-15 remains an open decision on a premise req/03 AMB-15 has withdrawn as false | PROVENANCE-DEFECT | **MINOR** | 5 | U-15, AMB-15, U-06 | no |
| [X-62](#x-62) | req/03 AMB-25 lists `PlannerState`, an identifier that does not occur in the source | PHANTOM-IDENTIFIER | **MINOR** | 5 | AMB-25 | no |
| [X-63](#x-63) | C-09 and AMB-24 cite README line ranges that contain no status block | PROVENANCE-DEFECT | **MINOR** | 4 | C-09, AMB-24 | no |
| [X-75](#x-75) | Residual used-but-undeclared variant paths across five more enums, and one variant silently dropped | UNDECLARED-VARIANT | **MINOR** | 6 | C-65, X-65, X-66, C-49, U-02, U-09 | YES |
| [X-53](#x-53) | Implementation status is 'READY' twice and 'IN PROGRESS' once in the source, and the README reverses the order | SCOPE-DRIFT | **INFO** | 3 | C-09, AMB-24 | no |

## Blocking
These must be decided before the work they gate can start. Each names the milestone or obligation it blocks in its **Decision needed** field.
- **X-01** — `ValidatedPlan` is both a compiler stage type and a theorem predicate
- **X-50** — The canonical envelope is specified with two field names, two tag widths and two endiannesses
- **X-54** — Four `TAG_*` constant names denote two disjoint tag namespaces with different values
- **X-67** — `HostFault` is declared once with two variants, and eight different undeclared variant paths are used — six of them on the frozen replay path

---

## X-01

**`ValidatedPlan` is both a compiler stage type and a theorem predicate**

- **Kind:** `TYPE-ROLE-HOMONYM` — one name used as both a type and a predicate/symbol
- **Severity:** BLOCKING
- **Terms affected:** T-04 `ValidatedPlan`, T-06 `ExecutablePlan`, T-03 `ParsedBlock`, T-05 `CapabilityCheckedPlan`

### Evidence (frozen source)

| Line | Text at that line | What it denotes there |
|---|---|---|
| `Red-on-Rust.md` L865 | `pub struct ValidatedPlan { ir: PlanIR, effects: EffectSet }` | a compiler stage struct — effect-annotated, NOT capability-checked, NOT bounded |
| `Red-on-Rust.md` L13488 | `pub struct ValidatedPlan {` | the same struct re-declared in the frozen turn-[21] era |
| `Red-on-Rust.md` L1784 | `\operatorname{ValidatedPlan}(P)` | a PREDICATE over the plan P in the central security property |
| `Red-on-Rust.md` L27494 | `&ValidatedPlan(P)\\` | the same predicate as the first conjunct of the frozen central theorem |
| `Red-on-Rust.md` L41338 | `ValidatedPlan(P)` | the same predicate in the README/turn-[60] statement of the theorem |

### The collision

One frozen name carries two incompatible roles. As a TYPE it denotes the second compiler stage, which has not been capability-checked and not been resource-bounded. As a PREDICATE `ValidatedPlan(P)` its argument P is the plan that enters the machine — i.e. an `ExecutablePlan`, the fourth stage. The type and the predicate's argument are therefore different objects, and the predicate is true of something the type is not.

### Why it matters

An implementer who binds the theorem's `P` to the struct `ValidatedPlan` gets a plan that has passed effect annotation only. `CapabilityWithinCeiling(E)`, `BudgetAvailable(E)` and the constructor-privacy guarantee would then be checked against an artifact that never went through capability or resource analysis — the central theorem would be stated about the wrong object and the security gate would be two stages short.

### Disposition

BOTH uses are frozen identifiers and NEITHER is renamed. Prose MUST qualify: `ValidatedPlan` (the stage type) vs `ValidatedPlan(P)` (the theorem predicate, whose argument is an `ExecutablePlan`). Code MUST NOT reuse the identifier for both: the predicate belongs in a verification context, the struct in `ror-compiler`. An explicit decision is required on whether the predicate is to be read as `IsExecutablePlan(P)`.

### Decision needed

Yes — read the theorem's `ValidatedPlan(P)` as a predicate over `ExecutablePlan`, or restate the conjunct. Affects R-CORE-02.

## X-50

**The canonical envelope is specified with two field names, two tag widths and two endiannesses**

- **Kind:** `FIELD-SET` — same type name, different field sets or field names
- **Severity:** BLOCKING
- **Terms affected:** T-62 `CanonicalEnvelope`, T-63 `CanonicalPayload`, T-21 `EffectDigest`, T-46 `WalFrame`
- **Previously registered as:** `C-02`

### Evidence (frozen source)

| Line | Text at that line | What it denotes there |
|---|---|---|
| `Red-on-Rust.md` L28298 | `/// [format_version: u8] [type_tag: u32 LE] [length: u32 LE] [payload: ...]` | turn [36]: `format_version`, `type_tag: u32 LE`, `length: u32 LE` |
| `Red-on-Rust.md` L29540 | `version:u8` | turn [40]: `version`, and `type_tag:u8`, `payload_length:u32_be` |
| `Red-on-Rust.md` L29905 | `payload_length: u32 BE` | turn [41]: big-endian length |
| `Red-on-Rust.md` L33816 | `version \| type_tag \| payload_length \| payload` | turn [46]: the frozen field sequence |
| `Red-on-Rust.md` L35102 | `pub payload_length: u32,        // Big-endian, checked` | turn [47]: `WalFrame` uses the same big-endian length |
| `Red-on-Rust.md` L38150 | `payload_length: u32 BE` | turn [54] master prompt: the frozen form restated |

### The collision

The `CanonicalSerialize` trait's own doc comment specifies the wire format as `[format_version: u8] [type_tag: u32 LE] [length: u32 LE] [payload]`, while every later statement — the 15A grammar, the 15B frame, and the turn-[54] master prompt — specifies `version: u8 | type_tag: u8 | payload_length: u32 BE | payload`. The two differ in a field NAME (`format_version`/`length` vs `version`/`payload_length`), the tag WIDTH (`u32` vs `u8`) and the ENDIANNESS (`LE` vs `BE`).

### Why it matters

This is the byte-level foundation of every digest and checksum in the system: `EffectDigest`, `StateDigest`, `ResultDigest`, the WAL frame checksum and snapshot determinism (R-PERSIST-05) all hash canonical bytes. An encoder built from the trait doc comment produces bytes that differ from the frozen format in the first six bytes of every object, so no digest would match, no golden vector would verify, and differential persistence testing (15C.34) would diverge on every case. The defect sits in an API contract comment, which is where an implementer looks first. It is not covered by C-02 (which concerns stale PRIMITIVE tags in §1.3).

### Disposition

Both specifications recorded verbatim; NO field is renamed and the superseded comment is not deleted from the record. The dictionary states the frozen form (L38147-38150, L33816) as canonical on the latest-frozen-text rule and flags the trait doc comment at L28298 as contradicting it — an explicit decision is required because the contradiction is inside an API contract, not in narrative prose. Blocks milestone M1 (canonical serialization).

### Decision needed

Yes — correct or retract the `CanonicalSerialize` doc-comment format at L28298; it contradicts the frozen 15A/15B envelope. Blocks M1.

## X-54

**Four `TAG_*` constant names denote two disjoint tag namespaces with different values**

- **Kind:** `SYMBOL-OVERLOAD` — one mathematical symbol, two or more denotations
- **Severity:** BLOCKING
- **Terms affected:** T-62 `CanonicalEnvelope`, T-63 `CanonicalPayload`, T-31 `Value`, T-45 `WAL`
- **Previously registered as:** `C-02`

### Evidence (frozen source)

| Line | Text at that line | What it denotes there |
|---|---|---|
| `Red-on-Rust.md` L29952 | `pub const TAG_BOOL: u8 = 0x10;` | turn [41]: `TAG_BOOL` is an ENVELOPE type tag |
| `Red-on-Rust.md` L33171 | `const TAG_UNIT: u8 = 0x00; const TAG_BOOL: u8 = 0x01; const TAG_INTEGER: u8 = 0x02;` | turn [45]: `TAG_BOOL` is a VALUE VARIANT discriminant |
| `Red-on-Rust.md` L29955 | `pub const TAG_SYMBOL: u8 = 0x20;` | turn [41]: envelope type tag for `Symbol` |
| `Red-on-Rust.md` L32368 | `const TAG_SYMBOL: u8 = 0x04;` | turn [43]: discriminant for `Value::Symbol` |
| `Red-on-Rust.md` L33194 | `Self::TAG_SYMBOL => {` | turn [45]: the discriminant arm |
| `Red-on-Rust.md` L33195 | `let sym_payload = cursor.read_envelope_payload(Symbol::TYPE_TAG)?;` | turn [45]: the ENVELOPE tag, one line below the discriminant of the same name |
| `Red-on-Rust.md` L29953 | `pub const TAG_INTEGER: u8 = 0x11;` | turn [41]: envelope type tag |
| `Red-on-Rust.md` L29954 | `pub const TAG_STRING: u8 = 0x12;` | turn [41]: envelope type tag |

### The collision

The identifier prefix `TAG_` names two disjoint namespaces. In turn [41]'s frozen 15A const block, `TAG_BOOL`/`TAG_INTEGER`/`TAG_STRING`/`TAG_SYMBOL`/`TAG_CAPREF`/`TAG_VEC`/`TAG_BTREEMAP` are ENVELOPE type tags (0x10, 0x11, 0x12, 0x20, 0x30, 0x40, 0x41). In turns [43] and [45], the SAME four names `TAG_BOOL`/`TAG_INTEGER`/`TAG_STRING`/`TAG_SYMBOL` are `Value` VARIANT DISCRIMINANTS with different values (0x01, 0x02, 0x03, 0x04). Turn [41] itself uses the prefix `DISC_` for discriminants, so the rename to `TAG_` in turns [43]-[45] is what creates the clash. Both blocks are labeled frozen; the later one governs the discriminants (per C-02) but nothing revokes turn [41]'s `TAG_*` envelope constants, which the frozen standalone tags `Value 0x00 / Symbol 0x20 / CapRef 0x30 / ActorId 0x40 / EffectId 0x41` still depend on.

### Why it matters

These are Rust constants, so the collision is not merely notational: a module that imports turn [41]'s const block and turn [45]'s `impl Value` block does not compile, and an implementer who resolves the clash by keeping one set silently re-tags the other layer. Concretely, `TAG_SYMBOL = 0x04` in the discriminant namespace and `0x20` in the envelope namespace, and the frozen `Value::Symbol` encoder needs BOTH in the same function (L33194-33195). Getting either wrong changes `EffectDigest`, `StateDigest` and `ResultDigest`, so every golden vector, WAL frame and snapshot digest diverges. R-CANON-03/04 and the 15C.36 differential boundary cannot be satisfied while the names are ambiguous. Blocks milestone M1.

### Disposition

Both namespaces recorded verbatim with their values; NO constant is renamed, because both are frozen identifiers and renaming either would silently change an API. The dictionary separates them as two TERMS — `EnvelopeTypeTag` (T-63, the `TAG_*`/`TYPE_TAG` namespace, values 0x00/0x10-0x12/0x20/0x30/0x40/0x41) and `ValueDiscriminant` (T-62, the `DISC_*`/`TAG_*` namespace, values 0x00-0x07) — and requires that any prose about a tag byte name its layer. The decision needed is which const block an implementation may import, and under what module path, since the two cannot coexist unqualified.

### Decision needed

Yes — the frozen 15A const blocks use `TAG_*` for two disjoint tag namespaces with conflicting values. Decide the qualified paths an implementation must use. Blocks M1.

## X-67

**`HostFault` is declared once with two variants, and eight different undeclared variant paths are used — six of them on the frozen replay path**

- **Kind:** `UNDECLARED-VARIANT` — an `Enum::Variant` path is used in the frozen source but appears in no declaration of that enum
- **Severity:** BLOCKING
- **Terms affected:** T-74 `HostFault`, T-42 `ReplayHost`, T-44 `HostExecutor`, T-70 `Fault`, T-41 `HostPolicy`, T-52 `RecoveryFault`
- **Previously registered as:** `AMB-08`, `U-14`, `C-50`

### Evidence (frozen source)

| Line | Text at that line | What it denotes there |
|---|---|---|
| `Red-on-Rust.md` L10820 | `pub enum HostFault {` | turn [18]: the ONLY declaration — two variants |
| `Red-on-Rust.md` L10821 | `IoError(String),` | declared variant 1 |
| `Red-on-Rust.md` L10822 | `PolicyViolation(String),` | declared variant 2 |
| `Red-on-Rust.md` L1203 | `HostFault::UnboundCapability` | turn [3]: UNDECLARED |
| `Red-on-Rust.md` L1208 | `HostFault::ConcreteScopeViolation` | turn [3]: UNDECLARED (also L1214) |
| `Red-on-Rust.md` L1210 | `HostFault::Io` | turn [3]: UNDECLARED — near-miss of the declared `IoError` (also L1216) |
| `Red-on-Rust.md` L1245 | `HostFault::ReplayTraceExhausted` | turn [3]: UNDECLARED — 1st of 6 uses |
| `Red-on-Rust.md` L10546 | `HostFault::TraceExhausted` | turn [18]: UNDECLARED — a THIRD name for the same exhausted-trace condition |
| `Red-on-Rust.md` L10550 | `HostFault::ReplayIdMismatch` | turn [18]: UNDECLARED |
| `Red-on-Rust.md` L10553 | `HostFault::ReplayDigestMismatch` | turn [18]: UNDECLARED |
| `Red-on-Rust.md` L24020 | `HostFault::ReplayTraceExhausted` | turn [30]: UNDECLARED |
| `Red-on-Rust.md` L25496 | `HostFault::ReplayTraceExhausted` | turn [32]: UNDECLARED |
| `Red-on-Rust.md` L25500 | `HostFault::ReplayCorruption` | turn [32]: UNDECLARED |
| `Red-on-Rust.md` L25838 | `HostFault::ReplayTraceExhausted` | turn [32]: UNDECLARED |
| `Red-on-Rust.md` L25841 | `HostFault::ReplayCorruption` | turn [32]: UNDECLARED — 'Reject mismatched digest' |
| `Red-on-Rust.md` L34519 | `HostFault::ReplayTraceExhausted` | turn [46]: UNDECLARED |
| `Red-on-Rust.md` L34522 | `HostFault::ReplayCorruption` | turn [46]: UNDECLARED |
| `Red-on-Rust.md` L34528 | `HostFault::ReplayCorruption` | turn [46]: UNDECLARED |
| `Red-on-Rust.md` L35225 | `HostFault::ReplayTraceExhausted` | turn [47]: UNDECLARED — the frozen 15C.42 `ReplayHost` |
| `Red-on-Rust.md` L35226 | `HostFault::ReplayCorruption` | turn [47]: UNDECLARED — the frozen 15C.42 `ReplayHost` |
| `Red-on-Rust.md` L23813 | `Host(HostFault),` | turn [30]: `HostFault` is the payload of the frozen `Fault::Host` variant |

### Evidence (canonicalization layer)

| File:line | Text at that line | Note |
|---|---|---|
| `req/01-registry-part4-durability-concurrency.md`:316 | ```ReplayTraceExhausted` is not a variant`` | AMB-08 dependency note — attributes the gap to the `Fault` enum, not to `HostFault` |
| `spec/05-terminology.md`:112 | ```HostFault` variants`` | listed as 'not enumerated' although L10820 declares two variants and eight are used |
| `mod/09-host.md`:38 | `ReplayTraceExhausted` | module prose citing an undeclared variant as if it were frozen |

### The collision

`pub enum HostFault` is declared exactly once, at L10820 (turn [18]), with two variants: `IoError(String)` and `PolicyViolation(String)`. The source then uses eight distinct `HostFault::` paths, **none** of which is declared: `UnboundCapability` (L1203), `ConcreteScopeViolation` (L1208, L1214), `Io` (L1210, L1216), `ReplayTraceExhausted` (L1245, L24020, L25496, L25838, L34519, L35225 — six uses), `ReplayCorruption` (L25500, L25841, L34522, L34528, L35226, L35227 — six uses), `TraceExhausted` (L10546), `ReplayIdMismatch` (L10550) and `ReplayDigestMismatch` (L10553). Neither declared variant is ever used, and `Io` is a near-miss of `IoError`. Two names denote the exhausted-trace condition (`ReplayTraceExhausted` six times, `TraceExhausted` once) and three denote a replay mismatch (`ReplayCorruption`, `ReplayIdMismatch`, `ReplayDigestMismatch`). `ReplayCorruption` is *also* a declared `Fault` variant (L23814), so the same identifier denotes a fault at two different levels of the taxonomy. The heaviest uses sit on the frozen 15C.42 `ReplayHost` (L35225-35227, turn [47]) and on the R-HOST-03/04/05 replay obligations — the code REQ-HOST-008 is written against.

### Why it matters

This is BLOCKING, not cosmetic. `ReplayHost` (T-42) is one of the 25 terms the normalization request names explicitly, and ordered replay is the mechanism that makes the differential observer's host side deterministic (R-HOST-03/04/05, REQ-HOST-007/008). None of the fault values that path can produce is declared anywhere, so the host error type cannot be written without inventing variants — which R-SCOPE-03 prohibits. Because `Fault::Host(HostFault)` (L23813) embeds `HostFault` in the machine-visible fault taxonomy, the gap propagates into the observation domain compared under R-REF-05. AMB-08 notices only one instance ('`ReplayTraceExhausted` is not a variant of the frozen `Fault` enum', req/01-part4 L316) and frames it as a `Fault`-enum problem; it is a `HostFault`-declaration problem, and it is eight variants wide, not one.

### Disposition

REPORTED as BLOCKING; no variant set invented and nothing renamed. T-74 records the single declaration verbatim and lists all eight undeclared paths plus both unused declared variants as protected tokens, so no implementation can treat the set as closed. AMB-08's dependency note is corrected to point at `HostFault` rather than the `Fault` enum, and a new AMB entry carries the decision. U-14 (error-variant enumeration) is the owning decision and is now BLOCKING-severity for this type: the host error enum must be declared before R-HOST-03/04/05 can be implemented or tested.

### Decision needed

Yes — BLOCKING. Declare `HostFault`'s variant set: which of `ReplayTraceExhausted`/`TraceExhausted` and `ReplayCorruption`/`ReplayIdMismatch`/`ReplayDigestMismatch` survive, whether `Io` is `IoError(String)`, and how `HostFault::ReplayCorruption` relates to `Fault::ReplayCorruption`.

## X-02

**The compilation pipeline is written with three different stage sequences**

- **Kind:** `STAGE-ORDER` — the same pipeline is written with different stage sequences
- **Severity:** MAJOR
- **Terms affected:** T-03 `ParsedBlock`, T-04 `ValidatedPlan`, T-05 `CapabilityCheckedPlan`, T-06 `ExecutablePlan`, T-07 `NormalizedAST`, T-08 `PlanIR`, T-01 `Block`
- **Previously registered as:** `U-22`

### Evidence (frozen source)

| Line | Text at that line | What it denotes there |
|---|---|---|
| `Red-on-Rust.md` L561 | `Block` | ordering 1 (turn [2]): Block → ParsedBlock → ValidatedPlan → CapabilityCheckedPlan → ExecutablePlan |
| `Red-on-Rust.md` L567 | `CapabilityCheckedPlan` | ordering 1 names four intermediate stages |
| `Red-on-Rust.md` L9100 | `Block` | ordering 1 restated (turn [17]), ending 'Machine execution' |
| `Red-on-Rust.md` L13595 | `ParsedBlock` | ordering 2 (turn [21]): Block → ParsedBlock → ValidatedPlan → PlanIR → ExecutablePlan; CapabilityCheckedPlan dropped, PlanIR inserted as a stage |
| `Red-on-Rust.md` L13603 | `PlanIR` | ordering 2 makes PlanIR a STAGE after ValidatedPlan |
| `Red-on-Rust.md` L39271 | `NormalizedAST` | ordering 3 (turn [58]): Block → NormalizedAST → ValidatedPlan → PlanIR → ExecutablePlan; ParsedBlock AND CapabilityCheckedPlan both dropped |
| `Red-on-Rust.md` L39273 | `ValidatedPlan` | ordering 3 places ValidatedPlan after NormalizedAST |

### The collision

Three renderings of the same pipeline disagree on which stages exist and in what order. Ordering 3 is the latest, and it omits two of the four frozen stage TYPES (`ParsedBlock`, `CapabilityCheckedPlan`) while promoting two field types (`NormalizedAST`, `PlanIR`) to stages. The frozen structs contradict the stage reading: `ParsedBlock { ast: NormalizedAST }` makes `NormalizedAST` a FIELD of stage 1, and `ValidatedPlan { ir: PlanIR, effects: EffectSet }` makes `PlanIR` a FIELD of stage 2 — neither is a stage between the others.

### Why it matters

The pipeline is the enforcement structure of `Block ≠ ExecutablePlan` (N-01). An implementation built from ordering 3 has no capability-checked stage, so `κ_req ⪯ κ_ambient` is never a separate gate; built from ordering 2 it also has none. U-22 already records that no pipeline stage performs effect-set inference; this collision shows the stage list itself is not single-valued.

### Disposition

All three renderings are recorded verbatim; none is deleted and no stage type is renamed. The dictionary takes the TYPE declarations (L864-L869, the only place stages are given fields) as authoritative for what the stages ARE, and records the three diagrams as three renderings of the same pipeline. An explicit decision is required on whether `CapabilityCheckedPlan` survives as a distinct stage or is folded into 'capability analysis'.

## X-03

**`ExecutablePlan`'s payload field is `ir: PlanIR` in two declarations and `expr: Expr` in three**

- **Kind:** `FIELD-SET` — same type name, different field sets or field names
- **Severity:** MAJOR
- **Terms affected:** T-06 `ExecutablePlan`, T-08 `PlanIR`, T-30 `Expr`

### Evidence (frozen source)

| Line | Text at that line | What it denotes there |
|---|---|---|
| `Red-on-Rust.md` L869 | `pub struct ExecutablePlan {` | turn [3]: payload field `ir: PlanIR` (L870) |
| `Red-on-Rust.md` L870 | `ir: PlanIR,` | the turn-[3] payload field |
| `Red-on-Rust.md` L13493 | `pub struct ExecutablePlan {` | turn [21]: payload field `expr: Expr` (L13494) |
| `Red-on-Rust.md` L13494 | `expr: Expr,` | the turn-[21] payload field |
| `Red-on-Rust.md` L14104 | `pub(crate) expr: Expr,` | turn [22]: `expr: Expr` |
| `Red-on-Rust.md` L14488 | `pub(crate) expr: Expr,` | turn [22] restated |
| `Red-on-Rust.md` L39973 | `ir: PlanIR,` | turn [58] bootstrap pack: REVERTS to `ir: PlanIR` |

### The collision

Five declarations of one frozen type use two different names AND two different types for the payload: `ir: PlanIR` (turns [3] and [58]) vs `expr: Expr` (turns [21] and [22], twice). `Expr` is the frozen 12-constructor AST; `PlanIR` is never declared and its only visible variants (`Invoke`, `Spawn { plan, trust_level }`) use a superseded surface name (C-17) and a retracted isolation field (U-05).

### Why it matters

The payload field is what the machine evaluates. Under 'latest frozen text governs' the turn-[58] `ir: PlanIR` would win — which would make the runtime evaluate an undeclared type whose variants are superseded, and would contradict the frozen `Expr` AST, `EvalState.expr`, and every transition rule written over `Expr`. This is a type-level contradiction in the single most security-critical artifact in the system.

### Disposition

Both field names and both field types are recorded; NEITHER is renamed and neither is silently dropped. The dictionary reports the contradiction and requires an explicit decision. Evidence favouring `expr: Expr` (declared AST, used by `EvalState`, `step()`, and all transition rules) is stated as evidence, not applied.

### Decision needed

Yes — which payload field/type is frozen: `expr: Expr` or `ir: PlanIR`. Blocks R-COMPILE-04/05 and M2.

## X-04

**The central theorem's first conjunct is `ValidatedRequest(E)` in one frozen statement and `ValidatedPlan(P)` in two**

- **Kind:** `PREDICATE-SIGNATURE` — one predicate name, several arities/argument orders
- **Severity:** MAJOR
- **Terms affected:** T-04 `ValidatedPlan`, T-02 `PlanProposal`, T-16 `Effect`, T-17 `EffectRequest`

### Evidence (frozen source)

| Line | Text at that line | What it denotes there |
|---|---|---|
| `Red-on-Rust.md` L23040 | `ValidatedRequest(E)` | turn [29]: first conjunct, argument is the EFFECT E |
| `Red-on-Rust.md` L23694 | `\text{ValidatedRequest}(E)` | turn [30] 'strongest Phase 12 theorem', boxed |
| `Red-on-Rust.md` L27494 | `&ValidatedPlan(P)\\` | turn [33]: first conjunct, argument is the PLAN P |
| `Red-on-Rust.md` L41338 | `ValidatedPlan(P)` | turn [60]/README: first conjunct, argument is the PLAN P |

### The collision

The single most important formula in the specification — `ExternalEffect(E) ⇒ …` — exists in two forms that differ in their FIRST conjunct, and the difference is not cosmetic: `ValidatedRequest(E)` is a predicate about the request being validated (argument: an `Effect`), while `ValidatedPlan(P)` is a predicate about the plan being validated (argument: a plan). `ValidatedRequest` occurs nowhere else in 42,312 lines.

### Why it matters

The two readings impose different obligations. 'The request was validated' is a runtime, per-effect property (gates 1-13 of the 16-step sequence). 'The plan was validated' is a compile-time, per-plan property (R-COMPILE-01..05). An implementation satisfying only one would claim conformance with R-CORE-02 while leaving the other half unchecked.

### Disposition

Both forms are recorded verbatim. The canonicalization layer (spec/00 §4, spec/01 R-CORE-02, README) already adopts `ValidatedPlan(P)` per latest-frozen-text; this entry records that the earlier form exists, that its argument type differs, and that no supersession note covers the change. `ValidatedRequest` is NOT forbidden (it is frozen source text) but is NOT canonical prose.

### Decision needed

Yes — confirm which conjunct R-CORE-02 states, and whether both properties are required (they are not equivalent).

## X-05

**`Authorized` has six incompatible signatures, including both orders in the governing invariant**

- **Kind:** `PREDICATE-SIGNATURE` — one predicate name, several arities/argument orders
- **Severity:** MAJOR
- **Terms affected:** T-10 `Authority`, T-09 `CapRef`, T-13 `CapabilityKernel`, T-16 `Effect`

### Evidence (frozen source)

| Line | Text at that line | What it denotes there |
|---|---|---|
| `Red-on-Rust.md` L3293 | `Authorized(E,\kappa)` | turn [6]: (Effect, capability-map) — 2 arguments |
| `Red-on-Rust.md` L4687 | `Authorized(E)` | turn [8]: (Effect) — 1 argument |
| `Red-on-Rust.md` L5998 | `Authorized(A,E,t)` | turn [10]: (Authority, Effect, time) — 3 arguments |
| `Red-on-Rust.md` L6548 | `/// Canonical Authorization Predicate: Authorized(A, E, t)` | turn [11] declares THIS the canonical predicate |
| `Red-on-Rust.md` L7152 | `\text{Authorized}(\kappa(c_{ref}), E, t)` | turn [13]: (κ(c), Effect, time) |
| `Red-on-Rust.md` L8548 | `Authorized(A_c,E,t)` | turn [15]: (A_c, Effect, time) |
| `Red-on-Rust.md` L41339 | `Authorized(E,\kappa,t)` | turn [60]/README: (Effect, capability-map, time) — argument ORDER SWAPPED vs the declared canonical form |

### The collision

The authorization predicate — the heart of the trust model — is written with six different arities and argument orders. Turn [11] explicitly declares `Authorized(A, E, t)` 'the Canonical Authorization Predicate', yet the frozen governing invariant in the README and turn [60] writes `Authorized(E, κ, t)`: the arguments are transposed and the second is the whole capability map `κ` rather than an `Authority`.

### Why it matters

The signature determines what the kernel is given. `Authorized(A,E,t)` takes an already-resolved `Authority` (so `κ(c)` resolution happens before the call); `Authorized(E,κ,t)` takes the map (so resolution happens inside). Those are different APIs with different trust boundaries, and N-03 (`CapRef ≠ Authority`) is enforced precisely at that resolution step. A transposed signature also makes `¬Authorized(E,κ,t) ⇒ ¬ExternalEffect(E)` (R-CORE-03) un-type-checkable against the declared canonical form.

### Disposition

All six signatures are recorded; none is renamed and none is deleted. The dictionary requires qualified prose that always shows the argument list. spec/01 R-CORE-02 and R-CORE-03 currently use both orders in adjacent requirements; that is reported (X-41 family) rather than silently harmonized. An explicit decision is required on the canonical signature.

### Decision needed

Yes — freeze one signature for `Authorized` and state whether the second argument is an `Authority` or the map `κ`. Affects R-CORE-02/03, R-KERN-02.

## X-06

**Two incompatible frozen `Observation` structs share one name**

- **Kind:** `TYPE-HOMONYM` — one name, two or more incompatible type declarations
- **Severity:** MAJOR
- **Terms affected:** T-54 `Observation (planner-facing)`, T-57 `Observation (differential)`, T-02 `PlanProposal`, T-58 `ReferenceModel`

### Evidence (frozen source)

| Line | Text at that line | What it denotes there |
|---|---|---|
| `Red-on-Rust.md` L27156 | `pub struct Observation {` | turn [33] PLANNER-facing: `{sequence, actor, value, events, faults, available_capabilities, budget}` — LLM-boundary input data |
| `Red-on-Rust.md` L36170 | `pub struct Observation {` | turn [48] DIFFERENTIAL: `{terminal_states, event_trace, effects, budgets, scheduler_trace, faults, state_digest}` — test comparison data |

### The collision

One name, two frozen declarations, disjoint field sets, different producers, different consumers, and different trust roles. The turn-[33] type is what the untrusted planner is shown (capability SUMMARIES only); the turn-[48] type is what the comparator consumes, and the source itself says it 'is a test representation, not a runtime serialization format' and 'must not become a third semantic wire protocol'.

### Why it matters

This is structurally the same defect as the `Value` domain collision (C-03/C-45) but it is NOT registered anywhere. The consequences are worse in one respect: if the planner-facing type is used as the differential observation, the oracle collapses to what the planner is allowed to see (15C.38 anti-oracle-collapse), and if the differential type is handed to the planner it leaks internal machine state (scheduler trace, state digest) across the untrusted boundary. Neither type's element types (`GlobalEvent`, `CapabilitySummary`, `BudgetSummary`, `Observed*`) is declared.

### Disposition

Both declarations are recorded verbatim and NEITHER is renamed, because renaming a frozen Rust type is an API change requiring an explicit decision. The dictionary disambiguates in PROSE only, by the parenthetical qualifiers `Observation (planner-facing)` and `Observation (differential)`, and makes the separation a law (N-22). spec/05 §5 lists only the differential sense; that omission is part of this finding.

### Decision needed

Yes — give the two types distinct frozen names, or state that one is normative. Affects R-PLANNER-01 and R-REF-05.

## X-07

**`EffectIssued` denotes a struct, a `WalRecord` variant and an `EffectJournalEntry` variant, with different payloads and field names**

- **Kind:** `STATE-VS-RECORD` — a lifecycle state, a record kind and a struct share a name
- **Severity:** MAJOR
- **Terms affected:** T-18 `EffectIssued`, T-47 `WalRecord`, T-23 `EffectJournal`, T-20 `EffectId`, T-21 `EffectDigest`, T-26 `Reserved`
- **Previously registered as:** `C-25`

### Evidence (frozen source)

| Line | Text at that line | What it denotes there |
|---|---|---|
| `Red-on-Rust.md` L1377 | `EffectIssued {` | turn [3] prose record: `{effect_id, capability, effect, target}` |
| `Red-on-Rust.md` L2254 | `\text{EffectIssued}(E.\text{id},\; c,\; E)` | turn [5]: an EVENT-LOG entry carrying the CapRef `c` |
| `Red-on-Rust.md` L23765 | `pub struct EffectIssued {` | turn [30] struct: `{id, actor, effect_digest, logical_time, issue_cost, reservation}` |
| `Red-on-Rust.md` L26229 | `Issued {` | turn [33] `EffectJournalEntry::Issued {id, actor, digest}` |
| `Red-on-Rust.md` L27729 | `EffectIssued { id: EffectId, actor: ActorId, digest: EffectDigest },` | turn [34] `WalRecord::EffectIssued` |
| `Red-on-Rust.md` L35130 | `EffectIssued { id: EffectId, actor: ActorId, digest: EffectDigest },` | turn [47] frozen 15B `WalRecord::EffectIssued` |
| `Red-on-Rust.md` L35140 | `\text{Issued}(E)` | turn [47] lifecycle PREDICATE `Completed(E) ⇒ Issued(E)` |

### The collision

One name carries four denotations across the frozen text: a prose record shape, an event-log entry, a standalone struct, an enum variant (twice, with and without the `Effect` prefix), and a lifecycle predicate. The payloads are not equivalent: the frozen struct carries `effect_digest`, `logical_time`, `issue_cost` and `reservation`; the frozen WAL variant carries only `id`, `actor` and `digest`. The digest field is spelled `effect_digest` in the structs and `digest` in the variants.

### Why it matters

The omitted fields are load-bearing. `reservation` is what makes `BUDGET-ESCROW-CONSERVATION` recoverable: if the durable issued record does not carry the reserved quantity, recovery cannot know how much escrow to hold for an indeterminate effect (N-24 forbids releasing it). `logical_time` is needed to re-establish `DeadlineValid`. The field-name split (`effect_digest` vs `digest`) means a single serialization routine cannot serve both carriers.

### Disposition

Every form is recorded verbatim; no field is renamed and no variant is dropped. The dictionary separates the four roles by TYPE (struct / record kind / lifecycle state / event) and requires prose to name the carrier explicitly — 'the `EffectIssued` struct' vs 'the `WalRecord::EffectIssued` record' vs 'the issued state'. The payload divergence is reported as needing a decision, not reconciled by inventing fields.

### Decision needed

Yes — state whether the durable issued record must carry `reservation`, `logical_time` and `issue_cost`, and fix one spelling for the digest field. Affects R-DUR-02/03, R-BUDGET-04, R-RECOV-02.

## X-08

**The symbol `C` denotes the Consumable vector, the Constraint of `derive`, and a required-capability set**

- **Kind:** `SYMBOL-OVERLOAD` — one mathematical symbol, two or more denotations
- **Severity:** MAJOR
- **Terms affected:** T-25 `Consumable`, T-12 `Constraint`, T-10 `Authority`, T-24 `Budget`

### Evidence (frozen source)

| Line | Text at that line | What it denotes there |
|---|---|---|
| `Red-on-Rust.md` L7130 | `$C = \langle F, I, D \rangle$` | turn [13]: `C` = Consumable balances |
| `Red-on-Rust.md` L6098 | `derive(A,C)\preceq A` | turn [10]: `C` = Constraint, the argument of derive |
| `Red-on-Rust.md` L8717 | `\text{kernel.derive}(c, C_{\text{req}})` | turn [15]: `C_req` = required constraint |
| `Red-on-Rust.md` L1976 | `\Gamma ; \kappa \vdash e \Leftarrow C_{\text{req}}` | turn [4]: `C_req` = the required CAPABILITY set in judgment J3 |
| `Red-on-Rust.md` L8707 | `C' = C - \text{cost}_C(\text{let})` | turn [15]: `C` = Consumable, inside the actor state `A_a` |
| `Red-on-Rust.md` L227 | `C = \langle \tau, \sigma, \eta \rangle` | turn [1]: `C` = a CAPABILITY record (τ, σ, η) — a fourth meaning, neither Consumable nor Constraint |

### The collision

`C` is simultaneously (a) the consumable budget vector, (b) the constraint argument of the derivation operator, and (c) subscripted as `C_req` for two different things — a required constraint (turn [15]) and a required capability set (turn [4] judgment J3). Both (a) and (b) appear in BOXED frozen formulae, and both appear in the README: `derive(A,C) ⪯ A` in the authority section and `C = ⟨F,I,D⟩` in the resource section.

### Why it matters

`derive(A,C) ⪯ A` is the no-amplification theorem (R-CORE-04). Read with `C` = Consumable it is nonsense; read with `C` = Constraint it is the load-bearing security law. Conversely `C' = C − cost_C(let)` is nonsense with `C` = Constraint. An implementer formalizing either formula must guess, and the two guesses live in different modules (MOD-03 capability vs MOD-04 budget).

### Disposition

Both denotations are recorded and NEITHER symbol is renamed — renaming a mathematical symbol would silently alter a frozen formula. The dictionary requires that prose and any mechanization state the namespace: 'the constraint C' vs 'the consumable vector C'. Where a formula is quoted, it is quoted verbatim with its turn provenance so the intended denotation is recoverable from context.

## X-09

**The symbol `R` denotes Reserved resources, the authority resource limit, a capability ceiling, a dynamic budget, a receipt, and the revocation set**

- **Kind:** `SYMBOL-OVERLOAD` — one mathematical symbol, two or more denotations
- **Severity:** MAJOR
- **Terms affected:** T-26 `Reserved`, T-10 `Authority`, T-19 `EffectReceipt`, T-24 `Budget`

### Evidence (frozen source)

| Line | Text at that line | What it denotes there |
|---|---|---|
| `Red-on-Rust.md` L7131 | `$R = \langle M, S \rangle$` | turn [13]: `R` = Reserved capacities |
| `Red-on-Rust.md` L6375 | `$$A_o = \langle S, Q, R, T \rangle$$` | turn [11]: `R` = the per-operation ResourceLimit component of Authority |
| `Red-on-Rust.md` L5778 | `cost(E)\le R_A` | turn [9]: `R_A` = a capability's resource ceiling |
| `Red-on-Rust.md` L6420 | `the capability's ceiling $R_A$. The dynamic execution budget $R_B$` | turn [11] EXPLICITLY distinguishes `R_A` from `R_B` |
| `Red-on-Rust.md` L2021 | `R.\text{id} = E.\text{id}` | turn [5]: `R` = an EffectReceipt |
| `Red-on-Rust.md` L341 | `the global Revocation Set $\mathcal{R}$` | turn [1]: calligraphic `R` = the revocation lineage set |

### The collision

`R` carries at least six denotations, four of them in frozen formulae: the Reserved budget vector, the authority's resource-limit component, a receipt, and (calligraphic) the revocation set. Two further subscripted forms — `R_A` (capability ceiling) and `R_B` (dynamic execution budget) — are distinguished only by a prose note at L6420.

### Why it matters

`ReserveOK(r,R) ⇔ R + r ≤ R_max` (budget) and `cost(E) ≤ R_A` (authority ceiling) are DIFFERENT checks against DIFFERENT objects, and R-BUDGET-03 vs R-CAP-03 own them separately. An implementation that conflates them either lets a capability's ceiling be satisfied by the actor's free memory, or lets the actor's reservation exceed the grant. The receipt reading of `R` additionally collides inside the receipt rule itself (`R.id = E.id`).

### Disposition

All denotations recorded; no symbol renamed. The source's own disambiguation at L6420 is adopted as the dictionary's rule: `R_A` is a capability ceiling (authority), `R_B`/`R` is the actor's reserved budget (resource), `R` in a receipt rule is a receipt, and `ℛ` is the revocation set. Prose MUST name the object, not the letter.

## X-10

**The symbol `S` denotes the Snapshot, the authority Scope component, and concurrency Slots**

- **Kind:** `SYMBOL-OVERLOAD` — one mathematical symbol, two or more denotations
- **Severity:** MAJOR
- **Terms affected:** T-48 `Snapshot`, T-10 `Authority`, T-26 `Reserved`

### Evidence (frozen source)

| Line | Text at that line | What it denotes there |
|---|---|---|
| `Red-on-Rust.md` L26132 | ``- \(S\) = persisted `GlobalState` snapshot,`` | turn [33]: `S` = the Snapshot in `D = ⟨S,L,H⟩` |
| `Red-on-Rust.md` L6375 | `$$A_o = \langle S, Q, R, T \rangle$$` | turn [11]: `S` = the Scope component of an operation authority |
| `Red-on-Rust.md` L7131 | `$R = \langle M, S \rangle$` | turn [13]: `S` = concurrency Slots inside Reserved |
| `Red-on-Rust.md` L26410 | `CommittedSnapshot(S)` | turn [33]: `S` as the predicate's argument — the snapshot reading |
| `Red-on-Rust.md` L6426 | `S_{A'} \preceq_S S_A` | turn [11]: `S` under its own scope order `⪯_S` |

### The collision

`S` is the snapshot (persistence), the scope component of authority (capability algebra), and the concurrency-slot dimension of Reserved (budget) — three frozen denotations in three different modules, two of them inside tuple definitions (`⟨S,L,H⟩` and `⟨M,S⟩`) that both describe durable/bounded state.

### Why it matters

`R = ⟨M,S⟩` and `D = ⟨S,L,H⟩` can appear on the same page of a persistence design: in the first, `S` is slots; in the second, `S` is the snapshot. An implementer deriving a snapshot schema from the tuple forms could carry a slot count where a state image belongs. The scope reading additionally has its own order symbol `⪯_S`, so `S ⪯_S S'` and `S is self-consistent` are unrelated statements sharing notation.

### Disposition

All three recorded; none renamed. Prose MUST qualify: 'the snapshot S', 'the scope component S', 'the slot dimension S'. Struct field names (`slots`, `scope`, `version`/`state_digest`) are the unambiguous layer and are preferred in any implementation-facing text.

## X-12

**The symbol `D` denotes the durable machine state and the duration consumable**

- **Kind:** `SYMBOL-OVERLOAD` — one mathematical symbol, two or more denotations
- **Severity:** MAJOR
- **Terms affected:** T-25 `Consumable`, T-52 `RecoveryFault`, T-27 `Deadline`
- **Previously registered as:** `U-01`

### Evidence (frozen source)

| Line | Text at that line | What it denotes there |
|---|---|---|
| `Red-on-Rust.md` L26127 | `D=\langle S,L,H\rangle` | turn [33]: `D` = the durable machine state |
| `Red-on-Rust.md` L26139 | `Recover(D)=Replay(S,L,H)` | turn [33]: `D` as the recovery function's argument |
| `Red-on-Rust.md` L7130 | `$C = \langle F, I, D \rangle$` | turn [13]: `D` = the duration dimension of Consumable |
| `Red-on-Rust.md` L41544 | `C=\langle F,I,D\rangle` | README/turn [60]: `D` = duration |

### The collision

`D` is the entire durable state in the recovery model (`Recover(D) = State_before_crash`, the qualified theorem of R-CORE-09) and one budget dimension in the resource model. Both are frozen, both appear in boxed formulae, and both belong to requirements about crash safety.

### Why it matters

The recovery theorem `Recover(D) = State_before_crash` and the budget vector `C = ⟨F,I,D⟩` are both cited by crash-recovery obligations. A reader who takes `D` as duration in the recovery theorem reads it as 'recovering the duration budget', and a reader who takes `D` as durable state in the budget vector reads the consumable triple as ⟨fuel, I/O, durable state⟩. U-01 already leaves the operational meaning of duration undefined, so the collision compounds an open decision.

### Disposition

Both recorded; neither renamed. Prose MUST say 'the durable state D' or 'the duration dimension D'. The dictionary notes that `Deadline` (`W`) and duration (`D`) are additionally distinct bounds (N-18), so the letter `D` must never be used for a deadline.

## X-13

**The symbol `L` denotes the durable WAL, the Lifetime authority component, and the transition-tuple log**

- **Kind:** `SYMBOL-OVERLOAD` — one mathematical symbol, two or more denotations
- **Severity:** MAJOR
- **Terms affected:** T-45 `WAL`, T-10 `Authority`, T-49 `EventLog`, T-52 `RecoveryFault`

### Evidence (frozen source)

| Line | Text at that line | What it denotes there |
|---|---|---|
| `Red-on-Rust.md` L26133 | `- \(L\) = append-only durable event log after that snapshot,` | turn [33]: `L` = the WAL / durable log |
| `Red-on-Rust.md` L6501 | `pub struct Authority<S, Q, R, L> {` | turn [11]: `L` = the Lifetime type parameter |
| `Red-on-Rust.md` L6497 | `pub lifetime: L,` | turn [11]: `L` bound to the field `lifetime` |
| `Red-on-Rust.md` L2254 | `\mathcal{L} \oplus \text{EffectIssued}(E.\text{id},\; c,\; E)` | turn [5]: calligraphic `L` = the log appended to by transitions |
| `Red-on-Rust.md` L2290 | `\langle e, \rho, \kappa, \mathcal{H}, B, \mathcal{L} \rangle` | turn [6]: `𝓛` as a machine-configuration component |

### The collision

`L` is the durable log in the recovery model, the lifetime component of authority in the capability algebra (where it is ALSO the symbol that collides with the math's `T`, X-17), and — calligraphic — the append-only log carried in the transition tuples of turns [5]-[6]. The plain and calligraphic forms are not consistently distinguished: turn [33] uses plain `L` for the durable log while turns [5]-[6] use `𝓛` for the transition log.

### Why it matters

Lifetime is a security-relevant authority component (`Valid(c,t)` checks it) and the WAL is the durability mechanism; both appear in crash-recovery reasoning. `Replay(S,L,H)` read with `L` = lifetime is meaningless, and `⟨S,Q,R,L⟩` read with `L` = a log makes the authority order untypeable.

### Disposition

All recorded; none renamed. Prose MUST qualify: 'the durable log L', 'the lifetime component L', 'the transition log 𝓛'. Quotations preserve the source's own calligraphic/plain distinction exactly.

## X-16

**`F` denotes fuel, the effect set, and 'effect invoked'; `M` denotes memory and a replay-tuple component**

- **Kind:** `SYMBOL-OVERLOAD` — one mathematical symbol, two or more denotations
- **Severity:** MAJOR
- **Terms affected:** T-25 `Consumable`, T-26 `Reserved`, T-12 `Constraint`, T-08 `PlanIR`
- **Previously registered as:** `U-22`

### Evidence (frozen source)

| Line | Text at that line | What it denotes there |
|---|---|---|
| `Red-on-Rust.md` L7130 | `$C = \langle F, I, D \rangle$` | turn [13]: `F` = fuel |
| `Red-on-Rust.md` L2217 | `\;!\; \mathcal{F} \;@\; B_{\text{child}}` | turn [4]: calligraphic `F` = the static effect SET |
| `Red-on-Rust.md` L7171 | `(\lambda \bar{x}. e_{body})^{\Phi_f}_{B_f}` | turn [13]: `Φ_f` = a function's effect set |
| `Red-on-Rust.md` L672 | `effect invoked` | turn [2]: the third component of the replay tuple `(B_0,κ_0,F_0,M_0)` is the effect invoked |
| `Red-on-Rust.md` L658 | `(B_0,\kappa_0,F_0,M_0)` | turn [2]: `F_0` = effect invoked, `M_0` = arguments |
| `Red-on-Rust.md` L7131 | `$R = \langle M, S \rangle$` | turn [13]: `M` = memory bytes |

### The collision

`F` is the fuel dimension of Consumable, the (calligraphic or `Φ`-form) static effect set of the judgments, and — in the turn-[2] replay tuple — the effect invoked. `M` is the memory dimension of Reserved and, in the same turn-[2] tuple, the arguments. The turn-[2] tuple's own legend (L668-676) maps its four components to input block / capability identity / effect invoked / arguments, so `B`, `κ`, `F`, `M` all denote something other than their frozen meanings there.

### Why it matters

Fuel and effect sets are the two things the compiler's resource and effect analyses produce, and U-22 records that no pipeline stage is named as producing the effect set `F`. A reader resolving `F` to fuel in that gap report reads it as a missing fuel analysis; the actual gap is effect-set inference. That is a different requirement with a different owner.

### Disposition

All denotations recorded; none renamed. The dictionary requires prose to name the object ('fuel F', 'the effect set 𝓕', 'the function's effect annotation Φ_f') and marks the turn-[2] replay tuple as superseded notation whose component letters do not carry their later meanings.

## X-17

**Authority's fourth component is `T` in the frozen math and `L` in the frozen Rust sketch of the same turn**

- **Kind:** `SYMBOL-OVERLOAD` — one mathematical symbol, two or more denotations
- **Severity:** MAJOR
- **Terms affected:** T-10 `Authority`, T-12 `Constraint`, T-45 `WAL`

### Evidence (frozen source)

| Line | Text at that line | What it denotes there |
|---|---|---|
| `Red-on-Rust.md` L6375 | `$$A_o = \langle S, Q, R, T \rangle$$` | turn [11] math: the fourth component is `T` |
| `Red-on-Rust.md` L6402 | `\langle S \sqcap S_c,\; Q \sqcap Q_c,\; R \sqcap R_c,\; T \sqcap T_c \rangle` | turn [11] `derive_op`: meets over `S,Q,R,T` |
| `Red-on-Rust.md` L6497 | `pub lifetime: L,` | turn [11] Rust: the same component is named `lifetime` with type parameter `L` |
| `Red-on-Rust.md` L6501 | `pub struct Authority<S, Q, R, L> {` | turn [11] Rust: `Authority<S,Q,R,L>` |
| `Red-on-Rust.md` L6505 | `impl<S: Scope, Q: ParamConstraint, R: ResourceLimit, L: Lifetime>` | turn [11]: `L: Lifetime` confirms `L` is the lifetime component |

### The collision

Inside a single turn, the frozen capability algebra writes the per-operation authority as `⟨S,Q,R,T⟩` and the accompanying Rust sketch parameterizes the same object as `Authority<S,Q,R,L>` with `L: Lifetime` and a field named `lifetime`. `T` and `L` denote the same component. `L` independently denotes the durable log (X-13) and `T` independently denotes crash points `T0`-`T6` and the `TEST` obligation prefix.

### Why it matters

The no-amplification theorem is stated over all four components (`T' ⪯_T T` in the proof sketch at L6426). A mechanization that binds `T` to the crash-point namespace, or `L` to the WAL, mis-states R-CORE-04. The Rust generic parameter list is an API surface, so renaming either side is prohibited.

### Disposition

Both symbols recorded as denoting the same component; NEITHER is renamed. The dictionary states the mapping explicitly — math `T` = Rust `L` = the field `lifetime` — and requires any mechanization or implementation to carry both notations with the mapping attached. spec/00 §6 lists the kept math symbols but not this one; the omission is noted rather than back-filled silently.

## X-18

**The machine configuration is written three ways: `Σ` (6 components), an unnamed 7-tuple, and `G`/`A_a` (9 components)**

- **Kind:** `SCOPE-DRIFT` — a name's scope changed between frozen eras without retraction
- **Severity:** MAJOR
- **Terms affected:** T-38 `GlobalState`, T-37 `ActorState`, T-32 `EvalState`, T-25 `Consumable`
- **Previously registered as:** `C-42`, `U-02`

### Evidence (frozen source)

| Line | Text at that line | What it denotes there |
|---|---|---|
| `Red-on-Rust.md` L718 | `$$ \Sigma = \langle P, \rho, \kappa, \mathcal{H}, \phi, \mathcal{E} \rangle $$` | turn [2]: `Σ` = ⟨program, env, caps, heap, fuel, event log⟩ |
| `Red-on-Rust.md` L7161 | `\langle \text{let } x = v \text{ in } e_2, \rho, \kappa, B, t, \mathcal{H}, \mathcal{E} \rangle` | turn [13]: a 7-component configuration ⟨expr, env, caps, BUDGET, time, heap, log⟩ — fuel replaced by a whole `B`, and `t` added |
| `Red-on-Rust.md` L8666 | `$$ A_a = \langle e, \rho, \kappa, \mathcal{H}, C, R, W, \text{mailbox}, \text{status} \rangle $$` | turn [16]: the per-actor state, 9 components, budget split into `C,R,W` |
| `Red-on-Rust.md` L8702 | `Transitions are written as $G \xrightarrow{a, c} G'$` | turn [16]: `G` replaces `Σ` as the global configuration |
| `Red-on-Rust.md` L11061 | `fn step_request(actor: &mut ActorState, machine: &mut GlobalConfig, expr: Expr)` | turn [18]: the Rust name is `GlobalConfig` here and `GlobalState` from turn [31] |

### The collision

The object a transition acts on is written three different ways with three different component sets, and the global/per-actor split moves: turn [2] has one flat `Σ`; turn [13] has a flat 7-tuple with `B` and `t`; turn [16] splits into a global `G` mapping actor ids to 9-component `A_a`s. spec/00 §6 lists `Σ` and `G` as kept symbols without recording that they are different shapes.

### Why it matters

Determinism is stated over machine configurations: `InitialState + SchedulerTrace + HostTrace ⇒ UniqueMachineTrace` (R-CORE-08), and snapshot determinism requires a byte-stable state (R-PERSIST-05). Which components constitute 'the state' decides what a state digest covers. C-15/U-02 already record that no canonical encoding is frozen for machine state; this collision shows the state's SHAPE is not single-valued either.

### Disposition

All three notations recorded verbatim; none renamed. The dictionary adopts the turn-[16]/[31] split (`GlobalState` + `ActorState`) as the current shape because it is the only one with frozen Rust declarations, and marks `Σ` and the 7-tuple as superseded notations retained for traceability. The component-set difference is reported, not papered over.

## X-19

**The budget gate is named `BudgetOK`, `WithinBudget`, `BudgetAvailable`, `ReserveOK`, `ReleaseOK` with six signatures**

- **Kind:** `PREDICATE-SIGNATURE` — one predicate name, several arities/argument orders
- **Severity:** MAJOR
- **Terms affected:** T-24 `Budget`, T-25 `Consumable`, T-26 `Reserved`, T-29 `CostModel`
- **Previously registered as:** `C-07`

### Evidence (frozen source)

| Line | Text at that line | What it denotes there |
|---|---|---|
| `Red-on-Rust.md` L7035 | `BudgetOK(c,\Sigma)` | turn [13]: (command, configuration) |
| `Red-on-Rust.md` L7151 | `**$\text{BudgetOK}$**: Verifies $C - \text{cost}_{\text{consumable}}(c) \ge 0$` | turn [13] gives `BudgetOK`'s content |
| `Red-on-Rust.md` L7334 | `\text{BudgetOK}(\Delta C, \Delta R, C, R)` | turn [13]: (ΔC, ΔR, C, R) — a different arity |
| `Red-on-Rust.md` L1788 | `\operatorname{WithinBudget}(e,B)` | turn [4]: (expression, budget) |
| `Red-on-Rust.md` L6968 | `WithinBudget(B,E)` | turn [12]: (budget, effect) — ARGUMENTS TRANSPOSED vs turn [4] |
| `Red-on-Rust.md` L8820 | `\text{WithinBudget}(E, C, R, R_A)` | turn [16]: (effect, C, R, R_A) |
| `Red-on-Rust.md` L8550 | `WithinBudget(E,B,R_{A_c})` | turn [15]: (effect, B, R_Ac) — a fifth arity |
| `Red-on-Rust.md` L23694 | `\text{BudgetAvailable}(E)` | turn [30]: `BudgetAvailable(E)` in the governing invariant |
| `Red-on-Rust.md` L7525 | `ReserveOK` | turn [15] correction: `ReserveOK(r,R) ⇔ R+r ≤ R_max` |

### The collision

The resource gate has three predicate NAMES (`BudgetOK`, `WithinBudget`, `BudgetAvailable`) plus two operation-specific names (`ReserveOK`, `ReleaseOK`), and at least six different signatures: `(c,Σ)`, `(ΔC,ΔR,C,R)`, `(e,B)`, `(B,E)`, `(E,C,R,R_A)`, `(E,B,R_{A_c})`, `(E)`. Turn [4] and turn [12] transpose the arguments of the same name.

### Why it matters

This is the gate that enforces `BUDGET-CONSUMPTION-CONSERVATION` and `BUDGET-ESCROW-CONSERVATION`, and a conjunct of the central theorem (`BudgetAvailable(E)`). C-07 records that one early form had the reservation direction WRONG; this collision records that the name and arity are not single-valued either, so an implementer cannot tell whether `BudgetAvailable(E)` is the same check as `WithinBudget(E,C,R,R_A)` or a weaker one that ignores the capability ceiling `R_A`.

### Disposition

All names and signatures recorded; none renamed. The dictionary separates the concepts: the CONSUMABLE/RESERVED admissibility check (`ReserveOK`/`ReleaseOK`, frozen by the [15] correction), the DEADLINE check (`t + δ_t ≤ W`, N-18), the CAPABILITY CEILING check (`cost(E) ≤ R_A`, authority-owned), and the composite gate that the central theorem calls `BudgetAvailable(E)`. An explicit decision is required on the composite gate's signature.

### Decision needed

Yes — freeze one name and signature for the composite budget gate and state its relation to `ReserveOK`, `ReleaseOK` and the `R_A` ceiling check. Affects R-BUDGET-03, R-CORE-02.

## X-20

**`HostPolicy` is declared with two incompatible methods: `is_permitted(…) -> bool` and `authorize(…) -> Result<(), HostPolicyError>`**

- **Kind:** `METHOD-SIGNATURE` — one trait name, incompatible method names/returns
- **Severity:** MAJOR
- **Terms affected:** T-41 `HostPolicy`, T-16 `Effect`
- **Previously registered as:** `U-14`, `AMB-08`

### Evidence (frozen source)

| Line | Text at that line | What it denotes there |
|---|---|---|
| `Red-on-Rust.md` L10163 | `pub trait HostPolicy {` | turn [18] declaration |
| `Red-on-Rust.md` L10164 | `fn is_permitted(&self, effect: &Effect) -> bool;` | turn [18] method: infallible bool |
| `Red-on-Rust.md` L21893 | `pub trait HostPolicy {` | turn [29] declaration |
| `Red-on-Rust.md` L21894 | `fn authorize(` | turn [29] method name |
| `Red-on-Rust.md` L21897 | `) -> Result<(), HostPolicyError>;` | turn [29] return type: fallible |
| `Red-on-Rust.md` L8733 | `\text{HostPolicyOK}(E) \quad \text{// Gate 3: Host Policy}` | turn [15]: a third form — the mathematical predicate |

### The collision

One frozen trait name, two incompatible method signatures, plus a mathematical predicate for the same gate. `is_permitted(&Effect) -> bool` cannot distinguish 'policy denies this' from 'the policy could not be evaluated'; `authorize(&Effect) -> Result<(), HostPolicyError>` can, and carries a typed error that the frozen `Fault::HostPolicyDenied(HostPolicyError)` variant requires.

### Why it matters

`Fault::HostPolicyDenied(HostPolicyError)` (L23811) is only constructible from the fallible form. An implementation of the `bool` form must synthesize a `HostPolicyError`, which is undefined anyway (U-14). Because differential testing compares faults (R-REF-05), the two forms produce different observations for the same denial — a divergence with no adjudication target.

### Disposition

Both method names and both return types recorded; neither renamed. The dictionary notes that only the fallible form can satisfy `Fault::HostPolicyDenied(…)` and reports the choice as an open decision, joined to U-14 (error-variant enumeration). `HostPolicyOK(E)` is recorded as the mathematical name of the same gate, not a third API.

### Decision needed

Yes — freeze one `HostPolicy` method signature; blocked by U-14 (`HostPolicyError` variants).

## X-21

**`ActorStatus` is declared twice with incompatible variant payloads**

- **Kind:** `TYPE-HOMONYM` — one name, two or more incompatible type declarations
- **Severity:** MAJOR
- **Terms affected:** T-35 `ActorStatus`, T-36 `RunState`, T-32 `EvalState`, T-26 `Reserved`
- **Previously registered as:** `C-18`, `AMB-05`

### Evidence (frozen source)

| Line | Text at that line | What it denotes there |
|---|---|---|
| `Red-on-Rust.md` L9411 | `pub enum ActorStatus {` | turn [17] declaration |
| `Red-on-Rust.md` L9413 | `Pending(PendingEffect),` | turn [17]: `Pending` is a TUPLE variant carrying a `PendingEffect` |
| `Red-on-Rust.md` L9414 | `Blocked(Continuation),` | turn [17]: `Blocked` CARRIES the continuation |
| `Red-on-Rust.md` L23793 | `pub enum ActorStatus {` | turn [30] declaration |
| `Red-on-Rust.md` L23795 | `Pending {` | turn [30]: `Pending` is a STRUCT variant |
| `Red-on-Rust.md` L23798 | `reservation: Reserved,` | turn [30]: `Pending` carries the RESERVATION |
| `Red-on-Rust.md` L23800 | `Blocked, // For Receive` | turn [30]: `Blocked` is a UNIT variant |
| `Red-on-Rust.md` L23786 | ``the continuation remains safely in `actor.eval.continuation``` | turn [30] states WHERE the continuation lives instead |

### The collision

Two frozen declarations of one enum differ in variant KIND (tuple vs struct vs unit), in payload, and in the location of the continuation. Turn [17] puts the continuation inside `Blocked(Continuation)` and the pending effect inside `PendingEffect {id, effect, continuation}`; turn [30] makes `Blocked` a unit variant, moves the continuation to `actor.eval.continuation`, and puts a `reservation` inside `Pending`.

### Why it matters

The continuation's location determines what a snapshot must encode and what recovery must restore (R-PERSIST-04, R-RECOV-03) — and no canonical encoding is frozen for either (U-02). The `Pending` payload determines whether escrow can be reconstructed after a crash at T2/T3: turn [17]'s `Pending` carries no reservation, so an implementation using it cannot satisfy `BUDGET-ESCROW-CONSERVATION` across recovery. C-18/AMB-05 cover `ActorStatus` vs `RunState`; neither covers this split.

### Disposition

Both declarations recorded verbatim; neither renamed and neither variant dropped. The dictionary marks the turn-[17] form superseded on the strength of the turn-[30] prose that explicitly relocates the continuation, and reports the reservation-payload difference as needing confirmation because it changes what recovery can restore.

### Decision needed

Yes — confirm the frozen `ActorStatus` variant payloads, in particular that `Pending` carries `reservation`.

## X-22

**`PendingEffect.id` vs `ActorStatus::Pending.effect_id`: two spellings of one field, and `continuation` vs `reservation`**

- **Kind:** `FIELD-SET` — same type name, different field sets or field names
- **Severity:** MAJOR
- **Terms affected:** T-35 `ActorStatus`, T-20 `EffectId`, T-32 `EvalState`, T-26 `Reserved`

### Evidence (frozen source)

| Line | Text at that line | What it denotes there |
|---|---|---|
| `Red-on-Rust.md` L9419 | `pub struct PendingEffect {` | turn [17] struct declaration |
| `Red-on-Rust.md` L9420 | `pub id: EffectId,` | turn [17]: the field is `id` |
| `Red-on-Rust.md` L9422 | `pub continuation: Continuation,` | turn [17]: the payload includes the continuation |
| `Red-on-Rust.md` L23796 | `effect_id: EffectId,` | turn [30]: the same value is spelled `effect_id` |
| `Red-on-Rust.md` L23798 | `reservation: Reserved,` | turn [30]: the payload includes the reservation instead |

### The collision

The pending-effect payload exists in two frozen forms whose field NAMES differ (`id` vs `effect_id`) and whose third component differs in kind (`continuation: Continuation` vs `reservation: Reserved`). Elsewhere the frozen records use `id` consistently (`EffectRequest.id`, `EffectIssued.id`, `EffectReceipt.id`, all `WalRecord` variants), so `effect_id` is the odd spelling — and it is the one in the later declaration.

### Why it matters

Field names are protocol fields: they appear in canonical encodings, in counterexample artifacts, and in differential observations of faults. Two spellings for one value means two encodings, and `unmarshal(marshal(v)) = v` (R-MARSHAL-03) cannot hold across them. The payload difference is worse: a snapshot written from the turn-[17] form cannot restore escrow, and one written from the turn-[30] form cannot restore the continuation from the status alone.

### Disposition

Both spellings recorded as frozen protocol fields; NEITHER is renamed. The dictionary requires that any encoding decision name the carrier explicitly and reports the inconsistency as part of X-21's decision. It notes, as evidence only, that `id` is the spelling used by every other frozen effect record.

### Decision needed

Yes — one spelling for the effect id field in the pending payload.

## X-24

**`ActorId` and `EffectId` are declared both as `pub type X = u64` and as `pub struct X(pub u64)`**

- **Kind:** `TYPE-HOMONYM` — one name, two or more incompatible type declarations
- **Severity:** MAJOR
- **Terms affected:** T-20 `EffectId`, T-34 `ActorId`, T-62 `CanonicalEnvelope`, T-18 `EffectIssued`, T-47 `WalRecord`

### Evidence (frozen source)

| Line | Text at that line | What it denotes there |
|---|---|---|
| `Red-on-Rust.md` L9127 | `pub type ActorId = u64;` | turn [17]: ALIAS form |
| `Red-on-Rust.md` L9128 | `pub type EffectId = u64;` | turn [17]: ALIAS form, same code block as `CapRef` |
| `Red-on-Rust.md` L9342 | `pub struct EffectId(pub u64);` | turn [17]: NEWTYPE form, later in the same turn |
| `Red-on-Rust.md` L10669 | `pub struct ActorId(pub u64);` | turn [18]: NEWTYPE form |
| `Red-on-Rust.md` L23735 | `pub struct EffectId(pub u64);` | turn [30]: NEWTYPE form, frozen era |
| `Red-on-Rust.md` L33087 | `## 3. Domain Types (Strict Payload Separation)` | turn [45]: 15A gives each id its own tag |

### The collision

Both identifier types exist in two incompatible forms — a type ALIAS (`pub type X = u64`) and a NEWTYPE (`pub struct X(pub u64)`) — and both forms appear inside turn [17]. An alias makes `ActorId` and `EffectId` the same type as each other and as `u64`; a newtype makes them three distinct nominal types.

### Why it matters

The frozen 15A tag set assigns `ActorId` tag `0x40` and `EffectId` tag `0x41`. A distinct tag per type is only expressible if the types are nominally distinct, so the alias form is inconsistent with the frozen wire format. Beyond encoding, the alias form permits passing an `EffectId` where an `ActorId` is expected — a confusion the effect protocol cannot survive, since `WalRecord::EffectCompleted` carries an id and a digest but no actor, and recovery keys on it.

### Disposition

Both forms recorded; NEITHER renamed. The dictionary reports the alias form as inconsistent with the frozen 15A tag assignment — evidence, not a decision — and leaves the choice to an explicit addendum. `LogicalTime` and the digest newtypes are declared only as newtypes, so the inconsistency is confined to the two id types.

### Decision needed

Yes — confirm the newtype form for `ActorId`/`EffectId` (required by 15A tags `0x40`/`0x41`).

## X-25

**`CapRef` is declared as `CapRef(pub(crate) u64)` and as `CapRef { index: u32, generation: u32 }`**

- **Kind:** `FIELD-SET` — same type name, different field sets or field names
- **Severity:** MAJOR
- **Terms affected:** T-09 `CapRef`, T-10 `Authority`

### Evidence (frozen source)

| Line | Text at that line | What it denotes there |
|---|---|---|
| `Red-on-Rust.md` L915 | `pub struct CapRef(pub(crate) u64);` | turn [3]: single-integer form |
| `Red-on-Rust.md` L3646 | `pub struct CapRef(pub(crate) u64);` | turn [7]: same form |
| `Red-on-Rust.md` L5949 | `pub struct CapRef(pub(crate) u64);` | turn [10]: same form |
| `Red-on-Rust.md` L5966 | `pub struct CapRef {` | turn [10]: generational form appears in the SAME turn |
| `Red-on-Rust.md` L9131 | `pub struct CapRef {` | turn [17]: frozen generational form |
| `Red-on-Rust.md` L9146 | ```CapRef` fields remain private. There should be no public constructor from arbitrary integers.`` | turn [17] states the privacy requirement |

### The collision

`CapRef` has two frozen-era shapes: a single opaque `u64` and a generational `{index: u32, generation: u32}` pair. Both appear in turn [10]; the generational form is the one carried forward and the one 15A encodes under tag `0x30`.

### Why it matters

The generational form is what makes revocation and reuse safe: a stale reference to a recycled slot fails on generation mismatch. A single `u64` cannot express that, so `CAP-REVOCATION-ANCESTOR` and mutation M005 ('accepting revoked capabilities') are not testable against the single-integer form. The privacy requirement at L9145 also differs in force: the single-integer form's field is `pub(crate)`, which is not 'no public constructor from arbitrary integers'.

### Disposition

Both shapes recorded verbatim; neither renamed. The dictionary marks the single-`u64` form superseded (it cannot express generational reuse, which the frozen revocation obligations require) and states that as evidence rather than as an editorial choice. spec/05 §1 gives only the generational form and does not record that the other ever existed.

## X-26

**`Effect` is declared three times with three different field sets**

- **Kind:** `FIELD-SET` — same type name, different field sets or field names
- **Severity:** MAJOR
- **Terms affected:** T-16 `Effect`, T-21 `EffectDigest`, T-22 `EffectCost`, T-09 `CapRef`

### Evidence (frozen source)

| Line | Text at that line | What it denotes there |
|---|---|---|
| `Red-on-Rust.md` L1166 | `pub struct Effect {` | turn [3] declaration |
| `Red-on-Rust.md` L1167 | `pub kind: EffectKind,` | turn [3]: field `kind`, not `op` |
| `Red-on-Rust.md` L1169 | `pub cap_ref: CapRef,` | turn [3]: the effect CARRIES a capability reference |
| `Red-on-Rust.md` L6541 | `pub struct Effect {` | turn [11] declaration |
| `Red-on-Rust.md` L6545 | `pub cost: ResourceUsage, // Static cost of this specific effect` | turn [11]: the cost field's type is `ResourceUsage` |
| `Red-on-Rust.md` L9297 | `pub struct Effect {` | turn [17] declaration — the frozen form |
| `Red-on-Rust.md` L9301 | `pub cost: Cost,` | turn [17]: the cost field's type is `Cost` |

### The collision

Three frozen-era declarations of `Effect` disagree on both fields and field types: `{kind: EffectKind, cap_ref: CapRef, target}` (turn [3]); `{op, target, params, cost: ResourceUsage}` (turn [11]); `{op, target, params, cost: Cost}` (turn [17], carried unchanged into turn [18]). The turn-[3] form has no `op`, no `params`, no `cost`, and DOES have a capability reference.

### Why it matters

`EffectDigest = SHA-256(canonical_bytes(effect))` is the semantic identity used to validate every receipt and every journal record. Which fields are in the hashed bytes decides what the digest commits to. Including `cap_ref` (turn [3]) binds the digest to a `CapRef`, so the same effect requested through a different capability would digest differently and replay would fail; excluding it (frozen) makes the digest a pure function of the effect description. The `ResourceUsage`/`Cost` rename additionally changes the hashed field's type name.

### Disposition

All three field sets recorded verbatim; no field renamed and none silently dropped. The frozen form (L9297) is the current definition; the other two are marked superseded with their exact shapes preserved. The digest-semantics consequence of the `cap_ref` difference is stated explicitly because it is a security property, not a naming preference.

## X-27

**`EffectRequest` is declared three times; the frozen form drops the `cap: CapRef` field**

- **Kind:** `FIELD-SET` — same type name, different field sets or field names
- **Severity:** MAJOR
- **Terms affected:** T-17 `EffectRequest`, T-16 `Effect`, T-09 `CapRef`

### Evidence (frozen source)

| Line | Text at that line | What it denotes there |
|---|---|---|
| `Red-on-Rust.md` L1447 | `pub struct EffectRequest {` | turn [4] declaration |
| `Red-on-Rust.md` L1449 | `pub cap: CapRef,` | turn [4]: `{id, cap}` — NO effect field |
| `Red-on-Rust.md` L9314 | `pub struct EffectRequest {` | turn [17] declaration |
| `Red-on-Rust.md` L9317 | `pub cap: CapRef,` | turn [17]: `{id, effect, cap}` |
| `Red-on-Rust.md` L10325 | `pub cap: CapRef,` | turn [18]: `{id, effect, cap}` |
| `Red-on-Rust.md` L23758 | `pub struct EffectRequest {` | turn [30] declaration — the frozen form |
| `Red-on-Rust.md` L23756 | `// Transient message to the host adapter` | turn [30] states its role |

### The collision

The host-bound message has three frozen-era shapes: `{id, cap}` (turn [4], with no effect at all), `{id, effect, cap}` (turns [17]-[18]), and `{id, effect}` (turn [30], frozen). The `cap: CapRef` field is present in the first two and absent from the frozen form.

### Why it matters

The dropped field is a security decision, not a typo: the frozen form sends the host adapter an effect description and an id, and no capability reference. That is consistent with R-TRUST-03 (no hidden authority; the host is partially trusted) and with `CapRef ⇏ AuthorityInspection` (gate property 2). An implementation built from the turn-[17] shape leaks a `CapRef` across the host boundary, and one built from the turn-[4] shape sends no effect at all. The turn-[4] shape also makes `EffectDigest` uncomputable at the boundary.

### Disposition

All three shapes recorded verbatim; no field renamed. The frozen form is the current definition; the `cap` field is listed as superseded WITH the observation that its removal is what keeps authority off the host boundary, so a future addendum re-adding it would be a security-relevant change requiring explicit justification.

## X-28

**`Block` is declared as `Block(pub Vec<Value>)` and as `Block { forms: Vec<Form> }`**

- **Kind:** `FIELD-SET` — same type name, different field sets or field names
- **Severity:** MAJOR
- **Terms affected:** T-01 `Block`, T-31 `Value`, T-03 `ParsedBlock`

### Evidence (frozen source)

| Line | Text at that line | What it denotes there |
|---|---|---|
| `Red-on-Rust.md` L855 | `pub struct Block(pub Vec<Value>);` | turn [3]: tuple struct over `Value` |
| `Red-on-Rust.md` L13484 | `pub struct Block {` | turn [21] declaration |
| `Red-on-Rust.md` L13485 | `pub forms: Vec<Form>,` | turn [21]: named field over `Form` |

### The collision

The untrusted input type has two declarations with different element types: `Vec<Value>` (turn [3]) and `Vec<Form>` (turn [21]). `Form` is never declared anywhere in the source, and `Value` is itself a colliding name with two incompatible domains (X-45).

### Why it matters

`Block` is the domain of the parser and the subject of `Block ≠ ExecutablePlan` (N-01) and of the first security gate `Block ⇏ ExecutablePlan`. Its element type decides what the parser accepts and therefore what the LLM may emit. `Vec<Value>` means a block is a sequence of machine values (so a block can contain a `Value::Capability`); `Vec<Form>` means a block is a sequence of syntactic forms of an undeclared type. The two give different answers to whether a raw capability can appear in untrusted input.

### Disposition

Both declarations recorded verbatim; neither renamed. `Form` is reported as an undefined type (X-29) rather than being given an invented definition. The dictionary notes the security consequence of the element-type difference and requires an explicit decision.

### Decision needed

Yes — freeze `Block`'s element type (`Value` or `Form`) and declare `Form` if it is retained. Affects R-COMPILE-02 and the first security gate.

## X-29

**Names used as field types, stage names and AST nodes that are never declared**

- **Kind:** `UNDEFINED-TYPE` — a name is used as a type but never declared
- **Severity:** MAJOR
- **Terms affected:** T-07 `NormalizedAST`, T-01 `Block`, T-54 `Observation (planner-facing)`, T-57 `Observation (differential)`, T-03 `ParsedBlock`, T-15 `DelegatedCapability`
- **Previously registered as:** `U-02`

### Evidence (frozen source)

| Line | Text at that line | What it denotes there |
|---|---|---|
| `Red-on-Rust.md` L864 | `pub struct ParsedBlock { ast: NormalizedAST }` | `NormalizedAST`: 2 occurrences, no declaration |
| `Red-on-Rust.md` L39271 | `NormalizedAST` | `NormalizedAST` as a pipeline stage name |
| `Red-on-Rust.md` L13485 | `pub forms: Vec<Form>,` | `Form`: used as `Block`'s element type, no declaration |
| `Red-on-Rust.md` L27160 | `pub events: Vec<GlobalEvent>,` | `GlobalEvent`: no declaration |
| `Red-on-Rust.md` L27162 | `pub available_capabilities: CapabilitySummary,` | `CapabilitySummary`: no declaration |
| `Red-on-Rust.md` L27163 | `pub budget: BudgetSummary,` | `BudgetSummary`: no declaration |
| `Red-on-Rust.md` L36171 | `pub terminal_states: Vec<ObservedActor>,` | `ObservedActor` and the six other `Observed*` types: no declarations |
| `Red-on-Rust.md` L25989 | `Expr::Delegate {` | turn [32]: an AST NODE used in a match sketch and in the delegation proof table, but no `pub enum Expr` (L12145, L14030, L14413, L20295, L20702) declares it |
| `Red-on-Rust.md` L26058 | ``Authority can only cross boundaries via `Expr::Delegate``` | turn [32]: Theorem 2's proof — site added by the X-70 sweep |
| `Red-on-Rust.md` L26078 | ``\| **C: Delegation** \| `Expr::Delegate` \|`` | turn [32]: property-test matrix row C — site added by the X-70 sweep |

### The collision

`NormalizedAST`, `Form`, `GlobalEvent`, `CapabilitySummary`, `BudgetSummary` and the seven `Observed*` element types are all used in frozen declarations and none is declared anywhere in the source. `PlanIR` (X-30) is a seventh: it is used with variants but never declared as an enum. `Expr::Delegate` is an eighth, and the only AST-level case: it is named in the delegation proof table and a match sketch, but none of the five `pub enum Expr` declarations contains it — the same fact AMB-11 registers from the ambiguity side.

### Why it matters

Three of these block obligations directly. `NormalizedAST`/`PlanIR` are the compiler's stage contents (R-COMPILE-02/03). `CapabilitySummary`/`BudgetSummary` define exactly how much machine state the untrusted planner may see — the sanitization boundary of R-PLANNER-01 and of the gated-reflection design — so leaving them undeclared leaves the LLM boundary's information flow unspecified. The `Observed*` types define the differential comparison domain (R-REF-05), so leaving them undeclared leaves the oracle's shape unspecified.

### Disposition

Every undefined name is recorded as a term entry or in this collision with its usage sites, and NONE is given an invented definition — filling a gap by invention is exactly what R-SCOPE-03 prohibits. Each is reported as requiring an explicit declaration. This extends the U-02 family (machine-state encodings) to names that have no declaration at all, which U-02 does not list.

### Decision needed

Yes — declare `NormalizedAST`, `Form`, `GlobalEvent`, `CapabilitySummary`, `BudgetSummary`, and the seven `Observed*` types (or retract the fields that use them).

## X-30

**`PlanIR` is used with variants but never declared, and its variants use two superseded names**

- **Kind:** `UNDEFINED-TYPE` — a name is used as a type but never declared
- **Severity:** MAJOR
- **Terms affected:** T-08 `PlanIR`, T-06 `ExecutablePlan`, T-30 `Expr`
- **Previously registered as:** `C-17`, `U-05`, `AMB-25`

### Evidence (frozen source)

| Line | Text at that line | What it denotes there |
|---|---|---|
| `Red-on-Rust.md` L865 | `pub struct ValidatedPlan { ir: PlanIR, effects: EffectSet }` | turn [3]: `PlanIR` as a field type |
| `Red-on-Rust.md` L986 | `EvaluateSequence { remaining: Vec<PlanIR> },` | turn [3]: `PlanIR` inside a continuation frame |
| `Red-on-Rust.md` L1037 | `PlanIR::Value(v) => StepResult::Halt(v), // Rule 3` | turn [3]: variant `Value` |
| `Red-on-Rust.md` L1039 | `PlanIR::Invoke { func, args, cap } => {` | turn [3]: variant `Invoke` — the superseded surface name (C-17) |
| `Red-on-Rust.md` L1051 | `PlanIR::Spawn { plan, trust_level } => {` | turn [3]: variant `Spawn` with `trust_level` — the retracted isolation field (U-05) |
| `Red-on-Rust.md` L13603 | `PlanIR` | turn [21]: `PlanIR` as a pipeline STAGE |
| `Red-on-Rust.md` L39973 | `ir: PlanIR,` | turn [58]: `PlanIR` as `ExecutablePlan`'s payload type |

### The collision

`PlanIR` is never declared as an enum, yet it is used with at least three variants (`Value`, `Invoke`, `Spawn`) and as the payload type of `ExecutablePlan` in the turn-[58] bootstrap pack. Two of its three visible variants use names the frozen text supersedes: `Invoke` (the frozen constructor is `Expr::Request`, C-17) and `trust_level` (the frozen `Expr::Spawn` has no isolation field, U-05).

### Why it matters

This is the type that X-03 would make the runtime evaluate if the turn-[58] `ExecutablePlan { ir: PlanIR }` declaration were taken as governing. It has no declaration, no closed variant set, and its known variants reference a retracted surface. Building M2 (pure CEK) on it is impossible without inventing its definition, which R-SCOPE-03 prohibits.

### Disposition

All usage sites recorded; the name is not renamed and no variant set is invented. The dictionary reports `PlanIR` as undefined and notes that its only visible variants are superseded forms of `Expr::Value`, `Expr::Request` and `Expr::Spawn`, which is evidence about its intended role but not a definition. Joined to the X-03 decision.

### Decision needed

Yes — declare `PlanIR` or state that `Expr` is the lowered representation. Blocks X-03's resolution.

## X-31

**The durable log has five names, and a sixth name denotes a different in-memory object**

- **Kind:** `SCOPE-DRIFT` — a name's scope changed between frozen eras without retraction
- **Severity:** MAJOR
- **Terms affected:** T-45 `WAL`, T-49 `EventLog`, T-46 `WalFrame`, T-47 `WalRecord`
- **Previously registered as:** `U-16`, `AMB-14`

### Evidence (frozen source)

| Line | Text at that line | What it denotes there |
|---|---|---|
| `Red-on-Rust.md` L27716 | `strict Write-Ahead Log (WAL) ordering` | turn [34]: 'Write-Ahead Log (WAL)' — the definition |
| `Red-on-Rust.md` L27706 | `// 6. Serialize event_log length (actual events are in the WAL)` | turn [34]: the WAL is where the events actually live |
| `Red-on-Rust.md` L26133 | `- \(L\) = append-only durable event log after that snapshot,` | turn [33]: the same object called `L` |
| `Red-on-Rust.md` L28427 | `CommittedSnapshot + DurableLog + EffectJournal` | turn [36]: the same object called `DurableLog` in a boxed theorem |
| `Red-on-Rust.md` L25539 | `pub event_log: EventLog,` | turn [32]: `EventLog` — the IN-MEMORY log, a different object |
| `Red-on-Rust.md` L35099 | `pub struct WalFrame {` | turn [47]: the frozen durable framing type |

### The collision

One durable structure is named `WAL`, `Write-Ahead Log`, `L`, `DurableLog` and 'append-only durable event log' across turns [33]-[58]; and `EventLog` — which sounds like a synonym — is the in-memory log whose LENGTH is snapshotted because its contents are in the WAL. Two of the five names appear inside boxed theorems.

### Why it matters

N-19 (`WAL ≠ EventLog`) is the durability law behind `HostInvoked(E) ⇒ DurableIssued(E)`. If `EventLog` is read as the WAL, an in-memory append satisfies the durability invariant and crash point T2 becomes survivable in a test while being fatal in production. The alias spread is what makes that misreading available: four of the five names are prose, and only `WalFrame`/`WalRecord` are typed.

### Disposition

All five names recorded; none renamed. The dictionary fixes `WAL` as canonical prose for the durable structure, lists `L` and `DurableLog` as frozen symbols that denote it (retained in quotations), and lists `EventLog` as a DISTINCT term (T-49) whose confusion with the WAL is forbidden. U-16/AMB-14 (the `EventSequence`/`WalSequence` relationship) is the related open decision.

## X-32

**`EffectJournal`: a separate durable structure, a superseded enum, and WAL record kinds — and a boxed theorem that counts it as a third component**

- **Kind:** `SCOPE-DRIFT` — a name's scope changed between frozen eras without retraction
- **Severity:** MAJOR
- **Terms affected:** T-23 `EffectJournal`, T-45 `WAL`, T-47 `WalRecord`, T-52 `RecoveryFault`, T-18 `EffectIssued`
- **Previously registered as:** `C-25`

### Evidence (frozen source)

| Line | Text at that line | What it denotes there |
|---|---|---|
| `Red-on-Rust.md` L26134 | `- \(H\) = durable host-effect journal.` | turn [33]: the journal as `H` in `D = ⟨S,L,H⟩` |
| `Red-on-Rust.md` L26216 | `Introduce a durable effect journal separate from the ordinary machine event log:` | turn [33]: 'separate from' — a distinct durable structure |
| `Red-on-Rust.md` L26222 | `pub enum EffectJournalEntry {` | turn [33]: its own enum, unprefixed variants |
| `Red-on-Rust.md` L28427 | `CommittedSnapshot + DurableLog + EffectJournal` | turn [36]: BOXED recovery theorem naming THREE durable components |
| `Red-on-Rust.md` L35127 | `pub enum WalRecord {` | turn [47]: 15B — the journal's records are WAL kinds |
| `Red-on-Rust.md` L35143 | ``A digest mismatch is `EffectJournalCorruption`, not a different effect.`` | turn [47]: the journal name survives as a fault name inside the unified model |

### The collision

The journal's ontological status changes: a separate durable structure with its own enum (turn [33]), a first-class component of a boxed recovery theorem (turn [36]), and — in the frozen 15B model — a family of `WalRecord` kinds with no separate structure (turn [47]). The name survives the unification in `EffectJournalCorruption`, so the frozen text uses 'journal' for something that no longer has its own storage.

### Why it matters

`Recover(D) = Replay(S,L,H)` is stated over three components; 15B gives recovery two durable inputs (snapshot + WAL). R-RECOV-01/03 are written against the three-component form. An implementer must decide whether `H` is a separate file (two logs to order and fsync, and a crash point between them that T0-T6 does not enumerate) or a projection of the WAL (no separate ordering, but then `Replay` takes two arguments). C-25 records the unification as MINOR 'resolved-by-later-text' and does not cite the boxed theorem, which is the site where the three-component reading is normative.

### Disposition

All three statuses recorded verbatim; no name renamed and no structure invented. The dictionary states N-20 (`WAL ≠ EffectJournal` as structures, journal = record taxonomy) as the reading consistent with 15B, and reports that the boxed theorem at L28427/L28577 still counts three components — extending C-25 rather than contradicting it.

### Decision needed

Yes — restate `Recover(D)` against the unified 15B model, or confirm that `H` remains a separate durable structure with its own ordering and crash points.

## X-33

**`Snapshot` denotes a persistence concept, `GlobalSnapshot` a type, and `EnvironmentSnapshot` an unrelated closure capture**

- **Kind:** `TYPE-HOMONYM` — one name, two or more incompatible type declarations
- **Severity:** MAJOR
- **Terms affected:** T-48 `Snapshot`, T-31 `Value`, T-47 `WalRecord`, T-33 `Frame`
- **Previously registered as:** `U-02`

### Evidence (frozen source)

| Line | Text at that line | What it denotes there |
|---|---|---|
| `Red-on-Rust.md` L26132 | ``- \(S\) = persisted `GlobalState` snapshot,`` | turn [33]: the concept, symbol `S` |
| `Red-on-Rust.md` L26301 | `pub struct GlobalSnapshot {` | turn [33]: the frozen persistence type |
| `Red-on-Rust.md` L12357 | `pub env: EnvironmentSnapshot,` | turn [21]: an UNRELATED type — a closure's captured environment |
| `Red-on-Rust.md` L12356 | `pub body: Box<Expr>,` | turn [21]: `FunctionValue { params, body, env }` — the only use of `EnvironmentSnapshot` |
| `Red-on-Rust.md` L35133 | `SnapshotCommit { event_sequence: EventSequence, snapshot_version: SnapshotVersion, state_digest: StateDigest },` | turn [47]: the commit record kind |
| `Red-on-Rust.md` L26410 | `CommittedSnapshot(S)` | turn [33]: the integrity predicate |

### The collision

The word 'Snapshot' names four distinct things: the durable state image concept (`S`), the frozen type `GlobalSnapshot`, the commit record `SnapshotCommit`, and `EnvironmentSnapshot` — a closure-environment capture that has nothing to do with persistence and is declared exactly once, as the type of `FunctionValue.env`, without ever being defined.

### Why it matters

`FunctionValue` must be encoded in snapshots for closures to survive recovery (U-02 lists `FunctionValue` among the types without a canonical encoding), and its `env` field's type is `EnvironmentSnapshot` — a name that reads as a persistence artifact. An implementer could reasonably encode a nested `GlobalSnapshot` there, or search the persistence module for a type that lives in the calculus. The undefined-ness compounds X-29.

### Disposition

All four uses recorded; no name renamed. The dictionary separates them as: `Snapshot` (concept, T-48), `GlobalSnapshot` (frozen type), `SnapshotCommit` (record kind), and `EnvironmentSnapshot` (undefined calculus type, listed in X-29). Prose MUST NOT use 'snapshot' unqualified where the closure capture is meant.

## X-34

**The plan family: `Plan`, `PlanProposal`, `PlanIR`, `ExecutablePlan` overlap — and AMB-25 adds a fifth name that does not exist**

- **Kind:** `SCOPE-DRIFT` — a name's scope changed between frozen eras without retraction
- **Severity:** MAJOR
- **Terms affected:** T-02 `PlanProposal`, T-06 `ExecutablePlan`, T-08 `PlanIR`, T-04 `ValidatedPlan`
- **Previously registered as:** `AMB-25`

### Evidence (frozen source)

| Line | Text at that line | What it denotes there |
|---|---|---|
| `Red-on-Rust.md` L551 | ``### The really interesting primitive: `Plan``` | turn [2]: `Plan` as the fundamental primitive |
| `Red-on-Rust.md` L561 | `Block` | turn [2]: the pipeline that replaced the `Plan` primitive |
| `Red-on-Rust.md` L27175 | `pub struct PlanProposal {` | turn [33]: the planner's output |
| `Red-on-Rust.md` L865 | `pub struct ValidatedPlan { ir: PlanIR, effects: EffectSet }` | turn [3]: `PlanIR` |
| `Red-on-Rust.md` L27122 | `PlanIR` | turn [33]: `PlanIR` still current in the frozen-era architecture diagram |
| `Red-on-Rust.md` L869 | `pub struct ExecutablePlan {` | turn [3]: the machine's input |

### The collision

Five plan-family names are used with overlapping meanings across the transcript: `Plan` (the turn-[2] 'really interesting primitive', later obsolete), `PlanProposal` (planner output), `PlanIR` (an undeclared intermediate, still appearing in a turn-[33] architecture diagram), and `ExecutablePlan` (machine input) — plus `ValidatedPlan`/`CapabilityCheckedPlan`/`ParsedBlock` as stages. AMB-25 records this overlap and adds `PlannerState`, which occurs NOWHERE in `Red-on-Rust.md` (see X-60).

### Why it matters

The overlap is what makes X-01 and X-04 possible: if 'plan' has no fixed denotation, then `ValidatedPlan(P)` cannot be pinned to a stage or to the final artifact, and `PlanIR` can appear as a stage, a field type, and `ExecutablePlan`'s payload (X-03) without contradiction being noticed. `Plan` as a primitive is obsolete but never retracted, so a reader of turn [2] alone gets a different architecture.

### Disposition

All names recorded; none renamed. The dictionary marks `Plan` (turn [2]) obsolete per spec/05 §1 and requires that prose always use the full stage name. AMB-25 is linked and its phantom `PlannerState` reported separately (X-60) rather than silently corrected.

## X-35

**`Expr::Request` is declared with two different field sets**

- **Kind:** `FIELD-SET` — same type name, different field sets or field names
- **Severity:** MAJOR
- **Terms affected:** T-30 `Expr`, T-17 `EffectRequest`, T-16 `Effect`
- **Previously registered as:** `C-17`

### Evidence (frozen source)

| Line | Text at that line | What it denotes there |
|---|---|---|
| `Red-on-Rust.md` L10420 | `Expr::Request { cap, args } => {` | turn [18]: fields `cap`, `args` |
| `Red-on-Rust.md` L12183 | `Request {` | turn [21]: the frozen AST constructor |
| `Red-on-Rust.md` L12184 | `capability: Box<Expr>,` | turn [21]: field `capability`, an EXPRESSION |
| `Red-on-Rust.md` L12185 | `operation: Op,` | turn [21]: field `operation` |
| `Red-on-Rust.md` L12186 | `target: TargetExpr,` | turn [21]: field `target` |
| `Red-on-Rust.md` L12187 | `params: Vec<Expr>,` | turn [21]: field `params` |
| `Red-on-Rust.md` L14039 | `Request { capability: Box<Expr>, operation: Op, target: TargetExpr, params: Vec<Expr> },` | turn [22]: the frozen field set restated |

### The collision

The effect-request constructor has two frozen-era field sets: `{cap, args}` (turn [18]) and `{capability, operation, target, params}` (turns [21]-[22], the frozen AST). The difference is not cosmetic: `cap` in the early form is a bound capability, while `capability: Box<Expr>` in the frozen form is an EXPRESSION that must be evaluated — which is why the 16-step request sequence has separate steps for capability evaluation, target evaluation and argument evaluation.

### Why it matters

The frozen 16-step sequence (R-EFFECT-03) evaluates capability, target and arguments as three separate ordered steps and short-circuits on the first failure (R-EFFECT-04: five assertions per gate). With `{cap, args}` there is no target expression to evaluate and no ordering to test, so `CEK-CALL-ARGS-LTR` and the gate short-circuit obligations cannot be expressed. `args` vs `params` is also a protocol-field rename inside a frozen AST.

### Disposition

Both field sets recorded verbatim; neither renamed. The frozen form (turns [21]-[22], twice) is current; the `{cap, args}` form is marked superseded with its shape preserved. The dictionary notes that `args`/`params` are different spellings of the same role and that `Expr::Call` uses `args` while `Expr::Request` uses `params` in the SAME frozen declaration — so the inconsistency is internal to the frozen AST, not only across eras.

## X-36

**Capability liveness and coverage are named three ways each, with different arguments**

- **Kind:** `PREDICATE-SIGNATURE` — one predicate name, several arities/argument orders
- **Severity:** MAJOR
- **Terms affected:** T-09 `CapRef`, T-10 `Authority`, T-13 `CapabilityKernel`, T-16 `Effect`

### Evidence (frozen source)

| Line | Text at that line | What it denotes there |
|---|---|---|
| `Red-on-Rust.md` L6301 | `Valid(c,t)` | turn [10]: `Valid(c,t)` — reference and time |
| `Red-on-Rust.md` L5934 | `\neg Valid(c)` | turn [9]: `Valid(c)` — one argument |
| `Red-on-Rust.md` L2006 | `$$\frac{\neg\,\text{live}(\kappa(c))}` | turn [5]: `live(κ(c))` — lowercase, takes the AUTHORITY |
| `Red-on-Rust.md` L2254 | `\text{valid}(\kappa(c))` | turn [5]: `valid(κ(c))` — lowercase, takes the AUTHORITY |
| `Red-on-Rust.md` L2254 | `\text{covers}(\kappa(c),\; E.\text{target})` | turn [5]: `covers` takes the authority and the TARGET |
| `Red-on-Rust.md` L4501 | `\operatorname{Covers}(Authority(c),E,t)` | turn [8]: `Covers` takes the authority, the EFFECT and time |
| `Red-on-Rust.md` L3626 | `pub fn covers(&self, effect: &Effect) -> bool {` | turn [7]: the Rust method takes the whole effect |

### The collision

Two kernel decisions each have three names and several arities. Liveness: `Valid(c,t)` / `Valid(c)` / `valid(κ(c))` / `live(κ(c))`. Coverage: `covers(κ(c), E.target)` / `Covers(Authority(c), E, t)` / `fn covers(&self, &Effect) -> bool`. The arguments differ in KIND as well as number: some take the `CapRef`, some the `Authority` behind it, and coverage is checked against the target in one form and the whole effect in another.

### Why it matters

Whether the argument is `c` or `κ(c)` is exactly the N-03 boundary (`CapRef ≠ Authority`): a liveness predicate over `c` can be evaluated by the machine, while one over `κ(c)` requires the kernel to resolve authority first. Whether coverage is checked against `E.target` or against `E` decides whether `params` and `cost` are inside the authorization decision — which changes what `EffectDigest` must commit to and whether a parameter-constraint (`Q`) violation is a coverage failure at all.

### Disposition

All names and signatures recorded; none renamed. The dictionary requires prose to name the predicate with its argument list, and records that the frozen transition rules use `Valid(c,t)` (turn [15] onward) while the algebra uses `valid`/`live`/`covers` over `κ(c)` (turns [5]-[8]). An explicit decision is needed on the coverage argument, since it determines the scope of the `Q` component.

### Decision needed

Yes — freeze one liveness and one coverage predicate signature, and state whether coverage is checked against `E.target` or the whole `E`.

## X-38

**Capability denial carries NINE names across eras (C-08 reports four), host-policy denial two, and two variants have split payload types**

- **Kind:** `TYPE-HOMONYM` — one name, two or more incompatible type declarations
- **Severity:** MAJOR
- **Terms affected:** T-70 `Fault`, T-72 `CapabilityError`, T-41 `HostPolicy`, T-09 `CapRef`, T-10 `Authority`, T-35 `ActorStatus`
- **Previously registered as:** `C-08`, `U-08`, `U-14`, `AMB-08`

### Evidence (frozen source)

| Line | Text at that line | What it denotes there |
|---|---|---|
| `Red-on-Rust.md` L1949 | `**Faults:**` | turn [5]: the v1 fault GRAMMAR — `CapViolation \| BudgetExhausted \| ScopeViolation \| Revoked \| HostFault \| IsolationBreach` |
| `Red-on-Rust.md` L133 | `CapabilityViolation` | turn [1]: 'returns a structured `CapabilityViolation` error *as data*' |
| `Red-on-Rust.md` L937 | `return Err(Fault::CapabilityRevoked(cref));` | turn [3]: `CapabilityRevoked` carrying a `CapRef` |
| `Red-on-Rust.md` L3667 | `CapabilityRevoked` | turn [7]: `CapabilityRevoked` with NO payload |
| `Red-on-Rust.md` L944 | `return Err(Fault::ScopeViolation(cref, target.clone()));` | turn [3]: `ScopeViolation` — no later counterpart |
| `Red-on-Rust.md` L7374 | `AuthorizationFailed` | turn [13]: the v0.3 denial rule (C-08 cites L7435 for this name — X-59) |
| `Red-on-Rust.md` L8721 | `Fault}(\text{CapabilityRevoked` | turn [14]: v0.3 `E-AttenuateDenied` concludes `Fault(CapabilityRevoked)` |
| `Red-on-Rust.md` L8758 | ```CapabilityViolation`, `BudgetExhausted`, or `HostPolicyViolation``` | turn [14]: v0.3 `E-RequestDenied` names the denial faults ONE LINE outside the range AMB-08 cites (L8748-8757) |
| `Red-on-Rust.md` L20389 | `let fault = Fault::CapabilityError(error);` | turn [28]: the variant is named `CapabilityError` here |
| `Red-on-Rust.md` L20790 | `let fault = Fault::CapabilityError(error);` | turn [28]: the same construction, restated |
| `Red-on-Rust.md` L20538 | `Outcome::Fault(Fault::CapabilityError(` | turn [28]: a PROPERTY TEST asserts on the pre-rename variant name |
| `Red-on-Rust.md` L22430 | `Capability(CapabilityError),` | turn [29]: RENAMED to `Capability` — `CapabilityError` never retracted |
| `Red-on-Rust.md` L23808 | `Capability(CapabilityError),` | turn [30]: the frozen form |
| `Red-on-Rust.md` L26870 | `CapabilityDenied,` | turn [33]: a NINTH name, in the actor-local `Fault` declared AFTER the frozen one |
| `Red-on-Rust.md` L10885 | `HostPolicyViolation,` | turn [18]: a SECOND variant name for host-policy denial |
| `Red-on-Rust.md` L10480 | `Fault::HostPolicyViolation` | turn [18]: used where later turns use `HostPolicyDenied` |
| `Red-on-Rust.md` L22436 | `HostPolicyDenied(HostPolicyError),` | turn [29]: host-policy denial with a STRUCTURED payload |
| `Red-on-Rust.md` L23323 | `HostPolicyDenied(String),` | turn [30]: the same variant with an UNSTRUCTURED `String` payload |
| `Red-on-Rust.md` L23813 | `Host(HostFault),` | turn [30]: the frozen `Fault` variant whose payload is `HostFault` (T-74) |
| `Red-on-Rust.md` L21897 | `) -> Result<(), HostPolicyError>;` | turn [29]: the payload's error type — never declared as an enum |

### Evidence (canonicalization layer)

| File:line | Text at that line | Note |
|---|---|---|
| `spec/06-contradictions-ambiguities.md`:21 | `Nine names for the same denial outcome, not four` | C-08's description, corrected in place on this pass; it previously read "Four names for the same denial outcome" and its severity cell was MINOR |
| `spec/09-unresolved-decisions.md`:54 | `denial outcome is named` | U-08 lists four names; the verified count is nine |

### The collision

The capability-denial outcome is named **nine** different ways across the 60 turns: `CapViolation` (v1 grammar L1949), `CapabilityViolation` (L133, L1042, v0.3 L8758), `Revoked` (v1 grammar L1949), `CapabilityRevoked` (L937 *with* a `CapRef` payload, L3667 *without*, v0.3 L8721), `ScopeViolation` (L944, L1949 — no later counterpart), `AuthorizationFailed` (L7374), `Fault::CapabilityError(…)` (L20389, L20790, asserted by a property test at L20538), the frozen `Fault::Capability(CapabilityError)` (L22430 turn [29], L23808 turn [30]), and `CapabilityDenied` (L26870, in the turn-[33] actor-local `Fault` declared *after* the frozen one). The rename `CapabilityError` → `Capability` between turns [28] and [29] is never retracted. The host-policy outcome is named `HostPolicyDenied` and `HostPolicyViolation`, and `HostPolicyDenied` itself carries two payload types across two frozen-era declarations: `HostPolicyError` (L22436 turn [29]; L23811 turn [30]) and `String` (L23323, turn [30]). `Fault` is declared seven times (L10882, L17788, L18125, L22415, L23319, L23806, L26865).

### Why it matters

Faults are part of the normalized observation domain (R-REF-05), so two implementations choosing different declarations produce a differential divergence with no defect on either side. `HostPolicyDenied(String)` vs `HostPolicyDenied(HostPolicyError)` is not a naming difference: a `String` payload cannot be matched exhaustively and has no canonical encoding, while `HostPolicyError` is never declared as an enum at all (U-14). The turn-[28]→[29] rename is load-bearing in a way pure naming is not: L20538 is a property test asserting `Fault::CapabilityError(CapabilityError::Revoked)`, so an implementation that follows the frozen L23808 name fails a test the source itself states. C-08 reports 'four names'; U-08/AMB-08 add `IsolationBreach`, which is the *receipt-mismatch* fault (L2024, L7223, L8766) and not a denial at all. None reports `CapViolation`, `Revoked`, `Fault::CapabilityError`, `CapabilityDenied`, the payload-type split, or the seven declarations.

### Disposition

All nine denial names, both host-policy names, both payload types and all seven declaration sites are recorded verbatim in T-70/T-41/T-72; nothing is renamed and no declaration is deleted. The dictionary raises C-08's count from four to nine, annotates C-08 in place, and requires the U-08 decision to fix names AND payload types AND to state which of the seven declarations governs. C-08's own line citations are wrong (X-59), which is why the spread could not previously be audited from the register. Severity raised MINOR → MAJOR: the L20538 property test asserts a superseded variant name, so this is not cosmetic.

### Decision needed

Yes — U-08 must fix variant names AND payload types, identify which of the seven `Fault` declarations governs, and resolve the L20538 test that asserts the pre-rename `Fault::CapabilityError`.

## X-39

**spec/05 defines `Effect` with a `capability` field that no frozen declaration has**

- **Kind:** `ALIAS-DEFECT` — the canonicalization layer states an alias/definition the source does not support
- **Severity:** MAJOR
- **Terms affected:** T-16 `Effect`, T-21 `EffectDigest`, T-30 `Expr`

### Evidence (frozen source)

| Line | Text at that line | What it denotes there |
|---|---|---|
| `Red-on-Rust.md` L9297 | `pub struct Effect {` | the frozen declaration: `{op, target, params, cost}` — no capability field |
| `Red-on-Rust.md` L1169 | `pub cap_ref: CapRef,` | the only declaration with a capability field is the superseded turn-[3] form |
| `Red-on-Rust.md` L23738 | `pub struct EffectDigest(pub [u8; 32]);` | the digest is over the effect's canonical bytes |

### Evidence (canonicalization layer)

| File:line | Text at that line | Note |
|---|---|---|
| `spec/05-terminology.md`:14 | `{capability, operation, target, params, cost}` | the defective field list, corrected by this dictionary |

### The collision

The glossary of record gives `Effect` as `{capability, operation, target, params, cost}`. No declaration in 42,312 lines has that field set. The frozen form (L9297, repeated at L10309 and L10792) is `{op, target, params, cost}`; the only form with a capability field is the superseded turn-[3] `{kind, cap_ref, target}`, which has neither `operation` nor `params`. The glossary row is a hybrid of a superseded shape and the frozen one, and it also renames `op` to `operation`.

### Why it matters

`EffectDigest = SHA-256(canonical_bytes(effect))` and every receipt, journal record and replay comparison keys on it. A glossary that puts `capability` inside `Effect` tells an implementer to hash a `CapRef` into the digest — so the same effect requested through a different capability would produce a different digest, replay would fail on a valid trace, and `EFFECT-RECEIPT-DIGEST-VALIDATION` would be unsatisfiable. Renaming `op` to `operation` additionally collides with `Expr::Request.operation`, which is a DIFFERENT field of a different type.

### Disposition

The glossary row is corrected in this pass to the frozen field set, with the correction recorded here rather than applied silently: `Effect = {op, target, params, cost}` (L9297), and `operation` is `Expr::Request.operation`, not an `Effect` field. No source identifier is renamed — the frozen field names are restored to the glossary.

## X-40

**spec/05 and mod/02 treat `ValidatedPlan`, `CapabilityCheckedPlan` and `PlanIR` as aliases of `ExecutablePlan`**

- **Kind:** `ALIAS-DEFECT` — the canonicalization layer states an alias/definition the source does not support
- **Severity:** MAJOR
- **Terms affected:** T-04 `ValidatedPlan`, T-05 `CapabilityCheckedPlan`, T-06 `ExecutablePlan`, T-08 `PlanIR`, T-07 `NormalizedAST`

### Evidence (frozen source)

| Line | Text at that line | What it denotes there |
|---|---|---|
| `Red-on-Rust.md` L865 | `pub struct ValidatedPlan { ir: PlanIR, effects: EffectSet }` | a declared stage TYPE with its own fields |
| `Red-on-Rust.md` L866 | `pub struct CapabilityCheckedPlan { ir: PlanIR, required_caps: CapSet }` | a declared stage TYPE with its own fields |
| `Red-on-Rust.md` L869 | `pub struct ExecutablePlan {` | the final artifact — different fields again |

### Evidence (canonicalization layer)

| File:line | Text at that line | Note |
|---|---|---|
| `spec/05-terminology.md`:13 | `are **stage names**` | the alias resolution that conflates three declared stage types with the final artifact |
| `mod/02-compiler.md`:52 | `not artifacts in their own right` | the same claim propagated into the module layer |

### The collision

The glossary lists `ValidatedPlan`, `CapabilityCheckedPlan` and `PlanIR` in the 'Aliases observed in source' column for `ExecutablePlan` and resolves them as 'stage names'. mod/02 repeats the claim more strongly: stage names are 'not artifacts in their own right'. But two of the three ARE declared artifacts with their own fields, private to `mod compiler`, and `ValidatedPlan` is additionally a predicate in the central theorem (X-01). Calling them aliases of the final artifact states that they denote the same object, which is false on the source's own declarations.

### Why it matters

This is the alias-rule form of the conflation N-01/N-02/N-11/N-12 exist to prevent. An implementer following the glossary would treat a `ValidatedPlan` as an `ExecutablePlan` and admit an artifact that has passed effect annotation only — skipping capability analysis (`κ_req ⪯ κ_ambient`) and resource bounding (`bounds: ResourceBounds`) — into the machine. That defeats `Block ≠ ExecutablePlan` from the inside, with the glossary as authority.

### Disposition

The alias column is corrected: `ValidatedPlan` (T-04) and `CapabilityCheckedPlan` (T-05) are distinct TERMS with their own entries, not aliases; `PlanIR` (T-08) is an undeclared IR name, not an alias; `NormalizedAST` (T-07) likewise. The only genuine obsolete alias recorded is `Plan` (turn [2]). No identifier is renamed. mod/02's NON-NORMATIVE-CONTENT bullet is corrected to point at this finding.

## X-45

**Two incompatible `Value` domains share one name**

- **Kind:** `TYPE-HOMONYM` — one name, two or more incompatible type declarations
- **Severity:** MAJOR
- **Terms affected:** T-31 `Value`, T-39 `Mailbox`, T-62 `CanonicalEnvelope`, T-48 `Snapshot`
- **Previously registered as:** `C-03`, `C-45`, `U-09`, `AMB-21`
- **Provenance:** extends or corrects an existing register entry; not a new finding.

### Evidence (frozen source)

| Line | Text at that line | What it denotes there |
|---|---|---|
| `Red-on-Rust.md` L12283 | `pub enum Value {` | turn [21]: the MACHINE domain (11 variants) |
| `Red-on-Rust.md` L13969 | `pub enum Value {` | turn [22]: re-declared |
| `Red-on-Rust.md` L33164 | `pub enum Value {` | turn [45]: the 15A CANONICAL domain (8 variants, including `Map`) |
| `Red-on-Rust.md` L33167 | `List(Vec<Value>), Map(BTreeMap<Symbol, Value>),` | turn [45]: `Map` is not a machine variant |

### The collision

The machine `Value` (11 variants including `Bytes`, `Tuple`, `Function`, `Actor`) and the 15A canonical `Value` (8 variants including `Map`) share a name with incompatible variant sets. `marshal`/`unmarshal` and the round-trip law `unmarshal(marshal(v)) = v` are stated for 'all pure values' without saying which domain.

### Why it matters

This is the largest open naming decision in the specification and it blocks R-MARSHAL-03: a round-trip law cannot hold across two domains whose variant sets differ in both directions. It also decides what a snapshot can encode, since `Value::Function` and `Value::Actor` are machine-only and `Value::Map` is canonical-only.

### Disposition

Recorded as-is; NEITHER domain renamed, because U-09 is the open decision that must choose (spec/05 §7 and req/03 AMB-21 both defer to it). This entry restates the collision so the dictionary is complete and links the upstream registers rather than duplicating their analysis.

### Decision needed

Yes — U-09: name and relate the two value domains.

## X-47

**`EventSequence` and `WalSequence` are separate newtypes with no stated relationship**

- **Kind:** `TYPE-HOMONYM` — one name, two or more incompatible type declarations
- **Severity:** MAJOR
- **Terms affected:** T-49 `EventLog`, T-45 `WAL`, T-46 `WalFrame`, T-47 `WalRecord`
- **Previously registered as:** `U-16`, `AMB-14`
- **Provenance:** extends or corrects an existing register entry; not a new finding.

### Evidence (frozen source)

| Line | Text at that line | What it denotes there |
|---|---|---|
| `Red-on-Rust.md` L31697 | `pub struct EventSequence(pub u64);` | turn [43]: the in-memory event sequence |
| `Red-on-Rust.md` L33868 | `pub struct WalSequence(pub u64);` | turn [46]: the durable WAL sequence |
| `Red-on-Rust.md` L35119 | `pub struct WalSequence(pub u64);` | turn [47]: restated, 'strictly monotonic' |
| `Red-on-Rust.md` L35133 | `SnapshotCommit { event_sequence: EventSequence, snapshot_version: SnapshotVersion, state_digest: StateDigest },` | turn [47]: a WAL record that carries an `EventSequence`, not a `WalSequence` |

### The collision

Two `u64` newtypes sequence the in-memory event log and the durable WAL, and the frozen `WalRecord::SnapshotCommit` carries an `EventSequence` INSIDE a record that has its own `WalSequence` in its frame. Whether one is a projection of the other, or they advance independently, is never stated.

### Why it matters

The WAL gap check `s_{n+1} = s_n + 1` is a conformance obligation (WAL-SEQUENCE-CONTINUITY, WAL-GAP-REJECT). If effect records and event records consume the same sequence, a single total order satisfies it; if they do not, the gap check must be applied per kind and `SnapshotCommit`'s embedded `EventSequence` needs its own continuity rule. Recovery ordering (R-RECOV-03) depends on the answer.

### Disposition

Both types recorded; neither renamed nor merged. U-16/AMB-14 is the open decision; this entry adds the concrete evidence that a WAL record embeds an `EventSequence`, which constrains the answer (a single total order is the reading consistent with the frozen gap-check rule).

### Decision needed

Yes — U-16.

## X-52

**'FROZEN' is applied to four different objects, and the README applies it to a fifth**

- **Kind:** `SCOPE-DRIFT` — a name's scope changed between frozen eras without retraction
- **Severity:** MAJOR
- **Terms affected:** T-69 `Frozen`, T-64 `Specification`, T-66 `Verification`, T-67 `Proof`, T-68 `EvidenceStatus`, T-65 `Implementation`

### Evidence (frozen source)

| Line | Text at that line | What it denotes there |
|---|---|---|
| `Red-on-Rust.md` L38935 | `ARCHITECTURE: FROZEN` | turn [54]: the architecture |
| `Red-on-Rust.md` L38936 | `SPECIFICATION: FROZEN` | turn [54]: the specification text |
| `Red-on-Rust.md` L38937 | `REFERENCE CONTRACT: FROZEN` | turn [54]: the reference-model contract |
| `Red-on-Rust.md` L38938 | `VERIFICATION CONTRACT: FROZEN` | turn [54]: the verification CONTRACT |
| `Red-on-Rust.md` L41305 | `Verification:       FROZEN` | turn [58]: 'Verification' without 'CONTRACT' |

### Evidence (canonicalization layer)

| File:line | Text at that line | Note |
|---|---|---|
| `README.md`:12 | `Verification:       FROZEN` | the README's contract-less form |

### The collision

The frozen status block applies `FROZEN` to four distinct objects — architecture, specification, reference contract, verification contract. The turn-[58] and README blocks drop the word 'CONTRACT' and say `Verification: FROZEN`, which reads as a claim that verification has been frozen (i.e. completed and fixed) rather than that the contract governing it has. spec/05 §6.10 states the correct reading as a normalization rule.

### Why it matters

This is the N-31 law (`Frozen ≠ Verified`) and it is the repository's central claim-discipline risk: at this commit no verification has been performed at all, so `Verification: FROZEN` read as 'verified and fixed' would be a false conformance claim, which R-CLAIM-01 prohibits. The same word carries the 'requirements are stable' meaning in all five sites and the 'evidence is complete' meaning in none of them.

### Disposition

All five status lines recorded verbatim; none rewritten. The dictionary makes `Frozen` (T-69) a term with the single meaning 'requirements are stable', forbids 'verified'/'final'/'complete'/'correct' as substitutes, and requires that any quotation of a status block preserve the word 'CONTRACT' where the source has it and gloss it where the source omits it. spec/05 §6.9-6.10 is linked as the existing rule.

## X-55

**Turn [41]'s '(Frozen)' `Value` discriminant table lists 5 of 8 variants and contradicts turns [43]/[45] on `Capability`**

- **Kind:** `FIELD-SET` — same type name, different field sets or field names
- **Severity:** MAJOR
- **Terms affected:** T-62 `CanonicalEnvelope`, T-63 `CanonicalPayload`, T-31 `Value`, T-13 `CapabilityKernel`
- **Previously registered as:** `C-02`

### Evidence (frozen source)

| Line | Text at that line | What it denotes there |
|---|---|---|
| `Red-on-Rust.md` L29927 | `### 3. Value Variant Discriminants (Frozen)` | turn [41]: the table is titled Frozen |
| `Red-on-Rust.md` L29934 | ``\| `Capability(c)` \| `0x0A` \| Complete `CapRef` envelope \|`` | turn [41]: `Capability` = 0x0A |
| `Red-on-Rust.md` L29965 | `pub const DISC_CAPABILITY: u8 = 0x0A;` | turn [41]: the const agrees with its own table |
| `Red-on-Rust.md` L32369 | `const TAG_CAPABILITY: u8 = 0x05;` | turn [43]: `Capability` = 0x05 |
| `Red-on-Rust.md` L33172 | `const TAG_STRING: u8 = 0x03; const TAG_SYMBOL: u8 = 0x04; const TAG_CAPABILITY: u8 = 0x05;` | turn [45]: `Capability` = 0x05, and `Symbol`/`List`/`Map` now exist |
| `Red-on-Rust.md` L29527 | ``Your implementation itself produces `0x09`; the test currently expects `0x0A`, so the test would fail.`` | turn [40]: the 0x0A expectation is acknowledged as a failing test, one turn before it is frozen |

### The collision

The turn-[41] discriminant table is headed '(Frozen)' but enumerates only `Unit`, `Bool`, `Integer`, `String` and `Capability` — `Symbol`, `List` and `Map` have no discriminant at all, so three of the eight frozen `Value` variants are unencodable under it. It also assigns `Capability` the byte 0x0A, while turns [43] and [45] assign 0x05 in a dense 0x00-0x07 range. Turn [40], one turn earlier, records that an implementation produced 0x09 where a test expected 0x0A and that the test 'would fail' — so 0x0A entered the frozen table from a known-broken expectation.

### Why it matters

A capability carried inside a `Value` is the object `Expr::Request.capability` resolves to, and `Value::Capability(CapRef)` is one of the two variants whose payload is a nested envelope. Its discriminant therefore participates in every `EffectDigest` for a capability-bearing request and in `StateDigest` for any snapshot holding a `CapRef`. Two frozen tables disagreeing on that byte means two conforming encoders produce different digests for the same state, which breaks R-PERSIST-05 determinism and makes 15C.34 differential persistence testing undecidable. The incompleteness is worse than the contradiction: an implementer following the '(Frozen)' table literally cannot encode `Value::List` at all.

### Disposition

Both tables recorded verbatim; neither rewritten and no discriminant renamed. Under latest-frozen-text the dense turn-[45] set 0x00-0x07 governs, which is also the resolution req/03 §2 already records for C-02 ('`Value` envelope discriminants `0x00`–`0x07`'). This entry adds what C-02 does not cover: that the superseded table is itself labeled Frozen, that it is INCOMPLETE rather than merely different, and that the specific conflicting variant is `Capability`.

## X-57

**`Request` denotes an `Expr` variant, a redex form, a theorem predicate, an implementation phase and a struct stem**

- **Kind:** `SYMBOL-OVERLOAD` — one mathematical symbol, two or more denotations
- **Severity:** MAJOR
- **Terms affected:** T-14 `CapabilityContext`, T-17 `EffectRequest`, T-32 `EvalState`, T-18 `EffectIssued`, T-45 `WAL`
- **Previously registered as:** `AMB-13`, `C-01`

### Evidence (frozen source)

| Line | Text at that line | What it denotes there |
|---|---|---|
| `Red-on-Rust.md` L12183 | `Request {` | turn [21]: the `Expr::Request` AST variant |
| `Red-on-Rust.md` L14039 | `Request { capability: Box<Expr>, operation: Op, target: TargetExpr, params: Vec<Expr> },` | turn [22]: variant, field set A |
| `Red-on-Rust.md` L14422 | `Request { capability: Box<Expr>, operation: Op, target: Box<Expr>, params: Vec<Expr> },` | turn [22]: variant, field set B (`target: Box<Expr>` not `TargetExpr`) |
| `Red-on-Rust.md` L7374 | `\langle K[\textbf{request}(E, \text{cap}(c))],` | turn [13]: `request(E, cap(c))`, a lowercase REDEX FORM in an evaluation context |
| `Red-on-Rust.md` L7255 | `$$ \boxed{ \neg \text{Authorized}(A, E, t) \;\Rightarrow\; \neg \text{Request}(E) } $$` | turn [13]: `Request(E)`, a PREDICATE over effects in the central theorem |
| `Red-on-Rust.md` L15927 | `\text{Request}` | turn [23]: `Request` as a rung of the implementation-phase ladder Let/Seq/If → Lambda/Call → Attenuate → Request → Actors → Host |
| `Red-on-Rust.md` L20270 | `\text{Phase 12: Request}` | turn [27]: `Request` as a PHASE NAME |
| `Red-on-Rust.md` L1447 | `pub struct EffectRequest {` | turn [3]: the struct whose stem is `Request` |
| `Red-on-Rust.md` L11061 | `fn step_request(actor: &mut ActorState, machine: &mut GlobalConfig, expr: Expr)` | turn [18]: the transition function |
| `Red-on-Rust.md` L35129 | `EffectPrepared { id: EffectId, actor: ActorId, digest: EffectDigest },` | turn [47]: the durable lifecycle has NO `Request` record — the in-memory `EffectRequest` corresponds to `EffectPrepared` |

### The collision

One stem carries five roles: `Expr::Request` is a term constructor (declared with two different field sets, X-35); `request(E, cap(c))` is a lowercase redex form in the operational rules; `Request(E)` is a predicate in the boxed central theorem; `Request`/`Phase 12: Request` is an implementation-phase name; and `EffectRequest` / `step_request` are a struct and a function built on the stem. The durable WAL lifecycle then has no `Request` record at all — its first stage is `EffectPrepared` — so the in-memory and durable vocabularies do not line up on this stem.

### Why it matters

R-CORE-03 is stated as `¬Authorized(A,E,t) ⇒ ¬Request(E)` and glossed 'equivalently `¬Authorized ⇒ ¬Request` at the operational level' (spec/01 L27). That equivalence holds only if the PREDICATE `Request(E)` and the operational form `Expr::Request` denote the same event, and neither is the durable `EffectPrepared`. An implementer who instruments the wrong one — e.g. counts `WalRecord::EffectPrepared` rows as `Request(E)` — gets a theorem that is unfalsifiable, because the WAL can contain a `Prepared` record for a request the evaluator rejected before issuing. This is the `EffectRequest ≠ EffectIssued` distinction (N-16) at the naming level.

### Disposition

All five roles recorded; no identifier renamed — `Expr::Request`, `EffectRequest`, `step_request`, `request(·,·)` and `Request(·)` are all frozen. The dictionary gives each its own TERM (`Request` the predicate, T-14; `Expr::Request` the variant, T-32; `EffectRequest` the struct, T-17) and states the bridge explicitly: `Request(E)` is true exactly when the evaluator reaches an `Expr::Request` redex whose checks pass, which produces an `EffectRequest`, which is durable as `WalRecord::EffectPrepared`. Phase names are marked as PROSE, never as types.

## X-58

**`Fault` is declared seven times and `HostPolicyDenied` carries two different payload types**

- **Kind:** `TYPE-HOMONYM` — one name, two or more incompatible type declarations
- **Severity:** MAJOR
- **Terms affected:** T-70 `Fault`, T-71 `GlobalFault`, T-74 `HostFault`, T-41 `HostPolicy`, T-35 `ActorStatus`, T-36 `RunState`, T-52 `RecoveryFault`
- **Previously registered as:** `AMB-08`, `C-08`, `U-08`

### Evidence (frozen source)

| Line | Text at that line | What it denotes there |
|---|---|---|
| `Red-on-Rust.md` L10882 | `pub enum Fault {` | turn [18]: declaration 1 — has `HostPolicyViolation`, no payload |
| `Red-on-Rust.md` L17788 | `pub enum Fault {` | turn [25]: declaration 2 |
| `Red-on-Rust.md` L18125 | `pub enum Fault {` | turn [26]: declaration 3 |
| `Red-on-Rust.md` L22415 | `pub enum Fault {` | turn [29]: declaration 4 |
| `Red-on-Rust.md` L22436 | `HostPolicyDenied(HostPolicyError),` | turn [29]: payload is the STRUCTURED `HostPolicyError` |
| `Red-on-Rust.md` L23319 | `pub enum Fault {` | turn [30]: declaration 5 |
| `Red-on-Rust.md` L23323 | `HostPolicyDenied(String),` | turn [30]: payload is an UNSTRUCTURED `String` |
| `Red-on-Rust.md` L23806 | `pub enum Fault {` | turn [30]: declaration 6 |
| `Red-on-Rust.md` L23811 | `HostPolicyDenied(HostPolicyError),` | turn [30]: back to `HostPolicyError` |
| `Red-on-Rust.md` L26865 | `pub enum Fault {` | turn [33]: declaration 7 |
| `Red-on-Rust.md` L10885 | `HostPolicyViolation,` | turn [18]: a SECOND variant name for host-policy denial |
| `Red-on-Rust.md` L10480 | `actor.status = ActorStatus::Fault(Fault::HostPolicyViolation);` | turn [18]: `HostPolicyViolation` used where later turns use `HostPolicyDenied` |
| `Red-on-Rust.md` L21897 | `) -> Result<(), HostPolicyError>;` | turn [29]: the error type the structured payload carries |

### The collision

`pub enum Fault` is declared seven times across turns [18]-[33], and the host-policy denial variant appears under two names (`HostPolicyViolation`, payload-less, turn [18]; `HostPolicyDenied`, turn [29] onward) and, under the later name, with two payload types: `HostPolicyError` (L22436, L23811) and `String` (L23323). AMB-08 records the `HostPolicyDenied`/`HostPolicyViolation` naming split; the PAYLOAD split and the seven-fold redeclaration are not recorded anywhere.

### Why it matters

`Fault` is what an actor's `ActorStatus::Fault(·)` carries, what `MachineEvent::Fault(·)` reports (L23499), what a WAL event records, and what 15C.43 deliberate fault-injection validation asserts on. A `String` payload makes the denial reason unmatchable — an implementation cannot branch on WHICH host policy refused, so the fault-precedence rule 'CapabilityViolation > BudgetExhausted > HostPolicyViolation' (L8971) is not testable, and `FAULT-CLASSIFICATION-EXHAUSTIVE` cannot be discharged. It also breaks replay determinism: a host-supplied `String` is non-deterministic content inside a record that R-PERSIST-05 requires be reproducible byte-for-byte.

### Disposition

All seven declarations and both payload types recorded verbatim; nothing renamed and no declaration deleted. Under latest-frozen-text the structured `HostPolicyDenied(HostPolicyError)` governs (turn [33]'s declaration is the last), but this entry flags that the choice is load-bearing for replay determinism and needs explicit confirmation rather than silence. AMB-08 is linked and extended.

## X-59

**C-08's provenance for the `Fault` taxonomy is wrong in three of its four citations and its fourth mis-describes the text it points at; U-08, spec/05 and REQ-CALC-013 repeat the error**

- **Kind:** `PROVENANCE-DEFECT` — a citation in the canonicalization layer does not point at the text it claims
- **Severity:** MAJOR
- **Terms affected:** T-70 `Fault`, T-72 `CapabilityError`, T-74 `HostFault`, T-41 `HostPolicy`, T-09 `CapRef`, T-10 `Authority`
- **Previously registered as:** `C-08`, `U-08`, `U-14`, `AMB-08`, `C-53`

### Evidence (frozen source)

| Line | Text at that line | What it denotes there |
|---|---|---|
| `Red-on-Rust.md` L1995 | `$$\frac{}{\langle \text{if true } e_2` | what C-08's 1st citation actually points at: the `if true` cost rule (turn [5]), not a fault |
| `Red-on-Rust.md` L7435 | `\boxed{ \text{ExternalEffect}(E)` | what C-08's 3rd citation actually points at: the boxed `ExternalEffect` theorem (turn [13]) |
| `Red-on-Rust.md` L7374 | `\text{AuthorizationFailed}` | the real site of C-08's 3rd name — 61 lines BEFORE the line C-08 cites |
| `Red-on-Rust.md` L1042 | `return StepResult::Fault(Fault::CapabilityViolation(e));` | the real site of C-08's 1st name (turn [3]) |
| `Red-on-Rust.md` L937 | `return Err(Fault::CapabilityRevoked(cref));` | the real site of C-08's 2nd name (turn [3]) |
| `Red-on-Rust.md` L23784 | `## 2. Actor Status and Fault Taxonomy` | C-08's 4th citation: a section HEADING — the start of R-CALC-06's own cited range L23784-23819 |
| `Red-on-Rust.md` L23806 | `pub enum Fault {` | the frozen declaration that range contains, 22 lines below the heading |
| `Red-on-Rust.md` L23807 | `// ... (previous faults)` | elision marker: the frozen block does NOT restate earlier variants |
| `Red-on-Rust.md` L23808 | `Capability(CapabilityError),` | the frozen variant — so it DOES exist, contra C-08's `with variants undefined` |
| `Red-on-Rust.md` L20408 | `pub enum CapabilityError {` | the inner error enum IS declared (turn [28]) — contra U-08 and spec/05 L112 |
| `Red-on-Rust.md` L10820 | `pub enum HostFault {` | and so is `HostFault` (turn [18]) — contra U-08 and spec/05 L112 |

### Evidence (canonicalization layer)

| File:line | Text at that line | Note |
|---|---|---|
| `spec/06-contradictions-ambiguities.md`:21 | `fault(CapabilityViolation)` | C-08's 1st (wrong) citation, kept verbatim above the correction |
| `spec/06-contradictions-ambiguities.md`:21 | `with variants undefined` | C-08's false gloss on its 4th citation |
| `spec/09-unresolved-decisions.md`:54 | `denial outcome is named` | U-08 — four names listed, nine verified (X-38) |
| `spec/05-terminology.md`:112 | `Enum variants not enumerated` | the same claim under U-14 |
| `req/01-registry-part2-semantics.md`:186 | `inner variants not enumerated` | REQ-CALC-013's INVARIANTS — false on both halves |

### The collision

C-08 (spec/06 L21) cites four lines for the capability-denial naming spread. Read at those exact lines: **L1995** is the `if true` cost rule, **L7363** is a blank line, **L7435** is the boxed `ExternalEffect` theorem. None contains a fault, and the three lowercase forms C-08 quotes — `fault(CapabilityViolation)`, `fault(CapabilityRevoked)`, `fault(AuthorizationFailed)` — occur nowhere in L1-42312. The real sites are `Fault::CapabilityViolation(e)` L1042, `Fault::CapabilityRevoked(cref)` L937, and `AuthorizationFailed` L7374, 61 lines before the cited L7435. The **fourth** citation is the opposite kind of error: L23784 is the heading '## 2. Actor Status and Fault Taxonomy', the start of the range mod/01 L155 and spec/03 L52 already cite for R-CALC-06 (L23784-23819), and that range does contain the frozen `pub enum Fault` at L23806 with `Capability(CapabilityError)` at L23808. So the citation is right and the gloss is wrong twice over: 'with variants undefined' is false (L23807-23815 name eight variants), and the path form C-08 writes, `Fault::Capability(CapabilityError)`, is a rendering of a variant the source writes as `Capability(CapabilityError),` inside the enum. The error then propagates. **U-08** (spec/09 L54) claims the inner `CapabilityError` / `HostPolicyError` / `EffectError` / `HostFault` variants 'are not enumerated' — but `pub enum CapabilityError` is declared at L20408 and `pub enum HostFault` at L10820; only `HostPolicyError` and `EffectError` genuinely lack a declaration. **spec/05 L112** makes the same claim for the same four names under U-14. **REQ-CALC-013** (req/01-part2 L186) states the taxonomy is a 'closed set; inner variants not enumerated in the source' — false on both halves, since L23807 carries an explicit `// ... (previous faults)` elision (so the set is NOT closed) and two of the four inner enums ARE declared.

### Why it matters

The register is the layer an implementer trusts instead of re-reading 42,312 lines. Three wrong line numbers send them to unrelated text; the false 'variants undefined' gloss makes them re-litigate two enums that are already declared and, worse, treat the frozen `Fault` set as closed when the source explicitly elides part of it. `Fault` identity is compared by the differential observer (R-REF-05), so an incorrect variant set is a correctness defect, not a documentation nit.

### Disposition

PROVENANCE-CORRECTED; nothing renamed. C-08's original wording is kept and annotated in place (spec/06 L21) with the verified sites; U-08 (spec/09 L54), spec/05 L112 and REQ-CALC-013's INVARIANTS (req/01-part2 L186) are amended to restrict the 'not enumerated' claim to `HostPolicyError` and `EffectError` only and to state that `CapabilityError` (L20408) and `HostFault` (L10820) are declared. U-08/U-14 remain OPEN on their merits — the elision at L23807 does leave the variant set unclosed — but the open question is now stated against the real text. WITHDRAWN CLAIM, recorded rather than silently overwritten (R-SCOPE-03): an earlier annotation added to C-08 by this same normalization pass asserted that `CapabilityError` 'exists only as a `Result` error type (L9736/L9743/L9749/L19212), never as a `Fault` variant'. That was itself wrong — `Capability(CapabilityError)` is a `Fault` variant at L22430 and L23808, and `Fault::CapabilityError(error)` is constructed at L20389 and L20790. It is withdrawn and replaced.

### Decision needed

No new decision; U-08/U-14 stand, restated against verified text.

## X-64

**`Fault::StalePlan` is used by the frozen source at L28373 but is a variant of none of the seven `Fault` declarations**

- **Kind:** `UNDECLARED-VARIANT` — an `Enum::Variant` path is used in the frozen source but appears in no declaration of that enum
- **Severity:** MAJOR
- **Terms affected:** T-70 `Fault`, T-02 `PlanProposal`, T-04 `ValidatedPlan`
- **Previously registered as:** `C-54`, `C-38`, `U-13`, `AMB-08`, `AMB-34`, `X-62`, `X-69`

### Evidence (frozen source)

| Line | Text at that line | What it denotes there |
|---|---|---|
| `Red-on-Rust.md` L28373 | ``is rejected with `Fault::StalePlan``` | turn [36]: the ONLY occurrence of the qualified path — the source names the variant itself |
| `Red-on-Rust.md` L27236 | `StalePlan` | turn [33]: a bare token, the sole content of a one-line ```text block |
| `Red-on-Rust.md` L23806 | `pub enum Fault {` | the frozen declaration R-CALC-06 cites: eight listed variants, no `StalePlan` |
| `Red-on-Rust.md` L23807 | `// ... (previous faults)` | the elision that makes the frozen block non-exhaustive |
| `Red-on-Rust.md` L26865 | `pub enum Fault {` | turn [33]: the actor-local declaration, contemporary with L27236, also without `StalePlan` |
| `Red-on-Rust.md` L10882 | `pub enum Fault {` | turn [18]: no `StalePlan` |

### Evidence (canonicalization layer)

| File:line | Text at that line | Note |
|---|---|---|
| `spec/01-canonical-specification.md`:138 | ``plus `StalePlan` at the planner boundary`` | normative R-CALC-06 — source-supported and kept; its annotation now says used-but-undeclared, not phantom |
| `req/01-registry-part2-semantics.md`:197 | `Verified, correction reverted` | REQ-CALC-014 STATEMENT, restored after the phantom claim was shown false |
| `req/01-registry-part2-semantics.md`:199 | `Withdrawal reverted` | REQ-CALC-014 POSTCONDITIONS, restored — `Fault::StalePlan` occurs verbatim at L28373 |
| `req/01-registry-part2-semantics.md`:195 | `L28373([36])` | REQ-CALC-014's SOURCE line, which cited the occurrence all along |
| `req/03-ambiguous.md`:68 | `that strike was itself wrong` | AMB-08's list, qualified in place rather than struck |
| `req/03-ambiguous.md`:264 | `occurs nowhere in L1–42312` | AMB-34, rewritten, with the withdrawn claim quoted |
| `spec/06-contradictions-ambiguities.md`:68 | ```Fault::StalePlan` occurs verbatim once, at L28373`` | C-54, rewritten from a phantom finding to a used-but-undeclared one |
| `spec/06-contradictions-ambiguities.md`:81 | `rewritten** in this revision` | C-59..C-65 summary line, recording the retraction of the earlier claim |

### The collision

`Fault::StalePlan` occurs verbatim once in L1-42312, at L28373 (turn [36]): “A `PlanProposal` with `observation_sequence < current_sequence` is rejected with `Fault::StalePlan`”. The bare token `StalePlan` occurs once more, at L27236 (turn [33]), as the sole content of a one-line ```text block. No `pub enum Fault` declaration — L10882, L17788, L18125, L22415, L23319, L23806, L26865 — contains the variant, and the frozen L23806 block elides its own head with `// ... (previous faults)` at L23807, so it cannot be read as exhaustive. This is therefore a used-but-undeclared variant path, one of twelve (X-69), and NOT a phantom introduced by the canonicalization layer. Three records name it and all three are source-supported: **spec/01 L138** (normative R-CALC-06) writes “… | InvalidReceipt` (plus `StalePlan` at the planner boundary)”; **REQ-CALC-014** (req/01-part2 L195-199) states “`StalePlan` is a member of the fault taxonomy at the planner boundary” with POSTCONDITIONS “`Fault::StalePlan` produced” and a SOURCE line that already cited L28373; **AMB-08** (req/03 L68) listed it among the frozen variants. What is *not* supported is AMB-08's citation “L23806-23824”, which runs past the enum's closing brace at L23816 into the unrelated heading “## 3. Request Continuation Frames” at L23821 and contains no `StalePlan`; the denial names are at L8758, one line outside the range AMB-08 cited.

### Why it matters

Two separate things matter here, and the second is about this repository rather than the source. (1) The source names a fault variant that none of its own declarations admits, so an implementer following R-CALC-06 adds a variant no frozen declaration authorizes — and because `Fault` identity is compared by the differential observer (R-REF-05), that addition is observable, not inert. It also widens R-CALC-06 from eight variants to nine, and AMB-08 is graded “Blocking: yes … the single most blocking ambiguity in the set”, so its statement is the one most likely to be implemented from. (2) An earlier revision of this pass filed this row as a PHANTOM-IDENTIFIER on the claim that “`Fault::StalePlan` occurs nowhere in L1-42312”, and amended four documents on that premise. The claim is false — the string occurs at L28373 — and REQ-CALC-014's own SOURCE line had cited L28373 all along, so the withdrawal contradicted the record's own provenance. A canonicalization layer that retracts correct normative text on a misread grep is a worse defect than the one it was trying to fix, which is why the retraction is itself recorded rather than quietly undone.

### Disposition

REPORTED, not resolved, and the earlier false correction REVERTED per R-SCOPE-03: the four documents amended on the “occurs nowhere” premise are restored, each with the withdrawn wording quoted in place so the retraction stays visible — spec/01 L138 (its annotation now records that `StalePlan` is used-but-undeclared rather than phantom), REQ-CALC-014's STATEMENT (L197) and POSTCONDITIONS (L199), and AMB-08's list (req/03 L68). AMB-34 is rewritten from “asserted but undeclared phantom” to “used but undeclared”, and C-54 likewise. The dictionary records `StalePlan` as a protected *source token* at both L27236 and L28373 and explicitly NOT as a declared `Fault` variant. Whether it SHOULD join the declared taxonomy is left to U-08, which owns the variant set — and U-08 now has to rule on all twelve undeclared paths at once (X-69), not on this one alone. Nothing is renamed and no variant is invented.

### Decision needed

Yes, but owned by U-08 and now widened by X-69: does `StalePlan` join the declared `Fault` taxonomy (the source uses the qualified path at L28373, so the answer is no longer forced), or is staleness rejection remapped onto a declared variant?

## X-65

**`MarshalFault` is declared twice with completely disjoint variant sets, and is used as an elided `Fault` payload**

- **Kind:** `TYPE-HOMONYM` — one name, two or more incompatible type declarations
- **Severity:** MAJOR
- **Terms affected:** T-73 `MarshalFault`, T-70 `Fault`, T-35 `ActorStatus`
- **Previously registered as:** `AMB-08`, `U-14`

### Evidence (frozen source)

| Line | Text at that line | What it denotes there |
|---|---|---|
| `Red-on-Rust.md` L10846 | `pub enum MarshalFault {` | turn [18]: declaration 1 |
| `Red-on-Rust.md` L10847 | `CapabilityNotTransferable,` | declared variant 1a |
| `Red-on-Rust.md` L10848 | `InvalidFormat,` | declared variant 1b |
| `Red-on-Rust.md` L25983 | `pub enum MarshalFault {` | turn [32]: declaration 2 — DISJOINT from declaration 1 |
| `Red-on-Rust.md` L25984 | `CapabilityRequiresDelegation,` | declared variant 2a — the one mod/06 and REQ-MARSHAL cite |
| `Red-on-Rust.md` L25985 | `SerializationError,` | declared variant 2b |
| `Red-on-Rust.md` L26871 | `MarshalFault(...),` | turn [33]: `MarshalFault` as a `Fault` variant payload, written elided |

### Evidence (canonicalization layer)

| File:line | Text at that line | Note |
|---|---|---|
| `mod/06-actor.md`:103 | `MarshalFault::CapabilityRequiresDelegation` | cites only the turn-[32] variant set |
| `req/01-registry-part1-foundations.md`:301 | `Err(MarshalFault::CapabilityRequiresDelegation)` | REQ postcondition citing only the turn-[32] set |
| `spec/08-verification-mapping.md`:63 | `MarshalFault` | verification mapping that assumes a single variant set |

### The collision

`pub enum MarshalFault` is declared twice. Turn [18] (L10846-10849) declares {`CapabilityNotTransferable`, `InvalidFormat`}; turn [32] (L25983-25986) declares {`CapabilityRequiresDelegation`, `SerializationError`}. The two sets share **zero** variants, so this is not a widening but a replacement with no retraction and no supersession note. The canonicalization layer cites only the turn-[32] form (mod/06-actor L62/L103, REQ-MARSHAL postcondition `Err(MarshalFault::CapabilityRequiresDelegation)` at req/01-part1 L301), and no record anywhere notes that `CapabilityNotTransferable` and `InvalidFormat` exist or have been dropped. Separately, the turn-[33] actor-local `Fault` (L26865) carries `MarshalFault(...)` as a variant payload with the payload elided, so the `Fault` taxonomy depends on a type whose own variant set is contested.

### Why it matters

R-MARSHAL-01..04 make capability rejection at the marshalling boundary a security property, and spec/08 maps 'embedded CapRef in List ⇒ MarshalFault' to a verification obligation. An implementation that matches on the turn-[18] set cannot produce `CapabilityRequiresDelegation`, and one that matches on the turn-[32] set cannot produce `CapabilityNotTransferable`; the two are not aliases, they denote different conditions (non-transferable vs requires-delegation). Because faults are compared by the differential observer, the choice is observable.

### Disposition

Both declarations recorded verbatim in T-73 with the turn-[18] form listed under `supersedes`; nothing renamed and neither declaration deleted. Under latest-frozen-text the turn-[32] set governs, but this entry flags that the supersession was never stated and that `CapabilityNotTransferable` has no successor — the same gap C-08 records for `ScopeViolation`. Joined to U-08/U-14, which own the error-variant enumeration.

### Decision needed

Yes, folded into U-14: which `MarshalFault` variant set governs, and does `CapabilityNotTransferable` survive as a distinct condition?

## X-66

**`CapabilityError::Invalid` is used as the `derive` fallback but never declared; the declared sibling `InvalidConstraint` is used for the same fallback in the same turn**

- **Kind:** `UNDECLARED-VARIANT` — an `Enum::Variant` path is used in the frozen source but appears in no declaration of that enum
- **Severity:** MAJOR
- **Terms affected:** T-72 `CapabilityError`, T-70 `Fault`, T-13 `CapabilityKernel`, T-09 `CapRef`
- **Previously registered as:** `U-14`, `U-08`, `X-59`

### Evidence (frozen source)

| Line | Text at that line | What it denotes there |
|---|---|---|
| `Red-on-Rust.md` L20408 | `pub enum CapabilityError {` | turn [28]: the ONLY declaration of the inner error enum |
| `Red-on-Rust.md` L20409 | `Revoked,` | declared variant |
| `Red-on-Rust.md` L20410 | `Expired,` | declared variant — never used; the used `ExpiredOrRevoked` belongs to `RefCapabilityError` |
| `Red-on-Rust.md` L20411 | `InvalidConstraint,` | declared variant |
| `Red-on-Rust.md` L20412 | `// ...` | verbatim elision marker — the declared set is not closed |
| `Red-on-Rust.md` L20451 | `Err(CapabilityError::InvalidConstraint)` | turn [28]: `CapabilityKernelView::derive` fallback, using the DECLARED variant |
| `Red-on-Rust.md` L20835 | `unwrap_or_else(\|\| Err(CapabilityError::Invalid))` | turn [28]: the SAME fallback restated, using an UNDECLARED variant |

### Evidence (canonicalization layer)

| File:line | Text at that line | Note |
|---|---|---|
| `spec/05-terminology.md`:112 | ```CapabilityError``` | listed as 'Enum variants not enumerated' although L20408 declares them |
| `spec/09-unresolved-decisions.md`:54 | `are not enumerated` | U-08's claim, which hides the declared set and the `Invalid` split |

### The collision

`pub enum CapabilityError` is declared once, at L20408 (turn [28]), as {`Revoked`, `Expired`, `InvalidConstraint`, `// ...`}. Within the same turn the `CapabilityKernelView::derive` result-queue fallback is written twice with two different error values: L20451 uses `Err(CapabilityError::InvalidConstraint)` — a declared variant — while L20835 uses `unwrap_or_else(|| Err(CapabilityError::Invalid))`. `CapabilityError::Invalid` is never declared. The elision at L20412 leaves the set formally open, but nothing in the source introduces `Invalid`, and the two sites are not two different methods: both pop the front of `self.results` and return the default when it is empty. The reference model uses a third name again, `RefCapabilityError::ExpiredOrRevoked` (L20619), which collapses the declared `Expired` and `Revoked` into one.

### Why it matters

`CapabilityError` is the payload of the frozen `Fault::Capability(CapabilityError)` variant (L23808), so its variant set is part of the fault vocabulary the differential observer compares (R-REF-05). An implementation that follows L20835 cannot compile against the L20408 declaration; one that follows L20451 reports a different fault value for the identical empty-queue condition. spec/05 L112 and U-08 currently say these variants are 'not enumerated', which hides the fact that a declaration exists and that the source contradicts itself against it (X-59).

### Disposition

REPORTED; nothing renamed and no variant invented. T-72 records the declaration verbatim, marks `Invalid` as used-but-undeclared and `Expired` as declared-but-unused, and keeps the elision marker as a protected token so the set is not represented as closed. spec/05 L112 and U-08 are amended to say that `CapabilityError` IS declared at L20408 behind an elision, and that the open question is the *elided* remainder plus the `Invalid`/`InvalidConstraint` split. Joined to U-14.

### Decision needed

Yes, folded into U-14: is `Invalid` a distinct variant or a typo for `InvalidConstraint`, and what fills the L20412 elision?

## X-68

**`HostFault` denotes a fault NAME in the v1 grammar and a Rust TYPE from turn [18]; `Revoked` denotes a fault name and a `CapabilityError` variant**

- **Kind:** `TYPE-ROLE-HOMONYM` — one name used as both a type and a predicate/symbol
- **Severity:** MAJOR
- **Terms affected:** T-74 `HostFault`, T-70 `Fault`, T-72 `CapabilityError`
- **Previously registered as:** `AMB-08`, `U-08`, `X-57`, `X-01`

### Evidence (frozen source)

| Line | Text at that line | What it denotes there |
|---|---|---|
| `Red-on-Rust.md` L1949 | `**Faults:**` | turn [5]: the v1 grammar `F ::= CapViolation \| BudgetExhausted \| ScopeViolation \| Revoked \| HostFault \| IsolationBreach` — here `HostFault` and `Revoked` are MEMBERS of `F`, i.e. faults |
| `Red-on-Rust.md` L10820 | `pub enum HostFault {` | turn [18]: `HostFault` becomes a TYPE — the payload of `Fault::Host` |
| `Red-on-Rust.md` L23813 | `Host(HostFault),` | turn [30]: the frozen `Fault` variant that carries the type |
| `Red-on-Rust.md` L20409 | `Revoked,` | turn [28]: `Revoked` becomes a VARIANT of `CapabilityError`, which is itself the payload of `Fault::Capability` |
| `Red-on-Rust.md` L2024 | `IsolationBreach` | turn [5]: `fault(IsolationBreach)` — a member of `F` used as a receipt-mismatch conclusion |
| `Red-on-Rust.md` L8766 | `IsolationBreach` | turn [14]: v0.3 `E-ReceiptMismatch` concludes `Fault(IsolationBreach)` |

### Evidence (canonicalization layer)

| File:line | Text at that line | Note |
|---|---|---|
| `req/03-ambiguous.md`:69 | ``previously also mapped `IsolationBreach``` | AMB-08's reading (a), corrected in place: `IsolationBreach` is the receipt-mismatch fault |
| `spec/01-canonical-specification.md`:138 | ``The frozen fault taxonomy is the Rust `Fault` enum`` | R-CALC-06 states a flat variant list that matches neither reading of `HostFault` |

### The collision

Two identifiers in the fault vocabulary change grammatical role between eras without retraction. **`HostFault`** is a *member of the fault grammar* `F` at L1949 (turn [5]) — i.e. it denotes one fault, a sibling of `CapViolation` and `BudgetExhausted` — and from L10820 (turn [18]) it denotes a *Rust enum type*, the payload of the frozen `Fault::Host(HostFault)` variant (L23813). Under the first reading `Fault::HostFault` would be a leaf fault; under the second `HostFault` is a whole sub-taxonomy (and an undeclared one — X-67). **`Revoked`** is likewise a member of `F` at L1949 and, from L20409 (turn [28]), a variant of `CapabilityError`, which is the payload of `Fault::Capability(CapabilityError)` — so `Revoked` moves from the top level of the taxonomy to two levels down. **`IsolationBreach`** stays a member of `F` (L2024, L7223) and is used as the conclusion of the *receipt-mismatch* rule (L8766), yet AMB-08 lists it among the capability-denial names, and it appears in no `Fault` declaration.

### Why it matters

A name that denotes both a fault and a type of faults cannot be compiled, encoded or compared without picking a level, and the two levels have different canonical encodings: a leaf fault is one discriminant, a nested enum is a discriminant plus a payload. R-CALC-06 states the taxonomy as a flat variant list, which matches neither reading for `HostFault`. This is the same class of defect as X-57 (`Request` used as five different kinds of thing) and X-01 (`ValidatedPlan` as a type and as a predicate), and it is invisible to a name-based glossary because the *name* never changes — only its level in the taxonomy does.

### Disposition

REPORTED; both readings recorded and neither chosen. T-70 and T-74 carry the v1 grammar members (`HostFault`, `Revoked`, `CapViolation`, `IsolationBreach`) as protected tokens with their role stated, and T-74's `forbidden` list bars using `HostFault` as a fault name. AMB-08's classification of `IsolationBreach` as a capability-denial name is corrected: the source uses it for receipt mismatch. Joined to U-08, which must fix the *level* of each name as well as its spelling.

### Decision needed

Yes, folded into U-08: for each of `HostFault`, `Revoked` and `IsolationBreach`, state whether it is a leaf fault, a nested error type, or a variant of one — and at which level of the taxonomy it sits.

## X-69

**Twelve `Fault::` variant paths are used in the frozen source and declared by no `Fault` enum**

- **Kind:** `UNDECLARED-VARIANT` — an `Enum::Variant` path is used in the frozen source but appears in no declaration of that enum
- **Severity:** MAJOR
- **Terms affected:** T-70 `Fault`, T-02 `PlanProposal`, T-56 `LLMOutput`, T-24 `Budget`, T-27 `Deadline`
- **Previously registered as:** `C-08`, `C-58`, `AMB-08`, `U-08`, `U-13`

### Evidence (frozen source)

| Line | Text at that line | What it denotes there |
|---|---|---|
| `Red-on-Rust.md` L28373 | ``is rejected with `Fault::StalePlan``` | turn [36]: the staleness rejection, naming a variant no declaration contains |
| `Red-on-Rust.md` L941 | `Fault::AuthoritySuspended` | turn [3]: capability-denial family |
| `Red-on-Rust.md` L1018 | `Fault::FuelExhausted` | turn [3]: budget family; the declared name is `BudgetExhausted` |
| `Red-on-Rust.md` L944 | `Fault::ScopeViolation` | turn [3] |
| `Red-on-Rust.md` L3671 | `Fault::ScopeViolation` | turn [7] |
| `Red-on-Rust.md` L5059 | `Fault::ScopeViolation` | turn [9] |
| `Red-on-Rust.md` L6704 | `Fault::Revoked` | turn [11] |
| `Red-on-Rust.md` L6705 | `Fault::AncestorRevoked` | turn [11]: a near-synonym of `Revoked` in the same list |
| `Red-on-Rust.md` L6706 | `Fault::Unauthorized` | turn [11]: a third name for the same denial |
| `Red-on-Rust.md` L937 | `Fault::CapabilityRevoked(cref)` | turn [3]: payload-bearing form |
| `Red-on-Rust.md` L10446 | `Fault::CapabilityRevoked` | turn [18] |
| `Red-on-Rust.md` L5055 | `Fault::CapabilityRevoked` | turn [9] |
| `Red-on-Rust.md` L10447 | `CapabilityRevoked` | turn [18]: seven uses in all |
| `Red-on-Rust.md` L10466 | `Fault::ReservedCapacityExceeded` | turn [18] |
| `Red-on-Rust.md` L10467 | `ReservedCapacityExceeded` | turn [18] |
| `Red-on-Rust.md` L20389 | `Fault::CapabilityError(error)` | turn [28]: also X-38/X-66 — a type of the same name exists |
| `Red-on-Rust.md` L25714 | `Fault::NoSuchActor` | turn [32] |
| `Red-on-Rust.md` L26017 | `Fault::UnknownActor` | turn [32]: a second name for the same condition, 303 lines later |
| `Red-on-Rust.md` L23806 | `pub enum Fault {` | the frozen declaration R-CALC-06 cites |
| `Red-on-Rust.md` L23807 | `// ... (previous faults)` | the elision that makes the frozen block non-exhaustive |
| `Red-on-Rust.md` L26865 | `pub enum Fault {` | turn [33]: actor-local declaration, also without any of the twelve |

### Evidence (canonicalization layer)

| File:line | Text at that line | Note |
|---|---|---|
| `spec/06-contradictions-ambiguities.md`:73 | ``Twelve `Fault::` variant paths`` | C-59, the row this entry backs |
| `spec/06-contradictions-ambiguities.md`:68 | `one of twelve (C-59)` | C-54, corrected to point at the population finding |
| `req/03-ambiguous.md`:68 | ``one of twelve such `Fault::` paths`` | AMB-08, qualified rather than struck |

### The collision

Checking every `Fault::` path in L1-42312 against the seven `pub enum Fault` declarations (L10882, L17788, L18125, L22415, L23319, L23806, L26865) yields TWELVE distinct variant paths that the source uses and no declaration contains: `CapabilityRevoked` (7 uses: L937, L3667, L3683, L5055, L5071, L10446, L10447), `ScopeViolation` (3: L944, L3671, L5059), `CapabilityError` (3: L20389, L20538, L20790), `ReservedCapacityExceeded` (2: L10466, L10467), `AuthoritySuspended` (L941), `FuelExhausted` (L1018), `Revoked` (L6704), `AncestorRevoked` (L6705), `Unauthorized` (L6706), `NoSuchActor` (L25714), `UnknownActor` (L26017) and `StalePlan` (L28373). The frozen L23806 block elides its own head with `// ... (previous faults)` at L23807, so it cannot be read as exhaustive; the other six declarations are not elided and do not contain these names either.

### Why it matters

`Fault` is the machine's terminal failure value, and its identity is what the differential observer compares (R-REF-05), what `FaultKind` is derived from (R-CORE-09), and what L26877-L26880 orders as “the same order as enum declaration” — an ordering that is undefined for a variant no declaration contains. An implementation cannot construct a `Fault::CapabilityRevoked(cref)` that no declaration admits and a test cannot assert on one. Worse, several of the twelve are near-synonyms differing only in spelling (`CapabilityRevoked`/`Revoked`/`AncestorRevoked`/`Unauthorized`, `NoSuchActor`/`UnknownActor`), so the count of distinct capability-denial faults comes out as four, nine or twelve depending on which set a reader takes — which is exactly why C-58 and AMB-08 disagree, and why AMB-08 is graded the single most blocking ambiguity in the set. The capability-denial families are the set the frozen `Authority` invariants and the `capcheck`/`scope` obligations turn on.

### Disposition

REPORTED, not resolved, and nothing renamed or invented. X-64 keeps the `StalePlan` case individually because it crosses REQ-CALC-014's stated postcondition, and X-38 keeps the `CapabilityError` case because a separate declared type of that name exists; this entry is the population-level finding, held apart from both so every affected record stays traceable. U-08 already owns the `Fault` variant set and has to close all twelve at once: either the seven declarations are incomplete, in which case the twelve are added and each near-synonym family resolved to one name, or the twelve uses are prose errors to be remapped onto declared variants. The source records neither option. All twelve names are listed in T-70's `protected` so no later pass normalizes one away by accident.

### Decision needed

Yes — owned by U-08, but U-08 as written covers only the declared variant set; it has to be widened to rule on the twelve undeclared paths and on the near-synonym families.

## X-70

**Theorem 2's proof and the property-test matrix both depend on `Expr::Delegate`, which no `enum Expr` declaration admits**

- **Kind:** `UNDECLARED-VARIANT` — an `Enum::Variant` path is used in the frozen source but appears in no declaration of that enum
- **Severity:** MAJOR
- **Terms affected:** T-30 `Expr`, T-15 `DelegatedCapability`, T-31 `Value`, T-12 `Constraint`, T-13 `CapabilityKernel`, T-10 `Authority`
- **Previously registered as:** `C-60`, `X-29`, `AMB-11`, `C-16`, `U-02`

### Evidence (frozen source)

| Line | Text at that line | What it denotes there |
|---|---|---|
| `Red-on-Rust.md` L26056 | `Theorem 2: No Authority Amplification` | turn [32]: the theorem whose proof depends on the undeclared node |
| `Red-on-Rust.md` L26057 | `ExplicitlyDelegatedAuthority` | turn [32]: the boxed statement — authority may grow only by explicit delegation |
| `Red-on-Rust.md` L26058 | ``Authority can only cross boundaries via `Expr::Delegate``` | turn [32]: the proof's ONLY authority-crossing mechanism |
| `Red-on-Rust.md` L26078 | ``\| **C: Delegation** \| `Expr::Delegate` \|`` | turn [32]: property-test matrix row C, three invariants asserted on the node |
| `Red-on-Rust.md` L25989 | `Expr::Delegate {` | turn [32]: the only place its fields are given |
| `Red-on-Rust.md` L25991 | `constraint: Constraint` | turn [32]: field 2 of 2 — a T-12 `Constraint`, the same field `Attenuate` carries |
| `Red-on-Rust.md` L12145 | `pub enum Expr {` | turn [21]: the frozen AST, twelve constructors, no `Delegate` |
| `Red-on-Rust.md` L20702 | `pub enum Expr {` | turn [28]: `Var, Lit, Prim, If, Seq, Lambda, Call, Attenuate` — no `Delegate` |
| `Red-on-Rust.md` L24062 | ``explicit `Delegate` operations`` | turn [32]: prose use |
| `Red-on-Rust.md` L25700 | `Expr::Delegate` | turn [32]: prose use |

### Evidence (canonicalization layer)

| File:line | Text at that line | Note |
|---|---|---|
| `spec/06-contradictions-ambiguities.md`:74 | `Theorem 2's proof and the property-test matrix` | C-60, rewritten from a duplicate of X-29 to the theorem-dependency finding |
| `req/03-ambiguous.md`:91 | ```Expr::Delegate` is absent from the frozen AST`` | AMB-11, which already records the declaration gap and is not superseded |

### The collision

X-29, AMB-11 and C-16 all record the underlying fact: `Expr::Delegate` is used by the frozen source and appears in none of the five `pub enum Expr` declarations (L12145 — twelve constructors, L14030, L14413, L20295, L20702). This entry records what the sweep found beyond that, which none of the three states: TWO NORMATIVE ARTIFACTS DEPEND ON THE UNDECLARED NODE. Theorem 2 (No Authority Amplification, L26056-26058) is proved by exhaustion over the ways authority can cross a boundary — “Ordinary `Send` operations pass through `marshal()`, which strictly rejects `Value::Capability`. Authority can only cross boundaries via `Expr::Delegate`, which invokes `CapabilityKernel::derive`, guaranteeing `child <= parent`” — so the node is the proof's single non-trivial case. The property-test matrix at L26078 makes row C (“Delegation”) assert three invariants on it: kernel derivation called exactly once, `child <= parent`, and a revoked parent cannot delegate. The sweep also found two further use sites that AMB-11 does not list (L26058, L26078) and one field detail: `Delegate` carries `constraint: Constraint` (L25991), the same field `Expr::Attenuate` carries, so attenuation is declared and delegation is not despite the two sharing a shape.

### Why it matters

A theorem proved by exhaustion is only as sound as its case list, and here one case names a constructor the frozen AST does not admit. Two consequences follow, and they pull in opposite directions. If `Delegate` is not constructible, Theorem 2's proof has an empty case and its conclusion holds only because authority then cannot cross at all — a stronger claim than the theorem states, and one that would make row C of the test matrix untestable. If `Delegate` IS constructible, then the frozen twelve-constructor `Expr` is incomplete, and every obligation quantified over plans — R-VALID-03, R-CAPCHK-04, and the boxed `ExternalEffect(E) ⇒ ValidatedPlan(P)` theorem (X-46) — is quantified over an AST missing a node that transfers authority. Because L-04 (CapRef ≠ Authority) and L-05 (LLM output ≠ Authority) make authority transfer the one operation that must not be inferred, an authority-carrying AST node that exists only in a proof sketch is the single worst place for a declaration gap to be. This is a Verification-versus-Specification defect in the sense L-08 draws: the proof text asserts a property of a surface the specification does not declare.

### Disposition

REPORTED, not resolved, nothing renamed and no constructor invented. X-29 keeps the declaration-gap finding and gains the two additional use sites; AMB-11 keeps the two-readings analysis and its correction to `spec/01` L334; this entry adds only the dependence of Theorem 2 and of test-matrix row C, which is what makes the gap blocking rather than cosmetic. `Expr::Delegate` is already protected in T-30 and T-15, so it cannot be normalized away; `Value::DelegatedCapability` (X-74) is added to T-31's `protected` for the same reason. The decision — is `Delegate` a thirteenth constructor, or is Theorem 2's case list to be restated without it? — is not recorded in the source and is escalated to U-02, which already owns the undefined-name family.

### Decision needed

Yes — owned by U-02 as extended by this entry: does `Expr::Delegate` become a declared thirteenth constructor (freezing the L25989-25992 field set), or must Theorem 2's proof and test-matrix row C be restated without it?

## X-71

**`MachineEvent` is declared eight times and used with eight variant paths declared by none of them**

- **Kind:** `UNDECLARED-VARIANT` — an `Enum::Variant` path is used in the frozen source but appears in no declaration of that enum
- **Severity:** MAJOR
- **Terms affected:** T-75 `MachineEvent`, T-47 `WalRecord`, T-45 `WAL`, T-70 `Fault`, T-35 `ActorStatus`
- **Previously registered as:** `U-28`

### Evidence (frozen source)

| Line | Text at that line | What it denotes there |
|---|---|---|
| `Red-on-Rust.md` L14697 | `pub enum MachineEvent {` | turn [23]: first declaration |
| `Red-on-Rust.md` L15958 | `pub enum MachineEvent {` | turn [24] |
| `Red-on-Rust.md` L17588 | `pub enum MachineEvent {` | turn [25]: adds `ApplyFunction` |
| `Red-on-Rust.md` L18104 | `pub enum MachineEvent {` | turn [26] |
| `Red-on-Rust.md` L18631 | `pub enum MachineEvent {` | turn [26] |
| `Red-on-Rust.md` L20318 | `pub enum MachineEvent {` | turn [28]: adds `EnterAttenuate`, `DeriveCapability`, `Fault` |
| `Red-on-Rust.md` L20724 | `pub enum MachineEvent {` | turn [28] |
| `Red-on-Rust.md` L22002 | `pub enum MachineEvent {` | turn [29]: adds `EffectIssued`, `EffectCompleted` |
| `Red-on-Rust.md` L22003 | `// ...` | the elision that makes the last declaration non-exhaustive |
| `Red-on-Rust.md` L21483 | `MachineEvent::EnterRequest` | turn [29]: used, never declared |
| `Red-on-Rust.md` L21536 | `MachineEvent::BeginRequestTarget` | turn [29]: used, never declared |
| `Red-on-Rust.md` L21645 | `MachineEvent::BeginRequestArgument` | turn [29]: used, never declared |
| `Red-on-Rust.md` L25740 | `MachineEvent::Blocked` | turn [32]: the declared name is `Block` |
| `Red-on-Rust.md` L25668 | `MachineEvent::Spawned` | turn [32]: never declared |
| `Red-on-Rust.md` L25966 | `MachineEvent::ActorSpawned` | turn [32]: a second name for `Spawned`, with `{ parent, child }` |
| `Red-on-Rust.md` L25728 | `MachineEvent::Sent` | turn [32]: never declared |
| `Red-on-Rust.md` L26027 | `MachineEvent::MessageSent` | turn [32]: a second name for `Sent`, with `{ from, to }` |

### Evidence (canonicalization layer)

| File:line | Text at that line | Note |
|---|---|---|
| `spec/06-contradictions-ambiguities.md`:75 | ```MachineEvent` is declared eight times`` | C-61, the row this entry backs |
| `spec/09-unresolved-decisions.md`:144 | ``### U-28 — Which `MachineEvent` names govern`` | the decision this entry escalates to; added by the same sweep |
| `req/03-ambiguous.md`:277 | ``### AMB-36 — `MachineEvent` is declared eight times`` | the ambiguity row this entry backs |

### The collision

`MachineEvent` has EIGHT declarations (L14697, L15958, L17588, L18104, L18631, L20318, L20724, L22002), the last with its head elided as `// ...` at L22003. Beyond the drift between those declarations, eight further variant paths are used and declared by none of them: `EnterRequest` (L21483, L23380), `BeginRequestTarget` (L21536, L23398), `BeginRequestArgument` (L21645, L23426), `Blocked` (L25740, L26038), `Spawned` (L25668), `ActorSpawned` (L25966), `Sent` (L25728) and `MessageSent` (L26027). Two of the eight are second names for a concept the others also name: `Blocked` against the declared `Block`, and `Spawned`/`ActorSpawned` and `Sent`/`MessageSent` as pairs used in different turns of the same document.

### Why it matters

This is the vocabulary the trace is made of, so it decides three things at once: what the WAL records (T-45), what the differential observer compares between two implementations (R-REF-05), and what a conformance fixture may assert. If one implementation emits `Spawned` and another `ActorSpawned` for the same transition, the differential harness reports a divergence that is a naming artifact rather than a semantic one — the same failure mode as X-21's `Running`/`Active`, but on the event stream instead of the actor state, and there are four such pairs here rather than one. `Blocked` is worse than cosmetic because `Blocked` is also an `ActorStatus` variant (X-74) and a `StepResult` variant (X-73), so a reader of an event log cannot tell which layer the event came from. `EffectIssued`/`EffectCompleted` ARE declared here (L22005, L22010) with `{ id, digest }`, which is what makes L-06 (EffectIssued ≠ EffectCompleted) enforceable at all — so the enum matters to the request's own required distinctions, not only to the trace.

### Disposition

REPORTED, not resolved, and `MachineEvent` is filed as T-75 — it had no term of record at all before this sweep, despite being the event vocabulary the WAL and the differential comparison are built on. The eight declarations are additive across turns (each introduces the events for that turn's feature), so a union reading is available; but the four duplicate names have to be resolved to one name each by a single source ruling, and no such ruling exists. All eight undeclared paths are listed in T-75's `protected` so none is normalized away by a later pass. Nothing is renamed.

### Decision needed

Yes — `spec/09` U-28: is the vocabulary the union of all eight declarations or only the last, which name governs each duplicate pair, and are the three `*Request*` events declared or struck?

## X-72

**`CanonicalError` is declared seven times in four shapes, with the same variant names at different arities**

- **Kind:** `DIVERGENT-SHAPE` — the same type name is declared repeatedly with materially different variant or field shapes
- **Severity:** MAJOR
- **Terms affected:** T-76 `CanonicalError`, T-62 `CanonicalEnvelope`, T-63 `CanonicalPayload`, T-47 `WalRecord`, T-31 `Value`
- **Previously registered as:** `C-47`, `C-48`, `C-49`, `U-29`, `U-14`

### Evidence (frozen source)

| Line | Text at that line | What it denotes there |
|---|---|---|
| `Red-on-Rust.md` L29188 | `pub enum CanonicalError {` | turn [38]: shape (i), five unit variants |
| `Red-on-Rust.md` L29189 | `InvalidVersion,` | turn [38]: a UNIT variant |
| `Red-on-Rust.md` L29968 | `pub enum CanonicalError {` | turn [41]: shape (ii), seven variants, two respelled |
| `Red-on-Rust.md` L29973 | `PayloadTooShort,` | turn [41]: where the others say `UnexpectedEof` |
| `Red-on-Rust.md` L29975 | `Utf8Error,` | turn [41]: where the others say `InvalidUtf8` |
| `Red-on-Rust.md` L30661 | `pub enum CanonicalError {` | turn [41]: shape (iii), nine struct variants |
| `Red-on-Rust.md` L30662 | `InvalidVersion { expected: u8, found: u8 }` | turn [41]: the SAME name, now payload-bearing |
| `Red-on-Rust.md` L30666 | `InvalidUtf8,` | turn [41]: unit, alongside payload-bearing siblings |
| `Red-on-Rust.md` L30670 | `InvalidBoolValue { found: u8 }` | turn [41]: only in this shape |
| `Red-on-Rust.md` L34994 | `pub enum CanonicalError {` | turn [47]: shape (iv), head elided |
| `Red-on-Rust.md` L34996 | `DuplicateMapKey` | turn [47]: “NEW: Enforces strict injectivity” |

### Evidence (canonicalization layer)

| File:line | Text at that line | Note |
|---|---|---|
| `spec/06-contradictions-ambiguities.md`:76 | ```CanonicalError` is declared seven times`` | C-62, the row this entry backs |
| `spec/09-unresolved-decisions.md`:151 | ``### U-29 — Which `CanonicalError` shape governs`` | the decision this entry escalates to; added by the same sweep |
| `req/03-ambiguous.md`:285 | ``### AMB-37 — `CanonicalError` is declared seven times`` | the ambiguity row this entry backs |

### The collision

`CanonicalError` has SEVEN declarations (L29188, L29968, L30661, L32083, L32959, L33299, L34994) in four materially different shapes. Shape (i) L29188 has five unit variants. Shape (ii) L29968 has seven and respells two of them — `Utf8Error` where the others say `InvalidUtf8`, `PayloadTooShort` where the others say `UnexpectedEof` — and adds `LengthOverflow`, which shape (i) lacks entirely. Shape (iii) L30661 turns six of the same names into payload-bearing struct variants (`InvalidVersion { expected: u8, found: u8 }`, `InvalidTypeTag { expected: u8, found: u8 }`, `LengthMismatch { expected: u32, found: usize }`, `TrailingBytes { count: usize }`, `InvalidDiscriminant { found: u8 }`, `InvalidBoolValue { found: u8 }`). Shape (iv) L34994 elides its head as `// ... previous variants` and adds `DuplicateMapKey`.

### Why it matters

This is the `Err` arm of every `canonical_serialize` and `canonical_deserialize`, so it is what reports every violation of the frozen envelope and payload rules — the same path on which X-50 (the envelope wire format) is already BLOCKING. The arity divergence is not cosmetic: `InvalidVersion` as a unit variant cannot carry the expected and found version bytes, so a decoder written against L29188 loses the diagnostic L30661 requires, and a test written against L30661 does not compile against L29188. Two spellings for one condition (`InvalidUtf8`/`Utf8Error`, `UnexpectedEof`/`PayloadTooShort`) is X-21's `Running`/`Active` pattern on the error channel, where a fixture matching one spelling silently passes on the other — and canonicalization is precisely where a silent pass becomes a consensus fork, because two nodes that disagree on which errors are fatal disagree on the digest. `DuplicateMapKey` is the only variant that enforces map injectivity, and it exists in one of four shapes, so whether canonical encoding rejects duplicate keys at all depends on which declaration an implementer reads.

### Disposition

REPORTED, not resolved; `CanonicalError` is filed as T-76 with all four shapes given verbatim in `shape`/`supersedes` and every divergent spelling listed in `protected` so none is normalized away. L30661 is the most informative and the latest non-elided declaration, but nominating it would drop `PayloadTooShort` and `Utf8Error` from the record, so no shape is chosen here. U-08 governs `Fault` only; `CanonicalError` needs its own ruling before any canonical-codec test can be written, and that ruling has to state whether the payload-bearing shape (iii) supersedes (i) and (ii) or whether the unit variants remain legal.

### Decision needed

Yes — `spec/09` U-29: which of the four shapes governs, do the unit variants of shapes (i)/(ii) survive shape (iii)'s payload-bearing forms, and which spelling governs each respelled pair?

## X-73

**`StepResult` is two disjoint enums — the CEK machine's and the actor scheduler's — sharing one name**

- **Kind:** `TYPE-HOMONYM` — one name, two or more incompatible type declarations
- **Severity:** MAJOR
- **Terms affected:** T-77 `StepResult`, T-70 `Fault`, T-35 `ActorStatus`, T-36 `RunState`, T-17 `EffectRequest`
- **Previously registered as:** `C-63`, `X-23`, `U-26`

### Evidence (frozen source)

| Line | Text at that line | What it denotes there |
|---|---|---|
| `Red-on-Rust.md` L1006 | `pub enum StepResult {` | turn [3]: the CEK machine's step outcome |
| `Red-on-Rust.md` L1007 | `Continue,` | turn [3]: machine variant 1 |
| `Red-on-Rust.md` L1010 | `YieldToHost(Effect),` | turn [3]: carries a T-20 `Effect` |
| `Red-on-Rust.md` L9586 | `pub enum StepResult {` | turn [17]: the actor scheduler's step outcome |
| `Red-on-Rust.md` L9587 | `Progressed,` | turn [17]: scheduler variant 1 |
| `Red-on-Rust.md` L9588 | `Blocked(ActorId),` | turn [17]: carries an identity the machine's variants never do |
| `Red-on-Rust.md` L9591 | `Faulted(ActorId, Fault),` | turn [17]: not an alias of the machine's `Fault(Fault)` |
| `Red-on-Rust.md` L9592 | `NoRunnableActors,` | turn [17]: meaningful only at scheduler level |
| `Red-on-Rust.md` L10397 | `pub enum StepResult {` | turn [18]: scheduler family restated |
| `Red-on-Rust.md` L10947 | `pub enum StepResult {` | turn [18]: scheduler family restated |

### Evidence (canonicalization layer)

| File:line | Text at that line | Note |
|---|---|---|
| `spec/06-contradictions-ambiguities.md`:77 | ```StepResult` is two disjoint enums`` | C-63, the row this entry backs |
| `spec/09-unresolved-decisions.md`:130 | ``### U-26 — Which layer owns the name `StepResult`?`` | the decision this entry escalates to; added by the same sweep |
| `req/03-ambiguous.md`:293 | ``### AMB-38 — `StepResult` names two disjoint enums`` | the ambiguity row this entry backs |

### The collision

Two enums named `StepResult` have no variant in common. L1006 (turn [3], the CEK machine) declares `Continue | Halt(Value) | Fault(Fault) | YieldToHost(Effect)` — one reduction of one actor, carrying no identity. L9586 (turn [17], the actor scheduler; restated at L10397 and L10947) declares `Progressed | Blocked(ActorId) | Pending(ActorId, EffectRequest) | Halted(ActorId, Value) | Faulted(ActorId, Fault) | NoRunnableActors` — every variant carries an `ActorId`, and `Pending` carries a T-28 `EffectRequest`. They are not successive versions of one type; they are the step outcome of two different layers, and neither declaration mentions the other.

### Why it matters

Both are returned by a method an implementer will call `step`, and a reader of any single turn cannot tell which is meant. Turn [3] says a step yields `YieldToHost(Effect)`; turn [17] says a step yields `Pending(ActorId, EffectRequest)` — and `Effect` (T-16) versus `EffectRequest` (T-17) is one of the distinctions this normalization request explicitly requires to be kept separate, so the homonymy puts that distinction at risk from the type name itself. The scheduler's `Faulted(ActorId, Fault)` and the machine's `Fault(Fault)` are likewise different types, not aliases, and X-23 already records `Faulted` versus `Fault` as a live split inside `RunState`. Prose saying “the step returned Blocked” is ambiguous between three enums (`StepResult`, `ActorStatus`, `RunState`), which is the ambiguity that makes X-71's `MachineEvent::Blocked` undiagnosable from a log.

### Disposition

REPORTED, not resolved; recorded as T-77 with both shapes given verbatim. Renaming either enum would violate the no-silent-rename constraint, and unlike `Observation`/`HostObservation` (X-06) the source provides no second name to adopt — so the homonymy stands and is disambiguated by layer in every dictionary entry that mentions it (T-70 for the machine, T-35 for the scheduler). T-77's `forbidden` list bans the unqualified phrase “step result” for exactly this reason.

### Decision needed

Yes — `spec/09` U-26: which layer keeps the name `StepResult` and what the other layer's step outcome is called. The source offers no second name, so this cannot be settled by citation alone.

## X-74

**`ActorStatus` is declared seven times in three shapes; X-21 records only two declarations**

- **Kind:** `DIVERGENT-SHAPE` — the same type name is declared repeatedly with materially different variant or field shapes
- **Severity:** MAJOR
- **Terms affected:** T-35 `ActorStatus`, T-37 `ActorState`, T-32 `EvalState`, T-17 `EffectRequest`, T-26 `Reserved`, T-77 `StepResult`
- **Previously registered as:** `C-64`, `X-21`, `U-27`

### Evidence (frozen source)

| Line | Text at that line | What it denotes there |
|---|---|---|
| `Red-on-Rust.md` L9411 | `pub enum ActorStatus {` | turn [17]: shape (i) |
| `Red-on-Rust.md` L10346 | `pub enum ActorStatus {` | turn [18]: shape (i) restated |
| `Red-on-Rust.md` L10866 | `pub enum ActorStatus {` | turn [18] |
| `Red-on-Rust.md` L21234 | `pub enum ActorStatus {` | turn [29]: shape (ii), a three-field `Pending` |
| `Red-on-Rust.md` L21240 | `continuation: Continuation,` | turn [29]: the continuation INSIDE `Pending` |
| `Red-on-Rust.md` L21244 | `Blocked(Continuation),` | turn [29]: and also inside `Blocked` |
| `Red-on-Rust.md` L23306 | `pub enum ActorStatus {` | turn [30]: shape (iii), `continuation` dropped |
| `Red-on-Rust.md` L23793 | `pub enum ActorStatus {` | turn [30]: shape (iii) restated |

### Evidence (canonicalization layer)

| File:line | Text at that line | Note |
|---|---|---|
| `spec/06-contradictions-ambiguities.md`:78 | ```ActorStatus` is declared seven times`` | C-64, the row this entry backs |
| `spec/09-unresolved-decisions.md`:137 | ``### U-27 — Which `ActorStatus` shape governs`` | the decision this entry escalates to; added by the same sweep |
| `req/03-ambiguous.md`:301 | ``### AMB-39 — `ActorStatus` is declared seven times`` | the ambiguity row this entry backs |

### The collision

X-21 records `ActorStatus` as declared twice (L9411 and L10346). A full sweep finds SEVEN declarations — L9411, L10346, L10866, L21234, L23306, L23793 and the turn-[20] restatement at L10866 — in THREE distinct shapes. Shape (i), L9411/L10346: `Pending(PendingEffect), Blocked(Continuation)` — a tuple `Pending` and a payload-bearing `Blocked`. Shape (ii), L21234: `Pending { effect: EffectRequest, continuation: Continuation, reservation: ReservedCapacity }, Blocked(Continuation)` — a three-field struct `Pending`. Shape (iii), L23306/L23793: `Pending { effect: EffectRequest, reservation: ReservedCapacity }, Blocked` — `continuation` dropped from `Pending` and `Blocked` reduced to a unit variant. The `Continuation` payload therefore moves: inside `Blocked` in shapes (i) and (ii), inside `Pending` in shape (ii) as well, and absent from both in shape (iii).

### Why it matters

`ActorStatus` is the state that decides whether an actor is resumable, and the location of its `Continuation` payload is exactly what a scheduler needs in order to resume it. Shape (iii) carries no `Continuation` at all, so an actor in `Pending { effect, reservation }` cannot be resumed from its own status — the continuation has to live somewhere else — `ActorState.eval.continuation` (T-37, T-32) — and the source never says where. That is a semantic gap, not a naming one, and it is downstream of the `Running`/`Active` split X-21 already records: an implementer who normalizes the name without also picking a shape gets a status type that cannot resume its own actors, and every replay test built on it fails for a reason the naming fix appears to have solved. The seven-declaration count also bears on X-21's disposition, which was written against two and so understates how much of the source has to be reconciled.

### Disposition

REPORTED, not resolved, with X-21 kept intact: X-21's `Running`/`Active` finding is correct and stands, and this entry corrects its population count rather than superseding it, because the two findings are about different things (naming versus shape) and merging them would lose one. T-35's note is updated in place to say seven declarations in three shapes and to cross-link both entries. No shape is nominated — shapes (i) to (iii) are successive turns' views and the source gives no precedence rule for `ActorStatus` (U-08 covers `Fault` only). All three shapes are given verbatim in T-35's `supersedes`/`shape` so none is lost.

### Decision needed

Yes — `spec/09` U-27: which shape governs, and where shape (iii)'s continuation lives — the actor table, the WAL, or a `ContinuationFrame`.

## X-11

**The symbol `A` denotes Authority and, subscripted, an actor's state**

- **Kind:** `SYMBOL-OVERLOAD` — one mathematical symbol, two or more denotations
- **Severity:** MINOR
- **Terms affected:** T-10 `Authority`, T-37 `ActorState`

### Evidence (frozen source)

| Line | Text at that line | What it denotes there |
|---|---|---|
| `Red-on-Rust.md` L6146 | `Authority =` | turn [10]: `A` = Authority |
| `Red-on-Rust.md` L8666 | `$$ A_a = \langle e, \rho, \kappa, \mathcal{H}, C, R, W, \text{mailbox}, \text{status} \rangle $$` | turn [16]: `A_a` = the ActorState of actor a |
| `Red-on-Rust.md` L340 | `the block in $A_A$, serializes the data, and reconstructs an isomorphic block in $A_B$` | turn [1]: `A_A`/`A_B` = actor A's / actor B's state |
| `Red-on-Rust.md` L6501 | `pub struct Authority<S, Q, R, L> {` | turn [11]: `Authority` as a Rust type |

### The collision

`A` is Authority in the capability algebra and, subscripted, an actor's local state in the operational semantics — with turn [1] using capital subscripts (`A_A`, `A_B`) and turn [16] using a lower-case one (`A_a`). Inside `A_a`'s own definition, `C` and `R` are budget components (X-08, X-09), so a single formula overloads three letters at once.

### Why it matters

`derive(A,C) ⪯ A` (authority) and `G[a ↦ A_a[…]]` (actor state) are the two most quoted formulae in their respective modules. Reading `A_a` as 'the authority of a' would make the transition rules claim that every step rewrites an authority — the opposite of the no-amplification law.

### Disposition

Both recorded; neither renamed. The dictionary fixes prose: 'the authority A' vs 'the actor state A_a'. Subscript case is preserved verbatim in quotations (`A_A`/`A_B` in turn [1], `A_a` from turn [15] on) and flagged as superseded notation, not corrected.

## X-14

**The symbol `H` denotes the effect journal while calligraphic `ℋ` denotes the heap**

- **Kind:** `SYMBOL-OVERLOAD` — one mathematical symbol, two or more denotations
- **Severity:** MINOR
- **Terms affected:** T-23 `EffectJournal`, T-37 `ActorState`, T-45 `WAL`

### Evidence (frozen source)

| Line | Text at that line | What it denotes there |
|---|---|---|
| `Red-on-Rust.md` L26134 | `- \(H\) = durable host-effect journal.` | turn [33]: `H` = the EffectJournal |
| `Red-on-Rust.md` L718 | `$$ \Sigma = \langle P, \rho, \kappa, \mathcal{H}, \phi, \mathcal{E} \rangle $$` | turn [2]: calligraphic `ℋ` = the agent's isolated heap/arena |
| `Red-on-Rust.md` L724 | `*   $\mathcal{H}$: The agent's isolated heap/arena.` | turn [2] defines `ℋ` as the heap |
| `Red-on-Rust.md` L8666 | `A_a = \langle e, \rho, \kappa, \mathcal{H}, C, R, W` | turn [16]: `ℋ` inside the actor state |

### The collision

Plain `H` is the durable effect journal; calligraphic `ℋ` is the per-actor heap, used 86 times including inside the frozen actor-state definition. The distinction exists but rests entirely on a font change, and the two denote a durable record family and an in-memory arena respectively.

### Why it matters

spec/05 §4 lists `H` as an alias of the effect journal without noting that `ℋ` is the heap; a reader applying that alias to the transition rules would read the actor's heap as a journal. Low probability, high confusion cost, and trivially avoided by naming the object.

### Disposition

Both recorded; neither renamed. The dictionary requires prose to name the object ('the journal H', 'the heap ℋ') and preserves the calligraphic form verbatim in every quotation. spec/05's alias row is annotated accordingly (X-41 family).

## X-15

**The symbol `B` denotes the Budget and, in turn [1], a Block**

- **Kind:** `SYMBOL-OVERLOAD` — one mathematical symbol, two or more denotations
- **Severity:** MINOR
- **Terms affected:** T-24 `Budget`, T-01 `Block`

### Evidence (frozen source)

| Line | Text at that line | What it denotes there |
|---|---|---|
| `Red-on-Rust.md` L7129 | `$$ B = \langle C, R, W \rangle $$` | turn [13]: `B` = Budget |
| `Red-on-Rust.md` L132 | `generates a new block $B$ utilizing only the sanctioned vocabulary` | turn [1]: `B` = a Block |
| `Red-on-Rust.md` L7171 | `f = (\lambda \bar{x}. e_{body})^{\Phi_f}_{B_f}` | turn [13]: `B_f` = a closure's budget annotation |
| `Red-on-Rust.md` L2217 | `B_{\text{child}} \leq B_{\text{alloc}}` | turn [4]: `B_child`, `B_alloc` = spawn budgets |

### The collision

`B` is the budget triple in every frozen-era formula and a block in the turn-[1] epistemic-loop narrative. The subscripted family (`B_f`, `B_max`, `B_child`, `B_alloc`, `B_parent_remainder`) is uniformly budget-valued.

### Why it matters

The turn-[1] use predates the typed `Block` and is narrative, so the practical risk is confined to reading early text. It matters for one reason: `Block` is the untrusted input of N-01, and a reader who carries `B` = block into the budget formulae would read `B = ⟨C,R,W⟩` as a decomposition of untrusted program data.

### Disposition

Both recorded; neither renamed. `B` is canonical for Budget from turn [13] onward; the turn-[1] block usage is marked superseded narrative and quoted only with its provenance. Prose uses `Block`, never `B`, for program data.

## X-23

**`RunState::Faulted` vs `ActorStatus::Fault`: near-homonym variants of two distinct enums**

- **Kind:** `TYPE-HOMONYM` — one name, two or more incompatible type declarations
- **Severity:** MINOR
- **Terms affected:** T-35 `ActorStatus`, T-36 `RunState`, T-70 `Fault`
- **Previously registered as:** `C-18`, `AMB-05`

### Evidence (frozen source)

| Line | Text at that line | What it denotes there |
|---|---|---|
| `Red-on-Rust.md` L25532 | `Faulted,` | turn [32]: the `RunState` variant is spelled `Faulted` |
| `Red-on-Rust.md` L9416 | `Fault(Fault),` | turn [17]: the `ActorStatus` variant is spelled `Fault` and carries a `Fault` |
| `Red-on-Rust.md` L23793 | `pub enum ActorStatus {` | turn [30]: the enum whose fault variant is `Fault` |
| `Red-on-Rust.md` L23806 | `pub enum Fault {` | turn [30]: and `Fault` is ALSO the name of the payload type |

### The collision

Three related names differ by one suffix: `RunState::Faulted` (a scheduler-visible state), `ActorStatus::Fault` (a machine-visible state), and `Fault` (the taxonomy type carried by the latter). The source keeps all three, and C-18 records that the mapping between the two enums is 'implied but not stated as a table'.

### Why it matters

Faults are compared by the differential comparator (R-REF-05 lists faults among normalized observations). Without a stated mapping, production and reference may report the same condition as `RunState::Faulted` and `ActorStatus::Fault(f)` respectively and produce a divergence that adjudication cannot classify — it is neither a production nor a reference defect, but an unstated correspondence.

### Disposition

All three names recorded exactly as spelled; none renamed and none unified. The dictionary requires prose to name the enum (`RunState::Faulted` vs `ActorStatus::Fault`) and reports the missing mapping table as part of C-18's residual, not as a new decision.

## X-37

**`Authority` is declared seven times and `Frame` eleven times, with an elided `AuthorityNode` between them**

- **Kind:** `TYPE-HOMONYM` — one name, two or more incompatible type declarations
- **Severity:** MINOR
- **Terms affected:** T-10 `Authority`, T-11 `AuthorityNode`, T-13 `CapabilityKernel`, T-33 `Frame`, T-14 `CapabilityContext`
- **Previously registered as:** `AMB-26`, `U-02`

### Evidence (frozen source)

| Line | Text at that line | What it denotes there |
|---|---|---|
| `Red-on-Rust.md` L488 | `struct Authority {` | turn [2] declaration |
| `Red-on-Rust.md` L918 | `pub(crate) struct Authority {` | turn [3] declaration |
| `Red-on-Rust.md` L3591 | `pub struct Authority {` | turn [7] declaration |
| `Red-on-Rust.md` L6501 | `pub struct Authority<S, Q, R, L> {` | turn [11] declaration — the generic form |
| `Red-on-Rust.md` L12453 | `pub enum Frame {` | turn [21]: first of eleven `Frame` declarations |
| `Red-on-Rust.md` L23830 | `pub enum Frame {` | turn [30]: the frozen-era `Frame` declaration |
| `Red-on-Rust.md` L39373 | `pub(crate) struct AuthorityNode { ... }` | turn [58]: fields ELIDED |

### The collision

The authority type is declared seven times across turns [2]-[11] (v0.1 → v0.2 → v0.3 of the capability algebra), the continuation frame enum eleven times across turns [21]-[30], and the kernel-private `AuthorityNode` once with its fields elided. AMB-26 records the eleven `Frame` declarations and the `Authority`/`AuthorityNode`/`CapabilityKernel` interchange; the seven `Authority` declarations are not enumerated anywhere.

### Why it matters

A closed variant set is a requirement, not a preference: R-CEK-03 freezes the frame set, and eleven declarations give eleven candidate sets. The differential comparator observes faults and continuations, so two implementations choosing different declarations among the eleven would diverge without either being wrong. `AuthorityNode`'s elided fields mean the kernel's private state has no frozen shape at all, which U-02 needs in order to freeze a canonical encoding.

### Disposition

All declaration sites recorded; none renamed and none deleted. The dictionary points at the algebra version that governs (v0.2, turn [11], per spec/05 §1) and requires an explicit decision identifying WHICH of the eleven `Frame` declarations is the frozen set. AMB-26 is linked, not duplicated.

### Decision needed

Yes — identify the single frozen `Frame` declaration and state `AuthorityNode`'s fields (or confirm they are deliberately kernel-private and unencodable).

## X-41

**spec/01 and mod/02 reproduce one of three pipeline orderings, in an order the frozen structs contradict**

- **Kind:** `ALIAS-DEFECT` — the canonicalization layer states an alias/definition the source does not support
- **Severity:** MINOR
- **Terms affected:** T-03 `ParsedBlock`, T-04 `ValidatedPlan`, T-06 `ExecutablePlan`, T-07 `NormalizedAST`, T-08 `PlanIR`

### Evidence (frozen source)

| Line | Text at that line | What it denotes there |
|---|---|---|
| `Red-on-Rust.md` L864 | `pub struct ParsedBlock { ast: NormalizedAST }` | `NormalizedAST` is a FIELD of stage 1, not a stage before it |
| `Red-on-Rust.md` L865 | `pub struct ValidatedPlan { ir: PlanIR, effects: EffectSet }` | `PlanIR` is a FIELD of stage 2, not a stage after it |
| `Red-on-Rust.md` L39271 | `NormalizedAST` | the turn-[58] ordering this rendering follows |

### Evidence (canonicalization layer)

| File:line | Text at that line | Note |
|---|---|---|
| `spec/01-canonical-specification.md`:479 | `Block → parse → NormalizedAST` | the single-ordering rendering |
| `mod/02-compiler.md`:45 | `Block → parse → NormalizedAST` | the same rendering repeated in the module layer |

### The collision

The canonicalized crate contract renders the pipeline as `Block → parse → NormalizedAST → ValidatedPlan → PlanIR → capability analysis → resource analysis → ExecutablePlan`, faithfully following the turn-[58] diagram. That ordering places `NormalizedAST` before `ValidatedPlan` and `PlanIR` after it, whereas the frozen struct declarations make `NormalizedAST` the CONTENT of `ParsedBlock` and `PlanIR` the CONTENT of `ValidatedPlan`. It also omits two declared stages and is silent about the two other orderings (X-02).

### Why it matters

The rendering is faithful to one source site, so it is not an error of transcription — but as the only pipeline statement in the canonical specification it presents one of three contradictory orderings as settled, and inverts the type/field relationship of two names. An implementer reading spec/01 and mod/02 alone would build four stages where the structs declare four different ones.

### Disposition

The rendering is left in place (it is faithful to L39265-39280 and removing it would silently drop source text); this entry records that it is one of three orderings, that two names in it are field types rather than stages, and that the collision is X-02. Both spec/01 and mod/02 are annotated with a pointer to X-02 rather than edited.

## X-42

**`LogicalTime` is glossed in the source as 'a logical clock or deterministic timestamp'**

- **Kind:** `SCOPE-DRIFT` — a name's scope changed between frozen eras without retraction
- **Severity:** MINOR
- **Terms affected:** T-28 `LogicalTime`, T-27 `Deadline`

### Evidence (frozen source)

| Line | Text at that line | What it denotes there |
|---|---|---|
| `Red-on-Rust.md` L6437 | `It is an explicit component of the machine state $\Sigma$ (e.g., a logical clock or deterministic timestamp)` | turn [10]: three names for one object in one sentence |
| `Red-on-Rust.md` L9137 | `pub struct LogicalTime(pub u64);` | turn [17]: the frozen type |
| `Red-on-Rust.md` L5829 | `logical time` | turn [9]: the frozen prose name |

### The collision

The frozen type is `LogicalTime(pub u64)` and the frozen symbol is `t`, but the source glosses the same object as 'a logical clock' and 'a deterministic timestamp' in the sentence that establishes it is not host-fetched. spec/05 §2 lists both glosses as aliases.

### Why it matters

'Clock' implies a device that can be read, which is precisely what R-CAP-09 prohibits: logical time is a state component advanced by `δ_t`, never read from the host. 'Timestamp' implies wall-clock provenance. Both aliases invite the prohibited reading, and 'wall-clock time as semantic machine state' is one of the sixteen prohibited shortcuts (R-CLAIM-02).

### Disposition

The glosses are recorded as forbidden PROSE substitutes (they are not identifiers, so nothing is renamed): canonical prose is 'logical time' or `LogicalTime`. The source sentence is quoted verbatim wherever it is cited, with its provenance, so the glosses remain traceable.

## X-43

**`ReplayHost`'s trace field is `recorded_receipts` in one frozen form and `trace` in the other**

- **Kind:** `FIELD-SET` — same type name, different field sets or field names
- **Severity:** MINOR
- **Terms affected:** T-42 `ReplayHost`, T-19 `EffectReceipt`, T-20 `EffectId`
- **Previously registered as:** `C-22`

### Evidence (frozen source)

| Line | Text at that line | What it denotes there |
|---|---|---|
| `Red-on-Rust.md` L24011 | `pub struct ReplayHost {` | turn [30]: the `HashMap` form |
| `Red-on-Rust.md` L24012 | `pub recorded_receipts: HashMap<EffectId, EffectReceipt>,` | turn [30]: field `recorded_receipts`, keyed by id |
| `Red-on-Rust.md` L34498 | `pub struct ReplayHost {` | turn [46]: the frozen ordered form |
| `Red-on-Rust.md` L34499 | `trace: Vec<EffectReceipt>,` | turn [46]: field `trace`, ordered |

### The collision

C-22 resolves the mechanism (unordered map → ordered trace) but the field NAME also changes, from `recorded_receipts: HashMap<EffectId, EffectReceipt>` to `trace: Vec<EffectReceipt>`. The rename is not cosmetic: a map keyed by `EffectId` makes id lookup the primitive operation, while a vector makes POSITION the primitive, which is what allows the digest check to detect a divergent program consuming receipts out of order.

### Why it matters

The ordered form's whole point is that the next receipt is a function of position, not of the requested id — 'a corrupted or divergent program could issue a different effect and simply consume the next recorded result' (L1390) is the failure the id-keyed form permits. Keeping the `recorded_receipts` name would carry the keyed-lookup mental model into an ordered implementation.

### Disposition

Both field names recorded verbatim; neither renamed. C-22 is linked as the mechanism resolution; this entry adds the field-name change and states why the ordered field's name matters to the security property.

## X-44

**Three cost types and five cost functions: `Cost`, `EffectCost`, `ResourceUsage`, `CostModel`, `cost_C`/`cost_io`/`cost_res`**

- **Kind:** `TYPE-HOMONYM` — one name, two or more incompatible type declarations
- **Severity:** MINOR
- **Terms affected:** T-22 `EffectCost`, T-29 `CostModel`, T-16 `Effect`, T-24 `Budget`, T-25 `Consumable`, T-26 `Reserved`
- **Previously registered as:** `AMB-23`

### Evidence (frozen source)

| Line | Text at that line | What it denotes there |
|---|---|---|
| `Red-on-Rust.md` L9188 | `pub struct Cost {` | turn [17]: `Cost { consumable, reserved }` — `Effect.cost` |
| `Red-on-Rust.md` L6545 | `pub cost: ResourceUsage, // Static cost of this specific effect` | turn [11]: the same field's type named `ResourceUsage` |
| `Red-on-Rust.md` L21390 | `pub struct EffectCost {` | turn [29]: the split issue/complete/reserve model |
| `Red-on-Rust.md` L10168 | `pub trait CostModel {` | turn [18]: the op→cost mapping contract |
| `Red-on-Rust.md` L8707 | `C' = C - \text{cost}_C(\text{let})` | turn [15]: `cost_C`, the consumable cost function |
| `Red-on-Rust.md` L7381 | `C - \text{cost}_{\text{io}}(\text{receipt}.v), R - \text{cost}_{\text{res}}(E)` | turn [13]: `cost_io` and `cost_res`, two more cost functions |

### The collision

Cost is expressed by three type names (`Cost`, `ResourceUsage`, `EffectCost`), one trait (`CostModel` with `cost_c`/`cost_r`) and at least three mathematical functions (`cost_C`, `cost_io`, `cost_res`) plus `cost_consumable`/`cost_reserved` (L7151). `Cost` and `ResourceUsage` name the same field type in different eras; `Cost` and `EffectCost` are different types with overlapping purpose; and the math functions are subscripted inconsistently (`cost_C` vs `cost_c`).

### Why it matters

`R-BUDGET-07` freezes `CostModel` + `Cost` as the op→cost contract, while `R-EFFECT-05` freezes `EffectCost` as the split lifecycle model. An implementer must know which one an effect carries: `Effect.cost` is a `Cost`, not an `EffectCost`, so escrowing `complete_max` requires a second lookup that the type names do not make obvious. AMB-23 records `EffectCost`'s field-order ambiguity; the three-type spread is not recorded.

### Disposition

All names recorded; none renamed. The dictionary separates them by role: `Cost` = the static consumable/reserved pair carried by `Effect`; `EffectCost` = the lifecycle split (issue/complete_max/reserve); `ResourceUsage` = superseded name of `Cost`; `CostModel` = the mapping contract; the `cost_*` symbols = per-transition cost functions in the operational rules.

## X-46

**`GlobalState` vs `GlobalConfig`**

- **Kind:** `TYPE-HOMONYM` — one name, two or more incompatible type declarations
- **Severity:** MINOR
- **Terms affected:** T-38 `GlobalState`
- **Previously registered as:** `C-42`
- **Provenance:** extends or corrects an existing register entry; not a new finding.

### Evidence (frozen source)

| Line | Text at that line | What it denotes there |
|---|---|---|
| `Red-on-Rust.md` L8653 | `## 1. Global Configuration and State Definitions` | turn [15]: 'Global Configuration' |
| `Red-on-Rust.md` L11061 | `fn step_request(actor: &mut ActorState, machine: &mut GlobalConfig, expr: Expr)` | turn [18]: the Rust name `GlobalConfig` |
| `Red-on-Rust.md` L24156 | `pub struct GlobalState {` | turn [31]: the frozen Rust name `GlobalState` |
| `Red-on-Rust.md` L10128 | ``**`GlobalConfig`, `ActorState`, `Budget`, `CapabilityKernel`, `Effect`, `EventLog``` | turn [18]: `GlobalConfig` listed as a first-milestone artifact |

### The collision

The global machine record is `GlobalConfig` in the v0.3/turn-[15]-[18] era and `GlobalState` from turn [31] on. C-42 records this as MINOR resolved-by-later-text and spec/05 §6.3 makes `GlobalState` canonical.

### Why it matters

Resolved, but it is retained here because the superseded name appears in a milestone artifact list (L10128) that an implementer follows for M0, and because `GlobalConfig`'s shape is the 6-component v0.3 configuration (X-18) rather than the frozen `GlobalState` shape — so the name change carries a shape change that C-42 does not mention.

### Disposition

`GlobalState` canonical (per C-42 and spec/05 §6.3); `GlobalConfig` recorded as superseded and forbidden in current prose, retained in quotations. Neither is renamed. The associated shape change is cross-referenced to X-18.

## X-48

**'Reference machine' (pre-15C) and 'reference model' (15C) denote different objects**

- **Kind:** `SCOPE-DRIFT` — a name's scope changed between frozen eras without retraction
- **Severity:** MINOR
- **Terms affected:** T-58 `ReferenceModel`, T-65 `Implementation`
- **Previously registered as:** `C-33`

### Evidence (frozen source)

| Line | Text at that line | What it denotes there |
|---|---|---|
| `Red-on-Rust.md` L10128 | `Once that reference machine passes the algebraic/property tests` | turn [18]: 'reference machine' = the FIRST boring production milestone |
| `Red-on-Rust.md` L15871 | `Keep the reference machine maximally obvious.` | turn [23]: same sense |
| `Red-on-Rust.md` L16403 | `The reference machine must remain maximally transparent` | turn [24]: same sense |
| `Red-on-Rust.md` L35283 | `Phase 15C defines an independently implemented executable reference model` | turn [48]: 'reference model' = the INDEPENDENT oracle, zero shared logic |

### The collision

Before Phase 15C, 'the reference machine' means the first deliberately boring implementation of the production semantics — the thing the live host is later bolted onto. From 15C on, 'the reference model' means the INDEPENDENT comparator that must share zero core transition logic with production. The two are opposite in the one respect that matters: the first is the production baseline, the second must not be.

### Why it matters

R-SCOPE-04 requires zero shared core logic between production and reference. An implementer who reads 'reference machine' in the turn-[18]-[24] sense and treats that artifact as the 15C oracle gets a tautological differential test — the exact oracle-collapse the 15C.38 anti-oracle-collapse rules prohibit. C-33 covers a related point (the reference 'distinct language' suggestion) but not this sense shift.

### Disposition

Both senses recorded with their eras; neither phrase renamed. The dictionary fixes `ReferenceModel` (T-58) as the canonical name for the 15C independent oracle and marks 'reference machine' as superseded prose for the first production milestone, quotable only with its turn provenance.

## X-49

**Three identifier namespaces begin with `M`: milestones `M0`-`M11`, mutations `M001`-`M018`, and the memory symbol `M`**

- **Kind:** `SYMBOL-OVERLOAD` — one mathematical symbol, two or more denotations
- **Severity:** MINOR
- **Terms affected:** T-26 `Reserved`, T-60 `Mutation`

### Evidence (frozen source)

| Line | Text at that line | What it denotes there |
|---|---|---|
| `Red-on-Rust.md` L40763 | `## M0 — Workspace` | turn [58]: milestone identifiers `M0`…`M11` |
| `Red-on-Rust.md` L38477 | `M001 reverse argument evaluation` | turn [54]: mutation identifiers `M001`…`M018` |
| `Red-on-Rust.md` L7131 | `$R = \langle M, S \rangle$` | turn [13]: `M` = memory bytes |
| `Red-on-Rust.md` L658 | `(B_0,\kappa_0,F_0,M_0)` | turn [2]: `M_0` = a replay-tuple component |

### The collision

`M0` is a milestone, `M001` is a mutation, `M` is the memory dimension of Reserved, and `M_0` is a component of the turn-[2] replay tuple. spec/00 §3 registers `M-NN` and `M0NN` as separate identifier schemes, which is the correct disambiguation, but the mathematical `M` is not covered by that scheme.

### Why it matters

The practical hazard is in verification text: 'M0 gate' and 'M001 kill' can appear in the same sentence as a budget statement about `M`, and the mutation registry ID `M007` (budget escrow) is precisely a mutation about the budget that `M` denotes a component of.

### Disposition

All three namespaces recorded; none renamed — `M0NN` and `M-NN` are frozen identifier schemes and `M` is a frozen mathematical symbol. The dictionary requires the full form in prose ('milestone M0', 'mutation M001', 'the memory dimension M') and notes that spec/00 §3 already separates the two ID schemes.

## X-51

**spec/05's trait list omits `CanonicalSerialize`, the trait that carries the format**

- **Kind:** `ALIAS-DEFECT` — the canonicalization layer states an alias/definition the source does not support
- **Severity:** MINOR
- **Terms affected:** T-63 `CanonicalPayload`, T-62 `CanonicalEnvelope`, T-48 `Snapshot`

### Evidence (frozen source)

| Line | Text at that line | What it denotes there |
|---|---|---|
| `Red-on-Rust.md` L27685 | `pub trait CanonicalSerialize {` | turn [34]: the persistence-era trait |
| `Red-on-Rust.md` L28296 | `pub trait CanonicalSerialize {` | turn [36]: re-declared, with the L28298 doc comment |
| `Red-on-Rust.md` L29979 | `pub trait CanonicalPayload: Sized {` | turn [41]: the frozen 15A trait |
| `Red-on-Rust.md` L29178 | `pub trait CanonicalEncode {` | turn [40]: the frozen encode half |
| `Red-on-Rust.md` L29183 | `pub trait CanonicalDecode: Sized {` | turn [40]: the frozen decode half |
| `Red-on-Rust.md` L27061 | `D_S=H(CanonicalSerialize(GlobalState)).` | turn [33]: `CanonicalSerialize` used as a MATH FUNCTION symbol |

### Evidence (canonicalization layer)

| File:line | Text at that line | Note |
|---|---|---|
| `spec/05-terminology.md`:62 | ``Traits: `CanonicalPayload` / `CanonicalEncode` / `CanonicalDecode``` | the incomplete trait list |

### The collision

The glossary row for canonical encoding lists the traits as `CanonicalPayload` / `CanonicalEncode` / `CanonicalDecode` and puts `CanonicalSerialize` only in the row's canonical-term position, without recording that it is a separately declared trait (twice) whose doc comment is the site of the X-50 format collision, and that it also appears as a mathematical function symbol in the state-digest formula.

### Why it matters

`CanonicalSerialize` is infallible (`-> Vec<u8>`) while the frozen `CanonicalEncode`/`CanonicalDecode` pair is fallible (`Result<_, CanonicalError>`). R-CANON-02 and the strict-decoding rejection classes (R-PERSIST-02) are only expressible with the fallible pair, so which trait family is frozen decides whether decode failures are representable at all. The source's own checklist notes `CanonicalDecode` 'is declared but not implemented' (L29601).

### Disposition

All four trait names recorded, plus the math-function use; none renamed. The dictionary separates the infallible serialization trait (turn-[34]/[36] era, carrier of the X-50 defect) from the frozen fallible codec pair, and corrects the glossary row to list all four with their eras.

## X-56

**The byte 0x00 carries four distinct meanings across four encoding layers**

- **Kind:** `SYMBOL-OVERLOAD` — one mathematical symbol, two or more denotations
- **Severity:** MINOR
- **Terms affected:** T-62 `CanonicalEnvelope`, T-63 `CanonicalPayload`, T-31 `Value`
- **Previously registered as:** `C-02`

### Evidence (frozen source)

| Line | Text at that line | What it denotes there |
|---|---|---|
| `Red-on-Rust.md` L29951 | `pub const TAG_VALUE: u8 = 0x00;` | layer 1: the ENVELOPE type tag meaning 'what follows is a `Value`' |
| `Red-on-Rust.md` L29961 | `pub const DISC_UNIT: u8 = 0x00;` | layer 2: the `Value` VARIANT discriminant meaning 'Unit' |
| `Red-on-Rust.md` L29273 | `const TYPE_TAG: u8 = 0x00; // Envelope for the enum itself` | turn [40]: layer 1 restated, with the comment that makes the layering explicit |
| `Red-on-Rust.md` L28750 | ``\| `bool` \| 1 byte (`0x00` for false, `0x01` for true) \|`` | turn [38]: layer 3: 0x00 as the value `false` |
| `Red-on-Rust.md` L28756 | ``*   **`Option<T>`**: 1 byte tag (`0x00` = None, `0x01` = Some)`` | turn [38]: layer 4: 0x00 as `None` |
| `Red-on-Rust.md` L28757 | ``*   **`Result<T, E>`**: 1 byte tag (`0x00` = Ok, `0x01` = Err)`` | turn [38]: layer 4: 0x00 as `Ok` |
| `Red-on-Rust.md` L33182 | `0x00 => Ok(Value::Bool(false)),` | turn [45]: layer 3 inside a layer-2 arm |

### The collision

0x00 is the envelope type tag for `Value`, the `Value::Unit` discriminant, the encoding of `false`, and the encoding of `None`/`Ok`. Encoding `Value::Unit` therefore yields a byte string in which 0x00 appears as the type tag, inside the big-endian length, and as the discriminant. The turn-[38] table adds a fifth use at a superseded width, `Value::Unit: Tag 0x00000000` (L28760).

### Why it matters

The format is positionally decodable — the envelope fixes where each byte sits — so this is not a correctness defect. It is a reading hazard of exactly the kind C-02 warns about: an implementer who treats the type-tag registry and the discriminant table as one namespace (both are called 'tags', both begin at 0x00, and both are headed 'Frozen') will accept `0x00` as `Value::Unit` at the envelope layer and mis-frame every object. R-CANON-04's strict rejection of an unknown `type_tag` depends on the two namespaces staying separate.

### Disposition

All uses recorded verbatim; no tag renamed. The dictionary requires that any prose citing a tag byte name its layer (X-54's two TERMS), and records that the turn-[38] `0x00000000` width is superseded by the `u8` tags per X-50. C-02 is linked as the register entry that already separates standalone tags from discriminants.

## X-60

**req/00-method §5.4 asserts there is no `15C.1` heading; there is one, and 15C spans two heading levels**

- **Kind:** `PROVENANCE-DEFECT` — a citation in the canonicalization layer does not point at the text it claims
- **Severity:** MINOR
- **Terms affected:** T-58 `ReferenceModel`, T-64 `Specification`

### Evidence (frozen source)

| Line | Text at that line | What it denotes there |
|---|---|---|
| `Red-on-Rust.md` L35281 | `## 15C.1 Purpose` | turn [48]: `15C.1` EXISTS, as an H2 |
| `Red-on-Rust.md` L35326 | `# 15C.2 Non-Goals` | turn [48]: `15C.2` onward are H1 |
| `Red-on-Rust.md` L37151 | `# 15C.46 Phase Boundary` | turn [48]: the last of 46 numbered sections |

### Evidence (canonicalization layer)

| File:line | Text at that line | Note |
|---|---|---|
| `req/00-method.md`:220 | ``there is no `# 15C.1` heading`` | the false assertion, corrected by this dictionary |

### The collision

req/00-method §5.4 states 'The turn is numbered 15C.2…15C.46 — there is no `# 15C.1` heading; L35272–35325 is an unnumbered preamble'. Phase 15C in fact contains 46 numbered sections, 15C.1 through 15C.46: 45 at heading level H1 and one — `## 15C.1 Purpose` at L35281 — at H2, inside the range the method note calls an unnumbered preamble. The claim is true only for the literal string `# 15C.1` at H1, and the note's own accounting ('All 45 now carry at least…') leaves 15C.1's requirements unattributed.

### Why it matters

The method note is the anchor-of-record for the requirement registry: §5.1's corrected line anchors and §5.3's carried-forward anchors are what `req/_validate.py` checks against. A section believed not to exist is a section whose obligations are not registered, so REQ-REF-001/002/006 — which the note says cite L35281-35310 — are attributed to an 'unnumbered preamble' rather than to 15C.1. The inconsistent heading level (15C.1 at H2, 15C.2-15C.46 at H1) is the source-side reason the mistake was easy to make, and it also means any heading-level-driven extraction of 15C misses its first section.

### Disposition

req/00-method §5.4 is corrected in this pass to record 46 numbered sections at two heading levels, with L35281 cited as `## 15C.1 Purpose`. No requirement ID is renumbered and no obligation is re-homed; the correction is additive and is recorded here so the change to a method note is not silent.

## X-61

**spec/09 U-15 remains an open decision on a premise req/03 AMB-15 has withdrawn as false**

- **Kind:** `PROVENANCE-DEFECT` — a citation in the canonicalization layer does not point at the text it claims
- **Severity:** MINOR
- **Terms affected:** T-45 `WAL`, T-47 `WalRecord`, T-19 `EffectReceipt`, T-20 `EffectId`, T-51 `ReconciliationOutcome`
- **Previously registered as:** `U-15`, `AMB-15`, `U-06`

### Evidence (frozen source)

| Line | Text at that line | What it denotes there |
|---|---|---|
| `Red-on-Rust.md` L26593 | `pub enum ReconciliationOutcome {` | turn [32]: the variant set IS enumerated |
| `Red-on-Rust.md` L26594 | `Completed(EffectReceipt),` | variant 1 |
| `Red-on-Rust.md` L26595 | `NotExecuted,` | variant 2 |
| `Red-on-Rust.md` L26596 | `Indeterminate,` | variant 3 |
| `Red-on-Rust.md` L38211 | `Completed\Rightarrow Issued` | turn [54]: classification 1 of the three the enum matches |
| `Red-on-Rust.md` L38232 | `Indeterminate` | turn [54]: classification 2 |
| `Red-on-Rust.md` L38243 | `NotExecuted` | turn [54]: classification 3 |
| `Red-on-Rust.md` L35132 | `EffectReconciled { id: EffectId, digest: EffectDigest, outcome: ReconciliationOutcome },` | turn [47]: the frozen WAL record that carries it |

### Evidence (canonicalization layer)

| File:line | Text at that line | Note |
|---|---|---|
| `spec/09-unresolved-decisions.md`:73 | ``the variant set of `ReconciliationOutcome` is never enumerated`` | the false premise, corrected by this dictionary |
| `req/03-ambiguous.md`:127 | ```spec/09` U-15's claim that the variants are unspecified is likewise false`` | the earlier withdrawal that spec/09 never absorbed |

### The collision

spec/09 U-15 states that 'the variant set of `ReconciliationOutcome` is never enumerated (beyond the classification of interrupted effects as `Indeterminate`)' and asks for 'the variant set + per-class admissibility'. The variant set is enumerated at L26593-26597 as a closed three-variant set, and it matches exactly the three classifications the turn-[54] recovery text names. req/03 AMB-15 has already withdrawn the same claim and says so explicitly: '`spec/09` U-15's claim that the variants are unspecified is likewise false.' spec/09 was never updated.

### Why it matters

U-15 is a live entry in the unresolved-decisions register, so it advertises an open architectural decision that has no open content. Two registers in the same canonicalization layer now disagree about whether the question is settled, and the one that is wrong (spec/09) is the one a reader consults for open decisions. Worse, U-15's proposed variants — `Executed(result)`, `PartiallyExecuted` — do not exist in the frozen set, so implementing to U-15 would widen a closed enum and break `WalRecord::EffectReconciled` decoding against recorded traces.

### Disposition

spec/09 U-15 is corrected in this pass to the closed three-variant set with the L26593-26597 citation, and narrowed to the part that IS genuinely open: per-class admissibility under U-06, and the turn-[32] constraint that 'only a host protocol capable of answering authoritatively may produce `NotExecuted` or `Completed`' (L26601). AMB-15 is linked as the prior withdrawal. No variant is renamed; the correction removes a false premise rather than changing the type.

## X-62

**req/03 AMB-25 lists `PlannerState`, an identifier that does not occur in the source**

- **Kind:** `PHANTOM-IDENTIFIER` — a register names an identifier that occurs nowhere in the frozen source
- **Severity:** MINOR
- **Terms affected:** T-02 `PlanProposal`, T-06 `ExecutablePlan`, T-08 `PlanIR`, T-01 `Block`, T-55 `PlannerAccepted`
- **Previously registered as:** `AMB-25`

### Evidence (frozen source)

| Line | Text at that line | What it denotes there |
|---|---|---|
| `Red-on-Rust.md` L865 | `pub struct ValidatedPlan { ir: PlanIR, effects: EffectSet }` | one of the four plan-family names that DO occur |
| `Red-on-Rust.md` L27175 | `pub struct PlanProposal {` | turn [33]: the name that occupies the role AMB-25 assigns to `PlannerState` |

### Evidence (canonicalization layer)

| File:line | Text at that line | Note |
|---|---|---|
| `req/03-ambiguous.md`:195 | ```PlannerState``` | the phantom identifier, removed by this dictionary |

### The collision

AMB-25's statement is '`Plan`, `PlanProposal`, `PlanIR`, `ExecutablePlan`, `PlannerState` are used with overlapping meanings.' The identifier `PlannerState` occurs NOWHERE in `Red-on-Rust.md` (L1-42312) — not as a type, field, function, prose term or variant. The other four names are attested. `PlannerState` is a phantom introduced by the ambiguity register itself.

### Why it matters

The ambiguity register is what an implementer consults to find out which names are unsafe to rely on. A phantom entry there has two bad effects: it sends the reader looking for a type that does not exist, and it inflates the apparent size of the naming problem, which weakens the four real findings listed beside it. It also matters for the repository's own rule that generated facts be re-derived from the source — a term that fails that check should not be in a register at all.

### Disposition

AMB-25 is corrected in this pass to the four attested names, with the correction recorded here rather than applied silently, and `PlannerState` is entered in this dictionary as a FORBIDDEN variant that must not be introduced: the role it gestures at is occupied by `PlanProposal` (T-02), the compiler's output before validation. No source identifier is renamed, because none exists to rename.

## X-63

**C-09 and AMB-24 cite README line ranges that contain no status block**

- **Kind:** `PROVENANCE-DEFECT` — a citation in the canonicalization layer does not point at the text it claims
- **Severity:** MINOR
- **Terms affected:** T-64 `Specification`, T-65 `Implementation`, T-68 `EvidenceStatus`, T-69 `Frozen`
- **Previously registered as:** `C-09`, `AMB-24`

### Evidence (frozen source)

| Line | Text at that line | What it denotes there |
|---|---|---|
| `Red-on-Rust.md` L38939 | `IMPLEMENTATION: READY` | turn [54]: source status 1 |
| `Red-on-Rust.md` L39053 | `Implementation:     READY` | turn [54]: source status 2 |
| `Red-on-Rust.md` L41307 | `Implementation:     IN PROGRESS` | turn [58]: source status 3, the LATEST |

### Evidence (canonicalization layer)

| File:line | Text at that line | Note |
|---|---|---|
| `spec/06-contradictions-ambiguities.md`:22 | `README L22–28 ("Implementation: IN PROGRESS") vs README L656–661 / L42092–42100` | the defective citations |
| `req/03-ambiguous.md`:189 | ```README.md` L22–28 vs L656–661`` | the same defective citations, repeated |
| `README.md`:12 | `Implementation:     IN PROGRESS` | the real first status block |
| `README.md`:735 | `Implementation     READY` | the real last status block |

### The collision

C-09's evidence is 'README L22–28 ("Implementation: IN PROGRESS") vs README L656–661 / L42092–42100 ("Implementation: READY")' and AMB-24 repeats '`README.md` L22–28 vs L656–661'. The README's two status blocks are at L12 (`Implementation: IN PROGRESS`) and L735 (`Implementation READY`); L22-28 and L656-661 contain no status text. The third citation, L42092-42100, is beyond the end of the frozen source, whose last line is 42312 in a different file — the README is 745 lines long, so no README line in the 42000s exists. It was 708 lines when this collision was first recorded; the block moved to L732 when this pass added a `term/` paragraph to the README, and to L735 when the declaration sweep extended that same paragraph. The citation is therefore anchored to the `# Project Status` heading (now L732) as well as to the line, so that it survives further growth. The real in-source contradiction is between L38939/L39053 (`READY`, turn [54]) and L41307 (`IN PROGRESS`, turn [58]).

### Why it matters

The contradiction C-09 reports is real, but three of its four citations are unverifiable and one refers to a line range that cannot exist in the cited file. The status question is the repository's claim-discipline hinge: `READY` read as 'implementation exists' would be a conformance claim with no evidence behind it, which R-CLAIM-01 and the N-05/N-06 ladder prohibit. A reader who tries to check the citations, fails, and concludes the finding is spurious would be left with an unresolved status contradiction — the opposite of the intended effect.

### Disposition

C-09 and AMB-24 are corrected in this pass to the verified citations (README L12 and L735 under the `# Project Status` heading at L732; source L38939, L39053, L41307), and the resolution is stated: under latest-frozen-text the turn-[58] `IN PROGRESS` governs the source, while the canonicalization layer's own position — no implementation present, every obligation `SPECIFIED` (spec/00 §2) — governs the repository and makes both source status lines non-evidence. No status text is rewritten in either file.

## X-75

**Residual used-but-undeclared variant paths across five more enums, and one variant silently dropped**

- **Kind:** `UNDECLARED-VARIANT` — an `Enum::Variant` path is used in the frozen source but appears in no declaration of that enum
- **Severity:** MINOR
- **Terms affected:** T-31 `Value`, T-78 `ControlFrame`, T-73 `MarshalFault`, T-36 `RunState`, T-08 `PlanIR`, T-76 `CanonicalError`
- **Previously registered as:** `C-65`, `X-65`, `X-66`, `C-49`, `U-02`, `U-09`

### Evidence (frozen source)

| Line | Text at that line | What it denotes there |
|---|---|---|
| `Red-on-Rust.md` L1027 | `Value::Null` | turn [3]: the declared sets have `Unit`, not `Null` |
| `Red-on-Rust.md` L12283 | `pub enum Value {` | turn [21]: the first `Value` declaration |
| `Red-on-Rust.md` L25995 | `Value::DelegatedCapability` | turn [32]: in no `Value` declaration |
| `Red-on-Rust.md` L26000 | `DelegatedCapability` | turn [32]: second use, five lines later |
| `Red-on-Rust.md` L25694 | `MarshalFault::CorruptedPayload` | turn [32]: in neither `MarshalFault` declaration (X-65) |
| `Red-on-Rust.md` L985 | `pub enum ControlFrame {` | turn [3]: the only declaration, head elided at L989 |
| `Red-on-Rust.md` L986 | `Vec<PlanIR>` | turn [3]: `PlanIR` is declared nowhere |
| `Red-on-Rust.md` L987 | `FuncRef` | turn [3]: `FuncRef` is declared nowhere |
| `Red-on-Rust.md` L988 | `EffectSignature` | turn [3]: `EffectSignature` is declared nowhere |
| `Red-on-Rust.md` L1031 | `ControlFrame::ReduceIR` | turn [3]: used in the machine's own `match` |
| `Red-on-Rust.md` L1282 | `ControlFrame::ResumeWithResult` | turn [3]: used, never declared |
| `Red-on-Rust.md` L1092 | `pub enum TransitionEvent {` | turn [3]: the only declaration |
| `Red-on-Rust.md` L1055 | `TransitionEvent::ActorSpawned` | turn [3]: used 37 lines BEFORE the enum that should declare it |
| `Red-on-Rust.md` L24299 | `pub enum RunState {` | turn [31]: declares `NotRunnable` |
| `Red-on-Rust.md` L24300 | `NotRunnable,` | turn [31]: the variant that disappears |
| `Red-on-Rust.md` L25526 | `pub enum RunState {` | turn [32]: re-declared without `NotRunnable`, no supersession note |

### Evidence (canonicalization layer)

| File:line | Text at that line | Note |
|---|---|---|
| `spec/06-contradictions-ambiguities.md`:79 | `Residual used-but-undeclared variant paths` | C-65, the row this entry backs |

### The collision

The same sweep, on the enums too small for a row of their own: (a) `Value::Null` at L1027, where every declared `Value` set has `Unit` and not `Null` (L12283 onward); (b) `Value::DelegatedCapability` at L25995 and L26000, in no `Value` declaration, the declared capability variant being `Capability(Box<CapabilityToken>)`; (c) `MarshalFault::CorruptedPayload` at L25694, in neither `MarshalFault` declaration (L10846/L25983 versus L30645, already X-65); (d) `ControlFrame::ReduceIR` at L1031 and matched at L1035, plus `ControlFrame::ResumeWithResult` at L1282, against the single elided declaration at L985; (e) `TransitionEvent::ActorSpawned` at L1055, which precedes the only `TransitionEvent` declaration at L1092; and (f) `RunState::NotRunnable`, declared at L24300 and silently absent from the L25526 re-declaration.

### Why it matters

Each is individually small, but they are the same defect class as X-69 to X-71 and they sit on load-bearing paths. `Value::Null` versus `Value::Unit` is the canonical encoding of the empty value, which X-50's envelope format and X-72's `CanonicalError` both turn on — and C-49 already records that the frozen discriminant table lists 5 of 8 variants, so the empty value's tag is not pinned down from either direction. `Value::DelegatedCapability` is the value form of the delegation mechanism whose AST node is also undeclared (X-70), so delegation is missing at both layers, and `MarshalFault::CapabilityRequiresDelegation` (L25984) is the error for it — a fault whose success case cannot be represented. `ControlFrame`'s three declared variants reference `PlanIR`, `FuncRef` and `EffectSignature`, none of which is declared anywhere, so the control stack cannot be constructed from the frozen text at all, and its two undeclared variants are used in the machine's own `match` at L1031-L1035. `RunState::NotRunnable` vanishing between L24300 and L25526 with no supersession note is the R-SCOPE-03 pattern occurring inside the frozen source itself.

### Disposition

REPORTED as one grouped finding so a single ruling can close it; nothing renamed. `ControlFrame` is filed as T-78 with `ReduceIR` and `ResumeWithResult` protected and its three undeclared payload types named in the note. `Value::Null` and `Value::DelegatedCapability` are added to T-31's `protected` as source-used spellings rather than normalized to `Unit`/`Capability`; `MarshalFault::CorruptedPayload` is added to T-73's. `TransitionEvent` gets no term of its own — it is declared once (L1092) and its use-before-declaration is recorded in this entry's sites — while the dropped `RunState::NotRunnable` is added to T-36's `protected` with both declarations cited.

### Decision needed

Only in part: `NotRunnable`'s removal and `Null` versus `Unit` need a ruling; the rest follow from the X-69/X-70/X-72 rulings.

## X-53

**Implementation status is 'READY' twice and 'IN PROGRESS' once in the source, and the README reverses the order**

- **Kind:** `SCOPE-DRIFT` — a name's scope changed between frozen eras without retraction
- **Severity:** INFO
- **Terms affected:** T-65 `Implementation`, T-64 `Specification`, T-68 `EvidenceStatus`
- **Previously registered as:** `C-09`, `AMB-24`

### Evidence (frozen source)

| Line | Text at that line | What it denotes there |
|---|---|---|
| `Red-on-Rust.md` L38939 | `IMPLEMENTATION: READY` | turn [54] |
| `Red-on-Rust.md` L39053 | `Implementation:     READY` | turn [54], second status block |
| `Red-on-Rust.md` L41307 | `Implementation:     IN PROGRESS` | turn [58] — the LATEST source statement |

### Evidence (canonicalization layer)

| File:line | Text at that line | Note |
|---|---|---|
| `README.md`:12 | `Implementation:     IN PROGRESS` | the README's first status block |
| `README.md`:735 | `Implementation     READY` | the README's last status block |

### The collision

The source states `IMPLEMENTATION: READY` twice (turn [54]) and `Implementation: IN PROGRESS` once (turn [58], later). The README states `Implementation: IN PROGRESS` in its first status block (L12) and `Implementation: READY` in its last (L735). C-09/AMB-24 record the contradiction but cite README L22-28 and L656-661 and source L42092-42100, none of which contains a status block (X-61).

### Why it matters

Neither statement is repository evidence: this repository contains no implementation, so the correct status is 'no implementation present' and every obligation is `SPECIFIED` (spec/00 §2). The collision matters only because a reader may take 'READY' as a claim that implementation has begun, which would violate the evidence ladder (N-06).

### Disposition

All four status lines recorded verbatim with correct citations; none rewritten. Under latest-frozen-text the turn-[58] `IN PROGRESS` governs the source, and the canonicalization layer's 'no implementation present' governs the repository. This entry corrects C-09's citations by supplying the real ones rather than editing C-09.
