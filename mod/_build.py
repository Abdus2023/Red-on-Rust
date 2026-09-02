#!/usr/bin/env python3
"""Generator + consistency checker for the semantic-module split (mod/).

Reads:  mod/_ownership.py           (the ownership map — single source of truth)
        spec/03-obligation-matrix.md (canonical obligation short texts + provenance)
        spec/08-verification-mapping.md (frozen tags, mutation registry, milestone gates)
        spec/07-implementation-mapping.md (M0 workspace row)
        req/registry.json            (545 atomic records)
        mod/NN-*.md                  (the 17 hand-written module files)

Writes (--write): mod/18-ownership-matrix.md, mod/19-index.json

Checks (always, error = non-zero exit):
  1. R_OWNER partitions the 148 obligations of spec/03 (total, overlap-free).
  2. REQ records partition the 545 atomic records by parent-obligation propagation;
     every record with 0 or 2 cited parents is placed explicitly in REQ_OVERRIDE,
     and REQ_OVERRIDE contains exactly those records.
  3. All cross-reference and duplication endpoints exist; duplication marks (D-NN)
     are symmetric: every endpoint's module file mentions the D-NN id; the canonical
     endpoint's file marks it "(D-NN canonical)".
  4. Every module file carries the required 13 fields in order, plus
     CROSS-REFERENCES (schema: mod/00-overview.md §6).
  5. The REQUIREMENTS table of each module file lists exactly the obligations that
     module owns (row first cells `| R-…`), and no other module file lists them.
  6. Generated files (when present) are up to date with the map (checked in --check
     mode by regenerating and comparing).
"""

import json
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MOD = ROOT / "mod"
sys.path.insert(0, str(MOD))
import _ownership as O  # noqa: E402

REQUIRED_FIELDS = [
    "SECTION-ID", "TITLE", "PURPOSE", "NORMATIVE-CONTENT", "NON-NORMATIVE-CONTENT",
    "INPUTS", "OUTPUTS", "DEPENDENCIES", "INVARIANTS", "REQUIREMENTS",
    "SECURITY-BOUNDARY", "VERIFICATION-OBLIGATIONS", "SOURCE-PROVENANCE",
    "CROSS-REFERENCES",
]

R_RE = re.compile(r"\| (R-[A-Z]+-\d+) \|")
REQ_RE = re.compile(r"REQ-([A-Z]+)-(\d+)")


def parse_obligations():
    """spec/03 rows -> {R-ID: (short, provenance)}."""
    out = {}
    for line in (ROOT / "spec/03-obligation-matrix.md").read_text().splitlines():
        m = R_RE.match(line.strip())
        if m:
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            rid, short, prov = cells[0], cells[1], cells[2]
            assert len(cells) == 6, f"bad spec/03 row: {rid}"
            out[rid] = (short, prov)
    return out


def parse_req_records():
    d = json.loads((ROOT / "req/registry.json").read_text())
    return d["records"]


def req_ownership(records):
    """REQ-ID -> MOD per parent-obligation propagation + explicit overrides."""
    owner = {}
    errors = []
    for r in records:
        rid = r["REQ-ID"]
        parents = list(dict.fromkeys(re.findall(r"R-[A-Z]+-\d+", r["SOURCE"])))
        if len(parents) == 1:
            owner[rid] = O.R_OWNER[parents[0]]
        elif rid in O.REQ_OVERRIDE:
            owner[rid] = O.REQ_OVERRIDE[rid]
        else:
            errors.append(f"record {rid} has {len(parents)} parents and no override")
    overridden = set(O.REQ_OVERRIDE)
    special = {r["REQ-ID"] for r in records
               if len(list(dict.fromkeys(re.findall(r"R-[A-Z]+-\d+", r["SOURCE"])))) != 1}
    if overridden != special:
        errors.append(f"REQ_OVERRIDE/special mismatch: extra={sorted(overridden - special)} "
                      f"missing={sorted(special - overridden)}")
    return owner, errors


def runs(req_ids):
    """Collapse REQ ids to per-area runs: ['REQ-CAP-001…003', 'REQ-CAP-005']…"""
    by_area = defaultdict(list)
    for rid in req_ids:
        m = REQ_RE.fullmatch(rid)
        by_area[m.group(1)].append(int(m.group(2)))
    parts = []
    for area in sorted(by_area):
        ns = sorted(by_area[area])
        start = prev = ns[0]
        for n in ns[1:]:
            if n == prev + 1:
                prev = n
            else:
                parts.append(_fmt_run(area, start, prev))
                start = prev = n
        parts.append(_fmt_run(area, start, prev))
    return parts


def _fmt_run(area, a, b):
    return f"REQ-{area}-{a:03d}" if a == b else f"REQ-{area}-{a:03d}…{b:03d}"


