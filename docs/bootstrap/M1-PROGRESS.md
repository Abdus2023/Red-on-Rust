# M1 Progress — Canonical Serialization (Partial)

> **Superseded for governance wording by** `docs/bootstrap/M1-REVIEW.md`.
> This file remains as the original progress note; classification and evidence
> ceiling language below are corrected to match the R-REG evidence model.

## Identity

| Field | Value |
|---|---|
| Branch | `arena/01a06993-red-on-rust` |
| Implementation commit | `1b27bec` (plus review follow-up commit) |
| Predecessor | M0 GREEN (`docs/bootstrap/M0-B-VALIDATION.md`) |
| M1 classification (M0-A) | `PARTIALLY IMPLEMENTABLE` |
| **Canonical requirement statuses** | **all remain `SPECIFIED`** |
| **Evidence ceiling (R-REG ladder)** | **`SPECIFIED`** |
| Canonical registries modified | **NO** |

## Governance correction

The earlier draft of this note said:

```text
M1 (partial frozen subset): IMPLEMENTED + TESTED in-tree
EVIDENCE CEILING: SPECIFIED
```

Under `reg/03-status-transition-audit-model.md` those phrases name **ladder
rungs** that require an authorized `reg/status-transitions.json` entry with
matching evidence *kinds*. No such entry exists; all 184 `R-*` rows remain
`SPECIFIED` (`reg/06`, `final/08`).

**Corrected wording (compatible with EVIDENCE CEILING: SPECIFIED):**

```text
M1 frozen subset: code present in-tree; local cargo gates PASS
Canonical R-CANON-* registry status: SPECIFIED (unchanged)
Candidate transitions (NOT applied): see M1-REVIEW.md
```

In-tree source and tests are **repository artifacts**, not automatic
`IMPLEMENTED`/`TESTED` promotions.

## Scope executed

Frozen Phase-15A data-domain codec in `ror-core` (see M1-REVIEW for authority map).

## Cargo gates (see M1-REVIEW for fresh execution)

Recorded at implementation time; re-executed during M1 review.

## Deliberately not implemented

U-02, U-09, U-21 machine/effect encodings; R-MARSHAL full surface; registry promotion.

## Decision (see M1-REVIEW for authoritative classification)

```text
M0: GREEN
M1 frozen subset: see M1-REVIEW.md
M1 full milestone: NOT COMPLETE
M2: see M1-REVIEW.md
EVIDENCE CEILING: SPECIFIED
```
