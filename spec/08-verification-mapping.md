# 08 — Verification / Evidence Mapping

Maps obligations to (a) the source's own **verification-obligation tags**, (b) the **conformance test obligations** defined in the frozen source, and (c) the **evidence status in this repository**.

**Evidence status rule (binding):** a tag is *satisfied* in this repository only if a passing test artifact and (where required) differential/mutation/crash evidence exist here. **None do.** Every entry below is therefore `SPECIFIED` (the test is *required by the frozen spec*) — none is `TESTED`/`VERIFIED`.

## 1. Source verification-obligation tags (frozen set)

The master prompt §21 COVERAGE (L38544–38577) freezes this tag list; milestones (L40763–41273) reference it. These are the stable coverage identifiers (R-TEST-07).

| Tag | Obligation(s) covered | Required evidence (frozen) | Repo evidence |
|---|---|---|---|
| `CEK-CALL-ARITY-PRECHECK` | R-CEK-05 | Arity mismatch after function eval, before any arg eval; 0 arg evals, 0 host calls, 0 budget mutations on mismatch (mutation M002) | NONE |
| `CEK-CALL-ARGS-LTR` | R-CEK-05 | Strict left-to-right argument evaluation, observable in trace (mutation M001) | NONE |
| `CEK-CLOSURE-LEXICAL-CAPTURE` | R-CEK-03, R-CEK-04 | Free vars resolve in closure env, never caller env; shadowing case | NONE |
| `CAP-DERIVE-NO-AMPLIFICATION` | R-CAP-05, R-CORE-04 | `derive(parent, C).leq(parent)` over generated authorities (mutation M006) | NONE |
| `CAP-REVOCATION-ANCESTOR` | R-CAP-07 | Revoked ancestor ⇒ descendant invalid; lazy walk (mutation M004) | NONE |
| `BUDGET-CONSUMPTION-CONSERVATION` | R-BUDGET-05, R-CORE-05 | `C_available + C_escrowed + C_consumed = C_initial` after every step (mutation M007) | NONE |
| `BUDGET-ESCROW-CONSERVATION` | R-EFFECT-05, R-DUR-05 | complete_max escrow at issuance; escrow survives crash; no release after indeterminate (mutation M008) | NONE |
| `EFFECT-ISSUE-DURABLE-BEFORE-HOST` | R-DUR-01, R-CORE-06 | No `HostExecutor::execute` before durable `Issued`; crash harness T0–T4 | NONE |
| `EFFECT-RECEIPT-DIGEST-VALIDATION` | R-EFFECT-06 | ID+digest causal validation; tampered digest ⇒ ReplayCorruption, no resume (mutations M017, M018) | NONE |
| `SCHED-FIFO` | R-ACTOR-04 | FIFO selection; deterministic wakeup (mutation M012) | NONE |
| `SCHED-BLOCKED-NOT-SCHEDULED` | R-ACTOR-04 | Pending/Blocked/Halted/Faulted never selected (mutation M011) | NONE |
| `MARSHAL-NO-RAW-CAPABILITY` | R-MARSHAL-01, R-CORE-07 | Recursive rejection incl. nested caps (source README tag: `MARSHAL-CAPABILITY-REJECT`) | NONE |
| `WAL-SEQUENCE-CONTINUITY` | R-PERSIST-06 | `s_{n+1} = s_n + 1`; gaps/regressions rejected (mutation M015) | NONE |
| `RECOVERY-ISSUED-INDETERMINATE` | R-DUR-04, R-RECOV-02 | T2/T3/T4 ⇒ Indeterminate; never NotExecuted | NONE |
| `SNAPSHOT-COMMIT-INTEGRITY` | R-PERSIST-05 | ValidSnapshot iff commit+digest; partial snapshot ignored (crash T6) | NONE |
| `WAL-GAP-REJECT` | R-PERSIST-06 | (alias in blueprint L37364 and Bootstrap Pack L40643; same evidence as WAL-SEQUENCE-CONTINUITY) | NONE |

