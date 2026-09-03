# Addendum III — MEDIUM-HIGH freeze (SEC-006 / SEC-020 / SEC-022)

**Status: APPLIED** via `audit/spec_addendum3.py --apply` (adoption commit on
`arena/01a063c4-red-on-rust`; post-apply verification on the real tree:
161 obligations / 161 matrix rows / 148 records, `spec/_check.py` D1=0 exit 0
with only the pre-existing adjudicated warnings, index rebuilt at
161/84/27/19, `req/_validate.py` exit 0 / ERRORS 0). This file is retained as
the review record of exactly what was adopted and why; rollback is
`git revert` of the adoption commit. The exact edit set lives in
`audit/spec_addendum3.py` (this draft was generated from its constants, so the
two cannot drift); its dry run is full-fidelity — a `git archive` sandbox of
HEAD receives the edits and the entire verification stack
(`audit/spec_check.py`, `spec/_build_index.py`, `req/_validate.py`) runs there.

## 1. What this freezes (report §6 items 4/5/7 remainders)

| Addendum | Freezes | Extends / resolves |
|---|---|---|
| `R-ACTOR-09` | SEC-006: spawn transfers **no** capabilities by default (delegation is the only default path); explicit manifest + constraint compiler-checked, strictly attenuated (`Authority(child) ≺ Authority(parent)`; `≼` reserved for delegation); wholesale copying forbidden in the default case; the v0.3 `trust_level` phantom retracted (AMB-04); `BudgetAllocationSpec::validate_and_escrow` bounded (U-03 security-direction closure) | extends R-ACTOR-05/R-COMPILE-06/R-MARSHAL-05; resolves C-82; mutation M025 |
| `R-CORE-12` | SEC-020: fault totality on machine paths — panic-free non-test code (`unwrap`/`expect`/`unreachable!`/`panic!` forbidden), failures map to declared Faults (`Fault::InternalInvariant`, observable, differentially comparable); transition atomicity (complete-or-fault, no died-mid-transition); durable append precedes irreversible in-memory mutation; clippy `unwrap_used`/`expect_used` denial | extends R-EFFECT-04/R-BUDGET-02/R-REPO-03; resolves C-83; mutation M034 |
| `R-TRUST-04` | SEC-022 (V-03/V-11): one trust table, complete over every boundary-enforcing module — MOD-06/08/10 rows frozen (authoritative machine boundary); the 11-row table superseded; the planner (MOD-13/`ror-agent`) never a SECURITY/RUNTIME provider — prohibitions homed at MOD-03/06/08 | extends R-TRUST-01/R-SCOPE-04; resolves C-84; verification = dep/ regenerated with SC-1/2/3 hard-gated |
| `R-TRUST-05` | SEC-022 (V-10) + SEC-015 crate rule: the crate DAG carries the R-DUR-02 hinge edge `ror-runtime → ror-persistence` (inverted-trait alternative superseded); `ror-core → ror-kernel` stays forbidden; the forbidden-edge list checked mechanically against the real `Cargo.toml` DAG; no LLM-facing code in a crate with runtime/compiler/persistence handles | extends R-REPO-02/03/R-DUR-02; resolves C-85 |
| `C-82…C-85` (spec/06) | the security consequences registered (BLOCKING ×3, MAJOR ×1), all `resolved-by-addendum` | rows after C-81 |
| `M025`, `M034` (spec/08) | spawn clones parent context unattenuated; release failure silently ignored | registry → M001–M025, M032, M034 |

`dep/` is intentionally not regenerated here (it is the source-derived
register; `dep/_graph.py` re-derives edges from the frozen source): R-TRUST-04
records the normative corrections and names the SC-1/2/3 hard-gated
regeneration as its verification — the same layer discipline used for `term/`
in addendum II.

## 2. Exact normative texts (spec/01 insertions)

**R-ACTOR-09 (spawn authority rule — frozen addendum).** `Expr::Spawn` MUST NOT transfer parent capabilities by default: a spawned child's initial authority context is empty, and delegation (R-MARSHAL-05) is the only default transfer path. Any spawn-time authority transfer MUST be explicit: the plan declares a capability manifest plus constraint, compiler-checked against the plan's declared capability set (the R-COMPILE-06 discipline), and the kernel derives each manifest entry strictly attenuated (constraint ≠ ⊤ — identity derivation is not spawn). The spawn security theorem is strict: `Authority(child) ≺ Authority(parent)` — `≼` is reserved for delegation; wholesale capability copying (iterating the parent context under one constraint) is FORBIDDEN: the engineering rule binds the default case, not only explicit cloning. The v0.3 `trust_level`/`attenuated_context(κ_parent, trust_level)` form is SUPERSEDED (quoted, not deleted; the AMB-04 phantom is resolved by retraction). `BudgetAllocationSpec::validate_and_escrow` MUST be bounded: maximum child share, minimum parent retention, fault on violation (closes U-03 in the security direction). *(Frozen addendum — post-audit remediation SEC-006; additive per R-SCOPE-03; extends R-ACTOR-05/R-COMPILE-06/R-MARSHAL-05; resolves C-82; mutation M025; no source transcription.)*

