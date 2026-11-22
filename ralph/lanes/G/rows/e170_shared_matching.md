# e170 adjacent degree-six equality: fixed-left matching at h=8

**Hand reduction**, using `e170_equality_signatures.md` and
`e170_aligned_grid.md`. The twenty fixed private sites have ordered
supports `(i,j)` for `i≠j` in a 5 by 5 board, and the only crossing is
`L0-R0`. The eight other sites are double on both shores. Their left
and right lists each omit exactly two of the ten double supports, with
at least one missing support through the crossed label 0. There are
three hole shapes: disjoint (matching), meeting at 0 (middle), and
meeting away from 0 (leaf).

If a shore has disjoint holes, exchange shores and roots if needed so
that shore is left. Its crossed hole is `{0,a}`; its other hole consists
of two distinct nonzero labels different from `a`. A permutation fixing
0 sends `a` to 4 and the other hole to `{2,3}`. Apply this permutation
to **both** shores of the aligned board; the crossing and the diagonal
missing cells are preserved. The fixed left slot list is consequently
`(3,5,6,9,10,18,20,24)` (holes `17,12`). The right list is not pinned.

As for `e170_shared_middle.md`, select exactly one site per fixed left
slot and at most one per right slot. Both selected supports cannot
contain 0, since the site would form a triangle with the crossed edge.
Maximality requires each missing noncross cell `(i,i)` to be witnessed
by some selected double site containing `i` on each shore. There is
no common anchor, root, or fixed grid site for that cell. The four
positive MTF rows are therefore disjunctions of eligible selectors,
not fixed witness assignments.

Assign modeled edge variables by the actual graph on selected sites
and grid sites, and set all modeled edges incident with unselected
options false. Optional–optional edges are **not represented**; an
edge between two selected optional sites is not assumed absent. The
model forbids actual triangles among modeled edges. Every positive
blocker has a padded independent-ten witness of fixed grid sites,
with at most one optional site. A witness with an optional site is
guarded by the negated selector. If the guard is not true and every
literal edge is absent, pairwise nonedges among the witness sites
come either from the assigned variables or from shared anchors.
Together with its independent boundary padding, these would give a
forbidden independent ten. The literal binder uses the actual 12
boundary vertices, never a supposed nonedge between optional sites.

Consequently any target in this marked slice with a matching shore
would satisfy the shared formula. A checked refutation excludes its
scope; together with the accepted leaf and middle receipts it covers
all three shapes. No consequence is asserted at `h<8`, nor for an
entire equality case or degree distribution. Exact original-rank
bookkeeping and proof replay are in `../ROUND20_REPLAY.md`.
