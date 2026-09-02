# MOD-04 — BUDGET: Budget algebra and resource accounting

> Owns the resource story: the budget structure `⟨C, R, W⟩`, checked arithmetic,
> and the conservation laws that make budgets non-forgeable and non-teleportable.

## SECTION-ID

`MOD-04` (domain `BUDGET`). Owner module file for the `BUDGET` obligation area.

## TITLE

Budget model — consumables `C = ⟨F,I,D⟩`, reserved capacities `R = ⟨M,S⟩`, deadline
`W`; checked arithmetic; dual capability/runtime gating; partition conservation.

## PURPOSE

Make every resource accounting fact *provable arithmetic*, not convention: budgets
are structured (consumable vs reserved vs deadline), all operations use checked
arithmetic with explicit failure, effect issuance escrows worst-case completion, and
the global three-way partition `available + escrowed + consumed = initial` is
conserved across every transition, spawn, completion, and crash.

## NORMATIVE-CONTENT

Normative text home: `spec/01` S-11; atomic renderings
`req/01-registry-part3-resources-effects.md` (BUDGET block). This module owns:

- **Structure** (R-BUDGET-01): `B = ⟨C, R, W⟩`; consumables strictly decrease and are
  never returned; reserved capacities are held for a scope then released; the deadline
  compares against logical time (MOD-03's R-CAP-09 time), never wall-clock.
- **Checked arithmetic** (R-BUDGET-02): `BudgetError {ConsumableExhausted,
  ReservedCapacityExceeded, ReservedCapacityUnderflow, DeadlineExceeded}`;
  `saturating_sub` MUST NOT be used for semantic accounting.
- **Reservation predicates** (R-BUDGET-03): `ReserveOK(r,R,R_max) ⇔ R + r ≤ R_max`;
  `ReleaseOK(r,R) ⇔ r ≤ R` (frozen correction of the pre-fix mixed-direction form —
  C-07).
- **Dual gate** (R-BUDGET-04): `WithinBudget(E, C, R, R_A) ⇔ cost_C(E) ≤ C ∧
  ReserveOK(cost_R(E), R, R_max) ∧ cost(E) ≤ R_A` — runtime budget *and* capability
  ceiling (the ceiling conjunct is MOD-03's R-CAP-06 operand).
- **Conservation** (R-BUDGET-05): `C_n + Σ cost_cons(c_i) = C_0`;
  `R_n + Σ release_i = R_0 + Σ reserve_i`; `∀ active steps: t_i ≤ W`; global
  partition `C_available + C_escrowed + C_consumed = C_initial` with the three
  partition transfers (spawn = ownership transfer; issuance = `issue`→consumed +
  `complete_max`→escrowed; completion = actual→consumed, remainder→available) —
  canonical operative statement of the no-teleportation invariant (central restatement
  R-CORE-05 in MOD-01 — marked duplication D-02).
- **Time advancement** (R-BUDGET-06): `δ_t(pure) = 0`, `δ_t(host/scheduler) > 0`,
  validity `t + δ_t ≤ W`.
- **Cost model contract** (R-BUDGET-07): `CostModel` maps operations to
  `Cost {consumable, reserved}`; `Consumable ≠ Reserved` at the type level; the
  mapping is a configurable semantic contract, not anonymous tuples.
- **Budget fault** (R-BUDGET-08): any failed gate ⇒ `fault(BudgetExhausted)`; **no
  partial debit**; fault transitions preserve `C` and `R` (REQ-BUDGET-032).

Crate contract (mirrored by pointer): budget types and algebra in `ror-core`;
enforcement gates called from `ror-runtime`; budget *primitives* co-located with the
kernel (`ror-kernel`) per R-REPO-02 (normative text in `spec/01` S-22).

## NON-NORMATIVE-CONTENT

- Superseded dimension vectors: v1 6-dim, v0.1 5-dim `⟨F,M,C,I,W⟩` (C-06).
- The pre-fix `BudgetOK` mixing reservation directions (C-07) — recorded so an
  implementer never reads L7314 alone.
- The `⟨0,0,0⟩`-consumables-on-fault draft wording (C-28) — cosmetic; both forms
  preserve conservation.
- `BudgetAllocationSpec` validation policy is *not* budget-algebra content; it is an
  open decision item (U-03, MOD-06-side) which this module's predicates will host
  once frozen.

## INPUTS

- `EffectCost {issue, complete_max, reserve}` per request (MOD-01 type; MOD-08
  computes charges at gates 8–10, 13).
- Capability ceiling `R_A` for the dual gate (MOD-03).
- Logical time `t` and transition kind (for `δ_t`; from MOD-05/06/07).
- Spawn allocation specs (MOD-06; policy open under U-03).

## OUTPUTS

- Gate verdicts (`BudgetOK` true/false) and `fault(BudgetExhausted)` /
  `fault(DeadlineExceeded)` transitions (MOD-05/08 consume).
- Updated budget partitions per transition (durable content of snapshots/journal —
  MOD-11; survival invariant checked by MOD-12).
- `BudgetError` values (checked-arithmetic failures are data, never panics).

## DEPENDENCIES

- Module dependencies: MOD-01 (types `Consumable`/`Reserved`/`Budget`/`LogicalTime`),
  MOD-03 (ceiling operand; logical time discipline).
- Consumers: MOD-05 (every gated transition), MOD-06 (spawn escrow/teleportation
  laws), MOD-08 (gates 7–10, 13, completion accounting), MOD-11 (escrow durability),
  MOD-12 (post-crash revalidation).
- Crate edges: types in `ror-core`; gates via `ror-runtime`; primitives in
  `ror-kernel` (`spec/07` §2/§6).
- Blocking open items: **U-01** (operational meaning of the `D` consumable — AMB-01;
  exhaustion behavior is not testable until decided), **U-07** (per-transition `δ_t`
  values — AMB-19), **U-03** (spawn split policy, with MOD-06 — AMB-03).

## INVARIANTS

- `C_available + C_escrowed + C_consumed = C_initial` (R-BUDGET-05; canonical
  statement; central restatement R-CORE-05 — D-02). Spawn moves `available` → child's
  `available` (transfer, not creation); send carries no budget.
- `ReserveOK(r,R,R_max) ⇔ R + r ≤ R_max`; `ReleaseOK(r,R) ⇔ r ≤ R` (R-BUDGET-03).
- `WithinBudget(E,C,R,R_A) ⇔ cost_C(E) ≤ C ∧ ReserveOK(cost_R(E),R,R_max) ∧
  cost(E) ≤ R_A` (R-BUDGET-04).
- `δ_t(pure) = 0`; `δ_t(host/scheduler) > 0`; transition valid only if `t + δ_t ≤ W`
  (R-BUDGET-06).
- No partial debit on denial; fault transitions preserve `C` and `R`
  (R-BUDGET-08, REQ-BUDGET-032).
- Escrowed funds are immovable except via completion accounting or authoritative
  reconciliation (with MOD-08 R-EFFECT-05/07, MOD-11 R-DUR-05, MOD-12).

## REQUIREMENTS

Canonical text: `spec/01` S-11. All 8 obligations `SPECIFIED`.

| ID | Obligation (short) | Provenance (`Red-on-Rust.md`) | Verification |
|---|---|---|---|
| R-BUDGET-01 | `B = ⟨C=⟨F,I,D⟩, R=⟨M,S⟩, W⟩` semantics | L8683–8700, L9161–9175 | U-01 (D semantics) blocking |
| R-BUDGET-02 | Checked arithmetic; no `saturating_sub` | L9207–9245, L38002–38004 | M007, M009 |
| R-BUDGET-03 | `ReserveOK` / `ReleaseOK` predicates | L7487–7520, L8692–8696 | reservation property tests |
| R-BUDGET-04 | `WithinBudget` dual gate (runtime + capability ceiling) | L8692–8696 | short-circuit Track C (with MOD-08) |
| R-BUDGET-05 | Conservation (consumables, reserved, deadline, global partition) (D-02 canonical) | L7408–7425, L28203–28240, L35210–35215 | `BUDGET-CONSUMPTION-CONSERVATION`, `BUDGET-ESCROW-CONSERVATION`, teleportation test |
| R-BUDGET-06 | Time advancement `δ_t` (pure=0, host/scheduler>0, `t+δ_t ≤ W`) | L8698–8700, L10164–10168 | U-07 open |
| R-BUDGET-07 | `CostModel` contract; `Consumable ≠ Reserved` typing | L9155–9205, L10171–10177 | — |
| R-BUDGET-08 | ¬BudgetOK ⇒ `fault(BudgetExhausted)`, no partial debit | L7345–7352, L7410–7419 | Track C budget-gate test |

Atomic registry records under this module: REQ-BUDGET-001…032 — incl. explicitly
placed audit records REQ-BUDGET-008 (`D` operational meaning; AMB-01/U-01) and
REQ-BUDGET-032 (v0.3 E-RequestDenied: fault transitions preserve `C`,`R`; deny-side
cross-reference to MOD-08).
**8 obligations / 32 records.**

## SECURITY-BOUNDARY

Budgets are the machine's answer to resource exhaustion as an attack: an attacker who
can spend less than accounted, reserve more than granted, or teleport budget between
partitions defeats the resource-bounded claim of the thesis (R-SCOPE-01). Trust:
budget system = Yes (R-TRUST-01). Security-critical surfaces: checked arithmetic
(no saturation, no overflow-to-zero), escrow that survives crashes, and the refusal
to *ever* release `complete_max` escrow for an indeterminate effect (guarded by
mutation M008, mechanically in MOD-11/MOD-12).

## VERIFICATION-OBLIGATIONS

- Tags: `BUDGET-CONSUMPTION-CONSERVATION` (R-BUDGET-05);
  `BUDGET-ESCROW-CONSERVATION` (shared with MOD-11's R-DUR-05 and MOD-08's
  R-EFFECT-05 — escrow created at issuance, durable, survives crash).
- Mutations targeting this module: M007 (omit budget gate), M009 (permit negative
  resources); M008's escrow-release defect leaves durable state in MOD-11 (owner
  there; conservation consequence here).
- Conformance: budget partition conservation over randomized Spawn/Request/Complete
  sequences; teleportation test over the actor tree (with MOD-06); Track C
  dual-gate/short-circuit assertions (with MOD-08).
- Milestone gates: M5 (budget gates inside effect authorization), M9 (kill rate
  covers M007/M009), M10 (escrow survival across crash matrix).
- Determinism tie-in: all budget arithmetic is over logical time (R-CAP-09) so that
  the determinism theorem (MOD-07) is preserved.

## SOURCE-PROVENANCE

- Budget model v0.3 frozen: [16] (L8653–9050); predicates corrected [15]
  (L7487–7520); Rust shapes [17] (L9140–9245); partition freezing [35]
  (L28203–28240); master prompt §7 (L37964–38020, re-anchored per
  `req/00-method.md` §5.1); v0.3 rules L8726–8786 (E-Request/E-Spawn premises).
- Canonical set: `spec/02` S-11; `req/01-registry-part3-resources-effects.md`
  (BUDGET block).

## CROSS-REFERENCES

Owned here, binding elsewhere:

- R-BUDGET-04/08 → MOD-08 (realized as request gates 7–10 + denial short-circuit).
- R-BUDGET-05 → MOD-06 (spawn is transfer), MOD-08 (issuance/completion transfers),
  MOD-11 (escrow durability), MOD-12 (survival invariant R-RECOV-06).
- R-BUDGET-06 → MOD-07 (scheduler-step deltas), MOD-09 (host-interaction deltas).
- R-BUDGET-07 → MOD-02 (static bound computed against the same `CostModel`).

Owned elsewhere, binding BUDGET: R-CORE-05 (central restatement, MOD-01 — D-02);
R-EFFECT-05/07 (MOD-08 computes the actual charges; this module owns the accounting
law they must satisfy); R-DUR-05 (MOD-11 owns the durability of the escrow record);
R-PLANNER-02 (MOD-13: planner cannot modify budgets — enforcement at this module's
API surface). Open items: U-01, U-07 (this module, blocking), U-03 (with MOD-06),
U-13 (epoch/timestamps, MOD-13-side).
