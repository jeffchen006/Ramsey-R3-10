# Round 16 — critical receipt crosswalk and e109 source screen

## Result: cert inventory, pending critic

All **1,875 supplied deletion-critical** order-32/e108 keys bind to prior
MTF degree-seven-root certificate receipts, with **zero unbound keys**.
The exact disjoint merge with the accepted named reducible inventory
matches `scratch/B/work/e108_r11/union.g6` byte for byte.

| Critical cohort | Demand cliques | Dual LRATs | Unbound |
|---|---:|---:|---:|
| r6 | 569 | 45 | 0 |
| r8 | 761 | 381 | 0 |
| r10_scout | 57 | 4 | 0 |
| r10_stitch | 2 | 3 | 0 |
| r10_repuncture | 5 | 1 | 0 |
| r11 | 37 | 10 | 0 |
| Supplied critical total | 1,431 | 444 | 0 |
| Accepted supplied reducible total | 2,016,206 | 86,065 | 0 |
| Exact named union | 2,017,637 | 86,509 | 0 |

The 2,104,146 named keys are not the 2,104,151 in GR Table 14. The
**five absent critical keys** do not have ranks or certificates here.
Nothing was discovered or solved anew; no floor 109, distribution debit,
e88/U88 change, or order-40 candidate.

The machine-readable crosswalk is `scratch/B/work/e108_r16/critical-crosswalk.tsv`.
Each row starts with the canonical key and its 1-based union rank. The
cohort names map to `COHORTS` in `src/e108_r16_crosswalk.py`; `input_rank`
refers to that cohort's archived input in its original labeling, also
stored as `original_g6`. For a clique, `receipt_line` indexes the clique
file. For an LRAT it indexes both archived logs and the complement row;
`pins_line` is the physical line in `pins.tsv` (0 means unpinned). The
filename and CNF/payload hashes identify the exact checked proof. Raw
inputs, receipts, pins and both logs are checked against the earlier
freezes; each LRAT payload is hashed against both frozen logs. These
checks do not rerun proof search or the semantic proof checkers. No
binding required a fresh semantic replay. The negative controls detect
missing receipts, overlapping dispositions, switched labeled graphs,
duplicate canonical keys and a changed replay digest.

The reducible source and round-15 disposition stream are read in tandem
and digest-checked, then lexically merged against the normalized critical
keys, rejecting overlaps. An independent shell check (`sort -m -u`,
`cmp`, `awk`) reproduces the union bytes and checks every critical
rank against the original frozen union. Logs are
`scratch/B/logs/e108_r16_{crosswalk,independent_join}.log`.

## One-edge descent: hand, calibrated enum, and source gap

For triangle-free H, an addition H+xy preserves triangle-freeness iff
xy is a nonedge and `N_H(x) ∩ N_H(y)` is empty. Adding an edge cannot
increase alpha. Thus a **complete independent e109 source** yields all
and only the **addable** e108 critical keys by one-edge deletion, Ramsey
screening, and criticality testing. In a parent, deletion can create a
new forbidden independent set only using both endpoints, so the filter
looks for the remaining vertices outside both endpoint neighborhoods.
Saturated e108 keys have no eligible e109 parent and need a separate
argument or source. Absence in a partial source cannot establish saturation.

- Complete (3,6;16), 2,576 classes: descent from all 200 e34 parents
  recovers **13/13** withheld critical e33 keys, 137 labeled successful
  deletions, no extra keys or saturated misses. The e33 roster has 39
  total keys; `irreducible` independently gives the withheld set.
- Removing the two parents of one addable withheld key makes exactly
  that key unrecovered without changing its addability. An exhaustive
  labeled order-5 control leaves just the C5 class at e5 and no legal
  e6 parents: **0/1** criticals recovered, **one saturated** miss.
- All **1,875 supplied criticals are addable**, with **35–48** available
  pairs each; no inference about the five absent keys. The target arm
  computed only endpoint masks and did not materialize e109 graphs.
- The snapshot inventory sampled 3,920 workspace loose g6/s6 paths
  (plain: up to eight lines at start/middle/near tail; compressed: first
  eight). It observed order 32 in 226 files, no e109 records. No explicitly
  named e109 catalogue was found. The public screen found McKay's file
  for the order-35 (3,9) graph, not e109; Angeltveit's article reports
  the up-to-e112 computation without locating an e109 download on the
  checked page. This is a scoped source screen, not an exhaustive search
  of arbitrary filenames, archives or private project storage. See
  `scratch/B/work/e108_r16/source-{paths.txt,screen.tsv}` and
  `scratch/B/logs/e108_r16_{local_source,public_source,descent}.log`.
  Adding edges to already-known e108 keys does not give an independent
  source (round 6 had already tried higher-edge excursions). With no
  independent e109 input in hand, the target descent stops here.

## Replay

From `scratch/B`, use `LC_ALL=C`, `PYTHONDONTWRITEBYTECODE=1`,
`ulimit -v 16777216` and `ulimit -t 45`. Create a fresh lane-owned output
directory `DIR`; no solver is involved.

```bash
S=../../ralph/lanes/B/src
nice -n 5 timeout 60s python3 "$S/e108_r16_crosswalk.py" "$DIR/critical-crosswalk.tsv"
nice -n 5 timeout 60s python3 "$S/e109_descent_r16.py" control "$DIR"
nice -n 5 timeout 60s python3 "$S/e109_descent_r16.py" inventory "$DIR" --paths work/e108_r16/source-paths.txt
```

Successful checks took 6.93 CPU-s for crosswalk, 1.18 CPU-s for the
independent join, 0.81 CPU-s for descent controls plus addability, and
1.70 CPU-s for local inventory (~0.003 core-h total, peak 27,600 KiB).
The inventory was IO-limited (31.96 s wall); files are not a guaranteed
long-term snapshot. All runs were foreground. No outstanding jobs.
