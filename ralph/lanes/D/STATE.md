# Lane D — round 19, 2026-11-22 (final)

**Marked R(3), `K=2,t=17,m=15` (hand + enum): 4,817,781 compatible ordered wing assignments on the 162 fixed supports; 3,128,474 marked orbits. All 162 survive.** Independent bitset and coefficient counts agree, down to the individual group elements. Submitted for critic review; not a SAT result or closure. D-045's necessary support census and the separate D-044 `m=16` exclusion are critic-confirmed. `S=scratch/D/wing19`.

## Jobs

| PID | Command / log | Cores now | Start | Actual end |
|---|---|---:|---|---|
| none | Sequential bounded foreground only (`wing19.py`, `wing19_audit.py`, `wing19_filterprice.py`; `S/*.log`). No detached, live or stopped jobs. | 0 | ~16:03 | 16:09 |

## Results and claims

| Label | Result | Evidence | Core-h |
|---|---|---|---:|
| hand + enum | `e∈T`: 2,378,983 ordered / 1,549,150 marked orbits; `e∉T`: 2,438,798 / 1,579,324. On all pole labels, oriented weights 7,784,709,450 and 7,941,987,900. Not labelled Y or wing sites. No tip exchange. | `WING19.md`, `S/{counts.tsv,target.log,audit.log}`, `ROUND19_FREEZE.sha256` | 0.00104 count; 0.00122 audit |
| enum | All per-host weight/divisibility checks and 267 per-permutation counts matched; 99 of 105 nonidentities have nonzero fixed counts. Recovered literal 10/5 and 60/12 toys, rejected exchange, recovered all 125 physical C22 marks. | `S/{toy,controls,audit}.log`, `wing19_audit.py` | 0.00009 controls |
| hand + estimate | A tight pairwise-intersecting family of Y rows forbids two same-shore sites contained in its pole union and each meeting every member. Blocks physical duplicate masks too. Synthetic price (no target host): 0.252 CPU-s to index 406 row-pair masks per shore, 1.46 CPU-s projected host step; no measured target rejection rate. | `WING19.md`, `S/{filterprice,price}.log`, `wing19_filterprice.py` | 0.00034 both prices; **0.00270 total** (`S/*.time`) |

## Next

1. Critic/H: `bash ralph/lanes/D/round19_replay.sh scratch/critic/D19-audit` (fresh directory). Do not add the weighted counts to unlabelled orbits or treat the orbits as physical graphs. No original-kernel, `m=15`, `t=17` or K=2 closure. No candidate; R(4) not reached.
2. Request a **single count-only filtered join**, ≤30 CPU-s / 64 MiB, one worker, preserving all marked actions. Independently calibrate the tight-family rule on literal small margins before running it. No further action if not authorized. No proof pricing or production from the current counts.
