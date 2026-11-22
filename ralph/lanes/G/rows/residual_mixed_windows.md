# Residual mixed noncross pivots at e168

Scope throughout: exact e168 pin `(n6,n7,n8,n9)=(2,7,4,27)`, the two
adjacent degree-six roots and the strip hypotheses of `path_leaf_windows.md`,
one path/leaf strip A, and the opposite strip B either matching/incident
or path/middle. The A pivot is its noncross degree-seven centre `a`;
the B pivot `b` is noncross and has degree `d=8` or `9`. No whole
distribution exclusion follows from any subset of these windows.

## General cut, roles and coverage (hand)

Let `X` be the 28 vertices outside the roots and strips, and
`D_A=N(a)∩X`, `D_B=N(b)∩X`. Each has four private neighbours; their
sizes are six and `d−1`. Their overlap is precisely the codegree `j`.
Their paired antineighbourhood `T` has order `31−d+j`, with eight
retained anchors. Write `Q_A=D_A\D_B` and `Q_B=D_B\D_A`, of respective
sizes `6−j` and `d−1−j`. Because both selected pivots are uncrossed,
the eight retained anchors remain two independent four-sets with just
the one cross edge. Every retained exterior vertex has singleton or
double support on each marked side, with multiplicities at most four
for singleton and one for double.

For `d=8` there is one hole among the retained B anchor pairs and one
using `b`; for `d=9` both holes are retained. The retained A template
has all six doubles and four copies of each singleton. The retained B
template has respectively five or four doubles and four copies of each
singleton. Discard a role if a hole occurs as a double among retained
exterior vertices. Then exact multiset differences pin the A supports
on `Q_B` and the B supports on `Q_A`. These sets of labels can be
sorted independently and the `j` common vertices remain free. A's
two pivot-double slots are distinct noncross anchors and the unused
third noncross anchor is the other leaf; do not choose it ahead of
time. Degree signatures force six d7 and 22 d9 vertices in `X`, and
each d7 is a singleton on both sides. These are the same arithmetic
and completion clauses as in `mixed_pivot_windows.md`, with the cut
sizes above. Eager ten-set disjunctions are necessary only, and need
not encode all independent ten-sets.

Marked-degree contribution is at most
`(29−|Q_B|) + (43−2d−|Q_A|)` for the eight anchors. Each of the other
`|T|−8` vertices has degree at most seven. Thus the edge caps for
`(d,j)=(8,1),(8,2),(9,1),(9,2),(9,3),(9,4)` are respectively
`78,83,73,78,82,87`. They are safe upper bounds, not claims that the
endpoints are attained. For order 25 with δ=2 and order 26 with δ=3,
deleting a minimum-degree closed neighbourhood gives an order-22
`(3,7)` core. The prepared complete weak marked sources apply to
these minima and not to higher minimum degrees. Both orientations
of weakly marked representatives are tried.

## Isolate and leaf exclusion (hand)

An exterior vertex in `T` has two different strip neighbours, so an
isolated vertex or leaf is a retained anchor. With an isolate it is
not a cross endpoint. With a leaf at order 24, the crossed anchors
also cannot be the degree-one vertex: on A the cross endpoint has
eight exterior contacts before deleting `Q_B` (there is no double
with `a`), and `|Q_B|=6`. On B the crossed anchor has `8−h` exterior
contacts before the pivot cut, where `h` is its missing-double count
(one for matching, two for middle). It loses at most one through a
double with `b` and at most `|Q_A|` other contacts. For `d=9,j=2` this
gives at least `6−1−4=1` exterior contact. For `d=8,j=1` the matching
gives `7−1−5=1`; in the middle case `b` itself is deficient, so the
crossed anchor and `b` form a hole and the lower bound is `6−0−5=1`.
The cross edge adds one degree in each case.

Deleting an isolated anchor of order 23 gives an order-22 `(3,7)`
graph. Deleting a noncross leaf and its sole neighbour at order 24
does the same. That neighbour is exterior; no other exterior vertex
on either cut attaches to the deleted anchor. Consequently the core
contains disjoint independent 3- and 4-sets with exactly one cross
edge and every other vertex has a nonempty support of size ≤2 to
each side, with the same uniqueness and multiplicity caps.

