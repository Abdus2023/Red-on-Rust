#!/usr/bin/env python3
"""Build spec/10-index.json — the machine-readable index for the Red-on-Rust canonical specification.

All data here is a faithful encoding of spec/01..09 (no new normative content).
Run: python3 spec/_build_index.py
"""
import json, collections

SRC = "Red-on-Rust.md"

def prov(*ranges):
    return {"file": SRC, "line_ranges": list(ranges)}

SPEC = "SPECIFIED"

sections = [
 ("S-01","Part I — Foundations","Scope, status, conventions",["R-SCOPE-01","R-SCOPE-02","R-SCOPE-03","R-SCOPE-04"],prov("37640-37695","41280-41320"),None),
 ("S-02","Part I — Foundations","Core thesis and central invariants",["R-CORE-01","R-CORE-02","R-CORE-03","R-CORE-04","R-CORE-05","R-CORE-06","R-CORE-07","R-CORE-08","R-CORE-09","R-CORE-10","R-CORE-11","R-CORE-12","R-CORE-13"],prov("27485-27654","41320-41770"),None),
 ("S-03","Part I — Foundations","Trust model and trusted computing base",["R-TRUST-01","R-TRUST-02","R-TRUST-03","R-TRUST-04","R-TRUST-05"],prov("27611-27624","28178-28230","37722-37748"),None),
 ("S-04","Part I — Foundations","System architecture and component boundaries",["R-ARCH-01","R-ARCH-02","R-ARCH-03","R-ARCH-04","R-ARCH-05"],prov("37750-37790","9059-9118","39036-39195"),None),
 ("S-05","Part I — Foundations","LLM / planner boundary",["R-PLANNER-01","R-PLANNER-02","R-PLANNER-03","R-PLANNER-04","R-PLANNER-05","R-PLANNER-06","R-PLANNER-07"],prov("27150-27480","27920-27931","37750-37790"),None),
 ("S-06","Part I — Foundations","Compilation boundary",["R-COMPILE-01","R-COMPILE-02","R-COMPILE-03","R-COMPILE-04","R-COMPILE-05","R-COMPILE-06"],prov("37750-37790","9059-9097","39253-39308","1722-1775"),"U-22"),
 ("S-07","Part II — Language and machine semantics","Core calculus (syntax)",["R-CALC-01","R-CALC-02","R-CALC-03","R-CALC-04","R-CALC-05","R-CALC-06","R-CALC-07","R-CALC-08"],prov("12075-12195","3368-4062","23726-23820","8653-8707"),"U-04;U-06"),
 ("S-08","Part II — Language and machine semantics","CEK machine",["R-CEK-01","R-CEK-02","R-CEK-03","R-CEK-04","R-CEK-05","R-CEK-06","R-CEK-07"],prov("16861-18084","23821-23856","37800-37862","14632-14642"),None),
 ("S-09","Part II — Language and machine semantics","Capability algebra",["R-CAP-01","R-CAP-02","R-CAP-03","R-CAP-04","R-CAP-05","R-CAP-06","R-CAP-07","R-CAP-08","R-CAP-09","R-CAP-10"],prov("6344-6671","6672-6815"),None),
 ("S-10","Part II — Language and machine semantics","Capability kernel",["R-KERN-01","R-KERN-02","R-KERN-03","R-KERN-04","R-KERN-05","R-KERN-06"],prov("6672-6729","19077-19200","9119-9135","39370-39410"),None),
 ("S-11","Part III — Resources","Budget model",["R-BUDGET-01","R-BUDGET-02","R-BUDGET-03","R-BUDGET-04","R-BUDGET-05","R-BUDGET-06","R-BUDGET-07","R-BUDGET-08","R-BUDGET-09"],prov("8653-9050","9140-9245","28203-28240"),"U-01;U-07"),
 ("S-12","Part IV — Effects","Effect model and request sequence",["R-EFFECT-01","R-EFFECT-02","R-EFFECT-03","R-EFFECT-04","R-EFFECT-05","R-EFFECT-06","R-EFFECT-07","R-EFFECT-08"],prov("37891-37922","23857-24002","25799-25825"),"C-01"),
 ("S-13","Part IV — Effects","Transactional issuance and durability boundary",["R-DUR-01","R-DUR-02","R-DUR-03","R-DUR-04","R-DUR-05"],prov("35078-35258","37908-37981"),None),
 ("S-14","Part IV — Effects","Host boundary and replay",["R-HOST-01","R-HOST-02","R-HOST-03","R-HOST-04","R-HOST-05","R-HOST-06"],prov("25972-25996","37985-38000","24003-24030"),"U-06"),
 ("S-15","Part V — Concurrency","Actors and deterministic scheduling",["R-ACTOR-01","R-ACTOR-02","R-ACTOR-03","R-ACTOR-04","R-ACTOR-05","R-ACTOR-06","R-ACTOR-07","R-ACTOR-08","R-ACTOR-09","R-ACTOR-10"],prov("25457-26108","24069-25428"),"U-03;U-05"),
 ("S-16","Part V — Concurrency","Marshalling and delegation",["R-MARSHAL-01","R-MARSHAL-02","R-MARSHAL-03","R-MARSHAL-04","R-MARSHAL-05","R-MARSHAL-06"],prov("25674-26001","37946-37959","8695-8698"),"U-09"),
 ("S-17","Part VI — Persistence","Canonical serialization (15A frozen wire format)",["R-CANON-01","R-CANON-02","R-CANON-03","R-CANON-04","R-CANON-05","R-CANON-06","R-CANON-07","R-CANON-08","R-CANON-09","R-CANON-10","R-CANON-11","R-CANON-12","R-CANON-13"],prov("32936-33707","29451-31298","34987-35024"),"C-02"),
 ("S-18","Part VI — Persistence","Persistence protocol (15B)",["R-PERSIST-01","R-PERSIST-02","R-PERSIST-03","R-PERSIST-04","R-PERSIST-05","R-PERSIST-06","R-PERSIST-07","R-PERSIST-08"],prov("35078-35258","33757-34916"),"U-02;U-16"),
 ("S-19","Part VI — Persistence","Crash recovery",["R-RECOV-01","R-RECOV-02","R-RECOV-03","R-RECOV-04","R-RECOV-05","R-RECOV-06","R-RECOV-07","R-RECOV-08"],prov("35159-35258","26109-27484"),"U-15;U-17"),
 ("S-20","Part VII — Verification","Independent reference model and differential verification",["R-REF-01","R-REF-02","R-REF-03","R-REF-04","R-REF-05","R-REF-06"],prov("35272-37168","37985-38560","28590-28717"),None),
 ("S-21","Part VII — Verification","Test infrastructure, mutation, CI",["R-TEST-01","R-TEST-02","R-TEST-03","R-TEST-04","R-TEST-05","R-TEST-06","R-TEST-07","R-TEST-08","R-TEST-09","R-TEST-10","R-TEST-11"],prov("38587-38970","37169-37338","37339-37459"),None),
 ("S-22","Part VIII — Engineering and claims","Repository structure and crate responsibilities",["R-REPO-01","R-REPO-02","R-REPO-03"],prov("39036-41273"),None),
 ("S-23","Part VIII — Engineering and claims","Milestones and implementation order",["R-ORDER-01","R-ORDER-02","R-ORDER-03","R-ORDER-04","R-ORDER-05"],prov("40763-41273","37793-37812","42108-42266"),None),
 ("S-24","Part VIII — Engineering and claims","Conformance claims and prohibited shortcuts",["R-CLAIM-01","R-CLAIM-02","R-CLAIM-03","R-CLAIM-04"],prov("37416-37459","38858-38970","42030-42090"),None),
]

