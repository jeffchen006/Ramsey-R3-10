# Round 4: R(6) three-root and isolated-pair strata

All claims refer to the 9-regular case with maximum codegree six; none
closes R(6) or the whole Ramsey problem. `X` in the P3 rows means the
22-vertex complement of the three closed neighbourhoods. In the P2
rows `X` is the order-26 pair residue and `X'` removes a third anchor.
The accepted order-22 census is `gluing/val/r3_7_22.g6`. Independent
decoding verifies all 191 graphs, their triangle/alpha bounds and
the edge-count totals 1,6,30,60,59,25,10 at 60..66 edges.

| Branch | Necessary reduction | Checked scope |
|---|---|---|
| P3 diagonal five, e63 | Hall reduction, 13 ordered boundaries -> 8 after reversal. Fixed Lite6. | 60 x 8 = 480 CNFs, checked LRAT and identical full replay. Combined with accepted e64 reduction gives e(X)<=62. |
| P3 diagonal three, e65/e66 | Variable eligible boundary edges with guarded size-six core rows. | 35 CNFs, checked LRAT and identical full replay. Gives e(X)<=64 at this diagonal. |
| P3 diagonal four, e65/e66 | Same relaxation, separate diagonal parameter. | 35 CNFs, checked LRAT and identical full replay. Gives e(X)<=64 at this diagonal. |
| P3 diagonal five, e62 | 90 ordered boundaries -> 49 modulo reversal -> 44 passing. | 30 x 44 = 1,320 expected CNFs. Check final status in STATE; partial coverage is not a closure. |
| Isolated P2, f8, degree-three anchor, e(X')=65 | Same-wing equality template has fixed codegree seven; only 2+1 remains. | 25 CNFs, checked LRAT and identical full replay. Gives e(X')<=64 for this branch only. |

Reduction proofs: `proofs/path_three.md`, `proofs/p3_e63_relaxation.md`,
`proofs/isolated_pair.md` and `proofs/isolated_pair_anchor.md`.
`ROUND3_REPLAY.sha256` freezes the accepted prior-round evidence.

## Calibration and costs

- All fixed/variable P3 relaxations preserve planted C21 completions
  (with twin/profile sorting) and reject one-edge corruptions. In C22
  the isolated-pair bounds check on seven complete-wing and four
  one-missing pairs. C21 isolated-pair anchor calibration: 331 known
  regular graphs, 444 degree anchors and 23 equality templates;
  all 23 planted assignments passed and their flips failed.
- Matched e63 baseline and root-twins: each 16/16 plain refutations,
  429.31 and 389.75 CPU-s respectively, no proofs. Eight proof pilots:
  Lite6 37.68 CPU-s, Min6 312.98 CPU-s. Production Lite6 remaining
  472 took 2,076.95 CPU-s; full 480-proof replay took 1,023.09 CPU-s.
- Flexible e65/e66: respectively 13.73+199.42 and 14.53+197.68
  CPU-s at diagonals three/four; the 70 replays took 269.03 CPU-s.
  Four dispersed e64 keys at each diagonal also passed (52.26 and
  44.72 CPU-s total), but 55 residue keys per diagonal are untested.
- Flexible guarded diagonals three/four capped on each sampled lower
  e63/62/61/60 key. Flexible guarded/universal diagonal five both
  refuted one e63 seed but capped on two e62 and one e60 seeds. For e62,
  full 44-layout selector table: one checked seed, one cap; twelve
  fixed-boundary proofs on the same two seeds: 73.34 CPU-s, 12/12.
- Lower fixed pilot: five e61 keys in 56.56 CPU-s; five e60 keys in
  80.50 CPU-s. The corresponding full covers are 894 and 320 keys;
  neither was launched. The costs project to about 4.2 CPU-h before
  replay; this is a sample estimate, not a completion result.

## Replay from `scratch/C`

Do not overwrite proof files or retained logs. Timings vary. Each
command should run under `ulimit -v 16777216` and a wall timeout and
nice value as shown. To replay into new transcripts, choose fresh
log filenames; the index expects the canonical names shown in STATE.

```sh
lane=../../ralph/lanes/C
census=../../gluing/val/r3_7_22.g6
bin=../../opt/bin
py=../../opt/venv/bin/python
ulimit -v 16777216
nice -n 5 timeout 60 "$py" -B "$lane/p3_e63.py" "$census" "$bin" p3e63-minproofs --control
for orbit in 0 1 2 3 6 7 9 12; do
  nice -n 5 timeout 600 "$py" -B "$lane/p3_e63.py" "$census" "$bin" p3e63-minproofs \
      --orbit "$orbit" --mode lite6 --op verify
done
nice -n 5 timeout 60 "$py" -B "$lane/p3_e63_index.py" "$census" . --replay
for diagonal in 3 4; do
  nice -n 5 timeout 360 "$py" -B "$lane/p3_flexible.py" "$census" "$bin" p3flex-pilot \
      --diagonal "$diagonal" --mode guarded --verify --edges 65 --edges 66
done
nice -n 5 timeout 60 "$py" -B "$lane/p3_round4_index.py" "$census" . --part upper

nice -n 5 timeout 120 c++ -std=c++20 -O3 -Wall -Wextra -pedantic "$lane/p3_boundary_audit.cpp" -o p3_boundary_audit
nice -n 5 timeout 120 ./p3_boundary_audit 18 17 16 15
nice -n 5 timeout 60 "$py" -B "$lane/p3_boundary_levels.py" --dump
nice -n 5 timeout 60 "$py" -B "$lane/p3_round4_index.py" "$census" . --part boundary
nice -n 5 timeout 60 "$py" -B "$lane/p2_isolated_control.py" ../../duo/reg6_22.g6
nice -n 5 timeout 60 "$bin/pickg" -q -d6 -D6 ../B/val/r3_7_21.g6 p2iso-regular21.g6
nice -n 5 timeout 60 "$py" -B "$lane/p2_anchor.py" p2iso-regular21.g6 "$bin" p2anchor --control
nice -n 5 timeout 300 "$py" -B "$lane/p2_anchor.py" "$census" "$bin" p2anchor --split 1 --verify
nice -n 5 timeout 60 "$py" -B "$lane/p3_round4_index.py" "$census" . --part isolated-upper
```

`p3_boundary_audit.cpp` exhausts 27-bit assignments of the required
popcount and checks all seven Hall subset inequalities on each side
instead of finding matchings. The index performs an independent
edge-by-edge reversal and verifies each fixed filter. At e62, the
checked 44 layouts are sufficient as follows. A fixed root has no
X-neighbours, so its nonadjacent boundary pairs need a fixed common
neighbour by maximality and must respect the root cap. A boundary
vertex of degree below three would need at least seven independent
X-neighbours. The other tests only reject an already present forbidden
biclique, excess codegree or independent 10-set.

For a completed e62 production and replay, the following tests exact
coverage, matches proof hashes and CNF hashes, and checks proof sizes:

```sh
nice -n 5 timeout 60 "$py" -B "$lane/p3_round4_index.py" "$census" . --part lower --replay
```

The four e62 replay wrappers call `replay_p3_e62_shard.sh`; the script
never reads a proof until its producer row reports the full batch.
For spot checks use `p3_low_trials.py` with the saved boundary dump,
`--row N --layout K --mode fixed --verify`. A partial index explicitly
counts checked, deferred and absent keys; only the full proof and
position-preserving replay cover excludes the stratum.
