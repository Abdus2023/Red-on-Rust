# M1 Review — Frozen Serialization Audit & Evidence Reconciliation

## Identity

| Field | Value |
|---|---|
| Branch | `arena/01a06993-red-on-rust` |
| Bootstrap (M0-B) | `727a6efbfd10b943eed2c67552294cdafe68ffb8` |
| M0-B validation | `c951627` |
| M1 implementation | `1b27becd78a5c9a99f8a7ab91bfdbbb054b11e16` |
| Review HEAD (this commit) | recorded by commit containing this file |
| Review date | 2026-09-04 |
| Operation | audit / reconciliation — **not** M2 |

```text
git rev-parse HEAD at review execution: see §Execution evidence
```

---

## 1. Evidence-ceiling check

### Claim under audit

`docs/bootstrap/M1-PROGRESS.md` (pre-correction) stated both:

- `M1 partial: IMPLEMENTED + TESTED`
- `EVIDENCE CEILING: SPECIFIED`

### Canonical model (`reg/03-status-transition-audit-model.md`)

```text
SPECIFIED → IMPLEMENTED → TESTED → VERIFIED → PROVEN
```

| Status | Required evidence kind | May be inferred from cargo PASS? |
|---|---|---|
| SPECIFIED | provenance citation | n/a (bootstrap) |
| IMPLEMENTED | `source` + ledger entry | **NO** |
| TESTED | `test` + ledger entry | **NO** |
| VERIFIED | differential / mutation / crash-matrix | **NO** |
| PROVEN | proof artefact | **NO** |

`reg/status-transitions.json` entries: **0**.  
`reg/06` / `final/08`: status distribution **`{SPECIFIED: 184}`**.

Rule 4 (reg/03): transitions are **never** derived from “implementation ready”, “gate PASS”, or audit prose alone.

### Verdict

**GOVERNANCE INCONSISTENCY** (report wording only).

- Ladder words `IMPLEMENTED` / `TESTED` in the progress note were **not** backed by registry transitions.
- Pairing them with `EVIDENCE CEILING: SPECIFIED` was self-contradictory under R-REG.

**Correction applied (this review):**

- Progress note demoted to non-ladder language (“code present”; “local cargo gates PASS”).
- Canonical requirement statuses **unchanged** at `SPECIFIED`.
- No `reg/*` edits; no promotions.

**Post-correction:** **CONSISTENT** with EVIDENCE CEILING: SPECIFIED.

---

## 2. Implementation inventory

| Path | Role |
|---|---|
| `crates/ror-core/src/types.rs` | data-domain `Symbol`, `CapRef`, `ActorId`, `EffectId`, `Value` |
| `crates/ror-core/src/canonical/codec.rs` | envelope, cursor, traits |
| `crates/ror-core/src/canonical/primitives.rs` | standalone primitive codecs |
| `crates/ror-core/src/canonical/value.rs` | Value payload encode/decode |
| `crates/ror-core/src/canonical/data_decode.rs` | data-path entry + CapRef kernel helpers |
| `crates/ror-core/src/canonical/error.rs` | `CanonicalError` |
| `crates/ror-core/src/digest.rs` | pure-Rust SHA-256 + digest newtypes |
| `crates/ror-core/vectors/canonical/*` | golden fixtures |
| `docs/bootstrap/M1-PROGRESS.md` | progress note (governance-corrected) |

No production → `ror-reference` coupling. No third-party serializer crates.

---

## 3. Authority mapping (source → spec → requirement → verification)

| Implementation | Spec clause | Requirement | Verification obligation (registry) | Evidence class |
|---|---|---|---|---|
| Envelope `ver\|tag\|len_be\|payload` | S-17 R-CANON-02; R-CANON-13 | R-CANON-02, R-CANON-13 | golden vectors / format | EXECUTED tests + INDEPENDENT vectors (subset) |
| Standalone tags `0x00/0x20/0x30/0x40/0x41` | R-CANON-03 | R-CANON-03 | golden vectors; C-02 note | STATIC + EXECUTED |
| Value disc `0x00…0x07`; nested complete envelopes | R-CANON-04; Phase 15A sketch | R-CANON-04 | golden / round-trip | EXECUTED |
| Symbol 4B BE; CapRef 8B BE; ActorId/EffectId 8B BE | R-CANON-05 | R-CANON-05 | golden vectors | INDEPENDENT (`CapRef`, via R-CANON-11) |
| Map count-prefix; semantic Ord keys; `DuplicateMapKey` | R-CANON-06 | R-CANON-06 | M014 / ROR-011 | EXECUTED (synthetic duplicate) |
| Strict 5-check decoder; error set | R-CANON-07 | R-CANON-07 | ROR-010 malformed suite | EXECUTED (partial suite) |
| Checked lengths; no untrusted `with_capacity` | R-CANON-08 | R-CANON-08 | hostile-input properties | EXECUTED (structural) |
| `SHA-256(canonical_bytes)` | R-CANON-09 | R-CANON-09 | digest property tests | EXECUTED (KAT on hash; domain = raw bytes) |
| Injectivity claim scoped | R-CANON-10 | R-CANON-10 | round-trip + differential | EXECUTED round-trip only — **not VERIFIED** |
| Golden fixtures | R-CANON-11 | R-CANON-11 | M1 acceptance | INDEPENDENT + DERIVED (see §6) |
| Data path rejects `0x05` / standalone `0x30` | R-CANON-12 | R-CANON-12 | M022 negative vectors | EXECUTED |
| BE-only grammar; LE reject | R-CANON-13 | R-CANON-13 | M031 bidirectional | EXECUTED (LE length permute) |
| Independence of layout/serializers | R-CANON-01 | R-CANON-01 | format review | STATIC (hand-rolled codec) |

