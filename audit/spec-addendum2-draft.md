# Addendum II — HIGH-findings freeze (SEC-003 / SEC-004 / SEC-005 / SEC-016 / SEC-018)

**Status: APPLIED** via `audit/spec_addendum2.py --apply` (adoption commit on
`arena/01a063c4-red-on-rust`; post-apply verification: 157 obligations /
157 matrix rows / 148 records, `spec/_check.py` D1=0 exit 0 with only the
pre-existing adjudicated warnings, `req/_validate.py` 0 errors after its
explicit register expectations were recorded (76→81 C-rows, incl. the
retroactive C-77 from addendum I; post-audit addenda exempt from req/-citation
coverage by the records scope note), index rebuilt at 157/80/25/19). This file
is retained as the review record of exactly what was adopted and why; rollback
is `git revert` of the adoption commit. The exact edit set lives in
`audit/spec_addendum2.py` (this draft was generated from its constants, so the
two cannot drift).

## 1. What this freezes (audit report §6 item 3)

The five HIGH findings are specification-level absences or ill-formed
contracts on the authority boundary. Five additive obligations, four
registered-and-resolved conflicts, four registered mutations, and one
conformance tag freeze the fixes:

| Addendum | Freezes | Extends / resolves |
|---|---|---|
| `R-CORE-11` | SEC-016: one canonical signature per I2 predicate — `ValidatedRequest(E)` request-time (subsuming `ValidatedPlan`), `Authorized(holder, c, E, t)` with possession as a conjunct; the other five `Authorized` signatures superseded | extends R-CORE-02/R-KERN-04; resolves C-80, term/ X-01/X-04/X-05 (normative layer) |
| `R-CANON-12` | SEC-003: the data decoder rejects capability payloads (`0x05`, standalone `0x30` ⇒ `CanonicalError::CapabilityInData`); only the kernel-mediated codec path produces/consumes capability payloads; `unmarshal` runs `contains_capability` (symmetric boundary) | extends R-CANON-11/R-MARSHAL-03; resolves C-14/U-02 security direction, C-78 |
| `R-PERSIST-07` | SEC-004: durable authority lattice — snapshot carries the authority image (AuthorityNodes, revocation_set, generations); WAL event kinds Granted/Derived/Revoked; recovery reconstructs, replays, faults on dangling/generation-mismatched CapRefs; revocation monotonic across crashes | extends R-PERSIST-04/R-CAP-07/R-CORE-09; tag RECOVERY-REVOCATION-DURABLE |
| `R-MARSHAL-05` | SEC-005: delegation constructible — `Expr::Delegate` → `kernel.derive` → kernel-constructed envelope (never a plain `Value` variant); receive-side revalidation (liveness, lineage, target, generation) before registration, faults leave the recipient CapabilityContext byte-identical; `MarshalledValue` = checked bytes; `MarshalFault` unified | extends R-MARSHAL-02/04; resolves C-79, term/ X-65 (normative layer) |
| `R-MARSHAL-06` | SEC-018: `contains_capability` a frozen total predicate — closed traversal domain including `FunctionValue.env` recursively; sole exclusion kernel-sealed envelopes; invariant stated over reachability | extends R-CORE-07/R-MARSHAL-01; resolves C-81 |
| `C-78…C-81` (spec/06) | the security consequences of C-14/U-02, X-65, X-01/X-05, and the phantom predicate — registered (grades elevated) and resolved-by-addendum | new rows after C-77 |
| `M022/M023/M024/M032` (spec/08) | mutations that must be killed: unmarshal accepts capability payload; recovery resurrects revoked capability; registration without kernel revalidation; predicate skips closure environments | registry M001–M021 → M001–M024 + M032 |
| `RECOVERY-REVOCATION-DURABLE` (spec/08) | conformance tag: T0–T6 with pre-crash revocation; revoked stays revoked | tag set 18 → 19 |

`term/` is intentionally untouched: `term/02` is a generated, source-validated
register (`term/_terms.py` → `term/_dict.py`, re-grepped against
`Red-on-Rust.md` by `term/_check.py`). The normative resolutions are recorded
in R-CORE-11 / R-MARSHAL-05 / R-MARSHAL-06, which the term/ pipeline can cite
at its next regeneration.

## 2. Exact normative texts (spec/01 insertions)

