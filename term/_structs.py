#!/usr/bin/env python3
"""Struct-declaration field-set sweep for Red-on-Rust.md.

Re-derives, from the frozen source, every `struct` declaration and its field
set, so that claims of the form "struct X is declared N times with M distinct
shapes" in term/_terms.py and term/00-overview.md can be checked mechanically
instead of by eye.

A shape is the ordered tuple of (field_name, field_type) pairs. Visibility
modifiers are NOT part of a shape (`pub`, `pub(crate)`, `pub(super)` and no
modifier all normalise away): a visibility-only difference is reported in its
own bucket, never as a shape divergence. Elided bodies (`{ ... }`,
`// ...`, empty) are also their own bucket.

Usage:
    python3 term/_structs.py            # report
    python3 term/_structs.py --json     # machine-readable dump
    python3 term/_structs.py --struct Authority
"""
from __future__ import annotations

import argparse
import collections
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SOURCE = ROOT / "Red-on-Rust.md"

DECL = re.compile(
    r"^\s*(?:pub(?:\([^)]*\))?\s+)?struct\s+([A-Z][A-Za-z0-9_]*)\b(.*)$"
)
ENUM_DECL = re.compile(
    r"^\s*(?:pub(?:\([^)]*\))?\s+)?enum\s+([A-Z][A-Za-z0-9_]*)\b(.*)$"
)
VARIANT = re.compile(r"^\s*([A-Z][A-Za-z0-9_]*)\b\s*(.*)$", re.S)
# `pub name: Type,` — visibility stripped, trailing comma stripped, comment stripped.
FIELD = re.compile(
    r"^\s*(?:pub(?:\([^)]*\))?\s+)?([a-z_][A-Za-z0-9_]*)\s*:\s*(.+?)\s*,?\s*(?://.*)?$"
)
VIS = re.compile(r"^\s*(?:pub(?:\([^)]*\))?\s+)")
TURN = re.compile(r"^#{1,4}\s*.*?\[(\d+)\]")


def read_lines() -> list[str]:
    return SOURCE.read_text(encoding="utf-8").split("\n")


def turn_map(lines: list[str]) -> list[int]:
    """turn[n-1] == the turn heading that line n sits under (0 if none yet)."""
    turns: list[int] = []
    cur = 0
    for line in lines:
        m = TURN.match(line)
        if m:
            cur = int(m.group(1))
        turns.append(cur)
    return turns

def _split_top_level(text: str) -> list[str]:
    """Split on commas that are not nested inside <>, (), [] or {}."""
    out, depth, cur = [], 0, []
    for ch in text:
        if ch in "<([{":
            depth += 1
        elif ch in ">)]}":
            depth -= 1
        if ch == "," and depth == 0:
            out.append("".join(cur))
            cur = []
        else:
            cur.append(ch)
    out.append("".join(cur))
    return out


INLINE_COMMENT = re.compile(r"\s*//.*$")
BLOCK_COMMENT = re.compile(r"/\*.*?\*/")
# `std::collections::HashMap` and `HashMap` are one type written two ways; so
# are `slotmap::SlotMap<slotmap::DefaultKey, _>` and `SlotMap<DefaultKey, _>`.
# Module paths are therefore normalised away from field types, while the type
# NAME is kept: `SlotMap` vs `GenerationalArena` remains a real divergence.
MODULE_PATH = re.compile(r"\b[A-Za-z_][A-Za-z0-9_]*::")


def _generic_params(rest: str) -> list[str]:
    """Type parameters from `struct Authority<S, Q, R, L> {` -> [S, Q, R, L]."""
    m = re.match(r"\s*<", rest)
    if not m:
        return []
    depth, out = 0, []
    for ch in rest:
        if ch == "<":
            depth += 1
        elif ch == ">":
            depth -= 1
            if depth == 0:
                break
        if depth >= 1:
            out.append(ch)
    inner = "".join(out[1:])
    return [p.split(":")[0].strip() for p in _split_top_level(inner) if p.strip()]


