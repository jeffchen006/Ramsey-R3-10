# The same labelled rectangle in two root restorations

**Scope.** Let `G` be a triangle-free 9-regular graph on 40 vertices with
`α(G)≤9` and codegree at most five. Let disjoint independent four-sets `A,B`
span all 16 edges between them. For a vertex set `U`, let `F_U` be the graph
induced by vertices outside `U` with no neighbour in `U`. Assume that exactly
two vertices outside `A∪B` have no neighbour in either side. The only
external graph-class facts used in the scan are `R(3,6)=18` and the seven
order-17 classes (`notes/DEPENDENCIES.md`, D-R1 and D-G3).

1. An exterior vertex cannot meet both `A` and `B` because that creates
   a triangle. Thus `F_A ∪ F_B` covers all 32 exterior vertices, and
   their intersection consists of the two neutral vertices `Z`. An
   independent six-set in either window would make ten with its defining
   four-set. Hence each window has order at most 17 and the two orders
   sum to 34: both are 17. Let `P_A` be the 15 private sites in `F_B`,
   which are the vertices meeting `A`; define `P_B` symmetrically.
2. The four marks on `F_B` are `N(a)∖B` for `a∈A`. These are independent
   five-sets whose union is `P_A`; their pair intersections have size at
   most one since the corresponding pair already shares all four of `B`.
   Each site of multiplicity `r` spends `r−1` of the five excess
   incidences and `binom(r,2)` of the six pair slots. A site of multiplicity
   four would alone spend all six slots but only three incidences; two
   triple sites would use all six slots and at most four incidences. Both
   are impossible. With no triple site, there are five double sites and
   their pair slots form `K4` minus one edge. Accordingly, the counts of
   singleton sites in the marks are `3,3,2,2`. With one triple site,
   the three remaining pair slots all join its marks to the fourth mark,
   so there must be one double site in each slot: the counts are `3,3,3,2`.
   All statements hold symmetrically on the opposite side. The potentially
   missing edges of `G` after identifying the two neutral sites and
   fixing both frames are precisely cross edges `P_A×P_B`; all edges
   within a window and all edges incident to roots are determined.
3. Fix `a∈A`. Put `S=N(a)∖(B∪N(A∖{a}))`, the singleton group in its
   mark. Then the vertex set of `F_{A∖{a}}` is exactly
   `V(F_A) ⊔ {a} ⊔ S`: every opposite root sees all three surviving
   roots, every other exterior vertex is unchanged unless it saw just
   `a`, and `a` itself is admitted. The neighbourhood of `a` in this
   restored window is exactly `S`. Deleting its closed neighbourhood
   restores the **same physical** `F_A`, including the same two neutral
   labels. The restoration has independence number at most six, since
   the surviving three roots are independent and anticomplete to it.
4. For `|S|=3`, write `M_x=N_G(x)∩V(F_A)` for `x∈S`. The only added
   edges are the root star and the rows `M_x`; `S` is independent. Each
   row must be independent in `F_A`. An independent set using the root can
   add at most five window vertices. One not using the root chooses
   some subset `J⊆S` and then an independent set of `F_A` avoiding
   `⋃_{x∈J}M_x`. Thus a package on the window fits the restored
   Ramsey graph iff each row is independent and
   `α(F_A−⋃_{x∈J}M_x)≤6−|J|` for every `J`. Repetitions of equal row
   masks are permitted. One may store unordered multisets, provided all
   distinct permutations are tried in physical singleton order. The
   known singleton edge to `a` consumes one degree; the known vertices
   of `F_B` outside `Z` and the row in `F_A` account for the other eight.
   Therefore
   `M_x∩Z=N_{F_B}(x)∩Z` and `|M_x|=8−|N_{F_B}(x)∖Z|`.
5. In the opposite restoration, a three-site singleton group `T` for
   a root `b∈B` gives rows `M'_y` on the same physical `F_B`.
   For `x∈S,y∈T`, `y∈M_x` and `x∈M'_y` are the very same edge.
   Build the two Boolean arrays in physical site order and transpose the
   second. A package whose array has no match in a current opposite
   domain cannot be the true package, provided all true packages had
   survived up to that step. Induction proves soundness of iterative
   deletions. This is only a necessary pairwise condition: the same
   package must be used in all its rectangles in any actual graph.

## Other necessary tests used in the pilot

- Identifying `Z` must agree on its edge; the degrees of a neutral site
  sum to `9+[Z is an edge]`, since the single shared edge, if present,
  is counted twice. The two known common-neighbour counts for `Z` sum,
  with no overlap. Total missing degrees on the two private sides agree
  because they count the same cross edges. Each side has 15 sites and 20
  incident root edges, so equality of missing degrees is exactly equality
  of the sum of the within-window degrees at the 15 private sites.
- A local package counts shared neighbours of a singleton with both
  neutral vertices, every opposite root, and other members of its own
  group. For neutral and same-group pairs, partition the count into
  known neighbours on the private origin side and those from the row on
  the destination window; in same-group pairs add the common root. For
  opposite roots count the intersection with their mark and the common
  singleton root. Each count is at most five.
- The terminal check maps private vertices to disjoint labelled slots and
  glues only `Z`. Given a package, all three full neighbourhoods are
  fixed. Among packages enforce literal edge symmetry; common
  neighbourhoods have size zero for adjacent vertices and at most five
  otherwise. If the lower (mandatory) graph exceeds the triangle or
  codegree restrictions, or the upper (possible) graph itself contains
  an independent ten-set, every intermediate graph fails. Individual
  degrees below the lower or above the upper are impossible. Lower
  degree nine forbids all remaining edges incident to that vertex;
  upper degree nine forces them. An edge forming a triangle with two
  mandatory edges is forbidden. These operations preserve every possible
  completion. An unresolved terminal state would not prove existence.

The pilot verifies these tests only on its bound roster. Neither a `K4,4`
nor a two-neutral marking is asserted to be necessary for all of Case R.
