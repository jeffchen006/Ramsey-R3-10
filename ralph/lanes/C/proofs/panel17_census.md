# Cover of the cap-five biclique with two neutral sites

Let `G` be 9-regular on 40 vertices, triangle-free, with `α(G)≤9` and
all codegrees at most five. Let disjoint independent `A,B` span an
induced `K4,4`, and let `Z` be the exterior vertices with no neighbour
in `A∪B`. No exterior vertex can meet both sides since each edge
between the sides would then lie in a triangle. The two windows `F_A`
and `F_B` (closed antineighbourhoods of `A` and `B`) therefore have
union the 32 exterior vertices and intersection `Z`. Each has
independence number at most five by adjoining the independent four-set
it avoids. By `R(3,6)=18`, their orders are each at most 17, so
`|Z|≤2`, with `|Z|=2` equivalent to orders 17/17.

Assume `|Z|=2`. The justification for the row packages and all the
rejection rules is in `reciprocal_panel17.md`. The following shows
that the finite scan does not depend on picking a particular labelling:

1. Independently identify each physical window with a representative
   from the complete seven-class order-17 `(3,6)` catalogue (D-G3).
   This gives four distinct independent five-subsets in each host,
   their union all private sites. The exact mathematical predicate
   implemented in `legal_frame` additionally checks the following:
   each two marks intersect in at most one point (the corresponding
   roots share all four opposite roots); a site's degree plus its mark
   incidence count is at most nine; for a site and a root, the site's
   within-window neighbours in that root's mark number at most five;
   for two window sites, their within-window codegree plus the number
   of marks common to both is at most five. Each tested count is a
   count of actual neighbours or common neighbours. Thus the mark
   collection is in the inventory. Sorting marks just renames their
   roots. The two inventories may use the very same host or same
   frame ID: their private vertices and roots remain disjoint.
2. Each window has an increasing order on its two physical neutral
   labels. Identification of equal physical neutral sites is one of
   exactly two maps. Both maps and every ordered frame pair are
   considered, without symmetry quotient. `reciprocal_panel17.md`
   shows the four header tests are necessary: equality of private
   window degree sums, agreement on the neutral edge, two neutral
   degree sums with the shared edge counted only once, and the
   neutral codegree upper bound. Thus a candidate induces at least
   one header-passing alignment.
3. For each restored three-site star, all three rows of an actual
   alignment occur as a literal multiset in the regenerated atlas:
   enumerate independent sets of size below six and use the exact
   independence table on the complements of row unions as justified
   in `reciprocal_panel17.md`, step 4. All permutations are tried.
   All true choices simultaneously pass local and transpose tests
   and hence reach the terminal enumeration with their compatible
   fixed neighbourhoods. In particular, rejection of *every* joint
   filling by exact necessary propagation rules eliminates that
   alignment. Counting or arc consistency alone would not suffice.

It follows that an exhaustive run with no unresolved terminal filling
excludes `|Z|=2` for such a marked biclique. Equivalently, every `K4,4`
in a hypothetical cap-five regular example dominates all but at most
one vertex. This conditional result neither forces a biclique to exist
nor excludes one with zero or one neutral site, cap six, or cap seven.
