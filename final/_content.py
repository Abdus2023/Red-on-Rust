#!/usr/bin/env python3
"""FINAL1 compiler — curated compilation-layer content.

Data module (no side effects). Everything here is *organization*, not
semantics: section intros, the global-invariant registry rows, the
mathematical-symbol canonicalization table, the FINAL1-level ambiguity
records (`FA-nn`, additive namespace), the evidence-model block, and the
open-decisions framing. Normative text is never written here: it is
transcribed verbatim by `final/_build.py` from `spec/01` (the cleaned
authority), and the registries are re-emitted from `spec/03`, `spec/08`,
`spec/09`, `term/10-index.json`, `dep/05` and `req/registry.json`.

If anything in this module appears to add a requirement, an API, a
guarantee, an implementation claim, or a proof claim, it is a bug in the
compiler and the cleaned authorities govern (R-SCOPE-03 discipline).
"""
from __future__ import annotations

# --------------------------------------------------------------------------
# Section plan: FINAL1 §01..§29 -> (title, areas with explicit overrides)
# --------------------------------------------------------------------------

# Requirement-area -> canonical FINAL1 home section. Exceptions listed in
# `HOME_OVERRIDES` by full requirement ID.
AREA_HOME = {
    "SCOPE": 1, "CORE": 2, "ARCH": 2, "REPO": 2,
    "TRUST": 3,
    "CALC": 4,
    "COMPILE": 5,
    "CAP": 6, "KERN": 6,
    "BUDGET": 7,
    "CEK": 8,
    "ACTOR": 9,
    "EFFECT": 11, "DUR": 11,
    "HOST": 12,
    "CANON": 13, "MARSHAL": 13,
    "PERSIST": 14,
    "RECOV": 15,
    "PLANNER": 16,
    "REF": 17,
    "TEST": 18,
    "ORDER": 27,
    "CLAIM": 28,
}

HOME_OVERRIDES = {
    # S-15 is split: the FIFO scheduler and the deterministic-scheduling
    # theorem are §10 (Scheduler); the remainder stays in §09 (Actors).
    "R-ACTOR-04": 10, "R-ACTOR-07": 10,
    # S-20 is split: the normalized-observation and harness-enforcement
    # obligations are differential-verification (§18), not the model itself.
    "R-REF-05": 18, "R-REF-06": 18,
    # S-21 is distributed over the verification-regime sections 18..22.
    "R-TEST-01": 20, "R-TEST-02": 21, "R-TEST-03": 21,
    "R-TEST-04": 19, "R-TEST-05": 19, "R-TEST-06": 19,
    # R-TEST-07..12 keep the §18 default.
}

SECTION_TITLES = {
    1: "Scope",
    2: "Architectural Thesis",
    3: "Trust Model",
    4: "Semantic Domain",
    5: "Compilation Pipeline",
    6: "Capability Model",
    7: "Budget Model",
    8: "CEK Evaluator",
    9: "Actors",
    10: "Scheduler",
    11: "Effects",
    12: "Host Policy",
    13: "Serialization",
    14: "Persistence",
    15: "Crash Recovery",
    16: "Agent/LLM Loop",
    17: "Independent Reference Model",
    18: "Differential Testing",
    19: "Mutation Testing",
    20: "Exhaustive Testing",
    21: "Property Testing",
    22: "Stress Testing",
    23: "Security Invariants",
    24: "Determinism Invariants",
    25: "Recovery Invariants",
    26: "Requirement Registry",
    27: "Verification Registry",
    28: "Evidence Model",
    29: "Open Architectural Decisions",
}

# Which cleaned sections (S-nn) feed each FINAL1 section (for the index).
# Rendered content selection is by requirement home; this table only feeds
# the cross-reference alias map in `final/02`.
S_TO_FINAL = {
    "S-01": [1], "S-02": [2, 23, 24, 25], "S-03": [3, 23], "S-04": [2],
    "S-05": [16], "S-06": [5], "S-07": [4], "S-08": [8],
    "S-09": [6, 23], "S-10": [6], "S-11": [7, 24], "S-12": [11, 23],
    "S-13": [11, 15, 25], "S-14": [12], "S-15": [9, 10, 24], "S-16": [13],
    "S-17": [13, 24], "S-18": [14, 25], "S-19": [15, 25], "S-20": [17, 18, 23],
    "S-21": [18, 19, 20, 21], "S-22": [2], "S-23": [27], "S-24": [28],
}

# --------------------------------------------------------------------------
# Section intros for the compiled specification (final/01).
# Keys are final section numbers. `{n}` formatting is applied by _build.py.
# --------------------------------------------------------------------------

SECTION_INTROS = {
    1: ("Canonical scope obligations: the thesis sentence, the freeze/evidence "
        "discipline, the STOP-and-report process rule, and the production↔reference "
        "separation. Supersedes nothing: these four requirements are quoted verbatim "
        "from the cleaned authority (`spec/01` S-01). The document-status and "
        "governance rule of the cleaned set is restated here as §01.0 below; the "
        "status ladder itself is canonically defined in §28 (Evidence Model)."),
    2: ("The architectural thesis: the central negative invariant, the seven-conjunct "
        "external-effect chain, the cross-cutting core invariants (including the "
        "frozen post-audit addenda R-CORE-11…R-CORE-14), the component architecture, "
        "and the repository/crate structure with its frozen addendum-VI placement "
        "decisions. Global invariants defined in this section carry canonical `GI-` "
        "IDs registered in `final/05` and indexed in §23–§25; their normative text "
        "is defined here, exactly once, and referenced from elsewhere by ID."),
    3: ("The trust table, TCB composition, the no-hidden-authority rule, and the "
        "frozen addenda fixing trust-table completeness (R-TRUST-04) and the "
        "structural carriability of the durability hinge (R-TRUST-05). The "
        "isolation-posture decision (R-ARCH-05, §02) belongs to this boundary; "
        "residual accepted risk is recorded there, not softened."),
    4: ("The semantic domain proper: machine value domain, frozen expression AST, "
        "symbol identity, the effect descriptor and cost, the frozen fault taxonomy, "
        "effect recovery properties, and the Σ/G configuration structures. Every "
        "production type defined here has exactly one canonical definition, cited "
        "as the single home (see `final/02` §4, Type Definition Homes). "
        "Reference-model value domains (`RefValue`, `RefCapId`, `RefActorId`, "
        "RefEffectId`) are *distinct* abstractions — see §17; they are never "
        "collapsible with the production types defined here (N-27 discipline)."),
    5: ("The compilation boundary from untrusted `Block` data to trusted "
        "`ExecutablePlan`: pipeline, static judgment, plan temporal integrity, "
        "constructor privacy, and the frozen capability-literal rule (R-COMPILE-06). "
        "The effect-set-inference gap is carried forward verbatim as a non-normative "
        "gap note (U-22) — it is a recorded absence, not a resolved item."),
    6: ("The capability algebra (semantic domains, partial order, derivation, "
        "authorization predicate, revocation/lineage, the three frozen theorems, "
        "logical time, admissibility, lifetime retyping) and the capability kernel "
        "(opaque generation-safe `CapRef`, authority storage, substrate privacy, "
        "the possession gate, the `CapabilityContext` possession type, and the "
        "root-grant protocol). Theorem status stays `SPECIFIED` with source proof "
        "sketches; no mechanized proof exists and none is claimed (R-CAP-08 "
        "explicitly records this)."),
    7: ("The budget model: structure, checked arithmetic, reservation predicates, "
        "the dual gate, conservation, time advancement, the cost model, the fault "
        "rule, and the frozen addenda (escrow-disposition totality R-BUDGET-09, "
        "resource-state atomicity R-BUDGET-10, disposition normal form R-BUDGET-11, "
        "persistent capacity R-BUDGET-13, duration semantics R-BUDGET-15, the "
        "exhaustive δ_t table R-BUDGET-16). `R-BUDGET-12` was never frozen (its "
        "rule is folded into R-BUDGET-15/16) and `R-BUDGET-14` remains deferred — "
        "the ID gaps are deliberate and MUST NOT be re-used (§10 report)."),
    8: ("The explicit CEK machine: state, the value-return invariant, the frozen "
        "continuation-frame set (closure env ≠ caller env), lambda capture, call "
        "ordering with arity precheck, continuation preservation, and "
        "progress/preservation. No recursion into host-stack calls (N-15-adjacent; "
        "prohibited shortcut list, R-CLAIM-02)."),
    9: ("Actor isolation, global state, deterministic identity allocation, spawn "
        "transactionality, messaging, the no-amplification/no-teleportation pair, "
        "and the frozen spawn-authority (R-ACTOR-09) and mailbox-admission "
        "(R-ACTOR-10) obligations. The scheduler-visible obligations R-ACTOR-04 "
        "and R-ACTOR-07 are homed in §10; they are actors-adjacent but the "
        "canonical FIFO/at-most-once and scheduling-theorem statements are "
        "scheduler material (cleaned source S-15 split — see `final/02`)."),
    10: ("The deterministic scheduler: FIFO order with at-most-once runnable "
        "membership (R-ACTOR-04) and the deterministic-concurrency theorem "
        "(R-ACTOR-07, the canonical Phase-13 form of the determinism invariant per "
        "the `mod/18` duplication register D-05). The theorem inherits the recorded "
        "U-35 limitation: its parameters `SchedulerTrace`/`HostTrace`/`InitialState`/"
        "`UniqueMachineTrace` remain undefined in the corpus, which makes the "
        "unqualified theorem form currently unfalsifiable — carried forward, not "
        "quietly fixed (GI-DET-01 note)."),
    11: ("The effect pipeline as one frozen sequence: the request protocol (R-CORE-14 "
        "canonical 16-step order over the 16 obligations here), the gated transition "
        "shape, short-circuit denial, guaranteed completion accounting, receipt "
        "causality, completion accounting, receipt-result admission, and the "
        "transactional issuance boundary (R-DUR-01…07). Effect ordering is *frozen* "
        "material: `Prepared → Issued → HostInvoked → Completed/Reconciled` and the "
        "durable-before-host hinge are restated nowhere in this document except via "
        "GI references (GI-SEC-07, GI-SEC-09, GI-SEC-10, GI-REC-01)."),
    12: ("The host gate, adapter scope, the ordered replay host, the replay "
        "correspondence theorem, trace validation, and the durable receipt-result "
        "contract (R-HOST-06). The host is partially trusted; the negative "
        "guarantees (no host before durable issuance; replay never touches the "
        "external world) are carried at full strength."),
    13: ("Canonical serialization (Phase 15A wire format) and the marshalling/"
        "delegation boundary. This is the single home of: the universal envelope, "
        "the frozen tag namespaces, collection encodings, the strict decoder "
        "contract, checked arithmetic, the digest rules, the scoped injectivity "
        "claim, golden vectors as normative fixtures, the decode-side "
        "authority-minting ban (R-CANON-12), the one-grammar decision (R-CANON-13), "
        "recursive capability rejection (R-MARSHAL-01/02/06), the explicit "
        "delegation envelope (R-MARSHAL-05), and `MarshalledValue` as the "
        "canonical transport. Production `CapRef`/`ActorId`/`EffectId` encodings "
        "live here; the reference model's distinct `Ref*Id` identifiers are defined "
        "in §17 and are not re-typed here."),
    14: ("The persistence protocol (Phase 15B): the non-semantic-machine rule, "
        "two-level framing, the record taxonomy, snapshot content and atomic "
        "commit, sequence continuity, and the frozen authority-lattice "
        "(R-PERSIST-07) and rewinding-resistance (R-PERSIST-08) obligations. The "
        "open encoding gap for machine state (U-02) is *not* closed here; it is "
        "listed in §29 and carried in `final/09`."),
    15: ("Crash recovery: durable-state definition, the T0–T6 matrix, the 12-step "
        "recovery algorithm, independent recovery, strict validation (no silent "
        "repair), the budget recovery invariant, reconciliation, the frozen "
        "reconciliation protocol (R-RECOV-08) and reconstruction authority "
        "(R-RECOV-09). The irreducibility of `Indeterminate` and the "
        "`Indeterminate ≠ NotExecuted` law (N-24) bind every clause of this section."),
    16: ("The agent/LLM loop: proposal as data, the planner's absolute "
        "incapacities, causal binding by exact-epoch staleness (R-PLANNER-06), "
        "planner determinism is *not required* of the model but *is* required of "
        "the machine through recorded proposals (R-PLANNER-04), the outer-loop "
        "conformance obligations, and the capability-opaque observation channel "
        "(R-PLANNER-07). LLM non-authority is a negative guarantee and is stated at "
        "full strength (GI-SEC-12)."),
    17: ("The independent reference model as an architectural contract. No "
        "reference implementation exists in this repository; nothing here "
        "manufactures one. The independence boundary, scope, non-goals, and the "
        "differential purpose are the contract text. Identity separation is "
        "normative: production `Value`/`CapRef`/`ActorId`/`EffectId` (defined in "
        "§04/§13) are *not* the reference-model `RefValue`/`RefCapId`/`RefActorId`/"
        "`RefEffectId` (15C.4, L35471–35473; no conversion is permitted inside "
        "reference semantics — harness-boundary mapping only, 15C.21). The "
        "independence audit's verdict `REF1-CONDITIONAL` is the current verification "
        "state of this contract (see `final/08`); it MUST NOT be represented as "
        "`REF1-PASS`."),
    18: ("Differential verification: normalized observations (R-REF-05), the "
        "harness boundary enforcement (R-REF-06), obligation-tagged semantic "
        "coverage (R-TEST-07), the crash-injection matrix (R-TEST-08), divergence "
        "adjudication (R-TEST-09), CI gates (R-TEST-10), final acceptance "
        "(R-TEST-11), and the request-frame tags (R-TEST-12). All of these are "
        "verification *contracts*. None has repository evidence: the comparison "
        "domain types (`Observed*`) remain undeclared (recorded, F-04/UNKNOWN), and "
        "coverage metrics never substitute for the differential oracle."),
    19: ("The mutation-testing regime: the frozen baseline registry M001–M018 plus "
        "the additive post-audit mutants (registry currently defined through M042), "
        "the 100 % kill-rate gate for non-equivalent mutants, and "
        "mutation-validation-of-the-verifier. The registry is a *specification "
        "artifact* in this repository: mutants are defined; none has been executed "
        "(no kill-rate may be claimed, R-TEST-05/06 remain SPECIFIED)."),
    20: ("The exhaustive small-state baseline (bounded enumeration at every commit; "
        "the CI time target is a performance budget, never a semantic constraint — "
        "coverage MUST NOT be reduced to meet it). R-TEST-01 canonically defines all "
        "three execution-mode baselines including the stress floors cited by §22."),
    21: ("The property-testing regime: layered randomized generation with "
        "reproducible counterexample artifacts and the ten-step shrinking order. "
        "R-TEST-02/03 are homed here as the property-suite mechanics; the mode "
        "baselines are §20's canonical text."),
    22: ("Stress testing. The canonical requirements (depth 50k–100k, 100+ "
        "actors, long mailboxes, large WAL traces, repeated crash/recovery, large "
        "continuation states) are defined once, inside R-TEST-01's **Stress** "
        "baseline (§20); this section is the regime index required by the FINAL1 "
        "canonical order and deliberately contains no restatement — the definitions "
        "above are single-homed and referenced by ID."),
    23: ("Global security invariants — the canonical consolidation of the machine's "
        "invariant layer. Each `GI-SEC-nn` row below is a *registry* entry: the "
        "normative statement lives in its defining requirement (single home); this "
        "table supplies the stable ID other sections reference, and "
        "`final/05` supplies variables, domains, quantifiers, and state/transition "
        "context. No invariant is redefined here; no negative guarantee is weakened."),
    24: ("Global determinism invariants, consolidated under stable `GI-DET-nn` IDs "
        "with `final/05` as their formal registry. The determinism theorem carries "
        "its recorded limitation (U-35: unfalsifiable as stated) verbatim; the "
        "δ_t/duration laws are the addendum-IX frozen forms."),
    25: ("Global recovery and persistence invariants, consolidated under stable "
        "`GI-REC-nn` IDs with `final/05` as their formal registry. The crash "
        "classification lattice and the no-silent-repair rule are referenced here, "
        "defined in §14/§15. `Indeterminate` is irreducible: no row below, and no "
        "document, may represent it as resolvable by local policy."),
    27: ("The verification registry: every obligation tag, mutation, conformance "
        "suite entry, milestone gate, and claim-ladder row, with repository "
        "evidence state. Canonical home: `final/04-verification-registry.md` "
        "(re-emitted from `spec/08`, which is the cleaned authority). The "
        "implementation-order obligations R-ORDER-01…05 are homed here because "
        "their acceptance criteria are verification gates; the crate-structure "
        "obligations R-REPO-01…03 are homed in §02 (architecture)."),
    29: ("Every unresolved item is listed in `final/09-open-architectural-decisions."
        "md` with its stable identity preserved (U-…, C-…, X-…, V-…, F-01…F-11, "
        "F-INFL-01…12, AMB-27/REQ-RECOV-021) plus the FINAL1-level symbol-reuse "
        "records `FA-01…FA-10`. FINAL1 resolved none of them. Addenda VII–IX and "
        "U-38 are not reopened (no owner authorization to reopen accompanies this "
        "compilation). Where two authoritative sources conflict and no owner "
        "decision exists, the conflict is recorded here rather than adjudicated."),
}

