#!/usr/bin/env python3
"""spec_addendum2.py — HIGH-findings frozen-addendum applier (SEC-003/004/005/016/018).

Freezes the five HIGH remediations (audit report §6 item 3) as additive
normative text, across the same seven files as addendum I:

  spec/01  + R-CORE-11  (SEC-016: canonical I2 predicate signatures)
           + R-CANON-12 (SEC-003: decode-side authority minting forbidden)
           + R-PERSIST-07 (SEC-004: durable authority lattice)
           + R-MARSHAL-05 (SEC-005: delegation constructible + revalidated)
           + R-MARSHAL-06 (SEC-018: contains_capability frozen total predicate)
  spec/03  + 5 rows, Total 152 -> 157
  spec/06  + C-78..C-81 (security consequences registered; resolved-by-addendum)
  spec/08  + tag RECOVERY-REVOCATION-DURABLE, mutations M022/M023/M024/M032
  records  scope note extended to addendum II
  README   152 -> 157 IDs
  spec/_build_index.py  inline dataset extended (sections/reqs/mutations/tags/
            milestones/crates/id-scheme counts)

Default: DRY RUN — applies to temporary copies and re-measures with
audit/spec_check.py + a sandboxed index rebuild.  --apply: in place.
Exit 0 = proof complete; 1 = verification failed; 2 = safety abort
(already applied / anchor or count mismatch).

term/ rows (X-01/X-04/X-05/X-65 resolution marks, the contains_capability
phantom registration) are intentionally NOT touched here: term/02 is a
generated, source-validated register (term/_terms.py -> term/_dict.py,
re-grepped against Red-on-Rust.md by term/_check.py); the normative
resolutions are recorded in R-CORE-11/R-MARSHAL-05/R-MARSHAL-06, which the
term/ pipeline can cite when it is next regenerated.
"""

from __future__ import annotations

import re
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SPEC01 = REPO / "spec" / "01-canonical-specification.md"
MATRIX = REPO / "spec" / "03-obligation-matrix.md"
CONTRA = REPO / "spec" / "06-contradictions-ambiguities.md"
VMAP = REPO / "spec" / "08-verification-mapping.md"
RECORDS = REPO / "spec" / "normative-normalization-records.md"
README = REPO / "README.md"
CHECKER = REPO / "audit" / "spec_check.py"
BUILDIDX = REPO / "spec" / "_build_index.py"
SPEC09 = REPO / "spec" / "09-unresolved-decisions.md"

NEW_IDS = ["R-CANON-12", "R-CORE-11", "R-MARSHAL-05", "R-MARSHAL-06", "R-PERSIST-07"]
MARKERS = NEW_IDS + ["C-78", "C-79", "C-80", "C-81", "M022", "M023", "M024",
                     "M032", "RECOVERY-REVOCATION-DURABLE"]

ADD_CORE11 = "**R-CORE-11 (I2 predicate signatures, canonical form — frozen addendum).** The central theorem's predicates each have ONE canonical signature; all other frozen signatures are SUPERSEDED (quoted, not deleted). First conjunct: `ValidatedRequest(E)` — request-time validation inside the 16 gates — with the subsumption `ValidatedRequest(E) ⇒ ValidatedPlan(plan(E))`; the `ValidatedPlan` compiler-struct homonym (X-01) is disambiguated by qualification — `ValidatedPlan_pred` vs `ValidatedPlan_struct` — adopted repository-wide. Authorization: `Authorized(holder, c, E, t) ⇔ c ∈ κ_holder ∧ Valid(c, t) ∧ Authorized(κ_holder(c), E, t)` — holder first, possession a conjunct (formalizing R-KERN-04); the authority-first reading `Authorized(A, E, t)` is SUPERSEDED (quoted, not deleted). The 7-conjunct chain (R-CORE-02) is stated once, over these exact signatures; differential adjudication (R-TEST-09) MUST adjudicate against this form — weaker plan-time-only or authority-first readings MUST NOT satisfy the chain. *(Frozen addendum — post-audit remediation SEC-016; additive per R-SCOPE-03; extends R-CORE-02/R-KERN-04; resolves C-80 and, at the normative layer, term/ X-01/X-04/X-05; no source transcription.)*"

