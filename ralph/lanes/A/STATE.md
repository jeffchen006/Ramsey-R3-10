# Lane A state

Round 22, November 22, 2026. Allocation 2; independent reference and board
binding for G, not a second solver queue. R(7) remains closed by C's accepted
finite certificates, already replayed by A. Case R remains open. No candidate,
new target proof or case debit by A.

## Jobs

| PID (timeout / worker) | Command | Log | Cores | Start / expected end |
|---|---|---|---:|---|
| — | No detached jobs | — | 0 | — |

No target SAT. Foreground, one bounded reference worker at a time,
`nice -n 5`, `timeout`, `prlimit --cpu`, 512 MiB VM. `scratch/A/r22`
has the frozen output; `scratch/A/r22-final` and `scratch/A/r22-audit`
have clean replay timings. All 15 byte comparisons and 27 input/artifact
pins pass. `scratch/A/r22/audit.replay.log` records the comparisons. Total
timed cost 268.46 CPU-s (0.07457 core-h), including development and the
failed stronger-mutation attempt; largest RSS 148,224 KiB.

## Results and claims

| Label | Scope / exact result | Evidence | Core-h |
|---|---|---|---:|
| enum (calibration) | Historical exact one-defect class sets 129/11 at n15/16. Independently scanned all 2,576/7 n16/17 graphs at alpha<=5 and literally rebuilt 788/308 layouts; both two-defect sets empty. | `ROUND22_TWO_DEFECT.md`, `scratch/A/r22-audit/small.log` | 0.00675 per full control replay |
| enum (pending critic) | Exact width-three n16 two-defect **toy**, alpha<=6 and no MTF: 127,086 labelled placements, 53,411 board/class incidences, 8,119 unmarked classes, exact physical rescan; independent graph checker accepts all. Aliasing deletes 59,856 placements and 1,702 unmarked classes; explicit incompatible same-mask edge bits, short padding and optional/optional witnesses. G matches four representative projections and tests alias/short clauses on physical plants. | `ROUND22_TWO_DEFECT.md`, `ROUND22_FREEZE.sha256`, `scratch/A/r22/positive`, `scratch/A/r22/positive.check.log`, `scratch/G/round22/control.log` | 0.01011 per full positive replay, plus 0.00058 independent graph check |
| hand + enum (pending critic) | Necessary weak h=6 board census: 22,408 raw keys, 49 board orbits (9 RR, 16 RS, 24 SS), 19,651 hole-context keys. 80 root-oriented orbits; 18 swap-stabilized reps, only 16 bare-transpose fixed. Corrected label -> rep maps, independently compared by G for all raw boards and hole keys. No feasibility claim or solve. | `ROUND22_TWO_DEFECT.md`, `ROUND22_FREEZE.sha256`, `scratch/A/r22/h6.{boards,labels,holes}.tsv` | 0.00125 per cover replay |

## Next

- G owns calibrated h=6 target work. A has delivered both references on the
  board. Replay from root: `bash ralph/lanes/A/replay_two_defect22.sh r22-review full`.
  Confirm any later target coverage only against checked bindings/receipts.
- End h=7 comparisons; do not relaunch retired h=7 contexts. No h<=5
  extrapolation from this census. G-019 is already confirmed pub + enum.
- R19 card interface and held-out roster: `ROUND19_DELETION_CARDS.md`,
  `ROUND19_FREEZE.sha256`, `scratch/A/r19`. C owns fifth-row/join work.
  Earlier profile weights: `ROUND17_DIRECTION_PROFILES.md`,
  `ROUND17_FREEZE.sha256`, `scratch/A/r17-stream/weights{16,17}.tsv`.
