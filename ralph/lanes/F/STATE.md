# Lane F state

Round 16 complete. **3-core ceiling; no live or stopped jobs; no candidate.** Strongest new result (hand + cert, submitted to critic): the final ID8 36-card cannot acquire **even one** arbitrary vertex in a triangle-free graph with alpha≤9. With the reviewed prior reductions this excludes the entire *four-deletion cyclic unsigned free-involution 36-card family* of targets (hand + inherited enum/cert). Does not exclude the old 36-card alone, an unrestricted automorphism case or a global edge distribution. No change to best empirical score: 24 tens at e178 and e179. `ROUND16.md`, `round16_nearness.tsv`.

| Label | Result and evidence | Core-h |
|---|---|---:|
| hand + enum | Named hole: exactly one of 64 local cycle roles survives all 45 eight-singleton supports; independently reproduced from physical endpoint matchings. Singleton-only test by itself leaves 40 roles, and some four-hole cuts and polynomial multiples remain open. `scratch/F/r16/{full,contacts,restored,splitfull,multipilot}.stdout`. | 0.00467 |
| hand + cert | Seven-site bridge: no pole may take a full site, verticals restore **with the pole attached**, and the pole must meet every cyclic seven-window. `ROUND16.md`; `scratch/F/r16/{no_blind_pole.cnf,no_blind_pole.lrat,sataudit.stdout}`. | 0.00007 |
| hand + enum | Each of 89,445 first-column footprints, 2,623 D18 reps of sizes 3..8, terminates on a ten. Original-edge replay of all 23,428 deductions. `scratch/F/r16/{rosteraudit,eightaudit}.stdout`, `feet.trace`, `eight.trace`. | 0.00375 |
| hand + cert | ID8 is **not extendible to 37**, any verticals and any crossing signs. One ordinary CNF, 2,624 disjuncts, 320,371 vars / 768,865 clauses; both proof checkers plus frozen support rebinding PASS. `scratch/F/r16/id8_strong.{cnf,lrat}`, `strongbind.stdout`, `id8_frozen.py strong`, `ROUND16_FREEZE.sha256`. | 0.07530 |

**Next:** critic/H please replay `id8_frozen.py strong` and review the seven-window reduction, especially its mate-hit argument, before ledgering the conditional family closure. If accepted, retire the whole cyclic four-deletion family. A genuinely different follow-up would price a *single exceptional site* in an otherwise cyclic unsigned card (first check exactly which old filters fail without translation); require small controls and a priced one-pole gate, do not relaunch ID8 or old anneal searches. No extra cores requested. R15 ID21 confirmed as F-029. Earlier state is in `LOG.md`.

**Jobs:** all 50 foreground supervisors have exited (49 success; `onecycles` had a missing diagnostic import and was corrected in `cyclefixed`). All ran with nice 5, timeout, CPU and 4-GiB address-space caps. Total 301.63 CPU-s = 0.08379 core-h. No detached processes. Full unabridged commands and deadlines in `scratch/F/r16/jobs.tsv`; sample forecasts in `price.txt`, log paths below relative to `scratch/F/r16/`. Times are the host offsets recorded in `jobs.tsv` (+01:00).

