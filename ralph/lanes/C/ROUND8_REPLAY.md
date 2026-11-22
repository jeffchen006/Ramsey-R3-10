# Round 8 replay: P3 zero patterns and a bounded P2 index

Case R remains **open**. This bundle does not change the earlier P2
`(12,12)` certificate or the `(12,14)` K12 bound `16..21` (C-024/025).
Both predecessor SHA-256 manifests independently passed from the root.

## P3: exact boundary and zero-pattern scope

`proofs/p3_singleton_budget.md` gives the hand derivation. By the checked
C-021 diagonal-four cap, `e(X)<=63`. Both arms are pinned to eight;
the C high-arm index gives exactly four admissible boundary layouts
at e62 and five at e63. It has none at e61. Each row of the 191-graph
census is checked against its digest, triangle-freeness and alpha≤6.
The scout's two layouts bind 30+60 residue rows; omission of the fourth
blocker leaves 68 uncovered singleton masks in each layout. The two
independent boundary graphs and the planted C21 controls agree with
the existing constructors. This is **hand + enum**, not LRAT.

The zero multiset precheck examines 306 keys, with 105 satisfying the
eight-set avoider caps and exact forced-edge tests. 34 (including all
9 with q=0 and all 20 q=1 keys of the two q=2-only layouts) have exact
integer incompatibility witnesses. The only two fully excluded layouts
are still the scout layouts. There are 71 uncut zero patterns:

| e(X) | Matrix and holes (colon key) | Exact upper bound on q | Still live by q |
|---:|---|---:|---|
| 62 | `1:0:0:0:1` | 1 | 3 at 1 |
| 62 | `1:0:1:0:1` | 0 | none |
| 62 | `1:0:1:1:0` | 2 | 18 at 2 |
| 62 | `1:0:1:1:1` | 1 | 1 at 1 |
| 63 | `3:0:1:0:0` | 2 | 6 at 1, 9 at 2 |
| 63 | `3:0:1:0:1` | 0 | none |
| 63 | `3:0:1:2:0` | 2 | 18 at 2 |
| 63 | `3:0:1:2:1` | 1 | 1 at 1 |
| 63 | `10:0:1:0:1` | 2 | 10 at 1, 5 at 2 |

The independent fixed-X placement pass combines each residual pattern
with each compatible residue, checks degrees and any pair edge or
codegree constraint, and binds the counts to the exact row IDs/digests.
`zero-residue-bindings.tsv` has 420 rows, of which exactly the 90 scout
rows have no placements. On the residual rows there are 3,333 live
pattern/row keys with 212,200 labelled placements. None is a completion
count. Scout replay with zero counters and per-tag compatibility took
2.81 CPU-s; conditional discovery/replay took 28.80/14.29 CPU-s;
residue binding took 14.17 CPU-s. The conditioned LP is only a discovery
tool; the replay consumes small integer weights and rejects a bad
witness. No negative inference from an unproved row's LP status.

```sh
cd scratch/C/r8
ulimit -v 16777216
lane=../../../ralph/lanes/C
py=../../../opt/venv/bin/python
census=../../../gluing/val/r3_7_22.g6
nice -n 5 timeout 50 "$py" -B "$lane/p3_singleton_cover.py" "$census" \
  local-scout.tsv --verify capacity.json --tagged
cmp local-scout.tsv singleton-bindings.tsv
nice -n 5 timeout 60 "$py" -B "$lane/p3_zero_conditioned.py" zero-all.json
nice -n 5 timeout 60 "$py" -B "$lane/p3_zero_residue.py" "$census" \
  zero-all.json local-residue.tsv
cmp local-residue.tsv zero-residue-bindings.tsv
```

## P2: indexed requests on three held-out profiles

