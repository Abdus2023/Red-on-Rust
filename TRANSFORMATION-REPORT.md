# Red-on-Rust — Repository Transformation Report

**Controlled specification-source-processing pipeline · version 1.0.0 · mode: repository transformation, specification-processing infrastructure only.**

This report is generated: every figure below is computed from the artifacts it names. `python3 scripts/spec/pipeline.py --report` reproduces it, and `scripts/spec/_gate.py` (registered in `check.py`) fails the repository gate if the committed copy and a fresh render disagree.

## 1. Source and pipeline identity

| field | value |
|---|---|
| source hash | `sha256:2aeb9940665f6ef27bbba9895889e93b8be8c1ba9f5ff0558f2b95fee07a25eb` |
| source hash matches the pinned frozen identity | yes |
| source lines / bytes | 42312 / 1166812 |
| source turns | 60 (`[1]`–`[60]`) |
| pipeline | `redonrust-spec-pipeline` v`1.0.0` |
| render hash (content address of the whole artifact set) | `sha256:06a56825de98e4fc53651c54a685c57517c4f9dc57444aba5564bd24fa72bf82` |
| input artifacts (authority files read) | Red-on-Rust.md · spec/01 · spec/02 · spec/03 · spec/05 · spec/06 · spec/08 · spec/09 · req/registry.json · req/03 · reg/requirements.json · term/10-index.json · mod/19-index.json · dep/10-graph.json · spec/10-index.json · state/dispositions.json · state/repository-state.json · final/03 · audit/*.md · README.md |
| output artifacts (derived) | 65 in `build/spec/` + 7 committed pointers under `spec/0*-*/` + `spec/PIPELINE.md` + this report |


## 2. Counts

| measure | value |
|---|---|
| requirements | 184 (canonical registry `spec/03`) |
| obligations (canonical) | 184 |
| obligations (atomic layer) | 545 atomic records (`req/`), 533 cited by a single parent |
| sections | 24 (S-01…S-24, `spec/02`) |
| terminology entries | 86 canonical terms · 33 non-conflation laws · 87 collisions |
| dependency edges | 34 section · 0 requirement · kinds 7 |
| audit findings | 152 projected (113 C- rows + 39 U- rows) · categories 16 |
| evidence vectors | 34 across canonical:2, effects:25, persistence:7 |
| normalization records of record | 148 (Original+Normalized pairs in `spec/normative-normalization-records.md`) |
| proposals accepted into canonicalization | 0 |


## 3. Status of each acceptance condition (§22)

| condition | status | evidence |
|---|---|---|
| source snapshot exists | yes | `build/spec/source.sha256` + `snapshot.json` + `source-snapshot.md`; committed pointer `spec/00-source/README.md` |
| source hash is reproducible | yes | no timestamp in any artifact; `sha256sum Red-on-Rust.md` reproduces `sha256:2aeb9940665f6ef2…` |
| semantic sections exist | yes | 24 section files + `sections/index.json` (lossless, `spec/02` order) |
| requirements registry exists | yes | `build/spec/requirements.json` (184 entries) |
| obligations registry exists | yes | `build/spec/obligations.json` (184 + atomic layer) |
| terminology registry exists | yes | `build/spec/terminology.json` (86 terms) |
| dependency registry exists | yes | `build/spec/dependencies.json` |
| audit artifacts exist | yes | `build/spec/audit/` (16 category projections, incl. the five families named in §6) + `audit.json` |
| canonical specification exists | yes — as a projection | `build/spec/Red-on-Rust.canonical.md`; the human-readable authority stays `spec/01` (a second canonical copy would be duplicate authority, §20) |
| provenance survives every stage | yes | 64/65 artifacts carry a provenance block (JSON: a `provenance` field; markdown: a footer naming stage, generator, seed hash and inputs). The one exempt artifact is `source.sha256`: the seed digest itself, bare hex by contract so `sha256sum Red-on-Rust.md` diff against it is byte-exact |
| pipeline is deterministic | yes | render hash `sha256:06a56825de98e4fc…` reproduced by `_gate.py` on every `check.py` run; no clock/random/locale/network/filesystem-order use (S7 scans the stage sources) |
| pipeline is idempotent | yes | re-running writes nothing (`publish` compares bytes); canonical chunk multiset equals `spec/01`'s |
| canonicalization introduces no unauthorized requirements | yes | introduced 0, dropped 0, promotions 0 |
| registry identities are preserved | yes | `sha256:7ae2e7706b8e…` — identical set and order across spec/01, spec/03, spec/10, reg, final/03 |
| cross-artifact verification passes | yes | 40 checks, 0 failures |
| mutation tests detect deliberate drift | see §5 | drift battery in `tests/spec/_pipeline_mutations.py` |
| historical artifacts remain protected | yes | 12 sha256-pinned audit snapshots re-verified by S7 (113 findings projected without regrading) |
| evidence state remains unchanged | yes | ceiling `SPECIFIED`; statuses ['SPECIFIED']; `REF1-CONDITIONAL`/`V1-CONDITIONAL` carried verbatim |
| M0 remains NOT STARTED | yes | `state/repository-state.json` → `NOT STARTED` (no workspace exists (spec/08 §4)) |

## 4. Remaining ambiguities and contradictions

| family | open | ids |
|---|---|---|
| contradictions/ambiguities (`spec/06`) | 46 | C-03, C-04, C-05, C-08, C-101, C-102, C-14, C-15, C-16, C-19, C-24, C-26, C-30, C-38, C-45, C-46, C-47, C-48, C-49, C-50, C-51, C-54, C-55, C-56… |
| unresolved decisions (`spec/09`) | 28 | U-02, U-03, U-04, U-05, U-06, U-08, U-09, U-13, U-14, U-15, U-16, U-17, U-21, U-22, U-23, U-24, U-25, U-26, U-27, U-28, U-29, U-30, U-31, U-32… |
| BLOCKING-severity open rows carried into canonicalization | 33 | C-46, C-47, C-48, C-57, C-98, U-02, U-03, U-04, U-05, U-06, U-08, U-09, U-13, U-14, U-15, U-16, U-17, U-21, U-22, U-23, U-24, U-25, U-26, U-27, U-28, U-29, U-30, U-31, U-32, U-33, U-34, U-35, U-37 |
| MAJOR-severity open rows carried | 34 | C-03, C-04, C-05, C-08, C-101, C-14, C-15, C-19, C-24, C-45, C-49, C-50, C-51, C-54, C-55, C-56, C-58, C-59, C-60, C-61… |

`req/03-ambiguous.md` registers 39 ambiguity entries. Canonicalization carries every open row and discloses it in the canonical artifact's open-items section; none was silently resolved, and none was re-graded. Suggested new register ids (computed, **not** filed): 10 candidate finding(s) from this run's integrity scans.

## 5. Mutation status

| measure | value |
|---|---|
| battery | `tests/spec/_pipeline_mutations.py` (drift of each §14 failure shape, applied to a scratch copy; the working tree is never touched) |
| mutations defined | 16 |
| shapes covered | §10 normalization preserves meaning, §11 no silent acceptance, §12 no status upgrade, §14 counts diverge, §14 duplicate authority, §14 entry lacks source provenance, §14 generated files are stale, §14 historical artifact presented as current, §14 source provenance is missing/changed, §4.1 provenance / §5 authority order, §4.2 determinism, §4.4 no normative invention, §4.5 / §14 duplicate authority, §4.5 identity preservation, §9 ordering/provenance |
| registered in `check.py` | `scripts/spec/_gate.py` and `tests/spec/_pipeline_mutations.py` are both registered, so every repository gate run executes them |
| survivor policy | a surviving mutation is a hard failure of the battery, which fails `python3 check.py`; the gate never reports a partial kill table as success |


No kill rate is recorded in this report, deliberately: a measured number frozen in a derived artifact goes stale the moment the tree moves, and this repository has already been bitten by exactly that defect class (`state/02` DISP-14, a hand-frozen checker count). What the report states instead is the *invariant* — 16 deliberate drifts are defined, the battery runs inside `check.py`, and any survivor reddens the repository gate. For the table of this run: `python3 tests/spec/_pipeline_mutations.py -v`.

## 6. Provenance status

| measure | value |
|---|---|
| provenance fields on every generated artifact | `pipeline`, `pipeline_version`, `stage`, `generator`, `source{path,sha256}`, `inputs[]`, `authority_note`, `timestamp_present:false` |
| per-row provenance | 149 source-cited + 35 frozen-addendum (whose provenance is the governance action) |
| timestamps in semantic content | 0 (§4.1: they would destroy reproducibility) |
| content addressing | every artifact digest recorded in `build/spec/manifest.json`; set digest = `render_hash` |
| historical protection | 12 sha256-pinned audit snapshots re-hashed on every verify |
| source mutation | 0 bytes (`Red-on-Rust.md` opened read-only by S0; the pipeline writes only under `build/spec/`, `spec/0*-*/`, `spec/PIPELINE.md` and this report) |


## 7. Registry and verification status

| measure | value |
|---|---|
| registry status | 4 registries generated; identities identical to the canonical registry; 0 identity changes; 0 status changes; 0 rows without provenance |
| status transition channel | `reg/status-transitions.json` (append-only, ledger of record) — untouched by this transformation |
| verification status | ACCEPTED as a set of derived projections: 40 checks, 0 failures, 4 gaps reported (not closed) |
| verification verdict text | every projection agrees with its authority; the pipeline verified agreement, never machine conformance |
| what a PASS does not establish | that any R-… obligation is implemented, tested, verified or proven; that the determinism or security theorems hold for a machine (there is no machine); that REF1/V1 are anything other than CONDITIONAL |


## 8. Evidence level

Ceiling `SPECIFIED` — the ladder `SPECIFIED → IMPLEMENTED → TESTED → VERIFIED → PROVEN` (`spec/00` §2) is unchanged, and this transformation cannot move it: it produced scripts, schemas, registries, validators and audit tooling, no implementation and no conformance evidence.  `REF1-CONDITIONAL` and `V1-CONDITIONAL` remain conditional.  A green `check.py` (now including `scripts/spec/_gate.py`) is repository-integrity evidence only, never semantic verification.

## 9. M0 status and boundary compliance

M0: **NOT STARTED** — source: no workspace exists (spec/08 §4).

| forbidden during transformation (§21) | present? |
|---|---|
| Rust runtime implementation | no |
| CEK implementation | no |
| capability kernel implementation | no |
| actor implementation | no |
| scheduler implementation | no |
| host implementation | no |
| persistence implementation | no |
| effect implementation | no |
| agent runtime implementation | no |

No `.rs` file, `Cargo.toml`, crate, test, golden-vector implementation or CI configuration was added. The only new code is specification-processing infrastructure: `scripts/spec/*.py`, `tests/spec/_pipeline_mutations.py`, the committed pointers under `spec/0*-*/`, `spec/PIPELINE.md`, this report, `check.py` registration and `.gitignore`.

## 10. What this transformation changed about authority

Nothing.  Authority remains: frozen source `Red-on-Rust.md` → authoritative registers (`spec/01…spec/10`, `req/`, `reg/`, `mod/`, `dep/`, `term/`, `state/dispositions.json`) → explicit governance dispositions → deterministic generators → derived artifacts → proposals → human-readable projections (§5).  The pipeline sits at the generator/derived levels and its outputs say so on their first lines.

```
PROPOSAL IS NOT AUTHORITY.
REPRESENTATION IS NOT AUTHORITY.
DERIVATION IS NOT AUTHORITY.
ONLY VALIDATED, PROVENANCE-BEARING, CANONICAL ARTIFACTS MAY BECOME AUTHORITY.
```

STOP CONDITION (§24): the transformation stops before M0.  No implementation claim is made; the next authorized step is unchanged and remains the repository's decision, not this pipeline's.
