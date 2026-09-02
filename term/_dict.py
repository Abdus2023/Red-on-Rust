#!/usr/bin/env python3
"""Render the canonical terminology dictionary from term/_terms.py.

Generated files (do not edit by hand — edit `term/_terms.py` and re-run):

    term/01-dictionary.md    the 74 canonical terms, with the seven fields the
                             normalization request requires of every term
    term/02-collisions.md    the collision register (63 findings), every one cited
                             to a frozen-source line and re-grepped by _check.py
    term/03-laws.md          the non-conflation laws the distinctions imply
    term/10-index.json       machine-readable index of all three

Run:  python3 term/_dict.py --write     # regenerate
      python3 term/_dict.py             # dry run, report drift
"""
from __future__ import annotations

import collections
import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import _terms as T  # noqa: E402

SOURCE = T.SOURCE
SEV_ORDER = {"BLOCKING": 0, "MAJOR": 1, "MINOR": 2, "INFO": 3}


_SRC_TEXT: list[str] = []


def src_text() -> str:
    """The frozen source, read once, for verbatim-attestation of canonical names."""
    if not _SRC_TEXT:
        path = pathlib.Path(__file__).resolve().parent.parent / SOURCE
        _SRC_TEXT.append(path.read_text(encoding="utf-8") if path.exists() else "")
    return _SRC_TEXT[0]


def attested_verbatim(name: str) -> bool:
    """True if a canonical name occurs verbatim in the frozen source.

    Four canonical terms are descriptive labels for something the source has but
    never names with a single token (two `Observation` structs, the canonical byte
    format, the evidence-status ladder). They are rendered with an explicit banner
    so no reader mistakes the label for a frozen identifier.
    """
    return name in src_text()


def tid_key(tid: str) -> tuple:
    """Deterministic ordering for T-/N-/X- ids (REQUIRED_TERMS is a set)."""
    pre, _, num = tid.partition("-")
    return (pre, int(num) if num.isdigit() else 0)

GENERATED = (
    "<!-- GENERATED FILE — DO NOT EDIT BY HAND. -->\n"
    "<!-- Source of truth: `term/_terms.py`.  Regenerate: `python3 term/_dict.py --write`. -->\n"
    "<!-- Every line citation below is re-grepped against `Red-on-Rust.md` by `python3 term/_check.py`. -->\n"
)


# --------------------------------------------------------------------- helpers

def anchor_str(a, prefix: str = "L") -> str:
    if a is None:
        return "—"
    where = a.file if a.file and a.file != SOURCE else ""
    loc = f"{where}:{a.line}" if where else f"{prefix}{a.line}"
    turn = f", turn [{a.turn}]" if a.turn is not None else ""
    return f"`{loc}`{turn} — `{a.signature}`"


def short_anchor(a) -> str:
    if a is None:
        return "—"
    where = f"{a.file}:" if a.file and a.file != SOURCE else ""
    return f"{where}L{a.line}"


def tid_name(tid: str) -> str:
    for x in T.TERMS:
        if x.tid == tid:
            return f"{tid} `{x.canonical}`"
    return tid


def bullets(items, indent: str = "") -> str:
    return "".join(f"{indent}- {i}\n" for i in items) if items else f"{indent}- —\n"


def link_list(ids, resolver) -> str:
    return ", ".join(resolver(i) for i in ids) if ids else "—"


# ------------------------------------------------------------------ 01 dictionary

