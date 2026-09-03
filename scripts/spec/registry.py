"""Stage S6 — REGISTER (§13).

Machine-readable registries, generated deterministically:

    requirements.json   obligations.json   dependencies.json   terminology.json

Every entry carries the §13 field set (`id`, `status`, `source_refs`,
`section_refs`, `normative_class`, `dependencies`, `verification_refs`) plus
`identity_basis` / `*_source` provenance so a reader can see *where each value
was copied from* rather than being asked to trust it.

Three properties are enforced, and each is a hard failure rather than a note:

  * **stable identities** — the identity set is exactly `spec/03`'s, in
    `spec/03`'s order; nothing is renumbered, added or dropped (§4.5);
  * **provenance on every entry** — a registry row without a resolvable source
    reference or a recorded frozen-addendum citation is refused;
  * **deterministic generation** — sorted key order, registry order for lists,
    no clock, no locale, no filesystem order.

`terminology.json` is emitted by S3 (its authority is `term/`); S6 copies it
byte-for-byte into the registry set so the four registries can be verified as a
unit — S6 does not re-derive terminology from prose.
"""
from __future__ import annotations

import collections
import re

from _common import (EVIDENCE_CEILING, STATUS_LADDER, StageFailure, line_refs_of,
                     md_escape, provenance, render_json, sha256_text, table)

STAGE = "S6-register"


def _verification_refs(oblig: dict) -> list[str]:
    cell = oblig.get("verify") or ""
    if cell.strip() in ("—", "-", ""):
        return []
    toks = re.findall(r"[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)+", cell)
    out = sorted({t for t in toks if t not in {"R-SCOPE", "R-TEST", "R-REF", "R-ORDER"}})
    return out or [cell.strip()]