# Sections whose body is the verbatim transcription only (§26/§28 render
# curated text between the transcribed rows; handled specially by _build.py).

# --------------------------------------------------------------------------
# Global invariant registry (final/05; indexed into final/01 §23–25).
# home = canonical defining requirement (text lives there).
# xref = other requirements that must reference, not restate.
# --------------------------------------------------------------------------

GI_ROWS = [
 # ---------------- security ----------------
 dict(id="GI-SEC-01", family="SEC", name="No authority crosses to effect",
      formula="`LLMOutput ∧ UntrustedInput ↛ ExternalEffect`",
      home="R-CORE-01", xrefs=["R-CORE-02", "R-TRUST-01", "R-TRUST-02", "R-PLANNER-02", "R-CLAIM-01"],
      vars="`LLMOutput` — any planner output object; `UntrustedInput` — any `Block` data; `E` — any host-visible effect event",
      dom="over all runs of the machine; `E` ranges over host-visible effect events",
      quant="∀ run, ∀ E: `LLMOutput ∧ UntrustedInput ⇒ ¬ExternalEffect(E)` absent the §02 chain",
      ctx="machine-wide, every transition sequence; the central *negative* guarantee",
      note="Negative guarantee: MUST NOT be weakened for textual simplification; the "
           "authority audit's `SEC-001` class found it non-holding at specification "
           "level and the frozen addenda remediated at the normative layer — the "
           "guarantee stands as specified, unproven (no implementation)."),
 dict(id="GI-SEC-02", family="SEC", name="External-effect chain (7 conjuncts)",
      formula="`ExternalEffect(E) ⇒ ValidatedPlan(P) ∧ Authorized(E,κ,t) ∧ CapabilityWithinCeiling(E) ∧ BudgetAvailable(E) ∧ DeadlineValid(E,t) ∧ HostPolicyOK(E) ∧ Issued(E)`",
      home="R-CORE-02", xrefs=["R-CORE-11", "R-EFFECT-01", "R-EFFECT-03", "R-CORE-14", "R-DUR-02", "R-TEST-09"],
      vars="`E` — effect; `P = plan(E)`; `κ` — holder capability map; `t` — `LogicalTime`",
      dom="`E` all host-bound effects; predicates per their canonical signatures",
      quant="invariant over every transition (not a per-phase gate): the chain must hold for every observed `ExternalEffect`",
      ctx="request-transition composition, gates 1–16 (`R-EFFECT-01`/`R-CORE-14` ordering)",
      note="Canonical predicate signatures are frozen by R-CORE-11: `ValidatedRequest(E) ⇒ ValidatedPlan(plan(E))` and holder-first `Authorized(holder, c, E, t)`; "
           "plan-time-only or authority-first readings MUST NOT be substituted (differential adjudication R-TEST-09 binds to this form)."),
 dict(id="GI-SEC-03", family="SEC", name="No unauthorized effects",
      formula="`¬Authorized(A,E,t) ⇒ ¬ExternalEffect(E)`",
      home="R-CORE-03", xrefs=["R-CAP-06", "R-EFFECT-02"],
      vars="`A` — exercising authority per the canonical holder-possession form (R-CORE-11/R-KERN-04)",
      dom="all effect requests", quant="∀ E at every time `t`",
      ctx="authorization gate; equivalently `¬Authorized ⇒ ¬Request` operationally",
      note="mod/18 D-08: canonical algebraic predicate in R-CAP-06; the machine-level "
           "oblation is this row. Both homes kept; no restatement elsewhere."),
 dict(id="GI-SEC-04", family="SEC", name="No authority amplification",
      formula="`derive(A,C) ≼ A`",
      home="R-CAP-05", xrefs=["R-CORE-04", "R-ACTOR-09", "R-CAP-03"],
      vars="`A` — authority (`{(o,⟨S,Q,R,T⟩)}`); `C` — `Constraint`/`AdmissibleConstraint`",
      dom="∀ A, ∀ admissible C; ill-formed C ⇒ derivation undefined (R-CAP-10 totality clause)",
      quant="∀ A, C: the meet law holds pointwise per operation",
      ctx="kernel derivation; every attenuation at spawn/delegation sites",
      note="mod/18 D-01 canonicalized this invariant at the algebraic home (R-CAP-05); "
           "the spawn strictness `Authority(child) ≺ Authority(parent)` (R-ACTOR-09) is a "
           "*separate* strengthening, not this row; `≼` vs `≺` are distinct relations — do not conflate."),
 dict(id="GI-SEC-05", family="SEC", name="Revocation lineage",
      formula="`Valid(c,t) ⇔ Live(c) ∧ t ∈ Lifetime(c) ∧ ∀a ∈ Ancestors(c): Live(a)`",
      home="R-CAP-07", xrefs=["R-PERSIST-07", "R-CAP-09", "R-KERN-02"],
      vars="`c` — `CapRef`; ancestor chain in the kernel arena",
      dom="every capability with lineage depth d; check is O(d) lazy",
      quant="∀ c live-checked at gate time and at recovery",
      ctx="authorization gate; recovery revalidation (`RECOVERY-REVOCATION-DURABLE`)",
      note="Lifetime is logical (`LogicalTime`, half-open `[start, end)`) per R-CAP-11 "
           "(addendum IX resolved U-36). Revocation monotonic across crashes — a revoked "
           "capability never revalidates without a new explicit grant."),
 dict(id="GI-SEC-06", family="SEC", name="Budget conservation (no teleportation)",
      formula="`C_available + C_escrowed + C_consumed = C_initial` (global form `Σ_actors C_consumable + Σ_escrow C_escrow + Σ_issued C_issue = C_global_initial`)",
      home="R-BUDGET-05", xrefs=["R-CORE-05", "R-ACTOR-08", "R-BUDGET-11", "R-RECOV-06"],
      vars="`C_*` — per-actor consumable partitions; root budget minted once at init",
      dom="every reachable state, every partition transition",
      quant="invariant: after every step; across crashes (GI-REC-05) it must survive identically",
      ctx="every budget debit/escrow/refund transition (Op-01…Op-22 per R-BUDGET-10)",
      note="mod/18 D-02 canonical home is R-BUDGET-05. `audit/_conservation_checker.py` "
           "passing is a structural gate on the *rules*, not machine evidence; promotion "
           "forbidden (R-CORE-05 row stays SPECIFIED)."),
 dict(id="GI-SEC-07", family="SEC", name="Durable-before-host",
      formula="`HostInvoked(E) ⇒ DurableIssued(E)`",
      home="R-DUR-01", xrefs=["R-CORE-06", "R-DUR-02", "R-DUR-06", "R-DUR-07", "R-CORE-14"],
      vars="`E` — effect; `DurableIssued` — durable `Issued` record under 15A framing",
      dom="every host invocation path, including supervisor/reconciliation (R-RECOV-08: no exception)",
      quant="∀ E: host call without durable `Issued` is a conformance failure",
      ctx="issuance transaction steps 1–7 (R-DUR-02), journal-driven commit (R-DUR-07)",
      note="mod/18 D-03 canonical home is R-DUR-01; an in-memory object never satisfies "
           "`Issued` (R-CORE-06). The crate-DAG carrying of this hinge is frozen "
           "structurally by R-TRUST-05."),
 dict(id="GI-SEC-08", family="SEC", name="No raw capability transfer",
      formula="`marshal_value(v) ⇒ Err(MarshalFault::CapabilityRequiresDelegation)` if `contains_capability(v)`; `OrdinaryMarshal(Value::Capability) ⇒ Rejected`",
      home="R-MARSHAL-01", xrefs=["R-CORE-07", "R-MARSHAL-02", "R-MARSHAL-04", "R-MARSHAL-05", "R-MARSHAL-06", "R-CANON-12"],
      vars="`v` — any value crossing an actor/machine boundary (messages, receipts, snapshots, replay)",
      dom="unbounded structural depth incl. `FunctionValue.env` captured environments",
      quant="∀ crossings; exclusion only for kernel-sealed delegation envelopes",
      ctx="`Send`/`marshal`/`unmarshal`, decode-side admission, mailbox and snapshot byte paths",
      note="mod/18 D-04 canonical home is R-MARSHAL-01. Boundary invariant is stated "
           "over reachability (`marshal(v)=Ok ⇒ ¬∃c. Reachable(env_of(v), c)`, R-MARSHAL-06); "
           "the decode side (R-CANON-12) makes the boundary symmetric."),
 dict(id="GI-SEC-09", family="SEC", name="Receipt causality",
      formula="`Resume ⇒ id = id_pending ∧ effect_digest = digest_pending ∧ (R-HOST-06) result_digest = ResultDigest(result)`",
      home="R-EFFECT-06", xrefs=["R-EFFECT-07", "R-EFFECT-08", "R-HOST-03", "R-HOST-06", "R-HOST-04"],
      vars="`EffectReceipt {id, effect_digest, result}` (+ durable `result_digest` conjunct)",
      dom="every receipt on live and replay paths; result payload ∈ canonical data domain",
      quant="∀ receipts: mismatch ⇒ `ReplayCorruption`-family fault, no resume, no release",
      ctx="completion transition; replay step consumption",
      note="R-EFFECT-08: a receipt completes an effect, it never confers authority — "
           "capability/closure payload admission faults before resumption."),
 dict(id="GI-SEC-10", family="SEC", name="Gate short-circuit atomicity",
      formula="denial at any gate ⇒ subsequent gates not called, `next_effect_id` unchanged, budget unchanged, event log unchanged, `HostExecutor::execute` never invoked",
      home="R-EFFECT-04", xrefs=["R-CORE-12", "R-CORE-14", "R-BUDGET-10", "R-DUR-07"],
      vars="the five assertions of R-EFFECT-04 evaluated per gate 1–16",
      dom="every denial, including persistence-failure denials (R-DUR-07) and mailbox admission (R-ACTOR-10 sender-fault path)",
      quant="∀ denial events: Σ′ = Σ with the declared fault observable",
      ctx="request transition; live journal failure path (pre-s12 rollback)",
      note="Faults are data (never panics, R-CORE-12); resource-state atomicity is the "
           "resource-level refinement (R-BUDGET-10). The post-issuance host-failure path "
           "is the one declared exception shape (`c_issue` stays consumed)."),
 dict(id="GI-SEC-11", family="SEC", name="Planner observation opacity",
      formula="`contains_capability(Observation) = false` (recursive, events included); `Capability ∉ Observables(LLM)`; planner-visible `EffectIssued` carries `{id, actor, digest}` only",
      home="R-PLANNER-07", xrefs=["R-KERN-03", "R-MARSHAL-06", "R-PLANNER-01"],
      vars="`Observation` — planner-facing projection; `CapabilitySummary` — non-referential projection",
      dom="every machine state and observation emission; canonical encodings of planner-facing data",
      quant="∀ states, ∀ emissions", ctx="agent loop (ror-agent); observation projection rule",
      note="0x30/0x05 payloads absent from planner-facing encodings by property, not by "
           "convention; negative golden vectors are normative fixtures (R-CANON-11/12)."),
 dict(id="GI-SEC-12", family="SEC", name="LLM non-authority",
      formula="`LLMOutput ∈ Data`; `LLM output ∉ TCB authority`; planner MUST NOT allocate/authorize/modify/invoke",
      home="R-PLANNER-02", xrefs=["R-TRUST-01", "R-TRUST-02", "R-PLANNER-01", "R-KERN-06", "R-ARCH-01"],
      vars="planner — probabilistic proposal engine",
      dom="all planner outputs, all loop iterations", quant="∀ planner interaction",
      ctx="agent loop entry to the ordinary compile path only",
      note="Negative guarantee, preserved at full strength: the R-TRUST-04 addendum also "
           "bars the planner module from *providing* any security/runtime dependency — "
           "security obligations are never discharged inside LLM-facing crates."),
 dict(id="GI-SEC-13", family="SEC", name="Proposal staleness is exact-equality causal binding",
      formula="`AcceptProposal(p) ⇔ p.observation_sequence = current_planning_epoch` (either-direction mismatch ⇒ `Fault::StalePlan`, zero mutation)",
      home="R-PLANNER-06", xrefs=["R-PLANNER-03", "R-PLANNER-05", "R-CORE-12"],
      vars="`p.observation_sequence`, `current_planning_epoch`",
      dom="every proposal acceptance; future-tagged proposals included", quant="∀ p",
      ctx="planner boundary, pre-compilation",
      note="Superseded strictly-less reading is quoted, not deleted; the C-38 "
           "single-check description is corrected by this addendum — recorded."),
 dict(id="GI-SEC-14", family="SEC", name="Fault totality and transition atomicity",
      formula="`Σ →_c Σ'` either completes (all durable effects appended) or faults with the five R-EFFECT-04 assertions; no died-mid-transition outcome; every fallible op returns `Result`; `unwrap`/`expect`/`panic!` forbidden on machine paths",
      home="R-CORE-12", xrefs=["R-EFFECT-04", "R-BUDGET-02", "R-REPO-03", "audit/_conservation_checker.py"],
      vars="every machine transition; `Fault::InternalInvariant` family for check/commit drift",
      dom="evaluator, kernel, budget, persistence, runtime transitions (non-test paths)",
      quant="∀ transitions, ∀ failure modes", ctx="trusted boundary",
      note="The mid-transition window is removed, not merely its panic failure mode "
           "(journal-driven commit). Mutation M034 registered; no execution evidence — "
           "stays SPECIFIED."),
 dict(id="GI-SEC-15", family="SEC", name="Closed declared fault surface",
      formula="every trust-boundary crossing's fault set is frozen and declared; opaque codes/digests only for external error text; resume-vs-fault/budget/log effects pinned per variant",
      home="R-CORE-13", xrefs=["R-CALC-06", "R-EFFECT-08", "R-REF-05", "R-DUR-07"],
      vars="machine-fault enumeration incl. replay-path variants, `StalePlan`, unified `MarshalFault`, `InternalInvariant` family",
      dom="host→machine, storage→recovery, planner→machine crossings",
      quant="∀ crossing, ∀ fault variant", ctx="fault construction and differential fault comparison",
      note="U-08/U-14 remain OPEN (declared-surface work continues); the closed-set "
           "*rule* is frozen while the enumeration work is tracked — the addendum "
           "closes them only `in the security direction`, and this row preserves that "
           "distinction (no upgrade of the register rows)."),
 dict(id="GI-SEC-16", family="SEC", name="Kernel possession gate",
      formula="`Authorized_gated(actor, c, E, t) ⇔ c ∈ CapabilityContext(actor) ∧ Valid(c,t) ∧ Authorized(κ(c), E, t)`; `CapRef ≠ authority ownership`",
      home="R-KERN-04", xrefs=["R-KERN-01", "R-KERN-02", "R-KERN-03", "R-KERN-05", "R-KERN-06", "R-CAP-06"],
      vars="`CapRef {index, generation}`; per-actor possession structure",
      dom="every authorization call; recovery must reconstruct possession sets first",
      quant="∀ authorize/derive calls", ctx="authorization gate 2–4 region; kernel API contract",
      note="Root grant protocol (R-KERN-06): authority enters only via durable "
           "`CapabilityGranted`; no runtime minting path — audit of every recovered root "
           "authority to its durable record is the verification obligation."),
 dict(id="GI-SEC-17", family="SEC", name="Spawn transfers no authority by default",
      formula="`Expr::Spawn` child authority = ∅ unless an explicit, compiler-checked, strictly attenuated manifest derivation; `Authority(child) ≺ Authority(parent)`",
      home="R-ACTOR-09", xrefs=["R-ACTOR-05", "R-COMPILE-06", "R-MARSHAL-05", "R-CORE-04"],
      vars="spawn manifest entries; `BudgetAllocationSpec::validate_and_escrow` bounds (U-03 direction, security only)",
      dom="all spawn transitions from any (incl. LLM-authored) plan",
      quant="∀ spawn", ctx="spawn transaction, step 3 (capability derivation)",
      note="Wholesale copying is FORBIDDEN (the `derive(A,⊤)=A` identity path is not "
           "spawn); the v0.3 `trust_level` form is superseded-quoted. U-03 stays open "
           "for the allocation-policy half — preserved in §29."),
 dict(id="GI-SEC-18", family="SEC", name="Trust table completeness and structural carriability",
      formula="one frozen trust table covering every boundary-enforcing module; crate DAG carries `ror-runtime → ror-persistence`; `ror-core → ror-kernel` forbidden; no security dependency provided by the planner",
      home="R-TRUST-04", xrefs=["R-TRUST-01", "R-TRUST-05", "R-REPO-02", "R-REPO-03", "R-ARCH-05"],
      vars="module rows; crate edges; `SECURITY_DEPENDENCY`/`RUNTIME_DEPENDENCY` edges",
      dom="repository structure (Cargo DAG, visibility, clippy gates)",
      quant="structural invariant — re-checkable by `dep/_graph.py` (SC-1/2/3 hard gates)",
      ctx="build-order and review", note="Verified *structurally* in this repository only; "
           "structural repository integrity is not semantic verification (R-SCOPE-02 discipline)."),
 dict(id="GI-SEC-19", family="SEC", name="Reference-model independence",
      formula="zero shared core implementation logic: no `reference_* → production_*` calls for step/authorize/budget/recover/encode/scheduler; shared fixtures MAY be used, shared transitions MUST NOT",
      home="R-SCOPE-04", xrefs=["R-REF-02", "R-REF-04", "R-RECOV-04", "R-ARCH-02"],
      vars="production↔reference boundary at crate, call, type-identity (`Ref*Id`) levels",
      dom="the whole verification architecture", quant="∀ differential comparison",
      ctx="build structure; harness",
      note="Current state: `REF1-CONDITIONAL` (audit verdict) — several independence "
           "properties UNVERIFIED (F-01…F-11), no BLOCKING failure; MUST NOT be "
           "rendered PASS (F-INFL-02, BLOCKING-if-converted). The reference model "
           "remains an architectural contract: no reference implementation exists and "
           "none is manufactured from this specification."),
 dict(id="GI-SEC-20", family="SEC", name="Actor isolation",
      formula="`a ≠ b ⇒ Heap(a) ∩ Heap(b) = ∅ ∧ Env(a) ∩ Env(b) = ∅`; no cross-actor mutation; fresh arenas, `Environment::empty()` (no implicit environment inheritance)",
      home="R-ACTOR-01", xrefs=["R-ACTOR-02", "R-ACTOR-10", "R-CALC-02"],
      vars="actors; heaps; environments; continuations; mailboxes",
      dom="every reachable global state", quant="∀ distinct actor pairs",
      ctx="instantiation, execution, messaging",
      note="Mailbox footprint bounded by reserved `M` (R-ACTOR-10) extends the isolation "
           "claim into the heap; the resource-bounded thesis holds at every step."),
 dict(id="GI-SEC-21", family="SEC", name="No unconstrained embedded capability literals",
      formula="compilation faults on any `Value::Capability` literal not substituted by the compiler from the plan's declared capability set",
      home="R-COMPILE-06", xrefs=["R-COMPILE-02", "R-COMPILE-03", "R-CAP-10", "U-22"],
      vars="`Block` literals; plan capability manifest",
      dom="all compilation", quant="∀ plans, ∀ embedded capability values",
      ctx="compiler capability analysis",
      note="Closes U-22 `in the security direction` only — the J2 effect-set-inference "
           "re-spec gap (U-22) stays open (§29)."),
 dict(id="GI-SEC-22", family="SEC", name="Rewinding-resistant persistence",
      formula="chained WAL checksums `checksum_n = H(checksum_{n−1} ‖ frame_n)`; snapshot commit covers state digest and last WAL sequence; keyed (MAC/signature) if storage adversarial; `Durable(D) ⇒ Authentic(D)` where keyed",
      home="R-PERSIST-08", xrefs=["R-PERSIST-02", "R-PERSIST-05", "R-CORE-13"],
      vars="WAL frames; snapshot commit records",
      dom="all durable artifacts; key-epoch mismatch ⇒ `RecoveryFault`",
      quant="∀ frames, ∀ snapshots", ctx="append, sync, recovery verification",
      note="Keyless chaining detects corruption/rewinding but does not authenticate — "
           "the trust-table assumption is recorded explicitly, not softened."),
 # ---------------- determinism ----------------
 dict(id="GI-DET-01", family="DET", name="Determinism theorem",
      formula="`InitialState + SchedulerTrace + HostTrace ⇒ UniqueMachineTrace` (machine level; with a `PlannerAccepted` trace for end-to-end runs, R-PLANNER-04)",
      home="R-CORE-08", xrefs=["R-ACTOR-07", "R-TEST-10", "N-32"],
      vars="the four boxed terms; stochasticity confined above the machine boundary",
      dom="all machine executions under identical inputs",
      quant="uniqueness over full traces, not final states only",
      ctx="state-transition semantics; scheduler; host observation",
      note="PRESERVED LIMITATION (U-35, C-98/C-99, open): the four terms are undefined "
           "in all 42,312 source lines and in all five canonical organizations — the "
           "unqualified theorem is currently *ill-formed/unfalsifiable*. The compilation "
           "records this and does not fix it by defining the terms (R-SCOPE-03). "
           "U-36 (Lifetime) is resolved by R-CAP-11; U-37 (fixed integer widths) stays open."),
 dict(id="GI-DET-02", family="DET", name="Deterministic identity allocation",
      formula="`ActorId`/`EffectId` from global monotonic counters (`N' = N + 1`); never wall-clock, address, UUID, PID, thread-id, or RNG",
      home="R-ACTOR-03", xrefs=["R-EFFECT-03", "R-CALC-03"],
      vars="`N` counters; `Symbol(u32)` interned identity",
      dom="every allocation site (spawn, request)", quant="∀ allocations, deterministically ordered",
      ctx="global-state transitions", note="`Symbol` interning is the compiler-side half "
           "(R-CALC-03); runtime identity never uses `String` keys."),
 dict(id="GI-DET-03", family="DET", name="FIFO scheduler, at-most-once runnable",
      formula="runnable queue is FIFO with at-most-once membership; `Blocked/Pending/Halted/Faulted` actors are never scheduled; deterministic wake-exactly-once",
      home="R-ACTOR-04", xrefs=["R-ACTOR-06", "R-ACTOR-07", "SCHED-FIFO", "SCHED-BLOCKED-NOT-SCHEDULED"],
      vars="`RunnableQueue`; actor run-states",
      dom="every scheduler turn", quant="∀ turns",
      ctx="global step", note="At-most-once and wake-exactly-once are the mutation-tested "
           "shadows (M011/M012). Duplicate runnable entries MUST NOT exist."),
 dict(id="GI-DET-04", family="DET", name="Logical time only",
      formula="`t` ∈ machine state (logical clock); wall-clock MUST NOT be semantic machine state",
      home="R-CAP-09", xrefs=["R-BUDGET-06", "R-CAP-11", "R-BUDGET-15", "R-BUDGET-16", "N-18", "N-33"],
      vars="`t`, `δ_t`, `W`, `D`, `Lifetime` (logical, half-open per R-CAP-11)",
      dom="every time-consuming predicate (authorization `T`, deadline `W`, liveness bound)",
      quant="∀ transitions", ctx="machine-wide",
      note="The wall-clock `Lifetime` compared inside gate 6 was a determinism defect "
           "(DET-002/C-100) — resolved in the logical direction by R-CAP-11 (addendum IX); "
           "`LogicalTime ≠ Deadline` and `Lifetime ≠ WallClockInterval` are laws N-18/N-33."),
 dict(id="GI-DET-05", family="DET", name="One δ_t, one duration debit; quiescence rule",
      formula="every logical-time advance has exactly one `δ_t` (frozen enumeration) and exactly one `ΔD := δ_t` debit; `Deadlock ∧ ∃Pending ⇒ QuiescenceReconcile (δ_t = 0, ΔD = 0)`",
      home="R-BUDGET-16", xrefs=["R-BUDGET-06", "R-BUDGET-15", "R-BUDGET-09", "R-RECOV-08", "R-CAP-09"],
      vars="transition kinds; `Pending` effects; `GlobalStep::Deadlock`",
      dom="every transition kind; unknown kinds are a checker error, never a default",
      quant="∀ transitions, ∀ global advances", ctx="scheduler; liveness bound reachability",
      note="Addendum-IX frozen form (D7 condition discharged per the duration audit's §5 "
           "evidence). Post-deadline receipts admitted and settled via R-RECOV-08 — the "
           "old `t + δ_t ≤ W` receipt premise is superseded-quoted. Blocked-only quiescence "
           "admits NO reconciliation."),
 dict(id="GI-DET-06", family="DET", name="One canonical encoding grammar",
      formula="exactly one byte grammar (Phase 15A BE envelope); all digests/checksums over 15A bytes alone; `Canonical(x) = Canonical(y) ⇒ Digest(x) = Digest(y)`",
      home="R-CANON-13", xrefs=["R-CANON-01", "R-CANON-02", "R-CANON-09", "R-CANON-10", "R-PERSIST-01"],
      vars="envelope fields; `TAG_*` single namespace; digest functions",
      dom="all serialized payloads (values, effects, records, snapshots, journal)",
      quant="∀ encoders (production, reference, persistence writer) — golden vectors byte-exact, LE variants rejected",
      ctx="serialization; persistence framing; differential comparison",
      note="Injectivity is a *scoped structural* claim with machine-checked evidence "
           "expected (R-CANON-10) — not a mathematical proof; reverse digest direction holds "
           "only under collision-resistance assumption (C-13). The machine-state encodings "
           "(U-02) remain UNFROZEN: byte-level determinism of `GlobalState` is an open item, "
           "not a closure (it also blocks StateDigest operationalization; U-02 amended by the "
           "nondeterminism audit)."),
 dict(id="GI-DET-07", family="DET", name="Replay correspondence",
      formula="`LiveRun(Σ₀) ⇒ T ⇒ ReplayRun(Σ₀, T)` produces the same final configuration, per-step `E_replay,k = E_recorded,k ∧ R_replay,k.id = R_recorded,k.id` (digests in the frozen form)",
      home="R-HOST-04", xrefs=["R-HOST-03", "R-HOST-05", "R-PLANNER-04", "R-EFFECT-06", "R-HOST-06"],
      vars="`T` — ordered trace of (EffectIssued, EffectCompleted) pairs; `ReplayHost` consumption",
      dom="machine-state replay always; real-world replay only for reversible/idempotent classes",
      quant="∀ recorded runs", ctx="replay; conformance suite end-to-end replay",
      note="Replay proves machine-state/event reproduction subject to explicit external-"
           "effect reconciliation — it does NOT reproduce the external world (nondeterminism "
           "audit §5.4, preserved). Unordered-map replay is superseded (R-HOST-03)."),
 # ---------------- recovery & persistence ----------------
 dict(id="GI-REC-01", family="REC", name="Effect journal causality",
      formula="`Issued ⇒ Prepared`; `Completed ⇒ Issued`; `Reconciled ⇒ Issued`; `Prepared ∧ ¬Issued ⇒ Discard`; `Issued ∧ ¬Completed ⇒ Indeterminate`",
      home="R-DUR-03", xrefs=["R-DUR-04", "R-RECOV-02", "N-05", "N-24", "audit/_crash_consistency_checker.py"],
      vars="journal record kinds; identical `(EffectId, EffectDigest)` per effect",
      dom="every durable effect record and recovery classification",
      quant="∀ effects, ∀ crash points T0–T6", ctx="issuance transaction; recovery",
      note="Digest mismatch on a subsequent record is `EffectJournalCorruption`, never a "
           "different effect. The persistence audit verified the *contract* (specification-"
           "level causal ordering) — that is audit verdict language, not VERIFIED status."),
 dict(id="GI-REC-02", family="REC", name="Crash recovery equivalence (qualified)",
      formula="`Recover(Snapshot, EventLog, EffectJournal) ≡ PreCrashMachineState` at every defined persistence boundary, PROVIDED every interrupted effect is (a) durably reconciled, (b) idempotent/replayable via recorded receipt, or (c) explicitly `Indeterminate` and prevented from silent continuation",
      home="R-CORE-09", xrefs=["R-RECOV-01", "R-RECOV-02", "R-RECOV-03", "R-RECOV-08", "R-REF-01"],
      vars="`D = ⟨S,L,H⟩`; replay; classification lattice",
      dom="crashes at defined boundaries only (T0–T6)",
      quant="∀ defined crash points", ctx="recovery algorithm steps 1–12",
      note="`MUST NOT infer \"not executed\" from a missing completion record` is part of "
           "the invariant (R-CORE-09/R-DUR-04/R-RECOV-07). The recovery-step granularity "
           "discrepancy (AMB-27/REQ-RECOV-021: reconciliation inside `Recover(D)` vs after "
           "`RecoveryComplete`) is recorded open (§29; persistence audit residual)."),
 dict(id="GI-REC-03", family="REC", name="No silent repair",
      formula="`Invalid(D) ⇒ RecoveryFault`; recovery MUST NOT drop duplicate runnable actors, adjust budget mismatches, ignore sequence gaps, or ignore checksum failures",
      home="R-RECOV-05", xrefs=["R-CORE-10", "R-PERSIST-06", "R-PERSIST-08", "R-RECOV-09"],
      vars="corruption classes; stale-counter reconstruction",
      dom="every recovery run; counter *advancement* is recorded, never silent (R-RECOV-09)",
      quant="∀ invalid durable states", ctx="recovery validation steps",
      note="mod/18 D-07 canonical home R-RECOV-05. A snapshot counter greater than the "
           "journal maximum is a fault; `SnapshotCommit` inside the s12–14b section is a fault."),
 dict(id="GI-REC-04", family="REC", name="Escrow survives crash; disposition total",
      formula="`Issued ∧ ¬Completed ⇒ escrowed complete_max retained until durable reconciliation`; every escrowed unit leaves via exactly one frozen path (`Completed` / host-failure consumption / durable `Reconciled`); `Remains-Indeterminate` is a bounded transient",
      home="R-DUR-05", xrefs=["R-BUDGET-09", "R-BUDGET-11", "R-DUR-06", "R-BUDGET-16", "R-RECOV-08"],
      vars="`C_escrowed`; per-effect `EffectCost` reconstructed from durable payload",
      dom="all crash points; live faults unify with crash reconciliation",
      quant="∀ escrow entries; quiescent states contain no un-movable escrow",
      ctx="issuance; recovery; quiescence driver",
      note="R-DUR-06 (durable payload with cost) is what makes survival reconstructible at "
           "every T0–T6 point — before addendum VII the persistence audit called escrow "
           "survival *realizable but unprovable-as-frozen*; that history is preserved in the "
           "C-103…C-109 lineage, and current status remains SPECIFIED."),
 dict(id="GI-REC-05", family="REC", name="Budget and counter restoration",
      formula="three-way partition invariant survives crashes identically; `next_effect_id = max({id ∈ replayed EffectIssued}) + 1` (stale counter advanced and recorded; greater-than-journal ⇒ `RecoveryFault`)",
      home="R-RECOV-06", xrefs=["R-RECOV-09", "R-BUDGET-05", "R-RECOV-03"],
      vars="budget partitions; effect-ID counter",
      dom="every recovery", quant="∀ recovered states",
      ctx="recovery steps 4/11", note="T1 discard restores from the record (R-DUR-06); no "
           "budget discrepancy may be silently adjusted; restoration has a source of truth "
           "(pre-addendum-VII it had none — recorded in C-105 lineage)."),
 dict(id="GI-REC-06", family="REC", name="Indeterminate irreducibility",
      formula="`Indeterminate` is resolvable ONLY by authoritative host reconciliation evidence; no component (trusted or not) may resolve `Indeterminate ⇒ NotExecuted` (or ⇒ `Completed`) on local policy",
      home="R-RECOV-08", xrefs=["R-DUR-04", "R-RECOV-07", "R-CORE-09", "N-24", "R-CLAIM-02"],
      vars="`ReconciliationOutcome {Completed(EffectReceipt), NotExecuted, Indeterminate}` (closed set, L26593–26597; per-class admissibility = U-15's remaining question)",
      dom="interrupted effects; supervisor policy",
      quant="∀ outcomes", ctx="reconciliation protocol",
      note="Receipts recorded what the machine was TOLD, not what happened; the Indeterminate "
           "class is irreducible (nondeterminism audit §5.4). R-RECOV-08 freezes never-re-execute, "
           "idempotent-query-at-most, and `NotExecuted` gated behind authoritative evidence."),
 dict(id="GI-REC-07", family="REC", name="Sequence continuity and snapshot atomicity",
      formula="`s_{n+1} = s_n + 1` (gap ⇒ reject); snapshot atomic protocol `Begin → payload → fsync → Commit(state_digest)`; incomplete snapshots discarded; WAL payload is *only* 15A bytes",
      home="R-PERSIST-06", xrefs=["R-PERSIST-01", "R-PERSIST-02", "R-PERSIST-05", "R-DUR-07"],
      vars="`WalSequence`; snapshot markers; `state_digest`",
      dom="all durable writes; the persistence layer records and reconstructs; it is not a semantic machine",
      quant="∀ frames, ∀ snapshots", ctx="append path; recovery scan",
      note="`No secondary serialization` (R-PERSIST-01) plus U-02: until machine-state "
           "encodings are frozen, `state_digest` is required but uncomputable per the "
           "register — recorded open, both facts stand."),
]