def render_dictionary() -> str:
    out = [GENERATED, "\n# 01 — Canonical Terminology Dictionary\n", "\n"]
    out.append(
        f"{len(T.TERMS)} canonical terms. Each entry states the seven fields the "
        "normalization request requires — **CANONICAL_TERM**, **FORBIDDEN_VARIANTS**, "
        "**DEFINITION**, **TYPE**, **OWNER**, **FIRST_DEFINITION**, **DEPENDENTS** — "
        "plus the frozen shape, any superseded declarations, the obligations that use "
        "the term, and the collisions it participates in.\n"
    )
    out.append("\n")
    out.append(
        "**Hard constraint honoured throughout:** no API, type, mathematical symbol or "
        "protocol field is renamed anywhere in this dictionary. Where the frozen source "
        "uses two names for one thing, or one name for two things, both are recorded "
        "verbatim and the conflict is filed in `02-collisions.md`; the canonical term is "
        "the one an author must *use*, never a new identifier to *introduce*. Names the "
        "source froze are listed under **PROTECTED (do not rename)**.\n"
    )

    # index table
    out.append("\n## Index\n")
    out.append("| ID | CANONICAL_TERM | TYPE | DOMAIN | OWNER | FIRST_DEFINITION | Collisions |\n")
    out.append("|---|---|---|---|---|---|---|\n")
    for x in T.TERMS:
        req = " ★" if x.tid in T.REQUIRED_TERMS else ""
        out.append(
            f"| [{x.tid}](#{x.tid.lower()}-{slug(x.canonical)}) | `{x.canonical}`{req} "
            f"| {x.type} | {x.domain} | {x.owner} | `{short_anchor(x.first_definition)}` "
            f"| {len(x.collisions)} |\n"
        )
    out.append(
        f"\n★ = one of the {len(T.REQUIRED_TERMS)} terms the normalization request "
        "explicitly requires.\n"
    )

    # by domain
    by_domain: dict[str, list] = collections.defaultdict(list)
    for x in T.TERMS:
        by_domain[x.domain].append(x)
    domain_meta = {d[0]: d for d in T.DOMAINS}

    for dname, _mod, scope in T.DOMAINS:
        terms = by_domain.get(dname)
        if not terms:
            continue
        out.append(f"\n---\n\n## {dname} — {scope}\n")
        out.append(f"Owning module: **{domain_meta[dname][1]}**.\n")
        for x in terms:
            out.append(render_term(x))
    return "".join(out)


def slug(name: str) -> str:
    keep = []
    for ch in name.lower():
        if ch.isalnum():
            keep.append(ch)
        elif ch in " _:.:-/":
            keep.append("-")
    s = "".join(keep)
    while "--" in s:
        s = s.replace("--", "-")
    return s.strip("-")


def render_term(x) -> str:
    o = []
    o.append(f"\n### {x.tid} — `{x.canonical}`\n")
    if x.tid in T.REQUIRED_TERMS:
        o.append("*Required term.*\n")
    o.append("\n")
    if not attested_verbatim(x.canonical):
        o.append(
            "> **Label, not an identifier.** `" + x.canonical + "` does not occur "
            "verbatim in the frozen source. It is a descriptive name this dictionary "
            "uses to address one denotation unambiguously; the frozen identifier(s) it "
            "labels are listed under **PROTECTED (do not rename)** below. Introducing "
            "`" + x.canonical + "` into code, a protocol or a formula would be a rename "
            "and is prohibited.\n\n"
        )
    o.append(f"- **CANONICAL_TERM:** `{x.canonical}`\n")
    o.append(f"- **TYPE:** {x.type} — {T.TYPES.get(x.type, '')}\n")
    o.append(
        f"- **OWNER:** {x.owner} (`{x.owner_crate}`)\n"
    )
    o.append(f"- **DEFINITION:** {x.definition}\n")
    o.append(f"- **FIRST_DEFINITION:** {anchor_str(x.first_definition)}\n")
    if x.frozen_at:
        o.append(f"- **FROZEN_AT:** {anchor_str(x.frozen_at)}\n")
    o.append(
        "- **DEPENDENTS:** "
        + link_list(x.dependents, tid_name)
        + "\n"
    )
    o.append(
        "- **FORBIDDEN_VARIANTS:**\n"
        + (
            "".join(f"    - {forbidden_line(v)}\n" for v in x.forbidden)
            if x.forbidden
            else "    - —\n"
        )
    )
    if x.protected:
        o.append(
            "- **PROTECTED (do not rename):**\n"
            + "".join(f"    - {code_span(n)} — {w}\n" for n, w in x.protected)
        )
    if x.shape:
        o.append(f"- **FROZEN SHAPE:** `{x.shape}`\n")
    if x.supersedes:
        o.append(
            "- **SUPERSEDES (recorded, not deleted):**\n"
            + "".join(f"    - `{v}`\n" for v in x.supersedes)
        )
    if x.obligations:
        o.append(f"- **OBLIGATIONS:** {', '.join(f'`{r}`' for r in x.obligations)}\n")
    if x.sections:
        o.append(f"- **SECTIONS:** {', '.join(f'`{s}`' for s in x.sections)}\n")
    o.append(
        "- **COLLISIONS:** "
        + (
            ", ".join(f"[{c}](02-collisions.md#{c.lower()})" for c in x.collisions)
            if x.collisions
            else "—"
        )
        + "\n"
    )
    laws = [law.lid for law in T.LAWS if x.tid in (law.left, law.right)]
    if laws:
        o.append(
            "- **LAWS:** "
            + ", ".join(f"[{n}](03-laws.md#{n.lower()})" for n in laws)
            + "\n"
        )
    if x.note:
        o.append(f"- **NOTE:** {x.note}\n")
    return "".join(o)


