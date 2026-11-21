# Structure of the codegree-six graph in the regular case

**Status:** hand, conditional only on the usual Ramsey upper bounds. Let G
be a 9-regular triangle-free graph on 40 vertices with alpha <= 9. Define
J on the same vertices by joining pairs of codegree six in G. An edge of J
is always a nonedge of G. Then:

- Every length-three path of distinct vertices in J has endpoints adjacent
  in G and both diagonals of codegree three in G.
- Every component of J is a path on at most ten vertices (including an
  isolated vertex), or a cycle of length eight.
- A vertex with two J-neighbours of mutual codegree four or five lies in
  a path component on exactly three vertices.

## Two neighbours and four consecutive vertices

For two J-neighbours p,q of x, each has six neighbours inside N(x), so
they share at least three and are nonadjacent. In H=G-N[x] they have degree
three. Their H-neighbourhoods are disjoint: if they intersected, removing
their closed neighbourhoods from H would leave at least 23 vertices with
alpha <= 6, contrary to R(3,7)=23. In particular N(p) intersect N(q) is
contained in N(x). As in Sec. 8 of the report, three such neighbours
would have mutually disjoint H-neighbourhoods; deleting the three closed
neighbourhoods would leave 18 vertices with alpha <= 5, contrary to
R(3,6)=18. So J has maximum degree two.

Take four consecutive distinct path vertices v0,v1,v2,v3 of J and abbreviate
N_i=N(v_i). Put r=|N_0 intersect N_2|, s=|N_1 intersect N_3|,
t=|N_0 intersect N_3|, a=|N_0 intersect N_1 intersect N_2 intersect N_3|.
The preceding paragraph gives N_0 intersect N_2 contained in N_1 and
N_1 intersect N_3 contained in N_2. Hence triple intersections 012 and
123 have sizes r and s, and triple intersections 013 and 023 both equal
the fourfold one. By inclusion-exclusion,

    |N_0 union N_1 union N_2 union N_3|
      = 36-(18+r+s+t)+(r+s+2a)-a = 18-t+a <= 18.

If v0 and v3 were nonadjacent, these four vertices would be independent
(the two diagonals are nonedges by the preceding paragraph). At least
40-4-18=18 vertices would avoid the four closed neighbourhoods, with
alpha <= 5. This contradicts R(3,6)=18. Thus v0,v3 are adjacent, so N_0 and
N_3 are disjoint. Inside the six-set N_1 intersect N_2, the sets N_0
intersect N_2 and N_1 intersect N_3 are disjoint and both have size at
least three. They both have size exactly three, and partition it. This
also proves the assertion about codegree-four/five diagonals: if a
two-edge J path with such a diagonal could extend to a four-vertex J
path at either end, its diagonal would have to be three. A triangle of
J is excluded by `bicliques.md` (or by combining the containment for a
double neighbour with the K3,6 obstruction).

## Three-set decomposition and length bound

Consider a path of distinct vertices v0,...,vL with L >= 3. For
1 <= i <= L-1 put D_i=N_{i-1} intersect N_{i+1}. By the previous section
each D_i has size three and is also contained in N_i. Every interior edge
v_i v_{i+1} of J (1 <= i <= L-2) has

    N_i intersect N_{i+1} = D_i disjoint-union D_{i+1}.

For 2 <= i <= L-2 the intersection of this six-set with the corresponding
six-set on the preceding edge is exactly D_i (triple intersection).
Thus D_{i-1},D_i,D_{i+1} are pairwise disjoint and fill N_i. At the left
end put D_0=N_1 minus (D_1 union D_2). Because N_0 intersect D_2 is empty
(it is contained in D_1 intersect D_2), the six-set N_0 intersect N_1
is D_0 disjoint-union D_1. Put D_{-1}=N_0 minus (D_0 union D_1). Repeat
the endpoint definitions at the right for D_L,D_{L+1}. This proves for
every 0 <= i <= L:

    N_i = D_{i-1} disjoint-union D_i disjoint-union D_{i+1}.

