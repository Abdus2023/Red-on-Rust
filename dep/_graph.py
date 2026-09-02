#!/usr/bin/env python3
"""Generator + consistency checker for the typed dependency graph (`dep/`).

Run from anywhere:

    python3 dep/_graph.py            # check + report (non-zero exit on error)
    python3 dep/_graph.py --write    # also regenerate dep/01..05 and dep/10-graph.json

Reads
-----
    dep/_edges.py                    typed edge tables + classification rules
    mod/_ownership.py                MODULE_DEPS / INTRA_CRATE (flipped on import)
    mod/NN-*.md                      DEPENDENCIES prose (module edges)
    req/registry.json                545 atomic records + their DEPENDENCIES
    spec/10-index.json               crate list + section edges
    spec/07-implementation-mapping.md, spec/04-dependency-graph.md,
    mod/18-ownership-matrix.md       cross-checked for consistency

Writes (--write)
    dep/00-overview.md  dep/01-graph.md  dep/02-topological-order.md
    dep/03-cycles.md  dep/04-cross-section-table.md  dep/05-violations.md
    dep/10-graph.json

Checks (always)
  0.  the node-set definitions agree with the crate roles: every module of a
      production crate is in `PRODUCTION_NODES` and none is in
      `VERIFICATION_NODES`, and vice versa (a module missing from
      `PRODUCTION_NODES` would be invisible to HD-1).
  1.  every edge endpoint exists; no self-edges; every kind is in the
      seven-kind vocabulary; every edge carries non-empty evidence.
  2.  every `mod/_ownership.py` MODULE_DEPS edge appears in the module layer
      with the direction flipped into this document set's convention.
  3.  every module edge declared in a module file's DEPENDENCIES prose appears
      in the module layer, and every module-layer edge is justified by
      MODULE_DEPS, by prose, or by at least one `req/` witness pair.
  4.  every module pair matches exactly one classification rule (or an
      explicit override) — no edge gets a kind by default.
  5.  ror-reference / MOD-14 independence: none of the ten frozen forbidden
      crate edges is present, and no MOD-14 edge has an implementable kind.
  6.  security direction: every SECURITY_DEPENDENCY provider is an
      authoritative boundary component; the planner is never a provider.
  7.  the crate graph is acyclic; every cycle of the module layer's
      implementation graph (edges a frozen crate edge can carry) and every
      mutual module pair is listed and matches a named cycle family in
      `dep/_edges.py` `CYCLE_FAMILIES`.
  8.  the generated files (when present) are up to date with the tables — all
      seven of them, `dep/00-overview.md` included; it used to be exempt, which
      let the document describing the deliverable drift from the generator.
  9.  two provenance guards: the frozen dependency-direction blocks
      (`Red-on-Rust.md` L39757-39790 §13 and L39807-39828 §14) are still cited
      nowhere in `spec/`, `req/` or `mod/` (the basis of V-02/HD-5), and
      `README.md`'s copy of the component trust table still matches the frozen
      one at L41827-41838 (the basis of §1.5/V-11). The related cross-checks
      ID-1…ID-7 (`spec/04` vs `mod/18` arrow conventions, §13 edges,
      `spec/10-index.json` vocabulary, `MODULE_DEPS` `crate` labels, trust-table
      provenance of `AUTHORITY`) are reported in `dep/05` §4.
 10.  every edge citation in the generated text points the right way: a cited
      `A -> B` that is not an edge of its layer while `B -> A` is fails the run
      (the V-06 arrow-conversion hazard, checked mechanically over ~500
      citations). Quotations of `spec/07`/`mod/18`/`spec/10-index.json` notation
      are exempt, as is the one allowlisted assertion of an absent direction.
 11.  the provider constraint that `dep/00` §2 and `dep/01` §2.x print for each
      kind actually holds for every module edge of that kind, so the rendered
      column cannot drift from the classified edges. Each constraint is a
      predicate in `dep/_edges.py` `KIND_PROVIDER_CHECK`; SEMANTIC_DEPENDENCY is
      the only kind allowed to declare itself not machine-checkable.
 12.  the two ```dot blocks in `dep/01` (§1.3 crates, §2.9 modules) parse under
      `pydot`, and their parsed node sets and edge multisets equal the graphs
      they were generated from (crate edge labels included). Optional: with no
      `pydot` importable the run reports the check as SKIPPED rather than
      passing it, and the blocks have then had only the regex validation.
 13.  every resolution option in `dep/_edges.py` `RESOLUTIONS` (the what-if
      table behind `dep/05` §7) is a well-formed mutation of the graph as
      recorded: its crate pairs exist, its kinds are in the vocabulary, its
      rekind/drop targets are real module edges, and no option adds an edge
      §14 forbids.
"""

from __future__ import annotations

import collections
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEP = ROOT / "dep"
sys.path.insert(0, str(ROOT / "mod"))
sys.path.insert(0, str(DEP))
import _edges as E  # noqa: E402
import _ownership as O  # noqa: E402

ERRORS: list[str] = []


def n_checks() -> int:
    """Number of numbered entries in this module's `Checks (always)` list.

    Counted rather than hardcoded: the rendered count in `dep/00` §5 used to say
    "10 checks" while the list actually held 11 entries, because check 0 had been
    added without a docstring line.
    """
    return len(re.findall(r"^\s*\d+\.\s", __doc__, re.M))


def err(msg: str) -> None:
    ERRORS.append(msg)


# --------------------------------------------------------------------------
# loading
# --------------------------------------------------------------------------
def load_records():
    d = json.loads((ROOT / "req/registry.json").read_text())
    return d["records"]


def req_owner(records):
    """REQ-ID -> owning module (parent-obligation propagation + overrides)."""
    owner = {}
    for r in records:
        parents = list(dict.fromkeys(re.findall(r"R-[A-Z]+-\d+", r["SOURCE"])))
        rid = r["REQ-ID"]
        if len(parents) == 1:
            owner[rid] = O.R_OWNER[parents[0]]
        elif rid in O.REQ_OVERRIDE:
            owner[rid] = O.REQ_OVERRIDE[rid]
        else:
            err(f"{rid}: {len(parents)} parent obligations and no REQ_OVERRIDE")
    return owner


REQ_DEP_RE = re.compile(r"REQ-[A-Z]+-\d{3}")
REQ_RANGE_RE = re.compile(r"(REQ-[A-Z]+)-(\d{3})\s*[…-]+\s*(?:REQ-[A-Z]+-)?(\d{3})")


def req_dependencies(rec):
    """Records the given record depends on (single ids + expanded ranges)."""
    text = rec.get("DEPENDENCIES", "")
    out = set(REQ_DEP_RE.findall(text))
    for m in REQ_RANGE_RE.finditer(text):
        for n in range(int(m.group(2)), int(m.group(3)) + 1):
            out.add(f"{m.group(1)}-{n:03d}")
    return out


def parse_prose_deps():
    """(provider, consumer) pairs declared in each module file's DEPENDENCIES."""
    pairs, bodies = set(), {}
    for mid, _dom, _t, _crate, fname in O.MODULES:
        text = (ROOT / "mod" / fname).read_text()
        sec = text.split("## DEPENDENCIES", 1)[1].split("\n## ", 1)[0]
        buf, on = [], False
        for ln in sec.splitlines():
            if ln.startswith("- "):
                on = ln.strip().startswith("- Module dependencies")
                if on:
                    buf = [ln.strip()[2:]]
                elif buf:
                    break
            elif on and ln.strip():
                buf.append(ln.strip())
        body = " ".join(buf)
        bodies[mid] = body
        if "none upward" in body or "consumes everything" in body:
            continue
        found = []
        for m in re.finditer(r"MOD-(\d\d)(?:…MOD-(\d\d))?", body):
            if m.group(2):
                found += [f"MOD-{n:02d}" for n in range(int(m.group(1)), int(m.group(2)) + 1)]
            else:
                found.append("MOD-" + m.group(1))
        for provider in dict.fromkeys(found):
            if provider != mid:
                pairs.add((provider, mid))  # mid depends on provider
    return pairs, bodies


def moduledges_flipped():
    """{(provider, consumer): (declared_kind, basis)} from MODULE_DEPS."""
    out = {}
    for dependent, dependency, kind, basis in O.MODULE_DEPS:
        out[(dependency, dependent)] = (kind, basis)
    return out


def classify(p, c):
    if (p, c) in E.KIND_OVERRIDES:
        kind, why = E.KIND_OVERRIDES[(p, c)]
        return kind, "override", why
    for name, pred, kind, why in E.KIND_RULES:
        if pred(p, c):
            return kind, name, why
    return None, None, None


# --------------------------------------------------------------------------
# graph construction
# --------------------------------------------------------------------------
class Graph:
    def __init__(self, name, nodes, edges):
        self.name = name
        self.nodes = list(nodes)
        self.edges = edges                       # list of dicts
        self.depends_on = collections.defaultdict(set)   # node -> providers
        self.dependents = collections.defaultdict(set)   # node -> consumers
        for e in edges:
            self.depends_on[e["consumer"]].add(e["provider"])
            self.dependents[e["provider"]].add(e["consumer"])

    # --- structural queries -------------------------------------------
    @property
    def roots(self):
        return [n for n in self.nodes if not self.depends_on[n]]

    @property
    def leaves(self):
        return [n for n in self.nodes if not self.dependents[n]]

    def sub(self, kinds=None, nodes=None, name=None, pairs_exclude=()):
        ns = set(nodes) if nodes is not None else set(self.nodes)
        drop = set(pairs_exclude)
        edges = [e for e in self.edges
                 if e["provider"] in ns and e["consumer"] in ns
                 and (e["provider"], e["consumer"]) not in drop
                 and (kinds is None or e["kind"] in kinds)]
        return Graph(name or self.name, [n for n in self.nodes if n in ns], edges)

    def sccs(self):
        """Tarjan over `depends_on` (iterative)."""
        index, low, onstack = {}, {}, set()
        stack, out, counter = [], [], [0]
        for root in self.nodes:
            if root in index:
                continue
            work = [(root, iter(sorted(self.depends_on[root])))]
            index[root] = low[root] = counter[0]
            counter[0] += 1
            stack.append(root)
            onstack.add(root)
            while work:
                v, it = work[-1]
                advanced = False
                for w in it:
                    if w not in index:
                        index[w] = low[w] = counter[0]
                        counter[0] += 1
                        stack.append(w)
                        onstack.add(w)
                        work.append((w, iter(sorted(self.depends_on[w]))))
                        advanced = True
                        break
                    if w in onstack:
                        low[v] = min(low[v], index[w])
                if advanced:
                    continue
                work.pop()
                if work:
                    low[work[-1][0]] = min(low[work[-1][0]], low[v])
                if low[v] == index[v]:
                    comp = []
                    while True:
                        w = stack.pop()
                        onstack.discard(w)
                        comp.append(w)
                        if w == v:
                            break
                    out.append(sorted(comp))
        return sorted(out, key=lambda c: (-len(c), c[0]))

    def toposort(self):
        """Kahn over `depends_on`; dependencies before dependents.

        Returns (order, stuck) — `stuck` are the nodes left inside cycles.
        """
        pending = {n: set(self.depends_on[n]) for n in self.nodes}
        order, ready = [], sorted(self.roots)
        while ready:
            n = ready.pop(0)
            order.append(n)
            for m in sorted(self.dependents[n]):
                pending[m].discard(n)
                if not pending[m]:
                    ready.append(m)
            ready.sort()
        return order, [n for n in self.nodes if n not in order]

    def levels(self):
        """Longest-path layering on the SCC condensation (cycle-safe).

        Returns {level: [node, ...]} where level 0 holds the nodes that depend on
        nothing (outside cycles) and each later level depends only on earlier ones.
        """
        comp_of, comps = {}, []
        for comp in self.sccs():
            comps.append(list(comp))
            for n in comp:
                comp_of[n] = len(comps) - 1
        cdeps = {i: set() for i in range(len(comps))}
        for n in self.nodes:
            for p in self.depends_on[n]:
                if comp_of[p] != comp_of[n]:
                    cdeps[comp_of[n]].add(comp_of[p])
        remaining = {i: set(d) for i, d in cdeps.items()}
        lvl = {}
        ready = sorted(i for i in remaining if not remaining[i])
        while ready:
            i = ready.pop(0)
            lvl[i] = 0 if not cdeps[i] else 1 + max(lvl[j] for j in cdeps[i])
            for j in sorted(remaining):
                if i in remaining[j]:
                    remaining[j].discard(i)
                    if not remaining[j]:
                        ready.append(j)
            ready.sort()
        out = collections.defaultdict(list)
        for i, l in lvl.items():
            out[l].extend(comps[i])
        return {l: sorted(v) for l, v in sorted(out.items())}


def build_module_graph(prose_pairs, mdeps, witnesses):
    pairs = sorted(set(witnesses) | prose_pairs | set(mdeps))
    edges = []
    for p, c in pairs:
        if p == c:
            err(f"module self-edge {p}")
            continue
        kind, rule, basis = classify(p, c)
        if kind is None:
            err(f"module edge {p} -> {c} matches no classification rule")
            continue
        if kind not in E.KINDS:
            err(f"module edge {p} -> {c}: unknown kind {kind}")
            continue
        vis = []
        if (p, c) in mdeps:
            vis.append("crate-table")
        if (p, c) in prose_pairs:
            vis.append("prose")
        if (p, c) in witnesses:
            vis.append(f"{len(witnesses[(p, c)])} req")
        extra = []
        if (p, c) in mdeps:
            extra.append(f"MODULE_DEPS kind `{mdeps[(p, c)][0]}`: {mdeps[(p, c)][1]}")
        w = witnesses.get((p, c))
        if w:
            shown = ", ".join(f"{a} -> {b}" for a, b in sorted(w)[:3])
            extra.append(f"witnesses: {shown}" + (" ..." if len(w) > 3 else ""))
        edges.append({
            "provider": p, "consumer": c, "kind": kind, "rule": rule,
            "visibility": "+".join(vis) or "none",
            "basis": basis, "evidence": " | ".join(extra) or basis,
        })
    nodes = [m[0] for m in O.MODULES]
    return Graph("module", nodes, edges)


def build_crate_graph():
    names = [n for n, _r in E.CRATE_NODES]
    edges = []
    for p, c, kind, ev in E.CRATE_EDGES:
        if p not in names or c not in names:
            err(f"crate edge {p} -> {c}: unknown crate")
        if kind not in E.KINDS:
            err(f"crate edge {p} -> {c}: unknown kind {kind}")
        edges.append({"provider": p, "consumer": c, "kind": kind,
                      "visibility": "spec/07 §6", "basis": ev, "evidence": ev})
    return Graph("crate", names, edges)


def elementary_circuits(graph, maxlen=5):
    """Distinct elementary circuits of length 2..maxlen, canonicalised by rotation.

    Used only to justify why the kind-filtered subgraph is *not* the
    implementability test: it is riddled with small circuits even though only
    one of them is a strongly connected component.
    """
    adj: dict[str, set] = {}
    for e in graph.edges:
        adj.setdefault(e["provider"], set()).add(e["consumer"])
    found = set()

    def walk(start, cur, path, seen):
        for nxt in sorted(adj.get(cur, ())):
            if nxt == start and len(path) >= 2:
                found.add(tuple(path))
            elif nxt not in seen and len(path) < maxlen:
                walk(start, nxt, path + [nxt], seen | {nxt})

    for n in sorted(graph.nodes):
        walk(n, n, [n], {n})
    return {min(t[i:] + t[:i] for i in range(len(t))) for t in found}


def crate_graph_augmented(crate_graph):
    """The crate layer plus every edge `dep/01` §1.2 says the spec forces.

    Used to answer the question an architect actually asks of a missing edge:
    can the DAG absorb it, and does the build order survive?
    """
    extra = [dict(provider=p, consumer=c, kind=k, visibility="MISSING", basis=w)
             for p, c, k, w in E.CRATE_MISSING_EDGES]
    return Graph("crate+missing", crate_graph.nodes, crate_graph.edges + extra)


def build_section_graph(index):
    nodes = [s["id"] for s in index["sections"]]
    edges = []
    for e in index["dependency_graph"]["section_edges"]:
        p, c = e["from"], e["to"]
        kind = None
        for name, pred, k, why in E.SECTION_KIND_RULES:
            if pred(p, c):
                kind, rule, basis = k, name, why
                break
        if kind is None:
            err(f"section edge {p} -> {c} matches no kind rule")
            continue
        edges.append({"provider": p, "consumer": c, "kind": kind, "rule": rule,
                      "visibility": "spec/04 §A", "basis": basis, "evidence": basis})
    return Graph("section", nodes, edges)


