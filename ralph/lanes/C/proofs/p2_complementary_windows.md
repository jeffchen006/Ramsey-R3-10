# Complementary windows at a full-wing codegree-six pair

## Hypotheses and partition

Let G be a 9-regular triangle-free graph on 40 vertices with alpha at
most 9 and maximum codegree 6. Suppose every codegree-six pair has
three-by-three complete wings (the global `f*=9` subcase), and let
`u,v` be a codegree-six pair. Use `C=N(u)∩N(v)`, `Y=N(u)\C`,
`Z=N(v)\C`, and `X=V\({u,v}∪C∪Y∪Z)`. The accepted complete-arm
and path/triangle exclusions give that the graph of codegree-six
pairs is a matching. The common-support budget and no-siblings
argument in `p2_full_wings.md` apply. In particular the two sets
`A=N(Y)∩X`, `B=N(Z)∩X` are disjoint, their sizes are each at least
12, and `U=X\(A∪B)` has size at most 2. The ordered size pairs, up
to reversal, are `(12,12),(12,13),(12,14),(13,13)`.

The graphs `H_A=G[{u}∪C∪U∪A]` and `H_B=G[{v}∪C∪U∪B]` are the
antineighbourhoods of the independent sets Z and Y respectively.
They are triangle-free with alpha at most 6. Their marked roots
are of degree six and determine C. The core orders are given by
`|A|+|U|=26-|B|` and its reverse, not by the size of X. Thus the
order pairs for H are respectively `(21,21),(20,21),(19,21),
(20,20)`; order-13 cores cannot themselves serve as H windows.

## Packing and gluing identities

Every vertex of Y has five neighbours in A, and triangle-freeness
makes these independent. Two such five-sets meet in at most one:
their two Y vertices have four other common neighbours, and the
no-siblings argument excludes codegree six for them. The three
five-sets cover A. The same assertions hold for Z on B. This
describes exactly how to mark a half up to wing vertex permutation:
choose three distinct independent five-sets with pairwise overlap
at most one and prescribed union size, and take U to be the
complement of that union in the core. Every core vertex has
nonempty C support. Within a half at most one singleton support
uses a particular c, since that half avoids the other wing. If q of
its singleton supports lie in U, the half's support excess plus q
is at most two, by the global support budget. Once the wing is
added, no private degree exceeds nine, and `deg_C(x)+deg_wing(x)`
is at most five: this is the codegree with the marked root, whose
only codegree-six partner is the other root. Two C vertices have at
most four common neighbours within a core (the two roots are also
common), and local equality forces a partner in the codegree-six
matching. All these tests are necessary, not completion tests.

The overlap graph on `C∪U` is fixed by the U edge (if |U|=2) and
the U-neighbour mask of each c, as C is independent. The two root
vertices remain distinct. There are no unaccounted edges at a
vertex of C or U: for c the two roots and all X account for its
edges; for x in U all its neighbours are in C or X. By counting each
overlap edge twice, the exact equations are

    d_HA(c) + d_HB(c) = 9 + |N(c)∩U|      (c in C),
    d_HA(x) + d_HB(x) = 9 + |N(x)∩(C∪U)|  (x in U).

For a fixed ordering of U, the multiset of pairs
`(U-neighbour mask, degree in H)` at C determines admissible
complementary C maps: enumerate only bijections matching the mask
and the complementary degree. The U equations are separate. Each
C-pair codegree then equals the sum of the two local common-
neighbour counts minus the number of common U neighbours; each
local count has its own root, both of which are needed. In the
symmetric join one may order the two mark keys lexicographically:
reversing the sides and inverting the bijection preserves all
constraints. Equal mark keys remain included. Raw maps are not
necessarily unique isomorphism types.

## Necessary cross tests

