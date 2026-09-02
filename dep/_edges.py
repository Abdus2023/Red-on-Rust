"""Typed dependency edge tables + classification rules for the Red-on-Rust
specification (single source of truth for the generated `dep/` document set).

CONVENTION (frozen for this document set)
-----------------------------------------
Every edge below is a tuple ``(PROVIDER, CONSUMER, ...)`` and is rendered as

    PROVIDER -> CONSUMER          meaning: CONSUMER depends on PROVIDER

i.e. the arrow points from the thing depended upon to the thing that depends on
it.  This is the convention of `spec/04-dependency-graph.md` (its DOT edge
``S07->S08`` carries the note "S-08 depends on S-07").  It is the OPPOSITE of
the convention used by `mod/_ownership.py` / `mod/18-ownership-matrix.md`, whose
``MODULE_DEPS = (from, to, ...)`` tuples read ``from`` *depends on* ``to``.  The
import shim in `dep/_graph.py` flips `MODULE_DEPS` on the way in; see finding
V-06 in `dep/05-violations.md`.

Nothing here restates normative text.  Every edge carries a citation to the
place the dependency is actually stated (`Red-on-Rust.md` line ranges, `spec/`
sections, `mod/` DEPENDENCIES prose, or `req/` record IDs).
"""

# ---------------------------------------------------------------------------
# 1. Edge-kind vocabulary (the seven required kinds)
# ---------------------------------------------------------------------------
KINDS = (
    "TYPE_DEPENDENCY",
    "SEMANTIC_DEPENDENCY",
    "SECURITY_DEPENDENCY",
    "SERIALIZATION_DEPENDENCY",
    "PERSISTENCE_DEPENDENCY",
    "VERIFICATION_DEPENDENCY",
    "RUNTIME_DEPENDENCY",
)

# (meaning, implementable).  The provider-side constraint used to be a third
# free-text field here; it was contradicted by the classified edges for three of
# the seven kinds, so it moved to `KIND_PROVIDER_CHECK` below, where the rendered
# text and the predicate that enforces it are one entry (check 11).
KIND_DEF = {
    "TYPE_DEPENDENCY": (
        "The consumer names types/constructors declared by the provider.",
        True,
    ),
    "SEMANTIC_DEPENDENCY": (
        "The consumer's meaning is fixed by the provider's normative rule; no "
        "code edge is implied (specification-layer coupling).",
        False,
    ),
    "SECURITY_DEPENDENCY": (
        "The consumer's security property is *discharged* by the provider, which "
        "must be an authoritative machine-boundary component.",
        True,
    ),
    "SERIALIZATION_DEPENDENCY": (
        "The consumer's payloads/identities are encoded or decoded with the "
        "provider's canonical (15A) format.",
        True,
    ),
    "PERSISTENCE_DEPENDENCY": (
        "The consumer's durability, journal, snapshot or recovery behaviour is "
        "defined by the provider (15B).",
        True,
    ),
    "VERIFICATION_DEPENDENCY": (
        "Test-time coupling across the verification boundary: one endpoint is a "
        "MOD-14…MOD-17 module that supplies the oracle, harness, mutation run, CI "
        "or claim discipline, the other is the module under test. Never a "
        "production code edge.",
        False,
    ),
    "RUNTIME_DEPENDENCY": (
        "The consumer calls the provider during execution (a real call edge in "
        "the frozen crate DAG).",
        True,
    ),
}

# Kinds that would have to exist as Cargo edges if the dependency were
# implemented.  A cycle inside this subgraph is an implementation cycle; a cycle
# that needs a SEMANTIC_/VERIFICATION_ edge to close is a specification cycle.
IMPLEMENTABLE_KINDS = (
    "TYPE_DEPENDENCY",
    "SECURITY_DEPENDENCY",
    "SERIALIZATION_DEPENDENCY",
    "PERSISTENCE_DEPENDENCY",
    "RUNTIME_DEPENDENCY",
)
SPECIFICATION_KINDS = ("SEMANTIC_DEPENDENCY", "VERIFICATION_DEPENDENCY")

# ---------------------------------------------------------------------------
# 2. Authority model (for the security-direction and planner checks)
# ---------------------------------------------------------------------------
# R-TRUST-01 trust table / R-TRUST-02 TCB (`spec/03`, source L41823-41841,
# L28178-28230).  "Yes" rows are the authoritative machine boundary; they are
# the only legitimate PROVIDERS of a SECURITY_DEPENDENCY edge.
AUTHORITY = {
    "MOD-02": "Compiler — executable invariants (trust: Yes)",
    "MOD-03": "Capability kernel — authority decisions (trust: Yes)",
    "MOD-04": "Budget system — resource conservation (trust: Yes)",
    "MOD-05": "CEK machine — deterministic execution (trust: Yes)",
    "MOD-06": "Marshalling boundary — no raw capability transfer "
              "(INFERRED: `Red-on-Rust.md` L41827-41838 has no marshalling row; "
              "the rule is R-MARSHAL-01/02, not the trust table)",
    "MOD-07": "Scheduler — deterministic interleaving (trust: Yes)",
    "MOD-08": "Effect boundary — the only path to an external effect "
              "(INFERRED: the table's 'Effect journal' row is the journal, "
              "MOD-11; the rule here is R-EFFECT-03)",
    "MOD-10": "Canonical serializer — semantic identity "
              "(INFERRED: `Red-on-Rust.md` L41827-41838 has no serializer row; "
              "the rule is R-CANON-01/04, not the trust table)",
    "MOD-11": "Persistence / effect journal — durable + causal state (trust: Yes)",
    "MOD-12": "Recovery / supervisor — lifecycle and recovery (trust: Yes)",
    "MOD-09": "Replay host — recorded-effect reconstruction (trust: Yes; live host: Partial)",
}
# Which row(s) of the frozen trust table (`Red-on-Rust.md` L41827-41838) each
# module corresponds to.  Empty tuple = the table does not name this component,
# so its authority status is inferred from obligations rather than frozen.
# Checked by `dep/_graph.py` ID-7 against the parsed table.
TRUST_ROWS_OF_MODULE = {
    "MOD-01": (),
    "MOD-02": ("Compiler",),
    "MOD-03": ("Capability kernel",),
    "MOD-04": ("Budget system",),
    "MOD-05": ("CEK machine",),
    "MOD-06": (),
    "MOD-07": ("Scheduler",),
    "MOD-08": (),
    "MOD-09": ("Replay host", "Live host"),
    "MOD-10": (),
    "MOD-11": ("Persistence", "Effect journal"),
    "MOD-12": ("Supervisor",),
    "MOD-13": ("LLM / planner",),
    "MOD-14": (),
    "MOD-15": (),
    "MOD-16": (),
    "MOD-17": (),
}

NON_AUTHORITY = {
    "MOD-01": "specification layer: states invariants, enforces none",
    "MOD-13": "LLM / planner: proposal engine, trust table row 'No' (R-TRUST-01)",
    "MOD-14": "reference model: outside the TCB (verification side)",
    "MOD-15": "differential harness: outside the TCB",
    "MOD-16": "mutation registry: outside the TCB",
    "MOD-17": "verification/CI: outside the TCB",
}
PLANNER_NODES = {"MOD-13"}
REFERENCE_NODES = {"MOD-14"}
# Modules whose crate is a *production* crate (`CRATE_NODES` role 'production').
# MOD-13 belongs here: `ror-agent` is a production crate even though the planner
# is untrusted (R-TRUST-01) — untrusted is not the same as non-production, and
# leaving it out hid three unrealisable edges from HD-1.
PRODUCTION_NODES = {
    "MOD-01", "MOD-02", "MOD-03", "MOD-04", "MOD-05", "MOD-06", "MOD-07",
    "MOD-08", "MOD-09", "MOD-10", "MOD-11", "MOD-12", "MOD-13",
}
VERIFICATION_NODES = {"MOD-14", "MOD-15", "MOD-16", "MOD-17"}

