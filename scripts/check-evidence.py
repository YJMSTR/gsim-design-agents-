#!/usr/bin/env python3
"""Check that a task workspace has the expected evidence files."""
from __future__ import annotations

import argparse
from pathlib import Path

REQUIRED = [
    'docs/task-contract.md',
    'docs/draft.md',
    'docs/plan.md',
    'benchmark.csv',
    'candidates.jsonl',
]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--workspace', default='.')
    args = parser.parse_args()
    root = Path(args.workspace).resolve()
    missing = [rel for rel in REQUIRED if not (root / rel).exists()]
    if missing:
        print('missing evidence files:')
        for rel in missing:
            print(f'- {rel}')
        return 1
    print(f'evidence skeleton OK: {root}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