ADD_CANON12 = "**R-CANON-12 (decode-side authority minting forbidden — frozen addendum).** The data codec — the decoder for messages, receipt results, plan literals, and mailbox/snapshot value payloads — MUST reject capability payloads on decode: discriminant `0x05` (`TAG_CAPABILITY`) and standalone `0x30` (`CapRef::TYPE_TAG`) MUST yield `CanonicalError::CapabilityInData`, not a `Value::Capability`. Only the kernel-mediated codec path — persistence of kernel authority state and kernel-sealed delegation envelopes (R-MARSHAL-05) — may produce or consume capability payloads. `unmarshal` MUST run `contains_capability` (R-MARSHAL-06) over the decoded value regardless of provenance, making the marshalling boundary symmetric with `marshal`. Property: for all bytes `b`, `contains_capability(unmarshal_data(b)) = false ∨ unmarshal_data(b) = Err`. Resolves C-14/U-02 in the direction of the design rule (a serialized capability must go through explicit delegation); negative golden vectors (capability bytes, nested-at-depth, standalone envelope) are normative fixtures. *(Frozen addendum — post-audit remediation SEC-003; additive per R-SCOPE-03; extends R-CANON-11/R-MARSHAL-03; resolves C-78; no source transcription.)*"

ADD_PERSIST07 = "**R-PERSIST-07 (durable authority lattice — frozen addendum).** The kernel authority image — `AuthorityNode` set with parent links, the `revocation_set`, and generation counters — MUST be durable: snapshots MUST contain it (the invariant is frozen here; byte encoding remains U-02 scope), and the WAL MUST carry `CapabilityGranted`, `CapabilityDerived`, and `CapabilityRevoked` event kinds (freezing the event set in the security direction). Recovery MUST reconstruct the kernel arena, replay capability events after the snapshot sequence, and reject with `RecoveryFault` — never silently repair (R-RECOV-05, R-CORE-10) — any CapRef (in contexts, heaps, frames, mailboxes) that does not resolve with matching generation. Post-recovery, every actor capability MUST be revalidated: `∀ a, ∀ c ∈ caps(a): Valid(c, t_recovered)`; revocation MUST be monotonic across crashes — a revoked capability MUST NOT become valid again without a new explicit grant. `Recover(D) ≡ PreCrashMachineState` includes the authority lattice. *(Frozen addendum — post-audit remediation SEC-004; additive per R-SCOPE-03; extends R-PERSIST-04/R-CAP-07/R-CORE-09; tag `RECOVERY-REVOCATION-DURABLE`; no source transcription.)*"

ADD_MARSHAL05 = "**R-MARSHAL-05 (delegation surface constructible and revalidated — frozen addendum).** The sanctioned authority-transfer channel MUST be constructible as frozen: `Expr::Delegate { capability, constraint }` evaluates by calling `kernel.derive` with the declared constraint and produces a kernel-constructed delegation envelope — NOT a plain `Value` variant; `Value::DelegatedCapability` as a data variant is forbidden. Envelope admission at `Receive`: `register(envelope, recipient)` MUST be preceded by kernel revalidation — liveness, lineage (`DelegatedAuthority ≼ ParentAuthority`), target binding, and generation — against an existing kernel derivation record `d` with `envelope.cap = d.child ∧ d.parent ∈ sender.context`; any failure MUST fault with the recipient's `CapabilityContext` byte-identical (no partial registration). `MarshalledValue` is the checked-bytes form (R-MARSHAL-03): mailbox bytes MUST NOT exist as a `Value`, snapshots storing mailboxes store the checked form, and the private-constructor-wrapper reading is SUPERSEDED (quoted, not deleted). `MarshalFault` has ONE unified closed variant set. *(Frozen addendum — post-audit remediation SEC-005; additive per R-SCOPE-03; extends R-MARSHAL-02/R-MARSHAL-04; resolves C-79 and, at the normative layer, term/ X-65; no source transcription.)*"

ADD_MARSHAL06 = "**R-MARSHAL-06 (contains_capability is a frozen total predicate — frozen addendum).** `contains_capability(v)` MUST be a total predicate with an explicitly closed traversal domain: it MUST descend recursively, at unbounded structural depth, into `List`, `Map` (keys and values), `Tuple` elements, and — the load-bearing case — `FunctionValue.env` (captured closure environments, recursively: environments bind names to `Value`, and a closure whose environment binds a capability carries authority). Kernel-sealed delegation envelopes (R-MARSHAL-05) are the sole exclusion, and then only sealed by the kernel. `Bytes` are data — the decode-side rule (R-CANON-12) governs their rehydration. The boundary invariant is stated over reachability, not one value domain: `marshal(v) = Ok ⇒ ¬∃c. Reachable(env_of(v), c)` outside kernel-sealed envelopes. Closure-carrying values whose environments bind capabilities MUST fault at `marshal`, never round-trip. *(Frozen addendum — post-audit remediation SEC-018; additive per R-SCOPE-03; extends R-CORE-07/R-MARSHAL-01; resolves C-81; no source transcription.)*"

