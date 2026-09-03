"""scripts/spec/_common.py — shared machinery for the controlled specification pipeline.

WHAT THIS IS
------------
The single set of primitives the pipeline stages (S0–S7) share: authority
loaders, deterministic rendering helpers, provenance construction and the
fail-closed error type.  It is a **data module** (classified NON_CHECKER in
`check.py`): it checks nothing by itself, it makes the stages able to be
strict.

AUTHORITY CHAIN (this module adds no normative content anywhere)
----------------------------------------------------------------
    frozen source            Red-on-Rust.md            (S0 input; bytes are authority)
    cleaned canonical text   spec/01                   (normative text home of the R-… chunks)
    canonical registry       spec/03 (+ spec/02, spec/06, spec/08, spec/09)
    compiled registries      req/, reg/, mod/, dep/, term/, state/
        |
        v
    scripts/spec/*           deterministic generators/validators  <-- THIS PACKAGE
        |
        v
    build/spec/*             derived artifacts (NOT committed, NOT authority)
        |
        v
    spec/0[0-5]-*/ pointers  durable human-readable pointers to derived projections

Every figure a stage publishes is re-derived from the authority files listed
above.  Nothing here is parsed from a projection of a projection: `reg/`,
`spec/10`, `state/` and `mod/` JSON files are read as *derived-artifact
cross-checks*, and disagreement with their markdown authority is a hard failure
(`StageFailure`), never a silent re-base and never a choice of one value over
another (§5 authority order: source > registry > generator > derived).

DETERMINISM CONTRACT (§4.2 of the transformation instruction)
--------------------------------------------------------------
This module MUST NOT read wall-clock time, locale, network state, filesystem
modification times, hash randomization, or `os.environ` other than
`PYTHONHASHSEED` (which is only reported, never used to change behaviour).
Iteration order is always explicit (`sorted`, source order, or a registry's
declared order).  Rendering is byte-stable: JSON with `sort_keys=True`,
`ensure_ascii=False`, LF endings, explicit UTF-8, no trailing whitespace
carried from prose.  `pipeline_render_hash` lets a gate prove that two
independent runs produced identical bytes.

EVIDENCE DISCIPLINE
-------------------
A passing stage is repository-integrity evidence only.  No function here can
promote a status: the only status vocabulary accepted is the frozen ladder, and
the pipeline's ceiling is `SPECIFIED` because that is what the authorities
record (spec/00 §2).  Provenance and canonical hashes carry no timestamps.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
from pathlib import Path

# ---------------------------------------------------------------------------
# paths
# ---------------------------------------------------------------------------
HERE = Path(__file__).resolve().parent            # <repo>/scripts/spec
SCRIPTS = HERE.parent                              # <repo>/scripts
REPO = SCRIPTS.parent                              # <repo>

SOURCE_REL = "Red-on-Rust.md"                      # S0 input (frozen normative source)
BUILD_DIRNAME = "build/spec"                       # derived output (gitignored)

# ---------------------------------------------------------------------------
# identity / version
# ---------------------------------------------------------------------------
PIPELINE_NAME = "redonrust-spec-pipeline"
PIPELINE_VERSION = "1.0.0"                         # bump on ANY semantic change to rendering
PIPELINE_MODE = "specification-processing (pre-M0)"

# Frozen source of record, as declared by the authorities (spec/00, spec/10 meta).
SOURCE_EXPECTED_LINES = 42312
SOURCE_EXPECTED_SHA256 = ("2aeb9940665f6ef27bbba9895889e93b8be8c1ba9f5ff0558f2b95fee07a25eb")

# Optional strictness (see §12 "reject unresolved contradictions where required"):
# False = carry-and-disclose, the policy `spec/01` itself publishes under; True =
# canonicalization refuses to run while an open BLOCKING/MAJOR row bears on it.
STRICT_CANONICALIZATION = False

# §21 pre-M0 boundary: this package exists only to process the specification.
FORBIDDEN_DURING_TRANSFORMATION = [
    "Rust runtime implementation", "CEK implementation", "capability kernel implementation",
    "actor implementation", "scheduler implementation", "host implementation",
    "persistence implementation", "effect implementation", "agent runtime implementation",
]

# Status ladder (spec/00 §2) — the pipeline can only ever *carry* these.
STATUS_LADDER = ["SPECIFIED", "IMPLEMENTED", "TESTED", "VERIFIED", "PROVEN"]
EVIDENCE_CEILING = "SPECIFIED"

# §8 normative classes.  The repository's own vocabularies are the ones
# recognised; the §8 names are mapped onto them so no second classification
# system is invented (§20: extend governance, do not compete with it).
NORMATIVE_CLASSES = ["NORMATIVE", "DESCRIPTIVE", "EXPLANATORY", "EXAMPLE",
                     "HISTORICAL", "AMBIGUOUS"]
# req/00 §field NORMATIVE-LEVEL vocabulary (canonical, from reg/_compile.py)
LEVEL_VOCAB = ["MUST", "MUST NOT", "SHOULD", "SHOULD NOT", "MAY", "IS",
               "NON-NORMATIVE", "AMBIGUOUS"]
# spec/06 resolution-status vocabulary (canonical homes: spec/06 header)
FINDING_STATUSES = ["resolved-by-later-text", "superseded", "open",
                    "resolved-by-addendum", "INFO"]
# Severity vocabulary from spec/06 header
FINDING_SEVERITIES = ["BLOCKING", "MAJOR", "MINOR", "INFO"]

# ---------------------------------------------------------------------------
# fail-closed machinery (§19)
# ---------------------------------------------------------------------------


class StageFailure(Exception):
    """Any stage failure.  Raised, never collected-and-ignored: a stage that
    fails MUST prevent publication of the affected canonical artifact."""


class Finding:
    """An audit finding (§11).  Fields are exactly the required set; a finding
    with an empty `proposed_resolution` is *complete* — the pipeline proposes
    nothing it has not been given by an authority."""

    __slots__ = ("finding_id", "category", "severity", "source_refs", "artifacts",
                 "description", "proposed_resolution", "authority_required", "status")

    def __init__(self, finding_id, category, severity, description, *,
                 source_refs=(), artifacts=(), proposed_resolution="",
                 authority_required=True, status="open"):
        self.finding_id = finding_id
        self.category = category
        self.severity = severity
        self.source_refs = list(source_refs)
        self.artifacts = list(artifacts)
        self.description = description
        self.proposed_resolution = proposed_resolution
        self.authority_required = bool(authority_required)
        self.status = status

    def to_dict(self) -> dict:
        return {
            "affected_artifacts": sorted(self.artifacts),
            "authority_required": self.authority_required,
            "category": self.category,
            "description": self.description,
            "finding_id": self.finding_id,
            "proposed_resolution": self.proposed_resolution,
            "severity": self.severity,
            "source_refs": sorted(self.source_refs),
            "status": self.status,
        }


def fail(stage: str, msg: str) -> "StageFailure":
    return StageFailure(f"[{stage}] FAIL-CLOSED: {msg}")


# ---------------------------------------------------------------------------
# deterministic rendering primitives
# ---------------------------------------------------------------------------


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_text(text: str) -> str:
    return "sha256:" + sha256_hex(text.encode("utf-8"))


def sha256_bytes(b: bytes) -> str:
    return "sha256:" + sha256_hex(b)


def render_json(obj) -> str:
    """Canonical JSON bytes-as-string: sorted keys, no ascii escaping, LF, one
    trailing newline.  Stable across runs, hosts, and locales."""
    return json.dumps(obj, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def render_json_compact(obj) -> str:
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":")) + "\n"


def md_escape(text: str) -> str:
    """Escape literal pipes so a table row keeps the header's cell count —
    `req/_validate.py` §7d treats an unescaped `|` in a cell as corruption."""
    return text.replace("|", "\\|").replace("\n", " ")


def table(rows, header) -> str:
    """Deterministic markdown table. `rows` is a list of already-escaped cells."""
    out = ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
    for r in rows:
        out.append("| " + " | ".join(md_escape(str(c)) for c in r) + " |")
    return "\n".join(out) + "\n"


def provenance(stage: str, *, inputs=(), generators="", **extra) -> dict:
    """Provenance header shared by every generated artifact (§4.1).

    Deliberately timestamp-free: the identity of an artifact is
    (source hash, pipeline version, stage, input hashes).  A wall-clock stamp
    would make reproducible output impossible, so it appears in no semantic
    content and in no canonical hash."""
    p = {
        "pipeline": PIPELINE_NAME,
        "pipeline_version": PIPELINE_VERSION,
        "pipeline_mode": PIPELINE_MODE,
        "stage": stage,
        "generator": generators or "scripts/spec/pipeline.py",
        "source": {
            "path": SOURCE_REL,
            "sha256": None,
            "note": "filled by snapshot (S0); identity of the frozen bytes",
        },
        "inputs": [{"path": rel, "sha256": digest} for rel, digest in inputs],
        "timestamp_present": False,
        "timestamp_reason": ("timestamps would destroy reproducibility; excluded from "
                            "semantic content and canonical hashes (§4.1)"),
        "authority_note": ("DERIVED ARTIFACT — not a normative source. Where this file and its "
                           "authorities disagree, the authority governs and the gate fails."),
    }
    p.update(extra)
    return p


def pipeline_render_hash(name: str, files: dict) -> str:
    """A single deterministic digest over a rendered artifact set.

    `files` maps relative path -> text.  Because keys are sorted and content is
    byte-exact, two runs agreeing on this hash is proof of determinism and (for
    a re-run over its own output) idempotence — no timestamps involved."""
    h = hashlib.sha256()
    h.update(PIPELINE_NAME.encode("utf-8"))
    h.update(b"\0" + PIPELINE_VERSION.encode("utf-8"))
    h.update(b"\0" + name.encode("utf-8"))
    for rel in sorted(files):
        h.update(b"\0" + rel.encode("utf-8") + b"\0")
        h.update(files[rel].encode("utf-8"))
    return "sha256:" + h.hexdigest()


# ---------------------------------------------------------------------------
# authority loaders — every stage reads through these
# ---------------------------------------------------------------------------


def read_text(repo: Path, rel: str) -> str:
    p = repo / rel
    if not p.is_file():
        raise StageFailure(f"[loader] authority file missing: {rel}")
    return p.read_text(encoding="utf-8")


def read_bytes(repo: Path, rel: str) -> bytes:
    p = repo / rel
    if not p.is_file():
        raise StageFailure(f"[loader] authority file missing: {rel}")
    return p.read_bytes()


def load_json(repo: Path, rel: str):
    return json.loads(read_text(repo, rel))


_CRLF = re.compile(r"\r\n?")
# spec/01 chunks: a line starting `**R-AREA-NN.**` (optionally qualified, e.g.
# `**R-CORE-11 (title — frozen addendum).**`).  A chunk runs to the next chunk
# start, section/part heading, or `---` rule; anything in between (unnumbered
# normative blocks, S-nn.n subheads) belongs to the preceding requirement —
# the convention `final/02` §1 declares.
_RCHUNK_HEAD = re.compile(r"^\*\*(R-[A-Z]+-\d+)([^*]*)\.\*\*")
_SECTION_HEAD = re.compile(r"^## (S-\d{2}) (.*)$")
_PART_HEAD = re.compile(r"^# (Part .*)$")
_LINEREF = re.compile(r"L(\d{1,5})(?:\s*[–-]\s*(\d{1,5}))?")
# spec/03 rows: | R-… | short | provenance | Status | impl | verify |
_OBLIG_ROW = re.compile(r"^\| (R-[A-Z]+-\d+) \| ([^|]*) \| ([^|]*) \| ([^|]*) \| ([^|]*) \| ([^|]*) \|$")
_FINDING_ROW = re.compile(r"^\| (C-\d{2,3}) \|")
_U_HEAD = re.compile(r"^### (U-\d{2}) — (.*)$", re.M)


def split_cells(line: str) -> list[str]:
    """Split a markdown table row on UNescaped pipes (repo convention: a literal
    pipe inside a cell is written `\\|`)."""
    parts = re.split(r"(?<!\\)\|", line.strip())
    if parts and parts[0].strip() == "":
        parts = parts[1:]
    if parts and parts[-1].strip() == "":
        parts = parts[:-1]
    return [p.strip().replace("\\|", "|") for p in parts]


class Ctx:
    """All authorities, loaded and parsed once.  Every field records where it
    came from so a stage never cites an unregistered input."""

    def __init__(self, repo: Path):
        self.repo = Path(repo).resolve()
        self.warnings: list[str] = []
        self._load_source()
        self._load_spec01()
        self._load_spec02()
        self._load_spec03()
        self._load_spec06()
        self._load_spec08()
        self._load_spec09()
        self._load_derived()

    # -- S0 input ----------------------------------------------------------
    def _load_source(self):
        self.source_bytes = read_bytes(self.repo, SOURCE_REL)
        text = _CRLF.sub("\n", self.source_bytes.decode("utf-8"))
        self.source_text = text
        self.source_lines = text.split("\n")
        if self.source_lines and self.source_lines[-1] == "":
            self.source_lines = self.source_lines[:-1]
        self.source_sha256 = sha256_hex(self.source_bytes)
        self.source_line_count = len(self.source_lines)
        self.source_byte_count = len(self.source_bytes)
        self.turns = [int(m.group(1)) for m in
                      re.finditer(r"^## \[(\d+)\]", text, re.M)]

    def source_range(self, start: int, end: int) -> str:
        """1-based inclusive line range of the frozen source, read verbatim."""
        if not (1 <= start <= end <= self.source_line_count):
            raise StageFailure(f"[provenance] line range L{start}-L{end} outside source "
                               f"(1..{self.source_line_count})")
        return "\n".join(self.source_lines[start - 1:end])

    # -- spec/01: cleaned normative text home -----------------------------
    def _load_spec01(self):
        txt = read_text(self.repo, "spec/01-canonical-specification.md")
        self.spec01_text = txt
        lines = txt.split("\n")
        # line-indexed boundaries (no offset arithmetic, no greedy slicing):
        part_of, sec_of, sec_title = {}, {}, {}
        cur_part, cur_sec, cur_title = "", "", ""
        for i, line in enumerate(lines):
            pm = _PART_HEAD.match(line)
            if pm:
                cur_part = pm.group(1).strip()
            sm = _SECTION_HEAD.match(line)
            if sm:
                cur_sec, cur_title = sm.group(1), sm.group(2).strip()
            part_of[i], sec_of[i], sec_title[i] = cur_part, cur_sec, cur_title
        starts = [i for i, line in enumerate(lines) if _RCHUNK_HEAD.match(line)]
        self.chunks: list[dict] = []
        for n, s in enumerate(starts):
            end = len(lines)
            stop = starts[n + 1] + 1 if n + 1 < len(starts) else len(lines)
            for j in range(s + 1, stop):
                line = lines[j]
                if (_RCHUNK_HEAD.match(line) or line.startswith("## ")
                        or line.startswith("# ") or line.strip() == "---"):
                    end = j
                    break
            body = "\n".join(lines[s:end]).rstrip("\n").rstrip()
            sid = sec_of[s]
            m = _RCHUNK_HEAD.match(lines[s])
            self.chunks.append({
                "id": m.group(1),
                "qualifier": (m.group(2) or "").strip(),
                "section": sid,
                "section_title": sec_title[s],
                "part": part_of[s],
                "line": s + 1,
                "end_line": end,
                "text": body,
                "source_refs": line_refs_of(body),
                "sha256": sha256_text(body),
            })
        self.spec01 = {c["id"]: c for c in self.chunks}
        if len(self.spec01) != len(self.chunks):
            raise StageFailure("[spec/01] duplicate requirement chunk IDs in the normative text home")
        # chunks with no R-id (normative blocks carried with a preceding row)
        self.spec01_orphans = len(_SECTION_HEAD.findall(txt))  # bookkeeping only

    # -- spec/02: section hierarchy (S-01..S-24) --------------------------
    def _load_spec02(self):
        txt = read_text(self.repo, "spec/02-section-hierarchy.md")
        self.sections: list[dict] = []
        current_part = ""
        for line in txt.split("\n"):
            pm = re.match(r"^## (Part [IVX]+ .*)$", line)
            if pm:
                current_part = pm.group(1).strip()
                continue
            if not line.startswith("| S-"):
                continue
            cells = split_cells(line)
            if len(cells) < 4 or not re.match(r"^S-\d{2}$", cells[0]):
                continue
            self.sections.append({
                "id": cells[0],
                "title": cells[1],
                "part": current_part,
                "provenance": cells[2],
                "superseded": cells[3],
                "line_ranges": line_refs_of(cells[2]),
            })
        self.section_ids = [s["id"] for s in self.sections]
        self.section_by_id = {s["id"]: s for s in self.sections}
        # canonical section order is spec/01's own document order of S- headings
        self.section_order = [m.group(1) for m in
                              re.finditer(r"^## (S-\d{2}) ", self.spec01_text, re.M)]
        if len(self.section_order) != len(set(self.section_order)):
            raise StageFailure("[spec/02] duplicate section heading in spec/01")

    # -- spec/03: canonical registry --------------------------------------
    def _load_spec03(self):
        txt = read_text(self.repo, "spec/03-obligation-matrix.md")
        self.obligations: dict[str, dict] = {}
        order: list[str] = []
        for line in txt.split("\n"):
            if not line.startswith("| R-"):
                continue
            cells = split_cells(line)
            if len(cells) < 6 or not re.match(r"^R-[A-Z]+-\d+$", cells[0]):
                continue
            rid = cells[0]
            if rid in self.obligations:
                raise StageFailure(f"[spec/03] duplicate registry row for {rid}")
            self.obligations[rid] = {
                "id": rid, "short": cells[1], "provenance": cells[2],
                "status": cells[3], "impl": cells[4], "verify": cells[5],
            }
            order.append(rid)
        self.obligation_order = order

    # -- spec/06: findings register ---------------------------------------
    def _load_spec06(self):
        txt = read_text(self.repo, "spec/06-contradictions-ambiguities.md")
        self.findings: dict[str, dict] = {}
        for line in txt.split("\n"):
            if not _FINDING_ROW.match(line):
                continue
            cells = split_cells(line)
            if len(cells) < 6:
                raise StageFailure(f"[spec/06] malformed C- row ({len(cells)} cells): {cells[0]}")
            cid, title, severity, srcs, status, desc = cells[:6]
            u = None
            um = re.search(r"U-(\d{2})", status)
            if um:
                u = "U-%s" % um.group(1)
            self.findings[cid] = {
                "id": cid, "title": title, "severity": severity,
                "source_refs": line_refs_of(srcs), "sources_cell": srcs,
                "status": status, "u_ref": u, "description": desc,
            }

    # -- spec/08: verification tags + mutation registry --------------------
    def _load_spec08(self):
        txt = read_text(self.repo, "spec/08-verification-mapping.md")
        sec1 = txt.split("## 1. Source verification-obligation tags", 1)
        self.tags_frozen: list[str] = []
        self.tags_addendum: list[str] = []
        if len(sec1) > 1:
            body = sec1[1].split("## 2.", 1)[0]
            frozen_part, _, addendum_part = body.partition("**Post-audit addendum tags**")
            pat = re.compile(r"^\| `([A-Z][A-Z0-9]*(?:-[A-Z0-9]+)+)` \|", re.M)
            self.tags_frozen = pat.findall(frozen_part)
            self.tags_addendum = pat.findall(addendum_part)
        mut_body = txt.split("## 2. Mutation registry", 1)
        self.mutations = (re.findall(r"^\| (M\d{3}) \|", mut_body[1].split("## 3.", 1)[0], re.M)
                          if len(mut_body) > 1 else [])

    # -- spec/09: unresolved decisions ------------------------------------
    def _load_spec09(self):
        txt = read_text(self.repo, "spec/09-unresolved-decisions.md")
        self.decisions: dict[str, dict] = {}
        heads = list(_U_HEAD.finditer(txt))
        for i, h in enumerate(heads):
            end = heads[i + 1].start() if i + 1 < len(heads) else len(txt)
            body = txt[h.start():end]
            rid = h.group(1)
            resolved = None
            m = re.search(r"\*\*Resolved \(addendum ([IVX]+)[,)]", body)
            if m:
                resolved = "addendum %s" % m.group(1)
            elif "RETIRED by decision" in body:
                resolved = "recorded"
            elif re.search(r"\*\*Resolved \(2026-09-03, tooling", body):
                resolved = "repository-gate adoption"
            self.decisions[rid] = {
                "id": rid, "title": h.group(2).strip(),
                "status": "RESOLVED" if resolved else "OPEN",
                "resolution": resolved,
                "body_line": txt.count("\n", 0, h.start()) + 1,
            }

    # -- derived registries, read as cross-checks -------------------------
    def _load_derived(self):
        reg_path = self.repo / "reg/requirements.json"
        self.reg = load_json(self.repo, "reg/requirements.json") if reg_path.is_file() else None
        req_path = self.repo / "req/registry.json"
        self.req = load_json(self.repo, "req/registry.json") if req_path.is_file() else None
        s10_path = self.repo / "spec/10-index.json"
        self.spec10 = load_json(self.repo, "spec/10-index.json") if s10_path.is_file() else None
        term_path = self.repo / "term/10-index.json"
        self.term = load_json(self.repo, "term/10-index.json") if term_path.is_file() else None
        mod_path = self.repo / "mod/19-index.json"
        self.mod = load_json(self.repo, "mod/19-index.json") if mod_path.is_file() else None
        disp_path = self.repo / "state/dispositions.json"
        self.dispositions = (load_json(self.repo, "state/dispositions.json")
                             if disp_path.is_file() else None)
        dep_path = self.repo / "dep/10-graph.json"
        self.dep = load_json(self.repo, "dep/10-graph.json") if dep_path.is_file() else None


def line_refs_of(text: str) -> list[dict]:
    """`L123–L456` / `L1234` citations, in order of first appearance, deduped."""
    out: list[dict] = []
    seen = set()
    for m in _LINEREF.finditer(text):
        a = int(m.group(1))
        b = int(m.group(2)) if m.group(2) else a
        key = (a, b)
        if key in seen or b < a:
            continue
        seen.add(key)
        out.append({"start": a, "end": b})
    return out


def env_report() -> dict:
    """Environment facts that MUST NOT affect output, reported so the gate can
    prove it read them rather than depended on them."""
    return {
        "PYTHONHASHSEED": os.environ.get("PYTHONHASHSEED", "unset"),
        "hash_randomization_note": ("set() iteration order is never used for output; every "
                                    "collection is sorted or source-ordered before rendering"),
        "locale_note": "no locale-dependent formatting is used anywhere in the pipeline",
    }


def next_free_id(prefix: str, existing) -> str:
    """The next unused number of an id family, computed from the register's own
    maximum and zero-padded to the family's current width.

    Used only when a run must *file* an integrity finding: the pipeline prints
    a suggested id and never writes into `spec/06` or `spec/09` — filing is a
    governance act, not a generator act (§3: propose, do not authorize)."""
    sep = "" if prefix.endswith("-") else "-?"
    pat = re.compile("^" + prefix + sep + r"(\d{2,3})$")
    seen = [m.group(1) for m in (pat.match(str(i)) for i in existing) if m]
    nums = sorted({int(s) for s in seen})
    if not nums:
        return f"{prefix}{'-' if sep else ''}01"
    width = max(len(s) for s in seen)
    nxt = nums[-1] + 1
    hyphen = "" if prefix.endswith("-") else "-"
    return f"{prefix}{hyphen}{nxt:0{width}d}"
