# Round 9 independent review — 2026-11-22

## G: mixed j=3, order 26, minimum degree 3

**Hand necessity.** Use the inherited e168 `(2,7,4,27)` adjacent-
degree-six strip hypotheses, in particular the four singleton signatures
per column and exactly eight distinct double signatures per strip. The
pivots are the path/leaf centre A and an uncrossed degree-eight vertex B
of the mixed strip. Both pivots see their own root but not the other's
root or other strip. They are nonadjacent. Their X-degree is 6 and 7;
the common part has size 3, so the deleted X parts have sizes 3, 3, 4
(common, A-only, B-only). Both roots are deleted. Thus eight remaining
anchors and eighteen X vertices give 26 vertices, with alpha at most 7
by adjoining the two pivots to an independent set in the remainder.

Both arrays of four anchors are independent and there is still precisely
one cross edge. Each retained X vertex sees one or two anchors per side:
if it met a pivot it would not be retained. On A, all six retained pairs
are present in the full (pre-deletion) four-column signature multiset.
On B, exactly one of the two omitted pairs involves pivot B because its
X-degree is 7 (four singletons plus three doubles). The other pair is a
retained hole. In the matching shape the two holes are disjoint and the
cross anchor belongs to one of them; in the middle shape they meet at
the cross anchor. The four tuples of anchor singleton counts are each
bounded by 4; double multiplicities are at most 1; a retained hole cannot
be occupied. In A there are `16+6-18=4` missing occurrences, precisely
the B-only X parts; in B there are `16+5-18=3`, precisely the A-only X
parts. These orders can be sorted independently because the label sets
are disjoint. The opposite cases (A/B exchanged) must also be considered
on each weak un-oriented mark. The identity of A's noncross deficient
leaf is not part of the weak mark and is not fixed in G's production CNF.

For the edge cap, the full degree-sum contributions to the four retained
anchors per side are at most `16+12+1=29` and `16+10+1=27`, respectively,
before removing the opposite-exclusive X vertices. Those removals cost
at least 4 and 3 stubs, respectively, since every such X vertex still
meets the retained anchors of the opposite side. Hence the retained
anchor degree sum is at most 49. Every vertex of a triangle-free graph
has degree bounded by alpha, so the other eighteen vertices have degree
at most 7 in T. The handshake identity gives `2e(T)≤49+126=175`, i.e.
`e(T)≤87`. Neither triangle saturation nor degree restrictions of G
should be imposed on T itself. As a conditional tightening only, if a
degree-3 root is exterior then replace 126 by 122, giving `e(T)≤85`;
do not use it for an anchor root.

**Source binding.** For δ(T)=3, taking any minimum-degree vertex gives
a 22-vertex antineighbourhood with alpha at most 6, and hence a member of
the published 191-class `(3,7;22)` universe. The source used by A/G is
complete for the *weak mark*, not conditioned on existence of a pure
strip completion: the raw gluer from those 191 cores uses root degree
3, window degrees 3–7 and cap 91 (redundant at order 26, so it includes
every mixed window with cap 87). Its two-side traversal tests both anchor
and exterior root placements, with no forced side orientation: see A's
independent `scratch/A/strip9/{mixed.glue.log,mixed.scan.log,mixed.j3.source.log}`.
Every valid role transports along an isomorphism of the unordered weak
mark when both orderings and every permissible retained/pivot hole are
tried. Marked isomorphism is required; an unmarked graph census is not
an interchangeable role list.

**Enum check, not a closure.** H's checker uses a separate graph decode,
literal enumeration of all missing pair-of-pair choices on a hypothetical
fifth column, and independent multiset deficits. On the 1,767 previously
reconstructed weak mark representatives the key set is byte-for-byte
equal as a set to A's 7,166 records: 5,438 matching and 1,728 middle.
Taking just mixed side 0 would lose 2,973 listed ordered roles, and
taking just side 1 would lose 4,193; these are key counts, not counts of
distinct solution orbits lost. A's four triangle-free geometric addbacks
and four occupied-hole mutations are additional controls, not Ramsey
graphs. H neither reran the 2,712,471 raw windows nor replayed production
proofs. This argument does not cover δ(T)≥4, mixed j≤2, or a full e168
degree distribution.

