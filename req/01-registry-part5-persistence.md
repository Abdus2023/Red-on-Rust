# Atomic Requirement Registry — Part 5: Serialization, Persistence, Recovery (S-17 … S-19)

Areas: `CANON` (37), `PERSIST` (23), `RECOV` (22) — 82 atomic units.
Phase 15A is frozen down to byte level (`Red-on-Rust.md` L32936–33707, turn `[45]`, plus the duplicate-key patch L34987–35024, turn `[46]`); every constant below is copied, not paraphrased.

---

## S-17 Canonical serialization (frozen wire format, Phase 15A)

### REQ-CANON-001
- REQ-ID: REQ-CANON-001
- CATEGORY: serialization
- SOURCE: Red-on-Rust.md L28185–28228([35]); L28453–28465([36]); L41659–41690([60]); spec/01 S-17 R-CANON-01
- NORMATIVE-LEVEL: MUST
- STATEMENT: Semantic serialization is explicit and independent of Rust memory layout and of any Rust serializer.
- PRECONDITIONS: any canonical encoding
- POSTCONDITIONS: the byte layout is defined by this specification alone
- INVARIANTS: —
- DEPENDENCIES: REQ-CANON-004
- SECURITY-IMPACT: critical (layout-dependent encoding breaks reproducibility and injectivity)
- VERIFICATION-METHOD: golden vectors; format review
- EVIDENCE-STATUS: SPECIFIED

### REQ-CANON-002
- REQ-ID: REQ-CANON-002
- CATEGORY: serialization
- SOURCE: Red-on-Rust.md L28185–28228([35]); L29427 ([38]) ([39] "No `#[derive(Serialize)]`"); spec/01 S-17 R-CANON-01
- NORMATIVE-LEVEL: MUST NOT
- STATEMENT: `bincode` may *implement* the format but MUST NOT *define* it.
- PRECONDITIONS: implementation choice
- POSTCONDITIONS: the format is not derived from a serializer's behavior
- INVARIANTS: —
- DEPENDENCIES: REQ-CANON-001
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: format review; golden vectors
- EVIDENCE-STATUS: SPECIFIED

### REQ-CANON-003
- REQ-ID: REQ-CANON-003
- CATEGORY: serialization
- SOURCE: Red-on-Rust.md L28185–28228([35]); L28295([36]); spec/01 S-17 R-CANON-01
- NORMATIVE-LEVEL: MUST NOT
- STATEMENT: Canonical encoding is not based on struct layout, pointer addresses, allocator behavior, or platform-specific representation.
- PRECONDITIONS: any canonical encoding
- POSTCONDITIONS: bytes are reproducible across platforms and runs
- INVARIANTS: —
- DEPENDENCIES: REQ-CANON-001
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: golden vectors; canonical-bytes determinism check (M1 gate)
- EVIDENCE-STATUS: SPECIFIED

### REQ-CANON-004
- REQ-ID: REQ-CANON-004
- CATEGORY: serialization
- SOURCE: Red-on-Rust.md L30532–30543([41]); L33290–33347([45] final frozen); spec/01 S-17 R-CANON-02
- NORMATIVE-LEVEL: IS
- STATEMENT: The universal envelope is `version: u8` (currently `0x01`) `+ type_tag: u8` (stable explicit constant per type) `+ payload_length: u32 BE` (checked) `+ payload: bytes[payload_length]`.
- PRECONDITIONS: —
- POSTCONDITIONS: —
- INVARIANTS: — (single frame layout; kept whole per rule 6)
- DEPENDENCIES: REQ-CANON-005, REQ-CANON-019
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: golden vectors byte-exactness
- EVIDENCE-STATUS: SPECIFIED

### REQ-CANON-005
- REQ-ID: REQ-CANON-005
- CATEGORY: serialization
- SOURCE: Red-on-Rust.md L33087–33154([45]); spec/01 S-17 R-CANON-03
- NORMATIVE-LEVEL: IS
- STATEMENT: The standalone envelope type tags are exactly: `Value` = `0x00`, `Symbol` = `0x20`, `CapRef` = `0x30`, `ActorId` = `0x40`, `EffectId` = `0x41`.
- PRECONDITIONS: —
- POSTCONDITIONS: —
- INVARIANTS: — (closed tag set; no standalone envelopes exist for bool/integer/string)
- DEPENDENCIES: REQ-CANON-006, REQ-CANON-020
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: golden vectors; malformed-tag rejection
- EVIDENCE-STATUS: SPECIFIED

### REQ-CANON-006
- REQ-ID: REQ-CANON-006
- CATEGORY: serialization
- SOURCE: Red-on-Rust.md L30566([41] §1.3, stale); L30599–30646([41] golden vectors); L33087–33154([45]); spec/01 S-17 R-CANON-03; spec/06 C-02
- NORMATIVE-LEVEL: NON-NORMATIVE
- STATEMENT: The "revised grammar" §1.3 text listing Boolean `0x10`, Integer `0x11`, String `0x13` as standalone tags is stale: it contradicts the golden vectors of the same section and the final frozen implementation. An implementer reading only §1.3 would build a non-conforming decoder.
- PRECONDITIONS: —
- POSTCONDITIONS: —
- INVARIANTS: —
- DEPENDENCIES: REQ-CANON-005
- SECURITY-IMPACT: none (descriptive record of superseded text)
- VERIFICATION-METHOD: not applicable
- EVIDENCE-STATUS: SPECIFIED

### REQ-CANON-007
- REQ-ID: REQ-CANON-007
- CATEGORY: serialization
- SOURCE: Red-on-Rust.md L33155–33265([45]); L30544–30552([41] correction); spec/01 S-17 R-CANON-04
- NORMATIVE-LEVEL: IS
- STATEMENT: `Value := Envelope(type_tag = 0x00, payload = variant_discriminant: u8 + variant_payload)`.
- PRECONDITIONS: —
- POSTCONDITIONS: —
- INVARIANTS: —
- DEPENDENCIES: REQ-CANON-004, REQ-CANON-008
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: golden vectors
- EVIDENCE-STATUS: SPECIFIED

### REQ-CANON-008
- REQ-ID: REQ-CANON-008
- CATEGORY: serialization
- SOURCE: Red-on-Rust.md L33155–33265([45]); L33171–33173([45]); L33182–33183([45]); spec/01 S-17 R-CANON-04
- NORMATIVE-LEVEL: IS
- STATEMENT: The canonical `Value` type-tag constants are exactly `TAG_UNIT = 0x00`, `TAG_BOOL = 0x01`, `TAG_INTEGER = 0x02`, `TAG_STRING = 0x03`, `TAG_SYMBOL = 0x04`, `TAG_CAPABILITY = 0x05`, `TAG_LIST = 0x06`, `TAG_MAP = 0x07`; within the `Bool` payload, `0x00` decodes to false and `0x01` to true.
- PRECONDITIONS: —
- POSTCONDITIONS: —
- INVARIANTS: — (closed discriminant set)
- DEPENDENCIES: REQ-CANON-024
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: golden vectors; `InvalidDiscriminant` rejection
- EVIDENCE-STATUS: SPECIFIED

### REQ-CANON-009
- REQ-ID: REQ-CANON-009
- CATEGORY: serialization
- SOURCE: Red-on-Rust.md L33155–33200([45]); spec/01 S-17 R-CANON-04
- NORMATIVE-LEVEL: MUST
- STATEMENT: The `Bool` payload is 1 byte and MUST be `0x00` or `0x01` only.
- PRECONDITIONS: a `Bool` is encoded or decoded
- POSTCONDITIONS: any other byte is rejected
- INVARIANTS: —
- DEPENDENCIES: REQ-CANON-025
- SECURITY-IMPACT: high (two encodings of `true` would break injectivity)
- VERIFICATION-METHOD: `InvalidBoolValue` rejection test
- EVIDENCE-STATUS: SPECIFIED

### REQ-CANON-010
- REQ-ID: REQ-CANON-010
- CATEGORY: serialization
- SOURCE: Red-on-Rust.md L33155–33200([45]); spec/01 S-17 R-CANON-04
- NORMATIVE-LEVEL: IS
- STATEMENT: The `Integer` payload is 8 bytes, `i64`, big-endian two's complement.
- PRECONDITIONS: —
- POSTCONDITIONS: —
- INVARIANTS: —
- DEPENDENCIES: REQ-CANON-026
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: golden vectors (e.g. `Value::Integer(42)` ⇒ `01 00 00 00 00 09 02 00 00 00 00 00 00 00 2A`)
- EVIDENCE-STATUS: SPECIFIED

