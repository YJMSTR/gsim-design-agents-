# Agent Flow for GSim Multi-threading

This flow adapts Kernel Design Agents to a C++ RTL simulator optimization task. The reusable workflow stays here. GSim source edits, benchmarks, and profiler artifacts live in a separate task workspace.

## Principle

Profile -> Diagnose -> Plan -> Implement -> Validate -> Measure -> Record -> Promote or Reject.

Do not guess. A parallel RTL simulator can lose performance through load imbalance, barrier overhead, lock contention, false sharing, NUMA effects, or poor event granularity. Each candidate must be tied to measured evidence.

## Minimal loop

1. Define the task contract.
2. Let the agent inspect the implementation workspace and relevant `skills/mtwiki` pages.
3. Make the agent write `docs/draft.md` in the task workspace.
4. Convert the draft into `docs/plan.md`.
5. Implement one candidate.
6. Validate correctness against single-thread GSim and reference traces.
7. Measure the target metric across declared designs and thread counts.
8. Store evidence in `benchmark.csv`, `candidates.jsonl`, and `profile/<run_name>/`.
9. Promote, revise, or reject the candidate.
10. Repeat from the promoted baseline.

## Task contract fields

Each task must state:

- Objective.
- Inputs and outputs.
- Correctness requirements.
- Implementation constraints.
- Validation command.
- Evaluation command.
- Promotion criteria.
- Rollback/rejection criteria.

## Evidence records

Use these files in the task workspace:

- `docs/task-contract.md` for the filled contract.
- `docs/draft.md` for the first plan draft.
- `docs/plan.md` for the executable plan.
- `benchmark.csv` for measurable results.
- `candidates.jsonl` for candidate names, parent links, and decisions.
- `profile/<run_name>/reports/` for raw profiler output.
- `profile/<run_name>/analysis/` for extracted metrics.
- `profile/<run_name>/REPORT.md` for the final diagnosis and recommendation.

## Non-interference policy

Existing agent attempts under `/home/zhangyangjie/test`, especially the current `omp` run, are external state. This repository does not kill processes, reuse active run directories, or mutate an implementation workspace without an explicit task contract naming it.

## Existing-worktree handoff

Before continuing from prior GSim optimization attempts, read `docs/gsim-worktree-handoff.md`. The handoff is part of the draft phase: the agent must understand the current worktree layout, MT flags, regression scripts, and known candidate state before editing.