# (id, section, title, provenance, status, deps, impl_crates, verify_tags, related_findings)
requirements = [
 ("R-SCOPE-01","S-01","Thesis: deterministic, capability-scoped, resource-bounded, crash-recoverable execution machine","41293-41300",SPEC,[],[],[],[]),
 ("R-SCOPE-02","S-01","Architecture/specification/reference/verification contracts FROZEN; frozen != verified","38929-38942;41297-41315",SPEC,[],[],[],["C-09"]),
 ("R-SCOPE-03","S-01","STOP-and-report on ambiguity; no silent semantic modification","37664-37686",SPEC,[],["all"],["R-TEST-09"],[]),
 ("R-SCOPE-04","S-01","Zero shared core logic between production and reference","37696-37721",SPEC,[],["ror-reference","ror-differential"],["R-REF-02","dependency-graph review"],[]),
 ("R-CORE-01","S-02","LLMOutput AND UntrustedInput does not imply ExternalEffect","41320-41335;27505-27513",SPEC,[],["all"],["R-PLANNER-05","M004","M005","M006","M007","M008"],[]),
 ("R-CORE-02","S-02","External-effect chain (7 conjuncts)","41337-41351;27491-27509",SPEC,[],["all"],["R-TEST-07"],[]),
 ("R-CORE-03","S-02","NOT Authorized implies NOT ExternalEffect","42056-42064;7413-7419",SPEC,[],["ror-kernel","ror-runtime"],["M004","M005"],[]),
 ("R-CORE-04","S-02","derive(A,C) <= A (no authority amplification)","42066-42072;6399-6406",SPEC,[],["ror-kernel"],["CAP-DERIVE-NO-AMPLIFICATION","M006"],[]),
 ("R-CORE-05","S-02","Budget partition conservation (no teleportation)","42074-42080;28203-28240",SPEC,[],["ror-core","ror-runtime"],["BUDGET-CONSUMPTION-CONSERVATION","BUDGET-ESCROW-CONSERVATION","M007","M009"],["U-01"]),
 ("R-CORE-06","S-02","HostInvoked implies DurableIssued","42082-42088;35150-35156",SPEC,[],["ror-runtime","ror-persistence","ror-host"],["EFFECT-ISSUE-DURABLE-BEFORE-HOST"],[]),
 ("R-CORE-07","S-02","Ordinary marshalling rejects raw capabilities","42090-42098;25972-26001",SPEC,[],["ror-runtime"],["MARSHAL-NO-RAW-CAPABILITY"],["U-09"]),
 ("R-CORE-08","S-02","Determinism: initial state + scheduler trace + host trace implies unique machine trace","41623-41646;27518-27547",SPEC,[],["ror-runtime"],["SCHED-FIFO","R-REF-05"],["U-07"]),
 ("R-CORE-09","S-02","Causal crash recovery (qualified theorem); never infer NotExecuted","27551-27569;35159-35176",SPEC,[],["ror-persistence"],["RECOVERY-ISSUED-INDETERMINATE"],["U-15"]),
 ("R-CORE-10","S-02","No silent recovery corruption","42100-42105;35196-35208",SPEC,[],["ror-persistence"],["M015","M016","negative recovery tests"],[]),
 ("R-CORE-11","S-02","I2 predicate signatures, canonical form (frozen addendum)","addendum",SPEC,[],["ror-kernel","ror-runtime"],["R-TEST-09","R-KERN-04"],["C-80"]),
 ("R-CORE-12","S-02","Fault totality and transition atomicity on machine paths (frozen addendum)","addendum",SPEC,[],[],["M034","panic-catching fuzz harness"],["C-83"]),
 ("R-CORE-13","S-02","Closed declared fault surface (frozen addendum)","addendum",SPEC,[],[],["fault-coverage lint","differential fault matrix"],["C-91"]),
 ("R-TRUST-01","S-03","Trust table (LLM/Block No; host Partial; rest Yes)","41823-41841;27610-27624",SPEC,[],[],[],[]),
 ("R-TRUST-02","S-03","TCB composition; LLM output not in TCB authority","28178-28230",SPEC,[],[],[],[]),
 ("R-TRUST-03","S-03","No hidden authority; evaluator sees references only","37722-37748;19153-19175",SPEC,[],["ror-kernel","ror-runtime"],["Track B mock kernel","visibility checks"],[]),
 ("R-TRUST-04","S-03","One complete trust table; planner never a provider (frozen addendum)","addendum",SPEC,[],[],["dep/ SC-1/2/3 hard-gated"],["C-84"]),
 ("R-TRUST-05","S-03","Durability hinge crate edge structurally carriable (frozen addendum)","addendum",SPEC,[],["ror-runtime","ror-persistence"],["Cargo.toml DAG mechanical check"],["C-85"]),
 ("R-ARCH-01","S-04","End-to-end pipeline (LLM to host)","37750-37780;27287-27310",SPEC,[],["ror-agent","ror-compiler","ror-runtime"],[],[]),
 ("R-ARCH-02","S-04","Independent verification architecture","41406-41424",SPEC,[],["ror-differential"],["R-REF-01"],[]),
 ("R-ARCH-03","S-04","Block has no path into step(); plan constructors private","9086-9097;39296-39318",SPEC,[],["ror-compiler","ror-runtime"],["R-ORDER-03"],[]),
 ("R-ARCH-04","S-04","Dependency direction (algebra to kernel to plan to actor to global to scheduler to host)","9059-9085",SPEC,[],["all"],["Cargo dependency review"],[]),
 ("R-ARCH-05","S-04","Isolation posture decided; ladder retired (frozen addendum)","addendum",SPEC,[],["ror-host"],["dependency/visibility hard gate","dual-host-mode differential"],["C-93"]),
 ("R-PLANNER-01","S-05","PlanProposal data; LLMOutput in Data","27176-27198",SPEC,[],["ror-agent"],[],["U-13"]),
 ("R-PLANNER-02","S-05","Planner cannot allocate/authorize/modify/invoke/bypass","27271-27285;37781-37790",SPEC,[],["ror-agent"],["R-PLANNER-05(1)"],[]),
 ("R-PLANNER-03","S-05","Staleness check; StalePlan rejection without state mutation","27199-27236;28373",SPEC,[],["ror-agent","ror-runtime"],["R-PLANNER-05(2)"],["U-13"]),
 ("R-PLANNER-04","S-05","Planner need not be deterministic; PlannerAccepted recording","27392-27414",SPEC,[],["ror-agent"],["R-PLANNER-05(3)"],["U-13"]),
 ("R-PLANNER-05","S-05","LLM outer-loop conformance (3 test obligations)","27920-27931;28513-28521",SPEC,[],["ror-agent","ror-testkit"],["15E suite"],[]),
 ("R-PLANNER-06","S-05","Staleness is exact equality (frozen addendum)","addendum",SPEC,[],["ror-agent","ror-runtime"],["M026","epoch-boundary conformance"],["C-86"]),
 ("R-PLANNER-07","S-05","Observation channel capability-opaque (frozen addendum)","addendum",SPEC,[],["ror-agent"],["M027","observation-opacity property"],["C-87"]),
 ("R-COMPILE-01","S-06","Block != ExecutablePlan","41440-41452;3834-3838",SPEC,[],["ror-compiler"],["R-ORDER-03"],[]),
 ("R-COMPILE-02","S-06","Pipeline stages; any failure implies fault; no bypass","39253-39267",SPEC,[],["ror-compiler"],["malformed-Block rejection"],[]),
 ("R-COMPILE-03","S-06","Combined static judgment (type, effects, capability req, budget bound)","3874-3905",SPEC,[],["ror-compiler"],["U-22 (J2 gap)"],["U-22"]),
 ("R-COMPILE-04","S-06","Plan immutability / temporal integrity","1722-1745;2052-2070",SPEC,[],["ror-compiler"],[],[]),
 ("R-COMPILE-05","S-06","ExecutablePlan constructors private to compiler","39296-39318",SPEC,[],["ror-compiler"],["visibility review"],[]),
 ("R-COMPILE-06","S-06","Capability literals must be plan-bound (frozen addendum)","addendum",SPEC,[],["ror-compiler"],["embedded-literal battery"],["U-22"]),
 ("R-CALC-01","S-07","Machine Value domain (11 variants); Capability is opaque data","12290-12312",SPEC,[],["ror-core"],[],["C-03","U-09"]),
 ("R-CALC-02","S-07","Frozen Expr AST (12 constructors, declarative only)","12132-12170",SPEC,[],["ror-core"],[],["C-04","U-04","U-05"]),
 ("R-CALC-03","S-07","Symbol(u32) runtime identity; compiler maps names","12250-12270",SPEC,[],["ror-core","ror-compiler"],[],[]),
 ("R-CALC-04","S-07","Effect immutable data; EffectDigest=SHA-256(canonical); ID vs digest roles","9288-9348;23726-23772",SPEC,[],["ror-core"],["EFFECT-RECEIPT-DIGEST-VALIDATION"],["U-21"]),
 ("R-CALC-05","S-07","EffectCost {issue, complete_max, reserve}","25799-25825",SPEC,[],["ror-core"],["R-EFFECT-05"],[]),
 ("R-CALC-06","S-07","Frozen Fault taxonomy","23784-23819;27236",SPEC,[],["ror-core"],["fault-coverage metric"],["C-08","U-08"]),
 ("R-CALC-07","S-07","Effect replayability/reversibility/idempotence properties (table non-normative)","2141-2156;3858-3873;26669-26735",SPEC,[],["ror-core"],["U-06"],["C-05","U-06"]),
 ("R-CALC-08","S-07","Sigma and G configurations; global vs local state split","7119-7144;8653-8682;24148-24163",SPEC,[],["ror-core","ror-runtime"],[],[]),
 ("R-CEK-01","S-08","Explicit CEK; no recursive evaluation","41484-41499;37800-37812",SPEC,[],["ror-runtime"],["deep-call stress"],[]),
 ("R-CEK-02","S-08","Value-return invariant (terminal iff continuation empty)","16878-16905;37826-37838",SPEC,[],["ror-runtime","ror-reference"],["push/pop structural invariants"],[]),
 ("R-CEK-03","S-08","Frozen frame set; closure env != caller env","16927-16958;23821-23856",SPEC,[],["ror-runtime"],["CEK-CLOSURE-LEXICAL-CAPTURE"],[]),
 ("R-CEK-04","S-08","Lambda: lexical capture, pure, value-return path","16971-16995",SPEC,[],["ror-runtime"],["CEK-CLOSURE-LEXICAL-CAPTURE"],[]),
 ("R-CEK-05","S-08","Call: LTR evaluation; arity precheck before args; closure-env application","16878-16905;37840-37862",SPEC,[],["ror-runtime"],["CEK-CALL-ARITY-PRECHECK","CEK-CALL-ARGS-LTR","M001","M002","M003"],[]),
 ("R-CEK-06","S-08","Continuation preservation (+1/-1 per entry/resume)","14632-14642",SPEC,[],["ror-runtime"],["structural invariant tests"],[]),
 ("R-CEK-07","S-08","Progress and preservation","7441-7453;8850",SPEC,[],["ror-runtime"],["differential equivalence"],[]),
 ("R-CAP-01","S-09","Five semantic domains (O,S,Q,R,T) with orders and meets","6354-6379",SPEC,[],["ror-core","ror-kernel"],["algebra property tests"],[]),
 ("R-CAP-02","S-09","Operation-indexed authority","6370-6380",SPEC,[],["ror-kernel"],["cross-op contamination tests"],[]),
 ("R-CAP-03","S-09","Authority partial order","6381-6390",SPEC,[],["ror-kernel"],["monotonicity property"],[]),
 ("R-CAP-04","S-09","Constraint != Authority (narrowing request)","6391-6396;6406",SPEC,[],["ror-core","ror-kernel"],[],["U-02"]),
 ("R-CAP-05","S-09","derive = per-op meet; derive(A,C) <= A","6397-6404",SPEC,[],["ror-kernel"],["CAP-DERIVE-NO-AMPLIFICATION","M006"],[]),
 ("R-CAP-06","S-09","Canonical Authorized(A,E,t) predicate (5 conjuncts)","6406-6421;6647-6656",SPEC,[],["ror-kernel"],["Track B mock-kernel tests"],["U-21"]),
 ("R-CAP-07","S-09","Valid(c,t) incl. ancestor liveness; lazy revocation","6434-6445;6647-6656",SPEC,[],["ror-kernel"],["CAP-REVOCATION-ANCESTOR","M004"],[]),
 ("R-CAP-08","S-09","Algebra theorems 1-3 (stated; proof sketches only; NOT proven)","6422-6433;6657-6671",SPEC,[],["ror-kernel"],["property tests"],[]),
 ("R-CAP-09","S-09","Explicit logical time; no wall-clock","6434-6436;38858-38890",SPEC,[],["ror-core","ror-runtime"],["determinism tests"],["U-07"]),
 ("R-CAP-10","S-09","AdmissibleConstraint defined; fault never identity (frozen addendum)","addendum",SPEC,[],["ror-kernel","ror-compiler"],["M030","compiler negative suite"],["C-94"]),
 ("R-KERN-01","S-10","CapRef opaque, generation-safe, private fields, kernel-only construction","9127-9133;10178-10208",SPEC,[],["ror-core","ror-kernel"],["visibility review"],["C-14"]),
 ("R-KERN-02","S-10","Kernel API: authorize/derive/validate with logical time","6672-6728;19153-19175",SPEC,[],["ror-kernel"],["exactly-one-call mock tests"],[]),
 ("R-KERN-03","S-10","Authority internals inaccessible to evaluator/runtime","39397-39407",SPEC,[],["ror-kernel"],["visibility + mutation M005-class"],[]),
 ("R-KERN-04","S-10","Holder-possession binding at the gate (frozen addendum)","addendum",SPEC,[],["ror-kernel"],["M021","brute-force CapRef exhaustion from a non-holder"],["C-77"]),
 ("R-KERN-05","S-10","CapabilityContext real possession type; snapshots carry it (frozen addendum)","addendum",SPEC,[],["ror-kernel","ror-persistence"],["snapshot/recovery round-trip of possession sets"],["C-77"]),
 ("R-KERN-06","S-10","Root-grant protocol; Supervisor.host; planner-I/O separation (frozen addendum)","addendum",SPEC,[],["ror-kernel","ror-agent"],["PanicHost-wraps-all-handles conformance","grant audit test"],["C-95"]),
 ("R-BUDGET-01","S-11","Budget structure <C=<F,I,D>, R=<M,S>, W>","8683-8700;9161-9175",SPEC,[],["ror-core"],["U-01 (D semantics)"],["U-01"]),
 ("R-BUDGET-02","S-11","Checked arithmetic; no saturating_sub","9207-9245;38044-38046",SPEC,[],["ror-core"],["M007","M009"],[]),
 ("R-BUDGET-03","S-11","ReserveOK / ReleaseOK predicates","7487-7520;8692-8696",SPEC,[],["ror-core"],["reservation property tests"],["C-07"]),
 ("R-BUDGET-04","S-11","WithinBudget dual gate (runtime + capability ceiling)","8692-8696",SPEC,[],["ror-runtime","ror-kernel"],["short-circuit Track C"],[]),
 ("R-BUDGET-05","S-11","Conservation (consumables, reserved, deadline, global partition)","7408-7425;28203-28240;35210-35215",SPEC,[],["ror-core","ror-runtime"],["BUDGET-*-CONSERVATION","teleportation test"],["U-01"]),
 ("R-BUDGET-06","S-11","Time advancement delta_t (pure=0, host/scheduler>0, t+delta<=W)","8698-8700;10164-10168",SPEC,[],["ror-runtime"],["U-07"],["U-07"]),
 ("R-BUDGET-07","S-11","CostModel contract; Consumable != Reserved typing","9155-9205;10171-10177",SPEC,[],["ror-core"],[],["C-30","U-09"]),
 ("R-BUDGET-08","S-11","NOT BudgetOK implies fault(BudgetExhausted); no partial debit","7345-7352;7410-7419",SPEC,[],["ror-runtime"],["Track C budget-gate test"],[]),
 ("R-BUDGET-09","S-11","Escrow disposition totality incl. live faults (frozen addendum)","addendum",SPEC,[],["ror-runtime","ror-persistence"],["M035","ledger liveness","mixed crash+live harness"],["C-97"]),
 ("R-EFFECT-01","S-12","Request = construct-authorize-account-log-Pending-yield","12177-12194",SPEC,[],["ror-runtime"],[],[]),
 ("R-EFFECT-02","S-12","Gated transition shape Pre AND BudgetOK AND AuthOK","7145-7155;8700-8710",SPEC,[],["ror-runtime"],[],[]),
 ("R-EFFECT-03","S-12","Frozen 16-step request sequence","37891-37908",SPEC,[],["ror-runtime","ror-persistence"],["gate short-circuit matrix"],["C-01"]),
 ("R-EFFECT-04","S-12","Denial short-circuits all subsequent gates","24003-24045",SPEC,[],["ror-runtime"],["Track C (5 assertions per gate)"],[]),
 ("R-EFFECT-05","S-12","complete_max affordability at issuance","25799-25825",SPEC,[],["ror-runtime"],["budget escrow tests"],["C-23"]),
 ("R-EFFECT-06","S-12","Receipt validates ID + digest; mismatch implies ReplayCorruption, no resume","23949-24002;25952-25970",SPEC,[],["ror-runtime"],["EFFECT-RECEIPT-DIGEST-VALIDATION","M017","M018"],[]),
 ("R-EFFECT-07","S-12","Completion accounting (charge complete, release reservation, log, resume)","23949-24002",SPEC,[],["ror-runtime"],["conservation tests"],[]),
 ("R-EFFECT-08","S-12","Receipt-result admission: no authority via results (frozen addendum)","addendum",SPEC,[],["ror-runtime"],["EFFECT-RECEIPT-RESULT-NO-AUTHORITY","M019","M020"],[]),
 ("R-DUR-01","S-13","HostInvoked implies DurableIssued","35150-35156;37910",SPEC,[],["ror-runtime","ror-persistence"],["EFFECT-ISSUE-DURABLE-BEFORE-HOST"],[]),
 ("R-DUR-02","S-13","Issuance transaction order (7 steps, 2 fsyncs)","35150-35158",SPEC,[],["ror-persistence"],["crash harness T0-T4"],[]),
 ("R-DUR-03","S-13","Causal effect protocol (Issued=>Prepared; Completed=>Issued; Reconciled=>Issued; ID+digest identity)","35111-35144;37953-37965",SPEC,[],["ror-persistence"],["journal validator","M017"],["C-44"]),
 ("R-DUR-04","S-13","Prepared AND NOT Issued implies Discard; Issued AND NOT Completed implies Indeterminate (never NotExecuted)","35159-35176;37967-37981",SPEC,[],["ror-persistence"],["RECOVERY-ISSUED-INDETERMINATE","crash harness"],[]),
 ("R-DUR-05","S-13","Escrow survives crash","35210-35215",SPEC,[],["ror-persistence"],["post-recovery invariant check","M008"],[]),
 ("R-HOST-01","S-14","Host independently validates OS authority (defense in depth)","8560-8580;10168-10172",SPEC,[],["ror-host"],["host policy tests"],["C-27"]),
 ("R-HOST-02","S-14","Host performs only issued effects; partially trusted","41823-41841;27644",SPEC,[],["ror-host"],["PanicHost harness"],[]),
 ("R-HOST-03","S-14","Ordered ReplayHost; ID+digest per entry; no unordered map","25972-25996;37985-38000",SPEC,[],["ror-host","ror-reference"],["replay property tests"],["C-22"]),
 ("R-HOST-04","S-14","Replay correspondence (machine replay valid; real-world replay per effect class)","3946-3958;26249-26262",SPEC,[],["ror-host","ror-reference"],["R-REF-01 recovery equivalence"],["U-06"]),
 ("R-HOST-05","S-14","Replay validates trace, not just final state","38278-38300",SPEC,[],["ror-host"],["trace comparison"],[]),
 ("R-HOST-06","S-14","Durable receipt results, ResultDigest replay conjunct (frozen addendum)","addendum",SPEC,[],["ror-persistence","ror-runtime"],["M029","T5 byte-exact resumption"],["C-90"]),
 ("R-ACTOR-01","S-15","Actor isolation (heaps, envs, continuations, mailboxes, budgets, caps)","41623-41641;24268-24290",SPEC,[],["ror-runtime"],["Track D","isolation properties"],[]),
 ("R-ACTOR-02","S-15","GlobalState shape; logical time global","24148-24163;25514-25546",SPEC,[],["ror-runtime"],[],["C-42"]),
 ("R-ACTOR-03","S-15","Deterministic ID allocation; no address/PID/UUID/wall-clock identity","24226-24245",SPEC,[],["ror-runtime"],["determinism tests"],[]),
 ("R-ACTOR-04","S-15","FIFO scheduler; at-most-once membership; 1 transition/turn; non-runnable never scheduled","25558-25615;37924-37937",SPEC,[],["ror-runtime"],["SCHED-FIFO","SCHED-BLOCKED-NOT-SCHEDULED","M011","M012","M013","starvation test"],["C-18","C-37"]),
 ("R-ACTOR-05","S-15","Spawn: escrow + derived capabilities only; no wholesale clone","25573-25615;37940-37951",SPEC,[],["ror-runtime","ror-kernel"],["Track D","amplification test"],["U-03","U-05"]),
 ("R-ACTOR-06","S-15","Send async + deterministic wakeup; Receive blocks without fuel; FIFO mailbox","25702-25749;37940-37951",SPEC,[],["ror-runtime"],["Track D","M013"],[]),
 ("R-ACTOR-07","S-15","Deterministic concurrency theorem","25759-25766",SPEC,[],["ror-runtime"],["global differential (Track D)"],[]),
 ("R-ACTOR-08","S-15","No amplification / no teleportation theorems","26048-26070",SPEC,[],["ror-runtime"],["teleportation test","amplification test"],[]),
 ("R-ACTOR-09","S-15","Spawn authority rule: no default transfer, strict attenuation (frozen addendum)","addendum",SPEC,[],["ror-runtime","ror-kernel"],["M025","spawn fan-out amplification tests"],["C-82"]),
 ("R-ACTOR-10","S-15","Mailbox resource admission; payload-proportional cost (frozen addendum)","addendum",SPEC,[],["ror-runtime"],["M033","sender-flood stress","footprint-bounded property"],["C-96"]),
 ("R-MARSHAL-01","S-16","Recursive capability rejection in ordinary marshalling","41647-41658;25674-25701;37946-37951",SPEC,[],["ror-runtime"],["MARSHAL-NO-RAW-CAPABILITY"],["U-09"]),
 ("R-MARSHAL-02","S-16","Explicit delegation only; DelegatedCapability envelope; <= parent","25972-26001;37953-37959",SPEC,[],["ror-runtime","ror-kernel"],["Track C (delegation)"],[]),
 ("R-MARSHAL-03","S-16","MarshalledValue = canonical bytes; unmarshal(marshal(v)) = v","25674-25701;26073-26079",SPEC,[],["ror-runtime"],["Track B (marshalling)"],["U-09"]),
 ("R-MARSHAL-04","S-16","Semantic marshalling rule (CapRef not in marshal(v))","8695-8698",SPEC,[],["ror-runtime"],["Track B"],[]),
 ("R-MARSHAL-05","S-16","Delegation surface constructible and revalidated (frozen addendum)","addendum",SPEC,[],["ror-runtime","ror-kernel"],["M024","delegation negative suite"],["C-79"]),
 ("R-MARSHAL-06","S-16","contains_capability frozen total predicate (frozen addendum)","addendum",SPEC,[],["ror-runtime"],["M032","closure-smuggling corpus"],["C-81"]),
 ("R-CANON-01","S-17","Serialization independent of Rust layout/serializers","28185-28228;28453-28465",SPEC,[],["ror-core"],["format review"],[]),
 ("R-CANON-02","S-17","Universal envelope (version/tag/len/payload)","30532-30543;33290-33347",SPEC,[],["ror-core"],["golden vectors"],[]),
 ("R-CANON-03","S-17","Frozen standalone type tags (0x00,0x20,0x30,0x40,0x41)","33087-33154",SPEC,[],["ror-core"],["golden vectors"],["C-02"]),
 ("R-CANON-04","S-17","Value discriminants + nested-complete-envelope rule","30544-30552;33155-33265",SPEC,[],["ror-core"],["golden vectors","round-trip"],["C-02"]),
 ("R-CANON-05","S-17","Primitive payloads (Symbol/CapRef/ActorId/EffectId)","33087-33154",SPEC,[],["ror-core"],["golden vectors"],[]),
 ("R-CANON-06","S-17","Collections: count-prefixed; maps semantically ordered; duplicate keys rejected","30566-30573;34987-35024;38164-38172",SPEC,[],["ror-core"],["M014","duplicate-key regression (ROR-011)"],["C-41"]),
 ("R-CANON-07","S-17","Strict decoder contract (5 checks; explicit discriminants; CanonicalError set)","30575-30586;32948-33049",SPEC,[],["ror-core"],["malformed-input suite (ROR-010)"],[]),
 ("R-CANON-08","S-17","Checked arithmetic; no attacker preallocation; bounded nested cursors; fallible envelope","30574-30578;32948-33265",SPEC,[],["ror-core"],["hostile-input property tests"],[]),
 ("R-CANON-09","S-17","Digest rules + when-to-compare-bytes rule","28185-28228;30588-30590",SPEC,[],["ror-core"],["digest property tests"],["C-12","C-13"]),
 ("R-CANON-10","S-17","Injectivity as structural property + scoped evidence claim","30592-30598;35068",SPEC,[],["ror-core"],["round-trip + differential"],["C-12"]),
 ("R-CANON-11","S-17","Golden vectors as normative fixtures","30599-30646;31948-32010;33266-33286",SPEC,[],["ror-core (vectors/)"],["M1 acceptance"],[]),
 ("R-CANON-12","S-17","Data decoder rejects capability payloads (frozen addendum)","addendum",SPEC,[],["ror-core"],["M022","negative golden vectors"],["C-78"]),
 ("R-CANON-13","S-17","One canonical grammar, 15A BE sole (frozen addendum)","addendum",SPEC,[],["ror-core"],["M031","bidirectional golden vectors"],["C-92"]),
 ("R-PERSIST-01","S-18","Persistence = recording, not a semantic machine; no secondary serialization","33757-33790;35078-35087",SPEC,[],["ror-persistence"],["dependency review"],[]),
 ("R-PERSIST-02","S-18","Two-level framing; WalFrame checksum; 8 rejection classes","33802-33830;35088-35110",SPEC,[],["ror-persistence"],["negative parsing tests","M016"],[]),
 ("R-PERSIST-03","S-18","Record taxonomy; EventEnvelope monotonic sequence","33860-33900;35111-35144",SPEC,[],["ror-persistence"],["sequence property"],["U-16"]),
 ("R-PERSIST-04","S-18","Snapshot content (include/exclude lists)","26293-26330",SPEC,[],["ror-persistence"],["snapshot review"],["U-02"]),
 ("R-PERSIST-05","S-18","Atomic snapshot protocol; ValidSnapshot iff commit+digest","26216-26240;35177-35188",SPEC,[],["ror-persistence"],["SNAPSHOT-COMMIT-INTEGRITY","crash harness T6"],[]),
 ("R-PERSIST-06","S-18","WAL sequence continuity; gaps rejected","35088-35110;35189-35208",SPEC,[],["ror-persistence"],["WAL-SEQUENCE-CONTINUITY","WAL-GAP-REJECT","M015"],["U-16"]),
 ("R-PERSIST-07","S-18","Durable authority lattice; revocation survives crash (frozen addendum)","addendum",SPEC,[],["ror-persistence","ror-kernel"],["RECOVERY-REVOCATION-DURABLE","M023"],[]),
 ("R-PERSIST-08","S-18","Storage integrity rewinding-resistance (frozen addendum)","addendum",SPEC,[],["ror-persistence"],["tamper-at-every-T matrix","forged-record negatives"],["C-88"]),
 ("R-RECOV-01","S-19","D = <S,L,H>; Recover = Replay","26122-26140",SPEC,[],["ror-persistence"],["recovery differential"],["C-40"]),
 ("R-RECOV-02","S-19","Normative crash matrix T0-T6","35159-35176;28467-28493",SPEC,[],["ror-persistence"],["crash harness","M10"],[]),
 ("R-RECOV-03","S-19","Recovery algorithm (12 steps)","35189-35208;26271-26300",SPEC,[],["ror-persistence"],["recovery differential (R-REF-01)"],["U-02","U-17"]),
 ("R-RECOV-04","S-19","Independent recovery implementation","35189-35195;38858-38890",SPEC,[],["ror-persistence","ror-reference"],["dependency review"],[]),
 ("R-RECOV-05","S-19","Invalid(D) implies RecoveryFault; never silently repair","35196-35208;38254-38272",SPEC,[],["ror-persistence"],["negative corruption tests"],[]),
 ("R-RECOV-06","S-19","Budget partition invariant survives crash","35210-35215",SPEC,[],["ror-persistence"],["post-recovery invariant"],["U-01"]),
 ("R-RECOV-07","S-19","Reconciliation is the only resolution path for Indeterminate","35111-35144;26249-26262",SPEC,[],["ror-persistence","ror-host"],["U-15","reconciliation tests"],["U-06","U-15"]),
 ("R-RECOV-08","S-19","Reconciliation protocol frozen (frozen addendum)","addendum",SPEC,[],["ror-agent","ror-persistence"],["M028","T2/T3/T4 admissibility table"],["C-89"]),
 ("R-REF-01","S-20","Observe_P = Observe_R (+ recovery equivalence); evidence not proof","35281-35310;38935-38953",SPEC,[],["ror-differential"],["the gate itself"],["C-34"]),
 ("R-REF-02","S-20","Independence boundary (10 forbidden production deps)","35330-35375;37696-37721",SPEC,[],["ror-reference"],["dependency graph review"],["C-33"]),
 ("R-REF-03","S-20","Reference models all 12 semantic areas; clarity over speed","41848-41866;35281-35322;35341",SPEC,[],["ror-reference"],[],[]),
 ("R-REF-04","S-20","Reference non-goals","35326-35339",SPEC,[],["ror-reference"],[],[]),
 ("R-REF-05","S-20","Normalized observations; first divergence; no final-value-only comparison","38420-38470;41869-41906",SPEC,[],["ror-differential"],["comparator review"],[]),
 ("R-REF-06","S-20","PanicHost / MockKernel boundary enforcement","27891-27902",SPEC,[],["ror-testkit"],["harness tests"],[]),
 ("R-TEST-01","S-21","Three execution modes + frozen baselines; time != semantics","38587-38715;37251-37268",SPEC,[],["tests/"],["CI"],["C-11","C-29","C-31"]),
 ("R-TEST-02","S-21","Reproducible counterexample artifact (16 fields)","38890-38920;37293-37315",SPEC,[],["ror-differential"],["artifact schema"],[]),
 ("R-TEST-03","S-21","Shrinking protocol (10 ordered priorities)","38441-38463",SPEC,[],["ror-differential"],["shrinking tests"],[]),
 ("R-TEST-04","S-21","Baseline mutation registry M001-M018; additive","38473-38492",SPEC,[],["mutations/"],["registry review"],["C-10"]),
 ("R-TEST-05","S-21","100% kill rate (non-equivalent); adjudication for equivalents","38494-38500;37390-37400",SPEC,[],[],["M9 gate"],["C-32"]),
 ("R-TEST-06","S-21","Mutation validation (verification system tested)","38515-38540",SPEC,[],["ror-testkit"],["framework tests"],[]),
 ("R-TEST-07","S-21","Semantic coverage by obligation tags; metrics != oracle","38522-38560;37402-37414",SPEC,[],["ror-differential"],["coverage report"],[]),
 ("R-TEST-08","S-21","Crash-injection matrix T0-T6","38830-38846;35216-35236",SPEC,[],["ror-testkit"],["M10 gate"],[]),
 ("R-TEST-09","S-21","Fault adjudication (4-way classification)","38848-38862;37404-37414",SPEC,[],["process"],["R-SCOPE-03"],[]),
 ("R-TEST-10","S-21","CI gates (PR / nightly / release)","38864-38890;37287-37292",SPEC,[],["CI"],["gates"],[]),
 ("R-TEST-11","S-21","Final acceptance condition (3 conjuncts)","38885-38911;41196-41210",SPEC,[],[],["M11"],["C-34"]),
 ("R-REPO-01","S-22","Workspace layout; boundaries frozen, names flexible","39140-39195",SPEC,[],["workspace"],["R-ARCH-02"],["C-21"]),
 ("R-REPO-02","S-22","Ten crate contracts (contents + prohibitions)","39196-40762",SPEC,[],["crates/"],["dependency + visibility review"],[]),
 ("R-REPO-03","S-22","Boundaries enforced structurally (deps, visibility, types, traits, tests)","41223-41273",SPEC,[],["workspace"],["mutation + differential"],[]),
 ("R-ORDER-01","S-23","20-step implementation order; tests before dependents; reference early","37793-37812;42108-42142",SPEC,[],["process"],[],[]),
 ("R-ORDER-02","S-23","M0-M11 acceptance criteria","40763-41100",SPEC,[],["process"],["milestones"],[]),
 ("R-ORDER-03","S-23","First security gate (Block not-=> ExecutablePlan; 7-form differential)","41155-41195",SPEC,[],["ror-compiler","ror-runtime"],["gate"],[]),
 ("R-ORDER-04","S-23","Sprint 1 task set ROR-001..ROR-016","41091-41112",SPEC,[],["process"],[],[]),
 ("R-ORDER-05","S-23","Definition of done (7 components)","41124-41142",SPEC,[],["process"],[],[]),
 ("R-CLAIM-01","S-24","Scoped conformance claim (frozen wording)","38913-38917;42191-42265",SPEC,[],[],[],["C-34"]),
 ("R-CLAIM-02","S-24","16 prohibited shortcuts","38858-38890;42144-42188",SPEC,[],["all"],["mutation + review"],[]),
 ("R-CLAIM-03","S-24","Engineering response format; CONFLICT reporting","38808-38846",SPEC,[],["process"],[],[]),
 ("R-CLAIM-04","S-24","Start condition (no new semantic phase; reference alongside)","38921-38928",SPEC,[],["process"],[],[]),
]

