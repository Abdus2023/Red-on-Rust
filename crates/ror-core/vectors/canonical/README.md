# Canonical golden vectors (R-CANON-11)

Normative / derived byte fixtures for Phase 15A. Each `*.bin.hex` file is a
whitespace- and comment-tolerant hex dump of a full canonical envelope.

## Provenance (independence)

| File | Semantic value | Provenance class | Source of bytes |
|---|---|---|---|
| `integer_42.bin.hex` | `Value::Integer(42)` | **INDEPENDENT** — R-CANON-11 normative example | `final/01` / `spec/01` S-17 R-CANON-11 text: `01 00 00 00 00 09 02 00 00 00 00 00 00 00 2A` |
| `capref_5_2.bin.hex` | `CapRef{5,2}` | **INDEPENDENT** — R-CANON-11 normative example | same: `01 30 00 00 00 08 00 00 00 05 00 00 00 02` (data path MUST reject; R-CANON-12) |
| `unit.bin.hex` | `Value::Unit` | **DERIVED** from frozen grammar | Independently computed from R-CANON-02/04/07 (`disc 0x00`); **not** copied from the Rust encoder |
| `bool_true.bin.hex` | `Value::Bool(true)` | **DERIVED** from frozen grammar | Independently computed (`disc 0x01`, payload `0x01`) |
| `map_sym_bool.bin.hex` | `Map{Symbol(1)→false, Symbol(2)→true}` | **DERIVED** from frozen grammar | Independently computed as a **Value envelope** (R-CANON-04 complete-envelope rule). The narrative sketch’s standalone `tag=0x07 length=0x28` form is **non-normative** (0x07 ∉ R-CANON-03 standalone set) |

**VECTOR EVIDENCE:**

- R-CANON-11 examples (`integer_42`, `capref_5_2`): **INDEPENDENT** of the implementation under test.
- Additional fixtures (`unit`, `bool_true`, `map_sym_bool`): **DERIVED** from the frozen grammar by an external (non-Rust) derivation; cross-checked byte-exact against that derivation. They are **not** sole-sourced from `encode_canonical` output, but they are also **not** quoted verbatim in R-CANON-11 — treat as **NON-INDEPENDENT of the grammar reading** if that reading is later revised.

Loader and assertions: `ror-core` unit tests (`canonical::data_decode`, `canonical::vectors_test`).

Little-endian permutations of every vector MUST be rejected (R-CANON-13).
