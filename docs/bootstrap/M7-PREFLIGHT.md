# M7 Preflight — Persistence / WAL / Snapshot / Crash Recovery

**Operation type:** M7 PREFLIGHT ONLY — no production semantic implementation.  
**Final authorization:**

```text
M7 PREFLIGHT = GREEN WITH DISCLOSED LIMITATIONS — IMPLEMENTATION AUTHORIZED
```

```text
NEXT = M7 IMPLEMENTATION
```

Evidence labels: **FACT** | **DERIVED** | **DISCLOSED LIMITATION** | **PASS** | **PASS-DISCLOSED** | **BLOCK-***

---

## 1. Operation identity

| Item | Value | Class |
|---|---|---|
| Repository | `Abdus2023/Red-on-Rust` | FACT |
| Branch | `arena/01a06993-red-on-rust` | FACT |
| HEAD (preflight base) | `ea113657d4067117aeec4d5f910825ce08002110` | FACT |
| Working tree | clean at review tip | FACT |
| M6 review disposition | ACCEPTED WITH DISCLOSED EVIDENCE LIMITATIONS (`ea11365`) | FACT |
| M7 code | **NOT STARTED** | FACT |
| R-REG | **184 × SPECIFIED** | FACT |
| Toolchain | `ror-stable` rustc/cargo/fmt/clippy **1.88.0** | FACT |
| Baseline gates | fmt / check / test --lib / clippy `-D warnings` all **exit 0** | FACT |

**Production Rust semantics were not modified by this preflight.**

---

## 2. Git lineage (verified)

```text
f178562  M5 implementation
    ↓
7e6eb44  M5 implementation review
    ↓
9e8b8ca  M6 preflight
    ↓
2d89cae  M6 implementation
    ↓
e9c2fa5  M6 addendum evidence
    ↓
ea11365  M6 implementation review  = HEAD
```

All six SHAs are ancestors of HEAD (`git merge-base --is-ancestor`). **G-01/G-02 PASS.**

---

## 3. M6 review disposition (input)

| Item | State |
|---|---|
| M6 review | ACCEPTED WITH DISCLOSED EVIDENCE LIMITATIONS |
| Actor states | RUNNABLE / BLOCKED / PENDING / TERMINAL |
| Quiescence | Deadlock ∧ ∃Pending ⇒ QuiescenceReconcile; Indeterminate; δ_t=0 |
| M5 hinge | INTACT — no Actor→Host path |
| Bare CEK actor forms | require GlobalState (disclosed) |
| R-REG / OADs | unchanged |

M6 is an **upstream input**, not a redesign target.

---

## 4. Canonical authority inventory

| Domain | Primary homes | Status |
|---|---|---|
| Milestone name | R-ORDER-02 / final/04 M7 row | **FROZEN** |
| Persistence separation | R-PERSIST-01 | SPECIFIED |
| WAL framing / checksum | R-PERSIST-02, R-PERSIST-08 | SPECIFIED (layout detail U-32 OPEN) |
| Record taxonomy | R-PERSIST-03 (+ R-DUR-06 payload) | SPECIFIED |
| Snapshot content / atomic commit | R-PERSIST-04, R-PERSIST-05 | SPECIFIED (encoding U-02 OPEN) |
| Sequence continuity | R-PERSIST-06 | SPECIFIED |
| Authority lattice durability | R-PERSIST-07 | SPECIFIED |
| HostInvoked⇒DurableIssued | R-DUR-01 / R-CORE-06 / GI-SEC-07 | SPECIFIED — **IMMUTABLE** |
| Issuance transaction | R-DUR-02, R-DUR-06, R-DUR-07 | SPECIFIED |
| Causal journal | R-DUR-03 | SPECIFIED |
| Crash effect classification | R-DUR-04 | SPECIFIED |
| Escrow survival | R-DUR-05 | SPECIFIED |
| Durable state D=⟨S,L,H⟩ | R-RECOV-01 | SPECIFIED |
| Crash matrix T0–T6 | R-RECOV-02 | SPECIFIED |
| 12-step recovery | R-RECOV-03 | SPECIFIED |
| Independent recovery | R-RECOV-04 | SPECIFIED |
| No silent repair | R-RECOV-05 / R-CORE-10 | SPECIFIED |
| Budget recovery | R-RECOV-06 | SPECIFIED |
| Reconciliation | R-RECOV-07, R-RECOV-08 | SPECIFIED |
| Reconstruction authority | R-RECOV-09 | SPECIFIED |
| Receipt / host | R-HOST-04/06, R-EFFECT-06/07/08 | SPECIFIED |
| Ownership | mod/11 PERSISTENCE, mod/12 RECOVERY → `ror-persistence` | FACT |
| Dependencies | dep/10-graph.json; runtime→persistence REQUIRED | FACT |
| Evidence tags | final/04 WAL-*, RECOVERY-*, SNAPSHOT-*, EFFECT-ISSUE-* | FACT |
| OAD registry | final/09; spec/09 | FACT |

