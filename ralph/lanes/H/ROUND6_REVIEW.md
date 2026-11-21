# Round 6 — checked baseline and degree-six hand bridge

## Checked count and scopes

`check_round6_scope.py` merges G's frozen round-4 and round-5 keys with
`floor108_overlap.jsonl` and compares both the cuts and thresholds against
`round6_baseline.csv`. It checks duplicate case keys, the order and degree
sum on every row, disjointness, the e162 overlap, and repeated thresholds
(e170 `(0,10,0,30)` has two tightening rows, of which we keep the stronger).
This is bookkeeping, not a third enumeration or replay of the Farkas proofs.
The critic's independent merge and coverage verdict are in
`ralph/critic/round_005.md`; the H run is `scratch/H/round6-scope.log`.

- 368 → 283 after G's 84 global n6 cuts and one e168 parity cut; 283 → 278
  after B-013 and the exact distribution consequences. Case R is separate.
  B-012 is the e162 `(0,2,32,6)` cut already included in the latter five.
- Conditional U88 keys `(e,n6,n7,n8,n9)`:
  `(162,0,0,36,4)`, `(163,0,6,22,12)`, `(163,0,7,20,13)`,
  `(163,0,8,18,14)`, `(164,0,10,12,18)`, `(164,0,11,10,19)`,
  `(164,0,12,8,20)`, `(164,0,13,6,21)`, `(165,0,14,2,24)`,
  `(165,0,15,0,25)`. Four came in and four went out after the 283-count
  baseline. None is excluded just by this re-keying.
- Open e168 degree-six keys: 11 with n6=1, nine with n6=2. All 20 keys
  are printed by the check. They are disjoint from U88.
- C's `f*=9` codegree-six graph is a nonempty matching, not an R(6)
  exclusion. P3 residue bounds are not isolated-pair bounds. The 35,099
  marked H21 windows and 246,483 K13 graphs are separate necessary lists.
- E's certified scope is precisely f=32, t=4, δ(W)≥2, e(W)=12; no
  e(W)=11 exclusion. The f=28 mix retains the inherited F10 premise.

## Lean bridge (G-019 remains external)

For an MTF order-40 triangle-free graph with alpha≤9 and a degree-six
root, R(3,8)≤28 implies all vertices in the order-33 antineighbourhood
have degree ≥5 there. G's 984-class outer rejection supplies the only
new input: none has degree exactly five there. Thus every exterior
vertex has residue degree ≥6. The residue identity gives
`c(root,v) = d_G(v) − d_H(v) ≤ d_G(v) − 6`; MTF gives positive codegree
for nonadjacent vertices, so two degree-six vertices must be adjacent.
Triangle-freeness then makes n6≤2. These steps are in
`lean/R310/ResidueDegreeFive.lean`; neither the Ramsey bound nor the
enumeration is newly proved by Lean. G's outer search need not assume
MTF; the final positive-codegree implication does. No total-e restriction
on this bridge.

At an e168 degree-six root with the accepted residue floor 120, the
edge deletion identity forces Z≤48 and the MTF bound forces Z≥48.
If the other degree-six vertex is adjacent, the five remaining neighbours
have degrees 7–9 summing to 42. Their (7,8,9)-counts must be
`(0,3,2)` or `(1,1,3)`. This Lean theorem assumes the adjacent pair and
the absence of other degree-six vertices. It recovers the key parity
fact without any finite case check; it is not a closure for the nine
surviving n6=2 cases.

## Hand refinement: marked additions when n6=2

This audits A's two-root reduction and adds a profile test. Let the
adjacent degree-six roots be u,v, let A=N(u)−{v}, B=N(v)−{u}, and let X
be outside both closed neighbourhoods. A and B are disjoint independent
5-sets. In the signatures at v all vertices of A meet u, and u has four
private vertices and one double vertex (d(u)=6, one edge to v). Thus
there is exactly one A–B edge; write its B endpoint as b0. Relative to v
the remaining four private vertices for each B anchor, and eight double
vertices internal to B, lie in X. The e120 residue at u is X+B.

A nonedge within B is blocked from being added iff its endpoints have
a common neighbour in X. Exactly eight distinct pairs are blocked by
the two-element signatures; the complementary two pairs can both be
added. A triangle using both added edges would need a third edge within
B, which does not exist. Adding edges cannot increase alpha. All five
B vertices have degree eight in the e122 supergraph: four edges to the
private cell and one edge (or double-signature witness) for each of
four other anchors. The same argument applies on side A. This rules
out a zero-addition e120 input *in the n6=2 branch only*; two labelled
additions need not yield two nonisomorphic e121 classes. No completeness
of a partial e122 census follows.

The cross endpoint b0 has original degree ≥8 by the new cap: it and u
are nonadjacent and share v and the A endpoint of the cross edge. For
b∈B the two new edges must supply degree deficit
`8 − (d_G(b) − 1 − [b=b0])`; only the v edge and (for b0) the cross edge
were removed. This gives exactly three possible patterns for the two
marked edges:

| Original B degree profile | d_G(b0) | Marked e122 edges |
|---|---:|---|
| (0,3,2) | 8 | P3, centred at b0 |
| (0,3,2) | 9 | Matching |
| (1,1,3) | 9 | P3, centred at the degree-seven vertex |

The excluded `(1,1,3)` with d_G(b0)=8 would give two distinct vertices
of deficit two, impossible for two distinct edges. In particular in
the open e168 key `(2,8,2,28)` both sides must have type `(1,1,3)` by
disjointness and only two degree-eight vertices, so both marked e122
edge sets are paths centred at original degree-seven vertices and
the cross endpoints have original degree nine. This is a necessary
profile filter, not an exclusion. `check_round6_scope.py` checks all
five-label degree vectors and marked two-edge sets, plus 52 adjacent
equality-root controls in C13(1,5) (each with two blocked and one
legal pair among its three opposite-boundary vertices).
