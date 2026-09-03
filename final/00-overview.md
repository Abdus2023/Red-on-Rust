# Red-on-Rust — FINAL1 Canonical Specification Set

The FINAL1 specification-compiler output: the cleaned Red-on-Rust authorities compiled into one canonical specification in the mandated 29-section order, with consolidated global invariants, canonical registries, and carried-not-resolved open decisions.

| File | Output # | Content |
|---|---|---|
| `01-canonical-specification.md` | 1 | The canonical specification: §01–§29; all 184 `R-…` rows transcribed verbatim from `spec/01`; GI-indexed global invariants (§23–25) |
| `02-section-index.md` | 2 | Canonical section index; S-nn alias map; supersession carriers; type definition homes; ID namespaces |
| `03-requirement-registry.md` | 3 | Canonical requirement registry (184 stable IDs, status, provenance, homes; atomic-layer coverage note) |
| `04-verification-registry.md` | 4 | Canonical verification registry (spec/08 verbatim + FINAL1 binding statements) |
| `05-global-invariant-registry.md` | 5 | Global invariant registry (GI-SEC/DET/REC), math-symbol canonical table, FA records, single-home discipline |
| `06-terminology-glossary.md` | 6 | Terminology glossary (nine distinctions + production↔reference pairs, spec/05 verbatim, N-01…N-33, T-index) |
| `07-dependency-integrity-report.md` | 7 | Integrity report — computed every build (FINAL VALIDATION battery) |
| `08-evidence-status-matrix.md` | 8 | Evidence-status matrix (SPECIFIED-universe; REF1/V1-CONDITIONAL; UNKNOWN rows; no-upgrade ledger) |
| `09-open-architectural-decisions.md` | 9 | Open architectural decisions (U/C/V/F/F-INFL/AMB carry-forward; staleness records; FA index) |
| `10-canonicalization-report.md` | 10 | Canonicalization report (merged/normalized/resolved/preserved/superseded/changed/not-upgraded + validation checklist) |

**Regenerating:** `python3 final/_build.py --write`; `python3 check.py` runs this generator in check mode plus the whole repository battery (18 structural gates, 7 classified non-checkers — inventory derived from the check.py registration; historical counts 13/14/15 are retained as history only). **Semantics:** none of these files is an implementation, a test, a verification, or a proof; they are specification and registry artifacts (`final/08` says so per class). **Governance:** where `final/` and `spec/` differ, `spec/` and the frozen source govern — and the byte-identity gate makes that divergence impossible while the checks pass.

**Status of the compiled architecture (inherited, unchanged):** Red-on-Rust — architecture and specification FROZEN; repository BOOTSTRAP; every obligation SPECIFIED; `REF1-CONDITIONAL` and `V1-CONDITIONAL` preserved; `IMPLEMENTATION READY` in the exact, limited sense of `final/01` §01 — not `IMPLEMENTED`, `TESTED`, `VERIFIED`, `PROVEN`, or `PRODUCTION READY`.
