# Reciprocal windows at codegree cap five (hand reduction)

Let G be triangle-free, d-regular, and have independence number at
most d. Let disjoint root groups A and B, each of size t, span a
complete bipartite graph. Triangle-freeness makes each root group
independent and prohibits a vertex outside A+B seeing both groups.
Write F_A = G − (A ∪ N(A)) and F_B = G − (B ∪ N(B)). We use the
same letters for their vertex sets. Their union is all vertices outside
A+B, and their common part Z consists of the vertices seeing neither
root group. Put Q_A = F_A − Z and Q_B = F_B − Z. Every independent
set in F_A extends by A, so α(F_A) ≤ d−t; the same holds for F_B.

For every b in B, its neighbours outside A form an independent
(d−t)-set in Q_A. Their union over b is Q_A, and the intersections
of any two of the sets have order at most M−t under a codegree
cap M, because the roots already share t neighbours in A. The
same conditions hold for the other side. The sets of either group
are distinct at the tested parameters and may be listed in arbitrary
order: permuting the corresponding roots leaves the complete root
bipartite graph unchanged. For t=3, inclusion–exclusion proves the
necessary pair-intersection lower bound `3(d−t)−|Q_A|−2(M−t)`;
the analogous t=2 rule follows directly from the union size. A host
vertex already adjacent to h roots cannot exceed total degree d or
its allotted codegree with any root or host vertex. At a private vertex
x, `d−d_Q(x)−h ≤ d−t`: all those remaining neighbours are in the
opposite window, and are independent there. These are the local
enumeration tests; they do not assume the local marks extend.

Every z in Z has all its neighbours in the two windows, counted twice
precisely in their common induced graph. Thus, for every aligned z,
`d_F_A(z)+d_F_B(z)=d+d_Z(z)`. The opposite degree is between zero
and d−t by the independent-neighbourhood bound in each window.
Sorting the colour pairs `(d_Z(z),d_F(z))` augmented by the multiset
of colours of each vertex's neighbours in Z is necessary for an
alignment; construct requested colours using the displayed identity
before forming the neighbour multisets. The implemented encoding is
injective on those colour tuples: in the target, `d_Z≤3` by the
degree identity and `d_F≤6` on both sides. The same encoding also
fits the smaller control, `d=6,t=2`. Matching these keys is not
sufficient, so enumerate all adjacency-preserving bijections with
the required degrees, then all products of the two marked families.
This transports the planted marks under any unrooted catalogue
isomorphism; no restriction on host automorphisms is used.

After alignment the only unknown edges lie between Q_A and Q_B.
A potential edge with a common neighbour already present would form
a triangle and can never be present. Add every other possible edge to
form an upper graph; an independent (d+1)-set in that upper graph
persists in every completion. Lower codegree may not exceed M. Every
nonadjacent pair must have a common neighbour: if it did not, one
endpoint together with the d neighbours of the other would be
independent. When the pair consists of two fixed vertices, no future
edge can repair a violation. For a private vertex, every cross-row
choice must have the correct size, avoid triangles, obey the codegree
cap with fixed vertices and cover each unmet fixed vertex. Maintaining
row/column compatibility only removes choices inconsistent on a shared
edge. Edges missing from all choices in a row are then absent from its
upper graph. If deleting another edge from that upper graph exposes
an independent (d+1)-set, the edge is mandatory. Every such deletion
and forcing step preserves all genuine completions. These checks are
necessary, not a complete solver in general; unresolved maps would
remain open.

The sampled proof formulas instead encode only regularity, triangle
avoidance and independence, not the codegree cap. They have one
variable per possible private-side pair, with a negative unit if the
pair has a fixed common neighbour. For any row one includes negative
clauses for subsets larger by one than the deficit and positive clauses
for omissions that make the deficit unachievable. Two new edges of a
triangle must meet in a private vertex, and their opposite endpoints
must have a fixed edge; a negative 2-clause excludes this. Three new
edges cannot form a triangle, since the unknown-edge region is
bipartite. Every independent (d+1)-set of the lower graph requires
at least one new edge among its pairs; each such disjunction is encoded.
Therefore a checked UNSAT proof excludes the bound map even without
its cap. A map rejected by codegree alone is excluded only at that cap.

## Consequence for the codegree-five graph (hand, conditional on the join)

For d=9, t=3 and |V(G)|=40, inclusion–exclusion gives
`|F_A| = 10 + c(a0,a1)+c(a0,a2)+c(a1,a2) − |N(a0)∩N(a1)∩N(a2)|`.
If |F_A|=22 and M=5, its three pair codegrees are all five and its
triple has exactly three common neighbours, namely B. Conversely those
conditions on A yield |F_A|=22 with B defined by its common neighbours.
For this A the three neighbourhood masks of B in F_A have union at
least 12, and `|F_B| = 34−|Q_A|`. The exhaustive cap-five 22/22 join
rules out union 12, conditional on the complete order-22 class source
and the marked enumeration (`ROUND10_REPLAY.md`). The new *sample*
does not rule out union 13 in general. If a full 22/21 closure is later
obtained, it rules out both (opposite pair-codegrees 4,5,5 with three
triple neighbours) and (5,5,5 with four triple neighbours). These and
only these give |F_B|=21, by the same inclusion–exclusion equation
and t_B≥3. Equivalently, the B-masks in F_A have intersections
(1,2,2) and no triple point, or (2,2,2) and one triple point. None
of these deductions asserts that every R(5) graph has such a triple.