def requirements_table_ids(text):
    """R-IDs listed as first cell of a table row inside the REQUIREMENTS section."""
    sec = text.split("## REQUIREMENTS", 1)
    if len(sec) != 2:
        return None
    body = re.split(r"\n## ", sec[1], 1)[0]
    return sorted(set(re.findall(r"^\| (R-[A-Z]+-\d+) \|", body, re.M)))


def check_module_files(errors):
    files = {}
    for mod_id, domain, title, crate, fname in O.MODULES:
        p = MOD / fname
        if not p.exists():
            errors.append(f"missing module file {fname}")
            continue
        text = p.read_text()
        files[mod_id] = text
        # 4. required fields in order
        heads = re.findall(r"^## (.+)$", text, re.M)
        heads = [h.split("`")[0].strip() for h in heads]
        if heads[: len(REQUIRED_FIELDS)] != REQUIRED_FIELDS:
            errors.append(f"{fname}: field header order mismatch: {heads[:len(REQUIRED_FIELDS)]}")
        # 5. REQUIREMENTS table == owned set
        want = sorted(r for r, m in O.R_OWNER.items() if m == mod_id)
        got = requirements_table_ids(text)
        if got is None:
            errors.append(f"{fname}: no REQUIREMENTS section")
        else:
            if set(got) != set(want):
                errors.append(
                    f"{fname}: REQUIREMENTS table mismatch: "
                    f"missing={sorted(set(want) - set(got))} extra={sorted(set(got) - set(want))}")
        # section id field content
        if f"`{mod_id}`" not in text.split("## SECTION-ID", 1)[1].split("## ", 1)[0]:
            errors.append(f"{fname}: SECTION-ID does not contain {mod_id}")
    # 3b. duplication marks symmetric
    for did, kind, endpoints, canonical, note in O.DUPLICATES:
        for rid in endpoints:
            mod = O.R_OWNER.get(rid)
            if mod is None or mod not in files:
                errors.append(f"{did}: endpoint {rid} has no owner file")
                continue
            if did not in files[mod]:
                errors.append(f"{did}: not mentioned in {O.FILE_OF[mod]} (endpoint {rid})")
        cmod = O.R_OWNER.get(canonical)
        if cmod in files and f"({did} canonical)" not in files[cmod]:
            errors.append(f"{did}: canonical mark missing in {O.FILE_OF[cmod]}")
    return files


def check_map(errors):
    obl = parse_obligations()
    if set(obl) != set(O.R_OWNER):
        errors.append(f"obligation partition mismatch: uncovered={sorted(set(obl) - set(O.R_OWNER))} "
                      f"unknown={sorted(set(O.R_OWNER) - set(obl))}")
    # cross-ref sanity
    mods = {m[0] for m in O.MODULES}
    for rid, xs in O.R_XREF.items():
        if rid not in O.R_OWNER:
            errors.append(f"xref key {rid} not an obligation")
        for m, _why in xs:
            if m not in mods:
                errors.append(f"xref {rid} -> unknown module {m}")
            elif rid in O.R_OWNER and m == O.R_OWNER[rid]:
                errors.append(f"xref {rid} points at its own owner {m}")
    for did, kind, endpoints, canonical, _note in O.DUPLICATES:
        for rid in endpoints:
            if rid not in O.R_OWNER:
                errors.append(f"{did}: unknown endpoint {rid}")
        if canonical not in endpoints:
            errors.append(f"{did}: canonical {canonical} not among endpoints")
        owners = {O.R_OWNER[r] for r in endpoints}
        if len(owners) < 2 and did != "D-10":
            errors.append(f"{did}: intra-module duplication {owners} without explicit allowance")
    for tag, m in O.TAG_MODULE.items():
        if m not in mods:
            errors.append(f"tag {tag} -> unknown module {m}")
    for mut, m in O.MUTANT_MODULE.items():
        if m not in mods:
            errors.append(f"mutant {mut} -> unknown module {m}")
    for mm, ms in O.MILESTONE_MODULE.items():
        for m in ms:
            if m not in mods:
                errors.append(f"milestone {mm} -> unknown module {m}")
    return obl


# ---------------------------------------------------------------------------
# Generation
# ---------------------------------------------------------------------------

