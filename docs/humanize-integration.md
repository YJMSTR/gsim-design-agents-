# humanize2 Integration (2026-09-01)

The campaign loop now runs under [humanize2](https://github.com/humanfia/humanize2),
driven by this machine's omp binary acting as the `pi` backend.

## Pieces

- `.humanize/flows/gsim_optimize/` — the flow (modeled on `builtin/ralph_loop`):
  one round per turn, fresh `pi` session each round, the evidence ledger is the
  only inter-round memory. Stops on: round budget (default 42), `STOP` file, or
  `TARGET_ACHIEVED` file (both beside the flow; written by a round agent).
- `.humanize/flows/gsim_optimize/round-brief.md` — the self-contained per-round task: target,
  paths, one-hypothesis protocol, hard rules, stop-file semantics.
- `.humanize/flows/gsim_optimize/budget.yaml` — flow config (rounds/target/ledger path).
- `scripts/gsim-humanize.sh [ROUNDS]|stop` — harness-side entry point.

## Backend wiring

`~/.local/bin/pi` is a shim over `~/.local/bin/omp`: omp speaks the pi RPC
protocol (`omp --mode rpc`, protocolVersion 1/2) but lacks `--session-id` and
`--exclude-tools`; the shim drops them (the hmz backend holds one rpc process
per session; a fresh process is a fresh session, which per-round freshness
wants anyway). Agent spec: `-a pi/glm-5.3:high` (zhipu-coding-plan via omp's
fuzzy model match).

## Run it

```sh
scripts/gsim-humanize.sh          # 42-round budget from budget.yaml
scripts/gsim-humanize.sh 5        # 5 rounds
scripts/gsim-humanize.sh stop     # halt before next round
tail -f runs/humanize/loop.log (loop output is generated, stays untracked)    # watch
```

## Notes

- A trivial chat round costs ~4 min of agent startup; a working round is
  expected to take 30-90 min (read ledger → experiment → gate → ledger append).
- The flow never edits the campaign itself; the round agent does, under
  CLAUDE.md rules and `check-evidence.py` (non-zero exit fails the round).
- State (`rounds`) resumes across interrupted runs; budget exhaustion clears it.
