# FINAL1 — 09. Open Architectural Decisions

FINAL1 carried forward every unresolved item from the cleaned authorities and
all five audits **without adjudicating any of them**. Stable identities are
preserved exactly (`U-nn`, `C-nn`, `X-nn`, `V-nn`, `F-nn`, `F-INFL-nn`, `AMB-nn`);
nothing was merged, renumbered, re-graded, or closed by inference. Where a
decision **was** taken by the owner (frozen addenda I–IX, U-38's governance
adoption), this registry records the decision's existence and its register
state — it does not re-take it, and FINAL1 MUST NOT reopen Addenda VII–IX or
U-38 without explicit owner authorization.

Owner of every OPEN item: the specification authority empowered to issue frozen
addenda (R-SCOPE-03 STOP-and-report discipline). `U-90` is *not* a decision: it
is the mutation-harness fixture ID recorded at spec/09 process note 9 and is
listed here once, to prevent anyone mistaking it for a dangling reference.

## A. spec/09 register (computed status per row)

39 rows registered under U-01…U-45; the register's numbering contains gaps (e.g. U-10…U-12, U-18…U-20). FINAL1 neither fills, renumbers, nor reuses gap numbers — items keep their numbers when withdrawn or folded. **28 OPEN, 11 resolved.**

| ID | Title | Status | Resolution / note |
|---|---|---|---|
| `U-01` | Operational meaning of the `duration` consumable (D) | RESOLVED | by frozen addendum IX (2026-09-03) |
| `U-02` | Canonical encoding of machine (non-data) state is not frozen | OPEN | — |
| `U-03` | Spawn budget-allocation policy (who decides `B_alloc`, and its bounds) | OPEN | — |
| `U-04` | `await` constructor: formal retraction record | OPEN | — |
| `U-05` | Isolation ladder (WASM / OS-process modes): retired or deferred? | OPEN (stale) | the frozen addendum `R-ARCH-05` retires the ladder (C-93 re-graded); the U-05/C-19 register rows were not re-graded — preserved as-is |
| `U-06` | Effect replayability/reversibility/idempotence: semantics of non-boolean values and link to effect classes | OPEN | — |
| `U-07` | Per-transition logical-time deltas | RESOLVED | by frozen addendum IX (2026-09-03) |
| `U-08` | Fault taxonomy unification | OPEN | — |
| `U-09` | `Value` domain collision + orphaned `AdmissibleConstraint` | OPEN | — |
| `U-13` | `PlannerMetadata` / `ProposalDigest` definitions + staleness check exactness | OPEN | — |
| `U-14` | Error-variant enumeration (subset of U-08) | OPEN | — |
| `U-15` | `ReconciliationOutcome` variants | OPEN | — |
| `U-16` | `EventSequence` vs `WalSequence` | OPEN | — |
| `U-17` | Runnable queue: snapshot field vs recovery reconstruction | OPEN | — |
| `U-21` | `Op` / `Target` / `Params` domains | OPEN | — |
| `U-22` | Static effect-set inference (J2) not present in the frozen pipeline | OPEN | — |
| `U-23` | Is `ValidatedPlan` a type, a predicate, or both? | OPEN | — |
| `U-24` | Which canonical envelope is frozen? | OPEN | — |
| `U-25` | Two tag namespaces share the `TAG_*` prefix; which constants may an implementation import? | OPEN | — |
| `U-26` | Which layer owns the name `StepResult`? | OPEN | — |
| `U-27` | Which `ActorStatus` shape governs, and where does shape (iii)'s continuation live? | OPEN | — |
| `U-28` | Which `MachineEvent` names govern, and are the eight undeclared paths declared or struck? | OPEN | — |
| `U-29` | Which `CanonicalError` shape governs, and do the unit variants survive? | OPEN | — |
| `U-30` | Which payload does `MarshalledValue` carry — `Value` or canonical `Vec<u8>`? | OPEN | — |
| `U-31` | Which field set is `Authority`'s, which is `Constraint`'s, and what holds the kernel's arena? | OPEN | — |
| `U-32` | Does the durable `WalFrame` carry `payload_length`, and what is its checksum's input domain? | OPEN | — |
| `U-33` | Which reference-model declarations govern, and are its undeclared types declared or struck? | OPEN | — |
| `U-34` | Which turn-[31]/turn-[32] state structs govern — `run_state`, `members` and `scheduler`? | OPEN | — |
| `U-35` | The determinism theorem's own parameters are undefined | OPEN | — |
| `U-36` | Is `Lifetime` wall-clock or logical time? | RESOLVED | by frozen addendum IX (2026-09-03) |
| `U-37` | Fixed integer widths for semantic and serialized quantities (`usize` elimination) | OPEN | — |
| `U-38` | `spec/_check.py` severity wiring: D2/D3 warn where the SEC-023 class lives | RESOLVED | by repository-gate adoption (U-38 option (b); not a frozen addendum) |
| `U-39` | The two 16-step request protocols: which one does S-12 publish? | RESOLVED | by frozen addendum VII (2026-09-03) |
| `U-40` | Step-10 deadline predicate: `t ≤ W` or `t + δ_t(req) ≤ W`? | RESOLVED | by frozen addendum VII (2026-09-03) |
| `U-41` | Durable record payload for issuance: what makes `DurableIssued` and escrow survivable? | RESOLVED | by frozen addendum VII (2026-09-03) |
| `U-42` | Live journal/fsync failure at step 14: declared fault, rollback, or journal-driven commit? | RESOLVED | by frozen addendum VII (2026-09-03) |
| `U-43` | Persistence boundaries around the effect transaction: snapshot cadence, ID-counter restoration, completion sync | RESOLVED | by frozen addendum VII (2026-09-03) |
| `U-44` | Request-frame verification tags: add `REQUEST-ARGS-LTR` and `REQUEST-NON-CAP-SHORT-CIRCUIT` to the frozen tag set? | RESOLVED | by frozen addendum VII (2026-09-03) |
| `U-45` | Adopt R-BUDGET-10…14 (resource-accounting audit addendum), and reconcile its escrow paths with R-BUDGET-09? | RESOLVED | by frozen addendum VIII (2026-09-03) |

