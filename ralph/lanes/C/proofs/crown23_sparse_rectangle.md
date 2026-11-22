# Sparse attachment rectangles in the saturated eight-edge crown

**Scope (`hand`, pending review).** Use lane E's saturated
`(p,f,t)=(2,32,4)`, `δ(W)≥2`, `e(W)=8`, `P=0` branch and its
underlying degree result: four disjoint independent six-sets `A_i`,
`F=W⊔A_0⊔A_1⊔A_2⊔A_3` with `|W|=8`, and every attachment
vertex has fixed degree seven. Every card `F−A_i` is triangle-free
with independence number at most seven: its independent sets can
add the two nonadjacent moved vertices aligned with `A_i`. Neither
the e74 catalogue nor the identity or uniqueness of a missing class
is used. For every distinct `i,j` there are at least six edges
between `A_i,A_j`, and exactly six forces a perfect matching. For
the shared part of their cards, `e(X)≥38`; equality requires the
stitched rectangle to be `6K2`.

## Consequences of the card cap

Fix `L=A_i`, `R=A_j`, `X=F−(L∪R)` (20 physical sites), and let
`B=F[L∪R]`. It is bipartite with shores `L,R`. Every `B` vertex
`u` has `d_X(u)=7−d_B(u)`. The two following conditions are necessary.

1. `α(B)≤7` and `α(B−N_F(v))≤6` for each `v∈X`. The first is
   restriction from either card omitting one of the two retained
   roles. The second follows because any independent seven avoiding
   `v`'s neighbors could add `v`. The resulting eight fits a card:
   `v` belongs to at most one of the two retained groups, and if
   `v∈W` it belongs to neither. Thus for every `v∈X`, `N_F(v)∩V(B)`
   meets **every** maximum independent set of `B` when `α(B)=7`.
   This neighborhood is itself independent by triangle-freeness.
2. If `x∈L` has `d_B(x)=0`, its seven neighbors in `X` form an
   independent seven. Every `y∈R` must have a neighbor in that
   seven, since `X∪R=F−L` is one of the cards. In particular, for
   isolates on opposite shores the two degree-seven neighborhoods
   in `X` must intersect, so their union has size at most 13.

The argument for (2) uses the actual physical independent set
`N_X(x)`, not its image under an unmarked isomorphism. It holds for
all rectangle sizes and is also a sign/degree test on the stitched
input whenever `d_B(x)=0` is prescribed by the card degree.

## Sparse rectangles

By the bipartite matching/vertex-cover equality, `B` has a matching
of size at least `12−7=5`. If `e(B)=5`, it is `5K2` and has two
isolates, `x∈L,y∈R`. Each `v∈X` missing both isolates can pick
one nonneighbor from each edge (it cannot see both ends of an edge
in a triangle-free graph). Together with the isolates this is an
independent seven missing `N_F(v)`, contradicting (1). Therefore
the two isolates would have to dominate all 20 overlap vertices,
but they have at most 14 overlap neighbors in total. Fewer than
five edges is already excluded by the matching bound.

Suppose `e(B)=6` but it has no perfect matching. Start from a
size-five matching. There are exactly two unmatched sites, one on
each shore, and there is a single extra edge. It cannot join the
two unmatched sites, which would give a perfect matching, and it
cannot repeat a matched edge. There are precisely two remaining
possibilities, by which matching components the extra edge joins.

* **`P3 + 4K2 + K1`.** The extra edge joins an unmatched site to
  a matched site. The independent seven-sets consist of both
  endpoints of `P3`, the remaining isolate and one endpoint of
  each `K2`. If `v∈X` misses the two `P3` ends and the isolate, it
  can choose a nonneighbor from each of the four edges, as above.
  Thus those three distinguished vertices must dominate `X`. Their
  overlap degrees are `6,6,7`, with total 19, less than 20.
