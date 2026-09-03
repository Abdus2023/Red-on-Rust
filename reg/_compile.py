#!/usr/bin/env python3
"""R-REG — Red-on-Rust Requirements Registry Compiler.

WHAT THIS IS
------------
A registry-*compilation* step: it reads the canonical authorities and emits a
machine-readable requirements registry (`reg/requirements.json`) plus its JSON
schema and the audit reports listed in `reg/00-overview.md`.

It is NOT a requirements-extraction or redesign step. Every field is copied or
mechanically derived from an authoritative input, and the derivation rule is
recorded next to the value (`*_basis`, `*_source` fields). Where no authority
defines a value, the field is empty/null and the gap is *reported*, never
filled in.

AUTHORITY CHAIN (unchanged by this tool)
----------------------------------------
    Red-on-Rust.md  ->  spec/ (cleaned)  ->  final/03 + final/01 (canonical
    registry / canonical statements)  ->  reg/requirements.json (DERIVED)

If any two authorities disagree, or the generated output would disagree with
the canonical registry, this tool exits non-zero. It never picks a value.

MODES
-----
    python3 reg/_compile.py           # check mode (what `python3 check.py` runs):
                                      #   recompile in memory, run the validation
                                      #   battery (22 points), fail on any drift vs reg/*
    python3 reg/_compile.py --write   # render reg/* (after the same battery)

EVIDENCE DISCIPLINE
-------------------
Status is copied from the canonical registry (all 184 `SPECIFIED`). Nothing in
this tool can promote a status: there is no code path that writes any status
other than the one read from `final/03`, and the battery fails if any status
is not in the ladder or differs from the canonical row. Empty
`implementation_targets` / `test_targets` / `evidence` are *absence of
registered artefacts*, not claims. A passing run of this checker is
repository-integrity evidence only (V1 F-INFL-01).
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
sys.path.insert(0, str(REPO / "final"))
sys.path.insert(0, str(REPO / "req"))
import _parse as P  # noqa: E402  (final/_parse.py: cleaned-input parsers)
import _anchors as A  # noqa: E402  (req/_anchors.py: parent-obligation regex)

EXPECTED_COUNT = 184  # spec/00 §3 / final/03 — fails loudly if authority changes
STATUS_LADDER = ["SPECIFIED", "IMPLEMENTED", "TESTED", "VERIFIED", "PROVEN"]
# req/00 rule 4 vocabulary (the repository's canonical normative levels)
LEVEL_VOCAB = ["MUST", "MUST NOT", "SHOULD", "SHOULD NOT", "MAY", "IS",
               "NON-NORMATIVE", "AMBIGUOUS"]
# single-value priority when a compound row carries several levels
LEVEL_PRIORITY = ["MUST", "MUST NOT", "SHOULD", "SHOULD NOT", "MAY", "IS",
                  "NON-NORMATIVE", "AMBIGUOUS"]
IMPACT_ORDER = ["none", "low", "medium", "high", "critical"]
SECURITY_IMPACT_THRESHOLD = {"critical", "high"}

# Evidence-kind predicates: which evidence kinds are required for each status
# promotion. A generic evidence kind MUST NOT be used to claim any status level.
# This is the mechanical enforcement of the status-transition evidence model.
EVIDENCE_KINDS_FOR_STATUS = {
    "IMPLEMENTED": {"source"},  # implementation source files
    "TESTED": {"test"},         # executed test evidence
    "VERIFIED": {"differential", "mutation", "crash-matrix"},  # independent verification
    "PROVEN": {"proof"},        # formal proof artefacts
}
# All valid evidence kinds (for validation)
ALL_EVIDENCE_KINDS = {"source", "test", "differential", "mutation", "crash-matrix",
                      "proof", "repository-integrity-gate"}
# Evidence kinds that can never establish any status promotion
NON_PROMOTING_KINDS = {"repository-integrity-gate"}

REGISTRY_JSON = "reg/requirements.json"
SCHEMA_JSON = "reg/requirements.schema.json"
LEDGER_JSON = "reg/status-transitions.json"

INPUT_FILES = [
    "Red-on-Rust.md",
    "spec/01-canonical-specification.md",
    "spec/03-obligation-matrix.md",
    "spec/10-index.json",
    "final/01-canonical-specification.md",
    "final/03-requirement-registry.md",
    "final/05-global-invariant-registry.md",
    "req/registry.json",
    "dep/10-graph.json",
]


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def sha256_bytes(b: bytes) -> str:
    return "sha256:" + hashlib.sha256(b).hexdigest()


def sha256_file(rel: str) -> str:
    return sha256_bytes((REPO / rel).read_bytes())


def ws(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def md_cell(s: str) -> str:
    """Escape unescaped pipes (req/_validate.py 7d table-integrity rule)."""
    return re.sub(r"(?<!\\)\|", r"\\|", s)


def split_cell(cell: str) -> list[str]:
    if cell.strip() in ("", "—", "-"):
        return []
    return [t.strip() for t in cell.split(",") if t.strip()]


class Fail(Exception):
    pass


# ---------------------------------------------------------------------------
# input loading
# ---------------------------------------------------------------------------

def parse_final03() -> list[dict]:
    rows = []
    for ln in P.read("final/03-requirement-registry.md").split("\n"):
        if not ln.startswith("| R-") or ln.startswith("| R-ID"):
            continue
        cells = [c.strip() for c in re.split(r"(?<!\\)\|", ln.strip())[1:-1]]
        if len(cells) != 8:
            continue  # the per-area count table has 3 cells
        rows.append({"id": cells[0], "short": cells[1], "prov": cells[2],
                     "status": cells[3], "impl": cells[4], "verify": cells[5],
                     "home": cells[6], "cleaned": cells[7]})
    return rows


def parse_final01_chunks() -> tuple[dict, dict]:
    """Return ({rid: (home§, S-nn, status, text)}, {home§: title})."""
    txt = P.read("final/01-canonical-specification.md")
    titles, chunks = {}, {}
    cur, buf, sec = None, [], None
    for ln in txt.split("\n"):
        m = re.match(r"^## (§\d\d) (.*)$", ln)
        if m:
            sec = m.group(1)
            titles[sec] = m.group(2).strip()
        m = re.match(r"^\*\*(R-[A-Z]+-\d+)", ln)
        if m and cur is None:
            cur, buf = m.group(1), [ln]
            continue
        m = re.match(r"^<!-- FINAL1: (R-[A-Z]+-\d+) canonical home; cleaned authority "
                     r"spec/01 (S-\d\d); registry row final/03; status (\w+) -->$", ln)
        if m:
            if cur != m.group(1):
                raise Fail(f"final/01 chunk/marker mismatch: {cur} vs {m.group(1)}")
            chunks[cur] = (sec, m.group(2), m.group(3), "\n".join(buf).strip("\n"))
            cur, buf = None, []
            continue
        if cur is not None:
            buf.append(ln)
    return chunks, titles


def parse_gi_homes() -> dict[str, list[str]]:
    txt = P.read("final/05-global-invariant-registry.md")
    homes: dict[str, list[str]] = collections.defaultdict(list)
    for m in re.finditer(r"^#### (GI-[A-Z]+-\d+)[^\n]*\n(.*?)(?=^#### |\Z)", txt,
                         flags=re.M | re.S):
        h = re.search(r"Definitional home[^:]*:\*\*\s*`?(R-[A-Z]+-\d+)", m.group(2))
        if not h:
            raise Fail(f"final/05 {m.group(1)}: no definitional home parsed")
        homes[h.group(1)].append(m.group(1))
    return homes


def parse_spec03_ids() -> list[str]:
    return [m.group(1) for ln in P.read("spec/03-obligation-matrix.md").split("\n")
            for m in [re.match(r"^\| (R-[A-Z]+-\d+) \|", ln)] if m]


class Inputs:
    def __init__(self):
        self.final03 = parse_final03()
        self.final01, self.titles = parse_final01_chunks()
        self.spec01 = P.parse_spec01()
        self.spec01_text = {rid: t for s in self.spec01.values()
                            for rid, t in s["chunks"] if rid}
        self.spec03_ids = parse_spec03_ids()
        self.spec10 = P.load_spec_index()
        self.spec10_req = {r["id"]: r for r in self.spec10["requirements"]}
        self.req = P.load_registry()
        self.dep = json.loads(P.read("dep/10-graph.json"))
        self.gi = parse_gi_homes()
        self.tags = collections.defaultdict(list)
        for t in self.spec10["verification_tags"]:
            for o in t["obligations"]:
                self.tags[o].append(t["tag"])
        self.mutations = collections.defaultdict(list)
        for m in self.spec10["mutations"]:
            for o in m["kills_evidence_for"]:
                self.mutations[o].append(m["id"])
        # atomic records grouped by parent obligation (req/ SOURCE cite)
        self.atomic = collections.defaultdict(list)
        self.rec_parent = {}
        for rec in self.req["records"]:
            parents = A.parent_obligations(rec["SOURCE"])
            self.rec_parent[rec["REQ-ID"]] = parents
            for p in parents:
                self.atomic[p].append(rec)
        self.hashes = {f: sha256_file(f) for f in INPUT_FILES}


# ---------------------------------------------------------------------------
# derivations (each one mechanical and recorded)
# ---------------------------------------------------------------------------

def levels_in_text(text: str) -> list[str]:
    present = []
    t = text
    for neg, pos in (("MUST NOT", "MUST"), ("SHOULD NOT", "SHOULD")):
        if re.search(r"\b" + neg + r"\b", t):
            present.append(neg)
        t = re.sub(r"\b" + neg + r"\b", " ", t)
        if re.search(r"\b" + pos + r"\b", t):
            present.append(pos)
    if re.search(r"\bMAY\b", t):
        present.append("MAY")
    return sorted(present, key=LEVEL_PRIORITY.index)


NEG_TOKENS = ("MUST NOT", "↛", "⇏", "NEVER")


def negative_tokens(text: str) -> int:
    return sum(text.count(tok) for tok in NEG_TOKENS)


def impact_level(s: str) -> str | None:
    for lv in reversed(IMPACT_ORDER):
        if re.match(r"^\s*" + lv + r"\b", s):
            return lv
    return None


def frozen_lines(prov: str) -> list[str]:
    return re.findall(r"L\d+(?:–\d+)?", prov)


def addendum_of(prov: str) -> str | None:
    m = re.match(r"^addendum \((.*)\)$", prov)
    return m.group(1) if m else None


def build_requirement(I: Inputs, row: dict) -> dict:
    rid = row["id"]
    statement = I.spec01_text[rid]
    home, s_sec, f_status, f_text = I.final01[rid]
    idx = I.spec10_req[rid]
    recs = I.atomic.get(rid, [])

    # normative level -------------------------------------------------------
    present = levels_in_text(statement)
    if present:
        basis = "statement-keyword-scan (spec/01 canonical statement)"
    else:
        present = sorted({r["NORMATIVE-LEVEL"] for r in recs
                          if r["NORMATIVE-LEVEL"] in LEVEL_VOCAB},
                         key=LEVEL_PRIORITY.index)
        if present:
            basis = "atomic-records (req/ NORMATIVE-LEVEL of records citing this obligation)"
        else:
            present = ["MUST"]
            basis = ("declarative-convention (req/00 rule 4 / §31: a frozen obligation stated "
                     "declaratively records MUST); no keyword and no atomic record")
    level = present[0]

    # security classification -----------------------------------------------
    gi_sec = [g for g in I.gi.get(rid, []) if g.startswith("GI-SEC-")]
    impacts = [impact_level(r["SECURITY-IMPACT"]) for r in recs]
    impacts = [i for i in impacts if i]
    max_impact = max(impacts, key=IMPACT_ORDER.index) if impacts else None
    add = addendum_of(row["prov"])
    sec_audit = bool(add and add.startswith("SEC-"))
    sec_basis = []
    if gi_sec:
        sec_basis.append("final/05 GI-SEC definitional home: " + ", ".join(gi_sec))
    if max_impact in SECURITY_IMPACT_THRESHOLD:
        sec_basis.append(f"req/ SECURITY-IMPACT max over atomic records = {max_impact}")
    if sec_audit:
        sec_basis.append(f"frozen addendum from the authority/trust security audit ({add})")
    classified = bool(gi_sec) or max_impact is not None or sec_audit
    security_relevant = bool(sec_basis)

    # provenance --------------------------------------------------------------
    prov = {
        "source_document": "spec/01-canonical-specification.md",
        "source_section": s_sec,
        "source_hash": sha256_bytes(statement.encode("utf-8")),
        "source_document_hash": I.hashes["spec/01-canonical-specification.md"],
        "canonical_home": {"document": "final/01-canonical-specification.md",
                           "section": home,
                           "document_hash": I.hashes["final/01-canonical-specification.md"]},
        "registry_row": {"document": "final/03-requirement-registry.md",
                         "provenance_cell": row["prov"],
                         "document_hash": I.hashes["final/03-requirement-registry.md"]},
        "frozen_source": {"document": "Red-on-Rust.md",
                          "line_ranges": frozen_lines(row["prov"]),
                          "document_hash": I.hashes["Red-on-Rust.md"]},
        "frozen_addendum": add,
    }

    verify_tokens = split_cell(row["verify"])
    return {
        "id": rid,
        "section": home,
        "section_title": I.titles[home],
        "cleaned_section": s_sec,
        "category": rid.split("-")[1],
        "category_basis": "R-AREA-NN identifier scheme (spec/00 §3; final/03 per-area table)",
        "atomic_categories": sorted({r["CATEGORY"] for r in recs}),
        "short_title": row["short"],
        "statement": statement,
        "normative_level": level,
        "normative_levels_present": present,
        "normative_level_basis": basis,
        "negative_guarantee": negative_tokens(statement) > 0,
        "dependencies": list(idx["dependencies"]),
        "dependencies_source": "spec/10-index.json requirements[].dependencies (canonical; "
                               "no R-level dependency is registered)",
        "security_relevant": security_relevant,
        "security_classification": {
            "status": "CLASSIFIED" if classified else "UNCLASSIFIED",
            "gi_sec_homes": gi_sec,
            "atomic_security_impact_max": max_impact,
            "atomic_security_impacts": sorted(set(impacts), key=IMPACT_ORDER.index),
            "security_audit_addendum": sec_audit,
            "basis": sec_basis,
        },
        "global_invariants": list(I.gi.get(rid, [])),
        "implementation_targets": split_cell(row["impl"]),
        "implementation_targets_source": "final/03 Impl→ (== spec/03; normative crate homes per "
                                         "spec/07 — none exists in the repository, spec/07 §1)",
        "test_targets": verify_tokens,
        "test_targets_source": "final/03 Verify→ (== spec/03; spec/08 tags / test obligations — "
                               "repository evidence NONE for every row, final/04)",
        "verification_tags": list(I.tags.get(rid, [])),
        "mutations": list(I.mutations.get(rid, [])),
        "verification_method": row["verify"] if verify_tokens else None,
        "verification_method_source": "final/03 Verify→ cell verbatim (null where the canonical "
                                      "registry defines none)",
        "atomic_verification_methods": sorted({r["VERIFICATION-METHOD"] for r in recs}),
        "evidence": [],
        "status": row["status"],
        "status_source": "final/03 Status (== spec/03; == final/01 marker)",
        "atomic_records": [r["REQ-ID"] for r in recs],
        "related_findings": list(idx["related_findings"]),
        "provenance": prov,
    }


def build_registry(I: Inputs) -> dict:
    reqs = [build_requirement(I, row) for row in I.final03]
    return {
        "registry": "Red-on-Rust machine-readable requirements registry (R-REG)",
        "derived_artifact_notice": (
            "DERIVED ARTIFACT. Generated by reg/_compile.py from the canonical registry "
            "(final/03 <- spec/03) and canonical statements (spec/01, re-homed verbatim in "
            "final/01). It is not a normative source: where this file and the canonical "
            "registry differ, the canonical registry governs and the compiler fails."),
        "authority_chain": ["Red-on-Rust.md", "spec/ (cleaned canonical specification)",
                            "final/03-requirement-registry.md + final/01-canonical-specification.md",
                            "reg/requirements.json (this file, derived)"],
        "status_ladder": STATUS_LADDER,
        "normative_level_vocabulary": LEVEL_VOCAB,
        "evidence_rule": ("A status is promoted only with repository evidence recorded in "
                          "reg/status-transitions.json; empty implementation_targets / "
                          "test_targets / evidence are absence of registered artefacts, never "
                          "a claim. Repository checker PASS is integrity evidence only."),
        "conditional_verdicts": {"REF1": "REF1-CONDITIONAL", "V1": "V1-CONDITIONAL"},
        "sources": {f: I.hashes[f] for f in INPUT_FILES},
        "requirement_count": len(reqs),
        "requirements": reqs,
    }


def render_json(obj) -> str:
    return json.dumps(obj, indent=2, ensure_ascii=False, sort_keys=True) + "\n"


# ---------------------------------------------------------------------------
# JSON schema (+ a small self-contained validator; no third-party dependency)
# ---------------------------------------------------------------------------

def schema() -> dict:
    s = {"type": "string"}
    slist = {"type": "array", "items": s}
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "https://red-on-rust/reg/requirements.schema.json",
        "title": "Red-on-Rust machine-readable requirements registry",
        "type": "object",
        "additionalProperties": False,
        "required": ["registry", "derived_artifact_notice", "authority_chain", "status_ladder",
                     "normative_level_vocabulary", "evidence_rule", "conditional_verdicts",
                     "sources", "requirement_count", "requirements"],
        "properties": {
            "registry": s,
            "derived_artifact_notice": s,
            "authority_chain": slist,
            "status_ladder": {"type": "array", "items": s, "const": STATUS_LADDER},
            "normative_level_vocabulary": slist,
            "evidence_rule": s,
            "conditional_verdicts": {"type": "object", "additionalProperties": False,
                                     "required": ["REF1", "V1"],
                                     "properties": {"REF1": {"const": "REF1-CONDITIONAL"},
                                                    "V1": {"const": "V1-CONDITIONAL"}}},
            "sources": {"type": "object", "additionalProperties": {"type": "string",
                                                                    "pattern": "^sha256:[0-9a-f]{64}$"}},
            "requirement_count": {"type": "integer", "const": EXPECTED_COUNT},
            "requirements": {"type": "array", "minItems": EXPECTED_COUNT,
                             "maxItems": EXPECTED_COUNT, "items": {"$ref": "#/$defs/requirement"}},
        },
        "$defs": {
            "rid": {"type": "string", "pattern": "^R-[A-Z]+-[0-9]{2}$"},
            "hash": {"type": "string", "pattern": "^sha256:[0-9a-f]{64}$"},
            "requirement": {
                "type": "object",
                "additionalProperties": False,
                "required": ["id", "section", "section_title", "cleaned_section", "category",
                             "category_basis", "atomic_categories", "short_title", "statement",
                             "normative_level", "normative_levels_present",
                             "normative_level_basis", "negative_guarantee", "dependencies",
                             "dependencies_source", "security_relevant",
                             "security_classification", "global_invariants",
                             "implementation_targets", "implementation_targets_source",
                             "test_targets", "test_targets_source", "verification_tags",
                             "mutations", "verification_method", "verification_method_source",
                             "atomic_verification_methods", "evidence", "status",
                             "status_source", "atomic_records", "related_findings",
                             "provenance"],
                "properties": {
                    "id": {"$ref": "#/$defs/rid"},
                    "section": {"type": "string", "pattern": "^§[0-9]{2}$"},
                    "section_title": s,
                    "cleaned_section": {"type": "string", "pattern": "^S-[0-9]{2}$"},
                    "category": {"type": "string", "pattern": "^[A-Z]+$"},
                    "category_basis": s,
                    "atomic_categories": slist,
                    "short_title": s,
                    "statement": {"type": "string", "minLength": 1},
                    "normative_level": {"type": "string", "enum": LEVEL_VOCAB},
                    "normative_levels_present": {"type": "array", "minItems": 1,
                                                 "items": {"type": "string", "enum": LEVEL_VOCAB}},
                    "normative_level_basis": s,
                    "negative_guarantee": {"type": "boolean"},
                    "dependencies": {"type": "array", "items": {"$ref": "#/$defs/rid"},
                                     "uniqueItems": True},
                    "dependencies_source": s,
                    "security_relevant": {"type": "boolean"},
                    "security_classification": {
                        "type": "object", "additionalProperties": False,
                        "required": ["status", "gi_sec_homes", "atomic_security_impact_max",
                                     "atomic_security_impacts", "security_audit_addendum",
                                     "basis"],
                        "properties": {
                            "status": {"type": "string", "enum": ["CLASSIFIED", "UNCLASSIFIED"]},
                            "gi_sec_homes": {"type": "array",
                                             "items": {"type": "string", "pattern": "^GI-SEC-[0-9]{2}$"}},
                            "atomic_security_impact_max": {"type": ["string", "null"],
                                                           "enum": IMPACT_ORDER + [None]},
                            "atomic_security_impacts": {"type": "array",
                                                        "items": {"type": "string", "enum": IMPACT_ORDER}},
                            "security_audit_addendum": {"type": "boolean"},
                            "basis": slist,
                        }},
                    "global_invariants": {"type": "array",
                                          "items": {"type": "string", "pattern": "^GI-(SEC|DET|REC)-[0-9]{2}$"}},
                    "implementation_targets": slist,
                    "implementation_targets_source": s,
                    "test_targets": slist,
                    "test_targets_source": s,
                    "verification_tags": slist,
                    "mutations": {"type": "array", "items": {"type": "string", "pattern": "^M[0-9]{3}$"}},
                    "verification_method": {"type": ["string", "null"]},
                    "verification_method_source": s,
                    "atomic_verification_methods": slist,
                    "evidence": {"type": "array", "items": {"$ref": "#/$defs/evidence"}},
                    "status": {"type": "string", "enum": STATUS_LADDER},
                    "status_source": s,
                    "atomic_records": {"type": "array",
                                       "items": {"type": "string", "pattern": "^REQ-[A-Z]+-[0-9]{3}$"}},
                    "related_findings": slist,
                    "provenance": {"$ref": "#/$defs/provenance"},
                },
            },
            "evidence": {
                "type": "object", "additionalProperties": False,
                "required": ["kind", "reference", "establishes"],
                "properties": {
                    "kind": {"type": "string", "enum": ["source", "test", "differential",
                                                        "mutation", "crash-matrix", "proof",
                                                        "repository-integrity-gate"]},
                    "reference": s,
                    "establishes": {"type": "string", "enum": STATUS_LADDER + ["NONE"]},
                }},
            "provenance": {
                "type": "object", "additionalProperties": False,
                "required": ["source_document", "source_section", "source_hash",
                             "source_document_hash", "canonical_home", "registry_row",
                             "frozen_source", "frozen_addendum"],
                "properties": {
                    "source_document": {"const": "spec/01-canonical-specification.md"},
                    "source_section": {"type": "string", "pattern": "^S-[0-9]{2}$"},
                    "source_hash": {"$ref": "#/$defs/hash"},
                    "source_document_hash": {"$ref": "#/$defs/hash"},
                    "canonical_home": {"type": "object", "additionalProperties": False,
                                       "required": ["document", "section", "document_hash"],
                                       "properties": {"document": s,
                                                      "section": {"type": "string", "pattern": "^§[0-9]{2}$"},
                                                      "document_hash": {"$ref": "#/$defs/hash"}}},
                    "registry_row": {"type": "object", "additionalProperties": False,
                                     "required": ["document", "provenance_cell", "document_hash"],
                                     "properties": {"document": s, "provenance_cell": s,
                                                    "document_hash": {"$ref": "#/$defs/hash"}}},
                    "frozen_source": {"type": "object", "additionalProperties": False,
                                      "required": ["document", "line_ranges", "document_hash"],
                                      "properties": {"document": {"const": "Red-on-Rust.md"},
                                                     "line_ranges": {"type": "array",
                                                                     "items": {"type": "string", "pattern": "^L[0-9]+(–[0-9]+)?$"}},
                                                     "document_hash": {"$ref": "#/$defs/hash"}}},
                    "frozen_addendum": {"type": ["string", "null"]},
                }},
        },
    }


def validate_schema(inst, sch, root, path="$") -> list[str]:
    """Minimal JSON-Schema subset validator (type/enum/const/required/properties/
    additionalProperties/items/minItems/maxItems/uniqueItems/pattern/minLength/$ref)."""
    errs: list[str] = []
    if "$ref" in sch:
        ref = sch["$ref"]
        assert ref.startswith("#/")
        node = root
        for part in ref[2:].split("/"):
            node = node[part]
        return validate_schema(inst, node, root, path)
    if "const" in sch and inst != sch["const"]:
        errs.append(f"{path}: const mismatch")
    if "enum" in sch and inst not in sch["enum"]:
        errs.append(f"{path}: {inst!r} not in enum")
    if "type" in sch:
        types = sch["type"] if isinstance(sch["type"], list) else [sch["type"]]
        tmap = {"string": str, "integer": int, "boolean": bool, "array": list,
                "object": dict, "null": type(None)}
        ok = any(isinstance(inst, tmap[t]) and not (t == "integer" and isinstance(inst, bool))
                 for t in types)
        if not ok:
            errs.append(f"{path}: type {type(inst).__name__} not in {types}")
            return errs
    if isinstance(inst, str):
        if "pattern" in sch and not re.search(sch["pattern"], inst):
            errs.append(f"{path}: {inst!r} !~ {sch['pattern']}")
        if "minLength" in sch and len(inst) < sch["minLength"]:
            errs.append(f"{path}: too short")
    if isinstance(inst, list):
        if "minItems" in sch and len(inst) < sch["minItems"]:
            errs.append(f"{path}: fewer than {sch['minItems']} items")
        if "maxItems" in sch and len(inst) > sch["maxItems"]:
            errs.append(f"{path}: more than {sch['maxItems']} items")
        if sch.get("uniqueItems") and len(set(map(json.dumps, inst))) != len(inst):
            errs.append(f"{path}: items not unique")
        if "items" in sch:
            for i, it in enumerate(inst):
                errs += validate_schema(it, sch["items"], root, f"{path}[{i}]")
    if isinstance(inst, dict):
        for k in sch.get("required", []):
            if k not in inst:
                errs.append(f"{path}: missing required {k}")
        props = sch.get("properties", {})
        for k, v in inst.items():
            if k in props:
                errs += validate_schema(v, props[k], root, f"{path}.{k}")
            elif "additionalProperties" in sch:
                ap = sch["additionalProperties"]
                if ap is False:
                    errs.append(f"{path}: additional property {k}")
                elif isinstance(ap, dict):
                    errs += validate_schema(v, ap, root, f"{path}.{k}")
    return errs


# ---------------------------------------------------------------------------
# validation battery (the 20 acceptance checks)
# ---------------------------------------------------------------------------

def battery(I: Inputs, reg: dict, sch: dict, committed_reg: bytes | None) -> tuple[list, dict]:
    """Return (results, stats). results = [(ok, label)]. Any not-ok is FAIL."""
    res: list[tuple[bool, str]] = []
    st: dict = {}

    def ok(cond, label):
        res.append((bool(cond), label))

    reqs = reg["requirements"]
    ids = [r["id"] for r in reqs]
    canon_ids = [r["id"] for r in I.final03]
    st["count"] = len(ids)
    st["unique"] = len(set(ids))
    dup = [i for i, c in collections.Counter(ids).items() if c > 1]
    st["duplicates"] = dup
    st["missing"] = [i for i in canon_ids if i not in set(ids)]
    st["extra"] = [i for i in ids if i not in set(canon_ids)]

    # 1 schema validity, 2 required fields
    errs = validate_schema(reg, sch, sch)
    ok(not errs, f"1/2  schema validity + required fields: {len(errs)} violation(s)"
                 + (" — " + "; ".join(errs[:5]) if errs else ""))
    # 3 unique IDs
    ok(not dup, f"3    IDs unique: {st['unique']}/{st['count']} unique; duplicates {dup or 'none'}")
    # 4 canonical ID set preserved (five authorities)
    spec10_ids = [r["id"] for r in I.spec10["requirements"]]
    same = (ids == canon_ids == I.spec03_ids == spec10_ids
            and set(ids) == set(I.spec01_text) == set(I.final01))
    ok(same and len(ids) == EXPECTED_COUNT,
       f"4    canonical ID set preserved: reg {len(ids)} == final/03 {len(canon_ids)} == spec/03 "
       f"{len(I.spec03_ids)} == spec/10 {len(spec10_ids)} == spec/01 chunks {len(I.spec01_text)} "
       f"== final/01 chunks {len(I.final01)} (order-identical where ordered); expected "
       f"{EXPECTED_COUNT}: {'yes' if same else 'NO'}")
    # per-area counts vs final/03 area table
    area_tbl = {}
    for ln in P.read("final/03-requirement-registry.md").split("\n"):
        m = re.match(r"^\| (R-[A-Z]+) \| (\d+) \|", ln)
        if m:
            area_tbl[m.group(1)] = int(m.group(2))
    area_reg = collections.Counter("R-" + r["category"] for r in reqs)
    ok(area_tbl == dict(area_reg), f"4b   per-area counts identical to final/03 area table "
                                   f"({len(area_tbl)} areas)")
    # 5 statements preserved (byte-identical to spec/01; ws-identical to final/01)
    bad_s = [r["id"] for r in reqs if r["statement"] != I.spec01_text[r["id"]]]
    bad_f = [r["id"] for r in reqs if ws(r["statement"]) != ws(I.final01[r["id"]][3])]
    ok(not bad_s and not bad_f, f"5    statements preserved: byte-identical to spec/01 for "
                                f"{len(reqs) - len(bad_s)}/{len(reqs)}; whitespace-identical to "
                                f"final/01 for {len(reqs) - len(bad_f)}/{len(reqs)}")
    # 6 normative levels preserved: re-derivation stable + negative tokens conserved
    neg_src = sum(negative_tokens(I.spec01_text[i]) for i in ids)
    neg_reg = sum(negative_tokens(r["statement"]) for r in reqs)
    lvl_ok = all(r["normative_level"] in LEVEL_VOCAB and r["normative_level"] == r["normative_levels_present"][0]
                 for r in reqs)
    neg_flag_ok = all(r["negative_guarantee"] == (negative_tokens(r["statement"]) > 0) for r in reqs)
    ok(neg_src == neg_reg and lvl_ok and neg_flag_ok,
       f"6    normative levels preserved: {neg_reg} negative-guarantee tokens in registry == "
       f"{neg_src} in spec/01; every level in vocabulary; negative_guarantee flags consistent")
    st["negative_tokens"] = neg_reg
    # 7 dependencies resolve
    idset = set(ids)
    unresolved = [(r["id"], d) for r in reqs for d in r["dependencies"] if d not in idset]
    selfdep = [r["id"] for r in reqs if r["id"] in r["dependencies"]]
    canon_dep_ok = all(r["dependencies"] == I.spec10_req[r["id"]]["dependencies"] for r in reqs)
    ok(not unresolved and not selfdep and canon_dep_ok,
       f"7    dependencies resolve: {sum(len(r['dependencies']) for r in reqs)} R-level edges "
       f"(== spec/10 canonical); unresolved {unresolved or 'none'}; self-references "
       f"{selfdep or 'none'}")
    st["unresolved_dependencies"] = unresolved
    # 8 provenance exists, 9 hashes valid
    miss_prov = [r["id"] for r in reqs if not (r["provenance"]["source_section"]
                                                and r["provenance"]["source_hash"])]
    hash_ok = all(r["provenance"]["source_hash"] == sha256_bytes(I.spec01_text[r["id"]].encode())
                  and r["provenance"]["source_document_hash"] == I.hashes["spec/01-canonical-specification.md"]
                  and r["provenance"]["frozen_source"]["document_hash"] == I.hashes["Red-on-Rust.md"]
                  for r in reqs)
    no_lines = [r["id"] for r in reqs if not r["provenance"]["frozen_source"]["line_ranges"]]
    add_ok = all((r["provenance"]["frozen_addendum"] is not None) == (r["id"] in no_lines) for r in reqs)
    ok(not miss_prov and hash_ok and add_ok,
       f"8/9  provenance present for {len(reqs) - len(miss_prov)}/{len(reqs)}; source hashes "
       f"re-derive from the spec/01 chunk bytes and the input file hashes; {len(no_lines)} rows "
       f"without frozen-source line ranges are exactly the frozen addenda (recorded, not missing)")
    st["missing_provenance"] = miss_prov
    st["addenda_without_lines"] = no_lines
    # 10 status legal, 11 no unauthorized promotion
    illegal = [r["id"] for r in reqs if r["status"] not in STATUS_LADDER]
    canon_status = {r["id"]: r["status"] for r in I.final03}
    diff_status = [r["id"] for r in reqs if r["status"] != canon_status[r["id"]]
                   or r["status"] != I.final01[r["id"]][2]]
    ledger = json.loads((REPO / LEDGER_JSON).read_text()) if (REPO / LEDGER_JSON).exists() \
        else {"transitions": []}
    promoted = [r["id"] for r in reqs if r["status"] != "SPECIFIED"]
    unledgered = [i for i in promoted if not any(t["requirement_id"] == i for t in ledger["transitions"])]
    ok(not illegal and not diff_status and not unledgered,
       f"10/11 status values legal ({collections.Counter(r['status'] for r in reqs).most_common()}); "
       f"identical to final/03 and final/01 markers for all rows; no promotion without a ledger "
       f"entry (ledger entries: {len(ledger['transitions'])})")
    st["status_distribution"] = dict(collections.Counter(r["status"] for r in reqs))
    # 12 historical evidence unchanged: ledger is append-only (checked vs git HEAD copy)
    hist_ok, hist_note = ledger_append_only(ledger)
    # the detail depends on git state (committed vs not), so it is printed, not rendered
    print(f"     12   detail: {hist_note}", file=sys.stderr)
    ok(hist_ok, f"12   historical evidence unchanged: transition ledger is append-only vs the committed "
                f"copy; {len(ledger['transitions'])} entries")
    # 21 evidence-kind enforcement: every evidence entry in a ledger transition
    # MUST have a kind that is in the required set for the new_status.
    # This mechanically enforces the status-transition evidence model:
    #   SPECIFIED→IMPLEMENTED requires 'source' evidence
    #   IMPLEMENTED→TESTED requires 'test' evidence
    #   TESTED→VERIFIED requires 'differential'/'mutation'/'crash-matrix' evidence
    #   VERIFIED→PROVEN requires 'proof' evidence
    evidence_kind_violations = []
    for t in ledger["transitions"]:
        new_status = t.get("new_status", "")
        if new_status in EVIDENCE_KINDS_FOR_STATUS:
            required_kinds = EVIDENCE_KINDS_FOR_STATUS[new_status]
            for ev in t.get("evidence", []):
                kind = ev.get("kind", "")
                if kind in NON_PROMOTING_KINDS:
                    evidence_kind_violations.append(
                        (t["requirement_id"], new_status, kind,
                         f"repository-integrity-gate cannot establish {new_status}"))
                elif kind not in required_kinds and kind not in ALL_EVIDENCE_KINDS:
                    evidence_kind_violations.append(
                        (t["requirement_id"], new_status, kind,
                         f"unknown evidence kind {kind!r}"))
                elif kind not in required_kinds:
                    evidence_kind_violations.append(
                        (t["requirement_id"], new_status, kind,
                         f"evidence kind {kind!r} cannot establish {new_status} "
                         f"(required: {sorted(required_kinds)})"))
    ok(not evidence_kind_violations,
       f"21   evidence-kind enforcement: {len(evidence_kind_violations)} violation(s) "
       f"in {len(ledger['transitions'])} ledger entries; "
       f"{'violations: ' + str(evidence_kind_violations[:3]) if evidence_kind_violations else 'all kinds match target statuses'}")
    # 22 skip evidence completeness: if a transition skips intermediate levels,
    # the evidence package MUST include at least one evidence entry for each
    # skipped level's required kinds.
    skip_violations = []
    for t in ledger["transitions"]:
        prev_idx = STATUS_LADDER.index(t["previous_status"]) if t["previous_status"] in STATUS_LADDER else -1
        new_idx = STATUS_LADDER.index(t["new_status"]) if t["new_status"] in STATUS_LADDER else -1
        if prev_idx >= 0 and new_idx > prev_idx + 1:
            # This is a skip transition
            skipped = STATUS_LADDER[prev_idx + 1:new_idx]
            evidence_kinds_in_entry = {ev.get("kind") for ev in t.get("evidence", [])}
            for skipped_status in skipped:
                if skipped_status in EVIDENCE_KINDS_FOR_STATUS:
                    required = EVIDENCE_KINDS_FOR_STATUS[skipped_status]
                    if not (evidence_kinds_in_entry & required):
                        skip_violations.append(
                            (t["requirement_id"], t["previous_status"], t["new_status"],
                             skipped_status, f"skip missing {skipped_status} evidence "
                             f"(need kind in {sorted(required)})"))
            if not t.get("skip_justification"):
                skip_violations.append(
                    (t["requirement_id"], t["previous_status"], t["new_status"],
                     "SKIP", "skip transition without skip_justification"))
    ok(not skip_violations,
       f"22   skip evidence completeness: {len(skip_violations)} violation(s) in "
       f"skip transitions; "
       f"{'violations: ' + str(skip_violations[:3]) if skip_violations else 'all skips have complete evidence'}")
    # 13 security classification preserved
    gi_sec_ids = {rid for rid, gs in I.gi.items() if any(g.startswith("GI-SEC-") for g in gs)}
    sec_ok = all(r["security_relevant"] for r in reqs if r["id"] in gi_sec_ids) and \
        all(r["security_relevant"] == bool(r["security_classification"]["basis"]) for r in reqs)
    ok(sec_ok, f"13   security classification preserved: every GI-SEC home ({len(gi_sec_ids)}) is "
               f"security_relevant; flag == (basis non-empty) for all rows")
    st["security_relevant"] = sum(1 for r in reqs if r["security_relevant"])
    st["security_unclassified"] = [r["id"] for r in reqs
                                   if r["security_classification"]["status"] == "UNCLASSIFIED"]
    # 14/15/16 mappings not fabricated: equal to the canonical cells
    f03 = {r["id"]: r for r in I.final03}
    fab = [r["id"] for r in reqs
           if r["implementation_targets"] != split_cell(f03[r["id"]]["impl"])
           or r["test_targets"] != split_cell(f03[r["id"]]["verify"])
           or r["verification_method"] != (f03[r["id"]]["verify"] if split_cell(f03[r["id"]]["verify"]) else None)
           or r["verification_tags"] != I.tags.get(r["id"], [])
           or r["mutations"] != I.mutations.get(r["id"], [])]
    ok(not fab, f"14/15/16 implementation / test / verification mappings equal the canonical "
                f"final/03 cells and spec/10 tag+mutation maps for {len(reqs) - len(fab)}/{len(reqs)}")
    # 17 evidence traceable: every evidence entry references an existing repo path
    bad_ev = [(r["id"], e) for r in reqs for e in r["evidence"]
              if not (REPO / e["reference"].split("#")[0]).exists()]
    n_ev = sum(len(r["evidence"]) for r in reqs)
    ok(not bad_ev, f"17   evidence traceable: {n_ev} evidence entries; untraceable {bad_ev or 'none'}")
    # 18/19 deterministic + reproducible: two renders identical; committed file identical
    r2 = render_json(build_registry(I))
    r1 = render_json(reg)
    ok(r1 == r2, "18   deterministic: two independent in-memory compilations render byte-identical")
    if committed_reg is None:
        ok(False, f"19   reproducible: {REGISTRY_JSON} missing (run --write)")
    else:
        ok(committed_reg == r1.encode("utf-8"),
           f"19   reproducible: committed {REGISTRY_JSON} {'==' if committed_reg == r1.encode() else '!='} "
           f"fresh compilation ({sha256_bytes(committed_reg)[:23]}…)")
    st["registry_hash"] = sha256_bytes(r1.encode("utf-8"))
    # 20 governance
    chk = P.read("check.py")
    ok('"reg/_compile.py"' in chk, "20   governance: reg/_compile.py registered in check.py CHECKERS")

    st["no_impl"] = [r["id"] for r in reqs if not r["implementation_targets"]]
    st["no_test"] = [r["id"] for r in reqs if not r["test_targets"]]
    st["no_vm"] = [r["id"] for r in reqs if r["verification_method"] is None]
    st["no_evidence"] = [r["id"] for r in reqs if not r["evidence"]]
    return res, st


def ledger_append_only(ledger: dict) -> tuple[bool, str]:
    """The transition ledger may only grow: every entry in the git-HEAD copy must
    still be present, unchanged, at the same position."""
    try:
        old = subprocess.run(["git", "show", f"HEAD:{LEDGER_JSON}"], cwd=REPO,
                             capture_output=True, text=True)
    except OSError:
        return True, "git unavailable; append-only check skipped (reported, not passed silently)"
    if old.returncode != 0:
        return True, "no committed ledger yet (first compilation); nothing to preserve"
    prev = json.loads(old.stdout)["transitions"]
    cur = ledger["transitions"]
    if cur[:len(prev)] != prev:
        return False, "committed ledger entries were modified or removed"
    return True, f"ledger append-only vs HEAD ({len(prev)} historical entries preserved, " \
                 f"{len(cur) - len(prev)} new)"


# ---------------------------------------------------------------------------
# derived dependency view (report only — never written into `dependencies`)
# ---------------------------------------------------------------------------

def lifted_atomic_dependencies(I: Inputs, ids: list[str]):
    edges = I.dep["layers"]["requirement"]["edges"]
    lifted: dict[str, dict[str, set]] = collections.defaultdict(lambda: collections.defaultdict(set))
    self_loops = 0
    unparented = 0
    for e in edges:
        pc, pp = I.rec_parent.get(e["consumer"], []), I.rec_parent.get(e["provider"], [])
        if not pc or not pp:
            unparented += 1
        for c in pc:
            for p in pp:
                if c == p:
                    self_loops += 1
                else:
                    lifted[c][p].add(e["kind"])
    unresolved = [(c, p) for c in lifted for p in lifted[c] if p not in set(ids) or c not in set(ids)]
    n_edges = sum(len(v) for v in lifted.values())
    # mutual pairs (2-cycles) in the lifted view
    mutual = sorted({tuple(sorted((c, p))) for c in lifted for p in lifted[c] if c in lifted.get(p, {})})
    return {"atomic_edges": len(edges), "kinds": dict(collections.Counter(e["kind"] for e in edges)),
            "lifted": lifted, "lifted_edges": n_edges, "consumers": len(lifted),
            "self_loops": self_loops, "unparented_endpoint_edges": unparented,
            "unresolved": unresolved, "mutual_pairs": mutual}


# ---------------------------------------------------------------------------
# reports
# ---------------------------------------------------------------------------

GAP_TOKEN = re.compile(r"^(U|C)-\d+")

HDR = ("> **Derived artifact.** Generated by `python3 reg/_compile.py --write`; do not edit. "
       "`python3 reg/_compile.py` (check mode, registered in `check.py`) recompiles from the "
       "authorities and fails on any drift. Nothing here is implementation, test, verification "
       "or proof evidence for any `R-…` requirement; a PASS below is repository-integrity "
       "evidence only (V1 F-INFL-01).\n")


def bullets(items, limit=None):
    items = list(items)
    if not items:
        return "- none\n"
    shown = items if limit is None else items[:limit]
    out = "".join(f"- {md_cell(str(i))}\n" for i in shown)
    if limit is not None and len(items) > limit:
        out += f"- … ({len(items) - limit} more)\n"
    return out


def render_overview(reg, st) -> str:
    return f"""# Red-on-Rust — R-REG Machine-Readable Requirements Registry

