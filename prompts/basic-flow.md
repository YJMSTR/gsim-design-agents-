# GSim Design Agents Basic Flow Prompt

You are working in a GSim task implementation workspace. Your job is to produce the best correct candidate for the task contract below.

## Task Contract

- Task name: `<fill in>`
- Objective: Transform GSim into a multi-threaded RTL simulator that approaches 32-thread Verilator performance on the declared benchmark set.
- Correctness requirements: Multi-threaded GSim output must match the single-thread GSim reference bit-for-bit on declared regressions.
- Performance or quality target: `<fill in target thread count, designs, and parity/improvement threshold>`
- Allowed implementation approaches: static partitioning, dynamic scheduling, work stealing, per-thread buffers, low-contention queues, cache-line padding, NUMA-aware allocation, SIMD-friendly generated code, and compiler tuning.
- Constraints: `<fill in C++ standard, dependency policy, supported platforms, and branch/worktree rules>`
- Validation command: `<fill in command that proves correctness>`
- Evaluation command: `<fill in command that measures runtime across 1/2/4/8/16/32 threads>`
- Promotion criteria: validation passes, benchmark improves over parent, profiling evidence explains the change, and evidence files are updated.

## Workflow

1. Read the workspace structure, existing implementation, tests, benchmark scripts, and `docs/task-contract.md`.
2. If continuing from the prior worktree, read `docs/gsim-worktree-handoff.md` and write a handoff summary into `docs/draft.md` before editing.
3. Query `skills/mtwiki` only for references needed by this candidate.
4. Identify the baseline behavior, single-thread reference path, and validation command.
5. Write an implementation-plan draft to `docs/draft.md`.
6. Convert the draft into an executable `docs/plan.md` before editing code.
7. Implement one candidate at a time.
8. Run validation after each meaningful candidate.
9. Run evaluation and profiling for any candidate that passes validation.
10. Use `skills/perf-report-skill` to diagnose the dominant bottleneck.
11. Record candidate results, parent relationships, profiler evidence, and the promotion/rejection decision.

## Plan Draft Requirements

The draft in `docs/draft.md` must include:

- Current baseline and how it is validated.
- Main risks and unknowns.
- Candidate implementation directions ranked by expected value and risk.
- The first concrete implementation steps.
- Exact validation and evaluation commands.
- Evidence required to promote, revise, or reject a candidate.

Do not start implementation until the draft exists.
