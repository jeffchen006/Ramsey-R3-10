# Round 24 — low common row of a degree-seven or degree-eight partner

## Dispatch at 22:42 CET (estimates)

The exact degree-seven, low-common-row source through stem e49 has
0/0/0/0/289/7,227 unmarked graphs at e44..49, or 0/0/0/0/291/7,238
marked keys. The full 291-key e48 arm goes first, then the disjoint
2,158 marked e49 stems of minimum degree three. The 5,080 remaining e49
keys (minimum degree four) are not assigned; four e49 pilots are
individual receipts, not an exhaustive census of either arm.

On the same eight dispersed keys the first formula generated several
1.1–2.1 MB gzip proofs. The normalized formula plus LRAT dependency
trim and XZ produces 196–220,520 bytes, with both checkers accepting
all eight six-stem relaxations. Paired target stage CPU sums are about
0.7–1.2 s/key, not including all bash/startup/contended wall overhead.
Estimate ~0.65 core-h for 2,449 keys (planning bound ~0.9), 25–60 min
wall across two slots. Four e48 pilots imply ~18 MB payload; four
e49 pilots imply ~47 MB at 2,158 rows, exact tails unknown. Includes the
completed source price below (~0.13 core-h) separately. Both slots
use 72 MB retained guards, 12 MiB per raw file, 85 CPU-s per child, a
65 s solver wall cap and 16 GiB VM. Before launch there are ~67 MB of
local round files; the two guards and ≤76 MB combined live staging
reserve less than the round's 300 MB net growth. Caps leave keys open.

## Necessary marked stem shape (hand)

Let `H` be order 32/e108, triangle-free, saturated, with alpha at most
eight and every d6 puncture at e69 or e70. Use B-040/B-042 and the
round-23 d6/d6 exclusion as previously checked. Mark the e69 type-II
triple `uv`, with `d(u)=6`, `d(v)=r` in `{7,8}`. Let `A` be the three
common neighbors, `B=N(u)−A` the three u-private neighbors,
`C=N(v)−A` the `r−3` v-private neighbors, and `X` the rest outside
both closed neighborhoods. This note needs a low common row `a∈A`
of degree six. `Y=N(a)−{u,v}` consists of four independent X sites.

At `a`, the other two A sites are puncture columns containing both
`u` and `v`. They cannot both be doubles (duplicate mask), nor both
triples (only one allowed). Thus `a` is type II, one other A site is
the unique triple (giving a unique shared Y site `y'`), and the last
one contains just `u,v`. The A site sharing `y'` with `a` is high:
its codegree with `a` is three and the round-23 cut excludes d6/d6.
At `u`, the four Y columns all contain `a`, and exactly three are
singletons because all six singleton groups are full. The fourth is
already the double at `y'` from the A overlap. In particular there
are **no B–Y edges**.

The four singleton groups for Y at `a` are all size three and lie
inside `X−Y`: B and C already meet u or v, and the other A vertices
meet both. All remaining X columns there are distinct doubles, since
the one triple is already used. This gives `|X|=27−r`, `alpha(X)≤6`
(add `u,v` to a hypothetical I7), and an exact marked X mask census:

| partner | X order | Y singleton sites | Y double sites | d_X(Y) |
|---|---:|---:|---:|---:|
| d7 | 20 | 12 (three per row) | 4 distinct pairs | 20 |
| d8 | 19 | 12 (three per row) | 3 distinct pairs | 18 |

For d7 the four double pairs are a C4 or a triangle with a pendant
edge on the four sites of Y. Thus each Y degree in X is 4–6, not
only a sum restriction. The three `{v}` singletons at `a` must lie
in C; the rest of C are `{v,y}` doubles. Exactly `r−6` C–Y edges
occur, and they meet distinct Y sites **other than y'**: at `v`, at
most `9−r` columns can be singleton `{a}`, so at least `r−6` of the
three Y sites other than `y'` must meet C. The statement uses actual
wires and not just a rounded degree sum. The d8 geometry is recorded
but not lifted this round by this queue.

