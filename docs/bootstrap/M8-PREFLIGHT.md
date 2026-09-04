# M8 Preflight — Differential System

**Operation ID:** `RATF-M8-PREFLIGHT-001`  
**Operation type:** M8 PREFLIGHT ONLY — no production semantic implementation; no OAD/R-REG promotion; no M9.  
**Repository:** `Abdus2023/Red-on-Rust`  
**Branch:** `arena/01a06993-red-on-rust`  

**Final authorization:**

```text
M8 PREFLIGHT = GREEN WITH DISCLOSED LIMITATIONS — IMPLEMENTATION AUTHORIZED
```

```text
NEXT = M8 IMPLEMENTATION
```

```text
M8 IMPLEMENTATION = NOT STARTED
```

Evidence labels: **FACT** | **DERIVED** | **DISCLOSED LIMITATION** | **PASS** | **PASS-DISCLOSED** | **BLOCK-***

---

## 1. Repository identity and lineage

| Item | Value | Class |
|---|---|---|
| Repository | `Abdus2023/Red-on-Rust` | FACT |
| Branch | `arena/01a06993-red-on-rust` | FACT |
| HEAD (preflight base) | `2b565180b3d21699c4e4bcc49b70df704f4736da` | FACT |
| Working tree | clean at review tip (only this report added) | FACT |
| M7 implementation | `5a0463071111edf0b106bd8635c428dfa192fd7c` | FACT |
| M7 review | `2b56518` | FACT |
| M7 classification | ACCEPTED WITH DISCLOSED EVIDENCE LIMITATIONS | FACT |
| M7 preflight | `61a9e57` | FACT |
| `61a9e57` ancestor of `2b56518` | YES | FACT |
| `5a04630` ancestor of `2b56518` | YES | FACT |
| Later commits after M7 review altering M7 semantics | **none** (HEAD = review tip) | FACT |
| M8 code | **NOT STARTED** | FACT |
| R-REG | **184 × SPECIFIED** (`reg/requirements.json` `requirement_count`; `final/08`) | FACT |
| Toolchain baseline | `ror-stable` 1.88.0 (prior milestones) | FACT |

**Lineage:**

```text
61a9e57  M7 PREFLIGHT
    ↓
5a04630  M7 IMPLEMENTATION
    ↓
2b56518  M7 REVIEW  = HEAD
```

**No production Rust semantics modified by this preflight.**

---

## 2. Authoritative M8 discovery

### 2.1 What is M8? (canonical only)

| Source | Statement | Class |
|---|---|---|
| **R-ORDER-02** / `final/01` milestone table | **M8 Differential verification** — acceptance: `Observe(P) == Observe(R)` passes | **CANONICAL** |
| **final/04** verification registry | **M8** \| generated programs, reference execution, production execution, normalized comparison, first-divergence reporting, shrinking | **CANONICAL** |
| **mod/18-ownership-matrix.md** | M8 → MOD-15 DIFFERENTIAL, MOD-14 REFERENCE; same surface list | **CANONICAL** (ownership projection of frozen milestone) |
| **spec/07** implementation mapping | M8 Differential system \| R-REF-01…06, R-TEST-02…03, R-TEST-07 \| `ror-differential`, `ror-reference` | **CANONICAL** (mapping) |
| **mod/15-differential.md** | Full differential system: generation, both executions, normalized comparison, first-divergence, shrinking | **CANONICAL** module home prose |
| **mod/14-reference.md** | Reference independence + Observe equality (gate executed by MOD-15) | **CANONICAL** |
| `docs/bootstrap/M7-REVIEW.md` NEXT=M8 | process handoff only | **BOOTSTRAP** (not semantic authority) |
| `Red-on-Rust.md` “Phase 8” CEK prose | historical narrative / alternate numbering | **HISTORICAL** — **not** M8 milestone authority |
| Implementation convenience (“finish all diffs”) | — | **UNKNOWN** / non-authority |

