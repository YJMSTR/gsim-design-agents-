#!/usr/bin/env python3
"""Knob liveness lint: every GSIM_* environment variable referenced by run
scripts must actually be read by the generator source.

The campaign accumulated dead knobs (e.g. GSIM_MT_DENSE_R4=0 sat in the
champion recipe for weeks with zero code references). Dead knobs are worse
than absent knobs: they suggest a mechanism that does not exist, and they
silently rot when the code path is removed.

Usage:
    gsim-knob-lint.py --scripts GLOB [GLOB...] --src DIR [--src DIR...]
                      [--allow KNOWN_DEAD ...]

Scans each script for GSIM-style identifiers (GSIM_[A-Z0-9_]+) and checks that
each appears in at least one source file under each --src dir (plain text
search over *.cpp/*.h). Knobs listed via --allow are reported as known-dead
but do not fail the lint (use this to retire a knob in two commits: mark
allow-listed, then remove from scripts).

Exit 0 = all referenced knobs are live (or allow-listed); 1 = dead knobs found.
"""
from __future__ import annotations

import argparse
import glob as globmod
import re
import sys
from pathlib import Path

KNOB_RE = re.compile(r'\b(GSIM_[A-Z0-9_]+)\b')
SOURCE_SUFFIXES = ('.cpp', '.h', '.cc', '.hpp', '.cxx')


def script_knobs(path: Path) -> set[str]:
    try:
        text = path.read_text(errors='ignore')
    except OSError:
        return set()
    return set(KNOB_RE.findall(text))


def source_corpus(dirs: list[Path]) -> str:
    chunks = []
    for d in dirs:
        for suf in SOURCE_SUFFIXES:
            for p in d.rglob('*' + suf):
                if '.git' in p.parts:
                    continue
                try:
                    chunks.append(p.read_text(errors='ignore'))
                except OSError:
                    pass
    return '\n'.join(chunks)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--scripts', nargs='+', required=True,
                    help='shell script paths or globs to scan')
    ap.add_argument('--src', nargs='+', required=True, type=Path,
                    help='source dirs of the generator (searched recursively)')
    ap.add_argument('--allow', nargs='*', default=[],
                    help='knobs known-dead, reported but not failing')
    args = ap.parse_args()

    corpus = source_corpus(args.src)
    if not corpus:
        print('error: no source text found under --src dirs', file=sys.stderr)
        return 2

    allow = set(args.allow)
    knob_to_scripts: dict[str, set[str]] = {}
    for pat in args.scripts:
        matches = globmod.glob(pat) or ([pat] if Path(pat).is_file() else [])
        for m in matches:
            for k in script_knobs(Path(m)):
                knob_to_scripts.setdefault(k, set()).add(m)

    dead = sorted(k for k in knob_to_scripts if k not in corpus)
    failing = [k for k in dead if k not in allow]
    allowed = [k for k in dead if k in allow]

    for k in allowed:
        print('known-dead (allow-listed): %s  [%s]' % (k, ', '.join(sorted(knob_to_scripts[k]))))
    for k in failing:
        print('DEAD KNOB: %s  referenced by [%s] but absent from source'
              % (k, ', '.join(sorted(knob_to_scripts[k]))))

    live = len(knob_to_scripts) - len(dead)
    print('knobs: %d referenced, %d live, %d dead (%d allow-listed)'
          % (len(knob_to_scripts), live, len(dead), len(allowed)))
    return 1 if failing else 0


if __name__ == '__main__':
    sys.exit(main())
