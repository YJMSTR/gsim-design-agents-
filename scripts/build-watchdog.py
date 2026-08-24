#!/usr/bin/env python3
"""Watchdog for gsim emu builds: rescue optimizer-explosive translation units.

Symptom (three incidents in the 2026-08 campaign): instrumented/patched models
wrap hundreds of thousands of sites; a few heaviest TUs then explode the -O3
optimizer (observed: 2h47m on SimTop682/683 and counting). make waits on the
straggler while the other 47 slots idle.

This watchdog polls the build's clang processes; any TU compiling longer than
--threshold seconds is killed and recompiled at -O1 into the make-expected
object path (<BUILD_DIR>/gsim-compile/model/<Name>.o), so make's next pass
finds the object and links. Ratios counted by instrumentation are
optimizer-independent, so -O1 objects are valid for census/report builds.
For performance-candidate builds use a clean -O3 build instead (the watchdog
reports which TUs it downgraded so you can decide).

Usage:
  build-watchdog.py --build-dir /tmp/t16-rc2 [--threshold 1200] [--interval 60]
                    [--max-rescues 40] [--make-cmd "make gsim-build-emu ..."]
Stop conditions: emu exists (success), no clang AND no make alive (failure),
or --max-rescues exceeded.
"""
from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
import time
from pathlib import Path

CLANG_RE = re.compile(r'(SimTop\d+)\.cpp')


def find_stragglers(threshold: int) -> list[tuple[int, str, str]]:
    """Return [(pid, tu_stem, build_dir)] for clang compiles older than threshold."""
    out = []
    for pid in filter(str.isdigit, os.listdir('/proc')):
        try:
            cmdline = open(f'/proc/{pid}/cmdline', 'rb').read().decode('utf-8', 'replace')
        except OSError:
            continue
        if 'clang' not in cmdline or '.cpp' not in cmdline:
            continue
        m = CLANG_RE.search(cmdline)
        if not m:
            continue
        parts = cmdline.split('\0')
        # locate the model dir to derive build dir
        model_dir = None
        for i, p in enumerate(parts):
            if p.endswith('.cpp') and '/model/' in p:
                model_dir = os.path.dirname(p)
                break
        if model_dir is None:
            continue
        try:
            start_ticks = os.stat(f'/proc/{pid}').st_mtime  # not exact; use times below
            with open(f'/proc/{pid}/stat') as f:
                stat = f.read().split()
            # field 22 = starttime (ticks since boot); compute age vs boot time
            uptime = float(open('/proc/uptime').read().split()[0])
            hertz = os.sysconf('SC_CLK_TCK')
            start_time_ticks = int(stat[21])
            age = uptime - start_time_ticks / hertz
        except (OSError, IndexError, ValueError):
            continue
        if age > threshold:
            out.append((int(pid), m.group(1), model_dir))
    return out


def recompile_o1(model_dir: str, stem: str, log) -> bool:
    src = f'{model_dir}/{stem}.cpp'
    obj = f'{model_dir}/{stem}.o'
    cmd = [
        'clang++', '-O1', '-march=znver4', '-DCPU_XIANGSHAN',
        '-DGSIM_MT_DENSE_OWNER_READY_FLAGS_COMPILE=1',
        f'-I{model_dir}',
        '-I/home/zhangyangjie/test/XiangShan/difftest/src/test/csrc/gsim',
        '-I/home/zhangyangjie/test/XiangShan/difftest/difftest-src',
        '-I/home/zhangyangjie/test/XiangShan/difftest/generated-src',
        '-std=c++17', '-fPIC', '-c', src, '-o', obj,
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        log.write(f'[watchdog] O1 recompile FAILED {stem}: {r.stderr[-400:]}\n')
        return False
    log.write(f'[watchdog] rescued {stem} at -O1 ({os.path.getsize(obj)} bytes)\n')
    return True


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--build-dir', required=True)
    ap.add_argument('--threshold', type=int, default=1200, help='seconds before a TU is a straggler')
    ap.add_argument('--interval', type=int, default=60)
    ap.add_argument('--max-rescues', type=int, default=40)
    args = ap.parse_args()

    build_dir = Path(args.build_dir).resolve()
    emu = build_dir / 'gsim-compile' / 'emu'
    model_dir = build_dir / 'gsim-compile' / 'model'
    rescued: set[str] = set()

    print(f'[watchdog] watching {build_dir} (threshold {args.threshold}s)', flush=True)
    while True:
        if emu.exists():
            print('[watchdog] emu linked; done', flush=True)
            break
        if len(rescued) > args.max_rescues:
            print('[watchdog] too many rescues; aborting', flush=True)
            return 2
        procs = find_stragglers(args.threshold)
        if not procs:
            # no stragglers: check whether anything is still running
            any_clang = any(
                'clang' in open(f'/proc/{p}/cmdline', 'rb').read().decode('utf-8', 'replace')
                for p in filter(str.isdigit, os.listdir('/proc'))
                if os.path.exists(f'/proc/{p}/cmdline')
            )
            if not any_clang and not emu.exists():
                print('[watchdog] no clang left and no emu — build ended; check log', flush=True)
                break
            time.sleep(args.interval)
            continue
        for pid, stem, mdir in procs:
            if Path(mdir) != model_dir or stem in rescued:
                continue
            print(f'[watchdog] killing {stem} (pid {pid}); O1 recompile', flush=True)
            try:
                os.kill(pid, 9)
            except OSError:
                pass
            time.sleep(2)
            if recompile_o1(mdir, stem, sys.stdout):
                rescued.add(stem)
        time.sleep(args.interval)
    if rescued:
        print(f'[watchdog] rescued {len(rescued)} TUs at -O1: {sorted(rescued)}', flush=True)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
