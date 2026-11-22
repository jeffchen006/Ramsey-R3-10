#!/usr/bin/env bash
set -euo pipefail
export LC_ALL=C
root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../../../.." && pwd)
[[ $PWD == "$root/scratch/B/"* ]]
source=$root/scratch/ideas/r021_N
prior=$root/scratch/B/work/e108_r11
(cd "$source" && sha256sum -c B.sha256)
[[ $(wc -l < "$source/pool96.set") == 1842 ]]
[[ $(wc -l < "$root/scratch/B/work/e108_r11_complement/reducible96.g6") == 33312 ]]
[[ $(wc -l < "$source/lift96.union") == 23 ]]
for degree in 4 5 6; do
    [[ ! -s $source/lift96.$degree.set ]]
done
[[ $(wc -l < "$source/lift96.7.set") == 16 ]]
[[ $(wc -l < "$source/lift96.8.set") == 7 ]]
sort -u "$source/lift96."{4,5,6,7,8}.set | cmp "$source/lift96.union" -
comm --check-order -23 "$source/lift96.union" "$prior/critical.g6" > source.novel
[[ ! -s source.novel ]]
printf '%s\n' 'PASS 15 hashes; 1,842 + 33,312 source split; all 23 lifts in the named critical sublist'