findings = [
 ("C-01","Request-sequence numbering: 15 rules / 14 gates / 14 steps / 16 steps","MAJOR","resolved-by-later-text","open:U-none","7156-7248;7331-7407;11053-11090;23857-23948;37891-37908"),
 ("C-02","Stale primitive type tags in revised 15A grammar section 1.3","MAJOR","resolved-by-later-text","U-none","30566;30599-30646;33087-33265"),
 ("C-03","Two different Value domains share one name","MAJOR","open","U-09","12290-12312;33155-33265"),
 ("C-04","await elimination and isolation-level spawn: not re-declared in frozen documents","MAJOR","open","U-04;U-05","3830-3873;2310-2342;12132-12170;2718-2751"),
 ("C-05","Effect property values outside declared domain","MAJOR","open","U-06","3890-3905"),
 ("C-06","Budget vector dimension drift across versions","MAJOR","resolved-by-later-text","U-01 (residual)","1960;6730-6736;7119-7144;41537"),
 ("C-07","BudgetOK reserved-capacity direction error","MAJOR","resolved-by-later-text","U-none","7314-7330;7487-7520;8692-8696"),
 ("C-08","Fault naming inconsistency for capability denial (nine names verified; re-graded MINOR->MAJOR by term/ X-38; original citations wrong, see X-59)","MAJOR","open","U-08","1042;937;7374;23806-23816"),
 ("C-09","README internal status contradiction (IN PROGRESS vs READY)","MINOR","info-superseded","U-none","README 22-28; 655-661"),
 ("C-10","Mutation registry presented three ways","MINOR","resolved-by-later-text","U-none","37239-37249;38472-38492;41916"),
 ("C-11","<2 minutes exhaustive-mode target","MINOR","resolved-by-later-text","U-none","37261;37381-37386;38633"),
 ("C-12","Surjectivity misnomer for injectivity","MINOR","resolved-by-later-text","U-none","28465;30592-30598"),
 ("C-13","State-digest byte-equality claim overstated","MAJOR","resolved-by-later-text","U-none","27881-27883;28229-28240"),
 ("C-14","CapRef never-serialized comment vs 15A encoding vs snapshot content","MAJOR","open","U-02","6446;33087;26178-26195"),
 ("C-15","15A frozen tag set does not cover machine-state types","MAJOR","open","U-02","33087-33265;26178-26195"),
 ("C-16","Constraint in AST but no frozen data encoding","MINOR","open","U-02","12155;26002;6391"),
 ("C-17","invoke vs request naming","MINOR","resolved-by-later-text","U-none","1930;3840;12157"),
 ("C-18","RunState vs ActorStatus double enum","MINOR","info-both-kept","U-none","25514-25546;23784-23796"),
 ("C-19","Isolation ladder (WASM/OS) dropped without retraction","MAJOR","open","U-05","1292-1313;3960"),
 ("C-20","15 Core Invariants table has 10 rows","MINOR","info","U-none","27904-27918"),
 ("C-21","Three overlapping work-item numbering systems","MINOR","info","U-none","26109+;40763-41100;37800-37812;41090-41112"),
 ("C-22","ReplayHost HashMap vs ordered form","MAJOR","resolved-by-later-text","U-none","24003-24030;25972-25996;37985-38000"),
 ("C-23","EffectCost complete -> complete_max evolution","MAJOR","resolved-by-later-text","U-none","23726-23740;25808-25825"),
 ("C-24","Spawn budget-split policy (A2) never closed","MAJOR","open","U-03","3960-3970;12161;25573"),
 ("C-25","Separate durable effect journal vs unified WAL","MINOR","resolved-by-later-text","U-none","26146-26150;35111-35144"),
 ("C-26","Snapshot includes runnable queue AND recovery reconstructs it","MINOR","open","U-17","26178-26195;35207"),
 ("C-27","Host policy gate placement","MINOR","resolved-by-later-text","U-none","11069;37890;8560-8580"),
 ("C-28","E-BudgetFault zeroing of consumables","MINOR","info","U-none","7345-7352;7430-7434"),
 ("C-29","Stress depth bound 50k+ vs 50k-100k","MINOR","info","U-none","37263;38665"),
 ("C-30","AdmissibleConstraint trait orphaned","MINOR","open","U-09","10171"),
 ("C-31","Exhaustive baseline wording variance","MINOR","info","U-none","37253;38629"),
 ("C-32","100% kill rate scope","MINOR","resolved-by-later-text","U-none","37243;38494;40946"),
 ("C-33","Reference model distinct-language suggestion vs Rust crate","MINOR","resolved-by-later-text","U-none","28499;39140+"),
 ("C-34","property tests prove the code obeys the calculus (un-corrected claim)","MAJOR","resolved-by-later-text","U-none","37331;28246-28268;37444-37452;38955"),
 ("C-35","Compilation judgment: 4 judgments vs 1 combined","MINOR","resolved-by-later-text","U-22 (gap)","1953-1981;3874-3905"),
 ("C-36","Spawn isolation/trust parameter vs budget parameter","MINOR","resolved-by-later-text","U-05","3850;12161"),
 ("C-37","Deterministic interleaving wording for scheduler","INFO","info","U-none","41832;27618;25765"),
 ("C-38","observation_sequence vs current_planning_epoch check","MINOR","open","U-13","27236;28373;27918"),
 ("C-40","Recover(D) unqualified vs qualified theorem","MAJOR","resolved-by-later-text","U-none","26133;27551-27569"),
 ("C-41","15A frozen declared before duplicate-key patch","MINOR","resolved-by-later-text","U-none","33266;34987-35024"),
 ("C-42","GlobalState vs GlobalConfig naming","MINOR","resolved-by-later-text","U-none","8653;24148;25514"),
 ("C-43","Theorems stated vs proven","MAJOR","info-status-discipline","U-none","2028-2084;3940-4062;6422-6433;7408-7453;26048-26070;27485-27607"),
 ("C-44","Effect journal causal chain wording variance","INFO","resolved-by-later-text","U-none","26155-26170;35140-35144"),
 ("C-45","Value::Map vs machine-only variants (split of C-03)","MAJOR","open","U-09","12290-12312;33155-33265"),
]

