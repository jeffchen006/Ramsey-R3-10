# Round 23 — two-root cut for the e69 triple column

**Result (hand + enum + local cert, pending critic):** in a saturated
32/e108 residue with every d6 puncture at e69 or e70, no d6/d6 pair has
codegree three. The e69 triple column therefore needs a high-degree
partner. Remaining: e69 type I, high partners of type II, e65..68, and
addable keys; floor and missing-five count unchanged. The dispatch
sections are chronological; terminal results are at the end.

## Bound and dispatch, 20:54 host clock

Work on a proper finite saturated subcase, not the 25-vertex e69 or
e109 catalogue. Assume two nonadjacent degree-six vertices `u,v`, each
with a 69-edge puncture, have exactly three common neighbors `A`, all
of degree six. Let `B=N(u)\A`, `C=N(v)\A`, and `X=H-N[u]-N[v]`.
In this first batch also impose `e(B,C)=3`. Saturation makes each site in
either private triple hit the other triple, so these three edges are a
perfect matching. `H[X]` has order 21, independence number at most six,
and `108-39-39+18+3=51` edges. GR Table 12 gives exactly four seeds at
that level, sourced from the already count-checked lane-B order-21 file.

The smaller M8 control exhausts all 256 cross-shore assignments, with
independent literal checks: 0/4/4 accepted for alpha bounds 2/3/4.
Rank 1 builds in 1.77 CPU-s, solves in 0.44 CPU-s (a 59,271-byte LRAT),
and checks in 2.01 CPU-s via two checkers. At the pilot rate the remaining
three are about 13 CPU-s, two slots. Each rank has a 65 s solver wall
cap, per-process 90 CPU-s, 16 GiB VM and 32 MiB single-file limit.
Three additional in-flight job directories reserve <0.20 GB, and the
first-pilot files account for <0.01 GB. This price is not an e69 source
or lift price; it covers only this four-card marked subcase.

## Compact successor dispatch, 21:03 host clock

The same marked pair with cross counts 4, 5 or 6 gives 140, 717 and
5,167 jobs, respectively, over four listed cross boards. Both edge-52
boards, one interior edge-53 stem and one interior edge-54 stem pass both
checkers with only the I9 clauses using six stem vertices. If this
relaxation returns SAT the worker restores sizes five and six, then all
sizes. Only checked UNSAT closes a key. Compact pilots took 0.49–0.61
CPU-s build/solve/check and 4,565–6,139 compressed proof bytes per seed.
Projected for 6,024 keys: ~1 CPU-h plus overhead, ~30–60 min wall on
two slots, ~30–37 MB proof payload. Estimate only, not a bound. Use a
117 MB charged archive guard, 90 CPU-s/16 GiB VM per process, 65 s solver
wall, 32 MiB per raw file, 2 MiB per compressed proof, and a 3 h supervisor
cap. Pilot files <20 MB; two reserved staging slots <95 MB combined.
Scope is only the marked d6/d6 pair with all three common neighbors d6.

## One-low dispatch, 21:14 host clock

Below, the ID4 screen supersedes the stopped 441/6,024 compact queue.
For exactly one low common neighbor, impose the additional premise
that every degree-six puncture has at least 69 edges. Its stem row is an
independent dominating 4-set of degree sum 22 (proof below). At each
of e55/e56/e57/e58 the two independent scans retain 1/39/342/1,148
seeds, each with a unique such set. The Cartesian product of the three
common-degree profiles and compatible cross boards is **1,992** marked
keys (40/383/1,569 at profiles 677/678/688). No 25-vertex census required.

In four dispersively chosen jobs the two checkers accept the six-only
relaxation in every one, with 0.44–0.55 CPU-s per job and compressed
proofs from 24.5 KB to 129.1 KB. Estimate 0.3 CPU-h plus shell/I/O,
~12–35 min wall on two slots; ~108 MB if the small pilot mean persists,
not a guarantee. Use a separate **105 MB** charged archive guard,
restoring smaller independent-set constraints only following a SAT
relaxation. 90 CPU-s/16 GiB process limits, 65 s solver wall cap,
32 MiB raw/2 MiB compressed cap; ~95 MB conservative live reservation
and ~36 MB existing artifacts. A guard or cap leaves open jobs.

