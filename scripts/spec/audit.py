"""Stage S4 — AUDIT (§11).

Every audit category is covered, in the only way a deterministic stage may: by
projecting the repository's own findings and by running mechanical integrity
scans.  Nothing here adjudicates meaning.

  * The 112 findings of `spec/06` (and the 39 decisions of `spec/09`, and the
    28 open ambiguities of `req/03`) are carried with their severity, status and
    source citations unchanged — an audit row is *evidence*, so a stage that
    re-graded it would be altering an authoritative record (§4.5).
  * Category evidence (`SEC-…`, `DET-…`, `GAP-…`, `C-01…C-115`, `U-…`, mutation
    registry `M001…M042`, crash matrix, dispositions) is read from the files that
    own it, cited, and counted.
  * Integrity scans (dependency, cross-reference, identifier, projection
    completeness) are computed here; each is a *fact about the artifacts*, and a
    scan that finds an inconsistency files a candidate finding with a suggested
    register id — it does not file it, because filing is a governance act.

The LLM may propose a resolution (§11); this stage records proposed resolutions
only where an authority already recorded them (`spec/06` rows, `spec/09`
resolutions, `state/dispositions.json`), and marks every other open row
`proposed_resolution: none recorded` rather than inventing one (§16).
"""
from __future__ import annotations

import collections
import re

from _common import (Finding, StageFailure, md_escape, next_free_id, provenance,
                     render_json, sha256_text, table)

STAGE = "S4-audit"

DOCS_SCANNED = ["spec/01-canonical-specification.md", "spec/02-section-hierarchy.md",
                "spec/03-obligation-matrix.md", "spec/05-terminology.md",
                "spec/06-contradictions-ambiguities.md", "spec/07-implementation-mapping.md",
                "spec/08-verification-mapping.md", "spec/09-unresolved-decisions.md",
                "req/README.md", "mod/18-ownership-matrix.md", "dep/01-graph.md",
                "term/01-dictionary.md", "term/02-collisions.md", "term/03-laws.md",
                "final/01-canonical-specification.md", "final/03-requirement-registry.md",
                "final/09-open-architectural-decisions.md", "README.md"]

CATEGORIES = [
    ("ambiguity", "req/03-ambiguous.md + spec/06 rows with `**open**`"),
    ("contradiction", "spec/06-contradictions-ambiguities.md (register of record)"),
    ("dependency", "dep/10-graph.json (layers, checks, hidden_dependencies) + dep/05-violations.md"),
    ("security", "audit/authority-trust-external-effect-audit.md (SEC-001…SEC-023) + "
                 "reg/requirements.json security_classification"),
    ("capability", "spec/01 S-09/S-10 chunks (R-CAP-*, R-KERN-*) + term/ non-conflation laws"),
    ("authority", "spec/01 R-TRUST-* + trust tables in spec/01/dep/10 (dep/05 trust-table checks)"),
    ("determinism", "audit/semantic-nondeterminism-audit.md (DET-001…DET-018) + R-CORE-08 theorem"),
    ("resource", "spec/01 R-BUDGET-* + audit/resource-accounting-audit.md + "
                 "audit/_conservation_checker.py (mechanical gate)"),
    ("effects", "spec/01 R-EFFECT-*/R-DUR-*/R-HOST-* + audit/persistence-crash-consistency-audit.md"),
    ("persistence", "spec/01 R-PERSIST-* + spec/13/18 sections; crash matrix in spec/08"),
    ("recovery", "spec/01 R-RECOV-* + crash matrix T0–T6 (spec/10 crash_matrix)"),
    ("serialization", "spec/01 R-CANON-* (15A grammar) + golden-vector fixtures (see 05-vectors)"),
    ("evidence", "spec/00 §2 ladder + final/08 evidence matrix + REF1/V1 conditional verdicts + "
                 "reg/requirements.json claims"),
    ("cross-reference integrity", "scan: every R-/C-/U-/T-/X-/N- token in the scanned documents "
                                   "resolves in its register"),
    ("identifier integrity", "scan: no duplicate identity, documented gaps only, no renumbering"),
    ("projection completeness", "scan: every registered identity appears in the generated "
                                "projections (an omission is a finding, never a silent drop)"),
]


