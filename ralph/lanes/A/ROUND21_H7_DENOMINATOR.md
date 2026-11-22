# Round 21 — independent fixed-alignment denominator for G

**Hand + enum, pending critic.** The eight frozen `h=7` left-only
pilots have a union of **184 two-sided keys beyond the 51-key checked
baseline**. Counting labelled alignments once per canonical key gives
**5,592,650**, with individual counts ranging from 1,445 to 131,751.
This is the comparison queue if all eight pilots pass, not a proof
of coverage. No graph, context, distribution, or U88 key is excluded
by these counts.

## What is counted

For each fixed board and each pair of specified double-support lists,
form the nine distinguishable slots on each shore: the eight distinct
doubles and the one singleton at the coordinate with private-grid
margin three. Exactly seven sites are double on both shores: the two
singleton slots cannot be paired together, so their mates are distinct
doubles, leaving seven double/double sites.
An alignment is a bijection of these slots; no pair of slots may
contain both crossed anchors. Each empty noncross grid cell must be in
the Cartesian support of a matched site. The grid is fixed, including
the multiplicity of any occupied cell. Private/private site labels and
their internal edges do not form any additional choices in this count.
Likewise no exterior graph edges, degree budgets or independent sets
are tested. Legality here means the slot, triangle and witness tests
above, not realizability as a marked Ramsey graph.

**Counting identity.** Make an incidence matrix of admissible slot
pairs. For a subset of missing noncross cells, zero every matrix entry
that could witness any cell in that subset. The permanent of the
remaining matrix counts all bijections omitting the subset. The
alternating sum over subsets counts each bijection with `m` uncovered
cells exactly `(1-1)^m` times, hence retains precisely those covering all
required cells. The implementation merges equal zeroed-entry patterns
and computes each permanent by adding rows to a DP indexed only by used
columns. A separate literal loop visits every slot permutation and tests
the physical Cartesian footprints; it does not use the permanent or its
inclusion-exclusion terms. Both agree on **184/184** target counts.

**Context binding.** Enumerate the row/column relabellings fixing the
two crossed coordinates. Keep a relabelling, with or without shore
exchange, only if it preserves the entire matrix of cell multiplicities.
This also transports the deficient singleton to the deficient coordinate
on the destination shore. It gives a bijection on fixed alignment sets,
so we use the minimum two-sided context key and count **each labelled
alignment on that representative**, without dividing or multiplying by
the stabilizer. Independently reconstruct the exact baseline from the
six fixed/fixed scopes and the two broad scopes (not a proof replay).
For each frozen left context enumerate the 30 physical right hole lists
only. The exact keys in all eight lists and the baseline matched the
frozen JSON; transpose is not used on boards 2 and 3. No scan of the
81 fixed-left contexts or other target inputs.

## Data for G

`scratch/A/r21/alignments.tsv` is keyed by
`(board,left_pairs,right_pairs)` using the integers and ascending
support masks from `scratch/G/round19/h7-prereg.json`. Singleton columns
are also masks. Each row gives the count and all pilot IDs to which
it belongs, already excluding the 51 baseline keys. For an arbitrary
checked subset, sum column `fixed_labelled_alignments` **once** for each
row whose membership intersects it. `scratch/A/r21/prefix.tsv` contains
the increments and cumulative totals for consecutive successful pilots.
The sole fresh overlap is the board-5 key in pilots 6 and 8, of
weight **70,252**.

| Successful prefix through pilot | Fresh keys | Labelled alignments |
|---:|---:|---:|
| 1 | 15 | 118,702 |
| 2 | 45 | 284,957 |
| 3 | 63 | 1,030,097 |
| 4 | 92 | 1,562,755 |
| 5 | 122 | 2,848,285 |
| 6 | 139 | 4,386,107 |
| 7 | 168 | 4,881,204 |
| 8 | 184 | 5,592,650 |

The queue does not itself establish a runtime speedup. In particular,
the `h=8` per-ID timings are not measured `h=7` fixed-alignment costs,
and the six `h=7` fixed-**context** receipts cover many alignments per
formula. Neither is a matched direct runtime by itself; do not convert
this denominator into a claimed measured speedup, or into a comparison
with a fully symmetry-reduced fixed-alignment solver.

## Controls and resources

- The two counters agreed on 18 aligned and 90 one-defect small slot
  contexts with both zero and positive counts. For the six stored
  fixed/fixed `h=7` controls they independently returned
  2,128 / 1,977 / 8,547 / 8,924 / 26,119 / 31,976, matching `mass.log`.
  The extra aligned `h=8` count 2,399 also matched.
- Omit witness `(4,4)` on board 0: 2,128 -> 9,072. Omitting both
  compulsory singleton slots while maintaining the other tests admits
  2,443 partial matchings, none of which is a full alignment. Allowing
  crossed-anchor triangles (board 0) or pairing the singleton slots
  (board 2) also changes the corresponding controls.
- The 12-key sample was priced before full counting (`ROUND21_PRICE.md`).
  Full counting and literal cross-check: 33.31 CPU-s. Clean replay from
  the frozen inputs reproduced both tables byte for byte. Total timed
  cost including failed setup/calibration and mutation development:
  **47.10 CPU-s (0.01308 core-h)**, peak RSS 26,836 KiB, <1 MiB staged.
  One foreground worker at a time, 512 MiB virtual cap; no running jobs.

Replay from root: `bash ralph/lanes/A/replay_h7_alignments21.sh r21-review`.
Add `full` as the second argument to repeat the literal checks on all
184 target keys (use a new directory name).
