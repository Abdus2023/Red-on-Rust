# M11 CORRECTIVE / GOVERNANCE DISPOSITION

**Operation ID:** `M11-CORRECTIVE-001`  
**Operation type:** Corrective / governance disposition after rejected M11 review  
**Immutable rejected review:** `96b6d0b`  
**Immutable implementation base:** `ebc777e` (pre-corrective HEAD chain)  
**Governing rule:** Resolve canonical acceptance semantics first; only then align the executable oracle. Do not redefine “pass” for convenience.

```text
M11 CORRECTIVE / GOVERNANCE DISPOSITION = YELLOW — GOVERNANCE CONDITION REMAINS UNSATISFIED

RF-01 = RESOLVED-VIOLATED
RF-02 = CORRECTED
Canonical RC defect predicate = FAIL
RC oracle fail-closed = PASS (verified by regression)
Fresh M11 review required = YES
Production readiness = NOT CLAIMED
```

---

## 1. Corrective operation identity

| Item | Value |
|---|---|
| Prompt | M11-CORRECTIVE-001 |
| Prior review | `docs/bootstrap/M11-REVIEW.md` @ `96b6d0b` — **REJECTED** |
| Objective | Faithful R-ORDER-02 defect predicate in RC gate; preserve rejected review integrity |
| Non-objective | Force M11 RC PASS; close OADs; promote R-REG; re-grade defects |

---

## 2. Immutable review base

| Artifact | SHA / path | Status |
|---|---|---|
| M11 review REJECTED | `96b6d0b` | **IMMUTABLE** — not amended |
| Review report | `docs/bootstrap/M11-REVIEW.md` | preserved |
| Implementation boundary | `ebc777e` / impl `3de9c93` | preserved as historical base |
| RF-01 / RF-02 as recorded | M11-REVIEW §28 | not erased |

---

## 3. Implementation base

| Item | Value |
|---|---|
| Pre-corrective HEAD | `96b6d0b` (review tip) |
| M11 impl | `3de9c93` (`m11.rs`, `m11_rc_gate.py` v1) |
| Corrective changes | see §17 |

---

## 4. Authority sources inspected

| Source | Use |
|---|---|
| `final/01-canonical-specification.md` R-ORDER-02 | M11: *full test suite, stress, security review, **zero open high defects pass*** |
| `final/01` R-TEST-10 / R-TEST-11 | RC stage + three conjuncts (unchanged) |
| `final/04-verification-registry.md` | M11 multi-regime green board |
| `final/09-open-architectural-decisions.md` | C-row severity × open state register |
| `final/08-evidence-status-matrix.md` | REF1-CONDITIONAL; BLOCKING-if-inflation guards |
| `final/10-canonicalization-report.md` | 4 BLOCKING X- collisions; open C-rows |
| `reg/requirements.json` | 184 × SPECIFIED |
| `docs/bootstrap/M11-REVIEW.md` | RF-01/RF-02 evidence (immutable) |
| `scripts/m11_rc_gate.py` (v1) | RF-02 root cause |

**No authority conflict** requiring STOP-01: R-ORDER-02 text is unique; final/09 supplies the open high-severity C-row population.

---

## 5. RF-01 analysis

### 5.1 What «zero open high defects» means

