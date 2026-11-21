# Round 6 replay: complementary full-wing windows

## Exact result and status

**Composite enum + cert, pending critic:** in the global `R(6), f*=9`
subcase, no marked pair has `(|N(Y)∩X|,|N(Z)∩X|)=(12,12)`.
Equivalently every marked pair has at most one vertex of X avoiding
both wings. The other three size pairs `(12,13),(12,14),(13,13)` are
open. This is not a bound on the size or edge count of a P3 residue.
It uses the previous matching and no-siblings results and the complete
H21 census. The hand bridge is `proofs/p2_complementary_windows.md`.

The order-21 source is lane B's `scratch/B/val/r3_7_21.g6` (1,118,436
classes, each level matching GR Table 12; see lane B's frozen state).
The strong21 projected source and earlier checker are unchanged from
round 5. The exact checked joins are **pins**, not completed graphs:

| Stage | Count | Counting convention |
|---|---:|---|
| strong H21 | 35,099 | census graph index and marked root |
| wing pack / marked U | 659,322 / 331,422 | triples as unordered; U the uncovered pair |
| C-only / C and U degree join | 1,358,661 / 308,798 | ordered sides, left U in increasing order; both right orientations |
| full join with sorted mark sides | 154,614 | mark pairs with their U map, includes equal marks |
| C bijections, after C-codegree check | 332,582 | no additional loss at this check |
| distinct requests with both wing packs | 646,736 | no isomorphism quotient beyond side ordering and wing order |
| degree balance or local capacity rejects | 465,636 | exact necessary filter |
| degree propagation rejects | 6,802 | exact necessary filter |
| residual flow rejects (exclusive of previous screens) | 0 | exact necessary filter |
| complete-wing/codegree/iterated degree or flow rejects | 7,632 | exact necessary filter |
| permanent independent ten-set rejects | 165,532 | exact necessary filter |
| remaining cross-edge pins | 1,134 | CNF rebuilt from their *unpropagated* boundary |
| terminal refutations | 1,134 | CakeLRAT checked in production and replay; no SAT, caps, or missing rows |

Join pilot stride 97: 6,644 packs, 9 survivors; full filter 6.97
CPU-s and replay 7.47. CNF pilot stride 101: 12/12 checks, 7.01
CPU-s. Full proof production 432.47 CPU-s; fresh CNF/full retained
CakeLRAT replay 423.62 CPU-s. Separate 11-row textual LRAT spot
pilot passed both CakeLRAT and `lrat-check` (not a second verifier
on all 1,134). Seven C22 full-wing pairs give planted positive joins
and SATs; seven corrupted degree tests give checked UNSATs. Five
C22 marked pairs occur in graphs satisfying the global full-wing condition;
artificial one-/two-vertex reprojections test overlap multiplicities
and corruption, not completeness of a smaller global subcase.

## Binding and reproduction

`ROUND6_REPLAY.sha256` is rooted at the workspace. Terminal row format
is `index, vars, clauses, alpha_clauses, status, key_SHA256, CNF_SHA256,
proof_SHA256` (times excluded). `p2r6-cross-index.tsv` binds both logs
and actual proof/CNF files. A pin starts with left census ID, root and
U bitmask; then right census ID, root and ordered two U labels; then
the C bijection in ascending left-column order; then the three masks
for each wing. `cross` emits exactly the passing pack records. The
Python CNF implementation reconstructs the fixed graph independently
of the C++ search and validates both projections.

From `scratch/C`, replay in **fresh** filenames/workdirs (or use
equivalent paths in `scratch/critic` with explicit absolute inputs):