**Supersession at 21:15.** Stop the broad two-slot wave after 59 eligible
duals. Let `j` be the number of A–A double masks and `b` the number of
B–B double masks in the puncture at `u`. Counting incidences among
its six doubletons gives `b=21-sum(deg(A))+j`. The opposite private
shore contributes `q-3` distinct B–B masks (its row sums are 1/2),
so `e(X)=51+q+j-b<=54+j`. With a low common row `j<=2`, hence `e(X)<=56`;
even with all common rows high, `j<=3` gives `e(X)<=57`. The one-low
manifest reduces to **160** jobs (40/41/79), all on the independently
screened e55/e56 seeds. Adopt the 59 receipts; 101 residuals are priced
at ~50 CPU-s plus overhead, a few minutes on two slots. The charged
guard is reduced to 25 MB. Earlier pilots beyond e56 are redundant.

## Hand coverage proof

Let `H` be saturated triangle-free on 32 vertices with 108 edges and
`alpha(H)<=8`. Its degrees are 6–8 by B-040. Mark a nonadjacent pair
`u,v` with degrees six, codegree three, and 69-edge punctures at both
ends. Necessity of a second e69 puncture is automatic if every d6
puncture has at least 69 edges: B-040 gives an upper bound of 70, and
the all-single/double e70 mask pattern has no triple.

Write `A=N(u)∩N(v)`, `B=N(u)\A`, `C=N(v)\A`; all three sets have
size three. The only edges among `u,v,A,B,C` besides root spokes are
`B`–`C` cross edges, by triangle-freeness. Every `B` site must hit `C`
by saturation with respect to `v`, and conversely. The puncture at
`u` has `v` as its sole triple column by B-042. Every `C` site is a
singleton or double with respect to `B`, with no repeated doubles;
the reverse argument applies to `B` with respect to `C`. Thus the
cross graph has no isolated vertex, max degree two, and no four-cycle.
Its only components are paths or a six-cycle. Up to swapping the
shores and permuting within them the possibilities are:

| `q=e(B,C)` | cross components | code | labelled |
|---:|---|---:|---:|
| 3 | three edges | 273 | 6 |
| 4 | two 3-paths (centers on opposite sides) | 78 | 9 |
| 4 | edge and 4-path | 85 | 36 |
| 5 | 6-path | 94 | 36 |
| 6 | 6-cycle | 238 | 6 |

`X=H-N[u]-N[v]` is order 21 and has no I7 (add `u,v`). The edges
incident to the two neighborhoods count as `Z(u)+Z(v)-sum(deg(A))-q`
by inclusion–exclusion: edges incident to a shared row are counted
twice and the other doubly counted edges are exactly the cross edges.
The root edges are already included in these sums. Thus
`e(X)=108-39-39+sum(deg(A))+q`. The alternate `54+j` upper bound and
the absolute e57/e56 caps follow from the double count in the dispatch
section. For that count, each common row has exactly three singleton
columns (there are 18 in total, at most three per row), and uses its
root/other-root edges and `deg(a)-5` double incidences. Summing these
incidences over `A` counts A–A twice and A–B once, proving the equation
for `b`. Each opposite private site contributes a double if and only
if its cross-degree is two. This accounts for exactly `q-3` of the
B–B double masks. Distinct A–A double masks form a simple graph `D`
on `A`, so `j<=3`; when one row is low its degree in `D` is at most one,
giving `j<=2`.

**Small dominating rows (hand + enum).** For every `a in A`, its neighbors
other than `u,v` lie in `X`. They are independent and dominate `X`:
the centers `u,v` have no edge into `X`, so a nonedge `ax` must have
a common neighbor inside `X`. If `a` is low, its row is thus a size-four
independent dominating set. On the complete Table 12 e51..56 source
both the recursive and literal 4-subset tests found none through e54,
exactly one each on seven e55 and 183 e56 graphs, and none on other
e55/e56 graphs. Two low common rows cannot use the same X set: a
single A–A double is permitted per row pair, and no triple in `X` is
permitted. Hence **no such pair has two or more low common neighbors**,
even without the global near-tight premise. This subsumes the stopped
all-low queue. It uses the published class counts, not an assertion
that a fetched source is complete based only on an empty search.

