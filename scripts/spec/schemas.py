"""scripts/spec/schemas.py — JSON schemas for the pipeline's own artifacts.

These schemas describe the *shape of the derived artifacts*, so that a reader or
a later tool can validate a `build/spec/` file without reading the generator.
They are additive and non-normative: they constrain the pipeline's output, not
the specification.  The repository's requirement registry already has its own
schema (`reg/requirements.schema.json`), which stays authoritative for
`reg/requirements.json`; this module does not redefine it (R-SCOPE-03: no
competing register).
"""
from __future__ import annotations

from _common import EVIDENCE_CEILING, FINDING_SEVERITIES, LEVEL_VOCAB, NORMATIVE_CLASSES

STATUS = {"enum": ["SPECIFIED", "IMPLEMENTED", "TESTED", "VERIFIED", "PROVEN"]}
LINE_REF = {"type": "object", "required": ["path", "start", "end"], "properties": {
    "path": {"const": "Red-on-Rust.md"}, "start": {"type": "integer", "minimum": 1},
    "end": {"type": "integer", "minimum": 1}}}


def _provenance(stage_prefix: str) -> dict:
    return {
        "type": "object",
        "required": ["pipeline", "pipeline_version", "stage", "generator", "source", "inputs",
                     "timestamp_present"],
        "properties": {
            "pipeline": {"const": "redonrust-spec-pipeline"},
            "pipeline_version": {"type": "string", "pattern": r"^\d+\.\d+\.\d+$"},
            "stage": {"type": "string", "pattern": f"^{stage_prefix}"},
            "generator": {"type": "string"},
            "source": {"type": "object", "required": ["path", "sha256"]},
            "inputs": {"type": "array", "items": {"type": "object",
                                                  "required": ["path", "sha256"]}},
            "timestamp_present": {"const": False},
        },
        "additionalProperties": True,
    }


def requirement_entry() -> dict:
    return {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "title": "pipeline requirements registry entry (build/spec/requirements.json)",
        "description": ("Every value is copied or mechanically derived from spec/01 + spec/03. "
                        "No field may assert an evidence status above SPECIFIED, and no identity may "
                        "be introduced that the canonical registry does not define."),
        "type": "object",
        "required": ["id", "status", "normative_class", "section_refs", "source_refs",
                     "provenance_kind", "canonical_text_home", "identity_basis", "statement_sha256"],
        "properties": {
            "id": {"type": "string", "pattern": r"^R-[A-Z]+-\d+$"},
            "status": {**STATUS, "const": EVIDENCE_CEILING,
                       "x-ceiling": ("the pipeline cannot promote: spec/00 §2 makes SPECIFIED the "
                                      "ceiling while the repository contains no implementation")},
            "normative_class": {"enum": NORMATIVE_CLASSES},
            "normative_level": {"anyOf": [{"type": "null"}, {"enum": LEVEL_VOCAB}]},
            "section_refs": {"type": "array", "minItems": 1, "items": {"pattern": r"^S-\d{2}$"}},
            "source_refs": {"type": "array", "items": {"type": "string",
                                                        "pattern": r"^Red-on-Rust\.md:L\d+"}},
            "provenance_kind": {"enum": ["frozen-source-cited", "frozen-addendum", "registry-cited",
                                        "section-inherited"]},
            "addendum_note": {"type": ["string", "null"]},
            "canonical_text_home": {"type": "object", "required": ["document", "section",
                                                                  "line_start", "line_end",
                                                                  "text_sha256"]},
            "dependencies": {"type": "array", "items": {"type": "string"}},
            "verification_refs": {"type": "array", "items": {"type": "string"}},
            "implementation_targets": {"type": "array", "items": {"type": "string"}},
            "identity_basis": {"type": "string"},
            "statement_sha256": {"type": "string", "pattern": r"^sha256:[0-9a-f]{64}$"},
        },
        "additionalProperties": True,
    }