def parse_spec08():
    text = (ROOT / "spec/08-verification-mapping.md").read_text()
    tags = {}   # tag -> (obligations, evidence)
    for m in re.finditer(r"^\| `([A-Z][A-Z-]+)` \| ([^|]+) \| ([^|]+) \|", text, re.M):
        tags[m.group(1)] = (m.group(2).strip(), m.group(3).strip())
    mutants = {}  # M0NN -> (defect, obligations)
    for m in re.finditer(r"^\| (M0\d\d) \| ([^|]+) \| ([^|]+) \|$", text, re.M):
        mutants[m.group(1)] = (m.group(2).strip(), m.group(3).strip())
    milestones = {}  # M<n> -> acceptance
    for m in re.finditer(r"^\| (M\d{1,2}) \| ([^|]+) \|$", text, re.M):
        milestones[m.group(1)] = m.group(2).strip()
    return tags, mutants, milestones


def generate_matrix(obl, req_owner):
    dup_of = defaultdict(list)  # rid -> [(did, canonical)]
    for did, kind, endpoints, canonical, note in O.DUPLICATES:
        for rid in endpoints:
            dup_of[rid].append((did, canonical))
    lines = []
    A = lines.append
    A("# mod/18 — Obligation Ownership Matrix (GENERATED — do not edit; edit `mod/_ownership.py` and run `python3 mod/_build.py --write`)")
    A("")
    A("Total, duplicate-free partition of the 148 canonical obligations (`spec/03`) and of the")
    A("545 atomic records (`req/`) over the 17 semantic modules, per the ownership rules in")
    A("`mod/00-overview.md` §2. Every obligation below is `SPECIFIED` (status ladder `spec/00` §2).")
    A("Cross-reference column lists other modules the obligation binds (reasons abbreviated;")
    A("full cross-reference prose lives in the module files' CROSS-REFERENCES sections).")
    A("The provenance column quotes `spec/03` verbatim; where `req/00-method.md` §5.1 corrected")
    A("an anchor, the corrected range is carried in the owning module file's SOURCE-PROVENANCE.")
    A("")
    A("## 1. Obligation partition (148)")
    A("")
    n_obl = 0
    for mod_id, domain, title, crate, fname in O.MODULES:
        owned = sorted(r for r, m in O.R_OWNER.items() if m == mod_id)
        n_obl += len(owned)
        A(f"### {mod_id} — {domain} ({len(owned)} obligations)")
        A("")
        A("| Obligation | Short text (from `spec/03`) | Provenance | Cross-references | Duplication |")
        A("|---|---|---|---|---|")
        for rid in owned:
            short, prov = obl[rid]
            xrefs = ", ".join(f"{m} ({why})" for m, why in O.R_XREF.get(rid, [])) or "—"
            dups = ", ".join(
                f"{d} (canonical statement)" if rid == canon
                else f"{d} (marked restatement — canonical statement {canon}, {O.R_OWNER[canon]})"
                for d, canon in dup_of.get(rid, [])
            ) or "—"
            A(f"| {rid} | {short} | {prov} | {xrefs} | {dups} |")
        A("")
    A(f"**Partition check:** {n_obl} obligations across 17 modules (expected 148).")
    A("")
    A("## 2. Atomic-record partition (545)")
    A("")
    A("| Module | Records | Ranges |")
    A("|---|---|---|")
    n_rec = 0
    for mod_id, domain, _t, _c, _f in O.MODULES:
        ids = sorted(r for r, m in req_owner.items() if m == mod_id)
        n_rec += len(ids)
        A(f"| {mod_id} {domain} | {len(ids)} | {'; '.join(runs(ids))} |")
    A(f"| **total** | **{n_rec}** | |")
    A("")
    A("Placement rule for the 16 records whose registry SOURCE cites zero or two parent")
    A("obligations: explicit assignment in `_ownership.py` (REQ_OVERRIDE) with rationale in the")
    A("receiving module's REQUIREMENTS section; all other records follow their parent obligation.")
    A("")
    A("## 3. Explicit duplication / overlap register (D-01…D-12)")
    A("")
    A("Pairs/triples where the frozen source states the same content more than once. One endpoint")
    A("is the canonical statement; each other endpoint is an explicitly **marked** restatement.")
    A("No normative text exists in two owner's modules unmarked (rule 4, `mod/00-overview.md` §2).")
    A("")
    A("| ID | Kind | Endpoints | Canonical statement | Note |")
    A("|---|---|---|---|---|")
    for did, kind, endpoints, canonical, note in O.DUPLICATES:
        A(f"| {did} | {kind} | {' ⇄ '.join(endpoints)} | {canonical} ({O.R_OWNER[canonical]} "
          f"{O.DOMAIN[O.R_OWNER[canonical]]}) | {note} |")
    A("")
    A("## 4. Verification-obligation tag homes (frozen tag set, `spec/08` §1)")
    A("")
    A("Tags are verified *by* the module whose obligations they cover; coverage attribution and")
    A("reporting is MOD-15's (R-TEST-07), CI consumption MOD-17's (R-TEST-10).")
    A("")
    tags_map, _mut, _mile = parse_spec08()
    A("| Tag | Verifying module | Obligations covered (per `spec/08`) |")
    A("|---|---|---|")
    for tag, mod in sorted(O.TAG_MODULE.items()):
        obls = tags_map.get(tag, ("?", "?"))[0]
        A(f"| `{tag}` | {mod} {O.DOMAIN[mod]} | {obls} |")
    A("")
    A("## 5. Mutation registry map (M001–M018, baseline frozen; registry owned by MOD-16)")
    A("")
    A("| Mutant | Injected defect (per `spec/08`) | Targets | Semantics owner module |")
    A("|---|---|---|---|")
    _t, mutants, _m = parse_spec08()
    for mut in sorted(O.MUTANT_MODULE):
        defect, tgt = mutants.get(mut, ("?", "?"))
        mod = O.MUTANT_MODULE[mut]
        A(f"| {mut} | {defect} | {tgt} | {mod} {O.DOMAIN[mod]} |")
    A("")
    A("## 6. Milestone evidence-gate map (M0–M11; acceptance owned by MOD-17, R-ORDER-02)")
    A("")
    A("| Milestone | Required evidence (per `spec/08` §4) | Modules whose gates bind |")
    A("|---|---|---|")
    _t2, _m2, miles = parse_spec08()
    for mm in sorted(O.MILESTONE_MODULE, key=lambda x: int(x[1:])):
        ev = miles.get(mm, "workspace bootstrap: `cargo check/test/fmt/clippy` pass (spec/07 §4)")
        mods = ", ".join(f"{m} {O.DOMAIN[m]}" for m in O.MILESTONE_MODULE[mm])
        A(f"| {mm} | {ev} | {mods} |")
    A("")
    return "\n".join(lines) + "\n"


