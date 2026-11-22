# Physical two-window overlap, complementary degrees, and cross factors

## Scope and notation

In lane E's saturated four-pair crown, `F` consists of `W` and four
disjoint independent attachment groups `A_0,…,A_3`. When `e(W)=8`
and `P=0` in E's setup, `|W|=8`, `|A_i|=6`, and the prescribed
fixed degrees `D` are 8 on `W` and 7 elsewhere. Choose two distinct
omitted roles `i,j` whose cards are forced to be missing by E's
argument. Use actual marked copies of the same missing class if its
uniqueness is assumed; no statement here identifies its graph or
assumes that the other two cards are missing. For each unordered pair
of eligible omitted roles retain at least one orientation, or retain
both orientations and charge duplicates. Relabeling must preserve
physical incidence and membership, not the coordinates used by a
particular graph6 representative.

Write `L=A_i`, `R=A_j` and `X=F−(L∪R)`. Then `H_i=F−L=X∪R`
and `H_j=F−R=X∪L`. A marked join fuses the two restrictions to `X`
along one **induced** graph isomorphism carrying the supplied `W`
mark and the retained named groups to their respective marks. If a
projection has no separate retained group marks, preserve just the
available marks and defer restoration of the other marks. In this
physical union the two omitted groups are distinct sets even if their
coordinates in the two copies of the missing class happen to agree.
Every pair in `F` except `L×R` is prescribed by a card. Both signs on
`X` must agree. Conversely the restrictions of any real target furnish
one such alignment. No automorphism of the full card or of `F` is
assumed to extend the chosen isomorphism of `X`.

## Color the shared part before joining

For `v∈X`, the degree forced in `F` by the two cards is

```
d_Hi(v) + d_Hj(v) − d_X(v) = D(v).
```

This is inclusion-exclusion on the **actual** neighbor sets in the two
cards: their intersection is exactly `N_X(v)`. All remaining unknown
edges lie outside `X`. Hence the test can be built into an induced
isomorphism key: alongside each mark color and `d_X`, color `v` in
`H_i|X` by `d_Hi(v)`, and color a prospective image `u` in `H_j|X`
by `D(u)+d_X(u)−d_Hj(u)`. An isomorphism of these colored graphs
is exactly an uncolored marked isomorphism of `X` satisfying the
shared degrees. Compare the multisets of colors first. This is a
complementary key, **not** the requirement that the two visible card
degrees be equal. The two private incidence systems are carried along
separately, regardless of whether the colored `X` has automorphisms.

For `w∈W` in the `e(W)=8` setting, every group has a `w` contact and
`d_W(w)=2`. Its four group sizes total six. In particular
`4≤d_X(w)≤6`, and the two omitted contacts sum to `8−d_X(w)`;
they are not independent selections. If `e_{ij}=e_F(L,R)`, summing
degrees on either independent omitted six-set gives `42−e_{ij}`
edges from that set into `X`, so `e(X)=32+e_{ij}`. Neither scalar check
replaces the vertex-by-vertex equation.

## The unknown rectangle is an exact degree factor

First require that both cards are triangle-free; then their physical
union, with no `L×R` edges, is also triangle-free because every
triangle not using that rectangle would lie in a card. For `x∈L` and
`y∈R`, the edge `xy` is allowed exactly when
`N_X(x)∩N_X(y)=∅`. Its demand at `x` is `r(x)=D(x)−d_Hj(x)`
and at `y` it is `r(y)=D(y)−d_Hi(y)`. No triangle can contain two
new rectangle edges: their third side would be internal to one of
the independent omitted groups. Thus after the shared degree check,
completing to a triangle-free fixed graph of the prescribed degrees
is **equivalent** to choosing a spanning bipartite subgraph of the
allowed rectangle with degrees `r`. This equivalence does not yet
impose any independence bound.

Reject negative demands or unequal shore sums. For each `S⊆L`,
the generalized Hall condition is

```
sum_{x∈S} r(x) ≤ sum_{y∈R} min(r(y), |N_allowed(y)∩S|).
```

