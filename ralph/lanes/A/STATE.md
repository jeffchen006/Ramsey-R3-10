# Lane A state

Round 17, November 22, 2026. Share 5; no detached A jobs or new graph,
distribution exclusion, or whole-case closure. R(7) was closed by C's
accepted finite certificates (round 1) and replayed independently by A.
Marked 17/17 is accepted; do not rescan it, the R(7) cubes, or the retired
e168 strips. One-neutral marked 16/17 target package-filter accounting
uses the following new files; A did not perform its full target filter.

## Jobs

| PID (timeout / worker) | Command | Log | Cores | Start / expected end (CET) |
|---|---|---|---:|---|
| — | No detached A jobs | — | 0 | — |

Only bounded foreground C++ builds, audits and a side roster stream;
individual stages used `nice -n 5`, wall ≤120 s and VM ≤512 MiB, with
120–150 s CPU caps. Peak two processes for the producer/consumer pipe.
Clean replay: 86.51 CPU-s (0.0240 core-h); ten outputs byte-identical.
Total A compute this round <0.08 core-h including two capped aggregation
attempts and recompiles. Successful peak 319,208 KiB (compiler); working
checks below 79,000 KiB. Retained 28 MiB allocated scratch, including
one copy of the target weights. All 33 hash bindings checked.

## Results and claims

| Label | Scope/result | Evidence | CPU-h |
|---|---|---|---:|
| hand (pending critic) | Exact one-direction existence key: `(order,host,neutral)` destination + sorted group type multiset, with each group tuple sorted separately. Strata `(D,d)` join on complement; the both-pass labelled mass is a product of the two separately filtered subtotals at each fixed destination pair. Do not reuse this key for joint crossing or terminal results. | `ROUND17_DIRECTION_PROFILES.md` | — |
| enum (calibration) | Literal full 6/7 control matches weighted four-way counts: both 31,495, 6→7 only 3,009, zero reverse-only and neither; 34,504 total in each read order. All 153 marks pass, giving 142 distinct physical header IDs. Equimarginal adjacency changes the answer; permutations within a group preserve it. All 2,067 group receipts match C independently. | `scratch/A/r17-stream/{small.log,cross.log}` | <0.001 per control pass, excluding build |
| enum (target weights only, pending critic) | 2,223,225 / 28,834 joint cells representing 2,817,701 / 59,521 exact side frames; all old host/margin/shape counts and all 34 original products reproduced. **15,051,526,031** unfiltered headers; 582,982 compatible destination pairs with 6,118 forward and 1,001,962 reverse group query keys. 166,899,580 subtotal bucket visits if neither direction short circuits. No full target survivor count from A. | `scratch/A/r17-stream/{weights16.tsv,weights17.tsv,mass.log}`, `ROUND17_FREEZE.sha256` | 0.021 for a clean target weight generation + mass check, excluding build |
| enum (pilot agreement only) | All 544 frozen pilot IDs agree with every archived per-group presence bit; 47 both, 140 forward only, 96 reverse only, 261 neither. The 47 are not new terminal outcomes. | `scratch/A/r17-stream/{pilot.oracle.tsv,pilot.log}` | <0.002 per pass |

## Next

- C has the full weight tables and owns production/pricing. Use
  `scratch/A/r17-stream/weights{16,17}.tsv`; the old global Python
  aggregation in `scratch/A/r17/` hit the cap and its target file is
  unusable. Host-local aggregation uses ~61 MiB; streamed mass check
  uses ~77 MiB. Do not expand the header product.
- Run `bash ralph/lanes/A/replay_direction_profiles.sh all r17-replay`
  for clean weight regeneration and control checks. Any weighted target
  survivors remain only necessary-condition survivors; retain physical
  frame labels, marks, neutral and orientation for a later exact join.
- Review C's measured quotient and actual survivor mass before selecting
  any new production. No automatic scan of the one-neutral tails or two
  zero-neutral splits; no Case R debit.
