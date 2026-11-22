# Lane A state

Round 20, November 22, 2026. Allocation 8; directive only one worker,
0.30 core-h, 1 GiB/process, 128 MiB staging. The independent G-019 middle
expansion check is done; no new graph, distribution or whole-case debit.
R(7) closed by C's accepted finite certificates (round 1), already replayed by A.

## Jobs

| PID (timeout / worker) | Command | Log | Cores | Start / expected end |
|---|---|---|---:|---|
| — | No detached jobs | — | 0 | — |

One foreground worker, `nice -n 5`, `timeout`, `prlimit --cpu`, 1 GiB VM;
`scratch/A/r20` and `scratch/A/r20-clean`. All timed work including
three calibration-development attempts: 39.14 CPU-s (0.01087 core-h).
Peak 162,136 KiB (compiler), expansion 5,292 KiB; <1 MiB new staging.

## Results and claims

| Label | Scope / exact result | Evidence | Core-h |
|---|---|---|---:|
| enum (calibration) | All 9 order-5 alpha≤3 triangle-free cores. Full literal product and order-9 census agree, 46/135/0 labeled rows and 9/28/0 unrooted classes. 18 repeated-column and 165 proper-subcolumn assignments; both removed-row controls detected. | `scratch/A/r20/small.log`, `small{0,1,2}.{raw,literal}.tsv` | 0.00016 final test |
| estimate | 12 dispersed pilot sources, including both extreme edge layers; 0.31 CPU-s expansion. Projected 2.74–5.94 CPU-s for tail using mean / max; actual 4.14 s. | `ROUND20_PRICE.md`, `scratch/A/r20/pilot.log`, `tail-expand.time` | 0.00009 pilot expansion |
| hand + enum (G-019 audit, pending critic) | From all 118 exact graph6 inputs, independent Boolean-incidence expansion gives 989 labeled source multisets, 985 rooted orbits, 984 canonical unrooted classes; 123–130 histogram matches 5/44/149/266/294/184/41/1. All 118 source bindings and class sets match. Canonical list is byte-identical; deleted whole class and deleted rooted-role-only mutations detected. Clean replay matched. | `ROUND20_D5_AUDIT.md`, `ROUND20_FREEZE.sha256`, `scratch/A/r20/{all.coverage.tsv,all.diff.tsv,all.log,clean.compare.log}` | 0.01087 all-in |

## Next

- Ask critic to review G-019's middle arrow at `ROUND20_D5_AUDIT.md`.
  No new certification or distribution exclusion; do not rerun the
  477,142 prefilter, 984 outer tests, or this complete expansion without
  a particular audit reason. Replay command: `bash ralph/lanes/A/replay_d5_20.sh r20-review`.
- Released r19 card interface and exact held-out roster remain in
  `ROUND19_DELETION_CARDS.md`, `ROUND19_FREEZE.sha256`, `scratch/A/r19`.
  Lane C owns fifth-row/join work; no generic 159-ID join, retired e168
  strips, accepted marked 17/17, or unpriced 2.54-billion-survivor scan.
- Earlier marks/profile weights: `ROUND17_DIRECTION_PROFILES.md`,
  `ROUND17_FREEZE.sha256`, `scratch/A/r17-stream/weights{16,17}.tsv`.