# ---------------------------------------------------------------------------
# 3. Layer 1 — crate graph (10 frozen crates)
# ---------------------------------------------------------------------------
CRATE_NODES = [
    ("ror-core", "production"),
    ("ror-compiler", "production"),
    ("ror-kernel", "production"),
    ("ror-runtime", "production"),
    ("ror-persistence", "production"),
    ("ror-host", "production"),
    ("ror-agent", "production"),
    ("ror-reference", "verification"),
    ("ror-differential", "verification"),
    ("ror-testkit", "verification"),
]

# provider -> consumer  (consumer depends on provider)
CRATE_EDGES = [
    ("ror-core", "ror-compiler", "TYPE_DEPENDENCY",
     "spec/07 §6 `ror-compiler -> ror-core`; REQ-REPO-006/008"),
    ("ror-core", "ror-kernel", "TYPE_DEPENDENCY",
     "spec/07 §6 `ror-kernel -> ror-core`; REQ-REPO-006/009"),
    ("ror-core", "ror-runtime", "TYPE_DEPENDENCY",
     "spec/07 §6 `ror-runtime -> ror-core, ror-kernel`"),
    ("ror-kernel", "ror-runtime", "SECURITY_DEPENDENCY",
     "L39455 'The evaluator may depend on kernel interfaces but must not gain "
     "authority introspection'; R-TRUST-03; MODULE_DEPS MOD-05->MOD-03"),
    ("ror-core", "ror-persistence", "TYPE_DEPENDENCY",
     "spec/07 §6 `ror-persistence -> ror-core`"),
    ("ror-core", "ror-persistence", "SERIALIZATION_DEPENDENCY",
     "15B payloads are strictly 15A bytes (R-PERSIST-01/02); 15A lives in "
     "ror-core (R-CANON-01…11) — mod/11-persistence.md DEPENDENCIES"),
    ("ror-core", "ror-host", "TYPE_DEPENDENCY",
     "spec/07 §6 `ror-host -> ror-core, ror-runtime`"),
    ("ror-runtime", "ror-host", "RUNTIME_DEPENDENCY",
     "spec/07 §6 adapter boundary; L39508 §8 `ror-host` (HostExecutor + live "
     "host adapter interfaces); MODULE_DEPS MOD-09->MOD-08"),
    ("ror-core", "ror-agent", "TYPE_DEPENDENCY",
     "spec/07 §6 `ror-agent -> ror-core, ror-compiler, ror-runtime`"),
    ("ror-compiler", "ror-agent", "RUNTIME_DEPENDENCY",
     "spec/07 §6; R-PLANNER-02 (proposals must pass the compiler)"),
    ("ror-runtime", "ror-agent", "RUNTIME_DEPENDENCY",
     "spec/07 §6; REQ-ARCH-001 stage order (planner -> machine boundary)"),
    ("ror-core", "ror-testkit", "TYPE_DEPENDENCY",
     "spec/07 §6 `ror-testkit -> ror-core (+ test-only deps)`"),
    ("ror-reference", "ror-differential", "VERIFICATION_DEPENDENCY",
     "spec/07 §6 `ror-differential -> ror-reference, ...`; R-REF-05 comparator"),
    ("ror-runtime", "ror-differential", "VERIFICATION_DEPENDENCY",
     "spec/07 §6 'ror-runtime (black box)' — SUT observation edge, not a "
     "semantic dependency"),
    ("ror-testkit", "ror-differential", "VERIFICATION_DEPENDENCY",
     "spec/07 §6 `ror-differential -> ... ror-testkit`; R-REF-06 doubles"),
]

# Edges the specification *requires* but that no frozen crate list states.
# provider -> consumer, with the requirement that forces the edge.
CRATE_MISSING_EDGES = [
    ("ror-compiler", "ror-runtime", "TYPE_DEPENDENCY",
     "REQ-ARCH-004/005 + L39962-39998 §17: `fn execute(plan: &ExecutablePlan)` "
     "with construction `pub(crate)`-restricted to the compiler (L39947-39950). "
     "The runtime must name `ExecutablePlan`, so either the type is exported "
     "from `ror-compiler` (this edge) or it lives in `ror-core` behind a seal. "
     "Neither `spec/07` §6 nor `spec/10-index.json` states which."),
    ("ror-persistence", "ror-agent", "PERSISTENCE_DEPENDENCY",
     "mod/13-agent.md DEPENDENCIES 'MOD-11 (durable recording)': `PlannerAccepted` "
     "recording for exact replay (R-PLANNER-04, REQ-PLANNER-018). `ror-agent -> "
     "ror-persistence` appears in no crate list."),
    ("ror-persistence", "ror-runtime", "PERSISTENCE_DEPENDENCY",
     "`mod/_ownership.MODULE_DEPS` labels `MOD-08 -> MOD-11` a **crate** "
     "dependency ('request step 14 calls ror-persistence append/sync'), and "
     "R-DUR-02 / `spec/07` §3 make that call the hinge of the durability "
     "transaction — no effect before the journal is durable. `spec/07` §6 gives "
     "`ror-runtime -> ror-core, ror-kernel` only, and `spec/10-index.json` "
     "agrees with §6 here, so the edge exists nowhere. Either add it, or state "
     "the journal-trait inversion (`ror-runtime` owns the trait, "
     "`ror-persistence` implements it, which flips the edge to "
     "`ror-runtime -> ror-persistence`). See V-10."),
    ("ror-host", "ror-agent", "RUNTIME_DEPENDENCY",
     "mod/13-agent.md DEPENDENCIES 'MOD-09 (replay composition for the "
     "conformance suite)'; mod/09-host.md DEPENDENCIES 'MOD-13 (end-to-end "
     "replay composition)'. Direction undecided — see V-04."),
]

# Frozen forbidden edges.  Stored as (DEPENDENT, DEPENDENCY): the dependent MUST
# NOT depend on the dependency.  Source: L39809-39828 §14 and L39645-39651 §10.
FORBIDDEN_CRATE_EDGES = [
    ("ror-reference", "ror-runtime", "L39815 §14 FORBIDDEN; L39645-39651 §10"),
    ("ror-reference", "ror-kernel", "L39816 §14 FORBIDDEN; L39645-39651 §10"),
    ("ror-reference", "ror-persistence", "L39817 §14 FORBIDDEN; L39645-39651 §10"),
    ("ror-reference", "ror-host", "L39818 §14 FORBIDDEN; L39645-39651 §10"),
    ("ror-reference", "ror-agent", "L39645-39651 §10 (absent from the §14 list)"),
    ("ror-core", "ror-runtime", "L39820 §14 FORBIDDEN"),
    ("ror-core", "ror-kernel", "L39821 §14 FORBIDDEN"),
    ("ror-runtime", "ror-reference", "L39823 §14 FORBIDDEN"),
    ("ror-kernel", "ror-runtime", "L39824 §14 FORBIDDEN"),
    ("ror-compiler", "ror-runtime", "L39826 §14 FORBIDDEN"),
]

