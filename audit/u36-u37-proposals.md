# U-36 and U-37 — proposed resolutions

**STATUS: PROPOSAL. NOT ADOPTED. NOT FROZEN TEXT.**

Neither section below issues an `R-` obligation, changes an obligation status,
or is cited by any register row as authority. Companion to
`audit/u35-definitions-proposal.md`, same rules: if accepted, the accepted part
must be issued as a numbered frozen addendum under `spec/09` process note 1,
and only then do C-100 / C-102 move off `open` (R-SCOPE-03).

Unlike U-35, neither of these hides a prior question. Both are decidable today,
and the work that made them expensive — *enumerating every affected site* — is
done here and mechanically verified.

---

# U-36 — `Lifetime`: wall-clock or logical time?

## The evidence, complete

`Lifetime` is declared three times, identically in type:

| Line | Turn | Declaration |
|---|---|---|
| L3571 | [7] | `pub struct Lifetime { start: u64, end: u64 }` |
| L4959 | [9] | identical |
| L5403 | [9] | identical |

Five `// Unix timestamp` annotations, not four (the U-36 entry said four; it is
corrected in the same pass as this draft):

| Line | Text |
|---|---|
| L3572 | `pub start: u64,  // Unix timestamp` |
| L3573 | `pub end: u64,    // Unix timestamp` |
| L4960 | `pub start: u64,  // Unix timestamp` |
| L4961 | `pub end: u64,    // Unix timestamp` |
| L5404 | `pub start: u64, // Unix timestamp` |

L5405 (`pub end: u64,`) carries **no** annotation — the third declaration is
annotated on `start` only. Plus the prose at L5244.

The consumers:

| Line | Signature |
|---|---|
| L3577 | `pub fn contains(&self, time: u64) -> bool` |
| L4965 | `pub fn contains(&self, time: u64) -> bool` |
| L6489 | `fn contains(&self, t: u64) -> bool; // t ∈ T` |

and the two that decide the question. At L11881–11886:

```rust
pub fn authorizes(auth: &Authority, effect: &Effect, t: LogicalTime) -> bool {
    ...
    && auth.lifetime.contains(t)
}
```

and again at L6558, in a second authorization path:

```rust
&& op_auth.lifetime.contains(logical_time)
```

**A `LogicalTime` is passed, at two independent call sites, to a parameter the
source documents as a Unix timestamp.** The two readings cannot both hold, and the frozen text asserts
both within eight lines.

## Why this is not merely a naming defect

R-CAP-09 prohibits wall-clock time as semantic machine state. Under the Unix
reading, exactly one of two things is true, and both are violations:

1. The machine reads the host clock during authorization — so replaying a
   recorded trace on a later date flips authorization outcomes, and the
   determinism theorem is false on an input that appears nowhere in its
   antecedent (DET-006); or
2. It does not read the clock, and `contains(t: LogicalTime)` compares a
   logical counter against Unix epoch seconds — a comparison that is
   type-correct in Rust (`u64` vs `u64`) and meaningless in the semantics.
   Every capability is then either permanently valid or permanently expired,
   silently, with no diagnostic.

Reading (2) is the more dangerous because it *passes the compiler*. `u64` on
both sides is precisely why this survived to be found by an audit rather than
by a type error.

## Proposed

```rust
pub struct Lifetime {
    pub start: LogicalTime,
    pub end: LogicalTime,
}
impl Lifetime {
    pub fn contains(&self, t: LogicalTime) -> bool { self.start <= t && t < self.end }
}
```

- Half-open `[start, end)`, stated normatively — the frozen bodies at L3577 and
  L4965 should be checked against this before adoption; a closed interval
  changes expiry semantics by one tick and the source does not say which it is.
- The five `// Unix timestamp` annotations and the L5244 prose are recorded as
  **superseded, quoted not deleted** (R-SCOPE-03).
- `Deadline` (T-27) must be retyped in the same addendum or the split simply
  moves; it is the sibling term and U-01 already links them.

**If a wall-clock validity window is genuinely wanted** for some deployment
purpose, then it must be a *separate, explicitly non-semantic* field that
`authorizes` does not read, and R-CAP-09 needs an explicit carve-out saying so.
This proposal recommends against it: nothing in the frozen source uses a
wall-clock lifetime for anything, so the cost is zero and the hazard is real.