**R-CORE-11 (I2 predicate signatures, canonical form — frozen addendum).** The central theorem's predicates each have ONE canonical signature; all other frozen signatures are SUPERSEDED (quoted, not deleted). First conjunct: `ValidatedRequest(E)` — request-time validation inside the 16 gates — with the subsumption `ValidatedRequest(E) ⇒ ValidatedPlan(plan(E))`; the `ValidatedPlan` compiler-struct homonym (X-01) is disambiguated by qualification — `ValidatedPlan_pred` vs `ValidatedPlan_struct` — adopted repository-wide. Authorization: `Authorized(holder, c, E, t) ⇔ c ∈ κ_holder ∧ Valid(c, t) ∧ Authorized(κ_holder(c), E, t)` — holder first, possession a conjunct (formalizing R-KERN-04); the authority-first reading `Authorized(A, E, t)` is SUPERSEDED (quoted, not deleted). The 7-conjunct chain (R-CORE-02) is stated once, over these exact signatures; differential adjudication (R-TEST-09) MUST adjudicate against this form — weaker plan-time-only or authority-first readings MUST NOT satisfy the chain. *(Frozen addendum — post-audit remediation SEC-016; additive per R-SCOPE-03; extends R-CORE-02/R-KERN-04; resolves C-80 and, at the normative layer, term/ X-01/X-04/X-05; no source transcription.)*

**R-CANON-12 (decode-side authority minting forbidden — frozen addendum).** The data codec — the decoder for messages, receipt results, plan literals, and mailbox/snapshot value payloads — MUST reject capability payloads on decode: discriminant `0x05` (`TAG_CAPABILITY`) and standalone `0x30` (`CapRef::TYPE_TAG`) MUST yield `CanonicalError::CapabilityInData`, not a `Value::Capability`. Only the kernel-mediated codec path — persistence of kernel authority state and kernel-sealed delegation envelopes (R-MARSHAL-05) — may produce or consume capability payloads. `unmarshal` MUST run `contains_capability` (R-MARSHAL-06) over the decoded value regardless of provenance, making the marshalling boundary symmetric with `marshal`. Property: for all bytes `b`, `contains_capability(unmarshal_data(b)) = false ∨ unmarshal_data(b) = Err`. Resolves C-14/U-02 in the direction of the design rule (a serialized capability must go through explicit delegation); negative golden vectors (capability bytes, nested-at-depth, standalone envelope) are normative fixtures. *(Frozen addendum — post-audit remediation SEC-003; additive per R-SCOPE-03; extends R-CANON-11/R-MARSHAL-03; resolves C-78; no source transcription.)*

**R-PERSIST-07 (durable authority lattice — frozen addendum).** The kernel authority image — `AuthorityNode` set with parent links, the `revocation_set`, and generation counters — MUST be durable: snapshots MUST contain it (the invariant is frozen here; byte encoding remains U-02 scope), and the WAL MUST carry `CapabilityGranted`, `CapabilityDerived`, and `CapabilityRevoked` event kinds (freezing the event set in the security direction). Recovery MUST reconstruct the kernel arena, replay capability events after the snapshot sequence, and reject with `RecoveryFault` — never silently repair (R-RECOV-05, R-CORE-10) — any CapRef (in contexts, heaps, frames, mailboxes) that does not resolve with matching generation. Post-recovery, every actor capability MUST be revalidated: `∀ a, ∀ c ∈ caps(a): Valid(c, t_recovered)`; revocation MUST be monotonic across crashes — a revoked capability MUST NOT become valid again without a new explicit grant. `Recover(D) ≡ PreCrashMachineState` includes the authority lattice. *(Frozen addendum — post-audit remediation SEC-004; additive per R-SCOPE-03; extends R-PERSIST-04/R-CAP-07/R-CORE-09; tag `RECOVERY-REVOCATION-DURABLE`; no source transcription.)*

**R-MARSHAL-05 (delegation surface constructible and revalidated — frozen addendum).** The sanctioned authority-transfer channel MUST be constructible as frozen: `Expr::Delegate { capability, constraint }` evaluates by calling `kernel.derive` with the declared constraint and produces a kernel-constructed delegation envelope — NOT a plain `Value` variant; `Value::DelegatedCapability` as a data variant is forbidden. Envelope admission at `Receive`: `register(envelope, recipient)` MUST be preceded by kernel revalidation — liveness, lineage (`DelegatedAuthority ≼ ParentAuthority`), target binding, and generation — against an existing kernel derivation record `d` with `envelope.cap = d.child ∧ d.parent ∈ sender.context`; any failure MUST fault with the recipient's `CapabilityContext` byte-identical (no partial registration). `MarshalledValue` is the checked-bytes form (R-MARSHAL-03): mailbox bytes MUST NOT exist as a `Value`, snapshots storing mailboxes store the checked form, and the private-constructor-wrapper reading is SUPERSEDED (quoted, not deleted). `MarshalFault` has ONE unified closed variant set. *(Frozen addendum — post-audit remediation SEC-005; additive per R-SCOPE-03; extends R-MARSHAL-02/R-MARSHAL-04; resolves C-79 and, at the normative layer, term/ X-65; no source transcription.)*