unresolved = [
 ("U-01","Operational meaning of duration consumable D","BLOCKING","S-11","R-BUDGET-01;R-CORE-05;R-BUDGET-05;R-RECOV-06"),
 ("U-02","Canonical encoding of machine (non-data) state not frozen (incl. Authority, Expr, Frame, Environment, Constraint, SchedulerState, GlobalState)","BLOCKING","S-17;S-18;S-19","R-PERSIST-04;R-RECOV-03;R-CANON-02;R-KERN-01"),
 ("U-03","Spawn budget-allocation policy (BudgetAllocationSpec validation rules)","BLOCKING","S-15","R-ACTOR-05"),
 ("U-04","await constructor: explicit retraction or retention","BLOCKING","S-07","R-CALC-02"),
 ("U-05","Isolation ladder (WASM/OS): retired or deferred?","BLOCKING","S-07;S-15","R-CALC-02;R-ACTOR-05"),
 ("U-06","Effect replayability/reversibility/idempotence semantics + link to effect classes","BLOCKING","S-07;S-14;S-19","R-CALC-07;R-HOST-04;R-RECOV-07"),
 ("U-07","Per-transition logical-time deltas","PRE-MILESTONE","S-11","R-BUDGET-06;R-CORE-08;R-CAP-09"),
 ("U-08","Fault taxonomy unification (names + variant enumeration)","PRE-MILESTONE","S-07","R-CALC-06"),
 ("U-09","Value domain collision + orphaned AdmissibleConstraint","PRE-MILESTONE","S-07;S-16;S-17","R-CALC-01;R-MARSHAL-03;R-BUDGET-07"),
 ("U-13","PlannerMetadata / ProposalDigest definitions + exact staleness predicate","PRE-MILESTONE","S-05","R-PLANNER-01;R-PLANNER-03;R-PLANNER-04"),
 ("U-14","Error-variant enumeration (fold into U-08)","PRE-MILESTONE","S-07","R-CALC-06"),
 ("U-15","ReconciliationOutcome variants + per-class admissibility","PRE-MILESTONE","S-19","R-RECOV-07"),
 ("U-16","EventSequence vs WalSequence relationship","PRE-MILESTONE","S-18","R-PERSIST-03;R-PERSIST-06"),
 ("U-17","Runnable queue: snapshot field vs recovery reconstruction authority","PRE-MILESTONE","S-18;S-19","R-PERSIST-04;R-RECOV-03"),
 ("U-21","Op / Target / Params domain definitions + canonical encoding","PRE-MILESTONE","S-07;S-09","R-CALC-04;R-CAP-01;R-CAP-06"),
 ("U-22","Static effect-set inference (J2) not present in frozen pipeline","PRE-MILESTONE","S-06","R-COMPILE-03"),
]

