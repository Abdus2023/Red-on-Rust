# M5 Preflight

**Operation type:** M5 PREFLIGHT / implementation authorization only.  
**M5 implementation in this operation:** **NOT STARTED** (FACT).  
**Do not implement Request / effects / HostExecutor / WAL recovery in this commit.**

Evidence labels: **FACT** | **DERIVED** | **DISCLOSED LIMITATION** | **BLOCKER** | **AUTHORIZATION**

---

## 1. Repository identity

| Item | Value | Class |
|---|---|---|
| Branch | `arena/01a06993-red-on-rust` | FACT |
| HEAD | `96ce46e54656354ba70141fcae05f003ba3be673` | FACT |
| Subject | `review: reconcile M4 capability attenuation implementation` | FACT |
| M4 implementation | `958790a` (ancestor) | FACT |
| M4 review | `96ce46e` (= HEAD) | FACT |
| Working tree | clean | FACT |
| `docs/bootstrap/M4-REVIEW.md` | present; ACCEPTED WITH DISCLOSED EVIDENCE LIMITATIONS | FACT |

No silent reset/rebase/merge. Identity gate **PASS**.

---

## 2. Authority sources

| Source | Role |
|---|---|
| `final/01` R-ORDER-02 M5 row; R-CORE-02/06/11/14; R-EFFECT-01…08; R-DUR-01…07; R-HOST-01…06; R-CALC-02/04/05; R-CEK-03 Request* frames; R-BUDGET-04…08/15/16; R-TRUST-05; R-CANON-09/12/13 | Normative homes |
| `final/03` | Registry SPECIFIED rows |
| `final/04` M5 gate + `EFFECT-ISSUE-DURABLE-BEFORE-HOST`, `REQUEST-ARGS-LTR`, `REQUEST-NON-CAP-SHORT-CIRCUIT`, receipt tags | Verification obligations |
| `final/05` GI-SEC-02/07/09/10/16 | Global invariants |
| `final/08` | Evidence ceiling 184 × SPECIFIED |
| `final/09` | OADs; U-39…U-44 **RESOLVED** (addendum VII); U-02/U-08/U-09/U-21/U-31 **OPEN** |
| `dep/01-graph.md` / `dep/10-graph.json` | Edge authority |
| `mod/18-ownership-matrix.md` | MOD-08 EFFECT, MOD-09 HOST, MOD-11 PERSISTENCE |
| `reg/requirements.json` | **184 × SPECIFIED** (computed this preflight) |
| `R-REG-VERDICT.md` / `reg/status-transitions.json` | No promotion |
| `docs/bootstrap/M4-PREFLIGHT.md` / `M4-PROGRESS.md` / `M4-REVIEW.md` | M4 boundary + disclosures carried forward |

**Source-of-truth procedure:** requirement → verification tag → invariant → OAD → ownership → dep graph → M5 boundary. Prompts, code, and tests are **not** authority.

---

## 3. Canonical M5 scope

### Milestone acceptance (canonical)

| Source | Text | Class |
|---|---|---|
| `final/01` **R-ORDER-02** | **M5 Effects** — `16-step request sequence, issuance, receipts, host mock pass` | FACT |
| `final/04` milestone row | **M5** — authorization, budget gates, deadline, host policy, EffectId/Digest, durable issuance, receipt validation | FACT |

**Canonical M5 name (FACT):** Effects — **not** Actors (M6), **not** full Persistence/crash recovery (M7).

### Governing protocol (authoritative order)

**R-CORE-14** is the frozen 16-step request protocol (addendum VII; resolves U-39/C-103). It **SUPERSEDES** any earlier host-before-Issued listing in historical R-EFFECT-01 prose (quoted, not deleted):

