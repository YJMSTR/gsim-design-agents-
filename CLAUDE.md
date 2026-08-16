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
10. Record candidate relationships, benchmark rows, profiler evidence, and the promotion/rejection decision.

## Promotion rule

A candidate is promotable only if it preserves bit-for-bit simulator correctness and improves the declared target metric under the declared thread count. Measurements follow the protocol in `docs/agent-flow.md`: pinned, same-session, interleaved A/Bs, attribution via duty instrumentation, and wall time reported against the computed floor bound. Rejected candidates must stay recorded with their measured failure reason.
