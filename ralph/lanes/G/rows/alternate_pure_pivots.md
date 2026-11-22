# Alternate opposite pivots in the pure path/leaf case (hand)

Retain the two e168 profiles and the **both path/leaf** assumption
in `path_leaf_windows.md`. Use the uncrossed degree-seven centre on
side A. On side B choose either its noncrossed deficient leaf of
degree eight or a noncrossed full anchor of degree nine. In the first
case the maximum cross-side pivot codegree is four; in the second
it is five, by the order-27 upper bound for the common induced
antineighbourhood. In both cases the only common neighbours of
the two pivots are exterior (in X), because neither is crossed.

At these maximum codegrees, deleting the two closed neighbourhoods
gives order 27 and independence at most seven. Both original roots
are deleted; the retained strips are independent marked four-sets
with precisely the original sole cross edge. Every retained exterior
vertex has between one and two attachments on each marked side,
again with singleton counts bounded by four and double counts by
one per pair. Thus both orientations of the full 1,988 marked
order-27 source cover these pivots, regardless of the codegree of
the *two centres*. This is not an augmentation of order 25/26.

On the A side all six doubles of the retained marks are in the
signature list before removing opposite-exclusive vertices. Its
noncrossed missing leaf is existential (two distinct doubles to
nonstar marks from the A pivot). On the B side the marked role
assigns the original centre and, only in the full-pivot case, the
noncross leaf. The two globally absent double pairs are centre–star
and centre–leaf. A pair of retained marks cannot already occur as
a double in the fixed window if it is to be absent in the lift.
No other role is possible. There are 1,491 leaf keys and six full
keys from the exact scan (`pure-pivot.cover.log`); an independent
hole-loop matches the generator on all 256 local snapshots.

For a leaf pivot B there are four common deleted exterior vertices,
two A-only, and three B-only. The retained B columns have five
doubles before the cut, so their two absent occurrences pin the two
A-only labels. For a full pivot B the sizes are five, one, three,
and the B columns have four doubles, so their one absent occurrence
pins the A-only label. The missing occurrences in the A columns
pin the three B-only labels in both cases. These two independent
sorting conventions relabel disjoint sets, so lose no lift.

The remaining CNF conditions are the same necessities used for the
original pair: triangle-free, maximal, singleton/double lists, and
either (6,0,22) or (5,2,21) exterior vertices of degrees (7,8,9).
Every degree-seven exterior vertex is singleton on both sides.
Each eager ten-set consists of an actual independent six- or
seven-set of the window, the opposite pivot, and a subset of the
exclusive deleted exterior vertices; it is a ten-vertex edge
disjunction, not an asserted independent set. There are no other
alpha constraints. Certifying these cases does **not** close lower
codegrees at these pivots, or any e168 degree distribution.
