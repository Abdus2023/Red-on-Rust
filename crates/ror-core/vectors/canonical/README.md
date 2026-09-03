# Canonical golden vectors (R-CANON-11)

Normative byte fixtures for Phase 15A. Each `*.bin.hex` file is a whitespace-
and-comment-tolerant hex dump of the full canonical envelope.

| File | Semantic value | Notes |
|---|---|---|
| `integer_42.bin.hex` | `Value::Integer(42)` | R-CANON-11 example |
| `capref_5_2.bin.hex` | `CapRef{5,2}` | layout pin; **data path rejects** (R-CANON-12) |
| `map_sym_bool.bin.hex` | `Map{1→false, 2→true}` | Value-envelope form (R-CANON-04) |
| `unit.bin.hex` | `Value::Unit` | |
| `bool_true.bin.hex` | `Value::Bool(true)` | |

Loader and assertions live in `ror-core` tests (`canonical::data_decode` and
`tests` below this crate when present).

Little-endian permutations of every vector MUST be rejected (R-CANON-13).