PRIMITIVE_TYPES = set(
    "u8 u16 u32 u64 u128 usize i8 i16 i32 i64 i128 isize f32 f64 bool str char"
    .split()
)
STD_TYPES = set(
    "Vec HashMap BTreeMap HashSet BTreeSet VecDeque Option Result Box String Rc"
    " Arc Cell RefCell PhantomData NonZeroU64 Duration Instant Self".split()
)



def enum_sweep(lines: list[str]):
    """name -> list of enum declarations, each with its variant set.

    A variant is recorded as `Name` (unit), `Name(Type, ...)` (tuple) or
    `Name{field: Type, ...}` (struct-like), with visibility and module paths
    normalised exactly as for structs, so that a variant set can be compared
    across turns without path noise.
    """
    n = len(lines)
    turns = turn_map(lines)
    decls: dict[str, list[dict]] = collections.defaultdict(list)
    i = 0
    while i < n:
        m = ENUM_DECL.match(lines[i])
        if not m or "{" not in m.group(2):
            i += 1
            continue
        name, rest = m.group(1), m.group(2)
        line, turn = i + 1, turns[i]
        depth = rest.count("{") - rest.count("}")
        body = [rest[rest.index("{") + 1:]]
        j = i
        while depth > 0 and j + 1 < n:
            j += 1
            depth += lines[j].count("{") - lines[j].count("}")
            body.append(lines[j])
        cleaned, elided = _clean_body(body)
        variants: list[str] = []
        for frag in _split_top_level(cleaned):
            raw = " ".join(frag.split("\n")).strip().rstrip("}").strip()
            if not raw:
                continue
            vm = VARIANT.match(raw)
            if not vm:
                elided = True
                continue
            vname, payload = vm.group(1), vm.group(2).strip()
            payload = MODULE_PATH.sub("", VIS.sub("", payload)).strip()
            payload = re.sub(r"\s+", " ", payload)
            if payload.startswith("{"):
                inner = payload[payload.index("{") + 1:].rstrip("}").strip()
                fields = []
                for part in _split_top_level(inner):
                    fm = FIELD.match(part.strip())
                    if fm:
                        fields.append("%s:%s" % (fm.group(1),
                                                 _norm_type(fm.group(2))))
                    elif part.strip():
                        elided = True
                variants.append("%s{%s}" % (vname, ", ".join(fields)))
            elif payload.startswith("("):
                inner = payload[payload.index("(") + 1:].rstrip(")").strip()
                types = [_norm_type(t) for t in _split_top_level(inner)
                         if t.strip()]
                variants.append("%s(%s)" % (vname, ", ".join(types)))
            else:
                variants.append(vname)
        decls[name].append(dict(line=line, turn=turn, elided=elided,
                                variants=tuple(variants),
                                generics=tuple(_generic_params(rest))))
        i = j + 1
    return decls


def _norm_type(text: str) -> str:
    return re.sub(r"\s+", " ", MODULE_PATH.sub("", VIS.sub("", text))
                  .strip().rstrip(",").rstrip("}")).strip()


def _clean_body(body: list[str]) -> tuple[str, bool]:
    """Strip doc comments, attributes and comments from a declaration body;
    report whether the body contains an explicit `...` / `/* ... */` elision.

    Comments must go BEFORE comma-splitting: prose comments contain commas
    ("Reserved at issuance, released at completion") that would otherwise cut a
    fragment in half and swallow the following field.
    """
    kept: list[str] = []
    elided = False
    for line in body:
        if BLOCK_COMMENT.search(line):
            # `pub struct LiveHost { /* OS-level implementations */ }` — a block
            # comment in the body means the field list is not written out.
            # Checked first: such a line can also begin with `/*`, which the
            # doc-comment skip below would otherwise swallow silently.
            elided = True
            line = BLOCK_COMMENT.sub("", line)
        stripped = line.strip()
        if not stripped or stripped.startswith(("///", "//!", "#[", "/*", "*")):
            continue
        if re.fullmatch(r"(//\s*)?\.{3}|\}\s*$", stripped):
            if stripped == "}":
                continue
            elided = True
            continue
        no_comment = INLINE_COMMENT.sub("", line)
        # A comment carrying `...` means the author left the list incomplete:
        # `// ... other fields using naive representations` (L11575) and
        # `// ... previous variants` (L34996) are both elisions, not prose.
        if re.search(r"//.*\.{3}", stripped):
            elided = True
        kept.append(no_comment)
    return "\n".join(kept), elided