| Dimension | Authoritative finding |
|---|---|
| **Phrase home** | R-ORDER-02 M11 acceptance cell (final/01) |
| **«Defect» population for this gate** | Open **C-** contradiction/ambiguity rows in final/09 §B (severity register). Not OADs-as-such; not F-INFL guards; not disclosed evidence limitations (F-04, L-01/L-02) unless they appear as open high C-rows. |
| **Severity taxonomy in final/09** | `BLOCKING`, `MAJOR`, `MINOR`, `MINOR→MAJOR` (no separate enum token `HIGH` on C-rows). Product SEC audit used CRITICAL/HIGH historically; those SEC findings were **remediated by addenda** (C-77…97 resolved-by-addendum). |
| **«High» mapping** | Canonical text does **not** define a separate “high” enum. **BLOCKING** is release-blocking by name (cf. R-TEST-05 survivors as release-blocking). **MAJOR** is the next grade. Two readings documented: **narrow** = BLOCKING(/CRITICAL/HIGH); **conservative** = narrow + MAJOR. |
| **«Open»** | Register state contains `open` / `**open**` (including “resolved-by-later-text (incompleteness **open**)”). Not RESOLVED-only rows. |
| **Applicability** | All open C-rows in final/09 §B are in-scope for the register check. OADs (U-*) OPEN are **not** automatically C-row defects; U-35 is linked via **C-98 BLOCKING open**. |
| **SEC CRITICAL/HIGH** | Remediated; not counted as open product CRITICAL rows in final/09 C-table. |

### 5.2 Live register snapshot (fresh)

| Metric | Value |
|---|---|
| C-rows parsed | **41** |
| Open BLOCKING | **C-46, C-48, C-57, C-98** |
| Open MAJOR (incl. MINOR→MAJOR) | **31** ids (see predicate output) |
| Narrow high non-empty? | **YES** (4 BLOCKING) |
| Conservative high non-empty? | **YES** |

### 5.3 RF-01 decision

```text
RF-01-A — CONDITION VIOLATED
```

Even under the **narrowest** defensible reading (BLOCKING only), **four open BLOCKING** rows remain. Therefore:

```text
Canonical RC defect predicate = FAIL
M11 RC = NOT EARNED
```

No defect was downgraded, closed, renamed, or deleted. No R-ORDER-02 text was weakened.

**Note on C-46/C-48:** final/09 states normative-layer choices were resolved by addenda but **register rows were not re-graded** and remain open BLOCKING — carried verbatim. Corrective operation **must not** silently re-grade them.

---

## 6. Defect applicability matrix (high-severity open)

| defect_id | severity | state | RC_relevant | reason | source | disposition | required_action |
|---|---|---|---|---|---|---|---|
| C-46 | BLOCKING | open | **YES** | open BLOCKING | final/09 | leave open | governance re-grade or close with authority |
| C-48 | BLOCKING | open | **YES** | open BLOCKING | final/09 | leave open | governance |
| C-57 | BLOCKING | open | **YES** | open BLOCKING | final/09 | leave open | governance |
| C-98 | BLOCKING | open → U-35 | **YES** | open BLOCKING | final/09 | leave open | U-35 resolution or explicit RC exemption authority |
| C-03…C-101 MAJOR open set | MAJOR | open | **YES under conservative; NARROW-optional** | R-ORDER-02 «high» ambiguous vs MAJOR | final/09 | leave open | governance severity glossary |
| F-04 | OAD/UNKNOWN | OPEN | **NO as C-row** | evidence limitation / OAD | final/09 U/F | disclosed | do not auto-count as C-defect |
| U-35 | OAD OPEN | OPEN | via C-98 | theorem params | final/09 | disclosed | linked BLOCKING C-98 |
| M10 L-01/L-02 | disclosure | — | **NO** | evidence limitation | M10/M11 reviews | preserve | — |
| F-INFL-* | guards | — | **NO as open defect** | inflation guards, not current defects | final/09 V1 | preserve | — |
| SEC CRITICAL historical | remediated | resolved-by-addendum | **NO** | addenda closed product SEC | final/09 security | preserve | — |

Full open MAJOR id list is emitted by `python3 scripts/m11_rc_defect_predicate.py` (fresh).

---

## 7. RF-01 final disposition

```text
RF-01 = RESOLVED-VIOLATED
```

Governing executable reading for the RC gate: **`all` = narrow ∪ conservative** (fails on open BLOCKING **or** open MAJOR).  
**Narrow alone already FAILS** due to C-46/C-48/C-57/C-98 — so RF-01 does not depend on the MAJOR ambiguity.

---

## 8. RF-02 root cause

`scripts/m11_rc_gate.py` **v1** (`3de9c93`):

