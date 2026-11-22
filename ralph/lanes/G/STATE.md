# Lane G — round 23, November 22, 2026

**238 near-regular MTF distributions plus R remain open.** No candidate,
whole-distribution, `t9`, U88, or residue-floor change. Marked adjacent `e=170`
has accepted `h=8,7,6`; the `h=6` driver has now been fixed without solving.
`h=5` is partial: frozen 21:21:15 CET, **254/286 whole boards**, covering
**138,687/156,112 keys**; including verified relabelled partial-board keys,
**144,284/156,112 keys**. The ongoing snapshot is separate. `h≤4`, the
single-degree-six slice, and their parent distributions remain open.

## Jobs

Stage = `scratch/G/round23`. Latest dispatch snapshot `final-jobs.json`
(full args, process tree, CPU and stage size). At 21:25:13 the original
queues had finished and the following 11 one-core binary jobs were live.
All are detached under 5 GiB VM. Check actual `ps` before reassigning.

| timeout / Bash worker PID | Command and log (stage-relative) | Start | Deadline |
|---|---|---|---|
| 1748673 / 1748795 | `round23_binary_worker.sh pilot d283_100 l283_100` / `l283_100.log` | 21:25:02 | 21:50:02 |
| 1748784 / 1748830 | `round23_binary_worker.sh pilot d234_111 l234_111` / `l234_111.log` | 21:25:02 | 21:50:02 |
| 1748802 / 1748871 | `round23_binary_worker.sh pilot d242_111 l242_111` / `l242_111.log` | 21:25:02 | 21:50:02 |
| 1748869 / 1748991 | `round23_binary_worker.sh pilot d243_111 l243_111` / `l243_111.log` | 21:25:02 | 21:50:02 |
| 1748898 / 1748918 | `round23_binary_worker.sh pilot d254_111 l254_111` / `l254_111.log` | 21:25:02 | 21:50:02 |
| 1748913 / 1748983 | `round23_binary_worker.sh pilot d259_111 l259_111` / `l259_111.log` | 21:25:02 | 21:50:02 |
| 1748950 / 1749015 | `round23_binary_worker.sh pilot d277_111 l277_111` / `l277_111.log` | 21:25:02 | 21:50:02 |
| 1748956 / 1749000 | `round23_binary_worker.sh pilot d278_111 l278_111` / `l278_111.log` | 21:25:02 | 21:50:02 |
| 1748987 / 1749095 | `round23_binary_worker.sh pilot d280_111 l280_111` / `l280_111.log` | 21:25:02 | 21:50:02 |
| 1749008 / 1749096 | `round23_binary_worker.sh pilot d283_101 l283_101` / `l283_101.log` | 21:25:02 | 21:50:02 |
| 1749082 / 1749176 | `round23_binary_worker.sh pilot d283_110 l283_110` / `l283_110.log` | 21:25:02 | 21:50:02 |

Stage used 4.19 GB at 21:25:03. Latest workers each reserve 100 MB binary
+230 MB sliced ASCII, shared archive cap 4.48 GB under 8.8 GB stage
envelope. At least one checked board beyond the freeze (269) is in the
unfrozen view. All prior PIDs are historical;
`queue{1,2,3,4}.{pids,workers,tsv}`, `pilot.pids`, `deficit.pids`,
`mtf.pids`, `binary.pids`, `fresh.pids`, `recovery.{pids,workers,tsv}`
provide prior launch logs; latest in `late.{pids,workers}` and
`recovery-late.tsv`.

## Results and claims

| Label | Result | Evidence | Cost |
|---|---|---|---:|
| enum replay correction, no new debit | Correct h6 replay under A's versioned old-to-new maps, inverse restores all 22,408 labels; 49 board masses and 19,651 literal keys; old reversal rejected in 19,908 labels; both hole fixtures. No new G-059 claim. | `round23_transport.py`, `ROUND23_FREEZE.sha256`, stage `transport.log` | 5.77 CPU-s |
| hand + enum + local cert (pending critic) | At frozen h5 checkpoint, +30 whole boards and +16,779 whole-board keys over inclusive 224/121,908; 97 new checked proof files. Four fresh sampled CNF/hash/dual rechecks. Partial-board transport supplies 5,597 additional keys; request separate check by H/critic. | `ROUND23_REPLAY.md`, `ROUND23_FREEZE.sha256`, stage `handoff.json`, `hole-handoff.json`, `receipt-freeze.sha256`, `freeze-root-check.log` | 5.054 timed attempt core-h plus controls/fresh replay |
| hand + enum | Compact I10 clauses with physical guards; exact exterior edge sum via 8 degree deficits; A's four witnesses and three adverse mutations; 1,960 literal smaller positives, 48 independent small edge totals, 15 local guarded probes. Smaller sequential deficit block ~17.5k vs ~64k clauses. | `rows/e170_h5_physical_deficit.md`, stage `controls.log`, `oracle.log`, `deficit-control.log` | 0.002 core-h controls |
| hand + enum + open | Exterior MTF rows validate on 56 native/1,960 exterior-saturated controls and 1,904 negatives; target pilots `m174_1`, `m177_1` resource/raw capped. No scale-up yet. | `round23_mtf{,_audit}.py`, stage `mtf-control.log`, `work/m17*/` | <0.06 core-h |
| enum + local cert / open | Binary LRAT transport exact on PHP, verified sample slices; 249/11 stays open. Nine earlier successful binary branches from the 21:21 freeze can be replayed with the common receipt reader, and recovery continues. Proof archive guards alone never count as checked, even following solver UNSAT and initial checker success. | `round23_binary_lrat.cc`, `round23_binary_worker.sh`, stage `trim/`, `work/q*/`, `work/r*/` | included |

At fixed 21:21:15: 197 terminal attempts, 97 checked; others 44 raw
caps, 37 SAT relaxations, 17 archive-guard failures, one binary resource
failure, one earlier resource exit. Largest timed RSS 527,124 KiB,
3,382,286,169 bytes retained. Later receipts need a new snapshot/freeze.

## Next

1. Collect live jobs above, run `round23_h5_status.py .` and independently
   `round23_h5_hole_cover.py . SNAPSHOT`, then freeze any new receipts.
   Keep whole-board key count separate from partial-board transported keys.
   A key with any labelled representative in a checked prefix is excluded
   because changing labels preserves the graph and that board; no symmetry
   of a graph is assumed. All checked paths are exact occupancy scopes.
2. For remaining raw-cap leaves with prior UNSAT, prefer compressed binary
   retries or split on the next unassigned physical shore bit. Do not repeat
   `249/11` under the same binary cap. Plan exact cover separately from
   storage and increase archive room only if simultaneous file reserves fit.
   Avoid dropping any retained proof; specifically reserve archive capacity
   **before** dispatch so a checked raw is not stranded by a guard.
3. For genuine SAT relaxations, seed physical I10 cuts with the saved models
   via `round23_h5_seed.py`. Keep explicit selector guards and full boundary
   padding. Neither dense depth overlay nor raw-capped exterior MTF pilots
   alone justify scaling. Do not report a relaxation as a candidate.
4. Do not debit a parent distribution until both open structures are closed.
   Sixteen `e=170` degree-six distribution keys remain (nine single, seven
   adjacent pair); exact `t9` thresholds in `ROUND13_REPLAY.md`. `32/e108`
   stays with lane B. Historical round-22 state in stage `round22.STATE.md`.
