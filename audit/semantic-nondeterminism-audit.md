# Red-on-Rust Specification Audit — Semantic Nondeterminism

**Audit date:** 2026-09-03
**Audited artifact:** frozen specification set at branch commit `3d00818` (`Red-on-Rust.md`, 42,312 lines; canonical set `spec/`, `mod/`, `req/`, `term/`, `dep/`)
**Audit class:** sources of *semantic* nondeterminism — anything that can make two executions from the same declared inputs diverge in **machine state, event trace, or canonical bytes**. No authority, conformance, style, or performance findings except where they are the nondeterminism.
**Companion audit:** `audit/authority-trust-external-effect-audit.md` (SEC-001…023). Where a finding here shares a root cause with a SEC finding, it is cross-referenced; the contribution here is the *determinism* consequence, which that audit does not make.

---

## 1. What is under test

The specification's own determinism claim, stated four times in the frozen source and transcribed into four normative obligations:

> **DT.** `InitialState + SchedulerTrace + HostTrace ⇒ UniqueMachineTrace`
> *(L25338, L25763, L26053, L41641; `spec/01` R-CORE-08, R-ACTOR-07, R-PLANNER-04 (with `+ Plan`), R-SCOPE-01 informative; `mod/01` §INVARIANTS, `mod/07` §39/§93, `mod/13` §44)*

Two variants also occur in frozen text and are **not** the same statement:

- `MachineState + AcceptedPlan + SchedulerTrace + HostTrace ⇒ UniqueMachineTrace` (L28426, L28575)
- `Snapshot + EventLog + HostTrace + SchedulerTrace ⇒` identical recovered state (L26998)

Reading DT as an audit obligation, it asserts a **function**

```
step* : InitialState × SchedulerTrace × HostTrace → MachineTrace
```

is total and single-valued. An audit of semantic nondeterminism is therefore an audit of every input this function *actually* reads that is not one of those three arguments. Each such hidden input is a finding.

**Scope boundary, stated up front (and never violated below):** DT is a statement about the machine. It is *not* a statement about the world. See §5.

---

## 2. Verdict

**DT does not hold as stated, for three independent classes of reason.**

| Class | Verdict |
|---|---|
| **(A) The theorem is not well-formed.** `SchedulerTrace`, `HostTrace`, `InitialState`, and `UniqueMachineTrace` are **undefined terms** — they occur only inside the boxed formula, in all 13 occurrences across 42,312 lines, and in none of the four canonical organizations as a type, struct, grammar, or field list. A theorem quantifying over undefined objects cannot be discharged, and cannot be tested. | **DET-001, CRITICAL** |
| **(B) The machine reads inputs not in the theorem.** Nine concrete hidden inputs are present in *frozen, operative* text: `HashMap` iteration in state that is snapshotted and digested; a `HashMap`-keyed `ReplayHost`; Unix-timestamp capability lifetimes checked against `LogicalTime`; unfrozen `δ_t`; unfrozen canonical encoding for 90% of the snapshot; two coexisting canonical grammars; `usize` in semantic positions; `format!("{:?}")` host text entering machine values; filesystem "locate newest snapshot". | **DET-002…DET-013** |
| **(C) The required inventory is partially absent.** Of the seven mechanisms the machine "must use," three are frozen and adequate (LogicalTime, deterministic IDs, deterministic queues), two are frozen but incomplete (canonical serialization, ordered event traces), and two **do not exist as artifacts at all** (explicit SchedulerTrace, explicit HostTrace). | **§4 table** |

**Counts.** 18 findings: 2 CRITICAL, 5 HIGH, 6 MEDIUM, 3 LOW-MEDIUM, 2 CLEAN (checks that pass, recorded so the negative result is auditable).

`SchedulerTrace` and `HostTrace` are the *inputs the theorem is parameterized on*. They are the two things in the inventory that do not exist. That is the headline: **the determinism theorem's own free variables are undefined**, and every downstream verification obligation written against it (`R-REF-01`, `R-HOST-03/04/05`, Track A, Track D, the M1 "canonical bytes deterministic" acceptance gate) is therefore written against an unfixed referent.

### Finding index

| ID | Severity | Category (from the requested checklist) | One-line violation |
|---|---|---|---|
| DET-001 | CRITICAL | *(all — foundational)* | `SchedulerTrace`, `HostTrace`, `InitialState`, `UniqueMachineTrace` are undefined; DT quantifies over nothing |
| DET-002 | CRITICAL | unspecified serialization order | `GlobalState` snapshot encoding unfrozen for all machine (non-data) state; `state_digest` uncomputable, so "identical trace" is undecidable |
| DET-003 | HIGH | unordered map iteration | `Environment = HashMap<String, Value>` and `ActorTable = HashMap<ActorId, ActorState>` in frozen operative structs that are snapshotted and digested |
| DET-004 | HIGH | hash randomization | Rust `RandomState` is per-process seeded; every `HashMap`/`HashSet` in machine state imports a per-process random input DT does not admit |
| DET-005 | HIGH | host-dependent ordering / network timing | `ReplayHost` has three incompatible frozen shapes — `HashMap` lookup, `VecDeque` pop, ordered `Vec`+cursor — and only the third satisfies R-HOST-03 |
| DET-006 | HIGH | wall-clock time | `Lifetime { start: u64, end: u64 } // Unix timestamp` is compared against `LogicalTime` in the frozen `authorizes` predicate — a direct R-CAP-09 violation inside the authorization gate |
| DET-007 | HIGH | unspecified serialization order | Two complete canonical grammars (LE at L28309, BE at L29123) coexist frozen; digests differ; DT's "identical trace" is grammar-relative |
| DET-008 | MEDIUM | nondeterministic scheduling | `δ_t` per transition kind is unfrozen (U-07); `LogicalTime` advances on an unspecified schedule, so deadline outcomes are implementation-chosen |
| DET-009 | MEDIUM | hidden global state | Kernel authority arena, `revocation_set`, and generation counters sit outside `GlobalState` — DT's `InitialState` does not name the state authorization reads |
| DET-010 | MEDIUM | allocator-dependent semantics | `CapRef{index, generation}` and `GenerationalArena` semantics depend on slot-reuse policy, which is unfrozen; `SlotMap` key allocation is not a specified function |
| DET-011 | MEDIUM | platform-dependent integer behavior | `usize` in `MaxBytes(usize)`, `ResourceLimits.max_bytes/max_calls`, `ReplayHost.cursor`, arity fields — 32/64-bit divergence in authorization-relevant comparisons |
| DET-012 | MEDIUM | hidden global state / unspecified order | `format!("{:?}", e)` places Rust `Debug` output into `Value::String` inside a machine value (L23994) — compiler-version-dependent machine state |
| DET-013 | MEDIUM | filesystem ordering | "Locate newest committed snapshot" (L26482, L34345, L35193) is unspecified — directory-order-dependent recovery input |
| DET-014 | LOW-MED | thread scheduling | `Arc<Mutex>`/`dashmap`/`arc-swap` for arena and revocation set (L247, L334) never retired; concurrent structures under a lockstep theorem |
| DET-015 | LOW-MED | randomized identifiers | `fresh_handle()`/`fresh_actor()` (L2273, L2013 "globally unique") survive in frozen semantic rules alongside the counter fix that supersedes them |
| DET-016 | LOW-MED | nondeterministic scheduling | Spawn budget split `α` (A2) unfrozen; spawn is a machine transition whose numeric result is implementation-chosen |
| DET-017 | CLEAN | floating-point dependence | **No finding.** Zero `f32`/`f64` occurrences in 42,312 lines; all quantities are `u64`/`u32` with checked arithmetic |
| DET-018 | CLEAN | implicit environment variables | **No finding.** Zero `std::env`/`env::var`/`getenv` occurrences; no configuration-by-environment channel in frozen text |

---

## 3. Findings

---

### DET-001 — CRITICAL — The determinism theorem's free variables are undefined

**LOCATION**
- `Red-on-Rust.md` L25338, L25763, L26053, L27369, L27529, L27536–27539, L28238–28239, L28426, L28575, L37118–37121, L41641 — all 13 occurrences of `SchedulerTrace`
- `spec/01` L12 (R-SCOPE-01, informative), L37 (**R-CORE-08**, normative), L116 (**R-PLANNER-04**, normative), L334 (**R-ACTOR-07**, normative)
- `mod/01` §114, `mod/07` §39–40, §93, `mod/13` §44; `req/01-registry-part1` §15, §18, §327, §330
- `term/01-dictionary.md` — 81 canonical terms; **`SchedulerTrace`, `HostTrace`, `InitialState`, `UniqueMachineTrace` are not among them.** `LogicalTime` is T-28; `GlobalState` is present; the four theorem terms are absent from the dictionary, from the collision register, and from the non-conflation laws.

**VIOLATION**
Every occurrence of `SchedulerTrace` and `HostTrace` in the entire corpus is **inside the boxed formula or a restatement of it**. Neither term is ever:

- declared as a Rust type (no `struct SchedulerTrace`, no `struct HostTrace` — `grep` returns zero);
- given a field list, grammar, or canonical encoding;
- given an element type (is a `SchedulerTrace` a `Vec<ActorId>`? a `Vec<(LogicalTime, ActorId)>`? a decision log? a seed?);
- given a length/termination rule, an alignment rule to machine steps, or an equality relation;
- listed as a component of `GlobalState`, `Snapshot`, `WalRecord`, or `EventLog`.

`InitialState` is likewise never defined; the closest frozen artifact is `GlobalState` (L24156, L25535, L25863, L24157), and DET-009 shows `GlobalState` is *strictly smaller* than the state transitions read. `UniqueMachineTrace` is never defined either — in particular the specification never states **what equality on traces means** (event-list equality? state-digest sequence equality? final-state equality?), and R-HOST-05 ("replay validates trace, not just final state", L38278–38300) makes that distinction load-bearing without supplying it.

The consequence is not pedantic. Four normative `MUST` obligations (R-CORE-08, R-ACTOR-07, R-PLANNER-04, and by reference R-SCOPE-01/R-SCOPE-03) require conformance to a proposition whose subject and two parameters have no denotation. **An implementer cannot construct a `SchedulerTrace`, cannot serialize one, cannot compare two, and cannot record one for replay** — yet R-HOST-04 ("replay correspondence") and `mod/17` Track D ("global differential") are both specified as tests over exactly these objects.

Note also that the theorem appears in **three non-equivalent forms** in frozen text (§1): `InitialState + SchedulerTrace + HostTrace`, `MachineState + AcceptedPlan + SchedulerTrace + HostTrace` (L28426, L28575), and `Snapshot + EventLog + HostTrace + SchedulerTrace` (L26998). These differ in whether the plan is an input, and in whether the event log is an input or an output. If the `EventLog` is an *input* (L26998) while also being a `GlobalState` field written by transitions (L24160), the formula is circular. `spec/06` C-37 registers a nearby wording drift ("deterministic interleaving" vs FIFO lockstep) but does **not** register the undefinedness of the theorem's own terms — this is unregistered.

**NONDETERMINISM-ADMITTED**
Unbounded and unmeasurable. Because the parameters are undefined, *any* divergence between two runs can be attributed to "a different SchedulerTrace" or "a different HostTrace" post hoc. The theorem as frozen is **unfalsifiable**, which is the worst possible property for a claim whose entire purpose is to be mechanically checked. Every finding DET-002…DET-016 below is, formally, a candidate for that post-hoc absorption; they are filed as findings because a determinism claim that can absorb `HashMap` iteration order into "the scheduler trace was different" is not a determinism claim.

