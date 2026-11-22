# Compact physical witnesses and exterior degree deficits at `h=5` (hand)

Use the accepted marked `e=170` adjacent-degree-six hypotheses (G-043)
and the folded three-defect physical representation. In `W` there are
17 grid copies, six mixed sites, and five double/double sites. Both
wings supply one or two neighbours to each exterior site; `e(W)=86`.
The physical edge bits on the left count every true edge of `W`
exactly once. Inactive endpoint bits are false and the selected-mate
channels enforce equality to the other shore (including false when it
has an overlap). Thus counting all left bits gives the exact edge
count, not a count involving either anchors or two shore copies.

## Physical witness clause

Specify distinct grid copies, a list of legal pairs of non-grid slots
with no repeated endpoint on either shore, and a subset of the 12
boundary vertices. Their union must have size ten. The boundary subset
contains no fixed boundary edge (one root edge, the two root stars, and
one wing crossing) and no incident anchor of any specified exterior
site. It suffices to include both:

1. The negative selector of every specified non-grid pair.
2. The left physical edge literal for every exterior pair whose full
   two-wing supports are disjoint.

If all guards select the named pairs, these are ten distinct physical
vertices with all known boundary edges absent. An exterior pair omitted
in (2) shares a neighbour; its edge is false by triangle-freeness. An
exterior pair included in (2) has an existing left bit and that bit
equals the physical edge under the active pair selectors. Therefore the
clause's negation would give `I10`. No assumption is made that options
with overlapping or equal masks describe the same site. Conversely,
if an option is not selected the corresponding negative literal already
satisfies the clause; removing it can falsely reject a valid completion.
No converse from a surviving SAT answer to a target graph is asserted.

Width-three controls instantiate `I7` with 1,960 literal placements and
recover all their original graphs. Every placement is independently
an `I6` negative; all recovered negative witnesses validate against
literal graph edges. A supplied four-row crosswalk independently tests
two-non-grid witnesses and repeated contact sites on h5. Three
width-three lost-positive mutations cover missing selector guard,
missing possible option/option edge, and short boundary padding.

## Exact edge count by local deficits

For a selected exterior site with support sizes `(a,b)`, the necessary
degree interval from the two residue floors is
`6 − min(a,b) ≤ d_W ≤ 9 − a − b`. This gives intervals `[5,7]` for grid
copies, `[5,6]` for mixed sites, and `[4,5]` for doubles on both sides.
Denote the respective upper bounds `7,6,5` by `cap`. Their total is
`17·7+6·6+5·5 = 180`. Hence `Σ_W(cap−d_W) = 180−2·86 = 8`.

Two unary threshold indicators per grid site encode whether its
deficit is at least one or two. One unary indicator per potential left
slot encodes whether the deficit of that actual site is one; when the
slot is inactive it is forced false. When active its selected mate
determines its unique support-size category. In each category the
threshold indicator at distance `j` is forced equivalent to
`d_W ≤ cap−j` by the two implications, using all incident physical left
edge bits. Thus the indicator sum across 47 potential flags is exactly
the actual deficit, and `Σflags=8` imposes the same target edge count as
the larger edge-cardinality encoding. Tests check exact expected and
off-by-one budgets on 16 literal smaller boards and all admissible
local mixed/double active/inactive guard projections.

## Prefix accounting

The original split order is left double slots `0,1`. They are
existence bits, not graph edges. For a prefix `p` both complementary
children `p0,p1` have precisely the corresponding unit added, as checked
at the CNF delta. When later variables are used, their order is fixed
and explicitly checked in the successor's receipt. A node is covered
if it has a verified proof or both complementary children are covered.
Only when the empty prefix is covered do we debit a whole board and
all of its weak hole-context keys. Any learned clause or deficit sum
added on a child is independently necessary for the original graph
part of that child; closure does not assume SAT entailment by the
weaker baseline.

## Exterior maximality

For a pair of exterior sites with a possible left edge bit, maximal
triangle-freeness requires that an occupied pair is adjacent or has a
common neighbour. The pair already has disjoint left supports. A fixed
grid/grid pair with a shared right anchor has no left bit and is not
listed. For each optional site and right anchor, a contact indicator
is equivalent to the disjunction of its selected mates containing that
anchor. A listed grid/slot pair can therefore use its fixed grid right
anchor as a witness if the slot has the corresponding contact. A listed
slot/slot pair can use any right anchor common to both contacts; a
one-way conjunction literal implies both contacts. No root is incident
with an exterior site. The only remaining witnesses are all other
left exterior positions connected to both sites: use another one-way
conjunction literal for the pair of incident edge bits. A positive
incident edge implies its optional endpoint is active, so an inactive
slot cannot furnish a spurious witness. Include negative occupancy
guards for optional endpoints. Thus a real graph always extends to
the clauses, and a satisfied clause for two occupied endpoints gives
an edge or an actual witness. This concerns exterior pairs only, not
any change to the boundary maximality checks.

On the 1,960 smaller placements, literal physical exterior maximality
selects exactly 56. The CNF agrees on every placement and accepts all
1,960 after greedily saturating the exterior alone, with contact masks
unchanged. The audit reconstructs all shore contacts and possible
common-neighbour positions from the literal board.
