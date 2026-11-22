# Round 23: transport and physical blocker fixtures

## h=6 transport v1 (hand + enum, regression only)

`scratch/A/r23/transport.v1.json` fixes the format for the already accepted
weak inventory A-035. Each `h6.labels.tsv` row sends a **raw label to its
representative**. `left_perm[i]` and `right_perm[j]` are destinations of
source coordinates `i` and `j`; both fix 0. Place `M[i,j]` at
`[left_perm[i], right_perm[j]]`, then transpose the result if `swap=1`.
For hole masks, map bits by the corresponding shore permutation, sort each
pair and then exchange the shores if requested. The inverse inverses both
permutations and exchanges their order precisely when `swap=1`.

All 22,408 labels pass forward and inverse checks, against the 49 recorded
masses and 19,651 hole keys. Using the stored forward action backwards fails
on 19,908 labels. The fixture includes a nontrivial nonswap 3-cycle and a
non-involution with the post-permutation transpose, each with an explicit
board and hole round trip. This versions existing input bytes, not h6 proof
regeneration or new coverage.

## h=5 compact clause (hand + enum, controls only)

A witness names 10 **distinct physical sites**. A boundary vertex is an
integer; each exterior site in the fixture is a pair of zero-based folded
coordinates. Coordinates below the grid size name physical grid sites in
row-major order, including separate positions for repeated cells. Otherwise
subtract the grid size to get the slot index. Grid sites have a shared left
and right coordinate; a non-grid site must name its **actual selected pair**
and have a negative selector literal. Different selected sites cannot reuse
either shore slot, but can have equal contact masks.

For every pair of sites, reject the proposed witness if a root/anchor edge
or contact is fixed true. If the pair is fixed false by the boundary or a
shared anchor, it contributes no edge literal. Otherwise use the physical
left edge variable, with the right variable channelled under the selectors.
The resulting row is the disjunction of all negative selectors and all live
edges. If any selector is false the row is true; otherwise all named sites
exist simultaneously and falsifying the row supplies an independent ten-set.
In particular a left bit made false by a **right** shared anchor is omitted
only under the actual selected-pair guards. The fixture identifies the
existing baseline CNF channel clause proving this for each omitted left bit.
`full` retains crossed-out left bits; `compact` does not. Neither treats
contact masks as site identities. Guards cannot be inferred from slot
activity alone.

`scratch/A/r23/physical.v2.json` comes from an independent decoder which does
not import G's encoder or inspector. The full assignments satisfy all 87,000
baseline CNF rows (44,106 + 42,894), decode to the stored graph6s and agree
between the left and right channels. All four I10 witnesses have explicit
45-pair tables and falsify genuinely new rows of the respective baseline.
Neither model has an I10 using zero or one non-grid site.

| Board | Non-grid sites in witness | Full → compact | Repetition in witness |
|---|---:|---:|---|
| 201 | 2 | 14 → 9 | — |
| 201 | 4 | 13 → 7 | physical positions 29 and 31, same right mask 2 |
| 202 | 2 | 11 → 7 | — |
| 202 | 2 | 17 → 11 | physical positions 38 and 39, same left mask 2 |

All 1,960 supplied width-three order-17 placements decode back to their
physical graph6 and independently check triangle-free with alpha exactly 6.
Three mutations lose valid plants in this smaller alpha≤6 control:

- A **short** six-set (two selectors) has no physical seventh site that can
  extend it. Its short row `[-25,-18]` wrongly rejects the positive.
- Dropping optional/optional edge literal `45`, the sole true literal of a
  guarded seven-site row, wrongly rejects a graph whose two named sites are
  both present and adjacent.
- Dropping only `-17` from compact row `[-26,-22,-17,37]` wrongly rejects a
  positive where that left slot is paired with a different right slot. An
  independently checked second positive with all three requested selectors
  true satisfies the row by literal `37`.

No UNSAT, proof-chain, board, degree distribution, candidate, or budget
debit. Attach these fixtures to G's independent rebind, not its solver
frontier. Exact source snapshots are retained under `scratch/A/r23/h5-source`.

## Replay

From the workspace root: `bash ralph/lanes/A/replay_blockers23.sh r23-review`.
This verifies 20 pins, runs two bounded foreground Python workers serially,
and compares both versioned JSON results byte for byte. Clean replay took
3.36 CPU-s, peak 81,060 KiB. See `scratch/A/r23/replay.log`.
