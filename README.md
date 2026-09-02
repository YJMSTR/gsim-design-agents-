# GSim Design Agents

GSim Design Agents is an agent-centric workflow repository for turning `gsim`, a high-performance sparse-evaluation RTL simulator, into a multi-threaded simulator that can compete with 32-thread Verilator runs.

This repository mirrors the Kernel Design Agents structure, but changes the optimization target:

| KDA concept | This repository |
|---|---|
| CUDA kernel optimization | C++ RTL simulator multi-threading and profiling |
| KernelWiki skill | `skills/mtwiki` domain wiki for multi-threaded RTL simulation |
| `ncu-report-skill` | `skills/perf-report-skill` for `perf`/VTune/threading evidence |
| Kernel benchmark workspace | A separate `gsim` implementation workspace |

## Contents

| Path | Purpose |
|---|---|
| `docs/spec-measurement-protocol.md` | Normative measurement contracts (sessions, instruments, probe hygiene). |
| `docs/spec-evidence-records.md` | Normative evidence schemas, outcome vocabulary, artifact identity; enforced by `scripts/check-evidence.py`. |
| `docs/rationales/` | WHY behind the specs: the incident behind each rule. |
| `docs/agent-flow.md` | Minimal end-to-end workflow for the GSim optimization loop. |
| `scripts/` | Workspace bootstrapping (`init-task-workspace.py`), evidence contracts (`check-evidence.py`), build straggler rescue (`build-watchdog.py` — auto O1-fallback for optimizer-explosive instrumented TUs), champion reproduction classification (`gsim-champion-drift.py` — text-exact vs schedule-exact vs drift, with an explicit whitelist for accepted generator-evolution deltas), and knob liveness lint (`gsim-knob-lint.py` — fails when a run script references a GSIM_* variable the generator source never reads), and doc-knob consistency (`gsim-doc-knob-check.py` — fails when a documented knob exists nowhere in generator/model/build text; reverse direction is info-only for internal debug knobs). |

## Quick start

```bash
cd gsim-design-agents
python3 scripts/init-task-workspace.py --workspace /path/to/isolated/gsim-task
```

Then start an agent session in the task workspace and give it `prompts/basic-flow.md`, filled with the local validation and benchmark commands.

## Non-interference rule

Do not run commands in the sibling `../gsim` checkout unless the active task explicitly owns that workspace. Existing optimization runs, including the current `omp` process, are treated as external work.

## Handoff from the existing GSim worktree

The current optimization worktree is `../.worktrees/gsim-mt/gsim` (relative to this repo). New agents should not mutate it during workflow setup. Use `docs/gsim-worktree-handoff.md` as the orientation checklist before starting a candidate.

Recommended safe path:

1. Read `docs/gsim-worktree-handoff.md`.
2. Create a separate task workspace with `scripts/init-task-workspace.py`.
3. Copy or worktree-clone GSim only after the task contract names that workspace.
4. Run only read-only inspection commands against the existing worktree unless explicitly taking ownership.


## Session Results (2026-09-02, 42h campaign)

### T16 linux-30k champions (both frozen RTLs, seed-contract verified)

| Champion | Stack | Wall | Session gain |
|---|---|---|---|
| `newrtl-t16-compact-v4` (kunminghu-v3) | MAXMT2000 + LA1024 + CCD250 + SBO + sorted-waits | **6.91-6.94s** | 7.19 -> 6.91 (-3.9%) |
| `xiangshan-t16-compact-v4` (v86) | MAXMT1200 + LA128 + CCD350 + SBO + sorted-waits | **3.105s** | 3.378 -> 3.105 (-8.1% today) |

Ratio vs same-session rebuilt V-T16 (harness identity verified via instrCnt=86,469): **2.19-2.21x** (V drifts 15.3-16.4s across sessions; 2.30x at yesterday's 15.91s denominator).

### Methodology delivered (cross-design validated)
1. **Structure-layer params (MAXMT) inherit optima** - confirmed on both RTLs
2. **Emission-layer knobs (CCD/SBO/sorted-waits) transfer across designs**; schedule-layer (LA) and per-knob optima (gamma: 250 vs 350) are design-specific - transfer then re-sweep
3. **WP2' closure**: the 61.7G instruction excess vs Verilator is the intrinsic price of event detection (three measured slices: dead-strip DCE'd, OR-batching +1.16%, SIMD ceiling 1-3%)

Ledger: 179 entries (all green). Wiki addenda 1-22. Full attribution of the remaining gap to 2.5x.