### REQ-CANON-011
- REQ-ID: REQ-CANON-011
- CATEGORY: serialization
- SOURCE: Red-on-Rust.md L33155–33200([45]); spec/01 S-17 R-CANON-04
- NORMATIVE-LEVEL: IS
- STATEMENT: The `String` payload is `[length u32 BE][UTF-8]`.
- PRECONDITIONS: —
- POSTCONDITIONS: invalid UTF-8 is rejected
- INVARIANTS: —
- DEPENDENCIES: REQ-CANON-025
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: golden vectors; `InvalidUtf8` rejection test
- EVIDENCE-STATUS: SPECIFIED

### REQ-CANON-012
- REQ-ID: REQ-CANON-012
- CATEGORY: serialization
- SOURCE: Red-on-Rust.md L33155–33265([45]); spec/01 S-17 R-CANON-04
- NORMATIVE-LEVEL: MUST
- STATEMENT: Nested values are encoded as complete canonical envelopes, not stripped payloads.
- PRECONDITIONS: a nested value is encoded
- POSTCONDITIONS: each nesting level carries its own envelope
- INVARIANTS: —
- DEPENDENCIES: REQ-CANON-004, REQ-CANON-029
- SECURITY-IMPACT: critical (stripped payloads make the encoding ambiguous)
- VERIFICATION-METHOD: golden vectors for nested structures; round-trip
- EVIDENCE-STATUS: SPECIFIED

### REQ-CANON-013
- REQ-ID: REQ-CANON-013
- CATEGORY: serialization
- SOURCE: Red-on-Rust.md L33087–33154([45]); spec/01 S-17 R-CANON-05
- NORMATIVE-LEVEL: IS
- STATEMENT: The `Symbol(u32)` payload is 4 bytes big-endian.
- PRECONDITIONS: —
- POSTCONDITIONS: —
- INVARIANTS: —
- DEPENDENCIES: REQ-CANON-005
- SECURITY-IMPACT: medium
- VERIFICATION-METHOD: golden vectors
- EVIDENCE-STATUS: SPECIFIED

### REQ-CANON-014
- REQ-ID: REQ-CANON-014
- CATEGORY: serialization
- SOURCE: Red-on-Rust.md L33087–33154([45]); spec/01 S-17 R-CANON-05
- NORMATIVE-LEVEL: IS
- STATEMENT: The `CapRef` payload is `[index u32 BE][generation u32 BE]`.
- PRECONDITIONS: —
- POSTCONDITIONS: —
- INVARIANTS: —
- DEPENDENCIES: REQ-CANON-005; AMB-07 (CapRef "never serialized" comment vs frozen CapRef tag)
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: golden vectors (e.g. `CapRef{5,2}` ⇒ `01 30 00 00 00 08 00 00 00 05 00 00 00 02`)
- EVIDENCE-STATUS: SPECIFIED

### REQ-CANON-015
- REQ-ID: REQ-CANON-015
- CATEGORY: serialization
- SOURCE: Red-on-Rust.md L33087–33154([45]); spec/01 S-17 R-CANON-05
- NORMATIVE-LEVEL: IS
- STATEMENT: The `ActorId` and `EffectId` payloads are 8 bytes `u64` big-endian.
- PRECONDITIONS: —
- POSTCONDITIONS: —
- INVARIANTS: —
- DEPENDENCIES: REQ-CANON-005
- SECURITY-IMPACT: medium
- VERIFICATION-METHOD: golden vectors
- EVIDENCE-STATUS: SPECIFIED

### REQ-CANON-016
- REQ-ID: REQ-CANON-016
- CATEGORY: serialization
- SOURCE: Red-on-Rust.md L33200–33240([45]); L30566–30573([41]); spec/01 S-17 R-CANON-06
- NORMATIVE-LEVEL: IS
- STATEMENT: `List = [count u32 BE][element₁]…[elementₙ]`, each element a complete envelope.
- PRECONDITIONS: —
- POSTCONDITIONS: —
- INVARIANTS: —
- DEPENDENCIES: REQ-CANON-012, REQ-CANON-028
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: golden vectors; hostile-input property tests
- EVIDENCE-STATUS: SPECIFIED

### REQ-CANON-017
- REQ-ID: REQ-CANON-017
- CATEGORY: serialization
- SOURCE: Red-on-Rust.md L33200–33240([45]); L33167([45]); L33221–33238([45]); spec/01 S-17 R-CANON-06
- NORMATIVE-LEVEL: MUST
- STATEMENT: `Map = [count u32 BE][key₁][val₁]…`, with keys of type `Symbol` collected into a `BTreeMap<Symbol, Value>`, so decoded entries are in ascending `Symbol` order.
- PRECONDITIONS: a map is encoded
- POSTCONDITIONS: entries appear in semantic key order
- INVARIANTS: —
- DEPENDENCIES: REQ-CANON-018, REQ-CANON-035
- SECURITY-IMPACT: critical (unordered maps would make the encoding non-injective)
- VERIFICATION-METHOD: golden vectors; ordering property tests
- EVIDENCE-STATUS: SPECIFIED

### REQ-CANON-018
- REQ-ID: REQ-CANON-018
- CATEGORY: serialization
- SOURCE: Red-on-Rust.md L34987–35024([47] final 15A patch); L33719([46]); L38164–38172([54] §11); L33712([46] § duplicate-key rule first stated); spec/01 S-17 R-CANON-06; spec/06 C-41
- NORMATIVE-LEVEL: MUST
- STATEMENT: Map decoding MUST reject duplicate keys with `CanonicalError::DuplicateMapKey`, to preserve injectivity.
- PRECONDITIONS: a decoded map contains a repeated key
- POSTCONDITIONS: decoding fails with the specified error
- INVARIANTS: injectivity of the encoding
- DEPENDENCIES: REQ-CANON-035
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: mutation M014; duplicate-map-key regression (ROR-011); M1 gate
- EVIDENCE-STATUS: SPECIFIED

### REQ-CANON-019
- REQ-ID: REQ-CANON-019
- CATEGORY: serialization
- SOURCE: Red-on-Rust.md L32948–33049([45]); L30575–30586([41]); spec/01 S-17 R-CANON-07
- NORMATIVE-LEVEL: MUST
- STATEMENT: `CanonicalDecode` enforces check (1): `version = 0x01`.
- PRECONDITIONS: any decode
- POSTCONDITIONS: any other version is rejected with `InvalidVersion`
- INVARIANTS: —
- DEPENDENCIES: REQ-CANON-025
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: malformed-input suite (ROR-010)
- EVIDENCE-STATUS: SPECIFIED

### REQ-CANON-020
- REQ-ID: REQ-CANON-020
- CATEGORY: serialization
- SOURCE: Red-on-Rust.md L32948–33049([45]); L30575–30586([41]); spec/01 S-17 R-CANON-07
- NORMATIVE-LEVEL: MUST
- STATEMENT: `CanonicalDecode` enforces check (2): the type tag matches the expected tag.
- PRECONDITIONS: any decode
- POSTCONDITIONS: a mismatch is rejected with `InvalidTypeTag`
- INVARIANTS: —
- DEPENDENCIES: REQ-CANON-005
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: malformed-input suite
- EVIDENCE-STATUS: SPECIFIED

### REQ-CANON-021
- REQ-ID: REQ-CANON-021
- CATEGORY: serialization
- SOURCE: Red-on-Rust.md L32948–33049([45]); L30575–30586([41]); L30539–30544([41]); L33812–33816([46]); spec/01 S-17 R-CANON-07
- NORMATIVE-LEVEL: MUST
- STATEMENT: `CanonicalDecode` enforces check (3): exact length — the payload is exactly `payload_length` bytes.
- PRECONDITIONS: any decode
- POSTCONDITIONS: a length mismatch is rejected with `LengthMismatch`
- INVARIANTS: —
- DEPENDENCIES: REQ-CANON-026
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: malformed-input suite
- EVIDENCE-STATUS: SPECIFIED