| Step | Action | Owner (mod) |
|---|---|---|
| 1 | Evaluate capability expression | MOD-05 CEK |
| 2 | Evaluate target expression | MOD-05 |
| 3 | Evaluate arguments **left-to-right** (one per CEK step) | MOD-05; tag `REQUEST-ARGS-LTR` |
| 4 | Construct canonical `Effect` + `EffectDigest` | MOD-08 / MOD-01+10 |
| 5 | Validate CapRef (`Valid`) | MOD-03 |
| 6 | Authorize exact effect (`Authorized` + possession) | MOD-03; R-CORE-11 / R-KERN-04 |
| 7 | Capability ceiling | MOD-03/04 |
| 8 | Runtime budget (`issue + complete_max`) | MOD-04; R-EFFECT-05 |
| 9 | Runtime reservation | MOD-04 |
| 10 | Deadline `t + δ_t(req) ≤ W` | MOD-04; R-CORE-14 / U-40 |
| 11 | Host policy (`HostPolicyOK`) | MOD-09; fail-early |
| 12 | Allocate monotonic `EffectId` | MOD-08 |
| 13 | Commit issue budget / reservation (escrow) | MOD-04/08 |
| 14 | **Durable issuance** (Prepared→Issued, 2 fsyncs) | MOD-11; R-DUR-02 |
| 15 | Actor `Pending` | thin M5; full multi-actor = M6 |
| 16 | Host invocation | MOD-09; **only after** durable Issued |

**Hard security hinge (FACT):**

```text
HostInvoked(E)  ⇒  DurableIssued(E)     # R-DUR-01, R-CORE-06, GI-SEC-07
¬DurableIssued  ⇒  ¬HostExecutor::execute  for that new effect
```

Turn-[21] order with host emission before durable Issued is **SUPERSEDED** (R-CORE-14).

### External-effect chain (R-CORE-02 / R-CORE-11)

```text
ExternalEffect(E) ⇒
  ValidatedRequest(E)
  ∧ Authorized(holder, c, E, t)   # possession conjunct
  ∧ CapabilityWithinCeiling(E)
  ∧ BudgetAvailable(E)
  ∧ DeadlineValid(E, t)
  ∧ HostPolicyOK(E)
  ∧ Issued(E)                     # durable
```

### Out of M5 scope (DERIVED)

| Concern | Milestone |
|---|---|
| Multi-actor spawn/mailbox/scheduler | **M6** |
| Full WAL framing, snapshot protocol, T0–T6 crash matrix, recovery engine | **M7** (R-PERSIST-*/R-RECOV-*) |
| Planner/LLM boundary | later |
| Compiler Request static analysis suite | compiler track |
| Frame/GlobalState **byte** codecs | **U-02** |
| R-REG promotion / OAD close-by-fiat | never in preflight |
| Theorems PROVEN | not claimed |

**Thin M5 dependencies authorized (DERIVED — same pattern as M4 thin κ/grant):**

| Thin surface | Why needed in M5 | Full form deferred |
|---|---|---|
| Single-actor / harness `Pending` | R-CORE-14 step 15 | M6 actors |
| Budget + reservation + deadline gates for Request | steps 7–10 / R-EFFECT-05 | full MOD-04 algebra depth may lag |
| Persistence **issuance journal API** (append Prepared/Issued + sync) | R-DUR-01/02, R-TRUST-05 hinge | M7 WAL/snapshot/recovery |
| Host mock / ReplayHost / PanicHost | R-ORDER-02 “host mock”; R-HOST-02/03 | live OS host adapters |

---

## 4. Scope table (derived)

| Surface | Canonical authority | Owner crate | M5 sprint? | Decision |
|---|---|---|---|---|
| `Expr::Request { capability, operation, target, params }` | R-CALC-02 | `ror-core` (AST present) | **YES** CEK | AUTHORIZED |
| Request CEK frames | R-CEK-03 `RequestCapability` / `RequestTarget` / `RequestArgument` | `ror-runtime` | **YES** | AUTHORIZED |
| Non-cap short-circuit | R-EFFECT-04; `REQUEST-NON-CAP-SHORT-CIRCUIT` | runtime | **YES** | AUTHORIZED |
| Args LTR | R-CORE-14 §3; `REQUEST-ARGS-LTR` | runtime | **YES** | AUTHORIZED |
| `Effect` + `EffectDigest` | R-CALC-04; R-CANON-09 | core + runtime | **YES** | AUTHORIZED (provisional Op/Target/Params under U-21) |
| `EffectCost` | R-CALC-05 | core | **YES** | AUTHORIZED |
| Cap Valid + authorize | R-CAP-06/07; R-CORE-11; R-KERN-04 | kernel | **YES** (wire M4 algebra into gates 5–7) | AUTHORIZED |
| Budget / reservation / deadline | R-BUDGET-04/06/08/15/16; R-EFFECT-05 | core/runtime | **YES** thin request path | AUTHORIZED w/ disclosure |
| Host policy gate | R-HOST-01; step 11 | host + runtime | **YES** | AUTHORIZED |
| Monotonic `EffectId` | R-EFFECT-03 | runtime | **YES** | AUTHORIZED |
| Durable Prepared/Issued | R-DUR-01/02/06/07 | **persistence** + runtime | **YES** issuance API | AUTHORIZED; recovery **NO** |
| `HostExecutor::execute` | R-HOST-02; step 16 | host | **YES** mock | AUTHORIZED |
| Receipt ID+digest | R-EFFECT-06 | runtime | **YES** | AUTHORIZED |
| Receipt result admission | R-EFFECT-08 | runtime | **YES** | AUTHORIZED |
| Completion accounting | R-EFFECT-07 | runtime | **YES** | AUTHORIZED |
| Crash T0–T6 / full recovery | R-RECOV-*; R-DUR-04 classification rules | persistence | **PARTIAL** — classify/interface only if needed; **no** full engine | DEFERRED M7 |
| Reference effect model | R-REF-*; R-SCOPE-04 | `ror-reference` | **YES** independent | AUTHORIZED |
| Differential M5 | final/04 M5 | `ror-differential` | **YES** | AUTHORIZED |

