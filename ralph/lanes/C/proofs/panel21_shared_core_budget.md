# Physical core degree budgets for separate deletion cards (hand)

## Necessary condition

Fix a physical partial graph, including all required and forbidden edges
already established. Let `H` be the common induced core and let `S_i` be
pairwise disjoint physical singleton groups outside `H`. A restoration
of card `i` lives on `H ∪ {b_i} ∪ S_i`, where its root `b_i` is complete to
`S_i` and anticomplete to `H`. If the `b_i` are independent poles and
`H ∪ {b_i} ∪ S_i` is anticomplete to the other poles, then in an ambient
graph with `alpha ≤ a` every such card has `alpha ≤ a − (#poles − 1)`:
an independent set in the card can be augmented by all the other poles.

For each `h ∈ H`, let `p(h)` count **all** prescribed edges at `h`, whether
in the core, in another window, or inside one of the cards. Its remaining
capacity is `r(h) = d(h) − p(h)` for fixed target degree `d(h)`. For card
`i`, let `F_i` contain every admissible restoration in the fixed labels
(or a superset of all physical completions projected to the card).
For `f ∈ F_i`, let `u_i(f,h)` count the added, not prescribed, edges from
`h` into `S_i`. An empty `F_i` fails the uncoupled test. Otherwise set
`m_i(h) = min_{f ∈ F_i} u_i(f,h)`. Any completion contains one such `f` per
card. These edge contributions are disjoint because the `S_i` are
disjoint, and they are also disjoint from the prescribed incidences.
Therefore a necessary condition, at every physical `h`, is

```
sum_i m_i(h) ≤ sum_i u_i(f_i,h) ≤ r(h).
```

The last inequality can have slack from as-yet unassigned incidences
outside the cards. A card fully prescribed by a window contributes zero
added edges, not its original degree. Minimize across **all** permitted
restorations, including all physical lifts of an isomorphism type that
respect the pins. No automorphism may identify different physical
coordinates in the sum. This is a rejection test only, not sufficient
for a joint restoration.

## Strict toy: locally restorable even with exact aggregate totals

Use vertex labels `0,...,12` and two nonadjacent poles `0,2`. Their only
common neighbor is `1`; their private groups are `S_0={5,8,12}` and
`S_2={3,7,10}`. Both groups are independent. The common core `H` has
matching edges `6–11` and `9–4`, and site `1` has exactly the neighbors
`0,2,6,9`. Poles have no other edges, so a card `H ∪ {b} ∪ S_b`
is anticomplete to the opposite pole. Require 4-regularity,
triangle-freeness and `alpha ≤ 4` globally, hence `alpha ≤ 3` in each
card. In addition, prescribe `6–5` and `11–12` and forbid `9–12` and
`4–12`. All other `H`–singleton edges are initially open.

The exact aggregate counts cannot distinguish the two cards: there
must be ten `H`–singleton edges (the core degree sum is 16, minus four
internal incidences and two incidences to site `1`). For each singleton
group, its total degree after subtracting its three pole edges is nine;
the remaining neighbors can only be in `H` or the opposite group. Both
sides contribute the same number of edges crossing between the groups,
so each card must have exactly five `H`–singleton edges.

At site `6` three incidences are already prescribed: `6–11`, `6–1`,
and `6–5`. Thus `r(6)=1`. In any valid card, every core vertex hits its
singleton group (otherwise that vertex and the three singletons form
an independent four). In card `0`, sites `9` and `4` must both hit
`{5,8}`, and they cannot have a common neighbor since they are
adjacent. They take one distinct neighbor each. If `6` misses `8`,
then `6`, the one of `9,4` hitting `5`, and the singleton sites `8,12`
are independent: `6` must miss `12` because of the matched site `11`
and the prescribed `11–12`. Thus **every** restoration adds `6–8`,
regardless of the two possible assignments of `5,8` to `9,4`.
In card `2`, site `6` must hit at least one of `3,7,10`, all optional.
So the sum of the two added-degree minima at `6` is at least `2>1`.

Here are explicit local witnesses. A row lists the singleton neighbors
of its physical core site; both witnesses have exactly five such edges.

| Core site | Card `0` | Card `2` |
|---|---|---|
| `6` | `5,8` | `3` |
| `11` | `12` | `7` |
| `9` | `5` | `3,7` |
| `4` | `8` | `10` |

Each witness respects the prescribed and forbidden incidences and the
per-site degree bound including the fixed incidences of the other card.
No adjacent core pair shares a singleton neighbor, so each is
triangle-free. For either table column every core vertex hits at least
one singleton and every nonadjacent core pair has at least two distinct
singleton neighbors in its union, by inspection. Since the core is two
disjoint edges, these are all possibilities for an independent four
omitting the root. If it contains the root, it can contain only core
sites, at most two. This proves each card is locally restorable.

Also the negative scaffold has a triangle-free **degree-only**
completion (without the simultaneous card independence constraints).
Keep the prescribed scaffold; its full `H`–singleton rows for `6,11,9,4`
are `{5,10}`, `{8,12,7}`, `{5,3}`, `{8,7,10}` respectively. Include
exactly the intergroup edges `8–3`, `12–3`, `12–10`, `5–7`.
The degrees at the roots and `1` are fixed to four; at the core they
are four by the rows; at `5,8,12,3,7,10` their core and opposite-group
degrees are respectively `(2,1),(2,1),(1,2),(1,2),(2,1),(2,1)`,
in addition to one pole edge each. Adjacent core sites have disjoint
singleton neighborhoods, and the endpoints of each intergroup edge
have disjoint core neighborhoods, as the rows show. No triangle can
use a pole or `1` because its prescribed neighborhood is independent.
It is not an independence-bound completion: `{2,6,8,9,12}` is an
independent five. This separates the shared-card budget test from the
conjunction of local card restorability, even with the exact five-edge
counts, and feasibility of degrees and triangle-freeness alone.

## Planted positive: lift only the prohibition on `4–12`

Take the graph on `Z/13Z` with differences `±1,±5`. It is 4-regular and
triangle-free: the neighbors `1,5,8,12` of `0` are independent, and
translation sends every vertex to `0`. Its independence number is
four: `{0,2,4,6}` is independent. In any independent five, its five
cyclic gaps sum to 13 and are at least two. Their multisets must be
`(5,2,2,2,2)`, `(4,3,2,2,2)`, or `(3,3,3,2,2)`. The first has a
forbidden gap five, the second has a gap three next to a gap two (only
one gap four), and the third has a two-to-three boundary. Adjacent gaps
of two and three give a forbidden difference five.

With both poles and all other pins as in the strict toy, this graph
is admitted as soon as `4–12` is no longer forbidden. Its card `0`
uses no added edge at `6` beyond the prescribed `6–5`, and its card
`2` adds `6–7`, exactly exhausting the remaining capacity one. Using
total card degrees instead of added degrees would incorrectly reject
this positive at `6` (both cards must hit it). In both toys all
claims concern the same physical labels, not classes up to isomorphism.
