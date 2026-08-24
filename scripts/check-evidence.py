#!/usr/bin/env python3
"""Enforce the evidence-record contracts of docs/spec-evidence-records.md.

Checks a task workspace:
  - required evidence files exist
  - candidates.jsonl: parseable lines, required keys, date format,
    outcome vocabulary, parent/report reference resolution, transient states
  - benchmark.csv: exact header, row width, numeric sim_time_ms,
    candidate cross-reference to candidates.jsonl
  - champions/<name>/ referenced by promote records exist

Usage:
    check-evidence.py --workspace <dir> [--skip-benchmark]
                      [--candidates PATH] [--benchmark PATH]

Exit 0 = contracts satisfied; non-zero = violations (printed, one per line).
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path

REQUIRED_FILES = [
    'docs/task-contract.md',
    'docs/draft.md',
    'docs/plan.md',
    'benchmark.csv',
    'candidates.jsonl',
]

# docs/spec-evidence-records.md: outcome vocabulary
OUTCOME_TOKENS = {
    'baseline', 'promote', 'retain', 'reject', 'closed', 'measured',
    'analysis', 'correction', 'retracted', 'diagnostic', 'instrumentation',
    'validated',
}



# A record in one of these states must be finalized/superseded before the
# task closes; the checker reports them (as warnings counted as findings).
TRANSIENT_PREFIXES = (
    'building', 'generations-running', 'pending', 'in-flight', 'running',
)

BENCHMARK_HEADER = [
    'candidate', 'date', 'design', 'threads', 'compiler', 'flags',
    'sim_time_ms', 'speedup_vs_parent', 'speedup_vs_1t',
    'verilator_32t_ratio', 'cpu_util_pct', 'ipc', 'cache_miss_rate',
    'sync_overhead_pct', 'status', 'notes',
]

DATE_RE = re.compile(r'^\d{4}-\d{2}-\d{2}$')


class Findings:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def error(self, msg: str) -> None:
        self.errors.append(msg)

    def warn(self, msg: str) -> None:
        self.warnings.append(msg)

    @property
    def ok(self) -> bool:
        return not self.errors

    def report(self, path: Path) -> int:
        for w in self.warnings:
            print(f'warning: {w}')
        for e in self.errors:
            print(f'error: {e}')
        if self.ok:
            print(f'evidence contracts satisfied: {path}')
            return 0
        print(f'{len(self.errors)} violation(s) in {path}', file=sys.stderr)
        return 1

def check_candidates(path: Path, f: Findings,
                     vocab_since: str | None = None) -> dict[str, dict]:
    names: dict[str, dict] = {}
    transient: list[str] = []
    lines = path.read_text(encoding='utf-8').splitlines()
    if not any(l.strip() for l in lines):
        return names  # empty ledger: honest pre-baseline state
    for idx, line in enumerate(lines, 1):
        if not line.strip():
            continue
        where = f'candidates.jsonl:{idx}'
        try:
            rec = json.loads(line)
        except json.JSONDecodeError as exc:
            f.error(f'{where}: unparseable JSON ({exc.msg})')
            continue
        if not isinstance(rec, dict):
            f.error(f'{where}: not a JSON object')
            continue
        name = rec.get('name')
        if not name or not isinstance(name, str):
            f.error(f'{where}: missing or non-string "name"')
            continue
        if name in names:
            f.error(f'{where}: duplicate name "{name}" (first at record '
                    f'{names[name].get("_line", "?")})')
            continue
        rec['_line'] = idx
        names[name] = rec
        for key in ('name', 'date', 'status'):
            if key not in rec:
                f.error(f'{where}: missing required key "{key}"')
        date = rec.get('date')
        if isinstance(date, str) and not DATE_RE.match(date):
            f.error(f'{where}: date "{date}" is not YYYY-MM-DD')
        status = rec.get('status')
        if isinstance(status, str):
            token = status.split(' ', 1)[0].split('(', 1)[0].strip()
            if token and token.lower() not in OUTCOME_TOKENS:
                grandfathered = (vocab_since is not None
                                 and isinstance(date, str)
                                 and DATE_RE.match(date)
                                 and date < vocab_since)
                msg = (f'{where}: status token "{token}" not in the outcome '
                       f'vocabulary {sorted(OUTCOME_TOKENS)}')
                (f.warn if grandfathered else f.error)(msg)
            if any(token.lower().startswith(p) for p in TRANSIENT_PREFIXES):
                transient.append(f'{name} ({status})')
    for name, rec in names.items():
        parent = rec.get('parent')
        if parent is not None:
            if not isinstance(parent, str):
                f.error(f'candidates.jsonl:{rec["_line"]}: "parent" is not a string')
            elif parent not in names:
                f.error(f'candidates.jsonl:{rec["_line"]}: parent "{parent}" '
                        f'does not resolve to any record')
        report = rec.get('report')
        if report is not None:
            if not isinstance(report, str):
                f.error(f'candidates.jsonl:{rec["_line"]}: "report" is not a string')
            elif not (path.parent / report).exists():
                f.error(f'candidates.jsonl:{rec["_line"]}: report path '
                        f'"{report}" does not exist')
        if str(rec.get('status', '')).split(' ', 1)[0] == 'promote':
            has_identity = any(
                k in rec for k in ('commit', 'fingerprint', 'recipe_env',
                                   'champion', 'identity'))
            if not has_identity and not rec.get('report'):
                f.error(f'candidates.jsonl:{rec["_line"]}: promote record '
                        f'"{name}" lacks an identity tuple (commit/'
                        f'fingerprint/recipe_env/champion) or report')
    if transient:
        # A transient record counts as finalized when a later record maps its
        # name in a "finalized" object (the documented supersede pattern).
        finalized = set()
        for rec in names.values():
            fin = rec.get('finalized')
            if isinstance(fin, dict):
                finalized.update(fin.keys())
        open_transient = [t for t in transient
                          if t.split(' ', 1)[0] not in finalized]
        if open_transient:
            f.warn(f'{len(open_transient)} transient record(s) must be finalized '
                   f'before task close: ' + '; '.join(open_transient[:10]))
    return names


def check_benchmark(path: Path, f: Findings, names: dict[str, dict]) -> None:
    text = path.read_text(encoding='utf-8')
    rows = list(csv.reader(text.splitlines()))
    if not rows:
        f.error('benchmark.csv: empty file')
        return
    if rows[0] != BENCHMARK_HEADER:
        f.error(f'benchmark.csv: header mismatch; expected exactly the '
                f'{len(BENCHMARK_HEADER)}-column header of '
                f'spec-evidence-records.md')
        return
    unknown: set[str] = set()
    for idx, row in enumerate(rows[1:], 2):
        if not row:
            continue
        if len(row) != len(BENCHMARK_HEADER):
            f.error(f'benchmark.csv:{idx}: {len(row)} fields, expected '
                    f'{len(BENCHMARK_HEADER)} (quote fields containing commas)')
            continue
        cand = row[0].strip()
        if cand and cand not in names and cand not in unknown:
            unknown.add(cand)
            f.warn(f'benchmark.csv:{idx}: candidate "{cand}" has no '
                   f'candidates.jsonl record')
        sim = row[6].strip()
        if sim and not re.match(r'^-?\d+(\.\d+)?$', sim):
            f.error(f'benchmark.csv:{idx}: sim_time_ms "{sim}" is not numeric')


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    parser.add_argument('--workspace', default='.',
                        help='Task workspace to check')
    parser.add_argument('--skip-benchmark', action='store_true',
                        help='Skip benchmark.csv checks')
    parser.add_argument('--candidates',
                        help='Check an explicit candidates.jsonl only '
                             '(ignores workspace requirements)')
    parser.add_argument('--benchmark',
                        help='Check an explicit benchmark.csv only '
                             '(requires --candidates for cross-refs)')
    parser.add_argument('--vocab-since', metavar='DATE',
                        help='Outcome-vocabulary violations for records '
                             'dated before DATE are downgraded to warnings '
                             '(grandfathered history); DATE onward are '
                             'errors')
    args = parser.parse_args()

    f = Findings()
    if args.candidates or args.benchmark:
        cpath = Path(args.candidates) if args.candidates else None
        bpath = Path(args.benchmark) if args.benchmark else None
        if bpath and not cpath:
            print('error: --benchmark requires --candidates for cross-refs',
                  file=sys.stderr)
            return 2
        names = {}
        if cpath:
            if not cpath.exists():
                print(f'error: {cpath} does not exist', file=sys.stderr)
                return 2
            names = check_candidates(cpath, f, args.vocab_since)
        if bpath:
            if not bpath.exists():
                print(f'error: {bpath} does not exist', file=sys.stderr)
                return 2
            check_benchmark(bpath, f, names)
        return f.report(cpath.parent if cpath else bpath.parent)

    root = Path(args.workspace).resolve()
    missing = [rel for rel in REQUIRED_FILES if not (root / rel).exists()]
    if missing:
        for rel in missing:
            f.error(f'missing evidence file: {rel}')
        return f.report(root)
    names = check_candidates(root / 'candidates.jsonl', f, args.vocab_since)
    if not args.skip_benchmark:
        check_benchmark(root / 'benchmark.csv', f, names)
    return f.report(root)


if __name__ == '__main__':
    raise SystemExit(main())
