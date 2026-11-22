# Mixed pivot windows at e168 (hand)

Assume the exact e168 pin `(n6,n7,n8,n9)=(2,7,4,27)`, with a path/leaf
strip A and a matching/incident or path/middle strip B. Use the accepted
degree-six antineighbourhood hypotheses and strip structure in
`path_leaf_windows.md`. Choose A's uncrossed degree-seven centre and an
uncrossed anchor of B as pivots. Neither pivot sees the opposite strip
or root. Their common neighbours are exterior. The retained four anchors
on each side are independent and retain the unique cross edge. Each
surviving exterior support is a singleton or a double on each side, with
at most four copies of a singleton and one of a double. This envelope
does not depend on the choice of degrees or holes of B.

## Degree eight, codegree three, window minimum degree three

The degree-eight pivot in B has seven exterior neighbours (four singles,
three doubles); exactly one of B's missing pairs uses that pivot. With
the degree-seven pivot of A and codegree three, the induced common
antineighbourhood T has order 26, α≤7. There are 3 common, 3 A-only and
4 B-only deleted exterior vertices. A's retained four-column signature
list before the cut consists of 16 singles and 6 doubles, B's of 16
singles and 5 doubles. Their summed marked degrees are at most
`(29−4)+(27−3)=49`, so `2e(T)≤49+7·18=175` and `e(T)≤87`.

If δ(T)=3, deleting a degree-three vertex and its neighbourhood leaves
one of the 191 complete classes of `(3,7;22)`. The order-26 rooted gluer
uses all `(3,8)` lifts with δ=3, Δ≤7 and `e≤91`; this includes the
`e≤87` range, and the role scan verifies the weaker shared envelope.
Try both side assignments and each B hole placement, rejecting a hole
already occupied by a surviving double. The missing occurrences pin
4 B-only labels on the A side and 3 A-only labels on the B side. Sorting
these disjoint label sets independently loses no lift. The role CNF then
has exactly the same necessities as the old mixed degree-eight,
codegree-four encoding, with the indicated cut sizes instead.

## Degree nine, codegree five

An uncrossed degree-nine pivot of B has eight exterior neighbours
(four singles and all four incident doubles). Hence both missing pairs
are on the four retained B anchors. If the holes are a matching, they
are disjoint and the cross endpoint belongs to one; if they are a path
with cross endpoint in the middle, both contain that endpoint. Reject a
role if either of its holes already occurs as a surviving double.
The upper codegree bound is five because `|T|=22+j≤27`. At `j=5`,
`|T|=27` and the common / A-only / B-only exterior cut sizes are 5/1/3.
The original four-column multisets contain 22 and 20 signatures, and
the window retains 19 exterior vertices. This pins 3 B-only labels on A
and 1 A-only label on B. The upper sum of all marked degrees is
`(29−3)+(25−1)=50` and `e(T)≤91`.

Try both orientations of the original complete 1,988 weakly marked
order-27 keys and all legal pairs of retained holes. The five-anchor
strip degree signatures are unchanged, so the exterior still has
six d7 and 22 d9; all d7 are singleton on both sides. The proof CNF
adds triangle-freeness, maximality and the same eager ten-set edge
disjunctions. No proof of nonexistence is assumed for the unencoded
independent sets. This exclusion has no minimum-degree restriction on
T, but covers only the maximum codegree of a **noncross** d9 pivot.

Calibration: the order-26 source, both side orientations, and four
triangle-free positive addbacks plus occupied-hole negatives were
independently checked in `scratch/A/strip9/mixed.j3.source.log`.
The order-27 mutation matches all 24 historical d8 pilot DIMACS hashes,
and its d9 role enumeration matches an independent five-column-hole
oracle on 256 local snapshots. Each of its 162 d9 roles has a literal
triangle-free structural addback preserving T, exact support lists and
the marked degrees. These addbacks are not claimed MTF or alpha-valid.