def build_req_graph(records, owner):
    by = {r["REQ-ID"]: r for r in records}
    nodes = sorted(by)
    edges = []
    for r in records:
        for dep in sorted(req_dependencies(r)):
            if dep not in by:
                err(f"{r['REQ-ID']}: DEPENDENCIES names unknown {dep}")
                continue
            a, b = dep, r["REQ-ID"]          # provider=dep, consumer=record
            if a == b:
                continue
            edges.append({"provider": a, "consumer": b,
                          "kind": req_kind(by, owner, a, b),
                          "visibility": "req/registry.json DEPENDENCIES",
                          "basis": "", "evidence": ""})
    return Graph("requirement", nodes, edges), by


def req_kind(by, owner, provider, consumer):
    pm, cm = owner[provider], owner[consumer]
    if pm != cm:
        kind, _rule, _why = classify(pm, cm)
        return kind or "SEMANTIC_DEPENDENCY"
    area = provider.split("-")[1]
    if area == "CANON":
        return "SERIALIZATION_DEPENDENCY"
    if area in ("PERSIST", "DUR", "RECOV"):
        return "PERSISTENCE_DEPENDENCY"
    if area in ("REF", "TEST", "CLAIM"):
        return "VERIFICATION_DEPENDENCY"
    if area in ("CAP", "KERN", "TRUST"):
        return "SECURITY_DEPENDENCY"
    if area == "CALC":
        return "TYPE_DEPENDENCY"
    if area in ("CEK", "ACTOR", "EFFECT", "HOST", "COMPILE", "PLANNER", "MARSHAL"):
        return "RUNTIME_DEPENDENCY"
    return "SEMANTIC_DEPENDENCY"


def forward_refs_req(graph, by):
    def first_line(rec):
        m = re.search(r"L(\d+)", rec["SOURCE"])
        return int(m.group(1)) if m else 0
    out = []
    for e in graph.edges:
        la, lb = first_line(by[e["consumer"]]), first_line(by[e["provider"]])
        if la and lb and la < lb:
            out.append((e["consumer"], e["provider"], la, lb))
    return sorted(out, key=lambda t: -(t[3] - t[2]))


def forward_refs_section(graph):
    return sorted(
        (e["consumer"], e["provider"]) for e in graph.edges
        if int(e["consumer"][2:]) < int(e["provider"][2:])
    )


def crate_of_module():
    out = {}
    for crate, members in O.INTRA_CRATE.items():
        for m in members:
            out[m] = crate
    for _mid, _dom, _t, crate, _f in O.MODULES:
        out.setdefault(_mid, crate.split(" (+")[0].split(" (")[0])
    # explicit homes for the modules INTRA_CRATE does not list
    out.update({
        "MOD-02": "ror-compiler", "MOD-03": "ror-kernel", "MOD-09": "ror-host",
        "MOD-13": "ror-agent", "MOD-14": "ror-reference",
        "MOD-15": "ror-differential", "MOD-16": "mutations/registry.toml",
        "MOD-17": "tests/",
    })
    return out


def crate_edge_pairs():
    """(provider_crate, consumer_crate) pairs the frozen crate list carries."""
    return {(p, c) for p, c, _k, _e in E.CRATE_EDGES}


def realisable(e, crate_of):
    """Can a frozen Cargo edge carry this module edge?

    True when both modules sit in the same crate (an intra-crate call) or when
    the frozen crate list contains provider_crate -> consumer_crate.
    """
    cp, cc = crate_of[e["provider"]], crate_of[e["consumer"]]
    return cp == cc or (cp, cc) in crate_edge_pairs()


def cycle_family(fs):
    for fid, name, pred, verdict in E.CYCLE_FAMILIES:
        if pred(fs):
            return fid, name, verdict
    return None, None, None


def mutual_pairs(graph):
    pairs = {(e["provider"], e["consumer"]): e for e in graph.edges}
    return sorted({frozenset(k) for k in pairs if (k[1], k[0]) in pairs},
                  key=lambda fs: sorted(fs))


def hidden_dependencies(mod_graph, prose_pairs, mdeps, witnesses, crate_index,
                        crate_of):
    hd = []
    # HD-1: production-to-production edges no frozen crate edge can carry
    prod = [e for e in mod_graph.edges
            if e["provider"] in E.PRODUCTION_NODES and e["consumer"] in E.PRODUCTION_NODES
            and not realisable(e, crate_of)]
    hd.append(("HD-1", "Production couplings no frozen crate edge can carry",
               f"{len(prod)} module edges between production modules have no crate "
               "realisation: the specification states the coupling, but "
               "`spec/07` §6 has no edge that could carry it. Each is either a "
               "specification-layer statement (fine) or a missing crate edge "
               "(a finding).",
               [(e["provider"], e["consumer"], e["kind"],
                 f"would need crate edge {crate_of[e['provider']]} -> "
                 f"{crate_of[e['consumer']]} (absent); {e['visibility']}")
                for e in prod]))
    # HD-2: intra-crate couplings invisible in the crate DAG
    intra = collections.defaultdict(list)
    for e in mod_graph.edges:
        if crate_of[e["provider"]] == crate_of[e["consumer"]]:
            intra[crate_of[e["provider"]]].append((e["provider"], e["consumer"]))
    hd.append(("HD-2", "Intra-crate couplings the crate DAG cannot express",
               "The crate layer collapses each of these groups to a single node, "
               "so reading only `spec/07` §6 understates the coupling — and "
               "hides the three implementation cycles of `dep/03` §2.1.",
               {k: sorted(v) for k, v in sorted(intra.items())}))
    # HD-3: crate edges required but absent
    hd.append(("HD-3", "Required crate edges absent from every crate list",
               "Forced by the frozen text or by `mod/_ownership.MODULE_DEPS`; see "
               "`dep/05` V-01, V-04 and V-10. `dep/01` §1.2 shows the crate DAG "
               "absorbs all of them without becoming cyclic.",
               E.CRATE_MISSING_EDGES))
    # HD-4: crate edges in spec/07 §6 but missing from the machine-readable index
    idx_edges = {(c["name"], d) for c in crate_index["crates"] for d in c["depends_on"]
                 if d in {n for n, _r in E.CRATE_NODES}}
    prose_edges = {(c["name"], d) for c in crate_index["crates"] for d in c["depends_on"]
                   if d not in {n for n, _r in E.CRATE_NODES}}
    doc_edges = {(c, p) for p, c, _k, _e in E.CRATE_EDGES}
    kind_of = {(e["provider"], e["consumer"]): e["kind"] for e in
               [{"provider": p, "consumer": c, "kind": k} for p, c, k, _e in E.CRATE_EDGES]}
    hd.append(("HD-4", "`spec/07` §6 edges missing from `spec/10-index.json`",
               "The generated machine-readable crate graph is not the frozen one: "
               "`spec/_build_index.py` `crates[]` was written by hand and drifted.",
               [(prov, cons, kind_of.get((prov, cons), ""),
                 "present in `spec/07` §6 and in `dep/01` §1; "
                 + (f"appears in `spec/10-index.json` `crates[{cons}].depends_on` "
                    f"only as the prose string {[d for cc, d in prose_edges if cc == cons]}"
                    if any(cc == cons for cc, _d in prose_edges) else
                    f"absent from `spec/10-index.json` `crates[{cons}].depends_on`"))
                for cons, prov in sorted(doc_edges - idx_edges)]))
    # HD-5: forbidden-edge list with no obligation behind it
    hd.append(("HD-5", "Frozen prohibitions with no tracked obligation",
               "L39807-39828 §14 + L39645-39651 §10; no `R-…`, `REQ-…` or `C-…` "
               "record cites those lines.",
               [(d, p, "FORBIDDEN", ev) for d, p, ev in E.FORBIDDEN_CRATE_EDGES]))
    # HD-6: verification edges that reach into production
    verif = [e for e in mod_graph.edges
             if (e["provider"] in E.VERIFICATION_NODES) != (e["consumer"] in E.VERIFICATION_NODES)
             and e["kind"] == "VERIFICATION_DEPENDENCY"
             and {crate_of[e["provider"]], crate_of[e["consumer"]]} &
                 {"ror-runtime", "ror-reference", "ror-differential"}]
    hd.append(("HD-6", "Verification-layer edges that would become Cargo edges",
               "Test-time couplings between the verification layer and production "
               "crates. `ror-runtime -> ror-differential` — the 'ror-runtime "
               "(black box)' entry of `spec/07` §6 — is the one such edge a crate "
               "list already carries, and it is the only place the "
               "production machine and `ror-reference` co-reside in one dependency "
               "closure. Keep every one of these dev-dependency-only and behind "
               "the observation interface (R-REF-05), or the independence of the "
               "differential oracle becomes a build-graph fact instead of a "
               "semantic one.",
               [(e["provider"], e["consumer"], e["kind"],
                 f"{crate_of[e['provider']]} -> {crate_of[e['consumer']]}")
                for e in verif]))
    return hd


def security_checks(mod_graph):
    checks = []
    bad_provider = [e for e in mod_graph.edges
                    if e["kind"] == "SECURITY_DEPENDENCY"
                    and e["provider"] not in E.AUTHORITY]
    checks.append(("SC-1", "Every SECURITY_DEPENDENCY provider is an "
                           "authoritative machine-boundary component",
                   bad_provider,
                   "R-TRUST-01/R-TRUST-02 trust table; the provider is the "
                   "component that discharges the property"))
    inbound = [e for e in mod_graph.edges
               if e["provider"] in E.PLANNER_NODES
               and e["kind"] == "SECURITY_DEPENDENCY"]
    checks.append(("SC-2", "The LLM/planner is never the provider of a security "
                           "property",
                   inbound, "R-PLANNER-02 (planner cannot allocate/authorize/"
                            "modify/invoke/bypass); R-TRUST-01 trust-table row "
                            "'LLM / planner: No'"))
    outbound = [e for e in mod_graph.edges
                if e["provider"] in E.PLANNER_NODES
                and e["consumer"] in E.PRODUCTION_NODES
                and e["kind"] == "RUNTIME_DEPENDENCY"]
    checks.append(("SC-3", "No production component calls the planner at runtime",
                   outbound, "R-ARCH-01: the planner is upstream of the machine; "
                             "the machine never calls back into `ror-agent`"))
    return checks


def reference_checks(mod_graph, crate_graph):
    checks = []
    present = {(e["consumer"], e["provider"]) for e in crate_graph.edges}
    violated = [(d, p, ev) for d, p, ev in E.FORBIDDEN_CRATE_EDGES if (d, p) in present]
    checks.append(("RI-1", "None of the ten frozen forbidden crate edges exists",
                   violated, "L39807-39828 §14; L39645-39651 §10"))
    impl = [e for e in mod_graph.edges
            if e["consumer"] in E.REFERENCE_NODES
            and e["kind"] in E.IMPLEMENTABLE_KINDS]
    checks.append(("RI-2", "No MOD-14 dependency has an implementable kind "
                           "(TYPE/RUNTIME/SERIALIZATION/PERSISTENCE/SECURITY)",
                   impl, "R-REF-02 / R-SCOPE-04 zero shared core logic"))
    out_impl = [e for e in mod_graph.edges
                if e["provider"] in E.REFERENCE_NODES
                and e["kind"] in E.IMPLEMENTABLE_KINDS]
    checks.append(("RI-3", "No production module takes an implementable "
                           "dependency on MOD-14 (oracle edges are "
                           "VERIFICATION_DEPENDENCY only)",
                   out_impl, "R-RECOV-04 / REQ-TEST-045 'not a crate edge'"))
    prod_in_verif = [e for e in mod_graph.edges
                     if e["consumer"] in E.PRODUCTION_NODES
                     and e["provider"] in E.VERIFICATION_NODES
                     and e["kind"] in E.IMPLEMENTABLE_KINDS]
    checks.append(("RI-4", "No production module depends implementably on any "
                           "verification node",
                   prod_in_verif, "R-ARCH-02: verification is co-equal and "
                                  "outside the production dependency chain"))
    return checks


FORBIDDEN_BLOCK_LINES = ("39762", "39772", "39807", "39809", "39815", "39816",
                         "39817", "39818", "39820", "39821", "39823", "39824",
                         "39826")


def forbidden_block_citations():
    """Which documents cite the frozen dependency-direction blocks?

    `Red-on-Rust.md` L39757-39790 is §13 'Dependency Graph' and L39807-39828 is
    §14 'Forbidden Dependency Edges'.  V-02 claims no obligation, atomic record
    or finding cites them; this recomputes that claim on every run.
    """
    hits = []
    for sub in ("req", "spec", "mod"):
        for path in sorted((ROOT / sub).glob("*.md")):
            body = path.read_text()
            for ln in FORBIDDEN_BLOCK_LINES:
                if ln in body:
                    hits.append((f"{sub}/{path.name}", ln))
    return hits


TRUST_ROW_RE = re.compile(
    r"^\|\s*([^|]+?)\s*\|\s*\*{0,2}(Yes|No|Partial(?:ly trusted)?)\*{0,2}\s*"
    r"\|\s*([^|]+?)\s*\|\s*$")


def trust_tables(path="Red-on-Rust.md", md=True):
    """Every statement of the component trust table in a markdown file.

    Returns a list of runs; each run is a list of (line, component, trust, role).
    `Red-on-Rust.md` states the table twice (L27613-27623 and L41827-41838); the
    later one governs under the repository's supersession rule. `README.md`
    renders the same table with one cell per line, hence `md=False`.
    """
    if not md:
        return [_readme_trust_table()]
    runs, cur = [], []
    for i, line in enumerate((ROOT / path).read_text().splitlines(), 1):
        m = TRUST_ROW_RE.match(line)
        if m:
            cur.append((i, m.group(1), m.group(2), m.group(3)))
        elif cur:
            runs.append(cur)
            cur = []
    if cur:
        runs.append(cur)
    return runs


README_TRUST_TRUST = ("Yes", "No", "Partial", "Partially trusted")


def _readme_trust_table():
    """`README.md` renders the trust table as one cell per line; regroup it."""
    cells = [ln.strip() for ln in (ROOT / "README.md").read_text().splitlines()
             if ln.strip()]
    rows = []
    for i in range(len(cells) - 2):
        if cells[i + 1].strip("`*") in README_TRUST_TRUST:
            rows.append((i, cells[i].strip("`"), cells[i + 1].strip("`*"),
                         cells[i + 2]))
    return rows


def readme_trust_drift():
    """Does `README.md`'s copy of the trust table match the frozen one?

    Returns (source_rows, readme_rows, differing) where `differing` lists
    (component, source_trust, readme_trust) for mismatches and components
    present in only one of the two.
    """
    src = trust_tables()[-1]
    rd = trust_tables(md=False)[0]
    s_map = {c.strip("`"): (t, r) for _l, c, t, r in src}
    r_map = {c.strip("`"): (t, r) for _l, c, t, r in rd}
    diff = []
    for comp in sorted(set(s_map) | set(r_map)):
        a, b = s_map.get(comp), r_map.get(comp)
        if a != b:
            diff.append((comp,
                         f"{a[0]} / {a[1]}" if a else "_absent_",
                         f"{b[0]} / {b[1]}" if b else "_absent_"))
    return src, rd, diff


def authority_provenance():
    """Which AUTHORITY / NON_AUTHORITY entries the frozen trust table backs.

    Returns (frozen, inferred, partial, unlisted_rows) where `frozen` and
    `inferred` are module lists, `partial` maps a module to its non-`Yes` rows,
    and `unlisted_rows` lists table components no module claims.
    """
    runs = trust_tables()
    latest = runs[-1] if runs else []
    rows = {c: (t, r, l) for l, c, t, r in latest}
    frozen, inferred, partial = [], [], {}
    claimed = set()
    for mod, comps in E.TRUST_ROWS_OF_MODULE.items():
        if mod not in E.AUTHORITY and mod not in E.NON_AUTHORITY:
            continue
        if not comps:
            if mod in E.AUTHORITY:
                inferred.append(mod)
            continue
        for comp in comps:
            claimed.add(comp)
            if comp not in rows:
                if mod in E.AUTHORITY:
                    inferred.append(mod)
                continue
            trust = rows[comp][0]
            if mod in E.AUTHORITY:
                if trust == "Yes":
                    frozen.append(mod)
                else:
                    partial.setdefault(mod, []).append(f"{comp}={trust}")
    unlisted = [c for c in rows if c not in claimed]
    return (sorted(set(frozen)), sorted(set(inferred)), partial, unlisted, runs)


