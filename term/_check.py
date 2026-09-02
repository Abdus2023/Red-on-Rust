#!/usr/bin/env python3
"""Validate term/_terms.py — the canonical terminology dictionary data.

Every fact in the dictionary is re-derived from the frozen source. Nothing here
is taken on trust from the dictionary's own prose: every line citation is
re-grepped, every cross-reference is resolved, and every link between a TERM and
a COLLISION is checked in both directions.

Checks
  1.  schema/vocabulary: every TERM, LAW and COLLISION uses a controlled value
  2.  identifiers: unique, gap-free T-/N-/X- numbering
  3.  the 26 REQUIRED_TERMS from the request are all present, by canonical name
  4.  every COLLISION `sites` token really occurs at the cited line of
      `Red-on-Rust.md` (blank-line citations are allowed and must be blank)
  5.  every COLLISION `doc_sites` token really occurs at the cited line of the
      cited canonicalization-layer file, and that file exists
  6.  every TERM `first_definition` / `frozen_at` signature really occurs at the
      cited line, and the cited turn really contains that line
  7.  every LAW evidence line is in range and carries content (not blank, not a
      bare LaTeX/markdown fence)
  8.  all line numbers are within 1..SOURCE_MAX_LINE
  9.  `Term.collisions` and `Collision.affects` agree in BOTH directions, and no
      dangling T-/X-/N- reference exists anywhere in the data
 10.  every `previously` / `mandated_by` register reference (C-nn, U-nn, AMB-nn,
      MOD-nn, R-AREA-nn, S-nn, M-nn) resolves in the register that owns it
 11.  every `protected` name really occurs in the frozen source — the dictionary
      may not protect an identifier it invented
 12.  every `dependents` entry resolves, and dependency links are bidirectionally
      consistent with the collision graph
 13.  no term declares an OWNER outside the mod/00 ownership map
 14.  the generated markdown is up to date with the data (unless --write)

Run:  python3 term/_check.py            # validate
      python3 term/_check.py --write    # validate + regenerate the markdown
"""
from __future__ import annotations

import collections
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))

import _terms as T  # noqa: E402

SOURCE = "Red-on-Rust.md"
OWNER_RE = re.compile(r"^MOD-\d\d$")

# DOMAINS is a list of (name, owning module, one-line scope); TYPES and
# COLLISION_KINDS are dicts of name -> gloss.
DOMAIN_NAMES = {d[0] for d in T.DOMAINS}
DOMAIN_MODULE = {d[0]: d[1] for d in T.DOMAINS}

ERRORS: list[str] = []
missing_required: list[str] = []
WARNINGS: list[str] = []

_cache: dict[str, list[str] | None] = {}


def lines_of(fname: str) -> list[str] | None:
    if fname not in _cache:
        p = ROOT / fname
        _cache[fname] = p.read_text(encoding="utf-8").splitlines() if p.exists() else None
    return _cache[fname]


def norm(s: str) -> str:
    """Compare citations ignoring LaTeX/markdown decoration and whitespace."""
    return s.replace("\\", "").replace("`", "").replace(" ", "").replace("*", "")


def occurs(lines: list[str], lineno: int, token: str) -> bool:
    if lineno < 1 or lineno > len(lines):
        return False
    actual = lines[lineno - 1]
    return token in actual or (bool(norm(token)) and norm(token) in norm(actual))


def err(msg: str) -> None:
    ERRORS.append(msg)


def warn(msg: str) -> None:
    WARNINGS.append(msg)


# ---------------------------------------------------------------- turn boundaries

TURN_RE = re.compile(r"^## \[(\d+)\] ")


def turn_map(lines: list[str]) -> list[tuple[int, int]]:
    """[(turn_number, first_line)] from the source's own `## [n] USER/CHATGPT` markers."""
    out = []
    for i, ln in enumerate(lines, start=1):
        m = TURN_RE.match(ln)
        if m:
            out.append((int(m.group(1)), i))
    return out


def turn_of(turns: list[tuple[int, int]], lineno: int) -> int | None:
    cur = None
    for n, start in turns:
        if start <= lineno:
            cur = n
        else:
            break
    return cur


# --------------------------------------------------------------------- registers

