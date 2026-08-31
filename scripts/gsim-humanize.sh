#!/usr/bin/env bash
# Drive the gsim campaign through humanize2 (pi backend = omp via ~/.local/bin/pi shim).
#
# Usage:
#   scripts/gsim-humanize.sh [ROUNDS]        # run the gsim_optimize flow
#   scripts/gsim-humanize.sh stop            # halt the loop before the next round
#
# The flow (`.humanize/flows/gsim_optimize/`) reads runs/humanize/round-brief.md
# as the per-round task; each round is a FRESH pi session whose only memory is
# the evidence ledger. ROUNDS overrides the flow's 42-round budget.
set -euo pipefail
cd "$(dirname "$0")/.."

STOP_FILE=.humanize/flows/gsim_optimize/STOP
case "${1:-}" in
  stop) mkdir -p "$(dirname "$STOP_FILE")"; date -R > "$STOP_FILE"
        echo "wrote $STOP_FILE — the loop halts before its next round"; exit 0 ;;
esac

ROUNDS="${1:-42}"
# One hmz exec per round (fresh cycle each): hmz's pi-backend session anchoring
# wedges across turns with the omp argv shim (no --session-id), so the loop
# lives HERE instead of inside one flow run. Round count is tracked by the
# ledger tail (the flow's own state is per-run).
DONE=0
for ((i=1; i<=ROUNDS; i++)); do
  if [[ -f .humanize/flows/gsim_optimize/STOP || -f .humanize/flows/gsim_optimize/TARGET_ACHIEVED ]]; then
    echo "loop halted by marker file after $((i-1)) round(s)"; exit 0
  fi
  echo "=== humanize round $i/$ROUNDS $(date -R) ==="
  CFG="$(mktemp --suffix=.yaml)"
  sed "s/^rounds: .*/rounds: 1/" .humanize/flows/gsim_optimize/budget.yaml > "$CFG"
  if hmz exec -f local/gsim_optimize -a "pi/glm-5.3:high" -c "$CFG" \
       "$(cat .humanize/flows/gsim_optimize/round-brief.md)"; then
    :
  else
    echo "round $i hmz exec failed (exit $?) — stopping loop"; exit 1
  fi
  rm -f "$CFG"
done
echo "=== $ROUNDS rounds complete ==="