Full bodies, amendment notes and superseded-wording quotes are canonical in `spec/09`; FINAL1 re-emits nothing there beyond the status index above, and re-grades nothing (note especially the U-05 staleness row — a *recorded disagreement between the normative addendum and the register*, preserved as such).

## B. spec/06 open contradiction/ambiguity rows (41)

Open `C-…` rows and the decision items they hang on (computed; row text canonical in `spec/06`):

| C-ID | Severity | Linked decision / collision |
|---|---|---|
| `C-03` | MAJOR | **open** → U-09 |
| `C-04` | MAJOR | **open** → U-04 |
| `C-05` | MAJOR | **open** → U-06 |
| `C-08` | MAJOR | **open** → U-08 |
| `C-14` | MAJOR | **open** → U-02 |
| `C-15` | MAJOR | **open** → U-02 |
| `C-16` | MINOR→MAJOR | **open** → U-02 (part of) |
| `C-19` | MAJOR | **open** → U-05 |
| `C-24` | MAJOR | **open** → U-03 |
| `C-26` | MINOR | **open** → U-17 (minor) |
| `C-30` | MINOR | **open** → U-09 |
| `C-38` | MINOR | **open** → U-13 (minor) |
| `C-45` | MAJOR | **open** → U-09 |
| `C-46` | BLOCKING | **open** → `term/` X-01 |
| `C-48` | BLOCKING | **open** → `term/` X-54 |
| `C-49` | MAJOR | resolved-by-later-text (incompleteness **open**) |
| `C-50` | MAJOR | **open** → `term/` X-58 |
| `C-51` | MAJOR | **open** → `term/` X-57 |
| `C-54` | MAJOR | **open** → `term/` X-64 |
| `C-55` | MAJOR | **open** → `term/` X-65 |
| `C-57` | BLOCKING | **open** → `term/` X-67 (BLOCKING) |
| `C-59` | MAJOR | **open** → `spec/09` U-08 / `term/` X-69 |
| `C-61` | MAJOR | **open** → `spec/09` U-28 / `term/` X-71 |
| `C-62` | MAJOR | **open** → `spec/09` U-29 / `term/` X-72 |
| `C-63` | MAJOR | **open** → `spec/09` U-26 / `term/` X-73 |
| `C-64` | MAJOR | **open** → `spec/09` U-27 / `term/` X-74 |
| `C-65` | MINOR | **open** → `spec/09` U-02, U-08, U-09 / `term/` X-75 |
| `C-66` | MAJOR | **open** → `spec/09` U-30 / `term/` X-76 |
| `C-67` | MAJOR | **open** → `spec/09` U-31 / `term/` X-77 |
| `C-68` | MAJOR | **open** → `spec/09` U-33 / `term/` X-78 |
| `C-69` | MAJOR | **open** → `spec/09` U-33 / `term/` X-79 |
| `C-71` | MINOR | **open** → `term/` X-81 |
| `C-72` | MAJOR | **open** → `spec/09` U-31 / `term/` X-82 |
| `C-73` | MAJOR | **open** → `spec/09` U-34 / `term/` X-83 |
| `C-74` | MAJOR | **open** → `spec/09` U-33 / `term/` X-84 |
| `C-75` | MAJOR | **open** → `term/` X-85 |
| `C-76` | MAJOR | **open** → `term/` X-86 |
| `C-98` | BLOCKING | **open** → U-35 |
| `C-99` | MAJOR | **open** → U-35 |
| `C-101` | MAJOR | **open** → U-02 |
| `C-102` | MINOR | **open** → U-37 |

