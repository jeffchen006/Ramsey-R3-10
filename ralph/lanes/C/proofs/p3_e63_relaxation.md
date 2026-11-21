# P3: exterior-root caps, boundary relabelling, and a smaller CNF

Scope: an assumed 9-regular, maximal triangle-free graph on 40 vertices
with independence number at most nine and maximum codegree six. Use the
partition of `path_three.md` for three consecutive distinct roots
`v0,v1,v2` in the codegree-six graph J. The three roots are independent,
their exterior diagonal has codegree `s` in `{3,4,5}`, no root has a
neighbour in X, and X has order 22 and independence number at most six.
This bridge uses the accepted no-P4 certificate; it does not apply to
R(5), or to an isolated pair without changing the boundary partition.

## Necessary cap and boundary permutations

The three roots form an entire component of J: there is no J triangle,
and an additional J neighbour would produce four consecutive distinct
roots (if attached to the middle, use the earlier degree-two bound for J).
Thus every root-to-X pair has codegree at most five. A pair consisting of
a root and a nonroot boundary vertex also cannot have codegree six;
the fixed-boundary CNF need not use that extra restriction.

The fixed boundary can be relabelled independently of X. Within the
boundary, vertices with identical open neighbourhoods in its fixed
induced graph are nonadjacent and freely permutable, fixing the roots
pointwise. Given any extension, order these vertices lexicographically
by their binary X-neighbour vectors in the fixed label order of X, with
zero before one. This reorders no edges inside X and preserves the entire
fixed boundary. Sorting any number of equal-profile vertices is harmless.

To encode a pair of consecutive sorted vectors, forbid `1,0` at their
first differing coordinate. A prefix literal is forced whenever the
previous prefix is forced and the two bits agree, starting with a true
empty prefix. Each forbidding clause is conditioned on that prefix.
The forward implications suffice: every exact equal prefix is forced,
and setting all prefix literals to their actual values extends any
lexicographically ordered pair. The fixed code calls this `lex_order`.

The Hall reduction in `path_three.md` covers the two wing labellings and
the exchange of the two private middle vertices. For `s=5`, `e(X)=63`,
enumeration gives 13 representatives with roots held in order. Reversing
the roots simultaneously exchanges the opposite wings and the B0/B2
blocks, and leaves T and B1 as blocks. This is a relabelling of the
boundary while fixing X pointwise, not a claim of an automorphism of G.
Consequently either orientation yields the same completion question.
The independent index audit checks exact edge-by-edge relabellings on
these 13 representatives, giving eight orientation-free keys.

## Lite6 fixed-boundary relaxation

Fix X and one boundary. Use an attachment variable for every potential
X-to-nonroot edge, no variable for X-to-root edges. Degree sums and the
triangle, maximality and codegree constraints are the same basic rows
as in `P3_REPLAY.md`, except that all X-to-root codegrees are capped at
five. Integer cardinalities are encoded exactly. For a same-side pair,
each common neighbour in the other side is the AND of its two attachments,
and common neighbours inside the fixed graph contribute constants.
If the fixed pair is adjacent, triangles forbid each across-side AND;
if not, require total common-neighbour count in `[1,6]`. For a cross
pair the common count is a sum of single attachments: at one endpoint
the edge of each candidate two-step path is already fixed. The direct
attachment or a common-neighbour witness is necessary by maximality.
Every possible triangle has at least two vertices on one of the sides,
so the same-side rows already exclude all cross triangles.

For an independent set I in X and a maximal boundary independent set M,
let a member of M be available if it has no neighbour in I. All the
available members, together with I, are independent, hence at most
`9-|I|` members of M are available. Roots in M are always available and
are subtracted from the right-hand side. For a nonroot b, the gate
`available(b) OR (some attachment from I to b)` forces availability when
the actual attachments are all false. Gates set to their actual values
extend any true graph whenever the inequality holds. Dropping any of
these constraints can only weaken the formula. **Lite6 retains the
singletons and the independent sets of size at least six** (and the
empty set only if needed); it makes no claim about the other rows or
about any satisfying relaxation model. The other benchmark variant,
Min6, also retains these inequalities for every M of size nine for all I.

## Flexible-boundary relaxation for other strata

Do not fix the edges allowed among the deleted vertices. The root edges
and all other allowed/fixed entries are precisely those of `path_three.md`;
unknown eligible boundary edges get variables. In `p3_flexible.py`,
degree sums and the redundant boundary edge total are equalities.
For each pair, count its possible two-step paths using literals or ANDs,
including fixed contributions. An edge excludes every such path; a
nonedge needs a witness by maximality. The cap is five for every pair
involving a marked root except the two marked J edges. This applies to
any diagonal after the no-P4 result, not just diagonal five.

Every vertex of X must hit each of the three fixed root neighbourhoods:
these are independent nine-sets. For a size-six independent set I of X,
let S be a four-set in the boundary that has no fixed edge. If S contains
a true eligible edge then there is no constraint for S; otherwise some
member must be adjacent to I. Thus the clause disjoining all eligible
boundary edge literals in S and the negated availability literals of its
nonroots is necessary. Roots have no attachment and contribute no
negations. `guarded` includes all such S; `universal` includes only
those with no eligible edge. Both omit other mixed Ramsey rows, so only
UNSAT proves anything about extensions. Each marked block can be sorted
by its X-neighbour vectors; this permutes unknown eligible boundary
edges internally, preserves the fixed entries and candidate sets,
and is a valid choice even when the entire boundary graph is unknown.