def sweep(lines: list[str]):
    """Return name -> list of struct declarations.

    Each declaration is a dict with keys:
      line, turn, kind ('braced'|'tuple'|'unit'), elided (bool),
      shape (tuple of (name, type) for braced; tuple of types for tuple),
      raw_shape (same, with module paths and visibility left in place),
      raw_vis (per-field visibility prefixes), generics (own type parameters)

    A shape is the set of (field_name, field_type) pairs. Visibility and module
    paths are NOT part of a shape; both kinds of difference are reported in
    their own buckets so they are never mistaken for a field-set divergence.
    """
    n = len(lines)
    turns = turn_map(lines)
    decls: dict[str, list[dict]] = collections.defaultdict(list)
    i = 0
    while i < n:
        m = DECL.match(lines[i])
        if not m:
            i += 1
            continue
        name, rest = m.group(1), m.group(2).strip()
        line = i + 1
        turn = turns[i]

        if rest.startswith("("):  # tuple struct
            txt = rest
            j = i
            while txt.count("(") > txt.count(")") and j + 1 < n:
                j += 1
                txt += " " + lines[j].strip()
            inner = txt[txt.index("(") + 1 : txt.rindex(")")]
            raw_fields = tuple(
                re.sub(r"\s+", " ", part).strip().rstrip(",")
                for part in _split_top_level(inner) if part.strip()
            )
            fields = tuple(_norm_type(f) for f in raw_fields)
            decls[name].append(
                dict(line=line, turn=turn, kind="tuple", elided=False,
                     shape=fields, raw_shape=raw_fields, raw_vis=(),
                     generics=tuple(_generic_params(rest)))
            )
            i = j + 1
            continue

        if rest.startswith(";") or rest == "":  # unit struct
            decls[name].append(
                dict(line=line, turn=turn, kind="unit", elided=False,
                     shape=(), raw_shape=(), raw_vis=(),
                     generics=tuple(_generic_params(rest)))
            )
            i += 1
            continue

        if "{" in rest:  # braced struct
            depth = rest.count("{") - rest.count("}")
            body = [rest[rest.index("{") + 1 :]]
            j = i
            while depth > 0 and j + 1 < n:
                j += 1
                depth += lines[j].count("{") - lines[j].count("}")
                body.append(lines[j])
            shape: list[tuple[str, str]] = []
            raw_shape: list[tuple[str, str]] = []
            vis: list[str] = []
            cleaned, elided = _clean_body(body)
            for frag in _split_top_level(cleaned):
                raw = " ".join(frag.split("\n")).strip()
                raw = raw.rstrip("}").strip().rstrip(",").strip()
                if not raw:
                    continue
                fm = FIELD.match(raw)
                if fm:
                    shape.append((fm.group(1), _norm_type(fm.group(2))))
                    raw_shape.append((fm.group(1), fm.group(2).strip()))
                    vm = VIS.match(raw)
                    vis.append(vm.group(0).strip() if vm else "")
                elif raw.startswith(("fn ", "pub fn ", "impl ")):
                    continue  # stray method sketch inside the braces
                else:
                    elided = True  # body we cannot parse: treat as elided
            decls[name].append(
                dict(line=line, turn=turn, kind="braced", elided=elided,
                     shape=tuple(shape), raw_shape=tuple(raw_shape),
                     raw_vis=tuple(vis),
                     generics=tuple(_generic_params(rest)))
            )
            i = j + 1
            continue

        i += 1
    return decls