def direction_checks():
    out = []
    spec07 = (ROOT / "spec/07-implementation-mapping.md").read_text()
    spec04 = (ROOT / "spec/04-dependency-graph.md").read_text()
    mod18 = (ROOT / "mod/18-ownership-matrix.md").read_text()
    # ID-1: spec/04 convention
    ok04 = ("S07->S08" in spec04) and ("**S-08 depends on S-07**" in spec04)
    out.append(("ID-1", "`spec/04` arrow convention (provider -> consumer)",
                "confirmed" if ok04 else "NOT CONFIRMED",
                "`spec/04` DOT edge `S07->S08` is annotated 'S-08 depends on "
                "S-07' — the same convention as this document set."))
    # ID-2: mod/18 convention
    ok18 = ("MOD-02 COMPILER" in mod18 and "-> MOD-01 CORE" in mod18
            and "ror-compiler -> ror-core" in mod18)
    out.append(("ID-2", "`mod/18` arrow convention (dependent -> dependency)",
                "confirmed" if ok18 else "NOT CONFIRMED",
                "`mod/18` §0 renders `MOD-02 COMPILER -> MOD-01 CORE [crate] "
                "ror-compiler -> ror-core`, i.e. the arrow points at the "
                "dependency — the OPPOSITE of `spec/04`. See V-06."))
    # ID-3: §13 diagram vs spec/07 §6
    diff = []
    doc_edges = {(p, c) for p, c, _k, _e in E.CRATE_EDGES}
    for p, c in E.CRATE_DIAGRAM_EDGES:
        if (p, c) not in doc_edges:
            diff.append((p, c))
    out.append(("ID-3", "§13 diagram edges absent from the frozen crate list",
                diff,
                "L39762-39790 §13 asserts `ror-runtime -> ror-persistence`, "
                "`ror-runtime -> ror-host` and `ror-persistence -> ror-agent`; "
                "the first contradicts `spec/07` §3 (request step 14 calls "
                "`ror-persistence` from `ror-runtime`). See V-04."))
    # ID-4: index depends_on vocabulary
    index = json.loads((ROOT / "spec/10-index.json").read_text())
    names = {n for n, _r in E.CRATE_NODES}
    bad = [(c["name"], d) for c in index["crates"] for d in c["depends_on"]
           if d not in names]
    out.append(("ID-4", "`spec/10-index.json` `depends_on` entries that are not "
                        "crate names", bad,
                "prose inside a machine-readable edge list; any consumer of the "
                "index reads a wrong node set. See V-05."))
    hits = forbidden_block_citations()
    out.append(("ID-5", "documents citing `Red-on-Rust.md` L39757-39828 "
                        "(§13 diagram / §14 forbidden edges)",
                hits or "none",
                "none of `spec/03`, `spec/06`, `req/` or `mod/` cites the frozen "
                "dependency-direction blocks — the basis of V-02 and HD-5."))
    # ID-6: MODULE_DEPS entries labelled `crate` that no crate list carries
    crate_of = crate_of_module()
    frozen = {(p, c) for p, c, _k, _e in E.CRATE_EDGES}
    crate_level = [t for t in O.MODULE_DEPS if t[2] == "crate"]
    gap = []
    for dep, prov, _lvl, why in crate_level:
        pc, cc = crate_of.get(prov), crate_of.get(dep)
        if pc is None or cc is None or pc == cc or (pc, cc) in frozen:
            continue
        forbidden = any(d == cc and p == pc for d, p, _e in E.FORBIDDEN_CRATE_EDGES)
        gap.append((prov, dep,
                    ("FORBIDDEN " if forbidden else "") + f"{pc} -> {cc}",
                    why + (" — §14 forbids this direction outright" if forbidden
                           else "")))
    out.append(("ID-6", "`mod/_ownership.MODULE_DEPS` entries labelled `crate` "
                        "whose implied crate edge no crate list carries", gap,
                f"{len(gap)} of the {len(crate_level)} `crate`-labelled entries "
                f"(of {len(O.MODULE_DEPS)} total). `MOD-11 -> MOD-08` is the "
                "step-14 durability call of R-DUR-02; `MOD-03 -> MOD-04` needs "
                "`ror-core -> ror-kernel`, which L39821 §14 forbids. The other "
                "three have a non-crate home (`tests/`, "
                "`mutations/registry.toml`) on one side. See V-10, HD-3."))
    # ID-7: is the authoritative-boundary set backed by the frozen trust table?
    frozen_a, inferred_a, partial_a, unlisted, runs = authority_provenance()
    prov = [(m, ", ".join(E.TRUST_ROWS_OF_MODULE.get(m) or ()) or "no row",
             ("frozen + partial" if m in partial_a else
              "frozen" if m in frozen_a else "INFERRED"),
             E.AUTHORITY[m]) for m in sorted(E.AUTHORITY)]
    out.append(("ID-7", "`AUTHORITY` entries backed by a `Yes` row of the frozen "
                        "trust table (`Red-on-Rust.md` L41827-41838)", prov,
                f"{len(frozen_a)} of {len(E.AUTHORITY)} are frozen by the table; "
                f"{len(inferred_a)} ({', '.join(inferred_a)}) have no row and are "
                "inferred from obligations; `MOD-09` is `Yes` only as the replay "
                "host (`Live host` is `Partial`). The source states the table "
                f"{len(runs)} times "
                + (": " if len(runs) == 2 else ", ")
                + " and ".join(f"L{r[0][0]}-{r[-1][0]} ({len(r)} rows)"
                               for r in runs)
                + "; the later one adds `Persistence`, which the earlier lacks. "
                  "See V-11."))
    return out, spec07


# --------------------------------------------------------------------------
# rendering helpers
# --------------------------------------------------------------------------
def label(n):
    return f"{n} {O.DOMAIN[n]}" if n in O.DOMAIN else n


def edge_line(e):
    return f"{e['provider']} -> {e['consumer']}"


def kind_table(edges, cols=("provider", "consumer", "kind")):
    rows = ["| `A -> B` (B depends on A) | Kind | Visibility | Basis / evidence |",
            "|---|---|---|---|"]
    for e in edges:
        rows.append(f"| `{e['provider']} -> {e['consumer']}` | {e['kind']} | "
                    f"{e['visibility']} | {e['basis']}{' — ' + e['evidence'] if e['evidence'] and e['evidence'] != e['basis'] else ''} |")
    return "\n".join(rows)


def scc_members(comp):
    return ", ".join(label(n) for n in comp)


# --------------------------------------------------------------------------
# document generation
# --------------------------------------------------------------------------
HEADER = ("GENERATED by `python3 dep/_graph.py --write` — do not edit; edit "
          "`dep/_edges.py` and re-run. Convention: **`A -> B` means B depends "
          "on A** (the arrow points from the thing depended upon to the thing "
          "that depends on it), matching `spec/04`. `mod/18` uses the opposite "
          "convention — see `dep/05` V-06.")


def gen_overview(ctx):
    L = []
    A = L.append
    A("# dep/00 — Typed Dependency Graph: Method\n")
    A("**What this set is.** The dependency layer over the frozen "
      "specification's other three views. "
      "`spec/` splits it into 24 sections, `req/` into 545 atomic records, `mod/` "
      "into 17 semantic modules; `dep/` connects them: one typed, machine-checked "
      "dependency graph over all four layers, with the seven required edge kinds, "
      "and the structural questions answered against it — roots, leaves, strongly "
      "connected components, circular dependencies, hidden dependencies, invalid "
      "dependency directions, and requirements referenced before definition.\n")
    A("**What it is not.** It adds no normative text and no new obligation. Every "
      "edge cites the place the dependency is already stated (`Red-on-Rust.md` "
      "line ranges, `spec/` sections, `mod/` DEPENDENCIES prose, or `req/` record "
      "IDs). Where the sources disagree, the disagreement is reported as a finding "
      "in `dep/05`, not silently resolved.\n")
    A("---\n")
    A("## 1. Arrow convention\n")
    A("```")
    A("A -> B        means:  B depends on A")
    A("              A is the PROVIDER (depended upon), B the CONSUMER (dependent)")
    A("```")
    A("This is the convention of `spec/04-dependency-graph.md` (its DOT edge "
      "`S07->S08` carries the note \"S-08 depends on S-07\"). It is the **opposite** "
      "of `mod/_ownership.py` / `mod/18-ownership-matrix.md`, whose "
      "`MODULE_DEPS = (from, to, …)` reads *from depends on to*; `dep/_graph.py` "
      "flips `MODULE_DEPS` on import (check 2). Consequences for the vocabulary:\n")
    A("- **root** = a node with no incoming edge = depends on nothing (a foundation).")
    A("- **leaf** = a node with no outgoing edge = nothing depends on it (a terminal "
      "consumer).")
    A("- **topological order** = dependencies before dependents (a build order).\n")
    A("## 2. Edge kinds\n")
    A("| Kind | Meaning | Provider constraint (check 11) | Implementable (would be a Cargo edge) |")
    A("|---|---|---|---|")
    for k in E.KINDS:
        meaning, impl = E.KIND_DEF[k]
        A(f"| `{k}` | {meaning} | {E.KIND_PROVIDER_CHECK[k][0]} | "
          f"{'yes' if impl else 'no'} |")
    A("")
    A("`IMPLEMENTABLE_KINDS` = TYPE / SECURITY / SERIALIZATION / PERSISTENCE / "
      "RUNTIME. `SPECIFICATION_KINDS` = SEMANTIC / VERIFICATION. A cycle that needs "
      "a specification-kind edge to close is a *specification* cycle (a wording "
      "problem); a cycle inside the implementable subgraph is an *implementation* "
      "cycle (a code problem). `dep/03` separates the two.\n")
    A("The provider constraint is a predicate in `dep/_edges.py` "
      "`KIND_PROVIDER_CHECK`, stated over `MOD-NN` names, so check 11 verifies it "
      "against the module layer (L2) and fails the run if any edge of that kind "
      "breaks it. `SEMANTIC_DEPENDENCY` is the one kind that declares itself not "
      "machine-checkable, and check 11 enforces that it stays the only one.\n")
    A("## 3. Layers\n")
    A("| Layer | Nodes | Source of the edges | Document |")
    A("|---|---|---|---|")
    A("| L1 crate | 10 `ror-*` crates | `spec/07` §6, `Red-on-Rust.md` L39196-40762 "
      "§2-§12, L39807-39828 §14 | `dep/01` §1 |")
    A("| L2 module | 17 `MOD-NN` modules | `mod/_ownership.py` MODULE_DEPS ∪ the 17 "
      "module files' DEPENDENCIES prose ∪ `req/` record pairs | `dep/01` §2 |")
    A("| L3 requirement | 545 `REQ-…` records | `req/registry.json` DEPENDENCIES | "
      "`dep/01` §3 |")
    A("| L4 section | 24 `S-NN` sections | `spec/10-index.json` `dependency_graph` "
      "(= `spec/04` §A/DOT) | `dep/01` §4 |")
    A("")
    A("An L2 edge is *visible* if it appears in the crate table or in a module "
      "file's prose, and *witnessed* if at least one `req/` record pair implies it. "
      "Edges that are only witnessed are the hidden dependencies of `dep/05` HD-1.\n")
    A("## 4. Kind classification\n")
    A("Every L2 pair is classified by the first matching rule of "
      f"`dep/_edges.py` `KIND_RULES` ({len(E.KIND_RULES)} rules) or by an explicit "
      f"`KIND_OVERRIDES` ({len(E.KIND_OVERRIDES)} entries); `dep/_graph.py` "
      "check 4 fails the run if a pair matches none, so no "
      "edge can acquire a kind by default. L3 kinds are inherited from the owning "
      "modules when the pair crosses a module boundary, and from the provider "
      "record's area when it does not.\n")
    A("| Rule | Predicate (provider `p`, consumer `c`) | Kind |")
    A("|---|---|---|")
    for name, pred, kind, why in E.KIND_RULES:
        A(f"| `{name}` | `{_src_of(pred)}` | `{kind}` |")
    A("")
    A("| Override | Kind | Reason |")
    A("|---|---|---|")
    for (p, c), (kind, why) in sorted(E.KIND_OVERRIDES.items()):
        A(f"| `{p} -> {c}` | `{kind}` | {why} |")
    A("")
    A("## 5. Files\n")
    A("| File | Content | Maintenance |")
    A("|---|---|---|")
    A("| `00-overview.md` | this document | generated |")
    A("| `01-graph.md` | the typed graph, all four layers (output 1) | generated |")
    A("| `02-topological-order.md` | topological orderings and levels (output 2) | generated |")
    A("| `03-cycles.md` | SCCs, cycles, and per-cycle verdicts (output 3) | generated |")
    A("| `04-cross-section-table.md` | module × kind cross-section table (output 4) | generated |")
    A("| `05-violations.md` | hidden dependencies, invalid directions, independence violations (output 5) | generated |")
    A("| `10-graph.json` | machine-readable graph + analysis. The crate, module "
      "and section layers carry full node and edge lists; the requirement layer "
      "carries `node_count`, its 927 edges, roots, leaves, non-trivial SCCs and "
      "the 50 largest forward references, but not the 545 node names | generated |")
    A("| `_edges.py` | typed edge tables, classification rules, findings | hand-written |")
    A(f"| `_graph.py` | generator + checker (the {n_checks()} checks in its docstring) "
      "| hand-written |")
    A("")
    A("```")
    A("python3 dep/_graph.py            # check; non-zero exit on any error")
    A("python3 dep/_graph.py --write    # regenerate 01..05 + 10-graph.json")
    A("```")
    A("")
    A("The checker needs nothing beyond the standard library except for check 12, "
      "which parses the two ```dot blocks in `dep/01` with `pydot` and compares "
      "them against the graphs they were generated from. Without `pydot` the run "
      "still passes; it reports `DOT validation : SKIPPED` so the gap is visible "
      "rather than silent. Install it with `pip install pydot` to close it. "
      "Rendering the blocks to an image additionally needs the `graphviz` "
      "binaries (`dot`), which the checker never invokes.\n")
    A("**Status discipline.** Unchanged from `spec/00` §2: every requirement is "
      "`SPECIFIED`. A dependency edge is a statement about the specification, not "
      "evidence that anything is implemented; this repository still contains no "
      "Cargo workspace, so no layer of this graph has been exercised by a build.\n")
    return "\n".join(L) + "\n"


def _src_of(pred):
    import inspect
    try:
        src = inspect.getsource(pred).strip()
        return src.split("lambda p, c:", 1)[1].rstrip().rstrip(",")
    except (OSError, TypeError):
        return "?"


