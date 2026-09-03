# M1 Progress — Canonical Serialization (Partial)

## Identity

| Field | Value |
|---|---|
| Branch | `arena/01a06993-red-on-rust` |
| Predecessor | M0 GREEN (`docs/bootstrap/M0-B-VALIDATION.md`) |
| M1 classification (M0-A) | `PARTIALLY IMPLEMENTABLE` |
| Evidence ceiling | `SPECIFIED` (no requirement-status promotion) |
| Canonical registries modified | **NO** |

## Scope executed

Frozen Phase-15A data-domain codec in `ror-core`:

| Item | Location |
|---|---|
| Domain types `Symbol`, `CapRef`, `ActorId`, `EffectId`, `Value` | `crates/ror-core/src/types.rs` |
| Envelope / cursor / traits | `crates/ror-core/src/canonical/codec.rs` |
| Standalone primitive codecs (R-CANON-03/05) | `crates/ror-core/src/canonical/primitives.rs` |
| `Value` encode + data-path decode (R-CANON-04/06/08/12) | `crates/ror-core/src/canonical/value.rs` |
| Data-codec entry + CapRef kernel helpers | `crates/ror-core/src/canonical/data_decode.rs` |
| `CanonicalError` (+ `DuplicateMapKey`, `CapabilityInData`) | `crates/ror-core/src/canonical/error.rs` |
| SHA-256 digests (R-CANON-09), pure Rust | `crates/ror-core/src/digest.rs` |
| Golden vectors (R-CANON-11) | `crates/ror-core/vectors/canonical/` |

## M1 acceptance criteria (executed)

| Criterion | Result |
|---|---|
| Golden vectors pass | **PASS** — `integer_42`, `unit`, `bool_true`, `map_sym_bool`, `capref_5_2` |
| Round-trips pass | **PASS** — encode→decode identity for pure data values |
| Malformed inputs reject | **PASS** — bad version, trailing bytes, LE length permute, invalid discriminants |
| Duplicate keys reject | **PASS** — `CanonicalError::DuplicateMapKey` |
| Canonical bytes deterministic | **PASS** — repeated encode equal; digest stable |
| Capability data-path ban (R-CANON-12) | **PASS** — standalone `0x30` and disc `0x05` → `CapabilityInData` |
| One grammar BE only (R-CANON-13) | **PASS** — LE length permutations rejected |

```text
cargo fmt --check          PASS
cargo check --workspace    PASS
cargo test --workspace     PASS  (18 ror-core tests)
cargo clippy --workspace   PASS  (-D warnings)
```

## Deliberately not implemented (open / out of M1 partial scope)

| Item | Reason |
|---|---|
| Machine-state encodings (`Expr`, `Frame`, `GlobalState`, …) | **U-02 OPEN** |
| Full machine `Value` domain / collision with data domain | **U-09 OPEN** |
| `Op` / `Target` / `Params` / `Effect` body encoding | **U-21 OPEN** |
| Kernel-mediated authority image persistence | later milestone; CapRef *layout* only pinned |
| Marshalling / delegation envelopes (R-MARSHAL-*) | M-later; `contains_capability` data-domain stub only |
| Requirement status promotion in `reg/` / `final/03` | forbidden without evidence-ceiling raise |

## Semantic non-leakage

No CEK, actors, scheduler, capability kernel logic, effects, host execution,
persistence/recovery, agent/planner, or reference evaluator semantics were added.
Only the frozen 15A byte codec and supporting data types landed in `ror-core`.

## Canonical state

No modifications to:

`Red-on-Rust.md`, `spec/`, `req/`, `reg/`, `dep/`, `mod/`, `term/`, `audit/`,
`final/`, `state/`, `scripts/spec/`, `tests/spec/`.

## Decision

```text
M0: GREEN
M1 (partial frozen subset): IMPLEMENTED + TESTED in-tree
M1 (full milestone gate): NOT COMPLETE — open OADs remain
M2: NOT AUTHORIZED until M1 full gate or explicit partial-advance policy
```

```text
EVIDENCE CEILING: SPECIFIED
```

Requirement IDs `R-CANON-01`…`R-CANON-13` remain registry-status `SPECIFIED`.
In-tree tests constitute implementation evidence but do **not** rewrite the
canonical requirement registry.
