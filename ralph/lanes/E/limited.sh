#!/bin/bash
set -eu
ulimit -v 16777216
ulimit -f "${E_FILE_BLOCKS:-8388608}"
cpu_budget=$1
shift
exec prlimit --cpu="$cpu_budget" -- /usr/bin/time -f 'wall=%e cpu=%U+%S RSS=%M' "$@"
