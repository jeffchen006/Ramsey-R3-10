# Round 11

Began 2026-11-22T04:38:23; ended 2026-11-22T06:01:13.

## Flow checks
```json
{
 "round": 11,
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
- **Cert, pending critic:** Independently bound all **21,236** mixed d8/j2/δ(T)=2 middle-only roles to Lane G’s dual-checked LRATs. The final manifests match byte-for-byte, with zero failed IDs. Lane A did not rerun the proof checkers. The 69,278 matching roles remain outside this result.
- **Hand + enum, pending review:** All 6,160 order-21 marks have a singleton deficit. This strengthens the degree floor to \(d_T(s)\ge |T|-21\) for retained noncross B anchors when the B pivot has degree 9, and for original-degree-9 anchors when the pivot has degree 8.
- **Coverage only:** Checked all 51,395 direct order-24 role and pin maps. A real addback passed in both label orders; two double-deficit mutations exercised the hole branches. A real order-25 control confirms the equality anchor need not be minimum-degree.

No Lane A jobs remain. No candidate, whole-distribution exclusion, or R(7) closure. Replay: `ralph/lanes/A/ROUND11_REPLAY.md:9`.

## Lane B: Gluing (t9 <= 88, then a faster gluer) (ok)
**Lane B round 11:** Recovered 47 deletion-critical order-32/e108 classes from 377 e98 parents. The partial census is **2,104,146 of 2,104,151**, with **five missing**. The generation replay matched byte-for-byte.

- **Scoped cert, pending critic review:** 37 checked demand cliques and 10 dual-checked LRAT proofs rule out all 47 new residues at maximal triangle-free degree-seven roots. This does not establish floor 109.
- **Enum:** All 560 e95 parents produced zero critical outputs in the degree-4 and degree-5 arms, completing the e95 source search with the earlier degree-6–8 runs.
- **Next:** Request critic approval to pilot the 7,954 fresh e98 parents from older cohorts. The full queue is estimated at ~310 CPU-seconds for lifting alone, with no yield guarantee. It was not run.

No jobs remain running. No candidate graph, distribution closure, or e88 change. Replay details: `ralph/lanes/B/ROUND11_REPLAY.md:1`.

## Lane C: Theory for the 9-regular case R (ok)
**Submitted for critic review:** In the 9-regular case with maximum codegree five, a \(K_{3,3}\) cannot have opposite anti-triple windows of orders 22 and 21. This is a hand + enum result with checked LRAT proofs for the 32 maps that survived both enumerators.

- The independent replay matched all **11,657,178 rooted alignments** across **1,118,436 hosts**. After the 32 proof checks, none remain unresolved. Evidence: `ralph/lanes/C/ROUND11_REPLAY.md:61`.
- Combined with the prior 22/22 exclusion, an order-22 window forces the opposite window to have order at most 20. `ralph/lanes/C/proofs/reciprocal_r11.md:31`
- No Lane C jobs remain. No candidate was found; Case R and \(R(3,10)\) remain open.

## Lane D: New SAT encodings and splits for case R (ok)
**Round 11, lane D:** R(3,10) and case R(3) remain open. No candidate graph was found.

- **Hand + enum, submitted for review:** Every hypothetical R(3) graph has two vertex-disjoint codegree-one nonedges with **different unique common neighbors**. This reduces the required four-star roots from **117 to 111**. The final 382 cases in the single-witness branch also exhausted without a profile library. This is not a Section 7 certificate. `ralph/lanes/D/MONO_WITNESS.md:3`
- **Cert, local only:** Of 13,078 witness-star branches, 1,351 contain an explicit independent ten. All 1,351 LRAT proofs passed both checkers; 11,727 branches survive this test. `scratch/D/wit11/branch-audit.log:1`
- **Hand:** The number \(K\) of codegree-one nonedges is even, since counting opposite diagonals gives \(2C_4=1080+K\). `ralph/lanes/D/DEFECT_EXCESS.md:3`
- **Next:** Test whether the two three-vertex paths, including their witnesses, can be chosen vertex-disjoint. Only nine marked roots need investigation for the contrary case. H/critic: please audit the path joins and the distinction between capped and unrestricted libraries.

**Running now:** no D jobs, PIDs, or cores in use. Handoff: `ralph/lanes/D/STATE.md:1`.

## Lane E: Automorphisms (the open (p, f) cases) (ok)
- **Hand + enum + cert, pending critic:** Excluded cores 7 and 13 in the mixed \(f=32\) profile under the all-graph E-021 premise. Independently matched 825,703 lifts, replayed the full receipts, and regenerated and checked all 40 terminal CakeLRATs. Evidence: `ralph/lanes/E/shared74_round11.md:46`.
- **Hand + cert, pending critic:** Every triangle-free 26-vertex graph with \(\alpha\le7\) and at most 74 edges has minimum degree at least four. All 191 parent proofs passed fresh regeneration and replay. This result does not use E-021. Evidence: `ralph/lanes/E/window74_d3.md:53`.
- **Enum:** The new degree floor pruned none of the 42 archived heavy-core pilot residues. No full run on cores 9 or 18.
- **Handoff:** Nine mixed cores remain if the exclusions are accepted. Price core 16 next. No live jobs (0 cores), no candidate graph, and \(R(3,10)\) remains open.

## Lane F: Constructions: search for a (3,10,40)-graph (ok)
**Round 11: no candidate submitted.** The best observed order-40 score remains 24 independent ten-sets.

- **Hand + enum, pending critic:** Every triangle-free signing of a degree-eight cyclic unsigned 19-fiber card has at least **47** independent ten-sets. After removing any one fiber, at least **28** remain; after removing any two, at least **6** remain. Thus even six arbitrary new vertices cannot turn the 34-vertex remainder into a target.
- **Cert, pending critic:** All 27 intact profiles have independently replayed dual LRAT proofs excluding zero. The stronger numerical bounds use 243 checked deletion cases and double counting, not LRATs.
- **Resources:** 9.00 CPU-seconds total; zero target extensions needed. No jobs or PIDs remain.
- **Next:** Retire this family. Price the variant with cyclic crossing weights but independently chosen vertical edges. No additional cores requested.

Evidence and replay: `ralph/lanes/F/ROUND11.md:1`. Handoff: `ralph/lanes/F/STATE.md:1`.

## Lane G: Near-regular degree distributions N(e) (ok)
**Lane G, round 11:** No candidate and no whole-distribution closure. **278 near-regular distributions plus Case R remain open.**

- **Cert, independent audit pending:** Bound all 21,236 dual-checked LRAT proofs for the mixed `d8, j=2, δ(T)=2` path/middle tranche. The 69,278 matching roles are not covered. `ralph/lanes/G/ROUND11_REPLAY.md:3`
- **Hand + enum + inherited cert, pending review:** A pivot swap excludes all 30,800 B-side equality roles in the `d8, j=1` order-24 slice. Any surviving `d8` B-side equality case reduces to `j=3, δ(T)=4`; that slice is still open. `ralph/lanes/G/rows/pinned_anchor_swap.md:22`
- **Pilot:** The direct encoding matched 2,235 literal small addbacks. It produced 7/27 replayed `d8` certificates and 0/12 `d9` certificates; all other runs hit conflict caps. No production sweep is justified. `ralph/lanes/G/ROUND11_REPLAY.md:70`

No Lane G jobs remain. Next: review the swap and audit the middle tranche; seek a new cut before scaling A-side completion.

## Lane H: Literature scout, claim ledger, Lean (ok)
**Round 11, lane H — \(R(3,10)\) remains open.** No verified candidate or whole-distribution closure; the confirmed baseline is 278 near-regular MTF distributions plus Case R.

- **Lean:** Proved G’s 15-exterior-vertex contradiction and the resulting noncross-anchor degree bound. Also proved D’s empty/star/triangle classification. The pinned build and all 6 targeted and 306 project axiom checks passed. Neither result certifies a catalogue or search. `ralph/lanes/H/ROUND11_REVIEW.md:3`
- **Ledger:** Imported round-10 verdicts and recorded round-11 submissions at their actual scope. B’s 47 new keys and receipt identities match, leaving **five missing** pending critic review. H did not replay the proofs; floor 109 is not established. `ralph/CLAIMS.md:211`
- **Literature:** Found no newer Ramsey decision, public bulk order-39 catalogue, or new exact dense order-30 count. `ralph/lanes/H/LIT.md:238`

B’s 7,954 untried exact parents are the clearest next step, subject to critic approval. C’s 22/21 stream has 32 checked local repairs, but its independent census replay remains open. No H jobs or cores remain in use.

## Referee (gemini-4-neon-xhigh, failed)
(the turn failed: exit 3; log scratch/flow/turns/r011_referee.log; )
r310-referee: session cleared; next turn starts a new context


## Critic (ok)
**Round 11: no verified candidate or whole-distribution closure.** The baseline remains 278 near-regular MTF distributions plus Case R.

- **B:** Confirmed 47 new e108 classes and their scoped extension proofs. The census is **2,104,146 of 2,104,151**; floor 109 is not established.
- **C/D:** Confirmed C’s cap-five 22/21 reciprocal-window exclusion, including all 32 proof repairs. Confirmed D’s distinct-witness reduction from 117 to 111 sufficient roots.
- **A/G, E, F, H:** Confirmed the 21,236 middle-only proof bindings and pivot reduction; E’s two conditional core exclusions and separate degree floor; F’s 47/28/6 bounds; and H’s two Lean results.
- **Rejected:** None at stated scope. No rule break observed or referee GAP submitted. Final check: zero busy solvers, 88.2/150 GB scratch.
- **Round 12 cores:** A4, B18, C5, D11, E23, F3, G14, H2 — **80 total**.
- **Best next step:** B’s approved 7,954-parent e98 wave targets the five missing classes. Even full recovery still requires extension checks for the reducible classes.

Full review: `ralph/critic/round_011.md:1`. Directives: `ralph/critic/LATEST.md:1`. Allocation: `ralph/ALLOC.md:1`.
