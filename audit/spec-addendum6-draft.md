# Addendum VI draft — owner decisions for dep/05 open findings (2026-09-03)

Status: APPLIED (in force). Register: dep/05 §5/§6/§7 carry the matching
status records; this draft is the decision record. All four decisions were
taken by the specification owner; none modifies frozen semantics — each
resolves a recorded ambiguity or gap (R-SCOPE-03 permits stating what the
frozen text left unstated; every superseded reading is quoted, not deleted).

## V-01 — ExecutablePlan has no determined crate home → V-01a applied

Decision: home `ExecutablePlan` (and its `Sealed` marker) in `ror-core`;
construction stays compiler-only (R-ARCH-03 unchanged) via a `PlanSeal` token
whose sole constructor is denied by the workspace clippy
`disallowed-methods` configuration in every crate except `ror-compiler`
(R-REPO-03 structural enforcement, same mechanism class as R-CORE-12's
unwrap/expect denial). No new crate edge — `ror-runtime` already depends on
`ror-core`. The `pub(crate) fn finalize` reading (L39947-39950 §16) is
superseded: `pub(crate)` is per-crate and cannot express cross-crate privacy.
V-01b (export from ror-compiler) is void. The `ror-compiler → ror-runtime`
TYPE entry is removed from CRATE_MISSING_EDGES (closed as not-needed).

## V-09 — MOD-04 BUDGET has no single crate home → explicit two-crate home

Decision: one MOD-04 module, explicit two-crate home — algebra + shared
ceiling/operand types in `ror-core`, per-transition gate calls in
`ror-runtime`; `ror-kernel` CONSUMES the core-defined operand types ("budget
primitives" in the R-REPO-02 kernel bullet is read that way; no budget
algebra or gate lives in `ror-kernel` — `ror-core → ror-kernel` is forbidden,
L39821 §14, upheld by R-TRUST-05). Stated in spec/01 (addendum VI note B),
spec/07 §3, mod/04 DEPENDENCIES, and the ownership map's crate string.

## V-10c — PlannerAccepted recording edge → applied

Decision: `ror-persistence → ror-agent` PERSISTENCE_DEPENDENCY added to
spec/07 §6 (`ror-agent → ror-core, ror-compiler, ror-runtime,
ror-persistence`), spec/10-index.json and dep CRATE_EDGES. V-10 is now fully
resolved (V-10a + V-10c applied, V-10b rejected).

## V-02 residual — ten §14 prohibitions as R-REPO-03 atomic records → deferred

Decision: deferred by the owner. It is a verification-checklist addition, not
an architecture change; revisit with implementation work. dep/05 V-02 keeps
the re-scoped record with the residual stated.

## Cascade summary

spec/01 (+2 refinement notes, no new obligation — 173 unchanged),
spec/07 (§6 edge + note, §3 two rows), spec/_build_index.py (ror-agent deps)
→ spec/10-index.json regenerated; mod/_ownership.py (MOD-04 crate string),
mod/04 (crate contract restated, superseded wording quoted), mod/18/19
regenerated; dep/_edges.py (CRATE_EDGES +1, CRATE_MISSING_EDGES now empty,
statuses for V-01/V-09/V-10, applied/void markers V-01a/V-01b/V-10c),
dep/ outputs regenerated. No new records (545 unchanged), no new obligations,
no milestone/tag changes.