### REQ-CANON-022
- REQ-ID: REQ-CANON-022
- CATEGORY: serialization
- SOURCE: Red-on-Rust.md L32948–33049([45]); L30575–30586([41]); spec/01 S-17 R-CANON-07
- NORMATIVE-LEVEL: MUST
- STATEMENT: `CanonicalDecode` enforces check (4): internal payload well-formedness.
- PRECONDITIONS: any decode
- POSTCONDITIONS: a malformed payload is rejected with the specific `CanonicalError`
- INVARIANTS: —
- DEPENDENCIES: REQ-CANON-009, REQ-CANON-011
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: malformed-input suite
- EVIDENCE-STATUS: SPECIFIED

### REQ-CANON-023
- REQ-ID: REQ-CANON-023
- CATEGORY: serialization
- SOURCE: Red-on-Rust.md L32948–33049([45]); L30575–30586([41]); spec/01 S-17 R-CANON-07
- NORMATIVE-LEVEL: MUST
- STATEMENT: `CanonicalDecode` enforces check (5): EOF and trailing-byte rejection.
- PRECONDITIONS: any decode
- POSTCONDITIONS: `UnexpectedEof` / `TrailingBytes` are produced as appropriate
- INVARIANTS: —
- DEPENDENCIES: REQ-CANON-025
- SECURITY-IMPACT: high (accepting trailing bytes permits malleable encodings)
- VERIFICATION-METHOD: malformed-input suite
- EVIDENCE-STATUS: SPECIFIED

### REQ-CANON-024
- REQ-ID: REQ-CANON-024
- CATEGORY: serialization
- SOURCE: Red-on-Rust.md L30575–30586([41]); L33155–33265([45]); spec/01 S-17 R-CANON-07
- NORMATIVE-LEVEL: MUST NOT
- STATEMENT: All discriminants are explicit stable constants; source-order changes MUST NOT change the wire format.
- PRECONDITIONS: any refactor of the Rust enums
- POSTCONDITIONS: the byte format is unchanged
- INVARIANTS: —
- DEPENDENCIES: REQ-CANON-008
- SECURITY-IMPACT: critical (a silent format change invalidates every durable artifact)
- VERIFICATION-METHOD: golden vectors as a regression gate
- EVIDENCE-STATUS: SPECIFIED

### REQ-CANON-025
- REQ-ID: REQ-CANON-025
- CATEGORY: serialization
- SOURCE: Red-on-Rust.md L32959–32990([45]); L34994–34996([47]); spec/01 S-17 R-CANON-07
- NORMATIVE-LEVEL: MUST
- STATEMENT: Malformed encodings are rejected with explicit `CanonicalError` values: `InvalidVersion, InvalidTypeTag, LengthMismatch, LengthOverflow, InvalidUtf8, UnexpectedEof, TrailingBytes, InvalidDiscriminant, InvalidBoolValue, DuplicateMapKey`.
- PRECONDITIONS: a malformed input is decoded
- POSTCONDITIONS: the specific error is returned, never a panic
- INVARIANTS: — (closed error set)
- DEPENDENCIES: REQ-CANON-019…REQ-CANON-023
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: malformed-input suite (ROR-010)
- EVIDENCE-STATUS: SPECIFIED

### REQ-CANON-026
- REQ-ID: REQ-CANON-026
- CATEGORY: serialization
- SOURCE: Red-on-Rust.md L32948–33049([45]); L30574–30578([41]); spec/01 S-17 R-CANON-08
- NORMATIVE-LEVEL: MUST
- STATEMENT: All length/pointer arithmetic in the codec is checked.
- PRECONDITIONS: any arithmetic on untrusted lengths
- POSTCONDITIONS: overflow is detected, not wrapped
- INVARIANTS: —
- DEPENDENCIES: REQ-CANON-027
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: hostile-input property tests
- EVIDENCE-STATUS: SPECIFIED

### REQ-CANON-027
- REQ-ID: REQ-CANON-027
- CATEGORY: serialization
- SOURCE: Red-on-Rust.md L32948–33049([45]); L29668([40]); spec/01 S-17 R-CANON-08
- NORMATIVE-LEVEL: MUST
- STATEMENT: A collection exceeding `u32::MAX` yields `LengthOverflow`.
- PRECONDITIONS: an oversized collection length is decoded
- POSTCONDITIONS: `LengthOverflow` is returned
- INVARIANTS: —
- DEPENDENCIES: REQ-CANON-026
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: hostile-input property tests
- EVIDENCE-STATUS: SPECIFIED

### REQ-CANON-028
- REQ-ID: REQ-CANON-028
- CATEGORY: serialization
- SOURCE: Red-on-Rust.md L32948–33049([45]); L30574–30578([41]); L33157([45]); spec/01 S-17 R-CANON-08
- NORMATIVE-LEVEL: MUST NOT
- STATEMENT: Decoding MUST prevent hostile allocation: decoded collections are built from `Vec::new()` and are never preallocated from an attacker-supplied count.
- PRECONDITIONS: decoding an untrusted collection
- POSTCONDITIONS: no allocation is sized by the attacker-supplied count
- INVARIANTS: —
- DEPENDENCIES: REQ-CANON-026
- SECURITY-IMPACT: critical (a large count would cause memory exhaustion)
- VERIFICATION-METHOD: hostile-input property tests; memory-usage assertions
- EVIDENCE-STATUS: SPECIFIED

### REQ-CANON-029
- REQ-ID: REQ-CANON-029
- CATEGORY: serialization
- SOURCE: Red-on-Rust.md L32948–33265([45]); spec/01 S-17 R-CANON-08
- NORMATIVE-LEVEL: MUST
- STATEMENT: Nested decoding uses bounded cursors: `read_envelope_payload` returns only the payload slice, and payload decoding uses a fresh bounded cursor.
- PRECONDITIONS: nested structures are decoded
- POSTCONDITIONS: a nested decode cannot read beyond its own payload
- INVARIANTS: —
- DEPENDENCIES: REQ-CANON-012
- SECURITY-IMPACT: critical (unbounded cursors allow cross-field confusion)
- VERIFICATION-METHOD: hostile-input property tests
- EVIDENCE-STATUS: SPECIFIED

### REQ-CANON-030
- REQ-ID: REQ-CANON-030
- CATEGORY: serialization
- SOURCE: Red-on-Rust.md L33266–33286([45] freeze); spec/01 S-17 R-CANON-08
- NORMATIVE-LEVEL: MUST
- STATEMENT: Envelope construction is fallible; the codec does not panic.
- PRECONDITIONS: any encode/decode
- POSTCONDITIONS: failures are returned as errors
- INVARIANTS: —
- DEPENDENCIES: REQ-CANON-025
- SECURITY-IMPACT: high (a panic on hostile input is a denial-of-service path)
- VERIFICATION-METHOD: fuzzing without panics; malformed-input suite
- EVIDENCE-STATUS: SPECIFIED

### REQ-CANON-031
- REQ-ID: REQ-CANON-031
- CATEGORY: serialization
- SOURCE: Red-on-Rust.md L28185–28228([35]); L30588–30590([41]); spec/01 S-17 R-CANON-09
- NORMATIVE-LEVEL: IS
- STATEMENT: `StateDigest = SHA-256(canonical_bytes)` and `EffectDigest = SHA-256(canonical_bytes(effect))`.
- PRECONDITIONS: —
- POSTCONDITIONS: —
- INVARIANTS: —
- DEPENDENCIES: REQ-CALC-008
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: digest property tests
- EVIDENCE-STATUS: SPECIFIED

### REQ-CANON-032
- REQ-ID: REQ-CANON-032
- CATEGORY: serialization
- SOURCE: Red-on-Rust.md L28229–28240([35] correction); L30588–30590([41]); spec/01 S-17 R-CANON-09
- NORMATIVE-LEVEL: MUST
- STATEMENT: `Canonical(x) = Canonical(y) ⇒ Digest(x) = Digest(y)`.
- PRECONDITIONS: two values with equal canonical bytes
- POSTCONDITIONS: their digests are equal
- INVARIANTS: `Canonical(x) = Canonical(y) ⇒ Digest(x) = Digest(y)`
- DEPENDENCIES: REQ-CANON-031
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: digest property tests
- EVIDENCE-STATUS: SPECIFIED