Necessity follows by counting the factor edges incident to `S`.
For sufficiency, form the flow network from the source to `L` with
capacities `r(x)`, from `L` to `R` with unit capacities on allowed
pairs, and from `R` to the sink with capacities `r(y)`. At a cut
whose source side in `L` is `S`, the minimum choice of which `y` to
include charges exactly `min(r(y),|N_allowed(y)∩S|)` for each `y`.
All source-left edges to `L−S` are also charged. Thus the inequality
for every `S` is exactly the assertion that no cut has capacity less
than the common shore sum. Integral maximum flow gives the desired
factor; its selected unit arcs give the rectangle edges. This takes
only 64 subsets when the omitted groups have size six. A failed `S`
is a small independently checkable receipt giving the exact demand
and capacity, rather than a comparison of separate row minima.

## Exact independence obligation after alignment

For any independent set `I⊆F`, let `s` be the number of distinct
attachment groups it meets. One shore of the four-pair crown can add
`4−s` uncovered moved vertices. An independent set of moved vertices
using both shores is contained in a single aligned pair (all other
cross-shore pairs are edges), so if `s≤3` it can add two, and if
`s=4` it can add none. Therefore the maximum number that can be added
is `max(4−s,2)` for `s≤3`, or 0 for `s=4`. For `alpha(G)≤9` the exact
fixed-set caps for `s=0,1,2,3,4` are `5,6,7,7,9` respectively.

For any violating set in the graph of prescribed **present** edges
(regardless of prescribed absences), forbid it by requiring at least
one selected factor edge in `(I∩L)×(I∩R)`. This is an empty clause if
no such edge is allowed. It suffices to generate independent sets of
sizes 6, 7, 8, 10, respectively with at most 0, 1, 3, 4 touched groups:
every larger witness contains a same-size subset meeting at most as
many groups. The 6-set test is trivial in the present core, but the
`s=3` case of the 8-set test is essential. Any witness not meeting
both tails can instead be tested in its complete card, once per mark.

One can obtain a necessary upper-graph test without enumerating
completions. For each allowed edge `xy`, ask whether a factor can
contain it: decrement both demands, remove that edge from the
residual rectangle, and recheck Hall. The supported edges are exactly
the union of the factor edge sets. A violating independent set in
the graph with all supported edges present stays independent in
every factor. Passing this test does not mean that one factor hits
all of the independence clauses at once. Testing two particular
clauses jointly is also exact as a local rejection: try each
supported edge in the first clause, pin it and check whether the
second has a supported edge under that pin (or was hit already).

There is a larger but still joint test on any fixed shared independent
set `U⊆X`. Take a set of roles `T` containing every attachment role
touched by `U`, and let `L_U,R_U` be the sites of `L,R` in roles of
`T` that miss **every** vertex of `U` (an excluded role gives the empty
set). For any factor, independence sets with this fixed shared part
are exactly `U` plus independent sets of its bipartite graph on
`L_U∪R_U`. By Kőnig's theorem that bipartite graph has independence
number `|L_U|+|R_U|−ν`, where `ν` is its maximum matching size: the
complement of an independent set is a vertex cover, so apply the
matching/vertex-cover equality. Writing `cap(T)` for the cap indexed
by `|T|`, the necessary constraint is consequently

```
ν ≥ |U| + |L_U| + |R_U| − cap(T).
```

All such constraints together are equivalent to the independence
obligation: any independent witness has some shared part and role
set tested here, and the cap list is nondecreasing with role count.
For a single such constraint, test whether **a factor can contain a
whole matching** of the required size in the scoped rectangle. For
each matching of that size, decrement the demands on its endpoints,
remove the pinned edges, and run the same Hall test. One success
passes precisely this single obligation. Its failure is sufficient
to reject the physical alignment. It can be stronger than measuring
matching in the union of the individually supported edges. For
example, let both shores be `0,1,2`, each demand one, with allowed
edges `(i,i)` and `(i,i+1 mod 3)`. Its two factors use only diagonal
or only shifted edges. On the rectangle `{0,1}×{0,2}` the union
contains the two disjoint edges `(0,0),(1,2)`, but no factor can
contain both. Passing different constraints with different factors
does not assert simultaneous completion. This implementation is
for selected constraints, not a priced exhaustive matching campaign.

Combining the factor demands with **all** the fixed-set clauses gives
exactly the extension obligation for this physical crown join. It is
not necessary to enumerate the W partitions again to use the factor
screen. In contrast the screen alone does not settle an unmarked case,
and enumerating marked pairs of the unknown missing class still
requires a separate coverage argument.