**M8 name (frozen acceptance, R-ORDER-02):**

```text
M8 Differential verification — Observe(P) == Observe(R) passes
```

**M8 verification surface (final/04):**

```text
generated programs,
reference execution,
production execution,
normalized comparison,
first-divergence reporting,
shrinking
```

**No alternate M8 interpretation is selected.** Historical “Phase 8 evaluator” text is explicitly **out of scope** for this milestone.

---

## 3. M8 authority map (projection)

| M8 item | Canonical source | Requirement IDs | Normative level | Security | Impl target | Test / evidence | Related OAD / UNKNOWN |
|---|---|---|---|---|---|---|---|
| Milestone acceptance | R-ORDER-02 | R-ORDER-02 | MUST | LOW | process + harness | Observe_P=Observe_R gate | — |
| Observe equality | R-REF-01 | R-REF-01 | MUST | MEDIUM | differential + reference | differential suite | F-04 Observed* |
| Recovery observe equality | R-REF-01 | R-REF-01 | MUST (persistence domain) | HIGH | m7 path + generator | recovery fixtures | U-02/U-32 |
| Reference independence | R-REF-02; R-SCOPE-04; GI-SEC-19 | R-REF-02, R-SCOPE-04 | MUST | CRITICAL | `ror-reference` | dep graph review | — |
| Reference models 12 areas | R-REF-03 | R-REF-03 | MUST | MEDIUM | `ror-reference` | area coverage | thin areas disclosed |
| Reference non-goals | R-REF-04 | R-REF-04 | MUST | MEDIUM | reference | review | — |
| Normalized observations + first divergence | R-REF-05 | R-REF-05 | MUST | HIGH | `ror-differential` | comparator tests | **F-04 UNKNOWN** |
| PanicHost / MockKernel harness | R-REF-06 | R-REF-06 | MUST | CRITICAL | testkit + diff | hinge tests | — |
| Independent verification arch | R-ARCH-02 | R-ARCH-02 | MUST | HIGH | differential | structural | — |
| Execution modes baselines | R-TEST-01 | R-TEST-01 | MUST (suite modes) | LOW | tests / differential | exhaustive/property/stress | U-35 carry |
| 16-field counterexample artifact | R-TEST-02 | R-TEST-02 | MUST | MEDIUM | `ror-differential` | artifact schema tests | field encoding provisional |
| Shrinking 10 priorities | R-TEST-03 | R-TEST-03 | MUST | MEDIUM | `ror-differential` | shrink tests | — |
| Obligation-tagged coverage | R-TEST-07 (+ R-TEST-12 tags) | R-TEST-07, R-TEST-12 | MUST | MEDIUM | differential | coverage report | metrics ≠ oracle |
| Fault adjudication 4-way | R-TEST-09 | R-TEST-09 | MUST (on divergence) | HIGH | process + harness | classification enum | — |
| Zero shared transition code | R-SCOPE-04 | R-SCOPE-04 | MUST | CRITICAL | reference | import/dep review | — |

**Atomic obligations (derived from final/04 + R-REF/R-TEST, not new norms):**

1. **Generate** programs / cases in the comparison domain (seeded, reproducible).  
2. **Execute production** as black-box SUT → normalized observation.  
3. **Execute reference** independently → normalized observation.  
4. **Compare** normalized observations (not final-value-only).  
5. **Report first divergence** (index + both sides + classification hook).  
6. **Shrink** failures per R-TEST-03 order; preserve failure predicate.  
7. **Emit** R-TEST-02 counterexample artifact (16 fields; runnable).  
8. **Track** R-TEST-07 obligation tags (evidence; never replace oracle).  
9. **Preserve** R-REF-02 independence and M5 hinge on all host-touching cases.  
10. **Include** recovery differential cases already required by R-REF-01 (Canonical Recover_P = Recover_R) within the M8 system surface where generation reaches persistence images.

