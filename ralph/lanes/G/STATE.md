# Lane G state — round 22, November 22, 2026

**238 near-regular MTF distributions plus R remain open.** No candidate,
whole-distribution, `t9`, U88, or residue-floor change. For the marked
`e=170` adjacent degree-six slice, `h=8` and `h=7` were accepted, and
all **49/49 `h=6` weak boards and 19,651/19,651 weak hole-context keys**
are now excluded by checked local proofs (pending critic). `h≤5`, the
single degree-six slice and the parent distributions are not closed.

## Jobs

| PID (timeout / worker) | Command | Log | Cores | Start | Expected end |
|---|---|---|---:|---|---|
| 2223755 / 2223757 | Finished `round22_three_worker.sh pilot 0 p0 full` | `scratch/G/round22/h5/pilot0.log` | 0 | 19:41 | checked |
| 2223925 / 2223927 | Finished `round22_three_worker.sh pilot 110 p110 full` | `scratch/G/round22/h5/pilot110.log` | 0 | 19:41 | checked |
| 2224117 / 2224125 | Finished `round22_three_worker.sh pilot 285 p285 full` | `scratch/G/round22/h5/pilot285.log` | 0 | 19:41 | CPU cap, open |
| 2331361 / 2331384 | `round22_three_worker.sh shard 0 queue1.tsv` | `scratch/G/round22/h5/queue1.0.log` | 1 | 19:43 | ≤00:43 Nov 23 |
| 2331571 / 2331574 | `round22_three_worker.sh shard 1 queue1.tsv` | `scratch/G/round22/h5/queue1.1.log` | 1 | 19:43 | ≤00:43 |
| 2331867 / 2331871 | `round22_three_worker.sh shard 2 queue1.tsv` | `scratch/G/round22/h5/queue1.2.log` | 1 | 19:43 | ≤00:43 |
| 2331961 / 2331963 | `round22_three_worker.sh shard 3 queue1.tsv` | `scratch/G/round22/h5/queue1.3.log` | 1 | 19:43 | ≤00:43 |
| 2332113 / 2332115 | `round22_three_worker.sh shard 4 queue1.tsv` | `scratch/G/round22/h5/queue1.4.log` | 1 | 19:43 | ≤00:43 |
| 2332287 / 2332297 | `round22_three_worker.sh shard 5 queue1.tsv` | `scratch/G/round22/h5/queue1.5.log` | 1 | 19:43 | ≤00:43 |
| 2332399 / 2332406 | `round22_three_worker.sh shard 6 queue1.tsv` | `scratch/G/round22/h5/queue1.6.log` | 1 | 19:43 | ≤00:43 |
| 2332980 / 2332988 | `round22_three_worker.sh shard 7 queue1.tsv` | `scratch/G/round22/h5/queue1.7.log` | 1 | 19:43 | ≤00:43 |
| 2333547 / 2333554 | `round22_three_worker.sh shard 8 queue1.tsv` | `scratch/G/round22/h5/queue1.8.log` | 1 | 19:43 | ≤00:43 |
| 2333988 / 2334009 | `round22_three_worker.sh shard 9 queue1.tsv` | `scratch/G/round22/h5/queue1.9.log` | 1 | 19:43 | ≤00:43 |
| 2334355 / 2334380 | `round22_three_worker.sh shard 10 queue1.tsv` | `scratch/G/round22/h5/queue1.10.log` | 1 | 19:43 | ≤00:43 |
| 2334645 / 2334655 | `round22_three_worker.sh shard 11 queue1.tsv` | `scratch/G/round22/h5/queue1.11.log` | 1 | 19:43 | ≤00:43 |
| 2334778 / 2334813 | `round22_three_worker.sh shard 12 queue1.tsv` | `scratch/G/round22/h5/queue1.12.log` | 1 | 19:43 | ≤00:43 |
| 2335058 / 2335063 | `round22_three_worker.sh shard 13 queue1.tsv` | `scratch/G/round22/h5/queue1.13.log` | 1 | 19:43 | ≤00:43 |
| 2335162 / 2335176 | `round22_three_worker.sh shard 14 queue1.tsv` | `scratch/G/round22/h5/queue1.14.log` | 1 | 19:43 | ≤00:43 |
| 2335319 / 2335327 | `round22_three_worker.sh shard 15 queue1.tsv` | `scratch/G/round22/h5/queue1.15.log` | 1 | 19:43 | ≤00:43 |
| 2335613 / 2335639 | `round22_three_worker.sh shard 16 queue1.tsv` | `scratch/G/round22/h5/queue1.16.log` | 1 | 19:43 | ≤00:43 |
| 2336155 / 2336175 | `round22_three_worker.sh shard 17 queue1.tsv` | `scratch/G/round22/h5/queue1.17.log` | 1 | 19:43 | ≤00:43 |
| 2336763 / 2336796 | `round22_three_worker.sh shard 18 queue1.tsv` | `scratch/G/round22/h5/queue1.18.log` | 1 | 19:43 | ≤00:43 |
| 2337243 / 2337269 | `round22_three_worker.sh shard 19 queue1.tsv` | `scratch/G/round22/h5/queue1.19.log` | 1 | 19:43 | ≤00:43 |
| 2640301 / 2640387 | Finished `round22_depth_pilot.sh 52` | `scratch/G/round22/h5/depth52.log` | 0 | 19:51 | wall timeout |

