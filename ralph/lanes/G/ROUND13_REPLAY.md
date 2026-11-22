# Round 13: floor 122 and the e170 equality price

## Exact conditional thresholds

The accepted starting ledger has 278 keys and uses the inherited gluing
premises. The new unrestricted MTF d6 floor 122 is already confirmed
in `ralph/critic/round_012.md`. The inequalities `Z>=48` and `Z<=e-122`
give 20+19 removals at e168/e169. At e170 in `(2,7,0,31)`, the other
d6 root is adjacent by G-021 and the five remaining neighbours have
odd degree, so `Z` cannot equal 48. These 40 removals are not new
round-13 claims. The surviving 238 keys match the critic TSV key for key.

Using floors 108/97/88, a checked LP contradiction at d9 floor `f`
proves `t9<=f-1`: a graph all of whose d9 residues have at least `f`
would give a point of that LP. All 12 new bounds improve by one:

| e | `(n6,n7,n8,n9)` | t9 old→new |
|---:|---|---:|
|170| (2,0,14,24) | 94→93 |
|170| (2,1,12,25) | 94→93 |
|170| (2,3,8,27) | 93→92 |
|171| (1,0,15,24) | 95→94 |
|171| (1,4,7,28) | 94→93 |
|171| (2,0,12,26) | 94→93 |
|171| (2,1,10,27) | 94→93 |
|172| (1,0,13,26) | 95→94 |
|172| (1,1,11,27) | 95→94 |
|172| (2,1,8,29) | 94→93 |
|173| (1,1,9,29) | 95→94 |
|174| (1,3,3,33) | 95→94 |

The floor-120 matched polytopes are all numerically feasible at the
12 newly rejected pins (`t9.binding.log`). There are no new U88 keys
or floor-88 contradictions and the ten old U88 keys are preserved.
In `scratch/G/round13`, `thresholds.csv` is the full ledger,
`multipliers.jsonl` certifies the 39 floor cuts, the parity cut, and
the 12 new bounds. The one-core production scan took 47.32 CPU-s.

## Integer projections (necessary, not extensions)

See `rows/e170_equality_signatures.md`. Nine single-root keys give
66 template/key rows (11 signature orbits); seven adjacent-root keys
give 30 rows (three marked wing shapes, paired before inventory
filtering). The join uses the same 28 sites with both supports and
their degree, cross-edge incidence totals, matching constraints and
independent-star bounds. It does not equate actual W-edge identities.
All 96 rows have checked integer points. One first-pass cap yielded a
point on retry. Production 31.33+96.92+11.68 CPU-s, exact replay
26.64+19.24 CPU-s. Smaller C13: 26 literal pairs accepted, 260 swapped
alignments rejected. Neither a target graph nor another closure.

## Matched fixed-source comparison (not a census)

See `rows/e170_bundled_demands.md`. Pilot: 128 rows from the old
522-row `scratch/G/round6/e122.pilot.g6`. Held-out: 384 spaced rows
from `scratch/G/round4/lat122.cover6.g6` after raw deduplication and
exclusion of pilot rows. `held.source.log` specifies the selection.
Dense labels show 512 distinct classes across the two panels. The
90,306-row source is partial, not the 90,223-row inverse scan.

| Method | Pilot 128 | Held-out 384 | Combined user CPU-s |
|---|---:|---:|---:|
| Old clique, legal maximal row sizes 5–8 | 66 rejected | 191 rejected | 0.22 |
| Old clique then pinned core, 5k conflicts on remainder | 58 unchecked UNSAT, 4 cap | 177 unchecked UNSAT, 16 cap | 26.90 incl. clique |
| Scout N unpinned rule (mode 0) | 128 rejected | 384 rejected | 16.62 |
| Equality sizes/one-overlap (mode 1) | 128 rejected | 384 rejected | 17.56 |
| Equality bundled/quota (mode 2) | 128 rejected | 384 rejected | 17.90 |

Bundling reduces deletion waves 1,003→827, but gains no rejections
and is slightly slower. Keep mode 0 for pricing. Literal planted
columns at 13 C13 equality roots survive all modes; independent
pivoted Python reconstruction checks 12 rows per panel in each mode
and matches obstruction IDs. No old-core UNSAT with missing proof is
credited as cert. No floor 123 or e170 distribution removal follows.

## Replay commands

Run from `scratch/G/round13` with a one-core thread limit and 16-GB
virtual-memory cap:

```bash
export PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
ulimit -v 16777216
r=../../..
p=$r/opt/venv/bin/python
g=$r/ralph/lanes/G
nice -n 5 timeout 45s "$p" -B "$g/round13_thresholds.py" . --verify
nice -n 5 timeout 15s "$p" -B "$g/round13_signatures.py" control .
for mode in single pair; do
  nice -n 5 timeout 90s "$p" -B "$g/round13_signatures.py" "$mode" . --verify
done
g++ -O3 -std=c++17 -I"$r/ralph/lanes/B/src" "$g/equality_demands.cc" -o equality_demands
cc -O3 -I"$r/ralph/lanes/B/src" "$g/demand_clique33.c" -o demand_clique33
nice -n 5 timeout 15s "$p" -B "$g/check_equality_demands.py" cal .
for prefix in attach held; do
  for mode in 0 1 2; do
    nice -n 5 timeout 45s ./equality_demands 9 6 6 170 "$mode" < "$prefix.g6" | cmp - "$prefix.$mode.tsv"
  done
  nice -n 5 timeout 100s "$p" -B "$g/check_equality_demands.py" audit . --count 12 --prefix "$prefix"
done
```

H/critic: bind the 12 new thresholds, not the signature or attachment
results as whole-key closures. G: no production until an independent
cover or a substantially stronger shared-W cut. The mixed e168 proofs
are historical and not additive. B owns descent to order32/e108.