### REQ-CANON-033
- REQ-ID: REQ-CANON-033
- CATEGORY: serialization
- SOURCE: Red-on-Rust.md L28229–28240([35] correction); L27881–27883([34] Pillar 1, superseded); spec/01 S-17 R-CANON-09; spec/06 C-13
- NORMATIVE-LEVEL: NON-NORMATIVE
- STATEMENT: The reverse direction (digest equality ⇒ byte equality) holds only as an operational integrity assumption under cryptographic collision resistance; the earlier claim that equal digests prove byte-for-byte identity is superseded.
- PRECONDITIONS: —
- POSTCONDITIONS: —
- INVARIANTS: —
- DEPENDENCIES: REQ-CANON-034
- SECURITY-IMPACT: none (descriptive; constrains what may be claimed)
- VERIFICATION-METHOD: not applicable
- EVIDENCE-STATUS: SPECIFIED

### REQ-CANON-034
- REQ-ID: REQ-CANON-034
- CATEGORY: serialization
- SOURCE: Red-on-Rust.md L28229–28240([35]); spec/01 S-17 R-CANON-09
- NORMATIVE-LEVEL: MUST
- STATEMENT: When both states are available, canonical bytes are compared directly; digests are used for persistence integrity, causal identity, and compact checkpoints.
- PRECONDITIONS: both states are available for comparison
- POSTCONDITIONS: the comparison uses bytes, not digests
- INVARIANTS: —
- DEPENDENCIES: REQ-REF-011
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: comparator review
- EVIDENCE-STATUS: SPECIFIED

### REQ-CANON-035
- REQ-ID: REQ-CANON-035
- CATEGORY: serialization
- SOURCE: Red-on-Rust.md L30592–30598([41] corrected wording); L28464([36]); L35068([47]); spec/01 S-17 R-CANON-10; spec/06 C-12
- NORMATIVE-LEVEL: MUST
- STATEMENT: Injectivity — `Canonical(x) = Canonical(y) ⇒ x = y` — is a structural specification property of the encoding design.
- PRECONDITIONS: any two values
- POSTCONDITIONS: equal encodings imply equal values
- INVARIANTS: `Canonical(x) = Canonical(y) ⇒ x = y`
- DEPENDENCIES: REQ-CANON-017, REQ-CANON-018, REQ-CANON-009
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: round-trip plus differential testing over the generated distribution
- EVIDENCE-STATUS: SPECIFIED

### REQ-CANON-036
- REQ-ID: REQ-CANON-036
- CATEGORY: serialization
- SOURCE: Red-on-Rust.md L30592–30598([41]); L35068([47]); spec/01 S-17 R-CANON-10
- NORMATIVE-LEVEL: MUST NOT
- STATEMENT: Injectivity is NOT claimed as a mathematical proof over arbitrary Rust programs; the evidence is machine-checked over the tested distribution.
- PRECONDITIONS: any conformance claim
- POSTCONDITIONS: the claim is scoped to the tested state space
- INVARIANTS: —
- DEPENDENCIES: REQ-CLAIM-017
- SECURITY-IMPACT: medium (claim discipline)
- VERIFICATION-METHOD: report review
- EVIDENCE-STATUS: SPECIFIED

### REQ-CANON-037
- REQ-ID: REQ-CANON-037
- CATEGORY: serialization
- SOURCE: Red-on-Rust.md L30599–30646([41]); L31948–32010([43] regenerated); L33266–33286([45] freeze); spec/01 S-17 R-CANON-11
- NORMATIVE-LEVEL: MUST
- STATEMENT: The frozen golden vectors are normative test fixtures for the format; they are not additional behavioral rules.
- PRECONDITIONS: an implementation of the codec exists
- POSTCONDITIONS: it reproduces every golden vector byte-for-byte
- INVARIANTS: —
- DEPENDENCIES: REQ-CANON-004…REQ-CANON-018
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: golden-vector byte-exactness (M1 acceptance gate)
- EVIDENCE-STATUS: SPECIFIED

---

## S-18 Persistence protocol (Phase 15B)

### REQ-PERSIST-001
- REQ-ID: REQ-PERSIST-001
- CATEGORY: persistence
- SOURCE: Red-on-Rust.md L33757–33790([46]); L35078–35087([47]); L38187([54] §12); spec/01 S-18 R-PERSIST-01
- NORMATIVE-LEVEL: MUST NOT
- STATEMENT: The persistence layer is not a semantic machine; it records and reconstructs the existing machine.
- PRECONDITIONS: persistence implementation
- POSTCONDITIONS: no semantic decisions are made in the persistence layer
- INVARIANTS: —
- DEPENDENCIES: REQ-PERSIST-002
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: dependency review (15B acceptance matrix)
- EVIDENCE-STATUS: SPECIFIED

### REQ-PERSIST-002
- REQ-ID: REQ-PERSIST-002
- CATEGORY: persistence
- SOURCE: Red-on-Rust.md L33757–33790([46]); L35078–35087([47]); L38187–38201([54] §12); L34264([46] parser rejections); spec/01 S-18 R-PERSIST-01
- NORMATIVE-LEVEL: MUST NOT
- STATEMENT: No secondary serialization: the payload of every persistence record is strictly the byte output of Phase 15A `CanonicalEncode`.
- PRECONDITIONS: any record is written
- POSTCONDITIONS: its payload bytes are 15A output
- INVARIANTS: —
- DEPENDENCIES: REQ-CANON-001
- SECURITY-IMPACT: critical (a second encoding would create divergent identities for the same object)
- VERIFICATION-METHOD: dependency review; payload round-trip tests
- EVIDENCE-STATUS: SPECIFIED

### REQ-PERSIST-003
- REQ-ID: REQ-PERSIST-003
- CATEGORY: persistence
- SOURCE: Red-on-Rust.md L33802–33830([46]); L35088–35110([47]); spec/01 S-18 R-PERSIST-02
- NORMATIVE-LEVEL: IS
- STATEMENT: Level 1 (semantic) framing is the 15A envelope `version | type_tag | payload_length | payload`, answering "what object is this?".
- PRECONDITIONS: —
- POSTCONDITIONS: —
- INVARIANTS: —
- DEPENDENCIES: REQ-CANON-004
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: framing conformance tests
- EVIDENCE-STATUS: SPECIFIED

### REQ-PERSIST-004
- REQ-ID: REQ-PERSIST-004
- CATEGORY: persistence
- SOURCE: Red-on-Rust.md L35099–35110([47]); L34237([46]); spec/01 S-18 R-PERSIST-02
- NORMATIVE-LEVEL: IS
- STATEMENT: Level 2 (persistence) framing is `WalFrame { sequence: WalSequence (u64, strictly monotonic), kind: WalRecordKind (u8), payload_length: u32 BE (checked), payload (15A bytes), checksum: SHA-256(sequence ‖ kind ‖ payload_length ‖ payload) }`, answering "where is the record and is it intact?".
- PRECONDITIONS: —
- POSTCONDITIONS: —
- INVARIANTS: checksum covers sequence, kind, length, and payload
- DEPENDENCIES: REQ-PERSIST-008, REQ-PERSIST-021
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: negative parsing tests; mutation M016
- EVIDENCE-STATUS: SPECIFIED

### REQ-PERSIST-005
- REQ-ID: REQ-PERSIST-005
- CATEGORY: persistence
- SOURCE: Red-on-Rust.md L33802–33830([46]); L35088–35110([47]); spec/01 S-18 R-PERSIST-02
- NORMATIVE-LEVEL: MUST
- STATEMENT: The WAL parser MUST reject truncated headers.
- PRECONDITIONS: a frame header is incomplete
- POSTCONDITIONS: the record is rejected
- INVARIANTS: —
- DEPENDENCIES: REQ-PERSIST-004
- SECURITY-IMPACT: high ; AMB-14
- VERIFICATION-METHOD: negative parsing tests
- EVIDENCE-STATUS: SPECIFIED