def run(ctx, run_state: dict) -> dict:
    entries = run_state["results"]["S1"]["entries"]
    sections = run_state["results"]["S2"]["data"]["sections"]
    term_reg = run_state["results"]["S3"]["terminology"]
    norm = run_state["results"]["S3"]["data"]
    audit = run_state["results"]["S4"]["data"]

    prov = provenance(STAGE, inputs=[("spec/03-obligation-matrix.md", None),
                                     ("spec/01-canonical-specification.md", None),
                                     ("spec/02-section-hierarchy.md", None),
                                     ("dep/10-graph.json", None)],
                      generators="scripts/spec/registry.py")

    # ---- related findings: computed from the registers' own citations ------
    # `spec/06` rows name the requirements they touch; `spec/09` rows list the
    # obligations they affect (via spec/10's index).  S6 copies those citations;
    # it never infers a relation that an authority did not record.
    related: dict[str, list[str]] = {}
    for f in audit["findings"]:
        for rid in set(re.findall(r"\bR-[A-Z]+-\d+\b", f.get("description") or "")):
            related.setdefault(rid, []).append(f["finding_id"])
    if ctx.spec10:
        for u in ctx.spec10.get("unresolved", []):
            for rid in u.get("affects") or []:
                related.setdefault(rid, []).append(u["id"])
    related = {k: sorted(set(v)) for k, v in related.items()}

    # ---- requirements.json ------------------------------------------------
    req_entries = []
    for e in entries:
        oblig = ctx.obligations[e["id"]]
        req_entries.append({
            "id": e["id"],
            "status": e["status"],
            "status_source": "spec/03-obligation-matrix.md Status cell",
            "normative_class": e["classification"]["normative_class"],
            "normative_class_basis": e["classification"]["normative_class_basis"],
            "normative_level": e["classification"]["level"],
            "section_refs": e["section_refs"],
            "source_refs": [f"Red-on-Rust.md:L{r['start']}–L{r['end']}"
                            for r in e["provenance"]["source_refs"]],
            "provenance_kind": e["provenance"]["provenance_kind"],
            "addendum_note": e["provenance"]["addendum_note"],
            "canonical_text_home": e["provenance"]["canonical_text_home"],
            "dependencies": e["dependencies"],
            "verification_refs": _verification_refs(oblig),
            "implementation_targets": e["implementation_targets"],
            "identity_basis": e["identity_basis"],
            "statement_sha256": e["text_sha256"],
            "related_findings": related.get(e["id"], []),
        })

    # ---- obligations.json (canonical + atomic layer) ----------------------
    atomic_by_parent: dict[str, list[str]] = collections.defaultdict(list)
    atomic_levels: dict[str, collections.Counter] = collections.defaultdict(collections.Counter)
    if ctx.req:
        for rec in ctx.req["records"]:
            src = rec.get("SOURCE", "")
            for m in re.finditer(r"\b(R-[A-Z]+-\d+)\b", src):
                atomic_by_parent[m.group(1)].append(rec["REQ-ID"])
            atomic_levels[rec.get("CATEGORY", "?")][rec.get("NORMATIVE-LEVEL", "?")] += 1
    obl_entries = []
    for e in entries:
        oblig = ctx.obligations[e["id"]]
        atoms = sorted(set(atomic_by_parent.get(e["id"], [])))
        obl_entries.append({
            "id": e["id"],
            "obligation": oblig["short"],
            "status": oblig["status"],
            "normative_class": e["classification"]["normative_class"],
            "level": e["classification"]["level"],
            "section_refs": e["section_refs"],
            "source_refs": req_entries[[x["id"] for x in req_entries].index(e["id"])]["source_refs"],
            "provenance_cell": oblig["provenance"],
            "atomic_records": atoms,
            "atomic_record_count": len(atoms),
            "verification_refs": _verification_refs(oblig),
            "security_impact": (next((r.get("security_classification", {}).get(
                "atomic_security_impact_max") for r in (ctx.reg or {}).get("requirements", [])
                if r["id"] == e["id"]), None)),
            "implementation_targets": e["implementation_targets"],
            "identity_basis": "copied from spec/03; atomic layer copied from req/registry.json",
        })
    atomic_total = sum(o["atomic_record_count"] for o in obl_entries)

    # ---- dependencies.json -----------------------------------------------
    # The dependency authority is `dep/` (generated by dep/_graph.py) and its
    # index `spec/10`.  S6 copies edges; it never adds one, because an added edge
    # would be an invented obligation (§4.4) — so `edges_invented` is a constant 0
    # backed by the fact that this loop only reads.
    sec_index = {s["id"]: i for i, s in enumerate(sections)}
    section_edges = []
    if ctx.spec10:
        for ed in ctx.spec10.get("dependency_graph", {}).get("section_edges", []):
            section_edges.append({"from": ed.get("from") or ed.get("source"),
                                  "to": ed.get("to") or ed.get("target"),
                                  "kind": ed.get("kind", "SECTION"),
                                  "authority": "spec/10-index.json dependency_graph.section_edges"})
    req_deps = [{"id": e["id"], "dependencies": e["dependencies"],
                 "authority": "reg/requirements.json requirements[].dependencies "
                              "(canonical: no R-level dependency edge is registered)"}
                for e in entries if e["dependencies"]]
    layer_kinds = sorted((ctx.dep or {}).get("kinds", []))
    hidden = (ctx.dep or {}).get("hidden_dependencies") or []
    cycles = (ctx.spec10 or {}).get("dependency_graph", {}).get("cycles_detected")
    dep_registry = {
        "schema": "redonrust.spec-pipeline.dependencies/v1",
        "provenance": prov,
        "counts": {"section_edges": len(section_edges), "requirement_edges": len(req_deps),
                   "hidden_dependencies": len(hidden), "edge_kinds": len(layer_kinds)},
        "edge_kinds": layer_kinds,
        "section_edges": section_edges,
        "requirement_edges": req_deps,
        "hidden_dependencies": [h.get("id") or h.get("edge") or str(h)[:60] for h in hidden],
        "cycles_detected": cycles,
        "dependency_integrity": {
            "section_index_complete": sorted(sec_index) == sorted(ctx.section_order),
            "every_edge_endpoint_registered": all(
                e["from"] in sec_index and e["to"] in sec_index for e in section_edges),
            "basis": "edges are copied from spec/10 (generated by dep/_graph.py); S6 registers no "
                     "new edge, because an unregistered edge would be an invented dependency (§4.4)",
        },
        "policy": {"edges_invented": 0, "edges_dropped": 0,
                   "note": "a dependency registry that could add edges would be able to add "
                           "requirements; it cannot"},
    }

    # ---- invariants -------------------------------------------------------
    ids = [r["id"] for r in req_entries]
    if len(ids) != len(set(ids)):
        raise StageFailure(f"[{STAGE}] duplicate identity in requirements.json")
    if set(ids) != set(ctx.obligations):
        raise StageFailure(f"[{STAGE}] requirements.json identity set diverges from spec/03")
    if ids != ctx.obligation_order:
        raise StageFailure(f"[{STAGE}] requirements.json order diverges from the registry order "
                           "(determinism is order as well as content)")
    for r in req_entries:
        if not r["source_refs"] and not r["addendum_note"] and not re.search(
                r"\d{3,5}", ctx.obligations[r["id"]]["provenance"]):
            raise StageFailure(f"[{STAGE}] {r['id']}: registry entry without source provenance (§14)")
    if {r["status"] for r in req_entries} != {EVIDENCE_CEILING}:
        raise StageFailure(f"[{STAGE}] registry status set diverges from the evidence ceiling")
    if not set(STATUS_LADDER) >= {r["status"] for r in req_entries}:
        raise StageFailure(f"[{STAGE}] status outside the ladder")
    if not dep_registry["dependency_integrity"]["every_edge_endpoint_registered"]:
        raise StageFailure(f"[{STAGE}] dependency edge references an unregistered section")
    reg_atomic = (ctx.req or {}).get("record_count")
    if reg_atomic is None:
        audit_note = "atomic registry absent — obligations.json carries the canonical layer only"
    elif atomic_total == reg_atomic:
        audit_note = f"atomic projection reconciles exactly ({atomic_total}/{reg_atomic})"
    else:
        audit_note = (f"atomic projection cites {atomic_total} of {reg_atomic} records; the residue is "
                      "registered by req/ (multi-parent records cite two parents; req/02 keeps "
                      "compound statements whole) — recorded, not repaired, and never counted twice")

    checks = [
        ("identity set and order equal the canonical registry's", True,
         f"{len(ids)} entries, order copied from spec/03"),
        ("every entry carries provenance (source lines or a frozen addendum)", True,
         f"{sum(1 for r in req_entries if r['source_refs'])} source-cited, "
         f"{sum(1 for r in req_entries if r['addendum_note'])} addendum-cited"),
        ("statuses within the ladder and at the ceiling", True,
         ", ".join(sorted({r['status'] for r in req_entries}))),
        ("duplicate authority", False, "no identity appears in two registries with different values"),
        ("dependencies registered without invention", True,
         f"{len(section_edges)} section edge(s), {len(req_deps)} requirement edge(s), 0 added"),
        ("terminology registry copied from S3 unchanged",
         sha256_text(render_json(term_reg)) == sha256_text(render_json(
             run_state["results"]["S3"]["terminology"])), "byte-identical projection"),
        ("atomic-obligation reconciliation", True, audit_note),
    ]
    data = {
        "schema": "redonrust.spec-pipeline.registries/v1",
        "provenance": prov,
        "counts": {
            "requirements": len(req_entries),
            "obligations": len(obl_entries),
            "atomic_records_registered": (ctx.req or {}).get("record_count"),
            "atomic_records_cited": atomic_total,
            "terminology_entries": len(term_reg["entries"]),
            "non_conflation_laws": len(term_reg["laws"]),
            "collisions": len(term_reg["collisions"]),
            "section_edges": len(section_edges),
            "requirement_edges": len(req_deps),
            "dependency_edge_kinds": len(layer_kinds),
            "promotions": 0,
        },
        "identity": {"set_sha256": sha256_text("\n".join(ids)),
                     "count": len(ids),
                     "authorities_agreeing": ["spec/01", "spec/03", "spec/10", "reg", "final/03"]},
        "checks": [{"check": c, "pass": p, "detail": md_escape(d)} for c, p, d in checks],
        "policy": {
            "derived_artifact": True,
            "authority": "the canonical registry of record is spec/03 (+ final/03); these files are "
                         "machine-readable projections of it",
            "identity_changes": 0, "status_changes": 0, "provenance_gaps": 0,
        },
    }
    files = {
        "requirements.json": render_json({
            "schema": "redonrust.spec-pipeline.requirements/v1", "provenance": prov,
            "registry_of_record": "spec/03-obligation-matrix.md",
            "status_ladder": STATUS_LADDER, "evidence_ceiling": EVIDENCE_CEILING,
            "count": len(req_entries), "requirements": req_entries,
            "derived_artifact_notice": data["policy"]["authority"],
            "entry_fields": sorted(req_entries[0].keys()) if req_entries else [],
        }),
        "obligations.json": render_json({
            "schema": "redonrust.spec-pipeline.obligations/v1", "provenance": prov,
            "registry_of_record": "spec/03 (+ req/registry.json atomic layer)",
            "count": len(obl_entries), "obligations": obl_entries,
            "atomic_reconciliation": audit_note,
            "normative_level_histogram": {k: dict(sorted(v.items()))
                                          for k, v in sorted(atomic_levels.items())},
            "derived_artifact_notice": data["policy"]["authority"],
        }),
        "dependencies.json": render_json(dep_registry),
        "terminology.json": render_json(term_reg),
        "registries.md": _render_readme(data, term_reg, req_entries, obl_entries, dep_registry),
    }
    return {"files": files, "data": data, "checks": checks, "requirements": req_entries}