ROW_CORE11 = "| R-CORE-11 | One canonical signature per I2 predicate: ValidatedRequest(E) request-time subsuming ValidatedPlan(plan(E)); Authorized(holder, c, E, t) possession conjunct (formalizes R-KERN-04); ValidatedPlan_pred vs ValidatedPlan_struct; chain stated once (X-01/X-04/X-05; C-80 resolved) | addendum (SEC-016) | SPECIFIED | ror-kernel, ror-runtime | R-TEST-09 differential adjudication |"
ROW_CANON12 = "| R-CANON-12 | Data decoder rejects capability payloads: 0x05 and standalone 0x30 yield CanonicalError::CapabilityInData; only the kernel-mediated codec path produces or consumes capability payloads; unmarshal runs contains_capability — symmetric boundary (C-14/U-02 security direction; C-78 resolved) | addendum (SEC-003) | SPECIFIED | ror-core | M022, negative golden vectors |"
ROW_PERSIST7 = "| R-PERSIST-07 | Durable authority lattice: snapshot carries the AuthorityNode set, revocation_set and generation counters; WAL event kinds CapabilityGranted/Derived/Revoked; recovery reconstructs the arena, replays capability events, faults on dangling or generation-mismatched CapRef; revocation monotonic across crashes (RECOVERY-REVOCATION-DURABLE) | addendum (SEC-004) | SPECIFIED | ror-persistence, ror-kernel | RECOVERY-REVOCATION-DURABLE, M023, crash matrix T0–T6 with pre-crash revocation |"
ROW_MARSHAL5 = "| R-MARSHAL-05 | Delegation constructible: Expr::Delegate calls kernel.derive and yields a kernel-constructed envelope, never a plain Value variant; receive-side revalidation (liveness, lineage, target, generation) before registration, faults leave the recipient CapabilityContext byte-identical; MarshalledValue is the checked-bytes form; MarshalFault unified (X-65; C-79 resolved) | addendum (SEC-005) | SPECIFIED | ror-runtime, ror-kernel | M024, delegation negative suite |"
ROW_MARSHAL6 = "| R-MARSHAL-06 | contains_capability is a frozen total predicate: closed traversal domain descending into List, Map, Tuple at any depth and FunctionValue.env recursively; sole exclusion kernel-sealed delegation envelopes; Bytes are data; marshal Ok implies no reachable capability (C-81 resolved) | addendum (SEC-018) | SPECIFIED | ror-runtime | M032, closure-smuggling corpus |"

C_ROWS = [
 "| C-78 | C-14/U-02 record the capability-encoding gap (`CapRef` serializable; the 15A decoder mints `Value::Capability` from raw bytes) as an encoding ambiguity; the security consequence — every bytes→value path mints authority references without kernel involvement (snapshot mailbox payloads, WAL decode, differential fixtures) — is absent (audit SEC-003) | BLOCKING | L33158–33191, L25685–25696, L26008–26030, L5987 | **resolved-by-addendum** → `R-CANON-12` | The marshalling pair is enforced asymmetrically as frozen: `marshal_value` rejects capabilities, `unmarshal_value = canonical_deserialize` accepts them, so the L5987 design rule (\"a serialized capability should go through an explicit delegation mechanism\") is unenforceable. `R-CANON-12` makes the boundary symmetric (decode-side rejection + `contains_capability` on every unmarshal) and reserves capability payloads to the kernel-mediated codec path; byte-level encoding choices remain U-02's open scope. Cross-ref: C-14, U-02, term/ X-50, X-54. |",
 "| C-79 | term/ X-65 records `MarshalFault` declared twice with disjoint variants and `MarshalledValue` as two incompatible boundary mechanisms (private-constructor Value wrapper vs raw canonical bytes); the security consequence — the sanctioned authority-transfer channel (R-MARSHAL-02's \"only exception\") is unimplementable as frozen, so every implementation invents its own authority-transfer surface — is absent (audit SEC-005) | BLOCKING | L10827–10841, L25683–25687, L25976–25986, L12145–12205, L8695–8697 | **resolved-by-addendum** → `R-MARSHAL-05` | Invented authority-transfer surfaces are the historical locus of capability-system failures (envelope forgery, missing receive-side revalidation, ignored constraints); the frozen `Expr::Delegate`/`DelegatedCapability` sketch has no AST node in the 12-constructor `Expr`, no value variant in any frozen `Value` domain, and no codec tag. `R-MARSHAL-05` freezes the kernel-constructed envelope, registration-time revalidation (liveness, lineage, target, generation), the checked-bytes `MarshalledValue`, and one unified `MarshalFault`. Cross-ref: term/ X-65, AMB-11, U-02. |",
 "| C-80 | term/ X-01 (BLOCKING) and X-05 (MAJOR) record the `ValidatedPlan` predicate/struct homonym and the six incompatible `Authorized` signatures; the security consequence — the verification contract for the entire audit is ill-formed, so the weaker reading (plan-time validation, authority-first authorization) is always available to an implementation under adjudication — is absent (audit SEC-016) | BLOCKING | L23694, L41337–41351, L865, L2111, L3293, L4687, L5998, L6406, L8733 | **resolved-by-addendum** → `R-CORE-11` | The conjunctive chain that R-CORE-02 restates is the verification contract for every other finding; an ill-formed contract launders security defects into \"reference defect\" or \"spec ambiguity\" adjudications. `R-CORE-11` freezes `ValidatedRequest(E)` (request-time, subsuming `ValidatedPlan`) and `Authorized(holder, c, E, t)` (possession conjunct, formalizing R-KERN-04), resolves the struct homonym by qualification, and requires differential adjudication against the canonical form. Cross-ref: term/ X-01, X-04, X-05. |",
 "| C-81 | `contains_capability` — the sole mechanism of the R-CORE-07/R-MARSHAL-01 marshalling boundary — is invoked exactly once (L25685–25691) and defined nowhere; no rule states its traversal domain, so closure-environment smuggling (a closure whose captured environment binds a capability) is undetectable (audit SEC-018) | MAJOR | L25685–25691, L12354–12359, L10860, L12283–12310 | **resolved-by-addendum** → `R-MARSHAL-06` | The term registry (T-73), collisions (X-65), and module files discuss `MarshalFault` variants but not the predicate's absence; it is a used-but-never-declared identifier — the declaration sweep's exact category (cf. X-29/X-30/X-64). The boundary the actor-isolation story depends on is one unresolved identifier wide. `R-MARSHAL-06` freezes the total predicate (closed traversal domain including `FunctionValue.env` recursively) and states the invariant over reachability, not one value domain. Cross-ref: R-CORE-07, R-MARSHAL-01, mutation M032. |",
]