### REQ-PERSIST-006
- REQ-ID: REQ-PERSIST-006
- CATEGORY: persistence
- SOURCE: Red-on-Rust.md L33802–33830([46]); L35088–35110([47]); spec/01 S-18 R-PERSIST-02
- NORMATIVE-LEVEL: MUST
- STATEMENT: The WAL parser MUST reject truncated payloads.
- PRECONDITIONS: a frame payload is shorter than declared
- POSTCONDITIONS: the record is rejected
- INVARIANTS: —
- DEPENDENCIES: REQ-PERSIST-004
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: negative parsing tests
- EVIDENCE-STATUS: SPECIFIED

### REQ-PERSIST-007
- REQ-ID: REQ-PERSIST-007
- CATEGORY: persistence
- SOURCE: Red-on-Rust.md L33802–33830([46]); L35088–35110([47]); spec/01 S-18 R-PERSIST-02
- NORMATIVE-LEVEL: MUST
- STATEMENT: The WAL parser MUST reject impossible lengths.
- PRECONDITIONS: a declared length cannot be satisfied
- POSTCONDITIONS: the record is rejected without preallocation
- INVARIANTS: —
- DEPENDENCIES: REQ-CANON-028
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: hostile-input tests
- EVIDENCE-STATUS: SPECIFIED

### REQ-PERSIST-008
- REQ-ID: REQ-PERSIST-008
- CATEGORY: persistence
- SOURCE: Red-on-Rust.md L33802–33830([46]); L35099–35110([47]); spec/01 S-18 R-PERSIST-02
- NORMATIVE-LEVEL: MUST
- STATEMENT: The WAL parser MUST reject checksum mismatches.
- PRECONDITIONS: the computed checksum differs from the stored one
- POSTCONDITIONS: the record is rejected
- INVARIANTS: —
- DEPENDENCIES: REQ-PERSIST-004
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: mutation M016 (ignore checksum mismatch)
- EVIDENCE-STATUS: SPECIFIED

### REQ-PERSIST-009
- REQ-ID: REQ-PERSIST-009
- CATEGORY: persistence
- SOURCE: Red-on-Rust.md L33802–33830([46]); L35088–35110([47]); spec/01 S-18 R-PERSIST-02
- NORMATIVE-LEVEL: MUST
- STATEMENT: The WAL parser MUST reject invalid record kinds.
- PRECONDITIONS: `kind` is outside `WalRecordKind`
- POSTCONDITIONS: the record is rejected
- INVARIANTS: —
- DEPENDENCIES: REQ-PERSIST-014
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: negative parsing tests
- EVIDENCE-STATUS: SPECIFIED

### REQ-PERSIST-010
- REQ-ID: REQ-PERSIST-010
- CATEGORY: persistence
- SOURCE: Red-on-Rust.md L33802–33830([46]); L35088–35110([47]); spec/01 S-18 R-PERSIST-02
- NORMATIVE-LEVEL: MUST
- STATEMENT: The WAL parser MUST reject sequence regressions.
- PRECONDITIONS: a frame's sequence is not greater than the previous
- POSTCONDITIONS: the record is rejected
- INVARIANTS: `WalSequence` strictly monotonic
- DEPENDENCIES: REQ-PERSIST-021
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: `WAL-SEQUENCE-CONTINUITY`
- EVIDENCE-STATUS: SPECIFIED

### REQ-PERSIST-011
- REQ-ID: REQ-PERSIST-011
- CATEGORY: persistence
- SOURCE: Red-on-Rust.md L33802–33830([46]); L35189–35208([47]); spec/01 S-18 R-PERSIST-02
- NORMATIVE-LEVEL: MUST
- STATEMENT: The WAL parser MUST reject sequence gaps.
- PRECONDITIONS: `s_{n+1} ≠ s_n + 1`
- POSTCONDITIONS: the record is rejected
- INVARIANTS: `s_{n+1} = s_n + 1`
- DEPENDENCIES: REQ-PERSIST-022
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: `WAL-GAP-REJECT`; mutation M015
- EVIDENCE-STATUS: SPECIFIED

### REQ-PERSIST-012
- REQ-ID: REQ-PERSIST-012
- CATEGORY: persistence
- SOURCE: Red-on-Rust.md L33802–33830([46]); L35088–35110([47]); spec/01 S-18 R-PERSIST-02
- NORMATIVE-LEVEL: MUST
- STATEMENT: The WAL parser MUST reject malformed canonical payloads.
- PRECONDITIONS: the 15A payload fails `CanonicalDecode`
- POSTCONDITIONS: the record is rejected with the `CanonicalError`
- INVARIANTS: —
- DEPENDENCIES: REQ-CANON-025, REQ-PERSIST-002
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: negative parsing tests
- EVIDENCE-STATUS: SPECIFIED

### REQ-PERSIST-013
- REQ-ID: REQ-PERSIST-013
- CATEGORY: persistence
- SOURCE: Red-on-Rust.md L33802–33830([46]); L35088–35110([47]); spec/01 S-18 R-PERSIST-02
- NORMATIVE-LEVEL: MUST
- STATEMENT: The WAL parser MUST reject trailing bytes.
- PRECONDITIONS: bytes remain after the declared frame
- POSTCONDITIONS: the input is rejected
- INVARIANTS: —
- DEPENDENCIES: REQ-CANON-023
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: negative parsing tests
- EVIDENCE-STATUS: SPECIFIED

### REQ-PERSIST-014
- REQ-ID: REQ-PERSIST-014
- CATEGORY: persistence
- SOURCE: Red-on-Rust.md L35127–35144([47]); L33905–33930([46]); L26146–26150([33] separate-journal form, superseded); spec/01 S-18 R-PERSIST-03; spec/06 C-25, C-39
- NORMATIVE-LEVEL: IS
- STATEMENT: `WalRecord ::= Event(EventEnvelope) | EffectPrepared { id, actor, digest } | EffectIssued { id, actor, digest } | EffectCompleted { id, digest, result_digest } | EffectReconciled { id, digest, outcome } | SnapshotCommit { event_sequence, snapshot_version, state_digest }`.
- PRECONDITIONS: —
- POSTCONDITIONS: —
- INVARIANTS: — (closed record set)
- DEPENDENCIES: U-15 (`ReconciliationOutcome` variants undefined); U-16
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: journal validator; record-kind coverage
- EVIDENCE-STATUS: SPECIFIED

### REQ-PERSIST-015
- REQ-ID: REQ-PERSIST-015
- CATEGORY: persistence
- SOURCE: Red-on-Rust.md L33861–33900([46]); L35111–35144([47]); spec/01 S-18 R-PERSIST-03
- NORMATIVE-LEVEL: MUST
- STATEMENT: `EventEnvelope { sequence: EventSequence, logical_time: LogicalTime, event: GlobalEvent }` with `e_i.sequence < e_{i+1}.sequence` (total ordering).
- PRECONDITIONS: events are appended
- POSTCONDITIONS: sequences strictly increase
- INVARIANTS: `e_i.sequence < e_{i+1}.sequence`
- DEPENDENCIES: U-16 (`EventSequence` vs `WalSequence` relationship undefined)
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: sequence property tests
- EVIDENCE-STATUS: SPECIFIED

### REQ-PERSIST-016
- REQ-ID: REQ-PERSIST-016
- CATEGORY: persistence
- SOURCE: Red-on-Rust.md L26293–26330([33]); L34156([46] snapshot scheduler state); spec/01 S-18 R-PERSIST-04
- NORMATIVE-LEVEL: MUST
- STATEMENT: A snapshot contains all machine state necessary to continue execution: logical time, ID counters, runnable queue, and per actor run state / `EvalState` / capabilities / heap / budget / mailbox / status, plus scheduler state, plus `version, last_event_sequence, last_effect_sequence, state_digest`.
- PRECONDITIONS: a snapshot is taken
- POSTCONDITIONS: execution can continue from it alone
- INVARIANTS: —
- DEPENDENCIES: U-02 (no frozen canonical encoding for machine state), U-17
- SECURITY-IMPACT: critical ; AMB-02
- VERIFICATION-METHOD: snapshot content review; recovery differential
- EVIDENCE-STATUS: SPECIFIED