def gen_graph(ctx):
    L = []
    A = L.append
    A("# dep/01 — Dependency Graph\n")
    A(HEADER + "\n")
    A("## 0. Summary\n")
    A("| Layer | Nodes | Edges | " + " | ".join(E.KINDS) + " |")
    A("|---|---|---|" + "---|" * len(E.KINDS))
    for g in (ctx["crate"], ctx["module"], ctx["req"], ctx["section"]):
        counts = collections.Counter(e["kind"] for e in g.edges)
        A(f"| {g.name} | {len(g.nodes)} | {len(g.edges)} | "
          + " | ".join(str(counts.get(k, 0)) for k in E.KINDS) + " |")
    A("")
    A("Roots/leaves per layer: §1.4 (crate), §2.8 (module), §3.3 (requirement), "
      "§4 (section). Orderings in `dep/02`; cycles in `dep/03`; the cross-section "
      "table in `dep/04`; violations in `dep/05`.\n")

    # ---- L1
    A("---\n\n## 1. Layer 1 — crate graph (10 crates)\n")
    A("Edges are the frozen crate direction (`spec/07` §6, restated from "
      "R-REPO-02/R-ARCH-04 and `Red-on-Rust.md` L39196-40762 §2-§12). Parallel "
      "edges of different kinds between the same pair are kept: `ror-persistence` "
      "depends on `ror-core` both for types and for the 15A byte format.\n")
    A(kind_table(ctx["crate"].edges))
    A("")
    A("### 1.1 Forbidden edges (frozen; none may appear above)\n")
    A("| Dependent | MUST NOT depend on | Source | Present? |")
    A("|---|---|---|---|")
    present = {(e["consumer"], e["provider"]) for e in ctx["crate"].edges}
    for d, p, ev in E.FORBIDDEN_CRATE_EDGES:
        A(f"| `{d}` | `{p}` | {ev} | {'**YES — VIOLATION**' if (d, p) in present else 'no'} |")
    A("")
    A("### 1.2 Required edges absent from every crate list\n")
    A("| `A -> B` (B depends on A) | Kind | Why the specification forces it |")
    A("|---|---|---|")
    for p, c, k, why in E.CRATE_MISSING_EDGES:
        A(f"| `{p} -> {c}` | {k} | {why} |")
    A("")
    aug = crate_graph_augmented(ctx["crate"])
    aord, astuck = aug.toposort()
    nscc = [c for c in aug.sccs() if len(c) > 1]
    before, after = ctx["crate"].levels(), aug.levels()
    b_of = {n: l for l, ms in before.items() for n in ms}
    a_of = {n: l for l, ms in after.items() for n in ms}
    moved = [(n, b_of[n], a_of[n]) for n in sorted(b_of) if b_of[n] != a_of.get(n)]
    A(f"**Adding all {len(E.CRATE_MISSING_EDGES)} keeps the crate layer acyclic** "
      f"({len(aug.edges)} edges, {len(nscc)} non-trivial SCCs"
      + ("" if not nscc else ": " + "; ".join(scc_members(c) for c in nscc))
      + ")"
      + ("" if not astuck else f", though {len(astuck)} crates become unplaceable")
      + ". The dependency levels of `dep/02` §1 change for "
      + (", ".join(f"`{n}` (level {b} -> {a})" for n, b, a in moved)
         if moved else "**no crate at all**")
      + (" — `ror-agent` drops below `ror-host` only because of the "
         "replay-composition edge whose direction is undecided (V-04); the other "
         "three gaps cost nothing." if moved else "")
      + " Every gap in this section is therefore cheap to close: none of them "
        "introduces a cycle, and none forces a workspace re-ordering beyond the "
        "one undecided edge.\n")
    A("### 1.3 Picture (graphviz, generated from the table above)\n")
    A("Arrows point to the dependent, exactly as in the table and in `spec/04`'s "
      "DOT block. Parallel edges of different kinds are separate arrows.\n")
    A("```dot")
    A("digraph ror_crates {")
    A('  rankdir=LR; node [shape=box, style=rounded, fontname="monospace"];')
    A('  edge  [fontname="monospace", fontsize=9];')
    for name, role in E.CRATE_NODES:
        style = ", color=gray40" if role == "verification" else ""
        A(f'  "{name}" [label="{name}\\n({role})"{style}];')
    for e in ctx["crate"].edges:
        A(f'  "{e["provider"]}" -> "{e["consumer"]}" '
          f'[label="{e["kind"].replace("_DEPENDENCY", "")}"];')
    A("  // ror-reference keeps no production edge (R-REF-02; L39807-39828 S14).")
    A("  // A call is not a dependency: ror-runtime CALLS ror-persistence at")
    A("  // request step 14, but ror-persistence does not depend on ror-runtime")
    A("  // (spec/07 S3; the S13 diagram implies otherwise - V-04).")
    A("  // Forced by the specification yet absent from every crate list (HD-3):")
    A("  //   ror-compiler -> ror-runtime   (ExecutablePlan, V-01)")
    A("  //   ror-persistence -> ror-agent  (PlannerAccepted recording)")
    A("  //   ror-host <-> ror-agent        (replay composition, V-04)")
    A("}")
    A("```")
    A("")
    A("### 1.4 Structural facts\n")
    g = ctx["crate"]
    A(f"- roots (depend on nothing): {', '.join('`%s`' % n for n in g.roots)}")
    A(f"- leaves (nothing depends on them): {', '.join('`%s`' % n for n in g.leaves)}")
    A(f"- SCCs: {len(g.sccs())} (all trivial — the crate graph is acyclic)"
      if all(len(c) == 1 for c in g.sccs()) else
      f"- SCCs: {len(g.sccs())} — **non-trivial components present**")
    A("")
    A("### 1.5 `spec/10-index.json` disagreement\n")
    idx = ctx["index"]
    A("| Crate | `spec/07` §6 / this table | `spec/10-index.json` `depends_on` |")
    A("|---|---|---|")
    for name, _role in E.CRATE_NODES:
        mine = sorted({e["provider"] for e in ctx["crate"].edges if e["consumer"] == name})
        theirs = next((c["depends_on"] for c in idx["crates"] if c["name"] == name), [])
        flag = "" if mine == sorted(d for d in theirs if d.startswith("ror-")) else " **≠**"
        A(f"| `{name}` | {', '.join('`%s`' % m for m in mine) or '—'} | "
          f"{', '.join('`%s`' % t for t in theirs) or '—'}{flag} |")
    A("")
    A("See `dep/05` V-05 (and ID-4 for the non-crate entries).\n")

    # ---- L2
    A("---\n\n## 2. Layer 2 — module graph (17 modules)\n")
    mg = ctx["module"]
    A(f"{len(mg.edges)} edges over 17 nodes. Visibility: `crate-table` = present in "
      "`mod/_ownership.py` MODULE_DEPS; `prose` = declared in the module file's "
      "DEPENDENCIES; `N req` = witnessed by N `req/` record pairs.\n")
    for kind in E.KINDS:
        sub = [e for e in mg.edges if e["kind"] == kind]
        A(f"### 2.{E.KINDS.index(kind)+1} `{kind}` ({len(sub)} edges)\n")
        if not sub:
            A("_none_\n")
            continue
        meaning, impl = E.KIND_DEF[kind]
        pred = E.KIND_PROVIDER_CHECK[kind][1]
        A(f"_{meaning}_ Provider constraint: {E.KIND_PROVIDER_CHECK[kind][0]}. "
          f"Implementable: {'yes' if impl else 'no'}.\n")
        if pred:
            A(f"Check 11 verifies that constraint against all {len(sub)} edges "
              "below.\n")
        else:
            A(f"Check 11 records this kind as not machine-checkable, so the "
              f"{len(sub)} edges below carry no provider assertion.\n")
        A("| `A -> B` (B depends on A) | Rule | Visibility | Why |")
        A("|---|---|---|---|")
        for e in sorted(sub, key=lambda e: (e["provider"], e["consumer"])):
            A(f"| `{label(e['provider'])} -> {label(e['consumer'])}` | {e['rule']} | "
              f"{e['visibility']} | {e['basis']} |")
        A("")
    impl = ctx["impl"]
    A("### 2.8 Structural facts\n")
    A("| Subgraph | Roots (depend on nothing) | Leaves (nothing depends on them) |")
    A("|---|---|---|")
    A("| full typed graph | " + (", ".join(f"`{label(n)}`" for n in mg.roots) or "_none_")
      + " | " + (", ".join(f"`{label(n)}`" for n in mg.leaves) or "_none_") + " |")
    A("| implementation graph | " + (", ".join(f"`{label(n)}`" for n in impl.roots) or "_none_")
      + " | " + (", ".join(f"`{label(n)}`" for n in impl.leaves) or "_none_") + " |")
    prod_nodes = [n for n in mg.nodes if n in E.PRODUCTION_NODES]
    A("| production modules, implementation edges | "
      + (", ".join(f"`{label(n)}`" for n in impl.sub(nodes=prod_nodes).roots) or "_none_")
      + " | " + (", ".join(f"`{label(n)}`" for n in impl.sub(nodes=prod_nodes).leaves) or "_none_")
      + " |")
    A("")
    A("`MOD-01` is a root of neither: it is the foundation every module depends on "
      "for types, but its own central-invariant restatements depend on the "
      "operative statements single-homed elsewhere (F-CORE-RESTATEMENT). "
      "`MOD-14` is a root of the implementation graph — the structural statement "
      "of reference independence (R-REF-02).\n")
    A("- most depended on (modules needing it), top: "
      + ", ".join(f"`{label(n)}`={len(mg.dependents[n])}"
                  for n in sorted(mg.nodes, key=lambda n: -len(mg.dependents[n]))[:5]))
    A("- most dependent (modules it needs), top: "
      + ", ".join(f"`{label(n)}`={len(mg.depends_on[n])}"
                  for n in sorted(mg.nodes, key=lambda n: -len(mg.depends_on[n]))[:5]))
    A("")
    A("### 2.9 DOT\n")
    A("```dot")
    A("digraph ror_modules {")
    A('  rankdir=LR; node [shape=box, fontname="monospace"];')
    A("  // A -> B means B depends on A")
    colors = {"TYPE_DEPENDENCY": "black", "SEMANTIC_DEPENDENCY": "gray50",
              "SECURITY_DEPENDENCY": "red", "SERIALIZATION_DEPENDENCY": "blue",
              "PERSISTENCE_DEPENDENCY": "darkgreen",
              "VERIFICATION_DEPENDENCY": "purple", "RUNTIME_DEPENDENCY": "orange"}
    for n in mg.nodes:
        A(f'  "{n}" [label="{n}\\n{O.DOMAIN[n]}"];')
    for e in sorted(mg.edges, key=lambda e: (e["kind"], e["provider"], e["consumer"])):
        style = "solid" if e["kind"] in E.IMPLEMENTABLE_KINDS else "dashed"
        A(f'  "{e["provider"]}" -> "{e["consumer"]}" '
          f'[color={colors[e["kind"]]}, style={style}];  // {e["kind"]}')
    A("}")
    A("```")
    A("")

    # ---- L3
    A("---\n\n## 3. Layer 3 — requirement graph (545 atomic records)\n")
    rg = ctx["req"]
    A(f"{len(rg.edges)} edges from the `DEPENDENCIES` field of "
      "`req/registry.json` (single IDs plus the 13 expanded `REQ-X-nnn…mmm` "
      "ranges). The full edge list is in `dep/10-graph.json` "
      "(`layers.requirement.edges`); the tables below summarise it.\n")
    A("### 3.1 By kind\n")
    counts = collections.Counter(e["kind"] for e in rg.edges)
    A("| Kind | Edges |")
    A("|---|---|")
    for k in E.KINDS:
        A(f"| `{k}` | {counts.get(k, 0)} |")
    A(f"| **total** | **{len(rg.edges)}** |")
    A("")
    agg = collections.Counter()
    intra = 0
    for e in rg.edges:
        pm, cm = ctx["owner"][e["provider"]], ctx["owner"][e["consumer"]]
        if pm != cm:
            agg[(pm, cm)] += 1
        else:
            intra += 1
    A(f"### 3.2 Aggregated to modules ({len(agg)} pairs)\n")
    A(f"Counts are record pairs; the kind is the module-layer kind of the pair. "
      f"{sum(agg.values())} of the {len(rg.edges)} requirement-layer edges cross a "
      f"module boundary and aggregate into these {len(agg)} pairs; the remaining "
      f"{intra} join two records of the same module, so they aggregate to nothing "
      "at this layer.\n")
    A("| `A -> B` (B depends on A) | Kind | Record pairs |")
    A("|---|---|---|")
    kind_of = {(e["provider"], e["consumer"]): e["kind"] for e in ctx["module"].edges}
    for (pm, cm), n in sorted(agg.items(), key=lambda kv: (-kv[1], kv[0])):
        A(f"| `{pm} -> {cm}` | {kind_of.get((pm, cm), '?')} | {n} |")
    A("")
    A("### 3.3 Structural facts\n")
    A(f"- **roots** (records that depend on nothing): {len(rg.roots)} — "
      + ", ".join(f"`{n}`" for n in rg.roots))
    A(f"- **leaves** (records nothing depends on): {len(rg.leaves)}")
    ntr = [c for c in rg.sccs() if len(c) > 1]
    A(f"- SCCs: {len(rg.sccs())}, of which **{len(ntr)} are non-trivial** "
      f"(circular requirements — see `dep/03` §3)")
    A(f"- largest SCC: {len(max(rg.sccs(), key=len))} records")
    A("")
    A("### 3.4 Requirements referenced before definition\n")
    fr = ctx["fwd_req"]
    A(f"**{len(fr)} of {len(rg.edges)} edges ({100*len(fr)//len(rg.edges)}%)** point "
      "at a record whose first cited `Red-on-Rust.md` line is *later* than the "
      "citing record's. This is expected for a specification assembled from a "
      "60-turn transcript whose later turns freeze what earlier turns assumed; it "
      "is a reading-order hazard, not a defect. The 15 largest gaps:\n")
    A("| Citing record | Defined at | Depends on | Defined at | Gap |")
    A("|---|---|---|---|---|")
    for a, b, la, lb in fr[:15]:
        A(f"| `{a}` | L{la} | `{b}` | L{lb} | +{lb-la} lines |")
    A("")
    A("At section level the same test gives "
      f"{len(ctx['fwd_sec'])} forward references: "
      + "; ".join(f"`{p} -> {c}` ({c} uses {p})" for c, p in ctx["fwd_sec"])
      + " (`spec/04` §A draws the cycle-closing edges `S-22 -> S-07/S-10/S-18` "
        "and `S-21 -> S-23` dashed for exactly this reason).\n")

    # ---- L4
    A("---\n\n## 4. Layer 4 — section graph (24 sections)\n")
    sg = ctx["section"]
    A("Edges are `spec/10-index.json` `dependency_graph.section_edges`, generated "
      "from `spec/_build_index.py` `section_edges`, which restates `spec/04` §A "
      "and its DOT block. Kinds are assigned by `dep/_edges.py` "
      "`SECTION_KIND_RULES`.\n")
    A("| `A -> B` (B depends on A) | Kind | Rule |")
    A("|---|---|---|")
    for e in sorted(sg.edges, key=lambda e: (e["provider"], e["consumer"])):
        A(f"| `{e['provider']} -> {e['consumer']}` | {e['kind']} | {e['rule']} |")
    A("")
    catch = [e for e in sg.edges if e["rule"] == "S-presentation-order"]
    A(f"Kinds come from the first matching rule of `SECTION_KIND_RULES` "
      f"({len(E.SECTION_KIND_RULES)} rules). The last rule is a catch-all, so "
      f"unlike the module layer a section edge cannot fail classification: "
      f"**{len(catch)} of {len(sg.edges)} edges** are `SEMANTIC_DEPENDENCY` by "
      "default and mean 'the source presents the consumer after the provider', "
      "not a semantic prerequisite — "
      + ", ".join(f"`{e['provider']} -> {e['consumer']}`" for e in
                  sorted(catch, key=lambda e: (e["provider"], e["consumer"])))
      + ". They are the weakest edges in this layer and the first to re-examine "
        "if the section cycle of `dep/03` §4 is ever broken.\n")
    A(f"- **roots**: {', '.join('`%s`' % n for n in sg.roots) or '_none_'}")
    A(f"- **leaves**: {', '.join('`%s`' % n for n in sg.leaves) or '_none_'}")
    ntr = [c for c in sg.sccs() if len(c) > 1]
    A(f"- SCCs: {len(sg.sccs())}, non-trivial: {len(ntr)}"
      + ("" if not ntr else " — " + "; ".join(scc_members(c) for c in ntr)))
    A("")
    return "\n".join(L) + "\n"


