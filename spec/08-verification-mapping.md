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

**Post-audit addendum tags** (not part of the frozen source set; added by remediations SEC-001 and SEC-004):

| Tag | Obligation(s) covered | Required evidence | Repo evidence |
|---|---|---|---|
| `EFFECT-RECEIPT-RESULT-NO-AUTHORITY` | R-EFFECT-08 (post-audit addendum) | Receipt-result admission: result payload is data-domain only, capability/closure-free at any nesting depth, verified before resumption (mutations M019, M020) | NONE |
| `RECOVERY-REVOCATION-DURABLE` | R-PERSIST-07 (post-audit addendum) | Revocation survives crash: crash matrix T0–T6 with revocation committed before the crash point; revoked caps stay revoked; dangling/generation-mismatched CapRefs ⇒ `RecoveryFault` (mutation M023) | NONE |

## 2. Mutation registry → obligation map (M001–M035, R-TEST-04)

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

**Evidence status:** registry is `SPECIFIED` (frozen content). No mutant is registered, injected, or killed in this repository; `MutationKillRate` is **not measured** (nothing to measure). 100% is a target, not a current claim (R-CLAIM-01).

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