**One low under near-tightness.** Suppose the low common row is `a`
and every d6 puncture has at least 69 edges. The other two A vertices
are columns for `a` and both masks contain `u,v`. The two masks cannot
both be doubles, and cannot both be triples by B-040/042; precisely
one is a triple. Therefore `a` has exactly one edge in `D`, and its own
puncture is e69. That one A–A overlap occupies its only double
incidence on *both* original roots; no B/C row hits any of its four
X neighbors. Its four neighbors in `X` thus have five total incidences
to the frame (three singly attached, one doubly attached to A). The
sum of their H degrees is `108-69-6-6=27`, hence their X degree sum
is `22`. The two ID4 routines agree on the weighted results, and this
weighted set is unique in each of the retained source graphs. All lower
stem levels are already impossible. The genuine one-low cover is:

| common degrees | e55 boards × seeds | e56 boards × seeds | total |
|---|---:|---:|---:|
| 677 | `q5: 1×1` | `q6: 1×39` | 40 |
| 678 | `q4: 2×1` | `q5: 1×39` | 41 |
| 688 | `q3: 1×1` | `q4: 2×39` | 79 |

**CNF binding.** The 189 primary variables are wires between the nine
frame rows and the 21 stem vertices; the roots have no X edges. Fixed
triangle-free shores imply that every possible non-fixed triangle has
two wires and one fixed edge. Exact saturation is an OR over direct
edge and all possible two-step paths (auxiliary AND witnesses may
always be chosen from an actual path). The full I9 constraint is a
cross product of independent sets on the two fixed shores with total
size nine. Removing constraints not using six stem vertices is a
relaxation, so UNSAT is still sufficient. Degree bounds constrain each
physical row and column; each private side has `36-sum(deg(A))-q` X
wires. The pin follows from the unique weighted row. Column witnesses
are ANDs of two wires, with at most one per mask, or none when the
mask already exists in the fixed cross board. Three-row columns are
forbidden in `X`; per-common double incidence is `deg(a)-5`; the low
row has exactly one A–A overlap. Sorting equal-degree common rows is
an automorphism of the frame that fixes the pin. For the matching
and six-cycle, sorting B rows is also allowed: any B permutation lifts
to a paired C permutation via the matching (or the missing matching).
No exchange of physical X vertices or support multiplicity is assumed.

**Remaining scope.** This does not classify a pair with all common
vertices high, a high-degree codegree-three partner, the e69 no-triple
pattern, or any addable missing key. No order-40 candidate or floor
increase. A separate mask-only count (44 -> 16 row orbits) applies the
degree-one condition on low common rows around a single e69 triple
mark under near-tightness; it uses neither d6 on the other root nor
the finite lift, and is not a census of extendable graphs.

## All-high refinement: q5 and q6

The neighbor sum at either root is 39. Each private triple has degree
sum at least 18, so `sum(deg(A))<=21`. With no low common row, all
three common rows have degree seven and all six private rows have
degree six. In the one-low batch the 79 profile-688 proofs are redundant
by this bound; the other 81 prove the one-low scope. For all-high,
`b=j` from the double count. Also if the cross-neighborhood union of a
private-row pair on one side is the whole opposite shore, that pair
cannot occur as a double at any X site. Such a site could not also
touch A by the root codegree bound, nor touch the opposite private
shore by triangle-freeness, contradicting saturation with the other root.

**q5, hand.** Label the cross path
`b0-c0-b1-c1-b2-c2`. On the B side two pairs already occur in the
fixed opposite shore (`b0,b1` and `b1,b2`); the remaining pair `b0,b2`
has full opposite-neighborhood union and cannot occur in X. On the C
side the same argument forbids the remaining `c0,c2` pair in X. Thus
`j=b=2`. Every X site with no A contact has exactly one B and one C
contact. There are eight such sites, since the 15 A wires share two
doubletons and have no triple. The singleton quotas on these eight
sites are `(3,3,2)` on B (one fixed singleton at `c2` hits `b2`) and
`(2,3,3)` on C (one fixed singleton at `b0` hits `c0`). These quotas,
on the nonedges of the cross board, force 2 sites on `b2,c0`, 3 on
`b0,c1`, and 3 on `b1,c2`: `b2` has only nonedge `c0`, `c1` has only
nonedge `b0`, and `b1` has only nonedge `c2`. Call the triple for
`b0,c1` the set `F`. The degree-six row `b0` has frame neighbors
`u,c0`, the three sites of `F`, and one additional site `x in X`.
The row `c1` has exactly `v,b1,b2` and `F` as its neighbors. The site
`x` cannot be adjacent to `c1` (its six neighbors are already fixed),
to `v` (it lies in X), to any site in `F` (they share `b0`), or to
`b1,b2` (no B–B double in X). The nonedge `x,c1` has no common
neighbor, contradicting saturation. No global near-tight assumption
is needed for this q5 argument beyond the two e69 root cuts.

