# Necessary linear mask-count rows for regular edge extensions

**Status:** hand; the underlying Ramsey upper bounds are premises from
`notes/DEPENDENCIES.md` (D-R1/Table of Ramsey numbers), not recomputed here.

Let G be a simple triangle-free graph of order n, regular degree d, and
independence number at most d. Let c be an upper bound on the codegree of
every nonadjacent pair. Root at an edge uv. Set A = N(u) minus {v},
B = N(v) minus {u}, F = G[A union B], and K = G[{u,v} union A union B].
Triangle-freeness makes A and B disjoint and independent. Thus F is
bipartite of two parts of size d-1, and it determines K: add u adjacent
to A and v, and v adjacent to B and u, with no other edges. Let X be the
complement of V(K) in V(G), of size n-2d.

## Columns

For x in X write M(x) = N(x) intersect V(K), a subset of A union B
since x is not adjacent to either root. M(x) is independent in K by
triangle-freeness. In any graph here every nonadjacent pair has a
common neighbour: if x and y were nonadjacent and had no common
neighbour, N(x) union {y} would be independent of size d+1. For each
root this gives 1 <= |M(x) intersect A| <= c and 1 <= |M(x) intersect B| <= c.
Finally M(x) must meet each independent d-set I in K; otherwise I union
{x} is independent. If K itself has an independent set larger than d,
the kernel has no extension. Make one nonnegative variable p_M for each
mask satisfying the stated column constraints. Any extension supplies
p_M equal to the number of vertices x with M(x)=M.

## Rows

1. **Order and degree.** Sum of all p_M is n-2d. For every z in A union B,
   the sum over M containing z is d minus deg_K(z), as this sum counts
   exactly the neighbours of z in X. The two roots already have degree d.
2. **Private neighbours.** For a in A, any two vertices in X with
   M intersect A = {a} are nonadjacent (both are neighbours of a) and
   can be added to N(u) minus {a} to get an independent (d+1)-set. Hence
   the sum of p_M for these masks is at most 1. The B case uses v.
3. **Codegrees.** For a nonedge zw of F (including pairs in the same part),
   its codegree is the number of common neighbours in K plus the sum
   of p_M for M containing both z and w. This lies between 1 and c.
4. **Ramsey residue.** Let I be independent in K, t = d-|I| >= 1, and
   L = V(K) minus I and its neighbours in K. The induced subgraph of G
   on L and the vertices x in X with M(x) disjoint from I is triangle-free
   with independence number at most t, since each independent set there
   can be joined to I. Thus |L| plus the sum of p_M over masks disjoint
   from I is at most R(3,t+1)-1. The implementation uses only t up to a
   configurable small depth.
5. **Residual degree.** For each z in L intersect (A union B), its
   neighbours in the residue of row 4 are an independent set in that
   residue. Thus deg_{G[L]}(z) plus the sum of p_M over masks disjoint
   from I and containing z is at most t. This row holds even when the
   Ramsey row alone permits more vertices.
6. **Expanded stars and shared masks (`--strong`, proposed by lane D).**
   If z is not in L, one can still bound the number of X-neighbours of
   z in the residue by t: they form an independent set in the residue
   whether or not z itself belongs to it. Here no term deg_{G[L]}(z)
   can be added. It suffices to test z outside I, as no mask in the
   residue touches I. Also for every (c+1)-set S in A union B the sum of
   p_M for M containing S is at most 1. Two such vertices in X would
   be nonadjacent (they share a neighbour) yet have codegree > c.
7. **Minimum-edge witness (`--min-edge` only).** Choose uv whose F has
   globally minimum size g, which is possible in any graph here. For
   a in A, the edge ua has rooted cross graph between N(u) minus {a}
   and N(a) minus {u}. Each b in N_F(a) contributes deg_F(b) edges: b
   sees the root v plus its F-neighbours other than a. Each x in X
   adjacent to a contributes |M(x) intersect A|-1 edges, because
   x does not see v. These contributions account for all edges of the
   cross graph and sum to at least g. The B case follows by swapping
   the roots. This pruning is conditional on the kernel being a
   globally minimum-edge witness. It is not an absolute nonextension
   result for any F rejected only by these additional rows.

## Exact refutation format

All rows are encoded as A p <= b with integral coefficients; equalities
are encoded by two opposite rows. Number the rows in generation order
starting at 0. For a fixed labelled F, a refutation lists pairs (row,
positive integer weight). Add the weighted rows. If all resulting
coefficients are nonnegative and the resulting right-hand side is
strictly negative, there cannot exist p >= 0. Float-based discovery is
not a premise: the verifier regenerates the columns and rows from F
and uses integer arithmetic for both tests. Feasible projected solutions
are not necessarily graph extensions. This lemma makes no claim that
the kernel list covers a case; case R(3) uses the separate edge-kernel
cover in `paper/latex/sec8.tex`.
