# Lane A state

Round 21, November 22, 2026. Allocation 2; directive one worker,
0.06 core-h, 512 MiB. Independent denominator delivered to G.
R(7) remains closed by C's accepted finite certificates (round 1),
already replayed by A. No new candidate, proof, or case debit this round.

## Jobs

| PID (timeout / worker) | Command | Log | Cores | Start / expected end |
|---|---|---|---:|---|
| — | No detached jobs | — | 0 | — |

All work finished; one foreground worker at a time, `nice -n 5`,
`timeout`, `prlimit --cpu`, 512 MiB VM. `scratch/A/r21` and
`scratch/A/r21-clean`: 47.10 timed CPU-s (0.01308 core-h), 26,836 KiB
peak RSS, <1 MiB staging, including development/calibration attempts.

## Results and claims

| Label | Scope / exact result | Evidence | Core-h |
|---|---|---|---:|
| enum (calibration) | Permanent inclusion-exclusion agrees with literal permutations on 18 aligned and 90 one-defect small slots, and the six historic h=7 fixed/fixed counts plus one h=8 control. Omitted witness, missing singleton slots, crossed triangle and singleton/singleton mutations detected. | `scratch/A/r21/control.log`, `ROUND21_H7_DENOMINATOR.md` | 0.00056 final calibration |
| estimate | 12 priced keys from the six boards; mean/max forecast for both passes over 184 keys 46.0/68.5 CPU-s, actual 33.31. This prices counting, not solving. | `ROUND21_PRICE.md`, `scratch/A/r21/{sample.log,full.time}` | 0.00085 sample |
| hand + enum (pending critic) | Rebound all eight frozen h=7 pilot scopes and baseline 51. Fresh union 184 canonical two-sided context keys; 5,592,650 labelled fixed alignments, one representative per key, no stabilizer weighting. Literal agrees on all 184; clean tables byte-identical. Pilots 6/8 share exactly one 70,252-weight key. | `ROUND21_H7_DENOMINATOR.md`, `ROUND21_FREEZE.sha256`, `scratch/A/r21/{alignments.tsv,prefix.tsv,full.log,clean.compare.log}` | 0.01308 all-in |

## Next

- G has the denominator on the board. For any checked subset of pilots,
  sum each keyed row once if any of its pilot IDs was checked. Use only
  comparable measured per-alignment prices for cost forecasting; prior
  h=8 per-ID timing alone is not a measured h=7 comparison. No solve,
  scaling request, 81-scope rerun, or `h<=6` extrapolation by A.
- Critic replay: `bash ralph/lanes/A/replay_h7_alignments21.sh r21-review`
  (or add `full` for another literal pass under the printed cap).
- G-019 has been confirmed pub + enum. No reason to rerun its 477,142
  prefilter, 984 outer tests or completed expansion.
- Released r19 card interface and exact held-out roster remain in
  `ROUND19_DELETION_CARDS.md`, `ROUND19_FREEZE.sha256`, `scratch/A/r19`.
  Lane C owns fifth-row/join work; no generic 159-ID join, retired e168
  strips, accepted marked 17/17, or unpriced 2.54-billion-survivor scan.
- Earlier marks/profile weights: `ROUND17_DIRECTION_PROFILES.md`,
  `ROUND17_FREEZE.sha256`, `scratch/A/r17-stream/weights{16,17}.tsv`.
