#!/usr/bin/env bash
set -euo pipefail
ulimit -v 16777216
lane=../../../ralph/lanes/A
time_args=(-f 'CPU %U %S WALL %e')
/usr/bin/time "${time_args[@]}" -o mixed.prefix.hash.time timeout -k 5s 675s prlimit --cpu=525:530 -- \
    bash "$lane/run_strip_audit.sh" mixed-prefix --fast-hash --exclude mixed.prefix.log > mixed.prefix.hash.log
/usr/bin/time "${time_args[@]}" -o lower.delta.hash.time timeout -k 5s 1250s prlimit --cpu=950:955 -- \
    bash "$lane/run_strip_audit.sh" continued --require-cover --only-continuation --fast-hash > lower.delta.hash.log
