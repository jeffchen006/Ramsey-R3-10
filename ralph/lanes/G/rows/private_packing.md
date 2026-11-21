# Two e168 integer packing cuts (hand + exact Farkas)

Assume G is maximal triangle-free of order 40 with independence number at
most nine, has 168 edges, and uses the established degree-six floor 120.
At every degree-six root the signature graph of `equality_private.md`
restricts the four neighbour counts (degrees 6,7,8,9) to:

| Name | 6 | 7 | 8 | 9 |
|---|---:|---:|---:|---:|
| A | 1 | 1 | 1 | 3 |
| B | 1 | 0 | 3 | 2 |
| C | 0 | 3 | 0 | 3 |
| D | 0 | 2 | 2 | 2 |
| E | 0 | 1 | 4 | 1 |
| F | 0 | 0 | 6 | 0 |

The six-profile list is the exhaustive check of all 9-edge subsets of
the 15 possible pairs on the signature graph. Each vertex must have
degree 1..4, and two degree-one vertices cannot be adjacent (their
corresponding neighbours in G both have degree six; their codegree in G
would exceed one). The graph induced by the degree-six vertices of G
is a matching with isolated vertices, since each root has at most one
degree-six neighbour. Any two distinct degree-six roots share at most
one neighbour: an adjacent pair shares none by triangle-freeness, and a
nonadjacent pair has the given `(6,6)` cap of one.

## Distribution `(5,0,9,26)`

Only B and F are possible. The number of B roots is even (endpoints of
the induced matching), so there must be an F root. There is at most one
F, since two six-subsets of the nine degree-eight vertices intersect in
at least three. Fix one F. At least two of each B root's three
degree-eight neighbours must lie outside F's six degree-eight
neighbours. This complement has size three. Distinct B roots cannot
use the same pair within it, so there are at most `C(3,2)=3` B roots.
Thus `B<=3`, `F<=1`, `-B-F<=-5` give `0<=-1` with unit weights.

## Distribution `(6,2,2,30)`

Only A and D are possible. Any D root sees all four degree-seven and
degree-eight vertices, and every other root of either type sees at least
two of these four. Thus `D<=0`. The single degree-seven and single
degree-eight neighbour of an A root specify a pair; distinct A roots
must specify distinct pairs. There are only `2*2=4` pairs. Thus `A<=4`,
`D<=0`, `-A-D<=-6` give `0<=-2` with unit weights.

The two proofs require neither the degree-seven floor nor either gluing
floor. `check_private_packing_cuts.py` checks the profile lists, the
packing constants and the two exact unit-weight Farkas contradictions.
`private_packing.py` obtains eight exclusions across all 47 eligible
profiles; the other six overlap the new equality LP exclusions.
