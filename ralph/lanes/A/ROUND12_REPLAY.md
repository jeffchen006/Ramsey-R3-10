# Round 12: independent binding of the alternative A pivot

**Scope:** exact mixed e168 pin `(n6,n7,n8,n9)=(2,7,4,27)`, the
accepted adjacent degree-six roots and strip hypotheses, original A
path/leaf noncross degree-seven centre `a`, noncross B pivot `b` of
degree `d`, and a noncross A equality anchor `s` in the original
order-24 pair window `T`. This is only the A-small subset of the
round-11 direct order-24 cases. There is no claim of completeness
for the high-minimum order-25/26 windows.

## Reroot identity and safe windows (hand)

All three pivots are independent. Write `D_x=N_G(x)∩X`,
`ε=d_G(s)−8`, `j=|D_a∩D_b|=d−7`, and
`τ=|D_a∩D_s∩D_b|`. Since `s` is noncross, it is either the other
leaf (ε=0) or a full anchor (ε=1). The slot lists give `|D_s|=7+ε`
and `|D_a∩D_s|=ε`. Equality means `d_T(s)=2`, not that the rerooted
centre is minimum. Subtracting the union from `D_s` yields

```
j' = |D_s ∩ D_b| = 5 + τ,
T' = G − (N_G[s] ∪ N_G[b]),     |T'| = 28 − ε − j + τ,
C  = T − N_T[s] = T' − N_T'[a], d_T'(a) = |T'| − 22.
```

The last identity of graphs is literal on the original labels: both
expressions delete `N_G[a]∪N_G[s]∪N_G[b]`. The unique directed A→B
cross edge survives both cuts. In `T'` the retained A holes are
`{a,cross_A}` for a leaf pivot, and also `{a,other_leaf}` for a full
pivot. For the full pivot, try either of the remaining noncross
anchors other than `a` as the other leaf. B holes do not change:
d8 has exactly one incident with `b`; d9 has none incident with `b`.
Try both assignments of the two weak four-sets to A and B, then
try both B shapes with the indicated cross endpoint.

| d | s | τ | j′ | order | degree of restored a | edge cap | supplied source |
|---:|---|---:|---:|---:|---:|---:|---|
| 8 | leaf | 0 | 5 | 27 | 5 | 91 | all |
| 8 | full | 0 | 5 | 26 | 4 | 86 | δ=3 only |
| 8 | full | 1 | 6 | 27 | 5 | 91 | all |
| 9 | leaf | 0 | 5 | 26 | 4 | 86 | δ=3 only |
| 9 | full | 0 | 5 | 25 | 3 | 81 | δ=2 only |
| 9 | full | 1 | 6 | 26 | 4 | 86 | δ=3 only |

For the edge caps, write `h_A=1+ε`, `h_B=d−7`,
`q_A=|D_s\D_b|`, `q_B=|D_b\D_s|`. The sum of the eight marked
degrees is at most `58−2(h_A+h_B)−q_A−q_B`: each side has
16 singleton slots and `6−h` double slots before the opposite-only
cut, each missing slot counts for at least one edge, and the cross
edge contributes two. All other degrees are at most seven because
`α(T')≤7`. Thus `e(T')≤floor((58−2(h_A+h_B)−q_A−q_B + 7(|T'|−8))/2)`.
Both lower-order caps lie within the old raw-gluer envelopes
(`e≤87` for `(25,δ=2)`, `e≤91` for `(26,δ=3)`); see
`scratch/G/round7/lowdegree{25,26}.full.glue.log` and
`ralph/lanes/G/ROUND7_REPLAY.md`. These covers depend on the complete
191 order-22 classes and the archived gluer/mark scans. The order-27
cover is A's independently reproduced 1,988 marks on 1,980 classes
from the complete McKay catalogue; see `PAIRED_WINDOWS.md` and
`scratch/A/path7/lineage27.log`. No padding of smaller hosts, and
**A-013 is not used**: `s` is not the centre pivot in that theorem.

## Binding and measured results (enum)

`audit_a_side_reroot.py` enumerates the round-11 A-small original IDs
using A's prior independent five-column hole oracle, not G's role
enumerator. For each supplied weak window and both orientations it
deletes each noncross A equality candidate of degree `|T'|−22`,
checks the original short-side singleton deficit, and compares the
induced marked role with the catalogue. The role certificate colors
both cross endpoints individually, both noncross groups, and the
exterior. Two gadgets encode the B holes (incident with `b` gets a
separate color at d8; both retained holes have the same color at d9).
Every link includes the actual 21-label permutation from the old
source record to the new window. It is checked against all edges and
colors, including gadget incidences, not just a canonical hash.

Take the complement of the seen signatures on each side against
the designated five-column pattern. On the A side, bin the missing
signatures by incidence to `(a,s)`; the exact numbers in these bins
that must pair with a B slot involving `b` are respectively
`1, j−τ, 5, τ` in the order `(0,0),(1,0),(0,1),(1,1)`. The other
slots in the first two bins are all already present in `T'`. The
baseline screen tests these exact margins; it ignores cross-pair
coverage on the missing slots.