**No new normative text authored.** Bootstrap consumes final/*.

---

## 5. What is M7? (authority-derived)

Canonical M7 name (**R-ORDER-02** / final/04):

```text
M7 Persistence — WAL frame encoding, sequence continuity, snapshot commit pass
```

final/04 verification row expands:

```text
WAL, snapshot, effect journal, checksum, sequence continuity, recovery
```

**M7 REQUIRED surfaces (DERIVED from SPECIFIED obligations):**

1. WAL two-level framing + checksum + sequence continuity (R-PERSIST-02/06/08)  
2. Unified journal record kinds (R-PERSIST-03; R-DUR-06 payloads)  
3. Atomic snapshot protocol + content obligations (R-PERSIST-04/05)  
4. Durable authority lattice (R-PERSIST-07)  
5. Recovery engine `Recover(D)=Replay(S,L,H)` (R-RECOV-01/03)  
6. Normative crash matrix T0–T6 (R-RECOV-02)  
7. Effect classification Prepared∧¬Issued⇒Discard; Issued∧¬Completed⇒Indeterminate (R-DUR-04)  
8. Reconciliation protocol without re-execution / without local NotExecuted (R-RECOV-07/08)  
9. ID reconstruction `next_effect_id` (R-RECOV-09)  
10. Independent reference recovery (R-RECOV-04; R-REF-02)  
11. Crash harness / differential recovery evidence (final/04)  
12. Preserve M5 hinge and M6 actor semantics as inputs  

**M7 MUST NOT:** redesign capability algebra, effect gates, actor/scheduler policy, close OADs, promote R-REG, invent host bypasses, invent Pending cancellation, invent message-to-dead policy.

---

## 6. M5 durability baseline (immutable input)

### Existing production path (FACT)

| Step | Location |
|---|---|
| authorize / budget / deadline / host policy | `ror-runtime/src/effects.rs` `run_effect_pipeline` |
| EffectId alloc | `ror-core::effect::EffectIdAlloc` |
| Prepared append + sync | `IssuanceJournal` / `MemoryJournal` |
| Issued append + sync | same |
| Host only after durable Issued | `is_durably_issued` assert; then `host.execute` |
| Receipt / Completed | M5 thin; full durable Completed path is M7 depth |

### R-DUR-02 strict order (canonical)

```text
1 pure validation/auth/budget
2 append EffectPrepared
3 sync
4 append EffectIssued
5 sync
6 actor → Pending
7 host receives EffectRequest
```

### R-DUR-06 payload (canonical)

Prepared/Issued carry `effect_bytes` + cost triple + digest (not observation-only `{id,actor,digest}`).

**M5 `MemoryJournal` is a thin in-memory hinge test journal — not the full WAL/snapshot engine.** M7 extends `ror-persistence` without replacing the hinge API contract.

---

## 7. M5 security hinge — IMMUTABLE

```text
HostInvoked(E) ⇒ DurableIssued(E)     (R-DUR-01 / GI-SEC-07)
```

### M7 recovery MUST NOT create

```text
recovery → host
replay → host
snapshot restore → host
WAL replay → host
actor recovery → host
scheduler recovery → host
receipt recovery → host
```

**except** through the existing issuance boundary when R-RECOV-08 authorizes an **idempotent host query** (not re-execution of the original effect) or a **new ordinary Request** through gates 1–16.

| Rule | Authority |
|---|---|
| Reconciliation NEVER re-executes | R-RECOV-08 |
| NotExecuted only with authoritative host-reconciliation evidence | R-RECOV-08; R-DUR-04; N-24 |
| Supervisor.host only via issuance boundary | R-RECOV-08 |
| No silent Indeterminate→NotExecuted | R-DUR-04 |

**Hinge vs recovery:** **compatible** — T2/T3/T4 become Indeterminate; host is not freely re-invoked. **M5 HINGE = INTACT.** No BLOCK-SECURITY / no BLOCK-CANONICAL conflict found.

---

## 8. Recovery state machine (authority-extracted — not invented)

### Durable effect lifecycle (R-DUR-03/04)

```text
Prepared → Issued → Completed
                 ↘ Reconciled
```

| State | Durability | Crash/restart | Host permission | Terminal? |
|---|---|---|---|---|
| *(absent)* | none | T0: effect does not exist | never | n/a |
| Prepared ∧ ¬Issued | Prepared only | T1: **Discard** | never | discard |
| Issued ∧ ¬Completed | Issued | T2–T4: **Indeterminate** | only via R-RECOV-08 | open until Reconciled/Completed |
| Completed | Completed | T5: complete; resume | no re-host | terminal success path |
| Reconciled | EffectReconciled | settled under admissibility table | no re-exec | terminal settle |
| Indeterminate | classification | not a free host path | R-RECOV-08 only | transient bound by R-BUDGET-09/16 |

**Indeterminate ≠ NotExecuted** (N-24). **Pending** (actor status, M6) is distinct from journal Indeterminate but must align at recovery (actor waiting on Issued effect).

### Global durable state (R-RECOV-01)

```text
D = ⟨S, L, H⟩
Recover(D) = Replay(S, L, H)
```

### 12-step recovery (R-RECOV-03) — summary

1 locate newest committed snapshot → 2 verify frame/checksum → 3 15A decode → 4 validate GlobalState invariants → 5 open WAL → 6 sequence continuity → 7 replay after snapshot seq → 8 reconstruct effect journal / causal chains → 9 classify interrupted effects → 10 reconstruct runnable queue → 11 digest vs checkpoint → 12 RecoveryComplete; resume scheduler.

**Never silently repair** (R-RECOV-05).

---

## 9. Crash-point inventory (R-RECOV-02 T0–T6)

| ID | Crash point | Durable before | After restart | Replay | Host | Receipt |
|---|---|---|---|---|---|---|
| **T0** | before Prepared | none | effect absent; no budget mut; normal CEK | none | never | n/a |
| **T1** | after Prepared (incl. failed Issued sync) | Prepared only | **Discard** prep; normal CEK; no host recon | discard path | never | n/a |
| **T2** | after Issued | Issued | **Indeterminate**; await recon | journal reconstruct | R-RECOV-08 only | missing |
| **T3** | after HostInvocation | Issued | **Indeterminate** | same | R-RECOV-08 only | missing |
| **T4** | after HostCompletion before Completed durable | Issued | **Indeterminate** (R-RECOV-09) | same | R-RECOV-08 only | may exist volatile |
| **T5** | after Completed durable | Completed | complete; byte-exact resume | no re-host | no | verified digests |
| **T6** | after SnapshotCommit | SnapshotCommit (+ prior) | clean resume from S + later L | replay post-S | per effects in L/H | per journal |

**Additional live failure points (R-DUR-07):** append/sync error before Issued ⇒ pre-s12 state; Host never invoked. Second sync failure ⇒ Prepared∧¬Issued ⇒ Discard at recovery (T1).

**Evidence tags:** EFFECT-ISSUE-DURABLE-BEFORE-HOST; RECOVERY-ISSUED-INDETERMINATE; crash harness T0–T6.

---

## 10. Prepared / Issued analysis

### Prepared ∧ ¬Issued

| Question | Canonical answer |
|---|---|
| Survives crash as live effect? | **No** — Discard (R-DUR-04, T1) |
| Replayed to host? | **Never** |
| Becomes Indeterminate? | **No** |
| May reach HostExecutor after recovery? | **No** |

### Issued ∧ ¬ receipt/Completed

| Question | Canonical answer |
|---|---|
| Classification | **Indeterminate** (T2–T4) |
| Escrow | **Survives** (R-DUR-05) |
| Host retry of original effect? | **Forbidden** re-execution (R-RECOV-08) |
| Path forward | R-RECOV-07/08 reconciliation; durable `EffectReconciled` |
| Local NotExecuted? | **Forbidden** without authoritative host recon evidence |

### Issued with Completed receipt

| Question | Canonical answer |
|---|---|
| Identity | id + effect digest + result digest (R-HOST-06; R-EFFECT-06) |
| Resume | T5 byte-exact from recorded result after sync-before-resume (R-RECOV-09) |
| Duplicate completion | causal protocol + digest checks; corruption ⇒ fault |

---

## 11. WAL analysis

| Topic | Authority | M7 duty |
|---|---|---|
| Separation | R-PERSIST-01 | recording only; **no second semantic machine**; payload = 15A CanonicalEncode |
| Framing | R-PERSIST-02 | WalFrame; monotonic WalSequence; gaps forbidden |
| Taxonomy | R-PERSIST-03 | Event / EffectPrepared / EffectIssued / EffectCompleted / EffectReconciled / SnapshotCommit (+ capability events R-PERSIST-07) |
| Payload shape | R-DUR-06 | effect_bytes + cost on Prepared/Issued |
| Continuity | R-PERSIST-06 | sₙ₊₁ = sₙ + 1; reject gaps/regressions |
| Integrity | R-PERSIST-08 | chained checksums; optional keyed MAC if adversarial medium |
| Frame field layout | **U-32 OPEN** | two source shapes (4-field vs 5-field + payload_length); checksum domain disputed |

**WAL AUTHORITY = PARTIAL** — obligations frozen; **byte layout provisional** under U-32 disclosure (must not silently close OAD).

**Existing code:** `MemoryJournal` is not a WAL. M7 must implement real framing in `ror-persistence`.

---

## 12. Snapshot analysis

| Topic | Authority | M7 duty |
|---|---|---|
| Content | R-PERSIST-04 | logical_time, ID counters, runnable queue, actor states, capability arena, budget, effect journal cursor — **complete machine state for resumption** |
| Authority lattice | R-PERSIST-07 | must be in snapshot (encoding still U-02) |
| Protocol | R-PERSIST-05 | Begin → payload → fsync → Commit+state_digest; incomplete = garbage |
| Validity | SNAPSHOT-COMMIT-INTEGRITY | ValidSnapshot iff commit+digest |
| Cadence | R-RECOV-09 | no SnapshotCommit inside issuance section s12–s14b |
| Encoding | **U-02 OPEN** | machine-state codecs not frozen |
| Runnable queue field | **U-17 OPEN** | persist field vs reconstruct-only |

**SNAPSHOT AUTHORITY = PARTIAL** — content/protocol frozen; **codecs provisional**.

---

## 13. Pending / Quiescence / recovery integration

| Rule | Source | M7 duty |
|---|---|---|
| Actor Pending while Issued wait | R-CORE-14; M6 | persist/reconstruct actor Pending with effect binding |
| Deadlock∧∃Pending ⇒ QR | R-BUDGET-16 | δ_t=0; Indeterminate; bind R-RECOV-08 |
| Pending survives Deadlock | M6 + R-BUDGET-16 | must survive crash as Indeterminate journal class when Issued |
| No invented cancel/timeout/Terminal | M6 review L-M6-TERM | still forbidden |
| QR itself is not crash recovery | R-BUDGET-16 | recovery uses R-RECOV-*; QR is live driver |

**PENDING RECOVERY = READY** at classification level (R-DUR-04/R-RECOV-*); actor-table encoding of Pending continuation remains **U-27/U-17** disclosed.

---

## 14. Actor / mailbox recovery disposition

Per R-PERSIST-04 + R-ACTOR-* + R-RECOV-03 step 10:

| Item | Disposition | Authority |
|---|---|---|
| ActorId counters | **PERSIST** (snapshot) | R-ACTOR-03; R-RECOV-09 style |
| Actor lifecycle status | **PERSIST** | R-PERSIST-04 actor states |
| Mailbox contents | **PERSIST** (encoding U-30/U-02) | R-PERSIST-04; isolation |
| Runnable queue | **PERSIST or RECONSTRUCT** | R-RECOV-03 §10; **U-17 OPEN** |
| Blocked/Pending/Terminal | **PERSIST** with status | R-ACTOR-04 eligibility after restore |
| Capability contexts | **PERSIST** + revalidate | R-PERSIST-07; R-KERN-05 |
| Logical time | **PERSIST** | R-PERSIST-04 |
| Scheduler “position” | **DERIVE** from runnable + statuses | no wall-clock |
| Global sequence counters | **PERSIST** / max-from-journal | R-RECOV-09 |
| In-flight non-durable send | **DISCARD** if not in durable log | DERIVED from durability boundaries |
| Messages to TERMINAL policy | **UNRESOLVED** beyond L-M6-TERM | do not invent |

**Do not assume** persistence of every Rust field; **do not assume** discard of required R-PERSIST-04 content.

---

## 15. Capability recovery

| Rule | Authority |
|---|---|
| CapRef ≠ AuthorityNode | R-KERN-01 (M4) |
| Authority lattice durable | R-PERSIST-07 |
| WAL capability events | Granted/Derived/Revoked |
| Reject dangling/generation mismatch | RecoveryFault — no silent repair |
| Post-recovery ∀c Valid(c, t_recovered) | R-PERSIST-07 |
| Revocation monotonic across crash | R-PERSIST-07; M023 |
| No amplification on restore | R-CAP-05 / R-ACTOR-09 spirit |

**CAPABILITY RECOVERY AUTHORITY = READY** (encoding of arena still U-02/U-31 disclosed).

---

## 16. Determinism requirements

| Must match across recovery runs | Source |
|---|---|
| ActorId / EffectId sequences after reconstruct | R-ACTOR-03; R-RECOV-09 |
| Logical time | R-PERSIST-04 |
| Mailbox FIFO order | R-ACTOR-06 |
| Runnable reconstruction deterministic | R-RECOV-03; R-ACTOR-04 |
| Budget partitions | R-RECOV-06 |
| Capability validity set | R-PERSIST-07 |
| Pending/Indeterminate set | R-DUR-04 |

**Prohibit:** wall-clock, random, HashMap-order semantics, env-dependent IDs, host observations without durable receipts.

**U-35 OPEN** — operational pillars required; theorem parameter falsifiability not closed (same as M6).

---

## 17. Reference-model requirements

| Requirement | Authority |
|---|---|
| Independent recovery implementation | R-RECOV-04 |
| No ProductionRecovery / ProductionPersistence as oracle | R-REF-02 |
| Differential: Canonical(Recover_P(D))=Canonical(Recover_R(D)) | final/04; R-REF-01 |
| Crate deps | reference → core only; recovery oracle edge is VERIFICATION not production |

**REFERENCE MODEL = READY** as a requirement; **code N/YI** (M7 impl must add independent recovery mirror — not call production recover).

---

## 18. Crash-matrix / test preflight (P01–P36)

| ID | Obligation | Method | Target | Evidence required | Authority status |
|---|---|---|---|---|---|
| P01 | WAL framing | unit/parse | ror-persistence | frames round-trip | PARTIAL (U-32) |
| P02 | checksum / chain | unit/neg | ror-persistence | M016 kill | SPECIFIED |
| P03–P04 | durable Prepared/Issued | unit + hinge | persist+runtime | EFFECT-ISSUE-* | SPECIFIED |
| P05–P12 | T0–T6 | crash harness | persist+runtime | RECOVERY-ISSUED-* | SPECIFIED |
| P13–P15 | replay / snapshot / combo | integration | persist | R-RECOV-01/03 | SPECIFIED |
| P16–P20 | malformed/partial/dup/gap/rollback | negative | persist | R-PERSIST-02/06; R-CORE-10 | SPECIFIED |
| P21–P24 | id/actor/mailbox/Pending preserve | crash | persist+runtime | R-PERSIST-04 | SPECIFIED/PARTIAL encode |
| P25 | Pending recon | recon tests | runtime+persist | R-RECOV-08 | SPECIFIED |
| P26–P27 | budget / logical time | invariant | both | R-RECOV-06 | SPECIFIED |
| P28 | cap non-amplify / no resurrect | M023 | kernel+persist | R-PERSIST-07 | SPECIFIED |
| P29–P30 | receipt validate / no dup host | mut M017/M028 | host path | R-HOST-06; hinge | SPECIFIED |
| P31 | recovery determinism | repeat recover | both | R-ACTOR-07 ops | PASS-DISCLOSED U-35 |
| P32–P33 | ref agree / crash diff | differential | reference | R-RECOV-04 | SPECIFIED req |
| P34–P35 | M5/M6 regression | workspace | all | prior green | baseline |
| P36 | hinge | mut host-before-Issued | runtime | GI-SEC-07 | SPECIFIED |

**This matrix is preflight planning — not executed evidence.** M7 code N/YI.

---

## 19. Mutation preflight (canonical targets)

| Mutation | Invariant | Expected | Security |
|---|---|---|---|
| duplicate host invocation | hinge + Issued identity | KILL | CRITICAL |
| skip Prepared/Issued durability | R-DUR-01/02 | KILL | CRITICAL |
| reorder/drop/dup WAL; corrupt checksum; seq rollback | R-PERSIST-02/06/08; R-CORE-10 | KILL | CRITICAL |
| reuse EffectId / ActorId | R-ACTOR-03; R-RECOV-09 | KILL | HIGH |
| lose/cancel Pending; advance time/budget on recover | R-DUR-04/05; R-BUDGET-16 | KILL | HIGH |
| restore revoked / amplify cap | R-PERSIST-07 | KILL | CRITICAL |
| forged/replayed receipt | R-HOST-06; R-EFFECT-06 | KILL | CRITICAL |
| restore TERMINAL as RUNNABLE; reorder mailbox | R-ACTOR-04/06 | KILL | HIGH |
| Indeterminate→NotExecuted local | R-RECOV-08; M028 | KILL | CRITICAL |

---

## 20. Dependency preflight

| Concern | Classification | Notes |
|---|---|---|
| Journal/WAL/snapshot/recovery home | `ror-persistence` (MOD-11/12) | **REQUIRED** existing crate |
| runtime → persistence | REQUIRED | already present (R-TRUST-05) |
| recovery → core | REQUIRED | types |
| reference recovery | VERIFICATION; core-only | no runtime/persistence import |
| New crate | **NOT REQUIRED** | extend ror-persistence + reference |
| runtime → host | FORBIDDEN | unchanged |
| reference → persistence | FORBIDDEN | keep |

**DEPENDENCIES = READY.** No FORBIDDEN/UNCLASSIFIED edge proposed. **G-18 PASS.**

---

## 21. OAD impact (none closed)

| OAD | M7 impact | Decision needed before impl? | Canonical answer? | Blocking? |
|---|---|---|---|---|
| **U-02** | machine/snapshot codecs | **Provisional encoding allowed**; must not claim freeze | No | **No** if disclosed thin codec (same pattern M5/M6) |
| **U-17** | runnable queue persist vs reconstruct | Choose reconstruct-from-statuses **or** persist field; document provisional | No | **No** if R-RECOV-03 §10 satisfied either way + disclosed |
| **U-32** | WalFrame fields/checksum domain | Prefer layout consistent with length-checked parser rules; disclose provisional | No | **No** if not claimed as OAD close |
| **U-30** | mailbox payload bytes vs Value | Follow R-MARSHAL-05 checked-bytes direction; disclose | No | No |
| **U-27** | Pending continuation locus | Thin: status + effect id binding; disclose | No | No |
| **U-06** | recon outcome per class | R-RECOV-08 closed security direction; per-class table residual | Partial | No for security floor |
| **U-08/14** | RecoveryFault labels | Provisional labels | No | No |
| **U-24/25** | envelope endian/tag | 15A existing path; disclose | No | No |
| **U-31** | authority arena fields | Kernel image durable; disclose | No | No |
| **U-34/35** | struct shapes / det theorem | Operational pillars | No | No |
| **U-03/09/21** | carry | No new answers | — | No |

**No OAD closed. No BLOCK-GOVERNANCE** under the established milestone pattern: provisional representations + explicit OPEN disclosure, without silent normative closure.

If implementation were to **pick U-32 and claim it frozen**, that would become BLOCK-GOVERNANCE mid-impl — preflight forbids that claim.

---

## 22. R-REG mapping

| Candidate cluster | Examples | Status |
|---|---|---|
| Durability | R-DUR-01…07 | SPECIFIED |
| Persist | R-PERSIST-01…08 | SPECIFIED |
| Recovery | R-RECOV-01…09 | SPECIFIED |
| Core restatements | R-CORE-06/09/10 | SPECIFIED |
| Host/effect | R-HOST-04/06; R-EFFECT-* | SPECIFIED |
| Budget recovery | R-BUDGET-09/11/13/16; R-RECOV-06 | SPECIFIED |

```text
R-REG = 184 × SPECIFIED
No promotions in this preflight
Implementation ≠ IMPLEMENTED evidence
```

---

## 23. Implementation boundary

### In (when authorized)

- WAL framing, append, sync, checksum chain, sequence  
- Snapshot begin/payload/commit  
- Full effect journal kinds + recovery classification T0–T6  
- 12-step recover; RecoveryFault paths  
- R-RECOV-08 binding hooks (thin admissible outcomes as specified)  
- Authority lattice durability  
- Independent reference recovery + crash differential  
- Crash harness / mutation intents  
- M5/M6 regression green  

### Out

- New cap/effect/actor/scheduler/delegation semantics  
- OAD closure; R-REG promotion  
- Alternate serialization ontology  
- Host bypass  
- Invented Pending cancel / message-to-dead / id reuse  

### Existing thin code to **extend**, not pretend complete

`crates/ror-persistence` `MemoryJournal` / `IssuanceJournal` — M5 hinge only.

---

## 24. Gate board

| Gate | Status | Notes |
|---|---|---|
| G-01 Repository identity | **PASS** | branch + HEAD ea11365 |
| G-02 Lineage | **PASS** | full chain verified |
| G-03 Canonical authority completeness | **PASS-DISCLOSED** | core frozen; U-02/U-32/U-17 encode gaps |
| G-04 M5 durability baseline | **PASS** | pipeline + MemoryJournal located |
| G-05 M5 security hinge | **PASS** | compatible with T0–T6 / R-RECOV-08 |
| G-06 Recovery state machine | **PASS** | R-DUR-04; R-RECOV-01…09 |
| G-07 Prepared/Issued semantics | **PASS** | Discard vs Indeterminate frozen |
| G-08 Crash-point authority | **PASS** | T0–T6 matrix |
| G-09 WAL authority | **PASS-DISCLOSED** | taxonomy frozen; U-32 layout |
| G-10 Snapshot authority | **PASS-DISCLOSED** | protocol/content frozen; U-02 encode |
| G-11 Pending/recovery | **PASS-DISCLOSED** | class frozen; U-27 locus |
| G-12 Actor/mailbox recovery | **PASS-DISCLOSED** | R-PERSIST-04; U-17/U-30 |
| G-13 Capability recovery | **PASS** | R-PERSIST-07 |
| G-14 Determinism | **PASS-DISCLOSED** | ops frozen; U-35 |
| G-15 Reference-model | **PASS** | R-RECOV-04 / R-REF-02 feasible |
| G-16 Crash-matrix | **PASS** | T0–T6 + evidence tags listed |
| G-17 Security threats | **PASS** | protections identified from authority |
| G-18 Dependency | **PASS** | ror-persistence home; no forbidden edge |
| G-19 OAD governance | **PASS** | none closed; provisional path disclosed |
| G-20 R-REG | **PASS** | 184 SPECIFIED |
| G-21 Scope containment | **PASS** | M7 boundary frozen |
| G-22 Test/evidence readiness | **PASS-DISCLOSED** | matrix defined; not executed |
| G-23 Mutation readiness | **PASS-DISCLOSED** | targets listed; not run |
| G-24 Workspace baseline | **PASS** | fmt/check/test/clippy green |

**BLOCKS = 0.**

---

## 25. Selected evidence records

### Evidence Record: G-05

- **Gate:** G-05 M5 security hinge  
- **Status:** PASS  
- **Canonical authority:** R-DUR-01; GI-SEC-07; R-RECOV-08  
- **Canonical rule:** Host only after DurableIssued; recon never re-executes freely  
- **Observed repository state:** `run_effect_pipeline` sole host path; T2–T4 → Indeterminate  
- **Relevant implementation:** `ror-runtime/src/effects.rs`; M5 review ea11365 hinge intact  
- **Evidence:** code inspection + M6 review  
- **Limitation:** NONE on hinge compatibility  
- **OAD/R-REG impact:** NONE  
- **Conclusion:** Recovery authority does not authorize host bypass.

### Evidence Record: G-08

- **Gate:** G-08 Crash-point authority  
- **Status:** PASS  
- **Canonical authority:** R-RECOV-02  
- **Canonical rule:** T0–T6 table  
- **Observed repository state:** matrix transcribed in final/01 §15  
- **Evidence:** final/01 R-RECOV-02  
- **Limitation:** harness N/YI  
- **Conclusion:** Crash points frozen for implementation planning.

### Evidence Record: G-09

- **Gate:** G-09 WAL authority  
- **Status:** PASS-DISCLOSED  
- **Canonical authority:** R-PERSIST-02/03/06/08; U-32 OPEN  
- **Canonical rule:** framed sequenced checksummed WAL; taxonomy fixed  
- **Observed repository state:** obligations SPECIFIED; frame field layout disputed in spec/09 U-32  
- **Limitation:** U-32 — provisional layout required at impl without OAD close  
- **Conclusion:** Implementable with disclosed provisional framing.

### Evidence Record: G-03

- **Gate:** G-03 Canonical authority completeness  
- **Status:** PASS-DISCLOSED  
- **Canonical authority:** final/01 §14–15; final/03; final/09  
- **Canonical rule:** M7 obligations exist at SPECIFIED; encode OADs open  
- **Limitation:** U-02/U-17/U-32/U-30/U-27 bound codecs/shapes  
- **Conclusion:** Sufficient to authorize impl under disclosed provisional encodings (M5/M6 precedent).

---

## 26. Disclosed limitations

| ID | Limitation |
|---|---|
| U-02 | Machine-state / snapshot byte codecs not frozen |
| U-17 | Runnable queue: snapshot field vs reconstruction |
| U-32 | WalFrame payload_length / checksum domain |
| U-30 | MarshalledValue mailbox wire form |
| U-27 | Pending continuation storage locus |
| U-06 residual | Per-class recon admissibility detail |
| U-08/14 | Fault label unification |
| U-24/25/31/34/35 | Envelope/tag/arena/struct/theorem carry |
| L-M7-THIN-NOW | MemoryJournal ≠ WAL; full engine N/YI |
| L-M7-PROV-CODEC | Impl may use provisional 15A-aligned encodings without claiming freeze |
| M5/M6 carry | prior disclosures remain |

---

## 27. Answers to preflight objective questions (compact)

1. **M7?** Persistence: WAL, snapshot, journal, checksum, sequence, recovery (R-ORDER-02).  
2. **Obligations?** R-PERSIST-01…08; R-DUR-01…07; R-RECOV-01…09; related CORE/HOST/BUDGET.  
3. **Immutable inputs?** M5 hinge+pipeline; M6 actors/Pending/QR; M4 caps.  
4. **State machine?** Prepared/Issued/Completed/Reconciled/Indeterminate + D=⟨S,L,H⟩.  
5. **Crash points?** T0–T6 (+ live R-DUR-07).  
6. **Survive?** Issued effects (Indeterminate), escrow, durable S/L/H, authority lattice, budget partitions.  
7. **Reconstruct?** GlobalState via snapshot+replay; runnable (U-17); next_effect_id.  
8. **Never replay?** Host effect re-execution; Prepared-only as live effect.  
9. **Never lose?** Issued identity+escrow until recon; committed snapshot+WAL integrity.  
10. **Pending?** Align with Issued→Indeterminate; no cancel invention.  
11. **Prepared¬Issued?** Discard.  
12. **Issued?** Indeterminate until Completed/Reconciled.  
13. **Missing receipt?** Indeterminate; R-RECOV-08 — not NotExecuted.  
14. **Actor/mailbox?** Required in snapshot content; codecs open.  
15. **Determinism?** Operational restore equality; U-35 open.  
16. **Reference?** Independent recover (R-RECOV-04).  
17. **Evidence?** T0–T6 harness, diff recover, mutations, M5/M6 regression.  
18. **Blocking gaps?** Encode OADs open but **not** blocking under provisional disclosure policy.

---

## 28. Final classification

### Authorization criteria

| Criterion | Met? |
|---|---|
| Mandatory authorities identified | yes |
| No hinge conflict | yes |
| Dependency placement authorized | yes |
| Reference independence feasible | yes |
| OAD answers not silently required as frozen | yes (provisional path) |
| Crash/recovery semantics sufficiently frozen | yes (T0–T6 + classification) |
| Scope implementation-ready | yes |
| Baseline workspace green | yes |
| No BLOCK-* | yes |

```text
M7 PREFLIGHT = GREEN WITH DISCLOSED LIMITATIONS — IMPLEMENTATION AUTHORIZED
```

```text
NEXT = M7 IMPLEMENTATION
```

### Explicit non-claims

```text
M7 is not implemented.
Recovery is not verified.
Crash safety is not verified.
Durability is not proven.
WAL correctness is not proven.
Snapshot correctness is not proven.
Host exactly-once behavior is not inferred.
R-REG remains 184 × SPECIFIED.
No OAD has been closed.
M5 HostInvoked ⇒ DurableIssued remains mandatory.
M6 actor semantics remain an upstream input.
No production semantic implementation was performed by this preflight.
Tests establish readiness baseline only — not recovery verification.
```

### Final state board

```text
M0–M4                      prior accepted
M5                         ACCEPTED WITH DISCLOSED EVIDENCE LIMITATIONS
M6                         ACCEPTED WITH DISCLOSED EVIDENCE LIMITATIONS
M7 preflight               GREEN WITH DISCLOSED LIMITATIONS — IMPLEMENTATION AUTHORIZED
M7 implementation          NOT STARTED
R-REG                      184 × SPECIFIED
NEXT                       M7 IMPLEMENTATION
```

---

*End of M7 PREFLIGHT. Do not begin M7 implementation in this operation.*