# ---------------------------------------------------------------------------
# Rows the terminology-normalization passes added to the registers are DERIVED
# from spec/06 and spec/09 instead of being hand-listed above, so this index
# cannot fall behind them again: it had.  spec/00-overview.md calls 10-index.json
# "the authoritative cross-index of sections, requirements, findings, unresolved
# items, and status", yet it stopped at C-45 and U-22 while the registers ran to
# C-76 and U-34 -- 31 findings and 12 decisions invisible to any machine reader.
#
# The curated tuples above are left exactly as authored: they carry hand-graded
# values a mechanical read cannot reproduce ("MAJOR (historical)" folded to
# MAJOR, C-09's "info-superseded", C-35's "U-22 (gap)").  Everything after them
# is parsed from the registers, and the completeness gate below fails the build
# if any register row is missing from the index -- so the next pass cannot
# silently reopen the gap.
# ---------------------------------------------------------------------------
import os, re

_HERE = os.path.dirname(os.path.abspath(__file__))
_S06 = os.path.join(_HERE, "06-contradictions-ambiguities.md")
_S09 = os.path.join(_HERE, "09-unresolved-decisions.md")

# C-39 is a pointer row that duplicates C-25 (spec/06's own summary line says
# so).  The index keeps one entry per finding, so it is excluded by name here
# rather than dropped silently.
INDEX_EXCLUSIONS = {"C-39": "pointer row duplicating C-25"}