**Not claimed:** R-MARSHAL-* full surface; machine `Value` (R-CALC-01); effect body encoding (R-CALC-04 / U-21).

---

## 4. Canonical serialization audit (spec as oracle)

### Envelope — PASS (frozen subset)

| Check | Spec | Observed |
|---|---|---|
| Version `0x01` | R-CANON-02 | enforced |
| Type tag `u8` | R-CANON-02/13 | enforced |
| `payload_length` u32 **BE** | R-CANON-02/13 | enforced |
| Nested values = complete envelopes | R-CANON-04 | Symbol/CapRef/List/Map elements use `encode_canonical` / `read_envelope_payload` |
| Trailing bytes after envelope | R-CANON-07 (5) | `expect_eof` |
| Trailing bytes inside payload | R-CANON-07 | payload cursor `expect_eof` |
| Malformed version / tag | R-CANON-07 | `InvalidVersion` / `InvalidTypeTag` |

### Maps — PASS (frozen subset)

| Check | Spec | Observed |
|---|---|---|
| Count u32 BE | R-CANON-06 | yes |
| Key = Symbol envelope; val = Value envelope | R-CANON-04/06 | yes |
| Order = semantic `Ord` on `Symbol(u32)` | R-CANON-06 | `BTreeMap` iteration |
| Duplicate key → `DuplicateMapKey` | R-CANON-06 | yes (decode) |

### Capabilities — PASS after review fix

| Check | Spec | Observed |
|---|---|---|
| Data decode disc `0x05` → `CapabilityInData` | R-CANON-12 | yes |
| Standalone `0x30` on data path → `CapabilityInData` | R-CANON-12 | yes |
| Kernel CapRef codec separate | R-CANON-05/12 | `encode_cap_ref_kernel` / `decode_cap_ref_kernel` |
| Data encode must not emit capability | R-CANON-12 symmetry | **Fixed in review:** `Value::encode_payload` for `Capability` now returns `CapabilityInData` (previously could emit via public `CanonicalEncode`) |

### Digests — PASS with disclosed limits

| Check | Spec | Observed |
|---|---|---|
| Domain = canonical bytes | R-CANON-09 | `StateDigest::of_bytes` / `of_encoded` |
| Algorithm SHA-256 | R-CANON-09 | pure-Rust FIPS-oriented impl |
| No serializer metadata in digest input | R-CANON-01/09 | raw bytes only |
| Effect body encoding | U-21 OPEN | `EffectDigest::of_bytes` only — no effect type codec |

SHA-256 correctness is **not** “cargo test PASS alone”: independent KATs added (empty, `abc`, NIST two-block, fox, boundary lengths 55/56/64/65). Still **not** a cryptographic certification.

### LengthMismatch variant

Named in R-CANON-07 and present on `CanonicalError`, but **no production path currently constructs** `LengthMismatch` (framing mismatches surface as `UnexpectedEof` / tag errors). **Disclosed limitation** — not a byte-format defect; incomplete error-taxonomy exercise.

---

## 5. Golden vector independence

| Vector | Class | Notes |
|---|---|---|
| `integer_42` | **INDEPENDENT** | Byte-identical to R-CANON-11 text |
| `capref_5_2` | **INDEPENDENT** | Byte-identical to R-CANON-11 text |
| `unit`, `bool_true`, `map_sym_bool` | **DERIVED** | Computed from frozen grammar by external derivation; match files; **not** R-CANON-11 quotes |

External re-derivation (Python, this review) matched all five fixture files byte-exact.