For 0 <= i <= L-3, v_{i+3} is adjacent to v_i but nonadjacent to
v_{i+1} (distance two in J). Both D_i and D_{i+1} are contained in
N_{i+1}. It follows that v_{i+3} is in D_{i-1}. Thus D_j contains
v_{j+4} for -1 <= j <= L-4. Reversing the path shows D_j contains
v_{j-4} for 4 <= j <= L+1. Because D_j is contained in the three
consecutive N-sets at j-1,j,j+1 wherever those indices exist, all pairs
at distance five along the path are adjacent in G. All pairs at distance
four are also adjacent when L >= 5: for a pair (i,i+4) with i <= L-4,
use D_i when i <= L-4 and it has a forward v_{i+4}, or use D_{i+4}
and the reversed statement. In fact D_i works for every such i, including
the endpoint blocks. Distance-three pairs were proved earlier. Distances
six through ten are then nonedges (each gap is the sum of two from
{3,4,5}, giving a two-edge walk, and G is triangle-free).

Suppose L >= 10 and restrict to v0,...,v10. The six vertices
v0,v1,v2,v8,v9,v10 are independent: within either triple the gaps are
one or two, and between them the gaps are six through ten. Their N-sets
are the union of the ten three-sets with indices -1..3 and 7..11.
For each j=-1,..,3, D_j and D_{j+8} both contain v_{j+4}. The five
index pairs are disjoint, so bounding each pair's union by five gives
total order at most 25. Outside the six roots and their neighbourhoods
remain at least 40-6-25=9 vertices with alpha <= 3, contradicting
R(3,4)=9. Hence there is no eleven-vertex path in J.

## Cycle possibilities and the eight-cycle seed

The graph J has maximum degree two, so its components are paths or
cycles; any cycle longer than ten would contain an eleven-vertex path.
A triangle is excluded above. Cycles of length four or five are excluded
by the length-three path result, since their corresponding endpoints
are at cyclic distance one or two (nonadjacent in G). Cycles of length
six or seven are excluded by the forced distance-five edge along a
five-edge path for the same reason. In a nine-cycle the vertices at
positions 0,3,6 make a triangle in G (three distance-three edges).
In a ten-cycle positions 0,3,6 make a triangle (cyclic gaps 3,3,4, using
a six-vertex path to force the distance-four edge). Thus only the
eight-cycle remains possible among cycles.

For such a cycle v_i with indices modulo eight, define D_i as above
with cyclic indices. The partition of N_i still holds, as does
v_{i+4} in D_i. Consecutive D-blocks up to gap two are disjoint by the
partition of a single N-set. Blocks at gaps three or four are disjoint
by belonging to N-sets of vertices at gap three: for a gap three use
N_{i+1},N_{i+4}, and for a gap four use N_i,N_{i+3}. Hence all eight
D_i are pairwise disjoint. The induced graph on the eight roots has
exactly the edges at cyclic distance three or four; distances one and
two are nonedges and there are no other distances. Each D_i consists
of v_{i+4} and two nonroot vertices, each of which is adjacent to exactly
the three roots at cyclic positions i-1,i,i+1 (it belongs to no other
D-block). Write B for the sixteen nonroots in the blocks and X for the
sixteen vertices outside the blocks. Consecutive triples of roots are
independent, so alpha(X)<=6. The eight roots induce twelve edges. Once
the roots are removed the remaining graph has 180-(72-12)=120 edges;
each vertex of B has remaining degree six. Thus e(X)=24+e(B), and
since X is triangle-free with alpha<=6, initially e(X)<=48.

For each i take the independent triple of roots v_{i-1},v_i,v_{i+1}.
Its closed-neighbourhood complement is X together with the six nonroots
in D_{i+3},D_{i+4},D_{i+5}. The three leftover root members of these blocks
are precisely the triple itself, which is removed. The six nonroots are
independent since any two of these blocks share a common root neighbour.
These eight 22-vertex graphs are in R(3,7;22), so each has maximum degree
at most six. For x in X its nine neighbours are all either in X or in B.
Each 22-vertex graph thus omits at least three of its B-neighbours. Every
vertex of B is omitted in five of the eight graphs. Summing gives
5*d_B(x)>=8*3=24, hence d_B(x)>=5 and d_X(x)<=4. Therefore e(X)<=32 and
e(B)<=8. In particular any of the eight R(3,7;22) residues exhibits an
independent six-set whose deletion leaves a (3,7;16) graph of maximum
degree four and edge count in [24,32]. Every six-set vertex b in that
residue has degree d_X(b) and contributes 6-d_X(b) to the total degree
sum 2*(e(X)-24) in B. These are necessary seed constraints and do not
yet exclude the eight-cycle.