_SEVERITIES = ("BLOCKING", "MAJOR", "MINOR", "INFO")


def _read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def _cells(line):
    """Split a markdown table row on UNescaped pipes only (`\|` is a literal)."""
    return [c.strip() for c in re.split(r"(?<!\\)\|", line)][1:-1]


def _flat(text):
    return re.sub(r"\s+", " ", text.replace("`", "").replace("*", "")).strip()


def _status(cell):
    low = _flat(cell).lower()
    if "open" in low:
        return "open"
    if "resolved-by-later-text" in low:
        return "resolved-by-later-text"
    if "resolved-by-addendum" in low:
        return "resolved-by-addendum"
    if "superseded" in low:
        return "info-superseded"
    if low.startswith("info"):
        return "info"
    return low or "open"


def _resolved_into(cell):
    refs = re.findall(r"\b(U-\d{2,3})\b", cell)
    if "`term/`" in cell or "term/" in cell:
        refs += ["term/" + x for x in re.findall(r"\b(X-\d{2})\b", cell)]
    return ";".join(dict.fromkeys(refs)) or "U-none"


def _line_ranges(cell):
    """Source line refs only: a cite that names another document (`spec/01` L25,
    README L22-28) is not a Red-on-Rust.md line, and provenance.file says it is."""
    cell = re.sub(r"`(?:spec|req|term|mod)(?:/[^`]*)?`\s*L?\d+(?:\s*[\u2013-]\s*\d+)?", " ", cell)
    cell = re.sub(r"`[^`]*\.md`\s*L?\d+(?:\s*[\u2013-]\s*\d+)?", " ", cell)
    cell = re.sub(r"\bREADME\b[^;)]*", " ", cell)
    out = []
    for m in re.finditer(r"L(\d+)(?:\s*[\u2013-]\s*(\d+))?", cell):
        out.append(m.group(1) + ("-" + m.group(2) if m.group(2) else ""))
    return ";".join(dict.fromkeys(out))


