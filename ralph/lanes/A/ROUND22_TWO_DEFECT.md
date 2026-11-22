# Round 22: independent two-defect control and weak-board inventory

Lane G owns the target encoding and solver queue. Lane A's evidence here is
`hand + enum`, pending critic review. It excludes no target board, retires no
distribution, and makes no timing inference from `h=7` to `h=6`.

## Physical small-board oracle

The width-three controls have adjacent degree-four roots, one crossing,
boundary `0,1` (roots), `2,3,4` (left), `5,6,7` (right), and crossing `2--5`.
Each shore has two singleton sites per anchor and distinct double masks; all
exterior sites contact each shore. Count two singleton/double sites in each
direction, so there are four grid sites. There is no MTF condition and no
target Hall row in this toy. At order `n` there are `n−14` doubles per shore,
and `h=n−16` double/double sites. In particular, order 15 is not a two-defect
control.

1. Scan the physical catalogues without assuming a grid: find actual root
   pairs and their one crossing, then reconstruct site contacts. List both
   root orientations, noncross anchor orders, grid-copy orders, and the two
   independent orders of each repeated singleton pair. Historical one-defect
   checks recover the exact 129/11 canonical sets and 174/11 marked pairs at
   orders 15/16. All 2,576 order-16 and 7 order-17 `(3,6)` source graphs have
   zero two-defect marks.
2. Independently enumerate raw toy boards and admissible physical mask pairs,
   then both choices of every exterior edge not prohibited by shared support.
   Check triangles as edges enter and the actual independent-set threshold at
   the leaves. At threshold six, all 788/308 physical layouts at orders 16/17
   have no completion, matching the catalogue scan.
3. At threshold seven, exhaustive order-16 extension gives 127,086 labelled
   placements, 53,411 board/class incidences and 8,119 unmarked canonical
   graphs. Rescan those 8,119 physical graphs, which have 8,239 qualifying
   unordered root pairs, to recover the identical labelled keys. A separate
   `tools/check_graph.py` pass also accepts all 8,119 graphs. This is an exact
   census of the **marked toy**, not of all `(3,7;16)` classes.

`scratch/A/r22/positive/` contains the data. The board is a nine-character
row-major string. The four exterior grid copies are in row-major order, then
the other four stand in **left** slot order. `left` and `right` are compact
active slot masks: increasing doubles first (`3,5,6`), then singleton masks
by coordinate, repeating a mask for each distinct vertex. `mates[i]` is the
zero-based compact right slot for left slot `i`, not a mask or full-option
index. The exact `graph` graph6 is in those physical labels; `canonical` is
nauty's unmarked graph6. `n16.d2.summary.tsv` includes all 100 geometric
boards, 61 with a positive. `n16.d2.classes.tsv` contains only positive
board/class keys; absent keys mean the exact empty set. The strict files
are in `scratch/A/r22/`, not its `positive/` subdirectory.

| Named board | Left/right deficit | Labelled placements | Classes |
|---|---|---:|---:|
| `001001110` | separate / separate | 633 | 372 |
| `001001200` | separate / repeated | 1,044 | 273 |
| `002000200` | repeated / repeated | 6,896 | 270 |

`n16.mutations.json` has physical positives for the following tests:

- `alias`: identifying two same-mask slots disallows their distinct mates.
  Such an alias deletes 59,856 placements from the full labelled toy census.
- `alias_edge`: making their same-shore edge bits equal would impose equality
  on two distinct physical adjacency values, even when the common left mask
  does not prohibit either edge. The other shore can force one false.
- `short_witness`: an independent exterior triple with no independent
  four-set on the available boundary. Requiring an edge in this triple is
  not a valid padded clause. Its actual labelling is suitable for planting.
- `option_edge`: a real edge between two distinct non-grid sites. A relaxation
  may omit the variable only without interpreting the omitted edge as false;
  an exact projector must recover it.

## Target weak boards and hole decorations

For G-043's `e=170` adjacent degree-six equality pair, let `M[i,j]`
count exterior private/private sites at coordinates `i,j`. At `h=6`,
`|M|=18`, each row/column has sum at most four, and `M[0,0]=0` by the
one crossing. The physical private-cell matching of size at least
`3 + [i=0]` into the opposite four noncross anchors uses distinct
coordinates, at most `|{j>0 : M[i,j]>0}|` grid sites, and at most
`4−sum(M[i,*])` non-grid singleton sites in the row. This gives the
necessary weak row inequality

```
|{j>0 : M[i,j]>0}| + 4 - sum(M[i,*]) >= 3 + [i=0].
```

Apply the column analogue. It implies every entry is at most two, since
a noncross positive coordinate contributes only one matching position and
the row surplus over distinct noncross coordinates is at most one. Both
shore deficits sum to two (`R` = two slots at one coordinate; `S` = one at
each of two coordinates). There are eight double masks per shore; of ten
potential pairs exactly two are holes, and at least one hole meets the
crossed coordinate by its degree cap. The two singleton slots on one
shore cannot mate to singleton slots on the other (those sites are
already in `M`). This leaves six double/double and four mixed sites.

The row-by-row oracle independently reconstructs all boards, then builds
orbits under independent noncross `S4` actions and root exchange. It also
partitions the 900 hole-decorations **at each representative** under that
board's stabilizer, not under all crossing-preserving actions. At `h=8/7`,
this regenerates 1/6 board orbits and 30/1,213 hole-context orbits; the
`h=6` inventory agrees with the prior Burnside totals without importing
that code or doing a matching run.

| Deficit type (unordered) | Board orbits | Labelled boards | Hole-context orbits |
|---|---:|---:|---:|
| RR | 9 | 2,200 | 2,035 |
| RS | 16 | 8,232 | 7,293 |
| SS | 24 | 11,976 | 10,323 |
| Total | 49 | 22,408 | 19,651 |

There are 80 board orbits when root exchange is disallowed. Bare transpose
fixes 16 of the 49 chosen reps; 18 have a swap-containing stabilizer element
when arbitrary permitted shore relabels are composed with transpose. The
other 31 pair two distinct oriented board orbits. Even for the 18, a swap
may not fix a particular hole decoration, let alone a graph/alignment.

- `h6.boards.tsv`: least row-major representative, labelled multiplicity,
  oriented multiplicity, exact deficits and plain/swap stabilizer sizes.
- `h6.labels.tsv`: raw label **to** representative, with old-to-new left/right
  permutations fixing coordinate zero, then transpose if `swap=1`.
- `h6.holes.tsv`: minimal hole-pair key within each representative, with
  fixed-board multiplicity and global labelled multiplicity. The latter sums
  to 22,408 × 900 = 20,167,200 board/hole labelings. These are **not** counts
  of feasible slot matchings or solved scopes.

## Replay

From the workspace root, `sha256sum -c ralph/lanes/A/ROUND22_FREEZE.sha256`,
then `bash ralph/lanes/A/replay_two_defect22.sh r22-review full`. Uses a fresh
lane-owned directory, a single bounded foreground process at a time, and no
SAT. For a narrower positive comparison run `two_defect_oracle22.py positive`
with `--only` and the desired raw board labels; only the requested boards
are within scope of that invocation.
