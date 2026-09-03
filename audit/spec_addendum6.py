#!/usr/bin/env python3
"""Addendum VI — owner decisions resolving dep/05 V-01, V-09, V-10c (2026-09-03).

Idempotency-guarded applier, same discipline as addenda I–V: every anchor is
counted (abort on ambiguity), every insertion is skipped if already present,
nothing is deleted (superseded wording is quoted at the superseding site).

Decisions (spec owner, recorded in audit/spec-addendum6-draft.md):
  V-01  -> V-01a: ExecutablePlan + Sealed homed in ror-core; construction
                 compiler-only via a PlanSeal token denied by clippy
                 disallowed-methods outside ror-compiler (R-REPO-03 Track-B).
                 No new crate edge (ror-runtime already depends on ror-core).
  V-09  -> explicit two-crate home: algebra + operand types in ror-core,
                 per-transition gate calls in ror-runtime; 'budget primitives'
                 in the R-REPO-02 kernel bullet = kernel consumes core types.
  V-10c -> applied: ror-persistence -> ror-agent PERSISTENCE edge
                 (PlannerAccepted durable recording, R-PLANNER-04).
  V-02 residual -> deferred by decision (no change here).

Applies to: spec/01 (two refinement notes), spec/07 (§6 edge + note, §3 rows).
The table/builder edits (spec/_build_index.py, mod/, dep/) are made in the
same commit and enforced by their own checkers.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
APPLIED = []


def guard(text, anchor, what):
    n = text.count(anchor)
    if n != 1:
        sys.exit(f"ABORT addendum VI: {what}: anchor count {n} for {anchor[:60]!r}")
    return text


def insert_after(text, anchor, block, what):
    if block.strip() in text:
        return text  # already applied
    guard(text, anchor, what)
    APPLIED.append(what)
    return text.replace(anchor, anchor + block, 1)


def replace_once(text, old, new, what):
    if new in text:
        return text  # already applied
    guard(text, old, what)
    APPLIED.append(what)
    return text.replace(old, new, 1)


# ---------------------------------------------------------------- spec/01 ---
p = ROOT / "spec/01-canonical-specification.md"
t = p.read_text(encoding="utf-8")

# Note A — ExecutablePlan crate home and seal (after R-ARCH-05, S-04).
anchor_a = "resolves C-93, retiring U-05; no source transcription.)*\n"
note_a = """
*(Frozen addendum VI — owner decision 2026-09-03, resolving `dep/05` V-01; additive per R-SCOPE-03; refines R-ARCH-03/R-REPO-02; no source transcription.)*

**ExecutablePlan crate home and seal (normative refinement).** The `ExecutablePlan` type and its `Sealed` marker MUST be defined in `ror-core`. Construction MUST remain compiler-only (R-ARCH-03 unchanged): `finalize` requires a `PlanSeal` token whose sole constructor is `pub` in `ror-core` and denied by the workspace clippy `disallowed-methods` configuration in every crate except `ror-compiler` (R-REPO-03 structural enforcement — the same mechanism class as R-CORE-12's `unwrap`/`expect` denial; Track-B). The source's `pub(crate) fn finalize` phrasing (L39947-39950 §16) is per-crate visibility and cannot express this cross-crate privacy; that reading is SUPERSEDED (quoted, not deleted — `dep/05` V-01). No new crate edge results: `ror-runtime` already depends on `ror-core` (`spec/07` §6), which is why the type home moves rather than the edge.
"""
t = insert_after(t, anchor_a, note_a, "spec/01 note A (V-01)")

# Note B — budget crate home (before R-REPO-03, S-22).
anchor_b = "**R-REPO-03 (boundary enforcement).**"
note_b = """*(Frozen addendum VI — owner decision 2026-09-03, resolving `dep/05` V-09; additive per R-SCOPE-03; refines R-REPO-02/R-BUDGET-01…09; no source transcription.)*

**Budget crate home made explicit (normative refinement).** The R-REPO-02 `ror-kernel` bullet's "budget primitives" MUST be read as: the kernel CONSUMES the budget operand types defined in `ror-core`; no budget algebra, operand type or per-transition gate lives in `ror-kernel`. The shared ceiling/operand types MUST live in `ror-core` (`ror-core → ror-kernel` is forbidden by §14's frozen list, upheld by R-TRUST-05); per-transition gate CALLS live in `ror-runtime` (`spec/07` §2 already splits the R-BUDGET obligations across `ror-core` and the runtime gates). MOD-04 BUDGET keeps one module with an explicit two-crate home — algebra + operand types in `ror-core`, gate calls in `ror-runtime` (`mod/04` DEPENDENCIES states it).