Narrative sketch map with standalone tag `0x07` / len `0x28` is **non-normative** under R-CANON-03/04; conforming Value-envelope form (payload len `0x29`) is used. That choice follows frozen grammar, not encoder convenience.

**VECTOR EVIDENCE summary:** mandatory R-CANON-11 examples are **INDEPENDENT**. Supplemental fixtures are **DERIVED** (grammar-independent of Rust encoder, but not specification-quoted).

---

## 6. Decoder independence

| Concern | Finding |
|---|---|
| Shared defect risk (encode≈decode) | Decode uses explicit discriminant table + envelope framing; does not call encode |
| Malformed paths | version, tag, EOF, trailing, bad bool, bad disc, duplicate key, capability — covered |
| Trust of encoder assumptions | Decoder does not assume sorted keys beyond insert-order rebuild into `BTreeMap`; rejects duplicates |
| Round-trip tests | Necessary but insufficient alone; independent vectors + negative tests reduce collusion risk |

**Not claimed:** differential agreement with a second independent decoder (would be VERIFIED-class).

---

## 7. OAD non-resolution

| OAD | Register | Classification | Notes |
|---|---|---|---|
| **U-02** | OPEN | **NOT TOUCHED** | No machine-state encodings |
| **U-09** | OPEN | **ISOLATED** | Public type named `Value` is **documented as 15A data-domain only**, not machine R-CALC-01; provisional API docs added in review |
| **U-21** | OPEN | **NOT TOUCHED** | No Op/Target/Params/Effect codec |
| **U-24** | OPEN (register) | **ISOLATED** | Implementation uses 15A BE envelope per **R-CANON-13** (addendum freezes one grammar). Register row still OPEN — **not** closed by this code; code does not invent LE alternative |
| **U-25** | OPEN (register) | **ISOLATED** | Imports 15A TAG_* namespace per R-CANON-13; revised-grammar tags not exposed as Value standalone tags |
| **U-29** | OPEN | **ISOLATED** | `CanonicalError` shape provisional; documented; addendum variants included |
| **U-30** | OPEN | **NOT TOUCHED** | No `MarshalledValue` type |
| **U-37** | OPEN | **ISOLATED** | Wire widths follow R-CANON-05; no `usize` on wire; semantic usize domains untouched |

**No ACCIDENTALLY RESOLVED** items. No OAD register edits.

---

## 8. API boundary audit

| Surface | Risk | Disposition |
|---|---|---|
| `pub enum Value` | U-09 name collision | Provisional docs; data-domain only |
| `pub enum CanonicalError` | U-29 shape | Provisional docs |
| `TAG_*` / disc constants | U-25 | 15A-only; R-CANON-13 |
| `CapRef { index, generation }` | frozen layout R-CANON-05 | OK |
| `encode_cap_ref_kernel` | kernel path exposure | Named; not data path |
| `MarshalledValue` | U-30 | **absent** |
| Integer widths on structs | U-37 | Match R-CANON-05 wire types |

**Not BLOCKED:** open decisions that leak are **documented provisional**, not silent freezes of unauthorized envelopes. Full ABI stability is **not** claimed.

---

## 9. Execution evidence (fresh this review)

```text
command environment:
  RUSTUP_TOOLCHAIN=ror-stable
  rustc 1.88.0 (6b00bc388 2025-06-23)
  cargo 1.88.0 (873a06493 2025-05-10)
  (stable channel per rust-toolchain.toml; offline custom toolchain link — same as M0-B validation)
```

| Gate | Exit | Result |
|---|---|---|
| `cargo fmt --check` | 0 | **PASS** (EXECUTED) |
| `cargo check --workspace` | 0 | **PASS** (EXECUTED) |
| `cargo test --workspace` | 0 | **PASS** (EXECUTED) |
| `cargo clippy --workspace -- -D warnings` | 0 | **PASS** (EXECUTED) |

### Tests

| Crate | Tests | Notes |
|---|---|---|
| `ror-core` | **21** passed (0 failed) after review SHA-256 KAT expansion | unit tests only |
| other workspace crates | 0 | skeletons |

What tests **actually** check: golden loaders, round-trip pure data, duplicate key, capability reject, LE length reject, trailing/version errors, SHA-256 KATs, digest stability on Integer(42).

What they **do not** check: differential second decoder, mutation kills, full ROR-010 matrix, effect digests over real `Effect` values, machine-state codecs.

---

## 10. Reference / trust boundary

| Check | Result |
|---|---|
| `ror-core` → `ror-reference` | absent |
| production crates → reference | absent (unchanged from M0-B) |
| unsafe code | none; `#![forbid(unsafe_code)]` retained |
| external serializer defines format | no |

