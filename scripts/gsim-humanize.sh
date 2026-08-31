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
CFG="$(mktemp --suffix=.yaml)"
trap 'rm -f "$CFG"' EXIT
sed "s/^rounds: .*/rounds: $ROUNDS/" .humanize/flows/gsim_optimize/budget.yaml > "$CFG"
exec hmz exec -f local/gsim_optimize -a "pi/glm-5.3:high" \
  -c "$CFG" \
  "$(cat .humanize/flows/gsim_optimize/round-brief.md)"
