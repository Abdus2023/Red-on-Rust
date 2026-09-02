# Red-on-Rust Specification Audit — Authority, Trust-Boundary, and External-Effect Errors

**Audit date:** 2026-09-02 (addendum A: SEC-016…019; addendum B: SEC-020…022; addendum C: SEC-023)
**Audited artifact:** frozen specification set at commit `a013dff` (`Red-on-Rust.md`, 42,312 lines; canonical set `spec/`, `mod/`, `req/`, `term/`, `dep/`)
**Audit class:** authority escalation, trust-boundary errors, external-effect gating — *exclusively*. No conformance, style, or performance findings.

---

## 1. Threat model applied (as instructed)

| Asset | Status |
|---|---|
| LLM output (`LLMOutput`, `PlanProposal`, `PlannerMetadata`) | **untrusted** |
| User input | **untrusted** |
| Red-like source (`Block`) | **untrusted** |
| `Block` | **non-executable** (`Block ≠ ExecutablePlan`) |
| `PlanProposal` | **non-authoritative** |
| `CapRef` | **opaque authority reference** (not authority; kernel is sole authority decider) |
| Evaluator / runtime / kernel / host-policy boundary | **authoritative (TCB)** |
| Live host | partial trust (defense in depth; can refuse, delay, misbehave) |
| Persistence / WAL / journal storage | trusted for *corruption detection* only (see SEC-009 — authenticity is unspecified) |

**Invariants under test:**

- **I1** `LLMOutput ∧ UntrustedInput ↛ ExternalEffect`
- **I2** `ExternalEffect(E) ⇒ ValidatedRequest(E) ∧ Authorized(E,κ,t) ∧ CapabilityWithinCeiling(E) ∧ BudgetAvailable(E) ∧ DeadlineValid(E,t) ∧ HostPolicyOK(E) ∧ Issued(E)`

## 2. Verdict summary

**I1 and I2 do not hold at specification level.** The 16-step gate sequence itself is sound and well-ordered, but the *state surrounding* the gates contains twenty-three specification-level defects through which untrusted input or a partially-trusted host can reach an `ExternalEffect` (or destroy/forge the authority facts the gates depend on): 3 CRITICAL (two complete authority-injection chains exist in conforming implementations; one silent deletion of operative security rules from the normative layer), 5 HIGH, 3 MEDIUM-HIGH, 9 MEDIUM, 2 LOW/MEDIUM, 1 LOW.

| ID | Severity | One-line violation |
|---|---|---|
| SEC-001 | CRITICAL | Effect-receipt **result values are unrestricted** — host/trace can resume any continuation with `Value::Capability` |
| SEC-002 | CRITICAL | Runtime authorization has **no holder-possession binding** — a known CapRef is exercisable by any actor |
| SEC-003 | HIGH | Canonical **decoder mints `Value::Capability` from raw bytes**; unmarshal side of the marshalling boundary is unenforced |
| SEC-004 | HIGH | **Kernel authority state is not durable** — revocation does not survive crash; capability arena absent from snapshot/WAL/recovery |
| SEC-005 | HIGH | The **delegation channel is unimplementable** as frozen (no AST node, no value variant, two fault vocabularies) |
| SEC-006 | MEDIUM-HIGH | **Spawn inherits all parent capabilities** under an attacker-chosen/unfrozen constraint — wholesale copying is the default |
| SEC-007 | MEDIUM | **Staleness predicate contradictory** — `<`-only reading accepts future-tagged proposals |
| SEC-008 | MEDIUM | **CapRef bits leak toward the untrusted planner** (events in `Observation`; `EffectRequest.cap` in the log; `CapabilitySummary` undefined) |
| SEC-009 | MEDIUM | Persistence integrity is **unkeyed SHA-256** — tamper-authenticity absent from the threat model |
| SEC-010 | MEDIUM | **Indeterminate-effect reconciliation protocol unfrozen** — a trusted-but-unspecified channel resolves real-world effects |
| SEC-011 | MEDIUM | **Durable receipt results are not representable** (`result_digest` only) — replay correspondence unimplementable without an unfrozen record |
| SEC-012 | MEDIUM | **Error paths use undeclared fault variants** (X-67 BLOCKING family) — host/replay errors cannot be written without inventing vocabulary |
| SEC-013 | LOW-MEDIUM | **Host/actor isolation is in-process and unfrozen** (isolation ladder never retired) — "Partial" host trust rests on Rust type safety alone |
| SEC-014 | LOW-MEDIUM | **`AdmissibleConstraint` is an unresolved premise** of attenuation — attacker-controlled constraints from untrusted `Block`s |
| SEC-015 | LOW | **Root-authority grant and supervisor channels unfrozen** — no protocol for who mints authority or bounds supervisor host access |
| SEC-016 | HIGH | **I2's own predicates are ill-formed** — `ValidatedRequest(E)` vs `ValidatedPlan(P)` vs the `ValidatedPlan` struct (X-01/X-04); `Authorized` has six incompatible signatures (X-05) |
| SEC-017 | MEDIUM | **Two complete canonical grammars (LE vs BE) coexist in frozen text** — digest identity of receipts/journal/replay is implementation-dependent for a wrong-grammar implementer (X-50/X-54) |
| SEC-018 | HIGH | **`contains_capability` is invoked but never defined** — the R-CORE-07 boundary's sole mechanism has no frozen traversal domain; closure-environment smuggling is undetectable |
| SEC-019 | MEDIUM | **Receiver-side resource asymmetry** — mailboxes unbounded, no recipient reservation at enqueue, no payload-size-proportional cost rule |
| SEC-020 | MEDIUM-HIGH | **Panic-discipline violations on trust-boundary commit paths** — `unwrap()`/`unreachable!()` after "safe due to checks" reasoning; a mid-transition panic breaks effect atomicity and manufactures `Indeterminate` history |
| SEC-021 | MEDIUM | **Live-fault escrow stranding** — no disposition rule for escrow when a `Pending` actor faults without a crash or the host never answers; conservation holds, spendable budget shrinks monotonically |
| SEC-022 | MEDIUM-HIGH | **The trust model is under-frozen where it matters most** — three authoritative boundary modules absent from the trust table (V-11), two divergent frozen tables, and the dependency layer *measures* SC-1/2/3 FAIL: planner recorded as security provider (V-03), production→planner runtime edge, and the R-DUR-02 durability hinge with no legal crate edge (V-10) |
| SEC-023 | CRITICAL | **Normative-layer content substitution: 48 of 148 `spec/01` obligations (mechanically measured, 6/6 sample hand-confirmed) carry a different rule than their stable ID denotes, and the normalization records self-certify each replacement as "Semantic Risk: None"** — no-amplification (CAP-05), the five-assertion denial short-circuit (EFFECT-04), the C-23 escrow fix (EFFECT-05), the 7-step issuance transaction (DUR-02), the receipt ID conjunct, recursive marshal rejection (MARSHAL-01), the amplification/teleportation theorems (ACTOR-08), authority invisibility (KERN-03), the reservation predicates (BUDGET-03), and the authoritative host checks (HOST-01/02) are all absent from the canonical text that every module names as the normative home |

Findings already registered in the repository's own registers (`C-…`, `U-…`, `AMB-…`, `X-…`) are marked; in every such case this audit's contribution is the **security consequence the register omits**, plus the required elevation of grade.

---

## 3. Findings

---

### SEC-001 — Receipt-result injection: `E-Receipt` resumes continuations with unrestricted values

**LOCATION**
- `Red-on-Rust.md` L8762–8769 — v0.3 rule **7. E-Receipt**: premise `R.h = h ∧ R.effect_id = Hash(E)`; conclusion `status ← K[R.result]`
- `Red-on-Rust.md` L23957–24002 — `resume_from_receipt` (14-gate era): `let result_value = match receipt.result { Ok(v) => v, … }; continue_with_value(actor, result_value)`
- `Red-on-Rust.md` L23540–23580, L11023+, L22155+ — two further frozen versions, identical behavior
- `Red-on-Rust.md` L22133–22152 — receipt protocol: "Only then may the result influence the machine" (ID+digest only)
- Canonical restatement: `spec/01` S-12 R-EFFECT-06/07 (validates ID **and** digest — nothing about the result payload)

**VIOLATION**
The receipt-validation rule constrains only *causal identity* (`id`, `digest`). The **result payload `R.result: Result<Value, HostFault>` is injected into the actor's continuation with no value-domain restriction**. In particular nothing forbids `Value::Capability(CapRef)`. The result channel is therefore an **ungated authority inlet into an actor's heap and environment** that never passes: the marshalling boundary (R-CORE-07 / R-MARSHAL-01: "authority never crosses an ordinary message boundary"), delegation (R-MARSHAL-02: kernel `derive` with `DelegatedAuthority ≼ ParentAuthority`), or spawn derivation (R-ACTOR-05). It also violates the module's own claim (`mod/08`): "the chain from untrusted proposal to external effect exists only here, and it is gated end-to-end" — the *return* half of the chain is ungated.

**ATTACK-PATH**
1. Live host (partial trust — "can refuse, delay, or misbehave") returns `EffectReceipt { id, digest_of_pending_effect, result: Ok(Value::Capability(CapRef_of_foreign_actor)) }`. ID and digest match the pending effect, so every frozen validation passes.
2. `resume_from_receipt`/E-Receipt resumes the awaiting continuation with the foreign `CapRef` in scope — the receiving actor now *holds* authority it was never granted, delegated, or spawned with.
3. Because gate 6 authorizes against the **global** kernel arena with no holder check (SEC-002), the actor immediately exercises it: `ExternalEffect` under foreign authority.
4. Variant: a tampered/replayed trace (see SEC-009, SEC-011) delivers the same receipt during recovery/replay — the injection also poisons *recovery* and *differential evidence*, since replayed machines faithfully reproduce the injected authority.
5. Variant: a hostile actor uses the receipt channel to **lander** a capability to a colluding actor via `Send` (as `Value::Capability` it is rejected by `marshal`; as a captured value inside a delegated envelope it is not rechecked) or simply holds it.

**EXPECTED-INVARIANT**
- I1 extension over the receipt channel: `HostResult(v) ⇒ ContainsCapability(v) = false ∧ v ∈ CanonicalDataDomain` — receipts are data, never authority.
- `R-CORE-07` (no raw capability transfer) must hold for **every** value-crossing: messages, receipts, snapshots, replay traces.
- Actor isolation (R-ACTOR-01): authority context of actor `a` changes only via kernel `derive` (attenuate/delegate/spawn).

**REMEDIATION**
1. Freeze a receipt-result admission rule: `resume_from_receipt` must run `contains_capability(R.result)` and fault (`Fault::InvalidReceipt`/new declared variant) on any `Value::Capability`, nested at any depth — the same recursive predicate the marshaller uses.
2. Restrict `R.result` to the canonical *data* domain (the 8-variant codec value set; see SEC-003/U-09) — `Function`/closure values from a host must also be rejected (code injection).
3. State the invariant negatively in `spec/01` S-12 alongside R-EFFECT-06: "a receipt may complete an effect; it may never confer authority."
4. For error results, replace `format!("{:?}", host_fault)` (L23997) with a declared, closed fault mapping — no raw debug-formatted host text in machine values.

**VERIFICATION**
- New mutation-registry entries (additive, per R-TEST-04): **M019** "resume with `Value::Capability` result" and **M020** "resume with closure result" — both must be killed.
- Property test: for every effect class, for arbitrary host results containing nested capabilities (List/Map/Tuple depths ≥ 3), `resume_from_receipt` faults and the actor's `CapabilityContext` is byte-identical before/after.
- Replay/differential: inject capability-bearing receipts in recorded traces; both production and reference must produce `ReplayCorruption`-family faults and identical final digests.
- Conformance tag proposal: `EFFECT-RECEIPT-RESULT-NO-AUTHORITY`.

---

### SEC-002 — No holder-possession binding at the authoritative gate (CapRef forgery ⇒ foreign authority exercise)

**LOCATION**
- `Red-on-Rust.md` L6702–6712 — `CapabilityKernel::authorize(&self, cap: CapRef, effect: &Effect, t: u64)`: resolves `cap` in the **global** `arena`, checks liveness/ancestors/coverage. No actor parameter.
- `Red-on-Rust.md` L9738–9744 — frozen kernel trait: `authorize(cap, effect, now)`; `derive(cap, constraint)`. No holder.
- `Red-on-Rust.md` L23891 — 14-gate `finalize_request` gate 6: `kernel.authorize(capability, &effect, now)` where `capability` is the **frame-resolved value**, not a `CapabilityContext` lookup.
- `Red-on-Rust.md` L10861 — `pub type CapabilityContext = (); // Maps to CapabilityKernel references` (per-actor possession set is literally the unit type in a frozen sketch)
- `Red-on-Rust.md` L11061 — "1. Resolve CapRef (via CapabilityContext)" — comment only; no frozen rule
- `Red-on-Rust.md` L6702 area — `arena: GenerationalArena<AuthorityNode>`, `revocation_set: HashSet<CapRef>` — kernel-global, actor-blind
- Canonical: `spec/01` S-10 R-CAP-06 — `Authorized(A,E,t) ⇔ op ∈ O_A ∧ target ∈ ⟦A_op.S⟧ ∧ A_op.Q(params) ∧ cost ≤ A_op.R ∧ t ∈ A_op.T` — **five conjuncts, none of them possession**
- Contrast: v0.3 formal rules (L8731, L8748) write `Authorized(κ(c), E, t)` with κ the *acting actor's* map — the formal layer assumes per-actor possession; the frozen kernel API and gate code do not implement it. (Unregistered conflict.)

**VIOLATION**
`CapRef = {index: u32, generation: u32}` — small, deterministic, globally allocated counters. Authority exercise at the authoritative boundary is a function of **the bits alone**: any actor whose heap contains a `Value::Capability(c)` can pass gate 5/6/7 for any effect covered by `κ(c)`, because the kernel never checks `c ∈ actor.capabilities`. The only possession barrier is the *static* `S-Invoke` premise `κ_static(e_cap) ⊢ e_eff` (L3924) — and what capability analysis must produce is explicitly undecided (U-22), with κ_static's population protocol unspecified (see SEC-015). "CapRef ≠ authority ownership" (L24905–24911) is asserted as a *marshalling* rationale, but the spec never turns it into a *kernel-side possession rule*.

**ATTACK-PATH**
1. Untrusted side learns CapRef bits — via SEC-008 (leak of `EffectRequest.cap` in events shown to the planner), via SEC-001 (host receipt injection), via SEC-003/SEC-009 (decode/persistence), or by **guessing**: indices are sequential u32 counters and generations are small; golden vectors (R-CANON-11, e.g. `CapRef{5,2}`) document the encoding.
2. LLM embeds `Value::Capability(CapRef{index: k, generation: g})` as a literal inside its proposed `Block` (`Block(pub Vec<Value>)` structurally admits it — L855).
3. If the plan's capability analysis does not reject foreign literals (U-22 undecided; S-Val admits any value with no κ_static premise), the literal reaches the evaluator; `Expr::Request`'s capability subexpression evaluates to the forged CapRef.
4. Gate 5 `Valid(c,t)` and gate 6 `Authorized` pass — the CapRef is live in the *global* arena (it belongs to another actor) and covers the effect.
5. Gates 7–16 pass with the *attacker's* budget. Result: `ExternalEffect` under a victim's authority. `LLMOutput ⇒ ExternalEffect` — **I1 broken** with no host misbehavior required, only one conforming-but-lax compiler reading.

**EXPECTED-INVARIANT**
- `Authorized(E, κ, t)` at the *machine gate* must be defined as: `c ∈ CapabilityContext(actor) ∧ Valid(c,t) ∧ Authorized(κ(c), E, t)` — possession is a conjunct of I2's `Authorized(E,κ,t)`, not a marshalling courtesy.
- `CapabilityWithinCeiling(E)` must be evaluated against the *requesting actor's* derived ceiling, which presupposes possession.
- CapRef opacity toward untrusted observers (this is the mechanism making "opaque authority reference" true rather than nominal).

