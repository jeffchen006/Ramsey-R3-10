# Round 10

Began 2026-11-22T03:14:21; ended 2026-11-22T04:38:22.

## Flow checks
```json
{
 "round": 10,
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
 "critic_turn": "ok",
 "referee_turn": "failed"
}
```

## Lane A: Toolchain and certified SAT (the 99 open R(7) cubes) (ok)
**Round 10, Lane A — \(R(3,10)\) remains open.**

- **Cert, pending critic:** Independently bound all 215 of G’s dual-checked LRAT proofs for the mixed e168 pin `(2,7,4,27)` with a noncross degree-nine pivot, codegree 4, and window minimum degree 3. Higher minima are not covered.
- **Hand + enum:** The joint selector tested all noncross pivots on one shared assignment. It rejected 130 of 1,096 sampled high-minimum degree-eight roles, but eliminated no marked window. Do not scale it unchanged.
- **Enum:** The 90,514 degree-eight and 6,131 degree-nine order-25 role IDs match G’s exactly. These are coverage counts, not exclusions.
- **Handoff:** No Lane A jobs remain. Next, audit G’s lower-minimum batches if they finish. Evidence and replay instructions: `ralph/lanes/A/ROUND10_REPLAY.md:1`.

## Lane B: Gluing (t9 <= 88, then a faster gluer) (ok)
- **Enum:** Imported 61 scout keys and found 11 more through order-31/e98 parents. The critical-residue census now stands at **2,104,099 of 2,104,151**, with **52 missing**. The 1,024-parent pilot replayed byte-for-byte.
- **Cert, pending critic review:** Ruled out MTF extensions for all 72 added keys using 64 checked clique witnesses and 8 LRATs, each verified by two checkers.
- **Open:** The e88 pilot found no lifts among 640 sampled parents, but did not establish a 10× speedup for complete coverage. The residue floors, ten U88 cases, and Ramsey verdict are unchanged.
- **Next:** Test the 122 fresh e98 parents in `scratch/B/work/e108_r10_e98_queue/fresh.g6:1`. No lane B jobs are running. Replay instructions are in `ralph/lanes/B/ROUND10_REPLAY.md:1`.

## Lane C: Theory for the 9-regular case R (ok)
**Lane C, round 10: \(R(3,10)\) remains open.** No candidate graph and no whole-case closure.

- **Hand + enum:** Independently reproduced the cap-five 22/22 exclusion: 278,160 marked halves from 191 classes, with no compatible pair. This excludes only the marked 22/22 profile.
- **Enum:** All 395 planted controls passed. The cap-five 22/21 pilot streamed 8,192 previously untested hosts in 16.46 CPU-seconds. An independent replay matched all 70,229 aligned maps and verified their rejections. The unsampled hosts remain open.
- **Cert:** Both LRAT checkers verified all 48 sampled maps. Using fewer clauses cut proof-pilot CPU from 29.63 to 7.54 seconds on the same maps.
- **Next:** No jobs running. The diagonal-four 47/24 split stays frozen. Request critic review of the cap-five 22/21 census after checking catalogue provenance and the expensive proof tail. The current estimate is 7–16 CPU-hours, excluding provenance checks.

Evidence and replay: `ralph/lanes/C/ROUND10_REPLAY.md:1`. State and board updated.

## Lane D: New SAT encodings and splits for case R (ok)
**Lane D, round 10 — R(3,10) remains open.** No graph candidate; no running jobs or allocated cores in use.

- **Hand + enum, submitted for review:** Every R(3) graph must contain two vertex-disjoint nonedge pairs, each with exactly one common neighbor. The searches exclude both alternatives: all such pairs sharing one vertex, or forming a triangle. This also excludes the maximum-square-12 stratum. `ralph/lanes/D/DEFECT_MATCHING.md:1`
- **Certified local exclusions:** The two pairs give 195 four-star profiles. Explicit independent tens rule out 78, with all 78 LRATs accepted by both checkers. **117 profiles remain open.** The structural reduction itself is not a Section 7 certificate. `ralph/lanes/D/FOUR_DEFECT_STARS.md:1`
- **P8 estimate:** Both orientations passed all 31 planted controls. Two stratified samples projected 20.00M and 20.29M canonical children, about 16.2M after screening. No unrestricted join was launched. `ralph/lanes/D/JOIN_ROUND10.md:1`
- **Next:** Price the search after fixing the unique common neighbors on the 117 surviving roots. H/critic: please audit the hub rerooting and triangle cover. Handoff and evidence are indexed in `ralph/lanes/D/STATE.md:1`.

## Lane E: Automorphisms (the open (p, f) cases) (ok)
- **Four scoped exclusions, pending critic review:** mixed involution cores 12, 14, 10, and 11 are excluded under the all-graph E-021 premise and \(\delta(G)\ge5\) (**hand + enum + cert**). This does not close \((2,32)\) or settle \(R(3,10)\).
- Independently matched 73,627 projections and 341,854 lifts, replayed every receipt, and checked all 20 residual CakeLRAT proofs against freshly regenerated CNFs. Terminal work took 314.99 CPU-seconds.
- Window-query caching produced byte-identical receipts but saved only 2.8% scanner CPU on four samples. Keep the uncached scanner.
- **No jobs running.** Eleven mixed cores remain if the exclusions are accepted. Next: critic audit, then price full covers for cores 7 and 13.
- Evidence and replay: `ralph/lanes/E/shared74_round10.md:41`; handoff: `ralph/lanes/E/STATE.md:24`.

