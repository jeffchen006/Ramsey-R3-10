#!/usr/bin/env bash
# One fresh agent session (one lane turn or one critic turn) as `codex exec` through SoruxGPT.
#   turn.sh MODEL EFFORT MINUTES PROMPT_FILE LAST_MESSAGE_FILE LOG_FILE
# Exit: 0 done, 124 cut off at MINUTES, other = failed (see LOG_FILE).
# The key is read from the hmz account (~/.hmz/providers/codex/soru/provider.json); it is never
# written into this repository. Codex keeps its state in scratch/flow/codex_home.
set -u
MODEL=$1 EFFORT=$2 MIN=$3 PROMPT=$4 OUT=$5 LOG=$6
ROOT=$(cd "$(dirname "$0")/../.." && pwd)
export CODEX_HOME=$ROOT/scratch/flow/codex_home
mkdir -p "$CODEX_HOME" "$(dirname "$OUT")" "$(dirname "$LOG")"
SORUX_KEY=$(python3 -I -c 'import json,os;print(json.load(open(os.path.expanduser("~/.hmz/providers/codex/soru/provider.json")))["env"]["CODEX_PROVIDER_KEY"])') || exit 3
export SORUX_KEY
CODEX=${CODEX:-$HOME/bin/codex}
cd "$ROOT" || exit 3
rm -f "$OUT"
# Write fence (Landlock): this turn and every job it starts may write only in the workspace,
# the temp dirs and the user caches below. Reading and the network stay open.
FENCE=(python3 -I "$ROOT/ralph/bin/fence.py" "$ROOT" /tmp /var/tmp /dev /proc "$HOME/.cache" "$HOME/.elan" --)
timeout -k 120 $((MIN * 60)) "${FENCE[@]}" "$CODEX" exec --skip-git-repo-check --dangerously-bypass-approvals-and-sandbox \
  -C "$ROOT" -m "$MODEL" -c "model_reasoning_effort=\"$EFFORT\"" \
  -c model_provider=sorux -c 'model_providers.sorux.name="sorux"' \
  -c 'model_providers.sorux.base_url="https://ai.soruxgpt.com/v1"' \
  -c 'model_providers.sorux.wire_api="responses"' -c 'model_providers.sorux.env_key="SORUX_KEY"' \
  -o "$OUT" - < "$PROMPT" > "$LOG" 2>&1