**REMEDIATION**
1. Freeze the kernel API with an explicit holder: `authorize(holder: ActorId | CapabilityContextToken, cap: CapRef, effect, t)`, or require gate 5 to resolve `cap` **through** `actor.capabilities` (kernel-side or runtime-side possession check — the spec must pick one and make it normative).
2. Make `CapabilityContext` a real frozen type (delete the `= ()` sketch from the operative set or mark it superseded) and require snapshots to carry it (ties into SEC-004).
3. Freeze the compiler obligation: "a `Block` containing a capability literal not bound in the plan's declared capability set is a compilation fault" (extend R-COMPILE-02/R-COMPILE-03; closes the U-22 gap in the security direction).
4. Register the conflict between v0.3's per-actor `κ(c)` and the kernel-substrate global arena (currently unregistered).

**VERIFICATION**
- Mutation **M021** "authorize without possession check" must be registered and killed.
- Amplification test extension (mod/06 already has the harness shape): force a foreign `CapRef` through `Request` — assert `Fault::Capability*`, zero `authorize`-side effects, victim context unchanged.
- Compiler conformance: `Block` with embedded `Value::Capability` literals (own, foreign, garbage-generation) — only own-bound literals compile.
- Exhaustive/property: brute-force CapRef space `{0..2⁸} × {0..2⁴}` from a non-holder actor over all ops — every exercise attempt faults.
- Track B mock-kernel assertion: `authorize` called with exactly the holder's resolution, not a raw frame value.

---

### SEC-003 — Canonical codec mints authority references from bytes; unmarshal side of the marshalling boundary is unenforced

**LOCATION**
- `Red-on-Rust.md` L33158–33191 — frozen 15A `Value` decoder: `TAG_CAPABILITY: u8 = 0x05` arm constructs `Ok(Value::Capability(CapRef { index, generation }))` from raw payload bytes (also standalone `CapRef::TYPE_TAG = 0x30`, L32327–32334, golden vectors L29367, L31196)
- `Red-on-Rust.md` L25685–25696 — frozen marshalling pair: `marshal_value` rejects `contains_capability(v)`; **`unmarshal_value(bytes) = canonical_deserialize(&bytes.0)` with no capability rejection**
- `Red-on-Rust.md` L26008–26030 — second frozen `execute_receive` calling `unmarshal(marshalled, &mut actor.capabilities)?` (registers delegated caps — a *different* function contract; see SEC-005)
- `Red-on-Rust.md` L5987 — design rule: "`CapRef` should not be serializable into a portable authority token. A serialized capability should go through an explicit delegation mechanism."
- Registered as C-14 (MAJOR, open → U-02) — but framed as an *encoding gap*, not a decode-side smuggling hole; the security reading is absent from the register.

**VIOLATION**
The marshalling invariant is enforced **asymmetrically**: only the encode direction (`marshal_value`) rejects capabilities. The decode direction accepts `Value::Capability` as a first-class codec product. Every bytes→value path in the machine therefore *mints* capability references without kernel involvement:
- `Receive` unmarshalling mailbox bytes (bytes are stored in snapshots — L26293–26330 includes `mailbox` — and reconstructed at recovery);
- snapshot/WAL decode at recovery steps 3/7 (L35193–35204);
- any future ingestion of canonical bytes (differential fixtures are explicitly allowed to treat canonical bytes as opaque inputs, 15C.36).
The frozen codec makes the L5987 design rule **unenforceable**: a "portable authority token" is exactly `01 00 00 00 00 0b 05 01 30 …` and the decoder accepts it.

**ATTACK-PATH**
1. Attacker with persistence write access (or a corrupted-then-consistent-looking record; see SEC-009 — checksums are unkeyed and recomputable) edits a snapshot's mailbox payload to contain a capability-bearing `Value`, recomputes the frame checksum and `state_digest` (or simply targets any implementation that stores mailbox bytes verbatim).
2. Recovery decodes the snapshot (step 3), rebuilds the mailbox, and the victim actor's `Receive` unmarshals `Value::Capability(foreign)` into its heap.
3. Gates 5–7 authorize globally (SEC-002) → external effect under foreign authority.
4. No `RecoveryFault` fires anywhere: every framing, checksum, sequence, and causality check passes — the forgery is *syntactically perfect* because the codec defines capability payloads as legal.

**EXPECTED-INVARIANT**
- `CapRef` = opaque authority reference: **only the kernel may introduce a capability into a value context** (construction, derivation, delegation registration). `decode: bytes → Value` must not be a capability-manufacturing oracle.
- Symmetric marshalling law: `CapRef ∉ unmarshal(b)` for any `b` not produced by the delegation protocol — the dual of R-MARSHAL-01's `CapRef ∉ marshal(v)`.
- Persistence layer (trust: Yes) must not be able to increase any actor's authority (R-ACTOR-08: `Authority_after ≼ Authority_before ∪ ExplicitlyDelegatedAuthority` — recovery is not a delegation event).

**REMEDIATION**
1. Split the codec: the *data* codec (messages, results, plan literals) must **reject** discriminant `0x05` and standalone `0x30` on decode (`CanonicalError::InvalidDiscriminant` or a new `CapabilityInData` error); a *separate* kernel-mediated codec path (persistence of kernel state, delegation envelopes) is the only legal producer/consumer of capability payloads.
2. Freeze `unmarshal` to run `contains_capability` on the decoded value regardless of provenance (defense in depth; makes the boundary symmetric).
3. Resolve C-14/U-02 in the direction the design rule already states, and record the *security* rationale in the C-14 row, not just the encoding rationale.
4. Make the two `unmarshal` forms (L25693 vs L26008) one normative contract (see SEC-005).

**VERIFICATION**
- Negative vectors: canonical bytes for `Value::Capability`, nested-at-depth capability payloads, standalone `0x30` envelopes — all must be rejected by the data decoder (add to `vectors/canonical` as normative *negative* fixtures).
- Mutation **M022** "unmarshal accepts capability payload" — must kill.
- Recovery negative test: snapshot with capability-bearing mailbox/heap values ⇒ `RecoveryFault` (this currently *passes* recovery — the test will fail today, which is the point).
- Property: for all bytes `b`, `contains_capability(unmarshal_data(b)) = false ∨ unmarshal_data(b) = Err`.

---

### SEC-004 — Kernel authority state is not durable: revocation and lineage do not survive crash

**LOCATION**
- `Red-on-Rust.md` L26293–26330 — snapshot content list: `logical_time, next_actor_id, next_effect_id, runnable, actors{run state, EvalState, capabilities, heap, budget, mailbox, status}, scheduler state` — **no `CapabilityKernel`, no `AuthorityNode` arena, no lineage, no revocation set/epoch**
- `Red-on-Rust.md` L33898–33932 — `WalRecord` taxonomy: `Event | EffectPrepared | EffectIssued | EffectCompleted | EffectReconciled | SnapshotCommit` — **no capability record kinds**
- `Red-on-Rust.md` L26448–26459 — event-log minimum set: `… CapabilityDerived` (no `CapabilityRevoked`, no `CapabilityGranted`), followed by "**The exact set should be frozen before claiming complete replay**" (still open)
- `Red-on-Rust.md` L35193–35204 (12-step) and L34344–34364 (19-step) — recovery algorithms: reconstruct/validate budget, runnables, journal, digests — **no kernel-state reconstruction, no CapRef-vs-arena revalidation**
- `Red-on-Rust.md` L6695–6699 — kernel internals: `arena: GenerationalArena<AuthorityNode>`, `revocation_set: HashSet<CapRef>` — process-resident only
- Contrast: `spec/01` S-18 R-PERSIST-04 (snapshot must contain "everything needed to continue"); U-02 records the *encoding* of `Authority` as unfrozen but not the *invariant* that it must be durable and revalidated.

**VIOLATION**
Per-actor `capabilities` (CapRef sets) are snapshotted, but the authority DAG they index — including **revocation state** — is not persisted by any frozen artifact, and no recovery step reconstructs or revalidates it. `Valid(c,t) ⇔ Live(c) ∧ t ∈ Lifetime(c) ∧ ∀a ∈ Ancestors(c). Live(a)` (R-CAP-07) is therefore **unreconstructible**: after crash-recovery every implementation must choose between (a) resurrecting authority nodes as live — **revoked capabilities come back to life**; (b) treating them as dead — legitimate authority is destroyed; (c) rebuilding the arena from event replay — impossible for revocation, which has no durable event at all. Any choice silently violates either R-CORE-09 (`Recover(D) ≡ PreCrashMachineState`) or R-CAP-07. This is an authority-escalation-by-crash-oracle: an attacker who can crash the machine (budget-exhaustion and crash injection are in-scope per the harness) can resurrect revoked authority.

**ATTACK-PATH**
1. Authority `c` (or an ancestor) is revoked at logical time `t₁` — kernel mutates `revocation_set` in process memory. Nothing durable records it.
2. Attacker induces a crash (the crash harness itself demonstrates crashes are a first-class input; DoS via budget/fuel exhaustion is trivially reachable from untrusted plans).
3. Recovery loads the snapshot: actor capability contexts contain `c`; the kernel arena is empty/stale.
4. A conforming implementation that reconstructs authority nodes (the only way to make `Valid(c,t)` true for legitimate caps) has no durable fact saying `c` was revoked → `c` is live again.
5. `Request(c, …)` passes gates 5–7 → `ExternalEffect` with authority the machine had explicitly withdrawn. Revocation — the only mechanism that *reduces* authority at runtime — is non-durable, so `derive(A,C) ≼ A` holds pointwise while the revocation lattice silently regresses.

**EXPECTED-INVARIANT**
- `Recover(D) ≡ PreCrashMachineState` must include the authority lattice: `∀c: Valid_recovered(c,t) ⇔ Valid_precrash(c,t)`.
- Monotonicity of revocation across crashes: a revoked capability may never become valid again without a *new explicit grant* through the (currently unfrozen — SEC-015) authority-injection protocol.
- Recovery step 4 ("validate recovered GlobalState invariants") must include: every CapRef in every actor context/heap resolves in the recovered arena, with matching generation.

**REMEDIATION**
1. Extend R-PERSIST-04's snapshot content with the kernel authority image: `AuthorityNode` set (authority payload, parent links), `revocation_set`, generation counters — with a frozen canonical encoding (folds into U-02's scope; the *invariant* must be frozen even where the bytes remain open).
2. Add WAL event kinds `CapabilityGranted / CapabilityDerived / CapabilityRevoked` (derivation is already implied at L26456; revocation is missing entirely) and freeze the event set (close the "exact set should be frozen" gap in the security direction).
3. Add recovery steps: reconstruct kernel arena; replay capability events after snapshot sequence; **reject** any CapRef (in contexts, heaps, frames, mailboxes) that does not resolve with matching generation — `RecoveryFault`, never silent repair (R-RECOV-05).
4. Re-validate post-recovery: `∀ actor a, ∀ c ∈ caps(a): Valid(c, t_recovered)`.

**VERIFICATION**
- Crash-matrix extension: T0–T6 with a revocation committed before the crash point; assert revoked caps stay revoked (`RECOVERY-REVOCATION-DURABLE`).
- Mutation **M023** "recovery resurrects revoked capability" — must kill.
- Negative recovery tests: snapshot referencing dangling/generation-mismatched CapRefs ⇒ `RecoveryFault`.
- Property: random grant/derive/revoke/crash sequences; post-recovery authorization outcomes must equal pre-crash outcomes for every CapRef.

---

### SEC-005 — The sanctioned authority-transfer channel (delegation) is unimplementable as frozen

**LOCATION**
- `Red-on-Rust.md` L12145–12205 — frozen 12-constructor `Expr`: `Value, Var, Let, Seq, If, Call, Lambda, Attenuate, Request, Spawn, Send, Receive` — **no `Delegate`**
- `Red-on-Rust.md` L25980–25986 — frozen delegation sketch: `Expr::Delegate { capability, constraint }` and `Value::DelegatedCapability(CapRef)` (a variant that exists in **no** frozen `Value` domain — machine domain L12283–12310 has 11 variants, none `DelegatedCapability`; canonical codec L33158–33165 has 8, none either)
- `Red-on-Rust.md` L25700 — "delegation is handled as a separate, explicit AST node (`Expr::Delegate`), which invokes `kernel.derive` and wraps the resulting `CapRef` in a specialized `DelegatedCapability` envelope that the marshaller *does* accept"
- `Red-on-Rust.md` L10827–10841 vs L25683–25687 / L25976–25979 — `MarshalledValue` is (a) a private-constructor wrapper around a `Value` ("strictly distinct from internal Values") and (b) raw canonical bytes — two incompatible boundary mechanisms; `MarshalFault` declared twice with disjoint variants (L25978 vs L10840: X-65/C-55 registered)
- `Red-on-Rust.md` L8695–8697 — formal rule: authority transfer requires `delegate(c, C, target_actor)` — an operator absent from the frozen AST and from every frozen `Expr`
- Registered as AMB-11 / U-02 / X-65 — graded as surface/encoding ambiguity; **the security consequence is not registered**

**VIOLATION**
R-MARSHAL-02 makes explicit delegation "the only exception" by which authority crosses an actor boundary — but the exception has no constructible representation: no AST node, no value variant, no codec tag, no marshal fault vocabulary, and two contradictory `MarshalledValue` types (a *type* boundary vs a *checked bytes* boundary — exactly the difference between "unforgeable by construction" and "unforgeable if the check runs"). A conforming implementation *must* invent this surface, and invented authority-transfer surfaces are the historical locus of capability-system failures (envelope forgery, missing revalidation at receive, constraint ignored). Additionally, the receive-side contract ("the recipient's kernel registers the new capability in its local context" — L26008) is only a code comment: no frozen rule says the envelope must be revalidated against the kernel (liveness, lineage, target binding) **at registration time**, which is the moment SEC-002/003 exploitation would otherwise be caught.

**ATTACK-PATH**
1. Implementation invents `Value::DelegatedCapability` as a data variant (the natural reading of L25986).
2. Because it "is a Value", it participates in general value traffic; an attacker crafts one around any CapRef bits (obtained per SEC-008/002) — there is no frozen rule binding envelope validity to a kernel-issued derivation record.
3. `Receive`'s `unmarshal(marshalled, &mut actor.capabilities)` (L26008) registers it; the recipient now holds authority whose `≼ parent` property was never checked at the only moment it could be.
4. Alternatively, an implementation without any delegation surface silently makes *spawn* the only transfer path (SEC-006) — full inheritance becomes the de-facto authority model.

**EXPECTED-INVARIANT**
- R-MARSHAL-02 must be realizable: `Expr::Delegate`, its envelope type, its encoding, its fault set, and its receive-side revalidation rule must all be frozen — otherwise "authority crosses only through the kernel" is unenforceable prose.
- Envelope admission rule: `register(envelope, recipient) ⇒ ∃ kernel derivation record d: envelope.cap = d.child ∧ d.parent ∈ sender.context ∧ DelegatedAuthority ≼ ParentAuthority ∧ recipient = d.target`.

**REMEDIATION**
1. Close U-02's `Expr::Delegate` clause with the security contract, not just the encoding: fields, evaluation order, kernel call, envelope type (kernel-constructed, not a plain `Value` variant), marshal acceptance rule, receive-side revalidation (liveness + lineage + target + generation), and fault taxonomy.
2. Pick one `MarshalledValue` mechanism. If bytes: the boundary is the SEC-003 check (must be frozen symmetric). If a private-constructor wrapper: state that mailbox bytes never exist as a `Value` and that snapshots storing mailboxes must store the *checked* form.
3. Unify `MarshalFault` (X-65) and bind it into the closed fault taxonomy (SEC-012).

**VERIFICATION**
- Track C delegation suite (exists as plan): add the negative cases — forged envelope, envelope for revoked parent, envelope targeted at a different actor, envelope with stale generation — each must fault with **no** change to the recipient's `CapabilityContext` (assert byte-identical context).
- Mutation **M024** "receive-side registration without kernel revalidation" — must kill.
- Cross-implementation differential must compare post-receive `CapabilityContext`s, not just terminal values.

---

### SEC-006 — Spawn default is wholesale capability inheritance; the attenuation constraint is unfrozen and attacker-adjacent

