# Red-on-Rust Specification Audit — Authority, Trust-Boundary, and External-Effect Errors

**Audit date:** 2026-09-02
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

**I1 and I2 do not hold at specification level.** The 16-step gate sequence itself is sound and well-ordered, but the *state surrounding* the gates contains fifteen specification-level defects through which untrusted input or a partially-trusted host can reach an `ExternalEffect` (or destroy/forge the authority facts the gates depend on): 2 CRITICAL (complete authority-injection chains exist in conforming implementations), 3 HIGH, 1 MEDIUM-HIGH, 6 MEDIUM, 2 LOW/MEDIUM, 1 LOW.

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

## 4. Escalation-vector coverage matrix

Requested search vectors vs. findings (● primary, ○ contributing):

| Vector | SEC-001 | SEC-002 | SEC-003 | SEC-004 | SEC-005 | SEC-006 | SEC-007 | SEC-008 | SEC-009 | SEC-010 | SEC-011 | SEC-012 | SEC-013 | SEC-014 | SEC-015 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| raw capability transfer | ● | ○ | ● | | ○ | | | ○ | ○ | | | | | | |
| capability copying | | ○ | | | | ● | | | | | | | | | |
| serialization | | | ● | ○ | ○ | | | | ○ | | ● | | | | |
| deserialization | | ○ | ● | ● | ○ | | | | ○ | | ○ | | | | |
| actor spawning | | ○ | | | ○ | ● | | | | | | | ○ | ○ | |
| message passing | | | ● | | ● | | | | | | | ○ | | | |
| planner output | | ● | | | | | ● | ● | | | | | | ○ | ● |
| continuation state | ● | | | ○ | | | | | | | ● | | | | |
| persistence | | | ○ | ● | | | | | ● | | ● | | | | |
| replay | ● | | | | | | ○ | | ○ | ○ | ● | ● | | | |
| host APIs | ● | | | | | | | | | ● | | ○ | ● | | ○ |
| FFI | | | | | | | | | | ○ | | | ● | | ○ |
| debugging interfaces | | ○ | | | | | | ○ | | | | ○ | | | ○ |
| reflection | | ○ | | | | | | ● | | | | | | | |
| error paths | ○ | | | | ○ | | | | | ○ | ○ | ● | | ● | |

No frozen `unsafe`, `extern "C"`, `transmute`, or native-callback-in-AST surface exists in the operative text (host callbacks in AST are explicitly forbidden, L12135–12136; `FunctionValue` is pure lambda data, L12354–12359) — FFI risk concentrates entirely in the host executor process boundary (SEC-013) and crate graph (SEC-015).

## 5. Mechanisms verified sound (no finding)

- **16-step gate order & short-circuit** (L38022–38050; R-EFFECT-03/04): correct, frozen, mutation-covered (M010); no reordering/skip path found in operative text.
- **Escrow accounting** (R-EFFECT-05, the C-23 fix): `can_consume(issue + complete_max)` with checked add — the historical under-escrow vulnerability is genuinely fixed in the canonical text.
- **Durable-before-host** (R-DUR-01/02): ordering with two fsyncs is airtight *within* the machine path (see SEC-010/015 for the paths around it).
- **Crash classification discipline** (R-DUR-04, T0–T6): never-infers-NotExecuted is consistently frozen.
- **Canonical decoder hardening** (R-CANON-07/08): checked lengths, no attacker preallocation, bounded cursors, trailing-byte and duplicate-key rejection — hostile-input discipline is excellent (the finding in SEC-003 is about *what* is accepted, not how).
- **Compiler boundary structure** (R-COMPILE-01/05): constructor privacy + `Block ≠ ExecutablePlan` hold in the operative text (the static-analysis content gap is filed under SEC-002/U-22 rather than as a boundary break).
- **Budget algebra** (checked arithmetic, partition conservation, no-partial-debit): no teleportation path found in the operative text (spawn-side policy gap filed as SEC-006/U-03).
- **Scheduler determinism** (FIFO, at-most-once, non-schedulable states): no authority-relevant defect.
- **Determinism/no-wall-clock discipline** (R-CAP-09): consistent.

## 6. Required actions, priority order

1. **SEC-001, SEC-002** — freeze receipt-result admission and holder-possession binding. Until both are frozen, the central thesis `LLMOutput ∧ UntrustedInput ↛ ExternalEffect` is falsifiable by a conforming implementation, and every other guarantee is derivative.
2. **SEC-003, SEC-004** — split data/kernel codecs; make the authority lattice durable and revalidated at recovery.
3. **SEC-005, SEC-006** — freeze the delegation surface and the spawn authority rule (strict attenuation or manifest).
4. **SEC-007, SEC-008** — equality staleness; capability-opaque observations (define `CapabilitySummary`).
5. **SEC-009…SEC-012** — storage authenticity decision; reconciliation protocol; durable receipts; fault enumeration (the repo's own BLOCKING grading of U-14/X-67 is endorsed and extended with the resume-vs-fault semantics requirement).
6. **SEC-013…SEC-015** — isolation posture decision; `AdmissibleConstraint`; root-grant protocol and crate separation.

All remediations are specification-level (frozen-addendum) actions; per R-SCOPE-03, none may be resolved by implementation choice or test adjustment. Proposed new mutation-registry entries M019–M030 are additive per R-TEST-04.
