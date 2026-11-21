#!/bin/bash
set -eu
ulimit -v 16777216
ulimit -f 8388608
cpu_budget=$1
shift
exec prlimit --cpu="$cpu_budget" -- /usr/bin/time -f 'wall=%e cpu=%U+%S RSS=%M' "$@"
