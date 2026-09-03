# U-35 — proposed definitions for the four theorem terms

**STATUS: PROPOSAL. NOT ADOPTED. NOT FROZEN TEXT.**

This document is *not* part of the canonical specification. It issues no
`R-` obligation, changes no obligation status, and is cited by no register row
as authority. It exists so that U-35 can be **decided** rather than
**re-derived** — the same pattern as U-38, where the option was built and left
unadopted so the choice would cost a flag rather than a project.

If the specification owner accepts any part of this, the accepted part must be
issued as a numbered frozen addendum to `spec/01` under `spec/09`'s process
note 1, and *then* the register rows move. Until that happens, C-98/C-99 stay
`open` and DET-001/DET-005 stay unresolved (R-SCOPE-03).

The theorem under discussion, stated at `Red-on-Rust.md` L25338 (turn [31]) and
twelve other places:

> `InitialState + SchedulerTrace + HostTrace ⇒ UniqueMachineTrace`

None of its four terms is declared anywhere in 42,312 lines (T-82…T-85).

---

## 0. What has to be true of any answer

Three constraints bind every option below. They are not preferences; each is
forced by frozen text or by a finding already filed.

1. **`SchedulerTrace` must be an input, never the event log** (N-32). The
   L26998 form `Snapshot+EventLog+HostTrace+SchedulerTrace` makes the machine's
   own output an antecedent, which is circular: replaying a recorded log
   reproduces that log trivially and establishes nothing.
2. **`HostTrace` must be ordered and cursor-consumed** (R-HOST-03, DET-005).
   Of six `ReplayHost` declarations in six shapes (X-87), only L34498
   (`trace: Vec<EffectReceipt>` + `cursor`) satisfies this unconditionally.
3. **The equality relation must be stated.** `UniqueMachineTrace` asserts
   uniqueness, and uniqueness is meaningless without saying *up to what*. This
   is the half of DET-001 that no amount of type-declaring fixes.

---

## 1. `InitialState` — the decision is already made, in two incompatible ways

This is the term where the frozen source does the most damage, and it is worth
separating from the other three because **the choice is not open — it was made
twice, differently.** `term/_structs.py` derives:

```
### GlobalState  (3 decls, 2 shapes)
  L24156  turn[31] shape1  actors, logical_time, runnable, event_log,
                           next_effect_id, next_actor_id, scheduler: SchedulerState
  L25535  turn[32] shape2  actors, logical_time, runnable, event_log,
                           next_effect_id, next_actor_id
  L25862  turn[32] shape2 (field order differs from L25535)
```

**The scheduler is part of the machine state at turn [31] and is not at turn
[32].** That single field decides the theorem's shape:

- If `scheduler: SchedulerState` **is** in the state, then scheduler decisions
  are a *function of the state*, and `SchedulerTrace` is a derived quantity —
  passing it as an independent antecedent is redundant at best and
  contradictory at worst (the state could imply a different next actor than the
  trace supplies, and nothing says which wins).
- If it **is not** in the state, the theorem is well-formed as written, but
  `RunnableQueue` gained a `members: BTreeSet<ActorId>` field in the same turn
  ([32], L25892 vs L24274) — so the queue now carries membership that the
  scheduler used to own, and the boundary moved rather than disappeared.

There is a further wrinkle worth surfacing because it is a live determinism
hazard rather than a definitional one. At L10375 the source declares
`GlobalConfig` with `actors: HashMap<ActorId, ActorState>` (one of three
`GlobalConfig` declarations — L9495 types the same field `ActorTable`) where every
`GlobalState` declaration uses `BTreeMap`. Whatever `InitialState` is defined
to be, **it must be defined over the `BTreeMap` form**; a `HashMap`-typed
initial configuration reintroduces DET-003 at the theorem's own antecedent.

**Proposed:**

```
InitialState := GlobalState(turn-[32] shape)  ⊎  KernelAuthorityImage
```

with `actors` typed `BTreeMap` normatively, and `KernelAuthorityImage` the
closed image of the kernel authority arena (DET-009) and capability slotmap
(DET-010) — both reachable from a transition today and fields of no declared
state. Choosing turn [32] keeps `SchedulerTrace` a genuine input, which is what
makes the theorem non-vacuous.