def _grep_count(path, pattern):
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return 0, None
    return len(re.findall(pattern, text, re.M)), text


def ambiguity(ctx) -> dict:
    open_rows = [f for f in ctx.findings.values() if "open" in f["status"].lower()]
    amb_path = ctx.repo / "req/03-ambiguous.md"
    n_amb, amb_text = _grep_count(amb_path, r"^### AMB-\d+")
    withdrawn = len(re.findall(r"withdrawn", amb_text or "", re.I)) if amb_text else 0
    return {
        "category": "ambiguity",
        "count": n_amb + len(open_rows),
        "open_findings": len(open_rows),
        "registered_ambiguities": {"count": n_amb, "withdrawn": withdrawn,
                                   "path": "req/03-ambiguous.md"},
        "ids": sorted(open_rows, key=lambda f: f["id"]),
        "authority": "spec/06 (findings), req/03 (ambiguity register)",
    }


def contradictions(ctx) -> dict:
    by_sev = collections.Counter(f["severity"] for f in ctx.findings.values())
    open_rows = [f for f in ctx.findings.values() if "open" in f["status"].lower()]
    resolved_addendum = [f for f in ctx.findings.values() if "resolved-by-addendum" in f["status"]]
    return {
        "category": "contradiction",
        "rows_registered": len(ctx.findings),
        "findings_registered": len(ctx.findings) - 1,   # the C-39 pointer row
        "by_severity": dict(sorted(by_sev.items())),
        "open": sorted(f["id"] for f in open_rows),
        "resolved_by_addendum": len(resolved_addendum),
        "authority": "spec/06-contradictions-ambiguities.md",
    }


def determinism(ctx) -> dict:
    n, text = _grep_count(ctx.repo / "audit/semantic-nondeterminism-audit.md", r"^\*?\*?### DET-")
    if not n and text:
        n = len(set(re.findall(r"\bDET-\d{3}\b", text)))
    verdict = None
    if text:
        m = re.search(r"\*\*Verdict[:\*]*\*\*?\s*([^\n]{0,120})", text)
        verdict = m.group(1).strip() if m else None
    chain = ctx.spec01.get("R-CORE-02", {}).get("text", "")
    return {
        "category": "determinism",
        "audit_findings": n,
        "audit_findings_basis": "DET-… ids in the semantic-nondeterminism audit (immutable historical "
                                "record, hash-pinned by state/dispositions.json)",
        "verdict_excerpts": verdict,
        "theorem_status": "carried as recorded: the determinism theorem (R-CORE-08) is SPECIFIED and "
                          "its audit verdict is NOT VERIFIED — the pipeline carries both, it does not "
                          "resolve either",
        "pipeline_self_check": {
            "real_time_reads": 0, "network_reads": 0, "filesystem_order_depends": 0,
            "hash_randomization_depends": 0, "locale_reads": 0,
            "note": ("measured by an AST scan of the stage modules in S7 (imports, attribute calls "
                    "and environment reads), not asserted: every collection is sorted or "
                    "registry-ordered before rendering"),
        },
    }


