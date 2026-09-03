# MOD-08 — EFFECT: Effect model and frozen request sequence

> Owns the only road from "program wants" to "machine asks": the immutable effect
> descriptor and the frozen 16-step gate sequence every request must traverse.

## SECTION-ID

`MOD-08` (domain `EFFECT`). Owner module file for the `EFFECT` obligation area.

## TITLE

Effect model and request sequence — evaluation of capability/target/arguments,
canonical `Effect` construction, the frozen gate order, short-circuit semantics,
affordability escrow, causal receipt validation, and completion accounting.

## PURPOSE

Ensure no external effect is ever *implicit*. A `Request` expression produces a
canonical `Effect` that traverses every gate — authority, resources, deadline, host
policy, durability — in one frozen order; denial at any gate annihilates the request
without side effects; only a request that survives all gates and durable issuance may
reach the host. Receipts re-enter causally (ID **and** digest), and completion
accounting always succeeds because worst-case cost was escrowed at issuance.

## NORMATIVE-CONTENT

Normative text home: `spec/01` S-12; atomic renderings
`req/01-registry-part3-resources-effects.md` (EFFECT block). This module owns:

- **Request semantics** (R-EFFECT-01): `Expr::Request` means construct → authorize →
  account → log → Pending → yield `EffectRequest`. It never means "execute the effect
  in the AST/evaluator"; `step()` never executes the host (REQ-EFFECT-001 second
  citation L10391).
- **Gated transition shape** (R-EFFECT-02): every active transition is
  `Pre(c,Σ) ∧ BudgetOK(c,Σ) ∧ AuthOK(c,Σ) ⊢ Σ →_c Σ'` (`AuthOK` only on
  authority-requiring transitions) — the operational face of `¬Authorized ⇒
  ¬ExternalEffect` (distribution D-08: predicate canonical in MOD-03).
- **Frozen 16-step request sequence** (R-EFFECT-03): capability → target → arguments
  (strict LTR) → construct canonical Effect + digest → validate lineage → authorize
  (kernel, logical time) → capability ceiling → consumable budget (`issue +
  complete_max`) → reservation → deadline (`t ≤ W`) → host policy (fail-early) →
  allocate deterministic `EffectId` → commit budget/reservation (transactional) →
  **durable issuance** (Prepared + Issued, each fsynced — the mechanism is MOD-11's
  R-DUR-02) → enter `Pending` → host invocation. Any deviation is a bug; no host
  interaction before durable issuance. Canonical realization of the 7-conjunct
  external-effect chain R-CORE-02 (marked refinement duplication D-12).
- **Short-circuit** (R-EFFECT-04): denial at any gate ⇒ subsequent gates uncalled,
  `next_effect_id` unincremented, actor budget unchanged, event log unchanged,
  `HostExecutor::execute` never invoked (five assertions per gate).
- **Guaranteed completion accounting** (R-EFFECT-05): gate 8 checks
  `can_consume(issue.checked_add(complete_max))`; overflow ⇒ fault; the remaining
  budget is then *mathematically* guaranteed `≥ complete_max` — the frozen fix for
  the under-escrow vulnerability (C-23).
- **Causal receipt validation** (R-EFFECT-06): a receipt must validate against both
  `EffectId` and `EffectDigest` of the pending effect before resumption; mismatch ⇒
  `fault(ReplayCorruption)`, continuation NOT resumed, reservation NOT released.
- **Completion accounting** (R-EFFECT-07): on valid receipt — charge `complete`
  (`≤ complete_max`), release reservation, append `EffectCompleted {id, digest,
  result}`, resume continuation with the receipt value.

Also owned (explicit placement): REQ-EFFECT-037…040 — the v0.3 `E-Request`,
`E-RequestDenied` (deterministic fault precedence: capability before budget),
`E-Receipt`, `E-ReceiptMismatch` rules.

Crate contract (mirrored by pointer): effect pipeline in `ror-runtime`; the durable
issuance step calls `ror-persistence` append/sync (R-DUR-02).

## NON-NORMATIVE-CONTENT

- Earlier numbering schemes (15-rule v0.2/v0.3; 14-step `step_request`; 14-gate
  `finalize_request`) are superseded presentations of the same content (C-01); the
  16-step form is canonical.
