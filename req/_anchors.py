"""Shared provenance constants for the Red-on-Rust requirement registry.

Every number here is derived from the frozen source `Red-on-Rust.md`
(42,312 lines) and from the canonicalization set in `spec/`.  Nothing is
inferred: values were obtained by direct `grep -n` / line-range reads during
extraction, and `req/_validate.py` re-greps the source to confirm them.
"""

from __future__ import annotations

import pathlib
import re

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
SOURCE_SPEC = REPO_ROOT / "Red-on-Rust.md"
REQ_DIR = REPO_ROOT / "req"
CANONICAL_SPEC = REPO_ROOT / "spec" / "01-canonical-specification.md"

# Hard provenance bound: the frozen source is exactly this many lines.
SOURCE_MAX_LINE = 42312

FIELDS = [
    "REQ-ID",
    "CATEGORY",
    "SOURCE",
    "NORMATIVE-LEVEL",
    "STATEMENT",
    "PRECONDITIONS",
    "POSTCONDITIONS",
    "INVARIANTS",
    "DEPENDENCIES",
    "SECURITY-IMPACT",
    "VERIFICATION-METHOD",
    "EVIDENCE-STATUS",
]

NORMATIVE_LEVELS = {
    "MUST",
    "MUST NOT",
    "SHOULD",
    "MAY",
    "IS",
    "NON-NORMATIVE",
    "AMBIGUOUS",
}

EVIDENCE_STATES = {"SPECIFIED", "IMPLEMENTED", "TESTED", "VERIFIED", "PROVEN", "UNKNOWN"}

AREAS = [
    "SCOPE", "CORE", "TRUST", "ARCH", "PLANNER", "COMPILE", "CALC", "CEK", "CAP",
    "KERN", "BUDGET", "EFFECT", "DUR", "HOST", "ACTOR", "MARSHAL", "CANON",
    "PERSIST", "RECOV", "REF", "TEST", "REPO", "ORDER", "CLAIM",
]

# ---------------------------------------------------------------------------
# Frozen line anchors.  Verified by grep during extraction; `_validate.py`
# re-checks each one against the source on every run.
# ---------------------------------------------------------------------------
ANCHORS: dict[str, int] = {
    "PlanProposal": 27175,
    "StalePlan": 27236,
    "PlannerAccepted": 27411,
    "Expr": 12145,
    "Value": 12283,
    "Fault": 23806,
    "Frame": 16943,
    "EvalState": 12655,
    "execute_spawn": 25624,
    "pub struct GlobalSnapshot": 26301,
    "Spawn": 12190,
    "fn execute_spawn": 25931,
    "Deadlock": 25579,
    "ActorSelected": 25567,
    "MarshalFault": 25685,
    "Delegate": 25989,
    "MarshalResult": 9905,
    "Continuation": 12517,
    "ReadCursor": 30723,
    "EventSequence": 31697,
    "WalFrame": 35099,
    "WalRecord": 35127,
    "GlobalSnapshot": 35181,
    "GlobalState": 24156,
    "CanonicalError": 32959,
    "AuthorityNode": 39373,
    "PanicHost": 27901,
    "M001": 38477,
    "MutationKillRate": 38506,
    "ROR-001": 41014,
}

# Frozen verification tags (spec/08 §1, Red-on-Rust.md L38544-38565).
FROZEN_TAGS = [
    "CEK-CALL-ARITY-PRECHECK",
    "CEK-CALL-ARGS-LTR",
    "CEK-CLOSURE-LEXICAL-CAPTURE",
    "CAP-DERIVE-NO-AMPLIFICATION",
    "CAP-REVOCATION-ANCESTOR",
    "BUDGET-CONSUMPTION-CONSERVATION",
    "BUDGET-ESCROW-CONSERVATION",
    "EFFECT-ISSUE-DURABLE-BEFORE-HOST",
    "EFFECT-RECEIPT-DIGEST-VALIDATION",
    "SCHED-FIFO",
    "SCHED-BLOCKED-NOT-SCHEDULED",
    "MARSHAL-NO-RAW-CAPABILITY",
    "WAL-SEQUENCE-CONTINUITY",
    "RECOVERY-ISSUED-INDETERMINATE",
    "SNAPSHOT-COMMIT-INTEGRITY",
    "WAL-GAP-REJECT",
]

LINE_CITE = re.compile(r"L(\d{1,6})(?:\s*[–-]\s*L?(\d{1,6}))?")
PARENT_OBLIGATION = re.compile(r"\bR-([A-Z]+)-(\d{2,3})\b")
RECORD_ID = re.compile(r"\bREQ-([A-Z]+)-(\d{3})\b")
IDENTIFIER = re.compile(r"`([A-Za-z_][A-Za-z0-9_]*(?:::[A-Za-z0-9_]+)*)`")
TURN_HEADER = re.compile(r"^## \[(\d+)\] ")


def read_source_lines() -> list[str]:
    return SOURCE_SPEC.read_text(encoding="utf-8").split("\n")


def turn_starts(lines: list[str]) -> list[tuple[int, int]]:
    """`[(turn_number, first_line), …]` re-derived from the source itself."""
    return [
        (int(m.group(1)), i + 1)
        for i, line in enumerate(lines)
        if (m := TURN_HEADER.match(line))
    ]


def turn_of(line_no: int, starts: list[tuple[int, int]]) -> int | None:
    turn = None
    for number, first in starts:
        if first <= line_no:
            turn = number
        else:
            break
    return turn


def load_registry_records() -> list[dict]:
    """Parse every `### REQ-…` record from `req/01-registry-part*.md`."""
    records: list[dict] = []
    for path in sorted(REQ_DIR.glob("01-registry-part*.md")):
        text = path.read_text(encoding="utf-8")
        blocks = re.split(r"^### ", text, flags=re.M)[1:]
        for block in blocks:
            header, _, body = block.partition("\n")
            rid = header.strip()
            if not RECORD_ID.fullmatch(rid):
                continue
            rec = {"REQ-ID": rid, "_file": path.name, "_fields": []}
            for line in body.split("\n"):
                if not line.startswith("- "):
                    if line.startswith("#"):
                        break
                    continue
                key, _, value = line[2:].partition(":")
                key = key.strip()
                if key in FIELDS:
                    if key == "REQ-ID":
                        # the header is authoritative; keep the field for the
                        # consistency check in _validate.py
                        rec["_id_field"] = value.strip()
                    else:
                        rec[key] = value.strip()
                    rec["_fields"].append(key)
            records.append(rec)
    return records


def cited_ranges(source_field: str) -> list[tuple[int, int]]:
    """All `L<a>–L<b>` ranges cited in a SOURCE field, as inclusive spans."""
    return [(lo, hi) for lo, hi, _ in cited_citations(source_field)]


def cited_citations(source_field: str) -> list[tuple[int, int, int | None]]:
    """Each cited range together with the `[turn]` marker that follows it."""
    out: list[tuple[int, int, int | None]] = []
    for m in LINE_CITE.finditer(source_field):
        start = int(m.group(1))
        end = int(m.group(2)) if m.group(2) else start
        tail = source_field[m.end():]
        marker = re.match(r"\s*\(\[(\d+)", tail)
        out.append(
            (min(start, end), max(start, end), int(marker.group(1)) if marker else None)
        )
    return out


def parent_obligations(source_field: str) -> list[str]:
    return [m.group(0) for m in PARENT_OBLIGATION.finditer(source_field)]