# --------------------------------------------------------------------------
# Mathematical symbols: canonical meanings (final/05 §2; FINAL1 §04 pointers).
# --------------------------------------------------------------------------

SYMBOL_ROWS = [
 ("`E`", "a single effect (request/issued/completed lifecycle object)", "R-CALC-04; R-CORE-02", ""),
 ("`P`", "the executable plan under which an effect was requested", "R-CORE-02 (homonym resolved by R-CORE-11)", "FA-10 pointer: `ValidatedPlan` type-vs-predicate split lives at X-01/C-46, not here"),
 ("`Σ`, `Σ′`, `Σ₀`", "local configuration `⟨e, ρ, κ, B, t, H, L⟩` (and post-state/initial)", "R-CALC-08", ""),
 ("`G`", "global configuration `⟨A, t, L, R, E_journal⟩`", "R-CALC-08", "overloaded `A`/`L`/`R` uses resolved per FA-01/FA-04"),
 ("`D` (budget)", "the duration consumable: per-actor remaining execution-duration budget", "R-BUDGET-01/15", "FA-02: `D = ⟨S,L,H⟩` (durable state, R-RECOV-01) is a different object reusing the letter"),
 ("`D` (durable)", "durable recovery input `⟨S, L, H⟩`", "R-RECOV-01", "FA-02"),
 ("`B`", "the actor budget `⟨C, R, W⟩`", "R-BUDGET-01", "FA-09: static bound `@ B`/`B_max` in the compilation judgment (R-COMPILE-03) is the plan-time upper bound, not the dynamic `B`"),
 ("`C` (budget)", "the consumable vector `⟨F, I, D⟩` and its partitions `C_available/C_escrowed/C_consumed`", "R-BUDGET-01/05/11", "FA-07: bare `C` is ALSO the `Constraint` argument of `derive(A,C)` (R-CAP-05)"),
 ("`R` (budget)", "the reserved-capacity vector `⟨M, S⟩`", "R-BUDGET-01", "FA-04: `R_A` is the capability resource ceiling (R-CAP-06); `R` is the third component of `G` (R-CALC-08)"),
 ("`W`", "absolute logical-time deadline, `ℕ ∪ {∞}`; `Deadline(None)` = ∞", "R-BUDGET-01; N-18", ""),
 ("`M`, `S` (budget)", "reserved memory bytes; reserved concurrency slots", "R-BUDGET-01", "FA-05: `S` is also the scope domain (R-CAP-01) and the snapshot component (R-RECOV-01)"),
 ("`t`", "logical time (machine state, never wall clock)", "R-CAP-09", ""),
 ("`δ_t(c)`", "the frozen logical-time delta of transition `c` (exhaustive table)", "R-BUDGET-06/16", ""),
 ("`ΔD`", "the duration debit for a logical-time advance (`ΔD := δ_t`, exactly one)", "R-BUDGET-15", ""),
 ("`κ`", "the holder's capability context map (`κ_holder(c) → Authority`)", "R-CORE-02; R-KERN-02; canonical signature by R-CORE-11", ""),
 ("`ρ`", "local environment (name → value bindings)", "R-CALC-08; R-CEK-03/04", ""),
 ("`A` (algebra)", "authority `= {(o, ⟨S,Q,R,T⟩)}`, operation-indexed", "R-CAP-01/02", "FA-01: `A` in `G = ⟨A, …⟩` is the actor map — same letter, different object"),
 ("`O`", "the finite enumerable operation set (`O_granted ⊆ O`)", "R-CAP-01/02", ""),
 ("`S` (scope), `Q`, `T`", "scope domain with interpretation `⟦A_op.S⟧`; parameter predicate; logical lifetime interval", "R-CAP-01/06; R-CAP-11 (half-open)", "FA-05; FA-10 (T0–T6 crash labels are subscripts, distinct from lifetime `T`)"),
 ("`≼`", "authority partial order (per-operation meet comparison)", "R-CAP-03", ""),
 ("`≺`", "strict authority order (spawn security theorem only)", "R-ACTOR-09", "`≼` is reserved for delegation — the two are NOT interchangeable"),
 ("`⊓`", "meet within a semantic domain", "R-CAP-05", ""),
 ("`⇒`, `⇔`, `∧`, `¬`, `∀`, `∃` / `□`", "implication; equivalence; conjunction; negation; quantifiers; `□` = “invariant over all reachable states” (used in this registry only)", "final/05 notation", ""),
 ("`↛`, `⇏`", "does not (entail / imply): the negative guarantees", "R-CORE-01; R-COMPILE-01 (`Block ⇏ ExecutablePlan`)", ""),
 ("`≻`", "version-supersession ordering of source texts (editorial notation only; not machine semantics)", "spec/00 §6", ""),
 ("`ε`", "the empty continuation (`Value ∧ K = ε ⇒ Halt`)", "R-CEK-02", ""),
 ("`K`", "continuation", "R-CEK-01/02/03", ""),
 ("`c`", "a capability reference/`CapRef` handle when bounded by possession (gate form)", "R-KERN-04; R-CORE-11", "also the transition label in `Σ →_c Σ'` (R-EFFECT-02); context decides"),
 ("`e`", "the current term under evaluation in `Σ`", "R-CALC-08", "FA-08: `Authorized(c, e, t)` (R-EFFECT-01 step 4) uses `e` for the effect; canonical effect symbol is `E`"),
 ("`V`, `v`", "value-domain element of the machine (11 variants)", "R-CALC-01", ""),
 ("`derive`, `attenuate`, `delegate`", "algebra operation; machine CEK operation; cross-actor authority transfer", "R-CAP-05; R-CEK-03; R-MARSHAL-02/05; N-29", "three names, three distinct operations — never conflated"),
 ("`marshal` / `unmarshal`", "boundary crossing with capability rejection / admission revalidation", "R-MARSHAL-01/03/06", ""),
 ("`contains_capability(v)`", "the frozen total predicate over reachability", "R-MARSHAL-06", ""),
 ("`Canonical(x)`, `StateDigest`, `EffectDigest`, `ResultDigest`", "15A bytes; SHA-256 digests over canonical bytes", "R-CANON-09/13; R-HOST-06", ""),
 ("`ExternalEffect`, `HostInvoked`, `DurableIssued`, `Prepared`, `Issued`, `Completed`, `Reconciled`", "event/record predicates with exactly the signatures defined in §02/§11/§13/§15", "R-CORE-02/11; R-DUR-03; R-EFFECT-*", ""),
 ("`ValidatedRequest(E)`, `ValidatedPlan_pred(P)`", "request-time validation predicate; disambiguated plan-predicate reading", "R-CORE-11", "type homonym `ValidatedPlan_struct` is X-01/U-23 — predicate and struct never interchangeable"),
 ("`Authorized(...)`, `Authorized_gated(...)`", "canonical authorization forms (holder-first)", "R-CORE-11; R-KERN-04", "authority-first `Authorized(A,E,t)` reading SUPERSEDED (quoted in R-CORE-11)"),
 ("`Live(c)`, `Ancestors(c)`", "kernel liveness; lineage chain", "R-CAP-07", ""),
 ("`Recover(D)`, `Replay(S,L,H)`, `LiveRun`, `ReplayRun`", "recovery/replay functions", "R-RECOV-01; R-HOST-04", ""),
 ("`N`", "the monotonic allocation counter (`N' = N + 1`)", "R-EFFECT-03; R-ACTOR-03", ""),
 ("`f`", "the frozen monotone per-byte send-cost lower bound", "R-ACTOR-10", ""),
 ("`Γ`", "typing context in the compilation judgment", "R-COMPILE-03", ""),
 ("`F` (judgment)", "the possible-effects set (conservative over-approximation; pure ⇒ `F = ∅`)", "R-COMPILE-03", "FA-06: also `F` = fuel dimension (R-BUDGET-01) and v1 fault grammar `F` (C-58)"),
 ("`⟦·⟧`", "scope interpretation", "R-CAP-06", ""),
]