**d8 corollary.** Every Y site has H degree `4 + d_D(y) + m_y`, where
`D` is the graph of double pairs, and `m_y∈{0,1}` records the one A
or two C marks, all on separate Y sites. Minimum degree six excludes
`D` with an isolated site, i.e. triangle plus isolated. For `D=K1,3`
the three leaves must be marked; for `D=P4` both ends and exactly
one internal site must be marked. In either case the H-degree list of
Y is **(6,6,6,7)**, never with a d8 Y neighbor. A literal finite check
of all 3/4-edge subsets and distinct tag placements is in
`src/high_r24_geometry.py` and `geometry.stdout`. This is not a
degree-eight-partner exclusion.

**Common-degree/cross cap.** Put `S=sum d_H(A)`, `j` the number of
A–A doubles at u, and `b` the number of B–B doubles there. Each
A row uses three singles, the common triple and its root edge;
the remaining `S−15` incidences into six doubles comprise two per
A–A and one per A–B. Hence `b=21−S+j`. There are only three B–B
pairs, so `b<=3`. Three common lows would each require one A–A
overlap with a high common row, impossible. With exactly two lows,
both must overlap the same high A row and `j=2`. Thus `S=19` would
imply `b=4`, impossible; their common degree profile must be `668`.
Also `S<=21` since the three B degrees sum to `39−S` and are at
least six each. This rules out `688`; the low-common list is
`668,677,678` (not asserted realizable). Each C site is
singleton/double at u, with no repeated double, so `q=e(B,C)`
is at most `|C|+3`. Since `e(X)=69−sum d_H(C)+q`, this caps the
low-common d7 and d8 stems at e52 and e47 respectively. More finely,
`q<=|C|+b` and `j<=2`, so profile `678` has d7 cap e51 and d8 cap
e46. These counts do not close the higher
stems. If d7 and `delta(X)=5`, D must be C4 (the paw has a d4 site),
a possible source partition for e50..52.

The only internal frame edges besides spokes are B–C edges; the lift
leaves **all 12** such positions variable for d7. At `u`, the sole
triple is `v`, leaving exactly 18 singles and six distinct doubles
over `C∪X`. Thus `Z(u)=6+3+18+2*6=39`. The exact full edge count for
d7 is equivalently `e(C,X)=108−39−4−e(X)=65−e(X)`; no cross count or
degree profiles of C are preselected. Every pairing of marks of X is
kept, including two marks on the same graph. Frame normalization
chooses row 3 for the other A site meeting Y and row 8 for the unique
C site meeting Y. The three B rows and the remaining three C rows
can each be ordered by their X row words, since no roles inside
either block are pinned and permuting them transports all B–C
wires. No permutation of Y or assumption of X automorphism is used.

## Source completeness and known controls

For triangle-free order-20 X with `alpha<=6` and `e<=49`, minimum
degree is 2–4: the degree sum gives at most four and R(3,6)=18
gives at least two by a minimum-root puncture. Deleting that root
and its neighborhood yields an order `19−d` triangle-free graph
with alpha at most five and at most `49−d²` edges. We exhaust the
complete lane-B order-15/16/17 sources (`64732/2576/7`) inherited
from bootstrap, with 60,244 / 2,576 / 7 parents respectively after
the cap. `glue5` glues every possible independent neighborhood row
of a minimum-degree root; the `high_r24_source.c` wrapper only
changes the emitted leaf predicate. It retains a leaf if and only if
it has at least one unordered Y matching the exact census; recursive
enumeration prunes using only independence, individual degrees
4–6, and the total degree 20. No maximality of X is assumed.
Different raw roots are deduplicated with `shortg`, and an independent
Python combination loop then emits **every** Y marking of the retained
canonical graph, validating triangles and I7s as well. Sorted graph6
and literal mark ranks are in `source.le49.g6`, `plan.tsv` and
`plan.stdout` under `scratch/B/work/e108_r24_high/`.

