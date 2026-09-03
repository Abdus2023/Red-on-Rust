#!/usr/bin/env python3
"""FINAL1 support: parsers for the cleaned input registers.

Import-only module (used by final/_build.py). Parses the frozen input
documents (spec/01, spec/03, spec/06, spec/08, spec/09, term/03, mod/18)
into structures the compiler re-emits verbatim where possible, so no
normative text is ever retyped by hand.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


def read(rel: str) -> str:
    return (REPO / rel).read_text(encoding="utf-8")


# ---------- spec/01: cleaned canonical specification ------------------------

SEC_HEAD = re.compile(r'^## (S-\d\d) (.*)$')
PART_HEAD = re.compile(r'^# Part .*$', re.M)
CHUNK_HEAD = re.compile(r'^\*\*(R-[A-Z]+-\d+)')


def parse_spec01():
    """Return {section_id: {"title":..., "chunks":[(rid_or_None, text)]}}.

    text is the chunk body verbatim (the leading `**RID ...**` bold opener is
    kept inside text so the rendering stays byte-identical to the source).
    Chunks whose head is not an R-... requirement are (None, text) orphans.
    """
    src = read('spec/01-canonical-specification.md')
    lines = src.split('\n')
    sections = {}
    cur = None
    cur_chunk = None  # [rid, [lines]]
    for ln in lines:
        m = SEC_HEAD.match(ln)
        if m:
            if cur is not None:
                _close(cur_chunk, cur)
            cur = {'title': m.group(2).strip(), 'chunks': []}
            cur_chunk = None
            sections[m.group(1)] = cur
            continue
        if cur is None:
            continue
        if ln.startswith('# '):  # Part header or End marker: section boundary
            _close(cur_chunk, cur)
            cur_chunk = None
            cur = None
            continue
        m2 = CHUNK_HEAD.match(ln)
        if m2:
            _close(cur_chunk, cur)
            cur_chunk = [m2.group(1), [ln]]
        elif cur_chunk is not None:
            cur_chunk[1].append(ln)
        else:
            # orphan line before the first R chunk of the section
            if cur['chunks'] and cur['chunks'][-1][0] is None:
                cur['chunks'][-1][1].append(ln)
            else:
                cur['chunks'].append((None, [ln]))
    if cur is not None:
        _close(cur_chunk, cur)
    # normalize: store chunk text as stripped joined lines
    for sid, s in sections.items():
        s['chunks'] = [(rid, '\n'.join(t).strip('\n')) for rid, t in s['chunks']]
    return sections


def _close(cur_chunk, cur):
    if cur_chunk is not None and any(x.strip() for x in cur_chunk[1]):
        cur['chunks'].append((cur_chunk[0], cur_chunk[1]))


# ---------- spec/03: obligation matrix rows ---------------------------------

def parse_spec03():
    """Return list of dict rows in file order (184 rows)."""
    rows = []
    for ln in read('spec/03-obligation-matrix.md').split('\n'):
        m = re.match(r'^\| (R-[A-Z]+-\d+) \|', ln)
        if not m:
            continue
        cells = [c.strip() for c in ln.strip().strip('|').split('|')]
        # split on unescaped pipes only; cells must be exactly 6
        rows.append({'id': cells[0], 'short': cells[1], 'prov': cells[2],
                     'status': cells[3], 'impl': cells[4], 'verify': cells[5]})
    return rows


# ---------- spec/06: contradictions register --------------------------------

def parse_spec06():
    rows = {}
    txt = read('spec/06-contradictions-ambiguities.md')
    for m in re.finditer(r'^\| (C-\d+) \|(.*)$', txt, re.M):
        rest = m.group(2)
        # severity = first cell; status = fifth cell (0-based: title,sev,src,status)
        cells = [c.strip() for c in rest.split('|')]
        if len(cells) < 4:
            continue
        cid = m.group(1)
        status = cells[3].strip() if len(cells) > 3 else ''
        rows[cid] = {'sev': cells[1], 'status': status, 'status_full': status}
    return rows


# ---------- spec/09: unresolved decisions ------------------------------------

def parse_spec09():
    txt = read('spec/09-unresolved-decisions.md')
    items = []
    heads = list(re.finditer(r'^### (U-\d+) — (.*)$', txt, re.M))
    for i, h in enumerate(heads):
        end = heads[i + 1].start() if i + 1 < len(heads) else len(txt)
        body = txt[h.start():end]
        rid, title = h.group(1), h.group(2).strip()
        resolved = bool(re.search(r'\*\*Resolved \(', body))
        retired = 'RETIRED by decision' in body
        items.append({'id': rid, 'title': title, 'body': body,
                      'resolved': resolved or retired})
    return items


# ---------- term/03 laws table ------------------------------------------------

def parse_laws():
    txt = read('term/03-laws.md')
    rows = []
    for m in re.finditer(r'^\| \[(N-\d+)\]\(#n-\d+\) \|([^|]*)\|([^|]*)\|([^|]*)\|$', txt, re.M):
        rows.append({'id': m.group(1), 'law': m.group(2).strip(),
                     'mandate': m.group(3).strip(), 'enforce': m.group(4).strip()})
    return rows


# ---------- mod/18 duplication register ---------------------------------------

def parse_dupreg():
    txt = read('mod/18-ownership-matrix.md')
    rows = []
    for m in re.finditer(r'^\| (D-\d+) \|([^|]*)\|([^|]*)\|([^|]*)\|(.*)\|$', txt, re.M):
        rows.append({'id': m.group(1), 'kind': m.group(2).strip(),
                     'members': m.group(3).strip(), 'canonical': m.group(4).strip(),
                     'note': m.group(5).strip()})
    return rows


# ---------- machine indexes ---------------------------------------------------

def load_term_index():
    return json.loads(read('term/10-index.json'))


def load_spec_index():
    return json.loads(read('spec/10-index.json'))


def load_registry():
    return json.loads(read('req/registry.json'))


if __name__ == '__main__':
    secs = parse_spec01()
    rid_total = []
    orphans = []
    for sid, s in sorted(secs.items()):
        for rid, text in s['chunks']:
            if rid:
                rid_total.append(rid)
            else:
                orphans.append((sid, text.split('\n')[0][:70]))
    print('sections:', len(secs), sorted(secs))
    print('R chunks:', len(rid_total), 'unique:', len(set(rid_total)))
    print('orphans:')
    for o in orphans:
        print('  ', o)