**LOCATION**
- `Red-on-Rust.md` L25631–25637 — frozen `execute_spawn`: `for (name, parent_cap) in parent.capabilities.iter() { child_caps.insert(name, kernel.derive(*parent_cap, &spawn_constraint, t)) }` — **every** parent capability is derived into the child under one constraint
- `Red-on-Rust.md` L12191–12194 — frozen `Expr::Spawn { body, budget: BudgetAllocationSpec }` — **no constraint field**: `spawn_constraint` (parameter at L25630) has no source in the AST
- `Red-on-Rust.md` L8770–8786 — v0.3 rule 9 E-Spawn: `κ_child = attenuated_context(κ_parent, trust_level)` — `trust_level` exists in no frozen type (AMB-04/C-36 registered)
- `Red-on-Rust.md` L25944–25952 — second frozen `execute_spawn` with the same iterate-all pattern
- README "Engineering Rules": "**wholesale capability copying**" is a prohibited shortcut
- U-03 (spawn split policy, open), U-05 (isolation ladder, open)

**VIOLATION**
`derive(A, C)` with constraint `C = ⊤` is the identity: the meet-semantics no-amplification law permits `derive(A,⊤) = A`. The frozen spawn code iterates *all* parent capabilities, and the constraint governing that derivation is **not expressible in the AST** and has no frozen source, default, or validation rule. A conforming implementation may therefore default to `⊤` — every spawned child receives authority *equal* to the parent's entire set. This satisfies `child ≼ parent` pointwise while functionally being the prohibited "wholesale capability copying," at fan-out scale, driven by untrusted plans (`Expr::Spawn` is authored by the LLM). The static budget rule (S-Spawn) bounds child *budget*, never child *authority*. `BudgetAllocationSpec` validation is likewise unstated (U-03: "if the parent chooses, a malicious parent could starve the child" — the inverse, a child duplicating full authority, is unregistered).

**ATTACK-PATH**
1. Untrusted plan contains `Spawn` nodes (budget-bounded, so cheap relative to the payoff).
2. With the constraint source unspecified, the implementation default (`⊤` or "copy context") grants each child the parent's full capability set.
3. Attacker spawns N children; revocation of a leak in one actor now requires revoking N+1 derived trees — and per SEC-004, revocation is non-durable anyway.
4. Authority containment (R-ACTOR-08) degrades from "derived, attenuated capabilities only" to "cloned capability sets": any single compromised child exercises the parent's full authority ceiling; `CapabilityWithinCeiling` is trivially satisfied at the *parent's* ceiling for all descendants.

**EXPECTED-INVARIANT**
- R-ACTOR-05 as written ("child receives **explicitly derived (attenuated) capabilities only** — wholesale copying/cloning forbidden") must be operationalized: spawn derivation must be **strictly** attenuating or the set of transferred capabilities must be explicitly enumerated in the plan (and statically checked).
- Engineering rule "no wholesale capability copying" must bind the default case, not only the explicit-clone case.

**REMEDIATION**
1. Freeze the spawn authority rule: either (a) `Expr::Spawn` carries an explicit capability manifest + constraint, checked by the compiler against κ_static; or (b) spawn transfers **no** capabilities by default and delegation (SEC-005) is the only transfer path. Ambiguity here is not implementable safely.
2. Resolve the `trust_level` phantom (AMB-04) by retraction or definition.
3. Freeze `BudgetAllocationSpec::validate_and_escrow` bounds (U-03): max child share, min parent retention, fault on violation.
4. State the security theorem explicitly: `Authority(child) ≺ Authority(parent)` for spawn (strict), reserving `≼` for delegation.

**VERIFICATION**
- Property: after any `Spawn`, `Authority(child) ≼ Authority(parent)` **and** (under remediation a) `Authority(child) ≼ manifest` — assert the manifest bound, not just the parent bound.
- Amplification/teleportation tests (mod/06) extended: spawn fan-out of ≥ 100 children; assert aggregate exercisable authority per operation-class is bounded by the parent's (no multiplicative growth of the *set*, and strict reduction under remediation).
- Mutation **M025** "spawn clones parent context unattenuated" — must kill.

---

### SEC-007 — Staleness predicate is contradictory; the `<`-only reading accepts future-tagged proposals

**LOCATION**
- `Red-on-Rust.md` L27208–27212 — "the compiler/runtime verifies `proposal.observation_sequence = current_planning_epoch` … or rejects it as stale" (**equality**)
- `Red-on-Rust.md` L27918, L28373, L28517 — conformance/outer-loop text: "a `PlanProposal` with `observation_sequence < current_sequence` is rejected with `Fault::StalePlan`" (**strictly-less** — says nothing about `>`)
- Registered C-38 / U-13, graded **MINOR**; canonical `spec/01` per C-38: "reject when `< current`"

**VIOLATION**
Under the canonical `<`-only reading, a proposal tagged with a **future** `observation_sequence` is not stale and must be accepted. The causal binding "a proposal is causally bound to the machine state it was generated from" (L27205) is then broken in the forward direction: an untrusted planner can submit proposals pre-staged for epochs that have not yet occurred. This breaks the planning-epoch trust boundary (the mechanism that makes `PlanProposal` non-authoritative *and non-predictive*), and it breaks end-to-end replay equivalence (R-PLANNER-05(3)) whenever live and replayed machines disagree on which proposals were accepted at which epoch.

**ATTACK-PATH**
1. Untrusted planner submits `PlanProposal { observation_sequence: S10⁹, block }` while the machine is at S100.
2. A `<`-conforming implementation accepts it (not `< current`).
3. The plan compiles and executes against state it was never entitled to observe; conversely the planner can hoard accepted-but-future plans, defeating the observe→propose→validate cycle and poisoning `PlannerAccepted` replay records (a future-tagged record cannot be replayed at its recorded epoch without divergence).
4. Determinism evidence (live ≡ replay byte-equality) fails or — worse — is "fixed" by weakening the replay check, laundering the boundary break into the verification stack.

**EXPECTED-INVARIANT**
`AcceptProposal(p) ⇔ p.observation_sequence = current_planning_epoch` (equality — the L27210 form), i.e. `≠ current ⇒ StalePlan ∧ zero state mutation`. The machine-epoch check is the *only* planner-boundary check; it must be exact in both directions.

**REMEDIATION**
1. Freeze equality as the predicate; correct L27918/L28373/L28517 conformance text to `≠`.
2. Re-grade C-38 from MINOR to security-relevant: the two phrasings are not "two phrasings of one check" — they define different acceptance sets.
3. Add the future-tagged case to R-PLANNER-05(2) as a mandatory rejection test.

**VERIFICATION**
- Conformance: submit proposals with `obs_seq ∈ {current−1, current, current+1, current+10⁹}` — accept only `current`; assert zero state mutation on both rejections.
- Mutation **M026** "accept future-tagged proposal" — must kill.
- Replay: a session containing a future-tagged proposal must replay identically after the fix (byte-equal `GlobalState`/`EventLog`).

---

### SEC-008 — Raw CapRef bits leak toward the untrusted planner (observations and event log)

**LOCATION**
- `Red-on-Rust.md` L27151–27163 — `Observation` handed to the planner contains `events: Vec<GlobalEvent>` and `available_capabilities: CapabilitySummary`
- `Red-on-Rust.md` — `CapabilitySummary` occurs **exactly once** in the entire corpus (L27162): never defined (unregistered)
- `Red-on-Rust.md` L9314–9317, L10322–10325, L10806–10809, L1447–1452 — four frozen `EffectRequest` declarations carry `pub cap: CapRef` (later forms L23129/L23282/L23758 drop it — an unregistered shape conflict)
- `Red-on-Rust.md` L10912–10915 — frozen `LogEntry::EffectIssued { id, digest, request: EffectRequest }` — the full request (capability included, in the cap-bearing shape) is appended to the event log that observations (and the supervisor/debugger, L1113) read
- `Red-on-Rust.md` L8740–8746 — v0.3 rule 5 logs `EffectIssued(h, Hash(E), E)` (no cap — the later/canonical shape; the conflict with the cap-bearing shapes is unregistered)
- `Red-on-Rust.md` L127 — early rule: "unrestricted reflection is a security leak (an agent could inspect and exfiltrate its own capability tokens)" — the leak the observation channel now institutionalizes

**VIOLATION**
`CapRef` is specified as an *opaque authority reference* whose bits must not confer anything (L24905: "CapRef ≠ authority ownership"). But nothing freezes **what the untrusted side may observe**, and the frozen surfaces drip raw references: an undefined `CapabilitySummary` (free to enumerate CapRefs), `Observation.events` over a `GlobalEvent` set that is itself unfrozen (L26459), and an `EffectIssued` log shape that embeds `EffectRequest.cap`. Combined with SEC-002 (no possession check at exercise time), observing the bits is *sufficient* to exercise the authority: opacity is the only thing between the planner and foreign authority, and the spec leaks it by default.

**ATTACK-PATH**
1. Planner receives `Observation` for epoch S_n containing events (incl. `EffectIssued` entries carrying `cap`) and/or a `CapabilitySummary` that lists CapRefs.
2. LLM copies a live victim CapRef into its next `Block` as a `Value::Capability` literal (encoding is public: golden vectors).
3. With a compiler reading that admits foreign literals (U-22 undecided) and gate 6's global resolution (SEC-002), the plan exercises the victim's authority.
4. No host misbehavior, no storage tampering: purely untrusted-input-driven. `LLMOutput ⇒ ExternalEffect`.

