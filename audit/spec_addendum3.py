#!/usr/bin/env python3
"""spec_addendum3.py — MEDIUM-HIGH frozen-addendum applier (SEC-006/020/022).

Freezes the three MEDIUM-HIGH remediations (audit report §6 items 4-5
remainders) as additive normative text:

  spec/01  + R-ACTOR-09 (SEC-006: spawn authority rule — no default transfer,
                         strict attenuation, trust_level retraction, budget
                         bounds)
           + R-CORE-12  (SEC-020: fault totality + transition atomicity on
                         machine paths; panic-free; InternalInvariant fault)
           + R-TRUST-04 (SEC-022 V-03/V-11: one complete trust table; the
                         planner is never a security/runtime provider)
           + R-TRUST-05 (SEC-022 V-10: the R-DUR-02 hinge crate edge is
                         structurally carriable; forbidden-edge mechanical
                         check; crate-separation rule)
  spec/03  + 4 rows, Total 157 -> 161
  spec/06  + C-82..C-85 (registered security consequences; resolved-by-addendum)
  spec/08  + mutations M025, M034
  records  scope note extended to addendum III
  README   157 -> 161 IDs
  spec/_build_index.py  inline dataset extended
  req/_validate.py      register expectation C-rows 81 -> 84 (recorded growth)

Default: DRY RUN — git-archive sandbox of HEAD, overlays the edits, and runs
the full verification stack there (spec_check, _build_index, req/_validate).
--apply: in place, same checks on the real tree.  Exit 0 = proof complete;
1 = verification failed; 2 = safety abort (already applied / anchor mismatch).

dep/ is intentionally NOT regenerated here: it is the source-derived register
(dep/_graph.py re-derives edges from the frozen source); R-TRUST-04/05 record
the normative corrections and name the regeneration (SC-1/2/3 promoted to
hard failures) as their verification, exactly as term/ was handled in
addendum II.
"""

from __future__ import annotations

import re
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SPEC01 = REPO / "spec" / "01-canonical-specification.md"
MATRIX = REPO / "spec" / "03-obligation-matrix.md"
CONTRA = REPO / "spec" / "06-contradictions-ambiguities.md"
VMAP = REPO / "spec" / "08-verification-mapping.md"
RECORDS = REPO / "spec" / "normative-normalization-records.md"
README = REPO / "README.md"
CHECKER = REPO / "audit" / "spec_check.py"
BUILDIDX = REPO / "spec" / "_build_index.py"
VALIDATE = REPO / "req" / "_validate.py"

NEW_IDS = ["R-ACTOR-09", "R-CORE-12", "R-TRUST-04", "R-TRUST-05"]
MARKERS = NEW_IDS + ["C-82", "C-83", "C-84", "C-85", "M025", "M034"]

ADD_ACTOR9 = "**R-ACTOR-09 (spawn authority rule — frozen addendum).** `Expr::Spawn` MUST NOT transfer parent capabilities by default: a spawned child's initial authority context is empty, and delegation (R-MARSHAL-05) is the only default transfer path. Any spawn-time authority transfer MUST be explicit: the plan declares a capability manifest plus constraint, compiler-checked against the plan's declared capability set (the R-COMPILE-06 discipline), and the kernel derives each manifest entry strictly attenuated (constraint ≠ ⊤ — identity derivation is not spawn). The spawn security theorem is strict: `Authority(child) ≺ Authority(parent)` — `≼` is reserved for delegation; wholesale capability copying (iterating the parent context under one constraint) is FORBIDDEN: the engineering rule binds the default case, not only explicit cloning. The v0.3 `trust_level`/`attenuated_context(κ_parent, trust_level)` form is SUPERSEDED (quoted, not deleted; the AMB-04 phantom is resolved by retraction). `BudgetAllocationSpec::validate_and_escrow` MUST be bounded: maximum child share, minimum parent retention, fault on violation (closes U-03 in the security direction). *(Frozen addendum — post-audit remediation SEC-006; additive per R-SCOPE-03; extends R-ACTOR-05/R-COMPILE-06/R-MARSHAL-05; resolves C-82; mutation M025; no source transcription.)*"