{HDR}
| File | Output # | Content |
|---|---|---|
| `requirements.json` | 1 | Machine-readable requirements registry ({reg['requirement_count']} records; derived from `final/03` + `spec/01`/`final/01`) |
| `requirements.schema.json` | 2 | JSON Schema (draft 2020-12) for `requirements.json` |
| `01-compilation-report.md` | 3 | Registry compilation report (the 15 mandated audit figures + the 22-point validation battery) |
| `02-identity-diff-report.md` | 4 | Identity/diff report against the canonical requirement registry |
| `03-status-transition-audit-model.md` + `status-transitions.json` | 5 | Status-transition/audit model and the (append-only) transition ledger |
| `04-provenance-report.md` | 6 | Provenance report |
| `05-dependency-integrity-report.md` | 7 | Dependency-integrity report |
| `06-evidence-coverage-summary.md` | 8 | Evidence coverage summary |
| `07-security-relevance-summary.md` | 9 | Security-relevance summary |
| `08-determinism-hash-report.md` | 10 | Deterministic-generation / hash report |

**Authority chain (unchanged):** `Red-on-Rust.md` → cleaned `spec/` → canonical registry `final/03` (+ canonical statements `spec/01`, re-homed verbatim in `final/01`) → `reg/requirements.json`. The generated registry is a derived artifact and **is not a competing normative source**: if it would disagree with the canonical registry, the compiler fails instead of choosing.

