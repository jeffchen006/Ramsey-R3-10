# Joint opposite pivots and projected degrees (hand)

Use the pure both-path/leaf setting at the two low-n8 e168 pins. From
the checked alternate pivot scopes (`alternate_pure_pivots.md`), the
codegree of either centre with the opposing noncross leaf is at most 3;
with either opposing full anchor it is at most 4. In a fixed completion
the literal `full` is exactly the existence of a double support
containing the anchor and its own centre. For each noncross opposing
anchor, impose `codegree + (not full) ≤ 4` in **one** CNF for both
orientations. All common neighbours are exterior.

Lane A's redundancy observation: such a noncross anchor `a` has exactly
seven exterior neighbours other than those that also see its own centre,
and no adjacent anchor in T. Exactly `7-d_T(a)` of these neighbours are
removed by the opposite centre exclusively. At most one additional
removed neighbour is common to the two centres, and this is possible
only when `full` holds. Thus δ(T)≥4 makes every cap automatic. At δ=3
only degree-three anchors can bind. This is not a new closure.

For a separate exact projection, fix the two pivot groups of deleted
exterior vertices. The signatures on the side *opposite* an exclusive
vertex's pivot are pinned by the missing occurrences. Each centre has
exactly two distinct double partners among its three noncross peers, so
track the two sets of used partners, rejecting a duplicate. A removed
vertex `y` with given anchor support `S` can only see retained exterior
vertices avoiding S and these retained neighbours must be independent.
Its only possible neighbours among removed exterior vertices lie in the
opposite-exclusive group (none for a common vertex). Comparing S to the
already pinned side of the other-exclusive signatures can only remove
choices. Consequently a safe integer degree ceiling is
`|S| + α(T[X_compatible]) + (# eligible opposite-exclusive vertices)`.

The DP tests all supersets of the allowed removed degree-class choices
under these ceilings, recording d7 and d8 totals. A d7 must be a
singleton on both sides. Every surviving exterior vertex must gain
at least one incident edge outside T: in the original graph, it is
nonadjacent to a pivot and must share a neighbour with it by maximality,
necessarily in the deleted exterior group. Therefore surviving d7s must
be singleton on both sides and have degree at most six in T, and surviving
d8s must have degree at most seven. Compare both exterior profiles to
these counts after subtracting the DP's removed d7 and d8 counts. This
does not require the allowed neighbours to coexist across different
vertices. A feasible projection is not evidence of a completion.

Controls: `joint_pivot_caps.py` tests 6,968 literal inequalities on
C13, C35, saturated Exoo39 and all small free edge assignments. A's
positive planted lift and leaf/full overflow controls directly test both
orientations. `projected_degree_caps.py` tests 15,322 capacities on the
same graphs, compares 384 independent-set maxima to literal enumeration,
and exercises DP transitions. All 52 dispersed production-like sample
marks pass both exterior profiles of the new degree-cap projection.
