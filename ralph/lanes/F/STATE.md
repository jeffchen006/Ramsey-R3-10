# Lane F state

Round 18 complete. **No candidate, zero running/stopped jobs.** The critic authorized one worker for a shared no-double parity bank, not a signing or joint search. Scope: the 17 intact sites of the *one-exceptional-site* marked construction, not the retired cyclic family or any unrestricted symmetry/degree case. Empirical nearness still 24 at 178 and 179 edges; `round18_nearness.tsv`.

| Label | Result and evidence | Core-h |
|---|---|---:|
| hand + enum (pending review) | 7,184/7,448 new no-double representative cuts (14,296 labelled; 72 fixed), on sites 1..17 plus at most one pole, valid for both columns. 264 unresolved (512 labelled). `ROUND18.md`, `scratch/F/r18/{targetck,wideck,ctlprep,tamper}.stdout`, both `.checked` production files. | included below |
| hand + enum (price only) | 353,474,849 → 16,182,483 unsigned marked joint headers, of which 15,573,942 have exactly one double in at least one role. 1,327 marked and 4,411 pole reps. Both arithmetic counts and clean replay match. `scratch/F/r18/{stratprice.stdout,doubleprice.tsv,clean.stdout}`, `ROUND18_FREEZE.sha256`. | 0.00420 total |

**Next:** Stop the no-double bank; do not scan the 16 million joint headers or reopen ID8/21. Request at most a single-worker, exactly-one-double shared bank pilot on the 3,709 remaining exterior reps, grouped by the doubled site. Check the physical triangle, restored-pair/vertical, polar edges and pin conventions rather than transferring a no-double certificate across the cut. 1,050 marked rows in this stratum; no inferred success rate. No more cores needed. H/critic: review this as a scoped construction filter only.

**Jobs:** inherited none; all 19 bounded foreground supervisors below **exited successfully**. No failures, timeouts, detached or stopped jobs. Start/deadline clocks use the host offset (+01:00). `scratch/F/r18/jobs.tsv` gives full invocation and timestamps. No job should be stopped or resumed. Prior states in `LOG.md`.

| PID | Command | Log (scratch/F/r18) | Cores | Start | Deadline |
|---:|---|---|---:|---|---|
| 3250962 | `../../../opt/venv/bin/python -B ../../../ralph/lanes/F/marked_bank.py control` | `ctlprep.stdout` | 1 | 14:36:42 | 14:37:07 |
| 3250973 | `g++ -std=c++20 -O3 -march=native ../../../ralph/lanes/F/marked_bank.cpp -o bank` | `build.stdout` | 1 | 14:36:42 | 14:37:12 |
| 3252100 | `./bank small.q 4 small.bank small.rows small.trace 8` | `ctl.stdout` | 1 | 14:36:44 | 14:37:04 |
| 3272230 | `../../../opt/venv/bin/python -B ../../../ralph/lanes/F/marked_bank_check.py small small.rows small.bank small.trace` | `ctlcheck.stdout` | 1 | 14:37:25 | 14:37:45 |
| 3272237 | `../../../opt/venv/bin/python -B ../../../ralph/lanes/F/marked_bank_check.py tamper` | `tamper.stdout` | 1 | 14:37:25 | 14:37:45 |
| 3272309 | `../../../opt/venv/bin/python -B ../../../ralph/lanes/F/marked_bank.py prepare` | `prep.stdout` | 1 | 14:37:25 | 14:37:50 |
| 3272433 | `./bank core.q 10 frozen.bank pilot.rows pilot.trace 8` | `pilot.stdout` | 1 | 14:37:25 | 14:37:50 |
| 3272490 | `../../../opt/venv/bin/python -B ../../../ralph/lanes/F/marked_bank_check.py pilot pilot.rows frozen.bank pilot.trace` | `pilotck.stdout` | 1 | 14:37:25 | 14:37:55 |
| 3280399 | `./bank core.q 10 frozen.bank target.rows target.trace 8` | `target.stdout` | 1 | 14:37:41 | 14:38:11 |
| 3280413 | `../../../opt/venv/bin/python -B ../../../ralph/lanes/F/marked_bank_check.py target target.rows frozen.bank target.trace` | `targetck.stdout` | 1 | 14:37:41 | 14:38:21 |
| 3280449 | `../../../opt/venv/bin/python -B ../../../ralph/lanes/F/marked_bank.py finish` | `price.stdout` | 1 | 14:37:42 | 14:38:12 |
| 3290687 | `../../../opt/venv/bin/python -B ../../../ralph/lanes/F/marked_bank.py extend` | `extend.stdout` | 1 | 14:38:08 | 14:38:28 |
| 3290695 | `./bank core.q 10 wider.bank restpilot.rows restpilot.trace 8` | `widenpilot.stdout` | 1 | 14:38:08 | 14:38:33 |
| 3290708 | `../../../opt/venv/bin/python -B ../../../ralph/lanes/F/marked_bank_check.py restpilot restpilot.rows wider.bank restpilot.trace` | `widenpilotck.stdout` | 1 | 14:38:08 | 14:38:33 |
| 3298397 | `./bank core.q 10 wider.bank rest.rows rest.trace 8` | `wide.stdout` | 1 | 14:38:28 | 14:38:53 |
| 3301207 | `../../../opt/venv/bin/python -B ../../../ralph/lanes/F/marked_bank_check.py rest rest.rows wider.bank rest.trace` | `wideck.stdout` | 1 | 14:38:31 | 14:38:56 |
| 3301226 | `../../../opt/venv/bin/python -B ../../../ralph/lanes/F/marked_bank.py final` | `final.stdout` | 1 | 14:38:31 | 14:38:51 |
| 3315290 | `../../../opt/venv/bin/python -B ../../../ralph/lanes/F/marked_bank.py final` | `stratprice.stdout` | 1 | 14:39:05 | 14:39:25 |
| 3315357 | `bash -c cd ../r18clean; bash ../../../ralph/lanes/F/round18_replay.sh` | `clean.stdout` | 1 | 14:39:06 | 14:40:01 |
