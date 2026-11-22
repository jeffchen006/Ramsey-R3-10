# Lane F state

Round 17 complete. **2-core ceiling; zero running or stopped jobs; no candidate.** R16 accepted and retired: F-032 seven-window bridge, F-030 ID8 to 37, F-031 cyclic four-deletion consequence. New task was a **price**, not joint production. Score unchanged: 24 independent tens at e178/e179; `round17_nearness.tsv`.

| Label | Result, scope, evidence | Core-h |
|---|---|---:|
| hand + cert | An interval of 14 untouched sites (28 vertices) of the marked ID8-derived core necessarily has an independent nine, even with arbitrary signs and verticals under triangle-freeness. Two triangles, three squares, three supports. 48-variable/76-clause CNF, 774-byte dual-checked LRAT. `ROUND17.md`, `scratch/F/r17/{local9.txt,marked9.cnf,marked9.lrat,cert2.stdout}`. | 0.00016 incl. controls, failed limit setup and extraction |
| hand + enum | Independent labelled and marked-symmetry rosters, exact for the specified relaxation. The 17 untouched sites have only the identity and reversal. Before prism price 13,084 exceptional rows (includes the unchanged one), 17,474 external columns. Three-face reusable cuts eliminate 5,831 of those exterior columns. `scratch/F/r17/{geometry,replay,prismfull}.stdout`, `prism.rejects`. | included below |
| hand + enum (pilot) | 96/105 row-independent first-pole contradictions, nine open; 48 deductions beyond the shared prism cuts. No sign enumeration, no extrapolated exclusions. `scratch/F/r17/{rankpilot.stdout,pilot.results}`. | 0.00043 target pilot |
| hand + enum (count, NOT a closure) | **353,474,849** unsigned changed-row/first-external-pole headers after all priced cuts, from 847,881,702 after the grounded floors. Distinct actual marginals: 8,511 marked-row and 11,595 exterior-footprint representatives. Two counting directions and labelled fixed points agree. `scratch/F/r17/{finish.stdout,finalmark.rows,finalpole.rows}`, `ROUND17_FREEZE.sha256`. | 0.01267 total all stages incl. 0.00581 clean replay |

**Next:** Do not scan those 353 million pairs; do not reopen the cyclic family. If authorized, price a single shared parity-mask bank on the remaining 7,448 exterior representatives with no full contact on 1..17. The 33/33 singleton-only pilot contradicts these *named* columns, not the untested population. Positive/adverse controls and original-edge or conventional local proof rebind required before any scaling. Request no extra cores. H/critic: review the interval-nine lemma and table as a scoped marked construction result; no distribution or unrestricted symmetry debit.

**Jobs:** all 37 foreground supervisors below exited; 35 success, `certctl` and `cert` could not raise a nested hard CPU limit and were rerun successfully as `certctl2` and `cert2`. No timeouts or kills. No jobs inherited from round 16. All commands under nice/timeout/CPU limit and 4-GiB virtual-memory cap. Measured 45.60 CPU-s = 0.01267 core-h, below 0.05 core-h. Commands/logs/start/deadlines are preserved in `scratch/F/r17/jobs.tsv`; log names below relative to that directory. Times are the host offsets in the TSV (+01:00). `round17_replay.sh` rebuilt the checks from a clean directory. Prior detail in `LOG.md`.

