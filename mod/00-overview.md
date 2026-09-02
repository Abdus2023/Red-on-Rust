# mod/00 — Semantic Module Split: Overview and Method

**What this document set is.** The frozen specification (`Red-on-Rust.md`) already has
two organizations: `spec/` splits it into 24 sections (`S-01`…`S-24`) that follow the
*document's* structure (turn order, phase boundaries), and `req/` splits it into 545
atomic requirement records grouped into 24 extraction areas. This set, `mod/`, is the
third organization required for engineering: a split into **17 semantic modules** that
follow **architectural responsibility** — which component owns a requirement's semantics —
rather than document length or transcript position.

**What this set is not.** It is not a third copy of the normative text. The canonical
normative text remains single-homed: full obligation wording lives in
`spec/01-canonical-specification.md` (with `spec/03` the obligation index), and atomic
wording in `req/01-registry-part*.md`. Module files register ownership, contracts,
invariants, boundaries and verification obligations **by reference**; the one-line
obligation labels in each `REQUIREMENTS` section are navigational summaries copied from
`spec/03`, and where a summary and `spec/01` differ, `spec/01` governs.

**Status discipline.** Unchanged from `spec/00` §2: every requirement is `SPECIFIED`;
nothing here is `IMPLEMENTED`, `TESTED`, `VERIFIED`, or `PROVEN`, because this repository
still contains no code, tests, or proofs. The module split itself is specification
organization, not implementation evidence.

---

## 1. The modules

| Module | Domain | Responsibility (one line) | Crate home (frozen, R-REPO-02) | File |
|---|---|---|---|---|
| MOD-01 | CORE | Core semantic domain types, central invariants, trust model, overall architecture | `ror-core` | `01-core.md` |
| MOD-02 | COMPILER | Untrusted `Block` → validated `ExecutablePlan`; static judgments | `ror-compiler` | `02-compiler.md` |
| MOD-03 | CAPABILITY | Capability algebra (v0.2), derivation, revocation, kernel API | `ror-kernel` | `03-capability.md` |
| MOD-04 | BUDGET | Budget algebra `⟨C,R,W⟩`, conservation, checked arithmetic | `ror-core` (+ gates in `ror-runtime`/`ror-kernel`) | `04-budget.md` |
| MOD-05 | EVALUATOR | Explicit CEK machine, continuation discipline | `ror-runtime` | `05-evaluator.md` |
| MOD-06 | ACTOR | Actor isolation, spawn, mailboxes, marshalling/delegation boundary | `ror-runtime` | `06-actor.md` |
| MOD-07 | SCHEDULER | Deterministic FIFO scheduling, one transition per turn | `ror-runtime` | `07-scheduler.md` |
| MOD-08 | EFFECT | Effect model, frozen 16-step request sequence, receipt handling | `ror-runtime` (+ durable steps via `ror-persistence`) | `08-effect.md` |
| MOD-09 | HOST | Live host gate, host adapter scope, ordered replay | `ror-host` | `09-host.md` |
| MOD-10 | SERIALIZATION | Canonical byte format (15A), strict decoding, digests | `ror-core` (+ `vectors/canonical`) | `10-serialization.md` |
| MOD-11 | PERSISTENCE | WAL, snapshots, effect journal, durable issuance transaction (15B) | `ror-persistence` | `11-persistence.md` |
| MOD-12 | RECOVERY | Recovery algorithm, T0–T6 classification, reconciliation entry | `ror-persistence` (+ `ror-reference` oracle) | `12-recovery.md` |
| MOD-13 | AGENT | LLM/planner proposal boundary, staleness, replay recording | `ror-agent` | `13-agent.md` |
| MOD-14 | REFERENCE | Independent executable semantic model; independence boundary | `ror-reference` | `14-reference.md` |
| MOD-15 | DIFFERENTIAL | Generator, runner, comparator, shrinking, counterexamples | `ror-differential` | `15-differential.md` |
| MOD-16 | MUTATION | Mutation registry, kill-rate gate, self-validation | `mutations/registry.toml` (+ `ror-testkit`) | `16-mutation.md` |
| MOD-17 | VERIFICATION | Evidence discipline, test infrastructure, CI gates, claims, repository/order governance | `tests/` + `scripts/` | `17-verification.md` |

The module order is the dependency order of the user's requested domain list, which is
also the architectural layering: semantic foundation → untrusted-input boundary →
authority → resources → machine → concurrency → effects → durable boundary → external
world → agents above → verification machinery beside.

## 2. Ownership rules (how requirements were placed)

