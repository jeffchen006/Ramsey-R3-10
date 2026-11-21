# Round 7: two bounded e108 sources and prefix handoff

Run commands from `scratch/B` with `LC_ALL=C`, `PYTHONDONTWRITEBYTECODE=1`,
`ulimit -v 16777216`, `nice -n 5`, and a `timeout`. No old lateral,
rewire, e43 or reducible-e88 batch was rerun.

## Adjacent-pair reconstruction (enum, sampled families only)

Given a triangle-free base B with alpha ≤ a, add adjacent vertices p and q
with attachment rows L and R. Triangle-freeness requires L and R to be
independent and disjoint. The extension has alpha ≤ a exactly when each
row hits every independent a-set of B. Edge-criticality at p-x, x in L,
requires an independent a-set meeting L only at x: q cannot belong to
the deletion witness because p-q remains. The same holds for R. Thus
enumerate inclusion-minimal independent transversals; an already chosen
vertex with no private witness cannot regain one as its row grows.
The edge p-q is critical exactly when B minus L union R has an independent
(a-1)-set. For a base edge x-y without a base-only deletion witness,
an independent (a+1)-set after deletion must use exactly one added
vertex. That row must avoid x and y, and the exterior of their two
neighborhoods minus the row must have an independent (a-2)-set. A
bitset cover tests all such base edges jointly. These conditions, the
edge budget and the degree tests give an exact enumeration **for the
supplied stems and an adjacent pair**, not for all order-32 graphs.

`src/adjacent_stems.c` extracts the induced base after deletion of both
ends of an old edge; `src/adjacent_critical.cc` reconstructs. The Python
oracle tests all disjoint assignments on six-vertex stems and all
forbidden-size subsets directly: 374 exact labelled cases, seven outputs.
The independent stem extractor matches all 315 labelled stems from 15
order-16/e21 graphs. Their canonical stems reconstruct 18 of the 42
critical e22 classes; stems from all 201 e22 classes reconstruct exactly
all 42. This is a positive control, not a completeness claim for stems
from the next lower edge level.

`logs/e108_r7_adjacent_sample.log`: 25 spaced critical e108 parents gave
2,700 distinct stems and 32 known critical e108 classes; 24 spaced e107
parents gave 2,549 distinct stems and zero outputs. No novel class in
either family. Extract, canon and generation cost about 0.9 CPU-s in
total, excluding the small controls. No expanded scan was launched.
`logs/e108_r7_final_retest.log` confirms byte-identical canonical output
after normalizing equal-size row orientation in the final build.

## Degree-six star on e65 seeds (enum / estimate)

At a rooted star with exterior B, p-x is critical iff some independent
(a-1)-set of B misses the attachment row of x; a witness containing p
cannot use any other neighbor of p. `CRITICAL_ROOT_EDGES` in `gluetrans.c`
filters rows by this exact necessary condition before forming the pair
matrix. `cal_critical_star.py` independently checks each root-edge witness.
The new filter matches the independently filtered **labelled** output
from the baseline for order-16/e22 roots of degrees 2 through 6 and,
after checking all edges, recovers all 42 critical control classes.
`logs/e108_r7_d6_control.log` records the control.

From Lane E's HoG file, independently checked all 396 distinct valid
order-25/e65 inputs (GR T13). The pilot has 23 dispersed seeds plus two
planted seeds, 25 distinct in all. It gives 45,192 labelled e108 outputs
and exactly the 21 planted critical classes; none are new. An independent
neighborhood-deletion map and nauty `labelg` bind all planted keys to
the actual seeds. The root-edge screen keeps **268,617/268,617** rows,
so it is not a useful speedup on this slice: 16.71 versus 16.40 solver
CPU-s, 0.46 CPU-s for leaf criticality alone. The paired critical output
multisets agree; no scale-up. See `logs/e108_r7_d6_{pilot,binding}.log`.
The bounded pilots do not change 2,102,885 known e108 classes, the 1,266
missing critical classes, or the scope of the 614 prior certificates.

## Prefix handoff (open)

The prefix supervisor PID 1180084 was left untouched. Its final canonical
output was not yet available this round. `src/replay_prefix_r7.sh lower`
will independently extract e86/e87, check both GR counts and require exact
equality to the checkpoint (`e86.g6`, `union87.g6`). `terminal` additionally
requires a successful terminal MTF-zero log and binds each ordered chunk
to freshly extracted e88 inputs. It subtracts the independently audited
disjoint union of reducible keys and rechecks the critical prefix keys.
`control` matches exactly the known 159/42 reducible/critical split of
201 order-16/e22 keys. The terminal invocation does not rerun the e43 or
reducible scans. Follow with a dispersed independent SAT sample from
`work/prefix_r7_replay/prefix.critical.g6` if nonempty (no proof implied).

If the prefix terminates with zero, the uncovered e88 inputs are exactly
the critical e88 residues with no d5 root of residual ≤58, no d6 root of
residual ≤51 and no d7 root of residual ≤43. There are no additional
outside-prefix d7/e43 keys. The full increment argument then requires a
d6/e52 or a d7/e44 root. Neither the size nor emptiness of this complement
is known, and the ten U88 distributions remain open regardless of prefix
completion absent a further result on that complement.