## G: mixed noncross degree-nine pivot, j=5

For the same pin and path/leaf centre, an uncrossed d9 pivot on B
has eight X-neighbours (four singleton vertices and all four incident
doubles). Both missing double pairs are therefore among the retained
four anchors of B. They are disjoint with the cross anchor in one of
them (matching), or meet exactly at the cross anchor (middle). Any
surviving double occupying either pair invalidates that role. Removing
the two pivot closed neighbourhoods now removes `6+8−5=9` X vertices
and leaves 27 vertices. The X cut is `5/1/3` (common/A-only/B-only);
it leaves 19 exterior vertices. The pre-cut lists on the retained
anchors have sizes 22 and 20, hence three missing occurrences on A
and one on B. Stub sums are at most `(29−3)+(25−1)=50` on the anchors
and `19·7=133` outside, so `e(T)≤91`. There is no minimum-degree
restriction on this T; the full established weak order-27 mark source
applies. This excludes no smaller codegree and no crossed pivot.

Independent role/receipt-ID comparison: with both assignments of the
1,988 weak marks, both shapes each pass the purely geometrical shape
condition in 11,928 tentative selections. After rejecting either occupied
hole, there are exactly 162 matching roles and none of middle shape, and
their full keys and receipt IDs match. Zero middle roles is an outcome of
the data, not an implicit omission. H did not replay the 162 proofs.
Evidence: `check_round9_semantics.py`, `scratch/H/round9-semantics.log`,
`scratch/G/round9/mixedfull.bound/certificates.tsv`.

## D: conditional high-codegree propagation

Fix root r and distinct `a,b,c,d` in `N(r)`. Let X and Y be exact triple
witnesses `{a,b,c}`, `{a,b,d}` with respect to `N(r)`, distinct from r.
If `a,d` has codegree three, r and Y are already common neighbours.
There is a third common neighbour Z, distinct from X since X misses d.
In the edge kernel at the edge `ra`, the triangle-free condition puts
`c,b,d` on the r side and `X,Y,Z` on the a side, with the two sides
disjoint; all six are distinct. The edges give the ordered simple P6
`c-X-b-Y-d-Z`. Under global L=6, D's no-C6 reroot lemma applies first;
kernel degree at most two then makes the simple P6 induced. (Its
internal vertices already have two path neighbours. The only remaining
chord would join its two endpoints, giving C6.) Either labelling
orientation is possible, and the first/fifth condition must hold for
both. The applicable profile premise is the **four** survivors after
the first 18 checks, before proof 2386 uses that same implication. It
forces `c,d` to have codegree three. The implication is not justified by
the three survivors of the dependent nineteenth check.

The Lean theorem `R310.kernelP6_opposite_pair` proves this conditional
step for general finite triangle-free graphs. It takes the first/fifth
condition on *simple* ordered P6s at `ra` as a premise. It does not
formalize the global L=6 implication, the no-C6 lemma, the source cover,
the profile data, or any LRAT. This keeps the dependency on the first 18
refutations outside Lean and avoids circular verification.

**Independent controls.** The checker uses only the known order-22
six-regular class file, a fresh set-based oriented path traversal, and an
explicit eight-anchor adjacency reconstruction from the frozen profile
rows. On cap-three C22 controls, 22 placements have the true local
profile condition and conclusion; 456 have a false profile condition
and false conclusion, so omitting the premise is not safe. In each of
2298, 2386, 2424 and 2431, both orientations are found and independently
give first/fifth codegree three. Eight degree-nine stars determine these
codegrees; unknown edges among exterior vertices cannot change them.
This is a check of the four-row property, not another verification of
the 19 refutations. Evidence: `check_round9_semantics.py` and
`scratch/H/round9-semantics.log`.
