#!/usr/bin/env python3
"""Mechanical crash-consistency audit gate.

Why it exists
-------------
The audit `audit/persistence-crash-consistency-audit.md` verifies, by hand, that
the persistence contract satisfies:

  Prepared -> Issued -> Completed / Reconciled
  Issued(E) => Prepared(E)
  Completed(E) => Issued(E)
  Reconciled(E) => Issued(E)
  HostInvoked(E) => DurableIssued(E)
  Prepared ^ -Issued => Discard
  Issued ^ -Completed => Indeterminate   (never automatically NotExecuted)
  Invalid(D) => RecoveryFault            (never silently repaired)

This checker re-derives those properties from the frozen registries/spec so a
future edit that weakens them is a hard gate failure rather than a silent drift.

It checks *presence of the normative clauses* in the active documents. It is NOT
a semantic verifier of the addenda text: a clause quoted as superseded in the
same document is still present, so the checker must not be used as evidence that
a superseded *ordering* is normative. The ordering questions are covered by the
requirement IDs and the R-CORE-14/R-DUR-06/R-DUR-07/R-RECOV-09 addenda blocks.

Run as part of `python3 check.py`.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

REG_DUR = REPO / "req/01-registry-part4-durability-concurrency.md"
REG_RECOV = REPO / "req/01-registry-part5-persistence.md"
SPEC = REPO / "spec/01-canonical-specification.md"
MOD_DUR = REPO / "mod/11-persistence.md"
MOD_RECOV = REPO / "mod/12-recovery.md"
AUDIT = REPO / "audit/persistence-crash-consistency-audit.md"


def norm(s: str) -> str:
    """Collapse whitespace so markdown/backtick formatting does not hide clauses."""
    return re.sub(r"\s+", " ", s)


def text(path: Path) -> str:
    return norm(path.read_text(encoding="utf-8"))


def req_block(source: str, req_id: str) -> str | None:
    """Return the normalized text of `### REQ-ID ...` (or its addendum paragraph).

    Registry records use `### REQ-DUR-001`. The canonical spec uses additive
    `**R-DUR-06 ...**` paragraphs; those are matched by the R- ID directly.
    """
    if "REQ-" in req_id:
        m = re.search(
            rf"###\s+{re.escape(req_id)}\b(.*?)(?=\n###\s+|\Z)", source, re.S
        )
        return norm(m.group(1)) if m else None
    # A spec addendum is a single `**R-...** ... *(Frozen addendum ...)*`
    # paragraph. Capture from the ID marker through the end of the paragraph.
    m = re.search(
        rf"\*\*{re.escape(req_id)}\b.*?(?=\n\*\*[A-Z][A-Z0-9-]+ |\Z)",
        source,
        re.S,
    )
    return norm(m.group(0)) if m else None


def check_contains(text_: str, needles: list[str], label: str) -> list[str]:
    """Return a list of failure messages; empty means the clause is present."""
    out = []
    for needle in needles:
        if needle not in text_:
            out.append(f"{label}: missing clause {needle!r}")
    return out


def collect() -> list[str]:
    failures: list[str] = []

    dur = text(REG_DUR)
    recov = text(REG_RECOV)
    spec = text(SPEC)
    mod_dur = text(MOD_DUR)
    mod_recov = text(MOD_RECOV)
    audit = text(AUDIT)

    # ------------------------------------------------------------------
    # 0. The audit document itself exists (the gate is anchored to it).
    # ------------------------------------------------------------------
    if "PASS" not in audit:
        failures.append(
            "audit/persistence-crash-consistency-audit.md: "
            "audit absent or does not carry the PASS verdict"
        )

    # ------------------------------------------------------------------
    # 1. Required causal ordering (requested unit-level law).
    # ------------------------------------------------------------------
    for req, needles in [
        ("REQ-DUR-001", ["HostInvoked(E) ⇒ DurableIssued(E)"]),
        ("REQ-DUR-002", [
            "append(EffectPrepared", "sync()", "append(EffectIssued",
            "actor", "Pending", "host adapter receives",
        ]),
        ("REQ-DUR-005", ["Issued(E) ⇒ Prepared(E)"]),
        ("REQ-DUR-006", ["Completed(E) ⇒ Issued(E)"]),
        ("REQ-DUR-007", ["Reconciled(E) ⇒ Issued(E)"]),
        ("REQ-DUR-008", [
            "identical", "EffectId", "EffectDigest",
            "Prepared", "Issued", "Completed", "Reconciled",
        ]),
        ("REQ-DUR-009", ["EffectJournalCorruption", "not a different effect"]),
        ("REQ-DUR-010", ["Prepared ∧ ¬Issued ⇒ Discard", "budget"]),
        ("REQ-DUR-011", ["Issued ∧ ¬Completed ⇒ Indeterminate"]),
        ("REQ-DUR-012", [
            "NEVER automatically classified", "NotExecuted",
            "host may have executed",
        ]),
        ("REQ-DUR-013", [
            "escrowed", "completion_maximum", "until reconciliation",
        ]),
    ]:
        block = req_block(dur, req)
        if block is None:
            failures.append(f"{req}: record not found in {REG_DUR.name}")
            continue
        failures.extend(check_contains(block, needles, req))

    # Durable issuance transaction order is also frozen as addendum R-DUR-06/07.
    for req, needles in [
        ("R-DUR-06", [
            "effect_bytes", "complete_max", "reserve",
            "EffectDigest(effect_bytes) = digest",
            "T1", "T2", "T4", "T5",
        ]),
        ("R-DUR-07", [
            "Fault::PersistenceError",
            "Prepared ∧ ¬Issued ⇒ Discard",
            "pre-s12",
            "never panics",
        ]),
    ]:
        block = req_block(spec, req)
        if block is None:
            failures.append(f"{req}: addendum paragraph not found in {SPEC.name}")
            continue
        failures.extend(check_contains(block, needles, req))

    # ------------------------------------------------------------------
    # 2. Crash matrix T0-T6 (entrypoint rows).
    # ------------------------------------------------------------------
    t_rows = [
        ("REQ-RECOV-003", ["T0", "does not exist", "no budget mutation",
                           "resumes normally"]),
        ("REQ-RECOV-004", ["T1", "discarded", "resumes normally"]),
        ("REQ-RECOV-005", ["T2", "Indeterminate", "reconciliation"]),
        ("REQ-RECOV-006", ["T3", "Indeterminate", "host may have executed"]),
        ("REQ-RECOV-007", ["T4", "Indeterminate", "before a durable `Completed`"]),
        ("REQ-RECOV-008", ["T5", "reconstructed", "resumes"]),
        ("REQ-RECOV-009", ["T6", "snapshot", "base", "subsequent", "replay"]),
    ]
    for req, needles in t_rows:
        block = req_block(recov, req)
        if block is None:
            failures.append(f"{req}: record not found in {REG_RECOV.name}")
            continue
        failures.extend(check_contains(block, needles, req))

    # The module-level normative matrix must carry the same rows.
    for needle in ["T0", "T1", "T2", "T3", "T4", "T5", "T6",
                   "Indeterminate", "reconciliation required"]:
        if needle not in mod_recov:
            failures.append(f"mod/12-recovery.md: missing crash-matrix term {needle!r}")

    # ------------------------------------------------------------------
    # 3. Critical rule: issued-but-incomplete is never absent.
    # ------------------------------------------------------------------
    # Registry side. The formal `Indeterminate` law lives in REQ-DUR-011
    # (checked above); REQ-DUR-012 only carries the NEVER-NotExecuted half.
    failures.extend(check_contains(
        req_block(dur, "REQ-DUR-012") or "",
        ["NEVER automatically classified", "NotExecuted",
         "host may have executed"],
        "REQ-DUR-012",
    ))
    # Recovery side.
    failures.extend(check_contains(
        req_block(recov, "REQ-RECOV-017") or "",
        ["only path", "Indeterminate", "never auto-resolves", "not executed"],
        "REQ-RECOV-017",
    ))
    failures.extend(check_contains(
        mod_recov,
        ["Issued ∧ ¬Completed", "Indeterminate", "only resolution path",
         "never auto-resolves"],
        "mod/12-recovery.md",
    ))

    # R-RECOV-08 frozen addendum.
    rreco8 = req_block(spec, "R-RECOV-08")
    if rreco8 is None:
        failures.append("R-RECOV-08: addendum paragraph not found in spec/01")
    else:
        failures.extend(check_contains(
            rreco8,
            ["reconciliation", "NEVER re-executes", "NotExecuted",
             "authoritative host-reconciliation evidence", "admissible"],
            "R-RECOV-08",
        ))

    # ------------------------------------------------------------------
    # 4. Corruption is never silently repaired.
    # ------------------------------------------------------------------
    failures.extend(check_contains(
        req_block(recov, "REQ-RECOV-011") or "",
        ["Invalid(D) ⇒ RecoveryFault"],
        "REQ-RECOV-011",
    ))
    failures.extend(check_contains(
        req_block(recov, "REQ-RECOV-012") or "",
        ["MUST NEVER", "silently repair", "gaps", "checksums",
         "causality violations"],
        "REQ-RECOV-012",
    ))
    # Snapshot validity / integrity (R-PERSIST-05), sequence continuity
    # (R-PERSIST-06) and chained checksums (R-PERSIST-08) in the canonical spec.
    failures.extend(check_contains(
        req_block(recov, "REQ-PERSIST-019") or "",
        ["ValidSnapshot(S)", "Commit(S)",
         "Digest(Canonical(S)) = RecordedDigest(S)"],
        "REQ-PERSIST-019",
    ))
    failures.extend(check_contains(
        req_block(recov, "REQ-PERSIST-022") or "",
        ["s_{n+1} = s_n + 1", "gaps", "rejected"],
        "REQ-PERSIST-022",
    ))
    for needle in [
        "checksum_n = H(", "chained", "snapshot commit record",
        "RecoveryFault", "effect evidence chain",
    ]:
        if needle not in spec:
            failures.append(f"spec/01: missing no-silent-repair clause {needle!r}")

    # ------------------------------------------------------------------
    # 5. Recovery = replay from snapshot + valid WAL + journal.
    # ------------------------------------------------------------------
    failures.extend(check_contains(
        req_block(recov, "REQ-RECOV-001") or "",
        ["D = ⟨S, L, H⟩", "latest committed snapshot",
         "durable event log", "durable effect journal"],
        "REQ-RECOV-001",
    ))
    failures.extend(check_contains(
        req_block(recov, "REQ-RECOV-002") or "",
        ["Recover(D) = Replay(S, L, H)", "replaying the log and journal over the snapshot"],
        "REQ-RECOV-002",
    ))
    r10 = req_block(recov, "REQ-RECOV-010") or ""
    failures.extend(check_contains(
        r10,
        ["locate", "newest committed snapshot", "framing/checksum",
         "sequence continuity", "reject gaps", "replay", "effect journal",
         "runnable queue", "invariants", "final state digest",
         "RecoveryComplete", "deterministic scheduler"],
        "REQ-RECOV-010",
    ))
    # Independent engine.
    failures.extend(check_contains(
        req_block(recov, "REQ-RECOV-014") or "",
        ["independent implementation", "anti-oracle-collapse"],
        "REQ-RECOV-014",
    ))

    # ------------------------------------------------------------------
    # 6. Recovery reconstruction and completion boundary (R-RECOV-09).
    # ------------------------------------------------------------------
    rreco9 = req_block(spec, "R-RECOV-09")
    if rreco9 is None:
        failures.append("R-RECOV-09: addendum paragraph not found in spec/01")
    else:
        failures.extend(check_contains(
            rreco9,
            ["next_effect_id", "max", "EffectIssued",
             "append(EffectCompleted)", "sync()", "charge", "resume",
             "T4", "T5", "fsync"],
            "R-RECOV-09",
        ))

    # ------------------------------------------------------------------
    # 7. Escrow survives crash.
    # ------------------------------------------------------------------
    failures.extend(check_contains(
        req_block(recov, "REQ-RECOV-013") or "",
        ["C_available + C_escrowed + C_consumed = C_initial",
         "survive crashes"],
        "REQ-RECOV-013",
    ))

    return failures


def main() -> int:
    failures = collect()
    if failures:
        print("CRASH-CONSISTENCY AUDIT GATE FAILURES:")
        for f in failures:
            print("  - " + f)
        print("%d failure(s)" % len(failures))
        return 1
    print(
        "PASS: causal ordering (Issued/Completed/Reconciled), "
        "crash matrix T0-T6, critical rule, no-silent-repair, "
        "recovery replay, and escrow survival clauses present."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