TAG_ROW2 = "| `RECOVERY-REVOCATION-DURABLE` | R-PERSIST-07 (post-audit addendum) | Revocation survives crash: crash matrix T0–T6 with revocation committed before the crash point; revoked caps stay revoked; dangling/generation-mismatched CapRefs ⇒ `RecoveryFault` (mutation M023) | NONE |"

MUT_ROWS2 = ("| M022 | unmarshal accepts capability payload | R-CANON-12 |\n"
             "| M023 | recovery resurrects revoked capability | R-PERSIST-07 |\n"
             "| M024 | receive-side registration without kernel revalidation | R-MARSHAL-05 |\n"
             "| M032 | contains_capability skips `FunctionValue.env` | R-MARSHAL-06 |")

RECORDS_NOTE2 = " The same holds for the five addendum-II obligations (`R-CANON-12`, `R-CORE-11`, `R-MARSHAL-05`, `R-MARSHAL-06`, `R-PERSIST-07`; remediations SEC-003/004/005/016/018)."

IDX_CORE11 = ' ("R-CORE-11","S-02","I2 predicate signatures, canonical form (frozen addendum)","addendum",SPEC,[],["ror-kernel","ror-runtime"],["R-TEST-09","R-KERN-04"],["C-80"]),'
IDX_CANON12 = ' ("R-CANON-12","S-17","Data decoder rejects capability payloads (frozen addendum)","addendum",SPEC,[],["ror-core"],["M022","negative golden vectors"],["C-78"]),'
IDX_PERSIST7 = ' ("R-PERSIST-07","S-18","Durable authority lattice; revocation survives crash (frozen addendum)","addendum",SPEC,[],["ror-persistence","ror-kernel"],["RECOVERY-REVOCATION-DURABLE","M023"],[]),'
IDX_MARSHAL5 = ' ("R-MARSHAL-05","S-16","Delegation surface constructible and revalidated (frozen addendum)","addendum",SPEC,[],["ror-runtime","ror-kernel"],["M024","delegation negative suite"],["C-79"]),'
IDX_MARSHAL6 = ' ("R-MARSHAL-06","S-16","contains_capability frozen total predicate (frozen addendum)","addendum",SPEC,[],["ror-runtime"],["M032","closure-smuggling corpus"],["C-81"]),'
IDX_MUTS2 = (' ("M022","unmarshal accepts capability payload",["R-CANON-12"]),\n'
             ' ("M023","recovery resurrects revoked capability",["R-PERSIST-07"]),\n'
             ' ("M024","receive-side registration without kernel revalidation",["R-MARSHAL-05"]),\n'
             ' ("M032","contains_capability skips FunctionValue.env",["R-MARSHAL-06"]),')
IDX_TAG2 = ' ("RECOVERY-REVOCATION-DURABLE",["R-PERSIST-07"],"M10 (post-audit addendum)"),'

