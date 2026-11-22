# e170 adjacent degree-six equality: a shared-grid middle obstruction

**Scope.** Use the equality signatures in `e170_equality_signatures.md`
and the `h=8` aligned grid. The two wings have five anchors each, and
only the pair of crossed anchors, labelled `(0,0)`, is joined. Every
other exterior site touching singleton anchors on both shores is exactly
one of the 20 off-diagonal cells. The remaining eight sites have distinct
double supports on both sides. This proof needs MTF and alpha at most
nine; it does not cover `h<8`, arbitrary pairs, or any whole degree
distribution.

Fix the left list to the eight masks `(3,5,6,10,12,18,20,24)`;
the two absent left pairs `(9,17)` meet at the crossed anchor. Offer
all ten possible pairs on the right. Create a selector for a left/right
pair of slots unless both supports include anchor 0. A graph assigns
exactly one selected site to every left slot, and at most one to every
right slot. The right list of eight is determined by the eight selected
sites; the formula does not force more than eight or fix which eight.
There are no singleton slots at `h=8` because the grid uses the entire
private quota. The four missing noncross cells `(i,i)`, `1≤i≤4`, must
each receive a selected common neighbor. Neither root nor any other
wing anchor is adjacent to both ends, and no grid site corresponds to
an empty cell. Thus each such MTF requirement is a positive disjunction
of the selectors meeting both anchors, not a chosen witness.

Use the same edge variables for the grid regardless of the selections.
Use edge variables from each optional site to the grid where supports
are disjoint; shared anchors themselves prohibit edges. Actual edges
between selected sites are not represented; they are **not** assumed
absent. A triangle row is a literal triangle among available edge
variables. Assign every modeled edge incident with an unselected
option false. For a padded set `T` of grid sites and at most one optional
site, let `A,B` be the unused left and right anchors. Available boundary
padding has independent maximum
`max(|A|+|B|−[0∈A∩B], 1+|A|, 1+|B|)`: take neither root or exactly one
root and the opposite shore to its neighbors. If the sum with `|T|`
is at least ten, some eligible modeled edge inside `T` must be present;
if `T` includes an option, guard the row by its negated selector. Every
such clause is necessary in the projection of an actual graph, not a
sufficient characterization. The binder computes the padding afresh
from the independent sets of the literal 12-vertex boundary; omitted
isolated sites in clauses must have a physical witness intersecting
every other support in the witness.

**Label action.** Sort masks as in the residue roster. When the middle
list is on the right, swap shores (including the two roots). On both
shores apply the *same* permutation fixing anchor 0: the off-diagonal
board and crossed edge are preserved, and left masks then coincide
with the fixed list. Transform both supports of each physical site,
not just the names of the hole pairs. Each of the eight transformed
sites has a legal selector; the eight selectors have distinct left and
right slots and hit the four actual MTF disjunctions. This map is
injective within a labelled scheme. Across schemes debit the original
`(scheme,rank)` keys once, never by accumulating selector counts from
overlapping receipts. The proof and exact physical count are documented
in `../ROUND19_REPLAY.md`.
