# M8 Implementation Progress — Differential System

**Operation type:** M8 IMPLEMENTATION ONLY  
**Authority:** M8 PREFLIGHT @ `docs/bootstrap/M8-PREFLIGHT.md` — GREEN WITH DISCLOSED LIMITATIONS — IMPLEMENTATION AUTHORIZED  
**Base:** `184538c` (M8 preflight) · M7 review `2b56518` · M7 impl `5a04630`

```text
M8 IMPLEMENTATION = COMPLETE WITH DISCLOSED EVIDENCE LIMITATIONS
NEXT = M8 IMPLEMENTATION REVIEW
```

---

## 1. Classification rationale

Mandatory M8 surfaces from final/04 / R-ORDER-02 are present:

| Surface | Status |
|---|---|
| Generated programs | DONE — seeded LCG generator (`system::generate`) |
| Reference execution | DONE — `run_reference` → `ror-reference` CEK |
| Production execution | DONE — `run_production` → `ror-runtime` CEK |
| Normalized comparison | DONE — provisional `NormalizedObservation` + `compare` |
| First-divergence reporting | DONE — `DiffPath` / `FirstDivergence` |
| Shrinking | DONE — deterministic candidates; predicate preserve |
| Coverage evidence | DONE — `CoverageEvidence` counters + tags |
| R-TEST-02 16-field artifact | DONE — `CounterexampleArtifact` |
| M2–M7 differential regression | GREEN (workspace lib tests) |

Disclosures (non-blocking under preflight policy): F-04 Observed\* still UNKNOWN (provisional schema); pure-CEK generation domain (M4–M7 remain pairwise modules); thin empty trace fields on pure-CEK artifacts; no M9/M10.

---

## 2. Implementation commit / homes

| Item | Value |
|---|---|
| Primary crate | `crates/ror-differential/src/system.rs` |
| Crate root | `crates/ror-differential/src/lib.rs` exports M8 API |
| Reference | unchanged independence (`ror-core` only) |
| Production | used as black-box SUT via existing m2 observe |

---

## 3. Canonical authority implemented (projection)

| Requirement | Surface |
|---|---|
| R-REF-01 Observe_P = Observe_R | `run_case` / `execute_seeded` / exhaustive seeds |
| R-REF-02 independence | reference Cargo + imports; runners split |
| R-REF-05 first divergence; not final-value-only | kind path before value path |
| R-REF-06 hinge | no host in system runners; M5 tests still green |
| R-TEST-02 16 fields | `CounterexampleArtifact::canonical_field_names` |
| R-TEST-03 shrink order (expr domain) | depth/arity/bindings via structural shrink |
| R-TEST-07 tags | evidence tags on coverage; not oracle |

---

## 4. Pipeline

```text
GenConfig(seed) → generate → DiffProgram
        → run_production / run_reference
        → normalize → compare
        → Equal | Diverged{first}
        → shrink(pred) → CounterexampleArtifact
        → CoverageEvidence
```

---

## 5. Tests executed (this operation)

| Suite | Result |
|---|---|
| `cargo fmt --all -- --check` | exit 0 |
| `cargo check --workspace` | exit 0 |
| `cargo test --workspace --lib` | exit 0 |
| `cargo clippy --workspace --all-targets -- -D warnings` | exit 0 |
| `system::` unit tests | **15 passed** |
| differential crate total | **90 passed** (75 prior + 15 M8) |
| M2–M7 modules | still green inside 90 |
| runtime effects (M5 hinge) | 96 runtime tests green |

**Evidence counts (exhaustive_small_state seed 1..=32):** generated=32, production=32, reference=32, divergent=0, equal=32 on pure-CEK domain.

---

## 6. Security assertions

| Assertion | Result |
|---|---|
| Untrusted seed ↛ Authority ↛ ExternalEffect | PASS — generator is test mechanism only |
| Production ≠ Reference implementation | PASS — separate crates/runners |
| HostInvoked ⇒ DurableIssued | PASS — M5 regression; no M8 host path |
| Recovery ↛ re-exec | PASS — M7 untouched |
| Differential ↛ Host bypass | PASS — pure CEK runners only |
| Generator ↛ Authority | PASS |
| Reference ↛ Production authority | PASS — no forbidden deps |

---

## 7. Determinism

| Check | Result |
|---|---|
| same seed → same program | PASS |
| same program → same observations | PASS |
| same observations → same compare | PASS |
| shrink deterministic | PASS |

---

## 8. OAD / R-REG / milestones

```text
F-04 Observed*     UNKNOWN — provisional NormalizedObservation; NOT closed
U-02 / U-17 / U-32 OPEN — carry; not closed
U-35               OPEN — operational det. only
R-REG              184 × SPECIFIED — NOT promoted
M9                 NOT STARTED
M10                NOT STARTED
M11                NOT STARTED
```

---

## 9. Known limitations

| ID | Limitation |
|---|---|
| L-M8-PURE-GEN | Generator targets M2/M3 pure CEK; M4–M7 use existing pairwise modules |
| L-M8-F04 | Observation schema provisional |
| L-M8-ARTIFACT-THIN | Trace/image fields empty on pure-CEK cases |
| L-M8-SHRINK-MAP | R-TEST-03 actor/WAL/crash priorities no-op on pure expr |
| L-M8-NO-PROOF | Agreement is evidence, not formal proof |
| L-M8-TESTKIT | ror-testkit still thin; doubles remain in-crate |

---

## 10. Explicit non-claims

```text
Observe equality is not formally proven.
F-04 is not resolved.
OADs are not closed.
R-REG is not promoted.
M9 mutation kill-rate is not implemented.
M10 crash gate is not implemented.
Generator does not authorize capabilities or invoke host.
Differential crate is not a second runtime.
```

---

## 11. Final board

```text
M7                         ACCEPTED WITH DISCLOSED EVIDENCE LIMITATIONS
M8 preflight               GREEN WITH DISCLOSED LIMITATIONS — IMPLEMENTATION AUTHORIZED
M8 implementation          COMPLETE WITH DISCLOSED EVIDENCE LIMITATIONS
R-REG                      184 × SPECIFIED
NEXT                       M8 IMPLEMENTATION REVIEW
```

---

*End of M8 IMPLEMENTATION progress. Do not begin M8 review in this operation.*
