# Marked path/leaf windows at e168

## Assumptions and exact reduction (hand)

Assume an MTF `(3,10;40)` graph of size 168 with one of the two
degree profiles `(n6,n7,n8,n9)=(2,8,2,28),(2,7,4,27)`. Use the
accepted degree-six floor 120 and the accepted minimum-degree-six
bound on both degree-six antineighbourhoods. The latter requires
the finite enumeration in `no_degree_five_residue.md`.
The roots `u,v` of degree six are adjacent. As in
`ralph/lanes/A/ADJACENT_DEG6.md`, their other neighbours form
independent five-sets `A,B`, joined by one cross edge. The remaining
set `X` has 28 vertices. For either strip there are exactly four
private exterior vertices per anchor and eight distinct double
signatures in `X`; there are no other signatures. Each strip with
path-shaped missing double signatures and cross endpoint a leaf
has degree multiset `(7,8,9,9,9)` in `G`. Its centre has six
neighbours `D` in `X`, four private and two double (the doubles
meet the two full anchors, not either leaf).

**Single centre.** In the antineighbourhood of the opposite root
and this centre, the four surviving strip anchors are independent.
The 22 surviving members of `X` meet these anchors in exactly
four identical singleton signatures per column and one double per
pair. In particular all four anchor degrees in this order-26
`(3,8)` window are seven. In the complete 62 e73 classes there is
no independent four-set of degree seven; this gives an e74 lower
bound for this window only. The minimum edge premise is the
published `(3,8;26)` edge table (D-E8/D-C8d). The upper caps e82
and e84, with their separate degree conditions, are in
`ralph/lanes/H/ROUND7_REVIEW.md`.

**Two path/leaf strips.** Let their centres be `c_A,c_B`.
They are nonadjacent and have no common neighbour outside `X`.
The codegree `j=|D_A∩D_B|` is 1, 2 or 3: the lower bound is
maximality, the upper bound follows since the centres have degree
7 and their common antineighbourhood has at most 27 vertices.
Delete their closed neighbourhoods. The `(3,8)` window `T` has
order `24+j`: both roots were deleted, as were the two centres
and `12-j` members of `X`. Its eight marked anchors are two
independent four-sets with exactly one edge between them. Each
surviving exterior vertex of `T` has one or two attachments to
each marked side. On either side each singleton occurs at most
four times and each double at most once. Every missing occurrence
from the full four-column multiset is on the *opposite-exclusive*
set of `6-j` deleted exterior vertices; the common and own-exclusive
vertices all attach to that side's centre.

The scan visits independent four-sets in the indicated graph6
labels. All their exterior neighbours lie in their neighbourhood
union; the opposite side's three noncross anchors are exactly
the remaining vertices outside the first side and its union.
Try each candidate opposite star with one attachment to the first
side and none to its own three nonstars. Test the full singleton
and double multiplicity conditions on both sides. This gives an
exact list of marked windows, not a list of actual completions.
In rooted mode the known gluing root is either itself a mark
(take that side first) or exterior (take the side containing the
least marked neighbour first). In the exterior case at least one
root neighbour belongs to each side. Sorting the two masks at
output just removes the orientation; it does not delete any orbit.

## Completion relaxation and certificate scope

Pin the induced labelled window, both roots, both centres, and the
three types of deleted exterior vertices (shared, A-only, B-only).
In the cut exterior no edge is possible except between A-only
and B-only, by their known centre attachments. For each side
assign the missing four-column occurrences to that side's opposite-
exclusive vertices in sorted order. The two sets being ordered
are disjoint, so this is a genuine two-sided labelling freedom.
No choice of which noncross cell is the other leaf is pinned.
There are exactly four singleton occurrences at each of five
columns, one double on every pair of noncentres, no double for
centre and star, and exactly two distinct centre/nonstar doubles.

`strip_completion.py` then enforces all triangles and the MTF
common-neighbour disjunction on every nonedge; each edge with a
fixed common neighbour is set to zero. For exterior vertices the
only possible degrees are 7, 8, 9. A degree-seven vertex must be a
singleton to both sides (otherwise one degree-six antineighbourhood
would have degree five there). The exterior degree count is either
`(6,0,22)` or `(5,2,21)`, since each strip consumes one d7, one d8,
and three d9 and the two remaining roots have degree six. This
imposes e168 without a global exact-edge cardinality constraint.
The encoding omits all alpha constraints in the primary proof run:
UNSAT of this relaxation is sufficient for every genuine completion.