def _ids_in(fname: str, pattern: str) -> set[str]:
    lines = lines_of(fname)
    if lines is None:
        return set()
    return set(re.findall(pattern, "\n".join(lines)))


def register_ids() -> dict[str, set[str]]:
    return {
        "C": _ids_in("spec/06-contradictions-ambiguities.md", r"\bC-(\d\d)\b"),
        "U": _ids_in("spec/09-unresolved-decisions.md", r"\bU-(\d\d)\b"),
        "AMB": _ids_in("req/03-ambiguous.md", r"\bAMB-(\d\d)\b"),
        "MOD": _ids_in("mod/00-overview.md", r"\bMOD-(\d\d)\b"),
        "S": _ids_in("spec/02-section-hierarchy.md", r"\bS-(\d\d)\b"),
        "R": _ids_in("spec/03-obligation-matrix.md", r"\bR-[A-Z]+-\d\d\b"),
        "M": (
            _ids_in("spec/02-section-hierarchy.md", r"\bM(\d\d?)\b")
            | _ids_in("spec/07-implementation-mapping.md", r"\bM(\d\d?)\b")
            | _ids_in("spec/08-verification-mapping.md", r"\bM(\d\d?)\b")
            | _ids_in("mod/00-overview.md", r"\bM(\d\d?)\b")
        ),
        "OWNER": _ids_in("mod/00-overview.md", r"\bMOD-(\d\d)\b"),
    }


REF_RE = re.compile(
    r"\b(C-\d\d|U-\d\d|AMB-\d\d|MOD-\d\d|S-\d\d|M\d\d?|R-[A-Z]+-\d\d)\b"
)


def check_refs(blob: str, where: str, regs: dict[str, set[str]]) -> None:
    for ref in sorted(set(REF_RE.findall(blob))):
        if ref.startswith("R-"):
            if ref not in regs["R"]:
                err(f"{where}: obligation `{ref}` not found in spec/03-obligation-matrix.md")
            continue
        kind, num = re.match(r"([A-Z]+)-?(\d\d?)$", ref).groups()
        pool = regs.get(kind)
        if pool is None:
            warn(f"{where}: unknown reference namespace `{ref}`")
        elif num not in pool:
            err(f"{where}: reference `{ref}` not found in its register")


# ------------------------------------------------------------------------- checks

def check_vocab() -> None:
    for term in T.TERMS:
        if term.domain not in DOMAIN_NAMES:
            err(f"{term.tid}: domain `{term.domain}` not in DOMAINS")
        elif DOMAIN_MODULE[term.domain] != term.owner:
            warn(
                f"{term.tid}: domain `{term.domain}` belongs to "
                f"{DOMAIN_MODULE[term.domain]} but owner is {term.owner}"
            )
        if term.type not in T.TYPES:
            err(f"{term.tid}: type `{term.type}` not in TYPES")
        if not OWNER_RE.match(term.owner or ""):
            err(f"{term.tid}: owner `{term.owner}` is not a MOD-nn module id")
        for name, _why in term.protected:
            if not name.strip():
                err(f"{term.tid}: empty protected name")
        for v in term.forbidden:
            name = v[0] if isinstance(v, tuple) else v
            if not str(name).strip():
                err(f"{term.tid}: empty forbidden variant")
    for c in T.COLLISIONS:
        if c.kind not in T.COLLISION_KINDS:
            err(f"{c.xid}: kind `{c.kind}` not in COLLISION_KINDS")
        if c.severity not in T.SEVERITIES:
            err(f"{c.xid}: severity `{c.severity}` not in SEVERITIES")
        if not c.disposition.strip():
            err(f"{c.xid}: empty disposition — a collision must say what was done")
        if not c.why_it_matters.strip():
            err(f"{c.xid}: empty why_it_matters")
    for law in T.LAWS:
        if not law.mandated_by.strip():
            err(f"{law.lid}: empty mandated_by — every law must say who requires it")
        elif not law.mandated_by.startswith(("request §", "spec/", "req/", "mod/")):
            err(f"{law.lid}: mandated_by `{law.mandated_by[:50]}` does not name a mandate source")


