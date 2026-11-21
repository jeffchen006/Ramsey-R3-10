# Degree-six roots have no exterior degree below six

## Complete finite cover (pub + enum)

Write `(3,k;n)` for a triangle-free graph of order `n` with independence
number at most `k-1`. If `H` is `(3,9;33)`, it has maximum degree eight.
Deleting a vertex of degree at most four and its neighbours would leave
at least 28 vertices with independence number at most seven, contrary
to `R(3,8)=28`. Thus to exclude minimum degree below six only degree
five needs to be covered. For a degree-five vertex `x`, its residue
`Q=H-N_H[x]` is a `(3,8;27)` graph. The published 477,142 catalogue count
(Brinkmann–Goedgebeur–Schlage-Puchta; also Angeltveit §3.2) binds the
valid, canonically distinct source from `scratch/A/rc7/r38_27.g6.gz`.

For a fixed core `Q`, glue a root of degree `d` whose independent
neighbours have attachment sets `S_i` in `Q`. A triangle is impossible
exactly when every `S_i` is independent in `Q`. The following tests
are necessary and sufficient for `alpha<=a`, given `alpha(Q)<=a-1`:

    for every T ⊆ [d] with |T|>=2,
    there is no independent (a+1-|T|)-set of Q outside the union of S_i for i in T.

Indeed, an independent set containing the root uses none of its neighbours;
one not containing the root can use any subset `T`. The cases `|T|<=1`
hold already. The tests are monotone under extending the `S_i` within
the independent sets, so every solution extends to a tuple of maximal
independent sets (MIS). Repeated columns are allowed unless a test
rejects them. This is the standard monotone gluing principle of
Angeltveit §4.2, not a premise that the desired graph is MTF.

`maximal_prefilter.c` generates MIS by pivoting on the complement;
`check_maximal_prefilter.cc` grows independent sets in order and checks
domination. Both impose the pair test and the higher-subset tests by
sorted tuple search. The C implementation removes pairs of columns
avoiding the same independent `(a-1)`-set; the C++ replay builds each
column's avoid mask and tests pair intersections. They keep the same 118
of 477,142 core keys for `a=8,d=5`. On the 118, `glue6` enumerates all
actual column sets with minimum degree five; the independent C++
enumerator instead generates each feasible MIS tuple and deletes cross
edges in increasing index order. At each deletion, minimum degree
cannot increase and alpha cannot decrease, which justifies pruning.
All genuine columns are subcolumns of a feasible MIS tuple, so none are
missed by this deletion order. Their canonical output sets are identical:

| Edges | 123 | 124 | 125 | 126 | 127 | 128 | 129 | 130 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Classes | 5 | 44 | 149 | 266 | 294 | 184 | 41 | 1 |

The cap 130 is exhaustive: if one vertex has degree five and maximum
degree is eight, `2e(H)<=5+32*8=261`. The C and C++ implementations
then repeat MIS gluing with `a=9,d=6` on all 984 graphs. Both find no
compatible tuple, **without fixing total edges, imposing MTF, or using
a degree-distribution pin**. The exact finite cover is `enum`, not a
global LRAT proof. A narrower **cert** result is available independently:
on every one of the 118 necessary cores, both LRAT checkers verify the
non-MTF min-degree-five extension CNF at most 122 edges UNSAT. This and
the 984-class cover do not use the six missing general e120/e121 types.

## Consequences (hand, conditional on the finite cover)

In any order-40 `(3,10;40)` graph `G`, the antineighbourhood of a
degree-six vertex `u` is `(3,9;33)`, so by the finite cover it has
minimum degree at least six. For any nonadjacent distinct `u,w`, with
`u` of degree six, `d_H(w)=d_G(w)-c_G(u,w)` exactly. Hence
`c_G(u,w) <= d_G(w)-6`. If `G` is maximal, every nonadjacent pair has
at least one common neighbour. Thus all degree-six vertices in `G`
are mutually adjacent, and triangle-freeness gives `n6<=2`. This
last step does require MTF. It implies the typed pair rows
`p_(6,t,c)=0` for `c>t-6` and requires every degree-six root profile
to contain all other degree-six vertices as neighbours. These rows
use no degree-eight or degree-nine gluing lower bounds.

The same profile implication works if the residue degree bound is
known only for particular profiles: roots whose residues are within
scope are universal in the class of degree six. If `n6>=3`, at most
one such root exists (two would form a triangle with a third); if one
exists, the induced graph is a star, since all other degree-six
vertices are its neighbours. Outside the scope we only count the
number of possible endpoints of each degree type as an upper bound.
These conditional rows are in `scan_d5_cuts.py`. Its global scan uses
cap 132 as a sentinel since any `(3,9;33)` has at most 132 edges.

The 84 direct contradictions use row `n6<=2` plus `-n6<=-q` for the
pinned case `q>=3`, with unit rational multipliers. The additional
e168 case `(2,9,0,29)` has a short hand proof: the two degree-six
vertices must be adjacent. At either, the established floor 120 and
the MTF private bound force `Z=48`; but the sum of the degrees of its
neighbours is six plus five odd numbers, hence odd, a contradiction.
This only needs floor 120. `d5_global_cuts.jsonl` records exact Farkas
certificates for the contradictions and five improved t9 bounds.

## Evidence and scope

- `root_certs/d5_order33.g6`: exact output, 984 canonical order-33 graphs.
- `root_certs/d5_order27_survivors.g6`: common 118-key inner survivor set.
- `scratch/G/round5/audit_d5_cover.log`: exact round-robin shard binding,
  canonical equivalences, dual LRAT hashes and all-level validity checks.
- `scratch/G/round5/d5.fullcontrol.binding.log`: exactly 178 of 191 known
  order-22 graphs have minimum degree five; gluing recovers that exact
  set and all 70 residue types from 944 roots. C++ independent trimming
  recovers the same 178. For outer degree six, 220 regular order-22
  controls (all roots of ten graphs) are retained by both filters.
- `scratch/G/round5/check_d5_rows.log`: C13, C35, saturated Exoo39, and
  all 191 order-22 graphs check the n-analogue at each actual residue
  minimum, including typed caps and universal roots.
- Neither the 11 e169-pinned proofs from round 4 nor the six unidentified
  e120/e121 keys are part of this cover. Remaining e168 degree-six
  profiles may still use missing degree-6/7 residue keys at e120.