**No M8 item without canonical authority was invented.**

---

## 4. Exact M8 scope

### 4.1 M8 IN-SCOPE

| Surface | Authority |
|---|---|
| Differential **system** in `ror-differential` (generator, runner, comparator, shrinker, artifacts) | final/04; mod/15; R-REPO-02 |
| Independent reference execution paths already modeled (extend only as needed for generated domain) | R-REF-03; mod/14 |
| Normalized observation model + first-divergence reporter | R-REF-05 |
| Seeded program/case generation for comparison domain | R-TEST-01/02; mod/15 |
| Shrinking protocol (10 ordered priorities) | R-TEST-03 |
| Reproducible 16-field counterexample artifacts | R-TEST-02 |
| Obligation-tag coverage reporting (evidence) | R-TEST-07 / R-TEST-12 |
| Harness boundary doubles (PanicHost / mock authorize) where cases touch effects | R-REF-06 |
| Integration of existing M2–M7 pairwise diffs under the system (regression + expansion) | DERIVED from R-REF-01 continuity |
| Divergence adjudication hooks (4-way enum) | R-TEST-09 |

### 4.2 M8 OUT-OF-SCOPE

| Item | Why |
|---|---|
| **M9** mutation registry kill-rate 100% | R-ORDER-02 M9; R-TEST-05 |
| **M10** crash/recovery **gate** (full T0–T6 acceptance) | R-ORDER-02 M10; R-TEST-08 as M10 gate (M7 already delivered recovery engine + partial diff) |
| **M11** release candidate | R-ORDER-02 |
| Closing OADs / F-04 | governance |
| Promoting R-REG | governance |
| Redesigning M5/M6/M7 production semantics | upstream accepted |
| New production evaluator / host / agent features “for better diffs” | not M8 |
| Formal proof of Observe equality | R-REF-01: evidence ≠ proof |
| Using coverage metrics as oracle | R-TEST-07 forbidden |
| Sharing production transition code into reference | R-REF-02 / R-SCOPE-04 |
| Historical Red-on-Rust.md “Phase 8” CEK rewrite | HISTORICAL, not R-ORDER-02 M8 |
| CI pipeline productization (R-TEST-10 full) | verification contract; M8 may emit artifacts/hooks but full CI gates are process/M11-adjacent — **disclose** thin local runner OK |

### 4.3 M8 DEPENDENCIES (upstream inputs)

| Input | Status |
|---|---|
| M1 canonical bytes / digests | accepted prior |
| M2–M3 CEK + lambda | accepted |
| M4 capability algebra | accepted |
| M5 effects + **HostInvoked⇒DurableIssued** | accepted; **immutable hinge** |
| M6 actors / mailbox / scheduler | accepted |
| M7 WAL/snapshot/recovery + independent recovery ref | accepted with disclosures |
| `ror-reference` independence | intact |
| `ror-differential` M2–M7 modules | present (partial system) |

### 4.4 M8 SECURITY CRITICAL PATHS

| Path | Rule |
|---|---|
| Generated case → production host | **MUST** go through ordinary M5 issuance; no harness shortcut to `execute` |
| PanicHost / negative cases | R-REF-06; host before Issued must panic/fail |
| Reference path | never calls production host/kernel/persistence |
| Differential crate | verification dependency only; not a production authority |
| Artifact / seed handling | untrusted input to **harness**, not to capability authority |
| Recovery images in generated cases | recover-only; no effect re-exec (R-RECOV-08) |

### 4.5 M8 DETERMINISM REQUIREMENTS

| Requirement | Authority |
|---|---|
| Same seed + generator_version → same case | R-TEST-02 |
| Observe equality independent of wall-clock / thread / env | R-CORE-08; R-REF-05 excludes non-semantic internals |
| Shrink steps deterministic given failure predicate | R-TEST-03 |
| No HashMap-order in normalized observations | R-CORE-08 spirit; DERIVED operational |
| U-35 | theorem parameters still open — **operational** determinism required; unqualified theorem not claimed |

