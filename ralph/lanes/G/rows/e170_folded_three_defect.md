# Three-defect board and peer Hall rows (hand)

The two-root premises and physical edge binding are the same as in
`e170_folded_two_defect.md`. At `h=5` the fixed grid has 17 copies;
there are three compulsory singleton slots on each shore (including
distinct labelled copies if the deficit repeats), eight occupied
double slots on each shore and five double/double sites. All 28
physical exterior sites remain represented; MTF, degree, private
margin, and padded blockers transfer unchanged. A finite inventory
with the same weak coordinate inequalities but total 17 agrees with
the prior Burnside count (286 boards and 156,112 weak keys).

**New selector-only rows.** On a width-`w` board, the private cell
`P_i` has `w−1` physical sites, and the opposite noncross anchors
form an independent set `B` of size `w−1`. All unused anchors on the
private cell's shore pad any independent set in the bipartite graph
between `P_i` and `B` by `w−1`: no other cross edge is present and
the sites only meet their own anchor on that shore. At its crossed
anchor `i=0` one may also add the opposite crossed anchor, since
triangle-freeness forbids those private sites meeting it, and its only
cross edge goes to the omitted anchor. If `I_k` is forbidden, König's
theorem therefore demands a matching of size at least
`3w−k−2+[i=0]` in `P_i × B`. For each subset `B' ⊆ B`, at least that
matching size minus `|B−B'|` different private sites hit `B'`. Subtract
the literal count of grid copies hitting it. The remainder is a lower
bound, `r`, on the number of the `s` compulsory singleton slots for
`i` whose selected opposite masks hit `B'`. For `0<r≤s`, encode this
by requiring **each** group of `s−r+1` distinct singleton slots to have
at least one such selected mate. Repeated slots count individually;
same-mask slots are not identified. If `r>s`, the empty clause is
valid. No automorphism or double-cover hypothesis is used.

Calibrations use the actual width-three boundary, both modes with
this rule evaluated at their own `k` and neither with target MTF or
target degree. The strict order-17 source and independent literal
physical enumerator agree on zero placements at `k=6`. At `k=7` the
SAT projection reproduces every one of 1,960 physical placements
(including mixed, repeated, and separated deficits) and every
canonical class, with no spurious or lost placement in any of 80
labelled small boards. The independent oracle uses explicit graph
edges and tests all independent sets; it does not use the Hall rule.
