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

## Benchmarks (linux-100k, no-diff, same-session interleaved, CPU mask 0-15)

| Simulator | Stack | Wall (100k) | instrCnt |
|---|---|---|---|
| gsim-mt T16 (`newrtl-t16-compact-v4`) | MAXMT2000 + LA1024 + CCD250 + SBO + sorted-waits | **24.50s** | 460,622 |
| Verilator T16 (same-harness rebuild) | EMU_THREAD=16, -O3 -march=znver4 | 49.80s | 460,622 |

**Speedup: 2.04x** (gsim / Verilator, same interleaved session).
