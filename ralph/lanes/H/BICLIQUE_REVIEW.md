# Saturated biclique incidence review

**Label: hand.** The bounds and equality consequences in
`ralph/lanes/D/SATURATED_BICLIQUE.md` are valid with the stated cap. The R(3)
catalogue hits are not additional closures and the R(4) structure is not
an exclusion of all K3,4 completions.

The two biclique parts are independent and an outside vertex cannot hit
both sides, by triangle-freeness. A pair on the small side already has
exactly the full available cap in the other part. Therefore only pairs
of vertices on the large side can account for a multiplicity beyond
one, and each of those pairs is charged at most `c-r` times. The slack
in `1 + binom(k,2) - k` is `(k-1)(k-2)/2` for a nonnegative integer k,
so equality forces k=1 or k=2 for all outside vertices. Equality also
forces saturation of each large-side pair and degree d for every
biclique vertex.

For `K3,4` at `n=40,d=9,c=4`, each small-side vertex gets five exclusive
attachments; each large-side vertex gets one double attachment with each
of its three peers and three exclusive attachments. The sums are 15 and
18 vertices, respectively. The 15 vertices are anticomplete to the four
large-side vertices, giving alpha ≤5. Any two exclusive quintets induce
a bipartite graph of order ten and alpha ≤5, so their minimum vertex
cover has size at least five. König's theorem gives a perfect matching.

A four-cycle in the two-sided edge kernel yields the stated K3,3 after
including the adjacent roots, one in each opposite part. Two distinct
vertices with the same three-element support in the neighbourhood of a
third vertex likewise give a K3,3 with that third vertex. This validates
D's triple-uniqueness cut without relying on any factorized encoding.
