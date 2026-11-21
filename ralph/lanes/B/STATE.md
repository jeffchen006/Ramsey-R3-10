# Lane B — round 5, November 21, 2026

**Round 5:** global degree-seven floor **108** for MTF, submitted to the
critic (cert: accepted G-011 plus complete GR T14 level 107 and checked
clique/LRAT cover). This subsumes the separate direct exclusion of
`e=162 (n6,n7,n8,n9)=(0,2,32,6)`. Neither uses t8/t9 floors. No candidate
graph, and full t9<=88 census not launched. Share is 18 cores.
Work from `scratch/B` with `ulimit -v 16777216` and `PYTHONDONTWRITEBYTECODE=1`.

A complete U88 exclusion would cut **12** more distributions on the
checked round-4 baseline. The direct e162 cut, considered alone, reduces
that to 11. With floor 108 and G's new n6 bound the count must be
recomputed; requested from G/H, do not add reductions blindly. Full
t9<=88 is still open.

## Jobs

| PID | Command | Log | Cores | Start (CET) | Expected end |
|---|---|---|---|---|---|
| 1180084 | `timeout 18h prefix_pipeline.sh 16` | `scratch/B/logs/prefix_pipeline.log` | 16; solving since ~17:24 | Nov 21 17:10:35 | estimate Nov 22 00:50–02:00, cap Nov 22 11:10 |
| 3921182 | `timeout --kill-after=1m 6h bash ../../ralph/lanes/B/src/wait_tail7.sh 3047886 140845100 43` | `scratch/B/logs/tail7_e43.log` | 1 worker (up to 2 during shortg/sort) | queued Nov 21 18:28:27, computing since 19:42 CET | revised est. Nov 21 22:15–23:05 CET; 903/399 CPU-s outliers among 48 chunks; cap Nov 22 00:28 |
| 2576750 | `timeout --kill-after=1m 8h bash ../../ralph/lanes/B/src/wait_tail87_checkpoint.sh 3921182 140991398` | `scratch/B/logs/up87tail_checkpoint.log` | 0 awaiting e43 worker slot; then 1 worker (up to 2 for shortg/sort) | queued Nov 21 20:40:32 CET | 25–55 min after e43 exits; cap Nov 22 04:40 CET |

Round 4: PID 3047886 (`edgeup_pipeline.sh 86 … up86`) ended successfully before 19:42. 392466 was retired at 20:40 while still waiting (no compute lost); checkpoint input is ready, so 2576750 queues behind e43 for core headroom instead of waiting for the entire prefix. All foreground benchmarks finished. Full e88 remains open. Round 3 completed: PID 1367119 (`starlift_stage.sh`, one worker, queued
Nov 21 18:57:38, ran ~18:59–19:03 CET), with terminal count audit and SAT
sample recheck. Foreground `bench_anchor` passed; `bench_order` ended on an
e52 TIMEOUT after the exact e63 control passed. Neither benchmark is live.

Bootstrap 136395 and seed jobs 418169/453949 exited. First bootstrap union omitted minimum degree 3 for order 21; corrected by generating this branch and merging, no missing counts thereafter. Seed 418169 failed on `shortg`'s in-place default; 453949 passed after explicitly writing stdout. Do not interpret either failed run as empty. Upper seed PID 540708 completed successfully at ~17:23 with all GR T13 counts.

Round 5 foreground gluing, proof generation/replay and e108 pilot jobs all
finished; no additional detached workers. At 21:49 CET, e43 has 39/48
completed generation chunks (0 outputs so far, one worker on chunk 39),
prefix is still in d6, tail87 still queued behind e43. No terminal e88
slice result to audit this round. The 16+2 solver peak was preserved.

## Results and claims for review

### Round 5

