# Round 5

Began 2026-11-21T21:09:10; ended 2026-11-21T22:16:52.

## Flow checks
```json
{
 "round": 5,
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
Round 5 audit complete. **\(R(3,10)\) remains unresolved:** no candidate graph, new case closure, or higher residue floor.

- **cert, supplied rows only:** Checked all 11,425 demand-clique witnesses and rebuilt and replayed all 2,890 LRAT proofs with both checkers. The 11 pinned proofs apply only at total \(e=169\); all 11 weaker unpinned cores have verified SAT assignments.
- **enum + hand:** The exact one-edge incidence audit leaves six order-33 classes missing. Any missing \(e=120\) residue is deletion-critical and has at most five nonisomorphic one-edge extensions. Zero extensions remains possible.
- **Handoff:** No live Lane A jobs. The replay and evidence are in `ralph/lanes/A/HIGH_RESIDUE_AUDIT.md:88`. Next: bind and audit any new catalogue rows from Lane G.

## Lane B: Gluing (t9 <= 88, then a faster gluer) (ok)
- **Cert, pending critic review:** Every degree-seven vertex \(v\) in a maximal triangle-free \((3,10,40)\)-graph leaves at least **108 edges** in \(G-N[v]\). This uses the checked floor 107 and does not rely on the degree-eight or degree-nine gluing bounds.
- **Evidence:** All 234,681 level-107 classes are covered by 231,455 checked demand cliques and 3,226 LRAT proofs replayed by both checkers. See `ralph/lanes/B/FLOOR7_108.md:1` and `scratch/B/logs/e107_floor108_replay.log:1`.
- **e108 remains open:** The reducible census and seven verified deletion-critical classes leave 1,873 classes missing. No full e108 gluing run was launched.
- **Running:** Prefix PID `1180084` uses 16 cores; e43 PID `3921182` uses one core and has completed 39 of 48 generation chunks; tail87 PID `2576750` is queued behind e43. Full \(t_9\le88\) remains open.
- **Next:** Audit the e43 and tail87 terminal results. Critic: replay the floor-108 bundle. G/H: recompute distribution overlaps without double-counting the direct e162 exclusion. \(R(3,10)\) remains undecided.

## Lane C: Theory for the 9-regular case R (ok)
**Round 5, lane C:** \(R(3,10)\) and \(R(6)\) remain open. No candidate graph and no live lane C jobs.

- **Cert, pending critic:** All 1,438 edge-cap keys passed exact coverage, CakeLPR replay, and hash checks. The three-root residue satisfies \(e(X)\le61\) at diagonal five and \(e(X)\le63\) at diagonals three and four.
- **Hand + cert, pending critic:** A hand argument ruled out 9/9 arms without the planned 119 SAT tests. All 120 remaining mixed 9/8 keys passed replay. Thus at \(f^*\ge8\), every three-root component has two arms of count eight and diagonal three or four. At \(f^*=9\), the codegree-six graph is a matching; isolated pairs remain open.
- **Hand reduction + enum:** The isolated full-wing branch reduces to smaller windows. The sieve leaves 35,099 marked order-21 windows and 246,483 order-13 cores, not completions. Next: measure a complementary join of two marked windows before launching more SAT.

Evidence and replay instructions are frozen in `ralph/lanes/C/ROUND5_REPLAY.md:1`; the handoff and review requests are in `ralph/lanes/C/STATE.md:1`.

## Lane D: New SAT encodings and splits for case R (ok)
R(3,10) remains unresolved. Lane D narrowed the alternative R(3) cover; the original 110 minimum-root representatives are unchanged.

- **Hand / enum:** The maximum-square split has 111 rooted keys. At maximum 12, the codegree floor rules out 19 keys by hand, and exact integer Farkas replay rules out all three cyclic keys (`enum`, pending encoding audit). That leaves 13 forest keys at maximum 12 and 76 keys at higher maxima.
- **Calibration:** Both exact SAT variants exhausted all 16 smaller C16 keys and reproduced the same 13 labelled outputs from five known graph classes.
- **Partial split:** For key 34, the count-six branch is excluded by exact LP replay without the forest assumption. Counts 7–14 remain feasible in the relaxation, not as graphs.
- **Handoff:** No graph candidate or live lane D jobs. Next: H/C audit the three cyclic exclusions before relying on the forest reduction. See `ralph/lanes/D/STATE.md:1` and `ralph/lanes/D/TRANSPORT.md:35`.

## Lane E: Automorphisms (the open (p, f) cases) (ok)
- **Cert, pending critic review:** Excluded the involution subcase with 32 fixed vertices, four size-six attachments, and a core \(W\) with minimum degree at least two and exactly 12 edges. All **7,962** window CNFs passed `cake_lpr` in **1.21 core-hours**. Regeneration and replay also passed for all 1,058 cubic windows and 56 sampled noncubic windows. `ralph/lanes/E/cubic32.md:3`
- **Mixed hand/cert/enum:** Froze the complete \(f=28\) cover, including inherited F10, without rerunning it. `ralph/lanes/E/f28_cover.md:1`
- **Next:** The 11-edge core remains open, but a new catalogue-based bound forces all four windows to have exactly 74 edges and leaves only two attachment incidence patterns. H/critic should audit the new exclusion before recording it. `ralph/lanes/E/window73.md:1`
- No Lane E jobs remain active. No candidate was submitted; \(R(3,10)\) remains undecided.

## Lane F: Constructions: search for a (3,10,40)-graph (ok)
**Round 5: no candidate.** Lane F’s best remains **24 independent 10-sets**, on the same two free-involution seeds. \(R(3,10)\) remains unresolved.

- **Enum:** Exact two-vertex completion on 486,212 new canonical order-38 cores found no graph with 23 or fewer independent 10-sets.
- **Enum:** Checked all 7,195 distinct clean four-deletion cores from the two seeds. No repair changing only edges incident to at most four vertices yields a valid graph. This rules out those two local neighborhoods, not the involution family.
- **Enum/open:** Exact two- and three-vertex repairs that retain existing bad sets also found no improvement. The corresponding four-vertex search was sampled, not exhausted.

No jobs remain live; the round used **0.387 core-hours**. Evidence and replay details are in `ralph/lanes/F/ROUND5.md:84`. Next round should use a different source pool or core-selection method rather than repeat these scans.

## Lane G: Near-regular degree distributions N(e) (ok)
- **85 additional distributions excluded, pending critic review.** This leaves **283 near-regular cases plus Case R**, with 10 conditional U88 cases. All 85 exact Farkas checks replayed.
- **Enum + hand:** Two independent enumerations found that none of the 984 minimum-degree-five order-33 residues can extend at a degree-six root. Thus, in an MTF candidate, all degree-six vertices are mutually adjacent, so \(n_6\le2\). This gives 84 cuts; parity gives the remaining e168 cut.
- **Conditional on Lane B’s floor 108:** Five more cuts would leave **278 plus Case R**. Four U88 keys change in each direction, so the count stays 10.
- No G jobs remain. The six missing e120/e121 classes are still open; the next target is the 20 surviving e168 distributions with a degree-six vertex.
- Proof and handoff: `ralph/lanes/G/rows/no_degree_five_residue.md:1`, `ralph/lanes/G/round5_cases.csv:1`, `ralph/lanes/G/STATE.md:1`.

## Lane H: Literature scout, claim ledger, Lean (ok)
**R(3,10) remains open.** The literature recheck found no result beyond \(40 \le R(3,10) \le 41\), no public bulk census of the 39-vertex graphs, and no exact count for the dense order-30 classes. Sources are recorded in `ralph/lanes/H/LIT.md:118`.

- **Ledger:** Eight confirmed cuts leave **368 near-regular MTF distributions plus Case R**. The 12 U88 targets and 39 potential e168 cuts remain open; B’s proposed e162 exclusion awaits critic review. See `ralph/CLAIMS.md:3`.
- **Lean:** Checked the nine distinct double signatures at degree-six equality, C’s complete-arm and wing-budget lemmas, and G’s degree-five residue reduction. The build, 12 targeted axiom reports, and 270 project axiom reports passed. No finite cover was proved in Lean. See `ralph/lanes/H/LEAN_REPRO.md:137`.
- **Jobs:** No Lane H jobs remain. The handoff is in `ralph/lanes/H/STATE.md:1`.

**Best next step:** Independently bind G’s degree-five residue sweep and exclude any survivors. A complete exclusion would bypass the six missing catalogue classes for graphs with at least three degree-six vertices, removing **18 e168 and 21 e169** distributions. No order-40 witness passed the flow gate.

## Critic (ok)
**Round 5: \(R(3,10)\) remains open.** No order-40 graph passed the flow gate.

- **Confirmed:** Lane B’s degree-seven residue floor of 108. All 3,226 LRAT proofs passed both checkers. Lane G’s independent enumeration and exact cut checks also passed.
- **Case count:** 90 additional near-regular MTF distributions are excluded, leaving **278 plus Case R**. The direct e162 exclusion is counted once; **10 U88 keys** remain conditional.
- **Other confirmed reductions:** C’s three-root caps and matching result at \(f^*=9\), D’s tight maximum-square forest reduction, and E’s 12-edge involution subcase. F’s searches found no improvement below 24 and exclude only the checked local neighborhoods.
- **Rejected:** Double-counting e162 or treating partial catalogues, sampled runs, or pinned proofs as full exclusions. No primary claim was rejected at its stated scope.
- **Rules:** No lane overage observed. The critic inadvertently rewrote three Lane C scratch CNFs; all three hashes matched the originals. No critic jobs remain.
- **New core split, A–H:** **2 / 22 / 8 / 2 / 17 / 2 / 25 / 2** = 80.
- **Best next step:** Use the degree-six equality signatures to seek a direct obstruction for the **20 surviving e168 distributions with a degree-six vertex**.

Full review: `ralph/critic/round_005.md:1`. Next-round directives: `ralph/critic/LATEST.md:1`.
