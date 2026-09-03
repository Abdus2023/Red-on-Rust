# Repository-State Repair Verdict — Canonicalization Repair Pass v2

> **Date:** 2026-09-03
> **Branch:** `arena/01a06901-red-on-rust`
> **Commit:** `2c27789` (this change set; parent `0a8f60d`)

## 1. Executive summary

The governance-first canonicalization repair pass v2 is **complete and green**.
Stale derived state was repaired at its generators, the one authorized semantic
correction (R-CORE-02 vs R-CORE-11 predicate inconsistency) was applied with
its measured consequences adjudicated, and a new fail-closed cross-artifact
gate now derives the repository state from the authorities on every
`check.py` run. **No implementation, no Rust code, no M0 work, no status
promotion, no frozen-source change** (`Red-on-Rust.md` untouched); addenda
VII–IX, the 16-step effect sequence, historical audit snapshots and R-REG
identities are preserved.

## 2. Stage dispositions (V-01 … V-08)

| Stage | Repair | Authority basis | Disposition |
|---|---|---|---|
| V-01 | `spec/09` header `Status: all OPEN` → derived register-status declaration (registered **39** · open **28** · resolved **11** · max **U-45**; gaps are numbering gaps, never missing records) | spec/09's own rows | DISP-13 |
| V-02 | Checker-count narratives derived from the `check.py` registration (ast, no execution) in `final/_build.py` and `reg/_compile.py`; historical counts (13/14/15) retained only where labeled historical | check.py registration | DISP-14 |
| V-03 | Canonical indexed tag set = `spec/08` §1 tables: **25 = 16 frozen (incl. WAL-GAP-REJECT alias row) + 9 addendum**; `MARSHAL-CAPABILITY-REJECT ≙ MARSHAL-NO-RAW-CAPABILITY` is a documented non-indexed alias; set-equality gates in `spec/_build_index.py` | spec/08 §1 | DISP-15 |
| V-04 | FINAL1/R-REG current-state cardinalities re-derived (checker counts, tag counts, U gaps); `mod/` TAG_MODULE completed to the 25-tag set with per-row rationale + completeness gate in `mod/_build.py`; `spec/00` §2 contents claim and §3 mutation-ID row (M001…M042) repaired | registers | DISP-14/DISP-15 |
| V-05 | R-CORE-02 first conjunct → `ValidatedRequest(E)` over R-CORE-11's canonical signatures; subsumption `ValidatedRequest(E) ⇒ ValidatedPlan(plan(E))` preserved in both bodies; `ValidatedPlan` not removed; 16-step order untouched; addenda VII–IX and U-38 not reopened; term/ X-04 amended with historical lines intact; D2 row adjudicated in `spec/_check_allowlist.txt` (37 rows, amendment note in file) | authorized semantic correction (the only one) | DISP-05 |
| V-06 | `state/dispositions.json`: 15 disposition records + **12 sha256-pinned protected historical audit snapshots**; editing a protected audit is now a provenance violation | governance registry | — |
| V-07 | `state/_project.py --write` renders the single repository-state projection (`state/repository-state.json`, `state/01`, `state/02`) — all values **derived** from the authorities, none hard-coded | authorities → projection | — |
| V-08 | `state/_project.py` check mode: fail-closed cross-artifact battery (checks 0–8, see `state/00-overview.md` §3); registered as the **16th `check.py` checker**; independent `*/_*.py` glob classification | — | — |

## 3. Validation expectations vs derived values

Every pin below is **derived** at gate time and compared against the expected
block inside `state/_project.py`; nothing is hard-coded to make a gate pass.

| Quantity | Derived | Expected |
|---|---|---|
| Requirements (five-authority identity) | 184 = 148 frozen + 36 addenda | 184 |
| Atomic records (`req/registry.json`) | 545, all `SPECIFIED` | 545 |
| U registry | 39 registered = 28 open + 11 resolved; numeric max U-45; gaps U-10…12, U-18…20 | 39/28/11/45 |
| Canonical indexed tags | 25 (16 frozen + 9 addendum) + 1 documented alias | 25 |
| Mutation registry | 42 dense (M001…M042) | 42 |
| Checkers / classified non-checkers | 16 / 7 (registration-derived; grew 15 → 16 with the V-08 gate) | 16/7 |
| Implementation / ceiling | `BOOTSTRAP` / `SPECIFIED` | BOOTSTRAP/SPECIFIED |
| REF1, V1 | `CONDITIONAL` (both) | CONDITIONAL |
| Claims (implemented/tested/verified/proven) | 0/0/0/0 | 0/0/0/0 |