# --------------------------------------------------------------------------
# FA-nn: FINAL1-level symbol-reuse records (preserved ambiguities). These do
# not create U-nn items (spec/09 owns that register); they record what the
# compilation found and leave adjudication to the owner.
# --------------------------------------------------------------------------

FA_ROWS = [
 dict(id="FA-01", symbol="`A`",
      uses="authority tuple (R-CAP-01, source L6354–6379) vs the actor map component of `G = ⟨A, t, L, R, E_journal⟩` (R-CALC-08, L24148–24163)",
      rule="Within FINAL1 rendering, `A` alone = authority; the actor map appears only inside the named tuple `G`. No renaming of the source formulas is performed.",
      status="preserved; notation-level, owner may fold into a future editorial pass"),
 dict(id="FA-02", symbol="`D`",
      uses="duration consumable (R-BUDGET-01, frozen semantics R-BUDGET-15) vs durable-state `D = ⟨S, L, H⟩` / `Recover(D)` (R-RECOV-01)",
      rule="Budget contexts read `D` as the consumable; recovery contexts read `D` as the durable triple. R-BUDGET-15 disambiguates the *semantics* of the budget side (addendum IX) but the letter collision itself is a frozen-notation fact and stays recorded.",
      status="preserved"),
 dict(id="FA-03", symbol="`H`",
      uses="isolated heap component of `Σ` (R-CALC-08) vs durable effect journal `H` (R-RECOV-01)",
      rule="Disambiguated by tuple membership; never used bare outside a named configuration.",
      status="preserved"),
 dict(id="FA-04", symbol="`R`",
      uses="reserved-capacity vector `⟨M,S⟩` (R-BUDGET-01) vs capability resource ceiling `R`/`R_A` (R-CAP-01/06) vs the `G` component `R` (R-CALC-08)",
      rule="Subscripts (`R_A`, `R_max`) and tuple membership are the disambiguators; the ceiling conjunct of the authorization predicate is always cited as `cost ≤ A_op.R`.",
      status="preserved"),
 dict(id="FA-05", symbol="`S`",
      uses="reserved slots `R=⟨M,S⟩` (R-BUDGET-01) vs scope domain `S` in `⟨S,Q,R,T⟩` (R-CAP-01) vs snapshot component `S` (R-RECOV-01)",
      rule="Tuple membership disambiguates; `⟦A_op.S⟧` marks the scope reading explicitly.",
      status="preserved"),
 dict(id="FA-06", symbol="`F`",
      uses="fuel dimension of `C=⟨F,I,D⟩` (R-BUDGET-01) vs possible-effects set in the compilation judgment (R-COMPILE-03) vs the v1 fault grammar `F` (source L1949; recorded at C-58)",
      rule="FINAL1 text uses the long names (`fuel`, `possible-effects set`, `fault grammar`) outside formula quotes. C-58 already records the grammar-level homonymy; this row adds the budget/judgment overload. No symbol is renamed.",
      status="preserved; C-58 (X-68) remains the authoritative record for the taxonomy level"),
 dict(id="FA-07", symbol="`C`",
      uses="consumables vector (R-BUDGET-01) vs the `Constraint` argument in `derive(A, C)` (R-CAP-05)",
      rule="`C` bare = constraint only inside algebra formulas (`derive`, `Satisfies`); budget partitions always carry subscripts (`C_available`, …).",
      status="preserved"),
 dict(id="FA-08", symbol="`e`",
      uses="current term of `Σ` (R-CALC-08) vs effect instance in `Authorized(c, e, t)` (R-EFFECT-01 step 4)",
      rule="Canonical effect symbol is `E`; the step-4 `e` is transcribed verbatim from the cleaned authority and is *not* silently corrected.",
      status="preserved"),
 dict(id="FA-09", symbol="`B`",
      uses="dynamic actor budget (R-BUDGET-01) vs static plan-time upper bound `@ B`, `B_max` (R-COMPILE-03)",
      rule="Named forms (`B_max`) are used for the static bound; the judgment `Γ; κ_static ⊢ e : τ ! F @ B` is quoted as frozen notation.",
      status="preserved"),
 dict(id="FA-10", symbol="`T`",
      uses="lifetime component of `⟨S,Q,R,T⟩` (R-CAP-01, retyped logical by R-CAP-11) vs crash-point labels `T0…T6` (R-RECOV-02)",
      rule="Bare `T` = lifetime; `T<i>` subscripts = crash points. Noted as benign; recorded for completeness of the one-meaning audit.",
      status="preserved; benign-by-context, no action requested"),
]

