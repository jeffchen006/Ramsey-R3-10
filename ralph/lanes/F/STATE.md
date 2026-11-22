# Lane F state

Round 21 complete. **No candidate; no active/stopped jobs.** All 14 marked two-double rows in the one-exceptional-site family remain open. `ROUND21.md` and `ROUND21_FREEZE.sha256` are the handoff. Round 20 state is in `LOG.md`.

| Label | Result / evidence | Core-h |
|---|---|---:|
| hand + enum (pending) | 0/14 marked cuts (23 labelled, 5 fixes); same 14 tested as exterior rows, 398 other two-double exterior reps untouched. All 170 bound deductions independently replayed. Geometry: 4 or 5 available ordinary sites, never the 6 required by four-endpoint padding. `scratch/F/r21/{pilot.open,verify.stdout,geometry.stdout}` | 0.00082 all-in |
| enum (pending) | Both inventories unchanged (668 marked / 1,137 exterior), unsigned joint headers 1,979,210 unchanged. No signing result or unrestricted case debit. `scratch/F/r21/{joint.tsv,price.stdout,mark.left,pole.left,two-double-exterior.untested}` | included |
| enum (controls) | 48/1,944 positive exterior and 48/3,888 positive marked small configurations preserved; small negative needs all four ends; two gate positives, six mutations rejected. `scratch/F/r21/{literal,mutations}.stdout`. No new order-40 nearness score: historical degree-valid best 24 at e=178,179, `round21_nearness.tsv`. | included |

**Next:** Park the four-endpoint rule here. Keep 435 one-double, 264 no-double, 412 two-double and 26 three-double exterior rows open. No expanded sweep or sign search requested. Optional **small controls only** for a distinct marked-only deduction using both exceptional endpoints together (see `ROUND21.md`); no target request without a calibrated strict improvement over the old forest rule. H: record the zero cut, not 170 exclusions.

**Jobs:** inherited none. All 20 one-worker foreground stages exited zero, no timeout/kill/detach. Full argv, supervisor, start and wall deadline in `scratch/F/r21/jobs.tsv`; output/time in `scratch/F/r21/<name>.{stdout,time}`. All timestamps below are local UTC+01:00 on 2026-11-22. No PID to kill/resume.

| PID | Command/log name | Cores | Start | Deadline |
|---:|---|---:|---|---|
| 3658620 | `hashes` | 1 | 17:58:05 | 17:58:19 |
| 3658639 | `build` | 1 | 17:58:05 | 17:58:24 |
| 3658892 | `small` | 1 | 17:58:07 | 17:58:20 |
| 3658919 | `control_s0` | 1 | 17:58:07 | 17:58:20 |
| 3658928 | `control_s1` | 1 | 17:58:08 | 17:58:20 |
| 3658937 | `control_s2` | 1 | 17:58:08 | 17:58:20 |
| 3658954 | `control_s3` | 1 | 17:58:08 | 17:58:20 |
| 3658964 | `control_s4` | 1 | 17:58:08 | 17:58:20 |
| 3658975 | `control_s5` | 1 | 17:58:08 | 17:58:20 |
| 3658984 | `control_s6` | 1 | 17:58:08 | 17:58:20 |
| 3658997 | `control_s7` | 1 | 17:58:08 | 17:58:20 |
| 3659006 | `control_old` | 1 | 17:58:08 | 17:58:20 |
| 3659015 | `control_pin` | 1 | 17:58:08 | 17:58:20 |
| 3659024 | `literal` | 1 | 17:58:08 | 17:58:23 |
| 3659220 | `mutations` | 1 | 17:58:08 | 17:58:21 |
| 3659426 | `preflight` | 1 | 17:58:08 | 17:58:22 |
| 3659728 | `produce` | 1 | 17:58:08 | 17:58:24 |
| 3659783 | `verify` | 1 | 17:58:08 | 17:58:23 |
| 3659792 | `price` | 1 | 17:58:08 | 17:58:23 |
| 3675643 | `geometry` | 1 | 17:58:57 | 17:59:09 |