ADD_CORE12 = "**R-CORE-12 (fault totality and transition atomicity — frozen addendum).** Machine code (evaluator, kernel, budget, persistence, runtime transitions) MUST be panic-free on non-test paths: every fallible operation returns `Result`, and every failure maps to a declared `Fault` — `unwrap`/`expect`/`unreachable!`/`panic!` are FORBIDDEN outside test doubles (the `#![forbid(unsafe_code)]` policy extended with the panic clause). Check/commit drift MUST fault, not panic: a declared internal-consistency fault (`Fault::InternalInvariant` family) MUST exist, observable and differentially comparable. Transition atomicity: a transition either completes (all durable effects appended) or faults with R-EFFECT-04's five assertions — there is no third died-mid-transition outcome inside the trusted boundary. Durable appends MUST precede irreversible in-memory mutations where feasible, or the commit MUST be journal-driven — the mid-transition window is removed, not merely its panic failure mode. Machine crates MUST compile under `clippy::unwrap_used`/`clippy::expect_used` denial (R-REPO-03 structural enforcement). *(Frozen addendum — post-audit remediation SEC-020; additive per R-SCOPE-03; extends R-EFFECT-04/R-BUDGET-02/R-REPO-03; resolves C-83; mutation M034; no source transcription.)*"

ADD_TRUST4 = "**R-TRUST-04 (one complete trust table; the planner is never a provider — frozen addendum).** The trust table exists exactly once and MUST be complete over every module that enforces a security boundary: rows for MOD-06 (marshalling and delegation boundary), MOD-08 (the effect gate sequence), and MOD-10 (the canonical codec) are frozen here as authoritative machine boundary (trust: Yes); the 11-row earlier table is SUPERSEDED (quoted, not deleted). The planner module (MOD-13 / `ror-agent`) MUST NOT appear as the provider of any `SECURITY_DEPENDENCY` or `RUNTIME_DEPENDENCY` edge: its records are prohibitions — negative contracts homed at their enforcing modules (MOD-03/06/08); security obligations MUST NOT be discharged inside any LLM-facing crate. Verification: `dep/` regenerated with SC-1/2/3 promoted from advisory rows to hard failures. *(Frozen addendum — post-audit remediation SEC-022 (V-03/V-11); additive per R-SCOPE-03; extends R-TRUST-01/R-SCOPE-04; resolves C-84; no source transcription.)*"

ADD_TRUST5 = "**R-TRUST-05 (structural carriability of the durability hinge — frozen addendum).** The frozen crate DAG MUST carry the R-DUR-02 hinge edge `ror-runtime → ror-persistence` (the step-14 durable append that `HostInvoked ⇒ DurableIssued` hangs on) — decided here in the direct direction; the inverted-trait alternative is SUPERSEDED (quoted, not deleted). The `ror-core → ror-kernel` implication is resolved per the frozen edge list's intent (forbidden; V-10b): authority storage stays kernel-side. The forbidden-edge list MUST be checked mechanically against the actual `Cargo.toml` DAG, and the crate-separation rule — no LLM-facing code in a crate holding runtime/compiler/persistence handles — is part of R-REPO-03's structural review. A build in which the durability call is structurally orphaned (a local journal shim) is a conformance failure. *(Frozen addendum — post-audit remediation SEC-022 (V-10) + the SEC-015 crate rule; additive per R-SCOPE-03; extends R-REPO-02/R-REPO-03/R-DUR-02; resolves C-85; no source transcription.)*"