### 4.6 M8 REQUIRED TESTING / REFERENCE / DIFFERENTIAL / MUTATION / EVIDENCE

| Family | Required? | Notes |
|---|---|---|
| Unit (generator, shrink, artifact, comparator) | YES | ror-differential |
| Integration (prod+ref run) | YES | existing m2–m7 + generated |
| Property / seeded generation | YES | R-TEST-01 property mode baseline (thin bounds OK if disclosed) |
| Differential (core) | YES | **is** M8 |
| First-divergence tests | YES | R-REF-05 |
| Shrink predicate preservation | YES | R-TEST-03 |
| Security / hinge | YES | R-REF-06 + M5 regression |
| Failure / malformed gen | YES | fail-closed harness |
| Mutation **kill-rate gate** | **NO** (M9) | may register **intents** only |
| Crash matrix gate | **NO** (M10) | may include recovery cases as R-REF-01 subset |
| Reference model | YES | must remain independent (R-REF-02) |
| Evidence | Observe agreement artifacts + coverage report + shrink minima | not proof |

---

## 5. OAD / UNKNOWN analysis

| ID | Issue | Status | M8 dependency | Proceed without close? | Constraint |
|---|---|---|---|---|---|
| **F-04** | `Observed*` comparison domain undeclared | UNKNOWN (final/01) | **Yes** — R-REF-05 types | **Yes** if provisional observation schema + explicit non-freeze | Same pattern as M5/M6/M7 provisional codecs |
| **U-35** | Determinism theorem parameters undefined | OPEN | Operational det. only | **Yes** | Do not claim theorem discharge |
| **U-02** | Machine-state codecs | OPEN | Recovery cases / artifacts | **Yes** | Reuse M7 provisional; no freeze |
| **U-17** | Runnable queue persist vs reconstruct | OPEN | Actor observe / recovery | **Yes** | Match M7 reconstruct choice in observe |
| **U-32** | WalFrame layout / checksum domain | OPEN | Persistence generation | **Yes** | Byte-compatible with M7 provisional |
| **U-27 / U-30** | Pending locus / mailbox wire | OPEN | Actor observe | **Yes** | Thin labels |
| **U-34** | State struct variants | OPEN | Observation field set | **Yes** | Provisional struct fields |
| **U-08 / U-14** | Fault label unification | residual | Fault observe | **Yes** | Compare declared fault codes, not debug text (R-CORE-13) |
| U-06 residual | Recon class table | OPEN | Recovery observe | **Yes** | Do not invent NotExecuted |

**Critical rule applied:** open OAD may be implemented around only with explicit provisional path — **authorized by M5–M7 milestone pattern** and final/01 recording F-04 as UNKNOWN without blocking SPECIFIED R-REF-05 obligations.

**No OAD must be closed before M8. No BLOCK-GOVERNANCE.**

If implementation **claims** Observed* frozen or closes F-04/U-*: **would become BLOCK-GOVERNANCE** mid-impl — preflight forbids that claim.

---

## 6. M7 baseline integrity

| Invariant | Still required | Intact at HEAD? |
|---|---|---|
| Prepared ∧ ¬Issued ⇒ Discard | YES | YES (M7 review) |
| Issued ∧ ¬Completed ⇒ Indeterminate | YES | YES |
| Indeterminate ≠ NotExecuted | YES | YES |
| Completed ⇒ reconstruct without host re-exec | YES | YES |
| Recovery ↛ original-effect re-exec | YES | YES |
| HostInvoked(E) ⇒ DurableIssued(E) | YES **permanent** | YES |

M8 **must not** redefine these. Differential cases that touch effects/recovery must **assert** them.

---

## 7. M5 security hinge (permanent)

```text
HostInvoked(E) ⇒ DurableIssued(E)     (R-DUR-01 / GI-SEC-07 / R-CORE-06)
```