# --------------------------------------------------------------------------
# Type definition homes (API & TYPE canonicalization; rendered in final/02).
# ("undeclared" rows record source-undeclared names per the term/ rule:
# reported, never filled in.)
# --------------------------------------------------------------------------

TYPE_HOMES = [
 ("`Value` (production)", "R-CALC-01", 4, ""),
 ("`Expr` (frozen AST)", "R-CALC-02", 4, "no `Delegate` constructor — the R-MARSHAL-05 delegation surface and the U-02 freeze scope quote the frozen AST unchanged"),
 ("`Symbol(u32)`", "R-CALC-03", 4, ""),
 ("`Effect`", "R-CALC-04", 4, ""),
 ("`EffectCost {issue, complete_max, reserve}`", "R-CALC-05", 4, ""),
 ("`Fault` taxonomy", "R-CALC-06", 4, "closed-set work tracked at U-08/U-14 (open)"),
 ("`Σ` / `G`", "R-CALC-08", 4, ""),
 ("`EvalState`", "R-CEK-01", 8, ""),
 ("`Frame` set", "R-CEK-03", 8, ""),
 ("`FunctionValue {params, body, env}`", "R-CEK-04", 8, "canonical encoding for snapshots: U-02 (open)"),
 ("`ExecutablePlan` (+ `Sealed`)", "R-ARCH-03 / addendum VI home note", 2, "crate home `ror-core`, compiler-only construction (V-01 resolved)"),
 ("`PlanSeal`", "addendum VI (unnumbered normative refinement in §02)", 2, ""),
 ("`PlanProposal`, `PlannerAccepted`", "R-PLANNER-01 / R-PLANNER-04", 16, "`PlannerMetadata`/`ProposalDigest` fields: U-13 (open)"),
 ("`Authority`", "R-CAP-01", 6, "field-set collision: U-31 (open)"),
 ("`Constraint` / `AdmissibleConstraint`", "R-CAP-04 / R-CAP-10", 6, "data-level encoding: U-02; trait status: U-09"),
 ("`CapRef {index, generation}`", "R-KERN-01", 6, "opaque; kernel-only construction"),
 ("`CapabilityContext`", "R-KERN-05", 6, "unit-type sketch superseded-quoted"),
 ("`CapabilityKernel`", "R-KERN-02", 6, ""),
 ("`Budget` / `Consumable` / `Reserved` / `Deadline`", "R-BUDGET-01", 7, ""),
 ("`EffectId` allocation", "R-EFFECT-03", 11, ""),
 ("`EffectReceipt`", "R-EFFECT-06", 11, ""),
 ("`EffectRequest` (transient host message)", "R-EFFECT-01 step 15 / spec/05 §1", 11, ""),
 ("`Envelope` (15A)", "R-CANON-02", 13, "one grammar only — R-CANON-13 (X-50/X-54 resolved at the normative layer)"),
 ("`CanonicalError`", "R-CANON-07", 13, "governing shape: U-29 (open)"),
 ("`MarshalledValue`", "R-MARSHAL-03", 13, "checked-bytes reading by R-MARSHAL-05; payload-type question U-30 (open)"),
 ("`DelegatedCapability` envelope", "R-MARSHAL-05", 13, "kernel-constructed; never a plain `Value` variant"),
 ("`WalRecord` / `WalFrame` / `WalSequence`", "R-PERSIST-02/03", 14, "`payload_length`/checksum domain: U-32 (open)"),
 ("`EventEnvelope` / `EventSequence`", "R-PERSIST-03", 14, "WAL relation: U-16 (open)"),
 ("`GlobalSnapshot`", "R-PERSIST-04/05", 14, "machine-state encoding: U-02 (open, largest gap)"),
 ("`ReconciliationOutcome`", "R-RECOV-07/08 (closed 3-variant set per U-15 correction, L26593–26597)", 15, "per-class admissibility: U-15 (open)"),
 ("`RunState` vs `ActorStatus`", "R-ACTOR-02/04 + spec/05 §3 (C-18; N-15)", 9, "two distinct enums; mapping implied, not stated — do not conflate"),
 ("`SchedulerState`", "R-ACTOR-04 (semantics) — shape undeclared", 10, "shape: U-02 (open)"),
 ("`CapabilitySummary`", "R-PLANNER-07 (frozen as non-referential projection)", 16, "type never declared in source (term/ rule 13; UNDECLARED) — projection *behavior* is specified, structure is not; recorded, not filled in"),
 ("`Observed*` comparison types", "R-REF-05 (normalized-observation contract) — shapes undeclared", 18, "X-29/X-84; REF1 F-04; UNKNOWN in V1 §8 — recorded, not filled in"),
 ("`Observation` (planner-facing)", "R-PLANNER-01/07", 16, "N-22 separates it from differential Observation (R-REF-05) — distinct terms, X-06"),
 ("reference-model values (`RefValue` family)", "15C declarations (source L35471+); contract R-REF-03", 17, "independent declarations U-33 (open)"),
 ("`RefCapId` / `RefActorId` / `RefEffectId`", "15C.4 (L35471–35473; restated §10 L39664–39666); contract R-SCOPE-04/R-REF-02", 17, "distinct identities, no conversion inside reference semantics (harness-boundary mapping 15C.21); duplicated authoritative declaration recorded as F-08"),
]