`C-46` (X-01 BLOCKING) and `C-48` (X-54) remain open at register level although the frozen addenda R-CORE-11 / R-CANON-13 resolved their underlying choices “at the normative layer” — the register rows themselves were not re-graded; carried verbatim.

## C. Carried-forward unresolved matters by input pass

### REF1 (reference-independence / differential audit)

- **Items:** F-01…F-11 (all `Disposition: OWNER-DECISION / TRACK`, none resolved; severities MAJOR×5, MINOR×2 + others, none BLOCKING/FAIL); verdict `REF1-CONDITIONAL`; §12 residual uncertainties. Enforcement surfaces: crate-edge enforcement obligations unregistered (F-09/HD-5/V-02).
- **FINAL1 disposition:** carried verbatim; §17 and `final/08` bind REF1-CONDITIONAL as the only admissible rendering

### V1 (evidence-integrity audit)

- **Items:** F-INFL-01…F-INFL-12 (dispositions PRESERVE / BLOCK-UPGRADE / OWNER-DECISION / TRACK; none is a current defect — they are inflation *guards* and material-gap records); verdict `V1-CONDITIONAL`; §8 residual UNKNOWN (4 rows).
- **FINAL1 disposition:** carried; §28 evidence model implements the guard semantics; the two contradictions V1 records *in the corpus* (F-INFL-12 registry disagreement `spec/10-index.json` vs `spec/07` §6 = dep V-05; and the spec/06 C-09 README orientation drift) remain unadjudicated

### persistence cleaning (persistence-crash-consistency audit)

- **Items:** Verdict: contract satisfies the requested crash-consistency property **provided the frozen addenda are normative**; the single substantive residual is recovery-step granularity `AMB-27 / REQ-RECOV-021` (reconciliation inside `Recover(D)` vs after `RecoveryComplete`). Mechanical gate `audit/_crash_consistency_checker.py` guards against clause weakening.
- **FINAL1 disposition:** residual carried in §29 and `final/09` §B; the *conditional* form of the verdict is preserved (audit-of-specification, not verification of implementation)

### effect cleaning (request-pipeline audit + remediation draft)

- **Items:** GAP-01…GAP-18; addendum VII resolved U-39…U-44 (C-103…C-107/C-109) and registered M037/M038; `audit/request-pipeline-remediation-draft.md` remains **NOT ADOPTED**; `spec-addendum7-draft.md` is the decision record for adopted content only.
- **FINAL1 disposition:** no draft was adopted by this compilation; recommendations that did not receive a frozen addendum stay recommendations (FINAL1 MUST NOT convert audit recommendations into normative requirements)

### determinism cleaning (semantic-nondeterminism audit)

- **Items:** DET-001…DET-018; C-98…C-102 graded `open` (this pass issued **no addendum** of its own); U-35 (theorem terms undefined) and U-37 (fixed integer widths) OPEN; U-36 resolved later by addendum IX (R-CAP-11). Clean categories (zero f32/f64; zero std::env) recorded as CLEAN — negative results are audit findings too. §5.4 replay limitation preserved in GI-DET-07.
- **FINAL1 disposition:** U-35's unfalsifiability note is attached to GI-DET-01 so the theorem can never be cited as PASS-verified; the boxed formula is transcribed unmodified

### budget cleaning (resource-accounting audit)

- **Items:** Addendum VIII froze R-BUDGET-10/11/13 (U-45 resolved; C-108 re-graded); `R-BUDGET-12` deliberately NOT frozen (folded into R-BUDGET-15/16, addendum IX); `R-BUDGET-14` **deferred** to a resource-family pass; U-03 (spawn allocation policy) stays open outside its security-direction closure (R-ACTOR-09).
- **FINAL1 disposition:** the ID gaps (no R-BUDGET-12, no R-BUDGET-14) are recorded at their source — the `spec/09` U-01 resolution line (“no R-BUDGET-12 ID is frozen”; “R-BUDGET-14 stays deferred”) — and in `final/09` §E / `final/10`; FINAL1 treats gap numbers as non-reusable without freezing new IDs for them

### security auditing (authority-trust-external-effect audit)