`h=6` pilots, 20-worker full dispatch and four split jobs are finished;
PIDs and start times in `scratch/G/round22/queue{1,2,3}.pids`. `h=5`
workers have a 5 h outer limit, per solve 900 CPU-s / 1,800 wall-s,
320 MiB raw and 5 GiB VM. Evidence: `scratch/G/round22/h5/{launch.sha256,queue1.pids,queue1.tsv,work/}`.
At the 19:53 snapshot, **14** queue supervisors were still live, one
core apiece: `2331361,2331571,2331867,2331961,2332980,2333988,2334645,2334778,2335058,2335162,2335319,2335613,2336763,2337243`.
All other PIDs in the table are historical at this snapshot; do not
kill or reuse them without checking actual `ps`. See `handoff.pids`.

## Results and claims

| Label | Result | Evidence | Core-h |
|---|---|---|---:|
| hand + enum + local cert (pending critic) | Full marked `h=6`: 47 unpinned whole boards + exact complementary splits of boards 45 and 46. 51 dual-checked LRATs; all 49 sets of physical padded/MTF rows audited separately. Exact 22,408 labelled boards and 19,651 hole keys corroborated by A. Whole attempts on boards 45/46 at 320 MiB failed both checkers, even with solver exit 20, and were not credited. | `ROUND22_REPLAY.md`, `ROUND22_FREEZE.sha256`, `rows/e170_folded_two_defect.md`, `scratch/G/round22/{receipts.json,split-checked.log}` | ~0.78 |
| enum (calibration) | `h=5` successor has 286 boards / 184,488 labelled boards / 156,112 weak hole keys, matching the earlier Burnside count. Width-three `n=17`, 80 boards, strict alpha≤5 gives zero, matching the published catalogue control; relaxed alpha≤6 exact comparison gives 1,960 labelled placements and 218 classes on 16 nonempty boards. 936 board/class incidences. Hall cuts included in both modes. | `round22_three.py`, `round22_three_inventory.py`, `scratch/G/round22/h5/{manifest.json,control.log,reference.log}` | ~0.008 + pilots |
| local cert + open (19:53 snapshot, pending critic) | `h=5`: 211/286 dual-checked boards, 117,224/156,112 weak keys. 75 boards open, including 38 SAT relaxations, 285 resource-capped and other pending attempts. The board-52 alternative hit a wall timeout. | `ROUND22_H5.md`, `scratch/G/round22/h5/{handoff.json,handoff.pids,work/}` | 1.64 finished attempt hours at snapshot; queue running |

## Handoff

- H/critic: verify exact `h=6` debit only. `receipts.json`/freeze names
  every formula and compressed proof, and `split-checked.log` binds the
  two unit pairs against the actual full CNFs. No fixed-alignment claim.
- `h=5` SAT models are relaxations, not candidates: all 37 decoded
  in the audit had an `I10`; two require ≥2 selected options, so full
  depth at option quota one is not sufficient in general. The board-52
  pilot added 284,910 depth clauses, blocked its prior model six ways,
  but returned no result in 95 wall-s (38.74 CPU-s). No new solver
  batch on this overlay. Prefer compact witnessed clauses, `e(W)=86`
  or auditable disjoint selector splits after collecting the queue.
  `scratch/G/round22/h5/{final-model.jsonl,deep-control.log,depth52.log}`.
- At e170, sixteen degree-six distribution keys remain (nine single,
  seven adjacent pair). `Z=48`, e(H)=122, 24 private and nine double
  sites; adjacent W has 28 sites, one crossing and 86 internal edges.
  Round-13 exact `t9` thresholds and membership remain in
  `ROUND13_REPLAY.md` and its freeze; 32/e108 remains lane B's.
