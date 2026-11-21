# Lane B — round 3, November 21, 2026

**Open:** no new degree distribution closed and no candidate graph. Full t9<=88 census not launched. Current share is 18 cores. Work from `scratch/B` with `ulimit -v 16777216` and `PYTHONDONTWRITEBYTECODE=1`.

## Jobs

| PID | Command | Log | Cores | Start (CET) | Expected end |
|---|---|---|---|---|---|
| 1180084 | `timeout 18h prefix_pipeline.sh 16` | `scratch/B/logs/prefix_pipeline.log` | 16; solving since ~17:24 | Nov 21 17:10:35 | estimate Nov 22 00:50–02:00, cap Nov 22 11:10 |
| 3047886 | `timeout --kill-after=1m 5h bash ../../ralph/lanes/B/src/edgeup_pipeline.sh 86 work/hog_30_86.canon up86` | `scratch/B/logs/edgeup2_full86.log` | 1 solver (up to 2 during shortg/sort) | Nov 21 18:04:04 | estimate Nov 21 19:34–20:34; cap 23:04 |
| 3921182 | `timeout --kill-after=1m 6h bash ../../ralph/lanes/B/src/wait_tail7.sh 3047886 140845100 43` | `scratch/B/logs/tail7_e43.log` | 0 while up86 runs, then 1 worker (up to 2 during shortg/sort) | queued Nov 21 18:28:27 CET | estimate Nov 21 22:00–22:40 CET; cap Nov 22 00:28 |

Round 3 completed: PID 1367119 (`starlift_stage.sh`, one worker, queued
Nov 21 18:57:38, ran ~18:59–19:03 CET), with terminal count audit and SAT
sample recheck. Foreground `bench_anchor` passed; `bench_order` ended on an
e52 TIMEOUT after the exact e63 control passed. Neither benchmark is live.

Bootstrap 136395 and seed jobs 418169/453949 exited. First bootstrap union omitted minimum degree 3 for order 21; corrected by generating this branch and merging, no missing counts thereafter. Seed 418169 failed on `shortg`'s in-place default; 453949 passed after explicitly writing stdout. Do not interpret either failed run as empty. Upper seed PID 540708 completed successfully at ~17:23 with all GR T13 counts.

## Results and claims for review

### Round 3

| Label | Result | Evidence | CPU-hours |
|---|---|---|---:|
| hand | An e88 dual outside prefix and d7/e43 has at least four d6/e52 or d7/e44 roots whose neighbors all have degree ≥5. This is a joint cover, not either branch separately; no global minimum-degree-5 assertion. H/critic review requested. | `ralph/lanes/B/ANCHOR88.md` | — |
| enum / estimate | `glueanchor -S 5` and optional `-P` match all 430 rooted labelled e63 controls and exact postfiltered outputs in four dispersed eight-parent blocks each at e52 and e44. 0.373 and 3.450 CPU s/input; optional overlap prefilter did not help. Estimated ~1,140 CPU-h before sort/I/O, 63 h on 18 continuously busy cores, so no full launch and 10x target unmet. | `scratch/B/logs/anchor_bench.log`, `ralph/lanes/B/LOG.md` | ~0.07 sample |
| enum | Star lift matches independent exact labelled oracle in both directions on order-22 controls; recovers 58/60 canonical e63 graphs. Independent exhaustive verifier also finds no one-star reduction of the retained edge-critical e88 dual (which is in the d5 prefix). | `scratch/B/logs/starlift_control.log`, `scratch/B/logs/starlift_critical88_ref.log` | <0.01 |
| enum | Exact star-lift slice from 133,434 up86 e87 parents: 14,454 globally edge-critical e88 duals, all MTF-negative; audited all 15 chunks and independent SAT agreed on 24/24. All 14,454 satisfy the prefix root condition, so they do not shrink the anchor complement and are not a complete e88 result. | `scratch/B/logs/starlift_stage{,_sat,_profile}.log`, `ralph/lanes/B/LOG.md` | 0.068 including SAT |
| estimate | Largest-first cost reflection (`-R`) matches canonical e63 outputs with multiplicities, but the first eight e52 inputs capped at 120 s wall (112.75 CPU s), versus 3.74 CPU s smallest-first. Do not scale. | `scratch/B/logs/order_bench.log`, `scratch/B/logs/anchor_bench.log` | 0.032 |

### Earlier rounds