### REQ-PERSIST-017
- REQ-ID: REQ-PERSIST-017
- CATEGORY: persistence
- SOURCE: Red-on-Rust.md L26293–26330([33]); L1177–1181([3]); spec/01 S-18 R-PERSIST-04
- NORMATIVE-LEVEL: MUST NOT
- STATEMENT: A snapshot MUST NOT serialize host implementation state: `HostExecutor`, OS handles, file descriptors, threads, sockets, raw pointers, process handles, or unvalidated host objects; these are reconstructed by the host adapter.
- PRECONDITIONS: a snapshot is taken
- POSTCONDITIONS: no host-implementation state is present
- INVARIANTS: —
- DEPENDENCIES: REQ-PERSIST-016
- SECURITY-IMPACT: critical (persisting handles would create non-replayable, unsafe state)
- VERIFICATION-METHOD: snapshot content review
- EVIDENCE-STATUS: SPECIFIED

### REQ-PERSIST-018
- REQ-ID: REQ-PERSIST-018
- CATEGORY: persistence
- SOURCE: Red-on-Rust.md L26216–26240([33]); L35177–35188([47]); spec/01 S-18 R-PERSIST-05
- NORMATIVE-LEVEL: MUST
- STATEMENT: Snapshot creation is transactional: (1) write `SnapshotBegin` marker; (2) write the canonical `GlobalSnapshot` payload (15A-encoded); (3) fsync the payload; (4) write the `SnapshotCommit` record (with `state_digest`); (5) fsync the commit record.
- PRECONDITIONS: a snapshot is requested
- POSTCONDITIONS: the five steps occur in order
- INVARIANTS: — (ordered protocol; kept whole per rule 6)
- DEPENDENCIES: REQ-PERSIST-019
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: crash point T6
- EVIDENCE-STATUS: SPECIFIED

### REQ-PERSIST-019
- REQ-ID: REQ-PERSIST-019
- CATEGORY: persistence
- SOURCE: Red-on-Rust.md L35177–35188([47]); L26216–26240([33]); L38252–L38260([54] §13); L34212–L34223([46] snapshot validity); spec/01 S-18 R-PERSIST-05
- NORMATIVE-LEVEL: MUST
- STATEMENT: `ValidSnapshot(S) ⇔ Commit(S) ∧ Digest(Canonical(S)) = RecordedDigest(S)`.
- PRECONDITIONS: a snapshot is evaluated for validity
- POSTCONDITIONS: validity holds iff a durable commit exists and the digest matches
- INVARIANTS: `ValidSnapshot(S) ⇔ Commit(S) ∧ Digest(Canonical(S)) = RecordedDigest(S)`
- DEPENDENCIES: REQ-PERSIST-020, REQ-CANON-031
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: `SNAPSHOT-COMMIT-INTEGRITY`
- EVIDENCE-STATUS: SPECIFIED

### REQ-PERSIST-020
- REQ-ID: REQ-PERSIST-020
- CATEGORY: persistence
- SOURCE: Red-on-Rust.md L26216–26240([33]); L35177–35188([47]); spec/01 S-18 R-PERSIST-05
- NORMATIVE-LEVEL: MUST
- STATEMENT: Recovery MUST ignore any snapshot lacking the durable `SnapshotCommit` marker; partial snapshots are garbage.
- PRECONDITIONS: recovery scans snapshots
- POSTCONDITIONS: an uncommitted snapshot is not used as a base
- INVARIANTS: —
- DEPENDENCIES: REQ-PERSIST-019
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: crash point T6; partial-snapshot tests
- EVIDENCE-STATUS: SPECIFIED

### REQ-PERSIST-021
- REQ-ID: REQ-PERSIST-021
- CATEGORY: persistence
- SOURCE: Red-on-Rust.md L35099–35110([47]); L35189–35208([47]); spec/01 S-18 R-PERSIST-06
- NORMATIVE-LEVEL: MUST
- STATEMENT: WAL sequence continuity MUST hold: `s_{n+1} = s_n + 1`.
- PRECONDITIONS: any two consecutive WAL frames
- POSTCONDITIONS: the successor sequence is exactly one greater
- INVARIANTS: `s_{n+1} = s_n + 1`
- DEPENDENCIES: REQ-PERSIST-010, REQ-PERSIST-011
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: `WAL-SEQUENCE-CONTINUITY`; mutation M015
- EVIDENCE-STATUS: SPECIFIED

### REQ-PERSIST-022
- REQ-ID: REQ-PERSIST-022
- CATEGORY: persistence
- SOURCE: Red-on-Rust.md L35189–35208([47]); L38164–38172([54] §11 alias); spec/01 S-18 R-PERSIST-06
- NORMATIVE-LEVEL: MUST
- STATEMENT: Gaps are rejected (obligation tags `WAL-GAP-REJECT` / `WAL-SEQUENCE-CONTINUITY`).
- PRECONDITIONS: a gap is detected
- POSTCONDITIONS: recovery/parsing fails rather than skipping
- INVARIANTS: `s_{n+1} = s_n + 1`
- DEPENDENCIES: REQ-PERSIST-021, REQ-RECOV-011
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: `WAL-GAP-REJECT`; mutation M015
- EVIDENCE-STATUS: SPECIFIED

---

## S-19 Crash recovery

### REQ-PERSIST-023
- REQ-ID: REQ-PERSIST-023
- CATEGORY: persistence
- SOURCE: Red-on-Rust.md L33731–33738([46]); L34987–35024([47] final 15A patch); spec/01 S-18 R-PERSIST-05
- NORMATIVE-LEVEL: MUST
- STATEMENT: The persistence layer establishes `Committed(D) ⇒ Canonical(D) ∧ IntegrityVerified(D)`: a committed durable artifact is canonically encoded and its integrity is verified.
- PRECONDITIONS: a durable artifact `D` carries a commit marker
- POSTCONDITIONS: `D` decodes under the 15A canonical codec and passes its checksum
- INVARIANTS: `Committed(D) ⇒ Canonical(D) ∧ IntegrityVerified(D)`
- DEPENDENCIES: REQ-PERSIST-004, REQ-PERSIST-019, REQ-CANON-004
- SECURITY-IMPACT: critical (a committed but non-canonical or unverified artifact would make recovery non-deterministic)
- VERIFICATION-METHOD: commit-then-decode property tests; corrupted-commit rejection tests
- EVIDENCE-STATUS: SPECIFIED
### REQ-RECOV-001
- REQ-ID: REQ-RECOV-001
- CATEGORY: recovery
- SOURCE: Red-on-Rust.md L26122–26140([33]); spec/01 S-19 R-RECOV-01
- NORMATIVE-LEVEL: IS
- STATEMENT: Durable state `D = ⟨S, L, H⟩` — the latest committed snapshot, the durable event log after it, and the durable effect journal.
- PRECONDITIONS: —
- POSTCONDITIONS: —
- INVARIANTS: —
- DEPENDENCIES: REQ-RECOV-002
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: recovery differential
- EVIDENCE-STATUS: SPECIFIED

### REQ-RECOV-002
- REQ-ID: REQ-RECOV-002
- CATEGORY: recovery
- SOURCE: Red-on-Rust.md L26122–26140([33]); L35037–L35038([47] 15B adoption); spec/01 S-19 R-RECOV-01
- NORMATIVE-LEVEL: MUST
- STATEMENT: `Recover(D) = Replay(S, L, H)`.
- PRECONDITIONS: durable state `D`
- POSTCONDITIONS: the recovered state is produced by replaying the log and journal over the snapshot
- INVARIANTS: `Recover(D) = Replay(S, L, H)`
- DEPENDENCIES: REQ-CORE-013, REQ-RECOV-010
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: `Canonical(Recover_P(D)) = Canonical(Recover_R(D))`
- EVIDENCE-STATUS: SPECIFIED

### REQ-RECOV-003
- REQ-ID: REQ-RECOV-003
- CATEGORY: recovery
- SOURCE: Red-on-Rust.md L35161([47] T0); L28482([36]); L26155–26165([33]); spec/01 S-19 R-RECOV-02
- NORMATIVE-LEVEL: MUST
- STATEMENT: Crash point **T0** (before `Prepared`; no durable state): the effect does not exist, there is no budget mutation, and execution resumes normally.
- PRECONDITIONS: crash before the `Prepared` record
- POSTCONDITIONS: as stated
- INVARIANTS: —
- DEPENDENCIES: REQ-RECOV-010
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: crash-injection matrix T0 (M10 gate)
- EVIDENCE-STATUS: SPECIFIED