# The source's only whole-graph picture (L39762-39790 §13 "Dependency Graph").
# Its arrows point from provider to consumer — the convention used by this
# document set — so it is recorded here in that same direction.
CRATE_DIAGRAM_EDGES = [
    ("ror-core", "ror-compiler"), ("ror-core", "ror-kernel"),
    ("ror-core", "ror-reference"),
    ("ror-compiler", "ror-runtime"), ("ror-kernel", "ror-runtime"),
    ("ror-runtime", "ror-persistence"), ("ror-runtime", "ror-host"),
    ("ror-persistence", "ror-agent"),
]

# ---------------------------------------------------------------------------
# 4. Layer 2 — module graph: kind classification rules
# ---------------------------------------------------------------------------
# Every rule is a predicate over (PROVIDER, CONSUMER) — i.e. over the pair
# "CONSUMER depends on PROVIDER".  Rules are applied in order to all 137 module
# pairs, whether the pair was declared in `mod/_ownership.py` MODULE_DEPS,
# declared in a module file's DEPENDENCIES prose, or only witnessed by
# `req/registry.json` records.  The first matching rule wins; `dep/_graph.py`
# errors out if a pair matches none, so no edge can acquire a kind by default.
RUNTIME_PROVIDER = ("MOD-05", "MOD-06", "MOD-07", "MOD-08", "MOD-09")
RUNTIME_CONSUMER = ("MOD-05", "MOD-06", "MOD-07", "MOD-08")

# Provider-side constraint per kind: (text rendered by `dep/00` §2 and `dep/01`
# §2.x, predicate over (provider, consumer)).  `dep/_graph.py` check 11 fails the
# run if any module edge of that kind violates the predicate, so the column in
# the documents cannot drift away from the classified edges the way the
# free-text "Legitimate provider" field did.  `None` means the constraint is a
# property of the source text rather than of the graph and so cannot be tested
# here; SEMANTIC_DEPENDENCY is the only such kind and check 11 enforces that.
KIND_PROVIDER_CHECK = {
    "TYPE_DEPENDENCY": (
        "a production module that declares the type — `ror-core` domain types "
        "(MOD-01/MOD-04/MOD-10) and the plan-input, capability-ceiling and "
        "durable-state shapes (MOD-02/MOD-03/MOD-06/MOD-07); no MOD-14…MOD-17 "
        "module supplies a production type",
        lambda p, c: p in PRODUCTION_NODES,
    ),
    "SEMANTIC_DEPENDENCY": (
        "the module that single-homes the operative statement — a property of the "
        "source text, not of the graph, so it is the one kind with no "
        "machine-checkable provider rule",
        None,
    ),
    "SECURITY_DEPENDENCY": (
        "an authoritative machine boundary, never the LLM/planner — with exactly "
        "one recorded exception, `MOD-13 -> MOD-01`, which is the V-03 defect "
        "(also reported by SC-1)",
        lambda p, c: p in AUTHORITY or (p, c) == ("MOD-13", "MOD-01"),
    ),
    "SERIALIZATION_DEPENDENCY": (
        "MOD-10 SERIALIZATION (`ror-core` canonical)",
        lambda p, c: p == "MOD-10",
    ),
    "PERSISTENCE_DEPENDENCY": (
        "MOD-11 PERSISTENCE / MOD-12 RECOVERY (`ror-persistence`)",
        lambda p, c: p in ("MOD-11", "MOD-12"),
    ),
    "VERIFICATION_DEPENDENCY": (
        "one endpoint is MOD-14…MOD-17 (`ror-reference`, `ror-differential`, "
        "`ror-testkit`, `tests/`) and that endpoint is the evidence supplier; the "
        "other endpoint is the module under test — no edge may join two "
        "production modules",
        lambda p, c: p in VERIFICATION_NODES or c in VERIFICATION_NODES,
    ),
    "RUNTIME_DEPENDENCY": (
        "the callee component — always a production module; no MOD-14…MOD-17 "
        "module is a runtime callee",
        lambda p, c: p in PRODUCTION_NODES,
    ),
}

