# Round 2

Began 2026-11-21T17:50:52; ended 2026-11-21T18:49:01.

## Flow checks
```json
{
 "round": 2,
 "verified_340_graphs": [],
 "graph_files_checked": [],
 "solver_processes_now": 17,
 "per_lane_now": {
  "B": 17
 },
 "rss_gb_now": 0.0,
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
- **R(7) — cert, previously accepted.** Preserved all four proof packages and replayed 977,008 roots and 49,569,079 proof nodes in 57.6 CPU-seconds. The replay no longer depends on Lane C’s scratch files. See `ralph/lanes/A/R7_REPLAY.md:1`.
- **R(6) path windows — enum, coverage only.** Independently matched all 2,454 catalogue rows in 49.82 CPU-seconds, recovered all 42 planted paths, and rejected a missing row, a forged empty cover, and a forged triangle row. No path case was closed. See `ralph/lanes/A/P4_REPLAY.md:1`.
- **PB provenance — open.** The binder matched all 189,418 retained proof-input rows against the provisional export plus the case constraints and rejected altered inputs. Lane H’s full `R310.Files` export is still needed. See `ralph/lanes/A/PB_BINDING.md:1`.

No Lane A jobs remain. Next: bind the full Lean export when available and independently check Lane C’s next path reduction. \(R(3,10)\) remains unresolved.

## Lane B: Gluing (t9 <= 88, then a faster gluer) (ok)
**Lane B, round 2: R(3,10) remains open.** No order-40 witness or new degree-distribution closure.

- **Enum:** Generated 4,751,963 distinct e88 duals reachable by two edge additions from the e86 census. The pilot found no MTF completion in 98,408 inputs; independent SAT agreed on all 24 sampled inputs. The full slice scan is still running.
- **Cert:** `ralph/lanes/B/critical88.json:1` gives a checked e88 dual with an independent 9-set after every single-edge deletion. Edge addition from e87 therefore cannot cover all e88 duals.
- **Estimate:** `gluecheap` matched the exact 191-graph control and ran 1.43× faster than `glue5` on the 96-parent e52 sample. The remaining e52 and e44 branches still project to about 79 hours at 18 fully occupied cores, before overhead. Neither was launched.
- **Jobs:** Prefix `1180084` (16 workers), MTF slice scan `3047886` (1 worker), and e43 branch `3921182` (queued behind the slice scan, then 1 worker).
- **Next:** Require exact e86 set equality and e86/e87 census counts from the prefix, then scan edge additions from the remaining e87 parents. Critic review requested for the deletion-witness check. Handoff: `ralph/lanes/B/STATE.md:5`.

## Lane C: Theory for the 9-regular case R (ok)
- **R(6), five-root paths — `enum`, pending critic acceptance.** Joining overlapping 22-vertex windows yielded 1,156 labelled residues. None could be extended: a separate verifier replayed all 289,649 proof nodes and rejected a forged shortage leaf. No search hit a limit.
- **R(6), four-root paths — open.** Lane A independently matched the 2,454-row cover. Maximality reduced it to 1,356 rows; all 15 SAT pilots reached their iteration cap without a verdict.
- **Next:** Factor the four-root extension by its two boundary sides. Keep isolated codegree-six edges and three-root paths with diagonal codegrees 3, 4, and 5 separate. A and H: please review the five-root cover and trace.
- No candidate graphs or running jobs. \(R(3,10)\) remains unresolved. Handoff: `ralph/lanes/C/STATE.md:1`; replay: `ralph/lanes/C/PATH_REPLAY.md:1`.

## Lane D: New SAT encodings and splits for case R (ok)
**R(3) remains open.** No new kernel exclusions or 40-vertex candidate. The 110 root-swap representatives cover rooted kernels; they do not partition unrooted graphs.

- **Hand:** An incidence count rules out \(K_{3,3}\) in R(3), so three-element neighborhood supports cannot repeat. The cut rejects 284 of 800 sampled side profiles, but closes no surviving kernel. See `ralph/lanes/D/SATURATED_BICLIQUE.md:1`.
- **Enum:** The factored encoding recovered all five expected C16 graphs across 13 kernels. The local catalogue found 22 forbidden pattern types on four coordinates, up to coordinate permutations. See `ralph/lanes/D/SIDE_FACTOR.md:1`.
- **Open:** All 10 baseline and 4 strengthened R(3) probes hit their 75 CPU-second limit without a verdict. No solver jobs remain.
- **Next:** Test whether sharing one graph of singleton-support vertices across the local constraints improves pruning. Do not scale the current encoding. Lane H and the critic were asked to review the hand lemma; results and job logs are indexed in `ralph/lanes/D/STATE.md:6`.

## Lane E: Automorphisms (the open (p, f) cases) (ok)
**Lane E, round 2:** No order-40 witness. \(R(3,10)\) remains unresolved.

- **Enum:** Excluded the full `(2,32)` branch with attachment sizes `5,5,5,6`. Across 1,470 anchors, none of 13,279 eligible windows admitted the required partition. An independent replay matched every anchor. `ralph/lanes/E/crown32_t1.md:3`
- **Enum:** Narrowed the remaining involution branches. The number of unattached fixed vertices is at most 6 for `(2,28,a=4)`, 11 for `(2,30,a=4)`, and 10 for `(2,30,a=5)`. `ralph/lanes/E/crown28_windows.md:3` · `ralph/lanes/E/crown30_windows.md:23`
- **Hand:** An order-three orbit with four fixed neighbors must have exactly 12 moved neighbors, not 15. Eight templates remain, and the local profile test excludes none of them. `ralph/lanes/E/order3_a4.md:3`

No jobs are running. H and the critic have the replay instructions. Next: test cross-attachment triangle constraints on the three surviving six-vertex cores for `(2,28,a=4)`.

## Lane F: Constructions: search for a (3,10,40)-graph (ok)
**Round 2: no candidate.** Lane F used 0.253 core-hours. No solver jobs remain.

- **enum:** Exhausted a 28,113-graph rewire component distinct from Exoo’s. None of its graphs extends to 40 vertices. The best degree-valid attachment still has 142 independent 10-sets.
- **open:** The best triangle-free, degree-valid 40-vertex start is 9-regular with 44 independent 10-sets and an order-3 automorphism fixing 10 vertices. The raw score of 30 still comes from degree-10 graphs.
- **enum:** All ten four-vertex repair cases for the 44-set start failed, without proof logs. Calibrated orbit rewiring also did not improve it. Neither result excludes the symmetry family.
- **Next:** Test a way to escape this local minimum before allocating more cores to the same starts. No extra cores or RAM requested.

Handoff: `ralph/lanes/F/STATE.md:5`. Score table: `ralph/lanes/F/round2_nearness.tsv:1`.

## Lane G: Near-regular degree distributions N(e) (ok)
**Lane G excluded 64 more near-regular distributions.** Counting the prior gluing exclusions, 454 remain plus Case R. \(R(3,10)\) is still undecided.

- **`cert` — 63 cuts without prior gluing assumptions.** Both LRAT checkers ruled out all five published 118-edge residual classes at a degree-six root, regardless of total edge count. Thus every degree-six residual has at least 119 edges, excluding the remaining 166-edge distributions with a degree-six vertex. See `ralph/lanes/G/rows/root_residue.md:1`.
- **`cert` — One conditional cut.** The new floor tightened 61 of 269 higher-edge bounds. All 63 exact Farkas certificates passed; one bound fell to 87, closing the 167-edge distribution `(8,0,2,30)` under the existing gluing floors. See `ralph/lanes/G/REPRO.md:45`.
- **`open` — Next step.** Both checkers excluded the 63 recovered 119-edge residual classes, but six of the published 69 are missing. Recovering and excluding those six would close another 55 distributions.
- **Handoff.** No jobs remain. H and the critic have the replay details; B has the revised count of 20 additional cases an 88-edge gluing exclusion would close.

## Lane H: Literature scout, claim ledger, Lean (ok)
**Round 2, lane H — \(R(3,10)\) remains open.** No order-40 witness passed the flow gate. The literature review found no change to the published bounds \(40\le R(3,10)\le41\), no public bulk order-39 catalogue, and no new exact dense order-30 count. See `ralph/lanes/H/LIT.md:3`.

- **Lean:** The pinned project builds without compiling Mathlib from source. All 263 existing and 15 new axiom reports use only standard axioms. The new lemmas cover residue bounds, path-window overlap, and typed wedge counts—not the census computations. See `ralph/lanes/H/LEAN_REPRO.md:1`.
- **Certificate provenance:** All three full-project OPBs match the provisional exports byte-for-byte. The retained PRc7 proof input matches all 189,418 rows; this does not establish UNSAT or cube coverage. See `scratch/H/pb-bind.log:1`.
- **Ledger:** Mirrored the critic’s verdicts: R(7) is `cert`, C8 and P5 remain `enum`, and G’s six conditional closures retain both gluing floors. See `ralph/CLAIMS.md:5`.

**Team outlook:** R(7) is the strongest confirmed closure. The most promising new regular-case work is the R(6) window reduction: A independently matched the 2,454 P4 layouts, and C replayed the P5 trace on 1,156 supplied residues. P4 remains open, B has not covered e88, and G’s five-residue certificate is recorded only at its proved edge level.

**Next:** Ask the critic to review P5 cover completeness and G to pin the degree-six residual premise before counting distribution closures. Lane H has no running jobs.

## Critic (ok)
- **Confirmed:** 64 new MTF degree-distribution exclusions: 63 independent of prior gluing and one conditional on both gluing floors. **454 near-regular distributions plus Case R remain.**
- **Confirmed:** No five-root codegree-six path in R(6), and no `(2,32)` involution with attachments `5,5,5,6`. Both are `enum`; four-root paths remain open.
- **Rejected:** The stale estimate of 24 further cuts from a complete e88 gluing exclusion. The corrected count is **20**. The e88 scan is incomplete.
- **Rules:** No Round 2 rule breaches observed. No order-40 graph passed the flow gate.
- **New core shares (A–H):** `6 / 18 / 6 / 6 / 18 / 6 / 18 / 2` = **80**.
- **Best next step:** Cover and exclude the six missing e119 degree-six residues. Completing that check would cut **55 more** distributions.

Full review: `ralph/critic/round_002.md:1`. Next-round directives: `ralph/critic/LATEST.md:1`.
