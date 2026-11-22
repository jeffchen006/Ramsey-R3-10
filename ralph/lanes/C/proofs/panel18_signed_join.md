# Exact auxiliary package join on the two one-neutral 16/17 slices

## Necessary domains

Use the marked `K4,4` cover from [panel16_cover.md](panel16_cover.md).
The order-16 and order-17 windows share the one neutral vertex `z`,
and their private labels are disjoint even if they have the same
integer coordinates. Every unrecorded edge is between private sides.
For the labelled marks on a source window and one root `a`, let `S`
be the sites whose only root neighbour on that shore is `a`. The
induced graph avoiding the other three roots on that shore and their
closed neighbourhoods consists of the opposite window, `a`, and `S`.
Indeed, those three deletions remove the opposite root shore and all
source private sites outside `S`. Those three roots are independent,
so an independent set in the residual graph has size at most six.
Also `S` is independent because all its members meet `a`.

In the residue write `R_s` for the row of opposite window neighbours
of `s ∈ S`, with `z` included if and only if it is already adjacent to
`s` in the source window. All rows are independent because `s` is
their common neighbour. There is one known edge to `a`; each source
window neighbour other than `z` is a known edge outside `R_s`. The
required degree is nine, so the row size is
`8 − d_source(s) + 1_{s∼z}`. For each nonempty `J ⊆ S`, the union
of its rows must hit every independent opposite-window set of size
`7−|J|`. Otherwise that set and `J` form an independent seven in the
residue. These tests define the domains: no property of a missing edge
is assumed. A graph that completes the physical header induces one
package in every domain. The converse need not hold.

## Bitmap receipt for a single domain's nonemptiness

Let the support of bitmap `M_k(R)` be the independent `k`-sets of the
labelled destination disjoint from `R`. Enumerate those sets once for
each `k`. For each site `v`, record the bitmap of sets containing `v`;
the complement of their union over `v ∈ R` is exactly `M_k(R)`. An
independent `k`-set avoids all rows in `J` if and only if its bit is
in every `M_k(R)`, so the row-union test is the emptiness of their
intersection. The code checks singles separately and keeps bitmap
entries at sizes 5, 4, and 3 for the pair, triple, and quadruple
tests in the target. Reordering positions by their option counts is
a bijection on choices, retaining each position's demand and its
forced neutral bit. For groups of four, the recursion checks pairs
with the first row before the later loops, then the second–third pair
and first triple; for each fourth choice it checks the other two
pairs, all three triples containing the fourth and the quadruple.
Intersecting a union of three masks with the fourth mask is empty iff
each corresponding intersection is empty. This covers every nonempty
subset. The grouped bitmap search therefore returns the exact answer
to individual existence, not a quotient on signed crossings.

## Signed physical compatibility

Use crossing coordinates `(a,b)` with `a` an original order-16
private label and `b` an original order-17 private label. The row for
`a` in a forward package signs each such position present or absent;
the row for `b` in a reverse package signs `(a,b)` by its transpose
interpretation. Omit `z` in both directions because its actual edges
are already recorded in the two windows. Labels do not change when
positions are interleaved or processed in a different order. Hence two
packages have a common completion on their signed positions if and
only if they give equal bits on their overlap. Groups on the same
side have disjoint coordinates, since their singleton sets are
disjoint. Two opposite groups overlap exactly on their singleton
rectangle. A tuple with pairwise agreement defines a unique signing
on the union of the covered positions, not necessarily a full graph.

An arc-revision step deletes a package only when none of the other
group's remaining packages have its matching rectangle. Initially
every possible tuple has all its entries available. If they remain
before an arc revision, an entry of that tuple has its partner as a
witness, so none of its tuple entries can be deleted. By induction
an empty domain reached by these deletions proves no compatible
tuple. A nonempty fixed point does not prove compatibility.
Independently, the Python audit builds the full domains, and at
each join level indexes packages by the signed-present mask on the
overlap with the union of previous covers. Agreement of those masks
enforces both signs because the cover is fixed for that group. The
index visits exactly the packages agreeing with the previous signing;
induction on the levels therefore enumerates all compatible tuples.
If capped, this path cannot be used to exclude the header.

Finally, the weighted marginal product groups only source existence
queries and their counts (see [panel17_weighted.md](panel17_weighted.md));
it does not transfer signed compatibility. A roster of distinct physical
headers can exhaust one bucket only when its positive count equals
the independently recomputed both-pass mass there and each listed
member independently passes both directions. If all such physical
headers have no joint tuple, all headers in that slice are excluded.