KIND_RULES = [
    ("R1-verification-sink",
     lambda p, c: c == "MOD-17",
     "VERIFICATION_DEPENDENCY",
     "the provider's claims/evidence/order obligations are defined in MOD-17, "
     "which is therefore the consumer here (R-TEST-*, R-CLAIM-*, R-ORDER-*, "
     "R-REPO-*)"),
    ("R2-verification-source",
     lambda p, c: p == "MOD-17",
     "VERIFICATION_DEPENDENCY",
     "MOD-17 supplies test infrastructure and CI to the modules whose test and "
     "CI obligations it defines (R-TEST-10; `ror-testkit`)"),
    ("R3-reference-mirror",
     lambda p, c: c == "MOD-14" and p in PRODUCTION_NODES,
     "SEMANTIC_DEPENDENCY",
     "the reference model re-models this module's frozen semantics "
     "(mod/14-reference.md: 'MOD-01…MOD-12 as *specification* dependencies'); "
     "R-REF-02/R-SCOPE-04 forbid turning it into an implementation edge"),
    ("R4-harness-target",
     lambda p, c: c in ("MOD-15", "MOD-16"),
     "VERIFICATION_DEPENDENCY",
     "the differential/mutation layer observes the provider as a black-box SUT "
     "or consumes its oracle"),
    ("R5-oracle",
     lambda p, c: p == "MOD-14",
     "VERIFICATION_DEPENDENCY",
     "independent oracle: the consumer's evidence is produced by the reference "
     "model (R-RECOV-04, REQ-TEST-045; MODULE_DEPS kind 'oracle')"),
    ("R6-harness-output",
     lambda p, c: p in ("MOD-15", "MOD-16"),
     "VERIFICATION_DEPENDENCY",
     "live-vs-replay differential / kill evidence consumed by the module whose "
     "obligations are under test"),
    ("R7-central-invariant-restatement",
     lambda p, c: c == "MOD-01",
     "SEMANTIC_DEPENDENCY",
     "MOD-01 restates a central invariant whose operative statement is "
     "single-homed in the provider (duplication register D-01…D-12, "
     "`mod/18-ownership-matrix.md` §3) — a specification-layer coupling, not a "
     "code edge"),
    ("R8-replay-composition",
     lambda p, c: {p, c} == {"MOD-09", "MOD-13"},
     "RUNTIME_DEPENDENCY",
     "end-to-end replay composition for the conformance suite; declared in BOTH "
     "module files and in neither crate list — see V-04/C-2 of `dep/03`"),
    ("R9-canonical-format",
     lambda p, c: p == "MOD-10",
     "SERIALIZATION_DEPENDENCY",
     "the consumer's payloads/digests are 15A-canonical bytes "
     "(R-CANON-*, R-MARSHAL-03/04, R-PERSIST-01/02)"),
    ("R10-durability",
     lambda p, c: p in ("MOD-11", "MOD-12"),
     "PERSISTENCE_DEPENDENCY",
     "durable records, journal chain, snapshot content or recovery "
     "classification (R-DUR-*, R-PERSIST-*, R-RECOV-*)"),
    ("R11-planner-prohibition",
     lambda p, c: c == "MOD-13" and p in ("MOD-03", "MOD-07"),
     "SECURITY_DEPENDENCY",
     "the planner prohibition ('MUST NOT allocate capabilities' / 'MUST NOT "
     "alter scheduler state') is discharged by the authority the planner must "
     "not touch — provider is an authoritative boundary, so the direction is "
     "valid (R-PLANNER-02, REQ-PLANNER-003/004/010)"),
    ("R12-constraint-semantics",
     lambda p, c: p == "MOD-03" and c == "MOD-02",
     "SEMANTIC_DEPENDENCY",
     "the compiler needs constraint semantics for the resource judgment "
     "(mod/02-compiler.md DEPENDENCIES) but no crate edge `ror-compiler -> "
     "ror-kernel` exists — see V-08"),
    ("R13-authority-kernel",
     lambda p, c: p == "MOD-03",
     "SECURITY_DEPENDENCY",
     "the authority decision is discharged by the capability kernel "
     "(derive/authorize/validate/revocation; R-CAP-*, R-KERN-*, R-TRUST-03)"),
    ("R14-domain-types",
     lambda p, c: p == "MOD-01",
     "TYPE_DEPENDENCY",
     "frozen semantic domain types and identifiers (R-CALC-*, R-CORE-*, "
     "REQ-REPO-006: `ror-core` is std-only)"),
    ("R15-budget-gates",
     lambda p, c: p == "MOD-04" and c in RUNTIME_CONSUMER,
     "RUNTIME_DEPENDENCY",
     "per-transition budget/deadline gate calls and escrow/charge points "
     "(R-BUDGET-05…08, R-EFFECT-05, gates 7–10/13)"),
    ("R15b-charging-points",
     lambda p, c: c == "MOD-04" and p in RUNTIME_PROVIDER,
     "SEMANTIC_DEPENDENCY",
     "the conservation law is *stated over* the charging points the machine "
     "defines; `ror-core` cannot depend on `ror-runtime` (L39820 §14), so this "
     "direction is specification-only"),
    ("R15c-durable-state-shapes",
     lambda p, c: p in ("MOD-06", "MOD-07") and c in ("MOD-11", "MOD-12"),
     "TYPE_DEPENDENCY",
     "snapshots/journal must encode actor and scheduler state shapes "
     "(R-PERSIST-04, R-RECOV-03 step 10); the shapes have to be declared in "
     "`ror-core` for `ror-persistence` to name them — un-frozen today (U-02)"),
    ("R15d-journal-back-reference",
     lambda p, c: p == "MOD-08" and c in ("MOD-11", "MOD-12"),
     "SEMANTIC_DEPENDENCY",
     "the journal chain and recovery classification are defined over records "
     "the request sequence produces, so the durable layer cites the machine. "
     "The coupling in the *other* direction (step 14: the request sequence "
     "calls `ror-persistence` append/sync, i.e. `MOD-11 -> MOD-08`) is the "
     "crate-level one, and `spec/07` §6 does not carry it — see V-10"),
    ("R16-budget-algebra",
     lambda p, c: p == "MOD-04" or c == "MOD-04",
     "TYPE_DEPENDENCY",
     "budget operands (`Consumable`/`Reserved`/`Deadline`) and the conservation "
     "law as an algebra/type dependency (R-BUDGET-01…04)"),
    ("R17-plan-input-type",
     lambda p, c: p == "MOD-02" and c == "MOD-05",
     "TYPE_DEPENDENCY",
     "the evaluator's input type is `ExecutablePlan` (REQ-ARCH-005; "
     "L39962-39998 §17) — the crate home of that type is undecided, see V-01"),
    ("R18-compiler-invocation",
     lambda p, c: p == "MOD-02",
     "RUNTIME_DEPENDENCY",
     "proposals are compiled before entering the machine (R-PLANNER-02, "
     "R-COMPILE-02, R-ARCH-01 stage order)"),
    ("R19b-planner-consumes-machine",
     lambda p, c: p in RUNTIME_PROVIDER and c == "MOD-13",
     "RUNTIME_DEPENDENCY",
     "the consumer here is the PLANNER, not the machine, so this is not an "
     "in-machine call: `spec/07` §6 lists `ror-agent -> ror-core, ror-compiler, "
     "ror-runtime`, i.e. the agent crate names the machine's runtime "
     "types/results. REQ-ARCH-001's stage order puts the planner upstream of the "
     "machine boundary; the reverse direction (machine -> planner) is R18 and is "
     "what SC-3 tests"),
    ("R19-machine-call",
     lambda p, c: p in RUNTIME_PROVIDER,
     "RUNTIME_DEPENDENCY",
     "in-machine call/sequence coupling: request sequence, scheduling, "
     "suspension/resume, issuance, replay (R-EFFECT-03, R-ACTOR-04, R-HOST-01)"),
]

# Hand overrides, applied after the rules (edge cases a rule would mislabel).
# Keyed (PROVIDER, CONSUMER).
KIND_OVERRIDES = {
    ("MOD-10", "MOD-01"): (
        "TYPE_DEPENDENCY",
        "15A encodes the `ror-core` data domain, so MOD-10 consumes MOD-01's "
        "types (R-CANON-04/05). The two `Value` domains collide here "
        "(C-03/C-45 -> U-09)."),
    ("MOD-01", "MOD-10"): (
        "SEMANTIC_DEPENDENCY",
        "NOT an encoding dependency: the machine `Value` domain is not the 15A "
        "`Value` domain (C-03/C-45 -> U-09). Witnesses REQ-CALC-001 -> "
        "REQ-CANON-009, REQ-CALC-008 -> REQ-CANON-001/021."),
    ("MOD-13", "MOD-01"): (
        "SECURITY_DEPENDENCY",
        "R-TRUST-01/R-CORE-01 as recorded depend on planner-boundary "
        "prohibitions (REQ-TRUST-001 -> REQ-PLANNER-003/010, SECURITY-IMPACT "
        "critical), which makes the planner module the PROVIDER of a security "
        "property. Enforcement is not in `ror-agent` (spec/07 §3) — see V-03."),
    ("MOD-03", "MOD-04"): (
        "TYPE_DEPENDENCY",
        "the resource ceiling operand of a capability is a value of the "
        "algebra's constraint/resource domain (mod/04-budget.md DEPENDENCIES: "
        "'MOD-03 (ceiling operand; logical time discipline)')."),
}

# ---------------------------------------------------------------------------
# 5. Layer 3 — section graph (24 sections), typed
# ---------------------------------------------------------------------------
# Edges are taken verbatim from `spec/10-index.json` `dependency_graph`
# (generated from `spec/_build_index.py` `section_edges`, which restates
# `spec/04` §A/DOT — provider -> consumer).  Kinds come from the notes in
# `spec/04` §A.
SECTION_KIND_RULES = [
    ("S-15A-canonical", lambda p, c: p == "S-17", "SERIALIZATION_DEPENDENCY",
     "15A canonical bytes underlie the consumer's records"),
    ("S-15B-durability", lambda p, c: p in ("S-18", "S-19") or (p, c) == ("S-12", "S-13"),
     "PERSISTENCE_DEPENDENCY", "15B framing / recovery classification"),
    ("S-verification", lambda p, c: p in ("S-20", "S-21") or c in ("S-20", "S-21", "S-24"),
     "VERIFICATION_DEPENDENCY", "reference/differential/mutation/CI evidence"),
    ("S-authority", lambda p, c: p in ("S-03", "S-09", "S-10") or c in ("S-12", "S-16"),
     "SECURITY_DEPENDENCY", "trust model / capability algebra / kernel authorize "
                            "the consumer's gates"),
    ("S-repository", lambda p, c: p in ("S-22", "S-23"), "RUNTIME_DEPENDENCY",
     "crate and milestone structure sequences the consumer (spec/04 §A dashed edges)"),
    ("S-machine", lambda p, c: p == "S-08", "RUNTIME_DEPENDENCY",
     "CEK machine semantics"),
    ("S-types", lambda p, c: p in ("S-01", "S-07"), "TYPE_DEPENDENCY",
     "scope/calculus domain types and vocabulary"),
    ("S-presentation-order", lambda p, c: True, "SEMANTIC_DEPENDENCY",
     "the section index follows the source's presentation order; this edge "
     "records order, not a semantic prerequisite"),
]

