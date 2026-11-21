# Round 6: exact max12 forest and count-pin pilot

## Scope and budget

Only the alternate maximum-root cover is used. The globally tight
class has `m=12`, all edge square counts 12 and nonedge codegrees 2..3.
The round-5 critic confirmed the three exact Farkas exclusions and
their forest consequence, not any exclusions among the 13 remaining
tight keys. Rootings within this class are a cover; the count pin
partitions the completions of a **fixed** labelled kernel, not the
unrooted graphs across all kernels. No forest premise is used at
max13..16 or on the original 110 minimum-root representatives.

Prior unrestricted eager SAT reached its 28 CPU-s cap on nontrivial
keys 22 and 110. The new encoding took 20.95 CPU-s for all 144 C16
solves. For key 34, use one matched unpinned pair and one matched
pin-seven pair: unfiltered eager, forest eager, unfiltered eager
with `k=7`, and forest eager with signed-square `k=7`. Limit each
to 48 CPU-s / 70 wall seconds and 16 GiB, at most two at once.
No whole-cover cost estimate is justified by these censored pilots.

The q22 LP pilot starts at the three t=0 keys and the already-tested
key34 at k=7, with two workers. The unfiltered key34 transport took
4.60 CPU-s; with forest and seed rows 16.48 CPU-s before speeding
up the window builder. Budget 35 CPU-s / 48 wall per probe (20 s
internal LP limit) and compare paired models on identical pins.

The compact SAT comparison at key32 uses the same rooted forest
constraint and compact counters on both arms, with vs. without the
global t=0 clause family. It is scoped to max12. From the 48 CPU-s
caps of all four earlier probes, budget two cores at 55 CPU-s /
80 wall seconds each. Use a 30,000-conflict first cutoff to record
comparable progress even if neither arm decides.

For the surviving choice of root in t=0 (key 32), compare the two
endpoint pins k=6,14 with and without q22 rows. The 20-second dual
probes on the same key were inconclusive at 24 CPU-s; use IPM as
previously useful on key21 and allow 32 CPU-s / 46 wall / 24 internal
LP seconds, two workers. This probes only the endpoints, not a k census.

## A nine-key cover of max12 (`hand` + existing catalogue)

Let `q22(e)` count squares through `e` whose two diagonals both
have codegree two. Let `p3(e)` count three-vertex path components
of the edge kernel at `e`. Set `S(e)=q22(e)+p3(e)`. These definitions
are invariant under swapping the two sides of the kernel.

In any triangle-free graph whose nonedge codegrees are 2 or 3,
write `n2,n3` for their global unordered counts, `A` for the number
of squares with two codegree-two diagonals, and `w` for the number
of codegree-three pairs whose common-neighbor triple has all three
of its pairs of the same codegree. Then

```
sum_e S(e) = 2*(n2 - n3 + w).
```

Proof: for each codegree-three pair `{a,b}`, put a graph on its
three common neighbors, connecting a pair exactly if its codegree
in the original graph is two. The sum of the edge counts `i` of
these three-vertex graphs is `n2-2*A`: each codegree-two pair defines
one square, and its other diagonal has codegree three unless it is
one of the two codegree-two diagonals of a square counted by `A`.
For a triple with `i=0,1,2,3` the number of degree-two vertices is
`0,0,1,3`, or `i-1+[i in {0,3}]`. Such a vertex `u` with the other
two common neighbors `y,z` gives a P3 in each of the kernels at
`ua` and `ub`: at `ua`, its center is `b` and the leaves are `y,z`.
The center has kernel degree `codeg(a,b)-1=2`, and the leaves each
have degree `codeg(u,y)-1=codeg(u,z)-1=1`. Conversely each P3 in an
edge kernel gives exactly one such pair and distinguished common
neighbor: take the P3 center and the root on the opposite side as
the codegree-three pair; the other root is the distinguished
common neighbor. Thus `sum p3 = 2*(n2-2*A-n3+w)`. Since `sum q22=4*A`,
the identity follows. The same degree interpretation shows that
`q22(e)` is exactly the number of isolated edge components of F.

In max12, `n2=360`, `n3=240`, from 30 nonneighbors and 72 two-walks
at each vertex. There are 180 edges, so `sum S=240+2*w` implies
global `s=max S >=2`. By the accepted forest premise and catalogue,
all possible scores are 0..3. Root at a maximizing edge. This gives
the following **disjoint unrooted partition**, with the indicated
rooted covers (not disjoint by kernel within a stratum):

| `s` | Chosen root keys | Additional premise on all edges |
|---:|---|---|
| 2 | 24, 25, 26, 28, 29, 32 | `S(e)<=2` |
| 3 | 21, 23, 27 | `S(e)<=3` |

Thus the max12 root cover needs nine instead of thirteen keys.
The four omitted keys can still occur at other edges; they have
not been refuted as rooted completion problems. If insist on the
separate subcase `t=max(q22)=0`, each edge is from {32,33,34}, with
`p3=2,1,0`, respectively. If `e32` counts edges with key 32, then
`240 <= sum p3 <= 180+e32`, hence `e32>=60`. Therefore **key 32
alone covers `t=0`**; no claim of a completion or contradiction.
The `t=0` subcase is a subset of `s=2`; don't add its key to the
nine again. Likewise in `s=2` at least 60 edges have score two.

