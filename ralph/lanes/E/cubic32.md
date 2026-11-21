# Order-two, 32 fixed points: cubic W branch

**Claim (cert, pending critic review):** exclude `(2,32)` with all four
attachments of size six (`t=4`), `δ(W)≥2`, and `e(W)=12`. This includes
the original cubic-only stratum `δ(W)≥3` by the capacity argument below.
The crown reduction uses the separately checked universal minimum degree
five (`involution.md`). No MTF assumption is made. This does **not** cover
`t=2,3`, `t=4, δ(W)≤1`, or cores with `e(W)≤11`.

## Hand reduction

Use the capacity bound in `crown32_pressure.md`. There are eight
vertices in `W`. Every `w` has an edge to each attachment: otherwise
`w` and that full attachment form an independent seven-set, which can
add three vertices on one side of the crown. In each attachment, the
vertices with exactly one edge there must use distinct columns (a
duplicate either makes a triangle or gives an independent seven-set).
There are six columns, so each attachment needs at least two double
rows. For `δ(W)≥3`, a vertex of W can supply at most one extra edge,
and can do so only at W-degree three. Hence W is cubic, every row is
double in exactly one attachment, and every attachment has six
singletons and two doubles. Each singleton uses one of the six columns
bijectively, and each double uses a pair of slots. They must be slots of
nonneighbors of the double row (triangle-freeness), and those two
singleton vertices must be adjacent (otherwise their triple with the
double row, plus the four unused columns, gives an independent seven-set).
Compare all independent `U ⊆ W` to their column union: for every such
`U`, `|N(U) ∩ A_i| ≥ |U|` is equivalent to `α(W∪A_i)≤6`.

Let `H_i=G[F\A_i]`. It has 26 vertices and independence number at most
seven because it can add the two vertices of the omitted moved pair.
Every `w∈W` has fixed degree `3+4+1=8`. Every attachment vertex has at
most seven fixed neighbors, since it has two moved neighbors. The exact
identity from `involution.md` now gives

```
Σ_i e(H_i) = Σ_{v∈∪A_i} d_F(v) + 2 Σ_{w∈W} d_F(w)
           ≤ 24·7 + 2·8·8 = 296.
```

Thus **some** `H_i` has at most 74 edges. It remains only to forbid such
a window. Its pinned edges are 12 inside W and 10 in each of three
incidences W–A, leaving at most 32 unknown edges. The fourth attachment
is not needed in the CNF; its double pair is the two unused rows and
must admit some valid support. Any pair of groups in a window adjoined
to W has `α≤7` since two moved vertices from the two absent groups on
one side of the crown can be added. These rows are redundant in the
full-alpha window CNF; the matched relaxation keeps them in place.

## Calibration and cost estimate before full launch

`cubic32.py calibrate` compares support generation to an explicit
triangle/independent-set oracle on all subgraphs of the 4- and 5-vertex
paths, with one or two doubles. An exhaustive small three-group control
compares all labelled graph completions to SAT on seven bounds;
the exact counts are `0,2,14,39,55,57,143`.

The ten-window stratified pilot gives ten UNSAT, with CPU around
1.1 s per CNF and solve under 0.2 CPU s per sampled row. Four matched
native-LRAT runs all pass `cake_lpr` (proofs 2 KB to 673 KB); the weaker
pair-only relaxation is SAT for three of the four, with one checked
UNSAT. No pilot hits a cap. Before full launch the projection is about
0.5 CPU-hours including the first replay, approximately 3–8 minutes
on eight cores depending on load, up to 5 GB for files; keep the per-job
caps and inspect limits separately. No unpinned sweep is justified.

## Widening the saturated branch

For `δ(W)≥2` the residual degree bound gives `d_F(w)≤8`, and every
vertex meets every group. In particular `d_W(w)≤4`. If `e(W)=12`, the
number of W–A edges is at most `8·8−2·12=40`. It is also at least 40
by the double-row argument above. So every group still has exactly
two rows with two neighbors and six rows with one; each `w` occurs
in exactly `4−d_W(w)` double pairs, allowing a pair to repeat across
groups. The low-window bound is unchanged. This covers the cubic
cores and 12 further triangle-free cores. The independent labelled
census normalizes the neighbors of one degree-two vertex to `{1,2}`
and compares the entire remaining edge search with explicit orbits.
Two noncubic cores have no viable four-group degree profile; other
cores leave 6,904 window representatives in total.

A faster relaxation retains only the projected independent-eight-set
clauses with at most eight edge literals, plus the degree, triangle and
edge budget clauses. It drops the redundant pair-window rows. Any
refutation is sound for the full window. The smaller controls compare
bounded cuts to filtered unrestricted cuts as well as comparing all
labelled completions of the unrestricted CNF. Thirteen stratified
noncubic pins all have checked LRAT proofs with 13.8–16.3k clauses and
about 0.3 CPU s per CNF. Project 0.6–1.0 CPU-hours for 6,904 pins with
proof checks, about 5–12 minutes on 12 cores with load variation, and
at most 4 GB for normal output. Launch only this exact stratum.

## Full decision and replay

| Directory under `scratch/E` | CNF variant | Window representatives | Checked UNSAT | SAT / limits | Measured encode + solve + check core-hours |
|---|---|---:|---:|---:|---:|
| `r5_cubic` | all projected independent-eight-set clauses | 1,058 | 1,058 | 0 / 0 | 0.5366 |
| `r5_saturated` | at most eight literals in independent-set clauses | 6,904 | 6,904 | 0 / 0 | 0.6778 |

For the cubic branch the independent enumeration normalizes one vertex's
neighbor set and finds all 96 labeled cubic cores with those neighbors:
24 from the cube's orbit and 72 from the other orbit. The windows are
canonical under all W automorphisms, a permutation of the three retained
groups, and a permutation of slots within each group. There are 348
representatives for the cube and 710 for the second core. The noncubic
core check compares all 1,210 labeled cores normalized at a degree-two
vertex to the disjoint permutation orbits of the twelve supplied graphs.
For each core `degree_profiles` lists the sorted multisets of four
double pairs with the required row multiplicities; any three groups that
remain after an omission are then represented in the support census.

Each directory's `freeze.log` contains aggregate timings and the SHA-256
of `certificates.sha256`; the latter binds every numbered CNF, native LRAT
and successful `cake_lpr` log to the window manifest. There are 572 empty
native traces in the short bundle, each with an explicit empty clause in
its CNF and an affirmative `cake_lpr` verdict. The seven interrupted
cubic shell invocations were rerun to checked UNSAT; no solver caps,
unchecked final UNSATs, or positive windows remain in either cover.
Separate regeneration and replay matches the recorded CNFs and checks
all 1,058 cubic proofs and 56 stratified noncubic proofs.

Run `sha256sum -c certificates.sha256` for file integrity. From
`scratch/E/r5_cubic`, `bash ../../../ralph/lanes/E/replay_cubic32.sh full`
rebuilds the projection and checks LRAT again. From `scratch/E/r5_saturated`,
use the corresponding `short` mode. Optional `OFFSET STRIDE` shards
replay disjoint row sets and use separate scratch directories.
