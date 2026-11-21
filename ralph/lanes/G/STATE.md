# Lane G state — round 7, November 22, 2026

**278 near-regular distributions + R remain open.** No order-40 candidate.
The exact baseline (`round6_baseline.csv`), ten U88 keys (`round6_u88.csv`),
and twenty e168 d6 keys (`round6_e168_d6.csv`) do not change. The six
missing e120/e121 classes and eleven single-root zero-addition cases remain.

## Jobs

| PID | Command and cwd | Log | Cores | Start | Expected end |
|---|---|---|---:|---|---|
| 360479 (master `timeout`), 360484 (shell) | `bash ../../../ralph/lanes/G/run_low25.sh`, `scratch/G/round7` | `scratch/G/round7/proof-low25.master.log`; numbered `.log`/`.time` per shard | 16 | Nov 22 00:04:11 CET | early estimate 00:28; current rate may reach the worker wall cap 00:44:11 before completion (master cap 00:45:51) |
| 710384 (master `timeout`); 710569, 710560 (Python workers) | `bash ../../../ralph/lanes/G/run_mixed_strip.sh`, `scratch/G/round7` | `scratch/G/round7/proof-mixed.master.log`; `proof-mixed.{0,1}.{log,time}` | 2 | Nov 22 00:12:22 CET | roughly Nov 22 00:40–01:10 CET (worker cap 01:32:22; master 01:34:02) |

Actual Python worker PIDs in shard order: 360519, 360530, 360520, 360538,
360548, 360542, 360545, 360532, 360541, 360535, 360524, 360540, 360546,
360526, 360543, 360544. Time wrappers are listed in
`scratch/G/round7/proof-low25.worker.pids`. Each worker runs one child
solver/checker at a time, in `scratch/G/round7`; always check `ps` before
acting on a PID. Estimate from a 42/42 proof pilot, 36.93 CPU-seconds:
4.19 CPU-h for the 17,152 remaining cases (actual throughput so far
below the pilot estimate). The mixed batch estimates 0.41 CPU-h
from 24/24 dual proofs in 6.89 CPU-s; no other detached G job.
At 00:14 CET the two production batches had 3,323 and 81 checked
proofs respectively and no nonterminal receipts. This excludes the
42 and 24 pilot proofs respectively; neither total shows coverage.
See `scratch/G/round7/handoff.snapshot.log`.

## Results and claims

| Label | Result | Evidence | CPU-h |
|---|---|---|---:|
| hand + enum | Path/leaf with both centres (`j` = codegree) yields an order `24+j` marked `(3,8)` window. Single-centre window is order 26, four independent degree-7 marks; none in complete 62 e73 (window floor 74 only). Smaller paired/single scans match 21/44 marks, including both positive and negative controls. | `rows/path_leaf_windows.md`, `strip_window.cc`, `scratch/G/round7/{single26e73,control,pair27}.log` | 0.007 |
| cert + enum cover | Both path/leaf, `j=3`, at `(2,8,2,28)` and `(2,7,4,27)` (e168): 477,142 complete input classes → 1,988 marked windows on 1,980 classes → 1,988 checked LRATs, none capped. A's different traversal matches the cover and A independently replayed all proofs and pinned edge maps. No α clauses needed. | `scratch/G/round7/c3.certificates.tsv`, `ralph/lanes/A/PAIRED_WINDOWS.md`, `scratch/A/path7/replay.{0,1}.log` | 0.218 producer (+0.160 A) |
| cert pending cover audit | Both path/leaf, `j=2` and `δ(T)=3` only: 191 order-22 cores → 2,712,471 labelled outputs → 2,111 marks (A's 7-set scanner agrees) → 1,767 marked representatives. 1,735 base LRATs and 32 eager LRATs passed both checkers. A: audit small-core generation/dedup; H: audit eager semantics. | `scratch/G/round7/c2.delta3.certificates.tsv`, `ROUND7_REPLAY.md` | 0.570 proof, 0.031 glue+scan, 0.020 mark replay |
| enum + open | Both path/leaf, `j=1` and `δ(T)=2` only: same 191 cores → 18,333,381 labelled outputs → 20,181 marks → 17,194 marked representatives. All 42 capped-budget eager pilot keys have LRAT; full pending batch running. | `scratch/G/round7/{lowdegree25.canon.keys,lowdegree25.proof.estimate,proof-low25.worker.pids}` | 0.095 glue+scan, 0.010 pilot |
| hand + enum / open | Mixed path/leaf plus matching/incident or path/middle, only pin `(2,7,4,27)`: choose a noncross degree-eight pivot on the second side. Maximum pivot codegree 4 gives an order-27 window in the same 1,988 marked source, with a missing double pair on the second side. Exact roles split to 3,688 matching and 1,491 middle keys. 24 dual-checked pilot keys; full batch running. | `rows/path_leaf_windows.md`, `scratch/G/round7/{mixed-j4.cover.log,mixed-j4.keys,proof-mixed-pilot.*.log}` | 0.004 cover+pilot |
| estimate | Matched 12 formerly capped `j=2` keys: cut budget alone gave 2 certs / 10 caps (64.55 CPU-s); overlay + budget gave 5 / 7 (~208 CPU-s); eager I10 windows + budget yielded 12 / 0 (7.25 CPU-s). Do not scale overlay approach. | `scratch/G/round7/proof-low26-{budget,overlay,eager}-pilot.*.{log,time}` | 0.078 |

## Handoff

- Full paired centre `j=3` is excluded for both low-`n8` profiles. This
  does **not** exclude either distribution: `j=1,2` beyond minimum-degree
  slices and mixed roles at `(2,7,4,27)` remain open.
- Do not assume the source for `δ(T)=2` or `δ(T)=3` covers larger minimum
  degree. Extending the exact source without enumerating the general
  order-25/26 classes is the next structural target. No gluing floor 121
  or 122 for all d6 residues, no change to the e169-pinned scope.
- `rows/path_leaf_windows.md` describes the reduction, independent source
  and clause semantics. `ROUND7_REPLAY.md` gives source/checker commands.
  `proof-low25` uses `--eager 10000 --cut-budget`; `proof-sample`,
  `proof-full`, `proof-low26-pilot`, `proof-low26` use no extras.
  The other two `j=2` certificate directories use the same options
  as `proof-low25`. Never count experimental alternate proofs twice.
- Before announcing a `j=1` slice closure, check every shard timestamp,
  exact key union, nonterminal keys and compressed proof index. Do not
  treat a wrapper timeout or CAP as UNSAT. The next round may start
  while the master is still live.
- Mixed `j=4` cert replay flags are `--mixed --eager 10000`, not
  `--cut-budget`. It only excludes a mixed graph **if there exists**
  a noncross degree-eight pivot with codegree 4. No scope for smaller
  mixed codegrees. Check all 5,179 keys before any closure claim.
- Earlier results, the 14 templates / 112 pins, exact three-anchor
  budgets and all 20 d6 and ten U88 keys are unchanged; see `LOG.md`.
