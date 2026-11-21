# Two-orbit footprint compatibility for order three, a=4

`order3_a4_pairs.py` extends the eight pinned shapes in `order3_a4.md`.
For a J-orbit use a representative word of its footprint in `H`;
each J-orbit can independently rotate labels, so retaining one word
per rotation is a cover. A choice of a fixed-neighbor subset of `A`
is nonempty by the preceding one-orbit calculation. It consumes one
of two available outside-orbit slots at each selected fixed vertex.
Enumerate the multisets of these subsets up to relabelling `A`.

If outside orbits J and K share a vertex in `A`, their block must be
empty. Otherwise allow every offset whose corresponding neighbors in
`H` are disjoint (test at phase zero and use cyclic invariance). Using
all the permitted edges is optimistic: if that graph has too large an
independent set, every subgraph fails. It suffices to test bit masks
of the three J and K vertices, then use precomputed H antineighborhood
independence. Impose `α(H+J+K)≤5+|A_J∪A_K|` and independently
`α(H+O+J+K)≤9`; the latter uses the phase masks for `O`, which has no
edges to J or K. These pair tests are combined with per-H degree loads
and exact binary-domain search; triangles involving three outside
orbits, full outside independence, and the other fixed vertices are
not enforced.

Calibration tests all 49 nonempty pairs of three-bit footprint masks
on a one-orbit H, with explicit graph construction and subset oracles
on nine and twelve vertices, including a positive and forbidden joins.
The full eight-template run took 2.15 CPU s. At `f=7`, 25/64
template-layout pairs survive; at `f=10`, 116/144 survive. Both
`S:1111` and `D:111` at `f=7` require exactly the one mask multiset
`(1,2,3,4,8,12)` up to labels. Every `(f, template)` still has a
survivor; these are relaxation profiles, not Ramsey graphs. No change
to the status of the original cases or a blanket restriction for F.
Evidence: `scratch/E/order3_a4_pairs.full.log`.