# ----------------------------------------------------------------- 02 collisions

def render_collisions() -> str:
    out = [GENERATED, "\n# 02 — Terminology Collision Register\n", "\n"]
    sev = collections.Counter(c.severity for c in T.COLLISIONS)
    kind = collections.Counter(c.kind for c in T.COLLISIONS)
    new = [c for c in T.COLLISIONS if c.new_finding]
    out.append(
        f"**{len(T.COLLISIONS)} collisions.** Every terminology collision found in the "
        "frozen source and in the canonicalization layer is reported here; none is "
        "silently resolved. Severity: "
        + ", ".join(f"{k} {sev[k]}" for k in ("BLOCKING", "MAJOR", "MINOR", "INFO") if sev[k])
        + f". {len(new)} are new findings not previously registered in `spec/06` or "
        "`req/03`; the remainder extend or correct an existing `C-`/`U-`/`AMB-` entry, "
        "which is named in **Previously registered as**.\n"
    )
    out.append(
        "\nA collision is filed when the source (or a document derived from it) uses one "
        "name for two incompatible things, two names for one thing without retracting "
        "either, a name for something never declared, or a citation for text that is not "
        "there. **Nothing is renamed to make a collision disappear.** The disposition "
        "states what the canonicalization layer does instead: record both, name the "
        "governing text, and escalate the decision where the source does not settle it.\n"
    )

    out.append("\n## Kinds\n")
    out.append("| Kind | Meaning | Count |\n|---|---|---|\n")
    for k, n in sorted(kind.items(), key=lambda kv: (-kv[1], kv[0])):
        out.append(f"| `{k}` | {T.COLLISION_KINDS.get(k, '')} | {n} |\n")

    out.append("\n## Summary\n")
    out.append("| ID | Collision | Kind | Severity | Terms | Previously | Decision needed |\n")
    out.append("|---|---|---|---|---|---|---|\n")
    for c in sorted(T.COLLISIONS, key=lambda c: (SEV_ORDER[c.severity], c.xid)):
        out.append(
            f"| [{c.xid}](#{c.xid.lower()}) | {md_escape_cell(c.title)} | {c.kind} | "
            f"**{c.severity}** | {len(c.affects)} | "
            f"{', '.join(c.previously) if c.previously else '—'} | "
            f"{'YES' if c.decision_needed else 'no'} |\n"
        )

    blocking = [c for c in T.COLLISIONS if c.severity == "BLOCKING"]
    if blocking:
        out.append("\n## Blocking\n")
        out.append(
            "These must be decided before the work they gate can start. Each names the "
            "milestone or obligation it blocks in its **Decision needed** field.\n"
        )
        for c in blocking:
            out.append(f"- **{c.xid}** — {c.title}\n")

    out.append("\n---\n")
    for c in sorted(T.COLLISIONS, key=lambda c: (SEV_ORDER[c.severity], c.xid)):
        out.append(render_collision(c))
    return "".join(out)


def md_escape_cell(s: str) -> str:
    return s.replace("|", "\\|").replace("\n", " ")


