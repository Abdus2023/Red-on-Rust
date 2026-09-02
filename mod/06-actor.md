# MOD-06 — ACTOR: Actor isolation, spawn, mailboxes, marshalling boundary

> Owns per-actor state, actor creation, message transport, and the rule that
> authority never crosses an ordinary message boundary.

## SECTION-ID

`MOD-06` (domain `ACTOR`). Owner module file for most of the `ACTOR` area and the
entire `MARSHAL` area.

## TITLE

Actors and the marshalling boundary — isolated heaps/environments/continuations/
mailboxes/budgets/capability contexts; deterministic spawn with escrow and derived
capabilities; asynchronous send and blocking receive; ordinary marshalling that
recursively rejects capabilities, with explicit delegation as the only exception.

## PURPOSE

Provide concurrency **without** semantic nondeterminism and **without** implicit
authority flow. Actors are fully isolated execution containers; the only information
that crosses an actor boundary is a marshalled *pure value*; the only authority that
crosses is a freshly *derived, attenuated* capability produced inside the capability
kernel (MOD-03) via the explicit `Delegate` operation.

## NORMATIVE-CONTENT

Normative text home: `spec/01` S-15 (isolation/spawn/send receive) and S-16
(marshalling/delegation); atomic renderings
`req/01-registry-part4-durability-concurrency.md` (ACTOR, MARSHAL blocks). This
module owns:

- **Isolation** (R-ACTOR-01): for `a ≠ b`, `Heap(a) ∩ Heap(b) = ∅ ∧ Env(a) ∩ Env(b)
  = ∅`, and equally for continuations, mailboxes, budgets, capability contexts;
  actors instantiate with fresh arenas and `Environment::empty()` — no implicit
  environment inheritance.
- **Global state shape** (R-ACTOR-02): `GlobalState { actors: BTreeMap<ActorId,
  ActorState>, logical_time, runnable: RunnableQueue, event_log, next_effect_id,
  next_actor_id, scheduler }`; logical time, ID allocation, and the event log are
  strictly global; actors observe `global.logical_time` at the instant their
  transition executes.
- **Deterministic identity** (R-ACTOR-03): `ActorId`/`EffectId` from global monotonic
  counters (`N' = N + 1`); identity never from memory addresses, PIDs, UUIDs, thread
  IDs, or wall-clock.
- **Spawn** (R-ACTOR-05): transactional — (1) validate + escrow budget (spawn is
  budget *transfer*, not creation); (2) allocate child ID; (3) child receives
  **explicitly derived (attenuated) capabilities only** via `kernel.derive(parent_cap,
  constraint, t)` — wholesale copying/cloning forbidden; (4) construct isolated child
  state; (5) enqueue deterministically; (6) log `ActorSpawned`.
- **Send/Receive** (R-ACTOR-06): `Send` = marshal + enqueue into target mailbox + log
  `MessageSent` + wake a `Blocked` target exactly once (deterministic wakeup);
  `Receive` dequeues or blocks **without consuming fuel** — `Blocked` is suspension,
  not a transition; mailboxes are FIFO.
- **Actor-level corollaries** (R-ACTOR-08): no amplification (`Authority_after ≼
  Authority_before ∪ ExplicitlyDelegatedAuthority`) and no teleportation
  (`Σ_actors C + Σ_escrow C + Σ_issued C = C_global_initial`) — corollaries of
  MOD-01's R-CORE-04/R-CORE-05 through the marshalling and spawn rules.
- **Marshalling, canonical owner** (R-MARSHAL-01…04 — placed here per architectural
  responsibility: the marshalling boundary *is* the actor message boundary, frozen in
  the Phase 13 actor machine; see `mod/00-overview.md` §3). Ordinary marshalling
  recursively rejects capabilities — nested in lists, tuples, functions, any
  structure: `marshal_value(v) ⇒ Err(MarshalFault::CapabilityRequiresDelegation)` if
  `contains_capability(v)` (canonical statement; central restatement R-CORE-07 in
  MOD-01 — marked duplication D-04). Authority crosses only through explicit
  delegation: the `Expr::Delegate` node invokes the kernel and wraps the result in a
  `DelegatedCapability` envelope the marshaller accepts, `DelegatedAuthority ≼
  ParentAuthority`. Transport bytes are canonical bytes:
  `MarshalledValue = canonical_serialize(v)`, with `unmarshal(marshal(v)) = v` for
  all pure values (round-trip scope itself is open — AMB-06/U-09).

Crate contract (mirrored by pointer): actors + marshalling live in `ror-runtime`
(R-REPO-02).

## NON-NORMATIVE-CONTENT

- The isolation ladder (in-process / WASM / OS-process spawn modes of early design)
  is **unresolved history, not current requirements** — it vanished from every frozen
  phase without explicit retraction (C-19, AMB-18, U-05). Spawn currently has no
  isolation field.