**Current state carried:** {reg['requirement_count']}/{EXPECTED_COUNT} identity established; status distribution {st['status_distribution']}; `REF1-CONDITIONAL` and `V1-CONDITIONAL` carried as conditional; repository remains ARCHITECTURE FROZEN / IMPLEMENTATION READY — which this registry does **not** convert into IMPLEMENTED, and `check.py` PASS is **not** converted into VERIFIED.

**Field semantics (binding for consumers):** `implementation_targets` are the normative crate homes registered in the canonical registry (`spec/07`); no crate exists in this repository. `test_targets` / `verification_tags` / `mutations` are the registered test *contracts*; repository evidence for every one is `NONE` (`final/04`). `evidence: []` and `status: SPECIFIED` are the current evidence-backed state. Fields suffixed `_basis` / `_source` record the mechanical derivation rule for the value they accompany.
"""


def render_compilation(reg, st, res, I) -> str:
    lines = [f"{'OK  ' if o else 'FAIL'} {l}" for o, l in res]
    fails = sum(1 for o, _ in res if not o)
    gap_markers = ', '.join(f"{r['id']} ({t})" for r in reg['requirements']
                            for t in r['test_targets'] if GAP_TOKEN.match(t))
    return f"""# R-REG — 01. Registry Compilation Report