**Tag normalization note:** the README (L41969–42010) lists a slightly different example set (e.g., `CEK-CALL-ARITY-PRECHECK`, `BUDGET-ESCROW-CONSERVATION`, `MARSHAL-CAPABILITY-REJECT`); the master-prompt list above is the frozen canonical set; `MARSHAL-CAPABILITY-REJECT` ≙ `MARSHAL-NO-RAW-CAPABILITY` (C-10, terminology 05 §5).

**Post-audit addendum tags** (not part of the frozen source set; added by remediations SEC-001/SEC-004 and addenda VII/VIII/IX):

| Tag | Obligation(s) covered | Required evidence | Repo evidence |
|---|---|---|---|
| `EFFECT-RECEIPT-RESULT-NO-AUTHORITY` | R-EFFECT-08 (post-audit addendum) | Receipt-result admission: result payload is data-domain only, capability/closure-free at any nesting depth, verified before resumption (mutations M019, M020) | NONE |
| `RECOVERY-REVOCATION-DURABLE` | R-PERSIST-07 (post-audit addendum) | Revocation survives crash: crash matrix T0–T6 with revocation committed before the crash point; revoked caps stay revoked; dangling/generation-mismatched CapRefs ⇒ `RecoveryFault` (mutation M023) | NONE |
| `BUDGET-ESCROW-DISPOSITION-TOTALITY` | R-BUDGET-09, R-BUDGET-11 (addendum VIII), R-EFFECT-05 | Every escrowed amount terminates: R-BUDGET-09's three-path totality with the five-leaf normal form as fine structure; `Remains-Indeterminate` bounded by the logical-time bound (mutation M039) | NONE |
| `PERSISTENT-CAPACITY-ACCOUNTING` | R-BUDGET-13 (addendum VIII), R-PERSIST-04 | Volatile RAM distinct from persistent storage; durable capacity accounted per WAL frame/snapshot artifact; overflow faults | NONE |
| `TIME-DELTA-ENUMERATED` | R-BUDGET-16 (addendum IX), R-BUDGET-06 | every time-capable transition kind carries its frozen δ_t; per host round trip = 2; the scheduler turn is the executed transition's δ_t (mutation M040) | NONE |
| `DURATION-NO-DOUBLE-CHARGE` | R-BUDGET-15 (addendum IX), R-BUDGET-01 | exactly one duration debit per logical-time advance; `cost_C(E)`'s duration component is declared/diagnostic only, never a machine debit (mutation M042) | NONE |
| `QUIESCENCE-RECONCILES-PENDING` | R-BUDGET-16 (addendum IX), R-BUDGET-09, R-RECOV-08 | stable quiescence with any `Pending` effect deterministically records `Indeterminate` per effect and binds to R-RECOV-08; Blocked-only quiescence does not (mutation M041) | NONE |
| `REQUEST-ARGS-LTR` | R-TEST-12 (addendum VII), R-EFFECT-01 | Request arguments evaluated strictly left-to-right, exactly one per CEK step (step 3 of the frozen sequence); Track A request-suite coverage | NONE |
| `REQUEST-NON-CAP-SHORT-CIRCUIT` | R-TEST-12 (addendum VII), R-EFFECT-04 | A non-capability capability expression faults before any target/parameter evaluation and before steps 4–16; no `EffectId`, budget or log mutation; `HostExecutor` never invoked | NONE |

## 2. Mutation registry → obligation map (M001–M042, R-TEST-04)

