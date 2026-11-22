# Shared edge rows at e170 (hand)

Assume the accepted MTF degree-six residue floor 122 and the adjacent
degree-six equality setup of `e170_equality_signatures.md`. Use its
28-site exterior W with 86 edges. The wings U and V have five anchors
each and one crossing between the marked endpoints. Index the wing
endpoints by 1 on both sides. Every W vertex has a nonempty support
in each wing, of size one or two. Put it in type `t=(S,T,d)`, with
degree `d` in G. Write `b_t` for the population of type t and `U_t`
for its old upper bound (one when either support is double, four
otherwise). Types never contain an edge internally because their
vertices share a wing neighbor.

## Shared counts, capacity and projections

For each unordered pair of distinct types `t,s`, allow an edge
variable `m_ts` only when the left supports are disjoint **and** the
right supports are disjoint. Any other edge is in a triangle with a
wing vertex. Count the actual W edges of the allowed type pair. Then
`m_ts<=b_t b_s`, hence `m_ts<=U_s b_t` and `m_ts<=U_t b_s`. Summing
the counts gives 86. Summing the same counts over all incident type
pairs gives `(d-|S|-|T|) b_t`. For each one-root pair of cells inside
W, its edge entry in the old model must equal the sum of the **same**
`m_ts` for which the unordered pair of projected supports is that
cell pair. Edges to the other wing are still set by the round-13
shared-vertex rows; do not count them again as W edges.

The two linear capacity rows suffice for the product at integer
points when one type has bound one. Otherwise exact product capacity
can be added lazily: write `b_t=sum(q_i)` with ordered binary `q_i`,
add quota variables `h_i<=b_s`, `h_i<=U_s q_i`, and require
`m_ts<=sum(h_i)`. For a genuine graph set `q_i=1[i<=b_t]` and
`h_i=b_s q_i`. Conversely, at any integer point the quotas sum to
at most `b_t b_s`. The new variables do not fix either population.
The pilot did not reach an integer point requiring these refinements;
97 small population pairs test the quota rows directly.

## Domination, codegree, private partners

For an anchor `a` missing from a type's support on its side, count
W edges from type t to types whose support on that side contains a.
These count exactly the W common neighbors of t vertices and a.
There is a boundary common neighbor precisely when a is the marked
cross endpoint and the opposite marked endpoint is in the opposite
support of t. With no such neighbor, the W sum is at least `b_t`
by MTF. By L6 the W sum in either case is at most
`(d+d(a)-11-1[via crossing]) b_t` in the target.

If t is private for anchor i on that side, keep only edges to types
private for a. A matching of size at least `p-1+1[ia is a double]`
between the two whole private cells leaves at most one vertex of the
i-cell without a matching edge, or none when ia is a double. Thus
that restricted edge sum is at least `b_t-1[ia is not a double]`.

For a fixed population pattern, the domination lower row has a cheap
obstruction independent of any edge projections: if `b_t>0`, there
is no boundary common neighbor, and no **occupied** type has both
supports disjoint from t and contains a in the required wing, no W
edge is possible. Equivalently, the variable-population necessary
row is `b_t <= U_t sum(b_s over such compatible types)`. The direct
filter checks for empty support in the sum; it neither enumerates
populations nor excludes any whole wing template.

## Mixed-wing edge windows

Let I be an independent subset of the fully prescribed boundary
`{u,v} union U union V`, and put `k=10-|I|`. Retain all W types whose
combined support avoids I. Use either those sites alone, or also add
all other boundary sites anticomplete to I. The resulting induced
graph has independence number less than k: an independent k-set
there would extend by I. The retained order is linear in populations
plus a fixed boundary term. Its edge count is the sum of retained
shared type edges, plus type populations weighted by their number
of contacts into the added boundary, plus fixed boundary edges.
Every support line `a e >= b n+c` lying below every published minimum
for `0<=n<R(3,k)` therefore gives a linear row. The generator checks
each emitted line against **every** table entry, and adds the order
cap separately. For the smaller analogue replace 10 by `alpha+1`.
For the target the priced windows use `3<=|I|<=9`, hence `1<=k<=7`.
These rows do not enforce all triangles in W or all independent-set
constraints. They are necessary, not an embedding test.
