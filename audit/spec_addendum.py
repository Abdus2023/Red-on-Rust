#!/usr/bin/env python3
"""spec_addendum.py — SEC-001/SEC-002 frozen-addendum applier (draft → tree).

Freezes the two remaining CRITICAL remediations as additive normative text
(audit report §6 item 2), across six files:

  spec/01-canonical-specification.md   + R-COMPILE-06, R-KERN-04, R-KERN-05,
                                        R-EFFECT-08 (frozen addenda, quoted-
                                        not-deleted supersession markers, no
                                        source transcription => D2-exempt)
  spec/03-obligation-matrix.md         + 4 rows, Total 148 -> 152
  spec/06-contradictions-ambiguities.md + resolution status "resolved-by-
                                        addendum" + C-77 (the previously
                                        unregistered v0.3-vs-global-arena
                                        authorization conflict)
  spec/08-verification-mapping.md      + tag EFFECT-RECEIPT-RESULT-NO-AUTHORITY,
                                        mutations M019/M020/M021
  spec/normative-normalization-records.md + scope note (addenda have no
                                        normalization record: each is its own
                                        original)
  README.md                            148 -> 152 IDs

Default: DRY RUN — applies to temporary copies and re-measures with
audit/spec_check.py (--records/--spec01/--matrix overrides).  --apply: in
place.  Exit 0 = proof complete; 1 = verification failed; 2 = safety abort
(already applied, or an anchor/count mismatch).

Evidence discipline: the precheck on the REAL tree must FAIL before any
apply (the addendum's absence is the finding); a passing precheck aborts
with "already applied" (idempotency).
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

NEW_IDS = ["R-COMPILE-06", "R-EFFECT-08", "R-KERN-04", "R-KERN-05"]
MARKERS = NEW_IDS + ["C-77", "M019", "M021", "EFFECT-RECEIPT-RESULT-NO-AUTHORITY",
                     "resolved-by-addendum"]

ADDENDUM = "**R-EFFECT-08 (receipt-result admission — frozen addendum).** A receipt may complete an effect; it MUST NOT confer authority. Before any continuation is resumed, the machine MUST run the recursive `contains_capability` predicate over the receipt's result payload at every nesting depth (`List`/`Map`/`Tuple` included) and MUST fault (`Fault::InvalidReceipt` family) on any `Value::Capability` and on any host `Function`/closure value. An admitted result MUST lie in the canonical data-domain (the 8-variant codec value set); host error results MUST enter machine values only through a declared, closed fault mapping — raw debug-formatted host text MUST NOT. This extends R-EFFECT-06 (causal validation of `id` and digest) from the receipt's identity to its payload: every value-crossing — messages, receipts, snapshots, replay traces — is subject to the no-raw-capability-transfer rule (R-CORE-07). *(Frozen addendum — post-audit remediation SEC-001 items 1–4; additive per R-SCOPE-03; extends R-EFFECT-06/R-EFFECT-07; no source transcription.)*"

ADD_KERN = "**R-KERN-04 (holder-possession binding at the gate — frozen addendum).** Authority exercise at the machine's authorization gate MUST be possession-gated: `Authorized_gated(actor, c, E, t) ⇔ c ∈ CapabilityContext(actor) ∧ Valid(c, t) ∧ Authorized(κ(c), E, t)` — possession is a conjunct of the gated authorization predicate, not a marshalling courtesy. The kernel `authorize` API MUST be holder-parameterized (`authorize(holder, cap, effect, t)`) and MUST resolve the `CapRef` through the requesting actor's capability context; the global-arena no-holder form (`authorize(cap, effect, t)`) is SUPERSEDED (quoted, not deleted). `CapRef` bits MUST NOT suffice to exercise authority — `CapRef ≠ authority ownership` is a kernel-side possession rule. This binds the per-actor reading of the v0.3 formal rules (`Authorized(κ(c), E, t)`) over the kernel-substrate global arena (conflict C-77, resolved by this addendum). *(Frozen addendum — post-audit remediation SEC-002 items 1 and 4; additive per R-SCOPE-03; extends R-CAP-06/R-KERN-02; no source transcription.)*"

ADD_KERN_CTX = "**R-KERN-05 (CapabilityContext is a real possession type — frozen addendum).** `CapabilityContext` MUST be a real frozen type: the per-actor possession structure mapping the actor's capability slots to live `CapRef`s. The unit-type sketch (`pub type CapabilityContext = ();`) is SUPERSEDED (quoted, not deleted). Snapshots MUST carry the capability context, and recovery MUST reconstruct each actor's possession set before any gate authorization — a possession gate that does not survive recovery enforces nothing. *(Frozen addendum — post-audit remediation SEC-002 item 2; additive per R-SCOPE-03; extends R-KERN-02/R-KERN-04; no source transcription.)*"

ADD_COMPILE = "**R-COMPILE-06 (capability literals must be plan-bound — frozen addendum).** A `Block` MUST NOT carry a `Value::Capability` literal that is not plan-bound: compilation MUST fault on any embedded capability literal — foreign, garbage-generation, or own-but-undeclared — unless the compiler itself substituted it from the plan's declared capability set. Undecided capability-analysis depth (U-22) MUST NOT leave embedded authority literals unconstrained; this closes the U-22 gap in the security direction. *(Frozen addendum — post-audit remediation SEC-002 item 3; additive per R-SCOPE-03; extends R-COMPILE-02/R-COMPILE-03; no source transcription.)*"

ROW_EFFECT = "| R-EFFECT-08 | Receipt-result admission: recursive contains_capability over the result payload at any nesting depth; no capability, no closure; data-domain only; host error via declared closed fault mapping only | addendum (SEC-001) | SPECIFIED | ror-runtime | EFFECT-RECEIPT-RESULT-NO-AUTHORITY, M019, M020 |"
ROW_KERN4 = "| R-KERN-04 | Possession-gated authorization: authorize(holder, cap, effect, t) resolves the CapRef through the actor capability context; global-arena no-holder authorize superseded; CapRef bits never suffice (C-77 resolved) | addendum (SEC-002) | SPECIFIED | ror-kernel | M021, brute-force CapRef exhaustion from a non-holder |"
ROW_KERN5 = "| R-KERN-05 | CapabilityContext real frozen possession type; unit-type sketch superseded; snapshots carry capability context; recovery reconstructs possession before gate authorization | addendum (SEC-002) | SPECIFIED | ror-kernel, ror-persistence | snapshot/recovery round-trip of possession sets |"
ROW_COMPILE = "| R-COMPILE-06 | Embedded Value::Capability literals must be plan-bound: foreign/garbage/undeclared capability literal is a compilation fault (U-22 security-direction closure) | addendum (SEC-002) | SPECIFIED | ror-compiler | compiler conformance: embedded-literal battery |"

C77 = "| C-77 | The v0.3 formal rules gate authorization with the acting actor's map (`Authorized(κ(c), E, t)`, L8731/L8748) while the frozen kernel resolves `CapRef`s in a global arena with no holder parameter (`authorize(&self, cap, effect, t)`, L6702–6712; trait L9738–9744; gate 6 L23891) — possession is assumed by the formal layer and absent from the operative gate (audit SEC-002; previously unregistered) | BLOCKING | L8731, L8748 vs L6702–6712, L9738–9744, L23891 | **resolved-by-addendum** → `R-KERN-04` binds the per-actor possession reading | The two readings differ in exactly one conjunct — `c ∈ CapabilityContext(actor)` — but that conjunct is the difference between \"CapRef bits suffice\" and \"CapRef bits do not suffice\" at the authoritative boundary; under the kernel-side global reading the SEC-002 forgery path (embed/guess a foreign `CapRef`, pass gates 5–6) is conformant. `R-KERN-04` makes possession a conjunct of the gated predicate and holder-parameterizes the kernel API; `R-KERN-05` gives `CapabilityContext` a real frozen type; `R-COMPILE-06` closes the compile-side literal path. |"

TAG_ROW = "| `EFFECT-RECEIPT-RESULT-NO-AUTHORITY` | R-EFFECT-08 (post-audit addendum) | Receipt-result admission: result payload is data-domain only, capability/closure-free at any nesting depth, verified before resumption (mutations M019, M020) | NONE |"

MUT_ROWS = "| M019 | resume with `Value::Capability` result | R-EFFECT-08 |\n| M020 | resume with closure result | R-EFFECT-08 |\n| M021 | authorize without possession check | R-KERN-04 |"

RECORDS_NOTE = "> **Post-audit addenda (outside this pass's scope):** obligations `R-COMPILE-06`, `R-KERN-04`, `R-KERN-05`, `R-EFFECT-08` were added after the normalization pass as frozen addenda (SEC-001/SEC-002 remediation). They have no normalization record: each is its own original — no substitution, `Original = Normalized` by construction."

# (file, find, replacement) — find must occur exactly once; replacement re-inserts find.
EDITS: list[tuple[Path, str, str]] = [
    # spec/01 — one obligation cluster per section, ID order preserved
    (SPEC01,
     "No hidden authority inspection.",
     "No hidden authority inspection.\n\n" + ADD_KERN + "\n\n" + ADD_KERN_CTX),
    (SPEC01,
     "host faults map to the fault/value mapping defined by the machine).",
     "host faults map to the fault/value mapping defined by the machine).\n\n" + ADDENDUM),
    (SPEC01,
     "not re-specified]. *(L39296–39318.)*",
     "not re-specified]. *(L39296–39318.)*\n\n" + ADD_COMPILE),
    # spec/03 — rows after their area neighbours + total
    (MATRIX,
     "| R-COMPILE-05 | ExecutablePlan constructors private to compiler | L39296–39318 | SPECIFIED | ror-compiler | visibility review |",
     "| R-COMPILE-05 | ExecutablePlan constructors private to compiler | L39296–39318 | SPECIFIED | ror-compiler | visibility review |\n" + ROW_COMPILE),
    (MATRIX,
     "| R-KERN-03 | Authority internals pub(crate)/inaccessible | L39397–39407 | SPECIFIED | ror-kernel | visibility + mutation M005-class |",
     "| R-KERN-03 | Authority internals pub(crate)/inaccessible | L39397–39407 | SPECIFIED | ror-kernel | visibility + mutation M005-class |\n" + ROW_KERN4 + "\n" + ROW_KERN5),
    (MATRIX,
     "| R-EFFECT-07 | Completion accounting (charge complete, release reservation, log, resume) | L23949–24002 | SPECIFIED | ror-runtime | conservation tests |",
     "| R-EFFECT-07 | Completion accounting (charge complete, release reservation, log, resume) | L23949–24002 | SPECIFIED | ror-runtime | conservation tests |\n" + ROW_EFFECT),
    (MATRIX,
     "**Total: 148 obligations.**",
     "**Total: 152 obligations** (148 transcribed from the frozen source + 4 post-audit frozen addenda: R-COMPILE-06, R-KERN-04, R-KERN-05, R-EFFECT-08)."),
    # spec/06 — new resolution status + C-77
    (CONTRA,
     "- **open**: requires an explicit architectural decision → also listed in `09-unresolved-decisions.md` with its `U-` ID.",
     "- **open**: requires an explicit architectural decision → also listed in `09-unresolved-decisions.md` with its `U-` ID.\n- **resolved-by-addendum**: a post-audit frozen addendum in `spec/01` resolves it (recorded; the addendum is the decision)."),
    # spec/08 — tag + mutations + registry title
    (VMAP,
     "`MARSHAL-CAPABILITY-REJECT` ≙ `MARSHAL-NO-RAW-CAPABILITY` (C-10, terminology 05 §5).",
     "`MARSHAL-CAPABILITY-REJECT` ≙ `MARSHAL-NO-RAW-CAPABILITY` (C-10, terminology 05 §5).\n\n**Post-audit addendum tag** (not part of the frozen source set; added by the SEC-001 remediation, obligation R-EFFECT-08):\n\n| Tag | Obligation(s) covered | Required evidence | Repo evidence |\n|---|---|---|---|\n" + TAG_ROW),
    (VMAP,
     "| M018 | resume after corrupted receipt | R-EFFECT-06 |",
     "| M018 | resume after corrupted receipt | R-EFFECT-06 |\n" + MUT_ROWS),
    (VMAP,
     "## 2. Mutation registry → obligation map (M001–M018, R-TEST-04)",
     "## 2. Mutation registry → obligation map (M001–M021, R-TEST-04)"),
    # records — scope note
    (RECORDS,
     "**Source:** `spec/01-canonical-specification.md` (24 sections, 148 requirements `R-SCOPE-01`…`R-CLAIM-04`).",
     "**Source:** `spec/01-canonical-specification.md` (24 sections, 148 requirements `R-SCOPE-01`…`R-CLAIM-04`).\n\n" + RECORDS_NOTE),
    # README — count
    (README,
     "- `spec/03-obligation-matrix.md` — 148 stable requirement IDs (`R-…`) with status and provenance",
     "- `spec/03-obligation-matrix.md` — 152 stable requirement IDs (`R-…`; 148 from the frozen source + 4 post-audit frozen addenda) with status and provenance"),
]

# spec/_build_index.py — index stays complete (the builder's inline dataset
# must carry the addendum, or the regenerated 10-index.json re-opens the
# exact cross-layer drift class this audit exists to kill)
IDX_REQ_COMPILE = ' ("R-COMPILE-06","S-06","Capability literals must be plan-bound (frozen addendum)","addendum",SPEC,[],["ror-compiler"],["embedded-literal battery"],["U-22"]),'
IDX_REQ_KERN4 = ' ("R-KERN-04","S-10","Holder-possession binding at the gate (frozen addendum)","addendum",SPEC,[],["ror-kernel"],["M021","brute-force CapRef exhaustion from a non-holder"],["C-77"]),'
IDX_REQ_KERN5 = ' ("R-KERN-05","S-10","CapabilityContext real possession type; snapshots carry it (frozen addendum)","addendum",SPEC,[],["ror-kernel","ror-persistence"],["snapshot/recovery round-trip of possession sets"],["C-77"]),'
IDX_REQ_EFFECT = ' ("R-EFFECT-08","S-12","Receipt-result admission: no authority via results (frozen addendum)","addendum",SPEC,[],["ror-runtime"],["EFFECT-RECEIPT-RESULT-NO-AUTHORITY","M019","M020"],[]),'
IDX_MUTS = (' ("M019","resume with Value::Capability result",["R-EFFECT-08"]),\n'
            ' ("M020","resume with closure result",["R-EFFECT-08"]),\n'
            ' ("M021","authorize without possession check",["R-KERN-04"]),')
IDX_TAG = ' ("EFFECT-RECEIPT-RESULT-NO-AUTHORITY",["R-EFFECT-08"],"M5 (post-audit addendum)"),'
IDX_PROV = ('def _prov(p):\n'
            '    if p == "addendum":\n'
            '        return {"file": "01-canonical-specification.md", "line_ranges": [],\n'
            '                "note": "post-audit frozen addendum (SEC-001/SEC-002); no source transcription"}\n'
            '    return prov(*p.split(";"))\n'
            '\n'
            'index = {')

EDITS += [
    (BUILDIDX,
     '    if "superseded" in low:\n        return "info-superseded"',
     '    if "resolved-by-addendum" in low:\n        return "resolved-by-addendum"\n'
     '    if "superseded" in low:\n        return "info-superseded"'),
    (BUILDIDX,
     '["R-COMPILE-01","R-COMPILE-02","R-COMPILE-03","R-COMPILE-04","R-COMPILE-05"],prov("37750-37790","9059-9097","39253-39308","1722-1775"),"U-22")',
     '["R-COMPILE-01","R-COMPILE-02","R-COMPILE-03","R-COMPILE-04","R-COMPILE-05","R-COMPILE-06"],prov("37750-37790","9059-9097","39253-39308","1722-1775"),"U-22")'),
    (BUILDIDX,
     '["R-KERN-01","R-KERN-02","R-KERN-03"],prov("6672-6729","19077-19200","9119-9135","39370-39410")',
     '["R-KERN-01","R-KERN-02","R-KERN-03","R-KERN-04","R-KERN-05"],prov("6672-6729","19077-19200","9119-9135","39370-39410")'),
    (BUILDIDX,
     '["R-EFFECT-01","R-EFFECT-02","R-EFFECT-03","R-EFFECT-04","R-EFFECT-05","R-EFFECT-06","R-EFFECT-07"],prov("37891-37922"',
     '["R-EFFECT-01","R-EFFECT-02","R-EFFECT-03","R-EFFECT-04","R-EFFECT-05","R-EFFECT-06","R-EFFECT-07","R-EFFECT-08"],prov("37891-37922"'),
    (BUILDIDX,
     ' ("R-COMPILE-05","S-06","ExecutablePlan constructors private to compiler","39296-39318",SPEC,[],["ror-compiler"],["visibility review"],[]),',
     ' ("R-COMPILE-05","S-06","ExecutablePlan constructors private to compiler","39296-39318",SPEC,[],["ror-compiler"],["visibility review"],[]),\n' + IDX_REQ_COMPILE),
    (BUILDIDX,
     ' ("R-KERN-03","S-10","Authority internals inaccessible to evaluator/runtime","39397-39407",SPEC,[],["ror-kernel"],["visibility + mutation M005-class"],[]),',
     ' ("R-KERN-03","S-10","Authority internals inaccessible to evaluator/runtime","39397-39407",SPEC,[],["ror-kernel"],["visibility + mutation M005-class"],[]),\n' + IDX_REQ_KERN4 + '\n' + IDX_REQ_KERN5),
    (BUILDIDX,
     ' ("R-EFFECT-07","S-12","Completion accounting (charge complete, release reservation, log, resume)","23949-24002",SPEC,[],["ror-runtime"],["conservation tests"],[]),',
     ' ("R-EFFECT-07","S-12","Completion accounting (charge complete, release reservation, log, resume)","23949-24002",SPEC,[],["ror-runtime"],["conservation tests"],[]),\n' + IDX_REQ_EFFECT),
    (BUILDIDX,
     ' ("M018","resume after corrupted receipt",["R-EFFECT-06"]),',
     ' ("M018","resume after corrupted receipt",["R-EFFECT-06"]),\n' + IDX_MUTS),
    (BUILDIDX,
     ' ("SNAPSHOT-COMMIT-INTEGRITY",["R-PERSIST-05"],"M7;M10"),',
     ' ("SNAPSHOT-COMMIT-INTEGRITY",["R-PERSIST-05"],"M7;M10"),\n' + IDX_TAG),
    (BUILDIDX,
     '"R-CAP-09","R-KERN-01","R-KERN-02","R-KERN-03"]),',
     '"R-CAP-09","R-KERN-01","R-KERN-02","R-KERN-03","R-KERN-04","R-KERN-05"]),'),
    (BUILDIDX,
     '"R-DUR-05","R-HOST-01","R-HOST-02","R-HOST-03","R-HOST-04","R-HOST-05"]),',
     '"R-DUR-05","R-HOST-01","R-HOST-02","R-HOST-03","R-HOST-04","R-HOST-05","R-EFFECT-08"]),'),
    (BUILDIDX,
     '"R-COMPILE-05","R-ORDER-03"]',
     '"R-COMPILE-05","R-COMPILE-06","R-ORDER-03"]'),
    (BUILDIDX,
     '"R-KERN-03","R-TRUST-03"]',
     '"R-KERN-03","R-KERN-04","R-KERN-05","R-TRUST-03"]'),
    (BUILDIDX,
     '"R-EFFECT-07","R-ACTOR-01"',
     '"R-EFFECT-07","R-EFFECT-08","R-ACTOR-01"'),
    (BUILDIDX,
     '"R-RECOV-07"],["ror-core"]),',
     '"R-RECOV-07","R-KERN-05"],["ror-core"]),'),
    (BUILDIDX,
     '"R-AREA-NN": "normative requirement/obligation (148)"',
     '"R-AREA-NN": "normative requirement/obligation (152; 148 source-transcribed + 4 post-audit frozen addenda)"'),
    (BUILDIDX,
     '"TAG": "source verification-obligation tags (17)"',
     '"TAG": "source verification-obligation tags (18; 17 frozen-source + 1 post-audit addendum)"'),
    (BUILDIDX,
     '"M0NN": "baseline mutation registry (18)"',
     '"M0NN": "baseline mutation registry (21; 18 baseline + 3 post-audit)"'),
    (BUILDIDX,
     'index = {',
     IDX_PROV),
    (BUILDIDX,
     '"provenance": prov(*p.split(";")),',
     '"provenance": _prov(p),'),
]

# C-77 row: line-based (C-76's row is huge; anchor on its unique line prefix)
CONTRA_C76_PREFIX = "| C-76 |"


def apply_edits(files: dict[Path, str]) -> dict[Path, str]:
    """Apply EDITS (+C-77 line insert) to a {path: text} mapping, in place."""
    for path, find, repl in EDITS:
        n = files[path].count(find)
        if n != 1:
            print(f"ABORT: anchor x{n} (need exactly 1) in {path.name}: {find[:70]!r}")
            sys.exit(2)
        files[path] = files[path].replace(find, repl, 1)
    lines = files[CONTRA].splitlines(keepends=True)
    idx = [i for i, ln in enumerate(lines) if ln.startswith(CONTRA_C76_PREFIX)]
    if len(idx) != 1:
        print(f"ABORT: C-76 anchor rows = {len(idx)} (need 1)")
        sys.exit(2)
    lines.insert(idx[0] + 1, C77 + "\n")
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
    for want, got, what in ((152, n_ob, "obligations"), (152, n_mx, "matrix rows"), (148, n_rc, "records")):
        if got != want:
            print(f"  FAIL: {what} = {got}, expected {want}")
            ok = False
    for m in MARKERS:
        if m not in t01 and m not in t03 and m not in trec and m not in extra:
            print(f"  FAIL: marker {m!r} absent from addendum targets")
            ok = False
    # cross-layer checker on the given paths
    out = subprocess.run(
        [sys.executable, str(CHECKER), "--records", str(records),
         "--spec01", str(spec01), "--matrix", str(matrix)],
        capture_output=True, text=True, check=False).stdout
    first = out.splitlines()[0] if out else ""
    print(f"[{label}] checker: {first}")
    if "152 spec/01 obligations, 152 matrix rows" not in first or "148 records" not in first:
        print("  FAIL: checker parse counts unexpected (vacuous-run guard)")
        ok = False
    bad = [ln for ln in out.splitlines()
           if re.search(r"\[D\d\] (R-COMPILE-06|R-EFFECT-08|R-KERN-04|R-KERN-05)", ln)]
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
    import shutil
    ok = True
    r = subprocess.run([sys.executable, str(builder)], cwd=cwd,
                       capture_output=True, text=True, check=False)
    counts = next((ln for ln in r.stdout.splitlines() if "requirements=" in ln), "")
    print(f"[{label}] index rebuild: {counts or r.stdout[-200:] or r.stderr[-200:]}")
    for want in ("requirements=152", "findings=76", "mutations=21", "tags=18", "sections=24"):
        if want not in counts:
            print(f"  FAIL: index counts missing {want!r}")
            ok = False
    data = _json.loads(index_json.read_text(encoding="utf-8"))
    blob = _json.dumps(data)
    for m in NEW_IDS + ["C-77", "resolved-by-addendum", "M021",
                        "EFFECT-RECEIPT-RESULT-NO-AUTHORITY", "post-audit frozen addendum"]:
        if m not in blob:
            print(f"  FAIL: 10-index.json missing {m!r}")
            ok = False
    st = [f for f in data.get("findings", []) if f.get("id") == "C-77"]
    if not st or st[0].get("status") != "resolved-by-addendum":
        print(f"  FAIL: C-77 status in index = {st[0]['status'] if st else 'absent'!r}")
        ok = False
    return ok


def main() -> int:
    global files_text_cache
    apply_mode = "--apply" in sys.argv

    targets = [SPEC01, MATRIX, CONTRA, VMAP, RECORDS, README, BUILDIDX]
    real = {p: p.read_text(encoding="utf-8") for p in targets}
    files_text_cache = real[CONTRA] + real[VMAP]

    # Precheck: the addendum must be ABSENT on the real tree (evidence), and
    # every anchor must be intact.  Presence => idempotency abort.
    present = [m for m in MARKERS
               if any(m in real[p] for p in targets)]
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
          f"SEC-001/SEC-002 unfrozen (this absence is the finding); "
          f"{len(EDITS) + 1} anchors intact")

    if not apply_mode:
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            files = apply_edits({p: real[p] for p in targets})
            for p in targets:
                (tmp / p.name).write_text(files[p], encoding="utf-8")
            shutil_copy = __import__("shutil").copy
            shutil_copy(SPEC09, tmp / SPEC09.name)
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
    print(f"applied: {len(EDITS) + 1} edits across {len(targets)} files")
    extra = files[CONTRA] + files[VMAP] + files[README]
    ok = check_tree(SPEC01, MATRIX, RECORDS, extra, "post-apply")
    ok = check_index(REPO, BUILDIDX, REPO / "spec" / "10-index.json", "post-apply") and ok
    print("\nAPPLY: " + ("VERIFIED" if ok else "VERIFICATION FAILED — inspect git diff"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
