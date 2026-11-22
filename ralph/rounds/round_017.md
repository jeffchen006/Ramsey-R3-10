# Round 17

Began 2026-11-22T13:12:15; ended 2026-11-22T14:32:42.

## Flow checks
```json
{
 "round": 17,
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
Lane A bound the exact multiplicities for the one-neutral 16/17 package-existence filter (**hand + enum, pending critic**). The weights reproduce all 34 strata and **15,051,526,031 unfiltered headers**. Lane A did not run the full target filter or close a case.

- The weighted counts match all 34,504 literal small-control headers in both directions, retain all 153 plants, and agree with all 2,067 independent predicate receipts. Two destinations with identical degree margins give different answers, so margins alone are not a valid cache key.
- On the 544 target pilot headers, 47 pass both directions, 140 pass only 16→17, 96 pass only 17→16, and 261 pass neither. These are package-existence results, not terminal outcomes.
- Clean replay reproduced ten outputs byte-for-byte. Total lane A work was under 0.08 core-hours; **no jobs remain**.

Lane C has the weights for the full quotient. Evidence and handoff: `ralph/lanes/A/ROUND17_DIRECTION_PROFILES.md:1` and `ralph/lanes/A/STATE.md:1`.

## Lane B: Gluing (t9 <= 88, then a faster gluer) (ok)
Lane B froze the evidence for **2,104,146 named e108 residues** already ruled out at maximal triangle-free degree-seven roots. **Five critical classes remain missing; the degree-seven floor stays at 108.** No new mathematical exclusion or candidate graph.

The archive audit checked **3,066 files**, preserved the labelled rank and pin maps, and rebuilt the manifest byte for byte in **0.0019 core-hours**. Evidence: `ralph/lanes/B/ROUND17_REPLAY.md:1`.

**No jobs running (0 cores).** Target generation stays parked until an independent order-32/e108 source supplies the missing classes, or an exact coverage argument passes a smaller withheld-key test and is priced for the full missing slice.

## Lane C: Theory for the 9-regular case R (ok)
- **Exact filter (`hand + enum`, pending review):** 2,542,514,492 of 15,051,526,031 labelled one-neutral 16/17 headers pass both package-existence checks. Of those, 47 already failed the round-16 joint check, leaving **2,542,514,445** untested at that stage.
- **Scoped exclusion (`hand + enum`):** An independent check found zero survivors among all 35,458,804 headers with `(D16,d16)=(71,5)`. The broader 16/17 case and Case R remain open.
- **Validation:** Matched all 34,504 smaller control IDs and all 544 target pilot IDs in both directions. The clean replay reproduced 17 outputs byte for byte. Total: **0.218 core-hours**. No candidate, new terminal scan, or active jobs.
- **Next:** Request approval to recover and check the physical frame IDs in two shape strata with just 46 and 24 survivors. Evidence and replay: `ralph/lanes/C/ROUND17_REPLAY.md:1`.

## Lane D: New SAT encodings and splits for case R (ok)
**Lane D excluded the marked case \(K=2,\ t=17,\ m=16\), pending critic review.** In R(3) with exactly two deficient pairs, if a marked deficient path lies on exactly 17 pentagons, its 14 untouched vertices span **at most 15 edges**. This does not exclude all 17-pentagon paths, close R(3), or decide R(3,10).

- **Evidence — hand + enum + cert (local):** All 15,282 canonical profiles were refuted. Two LRAT checkers verified every proof during production and again after archive replay. An independent census accounted for all 320,878 ordered shore placements; no ID or weight remained open.
- **Cost:** 2.07748 core-hours and 1.716 GiB of packed certificates. No jobs remain; no candidate was found.
- **Handoff:** `ralph/lanes/D/MIDDLE17.md:1` gives the reduction and replay instructions. `scratch/D/middle17/final/reconciled.log:1` records the final counts.
- **Next:** Request critic approval for a census only at \(m=15\), where exactly one untouched vertex meets three poles. No search of that case was launched.

## Lane E: Automorphisms (the open (p, f) cases) (ok)
**Conditional exclusion of mixed involution core 15**, pending critic review (`hand + enum + cert`). All 142 distinct IDs in the frozen queue were bound to their original cover rows and independently rechecked with CakeLRAT. No fallback was needed.

- On the same 16 IDs, width three took 17.44 CPU-s versus 27.99 CPU-s for width eight, including fresh rechecks. Rounds 16–17 used 0.148 core-hours total.
- Evidence and replay commands: `ralph/lanes/E/shared74_round17.md:48`. No jobs remain.
- Next: ask the critic to verify the exclusion and authorize pricing one of cores 1, 6, 9, or 18. The full `(2,32)` case and `R(3,10)` remain open.

## Lane F: Constructions: search for a (3,10,40)-graph (ok)
**Round 17, lane F:** No candidate. The family with one exceptional site remains open.

- **Hand + cert, submitted for review:** Any 14 consecutive untouched ID8 sites force an independent nine in a triangle-free lift, regardless of crossing signs or vertical edges. The proof uses three squares of a triangular prism; both LRAT checkers passed. `ralph/lanes/F/ROUND17.md:15`
- **Hand + enum:** The marked search has **353,474,849** surviving unsigned combinations of an exceptional row and a first external footprint, down from 847,881,702. Two independent counts agree. These are combinations, not graphs. `ralph/lanes/F/ROUND17.md:29`
- **Next:** Do not scan the joint combinations. Test a shared parity filter on the 7,448 remaining footprints with no double contact. The pilot rejected 33/33 sampled footprints of that type; the rest are untested.
- **Resources:** 0.01267 core-hours including clean replay. No running or stopped jobs; no extra cores requested. The best observed order-40 score remains 24 independent tens. `ralph/lanes/F/STATE.md:1`

## Lane G: Near-regular degree distributions N(e) (ok)
- **Hand + enum + local cert, pending review:** Rebound 1,419 prior proofs. For the marked `h=8` case only, old partial-support proofs exclude **1,935 additional alignment IDs** across 27 schemes. The smaller controls reproduced 24 and 0 classes.
- **Local cert:** Both LRAT checkers passed all **96 preregistered fresh IDs**. **155,746 IDs remain untested.** No additional scheme or degree distribution closed.
- **Estimate:** Direct coverage of the remainder would cost **7.53–8.65 core-hours** and **16.22–22.05 GiB** of raw receipts at sampled prices. These are not tail bounds.
- **Handoff:** Used 0.0389 core-hours; no jobs running. Replay evidence is in `ralph/lanes/G/ROUND17_REPLAY.md:3`. Critic review and authorization are needed before production.

## Lane H: Literature scout, claim ledger, Lean (ok)
**Round 17 — Lane H.** \(R(3,10)\) remains open at **40–41** in the sources checked through November 22, 2026. I found no public bulk order-39 catalogue or new exact dense order-30 counts. `ralph/lanes/H/LIT.md:409`

- **Lean H-032, pending review:** Two distinct poles share at most two sites besides the middle. They share at least one iff the middle is not their unique common neighbor. The smaller MTF controls produced 600 rows showing why “the middle is not a deficient endpoint” cannot replace that condition. The pinned build and all 5 targeted and 344 project axiom reports passed. `lean/R310/PoleMultiplicity.lean:91`
- **Ledger:** Imported round-16 verdicts, including F’s cyclic four-deletion family exclusion, not an unrestricted involution exclusion. The confirmed balance stays at **238 near-regular distributions plus Case R** and ten conditional U88 keys. `ralph/CLAIMS.md:3`

**Team outlook:** D has the strongest path to another certified regular subcase; its four workers remain active. A/C’s necessary filter reduced 15.05 billion marked headers to **2,542,514,492** that pass in both directions, pending review—not terminally compatible completions. E’s 142-ID core-15 exclusion is also pending. No H jobs remain; next is critic review and exact reconciliation of D’s completed and open profiles.

## Referee (claude-opus-5-5-high, failed)
(the turn failed: exit 3; log scratch/flow/turns/r017_referee.log; )
r310-referee: session cleared; next turn starts a new context


## Critic (ok)
**Round 17: three scoped exclusions confirmed.** No flow-verified graph; 238 near-regular MTF degree distributions plus Case R remain open.

- **D:** All 15,282 profiles reconcile. In marked `K=2, t=17`, the 14 untouched vertices span at most 15 edges.
- **E:** All 142 outstanding proofs rechecked. Mixed core 15 is conditionally excluded; cores 1, 6, 9 and 18 remain.
- **A/C:** The `(71,5)` stratum has zero survivors. Across all strata, 2,542,514,492 headers pass both package-existence checks—not joint compatibility.
- **B/F/G/H:** Confirmed the archive, prism and counting results, proof transfers, and Lean theorem within their stated scopes. No mathematical claim rejected. H’s report of active D workers was stale; no referee report was available.
- **Rules and allocation:** No rule breach found; scratch used 95.7/150 GB. New A–H ceilings: **6/2/5/28/16/2/8/2**, totaling 69.
- **Best next step:** Census D’s adjacent `m=15` layer. Its one exceptional pole and one triple row may keep the search small; no proof campaign is authorized yet.

Full review: `ralph/critic/round_017.md:1`. Directives: `ralph/critic/LATEST.md:1`. Allocation: `ralph/ALLOC.md:1`.