### M8 interaction map

| M8 activity | Touches host? | Required chain |
|---|---|---|
| Pure CEK / lambda generation | no | n/a |
| Capability / attenuate cases | kernel only | existing M4 path |
| Effect / Request generation | **yes** | validate → auth → budget → Prepared+sync → Issued+sync → host → receipt |
| Actor/scheduler cases | no direct host | M6 path |
| Recovery image cases | **no host** | `recover(D)` only |
| PanicHost negative | host must **not** run if gates fail | R-REF-06 |

**Forbidden:**

```text
M8 harness → HostExecutor::execute
M8 generator → skip Issued
M8 shrinker → re-enter host without gates
reference → production host
```

**No BLOCK-SECURITY** found in planned scope (verification-only crate edges).

---

## 8. Reference-model requirements

| Requirement | Status at HEAD | M8 duty |
|---|---|---|
| Independent reference | PASS (core-only Cargo) | preserve |
| R-REF-03 twelve areas | CEK, caps, effects, actors, recovery present; budgets/persistence thin | extend observations; **not** redesign production |
| R-REF-04 non-goals | documented | no second codec ontology; no shared transitions |
| Forbidden edges | all `present: false` in dep graph | keep |

```text
ror-reference ↛ ror-runtime | kernel | persistence | host | agent
```

**Feasible:** YES — existing independent models + M2–M7 diffs.

---

## 9. Dependency authority

### Convention reminder

Canonical graph edges are recorded as `provider → consumer` meaning **consumer depends on provider**.

### M8-relevant edges

| Edge | Kind | Status |
|---|---|---|
| ror-core → ror-reference | REQUIRED | present |
| ror-core → ror-differential | via members | present |
| ror-reference → ror-differential | VERIFICATION | present |
| ror-runtime → ror-differential | VERIFICATION (black-box SUT) | present |
| ror-persistence → ror-differential | VERIFICATION (SUT observe) | present |
| ror-host → ror-differential | VERIFICATION | present |
| ror-testkit → ror-differential | VERIFICATION | present |
| ror-reference → ror-persistence | **FORBIDDEN** | absent |
| ror-reference → ror-runtime | **FORBIDDEN** | absent |
| ror-runtime → ror-reference | **FORBIDDEN** | absent |

**M8 provider crates:** `ror-differential` (harness), `ror-reference` (oracle).  
**M8 consumer of production:** differential only (observation).  
**New crate:** **NOT REQUIRED.**  
**FORBIDDEN/UNCLASSIFIED edge proposed:** none.

**G-dep = PASS.**

### Module ownership

| Module | Crate | M8 role |
|---|---|---|
| MOD-15 DIFFERENTIAL | `ror-differential` | **primary implementation home** |
| MOD-14 REFERENCE | `ror-reference` | independent execution / observe |
| MOD-16/17 | testkit / verification | doubles, optional coverage hooks |
| MOD-05/08/06/11/12 | production | **SUT only** — not rewritten for M8 |

---

## 10. Trust-boundary analysis

```text
Untrusted Input (seeds, generated programs, artifact files)
        ↓
Harness Authority (validate case, bounds, no cap minting)
        ↓
Production SUT / Reference (separate)
        ↓
Normalized Observation (no raw caps as authority)
        ↓
Comparator / Artifact (evidence)
```

| Object | Trust |
|---|---|
| Generator seed | untrusted input to harness |
| Generated Expr / topology | untrusted **data** until admitted by production gates |
| Capability in production | trusted only via kernel possession | 
| Host execute | external effect — M5 gated only |
| Reference observation | evidence, not production authority |
| Coverage metrics | evidence, not oracle |

**No Untrusted→Authority or Untrusted→ExternalEffect bypass** in M8 design surface.

---

## 11. Status / R-REG discipline