**EXPECTED-INVARIANT**
- Capability-secrecy/tippet-model premise: knowledge of CapRef bits must never suffice to exercise authority (owned by SEC-002's remediation), **and** the untrusted observation channel must be capability-opaque by construction: `Observation` carries capability *summaries* (counts, classes, ceilings) — never references.
- `LLMOutput ∈ Data` must have its dual: `Capability ∉ Observables(LLM)`.

**REMEDIATION**
1. Freeze `CapabilitySummary` as a non-referential projection (e.g., per-operation-class ceilings and counts) — define it; it is currently a phantom type.
2. Freeze the `GlobalEvent`/`LogEntry` shape (L26459's own demand) with `EffectIssued` carrying `{id, actor, digest}` only — retract the `EffectRequest{cap}`-in-log shape (align with the v0.3 rule-5 shape).
3. Freeze an observation projection rule: events visible to the planner are filtered/redacted; capability references never cross to the untrusted side.
4. Register the `EffectRequest.cap` conflict (L23758 vs L8754).

**VERIFICATION**
- Property: for every machine state and observation emission, `contains_capability(Observation) = false` (recursive, incl. events).
- Conformance: planner-facing observations over effect-heavy traces assert no `0x30`/`0x05` payloads appear in their canonical encoding.
- Mutation **M027** "observation includes CapRef" — must kill.

---

### SEC-009 — Persistence integrity is unkeyed: corruption detection without tamper authenticity

**LOCATION**
- `Red-on-Rust.md` L33802–33830 — `WalFrame.checksum = SHA-256(sequence ‖ kind ‖ payload_length ‖ payload)`; nine rejection classes are all *consistency* checks
- `Red-on-Rust.md` L26303–26309 / R-PERSIST-05 — `state_digest = SHA-256(canonical_bytes)`, same property
- `Red-on-Rust.md` L35196–35208 — strict no-repair rule covers "gaps; checksums; budget inconsistencies; …" — i.e., detectable *inconsistency*, not consistent forgery
- Trust table: Persistence = Yes; no statement anywhere of the storage-channel threat model (unregistered)

**VIOLATION**
Every integrity mechanism in the persistence layer is an unkeyed hash over attacker-writable data. An attacker with write access to the persistence medium can construct **fully consistent** forged records (recompute checksums, sequences, and digests) — snapshots that mint authority (per SEC-003/004), WAL histories that never happened, `EffectCompleted` records for effects the host never performed, and `PlannerAccepted` records for proposals the LLM never made. The spec's no-silent-repair and gap-rejection invariants are all satisfied by the forgery; nothing detects it. The threat model never states whether persistence storage is assumed trustworthy-writable; given the thesis ("the machine is the security boundary"), an unauthenticated durable substrate is a boundary hole.

**ATTACK-PATH**
1. Attacker (or compromised host — partial trust — with filesystem reach) rewrites a WAL segment: appends `EffectCompleted` with a chosen `result_digest`, or better, crafts a snapshot whose actor heaps contain `Value::Capability` payloads (SEC-003 makes them legal bytes; SEC-004 leaves the arena un-recoverable so nothing contradicts them).
2. Recompute frame checksums and the snapshot `state_digest`; sequences remain contiguous.
3. Recovery accepts everything: framing ✓, checksum ✓, continuity ✓, journal causality ✓ (forged-but-well-ordered), budget conservation ✓ (attacker balanced it).
4. Machine resumes with injected authority / invented history; differential and reference recovery (which consume `D` as ground truth) **ratify** the forgery — the verification architecture itself is turned into a laundering device.

**EXPECTED-INVARIANT**
- `Committed(D) ⇒ IntegrityVerified(D)` (REQ-PERSIST-023) is only a corruption statement. Needed: `Durable(D) ⇒ Authentic(D)` — provenance from the machine's own key material (or an explicitly frozen assumption "persistence medium is non-adversarial", recorded in the trust table as such).
- External-effect evidence chain (`Prepared → Issued → Completed → Reconciled`) must be unforgeable, not merely well-ordered, because it is the *only* admissible evidence about the external world (R-DUR-04).

**REMEDIATION**
1. Decide and freeze the storage threat model. If storage may be adversarial: key the WAL/snapshot chain (MAC or signature over the sequence-linked frame chain — the strictly-monotonic sequence already forms a natural chain; the snapshot commit record signs the state digest and the last WAL sequence).
2. At minimum: chain the checksums (`checksum_n = H(checksum_{n−1} ‖ frame_n)`) so truncation/rewrite of any prefix breaks every later frame — cheap, keyless rewinding-resistance for accidental and naive attacks — and document that a keyless scheme does not authenticate.
3. Add the trust-table row: "Persistence medium: trusted-writable / adversarial" with the chosen consequence.

**VERIFICATION**
- Negative recovery tests upgraded: *consistently forged* records (recomputed checksums) — under a keyed scheme these must yield `RecoveryFault`; under a keyless scheme this test documents the accepted risk explicitly.
- Crash harness: tamper-at-every-T-point matrix (not just truncation/corruption).
- If keyed: key-management conformance (recovery rejects records from a different machine instance/key epoch).

---

### SEC-010 — Indeterminate-effect reconciliation is a trusted-but-unfrozen channel that resolves real-world effects

**LOCATION**
- `Red-on-Rust.md` L26249–26262 — `ReconciliationOutcome` (3 variants, L26593–26597) and "an authoritative host reconciliation protocol establishes its outcome"
- `Red-on-Rust.md` L26593–26597 — the declared set itself: `ReconciliationOutcome { Completed(EffectReceipt), NotExecuted, Indeterminate }` — `NotExecuted` **is** a declared durable resolution, and `Completed` embeds a full `EffectReceipt` (result values included)
- `Red-on-Rust.md` L27742 — `Issued`-without-`Completed` "is marked `Indeterminate` and handed to the supervisor's reconciliation policy"
- `Red-on-Rust.md` L26799–26842 — Supervisor owns "effect reconciliation" and itself holds `host: Box<dyn HostExecutor>` (L26807–26812)
- U-15 (outcome variants' "admissibility per effect class remains open"), U-06 (class rules open); MOD-12: "Reconciliation policy sketches (supervisor behavior) are outside the frozen machine core; only the record contract is frozen"

**VIOLATION**
Reconciliation is the **only** exit from `Indeterminate`, releases `complete_max` escrow (R-DUR-05), and writes durable `EffectReconciled` records — i.e., it produces authoritative statements about whether an `ExternalEffect` happened. Yet its protocol, authorization rules, and outcome admissibility are all unfrozen and live in a trusted component above the machine. Aggravating this: the frozen variant set **already contains `NotExecuted`** — the durable resolution the machine side is forbidden to infer — and `Completed(EffectReceipt)` embeds full receipt result values (which no admission rule constrains; SEC-001/011). The 7-conjunct chain (I2) is not stated to apply to reconciliation-driven actions (e.g., compensating effects, retries): nothing forbids a supervisor implementation from re-invoking the host for an indeterminate effect without re-running gates 5–14, or from resolving `Indeterminate → NotExecuted` on its own policy.

**ATTACK-PATH**
1. Untrusted plan issues an irreversible effect (e.g., `NetSend`); host executes; crash lands at T3 (`Issued`, no durable completion).
2. Recovery classifies `Indeterminate`; control passes to unfrozen supervisor policy.
3. A "helpful" policy retries the effect (double-spend) or infers not-executed and releases escrow (violating `Issued ∧ ¬Completed ⇒ Indeterminate` in spirit — the machine-side rule holds, but the *resolution* records `NotExecuted` semantics via an open outcome variant).
4. Escrow release and any compensating host action occur outside every frozen gate; the effect journal now contains machine-certified history that diverges from the real world — precisely the "lying about the world" failure MOD-11 exists to prevent.

**EXPECTED-INVARIANT**
- I2 must hold for **every** host invocation path, including supervisor/reconciliation ones: `Reconcile(E) ⇒ Issued(E) ∧ outcome ∈ AdmissibleOutcomes(class(E))`, and any compensating/retry effect is itself a full `Request` through gates 1–16.
- R-DUR-04's spirit: no component, trusted or not, may resolve an indeterminate effect without an authoritative, frozen admissibility rule.

**REMEDIATION**
1. Freeze the reconciliation protocol: outcome variants per effect class (closes U-06/U-15), the rule that reconciliation **never re-executes** an effect (idempotent query at most), and that compensating actions are ordinary gated requests.
2. Freeze the supervisor contract: it may allocate lifecycle decisions, not effects; `Supervisor.host` must be reachable only through the issuance boundary (or removed from the struct).
3. Restructure `ReconciliationOutcome`: `NotExecuted` must be removable or gated behind the (to-be-frozen) authoritative host-reconciliation evidence rule — as declared, it is a durable `NotExecuted` factory one unfrozen policy away from the R-DUR-04 violation; `Completed(EffectReceipt)` must inherit the SEC-001 result-admission rule and SEC-011's digest verification.

**VERIFICATION**
- Crash-matrix rows T2/T3/T4 with each declared outcome; assert escrow moves only per the frozen admissibility table.
- Mutation **M028** "reconciliation resolves Indeterminate as NotExecuted / releases escrow without admissible outcome" — must kill.
- Negative supervisor tests: attempt direct `host.execute` from supervisor path; assert `PanicHost`-style boundary enforcement.

---

### SEC-011 — Durable receipt results are not representable: replay correspondence vs. `result_digest`-only records

**LOCATION**
- `Red-on-Rust.md` L33917–33923 / L35131 — `WalRecord::EffectCompleted { id, digest, result_digest }` — digest only, never the result value
- `Red-on-Rust.md` L35220–35230 — frozen `ReplayHost::execute` returns `receipt.clone()` from `self.trace` — a full `EffectReceipt { …, result: Result<Value, HostFault> }`
- `Red-on-Rust.md` L26448–26459 — `GlobalEvent` set unfrozen; no frozen record carries result values (the in-memory `LogEntry::EffectCompleted{result}` at L10915 is process-resident)
- R-HOST-03/04 — ordered replay validating ID+digest per entry, same final configuration

**VIOLATION**
Replay requires per-step **receipt equality** (IDs *and* receipts — MOD-09 R-HOST-04), and `resume_from_receipt` needs the result `Value`; but the durable taxonomy stores only `result_digest`. Either the durable substrate cannot feed the `ReplayHost` (replay correspondence unimplementable; recovery of T5 "reconstruct completed effect; resume continuation" cannot resume with the recorded result), or implementations must add an unfrozen record kind carrying full result values — which is exactly the channel SEC-001 restricts and SEC-003 must police. The gap also forces `Value` results into durability scope, dragging the unresolved machine-vs-canonical `Value` collision (U-09) onto the replay-critical path.

**ATTACK-PATH** (integrity variant)
An implementation stores full result values in an ad-hoc WAL record (the only way to meet R-HOST-04). That record has no frozen validation contract: capability-bearing "results" (SEC-001) recorded there replay into actor heaps forever; a tampered result with a *correct* digest-pair (id, effect_digest still match; result_digest is not re-checked by any frozen rule at replay time — R-HOST-03 validates ID and effect digest only) silently alters resumed values, i.e., machine state after recovery is attacker-influenced with zero detectable inconsistency.

**EXPECTED-INVARIANT**
- Replay correspondence must be *implementable from frozen records*: either results are durably representable under a frozen contract that includes `ResultDigest(result_value)` verification at replay, or replay must be re-specified over digests only.
- Whatever record carries result values must enforce the SEC-001 admission rule (no capabilities, data-domain only).

**REMEDIATION**
1. Freeze the durable receipt: `EffectCompleted { id, digest, result_digest, result: CanonicalData }` with a **normative replay check** `ResultDigest(result) = result_digest` before the receipt may resume anything (extends R-EFFECT-06 with a third identity conjunct).
2. Scope `result` to the canonical data domain (SEC-003).
3. Alternatively, re-specify R-HOST-04 to digest-level equality and state that resumed values are reconstructed, not recorded — but then T5 resumption must be re-derived.

**VERIFICATION**
- Replay property: tamper `result` while keeping `result_digest` ⇒ `ReplayCorruption` (this kills the integrity variant above).
- Mutation **M029** "replay skips result-digest verification" — must kill.
- Crash T5 row: recovered actor's resumed value equals pre-crash value byte-exactly.

---

### SEC-012 — Error paths use undeclared fault variants; host/replay errors are unwritable without inventing vocabulary (X-67 family)

**LOCATION**
- `Red-on-Rust.md` L10818–10821 — the only `pub enum HostFault { IoError(String), PolicyViolation(String) }` ("neither of which is ever used" — term/ X-67)
- `Red-on-Rust.md` L35224–35228 — frozen `ReplayHost` uses `HostFault::ReplayTraceExhausted`, `HostFault::ReplayCorruption` — undeclared; six of eight undeclared paths sit on the frozen replay path (C-57, **BLOCKING**, U-14)
- `Red-on-Rust.md` L26871 — `Fault::Host(...)` elided payload; `StalePlan` in no `pub enum Fault` (C-54/X-64); `MarshalFault` twice with disjoint variants (L25978 vs L10840, X-65); `CapabilityError::Invalid` used vs `InvalidConstraint` declared (C-56/X-66)
- `Red-on-Rust.md` L23997 — `Value::String(format!("{:?}", e))`: host-fault debug text injected into machine values

**VIOLATION**
Error paths are where trust boundaries are crossed under worst conditions, and they are the one place the frozen spec forbids implementation freedom ("STOP-and-report", R-SCOPE-03; no invented variants). Nevertheless the frozen text uses fault variants that no declaration provides. Consequences: (a) implementations *must* invent error types on the security-critical replay/host boundary, so cross-implementation error behavior — including whether a host error aborts, retries, or resumes an actor — is unconstrained; (b) differential fault comparison (R-REF-05 compares faults) is ill-defined, so error-path divergences can hide authority-relevant differences (resume-vs-fault on receipt mismatch is exactly the SEC-001 behavior boundary); (c) `Debug`-formatted host text flows into semantic values, an untrusted-string channel with no canonical contract (host strings are external input).

**ATTACK-PATH**
Divergence-laundering: implementation A maps `ReplayCorruption`-class failures to a resumable fault; implementation B faults the actor. Both are "conforming" (the variant is undeclared). A tampered trace (SEC-009/011) replays cleanly on A — resuming continuations with attacker-chosen receipts — while the differential harness records a mere fault-label mismatch, adjudicated (R-TEST-09) as "harness defect" and papered over. The error-path ambiguity becomes the cover for the authority injection.

**EXPECTED-INVARIANT**
- Closed, declared fault surface on every trust-boundary crossing (host→machine, storage→recovery, planner→machine), so that `HostInvoked ⇒ DurableIssued` violations and receipt mismatches have exactly one observable semantics.
- No untrusted text enters machine values except through declared, canonical data constructors.

**REMEDIATION**
1. Resolve U-08/U-14 (BLOCKING) by freezing the full fault/error enumeration, including the six undeclared replay-path variants and the `MarshalFault` unification.
2. Mandate: host faults map to a closed machine-fault set; `format!("{:?}")` of external errors is prohibited in machine-visible values (opaque error codes or digests only).
3. Pin the resume-vs-fault behavior per fault variant (which faults resume continuations, which park actors) — this is security-critical, not cosmetic.

**VERIFICATION**
- Fault-coverage metric (R-CALC-06) must fail on any undeclared variant — add a lint/test that greps the crate for variant uses against the frozen enumeration (the repo's own `term/_check.py` discipline applied to code).
- Differential fault matrix: for each fault variant, both implementations must agree on {actor status, budget effect, continuation disposition, event-log delta} — not just the label.

---

### SEC-013 — Host and actors share one process; "Partial" host trust has no structural enforcement (isolation ladder never retired)

**LOCATION**
- `Red-on-Rust.md` L1292–1313 — isolation ladder (in-process / WASM / OS-process) with capability-gated isolation-level selection ("an untrusted agent should not be able to spawn a child with weaker isolation than its own")
- `Red-on-Rust.md` L1297 — "The `MachineState` and the `LiveHost` run in the same Rust process. … FFI calls are direct function invocations."
- Every later frozen phase: in-process actors; `Expr::Spawn` has no isolation field; the ladder is never retracted (C-19, U-05 registered as a *surface* question)
- `mod/09` SECURITY-BOUNDARY: the host "cannot create authority …, cannot fabricate receipts that resume continuations …, cannot rewrite history" — claims exceeding the frozen mechanism

**VIOLATION**
The trust table assigns the live host "Partial" and MOD-09 asserts behavioral limits on it, but the frozen architecture gives a misbehaving host **memory adjacency** to the entire machine: same process, same address space, only Rust's type system between a compromised host effect handler and `GlobalState`, the kernel arena, and the revocation set. "Defense in depth" (machine gate 11 ⊂ host check) is depth of *checks*, not of *isolation*. The early design's own answer (the ladder) is neither implemented nor retired — U-05 leaves the security posture undefined. All host-mediated findings (SEC-001, SEC-009) currently have zero structural backstop.

**ATTACK-PATH**
A single compromised host operation (e.g., a native library behind an effect) gains arbitrary read/write within the process: read the kernel arena (full authority disclosure — defeats CapRef opacity), flip `revocation_set` entries, or corrupt a pending actor's continuation. No gate is involved; the gates run *before* the host is invoked. This converts every "Partial trust" assumption into "full trust in every byte of host code and its transitive dependencies."

**EXPECTED-INVARIANT**
- The trust table's "Partial" must be *enforced by structure*: the host boundary should be a process (or equivalent isolation domain) boundary, with effects and receipts crossing as canonical bytes only — which is what the "Effects must be pure data, never code" rule (L1142) already implies for the *payload*, but not for the *executor*.
- At minimum, the spec must freeze the in-process choice *explicitly* and record the residual risk ("host compromise = machine compromise") in the trust model instead of implying behavioral containment.

**REMEDIATION**
1. Resolve U-05 by explicit addendum: either (a) retire the ladder and record the in-process residual risk as accepted (trust table footnote), or (b) freeze the out-of-process host adapter (effects/receipts over the canonical wire format, which already exists) for any deployment where host code is not fully trusted.
2. If (b): forbid in-process `Box<dyn HostExecutor>` in production configurations; keep it for tests (PanicHost/MockKernel are testkit doubles by definition).

**VERIFICATION**
- Dependency/visibility review item: production `ror-host` must not link against `ror-runtime` internals beyond the adapter trait (spec/07 §6 already hints this; make it a hard gate).
- If out-of-process mode is frozen: differential suite over both host modes (in-process double vs. byte-protocol host) must agree.

---

### SEC-014 — `AdmissibleConstraint` is an unresolved premise guarding kernel derivation of attacker-supplied constraints

**LOCATION**
- `Red-on-Rust.md` L8717–8723 — v0.3 rules 3/4 (`E-Attenuate`/`E-AttenuateDenied`): premise `AdmissibleConstraint(C_req)` — predicate never defined; occurrences L7858/L8717/L10068/L10171; the trait at L10171 is referenced nowhere else (AMB-12/U-09 registered, unresolved)
- `Red-on-Rust.md` L12177–12181 — `Expr::Attenuate { capability, constraint }` and `Expr::Spawn`'s budget spec: **`Constraint` and `BudgetAllocationSpec` are authored inside untrusted `Block`s**
- `Red-on-Rust.md` L10171 — `AdmissibleConstraint` trait declared once, orphaned
- MOD-03 INVARIANTS: "Constraint well-formedness is a *premise* of attenuation transitions — status formally open (AMB-12)"

**VIOLATION**
Untrusted `Block` data directly parameterizes `kernel.derive(parent, constraint)` (attenuation, spawn, and — per SEC-005 — delegation). The well-formedness gate on that parameter is a named-but-undefined premise. The meet-semantics law (`derive(A,C) ≼ A`) bounds *amplification*, not *attenuation fidelity*: for an inadmissible/ill-formed constraint, an implementation that defaults to ⊤ yields `derive(A, C_garbage) = A` — the requested restriction silently does nothing. Since constraints are how untrusted programs promise to self-restrict before handing authority onward (spawn/delegate), an undefined admissibility predicate makes the *narrowing contract* unenforceable exactly where the input is adversarial. Error-side behavior is equally open: `derive` fallback uses `CapabilityError::Invalid` vs declared `InvalidConstraint` (C-56) — the fault path is also undefined.

**ATTACK-PATH**
1. LLM proposes `Attenuate`/`Spawn`/`Delegate` with a constraint that is syntactically encodable but semantically inadmissible (empty operation set with vacuous `Q`, scope outside parent's interpretation, unsatisfiable lifetime interval — the domains are themselves open per U-21).
2. A conforming implementation cannot evaluate `AdmissibleConstraint` (undefined), so it accepts-and-ignores (⊤-default) or panics (crash oracle) or rejects (three different observable behaviors — also a differential fault bug per SEC-012).
3. Under accept-and-ignore, every downstream consumer (child actor, delegate recipient) holds the **unattenuated** parent authority while the event log records a derivation that auditors read as narrowed — authority laundering with a clean audit trail.

**EXPECTED-INVARIANT**
`derive(A,C)` with `C` inadmissible must be a **fault**, never identity: `¬AdmissibleConstraint(C) ⇒ ¬∃c'. derive(A,C)=c'`. Constraint admissibility must be decidable and frozen before any derivation path is implemented, because the inputs are attacker-authored.

**REMEDIATION**
1. Define `AdmissibleConstraint` (close AMB-12/U-09): decidable well-formedness per semantic domain (O/S/Q/R/T), plus the rule above.
2. Compiler obligation: constraints are validated at compile time (extend R-COMPILE-02/03) — reject inadmissible constraints in `Block`s before they reach the kernel.
3. Fix the `Invalid`/`InvalidConstraint` variant drift (C-56) as part of the SEC-012 enumeration.

**VERIFICATION**
- Property: `derive` with an inadmissible constraint never returns a CapRef (fault-only), across the full generated constraint space (including the U-21 boundary cases once domains are frozen).
- Mutation **M030** "inadmissible constraint treated as ⊤" — must kill.
- Compiler negative suite: `Block`s containing each inadmissible constraint class fail compilation with a declared fault.

---

### SEC-015 — Root-authority minting and supervisor-side host access are outside every frozen protocol

**LOCATION**
- `Red-on-Rust.md` L3118–3160 — `Authority(P_{t+1}) = AuthorizedCompilationContext(P_{t+1})`: fresh authority may enter at compilation "from an enclosing supervisor, policy engine, or fresh delegation event" — the grant channel itself is specified nowhere
- `Red-on-Rust.md` L263 — "the host creates an arena, allocates the initial κ (ambient capabilities), and injects the agent's prompt" (early design; no frozen successor)
- `Red-on-Rust.md` L26807–26812 — `Supervisor { machine, persistence, host: Box<dyn HostExecutor>, policy: Box<dyn HostPolicy> }`
- `spec/07` §6 — crate edge `ror-agent → ror-core, ror-compiler, ror-runtime`: the crate hosting **untrusted planner I/O** also links the compiler (ExecutablePlan construction) and the runtime directly
- MOD-13: the eight prohibitions are "technically enforced at the target module's API surface" — negative contract, no structural separation

**VIOLATION**
The kernel is declared "the only component that can construct" authority (R-KERN-01/03), but no frozen protocol says **who may call construction, with what policy, under what ceiling, or how a grant is recorded**. Symmetrically, the supervisor holds a host executor handle with no frozen rule restricting its use to issued effects; and the untrusted planner integration lives in the same crate (`ror-agent`) as the trusted supervisor with direct edges to compiler and runtime — the "planner cannot invoke the host / bypass compilation / allocate actors" prohibitions are enforced by code discipline inside one crate, not by any boundary the architecture would recognize. The trust boundary is thus drawn *through the middle of a crate*, which the trust table cannot express.

**ATTACK-PATH**
(Compromise-of-integration path — relevant because the planner channel is network-adjacent and processes LLM output.) A flaw in the planner-facing code inside `ror-agent` (prompt/observation serialization, streaming parse) runs with full in-process access: it can construct `ExecutablePlan`s via `ror-compiler` (bypassing nothing the compiler checks, but skipping proposal staleness and `PlannerAccepted` recording), allocate actors via `ror-runtime`, and call `host.execute` directly — `HostInvoked(E)` without `DurableIssued(E)`, violating R-DUR-01 with no gate ever seeing the request. Every "eight prohibitions" test (R-PLANNER-05) passes, because the machine-side boundary is intact; the breach is on the trusted side of an unstructured boundary.

**EXPECTED-INVARIANT**
- Authority enters the machine **only** through a frozen, auditable grant protocol: `Grant(source, authority, ceiling, t) ⇒ CapabilityGranted durable record ∧ authority ≼ deployment ceiling`.
- Supervisor/host: `Supervisor` may not invoke `HostExecutor` except with a durably-issued `EffectRequest` (the same precondition the machine obeys — R-HOST-02 "host performs only issued effects" must bind *all* callers).
- Untrusted-facing integration code must be structurally separated (crate or process) from supervisor/runtime handles.

**REMEDIATION**
1. Freeze the root-grant protocol (who, policy, ceiling, durable record — ties into SEC-004's `CapabilityGranted` event).
2. Remove `host` from the `Supervisor` struct, or type it as an issued-effect-only handle; state R-HOST-02 as binding every host caller.
3. Split `ror-agent`: `ror-planner-io` (untrusted side; no runtime/compiler edges, emits `PlanProposal` data only) vs. supervisor code in `ror-runtime`/`ror-agent-core`; add the edge to `dep/`'s crate DAG review.

**VERIFICATION**
- Dependency-graph review (R-REPO-03) gains a rule: no crate containing LLM/planner I/O may depend on `ror-compiler`/`ror-runtime`.
- Conformance: `PanicHost` wraps **all** host handles including the supervisor's (assert: no path to `execute` without a durable `Issued` record).
- Audit test: every live root authority in a recovered arena traces to a durable `CapabilityGranted` record.

---

### SEC-016 — The central theorem's predicates are ill-formed: `ValidatedRequest`/`ValidatedPlan` and six `Authorized` signatures

**LOCATION**
- `Red-on-Rust.md` L23694 — frozen central theorem: `ExternalEffect(E) ⇒ ValidatedRequest(E) ∧ Authorized(E,κ,t) ∧ …` (**request-time** validation; the form used by this audit's mandate)
- `Red-on-Rust.md` L41337–41351 (and README, and `spec/01` L24 R-CORE-02) — the same theorem with `ValidatedPlan(P)` (**plan-time** validation)
- `Red-on-Rust.md` L865 — `pub struct ValidatedPlan { ir: PlanIR, effects: EffectSet }` — a compiler stage **type**; `term/` X-01 grades the predicate/type homonym **BLOCKING**
- `Red-on-Rust.md` L2111 `Authorized(e, κ)`; L3293 `Authorized(E,κ)`; L4687 `Authorized(E)`; L5998/L6406 `Authorized(A,E,t)`; L8733 v0.3 `Authorized(κ(c), E, t)` — `term/` X-05 (MAJOR): "six incompatible signatures, including both orders in the governing invariant"
- `term/02-collisions.md` rows X-01 (BLOCKING), X-04 (MAJOR), X-05 (MAJOR) — registered as *terminology* collisions; the **verification-contract** consequence is not drawn anywhere

**VIOLATION**
The machine's central security property — the conjunctive chain every implementer must satisfy and every verifier must adjudicate — is stated over predicates that are not well-defined: (a) the first conjunct is `ValidatedRequest(E)` in one frozen statement and `ValidatedPlan(P)` in two, with `ValidatedPlan` also denoting a compiler struct; (b) `Authorized` takes the effect first, the authority first, the actor's capability map, or nothing, across six frozen signatures — X-05 confirms "both orders in the governing invariant" itself. These are not cosmetic: the two first-conjunct forms denote **different checks at different times** (compile-time plan validation vs. request-time validation inside the 16 gates), and the `Authorized` argument-order difference is exactly the difference between SEC-002's global-arena reading (`Authorized(A,E,t)`: authority decides over any requester) and the v0.3 per-actor reading (`Authorized(κ(c),E,t)`: the *holder's* map must contain the capability). The specification's own correction discipline (R-SCOPE-03: STOP on ambiguity) applies to the security theorem itself.

**ATTACK-PATH**
Adversarial-standard path rather than a runtime exploit: an implementation asserts conformance to the README form (`ValidatedPlan(P)` — satisfied by compiling the Block through the pipeline) while an auditor tests the L23694 form (`ValidatedRequest(E)` — requiring per-request revalidation), or vice versa. With `Authorized(A,E,t)` as the operative predicate, the no-possession behavior in SEC-002 is *conformant*; with `Authorized(κ(c),E,t)` it is a violation. Differential adjudication (R-TEST-09's four-way classification) cannot resolve a divergence when the invariant being diverged over has six signatures — the weaker reading is always available to the implementation that wants it. The chain that I2 restates is the *verification contract for all eighteen other findings*; an ill-formed contract launders each of them into a "reference defect" or "spec ambiguity" adjudication instead of a security defect.

**EXPECTED-INVARIANT**
One frozen signature per predicate, with the stronger (security-preserving) reading selected: `ValidatedRequest(E)` (request-time, subsuming `ValidatedPlan(P)` of the plan that produced `E`), and `Authorized(holder, c, E, t) ⇔ c ∈ κ_holder ∧ Valid(c,t) ∧ Authorized(κ_holder(c), E, t)` (the SEC-002 remediation, formalized).

**REMEDIATION**
1. Freeze the canonical statement of the 7-conjunct chain with exact predicate signatures and the subsumption relation `ValidatedRequest(E) ⇒ ValidatedPlan(plan(E))` (or drop the plan conjunct as redundant).
2. Resolve X-01 by renaming the compiler stage struct in a frozen addendum (the terminology pass's no-rename rule yields to a BLOCKING homonym on the security theorem), or by an explicit qualification convention (`ValidatedPlan_pred` vs `ValidatedPlan_struct`) adopted repository-wide.
3. Resolve X-05 by declaring `Authorized` argument order once and correcting the other five statements with supersession notes (the repo's own quoted-not-deleted discipline).

**VERIFICATION**
- `term/_check.py`-style mechanical check extended to the theorem statements: every occurrence of `ValidatedRequest`/`ValidatedPlan`/`Authorized` in normative text must cite the canonical signature.
- The differential fault matrix (SEC-012) must include chain-violation cases whose adjudication depends on the chosen signatures (e.g., forged-CapRef request compiles under plan-time reading, rejected under request-time reading — both implementations must reject after remediation).

---

### SEC-017 — Two complete canonical grammars (LE and BE) coexist in the frozen source; digest identity is implementation-dependent

**LOCATION**
- `Red-on-Rust.md` L28308, L28735 — "revised grammar": explicit widths, **Little-Endian** byte order for all multi-byte integers
- `Red-on-Rust.md` L29830, L29905, L29909, L30542 — Phase 15A final: universal envelope `payload_length: u32 BE`, length prefixes `u32 BE`, `CapRef [index u32 BE][generation u32 BE]`
- `term/02-collisions.md` X-50 (**BLOCKING**: "two field names, two tag widths and two endiannesses") and X-54 (**BLOCKING**: "`TAG_*` constants denote two disjoint tag namespaces"); `spec/06` C-02 marks the revised-grammar §1.3 tags stale — resolution direction known (15A BE governs), but both texts remain frozen without in-source supersession markers

**VIOLATION**
Canonical bytes are the machine's notion of **identity**: `EffectDigest = SHA-256(canonical_bytes(effect))` gates receipt admission (R-EFFECT-06), journal causality (R-DUR-03), replay validation (R-HOST-03), snapshot validity (R-PERSIST-05), and live-vs-replay equality (the differential oracle itself). The frozen source contains **two self-consistent, complete encodings** (LE vs BE, different tag widths and field names). An implementer who builds the revised grammar instead of 15A produces a machine that is internally correct, passes its own golden vectors, and computes digests that match nothing — every cross-implementation evidence artifact (differential equality, recovery differential `Canonical(Recover_P(D)) = Canonical(Recover_R(D))`, replay of recorded traces) is then vacuous or systematically false. The registers grade X-50/X-54 BLOCKING for milestone M1 (serialization) but never draw the consequence that **the integrity chains of MOD-08/09/11/12 all inherit the ambiguity**: a digest-mismatch rejection (`ReplayCorruption`) is only as trustworthy as the uniqueness of the byte grammar behind it.

**ATTACK-PATH**
Evidence-substitution path: a system assembled from components built against different grammars (reference model per the LE sketch, production per 15A — both "frozen-conformant" to a superficial reading) fails all differential runs; the pressure is then to "fix" the comparator (normalizing digests, comparing post-decode values) — which is precisely the comparator weakening R-REF-05 forbids ("never final-value-only") and MOD-17's prohibited-shortcut list targets. The weakened comparator then misses real receipt-substitution divergences (the SEC-001/011 attacks) because digest inequality has been reclassified as an encoding artifact.

**EXPECTED-INVARIANT**
- Exactly one canonical byte grammar may be frozen. All integrity predicates (`EffectDigest`, `StateDigest`, `ResultDigest`, WAL checksum inputs) must be defined over that grammar alone, and every earlier grammar text must carry an in-source supersession marker.
- Cross-implementation digest equality must be meaningful *by construction* — that is the entire justification for canonical serialization (R-CANON-01: "canonical encoding defines semantic identity").

**REMEDIATION**
1. Mark the LE revised-grammar sections superseded **in the frozen source** (the registers already say it; the source doesn't), or issue the one-line addendum: "15A (u32 BE, envelope `version u8 / type_tag u8 / payload_length u32 BE`) is the sole canonical grammar."
2. Resolve X-50/X-54 (field names `payload_length` vs `PayloadLength`; the two `TAG_*` namespaces) in the same addendum.
3. Add a machine-checkable conformance rule: every digest/checksum computation site cites the grammar version; `vectors/canonical` golden vectors are asserted byte-exact in CI for *both* production and reference (they already share fixtures — make the assertion bidirectional).

**VERIFICATION**
- CI gate: decode-encode round-trip over the full golden vector set for production, reference, **and** the persistence layer's payload writer (15B reuses 15A bytes — R-PERSIST-01).
- Negative test: LE-encoded variants of the golden vectors must be *rejected* by all three (guards against a mixed-grammar component).
- Mutation **M031** "component uses the superseded LE grammar" — must kill (detectable by golden-vector mismatch).

---

### SEC-018 — `contains_capability` is a phantom: the marshalling boundary's sole mechanism is undefined, and closure environments can smuggle capabilities

**LOCATION**
- `Red-on-Rust.md` L25685–25691 — frozen `marshal_value`: `if contains_capability(v) { return Err(MarshalFault::CapabilityRequiresDelegation) }` — the **only** occurrence of `contains_capability` in the entire corpus; it is never defined, and no rule states its traversal domain
- `Red-on-Rust.md` L12354–12359 — frozen `FunctionValue { params: Vec<Symbol>, body: Box<Expr>, env: EnvironmentSnapshot }` — closures carry a captured environment
- `Red-on-Rust.md` L10860 — `pub type Environment = HashMap<String, Value>;` (a frozen-era declaration) — environments map names to **`Value`**, which includes `Value::Capability` (machine domain L12283–12310)
- `Red-on-Rust.md` L26007–26030 — `unmarshal(marshalled, &mut actor.capabilities)` receive-side registration (the delegation path's only revalidation moment — likewise unspecified)
- Registered nowhere: the term registry (T-73), collisions (X-65), and module files all discuss `MarshalFault` variants, but the **predicate's absence** is unregistered

**VIOLATION**
R-CORE-07 (`OrdinaryMarshal(Value::Capability) ⇒ Rejected`) and R-MARSHAL-01 ("recursively rejects capabilities — nested in lists, tuples, functions, any structure") reduce, in the operative code, to one call to an **undefined function**. Nothing frozen states whether `contains_capability` descends into: closure environments (`FunctionValue.env` — the one hiding place whose traversal is *not* obvious, since it is an `EnvironmentSnapshot`, not a `Value`), `Bytes` payloads (self-deserializing smuggled refs per SEC-003), `Map` values, `Tuple` elements, or delegation envelopes. The module text asserts "recursive, no exceptions in pure data" — but the *frozen source* never defines the recursion. This is the boundary that the entire actor-isolation story ("isolation" as *authority* safety, MOD-06 SECURITY-BOUNDARY) depends on, and it is one unresolved identifier wide.

**ATTACK-PATH**
1. Attacker actor holds capability `c` and defines `f = λx. …c…` — the closure's captured environment binds `c` (`Environment: HashMap<String, Value>`).
2. `Send(target, Value::Function(f))`: `marshal_value` runs `contains_capability(v)`. An implementation whose predicate traverses only the top-level `Value` variants and the *direct* recursive value children (the natural reading — `EnvironmentSnapshot` is not a `Value`) finds no `Value::Capability` node: the closure crosses.
3. Recipient applies the closure; the environment is re-instantiated in the recipient's heap with `c` bound; the recipient evaluates `Request(c, …)`.
4. Gates 5–7 pass (global arena, no possession check — SEC-002): the recipient now exercises the sender's authority with **zero delegation events, zero marshaller faults, and an unchanged recipient `CapabilityContext`** — the Track-B/Track-C test assertions (`recipient context unchanged`) all *pass* while authority has moved. This defeats the amplification test's detection model exactly, because the capability is never *registered* — it lives in a closure environment.
5. The same ambiguity governs `unmarshal`'s registration side: whether receive-side revalidation (SEC-005) even sees environment-borne capabilities is unspecified.

**EXPECTED-INVARIANT**
- `contains_capability` must be a frozen, total predicate with an explicitly closed traversal domain that **includes** `FunctionValue.env` (recursively), `Tuple`/`List`/`Map` structure at any depth, and delegation envelope contents — and excludes nothing except kernel-sealed delegation envelopes.
- The invariant must be stated over *authority*, not over one value domain: `marshal(v) ⇒ ¬∃c. Reachable(env_of(v), c) ∧ c ∉ DelegatedEnvelopes(v)`.

**REMEDIATION**
1. Define `contains_capability` normatively in the marshalling section: traversal set, recursion depth (structural, unbounded), and behavior on `Bytes` (reject or opacify — `Bytes` are data, but see SEC-003 for the decode-side rule).
2. Extend the definition to closure environments explicitly (the non-obvious case), and state that environments crossing actor boundaries must be capability-free or delegation-wrapped.
3. Register the phantom in `term/` (it is a used-but-never-declared identifier — the declaration sweep's exact category, cf. X-29/X-30/X-64) so the repo's own mechanical checks catch drift.

**VERIFICATION**
- Mutation **M032** "`contains_capability` skips `FunctionValue.env`" — must kill (this is the load-bearing case).
- Property: for every marshalled value `v` (generated over closures capturing arbitrary environments, nested ≥ 3 deep), `marshal(v) = Ok ⇒ ¬∃c reachable from v` — asserted by an oracle predicate independent of the implementation's own traversal.
- Track B round-trip suite extended with closure-carrying values whose environments bind capabilities (must fault, never round-trip).
- Differential: both implementations must fault byte-identically on the closure-smuggling corpus (guards against one implementation quietly traversing envs while the other doesn't — a divergence currently invisible to every frozen test).

---

### SEC-019 — Receiver-side resource asymmetry: unbounded mailboxes, no enqueue-time reservation, no payload-proportional cost rule

**LOCATION**
- `Red-on-Rust.md` L8780–8786 — v0.3 rule 10 E-Send: charges the **sender** `cost_C(send)` consumables only; no reservation against the **recipient's** `R = ⟨M,S⟩`, no mailbox admission check
- `Red-on-Rust.md` L25702–25730 / L26007–26030 — frozen `execute_send`: `target.mailbox.push_back(enqueue)` unconditionally (bounded only by sender budget arithmetic nowhere in the function); `Mailbox`/`VecDeque<MarshalledValue>` — no capacity field anywhere in the corpus (searched: no mailbox bound/limit/max exists)
- `Red-on-Rust.md` L10168+ — `CostModel` trait: operation→cost mapping is "a configurable semantic contract" (L2066: "the actual mapping from IR operations to budget dimensions is a policy decision"); **no frozen rule makes send cost proportional to payload size**, while machine `Value` includes `Bytes(Vec<u8>)` and `String(String)` of unbounded constructed size
- `Red-on-Rust.md` L25573–25615 — spawn escrow is the only place reserved resources transfer; a spawned child that never `Receive`s retains its `M` reservation while its mailbox grows without charging it

**VIOLATION**
Budget conservation (`C_available + C_escrowed + C_consumed = C_initial`) is the machine's answer to resource exhaustion (MOD-04 SECURITY-BOUNDARY), but the frozen send transition debits only the sender's *consumables* and never checks or reserves the recipient's *memory* at enqueue time. Two asymmetries follow: (a) **whose resource is consumed** — mailbox bytes live in recipient state (snapshotted per R-PERSIST-04) but are paid for, if at all, by the sender's `I`/`F` units at a rate the unfrozen `CostModel` chooses; (b) **what a unit buys** — with no payload-proportional rule frozen, a configuration where one `send` unit buys an unbounded `Bytes` payload is conformant. The result is a budget-conserving machine whose *actual* memory footprint is unbounded relative to every frozen dimension — the resource-bounded thesis (R-SCOPE-01) holds in the algebra and fails in the heap.

**ATTACK-PATH**
1. Untrusted plan spawns (or compromises nothing — it *is* the attacker actor) with a modest `I` budget and constructs large `Bytes` payloads (constructed in-heap; no frozen rule bounds constructed value size against `M` either — same gap, construction side).
2. It sends the payloads in a loop to a victim actor that is `Pending`/long-running and never dequeues (or to many zombie children it spawned and abandoned — children it deliberately never schedules meaningfully).
3. Each send costs `cost_C(send)` (constant, sender-borne); each enqueue grows recipient-owned durable state (snapshot content includes mailboxes — R-PERSIST-04 — so the growth also inflates every snapshot/WAL cycle).
4. Global memory grows without violating any frozen invariant: budget conservation holds on all three partitions; the victim's `M` reservation is never consulted; `Deadlock`/`BudgetExhausted` never fires. Availability collapse with a clean audit trail — and snapshot bloat amplifies it into a persistence DoS.

**EXPECTED-INVARIANT**
- Conservation must extend to the resource actually consumed: `Enqueue(v, a_target) ⇒ ReservedOK(size(v), M_target, M_max_target) ∧ SenderCharged(size(v))` — or an equivalent frozen rule that makes memory growth attributable and bounded at admission time.
- Payload-proportional accounting: `cost_C(send) ≥ f(canonical_len(v))` for a frozen monotone `f` with `f` bounded away from 0 per byte (the `I` dimension exists for exactly this).

**REMEDIATION**
1. Freeze the send admission rule: enqueue requires available recipient mailbox capacity (checked, `ReservedCapacityExceeded` on denial — sender faults, sender pays), with capacity part of the recipient's `M` reservation.
2. Freeze the payload-proportional term of `cost_C(send)` over canonical byte length (MOD-10 already defines `Canonical(v)`; reuse it — this also makes the cost deterministic and replay-stable).
3. Symmetrically, bound *constructed* value size against the constructing actor's `M` (allocation is the same resource the reservation exists for).
4. Fold into U-03/U-07's addendum (spawn/budget deltas) so one decision freezes the whole resource-admission surface.

**VERIFICATION**
- Property: for any reachable state, `Σ sizeof(mailbox(a)) ≤ Σ M_reserved(a)` — memory footprint bounded by reserved resources at every step (this fails today by construction).
- Stress mode (MOD-15): sender-flood scenario — `100+` actors, zombie recipients, `Bytes` payloads; assert the machine faults (`ReservedCapacityExceeded`) rather than degrading; assert post-recovery snapshot size is bounded by the same invariant.
- Mutation **M033** "enqueue without recipient capacity check" — must kill.

---

### SEC-020 — Panic-discipline violations on trust-boundary commit paths ("safe due to checks" unwraps)

**LOCATION**
- `Red-on-Rust.md` L10487–10490 — gate-10 commit: `actor.budget.consume(effect.cost.consumable, now).unwrap(); // Safe due to checks` and `actor.budget.reserve(effect.cost.reserved, MAX_RESERVED).unwrap();`
- `Red-on-Rust.md` L23556–23563 — frozen `resume_from_receipt`: the `consume` is checked (faults on failure) but the very next line is `actor.budget.release(*expected_reservation).unwrap();` — mixed discipline in two adjacent lines of the receipt path; same pattern in the 14-gate-era version (L23957–24002)
- `Red-on-Rust.md` L23863–23882 — frozen `finalize_request`: `actor.eval.continuation.pop().unwrap()` and `let Frame::RequestArgument { … } = frame else { unreachable!() }`
- `Red-on-Rust.md` L10588 — `allocate_child_budget(parent_budget, child_budget, spawn_cost).unwrap()` (spawn commit path)
- Contradicted norm: `mod/04` OUTPUTS — "`BudgetError` values (checked-arithmetic failures are data, **never panics**)"; R-BUDGET-02; MOD-01's frozen fault taxonomy (every failure is a machine-visible `Fault`, which is what makes differential fault comparison well-defined — SEC-012)
- (Test-harness `panic!`/`unwrap` occurrences — L11194+, L14254, L15471 etc. — are excluded: they are doubles/asserts, not machine paths.)

**VIOLATION**
The specification's own discipline is total: budget failures are *data*, denial is a five-assertion side-effect-free fault (R-EFFECT-04), and every failure flows through the frozen taxonomy. Yet the frozen machine code panics at exactly the commit points where partial state exists: gate 10/13 (issue+reserve committed after checks), receipt completion (consume-then-release), spawn escrow, and request finalization (`unreachable!` on frame shape). Every unwrap is defended by a *reasoning* ("safe due to checks", "we already proved these can't fail") rather than by construction — and check/commit drift is precisely what maintenance, an M0nn mutation, or a recovery-side inconsistency (SEC-004's unrecoverable arena/budget state) induces. The failure mode of a broken invariant is then not a fault but a **panic mid-transition**, i.e., a crash with journal state that is neither the pre- nor the post-state of the transition.

**ATTACK-PATH**
1. Induce a check/commit drift (examples: `MAX_RESERVED` differing between the gate-9 check call site and the gate-13 commit call site after refactoring; reservation accounting corrupted by the SEC-004 recovery gap; a registered mutant of the M007/M009 family).
2. Gate 8/9 checks pass; gate 13 `reserve(...)` panics — **after** `consume(issue)` already mutated the budget and after `next_effect_id` incremented.
3. The process dies between the check side effects and the durable `EffectIssued` append; crash recovery classifies the half-committed effect per the T-matrix: a `EffectPrepared` already fsynced at step 14 makes the effect `Prepared ∧ ¬Issued ⇒ Discard` while the actor's snapshot budget state says "escrowed" — or `Issued` without the completion the actor actually performed, i.e., **`Indeterminate` for an effect that never reached the host**, or an invisible `Completed` for one that did.
4. The panic has thus *manufactured false effect history* through the very recovery machinery that exists to prevent it (R-DUR-04), and it did so outside the fault taxonomy — invisible to differential fault comparison (SEC-012), which compares only declared faults.
5. Secondary: panic on an attacker-influential path = crash oracle — untrusted plans influence which transitions run (deep argument lists, many pending actors), converting any latent drift into a remotely-schedulable crash.

**EXPECTED-INVARIANT**
- Totality of the fault surface on machine paths: every fallible operation in evaluator/kernel/budget/persistence transitions returns `Result`, and every failure maps to a declared `Fault` — no `unwrap`/`expect`/`unreachable!`/`panic!` in non-test machine code (the frozen `#![forbid(unsafe_code)]` policy at L40453 is the model: the same finality is needed for panics).
- Transition atomicity: a transition either completes (all durable effects appended) or faults (R-EFFECT-04's five assertions) — there is no third "died in the middle" outcome inside the trusted boundary.

**REMEDIATION**
1. Replace all machine-path unwraps with checked calls mapping to a declared internal-consistency fault (add the U-08-chosen equivalent of `Fault::InternalInvariant` to the taxonomy; it must be observable and differentially comparable).
2. Add the engineering rule: `clippy::unwrap_used`/`clippy::expect_used`/no `unreachable!` denied on non-test machine code; extend the frozen L40453 policy block with the panic clause.
3. Restructure the commit sequence so the durable append precedes irreversible in-memory mutations where feasible (or make the commit journal-driven), removing the mid-transition window rather than only its panic failure mode.

**VERIFICATION**
- Fuzz/property: the generated corpus (MOD-15's three modes) plus corrupted-snapshot inputs under a panic-catching harness — zero panics from machine code; every input terminates in `{value, declared fault}`.
- Mutation **M034** "release failure silently ignored (`unwrap` → `let _`)" — must kill (it recreates the M007/M009 family on the receipt path).
- Crash-injection extension: inject a failure at each inter-check commit line; assert recovery's T-classification matches the *durable* prefix exactly (no classification that contradicts the journal).
- Lint gate in CI: machine crates compile with the panic-forbidding lint set (R-REPO-03 structural enforcement).

---

### SEC-021 — Live-fault escrow stranding: no disposition for escrow when a `Pending` effect never completes outside a crash

**LOCATION**
- `Red-on-Rust.md` L23546–23552 / `spec/01` R-EFFECT-06 — receipt mismatch ⇒ `ReplayCorruption` fault with "reservation NOT released" (explicitly held)
- `Red-on-Rust.md` L23574–23580 — host-*failure* receipts **do** complete accounting (escrow consumed as the cost of failure; C-23 comment L25486–25490: "If the host fails, the escrow is simply consumed") — so the covered case is "a receipt arrived with `Err`"
- `Red-on-Rust.md` L35159–35176 / R-RECOV-02 — the T0–T6 matrix: escrow disposition rules exist **only** under crash recovery; R-RECOV-07 reconciliation is scoped to "interrupted effects" (post-crash)
- `Red-on-Rust.md` L41823–41841 — trust table: live host is Partial and can "refuse, delay, or misbehave" — *never answering* is inside the host's declared behavior envelope
- `Red-on-Rust.md` L26807–26817 — Supervisor responsibilities include "fatal-fault policy" — unfrozen (MOD-12: "reconciliation policy sketches are outside the frozen machine core")
- Unregistered: no rule anywhere disposes of escrow for `{Issued, ¬Completed}` in a **live** machine whose actor has faulted, been halted by fatal-fault policy, or whose receipt never arrives

**VIOLATION**
The budget conservation law (`C_available + C_escrowed + C_consumed = C_initial`) is an *accounting* invariant — it is satisfied equally by escrow held forever. The frozen disposition rules cover exactly three exits: completion (receipt `Ok`/`Err`), crash-recovery reconciliation, and T1 discard of prepared-only transactions. Missing: the live, non-crashed machine in which (a) an actor faults while `Pending` (the mismatch fault holds the reservation by design; any actor-local fatal fault likewise leaves the effect open), (b) the supervisor's fatal-fault policy halts a pending actor, or (c) the partial-trust host simply never answers (its declared right). In all three, `complete_max` + reservation remain in the escrowed partition **permanently**, with no frozen rule that ever moves them. The spec's own trust model guarantees the premise (host misbehavior is in-envelope), so the strand is not exotic: it is the steady-state response to host misbehavior.

**ATTACK-PATH**
1. Untrusted plan issues effects to a host that selectively stops answering (a misbehaving-but-conformant Partial host — or one wedged on an OS-level hang).
2. Each issued-never-answered effect strands `complete_max` + `reserve` in escrow; the actors sit `Pending` (unschedulable), also consuming concurrency slots (`S`).
3. No crash occurs, so recovery/reconciliation never triggers; the supervisor's fatal-fault policy is unfrozen, and even a frozen one has no rule saying where the escrow goes.
4. Repeat: `C_available` (and `S` slots) shrink monotonically while every frozen invariant — conservation, no-teleportation, all gates — holds verbatim. The machine becomes a progressive-availability-collapse system with a clean audit trail; at exhaustion it ends in `Deadlock` on an empty runnable queue with escrow full.
5. In the mismatch-fault variant the trigger is a corrupted receipt (SEC-009/011 make those injectable), so the strand is attacker-reachable without any host misbehavior: one bad receipt ⇒ one effect's escrow stranded, one actor faulted — a *permanent* resource burn per injection.

**EXPECTED-INVARIANT**
- Escrow disposition totality: every unit entering the escrowed partition eventually leaves via exactly one frozen path: `Completed` (actual ≤ `complete_max` charged, remainder released) | host-failure consumption (C-23 rule) | durable `Reconciled` (SEC-010's protocol). "Held forever in a live machine" is not a disposition.
- The liveness side of R-DUR-05: escrow *survives* crashes in order to be *reconciled* — survival without any reachable reconciliation path converts the durability invariant into a leak.

**REMEDIATION**
1. Freeze the escrow disposition table covering live faults: actor-fatal-fault with an open effect ⇒ the effect enters the same reconciliation protocol as post-crash `Indeterminate` (unifying SEC-010's protocol across live and crash paths); the supervisor fatal-fault policy must reference it.
2. Add a logical-time bound: a `Pending` effect whose actor's deadline `W` expires (or a frozen per-effect logical timeout) transitions to `Indeterminate` + reconciliation — machine state only (logical time), preserving determinism (no wall clock, R-CAP-09).
3. State the invariant: no reachable quiescent machine state contains escrow that no frozen rule can move (escrowed ⇒ ∃ enabled or pending disposition event).

**VERIFICATION**
- Long-session property: random plans + injected {host hangs, mismatch faults, fatal faults}; at quiescence assert `escrowed = 0 ∨ ∀ escrowed e: Reconciled(e) ∈ durable journal ∧ disposition admissible`.
- Ledger liveness test: `C_available` shrinks only via `consumed` or durable `Reconciled` — never by strand (escrow drains monotonically once inputs stop).
- Mutation **M035** "stranded escrow silently reclaimed to `available` without reconciliation" — must kill (the teleportation mirror-image: conserving the sum while laundering the strand).
- Crash+live mixed harness: crash *after* a live strand; assert recovery does not lose the stranded escrow's reconciliation obligation (journal-driven, not snapshot-driven, disposition).

---

### SEC-022 — The trust model is under-frozen where it matters most (V-03/V-10/V-11; SC-1/2/3 measured FAIL)

**LOCATION**
- `dep/05-violations.md` §1.2 — measured checks: **SC-1 FAIL** and **SC-2 FAIL** (`MOD-13 -> MOD-01 [SECURITY_DEPENDENCY]` — the *planner* module is the recorded provider of security properties); **SC-3 FAIL** (`MOD-13 -> MOD-09 [RUNTIME_DEPENDENCY]` — a production component calls the planner at runtime)
- `dep/05-violations.md` V-03 (MAJOR) — "the dependency as recorded … would let an implementation discharge R-TRUST-01 inside `ror-agent`"; 14 requirement edges; also uncarriable (no `ror-agent -> ror-core` crate edge → hidden dependency HD-1)
- `dep/05-violations.md` V-10 (MAJOR) — (a) the step-14 durable-issuance call (the hinge of R-DUR-02, `HostInvoked ⇒ DurableIssued`) implies a `ror-runtime → ror-persistence` dependency **no crate list carries** — "the single most load-bearing cross-crate call in the design is the one the crate list omits"; (b) `MOD-03 -> MOD-04` implies `ror-core -> ror-kernel`, **forbidden outright** by the frozen edge list (L39821 §14)
- `dep/05-violations.md` V-11 + `Red-on-Rust.md` L27613–27623 vs L41827–41841 — the trust table is frozen **twice with different rows** (11 vs 12; `Persistence` absent from the earlier), and **three authoritative boundary modules have no row at all**: MOD-06 (the marshalling/delegation boundary), MOD-08 (the effect gate sequence), MOD-10 (the canonical codec) — their trust status is inferred from obligations, not frozen in the table
- Cross-reference: SEC-015 (this audit) — same defect at the crate/integration level

**VIOLATION**
This audit's governing axiom — the evaluator/runtime/kernel/host-policy boundary is authoritative — is pinned by R-TRUST-01's table. That table is the one artifact the whole trust story reduces to, and it is (a) duplicated inconsistently, (b) missing the three modules whose authority is *purest* (the codec that mints identity, the marshalling boundary that stops authority transfer, the gate sequence all external effects traverse), and (c) contradicted by the machine-checked dependency graph, which the repository's own audit reports as three measured FAILs — including the planner module recorded as a security *provider* (14 edges) and a production→planner runtime edge. The recorded graph is normative input to `dep/`'s build order and R-REPO-03 structural enforcement; as recorded, it licenses discharging trust obligations inside the one crate that faces the untrusted LLM. And the most security-load-bearing crate call in the design — the durable append that `HostInvoked ⇒ DurableIssued` hangs on — has no legal edge in the frozen crate DAG: the no-host-before-durability hinge is structurally *uncarriable as declared* (implementers must add the edge ad hoc or invert the call, direction undecided — V-10's own note).

**ATTACK-PATH**
Structural/conformance path rather than a single runtime exploit: an implementation (or a reviewer adjudicating a differential divergence) consults the frozen trust artifacts to decide what is authoritative. With the planner recorded as a security provider and `ror-agent` unconstrained by any crate edge to `ror-core`, planner-integration code that "helpfully" enforces the eight prohibitions *inside* `ror-agent` (filtering proposals, synthesizing `PlannerAccepted` records) is defensible as R-TRUST-01 discharge per the recorded graph — while the machine-side checks it duplicates drift (SEC-015's bypass scenario). Separately, a build where `ror-runtime` cannot legally call `ror-persistence` grows a local journal shim ("just an interface") to satisfy R-DUR-02 — a second, unreviewed durability implementation exactly where the causal effect chain lives. Each drift is invisible to MOD-17's dependency review because the reviewed graph is the deficient one.

**EXPECTED-INVARIANT**
- One trust table, complete over every module that enforces a security boundary (all of MOD-02…MOD-12), stated once.
- The typed graph satisfies SC-1/2/3 by construction: no `SECURITY_DEPENDENCY` or `RUNTIME_DEPENDENCY` edge has the planner module as provider or the production side calling into it; prohibitions-on-the-planner are negative contracts homed at their enforcing modules (the correction V-03 itself prescribes).
- The crate DAG carries the R-DUR-02 hinge edge (`ror-runtime → ror-persistence`) or freezes the inverted trait contract explicitly — the durability call may not be structurally orphaned.

**REMEDIATION**
1. Apply V-03's decision: re-home R-TRUST-01's operative enforcement to MOD-03/06/08; keep planner records as prohibitions with no inbound security edge; regenerate `dep/` (the repository's own machinery then passes SC-1/2/3).
2. Apply V-10's decision on the persistence edge and V-09 (budget crate home); add trust-table rows for MOD-06/08/10 and supersede the 11-row table in-source (V-11).
3. Fold SEC-015's crate-separation rule (no LLM-facing code in a crate with runtime/compiler/persistence handles) into R-REPO-03's structural review checklist, so the regenerated graph is checked against it, not just against edge direction.

**VERIFICATION**
- `python3 dep/_graph.py` (the repo's own checker) with SC-1/2/3 promoted from advisory §1.2 rows to **hard failures** — regeneration succeeds only when the planner edges are gone.
- R-REPO-03 dependency review gains explicit assertions: `ror-agent` has no production handle edges; `ror-runtime → ror-persistence` exists (or the frozen inversion); the forbidden-edge list (L39807–39828) is checked mechanically against the actual `Cargo.toml` DAG (V-02 notes nothing currently tracks it).
- Trust-table conformance: a generated check that every module owning a SECURITY-BOUNDARY section has a trust row (mechanizable from `mod/` files + the table).

---

### SEC-023 — Normative-layer content rotation: the canonical specification no longer states the machine's operative security rules under their stable IDs

**LOCATION**
Primary (`spec/01-canonical-specification.md`, the layer every `mod/` file names as "Normative text home"):

- L176–186 — **CAPABILITY block rotated by two positions**: R-CAP-04 ("constraint vs authority") carries the 5-conjunct `Authorized` predicate (which is R-CAP-06 everywhere else); R-CAP-05 ("derivation") carries ancestor-cascading revocation (R-CAP-07's content) — **the derivation law `derive(A,C) = per-op meet; derive(A,C) ≼ A` appears in no CAPABILITY body** (it survives only centrally, R-CORE-04 L28); R-CAP-06 ("canonical authorization predicate") carries lineage-forest bookkeeping; R-CAP-07 carries lifetime expiry only (one conjunct); R-CAP-08 ("algebra theorems") carries the Attenuate evaluation sequence, not the theorems.
- L268–276 — **EFFECT block rotated**: R-EFFECT-04 ("short-circuit") carries receipt-*digest* validation (R-EFFECT-06's content) with **the ID conjunct absent** (digest-only, contra the frozen emphasis "a matching ID with a mismatching digest is not sufficient", L22166–22168); the five-assertion denial short-circuit (subsequent gates uncalled, `next_effect_id` unincremented, budget unchanged, event log unchanged, host never invoked — "the measurable definition of denial" per MOD-08) **appears in no body**; R-EFFECT-05 carries generic completion steps — **the C-23 escrow-affordability fix (`can_consume(issue.checked_add(complete_max))`, overflow ⇒ fault) is gone**; R-EFFECT-07 carries ReplayHost rules (HOST-03/05 content).
- L278–296 — **DURABILITY block**: R-DUR-02 ("issuance transaction, strict order") body is "Durability guarantees MUST hold across process crashes, power failures, and kernel panics…" — the 7-step transaction (append `Prepared` → fsync → append `Issued` → fsync → `Pending` → host) **is gone** (stray blank lines follow the body, consistent with mechanical truncation); R-DUR-03's ID+digest causal-chain rule is replaced by a vague WAL-before-visibility sentence; R-DUR-05 ("escrow survives crash") body is the **WAL frame layout** (R-PERSIST-02 content) — the escrow rule is gone and the body does not match its own citation (L35210–35215 is the escrow text).
- L298–300 — R-HOST-01 body is trait isolation (`HostAdapter`) — the **authoritative independent host check** (`¬HostPolicyOK(E) ⇒ ¬ExternalEffect(E)`, fail-early ⊂ authoritative) is gone; R-HOST-02 body is host-policy access control — **"host performs only issued effects"** (the `PanicHost`-tested precondition) is gone.
- L326 — R-ACTOR-08 body is termination cleanup — the **amplification and teleportation theorems are gone** from the obligation named after them.
- L330–338 — R-MARSHAL-01 body is canonical-bytes transport — **recursive/nested capability rejection is gone** (bare rejection survives only in R-CORE-07 and R-MARSHAL-02's plain form); R-MARSHAL-04 body introduces cyclic-heap/depth-limit content **citing L8695–8698, which is the `CapRef ∉ marshal(v)` rule** — body and citation disagree.
- L98 — R-PLANNER-03 states the **equality** staleness predicate (the secure reading) while `spec/06` C-38 records the canonical resolution as the `<`-only form — the registers mis-describe the canonical text in both directions (see SEC-007).

Secondary (`spec/normative-normalization-records.md` — the audit trail for the rewrites; entry lines: R-CAP-05 L600, R-CAP-06 L610, R-EFFECT-04 L825, R-EFFECT-05 L833, R-DUR-02 L875, R-ACTOR-08 L1043, R-MARSHAL-01 L1053):

- Each record **quotes the correct original** and then "normalizes" into a *different* rule — e.g. R-CAP-05's Original is the meet/derivation law, its Normalized is revocation cascade; R-DUR-02's Original is the 7-step transaction, its Normalized is the crash platitude; R-MARSHAL-01's Original is recursive rejection, its Normalized is transport format — every such record self-certifies **"Semantic Risk: None"**.
- The records' own governing rules (header) include "1. Preserve semantic strength… 8. Preserve negative guarantees. 9. **Preserve security invariants exactly.** 10. Preserve mathematical notation." — every rotated entry violates rules 1/8/9/10 while certifying compliance.

Cross-layer contradiction (same obligation ID, three different bodies):

| ID | `spec/01` body (normative home) | records' "Original" / `mod/`+`req/`+source | `spec/03` matrix + `spec/08` evidence map |
|---|---|---|---|
| R-CAP-05 | revocation cascade | derivation law `derive(A,C) ≼ A` | "derive ≼ A; CAP-DERIVE-NO-AMPLIFICATION, M006" (L70) |
| R-CAP-06 | lineage forest | 5-conjunct `Authorized` predicate | "Canonical Authorized predicate (5 conjuncts); Track B mock-kernel" (L71) |
| R-EFFECT-04 | receipt digest check | five-assertion denial short-circuit | short-circuit Track C evidence |
| R-DUR-02 | generic durability | 7-step issuance transaction | crash harness T0–T4 |
| R-MARSHAL-01 | transport format | recursive capability rejection | `MARSHAL-NO-RAW-CAPABILITY` |

**VIOLATION**
The repository's architecture single-homes normative text in `spec/01` ("Normative text remains single-homed in `spec/01`/`req/`" — README; every `mod/` file: "Normative text home: `spec/01` S-XX") and binds stable obligation IDs to verification tags, mutation targets, milestone gates, and crate homes through `spec/03`/`spec/08`. That ID→rule binding is now corrupt for **48 of 148 obligations (measured; see EXTENT below)** — the hand-confirmed security-operative subset includes the no-amplification law (locally), the measurable definition of denial, the escrow fix for the historical under-escrow vulnerability, the issuance transaction the crash matrix is defined against, half of receipt validation, the recursive qualifier that makes marshal rejection mean anything (SEC-018), both host-boundary rules, the authority-invisibility rule (R-KERN-03), and the reservation predicates (R-BUDGET-03). Nothing detected it: the normalization pass self-certified "Semantic Risk: None" on every replacement, and no mechanical check compares `spec/01` bodies against the records, the matrix, or the source. The README's escape hatch ("where the canonicalized text and `Red-on-Rust.md` differ, the source governs") is unenforceable in practice: an implementer resolving R-CAP-05 through the cross-reference chain (`spec/08` tag → `spec/03` row → `spec/01` body) reads revocation text and receives no diff signal telling them to go read L6397.

**ATTACK-PATH**
Adversarial-conformance path (no runtime exploit needed — the defect *is* the attack surface): an implementation team builds to `spec/01` as their single normative source, exactly as the repository instructs. Their machine: computes `derive` without the meet law's guarantee (R-CAP-05's body is silent — they implement attenuation as replacement, a bug class M006 exists to catch, but they write the conformance tests from `spec/01` too, so their "R-CAP-05" tests check revocation and pass); validates receipts by digest only (R-EFFECT-04's body — substitution of a stale same-digest receipt is invisible); escrows `issue` but not `complete_max` (R-EFFECT-05's body never states the checked add — the historical C-23 under-escrow vulnerability re-enters through the front door); performs host invocation after an in-memory "issued" flag (R-DUR-02's body demands crash-durability, not ordering); marshals values with a top-level capability check only (R-MARSHAL-01's body mandates format validation, not recursive rejection). Every gap maps to a runtime attack chain already documented in SEC-001…SEC-018 — but here the attacker does not need to exploit the machine, because the specification the machine is certified against stopped containing the rules. Differential testing would eventually catch behavioral divergence against the reference model — but the reference implementers read the same rotated layer, and where both agree on the weakened rule the differential passes vacuously: the oracle-collapse failure MOD-14/MOD-16 exist to prevent, entering through the documentation layer instead.

**EXPECTED-INVARIANT**
- **ID→rule binding integrity**: for every obligation ID, the `spec/01` body, the normalization record's Normalized text, the `spec/03` matrix description, the `spec/08` evidence mapping, and the cited source lines must state the same rule. Any rewrite that changes *which* rule an ID denotes (not merely its modality) is a supersession event requiring its own record — the repo's own R-SCOPE-03 discipline applied to its normative layer.
- Security rules may not be dropped from the canonical layer while surviving only inside audit-record quotations: presence in `spec/01` under the stable ID is what tags, mutants, and milestones resolve against.

**REMEDIATION**
1. Restore the ten-plus rotated bodies in `spec/01` from the records' own "Original" quotations (intact there) or from the cited source lines; re-run the normalization with content preservation actually enforced.
2. Add the missing mechanical check — the repo already practices exactly this discipline elsewhere (`term/_check.py` re-greps 1008 citations; `dep/_graph.py` re-derives every edge): a `spec/_check.py` that, per obligation ID, asserts agreement on rule identity across `spec/01` body ↔ records' Original/Normalized ↔ `spec/03` row, failing on rotation.
3. Re-adjudicate every "Semantic Risk: None" in the affected records; the fields are currently false.
4. Reconcile C-38's description of the canonical staleness form with `spec/01` L98 (which already carries the secure equality form) — SEC-007's remediation should adopt `spec/01`'s text as canonical and fix the conformance suite.

**VERIFICATION**
- The new cross-layer consistency check demonstrably fails on the current tree (write it before restoring, so the failure is evidence), then runs green in CI.
- Documentation-level mutation **M036**: "rotate one `spec/01` security body onto adjacent content" — the consistency check must kill it (guarding the normative layer the way M015/M016 guard the WAL).
- Post-restoration spot-proof: `derive(A,C) ≼ A`, the five short-circuit assertions, `can_consume(issue + complete_max)`, the 7-step order, `receipt.id ∧ receipt.digest`, recursive marshal rejection, `HostInvoked ⇒ DurableIssued`, and both host-boundary rules each appear under their stable IDs in `spec/01`, greppably.

**EXTENT, DISTRIBUTION, AND DETECTION GAP (measured — `audit/spec_check.py` + `audit/spec_map.py`, run evidence below)**

- **Displacement map (mechanical classification of the 48)**: **13 DISPLACED** — rotation proven by nearest-Original signature match ≥ 0.35, including every hand-verified case (R-CAP-04→R-CAP-06 at 0.62, R-CAP-05→R-CAP-07 at 0.60, R-DUR-05→R-PERSIST-02 at 0.41, R-EFFECT-05→R-EFFECT-07 at 0.37) plus R-EFFECT-02→R-DUR-01 at **0.86**, R-BUDGET-06→R-ACTOR-05, R-CAP-02/08→R-CORE-04, R-CANON-06/09→R-CANON-04, R-DUR-01→R-DUR-03, R-KERN-03→R-CLAIM-02, R-PERSIST-03→R-PERSIST-02; **30 WEAKENED** — rewritten to generic prose with the rule's distinctive content deleted (includes R-KERN-03's invisibility rule, R-BUDGET-03's predicates, R-HOST-05's trace-validation rule); **5 UNMATCHED** — invented/foreign text corresponding to no obligation (R-BUDGET-02, R-BUDGET-08, R-CEK-07, R-HOST-04, R-MARSHAL-04).
- **Mechanical measurement (D1): 48 of 148 records (32%)** have a "Normalized" text that denotes a *different rule* than the same record's "Original" quotation. Hand-adjudication of a six-record sample of newly flagged entries (R-CANON-03, R-BUDGET-03, R-HOST-05, R-MARSHAL-03, R-CEK-06, R-KERN-03) confirmed **6/6 true substitutions — zero false positives**. The corruption is therefore ~2.5× the original 19-obligation sample estimate, and it is not purely adjacent-block rotation: some entries are *replacements with other or invented text* (R-HOST-05's Normalized — "host callbacks MUST NOT directly mutate machine memory" — corresponds to no HOST obligation), and at least two are **security weakenings**: R-KERN-03 (Original: "`AuthorityNode` and all authority internals MUST remain `pub(crate)`/inaccessible… No hidden authority inspection" → Normalized: softer "mutations only via kernel interface" — the no-hidden-authority *operative* statement is gone, removing spec/01 support for SEC-002/008) and R-BUDGET-03 (Original: the C-07 frozen fix `ReserveOK(r,R,R_max) ⇔ R + r ≤ R_max`, `ReleaseOK(r,R) ⇔ r ≤ R` → Normalized: generic reserved-vector tracking — the predicate forms are gone).
- **Newly confirmed security-significant substitutions beyond the original 19**: R-KERN-03 (authority invisibility), R-BUDGET-03 (reservation predicate fix), R-CEK-06 (continuation +1/−1 frame preservation → replaced by environment-lookup text), R-CANON-03 (frozen tag table → replaced by UTF-8 rules), R-HOST-05 (trace-level replay validation → replaced by host-callback text), R-MARSHAL-03 (marshal round-trip law → replaced by delegation-envelope contents).
- **Checker agreement (D2/D3)**: 52 obligations where the `spec/01` body does not match its own cited source lines, 54 where the `spec/03` matrix row disagrees with the `spec/01` body (both include some low-signal terse-body cases; the union with D1 is the confirmed set).
- **`req/` is intact.** The atomic registry carries every substituted rule verbatim: the derivation law (part2 L765/L821/L824), the 5-conjunct predicate (L737), the escrow fix `can_consume(issue + complete_max)` (part3 L593), the receipt ID∧digest conjunction (part3 L834), recursive marshal rejection (part4 L908/L922), and the full 7-step issuance transaction (REQ-DUR-002, part4 L23–30, with both fsync positions); `req/02` CN-01 keeps the 7-conjunct chain as one unsplit record. The README's "single-homed in `spec/01`/`req/`" therefore half-broke: one home lost the rules, the other kept them — which makes restoration fully mechanical and traceable.
- **Distribution is the worst possible**: the 100 D1-clean records are precisely the *definitional/provenance* obligations — all of CORE (R-CORE-01…10), TRUST, SCOPE, ARCH, CLAIM, ORDER, REPO, TEST, REF, PLANNER, RECOV, COMPILE, CALC, plus the structural survivors KERN-01/02, CEK-01/02/04/05, DUR-04, EFFECT-01/03, MARSHAL-02, PERSIST-02/04/05/06, BUDGET-05/07, ACTOR-02…07, CAP-01/09, CANON-04 — while the flagged 48 concentrate in the *authority- and effect-enforcement* obligations (CAP-02…08, KERN-03, BUDGET-01…04/06/08, CANON-01…03/05…11, DUR-01/02/03/05, EFFECT-02/04…07, HOST-01…05, MARSHAL-01/03/04, PERSIST-01/03, ACTOR-01/08, CEK-03/06/07). A reader auditing the canonical layer finds the machine's shape fully specified and its security gates missing.
- **Detection gap is precise**: `req/_validate.py` check #5 verifies only that each `spec/01` obligation ID is *cited* by some record (existence, not content), and its check #7 — "signature provenance: every type-like identifier in STATEMENT … occurs inside the cited line range … the check that catches a copied-but-wrong `L3xxxx` citation" — is applied **only to registry records, never to `spec/01` bodies**. The repository built exactly the right weapon and pointed it away from the layer that substituted.
- **Remediation refinement**: the detector now exists as `audit/spec_check.py` (stdlib-only, deterministic; exit 1 on any ID→rule violation). On the current tree it reports `parsed: 148 records, 148 spec/01 obligations, 148 matrix rows` → **FAIL: 154 violations (48×D1, 52×D2, 54×D3)** — the "demonstrable failure" evidence VERIFICATION requires, produced *before* any restoration. The **restoration draft** also exists: `audit/spec01-restoration-draft.md` (755 lines, generated by `audit/spec_map.py`) — for each of the 48: the substituted text (quoted, per the repository's quoted-not-deleted discipline), the restoration text (the record's own Original — verified against `req/`), the displacement classification, and an adoption procedure gated on `spec_check.py` exiting 0. **Dry-run proof (`audit/spec_restore_dryrun.py`, frozen text untouched):** applying the draft to temporary copies of both corrupted layers moves the detectors from 48/52/54 to **D1=0, D2=18, D3=16** — and the residuals delimit cleanly: zero residual D2/D3 *on the restored 48* except four D3 label-vs-content false positives (matrix rows that name a theorem — "No amplification / no teleportation theorems", "Progress & preservation" — against bodies that state it); all other residuals are pre-existing terse-body/label-row cases on D1-clean obligations, previously masked by the larger counts. The draft is therefore proven sufficient to restore ID→rule binding integrity. Promote the checker to `spec/_check.py` (or extend `req/_validate.py` check #7 to `spec/01` bodies) so it gates regeneration; M036 is its mutation target.

---

## 4. Escalation-vector coverage matrix

Requested search vectors vs. findings (● primary, ○ contributing):

| Vector | SEC-001 | SEC-002 | SEC-003 | SEC-004 | SEC-005 | SEC-006 | SEC-007 | SEC-008 | SEC-009 | SEC-010 | SEC-011 | SEC-012 | SEC-013 | SEC-014 | SEC-015 | SEC-016 | SEC-017 | SEC-018 | SEC-019 | SEC-020 | SEC-021 | SEC-022 | SEC-023 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| raw capability transfer | ● | ○ | ● | | ○ | | | ○ | ○ | | | | | | | | | ● | | | | | ○ |
| capability copying | | ○ | | | | ● | | | | | | | | | | | | ○ | | | | | ○ |
| serialization | | | ● | ○ | ○ | | | | ○ | | ● | | | | | | ● | ○ | ○ | | | | ○ |
| deserialization | | ○ | ● | ● | ○ | | | | ○ | | ○ | | | | | | ● | | | | | | |
| actor spawning | | ○ | | | ○ | ● | | | | | | | ○ | ○ | | | | | ○ | ○ | | | |
| message passing | | | ● | | ● | | | | | | | ○ | | | | | | ● | ● | | | | ○ |
| planner output | | ● | | | | | ● | ● | | | | | | | ● | | | | | | | ○ | |
| continuation state | ● | | | ○ | | | | | | | ● | | | | | | | ○ | | ○ | | | |
| persistence | | | ○ | ● | | | | | ● | | ● | | | | | | ○ | | ○ | ○ | ○ | ● | ○ |
| replay | ● | | | | | | ○ | | ○ | ○ | ● | ● | | | | | ● | | | | | | ○ |
| host APIs | ● | | | | | | | | | ● | | ○ | ● | | ○ | | | | | ○ | ● | | ○ |
| FFI | | | | | | | | | | ○ | | | ● | | ○ | | | | | | | | |
| debugging interfaces | | ○ | | | | | | ○ | | | | ○ | | | ○ | | | | | | | | |
| reflection | | ○ | | | | | | ● | | | | | | | | | | ○ | | | | | |
| error paths | ○ | | | | ○ | | | | | ○ | ○ | ● | | ● | | | | | | ● | ○ | | |
| resource-boundary DoS | | | | | | ○ | | | | | | | | | | | | | ● | ○ | ● | | |
| trust-model/dependency integrity | | | | ○ | | | | | | | | | ○ | | ● | ○ | ○ | ○ | | | | ● | ○ |
| normative-layer integrity (ID→rule binding) | | | | | ○ | | ○ | | | ○ | | ○ | | | | ○ | | ○ | ○ | | | | ● |

No frozen `unsafe`, `extern "C"`, `transmute`, or native-callback-in-AST surface exists in the operative text — **verified positively**: the frozen source *prohibits* semantic feature flags including `feature = "unsafe-capabilities"` by name (L40408–40420), mandates `#![forbid(unsafe_code)]` as the default crate-level policy (L40453–40465), forbids host callbacks in the AST (L12134–12136), and `FunctionValue` is pure lambda data (L12354–12359). FFI risk concentrates entirely in the host executor process boundary (SEC-013) and crate graph (SEC-015).

## 5. Mechanisms verified sound (no finding — verified against the frozen source `Red-on-Rust.md` and the `mod/` layer)

> **Caveat (SEC-023):** several of the rules below (gate ordering, short-circuit assertions, escrow fix, durable-before-host) are sound *where the frozen source states them* but were dropped or rotated out of `spec/01`, the designated normative home. "Verified sound" therefore means "sound in the frozen source and module layer," not "securely stated at every layer."

- **16-step gate order & short-circuit** (L38022–38050; R-EFFECT-03/04): correct, frozen, mutation-covered (M010); no reordering/skip path found in operative text.
- **Escrow accounting** (R-EFFECT-05, the C-23 fix): `can_consume(issue + complete_max)` with checked add — the historical under-escrow vulnerability is genuinely fixed in the canonical text.
- **Durable-before-host** (R-DUR-01/02): ordering with two fsyncs is airtight *within* the machine path (see SEC-010/015 for the paths around it).
- **Crash classification discipline** (R-DUR-04, T0–T6): never-infers-NotExecuted is consistently frozen.
- **Canonical decoder hardening** (R-CANON-07/08): checked lengths, no attacker preallocation, bounded cursors, trailing-byte and duplicate-key rejection — hostile-input discipline is excellent (the findings in SEC-003/SEC-017 concern *what* is accepted and *which* grammar governs, not how rigorously it is parsed).
- **Compiler boundary structure** (R-COMPILE-01/05): constructor privacy + `Block ≠ ExecutablePlan` hold in the operative text (the static-analysis content gap is filed under SEC-002/U-22 rather than as a boundary break).
- **Budget algebra** (checked arithmetic, partition conservation, no-partial-debit): no teleportation path found in the operative text (spawn-side policy gap filed as SEC-006/U-03).
- **Scheduler determinism** (FIFO, at-most-once, non-schedulable states): no authority-relevant defect.
- **Determinism/no-wall-clock discipline** (R-CAP-09): consistent.

## 6. Required actions, priority order

1. **SEC-023** — restore the substituted obligation bodies in `spec/01` and promote the cross-layer ID→rule consistency check. Until the normative layer states the rules again, *every other remediation is undraftable*: the frozen addenda this audit prescribes would be written against a layer that no longer contains the rules they amend. (The correct texts survive verbatim in the normalization records' "Original" quotations and in `req/` — restoration is mechanical; the detector already exists at `audit/spec_check.py` and fails on the current tree: 48×D1/52×D2/54×D3.)
2. **SEC-001, SEC-002** — freeze receipt-result admission and holder-possession binding. Until both are frozen, the central thesis `LLMOutput ∧ UntrustedInput ↛ ExternalEffect` is falsifiable by a conforming implementation, and every other guarantee is derivative.
3. **SEC-016, SEC-018** — freeze one signature set for the central theorem's predicates (ValidatedRequest subsumption; `Authorized(holder,c,E,t)`), and define `contains_capability` including closure environments. An ill-formed invariant and an undefined boundary predicate make all other remediations unadjudicable.
4. **SEC-003, SEC-004, SEC-022** — split data/kernel codecs; make the authority lattice durable and revalidated at recovery; complete and de-duplicate the trust table, re-home the planner security edges (V-03), and carry the R-DUR-02 crate edge (V-10) — the durability hinge must be structurally carriable.
5. **SEC-005, SEC-006** — freeze the delegation surface and the spawn authority rule (strict attenuation or manifest).
6. **SEC-007, SEC-008, SEC-017** — equality staleness (adopt `spec/01` L98's form; fix the `<`-only conformance text); capability-opaque observations (define `CapabilitySummary`); single canonical grammar with in-source supersession of the LE text.
7. **SEC-009…SEC-012, SEC-020** — storage authenticity decision; reconciliation protocol (incl. the declared `NotExecuted` variant); durable receipts; fault enumeration; panic-free machine paths with a declared internal-consistency fault (the repo's own BLOCKING grading of U-14/X-67 is endorsed and extended with the resume-vs-fault semantics requirement).
8. **SEC-013, SEC-014, SEC-015, SEC-019, SEC-021** — isolation posture decision; `AdmissibleConstraint`; root-grant protocol and crate separation; mailbox/payload resource-admission rules; escrow disposition totality for live faults.

All remediations are specification-level (frozen-addendum) actions; per R-SCOPE-03, none may be resolved by implementation choice or test adjustment. Proposed new mutation-registry entries M019–M036 are additive per R-TEST-04.

---

## 7. Audit closure

**Layers examined:** frozen source `Red-on-Rust.md` (grep-swept in full; ~60 sections read in depth), `spec/` (01–09 + normalization records + index), `mod/` (all 20 files), `req/` (registry parts 1–8 + method/compound/ambiguous + `registry.json` structure + `_validate.py` scope), `term/` (collisions index, laws, dictionary spot-checks), `dep/` (violations register §1–§7, graph), `README.md`. **Tooling delivered:** `audit/spec_check.py` — the SEC-023 cross-layer ID→rule consistency detector (D1 records' Original↔Normalized rule identity, D2 spec/01 body↔cited source lines, D3 spec/01 body↔spec/03 matrix rows); deterministic, stdlib-only, exits 1 on violation; current-tree run: **FAIL, 154 violations (48/52/54)**. `audit/spec_map.py` + `audit/spec01-restoration-draft.md` — the displacement map (13 DISPLACED / 30 WEAKENED / 5 UNMATCHED) and the per-obligation restoration draft for specification-owner adoption (no frozen text changed). `audit/spec_restore_dryrun.py` — applies the draft to temporary copies and re-measures: **48/52/54 → 0/18/16, with zero true-positive residuals on the restored set** — the draft's sufficiency is proven.

**Vectors covered:** the 14 requested escalation vectors plus four that emerged (resource-boundary DoS, trust-model/dependency integrity, normative-layer integrity, panic/crash-oracle) — 18 vectors × 23 findings in §4.

**Closure criteria:** every finding cites frozen-source or repository-layer line evidence verified in this session; every requested vector maps to at least one primary finding; every security-relevant gap not filed here is already registered in the repository's own machinery (U-01…U-34, C-01…C-76, the X-01…X-86 blocking set, V-01…V-11, AMB-01…39) and is cross-referenced where it aggravates a finding. No further passes are planned; the highest-value next action is the remediation order in §6, beginning with SEC-023's mechanical restoration from `req/` and the records' "Original" quotations.

**Totals:** 23 findings — 3 CRITICAL (SEC-001, SEC-002, SEC-023), 5 HIGH (SEC-003, SEC-004, SEC-005, SEC-016, SEC-018), 3 MEDIUM-HIGH (SEC-006, SEC-020, SEC-022), 9 MEDIUM (SEC-007, SEC-008, SEC-009, SEC-010, SEC-011, SEC-012, SEC-017, SEC-019, SEC-021), 2 LOW-MEDIUM (SEC-013, SEC-014), 1 LOW (SEC-015); 18 proposed mutation-registry additions (M019–M036); 2 proposed new verification tags (`EFFECT-RECEIPT-RESULT-NO-AUTHORITY`, `RECOVERY-REVOCATION-DURABLE`).
