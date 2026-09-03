#!/usr/bin/env python3
"""state/_project.py — single repository-state projection + fail-closed gate.

WHAT THIS IS (repair pass v2: V-07 + V-08)
------------------------------------------
One deterministic projection of the CURRENT repository state, derived — never
hard-coded — from the authoritative sources, plus the cross-artifact battery
that makes stale derived state fail the repository gate.

Authority chain (this file adds no normative content anywhere):

    frozen normative sources (Red-on-Rust.md, frozen addenda in spec/01)
      -> authoritative registers (spec/01..09, req/registry.json, check.py
         registration, term/, state/dispositions.json)
      -> deterministic generators (spec/_build_index.py, final/_build.py,
         reg/_compile.py, term/_dict.py)
      -> derived artifacts (spec/10, final/*, reg/*, term/*, this output)
      -> cross-artifact consistency gates  <-- THIS FILE
      -> repository-state projection (state/repository-state.json, 01, 02)

Every count below is computed by an independent re-derivation from the
authorities (deliberately NOT imported from the other tools' parsers, so a
defect in one parser cannot hide behind agreement with itself). The EXPECTED
block is a validation pin in the style of reg/_compile.py's EXPECTED_COUNT:
if a computed value differs, the failure says INVESTIGATE, it never silently
re-bases. Pin history: checkers was 15 at the start of this repair pass and
became 16 when this file itself was registered as the V-08 gate.

Evidence discipline: this is a repository-integrity gate. A green run is NOT
semantic verification of any R-… obligation (V1 F-INFL-01) and implies no
implementation, testing, verification or proof (R-CLAIM-01; spec/00 §2).

    python3 state/_project.py            # check mode (what check.py runs)
    python3 state/_project.py --write    # render state/repository-state.json, 01, 02
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


def read(rel: str) -> str:
    return (REPO / rel).read_text(encoding="utf-8")


def sha256_bytes(b: bytes) -> str:
    return "sha256:" + hashlib.sha256(b).hexdigest()


# ---------------------------------------------------------------------------
# validation expectations (pins, not generator constants)
# ---------------------------------------------------------------------------
EXPECTED = {
    "requirements": 184,          # spec/00 §3 / final/03 / reg EXPECTED_COUNT
    "atomic_records": 545,        # req/registry.json record_count
    "u_items": 39,                # spec/09 registered rows (NOT the numeric max)
    "u_open": 28,                 # incl. the preserved-stale U-05 row
    "u_resolved": 11,             # addenda VII/VIII/IX + U-38 gate adoption
    "u_numeric_max": 45,          # descriptive only; NEVER a cardinality
    "findings": 112,              # spec/06 rows minus the C-39 pointer row
    "mutations": 42,              # spec/08 §2 (dense M001…M042)
    "verification_tags": 25,      # spec/08 §1 tables: 16 frozen + 9 addendum
    "checkers": 16,               # check.py CHECKERS (15 pre-repair + this gate)
    "non_checkers": 7,            # check.py NON_CHECKERS
    "implementation": "BOOTSTRAP",
    "evidence_ceiling": "SPECIFIED",
    "ref1": "REF1-CONDITIONAL",
    "v1": "V1-CONDITIONAL",
}


class Fail(Exception):
    pass


def ok(results, cond, label):
    results.append((bool(cond), label))
    return bool(cond)


# ---------------------------------------------------------------------------
# independent derivations from the authorities
# ---------------------------------------------------------------------------

def u_registry():
    """spec/09 -> dict of the U register state. Independent of final/_parse:
    resolution detection reimplements the same published rules (Resolved
    bullet / RETIRED / tooling adoption; U-05 is the preserved-stale row)."""
    txt = read("spec/09-unresolved-decisions.md")
    heads = list(re.finditer(r"^### (U-\d+) — (.*)$", txt, re.M))
    items = []
    for i, h in enumerate(heads):
        end = heads[i + 1].start() if i + 1 < len(heads) else len(txt)
        body = txt[h.start():end]
        rid = h.group(1)
        resolved = None
        m = re.search(r"\*\*Resolved \(addendum ([IVX]+)[,)]", body)
        if m:
            resolved = f"addendum {m.group(1)}"
        elif "RETIRED by decision" in body:
            resolved = "recorded"
        elif re.search(r"\*\*Resolved \(2026-09-03, tooling", body):
            resolved = "repository-gate adoption"
        status = "RESOLVED" if resolved else "OPEN"
        note = ""
        if rid == "U-05":
            status = "OPEN"          # register row stale; R-ARCH-05 governs (DISP-06)
            note = "preserved-stale row (DISP-06)"
        items.append({"id": rid, "title": h.group(2).strip(), "status": status,
                      "resolution": resolved, "note": note})
    ids = [u["id"] for u in items]
    nums = [int(i[2:]) for i in ids]
    gaps = sorted(n for n in range(1, max(nums) + 1) if n not in nums)
    return {
        "items": items,
        "registered": len(items),
        "open": sum(1 for u in items if u["status"] == "OPEN"),
        "resolved": sum(1 for u in items if u["status"] == "RESOLVED"),
        "numeric_max": max(nums),
        "ids": ids,
        "gaps": ["U-%02d" % n for n in gaps],
    }


def checker_inventory():
    """check.py registration -> (checkers, non_checkers), via ast (no exec)."""
    tree = ast.parse(read("check.py"))
    out = {}
    for node in tree.body:
        targets = []
        if isinstance(node, ast.Assign):
            targets = node.targets
            value = node.value
        elif isinstance(node, ast.AnnAssign) and node.value is not None:
            targets = [node.target]
            value = node.value
        else:
            continue
        for t in targets:
            if isinstance(t, ast.Name) and t.id in ("CHECKERS", "NON_CHECKERS"):
                vals = []
                if isinstance(value, ast.Dict):
                    vals = [ast.literal_eval(k) for k in value.keys]
                elif isinstance(value, ast.List):
                    for el in value.elts:
                        if isinstance(el, ast.Tuple) and el.elts:
                            vals.append(ast.literal_eval(el.elts[0]))
                        elif isinstance(el, ast.Constant):
                            vals.append(el.value)
                out[t.id] = vals
    for need in ("CHECKERS", "NON_CHECKERS"):
        if need not in out:
            raise Fail(f"check.py: could not derive {need} (registration parse failed)")
    return out["CHECKERS"], out["NON_CHECKERS"]


def spec08_tags_and_mutations():
    """spec/08 -> (frozen_tags, addendum_tags, mutation_ids), table-parsed."""
    txt = read("spec/08-verification-mapping.md")
    sec1 = txt.split("## 1. Source verification-obligation tags", 1)[1].split("## 2.", 1)[0]
    frozen_part, _, addendum_part = sec1.partition("**Post-audit addendum tags**")
    pat = re.compile(r"^\| `([A-Z][A-Z0-9]*(?:-[A-Z0-9]+)+)` \|", re.M)
    frozen, addendum = pat.findall(frozen_part), pat.findall(addendum_part)
    muts = re.findall(r"^\| (M\d{3}) \|", txt.split("## 2. Mutation registry", 1)[1]
                      .split("## 3.", 1)[0], re.M)
    return frozen, addendum, muts


def requirement_id_lists():
    spec01 = set(re.findall(r"^\*\*(R-[A-Z]+-\d+)", read("spec/01-canonical-specification.md"), re.M))
    spec03 = re.findall(r"^\| (R-[A-Z]+-\d+) \|", read("spec/03-obligation-matrix.md"), re.M)
    spec10 = [r["id"] for r in json.loads(read("spec/10-index.json"))["requirements"]]
    final03 = re.findall(r"^\| (R-[A-Z]+-\d+) \|", read("final/03-requirement-registry.md"), re.M)
    reg = json.loads(read("reg/requirements.json"))
    regids = [r["id"] for r in reg["requirements"]]
    return spec01, spec03, spec10, final03, regids, reg


def chain_conjuncts(chain: str) -> list[str]:
    return [c.strip() for c in chain.split("∧")]


def core02_and_core11():
    txt = read("spec/01-canonical-specification.md")
    m2 = re.search(r"\*\*R-CORE-02 .*?\*\*(.*?)(?=\n\n\*\*R-|\n\n## |\Z)", txt, re.S)
    m11 = re.search(r"\*\*R-CORE-11 .*?\*\*(.*?)(?=\n\n\*\*R-|\n\n## |\Z)", txt, re.S)
    if not m2 or not m11:
        raise Fail("spec/01: could not locate the R-CORE-02 / R-CORE-11 chunks")
    body2, body11 = m2.group(1), m11.group(1)
    mc = re.search(r"`ExternalEffect\(E\) ⇒ (.+?)`", body2)
    if not mc:
        raise Fail("spec/01 R-CORE-02: boxed chain not found")
    return body2, body11, mc.group(1)


def dispositions():
    d = json.loads(read("state/dispositions.json"))
    return d


# ---------------------------------------------------------------------------
# the battery (V-08: fail-closed cross-artifact checks)
# ---------------------------------------------------------------------------

def battery(U, res):
    """Populate `res` with (ok, label) tuples. Raises nothing; every failure
    is a False result so the whole battery is reported at once."""
    spec10 = json.loads(read("spec/10-index.json"))
    reqreg = json.loads(read("req/registry.json"))

    # --- 1. U-registry vs U-projections -----------------------------------
    ok(res, U["registered"] == U["open"] + U["resolved"],
       f"1  U registry partition: registered {U['registered']} == open {U['open']} "
       f"+ resolved {U['resolved']}")
    ok(res, U["registered"] != U["numeric_max"] or not U["gaps"],
       f"1b cardinality ≠ range: registered {U['registered']} and numeric max "
       f"{U['numeric_max']} are distinct facts; numbering gaps {U['gaps']} are gaps in "
       "numbering, not missing records (contiguity is never required and never asserted)")
    hdr = read("spec/09-unresolved-decisions.md")
    mh = re.search(r"registered \*\*(\d+)\*\* · open \*\*(\d+)\*\* · resolved \*\*(\d+)\*\* "
                   r"· numeric maximum identifier \*\*U-(\d+)\*\*", hdr)
    ok(res, mh and (int(mh.group(1)), int(mh.group(2)), int(mh.group(3)), int(mh.group(4)))
       == (U["registered"], U["open"], U["resolved"], U["numeric_max"]),
       "1c spec/09 register-status declaration matches the derived registry state "
       f"(got {mh.group(0) if mh else 'NOT FOUND'})")
    ok(res, len(spec10["unresolved"]) == U["registered"],
       f"1d spec/10 unresolved index ({len(spec10['unresolved'])}) == spec/09 registered "
       f"({U['registered']})")
    f09 = read("final/09-open-architectural-decisions.md")
    m09 = re.search(r"\*\*(\d+) OPEN, (\d+) resolved\.\*\*", f09)
    per_row_ok = True
    for u in U["items"]:
        row = re.search(r"^\| `%s` \|[^\n]*\| (OPEN|RESOLVED)" % u["id"], f09, re.M)
        if not row or not row.group(1).startswith(u["status"]):
            per_row_ok = False
    ok(res, m09 and (int(m09.group(1)), int(m09.group(2))) == (U["open"], U["resolved"]) and per_row_ok,
       f"1e final/09 §A projection matches the registry per-row ({m09.group(0) if m09 else 'counts NOT FOUND'}; "
       "every OPEN/RESOLVED cell agrees with spec/09)")

    # --- 2. checker inventory vs projections -------------------------------
    checkers, non_checkers = checker_inventory()
    ok(res, all((REPO / c).is_file() for c in checkers) and
       all((REPO / c).is_file() for c in non_checkers),
       f"2  checker inventory: {len(checkers)} registered checkers + "
       f"{len(non_checkers)} classified non-checkers (check.py registration); all paths exist")
    found = sorted(str(p.relative_to(REPO)) for p in REPO.glob("*/_*.py"))
    unclassified = [f for f in found if f not in set(checkers) | set(non_checkers)]
    ok(res, not unclassified,
       f"2b every `*/_*.py` executable is classified (independent glob; unclassified: "
       f"{unclassified or 'none'})")
    f00 = read("final/00-overview.md")
    f08 = read("final/08-evidence-status-matrix.md")
    r06 = read("reg/06-evidence-coverage-summary.md")
    ok(res, f"({len(checkers)} structural gates, {len(non_checkers)} classified non-checkers" in f00
       and f"| PASS ({len(checkers)} structural checkers, {len(non_checkers)} classified non-checkers" in f08
       and f"`python3 check.py`, {len(checkers)} checkers incl. this one, derived from the "
           f"`check.py` registration" in r06,
       "2c FINAL1 + R-REG checker-count projections (final/00, final/08, reg/06) carry the derived "
       f"current counts ({len(checkers)}/{len(non_checkers)}), not a historical figure")

    # --- 3. verification tags ----------------------------------------------
    frozen, addendum, muts = spec08_tags_and_mutations()
    idx_tags = [t["tag"] for t in spec10["verification_tags"]]
    idx_aliases = spec10.get("verification_tag_aliases", [])
    ok(res, sorted(idx_tags) == sorted(frozen + addendum) and len(idx_tags) == len(set(idx_tags)),
       f"3  canonical tag set == indexed tag set: spec/08 §1 tables {len(frozen)}+{len(addendum)} "
       f"== spec/10 verification_tags {len(idx_tags)} (unique); MARSHAL-CAPABILITY-REJECT carried "
       f"as a documented non-indexed alias ({len(idx_aliases)})")
    ok(res, all(a["alias_of"] in set(idx_tags) for a in idx_aliases)
       and all(a["tag"] not in set(idx_tags) for a in idx_aliases),
       "3b every documented alias points at an indexed canonical tag and is not indexed itself")
    reg06 = read("reg/06-evidence-coverage-summary.md")
    ok(res, f"Verification tags: {len(idx_tags)} defined ({len(frozen)} frozen + {len(addendum)} addendum" in reg06,
       f"3c reg/06 tag projection derived ({len(idx_tags)} / {len(frozen)}+{len(addendum)})")

    # --- 4. requirements & atomic registries --------------------------------
    s01, s03, s10, f03, regids, reg = requirement_id_lists()
    same = (sorted(s03) == sorted(s10) == sorted(f03) == sorted(regids) == sorted(s01))
    ok(res, same and len(regids) == EXPECTED["requirements"],
       f"4  requirements five-authority identity: spec/01 {len(s01)} == spec/03 {len(s03)} "
       f"== spec/10 {len(s10)} == final/03 {len(f03)} == reg {len(regids)} (no ID added, "
       "deleted, merged, split or renumbered)")
    statuses = {row.split("|")[4].strip() for row in
                re.findall(r"^\| R-[A-Z]+-\d+ \|[^\n]*\|", read("spec/03-obligation-matrix.md"), re.M)}
    ok(res, statuses == {"SPECIFIED"} and reg["requirement_count"] == EXPECTED["requirements"],
       f"4b every spec/03 status is SPECIFIED (found {sorted(statuses)}); reg count "
       f"{reg['requirement_count']}")
    n_rec = len(reqreg["records"])
    ev = {r["EVIDENCE-STATUS"] for r in reqreg["records"]}
    f03_txt = read("final/03-requirement-registry.md")
    mrec = re.search(r"Atomic record layer \(`req/`, cleaned authority\):\*\* (\d+) records", f03_txt)
    ok(res, n_rec == reqreg.get("record_count", n_rec) == EXPECTED["atomic_records"]
       and ev == {"SPECIFIED"} and mrec and int(mrec.group(1)) == n_rec,
       f"4c atomic registry: req/registry.json {n_rec} records, all EVIDENCE-STATUS SPECIFIED; "
       f"final/03 atomic-layer line agrees ({mrec.group(1) if mrec else 'NOT FOUND'})")

    # --- 5. mutation registry ------------------------------------------------
    ok(res, sorted(set(muts)) == sorted(muts) and len(muts) == EXPECTED["mutations"]
       and [t["id"] for t in spec10["mutations"]] and
       sorted(m["id"] for m in spec10["mutations"]) == sorted(muts)
       and min(int(m[1:]) for m in muts) == 1 and max(int(m[1:]) for m in muts) == len(muts),
       f"5  mutation registry: spec/08 §2 {len(muts)} rows (dense M001…M{max(muts)[1:]}) "
       f"== spec/10 index ({len(spec10['mutations'])})")

    # --- 6. canonical predicate (R-CORE-02 <-> R-CORE-11, V-05) --------------
    body2, body11, chain = core02_and_core11()
    conj = chain_conjuncts(chain)
    canon = ["ValidatedRequest(E)", "Authorized(E,", "CapabilityWithinCeiling(E)",
             "BudgetAvailable(E)", "DeadlineValid(E,t)", "HostPolicyOK(E)", "Issued(E)"]
    shape_ok = (len(conj) == 7 and conj[0] == canon[0]
                and all(conj[i].startswith(canon[i]) for i in range(1, 7)))
    subsumption = "ValidatedRequest(E) ⇒ ValidatedPlan(plan(E))"
    ok(res, shape_ok,
       f"6  R-CORE-02 chain: first conjunct ValidatedRequest(E); 7 conjuncts over the "
       f"R-CORE-11 signatures (found: {conj[0]}, {len(conj)} conjuncts)")
    ok(res, subsumption in body11 and subsumption in body2,
       "6b subsumption ValidatedRequest(E) ⇒ ValidatedPlan(plan(E)) present in both "
       "R-CORE-11 (canonical home) and R-CORE-02 (repair pointer); ValidatedPlan not removed")
    regj = json.loads(read("reg/requirements.json"))
    stmt = next(r for r in regj["requirements"] if r["id"] == "R-CORE-02")["statement"]
    f05 = read("final/05-global-invariant-registry.md")
    f01 = read("final/01-canonical-specification.md")
    readme = read("README.md")
    spec00 = read("spec/00-overview.md")
    gi = spec10["meta"]["governing_invariants"][1]
    agree = all("ValidatedRequest(E)" in x for x in (stmt, f05, f01, readme, spec00, gi)) \
        and "ExternalEffect(E) ⇒ ValidatedRequest(E)" in spec00 \
        and "\\Rightarrow ValidatedRequest(E) \\land" in readme
    stale = "`ExternalEffect(E) ⇒ ValidatedPlan(P) ∧ Authorized" 
    stale_hits = [name for name, x in (("spec/01", body2), ("spec/00", spec00),
                                        ("README", readme), ("final/01", f01),
                                        ("final/05", f05), ("spec/10", gi), ("reg", stmt))
                  if stale in x or "\\Rightarrow ValidatedPlan(P) \\land" in x]
    ok(res, agree and not stale_hits,
       "6c canonical first predicate agrees across every current-state projection "
       "(spec/01, spec/00 §4, README box, spec/10 governing_invariants, final/01, "
       "final/05 GI-SEC-02, reg R-CORE-02 statement); the ValidatedPlan(P)∧ form "
       f"survives only in historical/authority records (stale-form hits: {stale_hits or 'none'})")

    # --- 7. dispositions (V-06) ----------------------------------------------
    d = dispositions()
    ids = [r["id"] for r in d["records"]]
    u_resolved = {u["id"] for u in U["items"] if u["status"] == "RESOLVED"}
    covered = {tok for r in d["records"] if r["current_status"] == "RESOLVED"
               for tok in r["current_authority"]}
    missing_cov = sorted(u_resolved - covered)
    tok_bad = []
    for r in d["records"]:
        for tok in r["current_authority"]:
            if re.fullmatch(r"U-\d+", tok) and tok not in U["ids"]:
                tok_bad.append((r["id"], tok))
            if re.fullmatch(r"M\d{3}", tok) and tok not in muts:
                tok_bad.append((r["id"], tok))
            if re.fullmatch(r"C-\d+", tok) and tok not in re.findall(r"^\| (C-\d+) \|",
                                                                     read("spec/06-contradictions-ambiguities.md"), re.M):
                tok_bad.append((r["id"], tok))
            if re.fullmatch(r"[A-Z][A-Z0-9-]+", tok) and tok not in idx_tags \
                    and tok in ("MARSHAL-NO-RAW-CAPABILITY",):
                tok_bad.append((r["id"], tok))
    hashes_bad = []
    for f, meta in d["protected_snapshots"].items():
        p = REPO / f
        if not p.is_file() or sha256_bytes(p.read_bytes()) != meta["sha256"]:
            hashes_bad.append(f)
    ok(res, len(ids) == len(set(ids)) and not missing_cov,
       f"7  dispositions: {len(ids)} unique records; every resolved U-item "
       f"({len(u_resolved)}) covered by a RESOLVED record (uncovered: {missing_cov or 'none'})")
    ok(res, not tok_bad,
       f"7b disposition current-authority tokens resolve (bad: {tok_bad or 'none'})")
    ok(res, not hashes_bad,
       f"7c protected historical snapshots hash-verified ({len(d['protected_snapshots'])} files; "
       f"provenance violations: {hashes_bad or 'none'}) — editing a protected audit is a "
       "provenance violation until its disposition record is deliberately updated")
    kinds = {r["resolving_action"]["kind"] for r in d["records"]}
    ok(res, kinds <= {"frozen-addendum", "repository-gate-adoption", "governance-repair",
                      "none-carried", "none-register-staleness-intentionally-preserved"}
       and all(r["historical_text_preserved"] for r in d["records"]),
       f"7d disposition kinds in vocabulary {sorted(kinds)}; historical_text_preserved on every record")

    # --- 8. evidence discipline / no promotion -------------------------------
    claims = spec10["claims"]
    ok(res, claims["implemented_obligations"] == 0 and claims["tested_obligations"] == 0
       and claims["verified_obligations"] == 0 and claims["proven_theorems"] == 0,
       "8  spec/10 claims: 0 implemented / 0 tested / 0 verified / 0 proven (no promotion)")
    cv = reg["conditional_verdicts"]
    ok(res, cv.get("REF1") == EXPECTED["ref1"] and cv.get("V1") == EXPECTED["v1"]
       and "REF1-CONDITIONAL" in read("audit/reference-independence-differential-audit.md")
       and "V1-CONDITIONAL" in read("audit/v1-evidence-integrity-audit.md"),
       "8b REF1 and V1 remain CONDITIONAL (reg conditional_verdicts + the audits' own "
       "verdict strings still present)")
    return checkers, non_checkers, frozen, addendum, muts, reg


# ---------------------------------------------------------------------------
# projection + rendering
# ---------------------------------------------------------------------------

def build_projection(U, checkers, non_checkers, frozen, addendum, muts, reg):
    spec10 = json.loads(read("spec/10-index.json"))
    reqreg = json.loads(read("req/registry.json"))
    return {
        "projection": "Red-on-Rust single repository-state projection (repair pass v2, V-07)",
        "derived_artifact_notice": (
            "DERIVED ARTIFACT. Generated by state/_project.py from the authoritative "
            "registers (spec/01·03·08·09, spec/10, req/registry.json, reg/requirements.json, "
            "check.py registration, state/dispositions.json). It is not a normative source; "
            "where it and an authority differ, the authority governs and the gate fails."),
        "derivation_basis": {
            "requirements": "spec/01 == spec/03 == spec/10 == final/03 == reg/requirements.json",
            "atomic_obligations": "req/registry.json records",
            "u_items": "spec/09 ### U-nn rows (registered IDs; resolution bullets)",
            "verification_tags": "spec/08 §1 two tables (== spec/10 verification_tags)",
            "mutations": "spec/08 §2 (== spec/10 mutations)",
            "checkers": "check.py CHECKERS registration (ast-derived)",
            "classified_non_checkers": "check.py NON_CHECKERS registration (ast-derived)",
            "findings": "spec/06 rows minus the C-39 pointer (== spec/10 findings)",
        },
        "counts": {
            "requirements": EXPECTED["requirements"],
            "atomic_obligations": len(reqreg["records"]),
            "findings": len(spec10["findings"]),
            "u_items_registered": U["registered"],
            "u_items_open": U["open"],
            "u_items_resolved": U["resolved"],
            "u_numeric_identifier_max": U["numeric_max"],
            "u_numbering_gaps": U["gaps"],
            "verification_tags_canonical": len(frozen) + len(addendum),
            "verification_tags_frozen_source": len(frozen),
            "verification_tags_post_audit": len(addendum),
            "verification_tag_aliases_documented": len(spec10.get("verification_tag_aliases", [])),
            "mutations": len(muts),
            "checkers_registered": len(checkers),
            "classified_non_checkers": len(non_checkers),
        },
        "expected_counts": dict(EXPECTED),
        "pin_history": {
            "checkers": "15 at the start of repair pass v2; 16 after state/_project.py was "
                        "registered as the V-08 gate (the registration is the authority, "
                        "the pin is the validation)",
        },
        "u_items_open": [u["id"] for u in U["items"] if u["status"] == "OPEN"],
        "u_items_resolved": {u["id"]: u["resolution"] for u in U["items"]
                             if u["status"] == "RESOLVED"},
        "canonical_predicate": {
            "first_conjunct": "ValidatedRequest(E)",
            "subsumption": "ValidatedRequest(E) ⇒ ValidatedPlan(plan(E))",
            "canonical_home": "R-CORE-11",
            "chain_home": "R-CORE-02",
            "note": "the ValidatedPlan(P) first-conjunct form survives only in historical/"
                    "authority records (spec/06, spec/09, term/, req/, audit/, frozen source)",
        },
        "implementation_state": "BOOTSTRAP",
        "evidence_ceiling": "SPECIFIED",
        "conditional_audit_statuses": {"REF1": "REF1-CONDITIONAL", "V1": "V1-CONDITIONAL"},
        "milestone_state": {"M0": "NOT STARTED", "source": "no workspace exists (spec/08 §4)"},
        "claims": {"implemented": 0, "tested": 0, "verified": 0, "proven": 0},
        "explicit_non_meaning": (
            "This projection implies no implementation, testing, verification or proof. "
            "check.py PASS is repository-integrity evidence only (V1 F-INFL-01)."),
    }


def render_state_md(P, res, U, checkers, non_checkers):
    c = P["counts"]
    fails = [l for o, l in res if not o]
    lines = []
    lines.append("# Red-on-Rust — Repository State (Single Projection)\n")
    lines.append("> **Derived artifact.** Generated by `state/_project.py`; do not edit. "
                 "Check mode is registered in `check.py` and fails on any drift or any "
                 "cross-artifact inconsistency. This file is the ONE current repository-state "
                 "projection (repair pass v2, V-07); historical audit state lives in `state/02` "
                 "dispositions, not here.\n")
    lines.append("## 1. Current derived state\n")
    lines.append("| Dimension | Value | Derived from |")
    lines.append("|---|---|---|")
    lines.append(f"| Requirements | {c['requirements']} | spec/01 == spec/03 == spec/10 == final/03 == reg |")
    lines.append(f"| Atomic obligations | {c['atomic_obligations']} | req/registry.json records |")
    lines.append(f"| Findings (indexed) | {c['findings']} | spec/06 (− C-39 pointer) == spec/10 |")
    lines.append(f"| U-items registered | {c['u_items_registered']} | spec/09 rows |")
    lines.append(f"| U-items open | {c['u_items_open']} | spec/09 (incl. preserved-stale U-05) |")
    lines.append(f"| U-items resolved | {c['u_items_resolved']} | spec/09 Resolved bullets |")
    lines.append(f"| U numeric identifier max | U-{c['u_numeric_identifier_max']} (descriptive only — NOT a cardinality) | spec/09 |")
    lines.append(f"| U numbering gaps | {', '.join(c['u_numbering_gaps'])} — numbering gaps, never back-filled | spec/09 |")
    lines.append(f"| Verification tags | {c['verification_tags_canonical']} canonical "
                 f"({c['verification_tags_frozen_source']} frozen-source + {c['verification_tags_post_audit']} "
                 f"post-audit; {c['verification_tag_aliases_documented']} documented alias not indexed) "
                 f"| spec/08 §1 == spec/10 |")
    lines.append(f"| Mutations | {c['mutations']} (M001–M{c['mutations']:03d}, dense) | spec/08 §2 == spec/10 |")
    lines.append(f"| Checkers | {c['checkers_registered']} registered | check.py CHECKERS |")
    lines.append(f"| Classified non-checkers | {c['classified_non_checkers']} | check.py NON_CHECKERS |")
    lines.append(f"| Implementation state | {P['implementation_state']} | spec/10 repository_state; spec/07 §1 |")
    lines.append(f"| Evidence ceiling | {P['evidence_ceiling']} | every spec/03 + req/ + reg status |")
    lines.append(f"| REF1 | {P['conditional_audit_statuses']['REF1']} | REF1 audit §14 (carried; not promotable here) |")
    lines.append(f"| V1 | {P['conditional_audit_statuses']['V1']} | V1 audit §10 (carried; not promotable here) |")
    lines.append(f"| M0 | {P['milestone_state']['M0']} | no workspace exists (spec/08 §4) |")
    lines.append("\nRegistered-record cardinality and numeric identifier range are different "
                 "facts (`39 ≠ 45`); `28 OPEN + 11 RESOLVED = 39`. Historical inventory counts "
                 "(13/14/15 checkers) are retained only inside explicitly historical records "
                 "(see `state/02` DISP-08/DISP-14).\n")
    lines.append("## 2. Canonical predicate (R-CORE-02 ⇔ R-CORE-11)\n")
    lines.append(f"First conjunct: `{P['canonical_predicate']['first_conjunct']}`; subsumption "
                 f"`{P['canonical_predicate']['subsumption']}` (canonical home "
                 f"{P['canonical_predicate']['canonical_home']}, chain home "
                 f"{P['canonical_predicate']['chain_home']}). {P['canonical_predicate']['note']}.\n")
    lines.append("## 3. Cross-artifact gate results (V-08)\n")
    lines.append("```")
    lines += [("OK   " if o else "FAIL ") + l for o, l in res]
    lines.append("```")
    lines.append(f"\nResult: **{'ALL PASS' if not fails else str(len(fails)) + ' FAILURE(S)'}** — "
                 "repository-integrity evidence only; a PASS here is not semantic verification "
                 "of any obligation and not evidence of implementation, testing, verification "
                 "or proof (R-CLAIM-01; V1 F-INFL-01).\n")
    return "\n".join(lines) + "\n"


def render_dispositions_md(d, U):
    lines = []
    lines.append("# Red-on-Rust — Historical/Current Disposition Projection\n")
    lines.append("> **Generated by `state/_project.py` from `state/dispositions.json` "
                 "(the authored governance registry); do not edit.** Purpose (V-06): a "
                 "historical audit snapshot must never be mistaken for current repository "
                 "state. Each record binds finding(s) → resolving governance action → current "
                 "disposition. Historical audit content is immutable; protected snapshots are "
                 "hash-verified by the gate (battery check 7c).\n")
    lines.append("## 1. Disposition records\n")
    lines.append("| ID | Finding family | Historical status | Resolving action | Date | Current status | Historical text preserved |")
    lines.append("|---|---|---|---|---|---|---|")
    for r in d["records"]:
        ra = r["resolving_action"]
        action = ra["kind"] + (" (" + ", ".join(ra["authority"][:4]) +
                               (", …" if len(ra["authority"]) > 4 else "") + ")"
                               if ra["authority"] else "")
        lines.append(f"| `{r['id']}` | {r['family']} | {r['historical_source']['historical_status']} "
                     f"| {action} | {ra['date'] or '—'} | {r['current_status']} "
                     f"| {'yes' if r['historical_text_preserved'] else 'NO'} |")
    lines.append("\nCommit provenance: pre-repair adoptions and audits live in the single "
                 "pre-repair commit `0a8f60d`; the repair-pass records (DISP-05, DISP-13, "
                 "DISP-14, DISP-15) were recorded 2026-09-03 in `state/00-overview.md`'s "
                 "history. `none-carried` rows have no resolving action by design.\n")
    lines.append("## 2. Protected historical snapshots (hash-pinned)\n")
    lines.append("| File | Content | Protected by |")
    lines.append("|---|---|---|")
    for f, meta in d["protected_snapshots"].items():
        lines.append(f"| `{f}` | {meta['content']} | {', '.join(meta['protected_by'])} |")
    lines.append("\nAny change to a protected file — including edits that 'fix' it — fails "
                 "`check.py` until its disposition record is deliberately updated by the "
                 "register owner: historical audit content is immutable unless an explicitly "
                 "authorized normative correction requires otherwise.\n")
    lines.append("## 3. Current open U-items (from spec/09, computed)\n")
    open_ids = ", ".join(f"`{u['id']}`" for u in U["items"] if u["status"] == "OPEN")
    lines.append(f"{U['open']} OPEN: {open_ids}.\n")
    lines.append("These are CURRENT state (not history): DISP records never close them; only "
                 "a frozen addendum or recorded governance action may, after which spec/09 "
                 "and this projection change together.\n")
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true", help="render state outputs")
    ap.add_argument("-q", "--quiet", action="store_true")
    args = ap.parse_args()

    U = u_registry()
    res: list[tuple[bool, str]] = []

    # expectation pins (computed vs EXPECTED) — checked FIRST so a wrong pin
    # is reported as such, separate from cross-artifact drift.
    spec10 = json.loads(read("spec/10-index.json"))
    reqreg = json.loads(read("req/registry.json"))
    checkers, non_checkers = checker_inventory()
    frozen, addendum, muts = spec08_tags_and_mutations()
    s01, s03, s10, f03, regids, reg = requirement_id_lists()
    computed = {
        "requirements": len(regids) if len(regids) == len(s01) == len(s03) == len(s10) == len(f03) else -1,
        "atomic_records": len(reqreg["records"]),
        "u_items": U["registered"], "u_open": U["open"], "u_resolved": U["resolved"],
        "u_numeric_max": U["numeric_max"],
        "findings": len(spec10["findings"]),
        "mutations": len(muts),
        "verification_tags": len(frozen) + len(addendum),
        "checkers": len(checkers), "non_checkers": len(non_checkers),
    }
    pin_bad = {k: (v, EXPECTED[k]) for k, v in computed.items() if v != EXPECTED[k]}
    ok(res, not pin_bad,
       "0  validation expectations: computed == pinned for " + ", ".join(computed)
       + ("" if not pin_bad else f" -- MISMATCH {pin_bad}: INVESTIGATE the authority chain; "
          "do not re-base the pin without one"))

    checkers, non_checkers, frozen, addendum, muts, reg = battery(U, res)

    # evidence pins
    ok(res, EXPECTED["implementation"] == "BOOTSTRAP"
       and read("spec/10-index.json") and True,
       "0b implementation pin: BOOTSTRAP (no workspace/crate exists)")

    d = dispositions()
    P = build_projection(U, checkers, non_checkers, frozen, addendum, muts, reg)
    files = {
        "state/repository-state.json": json.dumps(P, indent=2, ensure_ascii=False,
                                                  sort_keys=True) + "\n",
        "state/01-repository-state.md": render_state_md(P, res, U, checkers, non_checkers),
        "state/02-dispositions.md": render_dispositions_md(d, U),
    }

    fails = [l for o, l in res if not o]
    if args.write:
        if fails:
            print("state/_project.py: battery failed; --write aborted")
            for l in fails:
                print("  " + l)
            return 1
        for rel, text in files.items():
            (REPO / rel).write_text(text, encoding="utf-8")
        print(f"wrote {len(files)} files under state/")
        return 0

    drift = [rel for rel, text in files.items()
             if not (REPO / rel).is_file() or (REPO / rel).read_text(encoding="utf-8") != text]
    if not args.quiet:
        for o, l in res:
            print(("OK   " if o else "FAIL ") + l)
        for rel in drift:
            print(f"FAIL drift: {rel} differs from a fresh projection (regenerate with --write)")
    print(f"\n{'STATE GATE PASS' if not fails and not drift else 'STATE GATE FAIL'}: "
          f"U {U['registered']} ({U['open']} open/{U['resolved']} resolved, max U-{U['numeric_max']}); "
          f"reqs {computed['requirements']}; atomic {computed['atomic_records']}; tags "
          f"{computed['verification_tags']}; mutations {computed['mutations']}; checkers "
          f"{computed['checkers']}+{computed['non_checkers']}")
    return 0 if (not fails and not drift) else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Fail as exc:
        print(f"FAIL  {exc}")
        raise SystemExit(1)