`forest_score.py` replays the identity with direct pair and
component counts on the Clebsch control and the 6-regular positive
`C20(2,5,6)` control (codegrees 2 and 3 and alpha 6). It independently
scores each kernel's components, frozen in `scratch/D/seed_r6/forest_score.log`.
It independently enumerates the size multisets: a forest on 16
anchors with 12 edges and no isolates has four paths; a matching
of size at least seven permits zero or two odd paths. In the latter
case they must have opposite side imbalances, so any size multiset
allows only one rooted signature modulo side swap. The full
max-root catalogue also has the round-5 genbg check.

## q22 cap projection (`hand`)

Root at an edge maximizing `q22`, so the cap `t` is its number
of isolated edges. On an old root-to-anchor edge `ua`, fix the
side `N(u)-a`. For same-side anchors `a,b` other than the old
opposite root, a common fixed anchor (other than `u`) has
codegree three with `u`: it must have two F-neighbors, `a,b`.
If there is no such anchor, let `O2(a,b),O3(a,b)` count selected
outer masks containing `a,b` and having respectively two or three
attachments on that side. Then `O2+O3` is 1 or 2. The contribution
of this pair to `q22(ua)` is exactly `max(0,2-O2-2*O3)`: it is
one iff its only common neighbor besides `u` is a 2-block. Pairs
with a common fixed anchor contribute zero. The pair involving
the old opposite root contributes one precisely if `a` belongs
to an isolated F edge. Thus requiring every subset sum of the
linear terms `2-O2-2*O3` to be at most `t-fixed` is exact for
these root-to-anchor caps on integral selections. This is only a
necessary LP for caps on *all* edges. Group averaging remains
valid because every subgroup image satisfies the same entire
system of linear rows.

`check_q22.py` verifies the local expression exhaustively and all
360 root-local cap decisions on `C20(2,5,6)`, including 300 negative
controls, using an independent four-vertex square census. `q22=0`
transport on keys 32 and 33 remained undecided at the LP limit;
key34 and the matched k=7 relaxations remain feasible. This is
separate from the nine-key proof, which does not assume any LP
verdict from this round.

## Exact SAT and LP pilots (`enum` controls; target `open`)

- Root-to-anchor acyclicity: compress each degree-two opposite
  vertex to an edge on the fixed side, forbid parallel copies,
  and guess a strict total order with at most one preceding
  neighbor per vertex. A forest admits this order by putting parents
  before children; conversely the latest vertex of a cycle would
  have two predecessors. Outside arcs producing the known fixed
  six-cycle are forbidden eagerly. All other rerooted cycles are
  cut by their explicit edge witnesses; independence is checked
  on every candidate. The unfiltered arm uses neither forest rule.
- The signed pin uses `2*C4(X)+2*z=4*k-8` from `MAX_ROOT.md`, with
  `2*C4(X)=sum_{pairs of X}([c_X>=2]+2*[c_X>=3])`. The exact count
  `k` counts the masks with two attachments on both sides. The two
  SAT implementations each exhaust all 144 C16 control cells:
  plain, forest and seven disjoint signed count pins on each of
  16 keys. The exact sets match 13 unfiltered graphs and two forest
  graphs, including one with nontrivial path components. The
  tight signed C16 specialization (no C4 in X) was checked against
  the corresponding Clebsch control.
- On key34, all four unpinned/k=7 probes hit 48 CPU-s without an
  initial model or proof; peak RSS below 550 MiB. The compact
  key32 variant shares the four codegree thresholds and tight high
  rows. The no-2/2 clauses state that of the two diagonals of any
  square, at least one has codegree three. Each row is conditional
  on the two common-neighbor indicators for one diagonal. This
  admits the all-high K3,3 control and rejects tight Clebsch. Key32
  without this filter reached 30,001 conflicts in 50.46 CPU-s; the
  filtered arm hit the 55 CPU-s cap. Neither decided. Build size
  was 379,647 vars and 992,691 vs. 1,120,456 clauses. The matched
  k=6 and 14 IPM pins on key32 hit their internal limits in both arms.
- For independent boundary seed I, the X window avoiding I has
  alpha at most `d-|I|`. Add its small exact order cap and convex
  edge-floor rows, and bound each selected window vertex's window
  valence by `d-|I|`, since its neighbors are independent. Small
  floors and next-order emptiness for alpha 0..3 were checked
  exhaustively by `geng` and an independent-set recount. All 13
  rational C16 controls satisfy the rows. Key34 remains feasible
  with windows, with or without forest; key21 dual transport was
  inconclusive. These add overhead without a demonstrated target
  exclusion. Binomial pair enumeration reduced the key34 window
  build to roughly 5 CPU-s from 14–17 CPU-s.

All logs and measured limits are under `scratch/D/seed_r6/`; no
target UNSAT certification and no target candidate. Do not extend
the capped SAT or LP probes unchanged. Next, test a selective
constraint arising from the score-2 stratum or pin an exact small
support design in t=0, always with a matched baseline.