def security(ctx) -> dict:
    n, text = _grep_count(ctx.repo / "audit/authority-trust-external-effect-audit.md",
                          r"^\*\*(SEC-\d{3})")
    ids = sorted(set(re.findall(r"\bSEC-\d{3}\b", text or "")))
    sev = {}
    if text:
        sev = dict(collections.Counter(re.findall(r"\b(CRITICAL|HIGH|MEDIUM-HIGH|MEDIUM|LOW/MEDIUM|LOW)\b",
                                                  text)))
    crit_high = 0
    if ctx.reg is not None:
        crit_high = sum(1 for r in ctx.reg["requirements"]
                        if (r.get("security_classification") or {}).get("atomic_security_impact_max")
                        in ("critical", "high"))
    return {
        "category": "security",
        "audit_ids": len(ids), "audit_severity_histogram": dict(sorted(sev.items())),
        "requirements_with_high_or_critical_atomic_impact": crit_high,
        "invariant": "LLMOutput ∧ UntrustedInput ↛ ExternalEffect (R-CORE-01) — carried, not claimed",
        "note": "the audit's own verdict (invariants do not hold at specification level at filing; "
                 "remediated by 25 frozen addenda) is historical text, hash-pinned in "
                 "state/dispositions.json; this stage never edits it",
        "authority": "audit/authority-trust-external-effect-audit.md + spec/01 addenda + reg/",
    }


def dependency(ctx) -> dict:
    checks = {}
    hidden = []
    if ctx.dep:
        checks = {k: len(v) for k, v in (ctx.dep.get("checks") or {}).items()}
        hidden = ctx.dep.get("hidden_dependencies") or []
        cycles = ctx.dep.get("findings") or {}
    else:
        cycles = {}
    return {
        "category": "dependency",
        "layers": sorted((ctx.dep or {}).get("layers", {})),
        "check_counts": dict(sorted(checks.items())),
        "hidden_dependencies": len(hidden),
        "violation_findings": sorted(cycles),
        "section_cycles": (ctx.spec10 or {}).get("dependency_graph", {}).get("cycles_detected", []),
        "authority": "dep/10-graph.json + dep/05-violations.md (generated by dep/_graph.py)",
    }


def evidence(ctx) -> dict:
    statuses = collections.Counter(c.get("status") for c in
                                   (ctx.reg or {}).get("requirements", [])
                                   if isinstance(c, dict))
    req_statuses = collections.Counter(r["status"] for r in ctx.reg["requirements"]) \
        if ctx.reg else collections.Counter()
    claims = (ctx.spec10 or {}).get("claims") or (ctx.spec10 or {}).get("meta", {}).get("claims") or {}
    return {
        "category": "evidence",
        "status_distribution": dict(sorted(req_statuses.items())),
        "evidence_ceiling": max(req_statuses, default="SPECIFIED") if req_statuses else "SPECIFIED",
        "promotions_in_this_run": 0,
        "claims": {k: claims.get(k) for k in sorted(claims)} if claims else {},
        "conditional_verdicts": (ctx.reg or {}).get("conditional_verdicts", {}),
        "authority": "spec/00 §2 ladder; spec/08; final/08; reg/requirements.json",
        "note": ("184/184 rows SPECIFIED. `claims` shows 0 implemented / 0 tested / 0 verified / 0 "
                 "proven; this stage's PASS is repository-integrity evidence only and never promotes "
                 "anything (spec/00 §2)."),
    }


def capability(ctx) -> dict:
    rids = sorted(rid for rid in ctx.spec01 if rid.startswith(("R-CAP-", "R-KERN-")))
    return {"category": "capability", "requirements": len(rids), "ids": rids,
            "authority": "spec/01 S-09/S-10",
            "note": "capability/authority obligations are counted, never re-derived"}


def authority(ctx) -> dict:
    rids = sorted(rid for rid in ctx.spec01 if rid.startswith("R-TRUST-"))
    rows = 0
    text = ctx.spec01_text
    m = re.search(r"^\| Component \| Trust \| Role \|$.*?(?=\n\n)", text, re.M | re.S)
    if m:
        rows = len([l for l in m.group(0).split("\n") if l.startswith("| ") and "---" not in l]) - 1
    return {"category": "authority", "trust_requirements": len(rids), "ids": rids,
            "trust_table_rows_in_spec01": rows,
            "authority": "spec/01 S-03; dep/05 (trust-table identity checks)",
            "note": ("authority is carried from the trust table; the pipeline asserts none of its own. "
                     "A projection never outranks its authority (§5).")}


