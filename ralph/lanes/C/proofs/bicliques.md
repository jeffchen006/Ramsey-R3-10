# Biclique obstruction in a (3,10,40)-graph

**Status:** hand, conditional only on the standard Ramsey upper bounds
listed in `notes/DEPENDENCIES.md` (D-R1). No regularity or saturation needed.

Let G be triangle-free and have independence number at most k. Suppose
disjoint vertex sets A and B, of sizes a,b >= 1, have every A--B edge.
Both parts are independent: any edge inside one part would make a triangle
with any vertex of the other. Partition the remaining vertices into P,
which have no neighbour in A, and Q, which have a neighbour in A. Every
vertex in Q has no neighbour in B (an edge to B together with its
neighbour in A would form a triangle). Any independent set in P can be
joined to A, so alpha(P) <= k-a, and any independent set in Q can be joined
to B, so alpha(Q) <= k-b. Apply the Ramsey upper bounds for these
triangle-free induced subgraphs. The conclusion is

    |V(G)| <= a+b+(R(3,k+1-a)-1)+(R(3,k+1-b)-1).

If a or b equals k, the corresponding term is zero (an independence
number at most zero requires an empty graph).

For k=9, a=3, b=6, the bound is 9+22+8=39, using
R(3,7)=23 and R(3,4)=9. For k=9, a=4, b=5, it is 9+17+13=39,
using R(3,6)=18 and R(3,5)=14. Thus neither K_{3,6} nor K_{4,5}
is a subgraph of a (3,10,40)-graph. In bitmask language, every
three vertices have at most five common neighbours and every
four have at most four common neighbours (adjacent vertices have none).

## Application to the two-codegree-six seed

In the regular case, let w,z be two nonneighbours of v, each with
codegree six with v. They have a common neighbour in N(v) since both
of their N(v)-neighbourhoods have size six in a nine-set; hence they
are nonadjacent. In H=G-N[v], the vertices w,z both have degree three.
If their neighbourhoods in H intersected, removing their closed
neighbourhoods from H would leave at least 30-2-6+1=23 vertices, with
independence number at most six (one could add v,w,z). This contradicts
R(3,7)=23. Therefore the w,z codegree equals their common intersection
with N(v), i.e. the triple common-neighbour count of v,w,z. That count
is at most five by the biclique obstruction. It is at least three by
the intersection bound inside N(v). In particular the graph of
codegree-six nonedges is triangle-free in R(6).
