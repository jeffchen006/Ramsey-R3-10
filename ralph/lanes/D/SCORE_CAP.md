# Round 7: eager maximum-score cap

## Experiment plan

Use max12 forest key **24** (component sizes `2,2,4,8`, root
score two), signed count pin `k=7`. Compare the same shared eager
forest encoding with and without global `S<=2`, two foreground
slots, identical solver settings and signed count pins.
Keep anchor-forest, blocked-arc and lazy alpha/cycle handling on both
arms. The unfiltered control is a superset; it does not have the
optional score cut on nonroot edges. This is not a key32/q22 or key34
retry. Report terminal decisions, base variables and clauses, and the
wall/CPU cap separately from evidence about computational difficulty.

Round 6's comparable runs reached 48–55 CPU-s without a terminal
answer. The exact C16/C20 score-control run takes 28.22 CPU-s total
including 18 tight rooted solves. Allow at most 100 CPU-s and 170
wall seconds per target arm, 16 GiB, chunking in 2,500 conflicts for
censored progress counts. Do not extrapolate time to a full run from
two censored probes; do not use the third slot for an unvalidated cut.

## Score encoding (`hand`, calibrated `enum`)

For a diagonal pair `{a,b}` with common neighbor `v`, call `v` clean
for that pair if every other common neighbor `y` has `codeg(v,y)<3`.
These other common neighbors all share `a,b` with `v`, so they have
codegree two with it. In the kernel at `av`, `b` is the corresponding
vertex on the far side. It has degree `codeg(a,b)-1`. With codegree
three, cleanliness means both of its neighbors are leaves, exactly a
`P3` centered at `b`. With codegree two, cleanliness means its only
neighbor is a leaf, exactly an isolated edge. To count each isolated
edge only once, count only the contributions from the lower endpoint
of `av`; count `P3` from both endpoints. Codegree one contributes zero.
Thus these signed selection rows count the score exactly whenever
codegrees are at most three. No forest premise is needed for the
score encoding itself. The experiments use it only in the max12
forest case; the unrelated higher strata are untouched.

The driver reuses shared products for common neighbors; its score
layer has a separate exact truncated count for codegree three.
Each clean selector is equivalent to a common-neighbor product AND
the negation of all other common-neighbor/high-codegree products.
Eager at-most constraints apply before the first SAT search. Both
arms use the same lazy cycle and independent-set rejection code.

Calibration: forced every score threshold on every edge of 13 C16
labelled controls (two forest, eleven nonforest) and the nonforest
C20 circulant, with 2,960 contradictory selector queries rejected.
Then reproduced the exact labelled output sets on all three tight
C16 catalogue keys at caps none/0/1/2/3/4 (18 exhaustive solves).
One Clebsch completion survives none/4 only. See
`scratch/D/score_r7/cal.log` and `cal16/`.

## Matched target outcomes (`open`)

| Key 24, k=7 | Initial clauses | Last logged conflicts | Intermediate SAT models | Terminal decisions | CPU-s |
|---|---:|---:|---:|---:|---:|
| Control | 1,108,371 | 72,530 | 0 | 0 | 99.95 |
| Global score cap | 3,568,570 | 10,001 | 0 | 0 | 99.93 |

Both hit the CPU limit (signal 9, wrapper status 137), not an UNSAT
result. Max RSS 361 MiB vs. 1,028 MiB. This run is a negative cost
measurement on one pin; conflicts are progress counters, not a
heuristic estimate of the number remaining. Logs frozen at
`scratch/D/score_r7/key24-{base,eager}.{log,time}`. Do not scale the
global build merely because it has an exact interpretation.

## Exact secondary split of the score-two stratum (`hand`)

Write `M_i` for the number of edges of score `i`. In max12 with
`max S=2`, the existing double count gives
`M_2=60+M_0+2*w`. Let `J` be the graph consisting of all 40 vertices
and its `M_2` score-two edges, and write `d_2(v)=deg_J(v)`. Then

```
sum_{uv in E(J)} (d_2(u)+d_2(v)) = sum_v d_2(v)^2 >= M_2^2/10.
```