# ---------------------------------------------------------------------------
# 6. Findings (hand-authored; rendered with computed evidence by `_graph.py`)
# ---------------------------------------------------------------------------
FINDINGS = {
    "V-01": dict(
        title="`ExecutablePlan` has no determined crate home, so a required crate "
              "edge is undecided",
        severity="BLOCKING",
        constraint="crate DAG completeness (R-REPO-02, R-ARCH-03)",
        body=(
            "L39962-39998 §17 freezes `fn execute(plan: &ExecutablePlan)` with "
            "`ExecutablePlan { ir, bounds, _sealed: Sealed }` and construction "
            "`pub(crate) fn finalize(...)` restricted to the compiler "
            "(L39947-39950 §16). `pub(crate)` privacy is per-crate, so the type "
            "must either be exported from `ror-compiler` (which requires the edge "
            "`ror-runtime -> ror-compiler`) or live in `ror-core` behind a seal "
            "that Rust cannot express as `pub(crate)`. `spec/07` §6 and "
            "`spec/10-index.json` state `ror-runtime -> ror-core, ror-kernel` "
            "only, i.e. they silently assume the second option without "
            "specifying the sealing mechanism. §13's diagram "
            "(L39762-39790) shows `ror-compiler -> ror-runtime`, i.e. the first."),
        decision="Fix the crate home of `ExecutablePlan` and the sealing "
                 "mechanism; add the resulting edge to `spec/07` §6. Needs a new "
                 "`U-` item (no existing U-item covers it — `spec/09` has 16). "
                 "L39831 is the only frozen sentence that speaks to the choice — "
                 "it permits adjusting the compiler/kernel direction where "
                 "implementation mechanics require it, provided the compiler "
                 "never receives authority to execute effects — and no document "
                 "in `spec/`, `req/` or `mod/` cites it. `dep/05` §7 prices both "
                 "answers.",
    ),
    "V-02": dict(
        title="The frozen forbidden-edge list is not tracked by any obligation or "
              "atomic record",
        severity="MAJOR",
        constraint="ror-reference independence / boundary enforcement (R-REPO-03)",
        body=(
            "L39807-39828 §14 'Forbidden Dependency Edges' lists 9 Cargo-level "
            "prohibitions and L39645-39651 §10 adds a 10th "
            "(`ror-reference -> ror-agent`). A repository-wide search finds no "
            "`R-…` obligation in `spec/03`, no atomic record in `req/` and no "
            "finding in `spec/06` that cites L39757-39828: only "
            "REQ-REPO-014 ('`ror-reference` … with no production dependencies') "
            "carries part of it, and its SOURCE range (L39196-40762) swallows the "
            "block without stating it. Five of the ten prohibitions "
            "(`ror-core -> ror-runtime`, `ror-core -> ror-kernel`, "
            "`ror-runtime -> ror-reference`, `ror-kernel -> ror-runtime`, "
            "`ror-compiler -> ror-runtime`) therefore have no verification "
            "obligation at all, so the 'Cargo dependency review' mapped to "
            "R-ARCH-04 has no enumerated checklist."),
        decision="Register the ten prohibitions as atomic records under R-REPO-03 "
                 "and map them to a Track-B structural test.",
    ),
    "V-03": dict(
        title="Security dependencies whose provider is the LLM/planner module",
        severity="MAJOR",
        constraint="LLM/planner components must never become security authorities",
        body=(
            "The trust-model obligations in MOD-01 depend on planner-boundary "
            "records: REQ-TRUST-001 -> REQ-PLANNER-003 ('the model MUST NOT "
            "allocate capabilities', SECURITY-IMPACT critical) and "
            "REQ-TRUST-001 -> REQ-PLANNER-010 ('… MUST NOT alter scheduler "
            "state'). In the typed graph these are SECURITY_DEPENDENCY edges "
            "whose PROVIDER is MOD-13 AGENT, i.e. the planner module is the "
            "depended-upon side of a security property. The properties are "
            "*prohibitions on* the planner, not authority *held by* it, and "
            "`spec/07` §3 puts enforcement at the machine boundary "
            "('the check lives at the machine boundary, not in the LLM "
            "integration'), so the architecture is sound — but the dependency "
            "as recorded makes the planner a provider of security guarantees and "
            "would let an implementation discharge R-TRUST-01 inside `ror-agent`. "
            "It is also uncarriable: no crate edge `ror-agent -> ror-core` exists, "
            "so the edge appears in HD-1 too, and the same holds for the reverse "
            "planner edge `MOD-13 -> MOD-09`, which is SC-3's offender."),
        decision="Re-home the enforcement obligation: state R-TRUST-01's "
                 "operative form against MOD-03/MOD-06/MOD-08 and keep the "
                 "planner records as prohibitions only (no inbound security edge).",
    ),
    "V-04": dict(
        title="The source's §13 'Dependency Graph' contradicts the frozen crate "
              "edge list on one edge and adds three no crate list carries",
        severity="MAJOR",
        constraint="invalid dependency direction (R-ARCH-04, R-REPO-02)",
        body=(
            "Read in this document set's convention (arrow points to the "
            "dependent), L39762-39790 §13 draws 8 crate edges. Four agree with "
            "`spec/07` §6 (`ror-core -> ror-compiler`, `ror-core -> ror-kernel`, "
            "`ror-kernel -> ror-runtime`, `ror-runtime -> ror-host`). The other "
            "four do not, and they are not all the same kind of error "
            "(`dep/_graph.py` ID-3 lists them): "
            "(a) `ror-runtime -> ror-persistence` — i.e. the durable layer "
            "depending on the machine — is a **genuine contradiction**, not a "
            "convention artefact: request step 14 calls `ror-persistence` "
            "append/sync *from* `ror-runtime` (`spec/07` §3, R-DUR-02), and the "
            "durable layer has to survive the machine it outlives. "
            "(b) `ror-compiler -> ror-runtime` is V-01's undecided "
            "`ExecutablePlan` edge, absent from §6 (and the reverse direction is "
            "the one §14 forbids). "
            "(c) `ror-persistence -> ror-agent` is the `PlannerAccepted` "
            "recording edge — absent from §6, tracked as HD-3. "
            "(d) `ror-core -> ror-reference` conflicts with "
            "`spec/10-index.json`'s 'frozen semantics only (no production core "
            "deps)' and with R-REF-02 as recorded, though §14 does not forbid "
            "`ror-reference -> ror-core`. "
            "The §13 picture is a pipeline/data-flow diagram mislabelled "
            "'Dependency Graph'."),
        decision="Mark §13 as non-normative (pipeline order) or redraw it in the "
                 "depends-on direction; `spec/07` §6 governs.",
    ),
    "V-05": dict(
        title="Machine-readable crate graph in `spec/10-index.json` disagrees "
              "with `spec/07` §6",
        severity="MAJOR",
        constraint="crate DAG completeness (R-REPO-02)",
        body=(
            "`spec/07` §6 and `mod/_ownership.py` MODULE_DEPS both give "
            "`ror-host -> ror-core, ror-runtime` (adapter boundary). "
            "`spec/10-index.json` `crates[].depends_on` for `ror-host` lists "
            "`['ror-core']` only. Two `depends_on` entries are also not crate "
            "names — `'frozen semantics only (no production core deps)'` for "
            "`ror-reference` and `'ror-runtime (black box)'` for "
            "`ror-differential` — so any tool that reads the index as a crate "
            "DAG gets a wrong node set as well as a wrong edge set."),
        decision="Generate `spec/10-index.json` crate edges from one table "
                 "(ideally the `dep/` layer-1 table) and keep prose out of "
                 "`depends_on`.",
    ),
    "V-06": dict(
        title="`spec/04` and `mod/18` publish the same dependency relation with "
              "opposite arrow conventions",
        severity="MAJOR",
        constraint="graph legibility / tooling safety",
        body=(
            "`spec/04` §A/DOT writes `S07->S08` and annotates it 'S-08 depends on "
            "S-07' — arrow points to the dependent. `mod/18-ownership-matrix.md` "
            "§0 writes `MOD-02 COMPILER -> MOD-01 CORE [crate] ror-compiler -> "
            "ror-core`, where `MODULE_DEPS = (from, to)` means *from depends on "
            "to* — arrow points to the dependency. `mod/19-index.json` "
            "`module_dependency_graph.edges[{from,to}]` inherits the second "
            "convention. Concatenating the two graphs inverts the DAG."),
        decision="State the convention in both documents; `dep/` normalises on "
                 "`A -> B` = 'B depends on A' and flips MODULE_DEPS on import.",
    ),
    "V-07": dict(
        title="Prose-declared module dependencies are not in the machine-checked "
              "module graph",
        severity="MAJOR",
        constraint="graph completeness (mod/_build.py check 8)",
        body=(
            "`mod/_build.py` check 8 validates only `MODULE_DEPS` (crate/oracle/"
            "sut edges). The 17 module files' `DEPENDENCIES` prose declares more "
            "module edges than that table contains, and the prose and the table "
            "disagree in both directions. The prose-only edges include real "
            "cross-crate couplings — `MOD-10 -> MOD-11` (15B payloads are 15A "
            "bytes), `MOD-10 -> MOD-12` (15A decode at recovery step 3), "
            "`MOD-03 -> MOD-02` (constraint semantics), `MOD-02 -> MOD-05` "
            "(`ExecutablePlan` input type), `MOD-11 -> MOD-13` and "
            "`MOD-13 -> MOD-09` — none of which any checker verifies. These are "
            "written in this document set's convention (`A -> B` = B depends on "
            "A); the module files' prose reads the other way, which is exactly "
            "the V-06 hazard."),
        decision="Fold the prose edges into the checked table (typed), or have "
                 "`mod/_build.py` parse the DEPENDENCIES prose and assert "
                 "agreement with `dep/`.",
    ),
    "V-09": dict(
        title="MOD-04 BUDGET has no single crate home, so its edges cannot be "
              "checked against the crate DAG",
        severity="MAJOR",
        constraint="crate DAG completeness (R-REPO-02)",
        body=(
            "`mod/_ownership.py` gives MOD-04's crate as 'ror-core (+ gates in "
            "ror-runtime / ror-kernel)' and `spec/07` §2 splits the budget "
            "obligations across `ror-core` (R-BUDGET-01…07) and the runtime "
            "gates. Eight of MOD-04's edges therefore have an undecidable crate "
            "realisation, including the two that close cycles "
            "(`MOD-03 <-> MOD-04` ceiling operand, `MOD-04 <-> MOD-11/12` escrow "
            "durability). `ror-core -> ror-kernel` is forbidden (L39821 §14), so "
            "the shared ceiling/operand types must live in `ror-core`; the gate "
            "*calls* must live in `ror-runtime`. That split is never stated."),
        decision="Split MOD-04 into a `ror-core` algebra part and a `ror-runtime` "
                 "gate part (two modules, or one module with an explicit "
                 "two-crate home), then re-check the crate realisability of its "
                 "edges.",
    ),
    "V-08": dict(
        title="`ror-compiler -> ror-kernel` is required by the compiler's own "
              "dependency note but absent from the frozen crate list",
        severity="MAJOR",
        constraint="crate DAG completeness / single-homing of constraint semantics",
        body=(
            "mod/02-compiler.md DEPENDENCIES declares 'MOD-03 (constraint "
            "semantics; ceiling data for the resource judgment)'. Constraint "
            "admissibility, `⊓` and attenuation order are single-homed in "
            "MOD-03 (`ror-kernel`), but `spec/07` §6 gives `ror-compiler -> "
            "ror-core` only, and §14 does not forbid `ror-compiler -> "
            "ror-kernel` (it forbids the reverse). So the compiler must either "
            "duplicate the constraint semantics (violating the one-owner rule) or "
            "gain an undeclared crate edge. The gap is downstream of U-09 "
            "(`AdmissibleConstraint` orphaned, C-30) and U-21."),
        decision="Decide whether constraint *types* alone (ror-core) suffice for "
                 "the resource judgment, or add `ror-compiler -> ror-kernel`.",
    ),
    "V-10": dict(
        title="`mod/_ownership.MODULE_DEPS` asserts crate-level edges that "
              "`spec/07` §6 does not carry — one of them in a forbidden direction",
        severity="MAJOR",
        constraint="crate DAG completeness (R-REPO-02) + forbidden edges "
                   "(L39807-39828 §14)",
        body=(
            "`mod/_ownership.MODULE_DEPS` marks 23 of its 25 entries `crate`. "
            "Checked against `spec/07` §6 (`dep/_graph.py` ID-6), **5 imply a "
            "crate edge that no crate list carries**. Two are production "
            "couplings. (a) `MOD-11 -> MOD-08` — 'request step 14 calls "
            "`ror-persistence` append/sync' — needs `ror-persistence -> "
            "ror-runtime`, i.e. `ror-runtime` depending on `ror-persistence`. "
            "That call is the hinge of R-DUR-02 (no external effect before the "
            "journal is durable), so the single most load-bearing cross-crate "
            "call in the design is the one the crate list omits. (b) `MOD-03 -> "
            "MOD-04` — 'budget primitives co-located with ror-kernel; ceiling "
            "operand from the algebra' — needs `ror-core -> ror-kernel`, which "
            "L39821 §14 forbids outright; the note is independent evidence for "
            "V-09, because the module table itself treats MOD-04's primitives "
            "as kernel-resident while `crate_of_module()` homes MOD-04 in "
            "`ror-core`. The other three (`MOD-17 -> MOD-15`, `MOD-15 -> "
            "MOD-16`, `MOD-17 -> MOD-16`) have a non-crate home on at least one "
            "side (`tests/`, `mutations/registry.toml`), so they are dev "
            "couplings, but the `crate` label is wrong for them too."),
        decision="Add `ror-persistence -> ror-runtime` to `spec/07` §6, or state "
                 "the journal-trait inversion explicitly (which flips the edge "
                 "the other way and must then be checked against the "
                 "persistence-before-runtime build order). Re-label the three "
                 "test-side entries. Settle V-09 before deciding (b).",
    ),
    "V-11": dict(
        title="The frozen trust table does not cover three modules the graph "
              "treats as security authorities — and the source states it twice, "
              "with different rows",
        severity="MINOR",
        constraint="security dependencies must point at the authoritative "
                   "machine boundary (R-TRUST-01)",
        body=(
            "`Red-on-Rust.md` states the trust table twice: L27613-27623 (11 "
            "rows) and L41827-41838 (12 rows — the later one adds `Persistence | "
            "Yes | Durable machine state`, which the earlier one lacks; wording "
            "also drifts, 'Partially trusted' -> 'Partial', 'ReplayHost' -> "
            "'Replay host', 'Causal durability' -> 'Causal effect state'). Under "
            "the repository's supersession rule the later table governs, and "
            "`README.md` reproduces all 12 rows. Measured against it "
            "(`dep/_graph.py` ID-7), **three modules in `AUTHORITY` have no row "
            "at all**: `MOD-06` ACTOR (marshalling / delegation), `MOD-08` "
            "EFFECT (the table's 'Effect journal' row is the journal, i.e. "
            "MOD-11) and `MOD-10` SERIALIZATION. Their authority is inferred "
            "from R-MARSHAL-01/02, R-EFFECT-03 and R-CANON-01/04, not frozen by "
            "the table. No `SECURITY_DEPENDENCY` currently has one of the three "
            "as provider, so SC-1's PASS does not rest on them today — but the "
            "set is presented in `dep/05` §1.2 as the authoritative boundary, so "
            "the gap has to be visible. Separately, `spec/06` C-37 cites "
            "'L41641 (trust table: Deterministic interleaving)'; L41641 is "
            "the FIFO-scheduler passage, and the rows that say 'Deterministic "
            "interleaving' are L27618 and L41832."),
        decision="Add rows for the marshalling boundary, the effect boundary and "
                 "the canonical serializer to the trust table (or state that "
                 "they are inside the TCB by the obligations cited), and fix "
                 "C-37's provenance line.",
    ),
}