ROW_ACTOR9 = "| R-ACTOR-09 | Spawn transfers no capabilities by default (delegation is the only default path); explicit manifest + constraint compiler-checked, strictly attenuated; Authority(child) ≺ parent; trust_level phantom retracted; BudgetAllocationSpec bounds (C-82 resolved; M025) | addendum (SEC-006) | SPECIFIED | ror-runtime, ror-kernel | M025, spawn fan-out amplification tests |"
ROW_CORE12 = "| R-CORE-12 | Fault totality on machine paths: panic-free non-test code, failures map to declared Fault (InternalInvariant family); transition atomicity — complete or fault, no died-mid-transition; durable append precedes in-memory mutation; clippy unwrap/expect denial (C-83 resolved; M034) | addendum (SEC-020) | SPECIFIED | all machine crates | M034, panic-catching fuzz harness |"
ROW_TRUST4 = "| R-TRUST-04 | One complete trust table: MOD-06/08/10 rows frozen (authoritative machine boundary); 11-row table superseded; planner never a security/runtime provider — prohibitions homed at enforcing modules; dep/ SC-1/2/3 hard failures (C-84 resolved) | addendum (SEC-022) | SPECIFIED | — | dep/ regeneration with SC-1/2/3 hard-gated |"
ROW_TRUST5 = "| R-TRUST-05 | Crate DAG carries the R-DUR-02 hinge edge ror-runtime → ror-persistence (inverted trait superseded); ror-core → ror-kernel forbidden; forbidden-edge list checked against Cargo.toml; crate-separation rule (C-85 resolved) | addendum (SEC-022) | SPECIFIED | ror-runtime, ror-persistence | Cargo.toml DAG mechanical check |"

C_ROWS = [
 "| C-82 | `execute_spawn` iterates *all* parent capabilities under one `spawn_constraint` that has no AST source (`Expr::Spawn` carries no constraint field; L25631–25637, L12191–12194), the v0.3 `trust_level` is a phantom (AMB-04/C-36), and `BudgetAllocationSpec` validation is unstated (U-03) — the security consequence, that a conforming implementation may default to identity derivation and fan out full parent authority at scale from untrusted plans while `child ≼ parent` holds pointwise, is unregistered (audit SEC-006) | BLOCKING | L25631–25637, L12191–12194, L8770–8786, L25944–25952 | **resolved-by-addendum** → `R-ACTOR-09` | \"Wholesale capability copying\" is a README-prohibited shortcut, yet it is the default the frozen code shape permits: `derive(A,⊤) = A` is legal under the meet semantics, `Expr::Spawn` is authored by the LLM, and the static budget rule bounds child *budget*, never child *authority*. `R-ACTOR-09` freezes no-default-transfer (delegation is the only default path), explicit compiler-checked manifests with strict attenuation `Authority(child) ≺ Authority(parent)`, retracts the `trust_level` phantom, and bounds `BudgetAllocationSpec::validate_and_escrow` (max child share, min parent retention, fault on violation). Cross-ref: U-03, U-05, C-36/AMB-04, mutation M025. |",
 "| C-83 | The frozen machine code panics at exactly the commit points where partial state exists — gate-10/13 `consume(...).unwrap()`/`reserve(...).unwrap()` (\"Safe due to checks\"), the receipt-path `release(...).unwrap()` beside a checked `consume`, `allocate_child_budget(...).unwrap()`, `finalize_request`'s `pop().unwrap()` + `unreachable!()` — contradicting the frozen discipline that budget failures are data, never panics (mod/04, R-BUDGET-02, MOD-01 fault taxonomy); unregistered as a conflict (audit SEC-020) | BLOCKING | L10487–10490, L23556–23563, L23863–23882, L10588 | **resolved-by-addendum** → `R-CORE-12` | Every unwrap is defended by reasoning, not construction — and check/commit drift is what maintenance, an M0nn mutation, or the SEC-004 recovery gap induces; a panic mid-transition leaves journal state that is neither pre- nor post-state, so recovery manufactures false effect history (`Indeterminate` for an effect that never reached the host) outside the fault taxonomy, invisible to differential comparison. `R-CORE-12` freezes fault totality (declared `Fault::InternalInvariant`, observable and differentially comparable), transition atomicity, durable-append-before-mutation ordering, and the clippy denial gate. Cross-ref: U-14/X-67 fault enumeration (SEC-012), R-EFFECT-04, mutation M034. |",
 "| C-84 | The trust table is frozen twice with different rows (11 vs 12; `Persistence` absent from the earlier) and three authoritative boundary modules have no row at all (MOD-06 marshalling, MOD-08 effect gates, MOD-10 codec); the dependency layer *measures* SC-1/2/3 FAIL — the planner module recorded as security provider (14 edges, V-03) and a production→planner runtime edge — so the recorded graph licenses discharging R-TRUST-01 inside the one crate that faces the untrusted LLM (audit SEC-022) | BLOCKING | dep/05-violations.md §1.2, V-03, V-11; L27613–27623 vs L41827–41841 | **resolved-by-addendum** → `R-TRUST-04` | The trust table is the one artifact the whole trust story reduces to, and the machine-checked graph that MOD-17 reviews is the deficient one. `R-TRUST-04` freezes the table once, complete (MOD-06/08/10 authoritative), re-homes the planner's records as prohibitions enforced at MOD-03/06/08, and hard-gates `dep/` regeneration on SC-1/2/3. Cross-ref: V-03, V-11, SEC-015, R-TRUST-01, R-SCOPE-04. |",
 "| C-85 | The step-14 durable append — the hinge of R-DUR-02 (`HostInvoked ⇒ DurableIssued`) — implies a `ror-runtime → ror-persistence` dependency no crate list carries (V-10a: \"the single most load-bearing cross-crate call in the design is the one the crate list omits\"), and `MOD-03 → MOD-04` implies `ror-core → ror-kernel`, forbidden outright by the frozen edge list (V-10b); the durability hinge is structurally uncarriable as declared (audit SEC-022) | MAJOR | dep/05-violations.md V-10; L39807–39828 | **resolved-by-addendum** → `R-TRUST-05` | A build that cannot legally make the durability call grows a local journal shim — a second, unreviewed durability implementation exactly where the causal effect chain lives. `R-TRUST-05` freezes the direct edge (inverted trait superseded), keeps authority storage kernel-side, requires the forbidden-edge list to be checked mechanically against the actual `Cargo.toml` DAG, and folds in the crate-separation rule (no LLM-facing code in a crate with runtime/compiler/persistence handles). Cross-ref: V-10, V-02, V-09, R-DUR-02, R-REPO-02/03, SEC-015. |",
]

