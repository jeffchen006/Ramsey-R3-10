# Lane A state

Round 9, November 22, 2026. Share 4; no live or stopped jobs.
No order-40 candidate, whole-distribution exclusion, or Case R closure.
Round 9 evidence: `ROUND9_REPLAY.md`, `scratch/A/strip9/round9.freeze.sha256`.
Round 1–8 history: `LOG.md`; use the historical tracked G sources when
checking the old R8 input manifest (see variant provenance below).

## Jobs

The detached jobs below all ran in `scratch/A/strip9`. Times host local.

| timeout PID / worker PID | Command | Log and timing | Cores | Start–end |
|---|---|---|---:|---|
| 634622 / 634629 | `run_mixed26_audit.sh --fast-hash --shard 0 3` | `mixed.hash.0.{log,time}` | 1 | 01:59:48–02:06:16 complete |
| 634623 / 634630 | `run_mixed26_audit.sh --fast-hash --shard 1 3` | `mixed.hash.1.{log,time}` | 1 | 01:59:48–02:05:26 complete |
| 634624 / 634631 | `run_mixed26_audit.sh --fast-hash --shard 2 3` | `mixed.hash.2.{log,time}` | 1 | 01:59:48–02:05:34 complete |

All foreground controls and the 162 dual replays finished; G's completed
production jobs are not A's. The measured estimate before launch was
883 CPU-s at 3 cores, in `mixed.terminal.estimate` (actual 840.13 CPU-s).

## Results / claims

| Label | Scope and result | Evidence | A CPU-h |
|---|---|---|---:|
| hand + enum + cert, pending critic | At `(2,7,4,27)` only with mixed path/leaf and matching/incident or path/middle strips, **noncross d8 B pivot at j=3 and δ(T)=3**. Independently: 191 cores -> 2,712,471 byte-identical labelled lifts -> 2,111 exact marks -> 1,767 colour orbits -> 7,166 exact ordered roles. Both orientations, four structural addbacks and four occupied-hole negatives pass; previous j4 5,179 roles reproduced. All 7,166 G dual-checked, all independent pin maps/CNF/compressed-trace digests match, and A dual replayed 16 pilot traces. | `ROUND9_REPLAY.md`, `scratch/A/strip9/{mixed.j3.source.log,mixed.terminal.tsv,mixed.union.log,mixed.G.join.log,mixed.pilot.replay.log}` | 0.233 hash + 0.025 controls/source |
| hand + enum + cert, pending critic | Same mixed pin, **noncross d9 B pivot at j=5**, no δ(T) restriction. Both holes retained on B; cut 5/1/3. Exactly 162 matching and zero middle roles over the exact 1,988-mark envelope, both orientations. All 162 independent pin/CNF/trace digests and dual LRATs pass. | `scratch/A/strip9/{mixedfull.source.log,mixedfull.terminal.tsv,mixedfull.G.join.log,mixedfull.dual.union.log}` | 0.015 |
| cert provenance only | c1/δ2: both terminal indexes cover the same 17,194 keys: 17,152 identical traces, ten eager-pilot/eager-retry paths at the same CNF, 32 G `--eager 0` vs A `--eager 10000` distinct CNFs, all `--cut-budget`. Both variants of the 32 were separately dual checked by the critic, not cross-used. No new proof run. | `crosswalk_c1_variants.py`, `scratch/A/strip9/c1.variants.tsv`, `scratch/critic/r8/G/{differences,primary.check,eager.check}` | <0.001 |
| hand + enum, no closure | Joint pure caps are redundant at δ(T)≥4: noncross leaf codegree `7-d_T`, full codegree `7-d_T` plus at most one. At δ=3 only degree-three anchors can bind. C5 plus pure structural cap-positive and overflow-negative controls agree with G's CNF. Zero standalone removals on 205/260 respective pilot rows. | `audit_joint_pivots.py`, `scratch/A/strip9/joint.audit.log` | <0.001 |
| hand + enum/estimate, no closure | Conditional two-root source for pure order26 δ4: 604,645 order21 cores with a second root of degree 3/4, C5 double gluing recovers C13, lookup confirms 258/260 held-out marks (two not eligible). Matched addback forecast only ~1.5× better (7.45 vs 11.15 CPU-h); no proof-stage reduction demonstrated. | `profile_two_root_residue.py`, `ROUND9_REPLAY.md`, `scratch/A/strip9/{S21.full.log,S21.heldout.log,S21.matched.graft.time,S21.baseline.graft.time}` | 0.011 |

## Next

- Critic/H: record only these two mixed scopes if accepted. Mixed d8
  j≤2 and j=3 other δ, and d9 j≤4 remain outside them. Neither pin is
  a whole-distribution closure. Do not repeat the terminal replays.
- Do not scale the pure joint caps, two-root gluer or previous boundary
  arc/projection pilots unchanged. Need a structural filter that prevents
  large numbers of proof jobs, not merely another modest source shrink.
- If needed, obtain the two old G source versions via `git show
  eb5b11c:ralph/lanes/G/<file>`; both recorded R8 digests match that
  revision. The A R8 checker itself remains byte-identical.
- R(7) has no new pilot this round per critic direction; do not reopen
  measured old cube routes without a materially different split.
