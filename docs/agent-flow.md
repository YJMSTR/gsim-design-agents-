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

## Measurement protocol

Rules earned from rejected candidates and retracted claims. Follow them exactly; a violated protocol voids the measurement.

- Timing A/Bs are same-session, alternating-interleaved, and pinned with `GSIM_MT_CPU_AFFINITY=auto`. Unpinned dense runs at 8+ workers have a bistable 2-3x slow mode from migration churn. Machine load drifts absolute numbers 50%+ within a day; never compare numbers across sessions.
- Attribution uses `GSIM_MT_DENSE_DUTY` (per-lane padded counters, cycle granularity, ~0.6% distortion). `GSIM_MT_PROFILE` is observer-dominated (~19x distortion at T32) and its numbers are unusable for budget arithmetic; the v470 "4.6% headroom" claim was retracted because it relied on them.
- Report every candidate as wall time vs the computed floor bound, not just wall deltas. The bound comes from a latency-augmented recurrence (PEG dump + `mcr`) with measured token costs (same-CCD ~24.5ns, cross-CCD ~290ns).
- Compute the offline ceiling before implementing a scheduler change. Example: a KL partition on the traffic matrix showed CCD relabeling ceiling ~1.5%, so the 1.5h gen+build probe was skipped. When the data exists, offline analysis beats probes.
- A component's CPU share is not wall relevance. The lookahead tail scan is 40% of CPU but wall-neutral when elided 17% because it runs in stall slack. Always A/B before believing a profile share. The same discipline applies to slack-absorption mechanisms generally: verify critical-path share with a calibrated replay before implementation (speculation measured 82.9% raw hit rate but only +1.2-2.2% wall; tree helpers +0.34%).
- Decision/microbenchmark experiments must not fake the win: drive kernels with inputs captured from real production cycles, keep production state arrays and memory layout (no source-level hoisting of hot fields into registers as a benchmark trick — compiler register allocation is fine), and verify by memcmp against same-cycle production state. A kernel measured outside production constraints proves nothing.
- Probe hygiene: experimental changes sit behind default-off knobs; rejected probes are reverted from the tree; every rejection is recorded in `candidates.jsonl` with its numbers.

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

Existing agent attempts in the surrounding workspace (sibling directories of this repository), especially any active `omp` run, are external state. This repository does not kill processes, reuse active run directories, or mutate an implementation workspace without an explicit task contract naming it.

## Existing-worktree handoff

Before continuing from prior GSim optimization attempts, read `docs/gsim-worktree-handoff.md`. The handoff is part of the draft phase: the agent must understand the current worktree layout, MT flags, regression scripts, and known candidate state before editing.