# ---------------------------------------------------------------------------
# 6b. Resolution options for the three findings that block the module layer
# ---------------------------------------------------------------------------
# An option is a *mutation of the graph as recorded*, never a decision: the
# decision belongs to the specification owner.  `dep/_graph.py` applies each
# mutation, recomputes the metrics, and prints what actually changes, so the
# consequences next to an option are measured rather than asserted.  Mutations:
#   add_crate_edges   (provider, consumer, kind) triples added to `spec/07` §6
#   rekind            {(provider, consumer): kind} — a module edge re-recorded
#                     with a different kind (e.g. specification-layer)
#   drop_module_edges [(provider, consumer)] — module edges removed because the
#                     obligation is re-homed or the prose declaration withdrawn
RESOLUTIONS = {
    "V-01": dict(
        question="Where does `ExecutablePlan` live, and how is it sealed?",
        options=[
            dict(id="V-01a",
                 label="Home it in `ror-core`, behind a seal",
                 change={},
                 note="No new crate edge: the runtime already depends on "
                      "`ror-core`. The open part is the mechanism, not the "
                      "direction — L39947-39950 §16 restricts construction to "
                      "`pub(crate) fn finalize`, and `pub(crate)` is per-crate, "
                      "so a `ror-core` home needs a seal Rust cannot express "
                      "that way. As recorded the module edge stays "
                      "`MOD-02 -> MOD-05`, which would then overstate who owns "
                      "the type."),
            dict(id="V-01b",
                 label="Export it from `ror-compiler`",
                 change=dict(add_crate_edges=[
                     ("ror-compiler", "ror-runtime", "TYPE_DEPENDENCY")]),
                 note="Adds `ror-compiler -> ror-runtime`, i.e. the runtime "
                      "names the compiler's type — the direction §13's diagram "
                      "already draws. §14 L39826 forbids only the reverse (the "
                      "compiler depending on the runtime), and L39831 permits "
                      "adjusting the compiler/kernel direction where "
                      "implementation mechanics require it, provided the "
                      "compiler never receives authority to execute effects, "
                      "which a type dependency does not grant."),
        ]),
    "V-03": dict(
        question="Who provides the security property that R-TRUST-01/R-CORE-01 "
                 "record against the planner prohibitions?",
        options=[
            dict(id="V-03a",
                 label="Keep as recorded",
                 change={},
                 note="SC-1 and SC-2 stay FAIL: on 14 obligations the "
                      "LLM/planner module is the provider of a security "
                      "property. The architecture is sound — enforcement sits "
                      "at the machine boundary (`spec/07` §3) — so what is "
                      "unsound is the record, not the design."),
            dict(id="V-03b",
                 label="Re-home the obligations onto the enforcing boundary and "
                       "drop the planner as provider",
                 change=dict(drop_module_edges=[("MOD-13", "MOD-01")]),
                 note="The coupling does not vanish: `MOD-03 -> MOD-01` already "
                      "exists (SEMANTIC, 13 req), so the invariant stays in the "
                      "graph with an authoritative provider. This is what "
                      "F-PLANNER-TRUST's verdict recommends."),
            dict(id="V-03c",
                 label="Keep the pair, record it as specification-layer",
                 change=dict(rekind={("MOD-13", "MOD-01"):
                                     "SEMANTIC_DEPENDENCY"}),
                 note="The weakest change that clears SC-1/SC-2: no "
                      "SECURITY_DEPENDENCY has a non-authoritative provider any "
                      "more. It leaves the planner as the module the trust "
                      "obligations point at, so it fixes the check without "
                      "fixing the reading."),
        ]),
    "V-04": dict(
        question="Which direction does the host/agent replay composition run, "
                 "or does it belong to neither crate?",
        options=[
            dict(id="V-04a",
                 label="The agent depends on the host",
                 change=dict(add_crate_edges=[
                     ("ror-host", "ror-agent", "RUNTIME_DEPENDENCY")]),
                 note="Carries `MOD-09 -> MOD-13` (R8-replay-composition) and "
                      "leaves `MOD-13 -> MOD-09` uncarried."),
            dict(id="V-04b",
                 label="The host depends on the agent",
                 change=dict(add_crate_edges=[
                     ("ror-agent", "ror-host", "RUNTIME_DEPENDENCY")]),
                 note="Carries `MOD-13 -> MOD-09` and leaves `MOD-09 -> MOD-13` "
                      "uncarried."),
            dict(id="V-04c",
                 label="Carry both prose declarations as they stand",
                 change=dict(add_crate_edges=[
                     ("ror-host", "ror-agent", "RUNTIME_DEPENDENCY"),
                     ("ror-agent", "ror-host", "RUNTIME_DEPENDENCY")]),
                 note="Measured below rather than asserted: both directions "
                      "typed RUNTIME is a crate-level 2-cycle, so this option "
                      "is not available while the crate layer is required to be "
                      "a DAG (check 7)."),
            dict(id="V-04d",
                 label="Neither crate owns it — the conformance suite composes "
                       "the two",
                 change=dict(drop_module_edges=[("MOD-09", "MOD-13"),
                                                ("MOD-13", "MOD-09")]),
                 note="F-HOST-AGENT's own verdict: `tests/` composes host and "
                      "agent, and both prose declarations are withdrawn. No "
                      "crate edge is needed and no obligation is lost, because "
                      "the composition is a test-time concern."),
        ]),
}