def gen_topo(ctx):
    L = []
    A = L.append
    A("# dep/02 — Topological Ordering\n")
    A(HEADER + "\n")
    A("Orderings list **dependencies before dependents** (a build order). Where a "
      "layer contains cycles, a total order does not exist; the section gives the "
      "topological order of the SCC condensation instead and names the nodes left "
      "inside cycles.\n")

    g = ctx["crate"]
    order, _stuck = g.toposort()
    A("## 1. Layer 1 — crate graph\n")
    A("Acyclic, so a total order exists. Ties — crate pairs with no edge in either "
      "direction in `spec/07` §6 — are broken **alphabetically by crate name**, "
      "which is what `Graph.toposort()` does (`sorted()`); the relative order of "
      "a tied pair is an artefact of that and carries no architectural meaning. "
      "`ror-persistence` and `ror-runtime` are such a tie: neither depends on the "
      "other, because the durable layer does not depend on the machine — the "
      "machine calls it (`spec/07` §3, R-DUR-02) — and alphabetically persistence "
      "sorts first. So adding the `ror-runtime -> ror-persistence` edge that "
      "`mod/_ownership.MODULE_DEPS` labels `crate` but `spec/07` §6 does not carry "
      "(V-10), which `Red-on-Rust.md` §13 draws the other way (V-04), would not "
      "move `ror-runtime` — persistence already precedes it here (`dep/01` §1.2).\n")
    A("```")
    for i, n in enumerate(order, 1):
        A(f"{i:2d}. {n}")
    A("```")
    A("")

    A("## 2. Layer 2 — module graph\n")
    mg, impl = ctx["module"], ctx["impl"]
    A("### 2.1 Implementation graph (edges a frozen crate edge can carry)\n")
    A("This is the order a Cargo workspace would have to be built in. Edges are "
      "kept only where both modules sit in one crate or `spec/07` §6 carries the "
      "crate edge.\n")
    order, stuck = impl.toposort()
    A("```")
    for i, n in enumerate(order, 1):
        A(f"{i:2d}. {n} {O.DOMAIN[n]:<14} ({ctx['crate_of'][n]})")
    A("```")
    incyc = sorted({n for c in impl.sccs() if len(c) > 1 for n in c})
    A(f"Kahn's algorithm places {len(order)} nodes; the remaining "
      f"{len(stuck)} are downstream of the three intra-crate SCCs of `dep/03` §2.1 "
      f"({', '.join(incyc)}), so they have no position until each SCC is collapsed "
      "to a single node. Inside an SCC the order is free (one crate); between SCCs "
      "the condensation below is the usable build order:\n")
    A("```")
    for lvl, members in impl.levels().items():
        A(f"level {lvl}: " + ", ".join(f"{n} {O.DOMAIN[n]}" for n in members))
    A("```")
    A("")
    A("### 2.2 Full typed graph — condensation order\n")
    A("With every edge included the module graph is one strongly connected "
      "component (`dep/03` §2.3), so no partial order exists at all. The listing "
      "below is the same graph with the two *specification-layer* families of "
      "`dep/03` §2.2 removed — **F-CORE-RESTATEMENT** (central invariants "
      "restated in the thesis text) and **F-EVIDENCE-LOOP** (a module citing the "
      "evidence that discharges it, and the evidence citing back) — because those "
      "pairs carry no Cargo edge and no obligation of their own:\n")
    all_pairs = mutual_pairs(mg)
    spec_fro = {fs for fs in all_pairs
                if cycle_family(fs)[0] in ("F-CORE-RESTATEMENT", "F-EVIDENCE-LOOP")}
    spec_pairs = {(a, b) for fs in spec_fro for a in fs for b in fs if a != b}
    core_free = mg.sub(pairs_exclude=spec_pairs)
    order, stuck = core_free.toposort()
    rest = collections.Counter(cycle_family(fs)[0] for fs in all_pairs
                               if fs not in spec_fro)
    A("```")
    for i, n in enumerate(order, 1):
        A(f"{i:2d}. {n} {O.DOMAIN[n]:<14} ({ctx['crate_of'][n]})")
    if stuck:
        A("   -- inside cycles: " + ", ".join(stuck))
    A("```")
    red_ntr = [c for c in core_free.sccs() if len(c) > 1]
    red_in = sorted(red_ntr[0]) if red_ntr else []
    red_down = [n for n in stuck if n not in red_in]
    A(f"That removes {len(spec_fro)} of the {len(all_pairs)} mutual pairs "
      f"and **still leaves no partial order**: one SCC still covers "
      f"{len(red_in)} modules ({', '.join(red_in)}), and the other "
      f"{len(red_down)} ({', '.join(red_down)}) hang off it, so Kahn's algorithm "
      f"places {len(order)} nodes. The "
      f"{sum(rest.values())} mutual pairs that survive are "
      + ", ".join(f"{k} ({v})" for k, v in sorted(rest.items()))
      + " (`dep/03` §2.2). Each of them is a real coupling between two production "
      "modules, so none can be argued away as specification-layer noise: they close "
      "only when V-01 (`ExecutablePlan`'s crate home), V-03 (MOD-13 as a security "
      "provider) and V-04 (the host/agent replay edge) are decided. The condensation "
      "of the reduced graph is therefore the finest order available:\n")
    A("```")
    for lvl, members in core_free.levels().items():
        A(f"level {lvl}: " + ", ".join(f"{n} {O.DOMAIN[n]}" for n in members))
    A("```")
    A("")

    A("## 3. Layer 3 — requirement graph\n")
    rg = ctx["req"]
    order, stuck = rg.toposort()
    A(f"Kahn's algorithm places {len(order)} of {len(rg.nodes)} records; "
      f"**{sum(len(c) for c in rg.sccs() if len(c) > 1)} records sit inside the "
      f"{len([c for c in rg.sccs() if len(c) > 1])} non-trivial SCCs** of `dep/03` "
      "§3. The table is the condensation layering, which assigns every record a "
      "level (level 0 = depends on nothing, directly or through a cycle):\n")
    levels = rg.levels()
    A("| Level | Records | First / last in level |")
    A("|---|---|---|")
    for lvl, members in levels.items():
        A(f"| {lvl} | {len(members)} | `{members[0]}` … `{members[-1]}` |")
    A("")
    A("Level 0 — the specification's foundation (records that depend on "
      "nothing outside their own cycle):\n")
    A("```")
    A(", ".join(levels[min(levels)]))
    A("```")
    A("")

    sg = ctx["section"]
    order, stuck = sg.toposort()
    cyc = [c for c in sg.sccs() if len(c) > 1]
    A("## 4. Layer 4 — section graph\n")
    inbig = sorted(cyc[0]) if cyc else []
    down = [n for n in stuck if n not in inbig]
    A(f"**Not acyclic.** One SCC covers **{len(inbig)} of the "
      f"{len(sg.nodes)} sections** (`dep/03` §4), so Kahn's algorithm can place "
      f"only the {len(order)} sections above it; the other {len(stuck)} have no "
      f"position — {len(inbig)} because they are in the cycle, {len(down)} "
      f"({', '.join(down)}) because they depend on sections inside it. The loop "
      "closes through the packaging sections: `S-21` (test infrastructure) -> "
      "`S-23` (milestones) -> `S-22` (crate responsibilities) -> `S-07`, `S-10`, "
      "`S-18` (the semantics they package). `spec/04` §A already marks the "
      "cycle-closing edges dashed (`S22->S07`, `S22->S10`, `S22->S18`, "
      "`S21->S23`, DOT block L166-167), so the cycle is visible in the drawing; "
      "it is simply not stated anywhere as a cycle, and no section can be built "
      "before it. (`spec/04` §B's 'Cycle check: no circular dependencies "
      "detected among frozen objects' is about the object layer, not this one.)\n")
    A("```")
    for i, n in enumerate(order, 1):
        A(f"{i:2d}. {n}")
    A("```")
    A(f"**In the cycle ({len(inbig)}):** {', '.join(inbig)}\n")
    A(f"**Downstream of the cycle, also unplaceable ({len(down)}):** "
      f"{', '.join(down)}\n")
    A("Condensation levels (the cycle collapsed to one node):\n")
    A("```")
    for lvl, members in sg.levels().items():
        A(f"level {lvl}: " + ", ".join(members))
    A("```")
    A("")

    return "\n".join(L) + "\n"


def gen_cycles(ctx):
    L = []
    A = L.append
    mg, impl = ctx["module"], ctx["impl"]
    A("# dep/03 — Strongly Connected Components and Cycles\n")
    A(HEADER + "\n")
    A("A strongly connected component (SCC) with more than one member is a set of "
      "nodes that mutually depend on each other: none of them can be specified, "
      "implemented or tested before the others. Two graphs are examined, because "
      "the answer differs:\n")
    A("- the **implementation graph** — the module edges a frozen Cargo edge could "
      f"actually carry ({len(impl.edges)} of {len(mg.edges)}). Cycles here are real "
      "import cycles.")
    A("- the **full typed graph** — all seven kinds. Cycles here are usually "
      "specification cycles: a restatement, an evidence loop, or a "
      "cross-reference that has no code edge behind it.\n")
    A("Every cycle below is matched against a family in `dep/_edges.py` "
      "`CYCLE_FAMILIES`; the run fails if a cycle matches none, so no cycle goes "
      "unjudged.\n")

    A("## 1. Layer 1 — crate graph\n")
    ntr = [c for c in ctx["crate"].sccs() if len(c) > 1]
    A(f"**{len(ntr)} non-trivial SCCs.** The frozen crate graph is a DAG. That is "
      "what makes the independence checks of `dep/05` §1 meaningful: the "
      "prohibitions are satisfiable.\n")

    A("## 2. Layer 2 — module graph\n")
    A("### 2.1 Implementation cycles (edges a frozen crate edge can carry)\n")
    impl_ntr = [c for c in impl.sccs() if len(c) > 1]
    A(f"{len(impl.sccs())} SCCs, **{len(impl_ntr)} non-trivial**. All of them are "
      "inside a single crate, so the crate DAG stays acyclic; they are still real "
      "mutual imports within that crate.\n")
    for comp in impl_ntr:
        fs = frozenset(comp)
        fid, fname, verdict = cycle_family(fs)
        edges = [e for e in impl.edges if e["provider"] in fs and e["consumer"] in fs]
        A(f"#### SCC {{{', '.join(comp)}}} — {ctx['crate_of'][comp[0]]}\n")
        A(f"- family **{fid}** — {fname}")
        A(f"- {len(edges)} edges inside the component:")
        for e in sorted(edges, key=lambda e: (e["provider"], e["consumer"])):
            A(f"  - `{label(e['provider'])} -> {label(e['consumer'])}` "
              f"[{e['kind']}, {e['visibility']}]")
        A(f"- **verdict:** {verdict}")
        A("")
    A("### 2.2 Mutual-dependency pairs in the full typed graph\n")
    mut = mutual_pairs(mg)
    byfam = collections.defaultdict(list)
    for fs in mut:
        fid, fname, verdict = cycle_family(fs)
        byfam[(fid, fname, verdict)].append(fs)
    A(f"**{len(mut)} pairs** of modules depend on each other. Grouped by family:\n")
    for (fid, fname, verdict), members in sorted(byfam.items(), key=lambda kv: kv[0][0] or ""):
        A(f"#### {fid} — {fname} ({len(members)})\n")
        A("| Pair | `A -> B` | `B -> A` |")
        A("|---|---|---|")
        for fs in members:
            a, b = sorted(fs)
            e1 = next(e for e in mg.edges if e["provider"] == a and e["consumer"] == b)
            e2 = next(e for e in mg.edges if e["provider"] == b and e["consumer"] == a)
            A(f"| `{a}` ↔ `{b}` | {e1['kind'].replace('_DEPENDENCY','')} "
              f"[{e1['visibility']}] | {e2['kind'].replace('_DEPENDENCY','')} "
              f"[{e2['visibility']}] |")
        A("")
        A(f"**Verdict:** {verdict}\n")
    A("### 2.3 Why the full graph is one component\n")
    full_ntr = [c for c in mg.sccs() if len(c) > 1]
    all_mp = mutual_pairs(mg)
    spec_fro = {fs for fs in all_mp
                if cycle_family(fs)[0] in ("F-CORE-RESTATEMENT", "F-EVIDENCE-LOOP")}
    reduced = mg.sub(pairs_exclude={(a, b) for fs in spec_fro
                                    for a in fs for b in fs if a != b})
    rest_mp = [fs for fs in all_mp if fs not in spec_fro]
    reduced_ntr = [c for c in reduced.sccs() if len(c) > 1]
    intra_n = len([fs for fs in rest_mp if cycle_family(fs)[0] in
                   ("F-INTRA-RUNTIME", "F-INTRA-CORE", "F-INTRA-PERSISTENCE")])
    A(f"The full typed graph has **{len(full_ntr)} non-trivial SCC covering all "
      f"{len(full_ntr[0]) if full_ntr else 0} modules**. That is not a finding "
      "about the architecture on its own; most of it is the union of the two "
      "systematic families above: every production module is mutually connected "
      "to MOD-01 (central-invariant restatement, F-CORE-RESTATEMENT) and to "
      "MOD-17 (evidence loop, F-EVIDENCE-LOOP), and MOD-01/MOD-17 touch "
      "everything. Deleting those two families removes "
      f"{len(spec_fro)} of the {len(all_mp)} mutual pairs — but **not** the "
      f"cycle: {len(rest_mp)} mutual pairs survive, one SCC still covers all "
      f"{len(reduced_ntr[0]) if reduced_ntr else 0} production modules, and the "
      f"reduced graph still has no root (its only leaves are "
      f"{', '.join(reduced.leaves) or 'none'}), so Kahn's algorithm places "
      f"{len(reduced.toposort()[0])} of {len(reduced.nodes)} modules "
      "(`dep/02` §2.2). The three implementation cycles "
      f"of §2.1 are therefore not the whole story: {intra_n} of the surviving "
      f"pairs are the intra-crate ones of §2.1, and the other {len(rest_mp) - intra_n} "
      "close through couplings that mix the specification and implementation "
      "layers (F-BUDGET-GATE, F-CEILING-OPERAND, F-DURABILITY-JOURNAL, "
      "F-EFFECT-HOST, F-ESCROW-DURABILITY, F-HOST-AGENT, F-PLANNER-TRUST).\n")
    A("| Subgraph | Edges | Non-trivial SCCs | Roots | Leaves |")
    A("|---|---|---|---|---|")
    for name, g in [("full typed graph", mg),
                    ("implementation graph", impl),
                    ("production modules only (all kinds)",
                     mg.sub(nodes=[n for n in mg.nodes if n in E.PRODUCTION_NODES])),
                    ("production, implementation edges",
                     impl.sub(nodes=[n for n in mg.nodes if n in E.PRODUCTION_NODES])),
                    ("verification modules only",
                     mg.sub(nodes=[n for n in mg.nodes if n in E.VERIFICATION_NODES])),
                    (f"full graph minus F-CORE-RESTATEMENT + F-EVIDENCE-LOOP "
                     f"({len(spec_fro)} pairs deleted)", reduced),
                    ("kind-filtered subgraph (NOT the implementability test)",
                     mg.sub(E.IMPLEMENTABLE_KINDS))]:
        n = [c for c in g.sccs() if len(c) > 1]
        A(f"| {name} | {len(g.edges)} | {len(n)}"
          + (f" (largest {len(max(n, key=len))})" if n else "")
          + f" | {', '.join(g.roots) or '—'} | {', '.join(g.leaves) or '—'} |")
    A("")
    kf = mg.sub(E.IMPLEMENTABLE_KINDS)
    A(f"The last row is why kind alone cannot decide implementability: the "
      f"{len(kf.edges)}-edge kind-filtered subgraph has "
      f"{len([c for c in kf.sccs() if len(c) > 1])} non-trivial SCC but "
      f"**{len(elementary_circuits(kf))} elementary circuits of length 2-5** "
      "(9 of length 2, 15 of length 3, 38 of length 4, 87 of length 5), so "
      "'acyclic in kind' is not a usable test. Crate realisability (§2.1) is.\n")

    A("## 3. Layer 3 — requirement graph\n")
    rg = ctx["req"]
    ntr = [c for c in rg.sccs() if len(c) > 1]
    A(f"**{len(ntr)} non-trivial SCCs** among {len(rg.sccs())} components "
      f"({sum(len(c) for c in ntr)} of {len(rg.nodes)} records sit inside a "
      "cycle). Families, classified by the areas involved:\n")
    fam = collections.Counter()
    for c in ntr:
        areas = {r.split("-")[1] for r in c}
        if areas & {"CLAIM"}:
            fam["claim discipline — an obligation and the claim it licenses cite each other"] += 1
        elif areas & {"CORE", "TRUST", "SCOPE", "ARCH"}:
            fam["central-invariant restatement (D-register duplication)"] += 1
        elif len(areas) == 1:
            fam[f"intra-area mutual definition ({sorted(areas)[0]})"] += 1
        else:
            fam["cross-area operational mutual definition"] += 1
    A("| Family | SCCs |")
    A("|---|---|")
    for k, v in fam.most_common():
        A(f"| {k} | {v} |")
    A("")
    A("### 3.1 The one that needs architectural review\n")
    big = max(ntr, key=len)
    A(f"**{len(big)} mutually dependent records** spanning "
      f"{len({r.split('-')[1] for r in big})} areas "
      f"({', '.join(sorted({r.split('-')[1] for r in big}))}): the request "
      "sequence, the issuance transaction, the escrow law, the host gate and the "
      "recovery classification each cite the others.\n")
    A("```")
    sb = sorted(big)
    for i in range(0, len(sb), 6):
        A("  " + "  ".join(f"{x:<16}" for x in sb[i:i + 6]))
    A("```")
    A("Direct mutual citations inside it (each record appears in the other's "
      "DEPENDENCIES):\n")
    eset = {(e["provider"], e["consumer"]) for e in rg.edges}
    shown = 0
    for e in sorted(rg.edges, key=lambda e: (e["consumer"], e["provider"])):
        if (e["consumer"] in big and e["provider"] in big
                and (e["consumer"], e["provider"]) in eset and e["consumer"] < e["provider"]
                and shown < 14):
            A(f"- `{e['consumer']}` ⇄ `{e['provider']}`")
            shown += 1
    A("")
    A("**Verdict.** Two readings are possible and the frozen text does not choose "
      "between them: (a) the 16-step request sequence (R-EFFECT-03) is normative "
      "and the durability transaction (R-DUR-02) is its step 14, or (b) the "
      "issuance transaction is normative and the sequence states when it is "
      "invoked. Conformance testing cannot separate them, so production and "
      "reference may pick different readings and still agree on every observable "
      "— until a crash point separates them (this is the same knot as U-02/U-17). "
      "Recommend naming R-EFFECT-03 the single normative ordering and restating "
      "R-DUR-02 as its step 14.\n")
    A("### 3.2 All non-trivial SCCs\n")
    A("| # | Size | Records | Areas |")
    A("|---|---|---|---|")
    for i, c in enumerate(sorted(ntr, key=lambda c: (-len(c), c[0])), 1):
        areas = ", ".join(sorted({r.split("-")[1] for r in c}))
        cells = (", ".join(f"`{r}`" for r in sorted(c)) if len(c) <= 6
                 else f"`{sorted(c)[0]}` … `{sorted(c)[-1]}`")
        A(f"| {i} | {len(c)} | {cells} | {areas} |")
    A("")

    A("## 4. Layer 4 — section graph\n")
    sg = ctx["section"]
    ntr = [c for c in sg.sccs() if len(c) > 1]
    A(f"{len(sg.sccs())} SCCs, **{len(ntr)} non-trivial**.\n")
    for c in ntr:
        A(f"- **{{{', '.join(c)}}}** ({len(c)} sections) — the loop closes through "
          "the three packaging sections (`S-21` test infrastructure, `S-22` "
          "repository structure, `S-23` milestones): `spec/04` §A draws "
          "`S-22 -> S-07`, "
          "`S-22 -> S-10`, `S-22 -> S-18` dashed (repository structure is *hosted "
          "by* the semantics it packages) while `S-21 -> S-23 -> S-22` runs "
          "forward, so the section graph is cyclic even though `spec/04` §B "
          "reports 'no circular dependencies detected among frozen objects' "
          "(that claim is about the semantic-object graph, not this one).")
    A("")
    A(f"Forward references (a section that uses material defined later): "
      f"{len(ctx['fwd_sec'])} of {len(sg.edges)} — "
      + "; ".join(
          "`%s -> %s` (%s depends on %s, defined %d section%s later)"
          % (p, c, c, p, int(p[2:]) - int(c[2:]),
             "" if int(p[2:]) - int(c[2:]) == 1 else "s")
          for c, p in ctx["fwd_sec"]) + ".\n")
    return "\n".join(L) + "\n"


