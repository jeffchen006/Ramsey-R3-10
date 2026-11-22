# Round 19 — shared-grid middle gate and deferred one-defect pilots

Authorize exactly the critic's one shape: `h=8`, fixed left middle, any
right. Preflight generated and bound 724 variables and 23,733 clauses.
Controls reproduced aligned 24/0 and changed-board 129/11 canonical
classes, and 208 actual positive projections used a right double list
different from the left. A forged edge unit, unguarded optional-edge
row, false slot mutex and shortened MTF row were rejected. The accepted
leaf LRAT passed both checkers again. Physical preregistration found
57,947 eligible IDs in six of the 12 open schemes, out of 79,072; these
are only potential before the solve and dual checks.

One foreground nice +5 worker; 512 MiB virtual memory, 30 solver CPU-s,
45 wall-s, 96 MiB proof file, 128 MiB total new scratch, 360 CPU-s
all-in. Stop this shape on SAT, cap or any binding/checker failure;
on anything but fully checked UNSAT, retain 79,072. No matching-shape
solve, fixed-ID proofs or `h=7` solves this round.

**Before target**: scout leaf took 0.79 solver CPU-s and 2.79 CPU-s
end-to-end, including replay, and wrote 5.51 MB CNF+LRAT. The middle
CNF is 6.5% larger by bytes; that is an input size comparison, not a
runtime bound. Baseline for this round took 13.10 CPU-s, 134,516 KiB
maximum RSS and ~11 MiB apparent scratch. Budget ~30 CPU-s total and
~30 MiB disk for a similar proof plus one clean review; within the
caps, even counting 30 CPU-s for the solve rather than the leaf timing.
Budget only one extra ~11 MiB review workspace (since removed after
comparison); together with the capped proof file the accounting stays
within 128 MiB. Neither proof size nor runtime is forecast reliably
from the different shape.

## `h=7` preregistration — no solving authorized

Baseline: 51 checked **two-sided orbits** out of 1,213; 1,162 open.
81 is the size of a sufficient fixed-left test lattice after choosing
the orientation of each board, not the denominator for 51. Disperse by
board then by fixed-left order: take lexicographic quantiles among the
representatives that add any right-context orbit not previously checked
or scheduled earlier in this list. Freeze the resulting list before any
of these eight formulas are solved. Masks label the two *missing* left
pairs (bit 0 is the crossed anchor); singleton is the deficient left
coordinate's mask. Boards 2 and 3 are transpose-asymmetric.

| Pilot | Board | Left holes | Singleton | Preserving/flipping stabilizers | Right orbits | Fresh from baseline | Increment if earlier all pass |
|---:|---:|---|---:|---:|---:|---:|---:|
| 1 | 0 | 17,18 | 1 | 6/6 | 18 | 15 | 15 |
| 2 | 1 | 5,20 | 1 | 2/2 | 30 | 30 | 30 |
| 3 | 2 | 3,17 | 1 | 6/0 | 18 | 18 | 18 |
| 4 | 3 | 17,24 | 1 | 4/0 | 30 | 29 | 29 |
| 5 | 4 | 5,20 | 2 | 2/2 | 30 | 30 | 30 |
| 6 | 5 | 3,9 | 2 | 4/4 | 18 | 17 | 17 |
| 7 | 2 | 17,24 | 1 | 6/0 | 30 | 29 | 29 |
| 8 | 5 | 9,10 | 2 | 4/4 | 18 | 17 | 16 |

For each checked broad receipt, subtract the baseline and all earlier
**checked** receipts from the set of keys
`(board, canon_stab(left_pairs,right_pairs))` over the 30 legal right
hole lists. The stabilizer fixes the crossing, preserves board
multiplicities, and only transposes when the transformed board is that
same representative. Use the JSON's explicit keys; do not credit
counts per left context or the raw 30 right lists. All eight would add
**184 distinct** context orbits, but none is tested. Future priced
pilot (separate authorization): record generation, solve, semantic
binding, checker times and proof bytes for each. For a per-alignment
comparison count the compatible matchings once per freshly covered
two-sided orbit, requiring compulsory slots, admissible crossed masks
and every missing noncross cell. Stop before bulk on any model, cap,
failed audit, or less than 10-fold forecast saving against that exact
fixed-alignment queue. No extrapolation to `h≤6`.