**q6, hand conditional on the near-tight one-low exclusion.** Index
the private shores so their nonedges are precisely `b_i,c_i`. All
three B–B doubles and all three C–C doubles occur in the cross graph.
Now `j=3`; each A row uses both its double incidences on the other two
A rows, so no X vertex hits both A and a private row. There are exactly
nine X sites not hitting A. Each has one B and one C contact, hence it
hits a matched nonedge `b_i,c_i`. Each of the six private rows has
exactly three X neighbors (degree six, with one root and two cross
neighbors), so the nine sites split into three triples `F_i`, each the
whole common neighborhood of `b_i,c_i`. There are no edges from A to
any `F_i`. The eight low rows `u,v,B,C` form the cube `K4,4` minus a
perfect matching, with opposite pairs `u,v` and `b_i,c_i`. Re-root at
any of the latter pairs. The remaining six low rows are precisely its
private shores, with q6 again (explicitly, the three cross nonedges
are the other opposite pairs of the cube). By near-tightness the two
root cuts are e69, and the exclusions for one or more low common
neighbors make their common triple all high. The preceding no-mixed
argument for the new frame implies no edge from `F_i` to any of the
other three common triples. Each triple is independently an independent
set, being contained in a root neighborhood. This yields an independent
12-set, impossible. Both q5 and q6 rely on physical contacts, not a
claim that a symmetric approximate model is an actual completion.

Thus for a near-tight marked d6/d6 codegree-three pair, only the
all-7 common triple and cross q=3 or q=4 survive these results;
their possible X edges are exactly 54 or 55, respectively.

## q3 matching dispatch

The three common A rows are now independent dominating 5-sets in X.
Their pairwise intersections have size at most one and their triple
intersection is empty. For one row meeting `k` other rows, `2-k` mixed
double incidences remain on each root cut. An unshared X site of degree
four costs at least one of these mixed incidences by the H degree floor;
degree three costs two, and a shared site of degree at most three is
impossible. This is the filter in `idjoin_r23.c`. The smaller C6
has exactly one join of three disjoint independent dominating pairs;
P6 has none. At e54 the filter retains 906 of 5,167 stems. At e55,
2P3 requires `j=1` and retains 9,237; P4+edge allows `j=1,2` and
retains 12,805. These e55 rows are not priced for production.

Four q3 pilots at dispersed ranks all dual-check with the six-only
relaxation. Build/solve/check price 0.66–0.73 CPU-s per seed, zipped
proofs 92–129 KB. Estimate for 906: 0.18 core-h plus overhead,
~12–25 min wall with observed host contention, ~100 MB proof payload.
Two single-core slots, 12 MiB raw-file caps, 110 MB charged archive
guard, 60 min supervisor wall cap. Peak B growth budget assumes 70 MB
existing, 110 MB archive and <57 MB simultaneous reserves. This is only
the profile-777 matching board; q4 remains open.

## Four-edge boards: both excluded under near-tightness

**Two 3-paths (hand + enum).** Label the cross edges
`b0-c0,b0-c1,b1-c2,b2-c2`. Both missing private pairs on either side
have full opposite-neighborhood union, so no private double can occur
in X, and `j=b=1`. Exactly 14 X sites touch A, one of them twice.
The 7 sites with no A contact each hit exactly one B and one C.
The no-A singleton quotas are `(1,3,3)` for B and `(3,3,1)` for C
(the two fixed opposite singles spend two places on the corresponding
center). Since `b0,c2` are each nonadjacent only to one another across
the cross board, one of these seven sites, call it `z`, hits them both;
the other six meet the leaves `L={b1,b2,c0,c1}`.

`W=A∪L∪{z}` is an independent eight-set. There are 13 X sites with
exactly one A contact. Each of the four leaves has at most one mixed
A contact in X: it has two double incidences in its root cut, one already
spent in the fixed opposite shore, and there are no private doubles in
X. Thus at most four of the 13 sites have a contact in L. Of the rest,
at most three can miss z: at most one per A row can have that A row as
its sole contact in W by B-042's Hall inequality. It follows that z
needs at least six X contacts. As it already hits `b0,c2`, it has degree
exactly eight and precisely six X neighbors, all among these sites
with one A contact and no L contact. Triangle-freeness blocks any
`b0,c2` contacts at those neighbors. So each is a **pure** A singleton,
with exactly one wire to the whole frame.