Consequently either there is an edge of `J` with `d_2(u)+d_2(v)>=7`
(the **dense** subcase; choose such an edge as root), or every edge
has endpoint sum at most six. The latter forces `M_2<=60`, hence
`M_2=60`, `M_0=w=0`, and equality in Cauchy–Schwarz: `J` is cubic.
Conversely those equalities imply that the endpoint sum is six
everywhere (the **balanced** subcase; root at any score-two edge).
The two subcases are disjoint before rooting. The six old score-two
keys still cover each case; this is not a new deletion by itself.
Nothing changes for score three or for the 110 minimum-root keys.

Every edge kernel at an edge incident with either original root
is preserved by deleting the edges of the exterior `X`: one side
of each kernel is wholly in the fixed neighborhood of that root,
while the other side is independent. Thus all 17 scores of the two
stars are exactly computable from just the attachments. Impose
`S<=2` on those stars. On the dense arm at least five of the 16
nonroot star edges have score two (the root edge is counted twice).
On the balanced arm at each root exactly two of the eight nonroot
edges have score two and none has score zero. Also keep the local
consequence `w=0`: for every codegree-three pair incident with an
original root, its triple of common neighbors has both a high and
a low pair. Codegrees of those common-neighbor pairs are exact in
the projection since both vertices belong to the fixed root block.

The projected CNF keeps degrees of fixed vertices, 2/3 side sizes,
2/3 codegrees for fixed nonedges, no common neighbor for fixed
edges, at most three shared anchors for outside pairs, constant
square count at root-star edges, forest at root-to-anchor edges,
the unsigned `k` pin and the old independent-seed avoidance rows.
Unknown exterior edges cannot appear in these constraints. A SAT
projection is not a graph witness. An UNSAT projection would need
the deterministic CNF, a proof replay, and an audit of completeness.

Two-star calibration: 27,360 score-threshold checks after deleting
exterior edges at all 580 rooted C16/C20 control edges. The named
mixed-triple condition kept 200 and rejected 380 roots, matching
independent common-neighbor scans. The three projected tight C16
keys give the known one SAT/two UNSAT pattern; the Clebsch controls
accept and reject the appropriate stronger count pins in both modes.
Total 14.34 CPU-s. Evidence: `scratch/D/score_r7/star-cal.log`.

Projection cost estimate: the new two-star check took 14.34 CPU-s
on the whole smaller corpus, while the full target eager layer took
18.93 CPU-s merely to assemble. Test base/dense/balanced only on
key 24, k=7, at 45 CPU-s and 95 wall seconds, max three slots and
16 GiB per process. Stop if the projection has no terminal attrition;
do not widen to other pins on SAT projections alone.

| Key 24, k=7 (attachments only) | Clauses | Added clauses | CPU-s | Outcome |
|---|---:|---:|---:|---|
| Base | 423,461 | 0 | 7.64 | SAT projection |
| Dense | 453,857 | 30,396 | 4.73 | SAT projection |
| Balanced | 466,305 | 42,844 | 44.93 | Capped, no terminal result |

The base witness violates the star cap (one star edge has score
three). The dense witness has 7 and 8 score-two incidences at the
roots, and none with score above two. These are attachment records
only, saved under `scratch/D/score_r7/star24-*.g6`. No target pin
was excluded, so stop this pilot. The two-star constraints cost
about 1.2–1.7% as many extra clauses as the global score layer;
they are strictly weaker and this is not a solver speedup claim.

## Replay

From the workspace root, `source opt/env.sh` and export
`PYTHONPATH="$PWD/ralph/lanes/C:$PWD/ralph/lanes/D:$PWD/duo"` and
`PYTHONDONTWRITEBYTECODE=1`, then work in `scratch/D/score_r7`.
The control drivers are `check_score_sat.py ../max_root_sat16 cal16`
and `check_score_star.py ../max_root_sat16`. For the original global
pilot use its preserved driver `global_score_sat.py` with arguments
`24 key24-base.g6 --log key24-base.log --pin 7 --chunk 2500`, or the
same for `eager` plus `--cap 2`. For the projection use
`score_star.py 24 7 MODE star24-MODE.g6`. Apply the bounds above and
write to fresh outputs; evidence and code are hashed in
`scratch/D/round7_evidence.sha256`.