**EXPECTED-INVARIANT**
DT must be stated over defined objects:
- `SchedulerTrace := Vec<SchedulerDecision>` with `SchedulerDecision` frozen (at minimum `{ step: StepIndex, actor: ActorId }`), a canonical encoding, and an alignment rule to machine steps (one decision per scheduler turn).
- `HostTrace := Vec<EffectReceipt>` **ordered**, consumed by cursor, with the R-HOST-03 identity checks (id, effect digest, and per R-HOST-06 result digest) as admission conditions — i.e. exactly the L34498 `ReplayHost` shape, not the L24011 `HashMap` shape (DET-005).
- `InitialState := GlobalState ⊎ KernelAuthorityImage` (DET-009), with R-PERSIST-07's durable authority lattice included by construction.
- `UniqueMachineTrace` equality defined as **pointwise equality of the canonical state-digest sequence and the canonical event-envelope sequence** — which presupposes DET-002 and DET-007 are closed.

**REMEDIATION**
1. Freeze the four definitions as a new normative subsection of `spec/01` S-02 (adjacent to R-CORE-08), with `term/` entries T-82…T-85 and non-conflation laws separating `SchedulerTrace` (an input the machine *consumes*) from `EventLog` (an output the machine *produces*) — the L26998 form conflates them.
2. Pick **one** form of the theorem. Recommend `InitialState + SchedulerTrace + HostTrace ⇒ UniqueMachineTrace` with `AcceptedPlan` folded into `InitialState` (the L28426 form then becomes a corollary, not a competitor), and record L26998/L28426/L28575 as SUPERSEDED — quoted, not deleted, per R-SCOPE-03.
3. Register the theorem's three-way variance as a new `C-98` row in `spec/06`, and the undefinedness as `U-35` in `spec/09` (blocking: it gates Track A, Track D, R-HOST-03/04/05, and R-REF-01).
4. Add the four terms to `term/` and re-run `python3 term/_check.py`.

**VERIFICATION**
- A `SchedulerTrace` round-trip golden vector: encode → decode → byte-identical.
- Trace-equality conformance: two runs from identical `(InitialState, SchedulerTrace, HostTrace)` must produce byte-identical digest sequences, and the harness must *fail* if `UniqueMachineTrace` equality is implemented as final-state-only (this is the R-HOST-05 obligation made testable).
- Mutation **M037** "replay compares final state only, not trace" — must be killed.
- Conformance tag: `DETERMINISM-THEOREM-WELL-FORMED`.

---

### DET-002 — CRITICAL — Canonical encoding is frozen for ~10% of the state the theorem ranges over

**LOCATION**
- `spec/09` **U-02** — "15A freezes byte-level grammar **only** for the data-value domain (`Value`, `Symbol`, `CapRef`, `ActorId`, `EffectId`)… **No byte-level encoding for any of these is specified**" for `Expr`, `Frame`, `Environment`, `Constraint`, `Authority`/`AuthorityNode`, `CapabilityContext`, `Budget`, `Mailbox`, `SchedulerState`, `GlobalState`
- `Red-on-Rust.md` L27699–27708 — `impl CanonicalSerialize for GlobalState` is a **comment-only sketch**: "// 4. Serialize actors (ordered by ActorId to ensure determinism) … // ... strictly ordered, no hash-map iteration randomness". There is no body.
- L27701 `fn state_digest(&self) -> StateDigest { StateDigest(sha256(&self.canonical_serialize())) }` — the digest is defined over a function that has no frozen definition
- `spec/01` R-PERSIST-05 (state digest), R-RECOV-03 step (3) (decode snapshot via 15A), R-CORE-08 (determinism)

**VIOLATION**
DT's conclusion is trace equality, and R-HOST-05 requires trace comparison rather than final-state comparison. Both are operationalized through `StateDigest = sha256(canonical_serialize(GlobalState))`. But `canonical_serialize` for `GlobalState` **does not exist as a specification** — only as a six-line comment listing what one would serialize, in an order that is itself only partly stated ("ordered by ActorId" for actors; nothing for `Environment`, `Mailbox`, `CapabilityContext`, continuation frames, or the heap).

This is the difference between "the spec forbids nondeterminism" and "the spec determines the bytes." The frozen text does the former (L27987, L28309, L28738: "`BTreeMap`, never unordered-map iteration"; "Iteration order of hash-based collections is strictly forbidden") and not the latter. Two conforming implementations that both obey every prohibition will still produce **different `StateDigest` values** for the same logical state, because field order, `Option`/`Result` tag choice for machine-only types, `Expr` node discriminants, and `Environment` key ordering are all unfrozen. DT's conclusion is then untestable *between implementations* — which is precisely the differential-testing contract R-REF-01/R-REF-03 depends on.

The heap is the sharpest case. `GenerationalArena<Value>` is a frozen `ActorState` field (L25549, L24188 area) and L10862 defines it as `pub type GenerationalArena<T> = Vec<T>; // Placeholder for slotmap`. Whether the canonical form of a heap is the slot vector *including tombstones* (allocator-order-dependent — DET-010) or a reachability-ordered traversal (allocator-independent) changes every digest in the system, and is unstated.

**NONDETERMINISM-ADMITTED**
Cross-implementation and cross-version digest divergence for identical logical state. Concretely: differential testing (R-REF-01/05) cannot compare states, recovery cannot verify step (11) "compute final state digest vs trailing checkpoint", and R-PERSIST-08's chained checksums authenticate bytes whose meaning is implementation-private.

**EXPECTED-INVARIANT**
`Canonical(x) = Canonical(y) ⟺ x = y` (L28318) must hold **across implementations**, not within one. This requires a total frozen encoding for every reachable component of `InitialState`.

**REMEDIATION**
1. Close U-02 by freezing type tags and payload layouts for the ten named machine types, extending the 15A envelope (R-CANON-02) rather than inventing a second format (the L32022 rule).
2. Freeze the heap canonicalization rule explicitly: recommend **reachability-ordered traversal from roots (env, continuation frames, mailbox), with tombstones excluded** — this makes the digest allocator-independent and closes DET-010's digest half.
3. Freeze `Environment` ordering. Note that the L10860 `HashMap<String, Value>` (DET-003) must first become a `BTreeMap<Symbol, Value>`; ordering is then "ascending `Symbol`", not "lexicographic `String`" — the two differ whenever interning order differs from byte order, and `term/` T-?? does not fix which.
4. Golden vectors (R-CANON-11) for a non-trivial `GlobalState`: two actors, a non-empty mailbox, a two-frame continuation, one live capability.

**VERIFICATION**
- Cross-implementation digest equality: production and reference must produce byte-identical `StateDigest` for a shared corpus of logical states (this is the M1 gate "canonical bytes deterministic" made real).
- Mutation **M038** "serialize `GlobalState` fields in declaration order instead of frozen order" — must be killed.
- Conformance tag: `CANONICAL-MACHINE-STATE-TOTAL`.

---

### DET-003 — HIGH — `HashMap` in frozen operative machine state (unordered map iteration)

**LOCATION**
- L10860 `pub type Environment = HashMap<String, Value>;`
- L10902 / L10382 `pub type ActorTable = HashMap<ActorId, ActorState>;`
- L10376 `pub actors: std::collections::HashMap<ActorId, ActorState>,`
- L6502, L6520, L6537 `pub ops: std::collections::HashMap<Op, OpAuthority<S, Q, R, L>>,` — **inside `Authority`**, the object `authorizes` iterates
- L1195 `cap_bindings: HashMap<CapRef, OsAuthority>`
- L5432 `children: HashMap<DefaultKey, Vec<DefaultKey>>` — the revocation lineage graph, traversed by `revoke_recursive` (L5441)
- L928 / L5431 / L6697 `revocation_set: HashSet<...>`
- L3592–3594, L4980–4982, L11573–11574 `pub ops: HashSet<Op>, pub scope: HashSet<Target>, pub params: HashSet<Predicate>`
- L24012 `pub recorded_receipts: HashMap<EffectId, EffectReceipt>` (see DET-005)
- **Contrast (the fix, also frozen):** L24157/L25536/L25863 `pub actors: BTreeMap<ActorId, ActorState>`; L19604 `pub operations: BTreeMap<Op, RefOperationAuthority>`; L9521 "The scheduler should not depend on Rust's `HashMap` iteration order."

**VIOLATION**
The specification contains **both** the prohibition and the violation, frozen, with no supersession record. L28738 states "Iteration order of hash-based collections is strictly forbidden" and L27987 "`BTreeMap`, never unordered-map iteration" — yet the operative struct definitions an implementer will copy (the Phase-13 blueprint at L10855–10940, the capability kernel at L5425–5445, the `Authority` product lattice at L3590–3596) use `HashMap`/`HashSet` throughout.

Three of these are *semantically* load-bearing, not merely representational:

1. **`Environment = HashMap<String, Value>`** — the CEK environment. It is part of `EvalState`, part of `ActorState`, part of the snapshot, part of the digest. Its iteration order affects serialization (DET-002) and, if any rule enumerates bindings, evaluation.
2. **`children: HashMap<DefaultKey, Vec<DefaultKey>>` with `revoke_recursive`** — `revoke_recursive` iterates `children.remove(&key)` and recurses. The *set* of revoked capabilities is order-independent, but the **event order** is not: if each revocation emits a `CapabilityRevoked` WAL record (now mandatory under R-PERSIST-07), the WAL byte sequence — and therefore R-PERSIST-08's chained checksum, and therefore the recovery digest — depends on `HashMap` iteration order. This is a direct DT violation on a durable path, and it is unregistered.
3. **`Authority.ops: HashMap<Op, OpAuthority>` / `scope: HashSet<Target>`** — `derive` (L6520) builds `derived_ops` by iterating. If derivation ever short-circuits, faults on the first inadmissible entry (R-CAP-10 now requires a fault, not identity), or emits per-op events, *which* fault or event is produced depends on iteration order. R-CAP-10 froze the fault; it did not freeze the order in which candidate constraints are examined.

`spec/06` does not carry a row for the `HashMap`-in-operative-structs conflict; `spec/03` R-CANON-01/R-HOST-03 gesture at "no unordered map" but bind only serialization and the replay host, not `Environment`, not `Authority`, not the revocation lineage.

**NONDETERMINISM-ADMITTED**
Per-process (DET-004) variation in: snapshot bytes, `StateDigest`, WAL record order on revocation cascades, and — where derivation is fallible — *which* `Fault` a program observes. The last is semantic in the strongest sense: two runs of the same program on the same inputs return different faults.

**EXPECTED-INVARIANT**
No hash-ordered container may appear in `GlobalState`, `ActorState`, `Authority`, `AuthorityNode`, the revocation structures, or anything reachable from them. Ordered containers only, with the ordering key frozen. Hash containers are permissible **only** as non-semantic acceleration indices that are (a) never iterated, (b) never serialized, and (c) reconstructible from ordered state — and that permission must be written down, since an implementer optimizing a lookup will otherwise reintroduce the defect legally.

**REMEDIATION**
1. Sweep every frozen struct: `HashMap → BTreeMap`, `HashSet → BTreeSet`, in `Environment` (also `String → Symbol`, see DET-002 rem. 3), `ActorTable`, `Authority.ops/scope/params`, `cap_bindings`, `children`, `revocation_set`. Record the `HashMap` forms as SUPERSEDED, quoted.
2. Freeze `revoke_recursive` as a **deterministic traversal**: children in ascending `CapRef` order, pre-order, emitting `CapabilityRevoked` in that exact order — and state that the WAL sequence is part of the observable trace.
3. Freeze the "acceleration index" carve-out with its three conditions, so that the prohibition survives optimization.
4. Structural enforcement (the R-REPO-03 / R-CORE-12 mechanism class): workspace clippy `disallowed-types` denying `std::collections::HashMap`/`HashSet` in `ror-core`, `ror-kernel`, `ror-runtime`, `ror-persistence`. A lint is worth more than a sentence here, because the defect is a one-character edit away at all times.

**VERIFICATION**
- Mutation **M039** "`BTreeMap` → `HashMap` in `GlobalState.actors`" and **M040** "`revoke_recursive` iterates children in map order" — both must be killed.
- Property test: for a fixed logical state, `state_digest` is invariant across 1,000 process launches (this is the DET-004 test; it kills both findings at once).
- Revocation-cascade WAL determinism: a 50-node lineage revoked at the root produces a byte-identical WAL segment across runs and across implementations.

