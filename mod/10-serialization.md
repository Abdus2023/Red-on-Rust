# MOD-10 — SERIALIZATION: Canonical serialization (15A)

> Owns the bytes: the single canonical, implementation-independent byte format that
> defines semantic identity for everything the machine persists, digests, or
> transports.

## SECTION-ID

`MOD-10` (domain `SERIALIZATION`). Owner module file for the `CANON` obligation area.

## TITLE

Canonical serialization — universal envelope, frozen type tags and discriminants,
strict decoding under hostile input, digest discipline, injectivity claim, and the
golden vectors that pin the format byte-for-byte.

## PURPOSE

Make *identity* a pure function of bytes. `Canonical(x) = Canonical(y)` must decide
semantic sameness for values, effects, and durable records without dependence on Rust
layout, allocator behavior, pointer addresses, or platform representation — because
digests (MOD-08/09/11), recovery determinism (MOD-12), and differential comparison
(MOD-15) are all defined over these bytes.

## NORMATIVE-CONTENT

Normative text home: `spec/01` S-17; atomic renderings
`req/01-registry-part5-persistence.md` (CANON block). This module owns (frozen at
byte level, Phase 15A incl. the duplicate-key patch — C-41):

- **Independence** (R-CANON-01): the format is explicit and independent of any
  serializer; `bincode` may implement but must not define it; canonical encoding
  defines semantic identity.
- **Universal envelope** (R-CANON-02): `version: u8 (0x01) + type_tag: u8 +
  payload_length: u32 BE (checked) + payload`.
- **Frozen tags** (R-CANON-03): standalone envelopes — `Value 0x00`, `Symbol 0x20`,
  `CapRef 0x30`, `ActorId 0x40`, `EffectId 0x41`. (The "revised grammar §1.3"
  primitive tags 0x10/0x11/0x13 are **stale** — C-02; bool/integer/string exist only
  as `Value` discriminants.)
- **Value encoding** (R-CANON-04): envelope tag `0x00`, payload = discriminant u8 +
  variant payload; discriminants `Unit 0x00 … Map 0x07`; **nested values are complete
  canonical envelopes**, not stripped payloads.
- **Primitive payloads** (R-CANON-05): `Symbol` 4B BE; `CapRef` `[index u32 BE][gen
  u32 BE]`; `ActorId`/`EffectId` 8B u64 BE.
- **Collections** (R-CANON-06): count-prefixed; map entries ordered by the semantic
  `Ord` on keys; decoding rejects duplicate keys (`DuplicateMapKey`) to preserve
  injectivity.
- **Strict decoder contract** (R-CANON-07): enforced in order — version, expected
  tag, exact length, payload well-formedness, trailing-byte rejection; explicit stable
  discriminants; explicit `CanonicalError` set (`InvalidVersion, InvalidTypeTag,
  LengthMismatch, LengthOverflow, InvalidUtf8, UnexpectedEof, TrailingBytes,
  InvalidDiscriminant, InvalidBoolValue, DuplicateMapKey`).
- **Hostile-input discipline** (R-CANON-08): all length arithmetic checked;
  `u32::MAX` overflow ⇒ `LengthOverflow`; encoded counts never authorize
  preallocation (grow from `Vec::new()`); bounded nested cursors; fallible envelope
  construction (no panics).
- **Digest discipline** (R-CANON-09): `StateDigest = SHA-256(canonical_bytes)`;
  `EffectDigest = SHA-256(canonical_bytes(effect))`; `Canonical(x) = Canonical(y) ⇒
  Digest(x) = Digest(y)` mechanically; the converse only under collision resistance —
  compare bytes directly when both states are available (frozen correction C-13).
- **Injectivity, scoped** (R-CANON-10): injectivity is a structural specification
  property with machine-checked *evidence* scoped to the generated distribution —
  not a proof claim about arbitrary Rust programs ("surjectivity" wording is a
  superseded misnomer — C-12).
- **Golden vectors** (R-CANON-11): normative test fixtures (e.g. `Integer(42)` ⇒
  `01 00 00 00 00 09 02 00 … 2A`; `CapRef{5,2}` ⇒ `01 30 00 00 00 08 …`),
  byte-exact, regenerated and frozen.

Crate contract (mirrored by pointer): canonical traits + data-domain encodings in
`ror-core`; fixtures in `vectors/canonical` (R-REPO-02).