---

## 5. Request semantics

**AST (R-CALC-02, FACT — already in `ror-core`):**

```text
Expr::Request {
  capability: Box<Expr>,
  operation: Box<Expr>,
  target: Box<Expr>,
  params: Vec<Expr>,
}
```

**Current code (FACT):** both CEKs fault `UnsupportedInM2 { "Request" }` — correct pre-M5 posture.

**Trust path (AUTHORIZATION):**

```text
Untrusted Expr::Request
  ↛ HostExecutor
  ↛ filesystem / network / process
only via: CEK eval → ValidatedRequest gates → durable Issued → host
```

---

## 6. CEK ordering

**Authoritative evaluation order (R-CORE-14 + R-CEK-03):**

1. Evaluate **capability** expression → require `Value::Capability` (**short-circuit** if not — before target/params; R-EFFECT-04 / `REQUEST-NON-CAP-SHORT-CIRCUIT`).
2. Evaluate **target** expression.
3. Evaluate **params** left-to-right, one value per CEK step (`RequestArgument` frame).
4. Then gates 4…16 (construct Effect … host).

**M3 non-regression (AUTHORIZATION):** Call path remains `operator → FunctionValue → arity precheck → args LTR`. Request MUST NOT alter Call arity-order gate.

**R-CEK-03 frames (FACT):** `RequestCapability { operation, target, params, env }`, `RequestTarget { capability, operation, params, caller_env }`, `RequestArgument { capability, operation, target, evaluated, remaining, caller_env }`.

**Note:** `operation` appears in AST as `Box<Expr>` (R-CALC-02) while some sketches treat `Op` as immediate. **DERIVED reading:** evaluate `operation` expression to a domain `Op` value (provisional under U-21), consistent with other Request fields being expressions. If implementation discovers a frozen non-Expr `Op` form that conflicts, **STOP — CANONICAL AUTHORITY CONFLICT** (do not invent).

**Frames:** in-memory only (U-02 OPEN) — no frame codecs in M5.

---

## 7. Capability authorization

**Carry-forward M4 disclosures (FACT from M4-REVIEW):**

- `CapRef::from_kernel_parts` is **public**; bits ≠ authority (arena-gated).
- Shared `ror_core::admissible_constraint_wrt_parent` between P and R.

**M5 requirements:**

| Gate | Law | M5 action |
|---|---|---|
| 5 Valid | R-CAP-07 | `kernel.valid(cap, t)` |
| 6 Authorize | R-CAP-06 + R-CORE-11 possession | `authorize` / `authorize_algebra` with holder context |
| 7 Ceiling | R-BUDGET-04 / R-CAP-06 cost≤R | dual gate |

**CapRef boundary decision (AUTHORIZATION):** M5 **MAY** consume current M4 CapRef/kernel APIs. Stricter “delete public `from_kernel_parts`” is **not** a mandatory M5 blocker: GI-SEC-16 / Valid gate still prevent bit-forgery from exercising authority. Optionally tighten visibility in M5 **without** claiming U-*/R-KERN OAD closed.

**MUST NOT:** host or persistence mint CapRefs; data-path decode mint (R-CANON-12 already holds).

