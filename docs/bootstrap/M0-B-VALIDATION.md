# M0-B Validation Report

## Identity

| Field | Value |
|---|---|
| Branch | `arena/01a06993-red-on-rust` |
| Bootstrap commit validated | `727a6efbfd10b943eed2c67552294cdafe68ffb8` |
| Bootstrap commit subject | `bootstrap: create M0-B workspace skeleton` |
| Working tree at validation start | clean at `727a6ef` (only this report added afterward) |
| Validation date | `2026-09-03` |
| Evidence ceiling | `SPECIFIED` |
| Requirement promotion | **NONE** |

```text
git rev-parse HEAD  →  727a6efbfd10b943eed2c67552294cdafe68ffb8
git status --short  →  (empty before report commit)
```

---

## Decision

```text
M0-A: GREEN
M0-B structure: GREEN
M0-B validation: GREEN
M0: GREEN
M1: AUTHORIZED
```

All required execution gates passed against the real bootstrap tree. No bootstrap defect was found. No semantic implementation was introduced. Canonical specification/registries were not modified. Requirement statuses remain unchanged at ceiling `SPECIFIED`.

---

## 1. Toolchain (Executed evidence)

Committed declaration (`rust-toolchain.toml`) — **not modified**:

```toml
[toolchain]
channel = "stable"
components = ["rustfmt", "clippy"]
profile = "minimal"
```

| Command | Exit | Output |
|---|---|---|
| `rustup show active-toolchain` | 0 | `ror-stable (overridden by environment variable RUSTUP_TOOLCHAIN)` |
| `rustc --version` | 0 | `rustc 1.88.0 (6b00bc388 2025-06-23)` |
| `cargo --version` | 0 | `cargo 1.88.0 (873a06493 2025-05-10)` |
| `rustup --version` | 0 | `rustup 1.29.0 (28d1352db 2026-03-05)` |

Notes (environment, not product changes):

- Declaration selects the **stable** channel with `rustfmt` and `clippy`, profile `minimal`. No nightly substitution.
- Host could not reach `static.rust-lang.org` (TLS handshake EOF). A **stable 1.88.0** toolchain (rustc, cargo, rust-std, rustfmt, clippy) was installed offline from the published stable component set and registered with rustup as custom toolchain `ror-stable`.
- `RUSTUP_TOOLCHAIN=ror-stable` was used so validation did not mutate `rust-toolchain.toml` and did not switch the product declaration to nightly.
- Exact channel float at bootstrap time is unspecified by the declaration; 1.88.0 is a concrete stable release satisfying the declared channel/components.

---

## 2. `cargo metadata` (Executed evidence)

```text
command: cargo metadata --no-deps --format-version 1
exit:    0
```

### Workspace members (actual)

| # | Package | Manifest |
|---|---|---|
| 1 | `ror-core` | `crates/ror-core/Cargo.toml` |
| 2 | `ror-compiler` | `crates/ror-compiler/Cargo.toml` |
| 3 | `ror-kernel` | `crates/ror-kernel/Cargo.toml` |
| 4 | `ror-runtime` | `crates/ror-runtime/Cargo.toml` |
| 5 | `ror-persistence` | `crates/ror-persistence/Cargo.toml` |
| 6 | `ror-host` | `crates/ror-host/Cargo.toml` |
| 7 | `ror-agent` | `crates/ror-agent/Cargo.toml` |
| 8 | `ror-reference` | `crates/ror-reference/Cargo.toml` |
| 9 | `ror-differential` | `crates/ror-differential/Cargo.toml` |
| 10 | `ror-testkit` | `crates/ror-testkit/Cargo.toml` |

Metadata gate: **PASS** (10/10 expected members present).

---

## 3. Dependency gate (Executed metadata + canonical authority)

### Convention (authoritative)

From `dep/10-graph.json`:

> `A -> B` means **B depends on A** (provider → consumer).

### Actual Cargo crate-to-crate edges

Resolved from `cargo metadata --no-deps` (workspace package path dependencies only). Listed as **provider → consumer**:

| # | Actual edge | Canonical classification |
|---|---|---|
| 1 | `ror-core → ror-compiler` | REQUIRED/ALLOWED — `TYPE_DEPENDENCY` |
| 2 | `ror-core → ror-kernel` | REQUIRED/ALLOWED — `TYPE_DEPENDENCY` |
| 3 | `ror-core → ror-runtime` | REQUIRED/ALLOWED — `TYPE_DEPENDENCY` |
| 4 | `ror-kernel → ror-runtime` | REQUIRED/ALLOWED — `SECURITY_DEPENDENCY` |
| 5 | `ror-core → ror-persistence` | REQUIRED/ALLOWED — `TYPE_DEPENDENCY`, `SERIALIZATION_DEPENDENCY` |
| 6 | `ror-persistence → ror-runtime` | REQUIRED/ALLOWED — `PERSISTENCE_DEPENDENCY` |
| 7 | `ror-core → ror-host` | REQUIRED/ALLOWED — `TYPE_DEPENDENCY` |
| 8 | `ror-runtime → ror-host` | REQUIRED/ALLOWED — `RUNTIME_DEPENDENCY` |
| 9 | `ror-core → ror-agent` | REQUIRED/ALLOWED — `TYPE_DEPENDENCY` |
| 10 | `ror-compiler → ror-agent` | REQUIRED/ALLOWED — `RUNTIME_DEPENDENCY` |
| 11 | `ror-runtime → ror-agent` | REQUIRED/ALLOWED — `RUNTIME_DEPENDENCY` |
| 12 | `ror-persistence → ror-agent` | REQUIRED/ALLOWED — `PERSISTENCE_DEPENDENCY` |
| 13 | `ror-core → ror-testkit` | REQUIRED/ALLOWED — `TYPE_DEPENDENCY` |
| 14 | `ror-reference → ror-differential` | REQUIRED/ALLOWED — `VERIFICATION_DEPENDENCY` |
| 15 | `ror-runtime → ror-differential` | REQUIRED/ALLOWED — `VERIFICATION_DEPENDENCY` |
| 16 | `ror-testkit → ror-differential` | REQUIRED/ALLOWED — `VERIFICATION_DEPENDENCY` |

| Metric | Count |
|---|---|
| Actual workspace edges | 16 |
| REQUIRED/ALLOWED | 16 |
| FORBIDDEN | **0** |
| UNCLASSIFIED | **0** |
| Missing implementable canonical edges | **0** |

Authorities consulted: `dep/10-graph.json`, `mod/18-ownership-matrix.md`.

Dependency gate: **PASS**.

---

## 4. Reference independence (Executed metadata)

| Check | Result |
|---|---|
| `ror-reference` path/workspace deps | **none** |
| `ror-reference` → `{ror-runtime,ror-kernel,ror-persistence,ror-host,ror-agent}` | **absent** |
| Production crates → `ror-reference` | **none** |
| `ror-differential` → `ror-reference` | present — classified `VERIFICATION_DEPENDENCY` (allowed verification edge) |

Reference independence gate: **PASS**.

---

## 5. Unsafe gate

### Static evidence — crate roots

Every bootstrap crate root contains `#![forbid(unsafe_code)]`:

| Crate root | `#![forbid(unsafe_code)]` |
|---|---|
| `crates/ror-core/src/lib.rs` | present |
| `crates/ror-compiler/src/lib.rs` | present |
| `crates/ror-kernel/src/lib.rs` | present |
| `crates/ror-runtime/src/lib.rs` | present |
| `crates/ror-persistence/src/lib.rs` | present |
| `crates/ror-host/src/lib.rs` | present |
| `crates/ror-agent/src/lib.rs` | present |
| `crates/ror-reference/src/lib.rs` | present |
| `crates/ror-differential/src/lib.rs` | present |
| `crates/ror-testkit/src/lib.rs` | present |

### Static evidence — repository `unsafe` scan

Workspace search over `*.rs` (excluding `target/`) for `\bunsafe\b`: **no matches** outside the `forbid(unsafe_code)` attributes themselves (attribute tokens contain the word; no `unsafe` blocks, fns, traits, or impls exist).

Unsafe gate: **PASS**.

---

## 6. Format / compile / test / clippy (Executed evidence)