## NON-NORMATIVE-CONTENT

- Golden vectors are fixtures that *pin* the format, not additional behavioral rules
  (R-CANON-11 wording).
- Stale "revised 15A grammar" §1.3 tag table (C-02) — an implementer reading only it
  would build a non-conforming decoder; recorded here deliberately.
- The 625-line frozen Rust implementation block (L30647, corrected L33290) is
  specification text: conformance = byte-exact reproduction of the vectors, not
  copying the sketch.
- The `CapRef "never serialized directly"` comment (early design) versus the frozen
  0x30 tag is an open reconciliation (C-14 → U-02): the intended reading (delegation/
  persistence only, never ordinary marshalling) is **not** yet frozen text.

## INPUTS

- Domain values to encode: machine/canonical `Value`, `Symbol`, `CapRef`,
  `ActorId`, `EffectId` (MOD-01); marshalled pure values (MOD-06); effect
  descriptors for digests (MOD-08).
- Machine-state structures requiring encoding for snapshots — **encodings not yet
  frozen** (U-02: `Expr`, `Frame`, `Environment`, `Constraint`, `Authority`,
  `Budget`, `Mailbox`, `SchedulerState`, `GlobalState`). This is the largest open gap
  in the specification.

## OUTPUTS

- Canonical bytes; `EffectDigest`/`StateDigest` values; explicit `CanonicalError`
  rejection outcomes.
- The identity function consumed by MOD-08 (effect identity), MOD-09 (replay
  validation), MOD-11 (checksums, record payloads, snapshot digest), MOD-12
  (recovery decode), MOD-15 (digest comparison in observations).

## DEPENDENCIES

- Module dependencies: MOD-01 (data types).
- Consumers: MOD-06 (marshalling uses this format, R-MARSHAL-03/04), MOD-08
  (EffectDigest), MOD-09, MOD-11 (15B payloads are strictly 15A bytes, R-PERSIST-01/
  02), MOD-12 (15A decode at recovery step 3), MOD-15 (observation digests).
- Crate edge: `ror-core` internal; fixtures under `vectors/`.
- Blocking open items: **U-02** (machine-state encodings; AMB-02/07/28),
  **U-09** (two `Value` domains; AMB-06/21), **U-21** (`Op`/`Target`/`Params`
  encodings feed `EffectDigest`).

## INVARIANTS

- Envelope grammar as frozen; nested values are complete envelopes (R-CANON-02/04).
- Strict decoding: the five ordered checks; trailing bytes rejected; duplicate map
  keys rejected; explicit discriminant table (R-CANON-06/07).
- No attacker-controlled preallocation; checked length arithmetic; bounded cursors
  (R-CANON-08).
- `Canonical(x) = Canonical(y) ⇒ Digest(x) = Digest(y)`; converse only under
  collision resistance (R-CANON-09).
- Injectivity as structural property + scoped evidence claim (R-CANON-10).
- Canonical bytes are deterministic: same semantic value ⇒ same bytes, everywhere,
  always (R-CANON-01/11; feeds the determinism theorem MOD-07).

## REQUIREMENTS

Canonical text: `spec/01` S-17; addenda II, IV. All 13 obligations `SPECIFIED`.