---

## 8. EffectRequest boundary

**Effect (R-CALC-04):**

```text
Effect {
  capability: CapRef,
  operation: Op,       # U-21 provisional
  target: Target,      # U-21 provisional
  params: Params,      # U-21 provisional
  cost: EffectCost,
}
```

**EffectDigest:** `SHA-256(canonical_bytes(effect))` (R-CALC-04 / R-CANON-09) — in-tree SHA-256 already present (M1).

**EffectRequest (host-facing, DERIVED from R-DUR-02 step 7 + R-HOST-02):** carries issued effect identity for host execution — at minimum what host needs to perform an **already Issued** effect (id, digest, effect payload / effect_bytes). Exact struct fields MUST follow frozen sketches without inventing alternate semantics; **MUST NOT** include raw Authority.

**Ownership:** constructed in runtime after gates; consumed by `ror-host`.

---

## 9. EffectCost

**R-CALC-05 (FACT):**

```text
EffectCost { issue: Consumable, complete_max: Consumable, reserve: Reserved }
```

| Rule | Authority | M5 |
|---|---|---|
| Charge `issue` at request | R-CALC-05 | YES |
| Escrow `complete_max` at issuance | R-EFFECT-05 / R-BUDGET-05 | YES |
| Gate 8: afford `issue + complete_max` | R-EFFECT-05 | YES |
| δ_t(request issuance)=1; receipt=1; pure CEK=0 | R-BUDGET-16 | YES (logical clock) |
| Full budget algebra / conservation harness | MOD-04 | **thin** for Request path; depth may lag (**DISCLOSED**) |

**Not blocked:** budget rules for the request path are SPECIFIED (R-BUDGET-*). Implement **minimum** Consumable/Reserved/Deadline types needed for gates — do not invent a second cost model.

---

## 10. Canonical effect bytes

**Authority:** R-CANON-01/09/12/13; R-DUR-06; R-PERSIST-01.

| Principle | M5 rule |
|---|---|
| One grammar | Phase **15A** only |
| `effect_bytes` | `CanonicalEncode(Effect)` |
| Digest | SHA-256 over those bytes |
| Journal payload | R-DUR-06: Prepared/Issued carry `effect_bytes` + EffectCost triple + id/actor/digest |
| No capability in data path | R-CANON-12 — effect encoding must not smuggle Authority; CapRef payload only via allowed paths |
| No alternate host/runtime/persistence codecs | FORBIDDEN |

**U-02** remains OPEN for **machine-state** snapshots — not an excuse to fork effect encoding. Effect descriptor encoding is M5-in-scope under 15A + R-CALC-04 field set (provisional domain enums OK under U-21).

---

## 11. Prepared / Issued ordering

**Causal protocol (R-DUR-03):**

```text
Issued(E)      ⇒ Prepared(E)
Completed(E)   ⇒ Issued(E)
Reconciled(E)  ⇒ Issued(E)
```

**Issuance transaction (R-DUR-02) — strict order:**

1. Pure validation / auth / budget (steps 1–11 / 12–13 prep)
2. `persistence.append(EffectPrepared { … })`
3. `persistence.sync()`
4. `persistence.append(EffectIssued { … })`
5. `persistence.sync()`
6. Actor → `Pending`
7. Host receives `EffectRequest`

**R-DUR-06 payloads:** Prepared/Issued include `effect_bytes`, `issue`, `complete_max`, `reserve` (not merely `{id,actor,digest}`).

**R-CORE-14 atomic section:** steps 12–14b one atomic section — no SnapshotCommit, no scheduler yield, no observable event mid-section.

**Live failure (R-DUR-07):** append/sync error → `Fault::PersistenceError` (provisional under U-08 if enum not closed); roll back to pre-s12; five R-EFFECT-04 assertions; host **never** called.

**Crash classification (R-DUR-04):** rules are SPECIFIED; **full recovery engine = M7**. M5 journal MUST be able to *record* Prepared/Issued correctly so M7 can classify later. M5 **MUST NOT** silently repair invalid durable state.

---

## 12. Durable issuance boundary (hard gate)