```text
requirement_count = 184
status ladder = SPECIFIED → IMPLEMENTED → TESTED → VERIFIED → PROVEN
current distribution = 184 × SPECIFIED
```

**Preflight promotes nothing.**  
M8 implementation ≠ IMPLEMENTED evidence in R-REG.

---

## 12. Current implementation surface (read-only)

| Finding | Classification |
|---|---|
| `ror-differential` m2…m7 pairwise `compare_*` | **M8 PREREQUISITE** / partial system |
| `ror-reference` pure_cek, cap_algebra, effect_model, actor_model, recovery_model | **M8 PREREQUISITE** |
| PanicHost / hinge tests in runtime + differential | **AUTHORIZED EXISTING** (R-REF-06 fragment) |
| Program **generator** | **M8 GAP** |
| **Shrinker** (10 priorities) | **M8 GAP** |
| **16-field** counterexample artifact type | **M8 GAP** |
| Unified **first-divergence** reporter (multi-trace) | **M8 GAP** (pairwise equality only today) |
| R-TEST-07 coverage report aggregator | **M8 GAP** (tags exist in tests ad hoc) |
| `ror-testkit` nearly empty | **M8 PREREQUISITE thin** — doubles may live in differential/reference as today |
| Full R-TEST-01 stress floors | **M8 OUT-OF-SCOPE / disclosed thin** optional subset |
| M9 mutation runner | **M8 OUT-OF-SCOPE** |
| TODO/unimplemented! M8 engine | absent (gap by absence, not stub markers) |

**No POTENTIAL CONFLICT** requiring BLOCK: existing m2–m7 are compatible substrates to unify under M8 system APIs.

---

## 13. Security-critical M8 surfaces (plan)

| Surface | Authority | Trust | Invariant | Failure mode | Test | Mutation intent |
|---|---|---|---|---|---|---|
| Host path in generated Request | R-DUR-01 | SUT | Issued before host | hinge break | PanicHost cases | host-before-Issued |
| Comparator ignoring traces | R-REF-05 | harness | first divergence | false PASS | multi-event fixtures | final-value-only compare |
| Shared transition import | R-REF-02 | build | independence | oracle collapse | dep/import CI | add forbidden dep |
| Shrink drops failure | R-TEST-03 | harness | predicate preserve | bad minimal | shrink tests | skip predicate check |
| Artifact non-reproducible | R-TEST-02 | harness | seed replay | flaky | replay artifact | drop seed field |
| Coverage as pass | R-TEST-07 | process | metrics ≠ oracle | false confidence | doc + API | — |
| Recovery re-exec in case | R-RECOV-08 | SUT | no re-host | security | recovery fixtures | call host in recover |

---

## 14. Failure / fail-closed requirements

| Condition | Canonical direction | M8 harness duty |
|---|---|---|
| Malformed generated program | production Fault | observe Fault both sides / adjudicate |
| Missing/expired cap | Unauthorized | agree deny; no host |
| Persistence failure mid-issue | R-DUR-07 | no host; agree |
| Host failure after Issued | HostFailed path | agree classification |
| Spec ambiguity on diverge | R-TEST-09 | classify **specification ambiguity**; do not patch oracle |
| Corrupt durable image in case | R-RECOV-05 | both recover fail closed |
| Impossible transition | Fault | agree |

Where error **labels** remain U-08/U-14 open: compare **stable codes**, disclose provisional mapping — **PASS-DISCLOSED**, not BLOCK.

---

## 15. Test-plan readiness (projection only)

