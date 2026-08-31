# GSim Campaign — One Optimization Round

You are one round of a long-running performance campaign on the gsim-mt RTL
simulator. You have NO memory of previous rounds: the evidence ledger is the
only memory. Read it before acting.

## Where things are (verify with ls; paths relative to this repo)

- Campaign contract + workflow: `CLAUDE.md`, `docs/agent-flow.md`, `docs/spec-evidence-records.md`
- Evidence ledger (append-only memory): `../gsim-task-saturate-sparse/candidates.jsonl`
  — read the LAST 5 entries (tail) before choosing what to do. Latest entries
  are also your progress log.
- Champions + registries: `../gsim-task-verilator-dual-default4488/champions/`
- gsim generator worktree (code + docs): `/tmp/gsim-wip-b1-lookahead` (branch
  `deliver/gsim-mt-dense-v1`; NEVER push anywhere but `yjmstr` remote)
- Frozen FIR inputs (read-only): `../rtl-kunminghu-v3-frozen/SimTop.fir` (active
  RTL), `../rtl-v86-frozen/SimTop.fir`
- Domain knowledge: `skills/mtwiki/wiki/` (esp. wiki-generator-speed.md 追记 1-9)
- Ledger append tool (USE THIS, never `cat >>`): `python3 scripts/ledger-append.py <ledger> '<json>'`
- Evidence check (must pass before your round ends):
  `python3 scripts/check-evidence.py --workspace ../gsim-task-saturate-sparse --vocab-since 2026-08-20`

## The target

gsim-mt T16 (kunminghu-v3, linux.bin 30k cycles, no-diff) at ≥ 2.5× SAME-SESSION
same-thread Verilator T16. Current best: 7.19s (champion newrtl-t16-compact-v2,
MAXMT=1700) vs V-T16 15.35s = 2.13×. 2.5× needs gsim ≤ V/2.5 measured in the
SAME interleaved session (never reuse a denominator from an earlier session).

## One round = exactly ONE hypothesis

1. Read the ledger tail. Pick ONE lever (unexplored or promising). Suggested
   menu (not exhaustive — the ledger knows what is already tried):
   - knob sweeps: GSIM_MT_DENSE_LOOKAHEAD (128 now), VCONTRACT_CAP, sched order,
     worker-major-text variants, OWNER_BANK_COUNTERS, per-tier MAXMT via
     GSIM_MT_DENSE_VCONTRACT_MAXMT_AUTO probe (commit 114fec0)
   - schedule search: seed2 two-pass POLICY=auto, compact variants
   - T32-width tier work (its champion is MAXMT=2400 fresh, never swept)
   - v86-T16 re-registration at MAXMT=1200 (measured -11.4%, needs gate+seed)
   - codegen: emission knobs documented in README "Toolchain pipeline cost"
2. STATE OF PLAY (2026-09-01, read the ledger tail to confirm): the T16 knob
   surface is CLOSED at high statistical power (three sessions; best compound
   MAXMT=2000 x LOOKAHEAD=512 = 7.08s, -2.58% vs champion, 8/8 pairs disjoint
   but below the 3% registration bar). 2.5x (needs <=6.26s same-session) is
   NOT reachable via knobs: wall time is work-bound. Remaining levers are
   CODE-LEVEL, each must be default-off and FIR-gate-verified byte-identical
   when off:
   - executor sync protocol: owner-ready token batching/coalescing per level,
     banked counters beyond GSIM_MT_DENSE_OWNER_BANK_COUNTERS, level barrier
     elision when a level is single-worker
   - emission layout: per-worker major-text specialization, activation-check
     hoisting, subStep splitting by measured icache pressure (see
     wiki-compile-optimization / A104 R1-S1 notes in mtwiki)
   - duty-cycle: per-worker idle instrumentation to find which levels strand
     workers (lvlSum says 1600 optimal but measured 2000 - the gap IS the
     stranding; a schedule/emission change that closes it is worth ~3-5%)
   - T32-width findings that transfer down (its tier was never swept)
3. State the hypothesis in one sentence, run the experiment SMALL (a probe or
   one generation+build+interleaved-bench), record numbers. Code-level probes:
   measure BEFORE building (read the emitted cpp, count tokens/branches) -
   a day of building is not needed to kill a bad idea.
3. If it wins ≥3% on a clean interleaved A/B (warmup discarded, ≥3 rounds,
   fixed mask 0-15, machine serialized): run the correctness gate (coremark
   full difftest must HIT GOOD TRAP pc=0x80001ca0, 663758 instr, zero mismatch)
   and only then register/update a champion directory + README row.
5. Append ONE ledger entry (validated status vocabulary: analysis/baseline/
   closed/correction/diagnostic/instrumentation/measured/promote/reject/retain/
   retracted/validated) and run the evidence check. Non-zero exit = your round
   failed; fix the ledger before ending.
6. End your turn with a 3-line summary: what was tried, the number, next hint.

## Hard rules

- NO PGO, NO LTO in build flags. No pushing to `origin` (openXiangShan).
- Don't modify frozen FIRs or difftest-extmodule.cpp in build/generated-src
  without re-reading `champions/newrtl-v1-baseline/REBUILD.md` (topdown adapter).
- Runtime GSIM_THREADS must equal generation width (14-16× cliff otherwise).
- Every perf claim: instrCnt must be 86,469 (linux-30k) — if not, something is
  wrong; investigate, don't record.
- Time-box one round to ~1 hour of machine work. Small experiments only.
- If the 2.5× target is MET and gated: write `.humanize/flows/gsim_optimize/TARGET_ACHIEVED`
  with the numbers inside, update README + champion, then end.
- If you believe the loop should stop for another reason: write `.humanize/flows/gsim_optimize/STOP`
  with one sentence why, then end.