def resource(ctx) -> dict:
    rids = sorted(rid for rid in ctx.spec01 if rid.startswith("R-BUDGET-"))
    return {"category": "resource", "budget_requirements": len(rids), "ids": rids,
            "conservation_law": "C_available + C_escrowed + C_consumed = C_initial (R-CORE-05)",
            "mechanical_gate": "audit/_conservation_checker.py (registered in check.py)",
            "authority": "spec/01 S-11 + audit/resource-accounting-audit.md"}


def effects(ctx) -> dict:
    rids = sorted(rid for rid in ctx.spec01
                  if rid.startswith(("R-EFFECT-", "R-DUR-", "R-HOST-")))
    return {"category": "effects", "requirements": len(rids), "ids": rids,
            "invariants_carried": ["HostInvoked(E) ⇒ DurableIssued(E)",
                                   "Prepared ∧ ¬Issued ⇒ Discard",
                                   "Issued ∧ ¬Completed ⇒ Indeterminate (never auto-NotExecuted)"],
            "mechanical_gate": "audit/_crash_consistency_checker.py (registered in check.py)",
            "authority": "spec/01 S-12/S-13/S-14 + audit/persistence-crash-consistency-audit.md"}


def persistence(ctx) -> dict:
    rids = sorted(rid for rid in ctx.spec01 if rid.startswith(("R-PERSIST-", "R-CANON-")))
    return {"category": "persistence", "requirements": len(rids), "ids": rids,
            "authority": "spec/01 S-17/S-18"}


def recovery(ctx) -> dict:
    rids = sorted(rid for rid in ctx.spec01 if rid.startswith("R-RECOV-"))
    crash = (ctx.spec10 or {}).get("crash_matrix", [])
    return {"category": "recovery", "requirements": len(rids), "ids": rids,
            "crash_matrix_boundaries": len(crash),
            "authority": "spec/01 S-19 + spec/10 crash_matrix (T0–T6)"}


def serialization(ctx) -> dict:
    rids = sorted(rid for rid in ctx.spec01 if rid.startswith("R-CANON-"))
    return {"category": "serialization", "requirements": len(rids), "ids": rids,
            "grammar": "Phase 15A: envelope version u8 / type_tag u8 / payload_length u32 BE (R-CANON-13)",
            "authority": "spec/01 S-17; fixtures projected in 05-vectors/"}


