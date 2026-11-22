# Round 11: middle tranche and pinned order-21 completion

## Mixed d8 j2 order25, minimum two, path/middle only

PID 3097303 completed at 04:00:44 CET. Binding matched all 21,236
ordered receipts against all 12 shards and raw graph6 labels,
recorded DIMACS digests and hashed the compressed proof bytes.
The A role list is byte-identical after sorting. The producer's
11,205.6 CPU-s certificates passed both CakeLRAT and lrat-check.
The 69,278 roles of the matching arm are not included.

From `scratch/G/round10` (`ulimit -v 16777216`):

```sh
root=../../..; py=$root/opt/venv/bin/python; src=$root/ralph/lanes/G
nice -n 5 timeout 155s "$py" -B "$src/bind_strip_batch.py" \
  r25.d8.middle.keys ../round7/lowdegree25.raw.g6 r25.d8.middle.rebind \
  --batch r25.d8.middle.keys r25.d8.middle 12 r25.d8.middle
cmp r25.d8.middle.rebind/certificates.tsv r25.d8.middle.bound/certificates.tsv
cmp r25.d8.middle.sorted r25.d8.middle.A.sorted
```

## Direct pinned order-24 window: exact scope (hand)

Only the mixed `(2,7,4,27)` pin with the strip premises in
`rows/residual_mixed_windows.md`, with B noncross d8 j1 or d9 j2,
and a retained noncross anchor `s` of degree two in `T`. Here `δ(T)≥2`
already, so this is a specified type of minimum-degree vertex,
not all windows with minimum two. At other orders an equality
anchor need not be a minimum-degree vertex.

Take `T−N_T[s]` of order 21 and mark the ordered 3+4 retained
anchors. Every valid lift can be labelled as a source mark, `s=21`,
and its two distinct exterior neighbours at 22 and 23. All core
pairs are fixed. The edge 22/23 is absent by triangles; their other
contacts inside `T` remain free. Try both assignments to A/B and all
hole pairs not already occupied. G has roots 24,25, pivots 26,27 and
then common/A-only/B-only exterior positions. As in the fully pinned
formula, triangles forbid all cut-exterior edges except between the
two exclusive groups. The exact strip profiles impose the singleton
and double counts, with the A-centre's two noncross doubles among
three options: two are implied by six fixed pivot contacts and four
singletons. Exterior degrees are six d7 (singleton on both sides)
and 22 d9.

On the restored three-side, exactly one old-only signature slot is
missing from the generic 15; it is either consumed by a designated B
double hole or realized on the opposite-exclusive group. Neither 22
nor 23 can fill that slot because both touch `s`. Pin the one needed
slot to the first label of its group; when consumed as a hole, every
label of the group meets `s`. No restriction to the catalogue's
singleton deficit is coded. The opposite group and all other support
assignments are free except for optional lexicographic ordering.
Relabel either exclusive group within its free suffix by its support
row, and independently relabel 22/23 by their core contact rows;
both sorts preserve lifts. Mandatory eight-set cuts in `T` use 22/23
plus every independent six-set of the core; these are precisely the
possible independent eights since the core has α≤6 and `s` meets
both added neighbours. The eager ten-set cuts use a core six-set,
an exclusive trio and the opposite pivot. Omitting other independent
ten-sets only weakens the formula.

The optional neighbourhood row uses a fixed independent core set `I`
and a set `S` of fixed neighbours of one center outside the core. In
a triangle-free graph `S` is independent, so at least `|I|+|S|−9`
members of `S` must touch `I`; otherwise their untouched complement
with `I` gives an independent ten-set. This was tested separately
and not used in proof production.

## Controls and prices

Literal contact-mask enumeration matches SAT on all 42 ordered
marks of the 410-graph order-eight control. At singleton cap two
all 42 are negative; at cap three all are positive with 2,235 distinct
unordered lifts, with or without symmetry sorting. Each literal
positive passes full triangle and independence checks. The additional
row passes C13, C35 and Exoo39 at their α and rejects a star at a
tighter α. Both pivot-swap identities pass 14,428 independent-triple
tests on the three graphs. A independently plants a real order-24
addback in both orders and exercises consumed/retained branches on
physical double-deficit mutations rejected as Ramsey parents
(`scratch/A/strip11/short.cnf.log`).

Same four dispersed order-21 marks: **100,569** literal weak lifts
(0.25 CPU-s, count only) versus **27 d8 + 1 d9** direct roles.
This measures queue compression, not speedup against fully solving
the literal lifts. The independent structural census on 6,160 marks
yields 49,597 d8 and 1,798 d9 roles (2.51 CPU-s). The pivot swap
removes 30,800 d8 B-small roles; d9 roles are all A-small.

| Same 27 d8 roles, 16k conflicts | Unchecked UNSAT | CAP | CPU-s |
|---|---:|---:|---:|
| Eager baseline | 0 | 27 | 41.98 |
| Neighbourhood and window-degree cuts instead of eager | 0 | 27 | 65.81 |
| Eager + sorted slots | 4 | 23 | 32.15 |

At 50k conflicts, eager/sorted pilot production and fresh replay give
**7/27 d8** (three A-small, four B-small already covered by the swap)
and **0/12 d9** across the dispersed d9 list. All others capped. All
seven CNF digests and 22,268,904 compressed trace bytes agree across
dual replays. The d8 price is 104.99 CPU-s; d9 55.49 CPU-s. The d9
projection of ~2.3 CPU-h covers **only a 50k-conflict capped sweep**,
not a complete proof price. No production queue is justified.

From `scratch/G/round11` (`ulimit -v 16777216`):

```sh
root=../../..; py=$root/opt/venv/bin/python; src=$root/ralph/lanes/G
keys=../round10/short-anchor.full.keys
nice -n 5 timeout 65s "$py" -B "$src/test_pinned_anchor.py" \
  ../round10/short-anchor.control.keys --control
nice -n 5 timeout 65s "$py" -B "$src/test_pinned_anchor.py" "$keys" --count 4
for degree in 8 9; do
  nice -n 5 timeout 30s "$py" -B "$src/pinned_anchor_window.py" "$keys" \
    --degree "$degree" --count-only
done
nice -n 5 timeout 175s "$py" -B "$src/pinned_anchor_window.py" "$keys" \
  --degree 8 --count 4 --eager --sorted-slots --conflicts 16000
for shard in 0 1; do
  nice -n 5 timeout 110s "$py" -B "$src/prove_pinned_anchors.py" "$keys" proof.d8 \
    --degree 8 --parents 4 --shard "$shard" 2 --replay
done
```
