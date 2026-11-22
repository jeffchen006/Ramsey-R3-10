# Round 21

Began 2026-11-22T17:53:18; ended 2026-11-22T19:19:14.

## Flow checks
```json
{
 "round": 21,
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
 }
}
```

## Lane A: Toolchain and certified SAT (the 99 open R(7) cubes) (ok)
**Hand + enum, pending critic:** Lane G’s eight frozen \(h=7\) pilots cover **184 distinct context keys beyond the 51-key baseline**. Those keys contain **5,592,650 labelled fixed alignments**, counted once per canonical context without stabilizer weighting.

- The permanent-based count matched literal permutation enumeration on all 184 keys and all six historical controls. Clean replay reproduced both tables byte for byte.
- Posted `scratch/A/r21/alignments.tsv:1` and `scratch/A/r21/prefix.tsv:1` for G to price whichever pilots pass. The first pilot accounts for 15 fresh keys and 118,702 alignments.
- Used **0.01308 core-hours**. No jobs remain; no candidate, new exclusion, or runtime speedup is claimed.

## Lane B: Gluing (t9 <= 88, then a faster gluer) (ok)
Lane B remains parked at floor 108. All five critical keys are still missing, and no case was closed.

- **Hand, pending critic:** A saturated 32-vertex, 108-edge residue with at most three degree-eight vertices has a degree-six vertex whose closed-neighborhood deletion leaves at most 69 edges. If there are exactly four degree-eight vertices and all degree-six deletions leave 70 edges, the induced 12-vertex degree-six subgraph is forced up to isomorphism. Evidence: `ralph/lanes/B/ROUND21_TIGHT_LAYER.md:1`.
- Five fixed controls passed in 0.02 CPU-seconds. No target scan, solver jobs, live PIDs, or candidate.
- Updated `ralph/lanes/B/STATE.md:1` and posted to the board. Reopen only on an independently supplied missing key or a calibrated, fully priced coverage proposal.

## Lane C: Theory for the 9-regular case R (ok)
- **Hand, pending review:** At a fixed core vertex, sum the minimum added degree required by each disjoint card over all admissible labelled restorations. That sum cannot exceed the degree remaining after all prescribed incidences are counted. Proof: `ralph/lanes/C/proofs/panel21_shared_core_budget.md:3`.
- **Enum, toy only:** Both cards in the strict 13-vertex fixture pass separately, with 2 and 18 restorations satisfying their exact edge totals. Every restoration of either card needs one more edge at vertex `6`, but only one slot remains. Lifting just the prohibition on `4–12` admits a complete positive.
- Checked all 16,384 local masks; the clean replay matched byte-for-byte. Total: 0.73 CPU-s. Evidence: `ralph/lanes/C/ROUND21_REPLAY.md:1`.
- Lane C is parked pending critic review. No target inputs, solver jobs, candidates, or case closures. Case R remains open.

## Lane D: New SAT encodings and splits for case R (ok)
**Hand + enum, pending critic:** In marked R(3) at `K=2,t=17,m=15`, the stronger one-shore bound excludes **9 of 159** remaining supports, leaving **150**. All nine admit assignments on each shore separately, but no compatible pair. Their roster IDs are `128, 140, 232, 299, 488, 614, 1009, 1011, 1068`.

Ordered assignments fell from **2,296,202 to 443,384**; marked orbits fell from **1,334,977 to 266,500**. An independent implementation reproduced all 264 fixed counts and their deltas. No original kernel closed, and no candidate was found.

**Resources:** 0.00386 core-hours; no running jobs or PIDs. Evidence: `ralph/lanes/D/WING21.md:1`.

**Next request:** Authorize the marginal forced-Y-edge test on the 150 survivors. All 27 edges it forced in planted controls were present. It has not been run on the target.

## Lane E: Automorphisms (the open (p, f) cases) (ok)
**Round 21 — Lane E:** Submitted the exclusion of conditional mixed core 1 `G?bFbo` for critic review (**hand + enum + cert**, under E-021/E-042/E-043 only).

- All **115/115** residual IDs passed fresh physical-lift binding and both LRAT checkers at width three. No width-eight fallback was needed.
- The audit reconciled all **565,531** lifts: 565,384 replayed obstructions, 32 previously checked IDs, and 115 newly checked IDs. **Zero remain.**
- Used about **0.024 core-hours** and **132 MiB** of staging. PID `3642341` exited normally; no jobs or candidates remain.
- The full involution case and \(R(3,10)\) remain open. Next: seek authorization for a bounded census and pricing pilot on core 6; nothing launched.

Evidence: `ralph/lanes/E/shared74_round21.md:30` and `scratch/E/r21_shared/freeze.1.sha256:1`.

## Lane F: Constructions: search for a (3,10,40)-graph (ok)
**Lane F, round 21 — hand + enum, pending critic review.** All 14 marked two-double rows remain open. The four-endpoint rule needs six additional sites to force an independent ten; every tested row leaves only four or five, regardless of signing.

The independent checker replayed 170 deductions, none of which excluded a row. The unsigned joint count remains **1,979,210**. The 398 exterior-only two-double rows were not tested.

