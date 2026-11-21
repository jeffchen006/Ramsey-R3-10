# Exact overlapping windows for codegree-six paths

**Status:** hand reductions and finite enumerations conditional on the
order-22 census. No assertion is made about an isolated codegree-six
edge or a three-root component, including any of its diagonal types.

Let G be a Case R(6) model and let v0,v1,... be distinct consecutive
vertices in the graph J of codegree-six pairs. No inducedness in G is
assumed. Use the three-set decomposition of `codegree_six_paths.md`:
for a span with roots numbered 0 through L, write
N(vi) = D(i-1) disjoint-union D(i) disjoint-union D(i+1).

G is maximal triangle-free: adding a triangle-free edge would give a
vertex with ten independent neighbours. This follows from regularity
without a separate restriction to maximal graph candidates.

## Four roots: a 20-vertex overlap

For v0,...,v3, put A = G - N[v1] - N[v2]. The middle roots are distinct
and nonadjacent. The open neighbourhoods of v1,v2 have union of size
18-6=12, namely the four disjoint blocks D0,D1,D2,D3. For disjointness of
D0 and D3, use N(v1) intersect N(v2) = D1 disjoint-union D2; all other
pairwise disjointness follows from the within-neighbourhood partitions.
Thus A has 26 vertices. In A, v0,v3 are adjacent and have respective
open neighbourhoods D(-1), D4. Indeed each exterior block is disjoint
from all four middle blocks: disjointness from the blocks in its own
neighbourhood follows from its partition, and disjointness from the
neighbourhood of the other middle root follows from the distance-two
intersection containment. The exterior blocks cannot contain v1 or v2
since these roots are nonadjacent to v0 and v3. Moreover D(-1) and D4 are
disjoint since v0v3 is an edge of a triangle-free graph.

Write Y = D4 minus {v0}, Z = D(-1) minus {v3}, and X = A minus
(Y union Z union {v0,v3}). Both Y and Z are independent pairs. The
consecutive triple windows are

    H0 = G - N[v0] - N[v1] - N[v2] = A - N_A[v0] = X + Y,
    H1 = G - N[v1] - N[v2] - N[v3] = A - N_A[v3] = X + Z,

where the plus sign means induced subgraph on the indicated union, not
graph disjoint union. Each triple is independent in G, so both windows
are among the 191 triangle-free graphs of order 22 and alpha <= 6.

Enumerate every independent pair in each census graph, with the one
necessary restriction that the common neighbours of the marked pair in
the census graph number at most five (the missing opposite root is
also common in G). Delete the mark and group the remaining order-20
graphs by isomorphism. At each labelled representative X, transport
the pair's two X-neighbourhood masks by **every** such isomorphism and
store the pair of masks in sorted order. Interchanging equal masks
loses nothing because cross edges are searched in all labelled ways.
Take all unordered pairs of resulting marked types, including equal
types (reverse the root sequence if needed). Add the two endpoint roots
with exactly their specified A-neighbourhoods, and all possible subsets
of Y--Z edges that do not form triangles with X. There are no other
undetermined A edges. This covers the A of every model with such a
path, up to orientation and relabelling that preserves the marked parts.

Retain a row only if:

- A has 73..81 edges: 73 is the published e(3,8,26), since an
  independent set of A can add both middle roots. If B is the deleted
  14-vertex set, it has 18 edges incident to its roots and its only
  other possible edges join D0 to D3 (every other block pair has a
  common adjacent root). Thus e(A) = 180 - 14*9 + e(B) = 72 + e(D0,D3).
- The A-degrees are 3..7 and alpha(A) <= 7. The upper degree bound
  follows from triangle-freeness. For the lower bound, deleting a
  closed A-neighbourhood leaves at most 22 vertices (alpha <= 6).
- All codegrees in A are <= 6 because A is induced in G.

The output layout, encoded as ordinary labelled graph6, is X[20], Y[2],
Z[2], v0, v3. It is a cover, not a classification of feasible full
extensions and not a partition of models. The reduction is local to a
four-root span; extra J-neighbours at its endpoints are not excluded.
The program's control uses six-regular C21(1,4,6), c=4, two-set blocks,
and the complete three-class (3,4;8) census. In this calibration the
two middle roots delete 10 vertices, A has order 11, the two windows
overlap on seven, and the cross-block edge identity is 15+e(D0,D3).

There is an additional P4 filter, not needed for the P5 scan below.
Write B = V(G) minus V(A). No y in Y can be adjacent to v1 or v2,
which have no neighbours in A; the same is true of z in Z. No common
neighbour of y,z can lie in D0 or D1: each vertex of those blocks sees
v0 and therefore cannot see z. Likewise no common neighbour can lie in
D2 or D3, which see v3 and cannot see y. Neither endpoint root is a
common neighbour within A, so the only possible common neighbours of
y,z lie in X. By maximality and triangle-freeness, yz is therefore an
edge if and only if the masks of y,z on X are disjoint.

## Five roots: the two A graphs share a triple window

Now use v0,...,v4 and the blocks D(-1) through D5. These seven blocks
are disjoint. In general any pair of these whose indices differ by
at most two occurs in a common root neighbourhood and is disjoint by
the decomposition. For indices j<k differing by 3..6, choose
i in [j-1,j+1] intersect [0,4] and h in [k-1,k+1] intersect [0,4]
with 3 <= h-i <= 5. Such choices exist: the largest difference is at
least 3 (choose i=max(0,j-1), h=min(4,k+1)); the smallest is at most
4 (choose i=min(4,j+1), h=max(0,k-1)); attainable differences form an
integer interval. Then vi,vh are adjacent, so their neighbourhoods
are disjoint. Each selected block lies in the corresponding one.

