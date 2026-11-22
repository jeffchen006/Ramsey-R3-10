# Round 18

Began 2026-11-22T14:32:42; ended 2026-11-22T15:58:44.

## Flow checks
```json
{
 "round": 18,
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
 "scout_turns": {
  "R": "ok",
  "N": "ok",
  "T": "failed"
 },
 "referee_turn": "failed"
}
```

## Lane A: Toolchain and certified SAT (the 99 open R(7) cubes) (ok)
Lane A handed Lane C all **70 labelled headers** that pass both marginal tests (`enum`, pending critic): 46 of 32,340 in the `(67,5)` slice and 24 of 28,301 in the `(68,4)` slice. One had already been tested in the pilot, leaving 69 new joint checks.

The independent literal evaluator matched every group decision across all 60,641 raw headers. The smaller control reproduced all 34,504 IDs and retained all 153 planted marks. All 53 hash bindings passed.

Handoff: `scratch/A/r18/survivors.cases.tsv:1`. Evidence and replay: `ralph/lanes/A/ROUND18_PHYSICAL_IDS.md:1`.

Lane A used 0.049 core-hours; no jobs remain. Lane C owns the joint checks. No new graph or case closure is claimed.

## Lane B: Gluing (t9 <= 88, then a faster gluer) (ok)
Lane B remained parked per the critic’s directive (`ralph/lanes/B/STATE.md:3`). Five critical 32-vertex, 108-edge classes are still missing, so the degree-7 floor stays at 108. No jobs or replays ran. Reopen only with an independently sourced new key or an exact coverage argument with a withheld-key calibration and a full-slice cost estimate.

## Lane C: Theory for the 9-regular case R (ok)
**Hand + enum, pending critic:** Two marked one-neutral 16/17 slices have no completion. For `(67,5;2333,3334)`, 46 of 32,340 headers passed both marginal filters; for `(68,4;2333,3334)`, 24 of 28,301 passed. Independent join checks found **zero compatible tuples** across all 70 survivors.

One survivor was already tested, so 69 joint failures are new. Case R remains open, with 2,542,514,376 marginal survivors still untested for joint compatibility.

The clean replay matched all 16 output comparisons. Total cost was 0.13740 core-hours. No candidate and no running jobs. Evidence: `ralph/lanes/C/ROUND18_REPLAY.md:1`.

Next: critic review of the two scoped exclusions. Price the next 159-survivor slice separately if authorized.

## Lane D: New SAT encodings and splits for case R (ok)
**Lane D, round 18 — hand + enum, pending critic review.** For marked `R(3), K=2, t=17, m=15`, 162 of 1,143 support types pass the necessary Hall tests: 99 with the exceptional pole inside the triple and 63 outside. Accounting for the triple rejects 22 types that the ordinary two-pole test misses.

Independent counting and two clean replays confirmed the roster and its weight of 651,000 oriented, pole-labelled supports. **The `m=15` case remains open.** No target wing pairs were constructed and no SAT jobs were launched.

**Resources:** 0.00198 core-hours; no running or stopped jobs.  
**Next request:** authorize a count-only wing join capped at 90 CPU-seconds, without materializing the 4.08 billion naive pairs.  
**Evidence:** `ralph/lanes/D/TRIPLE18.md:1`; handoff in `ralph/lanes/D/STATE.md:1`.

## Lane E: Automorphisms (the open (p, f) cases) (ok)
**Lane E, round 18: core 1 remains open.** No candidate graph or new case closure.

- **Enum:** Independently regenerated the ordered cover for `G?bFbo` under E-021: 24 branches, 68,323 projections, and 565,531 lifts. The three pilot bands replayed cleanly and left 24 terminal IDs.
- **Cert, pilot only:** Both proof routes checked the same 16 IDs, including fresh rebinds. Width three took 13.98 CPU-s; width eight took 26.64 CPU-s.
- **Estimate:** A full scan and independent replay would take about 519 CPU-s. Request authorization to obtain the exact terminal queue, with two workers and no bulk proof run.
- **Resources:** Used 0.03008 core-hours and retained about 53 MiB. No jobs remain.

Report: `ralph/lanes/E/shared74_round18.md:1`. Evidence: `scratch/E/r18_shared/freeze.1.sha256:1`.

## Lane F: Constructions: search for a (3,10,40)-graph (ok)
**Lane F, round 18 — hand + enum, pending critic review.** The parity test ruled out **7,184 of 7,448** contact patterns that meet at most one endpoint per untouched site; 264 remain open. Each exclusion applies to both the exceptional endpoint and the exterior pole.

Two independent counts agree: **16,182,483 unsigned joint headers remain**, down from 353,474,849 without scanning the pairs. These are possible contact patterns, not graph realizations. No candidate was found, and no unrestricted Ramsey case was closed.

A clean replay checked every deduction and reproduced both counts. Total cost: **0.00420 core-hours**; **no jobs running**. Evidence: `ralph/lanes/F/ROUND18.md:1`.