def generate_index(obl, req_owner):
    mods = []
    for mod_id, domain, title, crate, fname in O.MODULES:
        owned = sorted(r for r, m in O.R_OWNER.items() if m == mod_id)
        ids = sorted(r for r, mm in req_owner.items() if mm == mod_id)
        mods.append({
            "id": mod_id,
            "domain": domain,
            "title": title,
            "crate": crate,
            "file": fname,
            "obligations": owned,
            "obligation_count": len(owned),
            "record_count": len(ids),
            "record_ranges": runs(ids),
            "cross_references": {r: [m for m, _w in xs] for r, xs in O.R_XREF.items()
                                 if O.R_OWNER.get(r) == mod_id},
            "verification_tags": sorted(t for t, m in O.TAG_MODULE.items() if m == mod_id),
            "mutations_targeted": sorted(m for m, mm in O.MUTANT_MODULE.items() if mm == mod_id),
            "milestone_gates": sorted(mm for mm, ms in O.MILESTONE_MODULE.items() if mod_id in ms),
            "open_items_affecting": sorted(u for u, ms in O.U_AFFECTED.items() if mod_id in ms),
        })
    return {
        "specification": "Red-on-Rust.md",
        "organization": "17 semantic modules, split by architectural responsibility (not document length)",
        "normative_text_home": "spec/01 (obligations), req/ (atomic records); mod/ registers ownership, no normative text is duplicated except as marked in `duplications`",
        "module_count": len(mods),
        "obligation_count": sum(m["obligation_count"] for m in mods),
        "record_count": sum(m["record_count"] for m in mods),
        "evidence_status_of_every_obligation": "SPECIFIED",
        "modules": mods,
        "duplications": [
            {"id": did, "kind": kind, "endpoints": eps, "canonical": canonical, "note": note}
            for did, kind, eps, canonical, note in O.DUPLICATES
        ],
    }


def main():
    write = "--write" in sys.argv
    errors = []
    obl = check_map(errors)
    records = parse_req_records()
    req_owner, req_errors = req_ownership(records)
    errors += req_errors
    check_module_files(errors)
    if len(records) != 545:
        errors.append(f"expected 545 records, found {len(records)}")

    matrix = generate_matrix(obl, req_owner)
    index = json.dumps(generate_index(obl, req_owner), indent=2, ensure_ascii=False) + "\n"

    for path, content in [(MOD / "18-ownership-matrix.md", matrix), (MOD / "19-index.json", index)]:
        if write:
            path.write_text(content)
        elif path.exists() and path.read_text() != content:
            errors.append(f"{path.name} is stale; run `python3 mod/_build.py --write`")
        elif not path.exists() and not write:
            errors.append(f"{path.name} missing; run `python3 mod/_build.py --write`")

    if errors:
        for e in errors:
            print("ERROR:", e)
        print(f"{len(errors)} error(s)")
        return 1
    print("mod/: 0 errors" + (" (generated 18-ownership-matrix.md, 19-index.json)" if write else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