{HDR}
## 1. Mandated audit figures

| # | Figure | Value |
|---|---|---|
| 1 | Source registry hash (`final/03-requirement-registry.md`) | `{I.hashes['final/03-requirement-registry.md']}` |
| 1b | Source statement authority hash (`spec/01-canonical-specification.md`) | `{I.hashes['spec/01-canonical-specification.md']}` |
| 1c | Frozen source hash (`Red-on-Rust.md`) | `{I.hashes['Red-on-Rust.md']}` |
| 2 | Generated registry hash (`reg/requirements.json`) | `{st['registry_hash']}` |
| 3 | Requirement count | {st['count']} (expected {EXPECTED_COUNT}) |
| 4 | Unique-ID count | {st['unique']} |
| 5 | Duplicate IDs | {st['duplicates'] or 'none'} |
| 6 | Missing IDs (canonical − generated) | {st['missing'] or 'none'} |
| 7 | Extra IDs (generated − canonical) | {st['extra'] or 'none'} |
| 8 | Unresolved dependencies | {st['unresolved_dependencies'] or 'none'} (0 R-level dependencies are registered by the canonical index) |
| 9 | Missing provenance | {st['missing_provenance'] or 'none'} ({len(st['addenda_without_lines'])} frozen addenda carry no frozen-source line range by design — see `04-provenance-report.md`) |
| 10 | Status distribution | {st['status_distribution']} |
| 11 | Security-relevant requirement count | {st['security_relevant']} / {st['count']} ({len(st['security_unclassified'])} UNCLASSIFIED — no authoritative classification input; **not** asserted non-relevant) |
| 12 | Requirements lacking implementation targets | {len(st['no_impl'])} |
| 13 | Requirements lacking test targets | {len(st['no_test'])} |
| 14 | Requirements lacking verification methods | {len(st['no_vm'])} |
| 15 | Requirements lacking evidence | {len(st['no_evidence'])} (all — the repository holds no implementation/test/proof artefacts, `spec/07` §1) |

