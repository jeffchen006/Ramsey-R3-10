# Degree-seven adjacency traces in the all-missing crown

**Scope.** Saturated `(2,32),t=4,e(W)=8,P=0,δ(W)≥2` with the
all-missing hypothesis established conditionally on E-021 in
E's round 23. Thus `W` has eight sites with fixed degree eight,
the four disjoint independent roles `A_i` have six sites of fixed
degree seven, and `H_i=F−A_i` are pairwise isomorphic triangle-free
26-vertex cards with 74 edges and independence number at most seven.
Every `w∈W` meets every role. In the `b_max=16` arm, omit its unique
largest role `D`; the three retained roles have totals `(10,10,12)`
or `(10,11,11)`. The `W` residue therefore has four singleton and
four triple rows in `D`, and the common number of degree-seven
vertices of the cards is six (E round 23). No specific identity,
mark correspondence or embedding of the missing graph is assumed.

## Role-bound sparse test

For retained roles `i,j` and complementary retained role `k`, C-056
gives `e_ij=e_Dk+24−b_i−b_j`, so the pinned-card variable `e_ij`
is at least `30−b_i−b_j`. If equality holds, the **omitted** rectangle
`D×A_k`, not the observed `A_i×A_j`, is a perfect matching. If the
observed count is one above the floor, the three forbidden seven-edge
shapes likewise apply to `D×A_k`. A retained exterior degree-seven
site in `A_k` has no neighbor in `D`, so if such a site is proposed,
increase `e_ij`'s lower bound by one. The number of disjoint-
W-support pairs in `A_i×A_j` is an upper bound. This permits an
early root veto without a completed card. If an actual card reaches
the screen, the six individual deficits `7−d_H(v)`, `v∈A_k`, are
known, and all must be one at equality. No equality issue on a
different role pair implies this one.

## Degree-seven induced graph

For any omitted role `A`, a `W` site has degree seven in `H_A`
exactly when its `A` row is singleton. For an exterior site
`v∈F−(A∪W)`, its fixed degree is seven, so it has degree seven
in `H_A` exactly when `N_F(v)∩A=∅`. Any two such exterior sites
are adjacent: if not, they and the six vertices of `A` form an
independent eight that misses at least one of the four roles
and so lies in another card. A triangle is forbidden, so there
are at most two. In `H_D` there are exactly two, `x,y`, since four
degree-seven sites are in `W`. They lie in different retained
roles and cannot share a `W` neighbor. Put `T` for the four
singleton W rows of `D`, in a fixed order. All signs on
`T∪{x,y}` are fixed by the pinned `W`, its three known supports,
and the required `xy` edge.

Consider a retained role `A` with `b_A=10`. It has six singleton
rows `S_A` under the extreme roster premise. Its six degree-seven
sites are precisely `S_A`. The restriction of any card isomorphism
`H_D→H_A` to the degree-seven sites must be an isomorphism from
the preceding six-vertex graph onto `W[S_A]`. This is only a
restriction: it need not send `W` to `W`. For the two b10 roles
in `(10,10,12,16)`, separate isomorphisms must be allowed.

## Exact trace subtraction on the pinned card

For an ordered list `U` of four sites in a card, the trace of a
vertex is its four adjacency bits to `U`, including a zero self
bit when applicable. The card trace histogram counts **all** 26
vertices, including `U`, by trace. An isomorphism preserves this
histogram to the correspondingly ordered image list.

Select a candidate degree-seven isomorphism for `H_D→H_A`.
Let `U` be the ordered image of `T`; all its elements are in
`S_A⊂W`. The full histogram to `T` in `H_D` is known: every
edge incident to `W` there is pinned. In `H_A`, the part of the
histogram from `W` and the two retained roles other than `D` is
known (these are 20 sites). Subtract each of its 16 bins from
the histogram of `H_D`. The difference must be nonnegative, sum
to six, and have correct marginals, because it is exactly the
histogram of the six `D` columns restricted to the ordered `U`.
A positive bin cannot contain both endpoints of a `W` edge by
triangle-freeness. This test uses no unknown cross edge.

To enforce simultaneous compatibility, enumerate the unordered
multiset of six actual `D` support columns over all eight `W`
rows. Triangle-freeness forbids a column meeting both endpoints
of a `W` edge. The crown one-wing cap is `α(W∪D)≤6`: an independent
set in this window can add three mutually nonadjacent moved sites
from the other three roles. Thus for every independent `J⊂W`,
`|N_D(J)|≥|J|`; otherwise `J` plus its nonneighbors in `D` already
exceeds six. In particular two singleton rows have different
slots: if they are adjacent this follows by triangle-freeness,
and otherwise the inequality on their independent pair proves it.
Fix the four singleton rows to four distinct temporary slots;
try all three-subsets of six slots for each triple row, apply the
triangle and one-wing constraints, then sort columns. Every
physical support has a labelling in this enumeration, with no
assumption on support symmetry. For a single candidate `x,y`
there must be **one** such multiset that meets the trace demand
for some image `U` for each comparison `A`. The chosen image lists
can differ between comparisons. A union of supports individually
compatible with different cards is not sufficient.

As a final weak capacity test, delete `x,y` from the pool of
potential neighbors of every `D` vertex. A `D` column can only
contact a retained vertex with disjoint `W` support. Every other
exterior vertex in `H_D` needs at least one such possible contact,
since it is not degree seven in `H_D`. A `D` column of size `s`
needs at least `7−s` possible exterior contacts in total. For
each retained role `A`, at most `6−|S_A|` vertices of `D` can
lack a possible contact to `A`, because `H_A` has exactly that
many exterior degree-seven sites (some may be in other roles).
An empty joint choice of `x,y` and support multiset excludes the
pinned row under the hypotheses. A nonempty choice is a necessary
condition only; it is neither a compatible full card isomorphism
nor a physical completion.

## Other all-W anchors

More generally let `K` be the common degree-seven count, and let
`S_i` be the singleton W rows of role `i`. The above test works
against any retained role with `|S_i|=K`, not just a size-ten
role. In particular a retained size-11 role with one triple and
one double or size-12 role with two triples has six singleton
rows and supplies another comparison at `K=6`. The same
omitted support must meet all three comparison demands. For a
general omitted role `D`, enumerate `K−|S_D|` exterior high sites,
an integer in `[0,2]`. When it is zero or one, there is no exterior
high-high edge to prescribe; otherwise impose the edge as above.
Use the full ordered `S_D` (not necessarily four roots) for traces.
The local support enumeration just uses all subsets of the specified
row size at each nonsingleton row. Replace `6−|S_A|` by `K−|S_A|`
in the final capacity test. When no retained role has `|S_i|=K`,
this version provides no veto.

At `b_max=15` and `b_min=10`, the minimum role has six W
singletons. Indeed its two excess incidences can be two doubles
or one triple; the triple would give seven distinct singleton
slots in a six-set, impossible by the one-wing argument. Hence
`K≥6`. The omitted role has seven excess incidences and at most
two excess at a row, so at least four nonsingletons, at most four
singletons, and `K≤4+2=6`. Therefore `K=6`, the omitted row sizes
are four singletons, one double and three triples, and a b10
comparison is available in either `(10,10,13,15)` or `(10,11,12,15)`.
For `(11,11,11,15)` one must not assume `K=6` or the existence of
an anchor. These statements about other profiles are necessary
conditions, not a census or an exclusion of a profile.
