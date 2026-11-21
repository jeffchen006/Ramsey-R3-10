# Involution with 32 fixed points and attachments 5,5,5,6

**Result (`enum`, pending critic): the entire `t=1` branch is excluded.**
Here `t` is the number of size-six attachments, not the maximum attachment
size. The result uses all graphs, not just maximal triangle-free ones. It
does not exclude `t=2,3,4`. The isolate branch is the previously reviewed
E-006; this file supplies the remaining no-isolate case.

## Necessary conditions and anchor coverage

Use the crown reduction in `involution.md`, including its universal `δ≥5`
dependency (Review 4, independently replayed by the critic in round 1).
Write `A_0,A_1,A_2,A_3` for the four disjoint independent attachments, where
`A_1` has size six and the others size five; let `W` be the remaining 11
fixed vertices. Let `H_i=G[F\A_i]`. Each `H_i` is triangle-free, `α(H_i)≤7`,
and has maximum degree at most 7. A whole side of the crown can join an
independent set of `W`; the three side vertices other than the one at
orbit `j` can join one in `W∪A_j`. Consequently

```
α(W) ≤ 5,                    α(W∪A_j) ≤ 6 for every j.
```

In the no-isolate case, call `w∈W` costly in the anchor `H_0` if its
induced degree in `W` is at least two or its degree in `H_0` is less
than seven. If `d_F(w)=9`, the bounds `d_{H_i}(w)≤7` imply that it has
at least two neighbors in each of the four attachments. It has at
least one neighbor in `W`, so equality holds: exactly two in each
attachment, one in `W`, and `d_{H_0}(w)=7`. Thus every costly vertex
has `d_F(w)≤8`; the others have `d_F(w)≤9`. Attachment vertices have
`d_F≤7`, since each also meets its own moved pair.

Choose `H_0` least by edge count among the three size-27 `H_i`, and
write `e=e(H_0)`. Each edge of `G[F]` within `W` is counted four times
in `Σ_i e(H_i)`, each between `W` and an attachment three times, and
each between attachments twice. If there are `b` costly vertices,

```
3e + 73 ≤ Σ_i e(H_i) = Σ_{v∈F\W} d_F(v) + 2Σ_{w∈W} d_F(w) ≤ 345 - 2b.
```

The 73 is the published `e(3,8;26)` lower bound (GR Table 13, D-E8).
The graph on `W` is not bipartite: a bipartition of its 11 vertices
would give an independent set of at least six. Therefore it contains
a shortest odd cycle, which is induced (a chord gives a shorter odd
cycle), has length at least five, and all its vertices are costly.
So `b≥5`, giving `85≤e≤87` by D-E8. The maximum `b` is 8, 7, 5 at
`e=85,86,87`, respectively. At `e=87` the cycle has length five and
the other six vertices have induced degree one. They cannot attach as
leaves to the cycle: deleting such a leaf and its neighbor leaves nine
vertices of independence number at most four (any independent set could
add the deleted leaf), hence another odd cycle, but at most four vertices
with degree at least two. Thus `W=C5 ⊔ 3K2` at `e=87` and its six matching
endpoints have degree seven in the anchor.

## Checks

The 1,470 input graphs come from McKay's `(3,8;27)` list. Each scanner
checks graph6, order, triangle-freeness, absence of an independent 8-set
and edge count. `shortg` independently checks pairwise nonisomorphism.
The `4,92,1374` counts match GR Table 13 (D-C8e), completing the cover.
These are unrooted anchors; all vertex assignments in each labeling are
allowed, so canonical labeling need not preserve `W` or the attachments.

- `crown_sieve.cc`: enumerate induced `C5/C7`, then enlarge to `W` while
  updating the costly-vertex bound and ruling out isolates. Try disjoint
  independent sets of sizes `6,5,5` in the complement, with `α(W∪A_j)≤6`
  for every proposed part. No partition reaches the extension stage.
  The generic extension stage, if reached, adds the missing independent
  attachment by independent neighbor masks and tests degrees, edge floors,
  and all moved independent-set types (fixed-only, two from one moved pair,
  or a subset of one crown side). For the last type only three/four moved
  vertices add rows; one or two are covered by the `H_i` checks.
- `replay_crown32_t1.cc`: independent check. For `e=85,86` scan all
  11-subsets (no odd-cycle branching). For `e=87` start with the induced
  degree-seven matching, then take a `C5` in its antineighborhood. Use a
  vertex-by-vertex quota coloring backtrack, with independent-set checks
  using a different recursion. This checks only the weaker necessary
  partition, not extension. The counts match for every anchor.
- `calibrate_crown.py`: the full extension code agrees with the direct
  10-vertex graph oracle on all six labeled path/one-edge Petersen anchors
  (three true, three false), explicitly checks the witnesses, and rejects a
  triangle. A direct subset oracle checks all `8 × C(15,11)` windows on
  planted `C5/C7` controls against the cycle-first generator (387 qualifying
  rows). The replay's optimized `e=87` branch is also tested against its
  direct 11-subset mode on the sampled `e=87` inputs.

| e | distinct anchors | windows before partition | partitions | complete extensions |
|---:|---:|---:|---:|---:|
| 85 | 4 | 10,162 | 0 | 0 |
| 86 | 92 | 3,075 | 0 | 0 |
| 87 | 1,374 | 42 | 0 | 0 |

The stratified pilot (all four e85, 12 e86, 17 e87) took 0.96 CPU s;
the partition-first baseline completed zero anchors before the hard CPU
limit (~85 CPU s), so it gave no useful throughput estimate. The full
cycle-first pass took 2.78 CPU s, and the independent pass 10.56 CPU s.
This is exhaustive `enum`, not an LRAT/DRAT certificate. Evidence:
`scratch/E/crown27.{manifest,full.log,replay.full.log,stratified.log}`,
`scratch/E/crown27.g6`, `scratch/E/cal_crown_v3.log`.

## Replay

From `scratch/E` (or a caller-selected work directory, with `ROOT` set
to the workspace and `r38_27.g6.gz` available there):

```sh
set -o pipefail
gzip -dc r38_27.g6.gz | "$ROOT/opt/bin/pickg" -q -e85:87 > crown27.g6
"$ROOT/opt/bin/shortg" -q -T"$PWD" crown27.g6 crown27.canon.g6
wc -l crown27.g6 crown27.canon.g6
for edges in 85 86 87; do "$ROOT/opt/bin/pickg" -q -e"$edges" crown27.g6 | wc -l; done
for code in crown_sieve replay_crown32_t1; do
  TMPDIR="$PWD" g++ -std=c++20 -O3 -march=native -Wall -Wextra -Werror \
     "$ROOT/ralph/lanes/E/$code.cc" -o "$code"
done
LIMIT="$ROOT/ralph/lanes/E/limited.sh"
nice -n 5 timeout 60 bash "$LIMIT" 40 python3 "$ROOT/ralph/lanes/E/calibrate_crown.py" ./crown_sieve
nice -n 5 timeout 120 bash "$LIMIT" 60 ./crown_sieve 32-1 < crown27.g6 > crown27.full.log 2>&1
nice -n 5 timeout 180 bash "$LIMIT" 90 ./replay_crown32_t1 < crown27.g6 > crown27.replay.full.log 2>&1
diff -u <(awk 'NF==9 {print $1,$2,$8,$9}' crown27.full.log) <(awk 'NF==4' crown27.replay.full.log)
```