| Family | Canonical req | Target | Observable | Failure class |
|---|---|---|---|---|
| Generator unit | R-TEST-02 | differential | seed→case stable | FAIL-IMPLEMENTATION (later) |
| Comparator unit | R-REF-05 | differential | first divergence index | |
| Shrink unit | R-TEST-03 | differential | minimal + predicate | |
| Artifact schema | R-TEST-02 | differential | 16 fields present; replay | |
| Exhaustive small-state | R-TEST-01 | differential | bounds depth≤4, actors≤2, caps≤2 | |
| Property seeded | R-TEST-01 | differential | N seeds agree | |
| M2–M7 regression | prior | differential | all green | BLOCK-REGRESSION if broken |
| Hinge security | R-REF-06 / R-DUR-01 | runtime+diff | panic / no host | BLOCK-SECURITY |
| Independence structural | R-REF-02 | reference Cargo | no forbidden deps | BLOCK-INDEPENDENCE |
| Coverage report | R-TEST-07 | differential | tag map emitted | evidence only |
| Adjudication enum | R-TEST-09 | differential | 4-way on forced diverge | |

**Tests not written in this preflight.**

---

## 16. Mutation-plan readiness

| Intent | Class |
|---|---|
| Host before Issued in harness path | **CANONICAL** (R-REF-06 / GI-SEC-07) |
| Final-value-only comparator | **CANONICAL** (R-REF-05) |
| Forbidden reference→persistence dep | **CANONICAL** (R-REF-02) |
| Shrink without predicate check | **CANONICAL** (R-TEST-03) |
| Drop seed from artifact | **CANONICAL** (R-TEST-02) |
| Patch reference to match prod on diverge | **CANONICAL** (R-TEST-09) |
| Full M001–M042 kill suite | **NOT AUTHORIZED** in M8 (M9) |
| Skip WAL checksum in prod | M7/M9-adjacent; **NOT** M8 primary |

M8 may **execute** security intents above as harness self-tests; **must not** claim R-TEST-05 kill-rate.

---

## 17. Gate board

| Gate | Status | Notes |
|---|---|---|
| G-01 Identity / lineage | **PASS** | HEAD=2b56518; ancestors OK |
| G-02 Canonical M8 discovery | **PASS** | R-ORDER-02 + final/04; Phase-8 historical rejected |
| G-03 Authority map completeness | **PASS-DISCLOSED** | F-04 Observed* UNKNOWN; provisional path |
| G-04 Scope containment | **PASS** | M9/M10/M11 excluded |
| G-05 M7 baseline / invariants | **PASS** | review accepted; invariants listed |
| G-06 M5 hinge compatibility | **PASS** | no M8→Host bypass in scope |
| G-07 Reference independence feasible | **PASS** | edges clean; models exist |
| G-08 Dependency / ownership | **PASS** | MOD-15/14; no forbidden edge |
| G-09 Trust boundary | **PASS** | verification harness only |
| G-10 Determinism | **PASS-DISCLOSED** | ops required; U-35 open |
| G-11 OAD governance | **PASS** | none forced closed; provisional OK |
| G-12 R-REG | **PASS** | 184 SPECIFIED |
| G-13 Implementation surface readiness | **PASS-DISCLOSED** | generator/shrink/artifact GAP expected |
| G-14 Test/mutation plan readiness | **PASS-DISCLOSED** | plan defined; not executed |
| G-15 Security critical paths | **PASS** | mapped; hinge preserved |
| G-16 Fail-closed | **PASS-DISCLOSED** | U-08/14 labels residual |

**BLOCKS = 0.**

---

## 18. Authorization criteria

| Criterion | Met? |
|---|---|
| Canonical M8 scope identified | **yes** |
| No unresolved canonical conflict blocks impl | **yes** (F-04 → provisional) |
| Dependency graph sufficient | **yes** |
| Security boundaries explicit | **yes** |
| M7 regression baseline intact | **yes** |
| Reference-model strategy feasible | **yes** |
| Differential surface identifiable | **yes** |
| Test surface identifiable | **yes** |
| Required OAD closures unnecessary or already closed | **yes** (none required closed) |
| No governance violation | **yes** |

```text
M8 PREFLIGHT = GREEN WITH DISCLOSED LIMITATIONS — IMPLEMENTATION AUTHORIZED
```