Consequently `deg_X(z)=6` and its X neighbors have X degrees at least
five. If such a neighbor x has `deg_X(x)=5`, it has H degree six and
already meets a degree-seven A row and degree-eight z. Thanks to the
≥69 premise, its neighbor degree sum is at most 39: every other H
neighbor must have degree six. In X, those other neighbors can have
degree at most five (every X site has at least one wire). If they have
degree five they must be A singletons: sites with no A contact have
two wires (one on each side by saturation), and double A sites also
have two wires. Finally any X vertex of degree ≤3 must hit A, since
without A it has exactly two wires. The three A rows are independent
dominating 5-sets, with exactly one pair overlap of size one and no
other overlap. The resulting necessary join is **empty** on all
27,289 e55 stems. The recursive C join and an independent literal
center-first Python enumeration agree; the latter even drops the
generic per-row mixed-incidence degree-budget inequality. It finds
354 potential centers on 353 graphs before the row join, zero after.

**Four-path plus edge (hand).** Label the cross graph with the isolated
edge `b0-c0` and path `c1-b1-c2-b2`. The fixed private double masks are
`{b1,b2}` and `{c1,c2}`; full cross-neighborhood unions forbid all other
private doubles in X except `{b0,b2}` and `{c0,c1}`. As `j=b`, the two
possibilities are `j=1` and `j=2`.

If `j=2`, both exceptional doubles occur. Their X sites must have
supports `{b0,b2,c1}` and `{b2,c0,c1}` on B/C (the only permissible
opposite contacts), and cannot hit A. They are distinct. All remaining
no-A sites each hit one B and one C. Without spending the two exceptional
columns the no-A singleton quotas are `(2,2,3)` and `(2,3,2)` (fixed B
singletons at `c0,c1`, fixed C singletons at `b0,b2`). The exceptional
columns spend one `b2` singleton and one `c1` singleton. The resulting
quotas `(2,2,2)` on each side force two single-single sites on each
of `b1,c0`, `b0,c2`, and `b2,c1`: `b1` and `c2` each have only one
cross nonedge, after which the remaining quotas force `b2,c1`. This
gives `b2,c1` four common neighbors counting both exceptional sites,
contrary to the near-tight cap three on a d6 pair.

If `j=1`, there are no private doubles in X. By the same quotas,
there are two no-A sites each on `b1,c0` and `b0,c2` and three on
`b2,c1`. Call the latter triple F, whose members hit no A row. The
degree-six path endpoints `b2,c1` each have exactly one further X
neighbor, say `x,y` respectively, with A contact (their three X
singleton columns are exactly F, and their fixed cross contacts have
cross degree two). If `x=y`, the pair has codegree four. Otherwise
they must be adjacent: saturation for `x,c1` cannot route via F (all
are neighbors of b2), v (no X contact), b1 (no private double in X),
or directly to c1 (its neighbors already fixed). Only y remains.

Now re-root at `b2,c1`; its common triple F has all degrees seven
by the previously proved common-neighbor exclusion and degree-sum
bound. Its new private shores are `{u,c2,x}`, `{v,b1,y}`, with the
four-path `u-b1-c2-v` and isolated edge `x-y` (the two mixed X sites
have no other private contact on their own original side). This is
the same four-path-plus-edge case; `j=2` was just excluded, so apply
the endpoint conclusion for `j=1` to `u,v`. Their singleton triple
in the new X is A, and their extra X neighbors are `b0,c0`. These
must touch F according to that conclusion. But F has precisely
private contacts `b2,c1` by definition, therefore no `b0,c0` contact.
Contradiction.

The only still-unresolved d6/d6 codegree-three board under the ≥69
premise is therefore the profile-777 matching (`q=3`). This does not
remove the e69 no-triple type or a triple with a higher-degree partner.

## Terminal matching and fresh replay

