# Lane D — round 20, 2026-11-22 (final)

**Marked R(3), `K=2,t=17,m=15`: 3 of 162 Y supports excluded (hand + enum, pending critic).** The 159 remaining supports have 2,296,202 ordered wing assignments on fixed representatives / 1,334,977 marked orbits satisfying the tested conditions. These are not graphs. No original kernel or whole marked layer closed. Prior D-046 and D-047 critic-confirmed (`ralph/critic/round_019.md`); round 19 handoff archived in `LOG.md`. `S=scratch/D/wing20`.

## Jobs

| PID | Command / log | Cores now | Start | Actual end |
|---|---|---:|---|---|
| None | Sequential bounded foreground `wing20.py`, `wing20_audit.py`, `wing20_nextprice.py`; `S/*.log`. No detached, live or stopped jobs. | 0 | ~17:23 | 17:28 |

## Results and claims

| Label | Result | Evidence | Core-h |
|---|---|---|---:|
| hand + enum | On lines 255, 345, 350 of the frozen support roster, both individual margins are nonempty but there is no compatible ordered pair. All 3 are `e∈T`. All 162 identity counts decrease; 2,521,579 ordered assignments and 1,793,497 marked orbits removed. `e∈T` 96 hosts, 1,168,799 / 652,035 remain; `e∉T` 63 hosts, 1,127,403 / 682,942. | `WING20.md`, `S/{counts.tsv,target.log,audit.log,audit_stream.log}`, `ROUND20_FREEZE.sha256` | 0.000442 production; 0.004017 independent checks combined |
| enum | All 267 old/new/delta fixed counts, per-host margins and orbit totals independently recovered. 672 generic literal pair tests with 243 positives; equal-mask multiplicity controls, 250 planted shores survive. | `S/{controls,toy,audit}.log`, `wing20_audit.py` | included; all round work **0.00496** |
| hand + estimate | Arbitrary-size one-shore independent witness: for intersecting F, U containing its union, compatible shore count must be ≤ `1+|U|−|F|`. Strict three-site toy, 210 literal profiles. Synthetic filter only ~5.5–7.4 CPU-s projected to 159 hosts; **no target run**. | `WING20.md`, `wing20_nextprice.py`, `S/nextprice.log` | 0.00017 |

## Next

1. Critic/H: `bash ralph/lanes/D/round20_replay.sh scratch/critic/D20-audit` in a fresh audit directory. Scope is exactly three marked supports; not SAT, candidate or certificate.
2. Request the arbitrary-size one-shore count on the remaining 159, one worker, ≤30 CPU-s / 64 MiB; first reproduce the 250 planted shores for this stronger rule, then per-host actions/deltas, independent ≤60 CPU-s check if feasible. No target test or proof campaign unless authorized. R(4) not reached.
