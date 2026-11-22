#!/usr/bin/env bash
# One fresh Gemini or Claude turn (Antigravity `agy`, driven by agentlink) under the same Landlock write fence as turn.sh.
#   turn_agy.sh MODEL EFFORT MINUTES PROMPT_FILE LAST_MESSAGE_FILE LOG_FILE NAME
# Exit: 0 done, 124 cut off at MINUTES, 2 failed turn (agentlink), other = failed (see LOG_FILE).
# The agentlink agent r310-NAME is made on first use and reset before every turn (a fresh context each
# round, as in a Ralph loop). It runs on the user's Google AI subscription (quota shared with other jobs); keep the use moderate.
set -u
MODEL=$1 EFFORT=$2 MIN=$3 PROMPT=$4 OUT=$5 LOG=$6 NAME=r310-$(echo "${7:-turn}" | tr -c 'A-Za-z0-9_\n-' '-')
ROOT=$(cd "$(dirname "$0")/../.." && pwd)
cd "$ROOT" || exit 3
mkdir -p "$(dirname "$OUT")" "$(dirname "$LOG")"
rm -f "$OUT"
AL=${AGENTLINK:-$HOME/.local/bin/agentlink}
have=$("$AL" list 2>/dev/null | awk -v n="$NAME" '$1 == n {print $3}')
if [ -n "$have" ] && [ "$have" != "$MODEL" ]; then "$AL" rm "$NAME" >/dev/null 2>&1; have=; fi
if [ -z "$have" ]; then
  "$AL" new "$NAME" --backend agy --model "$MODEL" --cwd "$ROOT" --task-file "$ROOT/ralph/GEMINI_ROLE.md" > "$LOG" 2>&1 || exit 3
fi
"$AL" reset "$NAME" >> "$LOG" 2>&1
FENCE=(python3 -I "$ROOT/ralph/bin/fence.py" "$ROOT" /tmp /var/tmp /dev /proc "$HOME/.cache" "$HOME/.elan"
       "$HOME/.local/state/agentlink" "$HOME/.gemini" --)
# Own process group, so that a cut-off also ends agy (agentlink's child). Detached jobs (setsid) are not touched.
setsid "${FENCE[@]}" "$AL" ask "$NAME" --from r310_ralph - < "$PROMPT" > "$OUT" 2>> "$LOG" &
PG=$!
( sleep $((MIN * 60)); kill -TERM -- -$PG 2>/dev/null; sleep 120; kill -KILL -- -$PG 2>/dev/null ) &
WATCH=$!
wait $PG; CODE=$?
kill $WATCH 2>/dev/null
case $CODE in 143|137) exit 124 ;; *) exit $CODE ;; esac
