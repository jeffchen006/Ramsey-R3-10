# An isolated maximum-codegree pair with almost complete wings

Let G be a triangle-free d-regular graph on n vertices with independence
number at most d and maximum codegree k, where k>=3. Suppose nonadjacent
u,v have codegree k and are the only codegree-k partners of one another.
Write C=N(u) intersect N(v), Y=N(u) minus C, Z=N(v) minus C, and
X=G-(N[u] union N[v]). Put m=d-k. Both wings are independent m-sets,
and C is independent and has no edge to either wing: otherwise there
would be a triangle at u or v. Every vertex of C has exactly d-2
neighbours in X, as its only other neighbours are u and v. The two
root neighbourhoods are independent sets of size d.

For x in X, let y(x),z(x) be its numbers of neighbours in Y,Z.
All neighbours of x are in X+C+Y+Z. Its codegree with u is
`d - d_X(x) - z(x)`, since the neighbours of x in N(u) are those
in C+Y; symmetrically its codegree with v is `d - d_X(x) - y(x)`.
Neither codegree is k by isolation, so

    y(x) >= m+1-d_X(x),      z(x) >= m+1-d_X(x).

The two wing-neighbour sets of x have no edge between them, by
triangle-freeness. If Y--Z is complete this gives **min degree in X
at least m+1**. In addition every x has a neighbour in C: otherwise
it must hit both Y and Z to avoid extending a root neighbourhood
to an independent (d+1)-set, impossible when Y--Z is complete.

If Y--Z lacks exactly one edge yz, then d_X(x) cannot be below m:
otherwise two neighbours in each wing would require four missing
edges. Put D={x in X: d_X(x)=m}. Each x in D sees exactly y and z
on the wings, and hence exactly k-2 vertices of C. Let U be the set
of vertices in X with no C-neighbour. Each x in U must have wing
neighbours on both sides because the root neighbourhoods are
independent d-sets, and hence is adjacent to both y and z. Since
k>=3, D and U are disjoint. The common neighbourhood of y,z has
size at most k, so `|D|+|U|<=k`. On the other hand counting C--X
edges gives

    k(d-2) >= (k-2)|D| + |X|-|D|-|U|.

Using `|U| <= k-|D|` yields

    (k-2)|D| <= k(d-1)-|X|.

In R(6), apply this only to a two-vertex J component, not to either
edge of a three-vertex J component. Here `(d,k,|X|)=(9,6,26)`.
The known edge identity gives `e(X)=72+e(Y,Z)`. Therefore the e81
residue has minimum degree at least four. The general counting
bound gives at most five degree-three vertices at e80, but the
target has a sharper bound. In any triangle-free graph X on 26
vertices with alpha<=7, two nonadjacent vertices of degree three
would leave at least 18 vertices after deleting their closed
neighbourhoods. The remainder has alpha<=5, contrary to R(3,6)=18.
Thus its degree-three vertices form a clique. The e80 vertices in
D all neighbour y, so they are independent; consequently at e80
there is **at most one degree-three vertex**. The same argument
gives this stronger conclusion whenever all missing wing edges
share an endpoint, since every degree-three vertex must hit both
wings and its cross rectangle lies in the missing edges. These
are necessary filters, not exclusions of an edge stratum.

The exact calibration is `p2_isolated_control.py` on the known
6-regular order-22 census. It derives the pair and wing partitions,
checks the input graphs, and verifies the generalized pointwise and
counting bounds on every applicable pair.
