# Lane F state

Round 20 complete. **No candidate or active/stopped jobs.** The one-double census in the one-exceptional-site family is complete, not the construction itself. Round 19 state archived in `LOG.md`. `ROUND20.md` and `ROUND20_FREEZE.sha256` are the handoff.

| Label | Result / evidence | Core-h |
|---|---|---:|
| hand + enum (pending) | 3,172/3,581 previously unseen one-double reps physically excluded (6,339 labels, 5 fixes), including 646/1,018 marked. Union with pilot: 3,274/3,709 excluded, 435 open (391 marked). Exact open lists; 50,877 new GF(2) deductions. `scratch/F/r20/{preflight.stdout,verify.stdout,pilot.checked,one-double.open,strata.tsv}`. | 0.00199 all-in |
| hand + enum (price, pending) | Unsigned compatible joint headers after simultaneous reversal: 15,613,661 → 1,979,210, net 13,634,451; inclusion/exclusion and reversal checked. `scratch/F/r20/{joint.tsv,price.stdout,mark.left,pole.left}`. No graph/existence or global case inference. | included |
| enum (control) | Repeated exhaustive small controls, marked C8 positive, corrupted pins and projected-form mutations. `scratch/F/r20/{calibrate,tamper,corrupt_pin}.stdout` and `positive.gate`. No new order-40 score: historical degree-valid minimum 24 at e=178,179; `round20_nearness.tsv`. | included |

**Next, subject to critic:** Only 14 two-double marked rows (also exterior). Test six singleton sites padded by four physically independent doubled endpoints, plus the older allowed modes; require the new smaller positive, exhaustive controls, corrupted pair/pin and independent physical GF(2) replay first. Request one worker, ≤0.02 core-h / 512 MiB, no other rows or signing. Keep the 435 open one-double and 264 no-double rows parked. Other remaining exterior reps: 412 two-double (including those 14) and 26 three-double. H: record the scoped physical cuts and the post-pilot net price separately.

**Jobs:** inherited none. All 19 foreground commands exited zero; none detached, stopped, timed out or killed. Full argv/start/deadline and supervisor PID: `scratch/F/r20/jobs.tsv`; `<name>.stdout` and `<name>.time` in that directory. Table times are 2026-11-22, UTC+01:00. No PID to kill or resume.

| PID | Command/log name | Cores | Start | Deadline |
|---:|---|---:|---|---|
| 2961708 | `hashes` | 1 | 17:23:47 | 17:24:02 |
| 2961718 | `build` | 1 | 17:23:47 | 17:24:09 |
| 2962192 | `small` | 1 | 17:23:49 | 17:24:02 |
| 2962205 | `control_c3_0` | 1 | 17:23:49 | 17:24:01 |
| 2962214 | `control_c3_1` | 1 | 17:23:49 | 17:24:01 |
| 2962224 | `control_c3_2` | 1 | 17:23:50 | 17:24:02 |
| 2962234 | `control_c3_3` | 1 | 17:23:50 | 17:24:02 |
| 2962243 | `control_c3_4` | 1 | 17:23:50 | 17:24:02 |
| 2962252 | `control_c3_5` | 1 | 17:23:50 | 17:24:02 |
| 2962263 | `control_c3_6` | 1 | 17:23:50 | 17:24:02 |
| 2962272 | `control_c3_7` | 1 | 17:23:50 | 17:24:02 |
| 2962282 | `control_c4_45` | 1 | 17:23:50 | 17:24:02 |
| 2962291 | `calibrate` | 1 | 17:23:50 | 17:24:10 |
| 2963087 | `tamper` | 1 | 17:23:51 | 17:24:05 |
| 2963164 | `corrupt_pin` | 1 | 17:23:51 | 17:24:05 |
| 2963312 | `preflight` | 1 | 17:23:51 | 17:24:06 |
| 2963436 | `produce` | 1 | 17:23:51 | 17:24:36 |
| 2965550 | `verify` | 1 | 17:23:54 | 17:24:22 |
| 2966087 | `price` | 1 | 17:23:55 | 17:24:15 |