def _expand(text, kind):
    """Collect ids of one family, expanding `A-01\u2026A-04` style ranges."""
    if kind == "S":
        pat = r"S-(\d{2})"
    else:
        pat = r"R-([A-Z]+)-(\d{2})"
    out = []
    for m in re.finditer(r"(%s)(?:\s*[\u2026-]\s*(%s))?" % (pat, pat), text):
        first, second = m.group(1), m.group(len(m.groups()) // 2 + 1)
        out.append(first)
        if second and second != first:
            if kind == "S":
                lo, hi = int(first[2:]), int(second[2:])
                out += ["S-%02d" % n for n in range(lo + 1, hi + 1)]
            else:
                area = first.split("-")[1]
                lo, hi = int(first.split("-")[2]), int(second.split("-")[2])
                out += ["R-%s-%02d" % (area, n) for n in range(lo + 1, hi + 1)]
    return list(dict.fromkeys(out))


def derive_findings(curated):
    rows = []
    for line in _read(_S06).split("\n"):
        m = re.match(r"^\| (C-\d{2,3}) \|", line)
        if not m or m.group(1) in curated or m.group(1) in INDEX_EXCLUSIONS:
            continue
        cells = _cells(line)
        assert len(cells) == 6, "%s: expected 6 cells, got %d" % (m.group(1), len(cells))
        cid, title, sev, src, status, _desc = cells
        base = next((x for x in _SEVERITIES if x in sev.upper()), _flat(sev))
        rows.append((cid, _flat(title), base, _status(status),
                     _resolved_into(status), _line_ranges(src)))
    return rows


def derive_unresolved(curated):
    req_section = {r[0]: r[1] for r in requirements}
    rows = []
    for block in re.split(r"^### ", _read(_S09), flags=re.M)[1:]:
        head, _, body = block.partition("\n")
        m = re.match(r"(U-\d{2})\s*\u2014\s*(.+)$", head.strip())
        if not m or m.group(1) in curated:
            continue
        where = re.search(r"^- \*\*Where:\*\*(.*)$", body, re.M)
        gate = re.search(r"^- \*\*Blocking:\*\*\s*(\w+)", body, re.M)
        w = where.group(1) if where else ""
        blocking = "BLOCKING" if (gate and gate.group(1).lower().startswith("y")) else "PRE-MILESTONE"
        reqs = _expand(w, "R")
        secs = _expand(w, "S")
        if not secs:
            # a Where bullet that names requirements but no section (U-25) still
            # belongs somewhere: take the sections those requirements live in.
            secs = list(dict.fromkeys(req_section[r] for r in reqs if r in req_section))
        rows.append((m.group(1), _flat(m.group(2)), blocking, ";".join(secs), ";".join(reqs)))
    return rows


findings += derive_findings({f[0] for f in findings})
unresolved += derive_unresolved({u[0] for u in unresolved})


def assert_index_complete():
    """Every register row must be indexed, or excluded by name."""
    have_c = {f[0] for f in findings}
    have_u = {u[0] for u in unresolved}
    miss_c = [c for c in re.findall(r"^\| (C-\d{2,3}) \|", _read(_S06), re.M)
              if c not in have_c and c not in INDEX_EXCLUSIONS]
    miss_u = [u for u in re.findall(r"^### (U-\d{2,3}) ", _read(_S09), re.M) if u not in have_u]
    stale = sorted(have_c - set(re.findall(r"^\| (C-\d{2,3}) \|", _read(_S06), re.M)))
    if miss_c or miss_u or stale:
        raise SystemExit(
            "spec/10-index.json would not match the registers:\n"
            "  findings in spec/06 but not indexed : %s\n"
            "  decisions in spec/09 but not indexed: %s\n"
            "  indexed findings with no spec/06 row  : %s" % (miss_c, miss_u, stale))


assert_index_complete()

mutations = [
 ("M001","reverse argument evaluation",["R-CEK-05"]),
 ("M002","skip arity precheck",["R-CEK-05"]),
 ("M003","allow non-function application",["R-CEK-05"]),
 ("M004","accept revoked capability",["R-CAP-07","R-CORE-03"]),
 ("M005","omit capability ceiling",["R-CAP-06"]),
 ("M006","permit capability amplification",["R-CAP-05","R-CORE-04"]),
 ("M007","omit budget gate",["R-BUDGET-04","R-BUDGET-08"]),
 ("M008","release indeterminate escrow",["R-DUR-05"]),
 ("M009","permit negative resources",["R-BUDGET-02"]),
 ("M010","allocate EffectId before authorization",["R-EFFECT-03","R-EFFECT-04"]),
 ("M011","schedule blocked actor",["R-ACTOR-04"]),
 ("M012","duplicate runnable queue entry",["R-ACTOR-04"]),
 ("M013","break mailbox FIFO",["R-ACTOR-06"]),
 ("M014","accept duplicate canonical map key",["R-CANON-06"]),
 ("M015","ignore WAL sequence gap",["R-PERSIST-06"]),
 ("M016","ignore checksum mismatch",["R-PERSIST-02"]),
 ("M017","accept mismatched EffectDigest",["R-EFFECT-06","R-DUR-03"]),
 ("M018","resume after corrupted receipt",["R-EFFECT-06"]),
 ("M019","resume with Value::Capability result",["R-EFFECT-08"]),
 ("M020","resume with closure result",["R-EFFECT-08"]),
 ("M021","authorize without possession check",["R-KERN-04"]),
 ("M022","unmarshal accepts capability payload",["R-CANON-12"]),
 ("M023","recovery resurrects revoked capability",["R-PERSIST-07"]),
 ("M024","receive-side registration without kernel revalidation",["R-MARSHAL-05"]),
 ("M025","spawn clones parent context unattenuated",["R-ACTOR-09"]),
 ("M034","release failure silently ignored (unwrap to let _)",["R-CORE-12"]),
 ("M030","inadmissible constraint treated as top",["R-CAP-10"]),
 ("M033","enqueue without recipient capacity check",["R-ACTOR-10"]),
 ("M035","stranded escrow silently reclaimed without reconciliation",["R-BUDGET-09"]),
 ("M026","accept future-tagged proposal",["R-PLANNER-06"]),
 ("M027","observation includes CapRef",["R-PLANNER-07"]),
 ("M028","reconciliation resolves Indeterminate as NotExecuted without admissible outcome",["R-RECOV-08"]),
 ("M029","replay skips result-digest verification",["R-HOST-06"]),
 ("M031","component uses the superseded LE grammar",["R-CANON-13"]),
 ("M032","contains_capability skips FunctionValue.env",["R-MARSHAL-06"]),
]

tags = [
 ("CEK-CALL-ARITY-PRECHECK",["R-CEK-05"],"M3"),
 ("CEK-CALL-ARGS-LTR",["R-CEK-05"],"M3"),
 ("CEK-CLOSURE-LEXICAL-CAPTURE",["R-CEK-03","R-CEK-04"],"M3"),
 ("CAP-DERIVE-NO-AMPLIFICATION",["R-CAP-05","R-CORE-04"],"M4"),
 ("CAP-REVOCATION-ANCESTOR",["R-CAP-07"],"M4"),
 ("BUDGET-CONSUMPTION-CONSERVATION",["R-BUDGET-05","R-CORE-05"],"M5"),
 ("BUDGET-ESCROW-CONSERVATION",["R-EFFECT-05","R-DUR-05"],"M5;M10"),
 ("EFFECT-ISSUE-DURABLE-BEFORE-HOST",["R-DUR-01","R-CORE-06"],"M5;M10"),
 ("EFFECT-RECEIPT-DIGEST-VALIDATION",["R-EFFECT-06"],"M5"),
 ("SCHED-FIFO",["R-ACTOR-04"],"M6"),
 ("SCHED-BLOCKED-NOT-SCHEDULED",["R-ACTOR-04"],"M6"),
 ("MARSHAL-NO-RAW-CAPABILITY",["R-MARSHAL-01","R-CORE-07"],"M6"),
 ("MARSHAL-CAPABILITY-REJECT",["R-MARSHAL-01","R-CORE-07"],"M6 (README alias of MARSHAL-NO-RAW-CAPABILITY)"),
 ("WAL-SEQUENCE-CONTINUITY",["R-PERSIST-06"],"M7"),
 ("WAL-GAP-REJECT",["R-PERSIST-06"],"M7 (alias emphasis)"),
 ("RECOVERY-ISSUED-INDETERMINATE",["R-DUR-04","R-RECOV-02"],"M10"),
 ("SNAPSHOT-COMMIT-INTEGRITY",["R-PERSIST-05"],"M7;M10"),
 ("EFFECT-RECEIPT-RESULT-NO-AUTHORITY",["R-EFFECT-08"],"M5 (post-audit addendum)"),
 ("RECOVERY-REVOCATION-DURABLE",["R-PERSIST-07"],"M10 (post-audit addendum)"),
]

crash_matrix = [
 ("T0","before Prepared","none","effect does not exist; no budget mutation; resume normally"),
 ("T1","after Prepared","Prepared only","discard incomplete preparation; resume normally"),
 ("T2","after Issued","Prepared + Issued","Indeterminate; requires reconciliation"),
 ("T3","host invoked","Prepared + Issued","Indeterminate (host may have executed)"),
 ("T4","host completed (not durable)","Prepared + Issued","Indeterminate (completion not durable)"),
 ("T5","after Completed","Completed durable","reconstruct completed effect; resume continuation"),
 ("T6","after SnapshotCommit","snapshot + WAL","recover snapshot base; replay subsequent WAL records"),
]

milestones = [
 ("M0","Workspace",["cargo check/test/fmt/clippy pass","no semantic functionality required"],["R-REPO-01","R-ORDER-04"]),
 ("M1","Canonical serialization",["golden vectors pass","round trips pass","malformed inputs reject","duplicate keys reject","canonical bytes deterministic"],["R-CANON-01","R-CANON-02","R-CANON-03","R-CANON-04","R-CANON-05","R-CANON-06","R-CANON-07","R-CANON-08","R-CANON-09","R-CANON-10","R-CANON-11","R-CANON-12","R-CANON-13"]),
 ("M2","Pure CEK",["differential equivalence for Value Var Let Seq If"],["R-CEK-01","R-CEK-02","R-CEK-06","R-CEK-07","R-REF-01"]),
 ("M3","Lambda / Call",["CEK-CALL-ARITY-PRECHECK","CEK-CALL-ARGS-LTR","CEK-CLOSURE-LEXICAL-CAPTURE","deep-call stress"],["R-CEK-03","R-CEK-04","R-CEK-05"]),
 ("M4","Capability / Attenuation",["CAP-DERIVE-NO-AMPLIFICATION","revocation","expiration","lexical capability binding","independent reference capability algebra"],["R-CAP-01","R-CAP-02","R-CAP-03","R-CAP-04","R-CAP-05","R-CAP-06","R-CAP-07","R-CAP-08","R-CAP-09","R-KERN-01","R-KERN-02","R-KERN-03","R-KERN-04","R-KERN-05","R-KERN-06","R-CAP-10","R-MARSHAL-05"]),
 ("M5","Effects",["authorization","budget gates","deadline","host policy","EffectId","EffectDigest","durable issuance","receipt validation"],["R-EFFECT-01","R-EFFECT-02","R-EFFECT-03","R-EFFECT-04","R-EFFECT-05","R-EFFECT-06","R-EFFECT-07","R-DUR-01","R-DUR-02","R-DUR-03","R-DUR-04","R-DUR-05","R-HOST-01","R-HOST-02","R-HOST-03","R-HOST-04","R-HOST-05","R-EFFECT-08","R-CORE-11","R-CORE-12","R-HOST-06","R-CORE-13","R-BUDGET-09"]),
 ("M6","Actors",["FIFO scheduler","FIFO mailbox","spawn isolation","send/receive","delegation","blocked/wakeup semantics"],["R-ACTOR-01","R-ACTOR-02","R-ACTOR-03","R-ACTOR-04","R-ACTOR-05","R-ACTOR-06","R-ACTOR-07","R-ACTOR-08","R-MARSHAL-01","R-MARSHAL-02","R-MARSHAL-03","R-MARSHAL-04","R-MARSHAL-06","R-ACTOR-09","R-ACTOR-10","R-ARCH-05"]),
 ("M7","Persistence",["WAL","snapshot","effect journal","checksum","sequence continuity","recovery"],["R-PERSIST-01","R-PERSIST-02","R-PERSIST-03","R-PERSIST-04","R-PERSIST-05","R-PERSIST-06","R-RECOV-01","R-RECOV-03","R-RECOV-04","R-RECOV-05","R-RECOV-06","R-PERSIST-07","R-PERSIST-08"]),
 ("M8","Differential system",["generated programs","reference execution","production execution","normalized comparison","first-divergence reporting","shrinking"],["R-REF-01","R-REF-02","R-REF-03","R-REF-04","R-REF-05","R-REF-06","R-TEST-02","R-TEST-03","R-TEST-07"]),
 ("M9","Mutation gate",["MutationKillRate = 100% for all registered non-equivalent mutants"],["R-TEST-04","R-TEST-05","R-TEST-06"]),
 ("M10","Crash/recovery gate",["T0..T6 all produce the frozen expected classification"],["R-RECOV-02","R-TEST-08","R-DUR-04","R-PERSIST-07","R-RECOV-08"]),
 ("M11","Release candidate",["exhaustive","property","mutation","differential","crash","stress","determinism","serialization","security all green"],["R-TEST-10","R-TEST-11","R-CLAIM-01"]),
]

sprint = [
 ("ROR-001","Create Cargo workspace",["R-REPO-01"]),
 ("ROR-002","Pin Rust toolchain",["R-REPO-01"]),
 ("ROR-003","Create ror-core domain types",["R-CALC-01","R-CALC-02","R-CALC-03","R-CALC-04","R-BUDGET-01","R-KERN-01"]),
 ("ROR-004","Implement canonical cursor",["R-CANON-07","R-CANON-08"]),
 ("ROR-005","Implement canonical envelope",["R-CANON-02","R-CANON-08"]),
 ("ROR-006","Implement primitive canonical types",["R-CANON-05"]),
 ("ROR-007","Implement Value canonical encoding",["R-CANON-04","R-CANON-06"]),
 ("ROR-008","Implement independent Value canonical decoding",["R-CANON-07"]),
 ("ROR-009","Add canonical golden vectors",["R-CANON-11"]),
 ("ROR-010","Add malformed-input suite",["R-CANON-07"]),
 ("ROR-011","Add duplicate-map-key regression",["R-CANON-06"]),
 ("ROR-012","Create reference-model crate",["R-REF-02","R-REF-03"]),
 ("ROR-013","Create differential observation API",["R-REF-05"]),
 ("ROR-014","Implement pure reference CEK",["R-REF-03"]),
 ("ROR-015","Implement pure production CEK",["R-CEK-01","R-CEK-02"]),
 ("ROR-016","Add first production/reference differential tests",["R-REF-01"]),
]

crates = [
 ("ror-core","Lowest-level semantic domain types; std-only",["R-CALC-01","R-CALC-02","R-CALC-03","R-CALC-04","R-CALC-05","R-CALC-06","R-CALC-08","R-BUDGET-01","R-BUDGET-02","R-BUDGET-03","R-BUDGET-04","R-BUDGET-05","R-BUDGET-06","R-BUDGET-07","R-CAP-01","R-KERN-01","R-CANON-01","R-CANON-02","R-CANON-03","R-CANON-04","R-CANON-05","R-CANON-06","R-CANON-07","R-CANON-08","R-CANON-09","R-CANON-10","R-CANON-11","R-CANON-12","R-CANON-13"],[]),
 ("ror-compiler","Block -> ExecutablePlan; plan constructors private",["R-ARCH-03","R-COMPILE-01","R-COMPILE-02","R-COMPILE-03","R-COMPILE-04","R-COMPILE-05","R-COMPILE-06","R-ORDER-03"],["ror-core"]),
 ("ror-kernel","CapabilityKernel: derive/authorize/validate/revocation; authority storage",["R-CAP-02","R-CAP-03","R-CAP-04","R-CAP-05","R-CAP-06","R-CAP-07","R-CAP-08","R-CAP-09","R-KERN-01","R-KERN-02","R-KERN-03","R-KERN-04","R-KERN-05","R-KERN-06","R-CAP-10","R-PERSIST-07","R-CORE-11","R-TRUST-03"],["ror-core"]),
 ("ror-runtime","CEK machine, actors, scheduler, effects, marshalling",["R-ARCH-01","R-CORE-08","R-CEK-01","R-CEK-02","R-CEK-03","R-CEK-04","R-CEK-05","R-CEK-06","R-CEK-07","R-EFFECT-01","R-EFFECT-02","R-EFFECT-03","R-EFFECT-04","R-EFFECT-05","R-EFFECT-06","R-EFFECT-07","R-EFFECT-08","R-ACTOR-01","R-ACTOR-02","R-ACTOR-03","R-ACTOR-04","R-ACTOR-05","R-ACTOR-06","R-ACTOR-07","R-ACTOR-08","R-MARSHAL-01","R-MARSHAL-02","R-MARSHAL-03","R-MARSHAL-04","R-MARSHAL-05","R-MARSHAL-06","R-CORE-11","R-ACTOR-09","R-CORE-12","R-CORE-13","R-HOST-06","R-ACTOR-10","R-BUDGET-09","R-ARCH-05"],["ror-core","ror-kernel","ror-persistence"]),
 ("ror-persistence","WAL, snapshots, effect journal, recovery",["R-DUR-01","R-DUR-02","R-DUR-03","R-DUR-04","R-DUR-05","R-PERSIST-01","R-PERSIST-02","R-PERSIST-03","R-PERSIST-04","R-PERSIST-05","R-PERSIST-06","R-RECOV-01","R-RECOV-02","R-RECOV-03","R-RECOV-04","R-RECOV-05","R-RECOV-06","R-RECOV-07","R-KERN-05","R-PERSIST-07","R-TRUST-05","R-PERSIST-08","R-HOST-06","R-RECOV-08"],["ror-core"]),
 ("ror-host","Host execution and replay boundaries",["R-HOST-01","R-HOST-02","R-HOST-03","R-HOST-04","R-HOST-05"],["ror-core"]),
 ("ror-agent","Planner/observation/supervisor integration",["R-ARCH-01","R-PLANNER-01","R-PLANNER-02","R-PLANNER-03","R-PLANNER-04","R-PLANNER-05","R-PLANNER-06","R-PLANNER-07","R-RECOV-08","R-KERN-06"],["ror-core","ror-compiler","ror-runtime","ror-persistence"]),
 ("ror-reference","Independent executable semantic model",["R-REF-01","R-REF-02","R-REF-03","R-REF-04"],["frozen semantics only (no production core deps)"]),
 ("ror-differential","Generator, runner, comparator, shrinking",["R-REF-01","R-REF-05","R-TEST-02","R-TEST-03","R-TEST-07"],["ror-reference","ror-runtime (black box)","ror-testkit"]),
 ("ror-testkit","Test infrastructure and controlled doubles",["R-REF-06","R-TEST-06","R-TEST-08"],["ror-core"]),
]

# dependency edges (section level), from 04
section_edges = [
 ("S-01","S-02"),("S-01","S-03"),("S-01","S-04"),
 ("S-03","S-04"),("S-04","S-05"),("S-05","S-06"),("S-06","S-07"),
 ("S-07","S-08"),("S-08","S-09"),("S-09","S-10"),
 ("S-08","S-11"),("S-08","S-12"),("S-10","S-12"),("S-11","S-12"),
 ("S-12","S-13"),("S-17","S-13"),("S-13","S-14"),
 ("S-08","S-15"),("S-15","S-16"),("S-10","S-16"),
 ("S-16","S-17"),("S-17","S-18"),("S-18","S-19"),
 ("S-19","S-20"),("S-07","S-20"),("S-13","S-20"),
 ("S-20","S-21"),("S-21","S-24"),("S-20","S-24"),
 ("S-22","S-07"),("S-22","S-10"),("S-22","S-18"),
 ("S-23","S-22"),("S-21","S-23"),
]

def _prov(p):
    if p == "addendum":
        return {"file": "01-canonical-specification.md", "line_ranges": [],
                "note": "post-audit frozen addendum (SEC-001/SEC-002); no source transcription"}
    return prov(*p.split(";"))

index = {
  "meta": {
    "specification": "Red-on-Rust frozen technical specification (canonicalized)",
    "source_of_record": {"file": SRC, "lines": 42312, "turns": 60, "description": "60-turn design conversation; turns [1]-[60]; final orientation document in README.md (turn [60])"},
    "source_state": "FROZEN (architecture, specification, reference contract, verification contract)",
    "repository_state": "BOOTSTRAP - no implementation, tests, or proof artifacts present; all obligations SPECIFIED",
    "canonicalized_on": "2026-09-02",
    "status_ladder": ["SPECIFIED","IMPLEMENTED","TESTED","VERIFIED","PROVEN"],
    "evidence_rule": "A claim is promoted only with repository evidence; none exists, so all obligations are SPECIFIED.",
    "governing_invariants": [
      "LLMOutput AND UntrustedInput does not imply ExternalEffect",
      "ExternalEffect(E) implies ValidatedPlan(P) AND Authorized(E,kappa,t) AND CapabilityWithinCeiling(E) AND BudgetAvailable(E) AND DeadlineValid(E,t) AND HostPolicyOK(E) AND Issued(E)"
    ],
    "trust_model": {
      "security_boundary": "the evaluator/runtime machine (compiler boundary, capability kernel, CEK machine, scheduler, budget system, canonical serializer, WAL/recovery, effect boundary)",
      "not_a_boundary": ["the Red-like language (Block data)"],
      "llm_role": "probabilistic proposal engine; never an authority; LLMOutput in Data"
    },
    "id_schemes": {
      "S-NN": "specification section (24)",
      "R-AREA-NN": "normative requirement/obligation (173; 148 source-transcribed + 25 post-audit frozen addenda)",
      "C-NN": f"contradiction/ambiguity finding ({len(findings)} indexed; {len(findings)+len(INDEX_EXCLUSIONS)} rows in spec/06, incl. pointer C-39 which duplicates C-25)",
      "U-NN": f"unresolved item requiring explicit decision ({len(unresolved)})",
      "M-NN": "milestone M0-M11",
      "TAG": "source verification-obligation tags (19; 17 frozen-source + 2 post-audit addenda)",
      "M0NN": "baseline mutation registry (35; 18 baseline + 17 post-audit: M019–M035)",
      "ROR-NNN": "first-sprint tasks (16)"
    },
    "documents": {
      "01-canonical-specification.md": "cleaned normative text with inline requirement IDs",
      "02-section-hierarchy.md": "section index with provenance and supersession",
      "03-obligation-matrix.md": "all requirements with stable IDs, status, provenance",
      "04-dependency-graph.md": "section/object/verification dependency graphs + DOT",
      "05-terminology.md": "glossary, normalization rules, under-specified terms",
      "06-contradictions-ambiguities.md": f"findings C-01..C-{max(int(f[0][2:]) for f in findings):02d} with severity and status",
      "07-implementation-mapping.md": "obligations -> crates/modules; actual repo state; milestone crosswalk",
      "08-verification-mapping.md": "obligations -> tags/tests/evidence; claim ladder per theorem",
      "09-unresolved-decisions.md": f"items U-01..U-{max(int(u[0][2:]) for u in unresolved):02d} requiring explicit architectural decisions",
      "10-index.json": "this file (machine-readable index)"
    }
  },
  "sections": [
    {"id": s, "part": p, "title": t, "requirements": reqs, "provenance": pr, "related_unresolved": (u.split(";") if u else None)}
    for (s,p,t,reqs,pr,u) in sections
  ],
  "requirements": [
    {"id": r, "section": s, "title": t, "provenance": _prov(p), "status": st,
     "dependencies": deps, "implementation": impl, "verification": ver, "related_findings": rel}
    for (r,s,t,p,st,deps,impl,ver,rel) in requirements
  ],
  "findings": [
    {"id": c, "title": t, "severity": sev, "status": st, "resolved_into": r, "provenance": prov(*p.split(";"))}
    for (c,t,sev,st,r,p) in findings
  ],
  "unresolved": [
    {"id": u, "title": t, "blocking": b, "section": s, "affects": a.split(";")}
    for (u,t,b,s,a) in unresolved
  ],
  "mutations": [
    {"id": m, "defect": d, "kills_evidence_for": k}
    for (m,d,k) in mutations
  ],
  "verification_tags": [
    {"tag": tg, "obligations": o, "milestone": m}
    for (tg,o,m) in tags
  ],
  "crash_matrix": [
    {"id": c, "point": p, "durable_state": d, "required_recovery_result": r}
    for (c,p,d,r) in crash_matrix
  ],
  "milestones": [
    {"id": m, "name": n, "acceptance": acc, "obligations": o}
    for (m,n,acc,o) in milestones
  ],
  "first_sprint": [
    {"id": t, "task": task, "obligations": o}
    for (t,task,o) in sprint
  ],
  "crates": [
    {"name": c, "responsibility": r, "obligations": o, "depends_on": d}
    for (c,r,o,d) in crates
  ],
  "dependency_graph": {
    "section_edges": [{"from": a, "to": b} for (a,b) in section_edges],
    "object_chain": [
      "CanonicalEncoding(15A)","SemanticDomains(CapabilityAlgebra v0.2)","CapabilityKernel",
      "Effect/EffectCost","ExecutablePlan(compiler artifact)","BudgetAlgebra",
      "ActorState","GlobalState","Scheduler","EffectIssuance(durable boundary)",
      "Marshalling/Delegation","HostExecutor/ReplayHost","WAL/Snapshot/EffectJournal(15B)","Recovery(independent)"
    ],
    "verification_chain": [
      "frozen semantics","production implementation","reference implementation (independent)",
      "normalized observations","differential comparator (first divergence)",
      "exhaustive/property/crash/mutation evidence","acceptance R-TEST-11 -> M11"
    ],
    "cycles_detected": []
  },
  "claims": {
    "implemented_obligations": 0,
    "tested_obligations": 0,
    "verified_obligations": 0,
    "proven_theorems": 0,
    "conformance_claim_wording": "The independent reference model, exhaustive/property-based tests, mutation testing, and crash-injection suite provide machine-checked evidence that the implementation conforms to the frozen calculus over the tested state space.",
    "note": "Counts are zero because no implementation or evidence exists in the repository; no claim may be promoted without evidence (R-CLAIM-01, 00-overview section 2)."
  }
}

# validate referential integrity
req_ids = {r[0] for r in requirements}
sec_ids = {s[0] for s in sections}
for r,s,t,p,st,deps,impl,ver,rel in requirements:
    assert s in sec_ids, f"bad section {s} in {r}"
for (c,t,sev,st,res,p) in findings:
    pass
for (u,t,b,s,a) in unresolved:
    for part in (x for x in a.split(";") if x):
        assert part in req_ids, f"bad req {part} in {u}"
    for part in (x for x in s.split(";") if x):
        assert part in sec_ids, f"bad section {part} in {u}"
for (tg,o,m) in tags:
    for part in o:
        assert part in req_ids, f"bad req {part} in tag {tg}"
for (m,d,k) in mutations:
    for part in k:
        assert part in req_ids, f"bad req {part} in mutant {m}"
for (m,n,acc,o) in milestones:
    for part in o:
        assert part in req_ids, f"bad req {part} in milestone {m}"
for (c,r,o,d) in crates:
    for part in o:
        assert part in req_ids, f"bad req {part} in crate {c}"
# every requirement appears in exactly one section
from collections import Counter
sec_of_req = Counter(r[1] for r in requirements)
for (s,p,t,reqs,pr,u) in sections:
    for rq in reqs:
        assert rq in req_ids, f"section {s} lists unknown req {rq}"
assigned = Counter()
for (r,s,t,p,st,deps,impl,ver,rel) in requirements:
    assigned[s] += 1
for (s,p,t,reqs,pr,u) in sections:
    assert assigned[s] == len(reqs), f"section {s}: {assigned[s]} vs {len(reqs)}"

with open("spec/10-index.json","w") as f:
    json.dump(index, f, indent=2, ensure_ascii=False)
    f.write("\n")

print(f"sections={len(sections)} requirements={len(requirements)} findings={len(findings)} "
      f"unresolved={len(unresolved)} mutations={len(mutations)} tags={len(tags)} "
      f"milestones={len(milestones)} sprint={len(sprint)} crates={len(crates)} edges={len(section_edges)}")
print("wrote spec/10-index.json")