```sh
set -euo pipefail
ulimit -c 0
ulimit -v 16777216
lane=../../ralph/lanes/C
bin=../../opt/bin
nice -n 5 timeout 60 c++ -O3 -std=c++20 -Wall -Wextra -pedantic "$lane/p2_window_join.cpp" -o p2_round6_local
nice -n 5 timeout 45 ./p2_round6_local control ../../duo/reg6_22.g6
nice -n 5 timeout 60 ./p2_round6_local cross p2r5-strong21.tsv round6-pins-local.tsv 1
cmp p2r6-window21-cross.tsv round6-pins-local.tsv
nice -n 5 timeout 45 python3 -B "$lane/p2_cross_cert.py" control "$bin" round6-control-local ../../duo/reg6_22.g6
nice -n 5 timeout 30 python3 -B "$lane/p2_cross_cert.py" run "$bin" round6-spot-local p2r5-strong21.tsv \
  round6-pins-local.tsv --begin 0 --end 1 --verify --proof-dir p2r6-cross-full
```

The same `run` invocation with `--begin S --step 4` (no `--end`)
covers a shard; only launch if needed. Do not regenerate the full
production to check a hash. The existing exact binding can be checked
without writing into proof workdirs:

```sh
nice -n 5 timeout 60 python3 -B "$lane/p2_cross_index.py" round6-pins-local.tsv \
  p2r6-cross-full p2r6-cross-replay round6-index-local.tsv
cmp p2r6-cross-index.tsv round6-index-local.tsv
```

## Asymmetric pilot only

The H21 side-13 and side-14 scans have 243,859 and 33,222 marks,
respectively (1,458,506 and 353,115 packs). One-window independent
capacity inequalities remove **zero** of those packs in 11.74 CPU-s.
For `(12,14)`, H21 projects to 39 H19 degree/edge profiles. A K12
core-gluer pilot uses census steps of 307: 381 cores, 117,959 raw
windows in 53.38 CPU-s. Exact pair-bitset pruning reproduces those
raw bytes in 11.54 CPU-s; adding the 39 exact profiles gives the
verified raw subset of 5,013 in 3.90 CPU-s. Marked-root canonical
labeling leaves 4,749 H19 keys. All 5 H21 positive gluer controls
were recovered from their prescribed core. The unchanged unprofiled
K13/side12 pilot was capped at 100 wall seconds; its partial raw
output is not a census. No full H19/H20 run was launched.

Direct profile pairing would require at least **513,826,944 raw
wing/C maps in the H19 pilot alone**, before cross filters or
isomorphism deduplication of pair maps; 1.58e11 is a linear sample
projection, not a lower bound on the full cover. In the sample each
rooted H19 key has at least one admissible pack. For each profile
the count multiplies its H19 count, its exact H21 pack weight and
the factorials of repeated column sizes. C6/full-wing filters and
cross balance beyond the profile are not counted as survivors.

```sh
nice -n 5 timeout 65 c++ -O3 -std=c++20 -Wall -Wextra -pedantic "$lane/p2_marked_glue.cpp" -o round6-gluer
nice -n 5 timeout 55 ./round6-gluer control p2r5-strong21.tsv 5
nice -n 5 timeout 50 ./p2_round6_local profiles p2r5-strong21.tsv round6-profiles-local.tsv
cmp p2r6-h19-profiles.tsv round6-profiles-local.tsv
nice -n 5 timeout 60 ./round6-gluer glue ../B/val/r3_6_12.g6 12 307 > round6-h19-local.g6
nice -n 5 timeout 45 ./round6-gluer glue ../B/val/r3_6_12.g6 12 307 round6-profiles-local.tsv > round6-h19-profile-local.g6
nice -n 5 timeout 35 "$bin/labelg" -q '-fa^18z' round6-h19-profile-local.g6 round6-h19-label-local.g6
LC_ALL=C sort -u -T . round6-h19-label-local.g6 > round6-h19-canon-local.g6
nice -n 5 timeout 60 python3 -B "$lane/p2_profile_cost.py" round6-profiles-local.tsv \
  round6-h19-canon-local.g6 round6-h19-profile-local.g6 round6-h19-local.g6
```