def gen_table(ctx):
    L = []
    A = L.append
    A("# dep/04 — Cross-Section Dependency Table\n")
    A(HEADER + "\n")
    mg = ctx["module"]
    A("## 1. Module × kind matrix (counts)\n")
    A("Rows are modules; columns are the seven edge kinds. A cell reads "
      "`has ↓ / gives ↑`: **`has`** = how many edges of that kind the module "
      "*needs* (it is the consumer), **`gives`** = how many edges of that kind "
      "point *into* it (other modules need it). The last two columns are the "
      "same counts with the kinds summed. The row total over `has` is the "
      "module's fan-in in the usual sense and over `gives` its fan-out, because "
      "`A -> B` means B depends on A.\n")
    A("| Module | Crate / home | " + " | ".join(k.replace("_DEPENDENCY", "") for k in E.KINDS)
      + " | has (needs) | gives (needed by) |")
    A("|---|---|" + "---|" * (len(E.KINDS) + 2))
    for n in mg.nodes:
        outc = collections.Counter(e["kind"] for e in mg.edges if e["consumer"] == n)
        inc = collections.Counter(e["kind"] for e in mg.edges if e["provider"] == n)
        cells = []
        for k in E.KINDS:
            o, i = outc.get(k, 0), inc.get(k, 0)
            cells.append("—" if (o == 0 and i == 0) else f"{o}↓/{i}↑")
        A(f"| `{n}` {O.DOMAIN[n]} | `{ctx['crate_of'][n]}` | " + " | ".join(cells)
          + f" | {len(mg.depends_on[n])} | {len(mg.dependents[n])} |")
        if (len(mg.depends_on[n]) != sum(1 for e in mg.edges if e["consumer"] == n)
                or len(mg.dependents[n]) != sum(1 for e in mg.edges if e["provider"] == n)):
            err(f"dep/04 matrix row {n} disagrees with the edge list")
    A("")
    A("## 2. Per-module detail\n")
    A("`depends on` lists providers (what the module needs); `depended on by` "
      "lists consumers (what needs it).\n")
    for n in mg.nodes:
        A(f"### `{n}` {O.DOMAIN[n]} — `{ctx['crate_of'][n]}`\n")
        A("| Direction | Kind | Counterpart | Visibility |")
        A("|---|---|---|---|")
        for e in sorted((e for e in mg.edges if e["consumer"] == n),
                        key=lambda e: (e["kind"], e["provider"])):
            A(f"| depends on | {e['kind']} | `{label(e['provider'])}` | {e['visibility']} |")
        for e in sorted((e for e in mg.edges if e["provider"] == n),
                        key=lambda e: (e["kind"], e["consumer"])):
            A(f"| depended on by | {e['kind']} | `{label(e['consumer'])}` | {e['visibility']} |")
        if not mg.depends_on[n] and not mg.dependents[n]:
            A("| — | — | isolated | — |")
        A("")
    A("## 3. Kind × layer\n")
    A("| Kind | crate | module | requirement | section |")
    A("|---|---|---|---|---|")
    for k in E.KINDS:
        row = [sum(1 for e in g.edges if e["kind"] == k)
               for g in (ctx["crate"], ctx["module"], ctx["req"], ctx["section"])]
        A(f"| `{k}` | " + " | ".join(str(x) for x in row) + " |")
    A(f"| **total** | {len(ctx['crate'].edges)} | {len(ctx['module'].edges)} | "
      f"{len(ctx['req'].edges)} | {len(ctx['section'].edges)} |")
    A("")
    A("## 4. Crate × kind\n")
    A("| Crate | Depends on (kind) | Depended on by (kind) |")
    A("|---|---|---|")
    for name, _role in E.CRATE_NODES:
        g = ctx["crate"]
        dep = sorted({f"`{e['provider']}` ({e['kind'].replace('_DEPENDENCY','')})"
                      for e in g.edges if e["consumer"] == name})
        rev = sorted({f"`{e['consumer']}` ({e['kind'].replace('_DEPENDENCY','')})"
                      for e in g.edges if e["provider"] == name})
        A(f"| `{name}` | {', '.join(dep) or '—'} | {', '.join(rev) or '—'} |")
    A("")
    return "\n".join(L) + "\n"


def _realisable_with(e, crate_of, pairs):
    """`realisable` against an injected crate-edge set, for what-if analysis."""
    cp, cc = crate_of[e["provider"]], crate_of[e["consumer"]]
    return cp == cc or (cp, cc) in pairs


def graph_metrics(mg, cg, crate_of, pairs, base_pairs=None):
    """The numbers a decision turns on, computed from the graphs given.

    The implementation graph is defined exactly as `dep/02` §2.1 and `dep/03`
    §2.1 define it — every edge a frozen crate edge can carry, of any kind — so
    the baseline row here reads 50 edges / 3 non-trivial SCCs like the rest of
    the document set. Filtering by `IMPLEMENTABLE_KINDS` as well would give 43 /
    2 and quietly disagree with them.
    """
    impl = Graph("impl", mg.nodes,
                 [e for e in mg.edges if _realisable_with(e, crate_of, pairs)])
    return dict(
        acyclic=not any(len(c) > 1 for c in cg.sccs()),
        module_edges=len(mg.edges),
        impl_edges=len(impl.edges),
        hd1=sum(1 for e in mg.edges
                if e["provider"] in E.PRODUCTION_NODES
                and e["consumer"] in E.PRODUCTION_NODES
                and not _realisable_with(e, crate_of, pairs)),
        impl_sccs=len([c for c in impl.sccs() if len(c) > 1]),
        mutual_full=len(mutual_pairs(mg)),
        mutual_impl=len(mutual_pairs(impl)),
        build_order=cg.toposort()[0],
        carries=[] if base_pairs is None else [
            (e["provider"], e["consumer"], e["kind"]) for e in mg.edges
            if _realisable_with(e, crate_of, pairs)
            and not _realisable_with(e, crate_of, base_pairs)],
        sc_fail=[c for c, _t, o, _b in security_checks(mg) if o],
    )


def resolution_analysis(ctx):
    """Apply each `RESOLUTIONS` mutation and measure what actually changes.

    Nothing here is quoted from prose: every cell of `dep/05` §7 is recomputed
    from the mutated graphs, so an option cannot claim an effect it does not
    have. Returns (baseline_metrics, {finding: {"question", "options"}}).
    """
    mg, cg, crate_of = ctx["module"], ctx["crate"], ctx["crate_of"]
    base_pairs = crate_edge_pairs()
    baseline = graph_metrics(mg, cg, crate_of, base_pairs)
    out = {}
    for fid, spec in E.RESOLUTIONS.items():
        rows = []
        for opt in spec["options"]:
            ch = opt["change"]
            extra = ch.get("add_crate_edges", [])
            rekind = ch.get("rekind", {})
            drop = {tuple(x) for x in ch.get("drop_module_edges", [])}
            pairs = base_pairs | {(p, c) for p, c, _k in extra}
            cg2 = Graph("crate+option", cg.nodes, cg.edges + [
                dict(provider=p, consumer=c, kind=k, visibility="OPTION", basis="")
                for p, c, k in extra])
            edges = []
            for e in mg.edges:
                key = (e["provider"], e["consumer"])
                if key in drop:
                    continue
                e2 = dict(e)
                if key in rekind:
                    e2["kind"] = rekind[key]
                edges.append(e2)
            rows.append((opt, graph_metrics(Graph("module+option", mg.nodes, edges),
                                            cg2, crate_of, pairs, base_pairs)))
        out[fid] = dict(question=spec["question"], options=rows)
    return baseline, out