# --------------------------------------------------------------------------
# Evidence model (final/01 §28 body between the R-CLAIM rows).
# --------------------------------------------------------------------------

STATUS_BLOCK = """\
**FINAL1 compilation status.**

```
RED-ON-RUST
ARCHITECTURE FROZEN
IMPLEMENTATION READY
```

`IMPLEMENTATION READY` means this specification is sufficiently canonicalized and
internally structured to guide implementation. It explicitly does **not** mean
`IMPLEMENTED`, `TESTED`, `VERIFIED`, `PROVEN`, or `PRODUCTION READY`, and no such
stronger meaning may be inferred from this document or anywhere else in the
repository. The repository remains at the source-defined `BOOTSTRAP` state
(R-SCOPE-02): no Cargo workspace, no crate, no Rust source, no executed tests, no
golden-vector runs, no mutation runs, no crash-harness runs, no CI configuration,
no proof artifacts (spec/07 §1). The Rust code blocks inside the frozen source are
*specification artifacts* — normative as text, not implementations.

Conditions reported rather than absorbed (each carried in §29 / `final/09`, none
silently resolved by this compilation): `REF1-CONDITIONAL`; `V1-CONDITIONAL`;
machine-state canonical encodings (U-02); the determinism theorem's undefined
terms (U-35); the open fault-surface work (U-08/U-14); the remaining
{{N_OPEN}} open architectural-decision rows as computed in `final/09`.
"""

EVIDENCE_MODEL_PROSE = """\
**Canonicalization governance chain.** `Red-on-Rust.md` (frozen source, 42,312
lines, turns [1]–[60]) → cleaned authorities (`spec/` document set incl. the 25
frozen post-audit addenda I–V and addenda VI–IX owner decisions) → **this FINAL1
canonical compilation** (a mechanical, ID-preserving reorganization; it adds no
semantics). Where any rendering and the frozen source differ, the source's latest
frozen text governs (spec/01 rule, restated by R-SCOPE-02/03); `final/_build.py`
byte-verifies that every requirement row rendered here is identical (whitespace-
normalized) to its `spec/01` home, so the chain cannot drift silently.

**Artifact classes (distinction preserved at full strength).** `SPECIFICATION ≠
IMPLEMENTATION ≠ TEST ≠ VERIFICATION ≠ PROOF` (non-conflation laws N-06, N-07,
N-08; term/00 §4 bridges). Consequences for this document: (1) no specification-
only artifact (this file, `spec/01`, `req/`, `mod/`, the source code blocks) is
described as an implementation; (2) `python3 check.py` PASS is a *repository
integrity* result — structural presence/ordering/regex/ledger gates — and is
never represented as semantic verification or proof of any `R-…` obligation;
(3) no absent test is described as executed; every verification tag/mutant/
conformance row shows repository evidence `NONE`; (4) no conditional audit verdict
is rendered as PASS (see below).

**Promotion ledger (nothing was upgraded by this compilation).** SPECIFIED→
IMPLEMENTED, IMPLEMENTED→TESTED, TESTED→VERIFIED, VERIFIED→PROVEN: each requires
explicit repository-evidence per `spec/00` §2; none exists; none was granted. The
`audit/` verdicts are carried at their exact conditional wording.
"""