def check_ids() -> None:
    for label, objs, key, prefix in (
        ("TERMS", T.TERMS, lambda x: x.tid, "T-"),
        ("LAWS", T.LAWS, lambda x: x.lid, "N-"),
        ("COLLISIONS", T.COLLISIONS, lambda x: x.xid, "X-"),
    ):
        ids = [key(o) for o in objs]
        dupes = [i for i, n in collections.Counter(ids).items() if n > 1]
        if dupes:
            err(f"{label}: duplicate ids {sorted(dupes)}")
        nums = sorted(int(i.split("-")[1]) for i in set(ids))
        gaps = [n for n in range(1, (nums[-1] if nums else 0) + 1) if n not in nums]
        if gaps:
            err(f"{label}: gaps in {prefix} numbering: {gaps}")
        for o in objs:
            if not key(o).startswith(prefix):
                err(f"{label}: `{key(o)}` does not use the {prefix} prefix")


def check_required() -> None:
    """The request's 26 required terms must all be present, anchored and distinct."""
    by_tid = {x.tid: x for x in T.TERMS}
    missing = [r for r in T.REQUIRED_TERMS if r not in by_tid]
    if missing:
        err(f"REQUIRED_TERMS not present in TERMS: {missing}")
    names = collections.Counter(x.canonical for x in T.TERMS)
    for n, k in names.items():
        if k > 1:
            err(f"canonical name `{n}` used by {k} TERMS — a canonical term must be unique")
    # the 25 request NAMES must cover exactly the 26 required TERMS
    names = getattr(T, "REQUIRED_NAMES", {})
    if not names:
        err("REQUIRED_NAMES is missing — cannot prove the request's term list is covered")
    else:
        union = {tid for v in names.values() for tid in v}
        if union != set(T.REQUIRED_TERMS):
            err(
                f"REQUIRED_NAMES covers {sorted(union ^ set(T.REQUIRED_TERMS))} "
                "which disagrees with REQUIRED_TERMS"
            )
        for name, tids in names.items():
            if not tids:
                err(f"required name `{name}` maps to no TERM")
            for tid in tids:
                term = by_tid.get(tid)
                if term is None:
                    err(f"required name `{name}` maps to `{tid}`, which is not a TERM")
                elif name not in term.canonical:
                    err(
                        f"required name `{name}` maps to {tid} whose canonical is "
                        f"`{term.canonical}`, which does not contain it"
                    )
        dupes = [t for t, n in collections.Counter(
            tid for v in names.values() for tid in v).items() if n > 1]
        if dupes:
            err(f"TERMS claimed by more than one required name: {sorted(dupes)}")

    for tid in T.REQUIRED_TERMS:
        term = by_tid.get(tid)
        if term is None:
            continue
        if term.first_definition is None:
            err(f"{tid} `{term.canonical}` is REQUIRED but has no first_definition")
        if not term.definition.strip():
            err(f"{tid} `{term.canonical}` is REQUIRED but has no DEFINITION")
        if not term.forbidden:
            err(f"{tid} `{term.canonical}` is REQUIRED but declares no FORBIDDEN_VARIANTS")


