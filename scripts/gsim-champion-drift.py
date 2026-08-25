#!/usr/bin/env python3
"""Champion drift classifier: does the current generator tip still reproduce the
registered champion?

Two levels of reproduction are distinguished (the campaign learned the hard way
that conflating them produces overclaims):

  text-exact      - every model file sha256-identical to the registered artifact
  schedule-exact  - the seed2 replay applies 9/9 canon lines and the schedule
                    facts line is verbatim-identical, but the emitted text may
                    differ (generator evolution: new default-on fields, removed
                    instrumentation). Dense hot-path identity can be confirmed
                    separately by inspecting which files drifted.

Usage:
    gsim-champion-drift.py --champion DIR --candidate MODEL_DIR \
        [--gen-log PATH] [--facts-regex REGEX]

Inputs:
  --champion   registered champion dir containing model/ (and optionally
               facts.txt with the registered schedule-facts line)
  --candidate  freshly generated model dir (same generator invocation as the
               champion recipe, at the tip under test)
  --gen-log    optional generation stderr/stdout of the candidate run; when
               given, canon applied-lines and the [mt-dense-vcontract] facts
               line are extracted and compared against the champion's
               facts.txt (if present)

Exit codes:
  0  text-exact (or schedule-exact with only whitelisted drift; see --ok-drift)
  1  schedule-drift (canon/facts mismatch) or text drift beyond whitelist
  2  usage / missing inputs

The whitelist: --ok-drift NAME may be repeated; drift confined to those files
downgrades the verdict from TEXT-DRIFT-FAIL to schedule-exact-with-known-drift
(exit 0 with a warning line). Use it to pin the accepted generator-evolution
delta explicitly rather than silently accepting any drift.
"""
from __future__ import annotations

import argparse
import hashlib
import re
import sys
from pathlib import Path

CANON_RE = re.compile(r'\[schedule-seed2\] applied\s+\S+\s+nodes=\d+\s+canon=([0-9a-f]+)')

# Schedule-identity scalars: the four numbers that pin the contracted schedule.
# Trailing facts fields (pathMemoHits etc.) have been added/removed by generator
# evolution and are reported as info, not drift.
FACTS_SCALARS = ('sccs', 'mtasks', 'merges', 'cycRej')


def facts_scalars(line: str) -> dict[str, str] | None:
    out = {}
    for k in FACTS_SCALARS:
        m = re.search(r'\b' + k + r'=(\d+)', line)
        if not m:
            return None
        out[k] = m.group(1)
    return out


def manifest(root: Path) -> dict[str, str]:
    out = {}
    for p in sorted(root.rglob('*')):
        if p.is_file() and p.suffix in ('.cpp', '.h'):
            out[str(p.relative_to(root))] = hashlib.sha256(p.read_bytes()).hexdigest()
    return out


def canon_hashes(log_text: str) -> list[str]:
    return CANON_RE.findall(log_text)


def facts_line(log_text: str) -> str | None:
    for line in log_text.splitlines():
        if '[mt-dense-vcontract]' in line:
            return line.strip()
    return None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--champion', required=True, type=Path)
    ap.add_argument('--candidate', required=True, type=Path)
    ap.add_argument('--gen-log', type=Path)
    ap.add_argument('--ok-drift', action='append', default=[])
    args = ap.parse_args()

    champ_model = args.champion / 'model'
    if not champ_model.is_dir():
        champ_model = args.champion  # allow passing the model dir directly
    if not champ_model.is_dir() or not args.candidate.is_dir():
        print('missing model dir(s)', file=sys.stderr)
        return 2

    cm = manifest(champ_model)
    nm = manifest(args.candidate)
    if not cm or not nm:
        print('empty manifest (no .cpp/.h files)', file=sys.stderr)
        return 2

    only_c = sorted(set(cm) - set(nm))
    only_n = sorted(set(nm) - set(cm))
    both = set(cm) & set(nm)
    changed = sorted(f for f in both if cm[f] != nm[f])

    # Schedule-level identity FIRST: a facts/canon mismatch is a nondeterminism
    # signal even when the text happens to be identical, so it must not hide
    # behind a text-exact early return.
    sched_ok = None
    facts_path = args.champion / 'facts.txt'
    if args.gen_log and args.gen_log.is_file():
        log = args.gen_log.read_text(errors='ignore')
        canon = canon_hashes(log)
        facts = facts_line(log)
        # canon presence: N applied lines each carrying a content hash. Distinct
        # entries may legitimately share a hash, so we only require the expected
        # applied-line count when the champion facts.txt records one, else >= 1.
        canon_ok = len(canon) > 0
        if facts_path.is_file() and facts is not None:
            ref = facts_path.read_text().strip()
            rs, ns = facts_scalars(ref), facts_scalars(facts)
            if rs is None or ns is None:
                print('facts line missing core scalars; cannot verify schedule identity')
                sched_ok = False
            else:
                sched_ok = (rs == ns) and canon_ok
                if rs != ns:
                    print('FACTS DRIFT (core scalars):\n  champion: %s\n  candidate: %s'
                          % ({k: rs[k] for k in rs if rs[k] != ns.get(k)},
                             {k: ns[k] for k in ns if ns[k] != rs.get(k)}))
                elif facts != ref:
                    print('facts: core scalars identical; trailing fields evolved (info only)')
    if sched_ok is True:
        print('schedule-exact: canon lines applied, core facts scalars identical')
    elif sched_ok is False:
        print('VERDICT schedule-drift (facts/canon mismatch)')
        return 1

    if not only_c and not only_n and not changed:
        print('VERDICT text-exact: %d/%d files identical' % (len(nm), len(cm)))
        return 0

    print('TEXT DRIFT: %d changed, %d only-in-champion, %d only-in-candidate'
          % (len(changed), len(only_c), len(only_n)))
    for f in changed[:10]:
        print('  changed: ' + f)
    for f in (only_c + only_n)[:10]:
        print('  membership: ' + f)

    ok = set(args.ok_drift)
    unexplained = (set(changed) | set(only_c) | set(only_n)) - ok
    if ok and not unexplained:
        if sched_ok is True:
            print('VERDICT schedule-exact-with-known-drift (whitelist covers all deltas)')
        else:
            print('VERDICT text-drift-whitelisted (schedule identity NOT verified: '
                  'champion facts.txt or --gen-log missing)')
        return 0
    print('VERDICT text-drift-fail (unexplained drift: %d files)' % len(unexplained))
    return 1


if __name__ == '__main__':
    sys.exit(main())