- The `trust_level` premise of the v0.3 `E-Spawn` rule has no counterpart in the
  frozen AST or algebra (AMB-04, C-36).
- The two liveness enums `RunState` (scheduler-visible) and `ActorStatus`
  (machine-visible) coexist in frozen text; their mapping is implied, not tabulated
  (C-18, AMB-05; REQ-ACTOR-035 explicitly placed here).
- Delegation envelope field sketch (`L25700` area) is the operative delegation text;
  the *AST constructor* is absent from the frozen 12-constructor `Expr` (AMB-11,
  U-02) — the fields `⟨capability, constraint⟩` are defined at L25989–25992 (registry
  correction recorded in `req/00-method.md` §5.2).

## INPUTS

- Spawn intentions, send/receive requests from MOD-05 transitions.
- `BudgetAllocationSpec` attached to `Expr::Spawn` (MOD-02 surface; validation policy
  open — U-03).
- `derive` results and `DelegatedCapability` envelopes from MOD-03.
- Canonical encode/decode of pure values from MOD-10.
- Wakeup sources: receipts (MOD-08/09) and sends.

## OUTPUTS

- `ActorSpawned`, `MessageSent` events (to the global event log; durable via MOD-11),
  mailbox contents (`MarshalledValue`), deterministic child actor states.
- `MarshalFault::CapabilityRequiresDelegation` on any capability inside ordinary
  message data (including nested).
- Delegated capability registrations in the recipient's local capability context.

## DEPENDENCIES

- Module dependencies: MOD-01 (types/IDs), MOD-03 (derivation, authority opacity),
  MOD-04 (escrow/conservation), MOD-05 (per-actor CEK state), MOD-10 (marshal bytes).
- Consumers: MOD-07 (schedules these actors), MOD-11 (snapshot/journal content),
  MOD-14/15 (reference actor model + differential).
- Crate edge: `ror-runtime → ror-core, ror-kernel`.
- Blocking open items: **U-03** (spawn split policy — AMB-03), **U-05** (isolation
  ladder — AMB-04/18), **U-02** (`Constraint`/Delegate encoding, with MOD-02/10),
  **U-09** (marshal round-trip domain, AMB-06/21).

## INVARIANTS

- Isolation: `Heap(a) ∩ Heap(b) = ∅ ∧ Env(a) ∩ Env(b) = ∅` for `a ≠ b`; no actor
  mutates another's heap, environment, or continuation (R-ACTOR-01).
- Identity: `N' = N + 1`, ID = `N` before increment; identity is data (R-ACTOR-03).
- Spawn is transfer, not creation: child budget escrowed from parent; child authority
  `≼` parent via derivation only (R-ACTOR-05).
- Receive without message ⇒ `Blocked` **without fuel consumption**; mailboxes FIFO
  (R-ACTOR-06).
- No amplification: `Authority_after ≼ Authority_before ∪
  ExplicitlyDelegatedAuthority` (R-ACTOR-08).
- No teleportation: `Σ_actors C_consumable + Σ_escrow C_escrow + Σ_issued C_issue =
  C_global_initial` (R-ACTOR-08).
- Ordinary marshal: `contains_capability(v) ⇒ marshal(v) rejected` — recursive,
  no exceptions in pure data (R-MARSHAL-01; canonical statement of D-04).
- Delegation: `DelegatedAuthority ≼ ParentAuthority`; the runtime hands out a token
  envelope, never a raw kernel reference (R-MARSHAL-02).
- `unmarshal(marshal(v)) = v` for pure values within the marshal round-trip domain
  (R-MARSHAL-03; domain itself open under U-09/AMB-06).
- `CapRef ∉ marshal(v)` by default; `delegate(c, C, target_actor)` is the only
  authority transfer (R-MARSHAL-04).

## REQUIREMENTS

Canonical text: `spec/01` S-15/S-16. All 10 obligations `SPECIFIED`.