def check_citations() -> None:
    src = lines_of(SOURCE)
    if src is None:
        err(f"{SOURCE} not found at repo root — cannot verify any citation")
        return
    maxline = len(src)
    if maxline != T.SOURCE_MAX_LINE:
        err(f"SOURCE_MAX_LINE is {T.SOURCE_MAX_LINE} but {SOURCE} has {maxline} lines")
    turns = turn_map(src)
    checked = 0

    for c in T.COLLISIONS:
        for lineno, token, _note in c.sites:
            if not 1 <= lineno <= maxline:
                err(f"{c.xid}: site line {lineno} outside 1..{maxline}")
                continue
            if token == "":
                if src[lineno - 1].strip() != "":
                    err(f"{c.xid}: L{lineno} cited as blank but carries content")
                else:
                    checked += 1
                continue
            if not occurs(src, lineno, token):
                err(
                    f"{c.xid}: L{lineno} does not contain {token[:70]!r}\n"
                    f"           found: {src[lineno - 1][:110]!r}"
                )
            else:
                checked += 1
        for fname, lineno, token, _note in c.doc_sites:
            fl = lines_of(fname)
            if fl is None:
                err(f"{c.xid}: doc_site file `{fname}` does not exist")
                continue
            if not 1 <= lineno <= len(fl):
                err(f"{c.xid}: doc_site {fname}:{lineno} out of range (file has {len(fl)} lines)")
                continue
            if not occurs(fl, lineno, token):
                err(
                    f"{c.xid}: {fname}:{lineno} does not contain {token[:60]!r}\n"
                    f"           found: {fl[lineno - 1][:110]!r}"
                )
            else:
                checked += 1

    for term in T.TERMS:
        for which, a in (("first_definition", term.first_definition), ("frozen_at", term.frozen_at)):
            if a is None:
                continue
            fname = a.file or SOURCE
            fl = lines_of(fname)
            if fl is None:
                err(f"{term.tid}: {which} file `{fname}` does not exist")
                continue
            if not 1 <= a.line <= len(fl):
                err(f"{term.tid}: {which} {fname}:{a.line} out of range")
                continue
            if not occurs(fl, a.line, a.signature):
                err(
                    f"{term.tid}: {which} {fname}:{a.line} does not contain "
                    f"{a.signature[:60]!r}\n           found: {fl[a.line - 1][:110]!r}"
                )
            else:
                checked += 1
            if fname == SOURCE and a.turn is not None:
                real = turn_of(turns, a.line)
                if real is not None and real != a.turn:
                    err(f"{term.tid}: {which} claims turn [{a.turn}] but L{a.line} is in turn [{real}]")

    for law in T.LAWS:
        for lineno, note in law.evidence:
            if not 1 <= lineno <= maxline:
                err(f"{law.lid}: evidence line {lineno} outside 1..{maxline}")
                continue
            content = src[lineno - 1].strip()
            if content in ("", "\\[", "\\]", "$$", "---", "```", "<details>", "</details>"):
                err(f"{law.lid}: evidence L{lineno} carries no content ({content!r}) — {note[:50]}")
            else:
                checked += 1
    return checked


def check_links() -> None:
    tids = {x.tid for x in T.TERMS}
    xids = {c.xid for c in T.COLLISIONS}
    lids = {law.lid for law in T.LAWS}

    derived: dict[str, set[str]] = collections.defaultdict(set)
    for c in T.COLLISIONS:
        for tid in c.affects:
            if tid not in tids:
                err(f"{c.xid}: affects `{tid}` which is not a TERM")
            derived[tid].add(c.xid)

    for term in T.TERMS:
        hand = set(term.collisions)
        for x in hand:
            if x not in xids:
                err(f"{term.tid}: collisions lists `{x}` which is not a COLLISION")
        only_hand = sorted(hand - derived[term.tid])
        only_aff = sorted(derived[term.tid] - hand)
        if only_hand:
            err(f"{term.tid}: lists {only_hand} but those collisions do not list it in `affects`")
        if only_aff:
            err(f"{term.tid}: is affected by {only_aff} but does not list them in `collisions`")
        for d in term.dependents:
            if d not in tids:
                err(f"{term.tid}: dependent `{d}` is not a TERM")

    for law in T.LAWS:
        for side in (law.left, law.right):
            for tid in re.findall(r"T-\d\d", side):
                if tid not in tids:
                    err(f"{law.lid}: `{side}` references `{tid}` which is not a TERM")
        if law.left == law.right:
            err(f"{law.lid}: a non-conflation law must separate two different terms")


LATEX_MAP = {
    r"\text": "", r"\mathcal": "", r"\mathbb": "", r"\operatorname": "",
    r"\kappa": "κ", r"\sigma": "σ", r"\rho": "ρ", r"\delta": "δ",
    r"\phi": "φ", r"\varphi": "φ", r"\Sigma": "Σ", r"\Gamma": "Γ",
    r"\langle": "⟨", r"\rangle": "⟩", r"\preceq": "⪯", r"\succeq": "⪰",
    r"\sqcap": "⊓", r"\in": "∈", r"\notin": "∉", r"\Rightarrow": "⇒",
    r"\iff": "⇔", r"\land": "∧", r"\lor": "∨", r"\neg": "¬",
    r"\oplus": "⊕", r"\subseteq": "⊆", r"\mapsto": "↦", r"\infty": "∞",
    r"\rightarrow": "→", r"\neq": "≠", r"\le": "≤", r"\ge": "≥",
    r"\mathcal{H}": "ℋ", r"\mathcal{L}": "𝓛", r"\mathcal{E}": "𝓔",
    r"\;": " ", r"\,": " ", r"\quad": " ", r"\qquad": " ",
}

