# Lane F state

Round 19 complete. **No candidate, no running/stopped jobs.** Pilot only on exactly-one-double footprints; no new order-40 scores (best 24 at e=178 and 179; `round19_nearness.tsv`). Round 18 state archived in `LOG.md`.

| Label | Result and evidence | Core-h |
|---|---|---:|
| hand + enum (pending) | 102/128 pilot one-double footprints excluded in the one-exceptional-site construction (203 labels; 1 reversal fix). Marked subset 13 cuts/32 sampled; 26 open pilot rows. Independent replay of 2,050 deductions and clean match. `ROUND19.md`, `scratch/F/r19/{newcalib,pilotcheck,newtamper,mutation,clean}.stdout`, `pilot.checked`, `ROUND19_FREEZE.sha256`. | below |
| hand + enum (price only) | Actual unsigned joint headers 16,182,483 → 15,613,661 (−568,822), counting simultaneous reversal, not graphs. 4,309 exterior and 1,314 marked reps left across all strata. `scratch/F/r19/{detailprice.stdout,joint.tsv}`. | 0.00364 total |
| estimate | All 3,709 one-double reps ~11 CPU-s for one production+check+price, ~27 s with controls/clean rebuild and replay. No estimated cuts. `scratch/F/r19/{forecast.txt,cost.stdout,pilotrun.time,pilotcheck.time}`. | not spent |

**Next:** Critic: authorize one worker, ≤0.04 core-h, ≤512 MiB to run `scratch/F/r19/unexamined.rows` (3,581, no pilot repeats), same bank and checker. Combine only actual checked cuts with the 128 frozen pilot receipts, independently price and replay. Do not pursue the other 26 pilot rows, the 264 no-double leftovers, any signings, or reopen ID8/21. This is not a general degree/symmetry exclusion. H: review the 102 physical cuts and the price as separate scoped claims.

**Jobs:** inherited none. All 33 single-worker foreground invocations exited zero; no failures/timeouts, detached or stopped jobs. Exact commands and clocks in `scratch/F/r19/jobs.tsv`; each log below is `<name>.stdout` there. All times on 2026-11-22, host +01:00; full date/offset in TSV. No PIDs to kill or resume.

