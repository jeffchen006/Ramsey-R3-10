# Lane F state

Round 15 complete. Allocation **2**; no live/stopped jobs, no candidate. **Pending critic review: ID21 itself excluded (hand + cert), not just the named missing vertical.** Only ID8 survives the accepted R14 two-profile list if confirmed. No unrestricted-case debit and no order-40 score run. Observed best still **24 independent tens at e178 and e179**. R14 state/jobs archived in `LOG.md`. Full result: `ROUND15.md`.

| Label | Round 15 result / evidence | Core-h |
|---|---|---:|
| enum | Physical smaller controls, including correct and adverse hole/endpoint roles, local parity projection and SAT/UNSAT CNF calibrations. `scratch/F/r15/{small,localctl,branchesctl,lratctl}.stdout`. | 0.000108 |
| hand + enum | Missing vertical on ID21 impossible: 45 double-at-zero supports, 128 local parity roles → 11; all 11 refuted by old singletons. Rank ≤3 alone left five. `scratch/F/r15/{hole.rows,local.chart,local.pass,verify.stdout,branch4.*.proof}`. | 0.001539 |
| hand + enum | Restoring the vertical: recheck the other 117 roles using singleton supports only; all 117 now have independent rank-zero terminals. Final 128-role roster has 126 rank-zero, two XOR contradictions. `scratch/F/r15/{restored4.*.proof,allverify.stdout}`. | 0.000728 |
| hand + cert | Independent finite CNF with only 297 ten-singleton masks. Every ID21 old card already has a physical independent ten (and its mate), any verticals. One dual-checked LRAT, byte-identical regeneration from frozen distances and masks. `scratch/F/r15/id21.{cnf,lrat,trace}`, `id21.{lrat-check,cake_lpr}.log`, `hole_lrat.py frozen`, `round15_id21_masks.txt`. | 0.000181 |

**Next if approved:** ID8 only, distances 6,7,8,9. Calibrate and price one hole and the local parity dimension before considering any partition; no global signing or target wave. Retired families remain retired. No extra core request. `round15_nearness.tsv` keeps bounds separate from observations.

**Jobs R15:** all 17 collected, exit 0, total **9.20 CPU-s / 0.00256 core-h**. Commands below ran from `scratch/F/r15`. No live or stopped job.

| Supervisor / worker PID | Command | Log | Cores | Start | Deadline |
|---|---|---|---:|---|---|
| 746891 / - | `python3 -B ../../../ralph/lanes/F/hole_price.py control ` (wall 40s, CPU 25s) | `scratch/F/r15/small.{stdout,time}` | 1 | 2026-11-22T10:27:42+01:00 | 2026-11-22T10:28:22+01:00 |
| 751363 / - | `python3 -B ../../../ralph/lanes/F/hole_price.py price ` (wall 40s, CPU 25s) | `scratch/F/r15/price.{stdout,time}` | 1 | 2026-11-22T10:27:54+01:00 | 2026-11-22T10:28:34+01:00 |
| 768209 / - | `python3 -B ../../../ralph/lanes/F/hole_joint.py 31 ` (wall 45s, CPU 30s) | `scratch/F/r15/jointpilot.{stdout,time}` | 1 | 2026-11-22T10:28:49+01:00 | 2026-11-22T10:29:34+01:00 |
| 777746 / 777751 | `python3 -B ../../../ralph/lanes/F/hole_joint.py 1 ` (wall 45s, CPU 30s) | `scratch/F/r15/jointfull.{stdout,time}` | 1 | 2026-11-22T10:29:11+01:00 | 2026-11-22T10:29:56+01:00 |
| 799577 / - | `python3 -B ../../../ralph/lanes/F/hole_local.py control ` (wall 40s, CPU 25s) | `scratch/F/r15/localctl.{stdout,time}` | 1 | 2026-11-22T10:30:08+01:00 | 2026-11-22T10:30:48+01:00 |
| 800033 / - | `python3 -B ../../../ralph/lanes/F/hole_local.py inspect ` (wall 40s, CPU 25s) | `scratch/F/r15/localprice.{stdout,time}` | 1 | 2026-11-22T10:30:09+01:00 | 2026-11-22T10:30:49+01:00 |
| 819833 / - | `python3 -B ../../../ralph/lanes/F/hole_branches.py small ` (wall 40s, CPU 25s) | `scratch/F/r15/branchesctl.{stdout,time}` | 1 | 2026-11-22T10:30:54+01:00 | 2026-11-22T10:31:34+01:00 |
| 820231 / 820235 | `python3 -B ../../../ralph/lanes/F/hole_branches.py 3 1 ` (wall 45s, CPU 25s) | `scratch/F/r15/rolepilot.{stdout,time}` | 1 | 2026-11-22T10:30:55+01:00 | 2026-11-22T10:31:40+01:00 |
| 824162 / 824175 | `python3 -B ../../../ralph/lanes/F/hole_branches.py 3 11 ` (wall 45s, CPU 25s) | `scratch/F/r15/roles.{stdout,time}` | 1 | 2026-11-22T10:31:07+01:00 | 2026-11-22T10:31:52+01:00 |
| 831308 / 831312 | `python3 -B ../../../ralph/lanes/F/hole_branches.py 4 11 ` (wall 60s, CPU 35s) | `scratch/F/r15/rolesfour.{stdout,time}` | 1 | 2026-11-22T10:31:20+01:00 | 2026-11-22T10:32:20+01:00 |
| 869644 / - | `python3 -B ../../../ralph/lanes/F/hole_verify.py ` (wall 75s, CPU 45s) | `scratch/F/r15/verify.{stdout,time}` | 1 | 2026-11-22T10:32:40+01:00 | 2026-11-22T10:33:55+01:00 |
| 897602 / 897607 | `python3 -B ../../../ralph/lanes/F/hole_branches.py restored 4 6 ` (wall 45s, CPU 25s) | `scratch/F/r15/restoredpilot.{stdout,time}` | 1 | 2026-11-22T10:33:09+01:00 | 2026-11-22T10:33:54+01:00 |
| 904884 / 904888 | `python3 -B ../../../ralph/lanes/F/hole_branches.py restored 4 117 ` (wall 80s, CPU 45s) | `scratch/F/r15/restoreall.{stdout,time}` | 1 | 2026-11-22T10:33:23+01:00 | 2026-11-22T10:34:43+01:00 |
| 941760 / - | `python3 -B ../../../ralph/lanes/F/hole_verify.py ` (wall 75s, CPU 45s) | `scratch/F/r15/allverify.{stdout,time}` | 1 | 2026-11-22T10:34:07+01:00 | 2026-11-22T10:35:22+01:00 |
| 1020076 / - | `../../../opt/venv/bin/python -B ../../../ralph/lanes/F/hole_lrat.py control ` (wall 90s, CPU 50s) | `scratch/F/r15/lratctl.{stdout,time}` | 1 | 2026-11-22T10:35:29+01:00 | 2026-11-22T10:36:59+01:00 |
| 1028532 / - | `../../../opt/venv/bin/python -B ../../../ralph/lanes/F/hole_lrat.py batch ` (wall 130s, CPU 100s) | `scratch/F/r15/id21cert.{stdout,time}` | 1 | 2026-11-22T10:35:37+01:00 | 2026-11-22T10:37:47+01:00 |
| 1080985 / - | `../../../opt/venv/bin/python -B ../../../ralph/lanes/F/hole_lrat.py frozen ` (wall 90s, CPU 60s) | `scratch/F/r15/frozen.{stdout,time}` | 1 | 2026-11-22T10:36:30+01:00 | 2026-11-22T10:38:00+01:00 |
