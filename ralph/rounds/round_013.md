# Round 13

Began 2026-11-22T07:32:09; ended 2026-11-22T08:57:46.

## Flow checks
```json
{
 "round": 13,
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
**Lane A, round 13:** Independently reproduced the cap-five 17/17 reciprocal panel result (`hand + enum`, pending critic review). Across all 200 left triple-site frames and both shared-site identifications, all 498,668 preliminary IDs matched the scout’s stage counts exactly: **17,604 passed local checks; none passed the panel**.

All ten planted hosts passed, all 31,032 single-entry mutations were rejected, and the checker retained all 100 held panel survivors. The full replay took 9.42 CPU-seconds.

No jobs are running. The e168 reroot work is retired, and Lane C owns the next pilot. The rest of the 17/17 block and \(R(3,10)\) remain open. Replay: `ralph/lanes/A/ROUND13_REPLAY.md:1`.

## Lane B: Gluing (t9 <= 88, then a faster gluer) (ok)
**Lane B, round 13: five order-32/e108 classes are still missing.** No candidate graph, no floor 109, and no change to e88/U88.

- **enum — e98 remainder:** Tested all 545 named parents at both d7 and d8. The 1,394 labelled outputs reduced to 477 known critical classes, with zero new classes. Search and audit took 22.23 CPU-seconds. The other 200 parents were separately matched to N’s archived replay.
- **enum — e122 pilot:** All 77 proposed hosts were new relative to the 419 named prior hosts. They yielded five known critical e108 classes and zero new ones. Stopped without scaling.

No lane B jobs are running. The replay and checksums are ready for critic review in `ralph/lanes/B/ROUND13_REPLAY.md:1` and `ralph/lanes/B/ROUND13.sha256:1`. Next: seek a different source or a proof that narrows what remains, rather than repeating either search.

## Lane C: Theory for the 9-regular case R (ok)
**Round 13: the cap-five 17/17 pilot passed all three stop gates.** Case R and \(R(3,10)\) remain open.

- **Hand + enum:** Verified the labelled root restoration, matched all 9,959 atlas entries, and passed 3,448 planted panels and 31,032 single-bit mutation controls. The prior triple-site slice again had zero panel survivors.
- **Enum, pilot only:** Two independent scanners agreed on all 1,554,349 fresh alignment IDs, disjoint from the prior slices and samples. Of 197,502 local fits, 327 survived the transpose check and 97 admitted simultaneous row choices. Two terminal implementations rejected all 1,869 fillings.
- **Estimate:** The transpose check cut terminal calls **604×**. The full 17/17 scan is priced at **~0.38 CPU-hours** with both scanners and C’s terminal check, before any proof work. No production scan or solver jobs are running.

The clean replay passed. Evidence and replay instructions are in `ralph/lanes/C/ROUND13_REPLAY.md:1`. Next: critic review, then a bounded complete shard to reprice before scaling.

## Lane D: New SAT encodings and splits for case R (ok)
**Lane D, round 13:** R(3) and R(3,10) remain open. No candidate graph; no jobs running (0 cores).

- **Hand + enum + local cert, submitted for review:** Every hypothetical R(3) graph contains two disjoint deficient paths that each support four induced pentagons. The sixteen added vertices are all distinct. The sufficient four-star cover shrinks **102→101**: root 179 can always be replaced by another marking, not forbidden outright.
- **Hand + enum:** Nine of 41 internal book types require more than the 29 available outside vertices. This leaves **32 types and 528 unordered type pairs**; under K=2, at most 465 pairs remain.
- **Calibration and price:** Independent checks covered all 1,734 planted C22 path pairs and 1,106 deliberately incompatible labelings. Interface checks alone eliminated **0/11 parents and 0/39 frontier states**. Requiring the same 18 exterior vertices to satisfy every contact constraint eliminated **5/5 named sparse frontiers**; that deliberately selected sample is not a general hit-rate estimate.

Four local LRAT proofs passed both checkers on regenerated CNFs. Proof and scope: `ralph/lanes/D/DOUBLE_BOUQUET.md:1`. Handoff: `ralph/lanes/D/STATE.md:1`. Next: price the shared-exterior test on denser, stratified frontiers. Critic review requested; no additional cores needed.

## Lane E: Automorphisms (the open (p, f) cases) (ok)
**Mixed core 17 excluded under the all-graph E-021 premise** — hand + enum + cert, pending critic review. All 27 branches covered 2,135,171 lifts; both receipt replays passed, and all 262 residuals had freshly regenerated original CNFs checked by CakeLRAT. Total: 0.62728 core-hours. cite

The native witness checker cut the estimated scan-and-replay cost from 3,530 to 1,508 CPU-seconds. The narrower CNF pilot checked 129/129 IDs but was not used for the exclusion. Evidence: `ralph/lanes/E/shared74_round13.md:133` and `scratch/E/r13_shared/freeze.17.sha256:1`.

No jobs or candidates remain. Seven mixed cores remain if the critic accepts core 17; next, price core 5. \(R(3,10)\) remains unresolved.

## Lane F: Constructions: search for a (3,10,40)-graph (ok)
**Lane F, round 13 — hand + enum, submitted for critic review.** If deleting four vertices leaves 18 pairs with cyclic crossing weights, only **5 of 120 profiles** remain possible. All five have crossing degree seven and use the antipodal matching. None is a verified construction.

- **Hand:** Even without cyclicity, a 36-vertex card with a fixed-point-free involution must have maximum crossing degree at least seven to admit four addbacks.
- **Validation:** Two smaller positive addbacks passed the gate; deleting one contact from each made it fail. Independent replay reproduced the five-profile cover. Evidence: `ralph/lanes/F/ROUND13.md:3` and `scratch/F/r13/freeze.stdout:1`.
- **Status:** No order-40 candidate submitted. Best observed remains 24 independent tens at both 178 and 179 edges. No live PIDs; zero cores in use. Round cost: 24.23 CPU-seconds.
- **Next:** Test pair compatibility among profile 15’s 693 possible pole neighborhoods before assigning signs. No additional cores requested.

## Lane G: Near-regular degree distributions N(e) (ok)
**Lane G, round 13:** 238 near-regular MTF distributions plus Case R remain open. No new distribution closed, and no candidate graph was submitted.

- **Cert:** Reproduced the 238-key baseline and checked 12 new one-edge conditional `t9` improvements with exact rational Farkas multipliers. No new U88 keys; the ten existing ones remain.
- **Hand + enum:** All 66 single-root and 30 paired e170 signature projections have checked integer witnesses. The paired model joins both attachment masks on the same 28 vertices, but not the edges among them. These witnesses are not graph extensions.
- **Enum:** Scout N’s filter rejected all 512 sampled e122 residues in 16.62 CPU-seconds; the old clique/core route left 20 capped. The new bundling rule rejected no additional inputs. This sample does not establish floor 123.

No Lane G jobs are running. H/critic: please independently bind the 12 threshold receipts. Replay and next steps are in `ralph/lanes/G/ROUND13_REPLAY.md:1`.

## Lane H: Literature scout, claim ledger, Lean (ok)
**\(R(3,10)\) remains undecided.** The reviewed ledger now has **238 near-regular MTF distributions plus Case R**. The degree-six floor removed 40 exact keys; the ten conditional U88 keys are unchanged, and eight conditional E cores remain. See `ralph/CLAIMS.md:3`.

- **Exact replay:** Independently bound G’s 238-key table and checked all 52 multipliers. Twelve surviving keys gain a one-edge \(t_9\) tightening; none closes. `ralph/lanes/H/ROUND13_REVIEW.md:16`
- **Lean:** Formalized the conditional e170 parity cut and C’s \(e(P)+45=e(F_A)\) identity. The pinned build and all 319 project axiom reports passed.
- **Literature:** The November 22 refresh found no superseding decision, public bulk order-39 collection, or new exact dense order-30 count. `ralph/lanes/H/LIT.md:314`

The best next tests are G’s e170 equality signatures and, with critic approval, one bounded shard of C’s 17/17 scan. C’s matched pilot left zero open among 327 panel survivors, but it was not a full scan. Lane H has no running jobs.

## Referee (gemini-4-neon-xhigh, failed)
(the turn failed: exit 3; log scratch/flow/turns/r013_referee.log; )
r310-referee: session cleared; next turn starts a new context


## Critic (ok)
**Round 13: 238 near-regular MTF distributions plus Case R remain open.** No target graph was verified by the flow.

- **Confirmed:** E’s mixed core 17 is excluded under the E-021 all-graph premise. I replayed all 2,135,171 lifts and checked all 262 proofs against freshly regenerated CNFs. Seven mixed cores remain.
- **Confirmed:** D’s R(3) cover needs only 101 root representatives and 528 internal book-type pairs. G’s twelve one-edge `t9` improvements close no distribution. B still lacks five order-32/e108 classes.
- **Rejected only as a cost total:** E’s 0.62728 core-hours covers terminal work and its Python audit; all logged workers sum to 0.67977 core-hours. No scoped mathematical claim was rejected.
- **Rules:** No violation observed. Final check: zero busy solvers, 90.9/150 GB scratch. Round-14 core ceilings A–H: **3/8/8/13/30/2/14/2 = 80**.
- **Best next step:** C’s two scanners agreed on 1,554,349 pilot IDs, with no unresolved filling. Run the complete **4,322,749-header** first shard with A independently checking coverage, then reprice before scaling. This tests the marked 17/17 subcase, not all of Case R.

Full review: `ralph/critic/round_013.md:1`. Directives: `ralph/critic/LATEST.md:1`. Allocation: `ralph/ALLOC.md:1`.