### REQ-RECOV-004
- REQ-ID: REQ-RECOV-004
- CATEGORY: recovery
- SOURCE: Red-on-Rust.md L35163([47] T1); L38222–38226([54] §12); spec/01 S-19 R-RECOV-02
- NORMATIVE-LEVEL: MUST
- STATEMENT: Crash point **T1** (after `Prepared`; `Prepared` only): the incomplete preparation is discarded and execution resumes normally.
- PRECONDITIONS: crash after `Prepared`, before `Issued`
- POSTCONDITIONS: as stated
- INVARIANTS: `Prepared ∧ ¬Issued ⇒ Discard`
- DEPENDENCIES: REQ-DUR-010
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: crash-injection matrix T1
- EVIDENCE-STATUS: SPECIFIED

### REQ-RECOV-005
- REQ-ID: REQ-RECOV-005
- CATEGORY: recovery
- SOURCE: Red-on-Rust.md L35165([47] T2); L26155–26165([33]); L26592–26598([33]); spec/01 S-19 R-RECOV-02
- NORMATIVE-LEVEL: MUST
- STATEMENT: Crash point **T2** (after `Issued`; `Prepared + Issued`): the effect is `Indeterminate` and requires reconciliation.
- PRECONDITIONS: crash after `Issued`, before host completion
- POSTCONDITIONS: classification is `Indeterminate`
- INVARIANTS: `Issued ∧ ¬Completed ⇒ Indeterminate`
- DEPENDENCIES: REQ-DUR-011, REQ-RECOV-017
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: `RECOVERY-ISSUED-INDETERMINATE`; crash point T2
- EVIDENCE-STATUS: SPECIFIED

### REQ-RECOV-006
- REQ-ID: REQ-RECOV-006
- CATEGORY: recovery
- SOURCE: Red-on-Rust.md L35167([47] T3); spec/01 S-19 R-RECOV-02
- NORMATIVE-LEVEL: MUST
- STATEMENT: Crash point **T3** (host invoked; `Prepared + Issued`): the effect is `Indeterminate` because the host may have executed it.
- PRECONDITIONS: crash during host execution
- POSTCONDITIONS: classification is `Indeterminate`
- INVARIANTS: —
- DEPENDENCIES: REQ-DUR-011, REQ-DUR-012
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: crash point T3
- EVIDENCE-STATUS: SPECIFIED

### REQ-RECOV-007
- REQ-ID: REQ-RECOV-007
- CATEGORY: recovery
- SOURCE: Red-on-Rust.md L35169([47] T4); spec/01 S-19 R-RECOV-02
- NORMATIVE-LEVEL: MUST
- STATEMENT: Crash point **T4** (host completed, completion not durable; `Prepared + Issued`): the effect is `Indeterminate`.
- PRECONDITIONS: crash after host completion but before a durable `Completed`
- POSTCONDITIONS: classification is `Indeterminate`
- INVARIANTS: —
- DEPENDENCIES: REQ-DUR-011
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: crash point T4
- EVIDENCE-STATUS: SPECIFIED

### REQ-RECOV-008
- REQ-ID: REQ-RECOV-008
- CATEGORY: recovery
- SOURCE: Red-on-Rust.md L35171([47] T5); L26155–26165([33]); spec/01 S-19 R-RECOV-02
- NORMATIVE-LEVEL: MUST
- STATEMENT: Crash point **T5** (after `Completed`, durable): the completed effect is reconstructed and the continuation resumes.
- PRECONDITIONS: `Completed` is durable
- POSTCONDITIONS: the continuation resumes with the recorded result
- INVARIANTS: `Completed(E) ⇒ Issued(E)`
- DEPENDENCIES: REQ-EFFECT-034, REQ-EFFECT-035
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: crash point T5
- EVIDENCE-STATUS: SPECIFIED

### REQ-RECOV-009
- REQ-ID: REQ-RECOV-009
- CATEGORY: recovery
- SOURCE: Red-on-Rust.md L35173([47] T6); L28349([36]); spec/01 S-19 R-RECOV-02
- NORMATIVE-LEVEL: MUST
- STATEMENT: Crash point **T6** (after `SnapshotCommit`; snapshot + WAL): recovery uses the snapshot as base and replays the subsequent WAL records.
- PRECONDITIONS: a committed snapshot and later WAL records exist
- POSTCONDITIONS: only post-snapshot records are replayed
- INVARIANTS: —
- DEPENDENCIES: REQ-PERSIST-019, REQ-PERSIST-020
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: crash point T6; `SNAPSHOT-COMMIT-INTEGRITY`
- EVIDENCE-STATUS: SPECIFIED

### REQ-RECOV-010
- REQ-ID: REQ-RECOV-010
- CATEGORY: recovery
- SOURCE: Red-on-Rust.md L35189–35208([47]); L26272–26300([33]); spec/01 S-19 R-RECOV-03
- NORMATIVE-LEVEL: MUST
- STATEMENT: Recovery performs, in order: (1) locate the newest committed snapshot; (2) verify framing/checksum; (3) decode via 15A `CanonicalDecode`; (4) validate recovered `GlobalState` invariants (budget conservation, no duplicate runnable actors); (5) open the WAL and verify framing/checksums; (6) verify sequence continuity and reject gaps; (7) replay records sequentially after the snapshot sequence; (8) reconstruct the effect journal and validate causal chains; (9) classify interrupted effects (`Indeterminate` vs `Completed`); (10) reconstruct the runnable queue; (11) compute the final state digest against the trailing checkpoint; (12) enter `RecoveryComplete` and resume the deterministic scheduler.
- PRECONDITIONS: durable state `D` is available
- POSTCONDITIONS: a `RecoveryComplete` state or an explicit `RecoveryFault`
- INVARIANTS: — (ordered algorithm; kept whole per rule 6)
- DEPENDENCIES: REQ-RECOV-011, REQ-RECOV-016, REQ-RECOV-018; U-02, U-17
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: recovery differential (`Recover_P` vs `Recover_R`)
- EVIDENCE-STATUS: SPECIFIED

### REQ-RECOV-011
- REQ-ID: REQ-RECOV-011
- CATEGORY: recovery
- SOURCE: Red-on-Rust.md L35196–35208([47]); L38254–38272([54] §13); spec/01 S-19 R-RECOV-05
- NORMATIVE-LEVEL: MUST
- STATEMENT: `Invalid(D) ⇒ RecoveryFault`.
- PRECONDITIONS: validation of durable state fails at any recovery step
- POSTCONDITIONS: an explicit `RecoveryFault` is raised; no state is resumed
- INVARIANTS: `Invalid(D) ⇒ RecoveryFault`
- DEPENDENCIES: REQ-CORE-015, REQ-RECOV-012
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: negative corruption tests
- EVIDENCE-STATUS: SPECIFIED

### REQ-RECOV-012
- REQ-ID: REQ-RECOV-012
- CATEGORY: recovery
- SOURCE: Red-on-Rust.md L35196–35208([47]); L38866([54] §28); L34430–L34437([46] strict validation); spec/01 S-19 R-RECOV-05
- NORMATIVE-LEVEL: MUST NOT
- STATEMENT: The recovery engine MUST NEVER silently repair corruption — no dropping duplicate runnable actors, no fixing budget mismatches, no ignoring gaps, checksums, or causality violations.
- PRECONDITIONS: corruption is detected
- POSTCONDITIONS: durable state is left unmodified and the fault is reported
- INVARIANTS: —
- DEPENDENCIES: REQ-CLAIM-010
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: mutations M015, M016; negative recovery tests
- EVIDENCE-STATUS: SPECIFIED

### REQ-RECOV-013
- REQ-ID: REQ-RECOV-013
- CATEGORY: recovery
- SOURCE: Red-on-Rust.md L35210–35215([47]); spec/01 S-19 R-RECOV-06
- NORMATIVE-LEVEL: MUST
- STATEMENT: The three-way accounting `C_available + C_escrowed + C_consumed = C_initial` MUST survive crashes identically.
- PRECONDITIONS: recovery completes
- POSTCONDITIONS: the partition equality holds with the same values as before the crash
- INVARIANTS: `C_available + C_escrowed + C_consumed = C_initial`
- DEPENDENCIES: REQ-BUDGET-022, REQ-DUR-014
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: post-recovery invariant check
- EVIDENCE-STATUS: SPECIFIED

