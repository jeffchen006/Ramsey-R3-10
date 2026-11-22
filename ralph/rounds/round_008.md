# Round 8

Began 2026-11-22T00:38:05; ended 2026-11-22T01:45:20.

## Flow checks
```json
{
 "round": 8,
 "verified_340_graphs": [],
 "graph_files_checked": [],
 "solver_processes_now": 0,
 "per_lane_now": {},
 "rss_gb_now": 0,
 "core_cap": 80,
 "killed_over_caps": [],
 "lane_turns": {
  "A": "ok",
  "B": "ok",
  "C": "ok",
  "D": "ok",
  "E": "ok",
  "F": "ok",
  "G": "ok",
  "H": "ok"
 },
 "lanes_failing_in_a_row": {},
 "critic_turn": "ok"
}
```

## Lane A: Toolchain and certified SAT (the 99 open R(7) cubes) (ok)
Round 8 independently audited two certificate-backed exclusions, pending critic review:

- **Both strips path/leaf:** all 17,194 marked cases excluded at the two e168 low-\(n_8\) profiles when the centres have codegree 1 and the retained window has minimum degree 2.
- **Mixed strips:** all 5,179 marked roles excluded at \((2,7,4,27)\) when a noncross degree-eight pivot has codegree 4 with the path/leaf centre.

Lane G checked every LRAT with both checkers. Lane A independently matched both exact covers and every CNF and proof hash, and reran both checkers on sampled proofs. Evidence: `ralph/lanes/A/ROUND8_REPLAY.md:104`.

No lane A jobs remain. Neither degree distribution is closed, and \(R(3,10)\) remains undecided. The next gap is higher-minimum-degree windows and smaller mixed codegrees.

## Lane B: Gluing (t9 <= 88, then a faster gluer) (ok)
- **e88 prefix (enum):** Zero MTF completions on 5,873,187 inputs, including 153,612 edge-critical keys. All 5,736 input chunks passed digest replay; an independent SAT spot check rejected 24/24 critical keys. The e86/e87 files matched the checkpoint byte-for-byte. `ralph/lanes/B/ROUND8_REPLAY.md:96`
- **e108 scout tranche (cert, pending critic):** Excluded all 1,142 supplied keys at degree-seven MTF roots using 761 checked demand cliques and 381 dual-verified LRATs. The census is still 124 classes short. A calibrated 512-host pilot found no new keys and was stopped. `ralph/lanes/B/ROUND8_REPLAY.md:44`
- **Jobs:** PID `1180084` exited successfully. No lane B jobs remain. `ralph/lanes/B/STATE.md:29`
- **Next:** Critic review of both evidence bundles. The outside-prefix d6/e52 or d7/e44 critical complement and all ten U88 keys remain open. No new floor or Ramsey verdict.

## Lane C: Theory for the 9-regular case R (ok)
**Round 8 — Lane C.** Case R and \(R(3,10)\) remain open. No candidate graph or live jobs.

- **Hand + enum:** Independently replayed the four-blocker argument for two diagonal-four P3 layouts with 8/8 arms. It excludes exactly 90 indexed layout/residue pairs; all 330 other pairs remain open.
- **Hand + enum:** Integer replay excludes 34 of 105 compatible zero-mask patterns. Every surviving layout requires one or two vertices that miss all four common neighbours; two layouts require exactly two.
- **Enum / estimate:** The P2 pre-join index matched the direct check on 4,910,040 held-out requests. It rejected 97.6% early but delivered only **1.51×** net speedup. Do not scale it to the full join.
- **Handoff:** Frozen evidence is in `ralph/lanes/C/ROUND8_REPLAY.md:1`. Request critic and Lane H review of the 34 integer witnesses; next, test a bounded six-set join on one surviving P3 layout.

## Lane D: New SAT encodings and splits for case R (ok)
**R(3) remains open.** No graph candidate was found. Lane D has no running solver jobs.

- **Hand, pending audit:** Every hypothetical R(3) graph has an edge kernel containing an induced six-vertex path. If a six-vertex path closes into a cycle, another edge kernel contains an induced seven-vertex path. Proof: `ralph/lanes/D/PATH_ROOT.md:15`.
- **Hand + enum:** If the longest simple path in any edge kernel has **exactly six vertices**, only three boundary profiles remain: **2298, 2424, 2431**. Independent enumeration found 2,434 profiles; direct path checks left 22, and 19 projected CNF refutations replayed with both LRAT checkers. This is not a Sec. 7 closure, and the three-profile restriction does not apply to longer paths. Receipts: `scratch/D/punct8/receipts.tsv:1`.
- **Calibration:** Both punctured-root encodings recovered all three C22 cap-three classes and all 34 marked classes. All four matched target pilots hit their 60-CPU-second limits without a decision.
- **Next:** Audit the structural proof and the dependency behind the nineteenth refutation, then test joint attachment constraints on the remaining profiles. Handoff: `ralph/lanes/D/STATE.md:1`.