---

## 11. Registry preservation

| Path | Modified by M1 / this review? |
|---|---|
| `reg/requirements.json` | **NO** |
| `reg/requirements.schema.json` | **NO** |
| `reg/03-…` / `reg/04-…` / `reg/06-…` | **NO** |
| `final/03`, `final/04`, `final/08` | **NO** |
| `spec/`, `req/`, `dep/`, `mod/`, … | **NO** |
| `reg/status-transitions.json` | **NO** (still empty) |

### Candidate transitions (NOT applied)

| ID | Candidate | Evidence present in-tree | Missing for authorized promotion |
|---|---|---|---|
| R-CANON-02…08,11…13 (subset) | SPECIFIED → IMPLEMENTED | `source` files | ledger entry + owner approval + `spec/07` mapping update process |
| same | → TESTED | local `test` kind runs | ledger entry; `spec/08` mapping; broader suite |
| R-CANON-10 | → VERIFIED | — | differential / independent decoder evidence **absent** |
| any | → PROVEN | — | proof artefacts **absent** |

---

## 12. Governance summary

| Item | Value |
|---|---|
| Canonical specification modified | **NO** |
| Canonical registries modified | **NO** |
| Requirement statuses promoted | **NO** |
| OADs resolved | **NO** |
| Reference coupling introduced | **NO** |
| Unsafe code introduced | **NO** |
| Evidence ceiling | **SPECIFIED** |
| M1-PROGRESS ladder wording | **CORRECTED** (was inconsistent) |

---

## 13. Classification

### Frozen subset

```text
M1 FROZEN SUBSET = ACCEPTED WITH DISCLOSED EVIDENCE LIMITATIONS
```

**Accepted because:**

- Byte grammar matches frozen 15A / R-CANON-02…08/12/13 for the data domain.
- R-CANON-11 normative examples match exactly and are independent.
- Capability data-path ban holds (encode path tightened in review).
- Cargo gates re-executed PASS.
- OADs not silently closed; provisional API labeled.
- Registries untouched; statuses remain SPECIFIED.

**Disclosed limitations:**

1. Governance: in-tree code ≠ registry IMPLEMENTED/TESTED.
2. Vectors: only two fixtures are R-CANON-11-quoted; others DERIVED.
3. SHA-256: independent KATs added; not a certified crypto review.
4. `LengthMismatch` unused in production paths.
5. U-09/U-29 public types are provisional.
6. No differential second implementation (R-CANON-10 not VERIFIED).
7. U-24/U-25 remain OPEN in the OAD **register** even though R-CANON-13 freezes the grammar in the normative addendum (register staleness is pre-existing; not resolved here).

### Full milestone

```text
M1 full milestone = NOT COMPLETE
```

Open OADs (U-02, U-09, U-21, and register-open representation items) remain.

### M2

```text
M0 = GREEN
M1 frozen subset = ACCEPTED WITH DISCLOSED EVIDENCE LIMITATIONS
M1 full milestone = NOT COMPLETE
M2 = AUTHORIZED
```

M2 authorization is for work that does **not** require closed U-02/U-09/U-21 machine encodings; M2 (pure CEK) must still STOP on any ambiguity per R-SCOPE-03 and must not treat data-domain `Value` as the machine domain.

If a future change treats provisional `Value`/`CanonicalError` as ABI-frozen without OAD closure, reclassify frozen subset to **BLOCKED** until corrected.

---

## 14. Evidence category index

| Category | Used for |
|---|---|
| **EXECUTED** | cargo fmt/check/test/clippy this review; unit tests |
| **STATIC** | source inspection; OAD/spec reading; API surface |
| **DERIVED** | unit/bool/map fixtures from grammar; review re-derivation |
| **INDEPENDENT** | R-CANON-11 int42 + capref bytes; FIPS/NIST SHA-256 KATs |
| **NON-INDEPENDENT** | none of the R-CANON-11-quoted vectors |
| **OPEN** | U-02, U-09, U-21, U-24, U-25, U-29, U-30, U-37 (register) |

---

## 15. Review actions taken

1. Diagnosed GOVERNANCE INCONSISTENCY in M1-PROGRESS ladder wording → corrected.
2. Tightened `Value::Capability` encode to always `CapabilityInData` (R-CANON-12).
3. Expanded SHA-256 independent KATs (multi-block, boundaries).
4. Documented provisional U-09/U-29 API surface.
5. Documented vector provenance classes in `vectors/canonical/README.md`.
6. Produced this durable review report.
7. Did **not** modify canonical registries or promote requirements.
8. Did **not** begin M2 implementation in this operation.
