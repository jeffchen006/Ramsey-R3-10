# Independent review of the path-window reduction — November 21, 2026

**Label: hand.** This reviews the geometric and graph-theoretic cover in
`ralph/lanes/C/proofs/path_windows.md`. It does not independently enumerate
the census joins, prove census completeness, or close R(6).

## Four roots

The middle pair deletes 14 vertices: two roots, distinct from all four
three-sets D0 through D3, and four disjoint blocks. In the residual A the
outer roots are adjacent and have degree 3. In fact, v0's ambient neighbours
consist of D(-1), D0, D1; D(-1) is disjoint from N(v1) by that
decomposition and disjoint from N(v2) because N(v0) ∩ N(v2) = D1.
The reverse argument gives D4 at v3. Neither exterior block meets the
middle roots, by the nonedge statements at distances 1 and 2. The two
exterior blocks are disjoint by triangle-freeness. Each includes the
opposite root. The remaining two vertices on each side form independent
wings, and the complement of the two exterior blocks in A has order 20.
Deleting one endpoint's closed neighbourhood in A leaves precisely that
overlap with the opposite wing. These set identities hold with possible
additional J-neighbours outside the four-root span.

Both triple windows have alpha at most 6: an independent set in either
can add its independent triple. Inside either wing the two vertices
have a common neighbour in the deleted opposite root, so their codegree
in that window is at most 5 under the global cap 6. This restriction is on
the marked pair only. Given the overlap with both ordered wing lists,
the only unset pairs are the four cross edges. Permitting any of those
whose ends have disjoint X-neighbourhoods is exhaustive and does not
insert a triangle with X; the other vertices cannot close a triangle
because each root sees only its own wing and the other root.

For the edge bound the removed 14-set B has two nonadjacent degree-nine
roots whose full neighbourhoods lie in B. Its remaining edges are only
between D0 and D3, the unique pair of blocks that do not share a root
neighbour. Hence `e(A) = 180 - 14*9 + e(B) = 72 + e(D0,D3)`, so at most
81; the lower bound 73 uses the published `(3,8;26)` edge minimum, not
the census count. The A-degree floor 3 uses R(3,7)=23 after deleting a
closed neighbourhood in A; the degree ceiling 7 follows from alpha(A).

The join's unordered wing-pair ordering is valid only up to simultaneous
reversal of the path; the next join must admit both orientations. It is a
cover of the permitted layouts, not a classification of unrooted models.
Using only one arbitrary isomorphism per marked input is unsound in
general: invariant labelling of the overlap does not fix the transported
wing masks. C's code explicitly iterates all isomorphisms in that step.

## Five roots

The seven blocks are disjoint once all distance-3 and distance-4 edges
are known. Index gaps ≤2 lie in a common neighbourhood (hence use its
disjoint partition); for gaps 3..6, the block membership ranges inside
the five root neighbourhoods admit root indices at distance 3 or 4.
Their neighbourhoods are disjoint. The distances-1/2 nonedges imply
v2 belongs to none of the seven blocks; each other root belongs to its
stated outer block by its opposite endpoint adjacency and the two
nonedges to that span's middle roots.

After removing N[v2], the middle window H1 consists of W plus the
two disjoint marks P5 and P(-1). The outer differences are exactly
P4 plus {v0,v3} and P0 plus {v1,v4}. This follows by complementing the
two removed sets inside G-N[v2]: they are P0 plus {v1,v4} and P4 plus
{v0,v3}, respectively. In particular the union fills all of G-N[v2].
Edges from v0 to v4 and P0 and from v4 to P4 are forced; v1 and v3 have
no other cross incidences because their neighbourhood partitions
account for all nine neighbours. Remaining cross choices are P4--P0.
The two forbidden mark-to-outer intersections arise from common root
neighbours v4 and v0, respectively. Edge count 99 follows from
9-regularity and triangle-freeness; a surviving U vertex has exactly
`9 - c(v2,x)` neighbours, giving the lower bound 3, and nonzero
codegree is forced by maximal triangle-freeness (degree at most 8 also
follows from alpha(U)). This hand reduction is sound provided the join
uses every required P4 row in both directions and all overlap alignments,
or a proved equivalent quotient. The P4/P5 cardinality argument uses no
inducedness hypothesis on the ambient path.

## Final P5 cover and trace boundary

`path_window_join.py` uses either P4 wing as the mark in a port, retaining
all overlap isomorphisms. The port's marked set and two outer masks determine
every retained edge of that orientation: incidences with the roots are
forced by the layout, and sorting the two unlabeled masks is harmless
because all four cross-edge choices are considered. The two marks must be
disjoint and nonempty, so the entries of a genuine join are distinct.
Unordered port pairs therefore still cover reversal; in the output, the
right mark is P5 and the left mark is P(-1). The edge-count prefilter counts
four outside neighbourhoods into H1, six non-window root/wing edges per
wing size, and three root/root edges, then fills only the P4--P0 deficit.

At the extension stage the independent nine neighbours of v2 are assigned
three masks of each of three distinct root types. A repeated mask would
violate the cap even without the common v2, so selecting distinct columns
loses no completions. Exact vertex loads and the union-hitting, intersection,
and unsupported-pair rows all give necessary tests, as in the R(7) packing
trace. First-present-mask branching covers every completion in a finite node.
The separate verifier documented in `ralph/lanes/C/PATH_REPLAY.md` rejects
the existence of a full packing for each supplied residue; it does not
independently certify the census-to-residue cover. Keep the exclusion at
`enum` unless the critic accepts the coverage and replay chain together.