| Gate | Command | Exit | Result |
|---|---|---|---|
| format | `cargo fmt --check` | **0** | PASS (no output; tree formatted) |
| check | `cargo check --workspace` | **0** | PASS — all 10 crates checked |
| test | `cargo test --workspace` | **0** | PASS — 0 unit tests / 0 doc tests per crate (skeleton; none fabricated) |
| clippy | `cargo clippy --workspace` | **0** | PASS — all 10 crates; no lint findings |

### `cargo check --workspace` concise output

```text
    Checking ror-core v0.1.0
    Checking ror-reference v0.1.0
    Checking ror-persistence v0.1.0
    Checking ror-kernel v0.1.0
    Checking ror-testkit v0.1.0
    Checking ror-runtime v0.1.0
    Checking ror-compiler v0.1.0
    Checking ror-host v0.1.0
    Checking ror-differential v0.1.0
    Checking ror-agent v0.1.0
    Finished `dev` profile [unoptimized + debuginfo] target(s)
```

### `cargo test --workspace` concise output

```text
running 0 tests
test result: ok. 0 passed; 0 failed; 0 ignored; 0 measured
(×10 lib targets + ×10 doc-test targets)
Finished `test` profile — exit 0
```

### `cargo clippy --workspace` concise output

```text
    Checking ror-core … ror-agent (10 crates)
    Finished `dev` profile — exit 0
```

No lint configuration was weakened.

---

## 7. Semantic leakage (Static evidence — M0-B additions only)

M0-B commit file set (`727a6ef`):

- `Cargo.toml` (workspace members only)
- `rust-toolchain.toml`
- ten `crates/*/Cargo.toml` + ten `crates/*/src/lib.rs`

Each `lib.rs` is documentation-only skeleton text plus `#![forbid(unsafe_code)]`. No executable bodies implement:

| Concern | Present in M0-B code? |
|---|---|
| CEK | no |
| compiler semantics | no |
| actors | no |
| scheduler | no |
| capability authority | no |
| effects | no |
| host execution | no |
| persistence / recovery | no |
| canonical serialization | no |
| agent/planner semantics | no |
| reference evaluator | no |
| differential evaluator | no |

Semantic leakage: **NONE**.

---

## 8. Canonical state preservation (Static evidence)

Diff of bootstrap commit `727a6ef` against its parent for canonical paths:

```text
Red-on-Rust.md   — unchanged
spec/            — unchanged
req/             — unchanged
reg/             — unchanged
dep/             — unchanged
mod/             — unchanged
term/            — unchanged
audit/           — unchanged
final/           — unchanged
state/           — unchanged
scripts/spec/    — unchanged
tests/spec/      — unchanged
```

This validation operation:

- did **not** rerun S0–S7
- did **not** modify requirement statuses
- did **not** resolve OADs
- added only this report under `docs/bootstrap/`

Canonical state: **PRESERVED**.

---

## 9. Requirement statuses

| Item | Status |
|---|---|
| Highest requirement status | `SPECIFIED` |
| Promotions this validation | **NONE** |
| Evidence ceiling | `SPECIFIED` |

Execution of empty-skeleton cargo gates does not raise the evidence ceiling above `SPECIFIED`.

---

## 10. Gate conjunction

| Gate | Status |
|---|---|
| `cargo metadata` | **PASS** (exit 0) |
| `cargo fmt --check` | **PASS** (exit 0) |
| `cargo check --workspace` | **PASS** (exit 0) |
| `cargo test --workspace` | **PASS** (exit 0) |
| `cargo clippy --workspace` | **PASS** (exit 0) |
| dependency gate | **PASS** (FORBIDDEN=0, UNCLASSIFIED=0) |
| reference independence | **PASS** |
| unsafe gate | **PASS** |
| semantic leakage | **NONE** |
| canonical state | **PRESERVED** |
| requirement statuses | **UNCHANGED** |

---

## 11. Final status board

```text
M0-A: GREEN
M0-B structure: GREEN
M0-B validation: GREEN
M0: GREEN
M1: AUTHORIZED
```

```text
EVIDENCE CEILING: SPECIFIED
```

No M1 implementation work is begun by this commit. This commit contains only the durable validation report.
