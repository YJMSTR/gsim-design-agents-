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

The full protocol is normative in `spec-measurement-protocol.md`; the
incidents behind each rule are in `rationales/measurement-protocol.md`.
Summary of the binding rules:

- Timing A/Bs are same-session, alternating-interleaved, and pinned. A
  violated protocol voids the measurement.
- Attribution uses `GSIM_MT_DENSE_DUTY`; `GSIM_MT_PROFILE` numbers are not
  usable for budget arithmetic.
- Report wall time against the computed floor bound, and compute the offline
  ceiling before implementing a scheduler change.
- CPU share is not wall relevance; slack-absorbing mechanisms require
  critical-path verification before their gain is claimed.
- Microbenchmarks are valid only under production constraints (captured
  inputs, production layout, `memcmp` verification).
- Experimental changes sit behind default-off knobs; rejected probes are
  reverted and recorded; revalidate a knob before reusing it after executor
  changes.

## Evidence records

Schemas, file ownership, the outcome vocabulary, and artifact identity are
normative in `spec-evidence-records.md`; `scripts/check-evidence.py` is the
executable check and must pass after every ledger update. Use these files in
the task workspace:

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