| Mutant | Injected defect | Obligation it must kill evidence for |
|---|---|---|
| M001 | reverse argument evaluation | R-CEK-05 (LTR) |
| M002 | skip arity precheck | R-CEK-05 |
| M003 | allow non-function application | R-CEK-05 |
| M004 | accept revoked capability | R-CAP-07, R-CORE-03 |
| M005 | omit capability ceiling | R-CAP-06 (cost ≤ R_A conjunct) |
| M006 | permit capability amplification | R-CAP-05, R-CORE-04 |
| M007 | omit budget gate | R-BUDGET-04, R-BUDGET-08 |
| M008 | release indeterminate escrow | R-DUR-05 |
| M009 | permit negative resources | R-BUDGET-02 |
| M010 | allocate EffectId before authorization | R-EFFECT-03/04 (gate ordering) |
| M011 | schedule blocked actor | R-ACTOR-04 |
| M012 | duplicate runnable queue entry | R-ACTOR-04 (at-most-once) |
| M013 | break mailbox FIFO | R-ACTOR-06 |
| M014 | accept duplicate canonical map key | R-CANON-06 |
| M015 | ignore WAL sequence gap | R-PERSIST-06 |
| M016 | ignore checksum mismatch | R-PERSIST-02 |
| M017 | accept mismatched EffectDigest | R-EFFECT-06, R-DUR-03 |
| M018 | resume after corrupted receipt | R-EFFECT-06 |
| M019 | resume with `Value::Capability` result | R-EFFECT-08 |
| M020 | resume with closure result | R-EFFECT-08 |
| M021 | authorize without possession check | R-KERN-04 |
| M022 | unmarshal accepts capability payload | R-CANON-12 |
| M023 | recovery resurrects revoked capability | R-PERSIST-07 |
| M024 | receive-side registration without kernel revalidation | R-MARSHAL-05 |
| M025 | spawn clones parent context unattenuated | R-ACTOR-09 |
| M032 | contains_capability skips `FunctionValue.env` | R-MARSHAL-06 |
| M034 | release failure silently ignored (`unwrap` → `let _`) | R-CORE-12 |
| M030 | inadmissible constraint treated as ⊤ | R-CAP-10 |
| M033 | enqueue without recipient capacity check | R-ACTOR-10 |
| M035 | stranded escrow silently reclaimed to `available` without reconciliation | R-BUDGET-09 |
| M026 | accept future-tagged proposal | R-PLANNER-06 |
| M027 | observation includes CapRef | R-PLANNER-07 |
| M028 | reconciliation resolves Indeterminate as NotExecuted / releases escrow without admissible outcome | R-RECOV-08 |
| M029 | replay skips result-digest verification | R-HOST-06 |
| M031 | component uses the superseded LE grammar | R-CANON-13 |
| M036 | rotate one `spec/01` obligation body onto adjacent content (IDs left in place) | R-SCOPE-03, R-CLAIM-02 — the SEC-023 normative-layer class; detector `spec/_check.py` |
| M037 | in-memory s12–s13 mutations committed before the journal-driven append+fsync (host-visible pre-durability) | R-DUR-07 |
| M038 | issuance records carry `{id, actor, digest}` only (loss of the escrow/effect source of truth) | R-DUR-06 |
| M039 | `Remains-Indeterminate` treated as a terminal disposition (stranded escrow survives the logical-time bound) | R-BUDGET-11 |
| M040 | δ_t table violation: a time-capable transition kind advances logical time without its frozen δ_t (e.g., a scheduler turn charged +1 on top of the executed transition, or a kind omitted from the enumeration) | R-BUDGET-16 |
| M041 | post-deadline `EffectReceipt` routed through the normal deadline gate (rejected) instead of R-RECOV-08 settlement | R-BUDGET-16, R-RECOV-08 |
| M042 | `cost_C(E)`'s duration component debits `D` in addition to the transition's `ΔD := δ_t` (double charge) | R-BUDGET-15 |

**Evidence status:** registry is `SPECIFIED` (frozen content). No *machine* mutant is registered, injected, or killed in this repository; `MutationKillRate` for the machine-mutant registry is **not measured** (nothing to measure). 100% is a target, not a current claim (R-CLAIM-01). M037/M038 (addendum VII), M039 (addendum VIII) and M040–M042 (addendum IX) are registered the same way — machine mutants, unmeasurable in BOOTSTRAP; their document-mutant shapes are exercised by `audit/_checker_mutations.py` K19/K20/K21/K22-K24. M036 is the one measurable document mutant: it survives the historical default wiring and is **KILLED under the adopted repository gate** (U-38 option (b)) — see below.

**M036 is the one measurable document mutant.** Every other row above targets
machine behaviour and cannot be measured here (no implementation). M036 targets
*this document set*, and its detector — `spec/_check.py`, promoted from
`audit/spec_check.py` as the SEC-023 remediation — exists and runs green. It was
therefore measured directly under the default wiring (harness:
`audit/_checker_mutations.py` M036 group; method recorded in
`audit/semantic-nondeterminism-audit.md` §9):

