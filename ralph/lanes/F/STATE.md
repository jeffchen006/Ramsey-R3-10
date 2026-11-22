# Lane F — round 23 handoff

**No order-40 candidate. The 17-pair (34-vertex) construction has sharp maximum order 37** for a triangle-free graph with independence number ≤9. All exterior vertices and all verticals were unrestricted. This is a family-scoped claim for critic review, not a global Ramsey or symmetry result. Round 22's 668 marked rows / 1,137 exterior marginal remain retired; archived in `LOG.md`.

## Results / claims (pending critic review)

All paths below without a directory prefix are under `scratch/F/r23/`. Explanation and scope: `ralph/lanes/F/ROUND23.md`. Freeze: `ralph/lanes/F/ROUND23_FREEZE.sha256`, `receipts23.sha256` (19,906 content digests; both entire manifests verified).

| Label | Result and primary evidence | CPU |
|---|---|---:|
| hand + enum + local cert | All 2^35 = 34,359,738,368 normalized 17-site signs covered in 8,796 disjoint intervals. 456,388 strict saturated bare signs; 409,715 no first pole, 46,673 one-pole positive, none admits an independent triple of outside vertices. 32,231 admit a nonadjacent pair. Three native caps replaced by separately rebound dual mask LRATs + 815,286 physical pair entries. `all_summary.stdout`, `all_inventory.stdout`, `receipts/*stdout`. | 3,039.91 CPU-s main, checks extra |
| hand + enum | Every order39 extension needs an induced exterior C5. On 32,231 relevant signs, 32,214 disjoint-mask bipartitions + 17 actual noC5. Every order38 extension needs 2K2/P4/C4; 32,222 first-pass negatives + all nine capped words independently rerun to termination on all three shapes. Gated 37 attains the upper bound: `four/audit.stdout`, `four/nine.rows`, `five/audit.stdout`, `sharp.stdout`, `sharp37.gate`, `ralph/lanes/F/round23_witness37.g6`. Sharpness is enum, not a full LRAT. | 252.99 + 302.87 + 10.20 CPU-s (plus controls) |
| hand + local cert + enum | Complete subprefix 516577 (65,536 words): 583 physical support cuts + both LRAT consumers cover the 17 possible bare words; all 17 one-pole mask lists and physical pair/triple trace binders checked. Fresh `round23_replay.sh quick` succeeds (`clean.stdout`). Subset, not extra signing credit. | included; clean 10.23 CPU-s |
| enum | New degree-valid 34+6 observed score **212/e178**: 160,000 draws, 79,420 degree-valid including repeats, independent recount `near/score.stdout`, `near/6206451439.g6`. Lane-wide measured best remains **24/e178,179** (`round23_nearness.tsv`), not a family optimum. | 1.88 scoring CPU-s plus build |
| hand + enum + local cert | Wider **32+8**, not the whole 2^30 chart: eight triangle-free exterior vertices contain I4 or induced C5. Three fixed roots exclude both by full physical eight-addbacks (three dual-proved mask lists; 369/369 independent-four ranges). Three disjoint high-18-bit regions **232982,233198,258295** now terminal: 12,288 words = 3 fixed + 11,895 bare + 366 physical + 24 separate tail replacements. All 1,853 tail intervals / 29,463 first masks empty; `fixed_final.stdout`, `chart_handoff.stdout`, `tailaudit.stdout`, `split/`, `chart_tail/`. | 247.02 sampled CPU-s lower bound fixed production; chart scan 246.82; tails 214.07 |
| estimate / open | Broader high-12 regions 3640,3643,4035 minus the retired high-18 regions. 162-word pilot 151 bare + 5 complete physical + 6 caps. Only the first-quarter 193,496-word wave assigned; **580,486 further words unassigned**. Controls/cost/limits `front/{plan.stdout,forecast.txt,pilot.jsonl}`. | pilot 24.02 CPU-s; live production below |

Non-front lower-bound accounting ~4,419.84 CPU-s (1.228 core-h): `accounted.stdout` + chart scan + cap replacements. Fixed32 external 3-second sampling gives a lower bound, not a precise `wait4` charge. Front pilot/production separate. The scratch directory is ~60 MB including manifests and active frontier; last workspace monitor ~128.34 GB (concurrent directory changes logged). No memory kill. No stopped job observed. `dispatch.tsv` records the PID, command index, log, core, start and hard end of every prior production/follower. All earlier first/all, C5, 38-shapes, 32split, 32chart and 32tails jobs finished or were replaced; two `du` transient exits resumed only their untouched leaves. The fresh static replay and digest checks passed.

## Active jobs only

One **busy slot per row**; real detached Python supervisor / timeout PID; serial native child comes and goes. Working directory `scratch/F/r23/front/`; all run `eight_chart.py wave<SLOT>`, nice +5, CPU/wall/VM-limited. Dates below are Europe/Zurich, hard ends on Nov 23. Forecast range ~16 minutes to 2 hours from launch, hard limit 4 hours. Each `wave*.jsonl` records the physical outcomes, wall and child CPU per batch, and `wave*.meter` tracks logical bytes/cost/keys. No other F jobs live.

| Worker / timeout PID | Slot / log | Cores | Start Nov 22 | Hard end Nov 23 |
|---|---|---:|---|---|
| 2370569 / 2370562 | wave0 / `front/worker0.log` | 1 | 21:39:25 | 01:39:25 |
| 2370672 / 2370663 | wave1 / `front/worker1.log` | 1 | 21:39:25 | 01:39:25 |
| 2370765 / 2370752 | wave2 / `front/worker2.log` | 1 | 21:39:26 | 01:39:26 |
| 2371451 / 2371387 | wave3 / `front/worker3.log` | 1 | 21:39:26 | 01:39:26 |

Frozen 21:40:28 snapshot, including pilot: 27,554 attempted = 27,369 bare + 178 complete physical negatives + 7 capped; 166,104 assigned unattempted. After freezing, 21:41:37 read-only tally: 60,986 attempted, 7 caps, 132,672 assigned unattempted; all four workers live. These are checkpoint counts, not a whole-region claim. Run `cd scratch/F/r23/front && ../../../../opt/venv/bin/python -B ../../../../ralph/lanes/F/front_status.py` for the actual latest.

## Next round

1. Collect these four PIDs and the disjoint `wave*.keys` logs. Do not start another copy of an active batch. If a wave stopped mid-file, derive a fresh manifest from **unlogged** keys; a nonzero stage exit or a per-word mask/node cap remains open. Include the six pilot caps. Only publish results against an exact denominator and gate any actual 40-model via the flow.
2. Separate I4-only tails (check C5 really finished) from mask caps and other residuals. The first-mask splitter and physical witness bitsets are calibrated; e.g. `eight_tail.py` replaced the 24 earlier I4 caps, but its assertions are deliberately scoped to the old regions. Price a new tail before expanding. Do not charge an order-32 sign twice for its two arms. Do not launch the 580,486 unassigned keys unless priced and reallocated.
3. H/critic: review **sharp maximum 37 for the named 34-template** and the **12,288 wider chart words** as separate claims. Neither is a closed unrestricted distribution or involution. No need to rerun the old marked/exterior rows.
