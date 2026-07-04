#!/usr/bin/env python3
"""Initialize a GSim Design Agents task workspace without touching existing GSim runs."""
from __future__ import annotations

import argparse
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def copy_if_missing(src: Path, dst: Path) -> None:
    if dst.exists():
        return
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--workspace', required=True, help='New or existing isolated task workspace')
    args = parser.parse_args()
    workspace = Path(args.workspace).expanduser().resolve()
    workspace.mkdir(parents=True, exist_ok=True)
    for rel in ['docs', 'runs', 'outputs', 'profile']:
        (workspace / rel).mkdir(exist_ok=True)
    copy_if_missing(ROOT / 'templates' / 'task-contract.md', workspace / 'docs' / 'task-contract.md')
    copy_if_missing(ROOT / 'templates' / 'benchmark.csv', workspace / 'benchmark.csv')
    copy_if_missing(ROOT / 'templates' / 'candidates.jsonl', workspace / 'candidates.jsonl')
    print(f'initialized {workspace}')
    print('next: fill docs/task-contract.md, then start from prompts/basic-flow.md')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