Figures 12–15 are *absence of registered artefacts*. They neither promote nor demote any status (DEFINITION OF ABSENCE).

## 2. Validation battery (22 points; any FAIL aborts `--write` and fails `check.py`)

```
{chr(10).join(lines)}
```

Result: **{'ALL PASS' if not fails else f'{fails} FAILURE(S)'}** — repository-integrity result only.

## 3. Warnings carried (not converted into PASS)

- {len(st['security_unclassified'])} requirements have no authoritative security classification input (frozen addenda from the request-pipeline / duration-semantics / resource-accounting audits with no GI-SEC home and no atomic record): {', '.join(st['security_unclassified']) or 'none'}. `security_relevant` is `false` for them with `security_classification.status = UNCLASSIFIED`; this is a classification gap, not a negative finding.
- {sum(1 for r in reg['requirements'] if r['normative_level_basis'].startswith('declarative-convention'))} requirements carry a `normative_level` assigned by the req/00 declarative convention because the canonical statement contains no RFC keyword and no atomic record exists: {', '.join(r['id'] for r in reg['requirements'] if r['normative_level_basis'].startswith('declarative-convention')) or 'none'}.
- {sum(1 for r in reg['requirements'] if r['normative_level_basis'].startswith('atomic-records'))} requirements take their level from the atomic records (statement is a definition/formula without RFC keyword).
- Verify→ cells that are gap markers rather than methods (token names a `U-`/`C-` item): {gap_markers or 'none'}. They are carried verbatim and counted as *defined* by the canonical registry; the gap stays visible here.
- `python3 check.py` ALL PASS is repository-integrity evidence only; no requirement defines a repository checker as its verification method, so none is VERIFIED by it.
- `REF1-CONDITIONAL` and `V1-CONDITIONAL` remain conditional (`requirements.json` → `conditional_verdicts`).
"""


def render_identity(reg, st, I) -> str:
    reqs = reg["requirements"]
    f03 = {r["id"]: r for r in I.final03}
    rows = []
    for r in reqs:
        c = f03[r["id"]]
        rows.append(f"| {r['id']} | {c['status']} | {r['status']} | {'=' if c['status'] == r['status'] else 'DIFF'} "
                    f"| {r['section']} | {r['cleaned_section']} | {len(r['implementation_targets'])} | {len(r['test_targets'])} | "
                    f"{'yes' if r['security_relevant'] else ('unclassified' if r['security_classification']['status'] == 'UNCLASSIFIED' else 'no')} |")
    areas = collections.Counter(r["category"] for r in reqs)
    return f"""# R-REG — 02. Identity / Diff Report vs the Canonical Requirement Registry

