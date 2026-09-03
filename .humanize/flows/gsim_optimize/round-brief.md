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
  `dev/mt-dense-experiments`; push ONLY there, never to deliver)
- BRANCH HYGIENE (user directive 2026-09-03): `deliver/gsim-mt-dense-v1` is
  FROZEN at 114fec0 (the deliverable tip). ALL experiment commits go to
  `dev/mt-dense-experiments`. TIE/REJECT experiments: record evidence in the
  ledger but DO NOT keep the knob code as new commits unless the user asks -
  rejected code is complexity, the ledger is the preservation mechanism. A
  candidate's code earns deliver only via user-directed merge.
- Frozen FIR inputs (read-only): `../rtl-kunminghu-v3-frozen/SimTop.fir` (active
  RTL), `../rtl-v86-frozen/SimTop.fir`
- Domain knowledge: `skills/mtwiki/wiki/` (esp. wiki-generator-speed.md 追记 1-9)
- Ledger append tool (USE THIS, never `cat >>`): `python3 scripts/ledger-append.py <ledger> '<json>'`
- Evidence check (must pass before your round ends):
  `python3 scripts/check-evidence.py --workspace ../gsim-task-saturate-sparse --vocab-since 2026-08-20`

## The target

gsim-mt T16 (kunminghu-v3, linux.bin 30k cycles, no-diff) at ≥ 2.5× SAME-SESSION
same-thread Verilator T16. Current best: 6.91-6.94s (champion newrtl-t16-compact-v4,
MAXMT=2000 + LA1024 + CCD250 + SBO + sorted-waits, seed 2348c8900e5d3ce8) vs
rebuilt same-harness V-T16 15.31s (instrCnt=86,469 identity VERIFIED - NEVER compare
against build-vrtl July emu: old harness, instrCnt 65,889) = 2.19-2.21×. 2.5× needs
gsim ≤ V/2.5 measured in the SAME interleaved session.

## Attribution chain (2026-09-02, all measured — read the ledger tail)

1. Event detection nets ZERO at T16 (static-dense probe, entry
   static-dense-probe-tie-attribution-reversal): full evaluation ties the champion.
   WP2' shadow-memcmp surgery is DEAD. Activation/detection direction CLOSED.
2. Time-based profile (perf stat): IPC 1.31, "67% cache miss" = L2→L3, not DRAM.
3. Fill-source breakdown: DRAM only 2.1% of fills (NOT the wall); same-CCD L3 46%,
   cross-CCD L3 12% (priciest); single-CCD SMT = 3.1× worse (16 cores' MLP is
   load-bearing). Stall model = L3-latency × limited MLP.
4. Scan-class levers all measured: sorted-waits -1.53% (kept), batch ×3 tie,
   token-slot prefetch -0.57% marginal (kept off, entry scan-prefetch-marginal).
   The token array's churn is a minor fraction of L3 fills.

## One round = exactly ONE hypothesis

1. Read the ledger tail. Pick ONE lever (unexplored or promising). The
   attribution says: wall = L3-latency x limited MLP. Candidate menu, ranked by
   that evidence:
   - BODY-REGION PREFETCH: the dispatch loop knows the next mtask; its SBO
     owner state region is contiguous -> emit __builtin_prefetch for the next
     task's region in the dispatch prologue. Targets the 46% same-CCD L3 fill
     pool (bigger than the token churn measured at -0.57%). Default-off knob,
     FIR-gated, gate + 3-pair vs newrtl-t16-compact-v4.
   - Cross-CCD L3 elimination deeper than gamma250 (WP1-class partitioner
     work): the 12% cross-CCD L3 hits are the priciest regular traffic.
   - L3->L2 promotion: per-core hot set ~2.7MB vs 1MB L2 (43MB/16); any
     layout change that shrinks the per-worker hot footprint.
   - v86/T32/T8 tiers: emission-stack transfer rules in wiki zhuiji 21-22
     apply (transfer emission knobs, re-sweep gamma/MAXMT/LA per design).
   - T1-tier open question: event-vs-static at T1 serial UNMEASURED (T16 tie
     does not transfer; needs a T1-width generation, watch width-match rule).
2. STATE OF PLAY (2026-09-02, read the ledger tail to confirm): champions are
   newrtl-t16-compact-v4 (kunminghu: MAXMT2000+LA1024+CCD250+SBO+sorted-waits =
   6.91-6.94s, 5/5 validated, seed sealed) and xiangshan-t16-compact-v4 (v86:
   MAXMT1200+LA128+CCD350+SBO+sorted-waits = 3.105s, -8.1% day, seed sealed).
   ALL generation-level knobs are closed at both RTLs (MAXMT/LA/gamma/supernode
   re-swept at final stacks; wiki zhuiji 20-25 has the re-sweep discipline and
   the transfer map). The current target line is the v4 number above; do NOT
   use the old v2 7.19s baseline. Remaining levers are CODE-LEVEL per the menu
   above, each default-off and FIR-gate-verified byte-identical when off:
   - executor sync protocol: owner-ready token batching/coalescing per level,
     banked counters beyond GSIM_MT_DENSE_OWNER_BANK_COUNTERS, level barrier
     elision when a level is single-worker
   - emission layout: per-worker major-text specialization, activation-check
     hoisting, subStep splitting by measured icache pressure (see
     wiki-compile-optimization / A104 R1-S1 notes in mtwiki)

## Hard rules

- NO PGO, NO LTO in build flags. No pushing to `origin` (openXiangShan).
- Don't modify frozen FIRs or difftest-extmodule.cpp in build/generated-src
  without re-reading `champions/newrtl-v1-baseline/REBUILD.md` (topdown adapter).
- Runtime GSIM_THREADS must equal generation width (14-16× cliff otherwise).
- Every perf claim: instrCnt must be 86,469 (linux-30k) — if not, something is
  wrong; investigate, don't record.
- Measurement hygiene (2026-09-03 protocol): emu speed is an INODE property
  (per-inode page-cache physical pages; copies are new dice, hardlinks keep
  it). (a) any A/B delta must replicate across independent fresh builds, not
  just interleaved re-runs of one build pair; (b) a registered binary must be
  speed-verified IN PLACE (rebuild on the target fs + mv/rename, never a bare
  cp); (c) check load (<2) before timed runs - other tenants share the machine.
- Time-box one round to ~1 hour of machine work. Small experiments only.
- If the 2.5× target is MET and gated: write `.humanize/flows/gsim_optimize/TARGET_ACHIEVED`
  with the numbers inside, update README + champion, then end.
- If you believe the loop should stop for another reason: write `.humanize/flows/gsim_optimize/STOP`
  with one sentence why, then end.
