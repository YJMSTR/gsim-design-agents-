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
ln -s /home/zhangyangjie/test/gsim-design-agents/skills/perf-report-skill ~/.claude/skills/perf-report-skill
ln -s /home/zhangyangjie/test/gsim-design-agents/skills/mtwiki ~/.claude/skills/mtwiki
```

## Initialize a task workspace

```bash
python3 scripts/init-task-workspace.py --workspace /home/zhangyangjie/test/gsim-mt-task-001
```

Do not use `/home/zhangyangjie/test/.worktrees/gsim-mt/gsim` as a scratch workspace while existing runs are active.
