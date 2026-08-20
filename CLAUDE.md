# Agent Instructions

This repository is the reusable workflow reference for the GSim multi-threading effort. Keep implementation experiments in separate task workspaces.

## Repository rules

- Use English for repository-facing files, comments, documentation, prompts, and commit messages.
- Keep generated benchmark logs, profiler outputs, candidate binaries, and modified GSim source out of this repository.
- Put generated outputs in `runs/`, `outputs/`, or `profile/`; these paths are ignored by git.
- Treat `skills/mtwiki` as read-mostly domain knowledge. Update it only when adding reusable RTL simulation knowledge.
- Treat `skills/perf-report-skill` as the profiling-method skill. Update it when the profiling workflow or diagnosis rules change.
- Never touch the sibling GSim checkout (`../gsim` relative to this repository) from this repository's maintenance tasks. Use a separate implementation workspace.

## Expected agent workflow

1. Create or enter a separate GSim implementation workspace.
2. Define the task objective, constraints, validation command, evaluation command, and promotion criteria.
3. Use `prompts/basic-flow.md` as the starter prompt.
4. Read local task code and documentation before proposing code changes.
5. Write the initial plan draft to `docs/draft.md` inside the task workspace.
6. Convert the draft into an executable plan.
7. Implement one candidate at a time.
8. Validate correctness after each meaningful candidate.
9. Measure with `perf`, VTune, or project benchmarks.
10. Update the task contract and evidence ledgers per `docs/spec-evidence-records.md`;
    run `python3 scripts/check-evidence.py --workspace <task-workspace>` after every
    ledger update (non-zero exit blocks the step that produced the violation).
