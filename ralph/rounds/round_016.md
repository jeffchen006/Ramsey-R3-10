# Round 16

Began 2026-11-22T11:50:32; ended 2026-11-22T13:12:15.

## Flow checks
```json
{
 "round": 16,
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
- **Hand + enum, pending critic:** The one-neutral cap-five 16/17 case has **15,051,526,031 labelled headers** across 34 strata. The count uses bucket products without generating the Cartesian product. No case was closed. `ralph/lanes/A/ROUND16_ONE_NEUTRAL.md:68`
- **Calibration passed:** Literal enumeration matched all 34,504 smaller headers in each read direction. All 153 planted graphs reconstructed in both directions, and all 306 broken crossings were rejected. The clean replay matched the frozen artifacts.
- **Handoff:** Lane C has 544 bound pilot headers for terminal pricing. Lane A used about 0.010 core-hours and has no running jobs. Await Lane C’s pricing before considering production. `ralph/lanes/A/STATE.md:30`

## Lane B: Gluing (t9 <= 88, then a faster gluer) (ok)
- **Certificate inventory, pending critic review:** All 1,875 supplied critical e108 graphs match archived receipts: 1,431 demand cliques and 444 dual-checked LRATs, with zero unbound keys. An independent merge confirms 2,104,146 distinct covered keys when combined with the accepted reducible list. Five critical graphs remain missing; the degree-seven floor stays at 108.
- **Descent calibration:** One-edge deletion recovered all 13 withheld addable graphs in the smaller class and correctly missed the saturated C5. All supplied e108 criticals admit a triangle-free edge addition, but no independent e109 source was found, so target descent stopped.
- **Handoff:** No candidate graph or running jobs. Critic/H can review the crosswalk and replay instructions in `ralph/lanes/B/ROUND16_REPLAY.md:1`.

## Lane C: Theory for the 9-regular case R (ok)
**Case R remains open.** The one-neutral `16/17` pilot found no compatible row-package assignment on **544 of 15,051,526,031** labelled headers (`hand + enum`, pending review). **15,051,525,487** remain untested.

- An independent audit confirmed 497 headers with an empty package domain and 47 with no compatible join, including all eight headers where the literal join hit its cap. Both implementations retained all 153 smaller planted graphs and agreed on 1,596 terminal outcomes.
- The direct pilot took 2.60 CPU-seconds; the independent audit took 166.99. The projected full scan still costs about **4,348 core-hours** with the modeled cache, before pricing unseen tails. No production scan was launched; no jobs remain.
- Evidence and replay: `ralph/lanes/C/ROUND16_REPLAY.md:1`. Next: ask the critic to authorize pricing an exact weighted count by package-demand profile rather than another per-header scan.

## Lane D: New SAT encodings and splits for case R (ok)
**Lane D’s proof pilot passed; the full \(K=2,t=17,m=16\) slice remains open.** No exhaustive run was launched.

- **Enum:** Independently rebuilt all six middle-star supports and their 15,282 profile orbits. The CNF binding accepted all 125 planted smaller paths and rejected all 125 one-bit corruptions.
- **Cert (local):** All 155 fresh profiles and both previously capped profiles were UNSAT. Both LRAT checkers passed on every independently rebuilt CNF and again on archive replay. The slowest profile took 0.75 CPU-s end to end.
- **Estimate:** The full roster would take 1.34 core-hours for production and checking, plus 1.14 for separate replay. Compressed CNFs and proofs project to 1.53 GiB before metadata.
- **Next:** Request critic approval for **4 cumulative core-hours and 3 GiB**, initially at most four workers. No lane-D jobs are running. The \(m\le15\) cases and R(3) remain open.

Evidence: `ralph/lanes/D/MIDDLE16.md:1`; replay receipt: `scratch/D/middle16/replay.log:1`.

## Lane E: Automorphisms (the open (p, f) cases) (ok)
**Core 15 remains open.** The independently regenerated cover matched byte for byte, and all eight shards replayed: 34 branches, 94,738 projections, and 716,045 lifts. The exact queue contained **142 unresolved lifts**, exceeding the critic’s 100-ID limit. No target proof runs were launched.

The six-site positive, negative, and deliberately misbound CNF controls passed. Total cost was **0.097 core-hours**; no jobs remain and no candidate was found.

Replay evidence is in `ralph/lanes/E/shared74_round16.md:60`. If the critic authorizes proof pricing, 16 dispersed IDs are ready, including both queue extremes. No rescan is needed.

## Lane F: Constructions: search for a (3,10,40)-graph (ok)
**Lane F, round 16 — hand + cert, pending critic review.** The ID8 36-card cannot be extended by even one vertex without creating a triangle or an independent ten. This holds for arbitrary crossing signs and verticals; it does not rule out the 36-card itself.

The proof reduces 89,445 possible attachment patterns to 2,623 symmetry representatives. Both `lrat-check` and `cake_lpr` verified the combined certificate. Together with the previously reviewed reductions, this excludes the entire four-deletion cyclic 36-card family, not an unrestricted automorphism case. **R(3,10) remains open.**

All jobs finished: **0.08379 core-hours**, zero active PIDs, no candidate. Next: critic replay before retiring the family. Proof and replay instructions: `ralph/lanes/F/ROUND16.md:1`.

## Lane G: Near-regular degree distributions N(e) (ok)
- **Local exclusion (hand + enum + cert, pending critic):** All 1,828 alignments in the `h=8` `leaf+leaf.1` scheme for adjacent degree-six equality roots at `e=170` are excluded. The cover combines 356 prior IDs, 211 new IDs from the transfer pilot, and 1,261 direct tail proofs. Both LRAT checkers passed the full replay.
- **Calibration:** The smaller cases reproduced exactly 24 and 0 canonical classes. The independent scout audit counted 10,386 distinct covered IDs across 30 schemes, counting overlaps once.
- **Scope:** No other scheme was extended, no distribution or U88 key was closed, and no candidate was found. The 238 near-regular distributions plus Case R remain open.
- **Handoff:** Measured work used 0.0796 core-hours; no jobs remain. Critic and Lane H: review only the named local exclusion using `ralph/lanes/G/ROUND16_REPLAY.md:37`.

## Lane H: Literature scout, claim ledger, Lean (ok)
**R(3,10) remains open.** No flow-verified graph was found, and no whole case closed this round. The November 22 literature check found no result superseding the published bounds of 40–41, no public bulk order-39 catalogue, and no new exact dense order-30 counts. See `ralph/lanes/H/LIT.md:387`.

- **Lean, pending critic review:** At a marked path with 17 cross-wing edges and 16 untouched edges, the seven other middle neighbors have exactly 2/2/4 contacts under the explicit codegree hypotheses, and every untouched vertex has exactly two middle contacts. The pinned build, 7 targeted and 339 project axiom checks, and smaller controls passed. This proves the structural implication, not a case exclusion. `lean/R310/MiddleStar.lean:198`
- **Ledger:** Imported the round-15 verdicts and recorded round-16 submissions as pending. The confirmed balance remains 238 near-regular MTF distributions plus Case R, ten conditional U88 keys, five conditional E cores, and five missing B critical keys. `ralph/CLAIMS.md:3`

D’s 155 fresh dual-checked pilot proofs give the strongest measured next step for a bounded regular subcase. I recommend critic review of its proof and disk estimates before expanding. C’s one-neutral pilot leaves over 15 billion headers untested; that route needs a stronger filter, not a production scan. No H jobs are running.

## Referee (claude-opus-5-5-high, failed)
(the turn failed: exit 3; log scratch/flow/turns/r016_referee.log; )
r310-referee: session cleared; next turn starts a new context


## Critic (ok)
**Round 16 Review**
- Confirmed A/C header counts and 544-header pilot scope; no full one-neutral exclusion.
- Confirmed B’s 1,875-key crosswalk, 2,104,146 named union, and five missing criticals; floor remains 108.
- Confirmed D’s 157 local proofs and full 15,282-profile production price.
- Confirmed E’s exact 142-ID queue; no core closure yet.
- Confirmed F’s ID8 extension obstruction and cyclic four-deletion family scope.
- Confirmed G’s 1,828-ID aligned-scheme exclusion; no distribution debit.
- Confirmed H’s Lean middle-star implication; conditional only.
- Fourth-round audit reconfirmed the 238-distribution balance and MTF degree-six floor 122.
- No claims rejected; referee review is `UNCHECKED` because the referee turn failed.
- No rule violations, cap kills, candidates, or active jobs found; scratch is 93.5 GB.
- New allocation: `A/B/C/D/E/F/G/H = 5/2/4/26/12/2/4/2` cores, total 57.
- Highest-value direction: D’s bounded `K=2,t=17,m=16` proof campaign, capped at four workers and 4 cumulative core-hours.
- Wrote `ralph/critic/round_016.md`, replaced `ralph/critic/LATEST.md`, and updated `ralph/ALLOC.md`.
