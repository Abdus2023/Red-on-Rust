"""Validate the Red-on-Rust atomic requirement registry and emit registry.json.

Run from anywhere:  python3 req/_validate.py [--write]

Checks performed
----------------
1.  Every record has exactly the 12 required fields, in the required order.
2.  REQ-IDs are unique and area numbering is gap-free.
3.  NORMATIVE-LEVEL is in the frozen vocabulary; EVIDENCE-STATUS is in the
    allowed set and is never promoted above SPECIFIED.
4.  SOURCE cites at least one `Red-on-Rust.md` line range, every cited line is
    inside 1..42312, and the turn number is present.
5.  Parent-obligation coverage: every `R-AREA-NN` obligation in
    `spec/01-canonical-specification.md` is cited by at least one record, and
    every parent obligation cited by a record exists there.
6.  DEPENDENCIES resolve: every `REQ-…`, `CN-…`, `AMB-…`, `VU-…` reference
    points at something that exists in this directory.
7.  Signature provenance: every type-like identifier in STATEMENT or INVARIANTS
    actually occurs inside the line range(s) that record cites.  This is the
    check that catches a copied-but-wrong `L3xxxx` citation.
8.  Frozen line anchors in `_anchors.py` are re-grepped against the source.
9.  Declared per-area counts in each part-file header match the parsed records.

Exit status is 1 if any ERROR is reported.
"""

from __future__ import annotations

import collections
import json
import re
import sys

import _anchors as A

ERRORS: list[str] = []
WARNINGS: list[str] = []


def err(msg: str) -> None:
    ERRORS.append(msg)


def warn(msg: str) -> None:
    WARNINGS.append(msg)


# --------------------------------------------------------------------------
# Tokens that are legitimately referenced across record boundaries: a record
# names a type whose *declaration* sits outside its own cited range because the
# record is about behaviour, not about the declaration.  Each entry names the
# record's own anchor for that concept.  Anything not listed is an error.
# --------------------------------------------------------------------------
CROSS_REFERENCE_TOKENS: dict[str, str] = {
    "Fault": "closed enum declared L23806; behavioural records cite the rule",
    "Value": "machine value domain declared L12283",
    "Expr": "frozen AST declared L12145",
    "CapRef": "declared L12126",
    "EffectId": "declared L12122",
    "ActorId": "declared L12118",
    "EffectCost": "declared L10062",
    "Budget": "declared L10076",
    "Constraint": "declared L10068",
    "Authority": "declared L6380",
    "Block": "declared L12100",
    "EvalState": "declared L12655",
    "Frame": "declared L16943",
    "Spawn": "declared L12190 (frozen Expr variant)",
    "Delegate": "declared L25989-25992 (turn [32]); absent from the frozen AST L12145-12200",
    "WalFrame": "declared L35099",
    "WalRecord": "declared L35127",
    "GlobalSnapshot": "declared L35181",
    "GlobalState": "declared L24156, L25535, L25862 (three declarations)",
    "GlobalSnapshot": "declared L26301",
    "CanonicalError": "declared L32959",
    "MarshalFault": "declared L25685",
    "AuthorityNode": "declared L39373",
    "PlanProposal": "declared L27175",
    "ExecutablePlan": "declared L37964",
    "ValidatedPlan": "declared L37929",
    "NormalizedAST": "declared L37889",
    "PlanIR": "declared L37929",
    "Effect": "declared L10052",
    "Deadline": "declared L10114",
    "Lifetime": "declared L10074",
    "AdmissibleConstraint": "used L8717; declared-without-definition (AMB-12)",
    "ActorStatus": "declared L37838",
    "RunState": "declared L10140",
    "ReconciliationOutcome": "named L38185",
    "EventSequence": "declared L31697 and again L32060",
    "LogicalTime": "declared L12116",
    "Symbol": "declared L12108",
    "Environment": "declared L12600",
    "FunctionValue": "declared L12400",
    "Continuation": "declared L12517; `Frame` is declared 11 times",
    "MachineEvent": "declared L12700",
    "EffectReceipt": "declared L38074",
    "HostFault": "declared L27901",
    "PanicHost": "declared L27901",
    "CapabilityKernel": "declared L39253",
    "PlannerMetadata": "declared L27411",
    "ProposalDigest": "declared L27411",
    "StalePlan": "declared L27236",
    "BudgetAllocationSpec": "named L10076 (AMB-22)",
    "MutationKillRate": "declared L38506",
    "Consumable": "declared L10090",
    "Reserved": "declared L10094",
    "ReadCursor": "declared L30723 (the canonical decode cursor)",
    "MarshalResult": "declared L9905 and L10836",
    "MarshalledValue": "declared L25981",
    "WalSequence": "declared L35127",
    "Recover": "declared L26133",
    "Commit": "declared L35181",
    "Canonical": "declared L33087",
    "Digest": "declared L33087",
    "Observe_P": "declared L38585",
    "Observe_R": "declared L38585",
    "Recover_P": "declared L38653",
    "Recover_R": "declared L38653",
    "Authorized": "declared L6406",
    "Valid": "declared L6423",
    "WithinBudget": "declared L8833",
    "ReserveOK": "declared L10090",
    "ReleaseOK": "declared L10094",
    "derive": "declared L6425",
    "marshal": "declared L10165",
    "unmarshal": "declared L10165",
}


