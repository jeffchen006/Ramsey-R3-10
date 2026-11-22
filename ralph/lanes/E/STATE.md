# Lane E state — round 13 complete

2026-11-22; machine time CET (UTC+01:00). Allocation 26; peak 12 worker
slots. No detached
jobs or candidate submissions. All symmetry work covers all graphs,
not just MTF. Critic confirmed core 16 (E-032); see `LOG.md`.

## Jobs

Exact wrapper PID, start, cap, log and command in
`scratch/E/r13_shared/jobs.tsv` (one capped foreground worker per row).
Wrapper uses `nice -n 5`, `timeout` with 8-s grace, CPU limits and 16 GiB
address space. Audit/production details in `shared74_round13.md`.

| Work | Peak slots | Start range (CET) | Latest allowed finish (CET) |
|---|---:|---|---|
| Controls, census, price, narrow and native pilots | 12 | 07:34:27–07:41:30 | 07:44:40 |
| 20 production scans/merge, native full ordered replay | 10 | 07:42:29–07:44:33 | 08:04:41 |
| Exact-queue reprice, production CNFs and fresh proof rebind | 6 + replay | 07:44:33–07:45:53 | 07:47:05 |
| Old Python whole receipt audit (20 byte-bound shards) | 10 | 07:50:46–07:51:55 | 07:55:43 |

All 98 wrappers collected; no active or stopped workers at 07:53:30.
Proof artifacts respected the cap; round scratch about 601 MiB logical.

## Results and claims (for H / critic)

- Core 17 ``GCR`r_``: `(p,f,t)=(2,32,4)`, `δ(W)≥2`, `e(W)=11`,
  profile `(10,10,11,11)`, universal `δ(G)≥5` and the E-021
  all-graph sole-missing `e=74` class premise. All four omissions and
  `K=6,7,8` retained. Zero-based core IDs in `scratch/E/r5_saturated/e11.g6`.

| Item | Label | Evidence / cost |
|---|---|---|
| **Core 17 only excluded** under this scope: 27 independent first branches, no empties, 193,365 projections and 2,135,171 lifts, both complete receipt replays and 262 freshly regenerated original-CNF CakeLRATs. | hand + enum + cert, pending critic | `shared74_round13.md`, `scratch/E/r13_shared/freeze.17.sha256`; 0.36433 core-h main path, 0.62728 with Python audit |
| New native trace validator made the scan/replay price 1,508 vs 3,530 CPU-s on the same three bands, with identical receipts. Exhaustive order≤4 and mutated trace controls plus complete unchanged Python audit. | enum / estimate | `fast_trace74.py`, `check_trace74.c`, `shared74_round13.md`, `scratch/E/r13_shared/{calibrate.check.log,python.replay.total.17.log}` |
| Width-three pilot: 22/22 core-17 band residuals + 107/107 core-16 held-out terminal IDs all checked; same variables and literal-clause subset. No use in production. | hand + cert pilot | `width_shared74.py`, `scratch/E/r13_shared/freeze.width.sha256`; ≈0.006 core-h for all tested widths and holdout |

## Handoff

- Ask the critic to independently review and replay core 17. The replay
  recipe in `shared74_round13.md` uses the unchanged Python checker;
  native is not a prerequisite to accept the result. The exact 262-ID
  queue triggered its stop and was repriced on 16 spaced IDs before
  original proof work. No width-three or roster cuts used in closure.
- Seven mixed cores remain if 17 is accepted: 1,5,6,8,9,15,18. Consider
  exact cover + three-band price of 5 next, using the checked native
  validator. No unpriced heavy 9/18 scans. Audit a standalone narrow
  generator and price a wide fallback before adopting width three.
- No change to other f32 profiles; `(5,5)` already certified. No full
  `(2,32)` closure, rigidity or Ramsey verdict. No candidate submitted.
