#!/usr/bin/env bash
set -euo pipefail
root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../../.." && pwd)
source "$root/opt/env.sh"
export R310_ROOT="$root" PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
opb=$(realpath "${1:?usage: check_base.sh cube_R.opb}")
cd "$root/scratch/A/rc7"
ulimit -v 16777216
ulimit -f 2097152
sha256sum "$opb" Rc7b.cnf
/usr/bin/time -f 'TIMING wall=%e user=%U sys=%S rss=%M' \
    nice -n 5 timeout 720 prlimit --cpu=480:485 python -c '
import os, sys
root = os.environ["R310_ROOT"]
sys.path.insert(0, root + "/cert")
import base40_cert
base40_cert.BIN = root + "/opt/bin"
base40_cert.main()
' "$opb" Rc7b.cnf base-cert --dmin 9 --dmax 9 --mtf --fix-nbhd 9 \
    --codeg-max 7 --codeg-pair 7 --edges 10-11,10-12,8-11,8-12,9-11,9-12 \
    --block-from 13 --block-e 85