---

### DET-004 — HIGH — Hash randomization: `RandomState` is a per-process entropy input

**LOCATION**
Every location in DET-003, plus L247 `dashmap::DashSet` and L334 `dashmap` (DET-014).

**VIOLATION**
This is filed separately from DET-003 because the mechanism is different and the mitigation is different. Rust's `std::collections::HashMap` defaults to `RandomState`, which seeds SipHash-1-3 **from the OS RNG once per process**. Iteration order is therefore not merely "unspecified" (a portability problem) but **randomized per process** (a determinism problem): the same binary, same inputs, same machine, two launches ⇒ different order.

The specification never names this mechanism. It says "no hash-map iteration randomness" (L27707) and "Iteration order of hash-based collections is strictly forbidden" (L28738), which an implementer can satisfy in the letter by switching to a fixed-seed hasher (`FxHashMap`, `BTreeMap`-free `HashMap<_, _, BuildHasherDefault<...>>`) while leaving iteration order **platform- and capacity-dependent** — deterministic within a build, divergent across builds and across `usize` widths (DET-011). That reading passes the frozen prohibition and still breaks DT across the production/reference pair, which is exactly the pair R-REF-01 compares.

Consequence for the audit's central question: `HostTrace` and `SchedulerTrace` are supposed to be the *only* external inputs. `RandomState` is a fourth, unnamed input, drawn from the OS at process start, that reaches the state digest through DET-003's containers. It is invisible in every trace the specification defines, so a divergence it causes is **unattributable and unreproducible** — replay of the recorded traces will not reproduce it.

**NONDETERMINISM-ADMITTED**
Per-process OS entropy → iteration order → serialized bytes → `StateDigest` → replay/differential mismatch, with no recorded input that explains the mismatch.

**EXPECTED-INVARIANT**
The machine must have **no dependence on any hasher's seed**. Stronger than "don't iterate hash maps": no hash container in semantic state at all (DET-003), and no digest, ordering, or control-flow decision derived from `Hash`. Note that `#[derive(Hash)]` appears on `CapRef` (L11876), `StateDigest`, `SnapshotVersion`, `ResultDigest` (L33871–33877) — deriving `Hash` is harmless, *using* it for ordering is not; the specification should say so.

**REMEDIATION**
1. Fold into DET-003's container sweep and clippy denial.
2. Add one normative sentence naming the mechanism, because the current prohibition is mechanically ambiguous: "No machine state, event order, digest, or control-flow decision may depend on the output of `Hash`/`Hasher`, on any hasher seed, or on hash-container capacity. Substituting a fixed-seed hasher does NOT satisfy this rule."
3. CI: run the full determinism suite twice per job with `ASLR` and process identity varying, and compare digests — the cheapest possible detector for this whole finding class.

**VERIFICATION**
- The 1,000-launch digest-invariance property test (shared with DET-003).
- Mutation **M041** "replace `BTreeMap` with fixed-seed `HashMap`" — must be killed, proving the test detects the *letter-conforming* variant and not just the obvious one.
- Conformance tag: `NO-HASH-SEED-DEPENDENCE`.

---

### DET-005 — HIGH — `ReplayHost` has three incompatible frozen shapes; two of them break trace ordering

**LOCATION**
Six frozen declarations in five incompatible shapes, no supersession record between them:

| Line | Shape | Ordering property |
|---|---|---|
| L1234 | `{ cursor: usize, trace: Vec<Result<Value, HostFault>> }` | ordered, **no identity check** — "Optional: we can also assert that the replayed effect matches" |
| L9783 | `{ trace: ReplayTrace }` — `ReplayTrace` never defined | unknown |
| L10541 | `{ trace: VecDeque<EffectReceipt> }`, `pop_front` | ordered, id + effect-digest checked |
| L22339 | `{ receipts: ReceiptLog }` — "lookup recorded receipt", `ReceiptLog` never defined | **unordered lookup** |
| L24011 | `{ recorded_receipts: HashMap<EffectId, EffectReceipt>, cursor: usize }` | **`HashMap` lookup**; `cursor` present but **never read** in the frozen body; identity check demoted to "Optional but recommended" |
| L34498 | `{ trace: Vec<EffectReceipt>, cursor: usize }` | ordered + cursor + `ReplayCorruption` on id mismatch — **the only shape satisfying R-HOST-03** |

- Governing obligation: `spec/01` R-HOST-03 "Ordered ReplayHost; ID+digest per entry; no unordered map" (`spec/03` L123, provenance L25972–25996, L37985–38000). L34498 states the rule in prose: "The replay host should consume an **ordered effect trace**, not merely perform a map lookup."

**VIOLATION**
`HostTrace` is one of DT's two parameters. Its only concrete realization in frozen text is `ReplayHost`, and that realization is frozen **six times in five mutually incompatible shapes**, two of which (L22339, L24011) are explicitly the "merely perform a map lookup" pattern that L34498 forbids and R-HOST-03 outlaws. The L24011 form is the most dangerous because it is the *latest* full Phase-12 code block and it carries a vestigial `cursor: usize` field — an implementer reading it sees a cursor, assumes ordering, and gets `HashMap` lookup semantics.

The semantic difference is not cosmetic. Under map lookup:
- **Order is unchecked.** A machine that issues effects in a different order than recorded still replays "successfully", because each lookup finds its receipt. The replay therefore *fails to detect* the very nondeterminism it exists to detect. R-HOST-05 ("replay validates trace, not just final state") is unimplementable on this shape.
- **Duplicate/absent handling diverges.** `Vec`+cursor exhausts (`ReplayTraceExhausted`); a map re-serves the same receipt indefinitely for a repeated `EffectId`, silently converting a replay-detectable divergence into a clean run.
- **`HashMap` reintroduces DET-003/DET-004** on the replay path specifically, if the receipts are ever iterated or digested.

Note the interaction with the fault taxonomy: L1234/L10541 return `HostFault::ReplayTraceExhausted`/`ReplayIdMismatch`/`ReplayDigestMismatch`, L22339 says `ReplayCorruption`, and `spec/09` U-14 records these as **six undeclared variants on the frozen replay path, BLOCKING**. So the object DT is parameterized on cannot currently be given a well-typed error channel either. R-CORE-13 froze the enumeration; it did not pick the container.

**NONDETERMINISM-ADMITTED**
(a) Replay accepts executions whose effect order differs from the recording — a false negative in the primary determinism detector; (b) implementation-choice divergence in whether a given divergent run is detected at all.

**EXPECTED-INVARIANT**
`HostTrace` is an **ordered sequence consumed by a monotonic cursor**, with per-entry admission `receipt.id = request.id ∧ receipt.effect_digest = digest(request.effect) ∧ ResultDigest(receipt.result) = receipt.result_digest` (the third conjunct from R-HOST-06), and exhaustion is a declared fault. Order mismatch is `ReplayCorruption`, never a successful lookup.

**REMEDIATION**
1. Declare **L34498 the sole governing shape**, extended with R-HOST-06's result-digest conjunct. Record L1234, L9783, L10541, L22339, **L24011** as SUPERSEDED — quoted, not deleted. The `HashMap` field and the vestigial `cursor` in L24011 must be explicitly called out, because that block is the one most likely to be copied.
2. Define `HostTrace` as this type in the DET-001 definition set: `HostTrace := Vec<EffectReceipt>` + cursor discipline. Define `ReplayTrace` (L9783) and `ReceiptLog` (L22339) as SUPERSEDED aliases or delete-with-quote.
3. Register as a new `C-99` row in `spec/06` (MAJOR: two frozen shapes contradict a normative `MUST`), and as an `X-87` collision in `term/` (one name, six denotations).

**VERIFICATION**
- **Order-sensitivity test (the decisive one):** record a trace of ≥ 3 effects; replay a machine that issues them in a permuted order. The correct implementation yields `ReplayCorruption` at the first mismatch. **A map-lookup implementation completes successfully** — so this test distinguishes the shapes, and its absence is why the defect survived.
- Mutation **M042** "`ReplayHost` looks up by `EffectId` instead of consuming in order" — must be killed.
- Exhaustion, duplicate-id, and short-trace cases each map to a declared R-CORE-13 variant.
- Conformance tag: `HOSTTRACE-ORDERED-CURSOR`.

---

### DET-006 — HIGH — Unix-timestamp `Lifetime` is compared against `LogicalTime` inside the authorization gate

**LOCATION**
- L3571–3573 / L4959–4961 / L5403–5405 `pub struct Lifetime { pub start: u64, // Unix timestamp \n pub end: u64, // Unix timestamp }`
- L5244 "A time interval during which the capability is valid. $t_{start}, t_{end} \in \mathbb{N}$ (e.g., **Unix timestamps**)."
- L3577 `pub fn contains(&self, time: u64) -> bool { time >= self.start && time <= self.end }`
- L11881–11889 — the frozen pure authorization predicate:
  ```rust
  pub fn authorizes(auth: &Authority, effect: &Effect, t: LogicalTime) -> bool {
      auth.ops.contains(&effect.op)
          && ... && auth.lifetime.contains(t)   // Lifetime is Unix; t is LogicalTime
  }
  ```
- L5399 `pub max_duration: Duration,` in `ResourceLimits` — `std::time::Duration`, a wall-clock quantity, inside a resource ceiling
- **Contradicted by:** L6437 "Time $t$ is not fetched from the host OS. It is an explicit component of the machine state"; `spec/01` **R-CAP-09** "Wall-clock time MUST NOT be used as semantic machine state"; `term/` T-28 "never fetched from the host OS, and never wall-clock"; R-CLAIM-02 "Never: use wall-clock time for deterministic semantics"

**VIOLATION**
`authorizes` is *the* authorization predicate — R-CAP-06's five conjuncts, the thing gate 6 computes. Its fifth conjunct compares a `LogicalTime` (a `u64` counter starting near 0 and advancing by unfrozen `δ_t`, DET-008) against an interval documented three times as **Unix timestamps** (values near 1.7 × 10⁹). These are not the same quantity, and the frozen text asserts both readings.

Two failure modes, and they are opposite:

