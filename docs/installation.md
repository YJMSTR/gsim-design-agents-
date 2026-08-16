# Installation

## Clone this repository

```bash
git clone --recurse-submodules <repo-url> gsim-design-agents
cd gsim-design-agents
```

## Link project skills into Claude Code

```bash
mkdir -p .claude/skills
ln -s ../../skills/perf-report-skill .claude/skills/perf-report-skill
ln -s ../../skills/mtwiki .claude/skills/mtwiki
```

For user-level installation:

```bash
mkdir -p ~/.claude/skills
ln -s "$(pwd)/skills/perf-report-skill" ~/.claude/skills/perf-report-skill
ln -s "$(pwd)/skills/mtwiki" ~/.claude/skills/mtwiki
```

## Initialize a task workspace

```bash
python3 scripts/init-task-workspace.py --workspace ../gsim-mt-task-001
```
Relative workspace paths are resolved by the script. Do not use `../.worktrees/gsim-mt/gsim` (the existing GSim worktree) as a scratch workspace while existing runs are active.