1. **One canonical owner per requirement.** Each of the 148 canonical obligations
   (`R-…`, `spec/03`) is owned by exactly one module. Ownership is decided by
   *architectural responsibility*: which component's behavior the requirement constrains
   (the place a violation would have to be introduced), per the frozen crate contracts
   (R-REPO-02) and the dependency graph (`spec/04`).
2. **No relocation for tidiness.** A requirement is never moved merely because another
   module looks like a cleaner organizational bucket. Obligations stay with semantic
   ownership even when the result is uneven (SCHEDULER legitimately owns only 2
   obligations; CORE legitimately owns 27). Document length played no role.
3. **Spanning requirements cross-reference, they do not move.** Where a requirement
   binds several components (e.g. the 16-step request sequence touches capability,
   budget, durability, host), it keeps one canonical owner; the other components appear
   in its module's `CROSS-REFERENCES` section and in the owner's `DEPENDENCIES`. The
   complete register is generated in `18-ownership-matrix.md`.
4. **No silent duplication of normative text.** Normative statements live in one home
   (`spec/01`/`req/`). The frozen source itself states several invariants twice (a
   central-invariant statement in the thesis, and the operative statement in the owning
   component). Such pairs are **explicitly marked duplications**, registered in
   `18-ownership-matrix.md` §3 (IDs `D-01`…`D-12`) with one side designated the
   canonical statement. Module files quote the formulas only at their canonical side;
   the other side of each pair carries the mark `(marked duplication — canonical
   statement <R-…> in MOD-…)`.
5. **Atomic records inherit ownership.** Each of the 545 `req/` records follows the
   module of its parent `R-…` obligation. The 16 records that cite zero or two parents
   (the v0.3 transition-rule extractions and two kernel records recovered in the audit
   passes) are placed individually — see `mod/_ownership.py` `REQ_OVERRIDE` and the
   rationale note in each receiving module's `REQUIREMENTS` section.
6. **Unresolved items are not assigned owners.** `U-…` decisions and `AMB-…` ambiguities
   are not owned; they are listed under every module they *block or affect*, with the
   blocking module named in `spec/09`.
7. **Splitting preserves semantics, not numbering.** Obligation IDs (`R-…`, `REQ-…`,
   `C-…`, `U-…`, `M0NN`, tags) are unchanged. The module layer adds only `MOD-NN`
   identifiers and `D-NN` duplication-register IDs. No requirement was rewritten,
   merged, dropped, or "improved"; the split is a total, duplicate-free partition of
   the 148 obligations and of the 545 atomic records.

## 3. Ownership decisions that required judgment (disclosed)

Rule 1 forces a single owner even where the obligation matrix lists several crates.
The non-obvious decisions, so they can be audited and challenged:

- **Marshalling (R-MARSHAL-01…04) → MOD-06 ACTOR.** The marshalling boundary is the
  *actor message boundary* (frozen inside Phase 13, the actor machine; ror-runtime).
  There is no MARSHAL module in the required domain list, and moving it to
  SERIALIZATION would confuse the transport format with the authority-blocking rule.
  SERIALIZATION is cross-referenced for the byte format (R-MARSHAL-03/04).
- **Durability boundary (R-DUR-01…05) → MOD-11 PERSISTENCE.** The 15B effect journal and
  the append/sync mechanics are `ror-persistence`'s contract; the causal protocol
  (`Issued ⇒ Prepared`, etc.) is a property of durable records. EFFECT keeps the
  request *sequence* (R-EFFECT-03, whose step 14 invokes this boundary); RECOVERY keeps
  the *application* of the classification (R-RECOV-02 matrix). Cross-referenced both ways.
- **Scheduler obligations (R-ACTOR-04, R-ACTOR-07) → MOD-07 SCHEDULER.** The obligation
  prefix is `ACTOR` for historical reasons (both were frozen inside the Phase 13 actor
  text); the scheduler is a separately required domain and these are its entire
  semantic content. ACTOR keeps isolation/spawn/mailbox obligations.
- **Comparator semantics (R-REF-05) → MOD-15 DIFFERENTIAL.** Normalization, first
  divergence, and "never final-value-only" are the comparator's contract
  (`ror-differential`), not the reference model's construction. REFERENCE keeps what the
  reference model *is* (R-REF-01…04: purpose, independence, scope, non-goals).
- **Execution modes (R-TEST-01) → MOD-15 DIFFERENTIAL.** The three modes
  (exhaustive/property/stress) are the differential harness's execution modes
  (15C.39); the CI *cadence* that schedules them is VERIFICATION's R-TEST-10.
