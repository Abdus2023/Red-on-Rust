"""Canonical terminology dictionary for Red-on-Rust — the single source of truth.

Every value in this file is derived from the frozen source `Red-on-Rust.md`
(42,312 lines, turns [1]-[60]) and `README.md` (turn [60]) by direct line
reads during the terminology pass.  `term/_dict.py` re-greps the source to
confirm every anchor on every run, so nothing here is asserted on trust.

Design constraints honoured by this data (see term/00-overview.md §3):

  * NO SILENT RENAMES.  A frozen API name, Rust type, mathematical symbol, or
    protocol field is never rewritten.  Where the source uses two names for one
    thing, or one name for two things, BOTH are recorded and the collision is
    reported (X-NN).  `protected` lists the identifiers that must not be
    renamed; `forbidden` lists only *prose* substitutions that misstate the
    frozen denotation.
  * SUPERSEDED is not FORBIDDEN.  A superseded form stays in the record for
    traceability (spec/00 §1.2) and may be used in supersession/provenance
    notes; it may not be used as the current name.
  * The frozen source governs.  Where the canonicalization layer (spec/, mod/,
    req/) and the source disagree, the source wins and the disagreement is
    recorded as a collision against the canonicalization layer (§B of
    term/02-collisions.md).
"""

from __future__ import annotations

from dataclasses import dataclass, field

SOURCE = "Red-on-Rust.md"
SOURCE_MAX_LINE = 42312

# ---------------------------------------------------------------------------
# Controlled vocabularies
# ---------------------------------------------------------------------------

#: TYPE field vocabulary.  A term's TYPE says what kind of thing the name
#: denotes in the frozen source — this is what makes homonyms detectable.
TYPES = {
    "RUST-STRUCT": "a Rust `struct` declaration (nominal type)",
    "RUST-ENUM": "a Rust `enum` declaration (closed variant set)",
    "RUST-NEWTYPE": "a Rust single-field tuple `struct` wrapper",
    "RUST-TYPE-ALIAS": "a Rust `pub type X = Y` alias",
    "RUST-TRAIT": "a Rust `trait` (API contract)",
    "RUST-VARIANT": "an enum variant (not a type in its own right)",
    "RUST-FIELD": "a struct/variant field name (protocol field)",
    "RUST-METHOD": "a trait/inherent method name (API surface)",
    "MATH-SYMBOL": "a mathematical symbol in a frozen formula",
    "MATH-PREDICATE": "a mathematical predicate in a frozen formula/theorem",
    "MATH-FUNCTION": "a mathematical operation in a frozen algebra",
    "PROTOCOL-RECORD": "a durable/wire record kind",
    "PROTOCOL-FORMAT": "a frozen byte-level format",
    "STATE": "a lifecycle state of a machine object",
    "COMPONENT": "an architectural component / trusted layer",
    "CONCEPT": "a defined architectural concept with no single declaration",
    "PROCESS": "a defined procedure or pipeline",
    "CLAIM-STATUS": "a rung of the evidence ladder",
    "IDENTIFIER-CLASS": "a family of stable identifiers",
    "UNDECLARED-TYPE": "a name used as a type in frozen declarations but never declared anywhere",
    "STATE-VS-RECORD": "one name shared by a lifecycle state, a record kind and a struct",
}

#: Domains used to group the dictionary.  Each maps to one owning module.
DOMAINS = [
    ("PLAN-PIPELINE", "MOD-02", "Untrusted input to machine input"),
    ("AUTHORITY", "MOD-03", "Capability algebra, kernel, delegation"),
    ("EFFECT", "MOD-08", "Effect model and request/issuance protocol"),
    ("RESOURCE", "MOD-04", "Budget algebra and logical time"),
    ("MACHINE", "MOD-05", "Calculus, CEK machine, values, frames"),
    ("CONCURRENCY", "MOD-06", "Actors, status, mailboxes, marshalling"),
    ("SCHEDULING", "MOD-07", "Deterministic scheduling state"),
    ("HOST", "MOD-09", "Live host gate and ordered replay"),
    ("PERSISTENCE", "MOD-11", "Canonical encoding, WAL, snapshots, journal"),
    ("RECOVERY", "MOD-12", "Crash classification and reconciliation"),
    ("AGENT", "MOD-13", "LLM/planner boundary and observations"),
    ("VERIFICATION", "MOD-15", "Reference model, differential, mutation"),
    ("CLAIM", "MOD-17", "Evidence ladder and conformance claims"),
]

#: Collision severity (same scale as spec/06).
SEVERITIES = ["BLOCKING", "MAJOR", "MINOR", "INFO"]

#: Collision kinds — what sort of terminology failure occurred.
COLLISION_KINDS = {
    "TYPE-HOMONYM": "one name, two or more incompatible type declarations",
    "TYPE-ROLE-HOMONYM": "one name used as both a type and a predicate/symbol",
    "FIELD-SET": "same type name, different field sets or field names",
    "SYMBOL-OVERLOAD": "one mathematical symbol, two or more denotations",
    "PREDICATE-SIGNATURE": "one predicate name, several arities/argument orders",
    "STAGE-ORDER": "the same pipeline is written with different stage sequences",
    "STATE-VS-RECORD": "a lifecycle state, a record kind and a struct share a name",
    "UNDEFINED-TYPE": "a name is used as a type but never declared",
    "METHOD-SIGNATURE": "one trait name, incompatible method names/returns",
    "ALIAS-DEFECT": "the canonicalization layer states an alias/definition the source does not support",
    "SCOPE-DRIFT": "a name's scope changed between frozen eras without retraction",
    "PROVENANCE-DEFECT": "a citation in the canonicalization layer does not point at the text it claims",
    "PHANTOM-IDENTIFIER": "a register names an identifier that occurs nowhere in the frozen source",
    "DIVERGENT-SHAPE": "the same type name is declared repeatedly with materially different variant or field shapes",
    "UNDECLARED-VARIANT": "an `Enum::Variant` path is used in the frozen source but appears in no declaration of that enum",
}


@dataclass
class Anchor:
    """A verified location in a repository file (default: the frozen source).

    `turn` is the source turn number, or None for anchors into the
    canonicalization layer (spec/, mod/, req/), which has no turns.
    """

    line: int
    turn: int | None
    signature: str  # substring that MUST appear on that line
    file: str = SOURCE

    def cite(self) -> str:
        if self.file == SOURCE:
            return f"`Red-on-Rust.md` L{self.line} (turn [{self.turn}])"
        return f"`{self.file}` L{self.line}"


@dataclass
class Term:
    tid: str
    canonical: str
    domain: str
    type: str
    definition: str
    owner: str  # MOD-NN
    owner_crate: str
    first_definition: Anchor
    frozen_at: Anchor | None  # governing declaration, when it is not the first
    forbidden: list[str] = field(default_factory=list)
    protected: list[tuple[str, str]] = field(default_factory=list)
    dependents: list[str] = field(default_factory=list)  # other T-NN
    obligations: list[str] = field(default_factory=list)  # R-…
    sections: list[str] = field(default_factory=list)  # S-NN
    collisions: list[str] = field(default_factory=list)  # X-NN
    shape: str | None = None  # verbatim frozen declaration
    supersedes: list[str] = field(default_factory=list)  # superseded forms, kept
    note: str = ""

    @property
    def requires(self) -> bool:
        """True for the terms the normalization request names explicitly."""
        return self.tid in REQUIRED_TERMS


@dataclass
class Law:
    """A non-conflation law: two terms that MUST NOT be used for each other."""

    lid: str
    left: str
    right: str
    statement: str
    evidence: list[tuple[int, str]]
    consequence: str
    enforcement: str
    mandated_by: str


@dataclass
class Collision:
    xid: str
    title: str
    kind: str
    severity: str
    sites: list[tuple[int, str, str]]  # (line, token, what it denotes there)
    statement: str
    why_it_matters: str
    disposition: str
    affects: list[str]  # T-NN
    previously: list[str] = field(default_factory=list)  # C-…/U-…/AMB-…
    decision_needed: str = ""
    new_finding: bool = True
    #: (file, line, token, note) — collision sites in the canonicalization layer
    #: itself (spec/, mod/, req/, README.md) rather than in the frozen source.
    doc_sites: list[tuple[str, int, str, str]] = field(default_factory=list)


# ---------------------------------------------------------------------------
# The 25 term NAMES the normalization request lists, realized as 26 canonical
# TERMS: `Observation` maps to two, because the frozen source declares two
# incompatible structs under that one name (X-06).  Covering it with a single
# entry would be exactly the conflation the request asks to be reported.
# ---------------------------------------------------------------------------
REQUIRED_TERMS = {
    "T-01",  # Block
    "T-02",  # PlanProposal
    "T-03",  # ParsedBlock
    "T-04",  # ValidatedPlan
    "T-05",  # CapabilityCheckedPlan
    "T-06",  # ExecutablePlan
    "T-09",  # CapRef
    "T-10",  # Authority
    "T-16",  # Effect
    "T-17",  # EffectRequest
    "T-18",  # EffectIssued
    "T-19",  # EffectReceipt
    "T-20",  # EffectId
    "T-54",  # Observation (planner-facing)
    "T-41",  # HostPolicy
    "T-24",  # Budget
    "T-25",  # Consumable
    "T-26",  # Reserved
    "T-28",  # LogicalTime
    "T-34",  # ActorId
    "T-35",  # ActorStatus
    "T-45",  # WAL
    "T-48",  # Snapshot
    "T-23",  # EffectJournal
    "T-42",  # ReplayHost
    "T-57",  # Observation (differential)
}

#: request name -> the canonical TERMS that realize it.  `term/_check.py` verifies
#: that the 25 names cover exactly `REQUIRED_TERMS`, that every name maps to at
#: least one term, and that each mapped term's canonical name contains the request
#: name — so a required term cannot be dropped or renamed by accident.
REQUIRED_NAMES: dict[str, list[str]] = {
    "Block": ["T-01"],
    "PlanProposal": ["T-02"],
    "ParsedBlock": ["T-03"],
    "ValidatedPlan": ["T-04"],
    "CapabilityCheckedPlan": ["T-05"],
    "ExecutablePlan": ["T-06"],
    "CapRef": ["T-09"],
    "Authority": ["T-10"],
    "Effect": ["T-16"],
    "EffectRequest": ["T-17"],
    "EffectIssued": ["T-18"],
    "EffectReceipt": ["T-19"],
    "EffectId": ["T-20"],
    "Observation": ["T-54", "T-57"],
    "HostPolicy": ["T-41"],
    "Budget": ["T-24"],
    "Consumable": ["T-25"],
    "Reserved": ["T-26"],
    "LogicalTime": ["T-28"],
    "ActorId": ["T-34"],
    "ActorStatus": ["T-35"],
    "WAL": ["T-45"],
    "Snapshot": ["T-48"],
    "EffectJournal": ["T-23"],
    "ReplayHost": ["T-42"],
}


# ===========================================================================
# TERMS
# ===========================================================================
A = Anchor

TERMS: list[Term] = [
    # ---------------------------------------------------------------- A. plan
    Term(
        tid="T-01",
        canonical="Block",
        domain="PLAN-PIPELINE",
        type="RUST-STRUCT",
        definition=(
            "Homoiconic untrusted program data at the language surface: the form the "
            "LLM/planner emits and the only thing an untrusted producer may supply. "
            "`Block` carries no authority, no validation verdict, and no resource "
            "bound. It is never a security boundary (R-TRUST-01) and has no path into "
            "`step()` (R-ARCH-03)."
        ),
        owner="MOD-02",
        owner_crate="ror-compiler (consumer); produced by ror-agent",
        first_definition=A(855, 3, "pub struct Block(pub Vec<Value>);"),
        frozen_at=A(13484, 21, "pub struct Block {"),
        forbidden=[
            "program (as a synonym for Block)",
            "source (as a synonym for Block)",
            "raw plan",
            "plan (the obsolete turn-[2] primitive; see X-02)",
        ],
        protected=[
            ("Block", "frozen Rust type name; also the trust-table row name (L41828)"),
            ("B", "mathematical symbol for a block in turn [1] (L132); superseded by "
                  "the typed name but never renamed in that text"),
        ],
        dependents=["T-02", "T-03", "T-06", "T-30"],
        obligations=["R-COMPILE-01", "R-COMPILE-02", "R-TRUST-01", "R-ARCH-03"],
        sections=["S-06"],
        collisions=["X-02", "X-15", "X-28", "X-29", "X-62"],
        shape="pub struct Block { pub forms: Vec<Form> }   // L13484, turn [21]",
        supersedes=["pub struct Block(pub Vec<Value>);  // L855, turn [3]"],
        note=(
            "Two incompatible declarations exist (X-28) and the later one is typed "
            "over `Form`, which the source never declares (X-29 family). Neither form "
            "is renamed here; both are recorded and the difference is reported."
        ),
    ),
    Term(
        tid="T-02",
        canonical="PlanProposal",
        domain="PLAN-PIPELINE",
        type="RUST-STRUCT",
        definition=(
            "The complete output of the untrusted LLM/planner: "
            "`{ observation_sequence, block, planner_metadata }`. `LLMOutput ∈ Data`: "
            "a proposal is data to be validated, never authority, never a plan, and "
            "never machine input. A proposal whose `observation_sequence` is behind the "
            "current sequence is `StalePlan` and is rejected without state mutation."
        ),
        owner="MOD-13",
        owner_crate="ror-agent",
        first_definition=A(27175, 33, "pub struct PlanProposal {"),
        frozen_at=None,
        forbidden=[
            "plan (a PlanProposal is not a plan)",
            "proposal plan",
            "planner output plan",
            "draft ExecutablePlan",
        ],
        protected=[
            ("PlanProposal", "frozen Rust type name (single declaration; no variant forms)"),
            ("observation_sequence", "frozen protocol field"),
            ("planner_metadata", "frozen protocol field (content undefined, U-13)"),
            ("StalePlan", "frozen fault/rejection name"),
        ],
        dependents=["T-01", "T-55", "T-56"],
        obligations=["R-PLANNER-01", "R-PLANNER-03", "R-PLANNER-04", "R-CORE-01"],
        sections=["S-05"],
        collisions=["X-04", "X-06", "X-34", "X-62", "X-64", "X-69"],
        shape="pub struct PlanProposal { ... }   // L27175, turn [33]",
        note=(
            "Distinct from `PlannerAccepted` (T-55), which is the *recorded* accepted "
            "proposal used for replay, and from `Plan` (obsolete, turn [2])."
        ),
    ),
    Term(
        tid="T-03",
        canonical="ParsedBlock",
        domain="PLAN-PIPELINE",
        type="RUST-STRUCT",
        definition=(
            "Compiler stage 1 artifact: a `Block` whose syntax has been validated "
            "against the dialect grammar and normalized — `{ ast: NormalizedAST }`. "
            "It carries no effect set, no capability verdict, and no resource bound. "
            "Judgment 11 of turn [3]: `Γ ⊢_syntax B ⇒ P_parsed`."
        ),
        owner="MOD-02",
        owner_crate="ror-compiler",
        first_definition=A(864, 3, "pub struct ParsedBlock { ast: NormalizedAST }"),
        frozen_at=None,
        forbidden=["parsed program", "syntax tree (as a synonym for ParsedBlock)"],
        protected=[
            ("ParsedBlock", "frozen Rust type name; declared private to `mod compiler`"),
            ("ast", "frozen field name"),
            ("P_parsed", "the turn-[3] judgment's symbol for this stage"),
        ],
        dependents=["T-01", "T-04", "T-07"],
        obligations=["R-COMPILE-02", "R-COMPILE-03", "R-COMPILE-05"],
        sections=["S-06"],
        collisions=["X-01", "X-02", "X-28", "X-29", "X-41"],
        shape="pub struct ParsedBlock { ast: NormalizedAST }   // L864, turn [3]",
        note=(
            "Declared once (L864). Later pipeline renderings (L13595, L39267) keep the "
            "stage; L39271 replaces it with `NormalizedAST` as the stage name (X-02). "
            "Its field type `NormalizedAST` is never declared (X-29)."
        ),
    ),
    Term(
        tid="T-04",
        canonical="ValidatedPlan",
        domain="PLAN-PIPELINE",
        type="RUST-STRUCT",
        definition=(
            "Compiler stage 2 artifact: a `ParsedBlock` annotated with its statically "
            "extracted effect set — `{ ir: PlanIR, effects: EffectSet }`. It has NOT "
            "been capability-checked and NOT been resource-bounded, so it is not "
            "machine input. Judgment 12 of turn [3]: `P_parsed ⊢_effects F`."
        ),
        owner="MOD-02",
        owner_crate="ror-compiler",
        first_definition=A(865, 3, "pub struct ValidatedPlan { ir: PlanIR, effects: EffectSet }"),
        frozen_at=A(13488, 21, "pub struct ValidatedPlan {"),
        forbidden=[
            "ExecutablePlan (a ValidatedPlan is pre-capability-analysis)",
            "validated executable plan",
            "approved plan",
            "safe plan",
        ],
        protected=[
            ("ValidatedPlan", "frozen Rust type name AND a frozen mathematical "
                              "predicate symbol — see X-01; neither use may be renamed"),
            ("ValidatedPlan(P)", "the first conjunct of the central external-effect "
                                 "theorem (L27494, L41338); a predicate over the plan P"),
            ("ir", "frozen field name"),
            ("effects", "frozen field name"),
            ("P_valid", "the turn-[3] judgment's symbol for this stage"),
        ],
        dependents=["T-03", "T-05", "T-08"],
        obligations=["R-COMPILE-02", "R-COMPILE-03", "R-CORE-02"],
        sections=["S-06", "S-02"],
        collisions=['X-01', 'X-02', 'X-04', 'X-34', 'X-40', 'X-41', 'X-64'],
        shape="pub struct ValidatedPlan { ir: PlanIR, effects: EffectSet }   // L865, L13488",
        note=(
            "HOMONYM (X-01): `ValidatedPlan` denotes (a) this struct — an intermediate "
            "stage that has not been capability-checked — and (b) the predicate "
            "`ValidatedPlan(P)` in the central theorem, whose argument P is the plan "
            "that enters the machine (i.e. an `ExecutablePlan`). spec/05 recorded (b) "
            "as an *alias* of `ExecutablePlan`; that is the defect reported as X-40. "
            "Both uses are frozen identifiers and neither is renamed here."
        ),
    ),
    Term(
        tid="T-05",
        canonical="CapabilityCheckedPlan",
        domain="PLAN-PIPELINE",
        type="RUST-STRUCT",
        definition=(
            "Compiler stage 3 artifact: a `ValidatedPlan` for which the required "
            "authority has been computed and checked against ambient authority — "
            "`{ ir: PlanIR, required_caps: CapSet }`, with `κ_req ⪯ κ_ambient`. It has "
            "NOT been resource-bounded, so it is still not machine input. Judgment 13 "
            "of turn [3]."
        ),
        owner="MOD-02",
        owner_crate="ror-compiler",
        first_definition=A(866, 3, "pub struct CapabilityCheckedPlan { ir: PlanIR, required_caps: CapSet }"),
        frozen_at=None,
        forbidden=[
            "authorized plan (capability checking is static; runtime authorization is "
            "the kernel's `Authorized` decision)",
            "ExecutablePlan",
            "capability plan",
        ],
        protected=[
            ("CapabilityCheckedPlan", "frozen Rust type name; declared private to `mod compiler`"),
            ("required_caps", "frozen field name"),
            ("CapSet", "the field's type name, used only here"),
            ("P_cap", "the turn-[3] judgment's symbol for this stage"),
        ],
        dependents=["T-04", "T-06", "T-09"],
        obligations=["R-COMPILE-03", "R-COMPILE-05", "R-CAP-04"],
        sections=["S-06"],
        collisions=["X-01", "X-02", "X-40"],
        shape="pub struct CapabilityCheckedPlan { ir: PlanIR, required_caps: CapSet }   // L866",
        note=(
            "Declared once (L866) and named in two of the three pipeline renderings "
            "(L567, L9106); omitted from the third (L39265-39280) and from the "
            "turn-[21] rendering (X-02). Static capability *analysis* is not the "
            "runtime `Authorized(A_c, E, t)` gate (N-03)."
        ),
    ),
    Term(
        tid="T-06",
        canonical="ExecutablePlan",
        domain="PLAN-PIPELINE",
        type="RUST-STRUCT",
        definition=(
            "Compiler stage 4 artifact and the ONLY legal input to the machine: an "
            "immutable, resource-bounded plan whose constructors are private to the "
            "compiler (`_sealed: Sealed`), so no component outside `ror-compiler` can "
            "forge one. `Block ≠ ExecutablePlan`; the transition requires the whole "
            "parse → validate → capability → resource pipeline."
        ),
        owner="MOD-02",
        owner_crate="ror-compiler",
        first_definition=A(869, 3, "pub struct ExecutablePlan {"),
        frozen_at=A(14103, 22, "pub struct ExecutablePlan {"),
        forbidden=[
            "Block (as a synonym)",
            "compiled block",
            "plan (unqualified)",
            "validated plan (unqualified — see X-01)",
            "runnable program",
        ],
        protected=[
            ("ExecutablePlan", "frozen Rust type name"),
            ("_sealed", "frozen private marker field; the constructor-privacy mechanism"),
            ("Sealed", "frozen zero-sized private type"),
            ("bounds", "frozen field name"),
            ("expr", "frozen payload field name in the turn-[21]/[22] declarations"),
            ("ir", "frozen payload field name in the turn-[3]/[58] declarations — "
                   "see X-03; not renamed"),
            ("P_exec", "the turn-[3] judgment's symbol for this stage"),
        ],
        dependents=["T-05", "T-30", "T-32", "T-37"],
        obligations=["R-COMPILE-01", "R-COMPILE-04", "R-COMPILE-05", "R-ARCH-03", "R-ORDER-03"],
        sections=["S-06", "S-04"],
        collisions=["X-01", "X-02", "X-03", "X-30", "X-34", "X-40", "X-41", "X-62"],
        shape=(
            "pub struct ExecutablePlan { pub(crate) expr: Expr, "
            "pub(crate) bounds: ResourceBounds, _sealed: Sealed }   // L14103, L14487"
        ),
        supersedes=[
            "pub struct ExecutablePlan { ir: PlanIR, bounds: ResourceBounds, _sealed: Sealed }"
            "   // L869 (turn [3]) and L39972 (turn [58]) — payload field `ir: PlanIR`",
        ],
        note=(
            "FIVE declarations with two payload field names (`expr: Expr` at L13493, "
            "L14103, L14487; `ir: PlanIR` at L869 and L39972). X-03 reports this. The "
            "turn-[58] form reverts to `ir: PlanIR`, whose type is never declared and "
            "whose variants are superseded (X-30), so the dictionary records the "
            "collision and requires an explicit decision rather than picking a winner."
        ),
    ),
    Term(
        tid="T-07",
        canonical="NormalizedAST",
        domain="PLAN-PIPELINE",
        type="UNDECLARED-TYPE",
        definition=(
            "The normalized syntax artifact carried by `ParsedBlock.ast`. Used as a "
            "field type at L864 and as a pipeline stage name at L39271; the source "
            "never declares it, never gives it a variant set, and never states its "
            "relationship to the frozen `Expr` AST."
        ),
        owner="MOD-02",
        owner_crate="ror-compiler",
        first_definition=A(864, 3, "pub struct ParsedBlock { ast: NormalizedAST }"),
        frozen_at=None,
        forbidden=["normalized expression", "canonical AST (as a synonym)"],
        protected=[("NormalizedAST", "name used in frozen source text; not renamed")],
        dependents=["T-03", "T-30"],
        obligations=["R-COMPILE-02", "R-COMPILE-03"],
        sections=["S-06"],
        collisions=["X-02", "X-29", "X-40", "X-41"],
        note=(
            "Exactly two occurrences in 42,312 lines (L864, L39271). UNDEFINED-TYPE: "
            "this entry records the name and its usage, and reports the gap; it does "
            "not invent a declaration."
        ),
    ),
    Term(
        tid="T-08",
        canonical="PlanIR",
        domain="PLAN-PIPELINE",
        type="UNDECLARED-TYPE",
        definition=(
            "The intermediate representation carried by `ValidatedPlan.ir`, "
            "`CapabilityCheckedPlan.ir`, and (in two of five declarations) "
            "`ExecutablePlan.ir`. Used with variants `PlanIR::Value`, `PlanIR::Invoke`, "
            "`PlanIR::Spawn { plan, trust_level }` at L1037-L1051, but never declared "
            "as an enum."
        ),
        owner="MOD-02",
        owner_crate="ror-compiler",
        first_definition=A(865, 3, "pub struct ValidatedPlan { ir: PlanIR, effects: EffectSet }"),
        frozen_at=None,
        forbidden=["IR (unqualified)", "plan representation", "lowered block"],
        protected=[
            ("PlanIR", "name used in frozen source text; not renamed"),
            ("PlanIR::Invoke", "superseded variant name — the frozen AST constructor is "
                               "`Expr::Request` (C-17); retained for traceability"),
            ("trust_level", "superseded field of `PlanIR::Spawn`; the frozen `Expr::Spawn` "
                            "has no isolation field (U-05)"),
        ],
        dependents=["T-04", "T-05", "T-06", "T-30"],
        obligations=["R-COMPILE-02", "R-COMPILE-03"],
        sections=["S-06"],
        collisions=["X-02", "X-03", "X-16", "X-30", "X-34", "X-40", "X-41", "X-62", "X-75"],
        note=(
            "Two pipeline renderings place `PlanIR` AFTER `ValidatedPlan` as a distinct "
            "stage (L13603, L39275), while the frozen structs make it the *content* of "
            "`ValidatedPlan` (L865) — X-02. Its variant set uses `Invoke` and "
            "`trust_level`, both superseded (C-17, U-05) — X-30."
        ),
    ),
]


TERMS += [
    # ------------------------------------------------------------ B. authority
    Term(
        tid="T-09",
        canonical="CapRef",
        domain="AUTHORITY",
        type="RUST-STRUCT",
        definition=(
            "An opaque, generation-safe capability REFERENCE: `{ index: u32, "
            "generation: u32 }`, fields private, no public constructor from arbitrary "
            "integers. A `CapRef` is a name the machine can pass around and the "
            "evaluator can hold; it is NOT authority. The authority it denotes is "
            "`κ(c)` = `Authority(c)` = `A_c`, which is kernel-private. Ordinary "
            "marshalling rejects raw capabilities; authority crosses actor boundaries "
            "only by explicit delegation."
        ),
        owner="MOD-03",
        owner_crate="ror-kernel",
        first_definition=A(915, 3, "pub struct CapRef(pub(crate) u64);"),
        frozen_at=A(9131, 17, "pub struct CapRef {"),
        forbidden=[
            "capability (unqualified — denotes the grant, not the reference)",
            "capability token",
            "authority handle",
            "capability handle (the obsolete v0.3 `handle`/`h` wording)",
        ],
        protected=[
            ("CapRef", "frozen Rust type name; also 15A standalone tag `0x30`"),
            ("index", "frozen field name"),
            ("generation", "frozen field name"),
            ("c", "frozen mathematical symbol for a CapRef (e.g. `Valid(c,t)`)"),
            ("Value::Capability", "frozen machine-value variant that *carries* a CapRef"),
        ],
        dependents=["T-10", "T-11", "T-12", "T-15", "T-17"],
        obligations=["R-CAP-01", "R-CAP-05", "R-KERN-03", "R-MARSHAL-01", "R-CORE-07"],
        sections=["S-09", "S-10", "S-16"],
        collisions=["X-05", "X-25", "X-26", "X-27", "X-36", "X-38", "X-59", "X-66", "X-77", "X-82"],
        shape="pub struct CapRef { index: u32, generation: u32 }   // L9131, turn [17]",
        supersedes=["pub struct CapRef(pub(crate) u64);   // L915, L3646, L5034, L5949"],
        note=(
            "The single-`u64` form cannot express generational reuse safety and is "
            "superseded by the frozen `{index, generation}` form (X-25). N-03 "
            "(`CapRef ≠ Authority`) is the load-bearing distinction of the trust model."
        ),
    ),
    Term(
        tid="T-10",
        canonical="Authority",
        domain="AUTHORITY",
        type="MATH-SYMBOL",
        definition=(
            "The operation-indexed grant set behind a capability: "
            "`A = { (o, A_o) | o ∈ O_granted }` with `A_o = ⟨S, Q, R, T⟩` (scope, "
            "parameter constraint, resource limit, lifetime). Ordered by `⪯` "
            "(`A_1 ⪯ A_2` = A_1 grants no more authority than A_2); derivation "
            "satisfies `derive(A,C) ⪯ A`. Authority is kernel-private: the evaluator "
            "sees only `CapRef`s and can never inspect it."
        ),
        owner="MOD-03",
        owner_crate="ror-kernel",
        first_definition=A(488, 2, "struct Authority {"),
        frozen_at=A(6375, 11, "$$A_o = \\langle S, Q, R, T \\rangle$$"),
        forbidden=[
            "CapRef (as a synonym)",
            "capability reference",
            "permission set",
            "rights",
            "token",
        ],
        protected=[
            ("Authority", "frozen mathematical name AND a frozen Rust generic type name "
                          "(`Authority<S,Q,R,L>`, L6501) — both retained"),
            ("A", "frozen mathematical symbol"),
            ("A_o", "frozen symbol for the per-operation authority"),
            ("A_c", "frozen symbol for `Authority(c)`, the authority behind CapRef c"),
            ("κ(c)", "frozen notation for the same object via the capability map"),
            ("Authority(c)", "frozen notation; `AuthOK(c,E,t) ⇔ Valid(c,t) ∧ "
                             "Authorized(Authority(c),E,t)` (L7323)"),
            ("S", "the scope component symbol — collides with Slots and Snapshot (X-10)"),
            ("Q", "the parameter-constraint component symbol"),
            ("R", "the resource-limit component symbol — collides with Reserved (X-09)"),
            ("T", "the lifetime component symbol in the frozen math (L6375)"),
            ("L", "the lifetime type parameter in the frozen Rust sketch (L6501) — X-17"),
            ("O_granted", "frozen symbol for the granted operation set"),
            ("⪯", "frozen authority partial order"),
            ("⊓", "frozen meet operator used by `derive_op`"),
        ],
        dependents=["T-09", "T-11", "T-12", "T-13"],
        obligations=["R-CAP-01", "R-CAP-02", "R-CAP-03", "R-CORE-04", "R-KERN-03"],
        sections=["S-09", "S-10"],
        collisions=["X-05", "X-08", "X-09", "X-10", "X-11", "X-13", "X-17", "X-25", "X-36", "X-37", "X-38", "X-59", "X-70", "X-77", "X-78", "X-82", "X-84"],
        shape=(
            "A_o = ⟨S, Q, R, T⟩   // L6375, turn [11]\n"
            "A = { (o, A_o) | o ∈ O_granted }   // L6378, turn [11]"
        ),
        note=(
            "The Rust sketch in the SAME turn parameterizes it as `Authority<S,Q,R,L>` "
            "with `lifetime: L` (L6497, L6501) while the frozen math writes `T` for "
            "that component (X-17). Both symbols are recorded; neither is renamed, "
            "because renaming a mathematical symbol would silently alter the frozen "
            "algebra. `Authority` is a concept/math object plus a generic Rust type; "
            "the kernel-private node is `AuthorityNode` (T-11)."
        ),
    ),
    Term(
        tid="T-11",
        canonical="AuthorityNode",
        domain="AUTHORITY",
        type="RUST-STRUCT",
        definition=(
            "The kernel-private per-capability node holding the authority grant and its "
            "lineage. Declared `pub(crate) struct AuthorityNode { ... }` with fields "
            "elided; it MUST remain inaccessible to evaluator/runtime consumers, and "
            "the public capability API exposes only opaque `CapRef` handles."
        ),
        owner="MOD-03",
        owner_crate="ror-kernel",
        first_definition=A(39373, 58, "pub(crate) struct AuthorityNode { ... }"),
        frozen_at=None,
        forbidden=["capability record", "authority struct", "cap entry"],
        protected=[("AuthorityNode", "frozen Rust type name (fields elided in source)")],
        dependents=["T-09", "T-10"],
        obligations=["R-KERN-03", "R-TRUST-03", "R-CAP-05"],
        sections=["S-10"],
        collisions=["X-37", "X-77", "X-82", "X-84"],
        note=(
            "Structure never given (fields elided at L39373). AMB-26 records that "
            "`Authority`/`AuthorityNode`/`CapabilityKernel` are used interchangeably in "
            "places; this dictionary separates them: `Authority` is the grant (T-10), "
            "`AuthorityNode` the kernel-private holder, `CapabilityKernel` the component."
        ),
    ),
    Term(
        tid="T-12",
        canonical="Constraint",
        domain="AUTHORITY",
        type="RUST-STRUCT",
        definition=(
            "A narrowing REQUEST: the argument of `derive`. `Constraint` is not "
            "authority and cannot widen it — `derive(A,C) ⪯ A` and "
            "`derive_op(⟨S,Q,R,T⟩, ⟨S_c,Q_c,R_c,T_c⟩) = ⟨S⊓S_c, Q⊓Q_c, R⊓R_c, T⊓T_c⟩`. "
            "Well-formedness is gated by `AdmissibleConstraint`."
        ),
        owner="MOD-03",
        owner_crate="ror-kernel",
        first_definition=A(6536, 11, "pub struct Constraint<S, Q, R, L> {"),
        frozen_at=None,
        forbidden=["authority", "capability", "permission", "scope (unqualified)"],
        protected=[
            ("Constraint", "frozen Rust type name and frozen algebra object"),
            ("C", "the frozen symbol for a Constraint in `derive(A,C)` — collides with "
                  "Consumable `C` (X-08); both retained"),
            ("C_req", "frozen symbol for the required constraint in E-Attenuate (L8717)"),
            ("σ", "frozen symbol for a constraint in the turn-[5] attenuate rule (L2247)"),
            ("AdmissibleConstraint", "frozen trait name (status ambiguous, U-09/AMB-12)"),
        ],
        dependents=["T-10", "T-09", "T-15"],
        obligations=["R-CAP-04", "R-CAP-02", "R-CORE-04"],
        sections=["S-09"],
        collisions=["X-08", "X-16", "X-17", "X-70", "X-77", "X-78", "X-84"],
        note=(
            "No canonical byte encoding exists for `Constraint` in the frozen 15A tag "
            "set, although `Expr::Attenuate` embeds one as an immediate (C-16, U-02)."
        ),
    ),
    Term(
        tid="T-13",
        canonical="CapabilityKernel",
        domain="AUTHORITY",
        type="COMPONENT",
        definition=(
            "The trusted authority-decision layer: allocation, derivation, revocation, "
            "validity and the `Authorized` decision. It is the only component that may "
            "inspect `Authority`; the evaluator asks it and receives a verdict. Trusted "
            "per the trust table (R-TRUST-01)."
        ),
        owner="MOD-03",
        owner_crate="ror-kernel",
        first_definition=A(6680, 11, "pub struct CapRef {"),
        frozen_at=None,
        forbidden=["kernel (unqualified, where the CEK machine is meant)", "authority manager", "cap manager"],
        protected=[
            ("CapabilityKernel", "frozen component name; trust-table row"),
            ("kernel", "used in the source's own prose for this component"),
            ("kernel.derive", "frozen operation name in the E-Attenuate rule (L8717)"),
        ],
        dependents=["T-09", "T-10", "T-11", "T-12"],
        obligations=["R-KERN-01", "R-KERN-02", "R-KERN-03", "R-TRUST-03"],
        sections=["S-10"],
        collisions=["X-05", "X-36", "X-37", "X-55", "X-66", "X-70", "X-77", "X-82"],
        note=(
            "`kernel` is context-dependent in the source (capability kernel vs the CEK "
            "machine's core); the qualified name is canonical in prose. AMB-26 records "
            "the interchange."
        ),
    ),
    Term(
        tid="T-14",
        canonical="CapabilityContext",
        domain="AUTHORITY",
        type="RUST-STRUCT",
        definition=(
            "An actor-local binding of names to `CapRef`s — the actor's `κ`. It is part "
            "of `ActorState` (`capabilities: CapabilityContext`) and MUST be included "
            "in snapshots. It holds references only, never `Authority`."
        ),
        owner="MOD-06",
        owner_crate="ror-runtime",
        first_definition=A(25548, 32, "pub capabilities: CapabilityContext,"),
        frozen_at=None,
        forbidden=["actor capability set", "capability table", "κ (as a type name)"],
        protected=[
            ("CapabilityContext", "frozen Rust type name"),
            ("capabilities", "frozen `ActorState` field name"),
            ("κ", "frozen mathematical symbol for the capability map (`κ(c)` lookup)"),
            ("ρ", "the environment symbol — distinct from κ; never conflated"),
        ],
        dependents=["T-09", "T-37", "T-48"],
        obligations=["R-ACTOR-01", "R-ACTOR-02", "R-PERSIST-04"],
        sections=["S-15", "S-18"],
        collisions=["X-37", "X-57", "X-82"],
        note="No canonical byte encoding is frozen for `CapabilityContext` (C-15, U-02).",
    ),
    Term(
        tid="T-15",
        canonical="DelegatedCapability",
        domain="AUTHORITY",
        type="RUST-VARIANT",
        definition=(
            "The marshaller-accepted envelope that carries authority across an actor "
            "boundary by EXPLICIT delegation. Ordinary marshalling recursively rejects "
            "`Value::Capability`; only `Value::DelegatedCapability` is accepted, and "
            "only through the capability kernel. Delegation never amplifies: the "
            "derived authority is `⪯` the delegator's."
        ),
        owner="MOD-06",
        owner_crate="ror-runtime",
        first_definition=A(25989, 32, "Delegate"),
        frozen_at=None,
        forbidden=[
            "capability transfer",
            "capability copy",
            "raw capability passing",
            "marshalled capability",
        ],
        protected=[
            ("DelegatedCapability", "frozen `Value` variant name"),
            ("Expr::Delegate", "frozen AST constructor `{ capability: Box<Expr>, "
                               "constraint: Constraint }` (L25989-25992); absent from the "
                               "turn-[21] 12-constructor `Expr` (AMB-11)"),
            ("delegate", "frozen operation name for cross-actor authority transfer"),
            ("attenuate", "frozen operation name for in-actor narrowing — NOT a synonym "
                          "for delegate"),
            ("derive", "frozen algebra operation — NOT a synonym for either"),
        ],
        dependents=["T-09", "T-12", "T-39"],
        obligations=["R-MARSHAL-01", "R-MARSHAL-02", "R-CORE-07", "R-CAP-04"],
        sections=["S-16"],
        collisions=["X-29", "X-70", "X-77", "X-78"],
        note=(
            "spec/05 §1 separates `derive` (algebra op) / `attenuate` (machine "
            "operation) / `delegate` (cross-actor transfer); that separation is retained "
            "and made a law (N-12) because the source uses the three loosely."
        ),
    ),

    # --------------------------------------------------------------- C. effect
    Term(
        tid="T-16",
        canonical="Effect",
        domain="EFFECT",
        type="RUST-STRUCT",
        definition=(
            "Immutable canonical effect DATA: `{ op: Op, target: Target, params: Params, "
            "cost: Cost }`. An `Effect` is a description, not a request, not an "
            "issuance, and not an invocation. Its canonical bytes are hashed into "
            "`EffectDigest`, which is the effect's semantic identity across the "
            "issuance/receipt/recovery protocol."
        ),
        owner="MOD-08",
        owner_crate="ror-core (type); ror-runtime (protocol)",
        first_definition=A(1166, 3, "pub struct Effect {"),
        frozen_at=A(9297, 17, "pub struct Effect {"),
        forbidden=[
            "side effect (as a type name)",
            "effect request (an Effect is the payload of an EffectRequest)",
            "host call",
            "operation (unqualified — `op` is one field of an Effect)",
            "external effect (that is the theorem-level event `ExternalEffect(E)`, "
            "which additionally requires issuance)",
        ],
        protected=[
            ("Effect", "frozen Rust type name"),
            ("op", "frozen field name"),
            ("target", "frozen field name"),
            ("params", "frozen field name"),
            ("cost", "frozen field name"),
            ("Op", "frozen field type (finite enumerable set; U-21)"),
            ("Target", "frozen field type (domain undefined; U-21)"),
            ("Params", "frozen field type (domain undefined; U-21)"),
            ("Cost", "frozen field type in the turn-[17]/[18] declarations"),
            ("ResourceUsage", "the turn-[11] name of the same field's type (L6541) — "
                              "superseded, retained for traceability (X-26)"),
            ("cap_ref", "field of the turn-[3] `Effect` (L1166) — the frozen form has NO "
                        "capability field; retained, not renamed (X-26)"),
            ("kind", "field of the turn-[3] `Effect` (L1166) — superseded by `op`"),
            ("E", "frozen mathematical symbol for an effect"),
        ],
        dependents=["T-17", "T-21", "T-22"],
        obligations=["R-CALC-04", "R-CALC-05", "R-EFFECT-01"],
        sections=["S-07", "S-12"],
        collisions=["X-04", "X-05", "X-20", "X-26", "X-27", "X-35", "X-36", "X-39", "X-44"],
        shape="pub struct Effect { pub op: Op, pub target: Target, pub params: Params, pub cost: Cost }",
        supersedes=[
            "pub struct Effect { kind: EffectKind, cap_ref: CapRef, target: Target }   // L1166",
            "pub struct Effect { op, target, params, cost: ResourceUsage }   // L6541",
        ],
        note=(
            "spec/05 defines `Effect` as `{capability, operation, target, params, "
            "cost}`. No declaration in the source has that field set: the frozen form "
            "(L9297) has no capability field, and the only form with one is the "
            "superseded turn-[3] `cap_ref`. Because `EffectDigest = "
            "SHA-256(canonical_bytes(effect))`, adding a capability field would bind "
            "the digest to a `CapRef` and change digest semantics. Reported as X-39; "
            "the frozen field set is authoritative."
        ),
    ),
    Term(
        tid="T-17",
        canonical="EffectRequest",
        domain="EFFECT",
        type="RUST-STRUCT",
        definition=(
            "The TRANSIENT machine→host message: `{ id: EffectId, effect: Effect }`. It "
            "exists in memory only; its existence is never evidence of issuance. The "
            "frozen form deliberately carries no `CapRef`: the host adapter never "
            "receives authority, only the effect description and an id."
        ),
        owner="MOD-08",
        owner_crate="ror-runtime",
        first_definition=A(1447, 4, "pub struct EffectRequest {"),
        frozen_at=A(23758, 30, "pub struct EffectRequest {"),
        forbidden=[
            "effect (as a synonym for the request)",
            "issued effect",
            "host invocation",
            "external effect",
            "pending effect (that is `ActorStatus::Pending` / `PendingEffect`)",
        ],
        protected=[
            ("EffectRequest", "frozen Rust type name"),
            ("id", "frozen field name"),
            ("effect", "frozen field name"),
            ("cap", "field of the turn-[4]/[17]/[18] forms (L1449, L9317, L10325, "
                    "L10809) — dropped by the frozen form; retained, not renamed (X-27)"),
        ],
        dependents=["T-16", "T-20", "T-18", "T-42"],
        obligations=["R-EFFECT-01", "R-EFFECT-03", "R-DUR-01"],
        sections=["S-12", "S-13"],
        collisions=["X-04", "X-27", "X-35", "X-57", "X-73", "X-74", "X-86"],
        shape="pub struct EffectRequest { pub id: EffectId, pub effect: Effect }   // L23758",
        supersedes=[
            "pub struct EffectRequest { id: EffectId, cap: CapRef }   // L1447 (no effect field)",
            "pub struct EffectRequest { id, effect, cap: CapRef }   // L9314, L10322, L10806",
        ],
        note="N-04 (`EffectRequest ≠ EffectIssued`) is a durability law, not a naming preference.",
    ),
    Term(
        tid="T-18",
        canonical="EffectIssued",
        domain="EFFECT",
        type="STATE-VS-RECORD",
        definition=(
            "The DURABLE commitment fact that an effect may now be invoked: as a "
            "record `{ id: EffectId, actor: ActorId, effect_digest: EffectDigest, "
            "logical_time: LogicalTime, issue_cost: Consumable, reservation: Reserved "
            "}`; as a WAL record kind `WalRecord::EffectIssued { id, actor, digest }`; "
            "as a lifecycle predicate `Issued(E)`. `HostInvoked(E) ⇒ DurableIssued(E)`: "
            "the host is never invoked before this record is durable. Issuance is NOT "
            "completion."
        ),
        owner="MOD-11",
        owner_crate="ror-persistence (record); ror-runtime (protocol step)",
        first_definition=A(1377, 4, "EffectIssued {"),
        frozen_at=A(23765, 30, "pub struct EffectIssued {"),
        forbidden=[
            "completed effect",
            "executed effect",
            "finished effect",
            "successful effect",
            "issued (as a synonym for the transient request)",
        ],
        protected=[
            ("EffectIssued", "frozen Rust struct name AND frozen `WalRecord` variant "
                             "name AND frozen `EffectJournalEntry::Issued` variant — all "
                             "three retained (X-07)"),
            ("Issued(E)", "frozen lifecycle predicate (`Completed(E) ⇒ Issued(E)`)"),
            ("DurableIssued(E)", "frozen predicate in the durability invariant"),
            ("effect_digest", "frozen field name of the struct form"),
            ("digest", "frozen field name of the WAL/journal variant forms — a DIFFERENT "
                       "field name for the same value; not renamed (X-07)"),
            ("logical_time", "frozen field name (absent from the WAL variant)"),
            ("issue_cost", "frozen field name (absent from the WAL variant)"),
            ("reservation", "frozen field name (absent from the WAL variant)"),
            ("effect_id", "field name of the turn-[3] prose form (L1378) — superseded by `id`"),
        ],
        dependents=["T-17", "T-20", "T-21", "T-47", "T-23"],
        obligations=["R-DUR-01", "R-DUR-02", "R-DUR-03", "R-EFFECT-03", "R-CORE-06"],
        sections=["S-13", "S-18"],
        collisions=["X-07", "X-24", "X-32", "X-57", "X-81"],
        shape=(
            "pub struct EffectIssued { id, actor, effect_digest, logical_time, "
            "issue_cost, reservation }   // L23765\n"
            "WalRecord::EffectIssued { id: EffectId, actor: ActorId, digest: EffectDigest }"
            "   // L35130"
        ),
        supersedes=[
            "EffectIssued { effect_id, capability, effect, target }   // L1377 (turn [3] prose)",
            "ℒ ⊕ EffectIssued(E.id, c, E)   // L2254 (event-log entry carrying the CapRef)",
        ],
        note=(
            "The struct and the WAL variant are NOT the same payload: the variant omits "
            "`logical_time`, `issue_cost` and `reservation` and renames `effect_digest` "
            "to `digest`. Since escrow release on completion needs the reservation, the "
            "divergence is substantive (X-07) and is reported, not reconciled by "
            "renaming either field."
        ),
    ),
    Term(
        tid="T-19",
        canonical="EffectReceipt",
        domain="EFFECT",
        type="RUST-STRUCT",
        definition=(
            "The host→machine RESULT of an invoked effect: `{ id: EffectId, "
            "effect_digest: EffectDigest, result: Result<Value, HostFault> }`. A receipt "
            "is accepted only if BOTH its id and its digest match the issued record; a "
            "mismatch is `ReplayCorruption`/`InvalidReceipt`, never a silent accept. A "
            "receipt is not proof the effect happened — the durable issued record is."
        ),
        owner="MOD-08",
        owner_crate="ror-runtime (validation); ror-host (production)",
        first_definition=A(1454, 4, "pub struct EffectReceipt {"),
        frozen_at=A(23775, 30, "pub struct EffectReceipt {"),
        forbidden=[
            "result (unqualified)",
            "response",
            "completion record (the durable completion is `WalRecord::EffectCompleted`)",
            "acknowledgement",
        ],
        protected=[
            ("EffectReceipt", "frozen Rust type name"),
            ("id", "frozen field name"),
            ("effect_digest", "frozen field name"),
            ("result", "frozen field name"),
            ("HostFault", "frozen error type carried in `result` (variants undefined, U-14)"),
            ("ResultDigest", "frozen newtype for the digest of a result in "
                             "`WalRecord::EffectCompleted` — distinct from `EffectDigest`"),
            ("R", "frozen mathematical symbol for a receipt in the receipt rules (L2021, L7381)"),
        ],
        dependents=["T-18", "T-20", "T-21", "T-42"],
        obligations=["R-EFFECT-06", "R-HOST-03", "R-DUR-03"],
        sections=["S-12", "S-14"],
        collisions=["X-09", "X-43", "X-61", "X-81"],
        shape="pub struct EffectReceipt { pub id: EffectId, pub effect_digest: EffectDigest, pub result: Result<Value, HostFault> }",
        note=(
            "`R` as the receipt symbol (L2021, L7381) collides with `R` = Reserved and "
            "`R` = the authority resource-limit component (X-09)."
        ),
    ),
    Term(
        tid="T-20",
        canonical="EffectId",
        domain="EFFECT",
        type="RUST-NEWTYPE",
        definition=(
            "The monotonic allocation counter value identifying an effect instance: "
            "`pub struct EffectId(pub u64)`, allocated as `h = N_h; N_h' = N_h + 1`, "
            "carried by `GlobalState.next_effect_id`, and given 15A standalone tag "
            "`0x41`. An id is an ALLOCATION identity, not semantic identity: semantic "
            "identity is `EffectDigest`. On a denied request the id is not incremented."
        ),
        owner="MOD-08",
        owner_crate="ror-core (type); ror-runtime (allocation)",
        first_definition=A(9128, 17, "pub type EffectId = u64;"),
        frozen_at=A(23735, 30, "pub struct EffectId(pub u64);"),
        forbidden=[
            "handle (the obsolete v0.3 `h` wording as a current name)",
            "effect handle",
            "effect digest (as a synonym — id and digest have different roles)",
            "effect key",
        ],
        protected=[
            ("EffectId", "frozen type name; 15A standalone tag `0x41`"),
            ("h", "the frozen mathematical symbol for an allocated effect id in the "
                  "v0.3 transition rules (`Pending(h, E, K)`, L8740) — retained in those "
                  "rules; not a current prose name"),
            ("N_h", "frozen symbol for the id allocation counter"),
            ("next_effect_id", "frozen `GlobalState` field name"),
            ("id", "frozen field name wherever an `EffectId` is carried"),
            ("effect_id", "frozen field name in `ActorStatus::Pending` and "
                          "`PendingEffect` — a different spelling of the same value "
                          "(X-22); not renamed"),
        ],
        dependents=["T-17", "T-18", "T-19", "T-21"],
        obligations=["R-CALC-04", "R-EFFECT-02", "R-EFFECT-04", "R-DUR-03"],
        sections=["S-07", "S-12"],
        collisions=["X-07", "X-22", "X-24", "X-43", "X-61", "X-81"],
        shape="pub struct EffectId(pub u64);   // L9342, L23735",
        supersedes=["pub type EffectId = u64;   // L9128 (turn [17], earlier in the same turn)"],
        note=(
            "`pub type EffectId = u64` and `pub struct EffectId(pub u64)` both appear in "
            "turn [17] (L9128 and L9342). An alias cannot carry a distinct 15A tag, and "
            "15A gives `EffectId` tag `0x41` distinct from `ActorId` `0x40`, so the "
            "newtype is the only form consistent with the frozen wire format (X-24). "
            "Both are recorded; neither is renamed."
        ),
    ),
    Term(
        tid="T-21",
        canonical="EffectDigest",
        domain="EFFECT",
        type="RUST-NEWTYPE",
        definition=(
            "`SHA-256(canonical_bytes(effect))` — the SEMANTIC identity of an effect. "
            "Every subsequent record for an effect must carry the identical `EffectId` "
            "AND `EffectDigest`; a digest mismatch is `EffectJournalCorruption`, not a "
            "different effect. The ReplayHost validates ordered id + digest."
        ),
        owner="MOD-08",
        owner_crate="ror-core (type); ror-persistence (validation)",
        first_definition=A(9343, 17, "pub struct EffectDigest([u8; 32]);"),
        frozen_at=A(23738, 30, "pub struct EffectDigest(pub [u8; 32]);"),
        forbidden=["effect hash", "effect checksum", "effect id (as a synonym)"],
        protected=[
            ("EffectDigest", "frozen type name"),
            ("digest", "frozen field name in `WalRecord`/`EffectJournalEntry` variants"),
            ("effect_digest", "frozen field name in the `EffectIssued`/`EffectReceipt` structs"),
            ("ResultDigest", "frozen distinct newtype for a result's digest"),
            ("StateDigest", "frozen distinct newtype for a snapshot's digest"),
            ("ProposalDigest", "frozen distinct name for a proposal's digest (U-13)"),
        ],
        dependents=["T-16", "T-18", "T-19", "T-42"],
        obligations=["R-CALC-04", "R-DUR-03", "R-HOST-03", "R-EFFECT-06"],
        sections=["S-07", "S-13", "S-14"],
        collisions=["X-07", "X-26", "X-39", "X-50"],
        note=(
            "Three digest newtypes coexist (`EffectDigest`, `ResultDigest`, "
            "`StateDigest`) plus `ProposalDigest`; they are distinct and must not be "
            "interchanged. Field spelling differs by carrier (`digest` vs "
            "`effect_digest`) — recorded, not normalized."
        ),
    ),
    Term(
        tid="T-22",
        canonical="EffectCost",
        domain="EFFECT",
        type="RUST-STRUCT",
        definition=(
            "The split cost model of an effect: `{ issue: Consumable, complete_max: "
            "Consumable, reserve: Reserved }`. `issue` is charged at issuance, "
            "`reserve` is escrowed for the reservation, and `complete_max` is the "
            "ABSOLUTE MAXIMUM chargeable at receipt time — escrowing it up front is "
            "what makes guaranteed completion accounting conserve budget."
        ),
        owner="MOD-08",
        owner_crate="ror-core",
        first_definition=A(21390, 29, "pub struct EffectCost {"),
        frozen_at=A(25806, 32, "pub struct EffectCost {"),
        forbidden=["cost (unqualified, where `Cost` the budget pair is meant)", "price", "effect budget"],
        protected=[
            ("EffectCost", "frozen Rust type name"),
            ("issue", "frozen field name"),
            ("complete_max", "frozen field name (renamed from `complete` by the Phase 13 "
                             "correction; `complete_max` is canonical, C-23)"),
            ("complete", "the superseded turn-[29] field name — retained for "
                         "traceability; it under-escrows and is a fixed vulnerability"),
            ("reserve", "frozen field name"),
            ("Cost", "frozen DISTINCT type `{consumable, reserved}` used by "
                     "`Effect.cost` (L9182) — not a synonym for `EffectCost`"),
        ],
        dependents=["T-16", "T-24", "T-25", "T-26"],
        obligations=["R-CALC-05", "R-EFFECT-05", "R-BUDGET-07"],
        sections=["S-07", "S-12"],
        collisions=["X-26", "X-44"],
        note=(
            "`Cost` (the `Effect.cost` pair) and `EffectCost` (the split issue/complete/"
            "reserve model) are different types with overlapping purpose; AMB-23 "
            "records the field-order ambiguity of `EffectCost`."
        ),
    ),
    Term(
        tid="T-23",
        canonical="EffectJournal",
        domain="PERSISTENCE",
        type="CONCEPT",
        definition=(
            "The durable CAUSAL record of effect lifecycle: Prepared → Issued → "
            "Completed, or Issued → Reconciled, with the causal laws `Issued(E) ⇒ "
            "Prepared(E)`, `Completed(E) ⇒ Issued(E)`, `Reconciled(E) ⇒ Issued(E)`. In "
            "the frozen 15B model the journal is NOT a separate structure: its records "
            "are `WalRecord` kinds inside the WAL. A prepared-but-never-issued effect is "
            "discarded; an issued-but-not-completed effect is `Indeterminate`."
        ),
        owner="MOD-11",
        owner_crate="ror-persistence",
        first_definition=A(26134, 33, "- \\(H\\) = durable host-effect journal."),
        frozen_at=A(35127, 47, "pub enum WalRecord {"),
        forbidden=[
            "separate effect journal (superseded: 15B unifies it into the WAL)",
            "effect log",
            "transaction log",
            "audit log",
            "event log (that is `EventLog`, the in-memory machine log)",
        ],
        protected=[
            ("EffectJournal", "frozen name in the boxed recovery theorem (L28427, L28577)"),
            ("H", "frozen mathematical symbol for the journal in `D = ⟨S,L,H⟩` (L26134)"),
            ("EffectJournalEntry", "frozen turn-[33] enum name for journal records "
                                   "(L26222) — superseded by `WalRecord` kinds"),
            ("EffectJournalCorruption", "frozen fault name for a digest mismatch (L35143)"),
            ("EffectPrepared", "frozen `WalRecord` variant"),
            ("EffectCompleted", "frozen `WalRecord` variant"),
            ("EffectReconciled", "frozen `WalRecord` variant"),
        ],
        dependents=["T-18", "T-45", "T-47", "T-50", "T-51"],
        obligations=["R-DUR-02", "R-DUR-03", "R-DUR-04", "R-PERSIST-03", "R-RECOV-02"],
        sections=["S-13", "S-18", "S-19"],
        collisions=["X-07", "X-14", "X-32"],
        note=(
            "The boxed recovery theorem names THREE durable components "
            "(`CommittedSnapshot + DurableLog + EffectJournal`, L28427) while 15B "
            "freezes TWO durable structures (snapshot + WAL, journal as record kinds). "
            "C-25 records the unification but not the theorem site; X-32 reports it."
        ),
    ),
]


TERMS += [
    # ------------------------------------------------------------- D. resource
    Term(
        tid="T-24",
        canonical="Budget",
        domain="RESOURCE",
        type="RUST-STRUCT",
        definition=(
            "The resource bound of an actor/plan: `B = ⟨C, R, W⟩` = "
            "`{ consumable: Consumable, reserved: Reserved, deadline: Deadline }`. "
            "Conservation is explicit and checked: "
            "`C_available + C_escrowed + C_consumed = C_initial`. Checked arithmetic is "
            "required; saturating subtraction is prohibited for semantic accounting."
        ),
        owner="MOD-04",
        owner_crate="ror-core (algebra); gates in ror-runtime/ror-kernel",
        first_definition=A(1788, 4, "\\operatorname{WithinBudget}(e,B)"),
        frozen_at=A(9172, 17, "pub struct Budget {"),
        forbidden=[
            "resource limit (unqualified — that is the authority component `R_A`)",
            "quota",
            "allowance",
            "gas",
            "fuel (that is one dimension of `Consumable`)",
        ],
        protected=[
            ("Budget", "frozen Rust type name and trust-table row"),
            ("B", "frozen mathematical symbol — also used for a block in turn [1] (X-15)"),
            ("B_max", "frozen symbol for a static budget bound in the judgments"),
            ("B_f", "frozen symbol for a closure's budget annotation"),
            ("B_child", "frozen symbol for a spawned actor's budget"),
            ("B_alloc", "frozen symbol for the allocated spawn budget (U-03)"),
            ("R_B", "frozen symbol for the dynamic execution budget (L6420)"),
            ("BudgetAllocationSpec", "frozen `Expr::Spawn` field type (validation rules "
                                     "never stated, U-03)"),
        ],
        dependents=["T-25", "T-26", "T-27", "T-28", "T-29"],
        obligations=["R-BUDGET-01", "R-BUDGET-02", "R-BUDGET-05", "R-CORE-05"],
        sections=["S-11"],
        collisions=["X-08", "X-09", "X-15", "X-19", "X-44", "X-69"],
        shape="pub struct Budget { pub consumable: Consumable, pub reserved: Reserved, pub deadline: Deadline }",
        supersedes=[
            "6-dimension budget ⟨fuel, mem, msgs, calls, io, time⟩   // L1960 (v1)",
            "5-dimension cost algebra ⟨F, M, C, I, W⟩   // L6730 (v0.1)",
        ],
        note=(
            "Dimension drift across v1 → v0.1 → v0.2/v0.3 is recorded as C-06 "
            "(resolved-by-later-text); the frozen form is `⟨C,R,W⟩`. The operational "
            "meaning of the `duration` dimension is still undecided (U-01)."
        ),
    ),
    Term(
        tid="T-25",
        canonical="Consumable",
        domain="RESOURCE",
        type="RUST-STRUCT",
        definition=(
            "The strictly-decreasing budget component `C = ⟨F, I, D⟩` = "
            "`{ fuel: u64, io: u64, duration: u64 }`. Consumables are SPENT and never "
            "returned; escrow moves a quantity from `available` to `escrowed` and "
            "settlement moves it to `consumed`. Dimensions are named fields, not tuple "
            "positions."
        ),
        owner="MOD-04",
        owner_crate="ror-core",
        first_definition=A(7130, 13, "$C = \\langle F, I, D \\rangle$"),
        frozen_at=A(9159, 17, "pub struct Consumable {"),
        forbidden=[
            "spendable resources",
            "fuel (as a synonym for the whole vector)",
            "consumables (as a distinct type from `Consumable`)",
        ],
        protected=[
            ("Consumable", "frozen Rust type name"),
            ("C", "frozen mathematical symbol — ALSO the Constraint of `derive(A,C)` (X-08)"),
            ("fuel", "frozen field name"),
            ("io", "frozen field name"),
            ("duration", "frozen field name (operational meaning undecided, U-01)"),
            ("F", "frozen symbol for the fuel dimension — ALSO the effect set and the "
                  "replay-tuple 'effect invoked' (X-16)"),
            ("I", "frozen symbol for the I/O dimension"),
            ("D", "frozen symbol for the duration dimension — ALSO the durable state "
                  "`D = ⟨S,L,H⟩` (X-12)"),
            ("φ", "the turn-[2] symbol for remaining fuel (L718, L725) — superseded by "
                  "`F`/`fuel`, retained in that text"),
            ("C_available", "frozen partition symbol"),
            ("C_escrowed", "frozen partition symbol"),
            ("C_consumed", "frozen partition symbol"),
            ("C_initial", "frozen partition symbol"),
        ],
        dependents=["T-24", "T-22", "T-29"],
        obligations=["R-BUDGET-01", "R-BUDGET-03", "R-BUDGET-05", "R-CORE-05"],
        sections=["S-11"],
        collisions=['X-08', 'X-12', 'X-16', 'X-18', 'X-19', 'X-44'],
        shape="pub struct Consumable { pub fuel: u64, pub io: u64, pub duration: u64 }",
        note=(
            "The three accounting partitions `available`/`escrowed`/`consumed` are "
            "frozen; the source's informal `held`/`spent`/`remaining` are prose variants "
            "and are forbidden as substitutes (spec/05 §2)."
        ),
    ),
    Term(
        tid="T-26",
        canonical="Reserved",
        domain="RESOURCE",
        type="RUST-STRUCT",
        definition=(
            "The held-then-released budget component `R = ⟨M, S⟩` = "
            "`{ memory: u64, slots: u64 }`. Reservations are checked by "
            "`ReserveOK(r,R) ⇔ R + r ≤ R_max` and released by `ReleaseOK(r,R) ⇔ r ≤ R`. "
            "An indeterminate effect's reservation is NEVER silently released."
        ),
        owner="MOD-04",
        owner_crate="ror-core",
        first_definition=A(7131, 13, "$R = \\langle M, S \\rangle$"),
        frozen_at=A(9166, 17, "pub struct Reserved {"),
        forbidden=[
            "reserved capacity (as a distinct type)",
            "reservation (as a synonym for the vector — a reservation is one held quantity)",
            "escrow (escrow is a partition of `Consumable` accounting)",
        ],
        protected=[
            ("Reserved", "frozen Rust type name"),
            ("R", "frozen mathematical symbol — ALSO the authority resource-limit "
                  "component and the receipt symbol (X-09)"),
            ("memory", "frozen field name"),
            ("slots", "frozen field name"),
            ("M", "frozen symbol for the memory dimension — ALSO the replay-tuple "
                  "component and the milestone/mutation id prefixes (X-16)"),
            ("S", "frozen symbol for concurrency slots — ALSO Scope and Snapshot (X-10)"),
            ("R_max", "frozen symbol for the reservation ceiling"),
            ("R_A", "frozen symbol for a capability's resource ceiling — a DIFFERENT "
                    "object from the actor's `R`; L6420 states the distinction"),
            ("ReserveOK", "frozen predicate name ([15] correction)"),
            ("ReleaseOK", "frozen predicate name ([15] correction)"),
            ("reservation", "frozen field name in `EffectIssued` and `ActorStatus::Pending`"),
        ],
        dependents=["T-24", "T-22"],
        obligations=["R-BUDGET-01", "R-BUDGET-03", "R-BUDGET-04", "R-CORE-05"],
        sections=["S-11"],
        collisions=["X-07", "X-09", "X-10", "X-16", "X-19", "X-21", "X-22", "X-44", "X-49", "X-74"],
        shape="pub struct Reserved { pub memory: u64, pub slots: u64 }",
        supersedes=["(C ≥ ΔC) ∧ (R + ΔR ≥ 0)   // L7314 — wrong reservation direction (C-07)"],
        note="The direction error of the pre-[15] `BudgetOK` is C-07; `ReserveOK`/`ReleaseOK` are the frozen forms.",
    ),
    Term(
        tid="T-27",
        canonical="Deadline",
        domain="RESOURCE",
        type="RUST-NEWTYPE",
        definition=(
            "An ABSOLUTE logical-time bound `W ∈ ℕ ∪ {∞}`: "
            "`pub struct Deadline(pub Option<LogicalTime>)`, where `Deadline(None)` "
            "means ∞. A deadline is checked, not spent: validity is `t + δ_t ≤ W`. It is "
            "never a wall-clock time."
        ),
        owner="MOD-04",
        owner_crate="ror-core",
        first_definition=A(6748, 11, "3. **Deadline ($W$):**"),
        frozen_at=A(9140, 17, "pub struct Deadline(pub Option<LogicalTime>);"),
        forbidden=[
            "timeout (a timeout implies wall-clock measurement)",
            "time limit",
            "duration (that is the `D` consumable dimension)",
            "expiry (used for capability lifetime `T`, a different bound)",
        ],
        protected=[
            ("Deadline", "frozen Rust type name"),
            ("W", "frozen mathematical symbol"),
            ("DeadlineValid(E,t)", "frozen predicate in the central theorem"),
            ("DeadlineExceeded", "frozen `Fault` variant"),
        ],
        dependents=["T-24", "T-28"],
        obligations=["R-BUDGET-01", "R-BUDGET-06", "R-CAP-09"],
        sections=["S-11"],
        collisions=["X-12", "X-42", "X-69"],
        note="`W` (deadline) vs `D` (duration consumable) vs `T` (capability lifetime) are three distinct bounds.",
    ),
    Term(
        tid="T-28",
        canonical="LogicalTime",
        domain="RESOURCE",
        type="RUST-NEWTYPE",
        definition=(
            "The explicit deterministic time of the machine: `pub struct LogicalTime(pub "
            "u64)`, held once in `GlobalState.logical_time` and advanced only by "
            "transitions with `δ_t > 0` (host/scheduler steps; pure steps have "
            "`δ_t = 0`). It is a component of machine state, never fetched from the host "
            "OS, and never wall-clock."
        ),
        owner="MOD-04",
        owner_crate="ror-core (type); ror-runtime (advance)",
        first_definition=A(6437, 11, "It is an explicit component of the machine state"),
        frozen_at=A(9137, 17, "pub struct LogicalTime(pub u64);"),
        forbidden=[
            "wall-clock time",
            "system time",
            "timestamp (unqualified — the source's 'deterministic timestamp' means logical time)",
            "clock",
            "real time",
            "now",
        ],
        protected=[
            ("LogicalTime", "frozen Rust type name"),
            ("t", "frozen mathematical symbol for the current logical time"),
            ("δ_t", "frozen symbol for a per-transition time delta (values not enumerated, U-07)"),
            ("logical_time", "frozen field name in `GlobalState` and `EffectIssued`"),
        ],
        dependents=["T-27", "T-38", "T-18"],
        obligations=["R-BUDGET-06", "R-CAP-09", "R-CORE-08"],
        sections=["S-11", "S-09"],
        collisions=["X-42"],
        note=(
            "R-CAP-09 prohibits wall-clock time as semantic machine state. The per-"
            "transition `δ_t` values are not frozen (U-07), so `LogicalTime` is defined "
            "but its advancement schedule is not."
        ),
    ),
    Term(
        tid="T-29",
        canonical="CostModel",
        domain="RESOURCE",
        type="RUST-TRAIT",
        definition=(
            "The op→cost mapping contract: `fn cost_c(&self, op: &Op) -> Consumable` "
            "and `fn cost_r(&self, op: &Op) -> Reserved`. It prices operations; it does "
            "not decide admissibility (that is the budget gate) and it does not price "
            "the effect lifecycle split (that is `EffectCost`)."
        ),
        owner="MOD-04",
        owner_crate="ror-core",
        first_definition=A(10168, 18, "pub trait CostModel {"),
        frozen_at=None,
        forbidden=["cost function (as a type name)", "pricer", "meter"],
        protected=[
            ("CostModel", "frozen trait name"),
            ("cost_c", "frozen method name"),
            ("cost_r", "frozen method name"),
            ("Cost", "frozen struct `{consumable, reserved}` — the `Effect.cost` type"),
            ("cost_C", "frozen symbol for the consumable cost function in the v0.3 rules"),
            ("cost_io", "frozen symbol in the receipt rule (L7381)"),
            ("cost_res", "frozen symbol in the receipt rule (L7381)"),
        ],
        dependents=["T-25", "T-26", "T-22", "T-16"],
        obligations=["R-BUDGET-07"],
        sections=["S-11"],
        collisions=["X-19", "X-44"],
        note="`dep/05` §7 records what the cost model does NOT price; that statement is not a terminology source.",
    ),

    # -------------------------------------------------------------- E. machine
    Term(
        tid="T-30",
        canonical="Expr",
        domain="MACHINE",
        type="RUST-ENUM",
        definition=(
            "The frozen core-calculus AST: a closed set of 12 declarative constructors "
            "(`Value, Var, Let, Seq, If, Call, Lambda, Attenuate, Request, Spawn, Send, "
            "Receive`). `Expr` is what an `ExecutablePlan` carries into the machine; it "
            "is not the language surface (`Block`) and not an intermediate stage "
            "(`PlanIR`)."
        ),
        owner="MOD-01",
        owner_crate="ror-core",
        first_definition=A(12145, 21, "pub enum Expr {"),
        frozen_at=None,
        forbidden=[
            "AST (unqualified — `NormalizedAST` is a different, undeclared name)",
            "expression tree",
            "PlanIR (a superseded/undeclared IR name)",
            "code",
        ],
        protected=[
            ("Expr", "frozen Rust enum name"),
            ("Expr::Request", "frozen constructor `{ capability: Box<Expr>, operation: Op, "
                              "target: TargetExpr, params: Vec<Expr> }` (L12183)"),
            ("Expr::Attenuate", "frozen constructor `{ capability, constraint: Constraint, body }`"),
            ("Expr::Spawn", "frozen constructor `{ body, budget: BudgetAllocationSpec }`"),
            ("Expr::Delegate", "frozen constructor at L25989 — ABSENT from the turn-[21] "
                               "12-constructor set (AMB-11); not removed by this dictionary"),
            ("invoke", "the superseded v1/v2 surface name for `Request` (C-17); retained "
                       "in supersession notes only"),
            ("await", "the retracted constructor (U-04); retained for traceability"),
            ("e", "frozen mathematical symbol for an expression"),
        ],
        dependents=["T-06", "T-31", "T-32", "T-33"],
        obligations=["R-CALC-02", "R-CALC-03", "R-COMPILE-01"],
        sections=["S-07"],
        collisions=["X-03", "X-30", "X-35", "X-39", "X-70", "X-79", "X-85", "X-86"],
        shape="pub enum Expr { Value(Value), Var(Symbol), Let{..}, Seq{..}, If{..}, Call{..}, Lambda{..}, Attenuate{..}, Request{..}, Spawn{..}, Send{..}, Receive }",
        note=(
            "`Expr::Request` has two frozen field sets: `{cap, args}` (L10420, turn [18]) "
            "and `{capability, operation, target, params}` (L12183, turn [21]) — X-35."
        ),
    ),
    Term(
        tid="T-31",
        canonical="Value",
        domain="MACHINE",
        type="RUST-ENUM",
        definition=(
            "AMBIGUOUS BY SOURCE DECREE — two incompatible frozen domains share this "
            "name: the machine value domain (11 variants: `Unit, Bool, Integer, Bytes, "
            "Symbol, String, List, Tuple, Function, Capability, Actor`) and the 15A "
            "canonical data domain (8 variants: `Unit, Bool, Integer, String, Symbol, "
            "Capability, List, Map`). This dictionary records both and defers the naming "
            "decision to U-09; it does not rename either."
        ),
        owner="MOD-01",
        owner_crate="ror-core (machine); ror-core/15A (canonical)",
        first_definition=A(12283, 21, "pub enum Value {"),
        frozen_at=None,
        forbidden=[
            "data (unqualified — `Data` is proposed but NOT frozen as the canonical-domain name)",
            "term",
            "object",
        ],
        protected=[
            ("Value", "frozen name of BOTH domains; neither may be renamed without an "
                      "explicit decision (U-09)"),
            ("Value::Capability", "frozen machine-domain variant carrying a `CapRef`"),
            ("Value::Function", "frozen machine-domain variant"),
            ("Value::Map", "frozen canonical-domain variant (absent from the machine domain)"),
            ("FunctionValue", "frozen type `{params, body, env}`; `env: EnvironmentSnapshot` (X-33) "
                              "at L12357 but `env: Environment` at L13987/L14373 (X-85)"),
            ("Value::Null", "source-used spelling L1027 (turn [3]) — every declared `Value` set has `Unit`, not `Null` (X-75)"),
            ("Value::DelegatedCapability", "source-used path L25995/L26000 (turn [32]) — in no `Value` declaration; the declared capability variant is `Capability(Box<CapabilityToken>)` (X-70, X-75)"),
        ],
        dependents=["T-01", "T-30", "T-39", "T-46"],
        obligations=["R-CALC-01", "R-CANON-04", "R-MARSHAL-03"],
        sections=["S-07", "S-17"],
        collisions=["X-28", "X-33", "X-45", "X-54", "X-55", "X-56", "X-70", "X-72", "X-75", "X-76", "X-85"],
        note="Registered upstream as C-03, C-45, U-09, AMB-21. Restated here so the dictionary is complete.",
    ),
    Term(
        tid="T-32",
        canonical="EvalState",
        domain="MACHINE",
        type="RUST-STRUCT",
        definition=(
            "The per-actor evaluation triple `{ expr: Expr, env: Environment, "
            "continuation: Continuation }` — the explicit C/E/K state. A value is "
            "terminal only when its continuation is empty. The evaluator does not use "
            "recursive host-language calls for semantic call-stack management."
        ),
        owner="MOD-05",
        owner_crate="ror-runtime",
        first_definition=A(12655, 21, "pub struct EvalState {"),
        frozen_at=None,
        forbidden=["eval state (as prose)", "stack frame (that is `Frame`)", "CEK (the machine, not the state)"],
        protected=[
            ("EvalState", "frozen Rust type name"),
            ("expr", "frozen field name"),
            ("env", "frozen field name"),
            ("continuation", "frozen field name"),
            ("eval", "frozen `ActorState` field name (`actor.eval.continuation`)"),
            ("CEK", "frozen name of the machine (Control/Environment/Continuation)"),
        ],
        dependents=["T-30", "T-33", "T-37"],
        obligations=["R-CEK-01", "R-CEK-02", "R-ACTOR-02"],
        sections=["S-08"],
        collisions=["X-18", "X-21", "X-22", "X-57", "X-74", "X-79", "X-85", "X-86"],
        note="No canonical byte encoding is frozen for `EvalState` (C-15, U-02).",
    ),
    Term(
        tid="T-33",
        canonical="Frame",
        domain="MACHINE",
        type="RUST-ENUM",
        definition=(
            "A continuation frame — an element of the frozen frame set (R-CEK-03). A "
            "`Continuation` is a stack of `Frame`s. The set is closed; adding a frame "
            "kind is a specification change, not an implementation choice."
        ),
        owner="MOD-05",
        owner_crate="ror-runtime",
        first_definition=A(12453, 21, "pub enum Frame {"),
        frozen_at=A(16943, 25, "pub enum Frame {"),
        forbidden=["stack frame (unqualified)", "continuation (as a synonym for one frame)", "EvalFrame", "ContinuationFrame"],
        protected=[
            ("Frame", "frozen Rust enum name — declared ELEVEN times (AMB-26); all "
                      "declarations are retained"),
            ("Continuation", "frozen distinct type (a stack of frames, L12517)"),
            ("K", "frozen mathematical symbol for a continuation"),
        ],
        dependents=["T-32"],
        obligations=["R-CEK-03"],
        sections=["S-08"],
        collisions=["X-33", "X-37", "X-79", "X-85", "X-86"],
        note=(
            "AMB-26 records the eleven `pub enum Frame` declarations and notes that no "
            "type named `EvalFrame` or `ContinuationFrame` exists in the source; those "
            "names are therefore forbidden as invented identifiers."
        ),
    ),
    Term(
        tid="T-34",
        canonical="ActorId",
        domain="CONCURRENCY",
        type="RUST-NEWTYPE",
        definition=(
            "The identity of an actor: `pub struct ActorId(pub u64)`, allocated from "
            "`GlobalState.next_actor_id`, given 15A standalone tag `0x40`, and used as "
            "the ordering key for deterministic snapshot serialization. An `ActorId` is "
            "a name, not an actor: the actor is `ActorState`."
        ),
        owner="MOD-06",
        owner_crate="ror-core (type); ror-runtime (allocation)",
        first_definition=A(9127, 17, "pub type ActorId = u64;"),
        frozen_at=A(10669, 18, "pub struct ActorId(pub u64);"),
        forbidden=["actor handle", "actor reference (that is `ActorRef`, a value)", "pid", "agent id"],
        protected=[
            ("ActorId", "frozen type name; 15A standalone tag `0x40`"),
            ("N_a", "frozen mathematical symbol for the actor-id counter (L24249)"),
            ("next_actor_id", "frozen `GlobalState` field name"),
            ("a", "frozen mathematical symbol for the acting actor in `G --a,c--> G'`"),
            ("ActorRef", "frozen `Value` variant / spawn result type — distinct from `ActorId`"),
        ],
        dependents=["T-37", "T-38", "T-35"],
        obligations=["R-ACTOR-01", "R-ACTOR-02", "R-CANON-04"],
        sections=["S-15", "S-17"],
        collisions=['X-24'],
        shape="pub struct ActorId(pub u64);",
        supersedes=["pub type ActorId = u64;   // L9127 (turn [17]), L10184 (turn [18])"],
        note="Same alias-vs-newtype collision as `EffectId`; 15A tag `0x40` requires nominal distinctness (X-24).",
    ),
    Term(
        tid="T-35",
        canonical="ActorStatus",
        domain="CONCURRENCY",
        type="RUST-ENUM",
        definition=(
            "The MACHINE-visible status of an actor: `Running | Pending | Blocked | "
            "Halted | Fault`. In the frozen turn-[30] form `Pending` carries "
            "`{ effect_id, effect, reservation }` and the continuation stays in "
            "`actor.eval.continuation`; `Blocked` is a unit variant meaning blocked on "
            "`Receive`. `ActorStatus` is NOT `RunState`: the scheduler never sees "
            "`Runnable` here."
        ),
        owner="MOD-06",
        owner_crate="ror-runtime",
        first_definition=A(9411, 17, "pub enum ActorStatus {"),
        frozen_at=A(23793, 30, "pub enum ActorStatus {"),
        forbidden=[
            "status (unqualified — two distinct enums exist)",
            "RunState (as a synonym)",
            "actor state (that is `ActorState`, the whole record)",
            "run state",
        ],
        protected=[
            ("ActorStatus", "frozen Rust enum name"),
            ("status", "frozen `ActorState`/`A_a` field name carrying an `ActorStatus`"),
            ("Running", "frozen variant"),
            ("Pending", "frozen variant — ALSO a `RunState` variant (distinct enum)"),
            ("Blocked", "frozen variant — ALSO a `RunState` variant"),
            ("Halted", "frozen variant — ALSO a `RunState` variant"),
            ("Fault", "frozen `ActorStatus` variant (carries a `Fault`)"),
            ("PendingEffect", "frozen turn-[17] struct `{id, effect, continuation}` — "
                              "superseded payload of `Pending` (X-22)"),
            ("reservation", "frozen field of the turn-[30] `Pending` variant"),
        ],
        dependents=["T-36", "T-37", "T-18", "T-26"],
        obligations=["R-ACTOR-02", "R-ACTOR-04", "R-CALC-06"],
        sections=["S-15", "S-07"],
        collisions=["X-21", "X-22", "X-23", "X-38", "X-58", "X-65", "X-71", "X-73", "X-74", "X-83"],
        shape="pub enum ActorStatus { Running, Pending { effect_id, effect, reservation }, Blocked, Halted(Value), Fault(Fault) }",
        supersedes=[
            "pub enum ActorStatus { Running, Pending(PendingEffect), Blocked(Continuation), "
            "Halted(Value), Fault(Fault) }   // L9411 (turn [17])",
        ],
        note=(
        "SEVEN declarations in THREE shapes (X-74), not the two X-21 records. Shape (i) "
        "L9411/L10346 (turns [17]/[18]): `Pending(PendingEffect), Blocked(Continuation)` — the "
        "continuation inside `Blocked`. Shape (ii) L21234 (turn [29]): `Pending { effect: "
        "EffectRequest, continuation: Continuation, reservation: ReservedCapacity }, "
        "Blocked(Continuation)` — the continuation in BOTH variants. Shape (iii) L23306/L23793 "
        "(turn [30]): `Pending { effect: EffectRequest, reservation: ReservedCapacity }, Blocked` "
        "— the continuation in NEITHER, which is the form the frozen turn-[30] machine assumes "
        "when it keeps the continuation in `actor.eval.continuation` (T-37, T-32). X-21 covers "
        "the `Running`/`Active` naming split, X-74 the shape split and the seven-declaration "
        "count; C-18/AMB-05 cover `ActorStatus` vs `RunState`, not either split."
        ),
    ),
    Term(
        tid="T-36",
        canonical="RunState",
        domain="SCHEDULING",
        type="RUST-ENUM",
        definition=(
            "The SCHEDULER-visible run state of an actor: `Runnable | Running | Pending "
            "| Blocked | Halted | Faulted`, held as `ActorState.run_state`. `Runnable` "
            "means membership in the `RunnableQueue` (at-most-once). `RunState` is not "
            "`ActorStatus`; the mapping between them is implied by the source but never "
            "tabulated (C-18)."
        ),
        owner="MOD-07",
        owner_crate="ror-runtime",
        first_definition=A(24299, 31, "pub enum RunState {"),
        frozen_at=A(25526, 32, "pub enum RunState {"),
        forbidden=["status (unqualified)", "ActorStatus (as a synonym)", "scheduler state (that is `SchedulerState`, U-02)"],
        protected=[
            ("RunState", "frozen Rust enum name"),
            ("run_state", "frozen `ActorState` field name"),
            ("Runnable", "frozen variant — exists ONLY here, not in `ActorStatus`"),
            ("Faulted", "frozen variant — note the spelling differs from "
                        "`ActorStatus::Fault` (X-23); neither is renamed"),
            ("NotRunnable", "declared variant L24300 (turn [31]) — silently absent from the L25526 (turn [32]) re-declaration, no supersession note (X-75)"),
        ],
        dependents=["T-35", "T-37", "T-40"],
        obligations=["R-ACTOR-02", "R-ACTOR-04", "R-ACTOR-07"],
        sections=["S-15"],
        collisions=["X-21", "X-23", "X-58", "X-73", "X-75", "X-83"],
        note="Both enums are kept by the frozen text (C-18, INFO). The dictionary separates their ownership: ACTOR vs SCHEDULER.",
    ),
    Term(
        tid="T-37",
        canonical="ActorState",
        domain="CONCURRENCY",
        type="RUST-STRUCT",
        definition=(
            "The actor-local state record: `{ id: ActorId, run_state: RunState, eval: "
            "EvalState, capabilities: CapabilityContext, budget: Budget, mailbox: "
            "Mailbox, status: ActorStatus, ... }`. Actors isolate environments, "
            "continuations, heaps, mailboxes, budgets and capability contexts. "
            "Mathematically `A_a = ⟨e, ρ, κ, ℋ, C, R, W, mailbox, status⟩`."
        ),
        owner="MOD-06",
        owner_crate="ror-runtime",
        first_definition=A(8111, 15, "ActorState="),
        frozen_at=A(25544, 32, "pub struct ActorState {"),
        forbidden=["agent state", "actor", "A (unqualified — `A` is Authority)"],
        protected=[
            ("ActorState", "frozen Rust type name"),
            ("A_a", "frozen mathematical symbol for actor a's state (L8666)"),
            ("A_A", "the turn-[1] notation for actor A's state (L340) — superseded"),
            ("id", "frozen field name"),
            ("run_state", "frozen field name"),
            ("eval", "frozen field name"),
            ("capabilities", "frozen field name"),
            ("budget", "frozen field name"),
            ("mailbox", "frozen field name"),
            ("ℋ", "frozen symbol for the actor's isolated heap/arena"),
        ],
        dependents=["T-34", "T-35", "T-36", "T-32", "T-14", "T-24", "T-39"],
        obligations=["R-ACTOR-01", "R-ACTOR-02", "R-ACTOR-03", "R-PERSIST-04"],
        sections=["S-15"],
        collisions=["X-11", "X-14", "X-18", "X-74", "X-76", "X-83"],
        shape="A_a = ⟨e, ρ, κ, ℋ, C, R, W, mailbox, status⟩   // L8666, turn [16]",
        note=(
            "In `A_a`'s own definition the symbols `C` and `R` are the BUDGET components, "
            "while `A` elsewhere is AUTHORITY (X-11, X-08, X-09). The dictionary "
            "requires qualified prose: 'the actor state A_a' vs 'the authority A'."
        ),
    ),
    Term(
        tid="T-38",
        canonical="GlobalState",
        domain="MACHINE",
        type="RUST-STRUCT",
        definition=(
            "The frozen global machine configuration: `{ actors: BTreeMap<ActorId, "
            "ActorState>, logical_time: LogicalTime, runnable: RunnableQueue, event_log: "
            "EventLog, next_effect_id: EffectId, next_actor_id: ActorId }`. It is the "
            "object transitions act on (`G --a,c--> G'`) and the object a snapshot "
            "commits."
        ),
        owner="MOD-05",
        owner_crate="ror-runtime",
        first_definition=A(24156, 31, "pub struct GlobalState {"),
        frozen_at=A(25535, 32, "pub struct GlobalState {"),
        forbidden=[
            "GlobalConfig (the obsolete v0.3 name; C-42)",
            "machine state (unqualified — `Σ` and the 7-tuple also claim it, X-18)",
            "world state",
            "global config",
        ],
        protected=[
            ("GlobalState", "frozen Rust type name"),
            ("G", "frozen mathematical symbol (turn [15]/[16] transition rules)"),
            ("GlobalConfig", "the v0.3 name (L8653, L11061) — superseded, retained in "
                             "supersession notes (C-42)"),
            ("Σ", "the turn-[2] machine-configuration symbol `⟨P,ρ,κ,ℋ,φ,𝓔⟩` (L718) — "
                  "superseded, retained (X-18)"),
            ("actors", "frozen field name"),
            ("logical_time", "frozen field name"),
            ("runnable", "frozen field name"),
            ("event_log", "frozen field name"),
            ("SchedulerState", "a component named in the source whose shape is never "
                               "given (U-02)"),
        ],
        dependents=["T-34", "T-37", "T-28", "T-40", "T-49", "T-48"],
        obligations=["R-ACTOR-02", "R-PERSIST-04", "R-CORE-08"],
        sections=["S-15", "S-18"],
        collisions=["X-18", "X-46", "X-83"],
        shape="pub struct GlobalState { actors, logical_time, runnable, event_log, next_effect_id, next_actor_id }",
        note="No canonical byte encoding is frozen for `GlobalState` (C-15, U-02), yet R-PERSIST-04/05 require one.",
    ),
    Term(
        tid="T-39",
        canonical="Mailbox",
        domain="CONCURRENCY",
        type="CONCEPT",
        definition=(
            "The per-actor FIFO of `MarshalledValue`s. A `Send` is asynchronous and "
            "enqueues; a `Receive` blocks the actor when the mailbox is empty. Ordinary "
            "marshalling recursively rejects capabilities, so a mailbox can never carry "
            "raw authority."
        ),
        owner="MOD-06",
        owner_crate="ror-runtime",
        first_definition=A(8666, 16, "mailbox"),
        frozen_at=None,
        forbidden=["queue (unqualified — `RunnableQueue` is a different FIFO)", "inbox", "message buffer"],
        protected=[
            ("Mailbox", "frozen name"),
            ("mailbox", "frozen `ActorState` field name and `A_a` component symbol"),
            ("MarshalledValue", "frozen element type (canonical bytes transport)"),
            ("RunnableQueue", "frozen DISTINCT FIFO — the scheduler's queue, not a mailbox"),
            ("Deadlock", "frozen condition detected when all actors block (L25579)"),
        ],
        dependents=["T-37", "T-15", "T-36"],
        obligations=["R-ACTOR-03", "R-ACTOR-06", "R-MARSHAL-01", "R-MARSHAL-03"],
        sections=["S-15", "S-16"],
        collisions=["X-45", "X-76", "X-83"],
        note="No canonical byte encoding is frozen for `Mailbox` (C-15, U-02).",
    ),
    Term(
        tid="T-40",
        canonical="RunnableQueue",
        domain="SCHEDULING",
        type="CONCEPT",
        definition=(
            "The scheduler's FIFO of runnable actors with at-most-once membership: an "
            "actor is enqueued when it becomes `Runnable` and a duplicate runnable entry "
            "is a defect (mutation M014). The baseline scheduler grants one CEK "
            "transition per actor turn; blocked actors are never scheduled."
        ),
        owner="MOD-07",
        owner_crate="ror-runtime",
        first_definition=A(25538, 32, "pub runnable: RunnableQueue,"),
        frozen_at=None,
        forbidden=["run queue", "scheduler queue (acceptable prose, not a type name)", "mailbox", "ready set"],
        protected=[
            ("RunnableQueue", "frozen Rust type name"),
            ("runnable", "frozen `GlobalState` field name"),
            ("Runnable", "frozen `RunState` variant"),
            ("ActorSelected", "frozen event name for a turn grant (L25567)"),
            ("Scheduler", "frozen component name; trust-table row 'Deterministic interleaving' (C-37)"),
        ],
        dependents=["T-36", "T-38"],
        obligations=["R-ACTOR-04", "R-ACTOR-07", "R-CORE-08"],
        sections=["S-15"],
        collisions=["X-83"],
        note=(
            "The snapshot is said to contain the runnable queue while recovery "
            "reconstructs it from actor states (C-26, U-17): which is authoritative on "
            "mismatch is undecided."
        ),
    ),
]


TERMS += [
    # ----------------------------------------------------------------- F. host
    Term(
        tid="T-41",
        canonical="HostPolicy",
        domain="HOST",
        type="RUST-TRAIT",
        definition=(
            "The host-side policy gate, deliberately separate from the capability "
            "kernel: an independent defence-in-depth check that the concrete host is "
            "willing to perform this effect. Machine step 11 fails early on it "
            "(`HostPolicyOK(E)`), and the host's own check remains authoritative. A "
            "denial is `Fault::HostPolicyDenied(HostPolicyError)`."
        ),
        owner="MOD-09",
        owner_crate="ror-host",
        first_definition=A(10163, 18, "pub trait HostPolicy {"),
        frozen_at=A(21893, 29, "pub trait HostPolicy {"),
        forbidden=[
            "capability check (that is the kernel's `Authorized`)",
            "authorization (unqualified — `Authorized` is the kernel predicate)",
            "permission check",
            "security policy",
        ],
        protected=[
            ("HostPolicy", "frozen trait name"),
            ("is_permitted", "frozen method of the turn-[18] form, `-> bool` (L10164)"),
            ("authorize", "frozen method of the turn-[29] form, "
                          "`-> Result<(), HostPolicyError>` (L21894) — see X-20"),
            ("HostPolicyOK(E)", "frozen predicate, Gate 3 of E-Request (L8733) and a "
                                "conjunct of the central theorem"),
            ("HostPolicyError", "frozen error type (variants never enumerated, U-14)"),
            ("HostPolicyDenied", "frozen `Fault` variant (L23811)"),
            ("HostPolicyViolation", "the v0.3 rule's fault name (L8748-8757, L8925) — "
                                    "unreconciled with `HostPolicyDenied` (AMB-08)"),
            ("HostAuthorized(E)", "the turn-[7]/[13] predicate name for the same gate (L3297, L7103)"),
        ],
        dependents=["T-16", "T-17", "T-43"],
        obligations=["R-HOST-01", "R-CORE-02", "R-EFFECT-03"],
        sections=["S-14", "S-12"],
        collisions=['X-20', 'X-38', 'X-58', 'X-59', 'X-67'],
        shape="pub trait HostPolicy { fn authorize(&self, effect: &Effect) -> Result<(), HostPolicyError> }",
        supersedes=["pub trait HostPolicy { fn is_permitted(&self, effect: &Effect) -> bool }   // L10163"],
        note=(
            "The two forms are not equivalent: `-> bool` cannot distinguish 'denied' "
            "from 'policy error', so it cannot produce `HostPolicyError`. X-20 reports "
            "this; the dictionary records both and requires an explicit decision."
        ),
    ),
    Term(
        tid="T-42",
        canonical="ReplayHost",
        domain="HOST",
        type="RUST-STRUCT",
        definition=(
            "The recorded-effect host: an ordered trace of `EffectReceipt`s consumed by "
            "a cursor, which NEVER touches the external world and validates each "
            "request's id and digest against the next trace entry. Trusted "
            "(R-TRUST-01). An unordered map is explicitly not the normative replay "
            "mechanism."
        ),
        owner="MOD-09",
        owner_crate="ror-host",
        first_definition=A(1234, 3, "pub struct ReplayHost {"),
        frozen_at=A(34498, 46, "pub struct ReplayHost {"),
        forbidden=[
            "recorded host",
            "mock host (that is `PanicHost`/test doubles, a different object)",
            "replay cache",
            "receipt map",
        ],
        protected=[
            ("ReplayHost", "frozen Rust type name; trust-table row"),
            ("trace", "frozen field name of the ordered form"),
            ("cursor", "frozen field name"),
            ("recorded_receipts", "field name of the superseded `HashMap` form (L24012) — "
                                  "retained, not renamed (C-22)"),
            ("HostFault::ReplayTraceExhausted", "frozen fault variant"),
            ("ReplayCorruption", "frozen `Fault` variant for id/digest mismatch"),
        ],
        dependents=["T-19", "T-17", "T-21", "T-44"],
        obligations=["R-HOST-03", "R-HOST-04", "R-EFFECT-06"],
        sections=["S-14"],
        collisions=["X-43", "X-67", "X-81", "X-84"],
        shape="pub struct ReplayHost { trace: Vec<EffectReceipt>, cursor: usize }",
        supersedes=[
            "pub struct ReplayHost { recorded_receipts: HashMap<EffectId, EffectReceipt>, "
            "cursor: usize }   // L24011 (turn [30]) — C-22",
        ],
        note="C-22 resolves HashMap→ordered; X-43 records that the field name also changed (`recorded_receipts`→`trace`).",
    ),
    Term(
        tid="T-43",
        canonical="LiveHost",
        domain="HOST",
        type="RUST-STRUCT",
        definition=(
            "The external-world host adapter that actually invokes the OS/network. It is "
            "PARTIALLY trusted (R-TRUST-01): it may perform the effect, but it never "
            "decides authorization, never sees `Authority`, and is invoked only after "
            "durable issuance."
        ),
        owner="MOD-09",
        owner_crate="ror-host",
        first_definition=A(1191, 3, "pub struct LiveHost {"),
        frozen_at=None,
        forbidden=["host (unqualified — three hosts exist)", "OS adapter", "syscall layer", "real host"],
        protected=[
            ("LiveHost", "frozen Rust type name; trust-table row 'Live host / Partial'"),
            ("HostExecutor", "frozen trait both hosts implement"),
            ("Host", "frozen `Fault` variant carrying a `HostFault`"),
            ("HostFault", "frozen error type (variants undefined, U-14)"),
            ("HostInvoked(E)", "frozen predicate in the durability invariant"),
        ],
        dependents=["T-17", "T-19", "T-41", "T-44"],
        obligations=["R-HOST-01", "R-HOST-02", "R-CORE-06", "R-TRUST-01"],
        sections=["S-14"],
        collisions=[],
        note=(
            "Three hosts must never be conflated: `LiveHost` (external world, partial "
            "trust), `ReplayHost` (recorded, trusted), and the test doubles "
            "`PanicHost`/`MockKernel` (infrastructure, MOD-17)."
        ),
    ),
    Term(
        tid="T-44",
        canonical="HostExecutor",
        domain="HOST",
        type="RUST-TRAIT",
        definition=(
            "The host boundary contract: `fn execute(&mut self, request: &EffectRequest) "
            "-> Result<EffectReceipt, HostFault>`. It is the single seam at which the "
            "machine meets the external world, and therefore the seam the live/replay "
            "distinction is drawn across."
        ),
        owner="MOD-09",
        owner_crate="ror-host",
        first_definition=A(1187, 3, "pub trait HostExecutor {"),
        frozen_at=None,
        forbidden=["host trait", "host interface", "FFI boundary"],
        protected=[("HostExecutor", "frozen trait name"), ("execute", "frozen method name")],
        dependents=["T-17", "T-19", "T-42", "T-43"],
        obligations=["R-HOST-01", "R-HOST-02", "R-HOST-03"],
        sections=["S-14"],
        collisions=['X-67'],
        note="",
    ),

    # --------------------------------------------------------- G. persistence
    Term(
        tid="T-45",
        canonical="WAL",
        domain="PERSISTENCE",
        type="CONCEPT",
        definition=(
            "The Write-Ahead Log: the DURABLE, strictly ordered, gap-checked append log "
            "that makes `HostInvoked(E) ⇒ DurableIssued(E)` enforceable. Framed by "
            "`WalFrame`, populated by `WalRecord`, sequenced by `WalSequence`. The WAL is "
            "not the in-memory `EventLog`, and in the frozen 15B model it also carries "
            "the effect-journal record kinds."
        ),
        owner="MOD-11",
        owner_crate="ror-persistence",
        first_definition=A(27716, 34, "strict Write-Ahead Log (WAL) ordering"),
        frozen_at=A(35099, 47, "pub struct WalFrame {"),
        forbidden=[
            "event log (that is `EventLog`, in-memory)",
            "journal (unqualified — `EffectJournal` is a record-kind family inside the WAL)",
            "log (unqualified)",
            "transaction log",
            "persistence log",
        ],
        protected=[
            ("WAL", "frozen abbreviation; first token at L27706, defined at L27716"),
            ("Write-Ahead Log", "frozen expansion"),
            ("L", "frozen mathematical symbol for the durable log in `D = ⟨S,L,H⟩` (L26133)"),
            ("DurableLog", "frozen name in the boxed recovery theorem (L28427)"),
            ("WalFrame", "frozen framing type"),
            ("WalRecord", "frozen record-kind enum"),
            ("WalSequence", "frozen sequence newtype"),
            ("WalRecordKind", "frozen u8 discriminant type of `WalFrame.kind`"),
            ("WAL-GAP-REJECT", "frozen verification-obligation tag"),
            ("WAL-SEQUENCE-CONTINUITY", "frozen verification-obligation tag"),
        ],
        dependents=["T-46", "T-47", "T-49", "T-23", "T-48"],
        obligations=["R-PERSIST-01", "R-PERSIST-02", "R-PERSIST-03", "R-DUR-01", "R-CORE-06"],
        sections=["S-18", "S-13"],
        collisions=["X-13", "X-14", "X-17", "X-31", "X-32", "X-47", "X-54", "X-57", "X-61", "X-71", "X-80"],
        note=(
            "Five names denote this one durable structure (`WAL`, `Write-Ahead Log`, "
            "`L`, `DurableLog`, 'append-only durable event log'), and a sixth "
            "(`EventLog`) denotes a DIFFERENT in-memory one. U-16/AMB-14 concern the "
            "`EventSequence`/`WalSequence` relationship; X-31 records the naming spread."
        ),
    ),
    Term(
        tid="T-46",
        canonical="WalFrame",
        domain="PERSISTENCE",
        type="RUST-STRUCT",
        definition=(
            "The frozen durable frame: `{ sequence: WalSequence, kind: WalRecordKind, "
            "payload_length: u32, payload: Vec<u8>, checksum: [u8;32] }` with "
            "`checksum = SHA-256(sequence ‖ kind ‖ payload_length ‖ payload)`. The parser "
            "MUST reject truncated headers/payloads, impossible lengths, checksum "
            "mismatches, invalid record kinds, sequence regressions, sequence gaps, "
            "malformed canonical payloads, and trailing bytes."
        ),
        owner="MOD-11",
        owner_crate="ror-persistence",
        first_definition=A(34237, 46, "pub struct WalFrame {"),
        frozen_at=A(35099, 47, "pub struct WalFrame {"),
        forbidden=["log frame", "record frame", "WAL entry (ambiguous: frame vs record)"],
        protected=[
            ("WalFrame", "frozen Rust type name"),
            ("sequence", "frozen field name"),
            ("kind", "frozen field name"),
            ("payload_length", "frozen field name"),
            ("payload", "frozen field name"),
            ("checksum", "frozen field name"),
            ("s_{n+1} = s_n + 1", "frozen gap-check formula"),
        ],
        dependents=["T-45", "T-47"],
        obligations=["R-PERSIST-01", "R-PERSIST-02"],
        sections=["S-18"],
        collisions=["X-31", "X-47", "X-50", "X-80", "X-84"],
        shape="pub struct WalFrame { sequence, kind, payload_length, payload, checksum }",
        note="`WalFrame.kind` is a `WalRecordKind` u8 discriminant, distinct from the 15A envelope `type_tag`.",
    ),
    Term(
        tid="T-47",
        canonical="WalRecord",
        domain="PERSISTENCE",
        type="RUST-ENUM",
        definition=(
            "The frozen WAL record taxonomy: `Event(EventEnvelope) | EffectPrepared{id,"
            "actor,digest} | EffectIssued{id,actor,digest} | EffectCompleted{id,digest,"
            "result_digest} | EffectReconciled{id,digest,outcome} | SnapshotCommit{"
            "event_sequence,snapshot_version,state_digest}`. The causal laws "
            "`Issued(E) ⇒ Prepared(E)`, `Completed(E) ⇒ Issued(E)`, `Reconciled(E) ⇒ "
            "Issued(E)` are read off these kinds."
        ),
        owner="MOD-11",
        owner_crate="ror-persistence",
        first_definition=A(27724, 34, "pub enum WalRecord {"),
        frozen_at=A(35127, 47, "pub enum WalRecord {"),
        forbidden=["WAL entry", "log record", "journal entry (the superseded `EffectJournalEntry`)"],
        protected=[
            ("WalRecord", "frozen Rust enum name"),
            ("Event", "frozen variant"),
            ("EffectPrepared", "frozen variant"),
            ("EffectIssued", "frozen variant — same name as the T-18 struct (X-07)"),
            ("EffectCompleted", "frozen variant"),
            ("EffectReconciled", "frozen variant"),
            ("SnapshotCommit", "frozen variant"),
            ("digest", "frozen field name in the effect variants (vs `effect_digest` in "
                       "the structs — X-07)"),
            ("result_digest", "frozen field name"),
            ("outcome", "frozen field name"),
            ("event_sequence", "frozen field name"),
            ("snapshot_version", "frozen field name"),
            ("state_digest", "frozen field name"),
        ],
        dependents=["T-45", "T-46", "T-18", "T-23", "T-48", "T-51"],
        obligations=["R-PERSIST-03", "R-DUR-02", "R-DUR-03", "R-DUR-04"],
        sections=["S-18", "S-13"],
        collisions=["X-07", "X-24", "X-31", "X-32", "X-33", "X-47", "X-61", "X-71", "X-72", "X-80", "X-84"],
        shape="pub enum WalRecord { Event(EventEnvelope), EffectPrepared{..}, EffectIssued{..}, EffectCompleted{..}, EffectReconciled{..}, SnapshotCommit{..} }",
        supersedes=[
            "pub enum EffectJournalEntry { Prepared{..}, Issued{..}, Completed{..}, "
            "Reconciled{..} }   // L26222 (turn [33]) — unified into WalRecord by 15B (C-25)",
        ],
        note=(
            "Variant names are `Effect`-prefixed here but unprefixed in the superseded "
            "`EffectJournalEntry`. Both spellings are frozen in their own era; neither "
            "is renamed (X-07)."
        ),
    ),
    Term(
        tid="T-48",
        canonical="Snapshot",
        domain="PERSISTENCE",
        type="CONCEPT",
        definition=(
            "A committed, self-consistent, canonically encoded image of `GlobalState` "
            "with a version and a state digest. The frozen type is `GlobalSnapshot`; the "
            "commit fact is the `WalRecord::SnapshotCommit` record; the integrity "
            "property is `CommittedSnapshot(S) ⇒ S is self-consistent`. A corrupted or "
            "incomplete snapshot is IGNORED, never repaired. Snapshots MUST include "
            "actors' capability contexts."
        ),
        owner="MOD-11",
        owner_crate="ror-persistence",
        first_definition=A(26132, 33, "- \\(S\\) = persisted `GlobalState` snapshot,"),
        frozen_at=A(26301, 33, "pub struct GlobalSnapshot {"),
        forbidden=[
            "checkpoint (unqualified — the source's 'compare against checkpoint' is a "
            "recovery step, not the type)",
            "state dump",
            "image",
            "EnvironmentSnapshot (a closure-environment capture, unrelated to persistence)",
        ],
        protected=[
            ("Snapshot", "frozen concept name; trust-table row 'Persistence'"),
            ("GlobalSnapshot", "frozen Rust type name"),
            ("S", "frozen mathematical symbol for the snapshot in `D = ⟨S,L,H⟩` (L26127, glossed L26132) "
                  "— collides with Scope and Slots (X-10)"),
            ("CommittedSnapshot(S)", "frozen predicate"),
            ("SnapshotCommit", "frozen `WalRecord` variant"),
            ("SnapshotVersion", "frozen field type of `GlobalSnapshot.version`"),
            ("StateDigest", "frozen newtype for the snapshot digest"),
            ("version", "frozen field name"),
            ("state_digest", "frozen field name"),
            ("EnvironmentSnapshot", "frozen but UNDEFINED type used once, as "
                                    "`FunctionValue.env` (L12357) — X-33"),
            ("SNAPSHOT-COMMIT-INTEGRITY", "frozen verification-obligation tag"),
        ],
        dependents=["T-38", "T-14", "T-47", "T-45", "T-52"],
        obligations=["R-PERSIST-04", "R-PERSIST-05", "R-PERSIST-06", "R-RECOV-03"],
        sections=["S-18", "S-19"],
        collisions=["X-10", "X-33", "X-45", "X-51", "X-83", "X-85"],
        shape="pub struct GlobalSnapshot { version: SnapshotVersion, ... }   // L26301, L34122",
        note=(
            "`Snapshot` is a concept whose frozen type name is `GlobalSnapshot`; "
            "`EnvironmentSnapshot` shares the word and denotes something unrelated "
            "(X-33). The runnable queue's authority at recovery is undecided (U-17)."
        ),
    ),
    Term(
        tid="T-49",
        canonical="EventLog",
        domain="PERSISTENCE",
        type="RUST-STRUCT",
        definition=(
            "The IN-MEMORY, strictly append-only machine event log held in "
            "`GlobalState.event_log`, whose elements are `EventEnvelope`s with an "
            "`EventSequence`. It is not durable by itself: durability comes from the "
            "WAL, into which events are written as `WalRecord::Event`. Snapshot "
            "serialization records its LENGTH, not its contents."
        ),
        owner="MOD-11",
        owner_crate="ror-runtime (log); ror-persistence (durable framing)",
        first_definition=A(1086, 3, "pub struct EventLog {"),
        frozen_at=A(26427, 33, "pub struct EventEnvelope {"),
        forbidden=[
            "WAL (as a synonym — the WAL is the durable framing)",
            "journal (as a synonym)",
            "audit log",
            "trace (unqualified — `scheduler_trace`/`host_trace` are different traces)",
        ],
        protected=[
            ("EventLog", "frozen Rust type name"),
            ("event_log", "frozen `GlobalState` field name"),
            ("EventEnvelope", "frozen element type"),
            ("EventSequence", "frozen sequence newtype `pub struct EventSequence(pub u64)`"),
            ("𝓔", "the turn-[2] symbol for the replay/event log in `Σ` (L718) — superseded"),
            ("𝓛", "the turn-[5]/[13] symbol for the log in the transition tuples (L2254)"),
        ],
        dependents=["T-38", "T-45", "T-47"],
        obligations=["R-PERSIST-03", "R-PERSIST-06", "R-ACTOR-02"],
        sections=["S-18"],
        collisions=["X-13", "X-31", "X-47", "X-80"],
        note=(
            "U-16/AMB-14: the relationship between `EventSequence` and `WalSequence` is "
            "never stated. spec/05 §4 records `EventLog` ≠ `WAL`; that separation is "
            "retained here as the canonical reading."
        ),
    ),

    # ------------------------------------------------------------ H. recovery
    Term(
        tid="T-50",
        canonical="Indeterminate",
        domain="RECOVERY",
        type="STATE",
        definition=(
            "The classification of an effect that is `Issued(E) ∧ ¬Completed(E)` before "
            "reconciliation. An indeterminate effect's escrow is NEVER released and it is "
            "NEVER inferred to be `NotExecuted`: the system does not conclude 'did not "
            "happen' from a missing completion record."
        ),
        owner="MOD-12",
        owner_crate="ror-persistence",
        first_definition=A(26576, 33, "Issued(E)\\land\\neg Completed(E)"),
        frozen_at=A(26714, 33, "### Indeterminate"),
        forbidden=[
            "failed effect",
            "not executed",
            "unknown effect",
            "interrupted effect (acceptable prose, not the classification name)",
            "orphaned effect",
        ],
        protected=[
            ("Indeterminate", "frozen classification name and `ReconciliationOutcome` variant"),
            ("EffectRecoveryClass", "frozen enum of effect classes "
                                    "(Replayable/Idempotent/Reversible/Indeterminate, L26669)"),
            ("RECOVERY-ISSUED-INDETERMINATE", "frozen verification-obligation tag"),
        ],
        dependents=["T-18", "T-23", "T-51", "T-52"],
        obligations=["R-DUR-04", "R-RECOV-02", "R-CORE-09", "R-CLAIM-02"],
        sections=["S-19", "S-13"],
        collisions=[],
        note="Releasing an indeterminate effect's escrow is mutation M012 — a registered defect, not a design option.",
    ),
    Term(
        tid="T-51",
        canonical="ReconciliationOutcome",
        domain="RECOVERY",
        type="RUST-ENUM",
        definition=(
            "The closed result set of authoritative host-side resolution of an "
            "indeterminate effect: `pub enum ReconciliationOutcome { "
            "Completed(EffectReceipt), NotExecuted, Indeterminate }`. It is carried by "
            "`WalRecord::EffectReconciled.outcome`. `NotExecuted` here is an "
            "AUTHORITATIVE host statement, not an inference from a missing record."
        ),
        owner="MOD-12",
        owner_crate="ror-persistence (+ ror-host protocol)",
        first_definition=A(26244, 33, "outcome: ReconciliationOutcome,"),
        frozen_at=A(26593, 33, "pub enum ReconciliationOutcome {"),
        forbidden=["recovery result", "resolution", "outcome (unqualified)"],
        protected=[
            ("ReconciliationOutcome", "frozen Rust enum name"),
            ("Completed", "frozen variant (carries an `EffectReceipt`)"),
            ("NotExecuted", "frozen variant — reachable ONLY via authoritative reconciliation"),
            ("Indeterminate", "frozen variant"),
            ("outcome", "frozen field name"),
            ("Replayed", "NOT a variant: the token occurs nowhere in L1-42312 "
                         "(req/00-method §5.2); AMB-15 withdrawn"),
        ],
        dependents=["T-50", "T-19", "T-47"],
        obligations=["R-RECOV-07", "R-DUR-04"],
        sections=["S-19"],
        collisions=["X-61"],
        note=(
            "spec/09 U-15 states the variant set 'is never enumerated'; req/00-method "
            "§5.2 corrects this — the declaration exists at L26593-26597. This "
            "dictionary follows the corrected finding and records the disagreement "
            "rather than silently adopting either text."
        ),
    ),
    Term(
        tid="T-52",
        canonical="RecoveryFault",
        domain="RECOVERY",
        type="RUST-STRUCT",
        definition=(
            "The explicit outcome of invalid persistence state. Recovery either returns "
            "a `GlobalState` or a `RecoveryFault`; it never silently repairs state by "
            "mutation. `Recover(D) = State_before_crash` holds only under the frozen "
            "qualification (every interrupted effect reconciled, idempotent, or "
            "classified indeterminate)."
        ),
        owner="MOD-12",
        owner_crate="ror-persistence",
        first_definition=A(26506, 33, ") -> Result<GlobalState, RecoveryFault> {"),
        frozen_at=None,
        forbidden=["recovery error", "recovery failure (as a type name)", "corruption (unqualified)"],
        protected=[
            ("RecoveryFault", "frozen Rust type name"),
            ("EffectJournalCorruption", "frozen distinct fault for a digest mismatch (L35143)"),
            ("Recover(D)", "frozen function symbol"),
            ("Replay(S,L,H)", "frozen function symbol"),
            ("D", "frozen symbol for the durable state `⟨S,L,H⟩` — collides with the "
                  "duration consumable (X-12)"),
        ],
        dependents=["T-48", "T-45", "T-23", "T-50"],
        obligations=["R-RECOV-01", "R-RECOV-03", "R-CORE-09", "R-CORE-10"],
        sections=["S-19"],
        collisions=['X-12', 'X-13', 'X-32', 'X-58', 'X-67'],
        note="Two recovery step lists exist (12 steps L35193-35204; 19 steps L34344-34364) — AMB-27.",
    ),
    Term(
        tid="T-53",
        canonical="Supervisor",
        domain="RECOVERY",
        type="COMPONENT",
        definition=(
            "The trusted lifecycle and recovery authority: it enforces WAL ordering, "
            "commits snapshots, initiates recovery, and owns reconciliation. It is "
            "trusted (R-TRUST-01) and is not the planner, not the host, and not the "
            "scheduler."
        ),
        owner="MOD-12",
        owner_crate="ror-persistence (+ ror-runtime lifecycle)",
        first_definition=A(3136, 6, "Supervisor observes behavior."),
        frozen_at=A(26799, 33, "# 11. Supervisor"),
        forbidden=["monitor", "watchdog", "orchestrator", "manager"],
        protected=[("Supervisor", "frozen component name; trust-table row")],
        dependents=["T-45", "T-48", "T-52"],
        obligations=["R-PERSIST-01", "R-RECOV-01", "R-TRUST-01"],
        sections=["S-18", "S-19"],
        collisions=[],
        note="",
    ),

    # --------------------------------------------------------------- I. agent
    Term(
        tid="T-54",
        canonical="Observation (planner-facing)",
        domain="AGENT",
        type="RUST-STRUCT",
        definition=(
            "The sanitized machine-state summary handed to the untrusted planner: "
            "`{ sequence: EventSequence, actor: ActorId, value: Option<Value>, events: "
            "Vec<GlobalEvent>, faults: Vec<Fault>, available_capabilities: "
            "CapabilitySummary, budget: BudgetSummary }`. It is the input half of the "
            "LLM outer loop and the basis of the staleness check; it exposes capability "
            "SUMMARIES, never `CapRef`s or `Authority`."
        ),
        owner="MOD-13",
        owner_crate="ror-agent",
        first_definition=A(27156, 33, "pub struct Observation {"),
        frozen_at=None,
        forbidden=[
            "Observation (unqualified — two frozen types share the name, X-06)",
            "telemetry",
            "state dump",
            "normalized observation (that is the differential type, T-57)",
        ],
        protected=[
            ("Observation", "frozen Rust type name — shared with T-57; NOT renamed here "
                            "because renaming a frozen type requires an explicit decision"),
            ("sequence", "frozen field name"),
            ("actor", "frozen field name"),
            ("value", "frozen field name"),
            ("events", "frozen field name"),
            ("faults", "frozen field name"),
            ("available_capabilities", "frozen field name"),
            ("budget", "frozen field name"),
            ("GlobalEvent", "frozen field type — never declared (X-33 family)"),
            ("CapabilitySummary", "frozen field type — never declared"),
            ("BudgetSummary", "frozen field type — never declared"),
            ("observation_sequence", "frozen `PlanProposal` field matched against this "
                                     "observation's sequence"),
        ],
        dependents=["T-02", "T-56", "T-49"],
        obligations=["R-PLANNER-01", "R-PLANNER-03", "R-PLANNER-05"],
        sections=["S-05"],
        collisions=["X-06", "X-29"],
        shape="pub struct Observation { sequence, actor, value, events, faults, available_capabilities, budget }   // L27156",
        note=(
            "The parenthetical qualifier is a DICTIONARY qualification for prose, not a "
            "rename: the Rust identifier in the source is bare `Observation`. X-06 "
            "requires an explicit decision on distinct type names."
        ),
    ),
    Term(
        tid="T-55",
        canonical="PlannerAccepted",
        domain="AGENT",
        type="RUST-STRUCT",
        definition=(
            "The recorded accepted proposal, written so a run can be replayed without "
            "re-querying the (non-deterministic) planner. The planner need not be "
            "deterministic; the RECORD of what it returned is what makes replay "
            "deterministic."
        ),
        owner="MOD-13",
        owner_crate="ror-agent",
        first_definition=A(27411, 33, "pub struct PlannerAccepted {"),
        frozen_at=None,
        forbidden=["recorded proposal (as a type name)", "accepted plan", "proposal log entry"],
        protected=[
            ("PlannerAccepted", "frozen Rust type name"),
            ("ProposalDigest", "frozen field type — canonical form unspecified (U-13)"),
            ("PlannerMetadata", "frozen `PlanProposal` field type — fields never defined (U-13)"),
        ],
        dependents=["T-02", "T-56"],
        obligations=["R-PLANNER-04", "R-PLANNER-05"],
        sections=["S-05"],
        collisions=["X-62"],
        note="U-13 leaves `PlannerMetadata`/`ProposalDigest` and the exact staleness predicate undecided (C-38).",
    ),
    Term(
        tid="T-56",
        canonical="LLMOutput",
        domain="AGENT",
        type="MATH-SYMBOL",
        definition=(
            "The probabilistic producer's output, treated as DATA: `LLMOutput ∈ Data`. "
            "The LLM/planner proposes; it holds no authority and cannot allocate "
            "capabilities, authorize effects, modify budgets or scheduler state, "
            "allocate actors, invoke the host, bypass compilation, or bypass "
            "persistence. `LLMOutput ∧ UntrustedInput ↛ ExternalEffect`."
        ),
        owner="MOD-13",
        owner_crate="ror-agent",
        first_definition=A(27253, 33, "LLMOutput\\in Data"),
        frozen_at=None,
        forbidden=[
            "authority",
            "trusted input",
            "agent decision",
            "the model's plan",
            "instruction",
        ],
        protected=[
            ("LLMOutput", "frozen mathematical symbol in the central invariant"),
            ("LLM / planner", "frozen component name; trust-table row 'No'"),
            ("Planner", "frozen alternate capitalization in source prose"),
            ("UntrustedInput", "frozen symbol"),
            ("Data", "frozen symbol in `LLMOutput ∈ Data`"),
            ("R-CORE-01", "the obligation that states this"),
        ],
        dependents=["T-02", "T-01", "T-54"],
        obligations=["R-CORE-01", "R-PLANNER-01", "R-PLANNER-02", "R-TRUST-01", "R-TRUST-02"],
        sections=["S-02", "S-05", "S-03"],
        collisions=["X-69"],
        note="N-09 (`LLM output ≠ Authority`) is the thesis-level law; R-PLANNER-02 enumerates its eight prohibitions.",
    ),
]


TERMS += [
    # --------------------------------------------------- J. serialization names
    Term(
        tid="T-57",
        canonical="Observation (differential)",
        domain="VERIFICATION",
        type="RUST-STRUCT",
        definition=(
            "The normalized semantic observation both implementations emit for "
            "comparison: `{ terminal_states: Vec<ObservedActor>, event_trace: "
            "Vec<ObservedEvent>, effects: Vec<ObservedEffect>, budgets: "
            "Vec<ObservedBudget>, scheduler_trace: Vec<ObservedSchedulerStep>, faults: "
            "Vec<ObservedFault>, state_digest: Option<ObservedDigest> }`. It is a TEST "
            "representation and must not become a third semantic wire protocol. "
            "`Observe(Production(X)) = Observe(Reference(X))` is the principal oracle."
        ),
        owner="MOD-15",
        owner_crate="ror-differential (comparator); emitted by ror-runtime and ror-reference",
        first_definition=A(36170, 48, "pub struct Observation {"),
        frozen_at=None,
        forbidden=[
            "Observation (unqualified — two frozen types share the name, X-06)",
            "semantic observation (informal; acceptable only as prose for this type)",
            "oracle (that is the reference model in its oracle role)",
            "trace (unqualified)",
            "final value (comparison is never final-value-only)",
        ],
        protected=[
            ("Observation", "frozen Rust type name — shared with T-54; NOT renamed here"),
            ("Observe", "frozen function symbol in the oracle equation"),
            ("terminal_states", "frozen field name"),
            ("event_trace", "frozen field name"),
            ("effects", "frozen field name"),
            ("budgets", "frozen field name"),
            ("scheduler_trace", "frozen field name"),
            ("faults", "frozen field name"),
            ("state_digest", "frozen field name"),
            ("ObservedActor", "frozen field type"),
            ("ObservedEvent", "frozen field type"),
            ("ObservedEffect", "frozen field type"),
            ("ObservedBudget", "frozen field type"),
            ("ObservedSchedulerStep", "frozen field type"),
            ("ObservedFault", "frozen field type"),
            ("ObservedDigest", "frozen field type"),
        ],
        dependents=["T-58", "T-59", "T-31"],
        obligations=["R-REF-05", "R-TEST-02", "R-TEST-03", "R-ARCH-02"],
        sections=["S-20"],
        collisions=["X-06", "X-29"],
        shape="pub struct Observation { terminal_states, event_trace, effects, budgets, scheduler_trace, faults, state_digest }   // L36170",
        note=(
            "The seven `Observed*` element types are named but never declared; that gap "
            "is recorded, not filled. spec/05 §5 lists only this sense under "
            "'Normalized observation' and never mentions the planner-facing `Observation` "
            "(T-54) — X-06."
        ),
    ),
    Term(
        tid="T-58",
        canonical="ReferenceModel",
        domain="VERIFICATION",
        type="COMPONENT",
        definition=(
            "The independently implemented executable model of the frozen semantics, "
            "sharing ZERO core transition logic with production (R-SCOPE-04, R-REF-02). "
            "It is an oracle by comparison, not by construction: it does not make "
            "production correct, and agreement over the tested state space is evidence, "
            "not proof."
        ),
        owner="MOD-14",
        owner_crate="ror-reference",
        first_definition=A(11436, 20, "an independent reference model"),
        frozen_at=A(35283, 48, "Phase 15C defines an independently implemented executable reference model"),
        forbidden=[
            "reference implementation (acceptable prose, not the canonical name)",
            "oracle (informal; the reference model in its oracle role)",
            "golden model",
            "second implementation",
            "specification (a reference model is an implementation of the specification)",
        ],
        protected=[
            ("reference model", "frozen prose name"),
            ("executable reference model", "frozen prose name (15C heading)"),
            ("ror-reference", "frozen crate name"),
            ("Reference", "the axis endpoint in `Production → Observation → Reference`"),
            ("PanicHost", "frozen test double (MOD-17), not part of the reference model"),
            ("MockKernel", "frozen test double (MOD-17)"),
        ],
        dependents=["T-57", "T-59", "T-64", "T-66"],
        obligations=["R-REF-01", "R-REF-02", "R-REF-03", "R-REF-04", "R-SCOPE-04"],
        sections=["S-20"],
        collisions=["X-06", "X-48", "X-60", "X-78", "X-79", "X-84", "X-85"],
        note=(
            "The source also calls it 'the reference machine' (L10128, L15871, L16403) in "
            "the pre-15C era, where it meant the first boring milestone implementation — "
            "a DIFFERENT object from the 15C independent reference model. X-48."
        ),
    ),
    Term(
        tid="T-59",
        canonical="FirstDivergence",
        domain="VERIFICATION",
        type="CONCEPT",
        definition=(
            "The earliest point at which production and reference observations differ, "
            "reported by the comparator instead of a bare pass/fail. Divergences are "
            "adjudicated four ways: production defect, reference defect, harness defect, "
            "specification ambiguity — and specification ambiguity must be resolved "
            "explicitly, never hidden in a test adjustment."
        ),
        owner="MOD-15",
        owner_crate="ror-differential",
        first_definition=A(36655, 48, "First divergence"),
        frozen_at=A(36666, 48, "# 15C.32 First-Divergence Algorithm"),
        forbidden=["first failure", "mismatch point", "diff"],
        protected=[
            ("first divergence", "frozen prose name"),
            ("first_divergence", "frozen counterexample-artifact field"),
            ("Adjudication", "frozen 4-way classification name"),
            ("production defect", "frozen classification"),
            ("reference defect", "frozen classification"),
            ("harness defect", "frozen classification"),
            ("specification ambiguity", "frozen classification"),
        ],
        dependents=["T-57", "T-58", "T-60"],
        obligations=["R-REF-05", "R-TEST-02", "R-TEST-09"],
        sections=["S-20", "S-21"],
        collisions=[],
        note="",
    ),
    Term(
        tid="T-60",
        canonical="Mutation",
        domain="VERIFICATION",
        type="CONCEPT",
        definition=(
            "A deliberately injected known semantic defect (the registry entry) and its "
            "instance in a run (the mutant). The frozen baseline registry is M001-M018; "
            "an equivalent mutant is behaviorally indistinguishable and must be "
            "adjudicated and documented, never counted as a miss."
        ),
        owner="MOD-16",
        owner_crate="mutations/registry.toml (+ ror-testkit)",
        first_definition=A(37187, 49, "### The Critical Gate: Deliberate Fault-Injection Validation (Mutation Testing)"),
        frozen_at=A(38477, 54, "M001"),
        forbidden=["fault injection (unqualified — crash injection is a different suite)", "bug", "defect (unqualified)"],
        protected=[
            ("Mutation", "frozen name"),
            ("mutant", "frozen name for an instance"),
            ("M001…M035", "frozen mutation-registry IDs (M001…M018 baseline; M019…M035 added by frozen addenda I–V)"),
            ("equivalent mutant", "frozen classification"),
            ("non-equivalent mutation", "frozen scope of the 100% target"),
            ("mutations/registry.toml", "frozen file path"),
        ],
        dependents=["T-61", "T-59"],
        obligations=["R-TEST-04", "R-TEST-05", "R-TEST-06"],
        sections=["S-21"],
        collisions=["X-49"],
        note=(
            "`M0NN` mutation IDs share the letter M with milestones `M0`-`M11` and with "
            "the memory symbol `M`; X-49 records the three namespaces."
        ),
    ),
    Term(
        tid="T-61",
        canonical="MutationKillRate",
        domain="VERIFICATION",
        type="MATH-PREDICATE",
        definition=(
            "`MutationKillRate = 100%` over all REGISTERED NON-EQUIVALENT mutations. The "
            "denominator is the registry, not all possible mutants; coverage metrics are "
            "evidence and never replace differential agreement."
        ),
        owner="MOD-16",
        owner_crate="mutations/registry.toml",
        first_definition=A(38506, 54, "\\boxed{MutationKillRate=100\\%}"),
        frozen_at=None,
        forbidden=["mutation score", "kill rate (unqualified, without the scope)", "coverage (that is a different metric)"],
        protected=[
            ("MutationKillRate", "frozen symbol"),
            ("100% kill rate", "frozen target wording"),
            ("kill rate", "frozen informal wording — scope must be stated (C-32)"),
        ],
        dependents=["T-60", "T-59"],
        obligations=["R-TEST-05", "R-TEST-06"],
        sections=["S-21"],
        collisions=[],
        note="C-32 fixes the scope as registered non-equivalent mutants.",
    ),
    Term(
        tid="T-62",
        canonical="CanonicalEnvelope",
        domain="PERSISTENCE",
        type="PROTOCOL-FORMAT",
        definition=(
            "The frozen 15A semantic byte format: `version: u8 | type_tag: u8 | "
            "payload_length: u32 BE | payload`, the ONLY semantic representation. "
            "Rust struct layout is prohibited and `bincode` is explicitly not the "
            "canonical format (it may implement it). Duplicate map keys, trailing bytes "
            "and non-canonical encodings are rejected."
        ),
        owner="MOD-10",
        owner_crate="ror-core (+ vectors/canonical)",
        first_definition=A(28298, 36, "[format_version: u8] [type_tag: u32 LE] [length: u32 LE]"),
        frozen_at=A(38148, 54, "version: u8"),
        forbidden=[
            "wire format (unqualified — the WAL frame is also a wire format)",
            "serialization format",
            "bincode (explicitly NOT the canonical format)",
            "encoding (unqualified)",
        ],
        protected=[
            ("version", "frozen field name (the superseded form spells it `format_version`)"),
            ("type_tag", "frozen field name — `u8` in the frozen form, `u32 LE` in the "
                         "superseded trait doc comment (X-50); neither is renamed"),
            ("payload_length", "frozen field name — `u32 BE`; the superseded form names "
                               "it `length: u32 LE` (X-50)"),
            ("payload", "frozen field name"),
            ("format_version", "superseded field name (L28298) — retained for traceability"),
            ("length", "superseded field name (L28298) — retained for traceability"),
            ("CANONICAL_VERSION", "frozen constant name"),
            ("0x00", "frozen `Value` envelope tag"),
            ("0x20", "frozen `Symbol` tag"),
            ("0x30", "frozen `CapRef` tag"),
            ("0x40", "frozen `ActorId` tag"),
            ("0x41", "frozen `EffectId` tag"),
        ],
        dependents=["T-31", "T-46", "T-63", "T-21"],
        obligations=["R-CANON-01", "R-CANON-02", "R-CANON-03", "R-CANON-04", "R-CANON-06"],
        sections=["S-17"],
        collisions=["X-24", "X-45", "X-50", "X-51", "X-54", "X-55", "X-56", "X-72", "X-76", "X-80"],
        shape="version: u8 | type_tag: u8 | payload_length: u32 BE | payload   // L38147-38150",
        supersedes=[
            "[format_version: u8] [type_tag: u32 LE] [length: u32 LE] [payload]   // L28298 (turn [36])",
        ],
        note=(
            "The superseded form differs in field NAME, tag WIDTH and ENDIANNESS. An "
            "encoder built from the `CanonicalSerialize` doc comment at L28298 would be "
            "wire-incompatible with the frozen format, breaking every digest "
            "(`EffectDigest`, `StateDigest`) and the WAL checksum. X-50; the frozen "
            "form governs, and the superseded text is retained verbatim."
        ),
    ),
    Term(
        tid="T-63",
        canonical="CanonicalPayload",
        domain="PERSISTENCE",
        type="RUST-TRAIT",
        definition=(
            "The frozen canonical-codec trait family: `CanonicalPayload` (a type that "
            "has a canonical byte form, `TYPE_TAG: u8`), `CanonicalEncode` and "
            "`CanonicalDecode` (the fallible codec pair). `CanonicalSerialize` is the "
            "earlier, infallible form whose doc comment carries the superseded envelope "
            "specification."
        ),
        owner="MOD-10",
        owner_crate="ror-core",
        first_definition=A(27685, 34, "pub trait CanonicalSerialize {"),
        frozen_at=A(29979, 41, "pub trait CanonicalPayload: Sized {"),
        forbidden=["serializer (unqualified)", "codec (unqualified)", "marshaller (that is the actor boundary)"],
        protected=[
            ("CanonicalPayload", "frozen trait name"),
            ("CanonicalEncode", "frozen trait name"),
            ("CanonicalDecode", "frozen trait name — declared but not implemented in the "
                                "source's own checklist (L29601)"),
            ("CanonicalSerialize", "frozen EARLIER trait name (L27685, L28296) and a "
                                   "frozen math function symbol `D_S = "
                                   "H(CanonicalSerialize(GlobalState))` (L27061) — "
                                   "retained, not renamed"),
            ("TYPE_TAG", "frozen associated constant"),
            ("CanonicalError", "frozen error type"),
            ("ReadCursor", "frozen decode-cursor type"),
            ("encode_envelope", "frozen free function"),
        ],
        dependents=["T-62", "T-31", "T-48"],
        obligations=["R-CANON-02", "R-CANON-05", "R-CANON-07", "R-CANON-08"],
        sections=["S-17"],
        collisions=["X-50", "X-51", "X-54", "X-55", "X-56", "X-72"],
        note=(
            "spec/05 §4 lists the traits as `CanonicalPayload / CanonicalEncode / "
            "CanonicalDecode` and omits `CanonicalSerialize`, which is the name the "
            "source's persistence-era trait actually bears. X-51."
        ),
    ),

    # ------------------------------------------------------------- K. claims
    Term(
        tid="T-64",
        canonical="Specification",
        domain="CLAIM",
        type="CONCEPT",
        definition=(
            "The frozen statement of REQUIRED behavior: what the machine must do. A "
            "specification is evidence of nothing but itself. `SPECIFICATION: FROZEN` "
            "means the requirement text is stable; it never means the behavior has been "
            "implemented, tested, verified, or proven."
        ),
        owner="MOD-17",
        owner_crate="spec/ + req/ (documents)",
        first_definition=A(38936, 54, "SPECIFICATION: FROZEN"),
        frozen_at=None,
        forbidden=[
            "design",
            "contract (unqualified — 'reference contract' and 'verification contract' "
            "are distinct frozen items)",
            "proof",
            "guarantee",
            "implementation plan",
        ],
        protected=[
            ("SPECIFICATION: FROZEN", "frozen status line"),
            ("ARCHITECTURE: FROZEN", "frozen status line"),
            ("REFERENCE CONTRACT: FROZEN", "frozen status line"),
            ("VERIFICATION CONTRACT: FROZEN", "frozen status line"),
            ("S-NN", "frozen section identifier scheme"),
            ("R-AREA-NN", "frozen obligation identifier scheme"),
        ],
        dependents=["T-65", "T-66", "T-67", "T-69"],
        obligations=["R-SCOPE-01", "R-SCOPE-02", "R-CLAIM-01"],
        sections=["S-01", "S-24"],
        collisions=["X-52", "X-53", "X-60", "X-63"],
        note="N-06 (`Specification ≠ Implementation`) is enforced by the evidence ladder: text never confers `IMPLEMENTED`.",
    ),
    Term(
        tid="T-65",
        canonical="Implementation",
        domain="CLAIM",
        type="CONCEPT",
        definition=(
            "Repository code that realizes a requirement. `IMPLEMENTED` requires source "
            "files in this repository mapped in spec/07 — a Rust code block inside "
            "`Red-on-Rust.md` is SPECIFICATION TEXT, not repository code, and never "
            "raises evidence status."
        ),
        owner="MOD-17",
        owner_crate="crates/ (absent at this commit)",
        first_definition=A(38939, 54, "IMPLEMENTATION: READY"),
        frozen_at=None,
        forbidden=[
            "verification",
            "proof",
            "conformance",
            "the reference model (that is one implementation among two)",
        ],
        protected=[
            ("IMPLEMENTATION: READY", "frozen status line (turn [54]/[58])"),
            ("IMPLEMENTATION: IN PROGRESS", "the README's other status line — the two "
                                            "disagree (C-09); both retained"),
            ("ror-core…ror-testkit", "frozen crate names"),
            ("ROR-NNN", "frozen first-sprint task identifier scheme"),
        ],
        dependents=["T-64", "T-66", "T-68"],
        obligations=["R-SCOPE-02", "R-REPO-01", "R-REPO-02", "R-CLAIM-01"],
        sections=["S-01", "S-22", "S-24"],
        collisions=["X-48", "X-52", "X-53", "X-63"],
        note=(
            "This repository contains no implementation at this commit, so every "
            "obligation is `SPECIFIED` and no higher (spec/00 §2). The README's "
            "'IN PROGRESS'/'READY' wording is orientation, not evidence (C-09)."
        ),
    ),
    Term(
        tid="T-66",
        canonical="Verification",
        domain="CLAIM",
        type="CONCEPT",
        definition=(
            "Independent evidence that an implementation conforms: differential "
            "agreement against the reference model, exhaustive/property coverage, "
            "mutation kills, crash-matrix classification. `VERIFICATION CONTRACT: "
            "FROZEN` means the CONTRACT is frozen, not that verification has been "
            "performed. Verification is evidence over a tested state space."
        ),
        owner="MOD-17",
        owner_crate="tests/ + scripts/",
        first_definition=A(38938, 54, "VERIFICATION CONTRACT: FROZEN"),
        frozen_at=None,
        forbidden=[
            "proof",
            "testing (unqualified — testing is a means; verification is the evidence claim)",
            "validation (unqualified)",
            "certification",
        ],
        protected=[
            ("VERIFICATION: FROZEN", "the README's status line — means the contract is "
                                     "frozen (spec/05 §6.10)"),
            ("VERIFICATION CONTRACT: FROZEN", "frozen status line (turn [54])"),
            ("VERIFIED", "frozen ladder rung"),
            ("machine-checked evidence", "frozen claim wording (R-CLAIM-01)"),
            ("TAG-NAME", "frozen verification-obligation tag scheme"),
        ],
        dependents=["T-58", "T-57", "T-60", "T-61", "T-67"],
        obligations=["R-CLAIM-01", "R-TEST-07", "R-TEST-11", "R-SCOPE-02"],
        sections=["S-20", "S-21", "S-24"],
        collisions=["X-52"],
        note=(
            "'The property tests prove the code obeys the calculus' violates R-CLAIM-01 "
            "(C-34); the frozen wording is machine-checked evidence of refinement over "
            "the tested state space."
        ),
    ),
    Term(
        tid="T-67",
        canonical="Proof",
        domain="CLAIM",
        type="CONCEPT",
        definition=(
            "A formal, mechanized artifact establishing a statement. `PROVEN` requires a "
            "proof artifact in the repository. NO theorem in the frozen source has a "
            "mechanized proof: Theorems 1-6 carry proof SKETCHES only, so all remain "
            "`SPECIFIED`. The project deliberately does not claim test execution "
            "constitutes a mathematical proof of the calculus."
        ),
        owner="MOD-17",
        owner_crate="(none; no proof artifact exists)",
        first_definition=A(28263, 35, "formal proof obligations remain separately identified"),
        frozen_at=None,
        forbidden=[
            "verification (as a synonym for proof)",
            "guarantee",
            "established fact",
            "proven (as a status for any current obligation)",
        ],
        protected=[
            ("PROVEN", "frozen ladder rung"),
            ("proof sketch", "frozen description of Theorems 1-6"),
            ("formal mechanization", "frozen future-work wording"),
            ("Theorem 1…Theorem 6", "frozen theorem numbering"),
        ],
        dependents=["T-66", "T-68"],
        obligations=["R-CLAIM-01", "R-CLAIM-03", "R-SCOPE-02"],
        sections=["S-24", "S-01"],
        collisions=["X-52"],
        note="C-43 records that all six theorems have proof sketches only; N-08 (`Verification ≠ Proof`) is the law.",
    ),
    Term(
        tid="T-68",
        canonical="EvidenceStatus",
        domain="CLAIM",
        type="CLAIM-STATUS",
        definition=(
            "The strictly evidence-gated ladder `SPECIFIED → IMPLEMENTED → TESTED → "
            "VERIFIED → PROVEN`. Promotion requires a repository artifact; a "
            "specification requirement never confers `IMPLEMENTED` or higher. At this "
            "commit every obligation is `SPECIFIED`."
        ),
        owner="MOD-17",
        owner_crate="spec/00 §2 (vocabulary); artifacts in crates/, tests/, vectors/",
        first_definition=A(25, None, "| `SPECIFIED` | Normative requirement exists in the frozen source.", file="spec/00-overview.md"),
        frozen_at=None,
        forbidden=[
            "maturity level",
            "completion percentage",
            "confidence",
            "DONE",
        ],
        protected=[
            ("SPECIFIED", "frozen rung"),
            ("IMPLEMENTED", "frozen rung"),
            ("TESTED", "frozen rung"),
            ("VERIFIED", "frozen rung"),
            ("PROVEN", "frozen rung"),
            ("UNKNOWN", "frozen extra state in req/ — reserved for statements whose "
                        "normative status cannot be determined; NOT a weaker SPECIFIED"),
            ("EVIDENCE-STATUS", "frozen req/ record field name"),
        ],
        dependents=["T-64", "T-65", "T-66", "T-67"],
        obligations=["R-SCOPE-02", "R-CLAIM-01"],
        sections=["S-01"],
        collisions=["X-52", "X-53", "X-63"],
        note=(
            "The ladder VOCABULARY is a canonicalization-layer construct (spec/00 §2); "
            "the underlying discipline is source text ('machine-checked evidence', "
            "L28263; 'frozen means frozen', L38929-38942). FIRST_DEFINITION therefore "
            "cites `spec/00-overview.md`, not the source — recorded explicitly rather "
            "than back-dated into the frozen transcript."
        ),
    ),
    Term(
        tid="T-69",
        canonical="Frozen",
        domain="CLAIM",
        type="CONCEPT",
        definition=(
            "'Requirements are stable and may not be changed by implementation "
            "convenience.' Frozen NEVER means verified, correct, complete, or "
            "unambiguous: a frozen specification can still contain open contradictions "
            "(spec/06) and undecided items (spec/09). Where implementation difficulty "
            "exposes an ambiguity, STOP and report it; do not resolve semantic ambiguity "
            "by inventing behavior."
        ),
        owner="MOD-17",
        owner_crate="spec/ (documents)",
        first_definition=A(38935, 54, "ARCHITECTURE: FROZEN"),
        frozen_at=None,
        forbidden=["verified", "final", "complete", "correct", "closed"],
        protected=[
            ("FROZEN", "frozen status word"),
            ("STOP and report", "frozen rule wording (R-SCOPE-03, L37690)"),
            ("frozen addendum", "the only legal mechanism for changing frozen text"),
            ("superseded", "frozen marker for obsolete text retained for traceability"),
        ],
        dependents=["T-64", "T-66", "T-68"],
        obligations=["R-SCOPE-02", "R-SCOPE-03", "R-TEST-09"],
        sections=["S-01"],
        collisions=["X-52", "X-63"],
        note="spec/05 §6.9-6.10 states the same rule; this entry is the dictionary's term of record for it.",
    ),
    # ------------------------------------------------------- G. fault taxonomy
    Term(
        tid="T-70",
        canonical="Fault",
        domain="MACHINE",
        type="RUST-ENUM",
        definition=(
            "The machine-visible fault taxonomy: the payload of `StepResult::Fault(Fault)`, "
            "`ActorStatus::Fault(Fault)` and `MachineEvent::Fault(Fault)`, and the value the "
            "differential observer compares (R-REF-05). `pub enum Fault` is declared seven "
            "times across the 60 turns with differing variant sets; the frozen turn-[30] "
            "form names eight variants behind an explicit `// ... (previous faults)` elision, "
            "so the source never closes the set. Distinct from `GlobalFault` (the parallel "
            "global-machine taxonomy), `RecoveryFault`, `HostFault`, `MarshalFault` and "
            "`ObservedFault` (the 15C.46 differential record)."
        ),
        owner="MOD-01",
        owner_crate="ror-core",
        first_definition=A(1009, 3, "Fault(Fault),         // Unhandled Fault (Rule 15)"),
        frozen_at=A(23806, 30, "pub enum Fault {"),
        forbidden=[
            "fault (lowercase — the `fault(…)` form C-08 cites occurs nowhere)",
            "Faulted (that is the `RunState` variant, X-23)",
            "error / failure (unqualified — four distinct `*Error`/`*Fault` types exist)",
            "GlobalFault (parallel taxonomy for the global machine, T-71)",
        ],
        protected=[
            ("Fault", "frozen Rust enum name — SEVEN declarations (L10882, L17788, L18125, L22415, L23319, L23806, L26865)"),
            ("// ... (previous faults)", "verbatim elision marker at L23807 — the frozen block does not restate earlier variants"),
            ("Capability", "frozen variant L23808 (turn [30]); also L22430 (turn [29])"),
            ("CapabilityError", "variant NAME at L20389/L20790/L20538 (turn [28]) — renamed to `Capability` by turn [29] without retraction"),
            ("CapabilityDenied", "variant name at L26870 (turn [33]) actor-local `Fault`"),
            ("CapabilityViolation", "denial name L94/L133/L267/L463/L1042/L10456 and v0.3 L8758"),
            ("CapabilityRevoked", "denial name L937 (with a `CapRef` payload), L3667 (no payload), v0.3 L8721"),
            ("CapViolation", "v1 fault-grammar name L1949 — distinct from `CapabilityViolation`"),
            ("Revoked", "v1 fault-grammar name L1949 — distinct from `CapabilityError::Revoked`"),
            ("AuthorizationFailed", "v0.3 denial name L7374"),
            ("ScopeViolation", "v1 denial name L944/L1949 — no later counterpart"),
            ("BudgetExhausted", "frozen variant L23809; also in the v1 grammar L1949"),
            ("DeadlineExceeded", "frozen variant L23810"),
            ("HostPolicyDenied", "frozen variant L23811 — payload type split (X-58)"),
            ("HostPolicyViolation", "variant name L10885 (turn [18]) and v0.3 L8758"),
            ("EffectCanonicalization", "frozen variant L23812"),
            ("Host", "frozen variant L23813, carrying `HostFault` (T-74)"),
            ("ReplayCorruption", "frozen variant L23814 — also a `HostFault` path (X-67)"),
            ("InvalidReceipt", "frozen variant L23815"),
            ("IsolationBreach", "v1 grammar L1949 and receipt-mismatch conclusion L2024/L7223/L8766"),
            ("StalePlan", "source-used fault name: `Fault::StalePlan` at L28373 (turn [36]) and a bare token at L27236 (turn [33]) — declared by none of the seven `Fault` enums (X-64, X-69)"),
            ("AuthoritySuspended", "source-used `Fault::` path L941 (turn [3]) — in no declaration (X-69)"),
            ("FuelExhausted", "source-used `Fault::` path L1018 (turn [3]) — the declared name is `BudgetExhausted` (X-69)"),
            ("AncestorRevoked", "source-used `Fault::` path L6705 (turn [11]) — near-synonym of `Revoked` in the same list (X-69)"),
            ("Unauthorized", "source-used `Fault::` path L6706 (turn [11]) — a third name for the same denial (X-69)"),
            ("ReservedCapacityExceeded", "source-used `Fault::` path L10466-10467 (turn [18]) — in no declaration (X-69)"),
            ("NoSuchActor", "source-used `Fault::` path L25714 (turn [32]) — in no declaration (X-69)"),
            ("UnknownActor", "source-used `Fault::` path L26017 (turn [32]) — a second name for `NoSuchActor`, 303 lines later (X-69)"),
        ],
        dependents=["T-35", "T-36", "T-71", "T-72", "T-73", "T-74"],
        obligations=["R-CALC-06", "R-ACTOR-02", "R-ACTOR-04"],
        sections=["S-07", "S-15"],
        collisions=["X-23", "X-38", "X-58", "X-59", "X-64", "X-65", "X-66", "X-67", "X-68", "X-69", "X-71", "X-73", "X-81"],
        shape=(
            "pub enum Fault {\n"
            "    // ... (previous faults)\n"
            "    Capability(CapabilityError),\n"
            "    BudgetExhausted,\n"
            "    DeadlineExceeded,\n"
            "    HostPolicyDenied(HostPolicyError),\n"
            "    EffectCanonicalization(EffectError),\n"
            "    Host(HostFault),\n"
            "    ReplayCorruption, // ID or Digest mismatch\n"
            "    InvalidReceipt,\n"
            "}"
        ),
        supersedes=[
            "pub enum Fault { …, HostPolicyViolation, … }   // L10882 (turn [18]) — `HostPolicyViolation`, no payload",
            "let fault = Fault::CapabilityError(error);   // L20389/L20790 (turn [28]) — variant named `CapabilityError`",
            "pub enum Fault { …, CapabilityDenied, MarshalFault(...), HostFault(...), … }   // L26865 (turn [33]) — actor-local set",
        ],
        note=(
            "Nine distinct names are used for capability denial across eras "
            "(`CapViolation`, `CapabilityViolation`, `Revoked`, `CapabilityRevoked`, "
            "`ScopeViolation`, `AuthorizationFailed`, `Fault::CapabilityError`, "
            "`Fault::Capability(CapabilityError)`, `CapabilityDenied`) — X-38. "
            "The set is never closed by the source; U-08/U-14 remain open on their merits."
        ),
    ),
    Term(
        tid="T-71",
        canonical="GlobalFault",
        domain="MACHINE",
        type="RUST-ENUM",
        definition=(
            "The fault taxonomy of the GLOBAL machine step, parallel to `Fault`: "
            "`global_step(…) -> Result<GlobalStep, GlobalFault>`. Its eight variants cover "
            "durable state (`SnapshotCorruption`, `EventLogCorruption`, `EventSequenceGap`, "
            "`InvalidRecoveredState`, `EffectReconciliationFailure`, `PersistenceFailure`) and "
            "the actor table and scheduler (`ActorTableCorruption`, `SchedulerInvariantViolation`). None "
            "of the eight appears in any `Fault` declaration. It is named by no obligation, "
            "module or requirement record: R-CALC-06 describes \u201cthe frozen `Fault` "
            "taxonomy\u201d without it (spec/01 L138, spec/03 L52, mod/01 L155, mod/18 L68), "
            "and the only canonicalization-layer mention it has is the one this pass added "
            "when it linked the term from `req/03` AMB-08."
        ),
        owner="MOD-05",
        owner_crate="ror-runtime",
        first_definition=A(25576, 32, ") -> Result<GlobalStep, GlobalFault> {"),
        frozen_at=A(26885, 33, "pub enum GlobalFault {"),
        forbidden=["Fault (as a synonym — disjoint variant sets)", "global error"],
        protected=[
            ("GlobalFault", "frozen Rust enum name"),
            ("SnapshotCorruption", "frozen variant L26886"),
            ("EventLogCorruption", "frozen variant L26887"),
            ("EventSequenceGap", "frozen variant L26888"),
            ("InvalidRecoveredState", "frozen variant L26889"),
            ("EffectReconciliationFailure", "frozen variant L26890"),
            ("PersistenceFailure", "frozen variant L26891"),
            ("ActorTableCorruption", "frozen variant L26892"),
            ("SchedulerInvariantViolation", "frozen variant L26893"),
        ],
        dependents=["T-38", "T-48", "T-45", "T-52"],
        obligations=["R-CALC-06"],
        sections=["S-07"],
        collisions=["X-58"],
        shape=("pub enum GlobalFault { SnapshotCorruption, EventLogCorruption, EventSequenceGap, "
              "InvalidRecoveredState, EffectReconciliationFailure, PersistenceFailure, "
              "ActorTableCorruption, SchedulerInvariantViolation }   // L26885-26894, all eight"),
        note=("R-CALC-06 (spec/01 L138, spec/03 L52, mod/01 L155, mod/18 L68) describes "
              "\u201cthe frozen `Fault` taxonomy\u201d without mentioning that a second, disjoint "
              "eight-variant taxonomy governs the global machine step."),
    ),
    Term(
        tid="T-72",
        canonical="CapabilityError",
        domain="AUTHORITY",
        type="RUST-ENUM",
        definition=(
            "The structured reason carried by the frozen `Fault::Capability(CapabilityError)` "
            "variant and returned by the `CapabilityKernelView` API "
            "(`derive`/`revoke`/`…  -> Result<…, CapabilityError>`). Declared once, with an "
            "explicit elision; one variant used in the source is never declared."
        ),
        owner="MOD-03",
        owner_crate="ror-kernel",
        first_definition=A(9736, 17, ") -> Result<&Authority, CapabilityError>;"),
        frozen_at=A(20408, 28, "pub enum CapabilityError {"),
        forbidden=["CapabilityFault", "capability error (unqualified)"],
        protected=[
            ("CapabilityError", "frozen Rust enum name — the ONLY declaration (L20408)"),
            ("Revoked", "declared L20409; used 3× as `CapabilityError::Revoked` (L20527, L20538, L20941) — a fourth apparent hit at L21022 is `RefCapabilityError::Revoked`, the reference model's separate type, and is commented out"),
            ("Expired", "declared L20410 — never used; the used form `ExpiredOrRevoked` belongs to `RefCapabilityError` (L20619)"),
            ("InvalidConstraint", "declared L20411; used L20451 as the `derive` fallback"),
            ("Invalid", "USED at L20835 as the `derive` fallback — NEVER declared (X-66)"),
            ("// ...", "verbatim elision marker at L20412"),
            ("RefCapabilityError", "the reference model's separate error type (L19628, L20617) — not this enum"),
        ],
        dependents=["T-13", "T-09", "T-10", "T-70"],
        obligations=["R-CAP-01", "R-CAP-02"],
        sections=["S-07", "S-09"],
        collisions=['X-38', 'X-59', 'X-66', 'X-68'],
        shape="pub enum CapabilityError { Revoked, Expired, InvalidConstraint, /* … */ }",
        note=("spec/05 L112 and U-08 both claim these variants are \u201cnot enumerated\u201d; "
              "they are, at L20408\u201320413, behind an elision (X-59)."),
    ),
    Term(
        tid="T-73",
        canonical="MarshalFault",
        domain="CONCURRENCY",
        type="RUST-ENUM",
        definition=(
            "The fault produced when marshalling a value across an actor boundary fails. "
            "Declared twice with COMPLETELY DISJOINT variant sets, and used as an elided "
            "`Fault` payload (`MarshalFault(...)`) in the turn-[33] actor-local taxonomy."
        ),
        owner="MOD-06",
        owner_crate="ror-runtime",
        first_definition=A(10846, 18, "pub enum MarshalFault {"),
        frozen_at=A(25983, 32, "pub enum MarshalFault {"),
        forbidden=["marshalling error", "MarshalError"],
        protected=[
            ("MarshalFault", "frozen Rust enum name — TWO declarations"),
            ("CapabilityNotTransferable", "variant of the turn-[18] declaration (L10847)"),
            ("InvalidFormat", "variant of the turn-[18] declaration (L10848)"),
            ("CapabilityRequiresDelegation", "variant of the turn-[32] declaration (L25984) — the one mod/06 L62/L103 and REQ-MARSHAL cite"),
            ("SerializationError", "variant of the turn-[32] declaration (L25985)"),
            ("CorruptedPayload", "source-used `MarshalFault::` path L25694 (turn [32]) — in neither declaration (X-65, X-75)"),
        ],
        dependents=["T-35", "T-70"],
        obligations=["R-MARSHAL-01", "R-MARSHAL-02"],
        sections=["S-16"],
        collisions=["X-65", "X-75", "X-76"],
        shape="pub enum MarshalFault { CapabilityRequiresDelegation, SerializationError }   // L25983 (turn [32])",
        supersedes=["pub enum MarshalFault { CapabilityNotTransferable, InvalidFormat }   // L10846 (turn [18])"],
        note="Zero variants are shared between the two declarations (X-65).",
    ),
    Term(
        tid="T-74",
        canonical="HostFault",
        domain="HOST",
        type="RUST-ENUM",
        definition=(
            "The error type of the host boundary and of ordered replay: the payload of the "
            "frozen `Fault::Host(HostFault)` variant and the `Err` arm of "
            "`HostExecutor::execute`/`ReplayHost`. Declared ONCE, with two variants, while "
            "eight distinct variant paths are used in the source \u2014 six of them on the "
            "frozen replay path that R-HOST-03/04/05 and REQ-HOST-008 depend on."
        ),
        owner="MOD-09",
        owner_crate="ror-host",
        first_definition=A(10820, 18, "pub enum HostFault {"),
        frozen_at=None,
        forbidden=[
            "HostError",
            "host fault (unqualified)",
            "HostFault as a fault NAME (the v1 grammar L1949 uses `HostFault` as a member of "
            "`F`, i.e. as a fault, not as a type — X-68)",
        ],
        protected=[
            ("HostFault", "frozen Rust enum name — the ONLY declaration (L10820, turn [18])"),
            ("IoError(String)", "declared variant L10821"),
            ("PolicyViolation(String)", "declared variant L10822"),
            ("Io", "USED L1210/L1216 — never declared; near-miss of `IoError` (X-67)"),
            ("ConcreteScopeViolation", "USED L1208/L1214 — never declared (X-67)"),
            ("UnboundCapability", "USED L1203 — never declared (X-67)"),
            ("ReplayTraceExhausted", "USED 6× (L1245, L24020, L25496, L25838, L34519, L35225) — never declared (X-67)"),
            ("ReplayCorruption", "USED 6× (L25500, L25841, L34522, L34528, L35226, L35227) — never declared; ALSO a `Fault` variant (L23814) (X-67)"),
            ("TraceExhausted", "USED L10546 — never declared; a third name for the same condition (X-67)"),
            ("ReplayIdMismatch", "USED L10550 — never declared (X-67)"),
            ("ReplayDigestMismatch", "USED L10553 — never declared (X-67)"),
        ],
        dependents=["T-42", "T-44", "T-41", "T-70"],
        obligations=["R-HOST-03", "R-HOST-04", "R-HOST-05"],
        sections=["S-14"],
        collisions=['X-58', 'X-59', 'X-67', 'X-68'],
        shape="pub enum HostFault { IoError(String), PolicyViolation(String) }   // L10820 — the only declaration",
        note=(
            "Not one of the eight used variant paths is declared. `ReplayCorruption` is "
            "simultaneously a `HostFault` path and a `Fault` variant (L23814), so the same "
            "name denotes faults at two different levels of the taxonomy."
        ),
    ),
    # ------------------------------------------- H. sweep-found type families
    Term(
        tid="T-75",
        canonical="MachineEvent",
        domain="MACHINE",
        type="RUST-ENUM",
        definition=(
            "The machine's transition-event stream: what a step emits for the trace, and the "
            "vocabulary the differential observer and the WAL are built on. Declared eight "
            "times with materially different variant sets, three of them behind a `// ...` "
            "elision, and used with eight further variant paths that appear in no declaration."
        ),
        owner="MOD-05",
        owner_crate="ror-runtime",
        first_definition=A(14697, 23, "pub enum MachineEvent {"),
        frozen_at=A(22002, 29, "pub enum MachineEvent {"),
        forbidden=["event (unqualified)", "GlobalEvent (a different, also undeclared name)", "MachineEvents"],
        protected=[
            ("MachineEvent", "frozen Rust enum name — EIGHT declarations (L14697, L15958, L17588, L18104, L18631, L20318, L20724, L22002)"),
            ("EnterSeq", "declared variant (L14697 onward)"),
            ("EnterIf", "declared variant"),
            ("EnterCall", "declared variant (from L15958)"),
            ("EnterLambda", "declared variant from L15963 (turn [24]) onward"),
            ("ApplyFunction", "declared variant (from L17588)"),
            ("PushFrame", "declared variant"),
            ("PopFrame", "declared variant"),
            ("Block", "declared variant (L14697) — a `MachineEvent`, not the untrusted `Block` of T-01"),
            ("EnterAttenuate", "declared variant (L20318, L20724)"),
            ("DeriveCapability", "declared variant (L20318, L20724); constructed at L20386"),
            ("Fault", "declared variant; constructed at L20391/L20792 carrying a `Fault`"),
            ("EffectIssued", "declared variant (L22005) with `{ id, digest }`"),
            ("EffectCompleted", "declared variant (L22010) with `{ id, digest }`"),
            ("// ...", "verbatim elision marker at L22003 — the frozen block does not restate earlier variants"),
            ("EnterRequest", "USED L21483, L23380 — never declared (X-71)"),
            ("BeginRequestTarget", "USED L21536, L23398 — never declared (X-71)"),
            ("BeginRequestArgument", "USED L21645, L23426 — never declared (X-71)"),
            ("Blocked", "USED L25740, L26038 — never declared; the declared name is `Block` (X-71)"),
            ("Spawned", "USED L25668 — never declared (X-71)"),
            ("ActorSpawned", "USED L25966 with `{ parent, child }` — never declared; a SECOND name for `Spawned` (X-71)"),
            ("Sent", "USED L25728 — never declared (X-71)"),
            ("MessageSent", "USED L26027 with `{ from, to }` — never declared; a SECOND name for `Sent` (X-71)"),
            ("EnterLet", "declared variant L14698 (turn [23]) and in every later declaration, carrying a `Symbol`"),
            ("EvaluateValue", "declared variant L14701, carrying a `Value` — ALSO constructed in prose at L17575"),
            ("Lookup", "declared variant L14702, carrying a `Symbol`"),
            ("Halt", "declared variant L14705, carrying a `Value` — the same name as `StepResult::Halt` in a different enum (X-73)"),
            ("BeginArgument", "declared variant from L17596 (turn [25]), carrying a `usize`"),
            ("EndArgument", "declared variant from L17597 (turn [25]), carrying a `usize`"),
            ("// ... (Previous events)", "verbatim elision marker at L20319 (turn [28]) — one of three elided declarations"),
            ("// ... (previous variants)", "verbatim elision marker at L20725 (turn [28]) — note the different capitalisation and noun"),
        ],
        dependents=["T-47", "T-45", "T-70", "T-35", "T-38"],
        obligations=["R-CORE-08", "R-ACTOR-07"],
        sections=["S-07", "S-15"],
        collisions=["X-71"],
        shape=("pub enum MachineEvent { /* ... */ EffectIssued { id: EffectId, digest: EffectDigest }, "
               "EffectCompleted { id: EffectId, digest: EffectDigest } }   // L22002-22014, elided head"),
        note=(
            "Absent from the dictionary until the declaration sweep: the event vocabulary that "
            "the trace, the WAL and the differential comparison are all built on had no term of "
            "record, and no register entry counted its declarations."
        ),
    ),
    Term(
        tid="T-76",
        canonical="CanonicalError",
        domain="PERSISTENCE",
        type="RUST-ENUM",
        definition=(
            "The error type of canonical encoding and decoding — the `Err` arm of every "
            "`canonical_serialize` / `canonical_deserialize`, and therefore the type that "
            "reports every violation of the frozen envelope and payload rules. Declared seven "
            "times in four materially different shapes: unit variants, a differently-spelled "
            "set, payload-bearing struct variants for the same names, and an elided block "
            "adding one new variant."
        ),
        owner="MOD-10",
        owner_crate="ror-core (+ vectors/canonical)",
        first_definition=A(29188, 38, "pub enum CanonicalError {"),
        frozen_at=A(30661, 41, "pub enum CanonicalError {"),
        forbidden=["CanonicalizationError", "EncodeError", "DecodeError", "canonical error (unqualified)"],
        protected=[
            ("CanonicalError", "frozen Rust enum name — SEVEN declarations (L29188, L29968, L30661, L32083, L32959, L33299, L34994)"),
            ("InvalidVersion", "declared as a UNIT variant (L29189, L29970) and as a STRUCT variant `{ expected: u8, found: u8 }` (L30662) — same name, two arities (X-72)"),
            ("InvalidTypeTag", "unit (L29190, L29971) and struct `{ expected: u8, found: u8 }` (L30663) (X-72)"),
            ("LengthMismatch", "unit (L29191) and struct `{ expected: u32, found: usize }` (L30664); ABSENT from the L29968 set (X-72)"),
            ("LengthOverflow", "declared from L29968 onward; ABSENT from the first declaration L29188 (X-72)"),
            ("InvalidUtf8", "unit (L29192, L30666)"),
            ("Utf8Error", "a SECOND name for the same condition, only in the L29968 set (X-72)"),
            ("UnexpectedEof", "unit (L29193, L30667); ABSENT from the L29968 set, which has `PayloadTooShort` instead (X-72)"),
            ("PayloadTooShort", "only in the L29968 set (X-72)"),
            ("InvalidDiscriminant", "unit (L29972) and struct `{ found: u8 }` (L30669) (X-72)"),
            ("TrailingBytes", "unit (L29975) and struct `{ count: usize }` (L30668) (X-72)"),
            ("InvalidBoolValue", "struct `{ found: u8 }` (L30670), only in the L30661 set"),
            ("DuplicateMapKey", "added at L34996 behind a `// ... previous variants` elision — 'NEW: Enforces strict injectivity'"),
            ("// ... previous variants", "verbatim elision marker at L34995"),
        ],
        dependents=["T-62", "T-63", "T-47", "T-45", "T-31"],
        obligations=["R-CANON-01", "R-CANON-02"],
        sections=["S-17"],
        collisions=["X-72", "X-75"],
        shape=("pub enum CanonicalError { InvalidVersion { expected: u8, found: u8 }, "
               "InvalidTypeTag { expected: u8, found: u8 }, LengthMismatch { expected: u32, found: usize }, "
               "LengthOverflow, InvalidUtf8, UnexpectedEof, TrailingBytes { count: usize }, "
               "InvalidDiscriminant { found: u8 }, InvalidBoolValue { found: u8 } }   // L30661-30671"),
        supersedes=[
            "pub enum CanonicalError { InvalidVersion, InvalidTypeTag, LengthMismatch, InvalidUtf8, UnexpectedEof }   // L29188 (turn [38])",
            "pub enum CanonicalError { LengthOverflow, InvalidVersion, InvalidTypeTag, InvalidDiscriminant, PayloadTooShort, TrailingBytes, Utf8Error }   // L29968",
        ],
        note=(
            "Sits directly on the canonical-encoding path where X-50 (the envelope wire format) "
            "is already BLOCKING: which `CanonicalError` governs determines what a decoder may "
            "report, and the four shapes do not agree on names, spellings or arities."
        ),
    ),
    Term(
        tid="T-77",
        canonical="StepResult",
        domain="MACHINE",
        type="RUST-ENUM",
        definition=(
            "TWO DISJOINT ENUMS SHARE THIS NAME. (1) The CEK machine's single-step outcome "
            "(L1006, turn [3]): `Continue | Halt(Value) | Fault(Fault) | YieldToHost(Effect)` "
            "— one actor, one reduction, no identity carried. (2) The actor scheduler's step "
            "outcome (L9586, turn [17], restated L10397 and L10947): "
            "`Progressed | Blocked(ActorId) | Pending(ActorId, EffectRequest) | Halted(ActorId, Value) "
            "| Faulted(ActorId, Fault) | NoRunnableActors` — every variant carries an `ActorId`. "
            "They are not two versions of one type: they belong to different layers and have no "
            "variant in common."
        ),
        owner="MOD-05",
        owner_crate="ror-runtime",
        first_definition=A(1006, 3, "pub enum StepResult {"),
        frozen_at=A(9586, 17, "pub enum StepResult {"),
        forbidden=[
            "step result (unqualified — two disjoint enums exist)",
            "StepOutcome",
            "using the scheduler's `Faulted(ActorId, Fault)` where the machine's `Fault(Fault)` is meant (X-23, X-73)",
        ],
        protected=[
            ("StepResult", "frozen Rust enum name — FOUR declarations (L1006, L9586, L10397, L10947) in two disjoint families"),
            ("Continue", "machine variant L1007"),
            ("Halt", "machine variant L1008, carrying a `Value`"),
            ("Fault", "machine variant L1009, carrying a `Fault`"),
            ("YieldToHost", "machine variant L1010, carrying an `Effect`"),
            ("Progressed", "scheduler variant L9587"),
            ("Blocked", "scheduler variant L9588, carrying an `ActorId` — ALSO an `ActorStatus` and a `RunState` variant (X-21)"),
            ("Pending", "scheduler variant L9589, carrying `(ActorId, EffectRequest)`"),
            ("Halted", "scheduler variant L9590, carrying `(ActorId, Value)`"),
            ("Faulted", "scheduler variant L9591, carrying `(ActorId, Fault)` — ALSO a `RunState` variant (X-23)"),
            ("NoRunnableActors", "scheduler variant L9592"),
        ],
        dependents=["T-70", "T-35", "T-36", "T-34", "T-32"],
        obligations=["R-CEK-01", "R-ACTOR-04"],
        sections=["S-07", "S-15"],
        collisions=["X-73", "X-74"],
        shape=("pub enum StepResult { Continue, Halt(Value), Fault(Fault), YieldToHost(Effect) }   // L1006, machine\n"
               "pub enum StepResult { Progressed, Blocked(ActorId), Pending(ActorId, EffectRequest), "
               "Halted(ActorId, Value), Faulted(ActorId, Fault), NoRunnableActors }   // L9586, scheduler"),
        note=(
            "The machine/scheduler split is the same shape as the `Observation` split (X-06), "
            "which the request's own term list forced into two canonical terms; here the source "
            "gives no second name, so both are recorded under one entry with the homonymy "
            "filed as X-73 rather than resolved by renaming."
        ),
    ),
    Term(
        tid="T-78",
        canonical="ControlFrame",
        domain="MACHINE",
        type="RUST-ENUM",
        definition=(
            "The CEK machine's control stack frame: what `self.control` holds between "
            "reductions. Declared once, behind an elision, with three visible variants — and "
            "used with two variant paths that appear in no declaration. Its declared variants "
            "reference `PlanIR`, `FuncRef` and `EffectSignature`, none of which is declared "
            "anywhere either."
        ),
        owner="MOD-05",
        owner_crate="ror-runtime",
        first_definition=A(985, 3, "pub enum ControlFrame {"),
        frozen_at=None,
        forbidden=["control frame (unqualified)", "ControlStack", "Frame (that is T-33, a distinct declared enum)"],
        protected=[
            ("ControlFrame", "frozen Rust enum name — the ONLY declaration (L985, turn [3])"),
            ("EvaluateSequence", "declared variant L986, carrying `{ remaining: Vec<PlanIR> }`"),
            ("AwaitInvoke", "declared variant L987, carrying `{ func: FuncRef, args: Vec<Value> }`"),
            ("AwaitHostFFI", "declared variant L988, carrying `{ effect: EffectSignature }`"),
            ("// ...", "verbatim elision marker at L989"),
            ("ReduceIR", "USED L1031 and matched at L1035 — never declared (X-75)"),
            ("ResumeWithResult", "USED L1282 — never declared (X-75)"),
        ],
        dependents=["T-32", "T-30", "T-31", "T-77"],
        obligations=["R-CEK-01"],
        sections=["S-07"],
        collisions=["X-75"],
        shape=("pub enum ControlFrame { EvaluateSequence { remaining: Vec<PlanIR> }, "
               "AwaitInvoke { func: FuncRef, args: Vec<Value> }, AwaitHostFFI { effect: EffectSignature }, "
               "/* ... */ }   // L985-990"),
        note=(
            "Distinct from `Frame` (T-33), which is declared eleven times and is the "
            "evaluation frame of the frozen turn-[30] machine; the two names are not "
            "interchangeable and the source uses both."
        ),
    ),

    Term(
        tid="T-79",
        canonical="MarshalledValue",
        domain="CONCURRENCY",
        type="RUST-NEWTYPE",
        definition=(
            "The newtype that crosses the actor-isolation boundary: what a `Mailbox` holds "
            "and what `marshal_value` produces. Declared five times with two incompatible "
            "payloads — `MarshalledValue(Value)`, an in-memory value, at L9925 (turn [17]), "
            "L10828 (turn [18]) and L24765 (turn [31]); and `MarshalledValue(Vec<u8>)`, "
            "commented 'Canonical serialized bytes' at L25683 and 'an opaque, canonical byte "
            "representation' at L25980 (both turn [32]). The two payloads answer different "
            "questions: one says the boundary transports values, the other says it transports "
            "bytes, and each has frozen API attached that the other cannot satisfy."
        ),
        owner="MOD-06",
        owner_crate="ror-runtime (transport); ror-core/15A (canonical bytes)",
        first_definition=A(9925, 17, "pub struct MarshalledValue(Value);"),
        frozen_at=A(25683, 32, "pub struct MarshalledValue(pub Vec<u8>); // Canonical serialized bytes"),
        forbidden=[
            "marshalled value (unqualified prose)",
            "SerializedValue",
            "CanonicalBytes (a description in the L25683 comment, not a declared name)",
            "MarshalResult (that is the separate enum at L10836, not this newtype)",
        ],
        protected=[
            ("MarshalledValue", "frozen Rust newtype name — five declarations (L9925, L10828, L24765, L25683, L25981)"),
            ("Value", "frozen payload of the turns-[17]/[18]/[31] declarations"),
            ("Vec<u8>", "frozen payload of the turn-[32] declarations"),
            ("pub Vec<u8>", "the turn-[32] payload is declared PUBLIC at L25683 while L25980 calls the type 'opaque'"),
            ("new", "`pub(crate) fn new(v: Value) -> Self` — frozen at L10831, takes a `Value`"),
            ("into_inner", "`pub fn into_inner(self) -> Value` — frozen at L10832, cannot exist over a `Vec<u8>` payload"),
            ("marshal_value", "`fn marshal_value(v: &Value) -> Result<MarshalledValue, MarshalFault>` — frozen at L25685"),
            ("canonical_serialize", "the constructor actually used at L25690: `MarshalledValue(canonical_serialize(v))`"),
            ("contains_capability", "the pre-marshal capability scan at L25687"),
        ],
        dependents=["T-39", "T-37", "T-31", "T-62", "T-73"],
        obligations=["R-MARSHAL-01", "R-MARSHAL-02", "R-MARSHAL-03", "R-ACTOR-03"],
        sections=["S-15", "S-16", "S-17"],
        collisions=["X-76", "X-83"],
        shape=(
            "pub struct MarshalledValue(Value);                 // L9925, L10828, L24765\n"
            "pub struct MarshalledValue(pub Vec<u8>);           // L25683, 'Canonical serialized bytes'\n"
            "pub struct MarshalledValue(Vec<u8>);               // L25981, 'opaque, canonical byte representation'"
        ),
        supersedes=[],
        note=(
            "T-39 (`Mailbox`) already glosses this name in its `protected` list as 'frozen "
            "element type (canonical bytes transport)' — i.e. the dictionary had silently "
            "adopted the turn-[32] bytes reading while three earlier declarations, and the "
            "frozen `into_inner() -> Value`, say otherwise. Filed rather than resolved: "
            "neither payload is renamed (X-76)."
        ),
    ),
    Term(
        tid="T-80",
        canonical="RefState",
        domain="VERIFICATION",
        type="RUST-STRUCT",
        definition=(
            "The reference machine's state — the left-hand side of the differential observer "
            "R-REF-05 and the object whose digest is compared against the production machine's. "
            "Declared four times in two shapes: `{ expr: Expr, env: Environment, kont: "
            "Vec<Frame>, outcome: RefOutcome }` at L14728 (turn [23]) and, identically, at "
            "L15985 and L16423 (turn [24]); and `{ expr: RefExpr, env: RefEnv, continuation: "
            "Vec<RefFrame> }` at L35522 (turn [48]). The turn-[48] form renames `kont` to "
            "`continuation`, drops `outcome` entirely, and replaces every production type with "
            "a `Ref*` type — the only one of the four that satisfies reference-model "
            "independence, and the one whose `RefExpr` is declared nowhere in the source."
        ),
        owner="MOD-14",
        owner_crate="ror-reference",
        first_definition=A(14728, 23, "pub struct RefState {"),
        frozen_at=A(35522, 48, "pub struct RefState {"),
        forbidden=[
            "reference state (unqualified prose)",
            "RefMachineState",
            "ActorState (that is T-37, the production per-actor state)",
            "EvalState (that is T-32, the production CEK state)",
        ],
        protected=[
            ("RefState", "frozen Rust struct name — four declarations (L14728, L15985, L16423, L35522)"),
            ("expr", "frozen field name in all four declarations"),
            ("Expr", "the field's type in the turns-[23]/[24] declarations — the PRODUCTION AST (T-30)"),
            ("RefExpr", "the field's type at L35523 — declared nowhere (X-84)"),
            ("env", "frozen field name in all four declarations"),
            ("Environment", "the env type in the turns-[23]/[24] declarations"),
            ("RefEnv", "the env type at L35524 — declared once"),
            ("kont", "frozen field name at L14731/L15988/L16426 — the CEK spelling"),
            ("continuation", "the same field's other frozen name, at L35525"),
            ("Vec<Frame>", "the continuation's type in turns [23]/[24] — the PRODUCTION frame (T-33)"),
            ("Vec<RefFrame>", "the continuation's type at L35525"),
            ("outcome", "frozen field at L14732, absent from the turn-[48] declaration"),
            ("RefOutcome", "the outcome's type — declared three times"),
        ],
        dependents=["T-58", "T-30", "T-32", "T-33", "T-81"],
        obligations=["R-REF-01", "R-REF-02", "R-REF-05"],
        sections=["S-20"],
        collisions=["X-78", "X-79", "X-84", "X-86"],
        shape=(
            "pub struct RefState { expr: Expr, env: Environment, kont: Vec<Frame>, "
            "outcome: RefOutcome }        // L14728, L15985, L16423\n"
            "pub struct RefState { expr: RefExpr, env: RefEnv, continuation: Vec<RefFrame> }"
            "        // L35522"
        ),
        supersedes=[],
        note=(
            "The `kont`/`continuation` rename is the same field-name split X-22 records for the "
            "production side; here it also carries a type change, because the turn-[48] form is "
            "the only one written in the reference model's own vocabulary. Which form the "
            "differential oracle compares is undecided (X-79)."
        ),
    ),
    Term(
        tid="T-81",
        canonical="RefAuthority",
        domain="AUTHORITY",
        type="RUST-STRUCT",
        definition=(
            "The reference model's authority — the object `reference_derive` narrows and the "
            "authority against which the reference machine checks a capability request. "
            "Declared four times in three non-elided shapes: `{ ops: HashSet<Op>, scope: "
            "HashSet<Target>, /* ... other fields */ }` at L11572 (turn [20], body elided); "
            "`{ operations: BTreeMap<Op, RefOperationAuthority> }` at L19603 (turn [27]); "
            "`{ operations: BTreeSet<Op>, scope: RefScope, params: RefConstraint, resources: "
            "RefResources, lifetime: RefLifetime }` at L20851 (turn [28]); and "
            "`{ operations: BTreeMap<RefOp, RefOperationAuthority> }` at L35699 (turn [48]). "
            "The field is `ops` once and `operations` three times, the container is a "
            "`HashSet`, a `BTreeMap`, a `BTreeSet` and a `BTreeMap` again, and the key type "
            "changes from `Op` to `RefOp` between turns [27] and [48]."
        ),
        owner="MOD-14",
        owner_crate="ror-reference",
        first_definition=A(11572, 20, "pub struct RefAuthority {"),
        frozen_at=A(35699, 48, "pub struct RefAuthority {"),
        forbidden=[
            "reference authority (unqualified prose)",
            "RefCap",
            "RefConstraint (that is the NARROWING REQUEST — the argument of `reference_derive`, a different type)",
            "Authority (that is T-10, the production authority)",
        ],
        protected=[
            ("RefAuthority", "frozen Rust struct name — four declarations (L11572, L19603, L20851, L35699)"),
            ("ops", "frozen field name at L11573, and the field the frozen `reference_derive` body reads at L11580"),
            ("operations", "the same field's other frozen name — L19604, L20852, L35700"),
            ("scope", "frozen field at L11574 and L20853"),
            ("params", "frozen field at L20854"),
            ("resources", "frozen field at L20855"),
            ("lifetime", "frozen field at L20856"),
            ("reference_derive", "`fn reference_derive(parent: &RefAuthority, constraint: &RefConstraint) -> RefAuthority` — frozen at L11578"),
            ("RefOperationAuthority", "the per-operation authority — declared twice (L19608, L35703), identically"),
            ("Op", "the map/set key type at L19604 and L20852 — the PRODUCTION operation type"),
            ("RefOp", "the key type at L35700 — declared nowhere (X-84)"),
            ("RefScope", "component type at L19609/L20853/L35704 — declared nowhere (X-84)"),
            ("RefConstraint", "component type at L19610/L20854/L35705 and `reference_derive`'s second argument — declared nowhere (X-84)"),
            ("RefResources", "component type at L19611/L20855/L35706 — declared nowhere (X-84)"),
            ("RefLifetime", "component type at L19612/L20856/L35707 — declared nowhere (X-84)"),
        ],
        dependents=["T-10", "T-12", "T-15", "T-58", "T-80"],
        obligations=["R-REF-03", "R-REF-05", "R-CAP-02", "R-CAP-04"],
        sections=["S-09", "S-20"],
        collisions=["X-77", "X-78", "X-79", "X-84"],
        shape=(
            "pub struct RefAuthority { ops: HashSet<Op>, scope: HashSet<Target>, /* ... */ }   // L11572\n"
            "pub struct RefAuthority { operations: BTreeMap<Op, RefOperationAuthority> }       // L19603\n"
            "pub struct RefAuthority { operations: BTreeSet<Op>, scope: RefScope, params: RefConstraint,\n"
            "                          resources: RefResources, lifetime: RefLifetime }        // L20851\n"
            "pub struct RefAuthority { operations: BTreeMap<RefOp, RefOperationAuthority> }     // L35699"
        ),
        supersedes=[],
        note=(
            "The reference model is the differential oracle: if its authority type has three "
            "shapes and four of its five component types are undeclared, then R-REF-03 "
            "(`reference_derive` must equal the production `derive`) has no fixed left-hand "
            "side to compare against. The frozen `reference_derive` body reads `parent.ops` "
            "and `constraint.ops` — field names that only the turn-[20] declaration has."
        ),
    ),
    # -- T-82..T-86: semantic-nondeterminism audit (DET-001, DET-005, DET-006).
    # The four theorem terms are UNDECLARED-TYPE for the reason DET-001 states:
    # the source uses them only inside the determinism theorem and never
    # declares any of them. These entries record the names, every use site, and
    # the gap. Following T-07's precedent, they do NOT invent declarations --
    # the definitions are U-35's to freeze.
    Term(
        "T-82", "SchedulerTrace", "SCHEDULING", "UNDECLARED-TYPE",
        "The scheduler-decision sequence the determinism theorem takes as an INPUT the "
        "machine consumes. Thirteen occurrences in 42,312 lines, every one of them a use "
        "inside the theorem or its restatements; the source never declares it, never "
        "gives it an element type, and never says whether it is finite, total over the "
        "run, or replay-consumed by cursor. U-35 must freeze it.",
        "MOD-07", "ror-runtime",
        A(25338, 31, "InitialState + SchedulerTrace + HostTrace"),
        None,
        forbidden=["EventLog (an output, not this input — see N-32)",
                   "event trace", "schedule (unqualified)"],
        protected=[("SchedulerTrace", "name used in the frozen theorem; not renamed")],
        dependents=["T-83", "T-84", "T-85"],
        obligations=["R-CORE-08", "R-ACTOR-04"],
        sections=["S-02", "S-11"],
        collisions=[],
        note="UNDECLARED. 13 occurrences, all uses: L25338, L25763, L26053, L26998, "
             "L27369, L27529, L27538, L27818, L28238, L28426, L28575, L37120, L41641. "
             "L26998 gives a NON-EQUIVALENT form (Snapshot+EventLog+HostTrace+"
             "SchedulerTrace) that conflates this input with the EventLog output; "
             "L28426/L28575 give a third (MachineState+AcceptedPlan+...). DET-001; U-35.",
    ),
    Term(
        "T-83", "HostTrace", "HOST", "UNDECLARED-TYPE",
        "The host-outcome sequence the determinism theorem takes as an INPUT. Undeclared "
        "like T-82, but unlike T-82 the source does supply a candidate shape six times "
        "over, under the name `ReplayHost` (X-87) — in six mutually incompatible forms. "
        "Only L34498 (`trace: Vec<EffectReceipt>` + `cursor`) satisfies R-HOST-03's "
        "ordered-consumption requirement; the L24011 `HashMap<EffectId, EffectReceipt>` "
        "form makes replay order-insensitive and is the reason DET-005 is HIGH.",
        "MOD-09", "ror-host",
        A(25338, 31, "InitialState + SchedulerTrace + HostTrace"),
        None,
        forbidden=["ReceiptLog (one of the six competing shapes, not the term)",
                   "EffectLog", "host log"],
        protected=[("HostTrace", "name used in the frozen theorem; not renamed")],
        dependents=["T-82", "T-84", "T-85"],
        obligations=["R-CORE-08", "R-HOST-03"],
        sections=["S-02", "S-14"],
        collisions=["X-87"],
        note="UNDECLARED as a type; six competing `ReplayHost` carriers at L1234, L9783, "
             "L10541, L22339, L24011, L34498 (six distinct shapes; `term/_structs.py` derives "
             "the same 6/6 split independently). DET-005; U-35 proposes `Vec<EffectReceipt>`, "
             "ordered and cursor-consumed, per L34498.",
    ),
    Term(
        "T-84", "InitialState", "MACHINE", "UNDECLARED-TYPE",
        "The starting configuration the determinism theorem quantifies over. Nine "
        "occurrences, all uses. Critically, the source never says whether it is closed: "
        "`GlobalState` (T-18) is the declared machine state, but the kernel authority "
        "arena (DET-009) and the capability slotmap (DET-010) are reachable from a "
        "transition and are not fields of it. If `InitialState := GlobalState` alone, "
        "the theorem is false as written; U-35 proposes `GlobalState + KernelAuthorityImage`.",
        "MOD-01", "ror-core",
        A(25338, 31, "InitialState + SchedulerTrace + HostTrace"),
        None,
        forbidden=["GlobalState (not known to be equal — that is the open question)",
                   "Snapshot", "MachineState (a competing theorem form, L28426)"],
        protected=[("InitialState", "name used in the frozen theorem; not renamed")],
        dependents=["T-18", "T-82", "T-83", "T-85"],
        obligations=["R-CORE-08"],
        sections=["S-02"],
        collisions=["X-87"],
        note="UNDECLARED. 9 occurrences: L25338, L25763, L26053, L27369, L27529, L27536, "
             "L27818, L37118, L41641. L27369 adds a `Plan` term the other forms omit. "
             "DET-001, DET-009, DET-010; U-35.",
    ),
    Term(
        "T-85", "UniqueMachineTrace", "MACHINE", "UNDECLARED-TYPE",
        "The theorem's consequent: the object asserted to be uniquely determined. Ten "
        "occurrences, all uses. The source never defines the EQUALITY under which it is "
        "unique — pointwise state identity, state-digest equality, event-envelope "
        "sequence equality, or some conjunction. Without that relation the theorem has "
        "no truth condition, which is the second half of DET-001. U-35 proposes "
        "pointwise state-digest AND event-envelope sequence equality.",
        "MOD-01", "ror-core",
        A(25340, 31, "UniqueMachineTrace"),
        None,
        forbidden=["EventLog", "trace (unqualified)", "MachineTrace (no such declaration)"],
        protected=[("UniqueMachineTrace", "name used in the frozen theorem; not renamed")],
        dependents=["T-82", "T-83", "T-84"],
        obligations=["R-CORE-08"],
        sections=["S-02"],
        collisions=["X-87"],
        note="UNDECLARED, and the equality relation is unspecified. 10 occurrences: "
             "L25340, L25763, L26053, L27370, L27541, L27818, L28241, L28426, L28575, "
             "L41642. DET-001; U-35.",
    ),
    Term(
        "T-86", "Lifetime", "AUTHORITY", "RUST-STRUCT",
        "The validity interval of an `Authority`. Declared three times identically "
        "(L3571, L4959, L5403) as `{ start: u64, end: u64 }` with the verbatim comment "
        "`// Unix timestamp` on both fields — yet it is consumed by the pure "
        "authorization predicate `authorizes(auth, effect, t: LogicalTime)` at L11881-11889 "
        "via `auth.lifetime.contains(t)`. A wall-clock interval is therefore compared "
        "against logical time inside the one predicate R-CAP-09 requires to be free of "
        "wall-clock dependence. This is DET-006 and it is a type error, not a naming "
        "preference.",
        "MOD-03", "ror-kernel",
        A(3571, 7, "pub struct Lifetime {"),
        None,
        forbidden=["WallClockInterval (the current READING, which N-33 forbids)",
                   "validity window (unqualified)", "expiry"],
        protected=[("Lifetime", "frozen Rust type name"),
                   ("contains", "frozen method name used by `authorizes`")],
        dependents=["T-28", "T-27"],
        obligations=["R-CAP-09", "R-CORE-08"],
        sections=["S-09", "S-11"],
        collisions=[],
        shape="pub struct Lifetime {\n    pub start: u64,  // Unix timestamp\n    pub end: u64,    // Unix timestamp\n}",
        note="Three identical declarations: L3571, L4959, L5403. The `// Unix timestamp` "
             "comments are verbatim frozen text. DET-006 (HIGH); U-36 proposes retyping "
             "both fields to `LogicalTime` (T-28), jointly with U-01.",
    ),
]


# ===========================================================================
# LAWS — non-conflation rules.  N-01…N-09 are the special rules the
# normalization request states verbatim; N-10…N-26 are the distinctions the
# frozen source itself requires and that the request's term list implies.
# ===========================================================================
L = Law

LAWS: list[Law] = [
    L("N-01", "T-01", "T-06",
      "`Block ≠ ExecutablePlan`. Untrusted homoiconic data is never machine input; the "
      "transition requires the whole privileged pipeline and no raw `Block` has a path "
      "into `step()`.",
      [(41440, "R-COMPILE-01 obligation text"), (3834, "`Block ≠ ExecutablePlan` stated"),
       (9115, "A raw `Block` should have no path into `step()`"),
       (869, "`ExecutablePlan` carries `_sealed: Sealed`, private to `mod compiler`")],
      "Conflation makes the language surface a security boundary. It is the first of the "
      "four boxed properties of the first security gate (§36), and mutation M001-M003 "
      "target it.",
      "R-COMPILE-01, R-COMPILE-05, R-ARCH-03, R-ORDER-03 gate property 1",
      "request §Special rule; frozen source L3834, L41440-41452"),
    L("N-02", "T-02", "T-06",
      "`PlanProposal ≠ ExecutablePlan`. A proposal is untrusted data produced by a "
      "probabilistic generator; an executable plan is a validated, sealed compiler "
      "artifact. No proposal is a plan, and no plan is a proposal.",
      [(27175, "`PlanProposal { observation_sequence, block, planner_metadata }` — it "
               "*contains* a `Block`, it is not a plan"),
       (27271, "the planner cannot bypass compilation"),
       (41440, "`Block ≠ ExecutablePlan`, and a proposal's payload is a `Block`")],
      "Conflation lets the LLM's output reach the machine without compilation, defeating "
      "R-CORE-01 (`LLMOutput ∧ UntrustedInput ↛ ExternalEffect`).",
      "R-PLANNER-01, R-PLANNER-02, R-CORE-01, R-COMPILE-02",
      "request §Special rule"),
    L("N-03", "T-09", "T-10",
      "`CapRef ≠ Authority`. A `CapRef` is an opaque generational REFERENCE "
      "(`{index, generation}`) that the evaluator may hold and pass; `Authority` is the "
      "kernel-private grant set `A = {(o, ⟨S,Q,R,T⟩)}` it denotes. The bridge is a "
      "function, not an identity: `κ(c) = Authority(c) = A_c`. The evaluator can never "
      "inspect authority internals.",
      [(7323, "`AuthOK(c,E,t) ⇔ Valid(c,t) ∧ Authorized(Authority(c),E,t)` — the authority "
              "is obtained FROM the reference"),
       (9131, "`CapRef { index: u32, generation: u32 }`, fields private"),
       (6375, "`A_o = ⟨S,Q,R,T⟩` — a grant set, not a reference"),
       (39373, "`pub(crate) struct AuthorityNode { ... }` must remain inaccessible"),
       (41054, "gate property 2: `CapRef ⇏ AuthorityInspection`")],
      "Conflation makes authority inspectable from the evaluator, which is exactly the "
      "'no hidden authority' violation R-TRUST-03 prohibits, and it makes attenuation "
      "and revocation unimplementable as algebra.",
      "R-CAP-01, R-CAP-05, R-KERN-03, R-TRUST-03, R-ORDER-03 gate property 2",
      "request §Special rule; frozen source L7323, L41052"),
    L("N-04", "T-17", "T-18",
      "`EffectRequest ≠ EffectIssued`. A request is a TRANSIENT in-memory message "
      "`{id, effect}`; an issuance is a DURABLE commitment fact. The existence of a "
      "request object is never evidence that an effect was issued: 'an effect is not "
      "considered merely issued because an in-memory object exists.'",
      [(23758, "`EffectRequest` — comment: 'Transient message to the host adapter'"),
       (23765, "`EffectIssued` — comment: 'Durable, deterministic fact of commitment'"),
       (38050, "durable issuance precedes host invocation"),
       (42082, "`HostInvoked(E) ⇒ DurableIssued(E)`")],
      "Conflation permits host invocation before durability, the exact defect "
      "`EFFECT-ISSUE-DURABLE-BEFORE-HOST` and crash point T2 exist to catch.",
      "R-DUR-01, R-DUR-02, R-EFFECT-03 step 14, R-CORE-06",
      "request §Special rule; frozen source L23726-23772"),
    L("N-05", "T-18", "T-19",
      "`EffectIssued ≠ EffectCompleted`. Issuance commits the machine to an effect; "
      "completion records the host's result. `Completed(E) ⇒ Issued(E)`, never the "
      "converse, and `Issued(E) ∧ ¬Completed(E)` is `Indeterminate` — NOT `NotExecuted`. "
      "A missing completion record is not evidence of non-execution.",
      [(35140, "`Completed(E) ⇒ Issued(E)`"),
       (26576, "`Issued(E) ∧ ¬Completed(E)` — the indeterminate classification"),
       (38232, "crash classification: issued-but-not-completed ⇒ indeterminate"),
       (42100, "never infer NotExecuted from a missing completion record")],
      "Conflation causes an indeterminate effect's escrow to be released (mutation M012) "
      "and turns a possibly-executed external effect into a silently discarded one — a "
      "double-execution or lost-effect hazard.",
      "R-DUR-03, R-DUR-04, R-RECOV-02, R-CORE-09, RECOVERY-ISSUED-INDETERMINATE",
      "request §Special rule; frozen source L26576, L35140"),
    L("N-06", "T-64", "T-65",
      "`Specification ≠ Implementation`. Frozen requirement text describes required "
      "behavior; it is not code and confers no `IMPLEMENTED` status. A Rust code block "
      "inside `Red-on-Rust.md` is specification text, never repository evidence.",
      [(38929, "status block: SPECIFICATION FROZEN / IMPLEMENTATION READY — two different "
               "axes"),
       (28263, "'machine-checked evidence that the implementation refines …' — the "
               "implementation is a separate object")],
      "Conflation promotes claims without evidence, which is the failure mode spec/00 §2 "
      "exists to prevent; at this commit every obligation is `SPECIFIED`.",
      "R-SCOPE-02, R-CLAIM-01, spec/00 §2 ladder",
      "request §Special rule"),
    L("N-07", "T-65", "T-66",
      "`Implementation ≠ Verification`. Code that exists is not code that conforms. "
      "Verification is independent evidence — differential agreement, mutation kills, "
      "crash-matrix classification — produced by machinery that shares no core logic "
      "with the implementation.",
      [(37696, "zero shared core logic between production and reference"),
       (11779, "'testing an implementation against its own buggy logic merely proves "
               "consistency, not correctness'"),
       (28277, "corrected claim wording: evidence of refinement over the tested space")],
      "Conflation makes a test suite validate its own bugs and turns coverage into a "
      "conformance claim (R-TEST-09 prohibits weakening tests for convenience).",
      "R-SCOPE-04, R-REF-02, R-CLAIM-01, R-TEST-09",
      "request §Special rule"),
    L("N-08", "T-66", "T-67",
      "`Verification ≠ Proof`. Machine-checked evidence over a tested state space is not "
      "a mathematical proof of the calculus. No theorem in the frozen source has a "
      "mechanized proof; Theorems 1-6 carry proof sketches only and remain `SPECIFIED`.",
      [(37331, "superseded phrasing 'the property tests prove the code obeys the calculus'"),
       (28263, "frozen phrasing: 'formal proof obligations remain separately identified'"),
       (2028, "Theorem 1 with a proof sketch, not a proof")],
      "Conflation produces an unjustified conformance claim; C-34 records that any report "
      "using the uncorrected phrasing violates R-CLAIM-01.",
      "R-CLAIM-01, R-CLAIM-03, spec/00 §2 `PROVEN` rung",
      "request §Special rule; frozen source L28263, L37444-37452"),
    L("N-09", "T-56", "T-10",
      "`LLM output ≠ Authority`. `LLMOutput ∈ Data`. The planner proposes and holds no "
      "authority: it cannot allocate capabilities, authorize effects, modify budgets or "
      "scheduler state, allocate actors, invoke the host, bypass compilation, or bypass "
      "persistence.",
      [(27271, "the eight enumerated planner prohibitions"),
       (27253, "`LLMOutput ∈ Data`"),
       (41320, "`LLMOutput ∧ UntrustedInput ↛ ExternalEffect`"),
       (41828, "trust table: LLM/planner = No")],
      "Conflation is the whole threat model's failure: it makes a probabilistic generator "
      "a source of authority and defeats R-CORE-01 outright.",
      "R-CORE-01, R-PLANNER-01, R-PLANNER-02, R-TRUST-01, R-TRUST-02",
      "request §Special rule; frozen source L27271-27285"),
    # ---------------------------------------------------- derived distinctions
    L("N-10", "T-03", "T-04",
      "`ParsedBlock ≠ ValidatedPlan`. Syntactic validation against the dialect grammar "
      "produces a `ParsedBlock`; static effect annotation produces a `ValidatedPlan`. "
      "Judgments 11 and 12 of turn [3] are separate gates with separate failure modes.",
      [(734, "judgment 11: `Block → ParsedBlock`"), (737, "judgment 12: `ParsedBlock → ValidatedPlan`"),
       (864, "`ParsedBlock { ast: NormalizedAST }`"), (865, "`ValidatedPlan { ir: PlanIR, effects: EffectSet }`")],
      "Conflation collapses two compiler gates into one and makes U-22 (no effect-set "
      "inference stage) invisible.",
      "R-COMPILE-02, R-COMPILE-03", "request §Required distinctions"),
    L("N-11", "T-04", "T-05",
      "`ValidatedPlan ≠ CapabilityCheckedPlan`. An effect-set annotation is not an "
      "authority verdict. Capability checking computes `κ_req` and requires "
      "`κ_req ⪯ κ_ambient`; a `ValidatedPlan` has been checked for neither.",
      [(737, "judgment 12 yields `ValidatedPlan`"), (740, "judgment 13: `ValidatedPlan → CapabilityCheckedPlan`"),
       (866, "`CapabilityCheckedPlan { ir: PlanIR, required_caps: CapSet }`")],
      "Conflation lets an effect-annotated but authority-unchecked artifact be treated as "
      "safe, and makes `CAP-DERIVE-NO-AMPLIFICATION` untestable at the boundary.",
      "R-COMPILE-03, R-CAP-04", "request §Required distinctions"),
    L("N-12", "T-05", "T-06",
      "`CapabilityCheckedPlan ≠ ExecutablePlan`. Static capability satisfaction is not "
      "resource bounding. Only the fourth stage carries `bounds: ResourceBounds` and the "
      "`_sealed` marker that makes forgery impossible.",
      [(743, "judgment 14: `CapabilityCheckedPlan → ExecutablePlan`, 'statically bounds fuel/memory'"),
       (866, "no `bounds` field"), (869, "`bounds: ResourceBounds` + `_sealed: Sealed`")],
      "Conflation admits an unbounded plan to the machine, defeating the resource-bounded "
      "half of the thesis and R-BUDGET-01.",
      "R-COMPILE-03, R-COMPILE-05, R-BUDGET-01", "request §Required distinctions"),
    L("N-13", "T-16", "T-17",
      "`Effect ≠ EffectRequest`. An `Effect` is immutable effect DATA `{op, target, "
      "params, cost}` whose canonical bytes define `EffectDigest`; an `EffectRequest` is "
      "the transient message that carries one effect plus an allocated id.",
      [(9297, "`Effect { op, target, params, cost }`"), (23758, "`EffectRequest { id, effect }`"),
       (23738, "`EffectDigest(pub [u8;32])` — 'Canonical hash of the Effect'")],
      "Conflation puts the id (an allocation counter) inside the digested bytes, so "
      "re-issuing the same effect would produce a different digest and break "
      "`EFFECT-RECEIPT-DIGEST-VALIDATION`.",
      "R-CALC-04, R-EFFECT-01, R-EFFECT-06", "request §Required distinctions"),
    L("N-14", "T-18", "T-19",
      "`EffectIssued ≠ EffectReceipt`. The issued record is the machine's durable "
      "commitment (written before host invocation); the receipt is the host's result "
      "(received after). A receipt is validated AGAINST the issued record's id and "
      "digest; it never replaces it.",
      [(23765, "`EffectIssued` — durable fact"), (23775, "`EffectReceipt` — host result"),
       (38052, "'Receipt must validate both:' id and digest")],
      "Conflation accepts a host result for an effect that was never durably committed, "
      "or accepts a mismatched receipt (mutations M011, M017).",
      "R-EFFECT-06, R-DUR-03, R-HOST-03, EFFECT-RECEIPT-DIGEST-VALIDATION",
      "request §Required distinctions"),
    L("N-15", "T-35", "T-36",
      "`ActorStatus ≠ RunState`. Two distinct frozen enums: `ActorStatus` is "
      "machine-visible (`Running/Pending/Blocked/Halted/Fault`) and `RunState` is "
      "scheduler-visible (`Runnable/Running/Pending/Blocked/Halted/Faulted`). Neither "
      "subsumes the other; `Runnable` exists only in `RunState`, `Fault` only in "
      "`ActorStatus`.",
      [(23793, "frozen `ActorStatus`"), (25526, "frozen `RunState`"),
       (25546, "`ActorState` holds BOTH: `run_state` and `status`")],
      "Conflation schedules blocked actors (mutation M013) or loses the `Runnable` "
      "at-most-once queue invariant. C-18 keeps both; the mapping is never tabulated.",
      "R-ACTOR-02, R-ACTOR-04, SCHED-BLOCKED-NOT-SCHEDULED", "request §Required distinctions; C-18"),
    L("N-16", "T-24", "T-25",
      "`Budget ≠ Consumable`. `Budget` is the triple `B = ⟨C, R, W⟩`; `Consumable` is "
      "one component of it (`C = ⟨F, I, D⟩`), the strictly-decreasing part. A budget "
      "also holds reservations and a deadline, which are not spent.",
      [(7129, "`B = ⟨C, R, W⟩`"), (7130, "`C = ⟨F, I, D⟩`: Consumable balances"),
       (9172, "`Budget { consumable, reserved, deadline }`")],
      "Conflation treats a deadline as spendable or a reservation as consumed, breaking "
      "`C_available + C_escrowed + C_consumed = C_initial`.",
      "R-BUDGET-01, R-CORE-05, BUDGET-CONSUMPTION-CONSERVATION", "request §Required distinctions"),
    L("N-17", "T-25", "T-26",
      "`Consumable ≠ Reserved`. Consumables are strictly decreasing and never returned; "
      "reserved quantities are held and then RELEASED. `ReserveOK(r,R) ⇔ R + r ≤ R_max` "
      "and `ReleaseOK(r,R) ⇔ r ≤ R` are different checks in different directions.",
      [(7130, "consumables: fuel, I/O, duration"), (7131, "reserved: memory bytes, concurrency slots"),
       (7487, "the [15] correction giving `ReserveOK`/`ReleaseOK`"),
       (7314, "the pre-fix `BudgetOK` with the WRONG reservation direction")],
      "Conflation re-introduces the C-07 direction error (an unbounded reservation "
      "passes) or leaks reserved capacity on release.",
      "R-BUDGET-03, R-BUDGET-04, BUDGET-ESCROW-CONSERVATION", "request §Required distinctions; C-07"),
    L("N-18", "T-28", "T-27",
      "`LogicalTime ≠ Deadline`. `LogicalTime` (`t`) is the machine's current explicit "
      "time, advanced by `δ_t`; a `Deadline` (`W`) is an absolute bound checked against "
      "it (`t + δ_t ≤ W`). Neither is wall-clock time.",
      [(9137, "`pub struct LogicalTime(pub u64)`"), (9140, "`pub struct Deadline(pub Option<LogicalTime>)`"),
       (6437, "'Time t is not fetched from the host OS'"), (6748, "a deadline is checked, not spent")],
      "Conflation spends the deadline as a consumable or reads the clock from the host, "
      "violating R-CAP-09 and destroying replay determinism.",
      "R-BUDGET-06, R-CAP-09, R-CORE-08", "request §Required distinctions"),
    L("N-19", "T-45", "T-49",
      "`WAL ≠ EventLog`. The WAL is DURABLE framing (`WalFrame`/`WalRecord`/"
      "`WalSequence`); the `EventLog` is the IN-MEMORY append log of `EventEnvelope`s "
      "held in `GlobalState.event_log`. Snapshot serialization records the event log's "
      "LENGTH because its contents live in the WAL.",
      [(27706, "'actual events are in the WAL' — the in-memory log is not the WAL"),
       (27716, "the WAL protocol is a durable write ordering"),
       (25539, "`GlobalState.event_log: EventLog`"), (35127, "`WalRecord::Event(EventEnvelope)`")],
      "Conflation treats an in-memory append as durability, defeating "
      "`HostInvoked(E) ⇒ DurableIssued(E)` and the WAL gap checks.",
      "R-PERSIST-01, R-PERSIST-03, R-DUR-01, WAL-GAP-REJECT", "request §Required distinctions; U-16"),
    L("N-20", "T-45", "T-23",
      "`WAL ≠ EffectJournal` as STRUCTURES, but the journal is not a separate durable "
      "file either: in the frozen 15B model the journal's records ARE `WalRecord` kinds. "
      "The journal is a causal record TAXONOMY; the WAL is the durable framing that "
      "carries it.",
      [(26216, "'a durable effect journal separate from the ordinary machine event log' — "
               "turn-[33] wording"),
       (35127, "15B: journal records are `WalRecord` variants"),
       (28427, "the boxed theorem names `CommittedSnapshot + DurableLog + EffectJournal` "
               "as three components")],
      "Conflation either duplicates durable state (two logs to keep consistent) or loses "
      "the causal laws `Issued ⇒ Prepared`, `Completed ⇒ Issued`, `Reconciled ⇒ Issued`.",
      "R-DUR-02, R-DUR-03, R-PERSIST-03", "request §Required distinctions; C-25"),
    L("N-21", "T-48", "T-45",
      "`Snapshot ≠ WAL`. A snapshot is a committed, self-consistent, canonically encoded "
      "image of `GlobalState` with a version and digest; the WAL is the ordered durable "
      "log after it. `D = ⟨S, L, H⟩` and `Recover(D) = Replay(S, L, H)`: recovery needs "
      "both, and neither substitutes for the other.",
      [(26127, "`D = ⟨S,L,H⟩`"), (26132, "`S` = persisted `GlobalState` snapshot"),
       (26133, "`L` = append-only durable event log AFTER that snapshot"),
       (26410, "`CommittedSnapshot(S) ⇒ S is self-consistent`")],
      "Conflation loses the replay-after-snapshot ordering, so recovery reconstructs a "
      "state that never existed (crash point T6).",
      "R-PERSIST-04, R-PERSIST-05, R-RECOV-01, R-RECOV-03, SNAPSHOT-COMMIT-INTEGRITY",
      "request §Required distinctions"),
    L("N-22", "T-54", "T-57",
      "`Observation (planner-facing) ≠ Observation (differential)`. Two frozen types "
      "share the name `Observation`: the planner-facing summary is UNTRUSTED-BOUNDARY "
      "data (LLM input, capability summaries only) and the differential observation is "
      "TEST data (the comparison domain). They have disjoint field sets.",
      [(27156, "planner-facing `Observation { sequence, actor, value, events, faults, "
               "available_capabilities, budget }`"),
       (36170, "differential `Observation { terminal_states, event_trace, effects, "
               "budgets, scheduler_trace, faults, state_digest }`"),
       (36183, "'a test representation, not a runtime serialization format'")],
      "Conflation lets an LLM-facing structure become the differential oracle, which "
      "collapses the oracle (15C.38 anti-oracle-collapse) and leaks machine state to the "
      "planner.",
      "R-PLANNER-01, R-REF-05, R-TEST-03", "request §Required distinctions; X-06"),
    L("N-23", "T-20", "T-21",
      "`EffectId ≠ EffectDigest`. An id is a monotonic ALLOCATION counter value; a digest "
      "is `SHA-256(canonical_bytes(effect))`, the SEMANTIC identity. Two distinct "
      "requests can carry the same digest; the same request never carries two ids. "
      "Receipt validation requires BOTH to match.",
      [(23735, "`pub struct EffectId(pub u64)`"), (23738, "`pub struct EffectDigest(pub [u8;32])`"),
       (35143, "'must carry the identical `EffectId` and `EffectDigest`'"),
       (38052, "'Receipt must validate both:'")],
      "Conflation lets a corrupted or divergent program issue a DIFFERENT effect and "
      "consume the next recorded result — 'deterministic nonsense rather than "
      "deterministic replay' (L1390).",
      "R-CALC-04, R-DUR-03, R-EFFECT-06, R-HOST-03", "request §Required distinctions"),
    L("N-24", "T-50", "T-51",
      "`Indeterminate ≠ NotExecuted`. An interrupted effect is classified indeterminate; "
      "`NotExecuted` is reachable ONLY as an authoritative `ReconciliationOutcome` from "
      "the host reconciliation protocol, never as an inference from a missing record.",
      [(26576, "`Issued(E) ∧ ¬Completed(E)` ⇒ indeterminate"),
       (26593, "`enum ReconciliationOutcome { Completed(EffectReceipt), NotExecuted, "
               "Indeterminate }`"),
       (42100, "'never infer NotExecuted'"), (38232, "crash classification at T3/T4")],
      "Conflation re-executes an effect that may already have happened — a "
      "double-spend/double-write hazard; it is also prohibited outright by R-CLAIM-02.",
      "R-DUR-04, R-RECOV-02, R-RECOV-07, R-CORE-09, R-CLAIM-02", "request §Required distinctions"),
    L("N-25", "T-41", "T-10",
      "`HostPolicy ≠ Authority`. The host gate is an INDEPENDENT defence-in-depth check "
      "that the concrete host will perform the effect; the kernel's `Authorized(A_c,E,t)` "
      "is the authority decision. Both must hold: the machine fails early on host policy "
      "at step 11 and the host's own check remains authoritative.",
      [(21893, "'This is deliberately separate from the capability kernel'"),
       (10162, "'Independent of the capability kernel's abstract authorization'"),
       (8733, "`HostPolicyOK(E)` // Gate 3"), (8820, "both `Authorized(A_c,E,t)` and "
                                                     "`HostPolicyOK(E)` in one theorem")],
      "Conflation makes one gate cover for the other: either the host becomes an authority "
      "source (untrusted, partially trusted at best) or the kernel is assumed to know "
      "OS-level permissions it cannot know.",
      "R-HOST-01, R-CORE-02, R-TRUST-01", "request §Required distinctions"),
    L("N-26", "T-42", "T-43",
      "`ReplayHost ≠ LiveHost`. The replay host consumes an ordered recorded trace and "
      "NEVER touches the external world; the live host performs real effects and is only "
      "PARTIALLY trusted. Both implement `HostExecutor`; they are not interchangeable and "
      "an unordered map is not the normative replay mechanism.",
      [(34498, "`ReplayHost { trace: Vec<EffectReceipt>, cursor: usize }`"),
       (1191, "`LiveHost`"), (24011, "the superseded `HashMap` replay form"),
       (38298, "'Do not use an unordered map as the normative replay mechanism'"),
       (41836, "trust table: Replay host = Yes, Live host = Partial")],
      "Conflation either re-executes real external effects during replay (a live side "
      "effect inside a test) or accepts unordered replay, defeating R-CORE-08 "
      "determinism.",
      "R-HOST-02, R-HOST-03, R-HOST-04, R-CORE-08", "request §Required distinctions; C-22"),
    L("N-27", "T-58", "T-65",
      "`ReferenceModel ≠ Production implementation`. They share ZERO core transition "
      "logic. The reference model is not a second copy, not a wrapper, and not a "
      "specification: it is an independently written implementation used as a comparator.",
      [(37696, "R-SCOPE-04: zero shared core logic"),
       (35347, "15C.3 independence boundary; ten forbidden dependencies"),
       (11779, "'testing an implementation against its own buggy logic merely proves "
               "consistency'")],
      "Conflation makes the differential oracle tautological (oracle collapse, 15C.38) "
      "and destroys the only independent semantic evidence the project has.",
      "R-SCOPE-04, R-REF-01, R-REF-02, R-REF-04", "request §Required distinctions"),
    L("N-28", "T-12", "T-10",
      "`Constraint ≠ Authority`. A constraint is a NARROWING REQUEST — the argument of "
      "`derive` — and can never widen: `derive(A,C) ⪯ A` and each component meets "
      "(`S ⊓ S_c`, …). A constraint is not a grant, and holding one confers nothing.",
      [(6402, "`derive_op(⟨S,Q,R,T⟩, ⟨S_c,Q_c,R_c,T_c⟩) = ⟨S⊓S_c, Q⊓Q_c, R⊓R_c, T⊓T_c⟩`"),
       (6098, "`derive(A,C) ⪯ A`"), (6536, "`pub struct Constraint<S,Q,R,L>`"),
       (6535, "`/// Constraint: distinct from Authority.` — the doc comment asserting a "
              "distinction its own declaration does not implement (X-77)"),
       (6501, "`pub struct Authority<S, Q, R, L> { pub ops: HashMap<Op, OpAuthority<S,Q,R,L>> }` "
              "— a body character-for-character identical to L6536-L6538's (X-77)"),
       (6686, "`pub struct Constraint { ops: OperationSet, scope: ScopeConstraint, params: "
              "ParamConstraint, resources: ResourceLimits, lifetime: Lifetime }` — the five-field "
              "permission-set shape that `Authority` carries at L4360, so the two names' shapes "
              "are exchanged (X-77)"),
       (485, "`attenuation: Constraint` — `Constraint` used inside `struct Capability` in turn "
             "[2], nine turns before its first declaration")],
      "Conflation permits authority amplification through a 'constraint' that actually "
      "widens — the defect `CAP-DERIVE-NO-AMPLIFICATION` and mutation M006 exist to kill.",
      "R-CAP-02, R-CAP-04, R-CORE-04, CAP-DERIVE-NO-AMPLIFICATION", "request §Required distinctions"),
    L("N-29", "T-15", "T-12",
      "`delegate ≠ attenuate ≠ derive`. `derive` is the ALGEBRA operation "
      "(`derive(A,C) ⪯ A`); `attenuate` is the in-actor MACHINE operation "
      "(`Expr::Attenuate`, rule E-Attenuate); `delegate` is the CROSS-ACTOR authority "
      "transfer accepted by the marshaller (`Expr::Delegate` / "
      "`Value::DelegatedCapability`). Ordinary marshalling rejects raw capabilities.",
      [(6397, "`derive` in the algebra"), (8717, "rule E-Attenuate uses `kernel.derive`"),
       (25989, "`Expr::Delegate { capability, constraint }`"),
       (42090, "`OrdinaryMarshal(Value::Capability) ⇒ Rejected`")],
      "Conflation lets authority cross an actor boundary by ordinary message passing, "
      "amplifying the receiver's authority — `MARSHAL-NO-RAW-CAPABILITY` and mutation "
      "M008 target it.",
      "R-MARSHAL-01, R-MARSHAL-02, R-CAP-04, R-CORE-07", "spec/05 §1 (derive/attenuate/delegate row)"),
    L("N-30", "T-39", "T-40",
      "`Mailbox ≠ RunnableQueue`. Both are FIFOs, and both are per-machine, but a mailbox "
      "holds `MarshalledValue`s for one actor while the runnable queue holds actor "
      "identities with AT-MOST-ONCE membership. A duplicate runnable entry is a defect; a "
      "duplicate message is not.",
      [(25538, "`GlobalState.runnable: RunnableQueue // FIFO, explicitly ordered`"),
       (8666, "`A_a` carries a `mailbox` component"), (25579, "`Deadlock` when all actors block"),
       (38489, "mutation: accepting duplicate runnable entries")],
      "Conflation schedules an actor twice per turn (breaking one-transition-per-turn "
      "determinism) or treats message duplication as a scheduler defect.",
      "R-ACTOR-03, R-ACTOR-04, R-ACTOR-07, SCHED-FIFO", "request §Required distinctions"),
    L("N-31", "T-69", "T-66",
      "`Frozen ≠ Verified`. 'FROZEN' means the requirement text is stable; it never means "
      "the behavior has been verified. `VERIFICATION CONTRACT: FROZEN` freezes the "
      "CONTRACT, not the evidence, and a frozen specification may still contain open "
      "contradictions and undecided items.",
      [(38935, "the four FROZEN status lines"), (37664, "'frozen means frozen'"),
       (41297, "README: 'Frozen specification ≠ verified implementation'")],
      "Conflation treats a stable document as evidence of correctness and suppresses the "
      "STOP-and-report rule when an ambiguity is found.",
      "R-SCOPE-02, R-SCOPE-03, R-TEST-09", "spec/05 §6.9-6.10; request §Special rule (by implication)"),
    L("N-32", "T-82", "T-16",
      "`SchedulerTrace ≠ EventLog`. The scheduler trace is an INPUT the machine "
      "CONSUMES to resolve its nondeterministic choices; the event log is an OUTPUT the "
      "machine PRODUCES as it runs. They are not two names for one object, and a "
      "theorem that takes the output as an input is circular: it assumes the very "
      "sequence whose uniqueness it purports to establish.",
      [(25338, "InitialState + SchedulerTrace + HostTrace"),
       (26998, "Snapshot+EventLog+HostTrace+SchedulerTrace")],
      "The L26998 form is not a restatement of the L25338 theorem but a different and "
      "weaker claim. Replay from a recorded EventLog reproduces that log trivially; it "
      "establishes nothing about determinism of the transition relation.",
      "R-CORE-08, R-ACTOR-04", "spec/06 C-98; spec/09 U-35"),
    L("N-33", "T-86", "T-28",
      "`Lifetime ≠ WallClockInterval`. An authority's validity interval is compared "
      "against LOGICAL time by `authorizes(auth, effect, t: LogicalTime)`, so its "
      "endpoints must be logical times. The frozen declaration types them `u64` and "
      "annotates both `// Unix timestamp`, which makes authorization depend on the host "
      "clock — precisely what R-CAP-09 forbids.",
      [(3571, "pub struct Lifetime {"),
       (11885, "&& auth.lifetime.contains(t)")],
      "Two machines replaying identical inputs at different wall-clock instants can "
      "reach different authorization outcomes, so the determinism theorem fails on a "
      "hidden input that appears nowhere in its antecedent.",
      "R-CAP-09, R-CORE-08", "spec/06 C-100; spec/09 U-36"),
]


# ===========================================================================
# COLLISIONS — every terminology collision found in the corpus.
#
# `new_finding=True` means no existing register (spec/06 C-…, spec/09 U-…,
# req/03 AMB-…) records it.  Where an upstream register already covers the
# item, `previously` names it and the entry is kept so this report is complete
# rather than incremental.
#
# DISPOSITION DISCIPLINE: no disposition renames a frozen API, type,
# mathematical symbol, or protocol field.  Dispositions are: record both,
# qualify in prose, require an explicit decision, or mark superseded.
# ===========================================================================
X = Collision

COLLISIONS: list[Collision] = [
    X("X-01", "`ValidatedPlan` is both a compiler stage type and a theorem predicate",
      "TYPE-ROLE-HOMONYM", "BLOCKING",
      [(865, "pub struct ValidatedPlan { ir: PlanIR, effects: EffectSet }",
        "a compiler stage struct — effect-annotated, NOT capability-checked, NOT bounded"),
       (13488, "pub struct ValidatedPlan {",
        "the same struct re-declared in the frozen turn-[21] era"),
       (1784, "\\operatorname{ValidatedPlan}(P)",
        "a PREDICATE over the plan P in the central security property"),
       (27494, "&ValidatedPlan(P)\\\\",
        "the same predicate as the first conjunct of the frozen central theorem"),
       (41338, "ValidatedPlan(P)",
        "the same predicate in the README/turn-[60] statement of the theorem")],
      "One frozen name carries two incompatible roles. As a TYPE it denotes the second "
      "compiler stage, which has not been capability-checked and not been "
      "resource-bounded. As a PREDICATE `ValidatedPlan(P)` its argument P is the plan "
      "that enters the machine — i.e. an `ExecutablePlan`, the fourth stage. The type and "
      "the predicate's argument are therefore different objects, and the predicate is "
      "true of something the type is not.",
      "An implementer who binds the theorem's `P` to the struct `ValidatedPlan` gets a "
      "plan that has passed effect annotation only. `CapabilityWithinCeiling(E)`, "
      "`BudgetAvailable(E)` and the constructor-privacy guarantee would then be checked "
      "against an artifact that never went through capability or resource analysis — the "
      "central theorem would be stated about the wrong object and the security gate would "
      "be two stages short.",
      "BOTH uses are frozen identifiers and NEITHER is renamed. Prose MUST qualify: "
      "`ValidatedPlan` (the stage type) vs `ValidatedPlan(P)` (the theorem predicate, "
      "whose argument is an `ExecutablePlan`). Code MUST NOT reuse the identifier for "
      "both: the predicate belongs in a verification context, the struct in "
      "`ror-compiler`. An explicit decision is required on whether the predicate is to be "
      "read as `IsExecutablePlan(P)`.",
      ["T-04", "T-06", "T-03", "T-05"],
      [],
      "Yes — read the theorem's `ValidatedPlan(P)` as a predicate over `ExecutablePlan`, "
      "or restate the conjunct. Affects R-CORE-02.", True),
    X("X-02", "The compilation pipeline is written with three different stage sequences",
      "STAGE-ORDER", "MAJOR",
      [(561, "Block", "ordering 1 (turn [2]): Block → ParsedBlock → ValidatedPlan → "
                      "CapabilityCheckedPlan → ExecutablePlan"),
       (567, "CapabilityCheckedPlan", "ordering 1 names four intermediate stages"),
       (9100, "Block", "ordering 1 restated (turn [17]), ending 'Machine execution'"),
       (13595, "ParsedBlock", "ordering 2 (turn [21]): Block → ParsedBlock → ValidatedPlan "
                              "→ PlanIR → ExecutablePlan; CapabilityCheckedPlan dropped, "
                              "PlanIR inserted as a stage"),
       (13603, "PlanIR", "ordering 2 makes PlanIR a STAGE after ValidatedPlan"),
       (39271, "NormalizedAST", "ordering 3 (turn [58]): Block → NormalizedAST → "
                                "ValidatedPlan → PlanIR → ExecutablePlan; ParsedBlock AND "
                                "CapabilityCheckedPlan both dropped"),
       (39273, "ValidatedPlan", "ordering 3 places ValidatedPlan after NormalizedAST")],
      "Three renderings of the same pipeline disagree on which stages exist and in what "
      "order. Ordering 3 is the latest, and it omits two of the four frozen stage TYPES "
      "(`ParsedBlock`, `CapabilityCheckedPlan`) while promoting two field types "
      "(`NormalizedAST`, `PlanIR`) to stages. The frozen structs contradict the stage "
      "reading: `ParsedBlock { ast: NormalizedAST }` makes `NormalizedAST` a FIELD of "
      "stage 1, and `ValidatedPlan { ir: PlanIR, effects: EffectSet }` makes `PlanIR` a "
      "FIELD of stage 2 — neither is a stage between the others.",
      "The pipeline is the enforcement structure of `Block ≠ ExecutablePlan` (N-01). An "
      "implementation built from ordering 3 has no capability-checked stage, so "
      "`κ_req ⪯ κ_ambient` is never a separate gate; built from ordering 2 it also has "
      "none. U-22 already records that no pipeline stage performs effect-set inference; "
      "this collision shows the stage list itself is not single-valued.",
      "All three renderings are recorded verbatim; none is deleted and no stage type is "
      "renamed. The dictionary takes the TYPE declarations (L864-L869, the only place "
      "stages are given fields) as authoritative for what the stages ARE, and records the "
      "three diagrams as three renderings of the same pipeline. An explicit decision is "
      "required on whether `CapabilityCheckedPlan` survives as a distinct stage or is "
      "folded into 'capability analysis'.",
      ["T-03", "T-04", "T-05", "T-06", "T-07", "T-08", "T-01"],
      ["U-22"], "", True),
    X("X-03", "`ExecutablePlan`'s payload field is `ir: PlanIR` in two declarations and `expr: Expr` in three",
      "FIELD-SET", "MAJOR",
      [(869, "pub struct ExecutablePlan {", "turn [3]: payload field `ir: PlanIR` (L870)"),
       (870, "ir: PlanIR,", "the turn-[3] payload field"),
       (13493, "pub struct ExecutablePlan {", "turn [21]: payload field `expr: Expr` (L13494)"),
       (13494, "expr: Expr,", "the turn-[21] payload field"),
       (14104, "pub(crate) expr: Expr,", "turn [22]: `expr: Expr`"),
       (14488, "pub(crate) expr: Expr,", "turn [22] restated"),
       (39973, "ir: PlanIR,", "turn [58] bootstrap pack: REVERTS to `ir: PlanIR`")],
      "Five declarations of one frozen type use two different names AND two different "
      "types for the payload: `ir: PlanIR` (turns [3] and [58]) vs `expr: Expr` (turns "
      "[21] and [22], twice). `Expr` is the frozen 12-constructor AST; `PlanIR` is never "
      "declared and its only visible variants (`Invoke`, `Spawn { plan, trust_level }`) "
      "use a superseded surface name (C-17) and a retracted isolation field (U-05).",
      "The payload field is what the machine evaluates. Under 'latest frozen text "
      "governs' the turn-[58] `ir: PlanIR` would win — which would make the runtime "
      "evaluate an undeclared type whose variants are superseded, and would contradict "
      "the frozen `Expr` AST, `EvalState.expr`, and every transition rule written over "
      "`Expr`. This is a type-level contradiction in the single most security-critical "
      "artifact in the system.",
      "Both field names and both field types are recorded; NEITHER is renamed and neither "
      "is silently dropped. The dictionary reports the contradiction and requires an "
      "explicit decision. Evidence favouring `expr: Expr` (declared AST, used by "
      "`EvalState`, `step()`, and all transition rules) is stated as evidence, not "
      "applied.",
      ["T-06", "T-08", "T-30"],
      [], "Yes — which payload field/type is frozen: `expr: Expr` or `ir: PlanIR`. "
          "Blocks R-COMPILE-04/05 and M2.", True),
    X("X-04", "The central theorem's first conjunct is `ValidatedRequest(E)` in one frozen statement and `ValidatedPlan(P)` in two",
      "PREDICATE-SIGNATURE", "MAJOR",
      [(23040, "ValidatedRequest(E)", "turn [29]: first conjunct, argument is the EFFECT E"),
       (23694, "\\text{ValidatedRequest}(E)", "turn [30] 'strongest Phase 12 theorem', boxed"),
       (27494, "&ValidatedPlan(P)\\\\", "turn [33]: first conjunct, argument is the PLAN P"),
       (41338, "ValidatedPlan(P)", "turn [60]/README: first conjunct, argument is the PLAN P")],
      "The single most important formula in the specification — `ExternalEffect(E) ⇒ …` — "
      "exists in two forms that differ in their FIRST conjunct, and the difference is not "
      "cosmetic: `ValidatedRequest(E)` is a predicate about the request being validated "
      "(argument: an `Effect`), while `ValidatedPlan(P)` is a predicate about the plan "
      "being validated (argument: a plan). `ValidatedRequest` occurs nowhere else in "
      "42,312 lines.",
      "The two readings impose different obligations. 'The request was validated' is a "
      "runtime, per-effect property (gates 1-13 of the 16-step sequence). 'The plan was "
      "validated' is a compile-time, per-plan property (R-COMPILE-01..05). An "
      "implementation satisfying only one would claim conformance with R-CORE-02 while "
      "leaving the other half unchecked.",
      "Both forms are recorded verbatim. The canonicalization layer (spec/00 §4, spec/01 "
      "R-CORE-02, README) already adopts `ValidatedPlan(P)` per latest-frozen-text; this "
      "entry records that the earlier form exists, that its argument type differs, and "
      "that no supersession note covers the change. `ValidatedRequest` is NOT forbidden "
      "(it is frozen source text) but is NOT canonical prose.",
      ["T-04", "T-02", "T-16", "T-17"],
      [], "Yes — confirm which conjunct R-CORE-02 states, and whether both properties are "
          "required (they are not equivalent).", True),
    X("X-05", "`Authorized` has six incompatible signatures, including both orders in the governing invariant",
      "PREDICATE-SIGNATURE", "MAJOR",
      [(3293, "Authorized(E,\\kappa)", "turn [6]: (Effect, capability-map) — 2 arguments"),
       (4687, "Authorized(E)", "turn [8]: (Effect) — 1 argument"),
       (5998, "Authorized(A,E,t)", "turn [10]: (Authority, Effect, time) — 3 arguments"),
       (6548, "/// Canonical Authorization Predicate: Authorized(A, E, t)",
        "turn [11] declares THIS the canonical predicate"),
       (7152, "\\text{Authorized}(\\kappa(c_{ref}), E, t)", "turn [13]: (κ(c), Effect, time)"),
       (8548, "Authorized(A_c,E,t)", "turn [15]: (A_c, Effect, time)"),
       (41339, "Authorized(E,\\kappa,t)", "turn [60]/README: (Effect, capability-map, time) "
                                          "— argument ORDER SWAPPED vs the declared canonical form")],
      "The authorization predicate — the heart of the trust model — is written with six "
      "different arities and argument orders. Turn [11] explicitly declares "
      "`Authorized(A, E, t)` 'the Canonical Authorization Predicate', yet the frozen "
      "governing invariant in the README and turn [60] writes `Authorized(E, κ, t)`: the "
      "arguments are transposed and the second is the whole capability map `κ` rather "
      "than an `Authority`.",
      "The signature determines what the kernel is given. `Authorized(A,E,t)` takes an "
      "already-resolved `Authority` (so `κ(c)` resolution happens before the call); "
      "`Authorized(E,κ,t)` takes the map (so resolution happens inside). Those are "
      "different APIs with different trust boundaries, and N-03 (`CapRef ≠ Authority`) is "
      "enforced precisely at that resolution step. A transposed signature also makes "
      "`¬Authorized(E,κ,t) ⇒ ¬ExternalEffect(E)` (R-CORE-03) un-type-checkable against "
      "the declared canonical form.",
      "All six signatures are recorded; none is renamed and none is deleted. The "
      "dictionary requires qualified prose that always shows the argument list. spec/01 "
      "R-CORE-02 and R-CORE-03 currently use both orders in adjacent requirements; that "
      "is reported (X-41 family) rather than silently harmonized. An explicit decision is "
      "required on the canonical signature.",
      ["T-10", "T-09", "T-13", "T-16"],
      [], "Yes — freeze one signature for `Authorized` and state whether the second "
          "argument is an `Authority` or the map `κ`. Affects R-CORE-02/03, R-KERN-02.", True),
    X("X-06", "Two incompatible frozen `Observation` structs share one name",
      "TYPE-HOMONYM", "MAJOR",
      [(27156, "pub struct Observation {",
        "turn [33] PLANNER-facing: `{sequence, actor, value, events, faults, "
        "available_capabilities, budget}` — LLM-boundary input data"),
       (36170, "pub struct Observation {",
        "turn [48] DIFFERENTIAL: `{terminal_states, event_trace, effects, budgets, "
        "scheduler_trace, faults, state_digest}` — test comparison data")],
      "One name, two frozen declarations, disjoint field sets, different producers, "
      "different consumers, and different trust roles. The turn-[33] type is what the "
      "untrusted planner is shown (capability SUMMARIES only); the turn-[48] type is what "
      "the comparator consumes, and the source itself says it 'is a test representation, "
      "not a runtime serialization format' and 'must not become a third semantic wire "
      "protocol'.",
      "This is structurally the same defect as the `Value` domain collision (C-03/C-45) "
      "but it is NOT registered anywhere. The consequences are worse in one respect: if "
      "the planner-facing type is used as the differential observation, the oracle "
      "collapses to what the planner is allowed to see (15C.38 anti-oracle-collapse), and "
      "if the differential type is handed to the planner it leaks internal machine state "
      "(scheduler trace, state digest) across the untrusted boundary. Neither type's "
      "element types (`GlobalEvent`, `CapabilitySummary`, `BudgetSummary`, `Observed*`) "
      "is declared.",
      "Both declarations are recorded verbatim and NEITHER is renamed, because renaming a "
      "frozen Rust type is an API change requiring an explicit decision. The dictionary "
      "disambiguates in PROSE only, by the parenthetical qualifiers `Observation "
      "(planner-facing)` and `Observation (differential)`, and makes the separation a law "
      "(N-22). spec/05 §5 lists only the differential sense; that omission is part of "
      "this finding.",
      ["T-54", "T-57", "T-02", "T-58"],
      [], "Yes — give the two types distinct frozen names, or state that one is "
          "normative. Affects R-PLANNER-01 and R-REF-05.", True),
    X("X-07", "`EffectIssued` denotes a struct, a `WalRecord` variant and an `EffectJournalEntry` variant, with different payloads and field names",
      "STATE-VS-RECORD", "MAJOR",
      [(1377, "EffectIssued {", "turn [3] prose record: `{effect_id, capability, effect, target}`"),
       (2254, "\\text{EffectIssued}(E.\\text{id},\\; c,\\; E)", "turn [5]: an EVENT-LOG entry carrying the CapRef `c`"),
       (23765, "pub struct EffectIssued {", "turn [30] struct: `{id, actor, effect_digest, "
                                            "logical_time, issue_cost, reservation}`"),
       (26229, "Issued {", "turn [33] `EffectJournalEntry::Issued {id, actor, digest}`"),
       (27729, "EffectIssued { id: EffectId, actor: ActorId, digest: EffectDigest },",
        "turn [34] `WalRecord::EffectIssued`"),
       (35130, "EffectIssued { id: EffectId, actor: ActorId, digest: EffectDigest },",
        "turn [47] frozen 15B `WalRecord::EffectIssued`"),
       (35140, "\\text{Issued}(E)", "turn [47] lifecycle PREDICATE `Completed(E) ⇒ Issued(E)`")],
      "One name carries four denotations across the frozen text: a prose record shape, an "
      "event-log entry, a standalone struct, an enum variant (twice, with and without the "
      "`Effect` prefix), and a lifecycle predicate. The payloads are not equivalent: the "
      "frozen struct carries `effect_digest`, `logical_time`, `issue_cost` and "
      "`reservation`; the frozen WAL variant carries only `id`, `actor` and `digest`. The "
      "digest field is spelled `effect_digest` in the structs and `digest` in the variants.",
      "The omitted fields are load-bearing. `reservation` is what makes "
      "`BUDGET-ESCROW-CONSERVATION` recoverable: if the durable issued record does not "
      "carry the reserved quantity, recovery cannot know how much escrow to hold for an "
      "indeterminate effect (N-24 forbids releasing it). `logical_time` is needed to "
      "re-establish `DeadlineValid`. The field-name split (`effect_digest` vs `digest`) "
      "means a single serialization routine cannot serve both carriers.",
      "Every form is recorded verbatim; no field is renamed and no variant is dropped. "
      "The dictionary separates the four roles by TYPE (struct / record kind / lifecycle "
      "state / event) and requires prose to name the carrier explicitly — 'the "
      "`EffectIssued` struct' vs 'the `WalRecord::EffectIssued` record' vs 'the issued "
      "state'. The payload divergence is reported as needing a decision, not reconciled "
      "by inventing fields.",
      ["T-18", "T-47", "T-23", "T-20", "T-21", "T-26"],
      ["C-25"], "Yes — state whether the durable issued record must carry `reservation`, "
                "`logical_time` and `issue_cost`, and fix one spelling for the digest "
                "field. Affects R-DUR-02/03, R-BUDGET-04, R-RECOV-02.", True),
    X("X-08", "The symbol `C` denotes the Consumable vector, the Constraint of `derive`, and a required-capability set",
      "SYMBOL-OVERLOAD", "MAJOR",
      [(7130, "$C = \\langle F, I, D \\rangle$", "turn [13]: `C` = Consumable balances"),
       (6098, "derive(A,C)\\preceq A", "turn [10]: `C` = Constraint, the argument of derive"),
       (8717, "\\text{kernel.derive}(c, C_{\\text{req}})", "turn [15]: `C_req` = required constraint"),
       (1976, "\\Gamma ; \\kappa \\vdash e \\Leftarrow C_{\\text{req}}",
        "turn [4]: `C_req` = the required CAPABILITY set in judgment J3"),
       (8707, "C' = C - \\text{cost}_C(\\text{let})", "turn [15]: `C` = Consumable, inside "
                                                      "the actor state `A_a`"),
       (227, "C = \\langle \\tau, \\sigma, \\eta \\rangle", "turn [1]: `C` = a CAPABILITY record (τ, σ, η) — a fourth meaning, neither Consumable nor Constraint")],
      "`C` is simultaneously (a) the consumable budget vector, (b) the constraint "
      "argument of the derivation operator, and (c) subscripted as `C_req` for two "
      "different things — a required constraint (turn [15]) and a required capability set "
      "(turn [4] judgment J3). Both (a) and (b) appear in BOXED frozen formulae, and both "
      "appear in the README: `derive(A,C) ⪯ A` in the authority section and "
      "`C = ⟨F,I,D⟩` in the resource section.",
      "`derive(A,C) ⪯ A` is the no-amplification theorem (R-CORE-04). Read with `C` = "
      "Consumable it is nonsense; read with `C` = Constraint it is the load-bearing "
      "security law. Conversely `C' = C − cost_C(let)` is nonsense with `C` = Constraint. "
      "An implementer formalizing either formula must guess, and the two guesses live in "
      "different modules (MOD-03 capability vs MOD-04 budget).",
      "Both denotations are recorded and NEITHER symbol is renamed — renaming a "
      "mathematical symbol would silently alter a frozen formula. The dictionary requires "
      "that prose and any mechanization state the namespace: 'the constraint C' vs 'the "
      "consumable vector C'. Where a formula is quoted, it is quoted verbatim with its "
      "turn provenance so the intended denotation is recoverable from context.",
      ["T-25", "T-12", "T-10", "T-24"],
      [], "", True),
    X("X-09", "The symbol `R` denotes Reserved resources, the authority resource limit, a capability ceiling, a dynamic budget, a receipt, and the revocation set",
      "SYMBOL-OVERLOAD", "MAJOR",
      [(7131, "$R = \\langle M, S \\rangle$", "turn [13]: `R` = Reserved capacities"),
       (6375, "$$A_o = \\langle S, Q, R, T \\rangle$$", "turn [11]: `R` = the per-operation "
                                                        "ResourceLimit component of Authority"),
       (5778, "cost(E)\\le R_A", "turn [9]: `R_A` = a capability's resource ceiling"),
       (6420, "the capability's ceiling $R_A$. The dynamic execution budget $R_B$",
        "turn [11] EXPLICITLY distinguishes `R_A` from `R_B`"),
       (2021, "R.\\text{id} = E.\\text{id}", "turn [5]: `R` = an EffectReceipt"),
       (341, "the global Revocation Set $\\mathcal{R}$", "turn [1]: calligraphic `R` = the "
                                                          "revocation lineage set")],
      "`R` carries at least six denotations, four of them in frozen formulae: the "
      "Reserved budget vector, the authority's resource-limit component, a receipt, and "
      "(calligraphic) the revocation set. Two further subscripted forms — `R_A` "
      "(capability ceiling) and `R_B` (dynamic execution budget) — are distinguished only "
      "by a prose note at L6420.",
      "`ReserveOK(r,R) ⇔ R + r ≤ R_max` (budget) and `cost(E) ≤ R_A` (authority ceiling) "
      "are DIFFERENT checks against DIFFERENT objects, and R-BUDGET-03 vs R-CAP-03 own "
      "them separately. An implementation that conflates them either lets a capability's "
      "ceiling be satisfied by the actor's free memory, or lets the actor's reservation "
      "exceed the grant. The receipt reading of `R` additionally collides inside the "
      "receipt rule itself (`R.id = E.id`).",
      "All denotations recorded; no symbol renamed. The source's own disambiguation at "
      "L6420 is adopted as the dictionary's rule: `R_A` is a capability ceiling "
      "(authority), `R_B`/`R` is the actor's reserved budget (resource), `R` in a receipt "
      "rule is a receipt, and `ℛ` is the revocation set. Prose MUST name the object, not "
      "the letter.",
      ["T-26", "T-10", "T-19", "T-24"],
      [], "", True),
    X("X-10", "The symbol `S` denotes the Snapshot, the authority Scope component, and concurrency Slots",
      "SYMBOL-OVERLOAD", "MAJOR",
      [(26132, "- \\(S\\) = persisted `GlobalState` snapshot,", "turn [33]: `S` = the Snapshot "
                                                               "in `D = ⟨S,L,H⟩`"),
       (6375, "$$A_o = \\langle S, Q, R, T \\rangle$$", "turn [11]: `S` = the Scope component "
                                                         "of an operation authority"),
       (7131, "$R = \\langle M, S \\rangle$", "turn [13]: `S` = concurrency Slots inside "
                                              "Reserved"),
       (26410, "CommittedSnapshot(S)", "turn [33]: `S` as the predicate's argument — the "
                                       "snapshot reading"),
       (6426, "S_{A'} \\preceq_S S_A", "turn [11]: `S` under its own scope order `⪯_S`")],
      "`S` is the snapshot (persistence), the scope component of authority (capability "
      "algebra), and the concurrency-slot dimension of Reserved (budget) — three frozen "
      "denotations in three different modules, two of them inside tuple definitions "
      "(`⟨S,L,H⟩` and `⟨M,S⟩`) that both describe durable/bounded state.",
      "`R = ⟨M,S⟩` and `D = ⟨S,L,H⟩` can appear on the same page of a persistence design: "
      "in the first, `S` is slots; in the second, `S` is the snapshot. An implementer "
      "deriving a snapshot schema from the tuple forms could carry a slot count where a "
      "state image belongs. The scope reading additionally has its own order symbol "
      "`⪯_S`, so `S ⪯_S S'` and `S is self-consistent` are unrelated statements sharing "
      "notation.",
      "All three recorded; none renamed. Prose MUST qualify: 'the snapshot S', 'the scope "
      "component S', 'the slot dimension S'. Struct field names (`slots`, `scope`, "
      "`version`/`state_digest`) are the unambiguous layer and are preferred in any "
      "implementation-facing text.",
      ["T-48", "T-10", "T-26"],
      [], "", True),
    X("X-11", "The symbol `A` denotes Authority and, subscripted, an actor's state",
      "SYMBOL-OVERLOAD", "MINOR",
      [(6146, "Authority =", "turn [10]: `A` = Authority"),
       (8666, "$$ A_a = \\langle e, \\rho, \\kappa, \\mathcal{H}, C, R, W, \\text{mailbox}, \\text{status} \\rangle $$",
        "turn [16]: `A_a` = the ActorState of actor a"),
       (340, "the block in $A_A$, serializes the data, and reconstructs an isomorphic block in $A_B$",
        "turn [1]: `A_A`/`A_B` = actor A's / actor B's state"),
       (6501, "pub struct Authority<S, Q, R, L> {", "turn [11]: `Authority` as a Rust type")],
      "`A` is Authority in the capability algebra and, subscripted, an actor's local "
      "state in the operational semantics — with turn [1] using capital subscripts "
      "(`A_A`, `A_B`) and turn [16] using a lower-case one (`A_a`). Inside `A_a`'s own "
      "definition, `C` and `R` are budget components (X-08, X-09), so a single formula "
      "overloads three letters at once.",
      "`derive(A,C) ⪯ A` (authority) and `G[a ↦ A_a[…]]` (actor state) are the two most "
      "quoted formulae in their respective modules. Reading `A_a` as 'the authority of a' "
      "would make the transition rules claim that every step rewrites an authority — the "
      "opposite of the no-amplification law.",
      "Both recorded; neither renamed. The dictionary fixes prose: 'the authority A' vs "
      "'the actor state A_a'. Subscript case is preserved verbatim in quotations "
      "(`A_A`/`A_B` in turn [1], `A_a` from turn [15] on) and flagged as superseded "
      "notation, not corrected.",
      ["T-10", "T-37"],
      [], "", True),
    X("X-12", "The symbol `D` denotes the durable machine state and the duration consumable",
      "SYMBOL-OVERLOAD", "MAJOR",
      [(26127, "D=\\langle S,L,H\\rangle", "turn [33]: `D` = the durable machine state"),
       (26139, "Recover(D)=Replay(S,L,H)", "turn [33]: `D` as the recovery function's argument"),
       (7130, "$C = \\langle F, I, D \\rangle$", "turn [13]: `D` = the duration dimension of "
                                                  "Consumable"),
       (41544, "C=\\langle F,I,D\\rangle", "README/turn [60]: `D` = duration")],
      "`D` is the entire durable state in the recovery model (`Recover(D) = "
      "State_before_crash`, the qualified theorem of R-CORE-09) and one budget dimension "
      "in the resource model. Both are frozen, both appear in boxed formulae, and both "
      "belong to requirements about crash safety.",
      "The recovery theorem `Recover(D) = State_before_crash` and the budget vector "
      "`C = ⟨F,I,D⟩` are both cited by crash-recovery obligations. A reader who takes "
      "`D` as duration in the recovery theorem reads it as 'recovering the duration "
      "budget', and a reader who takes `D` as durable state in the budget vector reads "
      "the consumable triple as ⟨fuel, I/O, durable state⟩. U-01 already leaves the "
      "operational meaning of duration undefined, so the collision compounds an open "
      "decision.",
      "Both recorded; neither renamed. Prose MUST say 'the durable state D' or 'the "
      "duration dimension D'. The dictionary notes that `Deadline` (`W`) and duration "
      "(`D`) are additionally distinct bounds (N-18), so the letter `D` must never be "
      "used for a deadline.",
      ["T-25", "T-52", "T-27"],
      ["U-01"], "", True),
    X("X-13", "The symbol `L` denotes the durable WAL, the Lifetime authority component, and the transition-tuple log",
      "SYMBOL-OVERLOAD", "MAJOR",
      [(26133, "- \\(L\\) = append-only durable event log after that snapshot,",
        "turn [33]: `L` = the WAL / durable log"),
       (6501, "pub struct Authority<S, Q, R, L> {", "turn [11]: `L` = the Lifetime type "
                                                     "parameter"),
       (6497, "pub lifetime: L,", "turn [11]: `L` bound to the field `lifetime`"),
       (2254, "\\mathcal{L} \\oplus \\text{EffectIssued}(E.\\text{id},\\; c,\\; E)",
        "turn [5]: calligraphic `L` = the log appended to by transitions"),
       (2290, "\\langle e, \\rho, \\kappa, \\mathcal{H}, B, \\mathcal{L} \\rangle",
        "turn [6]: `𝓛` as a machine-configuration component")],
      "`L` is the durable log in the recovery model, the lifetime component of authority "
      "in the capability algebra (where it is ALSO the symbol that collides with the "
      "math's `T`, X-17), and — calligraphic — the append-only log carried in the "
      "transition tuples of turns [5]-[6]. The plain and calligraphic forms are not "
      "consistently distinguished: turn [33] uses plain `L` for the durable log while "
      "turns [5]-[6] use `𝓛` for the transition log.",
      "Lifetime is a security-relevant authority component (`Valid(c,t)` checks it) and "
      "the WAL is the durability mechanism; both appear in crash-recovery reasoning. "
      "`Replay(S,L,H)` read with `L` = lifetime is meaningless, and `⟨S,Q,R,L⟩` read with "
      "`L` = a log makes the authority order untypeable.",
      "All recorded; none renamed. Prose MUST qualify: 'the durable log L', 'the lifetime "
      "component L', 'the transition log 𝓛'. Quotations preserve the source's own "
      "calligraphic/plain distinction exactly.",
      ["T-45", "T-10", "T-49", "T-52"],
      [], "", True),
    X("X-14", "The symbol `H` denotes the effect journal while calligraphic `ℋ` denotes the heap",
      "SYMBOL-OVERLOAD", "MINOR",
      [(26134, "- \\(H\\) = durable host-effect journal.", "turn [33]: `H` = the EffectJournal"),
       (718, "$$ \\Sigma = \\langle P, \\rho, \\kappa, \\mathcal{H}, \\phi, \\mathcal{E} \\rangle $$",
        "turn [2]: calligraphic `ℋ` = the agent's isolated heap/arena"),
       (724, "*   $\\mathcal{H}$: The agent's isolated heap/arena.", "turn [2] defines `ℋ` "
                                                                     "as the heap"),
       (8666, "A_a = \\langle e, \\rho, \\kappa, \\mathcal{H}, C, R, W", "turn [16]: `ℋ` "
                                                                          "inside the actor state")],
      "Plain `H` is the durable effect journal; calligraphic `ℋ` is the per-actor heap, "
      "used 86 times including inside the frozen actor-state definition. The distinction "
      "exists but rests entirely on a font change, and the two denote a durable record "
      "family and an in-memory arena respectively.",
      "spec/05 §4 lists `H` as an alias of the effect journal without noting that `ℋ` is "
      "the heap; a reader applying that alias to the transition rules would read the "
      "actor's heap as a journal. Low probability, high confusion cost, and trivially "
      "avoided by naming the object.",
      "Both recorded; neither renamed. The dictionary requires prose to name the object "
      "('the journal H', 'the heap ℋ') and preserves the calligraphic form verbatim in "
      "every quotation. spec/05's alias row is annotated accordingly (X-41 family).",
      ["T-23", "T-37", "T-45"],
      [], "", True),
    X("X-15", "The symbol `B` denotes the Budget and, in turn [1], a Block",
      "SYMBOL-OVERLOAD", "MINOR",
      [(7129, "$$ B = \\langle C, R, W \\rangle $$", "turn [13]: `B` = Budget"),
       (132, "generates a new block $B$ utilizing only the sanctioned vocabulary",
        "turn [1]: `B` = a Block"),
       (7171, "f = (\\lambda \\bar{x}. e_{body})^{\\Phi_f}_{B_f}", "turn [13]: `B_f` = a "
                                                                    "closure's budget annotation"),
       (2217, "B_{\\text{child}} \\leq B_{\\text{alloc}}", "turn [4]: `B_child`, `B_alloc` = "
                                                            "spawn budgets")],
      "`B` is the budget triple in every frozen-era formula and a block in the turn-[1] "
      "epistemic-loop narrative. The subscripted family (`B_f`, `B_max`, `B_child`, "
      "`B_alloc`, `B_parent_remainder`) is uniformly budget-valued.",
      "The turn-[1] use predates the typed `Block` and is narrative, so the practical "
      "risk is confined to reading early text. It matters for one reason: `Block` is the "
      "untrusted input of N-01, and a reader who carries `B` = block into the budget "
      "formulae would read `B = ⟨C,R,W⟩` as a decomposition of untrusted program data.",
      "Both recorded; neither renamed. `B` is canonical for Budget from turn [13] onward; "
      "the turn-[1] block usage is marked superseded narrative and quoted only with its "
      "provenance. Prose uses `Block`, never `B`, for program data.",
      ["T-24", "T-01"],
      [], "", True),
    X("X-16", "`F` denotes fuel, the effect set, and 'effect invoked'; `M` denotes memory and a replay-tuple component",
      "SYMBOL-OVERLOAD", "MAJOR",
      [(7130, "$C = \\langle F, I, D \\rangle$", "turn [13]: `F` = fuel"),
       (2217, "\\;!\\; \\mathcal{F} \\;@\\; B_{\\text{child}}", "turn [4]: calligraphic `F` = "
                                                                "the static effect SET"),
       (7171, "(\\lambda \\bar{x}. e_{body})^{\\Phi_f}_{B_f}", "turn [13]: `Φ_f` = a "
                                                                "function's effect set"),
       (672, "effect invoked", "turn [2]: the third component of the replay tuple "
                               "`(B_0,κ_0,F_0,M_0)` is the effect invoked"),
       (658, "(B_0,\\kappa_0,F_0,M_0)", "turn [2]: `F_0` = effect invoked, `M_0` = arguments"),
       (7131, "$R = \\langle M, S \\rangle$", "turn [13]: `M` = memory bytes")],
      "`F` is the fuel dimension of Consumable, the (calligraphic or `Φ`-form) static "
      "effect set of the judgments, and — in the turn-[2] replay tuple — the effect "
      "invoked. `M` is the memory dimension of Reserved and, in the same turn-[2] tuple, "
      "the arguments. The turn-[2] tuple's own legend (L668-676) maps its four components "
      "to input block / capability identity / effect invoked / arguments, so `B`, `κ`, "
      "`F`, `M` all denote something other than their frozen meanings there.",
      "Fuel and effect sets are the two things the compiler's resource and effect "
      "analyses produce, and U-22 records that no pipeline stage is named as producing "
      "the effect set `F`. A reader resolving `F` to fuel in that gap report reads it as "
      "a missing fuel analysis; the actual gap is effect-set inference. That is a "
      "different requirement with a different owner.",
      "All denotations recorded; none renamed. The dictionary requires prose to name the "
      "object ('fuel F', 'the effect set 𝓕', 'the function's effect annotation Φ_f') and "
      "marks the turn-[2] replay tuple as superseded notation whose component letters do "
      "not carry their later meanings.",
      ["T-25", "T-26", "T-12", "T-08"],
      ["U-22"], "", True),
    X("X-17", "Authority's fourth component is `T` in the frozen math and `L` in the frozen Rust sketch of the same turn",
      "SYMBOL-OVERLOAD", "MAJOR",
      [(6375, "$$A_o = \\langle S, Q, R, T \\rangle$$", "turn [11] math: the fourth "
                                                         "component is `T`"),
       (6402, "\\langle S \\sqcap S_c,\\; Q \\sqcap Q_c,\\; R \\sqcap R_c,\\; T \\sqcap T_c \\rangle",
        "turn [11] `derive_op`: meets over `S,Q,R,T`"),
       (6497, "pub lifetime: L,", "turn [11] Rust: the same component is named `lifetime` "
                                  "with type parameter `L`"),
       (6501, "pub struct Authority<S, Q, R, L> {", "turn [11] Rust: `Authority<S,Q,R,L>`"),
       (6505, "impl<S: Scope, Q: ParamConstraint, R: ResourceLimit, L: Lifetime>",
        "turn [11]: `L: Lifetime` confirms `L` is the lifetime component")],
      "Inside a single turn, the frozen capability algebra writes the per-operation "
      "authority as `⟨S,Q,R,T⟩` and the accompanying Rust sketch parameterizes the same "
      "object as `Authority<S,Q,R,L>` with `L: Lifetime` and a field named `lifetime`. "
      "`T` and `L` denote the same component. `L` independently denotes the durable log "
      "(X-13) and `T` independently denotes crash points `T0`-`T6` and the `TEST` "
      "obligation prefix.",
      "The no-amplification theorem is stated over all four components "
      "(`T' ⪯_T T` in the proof sketch at L6426). A mechanization that binds `T` to the "
      "crash-point namespace, or `L` to the WAL, mis-states R-CORE-04. The Rust generic "
      "parameter list is an API surface, so renaming either side is prohibited.",
      "Both symbols recorded as denoting the same component; NEITHER is renamed. The "
      "dictionary states the mapping explicitly — math `T` = Rust `L` = the field "
      "`lifetime` — and requires any mechanization or implementation to carry both "
      "notations with the mapping attached. spec/00 §6 lists the kept math symbols but "
      "not this one; the omission is noted rather than back-filled silently.",
      ["T-10", "T-12", "T-45"],
      [], "", True),
    X("X-18", "The machine configuration is written three ways: `Σ` (6 components), an unnamed 7-tuple, and `G`/`A_a` (9 components)",
      "SCOPE-DRIFT", "MAJOR",
      [(718, "$$ \\Sigma = \\langle P, \\rho, \\kappa, \\mathcal{H}, \\phi, \\mathcal{E} \\rangle $$",
        "turn [2]: `Σ` = ⟨program, env, caps, heap, fuel, event log⟩"),
       (7161, "\\langle \\text{let } x = v \\text{ in } e_2, \\rho, \\kappa, B, t, \\mathcal{H}, \\mathcal{E} \\rangle",
        "turn [13]: a 7-component configuration ⟨expr, env, caps, BUDGET, time, heap, log⟩ "
        "— fuel replaced by a whole `B`, and `t` added"),
       (8666, "$$ A_a = \\langle e, \\rho, \\kappa, \\mathcal{H}, C, R, W, \\text{mailbox}, \\text{status} \\rangle $$",
        "turn [16]: the per-actor state, 9 components, budget split into `C,R,W`"),
       (8702, "Transitions are written as $G \\xrightarrow{a, c} G'$", "turn [16]: `G` "
                                                                       "replaces `Σ` as the "
                                                                       "global configuration"),
       (11061, "fn step_request(actor: &mut ActorState, machine: &mut GlobalConfig, expr: Expr)",
        "turn [18]: the Rust name is `GlobalConfig` here and `GlobalState` from turn [31]")],
      "The object a transition acts on is written three different ways with three "
      "different component sets, and the global/per-actor split moves: turn [2] has one "
      "flat `Σ`; turn [13] has a flat 7-tuple with `B` and `t`; turn [16] splits into a "
      "global `G` mapping actor ids to 9-component `A_a`s. spec/00 §6 lists `Σ` and `G` "
      "as kept symbols without recording that they are different shapes.",
      "Determinism is stated over machine configurations: `InitialState + SchedulerTrace "
      "+ HostTrace ⇒ UniqueMachineTrace` (R-CORE-08), and snapshot determinism requires a "
      "byte-stable state (R-PERSIST-05). Which components constitute 'the state' decides "
      "what a state digest covers. C-15/U-02 already record that no canonical encoding is "
      "frozen for machine state; this collision shows the state's SHAPE is not "
      "single-valued either.",
      "All three notations recorded verbatim; none renamed. The dictionary adopts the "
      "turn-[16]/[31] split (`GlobalState` + `ActorState`) as the current shape because "
      "it is the only one with frozen Rust declarations, and marks `Σ` and the 7-tuple as "
      "superseded notations retained for traceability. The component-set difference is "
      "reported, not papered over.",
      ["T-38", "T-37", "T-32", "T-25"],
      ["C-42", "U-02"], "", True),
    X("X-87",
      "`ReplayHost` — the sole concrete realization of the theorem's `HostTrace` "
      "parameter — is declared six times in six incompatible shapes, and only one "
      "of them is ordered",
      "DIVERGENT-SHAPE", "MAJOR",
      [(1234, "pub struct ReplayHost {",
        "turn [3]: `cursor: usize` + `trace: Vec<Result<Value, HostFault>>` — ordered, "
        "but the element type is a bare `Value`, not a receipt"),
       (9783, "pub struct ReplayHost {",
        "turn [17]: `trace: ReplayTrace` — delegates the shape to a type that is itself "
        "never declared"),
       (10541, "pub struct ReplayHost {",
        "turn [18]: `trace: VecDeque<EffectReceipt>` consumed by `pop_front()` — ordered, "
        "receipt-typed, and the only form whose consumption discipline is visible in its "
        "own body"),
       (22339, "pub struct ReplayHost {",
        "turn [29]: `receipts: ReceiptLog` — a third undeclared carrier type"),
       (24011, "pub struct ReplayHost {",
        "turn [30]: `recorded_receipts: HashMap<EffectId, EffectReceipt>` + `cursor: usize` "
        "commented `// For ordered trace consumption if needed` — UNORDERED lookup, and "
        "the cursor is optional by its own comment"),
       (34498, "pub struct ReplayHost {",
        "turn [46]: `trace: Vec<EffectReceipt>` + `cursor: usize` — the only declaration "
        "that is both receipt-typed and unconditionally ordered")],
      "The determinism theorem's `HostTrace` parameter has no declaration of its own "
      "(T-83), so `ReplayHost` is the only frozen text that fixes what a host trace IS. "
      "It does so six times, in six mutually incompatible shapes, spanning turns [3] "
      "through [46] — `term/_structs.py` derives the same 6-decls/6-shapes split "
      "independently from the frozen text.",
      "The shapes are not stylistic variants: they disagree about whether replay is "
      "ORDER-SENSITIVE. The L24011 `HashMap<EffectId, EffectReceipt>` form resolves "
      "effects by identifier lookup, so a permuted effect sequence replays identically "
      "and the theorem's `HostTrace` input carries strictly less information than the "
      "live run did. L35218 and L38282 both assert flatly that `ReplayHost` is ordered, "
      "and L34911 lists `ReplayHost validates ordered ID + digest` as a satisfied "
      "checklist item — claims the L24011 declaration does not support. R-HOST-03 "
      "requires ordered consumption; four of the six declarations cannot satisfy it.",
      "REPORTED. No declaration is struck and none is promoted: U-35 must choose, and "
      "the audit recommends L34498's shape (`Vec<EffectReceipt>` + cursor) because it is "
      "the only one that is simultaneously receipt-typed, unconditionally ordered, and "
      "consistent with the ordered-replay claims made elsewhere in frozen text.",
      ["T-83", "T-84", "T-85"],
      previously=["C-99", "U-35"],
      decision_needed="Which `ReplayHost` declaration governs, and is replay "
                      "order-sensitive? If the L24011 HashMap form governs, the "
                      "effect-order-permutation test in the audit §6 must pass by "
                      "construction and DET-005 is unfixable without a shape change.",
      doc_sites=[("spec/06-contradictions-ambiguities.md", 114,
                  "| C-99 | `ReplayHost`", "C-99"),
                 ("spec/09-unresolved-decisions.md", 206,
                  "### U-35", "U-35 rules on the governing shape")],
    ),
]


COLLISIONS += [
    X("X-19", "The budget gate is named `BudgetOK`, `WithinBudget`, `BudgetAvailable`, `ReserveOK`, `ReleaseOK` with six signatures",
      "PREDICATE-SIGNATURE", "MAJOR",
      [(7035, "BudgetOK(c,\\Sigma)", "turn [13]: (command, configuration)"),
       (7151, "**$\\text{BudgetOK}$**: Verifies $C - \\text{cost}_{\\text{consumable}}(c) \\ge 0$",
        "turn [13] gives `BudgetOK`'s content"),
       (7334, "\\text{BudgetOK}(\\Delta C, \\Delta R, C, R)", "turn [13]: (ΔC, ΔR, C, R) — "
                                                              "a different arity"),
       (1788, "\\operatorname{WithinBudget}(e,B)", "turn [4]: (expression, budget)"),
       (6968, "WithinBudget(B,E)", "turn [12]: (budget, effect) — ARGUMENTS TRANSPOSED vs "
                                   "turn [4]"),
       (8820, "\\text{WithinBudget}(E, C, R, R_A)", "turn [16]: (effect, C, R, R_A)"),
       (8550, "WithinBudget(E,B,R_{A_c})", "turn [15]: (effect, B, R_Ac) — a fifth arity"),
       (23694, "\\text{BudgetAvailable}(E)", "turn [30]: `BudgetAvailable(E)` in the "
                                             "governing invariant"),
       (7525, "ReserveOK", "turn [15] correction: `ReserveOK(r,R) ⇔ R+r ≤ R_max`")],
      "The resource gate has three predicate NAMES (`BudgetOK`, `WithinBudget`, "
      "`BudgetAvailable`) plus two operation-specific names (`ReserveOK`, `ReleaseOK`), "
      "and at least six different signatures: `(c,Σ)`, `(ΔC,ΔR,C,R)`, `(e,B)`, `(B,E)`, "
      "`(E,C,R,R_A)`, `(E,B,R_{A_c})`, `(E)`. Turn [4] and turn [12] transpose the "
      "arguments of the same name.",
      "This is the gate that enforces `BUDGET-CONSUMPTION-CONSERVATION` and "
      "`BUDGET-ESCROW-CONSERVATION`, and a conjunct of the central theorem "
      "(`BudgetAvailable(E)`). C-07 records that one early form had the reservation "
      "direction WRONG; this collision records that the name and arity are not "
      "single-valued either, so an implementer cannot tell whether `BudgetAvailable(E)` "
      "is the same check as `WithinBudget(E,C,R,R_A)` or a weaker one that ignores the "
      "capability ceiling `R_A`.",
      "All names and signatures recorded; none renamed. The dictionary separates the "
      "concepts: the CONSUMABLE/RESERVED admissibility check (`ReserveOK`/`ReleaseOK`, "
      "frozen by the [15] correction), the DEADLINE check (`t + δ_t ≤ W`, N-18), the "
      "CAPABILITY CEILING check (`cost(E) ≤ R_A`, authority-owned), and the composite "
      "gate that the central theorem calls `BudgetAvailable(E)`. An explicit decision is "
      "required on the composite gate's signature.",
      ["T-24", "T-25", "T-26", "T-29"],
      ["C-07"], "Yes — freeze one name and signature for the composite budget gate and "
                "state its relation to `ReserveOK`, `ReleaseOK` and the `R_A` ceiling "
                "check. Affects R-BUDGET-03, R-CORE-02.", True),
    X("X-20", "`HostPolicy` is declared with two incompatible methods: `is_permitted(…) -> bool` and `authorize(…) -> Result<(), HostPolicyError>`",
      "METHOD-SIGNATURE", "MAJOR",
      [(10163, "pub trait HostPolicy {", "turn [18] declaration"),
       (10164, "fn is_permitted(&self, effect: &Effect) -> bool;", "turn [18] method: infallible bool"),
       (21893, "pub trait HostPolicy {", "turn [29] declaration"),
       (21894, "fn authorize(", "turn [29] method name"),
       (21897, ") -> Result<(), HostPolicyError>;", "turn [29] return type: fallible"),
       (8733, "\\text{HostPolicyOK}(E) \\quad \\text{// Gate 3: Host Policy}",
        "turn [15]: a third form — the mathematical predicate")],
      "One frozen trait name, two incompatible method signatures, plus a mathematical "
      "predicate for the same gate. `is_permitted(&Effect) -> bool` cannot distinguish "
      "'policy denies this' from 'the policy could not be evaluated'; `authorize(&Effect) "
      "-> Result<(), HostPolicyError>` can, and carries a typed error that the frozen "
      "`Fault::HostPolicyDenied(HostPolicyError)` variant requires.",
      "`Fault::HostPolicyDenied(HostPolicyError)` (L23811) is only constructible from the "
      "fallible form. An implementation of the `bool` form must synthesize a "
      "`HostPolicyError`, which is undefined anyway (U-14). Because differential testing "
      "compares faults (R-REF-05), the two forms produce different observations for the "
      "same denial — a divergence with no adjudication target.",
      "Both method names and both return types recorded; neither renamed. The dictionary "
      "notes that only the fallible form can satisfy `Fault::HostPolicyDenied(…)` and "
      "reports the choice as an open decision, joined to U-14 (error-variant "
      "enumeration). `HostPolicyOK(E)` is recorded as the mathematical name of the same "
      "gate, not a third API.",
      ["T-41", "T-16"],
      ["U-14", "AMB-08"], "Yes — freeze one `HostPolicy` method signature; blocked by "
                          "U-14 (`HostPolicyError` variants).", True),
    X("X-21", "`ActorStatus` is declared twice with incompatible variant payloads",
      "TYPE-HOMONYM", "MAJOR",
      [(9411, "pub enum ActorStatus {", "turn [17] declaration"),
       (9413, "Pending(PendingEffect),", "turn [17]: `Pending` is a TUPLE variant carrying "
                                         "a `PendingEffect`"),
       (9414, "Blocked(Continuation),", "turn [17]: `Blocked` CARRIES the continuation"),
       (23793, "pub enum ActorStatus {", "turn [30] declaration"),
       (23795, "Pending {", "turn [30]: `Pending` is a STRUCT variant"),
       (23798, "reservation: Reserved,", "turn [30]: `Pending` carries the RESERVATION"),
       (23800, "Blocked, // For Receive", "turn [30]: `Blocked` is a UNIT variant"),
       (23786, "the continuation remains safely in `actor.eval.continuation`",
        "turn [30] states WHERE the continuation lives instead")],
      "Two frozen declarations of one enum differ in variant KIND (tuple vs struct vs "
      "unit), in payload, and in the location of the continuation. Turn [17] puts the "
      "continuation inside `Blocked(Continuation)` and the pending effect inside "
      "`PendingEffect {id, effect, continuation}`; turn [30] makes `Blocked` a unit "
      "variant, moves the continuation to `actor.eval.continuation`, and puts a "
      "`reservation` inside `Pending`.",
      "The continuation's location determines what a snapshot must encode and what "
      "recovery must restore (R-PERSIST-04, R-RECOV-03) — and no canonical encoding is "
      "frozen for either (U-02). The `Pending` payload determines whether escrow can be "
      "reconstructed after a crash at T2/T3: turn [17]'s `Pending` carries no "
      "reservation, so an implementation using it cannot satisfy "
      "`BUDGET-ESCROW-CONSERVATION` across recovery. C-18/AMB-05 cover `ActorStatus` vs "
      "`RunState`; neither covers this split.",
      "Both declarations recorded verbatim; neither renamed and neither variant dropped. "
      "The dictionary marks the turn-[17] form superseded on the strength of the "
      "turn-[30] prose that explicitly relocates the continuation, and reports the "
      "reservation-payload difference as needing confirmation because it changes what "
      "recovery can restore.",
      ["T-35", "T-36", "T-32", "T-26"],
      ["C-18", "AMB-05"], "Yes — confirm the frozen `ActorStatus` variant payloads, in "
                          "particular that `Pending` carries `reservation`.", True),
    X("X-22", "`PendingEffect.id` vs `ActorStatus::Pending.effect_id`: two spellings of one field, and `continuation` vs `reservation`",
      "FIELD-SET", "MAJOR",
      [(9419, "pub struct PendingEffect {", "turn [17] struct declaration"),
       (9420, "pub id: EffectId,", "turn [17]: the field is `id`"),
       (9422, "pub continuation: Continuation,", "turn [17]: the payload includes the continuation"),
       (23796, "effect_id: EffectId,", "turn [30]: the same value is spelled `effect_id`"),
       (23798, "reservation: Reserved,", "turn [30]: the payload includes the reservation "
                                         "instead")],
      "The pending-effect payload exists in two frozen forms whose field NAMES differ "
      "(`id` vs `effect_id`) and whose third component differs in kind (`continuation: "
      "Continuation` vs `reservation: Reserved`). Elsewhere the frozen records use `id` "
      "consistently (`EffectRequest.id`, `EffectIssued.id`, `EffectReceipt.id`, all "
      "`WalRecord` variants), so `effect_id` is the odd spelling — and it is the one in "
      "the later declaration.",
      "Field names are protocol fields: they appear in canonical encodings, in "
      "counterexample artifacts, and in differential observations of faults. Two "
      "spellings for one value means two encodings, and `unmarshal(marshal(v)) = v` "
      "(R-MARSHAL-03) cannot hold across them. The payload difference is worse: a "
      "snapshot written from the turn-[17] form cannot restore escrow, and one written "
      "from the turn-[30] form cannot restore the continuation from the status alone.",
      "Both spellings recorded as frozen protocol fields; NEITHER is renamed. The "
      "dictionary requires that any encoding decision name the carrier explicitly and "
      "reports the inconsistency as part of X-21's decision. It notes, as evidence only, "
      "that `id` is the spelling used by every other frozen effect record.",
      ["T-35", "T-20", "T-32", "T-26"],
      [], "Yes — one spelling for the effect id field in the pending payload.", True),
    X("X-23", "`RunState::Faulted` vs `ActorStatus::Fault`: near-homonym variants of two distinct enums",
      "TYPE-HOMONYM", "MINOR",
      [(25532, "Faulted,", "turn [32]: the `RunState` variant is spelled `Faulted`"),
       (9416, "Fault(Fault),", "turn [17]: the `ActorStatus` variant is spelled `Fault` and "
                                "carries a `Fault`"),
       (23793, "pub enum ActorStatus {", "turn [30]: the enum whose fault variant is `Fault`"),
       (23806, "pub enum Fault {", "turn [30]: and `Fault` is ALSO the name of the payload type")],
      "Three related names differ by one suffix: `RunState::Faulted` (a scheduler-visible "
      "state), `ActorStatus::Fault` (a machine-visible state), and `Fault` (the taxonomy "
      "type carried by the latter). The source keeps all three, and C-18 records that the "
      "mapping between the two enums is 'implied but not stated as a table'.",
      "Faults are compared by the differential comparator (R-REF-05 lists faults among "
      "normalized observations). Without a stated mapping, production and reference may "
      "report the same condition as `RunState::Faulted` and `ActorStatus::Fault(f)` "
      "respectively and produce a divergence that adjudication cannot classify — it is "
      "neither a production nor a reference defect, but an unstated correspondence.",
      "All three names recorded exactly as spelled; none renamed and none unified. The "
      "dictionary requires prose to name the enum (`RunState::Faulted` vs "
      "`ActorStatus::Fault`) and reports the missing mapping table as part of C-18's "
      "residual, not as a new decision.",
      ["T-35", "T-36", "T-70"],
      ["C-18", "AMB-05"], "", True),
    X("X-24", "`ActorId` and `EffectId` are declared both as `pub type X = u64` and as `pub struct X(pub u64)`",
      "TYPE-HOMONYM", "MAJOR",
      [(9127, "pub type ActorId = u64;", "turn [17]: ALIAS form"),
       (9128, "pub type EffectId = u64;", "turn [17]: ALIAS form, same code block as `CapRef`"),
       (9342, "pub struct EffectId(pub u64);", "turn [17]: NEWTYPE form, later in the same turn"),
       (10669, "pub struct ActorId(pub u64);", "turn [18]: NEWTYPE form"),
       (23735, "pub struct EffectId(pub u64);", "turn [30]: NEWTYPE form, frozen era"),
       (33087, "## 3. Domain Types (Strict Payload Separation)", "turn [45]: 15A gives each "
                                                                 "id its own tag")],
      "Both identifier types exist in two incompatible forms — a type ALIAS (`pub type X = "
      "u64`) and a NEWTYPE (`pub struct X(pub u64)`) — and both forms appear inside turn "
      "[17]. An alias makes `ActorId` and `EffectId` the same type as each other and as "
      "`u64`; a newtype makes them three distinct nominal types.",
      "The frozen 15A tag set assigns `ActorId` tag `0x40` and `EffectId` tag `0x41`. A "
      "distinct tag per type is only expressible if the types are nominally distinct, so "
      "the alias form is inconsistent with the frozen wire format. Beyond encoding, the "
      "alias form permits passing an `EffectId` where an `ActorId` is expected — a "
      "confusion the effect protocol cannot survive, since `WalRecord::EffectCompleted` "
      "carries an id and a digest but no actor, and recovery keys on it.",
      "Both forms recorded; NEITHER renamed. The dictionary reports the alias form as "
      "inconsistent with the frozen 15A tag assignment — evidence, not a decision — and "
      "leaves the choice to an explicit addendum. `LogicalTime` and the digest newtypes "
      "are declared only as newtypes, so the inconsistency is confined to the two id types.",
      ["T-20", "T-34", "T-62", "T-18", "T-47"],
      [], "Yes — confirm the newtype form for `ActorId`/`EffectId` (required by 15A tags "
          "`0x40`/`0x41`).", True),
    X("X-25", "`CapRef` is declared as `CapRef(pub(crate) u64)` and as `CapRef { index: u32, generation: u32 }`",
      "FIELD-SET", "MAJOR",
      [(915, "pub struct CapRef(pub(crate) u64);", "turn [3]: single-integer form"),
       (3646, "pub struct CapRef(pub(crate) u64);", "turn [7]: same form"),
       (5949, "pub struct CapRef(pub(crate) u64);", "turn [10]: same form"),
       (5966, "pub struct CapRef {", "turn [10]: generational form appears in the SAME turn"),
       (9131, "pub struct CapRef {", "turn [17]: frozen generational form"),
       (9146, "`CapRef` fields remain private. There should be no public constructor from arbitrary integers.",
        "turn [17] states the privacy requirement")],
      "`CapRef` has two frozen-era shapes: a single opaque `u64` and a generational "
      "`{index: u32, generation: u32}` pair. Both appear in turn [10]; the generational "
      "form is the one carried forward and the one 15A encodes under tag `0x30`.",
      "The generational form is what makes revocation and reuse safe: a stale reference "
      "to a recycled slot fails on generation mismatch. A single `u64` cannot express "
      "that, so `CAP-REVOCATION-ANCESTOR` and mutation M005 ('accepting revoked "
      "capabilities') are not testable against the single-integer form. The privacy "
      "requirement at L9145 also differs in force: the single-integer form's field is "
      "`pub(crate)`, which is not 'no public constructor from arbitrary integers'.",
      "Both shapes recorded verbatim; neither renamed. The dictionary marks the "
      "single-`u64` form superseded (it cannot express generational reuse, which the "
      "frozen revocation obligations require) and states that as evidence rather than as "
      "an editorial choice. spec/05 §1 gives only the generational form and does not "
      "record that the other ever existed.",
      ["T-09", "T-10"],
      [], "", True),
    X("X-26", "`Effect` is declared ten times with five different field sets, and its capability reference disappears and returns under a new name",
      "FIELD-SET", "MAJOR",
      [(1166, "pub struct Effect {", "turn [3] declaration"),
       (1167, "pub kind: EffectKind,", "turn [3]: field `kind`, not `op`"),
       (1169, "pub cap_ref: CapRef,", "turn [3]: the effect CARRIES a capability reference"),
       (6541, "pub struct Effect {", "turn [11] declaration"),
       (6545, "pub cost: ResourceUsage, // Static cost of this specific effect",
        "turn [11]: the cost field's type is `ResourceUsage`"),
       (9297, "pub struct Effect {", "turn [17] declaration — the frozen form"),
       (9301, "pub cost: Cost,", "turn [17]: the cost field's type is `Cost`"),
       (3637, "pub struct Effect {",
         "turn [7]: a FOURTH declaration — `params: Vec<u8>`, `resources`, no `cost`"),
       (3640, "pub params: Vec<u8>,",
         "turn [7]: raw bytes, where turn [11] says `params: Params`"),
       (5025, "pub struct Effect {",
         "turn [9]: identical to the turn-[7] form"),
       (21372, "pub struct Effect {",
         "turn [29]: a FIFTH form — `capability`, `operation`, `params: Params`, `cost: EffectCost`"),
       (21373, "pub capability: CapRef,",
         "turn [29]: the capability reference RETURNS, under a new field name"),
       (21374, "pub operation: Op,",
         "turn [29]: `op` renamed `operation`"),
       (23272, "pub struct Effect {",
         "turn [30]: the same fifth form"),
       (23276, "pub params: Params, // Canonicalized, normalized parameters",
         "turn [30]: the comment fixes the reading"),
      ],
      "Three frozen-era declarations of `Effect` disagree on both fields and field types: "
      "`{kind: EffectKind, cap_ref: CapRef, target}` (turn [3]); `{op, target, params, "
      "cost: ResourceUsage}` (turn [11]); `{op, target, params, cost: Cost}` (turn [17], "
      "carried unchanged into turn [18]). The turn-[3] form has no `op`, no `params`, no "
      "`cost`, and DOES have a capability reference.",
      "`EffectDigest = SHA-256(canonical_bytes(effect))` is the semantic identity used to "
      "validate every receipt and every journal record. Which fields are in the hashed "
      "bytes decides what the digest commits to. Including `cap_ref` (turn [3]) binds the "
      "digest to a `CapRef`, so the same effect requested through a different capability "
      "would digest differently and replay would fail; excluding it (frozen) makes the "
      "digest a pure function of the effect description. The `ResourceUsage`/`Cost` "
      "rename additionally changes the hashed field's type name."
      " A full sweep finds TEN declarations in FIVE field sets, not three in three. Two further sets "
      "sit between the ones recorded here: `{op, target, params: Vec<u8>, resources}` at L3637 "
      "(turn [7]) and L5025 (turn [9]) — raw parameter bytes and a `resources` field, with no `cost` "
      "at all; and `{capability: CapRef, operation: Op, target, params: Params, cost: EffectCost}` at "
      "L21372 (turn [29]), L23272 and L23748 (turn [30]). The turn-[29] form returns the capability "
      "reference that only the turn-[3] form had, under a new field name (`capability` for `cap_ref`), "
      "and renames `op` to `operation`. So `params` is `Vec<u8>` in turns [7] and [9] and `Params` "
      "from turn [11]; `cost` is `ResourceUsage` in turn [11], `Cost` in turns [17]-[18] and "
      "`EffectCost` from turn [29] (X-44).",
      "All three field sets recorded verbatim; no field renamed and none silently dropped. "
      "The frozen form (L9297) is the current definition; the other two are marked "
      "superseded with their exact shapes preserved. The digest-semantics consequence of "
      "the `cap_ref` difference is stated explicitly because it is a security property, "
      "not a naming preference.",
      ["T-16", "T-21", "T-22", "T-09"],
      [], "", True),
    X("X-27", "`EffectRequest` is declared three times; the frozen form drops the `cap: CapRef` field",
      "FIELD-SET", "MAJOR",
      [(1447, "pub struct EffectRequest {", "turn [4] declaration"),
       (1449, "pub cap: CapRef,", "turn [4]: `{id, cap}` — NO effect field"),
       (9314, "pub struct EffectRequest {", "turn [17] declaration"),
       (9317, "pub cap: CapRef,", "turn [17]: `{id, effect, cap}`"),
       (10325, "pub cap: CapRef,", "turn [18]: `{id, effect, cap}`"),
       (23758, "pub struct EffectRequest {", "turn [30] declaration — the frozen form"),
       (23756, "// Transient message to the host adapter", "turn [30] states its role")],
      "The host-bound message has three frozen-era shapes: `{id, cap}` (turn [4], with no "
      "effect at all), `{id, effect, cap}` (turns [17]-[18]), and `{id, effect}` (turn "
      "[30], frozen). The `cap: CapRef` field is present in the first two and absent from "
      "the frozen form.",
      "The dropped field is a security decision, not a typo: the frozen form sends the "
      "host adapter an effect description and an id, and no capability reference. That is "
      "consistent with R-TRUST-03 (no hidden authority; the host is partially trusted) "
      "and with `CapRef ⇏ AuthorityInspection` (gate property 2). An implementation built "
      "from the turn-[17] shape leaks a `CapRef` across the host boundary, and one built "
      "from the turn-[4] shape sends no effect at all. The turn-[4] shape also makes "
      "`EffectDigest` uncomputable at the boundary.",
      "All three shapes recorded verbatim; no field renamed. The frozen form is the "
      "current definition; the `cap` field is listed as superseded WITH the observation "
      "that its removal is what keeps authority off the host boundary, so a future "
      "addendum re-adding it would be a security-relevant change requiring explicit "
      "justification.",
      ["T-17", "T-16", "T-09"],
      [], "", True),
    X("X-28", "`Block` is declared as `Block(pub Vec<Value>)` and as `Block { forms: Vec<Form> }`",
      "FIELD-SET", "MAJOR",
      [(855, "pub struct Block(pub Vec<Value>);", "turn [3]: tuple struct over `Value`"),
       (13484, "pub struct Block {", "turn [21] declaration"),
       (13485, "pub forms: Vec<Form>,", "turn [21]: named field over `Form`")],
      "The untrusted input type has two declarations with different element types: "
      "`Vec<Value>` (turn [3]) and `Vec<Form>` (turn [21]). `Form` is never declared "
      "anywhere in the source, and `Value` is itself a colliding name with two "
      "incompatible domains (X-45).",
      "`Block` is the domain of the parser and the subject of `Block ≠ ExecutablePlan` "
      "(N-01) and of the first security gate `Block ⇏ ExecutablePlan`. Its element type "
      "decides what the parser accepts and therefore what the LLM may emit. `Vec<Value>` "
      "means a block is a sequence of machine values (so a block can contain a "
      "`Value::Capability`); `Vec<Form>` means a block is a sequence of syntactic forms "
      "of an undeclared type. The two give different answers to whether a raw capability "
      "can appear in untrusted input.",
      "Both declarations recorded verbatim; neither renamed. `Form` is reported as an "
      "undefined type (X-29) rather than being given an invented definition. The "
      "dictionary notes the security consequence of the element-type difference and "
      "requires an explicit decision.",
      ["T-01", "T-31", "T-03"],
      [], "Yes — freeze `Block`'s element type (`Value` or `Form`) and declare `Form` if "
          "it is retained. Affects R-COMPILE-02 and the first security gate.", True),
    X("X-29", "Names used as field types, stage names and AST nodes that are never declared",
      "UNDEFINED-TYPE", "MAJOR",
      [(864, "pub struct ParsedBlock { ast: NormalizedAST }", "`NormalizedAST`: 2 occurrences, no declaration"),
       (39271, "NormalizedAST", "`NormalizedAST` as a pipeline stage name"),
       (13485, "pub forms: Vec<Form>,", "`Form`: used as `Block`'s element type, no declaration"),
       (27160, "pub events: Vec<GlobalEvent>,", "`GlobalEvent`: no declaration"),
       (27162, "pub available_capabilities: CapabilitySummary,", "`CapabilitySummary`: no declaration"),
       (27163, "pub budget: BudgetSummary,", "`BudgetSummary`: no declaration"),
       (36171, "pub terminal_states: Vec<ObservedActor>,", "`ObservedActor` and the six "
                                                           "other `Observed*` types: no declarations"),
       (25989, "Expr::Delegate {", "turn [32]: an AST NODE used in a match sketch and in the "
                                   "delegation proof table, but no `pub enum Expr` (L12145, "
                                   "L14030, L14413, L20295, L20702) declares it"),
       (26058, "Authority can only cross boundaries via `Expr::Delegate`",
        "turn [32]: Theorem 2's proof — site added by the X-70 sweep"),
       (26078, "| **C: Delegation** | `Expr::Delegate` |",
        "turn [32]: property-test matrix row C — site added by the X-70 sweep")],
      "`NormalizedAST`, `Form`, `GlobalEvent`, `CapabilitySummary`, `BudgetSummary` and "
      "the seven `Observed*` element types are all used in frozen declarations and none "
      "is declared anywhere in the source. `PlanIR` (X-30) is a seventh: it is used with "
      "variants but never declared as an enum. `Expr::Delegate` is an eighth, and the only "
      "AST-level case: it is named in the delegation proof table and a match sketch, but "
      "none of the five `pub enum Expr` declarations contains it — the same fact AMB-11 "
      "registers from the ambiguity side."
      " The sweep of every struct and enum FIELD position (`python3 term/_structs.py --undeclared`) "
      "finds 69 type names used as field or variant-payload types with no declaration anywhere: the "
      "thirteen recorded here and in X-30, four `std`/external-crate names written unqualified, "
      "twenty-one named in some other existing entry or decision, and THIRTY-ONE recorded nowhere in "
      "the repository — among them the reference model's entire vocabulary (`RefExpr`, `RefOp`, "
      "`RefScope`, `RefConstraint`, `RefResources`, `RefLifetime`, `RefFunction`, `RefEvent`, "
      "`RefHeap`, `RefMessage`, `RefCapabilityContext`, `RefRecoveryFault`) and the authority layer's "
      "`AuthorityId`, `RevocationState` and `OsAuthority`. Those thirty-one are enumerated in X-84 "
      "rather than repeated here.",
      "Three of these block obligations directly. `NormalizedAST`/`PlanIR` are the "
      "compiler's stage contents (R-COMPILE-02/03). `CapabilitySummary`/`BudgetSummary` "
      "define exactly how much machine state the untrusted planner may see — the "
      "sanitization boundary of R-PLANNER-01 and of the gated-reflection design — so "
      "leaving them undeclared leaves the LLM boundary's information flow unspecified. "
      "The `Observed*` types define the differential comparison domain (R-REF-05), so "
      "leaving them undeclared leaves the oracle's shape unspecified.",
      "Every undefined name is recorded as a term entry or in this collision with its "
      "usage sites, and NONE is given an invented definition — filling a gap by "
      "invention is exactly what R-SCOPE-03 prohibits. Each is reported as requiring an "
      "explicit declaration. This extends the U-02 family (machine-state encodings) to "
      "names that have no declaration at all, which U-02 does not list.",
      ["T-07", "T-01", "T-54", "T-57", "T-03", "T-15"],
      ["U-02"], "Yes — declare `NormalizedAST`, `Form`, `GlobalEvent`, `CapabilitySummary`, "
                "`BudgetSummary`, and the seven `Observed*` types (or retract the fields "
                "that use them).", True),
    X("X-30", "`PlanIR` is used with variants but never declared, and its variants use two superseded names",
      "UNDEFINED-TYPE", "MAJOR",
      [(865, "pub struct ValidatedPlan { ir: PlanIR, effects: EffectSet }",
        "turn [3]: `PlanIR` as a field type"),
       (986, "EvaluateSequence { remaining: Vec<PlanIR> },", "turn [3]: `PlanIR` inside a "
                                                             "continuation frame"),
       (1037, "PlanIR::Value(v) => StepResult::Halt(v), // Rule 3", "turn [3]: variant `Value`"),
       (1039, "PlanIR::Invoke { func, args, cap } => {", "turn [3]: variant `Invoke` — the "
                                                         "superseded surface name (C-17)"),
       (1051, "PlanIR::Spawn { plan, trust_level } => {", "turn [3]: variant `Spawn` with "
                                                          "`trust_level` — the retracted "
                                                          "isolation field (U-05)"),
       (13603, "PlanIR", "turn [21]: `PlanIR` as a pipeline STAGE"),
       (39973, "ir: PlanIR,", "turn [58]: `PlanIR` as `ExecutablePlan`'s payload type")],
      "`PlanIR` is never declared as an enum, yet it is used with at least three variants "
      "(`Value`, `Invoke`, `Spawn`) and as the payload type of `ExecutablePlan` in the "
      "turn-[58] bootstrap pack. Two of its three visible variants use names the frozen "
      "text supersedes: `Invoke` (the frozen constructor is `Expr::Request`, C-17) and "
      "`trust_level` (the frozen `Expr::Spawn` has no isolation field, U-05).",
      "This is the type that X-03 would make the runtime evaluate if the turn-[58] "
      "`ExecutablePlan { ir: PlanIR }` declaration were taken as governing. It has no "
      "declaration, no closed variant set, and its known variants reference a retracted "
      "surface. Building M2 (pure CEK) on it is impossible without inventing its "
      "definition, which R-SCOPE-03 prohibits.",
      "All usage sites recorded; the name is not renamed and no variant set is invented. "
      "The dictionary reports `PlanIR` as undefined and notes that its only visible "
      "variants are superseded forms of `Expr::Value`, `Expr::Request` and `Expr::Spawn`, "
      "which is evidence about its intended role but not a definition. Joined to the X-03 "
      "decision.",
      ["T-08", "T-06", "T-30"],
      ["C-17", "U-05", "AMB-25"], "Yes — declare `PlanIR` or state that `Expr` is the "
                                  "lowered representation. Blocks X-03's resolution.", True),
]


COLLISIONS += [
    X("X-31", "The durable log has five names, and a sixth name denotes a different in-memory object",
      "SCOPE-DRIFT", "MAJOR",
      [(27716, "strict Write-Ahead Log (WAL) ordering", "turn [34]: 'Write-Ahead Log (WAL)' — the definition"),
       (27706, "// 6. Serialize event_log length (actual events are in the WAL)",
        "turn [34]: the WAL is where the events actually live"),
       (26133, "- \\(L\\) = append-only durable event log after that snapshot,",
        "turn [33]: the same object called `L`"),
       (28427, "CommittedSnapshot + DurableLog + EffectJournal",
        "turn [36]: the same object called `DurableLog` in a boxed theorem"),
       (25539, "pub event_log: EventLog,",
        "turn [32]: `EventLog` — the IN-MEMORY log, a different object"),
       (35099, "pub struct WalFrame {", "turn [47]: the frozen durable framing type"),
       (1086, "pub struct EventLog {",
         "turn [3]: the in-memory log's declaration"),
       (1088, "events: Vec<TransitionEvent>,",
         "turn [3]: its element type is `TransitionEvent`"),
       (10905, "pub struct EventLog {",
         "turn [18]: re-declared"),
       (10906, "events: Vec<LogEntry>,",
         "turn [18]: element type is now `LogEntry` — a different declared type"),
      ],
      "One durable structure is named `WAL`, `Write-Ahead Log`, `L`, `DurableLog` and "
      "'append-only durable event log' across turns [33]-[58]; and `EventLog` — which "
      "sounds like a synonym — is the in-memory log whose LENGTH is snapshotted because "
      "its contents are in the WAL. Two of the five names appear inside boxed theorems.",
      "N-19 (`WAL ≠ EventLog`) is the durability law behind `HostInvoked(E) ⇒ "
      "DurableIssued(E)`. If `EventLog` is read as the WAL, an in-memory append "
      "satisfies the durability invariant and crash point T2 becomes survivable in a test "
      "while being fatal in production. The alias spread is what makes that misreading "
      "available: four of the five names are prose, and only `WalFrame`/`WalRecord` are "
      "typed."
      " The log's ELEMENT type drifts with its names: `EventLog` is `{ events: Vec<TransitionEvent> }` "
      "at L1088 (turn [3]) and `{ events: Vec<LogEntry> }` at L10906 (turn [18]). Both element types "
      "are declared, so this is not an undefined-name problem (X-29, X-84) but a change of record "
      "type: `TransitionEvent` is the machine's transition record — whose variant "
      "`TransitionEvent::ActorSpawned` is used 37 lines before its own declaration (X-75) — while "
      "`LogEntry` is a name that appears nowhere else in the specification of the log's contents.",
      "All five names recorded; none renamed. The dictionary fixes `WAL` as canonical "
      "prose for the durable structure, lists `L` and `DurableLog` as frozen symbols "
      "that denote it (retained in quotations), and lists `EventLog` as a DISTINCT term "
      "(T-49) whose confusion with the WAL is forbidden. U-16/AMB-14 (the "
      "`EventSequence`/`WalSequence` relationship) is the related open decision.",
      ["T-45", "T-49", "T-46", "T-47"],
      ["U-16", "AMB-14"], "", True),
    X("X-32", "`EffectJournal`: a separate durable structure, a superseded enum, and WAL record kinds — and a boxed theorem that counts it as a third component",
      "SCOPE-DRIFT", "MAJOR",
      [(26134, "- \\(H\\) = durable host-effect journal.", "turn [33]: the journal as `H` in `D = ⟨S,L,H⟩`"),
       (26216, "Introduce a durable effect journal separate from the ordinary machine event log:",
        "turn [33]: 'separate from' — a distinct durable structure"),
       (26222, "pub enum EffectJournalEntry {", "turn [33]: its own enum, unprefixed variants"),
       (28427, "CommittedSnapshot + DurableLog + EffectJournal",
        "turn [36]: BOXED recovery theorem naming THREE durable components"),
       (35127, "pub enum WalRecord {", "turn [47]: 15B — the journal's records are WAL kinds"),
       (35143, "A digest mismatch is `EffectJournalCorruption`, not a different effect.",
        "turn [47]: the journal name survives as a fault name inside the unified model")],
      "The journal's ontological status changes: a separate durable structure with its "
      "own enum (turn [33]), a first-class component of a boxed recovery theorem (turn "
      "[36]), and — in the frozen 15B model — a family of `WalRecord` kinds with no "
      "separate structure (turn [47]). The name survives the unification in "
      "`EffectJournalCorruption`, so the frozen text uses 'journal' for something that no "
      "longer has its own storage.",
      "`Recover(D) = Replay(S,L,H)` is stated over three components; 15B gives recovery "
      "two durable inputs (snapshot + WAL). R-RECOV-01/03 are written against the "
      "three-component form. An implementer must decide whether `H` is a separate file "
      "(two logs to order and fsync, and a crash point between them that T0-T6 does not "
      "enumerate) or a projection of the WAL (no separate ordering, but then `Replay` "
      "takes two arguments). C-25 records the unification as MINOR "
      "'resolved-by-later-text' and does not cite the boxed theorem, which is the site "
      "where the three-component reading is normative.",
      "All three statuses recorded verbatim; no name renamed and no structure invented. "
      "The dictionary states N-20 (`WAL ≠ EffectJournal` as structures, journal = record "
      "taxonomy) as the reading consistent with 15B, and reports that the boxed theorem "
      "at L28427/L28577 still counts three components — extending C-25 rather than "
      "contradicting it.",
      ["T-23", "T-45", "T-47", "T-52", "T-18"],
      ["C-25"], "Yes — restate `Recover(D)` against the unified 15B model, or confirm "
                "that `H` remains a separate durable structure with its own ordering and "
                "crash points.", True),
    X("X-33", "`Snapshot` denotes a persistence concept, `GlobalSnapshot` a type, and `EnvironmentSnapshot` an unrelated closure capture",
      "TYPE-HOMONYM", "MAJOR",
      [(26132, "- \\(S\\) = persisted `GlobalState` snapshot,", "turn [33]: the concept, symbol `S`"),
       (26301, "pub struct GlobalSnapshot {", "turn [33]: the frozen persistence type"),
       (12357, "pub env: EnvironmentSnapshot,", "turn [21]: an UNRELATED type — a closure's "
                                                 "captured environment"),
       (12356, "pub body: Box<Expr>,", "turn [21]: `FunctionValue { params, body, env }` — the "
                                       "only use of `EnvironmentSnapshot`"),
       (35133, "SnapshotCommit { event_sequence: EventSequence, snapshot_version: SnapshotVersion, state_digest: StateDigest },",
        "turn [47]: the commit record kind"),
       (26410, "CommittedSnapshot(S)", "turn [33]: the integrity predicate")],
      "The word 'Snapshot' names four distinct things: the durable state image concept "
      "(`S`), the frozen type `GlobalSnapshot`, the commit record `SnapshotCommit`, and "
      "`EnvironmentSnapshot` — a closure-environment capture that has nothing to do with "
      "persistence and is declared exactly once, as the type of `FunctionValue.env`, "
      "without ever being defined.",
      "`FunctionValue` must be encoded in snapshots for closures to survive recovery "
      "(U-02 lists `FunctionValue` among the types without a canonical encoding), and its "
      "`env` field's type is `EnvironmentSnapshot` — a name that reads as a persistence "
      "artifact. An implementer could reasonably encode a nested `GlobalSnapshot` there, "
      "or search the persistence module for a type that lives in the calculus. The "
      "undefined-ness compounds X-29.",
      "All four uses recorded; no name renamed. The dictionary separates them as: "
      "`Snapshot` (concept, T-48), `GlobalSnapshot` (frozen type), `SnapshotCommit` "
      "(record kind), and `EnvironmentSnapshot` (undefined calculus type, listed in "
      "X-29). Prose MUST NOT use 'snapshot' unqualified where the closure capture is "
      "meant.",
      ["T-48", "T-31", "T-47", "T-33"],
      ["U-02"], "", True),
    X("X-34", "The plan family: `Plan`, `PlanProposal`, `PlanIR`, `ExecutablePlan` overlap — and AMB-25 adds a fifth name that does not exist",
      "SCOPE-DRIFT", "MAJOR",
      [(551, "### The really interesting primitive: `Plan`", "turn [2]: `Plan` as the "
                                                            "fundamental primitive"),
       (561, "Block", "turn [2]: the pipeline that replaced the `Plan` primitive"),
       (27175, "pub struct PlanProposal {", "turn [33]: the planner's output"),
       (865, "pub struct ValidatedPlan { ir: PlanIR, effects: EffectSet }", "turn [3]: `PlanIR`"),
       (27122, "PlanIR", "turn [33]: `PlanIR` still current in the frozen-era architecture diagram"),
       (869, "pub struct ExecutablePlan {", "turn [3]: the machine's input")],
      "Five plan-family names are used with overlapping meanings across the transcript: "
      "`Plan` (the turn-[2] 'really interesting primitive', later obsolete), "
      "`PlanProposal` (planner output), `PlanIR` (an undeclared intermediate, still "
      "appearing in a turn-[33] architecture diagram), and `ExecutablePlan` (machine "
      "input) — plus `ValidatedPlan`/`CapabilityCheckedPlan`/`ParsedBlock` as stages. "
      "AMB-25 records this overlap and adds `PlannerState`, which occurs NOWHERE in "
      "`Red-on-Rust.md` (see X-60).",
      "The overlap is what makes X-01 and X-04 possible: if 'plan' has no fixed "
      "denotation, then `ValidatedPlan(P)` cannot be pinned to a stage or to the final "
      "artifact, and `PlanIR` can appear as a stage, a field type, and `ExecutablePlan`'s "
      "payload (X-03) without contradiction being noticed. `Plan` as a primitive is "
      "obsolete but never retracted, so a reader of turn [2] alone gets a different "
      "architecture.",
      "All names recorded; none renamed. The dictionary marks `Plan` (turn [2]) obsolete "
      "per spec/05 §1 and requires that prose always use the full stage name. AMB-25 is "
      "linked and its phantom `PlannerState` reported separately (X-60) rather than "
      "silently corrected.",
      ["T-02", "T-06", "T-08", "T-04"],
      ["AMB-25"], "", True),
    X("X-35", "`Expr::Request` is declared with two different field sets",
      "FIELD-SET", "MAJOR",
      [(10420, "Expr::Request { cap, args } => {", "turn [18]: fields `cap`, `args`"),
       (12183, "Request {", "turn [21]: the frozen AST constructor"),
       (12184, "capability: Box<Expr>,", "turn [21]: field `capability`, an EXPRESSION"),
       (12185, "operation: Op,", "turn [21]: field `operation`"),
       (12186, "target: TargetExpr,", "turn [21]: field `target`"),
       (12187, "params: Vec<Expr>,", "turn [21]: field `params`"),
       (14039, "Request { capability: Box<Expr>, operation: Op, target: TargetExpr, params: Vec<Expr> },",
        "turn [22]: the frozen field set restated")],
      "The effect-request constructor has two frozen-era field sets: `{cap, args}` (turn "
      "[18]) and `{capability, operation, target, params}` (turns [21]-[22], the frozen "
      "AST). The difference is not cosmetic: `cap` in the early form is a bound "
      "capability, while `capability: Box<Expr>` in the frozen form is an EXPRESSION that "
      "must be evaluated — which is why the 16-step request sequence has separate steps "
      "for capability evaluation, target evaluation and argument evaluation.",
      "The frozen 16-step sequence (R-EFFECT-03) evaluates capability, target and "
      "arguments as three separate ordered steps and short-circuits on the first failure "
      "(R-EFFECT-04: five assertions per gate). With `{cap, args}` there is no target "
      "expression to evaluate and no ordering to test, so `CEK-CALL-ARGS-LTR` and the "
      "gate short-circuit obligations cannot be expressed. `args` vs `params` is also a "
      "protocol-field rename inside a frozen AST.",
      "Both field sets recorded verbatim; neither renamed. The frozen form (turns "
      "[21]-[22], twice) is current; the `{cap, args}` form is marked superseded with its "
      "shape preserved. The dictionary notes that `args`/`params` are different spellings "
      "of the same role and that `Expr::Call` uses `args` while `Expr::Request` uses "
      "`params` in the SAME frozen declaration — so the inconsistency is internal to the "
      "frozen AST, not only across eras.",
      ["T-30", "T-17", "T-16"],
      ["C-17"], "", True),
    X("X-36", "Capability liveness and coverage are named three ways each, with different arguments",
      "PREDICATE-SIGNATURE", "MAJOR",
      [(6301, "Valid(c,t)", "turn [10]: `Valid(c,t)` — reference and time"),
       (5934, "\\neg Valid(c)", "turn [9]: `Valid(c)` — one argument"),
       (2006, "$$\\frac{\\neg\\,\\text{live}(\\kappa(c))}", "turn [5]: `live(κ(c))` — lowercase, "
                                                            "takes the AUTHORITY"),
       (2254, "\\text{valid}(\\kappa(c))", "turn [5]: `valid(κ(c))` — lowercase, takes the "
                                            "AUTHORITY"),
       (2254, "\\text{covers}(\\kappa(c),\\; E.\\text{target})", "turn [5]: `covers` takes the "
                                                                  "authority and the TARGET"),
       (4501, "\\operatorname{Covers}(Authority(c),E,t)", "turn [8]: `Covers` takes the "
                                                           "authority, the EFFECT and time"),
       (3626, "pub fn covers(&self, effect: &Effect) -> bool {", "turn [7]: the Rust method "
                                                                 "takes the whole effect")],
      "Two kernel decisions each have three names and several arities. Liveness: "
      "`Valid(c,t)` / `Valid(c)` / `valid(κ(c))` / `live(κ(c))`. Coverage: "
      "`covers(κ(c), E.target)` / `Covers(Authority(c), E, t)` / `fn covers(&self, "
      "&Effect) -> bool`. The arguments differ in KIND as well as number: some take the "
      "`CapRef`, some the `Authority` behind it, and coverage is checked against the "
      "target in one form and the whole effect in another.",
      "Whether the argument is `c` or `κ(c)` is exactly the N-03 boundary (`CapRef ≠ "
      "Authority`): a liveness predicate over `c` can be evaluated by the machine, while "
      "one over `κ(c)` requires the kernel to resolve authority first. Whether coverage "
      "is checked against `E.target` or against `E` decides whether `params` and `cost` "
      "are inside the authorization decision — which changes what `EffectDigest` must "
      "commit to and whether a parameter-constraint (`Q`) violation is a coverage failure "
      "at all.",
      "All names and signatures recorded; none renamed. The dictionary requires prose to "
      "name the predicate with its argument list, and records that the frozen transition "
      "rules use `Valid(c,t)` (turn [15] onward) while the algebra uses "
      "`valid`/`live`/`covers` over `κ(c)` (turns [5]-[8]). An explicit decision is "
      "needed on the coverage argument, since it determines the scope of the `Q` "
      "component.",
      ["T-09", "T-10", "T-13", "T-16"],
      [], "Yes — freeze one liveness and one coverage predicate signature, and state "
          "whether coverage is checked against `E.target` or the whole `E`.", True),
    X("X-37", "`Authority` is declared seven times in six field sets, `Frame` eleven times in five variant sets, and `AuthorityNode` three times",
      "TYPE-HOMONYM", "MINOR",
      [(488, "struct Authority {", "turn [2] declaration"),
       (918, "pub(crate) struct Authority {", "turn [3] declaration"),
       (3591, "pub struct Authority {", "turn [7] declaration"),
       (6501, "pub struct Authority<S, Q, R, L> {", "turn [11] declaration — the generic form"),
       (12453, "pub enum Frame {", "turn [21]: first of eleven `Frame` declarations"),
       (23830, "pub enum Frame {", "turn [30]: the frozen-era `Frame` declaration"),
       (39373, "pub(crate) struct AuthorityNode { ... }", "turn [58]: fields ELIDED"),
       (9702, "pub(crate) struct AuthorityNode {",
         "turn [17]: `AuthorityNode` WITH four fields — not elided"),
       (9705, "generation: u32,",
         "turn [17]: the field `RuntimeAuthority` (L3649, L5037) lacks"),
       (39940, "pub struct AuthorityNode { ... }",
         "turn [58]: elided, and `pub` — the form the prose below forbids"),
       (39945, "must NOT be public.",
         "turn [58]: the rule the L39940 code block contradicts"),
       (4360, "pub struct Authority {",
         "turn [8]: a declaration this entry's count of seven includes but whose site is not listed"),
       (4979, "pub struct Authority {",
         "turn [9]: the same shape as L3591, restated"),
       (5368, "pub struct Authority {",
         "turn [9]: the merged form — five fields plus `id` and `parent`"),
      ],
      "The authority type is declared seven times across turns [2]-[11] (v0.1 → v0.2 → "
      "v0.3 of the capability algebra), the continuation frame enum eleven times across "
      "turns [21]-[30], and the kernel-private `AuthorityNode` once with its fields "
      "elided. AMB-26 records the eleven `Frame` declarations and the "
      "`Authority`/`AuthorityNode`/`CapabilityKernel` interchange; the seven `Authority` "
      "declarations are not enumerated anywhere.",
      "A closed variant set is a requirement, not a preference: R-CEK-03 freezes the "
      "frame set, and eleven declarations give eleven candidate sets. The differential "
      "comparator observes faults and continuations, so two implementations choosing "
      "different declarations among the eleven would diverge without either being wrong. "
      "`AuthorityNode`'s elided fields mean the kernel's private state has no frozen "
      "shape at all, which U-02 needs in order to freeze a canonical encoding."
      " Two corrections and one extension, from the declaration sweep now re-derivable with "
      "`python3 term/_structs.py`. (a) `AuthorityNode` is declared THREE times, not once, and is not "
      "always elided: L9702 (turn [17]) gives it four fields — `authority: Authority`, "
      "`parent: Option<CapRef>`, `generation: u32`, `live: bool` — i.e. exactly `RuntimeAuthority` "
      "(L3649, L5037) plus `generation`, which makes three names for the kernel's arena entry (X-77, "
      "X-82); L39373 and L39940 (both turn [58]) are the elided pair, and L39940 shows `pub struct "
      "AuthorityNode { ... }` immediately above the prose 'must NOT be public' (L39945), so that code "
      "block exhibits the forbidden form. (b) The seven `Authority` declarations are L488, L918, "
      "L3591, L4360, L4979, L5368 and L6501 — this entry's site list names four of them — and they "
      "carry SIX distinct field sets, filed as X-77. (c) The eleven `Frame` declarations carry FIVE "
      "distinct non-elided variant sets, filed as X-86. The counts recorded here are confirmed by the "
      "checker; the divergences behind them are filed separately rather than restated in this entry.",
      "All declaration sites recorded; none renamed and none deleted. The dictionary "
      "points at the algebra version that governs (v0.2, turn [11], per spec/05 §1) and "
      "requires an explicit decision identifying WHICH of the eleven `Frame` declarations "
      "is the frozen set. AMB-26 is linked, not duplicated.",
      ["T-10", "T-11", "T-13", "T-33", "T-14"],
      ["AMB-26", "U-02"], "Yes — identify the single frozen `Frame` declaration and state "
                          "`AuthorityNode`'s fields (or confirm they are deliberately "
                          "kernel-private and unencodable).", True),
    X(xid="X-38",
      title="Capability denial carries NINE names across eras (C-08 reports four), host-policy denial two, and two variants have split payload types",
      kind="TYPE-HOMONYM",
      severity="MAJOR",
      sites=[
        (1949, "**Faults:**", "turn [5]: the v1 fault GRAMMAR — `CapViolation | BudgetExhausted | ScopeViolation | Revoked | HostFault | IsolationBreach`"),
        (133, "CapabilityViolation", "turn [1]: 'returns a structured `CapabilityViolation` error *as data*'"),
        (937, "return Err(Fault::CapabilityRevoked(cref));", "turn [3]: `CapabilityRevoked` carrying a `CapRef`"),
        (3667, "CapabilityRevoked", "turn [7]: `CapabilityRevoked` with NO payload"),
        (944, "return Err(Fault::ScopeViolation(cref, target.clone()));", "turn [3]: `ScopeViolation` — no later counterpart"),
        (7374, "AuthorizationFailed", "turn [13]: the v0.3 denial rule (C-08 cites L7435 for this name — X-59)"),
        (8721, "Fault}(\\text{CapabilityRevoked", "turn [14]: v0.3 `E-AttenuateDenied` concludes `Fault(CapabilityRevoked)`"),
        (8758, "`CapabilityViolation`, `BudgetExhausted`, or `HostPolicyViolation`", "turn [14]: v0.3 `E-RequestDenied` names the denial faults ONE LINE outside the range AMB-08 cites (L8748-8757)"),
        (20389, "let fault = Fault::CapabilityError(error);", "turn [28]: the variant is named `CapabilityError` here"),
        (20790, "let fault = Fault::CapabilityError(error);", "turn [28]: the same construction, restated"),
        (20538, "Outcome::Fault(Fault::CapabilityError(", "turn [28]: a PROPERTY TEST asserts on the pre-rename variant name"),
        (22430, "Capability(CapabilityError),", "turn [29]: RENAMED to `Capability` — `CapabilityError` never retracted"),
        (23808, "Capability(CapabilityError),", "turn [30]: the frozen form"),
        (26870, "CapabilityDenied,", "turn [33]: a NINTH name, in the actor-local `Fault` declared AFTER the frozen one"),
        (10885, "HostPolicyViolation,", "turn [18]: a SECOND variant name for host-policy denial"),
        (10480, "Fault::HostPolicyViolation", "turn [18]: used where later turns use `HostPolicyDenied`"),
        (22436, "HostPolicyDenied(HostPolicyError),", "turn [29]: host-policy denial with a STRUCTURED payload"),
        (23323, "HostPolicyDenied(String),", "turn [30]: the same variant with an UNSTRUCTURED `String` payload"),
        (23813, "Host(HostFault),", "turn [30]: the frozen `Fault` variant whose payload is `HostFault` (T-74)"),
        (21897, ") -> Result<(), HostPolicyError>;", "turn [29]: the payload's error type — never declared as an enum"),
      ],
      statement=(
        "The capability-denial outcome is named **nine** different ways across the 60 turns: "
        "`CapViolation` (v1 grammar L1949), `CapabilityViolation` (L133, L1042, v0.3 L8758), "
        "`Revoked` (v1 grammar L1949), `CapabilityRevoked` (L937 *with* a `CapRef` payload, "
        "L3667 *without*, v0.3 L8721), `ScopeViolation` (L944, L1949 — no later counterpart), "
        "`AuthorizationFailed` (L7374), `Fault::CapabilityError(…)` (L20389, L20790, asserted "
        "by a property test at L20538), the frozen `Fault::Capability(CapabilityError)` "
        "(L22430 turn [29], L23808 turn [30]), and `CapabilityDenied` (L26870, in the "
        "turn-[33] actor-local `Fault` declared *after* the frozen one). The rename "
        "`CapabilityError` → `Capability` between turns [28] and [29] is never retracted. The "
        "host-policy outcome is named `HostPolicyDenied` and `HostPolicyViolation`, and "
        "`HostPolicyDenied` itself carries two payload types across two frozen-era "
        "declarations: `HostPolicyError` (L22436 turn [29]; L23811 turn [30]) and `String` "
        "(L23323, turn [30]). `Fault` is declared seven times (L10882, L17788, L18125, L22415, "
        "L23319, L23806, L26865)."),
      why_it_matters=(
        "Faults are part of the normalized observation domain (R-REF-05), so two "
        "implementations choosing different declarations produce a differential divergence "
        "with no defect on either side. `HostPolicyDenied(String)` vs "
        "`HostPolicyDenied(HostPolicyError)` is not a naming difference: a `String` payload "
        "cannot be matched exhaustively and has no canonical encoding, while `HostPolicyError` "
        "is never declared as an enum at all (U-14). The turn-[28]→[29] rename is load-bearing "
        "in a way pure naming is not: L20538 is a property test asserting "
        "`Fault::CapabilityError(CapabilityError::Revoked)`, so an implementation that follows "
        "the frozen L23808 name fails a test the source itself states. C-08 reports 'four "
        "names'; U-08/AMB-08 add `IsolationBreach`, which is the *receipt-mismatch* fault "
        "(L2024, L7223, L8766) and not a denial at all. None reports `CapViolation`, "
        "`Revoked`, `Fault::CapabilityError`, `CapabilityDenied`, the payload-type split, or "
        "the seven declarations."),
      disposition=(
        "All nine denial names, both host-policy names, both payload types and all seven "
        "declaration sites are recorded verbatim in T-70/T-41/T-72; nothing is renamed and no "
        "declaration is deleted. The dictionary raises C-08's count from four to nine, "
        "annotates C-08 in place, and requires the U-08 decision to fix names AND payload types "
        "AND to state which of the seven declarations governs. C-08's own line citations are "
        "wrong (X-59), which is why the spread could not previously be audited from the "
        "register. Severity raised MINOR → MAJOR: the L20538 property test asserts a superseded "
        "variant name, so this is not cosmetic."),
      affects=["T-70", "T-72", "T-41", "T-09", "T-10", "T-35"],
      previously=["C-08", "U-08", "U-14", "AMB-08"],
      decision_needed="Yes — U-08 must fix variant names AND payload types, identify which of the seven `Fault` declarations governs, and resolve the L20538 test that asserts the pre-rename `Fault::CapabilityError`.",
      new_finding=True,
      doc_sites=[
        ("spec/06-contradictions-ambiguities.md", 22, "Nine names for the same denial outcome, not four", "C-08's description, corrected in place on this pass; it previously read \"Four names for the same denial outcome\" and its severity cell was MINOR"),
        ("spec/09-unresolved-decisions.md", 56, "denial outcome is named", "U-08 lists four names; the verified count is nine"),
      ]),
]


COLLISIONS += [
    X("X-39", "spec/05 defines `Effect` with a `capability` field that no frozen declaration has",
      "ALIAS-DEFECT", "MAJOR",
      [(9297, "pub struct Effect {", "the frozen declaration: `{op, target, params, cost}` — "
                                     "no capability field"),
       (1169, "pub cap_ref: CapRef,", "the only declaration with a capability field is the "
                                      "superseded turn-[3] form"),
       (23738, "pub struct EffectDigest(pub [u8; 32]);", "the digest is over the effect's "
                                                          "canonical bytes")],
      "The glossary of record gives `Effect` as `{capability, operation, target, params, "
      "cost}`. No declaration in 42,312 lines has that field set. The frozen form "
      "(L9297, repeated at L10309 and L10792) is `{op, target, params, cost}`; the only "
      "form with a capability field is the superseded turn-[3] `{kind, cap_ref, target}`, "
      "which has neither `operation` nor `params`. The glossary row is a hybrid of a "
      "superseded shape and the frozen one, and it also renames `op` to `operation`.",
      "`EffectDigest = SHA-256(canonical_bytes(effect))` and every receipt, journal "
      "record and replay comparison keys on it. A glossary that puts `capability` inside "
      "`Effect` tells an implementer to hash a `CapRef` into the digest — so the same "
      "effect requested through a different capability would produce a different digest, "
      "replay would fail on a valid trace, and `EFFECT-RECEIPT-DIGEST-VALIDATION` would "
      "be unsatisfiable. Renaming `op` to `operation` additionally collides with "
      "`Expr::Request.operation`, which is a DIFFERENT field of a different type.",
      "The glossary row is corrected in this pass to the frozen field set, with the "
      "correction recorded here rather than applied silently: `Effect = {op, target, "
      "params, cost}` (L9297), and `operation` is `Expr::Request.operation`, not an "
      "`Effect` field. No source identifier is renamed — the frozen field names are "
      "restored to the glossary.",
      ["T-16", "T-21", "T-30"],
      [], "", True,
      [("spec/05-terminology.md", 14, "{capability, operation, target, params, cost}",
        "the defective field list, corrected by this dictionary")]),
    X("X-40", "spec/05 and mod/02 treat `ValidatedPlan`, `CapabilityCheckedPlan` and `PlanIR` as aliases of `ExecutablePlan`",
      "ALIAS-DEFECT", "MAJOR",
      [(865, "pub struct ValidatedPlan { ir: PlanIR, effects: EffectSet }",
        "a declared stage TYPE with its own fields"),
       (866, "pub struct CapabilityCheckedPlan { ir: PlanIR, required_caps: CapSet }",
        "a declared stage TYPE with its own fields"),
       (869, "pub struct ExecutablePlan {", "the final artifact — different fields again")],
      "The glossary lists `ValidatedPlan`, `CapabilityCheckedPlan` and `PlanIR` in the "
      "'Aliases observed in source' column for `ExecutablePlan` and resolves them as "
      "'stage names'. mod/02 repeats the claim more strongly: stage names are 'not "
      "artifacts in their own right'. But two of the three ARE declared artifacts with "
      "their own fields, private to `mod compiler`, and `ValidatedPlan` is additionally a "
      "predicate in the central theorem (X-01). Calling them aliases of the final "
      "artifact states that they denote the same object, which is false on the source's "
      "own declarations.",
      "This is the alias-rule form of the conflation N-01/N-02/N-11/N-12 exist to prevent. "
      "An implementer following the glossary would treat a `ValidatedPlan` as an "
      "`ExecutablePlan` and admit an artifact that has passed effect annotation only — "
      "skipping capability analysis (`κ_req ⪯ κ_ambient`) and resource bounding "
      "(`bounds: ResourceBounds`) — into the machine. That defeats `Block ≠ "
      "ExecutablePlan` from the inside, with the glossary as authority.",
      "The alias column is corrected: `ValidatedPlan` (T-04) and `CapabilityCheckedPlan` "
      "(T-05) are distinct TERMS with their own entries, not aliases; `PlanIR` (T-08) is "
      "an undeclared IR name, not an alias; `NormalizedAST` (T-07) likewise. The only "
      "genuine obsolete alias recorded is `Plan` (turn [2]). No identifier is renamed. "
      "mod/02's NON-NORMATIVE-CONTENT bullet is corrected to point at this finding.",
      ["T-04", "T-05", "T-06", "T-08", "T-07"],
      [], "", True,
      [("spec/05-terminology.md", 13, "are **stage names**",
        "the alias resolution that conflates three declared stage types with the final artifact"),
       ("mod/02-compiler.md", 52, "not artifacts in their own right",
        "the same claim propagated into the module layer")]),
    X("X-41", "spec/01 and mod/02 reproduce one of three pipeline orderings, in an order the frozen structs contradict",
      "ALIAS-DEFECT", "MINOR",
      [(864, "pub struct ParsedBlock { ast: NormalizedAST }", "`NormalizedAST` is a FIELD of "
                                                              "stage 1, not a stage before it"),
       (865, "pub struct ValidatedPlan { ir: PlanIR, effects: EffectSet }",
        "`PlanIR` is a FIELD of stage 2, not a stage after it"),
       (39271, "NormalizedAST", "the turn-[58] ordering this rendering follows")],
      "The canonicalized crate contract renders the pipeline as `Block → parse → "
      "NormalizedAST → ValidatedPlan → PlanIR → capability analysis → resource analysis → "
      "ExecutablePlan`, faithfully following the turn-[58] diagram. That ordering places "
      "`NormalizedAST` before `ValidatedPlan` and `PlanIR` after it, whereas the frozen "
      "struct declarations make `NormalizedAST` the CONTENT of `ParsedBlock` and `PlanIR` "
      "the CONTENT of `ValidatedPlan`. It also omits two declared stages and is silent "
      "about the two other orderings (X-02).",
      "The rendering is faithful to one source site, so it is not an error of "
      "transcription — but as the only pipeline statement in the canonical "
      "specification it presents one of three contradictory orderings as settled, and "
      "inverts the type/field relationship of two names. An implementer reading spec/01 "
      "and mod/02 alone would build four stages where the structs declare four different "
      "ones.",
      "The rendering is left in place (it is faithful to L39265-39280 and removing it "
      "would silently drop source text); this entry records that it is one of three "
      "orderings, that two names in it are field types rather than stages, and that the "
      "collision is X-02. Both spec/01 and mod/02 are annotated with a pointer to X-02 "
      "rather than edited.",
      ["T-03", "T-04", "T-06", "T-07", "T-08"],
      [], "", True,
      [("spec/01-canonical-specification.md", 494, "Block → parse → NormalizedAST",
        "the single-ordering rendering"),
       ("mod/02-compiler.md", 45, "Block → parse → NormalizedAST",
        "the same rendering repeated in the module layer")]),
    X("X-42", "`LogicalTime` is glossed in the source as 'a logical clock or deterministic timestamp'",
      "SCOPE-DRIFT", "MINOR",
      [(6437, "It is an explicit component of the machine state $\\Sigma$ (e.g., a logical clock or deterministic timestamp)",
        "turn [10]: three names for one object in one sentence"),
       (9137, "pub struct LogicalTime(pub u64);", "turn [17]: the frozen type"),
       (5829, "logical time", "turn [9]: the frozen prose name")],
      "The frozen type is `LogicalTime(pub u64)` and the frozen symbol is `t`, but the "
      "source glosses the same object as 'a logical clock' and 'a deterministic "
      "timestamp' in the sentence that establishes it is not host-fetched. spec/05 §2 "
      "lists both glosses as aliases.",
      "'Clock' implies a device that can be read, which is precisely what R-CAP-09 "
      "prohibits: logical time is a state component advanced by `δ_t`, never read from "
      "the host. 'Timestamp' implies wall-clock provenance. Both aliases invite the "
      "prohibited reading, and 'wall-clock time as semantic machine state' is one of the "
      "sixteen prohibited shortcuts (R-CLAIM-02).",
      "The glosses are recorded as forbidden PROSE substitutes (they are not identifiers, "
      "so nothing is renamed): canonical prose is 'logical time' or `LogicalTime`. The "
      "source sentence is quoted verbatim wherever it is cited, with its provenance, so "
      "the glosses remain traceable.",
      ["T-28", "T-27"],
      [], "", True),
    X("X-43", "`ReplayHost` has six declarations in six field sets: the trace field carries three names and four element types",
      "FIELD-SET", "MAJOR",
      [(24011, "pub struct ReplayHost {", "turn [30]: the `HashMap` form"),
       (24012, "pub recorded_receipts: HashMap<EffectId, EffectReceipt>,",
        "turn [30]: field `recorded_receipts`, keyed by id"),
       (34498, "pub struct ReplayHost {", "turn [46]: the frozen ordered form"),
       (34499, "trace: Vec<EffectReceipt>,", "turn [46]: field `trace`, ordered"),
       (1234, "pub struct ReplayHost {",
         "turn [3]: a THIRD field — `cursor: usize`"),
       (1237, "trace: Vec<Result<Value, HostFault>>,",
         "turn [3]: the trace holds RESULTS, not receipts"),
       (9783, "pub struct ReplayHost {",
         "turn [17]: `trace: ReplayTrace` — a type declared nowhere (X-84)"),
       (10541, "pub struct ReplayHost {",
         "turn [18]: `trace: VecDeque<EffectReceipt>` — a deque, and `cursor` gone"),
       (22339, "pub struct ReplayHost {",
         "turn [29]: `receipts: ReceiptLog` — a THIRD field name, its type declared nowhere (X-84)"),
      ],
      "C-22 resolves the mechanism (unordered map → ordered trace) but the field NAME "
      "also changes, from `recorded_receipts: HashMap<EffectId, EffectReceipt>` to "
      "`trace: Vec<EffectReceipt>`. The rename is not cosmetic: a map keyed by `EffectId` "
      "makes id lookup the primitive operation, while a vector makes POSITION the "
      "primitive, which is what allows the digest check to detect a divergent program "
      "consuming receipts out of order."
      " The sweep behind X-83/X-86 finds SIX declarations in SIX field sets, not two. Before the pair "
      "recorded here: `{cursor: usize, trace: Vec<Result<Value, HostFault>>}` at L1234 (turn [3]), "
      "where the trace holds RESULTS rather than receipts; `{trace: ReplayTrace}` at L9783 (turn [17]) "
      "and `{trace: VecDeque<EffectReceipt>}` at L10541 (turn [18]), both single-field and both "
      "without `cursor`; and `{receipts: ReceiptLog}` at L22339 (turn [29]), a third field name whose "
      "type is declared nowhere. The field is `trace` in four declarations and `receipts` / "
      "`recorded_receipts` in two; its element type is `Result<Value, HostFault>`, `ReplayTrace`, "
      "`EffectReceipt` (in a `VecDeque`, a `Vec`, and a `HashMap` keyed by `EffectId`) and "
      "`ReceiptLog`; and `cursor` is present in three declarations and absent from three. Severity is "
      "raised from MINOR: the map-versus-vector question recorded here is one instance of a six-way "
      "divergence in the replay host's only state.",
      "The ordered form's whole point is that the next receipt is a function of position, "
      "not of the requested id — 'a corrupted or divergent program could issue a "
      "different effect and simply consume the next recorded result' (L1390) is the "
      "failure the id-keyed form permits. Keeping the `recorded_receipts` name would "
      "carry the keyed-lookup mental model into an ordered implementation.",
      "Both field names recorded verbatim; neither renamed. C-22 is linked as the "
      "mechanism resolution; this entry adds the field-name change and states why the "
      "ordered field's name matters to the security property.",
      ["T-42", "T-19", "T-20"],
      ["C-22"], "", True),
    X("X-44", "Three cost types and five cost functions: `Cost`, `EffectCost`, `ResourceUsage`, `CostModel`, `cost_C`/`cost_io`/`cost_res`",
      "TYPE-HOMONYM", "MINOR",
      [(9188, "pub struct Cost {", "turn [17]: `Cost { consumable, reserved }` — `Effect.cost`"),
       (6545, "pub cost: ResourceUsage, // Static cost of this specific effect",
        "turn [11]: the same field's type named `ResourceUsage`"),
       (21390, "pub struct EffectCost {", "turn [29]: the split issue/complete/reserve model"),
       (10168, "pub trait CostModel {", "turn [18]: the op→cost mapping contract"),
       (8707, "C' = C - \\text{cost}_C(\\text{let})", "turn [15]: `cost_C`, the consumable cost function"),
       (7381, "C - \\text{cost}_{\\text{io}}(\\text{receipt}.v), R - \\text{cost}_{\\text{res}}(E)",
        "turn [13]: `cost_io` and `cost_res`, two more cost functions")],
      "Cost is expressed by three type names (`Cost`, `ResourceUsage`, `EffectCost`), one "
      "trait (`CostModel` with `cost_c`/`cost_r`) and at least three mathematical "
      "functions (`cost_C`, `cost_io`, `cost_res`) plus `cost_consumable`/`cost_reserved` "
      "(L7151). `Cost` and `ResourceUsage` name the same field type in different eras; "
      "`Cost` and `EffectCost` are different types with overlapping purpose; and the "
      "math functions are subscripted inconsistently (`cost_C` vs `cost_c`).",
      "`R-BUDGET-07` freezes `CostModel` + `Cost` as the op→cost contract, while "
      "`R-EFFECT-05` freezes `EffectCost` as the split lifecycle model. An implementer "
      "must know which one an effect carries: `Effect.cost` is a `Cost`, not an "
      "`EffectCost`, so escrowing `complete_max` requires a second lookup that the type "
      "names do not make obvious. AMB-23 records `EffectCost`'s field-order ambiguity; "
      "the three-type spread is not recorded.",
      "All names recorded; none renamed. The dictionary separates them by role: `Cost` "
      "= the static consumable/reserved pair carried by `Effect`; `EffectCost` = the "
      "lifecycle split (issue/complete_max/reserve); `ResourceUsage` = superseded name of "
      "`Cost`; `CostModel` = the mapping contract; the `cost_*` symbols = per-transition "
      "cost functions in the operational rules.",
      ["T-22", "T-29", "T-16", "T-24", "T-25", "T-26"],
      ["AMB-23"], "", True),
    X("X-45", "Two incompatible `Value` domains share one name",
      "TYPE-HOMONYM", "MAJOR",
      [(12283, "pub enum Value {", "turn [21]: the MACHINE domain (11 variants)"),
       (13969, "pub enum Value {", "turn [22]: re-declared"),
       (33164, "pub enum Value {", "turn [45]: the 15A CANONICAL domain (8 variants, "
                                    "including `Map`)"),
       (33167, "List(Vec<Value>), Map(BTreeMap<Symbol, Value>),", "turn [45]: `Map` is not a "
                                                                   "machine variant")],
      "The machine `Value` (11 variants including `Bytes`, `Tuple`, `Function`, `Actor`) "
      "and the 15A canonical `Value` (8 variants including `Map`) share a name with "
      "incompatible variant sets. `marshal`/`unmarshal` and the round-trip law "
      "`unmarshal(marshal(v)) = v` are stated for 'all pure values' without saying which "
      "domain.",
      "This is the largest open naming decision in the specification and it blocks "
      "R-MARSHAL-03: a round-trip law cannot hold across two domains whose variant sets "
      "differ in both directions. It also decides what a snapshot can encode, since "
      "`Value::Function` and `Value::Actor` are machine-only and `Value::Map` is "
      "canonical-only.",
      "Recorded as-is; NEITHER domain renamed, because U-09 is the open decision that "
      "must choose (spec/05 §7 and req/03 AMB-21 both defer to it). This entry restates "
      "the collision so the dictionary is complete and links the upstream registers "
      "rather than duplicating their analysis.",
      ["T-31", "T-39", "T-62", "T-48"],
      ["C-03", "C-45", "U-09", "AMB-21"], "Yes — U-09: name and relate the two value "
                                          "domains.", False),
    X("X-46", "`GlobalState` vs `GlobalConfig`",
      "TYPE-HOMONYM", "MINOR",
      [(8653, "## 1. Global Configuration and State Definitions", "turn [15]: 'Global Configuration'"),
       (11061, "fn step_request(actor: &mut ActorState, machine: &mut GlobalConfig, expr: Expr)",
        "turn [18]: the Rust name `GlobalConfig`"),
       (24156, "pub struct GlobalState {", "turn [31]: the frozen Rust name `GlobalState`"),
       (10128, "**`GlobalConfig`, `ActorState`, `Budget`, `CapabilityKernel`, `Effect`, `EventLog`",
        "turn [18]: `GlobalConfig` listed as a first-milestone artifact"),
       (9496, "pub actors: ActorTable,",
         "turn [17]: `GlobalConfig` holds an `ActorTable`"),
       (10376, "pub actors: std::collections::HashMap<ActorId, ActorState>,",
         "turn [18]: the abstraction is inlined as a `HashMap`"),
       (10930, "pub actors: ActorTable,",
         "turn [18]: and returns to `ActorTable` in the SAME turn"),
       (24157, "pub actors: BTreeMap<ActorId, ActorState>,",
         "turn [31]: `GlobalState` uses a THIRD container for the same map"),
      ],
      "The global machine record is `GlobalConfig` in the v0.3/turn-[15]-[18] era and "
      "`GlobalState` from turn [31] on. C-42 records this as MINOR "
      "resolved-by-later-text and spec/05 §6.3 makes `GlobalState` canonical.",
      "Resolved, but it is retained here because the superseded name appears in a "
      "milestone artifact list (L10128) that an implementer follows for M0, and because "
      "`GlobalConfig`'s shape is the 6-component v0.3 configuration (X-18) rather than "
      "the frozen `GlobalState` shape — so the name change carries a shape change that "
      "C-42 does not mention."
      " The two names also disagree with themselves about the actor table's type: `GlobalConfig.actors` "
      "is `ActorTable` at L9496 (turn [17]), `std::collections::HashMap<ActorId, ActorState>` at "
      "L10376 (turn [18]) and `ActorTable` again at L10930 — the same turn as the inlined form. Turn "
      "[31] then gives `GlobalState.actors: BTreeMap<ActorId, ActorState>` (L24157), a THIRD container "
      "for the same map, so the actor table is an abstraction, a `HashMap` and a `BTreeMap` in three "
      "places. Which container governs decides iteration order, and therefore the determinism that "
      "the scheduler's FIFO rule (R-ACTOR-04) and X-83's `members` field both assume.",
      "`GlobalState` canonical (per C-42 and spec/05 §6.3); `GlobalConfig` recorded as "
      "superseded and forbidden in current prose, retained in quotations. Neither is "
      "renamed. The associated shape change is cross-referenced to X-18.",
      ["T-38"],
      ["C-42"], "", False),
    X("X-47", "`EventSequence` and `WalSequence` are separate newtypes with no stated relationship, and a third name `EffectSequence` is declared nowhere",
      "TYPE-HOMONYM", "MAJOR",
      [(31697, "pub struct EventSequence(pub u64);", "turn [43]: the in-memory event sequence"),
       (33868, "pub struct WalSequence(pub u64);", "turn [46]: the durable WAL sequence"),
       (35119, "pub struct WalSequence(pub u64);", "turn [47]: restated, 'strictly monotonic'"),
       (35133, "SnapshotCommit { event_sequence: EventSequence, snapshot_version: SnapshotVersion, state_digest: StateDigest },",
        "turn [47]: a WAL record that carries an `EventSequence`, not a `WalSequence`"),
       (26301, "pub struct GlobalSnapshot {",
         "turn [33]: the snapshot carries BOTH sequence fields"),
       (26305, "pub last_effect_sequence: EffectSequence,",
         "turn [33]: `EffectSequence` — declared nowhere (X-84)"),
       (34126, "pub last_effect_sequence: EffectSequence,",
         "turn [46]: the same undeclared name, thirteen turns later"),
      ],
      "Two `u64` newtypes sequence the in-memory event log and the durable WAL, and the "
      "frozen `WalRecord::SnapshotCommit` carries an `EventSequence` INSIDE a record that "
      "has its own `WalSequence` in its frame. Whether one is a projection of the other, "
      "or they advance independently, is never stated."
      " `GlobalSnapshot` carries a THIRD sequence name beside the two recorded here: "
      "`last_effect_sequence: EffectSequence` at L26305 (turn [33]) and again at L34126 (turn [46]), "
      "in the same struct as `last_event_sequence: EventSequence`. `EffectSequence` is declared "
      "nowhere in the source (X-84) and differs from the declared `EventSequence` by one letter, so "
      "the frozen snapshot type either names a third sequence domain — an effect sequence distinct "
      "from both the event sequence and the WAL sequence — or misspells the first. Nothing in the "
      "text says which, and a snapshot that records two sequence numbers whose relationship is "
      "unstated cannot be validated on recovery.",
      "The WAL gap check `s_{n+1} = s_n + 1` is a conformance obligation "
      "(WAL-SEQUENCE-CONTINUITY, WAL-GAP-REJECT). If effect records and event records "
      "consume the same sequence, a single total order satisfies it; if they do not, the "
      "gap check must be applied per kind and `SnapshotCommit`'s embedded `EventSequence` "
      "needs its own continuity rule. Recovery ordering (R-RECOV-03) depends on the "
      "answer.",
      "Both types recorded; neither renamed nor merged. U-16/AMB-14 is the open decision; "
      "this entry adds the concrete evidence that a WAL record embeds an `EventSequence`, "
      "which constrains the answer (a single total order is the reading consistent with "
      "the frozen gap-check rule).",
      ["T-49", "T-45", "T-46", "T-47"],
      ["U-16", "AMB-14"], "Yes — U-16.", False),
    X("X-48", "'Reference machine' (pre-15C) and 'reference model' (15C) denote different objects",
      "SCOPE-DRIFT", "MINOR",
      [(10128, "Once that reference machine passes the algebraic/property tests",
        "turn [18]: 'reference machine' = the FIRST boring production milestone"),
       (15871, "Keep the reference machine maximally obvious.", "turn [23]: same sense"),
       (16403, "The reference machine must remain maximally transparent", "turn [24]: same sense"),
       (35283, "Phase 15C defines an independently implemented executable reference model",
        "turn [48]: 'reference model' = the INDEPENDENT oracle, zero shared logic")],
      "Before Phase 15C, 'the reference machine' means the first deliberately boring "
      "implementation of the production semantics — the thing the live host is later "
      "bolted onto. From 15C on, 'the reference model' means the INDEPENDENT comparator "
      "that must share zero core transition logic with production. The two are opposite "
      "in the one respect that matters: the first is the production baseline, the second "
      "must not be.",
      "R-SCOPE-04 requires zero shared core logic between production and reference. An "
      "implementer who reads 'reference machine' in the turn-[18]-[24] sense and treats "
      "that artifact as the 15C oracle gets a tautological differential test — the exact "
      "oracle-collapse the 15C.38 anti-oracle-collapse rules prohibit. C-33 covers a "
      "related point (the reference 'distinct language' suggestion) but not this sense "
      "shift.",
      "Both senses recorded with their eras; neither phrase renamed. The dictionary fixes "
      "`ReferenceModel` (T-58) as the canonical name for the 15C independent oracle and "
      "marks 'reference machine' as superseded prose for the first production milestone, "
      "quotable only with its turn provenance.",
      ["T-58", "T-65"],
      ["C-33"], "", True),
    X("X-49", "Three identifier namespaces begin with `M`: milestones `M0`-`M11`, mutations `M001`-`M018`, and the memory symbol `M`",
      "SYMBOL-OVERLOAD", "MINOR",
      [(40763, "## M0 — Workspace", "turn [58]: milestone identifiers `M0`…`M11`"),
       (38477, "M001 reverse argument evaluation", "turn [54]: mutation identifiers `M001`…`M018`"),
       (7131, "$R = \\langle M, S \\rangle$", "turn [13]: `M` = memory bytes"),
       (658, "(B_0,\\kappa_0,F_0,M_0)", "turn [2]: `M_0` = a replay-tuple component")],
      "`M0` is a milestone, `M001` is a mutation, `M` is the memory dimension of "
      "Reserved, and `M_0` is a component of the turn-[2] replay tuple. spec/00 §3 "
      "registers `M-NN` and `M0NN` as separate identifier schemes, which is the correct "
      "disambiguation, but the mathematical `M` is not covered by that scheme.",
      "The practical hazard is in verification text: 'M0 gate' and 'M001 kill' can appear "
      "in the same sentence as a budget statement about `M`, and the mutation registry "
      "ID `M007` (budget escrow) is precisely a mutation about the budget that `M` "
      "denotes a component of.",
      "All three namespaces recorded; none renamed — `M0NN` and `M-NN` are frozen "
      "identifier schemes and `M` is a frozen mathematical symbol. The dictionary "
      "requires the full form in prose ('milestone M0', 'mutation M001', 'the memory "
      "dimension M') and notes that spec/00 §3 already separates the two ID schemes.",
      ["T-26", "T-60"],
      [], "", True),
    X("X-50", "The canonical envelope is specified with two field names, two tag widths and two endiannesses",
      "FIELD-SET", "BLOCKING",
      [(28298, "/// [format_version: u8] [type_tag: u32 LE] [length: u32 LE] [payload: ...]",
        "turn [36]: `format_version`, `type_tag: u32 LE`, `length: u32 LE`"),
       (29540, "version:u8", "turn [40]: `version`, and `type_tag:u8`, `payload_length:u32_be`"),
       (29905, "payload_length: u32 BE", "turn [41]: big-endian length"),
       (33816, "version | type_tag | payload_length | payload", "turn [46]: the frozen field "
                                                                "sequence"),
       (35102, "pub payload_length: u32,        // Big-endian, checked",
        "turn [47]: `WalFrame` uses the same big-endian length"),
       (38150, "payload_length: u32 BE", "turn [54] master prompt: the frozen form restated")],
      "The `CanonicalSerialize` trait's own doc comment specifies the wire format as "
      "`[format_version: u8] [type_tag: u32 LE] [length: u32 LE] [payload]`, while every "
      "later statement — the 15A grammar, the 15B frame, and the turn-[54] master prompt "
      "— specifies `version: u8 | type_tag: u8 | payload_length: u32 BE | payload`. The "
      "two differ in a field NAME (`format_version`/`length` vs `version`/"
      "`payload_length`), the tag WIDTH (`u32` vs `u8`) and the ENDIANNESS (`LE` vs `BE`).",
      "This is the byte-level foundation of every digest and checksum in the system: "
      "`EffectDigest`, `StateDigest`, `ResultDigest`, the WAL frame checksum and snapshot "
      "determinism (R-PERSIST-05) all hash canonical bytes. An encoder built from the "
      "trait doc comment produces bytes that differ from the frozen format in the first "
      "six bytes of every object, so no digest would match, no golden vector would "
      "verify, and differential persistence testing (15C.34) would diverge on every case. "
      "The defect sits in an API contract comment, which is where an implementer looks "
      "first. It is not covered by C-02 (which concerns stale PRIMITIVE tags in §1.3).",
      "Both specifications recorded verbatim; NO field is renamed and the superseded "
      "comment is not deleted from the record. The dictionary states the frozen form "
      "(L38147-38150, L33816) as canonical on the latest-frozen-text rule and flags the "
      "trait doc comment at L28298 as contradicting it — an explicit decision is required "
      "because the contradiction is inside an API contract, not in narrative prose. "
      "Blocks milestone M1 (canonical serialization).",
      ["T-62", "T-63", "T-21", "T-46"],
      ["C-02"], "Yes — correct or retract the `CanonicalSerialize` doc-comment format at "
                "L28298; it contradicts the frozen 15A/15B envelope. Blocks M1.", True),
    X("X-51", "spec/05's trait list omits `CanonicalSerialize`, the trait that carries the format",
      "ALIAS-DEFECT", "MINOR",
      [(27685, "pub trait CanonicalSerialize {", "turn [34]: the persistence-era trait"),
       (28296, "pub trait CanonicalSerialize {", "turn [36]: re-declared, with the L28298 "
                                                 "doc comment"),
       (29979, "pub trait CanonicalPayload: Sized {", "turn [41]: the frozen 15A trait"),
       (29178, "pub trait CanonicalEncode {", "turn [40]: the frozen encode half"),
       (29183, "pub trait CanonicalDecode: Sized {", "turn [40]: the frozen decode half"),
       (27061, "D_S=H(CanonicalSerialize(GlobalState)).", "turn [33]: `CanonicalSerialize` "
                                                           "used as a MATH FUNCTION symbol")],
      "The glossary row for canonical encoding lists the traits as `CanonicalPayload` / "
      "`CanonicalEncode` / `CanonicalDecode` and puts `CanonicalSerialize` only in the "
      "row's canonical-term position, without recording that it is a separately declared "
      "trait (twice) whose doc comment is the site of the X-50 format collision, and that "
      "it also appears as a mathematical function symbol in the state-digest formula.",
      "`CanonicalSerialize` is infallible (`-> Vec<u8>`) while the frozen "
      "`CanonicalEncode`/`CanonicalDecode` pair is fallible (`Result<_, CanonicalError>`). "
      "R-CANON-02 and the strict-decoding rejection classes (R-PERSIST-02) are only "
      "expressible with the fallible pair, so which trait family is frozen decides whether "
      "decode failures are representable at all. The source's own checklist notes "
      "`CanonicalDecode` 'is declared but not implemented' (L29601).",
      "All four trait names recorded, plus the math-function use; none renamed. The "
      "dictionary separates the infallible serialization trait (turn-[34]/[36] era, "
      "carrier of the X-50 defect) from the frozen fallible codec pair, and corrects the "
      "glossary row to list all four with their eras.",
      ["T-63", "T-62", "T-48"],
      [], "", True,
      [("spec/05-terminology.md", 62, "Traits: `CanonicalPayload` / `CanonicalEncode` / `CanonicalDecode`",
        "the incomplete trait list")]),
    X("X-52", "'FROZEN' is applied to four different objects, and the README applies it to a fifth",
      "SCOPE-DRIFT", "MAJOR",
      [(38935, "ARCHITECTURE: FROZEN", "turn [54]: the architecture"),
       (38936, "SPECIFICATION: FROZEN", "turn [54]: the specification text"),
       (38937, "REFERENCE CONTRACT: FROZEN", "turn [54]: the reference-model contract"),
       (38938, "VERIFICATION CONTRACT: FROZEN", "turn [54]: the verification CONTRACT"),
       (41305, "Verification:       FROZEN", "turn [58]: 'Verification' without 'CONTRACT'")],
      "The frozen status block applies `FROZEN` to four distinct objects — architecture, "
      "specification, reference contract, verification contract. The turn-[58] and README "
      "blocks drop the word 'CONTRACT' and say `Verification: FROZEN`, which reads as a "
      "claim that verification has been frozen (i.e. completed and fixed) rather than that "
      "the contract governing it has. spec/05 §6.10 states the correct reading as a "
      "normalization rule.",
      "This is the N-31 law (`Frozen ≠ Verified`) and it is the repository's central "
      "claim-discipline risk: at this commit no verification has been performed at all, "
      "so `Verification: FROZEN` read as 'verified and fixed' would be a false "
      "conformance claim, which R-CLAIM-01 prohibits. The same word carries the "
      "'requirements are stable' meaning in all five sites and the 'evidence is complete' "
      "meaning in none of them.",
      "All five status lines recorded verbatim; none rewritten. The dictionary makes "
      "`Frozen` (T-69) a term with the single meaning 'requirements are stable', forbids "
      "'verified'/'final'/'complete'/'correct' as substitutes, and requires that any "
      "quotation of a status block preserve the word 'CONTRACT' where the source has it "
      "and gloss it where the source omits it. spec/05 §6.9-6.10 is linked as the "
      "existing rule.",
      ["T-69", "T-64", "T-66", "T-67", "T-68", "T-65"],
      [], "", True,
      [("README.md", 12, "Verification:       FROZEN", "the README's contract-less form")]),
    X("X-53", "Implementation status is 'READY' twice and 'IN PROGRESS' once in the source, and the README reverses the order",
      "SCOPE-DRIFT", "INFO",
      [(38939, "IMPLEMENTATION: READY", "turn [54]"),
       (39053, "Implementation:     READY", "turn [54], second status block"),
       (41307, "Implementation:     IN PROGRESS", "turn [58] — the LATEST source statement")],
      "The source states `IMPLEMENTATION: READY` twice (turn [54]) and `Implementation: "
      "IN PROGRESS` once (turn [58], later). The README states `Implementation: IN "
      "PROGRESS` in its first status block (L12) and `Implementation: READY` in its last "
      "(L735). C-09/AMB-24 record the contradiction but cite README L22-28 and L656-661 "
      "and source L42092-42100, none of which contains a status block (X-61).",
      "Neither statement is repository evidence: this repository contains no "
      "implementation, so the correct status is 'no implementation present' and every "
      "obligation is `SPECIFIED` (spec/00 §2). The collision matters only because a "
      "reader may take 'READY' as a claim that implementation has begun, which would "
      "violate the evidence ladder (N-06).",
      "All four status lines recorded verbatim with correct citations; none rewritten. "
      "Under latest-frozen-text the turn-[58] `IN PROGRESS` governs the source, and the "
      "canonicalization layer's 'no implementation present' governs the repository. This "
      "entry corrects C-09's citations by supplying the real ones rather than editing "
      "C-09.",
      ["T-65", "T-64", "T-68"],
      ["C-09", "AMB-24"], "", True,
      [("README.md", 12, "Implementation:     IN PROGRESS", "the README's first status block"),
       ("README.md", 780, "Implementation     READY", "the README's last status block")]),
]


COLLISIONS += [
    X("X-54", "Four `TAG_*` constant names denote two disjoint tag namespaces with different values",
      "SYMBOL-OVERLOAD", "BLOCKING",
      [(29952, "pub const TAG_BOOL: u8 = 0x10;", "turn [41]: `TAG_BOOL` is an ENVELOPE type tag"),
       (33171, "const TAG_UNIT: u8 = 0x00; const TAG_BOOL: u8 = 0x01; const TAG_INTEGER: u8 = 0x02;",
        "turn [45]: `TAG_BOOL` is a VALUE VARIANT discriminant"),
       (29955, "pub const TAG_SYMBOL: u8 = 0x20;", "turn [41]: envelope type tag for `Symbol`"),
       (32368, "const TAG_SYMBOL: u8 = 0x04;", "turn [43]: discriminant for `Value::Symbol`"),
       (33194, "Self::TAG_SYMBOL => {", "turn [45]: the discriminant arm"),
       (33195, "let sym_payload = cursor.read_envelope_payload(Symbol::TYPE_TAG)?;",
        "turn [45]: the ENVELOPE tag, one line below the discriminant of the same name"),
       (29953, "pub const TAG_INTEGER: u8 = 0x11;", "turn [41]: envelope type tag"),
       (29954, "pub const TAG_STRING: u8 = 0x12;", "turn [41]: envelope type tag")],
      "The identifier prefix `TAG_` names two disjoint namespaces. In turn [41]'s frozen "
      "15A const block, `TAG_BOOL`/`TAG_INTEGER`/`TAG_STRING`/`TAG_SYMBOL`/`TAG_CAPREF`/`"
      "TAG_VEC`/`TAG_BTREEMAP` are ENVELOPE type tags (0x10, 0x11, 0x12, 0x20, 0x30, "
      "0x40, 0x41). In turns [43] and [45], the SAME four names `TAG_BOOL`/`TAG_INTEGER`/"
      "`TAG_STRING`/`TAG_SYMBOL` are `Value` VARIANT DISCRIMINANTS with different values "
      "(0x01, 0x02, 0x03, 0x04). Turn [41] itself uses the prefix `DISC_` for "
      "discriminants, so the rename to `TAG_` in turns [43]-[45] is what creates the "
      "clash. Both blocks are labeled frozen; the later one governs the discriminants "
      "(per C-02) but nothing revokes turn [41]'s `TAG_*` envelope constants, which the "
      "frozen standalone tags `Value 0x00 / Symbol 0x20 / CapRef 0x30 / ActorId 0x40 / "
      "EffectId 0x41` still depend on.",
      "These are Rust constants, so the collision is not merely notational: a module that "
      "imports turn [41]'s const block and turn [45]'s `impl Value` block does not "
      "compile, and an implementer who resolves the clash by keeping one set silently "
      "re-tags the other layer. Concretely, `TAG_SYMBOL = 0x04` in the discriminant "
      "namespace and `0x20` in the envelope namespace, and the frozen `Value::Symbol` "
      "encoder needs BOTH in the same function (L33194-33195). Getting either wrong "
      "changes `EffectDigest`, `StateDigest` and `ResultDigest`, so every golden vector, "
      "WAL frame and snapshot digest diverges. R-CANON-03/04 and the 15C.36 differential "
      "boundary cannot be satisfied while the names are ambiguous. Blocks milestone M1.",
      "Both namespaces recorded verbatim with their values; NO constant is renamed, "
      "because both are frozen identifiers and renaming either would silently change an "
      "API. The dictionary separates them as two TERMS — `EnvelopeTypeTag` (T-63, the "
      "`TAG_*`/`TYPE_TAG` namespace, values 0x00/0x10-0x12/0x20/0x30/0x40/0x41) and "
      "`ValueDiscriminant` (T-62, the `DISC_*`/`TAG_*` namespace, values 0x00-0x07) — and "
      "requires that any prose about a tag byte name its layer. The decision needed is "
      "which const block an implementation may import, and under what module path, since "
      "the two cannot coexist unqualified.",
      ["T-62", "T-63", "T-31", "T-45"],
      ["C-02"], "Yes — the frozen 15A const blocks use `TAG_*` for two disjoint tag "
                "namespaces with conflicting values. Decide the qualified paths an "
                "implementation must use. Blocks M1.", True),
    X("X-55", "Turn [41]'s '(Frozen)' `Value` discriminant table lists 5 of 8 variants and contradicts turns [43]/[45] on `Capability`",
      "FIELD-SET", "MAJOR",
      [(29927, "### 3. Value Variant Discriminants (Frozen)", "turn [41]: the table is "
                                                               "titled Frozen"),
       (29934, "| `Capability(c)` | `0x0A` | Complete `CapRef` envelope |",
        "turn [41]: `Capability` = 0x0A"),
       (29965, "pub const DISC_CAPABILITY: u8 = 0x0A;", "turn [41]: the const agrees with "
                                                          "its own table"),
       (32369, "const TAG_CAPABILITY: u8 = 0x05;", "turn [43]: `Capability` = 0x05"),
       (33172, "const TAG_STRING: u8 = 0x03; const TAG_SYMBOL: u8 = 0x04; const TAG_CAPABILITY: u8 = 0x05;",
        "turn [45]: `Capability` = 0x05, and `Symbol`/`List`/`Map` now exist"),
       (29527, "Your implementation itself produces `0x09`; the test currently expects `0x0A`, so the test would fail.",
        "turn [40]: the 0x0A expectation is acknowledged as a failing test, one turn before "
        "it is frozen")],
      "The turn-[41] discriminant table is headed '(Frozen)' but enumerates only `Unit`, "
      "`Bool`, `Integer`, `String` and `Capability` — `Symbol`, `List` and `Map` have no "
      "discriminant at all, so three of the eight frozen `Value` variants are unencodable "
      "under it. It also assigns `Capability` the byte 0x0A, while turns [43] and [45] "
      "assign 0x05 in a dense 0x00-0x07 range. Turn [40], one turn earlier, records that "
      "an implementation produced 0x09 where a test expected 0x0A and that the test "
      "'would fail' — so 0x0A entered the frozen table from a known-broken expectation.",
      "A capability carried inside a `Value` is the object `Expr::Request.capability` "
      "resolves to, and `Value::Capability(CapRef)` is one of the two variants whose "
      "payload is a nested envelope. Its discriminant therefore participates in every "
      "`EffectDigest` for a capability-bearing request and in `StateDigest` for any "
      "snapshot holding a `CapRef`. Two frozen tables disagreeing on that byte means two "
      "conforming encoders produce different digests for the same state, which breaks "
      "R-PERSIST-05 determinism and makes 15C.34 differential persistence testing "
      "undecidable. The incompleteness is worse than the contradiction: an implementer "
      "following the '(Frozen)' table literally cannot encode `Value::List` at all.",
      "Both tables recorded verbatim; neither rewritten and no discriminant renamed. "
      "Under latest-frozen-text the dense turn-[45] set 0x00-0x07 governs, which is also "
      "the resolution req/03 §2 already records for C-02 ('`Value` envelope discriminants "
      "`0x00`–`0x07`'). This entry adds what C-02 does not cover: that the superseded "
      "table is itself labeled Frozen, that it is INCOMPLETE rather than merely "
      "different, and that the specific conflicting variant is `Capability`.",
      ["T-62", "T-63", "T-31", "T-13"],
      ["C-02"], "", True),
    X("X-56", "The byte 0x00 carries four distinct meanings across four encoding layers",
      "SYMBOL-OVERLOAD", "MINOR",
      [(29951, "pub const TAG_VALUE: u8 = 0x00;", "layer 1: the ENVELOPE type tag meaning "
                                                   "'what follows is a `Value`'"),
       (29961, "pub const DISC_UNIT: u8 = 0x00;", "layer 2: the `Value` VARIANT "
                                                   "discriminant meaning 'Unit'"),
       (29273, "const TYPE_TAG: u8 = 0x00; // Envelope for the enum itself",
        "turn [40]: layer 1 restated, with the comment that makes the layering explicit"),
       (28750, "| `bool` | 1 byte (`0x00` for false, `0x01` for true) |",
        "turn [38]: layer 3: 0x00 as the value `false`"),
       (28756, "*   **`Option<T>`**: 1 byte tag (`0x00` = None, `0x01` = Some)",
        "turn [38]: layer 4: 0x00 as `None`"),
       (28757, "*   **`Result<T, E>`**: 1 byte tag (`0x00` = Ok, `0x01` = Err)",
        "turn [38]: layer 4: 0x00 as `Ok`"),
       (33182, "0x00 => Ok(Value::Bool(false)),", "turn [45]: layer 3 inside a layer-2 arm")],
      "0x00 is the envelope type tag for `Value`, the `Value::Unit` discriminant, the "
      "encoding of `false`, and the encoding of `None`/`Ok`. Encoding `Value::Unit` "
      "therefore yields a byte string in which 0x00 appears as the type tag, inside the "
      "big-endian length, and as the discriminant. The turn-[38] table adds a fifth use "
      "at a superseded width, `Value::Unit: Tag 0x00000000` (L28760).",
      "The format is positionally decodable — the envelope fixes where each byte sits — "
      "so this is not a correctness defect. It is a reading hazard of exactly the kind "
      "C-02 warns about: an implementer who treats the type-tag registry and the "
      "discriminant table as one namespace (both are called 'tags', both begin at 0x00, "
      "and both are headed 'Frozen') will accept `0x00` as `Value::Unit` at the envelope "
      "layer and mis-frame every object. R-CANON-04's strict rejection of an unknown "
      "`type_tag` depends on the two namespaces staying separate.",
      "All uses recorded verbatim; no tag renamed. The dictionary requires that any "
      "prose citing a tag byte name its layer (X-54's two TERMS), and records that the "
      "turn-[38] `0x00000000` width is superseded by the `u8` tags per X-50. C-02 is "
      "linked as the register entry that already separates standalone tags from "
      "discriminants.",
      ["T-62", "T-63", "T-31"],
      ["C-02"], "", True),
    X("X-57", "`Request` denotes an `Expr` variant, a redex form, a theorem predicate, an implementation phase and a struct stem",
      "SYMBOL-OVERLOAD", "MAJOR",
      [(12183, "Request {", "turn [21]: the `Expr::Request` AST variant"),
       (14039, "Request { capability: Box<Expr>, operation: Op, target: TargetExpr, params: Vec<Expr> },",
        "turn [22]: variant, field set A"),
       (14422, "Request { capability: Box<Expr>, operation: Op, target: Box<Expr>, params: Vec<Expr> },",
        "turn [22]: variant, field set B (`target: Box<Expr>` not `TargetExpr`)"),
       (7374, "\\langle K[\\textbf{request}(E, \\text{cap}(c))],", "turn [13]: `request(E, cap(c))`, "
                                                                    "a lowercase REDEX FORM in an "
                                                                    "evaluation context"),
       (7255, "$$ \\boxed{ \\neg \\text{Authorized}(A, E, t) \\;\\Rightarrow\\; \\neg \\text{Request}(E) } $$",
        "turn [13]: `Request(E)`, a PREDICATE over effects in the central theorem"),
       (15927, "\\text{Request}", "turn [23]: `Request` as a rung of the implementation-phase "
                                   "ladder Let/Seq/If → Lambda/Call → Attenuate → Request → "
                                   "Actors → Host"),
       (20270, "\\text{Phase 12: Request}", "turn [27]: `Request` as a PHASE NAME"),
       (1447, "pub struct EffectRequest {", "turn [3]: the struct whose stem is `Request`"),
       (11061, "fn step_request(actor: &mut ActorState, machine: &mut GlobalConfig, expr: Expr)",
        "turn [18]: the transition function"),
       (35129, "EffectPrepared { id: EffectId, actor: ActorId, digest: EffectDigest },",
        "turn [47]: the durable lifecycle has NO `Request` record — the in-memory "
        "`EffectRequest` corresponds to `EffectPrepared`")],
      "One stem carries five roles: `Expr::Request` is a term constructor (declared with "
      "two different field sets, X-35); `request(E, cap(c))` is a lowercase redex form in "
      "the operational rules; `Request(E)` is a predicate in the boxed central theorem; "
      "`Request`/`Phase 12: Request` is an implementation-phase name; and `EffectRequest` "
      "/ `step_request` are a struct and a function built on the stem. The durable WAL "
      "lifecycle then has no `Request` record at all — its first stage is "
      "`EffectPrepared` — so the in-memory and durable vocabularies do not line up on "
      "this stem.",
      "R-CORE-03 is stated as `¬Authorized(A,E,t) ⇒ ¬Request(E)` and glossed "
      "'equivalently `¬Authorized ⇒ ¬Request` at the operational level' (spec/01 L27). "
      "That equivalence holds only if the PREDICATE `Request(E)` and the operational "
      "form `Expr::Request` denote the same event, and neither is the durable "
      "`EffectPrepared`. An implementer who instruments the wrong one — e.g. counts "
      "`WalRecord::EffectPrepared` rows as `Request(E)` — gets a theorem that is "
      "unfalsifiable, because the WAL can contain a `Prepared` record for a request the "
      "evaluator rejected before issuing. This is the `EffectRequest ≠ EffectIssued` "
      "distinction (N-16) at the naming level.",
      "All five roles recorded; no identifier renamed — `Expr::Request`, `EffectRequest`, "
      "`step_request`, `request(·,·)` and `Request(·)` are all frozen. The dictionary "
      "gives each its own TERM (`Request` the predicate, T-14; `Expr::Request` the "
      "variant, T-32; `EffectRequest` the struct, T-17) and states the bridge explicitly: "
      "`Request(E)` is true exactly when the evaluator reaches an `Expr::Request` redex "
      "whose checks pass, which produces an `EffectRequest`, which is durable as "
      "`WalRecord::EffectPrepared`. Phase names are marked as PROSE, never as types.",
      ["T-14", "T-17", "T-32", "T-18", "T-45"],
      ["AMB-13", "C-01"], "", True),
    X("X-58", "`Fault` is declared seven times and `HostPolicyDenied` carries two different payload types",
      "TYPE-HOMONYM", "MAJOR",
      [(10882, "pub enum Fault {", "turn [18]: declaration 1 — has `HostPolicyViolation`, no "
                                    "payload"),
       (17788, "pub enum Fault {", "turn [25]: declaration 2"),
       (18125, "pub enum Fault {", "turn [26]: declaration 3"),
       (22415, "pub enum Fault {", "turn [29]: declaration 4"),
       (22436, "HostPolicyDenied(HostPolicyError),", "turn [29]: payload is the STRUCTURED "
                                                      "`HostPolicyError`"),
       (23319, "pub enum Fault {", "turn [30]: declaration 5"),
       (23323, "HostPolicyDenied(String),", "turn [30]: payload is an UNSTRUCTURED `String`"),
       (23806, "pub enum Fault {", "turn [30]: declaration 6"),
       (23811, "HostPolicyDenied(HostPolicyError),", "turn [30]: back to `HostPolicyError`"),
       (26865, "pub enum Fault {", "turn [33]: declaration 7"),
       (10885, "HostPolicyViolation,", "turn [18]: a SECOND variant name for host-policy "
                                        "denial"),
       (10480, "actor.status = ActorStatus::Fault(Fault::HostPolicyViolation);",
        "turn [18]: `HostPolicyViolation` used where later turns use `HostPolicyDenied`"),
       (21897, ") -> Result<(), HostPolicyError>;", "turn [29]: the error type the "
                                                     "structured payload carries")],
      "`pub enum Fault` is declared seven times across turns [18]-[33], and the "
      "host-policy denial variant appears under two names (`HostPolicyViolation`, "
      "payload-less, turn [18]; `HostPolicyDenied`, turn [29] onward) and, under the "
      "later name, with two payload types: `HostPolicyError` (L22436, L23811) and `String` "
      "(L23323). AMB-08 records the `HostPolicyDenied`/`HostPolicyViolation` naming "
      "split; the PAYLOAD split and the seven-fold redeclaration are not recorded "
      "anywhere.",
      "`Fault` is what an actor's `ActorStatus::Fault(·)` carries, what "
      "`MachineEvent::Fault(·)` reports (L23499), what a WAL event records, and what "
      "15C.43 deliberate fault-injection validation asserts on. A `String` payload makes "
      "the denial reason unmatchable — an implementation cannot branch on WHICH host "
      "policy refused, so the fault-precedence rule 'CapabilityViolation > "
      "BudgetExhausted > HostPolicyViolation' (L8971) is not testable, and "
      "`FAULT-CLASSIFICATION-EXHAUSTIVE` cannot be discharged. It also breaks replay "
      "determinism: a host-supplied `String` is non-deterministic content inside a "
      "record that R-PERSIST-05 requires be reproducible byte-for-byte.",
      "All seven declarations and both payload types recorded verbatim; nothing renamed "
      "and no declaration deleted. Under latest-frozen-text the structured "
      "`HostPolicyDenied(HostPolicyError)` governs (turn [33]'s declaration is the last), "
      "but this entry flags that the choice is load-bearing for replay determinism and "
      "needs explicit confirmation rather than silence. AMB-08 is linked and extended.",
      ["T-70", "T-71", "T-74", "T-41", "T-35", "T-36", "T-52"],
      ["AMB-08", "C-08", "U-08"], "", True),
    X(xid="X-59",
      title="C-08's provenance for the `Fault` taxonomy is wrong in three of its four citations and its fourth mis-describes the text it points at; U-08, spec/05 and REQ-CALC-013 repeat the error",
      kind="PROVENANCE-DEFECT",
      severity="MAJOR",
      sites=[
        (1995, "$$\\frac{}{\\langle \\text{if true } e_2", "what C-08's 1st citation actually points at: the `if true` cost rule (turn [5]), not a fault"),
        (7435, "\\boxed{ \\text{ExternalEffect}(E)", "what C-08's 3rd citation actually points at: the boxed `ExternalEffect` theorem (turn [13])"),
        (7374, "\\text{AuthorizationFailed}", "the real site of C-08's 3rd name — 61 lines BEFORE the line C-08 cites"),
        (1042, "return StepResult::Fault(Fault::CapabilityViolation(e));", "the real site of C-08's 1st name (turn [3])"),
        (937, "return Err(Fault::CapabilityRevoked(cref));", "the real site of C-08's 2nd name (turn [3])"),
        (23784, "## 2. Actor Status and Fault Taxonomy", "C-08's 4th citation: a section HEADING — the start of R-CALC-06's own cited range L23784-23819"),
        (23806, "pub enum Fault {", "the frozen declaration that range contains, 22 lines below the heading"),
        (23807, "// ... (previous faults)", "elision marker: the frozen block does NOT restate earlier variants"),
        (23808, "Capability(CapabilityError),", "the frozen variant — so it DOES exist, contra C-08's `with variants undefined`"),
        (20408, "pub enum CapabilityError {", "the inner error enum IS declared (turn [28]) — contra U-08 and spec/05 L112"),
        (10820, "pub enum HostFault {", "and so is `HostFault` (turn [18]) — contra U-08 and spec/05 L112"),
      ],
      statement=(
        "C-08 (spec/06 L21) cites four lines for the capability-denial naming spread. Read at "
        "those exact lines: **L1995** is the `if true` cost rule, **L7363** is a blank line, "
        "**L7435** is the boxed `ExternalEffect` theorem. None contains a fault, and the three "
        "lowercase forms C-08 quotes — `fault(CapabilityViolation)`, `fault(CapabilityRevoked)`, "
        "`fault(AuthorizationFailed)` — occur nowhere in L1-42312. The real sites are "
        "`Fault::CapabilityViolation(e)` L1042, `Fault::CapabilityRevoked(cref)` L937, and "
        "`AuthorizationFailed` L7374, 61 lines before the cited L7435. The **fourth** citation "
        "is the opposite kind of error: L23784 is the heading '## 2. Actor Status and Fault "
        "Taxonomy', the start of the range mod/01 L155 and spec/03 L52 already cite for "
        "R-CALC-06 (L23784-23819), and that range does contain the frozen `pub enum Fault` at "
        "L23806 with `Capability(CapabilityError)` at L23808. So the citation is right and the "
        "gloss is wrong twice over: 'with variants undefined' is false (L23807-23815 name eight "
        "variants), and the path form C-08 writes, `Fault::Capability(CapabilityError)`, is a "
        "rendering of a variant the source writes as `Capability(CapabilityError),` inside the "
        "enum. The error then propagates. **U-08** (spec/09 L54) claims the inner "
        "`CapabilityError` / `HostPolicyError` / `EffectError` / `HostFault` variants 'are not "
        "enumerated' — but `pub enum CapabilityError` is declared at L20408 and "
        "`pub enum HostFault` at L10820; only `HostPolicyError` and `EffectError` genuinely lack "
        "a declaration. **spec/05 L112** makes the same claim for the same four names under "
        "U-14. **REQ-CALC-013** (req/01-part2 L186) states the taxonomy is a 'closed set; inner "
        "variants not enumerated in the source' — false on both halves, since L23807 carries an "
        "explicit `// ... (previous faults)` elision (so the set is NOT closed) and two of the "
        "four inner enums ARE declared."),
      why_it_matters=(
        "The register is the layer an implementer trusts instead of re-reading 42,312 lines. "
        "Three wrong line numbers send them to unrelated text; the false 'variants undefined' "
        "gloss makes them re-litigate two enums that are already declared and, worse, treat the "
        "frozen `Fault` set as closed when the source explicitly elides part of it. `Fault` "
        "identity is compared by the differential observer (R-REF-05), so an incorrect variant "
        "set is a correctness defect, not a documentation nit."),
      disposition=(
        "PROVENANCE-CORRECTED; nothing renamed. C-08's original wording is kept and annotated "
        "in place (spec/06 L21) with the verified sites; U-08 (spec/09 L54), spec/05 L112 and "
        "REQ-CALC-013's INVARIANTS (req/01-part2 L186) are amended to restrict the 'not "
        "enumerated' claim to `HostPolicyError` and `EffectError` only and to state that "
        "`CapabilityError` (L20408) and `HostFault` (L10820) are declared. U-08/U-14 remain OPEN "
        "on their merits — the elision at L23807 does leave the variant set unclosed — but the "
        "open question is now stated against the real text. WITHDRAWN CLAIM, recorded rather "
        "than silently overwritten (R-SCOPE-03): an earlier annotation added to C-08 by this "
        "same normalization pass asserted that `CapabilityError` 'exists only as a `Result` "
        "error type (L9736/L9743/L9749/L19212), never as a `Fault` variant'. That was itself "
        "wrong — `Capability(CapabilityError)` is a `Fault` variant at L22430 and L23808, and "
        "`Fault::CapabilityError(error)` is constructed at L20389 and L20790. It is withdrawn "
        "and replaced."),
      affects=["T-70", "T-72", "T-74", "T-41", "T-09", "T-10"],
      previously=["C-08", "U-08", "U-14", "AMB-08", "C-53"],
      decision_needed="No new decision; U-08/U-14 stand, restated against verified text.",
      new_finding=True,
      doc_sites=[
        ("spec/06-contradictions-ambiguities.md", 22, "fault(CapabilityViolation)", "C-08's 1st (wrong) citation, kept verbatim above the correction"),
        ("spec/06-contradictions-ambiguities.md", 22, "with variants undefined", "C-08's false gloss on its 4th citation"),
        ("spec/09-unresolved-decisions.md", 56, "denial outcome is named", "U-08 — four names listed, nine verified (X-38)"),
        ("spec/05-terminology.md", 112, "Enum variants not enumerated", "the same claim under U-14"),
        ("req/01-registry-part2-semantics.md", 186, "inner variants not enumerated", "REQ-CALC-013's INVARIANTS — false on both halves"),
      ]),
    X("X-60", "req/00-method §5.4 asserts there is no `15C.1` heading; there is one, and 15C spans two heading levels",
      "PROVENANCE-DEFECT", "MINOR",
      [(35281, "## 15C.1 Purpose", "turn [48]: `15C.1` EXISTS, as an H2"),
       (35326, "# 15C.2 Non-Goals", "turn [48]: `15C.2` onward are H1"),
       (37151, "# 15C.46 Phase Boundary", "turn [48]: the last of 46 numbered sections")],
      "req/00-method §5.4 states 'The turn is numbered 15C.2…15C.46 — there is no "
      "`# 15C.1` heading; L35272–35325 is an unnumbered preamble'. Phase 15C in fact "
      "contains 46 numbered sections, 15C.1 through 15C.46: 45 at heading level H1 and "
      "one — `## 15C.1 Purpose` at L35281 — at H2, inside the range the method note "
      "calls an unnumbered preamble. The claim is true only for the literal string "
      "`# 15C.1` at H1, and the note's own accounting ('All 45 now carry at least…') "
      "leaves 15C.1's requirements unattributed.",
      "The method note is the anchor-of-record for the requirement registry: §5.1's "
      "corrected line anchors and §5.3's carried-forward anchors are what "
      "`req/_validate.py` checks against. A section believed not to exist is a section "
      "whose obligations are not registered, so REQ-REF-001/002/006 — which the note says "
      "cite L35281-35310 — are attributed to an 'unnumbered preamble' rather than to "
      "15C.1. The inconsistent heading level (15C.1 at H2, 15C.2-15C.46 at H1) is the "
      "source-side reason the mistake was easy to make, and it also means any "
      "heading-level-driven extraction of 15C misses its first section.",
      "req/00-method §5.4 is corrected in this pass to record 46 numbered sections at two "
      "heading levels, with L35281 cited as `## 15C.1 Purpose`. No requirement ID is "
      "renumbered and no obligation is re-homed; the correction is additive and is "
      "recorded here so the change to a method note is not silent.",
      ["T-58", "T-64"],
      [], "", True,
      [("req/00-method.md", 220, "there is no `# 15C.1` heading",
        "the false assertion, corrected by this dictionary")]),
    X("X-61", "spec/09 U-15 remains an open decision on a premise req/03 AMB-15 has withdrawn as false",
      "PROVENANCE-DEFECT", "MINOR",
      [(26593, "pub enum ReconciliationOutcome {", "turn [32]: the variant set IS enumerated"),
       (26594, "Completed(EffectReceipt),", "variant 1"),
       (26595, "NotExecuted,", "variant 2"),
       (26596, "Indeterminate,", "variant 3"),
       (38211, "Completed\\Rightarrow Issued", "turn [54]: classification 1 of the three the "
                                               "enum matches"),
       (38232, "Indeterminate", "turn [54]: classification 2"),
       (38243, "NotExecuted", "turn [54]: classification 3"),
       (35132, "EffectReconciled { id: EffectId, digest: EffectDigest, outcome: ReconciliationOutcome },",
        "turn [47]: the frozen WAL record that carries it")],
      "spec/09 U-15 states that 'the variant set of `ReconciliationOutcome` is never "
      "enumerated (beyond the classification of interrupted effects as `Indeterminate`)' "
      "and asks for 'the variant set + per-class admissibility'. The variant set is "
      "enumerated at L26593-26597 as a closed three-variant set, and it matches exactly "
      "the three classifications the turn-[54] recovery text names. req/03 AMB-15 has "
      "already withdrawn the same claim and says so explicitly: '`spec/09` U-15's claim "
      "that the variants are unspecified is likewise false.' spec/09 was never updated.",
      "U-15 is a live entry in the unresolved-decisions register, so it advertises an "
      "open architectural decision that has no open content. Two registers in the same "
      "canonicalization layer now disagree about whether the question is settled, and "
      "the one that is wrong (spec/09) is the one a reader consults for open decisions. "
      "Worse, U-15's proposed variants — `Executed(result)`, `PartiallyExecuted` — do not "
      "exist in the frozen set, so implementing to U-15 would widen a closed enum and "
      "break `WalRecord::EffectReconciled` decoding against recorded traces.",
      "spec/09 U-15 is corrected in this pass to the closed three-variant set with the "
      "L26593-26597 citation, and narrowed to the part that IS genuinely open: per-class "
      "admissibility under U-06, and the turn-[32] constraint that 'only a host protocol "
      "capable of answering authoritatively may produce `NotExecuted` or `Completed`' "
      "(L26601). AMB-15 is linked as the prior withdrawal. No variant is renamed; the "
      "correction removes a false premise rather than changing the type.",
      ["T-45", "T-47", "T-19", "T-20", "T-51"],
      ["U-15", "AMB-15", "U-06"], "", True,
      [("spec/09-unresolved-decisions.md", 75,
        "the variant set of `ReconciliationOutcome` is never enumerated",
        "the false premise, corrected by this dictionary"),
       ("req/03-ambiguous.md", 127,
        "`spec/09` U-15's claim that the variants are unspecified is likewise false",
        "the earlier withdrawal that spec/09 never absorbed")]),
    X("X-62", "req/03 AMB-25 lists `PlannerState`, an identifier that does not occur in the source",
      "PHANTOM-IDENTIFIER", "MINOR",
      [(865, "pub struct ValidatedPlan { ir: PlanIR, effects: EffectSet }",
        "one of the four plan-family names that DO occur"),
       (27175, "pub struct PlanProposal {", "turn [33]: the name that occupies the role "
                                             "AMB-25 assigns to `PlannerState`")],
      "AMB-25's statement is '`Plan`, `PlanProposal`, `PlanIR`, `ExecutablePlan`, "
      "`PlannerState` are used with overlapping meanings.' The identifier `PlannerState` "
      "occurs NOWHERE in `Red-on-Rust.md` (L1-42312) — not as a type, field, function, "
      "prose term or variant. The other four names are attested. `PlannerState` is a "
      "phantom introduced by the ambiguity register itself.",
      "The ambiguity register is what an implementer consults to find out which names are "
      "unsafe to rely on. A phantom entry there has two bad effects: it sends the reader "
      "looking for a type that does not exist, and it inflates the apparent size of the "
      "naming problem, which weakens the four real findings listed beside it. It also "
      "matters for the repository's own rule that generated facts be re-derived from the "
      "source — a term that fails that check should not be in a register at all.",
      "AMB-25 is corrected in this pass to the four attested names, with the correction "
      "recorded here rather than applied silently, and `PlannerState` is entered in this "
      "dictionary as a FORBIDDEN variant that must not be introduced: the role it "
      "gestures at is occupied by `PlanProposal` (T-02), the compiler's output before "
      "validation. No source identifier is renamed, because none exists to rename.",
      ["T-02", "T-06", "T-08", "T-01", "T-55"],
      ["AMB-25"], "", True,
      [("req/03-ambiguous.md", 195, "`PlannerState`",
        "the phantom identifier, removed by this dictionary")]),
    X("X-63", "C-09 and AMB-24 cite README line ranges that contain no status block",
      "PROVENANCE-DEFECT", "MINOR",
      [(38939, "IMPLEMENTATION: READY", "turn [54]: source status 1"),
       (39053, "Implementation:     READY", "turn [54]: source status 2"),
       (41307, "Implementation:     IN PROGRESS", "turn [58]: source status 3, the LATEST")],
      "C-09's evidence is 'README L22–28 (\"Implementation: IN PROGRESS\") vs README "
      "L656–661 / L42092–42100 (\"Implementation: READY\")' and AMB-24 repeats "
      "'`README.md` L22–28 vs L656–661'. The README's two status blocks are at L12 "
      "(`Implementation: IN PROGRESS`) and L735 (`Implementation READY`); L22-28 and "
      "L656-661 contain no status text. The third citation, L42092-42100, is beyond the "
      "end of the frozen source, whose last line is 42312 in a different file — the "
      "README is 745 lines long, so no README line in the 42000s exists. It was 708 lines when this collision was first recorded; the block moved to L732 when this pass added a `term/` paragraph to the README, and to L735 when the declaration sweep extended that same paragraph. The citation is therefore anchored to the `# Project Status` heading (now L732) as well as to the line, so that it survives further growth. The real "
      "in-source contradiction is between L38939/L39053 (`READY`, turn [54]) and L41307 "
      "(`IN PROGRESS`, turn [58]).",
      "The contradiction C-09 reports is real, but three of its four citations are "
      "unverifiable and one refers to a line range that cannot exist in the cited file. "
      "The status question is the repository's claim-discipline hinge: `READY` read as "
      "'implementation exists' would be a conformance claim with no evidence behind it, "
      "which R-CLAIM-01 and the N-05/N-06 ladder prohibit. A reader who tries to check "
      "the citations, fails, and concludes the finding is spurious would be left with an "
      "unresolved status contradiction — the opposite of the intended effect.",
      "C-09 and AMB-24 are corrected in this pass to the verified citations (README L12 "
      "and L735 under the `# Project Status` heading at L732; source L38939, L39053, L41307), and the resolution is stated: under "
      "latest-frozen-text the turn-[58] `IN PROGRESS` governs the source, while the "
      "canonicalization layer's own position — no implementation present, every "
      "obligation `SPECIFIED` (spec/00 §2) — governs the repository and makes both source "
      "status lines non-evidence. No status text is rewritten in either file.",
      ["T-64", "T-65", "T-68", "T-69"],
      ["C-09", "AMB-24"], "", True,
      [("spec/06-contradictions-ambiguities.md", 23,
        "README L22–28 (\"Implementation: IN PROGRESS\") vs README L656–661 / L42092–42100",
        "the defective citations"),
       ("req/03-ambiguous.md", 189, "`README.md` L22–28 vs L656–661",
        "the same defective citations, repeated"),
       ("README.md", 12, "Implementation:     IN PROGRESS", "the real first status block"),
       ("README.md", 780, "Implementation     READY", "the real last status block")]),
    X(xid="X-64",
      title="`Fault::StalePlan` is used by the frozen source at L28373 but is a variant of none of the seven `Fault` declarations",
      kind="UNDECLARED-VARIANT",
      severity="MAJOR",
      sites=[
        (28373, "is rejected with `Fault::StalePlan`", "turn [36]: the ONLY occurrence of the qualified path — the source names the variant itself"),
        (27236, "StalePlan", "turn [33]: a bare token, the sole content of a one-line ```text block"),
        (23806, "pub enum Fault {", "the frozen declaration R-CALC-06 cites: eight listed variants, no `StalePlan`"),
        (23807, "// ... (previous faults)", "the elision that makes the frozen block non-exhaustive"),
        (26865, "pub enum Fault {", "turn [33]: the actor-local declaration, contemporary with L27236, also without `StalePlan`"),
        (10882, "pub enum Fault {", "turn [18]: no `StalePlan`"),
      ],
      statement=(
        "`Fault::StalePlan` occurs verbatim once in L1-42312, at L28373 (turn [36]): “A "
        "`PlanProposal` with `observation_sequence < current_sequence` is rejected with "
        "`Fault::StalePlan`”. The bare token `StalePlan` occurs once more, at L27236 (turn [33]), "
        "as the sole content of a one-line ```text block. No `pub enum Fault` declaration — "
        "L10882, L17788, L18125, L22415, L23319, L23806, L26865 — contains the variant, and the "
        "frozen L23806 block elides its own head with `// ... (previous faults)` at L23807, so it "
        "cannot be read as exhaustive. This is therefore a used-but-undeclared variant path, one "
        "of twelve (X-69), and NOT a phantom introduced by the canonicalization layer. Three "
        "records name it and all three are source-supported: **spec/01 L138** (normative "
        "R-CALC-06) writes “… | InvalidReceipt` (plus `StalePlan` at the planner boundary)”; "
        "**REQ-CALC-014** (req/01-part2 L195-199) states “`StalePlan` is a member of the fault "
        "taxonomy at the planner boundary” with POSTCONDITIONS “`Fault::StalePlan` produced” and "
        "a SOURCE line that already cited L28373; **AMB-08** (req/03 L68) listed it among the "
        "frozen variants. What is *not* supported is AMB-08's citation “L23806-23824”, which "
        "runs past the enum's closing brace at L23816 into the unrelated heading “## 3. Request "
        "Continuation Frames” at L23821 and contains no `StalePlan`; the denial names are at "
        "L8758, one line outside the range AMB-08 cited."),
      why_it_matters=(
        "Two separate things matter here, and the second is about this repository rather than the "
        "source. (1) The source names a fault variant that none of its own declarations admits, "
        "so an implementer following R-CALC-06 adds a variant no frozen declaration authorizes — "
        "and because `Fault` identity is compared by the differential observer (R-REF-05), that "
        "addition is observable, not inert. It also widens R-CALC-06 from eight variants to "
        "nine, and AMB-08 is graded “Blocking: yes … the single most blocking ambiguity in the "
        "set”, so its statement is the one most likely to be implemented from. (2) An earlier "
        "revision of this pass filed this row as a PHANTOM-IDENTIFIER on the claim that "
        "“`Fault::StalePlan` occurs nowhere in L1-42312”, and amended four documents on that "
        "premise. The claim is false — the string occurs at L28373 — and REQ-CALC-014's own "
        "SOURCE line had cited L28373 all along, so the withdrawal contradicted the record's own "
        "provenance. A canonicalization layer that retracts correct normative text on a "
        "misread grep is a worse defect than the one it was trying to fix, which is why the "
        "retraction is itself recorded rather than quietly undone."),
      disposition=(
        "REPORTED, not resolved, and the earlier false correction REVERTED per R-SCOPE-03: the "
        "four documents amended on the “occurs nowhere” premise are restored, each with the "
        "withdrawn wording quoted in place so the retraction stays visible — spec/01 L138 (its "
        "annotation now records that `StalePlan` is used-but-undeclared rather than phantom), "
        "REQ-CALC-014's STATEMENT (L197) and POSTCONDITIONS (L199), and AMB-08's list (req/03 "
        "L68). AMB-34 is rewritten from “asserted but undeclared phantom” to “used but "
        "undeclared”, and C-54 likewise. The dictionary records `StalePlan` as a protected "
        "*source token* at both L27236 and L28373 and explicitly NOT as a declared `Fault` "
        "variant. Whether it SHOULD join the declared taxonomy is left to U-08, which owns the "
        "variant set — and U-08 now has to rule on all twelve undeclared paths at once (X-69), "
        "not on this one alone. Nothing is renamed and no variant is invented."),
      affects=["T-70", "T-02", "T-04"],
      previously=["C-54", "C-38", "U-13", "AMB-08", "AMB-34", "X-62", "X-69"],
      decision_needed="Yes, but owned by U-08 and now widened by X-69: does `StalePlan` join the declared `Fault` taxonomy (the source uses the qualified path at L28373, so the answer is no longer forced), or is staleness rejection remapped onto a declared variant?",
      new_finding=True,
      doc_sites=[
        ("spec/01-canonical-specification.md", 160, "plus `StalePlan` at the planner boundary", "normative R-CALC-06 — source-supported and kept; its annotation now says used-but-undeclared, not phantom"),
        ("req/01-registry-part2-semantics.md", 197, "Verified, correction reverted", "REQ-CALC-014 STATEMENT, restored after the phantom claim was shown false"),
        ("req/01-registry-part2-semantics.md", 199, "Withdrawal reverted", "REQ-CALC-014 POSTCONDITIONS, restored — `Fault::StalePlan` occurs verbatim at L28373"),
        ("req/01-registry-part2-semantics.md", 195, "L28373([36])", "REQ-CALC-014's SOURCE line, which cited the occurrence all along"),
        ("req/03-ambiguous.md", 68, "that strike was itself wrong", "AMB-08's list, qualified in place rather than struck"),
        ("req/03-ambiguous.md", 264, "occurs nowhere in L1–42312", "AMB-34, rewritten, with the withdrawn claim quoted"),
        ("spec/06-contradictions-ambiguities.md", 69, "`Fault::StalePlan` occurs verbatim once, at L28373", "C-54, rewritten from a phantom finding to a used-but-undeclared one"),
        ("spec/06-contradictions-ambiguities.md", 126, "rewritten** in this revision", "C-59..C-65 summary line, recording the retraction of the earlier claim"),
      ]),
    X(xid="X-65",
      title="`MarshalFault` is declared twice with completely disjoint variant sets, and is used as an elided `Fault` payload",
      kind="TYPE-HOMONYM",
      severity="MAJOR",
      sites=[
        (10846, "pub enum MarshalFault {", "turn [18]: declaration 1"),
        (10847, "CapabilityNotTransferable,", "declared variant 1a"),
        (10848, "InvalidFormat,", "declared variant 1b"),
        (25983, "pub enum MarshalFault {", "turn [32]: declaration 2 — DISJOINT from declaration 1"),
        (25984, "CapabilityRequiresDelegation,", "declared variant 2a — the one mod/06 and REQ-MARSHAL cite"),
        (25985, "SerializationError,", "declared variant 2b"),
        (26871, "MarshalFault(...),", "turn [33]: `MarshalFault` as a `Fault` variant payload, written elided"),
      ],
      statement=(
        "`pub enum MarshalFault` is declared twice. Turn [18] (L10846-10849) declares "
        "{`CapabilityNotTransferable`, `InvalidFormat`}; turn [32] (L25983-25986) declares "
        "{`CapabilityRequiresDelegation`, `SerializationError`}. The two sets share **zero** "
        "variants, so this is not a widening but a replacement with no retraction and no "
        "supersession note. The canonicalization layer cites only the turn-[32] form "
        "(mod/06-actor L62/L103, REQ-MARSHAL postcondition "
        "`Err(MarshalFault::CapabilityRequiresDelegation)` at req/01-part1 L301), and no record "
        "anywhere notes that `CapabilityNotTransferable` and `InvalidFormat` exist or have been "
        "dropped. Separately, the turn-[33] actor-local `Fault` (L26865) carries "
        "`MarshalFault(...)` as a variant payload with the payload elided, so the `Fault` "
        "taxonomy depends on a type whose own variant set is contested."),
      why_it_matters=(
        "R-MARSHAL-01..04 make capability rejection at the marshalling boundary a security "
        "property, and spec/08 maps 'embedded CapRef in List ⇒ MarshalFault' to a verification "
        "obligation. An implementation that matches on the turn-[18] set cannot produce "
        "`CapabilityRequiresDelegation`, and one that matches on the turn-[32] set cannot "
        "produce `CapabilityNotTransferable`; the two are not aliases, they denote different "
        "conditions (non-transferable vs requires-delegation). Because faults are compared by "
        "the differential observer, the choice is observable."),
      disposition=(
        "Both declarations recorded verbatim in T-73 with the turn-[18] form listed under "
        "`supersedes`; nothing renamed and neither declaration deleted. Under latest-frozen-text "
        "the turn-[32] set governs, but this entry flags that the supersession was never stated "
        "and that `CapabilityNotTransferable` has no successor — the same gap C-08 records for "
        "`ScopeViolation`. Joined to U-08/U-14, which own the error-variant enumeration."),
      affects=["T-73", "T-70", "T-35"],
      previously=["AMB-08", "U-14"],
      decision_needed="Yes, folded into U-14: which `MarshalFault` variant set governs, and does `CapabilityNotTransferable` survive as a distinct condition?",
      new_finding=True,
      doc_sites=[
        ("mod/06-actor.md", 103, "MarshalFault::CapabilityRequiresDelegation", "cites only the turn-[32] variant set"),
        ("req/01-registry-part1-foundations.md", 301, "Err(MarshalFault::CapabilityRequiresDelegation)", "REQ postcondition citing only the turn-[32] set"),
        ("spec/08-verification-mapping.md", 127, "MarshalFault", "verification mapping that assumes a single variant set"),
      ]),
    X(xid="X-66",
      title="`CapabilityError::Invalid` is used as the `derive` fallback but never declared; the declared sibling `InvalidConstraint` is used for the same fallback in the same turn",
      kind="UNDECLARED-VARIANT",
      severity="MAJOR",
      sites=[
        (20408, "pub enum CapabilityError {", "turn [28]: the ONLY declaration of the inner error enum"),
        (20409, "Revoked,", "declared variant"),
        (20410, "Expired,", "declared variant — never used; the used `ExpiredOrRevoked` belongs to `RefCapabilityError`"),
        (20411, "InvalidConstraint,", "declared variant"),
        (20412, "// ...", "verbatim elision marker — the declared set is not closed"),
        (20451, "Err(CapabilityError::InvalidConstraint)", "turn [28]: `CapabilityKernelView::derive` fallback, using the DECLARED variant"),
        (20835, "unwrap_or_else(|| Err(CapabilityError::Invalid))", "turn [28]: the SAME fallback restated, using an UNDECLARED variant"),
      ],
      statement=(
        "`pub enum CapabilityError` is declared once, at L20408 (turn [28]), as "
        "{`Revoked`, `Expired`, `InvalidConstraint`, `// ...`}. Within the same turn the "
        "`CapabilityKernelView::derive` result-queue fallback is written twice with two "
        "different error values: L20451 uses `Err(CapabilityError::InvalidConstraint)` — a "
        "declared variant — while L20835 uses "
        "`unwrap_or_else(|| Err(CapabilityError::Invalid))`. `CapabilityError::Invalid` is "
        "never declared. The elision at L20412 leaves the set formally open, but nothing in the "
        "source introduces `Invalid`, and the two sites are not two different methods: both pop "
        "the front of `self.results` and return the default when it is empty. The reference "
        "model uses a third name again, `RefCapabilityError::ExpiredOrRevoked` (L20619), which "
        "collapses the declared `Expired` and `Revoked` into one."),
      why_it_matters=(
        "`CapabilityError` is the payload of the frozen `Fault::Capability(CapabilityError)` "
        "variant (L23808), so its variant set is part of the fault vocabulary the differential "
        "observer compares (R-REF-05). An implementation that follows L20835 cannot compile "
        "against the L20408 declaration; one that follows L20451 reports a different fault "
        "value for the identical empty-queue condition. spec/05 L112 and U-08 currently say "
        "these variants are 'not enumerated', which hides the fact that a declaration exists and "
        "that the source contradicts itself against it (X-59)."),
      disposition=(
        "REPORTED; nothing renamed and no variant invented. T-72 records the declaration "
        "verbatim, marks `Invalid` as used-but-undeclared and `Expired` as declared-but-unused, "
        "and keeps the elision marker as a protected token so the set is not represented as "
        "closed. spec/05 L112 and U-08 are amended to say that `CapabilityError` IS declared at "
        "L20408 behind an elision, and that the open question is the *elided* remainder plus the "
        "`Invalid`/`InvalidConstraint` split. Joined to U-14."),
      affects=["T-72", "T-70", "T-13", "T-09"],
      previously=["U-14", "U-08", "X-59"],
      decision_needed="Yes, folded into U-14: is `Invalid` a distinct variant or a typo for `InvalidConstraint`, and what fills the L20412 elision?",
      new_finding=True,
      doc_sites=[
        ("spec/05-terminology.md", 112, "`CapabilityError`", "listed as 'Enum variants not enumerated' although L20408 declares them"),
        ("spec/09-unresolved-decisions.md", 56, "variants are not enumerated", "U-08's claim, which hides the declared set and the `Invalid` split"),
      ]),
    X(xid="X-67",
      title="`HostFault` is declared once with two variants, and eight different undeclared variant paths are used — six of them on the frozen replay path",
      kind="UNDECLARED-VARIANT",
      severity="BLOCKING",
      sites=[
        (10820, "pub enum HostFault {", "turn [18]: the ONLY declaration — two variants"),
        (10821, "IoError(String),", "declared variant 1"),
        (10822, "PolicyViolation(String),", "declared variant 2"),
        (1203, "HostFault::UnboundCapability", "turn [3]: UNDECLARED"),
        (1208, "HostFault::ConcreteScopeViolation", "turn [3]: UNDECLARED (also L1214)"),
        (1210, "HostFault::Io", "turn [3]: UNDECLARED — near-miss of the declared `IoError` (also L1216)"),
        (1245, "HostFault::ReplayTraceExhausted", "turn [3]: UNDECLARED — 1st of 6 uses"),
        (10546, "HostFault::TraceExhausted", "turn [18]: UNDECLARED — a THIRD name for the same exhausted-trace condition"),
        (10550, "HostFault::ReplayIdMismatch", "turn [18]: UNDECLARED"),
        (10553, "HostFault::ReplayDigestMismatch", "turn [18]: UNDECLARED"),
        (24020, "HostFault::ReplayTraceExhausted", "turn [30]: UNDECLARED"),
        (25496, "HostFault::ReplayTraceExhausted", "turn [32]: UNDECLARED"),
        (25500, "HostFault::ReplayCorruption", "turn [32]: UNDECLARED"),
        (25838, "HostFault::ReplayTraceExhausted", "turn [32]: UNDECLARED"),
        (25841, "HostFault::ReplayCorruption", "turn [32]: UNDECLARED — 'Reject mismatched digest'"),
        (34519, "HostFault::ReplayTraceExhausted", "turn [46]: UNDECLARED"),
        (34522, "HostFault::ReplayCorruption", "turn [46]: UNDECLARED"),
        (34528, "HostFault::ReplayCorruption", "turn [46]: UNDECLARED"),
        (35225, "HostFault::ReplayTraceExhausted", "turn [47]: UNDECLARED — the frozen 15C.42 `ReplayHost`"),
        (35226, "HostFault::ReplayCorruption", "turn [47]: UNDECLARED — the frozen 15C.42 `ReplayHost`"),
        (23813, "Host(HostFault),", "turn [30]: `HostFault` is the payload of the frozen `Fault::Host` variant"),
      ],
      statement=(
        "`pub enum HostFault` is declared exactly once, at L10820 (turn [18]), with two "
        "variants: `IoError(String)` and `PolicyViolation(String)`. The source then uses eight "
        "distinct `HostFault::` paths, **none** of which is declared: `UnboundCapability` "
        "(L1203), `ConcreteScopeViolation` (L1208, L1214), `Io` (L1210, L1216), "
        "`ReplayTraceExhausted` (L1245, L24020, L25496, L25838, L34519, L35225 — six uses), "
        "`ReplayCorruption` (L25500, L25841, L34522, L34528, L35226, L35227 — six uses), "
        "`TraceExhausted` (L10546), `ReplayIdMismatch` (L10550) and `ReplayDigestMismatch` "
        "(L10553). Neither declared variant is ever used, and `Io` is a near-miss of "
        "`IoError`. Two names denote the exhausted-trace condition (`ReplayTraceExhausted` six "
        "times, `TraceExhausted` once) and three denote a replay mismatch (`ReplayCorruption`, "
        "`ReplayIdMismatch`, `ReplayDigestMismatch`). `ReplayCorruption` is *also* a declared "
        "`Fault` variant (L23814), so the same identifier denotes a fault at two different "
        "levels of the taxonomy. The heaviest uses sit on the frozen 15C.42 `ReplayHost` "
        "(L35225-35227, turn [47]) and on the R-HOST-03/04/05 replay obligations — the code "
        "REQ-HOST-008 is written against."),
      why_it_matters=(
        "This is BLOCKING, not cosmetic. `ReplayHost` (T-42) is one of the 25 terms the "
        "normalization request names explicitly, and ordered replay is the mechanism that makes "
        "the differential observer's host side deterministic (R-HOST-03/04/05, "
        "REQ-HOST-007/008). None of the fault values that path can produce is declared "
        "anywhere, so the host error type cannot be written without inventing variants — which "
        "R-SCOPE-03 prohibits. Because `Fault::Host(HostFault)` (L23813) embeds `HostFault` in "
        "the machine-visible fault taxonomy, the gap propagates into the observation domain "
        "compared under R-REF-05. AMB-08 notices only one instance ('`ReplayTraceExhausted` is "
        "not a variant of the frozen `Fault` enum', req/01-part4 L316) and frames it as a "
        "`Fault`-enum problem; it is a `HostFault`-declaration problem, and it is eight variants "
        "wide, not one."),
      disposition=(
        "REPORTED as BLOCKING; no variant set invented and nothing renamed. T-74 records the "
        "single declaration verbatim and lists all eight undeclared paths plus both unused "
        "declared variants as protected tokens, so no implementation can treat the set as "
        "closed. AMB-08's dependency note is corrected to point at `HostFault` rather than the "
        "`Fault` enum, and a new AMB entry carries the decision. U-14 (error-variant "
        "enumeration) is the owning decision and is now BLOCKING-severity for this type: the "
        "host error enum must be declared before R-HOST-03/04/05 can be implemented or tested."),
      affects=["T-74", "T-42", "T-44", "T-70", "T-41", "T-52"],
      previously=["AMB-08", "U-14", "C-50"],
      decision_needed="Yes — BLOCKING. Declare `HostFault`'s variant set: which of `ReplayTraceExhausted`/`TraceExhausted` and `ReplayCorruption`/`ReplayIdMismatch`/`ReplayDigestMismatch` survive, whether `Io` is `IoError(String)`, and how `HostFault::ReplayCorruption` relates to `Fault::ReplayCorruption`.",
      new_finding=True,
      doc_sites=[
        ("req/01-registry-part4-durability-concurrency.md", 316, "`ReplayTraceExhausted` is not a variant", "AMB-08 dependency note — attributes the gap to the `Fault` enum, not to `HostFault`"),
        ("spec/05-terminology.md", 112, "`HostFault` variants", "listed as 'not enumerated' although L10820 declares two variants and eight are used"),
        ("mod/09-host.md", 38, "ReplayTraceExhausted", "module prose citing an undeclared variant as if it were frozen"),
      ]),
    X(xid="X-68",
      title="`HostFault` denotes a fault NAME in the v1 grammar and a Rust TYPE from turn [18]; `Revoked` denotes a fault name and a `CapabilityError` variant",
      kind="TYPE-ROLE-HOMONYM",
      severity="MAJOR",
      sites=[
        (1949, "**Faults:**", "turn [5]: the v1 grammar `F ::= CapViolation | BudgetExhausted | ScopeViolation | Revoked | HostFault | IsolationBreach` — here `HostFault` and `Revoked` are MEMBERS of `F`, i.e. faults"),
        (10820, "pub enum HostFault {", "turn [18]: `HostFault` becomes a TYPE — the payload of `Fault::Host`"),
        (23813, "Host(HostFault),", "turn [30]: the frozen `Fault` variant that carries the type"),
        (20409, "Revoked,", "turn [28]: `Revoked` becomes a VARIANT of `CapabilityError`, which is itself the payload of `Fault::Capability`"),
        (2024, "IsolationBreach", "turn [5]: `fault(IsolationBreach)` — a member of `F` used as a receipt-mismatch conclusion"),
        (8766, "IsolationBreach", "turn [14]: v0.3 `E-ReceiptMismatch` concludes `Fault(IsolationBreach)`"),
      ],
      statement=(
        "Two identifiers in the fault vocabulary change grammatical role between eras without "
        "retraction. **`HostFault`** is a *member of the fault grammar* `F` at L1949 (turn [5]) "
        "— i.e. it denotes one fault, a sibling of `CapViolation` and `BudgetExhausted` — and "
        "from L10820 (turn [18]) it denotes a *Rust enum type*, the payload of the frozen "
        "`Fault::Host(HostFault)` variant (L23813). Under the first reading `Fault::HostFault` "
        "would be a leaf fault; under the second `HostFault` is a whole sub-taxonomy (and an "
        "undeclared one — X-67). **`Revoked`** is likewise a member of `F` at L1949 and, from "
        "L20409 (turn [28]), a variant of `CapabilityError`, which is the payload of "
        "`Fault::Capability(CapabilityError)` — so `Revoked` moves from the top level of the "
        "taxonomy to two levels down. **`IsolationBreach`** stays a member of `F` (L2024, "
        "L7223) and is used as the conclusion of the *receipt-mismatch* rule (L8766), yet AMB-08 "
        "lists it among the capability-denial names, and it appears in no `Fault` declaration."),
      why_it_matters=(
        "A name that denotes both a fault and a type of faults cannot be compiled, encoded or "
        "compared without picking a level, and the two levels have different canonical "
        "encodings: a leaf fault is one discriminant, a nested enum is a discriminant plus a "
        "payload. R-CALC-06 states the taxonomy as a flat variant list, which matches neither "
        "reading for `HostFault`. This is the same class of defect as X-57 (`Request` used as "
        "five different kinds of thing) and X-01 (`ValidatedPlan` as a type and as a predicate), "
        "and it is invisible to a name-based glossary because the *name* never changes — only "
        "its level in the taxonomy does."),
      disposition=(
        "REPORTED; both readings recorded and neither chosen. T-70 and T-74 carry the v1 "
        "grammar members (`HostFault`, `Revoked`, `CapViolation`, `IsolationBreach`) as "
        "protected tokens with their role stated, and T-74's `forbidden` list bars using "
        "`HostFault` as a fault name. AMB-08's classification of `IsolationBreach` as a "
        "capability-denial name is corrected: the source uses it for receipt mismatch. Joined "
        "to U-08, which must fix the *level* of each name as well as its spelling."),
      affects=["T-74", "T-70", "T-72"],
      previously=["AMB-08", "U-08", "X-57", "X-01"],
      decision_needed="Yes, folded into U-08: for each of `HostFault`, `Revoked` and `IsolationBreach`, state whether it is a leaf fault, a nested error type, or a variant of one — and at which level of the taxonomy it sits.",
      new_finding=True,
      doc_sites=[
        ("req/03-ambiguous.md", 69, "previously also mapped `IsolationBreach`", "AMB-08's reading (a), corrected in place: `IsolationBreach` is the receipt-mismatch fault"),
        ("spec/01-canonical-specification.md", 160, "The frozen fault taxonomy is the Rust `Fault` enum", "R-CALC-06 states a flat variant list that matches neither reading of `HostFault`"),
      ]),
    X(xid="X-69",
      title="Twelve `Fault::` variant paths are used in the frozen source and declared by no `Fault` enum",
      kind="UNDECLARED-VARIANT",
      severity="MAJOR",
      sites=[
        (28373, "is rejected with `Fault::StalePlan`", "turn [36]: the staleness rejection, naming a variant no declaration contains"),
        (941, "Fault::AuthoritySuspended", "turn [3]: capability-denial family"),
        (1018, "Fault::FuelExhausted", "turn [3]: budget family; the declared name is `BudgetExhausted`"),
        (944, "Fault::ScopeViolation", "turn [3]"),
        (3671, "Fault::ScopeViolation", "turn [7]"),
        (5059, "Fault::ScopeViolation", "turn [9]"),
        (6704, "Fault::Revoked", "turn [11]"),
        (6705, "Fault::AncestorRevoked", "turn [11]: a near-synonym of `Revoked` in the same list"),
        (6706, "Fault::Unauthorized", "turn [11]: a third name for the same denial"),
        (937, "Fault::CapabilityRevoked(cref)", "turn [3]: payload-bearing form"),
        (10446, "Fault::CapabilityRevoked", "turn [18]"),
        (5055, "Fault::CapabilityRevoked", "turn [9]"),
        (10447, "CapabilityRevoked", "turn [18]: seven uses in all"),
        (10466, "Fault::ReservedCapacityExceeded", "turn [18]"),
        (10467, "ReservedCapacityExceeded", "turn [18]"),
        (20389, "Fault::CapabilityError(error)", "turn [28]: also X-38/X-66 — a type of the same name exists"),
        (25714, "Fault::NoSuchActor", "turn [32]"),
        (26017, "Fault::UnknownActor", "turn [32]: a second name for the same condition, 303 lines later"),
        (23806, "pub enum Fault {", "the frozen declaration R-CALC-06 cites"),
        (23807, "// ... (previous faults)", "the elision that makes the frozen block non-exhaustive"),
        (26865, "pub enum Fault {", "turn [33]: actor-local declaration, also without any of the twelve"),
      ],
      statement=(
        "Checking every `Fault::` path in L1-42312 against the seven `pub enum Fault` "
        "declarations (L10882, L17788, L18125, L22415, L23319, L23806, L26865) yields TWELVE "
        "distinct variant paths that the source uses and no declaration contains: "
        "`CapabilityRevoked` (7 uses: L937, L3667, L3683, L5055, L5071, L10446, L10447), "
        "`ScopeViolation` (3: L944, L3671, L5059), `CapabilityError` (3: L20389, L20538, "
        "L20790), `ReservedCapacityExceeded` (2: L10466, L10467), `AuthoritySuspended` (L941), "
        "`FuelExhausted` (L1018), `Revoked` (L6704), `AncestorRevoked` (L6705), `Unauthorized` "
        "(L6706), `NoSuchActor` (L25714), `UnknownActor` (L26017) and `StalePlan` (L28373). "
        "The frozen L23806 block elides its own head with `// ... (previous faults)` at L23807, "
        "so it cannot be read as exhaustive; the other six declarations are not elided and do "
        "not contain these names either."),
      why_it_matters=(
        "`Fault` is the machine's terminal failure value, and its identity is what the "
        "differential observer compares (R-REF-05), what `FaultKind` is derived from "
        "(R-CORE-09), and what L26877-L26880 orders as “the same order as enum declaration” — "
        "an ordering that is undefined for a variant no declaration contains. An implementation "
        "cannot construct a `Fault::CapabilityRevoked(cref)` that no declaration admits and a "
        "test cannot assert on one. Worse, several of the twelve are near-synonyms differing "
        "only in spelling (`CapabilityRevoked`/`Revoked`/`AncestorRevoked`/`Unauthorized`, "
        "`NoSuchActor`/`UnknownActor`), so the count of distinct capability-denial faults comes "
        "out as four, nine or twelve depending on which set a reader takes — which is exactly "
        "why C-58 and AMB-08 disagree, and why AMB-08 is graded the single most blocking "
        "ambiguity in the set. The capability-denial families are the set the frozen `Authority` "
        "invariants and the `capcheck`/`scope` obligations turn on."),
      disposition=(
        "REPORTED, not resolved, and nothing renamed or invented. X-64 keeps the `StalePlan` "
        "case individually because it crosses REQ-CALC-014's stated postcondition, and X-38 "
        "keeps the `CapabilityError` case because a separate declared type of that name exists; "
        "this entry is the population-level finding, held apart from both so every affected "
        "record stays traceable. U-08 already owns the `Fault` variant set and has to close all "
        "twelve at once: either the seven declarations are incomplete, in which case the twelve "
        "are added and each near-synonym family resolved to one name, or the twelve uses are "
        "prose errors to be remapped onto declared variants. The source records neither option. "
        "All twelve names are listed in T-70's `protected` so no later pass normalizes one away "
        "by accident."),
      affects=["T-70", "T-02", "T-56", "T-24", "T-27"],
      previously=["C-08", "C-58", "AMB-08", "U-08", "U-13"],
      decision_needed="Yes — owned by U-08, but U-08 as written covers only the declared variant set; it has to be widened to rule on the twelve undeclared paths and on the near-synonym families.",
      new_finding=True,
      doc_sites=[
        ("spec/06-contradictions-ambiguities.md", 74, "Twelve `Fault::` variant paths", "C-59, the row this entry backs"),
        ("spec/06-contradictions-ambiguities.md", 69, "one of twelve (C-59)", "C-54, corrected to point at the population finding"),
        ("req/03-ambiguous.md", 68, "one of twelve such `Fault::` paths", "AMB-08, qualified rather than struck"),
      ]),
    X(xid="X-70",
      title="Theorem 2's proof and the property-test matrix both depend on `Expr::Delegate`, which no `enum Expr` declaration admits",
      kind="UNDECLARED-VARIANT",
      severity="MAJOR",
      sites=[
        (26056, "Theorem 2: No Authority Amplification", "turn [32]: the theorem whose proof depends on the undeclared node"),
        (26057, "ExplicitlyDelegatedAuthority", "turn [32]: the boxed statement — authority may grow only by explicit delegation"),
        (26058, "Authority can only cross boundaries via `Expr::Delegate`", "turn [32]: the proof's ONLY authority-crossing mechanism"),
        (26078, "| **C: Delegation** | `Expr::Delegate` |", "turn [32]: property-test matrix row C, three invariants asserted on the node"),
        (25989, "Expr::Delegate {", "turn [32]: the only place its fields are given"),
        (25991, "constraint: Constraint", "turn [32]: field 2 of 2 — a T-12 `Constraint`, the same field `Attenuate` carries"),
        (12145, "pub enum Expr {", "turn [21]: the frozen AST, twelve constructors, no `Delegate`"),
        (20702, "pub enum Expr {", "turn [28]: `Var, Lit, Prim, If, Seq, Lambda, Call, Attenuate` — no `Delegate`"),
        (24062, "explicit `Delegate` operations", "turn [32]: prose use"),
        (25700, "Expr::Delegate", "turn [32]: prose use"),
      ],
      statement=(
        "X-29, AMB-11 and C-16 all record the underlying fact: `Expr::Delegate` is used by the "
        "frozen source and appears in none of the five `pub enum Expr` declarations (L12145 — "
        "twelve constructors, L14030, L14413, L20295, L20702). This entry records what the sweep "
        "found beyond that, which none of the three states: TWO NORMATIVE ARTIFACTS DEPEND ON "
        "THE UNDECLARED NODE. Theorem 2 (No Authority Amplification, L26056-26058) is proved by "
        "exhaustion over the ways authority can cross a boundary — “Ordinary `Send` operations "
        "pass through `marshal()`, which strictly rejects `Value::Capability`. Authority can only "
        "cross boundaries via `Expr::Delegate`, which invokes `CapabilityKernel::derive`, "
        "guaranteeing `child <= parent`” — so the node is the proof's single non-trivial case. "
        "The property-test matrix at L26078 makes row C (“Delegation”) assert three invariants on "
        "it: kernel derivation called exactly once, `child <= parent`, and a revoked parent "
        "cannot delegate. The sweep also found two further use sites that AMB-11 does not list "
        "(L26058, L26078) and one field detail: `Delegate` carries `constraint: Constraint` "
        "(L25991), the same field `Expr::Attenuate` carries, so attenuation is declared and "
        "delegation is not despite the two sharing a shape."),
      why_it_matters=(
        "A theorem proved by exhaustion is only as sound as its case list, and here one case "
        "names a constructor the frozen AST does not admit. Two consequences follow, and they "
        "pull in opposite directions. If `Delegate` is not constructible, Theorem 2's proof has "
        "an empty case and its conclusion holds only because authority then cannot cross at all "
        "— a stronger claim than the theorem states, and one that would make row C of the test "
        "matrix untestable. If `Delegate` IS constructible, then the frozen twelve-constructor "
        "`Expr` is incomplete, and every obligation quantified over plans — R-VALID-03, "
        "R-CAPCHK-04, and the boxed `ExternalEffect(E) ⇒ ValidatedPlan(P)` theorem (X-46) — is "
        "quantified over an AST missing a node that transfers authority. Because L-04 (CapRef ≠ "
        "Authority) and L-05 (LLM output ≠ Authority) make authority transfer the one operation "
        "that must not be inferred, an authority-carrying AST node that exists only in a proof "
        "sketch is the single worst place for a declaration gap to be. This is a "
        "Verification-versus-Specification defect in the sense L-08 draws: the proof text asserts "
        "a property of a surface the specification does not declare."),
      disposition=(
        "REPORTED, not resolved, nothing renamed and no constructor invented. X-29 keeps the "
        "declaration-gap finding and gains the two additional use sites; AMB-11 keeps the "
        "two-readings analysis and its correction to `spec/01` L334; this entry adds only the "
        "dependence of Theorem 2 and of test-matrix row C, which is what makes the gap blocking "
        "rather than cosmetic. `Expr::Delegate` is already protected in T-30 and T-15, so it "
        "cannot be normalized away; `Value::DelegatedCapability` (X-74) is added to T-31's "
        "`protected` for the same reason. The decision — is `Delegate` a thirteenth constructor, "
        "or is Theorem 2's case list to be restated without it? — is not recorded in the source "
        "and is escalated to U-02, which already owns the undefined-name family."),
      affects=["T-30", "T-15", "T-31", "T-12", "T-13", "T-10"],
      previously=["C-60", "X-29", "AMB-11", "C-16", "U-02"],
      decision_needed="Yes — owned by U-02 as extended by this entry: does `Expr::Delegate` become a declared thirteenth constructor (freezing the L25989-25992 field set), or must Theorem 2's proof and test-matrix row C be restated without it?",
      new_finding=True,
      doc_sites=[
        ("spec/06-contradictions-ambiguities.md", 75, "Theorem 2's proof and the property-test matrix", "C-60, rewritten from a duplicate of X-29 to the theorem-dependency finding"),
        ("req/03-ambiguous.md", 91, "`Expr::Delegate` is absent from the frozen AST", "AMB-11, which already records the declaration gap and is not superseded"),
      ]),
    X(xid="X-71",
      title="`MachineEvent` is declared eight times and used with eight variant paths declared by none of them",
      kind="UNDECLARED-VARIANT",
      severity="MAJOR",
      sites=[
        (14697, "pub enum MachineEvent {", "turn [23]: first declaration"),
        (15958, "pub enum MachineEvent {", "turn [24]"),
        (17588, "pub enum MachineEvent {", "turn [25]: adds `ApplyFunction`"),
        (18104, "pub enum MachineEvent {", "turn [26]"),
        (18631, "pub enum MachineEvent {", "turn [26]"),
        (20318, "pub enum MachineEvent {", "turn [28]: adds `EnterAttenuate`, `DeriveCapability`, `Fault`"),
        (20724, "pub enum MachineEvent {", "turn [28]"),
        (22002, "pub enum MachineEvent {", "turn [29]: adds `EffectIssued`, `EffectCompleted`"),
        (22003, "// ...", "the elision that makes the last declaration non-exhaustive"),
        (21483, "MachineEvent::EnterRequest", "turn [29]: used, never declared"),
        (21536, "MachineEvent::BeginRequestTarget", "turn [29]: used, never declared"),
        (21645, "MachineEvent::BeginRequestArgument", "turn [29]: used, never declared"),
        (25740, "MachineEvent::Blocked", "turn [32]: the declared name is `Block`"),
        (25668, "MachineEvent::Spawned", "turn [32]: never declared"),
        (25966, "MachineEvent::ActorSpawned", "turn [32]: a second name for `Spawned`, with `{ parent, child }`"),
        (25728, "MachineEvent::Sent", "turn [32]: never declared"),
        (26027, "MachineEvent::MessageSent", "turn [32]: a second name for `Sent`, with `{ from, to }`"),
      ],
      statement=(
        "`MachineEvent` has EIGHT declarations (L14697, L15958, L17588, L18104, L18631, L20318, "
        "L20724, L22002), the last with its head elided as `// ...` at L22003. Beyond the drift "
        "between those declarations, eight further variant paths are used and declared by none "
        "of them: `EnterRequest` (L21483, L23380), `BeginRequestTarget` (L21536, L23398), "
        "`BeginRequestArgument` (L21645, L23426), `Blocked` (L25740, L26038), `Spawned` "
        "(L25668), `ActorSpawned` (L25966), `Sent` (L25728) and `MessageSent` (L26027). Two of "
        "the eight are second names for a concept the others also name: `Blocked` against the "
        "declared `Block`, and `Spawned`/`ActorSpawned` and `Sent`/`MessageSent` as pairs used "
        "in different turns of the same document."),
      why_it_matters=(
        "This is the vocabulary the trace is made of, so it decides three things at once: what "
        "the WAL records (T-45), what the differential observer compares between two "
        "implementations (R-REF-05), and what a conformance fixture may assert. If one "
        "implementation emits `Spawned` and another `ActorSpawned` for the same transition, the "
        "differential harness reports a divergence that is a naming artifact rather than a "
        "semantic one — the same failure mode as X-21's `Running`/`Active`, but on the event "
        "stream instead of the actor state, and there are four such pairs here rather than one. "
        "`Blocked` is worse than cosmetic because `Blocked` is also an `ActorStatus` variant "
        "(X-74) and a `StepResult` variant (X-73), so a reader of an event log cannot tell "
        "which layer the event came from. `EffectIssued`/`EffectCompleted` ARE declared here "
        "(L22005, L22010) with `{ id, digest }`, which is what makes L-06 (EffectIssued ≠ "
        "EffectCompleted) enforceable at all — so the enum matters to the request's own "
        "required distinctions, not only to the trace."),
      disposition=(
        "REPORTED, not resolved, and `MachineEvent` is filed as T-75 — it had no term of record "
        "at all before this sweep, despite being the event vocabulary the WAL and the "
        "differential comparison are built on. The eight declarations are additive across turns "
        "(each introduces the events for that turn's feature), so a union reading is available; "
        "but the four duplicate names have to be resolved to one name each by a single source "
        "ruling, and no such ruling exists. All eight undeclared paths are listed in T-75's "
        "`protected` so none is normalized away by a later pass. Nothing is renamed."),
      affects=["T-75", "T-47", "T-45", "T-70", "T-35"],
      previously=["U-28"],
      decision_needed="Yes — `spec/09` U-28: is the vocabulary the union of all eight declarations or only the last, which name governs each duplicate pair, and are the three `*Request*` events declared or struck?",
      new_finding=True,
      doc_sites=[
        ("spec/06-contradictions-ambiguities.md", 76, "`MachineEvent` is declared eight times", "C-61, the row this entry backs"),
        ("spec/09-unresolved-decisions.md", 146,
         "### U-28 — Which `MachineEvent` names govern",
         "the decision this entry escalates to; added by the same sweep"),
        ("req/03-ambiguous.md", 277,
         "### AMB-36 — `MachineEvent` is declared eight times",
         "the ambiguity row this entry backs"),
      ]),
    X(xid="X-72",
      title="`CanonicalError` is declared seven times in four variant sets and five payload shapes, with the same variant names at different arities",
      kind="DIVERGENT-SHAPE",
      severity="MAJOR",
      sites=[
        (29188, "pub enum CanonicalError {", "turn [38]: shape (i), five unit variants"),
        (29189, "InvalidVersion,", "turn [38]: a UNIT variant"),
        (29968, "pub enum CanonicalError {", "turn [41]: shape (ii), seven variants, two respelled"),
        (29973, "PayloadTooShort,", "turn [41]: where the others say `UnexpectedEof`"),
        (29975, "Utf8Error,", "turn [41]: where the others say `InvalidUtf8`"),
        (30661, "pub enum CanonicalError {", "turn [41]: shape (iii), nine struct variants"),
        (30662, "InvalidVersion { expected: u8, found: u8 }", "turn [41]: the SAME name, now payload-bearing"),
        (30666, "InvalidUtf8,", "turn [41]: unit, alongside payload-bearing siblings"),
        (30670, "InvalidBoolValue { found: u8 }", "turn [41]: only in this shape"),
        (34994, "pub enum CanonicalError {", "turn [47]: shape (iv), head elided"),
        (34996, "DuplicateMapKey", "turn [47]: “NEW: Enforces strict injectivity”"),
        (32086, "LengthMismatch { expected: usize, found: usize },",
          "turn [43]: shape (iii)'s `expected: u32` is `usize` here"),
        (32962, "LengthMismatch { expected: usize, found: usize },",
          "turn [45]: `usize` again"),
        (33302, "LengthMismatch { expected: usize, found: usize },",
          "turn [45]: `usize` a third time"),
      ],
      statement=(
        "`CanonicalError` has SEVEN declarations (L29188, L29968, L30661, L32083, L32959, "
        "L33299, L34994) in four materially different shapes. Shape (i) L29188 has five unit "
        "variants. Shape (ii) L29968 has seven and respells two of them — `Utf8Error` where the "
        "others say `InvalidUtf8`, `PayloadTooShort` where the others say `UnexpectedEof` — and "
        "adds `LengthOverflow`, which shape (i) lacks entirely. Shape (iii) L30661 turns six of "
        "the same names into payload-bearing struct variants (`InvalidVersion { expected: u8, "
        "found: u8 }`, `InvalidTypeTag { expected: u8, found: u8 }`, `LengthMismatch { expected: "
        "u32, found: usize }`, `TrailingBytes { count: usize }`, `InvalidDiscriminant { found: "
        "u8 }`, `InvalidBoolValue { found: u8 }`). Shape (iv) L34994 elides its head as `// ... "
        "previous variants` and adds `DuplicateMapKey`."
        " The field-set sweep behind X-83/X-86 separates one further distinction inside shape (iii): "
        "`LengthMismatch` carries `expected: u32` at L30664 (turn [41]) and `expected: usize` at L32086 "
        "(turn [43]), L32962 and L33302 (turn [45]) — four variant SETS but five payload shapes. The "
        "width that changes is the one `LengthOverflow` exists to police, so the turn-[41] and turn-[43] "
        "decoders disagree about what counts as an impossible length; the shape (iii) description above "
        "quotes the `u32` form and does not otherwise distinguish L30661 from L32083/L32959/L33299."),
      why_it_matters=(
        "This is the `Err` arm of every `canonical_serialize` and `canonical_deserialize`, so it "
        "is what reports every violation of the frozen envelope and payload rules — the same "
        "path on which X-50 (the envelope wire format) is already BLOCKING. The arity "
        "divergence is not cosmetic: `InvalidVersion` as a unit variant cannot carry the "
        "expected and found version bytes, so a decoder written against L29188 loses the "
        "diagnostic L30661 requires, and a test written against L30661 does not compile against "
        "L29188. Two spellings for one condition (`InvalidUtf8`/`Utf8Error`, "
        "`UnexpectedEof`/`PayloadTooShort`) is X-21's `Running`/`Active` pattern on the error "
        "channel, where a fixture matching one spelling silently passes on the other — and "
        "canonicalization is precisely where a silent pass becomes a consensus fork, because "
        "two nodes that disagree on which errors are fatal disagree on the digest. "
        "`DuplicateMapKey` is the only variant that enforces map injectivity, and it exists in "
        "one of four shapes, so whether canonical encoding rejects duplicate keys at all "
        "depends on which declaration an implementer reads."),
      disposition=(
        "REPORTED, not resolved; `CanonicalError` is filed as T-76 with all four shapes given "
        "verbatim in `shape`/`supersedes` and every divergent spelling listed in `protected` so "
        "none is normalized away. L30661 is the most informative and the latest non-elided "
        "declaration, but nominating it would drop `PayloadTooShort` and `Utf8Error` from the "
        "record, so no shape is chosen here. U-08 governs `Fault` only; `CanonicalError` needs "
        "its own ruling before any canonical-codec test can be written, and that ruling has to "
        "state whether the payload-bearing shape (iii) supersedes (i) and (ii) or whether the "
        "unit variants remain legal."),
      affects=["T-76", "T-62", "T-63", "T-47", "T-31"],
      previously=["C-47", "C-48", "C-49", "U-29", "U-14"],
      decision_needed="Yes — `spec/09` U-29: which of the four shapes governs, do the unit variants of shapes (i)/(ii) survive shape (iii)'s payload-bearing forms, and which spelling governs each respelled pair?",
      new_finding=True,
      doc_sites=[
        ("spec/06-contradictions-ambiguities.md", 77, "`CanonicalError` is declared seven times", "C-62, the row this entry backs"),
        ("spec/09-unresolved-decisions.md", 153,
         "### U-29 — Which `CanonicalError` shape governs",
         "the decision this entry escalates to; added by the same sweep"),
        ("req/03-ambiguous.md", 285,
         "### AMB-37 — `CanonicalError` is declared seven times",
         "the ambiguity row this entry backs"),
      ]),
    X(xid="X-73",
      title="`StepResult` is two disjoint enums — the CEK machine's and the actor scheduler's — sharing one name",
      kind="TYPE-HOMONYM",
      severity="MAJOR",
      sites=[
        (1006, "pub enum StepResult {", "turn [3]: the CEK machine's step outcome"),
        (1007, "Continue,", "turn [3]: machine variant 1"),
        (1010, "YieldToHost(Effect),", "turn [3]: carries a T-20 `Effect`"),
        (9586, "pub enum StepResult {", "turn [17]: the actor scheduler's step outcome"),
        (9587, "Progressed,", "turn [17]: scheduler variant 1"),
        (9588, "Blocked(ActorId),", "turn [17]: carries an identity the machine's variants never do"),
        (9591, "Faulted(ActorId, Fault),", "turn [17]: not an alias of the machine's `Fault(Fault)`"),
        (9592, "NoRunnableActors,", "turn [17]: meaningful only at scheduler level"),
        (10397, "pub enum StepResult {", "turn [18]: scheduler family restated"),
        (10947, "pub enum StepResult {", "turn [18]: scheduler family restated"),
      ],
      statement=(
        "Two enums named `StepResult` have no variant in common. L1006 (turn [3], the CEK "
        "machine) declares `Continue | Halt(Value) | Fault(Fault) | YieldToHost(Effect)` — one "
        "reduction of one actor, carrying no identity. L9586 (turn [17], the actor scheduler; "
        "restated at L10397 and L10947) declares `Progressed | Blocked(ActorId) | "
        "Pending(ActorId, EffectRequest) | Halted(ActorId, Value) | Faulted(ActorId, Fault) | "
        "NoRunnableActors` — every variant carries an `ActorId`, and `Pending` carries a T-28 "
        "`EffectRequest`. They are not successive versions of one type; they are the step "
        "outcome of two different layers, and neither declaration mentions the other."),
      why_it_matters=(
        "Both are returned by a method an implementer will call `step`, and a reader of any "
        "single turn cannot tell which is meant. Turn [3] says a step yields "
        "`YieldToHost(Effect)`; turn [17] says a step yields `Pending(ActorId, EffectRequest)` "
        "— and `Effect` (T-16) versus `EffectRequest` (T-17) is one of the distinctions this "
        "normalization request explicitly requires to be kept separate, so the homonymy puts "
        "that distinction at risk from the type name itself. The scheduler's `Faulted(ActorId, "
        "Fault)` and the machine's `Fault(Fault)` are likewise different types, not aliases, and "
        "X-23 already records `Faulted` versus `Fault` as a live split inside `RunState`. "
        "Prose saying “the step returned Blocked” is ambiguous between three enums "
        "(`StepResult`, `ActorStatus`, `RunState`), which is the ambiguity that makes X-71's "
        "`MachineEvent::Blocked` undiagnosable from a log."),
      disposition=(
        "REPORTED, not resolved; recorded as T-77 with both shapes given verbatim. Renaming "
        "either enum would violate the no-silent-rename constraint, and unlike "
        "`Observation`/`HostObservation` (X-06) the source provides no second name to adopt — so "
        "the homonymy stands and is disambiguated by layer in every dictionary entry that "
        "mentions it (T-70 for the machine, T-35 for the scheduler). T-77's `forbidden` list "
        "bans the unqualified phrase “step result” for exactly this reason."),
      affects=["T-77", "T-70", "T-35", "T-36", "T-17"],
      previously=["C-63", "X-23", "U-26"],
      decision_needed="Yes — `spec/09` U-26: which layer keeps the name `StepResult` and what the other layer's step outcome is called. The source offers no second name, so this cannot be settled by citation alone.",
      new_finding=True,
      doc_sites=[
        ("spec/06-contradictions-ambiguities.md", 78, "`StepResult` is two disjoint enums", "C-63, the row this entry backs"),
        ("spec/09-unresolved-decisions.md", 132,
         "### U-26 — Which layer owns the name `StepResult`?",
         "the decision this entry escalates to; added by the same sweep"),
        ("req/03-ambiguous.md", 293,
         "### AMB-38 — `StepResult` names two disjoint enums",
         "the ambiguity row this entry backs"),
      ]),
    X(xid="X-74",
      title="`ActorStatus` is declared seven times in three shapes; X-21 records only two declarations",
      kind="DIVERGENT-SHAPE",
      severity="MAJOR",
      sites=[
        (9411, "pub enum ActorStatus {", "turn [17]: shape (i)"),
        (10346, "pub enum ActorStatus {", "turn [18]: shape (i) restated"),
        (10866, "pub enum ActorStatus {", "turn [18]"),
        (21234, "pub enum ActorStatus {", "turn [29]: shape (ii), a three-field `Pending`"),
        (21240, "continuation: Continuation,", "turn [29]: the continuation INSIDE `Pending`"),
        (21244, "Blocked(Continuation),", "turn [29]: and also inside `Blocked`"),
        (23306, "pub enum ActorStatus {", "turn [30]: shape (iii), `continuation` dropped"),
        (23793, "pub enum ActorStatus {", "turn [30]: shape (iii) restated"),
      ],
      statement=(
        "X-21 records `ActorStatus` as declared twice (L9411 and L10346). A full sweep finds "
        "SEVEN declarations — L9411, L10346, L10866, L21234, L23306, L23793 and the turn-[20] "
        "restatement at L10866 — in THREE distinct shapes. Shape (i), L9411/L10346: "
        "`Pending(PendingEffect), Blocked(Continuation)` — a tuple `Pending` and a "
        "payload-bearing `Blocked`. Shape (ii), L21234: `Pending { effect: EffectRequest, "
        "continuation: Continuation, reservation: ReservedCapacity }, Blocked(Continuation)` — a "
        "three-field struct `Pending`. Shape (iii), L23306/L23793: `Pending { effect: "
        "EffectRequest, reservation: ReservedCapacity }, Blocked` — `continuation` dropped from "
        "`Pending` and `Blocked` reduced to a unit variant. The `Continuation` payload therefore "
        "moves: inside `Blocked` in shapes (i) and (ii), inside `Pending` in shape (ii) as well, "
        "and absent from both in shape (iii)."),
      why_it_matters=(
        "`ActorStatus` is the state that decides whether an actor is resumable, and the location "
        "of its `Continuation` payload is exactly what a scheduler needs in order to resume it. "
        "Shape (iii) carries no `Continuation` at all, so an actor in `Pending { effect, "
        "reservation }` cannot be resumed from its own status — the continuation has to live "
        "somewhere else — `ActorState.eval.continuation` (T-37, T-32) — and the source never says "
        "where. That is a semantic gap, "
        "not a naming one, and it is downstream of the `Running`/`Active` split X-21 already "
        "records: an implementer who normalizes the name without also picking a shape gets a "
        "status type that cannot resume its own actors, and every replay test built on it fails "
        "for a reason the naming fix appears to have solved. The seven-declaration count also "
        "bears on X-21's disposition, which was written against two and so understates how much "
        "of the source has to be reconciled."),
      disposition=(
        "REPORTED, not resolved, with X-21 kept intact: X-21's `Running`/`Active` finding is "
        "correct and stands, and this entry corrects its population count rather than "
        "superseding it, because the two findings are about different things (naming versus "
        "shape) and merging them would lose one. T-35's note is updated in place to say seven "
        "declarations in three shapes and to cross-link both entries. No shape is nominated — "
        "shapes (i) to (iii) are successive turns' views and the source gives no precedence rule "
        "for `ActorStatus` (U-08 covers `Fault` only). All three shapes are given verbatim in "
        "T-35's `supersedes`/`shape` so none is lost."),
      affects=["T-35", "T-37", "T-32", "T-17", "T-26", "T-77"],
      previously=["C-64", "X-21", "U-27"],
      decision_needed="Yes — `spec/09` U-27: which shape governs, and where shape (iii)'s continuation lives — the actor table, the WAL, or a `ContinuationFrame`.",
      new_finding=True,
      doc_sites=[
        ("spec/06-contradictions-ambiguities.md", 79, "`ActorStatus` is declared seven times", "C-64, the row this entry backs"),
        ("spec/09-unresolved-decisions.md", 139,
         "### U-27 — Which `ActorStatus` shape governs",
         "the decision this entry escalates to; added by the same sweep"),
        ("req/03-ambiguous.md", 301,
         "### AMB-39 — `ActorStatus` is declared seven times",
         "the ambiguity row this entry backs"),
      ]),
    X(xid="X-75",
      title="Residual used-but-undeclared variant paths across five more enums, and one variant silently dropped",
      kind="UNDECLARED-VARIANT",
      severity="MINOR",
      sites=[
        (1027, "Value::Null", "turn [3]: the declared sets have `Unit`, not `Null`"),
        (12283, "pub enum Value {", "turn [21]: the first `Value` declaration"),
        (25995, "Value::DelegatedCapability", "turn [32]: in no `Value` declaration"),
        (26000, "DelegatedCapability", "turn [32]: second use, five lines later"),
        (25694, "MarshalFault::CorruptedPayload", "turn [32]: in neither `MarshalFault` declaration (X-65)"),
        (985, "pub enum ControlFrame {", "turn [3]: the only declaration, head elided at L989"),
        (986, "Vec<PlanIR>", "turn [3]: `PlanIR` is declared nowhere"),
        (987, "FuncRef", "turn [3]: `FuncRef` is declared nowhere"),
        (988, "EffectSignature", "turn [3]: `EffectSignature` is declared nowhere"),
        (1031, "ControlFrame::ReduceIR", "turn [3]: used in the machine's own `match`"),
        (1282, "ControlFrame::ResumeWithResult", "turn [3]: used, never declared"),
        (1092, "pub enum TransitionEvent {", "turn [3]: the only declaration"),
        (1055, "TransitionEvent::ActorSpawned", "turn [3]: used 37 lines BEFORE the enum that should declare it"),
        (24299, "pub enum RunState {", "turn [31]: declares `NotRunnable`"),
        (24300, "NotRunnable,", "turn [31]: the variant that disappears"),
        (25526, "pub enum RunState {", "turn [32]: re-declared without `NotRunnable`, no supersession note"),
      ],
      statement=(
        "The same sweep, on the enums too small for a row of their own: (a) `Value::Null` at "
        "L1027, where every declared `Value` set has `Unit` and not `Null` (L12283 onward); "
        "(b) `Value::DelegatedCapability` at L25995 and L26000, in no `Value` declaration, the "
        "declared capability variant being `Capability(Box<CapabilityToken>)`; (c) "
        "`MarshalFault::CorruptedPayload` at L25694, in neither `MarshalFault` declaration "
        "(L10846/L25983 versus L30645, already X-65); (d) `ControlFrame::ReduceIR` at L1031 and "
        "matched at L1035, plus `ControlFrame::ResumeWithResult` at L1282, against the single "
        "elided declaration at L985; (e) `TransitionEvent::ActorSpawned` at L1055, which precedes "
        "the only `TransitionEvent` declaration at L1092; and (f) `RunState::NotRunnable`, "
        "declared at L24300 and silently absent from the L25526 re-declaration."),
      why_it_matters=(
        "Each is individually small, but they are the same defect class as X-69 to X-71 and they "
        "sit on load-bearing paths. `Value::Null` versus `Value::Unit` is the canonical encoding "
        "of the empty value, which X-50's envelope format and X-72's `CanonicalError` both turn "
        "on — and C-49 already records that the frozen discriminant table lists 5 of 8 variants, "
        "so the empty value's tag is not pinned down from either direction. "
        "`Value::DelegatedCapability` is the value form of the delegation mechanism whose AST "
        "node is also undeclared (X-70), so delegation is missing at both layers, and "
        "`MarshalFault::CapabilityRequiresDelegation` (L25984) is the error for it — a fault "
        "whose success case cannot be represented. `ControlFrame`'s three declared variants "
        "reference `PlanIR`, `FuncRef` and `EffectSignature`, none of which is declared "
        "anywhere, so the control stack cannot be constructed from the frozen text at all, and "
        "its two undeclared variants are used in the machine's own `match` at L1031-L1035. "
        "`RunState::NotRunnable` vanishing between L24300 and L25526 with no supersession note "
        "is the R-SCOPE-03 pattern occurring inside the frozen source itself."),
      disposition=(
        "REPORTED as one grouped finding so a single ruling can close it; nothing renamed. "
        "`ControlFrame` is filed as T-78 with `ReduceIR` and `ResumeWithResult` protected and "
        "its three undeclared payload types named in the note. `Value::Null` and "
        "`Value::DelegatedCapability` are added to T-31's `protected` as source-used spellings "
        "rather than normalized to `Unit`/`Capability`; `MarshalFault::CorruptedPayload` is "
        "added to T-73's. `TransitionEvent` gets no term of its own — it is declared once "
        "(L1092) and its use-before-declaration is recorded in this entry's sites — while the "
        "dropped `RunState::NotRunnable` is added to T-36's `protected` with both declarations cited."),
      affects=["T-31", "T-78", "T-73", "T-36", "T-08", "T-76"],
      previously=["C-65", "X-65", "X-66", "C-49", "U-02", "U-09"],
      decision_needed="Only in part: `NotRunnable`'s removal and `Null` versus `Unit` need a ruling; the rest follow from the X-69/X-70/X-72 rulings.",
      new_finding=True,
      doc_sites=[
        ("spec/06-contradictions-ambiguities.md", 80, "Residual used-but-undeclared variant paths", "C-65, the row this entry backs"),
      ]),

    X(xid="X-76",
      title="`MarshalledValue` is declared with a `Value` payload three times and a `Vec<u8>` payload twice, and both payloads have frozen API",
      kind="DIVERGENT-SHAPE",
      severity="MAJOR",
      sites=[
        (9925, "pub struct MarshalledValue(Value);", "turn [17]: the boundary carries an in-memory value"),
        (10828, "pub struct MarshalledValue(Value);", "turn [18]: same payload"),
        (10831, "pub(crate) fn new(v: Value) -> Self { Self(v) }", "turn [18]: frozen constructor — takes a `Value`"),
        (10832, "pub fn into_inner(self) -> Value { self.0 }", "turn [18]: frozen accessor — returns a `Value`; impossible over a byte payload"),
        (24765, "pub struct MarshalledValue(Value);", "turn [31]: the `Value` payload survives into the scheduler era"),
        (25683, "pub struct MarshalledValue(pub Vec<u8>); // Canonical serialized bytes", "turn [32]: payload becomes bytes, and is declared PUBLIC"),
        (25685, "pub fn marshal_value(v: &Value) -> Result<MarshalledValue, MarshalFault>", "turn [32]: frozen signature"),
        (25690, "Ok(MarshalledValue(canonical_serialize(v)))", "turn [32]: constructed from canonical bytes, not from a value"),
        (25980, "// The MarshalledValue is an opaque, canonical byte representation.", "turn [32]: 'opaque' — the payload at L25683 is `pub`"),
        (25981, "pub struct MarshalledValue(Vec<u8>);", "turn [32]: bytes again, this time private"),
      ],
      statement=(
        "The type that crosses the actor-isolation boundary is declared five times with two "
        "incompatible payloads: `MarshalledValue(Value)` at L9925 (turn [17]), L10828 (turn [18]) "
        "and L24765 (turn [31]); `MarshalledValue(pub Vec<u8>)` at L25683 and "
        "`MarshalledValue(Vec<u8>)` at L25981 (both turn [32]). Each payload carries frozen API "
        "that the other cannot satisfy: the `Value` form has `new(v: Value)` (L10831) and "
        "`into_inner(self) -> Value` (L10832); the byte form is built by "
        "`MarshalledValue(canonical_serialize(v))` (L25690). Visibility also disagrees — L25683 "
        "makes the payload `pub` while L25980, three lines above the identical declaration at "
        "L25981, calls the type 'opaque'. No supersession note connects the eras."),
      why_it_matters=(
        "`MarshalledValue` is the element type of `Mailbox` (T-39) and the payload of "
        "`ActorState.mailbox`, so this decides whether inter-actor communication transports "
        "values or canonical bytes — and the two answers have different security content. If the "
        "payload is a `Value`, the capability scan `contains_capability` (L25687) runs on the "
        "object being sent; if it is bytes, the scan runs on a value that is then re-serialized, "
        "and R-MARSHAL-01's 'no CapRef inside a marshalled value' is a claim about a decoding "
        "step the spec never freezes. `into_inner() -> Value` is also the accessor an actor would "
        "use to read a delivered message: over bytes it does not type-check, so the frozen API of "
        "turn [18] and the frozen payload of turn [32] cannot both be implemented. T-39's note "
        "records that 'no canonical byte encoding is frozen for Mailbox (C-15, U-02)' — the "
        "turn-[32] declarations assert one, which is a further reason this needs a ruling rather "
        "than a silent reading."),
      disposition=(
        "REPORTED; nothing renamed and neither payload struck. Filed as T-79 with all five "
        "declarations and both APIs protected verbatim (`Value`, `Vec<u8>`, `pub Vec<u8>`, "
        "`new`, `into_inner`, `marshal_value`, `canonical_serialize`, `contains_capability`), so "
        "a ruling can pick a payload without any earlier text being rewritten. T-39's gloss "
        "('canonical bytes transport') is left in place and cross-referenced from T-79's note "
        "rather than edited, because it is itself evidence of the turn-[32] reading."),
      affects=["T-79", "T-39", "T-31", "T-37", "T-62", "T-73"],
      previously=["C-15", "U-02", "X-65", "X-50"],
      decision_needed=(
        "Which payload is `MarshalledValue`'s — `Value` (turns [17]-[31], with `new`/"
        "`into_inner`) or `Vec<u8>` (turn [32], with `canonical_serialize`)? And is the payload "
        "`pub` (L25683) or private/'opaque' (L25980-L25981)?"),
      new_finding=True,
      doc_sites=[
        ("spec/06-contradictions-ambiguities.md", 81, "| C-66 | `MarshalledValue`'s payload is `Value`",
         "C-66, the contradictions-register row for this finding"),
        ("spec/09-unresolved-decisions.md", 162, "### U-30 — Which payload does `MarshalledValue` carry",
         "U-30, the decision this finding needs"),
        ("term/00-overview.md", 175, "| `term/_terms.py T-79…T-81, N-28` |",
         "the §6 row recording T-79's creation"),
        ("README.md", 113, "(`X-01`…`X-87`, of which 4 are BLOCKING)",
         "the README's collision-register count, updated by this pass"),
      ]),
    X(xid="X-77",
      title="`Authority` has seven declarations in six field sets and changes denotation, while `Constraint` is declared twice with `Authority`'s own two shapes",
      kind="DIVERGENT-SHAPE",
      severity="MAJOR",
      sites=[
        (488, "struct Authority {", "turn [2]: a revocation NODE — parent, state, rights"),
        (489, "parent: Option<AuthorityId>,", "turn [2]: `AuthorityId` is declared nowhere (X-84)"),
        (490, "state: RevocationState,", "turn [2]: `RevocationState` is declared nowhere (X-84)"),
        (491, "rights: Rights,", "turn [2]: `Rights` is declared nowhere (X-84)"),
        (485, "attenuation: Constraint,", "turn [2]: `Constraint` used nine turns before its first declaration"),
        (918, "pub(crate) struct Authority {", "turn [3]: the node again, `parent` re-typed to `Option<CapRef>`"),
        (3591, "pub struct Authority {", "turn [7]: a PERMISSION SET — ops, scope, params, resources, lifetime"),
        (4360, "pub struct Authority {", "turn [8]: the same five fields with abstract component types (`OperationSet`, `Scope`, `ParamConstraint`)"),
        (4979, "pub struct Authority {", "turn [9]: back to the concrete `HashSet` component types"),
        (5368, "pub struct Authority {", "turn [9]: a MERGED form — five fields plus `id` and `parent`"),
        (5370, "pub ops: HashSet<Operation>,", "turn [9]: `Operation`, not `Op`; declared nowhere (X-84)"),
        (6501, "pub struct Authority<S, Q, R, L> {", "turn [11]: a MAP form — one field, `ops: HashMap<Op, OpAuthority<S,Q,R,L>>`"),
        (6535, "/// Constraint: distinct from Authority. Represents a narrowing request.", "turn [11]: the doc comment"),
        (6536, "pub struct Constraint<S, Q, R, L> {", "turn [11]: whose body is character-for-character `Authority`'s at L6501-L6503"),
        (6686, "pub struct Constraint {", "turn [11]: a second `Constraint`, five fields — the shape `Authority` has at L4360"),
        (6688, "pub scope: ScopeConstraint,", "turn [11]: `ScopeConstraint`, where `Authority` says `Scope`; declared nowhere (X-84)"),
        (3649, "pub(crate) struct RuntimeAuthority {", "turn [7]: the NODE under a second name — authority, live, parent"),
        (9702, "pub(crate) struct AuthorityNode {", "turn [17]: the NODE under a third name — the same three fields plus `generation`"),
      ],
      statement=(
        "`Authority` is declared seven times (L488, L918, L3591, L4360, L4979, L5368, L6501) in "
        "SIX distinct field sets, and its denotation changes: in turns [2] and [3] it is a node "
        "of the revocation tree (`parent`, `state`, `rights`); from turn [7] it is a set of "
        "permissions (`ops`, `scope`, `params`, `resources`, `lifetime`), spelled with concrete "
        "`HashSet` types at L3591/L4979, with abstract component types at L4360, and merged with "
        "the node's `id`/`parent` at L5368; at L6501 it becomes a one-field map from `Op` to "
        "`OpAuthority`. Its component type names drift with it — `Op`/`Operation`, "
        "`Predicate`/`ParamConstraint`/`ParamPredicate`, `Resources`/`ResourceLimits`, "
        "`HashSet<Target>`/`Scope`. `Constraint` is declared twice in the SAME turn: at L6536 "
        "with a body character-for-character identical to `Authority`'s at L6501, under a doc "
        "comment reading 'Constraint: distinct from Authority'; and at L6686 with the five-field "
        "permission-set shape that `Authority` carries at L4360. The two names' shapes are "
        "therefore exchanged. Separately, the revocation node has three names across eras — "
        "`Authority` (turns [2], [3]), `RuntimeAuthority` (turns [7], [9]) and `AuthorityNode` "
        "(turn [17]) — the last two being identical but for `AuthorityNode`'s extra `generation` "
        "field."),
      why_it_matters=(
        "N-28 requires `Constraint ≠ Authority` and the request's required distinctions include "
        "`CapRef ≠ Authority`; but at L6501/L6536 the two are the same struct, so `derive(A, C)` "
        "(L6519) is a map-meet between structurally identical types and nothing in the frozen "
        "declarations prevents a 'constraint' from being used as a grant — precisely the "
        "amplification that `CAP-DERIVE-NO-AMPLIFICATION` and mutation M006 exist to kill. The "
        "denotation change is worse than a rename: a reader who takes `Authority` from turn [2] "
        "and `Authority` from turn [11] to be one type will conclude that a permission set has a "
        "revocation state and a parent, or that a node has an operation set. X-37 records the "
        "seven declarations but does not compare their field sets, and states that "
        "`AuthorityNode` is declared once with its fields elided — L9702 declares it with four "
        "fields, and L39373/L39940 are two further, elided declarations."),
      disposition=(
        "REPORTED; no field, type or name renamed. T-10 (`Authority`) and T-12 (`Constraint`) "
        "keep their canonical readings and gain pointers to this entry; all six `Authority` field "
        "sets and both `Constraint` field sets are recorded verbatim in T-10's/T-12's `protected` "
        "lists where they are not already. `RuntimeAuthority` is added to T-11 (`AuthorityNode`) "
        "as a protected earlier name rather than being treated as a separate type. N-28 gains the "
        "L6501/L6535/L6686 evidence so the law and the declarations that contradict it sit in the "
        "same view."),
      affects=["T-10", "T-12", "T-11", "T-13", "T-09", "T-15", "T-81"],
      previously=["X-37", "AMB-26", "U-02", "U-21", "C-56"],
      decision_needed=(
        "Which field set is `Authority`'s and which is `Constraint`'s? The turn-[11] "
        "declarations give both names the same body and then give `Constraint` the shape "
        "`Authority` had at turn [8]. Also: is the revocation node `Authority`, "
        "`RuntimeAuthority` or `AuthorityNode`, and does it carry `generation`?"),
      new_finding=True,
      doc_sites=[
        ("spec/06-contradictions-ambiguities.md", 82, "| C-67 | `Authority` is declared seven times in six field sets",
         "C-67"),
        ("spec/09-unresolved-decisions.md", 170, "### U-31 — Which field set is `Authority`'s",
         "U-31"),
        ("term/00-overview.md", 175, "| `term/_terms.py T-79…T-81, N-28` |",
         "the §6 row recording N-28's four new evidence sites"),
        ("term/00-overview.md", 174, "| `term/_terms.py X-26, X-37, X-43, X-46, X-47, X-72` |",
         "the §6 row recording X-37's correction, which this entry extends"),
      ]),
    X(xid="X-78",
      title="`RefAuthority` is declared four times in three shapes; the frozen `reference_derive` body reads a field name only the first declaration has",
      kind="DIVERGENT-SHAPE",
      severity="MAJOR",
      sites=[
        (11572, "pub struct RefAuthority {", "turn [20]: first declaration"),
        (11573, "pub ops: HashSet<Op>,", "turn [20]: the field is `ops`, a set of the PRODUCTION `Op`"),
        (11575, "// ... other fields using naive representations", "turn [20]: the body is elided — the first shape is incomplete as written"),
        (11578, "pub fn reference_derive(parent: &RefAuthority, constraint: &RefConstraint) -> RefAuthority", "turn [20]: frozen signature; `RefConstraint` is declared nowhere (X-84)"),
        (11580, "ops: parent.ops.intersection(&constraint.ops).cloned().collect(),", "turn [20]: frozen body — reads `.ops` on both arguments, and needs SETS to call `intersection`"),
        (11581, "scope: parent.scope.intersection(&constraint.scope).cloned().collect(),", "turn [20]: same, for `scope`"),
        (19603, "pub struct RefAuthority {", "turn [27]: second declaration"),
        (19604, "pub operations: BTreeMap<Op, RefOperationAuthority>,", "turn [27]: field renamed `ops` -> `operations`; container becomes a MAP, so `intersection` no longer applies"),
        (20851, "pub struct RefAuthority {", "turn [28]: third declaration"),
        (20852, "pub operations: BTreeSet<Op>,", "turn [28]: a SET again, but named `operations`, with four `Ref*` component fields alongside"),
        (35699, "pub struct RefAuthority {", "turn [48]: fourth declaration"),
        (35700, "pub operations: BTreeMap<RefOp, RefOperationAuthority>,", "turn [48]: key type changes `Op` -> `RefOp`, which is declared nowhere (X-84)"),
        (35703, "pub struct RefOperationAuthority {", "turn [48]: re-declared, identical to L19608"),
      ],
      statement=(
        "The reference model's authority type has four declarations and three non-elided field "
        "sets: `{ ops: HashSet<Op>, scope: HashSet<Target>, /* ... other fields */ }` (L11572, "
        "turn [20], body elided); `{ operations: BTreeMap<Op, RefOperationAuthority> }` (L19603, "
        "turn [27]); `{ operations: BTreeSet<Op>, scope: RefScope, params: RefConstraint, "
        "resources: RefResources, lifetime: RefLifetime }` (L20851, turn [28]); and "
        "`{ operations: BTreeMap<RefOp, RefOperationAuthority> }` (L35699, turn [48]). The field "
        "is `ops` once and `operations` three times; the container is a `HashSet`, a `BTreeMap`, "
        "a `BTreeSet` and a `BTreeMap`; and the key type is the production `Op` in turns [20] and "
        "[27]-[28] and the undeclared `RefOp` in turn [48]. Four of the five component types "
        "(`RefScope`, `RefConstraint`, `RefResources`, `RefLifetime`) are declared nowhere. The "
        "frozen `reference_derive` body (L11579-L11583) reads `parent.ops`, `constraint.ops` and "
        "`parent.scope`, and calls `.intersection()` on them — a field name that only the "
        "turn-[20] declaration has and a set operation that the two map-shaped declarations "
        "cannot support."),
      why_it_matters=(
        "R-REF-03 requires the reference `derive` to equal the production `derive`, and the "
        "reference model is the differential oracle for the whole capability algebra; but its "
        "authority type has no fixed shape, its narrowing function is frozen against a field name "
        "that three of four declarations do not have, and its component vocabulary is "
        "undeclared. An implementer cannot write `reference_derive` from this text without "
        "choosing a shape, and whichever is chosen determines whether the oracle compares sets "
        "(turn [20]/[28]) or per-operation authority maps (turn [27]/[48]) — two different "
        "notions of attenuation. The turn-[28] shape is also the only one that mirrors the "
        "production `Authority`'s five components, which is what C-33's independence rule "
        "forbids it to reuse directly."),
      disposition=(
        "REPORTED; nothing renamed. Filed as T-81 with all four declarations, both field "
        "spellings (`ops`, `operations`), all four container forms, the frozen `reference_derive` "
        "signature and body, and the five undeclared component types protected verbatim. The "
        "undeclared names are also listed in X-84 so that one ruling can cover the reference "
        "model's whole vocabulary."),
      affects=["T-81", "T-10", "T-12", "T-58", "T-80", "T-15"],
      previously=["C-33", "U-21", "X-84"],
      decision_needed=(
        "Which `RefAuthority` shape is the oracle's — a set of operations (turns [20], [28]) or a "
        "map to `RefOperationAuthority` (turns [27], [48]) — and is its key the production `Op` "
        "or the undeclared `RefOp`? `reference_derive`'s frozen body only type-checks against the "
        "first."),
      new_finding=True,
      doc_sites=[
        ("spec/06-contradictions-ambiguities.md", 83, "| C-68 | `RefAuthority` is declared four times in three shapes",
         "C-68"),
        ("spec/09-unresolved-decisions.md", 186, "### U-33 — Which reference-model declarations govern",
         "U-33"),
        ("term/00-overview.md", 173, "| `term/_structs.py` | **new checker**",
         "the §6 row for the checker that produced the counts"),
      ]),
    X(xid="X-79",
      title="`RefState` is declared with the production machine's types in turns [23]-[24] and with `Ref*` types in turn [48], renaming `kont` and dropping `outcome`",
      kind="FIELD-SET",
      severity="MAJOR",
      sites=[
        (14728, "pub struct RefState {", "turn [23]: first declaration"),
        (14729, "pub expr: Expr,", "turn [23]: the PRODUCTION AST (T-30)"),
        (14730, "pub env: Environment,", "turn [23]: the production environment"),
        (14731, "pub kont: Vec<Frame>,", "turn [23]: the CEK spelling `kont`, holding the PRODUCTION frame (T-33)"),
        (14732, "pub outcome: RefOutcome,", "turn [23]: a fourth field"),
        (15985, "pub struct RefState {", "turn [24]: re-declared identically"),
        (16423, "pub struct RefState {", "turn [24]: re-declared identically again"),
        (35522, "pub struct RefState {", "turn [48]: the independent form"),
        (35523, "pub expr: RefExpr,", "turn [48]: `RefExpr` — declared nowhere, though `RefFrame` uses it in twelve places (X-84)"),
        (35524, "pub env: RefEnv,", "turn [48]: `RefEnv` — declared once"),
        (35525, "pub continuation: Vec<RefFrame>,", "turn [48]: `kont` renamed, and the frame type is the reference model's own"),
        (35541, "pub enum RefFrame {", "turn [48]: declared, and every one of its variants carries `RefExpr`, `RefEnv`, `RefOp` or `RefConstraint` payloads"),
      ],
      statement=(
        "The reference machine's state has four declarations in two field sets. Turns [23] and "
        "[24] (L14728, L15985, L16423) all declare `{ expr: Expr, env: Environment, kont: "
        "Vec<Frame>, outcome: RefOutcome }` — built entirely from PRODUCTION types. Turn [48] "
        "(L35522) declares `{ expr: RefExpr, env: RefEnv, continuation: Vec<RefFrame> }`: the "
        "field `kont` is renamed `continuation`, the field `outcome` is dropped, and every type "
        "is replaced by the reference model's own. `RefExpr`, the type of the new form's central "
        "field, is declared nowhere in the source, although the declared `RefFrame` enum (L35541) "
        "uses it in twelve variant payloads."),
      why_it_matters=(
        "C-33 records the rule that the reference model must not depend on any production crate, "
        "and turn [54] restates it; the turns-[23]/[24] `RefState` violates it on its face, since "
        "`Expr`, `Environment` and `Frame` are the production machine's types. The turn-[48] form "
        "satisfies the rule but is the one whose vocabulary is undeclared, so the oracle's state "
        "cannot be constructed from the frozen text. `outcome` matters separately: it is what the "
        "reference machine reports, and R-REF-05's differential comparison has to compare "
        "something — with `outcome` absent from the governing shape, the comparison's left-hand "
        "side is only a configuration, not a result. The `kont`/`continuation` split is the same "
        "field-name divergence X-22 records on the production side, here carrying a type change "
        "as well."),
      disposition=(
        "REPORTED; neither spelling renamed and `outcome` not struck. Filed as T-80 with all four "
        "declarations, both field names (`kont`, `continuation`), all six type names (`Expr`, "
        "`Environment`, `Vec<Frame>`, `RefExpr`, `RefEnv`, `Vec<RefFrame>`) and the dropped "
        "`outcome` protected verbatim. `RefExpr` is listed in X-84's undeclared family."),
      affects=["T-80", "T-58", "T-30", "T-32", "T-33", "T-81"],
      previously=["C-33", "X-22", "X-84"],
      decision_needed=(
        "Which `RefState` governs the differential oracle — the production-typed form of turns "
        "[23]-[24] (which C-33 forbids) or the independent turn-[48] form (whose `RefExpr` is "
        "undeclared)? And does the reference state carry `outcome`, or is the comparison made on "
        "configurations alone?"),
      new_finding=True,
      doc_sites=[
        ("spec/06-contradictions-ambiguities.md", 84, "| C-69 | `RefState` is declared with the production machine's types",
         "C-69"),
        ("spec/09-unresolved-decisions.md", 186, "### U-33 — Which reference-model declarations govern",
         "U-33"),
      ]),
    X(xid="X-80",
      title="`WalFrame` gains `payload_length: u32` in turn [47] and puts it inside the checksum's SHA-256 domain, so every checksum changes",
      kind="FIELD-SET",
      severity="MAJOR",
      sites=[
        (34237, "pub struct WalFrame {", "turn [46]: four fields — sequence, kind, payload, checksum"),
        (34241, "pub checksum: [u8; 32],", "turn [46]: the checksum's input domain is not stated here"),
        (35099, "pub struct WalFrame {", "turn [47]: five fields"),
        (35100, "pub sequence: WalSequence,      // u64, strictly monotonic", "turn [47]: width fixed in a comment"),
        (35101, "pub kind: WalRecordKind,        // u8, explicit enum discriminant", "turn [47]: `WalRecordKind` is declared nowhere (X-84)"),
        (35102, "pub payload_length: u32,        // Big-endian, checked", "turn [47]: the new field, big-endian"),
        (35104, "pub checksum: [u8; 32],         // SHA-256(sequence || kind || payload_length || payload)", "turn [47]: the checksum domain now includes `payload_length`"),
        (35109, "The persistence parser must reject: truncated headers, truncated payloads, impossible ", "turn [47]: the rejection rule that presumes a length field the turn-[46] frame does not have"),
      ],
      statement=(
        "The durable frame is declared twice with different field sets: `{ sequence, kind, "
        "payload, checksum }` at L34237 (turn [46]) and `{ sequence, kind, payload_length, "
        "payload, checksum }` at L35099 (turn [47]). The added field is not inert — L35104 fixes "
        "the checksum as `SHA-256(sequence || kind || payload_length || payload)`, so the two "
        "declarations compute different digests over the same record. The added field is also "
        "declared `u32` and 'Big-endian' (L35102), which is a third appearance of the "
        "endianness/width question C-47 and X-50 raise for the canonical envelope, and the "
        "turn-[47] parser rule at L35109 ('must reject: truncated headers, truncated payloads, "
        "impossible lengths') presumes a length field the turn-[46] frame does not carry. "
        "`WalFrame.kind`'s type, `WalRecordKind`, is declared nowhere, so the frame's "
        "discriminant has no variant list at either turn."),
      why_it_matters=(
        "The WAL is the recovery substrate: R-PERSIST-01/R-PERSIST-02 and the replay path read "
        "these bytes, and a checksum computed over a different concatenation than the one written "
        "makes every previously written record unverifiable. This is not a cosmetic field "
        "addition — it silently changes the digest of every frame, which is exactly the class of "
        "change R-SCOPE-03 says must never pass without a report. The big-endian `u32` also "
        "interacts with X-50: if the envelope layer is little-endian and the frame header is "
        "big-endian, a single implementation must contain both, and nothing in the frozen text "
        "says where the boundary falls. Without `WalRecordKind`'s variants, the 'impossible "
        "lengths' and 'truncated headers' rejections cannot be enumerated either."),
      disposition=(
        "REPORTED; neither field set rewritten and the checksum formula quoted verbatim. T-46 "
        "(`WalFrame`) gains both shapes and the checksum-domain string in its `protected` list, "
        "and `WalRecordKind` is recorded in X-84 as an undeclared field type. The endianness "
        "question is left with X-50/C-47 rather than restated as a new finding."),
      affects=["T-46", "T-45", "T-47", "T-49", "T-62"],
      previously=["X-31", "X-50", "C-47", "U-24", "X-84"],
      decision_needed=(
        "Does the durable frame carry `payload_length`, and is the checksum "
        "`SHA-256(sequence || kind || payload_length || payload)` (L35104) or a digest over the "
        "turn-[46] four-field concatenation? Also: is the header big-endian while the envelope is "
        "little-endian (X-50), and what are `WalRecordKind`'s variants?"),
      new_finding=True,
      doc_sites=[
        ("spec/06-contradictions-ambiguities.md", 85, "| C-70 | `WalFrame` gains `payload_length: u32`",
         "C-70"),
        ("spec/09-unresolved-decisions.md", 178, "### U-32 — Does the durable `WalFrame` carry `payload_length`",
         "U-32"),
      ]),


    X(xid="X-81",
      title="`EffectReceipt`'s first declaration has no `effect_digest`, the field every later receipt-integrity check reads",
      kind="FIELD-SET",
      severity="MINOR",
      sites=[
        (1454, "pub struct EffectReceipt {", "turn [4]: two fields — `id`, `result`"),
        (9375, "pub struct EffectReceipt {", "turn [17]: three fields — `id`, `effect_digest`, `result`"),
        (10329, "pub struct EffectReceipt {", "turn [18]: three fields"),
        (10813, "pub struct EffectReceipt {", "turn [18]: three fields again"),
        (22140, "pub struct EffectReceipt {", "turn [29]: three fields"),
        (23299, "pub struct EffectReceipt {", "turn [30]: three fields"),
        (23775, "pub struct EffectReceipt {", "turn [30]: three fields again"),
        (23814, "ReplayCorruption, // ID or Digest mismatch", "turn [30]: the fault that presumes a digest on the receipt"),
        (23815, "InvalidReceipt,", "turn [30]: and the fault for a receipt that does not match its effect"),
      ],
      statement=(
        "`EffectReceipt` is declared seven times in two field sets: `{ id: EffectId, result: "
        "Result<Value, HostFault> }` at L1454 (turn [4]) and `{ id: EffectId, effect_digest: "
        "EffectDigest, result: Result<Value, HostFault> }` at L9375 (turn [17]) and at all five "
        "later declarations (L10329, L10813, L22140, L23299, L23775). The turn-[4] form omits "
        "`effect_digest`, the field that binds a receipt to the effect it completes, and no "
        "supersession note connects the two."),
      why_it_matters=(
        "`EffectReceipt` is one of the request's required terms and the object the replay host "
        "supplies in place of real effects (R-HOST-03, R-EFFECT-06). Replay integrity is stated "
        "in terms of the digest: turn [30]'s `Fault` declares `ReplayCorruption` with the comment "
        "'ID or Digest mismatch' (L23814) and `InvalidReceipt` (L23815) beside it, and X-43 "
        "records that the ordered-trace form of `ReplayHost` exists precisely so a digest check "
        "can catch receipts consumed out of order. A receipt without a digest cannot be checked "
        "against its effect at all, so the turn-[4] shape makes the replay host's central "
        "guarantee unrepresentable. The severity is MINOR only because six of seven declarations "
        "agree and the direction of travel is unambiguous; it is still a field-set divergence in "
        "a required term, and the two shapes are not interchangeable in a signature."),
      disposition=(
        "REPORTED; `effect_digest` neither added to nor struck from the turn-[4] text. T-19 "
        "(`EffectReceipt`) keeps the three-field form as canonical and gains both shapes plus "
        "`effect_digest` in its `protected` list, with this entry cited."),
      affects=["T-19", "T-18", "T-20", "T-42", "T-70"],
      previously=["X-43", "C-22", "U-06"],
      decision_needed=(
        "Only formally: does the turn-[4] two-field `EffectReceipt` survive as an earlier shape, "
        "or is `effect_digest` part of the receipt from the start? Every integrity check in the "
        "frozen text assumes it is."),
      new_finding=True,
      doc_sites=[
        ("spec/06-contradictions-ambiguities.md", 86, "| C-71 | `EffectReceipt`'s first declaration has no `effect_digest`",
         "C-71"),
      ]),
    X(xid="X-82",
      title="`CapabilityKernel`'s arena changes value type and container, its `revocation_set` is dropped and re-typed, and `children` appears in one declaration only",
      kind="DIVERGENT-SHAPE",
      severity="MAJOR",
      sites=[
        (925, "pub(crate) struct CapabilityKernel {", "turn [3]: first declaration"),
        (927, "arena: slotmap::SlotMap<slotmap::DefaultKey, Authority>,", "turn [3]: the arena holds `Authority` — which in turn [3] is a revocation NODE (X-77)"),
        (928, "revocation_set: HashSet<slotmap::DefaultKey>,", "turn [3]: keyed by the arena's slot key"),
        (3656, "pub(crate) struct CapabilityKernel {", "turn [7]: one field only"),
        (3657, "arena: slotmap::SlotMap<slotmap::DefaultKey, RuntimeAuthority>,", "turn [7]: value type becomes `RuntimeAuthority`; `revocation_set` is GONE"),
        (5044, "pub(crate) struct CapabilityKernel {", "turn [9]: still one field, still `RuntimeAuthority`"),
        (5429, "pub struct CapabilityKernel {", "turn [9]: `revocation_set` returns and `children` appears"),
        (5430, "arena: SlotMap<DefaultKey, Authority>,", "turn [9]: value type back to `Authority`, now a permission set (X-77)"),
        (5432, "children: HashMap<DefaultKey, Vec<DefaultKey>>, // Parent -> Children", "turn [9]: the lineage index, in no other declaration"),
        (6694, "pub struct CapabilityKernel {", "turn [11]: `children` gone again"),
        (6695, "// Private arena mapping CapRef to Authority + lineage metadata", "turn [11]: lineage is now a COMMENT, not a field"),
        (6696, "arena: GenerationalArena<AuthorityNode>,", "turn [11]: container changes to `GenerationalArena`, value type to `AuthorityNode`"),
        (6697, "revocation_set: HashSet<CapRef>, // Or epoch-based generation tracking", "turn [11]: re-typed from a slot key to a `CapRef`, and the comment leaves the mechanism OPEN"),
      ],
      statement=(
        "The kernel is declared five times in four field sets. The arena's value type is "
        "`Authority` (L927, turn [3]), `RuntimeAuthority` (L3657/L5044, turns [7] and [9]), "
        "`Authority` again (L5430, turn [9]) and `AuthorityNode` (L6696, turn [11]) — three names "
        "for the node whose relationship is X-77's, and two of them change denotation between "
        "turns. Its container is `slotmap::SlotMap` in four declarations and `GenerationalArena` "
        "in the fifth. `revocation_set` is present at L928, absent from the turn-[7] and "
        "turn-[9] single-field declarations, present again at L5431, and present at L6697 with a "
        "different element type (`HashSet<CapRef>` instead of `HashSet<DefaultKey>`) and a "
        "comment — 'Or epoch-based generation tracking' — that leaves the mechanism undecided in "
        "the source itself. `children: HashMap<DefaultKey, Vec<DefaultKey>>` appears only at "
        "L5432; by L6695 lineage has been demoted to a comment."),
      why_it_matters=(
        "The kernel is the trust root (R-KERN-01 to R-KERN-03) and the object whose arena the "
        "ABA-safety argument depends on: `revocation_set` keyed by a bare slot key cannot "
        "distinguish a recycled index from a live capability, which is the whole reason `CapRef` "
        "carries a `generation` (X-25) and the reason L6697's `HashSet<CapRef>` is a materially "
        "different design. The two forms are not equivalent, and the frozen text offers both. "
        "Dropping `revocation_set` in turns [7] and [9] also removes the only place revocation "
        "state lives, while dropping `children` in turn [11] removes the only field that could "
        "implement cascading revocation — L6695's comment asserts 'lineage metadata' that no "
        "field of that declaration carries. An in-source 'Or epoch-based generation tracking' is "
        "an undecided decision recorded nowhere else in the registers."),
      disposition=(
        "REPORTED; no field renamed, no container chosen. T-13 (`CapabilityKernel`) gains all four "
        "field sets, both `revocation_set` element types and the `children` field in its "
        "`protected` list; `RuntimeAuthority` is protected under T-11 (`AuthorityNode`) per X-77. "
        "The undecided 'Or epoch-based' comment is carried in this entry's sites so it can be "
        "ruled on with U-02/X-25 rather than discovered again at implementation time."),
      affects=["T-13", "T-11", "T-10", "T-09", "T-14"],
      previously=["X-37", "X-25", "AMB-26", "U-02"],
      decision_needed=(
        "What does the kernel's arena hold — `Authority`, `RuntimeAuthority` or `AuthorityNode` — "
        "in which container (`SlotMap` or `GenerationalArena`)? Is `revocation_set` keyed by slot "
        "key or by `CapRef`, is it present at all in the turns-[7]/[9] form, and is revocation "
        "tracked by set or 'epoch-based generation tracking' (L6697)? Does `children` exist?"),
      new_finding=True,
      doc_sites=[
        ("spec/06-contradictions-ambiguities.md", 87, "| C-72 | `CapabilityKernel`'s arena changes value type and container",
         "C-72"),
        ("spec/09-unresolved-decisions.md", 170, "### U-31 — Which field set is `Authority`'s",
         "U-31, which also rules on the kernel's arena"),
      ]),
    X(xid="X-83",
      title="The turn-[31] and turn-[32] state structs are not the same structs: `run_state` and `members` appear, `scheduler` disappears, and `mailbox` changes type within turn [18]",
      kind="FIELD-SET",
      severity="MAJOR",
      sites=[
        (24156, "pub struct GlobalState {", "turn [31]: seven fields"),
        (24168, "pub scheduler: SchedulerState,", "turn [31]: the scheduler is part of the machine state"),
        (25535, "pub struct GlobalState {", "turn [32]: six fields — `scheduler` is GONE"),
        (25862, "pub struct GlobalState {", "turn [32]: six fields again"),
        (24197, "pub struct ActorState {", "turn [31]: seven fields, `status` but no `run_state`"),
        (25544, "pub struct ActorState {", "turn [32]: EIGHT fields — `run_state` added, `status` kept"),
        (25546, "pub run_state: RunState,", "turn [32]: the added field"),
        (25552, "pub status: ActorStatus, // Running, Pending, Blocked, Halted, Fault", "turn [32]: the pre-existing field, retained alongside"),
        (25871, "pub struct ActorState {", "turn [32]: the same turn's other declaration — seven fields, no `run_state`"),
        (24274, "pub struct RunnableQueue {", "turn [31]: one field"),
        (24275, "queue: VecDeque<ActorId>,", "turn [31]: a bare FIFO — nothing here can enforce at-most-once membership"),
        (25892, "pub struct RunnableQueue {", "turn [32]: two fields"),
        (25894, "members: BTreeSet<ActorId>, // Enforces \"at most once\" invariant", "turn [32]: the field R-ACTOR-04 and mutation M012 depend on"),
        (9438, "pub struct ActorState {", "turn [17]: `mailbox: Mailbox`"),
        (10360, "pub struct ActorState {", "turn [18]: `mailbox: VecDeque<MarshalledValue>` — the abstract type replaced inline"),
        (10892, "pub struct ActorState {", "turn [18]: `mailbox: Mailbox` again, in the SAME turn"),
      ],
      statement=(
        "Four field-set divergences sit in the scheduler/state layer, three of them between the "
        "adjacent turns [31] and [32]. (a) `GlobalState` carries `scheduler: SchedulerState` at "
        "L24168 (turn [31]) and does not at L25535 or L25862 (turn [32]). (b) `ActorState` gains "
        "`run_state: RunState` at L25546 (turn [32]) while KEEPING `status: ActorStatus` at "
        "L25552, so that one declaration carries both status fields; the same turn's other "
        "declaration (L25871) has only `status`. (c) `RunnableQueue` is `{ queue: "
        "VecDeque<ActorId> }` at L24274 (turn [31]) and `{ queue, members: BTreeSet<ActorId> }` "
        "at L25892 (turn [32]), where the comment on `members` reads 'Enforces \"at most once\" "
        "invariant'. (d) One turn earlier in kind: `ActorState.mailbox` is `Mailbox` at L9438 "
        "(turn [17]), `VecDeque<MarshalledValue>` at L10360 (turn [18]) and `Mailbox` again at "
        "L10892 — the same turn disagreeing with itself."),
      why_it_matters=(
        "Each divergence lands on an obligation rather than on prose. R-ACTOR-04 requires that "
        "'one actor appears in the runnable queue at most once' and mutation M012 ('duplicate "
        "runnable queue entry') exists to kill an implementation that gets it wrong — but the "
        "turn-[31] `RunnableQueue` has no membership index, so at-most-once is unenforceable in "
        "that shape, and U-17 already asks whether the queue is snapshotted or reconstructed on "
        "recovery. Dropping `scheduler` from `GlobalState` removes scheduler state from the "
        "object that `GlobalSnapshot.machine_state` persists (L26303), which changes what "
        "recovery can restore. Carrying `run_state` and `status` in one `ActorState` gives two "
        "sources of truth for whether an actor is blocked — the exact overlap X-23 records "
        "between `RunState::Faulted` and `ActorStatus::Fault` — while the same turn's other "
        "declaration has one. And `mailbox: VecDeque<MarshalledValue>` inlines the type X-76 "
        "shows is itself declared two ways, so the mailbox's element type is doubly undecided."),
      disposition=(
        "REPORTED as one grouped entry so a single ruling can settle the turn-[31]/[32] state "
        "layer; no field added to or removed from any declaration. T-37 (`ActorState`), T-38 "
        "(`GlobalState`), T-40 (`RunnableQueue`) and T-39 (`Mailbox`) each gain the divergent "
        "field lists in their `protected` entries with this entry cited. `RunState::NotRunnable`'s "
        "disappearance between L24299 and L25526 is X-75's and is not restated here."),
      affects=["T-37", "T-38", "T-40", "T-39", "T-36", "T-35", "T-79", "T-48"],
      previously=["X-75", "X-23", "U-17", "X-76"],
      decision_needed=(
        "Does `GlobalState` carry `scheduler: SchedulerState`? Does `ActorState` carry "
        "`run_state`, `status`, or both? Does `RunnableQueue` carry `members` (and if not, how is "
        "R-ACTOR-04's at-most-once enforced)? Is `ActorState.mailbox` a `Mailbox` or an inline "
        "`VecDeque<MarshalledValue>`?"),
      new_finding=True,
      doc_sites=[
        ("spec/06-contradictions-ambiguities.md", 88, "| C-73 | The turn-[31] and turn-[32] state structs are not the same structs",
         "C-73"),
        ("spec/09-unresolved-decisions.md", 194, "### U-34 — Which turn-[31]/turn-[32] state structs govern",
         "U-34"),
      ]),
    X(xid="X-84",
      title="Thirty-one more type names are used in frozen field positions and declared nowhere — including the reference model's whole vocabulary",
      kind="UNDEFINED-TYPE",
      severity="MAJOR",
      sites=[
        (35523, "pub expr: RefExpr,", "turn [48]: `RefState`'s central field type — undeclared, and used in twelve `RefFrame` variant payloads"),
        (35541, "pub enum RefFrame {", "turn [48]: declared, and built from `RefExpr`, `RefOp`, `RefConstraint`, `RefFunction`, `RefCapId`"),
        (35700, "pub operations: BTreeMap<RefOp, RefOperationAuthority>,", "turn [48]: `RefOp` undeclared (X-78)"),
        (19608, "pub struct RefOperationAuthority {", "turn [27]: declared — but its four field types `RefScope`, `RefConstraint`, `RefResources`, `RefLifetime` are not"),
        (35903, "pub run_state: RefRunState,", "turn [48]: with `RefCapabilityContext`, `RefHeap`, `VecDeque<RefMessage>` beside it"),
        (36042, "pub event_log: Vec<RefEvent>,", "turn [48]: `RefEvent` undeclared"),
        (36098, "RefRecoveryFault", "turn [48]: undeclared"),
        (36135, "pub trace: Vec<RefReceipt>,", "turn [48]: `RefReceipt` undeclared"),
        (484, "authority: AuthorityId,", "turn [2]: `Capability`'s own field type — undeclared"),
        (488, "struct Authority {", "turn [2]: whose `RevocationState` and `Rights` are undeclared too (X-77)"),
        (1191, "pub struct LiveHost {", "turn [3]: `FileSystemBackend`, `NetworkBackend` and `OsAuthority` — all three undeclared"),
        (34237, "pub struct WalFrame {", "turn [46]: `WalRecordKind`, the frame's discriminant type, is undeclared (X-80)"),
        (26301, "pub struct GlobalSnapshot {", "turn [33]: `last_effect_sequence: EffectSequence` — undeclared, beside `last_event_sequence: EventSequence`, which IS declared (X-47)"),
        (4361, "pub ops: OperationSet,", "turn [8]: `OperationSet` undeclared, and reused at L6687 by `Constraint`"),
        (5730, "ScopeConstraint", "turn [10]: with `OpConstraint` — both undeclared"),
        (9784, "trace: ReplayTrace,", "turn [17]: `ReplayTrace` undeclared (X-43)"),
        (22340, "receipts: ReceiptLog,", "turn [29]: `ReceiptLog` undeclared (X-43)"),
        (3540, "AddrPattern", "turn [6]: with `PathPattern` — the target pattern types, undeclared"),
        (5381, "CommandPattern", "turn [9]: with `GlobPattern`, `IpRange`, `PortSet` — the scope pattern types, undeclared"),
        (12917, "SendRequest", "turn [21]: with `SpawnRequest` — undeclared, and used in three declarations each"),
      ],
      statement=(
        "A field-position sweep of every struct and enum declaration in the source (272 struct "
        "declarations, 108 enum declarations) finds 69 type names used as field or variant-payload "
        "types that are declared nowhere. Thirteen are already recorded (X-29's `NormalizedAST`, "
        "`Form`, `GlobalEvent`, `CapabilitySummary`, `BudgetSummary` and the seven `Observed*` "
        "element types; X-30's `PlanIR`), four are `std` or external-crate types written "
        "unqualified (`SlotMap`, `DefaultKey`, `PathBuf`, `SocketAddr`), and twenty-one more are "
        "named in an existing entry or decision (`Rights`, `Operation`, `WalRecordKind`, "
        "`EffectSet`, `CapSet`, `ResourceBounds`, `ResourceUsage`, `EnvironmentSnapshot`, "
        "`Machine`, `ActorRef`, `TargetExpr`, `BudgetAllocationSpec`, `SendRequest`'s siblings, "
        "`PlannerMetadata`, `ProposalDigest`, `FuncRef`, `EffectSignature`, `EffectError`, "
        "`HostPolicyError`, `RecoveryFault`, `RefReceipt`/`RefRunState`). The remaining THIRTY-ONE "
        "are recorded nowhere in the repository: the reference model's twelve (`RefExpr`, `RefOp`, "
        "`RefScope`, `RefConstraint`, `RefResources`, `RefLifetime`, `RefFunction`, `RefEvent`, "
        "`RefHeap`, `RefMessage`, `RefCapabilityContext`, `RefRecoveryFault`), the authority "
        "layer's three (`AuthorityId`, `RevocationState`, `OsAuthority`), the algebra's three "
        "(`OperationSet`, `ScopeConstraint`, `OpConstraint`), the host's four "
        "(`FileSystemBackend`, `NetworkBackend`, `ReplayTrace`, `ReceiptLog`), the pattern "
        "types' six (`AddrPattern`, `PathPattern`, `CommandPattern`, `GlobPattern`, `IpRange`, "
        "`PortSet`), `EffectSequence`, and the two actor-request types (`SendRequest`, "
        "`SpawnRequest`)."),
      why_it_matters=(
        "These are not decorative names: they are the types of fields in frozen declarations, so "
        "each one is a hole in a structure the spec requires an implementation to build. The "
        "reference-model cluster is the worst, because R-REF-05's differential observer is the "
        "project's central verification instrument and C-33 forbids it from borrowing production "
        "types — the twelve `Ref*` names ARE its vocabulary, and none is declared, so the oracle "
        "is specified in a language the source never defines (X-78, X-79). `AuthorityId`, "
        "`RevocationState` and `Rights` are the field types of the turn-[2] `Authority` and of "
        "`Capability` itself, so the capability's own definition rests on three undefined types. "
        "`WalRecordKind` is the discriminant of the durable frame, whose variants the turn-[47] "
        "parser rules need in order to reject bad records (X-80). `EffectSequence` differs from "
        "the declared `EventSequence` by one letter and sits beside it in the same struct (X-47), "
        "so a reader cannot tell whether it is a typo or a third sequence domain."),
      disposition=(
        "REPORTED as an extension of X-29 rather than as thirty-one separate entries; nothing "
        "renamed and no type invented to fill a hole. The reference-model names are protected "
        "verbatim under T-80/T-81; `AuthorityId`, `RevocationState`, `Rights` and `OsAuthority` "
        "under T-10/T-11; `WalRecordKind` under T-46; `EffectSequence` under T-47; `ReplayTrace` "
        "and `ReceiptLog` under T-42. The counts in this entry are re-derivable with "
        "`python3 term/_structs.py --undeclared`, which is the checker that produced them."),
      affects=["T-80", "T-81", "T-10", "T-11", "T-46", "T-47", "T-42", "T-58", "T-12"],
      previously=["X-29", "X-30", "X-75", "U-13", "U-16", "U-21", "C-33"],
      decision_needed=(
        "Are the thirty-one names to be declared (and by whom — the reference model's twelve "
        "belong to `ror-reference`), or are they placeholders for production types the reference "
        "model is forbidden to reuse (C-33)? `EffectSequence` in particular needs a ruling: a "
        "third sequence domain, or a misspelling of `EventSequence`?"),
      new_finding=True,
      doc_sites=[
        ("spec/06-contradictions-ambiguities.md", 89, "| C-74 | Thirty-one more type names are used in frozen field positions",
         "C-74"),
        ("spec/09-unresolved-decisions.md", 186, "### U-33 — Which reference-model declarations govern",
         "U-33, which rules on the twelve `Ref*` names"),
        ("term/00-overview.md", 213, "python3 term/_structs.py --undeclared # field types declared nowhere: 69 names",
         "the §8 command that re-derives this entry's counts"),
      ]),
    X(xid="X-85",
      title="`FunctionValue.env` is an `EnvironmentSnapshot` in one declaration and a live `Environment` in two; X-33 records the name, not the divergence",
      kind="FIELD-SET",
      severity="MAJOR",
      sites=[
        (12354, "pub struct FunctionValue {", "turn [21]: first declaration"),
        (12357, "pub env: EnvironmentSnapshot,", "turn [21]: a SNAPSHOT of the defining environment — and a type declared nowhere (X-84)"),
        (13984, "pub struct FunctionValue {", "turn [22]: second declaration"),
        (13987, "pub env: Environment, // Immutable snapshot for reference interpreter",
         "turn [22]: the LIVE type name, with a comment that asserts the SNAPSHOT reading"),
        (14370, "pub struct FunctionValue {", "turn [22]: third declaration"),
        (14373, "pub env: Environment, // Captured lexical environment", "turn [22]: 'captured lexical environment' — the snapshot reading again, under the live type name"),
      ],
      statement=(
        "The closure value is declared three times with two different types for its captured "
        "environment: `env: EnvironmentSnapshot` at L12357 (turn [21]) and `env: Environment` at "
        "L13987 and L14373 (both turn [22]). `Environment` is declared four times in the source; "
        "`EnvironmentSnapshot` is declared nowhere. The other two fields (`params: Vec<Symbol>`, "
        "`body: Box<Expr>`) are identical in all three declarations, so this is a one-field "
        "divergence with two readings — and the two turn-[22] comments both assert the snapshot "
        "reading under the live type name: 'Immutable snapshot for reference interpreter' "
        "(L13987) and 'Captured lexical environment' (L14373). X-33 records `EnvironmentSnapshot` "
        "as a homonym of `Snapshot`, used once and never defined; it does not record that the "
        "same field has a second, DECLARED type in the two later declarations, which is the fact "
        "filed here."),
      why_it_matters=(
        "This is not a naming quibble: a snapshot and a live environment are different semantic "
        "objects. Capturing a snapshot gives lexical scoping and makes a closure's behaviour "
        "independent of later mutation of the defining scope; capturing the live environment gives "
        "dynamic visibility of those mutations. The two readings produce different traces for the "
        "same program, so the choice is observable by the differential oracle and by replay "
        "determinism (R-CALC-02/R-CALC-03, and the CEK rules that push and pop `Env` on a call). "
        "It is also unimplementable as written in the turn-[21] form, since `EnvironmentSnapshot` "
        "has no declaration (X-33, X-84) — an implementer must either invent it or substitute "
        "`Environment`, which silently decides the semantics the spec left open. The turn-[22] "
        "comments point the other way: they describe `Environment` as an immutable snapshot and a "
        "captured lexical environment, so the source's prose intends capture-by-snapshot while "
        "its type names say otherwise. Recovery depends on the answer too: X-33 notes that "
        "`FunctionValue` must be encodable in snapshots for closures to survive recovery, and a "
        "live environment cannot be encoded independently of the actor that owns it."),
      disposition=(
        "REPORTED; neither type renamed and no `EnvironmentSnapshot` declaration invented. T-31's "
        "neighbours are untouched: the two spellings are protected under this entry and cited "
        "from the `Value::Function` payload, whose frozen form carries the closure. "
        "`EnvironmentSnapshot` is listed in X-84's undeclared set."),
      affects=["T-31", "T-30", "T-32", "T-33", "T-58", "T-48"],
      previously=["X-33", "X-84", "X-45", "U-09", "U-02"],
      decision_needed=(
        "Does a `FunctionValue` capture a snapshot of its defining environment or the live "
        "environment? The type names say both (L12357 `EnvironmentSnapshot`; L13987 and L14373 "
        "`Environment`) while both turn-[22] comments say 'snapshot'. If a snapshot, "
        "`EnvironmentSnapshot` needs a declaration and a stated relationship to `Environment`; if "
        "live, L12357's type name and the two comments need a ruling that they are synonyms."),
      new_finding=True,
      doc_sites=[
        ("spec/06-contradictions-ambiguities.md", 90, "| C-75 | `FunctionValue.env` is an `EnvironmentSnapshot` in one declaration",
         "C-75"),
      ]),
    X(xid="X-86",
      title="`Frame`'s eleven declarations carry five distinct variant sets, and the continuation's variant names change twice",
      kind="DIVERGENT-SHAPE",
      severity="MAJOR",
      sites=[
        (12453, "pub enum Frame {", "turn [21]: nine variants — LetValue, Seq, If, CallFunction, CallArgument, Attenuate, RequestCapability, SendTarget, SendValue"),
        (14047, "pub enum Frame {", "turn [22]: the same nine names, different payloads"),
        (14430, "pub enum Frame {", "turn [22]: the same nine names, payloads differing again"),
        (16943, "pub enum Frame {", "turn [25]: FIVE variants — Attenuate and all three request/send frames are gone"),
        (18650, "pub enum Frame {", "turn [26]: the same five"),
        (19429, "pub enum Frame {", "turn [27]: SIX — Attenuate returns, the request frames do not"),
        (20307, "pub enum Frame {", "turn [28]: a one-variant excerpt (`Attenuate`), body elided"),
        (21181, "pub enum Frame {", "turn [29]: a three-variant excerpt — RequestCapability, RequestTarget, RequestArgument"),
        (23339, "pub enum Frame {", "turn [30]: the same three, elided"),
        (23830, "pub enum Frame {", "turn [30]: the same three again"),
      ],
      statement=(
        "The continuation frame enum is declared eleven times (L12453, L14047, L14430, L16943, "
        "L18650, L19429, L20307, L20713, L21181, L23339, L23830) in five distinct non-elided "
        "variant sets: nine variants at L12453 (turn [21]); the same nine names with different "
        "payloads at L14047 and again at L14430 (turn [22], so three sets among nine-variant "
        "declarations); five variants at L16943 and L18650 (turns [25], [26]); six at L19429 "
        "(turn [27]); and three at L23339/L23830 (turn [30]), with L20307/L20713 (turn [28]) and "
        "L21181 (turn [29]) as one- and three-variant excerpts whose bodies are elided. The "
        "request frames change name as well as presence: `SendTarget`/`SendValue` in turn [21], "
        "`RequestCapability` in turns [21]-[22], and `RequestTarget`/`RequestArgument` from turn "
        "[29] — while `Attenuate` disappears in turn [25] and returns in turn [27]. AMB-26 "
        "records the eleven declarations; the variant sets are not enumerated anywhere."),
      why_it_matters=(
        "`Frame` is the continuation of the CEK machine (T-33, R-CEK-03) and the element type of "
        "`EvalState.continuation`, so its variant set determines which reduction rules can be "
        "resumed at all. A five-variant frame cannot resume an effect request; a three-variant "
        "frame cannot resume a `Let`, a `Seq` or a call. Since the machine's transitions are "
        "frozen per turn and the frames they push are named in those transitions, the divergence "
        "is not cosmetic: two turns' machines have incompatible continuations, and no "
        "supersession note says which governs. The same enum is the type of `RefState.kont` in "
        "turns [23]-[24] (X-79), so the reference machine inherits whichever set is chosen. "
        "X-35 already records that `Expr::Request` has two field sets; this is the continuation "
        "side of the same drift."),
      disposition=(
        "REPORTED; no variant renamed, none struck, and the excerpts at L20307/L20713/L21181 are "
        "recorded as elided rather than counted as full declarations. T-33 (`Frame`) gains the "
        "five variant sets and all eleven declaration lines in its `protected` list and note, and "
        "X-37's claim that `Frame` is declared eleven times is confirmed by the checker that "
        "produced this entry (`python3 term/_structs.py --enums`)."),
      affects=["T-33", "T-32", "T-30", "T-80", "T-17"],
      previously=["X-37", "AMB-26", "X-35", "X-57", "U-02"],
      decision_needed=(
        "Which `Frame` variant set governs — the nine-variant form of turns [21]-[22], the "
        "five/six-variant forms of turns [25]-[27], or the three-variant form of turn [30]? And "
        "are the request frames `SendTarget`/`SendValue`, `RequestCapability`, or "
        "`RequestTarget`/`RequestArgument`?"),
      new_finding=True,
      doc_sites=[
        ("spec/06-contradictions-ambiguities.md", 91, "| C-76 | `Frame`'s eleven declarations carry five distinct variant sets",
         "C-76"),
        ("term/00-overview.md", 212, "python3 term/_structs.py --enums      # every enum variant set: 11 names with >1",
         "the §8 command that re-derives the variant sets"),
      ]),

]
