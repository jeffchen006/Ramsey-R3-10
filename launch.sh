#!/usr/bin/env bash
# Start the r310_ralph hmz flow (8 lanes + 1 critic, a fresh session each round) in this folder.
#   ./launch.sh               48 h run, GPT-6.2-sol through SoruxGPT for lanes and critic, 80 cores
#   ./launch.sh --dry-run     one short test round, no research
#   ./launch.sh --resume      carry on the last run
# Engine 'exec' (default): each turn is `codex exec` via ralph/bin/turn.sh under a Landlock write
# fence (ralph/bin/fence.py). hmz 0.2.1/0.2.2's own codex harness fails with the SoruxGPT account.
# Claude later: ENGINE=hmz WORKER=claude/claude-opus-5-5:high CRITIC=... ./launch.sh --resume
# Extra -p settings may follow, e.g.: ./launch.sh -p round_minutes=45,cores=64
set -euo pipefail
cd "$(dirname "$0")"
HMZ=${HMZ:-$HOME/.local/share/uv/tools/hmz/bin/hmz}
ENGINE=${ENGINE:-exec}
WORKER=${WORKER:-codex/gpt-6.2-sol:high}   # used only by ENGINE=hmz
CRITIC=${CRITIC:-codex/gpt-6.2-sol:high}   # used only by ENGINE=hmz
MODEL=${MODEL:-gpt-6.2-sol}
DURATION=${DURATION:-48h}
args=()
params="budget.duration=$DURATION,hours=${DURATION%h},engine=$ENGINE,model=$MODEL"
case "${1:-}" in
  --dry-run)
    params="budget.duration=40m,dry_run=true,max_rounds=1,hours=0.5,engine=$ENGINE,model=$MODEL"
    shift ;;
  --resume)
    args+=(--resume)
    shift ;;
esac
exec "$HMZ" exec -f r310_ralph -a "worker=$WORKER,critic=$CRITIC" -p "$params" "${args[@]}" "$@" "${NOTE:-}"