ARTIFACT_CLASS_ROWS = [
 ("SPECIFICATION", "this document; `spec/01`; `spec/03`; `req/` registry; frozen source normative text and code sketches",
  "normative as specification text; not implementation evidence"),
 ("IMPLEMENTATION", "none in repository", "every obligation SPECIFIED and no higher"),
 ("TEST", "none executed; test *contracts* only (R-TEST-*, vectors, mutation registry M001–M042 defined-not-run)",
  "no absent test may be described as executed"),
 ("VERIFICATION", "structural gates only: `check.py` 13 checkers PASS (repository integrity); audit gates (conservation/crash-consistency/reference-independence/checker-mutations)",
  "a passing repository checker MUST NOT be represented as proof unless that checker is explicitly and sufficiently defined as the proof method — none is; the gates check presence/structure, not machine semantics"),
 ("PROOF", "none; source proof sketches exist for R-CAP-08 theorems", "PROVEN is explicitly NOT claimed (R-CAP-08; R-CLAIM-01: tests are never proof of the entire calculus)"),
]

CONDITIONAL_ROWS = [
 dict(name="REF1-CONDITIONAL",
      quote="`REF1-CONDITIONAL`. … Not REF1-PASS: multiple required independence properties are UNVERIFIED (observation-equivalence, recovery-equivalence, no-production-semantics-via-`ror-core`, crate-edge enforcement) and several findings (F-01…F-05, F-09, F-11) remain open. … Not REF1-FAIL: no finding is a confirmed BLOCKING coupling … Not REF1-INDETERMINATE: the repository does contain sufficient evidence to determine what the potentially blocking coupling vectors are.",
      src="`audit/reference-independence-differential-audit.md` §14",
      rule="MUST NOT be represented as REF1-PASS anywhere without new evidence satisfying F-INFL-02's conditions (independent encoder, declared comparison domain, `ror-core` clause operationalized, crate-edge obligations registered, mutation 100 %, crash harness, differential agreement). The independent reference model remains an architectural contract; FINAL1 does not manufacture a reference implementation from the specification."),
 dict(name="V1-CONDITIONAL",
      quote="**V1-CONDITIONAL** … The verification-state model is coherent, accurate, and fully preserved. … However, material non-blocking evidence gaps remain — indeed, they define the BOOTSTRAP state — including missing implementation, missing execution tests, missing independent encoder, undeclared comparison domain, missing crash harness, missing mutation execution, missing security execution, unregistered enforcement obligations, and an unresolved registry disagreement. These gaps are fully documented in findings F-INFL-01 through F-INFL-12 and in the REF1 audit (F-01…F-11; REF1-CONDITIONAL). They prevent V1-PASS … but do not cause V1-FAIL …",
      src="`audit/v1-evidence-integrity-audit.md` §10",
      rule="Carried at CONDITIONAL (no input evidence establishes a stronger status). Preserved UNKNOWN claims (V1 §8: F-01 `ror-core`-dependence semantics, F-05 snapshot/WAL/journal record identity, F-04 `Observed*` comparison domain, REF1-vs-build import question) remain UNKNOWN — recorded ambiguity, not absent evidence. F-INFL-01 (checker-gate inflation) and F-INFL-02 (REF1→PASS inflation) are BLOCKING-if-they-occur guards: this compilation asserts neither is occurring; `final/07` re-checks the REF1-PASS representation rule."),
]

# --------------------------------------------------------------------------
# final/09 curated framing blocks.
# --------------------------------------------------------------------------

OPEN_DECISIONS_PREAMBLE = """\
FINAL1 carried forward every unresolved item from the cleaned authorities and
all five audits **without adjudicating any of them**. Stable identities are
preserved exactly (`U-nn`, `C-nn`, `X-nn`, `V-nn`, `F-nn`, `F-INFL-nn`, `AMB-nn`);
nothing was merged, renumbered, re-graded, or closed by inference. Where a
decision **was** taken by the owner (frozen addenda I–IX, U-38's governance
adoption), this registry records the decision's existence and its register
state — it does not re-take it, and FINAL1 MUST NOT reopen Addenda VII–IX or
U-38 without explicit owner authorization.

Owner of every OPEN item: the specification authority empowered to issue frozen
addenda (R-SCOPE-03 STOP-and-report discipline). `U-90` is *not* a decision: it
is the mutation-harness fixture ID recorded at spec/09 process note 9 and is
listed here once, to prevent anyone mistaking it for a dangling reference.
"""

CARRY_FORWARD_GROUPS = [
 dict(input="REF1 (reference-independence / differential audit)",
      items="F-01…F-11 (all `Disposition: OWNER-DECISION / TRACK`, none resolved; severities MAJOR×5, MINOR×2 + others, none BLOCKING/FAIL); verdict `REF1-CONDITIONAL`; §12 residual uncertainties. Enforcement surfaces: crate-edge enforcement obligations unregistered (F-09/HD-5/V-02).",
      final1="carried verbatim; §17 and `final/08` bind REF1-CONDITIONAL as the only admissible rendering"),
 dict(input="V1 (evidence-integrity audit)",
      items="F-INFL-01…F-INFL-12 (dispositions PRESERVE / BLOCK-UPGRADE / OWNER-DECISION / TRACK; none is a current defect — they are inflation *guards* and material-gap records); verdict `V1-CONDITIONAL`; §8 residual UNKNOWN (4 rows).",
      final1="carried; §28 evidence model implements the guard semantics; the two contradictions V1 records *in the corpus* (F-INFL-12 registry disagreement `spec/10-index.json` vs `spec/07` §6 = dep V-05; and the spec/06 C-09 README orientation drift) remain unadjudicated"),
 dict(input="persistence cleaning (persistence-crash-consistency audit)",
      items="Verdict: contract satisfies the requested crash-consistency property **provided the frozen addenda are normative**; the single substantive residual is recovery-step granularity `AMB-27 / REQ-RECOV-021` (reconciliation inside `Recover(D)` vs after `RecoveryComplete`). Mechanical gate `audit/_crash_consistency_checker.py` guards against clause weakening.",
      final1="residual carried in §29 and `final/09` §B; the *conditional* form of the verdict is preserved (audit-of-specification, not verification of implementation)"),
 dict(input="effect cleaning (request-pipeline audit + remediation draft)",
      items="GAP-01…GAP-18; addendum VII resolved U-39…U-44 (C-103…C-107/C-109) and registered M037/M038; `audit/request-pipeline-remediation-draft.md` remains **NOT ADOPTED**; `spec-addendum7-draft.md` is the decision record for adopted content only.",
      final1="no draft was adopted by this compilation; recommendations that did not receive a frozen addendum stay recommendations (FINAL1 MUST NOT convert audit recommendations into normative requirements)"),
 dict(input="determinism cleaning (semantic-nondeterminism audit)",
      items="DET-001…DET-018; C-98…C-102 graded `open` (this pass issued **no addendum** of its own); U-35 (theorem terms undefined) and U-37 (fixed integer widths) OPEN; U-36 resolved later by addendum IX (R-CAP-11). Clean categories (zero f32/f64; zero std::env) recorded as CLEAN — negative results are audit findings too. §5.4 replay limitation preserved in GI-DET-07.",
      final1="U-35's unfalsifiability note is attached to GI-DET-01 so the theorem can never be cited as PASS-verified; the boxed formula is transcribed unmodified"),
 dict(input="budget cleaning (resource-accounting audit)",
      items="Addendum VIII froze R-BUDGET-10/11/13 (U-45 resolved; C-108 re-graded); `R-BUDGET-12` deliberately NOT frozen (folded into R-BUDGET-15/16, addendum IX); `R-BUDGET-14` **deferred** to a resource-family pass; U-03 (spawn allocation policy) stays open outside its security-direction closure (R-ACTOR-09).",
      final1="the ID gaps (no R-BUDGET-12, no R-BUDGET-14) are recorded at their source — the `spec/09` U-01 resolution line (“no R-BUDGET-12 ID is frozen”; “R-BUDGET-14 stays deferred”) — and in `final/09` §E / `final/10`; FINAL1 treats gap numbers as non-reusable without freezing new IDs for them"),
 dict(input="security auditing (authority-trust-external-effect audit)",
      items="SEC-001…SEC-023 (3 CRITICAL, 5 HIGH, 3 MEDIUM-HIGH, 9 MEDIUM, 2 LOW/MEDIUM, 1 LOW); remediated by the security post-audit frozen addenda (rows carrying the `post-audit remediation SEC-nnn` tag in `spec/01`; incl. R-CORE-11…14, R-CAP-10, R-KERN-04…06, R-MARSHAL-05/06, R-HOST-06, R-RECOV-08, R-PERSIST-07/08, R-BUDGET-09, R-ACTOR-09/10, R-PLANNER-06/07, R-TRUST-04/05, R-ARCH-05, R-DUR-06/07 …); C-77…C-97 read `resolved-by-addendum`. Residual: U-08 (fault taxonomy) and U-14 (error-variant enumeration) stay OPEN despite the security-direction closures; U-38 resolved by repository-gate adoption (option (b), 2026-09-03) — not by normative text, and the 36 allowlisted D2/D3 warnings remain adjudicated warnings, not verified-clean rows.",
      final1="every remediation is cited through its frozen addendum; the compilation does not restate audit findings as new requirements"),
 dict(input="dependency analysis (dep/ register)",
      items="V-01, V-03, V-04 (in part), V-09, V-10 RESOLVED by addenda III/VI; still open/re-scoped: V-02 (re-scoped; §13/§14 blocks now tracked but the obligation-homing question stands), V-04 (a)(c) records retained as ID-3 history, V-05 (machine-index vs spec/07 §6 disagreement — owner decision required; F-INFL-12 records it), V-06 (arrow-convention statement), V-07 (prose-vs-machine graph edges), V-08 (`ror-compiler → ror-kernel` decision), V-11 (re-scoped; module-row inference for MOD-06/08/10 stands); hidden dependencies HD-1…HD-6; documented cycles: module layer 2 non-trivial SCCs, requirement layer 63 SCCs, section layer one 16-section SCC (dep/03) — *reported for architectural review, not new defects*; `dep/05` §7 measured remediation prices for the four build-order blockers without applying any.",
      final1="§29 lists the open V-rows; cycle results are reported as the dep/ register states them — no dependency direction was changed by this compilation"),
]

STALENESS_RECORDS = [
 ("register staleness — U-05/C-19", "`spec/01` R-ARCH-05 (frozen addendum) states the isolation ladder (U-05) is RETIRED by decision and `spec/06` C-93 is re-graded `resolved-by-addendum`; the `spec/09` U-05 row and `spec/06` C-19 row, however, still read `open`. FINAL1 preserves the normative decision (retirement) AND the unre-graded rows (register staleness), records the disagreement here, and takes no re-grade action: re-grading `spec/09`/`spec/06` rows belongs to the register owners, not to the compiler."),
 ("machine-index vs prose register", "`spec/10-index.json` `ror-host.depends_on` (and the two prose-in-edge entries) vs `spec/07` §6; tracked as dep/05 V-05 and V1 F-INFL-12; unadjudicated."),
 ("stale counts in living documents", "`req/04-verification-undefined.md` header prose says “all 497 registry records” and “8 records” where `req/registry.json` currently carries **545** records and §1 lists **9** rows (VU-01…VU-09); `spec/05-terminology.md` §8 says “78 canonical terms / 31 laws / X-01…X-86 / N-01…N-31” where `term/10-index.json` carries **86 / 33 / X-01…X-87 (87 entries) / N-01…N-33**; `README.md` paraphrases the collision register as “86-entry”. FINAL1 reports these as stale prose in the inputs and does not edit them (the counts in `final/*` are computed fresh from the machine indexes)."),
 ("withdrawn claims preserved", "Two false claims made by earlier passes are preserved quoted-not-deleted per R-SCOPE-03 (spec/06 C-08 CapabilityError assertion; X-64 “`Fault::StalePlan` occurs nowhere” — false at L28373; see term/00 §6). FINAL1 restates neither as live nor as deleted."),
]

