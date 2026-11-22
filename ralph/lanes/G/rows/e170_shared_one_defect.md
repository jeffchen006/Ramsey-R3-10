# Shared-grid clauses, marked e170 adjacent d6 equality at h=7

**Hand.** Start from `e170_equality_signatures.md` and the six-board
cover in N-009. The exterior `W` has 28 sites, each meeting each wing
in one or two anchors, and eight distinct double supports per wing.
If seven sites are double on both wings, there are `8+8−7=9` sites
with at least one double support. The other 19 are the private/private
grid. Each anchor had four private sites on its wing, so on each side
the row/column sum is four except at one coordinate where it is
three. The two missing private incidences are on distinct sites:
each is paired with a double on the other wing. Every physical site
is thus either a compulsory grid copy or a unique allowed pairing of a
left slot and a right slot. The crossed endpoints cannot both occur
on any site, by triangle-freeness. Parallel grid copies keep distinct
site indices even when their support masks agree.

Fix the left list of eight double supports and its deficient singleton.
On the right allow all ten double supports and the deficient singleton.
Select each left slot and the right singleton exactly once; right
double slots get mutexes only. A real graph uses eight of those ten.
No condition requiring the missing right pairs to meet the crossed
coordinate is needed for soundness: omitting it makes the formula
weaker. The coverage crosswalk only credits the 30 legal right lists
and their board stabilizer images. Shores may transpose for coverage
only if the physical matrix (including multiplicity) is preserved.
This does not impose a transpose constraint in the formula.

For each empty noncross cell, maximality requires a neighbour common
to its two anchors. The poles see different wings, and the only
wing-cross edge is between the crossed anchors, so such a common
neighbour lies in `W`. With no private/private site there, a selected
option must witness the cell. Include the positive row of **all**
allowed options with both anchors. No witness row for the crossed
edge, which is already present. The small non-MTF controls omit all
these maximality rows by design.

Introduce edge variables only for disjoint support pairs, and omit
option/option edge variables. On a real graph set a represented edge
true exactly when both endpoints are present and adjacent. A triangle
row of three represented edges holds: true edges would give a
physical triangle. If a padded blocker is false, every indicated
option is present and each two of its sites are nonadjacent, either
by a shared anchor or by a false edge variable explicitly in that
blocker. The row binder may add compulsory sites that share an anchor
with every chosen site and with each other. Finally the two poles and
ten anchors have a fixed induced graph, and no pole meets `W`; append
an independent subset disjoint from the union of the chosen supports.
The binder enumerates every independent subset of this boundary and
verifies that the resulting set can reach ten. Thus a false blocker
would contradict the graph condition. These implications from graph
to formula are all that the UNSAT receipts require.
