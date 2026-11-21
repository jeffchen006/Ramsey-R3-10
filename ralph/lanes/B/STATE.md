# Lane B — round 1, November 21, 2026

**Open:** no new degree distribution closed and no candidate graph. Full t9<=88 census not launched; the lower-count calibration and a partial e88 search are running. First round had no critic directives. Share is 20 cores. Work from `scratch/B` with `ulimit -v 16777216` and `PYTHONDONTWRITEBYTECODE=1`.

## Jobs

| PID | Command | Log | Cores | Start (CET) | Expected end |
|---|---|---|---|---|---|
| 1180084 | `timeout 18h prefix_pipeline.sh 16` | `scratch/B/logs/prefix_pipeline.log` | 16; solving since ~17:24 | Nov 21 17:10:35 | estimate Nov 22 00:24–03:24, cap Nov 22 11:10 |

Bootstrap 136395 and seed jobs 418169/453949 exited. First bootstrap union omitted minimum degree 3 for order 21; corrected by generating this branch and merging, no missing counts thereafter. Seed 418169 failed on `shortg`'s in-place default; 453949 passed after explicitly writing stdout. Do not interpret either failed run as empty. Upper seed PID 540708 completed successfully at ~17:23 with all GR T13 counts. No other detached solver jobs.

## Results and claims for review

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

## Next

1. Prefix PID 1180084 uses (5:3,6:3,7:1), sufficient for <=87 by exact `tcheck.py`; runs those seeds with output cap 88, so its e88 result is **partial only**. Require level 86/87 counts 1800/147335 and exact HoG canonical set equality at e86 before any inference. Monitor progress and recompute ETA from completed worker CPU samples. e88 MTF scan can find a witness; zero does not close e88. `scan_mtf.py` sends nonempty output to standard flow candidate path. Use own independent SAT on a dispersed e88 sample after file appears.
2. Seek a sharper prune for the missing e52 and e43–44 inputs. `gluegroup` ran 175.08 CPU s versus 86.10 s baseline on three parents; do not scale it. Do not run full `n30.py 88 --workers ...` unless updated measurement fits the remaining run. If a validated new gluer achieves the needed rate, reuse prefix chunk products where safe. A uniform sample tool is at `src/sample_levels.py`.
3. MTF-only exclusion is sufficient for the MTF distribution split, not for the original non-MTF universal t9 statement. Ask critic to review `mtfcover` completeness and any change of lane share if the full run fits only with reallocation.
