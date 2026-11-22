# Integral signatures at the e170 equality boundary (hand)

Use the critic-confirmed MTF floor `e(H_v) >= 122` for every degree-six
root `v`. At `e(G)=170`, M2 gives `Z(v)>=48`, so both are equalities.
The signature lemma (`equality_private.md`) gives four private sites at
each of the six anchors and nine distinct double sites. The double
signature graph `J` has nine edges and `d_G(i)=5+d_J(i)` at each anchor.
G-019 applies to `H_v` at 122 edges: `d_H(w)>=6`. In particular an
exterior degree-seven site is private. G-021 makes all degree-six
vertices pairwise adjacent, so triangle-freeness gives at most two.
In the single-root case `d_J(i)` is between two and four. Enumerating
the nine-edge subgraphs of `K6` with that range and quotienting by S6
gives 2,800 labelled masks and 11 orbits. For each distribution the
degree inventory of the root and its anchors must fit. As a further
check on a residue, `d_H` is in `6..8`; if `h_i` counts those degrees
then `h_8=h_6+13` by the 33 vertices and degree sum 244.

## Adjacent equal roots

Put `U=N(u)-v`, `V=N(v)-u`, and `W=G-(N[u] union N[v])`.
In the residue at `u`, the vertices of `V` all attach to the anchor `v`;
exactly four have only that attachment. The fifth can attach to only
one more anchor, so there is exactly one `U`–`V` edge, say `xy`. The
private cells for anchors in `U` all lie in `W`, and eight distinct
double cells lie there too. Both sides have five private cells and
eight doubles in `W`, with 36 attachments each. Thus `|W|=28` and
`e(W)=170-11-1-72=86`. The single cross edge does not require a reused
e168 strip or hole classification. On a side, its two missing double
pairs in `K5` form a matching or a path of length two. The cross
endpoint belongs to a missing pair, since otherwise its degree would
be ten. Up to labels preserving that endpoint, the three possibilities
are matching/incident, path/middle and path/leaf. The two wing
inventories are disjoint and both must fit the distribution.

## Shared-vertex rows

Use the necessary one-root cell-edge rows of `signature_matchings.md`
on both orientations. Let `S⊆U,T⊆V` be supports, and let
`b[S,T,d]` count the sites of `W` with that pair and final degree `d`.
One site cannot meet both `x` and `y`. Both residue degree floors
require `d>=6+max(|S|,|T|)`. Marginalizing over the other mask fixes
each one-root cell's population by degree. In the `u` projection,
the edges from a `W` cell to the private cell of peer `v` are the
sum of `|T-{y}|` over its sites; edges to its peer-double site `y`
are the sum of `1[y∈T]`. Reverse the argument at `v`. These rows use
the same vertices on both sides, not just separate compatible
degree totals. They do not identify the two projected edge matrices
*inside* `W`.

For a private cell at anchor `i∈U`, the matching to `V-{y}` has size
at least `3+1[i=x]`, by the private-cell matching lemma with peer
anchor `v`. If `B⊆V-{y}`, a matching of size `m` uses at least
`m-(4-|B|)` distinct sites having a support intersecting `B`. This
gives the claimed Hall lower rows on `b`; the same holds in reverse.
Every other cross pair of anchors needs a common neighbour by MTF,
and that neighbour must lie in `W`; the usual degree-pair cap supplies
the upper row. Finally, for any set `M` of wing anchors and any `q∈M`,
all sites whose combined support contains `q` and lies in `M` are
independent and can be joined to an independent subset of the wings
outside `M`. That subset has size `10-|M|` minus one if both crossed
endpoints are outside `M`. Subtract its size from nine for the row
upper bound. The same argument works with multiple *disjoint* crossing
edges by subtracting one for each completely outside `M`.

The integer projections are necessary, not embeddings. C13(1,5)
contains 26 actual saturated adjacent equality pairs (two disjoint
cross edges in the smaller analogue); literal graph substitutions pass
every row. All 260 tested nontrivial right-mask swaps are rejected:
156 would create a cross triangle and 104 pass this check but fail
one of the common-vertex equalities. The actual target has one cross
edge; bad alignments in the analogous control were not silently kept.