# ---------------------------------------------------------------------------
E_VERIF = {"MOD-14", "MOD-15", "MOD-16", "MOD-17"}
E_PROD = {"MOD-01", "MOD-02", "MOD-03", "MOD-04", "MOD-05", "MOD-06", "MOD-07",
          "MOD-08", "MOD-09", "MOD-10", "MOD-11", "MOD-12", "MOD-13"}

# 7. Cycle families (every SCC / mutual pair must match exactly one)
# ---------------------------------------------------------------------------
# `dep/_graph.py` fails the run if a computed cycle matches none of these, so no
# cycle can go unjudged.  A family is (id, name, predicate, verdict).  The
# predicate receives the frozenset of members.
CYCLE_FAMILIES = [
    ("F-PLANNER-TRUST", "trust model vs planner prohibitions",
     lambda fs: fs == {"MOD-01", "MOD-13"},
     "**REQUIRES ARCHITECTURAL REVIEW — V-03.** The closing edge "
     "`MOD-13 -> MOD-01` is a SECURITY_DEPENDENCY whose provider is the "
     "LLM/planner module. The properties are prohibitions *on* the planner and "
     "enforcement sits at the machine boundary (`spec/07` §3), so the "
     "architecture is sound, but as recorded the planner is a provider of a "
     "security guarantee. Re-home the operative statement of R-TRUST-01 against "
     "MOD-03/MOD-06/MOD-08 and the cycle disappears."),
    ("F-EVIDENCE-LOOP", "evidence loop (module ↔ verification layer)",
     lambda fs: bool(fs & E_VERIF) and not (fs <= E_PROD),
     "Not a code cycle. Both directions are VERIFICATION_DEPENDENCY (or the "
     "reference's SEMANTIC mirror): a module's obligations cite the evidence "
     "that discharges them, and the verification layer cites the obligations it "
     "tests. These edges are test-time only and are excluded from the "
     "implementation graph by construction (no frozen crate edge carries them, "
     "except `ror-reference -> ror-differential` and "
     "`ror-runtime -> ror-differential`, which are dev-dependencies — HD-6)."),
    ("F-HOST-AGENT", "end-to-end replay composition",
     lambda fs: fs == {"MOD-09", "MOD-13"},
     "**REQUIRES ARCHITECTURAL REVIEW.** `mod/09-host.md` declares MOD-13 and "
     "`mod/13-agent.md` declares MOD-09 for the same conformance-suite "
     "composition; neither `ror-host -> ror-agent` nor `ror-agent -> ror-host` "
     "appears in any crate list, and both directions are typed RUNTIME. Pick one "
     "owner — the conformance suite (`tests/`) should compose the two — and "
     "delete the other prose edge."),
    ("F-EFFECT-HOST", "effect / host handshake",
     lambda fs: fs == {"MOD-08", "MOD-09"},
     "Acceptable, resolved by dependency inversion. `MOD-08 -> MOD-09` is the "
     "real crate edge (`ror-runtime -> ror-host`, adapter boundary): the host "
     "implements a trait the runtime defines. The reverse `MOD-09 -> MOD-08` "
     "(receipts resume continuations, durable-trace sourcing) is a callback "
     "through that trait, so the crate DAG stays acyclic even though the module "
     "graph does not."),
    ("F-DURABILITY-JOURNAL", "journal chain vs request sequence",
     lambda fs: fs == {"MOD-08", "MOD-11"},
     "Acceptable, one direction is specification-only. `MOD-11 -> MOD-08` "
     "(the effect module depends on the journal: request step 14 calls "
     "`ror-persistence` append/sync) is a *crate-level* coupling according to "
     "`mod/_ownership.MODULE_DEPS`, but `spec/07` §6 carries no "
     "`ror-persistence -> ror-runtime` edge, so it is not realisable today — "
     "that gap is V-10/HD-3. The reverse (`ror-persistence` citing the request "
     "sequence) is specification-only and recorded as SEMANTIC — `dep/05` HD-1."),
    ("F-BUDGET-GATE", "budget algebra vs machine gates",
     lambda fs: "MOD-04" in fs and bool(fs & {"MOD-05", "MOD-06", "MOD-07", "MOD-08"}),
     "Acceptable. `MOD-04 -> <machine>` is the real per-transition gate call; "
     "the reverse edge is the conservation law *stated over* the machine's "
     "charging points, which is SEMANTIC only (`ror-core` may not depend on "
     "`ror-runtime`, L39820 §14)."),
    ("F-ESCROW-DURABILITY", "escrow durability / post-crash revalidation",
     lambda fs: "MOD-04" in fs and bool(fs & {"MOD-11", "MOD-12"}),
     "**Crate-ambiguous — V-09.** The escrow partition must be durable and must "
     "revalidate after recovery, but MOD-04's crate home is 'ror-core (+ gates "
     "in ror-runtime / ror-kernel)', so neither direction can be checked against "
     "the frozen crate list. Fix MOD-04's home, then this pair resolves to a "
     "one-way type dependency plus a specification constraint."),
    ("F-CEILING-OPERAND", "ceiling operand: capability algebra vs budget algebra",
     lambda fs: fs == {"MOD-03", "MOD-04"},
     "**Crate-ambiguous — V-09.** A capability's resource ceiling is a budget "
     "value and the budget's ceiling operand is a constraint value, so the two "
     "algebras are mutually typed. Both are partly in `ror-core`, and "
     "`ror-core -> ror-kernel` is forbidden (L39821 §14), so the shared operand "
     "type must live in `ror-core`. Not a code cycle once MOD-04's home is "
     "fixed."),
    ("F-INTRA-RUNTIME", "inside `ror-runtime`: evaluator / actor / scheduler / effect",
     lambda fs: bool(fs) and fs <= {"MOD-05", "MOD-06", "MOD-07", "MOD-08"},
     "**IMPLEMENTATION cycle, intra-crate — acceptable but must be documented.** "
     "All members live in `ror-runtime`, so no crate cycle arises. The mutual "
     "edges are the CEK `Request` transition (evaluation suspends into the "
     "request sequence, which resumes the continuation), the actor/scheduler "
     "runnable contract, and the `Pending`/wakeup handshake. Name `request.rs` "
     "and `transition.rs` as the single owners of the re-entry points so the "
     "cycle is a documented re-entry rather than a mutual import."),
    ("F-INTRA-CORE", "inside `ror-core`: domain types / budget algebra / canonical format",
     lambda fs: bool(fs) and fs <= {"MOD-01", "MOD-04", "MOD-10"},
     "Acceptable, intra-crate, and already anticipated: `spec/04` §B L94 flags "
     "exactly this risk ('`ror-core` hosting both `Expr`/`Value` and the "
     "canonical traits while `ror-runtime` needs canonical marshalling'). "
     "`ror-core` is one crate, so the cycle is a mutual reference between type "
     "domains inside it, not a Cargo cycle: `MOD-01 <-> MOD-10` is the `Value` "
     "(machine) vs `Value` (15A canonical) collision C-03/C-45 -> U-09, and "
     "`MOD-04 -> MOD-01` (SEMANTIC, 11 records) is a central-invariant "
     "restatement. Resolve U-09 by naming the two domains differently and the "
     "mutual reference disappears."),
    ("F-INTRA-PERSISTENCE", "inside `ror-persistence`: journal vs recovery",
     lambda fs: bool(fs) and fs <= {"MOD-11", "MOD-12"},
     "Acceptable, intra-crate. The journal chain defines what recovery reads and "
     "recovery defines which records are admissible; both are `ror-persistence`. "
     "The one thing to fix is U-17 (which of snapshot queue / reconstruction is "
     "authoritative), because that decides which side is normative."),
    ("F-CORE-RESTATEMENT", "central-invariant restatement (duplication register)",
     lambda fs: "MOD-01" in fs,
     "Not a code cycle. `MOD-01 -> X` is a TYPE_DEPENDENCY (the module needs the "
     "frozen domain types); `X -> MOD-01` is the central invariant restated in "
     "the trust/thesis text whose operative statement is single-homed in X "
     "(duplication register D-01…D-12, `mod/18` §3). The restatement side "
     "carries no code edge; it exists so a reader of the thesis can find the "
     "operative rule."),
]