| Supervisor PID | Command (full argv in jobs.tsv) | Log name | Cores | Start | Deadline |
|---:|---|---|---:|---|---|
| 1129999 | `g++ -O3 -std=c++20 -march=native ../../../ralph/lanes/F/one_double.cpp -o binary` | `build` | 1 | 16:05:06 | 16:05:36 |
| 1130900 | `../../../opt/venv/bin/python -B ../../../ralph/lanes/F/one_double_pilot.py small` | `ctlprep` | 1 | 16:05:08 | 16:05:28 |
| 1130947 | `./binary c3_0.q 4 c3_0.bank c3_0.rows c3_0.trace 8` | `runc3_0` | 1 | 16:05:08 | 16:05:24 |
| 1130990 | `./binary c3_1.q 4 c3_1.bank c3_1.rows c3_1.trace 8` | `runc3_1` | 1 | 16:05:08 | 16:05:24 |
| 1131028 | `./binary c3_2.q 4 c3_2.bank c3_2.rows c3_2.trace 8` | `runc3_2` | 1 | 16:05:09 | 16:05:25 |
| 1131064 | `./binary c3_3.q 4 c3_3.bank c3_3.rows c3_3.trace 8` | `runc3_3` | 1 | 16:05:09 | 16:05:25 |
| 1131097 | `./binary c3_4.q 4 c3_4.bank c3_4.rows c3_4.trace 8` | `runc3_4` | 1 | 16:05:09 | 16:05:25 |
| 1131119 | `./binary c3_5.q 4 c3_5.bank c3_5.rows c3_5.trace 8` | `runc3_5` | 1 | 16:05:09 | 16:05:25 |
| 1131147 | `./binary c3_6.q 4 c3_6.bank c3_6.rows c3_6.trace 8` | `runc3_6` | 1 | 16:05:09 | 16:05:25 |
| 1131171 | `./binary c3_7.q 4 c3_7.bank c3_7.rows c3_7.trace 8` | `runc3_7` | 1 | 16:05:09 | 16:05:25 |
| 1131209 | `./binary c4_45.q 4 c4_45.bank c4_45.rows c4_45.trace 8` | `runc4_45` | 1 | 16:05:09 | 16:05:25 |
| 1131239 | `../../../opt/venv/bin/python -B ../../../ralph/lanes/F/one_double_pilot.py calibrate` | `calib` | 1 | 16:05:09 | 16:05:54 |
| 1132724 | `../../../opt/venv/bin/python -B ../../../ralph/lanes/F/one_double_pilot.py tamper` | `tamper` | 1 | 16:05:11 | 16:05:31 |
| 1138228 | `g++ -O3 -std=c++20 -march=native ../../../ralph/lanes/F/one_double.cpp -o binary` | `rebuild` | 1 | 16:05:28 | 16:05:58 |
| 1139464 | `./binary c3_0.q 4 c3_0.bank c3_0.rows c3_0.trace 8` | `newc3_0` | 1 | 16:05:31 | 16:05:47 |
| 1139473 | `./binary c3_1.q 4 c3_1.bank c3_1.rows c3_1.trace 8` | `newc3_1` | 1 | 16:05:31 | 16:05:47 |
| 1139482 | `./binary c3_2.q 4 c3_2.bank c3_2.rows c3_2.trace 8` | `newc3_2` | 1 | 16:05:31 | 16:05:47 |
| 1139491 | `./binary c3_3.q 4 c3_3.bank c3_3.rows c3_3.trace 8` | `newc3_3` | 1 | 16:05:31 | 16:05:47 |
| 1139507 | `./binary c3_4.q 4 c3_4.bank c3_4.rows c3_4.trace 8` | `newc3_4` | 1 | 16:05:31 | 16:05:47 |
| 1139518 | `./binary c3_5.q 4 c3_5.bank c3_5.rows c3_5.trace 8` | `newc3_5` | 1 | 16:05:31 | 16:05:47 |
| 1139527 | `./binary c3_6.q 4 c3_6.bank c3_6.rows c3_6.trace 8` | `newc3_6` | 1 | 16:05:31 | 16:05:47 |
| 1139536 | `./binary c3_7.q 4 c3_7.bank c3_7.rows c3_7.trace 8` | `newc3_7` | 1 | 16:05:31 | 16:05:47 |
| 1139546 | `./binary c4_45.q 4 c4_45.bank c4_45.rows c4_45.trace 8` | `newc4_45` | 1 | 16:05:31 | 16:05:47 |
| 1139558 | `../../../opt/venv/bin/python -B ../../../ralph/lanes/F/one_double_pilot.py calibrate` | `newcalib` | 1 | 16:05:31 | 16:06:16 |
| 1139963 | `../../../opt/venv/bin/python -B ../../../ralph/lanes/F/one_double_pilot.py tamper` | `newtamper` | 1 | 16:05:32 | 16:05:52 |
| 1140009 | `../../../opt/venv/bin/python -B ../../../ralph/lanes/F/one_double_pilot.py pilot` | `freeze` | 1 | 16:05:32 | 16:05:52 |
| 1147766 | `./binary pilot.q 10 pilot.bank pilot.rows pilot.trace 8` | `pilotrun` | 1 | 16:05:48 | 16:06:23 |
| 1147786 | `../../../opt/venv/bin/python -B ../../../ralph/lanes/F/one_double_check.py pilot` | `pilotcheck` | 1 | 16:05:48 | 16:06:23 |
| 1147801 | `../../../opt/venv/bin/python -B ../../../ralph/lanes/F/one_double_pilot.py price` | `price` | 1 | 16:05:48 | 16:06:10 |
| 1168273 | `../../../opt/venv/bin/python -B ../../../ralph/lanes/F/one_double_pilot.py price` | `detailprice` | 1 | 16:06:37 | 16:06:59 |
| 1168357 | `../../../opt/venv/bin/python -B ../../../ralph/lanes/F/one_double_pilot.py estimate` | `cost` | 1 | 16:06:37 | 16:06:55 |
| 1168392 | `../../../opt/venv/bin/python -B ../../../ralph/lanes/F/one_double_pilot.py adverse` | `mutation` | 1 | 16:06:37 | 16:06:55 |
| 1168415 | `bash -c cd ../r19clean && bash ../../../ralph/lanes/F/round19_replay.sh` | `clean` | 1 | 16:06:37 | 16:07:17 |