### REQ-RECOV-014
- REQ-ID: REQ-RECOV-014
- CATEGORY: recovery
- SOURCE: Red-on-Rust.md L35189–35195([47]); L38866([54] §28); spec/01 S-19 R-RECOV-04
- NORMATIVE-LEVEL: MUST
- STATEMENT: The recovery engine MUST be an independent implementation from the normal execution path (anti-oracle-collapse).
- PRECONDITIONS: recovery is implemented
- POSTCONDITIONS: two implementations exist for one contract
- INVARIANTS: —
- DEPENDENCIES: REQ-RECOV-015, REQ-SCOPE-011
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: dependency-graph review
- EVIDENCE-STATUS: SPECIFIED

### REQ-RECOV-015
- REQ-ID: REQ-RECOV-015
- CATEGORY: recovery
- SOURCE: Red-on-Rust.md L38866([54] §28); L35189–35195([47]); spec/01 S-19 R-RECOV-04
- NORMATIVE-LEVEL: MUST NOT
- STATEMENT: Production recovery MUST NOT be used as the reference recovery oracle.
- PRECONDITIONS: differential recovery testing
- POSTCONDITIONS: the oracle is the independent implementation
- INVARIANTS: —
- DEPENDENCIES: REQ-CLAIM-011
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: dependency review; recovery differential
- EVIDENCE-STATUS: SPECIFIED

### REQ-RECOV-016
- REQ-ID: REQ-RECOV-016
- CATEGORY: recovery
- SOURCE: Red-on-Rust.md L35111–35144([47]); L26249–26262([33]); spec/01 S-19 R-RECOV-07
- NORMATIVE-LEVEL: MUST
- STATEMENT: `Issued ∧ ¬Completed` effects are handed to the supervisor's reconciliation policy, and the outcomes are recorded durably as `EffectReconciled`.
- PRECONDITIONS: recovery classifies an effect `Indeterminate`
- POSTCONDITIONS: a durable `EffectReconciled` record exists
- INVARIANTS: `Reconciled(E) ⇒ Issued(E)`
- DEPENDENCIES: REQ-DUR-007; U-15 (`ReconciliationOutcome` variants undefined)
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: reconciliation tests
- EVIDENCE-STATUS: SPECIFIED

### REQ-RECOV-017
- REQ-ID: REQ-RECOV-017
- CATEGORY: recovery
- SOURCE: Red-on-Rust.md L26249–26262([33]); L35111–35144([47]); L26592–26598([33]); spec/01 S-19 R-RECOV-07
- NORMATIVE-LEVEL: MUST
- STATEMENT: Reconciliation is the only path by which an `Indeterminate` effect becomes resolved; the system never auto-resolves to "not executed".
- PRECONDITIONS: an effect is `Indeterminate`
- POSTCONDITIONS: resolution occurs only through the reconciliation policy
- INVARIANTS: —
- DEPENDENCIES: REQ-DUR-012, REQ-CORE-014
- SECURITY-IMPACT: critical
- VERIFICATION-METHOD: reconciliation tests; crash matrix classification
- EVIDENCE-STATUS: SPECIFIED

### REQ-RECOV-018
- REQ-ID: REQ-RECOV-018
- CATEGORY: recovery
- SOURCE: Red-on-Rust.md L35193([47] step 4); L35207([47] step 10); spec/01 S-19 R-RECOV-03; spec/06 C-26
- NORMATIVE-LEVEL: AMBIGUOUS
- STATEMENT: Recovery step (4) validates recovered `GlobalState` invariants (budget conservation, no duplicate runnable actors) while step (10) reconstructs the runnable queue from actor states; the snapshot is also said to contain the runnable queue. Which is authoritative when the snapshot's queue and the reconstruction disagree is not stated.
- PRECONDITIONS: recovery steps 4 and 10
- POSTCONDITIONS: — (authority on mismatch undefined)
- INVARIANTS: —
- DEPENDENCIES: U-17, AMB-09
- SECURITY-IMPACT: high (a silently chosen queue could double-schedule an actor — mutation M012's target)
- VERIFICATION-METHOD: UNDEFINED until the precedence rule is frozen (req/04, VU-09)
- EVIDENCE-STATUS: SPECIFIED

### REQ-RECOV-019
- REQ-ID: REQ-RECOV-019
- CATEGORY: recovery
- SOURCE: Red-on-Rust.md L35205([47] step 11); spec/01 S-19 R-RECOV-03
- NORMATIVE-LEVEL: MUST
- STATEMENT: Recovery computes the final state digest and compares it against the trailing checkpoint.
- PRECONDITIONS: replay has completed
- POSTCONDITIONS: a mismatch is a `RecoveryFault`, not a silent continuation
- INVARIANTS: —
- DEPENDENCIES: REQ-RECOV-011, REQ-CANON-031; U-02
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: recovery differential; corrupted-checkpoint tests
- EVIDENCE-STATUS: SPECIFIED

### REQ-RECOV-020
- REQ-ID: REQ-RECOV-020
- CATEGORY: recovery
- SOURCE: Red-on-Rust.md L35207([47] step 12); L34358–34364([46]); spec/01 S-19 R-RECOV-03
- NORMATIVE-LEVEL: MUST
- STATEMENT: Recovery enters `RecoveryComplete` and resumes the deterministic scheduler.
- PRECONDITIONS: all recovery steps succeeded
- POSTCONDITIONS: scheduling resumes under the same deterministic rules
- INVARIANTS: —
- DEPENDENCIES: REQ-ACTOR-010, REQ-CORE-011
- SECURITY-IMPACT: high
- VERIFICATION-METHOD: post-recovery determinism differential
- EVIDENCE-STATUS: SPECIFIED

### REQ-RECOV-021
- REQ-ID: REQ-RECOV-021
- CATEGORY: recovery
- SOURCE: Red-on-Rust.md L34338–34364([46] §15B.11); spec/01 S-19 R-RECOV-03
- NORMATIVE-LEVEL: SHOULD
- STATEMENT: An earlier statement of the recovery procedure lists nineteen ordered steps (locate snapshot; verify framing; verify checksum; decode canonical snapshot; validate recovered `GlobalState`; open WAL; verify record framing; verify per-record checksum; verify WAL sequence continuity; replay records after snapshot sequence; reconstruct effect journal; validate effect causal chains; reconcile interrupted effects; reconstruct runnable queue; validate global invariants; compute state digest; compare against checkpoint/digest where applicable; enter `RecoveryComplete`; resume deterministic scheduler), and states the procedure should be deterministic and independently implemented from normal execution.
- PRECONDITIONS: recovery is specified or implemented
- POSTCONDITIONS: the nineteen-step ordering is accounted for
- INVARIANTS: —
- DEPENDENCIES: REQ-RECOV-010; AMB-27
- SECURITY-IMPACT: medium (the two step lists differ in granularity; see AMB-27)
- VERIFICATION-METHOD: recovery-step conformance review against the frozen 12-step list
- EVIDENCE-STATUS: SPECIFIED

### REQ-RECOV-022
- REQ-ID: REQ-RECOV-022
- CATEGORY: recovery
- SOURCE: Red-on-Rust.md L34801–34812([46]); L35189–35208([47] §15B.7); L28427([36] The Three Central Implications); spec/01 S-19 R-RECOV-01
- NORMATIVE-LEVEL: MUST
- STATEMENT: `CommittedSnapshot + ValidWAL + ValidEffectJournal + ReconciledEffects ⇒ UniqueRecoveredMachineState`.
- PRECONDITIONS: all four inputs are valid and effects are reconciled
- POSTCONDITIONS: recovery yields exactly one machine state
- INVARIANTS: `CommittedSnapshot ∧ ValidWAL ∧ ValidEffectJournal ∧ ReconciledEffects ⇒ UniqueRecoveredMachineState`
- DEPENDENCIES: REQ-RECOV-010, REQ-RECOV-021, REQ-DUR-010
- SECURITY-IMPACT: critical (a non-unique recovered state would break the determinism theorem across crashes)
- VERIFICATION-METHOD: repeated-recovery determinism tests over the crash matrix T0–T6
- EVIDENCE-STATUS: SPECIFIED
