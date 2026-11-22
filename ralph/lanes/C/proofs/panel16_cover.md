# One-neutral cap-five biclique: physical cover and packages

Let `G` be 9-regular, triangle-free, of order 40, with independence
number at most nine and codegrees at most five. Mark an induced
`K4,4`, and assume that exactly one vertex `z` outside it misses both
root shores. Each of the 32 exterior vertices other than `z` sees
exactly one shore: it sees at least one by definition, and seeing both
would give a triangle with a biclique edge. A window consists of all
exterior vertices avoiding one shore. Its independence number is at
most five because the avoided four roots can be adjoined. Thus both
orders are at most 17 by `R(3,6)=18`. Their sum is `32+1=33`; write them
in order **16, 17**, with private sizes **15, 16**. Each window carries
the marks of the four roots on the shore it *meets*, not of the shore
it avoids. Only the shared `z` is identified. There is no exchange
quotient inside this ordered domain.

## Shapes on the two shores

The marks are the four independent five-sets of a root's exterior
neighbours. They cover the private sites. Two marks intersect in at most
one site because the roots already share the entire opposite root
shore. An `r`-fold site spends `r-1` incidence excess and occupies
`binom(r,2)` pair slots which no other site can use. Incidence excess
is five on the 15-private side and four on the 16-private side.
Multiplicity four uses all six slots but just three excess, and is
impossible on both sides. Two distinct triple sites would repeat a
pair slot because any two triples of four marks intersect in at least
two marks. The remaining possibilities are:

| Private size | Triples | Doubles | Pair-slot pattern | Sorted singleton sizes |
|---:|---:|---:|---|---|
| 15 | 0 | 5 | `K4` minus one edge | `2233` |
| 15 | 1 | 3 | all three slots from the triple to the outsider | `2333` |
| 16 | 0 | 4 | `K4` minus two incident edges | `2334` |
| 16 | 0 | 4 | `K4` minus a matching | `3333` |
| 16 | 1 | 2 | two of the three slots from the triple to the outsider | `3334` |

In the no-triple rows, subtract each mark's slot degree from five.
For the triple rows, subtract one more from each mark meeting the
triple, then subtract the incident double slots. No shape is pruned
for its number of size-three groups. The pilot enumerates the singleton
groups of **all** sizes two, three and four, not just the triples.

## Header and frame cover

The order-16 and -17 `(3,6)` catalogues are the published 2,576 and 7
isomorphism classes (D-G3b/D-G3). Pick any isomorphism from a physical
window to its catalogue representative. In that representative record
the actual neutral site and the four marks, sorted as masks merely to
rename roots. Tests that the marks are independent and intersect at
most once are justified above. A host site’s window degree plus mark
multiplicity counts known neighbours, and is at most nine. A site's
neighbours in a given mark count known common neighbours with its
root. Two host sites have their window common neighbours and their
shared marked roots as disjoint sets of known common neighbours. Both
known counts are bounded by five. These tests preserve the physical
frame. There are no missing edges except between private sides.

Write `D_q` for the sum of window degrees on its `q-1` private sites,
and `d_q` for the degree of `z` in that window. The total missing
crossing degree there is `9(q-1)−20−D_q`, because exactly 20 root
incidences are already counted. The missing degree sums count the
same crossing edges. Thus `D_17=D_16+9`. The disjoint contributions
to the neutral degree require `d_16+d_17=9`. These are the two header
equalities. The two labelled frames and one neutral identification
are present in the unquotiented compatible header inventory. The
dispersed pilot samples that inventory; it does **not** claim that
every physical target is among the sampled IDs.

## Restoration and exact labelled join

Fix a root `a` on the shore meeting the source window. Let `S_a` be
the sites in its mark but in no other mark. All other exterior sites
are either in the opposite window (they miss the whole root shore) or
meet a surviving root in that shore. Every opposite root meets all
three surviving roots. Consequently, after removing the closed
neighbourhoods of the other three source roots, the remaining induced
graph is exactly the opposite physical window together with `a` and
`S_a`. Its independence number is at most six: adjoin the three
removed roots. The new graph consists of that window, the independent
sites in `S_a`, the edges from `a` to `S_a`, and the rows
`M_x=N_G(x)∩V(opposite window)` for `x∈S_a`.

Each row is independent by triangle-freeness. With the neutral mapped
to the neutral in the opposite window, `M_x` contains it precisely if
the source window has `xz`. Moreover
`|M_x|=8−|N_source(x)\{z}|`: count the root neighbour of `x` and the
known private neighbours in its source window. For every nonempty
`J⊆S_a`, the independence bound is exactly
`α(opposite window − union(M_x for x∈J))≤6−|J|`, since the selected
singleton sites can be adjoined. The case of no singleton follows
from the window bound, and one can use at most six sites if using
`a`. These conditions remain necessary and sufficient for the restored
graph alone. Ordered packages retain all assignments, including equal
rows when legal. The smaller analogue with regular degree `d`,
independence cap `b` and `r` roots per shore uses degree `d−1` in
place of eight and restoration cap `b−r+1` in place of six.

For any pair of opposite singleton groups, the two purported
rectangles must agree entry by entry: these are the same physical
edges. A true package always has a supporting opposite package for
every group, so iteratively removing packages without a matching
rectangle never removes a physical completion. Within a complete
assignment all rectangles must agree simultaneously. A literal join
and a join after this pairwise filtering therefore return exactly the
same assignments, regardless of pruning order. Placements from
different groups on the same shore fix disjoint rows, and placements
from opposite shores agree on the intersection by the join. Other
crossings can be left unknown. The terminal uses only necessary
degree / triangle / codegree / independent-set conditions on the
resulting lower and upper graph, detailed in the pilot report.

### Exact existence cache (not a join cache)

For one group, with the destination host and its neutral label fixed,
the only data imported from the source are the required size and
neutral bit of each row. Permuting these data permutes the row slots,
and also bijects the subsets tested in the restoration condition. Thus
the truth value of “there exists a package” depends only on the
destination host, its neutral, and the **multiset** of its group's row
demands, with the run's parameters fixed. This proves the cache key.
Stopping at the first valid package gives that truth value; to record
false, the ordered enumeration must finish. This result does not
identify packages on different physical singleton site labels and
does not allow using one cached representative for rectangle joins.

### Terminal rejection and independent binding

After a joint assignment, let `L` contain every known edge and `U`
contain all edges not known absent. The labelled rectangle equalities
allow the assignment to fix each of its crossings consistently in
both directions, so a physical graph represented by the assignment
satisfies `L ⊆ G ⊆ U`. A degree excess in `L`, shortage in `U`, or
an edge of `L` absent in `U` contradicts regularity or containment.
A triangle or a cap violation in `L` persists in `G`. An independent
ten-set in `U` remains independent in `G`. Remove any unknown edge
that would close a triangle with two edges of `L` or exceed an already
saturated lower degree. Force any upper edge incident to a site whose
upper degree equals nine. These steps preserve containment, so all
rejections are necessary; surviving is not a positive answer.

The separate Python package generator computes the same subset test
by enumerating all independent sets of the forbidden size and checking
that the union hits each one, rather than using the C++ subset alpha
recurrence. Its exact join indexes packages by their bits on crossings
already fixed by previous groups: a shared bit must have the same value
in both assignments, and all and only such matches are traversed.
Induction on the group index proves equality with the literal labelled
join. Python separately reconstructs bounds from the labelled geometry
and runs a set-based terminal, including a separate independent-set
search. The pilot happens to have no target terminal assignments;
the smaller positive controls check both terminal implementations.