- **Items:** SEC-001…SEC-023 (3 CRITICAL, 5 HIGH, 3 MEDIUM-HIGH, 9 MEDIUM, 2 LOW/MEDIUM, 1 LOW); remediated by the security post-audit frozen addenda (rows carrying the `post-audit remediation SEC-nnn` tag in `spec/01`; incl. R-CORE-11…14, R-CAP-10, R-KERN-04…06, R-MARSHAL-05/06, R-HOST-06, R-RECOV-08, R-PERSIST-07/08, R-BUDGET-09, R-ACTOR-09/10, R-PLANNER-06/07, R-TRUST-04/05, R-ARCH-05, R-DUR-06/07 …); C-77…C-97 read `resolved-by-addendum`. Residual: U-08 (fault taxonomy) and U-14 (error-variant enumeration) stay OPEN despite the security-direction closures; U-38 resolved by repository-gate adoption (option (b), 2026-09-03) — not by normative text, and the 36 allowlisted D2/D3 warnings remain adjudicated warnings, not verified-clean rows.
- **FINAL1 disposition:** every remediation is cited through its frozen addendum; the compilation does not restate audit findings as new requirements

### dependency analysis (dep/ register)

- **Items:** V-01, V-03, V-04 (in part), V-09, V-10 RESOLVED by addenda III/VI; still open/re-scoped: V-02 (re-scoped; §13/§14 blocks now tracked but the obligation-homing question stands), V-04 (a)(c) records retained as ID-3 history, V-05 (machine-index vs spec/07 §6 disagreement — owner decision required; F-INFL-12 records it), V-06 (arrow-convention statement), V-07 (prose-vs-machine graph edges), V-08 (`ror-compiler → ror-kernel` decision), V-11 (re-scoped; module-row inference for MOD-06/08/10 stands); hidden dependencies HD-1…HD-6; documented cycles: module layer 2 non-trivial SCCs, requirement layer 63 SCCs, section layer one 16-section SCC (dep/03) — *reported for architectural review, not new defects*; `dep/05` §7 measured remediation prices for the four build-order blockers without applying any.
- **FINAL1 disposition:** §29 lists the open V-rows; cycle results are reported as the dep/ register states them — no dependency direction was changed by this compilation

### Staleness / disagreement records preserved by this compilation

- **register staleness — U-05/C-19.** `spec/01` R-ARCH-05 (frozen addendum) states the isolation ladder (U-05) is RETIRED by decision and `spec/06` C-93 is re-graded `resolved-by-addendum`; the `spec/09` U-05 row and `spec/06` C-19 row, however, still read `open`. FINAL1 preserves the normative decision (retirement) AND the unre-graded rows (register staleness), records the disagreement here, and takes no re-grade action: re-grading `spec/09`/`spec/06` rows belongs to the register owners, not to the compiler.
- **machine-index vs prose register.** `spec/10-index.json` `ror-host.depends_on` (and the two prose-in-edge entries) vs `spec/07` §6; tracked as dep/05 V-05 and V1 F-INFL-12; unadjudicated.
- **stale counts in living documents.** `req/04-verification-undefined.md` header prose says “all 497 registry records” and “8 records” where `req/registry.json` currently carries **545** records and §1 lists **9** rows (VU-01…VU-09); `spec/05-terminology.md` §8 says “78 canonical terms / 31 laws / X-01…X-86 / N-01…N-31” where `term/10-index.json` carries **86 / 33 / X-01…X-87 (87 entries) / N-01…N-33**; `README.md` paraphrases the collision register as “86-entry”. FINAL1 reports these as stale prose in the inputs and does not edit them (the counts in `final/*` are computed fresh from the machine indexes).
- **withdrawn claims preserved.** Two false claims made by earlier passes are preserved quoted-not-deleted per R-SCOPE-03 (spec/06 C-08 CapabilityError assertion; X-64 “`Fault::StalePlan` occurs nowhere” — false at L28373; see term/00 §6). FINAL1 restates neither as live nor as deleted.

## D. FINAL1-level symbol-reuse records (`FA-01…FA-10`)

Not `U-nn` rows (FINAL1 creates no register items in owned namespaces); compilation-layer ambiguity records, identical policy — conflict preserved, not adjudicated. Full table with disambiguation rules: `final/05` §3; index copy in `final/01` §29.

## E. Deferred register states (must not be back-filled)

- `R-BUDGET-12` — never frozen (rule folded into R-BUDGET-15/16 by addendum IX).
- `R-BUDGET-14` — deferred to a resource-family pass (U-01 resolution explicitly left it deferred).
- `U-90` — mutation-harness fixture ID (spec/09 process note 9), not a decision.
- `req/02` CN-01…CN-42 compound-not-split decisions and `req/04` VU-01…VU-09 remain in the `req/` register; the 8-vs-9 count in `req/04` §1 is stale prose, recorded above.

## F. What FINAL1 forbade itself

No new architectural design; no silent adjudication of unresolved findings; no conversion of audit recommendations into normative requirements (the request-pipeline remediation draft is NOT ADOPTED and stays a draft recommendation); no reopening of Addenda VII–IX or U-38 (owner-authorization boundary); no re-grading of spec/06/spec/09 rows; no manufacture of a reference implementation from the specification; REF1-CONDITIONAL and V1-CONDITIONAL are carried exactly as issued.