- Ran workspace + m11 + m10 + m5 + m9 successfully.
- Set `overall_pass=true` when those stages passed.
- **Did not** evaluate R-ORDER-02 defect condition against final/09.
- Could therefore report PASS while open BLOCKING/MAJOR remained (M11-REVIEW RF-02).

---

## 9. Oracle correction

| Change | Path |
|---|---|
| New predicate module | `scripts/m11_rc_defect_predicate.py` |
| Gate v2 integrates predicate | `scripts/m11_rc_gate.py` (`schema: m11-rc-gate-v2`) |
| RF-02 regression tests | `scripts/test_m11_rc_defect_predicate.py` |

Predicate properties:

- Parses final/09 C-rows (authority input).
- Fail-closed on missing/unreadable/empty parse/unknown open severity.
- Does **not** read prior gate PASS flags.
- Does **not** modify the register.

Gate v2: `overall_pass` requires prior stages **and** `defect_predicate` ok.

---

## 10. Fail-closed rule

| Condition | Result |
|---|---|
| Missing register file | FAIL (`fail_closed=true`) |
| Unreadable register | FAIL |
| Zero C-rows parsed | FAIL |
| Unknown severity + open | treated as high → FAIL |
| Open BLOCKING | FAIL |
| Open MAJOR (reading all/conservative) | FAIL |
| Clean synthetic register | PASS (regression only) |

---

## 11. Regression tests

Command:

```bash
python3 scripts/test_m11_rc_defect_predicate.py
```

| Test | Result |
|---|---|
| live register open BLOCKING → FAIL | **PASS** |
| clean synthetic → PASS | **PASS** |
| open BLOCKING fixture → FAIL | **PASS** |
| open MAJOR → fail conservative/all | **PASS** |
| missing register fail-closed | **PASS** |
| empty malformed fail-closed | **PASS** |
| unknown severity open → high FAIL | **PASS** |
| parse C-98 live | **PASS** |
| **Summary** | **8/8 passed** |

---

## 12. Command-to-obligation matrix

| Obligation | Authority | Command | Expected | Actual | Evidence |
|---|---|---|---|---|---|
| Workspace integrity | process | `git status` / `git diff --check` | clean of unrelated | clean (m9-matrix restored) | FACT |
| fmt | workspace | `cargo fmt --all -- --check` | 0 | **0** | TESTED |
| check | workspace | `cargo check --workspace` | 0 | **0** | TESTED |
| test | workspace | `cargo test --workspace --lib -- --test-threads=1` | 0 | **0** | TESTED |
| clippy | workspace | `cargo clippy … -D warnings` | 0 | **0** | TESTED |
| Defect predicate | R-ORDER-02 | `python3 scripts/m11_rc_defect_predicate.py` | FAIL (live) | **exit 1, ok=false** | TESTED |
| RF-02 regression | corrective | `python3 scripts/test_m11_rc_defect_predicate.py` | 8/8 | **8/8** | TESTED |
| RC gate v2 | R-ORDER-02+ | `python3 scripts/m11_rc_gate.py` | overall_pass **false** | **false**; defect stage fail; other stages pass | TESTED |
| M9 campaign (inside gate) | R-TEST-11 c2 | via gate | 42/42 | pass stage | TESTED |

Toolchain: `ror-stable` 1.88.0.

---

## 13. Evidence freshness

| Artifact | Freshness |
|---|---|
| `/tmp/m11-rc-report.json` schema v2 | fresh after corrective gate run |
| Defect predicate live output | fresh |
| RF-02 unit regressions | fresh |
| Workspace cargo gates | fresh |
| v1 gate PASS claims | **STALE** for corrected oracle (see §15) |

---

## 14. Artifact provenance

```text
canonical: final/01 R-ORDER-02 + final/09 C-rows
    ↓
scripts/m11_rc_defect_predicate.py (implementation)
    ↓
scripts/m11_rc_gate.py v2 (consumer)
    ↓
python3 scripts/m11_rc_gate.py
    ↓
/tmp/m11-rc-report.json (derived; not authority)
    ↓
conclusion: overall_pass=false because defect predicate FAIL
```