def _key(d) -> tuple:
    """Shape identity, insensitive to field ORDER (order-only drift is a weaker
    fact and is bucketed separately in the report)."""
    return tuple(sorted(str(f) for f in d["shape"]))


def _fmt(shape) -> str:
    return ", ".join(("%s: %s" % f) if isinstance(f, tuple) else str(f)
                     for f in shape) or "-"


def report(decls, only=None) -> int:
    names = sorted(decls)
    if only:
        names = [x for x in names if x in only]
    multi = [x for x in names if len(decls[x]) > 1]
    div = []
    for x in names:
        real = [d for d in decls[x] if not d["elided"]]
        if len({_key(d) for d in real}) > 1:
            div.append((x, real))
    print("struct declarations: %d distinct names, %d declared more than once, "
          "%d total declarations" % (len(names), len(multi),
                                     sum(len(decls[x]) for x in names)))
    print("names with >1 distinct non-elided field set: %d\n" % len(div))
    for x, real in div:
        keys = []
        for d in real:
            if _key(d) not in keys:
                keys.append(_key(d))
        print("### %s  (%d decls, %d shapes)" % (x, len(decls[x]), len(keys)))
        for d in decls[x]:
            if d["elided"]:
                tag = "ELIDED"
            else:
                tag = "shape%d" % (keys.index(_key(d)) + 1)
                same = [e for e in real if _key(e) == _key(d)]
                if len(same) > 1 and same[0] is not d:
                    tag += " (field order differs from L%d)" % same[0]["line"]
            print("  L%-6d turn[%-3d] %-7s %s"
                  % (d["line"], d["turn"], tag, _fmt(d["shape"])))
        print()

    vis_only = []
    for x in names:
        real = [d for d in decls[x] if not d["elided"]]
        if len({_key(d) for d in real}) == 1 and len({d["raw_vis"] for d in real}) > 1:
            vis_only.append(x)
    if vis_only:
        print("visibility-only differences (NOT a shape divergence): %s"
              % ", ".join(vis_only))
    elided_names = [x for x in names if any(d["elided"] for d in decls[x])]
    if elided_names:
        print("declarations with an elided/unparseable body (excluded from "
              "shape comparison): %s" % ", ".join(elided_names))
    return len(div)


def undeclared_field_types(lines, decls, edecls=None):
    """Every type name used in a field position that is never declared.

    Covers struct fields and enum variant payloads. Excludes primitives, `std`
    collections, each declaration's own generic parameters, and types reached
    through a module path (external crates such as `slotmap::DefaultKey`).
    Returns name -> sorted list of use lines.
    """
    declared = set()
    any_decl = re.compile(
        r"\b(?:pub(?:\([^)]*\))?\s+)?(?:struct|enum|trait|type|union)\s+"
        r"([A-Z][A-Za-z0-9_]*)\b")
    for x in lines:
        for m in any_decl.finditer(x):
            declared.add(m.group(1))

    def type_names(text):
        for m in re.finditer(r"\b([A-Z][A-Za-z0-9_]*)\b", text):
            yield m.group(1)

    uses: dict[str, set[int]] = {}
    for name, ds in decls.items():
        for d in ds:
            skip = set(d["generics"]) | PRIMITIVE_TYPES | STD_TYPES
            for norm, raw in zip(d["shape"], d["raw_shape"] or d["shape"]):
                ftype = norm[1] if isinstance(norm, tuple) else norm
                rawtext = raw[1] if isinstance(raw, tuple) else raw
                for tn in type_names(ftype):
                    if tn in skip:
                        continue
                    if re.search(r"\b[A-Za-z_][A-Za-z0-9_]*::[^:]*\b%s\b" % tn,
                                 rawtext):
                        continue  # reached through a module path: external crate
                    uses.setdefault(tn, set()).add(d["line"])
    for name, ds in (edecls or {}).items():
        for d in ds:
            skip = set(d["generics"]) | PRIMITIVE_TYPES | STD_TYPES
            for variant in d["variants"]:
                payload = variant[variant.index("{") + 1:] if "{" in variant else (
                    variant[variant.index("(") + 1:] if "(" in variant else "")
                for tn in type_names(payload):
                    if tn in skip:
                        continue
                    uses.setdefault(tn, set()).add(d["line"])
    return {k: sorted(v) for k, v in uses.items() if k not in declared}