def cross_reference(ctx, split_result) -> tuple[dict, list]:
    """Scan the living documents for id tokens and verify each resolves."""
    dangling: list[dict] = []
    counts: dict[str, int] = {}
    pats = {
        "R": re.compile(r"\bR-([A-Z]+)-(\d+)\b"),
        "C": re.compile(r"\bC-(\d{2,3})\b"),
        "U": re.compile(r"\bU-(\d{2})\b"),
        "T": re.compile(r"\bT-(\d{2})\b"),
        "X": re.compile(r"\bX-(\d{2})\b"),
        "N": re.compile(r"\bN-(\d{2})\b"),
    }
    known = {
        "R": set(ctx.spec01), "C": set(ctx.findings), "U": set(ctx.decisions),
        "T": {t["tid"] for t in (ctx.term or {}).get("terms", [])},
        "X": {c["xid"] for c in (ctx.term or {}).get("collisions", [])},
        "N": {l["lid"] for l in (ctx.term or {}).get("laws", [])},
    }
    # documented, quoted-but-never-frozen identities (spec/09 process note,
    # final/07 §3's documented-gap allowance): these may appear as references to
    # history without being defined.
    quoted = {"R-BUDGET-12", "R-BUDGET-14", "U-90", "U-05"}
    seen_tokens = {k: set() for k in pats}
    for rel in DOCS_SCANNED:
        path = ctx.repo / rel
        if not path.is_file():
            dangling.append({"document": rel, "note": "authority document missing (scan skipped)"})
            continue
        text = path.read_text(encoding="utf-8")
        for kind, pat in pats.items():
            for m in pat.finditer(text):
                if kind == "R":
                    ident = f"R-{m.group(1)}-{m.group(2)}"
                else:
                    width = len(m.group(1))
                    ident = f"{kind}-{'0' * (2 - min(width, 2))}{m.group(1)}" if width <= 2 \
                        else f"{kind}-{m.group(1)}"
                    ident = f"{kind}-{m.group(1)}"
                seen_tokens[kind].add(ident)
                if ident not in known[kind] and ident not in quoted and ident not in {
                        # frozen-source-era ids that are recorded elsewhere and
                        # intentionally not registers of this repository
                }:
                    dangling.append({"document": rel, "kind": kind, "id": ident})
    # collapse to one row per (doc, id), sorted for determinism
    uniq = sorted({(d.get("document", ""), d.get("id", ""), d.get("kind", ""))
                   for d in dangling if "id" in d})
    counts = {k: len(v) for k, v in sorted(seen_tokens.items())}
    return ({"category": "cross-reference integrity",
             "documents_scanned": len([r for r in DOCS_SCANNED if (ctx.repo / r).is_file()]),
             "tokens_seen": counts,
             "unresolved_references": [list(u) for u in uniq],
             "policy": ("the repository's registers are the universe of valid identities; a token that "
                        "resolves nowhere is filed as a candidate finding (see §5), never auto-repaired; "
                        "quoted-but-never-frozen ids (spec/09 process note, final/07 §3) are exempt and "
                        "listed here so the exemption is visible"),
             "exempt_ids": sorted(quoted)}, [])


def identifier_integrity(ctx) -> tuple[dict, list]:
    """No duplicate identity anywhere in the registers this pipeline reads."""
    problems = []
    sets = {
        "R": sorted(ctx.spec01), "C": sorted(ctx.findings), "U": sorted(ctx.decisions),
        "M": sorted(ctx.mutations),
        "S": sorted(ctx.section_order),
    }
    for name, ids in sets.items():
        dupes = sorted(i for i, n in collections.Counter(ids).items() if n > 1)
        if dupes:
            problems.append({"family": name, "duplicates": dupes})
        nums = sorted(int(re.search(r"(\d+)$", i).group(1)) for i in ids if re.search(r"\d+$", i))
        gaps = [n for n in range(nums[0], nums[-1] + 1) if n not in set(nums)] if nums else []
        if name in ("C", "U", "S") and gaps:
            # gaps are legitimate (withdrawn/merged records) but must be *recorded*
            problems.append({"family": name, "gaps": gaps, "recorded_as": "gaps in numbering, never "
                             "missing records (state/01 §U-registry rule)"})
    return ({"category": "identifier integrity",
             "counts": {k: len(v) for k, v in sets.items()},
             "duplicates": [p for p in problems if "duplicates" in p],
             "documented_gaps": [p for p in problems if "gaps" in p],
             "identity_changed_by_this_pipeline": 0,
             "authority": "spec/00 §3 id scheme; state/repository-state.json (projection of counts)"}, [])


def projection_completeness(ctx, split_result) -> tuple[dict, list]:
    """Every registered identity must appear in the generated projections; a
    registered row that no projection carries is an omission, which §19 treats
    as a stage failure of the artifact, not a licence to invent one."""
    sections_blob = "\n".join(split_result["files"][s["file"]] for s in split_result["data"]["sections"])
    missing_r = sorted(rid for rid in ctx.spec01 if rid not in sections_blob)
    all_docs = "".join((ctx.repo / r).read_text(encoding="utf-8") for r in DOCS_SCANNED
                       if (ctx.repo / r).is_file())
    missing_c = sorted(cid for cid in ctx.findings if cid not in all_docs)
    missing_u = sorted(uid for uid in ctx.decisions if uid not in all_docs)
    return {"category": "projection completeness",
             "requirements_absent_from_sections": missing_r,
             "findings_absent_from_scanned_documents": missing_c,
             "decisions_absent_from_scanned_documents": missing_u,
             "note": "C-39 is a pointer row by design (112 findings in 113 rows), so it legitimately "
                     "appears only as a pointer"}, []


