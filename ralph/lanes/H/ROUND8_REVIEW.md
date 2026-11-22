# Round 8: scoped P3 and paired-window hypothesis audit

## C: diagonal-four P3, 8/8 arms, two exact layouts

This is a **different branch** from C-025's isolated pair with global
`f*=9`. Here `G` is 9-regular under the codegree-six cap, the three
marked roots form the codegree-six P3 (using C's structure result),
their diagonal has codegree four, and both arms have cross count
eight. A residue vertex has 3–5 neighbours in the deleted boundary:
its residue has order 22 and alpha at most six, so its degree in
the residue is at most six and at least four (otherwise its own
antineighbourhood has order at least 18 and alpha at most five).
The cap five on overlap with each marked root's neighbourhood also
needs that the three roots form a whole component; a bare marked
span without that conclusion would not justify the mask test.

`check_p3_singleton_binding.py` directly builds the two deleted
graphs from literal edge sets, with no import of C's classifier or
independence search. It enumerates all 9-set witnesses and every
3–5 attachment subset; verifies the four padded independent 8-set
blockers for every tag in the four common neighbours; and binds
the exact boundary/graph6 digests and row IDs to McKay's pinned
191-class source. Comparison: 0 zero-T masks in each layout, and
112/105 singleton masks per tag for matrices 1/3. In both layouts
0 hit all four blockers, whereas 17 hit the first three alone.
The smaller planted C21 independently passes triangle/alpha and
the appropriate mask tests (8 residue vertices, two zero-T masks
and six singleton masks), so zero masks are not silently discarded.
Missing, duplicate and crossed-boundary receipt controls fail.

Each blocker can be avoided by at most one actual vertex with that
singleton tag. Indeed two such vertices share its common neighbour
and are nonadjacent to each other; together they extend the padded
eight-set to ten. Thus at most 16 actual singleton vertices exist.
Conversely the four tags each send six edges to X; with no zero mask,
24 incidences on 22 vertices require at least 20 singleton vertices.
The bound rules out exactly matrix 1 with hole labels `(0,1),(0,1)`
and matrix 3 with the same hole labels. Their boundary digests bind
30 e62 and 60 e63 receipts respectively, **not** the full e62/e63
strata. The result is hand + enum; not LRAT and not a global P3 bound.
The separate weighted-capacity search is not part of this audit.

## G: lower paired and mixed completion hypotheses

Use the accepted e168 degree-six floor and exterior min-degree
bridge, two adjacent degree-six roots, and their exact unique
strip cross edge. The path/leaf centre has degree seven, sees one
root and six X vertices, and is not cross. A noncross mixed pivot
has degree eight, sees one root and seven X vertices, and has exactly
one missing double pair incident to it. To see the latter use
`degree = 9 - (number of incident holes) + [cross]`. The matching
role leaves three noncross d8 choices if the cross is incident to a
hole; the middle role leaves two. The pivots are distinct and
nonadjacent, with all common neighbours in X. Deletion gives alpha
at most seven by adjoining both pivots to any independent set of T,
and order `24+j` (7/7) or `23+j` (7/8), where `j` is the shared
open-neighbourhood size. This uses no MTF property of T. An order-25
T of minimum degree 2 or an order-26 T of minimum degree 3 has a
22-vertex `(3,7)` antineighbourhood at a minimum-degree root.
Using the same core census for those orders at higher minimum degree
would lose coverage; the order-27 source also does not replace it.

On each retained four-column side, the pivot and its common/own
exclusive neighbours were cut. Every missing incidence signature
on that side therefore belongs to an opposite-exclusive vertex,
with one whole signature per such vertex (no split by coordinates).
Sorting the two signature multisets only permutes disjoint deleted
classes whose internal adjacencies are not chosen, so no completion
is lost. The mixed four-column side uses five doubles rather than
six. Its remaining hole must be represented explicitly; the hole
incident to its pivot must be disjoint from the other hole for a
matching, or intersect it specifically at the star for path/middle.
These conditions preserve the degree profile and are not interchangeable
with making a particular unspecified noncross vertex the other leaf.

`strip_completion.py` uses exact degree selectors for exterior
vertices: in the two path/leaf branches `(d7,d8,d9)` is `(6,0,22)`
or `(5,2,21)`; in the mixed branch `(6,0,22)`. In either setting
a degree-seven exterior vertex must have singleton support to both
strips or one degree-six residue would have degree five there.
Among the deleted X vertices, all pairs other than opposite-exclusive
pairs share a pivot and are absent. For paired centres the optional edge-budget
row counts a d7 deficit twice, d8 once and d9 zero, plus edges across
the two exclusive groups. These are the only exclusive cross terms
in the deletion identity, independent of how the remaining unknown
edges are solved.

In either program, an eager clause uses `s=6` or `7` distinct
vertices of T, `9-s` distinct vertices exclusive to one pivot, and
the other pivot, which is adjacent to neither group. All ten labels
are distinct and every completion must have an edge among them;
omitting fixed-absent literals is valid, a fixed-present literal
makes the clause redundant, and truncation only weakens the
relaxation. The paired loop has no triples when the exclusive group
is already too small; this is not a dropped case. This audit checks
necessity of the encodings, not proofs, scan completeness, or receipt
finality. A/G retain those responsibilities.

## Lean boundary

`R310.CompletionBridge` proves preservation under one domain shrink
and a sequence of shrinks, plus paired-window order/alpha and the
order-22 rooted-core bridge. Compatibility of a genuine completion
and the no-support deletion condition are hypotheses, not facts
proved about the C executable. The window theorems assume the pivot
conditions; they do not enumerate the graph6 catalogues, verify
roles or any SAT proof, or rule out any Ramsey case.
