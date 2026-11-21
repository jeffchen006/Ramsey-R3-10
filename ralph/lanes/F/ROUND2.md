# Lane F, round 2 evidence

No `(3,10,40)` graph was found. Counts below refer to actual checkpoints
or to explicitly bounded local neighborhoods, never an automorphism family.
All run logs, input graph6 controls and outputs are in `scratch/F/r2/`,
except the carried-over `scratch/F/r1/` files named in `STATE.md`.

## Exact 39-vertex component and attachment scores

For any `(3,10,39)` graph `G`, replacing the neighborhood of `v` by `S`
preserves validity iff `S` is independent in `G-v` and hits all its
independent 9-sets. The converse move replaces `S` by the old neighborhood,
so this relation, on isomorphism classes, is symmetric. `k39_exact` covers
all possible hits by first-present selection in an uncovered 9-set, then
enumerating all independent extensions of the hit at each accepting leaf.
One representative per automorphism orbit of `v` suffices after nauty
canonicalization. `k39.patch` compares the complete canonical graph6 in
the hash table. The same hit test, without deleting a vertex, decides
whether a one-vertex extension exists.

The initial and fresh single-seed runs both drained their queue with
28,113 exact canonical forms, below their respective caps of 120,000 and
110,000. Ordered graph6 catalogues are byte-identical. The result indices
are consecutive `0..28112`; extension flags are all zero. A separate
`opt/bin/labelg` pass again yields 28,113 distinct classes and no Exoo
class in the catalogue (`closure39.audit`). Thus this is a different
rewire component from Exoo's. This is not an independent implementation
of rewire coverage, nor evidence of novelty versus the older 33 other
components whose graph files are unavailable. Label: `enum`.

`attach_score.cpp` is an independent, exact scorer of triangle-free
one-vertex attachments with degree window `[lo,k-1]`. Let `A` be the old
vertices below cap, and `R` the vertices at degree `lo-1`. A feasible
neighborhood must contain `R`, be independent, and be contained in `A`.
After rejecting incompatible `R`, freeze it and enumerate maximal
independent subsets of `A-(R union N(R))` by pivoted Bron–Kerbosch in
the complement. Maximizing hits is monotone, and every independent
subset of the original base has size at most `k-1`, so extending a feasible
set to a maximal one cannot break the upper cap for the new vertex.
Old bad sets containing `R` are already hit; project remaining independent
`(k-1)`-sets to admissible optional vertices, preserving multiplicities.
Their misses are exactly the new graph's `I_k`. Empty projections give
an unavoidable lower bound. With `verify`, a separate recursion over all
independent subsets checks the optimum per base, not just its witness.

- Positive controls: `C35-v` and the lane's random 39 witness minus its
  last vertex both reach zero and pass the gate (`attachctl{35,39}.gate`).
  Full `C35` cannot accept any new neighbor without exceeding degree 8.
- 384-input timing pilot: 0.15 CPU s; the 28,113-input full scan took
  25.92 CPU s with `verify`. In `[5,9]`, 26,603 bases admit at least one
  degree-valid attachment. Minimum `I10=142` at `idx=27717`, 178 edges,
  min/max degree 8/9. Direct recount: `attachbest.audit.jsonl`.

## Symmetric moves and pinned repair

`-symexchange` samples one or two present pair orbits and substitutes the
same number of absent orbits with the identical degree increment vector.
An orbit's increments are constant on each vertex cycle; the lookup key
packs at most four nonzero cycle indices and loads. Triangle checks use one
representative per added orbit *after* all trial edits. All remaining
triangles would already have existed in the input. `-symverify` compares
the degree vector and the old sequential independent-set count.

`-symstar`, `-symstar2`, and `-symstar2flex` hold the outside induced graph
fixed and reattach respectively one or two nontrivial vertex cycles. For
each outside vertex cycle, enumerate all crossing orbit subsets giving it
its required load; the selected cycles must meet their residual per-vertex
degree demands. Exact suffix bounds prune loads. The first two modes fix
the internal graph of the selected cycles; the last enumerates every
internal orbit pattern, with adjusted demands. Edge addition is monotone
for triangle creation, allowing early triangle pruning. For every legal
leaf and each orbit of internally independent subsets `S`, count
independent sets of size `k-|S|` in the outside common nonneighbors of
`S`, and multiply by the subset-orbit size. Also include sets missing
the selected cycles. Counts memoize `(size, outside mask)`; with
`-symverify`, each scored leaf is checked with a full recount. The minimum
can be short-circuited at zero; a timeout or `status=partial` never implies
neighborhood exhaustion. With no improvement on a complete pass, the
original seed is a local minimum for that move type and tested domain.
`-syma-max 4` filters the order-three fixed attachment count where used.