**R-CORE-12 (fault totality and transition atomicity — frozen addendum).** Machine code (evaluator, kernel, budget, persistence, runtime transitions) MUST be panic-free on non-test paths: every fallible operation returns `Result`, and every failure maps to a declared `Fault` — `unwrap`/`expect`/`unreachable!`/`panic!` are FORBIDDEN outside test doubles (the `#![forbid(unsafe_code)]` policy extended with the panic clause). Check/commit drift MUST fault, not panic: a declared internal-consistency fault (`Fault::InternalInvariant` family) MUST exist, observable and differentially comparable. Transition atomicity: a transition either completes (all durable effects appended) or faults with R-EFFECT-04's five assertions — there is no third died-mid-transition outcome inside the trusted boundary. Durable appends MUST precede irreversible in-memory mutations where feasible, or the commit MUST be journal-driven — the mid-transition window is removed, not merely its panic failure mode. Machine crates MUST compile under `clippy::unwrap_used`/`clippy::expect_used` denial (R-REPO-03 structural enforcement). *(Frozen addendum — post-audit remediation SEC-020; additive per R-SCOPE-03; extends R-EFFECT-04/R-BUDGET-02/R-REPO-03; resolves C-83; mutation M034; no source transcription.)*

**R-TRUST-04 (one complete trust table; the planner is never a provider — frozen addendum).** The trust table exists exactly once and MUST be complete over every module that enforces a security boundary: rows for MOD-06 (marshalling and delegation boundary), MOD-08 (the effect gate sequence), and MOD-10 (the canonical codec) are frozen here as authoritative machine boundary (trust: Yes); the 11-row earlier table is SUPERSEDED (quoted, not deleted). The planner module (MOD-13 / `ror-agent`) MUST NOT appear as the provider of any `SECURITY_DEPENDENCY` or `RUNTIME_DEPENDENCY` edge: its records are prohibitions — negative contracts homed at their enforcing modules (MOD-03/06/08); security obligations MUST NOT be discharged inside any LLM-facing crate. Verification: `dep/` regenerated with SC-1/2/3 promoted from advisory rows to hard failures. *(Frozen addendum — post-audit remediation SEC-022 (V-03/V-11); additive per R-SCOPE-03; extends R-TRUST-01/R-SCOPE-04; resolves C-84; no source transcription.)*

**R-TRUST-05 (structural carriability of the durability hinge — frozen addendum).** The frozen crate DAG MUST carry the R-DUR-02 hinge edge `ror-runtime → ror-persistence` (the step-14 durable append that `HostInvoked ⇒ DurableIssued` hangs on) — decided here in the direct direction; the inverted-trait alternative is SUPERSEDED (quoted, not deleted). The `ror-core → ror-kernel` implication is resolved per the frozen edge list's intent (forbidden; V-10b): authority storage stays kernel-side. The forbidden-edge list MUST be checked mechanically against the actual `Cargo.toml` DAG, and the crate-separation rule — no LLM-facing code in a crate holding runtime/compiler/persistence handles — is part of R-REPO-03's structural review. A build in which the durability call is structurally orphaned (a local journal shim) is a conformance failure. *(Frozen addendum — post-audit remediation SEC-022 (V-10) + the SEC-015 crate rule; additive per R-SCOPE-03; extends R-REPO-02/R-REPO-03/R-DUR-02; resolves C-85; no source transcription.)*

## 3. Companion edits

spec/03 (+4 rows, Total **161** = 148 + 13 addenda), spec/06 (+C-82…C-85),
spec/08 (+M025/M034, registry title), records scope note, README (161 IDs),
`spec/_build_index.py` (sections S-02/S-03/S-15, rows, mutations, milestones
M5/M6, crates runtime/persistence, id-scheme counts 161/27), and
`req/_validate.py` (recorded register growth 81 → 85 raw C-rows).

## 4. Verification record (pre-apply)

- Precheck: addendum ABSENT (all 10 markers), 30 anchors intact.
- Full-repo sandbox (git archive of HEAD + edits): obligations/matrix/records
  = 161/161/148; `spec_check` parses 148/161/161, D1=0, no FAIL, zero
  warnings on the four new obligations (36 pre-existing adjudicated);
  index rebuild `requirements=161 findings=84 mutations=27 tags=19`;
  `req/_validate.py` exit 0, ERRORS 0 (after the 81→85 correction the sandbox
  run itself forced — the first dry run failed with "expected 84 … found 85",
  because the validator counts raw rows incl. the C-39 pointer while the index
  excludes it; the correction is in the committed edit, not a suppressed check).
- New-row body↔matrix D3 overlaps: R-ACTOR-09 0.81, R-CORE-12 0.71,
  R-TRUST-04 0.91, R-TRUST-05 0.88.

## 5. Adoption procedure

1. `python3 audit/spec_addendum3.py` — re-run the full-sandbox dry-run proof.
2. `python3 audit/spec_addendum3.py --apply` — applies 30 edits across 8 files; every check re-runs on the real tree in-step.
3. `python3 spec/_check.py` — gate must exit 0; `git revert` is the rollback.

Generated from `audit/spec_addendum3.py` constants — 2026-09-03.
