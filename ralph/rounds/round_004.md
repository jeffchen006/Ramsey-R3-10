# Round 4

Began 2026-11-21T19:51:36; ended 2026-11-21T21:09:10.

## Flow checks
```json
{
 "round": 4,
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
Lane A finished the round-4 audit. **No new cases closed; \(R(3,10)\) remains unresolved.**

- **Cert, MTF only:** Packaged the degree-six floor-120 proof in a 3.8 MiB bundle. All 74 regenerated CNFs passed both LRAT checkers, including the six rows missing from the earlier bundle.
- **Cert, MTF only:** Independently replayed the degree-seven floor-107 proof: 19,589 residue graphs, 19,521 incompatibility witnesses, and 68 exceptions verified by both LRAT checkers.
- **Ledger:** Confirmed 55 incremental cuts and 23 conditional cuts. The tally leaves 376 near-regular distributions plus Case R. Complete e88 gluing exclusion would remove 13 more.

The end-to-end replay passed in 90 seconds. Instructions are in `ralph/lanes/A/FLOOR_AUDIT.md:70`. No Lane A jobs are running. Next: audit any complete e120 or e107 residue cover.

## Lane B: Gluing (t9 <= 88, then a faster gluer) (ok)
**Lane B, round 4: \(R(3,10)\) remains open.** No candidate graph or new degree-distribution exclusion.

- **Enum:** The completed up86 scan found zero maximal triangle-free completions across 4,751,963 distinct e88 duals. Independent SAT agreed on all 32 sampled inputs. Every dual in this slice meets the prefix root condition, so the scan does not cover the remaining e88 cases.
- **Enum:** The checkpoint matched all 1,800 canonical e86 graphs and validated all 147,335 e87 graphs. The disjoint tail from the remaining 13,901 e87 parents can now start before the full prefix finishes.
- **Estimate:** The faster gluers matched the controls, but the e52/e44 branches still project to about 893 CPU-hours—49.6 hours on 18 cores before final sorting and scanning. Neither full branch was launched.
- **Hand:** One 162-edge distribution forces a four-cycle on its degree-nine vertices. A second forces both degree-seven residues to have 107 edges. Neither is excluded. See `ralph/lanes/B/CYCLE162.md:1`.
- **Live:** Prefix `1180084` (16 cores), e43 `3921182` (1 core, 23/48 chunks), and tail87 `2576750` (queued behind e43). Next: audit the terminal counts and the tail’s exact input partition. Handoff: `ralph/lanes/B/STATE.md:7`.

## Lane C: Theory for the 9-regular case R (ok)
**Round 4 — Lane C:** \(R(3,10)\) and \(R(6)\) remain open. No candidate graph was found.

- **Cert, pending critic review:** Replayed all 480 diagonal-five P3 proofs at \(e(X)=63\), lowering its residue bound to 62. Replayed all 70 diagonal-three/four proofs at \(e(X)=65,66\), lowering those bounds to 64.
- **Cert, pending critic review:** For an isolated codegree-six pair at \(e(X)=80\) with a degree-three anchor, replayed all 25 equality proofs, lowering the anchored residue bound to 64. This does not exclude the entire pair case.
- **Hand:** An isolated pair’s residue has minimum degree at least four at \(e(X)=81\), and at most one degree-three vertex at \(e(X)=80\). A diagonal-five P3 cannot have both incident cross-edge counts at least eight.
- **Running:** At 20:32:40 CET, diagonal-five \(e(X)=62\) had 702/1,320 keys checked, 543 replayed, and no observed caps. Four producer cores (`1345478`, `1345482`, `1345489`, `1345498`) and four replay cores (`1752307`, `1752313`, `1810068`, `1946269`) remain live.
- **Next:** Finish the exact \(e(X)=62\) coverage audit, then prioritize diagonal-three/four \(e(X)=64\). H and the critic can review the reductions and proof bindings in `ralph/lanes/C/ROUND4_REPLAY.md:1`; the job handoff is in `ralph/lanes/C/STATE.md:22`.

## Lane D: New SAT encodings and splits for case R (ok)
**Round 4: no new certified exclusion or graph candidate.** R(3) still has 110 surviving rooted kernel representatives. No Lane D jobs are running.

- **R(3), hand + enum:** Two new attachment constraints preserve all five C16 classes. They reject 39 of 47 sampled profiles on kernel 88’s side 1 and 104 of 200 on kernel 149. Both sides still have surviving profiles; the unsplit kernel 149 test hit its 32 CPU-second cap. `ralph/lanes/D/OPPOSITE_SHADOW.md:24`
- **R(3), enum:** Whole-family upper bounds are too loose to justify a sweep. Adding cycle-count constraints to fixed edges slowed the matched SAT tests. `ralph/lanes/D/PIN_BOUND.md:32`
- **R(4), enum:** All 67,730 marked K3,4 partitions pass the single-group attachment test. Every witness was independently checked. `ralph/lanes/D/TRIPLE_U.md:24`

Next: use the attachment constraints to build a smaller exact split. H/critic review requested for the hand reductions; the handoff is in `ralph/lanes/D/STATE.md:1`.

## Lane E: Automorphisms (the open (p, f) cases) (ok)
- **Excluded `(2,28,a=6)` — `enum`, pending critic review.** A hand reduction forces four overlapping attachments. Their four 17-vertex windows must average at most 62 in a weighted degree count, but two independent checks found a minimum of 66 across all 7,057 eligible markings. See `ralph/lanes/E/overlap28.md:1`.
- This fills the last reported gap for involutions with 28 fixed vertices. H and the critic should review the reduction and combine it with the prior exclusions.
- **`f=32` remains open.** The capacity filter removed 775 cores. Three of nine pinned SAT probes gave unchecked UNSAT; six hit their CPU caps. Next, test the two cubic cores in the `t=4` branch. See `ralph/lanes/E/crown32_pressure.md:1`.
- No live lane-E jobs or candidate graphs. Handoff and evidence are in `ralph/lanes/E/STATE.md:1`.

## Lane F: Constructions: search for a (3,10,40)-graph (ok)
Round 4 lowered Lane F’s best degree-valid score from **44 to 24 independent 10-sets**. The two nonisomorphic near misses have 178 and 179 edges, degrees 8–9, and a fixed-point-free involution. Both scores were independently recounted. The gate rejected both, so \(R(3,10)\) remains unresolved.

- **Enum:** The new completion search passed the order-35 and order-38 controls. It exhausted all 7,191 distinct four-vertex repair cores of the score-26 seed without a valid completion. This excludes only that seed’s neighborhood, not an automorphism family.
- **Handoff:** Saved both score-24 seeds and replay details in `ralph/lanes/F/ROUND4.md:113`, updated `ralph/lanes/F/STATE.md:3`, and notified Lane E.
- **Resources:** 0.1035 core-hours. No live jobs and no request for more resources. Next: sample previously unseen cores from the two score-24 seeds.

## Lane G: Near-regular degree distributions N(e) (ok)
- **Cert — eight new \(e=168\) cuts.** Six use a signature-graph constraint with exact Farkas certificates; two use parity and pair packing. None relies on either gluing floor. Pending review, **368 near-regular distributions plus Case R remain**. A complete \(e(H_9)=88\) gluing exclusion would cut 12 more. Evidence: `ralph/lanes/G/round4_cases.csv:1`.
- **Cert — supplied residues only.** Checked all 1,223 known \(e(H_6)=120\) residues at any total edge count, and all 13,092 known \(e(H_6)=121\) residues through total \(e=169\). Eleven of the latter proofs are pinned to \(e=169\).
- **Open — six catalogue classes are still missing.** The combined cover is 14,389 of 14,395, so there is no new global degree-six floor and \(R(3,10)\) remains undecided.
- **Handoff:** No Lane G jobs remain. H and A have the cut index and replay instructions in `ralph/lanes/G/REPRO.md:148`. Next priority: obtain the six missing classes through an exact source or targeted decomposition rather than another broad sweep.

## Lane H: Literature scout, claim ledger, Lean (ok)
Round 4, lane H: **\(R(3,10)\) remains unresolved.** No order-40 graph has passed the flow gate.

- **Audit:** Confirmed the premises and exact case accounting for G’s degree-six floor: 55 new exclusions at \(e=167\), independent of either gluing floor. The checked ledger stands at **376 near-regular distributions plus Case R**; complete e88 gluing would cut 13 more. See `ralph/lanes/H/FLOOR6_REVIEW.md:1` and `ralph/CLAIMS.md:3`.
- **Lean:** Four theorems passed the build and axiom audit, covering attachment domination, demand incompatibility, and the degree-six edge-count bridge. The finite catalogues and LRAT coverage remain external to Lean. See `lean/R310/RootDemand.lean:11`.
- **Literature:** Found no later exact resolution, public order-39 bulk census, or exact dense order-30 counts. Source details are in `ralph/lanes/H/LIT.md:100`. No H jobs remain running.

**Best next step:** G’s fixed-root route has the strongest evidence. A complete e120 cover or an obstruction to the omitted classes would remove **47 more** distributions. C’s checked path restrictions narrow \(R(6)\) without closing it; E’s \((2,28,a=4)\) exclusion closes that symmetry branch for all graphs.

## Critic (ok)
- **Confirmed:** Eight new MTF degree-distribution exclusions at 168 edges leave **368 near-regular distributions plus Case R**. A complete e88 gluing exclusion would remove 12 more.
- **Deep audit passed:** All 74 degree-six floor proofs replayed with both LRAT checkers. The private-cell argument and all 55 earlier incremental cuts checked out.
- **Also confirmed:** The `(2,28,a=6)` involution exclusion, the scoped \(R(6)\) bounds, and both score-24 near misses. No order-40 graph passed the flow gate.
- **Rejected:** No properly scoped new exclusion. The old counts are superseded; the e62 replay and global e120/e121 coverage remain unchecked.
- **Rules and cores:** No confirmed rule violations. New A–H split: **2 / 18 / 8 / 2 / 21 / 4 / 23 / 2 = 80**.
- **Best next step:** Locate the six missing classes across e120/e121, or prove that none of the omitted e120 residues can extend at 168 edges. That would close **39 more distributions**.
- Full review: `ralph/critic/round_004.md:1`. Next directives: `ralph/critic/LATEST.md:1`.
