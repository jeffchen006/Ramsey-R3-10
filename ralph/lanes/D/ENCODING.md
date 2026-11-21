# Lane D: fixed edge kernels

## A cover independent of nauty (`hand` argument; `enum` instance)

Use the edge-kernel cover in `paper/latex/sec8.tex`: some edge in R(3) has a
bipartite kernel F on two specified 8-sets of maximum degree 2, with
matching number at least 7 and at most 13 edges. Every component of F is a
path (including an isolated vertex), or an even cycle of length at least 4.
The color-preserving type is specified by `(left vertices, right vertices,
path or cycle)`; paths alternate, and either side can be the larger color
class of an odd path. In each component a matching of size the smaller color
class is obtained by alternating edges, and no matching can be larger. Thus
matching sizes and edge counts add, and the complete color-preserving
isomorphism invariant is the sorted multiset of component types.

Enumerate that multiset with total color sizes `(8,8)`, matching at least 7,
and edge count at most 13. Replacing the multiset by the lexicographically
smaller of it and its color swap is sound: swap the orientation of the
rooted edge, then relabel both neighbor blocks. This proves coverage by
the resulting components, not a disjoint partition of unrooted graphs
(one graph can extend different kernels). It is an exact partition of the
admissible rooted edge kernels up to isomorphism and root swap.

Independent multiset enumeration in `catalogue_m3.py` checks all graph6
representatives in the nauty catalogue: 238 colored types and 166 up to
side exchange. A smaller 3+3 catalogue has 12 colored and 10 uncolored.
Evidence: `scratch/D/catalogues/component_check.log`; the exact 166-rep file
is `scratch/D/catalogues/R3_unoriented.g6`.

## CNF modes (`hand` soundness sketch, not link (a) certification)

An edge is represented by its SMS row-major variable. Fix the kernel
pointwise and assign all edges in it, including edges and nonedges from
the two roots to every other vertex. The outside block may be permuted.
The `fused` variant substitutes these constants in the triangle, degree
and codegree formulas. It uses one conjunction for each potential common
neighbor and a shared bidirectional threshold totalizer for positive
codegree on nonedges and maximum codegree. Every gate is an equivalence,
and the unit thresholds impose the bounds. The `base` mode instead uses
the original Sinz formula and appends kernel units.

The `local` variant adds valid eager constraints over the fixed kernel:
if an independent kernel seed I has size k−1, every outside vertex hits I;
if its size is k−2, outside vertices avoiding I form a clique (hence size
at most 2 since G is triangle-free); for k−3, at most 5 avoid I by
R(3,3)=6. The avoid indicator means none of the vertices in I is adjacent.
SMS still lazily enforces all independent-k-set clauses. The clauses only
supply short projections of independent-set restrictions that would
otherwise be found one full set at a time.

The `profile` variant adds the sum of codegree thresholds ≥2 through M
at each vertex: `d(d−1) − (n−1−d)` by 2-walk counting, since nonedges
have positive codegree. It also enforces the known singleton-codegree
matching condition in each neighborhood: if distinct `x,y,z` are all
adjacent to `w` and `c(x,y)=c(x,z)=1`, then `(N(x)−{w}) ∪ {y,z}` is
independent of size `d+1`. In particular, any x has at most d nonneighbors
of codegree 1, since their unique common neighbors with x must differ.

For `minedge`, it suffices to test completions rooted at an edge minimizing
the number of 4-cycles containing the edge. This adds necessary conditions
not imposed on an arbitrary rooted graph, and must preserve the root under
symmetry. For edge `uv` and adjacent `ua`, the 4-cycles on `ua` number
`sum_{w∈N(a)−{u}} (c(u,w)−1)`: each w is opposite u on exactly that many
cycles containing `ua`. Requiring this number to be at least `|E(F_uv)|`
for edges at the two roots is valid (we do not enforce global minimality).
For M=3 only, write L=n−1−d and h1(v)=number of nonneighbors with c=1.
If h2/h3 count the others, `h1+h2+h3=L` and `h1+2h2+3h3=d(d−1)`.
The number of 4-cycles at v is `h2+3h3=2d(d−1)−3L+h1`. Summing cycle
counts over the d edges incident to v counts each such cycle twice.
Thus choosing a root of minimum count `m=|E(F_uv)|` implies
`h1(v) ≥ ceil(dm/2) − (2d(d−1)−3L)` for EVERY vertex, even though the CNF
only compares root-adjacent edges explicitly. At (40,9,3), m=13 forces
`h1(v) ≥ 5`. On the LP projection this gives a linear inequality at
each root: `#isolates(opposite side in F) + sum_{|M∩own side|=1} p_M ≥ 5`.

## Boolean outside-mask projection (`hand` necessity, not sufficiency)

Let T(x) be the set of neighbors of an outside vertex x in A∪B. MTF
implies both sides occur. If two outside vertices have the same mask of
size at least 4, their codegree is at least 4. If they share a mask of size
at most 3, one root side is a singleton `{a}`. For that root u, both
vertices avoid `N(u)−{a}` and are nonadjacent to each other (they share
neighbor a). This gives an independent (d+1)-set. Thus **every outside
mask has multiplicity at most one** when the maximum codegree is ≤3.

`mask_sat.py` encodes C's projected rows with a Boolean variable per mask.
Base rows count order, degree and codegree; `--min-edge` also adds the
endpoint minimum-edge rows and the above root singleton floors. A sparse
variant makes the residue order, residue degree, and shared mask rows
lazy. A violated unit-coefficient upper bound is explained by any set of
`bound+1` selected masks in its support. Other lazy cuts compare required
and allowed outside edges:

- Outside edges between intersecting masks are forbidden by triangles.
  If a kernel nonedge between an outside mask T and an inner vertex z
  already has M common neighbors in the kernel, neighbors of T outside
  cannot contain z either. Apply both directions.
- Two outside masks that both avoid an independent kernel (d−1)-set must
  be adjacent. Count such forced edges against remaining degrees, reject
  mandatory forbidden edges and triangles, and count forced common
  neighbors against codegree caps.
- Every nonedge must have a common neighbor. If none is inside the
  kernel, the required outside witness must be eligible as an edge
  partner to both endpoints.
- Form the possible-edge supergraph from the fixed kernel, the chosen
  masks, and all allowed outside edges. A completion is a subgraph of it.
  An independent (d+1)-set in the supergraph therefore yields a blocking
  clause using only the selected outside masks in that witness. The
  kernel part is already fixed and no absent mask is assumed.

An UNSAT relaxation is a route to excluding a rooted kernel. A SAT
projection is not a Ramsey graph. The solver's assembler and the lazy
cut generator aren't independently certified. The experimental DRAT
option re-solves a frozen clause list with a fresh prover; it cannot certify
the encoding or lazy clause premises by itself.

## Proof status

`check_trace.py` verifies the original trace clauses against input, all
lazy independent-set clauses and the checked symmetry witness clauses;
checks that each witness fixes the kernel pointwise; independently checks
the lex step with `check_sb.py`, optionally again with Lean `sbcheck`;
then checks LRAT with CakeLPR. The initial smoke test is a negative C22
kernel (0 solutions, 20 witnesses, `scratch/D/cal22_proof/k0000.checked`),
and kernel 0 of R(3) also passed (0 solutions, 812 IS, 249 SB, including
Lean symmetry check, `scratch/D/r3_proof/k0000.checked`).
The input-CNF encoding link from a verified semantic specification via
VeriPB/CakePB is not yet built. A checked LRAT here is not an end-to-end
`cert` claim. Enumeration blocking clauses (if any models were found)
are not accepted by the proof-checker as valid theory clauses.