There are exactly fifteen exterior vertices in that core. On the
three-anchor side their total capacity is exactly `3·4 + 3 = 15`:
four singleton copies per anchor and one copy per unordered pair.
Therefore every slot is filled. The crossed anchor of the smaller
side sees four singleton and two double vertices, plus its opposite
cross endpoint. This gives degree **seven** in the `(3,7)` core,
contradicting its maximum degree six (every neighbourhood is
independent). This is a hand exclusion, independent of the order-22
catalogue and valid using only the strip hypotheses above.

More generally, for every noncross marked anchor `s` in a weak paired
`(3,8)` window, **`d_T(s) ≥ |T|−22`**. The usual Ramsey inequality
gives `d_T(s) ≥ |T|−23`. Equality to that weaker bound gives exactly
the forbidden 22-core: all neighbours of a noncross anchor are
exterior, so the 3+4 marks remain and all 15 surviving exterior
vertices retain their nonempty supports. If `d_T(s)=|T|−22`, the
analogous order-21 core has 14 exterior vertices and exactly one
unfilled smaller-side slot. That slot must contain the cross endpoint
to prevent degree seven. Hence the smaller-side cross endpoint has
degree six and the other two smaller-side anchors have degrees at
least five in the core. This equality reduction also applies to pure
paired windows, not just the mixed pin.

### Computational cross-check (enum)

`leaf_window_core.py` enumerates each independent four-set B. The
two noncross anchors on the smaller side are exactly the vertices
outside `B∪N(B)`, because all exterior vertices meet B. It then
tries all possible cross endpoints with one edge to B and none to
those two anchors, and checks both support tables. The ordered small
control has 42 positive marks among 410 graphs, equal to independent
brute force (21 marks up to swapping sides). All 191 known order-22
cores are checked for validity. Their 183,053 independent four-sets
produce 6,411 preliminary pairs and **zero** pairs passing support.

Thus at the mixed pin: `d9,j1` cannot have δ(T)=0, and `d8,j1` or
`d9,j2` cannot have δ(T)=1. The full isolate and rooted-leaf sources
run separately with zero weak marks as a cross-check. No claim about
order 23 with δ≥1 or order 24 with δ≥2 is implied.

## Shared-support interval projection (hand)

For each opposite pair of anchors other than the cross edge, any
maximality witness must be in `X`: neither root sees both strips, the
strips are independent and there is only the unique strip cross
edge. Its endpoints have no common exterior neighbour by triangle-
freeness. The single-pivot relaxation checks the same strip pattern
and only the MTF cross-pair rows incident to a selected pivot. Joint
checks every such cross-pair row on **one** support assignment.

For every alternate noncross B pivot `t`, `j_t` is the number of
vertices in `D_A` whose B support contains `t`. The retained anchors
have degrees exactly

```
cross_indicator(s) + #{x∈X\D_A : s∈support(x), t∉B_support(x)}.
```

With order `31−d(t)+j_t`, their interval is `[max(0, 8−d(t)+j_t),7]`,
using `R(3,7)=23` and triangle-freeness. The earlier checked exclusions
give `j_t≤3` (d8), `j_t≤4` (d9); for d8 and `j_t=3`, the lower
endpoint is four by the checked δ(T)=3 exclusion. All rows refer to
the same B attachment variables. The generic interval/deletion
identities pass C13, C35 and Exoo39 (`52/455/569` nonadjacent pairs).
An independent set-valued placement oracle reconstructs an explicit
positive triangle-free support shell and pins it back into the joint
CNF. On the held-out negative, all 210 B placements were tried,
30 satisfy the preliminary single-B necessities, and none satisfies
the joint interval tests (no A-centre-double assignment can fix this).
`joint.control.log` records details. The shell is not a full Ramsey
completion.

The joint projection is a pilot comparison, not an extra dependency
of any proof run. Neither joint projection nor the higher-minimum
samples justify scaling a higher-minimum census.

## Mixed cut budget (hand; optional proof pilot)

There are `d+5−j` deleted exterior vertices; let `l` count the degree-
seven vertices among them. The two deleted roots and two pivots have
total degree `19+d`. The deleted induced subgraph has `d+8+f` edges:
one root–root, two root–pivot, `6+(d−1)` pivot–exterior and `f` between
opposite-exclusive vertices. Subtract the sum of deleted degrees,
then add the deleted induced edge count. This gives

```
e(T) = 112 − 9d + 9j + 2l + f.
```

The optional `--cut-budget` counts the same low-degree selector
twice using a fresh equivalent literal, and counts the possible
exclusive cross edges once. The general edge identity was compared
directly to induced edge counts on the 1,076 nonadjacent pairs in the
three extremal controls. The selected production runs do not use this
optional row.
