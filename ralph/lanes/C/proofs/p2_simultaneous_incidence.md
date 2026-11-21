# Simultaneous incidence requests for a full-wing pair

## Scope

Use the partition and packing hypotheses of `p2_complementary_windows.md`.
At the marked pair, the two fixed windows, both sets of wing attachments and
the common-column bijection determine every edge except those between private
sets `A` and `B`. For the compressed formula below require `U=empty`; the
argument using the fixed graph directly also works with `U` in the base.
The production prototype tests `(12,14)` only. Its proof obligations are
necessary conditions, not an equivalence to the existence of a completion.

## One- and two-vertex requests

Fix the known graph and put `L=V\B`. All edges of `G[L]` are known.
Let `m` be the forbidden independent-set size (10 for the target; 7 for
the regular order-22 control). For each `b` in `B`, let `F_b` be its known
neighbours in `L`, let `P_b` be the still possible neighbours in `A`, and
let `r_b` be the degree deficit at `b`. In a completion, the set
`S_b=(N(b)∩L)\F_b` must be a subset of `P_b` of size `r_b`. The edges
within `B` are already fixed and accounted for in the deficit.

1. Reject if `G[L]` has an independent `m`-set. For each `b`, list all
   independent `r_b`-subsets `S` of `P_b` for which
   `G[L \ (F_b ∪ S)]` has no independent `(m−1)`-set. The list contains
   the actual `S_b` in every target completion: its elements are
   neighbours of `b` and so form an independent set; an independent
   `(m−1)`-set missing all those neighbours could be enlarged by `b`.
2. For distinct `b,b'` with a fixed edge between them, two choices are
   compatible only if `F_b ∪ S_b` and `F_b' ∪ S_b'` are disjoint.
   Otherwise a common vertex and the two adjacent vertices form a triangle.
   For a fixed nonedge `bb'`, require that the subgraph of `L` outside
   `F_b ∪ S_b ∪ F_b' ∪ S_b'` have no independent `(m−2)`-set. If it had
   one, both `b` and `b'` could be added. These are binary compatibility
   relations on whole neighbourhood choices, not coverage bounds summed
   over rows.
3. Delete a choice from any list whenever some other list contains no
   compatible choice. At every deletion, if the lists still contained the
   choices of a completion, its choices would be compatible by step 2.
   Induction therefore preserves the choices of every completion. An
   empty list proves impossibility of the marked boundary. Repeat until
   no deletions or an empty list; termination follows from finiteness.
   A cap or a nonempty fixed point yields **no** impossibility inference.

This test separately applies with `A` and `B` reversed. No degree or
edge not guaranteed by the original marks is inferred from a pass.

## Compressed exact witnesses when `U` is empty

Write `Y` for the wing attaching to `A`, `Z` for the wing attaching to
`B`, and `C` for the common columns. Every vertex of `B` has fixed
neighbours in `L` only in `C` and `Z`. Fix one vertex `b`, or two distinct
nonadjacent vertices `b,b'`, of `B`. Denote their union of fixed `C`
neighbours by `D`, and the size of the union of their fixed `Z` neighbours
by `q`. The particular names of these `q` vertices do not matter: in `L`,
all vertices of `Z` have the same neighbours and none has a neighbour in
`A`. For the base check with no vertices of `B`, use `D=empty,q=0`.

For an independent set `T` in `A`, let `C(T)` and `Y(T)` be its touched
columns and wing vertices. Once the selected vertices of `B` and `T`
are included, the available counts in the three boundary sets are

    c = |C| − |C(T) ∪ D|,
    y = |Y| − |Y(T)|,
    z = |Z| − q.

Both roots are still available: they have no neighbours in `A` or `B`.
`C` is independent, and it is anticomplete to both wings. The wings are
independent separately and complete to each other. The two roots are
nonadjacent; each is adjacent to every column and to its own wing, but not
to the other wing. Thus an independent set using `C` has at most
`c+max(y,z)` boundary vertices and one attaining that bound is available
if `c>0`. With no columns, it can take both roots (and no wings) or a
largest available wing and the root of the other wing. Hence the largest
boundary extension has size exactly

    max(2, max(1,c) + max(y,z)).

For `k=0,1,2` included vertices of `B`, cache each independent `T` whose
size plus this value is at least `m−k`. The union of the chosen cross
neighbourhoods must meet every cached `T`, including `T=empty` if that
is a witness. Conversely, when it meets every such `T`, no independent
`(m−k)`-set avoiding those neighbourhoods exists in the base: any such
set would give a missed witness by its intersection with `A`. This is an
exact reformulation of each test of the fixed `L` graph, not of the full
completion problem. The eligible `P_b` consists of the vertices of `A`
whose `C` supports are disjoint from the mapped `C` support of `b`:
in this partition `C` is the only possible fixed common-neighbour set
for a pair `a,b` with `a∈A,b∈B`. For an adjacent pair in `B`, its fixed
neighbourhoods in `C∪Z` cannot meet (the fixed data are triangle-free),
so the adjacent compatibility condition reduces to disjoint private
choices.

Consequently, for a fixed marked packed base, single lists can be keyed
by `(mapped C support, Z attachment count, deficit)`. Pair relations can
be keyed by the two list keys, the union `Z` count and whether the pair
is adjacent. Relation matrices retain exact support masks on the listed
choices. `p2_request_cache.hpp` caps the propagation representation at
64 choices per list, with a deferred result (not a rejection) if exceeded
and no earlier exact rejection has been obtained.

## Relationship to the earlier filter

Even a degree-feasible boundary that passes the all-possible-edges
independence check can fail these tests: such a graph gives no single
choice of `r_b` neighbours with which to meet every applicable request.
The five-vertex unit control already shows a pair failure with nonempty
single lists and feasible degree flow. The two rows each require their
one available edge to the same base vertex; using both rows would leave
the other two base vertices independent and give an independent four-set.
The frozen `(12,12)` proof bundle is independent of this method.

## Shared-core extension (not implemented in the cache)

For `U` nonempty, put it in `L`. Conditional on the independent choice
`T` in `A` and the selected vertices of `B`, enumerate the independent
subsets `Q` of `U` avoiding neighbours of both selected sets. A vertex
of `U` touches neither a root nor a wing. For a fixed `Q`, add `|Q|`
and remove `N(Q)∩C` from the available columns in the boundary formula.
Maximizing over `Q` is exact because every independent set has one such
intersection with `U`, and the boundary formula still attains its
maximum. Cross eligibility additionally excludes a common neighbour
in `U`. This observation does not generate or cover any H20 windows.