def finding_entry() -> dict:
    return {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "title": "audit finding entry (build/spec/audit.json findings[])",
        "description": ("§11 field set. `proposed_resolution` may be empty — an empty resolution is a "
                        "recorded absence, not an omission to be filled by the generator."),
        "type": "object",
        "required": ["finding_id", "category", "severity", "source_refs", "affected_artifacts",
                     "description", "proposed_resolution", "authority_required", "status"],
        "properties": {
            "finding_id": {"type": "string", "pattern": r"^[CU]-\d{2,3}$"},
            "category": {"type": "string"},
            "severity": {"enum": FINDING_SEVERITIES + ["BLOCKING", "HIGH", "MEDIUM", "LOW", "INFO",
                                                       "CRITICAL"]},
            "source_refs": {"type": "array", "items": {"type": "string"}},
            "affected_artifacts": {"type": "array", "items": {"type": "string"}},
            "description": {"type": "string", "minLength": 1},
            "proposed_resolution": {"type": "string"},
            "authority_required": {"type": "boolean"},
            "status": {"enum": ["open", "resolved", "resolved-by-addendum", "resolved-by-later-text",
                               "recorded", "superseded", "info"]},
        },
        "additionalProperties": True,
    }


def vector_entry() -> dict:
    return {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "title": "evidence vector entry (build/spec/vectors/*.json)",
        "type": "object",
        "required": ["vector_id", "family", "label", "authority", "status"],
        "properties": {
            "vector_id": {"type": "string", "pattern": r"^VEC-(CANON|PERSIST|EFFECT)-\d{2}$"},
            "family": {"enum": ["canonical", "persistence", "effects"]},
            "canonical_bytes": {"type": "string", "pattern": r"^(?:[0-9A-F]{2}(?: [0-9A-F]{2})*)?$"},
            "byte_length": {"type": "integer", "minimum": 0},
            "authority": {"type": "object", "required": ["document"]},
            "status": {**STATUS, "const": EVIDENCE_CEILING},
        },
        "additionalProperties": True,
    }


def snapshot_doc() -> dict:
    return {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "title": "source snapshot (build/spec/snapshot.json)",
        "type": "object",
        "required": ["schema", "provenance", "snapshot", "checks", "policy"],
        "properties": {
            "provenance": _provenance("S0"),
            "snapshot": {"type": "object", "required": ["lines", "bytes", "sha256_raw"],
                         "properties": {"lines": {"const": 42312}}},
            "policy": {"type": "object", "properties": {
                "semantic_modification_performed": {"const": False}}},
        },
        "additionalProperties": True,
    }


def manifest_doc() -> dict:
    return {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "title": "render manifest (build/spec/manifest.json)",
        "description": ("Content-addressed staleness record: an artifact on disk whose digest is not "
                        "listed is stale (§14).  No timestamp participates."),
        "type": "object",
        "required": ["schema", "render_hash", "pipeline_version", "source", "artifact_count",
                     "artifacts", "timestamp_present"],
        "properties": {
            "render_hash": {"type": "string", "pattern": r"^sha256:[0-9a-f]{64}$"},
            "source": {"type": "object", "required": ["path", "sha256"]},
            "artifacts": {"type": "object", "propertyNames": {"type": "string"},
                          "additionalProperties": {"pattern": r"^sha256:[0-9a-f]{64}$"}},
            "timestamp_present": {"const": False},
        },
        "additionalProperties": True,
    }


ALL = {
    "schemas/requirements.schema.json": requirement_entry(),
    "schemas/finding.schema.json": finding_entry(),
    "schemas/vector.schema.json": vector_entry(),
    "schemas/snapshot.schema.json": snapshot_doc(),
    "schemas/manifest.schema.json": manifest_doc(),
}


def render_files() -> dict:
    from _common import render_json
    return {rel: render_json(doc) for rel, doc in sorted(ALL.items())}