1. **If `Lifetime` really is Unix time**, then either the machine fetches wall-clock to populate it (direct R-CAP-09 violation; the capability's validity then depends on when the machine is *run*, so replay of a recorded trace at a later date yields a different authorization outcome — DT broken on the security gate), or it never does, and every capability with a realistic `start` is **permanently invalid** because `LogicalTime(k) < 1.7e9` for all realistic `k`. The latter is a silent total-denial bug that no property test over small `LogicalTime` values would catch, since such tests would use small `Lifetime` bounds too.
2. **If `Lifetime` is logical time** (the R-CAP-09-compliant reading), then the three "Unix timestamp" comments and the `Duration` field are wrong, and an implementer following the comments — which are more concrete than the prose — imports wall-clock into the TCB.

Either way the *same* frozen corpus authorizes two implementations that disagree on whether a given effect is permitted. That is a semantic divergence at the authority boundary, produced by a time-source ambiguity. `spec/06` has no row for it; `term/` T-27/T-28 correctly define `Deadline` and `LogicalTime` as never-wall-clock but do not register that `Lifetime` — a *different* frozen temporal type — says the opposite. This is unregistered.

Note that this is the *only* wall-clock ingress the audit found in operative semantic text. The specification is otherwise disciplined about time: L21953, L24260, L36971 all forbid wall-clock timestamps, and R-BUDGET-09 was careful to phrase the stalled-effect timeout as "a `Pending` effect whose deadline `W` expires (or a frozen per-effect **logical** timeout elapses) … machine state only, no wall clock (R-CAP-09), determinism preserved." That is exactly right, and it makes the surviving `Lifetime` defect more conspicuous rather than less.

**NONDETERMINISM-ADMITTED**
Replay-time-dependent authorization: the same `(InitialState, SchedulerTrace, HostTrace)` yields `Authorized` on the original run and `¬Authorized` on a replay performed later (or on a machine whose clock differs), or vice versa. Under DT this is impossible; under the frozen text it is a legal implementation.

**EXPECTED-INVARIANT**
`Lifetime.start`, `Lifetime.end`, `Deadline.W`, and every temporal comparison in `authorizes` are `LogicalTime`. No `std::time` type appears in any machine-state struct. Wall-clock may exist **only** in host-side logging and operator-facing metadata, and must be structurally unable to reach a machine value (the R-EFFECT-08 admission rule already provides the mechanism for the receipt channel).

**REMEDIATION**
1. Retype: `pub struct Lifetime { pub start: LogicalTime, pub end: LogicalTime }`. Strike the three "Unix timestamp" comments and L5244's parenthetical, recording them as SUPERSEDED (quoted).
2. Remove `max_duration: Duration` from `ResourceLimits`, or retype as logical-tick budget `D` — note the frozen cost algebra already has `D` as a *consumable* duration (L7130, L7303) whose operational semantics L7706 flags as undefined ("Duration `D` currently has no operational semantics"), so this should be resolved *with* that open item rather than independently.
3. Register `C-100` (MAJOR: wall-clock in the authorization predicate, contradicting R-CAP-09/R-CLAIM-02) and a `term/` entry for `Lifetime` with `FORBIDDEN_VARIANTS` noting the Unix reading.
4. Structural enforcement: clippy `disallowed-types` on `std::time::SystemTime`, `Instant`, `Duration` in all machine crates. This is the same mechanism class as R-CORE-12's `unwrap` denial and should be added to the same config.

**VERIFICATION**
- **Clock-shift replay test:** replay a recorded trace with the host clock advanced by 10 years; every authorization decision and the full trace digest must be identical. This test is cheap and would fail today on reading (1).
- Mutation **M043** "`Lifetime.contains` uses `SystemTime::now()`" — must be killed.
- Static check: zero `std::time` imports in `ror-core`/`ror-kernel`/`ror-runtime`/`ror-persistence`.
- Conformance tag: `NO-WALLCLOCK-IN-AUTHORIZATION`.

---

### DET-007 — HIGH — Two complete canonical grammars coexist; digest identity is grammar-relative

**LOCATION**
- L28309 (LE) "1. Integers: Explicit widths (u32, u64) and **Little-Endian (LE)** byte order."
- L29123 (BE) "`BTreeMap<K, V>`: Payload is `[Count: u32 (**Big-Endian**)]`…"; L29925/L29958 `TAG_BTREEMAP = 0x41`
- L30575, L33087–33154 — the 15A BE envelope, tags `0x00/0x20/0x30/0x40/0x41`
- L27703 "// 2. Serialize logical_time (u64 **LE**)" — inside the `GlobalState` sketch (DET-002)
- L29815 — the source's own note that a `BTreeMap<u32, Value>` golden vector "needs to be regenerated from the current envelope grammar rather than adapted from the previous LE/older-format vector"
- Resolution attempted: `spec/01` **R-CANON-13** "One canonical grammar: 15A BE envelope sole; LE revised grammar superseded in-source"; `spec/09` **U-12/U-?? (L114)** still records the open decision "confirm that the big-endian `u8`-tag form governs and that the L28298 doc comment is superseded"; cross-ref SEC-017, `term/` X-50/X-54

**VIOLATION**
Registered, and partially remediated by the R-CANON-13 addendum — but filed here because its *determinism* consequence is distinct from the security consequence SEC-017 records, and because the remediation is incomplete on the exact point this audit is about.

R-CANON-13 declares BE sole. But `spec/09` L114 still lists the confirmation as an **open decision**, and the LE statement survives at L28309 **inside an API doc comment**, which — as `spec/09` notes — "an implementer will read first." More importantly for DT: the `GlobalState` serialization sketch at L27703, which is the *only* text describing how the state digest is computed, says **LE**. So the one place the grammar meets the determinism theorem still specifies the superseded endianness, and DET-002 means there is no complete BE replacement for it to be superseded *by*.

DT's conclusion, operationalized, is equality of digest sequences. Every digest in the system — `EffectDigest`, `StateDigest`, `ResultDigest`, WAL frame checksums (now chained, R-PERSIST-08), snapshot commit records, the R-HOST-06 result-digest conjunct — is a hash of canonical bytes. A grammar ambiguity is therefore not a serialization detail; it is a **fork in the meaning of "unique trace."** Two conforming implementations produce disjoint digest universes, and the R-EFFECT-06 causal validation (`receipt.effect_digest = digest(request.effect)`) fails across them.

**NONDETERMINISM-ADMITTED**
Implementation-choice divergence in every digest, hence in replay admission, differential comparison, WAL chain validation, and recovery step (11).

**EXPECTED-INVARIANT**
Exactly one grammar reachable from any frozen text, with the digest definition stated over it.

**REMEDIATION**
1. Close the `spec/09` L114 decision affirmatively (BE governs) and mark it resolved by R-CANON-13, so the open-decision register stops contradicting the normative layer.
2. Correct **L27703** specifically — the `GlobalState` sketch must say BE, and must be replaced wholesale when DET-002 is closed. These two findings should be remediated together; fixing endianness in a sketch that has no body is not progress.
3. Bidirectional negative golden vectors: LE-encoded input must be **rejected**, not silently misparsed (R-CANON-13 already requires this; the vectors are the evidence).

**VERIFICATION**
- Mutation **M031** (already registered under R-CANON-13) plus **M044** "`GlobalState` digest serializes `logical_time` LE" — must be killed.
- Cross-implementation digest equality (shared with DET-002).

---

### DET-008 — MEDIUM — `δ_t` is unfrozen: `LogicalTime` advances on an implementation-chosen schedule

**LOCATION**
- `spec/09` **U-07** — "the rule is `δ_t(pure) = 0`, `δ_t(host/scheduler) > 0`, validity `t + δ_t ≤ W`. The *actual* delta values (is each scheduler turn `+1`? is each host round-trip `+1` or more? does spawning advance time?) are not enumerated in any frozen table."
- `term/` T-28 NOTE — "The per-transition `δ_t` values are not frozen (U-07), so `LogicalTime` is defined but its advancement schedule is not."
- `spec/01` R-BUDGET-06; R-CAP-09; L7141 `t ≤ W`; L11886 `auth.lifetime.contains(t)`
- U-07's own remark: an "any consistent assignment is conformant" resolution "would need to be stated, **since it changes what 'deterministic' means for deadlines**."

**VIOLATION**
`LogicalTime` is the specification's answer to wall-clock nondeterminism, and it is a good answer — DET-017/DET-018 and the discipline at L21953/L24260/L36971 show the design is serious. But a clock is only deterministic if its *advancement rule* is. Here it is not.

`t` is read by two decision procedures that gate execution: `t ≤ W` (deadline validity, gate 8) and `auth.lifetime.contains(t)` (authorization, gate 6). If implementation A charges `δ_t = 1` per host round-trip and implementation B charges `δ_t = 3`, then for a capability expiring at `W` there exist programs where A completes and B faults `DeadlineExceeded`. Both conform. DT is violated **between conforming implementations**, which is precisely the domain R-REF-01 differential testing operates in — and it will surface there as an unexplained mismatch, which R-TEST's release gate forbids shipping without adjudication, with no frozen fact to adjudicate against.

This also interacts with R-BUDGET-09, the escrow-totality addendum, which now makes deadline expiry *load-bearing for liveness*: "a `Pending` effect whose deadline `W` expires (or a frozen per-effect logical timeout elapses) transitions to `Indeterminate` + reconciliation." Whether and when that transition fires is now a function of the unfrozen `δ_t`. The addendum correctly avoided wall-clock; it inherited an unfrozen logical clock instead.

**NONDETERMINISM-ADMITTED**
Implementation-choice divergence in deadline and lifetime outcomes, and in the timing of escrow reconciliation — i.e. in *which faults occur* and *when budget returns*.

**EXPECTED-INVARIANT**
A frozen total function `δ_t : TransitionKind → ℕ`, with `δ_t(pure) = 0`, so that `t` at every step is a function of the step index and the transition sequence alone.

**REMEDIATION**
1. Freeze the table. Minimal defensible assignment: `δ_t = 0` for all pure CEK transitions; `δ_t = 1` per scheduler turn; `δ_t = 1` per host round-trip (issuance→receipt); `δ_t = 0` for spawn/send/receive (they are machine transitions, and charging them makes time a function of message volume, which couples deadlines to unrelated program structure). Whatever is chosen, **enumerate every transition kind** — a partial table reopens the gap.
2. Do **not** take the "any consistent assignment" escape without also weakening DT's stated scope, per U-07's own warning. Recommend against it: it converts DT from a cross-implementation property into a per-implementation one, silently invalidating R-REF-01.
3. Close U-07; note the R-BUDGET-09 dependency explicitly so the escrow-liveness argument rests on a frozen clock.

**VERIFICATION**
- Differential: production and reference must agree on `logical_time` after every step, not merely at the end (a `LogicalTime` column in the trace comparison).
- Boundary suite: programs whose deadline outcome flips under `δ_t ∈ {1,2,3}` must be in the corpus, and must produce identical results.
- Mutation **M045** "charge `δ_t = 1` on a pure transition" — must be killed.

---

### DET-009 — MEDIUM — Hidden global state: the kernel authority image is outside `InitialState`

**LOCATION**
- L24156–24168 / L25535–25542 / L25863 — the frozen `GlobalState`: `actors`, `logical_time`, `runnable`, `event_log`, `next_effect_id`, `next_actor_id`, (`scheduler`). **No kernel, no arena, no revocation set.**
- L5430–5432 / L6697 — `CapabilityKernel { arena: SlotMap<DefaultKey, Authority>, revocation_set: HashSet<...>, children: HashMap<...> }` — a separate, kernel-private, mutable object
- L5312–5318 — "Revocation … changes the **global state** $\mathcal{R}$" (a second, differently-named global)
- L247 — "a **global** or context-local Revocation Set $\mathcal{R}$"; L471 — the source's own objection: "I would not use a global revocation set … it introduces a potentially **global mutable security structure**"
- L10861 `pub type CapabilityContext = (); // Maps to CapabilityKernel references` — the per-actor possession set is the unit type
- Partial remediation: `spec/01` **R-PERSIST-07** (durable authority lattice — snapshots MUST contain it; cross-ref SEC-004)

**VIOLATION**
DT's antecedent is `InitialState`. The only frozen candidate is `GlobalState`, and `GlobalState` **does not contain the authority lattice** that gate 6 reads on every effect request. Two runs from identical `GlobalState`, identical `SchedulerTrace`, identical `HostTrace` can therefore differ in every authorization outcome, because a state component the theorem does not name differs.

R-PERSIST-07 closes this for *persistence* (snapshots must carry it, recovery must reconstruct it) — that addendum is correct and necessary. But it does not amend `GlobalState`, and DT is not a statement about snapshots; it is a statement about `InitialState`. The gap between "the snapshot contains X" and "the theorem's antecedent contains X" is exactly where an implementer will place a kernel that is constructed at startup from configuration rather than from the recorded initial state.

Compounding: `CapabilityContext = ()`. If per-actor possession is the unit type, then possession is not in `ActorState`, hence not in `GlobalState`, hence not in `InitialState`. R-CORE-11 has since frozen possession as a conjunct of `Authorized(holder, c, E, t)` (SEC-002/SEC-016 remediation) — so the *predicate* now reads a per-actor set that the *state definition* still declares to be `()`. The determinism consequence is that the input to authorization is not fully enumerated anywhere.

**NONDETERMINISM-ADMITTED**
Divergence in authorization from an unnamed initial input; and, on the replay path, the possibility that a replayed machine reconstructs a *different* authority lattice than the recorded run had, while every named input matches.

**EXPECTED-INVARIANT**
`InitialState := GlobalState`, and `GlobalState` is **closed**: every input any transition reads is a field of it. Concretely add `kernel: CapabilityKernelImage { arena, revocation_set, children/lineage, generation counters }`, and make `CapabilityContext` a real type held per actor.

**REMEDIATION**
1. Amend the frozen `GlobalState` with the kernel image; record the six-field version as SUPERSEDED (quoted). This is additive and consistent with R-PERSIST-07 — indeed R-PERSIST-07 is unimplementable without it, since one cannot snapshot a field that does not exist.
2. Delete-with-quote the `CapabilityContext = ()` sketch (already flagged by SEC-002 rem. 2 — this audit adds that it is a *determinism* defect, not only an authority one).
3. State the closure property normatively: "No transition may read state outside `GlobalState`, `SchedulerTrace`, or `HostTrace`." This single sentence is the operational content of DT, and the specification currently never says it. **It is the sentence that turns DT from a slogan into an obligation**, and every finding in this audit is an instance of its absence.
4. Retire the "global revocation set $\mathcal{R}$" phrasing (L247, L5312–5318) in favour of the kernel-image field; two names for one mutable global is a `term/` collision.

**VERIFICATION**
- Closure audit: a test-only `GlobalState` clone must be sufficient to re-run any recorded trace bit-identically with a **freshly constructed, empty** process (no ambient kernel).
- Mutation **M046** "construct the kernel from config rather than from `InitialState`" — must be killed.
- Conformance tag: `INITIALSTATE-CLOSED`.

---

### DET-010 — MEDIUM — Allocator-dependent semantics: `CapRef` generations and arena slot reuse

**LOCATION**
- L11876–11879 / L10197–10199 `pub struct CapRef { index: u32, generation: u32 }`
- L926–927 `arena: slotmap::SlotMap<slotmap::DefaultKey, Authority>`; L5430; L3657; L5045
- L10862 `pub type GenerationalArena<T> = Vec<T>; // Placeholder for slotmap`
- L200, L213 — "the arena's generation counter will mismatch, causing an immediate, safe panic (or a structured `InvalidReference` error)"
- L5960–5975 — "A dedicated opaque generational identifier is safer"
- R-PERSIST-07 — recovery MUST reject "any CapRef … that does not resolve with **matching generation**"

**VIOLATION**
`CapRef` values are **observable machine state**: they are compared, stored in actor heaps, snapshotted, and (per R-PERSIST-07) reconstructed by recovery with generation matching. But the function that produces them — slot allocation — is **not specified**. `slotmap::SlotMap`'s free-list policy (which index is reused after a free, and how generations increment) is a library implementation detail, not a frozen rule; `GenerationalArena<T> = Vec<T>` has no free list at all and would allocate a *different* index sequence for the same program.

So `CapRef` identity depends on the allocator, and the allocator is unfrozen. Two conforming implementations running the same program produce different `CapRef` bit patterns for corresponding capabilities. Since `CapRef` is canonically encoded (tag `0x30`, R-CANON-05) and appears in snapshots and — per SEC-008 — in `EffectRequest.cap` in the log, the **state digest and the event trace differ**. DT is violated even though nothing "random" happened.

The same argument applies to `GenerationalArena<Value>` for actor heaps: heap slot indices are values inside `Value` references, and if the canonical form of a heap is the slot vector (DET-002 rem. 2), digests inherit allocator policy directly.

This is distinct from DET-003/DET-004: no hashing is involved, and it is deterministic *within* an implementation. It is a **cross-implementation** and cross-version determinism defect, which is the axis differential testing (R-REF-01, R-REF-03 "independently structured") is specifically designed to exercise — and the reference model, being deliberately "small, direct, explicit," will certainly allocate differently from a `slotmap`-based production kernel. This mismatch is therefore not hypothetical; it is scheduled to occur on the first differential run.

**NONDETERMINISM-ADMITTED**
Allocator-policy-dependent identifier values → divergent canonical bytes, digests, and event traces across implementations and across dependency versions.

**EXPECTED-INVARIANT**
Either (a) `CapRef` allocation is a frozen deterministic function of machine state — monotonic `index` from a counter in `GlobalState` (the DET-015 pattern already used for `ActorId`/`EffectId`), with `generation` incremented per slot on reuse under a frozen reuse rule (recommend: **lowest free index first**, or **never reuse**, the latter being simplest and bounded by `u32`); or (b) `CapRef` is never canonically serialized and never observable, which contradicts R-CANON-05 and R-PERSIST-07 and is therefore not available.
Correspondingly, heap canonicalization must be reachability-ordered (DET-002 rem. 2) so that heap digests are allocator-independent regardless.

**REMEDIATION**
1. Freeze the allocation rule and the reuse rule in `spec/01` S-10, alongside R-CAP-07. State it as a function: `alloc(arena) → (index, generation)` with no library dependence.
2. Note explicitly that `slotmap` may be *used* only if its policy is pinned and asserted by test; otherwise implement the arena.
3. Delete-with-quote `pub type GenerationalArena<T> = Vec<T>` or mark it non-normative sketch (it silently has different semantics from every other reading).
4. Fold the heap canonicalization rule into the U-02 closure (DET-002).

**VERIFICATION**
- Cross-implementation `CapRef` sequence equality: production and reference must mint identical `CapRef` values for a shared derive/revoke script.
- Reuse-after-revoke property: revoke 100 capabilities, allocate 100 more, assert the exact frozen `(index, generation)` sequence.
- Mutation **M047** "reuse highest free index instead of lowest" — must be killed.

---

### DET-011 — MEDIUM — Platform-dependent integer behavior: `usize` in semantic positions

**LOCATION**
- L5391 `MaxBytes(usize)` — a `PredicateConstraint`, i.e. **part of an `Authority`**, evaluated by `auth.params.evaluate(...)` in `authorizes` (L11884)
- L5397–5398 `pub max_bytes: usize, pub max_calls: usize` in `ResourceLimits` — the resource ceiling `R`, compared by `effect.cost.leq(auth.resources)` (L11885)
- L1235, L24013, L34500 `cursor: usize` in `ReplayHost` — the `HostTrace` position
- L17797–17798, L18128, L22426 `expected: usize, actual: usize` in `ArityMismatch` — **fault payload**, hence observable machine state and differentially compared (R-REF-05)
- L17596–17597, L18111–18112 `BeginArgument(usize)`, `EndArgument(usize)` — trace event payloads
- L14851, L15005, L16091 `limit: usize`, `continuation_depth(...) -> usize` — the stack-depth bound
- **Contradicted by:** L27987 "explicit integer widths and endianness"; L28309 "Integers: **Explicit widths** (u32, u64)"; L28738; L11438 "The mathematical model assumes unbounded integers; the Rust implementation must explicitly handle the bounds of $u64$"

**VIOLATION**
`usize` is 64-bit on x86-64/aarch64 and 32-bit on 32-bit targets and on wasm32 — and wasm32 is not hypothetical here: L793 and the isolation ladder contemplate "a WASM sandbox," and R-ARCH-05 froze an out-of-process host adapter mode. Every `usize` in the list above is either (a) canonically serialized, (b) compared in an authorization or budget decision, or (c) carried in a fault payload that differential testing compares.

Consequences, concretely:
- `MaxBytes(usize)` and `max_bytes: usize` participate in `authorizes`. A ceiling of `2^32 + 1` is representable on 64-bit and **wraps or fails to construct** on 32-bit ⇒ different authorization outcomes for identical `Authority` data.
- Serializing a `usize` requires choosing a width; the frozen grammar (R-CANON-05/06) has `u32` and `u64` tags but no `usize` tag, so an implementer must pick, and the two picks produce different bytes and different digests (DET-002/DET-007 interaction).
- `ArityMismatch { expected, actual }` is a `Fault` payload. R-REF-05 compares faults; R-CORE-13 now requires comparing "resume-vs-fault behavior, budget effect, and event-log delta" per variant. A width difference in the payload is a differential mismatch on a path the release gate forbids shipping unadjudicated.

The specification's arithmetic discipline is otherwise excellent — L11438, L11781, L11789, L11963 show real care about `checked_add`/`checked_sub`, overflow-before-bound-check, and the `u64` mapping of the mathematical model, and L9211–9219 correctly rejects saturating arithmetic. `usize` is the gap in an otherwise-closed argument: the spec fixed *overflow* behavior and left *width* unfixed.

**NONDETERMINISM-ADMITTED**
Target-width-dependent authorization outcomes, canonical bytes, and fault payloads. Deterministic per target; divergent across targets — and DT contains no "same target" hypothesis.

**EXPECTED-INVARIANT**
No `usize`/`isize` in any type that is canonically serialized, compared in a gate, or carried in a `Fault`/event payload. Explicit `u32`/`u64` everywhere, with the width chosen per field and frozen.

**REMEDIATION**
1. Retype: `MaxBytes(u64)`, `max_bytes: u64`, `max_calls: u64`, `ArityMismatch { expected: u32, actual: u32 }`, `BeginArgument(u32)`, `EndArgument(u32)`, `continuation_depth -> u32`, `ReplayHost.cursor: u64`. Record the `usize` forms as SUPERSEDED, quoted.
2. Add "no `usize`/`isize` in semantic or serialized types" to the canonicalization rule list at L27987/L28309 — the list already says "no platform-dependent representation," which is the right principle stated too abstractly to be actionable; naming the type makes it enforceable.
3. Structural enforcement: clippy `disallowed-types` on `usize`/`isize` in `ror-core` serialized types (a `#[deny]` on the codec module at minimum). Where `usize` is unavoidable (indexing a Rust slice), the conversion must be explicit and checked (`u64::try_from`), consistent with R-CORE-12's no-panic rule.
4. CI: build and run the determinism suite on a 32-bit target (`i686` or `wasm32`) — this converts the whole class from "argued" to "tested" for the cost of one CI job.

**VERIFICATION**
- 32-bit/64-bit cross-target digest equality on the golden-vector corpus.
- Mutation **M048** "`max_bytes: u64` → `usize`" — must be killed on the 32-bit job.
- Boundary values `2^32 − 1`, `2^32`, `2^32 + 1` in ceiling comparisons must behave identically on both targets.

---

### DET-012 — MEDIUM — `format!("{:?}")` places compiler-version-dependent text into machine values

**LOCATION**
- L23994 `Err(e) => Value::Tuple(vec![Value::Symbol(Symbol(0)), Value::String(format!("{:?}", e))]), // Or specific Fault mapping`
- Partial remediation: `spec/01` **R-EFFECT-08** item 4 and **R-CORE-13** — "`format!(\"{:?}\")` debug text of external errors MUST NOT enter machine values — opaque error codes or digests only" (cross-ref SEC-001 rem. 4, SEC-012)

**VIOLATION**
Registered and normatively remediated — filed here because the *determinism* consequence is not stated in either addendum, and because the frozen code block survives at L23994 with only an "// Or specific Fault mapping" hedge.

`Debug` output is not a stable interface. It varies with the Rust compiler version, with `#[derive(Debug)]` field ordering, with the error type's internal structure, and — for wrapped `std::io::Error` — with the **OS locale and errno-to-string mapping**. The frozen line places that string into a `Value::String` inside a `Value::Tuple` that is resumed into an actor's continuation. It therefore becomes:

- part of `ActorState`, hence part of the snapshot, hence part of `StateDigest`;
- a value the program can branch on, so control flow depends on host error text;
- part of the differential comparison (R-REF-05) — and the reference model, by construction, has a different error type and thus different `Debug` output, guaranteeing a mismatch.

So a host-side `io::Error` renders as different bytes on two machines with different libc or different rustc, and DT breaks with `HostTrace` held nominally constant — because the `HostTrace` records a *receipt*, and the divergence is introduced by the machine's *rendering* of that receipt, downstream of the recorded input.

**NONDETERMINISM-ADMITTED**
Compiler-version-, OS-, and locale-dependent machine values and control flow, introduced after the trace boundary and therefore invisible to replay.

**EXPECTED-INVARIANT**
Host errors enter machine values only through a **closed, frozen mapping** to declared fault codes (R-CORE-13's enumeration). No free-form text from outside the machine boundary ever becomes a `Value`.

**REMEDIATION**
1. Replace L23994 with the R-CORE-13 mapping; record the `format!` form as SUPERSEDED, quoted. The addenda froze the rule; the operative code block must be corrected in place or an implementer copying Phase-12 code reintroduces it.
2. Extend the prohibition to `Display` as well as `Debug` — the current phrasing names only `{:?}`, and `{}` on an `io::Error` is *more* locale-dependent, not less. This is a one-word gap that the remediation as written does not close.
3. Structural enforcement: clippy `disallowed-methods` on `format!`/`to_string` applied to host error types in `ror-runtime`.

**VERIFICATION**
- Property: for every `HostFault` variant, the resulting machine value is byte-identical across rustc versions and across `LANG`/`LC_ALL` settings.
- Mutation **M049** "map host error via `format!(\"{:?}\")`" — must be killed.
- Differential: production and reference must produce identical machine values for identical host errors despite different internal error types (this is the test that makes the closed mapping real).

---

### DET-013 — MEDIUM — Filesystem ordering: "locate newest committed snapshot" is unspecified

**LOCATION**
- L26482 "1. Load newest committed snapshot."
- L34345 / L35193 "1. Locate newest committed snapshot." — step (1) of the frozen 12-step recovery algorithm
- `spec/01` **R-RECOV-03** step (1), transcribing it verbatim
- L33871 `pub struct SnapshotVersion(pub u64);` — the ordering key exists
- Related: `spec/09` **U-16** (`EventSequence` vs `WalSequence` relationship unstated), **U-17** (snapshot's runnable queue vs recovery reconstruction — which is authoritative)

**VIOLATION**
Recovery's first step selects the input to everything that follows, and "newest" is never defined. Candidate readings an implementer may legitimately choose:

- highest `SnapshotVersion` among files that parse — *correct*;
- highest filesystem **mtime** — wall-clock-dependent (R-CAP-09-adjacent), and wrong under clock skew, restore-from-backup, or `rsync -a`;
- lexicographically last filename — wrong at the `snapshot-9` / `snapshot-10` boundary;
- **first/last entry from `read_dir`** — `read_dir` order is filesystem- and inode-dependent (ext4 htree hashes filenames; XFS, APFS, tmpfs all differ), so this is host-dependent ordering in the literal sense.

If two committed snapshots exist — which is the normal steady state, since one does not delete the previous snapshot before the next is durable — then recovery's selection is host-dependent, and `Recover(D) ≡ PreCrashMachineState` (R-RECOV-01 family) holds only up to that choice. Recovering the same durable image on two hosts yields two different machine states, both "conforming." Under R-PERSIST-08's chained checksums the *later* snapshot pins a later WAL prefix, so the divergence is not merely "an older but valid state": the two recoveries consume different WAL suffixes and can classify different effects as `Indeterminate`, producing different reconciliation obligations (R-RECOV-08) and different escrow dispositions (R-BUDGET-09).

Neither `spec/06` nor `spec/09` carries a row for snapshot selection; U-16 and U-17 are adjacent (sequence relationships, queue authority) but neither asks *which file*.

**NONDETERMINISM-ADMITTED**
Filesystem-enumeration- and mtime-dependent choice of recovery base ⇒ divergent recovered state, divergent `Indeterminate` classification, divergent escrow.

**EXPECTED-INVARIANT**
"Newest committed snapshot" := the snapshot with the **greatest `SnapshotVersion`** whose commit record verifies (framing, checksum, state digest, and the R-PERSIST-08 chain link to its WAL sequence). Ties are impossible (versions are unique); a verifying snapshot with a greater version always wins; directory enumeration order is never consulted, and mtime is never consulted.

**REMEDIATION**
1. Amend R-RECOV-03 step (1) with that definition; one sentence closes it.
2. State the pairing rule: the selected snapshot's commit record names the last WAL sequence it covers (R-PERSIST-08 already requires the commit record to "cover the state digest and the last WAL sequence"), and step (7) replays strictly after that sequence — so snapshot selection and WAL suffix selection are one decision, not two.
3. Freeze retention: a snapshot may be deleted only after a strictly newer one is committed and verified. This makes "greatest verifying version" total (there is always at least one).
4. Prohibit `read_dir`-order dependence and mtime dependence explicitly in the persistence module; add mtime to the DET-006 `std::time` denial.

**VERIFICATION**
- Recovery determinism across hosts: the same durable image (three snapshots, one corrupt, plus WAL) must recover to a byte-identical `StateDigest` on ext4, XFS, and tmpfs, and after `touch`-ing files in adversarial mtime order.
- Mutation **M050** "select snapshot by mtime" and **M051** "select first `read_dir` entry" — both must be killed.
- Conformance tag: `RECOVERY-SNAPSHOT-SELECTION-TOTAL`.

---

### DET-014 — LOW-MEDIUM — Concurrent shared-state primitives under a lockstep theorem

**LOCATION**
- L247 "a highly concurrent, **lock-free hash set** (e.g., `dashmap::DashSet`) of nonces" — the revocation set
- L334 "the `Arena` struct is wrapped in an `Arc<Mutex<...>>` or, for higher performance, an **`arc-swap` / `dashmap`** structure"
- **Contradicted by:** L25765 "multiple isolated state machines progressing in a strictly deterministic, **scheduler-driven lockstep**"; R-ACTOR-04 (FIFO, one transition per turn); `spec/06` C-37; L26066 "Actors are instantiated with fresh `GenerationalArena`s"
- Note: the corpus contains **no** `rayon`, no `tokio`, no `async fn`, no thread pool, and no `thread::spawn` in operative machine text (verified by grep) — the machine is single-threaded by construction everywhere else.

**VIOLATION**
Filed LOW-MEDIUM because these are early (turn-[1]-era) design sketches that the frozen lockstep model supersedes in substance — but **no supersession record exists**, and they combine two hazards: concurrency primitives *and* hash containers (DET-003/DET-004), in the two most security-sensitive structures (the arena and the revocation set).

The determinism hazard if taken literally: `DashSet` iteration order depends on shard occupancy and insertion interleaving; `Arc<Mutex<Arena>>` permits lock-acquisition order to affect arena allocation order (DET-010); `arc-swap` permits a reader to observe either the pre- or post-swap arena depending on timing. None of these can occur under strict FIFO lockstep — which is the point: the specification's actual execution model is immune, and these three lines are the only text suggesting otherwise. An implementer optimizing for throughput will find explicit frozen permission to introduce shared mutable concurrent state into the TCB.

Cross-reference: SEC-013/R-ARCH-05 retired the isolation ladder and froze in-process structural isolation, accepting "host compromise is machine compromise: same address space." That accepted risk is bounded by the machine being single-threaded; it is a materially different risk if the arena is `arc-swap`ped under concurrent readers.

**NONDETERMINISM-ADMITTED**
If implemented as written: thread-interleaving-dependent revocation-set iteration and arena state — genuine thread-scheduling nondeterminism, unrecordable in `SchedulerTrace` (which, per DET-001, does not exist, and which in any case models *actor* scheduling, not OS threads).

**EXPECTED-INVARIANT**
The machine is single-threaded with respect to `GlobalState`. No `Mutex`, `RwLock`, atomic, or concurrent collection appears in machine state. Parallelism, if ever introduced, must be **outside** the state-transition function (e.g. parallel hashing of independent snapshot chunks) and must be provably order-independent.

**REMEDIATION**
1. Record L247 and L334 as SUPERSEDED by the lockstep model, quoted per R-SCOPE-03. This costs nothing and removes a standing invitation.
2. Add the single-threaded-machine invariant to `spec/01` S-15 alongside R-ACTOR-04 — it is currently implied by FIFO but never stated as a prohibition on shared-state primitives.
3. Structural enforcement: clippy `disallowed-types` on `Mutex`/`RwLock`/`dashmap`/`arc_swap`/`std::sync::atomic` in machine crates (same config as DET-003/DET-006/DET-011).

**VERIFICATION**
- Static: zero concurrency primitives in machine crates.
- Mutation **M052** "revocation set as `DashSet`" — must be killed (it will be killed by the DET-003 order tests, which is a useful demonstration that the container and concurrency findings share a detector).

---

### DET-015 — LOW-MEDIUM — `fresh_handle()` / `fresh_actor()` survive alongside the counter fix that supersedes them

**LOCATION**
- L2013 "$\text{id}$ is a fresh, **globally unique** effect identifier"
- L2273 `a = \text{fresh\_actor}()` — inside the frozen S-Spawn reduction rule
- L8284–8306 — the correction: "if handles are generated using nondeterministic host randomness, then $h_{original} \ne h_{replay}$… Therefore freshness must itself be deterministic. Use a machine-local allocator… For the reference interpreter, I recommend deterministic counters."
- L21949–21955 "No random UUID. No host-generated ID. No wall-clock timestamp. No pointer address."; L24226–24245 "Never derive actor identity from: memory addresses, OS process IDs, random UUIDs, thread IDs, wall-clock timestamps."
- `spec/01` **R-ACTOR-03**, **R-EFFECT-03** — monotonic counters, normative; `GlobalState.next_actor_id`/`next_effect_id`

**VIOLATION**
Filed LOW-MEDIUM because the specification **found and fixed this itself**, twice, normatively and well — R-ACTOR-03 and R-EFFECT-03 are exactly right, and `next_actor_id`/`next_effect_id` are frozen `GlobalState` fields. The residual defect is textual: the *operational semantics rules* still read `a = fresh_actor()` (L2273) and "globally unique" (L2013), with no pointer to the counter discipline, and those rules are what a semantics-first implementer transcribes. "Globally unique" is UUID-suggestive phrasing; "fresh" is a metavariable with no allocation rule attached.

The counter discipline is also **incomplete in one place**: DET-010 shows `CapRef` allocation was never given the same treatment. So the fix covered `ActorId` and `EffectId` and stopped one identifier short.

**NONDETERMINISM-ADMITTED**
Only if the semantics rules are read in isolation from R-ACTOR-03 — in which case: random or host-supplied identifiers, which the L8284 analysis correctly shows makes `h_original ≠ h_replay` and destroys replay outright.

**EXPECTED-INVARIANT**
Every identifier minted by the machine — `ActorId`, `EffectId`, `CapRef`, snapshot/WAL sequence numbers — is a pure function of `GlobalState` (a counter read, then `N' = N + 1`), with the counter itself part of `InitialState`.

**REMEDIATION**
1. Amend S-Spawn (L2273) to `a = N_a` with `N_a' = N_a + 1`, matching L24246's own formulation, and strike "globally unique" at L2013 in favour of "allocated by the monotonic `EffectId` counter." Quote the superseded forms.
2. Extend R-ACTOR-03's prohibition list to `CapRef` (DET-010 rem. 1) so the identifier discipline is total.

**VERIFICATION**
- Identifier-sequence equality across runs and implementations for a fixed program (this also covers DET-010 once `CapRef` is included).
- Mutation **M053** "allocate `ActorId` from a UUID" — must be killed.

---

### DET-016 — LOW-MEDIUM — Spawn budget split `α` is unfrozen; a machine transition has an implementation-chosen numeric result

**LOCATION**
- L2320 / L4035 (A2) "Rule S-Spawn requires $B_{child} \le B_{alloc}$, but **who decides $B_{alloc}$**? … A split policy (e.g., $B_{child} = \alpha \cdot B_{parent}$ for some $\alpha < 1$) needs to be defined."
- `spec/09` **U-03** — spawn budget-allocation policy, open
- `spec/01` **R-ACTOR-05** step (1) "validate and escrow budget (`BudgetAllocationSpec` → `validate_and_escrow`)" — names the mechanism, not the policy
- L2774–2787 — the conservation identity $B_p' = B_p - B_c - C_{spawn}$

**VIOLATION**
Spawn is a machine transition. Its effect on `GlobalState` includes the numeric budget split between parent and child. If the policy is unfrozen, two conforming implementations produce different `Budget` values in both actors after the same `spawn` — hence different `StateDigest`, hence different traces, hence DT violated between conforming implementations, and a guaranteed R-REF-01 differential mismatch.

Note that the conservation *law* holds under any split (that is what L2774–2787 proves, and it is proved correctly), which is precisely why this defect is easy to miss: the invariant the specification verifies is insensitive to the quantity the specification leaves open. Conservation is necessary for determinism here but nowhere near sufficient.

If the resolution is "the parent chooses, via an explicit `BudgetAllocationSpec` in the spawn expression," then determinism is restored **provided** the spec is a compiled-in constant of the `ExecutablePlan` and not host- or policy-supplied at runtime. That proviso is the determinism-relevant half of U-03 and is not currently stated; U-03 asks who decides, framed as a starvation/reasoning tradeoff, without noting that a *runtime* decider is also a DT violation.

**NONDETERMINISM-ADMITTED**
Implementation- or policy-choice divergence in post-spawn budget state; and, if the decider is the host or supervisor, an unrecorded runtime input to a machine transition.

**EXPECTED-INVARIANT**
`B_child` is a pure function of `(B_parent, BudgetAllocationSpec)` where the spec is carried by the `ExecutablePlan` (compiler-fixed, hence part of `InitialState`). No host, supervisor, or policy object contributes a value to a machine transition at runtime.

**REMEDIATION**
1. Close U-03 with the parent-declares reading, and add the determinism proviso explicitly: "`BudgetAllocationSpec` MUST be a compile-time constant of the `ExecutablePlan`; no runtime component may supply or adjust it." (Starvation concerns are then handled by R-ACTOR-09 spawn manifests and compiler validation, not by a runtime decider.)
2. Cross-reference R-BUDGET-09: escrow totality reasons about units entering and leaving escrow, and it needs the entering quantity to be determined.

**VERIFICATION**
- Differential: post-spawn `Budget` byte-equality between production and reference across a generated spawn corpus.
- Mutation **M054** "spawn splits budget 50/50 instead of per spec" — must be killed.

---

### DET-017 — CLEAN — Floating-point dependence: no finding

**EVIDENCE.** `grep -c -E "\bf64\b|\bf32\b" Red-on-Rust.md` ⇒ **0**. No `f32`/`f64`, no floating-point literal arithmetic, no `powf`/`sqrt`/transcendental, no fused-multiply-add, no `-ffast-math`-equivalent concern. The only mention of floating point anywhere is L188's "NaN-boxing" — a *pointer-tagging representation technique*, not arithmetic, and not reachable as a semantic value.

All machine quantities are `u64`/`u32` (budget `⟨F, I, D⟩`, `LogicalTime`, `ResourceLimits`, costs, digests), with checked arithmetic mandated (L9211–9219 "Budget operations should be checked, not saturating"; L11438, L11789, L11854, L11963) and saturating arithmetic explicitly prohibited (R-CLAIM-02, L37998 "Never use saturating subtraction. Use checked arithmetic.").

The one place a float would naturally appear is the spawn budget split `α` (DET-016, L2320: "$B_{child} = \alpha \cdot B_{parent}$ for some $\alpha < 1$"). It is currently only a hypothetical in an open question. **Recommendation, prophylactic:** when U-03 is closed, express any proportional split as an **integer ratio** (`B_child = B_parent * num / den` with checked multiplication and a frozen rounding rule — recommend floor, stated), never as a float. A single `f64` multiply there would import IEEE-754 rounding, x87-vs-SSE excess-precision, and LLVM contraction differences into the budget algebra and thereby into every subsequent authorization decision — reintroducing this entire finding class through the one door currently left ajar.

**Status: CLEAN.** Recorded so the negative result is auditable rather than merely absent, and so the `α` door is closed before it is used.

---

### DET-018 — CLEAN — Implicit environment variables: no finding

**EVIDENCE.** `grep -c -E "std::env|env::var|getenv" Red-on-Rust.md` ⇒ **0**. Also zero occurrences of `RUST_LOG`, `RUST_BACKTRACE`, `dotenv`, or any configuration-by-environment mechanism. No frozen text reads process environment, command-line arguments, current working directory, hostname, user id, or locale into machine state.

Machine configuration enters through `InitialState` and the deployment ceiling (R-KERN-06's grant protocol), which is the correct shape.

Two residual channels are worth naming, both indirect and both already covered elsewhere:
- **Locale** reaches machine values through `format!("{:?}")` on `io::Error` — DET-012.
- **`TZ`** would reach machine state through any wall-clock read — DET-006 is the only such site, and closing it closes this.

**Recommendation, prophylactic:** state the prohibition normatively rather than relying on its current accidental absence, since the first operational deployment will want `RUST_LOG`-style configuration: "No machine-crate code may read process environment, command-line arguments, CWD, hostname, uid, or locale. Observability configuration is host-side only and MUST NOT influence machine state or event ordering." Enforce with clippy `disallowed-methods` on `std::env::*` in machine crates — the same config accumulating under DET-003/DET-006/DET-011/DET-014.

**Status: CLEAN.**

---

## 4. Required inventory — conformance of the frozen specification

The machine "must use" seven mechanisms. Status of each in the frozen corpus:

| Required mechanism | Frozen? | Adequate? | Evidence / gap |
|---|---|---|---|
| **LogicalTime** | **YES** | **PARTIAL** | `pub struct LogicalTime(pub u64)` (L9137, L10201, L10686), held once in `GlobalState` (L24158), `term/` T-28, R-CAP-09 prohibits wall-clock. **Gaps:** `δ_t` advancement schedule unfrozen (DET-008); `Lifetime` is Unix-timestamped and compared against it (DET-006). The type is right; the clock's *rate* and one of its *comparands* are not. |
| **Deterministic IDs** | **YES** | **PARTIAL** | R-ACTOR-03 / R-EFFECT-03: monotonic counters, `next_actor_id`/`next_effect_id` in `GlobalState`; explicit prohibition of UUIDs, PIDs, addresses, thread IDs, wall-clock (L24258–24260, L21949–21953). **Gaps:** `CapRef` allocation left to the arena allocator (DET-010); `fresh_actor()`/"globally unique" survive in the semantics rules (DET-015). Two of three identifier families are fully disciplined. |
| **Explicit SchedulerTrace** | **NO** | **—** | **Does not exist as an artifact.** All 13 occurrences are inside the theorem. No type, no fields, no encoding, no equality, no recording rule, no `term/` entry (DET-001). |
| **Explicit HostTrace** | **NO** | **—** | **Does not exist as a defined artifact.** Same 13 occurrences. Its only concrete proxy, `ReplayHost`, is frozen in **six declarations across five mutually incompatible shapes**, two of which are unordered map lookups that violate R-HOST-03 (DET-001, DET-005). |
| **Canonical serialization** | **PARTIAL** | **NO** | 15A is frozen, thorough, and good **for the data-value domain** — envelope, tags, discriminants, ordered collections, duplicate-key rejection, strict decoder, golden vectors (R-CANON-01…13). **But** no encoding exists for `Expr`, `Frame`, `Environment`, `Constraint`, `Authority`, `CapabilityContext`, `Budget`, `Mailbox`, `SchedulerState`, `GlobalState` (U-02) — i.e. for almost everything DT ranges over (DET-002) — and two grammars still coexist at the one site where serialization meets the digest (DET-007). |
| **Ordered event traces** | **PARTIAL** | **PARTIAL** | `EventLog { events: Vec<LogEntry> }` (L10905) is ordered and append-only; `EventEnvelope { sequence, logical_time, event }` (L33888); WAL sequences gap-checked `s_{n+1} = s_n + 1`; R-PERSIST-08 now chains checksums. **Gaps:** `EventSequence` vs `WalSequence` relationship unstated (U-16); revocation-cascade event order is `HashMap`-dependent (DET-003 item 2); and the event log appears as a theorem *input* at L26998 while being a `GlobalState` field written by transitions — a circularity (DET-001). |
| **Deterministic queues** | **YES** | **YES** | `RunnableQueue { queue: VecDeque<ActorId> }` (L24272 area, L25538 "FIFO, explicitly ordered"), the at-most-once membership invariant (L24280: "ActorId occurs at most once in RunnableQueue"), R-ACTOR-04, mailboxes `VecDeque<MarshalledValue>` FIFO (R-ACTOR-06), `SchedulerState { runnable: VecDeque<ActorId>, blocked: BTreeSet<ActorId> }` (L10925) — ordered container for the blocked set, which is the correct choice and shows the discipline was applied deliberately here. **The one inventory item that is fully frozen and fully adequate.** |

**Summary: 1 of 7 fully adequate; 4 partial; 2 absent.** The two absent ones are the theorem's own parameters.

---

## 5. Verification of `InitialState + SchedulerTrace + HostTrace ⇒ UniqueMachineTrace`

### 5.1 Result

**NOT VERIFIED. The theorem is not currently well-formed, and — read against the frozen corpus as an implementer would — it is false.**

Two independent grounds:

**(1) Ill-formed (DET-001).** `SchedulerTrace`, `HostTrace`, `InitialState`, and `UniqueMachineTrace` have no definitions. A conditional whose antecedent parameters and consequent predicate are undefined has no truth value. It cannot be discharged by proof, by test, or by inspection. Additionally the theorem is stated in three non-equivalent forms (§1), one of which (L26998) takes the `EventLog` as an input while it is also a transition output.

**(2) False under the natural reading.** Take the most charitable available definitions — `InitialState := GlobalState`, `SchedulerTrace :=` the FIFO turn sequence, `HostTrace :=` the recorded receipts, `UniqueMachineTrace :=` the event/digest sequence. Then the transition function demonstrably reads **at least eleven further inputs** not among the three parameters:

| # | Hidden input | Finding | Reaches the trace via |
|---|---|---|---|
| 1 | `RandomState` hasher seed (per-process OS entropy) | DET-004 | `HashMap` iteration → serialized bytes, revocation event order |
| 2 | `HashMap`/`HashSet` iteration order | DET-003 | snapshot bytes, `StateDigest`, WAL order on revoke cascades, derive faults |
| 3 | Implementation's choice of machine-state encoding | DET-002 | every digest; `UniqueMachineTrace` equality itself |
| 4 | Implementation's choice of endianness/grammar | DET-007 | every digest |
| 5 | Host wall clock (via `Lifetime` Unix timestamps) | DET-006 | authorization outcome at gate 6 |
| 6 | Implementation's `δ_t` assignment | DET-008 | deadline/lifetime outcomes, escrow reconciliation timing |
| 7 | Kernel authority image (outside `GlobalState`) | DET-009 | authorization outcome at gate 6 |
| 8 | Arena/slot allocator policy | DET-010 | `CapRef` values → canonical bytes, digests |
| 9 | Target pointer width | DET-011 | ceilings, serialized widths, fault payloads |
| 10 | rustc version + OS locale (via `{:?}`) | DET-012 | machine `Value`s, control flow |
| 11 | Filesystem enumeration order / mtime | DET-013 | recovery base ⇒ recovered state, `Indeterminate` set |

Each is a counterexample: two runs agreeing on all three declared parameters and disagreeing in the trace. **One counterexample refutes the theorem; there are eleven.** Three of them (5, 7, 11) change *authorization or recovery outcomes*, not merely bytes — so the failure is semantic in the strongest sense, not representational.

### 5.2 What *is* true today

The specification has correctly identified and frozen the **architecture** of a deterministic machine. That is not a small thing, and it is the reason the above is a list of eleven closable defects rather than a redesign:

- time is state, not a syscall (R-CAP-09, T-28) — the single most important decision, and it is right;
- identifiers are counters, not entropy (R-ACTOR-03, R-EFFECT-03), with the failure mode explicitly analysed at L8284;
- scheduling is FIFO lockstep with at-most-once membership (R-ACTOR-04) — the fully-adequate inventory item;
- the host is a replaceable interface with a replay implementation (R-HOST-03/04/05);
- serialization is canonical, ordered, count-prefixed, and golden-vectored for the data domain (R-CANON-01…13);
- the corpus is **free of floating point (DET-017) and free of environment reads (DET-018)** — two entire nondeterminism classes eliminated by construction;
- there is no threading, no async runtime, and no work-stealing anywhere in operative text (DET-014 is three vestigial sketch lines, not a design).

The defects are of one kind: **the architecture is stated as prohibitions ("never use wall-clock", "unordered maps forbidden") rather than as a closed enumeration of inputs.** Prohibitions are unenforceable at the margin and are contradicted, in this corpus, by the very code blocks an implementer will copy. The corrective is DET-009 remediation 3 — one normative sentence:

> **No transition may read state outside `GlobalState`, `SchedulerTrace`, or `HostTrace`.**

That sentence is the operational content of DT, it is currently absent, and each of the eleven hidden inputs is an instance of its absence.

### 5.3 Conditions under which DT would hold

DT holds iff all of the following are discharged. This is the audit's proposed closure set:

1. **DET-001** — the four terms defined, one theorem form selected, trace equality specified.
2. **DET-002 + DET-007** — a total, single canonical encoding for everything reachable from `InitialState`; digests defined over it.
3. **DET-003 + DET-004** — no hash-ordered container, and no dependence on any hasher seed, anywhere in machine state.
4. **DET-005** — `HostTrace` is the ordered cursor-consumed sequence with three identity conjuncts; the map-lookup shapes superseded.
5. **DET-006** — no wall-clock quantity in any machine type; `Lifetime` retyped to `LogicalTime`.
6. **DET-008** — `δ_t` frozen as a total function of transition kind.
7. **DET-009** — `GlobalState` closed over the kernel image; the closure sentence stated normatively.
8. **DET-010 + DET-015** — all identifier and slot allocation is a frozen pure function of machine state, `CapRef` included.
9. **DET-011** — no `usize`/`isize` in serialized, compared, or fault-carried types.
10. **DET-012** — closed host-error mapping; no `Debug`/`Display` text in machine values.
11. **DET-013** — snapshot selection by greatest verifying `SnapshotVersion`; no filesystem or mtime dependence.
12. **DET-014 + DET-016** — concurrency sketches superseded; spawn split compile-time fixed.

Discharging 1–12 makes DT *well-formed and plausibly true*. It does not make it **proven** — per the repository's own status ladder (`SPECIFIED → IMPLEMENTED → TESTED → VERIFIED → PROVEN`), proof requires the evidence in §6, and every obligation in this repository is currently `SPECIFIED`.

### 5.4 What replay proves — and what it does not

**Stated in the required form, and this audit makes no stronger claim anywhere:**

> **Replay does not reproduce the external world.**
>
> Replay proves **machine-state / event reproduction**, subject to **explicit external-effect reconciliation.**

Unpacked:

- **What replay establishes.** Given a recorded `(InitialState, SchedulerTrace, HostTrace)`, re-execution reproduces the machine's internal state sequence and event trace exactly — *conditional on the closure set §5.3 being discharged*. Today, per §5.1, it does not even establish this.
- **What replay does not establish.** That any external effect occurred, occurred once, occurred with the recorded result, or is still true. The `ReplayHost` "NEVER touches the external world" (L24016) and returns recorded receipts; L1234 states the premise plainly — "The external world (the OS, the network) is inherently non-deterministic." A receipt is a **record that the machine was told something**, not evidence about the world. Replaying a `FileWrite` receipt writes nothing; the file may since have been deleted, and replay cannot detect that.
- **Why the gap is unavoidable, not a defect.** The specification is unusually honest here and this audit endorses its position. The crash matrix T0–T6 (L28345–28347) classifies post-`Issued`/pre-`Completed` states as **`Indeterminate`** — "The system cannot establish whether the effect occurred" (L26714) — and L26736 states the governing rule: "The machine must never falsely claim transparent recovery for `Indeterminate` effects." L26761: a recovered actor with an indeterminate effect "must **not** automatically resume its continuation." R-DUR-04 and R-RECOV-08 forbid *any* component from resolving `Indeterminate → NotExecuted` on local policy. That is the correct epistemology: the machine records what it did and what it was told, and refuses to infer the world's state from its own logs.
- **Therefore the composite claim.** External correspondence is **not** a consequence of replay. It is established, per effect class (`Replayable`, `Idempotent`, `Reversible`, `Indeterminate` — L26720–26730), by the **reconciliation protocol** (R-RECOV-08): an idempotent authoritative host query, never re-execution, with `NotExecuted` gated behind authoritative evidence and any compensating action passing gates 1–16 as an ordinary new `Request`. For the `Indeterminate` class no protocol can close the gap in general, and the specification correctly does not pretend otherwise.
- **Consequently, the honest formulation of the property, which should replace any looser wording in the README and `spec/00`:**

  > `Replay(InitialState, SchedulerTrace, HostTrace) ≡ RecordedMachineTrace` — **machine-internal**.
  > External-world correspondence is **not implied**, and is established only per effect class via explicit reconciliation, with `Indeterminate` irreducible.

  R-HOST-04 already gestures at this ("machine replay valid; real-world replay per effect class"). It should be stated as the headline framing wherever determinism is claimed, because "deterministic replay" is routinely read by implementers and reviewers as the stronger, false claim.

---

## 6. Recommended verification programme

Ordered by defect-detection yield per unit cost. Items 1–4 are cheap and would detect **eleven** of the sixteen findings.

1. **Two-launch digest invariance** (kills DET-003, DET-004, and the DET-014 sketches). Run the determinism suite twice in separate processes; require byte-identical `StateDigest` sequences. Rust's per-process hasher seeding means this fails immediately on any `HashMap` in serialized state. *One CI job.*
2. **32-bit cross-target run** (kills DET-011). Build and run the golden-vector and determinism suites on `i686`/`wasm32`; require identical bytes. *One CI job.*
3. **Clock-shift replay** (kills DET-006, and DET-013's mtime reading). Replay a recorded trace with the host clock advanced ten years and `TZ`/`LANG` varied; require an identical trace. *One test.*
4. **Effect-order-permutation replay** (kills DET-005 — the decisive test). Replay against a permuted effect order; require `ReplayCorruption` at the first mismatch. A map-lookup `ReplayHost` passes today by completing successfully; that is exactly why the defect survived six frozen declarations.
5. **Cross-implementation digest equality** (kills DET-002, DET-007, DET-010, DET-016). Production and reference must produce byte-identical digests for a shared corpus. This is the M1 acceptance gate "canonical bytes deterministic" made real, and it is the test the whole differential-testing contract (R-REF-01/03/05) presupposes.
6. **Filesystem-adversarial recovery** (kills DET-013). Same durable image across ext4/XFS/tmpfs, with adversarial mtimes and a corrupt newest snapshot; require identical recovery.
7. **Structural denial** (prevents regression of DET-003, DET-006, DET-011, DET-014, DET-018). One workspace clippy config denying, in machine crates: `HashMap`/`HashSet`, `std::time::{SystemTime, Instant, Duration}`, `usize`/`isize` in codec types, `Mutex`/`RwLock`/`dashmap`/`arc_swap`/atomics, `std::env::*`. Same mechanism class as R-CORE-12's `unwrap` denial and R-REPO-03's `PlanSeal` gate — the repository already has the pattern, this extends it.
8. **Mutation registry additions** (additive per R-TEST-04): **M037–M054** as filed above. All must be killed.

New conformance tags proposed: `DETERMINISM-THEOREM-WELL-FORMED`, `CANONICAL-MACHINE-STATE-TOTAL`, `NO-HASH-SEED-DEPENDENCE`, `HOSTTRACE-ORDERED-CURSOR`, `NO-WALLCLOCK-IN-AUTHORIZATION`, `INITIALSTATE-CLOSED`, `RECOVERY-SNAPSHOT-SELECTION-TOTAL`.

---

## 7. Register entries proposed

Additive; none rewrites frozen text. Per R-SCOPE-03 all supersessions quote rather than delete.

| Register | Proposed entries |
|---|---|
| `spec/06` (contradictions) | **C-98** DT stated in three non-equivalent forms, one circular (MAJOR) · **C-99** `ReplayHost` frozen in six declarations, five incompatible shapes, two violating R-HOST-03 (MAJOR) · **C-100** `Lifetime` Unix-timestamped and compared against `LogicalTime`, contradicting R-CAP-09/R-CLAIM-02 (MAJOR) · **C-101** `HashMap`/`HashSet` in operative machine structs vs the L28738 prohibition (MAJOR) · **C-102** `usize` in serialized/compared/fault types vs "explicit integer widths" (MINOR) |
| `spec/09` (unresolved) | **U-35** the four DT terms undefined — **BLOCKING** (gates Track A, Track D, R-HOST-03/04/05, R-REF-01) · **U-36** `CapRef`/arena allocation policy · **U-37** snapshot-selection rule. Amend **U-02** (add: blocks DT's conclusion, not only persistence), **U-07** (add: blocks cross-implementation determinism and R-BUDGET-09 liveness), **U-03** (add: the compile-time-fixed proviso) |
| `term/` | **T-82** `SchedulerTrace` · **T-83** `HostTrace` · **T-84** `InitialState` · **T-85** `UniqueMachineTrace` · **T-86** `Lifetime` (with the Unix reading as `FORBIDDEN_VARIANTS`) · **X-87** `ReplayHost` — one name, six denotations · non-conflation law **N-32** `SchedulerTrace ≠ EventLog` (input consumed vs output produced) · **N-33** `Lifetime ≠ WallClockInterval` |
| `spec/03` (obligations) | Determinism-closure addenda **R-CORE-14** (`InitialState` closed; no transition reads outside the three parameters) and **R-CORE-15** (DT terms defined; trace equality specified) |
| Mutation registry | **M037–M054** |

---

## 8. Statement of audit limits

- **This is a specification audit.** The repository contains no implementation (`spec/00` status discipline; every obligation `SPECIFIED`). No finding here is a claim about code behaviour; each is a claim that the frozen text **admits** a nondeterministic implementation, or fails to determine an outcome. Where a finding says "an implementer will," that is a claim about what the text licenses, not an observation.
- **No finding claims DT is unachievable.** All sixteen are closable, most by freezing a decision already scoped in `spec/09`. The architecture is sound; the enumeration of inputs is incomplete.
- **Findings are not promoted beyond `SPECIFIED`.** No verification claim, no evidence status change, no promotion on the status ladder is asserted by this document. §6 proposes tests; it does not report results.
- **On external effects, this audit asserts only §5.4** and asserts it in the required form: replay proves machine-state and event reproduction, subject to explicit external-effect reconciliation. **It does not claim, anywhere, that replay reproduces the external world.**
- **Coverage.** All fifteen requested categories were checked; every one is reported, including the two with no finding (DET-017 floating point, DET-018 environment variables), so that the negative results are auditable rather than silently omitted. Where a category's risk is real but indirect (network timing — see DET-005 and the `Indeterminate` discussion in §5.4; thread scheduling — DET-014), it is filed at the severity the frozen text supports rather than inflated.
- **Method.** Mechanical search across all 42,312 source lines plus the five canonical organizations, followed by hand-reading of every hit in operative context. Counts stated (13 `SchedulerTrace` occurrences; 0 `f64`/`f32`; 0 `std::env`; six `ReplayHost` declarations) are grep-verified at commit `3d00818` and are re-checkable by the commands recorded alongside each finding.