**This is the sub-decision I would most want an owner to make explicitly**,
because adopting turn [31] instead does not merely change a definition — it
makes the theorem's second parameter redundant, and the right response would be
to restate the theorem, not to define the term.

---

## 2. `SchedulerTrace`

```rust
pub struct SchedulerDecision {
    pub step: LogicalTime,   // the transition this decision governs
    pub actor: ActorId,      // which runnable actor is scheduled
}
pub type SchedulerTrace = Vec<SchedulerDecision>;
```

- **One decision per scheduler turn**, aligned by `step`: the *k*-th decision
  governs the transition taken at logical time *k*. A trace shorter than the run
  is a `TraceExhausted` fault, not a silent stop.
- `actor` must be in the runnable set at `step`, or the replay faults. This is
  what makes the trace *checkable* rather than merely consumed.
- Canonical encoding: `step` then `actor`, both fixed-width **little-endian**
  per L27702's `u64 LE` precedent — but see DET-007: LE and BE grammars both
  appear in frozen text, and this proposal does not resolve that. It only
  states that whichever wins must apply here too.
- **Not** the `EventLog` (N-32).

## 3. `HostTrace`

```rust
pub type HostTrace = Vec<EffectReceipt>;   // ordered; consumed by cursor
```

Adopting the L34498 `ReplayHost` shape as normative, per X-87 and R-HOST-03.
Consumption is strictly sequential: receipt *k* answers the *k*-th effect
request, and the host validates **both** `EffectId` and `EffectDigest` before
returning it — L34498 and L35218 already say this in prose; this makes it the
definition rather than a claim about one of six declarations.

The `HashMap<EffectId, EffectReceipt>` form at L24011 must then be recorded as
superseded (R-SCOPE-03: quoted, not deleted), because under it a permuted
effect sequence replays identically and DET-005 is unfixable.

## 4. `UniqueMachineTrace`

```
MachineTrace := Vec<(StateDigest, EventEnvelope)>
```

one entry per transition, and two traces are **equal** iff both sequences are
pointwise equal:

- `StateDigest` — the canonical digest of `InitialState`'s type after the
  transition. **This depends entirely on U-02** (the canonical machine-state
  encoding is unfrozen, DET-002); until U-02 is decided this definition names a
  function that does not exist. That is a real dependency, not a caveat.
- `EventEnvelope` — the canonical encoding of the event appended by that
  transition.

Requiring **both** matters: state-digest equality alone permits two runs that
reach identical states by emitting different events, and event equality alone
permits identical event streams over divergent hidden state.

---

## 5. What this proposal does not do

- It does **not** make the theorem true. With these definitions the theorem
  becomes *falsifiable*, which it currently is not — any divergence today is
  post-hoc attributable to "a different `SchedulerTrace`", since nothing says
  what one is. Eleven hidden inputs (DET-003/004/006/009/010/011/012/013 and
  the rest) still reach the trace and must be closed separately.
- It does **not** resolve U-02 (§4 depends on it), U-07 (δ_t), U-36
  (`Lifetime`), or DET-007 (LE vs BE, §2 depends on it). Three of the four
  definitions have an unresolved dependency, and pretending otherwise would
  reproduce exactly the defect this audit was asked to find.
- It does **not** claim replay reproduces the external world. `HostTrace` is a
  record of *receipts*; L23234 states the limit and this proposal keeps it —
  machine-state and event reproduction, subject to explicit external-effect
  reconciliation.

## 6. If adopted

`spec/01` S-02 gains a frozen subsection adjacent to R-CORE-08; T-82…T-85 move
from `UNDECLARED-TYPE` to their declared types with `frozen_at` anchors; C-98
and C-99 move from `open` to `resolved-by-addendum`; X-87's disposition names
the governing shape; and the effect-order-permutation test in the audit §6
becomes meaningful, since there is finally a specified ordering to violate.

None of that should happen until someone with authority over the specification
says so.