**R-MARSHAL-06 (contains_capability is a frozen total predicate — frozen addendum).** `contains_capability(v)` MUST be a total predicate with an explicitly closed traversal domain: it MUST descend recursively, at unbounded structural depth, into `List`, `Map` (keys and values), `Tuple` elements, and — the load-bearing case — `FunctionValue.env` (captured closure environments, recursively: environments bind names to `Value`, and a closure whose environment binds a capability carries authority). Kernel-sealed delegation envelopes (R-MARSHAL-05) are the sole exclusion, and then only sealed by the kernel. `Bytes` are data — the decode-side rule (R-CANON-12) governs their rehydration. The boundary invariant is stated over reachability, not one value domain: `marshal(v) = Ok ⇒ ¬∃c. Reachable(env_of(v), c)` outside kernel-sealed envelopes. Closure-carrying values whose environments bind capabilities MUST fault at `marshal`, never round-trip. *(Frozen addendum — post-audit remediation SEC-018; additive per R-SCOPE-03; extends R-CORE-07/R-MARSHAL-01; resolves C-81; no source transcription.)*

(Each ends with an explicit *frozen addendum* marker and no source-line
citation: addenda are new normative content, not transcriptions — D2 does not
apply; D1 does not apply because each is its own original.)

## 3. Companion edits

- **spec/03-obligation-matrix.md** — five rows (provenance `addendum (SEC-0xx)`,
  status SPECIFIED) and `Total: 157 obligations (148 transcribed + 9 addenda)`.
- **spec/06-contradictions-ambiguities.md** — rows **C-78** (decode-side
  minting; BLOCKING), **C-79** (unimplementable delegation surface; BLOCKING),
  **C-80** (ill-formed I2 verification contract; BLOCKING), **C-81** (phantom
  `contains_capability`; MAJOR), all `resolved-by-addendum`.
- **spec/08-verification-mapping.md** — tag `RECOVERY-REVOCATION-DURABLE`
  (post-audit table, now plural); mutations M022/M023/M024/M032; registry
  title → M001–M024 + M032.
- **spec/normative-normalization-records.md** — addendum scope note extended
  to the five addendum-II obligations.
- **spec/_build_index.py** — sections S-02/S-16/S-17/S-18; 5 requirement rows
  (`addendum` provenance); mutations/tags; milestones M1/M4/M5/M6/M7/M10;
  crates ror-core/kernel/runtime/persistence; id-scheme counts (157 / 19 / 25).
- **README.md** — 152 → 157 stable requirement IDs.

## 4. Verification record (this draft's proof, before any apply)

- Precheck on the real tree: addendum ABSENT (all 14 markers missing), 42
  anchors intact — the absence is the finding (five HIGHs unfrozen).
- Dry run (temporary copies): 157 obligations / 157 matrix rows / 148 records;
  `audit/spec_check.py` parses 148/157/157 (non-vacuous), D1=0, no FAIL, zero
  warnings on the five new obligations (36 pre-existing adjudicated, unchanged).
- New-row body↔matrix agreement (D3 overlap, threshold 0.25): R-CANON-12 0.76,
  R-PERSIST-07 0.81, R-MARSHAL-05 0.77, R-MARSHAL-06 0.92, R-CORE-11 0.79.
- Sandboxed `spec/_build_index.py` rebuild: `requirements=157 findings=80
  mutations=25 tags=19 sections=24`; JSON carries all new IDs, C-78…C-81 with
  status `resolved-by-addendum`, M032, and the new tag.

## 5. Adoption procedure

1. `python3 audit/spec_addendum2.py` — re-run the dry-run proof on the current tree.
2. `python3 audit/spec_addendum2.py --apply` — applies 42 edits across 7 files, re-runs every check on the real tree, regenerates `spec/10-index.json` (verified in-step).
3. `python3 spec/_check.py` — the promoted gate must still exit 0 (D1=0).
4. Single adoption commit (git-reversible); `req/_validate.py` sanity check.

Generated from `audit/spec_addendum2.py` constants — 2026-09-02.
