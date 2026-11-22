# Round 20

Began 2026-11-22T17:19:46; ended 2026-11-22T17:53:18.

## Flow checks
```json
{
 "round": 20,
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
 "critic_turn": "ok"
}
```

## Lane A: Toolchain and certified SAT (the 99 open R(7) cubes) (ok)
**G-019 expansion audit — hand + enum, pending critic review.** An independent enumerator processed all 118 frozen order-27 inputs and reproduced all 985 rooted classes at their exact source IDs. The 984 unrooted classes and their edge histogram matched the archive byte-for-byte.

Literal small-case enumeration, both missing-output controls, and a clean replay passed. Total cost: **0.01087 core-hours**. No jobs are running.

This checks only the expansion step; the prefilter and outer exclusions were not rerun. No new case was closed, and \(R(3,10)\) remains undecided. The audit is ready for critic review at `ralph/lanes/A/ROUND20_D5_AUDIT.md:1`.

## Lane B: Gluing (t9 <= 88, then a faster gluer) (ok)
**Lane B remains parked at floor 108.** Five deletion-critical 32-vertex, 108-edge classes are still missing. No case closed, no candidate found, and no jobs running.

- **Hand, pending critic review:** Every graph in this slice with minimum degree at most five admits a triangle-safe edge addition. Any saturated graph in the slice has at least eight degree-six vertices, and deleting the closed neighborhood of any of them leaves a 25-vertex graph with 65–70 edges. This does not classify the five missing graphs.
- Three smaller controls passed in 0.02 CPU-seconds, including recovery of a deliberately withheld critical graph. No target rescan or proof replay. Evidence: `ralph/lanes/B/ROUND20_SATURATION.md:1`.
- Updated `ralph/lanes/B/STATE.md:1` and the board. Reopen only with an independently supplied missing key or an exact, calibrated method priced for the full slice.

## Lane C: Theory for the 9-regular case R (ok)
- **Hand proof, pending review:** The three disjoint four-sets exhaust the 12-vertex core, so the neutral lies outside it. The fifth-row test then depends on just one bit from the left frame: whether a degree-four card deletes to that core. `ralph/lanes/C/proofs/panel20_factored_card.md:12`
- **Enumeration:** All 116 frozen right frames pass under both flag settings. Of 5,390 legal rows, 3,714 pass the stricter threshold and 5,390 pass the looser one. Literal restorations agree on every row; 840 C35 controls passed, and five replay files matched byte-for-byte. `ralph/lanes/C/ROUND20_REPLAY.md:26`
- **Stopped as directed.** No new pair evaluated or excluded, no candidate, and no active jobs. Total: 0.00203 core-hours. Case R remains open. Lane H can formalize the short exhaustion lemma if useful.

## Lane D: New SAT encodings and splits for case R (ok)
**Lane D, round 20 — hand + enum, pending critic review.** The two-site filter excludes 3 of 162 marked supports in R(3) at `K=2, t=17, m=15`: roster lines 255, 345, and 350. Each shore still has options individually, but none can be paired compatibly on those three supports.

- Ordered assignments on fixed representatives fell from **4,817,781 to 2,296,202**; marked orbits fell from **3,128,474 to 1,334,977**.
- All 250 planted calibration shores survived. An independent implementation matched all 267 before-and-after fixed counts and their deltas.
- No original kernel closed and no candidate was found. Total cost: **0.00496 core-hours**. No running or stopped jobs; 0 cores in use.
- **Next request:** authorize the stronger one-shore filter on the remaining 159 supports after calibration, capped at one worker, 30 CPU-seconds, and 64 MiB.

Evidence and replay instructions: `ralph/lanes/D/WING20.md:1`; per-host counts: `scratch/D/wing20/counts.tsv:1`.

## Lane E: Automorphisms (the open (p, f) cases) (ok)
- **Cert:** Both CakeLRAT and `lrat-check` verified freshly bound proofs at both widths for all 16 authorized IDs. Counting each ID once, conditional mixed core 1 has **32 of 147 IDs certified; 115 remain**.
- **Measured:** Width three took 11.67 CPU-s versus 15.90 CPU-s for width eight, with no fallbacks. Total round cost: 0.00892 core-h. No jobs remain active.
- **Next:** Request one worker for the exact 115-ID residual, narrow first, capped at 0.065 core-h and 224 MiB. That batch was not launched.
- No candidate was found, no full automorphism case closed, and \(R(3,10)\) remains undecided. Evidence: `ralph/lanes/E/shared74_round20.md:13` and `scratch/E/r20_shared/freeze.1.sha256:1`.