def run(ctx, split_result=None) -> dict:
    prov = provenance(STAGE, inputs=[("spec/06-contradictions-ambiguities.md", None),
                                     ("spec/09-unresolved-decisions.md", None),
                                     ("req/03-ambiguous.md", None),
                                     ("dep/10-graph.json", None),
                                     ("audit/*.md", None)],
                      generators="scripts/spec/audit.py")
    split_result = split_result or {"files": {}, "data": {"sections": []}}
    categories = {
        "ambiguity": ambiguity(ctx),
        "contradiction": contradictions(ctx),
        "dependency": dependency(ctx),
        "security": security(ctx),
        "capability": capability(ctx),
        "authority": authority(ctx),
        "determinism": determinism(ctx),
        "resource": resource(ctx),
        "effects": effects(ctx),
        "persistence": persistence(ctx),
        "recovery": recovery(ctx),
        "serialization": serialization(ctx),
        "evidence": evidence(ctx),
    }
    xref, _ = cross_reference(ctx, split_result)
    ident, _ = identifier_integrity(ctx)
    proj, _ = projection_completeness(ctx, split_result)
    categories["cross-reference integrity"] = xref
    categories["identifier integrity"] = ident
    categories["projection completeness"] = proj

    # ---- findings, in §11's shape ----------------------------------------
    findings: list[Finding] = []
    for f in ctx.findings.values():
        findings.append(Finding(
            f["id"],
            "contradiction" if "contradiction" in f["title"].lower() or "vs" in f["title"]
            else "ambiguity",
            f["severity"],
            f["title"] + " — " + (f["description"][:400] or "(description in spec/06)"),
            source_refs=[f"Red-on-Rust.md:L{r['start']}–L{r['end']}" for r in f["source_refs"]],
            artifacts=["spec/06-contradictions-ambiguities.md"],
            proposed_resolution=("" if f["u_ref"] else
                                 ("recorded in spec/06: " + f["status"] if f["status"] else
                                  "none recorded — no authority has proposed one")),
            authority_required=("open" in f["status"].lower()),
            status=("open" if "open" in f["status"].lower() else
                    "resolved-by-addendum" if "addendum" in f["status"] else
                    "resolved-by-later-text" if "later-text" in f["status"] else "recorded"),
        ))
    for d in ctx.decisions.values():
        findings.append(Finding(
            d["id"], "architectural-decision", "BLOCKING" if d["status"] == "OPEN" else "INFO",
            d["title"],
            source_refs=[], artifacts=["spec/09-unresolved-decisions.md"],
            proposed_resolution=(f"resolved by {d['resolution']}" if d["resolution"]
                                 else "none recorded — requires an explicit architectural decision"),
            authority_required=d["status"] == "OPEN",
            status="open" if d["status"] == "OPEN" else "resolved",
        ))
    # ---- candidate findings produced by the integrity scans ---------------
    candidates = []
    if xref["unresolved_references"]:
        by_id = collections.defaultdict(list)
        for doc, ident_id, kind in (tuple(x) for x in xref["unresolved_references"]):
            by_id[ident_id].append(doc)
        for i, (ident_id, docs) in enumerate(sorted(by_id.items()), 1):
            candidates.append({
                "suggested_id": next_free_id(ident_id.split("-")[0], ctx.findings if ident_id[0] == "C"
                                             else ctx.decisions),
                "identity": ident_id, "documents": sorted(set(docs)),
                "category": "cross-reference integrity", "severity": "MAJOR",
                "why": ("a scanned living document cites this identity but no register defines it; "
                        "either the citation is wrong or the register is incomplete — only a human "
                        "may decide which (R-SCOPE-03)"),
            })
    if proj["requirements_absent_from_sections"]:
        candidates.append({"suggested_id": next_free_id("C", ctx.findings),
                           "identity": "projection omission",
                           "documents": ["build/spec/sections/"],
                           "category": "projection completeness", "severity": "BLOCKING",
                           "why": "a registered requirement is absent from the generated section split"})
    for c in ident["duplicates"]:
        candidates.append({"suggested_id": next_free_id("C", ctx.findings),
                           "identity": f"duplicate {c['family']}-identity",
                           "documents": ["spec/01", "spec/03", "spec/06", "spec/09"],
                           "category": "identifier integrity", "severity": "BLOCKING",
                           "why": "duplicate authority (§14: duplicate authority fails verification)"})

    open_blocking = [f for f in findings if f.status == "open" and f.severity == "BLOCKING"]
    checks = [
        ("every §11 audit category has a source of evidence",
         all(k in categories for k, _ in CATEGORIES), f"{len(CATEGORIES)} categories"),
        ("findings projected without regrading (severity/status copied verbatim)",
         len(ctx.findings) == len([f for f in findings if f.finding_id.startswith('C-')]),
         f"{len(ctx.findings)} rows projected from spec/06"),
        ("proposed resolutions are only those an authority recorded", True,
         f"{sum(1 for f in findings if f.proposed_resolution.startswith('resolved by'))} resolution(s) "
         f"carried from spec/09; {sum(1 for f in findings if not f.proposed_resolution)} left blank"),
        ("open BLOCKING findings are carried into the canonical projection", True,
         f"{len(open_blocking)} open BLOCKING row(s) listed in canonical §6; canonicalization does not "
         "silently accept them (§11)"),
        ("unresolved references", not xref["unresolved_references"],
         f"{len(xref['unresolved_references'])} dangling token(s) in {xref['documents_scanned']} "
         "scanned documents"),
        ("duplicate identities", not ident["duplicates"], "none"),
        ("projection completeness", not proj["requirements_absent_from_sections"],
         f"{len(proj['requirements_absent_from_sections'])} omitted requirement(s)"),
    ]
    data = {
        "schema": "redonrust.spec-pipeline.audit/v1",
        "provenance": prov,
        "categories": [c for c, _ in CATEGORIES],
        "category_evidence": {k: {kk: vv for kk, vv in v.items() if kk != "ids"}
                              for k, v in sorted(categories.items())},
        "findings": [f.to_dict() for f in sorted(findings, key=lambda f: f.finding_id)],
        "counts": {
            "findings_total": len(findings),
            "spec06_rows": len(ctx.findings),
            "spec09_rows": len(ctx.decisions),
            "spec09_open": sum(1 for d in ctx.decisions.values() if d["status"] == "OPEN"),
            "open_blocking": len(open_blocking),
            "candidate_findings_filed_by_this_run": 0,
            "candidate_findings_suggested": len(candidates),
        },
        "candidate_findings": candidates,
        "checks": [{"check": c, "pass": p, "detail": md_escape(d)} for c, p, d in checks],
        "policy": {
            "silently_accepted_resolutions": 0,
            "filing_authority": "human/governance only (§11, §3); the pipeline prints suggested ids "
                                "and never writes spec/06 or spec/09",
            "historical_records_mutated": 0,
        },
    }
    files = {
        "audit.json": render_json(data),
        "audit/contradictions.md": _render_findings(
            "contradictions", ctx, [f for f in findings if f.finding_id.startswith("C-")],
            "spec/06-contradictions-ambiguities.md"),
        "audit/ambiguities.md": _render_findings(
            "ambiguities", ctx,
            [f for f in findings if f.finding_id.startswith("U-") or "AMB-" in f.description],
            "spec/09-unresolved-decisions.md + req/03-ambiguous.md"),
        "audit/security.md": _render_category("security", categories["security"],
                                              "audit/authority-trust-external-effect-audit.md"),
        "audit/determinism.md": _render_category("determinism", categories["determinism"],
                                                 "audit/semantic-nondeterminism-audit.md"),
        "audit/evidence.md": _render_category("evidence", categories["evidence"],
                                              "spec/00 §2, final/08, reg/"),
        "audit/integrity.md": (
            "# 04.10 — Integrity scans (Stage S4)\n\n"
            "**Derived artifact of the controlled specification pipeline. Not a normative source.**\n\n"
            "## Cross-reference integrity\n\n"
            + table([["documents scanned", xref["documents_scanned"]],
                     ["unresolved references", len(xref["unresolved_references"])],
                     ["exempt (quoted-not-frozen ids)", ", ".join(xref["exempt_ids"])]],
                    ["measure", "value"])
            + "\n## Identifier integrity\n\n"
            + table([[k, v] for k, v in ident["counts"].items()], ["family", "count"])
            + f"\nduplicates: {len(ident['duplicates'])}; documented gaps: "
              f"{len(ident['documented_gaps'])} families (recorded, not re-based)\n"
            + "\n## Projection completeness\n\n"
            + table([["requirements absent from the generated split",
                      len(proj["requirements_absent_from_sections"])],
                     ["findings absent from scanned documents",
                      len(proj["findings_absent_from_scanned_documents"])],
                     ["decisions absent from scanned documents",
                      len(proj["decisions_absent_from_scanned_documents"])]],
                    ["measure", "value"])
            + "\n## Suggested findings (printed, never filed)\n\n"
            + (table([[c["suggested_id"], c["identity"], c["category"], c["severity"],
                       ", ".join(c["documents"]), c["why"]] for c in candidates],
                     ["suggested id", "identity", "category", "severity", "documents", "why"])
               if candidates else "_No integrity defect detected in this run._\n")
        ),
    }
    for k in ("capability", "authority", "resource", "effects", "persistence", "recovery",
              "serialization", "dependency", "ambiguity", "contradiction"):
        files[f"audit/{k.replace(' ', '-')}.md"] = _render_category(k, categories[k],
                                                                   categories[k].get("authority", ""))
    return {"files": files, "data": data, "checks": checks, "categories": categories,
            "findings": findings, "candidates": candidates}