* **`P4 + 3K2 + 2K1`.** The extra edge joins two matched edges.
  The independent seven-sets choose both isolates, one from each
  `K2`, and an independent pair in `P4`. A vertex of `X` that misses
  the two isolates can avoid all such choices only if it sees an
  independent hitting set for the independent pairs of `P4`. With
  the path ordered `0,1,2,3`, those pairs are `{0,2}`, `{0,3}`,
  `{1,3}`. The only independent hitting set is `{0,3}`: the other
  two independent pairs are disjoint from each other and no single
  vertex hits all three. Thus each overlap vertex either sees an
  isolate or sees **both** ends of the path. The opposite-shore
  isolates have at most 13 different overlap neighbors by (2).
  The path ends each have overlap degree six, so at most six
  overlap vertices see both. The union accounts for at most 19
  vertices, again less than 20.

This eliminates both six-edge non-perfect patterns. With a perfect
matching and only six edges, all edges belong to that matching.
The identity `e(X)=32+e(B)` follows by deleting the opposite
independent six-set from either 74-edge card: its total fixed degree
is 42 and `e(B)` incidences were already omitted with the first set.
This bound excludes rectangles, not the whole eight-edge core or
an involution class. It is applicable to **any** omitted-role pair,
even when neither window is known to be the missing class.

## Profile-dependent bound for the overlap key

Write `e_{uv}=e_F(A_u,A_v)` and `b_u=e_F(W,A_u)`. For complementary
role pairs `{i,j}` and `{k,l}`, summing the degrees of the 12
attachment vertices in each pair yields

```
84 = (b_i+b_j) + 2 e_ij + e_F(A_i∪A_j,A_k∪A_l),
84 = (b_k+b_l) + 2 e_kl + e_F(A_i∪A_j,A_k∪A_l).
```

The cross term is the same. Also `Σ_u b_u = 8·8−2·8 = 48`, using
the saturated fixed degree of the eight W vertices and its eight
edges. Subtracting yields `e_ij = e_kl + 24 − (b_i+b_j)`. Thus when
`b_i,b_j≤12`, the shared part of the corresponding missing windows
satisfies the stronger lower bound

```
e(X) ≥ 62 − (b_i+b_j).
```

If it has equality, the **retained** rectangle `A_k×A_l`, already
known once those marks are given in the overlap, has exactly six
edges and must be a perfect matching. For example `(10,10)` omissions
require at least 42 overlap edges; at 42 the retained rectangle is
`6K2`. None of this requires the retained-role cards to be missing.

## Three forbidden seven-edge patterns

The same argument also forbids the following specific shapes with
seven edges. It does **not** require a perfect matching for every
seven-edge rectangle.

* **`C4 + 3K2 + 2K1`.** A maximum independent set consists of an
  opposite pair of the cycle, one endpoint from every edge, and
  both isolates. An independent set in the cycle lies in one shore,
  so an overlap site can always avoid its own cycle neighbors in
  one of the two opposite pairs. It must therefore see an isolate.
  The union of the isolates' overlap neighborhoods is at most 13.
* **The tree with arm lengths `(1,2,2)`, plus `2K2 + 2K1`.** Denote
  the center by `c`, the short arm by `c-a`, and the long arms by
  `c-b-d,c-e-f`. The tree's maximum independent sets are
  `{c,d,f}` or `{a}` plus one end of each edge `b-d,e-f`. An
  overlap site missing both isolates must see `a`: otherwise it
  can avoid its neighbors in the latter type and choose one
  nonneighbor from each isolated edge. This uses the fact that
  its neighborhood cannot meet both ends of an edge. There are
  at most `13+6=19` sites seeing an isolate or the leaf `a`.
* **The tree with arm lengths `(1,1,2)`, plus `3K2 + K1`.** With
  center `c` and arms `c-a,c-b,c-d-e`, its maximum independent
  sets are `{a,b,d}` and `{a,b,e}`. An overlap site missing
  `a,b` and the isolate can avoid its neighbors in one of those
  triples and one end of each independent edge. The two indicated
  leaves and the isolate have total overlap degrees `6+6+7=19`.

In each case the full maximum independent set has size seven,
so the overlap coverage is required by (1). The two-isolate cases
have isolates on opposite shores: if both were on one shore there
could be no matching of size five, contrary to `α(B)≤7`.