## 4. Execution status (§15 discipline)

**LOCALLY EXECUTED IN THE WORKSPACE (this session), results as follows — not
fabricated, not inferred from file structure:**

- `python3 check.py` → **ALL PASS — 16 checkers, 7 classified non-checkers**
  (final run after the last repair; includes `spec/_check.py --allowlist`
  with 37 adjudicated rows, 0 unlisted, 0 stale).
- `python3 audit/_checker_mutations.py` → **killed 33/33 (100 %)**, baseline
  green. New V-08 mutations K25–K32 were each killed **by
  `state/_project.py` specifically**: U-count inflation 39→45 (1c), U-status
  flip in a FINAL1 row (1e), checker de-registration 16→15 (2b/2c),
  unregistered executable (2b), tag-count lie 25→26 (3c), stale predicate
  reintroduced in the README box (6c), protected historical snapshot edit
  (7c), hand-edited projection (drift).
- `python3 state/_project.py` (bare check mode) → **STATE GATE PASS** with the
  full battery OK list (0b, 1, 1b–1e, 2, 2b, 2c, 3, 3b, 3c, 4, 4b, 4c, 5, 6,
  6b, 6c, 7, 7b–7d, 8, 8b).

**Owner-independent confirmation still required before M0** (per the v2
mandate): the owner must independently run, on their own checkout of commit
`2c27789`:

```
python3 check.py
python3 audit/_checker_mutations.py
python3 state/_project.py
```

and observe the three results above. A `check.py` PASS remains
repository-integrity evidence only — never semantic verification (V1
F-INFL-01) and never a status promotion.

## 5. Residual observations (no action taken, none blocking)

1. **Mutation-suite coverage of the gate set is partial by design**: the
   harness exercises 9 of the 16 registered checkers (it now includes the
   state gate; it still does not run `final/_build.py`, `reg/_compile.py`,
   `term/_reanchor.py`, `term/_dict.py`, `audit/_conservation_checker.py`,
   `audit/_crash_consistency_checker.py`,
   `audit/_reference_independence_checker.py` as killers). Those checkers'
   own drift modes are exercised indirectly through `check.py`.
2. **D2 similarity score of R-CORE-02** is 0.23 (was ≥ 0.25 before the V-05
   correction). The row is adjudicated in `spec/_check_allowlist.txt` with the
   amendment note; the divergence is the correction itself, not a
   transcription defect. Re-adjudication (row removal) is an owner decision.
3. **Preserved-stale records** (deliberate, recorded): U-05/C-19 register
   staleness vs the frozen `R-ARCH-05` addendum (DISP-06); C-110/C-111
   reserved; U-10…12/U-18…20 numbering gaps.
4. **Historical counts** (13/14/15 checkers; "26 tags"; M001–M035) survive
   only inside explicitly historical records (`state/02` DISP-08/DISP-14,
   frozen audit snapshots) — never as current-state claims.

## 6. Change inventory

31 tracked files modified + new `state/` document set
(`00-overview.md` authored; `dispositions.json` authored;
`repository-state.json`, `01-repository-state.md`, `02-dispositions.md`
generated; `_project.py` the gate). Generators repaired, generated prose
regenerated; frozen sources, addenda, historical audits and R-REG identities
untouched.

Follow-up (same pass): `README.md` document-set enumeration completed with the
`state/` paragraph (it described every organization except the one line 86
already cited); appended after the exact-position anchor block so no
line-anchored citation moved (`term/_reanchor.py`: nothing to move; full gate
re-run ALL PASS).

---

**Canonical repository state repaired and governance-consistent;
implementation remains the next phase.**