The stronger `audit_reroot_cross.py` checks literal pairing of the
missing A/B support multisets with those quotas. There must not be
an exterior row touching both crossed anchors, by triangles. Every
other A×B pair requires a common exterior neighbour by MTF (no
root or other strip anchor can be the witness). For any unfilled
A slot or any uncovered cross pair, at least one compatible row
must be used. Branch exhaustively on the tightest of these lists;
decrement both occurrences and its quota and remove newly witnessed
pairs. A cap would be retained, never rejected. This still ignores
the free exterior–exterior edges and is only a necessary filter.

| window | branch | rooted positions before / after cross test (raw) | distinct original IDs before / after |
|---|---|---:|---:|
| 27 all | d8 leaf τ=0 | 895 / 443 | 48 / 22 |
| 27 all | d8 full τ=1 | 4 / 4 | 1 / 1, contained in leaf IDs |
| 26 δ=3 | d8 full τ=0 | 170 / 170 | 77 / 77 |
| 26 δ=3 | d9 leaf τ=0 or full τ=1 | 0 / 0 | 0 / 0 |
| 25 δ=2 | d9 full τ=0 | 82 / 82 | 16 / 16 |

At order 26 one rooted position may link to multiple distinct old
IDs, so there are 172 link rows for its 170 positions. The raw and
canonical lists give byte-identical projected IDs by tag at both
orders 25/26, before and after the cross witness check. The final
order-27 and order-26 d8 ID sets are disjoint, union 99 of 18,797.
Each of the remaining **18,698** original d8 IDs can only lift via
a full τ=0 pivot, order 26 with δ=4. Each of the **1,782** d9 IDs
outside the order-25 δ=2 set must have a rerooted window of order
25 with δ=3 or order 26 with δ=4, and **every** A-small d9 order-26
reroot (even on those 16 IDs) must have δ=4. Here the lower bounds
come from `R(3,7)=23` and the upper bounds from `d_T'(a)=|T'|−22`.
These are alternative-scope statements, **not** elimination of
18,698 d8 or 1,782 d9 IDs from the entire A-small case. The other
99/16 IDs may still have unseen higher-minimum configurations.
No selected completion was solved.

## Controls and replay

- C13(1,5) and C13 give α=4 and α=6, respectively. All 234 independent
  triples preserve the residual on exchange. An actual relabelled
  C13 uses `(a,s,b)=(0,2,6)` before permutation, old marks `{4,9}`
  and `{8,11}`, common core `{4,8,9,10,11}`, directed cross 9→8.
  Adding 4–12 keeps both cores, both marked orientations, equality
  degree one and α=6 but moves δ(T') from zero to one. A scan for an
  equality anchor cannot impose that it be minimum.
- The cross matcher agrees with exhaustive literal slot permutations
  on 1,400 smaller width-three controls, 607 positive and 793
  negative. No target cross run hits the 20,000-state cap.
- Independent optimistic wing-only screen `audit_reroot_wing.py`:
  156 actual C13 positive projections and a planted I8 negative with
  a one-edge escape pass. All 768 dispersed target role/branch tests
  survive, one sample of 192 roles per B degree. This screen only
  checks maximal possible core contacts with the one newly retained
  independent wing; do not scale it or confuse it with G's joint test.
- All compute was foreground, single core. Final five maps 33.24
  CPU-s, five cross reruns 5.88 CPU-s; the wing pilot 2.83 CPU-s.
  No proof check or SAT production. Source generation was earlier.

From `scratch/A/strip12` (`ulimit -v 16777216`):

```sh
root=../../..; py=$root/opt/venv/bin/python; src=$root/ralph/lanes/A
old=../strip11/short.crossfirst.full.keys
for run in 27:0:A 26:3:A 26:3:canon 25:2:rooted 25:2:canon; do
  IFS=: read -r n delta tag <<< "$run"
  marks="../../G/round7/lowdegree$n.$tag.keys"
  opts=(--order "$n" --minimum "$delta")
  if [[ $n == 27 ]]; then marks=../path7/pair27.A.keys; opts=(--order 27); fi
  nice -n 5 timeout 90s "$py" -uB "$src/audit_a_side_reroot.py" "$old" "$marks" "map$n.$tag.tsv" "${opts[@]}"
  nice -n 5 timeout 15s "$py" -uB "$src/audit_reroot_cross.py" "map$n.$tag.tsv" "$marks" "cross$n.$tag.tsv"
  awk -F '\t' '$1!="False"{print $3 "\t" $4}' "cross$n.$tag.tsv" | LC_ALL=C sort -u > "cross$n.$tag.idtags"
done
nice -n 5 timeout 45s "$py" -uB "$src/audit_reroot_wing.py" "$old" wing.pilot.tsv
```

Exact bound-scope and complement IDs are in `scratch/A/strip12/`;
`round12.sha256` pins inputs, outputs and the three scripts.