| ID | Obligation (short) | Provenance (`Red-on-Rust.md`) | Verification |
|---|---|---|---|
| R-CANON-01 | Serialization independent of Rust layout/serializers | L28185–28228, L28453–28465 | format review |
| R-CANON-02 | Universal envelope (version/tag/len/payload) | L30532–30543, L33290–33347 | golden vectors |
| R-CANON-03 | Frozen standalone type tags (0x00, 0x20, 0x30, 0x40, 0x41) | L33087–33154 | golden vectors; C-02 stale-tags note |
| R-CANON-04 | Value discriminants + nested-complete-envelope rule | L30544–30552, L33155–33265 | golden vectors, round-trip |
| R-CANON-05 | Primitive payloads (Symbol/CapRef/ActorId/EffectId) | L33087–33154 | golden vectors |
| R-CANON-06 | Collections: count-prefixed; semantic key order; duplicates rejected | L30566–30573, L34987–35024, L38138–38183 | M014, duplicate-key regression (ROR-011) |
| R-CANON-07 | Strict decoder contract (5 checks; explicit discriminants; CanonicalError set) | L30575–30586, L32948–33049 | malformed-input suite (ROR-010) |
| R-CANON-08 | Checked arithmetic; no attacker preallocation; bounded cursors; fallible envelope | L30574–30578, L32948–33265 | hostile-input property tests |
| R-CANON-09 | Digest rules + when-to-compare-bytes rule | L28185–28228, L30588–30590 | digest property tests |
| R-CANON-10 | Injectivity: structural property + scoped evidence claim | L30592–30598, L35068 | round-trip + differential |
| R-CANON-11 | Golden vectors as normative fixtures | L30599–30646, L31948–32010, L33266–33286 | M1 acceptance |
| R-CANON-12 | Data decoder rejects capability payloads: 0x05 and standalone 0x30 yield CanonicalError::CapabilityInData; only the kernel-mediated codec path produces or consumes capability payloads; unmarshal runs contains_capability — symmetric boundary (C-14/U-02 security direction; C-78 resolved) | addendum II (SEC-003) | M022, negative golden vectors |
| R-CANON-13 | One canonical grammar: 15A BE envelope sole; LE revised grammar superseded in-source; single TAG_* namespace (X-50/X-54 resolved); all digests defined over 15A; bidirectional byte-exact golden vectors; LE variants rejected (C-92 resolved; M031) | addendum IV (SEC-017) | M031, bidirectional golden vectors |

Atomic registry records under this module: REQ-CANON-001…037. **13 obligations / 37 records.**

## SECURITY-BOUNDARY

The decoder is a front-line hostile-input surface (encoded counts, nested payloads,
trailing garbage are attacker-controlled in replay/fuzz contexts) — hence organic
growth, bounded cursors, checked arithmetic, and exact length. Equally: the format
*is* the machine's notion of identity; a non-injective or platform-dependent encoding
would silently break digests, journal causality, replay validation, and cross
implementation comparison.

## VERIFICATION-OBLIGATIONS

- Golden vectors byte-exactness (R-CANON-11); round-trip `decode(encode(x)) = x` +
  injectivity evidence over the generated distribution (R-CANON-10); malformed-input
  suite (ROR-010); duplicate-map-key regression (ROR-011 / M014).
- Mutation: M014 (accept duplicate canonical map key).
- Negative/structure tests for all `CanonicalError` classes (R-CANON-07).
- Milestone gate: M1 (golden vectors pass; round-trips pass; malformed reject;
  duplicate keys reject; bytes deterministic) — the first semantic milestone.
- 15C.36 canonical boundary differential (REQ-TEST-046, MOD-14-side): the harness may
  treat canonical bytes as opaque inputs/outputs (independence rule).

## SOURCE-PROVENANCE

- Final frozen 15A: [45] (L32936–33707); revised grammar + regenerated vectors
  [39]/[40] (L29451–31298); duplicate-key patch [46] (L34987–35024, part of the
  freeze per C-41); earlier drafts [36]/[38] superseded (C-02/C-12 trail); master
  prompt §11 (L38138–38183).
- Canonical set: `spec/02` S-17; `req/01-registry-part5-persistence.md` (CANON block).

## CROSS-REFERENCES

Owned here, binding elsewhere:

- R-CANON-01 → MOD-11 (no secondary serialization: 15B payloads are 15A bytes,
  R-PERSIST-01), MOD-06 (marshalling transport).
- R-CANON-04/05 → MOD-06 (marshal round-trip domain), MOD-01 (machine-vs-canonical
  `Value` collision — U-09 belongs to MOD-01 with this module affected).
- R-CANON-09 → MOD-08 (`EffectDigest`), MOD-11 (checksums, `state_digest`), MOD-09
  (replay validation), MOD-12 (trailing-checkpoint comparison step 11).
- R-CANON-10 → MOD-15 (evidence gathered over the generated distribution), MOD-17
  (claim discipline — injectivity is never claimed as a proof).

Owned elsewhere, binding SERIALIZATION: R-MARSHAL-03/04 (MOD-06 — marshalling is a
*client* of this codec; the round-trip law's scope is open, AMB-06); R-PERSIST-02
(MOD-11 — the WAL frame's payload layer must be exactly this format); R-DUR-02
(MOD-11 — journal record payloads); R-RECOV-03 step 3 (MOD-12 decodes via this
module). Open items: U-02 (this module, blocking M7), U-09, U-21.