No candidate, new score, or active job. Cost: **0.00082 core-hours**. Retire this rule on the marked roster; no additional cores requested. Exact open rows: `scratch/F/r21/pilot.open:1`. Evidence and next small control: `ralph/lanes/F/ROUND21.md:1`.

## Lane G: Near-regular degree distributions N(e) (ok)
**Round 21 — local certificates, pending critic.** All eight frozen `h=7` pilots passed both LRAT checkers in production and clean replay. After removing seven previously checked keys and one duplicate, they exclude **184 new two-sided contexts** in the marked `e=170` adjacent degree-six equality slice. That brings coverage to **235/1,213**, with **978 open**.

- Calibration reproduced the exact smaller class sets: 129 at order 15 and 11 at order 16. The binder checked 269 physical placements and rejected all 24 deliberately invalid clauses.
- Total cost: **71.94 CPU-seconds** and **138.4 MB** of LRAT proofs. Lane A counted **5,592,650** fixed alignments in the newly covered contexts, but there is no matched runtime comparison. No new batch requested.
- **No jobs running, no candidate, and no degree distribution closed.** Next: critic verification of the 184-key count, then a matched cost comparison before scaling.

Evidence and replay: `ralph/lanes/G/ROUND21_REPLAY.md:1`.

## Lane H: Literature scout, claim ledger, Lean (ok)
**R(3,10) remains open.** The latest published bounds I could verify are 40–41. The literature recheck found no public bulk order-39 catalogue or new exact order-30 counts for 88–99 edges; the search was limited. See `ralph/lanes/H/LIT.md:1`.

- **Lean, pending critic:** H-036 derives the local independence cap of five by adjoining four unused root neighbours, then proves the private-cell row bound without assuming a matching. Tight and extra-contact controls passed, as did the Lean build and 3 targeted / 362 project axiom checks. See `lean/R310/PrivatePadding.lean:23`.
- **Ledger:** Imported all 12 round-20 verdicts, including the complete G-019 replay. Only the marked aligned `h=8` slice closed; 238 near-regular MTF distributions plus Case R remain. See `ralph/CLAIMS.md:3`.
- **Best next evidence:** E’s 115 new certificates could close conditional mixed core 1 only. G’s eight receipts could add 184 distinct `h=7` contexts, leaving 978 open, but a matched timing comparison is still needed before scaling.

Lane H used 0.04021 core-hours. No jobs or candidate remain. Next: critic review of H-036 and the pending E/G claims.

## Idea scout R (ok): review/ideas/r021_R.md
- D: omit the entire long shore and leave the short shore unpinned in marked R(3), `K=2,t=17,m=15`.
- On support 404, one independently rebuilt, twice-checked proof covers all 16,060 surviving marked assignments.
- Discovery through both proof checks cost 44.6 CPU-s; 40 matched direct proofs imply an estimated 83× saving on this host.
- All 250 smaller planted shores passed. The unchanged witness sets admit a local model on 896, so new witnesses are needed there.
- Report: `review/ideas/r021_R.md:1`. Run `bash scratch/ideas/r021_R/replay.sh` before counting this support; R(3) remains open.

## Idea scout N (ok): review/ideas/r021_N.md
- G: Six dual-checked proofs cover all 1,213 marked `h=7` contexts at `e=170`, including 978 beyond G's round-21 receipts, pending critic review.
- Those 978 contexts represent 30,676,328 labelled alignments. The six successful solves took 72.45 CPU-s; clause verification and full proof replay took 44.12 CPU-s.
- The smaller one-defect controls recovered exactly 129 and 11 classes. No `h≤6` slice or degree distribution is excluded by this result.
- B: Lifting all 1,842 critical 31/e96 parents returned 23 known 32/e108 graphs and no missing key. No vertex deletion of a missing key can be thinned below 97 edges while preserving the Ramsey conditions.
- Report and replay instructions: `review/ideas/r021_N.md:1`. The five missing keys, the residue floors and the Ramsey verdict are unchanged.

## Idea scout T (failed): review/ideas/r021_T.md
(the turn failed: exit 3; log scratch/flow/turns/r021_scout_T.log; )
r310-scout_T: session cleared; next turn starts a new context


## Critic (ok)
**Round 21: all 12 lane claims confirmed within scope; none rejected.** No degree distribution closed and no graph was flow-verified. \(R(3,10)\) remains open.

- **G/N:** Six proofs passed both checkers and cover all **1,213** contexts in the marked `e=170, h=7` slice. The 978 contexts left after G’s pilots are closed; do not schedule them.
- **E:** All **115** remaining proofs replayed. Conditional mixed core 1 is closed under its stated assumptions; cores **6, 9, 18** remain.
- **D/R:** Nine support exclusions replayed. One additional proof excludes all **16,060** assignments on support 404, leaving **149** marked supports.
- **B/N:** The complete 1,842-parent e96 search returned 23 known keys and none of the five missing keys. The floor stays at 108.
- **Rules:** No substantiated breach. Scratch measured **97.0/150 GB**. Round-22 cores A–H: **2/2/2/24/26/2/20/2 = 80**; D and E alone can meet the 50-core utilization target.
- **Best next direction:** Run D’s whole-support proof on the remaining 149 hosts, splitting only those the projection cannot close.

Full review: `ralph/critic/round_021.md:1`. Dispatch directives: `ralph/critic/LATEST.md:1`.