MUT_ROWS3 = ("| M025 | spawn clones parent context unattenuated | R-ACTOR-09 |\n"
             "| M034 | release failure silently ignored (`unwrap` → `let _`) | R-CORE-12 |")

RECORDS_NOTE3 = " The same holds for the four addendum-III obligations (`R-ACTOR-09`, `R-CORE-12`, `R-TRUST-04`, `R-TRUST-05`; remediations SEC-006/020/022)."

IDX_ACTOR9 = ' ("R-ACTOR-09","S-15","Spawn authority rule: no default transfer, strict attenuation (frozen addendum)","addendum",SPEC,[],["ror-runtime","ror-kernel"],["M025","spawn fan-out amplification tests"],["C-82"]),'
IDX_CORE12 = ' ("R-CORE-12","S-02","Fault totality and transition atomicity on machine paths (frozen addendum)","addendum",SPEC,[],[],["M034","panic-catching fuzz harness"],["C-83"]),'
IDX_TRUST4 = ' ("R-TRUST-04","S-03","One complete trust table; planner never a provider (frozen addendum)","addendum",SPEC,[],[],["dep/ SC-1/2/3 hard-gated"],["C-84"]),'
IDX_TRUST5 = ' ("R-TRUST-05","S-03","Durability hinge crate edge structurally carriable (frozen addendum)","addendum",SPEC,[],["ror-runtime","ror-persistence"],["Cargo.toml DAG mechanical check"],["C-85"]),'
IDX_MUTS3 = (' ("M025","spawn clones parent context unattenuated",["R-ACTOR-09"]),\n'
             ' ("M034","release failure silently ignored (unwrap to let _)",["R-CORE-12"]),')