def gen_violations(ctx):
    L = []
    A = L.append
    A("# dep/05 — Independence Violations, Hidden Dependencies, Invalid Directions\n")
    A(HEADER + "\n")

    A("## 1. Architectural constraints, checked\n")
    A("### 1.1 `ror-reference` independence\n")
    A("Constraint: `ror-reference` MUST NOT depend on the production evaluator, "
      "kernel, scheduler, persistence, serializer, recovery, or host "
      "implementation (`Red-on-Rust.md` L39645-39651 §10, L39807-39828 §14; "
      "R-REF-02, R-SCOPE-04).\n")
    A("| Check | Result | Offenders |")
    A("|---|---|---|")
    for cid, text, offenders, basis in ctx["ref_checks"]:
        A(f"| {cid} {text} | {'**PASS**' if not offenders else '**FAIL**'} | "
          + (", ".join(f"`{edge_line(o)}`" if isinstance(o, dict) else
                       (f"`{o[0]} ↛ {o[1]}`" if isinstance(o, tuple) else str(o))
                       for o in offenders) or "—") + " |")
    A("")
    mirror = [e for e in ctx["module"].edges
              if e["consumer"] == "MOD-14" and e["provider"] in E.PRODUCTION_NODES]
    A(f"The reference model *does* depend on {len(mirror)} production modules "
      f"({', '.join(e['provider'] for e in sorted(mirror, key=lambda e: e['provider']))}) — "
      "but every one of those edges is `SEMANTIC_DEPENDENCY` (rule "
      "R3-reference-mirror), "
      "which is what `mod/14-reference.md` declares: 'MOD-01…MOD-12 as "
      "*specification* dependencies; no implementation dependencies on any "
      "production module'. The constraint is therefore about kind, not about "
      "reachability, and the typed graph is what makes it checkable.\n")
    A("### 1.2 Security dependencies point at the authoritative boundary\n")
    A("| Check | Result | Offenders |")
    A("|---|---|---|")
    for cid, text, offenders, basis in ctx["sec_checks"]:
        A(f"| {cid} {text} | {'**PASS**' if not offenders else '**FAIL**'} | "
          + (", ".join(f"`{edge_line(o)}` [{o['kind']}]" for o in offenders) or "—")
          + " |")
    A("")
    A("Authoritative boundary (providers permitted on a `SECURITY_DEPENDENCY`), "
      "from the R-TRUST-01 trust table:\n")
    for m, why in sorted(E.AUTHORITY.items()):
        A(f"- `{m}` {O.DOMAIN[m]} — {why}")
    A("")
    A("Not authoritative (may never provide a security edge):\n")
    for m, why in sorted(E.NON_AUTHORITY.items()):
        A(f"- `{m}` {O.DOMAIN.get(m, '')} — {why}")
    A("")
    A("### 1.3 LLM/planner is never a security authority\n")
    planner_sec = [e for e in ctx["module"].edges
                   if e["provider"] in E.PLANNER_NODES
                   and e["kind"] == "SECURITY_DEPENDENCY"]
    A(f"Edges whose provider is `{', '.join(sorted(E.PLANNER_NODES))}` and whose "
      f"kind is `SECURITY_DEPENDENCY`: **{len(planner_sec)}**\n")
    for e in planner_sec:
        A(f"- `{edge_line(e)}` [{e['visibility']}] — {e['basis']}")
    A("")
    A("This is finding **V-03** below: the planner appears as the *provider* of a "
      "security property because the trust-model obligations cite the planner "
      "prohibitions. The prohibitions are real and the enforcement is correctly "
      "placed at the machine boundary (`spec/07` §3), but as recorded the graph "
      "makes `ror-agent` a security dependency of `R-TRUST-01`.\n")

    A("### 1.4 The frozen prohibitions are not tracked anywhere\n")
    hits = forbidden_block_citations()
    A(f"A repository-wide search of `req/*.md`, `spec/*.md` and `mod/*.md` for the "
      f"line numbers of `Red-on-Rust.md` §13 (L39757-39790) and §14 "
      f"(L39807-39828) returns **{len(hits)} citations**"
      + (" — no document tracks the block." if not hits else
         ": " + ", ".join(f"`{f}` L{ln}" for f, ln in hits) + ".")
      + " The only tracked statement of any part of it is REQ-REPO-014 "
      "(`ror-reference` … no production dependencies), whose SOURCE range "
      "L39196-40762 swallows the block without stating it. See V-02 / HD-5.\n")
    A("### 1.5 Where the authority set comes from\n")
    frozen_a, inferred_a, partial_a, unlisted, runs = authority_provenance()
    latest = runs[-1] if runs else []
    _src, rd, drift = readme_trust_drift()
    A("`Red-on-Rust.md` states the component trust table "
      + ("**twice**" if len(runs) == 2 else f"**{len(runs)} times**") + ": "
      + ", ".join(f"L{r[0][0]}-{r[-1][0]} ({len(r)} rows)" for r in runs)
      + ". The later one governs (`spec/00` §2 supersession) and adds a "
        "`Persistence | Yes | Durable machine state` row the earlier one lacks. "
        f"`README.md` renders the same table and matches it on all "
      f"{len(rd)} rows" + ("" if not drift else
                           f" except {', '.join(d[0] for d in drift)}")
      + ". Checked against it, "
      f"**{len(frozen_a)} of the {len(E.AUTHORITY)} authoritative modules are "
      f"frozen by a `Yes` row** ({', '.join(frozen_a)}), "
      f"**{len(inferred_a)} are inferred** ({', '.join(inferred_a)}) because the "
      "table names no marshalling boundary, no effect boundary and no serializer "
      "— their authority rests on R-MARSHAL-01/02, R-EFFECT-03 and R-CANON-01/04. "
      "`MOD-09` is `Yes` only as the *replay* host; `Live host` is `Partial`. "
      f"One table row claims no module: "
      f"{', '.join(unlisted) or 'none'} (untrusted input data, not a component). "
      "No `SECURITY_DEPENDENCY` currently has an inferred module as provider, so "
      "SC-1's PASS does not depend on the gap — see V-11.\n")
    A("---\n\n## 2. Findings\n")
    prose_only = sorted(set(ctx["prose_pairs"]) - set(ctx["mdeps"]))
    table_only = sorted(set(ctx["mdeps"]) - set(ctx["prose_pairs"]))
    for vid, f in sorted(E.FINDINGS.items()):
        A(f"### {vid} — {f['title']}\n")
        A(f"- **severity:** {f['severity']}")
        A(f"- **constraint:** {f['constraint']}")
        A(f"- {f['body']}")
        if vid == "V-07":
            A(f"- **measured:** the module files' DEPENDENCIES prose declares "
              f"{len(ctx['prose_pairs'])} module pairs, `MODULE_DEPS` declares "
              f"{len(ctx['mdeps'])}, and they disagree both ways — "
              f"**{len(prose_only)} prose-only** "
              f"({', '.join(f'`{a} -> {b}`' for a, b in prose_only[:6])}, …) and "
              f"**{len(table_only)} table-only** "
              f"({', '.join(f'`{a} -> {b}`' for a, b in table_only[:6])}"
              f"{', …' if len(table_only) > 6 else ''}). The `dep/` module layer "
              "takes the union, so both sets appear there and are typed. "
              "`mod/_build.py` checks only `MODULE_DEPS`, so it verifies none of "
              f"the {len(prose_only)} prose-only pairs; conversely the "
              f"{len(table_only)} table-only pairs are checked but declared in no "
              "module file, so a reader of `mod/` will not find them.")
        A(f"- **decision required:** {f['decision']}")
        A("")

    A("---\n\n## 3. Hidden dependencies\n")
    A("A dependency is *hidden* when it is real in the specification but invisible "
      "in the graph an implementer would read (`spec/07` §6 crate list, "
      "`mod/18` §0 module table, `spec/10-index.json`).\n")
    for hid, title, why, items in ctx["hidden"]:
        n = len(items) if not isinstance(items, dict) else sum(len(v) for v in items.values())
        A(f"### {hid} — {title} ({n})\n")
        A(why + "\n")
        if isinstance(items, dict):
            A("| Crate | Hidden couplings |")
            A("|---|---|")
            for k, v in items.items():
                A(f"| `{k}` | " + ", ".join(f"`{a} -> {b}`" for a, b in v) + " |")
        elif items and isinstance(items[0], tuple):
            A("| Item | Detail |")
            A("|---|---|")
            for it in items:
                if len(it) == 2:
                    A(f"| `{it[0]} -> {it[1]}` | {ctx['pair_kind'].get((it[0], it[1]), '')} |")
                elif len(it) == 3:
                    A(f"| `{it[0]}` | {it[1]} — {it[2]} |")
                elif it[2] == "FORBIDDEN":
                    A(f"| `{it[0]}` ↛ `{it[1]}` | {it[3]} |")
                else:
                    A(f"| `{it[0]} -> {it[1]}` | {it[2]} — {it[3]} |")
        A("")
    A("---\n\n## 4. Invalid dependency directions\n")
    A("| ID | Check | Result | Note |")
    A("|---|---|---|---|")
    for did, text, result, note in ctx["direction"]:
        if isinstance(result, list):
            parts = []
            for it in result:
                if len(it) == 2:
                    a, b = it
                    parts.append(f"`{a} -> {b}`" if not str(b).startswith("L")
                                 else f"`{a}`/`{b}`")
                else:
                    parts.append(f"`{it[0]} -> {it[1]}` ({it[2]})")
            res = ", ".join(parts) or "none"
        else:
            res = str(result)
        A(f"| {did} | {text} | {res} | {note} |")
    A("")
    gap = ctx["direction"][-1][2]
    if gap:
        A("### 4.1 ID-6 in detail — `crate`-labelled module edges no crate list "
          "carries\n")
        A("| `A -> B` (B depends on A) | Implied crate edge | `MODULE_DEPS` note |")
        A("|---|---|---|")
        for prov, dep, implied, why in gap:
            A(f"| `{label(prov)} -> {label(dep)}` | `{implied}` | {why} |")
        A("")
    A("The direction question that matters is **ID-3/V-04**: `Red-on-Rust.md` "
      "L39762-39790 §13 is titled 'Dependency Graph' but its arrows are pipeline "
      "arrows. Read as dependencies it asserts `ror-persistence` depends on "
      "`ror-runtime`, which contradicts the request sequence (`spec/07` §3: "
      "`ror-persistence` append+sync is *called from* `ror-runtime`) and would "
      "make the durable layer depend on the machine it has to survive.\n")

    A("---\n\n## 5. Requirements referenced before definition\n")
    fr = ctx["fwd_req"]
    A(f"{len(fr)} of {len(ctx['req'].edges)} requirement edges "
      f"({100*len(fr)/len(ctx['req'].edges):.1f}%) cite a record whose first "
      "`Red-on-Rust.md` anchor is later than the citing record's. Section level: "
      f"{len(ctx['fwd_sec'])} backward edges. Neither is a defect in a transcript-"
      "derived specification, but both are reading-order hazards; the 15 largest "
      "gaps are tabulated in `dep/01` §3.4.\n")
    A("---\n\n## 6. What is *not* violated\n")
    A("- No circular crate dependency: the crate layer is a DAG "
      f"({len(ctx['crate'].sccs())} trivial SCCs).")
    A("- None of the ten frozen forbidden crate edges is present (RI-1).")
    A("- No MOD-14 dependency has an implementable kind (RI-2), and no production "
      "module takes an implementable dependency on the reference model (RI-3).")
    A("- No production module depends implementably on a verification node (RI-4).")
    A("- Every `SECURITY_DEPENDENCY` except the planner case of V-03 has an "
      "authoritative-boundary provider (SC-1).")
    A("")

    A("---\n\n## 7. What each blocking finding needs, and what each answer "
      "costs\n")
    baseline, resolutions = resolution_analysis(ctx)

    def delta(v, base):
        return f"{v}" if v == base else f"{v} ({v - base:+d})"

    A("V-01, V-03 and V-04 are the three findings that leave the module layer "
      "with no partial order at all (`dep/02` §2.2). Each option below is a "
      "mutation of the graph **as recorded** — a crate edge added to `spec/07` "
      "§6, a module edge re-recorded with another kind, or a prose declaration "
      "withdrawn. **None of them is applied, and none is a recommendation**: the "
      "decision belongs to the specification owner. What this layer contributes "
      "is the price of each answer, recomputed from the mutated graph rather "
      "than estimated. Deltas are against the graph as recorded.\n")
    A(f"**As recorded:** crate layer "
      f"{'acyclic' if baseline['acyclic'] else '**CYCLIC**'}; "
      f"{baseline['impl_edges']} of {baseline['module_edges']} module edges have "
      f"a crate realisation (the implementation graph of `dep/02` §2.1), with "
      f"{baseline['impl_sccs']} non-trivial SCCs; HD-1 = {baseline['hd1']}; "
      f"{baseline['mutual_full']} mutual pairs, {baseline['mutual_impl']} of them "
      f"inside that implementation graph; security failures "
      f"{', '.join(baseline['sc_fail']) or 'none'}.\n")
    for i, fid in enumerate(("V-01", "V-03", "V-04", "V-10"), 1):
        spec = resolutions[fid]
        A(f"### 7.{i} {fid} — {E.FINDINGS[fid]['title']}\n")
        A(f"*{spec['question']}*\n")
        A("| Option | Crate DAG | Impl graph (edges a crate edge can carry) | "
          "Impl SCCs | HD-1 | Mutual pairs (full / impl) | SC failures |")
        A("|---|---|---|---|---|---|---|")
        for opt, m in spec["options"]:
            A(f"| **{opt['id']}** {opt['label']} | "
              f"{'acyclic' if m['acyclic'] else '**CYCLIC**'} | "
              f"{delta(m['impl_edges'], baseline['impl_edges'])} of "
              f"{m['module_edges']} | "
              f"{delta(m['impl_sccs'], baseline['impl_sccs'])} | "
              f"{delta(m['hd1'], baseline['hd1'])} | "
              f"{delta(m['mutual_full'], baseline['mutual_full'])} / "
              f"{delta(m['mutual_impl'], baseline['mutual_impl'])} | "
              f"{', '.join(m['sc_fail']) or 'none'} |")
        A("")
        for opt, m in spec["options"]:
            A(f"- **{opt['id']}** — {opt['note']}")
            if m["carries"]:
                A("  - *Module edges that gain a crate realisation:* "
                  + ", ".join(f"`{p} -> {c}` ({k.replace('_DEPENDENCY', '')})"
                              for p, c, k in m["carries"]) + ".")
            base_order = baseline["build_order"]
            if (m["acyclic"] and len(m["build_order"]) == len(base_order)
                    and m["build_order"] != base_order):
                moved = [(n, base_order.index(n) + 1, m["build_order"].index(n) + 1)
                         for n in m["build_order"]
                         if base_order.index(n) != m["build_order"].index(n)]
                A(f"  - *Build order:* " + ", ".join(
                    f"`{n}` {a} → {b}" for n, a, b in moved)
                    + f". Full order becomes: {', '.join(m['build_order'])}.")
        A("")
    unpriced = [f for f in sorted(E.FINDINGS) if f not in E.RESOLUTIONS]
    A("### 7.5 What is not priced here\n")
    A(f"{len(unpriced)} of the {len(E.FINDINGS)} findings have no options above: "
      + ", ".join(f"`{f}`" for f in unpriced)
      + ". Most are tracking or provenance fixes — an untracked prohibition list, "
      "an index that disagrees with `spec/07` §6, a mis-cited line — where the "
      "graph looks the same whichever way they go, so there is nothing to "
      "measure. `V-09` is the exception, and the omission is deliberate: it *is* "
      "a graph decision, but its resolution splits `MOD-04` into a `ror-core` "
      "algebra part and a `ror-runtime` gate part, which changes the node set "
      "rather than the edges. This table models mutations of edges only; pricing "
      "V-09 would mean inventing an 18-module graph that the rest of this "
      "document set does not describe.\n")
    return "\n".join(L) + "\n"


def gen_index(ctx):
    ig = ctx["impl"]
    kf = ctx["module"].sub(E.IMPLEMENTABLE_KINDS)
    mg, cg, rg, sg = ctx["module"], ctx["crate"], ctx["req"], ctx["section"]
    return {
        "convention": "A -> B means B depends on A (provider -> consumer); matches spec/04, opposite of mod/18",
        "kinds": list(E.KINDS),
        "kind_definitions": {
            k: {"meaning": E.KIND_DEF[k][0],
                "provider_constraint": E.KIND_PROVIDER_CHECK[k][0],
                "provider_constraint_machine_checked":
                    E.KIND_PROVIDER_CHECK[k][1] is not None,
                "implementable": E.KIND_DEF[k][1]}
            for k in E.KINDS
        },
        "implementable_kinds": list(E.IMPLEMENTABLE_KINDS),
        "layers": {
            "crate": {
                "nodes": [n for n, _r in E.CRATE_NODES],
                "edges": [{k: v for k, v in e.items()} for e in cg.edges],
                "forbidden_edges": [{"dependent": d, "dependency": p, "source": ev,
                                     "present": (d, p) in {(e["consumer"], e["provider"]) for e in cg.edges}}
                                    for d, p, ev in E.FORBIDDEN_CRATE_EDGES],
                "missing_required_edges": [{"provider": p, "consumer": c, "kind": k, "why": w}
                                           for p, c, k, w in E.CRATE_MISSING_EDGES],
                "diagram_edges_L39762_39790": [{"provider": p, "consumer": c}
                                               for p, c in E.CRATE_DIAGRAM_EDGES],
                "roots": cg.roots, "leaves": cg.leaves,
                "topological_order": cg.toposort()[0],
                "non_trivial_sccs": [c for c in cg.sccs() if len(c) > 1],
            },
            "module": {
                "nodes": [{"id": n, "domain": O.DOMAIN[n], "crate": ctx["crate_of"][n]}
                          for n in mg.nodes],
                "edges": [{k: v for k, v in e.items()} for e in mg.edges],
                "roots": mg.roots, "leaves": mg.leaves,
                "non_trivial_sccs": [c for c in mg.sccs() if len(c) > 1],
                "levels_full_graph": {str(k): v for k, v in mg.levels().items()},
                # The implementation graph = edges a frozen crate edge can carry
                # (same crate, or an edge of `spec/07` S6).  This is what
                # `dep/01` S2.8, `dep/02` S2.1 and `dep/03` S2.1 report.
                "implementation": {
                    "definition": "crate_of[provider] == crate_of[consumer], or "
                                  "(crate_of[provider], crate_of[consumer]) is a "
                                  "frozen crate edge of spec/07 S6",
                    "edge_count": len(ig.edges),
                    "edges": [{k: v for k, v in e.items()} for e in ig.edges],
                    "roots": ig.roots,
                    "leaves": ig.leaves,
                    "topological_order": ig.toposort()[0],
                    "not_orderable": ig.toposort()[1],
                    "levels": {str(k): v for k, v in ig.levels().items()},
                    "cycles": [sorted(c) for c in ig.sccs() if len(c) > 1],
                },
                # Kind-filtered subgraph, kept for reference only: filtering by
                # IMPLEMENTABLE_KINDS is NOT the implementability test -- it
                # leaves 149 elementary circuits of length 2..5 (9/15/38/87),
                # which is why `dep/03` S2.1 uses crate realisability instead.
                "kind_filtered_subgraph": {
                    "kinds": sorted(E.IMPLEMENTABLE_KINDS),
                    "edge_count": len(kf.edges),
                    "roots": kf.roots,
                    "leaves": kf.leaves,
                    "cycles": [sorted(c) for c in kf.sccs() if len(c) > 1],
                    "elementary_circuits_len_2_to_5": len(elementary_circuits(kf)),
                },
            },
            "requirement": {
                "node_count": len(rg.nodes),
                "edges": [{"provider": e["provider"], "consumer": e["consumer"],
                           "kind": e["kind"]} for e in rg.edges],
                "roots": rg.roots,
                "leaves": rg.leaves,
                "scc_count": len(rg.sccs()),
                "non_trivial_sccs": [c for c in rg.sccs() if len(c) > 1],
                "forward_reference_count": len(ctx["fwd_req"]),
                "forward_references_largest": [
                    {"citing": a, "citing_line": la, "target": b, "target_line": lb}
                    for a, b, la, lb in ctx["fwd_req"][:50]],
            },
            "section": {
                "nodes": sg.nodes,
                "edges": [{"provider": e["provider"], "consumer": e["consumer"],
                           "kind": e["kind"]} for e in sg.edges],
                "roots": sg.roots, "leaves": sg.leaves,
                "topological_order": sg.toposort()[0],
                "backward_edges": [{"consumer": c, "provider": p} for c, p in ctx["fwd_sec"]],
                "non_trivial_sccs": [c for c in sg.sccs() if len(c) > 1],
            },
        },
        "authority": E.AUTHORITY,
        "non_authority": E.NON_AUTHORITY,
        "checks": {
            "reference_independence": [
                {"id": c, "check": t, "pass": not o,
                 "offenders": [edge_line(x) if isinstance(x, dict) else list(x) for x in o]}
                for c, t, o, _b in ctx["ref_checks"]],
            "security_direction": [
                {"id": c, "check": t, "pass": not o, "offenders": [edge_line(x) for x in o]}
                for c, t, o, _b in ctx["sec_checks"]],
            "direction": [{"id": d, "check": t,
                           "result": (r if isinstance(r, str) else [list(x) for x in r]),
                           "note": n} for d, t, r, n in ctx["direction"]],
        },
        "hidden_dependencies": [
            {"id": h, "title": t, "why": w,
             "items": ({k: [list(x) for x in v] for k, v in items.items()}
                       if isinstance(items, dict) else [list(x) for x in items])}
            for h, t, w, items in ctx["hidden"]],
        "findings": {k: v for k, v in sorted(E.FINDINGS.items())},
    }


# --------------------------------------------------------------------------
CITE_MOD = re.compile(r"`(MOD-\d\d)(?: [A-Z]+)? -> (MOD-\d\d)(?: [A-Z]+)?`")
CITE_CRATE = re.compile(r"`(ror-[a-z]+) -> (ror-[a-z]+)`")
CITE_SEC = re.compile(r"`(S-\d\d) -> (S-\d\d)`")

# A citation immediately preceded by one of these is a quotation of that
# document's own notation (spec/07 §6 and mod/18 both write dependent ->
# dependency), not an assertion in this document set's convention.
CITE_ATTRIBUTION = ("spec/07", "spec/10-index.json", "mod/18", "mod/19")

# Citations that are correct but read as an inversion: they assert that a
# direction is ABSENT, which is exactly the reverse of a frozen edge.
CITE_ALLOWLIST = {
    ("ror-agent", "ror-core"):
        "V-03 asserts this direction does not exist; the frozen edge is the "
        "reverse (`ror-core -> ror-agent`)",
}


DOT_RESERVED = {"node", "edge", "graph", "subgraph", "digraph", "strict"}