```text
NEXT = M8 IMPLEMENTATION
```

```text
M8 IMPLEMENTATION = NOT STARTED
```

---

## 19. Disclosed limitations

| ID | Limitation |
|---|---|
| F-04 | `Observed*` domain not frozen — provisional normalized observation schema required |
| U-35 | Determinism theorem parameters open — operational det. only |
| U-02/U-17/U-32 | Carry for persistence/recovery cases |
| U-27/U-30/U-34 | Actor/observe struct thin |
| U-08/U-14 | Fault label residual |
| L-M8-PARTIAL-NOW | m2–m7 pairwise ≠ full generator/shrink/artifact system |
| L-M8-TESTKIT-THIN | ror-testkit empty; doubles may remain in-crate |
| L-M8-CI | Full R-TEST-10 CI product not required to finish M8 code surface |
| L-M8-NO-PROOF | Observe equality is evidence, not proof (R-REF-01) |
| M5–M7 carry | prior disclosures remain |

---

## 20. Explicit non-claims

```text
M8 is not implemented.
Observe(P)==Observe(R) is not verified by this preflight.
Generator/shrinker/artifacts do not yet exist as a complete system.
F-04 is not closed.
No OAD is closed.
R-REG remains 184 × SPECIFIED.
M9 mutation kill-rate is not authorized.
M10 crash gate is not authorized.
Differential agreement will be evidence, not proof.
M5 HostInvoked ⇒ DurableIssued remains mandatory.
Reference independence remains mandatory.
No production semantic implementation was performed by this preflight.
```

---

## 21. Final state board

```text
M0–M4                      prior accepted
M5                         ACCEPTED WITH DISCLOSED EVIDENCE LIMITATIONS
M6                         ACCEPTED WITH DISCLOSED EVIDENCE LIMITATIONS
M7                         ACCEPTED WITH DISCLOSED EVIDENCE LIMITATIONS
M8 preflight               GREEN WITH DISCLOSED LIMITATIONS — IMPLEMENTATION AUTHORIZED
M8 implementation          NOT STARTED
R-REG                      184 × SPECIFIED
NEXT                       M8 IMPLEMENTATION
```

---

## 22. Selected evidence records

### Evidence Record: G-02

- **Gate:** Canonical M8 discovery  
- **Status:** PASS  
- **Canonical authority:** R-ORDER-02; final/04 M8 row; mod/18 M8 row  
- **Canonical rule:** Differential verification system; Observe(P)==Observe(R)  
- **Observed repository state:** consistent across final/01, final/04, mod/15, spec/07  
- **Evidence:** rg + section read  
- **Limitation:** Red-on-Rust.md Phase 8 is HISTORICAL noise — discarded  
- **Conclusion:** M8 scope uniquely identified; no multi-interpretation block.

### Evidence Record: G-03

- **Gate:** Authority completeness / F-04  
- **Status:** PASS-DISCLOSED  
- **Canonical authority:** R-REF-05 SPECIFIED; F-04 UNKNOWN  
- **Canonical rule:** normalized observations required; domain types undeclared  
- **Limitation:** provisional Observed schema at impl without freeze  
- **Conclusion:** Same governance pattern as U-02/U-32 on M7 — not BLOCK.

### Evidence Record: G-06

- **Gate:** M5 hinge vs M8  
- **Status:** PASS  
- **Canonical authority:** R-DUR-01; GI-SEC-07; R-REF-06  
- **Canonical rule:** no host without DurableIssued; PanicHost in harness  
- **Conclusion:** M8 is verification; must not add Host bypass.

### Evidence Record: G-01

- **Gate:** Lineage  
- **Status:** PASS  
- **Evidence:** HEAD `2b56518`; ancestors `61a9e57`, `5a04630`  
- **Conclusion:** M8 starts from accepted M7 review tip.

---

*End of M8 PREFLIGHT. Do not begin M8 implementation in this operation.*