EDITS: list[tuple[Path, str, str]] = [
    # spec/01 — inserts after each section's current tail
    (SPEC01, "resolves C-80 and, at the normative layer, term/ X-01/X-04/X-05; no source transcription.)*",
     "resolves C-80 and, at the normative layer, term/ X-01/X-04/X-05; no source transcription.)*\n\n" + ADD_CORE12),
    (SPEC01, "*(L37722–37748; L19153–19175.)*",
     "*(L37722–37748; L19153–19175.)*\n\n" + ADD_TRUST4 + "\n\n" + ADD_TRUST5),
    (SPEC01, "(budget is created only at root initialization; spawn escrows; send carries no budget).",
     "(budget is created only at root initialization; spawn escrows; send carries no budget).\n\n" + ADD_ACTOR9),
    # spec/03 — rows after their area neighbours + total
    (MATRIX,
     "| R-CORE-11 | One canonical signature per I2 predicate: ValidatedRequest(E) request-time subsuming ValidatedPlan(plan(E)); Authorized(holder, c, E, t) possession conjunct (formalizes R-KERN-04); ValidatedPlan_pred vs ValidatedPlan_struct; chain stated once (X-01/X-04/X-05; C-80 resolved) | addendum (SEC-016) | SPECIFIED | ror-kernel, ror-runtime | R-TEST-09 differential adjudication |",
     "| R-CORE-11 | One canonical signature per I2 predicate: ValidatedRequest(E) request-time subsuming ValidatedPlan(plan(E)); Authorized(holder, c, E, t) possession conjunct (formalizes R-KERN-04); ValidatedPlan_pred vs ValidatedPlan_struct; chain stated once (X-01/X-04/X-05; C-80 resolved) | addendum (SEC-016) | SPECIFIED | ror-kernel, ror-runtime | R-TEST-09 differential adjudication |\n" + ROW_CORE12),
    (MATRIX,
     "| R-TRUST-03 | No hidden authority; evaluator sees refs only | L37722–37748, L19153–19175 | SPECIFIED | ror-kernel, ror-runtime | Track B (mock kernel), visibility checks |",
     "| R-TRUST-03 | No hidden authority; evaluator sees refs only | L37722–37748, L19153–19175 | SPECIFIED | ror-kernel, ror-runtime | Track B (mock kernel), visibility checks |\n" + ROW_TRUST4 + "\n" + ROW_TRUST5),
    (MATRIX,
     "| R-ACTOR-08 | No amplification / no teleportation theorems | L26048–26070 | SPECIFIED | ror-runtime | teleportation test, amplification test |",
     "| R-ACTOR-08 | No amplification / no teleportation theorems | L26048–26070 | SPECIFIED | ror-runtime | teleportation test, amplification test |\n" + ROW_ACTOR9),
    (MATRIX,
     "**Total: 157 obligations** (148 transcribed from the frozen source + 9 post-audit frozen addenda: R-COMPILE-06, R-CORE-11, R-KERN-04, R-KERN-05, R-EFFECT-08, R-MARSHAL-05, R-MARSHAL-06, R-CANON-12, R-PERSIST-07).",
     "**Total: 161 obligations** (148 transcribed from the frozen source + 13 post-audit frozen addenda: R-COMPILE-06, R-CORE-11, R-CORE-12, R-KERN-04, R-KERN-05, R-EFFECT-08, R-MARSHAL-05, R-MARSHAL-06, R-CANON-12, R-PERSIST-07, R-ACTOR-09, R-TRUST-04, R-TRUST-05)."),
    # spec/08 — mutations + registry title
    (VMAP,
     "| M024 | receive-side registration without kernel revalidation | R-MARSHAL-05 |",
     "| M024 | receive-side registration without kernel revalidation | R-MARSHAL-05 |\n| M025 | spawn clones parent context unattenuated | R-ACTOR-09 |"),
    (VMAP,
     "| M032 | contains_capability skips `FunctionValue.env` | R-MARSHAL-06 |",
     "| M032 | contains_capability skips `FunctionValue.env` | R-MARSHAL-06 |\n| M034 | release failure silently ignored (`unwrap` → `let _`) | R-CORE-12 |"),
    (VMAP,
     "## 2. Mutation registry → obligation map (M001–M024 + M032, R-TEST-04)",
     "## 2. Mutation registry → obligation map (M001–M025, M032, M034, R-TEST-04)"),
    # records — scope note extension
    (RECORDS,
     "(`R-CANON-12`, `R-CORE-11`, `R-MARSHAL-05`, `R-MARSHAL-06`, `R-PERSIST-07`; remediations SEC-003/004/005/016/018).",
     "(`R-CANON-12`, `R-CORE-11`, `R-MARSHAL-05`, `R-MARSHAL-06`, `R-PERSIST-07`; remediations SEC-003/004/005/016/018)." + RECORDS_NOTE3),
    # README — count
    (README,
     "- `spec/03-obligation-matrix.md` — 157 stable requirement IDs (`R-…`; 148 from the frozen source + 9 post-audit frozen addenda) with status and provenance",
     "- `spec/03-obligation-matrix.md` — 161 stable requirement IDs (`R-…`; 148 from the frozen source + 13 post-audit frozen addenda) with status and provenance"),
    # req/_validate.py — recorded register growth
    (VALIDATE,
     "    # C-77 (SEC-001/SEC-002 remediation, addendum I) and C-78…C-81\n    # (SEC-003/004/005/016/018, addendum II) — 76 -> 81, recorded here for the\n    # same reason.\n    if len(c_ids) != 81:\n        err(f\"expected 81 C- rows in spec/06, found {len(c_ids)}\")",
     "    # C-77 (SEC-001/SEC-002 remediation, addendum I), C-78…C-81\n    # (SEC-003/004/005/016/018, addendum II), and C-82…C-85 (SEC-006/020/022,\n    # addendum III) — 76 -> 81 -> 85, recorded here for the same reason\n    # (raw rows incl. the C-39 pointer; the index excludes it).\n    if len(c_ids) != 85:\n        err(f\"expected 85 C- rows in spec/06, found {len(c_ids)}\")"),
    # spec/_build_index.py — sections
    (BUILDIDX,
     '"R-CORE-10","R-CORE-11"],prov("27485-27654"',
     '"R-CORE-10","R-CORE-11","R-CORE-12"],prov("27485-27654"'),
    (BUILDIDX,
     '"R-TRUST-01","R-TRUST-02","R-TRUST-03"],prov("27611-27624"',
     '"R-TRUST-01","R-TRUST-02","R-TRUST-03","R-TRUST-04","R-TRUST-05"],prov("27611-27624"'),
    (BUILDIDX,
     '"R-ACTOR-07","R-ACTOR-08"],prov("25457-26108"',
     '"R-ACTOR-07","R-ACTOR-08","R-ACTOR-09"],prov("25457-26108"'),
    # spec/_build_index.py — requirement rows
    (BUILDIDX,
     ' ("R-CORE-11","S-02","I2 predicate signatures, canonical form (frozen addendum)","addendum",SPEC,[],["ror-kernel","ror-runtime"],["R-TEST-09","R-KERN-04"],["C-80"]),',
     ' ("R-CORE-11","S-02","I2 predicate signatures, canonical form (frozen addendum)","addendum",SPEC,[],["ror-kernel","ror-runtime"],["R-TEST-09","R-KERN-04"],["C-80"]),\n' + IDX_CORE12),
    (BUILDIDX,
     ' ("R-TRUST-03","S-03","No hidden authority; evaluator sees references only","37722-37748;19153-19175",SPEC,[],["ror-kernel","ror-runtime"],["Track B mock kernel","visibility checks"],[]),',
     ' ("R-TRUST-03","S-03","No hidden authority; evaluator sees references only","37722-37748;19153-19175",SPEC,[],["ror-kernel","ror-runtime"],["Track B mock kernel","visibility checks"],[]),\n' + IDX_TRUST4 + '\n' + IDX_TRUST5),
    (BUILDIDX,
     ' ("R-ACTOR-08","S-15","No amplification / no teleportation theorems","26048-26070",SPEC,[],["ror-runtime"],["teleportation test","amplification test"],[]),',
     ' ("R-ACTOR-08","S-15","No amplification / no teleportation theorems","26048-26070",SPEC,[],["ror-runtime"],["teleportation test","amplification test"],[]),\n' + IDX_ACTOR9),
    # spec/_build_index.py — mutations
    (BUILDIDX,
     ' ("M024","receive-side registration without kernel revalidation",["R-MARSHAL-05"]),',
     ' ("M024","receive-side registration without kernel revalidation",["R-MARSHAL-05"]),\n' + IDX_MUTS3),
    # spec/_build_index.py — milestone maps
    (BUILDIDX, '"R-HOST-05","R-EFFECT-08","R-CORE-11"]),', '"R-HOST-05","R-EFFECT-08","R-CORE-11","R-CORE-12"]),'),
    (BUILDIDX, '"R-MARSHAL-04","R-MARSHAL-06"]),', '"R-MARSHAL-04","R-MARSHAL-06","R-ACTOR-09"]),'),
    # spec/_build_index.py — crate maps
    (BUILDIDX,
     '"R-MARSHAL-03","R-MARSHAL-04","R-MARSHAL-05","R-MARSHAL-06","R-CORE-11"],["ror-core","ror-kernel"]),',
     '"R-MARSHAL-03","R-MARSHAL-04","R-MARSHAL-05","R-MARSHAL-06","R-CORE-11","R-ACTOR-09","R-CORE-12"],["ror-core","ror-kernel"]),'),
    (BUILDIDX,
     '"R-RECOV-07","R-KERN-05","R-PERSIST-07"],["ror-core"]),',
     '"R-RECOV-07","R-KERN-05","R-PERSIST-07","R-TRUST-05"],["ror-core"]),'),
    # spec/_build_index.py — id-scheme counts
    (BUILDIDX,
     '"R-AREA-NN": "normative requirement/obligation (157; 148 source-transcribed + 9 post-audit frozen addenda)"',
     '"R-AREA-NN": "normative requirement/obligation (161; 148 source-transcribed + 13 post-audit frozen addenda)"'),
    (BUILDIDX,
     '"M0NN": "baseline mutation registry (25; 18 baseline + 7 post-audit: M019–M024, M032)"',
     '"M0NN": "baseline mutation registry (27; 18 baseline + 9 post-audit: M019–M025, M032, M034)"'),
]