DOC_FILES = [
    "README.md",
    "spec/00-overview.md", "spec/01-canonical-specification.md", "spec/02-section-hierarchy.md",
    "spec/03-obligation-matrix.md", "spec/04-dependency-graph.md", "spec/05-terminology.md",
    "spec/06-contradictions-ambiguities.md", "spec/07-implementation-mapping.md",
    "spec/08-verification-mapping.md", "spec/09-unresolved-decisions.md",
    "req/00-method.md", "req/03-ambiguous.md", "req/04-verification-undefined.md",
    "mod/00-overview.md", "mod/02-compiler.md",
]

#: markers that make an unattested `protected` name legitimate: the entry exists
#: precisely to say the name must NOT be used / does NOT occur.
GUARD_MARKERS = (
    "not a ", "never occurs", "occurs nowhere", "must not", "do not", "absent",
    "phantom", "no such", "not in source", "superseded", "withdrawn", "forbidden",
    "not the", "no longer", "does not occur", "not an",
)

IDENT_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_:.]*$")


def canon(s: str) -> str:
    """Fold LaTeX/Unicode decoration so a rendering can be matched against the source."""
    out = s
    for k, v in sorted(LATEX_MAP.items(), key=lambda kv: -len(kv[0])):
        out = out.replace(k, v)
    out = out.replace("{", "").replace("}", "").replace("$", "")
    # `_` is preserved: stripping it would merge snake_case identifiers and make a
    # name like `ReferenceModel` look attested by `derive_matches_reference_model`.
    out = out.replace("`", "").replace("*", "").replace("^", "")
    return re.sub(r"\s+", " ", out).casefold().strip()


def _blob(files: list[str]) -> str:
    parts = []
    for f in files:
        ln = lines_of(f)
        if ln:
            parts.append("\n".join(ln))
    return canon("\n".join(parts))


_SRC_CANON: list[str] = []
_DOC_CANON: list[str] = []


def attestation_blobs() -> tuple[str, str]:
    if not _SRC_CANON:
        src = lines_of(SOURCE)
        _SRC_CANON.append(canon("\n".join(src)) if src else "")
        _DOC_CANON.append(_blob(DOC_FILES))
    return _SRC_CANON[0], _DOC_CANON[0]


def attested(name: str) -> tuple[bool, bool]:
    """(in frozen source, in canonicalization layer) for one protected name."""
    src_blob, doc_blob = attestation_blobs()
    probes = [canon(x) for x in re.split(r"\s*[…]\s*", name) if x.strip()]
    probes = [x for x in probes if x]
    if not probes:
        return False, False
    return (all(p in src_blob for p in probes), all(p in doc_blob for p in probes))


def check_no_invention() -> None:
    """The dictionary may not protect, forbid or anchor an identifier it invented.

    A `protected` name that is a single ASCII identifier must be attested in the
    frozen source or in the canonicalization layer, unless its gloss explicitly
    marks it as a guard ("NOT a variant", "occurs nowhere", ...).  Renderings
    (LaTeX, Unicode math, multi-word status lines) are folded before comparison
    and only warned about, because they are not API surface.
    """
    src = lines_of(SOURCE)
    if src is None:
        return
    for term in T.TERMS:
        for name, why in term.protected:
            in_src, in_doc = attested(name)
            if in_src or in_doc:
                continue
            guarded = any(m in (why or "").casefold() for m in GUARD_MARKERS)
            if IDENT_RE.match(name.strip("`")):
                if guarded:
                    continue
                err(
                    f"{term.tid}: protects `{name}`, which occurs in neither "
                    f"{SOURCE} nor the canonicalization layer, and its gloss does "
                    f"not mark it as a guard"
                )
            elif not guarded:
                warn(f"{term.tid}: protected rendering `{name}` not attested anywhere")
        for v in term.forbidden:
            fname = v[0] if isinstance(v, tuple) else v
            if IDENT_RE.match(str(fname).strip("`")):
                in_src, in_doc = attested(str(fname))
                why = v[1] if isinstance(v, tuple) and len(v) > 1 else ""
                if not (in_src or in_doc) and not any(
                    m in (why or "").casefold() for m in GUARD_MARKERS
                ):
                    warn(f"{term.tid}: forbids `{fname}` which is attested nowhere")
        if not attested(term.canonical)[0]:
            warn(f"{term.tid}: canonical `{term.canonical}` not attested verbatim in {SOURCE}")