Two options strengthen the lower-order proofs. `--cut-budget` imposes
the identity

    e(T) = 49 + 9j + Σ_{z in D_A union D_B}(9-d_G(z)) + e_X(D_A\D_B,D_B\D_A).

The sum of degrees of the deleted vertices is `26 + Σd_G(z)`
(two degree-six roots and two degree-seven centres). Their induced
edges are the root-root edge, two root-centre edges, 12 centre-to-X
edges, and the exclusive cross edges; all other deleted edges are
prohibited by triangle-freeness or the fixed root neighbourhoods.
Subtracting the sum and adding the double-counted internal edges
from 168 yields the identity. `--eager 10000` chooses up to 10,000
independent retained sets of each size 6 and 7 and all sets of `9-s`
opposite-exclusive vertices (where `s` is the retained set's size).
Together with the other centre these are ten distinct vertices.
For each ten-set the clause is the disjunction of its edges; a
fixed present edge makes the clause redundant, and fixed absent
edges are dropped. Not exhausting all possible ten-sets is safe.
Both options require no extra structural hypothesis.

For j=3 use the full 477,142-class McKay `(3,8;27)` catalogue, bound
as in `rows/no_degree_five_residue.md`. G's four-set scan and A's
independent maximal-seven-set scan give byte-identical 1,988 marked
keys on 1,980 classes. All 1,988 relaxed completion CNFs are UNSAT
with LRAT accepted by CakeLRAT and lrat-check. This excludes j=3
**only when both strips are path/leaf in the two stated profiles**.
It does not close a degree distribution. At `n8=2` both strips
must be path/leaf; at `n8=4` there is also a mixed-role branch.

For j=1 and j=2 the full classes of order 25 and 26 are not in
hand. A *separate* complete slice uses `delta(T)=2` (order 25)
or `delta(T)=3` (order 26). In either case the antineighbourhood
of a minimum-degree vertex has order 22 and independence at most
6, and is one of the 191 `(3,7;22)` classes. All other cases with
larger `delta(T)` are outside this slice. It would be unsound to
apply the order-27 proof to either lower-codegree slice.

## Mixed strips: a separate exact order-27 source

For the `(2,7,4,27)` pin, suppose `A` is path/leaf and `B` is
matching/incident or path/middle. Choose a noncross degree-eight
anchor `b` of `B` (there are at least two). It has seven X-neighbours:
four private and three double. In particular exactly one uncovered
pair is incident to `b`. The path centre `c_A` has six X-neighbours.
Neither pivot is an endpoint of the unique A–B edge; each meets only
its own root and X. Thus their codegree `j` is the X intersection
size, and `1<=j<=4` by MTF and the order-27 upper bound for their
common antineighbourhood. Removing both closed neighbourhoods
gives order `23+j`: eight marked anchors and `15+j` members of X.

When `j=4`, the same order-27 source and the same 1,988 marked
keys suffice after trying both assignments of the marked sides.
On side A the original four-column list has all six double pairs.
On side B the full four-column list has five double pairs; besides
the hole incident to `b`, the other hole is on two retained anchors.
In the matching case, the two holes are disjoint and the cross
endpoint lies on one of them (otherwise its degree is ten). In the
path/middle case, both holes have that cross endpoint in common.
The role enumeration tests all these choices, rejecting a surviving
double on the retained hole. It was checked by enumerating all two-
hole five-column signatures on four cross choices and 64 occupied
double masks (252 positive and four negative snapshots).

The deleted X vertices are four common, two A-only and three
B-only. Missing occurrences in the full four-column multisets pin
the opposite-exclusive lists as before. The A pivot has two
distinct centre doubles excluding its cross anchor, and the B
pivot has three doubles as fixed by its specified hole. The two
strips consume all four d8 vertices and one d7, so exterior degrees
are `(6,0,22)` in the 7/8/9 classes. As before degree-seven vertices
are singleton to both sides. The pilot uses only these rows,
triangles, maximality and eager ten-set edge disjunctions. No
claim for smaller mixed codegree, or for the whole mixed role.

## Calibration

On all 410 triangle-free eight-vertex graphs, the direct Python
combination oracle reproduces the paired scan (21 marks on 10 graphs)
and the single scan (44 marks on 18 graphs), with positive and negative
examples. Rooted paired traversal reproduces these same 21 marks.
The generic completion engine accepts C13, C35, and saturated Exoo39
with a masked adjacency block and true alpha, and rejects each at
one lower alpha. The gluer reconstructs precisely the unique C13
class from the complete three `(3,4;8)` graphs, with two labelled
outputs. The marked-window probes on these controls have the smaller
parameters; the target path/leaf assumptions need not hold in C35
or Exoo39.