{HDR}
## 1. Identity

| Authority | IDs | Relation to generated registry |
|---|---|---|
| `final/03-requirement-registry.md` (canonical registry) | {len(I.final03)} | order-identical, status-identical |
| `final/01-canonical-specification.md` §26 + canonical-home markers | {len(I.final01)} | ID set identical; statement whitespace-identical |
| `spec/03-obligation-matrix.md` (cleaned authority) | {len(I.spec03_ids)} | order-identical |
| `spec/01-canonical-specification.md` chunks (statement authority) | {len(I.spec01_text)} | ID set identical; statement byte-identical |
| `spec/10-index.json` requirements | {len(I.spec10['requirements'])} | order-identical; dependencies / findings copied |
| **generated `reg/requirements.json`** | **{st['count']}** | {st['unique']} unique; duplicates {st['duplicates'] or 'none'}; missing {st['missing'] or 'none'}; extra {st['extra'] or 'none'} |

Identity established: **{st['count']}/{EXPECTED_COUNT}** — canonical count = generated count; canonical ID set = generated ID set; each canonical ID occurs exactly once.

Deliberate, non-reusable ID gaps carried from the canonical registry: `R-BUDGET-12`, `R-BUDGET-14` (never frozen; never reused).

## 2. Per-area counts

| Area | Count |
|---|---|
{''.join(f'| R-{a} | {n} |' + chr(10) for a, n in sorted(areas.items()))}
## 3. Row-by-row diff (status, home, mapping sizes)

`=` in the Status-diff column means the generated status equals the canonical status. Any `DIFF` would have failed the build.

| R-ID | canonical status | generated status | diff | §home | S-sec | impl targets | test targets | security |
|---|---|---|---|---|---|---|---|---|
{chr(10).join(rows)}
"""


def render_status_model(reg, st) -> str:
    return f"""# R-REG — 03. Status-Transition / Audit Model

{HDR}
## 1. Ladder (canonical home `spec/00` §2 / `final/01` §28)

```
SPECIFIED -> IMPLEMENTED -> TESTED -> VERIFIED -> PROVEN
```

| Status | Evidence required (spec/00 §2) |
|---|---|
| SPECIFIED | citation into the frozen source / canonical statement (present for all {st['count']} rows via `provenance`) |
| IMPLEMENTED | source file(s) in this repository, mapped in `spec/07` |
| TESTED | test file + passing run, mapped in `spec/08` |
| VERIFIED | independent evidence: differential agreement, mutation kill, crash matrix |
| PROVEN | mechanized proof artefact in the repository |

## 2. Evidence-kind predicates (status-appropriate evidence)

The evidence `kind` MUST be appropriate for the target `establishes` status. A generic evidence kind MUST NOT be used to claim any status level.

| Target status | Required evidence kinds | Prohibited evidence kinds |
|---|---|---|
| `IMPLEMENTED` | `source` | `test`, `differential`, `mutation`, `crash-matrix`, `proof`, `repository-integrity-gate` |
| `TESTED` | `test` | `source`, `differential`, `mutation`, `crash-matrix`, `proof`, `repository-integrity-gate` |
| `VERIFIED` | `differential`, `mutation`, `crash-matrix` | `source`, `test`, `proof`, `repository-integrity-gate` |
| `PROVEN` | `proof` | `source`, `test`, `differential`, `mutation`, `crash-matrix`, `repository-integrity-gate` |

**Rationale:**
- `source` evidence (implementation files) establishes IMPLEMENTED, not TESTED/VERIFIED/PROVEN.
- `test` evidence (executed tests) establishes TESTED, not IMPLEMENTED/VERIFIED/PROVEN.
- `differential`/`mutation`/`crash-matrix` evidence establishes VERIFIED, not IMPLEMENTED/TESTED/PROVEN.
- `proof` evidence (formal proof artefacts) establishes PROVEN, not IMPLEMENTED/TESTED/VERIFIED.
- `repository-integrity-gate` evidence (check.py PASS) establishes NONE — it is repository-integrity evidence only, never a status promotion.

**Fail-closed rule:** If a ledger entry's evidence `kind` does not match the required kinds for its `new_status`, the compiler MUST reject the entry.

## 3. Skip semantics

If a status transition skips one or more intermediate levels, the evidence package MUST satisfy:
1. The target status's evidence requirements, AND
2. All intermediate status evidence requirements.

**Example:** SPECIFIED → VERIFIED requires:
- `source` evidence (for IMPLEMENTED), AND
- `test` evidence (for TESTED), AND
- `differential`/`mutation`/`crash-matrix` evidence (for VERIFIED).

A skip MUST NOT mean "higher status requested, therefore higher status is accepted." Every skip MUST carry an explicit `skip_justification` explaining why intermediate evidence is not required or is bundled.

**Fail-closed rule:** If a ledger entry skips levels and does not carry evidence for all intermediate statuses, the compiler MUST reject the entry unless an explicit authorized skip rule exists.

## 4. Rules enforced by the compiler

1. `status` is **copied** from `final/03` and cross-checked against the `final/01` canonical-home marker; the compiler has no code path that writes any other value.
2. A row whose status is above SPECIFIED must have at least one entry in `reg/status-transitions.json` — otherwise the build fails (battery point 10/11).
3. The ledger is **append-only**: the battery compares it with the git-HEAD copy and fails if any historical entry was altered or removed (point 12).
4. No inference: SPECIFIED→IMPLEMENTED, IMPLEMENTED→TESTED, TESTED→VERIFIED, VERIFIED→PROVEN are never derived from statement text, from `implementation_targets`, from `test_targets`, from a passing repository checker, or from the words "implementation ready", "gate PASS" or "audit complete".
5. Skipping a rung is admissible only if the ledger entry carries an explicit `skip_justification` and the evidence model permits it; the compiler rejects an entry whose `new_status` is not later in the ladder than `previous_status`.
6. `REF1-CONDITIONAL` / `V1-CONDITIONAL` are audit verdicts, not requirement statuses; they are carried in `conditional_verdicts` and may only change through a new audit record, never through this ledger.
7. **Evidence-kind enforcement:** Every evidence entry in a ledger transition MUST have a `kind` that is in the required set for the `new_status`. The compiler rejects entries with mismatched evidence kinds (battery point 21).
8. **Skip evidence completeness:** If a transition skips intermediate levels, the evidence package MUST include at least one evidence entry for each skipped level's required kinds. The compiler rejects incomplete skip evidence (battery point 22).