To separate cache reuse from a stronger mathematical filter, this
pilot packs the *existing* two-site request into a raw tuple. The key
contains the two opposite vertices' exact degree deficits, exact common
support subsets before mapping, exact numbers of incident wing rows,
the number of distinct wing rows meeting the pair, and whether the
pair is adjacent. The left cache is private to a fixed marked window
and wing pack. For that key and a **single shared** six-column map it
evaluates nonemptiness of both neighbourhood lists and the existing
pair-support predicate (see `proofs/p2_simultaneous_incidence.md`). The
map changes both common support masks simultaneously. The exact union
of incident wing rows is calculated from the same opposite wing pack,
not from independent choices of rows or a sum of incident counts.

The 720 six-column permutations have fixed lexicographic IDs. Start
from the IDs admitted by the unchanged token and column tests. For
each left-pack/right-pack pair, intersect this bitmap with the memoized
accepting IDs for each chosen two-site query. Unseen IDs are evaluated
on demand, not silently deleted. With at most 91 site pairs this is
exact for the pre-arc singleton/pair conjunction on the relevant
side, apart from duplicate predicate keys, which are idempotent. The
survivors still run the original complete left/right arc checks and
keep deferrals. It does not index arc consistency itself or enforce a
single choice across three predicates in the preliminary intersection.

Calibrated on all seven planted C22 full-wing pairs: identity passes,
the impossible degree mutation fails, and every examined alternative
permutation agrees with the direct request on both supports; smaller
negative prior controls still pass. In the held-out audit, all
4,910,040 mapped requests verify every column image in the bitmap and
every retained/deleted predicate against the mapped computation;
every bitmap deletion gives a direct baseline rejection. Each
unpruned/deferred map then uses original code. Baseline and the index
give identical pass/defer outputs (all empty, for these samples only).

| Profile | Mapped requests | 91-query bitmap deletions | Baseline CPU-s | Indexed CPU-s |
|---|---:|---:|---:|---:|
| `19,3,3,3,3,3,3` | 1,829,520 | 1,779,795 | 2.955 | 1.625 |
| `18,3,3,3,3,3,4` | 2,288,520 | 2,243,003 | 5.431 | 4.004 |
| `18,3,3,3,3,3,3` | 792,000 | 769,184 | 1.485 | 0.924 |
| Total | 4,910,040 | 4,791,982 | 9.871 | 6.552 |

This is **enum/estimate** evidence only: 97.6% preliminary attrition
but only **1.51×** net throughput, including input/bitmap construction.
The 12-query alternative pruned fewer and was slower in aggregate.
The 91-query index is not a cost-changing route at this rate; do not
scale to the outstanding 368.85B maps. No profile exclusions were
added, and no jobs were launched on full buckets.

```sh
cd scratch/C/r8
ulimit -v 16777216
lane=../../../ralph/lanes/C
sed 's/^int main(/int window_join_main(/' "$lane/p2_window_join.cpp" >p2_window_join_r7.inc
nice -n 5 timeout 10 python3 -B "$lane/p2_prejoin_build.py" .
TMPDIR="$PWD" nice -n 5 timeout 90 g++ -std=c++20 -O3 -Wall -Wextra -I. -I"$lane" \
  p2_prejoin.generated.cpp -o local-prejoin
nice -n 5 timeout 30 ./local-prejoin control ../../../duo/reg6_22.g6
awk 'NR%257==2' ../p2r7-census/h19-full-canon.g6 >local19.g6
awk 'NR%103==2 && NR%101!=1' ../p2r5-strong21.tsv >local21.tsv
cmp local19.g6 heldout19.g6; cmp local21.tsv heldout21.tsv
for row in '19,3,3,3,3,3,3 1829520' '18,3,3,3,3,3,4 2288520' '18,3,3,3,3,3,3 792000'; do
  read -r profile count <<<"$row"
  nice -n 5 timeout 70 ./local-prejoin cover local19.g6 local21.tsv direct.tsv "$count" "$profile"
  nice -n 5 timeout 70 ./local-prejoin idx-audit local19.g6 local21.tsv indexed.tsv "$count" "$profile" 91
  cmp direct.tsv indexed.tsv
done
```