- The early `Effect` shape that carried the capability inside `EffectRequest` is
  superseded (R-CALC-04 provenance); the pre-correction `complete` field name is
  superseded by `complete_max` (C-23).
- Effect-property per-operation table: illustrative (U-06; declared classes in
  MOD-01's R-CALC-07).

## INPUTS

- `EvalStep::RequestEffect` intents from MOD-05 (capability/target/argument values
  evaluated under evaluator discipline).
- Kernel verdicts (`Valid`, `Authorized`, ceiling) from MOD-03; budget verdicts and
  partitions from MOD-04; `HostPolicyOK` fail-early signal (authoritative twin in
  MOD-09); append/sync services from MOD-11.
- `EffectReceipt` values from MOD-09 (live or replay).

## OUTPUTS

- `Effect` + `EffectDigest` (canonical identity, MOD-01 type), `EffectId`
  allocations, `EffectPrepared`/`EffectIssued` durable records (via MOD-11),
  `EffectRequest` yields to the host adapter (MOD-09).
- Actor status `Pending` (MOD-06 state; MOD-07 stops scheduling it).
- Faults: capability/budget/deadline/host-policy/authorization faults per the frozen
  taxonomy (MOD-01 R-CALC-06), `ReplayCorruption`/`InvalidReceipt` on bad receipts.
- `EffectCompleted` events (to MOD-11 journal) and resumed continuations (to MOD-05).

## DEPENDENCIES

- Module dependencies: MOD-01 (descriptor/fault/cost types), MOD-03 (gates 5–7),
  MOD-04 (gates 8–10, 13; completion accounting law), MOD-05 (LTR evaluation,
  suspension), MOD-06 (Pending status, wakeup), MOD-07 (turn discipline),
  MOD-11 (step 14 mechanism), MOD-09 (step 11 fail-early + step 16 invocation).
- Consumers: MOD-09 (only issued requests), MOD-11/12 (journal chain + recovery
  classification), MOD-14/15 (effect trace observations).
- Crate edges: `ror-runtime` orchestrating; durable step via `ror-persistence`.
- Blocking open items: **U-06** (effect-property classes ↔ replay/reconciliation
  rules — AMB-20), **U-21** (`Op`/`Target`/`Params` domains), **U-01/U-07**
  (budget premises), **U-02** (`Constraint`/digest encodings upstream).

## INVARIANTS

- Frozen gate order (16 steps); no reordering, no skipping (R-EFFECT-03). Denial is
  total and side-effect-free (R-EFFECT-04).
- `complete_max` affordability at issuance: `can_consume(issue + complete_max)` with
  checked add; completion then cannot underflow (R-EFFECT-05).
- Receipt identity: `R.effect_id = pending.id ∧ R.digest = EffectDigest(pending.E)`
  before resume; otherwise `ReplayCorruption`, no resume, no release (R-EFFECT-06).
- Completion: `charge(complete ≤ complete_max)`; release reservation; append durable
  `EffectCompleted`; resume (R-EFFECT-07).
- Deterministic fault precedence on denial: capability failure before budget failure
  (REQ-EFFECT-038, v0.3 form).
- Durability prefix: host invocation only after durable `Issued` (mechanism and
  canonical statement owned by MOD-11's R-DUR-01 — cross-reference, D-03).

## REQUIREMENTS

Canonical text: `spec/01` S-12; addendum I. All 8 obligations `SPECIFIED`.

| ID | Obligation (short) | Provenance (`Red-on-Rust.md`) | Verification |
|---|---|---|---|
| R-EFFECT-01 | Request = construct→authorize→account→log→Pending→yield | L12177–12194 | step isolation tests |
| R-EFFECT-02 | Gated transition shape `Pre∧BudgetOK∧AuthOK` | L7145–7155, L8700–8710 | — |
| R-EFFECT-03 | Frozen 16-step request sequence (D-12 canonical) | L38022–38050, L23857–23948 | gate short-circuit matrix |
| R-EFFECT-04 | Denial short-circuits all subsequent gates (5 assertions/gate) | L24003–24045 | Track C (5 assertions per gate) |
| R-EFFECT-05 | complete_max affordability at issuance | L25799–25825 | budget escrow tests; `BUDGET-ESCROW-CONSERVATION` |
| R-EFFECT-06 | Receipt validates ID + digest; mismatch ⇒ ReplayCorruption, no resume | L23949–24002, L25952–25970, L38052–38072 | `EFFECT-RECEIPT-DIGEST-VALIDATION`, M017, M018 |
| R-EFFECT-07 | Completion accounting (charge, release, log, resume) | L23949–24002 | conservation tests |
| R-EFFECT-08 | Receipt-result admission: recursive contains_capability over the result payload at any nesting depth; no capability, no closure; data-domain only; host error via declared closed fault mapping only | addendum I (SEC-001) | EFFECT-RECEIPT-RESULT-NO-AUTHORITY, M019, M020 |

Atomic registry records under this module: REQ-EFFECT-001…040 (incl. explicitly
placed v0.3 rule extractions REQ-EFFECT-037…040).
**8 obligations / 40 records.**

## SECURITY-BOUNDARY

This module realizes the thesis's central claim operationally: **the chain from
untrusted proposal to external effect exists only here, and it is gated end-to-end.**
Every upstream module exists to make these gates meaningful (compiler validation,
kernel authority, budget), and every downstream module trusts only what leaves here
durably issued. The five short-circuit assertions per gate are the measurable
definition of "denial": nothing observable may happen after a `no`.

## VERIFICATION-OBLIGATIONS

- Tag: `EFFECT-RECEIPT-DIGEST-VALIDATION` (tampered digest ⇒ `ReplayCorruption`, no
  resume — M017, M018); co-verified: `EFFECT-ISSUE-DURABLE-BEFORE-HOST` (canonical
  verifying module MOD-11; the ordering halves of steps 14/16 are this module's).
- Mutations targeting this module: M010 (allocate `EffectId` before authorization —
  gate ordering), M017, M018.
- Conformance: 14-gate/16-step short-circuit matrix (5 assertions per gate); causal
  replay integrity suite; Track C gated-operation stage markers (REQ-TEST-036,
  MOD-15-side).
- Milestone gates: M5 (authorization, budget gates, deadline, host policy,
  EffectId/Digest, durable issuance, receipt validation).
- Harness enforcement consuming this module: `PanicHost` panics if invoked before all
  gates pass; `MockKernel` asserts exactly-one-call with exact parameters (R-REF-06,
  MOD-17 infrastructure).

## SOURCE-PROVENANCE

- Frozen 16-step sequence: [54] §8 (L38022–38050, anchor corrected per
  `req/00-method.md` §5.1), machine-internal 14-gate form [30] (L23857–24002,
  superseded numbering C-01), completion accounting correction [31]
  (L25479–25492, L25799–25825), Track C short-circuit [31]/[32] (L24003–24045).
- Canonical set: `spec/02` S-12; `req/01-registry-part3-resources-effects.md`
  (EFFECT block).

## CROSS-REFERENCES

Owned here, binding elsewhere:

- R-EFFECT-03 steps 5–7 → MOD-03 (kernel verdicts); steps 8–10, 13 → MOD-04;
  step 11 → MOD-09 (fail-early twin of R-HOST-01); step 14 → MOD-11 (R-DUR-02
  mechanism); step 15 → MOD-06/07 (Pending + unschedulable); step 16 → MOD-09.
- R-EFFECT-05/07 → MOD-04 (partition arithmetic law R-BUDGET-05), MOD-11 (escrow
  durable, R-DUR-05), MOD-12 (escrow survives recovery).
- R-EFFECT-06 → MOD-09 (receipt production/replay), MOD-10 (digest bytes), MOD-11
  (journal digest chain R-DUR-03, M017).
- R-EFFECT-01/02 → MOD-05 (yield/suspension discipline; gated transition form).

Owned elsewhere, binding EFFECT: R-CORE-02/03 (MOD-01 central statements this module
refines — D-12, D-08); R-DUR-01 (MOD-11 owns the durable-before-host statement);
R-HOST-02 (MOD-09: host performs only issued effects); R-CALC-04/05 (MOD-01 owns the
descriptor/cost types); R-BUDGET-04/08 (MOD-04 owns the gate predicates); R-RECOV-02
(MOD-12 classifies in-flight effects after a crash). Open items: U-06 (this module,
blocking M5/M7 reconciliation behavior), U-01/U-07 (MOD-04), U-21 (MOD-01/03/10).