EDITS: list[tuple[Path, str, str]] = [
    # spec/01 — one obligation cluster per section, ID order preserved
    (SPEC01, "*(L42100–42105; L35196–35208.)*",
     "*(L42100–42105; L35196–35208.)*\n\n" + ADD_CORE11),
    (SPEC01, "authority transfer requires the explicit `delegate(c, C, target_actor)` operation.",
     "authority transfer requires the explicit `delegate(c, C, target_actor)` operation.\n\n" + ADD_MARSHAL05 + "\n\n" + ADD_MARSHAL06),
    (SPEC01, "not additional behavioral rules.",
     "not additional behavioral rules.\n\n" + ADD_CANON12),
    (SPEC01, "*(L35088–35110; L35189–35208.)*",
     "*(L35088–35110; L35189–35208.)*\n\n" + ADD_PERSIST07),
    # spec/03 — rows after their area neighbours + total
    (MATRIX,
     "| R-CORE-10 | No silent recovery corruption | L42100–42105, L35196–35208 | SPECIFIED | ror-persistence | M015, M016, negative recovery tests |",
     "| R-CORE-10 | No silent recovery corruption | L42100–42105, L35196–35208 | SPECIFIED | ror-persistence | M015, M016, negative recovery tests |\n" + ROW_CORE11),
    (MATRIX,
     "| R-MARSHAL-04 | Semantic marshalling rule (CapRef ∉ marshal(v)) | L8695–8698 | SPECIFIED | ror-runtime | Track B |",
     "| R-MARSHAL-04 | Semantic marshalling rule (CapRef ∉ marshal(v)) | L8695–8698 | SPECIFIED | ror-runtime | Track B |\n" + ROW_MARSHAL5 + "\n" + ROW_MARSHAL6),
    (MATRIX,
     "| R-CANON-11 | Golden vectors as normative fixtures | L30599–30646, L31948–32010, L33266–33286 | SPECIFIED | ror-core (vectors/) | M1 acceptance |",
     "| R-CANON-11 | Golden vectors as normative fixtures | L30599–30646, L31948–32010, L33266–33286 | SPECIFIED | ror-core (vectors/) | M1 acceptance |\n" + ROW_CANON12),
    (MATRIX,
     "| R-PERSIST-06 | WAL sequence continuity; gaps rejected | L35088–35110, L35189–35208 | SPECIFIED | ror-persistence | WAL-SEQUENCE-CONTINUITY, WAL-GAP-REJECT, M015 |",
     "| R-PERSIST-06 | WAL sequence continuity; gaps rejected | L35088–35110, L35189–35208 | SPECIFIED | ror-persistence | WAL-SEQUENCE-CONTINUITY, WAL-GAP-REJECT, M015 |\n" + ROW_PERSIST7),
    (MATRIX,
     "**Total: 152 obligations** (148 transcribed from the frozen source + 4 post-audit frozen addenda: R-COMPILE-06, R-KERN-04, R-KERN-05, R-EFFECT-08).",
     "**Total: 157 obligations** (148 transcribed from the frozen source + 9 post-audit frozen addenda: R-COMPILE-06, R-CORE-11, R-KERN-04, R-KERN-05, R-EFFECT-08, R-MARSHAL-05, R-MARSHAL-06, R-CANON-12, R-PERSIST-07)."),
    # spec/08 — tag + mutations + registry title
    (VMAP,
     "**Post-audit addendum tag** (not part of the frozen source set; added by the SEC-001 remediation, obligation R-EFFECT-08):",
     "**Post-audit addendum tags** (not part of the frozen source set; added by remediations SEC-001 and SEC-004):"),
    (VMAP,
     "| `EFFECT-RECEIPT-RESULT-NO-AUTHORITY` | R-EFFECT-08 (post-audit addendum) | Receipt-result admission: result payload is data-domain only, capability/closure-free at any nesting depth, verified before resumption (mutations M019, M020) | NONE |",
     "| `EFFECT-RECEIPT-RESULT-NO-AUTHORITY` | R-EFFECT-08 (post-audit addendum) | Receipt-result admission: result payload is data-domain only, capability/closure-free at any nesting depth, verified before resumption (mutations M019, M020) | NONE |\n" + TAG_ROW2),
    (VMAP,
     "| M021 | authorize without possession check | R-KERN-04 |",
     "| M021 | authorize without possession check | R-KERN-04 |\n" + MUT_ROWS2),
    (VMAP,
     "## 2. Mutation registry → obligation map (M001–M021, R-TEST-04)",
     "## 2. Mutation registry → obligation map (M001–M024 + M032, R-TEST-04)"),
    # records — scope note extension
    (RECORDS,
     "`Original = Normalized` by construction.",
     "`Original = Normalized` by construction." + RECORDS_NOTE2),
    # README — count
    (README,
     "- `spec/03-obligation-matrix.md` — 152 stable requirement IDs (`R-…`; 148 from the frozen source + 4 post-audit frozen addenda) with status and provenance",
     "- `spec/03-obligation-matrix.md` — 157 stable requirement IDs (`R-…`; 148 from the frozen source + 9 post-audit frozen addenda) with status and provenance"),
    # spec/_build_index.py — sections
    (BUILDIDX,
     '"R-CORE-09","R-CORE-10"],prov("27485-27654"',
     '"R-CORE-09","R-CORE-10","R-CORE-11"],prov("27485-27654"'),
    (BUILDIDX,
     '"R-MARSHAL-03","R-MARSHAL-04"],prov("25674-26001"',
     '"R-MARSHAL-03","R-MARSHAL-04","R-MARSHAL-05","R-MARSHAL-06"],prov("25674-26001"'),
    (BUILDIDX,
     '"R-CANON-10","R-CANON-11"],prov(',
     '"R-CANON-10","R-CANON-11","R-CANON-12"],prov('),
    (BUILDIDX,
     '"R-PERSIST-05","R-PERSIST-06"],prov(',
     '"R-PERSIST-05","R-PERSIST-06","R-PERSIST-07"],prov('),
    # spec/_build_index.py — requirement rows
    (BUILDIDX,
     ' ("R-CORE-10","S-02","No silent recovery corruption","42100-42105;35196-35208",SPEC,[],["ror-persistence"],["M015","M016","negative recovery tests"],[]),',
     ' ("R-CORE-10","S-02","No silent recovery corruption","42100-42105;35196-35208",SPEC,[],["ror-persistence"],["M015","M016","negative recovery tests"],[]),\n' + IDX_CORE11),
    (BUILDIDX,
     ' ("R-MARSHAL-04","S-16","Semantic marshalling rule (CapRef not in marshal(v))","8695-8698",SPEC,[],["ror-runtime"],["Track B"],[]),',
     ' ("R-MARSHAL-04","S-16","Semantic marshalling rule (CapRef not in marshal(v))","8695-8698",SPEC,[],["ror-runtime"],["Track B"],[]),\n' + IDX_MARSHAL5 + '\n' + IDX_MARSHAL6),
    (BUILDIDX,
     ' ("R-CANON-11","S-17","Golden vectors as normative fixtures","30599-30646;31948-32010;33266-33286",SPEC,[],["ror-core (vectors/)"],["M1 acceptance"],[]),',
     ' ("R-CANON-11","S-17","Golden vectors as normative fixtures","30599-30646;31948-32010;33266-33286",SPEC,[],["ror-core (vectors/)"],["M1 acceptance"],[]),\n' + IDX_CANON12),
    (BUILDIDX,
     ' ("R-PERSIST-06","S-18","WAL sequence continuity; gaps rejected","35088-35110;35189-35208",SPEC,[],["ror-persistence"],["WAL-SEQUENCE-CONTINUITY","WAL-GAP-REJECT","M015"],["U-16"]),',
     ' ("R-PERSIST-06","S-18","WAL sequence continuity; gaps rejected","35088-35110;35189-35208",SPEC,[],["ror-persistence"],["WAL-SEQUENCE-CONTINUITY","WAL-GAP-REJECT","M015"],["U-16"]),\n' + IDX_PERSIST7),
    # spec/_build_index.py — mutations + tags
    (BUILDIDX,
     ' ("M021","authorize without possession check",["R-KERN-04"]),',
     ' ("M021","authorize without possession check",["R-KERN-04"]),\n' + IDX_MUTS2),
    (BUILDIDX,
     ' ("EFFECT-RECEIPT-RESULT-NO-AUTHORITY",["R-EFFECT-08"],"M5 (post-audit addendum)"),',
     ' ("EFFECT-RECEIPT-RESULT-NO-AUTHORITY",["R-EFFECT-08"],"M5 (post-audit addendum)"),\n' + IDX_TAG2),
    # spec/_build_index.py — milestone maps
    (BUILDIDX, '"R-CANON-10","R-CANON-11"]),', '"R-CANON-10","R-CANON-11","R-CANON-12"]),'),
    (BUILDIDX, '"R-KERN-04","R-KERN-05"]),', '"R-KERN-04","R-KERN-05","R-MARSHAL-05"]),'),
    (BUILDIDX, '"R-HOST-05","R-EFFECT-08"]),', '"R-HOST-05","R-EFFECT-08","R-CORE-11"]),'),
    (BUILDIDX, '"R-MARSHAL-04"]),', '"R-MARSHAL-04","R-MARSHAL-06"]),'),
    (BUILDIDX, '"R-RECOV-06"]),', '"R-RECOV-06","R-PERSIST-07"]),'),
    (BUILDIDX, '["R-RECOV-02","R-TEST-08","R-DUR-04"]),', '["R-RECOV-02","R-TEST-08","R-DUR-04","R-PERSIST-07"]),'),
    # spec/_build_index.py — crate maps
    (BUILDIDX, '"R-CANON-10","R-CANON-11"],[]),', '"R-CANON-10","R-CANON-11","R-CANON-12"],[]),'),
    (BUILDIDX, '"R-KERN-04","R-KERN-05","R-TRUST-03"]', '"R-KERN-04","R-KERN-05","R-PERSIST-07","R-CORE-11","R-TRUST-03"]'),
    (BUILDIDX, '"R-MARSHAL-03","R-MARSHAL-04"],["ror-core","ror-kernel"]),', '"R-MARSHAL-03","R-MARSHAL-04","R-MARSHAL-05","R-MARSHAL-06","R-CORE-11"],["ror-core","ror-kernel"]),'),
    (BUILDIDX, '"R-RECOV-07","R-KERN-05"],["ror-core"]),', '"R-RECOV-07","R-KERN-05","R-PERSIST-07"],["ror-core"]),'),
    # spec/_build_index.py — id-scheme counts
    (BUILDIDX,
     '"R-AREA-NN": "normative requirement/obligation (152; 148 source-transcribed + 4 post-audit frozen addenda)"',
     '"R-AREA-NN": "normative requirement/obligation (157; 148 source-transcribed + 9 post-audit frozen addenda)"'),
    (BUILDIDX,
     '"TAG": "source verification-obligation tags (18; 17 frozen-source + 1 post-audit addendum)"',
     '"TAG": "source verification-obligation tags (19; 17 frozen-source + 2 post-audit addenda)"'),
    (BUILDIDX,
     '"M0NN": "baseline mutation registry (21; 18 baseline + 3 post-audit)"',
     '"M0NN": "baseline mutation registry (25; 18 baseline + 7 post-audit: M019–M024, M032)"'),
]