"""
t = replace_once(t, anchor_b, note_b + anchor_b, "spec/01 note B (V-09)")
p.write_text(t, encoding="utf-8")

# ---------------------------------------------------------------- spec/07 ---
p = ROOT / "spec/07-implementation-mapping.md"
t = p.read_text(encoding="utf-8")

# §6 agent edge (V-10c).
t = replace_once(t,
    "ror-agent → ror-core, ror-compiler, ror-runtime\n",
    "ror-agent → ror-core, ror-compiler, ror-runtime, ror-persistence\n",
    "spec/07 §6 agent edge (V-10c)")

# §6 provenance note sentence.
t = insert_after(t,
    "only edge §14's frozen list does not forbid in either direction.\n",
    "\nOwner decision (addendum VI, `dep/05` V-10c applied): `ror-agent` gains "
    "`ror-persistence` — the `PlannerAccepted` durable recording (R-PLANNER-04, "
    "REQ-PLANNER-018).\n",
    "spec/07 §6 V-10c note")

# §3 rows — after the R-PLANNER-03 row.
t = insert_after(t,
    "| R-PLANNER-03 (staleness) | `ror-agent` proposal intake + `ror-runtime` boundary check | The check lives at the machine boundary, not in the LLM integration. |\n",
    "| R-ARCH-03 (plan constructors private) | `ExecutablePlan` homed in `ror-core` behind `PlanSeal`; `finalize` compiler-only (addendum VI, `dep/05` V-01 resolved) | Seal = clippy `disallowed-methods` on the token constructor everywhere except `ror-compiler` (Track-B); no new crate edge — `ror-runtime` already depends on `ror-core`. |\n"
    "| R-BUDGET-01…09 (budget crate home) | algebra + operand types in `ror-core`; gate calls in `ror-runtime`; `ror-kernel` consumes core types (addendum VI, `dep/05` V-09 resolved) | `ror-core → ror-kernel` is forbidden by §14's frozen list, so shared types must be core-resident. |\n",
    "spec/07 §3 rows (V-01/V-09)")
p.write_text(t, encoding="utf-8")

# Fix-up (same run discipline): ID-5 forbids citing the frozen block's line
# numbers outside the exempt C-85 row, so the two notes cite §14 by name.
for path, old, new in [
    (ROOT / "spec/01-canonical-specification.md",
     "(`ror-core → ror-kernel` is forbidden, L39821 §14, upheld by R-TRUST-05)",
     "(`ror-core → ror-kernel` is forbidden by §14's frozen list, upheld by R-TRUST-05)"),
    (ROOT / "spec/07-implementation-mapping.md",
     "`ror-core → ror-kernel` forbidden (L39821 §14), so shared types must be core-resident.",
     "`ror-core → ror-kernel` is forbidden by §14's frozen list, so shared types must be core-resident."),
]:
    t2 = path.read_text(encoding="utf-8")
    if old in t2:
        guard(t2, old, f"fix-up {path.name}")
        t2 = t2.replace(old, new, 1)
        path.write_text(t2, encoding="utf-8")
        APPLIED.append(f"fix-up L39821 wording ({path.name})")

print("addendum VI applied:", "; ".join(APPLIED) or "nothing to do (idempotent)")