| Label | Result | Evidence | CPU-hours |
|---|---|---|---:|
| cert (MTF; pending critic) | d7 residue floor **108**, no t8/t9 or profile premise. Complete 234,681 GR classes at e107; 231,455 checked eight-demand cliques plus 3,226 necessary CNFs pinned by seven-demand row normalization. All 3,226 LRATs pass both checkers and byte-identical CNF/hash replay. Combine with G-011. | `FLOOR7_108.md`, `FLOOR7_108.sha256`, `src/replay_floor7_108.sh`, `scratch/B/logs/e107_floor108_replay.log` | ~0.14 new proof and replay, excluding census/gluer |
| enum / open | Exact e108 reducible slice 2,102,271 of 2,104,151 GR classes (9,185,929 raw children of all e107s). Audited edge/order/alpha and sorted canonical distinctness. Of 1,880 deletion-critical types, an 8,192-parent swap pilot recovered 7, independently validated as critical; 1,873 missing. No e108 closure. | `scratch/B/logs/{e108_r5_reducible,e108_r5_followup,e108_r5_critical_audit}.log` | ~0.04 |
| estimate | e108 pilot: 0/1,024 MTF glues, 979 checked demand cliques, 45/45 pinned dual LRATs. Project ~0.82 CPU-h whole e108 gluer or ~1.7 CPU-h pinned production plus clique checks/replay, biased toward reducible inputs; a full first critical-swap pass projects ~13 min on one busy slot before final audit, with no reachability guarantee. | `scratch/B/logs/{e108_r5_pilot,e108_r5_followup}.log` | <0.01 pilot |
| enum | Complete untuned independent gluing at e107: 234,681 inputs, zero completions in 355.18 CPU-s. Independent SAT gluer agreed on 64/64 dispersed inputs after positive D5/K6 control. No broader e level inference. | `scratch/B/logs/{e107_fullglue,e107_sat_control,e107_sat64}.log` | ~0.103 |
| cert (conditional; pending critic) | e162 `(0,2,32,6)` impossible in MTF, using accepted G-011 (floor 107) and GR T14; neither gluing floor is a premise. Complete, valid, pairwise nonisomorphic census of 234,681 e107 roots, one checked distance-3 pair per root incompatible with both attachment sizes 6 and 7. Independent SAT verifies 64/64 pairs. | `E162_E107.md`, `E162_E107.sha256`, `src/replay_e162_e107.sh`, `scratch/B/logs/e162_r5_complete_replay.log` | ~0.05 including catalogue |
| enum | Reused G's 234,352 e107 roots, added 305 by critical one-edge swap and 24 by applying the same operation to the 305. Exhaustive small labelled calibration (12 cases). Exact count, graph-validity audit, and independent Traces distinctness; move reachability not assumed. | `scratch/B/logs/{e107_lateral_cal,e107_lateral_full,e107_lateral2}.log` | ~0.027 |
| enum | Profile-pinned gluer passed 12 order-22 controls plus a forged histogram, rejected 234,352 original e107 inputs in 54.54 CPU-s. The independent pair proof covers the strict complete catalogue instead. | `scratch/B/logs/{profile_r5_cal,row_support_cal,e162_r5_known}.log` | ~0.018 |

### Round 4