# C-82..C-85 rows: line-based, inserted after C-81's row
CONTRA_C81_PREFIX = "| C-81 |"


def apply_edits(files: dict[Path, str]) -> dict[Path, str]:
    for path, find, repl in EDITS:
        n = files[path].count(find)
        if n != 1:
            print(f"ABORT: anchor x{n} (need exactly 1) in {path.name}: {find[:70]!r}")
            sys.exit(2)
        files[path] = files[path].replace(find, repl, 1)
    lines = files[CONTRA].splitlines(keepends=True)
    idx = [i for i, ln in enumerate(lines) if ln.startswith(CONTRA_C81_PREFIX)]
    if len(idx) != 1:
        print(f"ABORT: C-81 anchor rows = {len(idx)} (need 1)")
        sys.exit(2)
    for row in reversed(C_ROWS):
        lines.insert(idx[0] + 1, row + "\n")
    files[CONTRA] = "".join(lines)
    return files


def check_tree(root: Path, label: str) -> bool:
    """Full verification stack over the given repo root (real or sandbox)."""
    import json as _json
    ok = True
    spec01, matrix, records = (root / p for p in
        ("spec/01-canonical-specification.md", "spec/03-obligation-matrix.md",
         "spec/normative-normalization-records.md"))
    contra, vmap = root / "spec/06-contradictions-ambiguities.md", root / "spec/08-verification-mapping.md"
    extra = contra.read_text(encoding="utf-8") + vmap.read_text(encoding="utf-8")
    t01, t03, trec = (p.read_text(encoding="utf-8") for p in (spec01, matrix, records))
    n_ob = len(re.findall(r"\*\*(R-[A-Z]+-\d+)[^\n]*?\*\*", t01))
    n_mx = len(re.findall(r"^\|\s*R-[A-Z]+-\d+\s*\|", t03, re.M))
    n_rc = len(re.findall(r"^### (R-[A-Z]+-\d+)\s*$", trec, re.M))
    print(f"[{label}] obligations={n_ob} matrix_rows={n_mx} records={n_rc}")
    for want, got, what in ((161, n_ob, "obligations"), (161, n_mx, "matrix rows"), (148, n_rc, "records")):
        if got != want:
            print(f"  FAIL: {what} = {got}, expected {want}")
            ok = False
    for m in MARKERS:
        if m not in t01 and m not in t03 and m not in extra:
            print(f"  FAIL: marker {m!r} absent from addendum targets")
            ok = False
    out = subprocess.run(
        [sys.executable, str(CHECKER), "--records", str(records),
         "--spec01", str(spec01), "--matrix", str(matrix)],
        capture_output=True, text=True, check=False).stdout
    first = out.splitlines()[0] if out else ""
    print(f"[{label}] checker: {first}")
    if "161 spec/01 obligations, 161 matrix rows" not in first or "148 records" not in first:
        print("  FAIL: checker parse counts unexpected (vacuous-run guard)")
        ok = False
    bad = [ln for ln in out.splitlines() if re.search(r"\[D\d\] (" + "|".join(NEW_IDS) + r")\b", ln)]
    for ln in bad:
        print(f"  FAIL: new addendum obligation flagged: {ln.strip()}")
        ok = False
    if "FAIL:" in out:
        print("  FAIL: checker hard-failed (D1 class)")
        ok = False
    print(f"[{label}] checker warnings: {len(re.findall(r'WARN ', out))}")
    # index rebuild
    r = subprocess.run([sys.executable, str(root / "spec" / "_build_index.py")], cwd=root,
                       capture_output=True, text=True, check=False)
    counts = next((ln for ln in r.stdout.splitlines() if "requirements=" in ln), "")
    print(f"[{label}] index rebuild: {counts or r.stdout[-200:] or r.stderr[-200:]}")
    for want in ("requirements=161", "findings=84", "mutations=27", "tags=19", "sections=24"):
        if want not in counts:
            print(f"  FAIL: index counts missing {want!r}")
            ok = False
    data = _json.loads((root / "spec" / "10-index.json").read_text(encoding="utf-8"))
    blob = _json.dumps(data)
    for m in NEW_IDS + ["C-82", "C-85", "M025", "M034", "resolved-by-addendum"]:
        if m not in blob:
            print(f"  FAIL: 10-index.json missing {m!r}")
            ok = False
    # req validator (needs the full tree: sandbox or real repo root)
    v = subprocess.run([sys.executable, str(root / "req" / "_validate.py")], cwd=root,
                       capture_output=True, text=True, check=False)
    vtail = [ln for ln in v.stdout.splitlines() if "ERRORS" in ln or "ERROR " in ln]
    print(f"[{label}] req/_validate exit={v.returncode}: {vtail[:2]}")
    if v.returncode != 0:
        ok = False
    return ok