# --------------------------------------------------------------------------
# final/10 curated blocks (report body parts; counters injected by _build.py).
# --------------------------------------------------------------------------

NOT_UPGRADED = [
 ("REF1-CONDITIONAL", "→ REF1-PASS", "prohibited by the REF1 audit itself and V1 F-INFL-02; no new evidence exists"),
 ("V1-CONDITIONAL", "→ V1-PASS", "the audit lists material non-blocking gaps as precisely the reason for CONDITIONAL; nothing in the inputs closes them"),
 ("`python3 check.py` ALL PASS (13 checkers)", "→ semantic VERIFIED for any R-…", "the checkers are structural gates over registers; none is defined as a proof method (R-CLAIM-01; spec/07 §1; V1 F-INFL-01)"),
 ("`audit/_conservation_checker.py` PASS", "→ R-CORE-05/R-BUDGET-05 VERIFIED or PROVEN", "it validates the *rules and harness contract* over Op-01…Op-22, not an executing machine; the addendum text itself cites it as gate evidence for a rule shape, not as machine evidence"),
 ("persistence audit “satisfies the requested crash-consistency property”", "→ R-RECOV-* VERIFIED", "conditional on the addenda being normative and at specification level only; carried as audit verdict, statuses unchanged"),
 ("request-pipeline audit “realizable through R-DUR-01/R-CORE-06/PanicHost/R-TRUST-05”", "→ provable/VERIFIED", "the audit's own verdict line was “not provable as frozen on four counts”; addendum VII froze remediations (specification changes), not verification evidence"),
 ("README “Implementation: IN PROGRESS / READY”", "→ IMPLEMENTED", "orientation, not repository evidence (C-09; spec/07 §1); every obligation remains SPECIFIED"),
 ("frozen addenda “resolves C-xx / closes U-xx in the security direction”", "→ register rows silently re-graded wholesale", "only the rows the addenda explicitly re-graded read `resolved-by-addendum`; the directional closures (U-03/U-06/U-08/U-14/U-22) stay OPEN in their own rows; U-05/C-19 staleness preserved"),
 ("golden vectors, `spec/08` conformance tables, mutation registry M001–M042, `ROR-001…016` sprint tasks, `crates/ror-*` layout", "→ existence of any code/test artifact", "all are normative *fixtures/contracts* inside the specification; the repository contains none of them (spec/07 §1)"),
 ("R-CAP-08 theorems' proof sketches", "→ PROVEN", "R-CAP-08's own text states PROVEN is NOT claimed; no mechanized proof exists"),
]

MERGED_DUPLICATES = [
 "S-15 split across §09 (Actors) and §10 (Scheduler) instead of repeating actor text in a scheduler section; the mod/18 duplication register (D-01…D-12) is honored: every central restatement has exactly one canonical home and every other section references it by ID.",
 "The two governing invariants carried 'into every section' by spec/00 §4 are stated once (their R-CORE homes) and referenced from §23/§24 via GI IDs; no section restates the boxed formulas.",
 "Section intros, alias tables and registry tables were generated from the registers; no type definition is restated in a second section (`final/02` §4 Type Definition Homes is an index of homes, not a definition).",
 "The '15 Core Invariants' table with 10 rows (C-20) is not re-rendered: the GI registry is the consolidation and its rows are ID-linked, so the numbering artifact never propagates.",
 "R-TEST-01's three execution modes are defined once (§20); §21/§22 reference them; §19–§22 hold exactly their own obligations (R-TEST-02/03, R-TEST-04…06).",
]

NORMALIZATIONS = [
 "Modal vocabulary: MUST / MUST NOT / SHOULD / SHOULD NOT / MAY / INFORMATIVE as already normalized by spec/01 (examples stay marked Non-normative; golden vectors stay 'normative fixtures, not behavioral rules').",
 "Terminology adopted from term/ unchanged (T-01…T-86 canonical names; forbidden variants avoided in all compilation-authored prose); no rename of any frozen API/type/symbol/field anywhere in FINAL1 output.",
 "Cross-reference style unified in compilation-authored text to full IDs (`R-`, `C-`, `U-`, `X-`, `N-`, `T-`, `V-`, `GI-`, `FA-`, `M0NN`, tags); transcribed rows keep their original wording verbatim (their `S-nn`/bare-file references resolve through `final/02`'s alias tables).",
 "`# Part …` structural headers of spec/01 removed (structure replaced by the 29-section canonical order); zero content deleted — every chunk re-homed.",
]

RESOLVED_REFS = [
 "All 184 `R-` tokens appearing anywhere in final/ resolve to exactly one home section (computed each build).",
 "All `S-nn` references inside transcribed text resolve through the S→§ alias table in `final/02` §2 (the cleaned sections remain the normative homes of their chunks; the alias table makes that resolution mechanical).",
 "Bare register-file references in transcribed text (`06`, `08`, `09`, …) resolve to the `spec/` document set by the convention declared in `final/01` §01; prefixed forms (`spec/01`, `mod/04`, `term/02`, `dep/05`, `req/03`, `audit/…`) are verified to name existing files.",
 "Every `C-nn` cited by a requirement resolves in `spec/06`; every `U-nn` in `spec/09` (U-90 excluded — harness fixture, recorded); every `X-nn` in the term index; every `N-nn` law; every `V-nn` in `dep/05`; every mutation `M0NN` within the M001–M042 registry; every obligation tag within the union of the spec/08 frozen + post-audit tag lists.",
 "Dangling-identifier scan found: none introduced by FINAL1. `NormalizedAST`, `PlanIR`, `Form`, `GlobalEvent`, `CapabilitySummary`, `BudgetSummary`, the seven `Observed*` types and `Expr::Delegate` remain source-undeclared names — recorded as such (term/ rule 13), never given invented definitions.",
]

SUPERSESSIONS = [
 "Superseded formulations are preserved inside their defining rows (quoted-not-deleted): the authority-first `Authorized(A,E,t)` reading (R-CORE-11); the 14-gate/14-step request numbering (R-EFFECT-03); the `{id, actor, digest}` persistence shapes (R-DUR-06); the no-holder kernel `authorize` (R-KERN-04); the `CapabilityContext = ()` sketch (R-KERN-05); the v0.3 `trust_level` spawn form (R-ACTOR-09); the strictly-less staleness reading (R-PLANNER-06); the cap-bearing `EffectRequest` log shape (R-PLANNER-07); the two-variant `HostFault` (R-CORE-13); the LE revised grammar (R-CANON-13); the `pub(crate) finalize` cross-crate reading and the `pub(crate)` ExecutablePlan home (addendum VI); the 11-row trust table (R-TRUST-04); the `Prepared/Issued` 15C.42 shapes; the five `// Unix timestamp` annotations (R-CAP-11); `t + δ_t ≤ W` as a receipt premise (R-BUDGET-16); the inverted durability trait (R-TRUST-05); the `EffectIssued{…issue_cost…}` v0.3 shape noted at R-RECOV-09 lineage; `GlobalConfig` (C-42), `complete` (C-23), HashMap ReplayHost (C-22), surjectivity (C-12), BudgetOK direction (C-07) and the rest of spec/06's `superseded`/`resolved-by-later-text` history.",
 "FINAL1 resurrects none of them; `final/02` §3 lists supersession carriers by requirement for traceability (computed by scanning 'SUPERSEDED' in the transcribed rows).",
]

# --------------------------------------------------------------------------
# final/00 + final/01 framing.
# --------------------------------------------------------------------------

FINAL_PREAMBLE = """\
# Red-on-Rust — FINAL1 Canonical Specification

**Compiled:** 2026-09-03 (FINAL1 specification-compiler pass).
**Method:** canonicalization of the cleaned Red-on-Rust sections, requirements,
invariants, dependencies, terminology, security constraints, persistence rules,
effect semantics, recovery rules, reference-model constraints, and verification
obligations into ONE canonical specification in the FINAL1-mandated 29-section
order, with global invariants consolidated (`GI-*`, registry `final/05`), one
stable ID per normative requirement (registry `final/03`), and evidence states
carried at exactly their support (`final/08`).
**Rule (inherited verbatim from the cleaned authority):** where any rendering and
the frozen source differ, the source's latest frozen text governs; discrepancies
are recorded (spec/00 §1), never silently corrected. FINAL1 performed no
architectural design, adjudicated no unresolved finding, converted no audit
recommendation into a requirement, and reopened neither Addenda VII–IX nor U-38.

Every requirement row below is transcribed **verbatim** (whitespace-normalized)
from `spec/01` (the cleaned normative text); requirement IDs are never
renumbered, reused, or reinterpreted. Each row retains its cleaned-provenance
annotation (source line ranges / addendum records); provenance to the frozen
transcript is reconstructible through `spec/03`/`req/` (`source → cleaned
authority → canonical definition → requirement → verification state`).

**Reading conventions.** `R-…`, `C-…`, `U-…`, `X-…`, `N-…`, `T-…`, `V-…`,
`GI-…`, `FA-…`, `M0NN`, and obligation tags are stable IDs resolvable as
described in §01.4. References of the form `S-nn` (cleaned section) or bare
`NN` (a `spec/` file) inside transcribed rows resolve through the tables of
`final/02`; they are frozen text and were not rewritten.

"""

SEC01_NOTE = """\
### §01.0 Status, scope of this compilation, and conventions (canonicalization front matter)

This section is the compilation's own framing. The normative scope rows
(R-SCOPE-01…04) follow verbatim. Four conventions bind every section:

1. **Artifact classes.** `SPECIFICATION ≠ IMPLEMENTATION ≠ TEST ≠ VERIFICATION ≠
   PROOF` (laws N-06…N-08). This document is a specification compilation. It
   contains, and may only contain, specification text, registries, and evidence
   *accounting*. §28 states the exact status of every claim class.
2. **Status ladder.** `SPECIFIED → IMPLEMENTED → TESTED → VERIFIED → PROVEN`,
   promotion only by explicit repository evidence (defined canonically in §28;
   identical to spec/00 §2). UNKNOWN is reserved for genuinely ambiguous
   contract-level evidence (V1 §8), never for merely-missing implementation.
3. **Reference resolution.** `S-nn` → cleaned section (alias map, `final/02`
   §2); bare numeric `NN` → `spec/NN` cleaned-document set; prefixed
   `spec/NN`, `mod/NN`, `req/NN`, `dep/NN`, `term/NN`, `audit/name` → repository
   files (all verified to exist by `final/_build.py`); `crates/ror-*` and
   `tests/…`/`vectors/…` paths are *frozen design intent* (R-REPO-01) and are
   never claimed to exist in this repository (spec/07 §1).
4. **Invariants.** Global machine-wide invariants carry `GI-…` IDs (§23–§25
   index; `final/05` formal registry: canonical statement home, variables,
   domains, quantifiers, state/transition context). Invariant definitions are
   single-homed; every other mention is a reference by ID. Mathematical symbols
   have exactly one canonical meaning per `final/05` §2; source-frozen symbol
   reuse is recorded as `FA-01…FA-10` (§29) rather than silently reinterpreted.
"""
