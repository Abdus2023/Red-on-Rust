# Addendum VIII — Resource-accounting adoption (ADOPTED 2026-09-03)

**Status:** APPLIED by `audit/spec_addendum8.py` (same discipline as addenda I–VII).
U-38 is deliberately NOT touched — checker-policy wiring stays separate from normative
resource-accounting changes.

**Owner decision (U-45 / C-108):**

1. **R-BUDGET-10 ADOPTED** — resource-state atomicity (every Op transition is one
   transactional resource mutation; `Precondition failure ⇒ Σ' = Σ`, with the explicit
   post-issuance host-failure caveat). Strengthens the gate matrix.
2. **R-BUDGET-11 ADOPTED, RECONCILED** — the escrow disposition normal form. R-BUDGET-09's
   three paths REMAIN the totality; `Consumed`/`Refunded` are its completion leaves;
   `Transferred`/`Disposed-with-explicit-sink` its reconciled leaves; `Remains-Indeterminate`
   is a BOUNDED transient (logical-time bound → reconciliation), never a terminal disposition.
   No divergence from R-BUDGET-09 remains and no amendment to it is required.
3. **R-BUDGET-13 ADOPTED** — persistent-capacity accounting as a dimension separate from
   volatile RAM (release on scope exit/halt; durable storage retained and snapshot-compacted;
   overflow faults).
4. **R-BUDGET-12 NOT ADOPTED** — its D-advancement/debit rule decides `spec/09` U-01, a
   separate open item; folded into U-01. Remains a non-normative proposal here.
5. **R-BUDGET-14 NOT ADOPTED** — deferred to a resource-family pass (tagged X-vector
   mechanism beyond the gate-matrix scope). Remains a non-normative proposal here.

**Register arithmetic:** 178 → 181 obligations (+3: R-BUDGET-10/11/13); findings 108 / rows
109 unchanged; U- items unchanged at 39 (U-45 resolved ≠ deleted); mutations 38 → 39 (M039);
verification tags 21 → 23 (`BUDGET-ESCROW-DISPOSITION-TOTALITY`, `PERSISTENT-CAPACITY-ACCOUNTING`).

**Frozen text** (spec/01, each its own original — no substitution):

**R-BUDGET-10 (resource-state atomicity — frozen addendum).** All resource mutations belonging to an operational transition occur transactionally: a failed precondition produces zero state drift and zero partial debit — `Precondition failure ⇒ Σ' = Σ` — except for post-issuance host-failure transitions, where `c_issue` remains consumed and the escrow is disposed via host-failure consumption/refund (R-DUR-07, R-BUDGET-11). This is the resource-level refinement of R-CORE-12's transition atomicity and R-CORE-14's s12–s14b atomic section: every Op-01…Op-22 transition is a single atomic resource mutation, and the `audit/_conservation_checker.py` randomized-transition harness is the gate evidence. *(Frozen addendum VIII — resource-accounting audit, owner decision 2026-09-03; additive per R-SCOPE-03; extends R-CORE-05/12, R-DUR-07; resolves C-108, decision U-45; no source transcription.)*

**R-BUDGET-11 (escrow disposition normal form — frozen addendum).** R-BUDGET-09's three paths are the escrow-disposition totality: every escrowed amount terminates via `Completed`, host-failure consumption, or durable `Reconciled`; the five-path normal form (`Consumed`, `Refunded`, `Transferred`, `Disposed-with-explicit-sink`, `Remains-Indeterminate`) is the complete fine structure OF that totality, not a fifth terminal path. `Consumed` (`C_consumed`) and `Refunded` (`C_available`) are the two leaves of `Completed` and of host-failure consumption (`actual ≤ complete_max` charged, remainder refunded; R-DUR-07). `Transferred` (child available partition) and `Disposed-with-explicit-sink` (`C_disposed` / `C_supervisor`) are the reconciled-outcome leaves selected per the R-RECOV-08 admissible-outcome table. `Remains-Indeterminate` (awaiting authoritative reconciliation) is a BOUNDED transient, not a disposition: it MUST reach reconciliation by the R-BUDGET-09 logical-time bound (machine state only, R-CAP-09) and then terminate via one of the four terminal leaves. No escrow may remain in any leaf indefinitely — the R-BUDGET-09 quiescent-strand invariant holds, and `C_available + C_escrowed + C_consumed + C_disposed = C_initial` at every reachable point. *(Frozen addendum VIII — resource-accounting audit, owner decision 2026-09-03; additive per R-SCOPE-03; extends R-BUDGET-09, R-DUR-05/07, R-EFFECT-05, R-RECOV-08/09; resolves C-108, decision U-45; mutation M039; no source transcription.)*

**R-BUDGET-13 (persistent-capacity accounting — frozen addendum).** Volatile RAM (`MEMORY` `M`) is kept strictly distinct from persistent storage capacity (`PERSISTENT_STORAGE` `M_storage`): RAM is released on scope exit or actor halt, while durable storage is retained across actor halts and managed via snapshot compaction (R-PERSIST-05/07, R-BUDGET-03 reservation predicates apply to each dimension separately). Persistent capacity MUST be accounted per WAL frame and per snapshot artifact; a snapshot that would exceed `M_storage` MUST fault, never silently truncate. *(Frozen addendum VIII — resource-accounting audit, owner decision 2026-09-03; additive per R-SCOPE-03; extends R-BUDGET-03/05, R-PERSIST-04/05/07; resolves C-108, decision U-45; no source transcription.)*