# C-78..C-81 rows: line-based, inserted after C-77's row
CONTRA_C77_PREFIX = "| C-77 |"


def apply_edits(files: dict[Path, str]) -> dict[Path, str]:
    """Apply EDITS (+C-78..81 line inserts) to a {path: text} mapping."""
    for path, find, repl in EDITS:
        n = files[path].count(find)
        if n != 1:
            print(f"ABORT: anchor x{n} (need exactly 1) in {path.name}: {find[:70]!r}")
            sys.exit(2)
        files[path] = files[path].replace(find, repl, 1)
    lines = files[CONTRA].splitlines(keepends=True)
    idx = [i for i, ln in enumerate(lines) if ln.startswith(CONTRA_C77_PREFIX)]
    if len(idx) != 1:
        print(f"ABORT: C-77 anchor rows = {len(idx)} (need 1)")
        sys.exit(2)
    for row in reversed(C_ROWS):
        lines.insert(idx[0] + 1, row + "\n")
    files[CONTRA] = "".join(lines)
    return files


def check_tree(spec01: Path, matrix: Path, records: Path, extra: str, label: str) -> bool:
    """Structural + checker verification over the given (possibly temp) files."""
    ok = True
    t01, t03, trec = (p.read_text(encoding="utf-8") for p in (spec01, matrix, records))
    n_ob = len(re.findall(r"\*\*(R-[A-Z]+-\d+)[^\n]*?\*\*", t01))
    n_mx = len(re.findall(r"^\|\s*R-[A-Z]+-\d+\s*\|", t03, re.M))
    n_rc = len(re.findall(r"^### (R-[A-Z]+-\d+)\s*$", trec, re.M))
    print(f"[{label}] obligations={n_ob} matrix_rows={n_mx} records={n_rc}")
    for want, got, what in ((157, n_ob, "obligations"), (157, n_mx, "matrix rows"), (148, n_rc, "records")):
        if got != want:
            print(f"  FAIL: {what} = {got}, expected {want}")
            ok = False
    for m in MARKERS:
        if m not in t01 and m not in t03 and m not in trec and m not in extra:
            print(f"  FAIL: marker {m!r} absent from addendum targets")
            ok = False
    out = subprocess.run(
        [sys.executable, str(CHECKER), "--records", str(records),
         "--spec01", str(spec01), "--matrix", str(matrix)],
        capture_output=True, text=True, check=False).stdout
    first = out.splitlines()[0] if out else ""
    print(f"[{label}] checker: {first}")
    if "157 spec/01 obligations, 157 matrix rows" not in first or "148 records" not in first:
        print("  FAIL: checker parse counts unexpected (vacuous-run guard)")
        ok = False
    bad = [ln for ln in out.splitlines()
           if re.search(r"\[D\d\] (" + "|".join(NEW_IDS) + r")\b", ln)]
    for ln in bad:
        print(f"  FAIL: new addendum obligation flagged: {ln.strip()}")
        ok = False
    if "FAIL:" in out:
        print("  FAIL: checker hard-failed (D1 class)")
        ok = False
    warn_n = len(re.findall(r"WARN \[D\d\]", out))
    print(f"[{label}] checker warnings (pre-existing adjudicated set): {warn_n}")
    return ok