---

## 15. Evidence invalidation

| Item | Action |
|---|---|
| Old oracle | v1 in `3de9c93` / pre-corrective `m11_rc_gate.py` |
| Old claim | `overall_pass=true` while open BLOCKING remained |
| Invalidation | **v1 RC PASS claims are stale** for v2 oracle semantics |
| Preservation | Review `96b6d0b` remains valid historical evidence of v1 failure mode |
| Required | Any future “RC PASS” claim must use **v2** gate + fresh run + governance clearing RF-01 |

---

## 16. Preserved limitations

Unchanged disclosures (not converted to pass):

- F-04 OPEN  
- U-35 / C-98 OPEN (C-98 still BLOCKING open — counted)  
- M10 L-01 / L-02  
- Stress 50k vs 50k–100k band  
- Pure-CEK property scope  
- Seed-board exhaustive limitation  
- M9 42/42 TESTED  
- R-REG 184 × SPECIFIED  
- OADs OPEN  
- Evidence TESTED ≠ VERIFIED/PROVEN  

---

## 17. Changed files

| Path | Role |
|---|---|
| `scripts/m11_rc_defect_predicate.py` | **NEW** — R-ORDER-02 defect predicate |
| `scripts/m11_rc_gate.py` | **UPDATED** — v2 fail-closed defect stage |
| `scripts/test_m11_rc_defect_predicate.py` | **NEW** — RF-02 regressions |
| `docs/bootstrap/M11-CORRECTIVE.md` | **NEW** — this report |

**Not changed:** `final/*`, `reg/*`, `mutations/registry.toml`, production crates, `docs/bootstrap/M11-REVIEW.md`, OADs.

---

## 18. Commit identities

| Role | SHA | Subject |
|---|---|---|
| Immutable rejected review | `96b6d0b` | M11 REVIEW — REJECTED |
| Corrective (this operation) | `4c1f633` | RF-01 violated; RF-02 defect predicate fail-closed (YELLOW) |

Further amend commits after push, if any, extend this table without rewriting `96b6d0b`.

---

## 19. Remaining blockers / follow-up

| Item | Status |
|---|---|
| Open BLOCKING C-46/C-48/C-57/C-98 | **remain** — require governance disposition |
| Open MAJOR set | **remain** |
| M11 RC PASS | **NOT EARNED** |
| Fresh M11 review | **REQUIRED** after this corrective lands |
| Spec text change to R-ORDER-02 | **NOT done** (would be separate governance) |
| Register re-grade of C-46/C-48 | **NOT done** (final/09 notes normative-layer fix without register update) |

---

## 20. Explicit non-claims

```text
This is NOT M11 accepted.
This is NOT a fresh M11 review result.
This is NOT production ready.
This is NOT R-REG promotion.
This is NOT OAD closure.
This is NOT VERIFIED/PROVEN.
v1 RC PASS is STALE under v2 oracle.
96b6d0b remains REJECTED historical review evidence.
```

### Terminal classification

```text
M11 CORRECTIVE / GOVERNANCE DISPOSITION = YELLOW
  — GOVERNANCE CONDITION REMAINS UNSATISFIED

RF-01 = RESOLVED-VIOLATED
RF-02 = CORRECTED
Canonical RC defect predicate = FAIL
RC oracle fail-closed = PASS
RF-02 regression = PASS
Workspace fmt/check/test/clippy = PASS
Evidence = TESTED
Historical review 96b6d0b = IMMUTABLE
Fresh M11 review required = YES
Production readiness = NOT CLAIMED

NEXT = FRESH M11 REVIEW REQUIRED
  (and/or GOVERNANCE follow-up on open BLOCKING/MAJOR rows)
```

---

*End of M11-CORRECTIVE-001. Do not auto-start fresh M11 review. Do not force RC PASS.*