def render_collision(c) -> str:
    o = [f"\n## {c.xid}\n", "\n"]
    o.append(f"**{c.title}**\n\n")
    o.append(f"- **Kind:** `{c.kind}` — {T.COLLISION_KINDS.get(c.kind, '')}\n")
    o.append(f"- **Severity:** {c.severity}\n")
    o.append(f"- **Terms affected:** {link_list(c.affects, tid_name)}\n")
    if c.previously:
        o.append(f"- **Previously registered as:** {', '.join(f'`{p}`' for p in c.previously)}\n")
    if not c.new_finding:
        o.append("- **Provenance:** extends or corrects an existing register entry; not a new finding.\n")
    o.append(f"\n### Evidence (frozen source)\n\n")
    o.append("| Line | Text at that line | What it denotes there |\n|---|---|---|\n")
    for lineno, token, note in c.sites:
        shown = token if token.strip() else "*(deliberately blank line)*"
        o.append(f"| `{SOURCE}` L{lineno} | {md_escape_cell(code_span(shown))} | {md_escape_cell(note)} |\n")
    if c.doc_sites:
        o.append("\n### Evidence (canonicalization layer)\n\n")
        o.append("| File:line | Text at that line | Note |\n|---|---|---|\n")
        for fname, lineno, token, note in c.doc_sites:
            o.append(f"| `{fname}`:{lineno} | {md_escape_cell(code_span(token))} | {md_escape_cell(note)} |\n")
    o.append(f"\n### The collision\n\n{c.statement}\n")
    o.append(f"\n### Why it matters\n\n{c.why_it_matters}\n")
    o.append(f"\n### Disposition\n\n{c.disposition}\n")
    if c.decision_needed:
        o.append(f"\n### Decision needed\n\n{c.decision_needed}\n")
    return "".join(o)


FORBIDDEN_RE = re.compile(r"^(?P<name>[^(]+?)\s*\((?P<gloss>.*)\)\s*$", re.S)


def forbidden_line(v) -> str:
    """`name (gloss)` -> a code span for the name and plain prose for the gloss."""
    name = v[0] if isinstance(v, tuple) else v
    why = (v[1] if isinstance(v, tuple) and len(v) > 1 else "") or ""
    m = FORBIDDEN_RE.match(str(name).strip())
    if m:
        head, gloss = m.group("name").strip(), m.group("gloss").strip()
        text = f"{code_span(head)} — {gloss}"
    else:
        text = code_span(str(name).strip())
    if why:
        text += f" ({why})"
    return text


def code_span(s: str) -> str:
    s = s.strip()
    if not s:
        return s
    fence = "``" if "`" in s else "`"
    return f"{fence}{s}{fence}"


# ----------------------------------------------------------------------- 03 laws

def render_laws() -> str:
    out = [GENERATED, "\n# 03 — Non-Conflation Laws\n", "\n"]
    out.append(
        f"{len(T.LAWS)} laws. A law states that two canonical terms must never be used "
        "for each other. The first nine are mandated by the request's special rule about "
        "not silently renaming an API, type, mathematical symbol or protocol field; the "
        "rest are mandated by the request's list of required distinctions or by a named "
        "part of the frozen specification. A law is not a rename: both terms keep their "
        "frozen names, and the law says which one a given sentence must use.\n"
    )
    out.append("\n| ID | Law | Mandated by | Enforced by |\n|---|---|---|---|\n")
    for law in T.LAWS:
        out.append(
            f"| [{law.lid}](#{law.lid.lower()}) | {md_escape_cell(law.statement.split('.')[0])} "
            f"| {md_escape_cell(law.mandated_by)} | {md_escape_cell(law.enforcement)} |\n"
        )
    out.append("\n---\n")
    for law in T.LAWS:
        out.append(f"\n## {law.lid}\n\n")
        out.append(f"**{law.statement}**\n\n")
        out.append(f"- **Left term:** {tid_name(law.left)}\n")
        out.append(f"- **Right term:** {tid_name(law.right)}\n")
        out.append(f"- **Mandated by:** {law.mandated_by}\n")
        out.append(f"- **Enforced by:** {law.enforcement}\n")
        out.append("\n### Evidence\n\n")
        for lineno, note in law.evidence:
            out.append(f"- `{SOURCE}` L{lineno} — {note}\n")
        out.append(f"\n### Consequence of conflating them\n\n{law.consequence}\n")
    return "".join(out)


# ------------------------------------------------------------------- 10 index.json

