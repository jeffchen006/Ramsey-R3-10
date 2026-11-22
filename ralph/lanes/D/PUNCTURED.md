# Round 8: punctured diagonal roots

## Preregistered bounded comparison

Use the eleven-profile scout cover (`review/ideas/astra_R.md`, idea 2).
Two dispersed target profiles 022 and 223 have different `z`, empty counts
and first singleton panel sizes. For each compare unfiltered SMS versus
one canonical panel in a selector disjunction plus the two tip windows.
Both are full graph formulas, not projections. Keep 4 slots maximum,
16 GiB per process, a 60 CPU-s solver limit (hard at 61) and 185 s wall
per arm. Smaller controls took <1 CPU-s per profile on most arms, but
other full target encodings hit 100 s; expect at most 244 solver CPU-s
for the pilot, **not** terminal coverage in a minute. No fan-out after
a double censor with no exhausted family. Measure outcomes, not conflicts.
Keep the established dense/balanced split frozen.

## Calibration and target results

The extractor starts with the two *tips*, not with the diagonal graph.
It tries both core directions and both full-vertex orders on each side
before applying the canonical signature convention. On the full 191 C22
classes it finds ten regular classes, three at cap three, containing
66, 35, 35 physical punctures. It uses coloured nauty certificates with
the six anchors individualized, not only an unrooted count. The 34 marked
classes across the eight feasible profiles match **exactly** on both SMS
runs, as do the three unrooted classes. Three of the eleven profiles
have a negative cell size on C22. See `scratch/D/punct8/cal-{base,panel}.log`.

The enhanced formula chooses a graph6 representative from `genbg` with
degree cap two on both sides of the first full–full singleton panel.
Two unused core vertices can augment an independent set in the panel, so
its matching number is at least its order minus `(degree-2)`. Reject a
panel C4, which would give K3,3 with the two full anchors. Row/column
permutations within these singleton cells are free *before* the first
panel. Individualize their vertices thereafter, retaining a safe subgroup
(identity on that panel), and never independently quotient later panels.
Both tip exterior neighborhoods have size `degree-2` and are independent;
their avoiders have independence number at most two and count at most
five. Encode both requirements. All other triangle/degree/codegree and
lazy independent-set conditions are identical to the control.

| Profile | Base clauses / CPU-s | Panel+tips clauses / CPU-s | Panel orbits after matching / after no-C4 | Terminal result |
|---|---:|---:|---:|---|
| 022 | 204,783 / 59.59 | 214,771 / 58.68 | 83 / 64 | both CPU-capped |
| 223 | 207,945 / 59.73 | 217,260 / 59.48 | 78 / 62 | both CPU-capped |

No full-model output or profile exhaustion. Per the stop rule no other
six-anchor target profiles were launched. `PATH_ROOT.md` is the new
eight-anchor structural argument, not an extrapolation from these timings.