| Requirement | Enforceable? | How (planned) |
|---|---|---|
| `HostInvoked ⇒ DurableIssued` | **YES** | API: `HostExecutor::execute` only reachable from runtime path after persistence confirms Issued+sync |
| No host on gate deny | **YES** | R-EFFECT-04 short-circuit; no EffectId / no journal / no host |
| Structural hinge | **YES** | Cargo already: `ror-runtime → ror-persistence` (R-TRUST-05); host does not own journal |
| No local journal shim bypassing crate | **YES** | persistence trait/API in `ror-persistence`; runtime calls it |

**Ownership of hinge:** MOD-08 sequence position + MOD-11 append/sync + MOD-09 never earlier.

**If implementation cannot type/API-enforce “no execute before Issued”:** that is an **implementation defect to fix in M5 sprint**, not a preflight BLOCKER — the canonical rule is frozen and the crate edge exists.

**Preflight verdict on this gate:** **PASS (enforceable)**.

---

## 13. HostExecutor boundary

**R-HOST-02:** host performs **only issued** effects; partially trusted.

**R-HOST-01:** live host independently validates OS policy (defense in depth); machine gate-11 is fail-early.

**R-HOST-03:** ordered ReplayHost; ID+digest per entry; no unordered map.

**M5 mock surface (R-ORDER-02 “host mock”):**

| Adapter | Role |
|---|---|
| `HostExecutor` trait | `execute(EffectRequest) → Result<…>` |
| Mock / scripted host | tests |
| `ReplayHost` | ordered trace replay (no real external I/O) |
| `PanicHost` | harness: any execute without Issued = panic/fail test |

**MUST NOT:** host mint CapRef, broaden Authority, or call kernel derive for untrusted input.

**Dep:** `ror-host → ror-core, ror-runtime` already in Cargo (FACT). Runtime must not depend on host for pure CEK; effect path injects host handle at machine boundary.

---

## 14. HostPolicy boundary

Gate 11 + host-side R-HOST-01. Policy denial → short-circuit (R-EFFECT-04); no Issued; no execute.

Provisional `HostPolicyDenied` fault label OK under U-08 OPEN (same pattern as M4).

---

## 15. Persistence boundary (M5 ≠ M7)

| M5 MUST | M7 owns |
|---|---|
| Issuance journal API: append Prepared/Issued + sync | Full `WalFrame` sequence continuity suite as M7 acceptance |
| R-DUR-06 record contents for issuance | Snapshot begin/commit protocol |
| Deterministic in-memory or test backend satisfying append/sync contract | T0–T6 crash matrix execution |
| R-DUR-07 live failure mapping | Recovery reconstruction / reconciliation engine |
| Hinge used by runtime | Authority lattice durability (R-PERSIST-07) full |

**R-PERSIST-01:** persistence is not a semantic machine; payloads = 15A bytes.

**BLOCKER test:** if M5 cannot record durable Issued without implementing full recovery — still OK: implement **journal interface + test double**, not recovery. Full recovery in M5 without authority = **MILESTONE BOUNDARY CONFLICT** — **forbidden**.

---

## 16. Failure semantics

| Class | Canonical direction | M5 posture |
|---|---|---|
| Auth / Valid deny | R-EFFECT-04 short-circuit | YES |
| Budget / deadline deny | R-BUDGET-08 shape; precedence notes R-BUDGET-15 | YES thin |
| Host policy deny | R-HOST-01 | YES |
| Persistence append/sync fail | R-DUR-07 `PersistenceError` | YES provisional label |
| Host execution fail | map via closed mapping; no debug text in values (R-EFFECT-08 / R-CORE-13) | YES provisional |
| Receipt ID/digest mismatch | R-EFFECT-06 `ReplayCorruption`; no resume | YES |
| Receipt capability/closure | R-EFFECT-08 InvalidReceipt family | YES |
| Indeterminate (issued∧¬completed) | R-DUR-04 | record/observe; full reconcile M7 |

**U-08 OPEN:** do not close fault taxonomy; provisional evaluator/runtime labels with disclosure (M3/M4 precedent).

**MUST NOT** collapse distinct classes into one generic error when canonical names exist.

---

## 17. Reference independence

| Rule | M5 requirement |
|---|---|
| R-SCOPE-04 / R-REF-02 | Reference MUST NOT call production runtime/kernel/host/persistence for transitions |
| Effect algebra / request observation | Independent reference model of gates + mock journal/host traces |
| Shared `ror-core` types | ALLOWED (Effect shells, 15A codec, digest) |
| Shared admissibility helper | Carry M4 disclosure; do not expand shared **transition** code |
| Forbidden: `ror-reference → {kernel,runtime,host,persistence}` | keep Cargo clean |