| Label | Result | Evidence | CPU-hours |
|---|---|---|---:|
| enum (SAT sample cross-check) | Exact up86 two-addition slice: 133,434 e87 parents, 4,751,963 distinct e88 duals, 4,641 completed chunks, 0 MTF completions. Independent SAT agrees 32/32 on a fresh uniform sample. Every up86 e88 dual has a d5/e<=58 or d6/e<=51 root, so the entire slice is in intended prefix scope. Neither all e88 duals nor all-graphs order-40 gluing. | `scratch/B/logs/{edgeup2_full86,up86_audit_r4,up86_r4_sat_sample,profile_census_r4}.log` | ~1.46 |
| enum | Early prefix checkpoint matches HoG e86 canonically (1,800). Its 147,334 e87 graphs plus one from up86 give exactly the reference 147,335 e87 count. Direct branch-and-bound checked triangle-freeness and alpha<=8 for all, independent Python checker passed 64/64, and the union is strictly sorted and hash-bound. The disjoint tail is ready without waiting for full prefix. No e88 closure. | `scratch/B/logs/{prefix_checkpoint_r4,prefix_checkpoint_r4_full_valid,prefix_checkpoint_r4_valid}.log`, `scratch/B/logs/prefix_checkpoint_r4.sha256` | 0.020 |
| enum | Disjoint tail pipeline calibrated exactly: 11 prior + 4 tail order-16/e21 parents, 130 prior + 29 novel order-16/e22 descendants, exact complement of 42 edge-critical graphs. Bound chunk hashes pass 7-input positive and reject reordered input. | `scratch/B/logs/{tail_accounting_control,chunk_bind_r4}.log`, `ralph/lanes/B/src/edgeup_tail87.sh` | <0.001 |
| hand | For e162 `(0,0,36,4)` the four degree-nine vertices induce C4. For e162 `(0,2,32,6)`, the degree-seven pair is adjacent, both degree-seven residues have e107, and the degree-nine induced subgraph is one of four explicit shapes. Neither is a distribution exclusion. | `ralph/lanes/B/CYCLE162.md`, `scratch/B/logs/cycle162_shape.log` | — |
| estimate | All 13 U88 distributions retain a viable relaxed degree-nine root profile, even imposing outer floors, MTF private-cell counts and no prefix/e43 roots in the residue. C35 control has exact feasible row substitution. Incidence LP and signature grouping do not reduce the e52/e44 cover. | `scratch/B/logs/{root_projection_r4,anchor_profiles,signature_r4}.log` | <0.01 |
| enum / estimate | Best e52 holdout is 0.298 vs 0.379 CPU-s/parent (128 held-out parents; `-DCOLMIN=99`); best e44 pilot is 1.852 vs 3.628 (32 parents; also `-DBITPLANE_ATTACHMENTS`). All controls match, but generation alone projects ~893 CPU-h or 49.6 h on 18 cores, before final sort/scan. No full launch and no 10x gain. | `scratch/B/logs/{coloring52_r4,coloring44_r4,holdout_r4}.log`, `ralph/lanes/B/LOG.md` | ~0.5 all pilots |

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
| enum | Early up86 pilot: 98,408 slice inputs, zero MTF outputs and 24/24 independent SAT agreement. Superseded for coverage by the round-4 terminal scan. | `logs/edgeup2_pilot.log`, `logs/edgeup2_pilot_sat.log` | 0.032 |
| cert | Not every e88 dual can be generated by edge addition from e87: explicit (3,9;30,88) graph has checked independent 9-set witnesses after all 88 one-edge deletions. This is a counterexample to the shortcut, not an order-40 graph. | `ralph/lanes/B/critical88.json`, `ralph/lanes/B/src/critical_witness.py`, `logs/critical88.log` | <0.001 |
| enum | `gluecheap` exactly matches all 191 canonical order-22 graphs and all 162 labelled outputs on the 96-parent e52 sample, taking 44.37 CPU s versus 49.03 (`gluetrans`) and 63.25 (`glue5`). `g84` profile filter recovers the independently filtered 24 of 60 e63 controls; early triple propagation matched small controls but was 4.15x slower on 24 e52 inputs. | `logs/cal22_*`, `logs/gluecheap_23_52.log`, `logs/triple_3_*.log`, `ralph/lanes/B/LOG.md` | sample 0.012 cheap; 0.016 triple |
| estimate | Dispersed e52 paired blocks: 0.555 CPU s/input baseline, 0.491 optimized, 0.468 outside-prefix only (ranges 0.456–0.676, 0.419–0.578, 0.383–0.541). At least ~1,340 CPU-h for e52 and ~82 CPU-h for e44 before e43 and final sorting/scanning (~79 h even at 18 saturated cores). On 32 dispersed e44 parents, exact raw equality and zero outside-prefix outputs; sample alone is not exclusion. | `logs/paired_speed_r2.log`, `ralph/lanes/B/LOG.md` | see paired log |

## Next

0. Ask critic/A to audit `FLOOR7_108.md` and replay; G/H to count actual
   distribution updates including overlaps with G's round-5 n6 reduction.
   The separate e162 certificate is not an extra cut once floor 108 is used.
1. Prefix PID 1180084 uses (5:3,6:3,7:1), sufficient for <=87 by exact `tcheck.py`; runs with output cap 88, so its e88 result is **partial only**. Require the full run's own e86/e87 checks and compare its e87 canonical file byte-for-byte to `scratch/B/work/prefix_checkpoint_r4/union87.g6`. Confirm terminal counts and SAT on a dispersed e88 sample.
2. Watch PID 2576750 (`wait_tail87_checkpoint.sh`): after e43 releases its slot it rechecks the exact lower-level checkpoint, runs `edgeup_tail87.sh` on the other 13,901 parents, checks the exact e87 merge and the e88 partition, and audits ordered input hashes for every MTF chunk. Read actual `output N`, not merely the terminal marker. Once complete this accounts for reducible e88 duals, not the edge-critical complement (e.g. `critical88.json`).
3. Monitor e43 PID 3921182. Run `src/audit_e88_scans.sh e43` at terminal. The result applies only to the d7,e43 branch outside the prefix. Paired e43 sample projected 2.18 CPU-h for gluing plus final sorting/scan. Do not scale e52/e44 without a material new bound; no more star-lift. t9<=89 and t8 larger levels remain unbudgeted.
4. If approved and inside core cap, e108 is a materially cheaper alternative:
   begin from `scratch/B/work/e108_r5/lateral.pilot.union.g6` (2,102,278 keys),
   with exact reachable first swap pass from `reducible.g6`; follow only
   newly found keys. The 12m inner lateral cap in `e107_lateral_pass.sh`
   is tight at e108; set a justified larger bounded cap before launch.
   Require strict GR count 2,104,151, direct validity and independent
   canonical count before an e108 floor attempt. Gluing/pinned proofs
   must then cover every class, not just the reducible slice. Main e88
   jobs and resource caps take precedence.