def render_index() -> str:
    payload = {
        "generated_by": "term/_dict.py",
        "source_of_truth": "term/_terms.py",
        "frozen_source": {"file": SOURCE, "lines": T.SOURCE_MAX_LINE},
        "counts": {
            "terms": len(T.TERMS),
            "required_terms": len(T.REQUIRED_TERMS),
            "laws": len(T.LAWS),
            "collisions": len(T.COLLISIONS),
            "collision_severities": dict(collections.Counter(c.severity for c in T.COLLISIONS)),
            "collision_kinds": dict(collections.Counter(c.kind for c in T.COLLISIONS)),
            "term_collision_links": sum(len(x.collisions) for x in T.TERMS),
            "new_findings": len([c for c in T.COLLISIONS if c.new_finding]),
        },
        "required_terms": [
            {"tid": t, "canonical": next(x.canonical for x in T.TERMS if x.tid == t)}
            for t in sorted(T.REQUIRED_TERMS, key=tid_key)
        ],
        "blocking_collisions": [
            {"xid": c.xid, "title": c.title, "decision_needed": c.decision_needed}
            for c in T.COLLISIONS
            if c.severity == "BLOCKING"
        ],
        "terms": [
            {
                "tid": x.tid,
                "CANONICAL_TERM": x.canonical,
                "TYPE": x.type,
                "OWNER": x.owner,
                "owner_crate": x.owner_crate,
                "domain": x.domain,
                "DEFINITION": x.definition,
                "FIRST_DEFINITION": (
                    None
                    if x.first_definition is None
                    else {
                        "file": x.first_definition.file or SOURCE,
                        "line": x.first_definition.line,
                        "turn": x.first_definition.turn,
                        "signature": x.first_definition.signature,
                    }
                ),
                "FROZEN_AT": (
                    None
                    if x.frozen_at is None
                    else {
                        "file": x.frozen_at.file or SOURCE,
                        "line": x.frozen_at.line,
                        "turn": x.frozen_at.turn,
                        "signature": x.frozen_at.signature,
                    }
                ),
                "DEPENDENTS": x.dependents,
                "FORBIDDEN_VARIANTS": x.forbidden,
                "PROTECTED": [{"name": n, "why": w} for n, w in x.protected],
                "obligations": x.obligations,
                "sections": x.sections,
                "collisions": x.collisions,
                "laws": [law.lid for law in T.LAWS if x.tid in (law.left, law.right)],
                "shape": x.shape,
                "supersedes": x.supersedes,
                "note": x.note,
            }
            for x in T.TERMS
        ],
        "laws": [
            {
                "lid": law.lid,
                "left": law.left,
                "right": law.right,
                "statement": law.statement,
                "mandated_by": law.mandated_by,
                "enforcement": law.enforcement,
                "consequence": law.consequence,
                "evidence": [{"file": SOURCE, "line": ln, "note": note} for ln, note in law.evidence],
            }
            for law in T.LAWS
        ],
        "collisions": [
            {
                "xid": c.xid,
                "title": c.title,
                "kind": c.kind,
                "severity": c.severity,
                "affects": c.affects,
                "previously": c.previously,
                "new_finding": c.new_finding,
                "decision_needed": c.decision_needed,
                "statement": c.statement,
                "why_it_matters": c.why_it_matters,
                "disposition": c.disposition,
                "sites": [{"file": SOURCE, "line": ln, "text": tok, "denotes": note}
                          for ln, tok, note in c.sites],
                "doc_sites": [{"file": f, "line": ln, "text": tok, "note": note}
                              for f, ln, tok, note in c.doc_sites],
            }
            for c in T.COLLISIONS
        ],
        "domains": [{"name": d[0], "module": d[1], "scope": d[2]} for d in T.DOMAINS],
        "types": T.TYPES,
        "collision_kinds": T.COLLISION_KINDS,
    }
    return json.dumps(payload, indent=1, ensure_ascii=False) + "\n"


def render_all() -> dict[str, str]:
    return {
        "01-dictionary.md": render_dictionary(),
        "02-collisions.md": render_collisions(),
        "03-laws.md": render_laws(),
        "10-index.json": render_index(),
    }


def main() -> int:
    write = "--write" in sys.argv
    rendered = render_all()
    drift = 0
    for fname, text in rendered.items():
        path = HERE / fname
        if write:
            path.write_text(text, encoding="utf-8")
            print(f"wrote term/{fname} ({len(text)} bytes, {text.count(chr(10))} lines)")
        else:
            if not path.exists():
                print(f"MISSING term/{fname}")
                drift += 1
            elif path.read_text(encoding="utf-8") != text:
                print(f"STALE   term/{fname}")
                drift += 1
            else:
                print(f"ok      term/{fname}")
    if not write and drift:
        print(f"{drift} generated file(s) out of date; run `python3 term/_dict.py --write`")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
