# Red-on-Rust — Atomic Requirement Extraction

Extraction of every normative requirement in the frozen Red-on-Rust specification into atomic requirement units.
Source of record: `../Red-on-Rust.md` (42,312 lines, 60-turn design transcript). Canonicalization set: `../spec/00`…`../spec/10`.
**Result: 491 atomic requirement records, all `EVIDENCE-STATUS: SPECIFIED`, covering 148/148 canonical obligations.**

## Files

| File | Content | Required output section |
|---|---|---|
| `00-method.md` | Extraction rules, field semantics, evidence discipline, split/keep policy, provenance audit and corrections, validation log | — (method) |
| `01-registry-part1-foundations.md` | 79 records — SCOPE 12, CORE 16, TRUST 9, ARCH 6, PLANNER 22, COMPILE 14 | **1. Atomic requirement registry** |
| `01-registry-part2-semantics.md` | 74 records — CALC 20, CEK 22, CAP 24, KERN 8 | 1 |
| `01-registry-part3-resources-effects.md` | 72 records — BUDGET 32, EFFECT 40 | 1 |
| `01-registry-part4-durability-concurrency.md` | 73 records — DUR 14, HOST 14, ACTOR 35, MARSHAL 10 | 1 |
| `01-registry-part5-persistence.md` | 80 records — CANON 37, PERSIST 22, RECOV 21 | 1 |
| `01-registry-part6-verification.md` | 47 records — REF 16, TEST 31 | 1 |
| `01-registry-part7-engineering.md` | 66 records — REPO 19, ORDER 25, CLAIM 22 | 1 |
| `02-compound-not-split.md` | 42 entries (CN-01…CN-42) covering 117 records kept whole, with the reason each cannot be split | **2. Compound requirements that could not safely be split** |
| `03-ambiguous.md` | 26 open ambiguities (AMB-01…AMB-27, AMB-15 withdrawn), plus 4 contradictions the source itself settles | **3. Ambiguous requirements** |
| `04-verification-undefined.md` | 8 records with an undefined verification method, 4 non-normative, 3 permissions, 79 review-only | **4. Requirements whose verification method is currently undefined** |
| `registry.json` | Machine-readable registry (generated) | 1 |
| `_anchors.py`, `_validate.py` | Provenance constants and the checker | — (tooling) |

## Record shape

Every record has exactly these twelve fields, in this order:
`REQ-ID`, `CATEGORY`, `SOURCE`, `NORMATIVE-LEVEL`, `STATEMENT`, `PRECONDITIONS`, `POSTCONDITIONS`, `INVARIANTS`, `DEPENDENCIES`, `SECURITY-IMPACT`, `VERIFICATION-METHOD`, `EVIDENCE-STATUS`.

`NORMATIVE-LEVEL` vocabulary: `MUST` (334), `MUST NOT` (91), `IS` (43), `SHOULD` (4), `MAY` (7), `AMBIGUOUS` (8), `NON-NORMATIVE` (4).

## Evidence status

Every record is `SPECIFIED`. The repository contains no Cargo workspace, crate, Rust source, test, golden vector, mutation registry, or CI configuration, so no record may be promoted to `IMPLEMENTED`, `TESTED`, `VERIFIED`, or `PROVEN` — specification text is not implementation evidence. Promotion requires a repository artifact cited in the record.

## Checking it

```
python3 req/_validate.py           # 0 errors / 0 warnings on a clean tree
python3 req/_validate.py --write   # regenerate req/registry.json
```

The checker re-derives its facts from `Red-on-Rust.md` rather than trusting the documents: field order, ID uniqueness and numbering, normative and evidence vocabularies, line-range bounds, agreement between every cited range and the turn it claims, existence and full coverage of the 148 parent obligations, resolution of every cross-reference, occurrence of every backticked identifier inside a cited range, and the frozen line anchors. `00-method.md` §6 lists each check with the injected fault that demonstrated it fires.
