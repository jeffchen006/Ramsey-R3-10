# Lane E state — round 6

2026-11-21; share 17 cores. All symmetry claims start with all graphs,
not MTF. No candidate graph; no claim on the Ramsey verdict. Round 5
is archived in `LOG.md`. Main scope: `(p,f,t)=(2,32,4), δ(W)≥2`.

## Jobs

Round-6 working directory `scratch/E/r6_e11`. All jobs collected;
no live lane-E solver or checker. Detached production history:

| Wrapper PIDs | Command | Start and expected end | Cores and logs |
|---|---|---|---|
| `2053353`–`2053368` | `batch_a11.py solve plan.a11.tsv --output proof.a11 --offset OFFSET --stride 16`, `nice -n 5`, wall 1380 s, CPU 1080 s, RAM 16 GiB | 22:51:33; all terminal at 23:04:28; cap would be 23:14:33 | 16; `proof.a11/{pids.tsv,worker.OFFSET.log,bind.OFFSET.jsonl}` |

Other jobs are collected. Four foreground pair-lift wrappers `1353334`–
`1353337` finished, zero extra catalogue classes. Mixed core censuses
`1764448`, `1764449`, `1764451`: exact support generation completed all
three; proof scan finished for core 0, CPU-killed after a *partial*
scan for each of 9 and 18. Do not treat those partial traces as covers.
Six foreground core-0 LRAT wrappers `1819545`–`1819550` finished;
389/389 checked. Independent core-0 replay finished at 22:54.
Final profile-A rescue and freeze finished at 23:04:59.

## Results / claims for H and critic

| Claim | Label | Evidence | Core-hours |
|---|---|---|---:|
| `(2,32,t=4,δ(W)≥2,e(W)=11,W=G?Beto)` excluded for both incidence profiles; 9,012 projection witnesses and 39,503 lifted witnesses replay; 389 distinct remaining primary windows checked and replayed. No expansion to other cores in `(10,10,11,11)`. | cert, pending independent scope review | `ralph/lanes/E/m11.md`; `scratch/E/r6_e11/{core0.replay.log,core0.certificates.sha256}` | ~0.07 including replay |
| All four windows have 74 edges whenever `e(W)≥9` under accepted saturation premises. At `e(W)=8,P=2`, the profiles are `b=(10,10,14,14)` and group deficits `(1,1,0,0)`; the two size-74 windows have at least six degree-seven vertices. | hand deduction conditional on enum saturation, not closure | `ralph/lanes/E/m11.md` | — |
| 1,624/1,625 known 74-edge classes (GR13), none with >4 degree-seven vertices. Any `m=11` solution would have ≥2 windows isomorphic to the same missing class; for `(10,10,11,11)` all four must be so. The 74-edge maximum degree-seven **multiplicity** is not settled. | enum-assisted necessary condition, not closure | `scratch/E/r6_e11/{addswap2.g6,catalogue_second.log,twoswap_full.log}`, `ralph/lanes/E/m11.md` | ~0.075, exploration |
| Full `(2,32,t=4,δ(W)≥2,e(W)=11,b=(10,10,10,12))` excluded: 19 core keys, 180,325 projections, 128,474 verified/replayed graph witnesses, 51,845 native CakeLRAT checks, and six primary SAT windows resolved by 144 exact omitted-group supports (101 witnesses + 43 independently replayed LRATs). No caps/missing. Overlaps core 0, not a closure of the other profile. | cert, pending independent scope review | `scratch/E/r6_e11/{graph.a11.replay.log,profile_a11.final.log,profile_a11.certificates.sha256}`, `ralph/lanes/E/m11.md` | 2.9089 primary + 0.0068 rescue/replay |
| Inherited f28 frozen mixed-status; e12 saturated branch frozen with 7,962 LRATs. Prior `(5,5)` is cert. No reruns. | previous statuses | `f28_cover.md`, `cubic32.md`, `slim5.md` | — |

## Next steps

- H/critic: audit the now frozen profile-A and core-0 boundaries
  from `m11.md`. Full profile A includes exactly the shape
  `(10,10,10,12)`. Don't rerun this batch unless a binding fails;
  `freeze_a11.py freeze --with-rescue` writes indexes, so use a
  scratch copy for any independent freeze replay.
- Remaining main m11 target is profile `(10,10,11,11)` except core
  `G?Beto`. Directly running the broad pinned SAT set is too large:
  core 9 alone has 192,113 feasible-after-domination projections and
  1,909,123 lifts. Do primary propagation before materializing exact
  omitted supports, and bind a small number of additional entire cores.
  Two-retained-group alpha screen finds only 11 witnesses on 6,114
  feasible pairs; depth-three two-literal branch finds only 2 new proofs
  on 389 residual projections. Do not scale either as the main route.
- The reverse 74-edge catalogue remains one short. All 1,624 roots
  were reattached at one/two vertices or two changed edges without
  recovering it. Don't repeat those moves unchanged. The last class,
  if it has ≤4 degree-seven vertices, additionally eliminates m9, m10,
  and deficit-two m8. If m8 has zero deficit, all W are 2-regular;
  `W=C8` or `2C4`. No conclusion for W leaves/isolates or `t=2,3`.