| PID | Command (see jobs.tsv for arguments) | Log | Cores | Start | Deadline |
|---:|---|---|---:|---|---|
| 823106 | `g++ -std=c++17 -O3 -mbmi2 -mpopcnt marked_price.cpp -o price` | `build.stdout` | 1 | 13:18:21 | 13:18:43 |
| 823243 | `./price control 1 small` | `ctl.stdout` | 1 | 13:18:22 | 13:18:40 |
| 843293 | `marked_audit.py control` | `literal.stdout` | 1 | 13:19:11 | 13:19:31 |
| 843348 | `marked_audit.py geometry` | `geometry.stdout` | 1 | 13:19:12 | 13:19:34 |
| 843380 | `./price price 64 pilot` | `pilot.stdout` | 1 | 13:19:12 | 13:19:34 |
| 847750 | `./price price 1 full` | `census.stdout` | 1 | 13:19:23 | 13:19:56 |
| 957881 | `g++ -std=c++17 -O3 -mbmi2 -mpopcnt marked_price.cpp -o price` | `build2.stdout` | 1 | 13:23:20 | 13:23:42 |
| 957998 | `./price control 1 small` | `ctl2.stdout` | 1 | 13:23:21 | 13:23:39 |
| 958006 | `./price price 1 full` | `census2.stdout` | 1 | 13:23:21 | 13:23:51 |
| 958117 | `marked_windows.py control small wsmall 1` | `ctlwindow.stdout` | 1 | 13:23:22 | 13:23:37 |
| 969214 | `marked_audit.py control` | `literal2.stdout` | 1 | 13:23:53 | 13:24:12 |
| 969310 | `marked_windows.py price full wsample 64` | `windowpilot.stdout` | 1 | 13:23:53 | 13:24:11 |
| 1006929 | `g++ -std=c++17 -O3 -mbmi2 -mpopcnt marked_price.cpp -o price` | `build3.stdout` | 1 | 13:25:13 | 13:25:35 |
| 1008276 | `./price smallpole 1 smallpole` | `ctlpole.stdout` | 1 | 13:25:14 | 13:25:32 |
| 1008294 | `marked_windows.py smallpole smallpole wspole 1` | `ctlpolewin.stdout` | 1 | 13:25:14 | 13:25:32 |
| 1008355 | `./price pole 1 pole` | `polecensus.stdout` | 1 | 13:25:15 | 13:25:37 |
| 1009297 | `marked_windows.py price full wmark 1` | `windowfull.stdout` | 1 | 13:25:16 | 13:25:41 |
| 1012104 | `marked_windows.py pole pole wpole 1` | `windowext.stdout` | 1 | 13:25:18 | 13:25:48 |
| 1051164 | `marked_joint.py control` | `jointctl.stdout` | 1 | 13:26:42 | 13:27:00 |
| 1051179 | `marked_joint.py pilot` | `jointpilot.stdout` | 1 | 13:26:42 | 13:27:04 |
| 1057110 | `marked_joint.py price` | `jointexact.stdout` | 1 | 13:26:55 | 13:27:53 |
| 1095331 | `marked_replay.py control` | `replayctl.stdout` | 1 | 13:28:23 | 13:28:41 |
| 1095348 | `marked_replay.py target` | `replay.stdout` | 1 | 13:28:23 | 13:29:08 |
| 1121580 | `g++ -std=c++20 -O3 -march=native column_join.cpp -o join` | `joinbuild.stdout` | 1 | 13:29:36 | 13:29:56 |
| 1122735 | `marked_sample.py control` | `rankctl.stdout` | 1 | 13:29:38 | 13:29:58 |
| 1122795 | `marked_sample.py target` | `rankpilot.stdout` | 1 | 13:29:38 | 13:30:23 |
| 1161387 | `marked_nine.py extract` | `extract.stdout` | 1 | 13:31:08 | 13:31:25 |
| 1161414 | `hole_lrat.py control` | `certctl.stdout` | 1 | 13:31:08 | 13:31:25 |
| 1161438 | `marked_nine.py cert` | `cert.stdout` | 1 | 13:31:08 | 13:31:26 |
| 1168942 | `hole_lrat.py control` | `certctl2.stdout` | 1 | 13:31:20 | 13:32:00 |
| 1169110 | `marked_nine.py cert` | `cert2.stdout` | 1 | 13:31:21 | 13:32:01 |
| 1230782 | `marked_prism.py control` | `prismctl.stdout` | 1 | 13:33:18 | 13:33:36 |
| 1230873 | `marked_prism.py bank` | `prismbank.stdout` | 1 | 13:33:18 | 13:33:40 |
| 1232122 | `marked_prism.py pilot` | `prismpilot.stdout` | 1 | 13:33:19 | 13:33:39 |
| 1263258 | `marked_prism.py price` | `prismfull.stdout` | 1 | 13:34:03 | 13:34:23 |
| 1285335 | `marked_finish.py` | `finish.stdout` | 1 | 13:34:40 | 13:35:08 |
| 1305714 | `cd ../r17clean; bash round17_replay.sh` | `clean.stdout` | 1 | 13:35:21 | 13:37:01 |