**Next request:** one worker to pilot the 3,709 exterior patterns with exactly one double contact. That filter could apply to 15,573,942 remaining headers through one role or the other; its exclusion rate is unknown.

## Lane G: Near-regular degree distributions N(e) (ok)
**Local exclusion certified, pending critic review.** Lane G ruled out `middle+middle.2` for the marked e170 adjacent degree-six equality pair with `h=8`. All 16,350 labelled alignments reconcile to checked proofs. Both LRAT checkers passed all 2,024 new certificates, and a clean replay verified 2,928,046 transported witness blocks.

- If confirmed, the untested count drops from 155,746 to **140,062** across the other 28 aligned schemes. No `h<8`, U88, or degree-distribution case was closed. R(3,10) remains undecided.
- Total cost: **0.117 core-hours** and about **94 MiB** of additional scratch. No jobs remain.
- Evidence and replay: `ralph/lanes/G/ROUND18_REPLAY.md:32`. Next: critic review before any further search.

## Lane H: Literature scout, claim ledger, Lean (ok)
- **Lean, pending critic review:** H-033 proves that the marked \(t=17,m=15\) layer forces one exceptional pole, one untouched triple, and thirteen double rows. The pole-to-tip codegree floor follows from the balance; the pole-pair lower bound uses the separate unique-witness premise. `lean/R310/MiddleDeficit.lean:75`
- **Validation:** Smaller controls, the pinned Lean 4.35.0 build, and all 10 targeted and 353 project axiom checks passed. Used 0.06184 core-hours; no H jobs remain. `ralph/lanes/H/ROUND18_REVIEW.md:54`
- **Ledger:** Imported round-17 verdicts and recorded the available round-18 submissions as pending. No flow-verified graph; the accepted balance remains **238 near-regular distributions plus Case R**, ten conditional U88 keys, and four conditional mixed cores. `ralph/CLAIMS.md:3`

D has the strongest checked regular-case result: all 15,282 profiles in the marked \(m=16\) slice are excluded. Its new \(m=15\) census gives 162 necessary support types, not a closure. The next step is critic review and, if authorized, a count-only wing join rather than expanding the pair product. A/C’s two scoped joint exclusions also await review.

## Idea scout R (ok): review/ideas/r018_R.md
- C: treat a triple site as a fifth pole. When the five poles leave a 13-vertex core, test both frames before choosing any crossing edge.
- With a four-pole site, the incidence budget leaves no room for an opposite triple site.
- This rejects 25,987 raw 16/17 headers; exactly 56 passed both old marginal tests, all at `(66,4)`.
- The order-35 control retained all 420 marked pair cards. Six unpinned target SAT pilots hit their conflict caps.
- Audit the 56 bindings, then price the 12-core extension on one held-out bin. R(5) remains open; see `review/ideas/r018_R.md:1`.

## Idea scout N (ok): review/ideas/r018_N.md
- G: One locally checked certificate covers 60,990 previously unresolved `h=8` alignment IDs in 2.79 CPU-seconds including replay.
- It fixes one wing’s hole pattern and shares the private-grid edges across all choices on the other wing; no edges between doubles are needed.
- At `h=7`, six grids give 81 one-sided contexts; the pilots cover 51 of 1,213 two-sided contexts, not the whole overlap.
- Smaller-case enumeration recovered the exact 24/0 aligned and 129/11 one-defect class sets at orders 15/16.
- Next: audit the receipt and test one remaining `h=8` wing shape. No floor or distribution changes. `review/ideas/r018_N.md:1`

## Idea scout T (failed): review/ideas/r018_T.md
(the turn failed: exit 3; log scratch/flow/turns/r018_scout_T.log; )
r310-scout_T: session cleared; next turn starts a new context


## Referee (claude-opus-5-5-high, failed)
(the turn failed: exit 3; log scratch/flow/turns/r018_referee.log; )
r310-referee: session cleared; next turn starts a new context


## Critic (ok)
**Round 18:** No flow-verified graph and no degree-distribution closure. **238 near-regular distributions plus Case R remain open.**

- **G and scout N:** Independent replay confirmed disjoint exclusions of 15,684 and 60,990 marked `h=8` alignment IDs. **79,072 remain across 12 schemes.**
- **A/C and scout R:** Two marked 16/17 slices are excluded, with 69 new failed joins. The fifth-pole argument separately excludes 56 more headers; these were not counted as failed joins.
- **D/E/F/H:** Confirmed the 162 necessary support types, 16 matched pilot proof IDs, reduction to 16,182,483 unsigned headers, and Lean deficit theorem. None closes its parent case.
- **Audit:** No mathematical claim rejected; no rule breach found. The referee and scout T produced no report.
- **Round 19 ceilings, A–H:** `7 / 2 / 6 / 29 / 17 / 3 / 13 / 2` — 79 assigned, one spare.

**Best next test:** G’s fixed-left `middle` selector proof could cover **57,947** remaining IDs in one run. No credit until the proof and label mapping check. Full review: `ralph/critic/round_018.md:1`; directives: `ralph/critic/LATEST.md:1`.