**If M5 needs production effect pipeline inside reference:** **BLOCKED — REFERENCE INDEPENDENCE FAILURE**. Preflight assessment: **avoidable** via independent ref CEK Request + ref journal/host doubles.

---

## 18. Differential surface

**final/04 M5 evidence targets (DERIVED observation set):**

| Observation | Compare P vs R |
|---|---|
| Request accept / gate deny fault | YES |
| Non-cap short-circuit (no id/budget/log/host) | YES |
| Args LTR side-effects on env/faults | YES |
| EffectId monotonicity (same seed) | YES |
| EffectDigest equality | YES |
| Prepared/Issued journal observations (semantic records) | YES |
| Host invoke count / ordering (Issued before execute) | YES |
| Receipt validate / complete / deny | YES |
| No host on deny | YES |

Normalize only non-semantic representation. Do not hide host-before-Issued bugs via normalization.

---

## 19. Security analysis

| Threat | Control |
|---|---|
| Expr → host bypass | CEK only through 16 steps; host after Issued |
| Capability amplification | M4 derive laws unchanged; Request does not mint Authority |
| CapRef forgery | Valid + possession gates |
| Pre-Issued host execution | R-DUR-01 API + PanicHost tests; tag `EFFECT-ISSUE-DURABLE-BEFORE-HOST` |
| Effect identity collision | Monotonic EffectId; digest causal pair |
| Duplicate issuance | single allocate path in atomic section |
| Receipt injects authority | R-EFFECT-08 contains_capability |
| Host mints authority | R-HOST-02; no kernel grant in host |
| Nondeterministic auth | logical time + pure predicates |

**Central invariant preserved:** `Untrusted Request ↛ Authority ↛ External Effect` without the chain.

---

## 20. Determinism analysis

| Rule | M5 |
|---|---|
| No wall-clock EffectId | R-EFFECT-03 |
| Logical time only | R-CAP-09 / R-BUDGET-16 |
| Canonical effect bytes stable | 15A |
| Host replay ordered | R-HOST-03 |
| No HashMap-order semantics for gates | prefer BTree / vectors |
| δ_t table exhaustive | R-BUDGET-16 |

---

## 21. M4 regression

Baseline @ this preflight (toolchain `ror-stable` 1.88.0):

| Command | Result |
|---|---|
| `cargo fmt --check` | **PASS** |
| `cargo check --workspace` | **PASS** |
| `cargo test --workspace` | **PASS** (129 passed across suites) |
| `cargo clippy … -D warnings` | **PASS** |

M4 surfaces (derive, no-amp, revoke, valid, Attenuate, ref algebra, differential m4) remain green. **No M4 semantic edits authorized** to “prepare” M5.

---

## 22. OAD reconciliation

| OAD | Status | M5 impact |
|---|---|---|
| **U-39** 16-step which form | **RESOLVED** (R-CORE-14) | use master-prompt order |
| **U-40** deadline predicate | **RESOLVED** (`t+δ_t≤W`) | gate 10 |
| **U-41** durable payload | **RESOLVED** (R-DUR-06) | effect_bytes + cost |
| **U-42** live journal failure | **RESOLVED** (R-DUR-07) | PersistenceError + rollback |
| **U-43** recovery boundaries | **RESOLVED** (R-RECOV-09) | **M7** primarily |
| **U-44** request tags | **RESOLVED** | REQUEST-ARGS-LTR / NON-CAP-SHORT-CIRCUIT |
| **U-02** machine codecs | **OPEN** | frames in-memory; effect bytes still 15A |
| **U-08** / **U-14** faults | **OPEN** | provisional labels |
| **U-09** Value domains | **OPEN** | keep split; Constraint/Effect shells disclosed |
| **U-21** Op/Target/Params | **OPEN** | provisional enums (extend M4 Op) |
| **U-31** Authority fields | **OPEN** | M4 provisional continues |
| **AMB-12** / REQ-CAP-024 | registry AMBIGUOUS | R-CAP-10 still governs attenuate; Request uses Authorized path |
| **U-06** effect property table | OPEN-ish | non-normative table; not M5 blocker |

**No mandatory OPEN OAD blocks M5** given addendum VII resolutions for the request pipeline. OPEN items remain **disclosed limitations**, not silent closes.

