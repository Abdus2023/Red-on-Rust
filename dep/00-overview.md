# dep/00 — Typed Dependency Graph: Method

**What this set is.** The dependency layer over the frozen specification's other three views. `spec/` splits it into 24 sections, `req/` into 545 atomic records, `mod/` into 17 semantic modules; `dep/` connects them: one typed, machine-checked dependency graph over all four layers, with the seven required edge kinds, and the structural questions answered against it — roots, leaves, strongly connected components, circular dependencies, hidden dependencies, invalid dependency directions, and requirements referenced before definition.

**What it is not.** It adds no normative text and no new obligation. Every edge cites the place the dependency is already stated (`Red-on-Rust.md` line ranges, `spec/` sections, `mod/` DEPENDENCIES prose, or `req/` record IDs). Where the sources disagree, the disagreement is reported as a finding in `dep/05`, not silently resolved.

---

## 1. Arrow convention

```
A -> B        means:  B depends on A
              A is the PROVIDER (depended upon), B the CONSUMER (dependent)
```
This is the convention of `spec/04-dependency-graph.md` (its DOT edge `S07->S08` carries the note "S-08 depends on S-07"). It is the **opposite** of `mod/_ownership.py` / `mod/18-ownership-matrix.md`, whose `MODULE_DEPS = (from, to, …)` reads *from depends on to*; `dep/_graph.py` flips `MODULE_DEPS` on import (check 2). Consequences for the vocabulary:

- **root** = a node with no incoming edge = depends on nothing (a foundation).
- **leaf** = a node with no outgoing edge = nothing depends on it (a terminal consumer).
- **topological order** = dependencies before dependents (a build order).

## 2. Edge kinds

| Kind | Meaning | Legitimate provider | Implementable (would be a Cargo edge) |
|---|---|---|---|
| `TYPE_DEPENDENCY` | The consumer names types/constructors declared by the provider. | domain-type owner (`ror-core`: MOD-01/MOD-04/MOD-10) | yes |
| `SEMANTIC_DEPENDENCY` | The consumer's meaning is fixed by the provider's normative rule; no code edge is implied (specification-layer coupling). | the module that single-homes the operative statement | no |
| `SECURITY_DEPENDENCY` | The consumer's security property is *discharged* by the provider, which must be an authoritative machine-boundary component. | authoritative boundary only (never the LLM/planner) | yes |
| `SERIALIZATION_DEPENDENCY` | The consumer's payloads/identities are encoded or decoded with the provider's canonical (15A) format. | MOD-10 SERIALIZATION (`ror-core` canonical) | yes |
| `PERSISTENCE_DEPENDENCY` | The consumer's durability, journal, snapshot or recovery behaviour is defined by the provider (15B). | MOD-11 PERSISTENCE / MOD-12 RECOVERY (`ror-persistence`) | yes |
| `VERIFICATION_DEPENDENCY` | The consumer's evidence (oracle, harness, mutation, CI, claim discipline) is defined by the provider; test-time only, never a production code edge. | MOD-14…MOD-17 (`ror-reference`, `ror-differential`, `ror-testkit`, `tests/`) | no |
| `RUNTIME_DEPENDENCY` | The consumer calls the provider during execution (a real call edge in the frozen crate DAG). | the callee component | yes |

`IMPLEMENTABLE_KINDS` = TYPE / SECURITY / SERIALIZATION / PERSISTENCE / RUNTIME. `SPECIFICATION_KINDS` = SEMANTIC / VERIFICATION. A cycle that needs a specification-kind edge to close is a *specification* cycle (a wording problem); a cycle inside the implementable subgraph is an *implementation* cycle (a code problem). `dep/03` separates the two.

## 3. Layers

| Layer | Nodes | Source of the edges | Document |
|---|---|---|---|
| L1 crate | 10 `ror-*` crates | `spec/07` §6, `Red-on-Rust.md` L39196-40762 §2-§12, L39807-39828 §14 | `dep/01` §1 |
| L2 module | 17 `MOD-NN` modules | `mod/_ownership.py` MODULE_DEPS ∪ the 17 module files' DEPENDENCIES prose ∪ `req/` record pairs | `dep/01` §2 |
| L3 requirement | 545 `REQ-…` records | `req/registry.json` DEPENDENCIES | `dep/01` §3 |
| L4 section | 24 `S-NN` sections | `spec/10-index.json` `dependency_graph` (= `spec/04` §A/DOT) | `dep/01` §4 |

An L2 edge is *visible* if it appears in the crate table or in a module file's prose, and *witnessed* if at least one `req/` record pair implies it. Edges that are only witnessed are the hidden dependencies of `dep/05` HD-1.

## 4. Kind classification

Every L2 pair is classified by the first matching rule of `dep/_edges.py` `KIND_RULES` (23 rules) or by an explicit `KIND_OVERRIDES` (4 entries); `dep/_graph.py` check 4 fails the run if a pair matches none, so no edge can acquire a kind by default. L3 kinds are inherited from the owning modules when the pair crosses a module boundary, and from the provider record's area when it does not.

