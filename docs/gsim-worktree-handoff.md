# Existing GSim Worktree Handoff

This note is the bridge from earlier ad-hoc agent optimization attempts to the new GSim Design Agents workflow.

## Existing workspace

- Existing worktree: `../.worktrees/gsim-mt/gsim` (relative to this repository; `<workspace>/.worktrees/gsim-mt/gsim` where `<workspace>` is the directory containing this repository)
- Treat it as active user/agent state. Do not kill processes, clean builds, delete outputs, or run long builds there during workflow setup.
- The user reported an active `omp` process in that workspace; avoid actions that compete for or invalidate that run.

## Repository shape observed

```text
gsim/
  Makefile
  README.md
  include/           # core headers
  src/               # compiler, graph, partitioning, C++ emitter, mt experiments
  scripts/           # regression, perf, diff, and mt-repcut check scripts
  test/              # minimized FIR regression inputs
  ready-to-run/      # larger prebuilt benchmark/design inputs
  emu/               # simulator harness sources
  mk/toolchain.mk    # compiler/toolchain settings
```

## Important Makefile paths

- `make build-gsim`: builds `build/gsim/gsim`.
- `make run dutName=<name>`: GSIM compile + emu build + run, logging to `build/<dut>/<dut>.log`.
- `make diff dutName=<name>`: Verilator/GSIM differential path using `MODE=2` internals.
- `make fir-tests`: auto-discovers `test/*.fir` and compiles them through GSIM.
- `make run-fir-test FIR_TEST=<case>`: runs one minimized FIR test.
- `scripts/regression.sh`: full functional then performance regression across `ysyx3`, `rocket`, `small-boom`, `large-boom`, `minimal-xiangshan`, and `default-xiangshan`.

## Current multi-threading surface

Observed command-line options in `src/main.cpp`:

- `--dump-mt-schedule-json`
- `--mt-helper-mode=off|seq|buffered-seq|mt|mt-level-dispatch`
- `--mt-repcut-lite=off|on`
- `--mt-repcut-copy-budget=N`
- `--mt-repcut-fanout-budget=N`
- `--mt-batch-formation=legacy|active-frequency|coarse`
- `--mt-coarse-runtime=layered|mtask`
- `--mt-coarse-profitability=off|static`
- `--mt-coarse-worker-policy=static|profitable`
- `--mt-active-frequency-cost-threshold=N`
- `--dump-mt-repcut-lite-report`
- `--dump-mt-coarse-region-report`
- `--disable-replication-opt`

`src/cppEmitter.cpp` contains the densest observed MT/repcut/coarse-region implementation state. Start there for architecture reading, but use LSP/search before editing exported symbols.

## Existing focused regression scripts

`src/cppEmitter.cpp` and `scripts/check-mt-repcut-lite-*.py` indicate prior work around RepCut-lite, coarse batch formation, and mt-level dispatch. The handoff agent should run or inspect these scripts before proposing a replacement architecture.

Observed script names:

- `scripts/check-mt-repcut-lite-bits-noshift-model.py`
- `scripts/check-mt-repcut-lite-bits-noshift-source.py`
- `scripts/check-mt-repcut-lite-chained-clone.py`
- `scripts/check-mt-repcut-lite-eq-mixed-width.py`
- `scripts/check-mt-repcut-lite-eq-neq.py`
- `scripts/check-mt-repcut-lite-eq-wide-literal.py`
- `scripts/check-mt-repcut-lite-local-dep.py`
- `scripts/check-mt-repcut-lite-multiconsumer-outside.py`
- `scripts/check-mt-repcut-lite-parallel-clone.py`
- `scripts/check-mt-repcut-lite-same-batch-dependency.py`
- `scripts/check-mt-repcut-lite-same-source-dep.py`

## First-session orientation checklist for a new implementation agent

1. Read this file, `docs/task-contract.md`, `docs/agent-flow.md`, and `skills/perf-report-skill/SKILL.md`.
2. Read GSim `README.md`, `Makefile`, `test/README.md`, and the `src/main.cpp` option block.
3. Identify the active branch/worktree state without running cleanup commands.
4. Map the MT implementation around `src/cppEmitter.cpp`, `include/config.h`, `src/main.cpp`, and any generated runtime helpers.
5. Run a cheap correctness smoke test in an isolated copy or named task workspace, not in the active worktree, unless the user explicitly transfers ownership.
6. Create `docs/draft.md` in the task workspace summarizing baseline, current candidate state, known flags, validation commands, benchmark commands, and risks.
7. Only then implement the next candidate.

## Handoff draft template

```markdown
# GSim MT Handoff Draft

## Baseline state
- Worktree:
- Branch/commit:
- Active candidate flags:
- Known passing tests:
- Known failing tests:

## Architecture map
- Frontend/parser:
- Graph passes:
- MT schedule construction:
- C++ emission/runtime:
- Benchmark harness:

## Command map
- Build:
- Single FIR smoke:
- Functional regression:
- Performance run:
- Verilator comparison:

## Current bottleneck evidence
- Latest benchmark row:
- Latest profile report:
- Dominant diagnosis pattern:

## Next candidate
- Candidate name:
- Parent:
- Expected effect:
- Validation command:
- Evaluation command:
- Promotion/rejection threshold:
```
