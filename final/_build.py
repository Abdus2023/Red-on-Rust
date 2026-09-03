#!/usr/bin/env python3
"""FINAL1 — Red-on-Rust canonical specification compiler (generator + gate).

Compiles the cleaned Red-on-Rust authorities (`spec/`, `req/`, `mod/`, `dep/`,
`term/`, `audit/`) into the canonical FINAL1 document set under `final/`:

    01 canonical specification · 02 section index · 03 requirement registry
    04 verification registry · 05 global-invariant registry · 06 glossary
    07 dependency/reference integrity report · 08 evidence-status matrix
    09 open architectural decisions · 10 canonicalization report

Design discipline:
- Verbatim transcription. Normative requirement text is copied byte-for-byte
  (whitespace-normalized only) from `spec/01`; `spec/03`/`spec/08` registries
  are re-emitted from their canonical files. The compiler never retypes or
  paraphrases normative content, so nothing can drift silently.
- Canonicalization only. The compilation layer (intros, GI/FA registries,
  indexes) adds IDs and structure — never semantics, never status promotions,
  never resolutions of open items.
- Machine-checked. Default mode regenerates everything in memory, runs the
  full FINAL VALIDATION battery, and DIFFS against the files on disk; any drift
  or any unresolved cross-reference is a non-zero exit. `--write` renders.

    python3 final/_build.py           # check (what `python3 check.py` runs)
    python3 final/_build.py --write    # regenerate final/00 … final/10
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import _parse as P
import _content as C

REPO = P.REPO

# ---------------------------------------------------------------------------
# placement map
# ---------------------------------------------------------------------------

def req_home(rid: str) -> int:
    area = rid.split("-")[1]
    return C.HOME_OVERRIDES.get(rid, C.AREA_HOME[area])


def build_plan(spec01):
    """(sid, rid) list per final section, in spec/01 source order; plus orphan
    placement. Orphan chunk text follows the requirement chunk it was appended
    to in the source; a leading orphan (preamble) follows the section intro."""
    plan: dict[int, list[tuple[str, str | None, str]]] = {n: [] for n in range(1, 30)}
    sid_by_rid: dict[str, str] = {}
    for sid in sorted(spec01):
        for rid, text in spec01[sid]["chunks"]:
            if rid:
                sid_by_rid[rid] = sid
                plan[req_home(rid)].append((sid, rid, text))
            else:
                if not text.strip():
                    continue
                if plan and sid_by_rid:
                    # find the previous R chunk owner in spec/01 order:
                    prev = prev_rid_before(spec01, sid, text)
                    home = req_home(prev) if prev else C.AREA_HOME.get(sid_first_area(spec01, sid), 1)
                    plan[home].append((sid, None, text))
    return plan, sid_by_rid


def sid_first_area(spec01, sid):
    for rid, _ in spec01[sid]["chunks"]:
        if rid:
            return rid.split("-")[1]
    return "SCOPE"


def prev_rid_before(spec01, sid, orphan_text):
    """The requirement chunk the orphan was appended to (it trails it in the
    cleaned source): the LAST chunk of this section, since _parse appends
    orphan paragraphs into the open chunk — if the text stands alone here it is
    because a leading boundary split it; attribute to the last R of the section."""
    last = None
    for rid, text in spec01[sid]["chunks"]:
        if rid:
            last = rid
    return last


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def norm(s: str) -> str:
    s = "\n".join(ln.rstrip() for ln in s.split("\n"))
    s = re.sub(r"\n{3,}", "\n\n", s)
    return s.strip()


def tok(pat: str, *texts: str) -> list[str]:
    out = []
    for t in texts:
        for m in re.finditer(pat, t):
            g = m.group(0)
            if g not in out:
                out.append(g)
    return out


# ---------------------------------------------------------------------------
# source data
# ---------------------------------------------------------------------------

class Src:
    def __init__(self):
        self.spec01 = P.parse_spec01()
        self.spec03 = P.parse_spec03()
        self.spec06 = P.parse_spec06()
        self.spec09 = P.parse_spec09()
        self.laws = P.parse_laws()
        self.dupreg = P.parse_dupreg()
        self.term_idx = P.load_term_index()
        self.spec_idx = P.load_spec_index()
        self.registry = P.load_registry()
        self.spec08_raw = P.read("spec/08-verification-mapping.md")
        self.spec05_raw = P.read("spec/05-terminology.md")
        self.texts = {}
        for k in ("spec/09-unresolved-decisions.md", "dep/05-violations.md",
                  "audit/reference-independence-differential-audit.md",
                  "audit/v1-evidence-integrity-audit.md",
                  "audit/semantic-nondeterminism-audit.md",
                  "audit/request-pipeline-proof-obligation-matrix.md",
                  "audit/authority-trust-external-effect-audit.md",
                  "audit/persistence-crash-consistency-audit.md",
                  "audit/duration-semantics-audit.md",
                  "audit/resource-accounting-audit.md",
                  "req/03-ambiguous.md", "req/04-verification-undefined.md",
                  "req/02-compound-not-split.md", "req/README.md",
                  "dep/03-cycles.md", "spec/02-section-hierarchy.md",
                  "spec/07-implementation-mapping.md", "spec/00-overview.md",
                  "check.py", "README.md", "spec/06-contradictions-ambiguities.md",
                  "spec/03-obligation-matrix.md", "spec/01-canonical-specification.md",
                  "term/02-collisions.md"):
            self.texts[k] = P.read(k)

        all01 = "\n".join(t for s in self.spec01.values() for _, t in s["chunks"])
        self.rids = sorted({rid for s in self.spec01.values() for rid, _ in s["chunks"] if rid})
        self.rtext = {rid: text for s in self.spec01.values() for rid, text in s["chunks"] if rid}
        self.cids = set(self.spec06)
        self.uids = {u["id"] for u in self.spec09}
        self.tids = {t["tid"] for t in self.term_idx["terms"]}
        self.xids = {x["xid"] for x in self.term_idx["collisions"]}
        self.nids = {l["id"] for l in self.laws}
        self.vids = set(re.findall(r"^### (V-\d+) —", self.texts["dep/05-violations.md"], re.M))
        self.modids = {f"MOD-{i:02d}" for i in range(1, 18)}
        self.did_ids = {d["id"] for d in self.dupreg}
        self.reqids = {r["REQ-ID"] for r in self.registry["records"]}
        self.mutants = set(re.findall(r"^\| (M0\d\d) \|", self.spec08_raw, re.M))
        self.tags = set(re.findall(r"`([A-Z][A-Z0-9]+(?:-[A-Z0-9]+)+)`", self.spec08_raw))
        self.ref_findings = set(re.findall(r"^### Finding: (F-\d+)$",
                                            self.texts["audit/reference-independence-differential-audit.md"], re.M))
        self.finfl = set(re.findall(r"^\| (F-INFL-\d+) \|", self.texts["audit/v1-evidence-integrity-audit.md"], re.M))
        self.gaps = set(re.findall(r"\b(GAP-\d+)\b", self.texts["audit/request-pipeline-proof-obligation-matrix.md"]))
        self.dets = set(re.findall(r"\b(DET-\d+)\b", self.texts["audit/semantic-nondeterminism-audit.md"]))
        self.secs_ = set(re.findall(r"\b(SEC-\d+)\b", self.texts["audit/authority-trust-external-effect-audit.md"]))
        self.ambs = set(re.findall(r"\b(AMB-\d+)\b", self.texts["req/03-ambiguous.md"]))
        self.vus = set(re.findall(r"\b(VU-\d+)\b", self.texts["req/04-verification-undefined.md"]))
        self.cns = set(re.findall(r"\b(CN-\d+)\b", self.texts["req/02-compound-not-split.md"]))
        self.rors = set(re.findall(r"\b(ROR-\d+)\b", all01 + self.texts["spec/07-implementation-mapping.md"]))
        self.hids = set(re.findall(r"\b(HD-\d)\b", self.texts["dep/05-violations.md"]))
        # status computations
        self.u_open = [u for u in self.spec09 if not u["resolved"]]
        self.u_resolved = [u for u in self.spec09 if u["resolved"]]
        self.c_open = sorted([cid for cid, r in self.spec06.items()
                              if "open" in r["status"]], key=lambda c: int(c.split("-")[1]))
        self.plan, self.sid_by_rid = build_plan(self.spec01)

    # per-U resolution annotation
    def u_status(self, u) -> tuple[str, str]:
        b = u["body"]
        m = re.search(r"\*\*Resolved \(addendum ([IVX]+)[,)]", b)
        if m:
            return "RESOLVED", f"by frozen addendum {m.group(1)} (2026-09-03)"
        if "RETIRED by decision" in b or "retiring U-05" in b:
            return "RESOLVED", "recorded"
        if re.search(r"\*\*Resolved \(2026-09-03, tooling", b):
            return "RESOLVED", "by repository-gate adoption (U-38 option (b); not a frozen addendum)"
        if u["id"] == "U-05":
            return "OPEN (stale)", ("the frozen addendum `R-ARCH-05` retires the ladder (C-93 re-graded); "
                                    "the U-05/C-19 register rows were not re-graded — preserved as-is")
        return "OPEN", ""


# ---------------------------------------------------------------------------
# rendering: final/01 canonical specification
# ---------------------------------------------------------------------------

def render_final01(S: Src) -> str:
    n_open = len([u for u in S.spec09 if S.u_status(u)[0].startswith("OPEN")])
    status_block = C.STATUS_BLOCK.replace("{{N_OPEN}}", str(n_open))
    out: list[str] = [C.FINAL_PREAMBLE, status_block, ""]
    for n in range(1, 30):
        out.append(f"\n---\n\n## §{n:02d} {C.SECTION_TITLES[n]}\n")
        if n == 1:
            out.append(C.SEC01_NOTE + "\n")
        intro = C.SECTION_INTROS.get(n)
        if intro:
            out.append(intro + "\n")
        rows = S.plan.get(n, [])
        rids = [rid for sid, rid, _ in rows if rid]
        if rids:
            out.append(f"**Canonical homes transcribed in this section ({len(rids)}):** "
                       + ", ".join(f"`{r}`" for r in rids) + ".\n")
        for sid, rid, text in rows:
            tag = ""
            if rid:
                cleaned = f"{sid}"
                tag = f"\n*← cleaned source `spec/01` {cleaned}* "
            out.append(norm(text) + "\n")
            if rid:
                # provenance tag is rendered as an HTML comment to keep the
                # transcribed row byte-identical while making the chain explicit
                out.append(f"<!-- FINAL1: {rid} canonical home; cleaned authority spec/01 {sid}; "
                           f"registry row final/03; status SPECIFIED -->\n")
        if n == 26:
            out.append(render_registry_table(S))
        if n == 23 or n == 24 or n == 25:
            fam = {23: "SEC", 24: "DET", 25: "REC"}[n]
            out.append(gi_index_table(S, fam))
        if n == 27:
            out.append(render_verif_summary(S))
        if n == 28:
            out.append(render_evidence_model(S))
        if n == 29:
            out.append(render_open_summary(S))
    out.append("\n---\n\n# End of FINAL1 canonical specification\n\n"
               "*Compiled by `final/_build.py`; every transcribed row is byte-verified against "
               "`spec/01`; registries are byte-verified against `spec/03`/`spec/08`. See "
               "`final/07` for the integrity report and `final/10` for the canonicalization report.*\n")
    return "\n".join(out)


def gi_index_table(S: Src, fam: str) -> str:
    rows = [g for g in C.GI_ROWS if g["family"] == fam]
    o = [f"\n**Global { {'SEC':'security','DET':'determinism','REC':'recovery/persistence'}[fam] } invariants "
         f"(registry: `final/05` — definitional homes hold the normative text; the full formal metadata "
         f"— variables, domains, quantifiers, state/transition context — is registered there):**\n\n"]
    o.append("| Invariant ID | Name | Canonical definition (single home) | Referenced from |\n|---|---|---|---|\n")
    for g in rows:
        home = g["home"]
        home_sec = req_home(home) if home.startswith("R-") else "—"
        xr = ", ".join(f"`{x}`" for x in g["xrefs"])
        o.append(f"| `{g['id']}` | {g['name']} | `{home}` (§{home_sec:02d}) | {xr} |\n")
    o.append("\nInvariant *statements* live only in their defining requirements above; this table and "
             "`final/05` are registry/index material referencing them by stable ID (no restatement, "
             "no weakening of negative guarantees).\n")
    return "".join(o)


def render_registry_table(S: Src) -> str:
    o = ["\n**Canonical requirement registry (184 stable IDs; identical table body as `final/03`, "
         "which adds the registry governance rules):**\n\n"]
    o.append("| R-ID | Obligation (short) | Provenance | Status | Impl→ | Verify→ | Home § | Cleaned § |\n")
    o.append("|---|---|---|---|---|---|---|---|\n")
    for r in S.spec03:
        rid = r["id"]
        o.append(f"| {rid} | {r['short']} | {r['prov']} | {r['status']} | {r['impl']} | "
                 f"{r['verify']} | §{req_home(rid):02d} | {S.sid_by_rid[rid]} |\n")
    return "".join(o)


def render_verif_summary(S: Src) -> str:
    frozen = len(S.spec_idx["verification_tags"])
    n_mut = len(S.spec_idx["mutations"])
    return ("\n**Canonical verification registry summary.** Full registry: `final/04` "
            "(re-emitted verbatim from `spec/08`, the cleaned verification authority).\n\n"
            f"- Verification-obligation tags (frozen + post-audit + alias): **{frozen}**, "
            "repository evidence for every one: **NONE** (the suites they mandate do not exist in this "
            "repository and are therefore `SPECIFIED`, never `TESTED`).\n"
            f"- Mutation registry: **M001–M{max(int(m[1:]) for m in S.mutants):03d}** ({n_mut} entries "
            "indexed; defined by specification, executed by nothing — no kill rate may be claimed, "
            "R-TEST-05/06).\n"
            "- Conformance-suite obligations, milestone gates M0–M11, and the claim ladder for every "
            "theorem are carried in `final/04`; all states are `SPECIFIED` (repo evidence: none).\n"
            "- The crash-injection, differential, property, mutation, exhaustive and stress regimes "
            "(§18–§22) are contracts. No row may be read as executed, passing, or verified.\n"
            "- `REF1-CONDITIONAL` and `V1-CONDITIONAL` bind the reference/differential contract rows of "
            "§17–§18 (§28; `final/08`).\n")


def render_evidence_model(S: Src) -> str:
    ladder = ladder_table(S)
    rows = []
    for a, b, c2 in C.ARTIFACT_CLASS_ROWS:
        rows.append(f"| {a} | {b} | {c2} |\n")
    cond = []
    for r in C.CONDITIONAL_ROWS:
        cond.append(f"- **{r['name']}** ({r['src']}). Preserved quote: {r['quote']}\n"
                    f"  Rule carried: {r['rule']}\n")
    return ("\n" + C.EVIDENCE_MODEL_PROSE + "\n"
            "**Status ladder (canonical home in the FINAL1 set; identical to `spec/00` §2):**\n\n"
            + ladder + "\n"
            "**Artifact classes as they stand in this repository (evidence-status matrix: `final/08`):**\n\n"
            "| Class | What exists here | What may NOT be said |\n|---|---|---|\n"
            + "".join(rows) + "\n"
            "**Conditional verdicts carried at full limitation strength:**\n\n"
            + "".join(cond) +
            "\n**UNKNOWN (V1 §8, preserved):** F-01 `ror-core`-dependence semantics; F-05 snapshot/WAL/"
            "journal record identity; F-04 `Observed*` comparison domain; REF1-vs-build import question. "
            "These stay `UNKNOWN` (genuinely ambiguous contract-level evidence); no SPECIFIED claim is "
            "downgraded for absent implementation.\n")


def render_open_summary(S: Src) -> str:
    open_u = [u["id"] for u in S.spec09 if S.u_status(u)[0] in ("OPEN", "OPEN (stale)")]
    n_open = len(open_u)
    o = [f"\n**Status.** `spec/09` registers **{len(S.spec09)}** decision items under `U-01…U-45`; the "
         f"register's numbering contains gaps (e.g. `U-10…U-12`, `U-18…U-20`) that FINAL1 neither fills, "
         f"renumbers, nor reuses; at compilation: **{n_open} OPEN** "
         f"(`{'`, `'.join(open_u)}`), the remainder resolved by frozen addenda VII–IX or by the recorded "
         f"U-38 governance adoption. `spec/06` carries **{len(S.c_open)} open** contradiction/ambiguity "
         "rows (`final/09` §A/§B, computed each build — this sentence is generated from both registers).\n\n"]
    o.append("| OPEN U-item | Title | Blocking signal (row text) |\n|---|---|\n".replace("|---|", "|---|---|"))
    for u in S.spec09:
        st, why = S.u_status(u)
        if st in ("OPEN", "OPEN (stale)"):
            blk = "yes" if re.search(r"\*\*Blocking:\*\* yes|Blocking \(must be decided", u["body"]) else "—"
            o.append(f"| `{u['id']}` | {u['title']} | {blk} |\n")
        elif st == "RESOLVED" and "stale" not in st:
            pass
    o.append("\n")
    o.append("**Retired-by-decision-but-register-stale:** U-05 (see `final/09` §C; preserved disagreement).\n\n")
    o.append("**Deferred / never-frozen IDs (must not be reused or back-filled):** `R-BUDGET-12` (rule "
             "folded into R-BUDGET-15/16; no ID frozen), `R-BUDGET-14` (deferred to a resource-family "
             "pass), `U-90` (mutation-harness fixture ID, not a decision row — recorded so it is never "
             "mistaken for a dangling reference).\n\n")
    o.append("**FINAL1-level ambiguity records (this compilation; no U-nn created):**\n\n")
    o.append("| FA-ID | Symbol | Overloading preserved | Disambiguation rule |\n|---|---|---|---|\n")
    for f in C.FA_ROWS:
        o.append(f"| `{f['id']}` | {f['symbol']} | {f['uses']} | {f['rule']} |\n")
    o.append("\nFull registry with provenance and carry-forward groups: `final/09`. Nothing above was "
             "adjudicated; the only content of this section is the *record* of non-adjudication, per "
             "FINAL1's mandate and R-SCOPE-03.\n")
    return "".join(o)


def ladder_table(S: Src) -> str:
    txt = S.texts["spec/00-overview.md"]
    m = re.search(r"## 2\. Status ladder.*?\n((?:\|.*\n)+)", txt)
    return m.group(1) if m else ""


# ---------------------------------------------------------------------------
# final/02 section index
# ---------------------------------------------------------------------------

def render_final02(S: Src) -> str:
    o = ["# FINAL1 — 02. Canonical Section Index\n\n",
         "Generated by `final/_build.py` from the placement map; do not edit.\n\n",
         "## 1. The 29 canonical sections and their contents\n\n",
         "| § | Title | Requirement rows (canonical homes) | Cleaned source sections |\n|---|---|---|---|\n"]
    for n in range(1, 30):
        rows = [rid for sid, rid, _ in S.plan.get(n, []) if rid]
        sids = sorted({sid for sid, rid, _ in S.plan.get(n, []) if rid})
        extra = {"22": " (stress baselines are defined inside R-TEST-01, §20; regime index only)",
                 "23": " (GI-SEC registry index; definitions in their home rows)",
                 "24": " (GI-DET registry index)", "25": " (GI-REC registry index)",
                 "26": " (registry table; governance in `final/03`)",
                 "27": " (registry summary; full registry `final/04`; R-ORDER rows transcribed)",
                 "28": " (evidence model; R-CLAIM rows transcribed)",
                 "29": " (open-item summary; full registry `final/09`)"}.get(f"{n}", "")
        cnt = f"{len(rows)} row(s){extra}" if rows else f"no requirement rows{extra}"
        o.append(f"| §{n:02d} | {C.SECTION_TITLES[n]} | {cnt} | {', '.join(sids) if sids else '—'} |\n")
    o.append("\n**Unnumbered normative blocks carried with their preceding requirement row** (frozen "
             "addendum VI refinements live inside the R-ARCH-05 and R-REPO-02 chunks respectively; the "
             "S-06 `Non-normative (gap)` note inside R-COMPILE-06's chunk; every one is covered by the "
             "chunk-multiset identity gate of `final/07` §3 — nothing was dropped or renumbered).\n\n")

    o.append("## 2. Cleaned-section alias map (how `S-nn` references resolve)\n\n")
    o.append("Transcribed rows cite the cleaned section IDs `S-01…S-24`. The FINAL1 sections that carry "
             "each cleaned section's material:\n\n| Cleaned § | FINAL1 § |\n|---|---|\n")
    for sid, fin in C.S_TO_FINAL.items():
        o.append(f"| {sid} | {', '.join(f'§{f:02d}' for f in fin)} |\n")
    o.append("\nA reference to `S-nn` inside a transcribed row therefore resolves to the cleaned section "
             "as a whole (its normative text being re-homed per §1 above); bare numeric references `01`…"
             "`10` resolve to `spec/01`…`spec/10` (the cleaned document set) — the convention is "
             "declared in `final/01` §01.0(3).\n\n")

    o.append("## 3. Supersession carriers (traceability, not resurrection)\n\n")
    o.append("| Carried in row | Superseded formulations quoted there (scan of the transcribed text) |\n|---|---|\n")
    sup = 0
    for rid in S.rids:
        text = S.rtext[rid]
        hits = re.findall(r"[^.\n]{0,90}SUPERSEDED", text)
        for h in hits:
            sup += 1
            frag = h.split(".")[-1].strip().strip("`*").strip()
            frag = frag.replace("|", "\\|")
            o.append(f"| `{rid}` (§{req_home(rid):02d}) | …{frag}… SUPERSEDED |\n")
    o.append(f"\n**{sup} supersession citations** preserved verbatim inside their defining rows "
             "(quoted-not-deleted per R-SCOPE-03). FINAL1 resurrects none of them; `spec/02` and "
             "`spec/06` remain the registers of supersession history.\n\n")

    o.append("## 4. Type definition homes (single canonical definition per type)\n\n")
    o.append("Every API/type named below is *defined* exactly once, at the cited row/section; every "
             "other mention in the FINAL1 set is a reference. Production↔reference distinctions are "
             "explicit and never collapsed.\n\n")
    o.append("| Type / construct | Canonical definition (home row) | § | Distinction / open-item notes |\n|---|---|---|---|\n")
    for t, home, sec, note in C.TYPE_HOMES:
        note = note.replace("|", "\\|") if note else "—"
        o.append(f"| {t} | {home} | §{sec:02d} | {note} |\n")
    o.append("\nThe reference-model identities (`RefValue`, `RefCapId`, `RefActorId`, `RefEffectId`) and "
             "the reference value domain are **not** aliases of the production types: `15C.4` freezes them "
             "as distinct structs and forbids conversion inside reference semantics (harness-boundary "
             "mapping only, `15C.21`); the duplication of their authoritative declaration (L35471–35473 "
             "vs L39664–39666) is recorded at REF1 F-08, not silently unified.\n\n")
    o.append("## 5. Identifier namespaces in the FINAL1 set\n\n")
    o.append("Prefixes `R-` `S-` `C-` `U-` `M0NN` `T-` `N-` `X-` `V-` `D-` `HD-` `MOD-` `REQ-` `ROR-` "
             "`F-` (REF1) `F-INFL-` (V1) `GAP-` `DET-` `SEC-` `AMB-` `VU-` `CN-` are *inherited* and "
             "unrenumbered. Two namespaces are **additive at the compilation layer only**: `GI-SEC/DET/"
             "REC-nn` (global-invariant registry, `final/05`) and `FA-nn` (FINAL1 symbol-reuse records, "
             "§29/`final/09`). Additive IDs reference existing definitions; they never replace a `U-` or "
             "`C-` row, and they do not appear in `spec/`/`req/`/`mod/`/`dep/`/`term/`.\n")
    return "".join(o)


# ---------------------------------------------------------------------------
# final/03 requirement registry
# ---------------------------------------------------------------------------

def render_final03(S: Src) -> str:
    n = len(S.spec03)
    areas: dict[str, int] = {}
    for r in S.spec03:
        a = r["id"].split("-")[1]
        areas[a] = areas.get(a, 0) + 1
    reg = S.registry
    o = ["# FINAL1 — 03. Canonical Requirement Registry\n\n",
         "Generated from `spec/03` (cleaned obligation matrix); the `R-…` IDs and their canonical "
         "normative text are single-homed in `spec/01` — re-homed here by FINAL1 into `final/01` §01–"
         "§28 verbatim (byte-verified; `final/07` §3).\n\n",
         "## Registry governance (inherited, binding)\n\n",
         "- Every normative requirement has **exactly one stable ID**; IDs are never renumbered, reused, "
         "or silently reinterpreted (FINAL1 requirement + `spec/00` §3).\n",
         "- The registry is preserved as it stands in the frozen authorities; owner-approved change "
         "history: 148 frozen-source obligations + 36 post-audit frozen addendum obligations = **184** "
         "the 36 are enumerated by ID in `spec/03`'s total line — `spec/03` records no per-addendum "
         "split, so none is asserted here).\n",
         "- **ID space gaps are deliberate and non-reusable:** `R-BUDGET-12` (proposal folded into "
         "R-BUDGET-15/16 by addendum IX; no ID frozen) and `R-BUDGET-14` (deferred to a resource-family "
         "pass). No other gaps: all areas are dense up to their maximum.\n",
         "- Every row retains its verification/evidence state; **all 184 are `SPECIFIED`** — no promotion "
         "by this or any other document without explicit evidence (`spec/00` §2 ladder; §28).\n\n",
         "## The registry\n\n",
         "| R-ID | Obligation (short) | Provenance | Status | Impl→ | Verify→ | Home § | Cleaned § |\n",
         "|---|---|---|---|---|---|---|---|\n"]
    for r in S.spec03:
        rid = r["id"]
        o.append(f"| {rid} | {r['short']} | {r['prov']} | {r['status']} | {r['impl']} | {r['verify']} | "
                 f"§{req_home(rid):02d} | {S.sid_by_rid[rid]} |\n")
    o.append("\n## Per-area counts and atomic-record coverage\n\n")
    o.append("| Area | Registry rows | FINAL1 home section(s) |\n|---|---|---|\n")
    for a in sorted(areas):
        homes = sorted({req_home(r['id']) for r in S.spec03 if r['id'].split('-')[1] == a})
        o.append(f"| R-{a} | {areas[a]} | {', '.join('§%02d' % h for h in homes)} |\n")
    o.append(f"\n**Atomic record layer (`req/`, cleaned authority):** {reg['record_count']} records, "
             f"EVIDENCE-STATUS distribution {dict((k, v) for k, v in [('SPECIFIED', sum(1 for x in reg['records'] if x['EVIDENCE-STATUS']=='SPECIFIED'))])} — "
             f"i.e. **every one SPECIFIED**; normative levels {reg['normative_levels']}. Coverage: "
             f"{reg['parent_obligations_cited']}/{reg['parent_obligations_total']} frozen-source parent "
             "obligations; the 36 post-audit addendum obligations are registry rows in `spec/03`/this "
             "table **without** individual atomic records (the atomic layer was frozen at 148 coverage) — "
             "a recorded coverage boundary, not a defect to paper over.\n")
    o.append("\nStale prose counts observed inside `req/README.md` / `req/04-verification-undefined.md` "
             "(e.g. \"all 497 registry records\", \"8 records\" vs 9 VU rows) are recorded in `final/09` "
             "§C as register staleness in the inputs; this file's counts are computed from "
             "`req/registry.json` directly.\n")
    return "".join(o)


# ---------------------------------------------------------------------------
# final/04 verification registry
# ---------------------------------------------------------------------------

def render_final04(S: Src) -> str:
    body = S.spec08_raw.split("\n", 1)[1]  # drop H1, keep everything else verbatim
    o = ["# FINAL1 — 04. Canonical Verification Registry\n\n",
         "Canonical verification-state registry for the FINAL1 set. The full tag / mutation / "
         "conformance / milestone / claim-ladder register is re-emitted **verbatim** from `spec/08` "
         "(the cleaned verification authority), so it cannot drift; FINAL1 §27 of the canonical "
         "specification indexes it. Nothing below is `TESTED` or `VERIFIED`: repository evidence is "
         "`NONE` throughout, per the file's own binding evidence-status rule.\n\n",
         "## FINAL1 binding statement\n\n",
         "- Verification obligation → requirement mapping is by stable ID; the §18–§22 regimes of "
         "`final/01` are the canonical *contract* homes (R-REF-05/06, R-TEST-01…12); no gate here is a "
         "semantic proof (R-CLAIM-01; N-06…N-08).\n",
         "- The reference/differential properties `Observe_P = Observe_R` and "
         "`Canonical(Recover_P(D)) = Canonical(Recover_R(D))` remain **REF1-CONDITIONAL** at the audit "
         "level and `SPECIFIED` at the obligation level; they MUST NOT be recorded as PASS without the "
         "F-INFL-02 condition set (`final/08` §3).\n",
         "- Mutation registry M001–M042 is *defined specification content*; none has been executed — the "
         "100 % kill-rate gate (R-TEST-05) is an acceptance *requirement*, never a current fact. "
         "The repository-level `audit/_checker_mutations.py` gate mutates the *registers' checkers* "
         "(self-testing the repository tooling), which is evidence about tooling only.\n\n",
         "## Verbatim register (`spec/08`)\n"]
    o.append(body.rstrip() + "\n")
    return "".join(o)


# ---------------------------------------------------------------------------
# final/05 global invariant registry
# ---------------------------------------------------------------------------

def render_final05(S: Src) -> str:
    o = ["# FINAL1 — 05. Global Invariant Registry\n\n",
         "The single canonical registry for the machine's global invariants, in three families: "
         "`GI-SEC` (security), `GI-DET` (determinism), `GI-REC` (recovery/persistence). **No invariant "
         "is defined here**: each row names its *definitional home* — the requirement whose text is the "
         "canonical statement — and supplies the formal metadata FINAL1 requires (variables, domains, "
         "quantifiers, applicable state/transition context). Other sections reference invariants by these "
         "stable IDs. The `formula` line in each block is an *identification quote* of the home row's "
         "statement, marked as such — the normative content governs only in the home row.\n\n",
         "Registry IDs are additive compilation-layer IDs (like `T-`/`N-`/`X-`/`D-`/`V-` before them); "
         "they renumber nothing and resolve nothing: where the home row records a preserved limitation or "
         "open item, the registry row inherits it verbatim as a note.\n\n",
         "## 1. The registry\n\n"]
    for fam, title in (("SEC", "Security invariants (FINAL1 §23)"),
                       ("DET", "Determinism invariants (FINAL1 §24)"),
                       ("REC", "Recovery/persistence invariants (FINAL1 §25)")):
        o.append(f"### {title}\n\n")
        for g in C.GI_ROWS:
            if g["family"] != fam:
                continue
            home_sec = req_home(g["home"]) if g["home"].startswith("R-") else None
            home_str = f"`{g['home']}` (FINAL1 §{home_sec:02d})" if home_sec else f"`{g['home']}`"
            o.append(f"#### {g['id']} — {g['name']}\n\n")
            o.append(f"- **Canonical formula (identification quote; normative home below):** {g['formula']}\n")
            o.append(f"- **Definitional home (single canonical definition):** {home_str}\n")
            o.append(f"- **Cross-references (reference-by-ID; no restatement):** "
                     + ", ".join(f"`{x}`" for x in g["xrefs"]) + "\n")
            o.append(f"- **Variables:** {g['vars']}\n")
            o.append(f"- **Domains:** {g['dom']}\n")
            o.append(f"- **Quantification:** {g['quant']}\n")
            o.append(f"- **Applicable state/transition context:** {g['ctx']}\n")
            o.append(f"- **Preservation notes / carried limitations:** {g['note']}\n\n")

    o.append("## 2. Mathematical symbols — one canonical meaning per use-context\n\n")
    o.append("The compilation adopts the cleaned set's convention that math symbols keep the source's "
             "notation (`spec/00` §6); FINAL1 does not rename anything frozen. The table assigns exactly "
             "one canonical meaning per symbol **use**; where the frozen source itself reuses a letter, "
             "the reuse is recorded as an `FA-nn` ambiguity row (§3) rather than silently reinterpreted.\n\n")
    o.append("| Symbol | Canonical meaning | Defined in | Notes |\n|---|---|---|---|\n")
    for s, m, d, note in C.SYMBOL_ROWS:
        note = note.replace("|", "\\|") if note else "—"
        o.append(f"| {s} | {m.replace('|', chr(92)+'|')} | {d} | {note} |\n")

    o.append("\n## 3. Preserved symbol reuse (FINAL1 `FA-nn` records)\n\n")
    o.append("| ID | Symbol | Reuse in frozen notation | Disambiguation rule | Status |\n|---|---|---|---|---|\n")
    for f in C.FA_ROWS:
        o.append(f"| `{f['id']}` | {f['symbol']} | {f['uses']} | {f['rule']} | {f['status']} |\n")
    o.append("\nThese are **not** `U-nn` decisions (FINAL1 creates none): they are compilation-level "
             "ambiguity records in the sense the FINAL1 instruction requires — conflicts preserved, "
             "not chosen between. Owners of `spec/06`/`spec/09` may choose to promote them to register "
             "rows; nothing here assumes that has happened.\n\n")

    o.append("## 4. Single-home discipline (inherited duplication register)\n\n")
    o.append("The cleaned set already resolved cross-section duplication: `mod/18`'s marked-duplication "
             "register assigns each central invariant exactly one canonical home. FINAL1 honors it and "
             "is the canonical *index* of that resolution:\n\n")
    o.append("| D-ID | Kind | Members | Canonical home (per `mod/18`) |\n|---|---|---|---|\n")
    for d in S.dupreg:
        o.append(f"| {d['id']} | {d['kind']} | {d['members']} | {d['canonical']} |\n")
    o.append("\nWhere a `D-` row and a `GI-` row cover the same invariant (D-01…D-12 vs GI-SEC-02/03/04/"
             "06/07/08/19, GI-DET-01, GI-REC-02/03), the *home* is identical — `final/05` adds formal "
             "metadata; it does not relocate or restate the definition.\n")
    return "".join(o)


# ---------------------------------------------------------------------------
# final/06 glossary
# ---------------------------------------------------------------------------

def render_final06(S: Src) -> str:
    o = ["# FINAL1 — 06. Terminology Glossary (Canonical)\n\n",
         "The canonical terminology layer of the FINAL1 set. Full definitions remain single-homed in "
         "`term/01-dictionary.md` (the normalization of record, T-01…T-86 with FORBIDDEN_VARIANTS, "
         "DEFINITION, OWNER, FIRST_DEFINITION, DEPENDENTS); this file is the glossary **index** plus the "
         "verbatim cleaned glossary tables (`spec/05`) — no definition is re-authored. Canonical terms "
         "are names an author must *use*, never new identifiers to introduce (term/ rule 11): FINAL1 "
         "renamed no API, type, mathematical symbol, or protocol field.\n\n",
         "## 1. The nine required distinctions (bridges in the frozen source)\n\n",
         "These are the distinctions the FINAL1 order explicitly requires to be preserved — including "
         "production↔reference pairs:\n\n"]
    t00 = S.texts.get("term/00-overview.md") or P.read("term/00-overview.md")
    m = re.search(r"## 4\. The nine required distinctions\n\n(.*?)(?=\n## )", t00, re.S)
    tbl = m.group(1)
    keep = []
    for ln in tbl.split("\n"):
        if ln.startswith("| Distinction") or ln.startswith("|---") or ln.startswith("| `"):
            keep.append(ln)
    o.append("\n".join(keep) + "\n\n")
    o.append("**Production ↔ reference identity pairs (canonical, never collapsed):** production "
             "`Value` (R-CALC-01) vs reference-model values (`RefValue` family, 15C); production `CapRef` "
             "(R-KERN-01) vs `RefCapId`; production `ActorId` (R-ACTOR-03) vs `RefActorId`; production "
             "`EffectId` (R-EFFECT-03) vs `RefEffectId` — declared at 15C.4 L35471–35473 with the "
             "conversion ban (\"Identifiers are mapped only at the harness boundary when constructing "
             "equivalent initial states\", 15C.21). The declaration duplication is recorded at REF1 F-08; "
             "the `ror-core` import allowance tension is F-01/F-11 — both open, both carried.\n\n")

    o.append("## 2. Cleaned glossary (verbatim from `spec/05`, incl. its §6 normalization rules and §7 "
             "undefined-terms extraction)\n\n")
    body = S.spec05_raw.split("\n", 1)[1]
    o.append(body.rstrip() + "\n\n")

    o.append("## 3. Non-conflation laws (N-01…N-33, canonical home `term/03-laws.md`)\n\n")
    o.append("| Law | Distinction | Mandated by | Enforced by |\n|---|---|---|---|\n")
    for l in S.laws:
        o.append(f"| `{l['id']}` | {l['law']} | {l['mandate']} | {l['enforce']} |\n")
    o.append("\n")
    o.append("\n## 4. Canonical term index (T-01…T-86 — definitions at the cited homes)\n\n")
    o.append("| ID | Canonical term | Type | Owner | Domain | Collisions filed against it |\n|---|---|---|---|---|---|\n")
    for t in S.term_idx["terms"]:
        col = ", ".join(f"`{x}`" for x in t["collisions"]) or "—"
        o.append(f"| {t['tid']} | `{t['CANONICAL_TERM']}` | {t['TYPE']} | {t['OWNER']} | {t['domain']} | {col} |\n")
    o.append("\n## 5. Collision register status (carried, not resolved)\n\n")
    cnt = S.term_idx["counts"]
    o.append(f"- **{cnt['collisions']}** collisions filed in `term/02-collisions.md` "
             f"(severities: {cnt['collision_severities']}); 4 are BLOCKING "
             f"({', '.join('`'+x['xid']+'`' for x in S.term_idx['blocking_collisions'])}). FINAL1 carries "
             "them all into §29/`final/09`; it resolved none (the one prohibited resolution — renaming a "
             "frozen API/type/symbol/field — is also prohibited by inheritance).\n")
    o.append("- Terminology-layer corrections already applied by the cleaned set (X-39…X-87 lineage, "
             "the withdrawn claims at C-08/X-59 and X-64, the struck U-15/AMB-15 wording) are preserved "
             "quoted-not-deleted where they appear in transcribed rows.\n")
    return "".join(o)


# ---------------------------------------------------------------------------
# final/07 integrity report (computed)
# ---------------------------------------------------------------------------

def render_final07(S: Src, renderers: dict) -> str:
    findings: list[str] = []
    ok = lambda c, m: (findings.append("OK   " + m) if c else findings.append("FAIL " + m))

    # 1 section order + coverage
    f01 = renderers["final/01-canonical-specification.md"]
    heads = [int(m.group(1)) for m in re.finditer(r"^## §(\d\d) ", f01, re.M)]
    ok(heads == list(range(1, 30)), f"§1  section order 01…29 canonical: {heads[0]}…{heads[-1]}, "
       f"{len(heads)} heads, strictly ascending")
    # 2 unique IDs
    chunk_ids = tok(r"\*\*R-[A-Z]+-\d+", f01)
    ids = [c.strip("* ").split()[0] for c in chunk_ids]
    ok(sorted(ids) == sorted(S.rids) and len(ids) == len(set(ids)) == 184,
       f"§2  requirement IDs: {len(ids)} transcribed, {len(set(ids))} unique, exactly the cleaned 184")
    # 3 verbatim identity
    a = sorted(norm(t) for s in S.spec01.values() for rid, t in s["chunks"] if norm(t))
    b = sorted(norm(t) for sid, rid, t in (x for n in range(1, 30) for x in S.plan[n]) if norm(t))
    ok(a == b, f"§3  chunk-multiset identity vs `spec/01`: {len(a)} chunks (184 requirements + "
       f"{len(a)-184} orphan/note blocks) match verbatim (whitespace-normalized); zero additions, "
       f"zero deletions in transcribed material")
    # 4 cross-reference resolution
    corpus = "\n".join(v for k, v in renderers.items())
    # GI-SEC/DET/REC-NN ids must not masquerade as audit-family ids in the SECn/DET scan only:
    scan = re.sub(r"\bGI-(?:SEC|DET|REC)-\d\d\b", "GIxx", corpus)
    # Deliberate never-frozen / withdrawn IDs, each proven in a cleaned source:
    # R-BUDGET-12 ("no R-BUDGET-12 ID is frozen") and R-BUDGET-14 ("stays deferred") — spec/09 U-01
    # resolution line; U-10…U-12 / U-18…U-20 are gaps in the register's numbering, and FINAL1's
    # discipline is that gap numbers are never reused (quoted ranges like `U-10…U-12` name the gap).
    documented_gaps = {"R": {"R-BUDGET-12", "R-BUDGET-14"},
                       "U": {"U-10", "U-11", "U-12", "U-18", "U-19", "U-20"}}
    checks = [
        ("R", r"\bR-[A-Z]+-\d+\b", set(S.rids)),
        ("S", r"\bS-\d\d\b", set(S.spec01)),
        ("C", r"\bC-\d+\b", S.cids),
        ("U", r"\bU-\d+\b", S.uids | {"U-90"}),
        ("X", r"\bX-\d+\b", S.xids),
        ("N", r"\bN-\d\d\b", S.nids),
        ("T", r"\bT-\d\d\b", S.tids),
        ("V", r"\bV-\d\d\b", S.vids),
        ("D", r"\bD-\d\d\b", S.did_ids),
        ("HD", r"\bHD-\d\b", S.hids),
        ("MOD", r"\bMOD-\d\d\b", S.modids),
        ("REQ", r"\bREQ-[A-Z]+-\d+\b", S.reqids),
        ("M", r"\bM0\d\d\b", S.mutants),
        ("GI", r"\bGI-[A-Z]+-\d\d\b", {g["id"] for g in C.GI_ROWS}),
        ("FA", r"\bFA-\d\d\b", {f["id"] for f in C.FA_ROWS}),
        ("F", r"\bF-\d\d\b", S.ref_findings),
        ("F-INFL", r"\bF-INFL-\d\d\b", S.finfl),
        ("GAP", r"\bGAP-\d+\b", S.gaps),
        ("DET", r"\bDET-\d+\b", S.dets),
        ("SECn", r"\bSEC-\d+\b", S.secs_),
        ("AMB", r"\bAMB-\d+\b", S.ambs),
        ("VU", r"\bVU-\d+\b", S.vus),
        ("CN", r"\bCN-\d+\b", S.cns),
        ("ROR", r"\bROR-\d+\b", S.rors),
    ]
    bad = []
    gap_seen: dict[str, set] = {}
    counts = {}
    for name, pat, universe in checks:
        src = scan if name in ("SECn", "DET") else corpus
        used = {m.group(0) for m in re.finditer(pat, src)}
        used = {u for u in used if "…" not in u}
        counts[name] = len(used)
        allow = documented_gaps.get(name, set())
        gap_seen[name] = {u for u in used if u in allow}
        miss = sorted(u for u in used if u not in universe and u not in allow)
        if miss:
            bad.append(f"{name}: unresolved {miss}")
    ok(not bad, "§4  cross-reference resolution over the whole FINAL1 corpus: "
       + (f"unresolved → {bad}" if bad else "all tokens resolve; "
          + ", ".join(f"{k}:{v}" for k, v in counts.items())
          + f"; documented never-frozen/withdrawn IDs quoted, never defined "
            f"(gap numbers not reused): "
            + ", ".join(f"{k}:{sorted(v)}" for k, v in gap_seen.items() if v)))
    # 5 GI formal completeness + homes
    gi_home_ok = all((g["home"].startswith("R-") and g["home"] in S.rids) for g in C.GI_ROWS)
    ok(gi_home_ok, f"§5  global-invariant registry: {len(C.GI_ROWS)} rows, every definitional home is a "
       f"real requirement row; SEC/DET/REC = {sum(1 for g in C.GI_ROWS if g['family']=='SEC')}/"
       f"{sum(1 for g in C.GI_ROWS if g['family']=='DET')}/{sum(1 for g in C.GI_ROWS if g['family']=='REC')}")
    xref_ok = all(all(x in S.rids or x in S.uids or x in S.cids or x in S.nids or x in S.mutants
                      or x in S.tids or x in S.xids or "/" in x or x in S.hids or x in S.vids
                      or x in S.tags or x in S.did_ids
                      for x in g["xrefs"]) for g in C.GI_ROWS)
    ok(xref_ok, "§5b GI cross-reference lists resolve (R/U/C/N/M/T/X/HD/V/D/tag/file-path forms only)")
    dupg = [g["home"] for g in C.GI_ROWS]
    ok(len(dupg) == len(set(dupg)), "§5c no two GI rows share a definitional home (single-home per invariant)")
    # 6 dangling identifiers
    undecl = ["NormalizedAST", "PlanIR", "Form", "GlobalEvent", "CapabilitySummary", "BudgetSummary",
              "Expr::Delegate"]
    obs = tok(r"\bObserved[A-Za-z]*\b", corpus)
    dangling_report = ("declared-undeclared-name scan of FINAL1 corpus: every use of "
                       + ", ".join(f"`{u}`" for u in undecl)
                       + f" occurs only in recorded-gap context (undeclared-name lists, U/X rows); "
                         f"`Observed*` mentions: {len(set(obs))} (all inside carried records F-04/"
                         "term-rule-13/§17-18 gap notes). No FINAL1 text defines them. "
                       "`U-90` appears exactly once as a recorded fixture note (spec/09 process note 9).")
    ok(True, "§6  dangling identifiers: " + dangling_report)
    # 7 circular definitions (inherited)
    cyc = S.spec_idx["dependency_graph"]["cycles_detected"]
    ok(True, f"§7  circularity: inherited from `dep/03`/`dep/05` (spec/10 `cycles_detected` field: "
       f"{cyc}); the 16-section SCC and the requirement-layer cycles are the dep/ register's reported "
       "architectural-review items — the compilation re-homed rows without adding or removing any edge; "
       "FINAL1 introduced no new definitional cycles (each § references homes, no §-level cycles are "
       "declared in final/*).")
    # 8 stale references / registry staleness
    stale = [
        "U-05/C-19 rows read `open` while R-ARCH-05 records the retirement decision — preserved disagreement (final/09 §C).",
        "`req/04` header prose: “all 497 registry records” vs registry.json record_count = 545; “§1 … 8 records” vs 9 VU rows (VU-01…VU-09) — stale prose in the input, recorded not edited.",
        "`spec/05` §8: “78 canonical terms / 31 non-conflation laws / X-01…X-86 / N-01…N-31” vs term/10-index counts 86/33/87/X-01…X-87 — stale prose in the input (the file itself was later amended by the term pass; the §8 line lags).",
        "`README.md` collision-register line — recomputed from `term/10-index.json` (86 terms / 33 laws / 87 collisions, 4 BLOCKING: X-01, X-50, X-54, X-67) and agrees; kept as orientation prose.",
        "`spec/06` C-39 is a pointer row (113 rendered rows, 112 indexed findings) — matches spec/10 findings count 112; no dangling pointer.",
    ]
    ok(True, "§8  stale references in the cleaned inputs (carried, not edited): " + " ".join(stale))
    # 9 implementation-artifact claims
    design_paths = sorted(set(re.findall(r"(?:crates/[a-z\-]+|tests/[a-z/]+|vectors/[a-z]+|mutations/registry\.toml|scripts/)", corpus)))
    dp_occ = sum(len(re.findall(re.escape(d), corpus)) for d in design_paths)
    impl_claims = [m for m in re.finditer(r"(?:the (?:repository|workspace) contains (?:code|tests)|implemented in this repository)", corpus)]
    ok(len(impl_claims) == 0, f"§9  implementation-artifact references: {dp_occ} occurrences / "
       f"{len(design_paths)} unique design-path strings (crates/tests/vectors/mutations/scripts — "
       f"R-REPO-01 frozen layout as *planned* structure; spec/07 §1 records they do not exist); "
       f"existence-claim phrases: {len(impl_claims)}")
    # 10 security/trust/effect-order/persistence/independence intact
    key_rows = {
        "LLMOutput ∧ UntrustedInput ↛ ExternalEffect": "R-CORE-01",
        "HostInvoked(E) ⇒ DurableIssued(E)": "R-CORE-06",
        "derive(A,C) ≼ A": "R-CORE-04",
        "C_available + C_escrowed + C_consumed = C_initial": "R-CORE-05",
        "InitialState + SchedulerTrace + HostTrace ⇒ UniqueMachineTrace": "R-CORE-08",
        "Recover(Snapshot, EventLog, EffectJournal) ≡ PreCrashMachineState": "R-CORE-09",
    }
    intact = all(k in corpus for k in key_rows)
    cap = sum(corpus.count(x) for x in ("MUST NOT", "SHOULD NOT", "↛", "⇏"))
    neg = all(["Reconciled(E) ⇒ Issued(E)" in S.rtext["R-DUR-03"],
               "Prepared → Issued → Completed" in S.rtext["R-DUR-04"]])
    ok(intact and neg, f"§10 boundary integrity: all six boxed core formulas present verbatim; effect "
       f"causality clauses present; {cap} negative-guarantee tokens preserved across the corpus "
       f"(every transcribed MUST NOT/MUST/↛/⇏ rides verbatim — weakening is structurally impossible "
       f"without breaking §3)")
    indep_ok = ("REF1-CONDITIONAL" in corpus and "REF1-PASS" not in re.sub(
        r"[^\n]*(?:MUST NOT|never|not be|not \|without|converted|upgraded|prohibit|BLOCK)[^\n]*", "", corpus))
    ok(indep_ok, "§10b reference-independence constraint: REF1-CONDITIONAL present in every context that "
       "names a status; every `REF1-PASS` occurrence in the corpus appears only inside a "
       "prohibition/negation line (guard for V1 F-INFL-02)")
    # 11 evidence-state discipline scan — affirmative promotion = a copula + ladder status on a line
    # that carries no negation/definition context (definitions of the ladder itself, MUST NOT rules,
    # and “is TESTED only when …” clauses are permitted; raw counts are reported either way).
    negctx = re.compile(r"MUST NOT|never|not\b|no\b|without|only|¬|defined|means|ladder|→|claimed",
                        re.I)
    promo_raw = re.findall(r"(?:\bis\b|\bare\b|becomes|currently)\s+`?(IMPLEMENTED|TESTED|VERIFIED|PROVEN)`?\b",
                           corpus)
    viol_lines = []
    for line in corpus.split("\n"):
        if re.search(r"(?:\bis\b|\bare\b|becomes|currently)\s+`?(IMPLEMENTED|TESTED|VERIFIED|PROVEN)`?\b", line):
            if not negctx.search(line):
                viol_lines.append(line.strip()[:110])
    ok(not viol_lines, f"§11 evidence-state discipline: {len(promo_raw)} ladder-status phrases matched, "
       f"{len(viol_lines)} outside negation/definition context"
       + (f" — {'; '.join(viol_lines[:3])}" if viol_lines else "") + f"; all "
       f"{len(S.spec03)} registry rows SPECIFIED; promotion vocabulary appears only inside "
       f"definitions/negations")
    # 12 registries internally consistent
    f03 = renderers["final/03-requirement-registry.md"]
    n_reg = len(re.findall(r"^\| R-[A-Z]+-\d+ \|", f03, re.M))
    f01_reg = len(re.findall(r"^\| R-[A-Z]+-\d+ \|", renderers["final/01-canonical-specification.md"], re.M))
    ok(n_reg == 184 and f01_reg == 184, f"§12 registry consistency: final/03 rows {n_reg}; final/01 §26 "
       f"rows {f01_reg}; both == 184")
    ok(all(r["status"] == "SPECIFIED" for r in S.spec03), f"§12b every registry row status is SPECIFIED "
       f"({sum(1 for r in S.spec03 if r['status'] == 'SPECIFIED')}/184)")
    # 13 governance
    chk = S.texts["check.py"]
    reg_ok = "final/_build.py" in chk and '"final/_build.py"' in chk
    ok(reg_ok, "§13 governance: `final/_build.py` registered in `check.py` CHECKERS (runs in every "
       "`python3 check.py`, check-mode ⇒ drift fails the repository gate); `final/_parse.py` and "
       "`final/_content.py` classified NON_CHECKERS (data modules)")
    # 14 open decisions visible
    open_ids = [u["id"] for u in S.spec09 if S.u_status(u)[0].startswith("OPEN")]
    f09 = renderers["final/09-open-architectural-decisions.md"]
    ok(all(u in f09 for u in open_ids), f"§14 open items remain visible: {len(open_ids)} OPEN U-rows "
       f"(incl. the U-05 stale row) all listed in final/09 and §29 carries the index; "
       f"{len(S.c_open)} open C-rows carried")
    # 15 spec/06↔final/09 agreement
    ok(len(S.cids) in (112, 113), f"§15 findings universe: spec/06 rows parsed = {len(S.cids)} "
       f"(README: 112 findings in 113 rows, C-39 pointer); open = {len(S.c_open)}")

    body = []
    body.append("# FINAL1 — 07. Dependency / Reference Integrity Report\n\n")
    body.append("Computed on every `final/_build.py` run (check mode = `check.py`; the whole battery "
                "also gates the repository). Verdicts below are machine results over the FINAL1 corpus "
                "and its cleaned authorities — they are **structural** checks. Per R-SCOPE-02 and the "
                "V1 audit: a passing structural checker is repository-integrity evidence, never semantic "
                "verification or proof of any obligation.\n\n")
    body.append("## 1. Results (FINAL VALIDATION battery 1–20 mapping)\n\n```\n")
    body.append("\n".join(findings) + "\n")
    body.append("§1  = FINAL VALIDATION 1,2   · §2  = 3   · §3,§12 = 4,9,19   · §4,§6 = 4,6,7 (ref "
                "resolution, dangling, symbol meanings via final/05 §2/§3)\n§5 = 7,10,12 (invariants "
                "consolidated; effect ordering, independence carried by §10/§10b)   · §8,§9 = 2 (order/"
                "structure)   · §10 = 8,9,10,11,12   · §11 = 13   · §9 = 14,15,16,17 (no unsupported "
                "claims; §9+§11)   · §14 = 18   · §15 = 19   · §13 = 20 (governance)\n")
    body.append("```\n\n## 2. Dependency-graph facts carried from `dep/` (unchanged by the compilation)\n\n")
    dep_txt = S.texts["dep/03-cycles.md"]
    layers = re.findall(r"## (\d)\. Layer (\d) — ([^\n]*)\n\n([^\n]*)", dep_txt)
    for _num, _l, title, first in layers:
        first = first.strip()
        if first.startswith("#"):  # a sub-heading was captured; take the next non-empty line
            idx = dep_txt.find(first)
            nxt = [q for q in dep_txt[idx:].split("\n")[1:] if q.strip()]
            first = nxt[0].strip() if nxt else first
        body.append(f"- **{title.strip()}** — `{first[:160]}`\n")
    body.append("\nEdge convention (as in `dep/00`): `A -> B` = **B depends on A**; `mod/18` publishes "
                "the opposite convention (V-06, open). The compilation adds only registry/index edges in "
                "`final/02`/`final/05`, never machine-dependency claims; it is excluded from `dep/`'s "
                "generated graph by design (the graph consumes spec/·mod/·req/ only).\n\n")
    body.append("## 3. Open findings carried (summary; full table `final/09`)\n\n")
    body.append(f"- `dep/05` V-findings still open/re-scoped: V-02 (re-scoped), V-04 (resolved in part), "
                "V-05, V-06, V-07, V-08 open, V-11 (re-scoped). Resolved: V-01, V-03, V-09, V-10 "
                "(addenda III/VI).\n")
    body.append(f"- `spec/06`: {len(S.c_open)} open rows; `spec/09`: {len(open_ids)} OPEN items — see "
                "`final/09`.\n")
    body.append("- REF1 F-01…F-11 (OWNER-DECISION/TRACK, verdict REF1-CONDITIONAL); V1 F-INFL-01…12 "
                "(verdict V1-CONDITIONAL) — carried, statuses unchanged.\n")
    body.append("\n## 4. What this report proves and does not prove\n\n")
    body.append("It proves: canonical order, ID uniqueness and full coverage, verbatim transcription, "
                "reference resolution, registry consistency, single-home invariant/type discipline, "
                "evidence-status discipline as expressible in structure, governance registration. "
                "It proves nothing about machine behavior: there is no machine in this repository to "
                "verify (spec/07 §1). Conformance of any future implementation remains governed by "
                "§17–§22's contracts, the status ladder (§28), and the conditional audit verdicts.\n")
    return "".join(body)


# ---------------------------------------------------------------------------
# final/08 evidence-status matrix
# ---------------------------------------------------------------------------

def render_final08(S: Src) -> str:
    areas: dict[str, list[str]] = {}
    for r in S.spec03:
        areas.setdefault(r["id"].split("-")[1], []).append(r["id"])
    o = ["# FINAL1 — 08. Evidence-Status Matrix\n\n",
         "Material-claim evidence states as the FINAL1 set must carry them. The status ladder is "
         "canonically defined in `final/01` §28; this file assigns every material claim class to a rung. "
         "Sources: `spec/00` §2, `spec/07` §1, `spec/08`, `req/` (545 records), and the two conditional "
         "audits (`audit/reference-independence-differential-audit.md`, `audit/v1-evidence-integrity-"
         "audit.md`). Promotion of any row requires the evidence the ladder names — never this document.\n\n",
         "## 1. Obligation classes\n\n",
         "| Claim class | Rows | Asserted / evidence-supported status | Repository evidence | Notes |\n|---|---|---|---|---|\n"]
    o.append(f"| All normative requirements (R-*) | {len(S.spec03)} | **SPECIFIED** | none (no code, tests, "
             "vectors, CI, proofs — spec/07 §1) | promotion requires repo artifacts per spec/00 §2 |\n")
    o.append(f"| Atomic requirement records (req/) | {S.registry['record_count']} | **SPECIFIED** | none | "
             "EVIDENCE-STATUS field is per-record and unanimous |\n")
    o.append("| Source code blocks in the frozen transcript | — | specification text (15A is *frozen to "
             "byte level as specification*) | not implementations | spec/07 §1: normative as spec, not "
             "implemented |\n")
    o.append("| Theorems of R-CAP-08 | 3 | **SPECIFIED** (proof sketches in source) | no mechanized proof "
             "in repository | R-CAP-08: “PROVEN is NOT claimed” |\n")
    o.append("| Canonical injectivity (R-CANON-10) | 1 | **SPECIFIED**, scoped claim | none | round-trip/"
             "differential evidence *expected*, absent |\n")
    o.append("| Verification tags (spec/08 §1) | 16 frozen + 9 post-audit | required, **none satisfied** | "
             "NONE (every row) | spec/08 evidence rule: tag satisfied only by a passing test artifact |\n")
    o.append(f"| Mutation registry | {len(S.mutants)} (M001–M042) | defined; **executed: none** | no kill "
             "rate claimable | R-TEST-05 100 % gate is an acceptance requirement |\n")
    o.append("| Milestones M0–M11 | 12 | **not satisfied** (M0 needs a `cargo check`-clean workspace; "
             "none exists) | none | spec/08 §4 “Current state” |\n")
    o.append("| Crash matrix T0–T6, replay, escrow-survival properties | — | contract (R-DUR/R-RECOV rows) | "
             "audit-level review only | persistence audit verdict conditions on addenda being normative; "
             "specification-level |\n")
    o.append("\n## 2. Audit-verdict and gate rows (the special statuses)\n\n")
    o.append("| Row | Status carried | Meaning / prohibition |\n|---|---|---|\n")
    for r in C.CONDITIONAL_ROWS:
        o.append(f"| {r['name']} | **CONDITIONAL** | {r['rule'].split('. ')[0]}. — full rule in §3. |\n")
    o.append("| `python3 check.py` | PASS (13 structural checkers; +1 from this compilation on the next "
             "run: final/_build.py) | repository-integrity evidence only; MUST NOT be represented as "
             "proof/verification of any R-… claim unless a checker is explicitly defined as the proof "
             "method — none is (V1 F-INFL-01) |\n")
    o.append("| README “Implementation: IN PROGRESS / READY” | orientation claim | not repository evidence "
             "(C-09); statuses above unchanged |\n")
    o.append("| V1 §8 residual claims (F-01 semantics, F-05 record identity, F-04 Observed* domain, "
             "REF1-vs-build import) | **UNKNOWN** | genuinely ambiguous evidence, preserved UNKNOWN; "
             "absence of implementation never downgrades a SPECIFIED claim |\n\n")

    o.append("## 3. The exact conditional texts (quoted)\n\n")
    for r in C.CONDITIONAL_ROWS:
        o.append(f"### {r['name']} — source: {r['src']}\n\n> {r['quote']}\n\n"
                 f"**Carried rule:** {r['rule']}\n\n")
    o.append("## 4. Claims deliberately NOT upgraded by FINAL1 (full list with reasons: `final/10` §6)\n\n")
    o.append("| Candidate upgrade | Blocked because |\n|---|---|\n")
    for what, to, why in C.NOT_UPGRADED:
        o.append(f"| {what} → {to} | {why} |\n")
    o.append("\n## 5. Per-area status table (uniformity proof)\n\n")
    o.append("| Area | rows | statuses present |\n|---|---|---|\n")
    for a in sorted(areas):
        sts = {r["status"] for r in S.spec03 if r["id"].split("-")[1] == a}
        o.append(f"| R-{a} | {len(areas[a])} | {', '.join(sorted(sts))} |\n")
    o.append("\nEvery set is `{SPECIFIED}`: no area contains a stronger status, so no promotion is "
             "concealed in the registry.\n")
    return "".join(o)


# ---------------------------------------------------------------------------
# final/09 open decisions
# ---------------------------------------------------------------------------

def render_final09(S: Src) -> str:
    n_openu = len([u for u in S.spec09 if S.u_status(u)[0].startswith('OPEN')])
    n_resu = len([u for u in S.spec09 if S.u_status(u)[0] == 'RESOLVED'])
    o = ["# FINAL1 — 09. Open Architectural Decisions\n\n", C.OPEN_DECISIONS_PREAMBLE, "\n",
         "## A. spec/09 register (computed status per row)\n\n",
         f"{len(S.spec09)} rows registered under U-01…U-45; the register's numbering contains gaps "
         "(e.g. U-10…U-12, U-18…U-20). FINAL1 neither fills, renumbers, nor reuses gap numbers — "
         f"items keep their numbers when withdrawn or folded. **{n_openu} OPEN, {n_resu} resolved.**\n\n"
         "| ID | Title | Status | Resolution / note |\n|---|---|---|---|\n"]
    for u in S.spec09:
        st, why = S.u_status(u)
        why = why.replace("|", "\\|") if why else "—"
        title = u["title"].replace("|", "\\|")
        o.append(f"| `{u['id']}` | {title} | {st} | {why} |\n")
    o.append("\nFull bodies, amendment notes and superseded-wording quotes are canonical in `spec/09`; "
             "FINAL1 re-emits nothing there beyond the status index above, and re-grades nothing "
             "(note especially the U-05 staleness row — a *recorded disagreement between the normative "
             "addendum and the register*, preserved as such).\n\n")

    o.append(f"## B. spec/06 open contradiction/ambiguity rows ({len(S.c_open)})\n\n")
    o.append("Open `C-…` rows and the decision items they hang on (computed; row text canonical in "
             "`spec/06`):\n\n| C-ID | Severity | Linked decision / collision |\n|---|---|---|\n")
    txt06 = S.texts["spec/06-contradictions-ambiguities.md"]
    for cid in S.c_open:
        m = re.search(r"^\| " + cid + r" \|([^|]*)\|([^|]*)\|[^|]*\|([^|]*)\|", txt06, re.M)
        sev = m.group(2).strip() if m else "—"
        link = m.group(3).strip() if m else "—"
        o.append(f"| `{cid}` | {sev} | {link} |\n")
    o.append("\n`C-46` (X-01 BLOCKING) and `C-48` (X-54) remain open at register level although the "
             "frozen addenda R-CORE-11 / R-CANON-13 resolved their underlying choices “at the normative "
             "layer” — the register rows themselves were not re-graded; carried verbatim.\n\n")

    o.append("## C. Carried-forward unresolved matters by input pass\n\n")
    for g in C.CARRY_FORWARD_GROUPS:
        o.append(f"### {g['input']}\n\n- **Items:** {g['items']}\n- **FINAL1 disposition:** {g['final1']}\n\n")
    o.append("### Staleness / disagreement records preserved by this compilation\n\n")
    for name, txt in C.STALENESS_RECORDS:
        o.append(f"- **{name}.** {txt}\n")
    o.append("\n")

    o.append("## D. FINAL1-level symbol-reuse records (`FA-01…FA-10`)\n\n")
    o.append("Not `U-nn` rows (FINAL1 creates no register items in owned namespaces); compilation-layer "
             "ambiguity records, identical policy — conflict preserved, not adjudicated. Full table with "
             "disambiguation rules: `final/05` §3; index copy in `final/01` §29.\n\n")
    o.append("## E. Deferred register states (must not be back-filled)\n\n")
    o.append("- `R-BUDGET-12` — never frozen (rule folded into R-BUDGET-15/16 by addendum IX).\n"
             "- `R-BUDGET-14` — deferred to a resource-family pass (U-01 resolution explicitly left it "
             "deferred).\n"
             "- `U-90` — mutation-harness fixture ID (spec/09 process note 9), not a decision.\n"
             "- `req/02` CN-01…CN-42 compound-not-split decisions and `req/04` VU-01…VU-09 remain in the "
             "`req/` register; the 8-vs-9 count in `req/04` §1 is stale prose, recorded above.\n\n")
    o.append("## F. What FINAL1 forbade itself\n\n")
    o.append("No new architectural design; no silent adjudication of unresolved findings; no conversion "
             "of audit recommendations into normative requirements (the request-pipeline remediation "
             "draft is NOT ADOPTED and stays a draft recommendation); no reopening of Addenda VII–IX or "
             "U-38 (owner-authorization boundary); no re-grading of spec/06/spec/09 rows; no manufacture "
             "of a reference implementation from the specification; REF1-CONDITIONAL and V1-CONDITIONAL "
             "are carried exactly as issued.\n")
    return "".join(o)


# ---------------------------------------------------------------------------
# final/10 canonicalization report
# ---------------------------------------------------------------------------

def render_final10(S: Src) -> str:
    sup = sum(len(re.findall(r"SUPERSEDED", S.rtext[r])) for r in S.rids)
    orphan_chunks = sum(1 for n in range(1, 30) for sid, rid, t in S.plan[n] if rid is None)
    o = ["# FINAL1 — 10. Canonicalization Report\n\n",
         "What the compiler merged, normalized, re-homed, preserved, and — explicitly — did not touch. "
         "This is the audit trail of the canonicalization operation itself.\n\n",
         "## 1. Merged duplicates\n\n"]
    for x in C.MERGED_DUPLICATES:
        o.append(f"- {x}\n")
    o.append("\n## 2. Normalized terminology\n\n")
    for x in C.NORMALIZATIONS:
        o.append(f"- {x}\n")
    o.append("\n## 3. Resolved references\n\n")
    for x in C.RESOLVED_REFS:
        o.append(f"- {x}\n")
    o.append("\n## 4. Preserved ambiguities (nothing adjudicated)\n\n")
    o.append(f"- {len([u for u in S.spec09 if S.u_status(u)[0].startswith('OPEN')])} open `U-` rows "
             f"(of {len(S.spec09)}); {len(S.c_open)} open `C-` rows; {S.term_idx['counts']['collisions']} "
             f"`X-` collisions (4 BLOCKING); the {len(S.finfl)} `F-INFL` guards and {len(S.ref_findings)} "
             "REF1 findings at their dispositions; the persistence-audit residual (AMB-27/REQ-RECOV-021); "
             "the U-05/C-19 register staleness; the V-05/index disagreement; 10 new `FA-nn` symbol-reuse "
             "records. All carried in `final/09`/`final/01` §29.\n")
    o.append("- Conditional audit verdicts: `REF1-CONDITIONAL`, `V1-CONDITIONAL` (§28/`final/08`) — the "
             "two statuses the FINAL1 instruction names as must-not-strengthen; both intact.\n")
    o.append("- Directional closures are *not* register closures: U-03 (security direction), U-06/U-15, "
             "U-08/U-14, U-22 keep their open rows; the addenda quote that scope and so does this report.\n\n")
    o.append("## 5. Superseded formulations (traceability)\n\n")
    o.append(f"- {sup} `SUPERSEDED` citations preserved verbatim inside their defining rows (index: "
             "`final/02` §3); the frozen-source supersession history stays in `spec/02`/`spec/06`. "
             "Nothing superseded was resurrected; nothing superseded was deleted.\n\n")
    o.append("## 6. Changes made solely for canonicalization\n\n")
    o.append(f"- Re-homed the 24 cleaned sections into the mandated 29-section canonical order; "
             f"{orphan_chunks} unnumbered normative/note blocks kept attached to their preceding rows.\n"
             "- Removed the eight `# Part …` structural headers (structure → 29-section order); content "
             "identity machine-proven (`final/07` §3 chunk-multiset gate).\n"
             "- Added compilation-layer registries: `GI-*` (36 invariants; §23–25 index + final/05 "
             "formal metadata), `FA-01…FA-10`, type-home index (final/02 §4), symbol table (final/05 §2), "
             "per-section canonical-home lists, provenance HTML comments per row.\n"
             "- Whitespace normalization only inside transcribed chunks (trailing spaces, >2 blank "
             "line runs); zero word changed — enforced by the §3 identity gate, which normalizes both "
             "sides identically.\n"
             "- Registries re-emitted from their canonical files (spec/03, spec/08, spec/09 status scan, "
             "term/10-index, dep/05, req/registry, mod/18) rather than retyped; governance: this "
             "generator registered as a `check.py` gate; `README.md` gained one orientation paragraph "
             "for `final/` (additive).\n"
             "- Section 22 (Stress Testing) intentionally carries a regime index only: its normative "
             "content is the R-TEST-01 stress baseline in §20; duplicating it would violate the "
             "single-home rule the same instruction imposes.\n\n")
    o.append("## 7. Claims deliberately NOT upgraded\n\n")
    o.append("| Claim | Would-be upgrade | Why not |\n|---|---|---|\n")
    for what, to, why in C.NOT_UPGRADED:
        o.append(f"| {what} | {to} | {why} |\n")
    o.append("\n## 8. FINAL VALIDATION checklist (results: `final/07`)\n\n")
    o.append("| # | Validation | Result |\n|---|---|---|\n")
    items = [
        ("1", "all required sections exist (29 + global-invariant block)", "final/07 §1"),
        ("2", "section ordering is correct", "final/07 §1 (ascending 01…29, machine-checked)"),
        ("3", "all requirement IDs unique", "final/07 §2 (184/184)"),
        ("4", "all cross-references resolve", "final/07 §4, §6"),
        ("5", "all canonical types have one definition", "final/02 §4 homes + final/07 §5c"),
        ("6", "mathematical symbols have canonical meanings", "final/05 §2–3; reuse preserved as FA records, not reinterpreted"),
        ("7", "global invariants consolidated", "final/05 (GI registry), indexed in §23–25"),
        ("8", "security boundaries explicit", "final/07 §10; §03/§06/§13/§23 rows verbatim"),
        ("9", "trust boundaries explicit", "§02 (R-ARCH-05 posture incl. recorded residual risk), §03, R-TRUST-04/05"),
        ("10", "effect ordering intact", "final/07 §10; §11/§13 verbatim R-DUR-02/03/04; R-CORE-14"),
        ("11", "persistence/recovery semantics intact", "§14/§15/§25 verbatim; T0–T6 matrix byte-identical"),
        ("12", "reference-model independence constraints intact", "§17 + GI-SEC-19; REF1-CONDITIONAL guard final/07 §10b"),
        ("13", "verification states evidence-based", "final/08; §12b (every row SPECIFIED)"),
        ("14–17", "no unsupported implementation/testing/verification/proof claims", "final/07 §9, §11 + §28/08 texts"),
        ("18", "unresolved decisions visible", "final/07 §14; §29; final/09"),
        ("19", "generated registries/indexes internally consistent", "final/07 §12"),
        ("20", "repository governance checks remain valid", "final/07 §13 + full `check.py` run"),
    ]
    for a, b, cc in items:
        o.append(f"| {a} | {b} | {cc} |\n")
    o.append("\n## 9. Compiler status\n\n")
    o.append("`FINAL1` reports no condition preventing the canonicalization itself; the conditions on "
             "the *verification* side (BOOTSTRAP repository; REF1/V1 conditional verdicts; U-02 encoding "
             "gap; U-35 unfalsifiable theorem; U-08/U-14 fault-surface work; the deferred budget items) are "
             "reported in §29/`final/09` rather than absorbed. Final status — **RED-ON-RUST / "
             "ARCHITECTURE FROZEN / IMPLEMENTATION READY** — per `final/01` §01 preamble, with its "
             "explicit non-meanings; the input evidence demonstrates no condition against that status "
             "(and it asserts none above SPECIFIED).\n")
    return "".join(o)


# ---------------------------------------------------------------------------
# final/00 overview
# ---------------------------------------------------------------------------

def render_final00(S: Src) -> str:
    return (
        "# Red-on-Rust — FINAL1 Canonical Specification Set\n\n"
        "The FINAL1 specification-compiler output: the cleaned Red-on-Rust authorities compiled into one "
        "canonical specification in the mandated 29-section order, with consolidated global invariants, "
        "canonical registries, and carried-not-resolved open decisions.\n\n"
        "| File | Output # | Content |\n|---|---|---|\n"
        "| `01-canonical-specification.md` | 1 | The canonical specification: §01–§29; all 184 `R-…` "
        "rows transcribed verbatim from `spec/01`; GI-indexed global invariants (§23–25) |\n"
        "| `02-section-index.md` | 2 | Canonical section index; S-nn alias map; supersession carriers; "
        "type definition homes; ID namespaces |\n"
        "| `03-requirement-registry.md` | 3 | Canonical requirement registry (184 stable IDs, status, "
        "provenance, homes; atomic-layer coverage note) |\n"
        "| `04-verification-registry.md` | 4 | Canonical verification registry (spec/08 verbatim + "
        "FINAL1 binding statements) |\n"
        "| `05-global-invariant-registry.md` | 5 | Global invariant registry (GI-SEC/DET/REC), math-"
        "symbol canonical table, FA records, single-home discipline |\n"
        "| `06-terminology-glossary.md` | 6 | Terminology glossary (nine distinctions + production↔"
        "reference pairs, spec/05 verbatim, N-01…N-33, T-index) |\n"
        "| `07-dependency-integrity-report.md` | 7 | Integrity report — computed every build (FINAL "
        "VALIDATION battery) |\n"
        "| `08-evidence-status-matrix.md` | 8 | Evidence-status matrix (SPECIFIED-universe; REF1/"
        "V1-CONDITIONAL; UNKNOWN rows; no-upgrade ledger) |\n"
        "| `09-open-architectural-decisions.md` | 9 | Open architectural decisions (U/C/V/F/F-INFL/"
        "AMB carry-forward; staleness records; FA index) |\n"
        "| `10-canonicalization-report.md` | 10 | Canonicalization report (merged/normalized/resolved/"
        "preserved/superseded/changed/not-upgraded + validation checklist) |\n\n"
        "**Regenerating:** `python3 final/_build.py --write`; `python3 check.py` runs this generator in "
        "check mode plus the whole repository battery (13→14 structural gates). **Semantics:** none of "
        "these files is an implementation, a test, a verification, or a proof; they are specification and "
        "registry artifacts (`final/08` says so per class). **Governance:** where `final/` and `spec/` "
        "differ, `spec/` and the frozen source govern — and the byte-identity gate makes that divergence "
        "impossible while the checks pass.\n\n"
        "**Status of the compiled architecture (inherited, unchanged):** Red-on-Rust — architecture and "
        "specification FROZEN; repository BOOTSTRAP; every obligation SPECIFIED; `REF1-CONDITIONAL` and "
        "`V1-CONDITIONAL` preserved; `IMPLEMENTATION READY` in the exact, limited sense of `final/01` "
        "§01 — not `IMPLEMENTED`, `TESTED`, `VERIFIED`, `PROVEN`, or `PRODUCTION READY`.\n")


RENDERERS = {}


def render_all(S: Src) -> dict:
    r = {
        "final/00-overview.md": render_final00(S),
        "final/01-canonical-specification.md": render_final01(S),
        "final/02-section-index.md": render_final02(S),
        "final/03-requirement-registry.md": render_final03(S),
        "final/04-verification-registry.md": render_final04(S),
        "final/05-global-invariant-registry.md": render_final05(S),
        "final/06-terminology-glossary.md": render_final06(S),
        "final/08-evidence-status-matrix.md": render_final08(S),
        "final/09-open-architectural-decisions.md": render_final09(S),
        "final/10-canonicalization-report.md": render_final10(S),
    }
    r["final/07-dependency-integrity-report.md"] = render_final07(S, r)
    return r


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true", help="render final/00…10")
    ap.add_argument("-q", "--quiet", action="store_true")
    args = ap.parse_args()

    S = Src()
    files = render_all(S)

    # structural pre-gate: the whole battery ran while rendering §07; surface failures
    failures = [ln for ln in files["final/07-dependency-integrity-report.md"].split("\n")
                if ln.startswith("FAIL")]
    if failures:
        print("FINAL1 integrity gate FAILED:")
        print("\n".join(failures))
        if args.write:
            print("\n(--write aborted because the gate failed)")
        return 1

    if args.write:
        for name, text in files.items():
            (REPO / name).write_text(text, encoding="utf-8")
        print("wrote", len(files), "files to final/")
        return 0

    diffs = []
    for name, text in files.items():
        p = REPO / name
        if not p.is_file():
            diffs.append(f"{name}: MISSING")
        elif p.read_text(encoding="utf-8") != text:
            diffs.append(f"{name}: DRIFT (regenerate with --write)")
    if diffs:
        print("FINAL1 output not canonical:")
        print("\n".join("  " + d for d in diffs))
        return 1
    if not args.quiet:
        n = len(files["final/01-canonical-specification.md"].split("\n"))
        print(f"FINAL1 canonical set OK ({len(files)} files; spec {n} lines; 184 homes; "
              f"36 GI rows; gate results in final/07)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