## Lane F: Constructions: search for a (3,10,40)-graph (ok)
**Lane F, round 20 — hand + enum, pending critic review.** In the one-exceptional-site construction, the checker excluded **3,172 of 3,581** previously unseen one-double footprints, including 646 in the marked subset. Combined with the pilot, **3,274 of 3,709 are excluded; 435 remain open**.

- Independent verification replayed 50,877 deductions after the smaller positive, exhaustive controls, and corrupted-pin tests passed.
- The exclusions reduced compatible unsigned footprint pairs from **15,613,661 to 1,979,210**, counting simultaneous reversal. These are not graph realizations; no candidate was produced and no unrestricted Ramsey case was closed.
- Cost: **0.00199 core-hours**. No running or stopped jobs; 0 cores in use.
- **Next request:** authorize one worker for a calibrated pilot on the 14 marked two-double footprints only, capped at 0.02 core-hours.
- Evidence: `ralph/lanes/F/ROUND20.md:1`. Exact unresolved roster: `scratch/F/r20/one-double.open:1`.

## Lane G: Near-regular degree distributions N(e) (ok)
**Lane G — hand + enum + cert, pending critic.** One fixed-left matching formula excludes the last **21,125** labelled alignments in the marked `e=170` adjacent degree-six equality `h=8` slice. Both LRAT checkers accepted the proof, and a clean replay reproduced the exact rank lists without double-counting.

This closes only the marked aligned slice, not the equality case or any degree distribution. **238 near-regular distributions plus Case R remain open.** No candidate graph; \(R(3,10)\) remains unresolved.

Total cost: **0.01041 core-hours**. No active jobs or PIDs. Next: critic replay, then the eight frozen `h=7` pilots if authorized. The `h=7` count remains **51/1,213** checked contexts.

Evidence and replay: `ralph/lanes/G/ROUND20_REPLAY.md:1`.

## Lane H: Literature scout, claim ledger, Lean (ok)
**Lean (H-035, pending critic):** Proved that the local independence cap forces a matching of size at least three, or four when the isolated cross site is present. This supplies H-034’s missing premise without assuming a matching. The build, 170 small controls, and all 359 project axiom checks passed. Evidence: `lean/R310/PrivateMatching.lean:140`.

Updated `ralph/CLAIMS.md:3` with the round-19 verdicts and round-20 submissions. C’s 12 signed exclusions are separate from the fifth-row filter, which cut nothing. The failed referee turn did leave a report: no mathematical gap was reported, and the negative control had 0/220 survivors.

**Team status:** No flow-verified graph; \(R(3,10)\) remains unresolved. G’s single certificate covering the last 21,125 marked aligned `h=8` ranks is the strongest result this round, pending critic review. It would close only that slice, not a degree distribution. E has 115 conditional terminal IDs still open.

**Next:** Ask the critic to replay H-035 and confirm G’s exact scope. Lane H used 0.022 core-hours; no jobs or PIDs remain. No new literature screen, per directive.

## Critic (ok)
**Round 20: all 12 claims confirmed within their stated scopes; none rejected or left unchecked.** No rule break found. No flow-verified graph or new degree-distribution closure; 238 near-regular MTF distributions plus Case R remain open.

- **G-056:** Both proof checkers accepted one certificate covering the last **21,125** labelled alignments. This closes the marked `e=170`, adjacent degree-six equality slice at `h=8`, not the whole equality case.
- **Deep audit:** Replayed the complete G-019 chain: **477,142** distinct valid inputs → **118** surviving cores → **984** unrooted expansions → **0** outer extensions. The result remains `pub + enum`; its consequence `n6≤2` requires MTF.
- **Other progress:** E has **32/147** conditional terminal IDs certified, **115** remaining. D excluded three marked supports. F reduced unsigned footprint pairs to **1,979,210**. C’s fifth-row test excluded no right frame and stops.
- **Round 21 ceilings:** A/B/C/D/E/F/G/H = **2/2/2/18/21/6/27/2** (80 total).
- **Highest priority:** Run G’s eight frozen `h=7` fixed-left pilots. Measure fresh coverage against the **51/1,213** checked two-sided contexts and compare proof cost with the exact fixed-alignment alternative before scaling.

Review: `ralph/critic/round_020.md:1` · Directives: `ralph/critic/LATEST.md:1` · Allocation: `ralph/ALLOC.md:1`
