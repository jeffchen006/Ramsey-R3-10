# Lane E state — round 5

2026-11-21; share 21 cores. No detached jobs, no candidate, no Ramsey
verdict. All symmetry claims concern all graphs, not just MTF. The
f=32 crown uses the separate certified universal minimum degree five;
the all-graphs f=28 a=6 argument does not. Round 4 archived in `LOG.md`.

## Jobs

All jobs are collected; no lane-E solver or replay remains. Times below
are host clock; wrapper PIDs are one core each. Production and replay
use `nice -n 5`, wall and CPU caps, and 16 GiB `ulimit -v`.

| Command and wrapper PIDs | Start; planned end | Evidence and status |
|---|---|---|
| `cubic32.py calibrate/census` from `scratch/E/r5_cubic`, serial | 21:15; <25 CPU s per invocation | `calibration.log`, `census.log`, `saturated.log`; exact smaller counts, 1058/6904 representatives |
| `run_cubic32.sh` pilots, 3525085–3525094; native LRAT and relaxations 3568003–3568011 (8); short pilots 3667362–3667375 (13) | 21:15–21:20; max 25 CPU/55 wall s per stage | `r5_cubic/{window,lrat,relax}.*.log`, `r5_saturated/short.*.log`; calibration harness error fixed and rerun before noncubic production |
| From `scratch/E/r5_cubic`, `cubic_batch.sh full OFFSET 8`, 3594311–3594318; seven interrupted wrappers rerun 3803040–3803046 | 21:18:19; est. 21:21–21:26; finished 21:23 | 1,058 checked; initial batch recorded seven interruptions while script was edited, all rerun to checked UNSAT; no caps |
| From `scratch/E/r5_saturated`, `cubic_short_batch.sh OFFSET 12`, 3697455–3697467 except 3697458 | 21:21:11; est. 21:26–21:33; finished 21:28 | `batch.OFFSET.tsv`; 6,904/6,904 checked; no caps |
| From `scratch/E/r5_cubic`, `replay_cubic32.sh full OFFSET 8`, 3952064–3952072 except 3952068 | 21:27; finished 21:32 | `replay.OFFSET.log`; 1,058/1,058 regenerated and replayed |
| From `scratch/E/r5_saturated`, `replay_cubic32.sh short OFFSET 512`, 4006589/90/91/93 | 21:28; finished 21:28:18 | `replay.{0,1,66,127}.log`; 56/56 regenerated and replayed |
| `window73.py`/`shortg`; `freeze_cubic32.py`, serial | 21:24–21:30 | `window73.log`, `freeze.log`, `certificates.sha256`; all initial checked proofs bound |

## Results and claims for H/critic

| Claim | Label | Evidence | Decisive core-hours |
|---|---|---|---:|
| `(2,28)` excluded by the frozen cover: a≤3 and a=5 hand, a=4 cert, a=6 enum, a=7 inherited F10. No new run. | mixed hand/cert/enum, pending aggregate review | `ralph/lanes/E/f28_cover.md` and its cited evidence | — |
| `(2,32,t=4,δ(W)≥2,e(W)=12)` excluded, including both cubic cores and all 12 noncubic saturated cores. An attachment omission forces at least one 26-vertex window with ≤74 edges. All 1,058 cubic and 6,904 noncubic window CNFs check UNSAT. No unchecked final UNSATs or caps. | cert, pending scope review | `ralph/lanes/E/cubic32.md`, `ralph/lanes/E/replay_cubic32.sh`, `scratch/E/r5_cubic/freeze.log`, `scratch/E/r5_saturated/freeze.log` and corresponding bindings | 1.2144 (production only) |
| `(2,32,t=4,δ(W)≥2)` forces fixed degree eight at every W vertex, and if `e(W)≥9`, all attachment vertices have fixed degree seven and `e(G)=176`. If `e(W)=11`, all four windows have 74 edges and the W–A incidence counts are `(10,10,10,12)` or `(10,10,11,11)`. | enum-assisted necessary bound, not closure | `ralph/lanes/E/window73.md`, `ralph/lanes/E/window73.g6`, `scratch/E/r5_saturated/window73.log` | <0.001 |
| Smaller support generators agree with independent subgraph and exact completion oracles; 3/4 pair-only relaxations SAT, while all four matched full pilot windows are checked UNSAT. | calibration and comparison | `scratch/E/r5_cubic/{calibration,relax.0,lrat.0}.log`, `ralph/lanes/E/cubic32.md` | <0.01 |

## Next steps

- H/critic: audit the 74-edge window reduction and SAT support cover;
  replay as desired. Do not mark all of f=32 closed or ask F to skip this
  whole symmetry family. No work needed on f=28 unless an audit fails.
- Remaining `(2,32)` crowns: `t=2,3`, `t=4` with `δ(W)≤1`, or with
  `δ(W)≥2` and `8≤e(W)≤11`. For 11 edges use degree saturation and
  the two incidence patterns in `window73.md`. Always omit a large
  group; two size-10 support pins remain in either pattern. A cheap
  `geng` pilot found 19 cores and pre-automorphism upper bounds 39,484
  two-support and 491,520 three-support combinations before omitted
  group feasibility (`scratch/E/r5_saturated/e11.forecast.log`). This
  is not a full coverage size or SAT timing; tighten before scaling.
- No work on `(5,0)`, order 3, or the other involution families. Prior
  `(5,5)` remains cert (`slim5.md`).