## Lane E: Automorphisms (the open (p, f) cases) (ok)
**Lane E, round 8:** Excluded mixed-profile core ``G?bF`w`` only, under the existing \(f=32,\ t=4,\ \delta(W)\ge2,\ e(W)=11\) all-graph premises. Status: **hand + enum + cert**, pending critic review. This does not settle \(R(3,10)\).

- Independently matched all 49,330 projections and 556,561 support orbits. Marked-window compatibility and shared edge propagation cut the proof queue from 40,880 to 5,488 to 932.
- All 932 proofs passed CakeLRAT against regenerated, byte-identical CNFs. The freeze manifest rehash passed.
- No live lane E jobs and no candidate graph. Sixteen mixed cores remain; next, sample core 4 or 12 before scaling.
- H/critic: please audit the shared-propagation invariant and residual IDs in `ralph/lanes/E/shared74_round8.md:1`. The frozen evidence is in `scratch/E/r8_shared/freeze.final.2.sha256:1`.

## Lane F: Constructions: search for a (3,10,40)-graph (ok)
**Lane F, round 8 — hand + enum + cert, pending critic review.** No `(3,10,40)` graph can have a fixed-point-free involution whose full unsigned quotient admits a 20-cycle on its fibers. The cycle need not be a symmetry of the graph itself. Other involutions and regular case R remain open.

- **Evidence:** 327 legal degree profiles reduced to 99 representatives. All 99 passed an independent check of the encoding and both LRAT proof checkers, with no capped or missing cases. The order-38 positive control passed the gate.
- **Nearness:** Two matched scores improved, 644→504 and 1048→632. Lane F’s overall best remains 24 independent 10-sets. No candidate was submitted.
- **Handoff:** All 16 jobs finished; no PIDs or cores remain active. H and the critic were asked to replay `ralph/lanes/F/ROUND8.md:86`. No further search on this quotient family is warranted.

## Lane G: Near-regular degree distributions N(e) (ok)
**Lane G, round 8:** No order-40 candidate or full degree-distribution closure. **278 near-regular distributions plus case R remain open.**

- **cert:** Bound all 17,194 dual-checked LRATs for the two \(e=168\) profiles with both strips path/leaf, centre codegree 1, and paired-window minimum degree 2. `ralph/lanes/G/ROUND8_REPLAY.md:8`
- **cert:** Bound all 5,179 mixed-role LRATs for profile `(2,7,4,27)` when an opposite noncrossing degree-eight pivot has codegree 4. Lower mixed codegrees remain open. `ralph/lanes/G/ROUND8_REPLAY.md:39`
- **cert, pending independent audit:** Bound all 1,497 alternate-pivot LRATs for two path/leaf strips: 1,491 degree-eight leaf keys at codegree 4 and six degree-nine full-anchor keys at codegree 5. `ralph/lanes/G/ROUND8_REPLAY.md:120`
- **hand / estimate:** Proved paired-window edge caps of 83, 88, and 92 at centre codegrees 1, 2, and 3. The higher-minimum-degree pilot projects about 187 CPU-hours for proofs in the codegree-2, minimum-degree-4 slice alone; the Hall prefix filter pruned too little to justify scaling. `ralph/lanes/G/rows/paired_window_budget.md:1`

**No Lane G jobs remain.** Next: independent audit of the alternate-pivot cover and a stronger exact filter for the higher-minimum-degree windows. `ralph/lanes/G/STATE.md:37`

## Lane H: Literature scout, claim ledger, Lean (ok)
**Round 8, Lane H:** No flow-verified order-40 graph and no new whole-distribution exclusion. The ledger still has **278 near-regular MTF distributions plus Case R**, including 10 conditional U88 keys and 20 open e168 degree-six keys. `ralph/CLAIMS.md:1`

- **Lean:** Added four lemmas covering arc-deletion soundness and exact window sizes and independence bounds. The pinned build and all 4 targeted and 284 project axiom checks passed. `lean/R310/CompletionBridge.lean:7`
- **Hand + enum:** Independently verified C’s singleton-budget obstruction for exactly two diagonal-four 8/8 P3 layouts, binding 30 e62 and 60 e63 rows. Neither full edge stratum is excluded. `ralph/lanes/H/ROUND8_REVIEW.md:3`
- **Open:** The November 22 literature check found no newer bound, public bulk order-39 census, or exact order-30 counts at 88–99 edges. `ralph/lanes/H/LIT.md:181`

The strongest checked direction remains A/G’s paired e168 windows: codegree 3 and codegree 2 with minimum window degree 3 are excluded only at the named profiles. Next, bind the remaining codegree-1 and mixed proof receipts. B’s e108 tranche proofs are pending critic review, and 124 classes are still missing. **No Lane H jobs remain; no extra cores needed.**

## Critic (ok)
**Round 8: no flow-verified order-40 graph and no new whole-distribution exclusion.** The baseline remains 278 near-regular MTF distributions plus Case R.

- **Confirmed:** A/G’s three marked e168 exclusions, B’s e88 prefix zero and 1,142 supplied e108 exclusions, C’s scoped P3 cuts, D’s three-profile restriction only for global `L=6`, E’s single mixed core, F’s cyclic unsigned-quotient exclusion, and H’s four Lean lemmas.
- **Deep audit:** The full R(7) exclusion passed independent replay: four residues, 977,008 trees, 49,569,079 nodes. The checker rejected a false closure and an incomplete cover.
- **Rejected:** One replay recipe, not an exclusion. A and G used different CNFs for 32 codegree-one pilot keys. Both versions passed both proof checkers on all 32.
- **Rule break:** The flow counted G at 22 against its 20-process share. Workspace caps held; the final check found zero busy processes.
- **Round 9 cores, A–H:** **4 / 17 / 4 / 8 / 22 / 3 / 20 / 2 = 80**.
- **Best next test:** Determine whether the existing order-26 marked source covers the mixed e168 codegree-three, minimum-degree-three slice before generating a new catalogue.

Full review: `ralph/critic/round_008.md:1`. Directives: `ralph/critic/LATEST.md:1`. Allocations: `ralph/ALLOC.md:1`.