def check_index(cwd: Path, builder: Path, index_json: Path, label: str) -> bool:
    """Run (possibly sandboxed) spec/_build_index.py and verify the counts."""
    import json as _json
    ok = True
    r = subprocess.run([sys.executable, str(builder)], cwd=cwd,
                       capture_output=True, text=True, check=False)
    counts = next((ln for ln in r.stdout.splitlines() if "requirements=" in ln), "")
    print(f"[{label}] index rebuild: {counts or r.stdout[-200:] or r.stderr[-200:]}")
    for want in ("requirements=157", "findings=80", "mutations=25", "tags=19", "sections=24"):
        if want not in counts:
            print(f"  FAIL: index counts missing {want!r}")
            ok = False
    data = _json.loads(index_json.read_text(encoding="utf-8"))
    blob = _json.dumps(data)
    for m in NEW_IDS + ["C-78", "C-79", "C-80", "C-81", "M032",
                        "RECOVERY-REVOCATION-DURABLE", "post-audit frozen addendum"]:
        if m not in blob:
            print(f"  FAIL: 10-index.json missing {m!r}")
            ok = False
    st = [f for f in data.get("findings", []) if f.get("id") == "C-78"]
    if not st or st[0].get("status") != "resolved-by-addendum":
        print(f"  FAIL: C-78 status in index = {st[0]['status'] if st else 'absent'!r}")
        ok = False
    return ok