def report_enums(edecls, only=None) -> int:
    names = sorted(edecls)
    if only:
        names = [x for x in names if x in only]
    div = []
    for x in names:
        real = [d for d in edecls[x] if not d["elided"]]
        if len({d["variants"] for d in real}) > 1:
            div.append(x)
    print("enum declarations: %d distinct names, %d declared more than once, "
          "%d total declarations"
          % (len(names), sum(1 for x in names if len(edecls[x]) > 1),
             sum(len(edecls[x]) for x in names)))
    print("names with >1 distinct non-elided variant set: %d\n" % len(div))
    for x in div:
        real = [d for d in edecls[x] if not d["elided"]]
        keys = []
        for d in real:  # elided declarations are shown but never counted
            if d["variants"] not in keys:
                keys.append(d["variants"])
        print("### %s  (%d decls, %d variant sets)"
              % (x, len(edecls[x]), len(keys)))
        for d in edecls[x]:
            tag = "ELIDED" if d["elided"] else "vset%d" % (keys.index(d["variants"]) + 1)
            bare = [v.split("{")[0].split("(")[0] for v in d["variants"]]
            print("  L%-6d turn[%-3d] %-7s %d variants: %s"
                  % (d["line"], d["turn"], tag, len(d["variants"]),
                     ", ".join(bare)))
        # per-variant-set diff for the common case of two sets
        if len(keys) == 2:
            a = {v.split("{")[0].split("(")[0] for v in keys[0]}
            b = {v.split("{")[0].split("(")[0] for v in keys[1]}
            if a - b:
                print("      only in vset1: %s" % ", ".join(sorted(a - b)))
            if b - a:
                print("      only in vset2: %s" % ", ".join(sorted(b - a)))
        print()
    return len(div)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--struct", action="append", default=None)
    ap.add_argument("--enums", action="store_true",
                    help="report enum variant-set divergences instead of structs")
    ap.add_argument("--undeclared", action="store_true",
                    help="list type names used in field positions that are "
                         "never declared anywhere in the source")
    args = ap.parse_args(argv)
    lines = read_lines()
    decls = sweep(lines)
    edecls = enum_sweep(lines)
    only = set(args.struct) if args.struct else None
    if args.json:
        out = {}
        for x in sorted(decls):
            if only and x not in only:
                continue
            out[x] = [
                dict(line=d["line"], turn=d["turn"], kind=d["kind"],
                     elided=d["elided"],
                     shape=[list(f) if isinstance(f, tuple) else f
                            for f in d["shape"]])
                for d in decls[x]
            ]
        json.dump(out, sys.stdout, indent=1)
        print()
        return 0
    if args.undeclared:
        missing = undeclared_field_types(lines, decls, edecls)
        print("type names used in struct/enum field positions but never "
              "declared: %d" % len(missing))
        for k in sorted(missing, key=lambda k: (-len(missing[k]), k)):
            print("  %-24s uses=%d  first_lines=%s"
                  % (k, len(missing[k]), missing[k][:6]))
        return 0
    if args.enums:
        return 0 if report_enums(edecls, only) >= 0 else 1
    report(decls, only)
    return 0


if __name__ == "__main__":
    sys.exit(main())