| Method | Positive controls | Target observations |
|---|---|---|
| balanced swaps | gate n35 and n39 recover from I9=1400 / I10=97 | 1,280,904 legal trial moves across `(3,10)` and `(5,0)`; neither improves in 128.31 CPU s |
| one star | gate n35 and n38 recover from I9=1885 / I10=96 | all windows complete for four seeds, no improvement |
| two stars, fixed interior | n38 control starts at I10=2, single star exhausts with I10=2, two stars hit zero; n35 also gated | five full sweeps (28/45/45/190/190 windows), 410,658 legal leaves total, no improvement |
| two stars, flexible interior | n38 starts at I10=50, fixed-interior sweeps finish at 14, flexible reaches zero; n35 also gated | `(3,10)` 45/45 and free involution 190/190 complete; `(5,0)` 8/28 and free order 4 27/45 complete plus a partial window each; no gain |
| four-hole SAT | both n35 and n39 planted repairs pass gate | exact cover count on I10=44 seed: no transversal of size <=3, ten of size 4; all ten failed SAT/prefilters in 11.59 CPU s, no proof logs |

Exact fixed-interior two-star legal-leaf counts: 133,920 at `(5,0)`,
8,928 at `(3,10)`, 217,232 at order 4, and 14,304 / 36,274 for the free
involution seeds (one inherited from order 4). Flexible mode at `(3,10)`
visits 1,091,810 nodes, 24,408 legal leaves, in 0.42 CPU s; free involution
5,435,962 nodes, 39,232 legal leaves, in 1.01 CPU s. Flexible `(5,0)` and
order 4 each received 101 wall seconds (75.82 and 78.67 CPU s), leaving
unvisited windows. Do not rescale unchanged starts without a new way to
escape the local minimum.

For four-hole repair, every successful edit touching at most four chosen
vertices has a size-four bad-set transversal (pad if smaller); the graph
outside it is fixed. `repair2.py --holes 4` enumerates these transversals
and uses the same exact extension CNF as in round 1. Thus the negative
result is for that single seed's whole four-vertex repair neighborhood,
not a reduction of the general symmetry case. Label: `enum`.

`-record-min-degree 5` captures accepted/restart checkpoints with degree
range `[5,softcap]` and no triangles, ranked by raw I10 independently of
weighted best. It agrees with the gate on n38. On `(3,4)` it recorded a
9-regular I10=293 even while the weighted best checkpoint was degree-10.

## Rebuild and launch

From the workspace root (all file outputs go under lane scratch):

```sh
mkdir -p scratch/F/build
cp anneal/ls.cpp scratch/F/build/exchange.cpp
patch scratch/F/build/exchange.cpp < ralph/lanes/F/sym.patch
patch scratch/F/build/exchange.cpp < ralph/lanes/F/exchange.patch
g++ -O3 -march=native -std=c++17 -I ralph/lanes/F scratch/F/build/exchange.cpp -o scratch/F/build/ls_exchange
g++ -O3 -march=native -std=c++20 ralph/lanes/F/attach_score.cpp -o scratch/F/build/attach_score
```

`launch.sh` records every command in `STATE.md` under the same flock used
for the slot check. The scratch register binds timeout supervisor PID,
boot ID and `/proc/PID/stat` creation ticks. Present but unreadable
registered identities are counted conservatively; timeout commands carry
a `lane-F:` tag for fallback accounting. Round-1 unmarked supervisors
were checked dead before migration. `scratch/F/concurrency.log` shows the
count immediately before every launch. Set `F_ROUND=r3` and create the
working directory before future launches. `run40.sh` uses `F_LS` when
supplied and gate-checks any target graph before publishing it.