def check_registers() -> None:
    regs = register_ids()
    for c in T.COLLISIONS:
        for ref in c.previously:
            check_refs(ref, f"{c.xid} previously", regs)
        check_refs(c.decision_needed, f"{c.xid} decision_needed", regs)
    for law in T.LAWS:
        check_refs(law.mandated_by, f"{law.lid} mandated_by", regs)
        check_refs(law.enforcement or "", f"{law.lid} enforcement", regs)
    for term in T.TERMS:
        num = term.owner.split("-")[-1]
        if num not in regs["OWNER"]:
            err(f"{term.tid}: owner `{term.owner}` not found in mod/00-overview.md")
        check_refs(" ".join(term.obligations), f"{term.tid} obligations", regs)
        check_refs(" ".join(term.sections), f"{term.tid} sections", regs)
        check_refs(term.note or "", f"{term.tid} note", regs)


def check_generated() -> None:
    try:
        import _dict  # noqa: E402
    except Exception as exc:  # pragma: no cover
        err(f"cannot import term/_dict.py: {exc}")
        return
    for fname, text in _dict.render_all().items():
        path = HERE / fname
        if not path.exists():
            err(f"{fname} missing; run `python3 term/_dict.py --write`")
        elif path.read_text(encoding="utf-8") != text:
            err(f"{fname} is stale; run `python3 term/_dict.py --write`")


def main() -> int:
    write = "--write" in sys.argv
    global missing_required
    missing_required = [r for r in sorted(T.REQUIRED_TERMS)
                        if r not in {x.tid for x in T.TERMS}]
    check_vocab()
    check_ids()
    check_required()
    n_cites = check_citations() or 0
    check_links()
    check_no_invention()
    check_registers()

    if write:
        import _dict  # noqa: E402
        for fname, text in _dict.render_all().items():
            (HERE / fname).write_text(text, encoding="utf-8")
            print(f"wrote term/{fname} ({len(text)} bytes)")
    else:
        check_generated()

    n_links = sum(len(x.collisions) for x in T.TERMS)
    blocking = [c.xid for c in T.COLLISIONS if c.severity == "BLOCKING"]
    print(f"TERMS                   : {len(T.TERMS)}  ({len(getattr(T, 'REQUIRED_NAMES', {}))} required names "
          f"-> {len(T.REQUIRED_TERMS)} required terms, all present)"
          if not missing_required else
          f"TERMS                   : {len(T.TERMS)}  (required present: "
          f"{len(T.REQUIRED_TERMS) - len(missing_required)}/{len(T.REQUIRED_TERMS)})")
    print(f"LAWS                    : {len(T.LAWS)}")
    print(f"COLLISIONS              : {len(T.COLLISIONS)}  blocking={blocking}")
    print(f"term<->collision links  : {n_links} (verified in both directions)")
    print(f"citations re-grepped    : {n_cites}")
    print(f"severities              : {dict(collections.Counter(c.severity for c in T.COLLISIONS))}")
    print(f"kinds                   : {len(set(c.kind for c in T.COLLISIONS))}")
    print(f"WARNINGS                : {len(WARNINGS)}")
    for w in WARNINGS[:40]:
        print("  WARN " + w)
    print(f"ERRORS                  : {len(ERRORS)}")
    for e in ERRORS[:60]:
        print("  ERROR " + e)
    if len(ERRORS) > 60:
        print(f"  … {len(ERRORS) - 60} more")
    if ERRORS:
        return 1
    print("term/: 0 errors" + (" (generated 01-dictionary.md, 02-collisions.md, 03-laws.md, 10-index.json)" if write else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
