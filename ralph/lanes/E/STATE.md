# Lane E — round 24 handoff (2026-11-22 CET)

All new work is for `(p,f,t)=(2,32,4)`, `δ(W)≥2`, `e(W)=8`,
`P=0`, universal `δ(G)≥5`, **without maximality**. Inherited r22/r23
known-card exclusions and the E-021 all-graph catalogue premise force
all four fixed deletion cards into the same single missing class.
No flow candidate; `(5,5)` remains certified from the earlier run.
See `ROUND24.md`, `ROUND23.md` and `LOG.md` for math and prior work.

## Jobs and exact state

Round-23 wrappers all gone at start. Round-24 repair wrappers
3745738/3745750/3745764/3745778 (one core each, 22:27:07 start) all
finished with 959/959 `CHECKED`, in `scratch/E/r24_deck/repair.*.log`.
Their exact commands, wall/CPU caps, and exit statuses are in
`scratch/E/r23_deck/{jobs,exits}.tsv`. No retry credit for old IDs.
Seven early replay wrappers reached their wall boundary before the
ledger was complete; 14,409 valid distinct rows retained, exact 941
anti-join then given a dedicated lease. No claim based on wall exit.

Round-24 work directory `scratch/E/r24_deck`. Every solver, census,
replay and heavy audit only runs while holding one of 22 file-lock
leases, released on actual child exit. `jobs.tsv` logs real one-core
timeout PIDs/commands/starts/deadlines and lease numbers; `exits.tsv`
logs completed statuses. The stopped initial dispatcher PID 3906844
had no solver child in its session (worker jobs have own sessions);
actual producer wrappers were not stopped. Stage wrapper 262414
exited cleanly, as did all cover/census, pilot and disk measurement.

| Real timeout PIDs | Command / log | Cores | Start / outer deadline (CET) |
|---|---|---:|---|
| 3906881/3906904/3906927/3906961/3906995/3907038/3907074/3907122/3907162/3907213/3907277/3907301/3907359/3907418/3907680 | `compact_deck24.py run --plan C8.plan --indexes C8.prod/SLOT.ids --output C8.prod/SLOT --archive-limit 125829120`; slots 0–13,21; `C8.SLOT.log` | 15×1 | 22:31:01–02 / Nov 23 02:24:26–27 |
| 291549/263797/263923/264113/264204/264275 | Same, slots 14–19 | 6×1 | 22:44:23–22:45:01 / Nov 23 02:37:48–02:38:26 |
| 774191 | Same, slot 20, started after complete 2C4 replay | 1 | 22:55:09 / Nov 23 02:48:34 |

Replay-tail wrapper 264350 exited 0 at 22:55:08; reserved dispatcher
91355 finished dispatch without an extra work slot. At 22:55:28
all 22 listed C8 wrappers were alive and not stopped. Expected most
shards end Nov 23 ~01:00–02:00 at the observed throughput (estimate;
upper bounds above); monitor the late shards and resource exits.

C8 baseline: 224 pilots + 242,938 assigned distinct nonpilot IDs.
Weighted pilot ~10.24 core-h, ~1.883 GB compressed proofs. Capacity:
<3.65 GB simultaneous reservation, 120 MiB archive + 32 MiB scratch
proof per worker, 2 GiB VM and child time limits; no cap is UNSAT.
Estimated elapsed varies with observed contention. `snapshots.tsv`
reports completed CPU deltas (does not count a lease as a busy core).

## Claims for H/critic (pending)

| Result | Label | Evidence |
|---|---|---|
| Exact independent column-first bmax=16 cover agrees with the prior row-first cover: 15,350 2C4 and 243,162 C8 keys. Originally missing 959 2C4 IDs repaired, no duplicates. | hand + enum cover; local certs | `ROUND24.md`, `scratch/E/r24_deck/{stage15.log,2c4.old.json,2c4.repair.ids}` |
| **Entire `2C4` core sector for bmax=16**, both profiles, excluded conditional on E-021. Role-specific physical CNFs and LRATs freshly rebound and dual-checked **15,350/15,350**: 14,409 initial replay + exact 941 tail. No open, no lazy masks. Round-24 solve/replay 0.540 core-h excluding census. | hand + enum + cert (conditional) | `ROUND24.md`, `scratch/E/r24_deck/{2c4.final.log,replay-tail.log,freeze.2c4.sha256}` |
| C8 29,578 distinct dual CHECKED at 22:55:17 (224 pilots over seven strata + 29,354 prod), zero other completed statuses, 213,584 unprocessed; independent bytes bound. Whole C8 production still open. | cert (local) + estimate + open | `price.log`, `snapshots.tsv`, `pilot/`, live `C8.prod/`, `jobs.tsv` |
| Two b15/min10 successor profiles factorized on both cores. `2C4 (10,10,13,15)` is smallest: 82 row packs, 80,896 ordered raw product upper. On 256 distinct sampled b15 rows, C-058 primary and independent literal gate agree on all stage counts and retained pair/support lists; 234/256 vetoed. Shape-only E-031 component screen separately calibrated on 13 C13 deletions and 2,163 labelled max-degree-two graphs. **No b15 closure.** | hand + enum (sample) + estimate | `ROUND24.md`, `stage15.log`, `profile15.*.gate.jsonl` and `.sample.jsonl` |

## Next

- Retire the 2C4 bmax=16 solver/replay arm; critic to check scoped
  closure from exact cover, `2c4.final.log` and `freeze.2c4.sha256`.
- Collect C8 receipts using `audit_deck24.py --prefix PREFIX`; an
  absent, capped or model row stays open. Keep pilot and modulo shards
  disjoint and verify packed LRAT members with `compact_deck24.py replay`.
  The C8 cover is complete but proof coverage is not.
- On released leases, start with `2C4 (10,10,13,15)`: exact independent
  row-pack and column cover, C's physically pinned primary/inverse
  trace gate, then calibrate b15 formulas with actual checked survivors
  before long production. 0.76 core-h structural-gate extrapolation;
  the additional ~0.43 core-h at b16 unit cost is uncalibrated for
  b15. The larger products and `(11,11,11,15)` remain unstaged for solve.
- Retire confirmed r23 e10 `(10,10,10,14)`, e8 known-card arms and
  old e11/P2 results. No concrete new missing-class source, no assumed
  marked isomorphism, and no whole `(2,32)` or unrestricted Ramsey claim.
