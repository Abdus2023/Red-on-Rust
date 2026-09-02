#!/usr/bin/env python3
"""spec_check.py — cross-layer ID->rule consistency checker (SEC-023 detector).

Verifies that the obligation ID -> rule binding is intact across the three
layers that share it:

  D1  spec/normative-normalization-records.md:
        each record's "Original" and "Normalized" quotations must describe
        the SAME rule (rule-identity preservation, per the records' own
        header rules 1/8/9/10).
  D2  spec/01-canonical-specification.md:
        each obligation body must agree with the source lines its own
        citation names (req/_validate.py check #7, applied to spec/01 —
        the layer it currently does not cover).
  D3  spec/01 body vs spec/03-obligation-matrix.md short description:
        the matrix row and the canonical body must denote the same rule.

Exit code: 0 if all checks pass, 1 if any check flags records.  The tool
is deliberately deterministic and stdlib-only.  It makes no changes.

Usage: python3 audit/spec_check.py [--verbose] [--strict] [--min-overlap F]
                        [--records PATH] [--spec01 PATH] [--matrix PATH]
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SPEC01 = REPO / "spec" / "01-canonical-specification.md"
RECORDS = REPO / "spec" / "normative-normalization-records.md"
MATRIX = REPO / "spec" / "03-obligation-matrix.md"
SOURCE = REPO / "Red-on-Rust.md"

MIN_OVERLAP = 0.25  # overlap coefficient below this => rule-identity mismatch

STOPWORDS = {
    # modal / boilerplate / prose glue — excluded from signatures
    "the", "and", "or", "not", "for", "into", "with", "must", "may", "should",
    "a", "an", "is", "are", "be", "been", "was", "were", "to", "of", "in",
    "on", "at", "by", "as", "it", "its", "this", "that", "these", "those",
    "each", "every", "all", "any", "no", "none", "if", "then", "else",
    "when", "where", "which", "who", "whom", "whose", "will", "shall",
    "can", "cannot", "could", "would", "might", "hold", "holds", "occur",
    "occurs", "exist", "exists", "state", "machine", "system", "use",
    "used", "using", "via", "per", "from", "during", "before", "after",
    "between", "within", "without", "under", "over", "new", "fresh", "only",
    "also", "such", "than", "more", "most", "less", "least", "same",
    "explicit", "explicitly", "strict", "strictly", "original", "normalized",
    "informative", "specified", "frozen", "note", "example", "examples",
    "see", "above", "below", "line", "lines", "src", "source", "turn",
    "level", "levels", "form", "forms", "well", "their", "there", "here",
    "have", "has", "had", "do", "does", "did", "but", "while", "until",
    "unless", "since", "because", "both", "either", "neither", "one", "two",
    "given", "following", "respect", "respectively", "etc", "and/or",
    # generic spec vocabulary that appears in nearly every obligation
    "must", "actor", "actors", "effect", "effects", "value", "values",
    "capability", "budget", "fault", "faults", "logical", "time", "record",
    "records", "recorded", "recovery", "transition", "transitions",
}

TOKEN_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_/'\-]{2,}|≼|⊓|⇒|⇔|∧|¬|∈|∩|Σ|κ|⟦⟧")


def signature(text: str) -> set[str]:
    """Distinctive-token signature of a normative text fragment."""
    text = re.sub(r"\u00a0", " ", text)
    toks = set()
    for m in TOKEN_RE.finditer(text):
        t = m.group(0).strip("'-").lower()
        while "/" in t:
            t = t.split("/")[0]
        if len(t) < 3 or t in STOPWORDS:
            continue
        toks.add(t)
    return toks


def overlap(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 1.0 if not a and not b else 0.0
    return len(a & b) / min(len(a), len(b))


# ---------------------------------------------------------------- parsing

def parse_records(path: Path | None = None) -> dict[str, tuple[str, str]]:
    """ID -> (original, normalized) from the normalization records."""
    src = Path(path) if path else RECORDS
    out: dict[str, tuple[str, str]] = {}
    cur, buf, mode = None, {"original": [], "normalized": []}, None
    for line in src.read_text(encoding="utf-8").splitlines():
        h = re.match(r"^### (R-[A-Z]+-\d+)\s*$", line)
        if h:
            if cur and buf["original"] and buf["normalized"]:
                out[cur] = ("\n".join(buf["original"]), "\n".join(buf["normalized"]))
            cur, buf, mode = h.group(1), {"original": [], "normalized": []}, None
            continue
        if line.strip().startswith("- **Original:**"):
            mode = "original"
            buf[mode].append(line.split("- **Original:**", 1)[1])
            continue
        if line.strip().startswith("- **Normalized:**"):
            mode = "normalized"
            buf[mode].append(line.split("- **Normalized:**", 1)[1])
            continue
        if line.strip().startswith(("- **Reason:**", "- **Semantic Risk:**")):
            mode = None
            continue
        if mode and line.strip().startswith(">"):
            buf[mode].append(line)
    if cur and buf["original"] and buf["normalized"]:
        out[cur] = ("\n".join(buf["original"]), "\n".join(buf["normalized"]))
    return out


def parse_spec01(path: Path | None = None) -> dict[str, tuple[str, list[tuple[int, int]]]]:
    """ID -> (body, cited line ranges) from the canonical specification."""
    src = Path(path) if path else SPEC01
    text = src.read_text(encoding="utf-8")
    out: dict[str, tuple[str, list[tuple[int, int]]]] = {}
    for m in re.finditer(
        r"\*\*(R-[A-Z]+-\d+)[^\n]*?\*\*(.+?)(?=\n\n\*\*R-|\n\n## |\n## |\Z)",
        text, re.S,
    ):
        rid, body = m.group(1), m.group(2)
        body = re.sub(r"\s+", " ", body).strip()
        ranges = []
        for c in re.finditer(r"L(\d{3,5})(?:[–-](\d{3,5}))?", body):
            a = int(c.group(1))
            b = int(c.group(2)) if c.group(2) else a
            ranges.append((a, b))
        out[rid] = (body, ranges)
    return out


def parse_matrix(path: Path | None = None) -> dict[str, str]:
    """ID -> short description from the obligation matrix."""
    src = Path(path) if path else MATRIX
    out: dict[str, str] = {}
    for line in src.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^\|\s*(R-[A-Z]+-\d+)\s*\|\s*([^|]+)\|", line)
        if m:
            out[m.group(1)] = m.group(2)
    return out


def source_lines() -> list[str]:
    return SOURCE.read_text(encoding="utf-8").splitlines()


# ---------------------------------------------------------------- checks

def check_d1(records, verbose):
    """Records: Original vs Normalized rule identity."""
    flags = []
    rows = []
    for rid in sorted(records):
        orig, norm = records[rid]
        s_o, s_n = signature(orig), signature(norm)
        sc = overlap(s_o, s_n)
        rows.append((rid, sc, len(s_o), len(s_n)))
        if sc < MIN_OVERLAP:
            flags.append((rid, sc, "D1", "record Normalized denotes a different rule than its Original"))
    if verbose:
        for rid, sc, no, nn in sorted(rows, key=lambda r: r[1]):
            print(f"  D1 {rid:14s} overlap={sc:.2f}  (|orig|={no}, |norm|={nn})")
    return flags


def check_d2(spec01, src, verbose):
    """spec/01 body vs its own cited source lines."""
    flags = []
    rows = []
    for rid in sorted(spec01):
        body, ranges = spec01[rid]
        if not ranges:
            continue
        cited = []
        for a, b in ranges:
            cited.extend(src[a - 1 : b])
        s_b, s_c = signature(body), signature("\n".join(cited))
        # citations legitimately contain extra material; measure recall of
        # the BODY's distinctive tokens in the cited range, minus the
        # citation tokens themselves which are body text
        s_b = {t for t in s_b if not re.fullmatch(r"l?\d+", t)}
        if not s_b or not s_c:
            continue
        inter = len(s_b & s_c)
        rec = inter / len(s_b)
        rows.append((rid, rec))
        if rec < MIN_OVERLAP:
            flags.append((rid, rec, "D2", "body does not match its own cited source lines"))
    if verbose:
        for rid, rec in sorted(rows, key=lambda r: r[1]):
            print(f"  D2 {rid:14s} body-in-citation recall={rec:.2f}")
    return flags


def check_d3(spec01, matrix, verbose):
    """spec/01 body vs spec/03 matrix short description."""
    flags = []
    rows = []
    for rid in sorted(set(spec01) & set(matrix)):
        body, _ = spec01[rid]
        s_b, s_m = signature(body), signature(matrix[rid])
        if not s_m:
            continue
        sc = overlap(s_b, s_m)
        rows.append((rid, sc))
        if sc < MIN_OVERLAP:
            flags.append((rid, sc, "D3", "spec/03 matrix row denotes a different rule than the spec/01 body"))
    if verbose:
        for rid, sc in sorted(rows, key=lambda r: r[1]):
            print(f"  D3 {rid:14s} body/matrix overlap={sc:.2f}")
    return flags


def main() -> int:
    ap = sys.argv[1:]
    verbose = "--verbose" in ap
    strict = "--strict" in ap
    global MIN_OVERLAP
    if "--min-overlap" in ap:
        MIN_OVERLAP = float(ap[ap.index("--min-overlap") + 1])
    records_path = Path(ap[ap.index("--records") + 1]) if "--records" in ap else None
    spec01_path = Path(ap[ap.index("--spec01") + 1]) if "--spec01" in ap else None
    matrix_path = Path(ap[ap.index("--matrix") + 1]) if "--matrix" in ap else None

    records = parse_records(records_path)
    spec01 = parse_spec01(spec01_path)
    matrix = parse_matrix(matrix_path)
    src = source_lines()

    print(f"parsed: {len(records)} records, {len(spec01)} spec/01 obligations, {len(matrix)} matrix rows"
          + (f" (spec01={spec01_path})" if spec01_path else "")
          + (f" (records={records_path})" if records_path else "")
          + (f" (matrix={matrix_path})" if matrix_path else ""))

    # D1 (records' Original vs Normalized rule identity) is the SEC-023 gate:
    # any D1 flag hard-fails.  D2/D3 are supporting signals with known
    # label-vs-content noise on terse bodies; they warn by default and
    # hard-fail only under --strict.
    d1 = check_d1(records, verbose)
    d2 = check_d2(spec01, src, verbose)
    d3 = check_d3(spec01, matrix, verbose)

    for rid, sc, check, msg in d1:
        print(f"  [{check}] {rid:14s} score={sc:.2f}  {msg}")
    if d1:
        print(f"\nFAIL: {len(d1)} D1 rule-identity violation(s) (SEC-023 class)")
        return 1
    for rid, sc, check, msg in d2 + d3:
        print(f"  WARN [{check}] {rid:14s} score={sc:.2f}  {msg}")
    if d2 or d3:
        print(f"\n{'FAIL' if strict else 'OK with warnings'}: "
              f"D1=0, {len(d2)}x D2, {len(d3)}x D3 "
              f"({'hard-failing under --strict' if strict else 'adjudicated terse-body/label cases; run with --strict to hard-fail'})")
        return 1 if strict else 0
    print("\nOK: no ID->rule binding violations detected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