| Rotations injected | Hard-failed (default config, historical) | Warn-only | Undetected |
|---|---|---|---|
| 12 adjacent-pair body swaps spread across all 173 obligations | **0** | 12 | 0 |

The rotation is detected — it raises a `D3` warning — but under the default
wiring **`spec/_check.py` exits 0**, because only `D1` (records-layer `Original`
vs `Normalized` rule identity) hard-fails; `D2`/`D3`, which are the checks that
compare the `spec/01` *body* against the source and the matrix, warn by default
and hard-fail only under `--strict`. The tree carries **36 pre-existing
adjudicated warnings** (18×D2, 18×D3), so a rotation moves the count to 37 —
camouflage, not a signal. A reviewer running the documented default command sees
`OK with warnings` and the same summary line as a clean tree.

This was the SEC-023 defect class reappearing one layer up: SEC-023 found 48
obligations whose stable ID denoted a different rule than their body, and the
remediation built a detector for it — but wired the *body-comparison* half of
that detector to a non-failing severity. `MutationKillRate` for the one
measurable mutant under the **default wiring** was **0%**; that measurement is
retained above as history and is **not** the repository gate.

**Adopted repository gate (U-38 option (b), 2026-09-03): M036 is KILLED.** The
gate (`check.py`) now invokes `spec/_check.py --allowlist` instead of the
default warn-only invocation. `spec/_check_allowlist.txt` holds the 36
adjudicated warnings (18×D2, 18×D3); any warning not in the list — including the
extra `D3` a body rotation raises — is a hard failure, and stale or malformed
allow-list rows are failures as well. Re-measured under the gate: the M036
rotation exits **1 (killed)**, with both rotated obligation IDs named. This is
a document-mutant measurement only — it says nothing about the machine-mutant
kill rate, which remains unmeasured (100% is a target, not a current claim;
R-CLAIM-01). `spec/_check.py`'s default mode is unchanged, so outside the
repository gate (e.g., invoking the checker directly without `--allowlist`)
behaviour is exactly as before. Mutation `K18` locks the claim on every run:
it re-runs the M036 rotation against `spec/_check.py --allowlist` and fails if
the SEC-023 class is ever unguarded again.

## 3. Conformance test obligations → obligation map (frozen suite)

| Conformance obligation (frozen) | Obligation(s) | Evidence in repo |
|---|---|---|
| 14-gate short-circuit matrix (per gate: subsequent gates untouched, ID not incremented, budget unchanged, log unchanged, host never called) | R-EFFECT-03, R-EFFECT-04 | NONE |
| Causal replay integrity (tampered digest/ID ⇒ ReplayCorruption, no continuation resume, no budget release) | R-EFFECT-06 | NONE |
| Marshalling authority isolation (embedded CapRef in List ⇒ MarshalFault; recipient context unchanged) | R-MARSHAL-01 | NONE — **blocked (X-65, C-55):** `MarshalFault` has two disjoint declarations (L10846 turn [18] vs L25983 turn [32], zero shared variants), so the fault value this test must assert is not yet determined|
| Global determinism / live-vs-replay final-state digest equality | R-CORE-08, R-ACTOR-07, R-HOST-04 | NONE |
| 15C differential: `Observe(Production(X)) = Observe(Reference(X))` | R-REF-01 | NONE |
| 15C differential recovery: `Canonical(Recover_P(D)) = Canonical(Recover_R(D))` | R-REF-01, R-RECOV-01/03 | NONE |
| Budget partition conservation over randomized Spawn/Request/Complete sequences | R-BUDGET-05 | NONE |
| Crash matrix T0–T6 execution for randomized effect types | R-RECOV-02, R-TEST-08 | NONE |
| LLM outer-loop: untrusted input rejection / stale proposal rejection / end-to-end replay | R-PLANNER-02…05 | NONE |
| Golden vectors byte-exactness | R-CANON-11 | NONE |
| Round-trip `decode(encode(x)) = x` + injectivity evidence over generated distribution | R-CANON-10 | NONE |
| Deep-call stress (50k–100k), 100+ actors, large WAL, repeated crash/recovery | R-TEST-01 (stress) | NONE |
| Starvation test (strict interleaving, 100 actors) | R-ACTOR-04 | NONE |
| Teleportation test (budget sum invariant over actor tree) | R-ACTOR-08 | NONE |
| Amplification test (forced CapRef through Send ⇒ fault, context unchanged) | R-MARSHAL-01, R-ACTOR-08 | NONE |
| First security gate (Block ⇏ ExecutablePlan; 7-form differential incl. faults) | R-ORDER-03 | NONE |