- **Harness doubles (R-REF-06) → MOD-17 VERIFICATION.** `PanicHost`/`MockKernel` are
  test-infrastructure (`ror-testkit`); they *enforce* the EFFECT/CAPABILITY boundaries
  but are owned by the infrastructure side.
- **Scope/process rules.** R-SCOPE-03 (STOP-and-report) and the engineering corpus
  (`R-REPO-*`, `R-ORDER-*`, `R-CLAIM-*`) sit in MOD-17 VERIFICATION because they govern
  *conformance process and boundary enforcement*, not any runtime component's behavior.
  Each runtime module mirrors the clauses that bind it by pointer (no duplicated text).
- **R-SCOPE-04 (zero shared core logic) → MOD-14 REFERENCE** — it constrains exactly the
  production/reference independence boundary; its restatement R-REF-02 is the canonical
  enumeration (D-10).

## 4. Identifier scheme (additive)

| Prefix | Meaning | Defined in |
|---|---|---|
| `MOD-NN` | Semantic module (01…17) | this document, §1 |
| `D-NN` | Marked-duplication register entry | `18-ownership-matrix.md` §3 |
| `R-…`, `REQ-…`, `C-…`, `U-…`, `M-NN`, tags, `ROR-NNN`, `M0NN` | unchanged, per `spec/00` §3 | `spec/`, `req/` |

## 5. Files

| File | Content | Maintenance |
|---|---|---|
| `00-overview.md` | this document | hand-written |
| `01-core.md` … `17-verification.md` | the 17 module specifications, each with the required 13 fields + `CROSS-REFERENCES` | hand-written, machine-checked |
| `18-ownership-matrix.md` | full obligation→owner partition, atomic-record partition, duplication register, mutant/tag/milestone maps | **generated** by `mod/_build.py` |
| `19-index.json` | machine-readable module/obligation/cross-reference index | **generated** by `mod/_build.py` |
| `_ownership.py` | the ownership map (single source of truth for the two generated files) | hand-written |
| `_build.py` | generator + consistency checker | hand-written |

Checking:

```
python3 mod/_build.py            # validate module files against the ownership map
python3 mod/_build.py --write    # also regenerate 18-ownership-matrix.md + 19-index.json
```

The checker enforces: (a) the 148-obligation partition is total and overlap-free,
matched against `spec/03`; (b) the 545-record partition is total and overlap-free,
matched against `req/registry.json`; (c) every module file carries the required 13
fields in order plus `CROSS-REFERENCES`; (d) every owned obligation appears in its
module's `REQUIREMENTS` section and in no other module's `REQUIREMENTS` section;
(e) cross-reference and duplication targets exist and duplication marks are symmetric.

## 6. Required module field schema

Every module file carries, in this exact order:

1. **SECTION-ID** — `MOD-NN`.
2. **TITLE** — module name.
3. **PURPOSE** — the architectural responsibility this module alone discharges.
4. **NORMATIVE-CONTENT** — the semantic territory owned, with pointers to the canonical
   text (`spec/01` sections, `req/` record ranges); never a second normative rendering.
5. **NON-NORMATIVE-CONTENT** — illustrative material, examples, superseded forms kept
   for traceability, and explicitly non-normative source text relevant to the module.
6. **INPUTS** — typed artifacts/authority the module consumes, with their producers.
7. **OUTPUTS** — typed artifacts/faults/traces the module produces, with consumers.
8. **DEPENDENCIES** — modules, crate edges (`spec/07` §6), and blocking `U-…` items.
9. **INVARIANTS** — the module's owned invariants, quoted verbatim where the source
   gives formulae; cross-level restatements carry explicit duplication marks.
10. **REQUIREMENTS** — the obligations this module canonically owns (ID, short
    statement, provenance, verification tag), plus the inherited atomic record ranges.
11. **SECURITY-BOUNDARY** — the trust boundary this module maintains, per R-TRUST-01/02/03.
12. **VERIFICATION-OBLIGATIONS** — frozen tags, mutation IDs, conformance obligations,
    milestone gates, and tracks that produce this module's evidence.
13. **SOURCE-PROVENANCE** — `Red-on-Rust.md` turns + line ranges (using the re-verified
    anchors of `req/00-method.md` §5.1 where they correct `spec/03`), plus `spec/`
    sections and `req/` part files.

14. **CROSS-REFERENCES** (additional field, required by the spanning rule) — every
    obligation owned elsewhere that binds this module, and every owned obligation that
    binds other modules; with duplication-register (D-NN) links and open `U-…`/`AMB-…`
    items affecting the module.