def main() -> int:
    apply_mode = "--apply" in sys.argv

    targets = [SPEC01, MATRIX, CONTRA, VMAP, RECORDS, README, BUILDIDX]
    real = {p: p.read_text(encoding="utf-8") for p in targets}

    # Precheck: the addendum must be ABSENT on the real tree (evidence), and
    # every anchor must be intact.  Presence => idempotency abort.
    present = [m for m in MARKERS if any(m in real[p] for p in targets)]
    anchor_fail = []
    for path, find, _ in EDITS:
        if real[path].count(find) != 1:
            anchor_fail.append((path.name, find[:60]))
    if present or anchor_fail:
        if present:
            print(f"ABORT: addendum already applied (markers present: {present})")
        else:
            print("ABORT: anchors unexpectedly absent — tree changed?")
            for name, f in anchor_fail:
                print(f"  missing/duplicated anchor in {name}: {f!r}")
        return 2
    print(f"precheck: addendum ABSENT on real tree (no markers found) — "
          f"SEC-003/004/005/016/018 unfrozen (this absence is the finding); "
          f"{len(EDITS) + len(C_ROWS)} anchors intact")

    if not apply_mode:
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            files = apply_edits({p: real[p] for p in targets})
            for p in targets:
                (tmp / p.name).write_text(files[p], encoding="utf-8")
            __import__("shutil").copy(SPEC09, tmp / SPEC09.name)
            (tmp / "spec").mkdir()
            extra = files[CONTRA] + files[VMAP] + files[README]
            ok = check_tree(tmp / SPEC01.name, tmp / MATRIX.name, tmp / RECORDS.name,
                            extra, "dry-run")
            ok = check_index(tmp, tmp / BUILDIDX.name, tmp / "spec" / "10-index.json",
                             "dry-run") and ok
            print("\nDRY RUN: " + ("PROOF COMPLETE — addendum verifies clean"
                                   if ok else "VERIFICATION FAILED"))
            return 0 if ok else 1

    files = apply_edits({p: real[p] for p in targets})
    for p in targets:
        p.write_text(files[p], encoding="utf-8")
    print(f"applied: {len(EDITS) + len(C_ROWS)} edits across {len(targets)} files")
    extra = files[CONTRA] + files[VMAP] + files[README]
    ok = check_tree(SPEC01, MATRIX, RECORDS, extra, "post-apply")
    ok = check_index(REPO, BUILDIDX, REPO / "spec" / "10-index.json", "post-apply") and ok
    print("\nAPPLY: " + ("VERIFIED" if ok else "VERIFICATION FAILED — inspect git diff"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