---

## 23. R-REG reconciliation

```text
reg/requirements.json → 184 × SPECIFIED   (computed this preflight)
```

- No status transitions.
- Preflight does **not** claim VERIFIED/PROVEN/IMPLEMENTED in R-REG.
- Mapping of M5 work to R-EFFECT/R-DUR/R-HOST IDs is documentation only.

---

## 24. Discrepancies (disclosed — not silent fixes)

| ID | Issue | Preflight resolution |
|---|---|---|
| D-M5-01 | R-EFFECT-01 historical steps list host emit before durable Issued | **R-CORE-14 wins**; R-EFFECT-01 historical order SUPERSEDED |
| D-M5-02 | R-EFFECT-03 registry blurb focuses on EffectId; full 16-step in R-CORE-14/R-EFFECT-01 | Implement R-CORE-14 sequence |
| D-M5-03 | R-CEK-03 Request frames vs Expr operation as Expr | Evaluate operation expr → Op (U-21 provisional) |
| D-M5-04 | Full actors for Pending | Thin harness Pending; M6 full |
| D-M5-05 | Full budget subsystem absent in code | Thin request-path budget types |
| D-M5-06 | Persistence crate stub | Implement issuance API only; not M7 recovery |
| D-M5-07 | Host crate stub | Mock/Replay/PanicHost |
| D-M5-08 | U-08 fault names | Provisional labels |
| D-M5-09 | M4 CapRef::from_kernel_parts public | Carry disclosure; gates still bind |
| D-M5-10 | Shared core admissibility helper | Carry M4 disclosure; no shared effect CEK |

**None classified BLOCKER** for starting implementation under disclosed limitations.

---

## 25. Explicit MAY / MUST NOT / DEFERRED

### MAY (authorized in M5 implementation sprint)

- CEK `Expr::Request` + R-CEK-03 Request* frames (in-memory).
- Construct `Effect` / `EffectCost` / `EffectDigest` (15A + in-tree SHA-256).
- Wire M4 kernel Valid + authorize into gates 5–7; thin possession context.
- Thin budget/reservation/deadline for request gates; logical δ_t per R-BUDGET-16.
- Monotonic EffectId allocator.
- `ror-persistence` issuance journal: Prepared/Issued append+sync (+ test double).
- Enforce Issued before `HostExecutor::execute`.
- `ror-host` HostExecutor trait + mock/replay/panic hosts.
- Receipt validate (id+digest) + result admission (R-EFFECT-08) + completion accounting.
- Independent reference Request/effect observation model.
- Differential M5 cases; short-circuit matrix tests; durable-before-host mutation intent.
- Provisional fault variants as needed (U-08 OPEN).
- Optional CapRef constructor visibility tightening **without** claiming OAD close.

### MUST NOT

- Invoke host before durable Issued for that effect.
- Implement full multi-actor scheduler/mailbox/spawn (M6).
- Implement full WAL/snapshot/T0–T6 recovery engine as M5 “done” (M7).
- Alternate effect serializers / LE grammar / non-15A digests.
- Import production effect CEK into `ror-reference`.
- Resolve OADs or promote R-REG.
- Regress M1–M4; change Call arity-before-args.
- Wall-clock EffectId or Lifetime.
- Expr/host direct FS/net/process bypass.
- Collapse fault classes arbitrarily.
- Claim PROVEN / semantic verification complete from tests alone.
- Add crates.io deps while network posture unchanged (prefer in-tree).
- `unsafe` code.

### DEFERRED

| Item | Until |
|---|---|
| Full actor runtime | M6 |
| Crash recovery / snapshot | M7 |
| Live OS host adapters beyond mock | later host track |
| Compiler Request static suite | compiler |
| U-02 machine codecs | OAD resolution |
| Full Fault enum freeze | U-08 |
| U-21 final host ontology | OAD |
| R-REG promotion | separate evidence process |
| M9 100% mutation kill | M9 |

---

## 26. Authorization decision

```text
M5 PREFLIGHT = GREEN WITH DISCLOSED LIMITATIONS — IMPLEMENTATION AUTHORIZED
```

**Meaning (AUTHORIZATION):**