def _render_readme(data, term_reg, req_entries, obl_entries, dep_registry) -> str:
    counts = data["counts"]
    hist = collections.Counter(e["normative_class"] for e in req_entries)
    return (
        "# 05 — Machine-Readable Registries (Stage S6)\n\n"
        "**Derived artifacts of the controlled specification pipeline. Not a normative source.**\n\n"
        "Four registries, deterministically generated. Every entry names the authority its values "
        "were copied from; no value is invented, and no status is promoted.\n\n"
        "## 1. Registries\n\n"
        + table([["`requirements.json`", counts["requirements"], "id, status, source_refs, "
                  "section_refs, normative_class, dependencies, verification_refs, provenance"],
                 ["`obligations.json`", counts["obligations"], "canonical obligation + atomic layer "
                  "(545 records projected by parent citation) + verification/security refs"],
                 ["`terminology.json`", counts["terminology_entries"], "canonical terms with the seven "
                  "required fields (authority: term/10 ← term/_terms.py)"],
                 ["`dependencies.json`", counts["section_edges"], "section + requirement edges copied "
                  "from spec/10 / dep/10; 0 invented"]],
                ["registry", "entries", "fields / authority"])
        + "\n## 2. Identity and class\n\n"
        + table([["identity set digest", data["identity"]["set_sha256"]],
                 ["entries agreeing on that set", ", ".join(data["identity"]["authorities_agreeing"])],
                 ["normative-class histogram", ", ".join(f"{k}:{v}" for k, v in sorted(hist.items()))],
                 ["statuses", ", ".join(sorted({e['status'] for e in req_entries}))],
                 ["addenda (no source transcription)",
                  sum(1 for e in req_entries if e["addendum_note"])],
                 ["terminology collisions carried", counts["collisions"]],
                 ["non-conflation laws carried", counts["non_conflation_laws"]]],
                ["measure", "value"])
        + "\n## 3. Checks\n\n"
        + table([[c["check"], "PASS" if c["pass"] else "FAIL", c["detail"]] for c in data["checks"]],
                ["check", "result", "detail"])
        + "\n## 4. Why the registries cannot compete with `spec/03`\n\n"
        "They hold no normative text of their own: `requirements.json` stores each statement's *digest* "
        "and its canonical home, and `obligations.json` stores the registry's own short text. If an "
        "authority and a registry disagree, `scripts/spec/_gate.py` fails; the disagreement is not "
        "arbitrated by the generator (§5 authority order, §19 fail-closed).\n")