| PID | Command (prefixes elided) | Log | Cores | Start | Deadline |
|---:|---|---|---:|---|---|
| 3357830 | `id8_local.py control` | `ctl.stdout` | 1 | 11:53:28 | 11:54:08 |
| 3357839 | `hole_lrat.py control` | `ctlcnf.stdout` | 1 | 11:53:28 | 11:54:08 |
| 3357876 | `id8_local.py pilot` | `pilot.stdout` | 1 | 11:53:28 | 11:54:08 |
| 3365659 | `id8_local.py full` | `full.stdout` | 1 | 11:53:52 | 11:54:32 |
| 3368878 | `id8_roles.py control` | `ctlrole.stdout` | 1 | 11:54:06 | 11:54:46 |
| 3369001 | `id8_roles.py 4 63 0 9 18 27 36 45 54` | `rank4price.stdout` | 1 | 11:54:07 | 11:54:57 |
| 3382156 | `id8_roles.py 6 63` | `rank6price.stdout` | 1 | 11:54:44 | 11:55:29 |
| 3405541 | `id8_regions.py control` | `ctlregion.stdout` | 1 | 11:56:15 | 11:56:55 |
| 3405584 | `id8_regions.py 2 pilot` | `regionpilot.stdout` | 1 | 11:56:15 | 11:56:55 |
| 3417057 | `id8_contacts.py control` | `ctlcontact.stdout` | 1 | 11:56:56 | 11:57:36 |
| 3417088 | `id8_contacts.py contacts` | `contacts.stdout` | 1 | 11:56:56 | 11:57:36 |
| 3441307 | `id8_pairs.py 4 7 9` | `pairpilot.stdout` | 1 | 11:58:04 | 11:58:44 |
| 3461980 | `id8_marks.py 0,4,8,12 0,4,9,13` | `fourpilot.stdout` | 1 | 11:58:56 | 11:59:41 |
| 3476550 | `id8_marks.py 0 0,4,8,12 0,4,8,13 0,4,9,13` | `condpilot.stdout` | 1 | 11:59:26 | 12:00:26 |
| 3488103 | `python -c (see jobs.tsv)` | `packpilot.stdout` | 1 | 12:00:02 | 12:00:42 |
| 3509946 | `id8_split.py 0,4,8,12 6 pilot` | `splitpilot.stdout` | 1 | 12:00:46 | 12:01:36 |
| 3512384 | `id8_split.py 0,4,8,12 6 full` | `splitfull.stdout` | 1 | 12:00:54 | 12:01:49 |
| 3554785 | `id8_lowdegree.py control` | `ctlmulti.stdout` | 1 | 12:03:02 | 12:03:42 |
| 3554793 | `id8_lowdegree.py 0,4,8,12 3 pilot` | `multipilot.stdout` | 1 | 12:03:02 | 12:03:52 |
| 3580134 | `python -c (see jobs.tsv)` | `onecycles.stdout` | 1 | 12:04:19 | 12:04:49 |
| 3592434 | `python -c (see jobs.tsv)` | `cyclefixed.stdout` | 1 | 12:04:59 | 12:05:29 |
| 3599727 | `id8_roles.py 6 0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 2… (jobs.tsv)` | `restored.stdout` | 1 | 12:05:33 | 12:06:23 |
| 3616373 | `id8_pack.py` | `pack24.stdout` | 1 | 12:06:35 | 12:07:15 |
| 3717544 | `id8_saturation.py control` | `satctl.stdout` | 1 | 12:12:05 | 12:12:45 |
| 3717566 | `id8_saturation.py target` | `satproof.stdout` | 1 | 12:12:05 | 12:12:45 |
| 3717589 | `id8_saturation_check.py` | `sataudit.stdout` | 1 | 12:12:05 | 12:12:45 |
| 3766935 | `id8_baskets.py control` | `basketctl.stdout` | 1 | 12:14:21 | 12:14:51 |
| 3766992 | `id8_baskets.py 13` | `basketprice.stdout` | 1 | 12:14:21 | 12:14:51 |
| 3770567 | `id8_baskets.py 1` | `baskets.stdout` | 1 | 12:14:31 | 12:15:11 |
| 3770583 | `../r14/join2 ../r14/control.q 4 ../r14/control.request controls.trace 12` | `joinctl.stdout` | 1 | 12:14:32 | 12:15:12 |
| 3770589 | `../r14/join2 id8.q 10 footpilot.request footpilot.trace 12` | `footpilot.stdout` | 1 | 12:14:32 | 12:15:22 |
| 3772127 | `../r14/join2 id8.q 10 feet.request feet.trace 12` | `allfeet.stdout` | 1 | 12:14:41 | 12:15:56 |
| 3784427 | `id8_roster.py` | `rosteraudit.stdout` | 1 | 12:15:17 | 12:17:02 |
| 3802160 | `id8_cnf_bank.py pilot 109` | `certpilot.stdout` | 1 | 12:16:21 | 12:18:06 |
| 3817620 | `id8_cnf_bank.py bank 1` | `certbank.stdout` | 1 | 12:17:00 | 12:21:10 |
| 3832197 | `id8_merge.py pilot` | `mergepilot.stdout` | 1 | 12:17:53 | 12:18:33 |
| 3844066 | `id8_frozen.py export` | `export.stdout` | 1 | 12:18:37 | 12:19:07 |
| 3844083 | `id8_merge.py pilot` | `mergepilot2.stdout` | 1 | 12:18:37 | 12:19:17 |
| 3844101 | `id8_frozen.py pilot` | `bindpilot.stdout` | 1 | 12:18:37 | 12:19:17 |
| 3850023 | `id8_eight.py` | `add8.stdout` | 1 | 12:18:59 | 12:19:29 |
| 3850114 | `../r14/join2 id8.q 10 eightpilot.request eightpilot.trace 12` | `eightpilot.stdout` | 1 | 12:18:59 | 12:19:39 |
| 3854042 | `../r14/join2 id8.q 10 eight.request eight.trace 12` | `all8.stdout` | 1 | 12:19:09 | 12:19:59 |
| 3868733 | `id8_frozen.py export8` | `export8.stdout` | 1 | 12:19:42 | 12:20:12 |
| 3868749 | `id8_cnf_bank.py eight 113` | `cert8pilot.stdout` | 1 | 12:19:42 | 12:20:37 |
| 3872381 | `id8_cnf_bank.py eight 1` | `cert8bank.stdout` | 1 | 12:19:54 | 12:23:59 |
| 3916340 | `id8_shadow.py` | `shadowctl.stdout` | 1 | 12:21:12 | 12:21:42 |
| 3926567 | `python -c (see jobs.tsv)` | `eightaudit.stdout` | 1 | 12:21:26 | 12:22:41 |
| 3940898 | `bash -c cd freshpilot && exec ../../../../opt/venv/bin/python -B ../../.… (jobs.tsv)` | `freshpilotrun.stdout` | 1 | 12:21:57 | 12:22:52 |
| 3949374 | `id8_merge.py strong` | `strongmerge.stdout` | 1 | 12:22:16 | 12:24:06 |
| 3950891 | `id8_frozen.py strong` | `strongbind.stdout` | 1 | 12:22:24 | 12:24:14 |
