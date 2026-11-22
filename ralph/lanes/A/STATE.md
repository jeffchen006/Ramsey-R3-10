# Lane A state

Round 18, November 22, 2026. Share 6; no detached A jobs or new graph,
distribution exclusion, or whole-case closure. R(7) was closed by C's
accepted finite certificates (round 1) and replayed independently by A.
Marked 17/17 is accepted; do not rescan it, the R(7) cubes or the retired
e168 strips.

## Jobs

| PID (timeout / worker) | Command | Log | Cores | Start / expected end (CET) |
|---|---|---|---:|---|
| — | No detached A jobs | — | 0 | — |

Only foreground jobs: processes under `nice -n 5`, timeout and 512 MiB
VM limit, peak two processes for frame producer/consumer. 176.07 measured
CPU-s = 0.04891 core-h total, including builds and clean replay. Peak
330,904 KiB (compiler), working checks ≤90,496 KiB. About 5.1 MiB new
allocated scratch. Clean binder 30.71 CPU-s; frozen A17/C17 pins verified.

## Results and claims

| Label | Scope/result | Evidence | CPU-h |
|---|---|---|---:|
| enum (calibration) | 34,504 ordered 6/7 physical IDs, 31,495 both-pass, all 153 plants (142 distinct physical IDs), 2,067 archived group decisions, 29,220 destination-pair totals. | `scratch/A/r18-clean/small/result.log` | included in total |
| enum (physical binding, pending critic) | Marked one-neutral 16/17, shapes `2333/3334`: `(67,5)` 32,340 raw → 46 both-pass; `(68,4)` 28,301 raw → 24. 12,762 group keys and 11,250 exact bucket totals. All 60,641 raw physical IDs and group bits checked using archived literal evaluator. | `ROUND18_PHYSICAL_IDS.md`, `ROUND18_FREEZE.sha256`, `scratch/A/r18/{survivors.cases.tsv,survivors.tsv,buckets.tsv,literal.oracle.tsv}` | 0.03136 literal check; 0.04891 all |
| enum (pilot accounting) | 16 old raw IDs in each slice; only both-pass intersection is `(2501780,31298)` (old pilot row 286, `(68,4)`), so 69 both-pass IDs new to C. | `scratch/A/r18/pilot-overlap.tsv` | included in total |

## Next

- Lane C owns the exact joint/terminal check, using the handed-off files.
  A's results concern marginal existence only; no join by A. Do not
  rescan the pilot or any new slice absent critic authorization.
- Replay: `bash ralph/lanes/A/replay_small_slices.sh all r18-review`,
  optionally followed by `bash ralph/lanes/A/replay_small_slices.sh literal r18-review`.
  Use `scratch/A/r18/survivors.cases.tsv` for the pinned 14-int handoff;
  the companion `survivors.tsv` preserves original labels and orientation.
- Previous hand/enum results and target profile weights are preserved in
  `ROUND17_DIRECTION_PROFILES.md`, `ROUND17_FREEZE.sha256`, and
  `scratch/A/r17-stream/weights{16,17}.tsv` (not the failed `r17/` file).
  The full marginal filter was C's run. No unpriced scans of the
  2.54-billion survivor roster, remaining one-neutral tails or zero-neutral
  splits; no Case R debit.
