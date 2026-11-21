# Lane D — round 5, 2026-11-21

**Open:** R(3) remains open; 110 original minimum-root representatives
are unchanged. No graph candidate, no full Section 7 certification.
For the alternate maximum-root cover, 19 isolate keys are excluded
by hand and three cyclic keys by exact checked LP (`enum`): 13 forest
keys at max12 and 76 keys at max13..16 remain.
R(4)'s K3,4 remains open and was not run this round. Earlier details
are in `LOG.md`. Lane share two cores. No detached jobs started.

## Results and claims

| Label | Scope | Evidence | CPU-h |
|---|---|---|---:|
| hand | Maximum-square root yields disjoint classes by global maximum m=12..16; within a class the rooted kernels form a cover. For m=12 all edge square counts are 12, every nonedge codegree is at least two. | `MAX_ROOT.md` | — |
| enum | Independent genbg census agrees on 111 root-swap keys: 35/39/26/8/3 by m. All 16 C16 max-root keys exhaust, with both exact variants matching 13 labeled copies of all five known controls. | `scratch/D/max_root_genbg.log`, `scratch/D/max_root_sat16/check.log` | ~0.002 |
| hand | Projection rows for fixed edges, outside-star filter, and orbit-averaged joint degree/codegree/edge-square LP. | `MAX_ROOT.md`, `TRANSPORT.md` | — |
| enum | 111/111 first projection solved and regenerated; 19 m12 isolate kernels excluded by the hand floor, all 92 others feasible relaxations. | `scratch/D/max_root_matching.jsonl`, `scratch/D/max_root_matching_verify.log` | 0.038 |
| open | Exact SAT on 22 and 110: both fixed and eager hit 28 CPU-s; both refute isolate key 0 immediately. No extension or improvement on nontrivial keys. | `scratch/D/max_root_sat40/index.log`, `scratch/D/max_root_sat40/*.time` | 0.033 |
| enum | Star-fixed-point projections exclude max12 20 and 22. Negative Farkas coefficients need 24 and 31 first-round UNSAT orbit representatives respectively, all checked by CakeLRAT. Binding to the original graph problem remains hand, not Sec. 7 (a). | `scratch/D/outer_star_direct{20,22}.log` | 0.041, two production/replay runs |
| enum | Full outside-star fixed point and projection on all 16 no-isolate keys. Only 20/22 refute; 14 feasible, complete trace/cover replay. | `scratch/D/outer_star_batch/index.log`, `scratch/D/round5_manifest_recheck.log` | 0.407 production |
| enum | Unfiltered transport: checked exact Farkas for 19/20/22, including corrupted-proof rejection; 34 feasible, 12 internal LP limits. All three cyclic keys in the max12 class are excluded, conditional only on the maximum-root premises, not on any local SAT filter. | `scratch/D/transport40/{19,20,22}.sweep.json`, `scratch/D/transport40/replay.log`, `scratch/D/forest_cover.log` | 0.085 sweep |
| hand | Once cyclic max12 keys are excluded, every edge kernel in max12 is a forest. Rerooting gives 6-cycle blockers and rank rows. Exact 22-type count pin `6<=k<=14` fixes X's degree histogram and `C4(X)=2k-4-z`. | `TRANSPORT.md`, `MAX_ROOT.md`, `scratch/D/{forest_obstructions,signed_square_cal16}.log` | — |
| enum/open | Forest LP retains 33/34 with and without star filters. Filtered IPM at 21 feasible; integer-mask MILP at 34 hits its limit, no verdict. Nine-way split on 34 checks k=6 UNSAT with or without forest rows (exact Farkas); k=7..14 feasible relaxations. No further whole kernel excluded. | `scratch/D/transport40/{21.ipm,34.integer,34.split-6-noforest}.json`, `scratch/D/transport40/split-replay.log`, `scratch/D/round5_manifest_recheck.log` | 0.052 pilots |

## Jobs (all ended)

| Supervisor PID / session | Command from `scratch/D` | Log | Cores | Start CET | End / cap |
|---:|---|---|---:|---|---|
| 30557 / 17186 | `outer_star.py 40 9 ID --orbits --fixpoint --projection-log ...`, keys 24,26,27,28,29,30,31,32 | `scratch/D/outer_star_batch/index.log` and per-key logs | 1 | 21:36:37 | done ~21:53; per-key 320 CPU-s / 480 wall |
| 136533 / 27902 | `transport_root.py 40 9 ID --bounded-dual`, keys 19–34 | `scratch/D/transport40/index.log` and `*.sweep.{json,time}` | 1 | 21:40:18 | done ~21:45; per-key 70 CPU-s / 100 wall |
| 479273 / 93327 | `transport_root.py 40 9 34 --bounded-dual --forest --pin-22-count K ...`, K=6..14 | `scratch/D/transport40/split-index.log` | 1 | ~21:52 | done ~21:53; per-pin 22 CPU-s / 35 wall |

All bounded foreground jobs including manifest recheck are complete;
no live or stopped Lane D PID as of 21:54 CET. One small two-key C16
MILP smoke overlapped the two target slots briefly; do not repeat.
Frozen input/output hashes: `scratch/D/round5_evidence.sha256`.

## Next

- H/C/critic: audit the unfiltered transport group lift, integer
  Farkas rows and scope for 19/20/22, then the forest corollary.
  The unfiltered LP supersedes the SAT-dependent exclusion evidence
  on 20/22, so an OPB/CNF bridge is not the immediate bottleneck.
- Keep maximum-root IDs separate from the 110 original min-root
  reps. Higher maximum classes have only the first projection scan.
- A feasible transport point is not a graph. Do not launch a wide
  SAT or pin sweep from these results, and do not repeat R(4)'s weak
  single-group filter. For max12 survivors, compare joint transport
  with a bounded exact count split or supported-arc pruning.
