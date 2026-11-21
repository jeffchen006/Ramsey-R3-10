# Independent replay of the accepted MTF degree floors

This audits Lane G's accepted exclusions, not a new search or case closure.

## Published coverage premise

Goedgebeur and Radziszowski, *New Computational Upper Bounds for Ramsey
Numbers R(3,k)*, EJC 20(1), #P30 (2013), arXiv:1210.5826v4, Tables 4 and
14: the minimum for `(3,9;33)` is 118, with exact counts 5 at 118 and 69
at 119; the minimum for `(3,9;32)` is 104, with exact counts 39, 952,
and 18,598 at 104–106. The PDF and text extract are pinned in
`FLOOR_AUDIT.sha256`. Completeness uses the published counts, not any
completeness assumption about the searches that produced the lists.

## Degree-six residue floor 120 (cert, MTF only)

`scratch/A/root-residue/complete-v2` (3.8 MiB) contains the ordered 74-row
catalogue, the row/graph6/CNF/LRAT digest index, and compressed LRATs. It
does not need the producer's bulk gluing files or stored DIMACS files.
`scratch/A/floor-audit4/root6.tsv` is the exact canonical crosswalk. All
68 earlier rows match their original labelled graph6, DIMACS and LRAT.
The disjoint six new e119 classes occupy rows **3, 6, 14, 15, 16, 29**
in Lane G's `new119.g6` order. Their raw labels and both proof hashes
match the separately pinned originals. All 74 independently regenerated
CNFs matched byte-for-byte at packing. `replay6.log` records both
checkers accepting every bound row. See `RESIDUE_BUNDLE.md` for the CNF
reduction and smaller positive controls.

## Degree-seven residue floor 107 (cert, MTF only)

The new checker directly tests absence of independent nine-sets via
greedy-color-bounded clique search on the complement. It does not use
Lane G's edge-addition replay to infer validity. All 19,589 inputs pass
size, edge-count, triangle-freeness, alpha and per-level canonical
uniqueness checks. The checker binds 39/951/18,531 incompatibility traces
to the ordered inputs and checks every trace. The exact complement is
0/1/67. Each complementary CNF is independently generated and compared
byte-for-byte in the original group order. The `LRAT` records in
`e105.log` and `e106.log` include original row number, proof path, three
digests and the verbatim lines `c VERIFIED` and `s VERIFIED UNSAT`. The
proof files are read in place. The MTF demand lemma is in
`../G/rows/floor7.md`.

Calibration: 191 canonically distinct `(3,7;22)` graphs agree with the
existing alpha checker, including positive and threshold+1 tests. At 220
planted six-regular roots, each singleton and all 2,259 uncovered residual
pairs have an actual attachment. The audit rejects a zero demand mask and
a replaced e105 exception (logs `negative_*.log`).

## Exact distribution delta

The arithmetic replay used G's existing checkers without an LP optimizer:
231 round-1, 63 floor-119, and 36/40/48/45 round-3 Farkas witnesses passed.
Independent bookkeeping starts from the pinned 545 MTF distributions,
verifies the round-1 table against the 524 near-regular keys and witness
thresholds, derives the 454-case input to round 3, and reconstructs
`round3_cases.csv` byte-for-byte. At a degree-six root the 33 exterior
vertices all have an attachment. Each of six private cells has at most
four vertices, since its members are independent and anticomplete to the
other five attachments. Thus at least `33 + (33 - 24) = 42` attachment
incidences plus six root edges give `Z >= 48`. Floor 120 excludes all e167
cases with a degree-six vertex: 56 original keys and **55 incremental**.
Using the earlier degree-eight and degree-nine gluing floors, the
degree-seven stages 105/106/107 add **8/6/9 conditional cuts**. **376
near-regular cases + R** remain under this tally; 13 more would fall if
complete e88 MTF gluing were excluded. This audit does not establish that
e88 exclusion. The independent delta also matches all 91 keys and 78
witness locators in G's `round3_frozen.csv` (`frozen-compare.log`).

## Reproduce

From the workspace root, with a fresh output directory under `scratch/A`:

```sh
bash ralph/lanes/A/replay_floor_audit.sh scratch/A/floor-audit4-replay
```

Observed costs: e106 pilot 1.95 CPU-s; full e104–106 audit 65.2 CPU-s,
266 MiB peak RSS. Degree-six pack/crosswalk/replay about 9 CPU-s; Farkas
replay about 12 CPU-s. See `scratch/A/floor-audit4/estimate.txt` and its
per-check logs. The full replay script passed in 89.6 CPU-s (90.2 wall).
No SAT calls or detached jobs.
