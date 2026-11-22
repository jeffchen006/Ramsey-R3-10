# P7 root cover and the global-L=7 exclusion (`hand + enum`, pending review)

In a 9-regular R(3) graph an edge kernel is bipartite of maximum degree
two. We count path **vertices**. The six-vertex stratum is handled in
`GRAFT.md`. This file assumes only that an induced P7 exists for its
unrestricted boundary cover; its search additionally assumes that no
kernel has a simple P8. It **does not** assume a forest, no C6, q*=12/13,
the three former L=6 keys, or the nineteen L=6 projected refutations.

## Unrestricted boundary

Use core labels `0,1` for the edge, `2..8` for a seven-vertex kernel path;
even path positions lie in N(0), odd ones in N(1). Endpoints are on the
same side; this path is induced even when other kernel components are
cycles. `long_root.py` takes **all 2434** earlier P6 profile representatives,
both orientations. Drop either endpoint to obtain an eight-star P6 core.
Remove the other endpoint's known occurrence from its exterior multiset;
the two halves agree on the remaining seven shared stars. In each shared
cell of size b, the two extra endpoints have fixed marginal counts p,q.
Their overlap ranges from max(0,p+q-b) to min(p,q), jointly constrained
by the endpoint-pair codegree cap. The four cell sizes then follow. No
independent-set or path-length cutoff is used in this join. This covers
all physical P7 roots; the only symmetry used is reversal of the path.
The choice of which root sees the endpoints is intrinsic.

- 75 shared buckets on each side; 170,544 pairs of half profiles.
- 484,288 labelled nine-star multisets; **243,175** reversal orbits.
- Independent check `long_direct.cpp` enumerates independent masks directly
  from the 9-by-9 core, remaining degrees, pair rooms and 31 exterior slots
  (11 units of pair slack). No eight-star source or gluing. Both full
  canonical files agree after byte sorting. The direct search is faster:
  ~1.6 vs 20.0 CPU-s including output.
- Seen on all 155 physical cap-three C22 P7 marks, 12 real profile orbits.
  The smaller *planted* P6 library is deliberately not an unrestricted
  smaller source: its join yields 40 candidates, not the full C22 incidence
  count. The exact C22 completed-graph control below is a separate test.

## Search, under the global maximum of seven

`long_filter.cpp` maintains a mandatory lower graph and possible upper graph.
Remove optional edges creating a triangle, a fourth common neighbor, or an
oversaturated degree. If a vertex has precisely nine possible neighbors,
force them all. A forced nonedge needs a common neighbor; force a unique
possible witness. A ten-set independent even in the upper graph is fatal.
In the seven-cap pass, an arc is impossible if its addition gives a
kernel component of size >=8 (every extendible partial kernel is a union
of paths/cycles). Conversely, for possible edge xy, if eight further
vertices are upper-independent and have no possible adjacency to either x
or y, xy must be present. Iterate to stability. No assumption that an
eight-vertex path is induced; both paths and C8s violate **this** cap.

`long_search.cpp` starts from complete stars. A free row is enumerated up to
permutations within equal masks on **explicitly frozen stars**. Choose a
pivot, keep lower-graph forced neighbors, and choose initial segments of
the remaining available members of each cell; include the pivot's full row
and recurse. The unknown subgraph is never pinned by a symmetry from the
decorated-panel pilot. Implied arcs are recalculated from the explicit
frozen state on each call. For a candidate row, codegrees versus the frozen
stars and degree nine are necessary. On reaching a node budget the input
is returned **open**, not exhausted.

Later passes may use only the *complete* library of still-open P7 profiles
from the previous pass, in both orientations. For each P7 in the lower
graph, the exterior multiset on its fully known stars must project from a
library entry. A 64-bit additive hash implements lookup: collisions can
only **add** candidate entries; rejection on a missing hash is safe. A
known full-star fingerprint is based on a mandatory vertex of degree nine.
The stronger mode also checks the simultaneous lower/upper 9-bit mask
domains against the complete list of exterior slots for each candidate.
Find a perfect matching. A slot edge is supported if its contracted
alternating arc belongs to a directed cycle (including an assigned loop).
Across **all** candidate profiles/matchings take the union of possible
bits and intersection of necessary bits, then rerun propagation. This
enforces multiple exterior rows jointly without trusting one matching.
The stronger mode is `4`; no small-Ramsey subproblem bounds are needed
in the terminal seven-cap chain.

| Stage | Rows | Exhausted at this stage | Unresolved | Search nodes | Solver CPU-s |
|---|---:|---:|---:|---:|---:|
| General lower/upper screen + required path length <=7 | 243,175 | 238,044 | 5,131 | — | 8.8 |
| Seven-cap arc and forced independent-set edges | 5,131 | 2,903 | 2,228 | — | 3.7 |
| 500 nodes, no reroot library | 2,228 | 2,121 | 107 | 98,181 | 74.3 |
| 5,000 nodes, library of 107 | 107 | 77 | 30 | 248,217 | 183.4 |
| 30,000 nodes, supported matching with library of 30 | 30 | 27 | 3 | 231,398 | 108.4 |
| 250,000 nodes, supported matching with library of 3 | 3 | 3 | **0** | 51,384 | 23.4 |

The final three took 17,120, 1, and 34,263 nodes. They are **not** the
earlier L=6 keys. No cap is used as a terminal exclusion. Across the raw
boundary, 168,540 survive the general test if the seven-cap is *not*
imposed; all direct remaining L>=8 work is separate.

## Calibration, receipts and trust boundary

`long_exact_control.py` compares exhaustive C++ completions against actual
individualized-core nauty certificates independently extracted from all
191 C22 classes, from which there are three cap-three regular graphs.
Every one of the 12 colored P7 representatives is recovered and no other
graph is returned. Repeated with four modes, including the final matching
rule. A deliberately empty library rejects all 12. The computed profiles
and witnesses are an enumerative result, **not a Section 7 certificate**.

In `scratch/D/joint9/`, `seven/terminal.tsv` gives one first terminal reason
per original representative, its line hash, exact chunk and ordinal. Rebuild
that join and verify sizes, order, budget and cut counts with
`round9_receipts.py .`. General and arc filters use `long_filter 40 9` and
`long_filter 40 9 7` respectively. Compile C++ with `g++ -O3 -std=c++17`.
Replay search stages with these arguments to `long_search`, on the indicated
`.in` files (paths relative to `scratch/D/joint9`):

```
40 9 7 500                             # seven/s??.in
40 9 7 5000 seven/overlap.tsv          # seven/level2/t??.in
40 9 7 30000 seven/level2/residue.tsv 4 # seven/level3/u??.in
40 9 7 250000 seven/level3/residue.tsv 4 # seven/level4/v??.in
```

`overlap.tsv` equals the 107 node-caps; the prospective fixed-point
signature filter deleted **none** on its own. The aggregate reported
search work is 389.4 CPU-s, excluding controls, pilots, replay and
counting. Compare receipt statuses/node counts/histograms, not timings;
the code gained a final histogram bin after level 1 (zero in its replay).

Combined with the lower-length strata, every remaining R(3) graph would
have a **simple P8**, which can be an induced P8 or can close to a C8
component. That distinction matters. Neither R(3) nor R(3,10) closes.
