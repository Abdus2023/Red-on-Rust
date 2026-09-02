# MOD-09 — HOST: Host boundary and replay

> Owns the only place the machine touches the outside world — and the fully
> deterministic mock of that world used for replay and recovery evidence.

## SECTION-ID

`MOD-09` (domain `HOST`). Owner module file for the `HOST` obligation area.

## TITLE

Host boundary — the partially trusted live-host gate (defense in depth), the
adapter's only-issued-effects scope, the ordered validating `ReplayHost`, the replay
correspondence theorem, and trace-level (not state-level) replay validation.

## PURPOSE

Keep the outside world outside the model: the machine decides *whether* an effect may
happen (MOD-08 gates); the host only *performs* what was durably issued, while
independently re-checking OS-level authority. Replay reconstructs machine behavior
from records alone — ordered, digest-validated, never re-executing the real world —
so that determinism, recovery, and audit do not depend on live external state.

## NORMATIVE-CONTENT

Normative text home: `spec/01` S-14; atomic renderings
`req/01-registry-part4-durability-concurrency.md` (HOST block). This module owns:

- **Host gate, defense in depth** (R-HOST-01): the live host independently validates
  concrete OS-level authority/policy for each effect (`HostPolicyOK`); the machine's
  step-11 check is fail-early, the host's is authoritative; `¬HostPolicyOK(E) ⇒
  ¬ExternalEffect(E)` (fixed reading per C-27).
- **Adapter scope** (R-HOST-02): the host performs **only issued effects** and is the
  single partially-trusted component ("Partial") in the trust table.
- **Ordered replay host** (R-HOST-03): `ReplayHost` reconstructs recorded effects and
  NEVER touches the external world; for every request it consumes the **next** trace
  entry and validates both `EffectId` and `EffectDigest` sequentially; mismatch or
  exhausted trace ⇒ `ReplayCorruption` / `ReplayTraceExhausted`; an unordered map is
  forbidden as the normative replay mechanism (HashMap form superseded — C-22).
- **Replay correspondence** (R-HOST-04): if `LiveRun(Σ₀)` produces trace `T` of
  issued/completed pairs, `ReplayRun(Σ₀, T)` produces the same final configuration,
  provided per-step equality of recorded vs replayed effects and receipts (IDs and
  digests). Machine-state replay is always valid; real-world replay only for
  reversible/idempotent effects — the replay host refuses to re-execute irreversible
  effects and returns the recorded result (effect classes per MOD-01 R-CALC-07;
  class rules open under U-06).
- **Trace-level validation** (R-HOST-05): replay validates the trace, not merely the
  final state; `ReplayHost` never executes the external effect again (registry second
  citations L22333, L23234).

Crate contract (mirrored by pointer): host execution and replay boundaries in
`ror-host` (R-REPO-02).

## NON-NORMATIVE-CONTENT

- The Phase 12 `HashMap<EffectId, EffectReceipt>` replay draft with optional cursor
  is superseded (C-22); retained as a warning about exactly the kind of shortcut this
  module forbids.
- Example effect operations (FileRead/NetSend/…) are illustrative instances of the
  open operation domain (U-21); OS policy examples (path allowlists, …) are
  deployment-side and outside the frozen machine.

## INPUTS

- `EffectRequest { id, effect }` — only after durable issuance (MOD-08 step 16;
  MOD-11 R-DUR-01/02).
- OS authority/policy configuration (deployment input to the live host; not machine
  state).
- Ordered recorded traces (`EffectIssued`/`EffectCompleted` pairs) from MOD-11 for
  replay.
- Recorded planner proposals for end-to-end replay (`PlannerAccepted`, MOD-13-side).

## OUTPUTS

- `EffectReceipt { id, effect_digest, result: Result<Value, HostFault> }` (live) or
  the next recorded receipt (replay).
- Host faults mapped into the machine fault taxonomy (MOD-01 R-CALC-06).
- Replay failures: `ReplayCorruption`, `ReplayTraceExhausted`.
- Host-trace term of the determinism theorem (MOD-07) and of observations (MOD-15).

## DEPENDENCIES

- Module dependencies: MOD-01 (`Effect`/receipt/fault types), MOD-08 (issuance),
  MOD-10 (digest validation), MOD-11 (durable trace source), MOD-13 (end-to-end
  replay composition).
- Consumers: MOD-08 (receipts resume continuations), MOD-12 (recovery consults host
  reconciliation), MOD-15 (live-vs-replay differential).
- Crate edge: `ror-host → ror-core, ror-runtime` (adapter boundary, `spec/07` §6).
- Blocking open items: **U-06** (per-class replay/reconciliation rules — with
  MOD-08/12), **U-15** (`ReconciliationOutcome` variants, MOD-12-side), **U-21**
  (operation domain), **U-07** (host-interaction `δ_t`).

## INVARIANTS

- `¬HostPolicyOK(E) ⇒ ¬ExternalEffect(E)`; machine check fail-early, host check
  authoritative (R-HOST-01).
- Host performs only durably issued effects (R-HOST-02; precondition owned jointly
  with MOD-11 R-DUR-01 — D-03 points there).
- Replay is ordered and validating: request `k` consumes trace entry `k`, matching ID
  and digest; else `ReplayCorruption`/`ReplayTraceExhausted` (R-HOST-03).
- `LiveRun(Σ₀) ~ ReplayRun(Σ₀, T)`: same final configuration under per-step equality
  of effects and receipts (R-HOST-04); replay validates the **trace**, not just final
  state (R-HOST-05).

## REQUIREMENTS

Canonical text: `spec/01` S-14. All 5 obligations `SPECIFIED`.

| ID | Obligation (short) | Provenance (`Red-on-Rust.md`) | Verification |
|---|---|---|---|
| R-HOST-01 | Host independently validates OS authority (defense in depth) | L8560–8580, L10168–10172 | host policy tests |
| R-HOST-02 | Host performs only issued effects; partially trusted | L41823–41841, L27644 | `PanicHost` harness (R-REF-06) |
| R-HOST-03 | Ordered ReplayHost; ID+digest per entry; no unordered map | L25972–25996, L38278–38302 | replay property tests |
| R-HOST-04 | Replay correspondence (machine replay valid; real-world per effect class) | L3947–3958, L26249–26262 | R-REF-01 recovery equivalence |
| R-HOST-05 | Replay validates trace, not just final state | L38278–38302 | trace comparison |

Atomic registry records under this module: REQ-HOST-001…014. **5 obligations / 14 records.**

## SECURITY-BOUNDARY

The live host is the **only "Partial" trust** component (R-TRUST-01): it can refuse,
delay, or misbehave, but it cannot create authority (it performs only issued
effects), cannot fabricate receipts that resume continuations (digest validation in
MOD-08), and cannot rewrite history (records are durable and checked in MOD-11/12).
The boundary is deliberately redundant: machine gate 11 (fail-early) ⊂ host check
(authoritative) — a machine-side policy bug alone must not suffice for an
unauthorized external effect.

## VERIFICATION-OBLIGATIONS

- Conformance: host policy tests (R-HOST-01); `PanicHost` boundary enforcement
  (panics if `execute()` precedes durable issuance — MOD-17's R-REF-06 double);
  replay property tests incl. exhausted-trace and mismatch cases; live-vs-replay
  final-state digest equality (with MOD-07/15); trace-level comparison (R-HOST-05,
  consumed by MOD-15's comparator).
- Recovery equivalence participates in `Canonical(Recover_P(D)) = Canonical(Recover_R(D))`
  evidence (MOD-12/15).
- Milestone gates: M5 (host policy, replay behavior), M8 (differential over
  live/replay), M10 (crash matrix T3/T4 rows depend on host invocation semantics).
- No dedicated M0nn mutant: the boundary is probed structurally via `PanicHost` and
  via replay-integrity tests.

## SOURCE-PROVENANCE

- Replay correction (ordered + digest validation): [31] (L25972–25996); master prompt
  §12 host-policy / §14 replay (L38217–38221, L38278–38302, anchors corrected per
  `req/00-method.md` §5.1); replay correspondence v2 theorem [9] (L3947–3958) +
  Phase 14 effect classes [33] (L26249–26262); trust row [60] (L41823–41841).
- Canonical set: `spec/02` S-14; `req/01-registry-part4-durability-concurrency.md`
  (HOST block).

## CROSS-REFERENCES

Owned here, binding elsewhere:

- R-HOST-03/05 → MOD-15 (normalized trace comparison), MOD-12 (replay drives
  recovery), MOD-11 (trace source is the durable journal).
- R-HOST-01 → MOD-08 (gate 11 fail-early twin), MOD-01 (chain conjunct).
- R-HOST-04 → MOD-13 (end-to-end replay consumes `PlannerAccepted` + ReplayHost),
  MOD-12 (recovery equivalence).

Owned elsewhere, binding HOST: R-DUR-01/02 (MOD-11 — invocation only after durable
issuance; the host is the *consumer* of that guarantee), R-EFFECT-03 step 16 /
R-EFFECT-06 (MOD-08 — requests arrive only from step 16; receipts must validate),
R-CORE-08/R-ACTOR-07 (traces this module produces are terms of the determinism
theorem), R-CALC-07 (MOD-01 — effect classes gate real-world replay; open U-06),
R-PLANNER-02 (MOD-13 — planner cannot invoke the host). Open items: U-06, U-15,
U-21, U-07.