After a join, fix each window, each wing attachment, all Y--Z
edges and each root's own wing. All other edges except A--B are
determined absent. An A--B edge whose endpoints have a fixed common
neighbour is immediately forbidden. The remaining cross graph must
have the residual degree at each of its ends, so the totals must
agree, each residual degree must lie in `[0,available count]`, and
the unit-capacity bipartite matching flow must realize those degrees.
A vertex with zero residual degree loses its available edges; a
vertex with residual degree equal to its available count forces all
of them. A forced edge removes any new triangle-closing candidates.

For any pair with six fixed common neighbours, their codegree is
already six and neither endpoint can have a second such partner.
Any known exclusive neighbour of one endpoint is forbidden to
become adjacent to the other, as that would create a seventh common
neighbour. Thus all presently known exclusive neighbours on the two
sides really belong to the two wings of this pair. Every edge
between these two groups must be present by the complete-wing
hypothesis. This soundly forces edges or rejects if an edge is
unavailable. A pair with more than six fixed common neighbours is
impossible already. Iterate these operations and degree propagation
until stable. Finally, an independent ten-set in the graph of all
fixed *and* still possible edges is independent in every completion,
so it rejects the candidate. The complement signature and these
filter steps are finite exact enumeration, not solver certificates.

## Residual CNF and scope

For each surviving pin, reconstruct the boundary starting from the
two marked windows and packs, **before** degree, flow or complete-
wing propagation. There is one variable per A--B edge not forbidden
by a fixed common neighbour. For a vertex with domain D and deficit r,
emit one negative clause per (r+1)-subset of D and one positive
clause per (|D|-r+1)-subset of D (invalid deficit gives an empty
clause). Every potential triangle must miss a cross edge. For every
independent ten-set in the fixed graph, at least one candidate cross
edge inside it must be present. Deduplicating these positive clauses
preserves them; an empty one remains empty. This CNF deliberately
does not enforce codegree, matching or complete wings at other
pairs. Every completion of the marked pair therefore satisfies it.

`p2_window_join.cpp`, `p2_cross_cert.py` and `ROUND6_REPLAY.md` give
the computation for `(12,12)` only. Its conclusion is a composite
`enum + cert`, using the census, the necessary-filter proof and
the checked last-mile refutations. It rules out the two-avoider
branch under the stated hypotheses; it does not exclude another
wing-size pair, a general isolated complete-wing pair, or R(6).

## Target profiles for the (12,14) pilot

Here U is empty. Write `s=|A|`, `S_A=sum_{c∈C}d_HA(c)` and `e_A=e(G[A])`,
and similarly for B. Summing the degree deficits on a side gives
`9s-15-2e_A-(S_A-6)`. Each prospective cross edge adds one to both
side sums. Since `S_A+S_B=54`, for `s=14` this implies
`e_B=e_A+S_A-36`. The other six column sizes inside the core are
the sorted values `8-d_HA(c)`. These identities allow a census of
necessary input profiles for the smaller marked H19, but they do
not generate those H19 windows or prove anything about extension.

## One-window independent-set capacity bound (negative measurement)

This generalizes to degree d and wing size m. In a known marked H_A
with its wing pack fixed, let f(x) count the degree still assigned to
the opposite private side B. For a core vertex x of H_A this is
`d-d_HA(x)-deg_Y(x)` (zero Y attachments on U); for c in C it is
`d-d_HA(c)-1` because of the other root v; and f(u)=0. Thus for any
T in H_A, `|N(T)∩B| <= sum_{x∈T}f(x)`.

If T is independent of size t, the graph on `(B\N(T))∪Z` is
anticomplete to T. If T avoids C, also add the other root v since
its only neighbours in H_A lie in C. That graph is triangle-free
with alpha at most d−t. Thus the capacity sum is at least
`|B|+m+1+[T∩C=∅]−R(3,d−t+1)`. If T is contained in the core,
it extends by both roots; using only `B\N(T)` as the residual
graph yields the separate bound `|B|+1−R(3,d−t−1)`. The scan of
these exact bounds rejected no packs for either H21 side 13 or 14
against the opposite side of size 12. This is not a claim about
stronger incidence-pattern or edge-count refinements.
