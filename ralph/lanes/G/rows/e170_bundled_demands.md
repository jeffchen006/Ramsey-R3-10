# Bundled attachment-row demands at private equality (hand)

Use the setting of `equality_private.md`. In the fixed residue `H`,
call a site or a distance-greater-than-two pair a demand: maximality
requires some selected anchor row to contain it. Every anchor row
is a maximal independent set of `H`: a missing anchor-to-site edge
must have a common neighbour in `H`. Two distinct selected rows
cannot both avoid the same independent `a-1` sites of `H`, or those
sites plus the anchors violate `alpha(G)<=a`. They cannot share a
site already at degree `a-1` in `H` because `Delta(G)<=a`.
These basic compatibility and iterative-deletion rules are inherited
from scout N, `review/ideas/r012_N.md`.

At equality, a site has one or two anchor attachments; distinct rows
intersect in at most one site (the double-pair multiplicity bound).
The existence of `p=a+1-d` privates per row implies that a selected
row `M` has exactly `|M|-p` shared sites and size at least `p`. It also
has size at least `delta(G)-1` and no more than `p+d-1`.

For a site `z`, write `D(z)` for sites that form pair demands with
`z`. If two selected rows `M,N` share `z`, they are the only possible
rows covering pair demands through `z`, so `D(z)⊆M∪N`. This bundled
test can reject a pair of rows even where different partners could
cover each missing demand individually. For a selected row `M`,
every `z∈M` with `D(z) \ M` nonempty must have a partner. The number
of such mandatory sites cannot exceed `|M|-p`. Conversely at least
`|M|-p` sites of `M` must have *some* compatible still-available
partner containing them. The upper test is only necessary: it does
not assert that the partners can be selected simultaneously.

Starting from the maximal independent rows of the correct sizes,
delete rows lacking support for a missing demand or breaking either
shared-site bound. By induction none of the rows of an actual
extension can be deleted. An empty demand domain rules out that
specific fixed-residue extension (with the equality pin for the
new tests); a surviving row is not an extension. The generic scout
rule needs no equality pin; the new bundled and quota tests do.

`check_equality_demands.py` independently computes the fixed point
using a pivoted maximal-set enumerator and Python integer bitsets.
The positive control checks the actual four rows at all 13 C13(1,5)
equality roots, not merely an arbitrary nonempty domain. This includes
the actual attachment count and membership of each planted row.
