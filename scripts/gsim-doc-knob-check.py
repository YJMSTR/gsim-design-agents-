#!/usr/bin/env python3
"""Doc-knob consistency check: every GSIM_* knob named in the documentation
must exist somewhere the build can honor it.

Knob existence has three legitimate homes (learned from the v86 campaign):
  1. generator getenv:        std::getenv("GSIM_...") in src/|include/
  2. emitted model strings:   the knob name appears as a string literal in
                              generator emission code (runtime knobs are read
                              by the emitted model, not the generator)
  3. build-side variables:    .mk/Makefile text (e.g. GSIM_SORT_GENERATED_SOURCES)

A documented knob found in none of these is a stale-doc bug (like the
GSIM_MT_DENSE_R4 recipe entry that survived weeks with zero code references).
The reverse direction (code knobs missing from docs) is reported as info only:
internal debug/probe knobs legitimately stay undocumented.

Usage:
    gsim-doc-knob-check.py --doc README.md [--doc MORE.md ...] \
        --src DIR [DIR...] [--internal-prefix PREFIX ...]

Exit 0 = every documented knob exists; 1 = stale doc entries found.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

KNOB_RE = re.compile(r'\b(GSIM_[A-Z0-9_]{3,})\b')
TEXT_SUFFIXES = ('.cpp', '.h', '.cc', '.hpp', '.cxx', '.mk')
TEXT_NAMES = ('Makefile', 'makefile')
# Prose fragments that match the knob regex but are not knobs.
NON_KNOBS = {'GSIM_MT_DENSE_'}  # "GSIM_MT_DENSE_* knobs" prefix mentions


def doc_knobs(paths: list[Path]) -> dict[str, set[str]]:
    out: dict[str, set[str]] = {}
    for p in paths:
        text = p.read_text(errors='ignore')
        for k in KNOB_RE.findall(text):
            if k in NON_KNOBS or k.endswith('_'):
                continue
            out.setdefault(k, set()).add(str(p))
    return out


def source_text(dirs: list[Path]) -> str:
    chunks = []
    for d in dirs:
        for p in d.rglob('*'):
            if '.git' in p.parts or not p.is_file():
                continue
            if p.suffix in TEXT_SUFFIXES or p.name in TEXT_NAMES:
                try:
                    chunks.append(p.read_text(errors='ignore'))
                except OSError:
                    pass
    return '\n'.join(chunks)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--doc', nargs='+', required=True, type=Path)
    ap.add_argument('--src', nargs='+', required=True, type=Path)
    ap.add_argument('--internal-prefix', nargs='*',
                    default=['GSIM_DEBUG_', 'GSIM_MT_ACTACC', 'GSIM_MT_ANTICHAIN_',
                             'GSIM_MT_CYCLE_BATCH_', 'GSIM_MT_DENSE_BREAKDOWN_'],
                    help='code knobs with these prefixes are internal; not reported as undocumented')
    args = ap.parse_args()

    docs = doc_knobs(args.doc)
    corpus = source_text(args.src)
    if not corpus:
        print('error: no source text under --src', file=sys.stderr)
        return 2

    stale = sorted(k for k in docs if k not in corpus)
    for k in stale:
        print('STALE DOC KNOB: %s  documented in [%s] but absent from source/build text'
              % (k, ', '.join(sorted(docs[k]))))

    code_knobs = set(KNOB_RE.findall(corpus)) - NON_KNOBS
    undocumented = sorted(k for k in code_knobs - set(docs)
                          if not any(k.startswith(p) for p in args.internal_prefix))
    if undocumented:
        print('info: %d code knobs not documented (internal prefixes excluded):'
              % len(undocumented))
        for k in undocumented[:20]:
            print('  undocumented: ' + k)

    print('documented knobs: %d, stale: %d' % (len(docs), len(stale)))
    return 1 if stale else 0


if __name__ == '__main__':
    sys.exit(main())
