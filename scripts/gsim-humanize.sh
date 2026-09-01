#!/usr/bin/env bash
# Drive the gsim campaign through humanize2. Effort: glm-5.3:max by default
# (user directive 2026-09-01: use max, not high; kimi/k3:max also available). (pi backend = omp via ~/.local/bin/pi shim).
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
  # Builder + reviewer (user directive 2026-09-01): builder = glm-5.3 (or k3),
  # reviewer = codexa/gpt-5.6-sol, falling back to k3 when gpt is unavailable.
  # Guards: inherited junk AGENT/BUILDER/REVIEWER values (e.g. "1") are ignored.
  BUILDER="${BUILDER:-${AGENT:-pi/glm-5.3:max}}"
  case "$BUILDER" in */*) : ;; *) BUILDER="pi/glm-5.3:max" ;; esac
  REVIEWER="${REVIEWER:-}"
  if [[ -z "$REVIEWER" ]]; then
    REVIEWER="pi/codexa/gpt-5.6-sol:max"
    if ! timeout 90 omp --model codexa/gpt-5.6-sol --print "ok" >/dev/null 2>&1; then
      echo "reviewer fallback: codexa/gpt-5.6-sol unavailable -> k3"
      REVIEWER="pi/k3:max"
    fi
  fi
  timeout "${ROUND_TIMEOUT:-7200}" hmz exec -f local/gsim_optimize -a "$BUILDER" -a "$REVIEWER" \
    -c "$CFG" "$(cat .humanize/flows/gsim_optimize/round-brief.md)" &
  EXECPID=$!
  # Ledger watcher: the round's real end is its ledger entry. Once it lands,
  # give the agent 180s of grace for final words, then kill the (handshake-
  # wedged) exec instead of idling to the timeout.
  REVIEWS=runs/humanize/reviews.jsonl
  REV_BEFORE=$(wc -l < "$REVIEWS" 2>/dev/null || echo 0)
  while kill -0 $EXECPID 2>/dev/null; do
    sleep 30
    NOW=$(tail -1 "$LEDGER" 2>/dev/null | python3 -c 'import json,sys;print(json.loads(sys.stdin.read())["name"])' 2>/dev/null || echo none)
    if [[ "$NOW" != "$BEFORE" ]]; then
      # Builder's entry landed; the REVIEWER turn follows inside the same
      # exec. Wait for its verdict line (reviews.jsonl growth) or a hard
      # 45-min grace before releasing the (handshake-wedged) exec.
      REV_DEADLINE=$(( $(date +%s) + 2700 ))
      while kill -0 $EXECPID 2>/dev/null && [[ $(date +%s) -lt $REV_DEADLINE ]]; do
        sleep 30
        REV_NOW=$(wc -l < "$REVIEWS" 2>/dev/null || echo 0)
        [[ "$REV_NOW" != "$REV_BEFORE" ]] && break
      done
      kill $EXECPID 2>/dev/null && echo "round $i: ledger landed ($NOW), exec released (reviews $REV_NOW/$REV_BEFORE)"
      break
    fi
  done
  wait $EXECPID 2>/dev/null || true
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