## 5. Ledger entry shape (`reg/status-transitions.json`)

```json
{{
  "requirement_id": "R-…",
  "previous_status": "SPECIFIED",
  "new_status": "IMPLEMENTED",
  "evidence": [{{"kind": "source", "reference": "repo/path#anchor", "establishes": "IMPLEMENTED"}}],
  "verification_method": "…",
  "repository_revision": "git commit sha",
  "timestamp": "YYYY-MM-DD",
  "justification": "…",
  "skip_justification": null,
  "approved_by": "owner / authority"
}}
```

**Evidence-kind examples:**
- SPECIFIED → IMPLEMENTED: `{{"kind": "source", "reference": "crates/ror-core/src/lib.rs", "establishes": "IMPLEMENTED"}}`
- IMPLEMENTED → TESTED: `{{"kind": "test", "reference": "tests/cek_test.rs#test_let_binding", "establishes": "TESTED"}}`
- TESTED → VERIFIED: `{{"kind": "differential", "reference": "tests/differential/cek_agreement.rs", "establishes": "VERIFIED"}}`
- VERIFIED → PROVEN: `{{"kind": "proof", "reference": "proofs/capability_attenuation.v", "establishes": "PROVEN"}}`

## 6. Current ledger

Entries: **0**. Status distribution: {st['status_distribution']}. No transition has occurred; no historical evidence exists to overwrite. Every one of the {st['count']} canonical obligations remains at its evidence-backed status `SPECIFIED` — the bootstrap state is carried, not promoted.
"""


def render_provenance(reg, st, I) -> str:
    reqs = reg["requirements"]
    add = [r for r in reqs if r["provenance"]["frozen_addendum"]]
    src = [r for r in reqs if not r["provenance"]["frozen_addendum"]]
    by_add = collections.Counter(r["provenance"]["frozen_addendum"] for r in add)
    rows = "\n".join(
        f"| {r['id']} | {r['cleaned_section']} | {r['section']} | "
        f"{md_cell(', '.join(r['provenance']['frozen_source']['line_ranges']) or '—')} | "
        f"{md_cell(r['provenance']['frozen_addendum'] or '—')} | `{r['provenance']['source_hash'][7:23]}…` | {len(r['atomic_records'])} |"
        for r in reqs)
    return f"""# R-REG — 04. Provenance Report

{HDR}
## 1. Source hashes used for compilation (identify the authorities, not the output)

| Input | sha256 |
|---|---|
{''.join(f'| `{f}` | `{h}` |' + chr(10) for f, h in I.hashes.items())}
## 2. Per-requirement provenance model

Each record's `provenance` carries: `source_document` = `spec/01-canonical-specification.md` (the single home of the canonical normative text), `source_section` = its `S-nn` section, `source_hash` = sha256 of the exact statement bytes taken from that document (re-derived by the checker), `source_document_hash`, the FINAL1 `canonical_home` (`final/01` §), the `registry_row` (`final/03` provenance cell verbatim), and the `frozen_source` line ranges into `Red-on-Rust.md` with the frozen file's hash.

- Rows with frozen-source line ranges: **{len(src)}** (the 148 frozen-source obligations).
- Rows without line ranges: **{len(add)}** — exactly the frozen post-audit addenda ("no source transcription" by their own text); their provenance is the addendum identifier in `frozen_addendum` plus the `spec/01` statement hash. This is a recorded provenance *boundary*, not a missing provenance: {dict(by_add)}.
- Missing provenance (no section or no hash): {st['missing_provenance'] or 'none'}.
- Hashing deficiency: none — every source hash was established mechanically; no hash was invented.

## 3. Provenance table

| R-ID | S-sec | §home | frozen-source lines | addendum | statement hash | atomic records |
|---|---|---|---|---|---|---|
{rows}
"""


def render_dependency(reg, st, I, lifted) -> str:
    reqs = reg["requirements"]
    tbl = "\n".join(
        f"| {c} | {md_cell(', '.join(sorted(lifted['lifted'][c])))} |"
        for c in sorted(lifted["lifted"]))
    return f"""# R-REG — 05. Dependency-Integrity Report

{HDR}
## 1. Canonical R-level dependencies (the `dependencies` field)

The canonical machine index `spec/10-index.json` registers **0** R-level dependencies (`dependencies: []` for all {len(reqs)} rows). The generated registry copies that field exactly: {sum(len(r['dependencies']) for r in reqs)} edges, unresolved {st['unresolved_dependencies'] or 'none'}, duplicate IDs {st['duplicates'] or 'none'}, self-references none, stale/renamed identifiers none (every ID is checked against the five ID authorities in `02-identity-diff-report.md`). Nothing was copied from `spec/04`'s section/object graphs or from `dep/` into `dependencies`, because those graphs are typed over sections, modules and *atomic records*, not over `R-` IDs — lifting them would be a derivation, which is reported below but **not** serialized as a canonical dependency.

## 2. Derived view (report only): atomic-record graph lifted to R-level

Source: `dep/10-graph.json` requirement layer ({lifted['atomic_edges']} typed edges over {I.dep['layers']['requirement']['node_count']} `REQ-` records; kinds {lifted['kinds']}), lifted through each record's parent-obligation citation (`req/` SOURCE → `R-…`).

- Lifted R→R edges (consumer depends on provider): **{lifted['lifted_edges']}** over {lifted['consumers']} consumers; intra-obligation edges collapsed: {lifted['self_loops']}; atomic edges with an endpoint that cites no parent (addendum-only records): {lifted['unparented_endpoint_edges']}.
- All lifted endpoints resolve to canonical IDs: {'yes' if not lifted['unresolved'] else 'NO — ' + str(lifted['unresolved'])}.
- Mutual pairs (2-cycles) in the lifted view: {len(lifted['mutual_pairs'])}. Cycles are *expected* in this layer — `dep/03` records the requirement-layer SCCs as architectural-review items (restatement and evidence-loop families), not as violations; they are reported here, unadjudicated, and are one more reason this view is not serialized as `dependencies`.

| consumer R-ID | depends on (lifted providers) |
|---|---|
{tbl}
"""


def _registered_checker_count() -> int:
    """Count check.py CHECKERS entries by ast (no execution, no import)."""
    import ast as _ast
    tree = _ast.parse((REPO / "check.py").read_text(encoding="utf-8"))
    for node in tree.body:
        targets, value = [], None
        if isinstance(node, _ast.Assign):
            targets, value = node.targets, node.value
        elif isinstance(node, _ast.AnnAssign) and node.value is not None:
            targets, value = [node.target], node.value
        else:
            continue
        for t in targets:
            if isinstance(t, _ast.Name) and t.id == "CHECKERS" and isinstance(value, _ast.List):
                return len(value.elts)
    raise SystemExit("reg/_compile.py: could not derive CHECKERS from check.py")


def render_evidence(reg, st, I) -> str:
    reqs = reg["requirements"]
    n = len(reqs)
    tags = sum(1 for r in reqs if r["verification_tags"])
    muts = sum(1 for r in reqs if r["mutations"])
    atomic_vm = sum(1 for r in reqs if r["atomic_verification_methods"])
    # Derived from the spec/10 index, which is itself derived from spec/08 §1's
    # two tables (spec/_build_index.py asserts set equality) -- never hand-counted.
    idx_tags = I.spec10["verification_tags"]
    n_frozen = sum(1 for t in idx_tags if t.get("source") == "frozen-source")
    n_add = sum(1 for t in idx_tags if t.get("source") == "post-audit-addendum")
    n_alias = len(I.spec10.get("verification_tag_aliases", []))
    assert n_frozen + n_add == len(idx_tags), "spec/10 tag sources must partition the indexed set"
    # Checker count derived from the check.py registration (ast, no execution)
    # -- repair pass v2 (V-02): this line previously hard-coded "15 checkers"
    # and drifted the moment the state gate was registered as the 16th.
    n_checkers = _registered_checker_count()
    assert n_checkers >= 1, "check.py CHECKERS registration must be parseable"
    return f"""# R-REG — 06. Evidence Coverage Summary

{HDR}
## 1. Coverage of *registered contracts* (not of evidence)

| Dimension | Rows with a registered entry | Rows without | Meaning of "without" |
|---|---|---|---|
| `implementation_targets` (crate homes, `spec/07`) | {n - len(st['no_impl'])} | {len(st['no_impl'])} | no crate home registered — {', '.join(st['no_impl'])} |
| `test_targets` (Verify→ tokens, `spec/08`) | {n - len(st['no_test'])} | {len(st['no_test'])} | no verification mapping registered |
| `verification_tags` (frozen + addendum tags) | {tags} | {n - tags} | no coverage tag names this row |
| `mutations` (M001–M042 kill map) | {muts} | {n - muts} | no mutant targets this row |
| `verification_method` (Verify→ cell) | {n - len(st['no_vm'])} | {len(st['no_vm'])} | canonical registry defines none: {', '.join(st['no_vm'])} |
| `atomic_verification_methods` (req/ records) | {atomic_vm} | {n - atomic_vm} | the 36 addenda have no atomic records (recorded coverage boundary, `final/03`) |
| `evidence` (existing repository evidence) | {n - len(st['no_evidence'])} | {len(st['no_evidence'])} | **no implementation, test, differential, mutation-run, crash-run or proof artefact exists** (`spec/07` §1, `final/04`) |