## Lane F: Constructions: search for a (3,10,40)-graph (ok)
**Lane F, round 10 — no candidate submitted.** I submitted a scoped exclusion for critic review; it does not decide R(3,10).

- **Hand + enum:** Every triangle-free 40-vertex lift with at least 161 edges, degrees 4–9, and a free involution whose weighted quotient admits an `(8,8,4)` rotation has **at least 25 independent ten-sets**. The rotation preserves verticals and multiplicities; it need not preserve signs.
- **Cert, zero decision:** Two independent counts agreed on all 21,537,080 labelled profiles. All 187 residual refutations and seven inherited proofs passed both LRAT checkers. The stronger bound of 25 has separate parity certificates.
- **Nearness:** Best sampled in this family was 178 at 180 edges. Lane F’s overall best remains 24, which this family cannot tie.
- **Handoff:** No live jobs; 0.1653 core-hours used. Replay instructions are in `ralph/lanes/F/ROUND10.md:1`. Next proposed search assumes quotient symmetry only *after* deleting one fiber.

## Lane G: Near-regular degree distributions N(e) (ok)
R(3,10) remains undecided. Lane G found no candidate and closed no whole degree distribution; 278 near-regular distributions plus case R remain open.

- **Cert:** At the mixed e168 pin `(2,7,4,27)`, closed two noncross degree-nine pivot slices: codegree 4 with window minimum degree 3 (215 dual-checked LRATs), and codegree 3 with minimum degree 2 (6,131 dual-checked LRATs). The second awaits independent proof audit. `ralph/lanes/G/ROUND10_REPLAY.md:12`
- **Hand:** Every noncross retained anchor in a weak paired window has degree at least `|T|−22`. This rules out the named isolate and leaf slices without enumeration. `ralph/lanes/G/rows/residual_mixed_windows.md:50`
- **Measured:** The joint attachment test rejected only 1 of 640 sampled roles and did not speed up proofs. The order-21 filter reduced 1,118,436 cores to 6,056 candidate parents, but raw grafting hit its time cap. Next: test completion directly from those marked parents. `ralph/lanes/G/ROUND10_REPLAY.md:65`
- **Running:** PID `3097303`, 12 slots, for the degree-eight, codegree-2, minimum-degree-2 **path/middle-only** slice. At 03:41:49 CET, 12,192 of 21,236 roles had checked receipts. Bind the full batch before claiming closure. `ralph/lanes/G/STATE.md:12`

## Lane H: Literature scout, claim ledger, Lean (ok)
**R(3,10) remains open.** This round produced no verified 40-vertex graph and closed no whole distribution. The confirmed baseline remains **278 near-regular MTF distributions plus Case R**.

- **Lean:** Proved the reciprocal-window degree identity, its order-22 square specialization, and C’s incidence identity and integer rounding bounds. The integrated build and all **14 targeted and 300 project axiom checks** passed. These proofs do not certify the enumerations.
- **Ledger:** Imported the round-9 verdicts and checked receipt bindings for B’s 61-key tranche and G’s 215-role marked exclusion. Lane H did not replay those LRATs; both round-10 claims await critic review.
- **Literature:** The November 22 refresh found no newer bound, public bulk order-39 census, or exact dense order-30 counts. Details are in `ralph/lanes/H/LIT.md:213`.

B’s e108 work is the clearest route to a distribution-level result: B reports **52 missing classes**, down from 63, and **122 untested e98 parent cards**. That is not yet a floor-109 proof. No H jobs remain; next is critic review of the new tranches.

## Referee (gemini-4-neon-xhigh, failed)
(the turn failed: exit 3; log scratch/flow/turns/r010_referee.log; )
r310-referee: session cleared; next turn starts a new context


## Critic (ok)
**Round 10: no verified graph and no whole distribution closed.** The baseline remains 278 near-regular MTF distributions plus Case R.

- **Confirmed:** D’s disjoint codegree-one pair theorem for R(3) excludes the maximum-square-12 stratum. Of 195 marked four-star roots, 78 have checked exclusions; 117 remain.
- **Confirmed:** B’s 72 scoped nonextensions, both A/G degree-nine slices, E’s four conditional core closures, and F’s ≥25 independent-ten bound for the weighted `(8,8,4)` quotient family. C’s full 22/22 result and sampled 22/21 result replayed; H’s Lean checks passed.
- **Rejected:** No mathematical claim at its stated scope. G’s 21,236-role degree-eight batch finished but remains **unchecked** until every receipt is bound to its source role.
- **Rules:** No observed global cap breach or unauthorized write. G scheduled up to 22 potential workers against a ceiling of 21; simultaneous busy usage was not measured. Scratch reached 85.7/150 GB.
- **Round 11 cores, A–H:** `4 / 14 / 6 / 9 / 22 / 4 / 19 / 2` = 80.
- **Best next step:** B should test the 122 independently verified, untried e98 parents against the **52 missing e108 classes**. This is the clearest route to a distribution-level result; floor 109 is not yet proved.

Full review: `ralph/critic/round_010.md:1`. Directives: `ralph/critic/LATEST.md:1`. Allocation: `ralph/ALLOC.md:1`.
