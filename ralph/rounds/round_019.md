# Round 19

Began 2026-11-22T15:58:44; ended 2026-11-22T17:19:42.

## Flow checks
```json
{
 "round": 19,
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
- **Hand + enum, pending critic:** Built the lossless order-12 deletion-card index: 1,479 rooted cards across 10 core classes, with all 5,094 residual isomorphisms checked. Singleton counts of two or fewer remain unfiltered.
- **Calibration passed:** Checked 438 smaller roots, matched 105 literal reconstructions with both full and partial contacts, and rejected all 105 corrupted edge controls. Clean replay matched byte-for-byte.
- **Lane C handoff:** The preregistered bin has 116 physical headers, 12 passing both old margins, and zero prior-pilot overlaps. C owns the fifth-row test; A made no exclusion.
- Used **0.00536 core-hours**. No running jobs, candidate graph, or case closure. Evidence and replay: `ralph/lanes/A/ROUND19_DELETION_CARDS.md:1`.

## Lane B: Gluing (t9 <= 88, then a faster gluer) (ok)
**Round 19 — Lane B remains parked.** Five critical 32-vertex, 108-edge graph classes are still missing. The confirmed degree-seven floor remains 108; no new case closed and no candidate was found.

Verified no live Lane B jobs: 0 PIDs, 0 cores, and 0 solver core-hours. No scans or proof replays ran. Updated `ralph/lanes/B/STATE.md:3`; `git diff --check` passed.

Reopen only with an independently sourced new key or an exact coverage argument that recovers a deliberately withheld known key and has a cost estimate for the full slice.

## Lane C: Theory for the 9-regular case R (ok)
- **Fifth-row filter: no cut.** The held-out bin had 116 labelled headers; 12 passed both old margins, and all 578 legal fifth rows survived. The neutral lies outside the core and a degree-four restoration exists, so the filter adds no constraint on this bin.
- **Signed baseline: 12 new exclusions (`hand + enum`, pending critic).** The unchanged join and independent replay found no compatible tuple across all 12 headers, with no caps. These are signed exclusions, not fifth-row vetoes.
- **Case R remains open.** No candidate, no active jobs, and no expansion to other bins. Calibration and 15 clean replay comparisons passed; total cost was 0.03791 core-hours.
- Evidence: `ralph/lanes/C/ROUND19_REPLAY.md:1`. Next: critic review of the 12-ID exclusion; lane H can check the deletion shortcut in `ralph/lanes/C/proofs/panel19_fifth_row.md:1`.

## Lane D: New SAT encodings and splits for case R (ok)
**Lane D, round 19 — hand + enum, submitted for critic review.** All 162 supports in the marked `K=2, t=17, m=15` slice survive the pole-pair test. The count is **4,817,781 ordered wing assignments**, or **3,128,474 orbits** under pole relabellings that preserve the marks. These are incidence profiles, not graphs; no case closed.

Two independent methods agreed on all 267 fixed-point counts and all per-host weights. The small controls returned 10/5 and 60/12 ordered assignments/orbits, and all 125 planted order-22 marks passed. Evidence: `ralph/lanes/D/WING19.md:1` and `scratch/D/wing19/counts.tsv:1`.

**Resources:** 0.00270 core-hours; no running jobs, SAT calls, or candidate. **Next request:** one count-only pass to reject profiles that already force an independent ten using two sites on the same shore, capped at one worker, 30 CPU-seconds and 64 MiB.

## Lane E: Automorphisms (the open (p, f) cases) (ok)
**Lane E, round 19:** Scanned and replayed all 565,531 lifts across 68,323 projections for conditional mixed core 1 (`G?bFbo`). The exact merge leaves **147 terminal IDs**. All 24 prior pilot IDs match; 16 already have checked proofs, leaving **131 pending**. Core 1 remains open.

Scan and replay took 315 CPU-seconds versus 519 estimated. Total use was 0.08917 core-hours and 48.14 MiB of new staging. No new proofs or candidate graphs; no jobs remain active.

Evidence: `ralph/lanes/E/shared74_round19.md:1` and `scratch/E/r19_shared/freeze.1.sha256:1`. Next: request approval for the frozen 16-ID paired proof pilot before committing to the full queue.

## Lane F: Constructions: search for a (3,10,40)-graph (ok)
Lane F’s round-19 pilot excluded **102 of 128** tested one-double footprints in the one-exceptional-site construction; **26 remain open** (**hand + enum**, pending critic review). This produced no order-40 candidate and closes no unrestricted Ramsey case.

- An independent checker replayed all 2,050 deductions. All 312 valid small control configurations survived, and a clean run reproduced 58 artifacts.
- The cuts removed **568,822** unsigned joint headers after accounting for simultaneous reversal: **16,182,483 → 15,613,661**. These are construction choices, not graphs.
- **Resources:** 0.00364 core-hours used; no running or stopped jobs.

**Next:** Request one worker, capped at 0.04 core-hours, for the **3,581 untested** footprints. A full pass over all 3,709 is estimated at 11 CPU-seconds; no cut rate is extrapolated. Evidence and handoff: `ralph/lanes/F/ROUND19.md:1`.

## Lane G: Near-regular degree distributions N(e) (ok)
- **Local cert, pending critic:** One dual-checked LRAT excludes **57,947** previously open alignments for the marked `e=170`, adjacent degree-six equality case at `h=8`. If confirmed, **21,125** remain across six `matching+matching` schemes. No degree distribution closes; \(R(3,10)\) remains unresolved.
- Clean replay reproduced the exact alignment counts and the smaller-case controls (aligned **24/0**, one-defect **129/11**). Total compute was **0.00854 core-hours**. No jobs are running.
- `h=7` remains at **51/1,213** checked two-sided contexts. Eight pilots are preregistered but unrun.
- **Next:** Critic replay and ledger update via `ralph/lanes/G/ROUND19_REPLAY.md:1`, then test the remaining fixed-left `matching` shape if authorized.

## Lane H: Literature scout, claim ledger, Lean (ok)
**H-034 — Lean, pending critic review.** Proved the private-cell matching bound \(s-t\le 1-[i=0]\) and its transpose in `lean/R310/PrivateGrid.lean:42`. The proof allows multiple physical sites in one cell but never counts a double-supported site twice. The matching lower bound remains an explicit hypothesis.

The integrated Lean build, 3 targeted and 356 project axiom checks, 216 smaller controls, and the double-site mutation all passed. Lane H used 0.04003 core-hours; no jobs remain.

Updated `ralph/CLAIMS.md:3` with round 18 verdicts and available round 19 submissions. The accepted balance is unchanged: **238 near-regular MTF distributions plus Case R**, ten conditional U88 keys, four conditional mixed cores, and no flow-verified graph. G’s shared-grid certificate is the strongest next result to review: if its physical crosswalk is accepted, it reduces the marked \(h=8\) roster from **79,072 to 21,125** without closing a distribution.

Next: critic review of H-034 and G’s crosswalk, then import the remaining round 19 evidence. No new literature screen per directive.

## Referee (claude-opus-5-5-high, failed)
(the turn failed: exit 2; log scratch/flow/turns/r019_referee.log; )
r310-referee: session cleared; next turn starts a new context


## Critic (ok)
**Round 19:** No flow-verified graph and no new degree-distribution closure. The frontier remains 238 near-regular MTF distributions plus Case R.

- **G confirmed:** Two checkers verified one proof excluding **57,947** previously open alignments. Independent accounting leaves **21,125** across six schemes in the marked `h=8` slice.
- **C confirmed:** The signed baseline excluded **12** new headers. The fifth-row filter rejected **none of 578** legal rows and earns no exclusion credit.
- **Also confirmed:** A’s 1,479-card index; D’s 3,128,474 marked incidence orbits, with all 162 supports surviving; E’s 147 terminals, 131 still pending; F’s 102/128 pilot exclusions; and H’s conditional Lean matching bound.
- **Rejected:** Only the referee’s negative-control wording: all 220 controls were rejected, not zero. No substantive claim was rejected; no lane rule break was substantiated.
- **Round 20 cores, A–H:** `8 / 2 / 4 / 17 / 19 / 5 / 23 / 2` = **80**. **Priority:** test one fixed-left matching formula against G’s remaining 21,125 alignments before considering per-ID proofs.

Review: `ralph/critic/round_019.md:1`. Directives: `ralph/critic/LATEST.md:1`. Allocation: `ralph/ALLOC.md:1`.
