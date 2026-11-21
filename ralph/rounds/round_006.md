# Round 6

Began 2026-11-21T22:16:52; ended 2026-11-21T23:27:45.

## Flow checks
```json
{
 "round": 6,
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
**Round 6: no case closed; R(3,10) remains unresolved.**

- **Hand:** For each of the nine open e168 distributions with two degree-six vertices, both degree-six residues have a marked five-set with exactly two legal edge additions inside it. This rules out the zero-addition branch for those nine distributions, but not for the eleven one-root distributions. Proof: `ralph/lanes/A/ADJACENT_DEG6.md:3`.
- **Enum:** None of the 1,223 supplied e120 residues has the required mark (3.39 CPU-s). The inverse check passed 18 smaller two-addition controls. The six-class census gap remains open.
- **Enum:** Independently matched G’s 14 canonical equality templates and all 112 template/distribution pairs. Omitted templates, relabelled duplicates, and omitted pins were rejected. This checks the cover, not the SAT verdicts.
- **Handoff:** No live Lane A jobs. Prior proof hashes passed. Next: bind any new e120/e121 rows from G, keeping e169-pinned and unpinned proofs separate. `ralph/lanes/A/STATE.md:3` records the handoff.

## Lane B: Gluing (t9 <= 88, then a faster gluer) (ok)
**Round 6 — Lane B**
- **Enum:** All **5,719,576 deletion-reducible e88 residues** returned zero MTF completions. Independent replay verified the parent–child partition and all scan chunks; SAT agreed on 64 dispersed tail inputs. The outside-prefix d7/e43 branch also returned zero from all 1,521 seeds. `ralph/lanes/B/ROUND6_REPLAY.md:7`
- **Open:** The e108 census reached **2,102,885 of 2,104,151** classes; 1,266 critical classes remain missing. **Cert, pending review:** 569 checked demand cliques and 45 dual-checked LRATs exclude the 614 supplied critical classes only. No floor-109 claim. `ralph/lanes/B/ROUND6_REPLAY.md:50`
- **Running:** Prefix PID `1180084`, 16 cores. Next: compare its final e87 census byte-for-byte with the checkpoint. The critic has the replay bundle. `ralph/lanes/B/STATE.md:16`

No candidate graph. The edge-critical e88 complement and all ten U88 keys remain open; \(R(3,10)\) is not decided.

## Lane C: Theory for the 9-regular case R (ok)
- **New partial exclusion (`enum + cert`, pending critic):** In global \(R(6)\) with \(f^*=9\), the \((12,12)\) wing-size split is impossible. At most one residue vertex can avoid both wings.
- The exact join reduced 646,736 pack pairs to 1,134 pinned CNFs. All 1,134 refutations passed CakeLRAT and a full replay with freshly generated CNFs. Evidence and audit instructions: `ralph/lanes/C/ROUND6_REPLAY.md:1`.
- The other three splits remain open. The asymmetric pilot already yields over 513 million raw pairings before cross-edge filters, so the next step is a stronger incidence filter, not a larger run.
- No lane C jobs remain. No candidate graph was found; \(R(3,10)\) remains open.

## Lane D: New SAT encodings and splits for case R (ok)
- **Hand:** Reduced the max12 forest cover from 13 to **9 rooted keys**. The maximum score \(S\), the number of isolated edges plus three-vertex paths in an edge kernel, gives two disjoint strata: \(S_{\max}=2\) has six keys and \(S_{\max}=3\) has three. If no square has two codegree-two diagonals, key 32 alone covers that subcase. Proof and census: `ralph/lanes/D/TIGHT_FOREST.md:41`.
- **Enum:** Both SAT encodings matched all 144 smaller calibration cells. The target SAT and LP probes produced no refutation or graph. R(3) remains open, and the 110 minimum-root keys are unchanged.
- **Handoff:** No jobs remain; about 0.21 CPU-hours used. `ralph/lanes/D/STATE.md:1` records the evidence. H/critic review requested for the score proof; next test is an eager \(S(e)\le2\) constraint in the score-2 stratum.

## Lane E: Automorphisms (the open (p, f) cases) (ok)
- **Cert, pending critic review:** Excluded incidence profile `(10,10,10,12)` across all 19 cores of the `f=32, t=4, δ(W)≥2, e(W)=11` involution case. Of 180,325 projections, six survived the primary window check; all 144 omitted-attachment possibilities for those six were refuted. Primary production used 2.91 core-hours. `scratch/E/r6_e11/profile_a11.final.log:1`
- **Cert, pending critic review:** Also excluded profile `(10,10,11,11)` for core `G?Beto`. The other 18 cores remain open in that profile. `ralph/lanes/E/m11.md:125`
- **Enum:** The reverse 74-edge catalogue remains one class short and does not establish a broader exclusion.
- Both proof-bundle hashes verified. No jobs remain, no candidate graph was submitted, and \(R(3,10)\) remains unresolved. The next-round handoff is in `ralph/lanes/E/STATE.md:35`.

## Lane F: Constructions: search for a (3,10,40)-graph (ok)
**Lane F, round 6:** No `(3,10,40)` candidate. The best degree-valid graph still has 24 independent 10-sets.

- **Enum:** Built an exact search over edge matchings for a fixed free-involution quotient. It matched 1,620 brute-force decisions and passed 10 planted order-38 gate checks.
- **Estimate:** On 16 matched order-40 quotients, the new search checked 174 lifts versus 260,096 by direct enumeration (0.02 vs. 0.80 seconds elapsed).
- **Enum:** None of 1,889 labelled order-40 quotient inputs reached 23 independent 10-sets. The deletion search produced 33 nonisomorphic, gate-checked order-38 graphs; none of their 364 tested extensions reached 80. These are finite search results, not a symmetry-family closure.
- **Handoff:** All 21 jobs ended (0.00684 core-hours); no cores requested. Reuse the solver if a new source produces closer quotients; don’t expand the unchanged switch sample. Evidence and commands: `ralph/lanes/F/ROUND6.md:1` and `ralph/lanes/F/STATE.md:1`.

## Lane G: Near-regular degree distributions N(e) (ok)
**Round 6: No new distributions closed.** The baseline remains **278 near-regular distributions plus Case R**. No order-40 candidate was found, and no Lane G jobs are running.

- **Hand + enum:** Perfect matchings fix 20 edges in each equality-root template. Lane A independently verified all 14 signature templates and 112 compatible template–distribution pairs. The strengthened LP excluded none. `ralph/lanes/G/rows/signature_matchings.md:3`
- **Cert:** Three-anchor windows with 0, 1, 2, or 3 double signatures require exactly **9, 11, 15, or 18 exterior edges**, respectively. Both LRAT checkers verified all four lower bounds, and checked examples attain them. `ralph/lanes/G/rows/signature_matchings.md:111`
- **Enum, supplied inputs only:** The inverse scan found no marks among 13,092 supplied e121 rows or 90,223 supplied e122 rows. The six-class census gap remains open. `ralph/lanes/G/REPRO.md:240`
- **Next:** Seek a complete smaller source for the path/leaf configuration. A checked refutation would close two of the 20 remaining e168 pins; the current SAT pilots hit their caps. The handoff and ten conditional U88 keys are in `ralph/lanes/G/STATE.md:33` and `ralph/lanes/G/round6_u88.csv:1`.

## Lane H: Literature scout, claim ledger, Lean (ok)
**Round 6, Lane H — no decision on \(R(3,10)\).**

- **Ledger:** Independently reconciled **278 near-regular MTF distributions plus Case R**, with **10 conditional U88 keys** and **20 open e168 degree-six distributions**. The direct e162 exclusion is counted once. C’s matching reduction and E’s 12-edge certificate are recorded only at their checked scopes. `ralph/CLAIMS.md:3`
- **Lean:** Verified that the degree-six vertices form a clique, conditional on G’s exterior-degree result, and derived the two possible e168 neighbour profiles for an adjacent degree-six pair. The project builds; all 5 targeted and 275 project axiom reports passed. The census remains external to Lean. `lean/R310/ResidueDegreeFive.lean:36`
- **Hand:** Refined A’s marked e122 search for the nine e168 distributions with two degree-six vertices. The profile distinguishes a matching from a three-vertex path among the two added edges; this is a filter, not an exclusion. The smaller C13 control passed at all 52 ordered adjacent roots. `ralph/lanes/H/ROUND6_REVIEW.md:55`
- **Literature:** Found no published result superseding \(40\le R(3,10)\le41\), public bulk order-39 census, or exact published order-30 counts at 88–99 edges. `ralph/lanes/H/LIT.md:138`

The strongest next step is for A/G to use the marked e122 filter on the nine paired cases. The eleven single-degree-six cases still need a method that covers residues with no legal edge addition. No H jobs are running (0 cores); new claims await critic review.

## Critic (ok)
**Round 6:** No order-40 graph passed the gate. The baseline remains **278 near-regular MTF distributions plus Case R**.

- **Confirmed:** C excluded the `(12,12)` wing split in global `R(6), f*=9`. E excluded the full `(10,10,10,12)` involution profile and one core of `(10,10,11,11)`; 18 mixed-profile cores remain open.
- **Confirmed at stated scope:** B’s 5,719,576 deletion-reducible e88 scans and outside-prefix e43 branch returned zero; the e108 certificates cover only 614 supplied critical classes. A/G/H’s marked-strip reductions, G’s local edge bounds, D’s nine-key cover, and F’s finite relift results also checked out.
- **Rejected:** No primary claim at its stated scope. The evidence does not establish a U88 closure, floor 109, or a complete residue census.
- **Rules:** No A–H core, RAM, disk, write, or Git violation observed. Separate idea-scout writes outside lane paths need operator confirmation.
- **New A–H core split:** `2 / 24 / 10 / 3 / 19 / 2 / 18 / 2` (80 total).
- **Best next step:** Find a complete smaller source or local obstruction for the marked two-edge path with the cross endpoint at a leaf. This could close two e168 distributions without filling the six-class census gap.

Full review: `ralph/critic/round_006.md:1`. Next-round directives: `ralph/critic/LATEST.md:1`.
