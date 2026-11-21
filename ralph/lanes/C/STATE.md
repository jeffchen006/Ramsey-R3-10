# Lane C — round 3, 2026-11-21

**Open:** R(3,10), Case R and R(6). No candidate graph. Critic accepted
R(7) as `cert` in round 1; custom trace, not Lean. In R(6), J is the
graph of codegree-six pairs. A P4 or P5 means a span of distinct
consecutive roots in J, not an induced subgraph of G.

## Results and claims for H / critic

| Label | Result | Evidence | CPU-h |
|---|---|---|---:|
| cert, accepted round 1 | R(7) excluded. Preserve exact custom trace scope. | `ralph/critic/round_001.md`, `ralph/lanes/A/R7_REPLAY.md` | — |
| enum, retained | No J eight-cycle in R(6). | `proofs/cycle8_join.md`, `ralph/lanes/H/C6_REVIEW.md` | — |
| enum, confirmed round 2 | No five consecutive distinct roots: 1,156 joined H30/e99 rows, 940 unsupported MTF pairs, 216 exhaustive trees (289,649 nodes); separate verifier checks every node. Round 3 A independently matched P5 exactly modulo reversal, with positive/negative controls. | `PATH_REPLAY.md`, `PATH_INPUTS.sha256`, `scratch/C/p5_trace_verify.log`, `ralph/lanes/A/P5_REPLAY.md` | 0.048 C + 0.003 A |
| hand | Necessary eager projections onto one boundary side: given independent I in A avoiding v0, the available L-vertices are bounded by 9−\|I\| and D0 available by 8−\|I\| using v2; symmetric other side. Degree/triangle/MTF/codegree projection and row/column cross pin reduction. | `proofs/path_four_factor.md`, `ralph/lanes/H/P4_SIDE_REVIEW.md` | — |
| cert, composite pending critic | **No P4 span in R(6)**: 2,454 independently matched A26 rows, 1,356 after the exact MTF filter; 1,187 unpinned CNFs plus 1,035 pinned CNFs cover all retained rows. Every LRAT checked twice, regenerated CNF hashes identical, independent filter/orbit index has no missing keys. Consequently J has only P1/P2/P3 components, ≤26 c6 pairs and ≤13 J-degree-two vertices; this does not close R(6). | `P4_REPLAY.md`, `P4_INPUTS.sha256`, `scratch/C/p4-index.log`, `scratch/C/p4replay-{0,1,2,3}.log` | 0.454 proof production + 0.264 replay |
| enum, matched control | P4 new eager factor matches all 13 C21 feasible/infeasible keys, independently validates 8 witnesses; cap-only baseline solved 0/15 matched large rows, new unpinned proof pilot solves 14/15, pinned solves all six lower-stratum pilots. Full sweeps exhausted. | `P4_REPLAY.md`, `scratch/C/p4_factor_independent_control.log`, `scratch/C/p4proof-pilot.log`, `scratch/C/p4pinned-pilot.log` | 0.018 proof pilots |
| hand | For three consecutive roots with diagonal codegree five, their order-22 residue has **e(X)≤64**. At equality the deleted graph is fixed up to relabelling (wing nonedges are K2,2, both private middle neighbours use that 2+2 set, other eligible wing attachments saturated). No reliance on the P4 result. | `proofs/path_three.md`, `P3_REPLAY.md` | — |
| enum, boundary only | Direct tiny audit: all 512 wing patterns, Hall plus independence constraints, zero e>64, exactly one orbit at e64; e63 has 13 boundary orbits before further filtering, not extension results. C21 verifies all 42 oriented triple partitions and complete attachment positive/negative controls. | `verify_p3_boundary.py`, `scratch/C/p3boundary-e63.log`, `scratch/C/p3_top_{control,independent_control}.log` | <0.001 |
| cert, composite pending critic | Diagonal-five P3/e64: all 59 census rows covered (3 pilot, 56 production, no misses or caps). Full replay matched all regenerated CNF/proof hashes and rechecked all LRATs. This leaves diagonal-five e(X)≤63, not a closure of diagonal five or R(6). | `P3_REPLAY.md`, `P3_INPUTS.sha256`, `scratch/C/p3e64-index.log`, `scratch/C/p3e64-index.tsv` | 0.584 production + 0.269 replay |

## Live jobs

None. P3 e64 replay wrappers 3160833, 3160842, 3160849, 3160857
ended by 19:32 CET, all `IDENTICAL`. Archived commands, timings and
PIDs for all completed jobs are in `LOG.md`.

Measured static pilot 3/3 refutations at 17.57–20.09 CPU-s each;
proof/check calibration 33.60–37.39 CPU-s each, ~70 MB per LRAT.
Prelaunch estimate: 56 remaining cases ×40 CPU-s ≈2240 CPU-s,
four cores ≈9–10 minutes idle or ≲20 minutes at 2× wall; about
4 GB proof disk. Completed P4 job and cost details moved to `LOG.md`.

Production finished all 56 remaining P3 e64 rows (1995.85 CPU-s),
no caps; producer index `scratch/C/p3e64-index.log` has all 59 input
keys. Three pilot CNFs replayed with identical hashes in 50.97 CPU-s.
Full hash-bound replay: 917.02 CPU-s for 56 proofs versus estimate
950 CPU-s; 967.98 CPU-s including the three pilot replays.

## Next

1. Ask H to review the P3 Hall bridge and the critic to accept both
   exclusions only after reduction, coverage and replay audits.
   Preserve initial and replay proof evidence.
2. For diagonal five at e63, first test the 13 fixed-boundary orbits
   from `p3boundary-e63.log` on the 60 e63 seeds, with a dispersed
   pilot (all 13 survive fixed-boundary alpha/codegree/biclique checks).
   Avoid scaling an untested
   780-row cross product. Keep diagonal five's lower strata distinct.
3. P3 diagonals 3 and 4 have different middle-attachment multiplicities;
   isolated c6 edges (P2) have no common 22-vertex triple seed at all.
   No claim about other R(M) or near-regular cases. Don't revive P4/P5
   scans or the capped lazy-cut P4 pilot.
