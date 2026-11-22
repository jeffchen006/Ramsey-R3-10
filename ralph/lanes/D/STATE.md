# Lane D — round 18, 2026-11-22 (final)

**Marked R(3), `K=2,t=17,m=15`: 162 necessary untouched support types** (hand + enum, submitted for critic review). Not a closure; no target shore pair constructed, no SAT, proof or candidate. The `m=16` exclusion D-044 is critic-confirmed and includes the 384-ID checkpoint D-043. Prior production evidence remains unchanged; round 17 handoff is in `LOG.md`. `S=scratch/D/triple18` below.

## Jobs

| PID | Command / log | Cores now | Start | End |
|---|---|---:|---|---|
| none | All bounded foreground census/audit/price/replay steps finished; no detached, live or stopped jobs. | 0 | 14:36 | 14:44 |

## Results and claims

| Label | Result | Evidence | Core-h |
|---|---|---|---:|
| hand + enum | For the oriented marked path, the exceptional pole `e` has `(1,2)` wing contacts. One physical Y triple `T` and 13 doubles. Of 1,143 raw supports, 959 fail ordinary Hall and 22 more fail only with the triple: 3 triangles, 4 inside stars, 15 outside stars. **99 survive with `e∈T`, 63 with `e∉T`**; 407,400 + 243,600 fully pole-labelled oriented supports. No sufficiency/exclusion of `m=15` asserted. | `TRIPLE18.md`, `S/{roster.jsonl,witnesses.tsv,census.log,audit.log}`, `ROUND18_FREEZE.sha256` | 0.00047 census + independent audit |
| enum | Literal four-pole controls (432); all 125 C22 planted marks (22 containing a triple) and 10 regular hosts recovered. Different auditor proves disjoint coverage using independent raw polynomial coefficients 21,638 and 18,732. Two clean replays, each five deterministic bytestrings matched plus the exact pricing counts. | `S/{controls.log,replay.log,final-replay.log}`, `round18_replay.sh` | 0.00005 controls; 0.00126 clean passes |
| estimate | Marginals 4,062 and 6,202: 4,081,188,888 naive pairs, 283,218,542 degree-relaxed ordered output **upper bound, not an observed count**. Price count-only Burnside with 267 marked actions, ≤22,775,634 bitset ANDs. Two smaller literal join controls verified. | `S/{price.log,clean/price.log}`, `triple18_price.py`, `TRIPLE18.md` | 0.00021 pricing; **0.00198 total** by `S/*.time` |

## Next

1. Critic/H: `bash ralph/lanes/D/round18_replay.sh scratch/critic/D18-audit`. Marked data preserve short/long shore; no division by two. Distinguish canonical reps, fixed `e,T` weights, all pole-labelled oriented weights and labelled Y vertices. No whole-layer or original-kernel debit.
2. Request permission for a **count-only** compatible wing quotient across these 162 fixed hosts, using popcounts and stabilizer fixed counts, never storing the ordered pair product. Forecast 7–13 CPU-s inner loops; propose abort cap 90 CPU-s/64 MiB on the first pass. Independently check totals before any terminal pricing. No new cores needed; do not start a proof wave or infer any speedup from D-044 to this layer.