As a calibration before the wave, the unfiltered e44/e45 run returned
15/479 distinct graphs, matching GR Table 12; the d2/d3/d4 source
and e49 pilots used the same gluer. The filtered source itself took
~388 CPU-s, and the independent decoded mark table ~62 CPU-s, before
small canonicalization/controls (~0.13 core-h total). e44..47 are
empty by this exact source screen, not by a SAT timeout. The e50+
source is not covered by the minimum-root cap here. For e49 the d3
subcase is determined by the source input root (all output degrees
at least d); no d4 key can be in that subcase.

## Priced successor: e49/min4/max5

Nauty selects 56 distinct e49, min-degree-four, max-degree-five
graphs, yielding **60** marked keys. The e49 source's other
min-degree-four slice has 5,013 distinct graphs and 5,020 marks
at max degree six; it remains unassigned. At e48, the same min/max
selection gave 12 marked completed controls, 10.57 completed-stage
CPU-s and 879,292 proof bytes. Extrapolation to the 60 keys gives
~53 CPU-s and ~4.4 MB proof bytes, before shell overhead. The two
successor supervisors wait for both a normal `FINISH` marker and
predecessor wrapper exit on their own slot. They first try two e49
keys per slot under 12 s solver limits and gate on dual proofs and
700 KB combined charged data. If admitted, they use the same job
routine and each slot's independent 8 MB guard. No lease overlap,
no extra compute on the current e49/d3 keys.

**Other e49 work (open).** `e49.min4.max6.profiles.tsv` partitions the
5,020 unassigned marks by the number of degree-six X vertices and
the C4/paw double-mask shape; 69 marks have at least six degree-six
X vertices. For common profile `668`, the two low A rows require
disjoint Y sets (a shared site would be a third common neighbor of
those two lows). Every e49 source with two marks is in min4, and
`two-low.plan.tsv` gives exactly 11 disjoint pairs on 11 stems, of
which four lie in the waiting max5 queue. Join that queue first to
avoid re-solving any already excluded parent. The degree/independent
high-row checks left all 11 possible, not a no-lift result. The
experimental `src/high_r24_two_low.py build` pins the second low
row in the existing normalized lift and the shared row's degree
eight; the first formula built successfully (27,069 clauses), but
no solve or proof is claimed for that new specialization.

## Further hand cut: at most two low common neighbors of any pair

This holds in the same saturated near-tight H, **with no degree
restriction on the two endpoints**. If `p,q` have three low common
neighbors, choose one of those lows `a`. The other two lows are
nonadjacent to `a` and both give puncture columns containing `p,q`.
The prior d6/d6 cut forbids a third row in either column (e69/e70
allow no column larger than three), so both are the identical double.
That contradicts the no-duplicate-double rule. Therefore every
B site has at most two low C neighbors (pair it with v).

With `g=sum_C(d_H(c)−6)` and `q=e(B,C)`, the d7 edge count is
`45+q−g` and the d8 count is `39+q−g`. For `g=0`, the new cap
gives `q<=6`; otherwise the prior caps `q<=7/8` apply. Thus **d7
ends at stem e51**, and **d8 ends at e46**. These are upper bounds,
not claims that every lower level is resolved.

At d7 e51, `q=6,g=0` has all B cross-degrees two and cross shape P7
(two distinct doubles, two singles), and `q=7,g=1` is C6 plus a leaf
with one high C vertex incident to the B vertex of cross-degree
three. At d8 e46, `q=8,g=1` is forced: exactly one C is high (d7),
it is a double, and each B hits exactly two low C. Its B pair are
the two singleton owners; the other doubles use the third B. All
of this uses just the frame and the lower bound on d6 punctures.