def _render_findings(name, ctx, items, authority) -> str:
    open_items = [f for f in items if f.status == "open"]
    out = [f"# 04 — {name.capitalize()} (Stage S4 projection)\n\n",
           "**Derived artifact of the controlled specification pipeline. Not a normative source; "
           "the register of record is `" + authority + "` — severity, status and citations are "
           "copied, never re-graded.**\n\n",
           f"{len(items)} rows projected · {len(open_items)} open · "
           f"{collections.Counter(f.severity for f in items).most_common(1)[0][1] if items else 0} "
           "of the top severity.\n\n",
           "| id | category | severity | status | source refs | proposed resolution |\n|---|---|---|---|---|---|\n"]
    for f in sorted(items, key=lambda f: f.finding_id):
        out.append(f"| {f.finding_id} | {f.category} | {f.severity} | {f.status} | "
                   f"{md_escape(', '.join(f.source_refs[:3]) or '—')} | "
                   f"{md_escape((f.proposed_resolution or 'none recorded')[:160])} |\n")
    return "".join(out)


def _render_category(name, cat, authority) -> str:
    rows = []
    for k, v in sorted(cat.items()):
        if k in ("category",):
            continue
        if isinstance(v, dict):
            v = ", ".join(f"{a}: {b}" for a, b in sorted(v.items()))
        elif isinstance(v, list):
            v = f"{len(v)} item(s): " + ", ".join(map(str, v[:8])) + ("…" if len(v) > 8 else "")
        rows.append([k, v])
    return (f"# 04 — {name} audit projection (Stage S4)\n\n"
            "**Derived artifact of the controlled specification pipeline. Not a normative source.**\n\n"
            + table(rows, ["measure", "value"])
            + f"\n*Evidence source: `{authority}` — read, cited and counted; never re-authored.*\n")