## 4. Milestone → verification evidence gate (R-ORDER-02)

| Gate | Required evidence to declare milestone complete |
|---|---|
| M1 | golden vectors pass; round-trip pass; malformed reject; duplicate keys reject; bytes deterministic |
| M2 | differential equivalence (production vs reference) for Value/Var/Let/Seq/If |
| M3 | tags CEK-CALL-ARITY-PRECHECK, CEK-CALL-ARGS-LTR, CEK-CLOSURE-LEXICAL-CAPTURE + deep-call stress |
| M4 | CAP-DERIVE-NO-AMPLIFICATION + revocation/expiration/lexical binding + independent reference algebra |
| M5 | authorization, budget gates, deadline, host policy, EffectId/Digest, durable issuance, receipt validation |
| M6 | FIFO scheduler, FIFO mailbox, spawn isolation, send/receive, delegation, blocked/wakeup |
| M7 | WAL, snapshot, effect journal, checksum, sequence continuity, recovery |
| M8 | generated programs, reference execution, production execution, normalized comparison, first-divergence reporting, shrinking |
| M9 | MutationKillRate = 100% (registered non-equivalent) |
| M10 | T0–T6 exact classifications |
| M11 | exhaustive + property + mutation + differential + crash + stress + determinism + serialization + security all green |

**Current state:** no milestone acceptance evidence exists in this repository. M0 itself (workspace passing `cargo check/test/fmt/clippy`) is not satisfied because no workspace exists.

## 5. Claim ladder per theorem/invariant (claim discipline, C-43)

| Statement | Status | Evidence |
|---|---|---|
| Theorem 1–3 capability algebra (attenuation soundness, monotonicity, corollary) | SPECIFIED (proof sketches in source) | no mechanized proof in repo |
| Theorem capability preservation (machine) | SPECIFIED | none |
| Theorem budget monotonicity/conservation | SPECIFIED | none |
| Theorem isolation (actors) | SPECIFIED | none |
| Theorem replay correspondence | SPECIFIED | none |
| Theorem host-boundary authorization (central negative property) | SPECIFIED | none |
| Theorem temporal integrity | SPECIFIED | none |
| Deterministic concurrency theorem | SPECIFIED | none |
| No-amplification / no-teleportation theorems | SPECIFIED | none |
| Crash-recovery theorem (qualified) | SPECIFIED | none |
| External-effect chain (7 conjuncts) | SPECIFIED | none |
| Canonical injectivity | SPECIFIED (structural property; evidence claim scoped) | none |
| `Recover(D) = PreCrashState` (at defined boundaries) | SPECIFIED | none |

**No statement in the specification is `PROVEN`, `VERIFIED`, `TESTED`, or `IMPLEMENTED` in this repository.** Any downstream document that claims otherwise must cite a repository artifact; none currently exists.

## 6. Verification-dependency reminders (frozen)

1. Differential oracle is the primary evidence; coverage metrics, kill rate, and fuzz volume are **secondary evidence of test strength**, never substitutes (R-TEST-07, R-REF-01).
2. The mutation framework validates itself before being trusted (R-TEST-06).
3. Divergences are adjudicated 4-way before any oracle modification (R-TEST-09); specification ambiguity reopens the frozen spec explicitly (R-SCOPE-03).
4. The reference model is independently authored and reviewed (anti-oracle-collapse) (R-REF-02, R-RECOV-04).