**The d8 e46 top board is impossible (hand).** Both endpoints of the
high double have cross-degree three. There is at most one high B site
because `sum d_H(B)<=19`, so at least one endpoint `b` is low. Now
re-root at `(b,v)`: their three common neighbors are precisely the
three C neighbors of b, with degrees `6,6,7`. A low root with a
triple must be type II, so this violates the `667` cut. Thus the
d8 low-common-row source ends at **e45**, not e46. Likewise in d7
e51 with `q=7,g=1`, the unique cross-degree-three B site must be
high. This restriction does not exclude the d7 e51 board.

## Low-fibre bound for the d8 arm (hand)

For any degree-eight vertex v in near-tight H, put `F=N(v)∩D6`,
`f=|F|`. Each member of F has five remaining neighbors outside
`N[v]`, all low except at most one d7: the increment 2 from v uses
two of its at most three neighbor-degree increments. Its remaining
neighbors cannot be d8. Every vertex outside `N[v]` has at most
two F contacts by the all-endpoint common-low bound. Hence at least
`4f` low incidences to `D6−F`, and `n6>=3f`.

In this near-tight arm `n8<=11`: the degree sum gives `n8<=12`;
at 12 there are no d7, and the 20 lows can contribute at most 20
edges to D8, since no low has two d8 neighbors. The 12-site D8
triangle-free graph has at most 36 internal edges by Mantel, so
the sum of D8 degrees is at most `20+72<96`. Consequently f<=6.

Now suppose v is a d8 triple partner with a common low a. Let
`l=|A∩D6|`, either one or two. Outside `N[v]` the low u has precisely
l F contacts, for a deficit of `2−l` against capacity two. For each
low common row a, three of its four Y sites are low and at most two
have a C wire. A Y site of a cannot meet another low common row:
that row and a would have u,v and Y as three common neighbors.
Thus at least one of the three low Y sites has just a single F
contact. Different low A rows have disjoint Y and u is not in any
Y, giving **at least two outside-low contact deficits**. The improved
bound is `4f <= 2(n6−f)−2`, or `n6>=3f+1`.

If f=6, this forces `n8=11`, `n6=19` and exactly two d7 sites. The
five neighbors per fibre site outside `N[v]` give 30 incidences.
At most `2(19−6)−2=24` go to lows, at most four go to d7, and none
to another d8. Contradiction. Thus any marked d8 partner with a
low common row has **f<=5**, with `n8>=8` if f=5. In particular its
C shore cannot be all low. This removes `q=6,g=0` from the e45
board list, and removes common profile `668` at e45 when g=1.
No e45 or entire d8 arm is claimed closed.

At d8 e45, only `(q,g)=(7,1)` or `(8,2)` remain. In the former,
some B site has cross-degree ≥3. A low B site cannot have degree
≥4 into C (every d6 puncture column has size ≤3), nor three into
C: its triple would have either three lows or profile 667. Thus
at least one B is high, forcing `S=20` and at most one high B. Since
`668` is ruled out at g=1, the common degree profile is `677`. The
three non-low neighbors of v then all have degree seven. Its unique
marked d7 Y site is outside `N[v]`, so `n7>=4`; together with f=5,
this forces `8<=n8<=10` in this board arm.

