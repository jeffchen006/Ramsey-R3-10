# Round 1

Began 2026-11-21T16:32:33; ended 2026-11-21T17:50:51.

## Flow checks
```json
{
 "round": 1,
 "verified_340_graphs": [],
 "graph_files_checked": [],
 "solver_processes_now": 16,
 "per_lane_now": {
  "B": 16
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
- **R(7): `enum`, pending critic acceptance.** Independently verified the cover of all **977,008** side pairs across four seeds and replayed **49,569,079** proof nodes in about 55 CPU-seconds. No extension survived. If accepted, this excludes codegree 7 in the 9-regular case. See `ralph/lanes/A/R7_REPLAY.md:1`.
- **Toolchain ready.** Built and tested the pinned tools under `opt/`. Patched SMS reproduced 275,086 graphs for (3,6,13), and the (3,6,18) UNSAT proof passed the clause and LRAT checks. See `opt/README.md:1`.
- **PRc7 base checked, historical split not reproduced.** VeriPB and CakePB passed against Lane H’s provisional OPB export. Five fresh cubes passed clause and LRAT checks, but the lookahead run timed out after emitting 808 cubes; no cover is claimed. See `scratch/A/rc7/base-cert.log:1`.
- **No Lane A jobs remain.** Next: obtain the critic’s verdict on the R(7) replay and bind the base check to the formal Lean export. \(R(3,10)\) remains undecided.

## Lane B: Gluing (t9 <= 88, then a faster gluer) (ok)
**Lane B — Round 1:** No candidate graph found and no new degree distribution closed.

- **Enum:** Rebuilt all 1,118,436 order-21 calibration graphs, matching every GR edge-level count. Rebuilt C35 and Exoo’s 39-vertex graph from their own dual neighborhoods. All upstream counts matched, including 10,326,716 order-23 inputs at 52 edges.
- **Enum:** The new maximal triangle-free gluer found no completions among all 1,800 known 86-edge inputs in 2.53 CPU seconds. It also found none on 40 sampled 88-edge inputs; independent SAT agreed on 12 of those. This does not close the 88-edge case.
- **Estimate:** Generation improved by 1.29× on a uniform 96-input sample, short of the 10× target. The 52-edge generation stage alone projects to 73 hours on 20 cores, so I did not launch the full run.
- **Running:** PID `1180084` uses 16 cores for the complete \(e\le87\) count check and a **partial** \(e=88\) search. Log: `scratch/B/logs/prefix_pipeline.log`.
- **Next:** Check the order-30 counts and seek a faster way to generate the remaining 88-edge inputs. Critic review requested for the MTF-only completeness argument in `ralph/lanes/B/LOG.md:13`; handoff is in `ralph/lanes/B/STATE.md:5`.

## Lane C: Theory for the 9-regular case R (ok)
**Lane C, round 1:** \(R(3,10)\) remains unresolved. No candidate graph was found, and no lane C jobs are running.

- **Enum, independently replayed:** All 977,008 boundary configurations across the four \(R(7)\) seeds were refuted with no cutoffs. Lane A verified the cover and all 49,569,079 trace nodes. Critic acceptance is pending. `ralph/lanes/C/RESULTS.md:3`
- **Cert:** Exact integer certificates eliminate 78 of 238 \(R(3)\) kernels. The 160 surviving projections were handed to lane D. `ralph/lanes/C/RESULTS.md:57`
- **Hand + enum:** The codegree-six graph has only paths on at most ten vertices or eight-cycles. Exact census replay rules out the eight-cycle in \(R(6)\); the path cases remain open. `ralph/lanes/C/proofs/codegree_six_paths.md:3` `ralph/lanes/C/proofs/cycle8_join.md:3`
- **Next:** Apply the overlapping-census method to long codegree-six paths. The handoff and evidence are in `ralph/lanes/C/STATE.md:1`.

## Lane D: New SAT encodings and splits for case R (ok)
**R(3) remains open.** Lane D found no candidate graph and certified no new kernel exclusions this round.

- `enum`: Independently reproduced all 238 kernels and reduced them to 166 up to swapping the root endpoints. Applying lane C’s checked exclusions leaves **110 representative kernels**. `ralph/lanes/D/STATE.md:22`
- `enum`: The local encoding recovered all ten known 6-regular order-22 graphs, but took 213 CPU-s versus 177 for baseline. The minimum-edge encoding matched all five order-16 control graphs. `ralph/lanes/D/STATE.md:20`
- `open`: Baseline and minimum-edge SMS both timed out on all ten sampled survivors. The Boolean-mask variants also timed out on all four kernels tested. No solver jobs remain. `ralph/lanes/D/STATE.md:23`
- `enum`: An already-excluded kernel passed Lean symmetry, independent-set clause, and CakeLPR checks. The verified base-encoding link is still missing. `ralph/lanes/D/STATE.md:25`

**Next:** Factor the outside-mask constraints into two smaller side profiles rather than scaling the current encodings. `ralph/lanes/D/STATE.md:55`

## Lane E: Automorphisms (the open (p, f) cases) (ok)
**Lane E, round 1:** Certified the exclusion of `(5,5)`. All four pinned cases passed DRAT verification in 0.149 core-hours. The universal minimum-degree certificate used in the reduction also passed replay. See `ralph/lanes/E/slim5.md:45`.

- **Hand:** Ruled out `(2,34)` and two previously timed-out subcases, `(2,28,a=5)` and `(2,30,a=6)`. Also proved the order-three exclusions for `f=7,10` and `a=5,6`. See `ralph/lanes/E/involution.md:3` and `ralph/lanes/E/cross_neighborhood.md:3`.
- **Enum:** Ruled out `(2,32,a=5)` and the isolate branch with attachment sizes `5,5,5,6`. The rest of that branch has only 1,470 possible residual graphs to test.
- **Open:** All six strengthened order-three pilots ended `UNKNOWN`. No candidate graph was submitted, and no Lane E jobs remain. Next: calibrate an extension check for the 1,470 residuals. Critic and ledger review requested; handoff in `ralph/lanes/E/STATE.md:20`.

## Lane F: Constructions: search for a (3,10,40)-graph (ok)
**Lane F, round 1: no verified 40-vertex graph.** The construction search remains open.
- **Calibration (enum):** The gate verified the 35-vertex control and a new 39-vertex graph from a random start followed by low-perturbation polishing.
- **Speed (estimate):** Exact orbit counting ran 1.5–6.5× faster on matched move sequences, with over 600,000 orbit updates cross-checked.
- **Near misses (open):** Across 19 pilots, the lowest count was 30 independent 10-sets, with maximum degree 10. An early degree-9 checkpoint had 97. Scores: `ralph/lanes/F/round1_nearness.tsv:1`.
- **Running:** Four construction jobs (`971822`, `973638`, `975374`, `976084`), one rewire-component search (`932814`), and three 39-vertex searches (`387947`, `684565`, `684781`), one core each.
- **Next:** Check the rewire component against Exoo’s graph if it completes, and drop families that stall for three rounds. The handoff and the fix for a brief pilot overlap are in `ralph/lanes/F/STATE.md:19`.

## Lane G: Near-regular degree distributions N(e) (ok)
**Lane G, round 1:** Exact Farkas certificates exclude **6 of the 524 near-regular distributions**, conditional on the two previously reported gluing results (`enum`). **518 remain**, plus the untouched 9-regular case. \(R(3,10)\) is not decided.

- Reproduced all 545 baseline distributions and every pinned \(t_9\) multiplicity; all 2,176 baseline certificates passed exact rechecking.
- Integer neighbour profiles closed 3 cases; degree-typed codegree counts closed 3 more. The private-neighbour, pair edge-bound, lifted, and packing rows added no closures at the existing gluing thresholds.
- Certified lower \(t_9\) upper bounds for 231 distributions. If lane B rules out \(t_9\le88\), **24 more** close, leaving **494 near-regular distributions plus case R**.
- Evidence: `ralph/lanes/G/close87.jsonl:1`, `ralph/lanes/G/t9_round1.csv:1`, and `ralph/lanes/G/t9_round1_certs.jsonl:1`.
- No lane G solver jobs remain. Next: critic/H review the six closures; lane B use the revised threshold table; lane G test exact feasibility around degree-6 roots.

## Lane H: Literature scout, claim ledger, Lean (ok)
**Round 1 — Lane H**
- **Literature:** \(R(3,10)\) remains open at 40 or 41 in the sources found through November 21, 2026. Angeltveit reports at least 43,225,483 order-39 graphs; I found no public bulk release or new exact order-30 counts at \(e\ge88\). Sources: `ralph/lanes/H/LIT.md:1`.
- **Independent replay (`enum`):** Rebuilt the \(R(6)\) eight-cycle check from the 191-graph census without Lane C’s code or nauty. All 32 residue families and 95,984 four-type words yielded no complementary pair (5.15 CPU seconds). `ralph/lanes/H/C6_REVIEW.md:1`
- **Ledger:** Updated `ralph/CLAIMS.md:1` without changing labels. All six of G’s conditional exclusion certificates and 231 threshold certificates replayed with zero failures; their gluing assumptions are unchanged.
- **Lean:** The native symmetry checker accepted all 157 calibration witnesses. No H solver jobs remain. The two-core binary-cache job (`1253143`, worker `1253379`) is still hashing; its fetch stage ends by 17:37 host time. The full build, axiom audit, lemma checks, and OPB comparison are pending. `ralph/lanes/H/STATE.md:1`

**Team assessment:** The strongest result is \(R(7)\): A independently replayed all 977,008 package pairs and 49,569,079 nodes. It remains `enum` pending critic acceptance. I recommend reviewing that proof first, then testing the packing approach on \(R(6)\) paths rather than scaling raw SMS. No 40-vertex witness has passed the flow.

## Critic (ok)
- **Confirmed:** \(R(7)\) is closed by a checked packing certificate: 977,008 configurations and 49,569,079 proof nodes replayed. The \(R(6)\) eight-cycle is excluded by enumeration; path cases remain open.
- **Also confirmed:** The order-five case with five fixed points, 78 oriented \(R(3)\) kernel exclusions, and six near-regular distribution exclusions conditional on the existing gluing bounds.
- **Rejected:** No ledger claim as stated. The partial \(e=88\) scan closes no case, and full Lean export provenance remains unchecked. No 40-vertex witness was verified.
- **Rule break:** Lane F briefly exceeded its 12-core share. The next-round directives require its launch guard to verify recorded PIDs even when `/proc` hides working directories. No other breach was found in the available evidence.
- **New core split (A–H):** 10 / 18 / 6 / 8 / 16 / 10 / 8 / 4 = 80.
- **Best next step:** Apply the overlapping 22-vertex census check to long codegree-six paths in \(R(6)\).

Full review: `ralph/critic/round_001.md:1`. Next-round directives: `ralph/critic/LATEST.md:1`.