- Canonical M5 scope is determined: **Effects** — R-CORE-14 16-step Request, gates, EffectId/Digest, durable issuance, host mock, receipts (R-ORDER-02, final/04).
- Hard hinge `HostInvoked ⇒ DurableIssued` is frozen and **enforceable** via runtime→persistence→host ownership (R-DUR-01/02, R-TRUST-05).
- Addendum VII OADs (U-39…U-44) resolve prior request-pipeline blockers.
- M4 remains accepted-with-limitations; baseline green; M4 must not be rewritten for convenience.
- Implementation may proceed in a **separate M5 IMPLEMENTATION SPRINT** only within MAY above.
- M5 implementation remains **NOT STARTED** by this commit.
- Disclosed limitations (§24–§25) must be respected.
- OPEN OADs are **not** resolved by this preflight.

**Not authorized without new preflight/addendum:** M6 actors, M7 recovery, OAD closes, R-REG promotion, host-before-Issued designs, production↔reference effect coupling, alternate codecs, claiming verification/proof.

---

## 27. Commit decision

Preflight-only artifact; no M5 code; no M4 behavior change; no OAD/R-REG/canonical mutation; gates green; report complete; decision authorized-with-limitations.

```text
COMMIT = PERMITTED
```

---

## 28. Next authorized operation

```text
NEXT = M5 IMPLEMENTATION
```

Separate sprint. Deliverables (example, not exhaustive):

- `ror-core`: Effect, EffectCost, Consumable/Reserved thin types; Effect canonical encode  
- `ror-runtime`: Request CEK frames; 16-step gate driver; EffectId; Pending thin; receipt path  
- `ror-persistence`: issuance journal API + test backend (append/sync Prepared/Issued)  
- `ror-host`: HostExecutor + mock/replay/panic  
- `ror-kernel`: possession-aware authorize wiring as needed (no redesign of M4 algebra)  
- `ror-reference` + `ror-differential`: independent M5 observations  
- Short-circuit matrix; durable-before-host tests; M1–M4 regression green  
- **no** full recovery; **no** multi-actor; **no** R-REG edits  

---

## Final state board

```text
M0                         GREEN
M1 frozen subset           ACCEPTED WITH DISCLOSED EVIDENCE LIMITATIONS
M1 full                    NOT COMPLETE
M2 preflight               GREEN WITH DISCLOSED LIMITATIONS
M2 implementation          ACCEPTED WITH DISCLOSED EVIDENCE LIMITATIONS
M2 semantic verification   NOT CLAIMED
M3 preflight               GREEN WITH DISCLOSED LIMITATIONS
M3 implementation          ACCEPTED WITH DISCLOSED EVIDENCE LIMITATIONS
M3 semantic verification   NOT CLAIMED
M4 preflight               GREEN WITH DISCLOSED LIMITATIONS
M4 implementation          ACCEPTED WITH DISCLOSED EVIDENCE LIMITATIONS
M4 semantic verification   NOT CLAIMED
M5 preflight               GREEN WITH DISCLOSED LIMITATIONS
M5 implementation          NOT STARTED
R-REG                      184 × SPECIFIED
M6                         NOT STARTED
M7                         NOT STARTED
```

---

## Implementation boundary summary (for the next sprint)

| M5 target | Authority | Crate | Constraint | Auth |
|---|---|---|---|---|
| Request CEK + LTR + non-cap SC | R-CORE-14, R-CEK-03, R-EFFECT-04 | runtime | U-02 frames | **YES** |
| Effect + digest + cost | R-CALC-04/05, R-CANON-09 | core | U-21 domains | **YES** |
| Gates 5–11 | R-CAP/BUDGET/HOST | kernel+runtime+host | thin budget | **YES** |
| EffectId alloc | R-EFFECT-03 | runtime | monotonic only | **YES** |
| Durable Prepared/Issued | R-DUR-01/02/06/07 | persistence | not full WAL recovery | **YES** |
| Host execute after Issued | R-HOST-02, GI-SEC-07 | host | mock OK | **YES** |
| Receipt + completion | R-EFFECT-06/07/08 | runtime | provisional faults | **YES** |
| Reference + differential | R-REF, final/04 M5 | reference/diff | no prod import | **YES** |
| Full actors / scheduler | M6 | — | — | **NO** |
| Crash recovery / snapshots | M7 | — | — | **NO** |
| R-REG / OAD close | process | — | — | **NO** |

---

*End of M5 PREFLIGHT. Implementation is authorized only under the boundary above.*