def main() -> int:
    apply_mode = "--apply" in sys.argv

    targets = [SPEC01, MATRIX, CONTRA, VMAP, RECORDS, README, BUILDIDX, VALIDATE]
    real = {p: p.read_text(encoding="utf-8") for p in targets}

    present = [m for m in MARKERS if any(m in real[p] for p in targets)]
    anchor_fail = []
    for path, find, _ in EDITS:
        if real[path].count(find) != 1:
            anchor_fail.append((path.name, find[:60]))
    if present or anchor_fail:
        if present:
            print(f"ABORT: addendum already applied (markers present: {present})")
        else:
            print("ABORT: anchors unexpectedly absent — tree changed?")
            for name, f in anchor_fail:
                print(f"  missing/duplicated anchor in {name}: {f!r}")
        return 2
    print(f"precheck: addendum ABSENT on real tree (no markers found) — "
          f"SEC-006/020/022 unfrozen (this absence is the finding); "
          f"{len(EDITS) + len(C_ROWS)} anchors intact")

    files = apply_edits({p: real[p] for p in targets})

    if not apply_mode:
        with tempfile.TemporaryDirectory() as td:
            box = Path(td) / "repo"
            box.mkdir()
            subprocess.run(f"git archive HEAD | tar -x -C '{box}'", shell=True,
                           cwd=REPO, check=True)
            for p in targets:
                (box / p.relative_to(REPO)).write_text(files[p], encoding="utf-8")
            ok = check_tree(box, "dry-run")
            print("\nDRY RUN: " + ("PROOF COMPLETE — addendum verifies clean"
                                   if ok else "VERIFICATION FAILED"))
            return 0 if ok else 1

    for p in targets:
        p.write_text(files[p], encoding="utf-8")
    print(f"applied: {len(EDITS) + len(C_ROWS)} edits across {len(targets)} files")
    ok = check_tree(REPO, "post-apply")
    print("\nAPPLY: " + ("VERIFIED" if ok else "VERIFICATION FAILED — inspect git diff"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