**Small d8 source prefix (hand + enum).** The generalized native
mask filter, compiled with `-DSTREAM -DSTEM_ORDER=19`, scans the
complete local `val/r37_19_le39.g6`. Nauty confirms 11/417/10,447
at e37/e38/e39, the published GR Table 12 counts. Exact degree-18
ID4 with three singletons per row, no degree-three row and distinct
double pairs leaves **zero** through e39, in 0.04 CPU-s. See
`d8.e39.input.count`, `d8.e39.screen.g6`, and `d8.e39.time`. The
independent pre-existing four-loop scan also finds zero ID4s of
weight 18 even without the exact mask shape (`d8.e39.literal.stdout`). Combined
with the separate hand cap, the marked d8 stem window is now e40–45.
No physical d8 lift, e40–45 source generation or credit for those
levels. The pilot rate would be ~8 CPU-s to screen the e≤41 catalogue
**if regenerated**; no e40/e41 cache was found in the searched local
lane data. Price generation and physical lift separately. For e≤45
every order-19 stem has min degree 1–4,
so the source theorem uses complete R(3,6) parents of orders 14–17,
with per-root caps e−d², not an assumed database for higher levels.
Three labelled mask controls retain the star and reject a triangle
plus isolated row and a repeated double (`d8.mask.controls.g6`,
`d8.mask.expected.g6`); these synthetic boards are not Ramsey inputs.

## Completed subcase at 22:50 CET (pending critic)

For d7 with a low common row and **`e(X)<=48`**, the exact source
has no graphs through e47 and 291 literal marked keys at e48.
All **291/291** keys obtained a depth-six dual LRAT; no open entries.
`e48.terminal.tsv` binds every rank, mark, graph6, compressed proof
and uncompressed proof/CNF digest; `e48.terminal.json` is the exact
anti-join against the complete e48 denominator. This is a scoped
hand + enum + local cert result, not a floor or missing-key debit.
The e49/d3 workers immediately advanced to the disjoint successor.

## Physical formula and proof checking

`src/high_r24_lift.py` binds literal graph6 bytes and four indices to a
32-site graph. The two roots, the marked a-to-Y wires, and all X
edges/nonedges are fixed. All actual possible other edges are Boolean.
Triangle clauses test every three-site combination; diameter-two
clauses use a fixed edge, a candidate edge, or a physical common
neighbor with both edges present. The I9 generator tests independent
frame and stem sets and skips any pair joined by a **fixed** a–Y edge;
the clause is over all remaining physical wires including B–C. The
six-stem form omits I9s with fewer than six X sites. If SAT, a worker
restores five-stem then all I9s. Checked UNSAT on a relaxation is
sufficient. For the generic floating-edge graph logic the 512 M8
assignments yield exactly 0/1/1 for independence caps 2/3/4, matching
literal triangle, independence, degree and saturation checks on every
assignment. The original nonnormalized pilot and normalized pilot use
the same marks; only the latter goes into the queue.

CaDiCaL's ASCII LRAT is reduced to the dependency cone of its empty
clause. This reduction itself is not trusted: cake_lpr and lrat-check
must each accept the resulting uncompressed proof, then the proof and
CNF are hashed and the proof compressed. A replay rebuilds the exact
normalized CNF, validates both input hashes and both checker markers.
Per-rank files hold the primary graph6 and Y as well as timings, depth,
checker logs and the compressed proof. There are no SAT-only exclusions.

For fresh critic rebinds, `src/high_r24_rebind.sh RANK NEW_DIR` reads
the frozen e48 row, verifies the compressed archive, regenerates the
exact normalized CNF in the caller's scratch and runs both checkers
on the rebound proof. Useful dispersed ranks: `4,73,141,201,283,291`.
Run under `nice -n 5 timeout 120s`; one leased core. Do not regenerate
the whole e48 deck for production credit. Both production checkers
were already run for every proof; fresh independent rebind is for review.

## Handoff snapshot (23:14:33 CET)

The live e49/min3 arm has **1705/2,158** duals, 453 unlogged,
zero attempted-open, 1229.5 completed-stage CPU-s and 13917860
compressed proof bytes. `e49.handoff.tsv`/`e49.handoff.json` are
immutable partial receipts; not a terminal proof or an estimate of
nonexistence. Both one-core producers and both waiting successors
remain listed in STATE. The live round directory was 102479420 bytes
including original pilots and staging. The global logical-disk read
timed out on another lane's moving directories; no global value is
claimed from that read. No candidate or floor/debit change.