def dot_validation(ctx, docs):
    """Parse the two generated ```dot blocks and compare them with their graphs.

    Returns `(errors, status)`. `status` is the one-line summary, or None when
    `pydot` is not importable — the blocks then have only had the regex
    validation, and the summary says so rather than passing silently.

    `pydot` reports the `node […]` / `edge […]` default-attribute statements as
    pseudo-nodes, so those reserved names are dropped before the node sets are
    compared. Edge labels in the crate block abbreviate the kind
    (`TYPE` for `TYPE_DEPENDENCY`); the module block carries no labels, so only
    the endpoint pairs are compared there.
    """
    try:
        import pydot
    except ImportError:
        return [], None
    blocks = re.findall(r"```dot\n(.*?)```", docs[DEP / "01-graph.md"], re.S)
    if len(blocks) != 2:
        return [f"01-graph.md has {len(blocks)} ```dot blocks, expected 2"], None
    errs, notes = [], []
    for block, (name, g, labelled) in zip(blocks, (("ror_crates", ctx["crate"], True),
                                                  ("ror_modules", ctx["module"], False))):
        parsed = pydot.graph_from_dot_data(block)
        if not parsed:
            errs.append(f"pydot could not parse the {name} ```dot block")
            continue
        p = parsed[0]
        if p.get_name() != name:
            errs.append(f"```dot block is named `{p.get_name()}`, expected `{name}`")
        nodes = {n.get_name().strip('"') for n in p.get_nodes()} - DOT_RESERVED
        if nodes != set(g.nodes):
            errs.append(f"{name}: parsed nodes {sorted(nodes)} != graph nodes "
                        f"{sorted(g.nodes)}")
        got = collections.Counter((e.get_source().strip('"'), e.get_destination().strip('"'))
                                  for e in p.get_edges())
        want = collections.Counter((e["provider"], e["consumer"]) for e in g.edges)
        for pair in sorted(set(want) - set(got)):
            errs.append(f"{name}: `{pair[0]} -> {pair[1]}` is a graph edge but is "
                        "missing from the ```dot block")
        for pair in sorted(set(got) - set(want)):
            errs.append(f"{name}: the ```dot block draws `{pair[0]} -> {pair[1]}`, "
                        "which is not a graph edge")
        if got and want and set(got) == set(want) and got != want:
            errs.append(f"{name}: the ```dot block draws a different number of "
                        f"edges than the graph has ({sum(got.values())} vs "
                        f"{sum(want.values())})")
        if labelled:
            gotlab = collections.Counter(
                (e.get_source().strip('"'), e.get_destination().strip('"'),
                 (e.get_label() or "").strip('"')) for e in p.get_edges())
            wantlab = collections.Counter(
                (e["provider"], e["consumer"], e["kind"].replace("_DEPENDENCY", ""))
                for e in g.edges)
            if gotlab != wantlab:
                for k in sorted(set(wantlab) - set(gotlab)):
                    errs.append(f"{name}: edge `{k[0]} -> {k[1]}` should be labelled "
                                f"`{k[2]}` in the ```dot block")
                for k in sorted(set(gotlab) - set(wantlab)):
                    errs.append(f"{name}: the ```dot block labels `{k[0]} -> {k[1]}` "
                                f"`{k[2]}`, but the graph says otherwise")
        notes.append(f"{name} {sum(got.values())} edges")
    return errs, ("pydot " + getattr(pydot, "__version__", "?") + " parsed "
                  + "; ".join(notes))


def citation_inversions(ctx, docs):
    """Scan the generated prose for edge citations that point the wrong way.

    A citation `A -> B` is suspect when `A -> B` is *not* an edge of the relevant
    layer but `B -> A` is: that is the signature of an arrow written in the
    `mod/18` convention inside a document that states the `spec/04` one (V-06).
    Citing an edge that exists in neither direction is allowed — findings discuss
    forbidden and absent edges on purpose — and for the crate layer only a
    *frozen* reverse counts, so HD-1's "would need crate edge X (absent)" rows
    are not false positives.
    """
    mod_edges = {(e["provider"], e["consumer"]) for e in ctx["module"].edges}
    sec_edges = {(e["provider"], e["consumer"]) for e in ctx["section"].edges}
    frozen = {(p, c) for p, c, _k, _e in E.CRATE_EDGES}
    known_crate = frozen | {(p, c) for p, c, _k, _w in E.CRATE_MISSING_EDGES} \
        | {(p, c) for p, c in E.CRATE_DIAGRAM_EDGES} \
        | {(c, p) for p, c, _e in E.FORBIDDEN_CRATE_EDGES}
    suspects = []
    for path, body in sorted(docs.items()):
        for rx, edges, reverse_only, layer in (
                (CITE_MOD, mod_edges, mod_edges, "module"),
                (CITE_CRATE, known_crate, frozen, "crate"),
                (CITE_SEC, sec_edges, sec_edges, "section")):
            for m in rx.finditer(body):
                a, b = m.group(1), m.group(2)
                if a == b or (a, b) in edges:
                    continue
                if (b, a) not in reverse_only:
                    continue
                # quoting another document's notation is not an assertion of ours
                before = body[max(0, m.start() - 40):m.start()]
                if any(src in before for src in CITE_ATTRIBUTION):
                    continue
                if (a, b) in CITE_ALLOWLIST:
                    continue
                suspects.append((Path(path).name, layer, a, b))
    return suspects


def main():
    write = "--write" in sys.argv
    records = load_records()
    owner = req_owner(records)
    if len(records) != 545:
        err(f"expected 545 records, found {len(records)}")
    if len(owner) != len(records):
        err("requirement ownership incomplete")

    prose_pairs, prose_bodies = parse_prose_deps()
    mdeps = moduledges_flipped()
    witnesses = collections.defaultdict(list)
    for r in records:
        for dep in req_dependencies(r):
            if dep in owner and owner[dep] != owner[r["REQ-ID"]]:
                witnesses[(owner[dep], owner[r["REQ-ID"]])].append((dep, r["REQ-ID"]))

    mod_graph = build_module_graph(prose_pairs, mdeps, witnesses)
    crate_graph = build_crate_graph()
    index = json.loads((ROOT / "spec/10-index.json").read_text())
    section_graph = build_section_graph(index)
    req_graph, by = build_req_graph(records, owner)

    crate_of = crate_of_module()
    impl_graph = Graph("module-implementation", mod_graph.nodes,
                       [e for e in mod_graph.edges if realisable(e, crate_of)])

    # ---- checks -------------------------------------------------------
    # 2. MODULE_DEPS coverage
    mod_pairs = {(e["provider"], e["consumer"]) for e in mod_graph.edges}
    for pair in mdeps:
        if pair not in mod_pairs:
            err(f"MODULE_DEPS edge {pair[0]} -> {pair[1]} missing from the module layer")
    # 3. prose coverage + justification
    for pair in prose_pairs:
        if pair not in mod_pairs:
            err(f"prose edge {pair[0]} -> {pair[1]} missing from the module layer")
    for e in mod_graph.edges:
        pair = (e["provider"], e["consumer"])
        if pair not in mdeps and pair not in prose_pairs and pair not in witnesses:
            err(f"module edge {pair[0]} -> {pair[1]} has no justification")
        if e["visibility"] == "none":
            err(f"module edge {pair[0]} -> {pair[1]} has no visibility marker")
    # 0. node-set definitions must agree with the crate roles
    roles = dict(E.CRATE_NODES)
    for mod, crate in crate_of_module().items():
        role = roles.get(crate)
        if role == "production" and mod not in E.PRODUCTION_NODES:
            err(f"{mod} lives in production crate {crate} but is not in "
                "PRODUCTION_NODES — its edges would be invisible to HD-1")
        if role == "production" and mod in E.VERIFICATION_NODES:
            err(f"{mod} is in VERIFICATION_NODES but lives in {crate}")
        if role == "verification" and mod in E.PRODUCTION_NODES:
            err(f"{mod} is in PRODUCTION_NODES but lives in {crate}")
    # 1. generic edge sanity
    for g in (crate_graph, mod_graph, section_graph, req_graph):
        for e in g.edges:
            if e["provider"] == e["consumer"]:
                err(f"{g.name}: self-edge {e['provider']}")
            if e["kind"] not in E.KINDS:
                err(f"{g.name}: {edge_line(e)} unknown kind {e['kind']}")
            if e["provider"] not in g.nodes or e["consumer"] not in g.nodes:
                err(f"{g.name}: {edge_line(e)} unknown endpoint")
    # 11. the provider constraint that `dep/00` §2 and `dep/01` §2.x print for
    # each kind must hold for every module edge of that kind.  Stated over MOD-NN
    # names, so it is the module layer that is checked.
    for kind in E.KINDS:
        if kind not in E.KIND_PROVIDER_CHECK:
            err(f"{kind} has no entry in KIND_PROVIDER_CHECK — its rendered "
                "provider constraint would be unchecked")
        elif E.KIND_PROVIDER_CHECK[kind][1] is None and kind != "SEMANTIC_DEPENDENCY":
            err(f"{kind} is marked not machine-checkable; SEMANTIC_DEPENDENCY is "
                "the only kind allowed to be")
    for e in mod_graph.edges:
        desc, pred = E.KIND_PROVIDER_CHECK[e["kind"]]
        if pred is not None and not pred(e["provider"], e["consumer"]):
            err(f"{edge_line(e)} breaks its kind's provider constraint: {desc}")
    # 13. every RESOLUTIONS option must be a well-formed mutation of the graph as
    # recorded, and none may add an edge §14 forbids.
    crate_names = {n for n, _r in E.CRATE_NODES}
    forbidden = {(d, p) for d, p, _ev in E.FORBIDDEN_CRATE_EDGES}  # (dependent, dependency)
    for fid, spec in E.RESOLUTIONS.items():
        if fid not in E.FINDINGS:
            err(f"RESOLUTIONS offers options for {fid}, which is not a finding")
        for opt in spec["options"]:
            for p, c, k in opt["change"].get("add_crate_edges", []):
                if p not in crate_names or c not in crate_names:
                    err(f"{opt['id']}: `{p} -> {c}` is not a crate pair")
                if k not in E.KINDS:
                    err(f"{opt['id']}: unknown kind {k}")
                if (c, p) in forbidden:
                    err(f"{opt['id']}: `{p} -> {c}` would make {c} depend on "
                        f"{p}, which §14 forbids")
            for (p, c), k in opt["change"].get("rekind", {}).items():
                if (p, c) not in mod_pairs:
                    err(f"{opt['id']}: rekind target `{p} -> {c}` is not a "
                        "module edge")
                if k not in E.KINDS:
                    err(f"{opt['id']}: unknown kind {k}")
            for pair in opt["change"].get("drop_module_edges", []):
                if tuple(pair) not in mod_pairs:
                    err(f"{opt['id']}: drop target `{pair[0]} -> {pair[1]}` is "
                        "not a module edge")
    # the §7 baseline must be the very graph `dep/02` §2.1 and `dep/03` §2.1
    # print, or the what-if table silently uses a different implementation graph.
    base_m = graph_metrics(mod_graph, crate_graph, crate_of, crate_edge_pairs())
    if base_m["impl_edges"] != len(impl_graph.edges):
        err(f"`dep/05` §7 baseline implementation graph has {base_m['impl_edges']} "
            f"edges; `dep/02` §2.1 prints {len(impl_graph.edges)}")
    if base_m["impl_sccs"] != len([c for c in impl_graph.sccs() if len(c) > 1]):
        err(f"`dep/05` §7 baseline counts {base_m['impl_sccs']} non-trivial "
            f"implementation SCCs; `dep/03` §2.1 prints "
            f"{len([c for c in impl_graph.sccs() if len(c) > 1])}")
    if base_m["mutual_full"] != len(mutual_pairs(mod_graph)):
        err("`dep/05` §7 baseline mutual-pair count disagrees with `dep/03` §2.2")
    # 7. acyclicity where required
    if any(len(c) > 1 for c in crate_graph.sccs()):
        err("crate graph is not acyclic")
    aug = crate_graph_augmented(crate_graph)
    for comp in aug.sccs():
        if len(comp) > 1:
            err(f"crate graph + the §1.2 missing edges is cyclic: {sorted(comp)}")
    for e in aug.edges:
        for d, pn, _ev in E.FORBIDDEN_CRATE_EDGES:
            if e["consumer"] == d and e["provider"] == pn:
                err(f"crate edge {edge_line(e)} is forbidden by §14")
    for comp in impl_graph.sccs():
        if len(comp) > 1 and cycle_family(frozenset(comp))[0] is None:
            err(f"implementation SCC {sorted(comp)} matches no cycle family")
    for fs in mutual_pairs(mod_graph):
        if cycle_family(fs)[0] is None:
            err(f"mutual pair {sorted(fs)} matches no cycle family")

    hidden = hidden_dependencies(mod_graph, prose_pairs, mdeps, witnesses, index,
                                 crate_of)
    sec_checks = security_checks(mod_graph)
    ref_checks = reference_checks(mod_graph, crate_graph)
    direction, spec07 = direction_checks()
    if readme_trust_drift()[2]:
        err("`README.md` trust table drifted from `Red-on-Rust.md`: "
            + "; ".join(f"{c}: source {a} vs README {b}" for c, a, b
                        in readme_trust_drift()[2]))
    if forbidden_block_citations():
        err("V-02/HD-5 claim is stale: a document now cites the frozen "
            "dependency-direction block")
    fwd_req = forward_refs_req(req_graph, by)
    fwd_sec = forward_refs_section(section_graph)
    pair_kind = {(e["provider"], e["consumer"]): e["kind"] for e in mod_graph.edges}

    ctx = dict(prose_pairs=prose_pairs, mdeps=mdeps,
               crate=crate_graph, module=mod_graph, req=req_graph, section=section_graph,
               impl=impl_graph, crate_edges=crate_edge_pairs(),
               owner=owner, index=index, crate_of=crate_of, hidden=hidden,
               sec_checks=sec_checks, ref_checks=ref_checks, direction=direction,
               fwd_req=fwd_req, fwd_sec=fwd_sec, pair_kind=pair_kind)

    docs = {
        DEP / "00-overview.md": gen_overview(ctx),
        DEP / "01-graph.md": gen_graph(ctx),
        DEP / "02-topological-order.md": gen_topo(ctx),
        DEP / "03-cycles.md": gen_cycles(ctx),
        DEP / "04-cross-section-table.md": gen_table(ctx),
        DEP / "05-violations.md": gen_violations(ctx),
        DEP / "10-graph.json": json.dumps(gen_index(ctx), indent=1, ensure_ascii=False) + "\n",
    }
    for fname, layer, a, b in citation_inversions(ctx, docs):
        err(f"{fname}: `{a} -> {b}` is not a {layer} edge but `{b} -> {a}` is — "
            "probable arrow-convention inversion (V-06)")
    dot_errs, dot_status = dot_validation(ctx, docs)
    for m in dot_errs:
        err(m)

    for path, content in docs.items():
        if write:
            path.write_text(content)
        else:
            if not path.exists():
                err(f"{path.name} missing; run `python3 dep/_graph.py --write`")
            elif path.read_text() != content:
                err(f"{path.name} is stale; run `python3 dep/_graph.py --write`")

    mg = mod_graph
    print(f"layers                  : crate={len(crate_graph.nodes)}/{len(crate_graph.edges)} "
          f"module={len(mg.nodes)}/{len(mg.edges)} "
          f"requirement={len(req_graph.nodes)}/{len(req_graph.edges)} "
          f"section={len(section_graph.nodes)}/{len(section_graph.edges)}")
    print(f"module edges by kind    : "
          f"{dict(collections.Counter(e['kind'] for e in mg.edges))}")
    print(f"module roots/leaves     : {mg.roots} / {mg.leaves}")
    print(f"module SCCs             : full {len(mg.sccs())} "
          f"(non-trivial {len([c for c in mg.sccs() if len(c) > 1])}); "
          f"implementation graph {len(impl_graph.edges)} edges, "
          f"{len([c for c in impl_graph.sccs() if len(c) > 1])} implementation cycles; "
          f"{len(mutual_pairs(mg))} mutual pairs")
    print(f"section SCCs            : {len(section_graph.sccs())} "
          f"(non-trivial {len([c for c in section_graph.sccs() if len(c) > 1])})")
    print(f"requirement SCCs        : {len(req_graph.sccs())} "
          f"(non-trivial {len([c for c in req_graph.sccs() if len(c) > 1])})")
    print(f"forward references      : requirement {len(fwd_req)}/{len(req_graph.edges)}, "
          f"section {len(fwd_sec)}/{len(section_graph.edges)}")
    print(f"hidden dependencies     : " + ", ".join(f"{h}={len(i) if not isinstance(i, dict) else sum(len(v) for v in i.values())}"
                                                   for h, _t, _w, i in hidden))
    failed = [c for c, _t, o, _b in sec_checks + ref_checks if o]
    print(f"independence checks     : "
          f"{len(sec_checks) + len(ref_checks) - len(failed)} pass, {len(failed)} fail"
          + (f" -> {[c for c, _t, o, _b in sec_checks + ref_checks if o]}" if failed else ""))
    print("DOT validation          : "
          + (dot_status or "SKIPPED — pydot not installed, the ```dot blocks had "
                           "only the regex validation"))
    if ERRORS:
        for e in ERRORS[:40]:
            print("  ERROR", e)
        if len(ERRORS) > 40:
            print(f"  … {len(ERRORS) - 40} more")
    print(f"ERRORS                  : {len(ERRORS)}")
    return 1 if ERRORS else 0


if __name__ == "__main__":
    sys.exit(main())
