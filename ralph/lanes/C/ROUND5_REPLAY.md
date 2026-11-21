# Round 5: P3 edge caps, high-arm cuts, and isolated full-wing pairs

The objects are Case R(6) graphs only. No new whole R(6), R, or
R(3,10) exclusion is asserted. Each certificate bundle needs the
named hand bridge and the exact local residue cover as well as LRAT.

## Unrestricted P3 edge caps (composite cert, pending critic)

| New stratum | Checked keys | Bridge | Implication together with accepted C-016 |
|---|---:|---|---|
| Diagonal five e62 | 30 residues × 44 boundary orbits = 1,320 | `proofs/p3_e63_relaxation.md`, `ROUND4_REPLAY.md` | e(X)<=61 at diagonal five |
| Diagonal three e64 | 59 guarded variable-boundary CNFs | same | e(X)<=63 at diagonal three |
| Diagonal four e64 | 59 guarded variable-boundary CNFs | same | e(X)<=63 at diagonal four |

All 1,438 keys have proof-checked production and replay. The round
five index verifies *terminal* shard ownership and row counts, checks
expected disjoint pilot/producer coverage, requires exact replay
record equality including regenerated DIMACS digests, and rehashes
every retained LRAT against its replay record. No missing/deferred
key. For e62 the independent boundary audit confirms 90 ordered to
49 reversal orbits to 44 passing. The pilot/production/replay costs
were 73.34 / 8,556.74 / 3,588.09 CPU-s, with 14,891,255,705 proof
bytes. e64 actual production (not counting the eight prior pilots)
was 873.04 and 761.39 CPU-s at diagonals 3 and 4; replay 359.31 and
346.02 CPU-s, 1,290,785,634 proof bytes. The caps are for the
associated P3 residue only, not an isolated P2 residue.

## Arm counts and isolated complete wings

- `proofs/p3_complete_arms.md`: the 119 contemplated full-arm (9/9)
  proofs are unnecessary. A hand contradiction uses at least four
  antineighbours of the triple intersection, and the already
  accepted diagonal-three e(X)<=64. Thus in global f*=9 the
  nonempty codegree-six graph J is a matching. Degree-four positive
  and corrupted controls cover both wing-edge types. C35, C21 and
  C22 were also checked; they had partitioned but no full-arm marks.
- `proofs/p3_mixed_arms.md`: for diagonal three and both arms >=8,
  3 of 16 boundary layouts at e(X)<=63 have necessary 22-vertex
  antineighbour CNFs refuted and replayed (indices 1, 5, 6). The
  other 13 are relaxation-SAT only. The C21 actual 2-vertex
  antineighbour calibration passes and rejects the corrupted
  attachment. The 9/8 arm subcase has two remaining boundaries,
  one at each of diagonals three and four, both e63. Their fixed
  Lite6 proof cover is complete: 60+60 terminal exact checks,
  identical regenerated CNF and retained proof hashes, no caps or
  absences. Production 373.31 / 772.88 CPU-s, replay 138.97 / 187.44
  CPU-s, 1,570,731,234 proof bytes. Consequently, together with the
  earlier full-arm and diagonal-five arguments, in R(6) at f*>=8
  every P3 has diagonal three/four and both arm counts eight. This
  is a composite cert claim pending critic, not a P3 or P2 exclusion.
- `proofs/p2_full_wings.md`: an individual full-wing pair has total
  common-support excess over two at most two, independent of J.
  In global f*=9 there is no codegree-six pair within either wing.
  Deleting the closed neighbourhood of the smaller wing leaves a
  marked (3,7) order-21 graph or an order-20 graph with a (3,6)
  order-13 core. These reductions and the counts below are not P2
  exclusions. The C22 complete-pair control tests all seven observed
  k4 full-wing pairs, 14 actual wing packings and 14 impossible
  lower-overlap counterparts.

The exact catalogue sieve has two outputs. In the order-21 catalogue
13,576,969 degree-six marks give 35,257 sum-passing marks and 35,248
packing/degree-passing marks (31,693 input isomorphism classes).
The stronger support, root-codegree and common-column tests leave
35,099 marks (31,565 input classes); the column check alone cuts none.
Separately 246,483/275,086 order-13 cores admit three independent
five-sets of pair overlap <=1 covering the core. These are cover
sizes, not numbers of extendible graphs. Scan CPU under 5s total.

## Replay commands from `scratch/C`

The expected output basenames below are used by the frozen indexes.
Use fresh output names when rebuilding to avoid overwriting evidence.
All software and source references are repository-relative.

```sh
set -euo pipefail
ulimit -v 16777216
lane=../../ralph/lanes/C
py=../../opt/venv/bin/python
bin=../../opt/bin
census=../../gluing/val/r3_7_22.g6
nice -n 5 timeout 180 "$py" -B "$lane/p3_round5_index.py" "$census" . \
    --part lower --hash-retained --output replay-e62-index.tsv
cmp p3r5-e62-index.tsv replay-e62-index.tsv
nice -n 5 timeout 100 "$py" -B "$lane/p3_round5_index.py" "$census" . \
    --part upper --hash-retained --output replay-e64-index.tsv
cmp p3r5-e64-index.tsv replay-e64-index.tsv
nice -n 5 timeout 120 "$py" -B "$lane/p3_complete_arms_check.py" \
    p2iso-regular21.g6 ../../duo/reg6_22.g6
nice -n 5 timeout 45 "$py" -B "$lane/p3_antineighbour.py" "$bin" p3r5-antineighbour --control
nice -n 5 timeout 90 "$py" -B "$lane/p3_antineighbour.py" "$bin" p3r5-antineighbour \
    --verify --layout 1 --layout 5 --layout 6
nice -n 5 timeout 90 "$py" -B "$lane/p3_mixed_arms.py" "$census" "$bin" p3r5-mixed --control
nice -n 5 timeout 100 "$py" -B "$lane/p3_round5_index.py" "$census" . \
    --part mixed --hash-retained --output replay-mixed-index.tsv
cmp p3r5-mixed-index.tsv replay-mixed-index.tsv
nice -n 5 timeout 90 c++ -O3 -std=c++20 -Wall -Wextra -pedantic "$lane/p2_wing_windows.cpp" -o p2_wing_windows
nice -n 5 timeout 45 ./p2_wing_windows control ../../duo/reg6_22.g6
nice -n 5 timeout 150 ./p2_wing_windows core13 ../B/val/r3_6_13.g6 replay-core13.tsv
cmp p2r5-core13.tsv replay-core13.tsv
nice -n 5 timeout 150 ./p2_wing_windows window21 ../B/val/r3_7_21.g6 replay-window21.tsv
cmp p2r5-window21.tsv replay-window21.tsv
nice -n 5 timeout 150 ./p2_wing_windows strong21 ../B/val/r3_7_21.g6 replay-strong21.tsv
cmp p2r5-strong21.tsv replay-strong21.tsv
```

The mixed-arm and e64 production scripts intentionally refuse to
overwrite proof files. For spot replay of a specific checked row,
use `p3_mixed_arms.py CENSUS BIN p3r5-mixed --diagonal D --row N
--verify` or `p3_flexible.py CENSUS BIN p3flex-pilot --diagonal D
--mode guarded --row N --verify`. For e62 use the fixed row/layout
replay in `ROUND4_REPLAY.md`. Take care to preserve the fixed boundary
input and check the corresponding rows of each TSV.
