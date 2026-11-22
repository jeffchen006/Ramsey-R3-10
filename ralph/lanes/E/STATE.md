# Lane E state — round 16 complete

2026-11-22 CET. Allocation 33, at most five actual concurrent capped
slots (four during full scan/replay). The critic accepted core 8 as
E-038; see `LOG.md`. This round priced only zero-based core 15 (`GCQf?{`).

## Jobs

No active, stopped, killed or detached jobs; zero cores. All 41 capped
wrappers collected: 40 exits 0 and one recovered native calibration
setup error before the tests. All production/replay workers exited 0.
Exact PIDs, commands, log names, slots and actual end times are in
`scratch/E/r16_shared/{jobs,exits}.tsv`.

| Work | Peak slots | Start range / latest allowed finish (CET) |
|---|---:|---|
| Controls, census, ordered bind and pilot | 5 | 11:53:02–11:55:23 / 12:00:34 |
| Eight full scans and unchanged replays, merge and exact queue | 4 | 11:56:14–11:57:43 / 12:00:05 |
| Future proof-roster control only; six sites | 1 | 11:57:28 / 11:57:54 |

## Results for H / critic

Scope: `(p,f,t)=(2,32,4)`, `δ(W)≥2`, `e(W)=11`, mixed
`(10,10,11,11)`, universal `δ(G)≥5`, E-021 all-graph sole-missing
`e=74` premise, all four omission roles and `K=6,7,8`. Not MTF-only.

| Item | Label | Evidence and cost |
|---|---|---|
| Independently regenerated exact ordered cover matches all 34 first branches (no empties), 94,738 projections, 716,045 lifts. All eight shards replayed. The exact queue has **142 open IDs in 110 projections**. **Stopped before any target proof work** (100-ID ceiling). | enum (replayed queue) / open (core 15), no closure claim | `shared74_round16.md`; `scratch/E/r16_shared/{freeze.15.sha256,bind.cover.15.log,merge.15.log,queue.15.jsonl}`. 0.09102 core-h main, 0.09697 whole round, ~75 MB retained. |
| Every canonical first branch included in the price ledger: front/interior/tail samples had 544/171/148 hard lifts and 17/3/3 terminal IDs. Known smaller support and six-site positives/negatives, misbound narrow branch, and ordered mismatch controls pass. Counts are measured, not a proof-cost forecast. | enum + estimate (pricing only) | `scratch/E/r16_shared/{hard.15.tsv,pilot.15.branches.tsv,calibrate.order-misbind.log}`; included in total. |

## Handoff

- Mixed cores **1, 6, 9, 15, 18** still open; no work on others this
  round. The core-15 exact queue and the reserved 16 dispersed IDs
  include both extremes; none were given to a target solver. Ask the
  critic whether to reopen that proof gate or redirect. Do not rescan
  merely to recover the queue, and do not transfer core-8 prices to it.
- `ordered_cover74.py` binds the stable global projection/lift IDs.
  `audit_routes74.py` adds a fail-fast route wrapper and exact recheck
  roster audit; calibrated only on the smaller known control here.
- `(5,5)` already certified. No full `(2,32)` closure, no candidate,
  no rigidity theorem, and no Ramsey verdict.
