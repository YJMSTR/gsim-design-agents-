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
  LEDGER=../gsim-task-saturate-sparse/candidates.jsonl
  BEFORE=$(tail -1 "$LEDGER" 2>/dev/null | python3 -c 'import json,sys;print(json.loads(sys.stdin.read())["name"])' 2>/dev/null || echo none)
  CFG="$(mktemp --suffix=.yaml)"
  sed "s/^rounds: .*/rounds: 1/" .humanize/flows/gsim_optimize/budget.yaml > "$CFG"
  # A round is DONE when its ledger entry lands, not when hmz exits: omp's rpc
  # handshake can hang after a completed turn (protocol divergence), so timeout
  # bounds the process and the ledger tail is the real completion signal.
  timeout "${ROUND_TIMEOUT:-7200}" hmz exec -f local/gsim_optimize -a "pi/glm-5.3:high" \
    -c "$CFG" "$(cat .humanize/flows/gsim_optimize/round-brief.md)" || \
    echo "round $i exec ended early (code $?)"
  rm -f "$CFG"
  pkill -f "omp --mode rpc" 2>/dev/null || true
  AFTER=$(tail -1 "$LEDGER" 2>/dev/null | python3 -c 'import json,sys;print(json.loads(sys.stdin.read())["name"])' 2>/dev/null || echo none)
  if [[ "$BEFORE" == "$AFTER" ]]; then
    echo "round $i produced NO new ledger entry (${BEFORE}) — counting as a spent round"
  else
    echo "round $i recorded: $AFTER"
  fi
done
echo "=== $ROUNDS rounds complete ==="