---

# U-37 — fixed integer widths (`usize` elimination)

## The evidence, complete

`usize` occurs **102 times**; **49** are in declaration positions. Mechanically
classified:

| Class | Count | Semantic? |
|---|---|---|
| `fn`-signature | 23 | mostly no — local byte offsets |
| struct field | 19 | mixed |
| variant / newtype payload | 7 | **yes** |

The distinction that matters is **does the value cross a semantic or serialized
boundary**, not whether it is spelled `usize`. Three classes:

### (a) Genuinely semantic — must be frozen

| Line | Site | Proposed |
|---|---|---|
| L5391 | `MaxBytes(usize)` | `u64` |
| L5397 | `ResourceLimits.max_bytes: usize` | `u64` |
| L5398 | `ResourceLimits.max_calls: usize` | `u64` |
| L17596–7, L18111–2, L18637–8 | `BeginArgument(usize)` / `EndArgument(usize)` | `u32` |
| L17797–8, L22426–7 | `expected` / `actual` arity | `u32` |
| L1235, L24013, L34500, L36136 | `ReplayHost.cursor` | `u64` |

### (b) The one that is already a contradiction

`max_bytes` and `max_calls` are **`u64` at L3555–3556 and L4943–4944**
(`pub struct Resources`) and **`usize` at L5397–5398**
(`pub struct ResourceLimits`). Same field names, same role, two widths — and
both types are used as `Authority.resources`:

| Field type | Declarations |
|---|---|
| `resources: Resources` | L3595, L3641, L4364, L4983, L5029 |
| `resources: ResourceLimits` | L5373, L5732, L6690 |

So the width of an authorization ceiling depends on which `Authority`
declaration governs — which is itself unresolved (X-87's sibling problem;
`Authority` is 7 declarations in 6 shapes). **U-37 cannot be fully discharged
without that choice**, and this is the one dependency in this document. The
narrow fix is available regardless: whichever `Authority` wins, the ceiling
fields are `u64`, because the source already writes them that way in five of
eight declarations.

### (c) False positives — leave alone

The 23 `fn`-signature hits are overwhelmingly *local* byte counts that never
reach the wire: `decode_payload(...) -> Result<(Self, usize)>` returns bytes
consumed, `read_bytes(&mut self, n: usize)`, `remaining(&self) -> usize`,
`pos: usize` in the read cursor. These are implementation-internal and
platform-width is correct for them.

**The source already knows this.** At L30715, L32139 and L33444:

```rust
fn checked_length(len: usize) -> Result<u32, CanonicalError> {
    u32::try_from(len).map_err(|_| CanonicalError::LengthOverflow)
}
```

That function *is* the boundary discipline this proposal asks to be made
normative: `usize` inside, `u32`/`u64` with a checked conversion at the edge.
The defect is not that `usize` appears; it is that the discipline is applied in
the canonicalization layer and nowhere else.

## Proposed

One normative rule, plus a table:

> No `usize` may appear in a field, variant payload, or trait-method signature
> whose value is (i) compared during authorization, (ii) serialized, or
> (iii) part of `InitialState`. Local offsets and lengths may use `usize`
> provided every conversion to a semantic or serialized value goes through a
> checked narrowing that faults on overflow, as `checked_length` already does.

with widths frozen per the table in (a). This is stricter than "ban `usize`"
and weaker than "rewrite the decoder" — it targets the actual hazard, which is
DET-011: a 32-bit or wasm32 target silently computing different ceilings and
different arity errors than a 64-bit one.

## Scope note

U-37 is filed non-blocking, and that is right for a 64-bit-only milestone. It
becomes **blocking the moment wasm32 is in scope** — L793 contemplates a WASM
sandbox and R-ARCH-05 freezes the target list. The cheap cross-target test in
the audit §6 detects the entire class, but only once an implementation exists.

---

## What neither proposal does

Neither closes its finding. C-100 and C-102 stay `open` until frozen text is
issued. Neither claims replay reproduces the external world. U-36 depends on
U-01 (`Deadline`/`Lifetime` are joint); U-37 depends on the `Authority` shape
question. Both dependencies are stated here rather than discovered later.