| Rule | Predicate (provider `p`, consumer `c`) | Kind |
|---|---|---|
| `R1-verification-sink` | ` c == "MOD-17"` | `VERIFICATION_DEPENDENCY` |
| `R2-verification-source` | ` p == "MOD-17"` | `VERIFICATION_DEPENDENCY` |
| `R3-reference-mirror` | ` c == "MOD-14" and p in PRODUCTION_NODES` | `SEMANTIC_DEPENDENCY` |
| `R4-harness-target` | ` c in ("MOD-15", "MOD-16")` | `VERIFICATION_DEPENDENCY` |
| `R5-oracle` | ` p == "MOD-14"` | `VERIFICATION_DEPENDENCY` |
| `R6-harness-output` | ` p in ("MOD-15", "MOD-16")` | `VERIFICATION_DEPENDENCY` |
| `R7-central-invariant-restatement` | ` c == "MOD-01"` | `SEMANTIC_DEPENDENCY` |
| `R8-replay-composition` | ` {p, c} == {"MOD-09", "MOD-13"}` | `RUNTIME_DEPENDENCY` |
| `R9-canonical-format` | ` p == "MOD-10"` | `SERIALIZATION_DEPENDENCY` |
| `R10-durability` | ` p in ("MOD-11", "MOD-12")` | `PERSISTENCE_DEPENDENCY` |
| `R11-planner-prohibition` | ` c == "MOD-13" and p in ("MOD-03", "MOD-07")` | `SECURITY_DEPENDENCY` |
| `R12-constraint-semantics` | ` p == "MOD-03" and c == "MOD-02"` | `SEMANTIC_DEPENDENCY` |
| `R13-authority-kernel` | ` p == "MOD-03"` | `SECURITY_DEPENDENCY` |
| `R14-domain-types` | ` p == "MOD-01"` | `TYPE_DEPENDENCY` |
| `R15-budget-gates` | ` p == "MOD-04" and c in RUNTIME_CONSUMER` | `RUNTIME_DEPENDENCY` |
| `R15b-charging-points` | ` c == "MOD-04" and p in RUNTIME_PROVIDER` | `SEMANTIC_DEPENDENCY` |
| `R15c-durable-state-shapes` | ` p in ("MOD-06", "MOD-07") and c in ("MOD-11", "MOD-12")` | `TYPE_DEPENDENCY` |
| `R15d-journal-back-reference` | ` p == "MOD-08" and c in ("MOD-11", "MOD-12")` | `SEMANTIC_DEPENDENCY` |
| `R16-budget-algebra` | ` p == "MOD-04" or c == "MOD-04"` | `TYPE_DEPENDENCY` |
| `R17-plan-input-type` | ` p == "MOD-02" and c == "MOD-05"` | `TYPE_DEPENDENCY` |
| `R18-compiler-invocation` | ` p == "MOD-02"` | `RUNTIME_DEPENDENCY` |
| `R19b-planner-consumes-machine` | ` p in RUNTIME_PROVIDER and c == "MOD-13"` | `RUNTIME_DEPENDENCY` |
| `R19-machine-call` | ` p in RUNTIME_PROVIDER` | `RUNTIME_DEPENDENCY` |

| Override | Kind | Reason |
|---|---|---|
| `MOD-01 -> MOD-10` | `SEMANTIC_DEPENDENCY` | NOT an encoding dependency: the machine `Value` domain is not the 15A `Value` domain (C-03/C-45 -> U-09). Witnesses REQ-CALC-001 -> REQ-CANON-009, REQ-CALC-008 -> REQ-CANON-001/021. |
| `MOD-03 -> MOD-04` | `TYPE_DEPENDENCY` | the resource ceiling operand of a capability is a value of the algebra's constraint/resource domain (mod/04-budget.md DEPENDENCIES: 'MOD-03 (ceiling operand; logical time discipline)'). |
| `MOD-10 -> MOD-01` | `TYPE_DEPENDENCY` | 15A encodes the `ror-core` data domain, so MOD-10 consumes MOD-01's types (R-CANON-04/05). The two `Value` domains collide here (C-03/C-45 -> U-09). |
| `MOD-13 -> MOD-01` | `SECURITY_DEPENDENCY` | R-TRUST-01/R-CORE-01 as recorded depend on planner-boundary prohibitions (REQ-TRUST-001 -> REQ-PLANNER-003/010, SECURITY-IMPACT critical), which makes the planner module the PROVIDER of a security property. Enforcement is not in `ror-agent` (spec/07 §3) — see V-03. |

## 5. Files

| File | Content | Maintenance |
|---|---|---|
| `00-overview.md` | this document | hand-written |
| `01-graph.md` | the typed graph, all four layers (output 1) | generated |
| `02-topological-order.md` | topological orderings and levels (output 2) | generated |
| `03-cycles.md` | SCCs, cycles, and per-cycle verdicts (output 3) | generated |
| `04-cross-section-table.md` | module × kind cross-section table (output 4) | generated |
| `05-violations.md` | hidden dependencies, invalid directions, independence violations (output 5) | generated |
| `10-graph.json` | machine-readable graph + analysis. The crate, module and section layers carry full node and edge lists; the requirement layer carries `node_count`, its 927 edges, roots, leaves, non-trivial SCCs and the 50 largest forward references, but not the 545 node names | generated |
| `_edges.py` | typed edge tables, classification rules, findings | hand-written |
| `_graph.py` | generator + checker (the 10 checks in its docstring) | hand-written |

```
python3 dep/_graph.py            # check; non-zero exit on any error
python3 dep/_graph.py --write    # regenerate 01..05 + 10-graph.json
```

**Status discipline.** Unchanged from `spec/00` §2: every requirement is `SPECIFIED`. A dependency edge is a statement about the specification, not evidence that anything is implemented; this repository still contains no Cargo workspace, so no layer of this graph has been exercised by a build.