| Label | Result | Evidence under `scratch/B` unless noted | CPU-hours |
|---|---|---|---:|
| enum | All 1,118,436 R(3,7;21) graphs rebuilt; all 13 GR T12 levels exact. | `logs/r37_21_final.log`, `logs/r37_21_3.log`, `logs/bootstrap.log`, `val/r3_7_21.g6` | <0.15 |
| enum | Verified 1,800 order-30 e86 and 560 order-31 e95 HoG inputs independently for graph validity, edge counts and distinct canonical labels. | `logs/hog_30_86.log`, `logs/hog_31_95.log`, `work/hog_30_86.canon`, `work/hog_31_95.canon`, `logs/bootstrap.log` | <0.01 |
| enum | `glue`, `glue2`, `glue5` rebuild C35 and Exoo from their own dual neighbourhoods (same canonical sets: 1, 18 respectively at chosen roots). | `logs/Ramseygraphs_3_9_35_e140.selftest`, `logs/exoo39.selftest` | included in bootstrap |
| enum | Exact upstream R(3,7) counts through specified e windows at n=16–19; exact R(3,8;22,<=44), (23,<=52), (24,<=58) per GR, including all 10,326,716 e52 inputs. | `logs/seed_small_retry.log`, `logs/seed_upper52.log:470` | small 0.006; upper 0.760 |
| enum | `gluetrans`, `gluepair`, `glueres` each recover exactly the canonical 191 order-22 graphs (same files, not just counts). `gluepair` and `gluetrans` match baseline on real order-30 samples. | `work/cal22_*.g6`, `logs/cal22_*.log`, `logs/real_*` | <0.1 calibration; see LOG for sample timings |
| enum | `mtfcover` passed C35 and 12 MTF order-22 re-glues against `glue2` filtered for MTF. All 1,800 e86 inputs gave no MTF completion, 2.53 CPU s; independent SAT gluer found C35 SAT and agreed on 8/8 e86 samples. Recheck of a previously closed level, not a new closure. | `logs/mtfcover_cal.log`, `logs/mtf86_full.log`, `logs/sat_control.log`, `logs/sat86_sample.log` | <0.003 |
| hand | Completeness of MTF cover branching and scope of results. | `ralph/lanes/B/LOG.md` | — |
| enum | Sampled 40 distinct e88 duals generated in the d5 calibration. No MTF completion; independent SAT agreed on 12/12. Not a full e88 result. | `logs/mtf88_sample.log`, `logs/sat88_sample.log` | <0.002 |
| estimate | Generation, not final scan, still controls e88: uniform sample of 96 from the exact n23,e52 family took 49.03 vs 63.25 CPU s (1.29x) with matching output. At 0.511 s/input, the 10,326,716-input stage alone projects ~1,465 CPU-hours = 73 h at 20 fully busy cores. No full launch; need <=0.27 s/input for practical completion. 10x target **not met** for generation. | `logs/uniform_23_52_gluetrans.log`, `logs/uniform_23_52_glue5.log`, `ralph/lanes/B/LOG.md` | sample 0.031 |
| enum | Exact two-edge slice from all e86 duals: 133,434 canonical e87 parents and 4,751,963 distinct e88 duals. Pilot 98,408 slice inputs, zero MTF outputs and 24/24 independent SAT agreement; full slice scan still running. | `logs/edgeup2_full86.log`, `logs/edgeup2_pilot.log`, `logs/edgeup2_pilot_sat.log` | generation 0.023; pilot + SAT 0.032 |
| cert | Not every e88 dual can be generated by edge addition from e87: explicit (3,9;30,88) graph has checked independent 9-set witnesses after all 88 one-edge deletions. This is a counterexample to the shortcut, not an order-40 graph. | `ralph/lanes/B/critical88.json`, `ralph/lanes/B/src/critical_witness.py`, `logs/critical88.log` | <0.001 |
| enum | `gluecheap` exactly matches all 191 canonical order-22 graphs and all 162 labelled outputs on the 96-parent e52 sample, taking 44.37 CPU s versus 49.03 (`gluetrans`) and 63.25 (`glue5`). `g84` profile filter recovers the independently filtered 24 of 60 e63 controls; early triple propagation matched small controls but was 4.15x slower on 24 e52 inputs. | `logs/cal22_*`, `logs/gluecheap_23_52.log`, `logs/triple_3_*.log`, `ralph/lanes/B/LOG.md` | sample 0.012 cheap; 0.016 triple |
| estimate | Dispersed e52 paired blocks: 0.555 CPU s/input baseline, 0.491 optimized, 0.468 outside-prefix only (ranges 0.456–0.676, 0.419–0.578, 0.383–0.541). At least ~1,340 CPU-h for e52 and ~82 CPU-h for e44 before e43 and final sorting/scanning (~79 h even at 18 saturated cores). On 32 dispersed e44 parents, exact raw equality and zero outside-prefix outputs; sample alone is not exclusion. | `logs/paired_speed_r2.log`, `ralph/lanes/B/LOG.md` | see paired log |

## Next

1. Prefix PID 1180084 uses (5:3,6:3,7:1), sufficient for <=87 by exact `tcheck.py`; runs those seeds with output cap 88, so its e88 result is **partial only**. Require e86/e87 counts 1800/147335 and exact HoG canon equality at e86. At 19:05 CET, d5 complete (132,817, 28,497.87 CPU s) and d6 483/2847 chunks, recent ~7–8 chunks/min. Confirm by SAT on a dispersed e88 sample once the census file appears.
2. Require `src/audit_e88_scans.sh up86` after terminal (at 19:05 CET, 2861/4641 chunks, zero so far). `src/edgeup_tail87.sh` is staged, **not launched**: after exact completeness checks and the up86 scan, add from the 13,901 e87 parents outside the existing slice and scan only the new e88 graphs. Complete only for duals admitting at least one Ramsey-preserving edge deletion. Cannot cover `critical88.json`.
3. Monitor queued e43 PID 3921182. Run `src/audit_e88_scans.sh e43` at terminal. The result applies only to the d7,e43 branch outside the prefix. Paired e43 sample projected 2.18 CPU-h for gluing plus final sorting/scan. Read `ANCHOR88.md` when developing a larger generation prune; do not scale either e52/e44 at the current estimated cost. t9<=89 and t8 larger levels remain unbudgeted.
4. Use G's checked round-2 threshold table: an MTF e88 exclusion would close **20 additional** distributions on that baseline (434 nonregular + R left). Reconcile overlaps if G's separate round-3 floor-120 result is accepted. No new distribution closure this turn. MTF-only exclusion is not an all-graphs t9 statement.
