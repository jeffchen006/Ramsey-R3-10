# Lane E state — round 17 complete

2026-11-22 CET. Allocation ceiling 12; critic cap four simultaneous
workers for core 15 only. No other core search. No cover rescan.

## Jobs

None active, stopped, killed, or detached; zero cores. All 18 wrapper
PIDs collected: 17 exit zero and one fixed helper syntax error before
calibration. Exact logged PIDs, commands, logs, start, caps, expected
and actual ends: `scratch/E/r17_shared/{jobs,exits}.tsv`.

| Work | PIDs (bounded wrappers) | Slots | Start range / latest actual end CET |
|---|---|---:|---|
| Controls, comparison and exact queue audit | 746347, 748222, 748223, 753274, 756311, 773097, 778386, 778482, 779246 | 2 | 13:14:51–13:16:27 / 13:16:27 |
| 126 production routes | 790201, 790207, 790203, 790204 | 4 | 13:17:04 / 13:17:28 |
| Independent rebinds | 800714, 801931, 802084, 802093 | 4 | 13:17:26–13:17:28 / 13:17:39 |
| Final exact union check | 815245 | 1 | 13:18:02 / 13:18:03 |

## Results for H / critic

Scope: core 15 (`GCQf?{`) only, `(p,f,t)=(2,32,4)`, `δ(W)≥2`,
`e(W)=11`, mixed `(10,10,11,11)`, universal `δ(G)≥5`, E-021 all-graph
sole-missing `e=74` premise, all four omission roles and `K=6,7,8`.
Not MTF-only.

| Item | Label | Evidence and cost |
|---|---|---|
| Conditional core 15 exclusion, pending critic. Round-16 exact ordered cover (34 branches, 94,738 projections, 716,045 lifts) and unchanged ordered receipt bind the queue. All **142/142 distinct exact IDs** (16+32+32+31+31) have freshly rebound width-three CakeLRATs; no wide fallback. | hand + enum + cert (conditional) | `shared74_round17.md`, `scratch/E/r17_shared/{freeze.15.sha256,checked.15.tsv,final.audit.log}`, `scratch/E/r16_shared/freeze.15.sha256`. 182.49 CPU-s this round, 531.58 (0.14766 core-h) across both; ~254 MB retained. |
| Matched 16 including both queue extremes: narrow 17.44 CPU-s vs wide 27.99 with fresh binds/checks, 40,624 vs 177,156 KiB peak. Six-site positive, negative, wrong branch and wrong replay ID controls pass. | enum + cert (pilot) + estimate | `shared74_round17.md`; `scratch/E/r17_shared/{controls.log,compare.audit.log,compare.narrow.log,compare.wide.log,compare.narrow.rebind.log,compare.wide.rebind.log}`; 47.44 CPU-s including all comparison controls. Savings are for this sample only. |

## Handoff

- Ask the critic to verify the core-15 freeze and fresh proof replays.
  Four mixed cores **1, 6, 9, 18** remain if core 15 is accepted;
  request authorization to price one remaining core, not a batch.
- `core15_queue74.py` independently extracts opens from the immutable
  merged receipt, binds exact original rows and branch boundaries, and
  checks disjoint route rosters. The round-17 report has replay commands.
- `(5,5)` was already certified. No candidate, full `(2,32)` closure,
  rigidity theorem, or Ramsey verdict.
