# Three codegree-six roots: keep the diagonal types separate

Let v0,v1,v2 be distinct consecutive roots in J, the graph of
codegree-six pairs in a Case R(6) graph G. The roots are independent;
and N(v0) intersect N(v2) is contained in N(v1), as proved in
`codegree_six_paths.md`. Put s=c(v0,v2). Then 3<=s<=5 (size six
would give a K3,6). In N(v1) partition by membership in N(v0) and
N(v2), calling the four blocks T (both), B0 (only v0), B2 (only v2),
and B1 (neither). Their sizes, respectively, are s, 6-s, 6-s, s-3.

In G-N[v1] the two exterior roots have three neighbours each;
write Y=N(v0)\N(v1) and Z=N(v2)\N(v1). These wings are disjoint
by the containment; each is independent. The rest after removing
all three closed neighbourhoods is the order-22 graph X with
alpha<=6. The deleted set has 18 vertices and exactly 27 edges
incident to the three roots. Among the remaining deleted vertices,
the only possible edges are Y--Z, B0--Z, B2--Y, and B1--(Y+Z).
Indeed all four B-blocks and T meet at v1, and a shared exterior
root rules out every excluded wing incidence. If f is the total
number of the possible edges actually used, summing degrees of
the deleted vertices gives

    e(X) = 180 - 18*9 + 27 + f = 45 + f.

These formulas apply to a three-root span without assuming it is
an entire component. They do not apply to an isolated J edge.

## Boundary bound and the e64 shape when s=5

Let r=|E(Y,Z)|, and let m be the size of a maximum matching in
that 3-by-3 bipartite graph. The wing-neighbours of each vertex in
B1 form an independent set in Y+Z; the m
disjoint matching edges force its size to be at most 6-m. Thus

    f <= r + 6*(6-s) + (s-3)*(6-m).

For s=5 this is r+18-2*m. A 3-by-3 bipartite graph of matching
size m has at most 3*m edges: by König's theorem it has a vertex
cover of size m, and each of its vertices covers at most three
edges. Thus f<=18+m<=21.

For any independent Q contained in the wings, the union of Q and
its nonneighbours in N(v1) is independent. Thus the neighbourhood
of Q in N(v1) has size at least |Q|. Applied to all subsets of Y,
this is Hall's condition for a perfect matching of Y into B2+B1,
which has size three. Symmetrically Z must match into B0+B1. In
particular **both** B1 vertices need a neighbour in each wing, and
their joint neighbours must contain at least two vertices in
each wing. Also every independent subset of Y+Z can include T,
hence alpha(Y+Z)<=4 and m>=2 by König's theorem.

The two B1 neighbourhoods are mixed independent sets in Y+Z. A
mixed set with a vertices of Y and b of Z requires all a*b cross
edges to be missing.

- If m=3 and r=9, there is no mixed set. If r=8, such a set
  has size at most two, and f<=8+6+4=18. If r=7, a mixed set
  of size three requires both missing edges to share their
  singleton endpoint. There is at most one such triple. Both
  B1 vertices cannot choose it, as their joint neighbours in
  its singleton wing would violate Hall. Thus f<=7+6+3+2=18.
  For r<=6 we have f<=r+18-2*m<=18.
- If m=2, then r<=6. Equality r=6 requires that a two-vertex
  cover is in one wing (a cover with one vertex in each wing
  can cover at most five edges) and both vertices have degree
  three. Then any mixed independent set must use the third
  vertex in the cover's wing, and no other vertex of that wing.
  This again violates Hall for the two B1 vertices. Thus r<=5
  and f<=r+18-2*m<=19.

Consequently **e(X)<=64 for diagonal s=5**. Equality requires
m=2, r=5, both B0 and B2 saturated into their opposite wing, and
both B1 neighbourhoods to be mixed independent four-sets. If a
four-set has split 1+3, it uses three of the four missing edges
sharing the singleton endpoint. A second four-set with the same
split but a different singleton would need six missing edges.
One of split 3+1 intersects those three edges in at most one edge,
and would need at least five missing edges in union. One of split
2+2 requires four missing edges, and at most two can overlap the
three edges of the first four-set. Thus the other four-set would
have to repeat the same singleton, violating Hall. The reversed
split 3+1 is symmetric. Both four-sets therefore have split 2+2
and each accounts for all four missing edges. Their neighbourhoods
are identical on those two vertices in each wing. Equivalently,
Y--Z has exactly the edges incident to the remaining vertex in
each wing, and the e64 deleted graph is unique up to block relabelling.

In this equality shape every vertex of X has a neighbour in T.
Indeed, let Y' and Z' be the two selected vertices in each wing,
and let y* and z* be the remaining vertices. The independent
nine-set T+Y'+Z' must have a neighbour of every vertex of X. If a
vertex x of X avoids T and hits Y', it cannot see z* or any vertex
of B2+B1: every vertex of Y' sees them, so triangles would result.
But T+{z*}+B2+B1 is independent of size nine, so x must hit it, a
contradiction. Hitting Z' gives the symmetric contradiction. The
five vertices of T each have six X-neighbours (their only other
neighbours are the roots). Therefore at least 14 of the 22 vertices
of X have exactly one neighbour in T, since the 30 total incidences
leave only eight beyond the first at each X-vertex. Neither extra
fact is needed by the e64 proof CNFs: their independence rows
already impose the saturated-set constraints.

An earlier (weaker) e66 proof package at `scratch/C/p3-top-certs`
first inferred the shape with complete Y--Z from the bound
f<=18+m<=21, then used K3,6 to force the two B1 vertices to choose
opposite wings. The resulting graph already contains an independent
10-set inside the deleted part, so SAT refutation of that weaker
stratum is redundant. The Hall argument above does not use that
computation or the P4 exclusion.

For the six-regular 21-vertex calibration with codegree-four
pairs, the wing sizes are two, the diagonal of the planted C21
span is two, and the corresponding X has order eight. With
degree six and 13 deleted vertices the identity becomes
e(X)=63-13*6+3*6+f=3+f. Use this full planted graph to check the
partition and a fixed-boundary encoding before any larger run.