| ID | Obligation (short) | Provenance (`Red-on-Rust.md`) | Verification |
|---|---|---|---|
| R-ACTOR-01 | Actor isolation (heaps, envs, continuations, mailboxes, budgets, caps) | L41623–41641, L24268–24290 | Track D, isolation properties |
| R-ACTOR-02 | GlobalState shape; logical time global | L24148–24163, L25514–25546 | — |
| R-ACTOR-03 | Deterministic ID allocation; no address/PID/UUID/wall-clock identity | L24226–24245 | determinism tests |
| R-ACTOR-05 | Spawn: escrow + derived capabilities only; no wholesale clone | L25573–25615, L38074–38106 | Track D, amplification test, U-03 |
| R-ACTOR-06 | Send async + deterministic wakeup; Receive blocks without fuel; FIFO mailbox | L25702–25749, L38074–38106 | Track D, M013 |
| R-ACTOR-08 | No amplification / no teleportation theorems | L26048–26070 | teleportation test, amplification test |
| R-MARSHAL-01 | Recursive capability rejection in ordinary marshal (D-04 canonical) | L41647–41658, L25674–25701, L38074–38106 | `MARSHAL-NO-RAW-CAPABILITY` |
| R-MARSHAL-02 | Explicit delegation only; DelegatedCapability envelope; ≼ parent | L25972–26001, L25989–25992 | Track C (delegation) |
| R-MARSHAL-03 | MarshalledValue = canonical bytes; unmarshal(marshal(v)) = v | L25674–25701 | Track B (marshalling) |
| R-MARSHAL-04 | Semantic marshalling rule (CapRef ∉ marshal(v)) | L8695–8698 | Track B |

Atomic registry records under this module: REQ-ACTOR-001…009, REQ-ACTOR-017…030,
REQ-ACTOR-032…035; REQ-MARSHAL-001…010 (incl. explicitly placed REQ-ACTOR-024 v0.3
E-Spawn — AMB-04 — and REQ-ACTOR-035 RunState/ActorStatus, cross-referenced to
MOD-07; scheduler records REQ-ACTOR-010…016, REQ-ACTOR-031 belong to MOD-07).
**10 obligations / 37 records.**

## SECURITY-BOUNDARY

Actor boundaries are where *containment* is proven: a compromised or hostile actor
reads nothing outside its heap, holds only derived authority, and can spend only
escrowed budget. The marshalling gate is the single ordinary channel between actors;
making it recursively capability-free is what turns "isolation" from memory safety
into *authority* safety. The verifier's sharpest probes here: forced `CapRef`-in-`Send`
tests (amplification test), teleportation accounting over actor trees, M013 mailbox
reordering, and nested-capability marshalling (M006-class).

## VERIFICATION-OBLIGATIONS

- Tag: `MARSHAL-NO-RAW-CAPABILITY` (recursive rejection incl. nested caps; README tag
  `MARSHAL-CAPABILITY-REJECT` ≙ same per C-10/05 §normalization).
- Mutations: M013 (break mailbox FIFO); M006-class delegated-amplification probes.
- Conformance: marshalling authority isolation (embedded `CapRef` in `List` ⇒
  `MarshalFault`; recipient context unchanged); amplification test (forced CapRef
  through Send ⇒ fault); teleportation test (budget sum over actor tree); spawn
  isolation suite; delegation attenuation Track C; marshalling round-trip Track B.
- Tracks: Track D — independent single-threaded reference simulator proving trace
  equivalence with production `GlobalState` (REQ-TEST-058, MOD-15-side).
- Milestone gates: M6 (FIFO mailbox, spawn isolation, send/receive, delegation,
  blocked/wakeup) jointly with MOD-07.

## SOURCE-PROVENANCE

- Frozen actor machine: [32] (L25457–26108); global machine [31] (L24069–25428);
  master prompt §9 actors / §10 marshalling (L38074–38136, anchors corrected per
  `req/00-method.md` §5.1); theorems [32] (L26048–26070); delegation envelope
  [32] (L25972–26001).
- Canonical set: `spec/02` S-15/S-16; `req/01-registry-part4-durability-concurrency.md`.

## CROSS-REFERENCES

Owned here, binding elsewhere:

- R-MARSHAL-03/04 → MOD-10 (bytes are the canonical format; round-trip law scoped by
  that module's injectivity claim).
- R-MARSHAL-02 → MOD-03 (delegation is a kernel `derive`; envelope ≼ parent),
  MOD-02 (`Expr::Delegate` surface undecided — U-02), MOD-10 (envelope encoding).
- R-ACTOR-02 → MOD-07 (runnable queue contents), MOD-04 (global time/deadline),
  MOD-11 (snapshot content list).
- R-ACTOR-05 → MOD-03 (only `derive` may produce child authority), MOD-04 (escrow).
- R-ACTOR-06 → MOD-07 (wakeup enqueues at queue back).
- R-ACTOR-08 → MOD-01 (corollaries of R-CORE-04/05; not restatements — derivation
  chain only).

Owned elsewhere, binding ACTOR: R-ACTOR-04/07 schedule these actors (MOD-07);
R-CORE-07 (MOD-01 central restatement, D-04); R-EFFECT-03 step 15 sets `Pending`
(MOD-08); R-RECOV-03 step 10 reconstructs the runnable queue (MOD-12); R-PERSIST-04
snapshots carry actor state (MOD-11); R-PLANNER-02 (MOD-13: planner cannot allocate
actors). Open items: U-03, U-05 (this module, blocking M6), U-02 (with
MOD-02/10/11), U-09 (with MOD-01/10).
