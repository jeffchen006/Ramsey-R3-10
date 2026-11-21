# Exact degree-six residual floor (hand reduction, checked LRAT)

Let `G` be an MTF triangle-free 40-vertex graph with independence number at
most nine. Let `v` have degree six, `A=N(v)`, and `H=G-N[v]`. Then `H` has
33 vertices and no independent nine-set (adjoin `v` to one). By
Goedgebeur–Radziszowski (GR), *New Computational Upper Bounds for Ramsey
Numbers R(3,k)*, EJC 20(1), #P30 (2013), Tables 4 and 14, `e(H)>=118` and
the `e(H)=118` stratum has exactly five isomorphism classes. `root_certs/`
contains five valid nonisomorphic representatives. No previous gluing or
numerical LP filters are hypotheses of this result.

## Clauses that must hold

Triangle-freeness makes `A` independent and each attachment
`S_i=N(a_i)∩H` independent. Furthermore each `S_i` dominates `H`: for
`x∈H\S_i`, MTF gives a common neighbour of `a_i,x` and that neighbour must
be in `H` (not `v` or in `A`). Index the coordinates `b[i,x]` by the
membership `x∈S_i`. The generator `root_core.py` emits precisely:

1. For each edge `xy` of `H` and `i`, `¬b[i,x] ∨ ¬b[i,y]`.
2. For each `x,i`, one of `b[i,x]` and `b[i,y]` for `y∈N_H(x)` holds.
3. For each `x`, at least one `b[i,x]` holds (MTF for `v,x`), and at most
   `9-d_H(x)` hold (`N_G(x)` is independent). The upper bound forbids
   every subset of literals of size one greater than the cap.
4. For each nonedge `xy` without a common neighbour in `H`, at least one
   common neighbour is in `A`. A positive auxiliary `q_i` implies both
   `b[i,x]` and `b[i,y]`; a clause requires at least one `q_i`. An actual
   extension assigns each `q_i` to the conjunction, so no extension is
   lost. The clauses for different pairs use disjoint auxiliaries.

These are necessary, not a full equivalence to extending `H`. None fixes
`e(G)`, demands a degree floor for other vertices, nor lists independent
sets of size ten. All five necessary CNFs are UNSAT by checked LRAT (both
`lrat-check` and `cake_lpr`); hence **`e(H)>=119` at every degree-six root**.
The Python generator has no third-party dependency. Substitution of the
actual extension assignment validates every generated clause at every root
of C35, MTF-saturated Exoo39, and the ten 6-regular order-22 controls
(294 rooted positives).

## Distribution cuts

Recall `Z(v)=∑_{a∈A} d_G(a)=6+∑_i |S_i|` and `e(G)=e(H)+Z(v)`.
The existing MTF private-neighbour bound gives `Z(v)>=48`: vertices in a
private cell `S_i\⋃_{j≠i} S_j` are independent and augment `A\{a_i}`, so
each of the six cells has size at most four. Of 33 exterior vertices each
is hit, at most 24 only once, giving at least 42 hits. Thus `n6>0` implies
`e(G)>=167`; equivalently at fixed `e=166` the new row is `n6<=0`.
For a pinned distribution with `n6=q>0`, the exact integer Farkas
combination `1·(n6<=0)+1·(-n6<=-q)` gives `0<=-q`. There are 65 such
distributions in the original 524; two were already closed in round 1,
so 63 more are excluded. The row `e(H)>=119` also tightens the degree-six
profile filter `Z(v)<=e(G)-119` at larger `e`.

## Independent small check

For `e(G)=166`, the sum `∑|S_i|=42` at `e(H)=118`. Exact
Bron–Kerbosch search in the complements of the five graph6 inputs finds
minimum dominating-independent-set size 7, with respectively 25, 11, 17,
11, 25 sets of size 7. Thus every `S_i` has size 7. In every input some
`x∈H` belongs to **no** size-7 dominating independent set, violating MTF
for `v,x`. `check_root_cover.py` independently replays this argument and
passes the same 294 positive controls. At `e(G)=167`, exactly one `S_i`
may have size 8 when `e(H)=118`; the vertices omitted by all size-7 sets
include an edge in every input and therefore cannot all be covered by the
single independent attachment of size 8. At `e(H)=119` and `e(G)=167`, any
two nonadjacent exterior vertices with no common neighbour in `H` must
lie together in some size-7 attachment if the common minimum is 7.
Results for incomplete `e=119` lists are not a cover.