From the distance-3 through distance-5 results and the block
decomposition, v0 belongs to D4, v1 to D5, v3 to D(-1), v4 to D0,
and v2 belongs to none. More explicitly: v0,v3 occur in the exterior
blocks of span 0..3, while v1,v4 occur in the exterior blocks of span
1..4. The blocks D(-1) through D5 are all contained in at least one
root-neighbourhood and v2 has no neighbours among the five roots.
Let Pj = Dj minus the roots. For j=-1,0,4,5, these sets have size two.
Let W be the vertices outside all seven blocks and the five roots;
its order is 18. The middle triple window is

    H1 = G[W union P5 union P(-1)].

The block decomposition of either four-root subspan is the restriction
of the five-root decomposition: each internal block is defined by its
two surrounding N-sets, and the endpoint blocks are the unique remaining
parts of the adjacent N-sets after those internal blocks are deleted.
In the output layout of a P4 row, the two successive A graphs are

    A0: X = W + P5,    Y = P4, Z = P(-1), roots v0,v3;
    A1: X = W + P(-1), Y = P5, Z = P0,    roots v1,v4.

Always use both orientations of each P4 row in this join. For A0 mark
Z in H1 = X+Z; for A1 mark Y in H1 = X+Y. Align H1 by every induced
graph isomorphism, with disjoint marks. In A0 check that P4 and P5 have
no cross edges (both see v4 in G). In A1 check that P0 and P(-1) have
no cross edges (both see v0). These checks are necessary, not assumed
complete. The union of A0 and A1 is exactly U = G - N[v2], since their
deleted sets intersect in {v2} union D1 union D2 union D3. The only
still-unknown edges join the two disjoint outer parts A0-H1 and A1-H1.
Among those, the known root-neighbourhoods fix all incidences involving
a root: v0 sees v4 and all of P0; v4 sees all of P4; v1 has no new
neighbours in A0-H1, and v3 has none in A1-H1. All others are the four
possible edges P4--P0. Enumerate those independently and retain only
triangle-free U with e=99, alpha<=8, degrees in [3,8] (since
deg_U(x)=9-c(v2,x)), and codegrees at most six. Every real U must occur
in this enumerated superset. In the C21 calibration U has order 14,
e=27, degree range [2,5] (a permissive upper bound from alpha<=5),
and its shared H1 has two disjoint singleton marks instead of pairs.

## Exact R(6) extension filter for the five-root span

The complement of U contains v2 and its nine neighbours. Those nine
vertices form an independent set and their neighbourhoods in U have
size eight. D1, D2, D3 (three vertices each) meet the four marked
roots (v0,v1,v3,v4) in the masks {v0,v1}, {v1,v3}, {v3,v4}
respectively. Enumerate all size-eight independent masks in U with
those exact intersections. An eligible mask M can be dropped if a
vertex x of U has |N_U(x) intersect M| > 6: this is already the
codegree of x and the outside vertex, which have no possible common
neighbour outside U. x is not adjacent to v2, and the nine outside
vertices have no edges to each other. Masks with adjacent roots cannot
pass; here the prescribed pairs are independent in every cover row.

Any completion picks three distinct masks of each type and loads each
x of U exactly 9-deg_U(x) times. Distinct outside vertices have common
neighbour v2, so their U-masks intersect in at most five vertices.
Two selected masks must also jointly hit every independent 8-set of
U; otherwise the two outside vertices extend that set to size ten.
Finally, each nonadjacent pair x,y in U with no common neighbour in U
requires a selected mask containing both, by maximality. These are
necessary conditions; none relies on full codegree restrictions for
pairs of U vertices after attachment.

The exact filter rejects a root if the initial load of a vertex is
impossible counting types with capacity three, or a required pair is
unsupported. Otherwise it explores a finite tree. At each node a
positive colour-type quota, positive vertex quota, or unsatisfied
pair requirement gives a set P of still viable masks at least one of
which must be used. If any quota exceeds the count of available
masks meeting it, the node is impossible. Branch in order through P;
the branch choosing its i-th mask forbids all earlier masks in P,
and forbids any incompatible masks and any that would overspend a
remaining quota. Every completion has a first selected mask in P,
so no completion is lost. Once nine masks have been chosen, there
are no undetermined edges; test the resulting graph for an independent
10-set. A genuine completion would pass. The depth is at most nine.

The 1,156 joined residues yielded 940 unsupported-pair exclusions and
216 exhaustive trees (289,649 total nodes, max 10,760). No nine-mask
packing was even reached, so no final independence tests are needed
in the refutation trace. No node limit was set. The full calculation, conditional
on the 191-census and hand reductions, excludes any five consecutive
distinct vertices of J in R(6). This is `enum` pending independent
coverage and search replay; it is not a Lean or SAT certificate.

## P4 propagation pilot

When extending A, any new vertex in D0 or D1 sees v0, and therefore
does not see its A-neighbours. Likewise for D2/D3 and v3. Every edge
within the deleted part B is already specified by its root stars,
except the pairs D0 x D3. These conditions specify the initial allowed
edges in the propagation test. The possible extensions are maintained
as forced edges plus an edge superset containing all candidates. At
each step the degree must lie between the forced and possible degree;
equality at either bound fixes the remaining incidental candidates.
With a forced common neighbour, a pair must be a nonedge, and with
six forced common neighbours no further possible common neighbour can
become forced. Any edge within a forced triangle is a conflict; if just
two sides are forced the third must be absent. Maximality forces a pair
with no possible common neighbour to be adjacent; when a forced nonedge
has only one possible common neighbour, both links to it are forced.
These operations preserve every possible model. For the residual
D0 x D3 unknowns the test tries every subset completing the required
count e(A)-72, and reapplies propagation; no other unknowns are split.
Thus surviving partial assignments are not model completions.
