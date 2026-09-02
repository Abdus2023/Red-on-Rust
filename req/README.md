# Red-on-Rust — Atomic Requirement Extraction

Extraction of every normative requirement in the frozen Red-on-Rust specification into atomic requirement units.
Source of record: `../Red-on-Rust.md` (42,312 lines, 60-turn design transcript). Canonicalization set: `../spec/00`…`../spec/10`.
**Result: 541 atomic requirement records, all `EVIDENCE-STATUS: SPECIFIED`, covering 148/148 canonical obligations.**

## Files

| File | Content | Required output section |
|---|---|---|
| `00-method.md` | Extraction rules, field semantics, evidence discipline, split/keep policy, provenance audit and corrections, validation log | — (method) |
| `01-registry-part1-foundations.md` | 79 records — SCOPE 12, CORE 16, TRUST 9, ARCH 6, PLANNER 22, COMPILE 14 | **1. Atomic requirement registry** |
| `01-registry-part2-semantics.md` | 77 records — CALC 20, CEK 22, CAP 26, KERN 9 | 1 |
| `01-registry-part3-resources-effects.md` | 72 records — BUDGET 32, EFFECT 40 | 1 |
| `01-registry-part4-durability-concurrency.md` | 73 records — DUR 14, HOST 14, ACTOR 35, MARSHAL 10 | 1 |
| `01-registry-part5-persistence.md` | 82 records — CANON 37, PERSIST 23, RECOV 22 | 1 |
| `01-registry-part6-verification.md` | 48 records — REF 17, TEST 31 | 1 |
| `01-registry-part7-engineering.md` | 66 records — REPO 19, ORDER 25, CLAIM 22 | 1 |
| `01-registry-part8-reference-15C.md` | 44 records — REF 19, TEST 25 (Phase 15C reference model + differential harness, turn `[48]`) | 1 |
| `02-compound-not-split.md` | 42 entries (CN-01…CN-42) covering 117 records kept whole, with the reason each cannot be split | **2. Compound requirements that could not safely be split** |
| `03-ambiguous.md` | 28 open ambiguities (AMB-01…AMB-29, AMB-15 withdrawn), plus 4 contradictions the source itself settles | **3. Ambiguous requirements** |
| `04-verification-undefined.md` | 8 records with an undefined verification method, 4 non-normative, 4 permissions, 96 review-only | **4. Requirements whose verification method is currently undefined** |
| `registry.json` | Machine-readable registry (generated) | 1 |
| `_anchors.py`, `_validate.py` | Provenance constants and the checker | — (tooling) |
| `_coverage.py` | Omission audit: normative-marker source lines that no record cites | — (tooling) |

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
python3 req/_coverage.py           # omission audit: 74/74 normative-marker lines cited
```

The checker re-derives its facts from `Red-on-Rust.md` and `spec/` rather than trusting the documents: field order, ID uniqueness and numbering, normative and evidence vocabularies, line-range bounds, agreement between every cited range and the turn it claims, existence and full coverage of the 148 parent obligations, resolution of every internal cross-reference, existence of every `C-nn`/`U-nn` reference in `spec/06`/`spec/09`, occurrence of every backticked identifier inside a cited range, and the frozen line anchors.

**Omission audit:** in the three requirement-dense regions (turn `[54]` master prompt, turn `[58]` bootstrap pack, closing turns `[59]`–`[60]`), all **74/74** normative-marker lines are cited by at least one record. Extended with `--all-turns` over the whole transcript, the frozen-content turns were triaged line by line: turn `[58]` is 23/23, turn `[46]` and turn `[21]` are complete apart from LaTeX continuation lines, code comments, and two commentary sentences; three requirements that pass had missed were found that way and are now REQ-KERN-009, REQ-PERSIST-023, REQ-RECOV-022 (plus the MAY permission REQ-REF-017).

**Cross-reference completeness:** all **45/45** contradictions in `spec/06` and all **16/16** unresolved decisions in `spec/09` are accounted for by a registry record or an ambiguity entry — none is silently dropped, and no reference points at an item that does not exist. `00-method.md` §6 lists each check with the injected fault that demonstrated it fires.
