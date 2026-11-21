#!/bin/bash
set -euo pipefail
root=$(cd "$(dirname "$0")/../../.." && pwd)
file=$(realpath "$1")
cd "$root/lean"
export LEAN_PATH="$PWD/.lake/build/lib/lean"
exec "${HOME}/.elan/bin/lean" --run SBMain.lean "$file"
