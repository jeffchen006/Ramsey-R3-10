# Lane C — round 7, 2026-11-21/22

R(3,10), Case R, R(6), and global `f*=9` remain **open**. No candidate.
`J` is the codegree-six graph, `f*` the minimum wing cross count among
those pairs. P2 means an isolated J edge, not an arm of a P3. Pair and
three-root residues differ. For `(12,14)` the order-19 and order-21
windows have private core orders 12 and 14, with no shared core U.

## Results and claims for H / critic

| Label | Result | Evidence (lane-relative unless absolute) | CPU-h |
|---|---|---|---:|
| hand | Whole-neighbourhood lists for one opposite vertex enforce exact deficit, triangle-free choice and all appropriate independent-9 requests; pairs enforce disjoint choices if adjacent and the independent-8 requests otherwise. Arc deletion preserves completion. Exact U0 boundary formula and safe 64-choice deferral. | `proofs/p2_simultaneous_incidence.md`, `p2_incidence.cpp`, `p2_request_cache.hpp` | — |
| hand + enum, pending critic | **In global R(6), f*=9, (12,14), the smaller private K12 must have 16 ≤ e(K12) ≤ 21.** Four e23/24 profiles empty (full census and disjoint high-edge replay); all e15 and e22 profiles among 11 exhaustive streaming profiles. 317,795,664/317,795,664 tested, no passes or deferrals. The remaining 24 of 39 profiles stay open, as do `(12,13),(13,13)`. Not an `X` or P3 bound. | `ROUND7_REPLAY.{md,sha256}`, `scratch/C/p2r7-census/{universe,high-full,run-index,run-totals,smallest-audit}.log` | 0.155 join, 0.004 direct replay |
| enum | All 116,792 K12 classes independently reproduced by geng/pickg/labelg. Two terminal gluer subsets produce 2,121,010 raw windows, 1,988,646 rooted canonical H19s, all accepted by independent pickg degree-free triangle/alpha screen. 39 projected profiles, 35 represented; 369,169,500,080 raw maps before any cross test. Not a completion count. | `scratch/C/p2r7-census/{k12-audit,final-counts,count,universe}.log`, `profiles.tsv`; `ROUND7_REPLAY.md` | 0.372 gen + <0.02 check |
| enum / estimate, pilot only | 7/7 planted C22 pairs pass, including their actual row choices. Direct and cached filters agree on 16,080 mapped pilot requests, removing 454 old-filter survivors. Cached-only 166,128 and 1,309,452 samples have no survivors. C-free relaxation deferred every input tested; looser wing counts were slower and retained 1,577/166,128. Three hot shards suggest 1.5–3.6 microseconds per map; entire cover ~208 CPU-h at broader 2.03 microseconds, not a bound. | `ROUND7_REPLAY.md`, `scratch/C/p2r7-incidence-{control,audit,audit-other,arc-wide,arc-large,loose}.log`, `scratch/C/p2r7-hot/` | <0.015 |
| confirmed round 6 | Global R(6), f*=9 rules out `(12,12)` wing union sizes, at most one U vertex. Full 1,134 CakeLRAT checks and replay; frozen bundle unchanged. | `ROUND6_REPLAY.{md,sha256}`, `ralph/critic/round_006.md`, claim C-024 | prior |
| previously confirmed | R(7) excluded; R(6) has no P4. P3 diagonal five residue e≤61; diagonals three/four e≤63. If f*≥8 every P3 has arms both 8 and diagonal 3 or 4. In global f*=9 J is a nonempty matching. No inference to P2 residue edge counts. | `ralph/critic/round_{001,003,004,005}.md`, `ROUND5_REPLAY.md` | prior |
| previously confirmed | Isolated f8/e80 has at most one degree-three vertex and when one exists the anchored X' has e(X')≤64. Full wings have 10–12 singleton C supports and excess ≤2; global f*=9 excludes wing siblings in J and each wing covers ≥12 X vertices. | `ROUND4_REPLAY.md`, `proofs/p2_full_wings.md`, `ralph/critic/round_{004,005}.md` | prior |

## Jobs

None. Full command, limit, start/end, working directory and log records
in `scratch/C/p2r7-census/{jobs,cover-jobs,run-jobs}.tsv`.

| PIDs (timeout/initial worker) | Allocation | Terminal |
|---|---|---|
| 3860048/3860059, 3860049/3860061 | 1 each, K12 generator shards, Nov 21 23:41:15, hard end Nov 22 00:16:15 | Both finished 58,396 cores; raw logs/counts retained. |
| 123906/123960, 123907/123954, 123908/123961 | 1 each, staging, Nov 21 23:56:17, hard end Nov 22 00:16:17 | Guard refused all three before the join (wrong multiplier had been passed as limit); no result. |
| 141740/141775, 141741/141774, 141742/141768 | 1 each, exact bounded profiles, Nov 21 23:56:55, hard end Nov 22 00:16:55 | All 11 done, last at 00:01:30; indexed and validated. |

## Next

1. H/critic: audit the scoped e(K12) bound and 15/39 profile reductions;
   `ROUND7_REPLAY.md` separates code, input coverage and absence claims.
   Formalize the pure arc-deletion preservation lemma if useful.
2. Do not materialize the raw join. Remaining 24 profiles have
   368,851,704,416 raw maps; top three alone have 188B. Try factoring
   the C-map permutations into bitmap requests keyed by paired support
   types, or get critic-approved cumulative CPU allocation before a
   full sharded stream. The 11 terminal profiles cover only ~0.086% of
   raw maps; three hot-profile samples are **not** exclusions.
3. Preserve H19/H20/H21 distinction. The appendix gives the U1 alpha
   formula for `(12,13)` but it has not been implemented or calibrated;
   `(13,13)` can use the U0 cache but still needs H20/K13 catalogues.
   The earlier aggregate capacity test and loose wing grouping should
   not be rerun unchanged. Isolated anchored f8/e80 e64 (236 fixed
   keys) remains a separately bounded option, not P3.
