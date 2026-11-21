# Fixing the four exclusive neighbourhoods for a K2,2 pair

**Status:** hand reduction, not an exclusion. In addition to the case R(7)
where this shape follows from Lemma R7, the reduction applies to smaller
controls with the same fixed shape.

Let G be a triangle-free d-regular graph with independence number at most d,
and let c < d be an upper bound on nonedge codegree. Suppose two nonadjacent
vertices u,w share d-2 common neighbours C, and their exclusive neighbours
A and B (two vertices each) induce a complete bipartite K2,2. The fixed
residue X consists of all vertices outside these thirteen vertices in R(7)
(outside d+4 vertices in general). It has independence number at most d-2
because u,w can be added to any independent subset of X. Each boundary
vertex z in A or B has exactly d-3 neighbours in X and each z in C has
exactly d-2. Each of those neighbourhoods is independent.

## Necessary constraints for a pair of sides

Write M1,M2 for the X-neighbourhoods of the two A vertices, and N1,N2 for
those of the two B vertices. The same rules apply with A and B switched.

1. `M1 | M2` and `N1 | N2` are disjoint by triangle-freeness and the
   four edges between A and B. Each x in X needs at least one neighbour
   in C: N(u) and N(w) are maximum independent sets, so x must hit both.
   Without C this would force x to have neighbours on both sides, a
   triangle. For each x the four masks may therefore spend at most
   d-deg_X(x)-1 neighbours at x.
2. For every independent (d-2)-set I in X, each of the two unions meets I.
   Otherwise I plus the corresponding two boundary vertices and the
   opposite root is independent of size d+1.
3. M1 and M2 can overlap in at most c-3 vertices: the vertices of A
   are nonadjacent and share u and the two B vertices in addition to
   their common neighbours in X.
4. For i=1,2, each x outside the closed neighbourhood of Mi in X must
   touch at least one B vertex. The nonedge formed by x and the boundary
   vertex with neighbourhood Mi needs a common neighbour, because
   the degree-d neighbourhood of either vertex is maximum independent.
   Its common neighbour cannot be in X by the definition of x, cannot
   be a root (x is outside both closed root neighbourhoods), and cannot
   be in A or C (which share a root with the given boundary vertex).

Thus each side can be generated as an unordered pair of eligible masks,
with an attached union U and set D of vertices required on the opposite
side. A package already fails if its own U intersects D. Two packages
survive the filter exactly when their U sets are disjoint and each D is
contained in the other U. These are only necessary conditions. The code
does not quotient by automorphisms in X.

## Complete independence constraints at fixed residue

For a chosen set of d-2 neighbourhood masks of C (distinct, because
two equal masks would give a nonedge of codegree d), and for an
independent I in X, define miss_C, miss_A, miss_B as the numbers of
the masks in each part disjoint from I. An independent set meeting X in
exactly I and including neither root can add all avoiding masks in C
and at most one of A or B. This follows because A/B is complete while
C has no edges to A or B (the relevant pair shares a root neighbour).
So the necessary and sufficient independence row for this situation is
`|I| + miss_C + max(miss_A, miss_B) <= d`. If it uses both roots,
only vertices in I are available and |I| <= d-2. If it uses exactly
one root, only the *opposite* exclusive side is available and row 2
above excludes the only possible violation (|I|=d-2 and both masks
on that side disjoint from I). The rows for |I|=0 or 1 hold from
the fixed sizes and the requirement that x in X hits C.

## Depth-first completion at fixed side packages

After fixing a pair of side packages, subtract the known A/B coverage
from each X vertex's boundary degree. This leaves positive demands whose
sum is (d-2)^2. There is one candidate colour for each independent
(d-2)-set of X. Selecting a colour consumes one unit of demand at each
of its vertices. When the demand reaches zero, all remaining colours
at that vertex are forbidden. Overlap exceeding c-2 with a previously
selected colour is forbidden by the c-codegree cap for the two C vertices
with shared root neighbours u,w. For each independent (d-2)-set I in X the
row above restricts the number of colours disjoint from I to
2-max(miss_A,miss_B). The search maintains this budget, removing those
colours from the domain when the budget reaches zero. All other
independence rows are checked on completed lists of colours.

When two nonadjacent vertices x,y have no common neighbours in X or in
the fixed side packages, they must appear together in at least one C
colour. (They are adjacent to neither root.) The search maintains these
uncovered pairs in a bitmask. A branch pivot is either such an uncovered
pair or a vertex whose residual demand is positive. Every completion must
contain some allowed colour containing that pivot. Order the pivot's
candidate colours and in each branch pick the first that occurs in the
completion: earlier colours covering that pivot may be removed in the
branch, but all other allowed colours remain until a proved constraint
eliminates them. Thus without a node cutoff every admissible completion
is searched. Since each colour has size d-2, once d-2 colours have been
chosen without exceeding the residual demands, all demands are met.

The DFS is a candidate enumerator, not a formally verified checker. A
finished negative result is `enum`; hitting its node cutoff is **open**.
The separate set-variable SAT pilot is also unchecked unless followed by
CNF validation and a proof run.
