# Lane D — round 4, 2026-11-21

**Open:** R(3) still has 110 surviving root-swap kernel representatives
(cover only); R(4)'s K3,4 stratum is open. No graph candidate, no new
certified exclusion. Share four cores; peak one concurrent solver.
Round 1–3 details are preserved in `LOG.md`.

## Claims and results

| Label | Scope and outcome | Evidence | Core-hours |
|---|---|---|---:|
| hand | One T-group's attachment masks obey the degree and codegree slacks and the pair/triple residual alpha bounds. | `TRIPLE_U.md` | — |
| enum | All 67,730 marked K3,4 U partitions pass that filter (0 capped). Counts C15-only / C6+C9-only / both: 8,669 / 40,008 / 19,053. Verified every emitted witness and exhaustively matched the 30 smaller control rows. | `scratch/D/triple{12,15}.{log,replay}`, `ROUND4_INPUTS.sha256` | 0.021 |
| hand | Three-fold star/pair projection entropy bound for whole pin families; singleton-codegree matching gives an extra necessary row. | `PIN_BOUND.md` | — |
| enum | Exact brute/SAT C16 counts agree for all 26 sides. Matched target cut removes 5/501. Whole-family bounds on all 110 reps (smaller orientation) remain 6.14e13 to 2.89e17; sum 6.9156e18 rounded up. These are upper bounds, not actual counts or a duration estimate. | `scratch/D/{pin_bound16.matching,pin_bound40.matching,pair_match40}.tsv` | ~0.007 |
| hand | Opposite support necessary condition and explicit 2-slot obstruction on 88 side 1 and 5-slot obstruction on 149. | `OPPOSITE_SHADOW.md` | — |
| enum | General right-incidence relaxation rejects 27/48 with width 2 and 32/48 with width 3. Matched hand blockers remove 44/501 (39/47 for 88 side 1); transversal removes 104/200 for 149. Exact per-kernel C16 outputs preserved. No whole side refuted. | `scratch/D/{opposite_shadow40.tsv,opposite_shadow40.partial.tsv,shadow_block40.tsv,opposite_block_cal16/check.log,opposite_block_r3/}` | ~0.010 |
| enum | Perfect-matching incidence on 149: 200/200 sampled pins infeasible. Unpinned relaxation hit a 32 CPU-s cap (open, no verdict). C16 positive control 17/17. | `scratch/D/{matching_kernel40.0.log,matching_kernel40.1.log,matching_kernel_join40.log,matching_kernel_join16.log}` | 0.011 |
| enum | Fixed-cycle direct/deficit exact C16 filtered sets: 37 labelled outputs across 241 profiles (all five classes). R(3) matched 8/8 UNSAT each variant; build+solve 9.57/27.87/13.02 CPU-s baseline/direct/deficit. Don't scale. | `FIXED_CYCLES.md`, `scratch/D/{fixed_cycle_cal16/,fixed_cycle_r3/matched.log}` | ~0.015 |

## Jobs

No detached jobs started this round. All bounded foreground probes
and replays ended; no running or stopped Lane D PID. Round-3 four
supervisors were gone when checked at round start. Notable caps:

| Foreground command | Log in `scratch/D` | Cores | Start CET | Hard wall | Outcome |
|---|---|---:|---|---|---|
| `triple_u 5 200000 0` | `triple15.log` | 1 | ~19:56 | 300 s | done (47.18 CPU-s) |
| `matching_kernel_join.py 9 40` | `matching_kernel_join40.log` | 1 | ~20:14 | 42 s | CPU cap (signal 24), open |

## Next

- Prioritize the opposite attachment blockers. Treat the 2-slot and
  transversal clauses as necessary conditions; seek a genuinely
  smaller exact unpinned incidence split. Preserve all 110 surviving
  rooted representatives and the C16 per-kernel labeled outputs.
- Do not launch a pin catalogue sweep from the loose upper bound or
  extrapolate the perfect matching sample to all profiles. Avoid
  repeating shared-width/core reuse and global fixed-cycle models.
- K3,4: one group at a time is demonstrably too weak; only test joint
  row resource constraints across T groups or explicit V attachments.
- H/critic: review the new hand blockers and entropy projection bound.
  Lane A certificate work is not needed absent a complete kernel
  refutation; future claims must bind the added shadow clauses.