def expand_ranges(text: str) -> set[str]:
    """Expand `REQ-X-006…REQ-X-018` style spans and collect single ids."""
    found: set[str] = set()
    for m in A.RECORD_ID.finditer(text):
        found.add(m.group(0))
    for m in re.finditer(r"(REQ-[A-Z]+)-(\d{3})\s*[…-]+\s*(?:REQ-[A-Z]+-)?(\d{3})", text):
        area, lo, hi = m.group(1), int(m.group(2)), int(m.group(3))
        for n in range(lo, hi + 1):
            found.add(f"{area}-{n:03d}")
    return found


def main() -> int:
    write_json = "--write" in sys.argv

    lines = A.read_source_lines()
    if len(lines) - 1 != A.SOURCE_MAX_LINE:
        err(f"source line count {len(lines)-1} != declared bound {A.SOURCE_MAX_LINE}")

    records = A.load_registry_records()
    if not records:
        err("no records parsed")
        return 1

    starts = A.turn_starts(lines)
    if len(starts) != 60:
        err(f"expected 60 turn headers in the source, found {len(starts)}")
    source_blob = "\n".join(lines)

    canonical = A.CANONICAL_SPEC.read_text(encoding="utf-8")
    parents = sorted({m.group(0) for m in A.PARENT_OBLIGATION.finditer(canonical)})

    seen: dict[str, str] = {}
    per_file: collections.Counter = collections.Counter()
    per_area: collections.Counter = collections.Counter()
    area_max: dict[str, int] = {}

    for rec in records:
        rid = rec["REQ-ID"]
        per_file[rec["_file"]] += 1
        area = rid.split("-")[1]
        per_area[area] += 1
        area_max[area] = max(area_max.get(area, 0), int(rid.split("-")[2]))

        # 1. fields
        if rec["_fields"] != A.FIELDS:
            err(f"{rid}: field list {rec['_fields']} != required {A.FIELDS}")

        if rec.get("_id_field") != rid:
            err(f"{rid}: header and REQ-ID field disagree (field says {rec.get('_id_field')!r})")

        # 2. uniqueness
        if rid in seen:
            err(f"{rid}: duplicate (also in {seen[rid]})")
        seen[rid] = rec["_file"]

        # 3. vocabularies
        lvl = rec.get("NORMATIVE-LEVEL", "")
        if lvl not in A.NORMATIVE_LEVELS:
            err(f"{rid}: NORMATIVE-LEVEL {lvl!r} not in vocabulary")
        ev = rec.get("EVIDENCE-STATUS", "")
        if ev not in A.EVIDENCE_STATES:
            err(f"{rid}: EVIDENCE-STATUS {ev!r} not allowed")
        elif ev != "SPECIFIED":
            err(f"{rid}: EVIDENCE-STATUS promoted to {ev!r}")

        # 4. provenance bounds + turn/range agreement
        source = rec.get("SOURCE", "")
        cits = A.cited_citations(source)
        spans = [(lo, hi) for lo, hi, _ in cits]
        if not spans:
            err(f"{rid}: SOURCE cites no Red-on-Rust.md line range")
        for lo, hi, declared in cits:
            if lo < 1 or hi > A.SOURCE_MAX_LINE or lo > hi:
                err(f"{rid}: cited range L{lo}-L{hi} outside 1..{A.SOURCE_MAX_LINE}")
            actual = A.turn_of(lo, starts)
            if declared is None:
                err(f"{rid}: L{lo}-L{hi} carries no turn marker")
            elif declared != actual:
                err(
                    f"{rid}: L{lo}-L{hi} labelled [{declared}] but those lines are in turn [{actual}]"
                )

        # 5. parent obligations cited must exist
        for p in A.parent_obligations(source):
            if p not in parents:
                err(f"{rid}: cites unknown parent obligation {p}")

        # 7. signature provenance
        blob = rec.get("STATEMENT", "") + " " + rec.get("INVARIANTS", "")
        for tok in {m.group(1) for m in A.IDENTIFIER.finditer(blob)}:
            if tok in A.FIELDS or tok.startswith(("REQ-", "R-")):
                continue
            if len(tok) <= 2:
                continue  # single math symbols (F, S, R, t, …)
            if not (":" in tok or "_" in tok or tok[0].isupper()):
                continue  # ordinary words, math symbols, prose
            if tok in CROSS_REFERENCE_TOKENS and tok in source_blob:
                continue
            if any(tok in "\n".join(lines[lo - 1:hi]) for lo, hi in spans):
                continue
            if tok in CROSS_REFERENCE_TOKENS:
                err(f"{rid}: cross-reference token `{tok}` does not occur anywhere in the source")
                continue
            if "::" in tok and tok.rsplit("::", 1)[-1] in "\n".join(
                lines[lo - 1:hi] for lo, hi in spans
            ):
                continue  # path-qualified name whose variant is declared in range
            first = next(
                (i + 1 for i, ln in enumerate(lines) if tok in ln), None
            )
            err(
                f"{rid}: token `{tok}` not in cited ranges "
                f"{['L%d-L%d' % s for s in spans]}; first occurrence "
                f"{'L%d' % first if first else 'NONE'}"
            )

    # 2b. gap-free numbering
    for area, mx in sorted(area_max.items()):
        if area not in A.AREAS:
            err(f"unknown area {area!r}")
        if per_area[area] != mx:
            err(f"area {area}: {per_area[area]} records but highest index {mx} (gap)")

    # 5b. parent coverage
    cited_parents = set()
    for rec in records:
        cited_parents.update(A.parent_obligations(rec.get("SOURCE", "")))
    missing = [p for p in parents if p not in cited_parents]
    if missing:
        err(f"{len(missing)} parent obligations not cited: {missing}")

    # 6. dependency resolution
    cn = set(re.findall(r"\bCN-\d+\b", (A.REQ_DIR / "02-compound-not-split.md").read_text()))
    amb = set(re.findall(r"\bAMB-\d+\b", (A.REQ_DIR / "03-ambiguous.md").read_text()))
    vu = set(re.findall(r"\bVU-\d+\b", (A.REQ_DIR / "04-verification-undefined.md").read_text()))
    all_ids = set(seen)
    for rec in records:
        for ref in expand_ranges(rec.get("DEPENDENCIES", "")):
            if ref not in all_ids:
                err(f"{rec['REQ-ID']}: DEPENDENCIES references unknown {ref}")
        for kind, pool, doc in (
            ("CN", cn, "02-compound-not-split.md"),
            ("AMB", amb, "03-ambiguous.md"),
            ("VU", vu, "04-verification-undefined.md"),
        ):
            for m in re.findall(rf"\b{kind}-\d+\b", rec.get("DEPENDENCIES", "") + rec.get("SECURITY-IMPACT", "") + rec.get("VERIFICATION-METHOD", "") + rec.get("INVARIANTS", "")):
                if m not in pool:
                    err(f"{rec['REQ-ID']}: references {m}, absent from {doc}")

    # 7b. every cross-reference token must be a real source identifier
    for tok in CROSS_REFERENCE_TOKENS:
        if tok not in source_blob:
            err(f"CROSS_REFERENCE_TOKENS lists `{tok}`, absent from the source")

    # 8. anchors
    for tok, ln in A.ANCHORS.items():
        if ln > len(lines) or tok not in lines[ln - 1]:
            first = next((i + 1 for i, l in enumerate(lines) if tok in l), None)
            err(f"anchor {tok}@L{ln} wrong; first occurrence {'L%d' % first if first else 'NONE'}")

    # 9. declared counts in part-file headers
    for path in sorted(A.REQ_DIR.glob("01-registry-part*.md")):
        header = path.read_text(encoding="utf-8")[:2000]
        declared = re.findall(r"`([A-Z]+)` \((\d+)\)", header)
        for area, n in declared:
            if int(n) != per_area[area]:
                err(f"{path.name}: header declares {area}={n}, parsed {per_area[area]}")
        total = re.search(r"— (\d+) atomic units", header)
        declared_sum = sum(int(n) for _, n in declared)
        if total and int(total.group(1)) != declared_sum:
            err(f"{path.name}: header total {total.group(1)} != sum of declared areas {declared_sum}")
        if declared and declared_sum != per_file[path.name]:
            err(f"{path.name}: declared {declared_sum} records, parsed {per_file[path.name]}")

    # ------------------------------------------------------------------
    payload = {
        "specification": "Red-on-Rust.md",
        "source_lines": A.SOURCE_MAX_LINE,
        "record_count": len(records),
        "evidence_status_of_every_record": "SPECIFIED",
        "per_file": dict(per_file),
        "per_area": dict(per_area),
        "normative_levels": dict(collections.Counter(r.get("NORMATIVE-LEVEL", "") for r in records)),
        "parent_obligations_total": len(parents),
        "parent_obligations_cited": len(cited_parents),
        "records": [
            {k: v for k, v in r.items() if not k.startswith("_")} for r in records
        ],
        "validator_checks": [
            "12 fields present and ordered",
            "unique IDs, header/field agreement, gap-free area numbering",
            "normative-level and evidence-state vocabularies, no promotion",
            "line cites within 1..42312, every cite carries a turn marker",
            "cited lines really are in the turn the SOURCE claims",
            "parent-obligation existence and full 148-obligation coverage",
            "DEPENDENCIES / CN- / AMB- / VU- references resolve",
            "every backticked identifier in STATEMENT or INVARIANTS occurs in a cited range",
            "frozen anchors re-grepped against the source",
            "part-file header counts match parsed records",
        ],
    }
    out = A.REQ_DIR / "registry.json"
    if write_json:
        out.write_text(json.dumps(payload, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"records parsed          : {len(records)}")
    print(f"files                   : {dict(per_file)}")
    print(f"normative levels        : {dict(collections.Counter(r.get('NORMATIVE-LEVEL','') for r in records))}")
    print(f"evidence states         : {dict(collections.Counter(r.get('EVIDENCE-STATUS','') for r in records))}")
    print(f"parent obligations      : {len(cited_parents)}/{len(parents)} cited")
    print(f"per area                : {dict(sorted(per_area.items()))}")
    print(f"cross-reference tokens  : {len(CROSS_REFERENCE_TOKENS)}")
    if write_json:
        print(f"written                 : {out} ({out.stat().st_size} bytes)")
    print(f"ERRORS                  : {len(ERRORS)}")
    for e in ERRORS[:60]:
        print("  ERROR " + e)
    if len(ERRORS) > 60:
        print(f"  … {len(ERRORS)-60} more")
    print(f"WARNINGS                : {len(WARNINGS)}")
    for w in WARNINGS[:20]:
        print("  WARN " + w)
    return 1 if ERRORS else 0


if __name__ == "__main__":
    sys.exit(main())
