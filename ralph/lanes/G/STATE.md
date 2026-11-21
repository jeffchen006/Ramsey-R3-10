# Lane G state — round 5, 2026-11-21

## Current baseline and scope

**283 near-regular distributions + R** remain against the critic's
round-4 baseline (368+R), if the round-5 cover is accepted. No order-40
candidate. **10** of these are conditional U88 (two e169 overlaps with
the new direct cuts). Lane B's pending global degree-seven floor 108
would cut five more (including its separate e162 result; do not double
count), yielding **278+R** and 10 refreshed U88 keys. Neither its proof
nor either gluing floor is needed for the main 85 cuts.

The six order-33 e120/e121 keys are still missing. None has degree five.
No global floor 121/122 for all degree-six MTF residues is claimed;
39 previous potential e168/floor121 cuts now reduce to 20 independent
remaining keys. The 11 prior e169-pinned proofs remain pinned.

## Round 5 results and claims

| Label | Result / claim | Evidence | CPU-h |
|---|---|---|---:|
| pub + enum | The full 477,142-key class `(3,8;27)` leaves 118 keys for a degree-five root in `(3,9;33)`. Two exact maximal-column filters agree byte-for-byte. Two exact extenders canonically agree on all 984 min-five classes, e123..130. | `rows/no_degree_five_residue.md`, `root_certs/{d5_order27_survivors,d5_order33}.g6`, `audit_d5_cover.py`, `scratch/G/round5/audit_d5_cover.log` | 1.29 filters, 0.02 gluing |
| cert conditional on enumerated cover | All 118 fixed-core extensions at cap122 dual-LRAT UNSAT. Exact non-MTF minimum degree-five lower bound 123 at order 33; five verified positive graphs attain it. | `d5_fixed.py`, `scratch/G/round5/d5/{cap122,full_e123.can.g6}`, cover audit log | est. 0.14–0.3 |
| enum | Both full exact outer degree-six maximal-column gluers reject all 984 residues. No parent edge, MTF, or distribution premise. The exact canonical source, shard partition, counts and logs all pass audit. | `maximal_prefilter.c`, `check_maximal_prefilter.cc`, `scratch/G/round5/{d6,audit_d5_cover.log}` | 0.056 |
| hand + exact Farkas, contingent on enum | In an MTF `(3,10;40)` graph, every degree-six vertex is adjacent to every other one, so `n6<=2`. The new global pair cap is `c(6,t)<=t-6`. 84 direct unit-Farkas cuts; e168 `(2,9,0,29)` also cut by odd `Z` vs `Z=48` (uses accepted floor120). Five improved t9 bounds. | `rows/no_degree_five_residue.md`, `d5_global_cuts.jsonl`, `scan_d5_cuts.py --verify`, `round5_cases.csv` | <0.06 |
| estimate/open | Order-32 d4 pilot leaves 237/520 cores at 3.233 CPU-s. It is not the tiny-survivor regime; require a tighter early edge cap or a different split before scaling. | `scratch/G/round5/d4.pilot.max.log` | <0.001 |
| conditional exact Farkas | Assuming Lane B's floor 108: five further cuts (two independent of gluing floors, three with them) and 39 tightened threshold keys. Four removals and four additions among candidate U88 keys; still ten. | `floor108_overlap.jsonl`, `scratch/G/round5/floor108_summary.log` | 0.025 |

Calibration: all 178 degree-five order-22 graphs recovered from 2,576
cores by both implementations, with all 70 exterior types from 944
actual roots. Both outer filters accept 220 regular order-22 roots.
The row analogue checks C13, C35, saturated Exoo39, all 191 saturated
order-22 graphs and a nonvacuous smaller adjacent-peer control. See
`scratch/G/round5/{d5.fullcontrol.binding.log,check_d5_rows.log}`.

## Jobs

No live G jobs. All listed detached wrappers finished; checked `ps`,
all terminal files and logs. Times CET; one core per listed PID. The
foreground eight-input *relaxed* core pilot included SAT and wall caps;
it is not used for any exclusion (`d5/high.pilot.log`).

| PIDs | Command (cwd `scratch/G/round5`) | Log | Start | Expected then / outcome |
|---|---|---|---|---|
| 3743061–3743068 | `timeout 1200s bash ../../../ralph/lanes/G/run_d5.sh ID` | `d5/worker.ID.log` | 21:22:12 | 21:32–38; all 32 done by 21:29:39 |
| 4025790, 4025791, 4025793, 4025797, 4025803, 4025809, 4025815, 4025822 | `timeout 1000s bash ../../../ralph/lanes/G/audit_d5_shard.sh ID` | `d5/audit.worker.ID.log` | 21:28:40 | 21:33–40; all 32 done 21:32–33 |
| 4097864, 4097888, 4097910, 4097924, 4097941, 4097958, 4097980, 4098003 | `timeout 1000s bash ../../../ralph/lanes/G/replay_d5_fixed.sh STEMS` | `d5/lrat.worker.ID.log` | 21:31:41 | 21:34–38; 118/118 checked with pilots by 21:33:29 |
| 4736, 4737, 4739, 4740, 4741, 4742, 4743, 4745 | `timeout 200s bash -c ... bash d6/full.ID` (`./maximal_prefilter 9 6 --witness`) | `d6/worker.ID.log`, `d6/full.ID.log` | 21:35:49 | 21:36–38; all 8 done by 21:36:19 |

## Handoff

- A/critic: independent review of the finite cover and bytes, entry point
  `rows/no_degree_five_residue.md`; Lane G already ran independent C++
  generation and `audit_d5_cover.py --lrat`. H: bind 85 exclusion keys,
  record exact status and consider formalizing the elementary hand bridge.
  B: U88 now 10 relative to G's baseline. If floor108 is accepted then
  replace the key set using `floor108_summary.log` (still 10).
- Next: after `n6<=2`, prioritize the 20 still-open e168 cases with a
  degree-six root. Only a cover of missing e120 graphs or a different
  direct obstruction can close them. Any remaining e120 graph is
  deletion-critical and has at most five distinct one-edge e121 children;
  do not assume it has children. No unchanged broad replacement sweep.
  Downstream possibility: exact order-32 d4 low-edge cover if the cut
  reduces the measured 46% survivor rate by orders of magnitude.
- Prior accepted floors: degree-six 120 (`rows/floor120.md`, complete 5+69
  classes, unpinned checked proofs); degree-seven 107 (`rows/floor7.md`).
  No assumptions about extension of general e120/e121 classes. Historical
  runs, mislabeled mixed levels and scope repairs are in `LOG.md` and
  `REPRO.md`. Frozen `round4_cases.csv` reproduces its accepted 368+R and
  all round-4 rows, including its independent signature/packing cuts.