Production finished 906/906 at 21:33, all mode 6, with 610.50 CPU-s
build/solve/check and 108,772,183 compressed LRAT bytes. There was no
guard stop, timeout, cap, or SAT leaf; charged total 109,859,383 B.
The independent literal 5-subset/degree-cost join reproduced the entire
5,167-row e54 join table byte for byte. `audit_duals` checked alpha,
triangle-freeness and order/size on every e51..56 source; a separate
canonicalization confirmed pairwise nonisomorphism at each published
Table 12 count. The terminal audit binds all matching keys and archived
proof hashes. Fresh replay rebuilt and checked all 906 proofs, 453 per
slot with exact log equality to each slot file, completing at 21:42:53.
622.91 CPU-s for the two replays. One-low fresh replay also completed
160/160. No new proof generation during replay.

**Combined scope (hand + enum + local cert, pending critic).** There
is no nonadjacent degree-six pair of codegree three in a saturated
32/e108 residue whose degree-six punctures are all e69 or e70. Hence in
that near-tight arm any e69 triple-column root has a degree-seven or
degree-eight partner; the all-single/double e69 pattern is untouched.
No claim on a missing class, on the e65..68 escape, or on `R(3,10)`.

For a future high-partner arm, the degree-one rule on a low A row
in the A–A double graph still holds, since it used only the original
degree-six marked root. The new result forbids an A–A double joining
two low common rows: those two low rows would have codegree three
(`u,v` and the double's X site). Among the degree-feasible e69 triple
mask patterns the literal row-orbit count is **44 -> 16 -> 14** after
these two restrictions, with common degrees 668, 677, 678 or 777.
This is mask arithmetic, not a census of extendable graphs. If `v` is
the high partner then `|X|=27-deg(v)`. For any low common row, the
four X neighbors still dominate X, and its 39 neighbor-degree sum
and at least five frame wires at these four sites give
`sum(deg_X)<=28-deg(v)`. Applying the singleton bound to an ID4 inside
X (alpha ≤6) gives `sum(deg_X)>=2(|X|-4)-12`. Thus a low common
row requires an X-ID4 of weight 20..21 at order 20, or 18..20 at
order 19. No complete or priced high-partner source follows from this.

Another immediate consequence in the near-tight arm: every pair of
degree-six sites has codegree at most two. If their layer has `s` sites
and one site has internal degree `r`, each of its `r` neighbors in the
layer has internal degree at least three (a root neighbor sum at most
39 allows only three increments over degree six). Its internal wedges
thus number at least `2r`. Their other endpoints must be among its
`s-1-r` internal nonneighbors, with capacity two each. Hence
`r <= floor((s-1)/2)`. For example, no degree-eight vertices means
`s=8` by the degree sum, and the low layer must be cubic: each of its
roots is e69 with three degree-seven neighbors. This is only a layer
restriction, not an exclusion of the maximum-degree-seven case.

## Replay entry points

From `scratch/B`, use `LC_ALL=C`, `PYTHONDONTWRITEBYTECODE=1`,
`ulimit -v 16777216`, a CPU limit, `nice -n 5`, and `timeout` for each
run. Let `R=work/e108_r23_pair`, `S=../../ralph/lanes/B/src`, and
`P=../../opt/venv/bin/python`. The count-checked source is
`val/r3_7_21.g6`; `pickg -eEDGE` separates the exact levels. Tools under
`build/` were compiled with `cc -O3 -Wall -Wextra` (source basenames).

```bash
timeout 30s "$P" "$S/paircut_r23.py" --control
timeout 20s "$P" "$S/paircut_r23_geometry.py"
timeout 40s build/idjoin_r23_literal <"$R/stems54.g6" | cmp - "$R/idjoin54.tsv"
timeout 85s "$P" "$S/paircut_r23_hall.py" "$R/stems55.g6"
timeout 40s "$P" "$S/paircut_r23_audit.py" "$R" --reduced --terminal
timeout 50s "$P" "$S/paircut_r23_audit.py" "$R" --matching --terminal
```

`src/paircut_r23_replay.sh` uses each receipt to rebuild its CNF from the
graph6 bytes and board/profile metadata, then checks both compressed
proof and new CNF hashes before running both proof checkers. It accepts
two arguments, the queue directory (`$R/reduced` or `$R/highq3`) and slot
index (0 or 1). Do not restart a live slot; each slot uses one CPU.
`ROUND23.sha256` pins the source, immutable receipts, disposition logs
and sources of the checked code. Compressed proofs are transitively
pinned via checked receipt hashes, not by independent listing of paths.