## 2. Evidence state

- Status distribution: {st['status_distribution']} — every row's status is the evidence-backed `SPECIFIED`; no row was promoted for having a registered target, tag or mutant (DEFINITION OF ABSENCE).
- Verification tags: {len(idx_tags)} defined ({n_frozen} frozen + {n_add} addendum; {n_alias} documented alias not indexed), repository evidence `NONE` for each (`final/04` §1). Mutation registry: {len(I.spec10['mutations'])} defined, executed none. Milestones M0–M11: none satisfied.
- Repository gates (`python3 check.py`, {n_checkers} checkers incl. this one, derived from the `check.py` registration): repository-integrity evidence only. No requirement defines a repository checker as its verification method; `audit/_conservation_checker.py` is named by R-BUDGET-10 as *gate evidence for the rule shape*, which `final/08` §4 explicitly declines to treat as machine evidence — carried unchanged.
- `REF1-CONDITIONAL`, `V1-CONDITIONAL`: conditional; V1 §8 UNKNOWN items remain UNKNOWN.
- Requirements lacking evidence: {len(st['no_evidence'])}/{n}. This figure is the bootstrap state, reported as such.
"""


def render_security(reg, st) -> str:
    reqs = reg["requirements"]
    rel = [r for r in reqs if r["security_relevant"]]
    basis = collections.Counter()
    for r in rel:
        for b in r["security_classification"]["basis"]:
            basis[b.split(":")[0].split(" = ")[0].split(" (")[0]] += 1
    neg = [r for r in reqs if r["negative_guarantee"]]
    rows = "\n".join(
        f"| {r['id']} | {md_cell(', '.join(r['security_classification']['gi_sec_homes']) or '—')} | "
        f"{r['security_classification']['atomic_security_impact_max'] or '—'} | "
        f"{'yes' if r['security_classification']['security_audit_addendum'] else '—'} | "
        f"{r['normative_level']}{' (+MUST NOT)' if 'MUST NOT' in r['normative_levels_present'] and r['normative_level'] != 'MUST NOT' else ''} | "
        f"{'yes' if r['negative_guarantee'] else '—'} |"
        for r in rel)
    uncl = [r for r in reqs if r["security_classification"]["status"] == "UNCLASSIFIED"]
    return f"""# R-REG — 07. Security-Relevance Summary

{HDR}
## 1. Classification rule (authoritative inputs only)

`security_relevant = true` iff at least one of:

1. the requirement is the **definitional home of a `GI-SEC-nn` global invariant** (`final/05`);
2. the **maximum `SECURITY-IMPACT`** over the `req/` atomic records citing it is `critical` or `high`;
3. it is a **frozen addendum produced by the authority/trust/external-effect security audit** (`SEC-nnn` provenance).

The rule never consults `implementation_targets`, `test_targets` or `evidence` — an empty target list cannot make a requirement non-security-relevant. Rows for which none of the three inputs exists are `UNCLASSIFIED` (flag `false`, classification gap reported), not "non-relevant".

## 2. Figures

- Security-relevant: **{len(rel)} / {len(reqs)}**. Basis counts: {dict(basis)}.
- UNCLASSIFIED (no input): {len(uncl)} — {', '.join(r['id'] for r in uncl) or 'none'}.
- Classified not security-relevant by the authoritative atomic classification (max `SECURITY-IMPACT` `medium`/`low`; no GI-SEC home; not a SEC addendum): {len(reqs) - len(rel) - len(uncl)} — {', '.join(r['id'] for r in reqs if not r['security_relevant'] and r['security_classification']['status'] == 'CLASSIFIED')}.
- Negative guarantees preserved: {len(neg)} requirements carry `MUST NOT` / `↛` / `⇏` / `NEVER` tokens; {st['negative_tokens']} tokens total, identical to the `spec/01` source (battery point 6). No `MUST NOT` was rewritten, weakened or merged.
- GI-SEC homes: 22, all security-relevant (battery point 13).

## 3. Security-relevant requirements

| R-ID | GI-SEC home(s) | atomic impact max | SEC-audit addendum | normative level | negative guarantee |
|---|---|---|---|---|---|
{rows}
"""


def render_hash(reg, st, I, sch_text, ledger_text) -> str:
    return f"""# R-REG — 08. Deterministic-Generation / Hash Report

{HDR}
## 1. Determinism guarantees

- Serialization: `json.dumps(sort_keys=True, indent=2, ensure_ascii=False)` + trailing newline; UTF-8; no timestamps, no git revision, no environment-dependent value inside `requirements.json`.
- Ordering: requirement order = `final/03` row order (= `spec/03` = `spec/10`); list-valued fields keep authority order or are sorted where they come from sets (`atomic_categories`, `atomic_verification_methods`, `normative_levels_present`, `atomic_security_impacts`).
- Battery point 18 compiles twice in one process and requires byte-identical output; point 19 requires the committed file to equal a fresh compilation (so `check.py` fails on any drift, hand edit, or authority change not followed by `--write`).

## 2. Hashes

| Artifact | Role | sha256 |
|---|---|---|
| `reg/requirements.json` | generated registry | `{st['registry_hash']}` |
| `reg/requirements.schema.json` | generated schema | `{sha256_bytes(sch_text.encode())}` |
| `reg/status-transitions.json` | transition ledger (append-only) | `{sha256_bytes(ledger_text.encode())}` |
{''.join(f'| `{f}` | input authority | `{h}` |' + chr(10) for f, h in I.hashes.items())}
The generated hash is a function of the input hashes above and of `reg/_compile.py`. Re-running `python3 reg/_compile.py --write` on the same inputs reproduces it exactly; if it does not, the checker reports the drift and fails.
"""


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def compile_all(I: Inputs):
    reg = build_registry(I)
    sch = schema()
    committed = (REPO / REGISTRY_JSON).read_bytes() if (REPO / REGISTRY_JSON).exists() else None
    res, st = battery(I, reg, sch, committed)
    lifted = lifted_atomic_dependencies(I, [r["id"] for r in reg["requirements"]])
    ledger_path = REPO / LEDGER_JSON
    ledger_text = ledger_path.read_text(encoding="utf-8") if ledger_path.exists() else render_json(
        {"ledger": "R-REG status-transition ledger (append-only; historical entries immutable)",
         "entry_fields": ["requirement_id", "previous_status", "new_status", "evidence",
                          "verification_method", "repository_revision", "timestamp",
                          "justification", "skip_justification", "approved_by"],
         "transitions": []})
    sch_text = render_json(sch)
    files = {
        REGISTRY_JSON: render_json(reg),
        SCHEMA_JSON: sch_text,
        LEDGER_JSON: ledger_text,
        "reg/00-overview.md": render_overview(reg, st),
        "reg/01-compilation-report.md": render_compilation(reg, st, res, I),
        "reg/02-identity-diff-report.md": render_identity(reg, st, I),
        "reg/03-status-transition-audit-model.md": render_status_model(reg, st),
        "reg/04-provenance-report.md": render_provenance(reg, st, I),
        "reg/05-dependency-integrity-report.md": render_dependency(reg, st, I, lifted),
        "reg/06-evidence-coverage-summary.md": render_evidence(reg, st, I),
        "reg/07-security-relevance-summary.md": render_security(reg, st),
        "reg/08-determinism-hash-report.md": render_hash(reg, st, I, sch_text, ledger_text),
    }
    return files, res, st


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--write", action="store_true", help="render reg/* after a green battery")
    ap.add_argument("-q", "--quiet", action="store_true")
    args = ap.parse_args()
    try:
        I = Inputs()
        files, res, st = compile_all(I)
    except Fail as exc:
        print(f"FAIL  authority conflict: {exc}")
        return 1
    fails = [l for o, l in res if not o]
    if not args.quiet:
        for o, l in res:
            print(("OK   " if o else "FAIL ") + l)
    if args.write:
        # point 19 legitimately fails before the first write / after an authority change
        hard = [l for l in fails if not l.startswith("19")]
        if hard:
            print("\n(--write aborted because the battery failed)")
            return 1
        for rel, text in files.items():
            (REPO / rel).parent.mkdir(parents=True, exist_ok=True)
            (REPO / rel).write_text(text, encoding="utf-8")
        rev = subprocess.run(["git", "rev-parse", "HEAD"], cwd=REPO, capture_output=True, text=True)
        print(f"\nwrote {len(files)} files under reg/ at repository revision "
              f"{rev.stdout.strip() or 'unknown'}; registry hash {st['registry_hash']}")
        return 0
    drift = [rel for rel, text in files.items()
             if not (REPO / rel).exists() or (REPO / rel).read_text(encoding="utf-8") != text]
    for rel in drift:
        print(f"FAIL drift: {rel} differs from a fresh compilation (regenerate with --write)")
    print(f"\n{'R-REG PASS' if not fails and not drift else 'R-REG FAIL'}: {st['count']}/{EXPECTED_COUNT} "
          f"identity; status {st['status_distribution']}; registry {st['registry_hash'][:23]}…")
    return 1 if (fails or drift) else 0


if __name__ == "__main__":
    raise SystemExit(main())
