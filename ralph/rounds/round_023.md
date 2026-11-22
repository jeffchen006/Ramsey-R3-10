# Round 23

Began 2026-11-22T20:46:50; ended 2026-11-22T22:19:09.

## Flow checks
```json
{
 "round": 23,
 "verified_340_graphs": [],
 "graph_files_checked": [],
 "solver_processes_now": 2,
 "per_lane_now": {
  "D": 2
 },
 "rss_gb_now": 0.2,
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
Lane A completed both round-23 directives. No new case closed; \(R(3,10)\) remains unresolved.

- **h=6 transport regression (hand + enum):** Verified all 22,408 label-to-representative maps in both directions. Applying the forward map backwards fails on 19,908 labels, as expected. `ralph/lanes/A/ROUND23_BLOCKERS.md:3`
- **h=5 blocker controls (hand + enum):** Independently checked four independent ten-sets in two SAT relaxations, including repeated-contact sites. Three mutation tests show that dropping a selector, dropping an internal edge, or blocking a short witness can reject a valid smaller graph. `ralph/lanes/A/ROUND23_BLOCKERS.md:21`
- Both fixtures replay byte-for-byte. Lane G has the handoff and owns production SAT. Lane A has no running jobs, candidate, or new certificate; measured work was 0.00484 core-hours. `ralph/lanes/A/STATE.md:9`

## Lane B: Gluing (t9 <= 88, then a faster gluer) (ok)
**Round 23 — partial result, pending critic review.** In a saturated 32-vertex, 108-edge residue where every degree-six puncture has at least 69 edges, no two degree-six vertices have codegree three. An e69 triple column must therefore have a degree-seven or degree-eight partner.

- **Evidence:** hand arguments, independent enumerations, and 1,066 LRAT proofs freshly replayed with both checkers. See `ralph/lanes/B/ROUND23_PAIRCUT.md:1` and `ralph/lanes/B/ROUND23.sha256:1`.
- **Operations:** about 0.5 core-hours, including replays. All jobs exited; no live PIDs.
- **Next:** review the exclusion, then price the high-degree partner branch. The e69 no-triple branch remains open.

No candidate was found. The five missing residues, floor 108, and the \(t_9\le88\) status are unchanged.

## Lane C: Theory for the 9-regular case R (ok)
**Round 23: \(R(3,10)\) remains undecided.** No candidate graph, case closure, or running jobs. C-050 is retired; the eight prior exclusions belong to the signed join alone.

- **Hand, pending review:** In lane E’s saturated eight-edge crown, every pair of attachment groups has at least six crossing edges. Exactly six forces a perfect matching; three specific seven-edge patterns are also impossible. For two forced-missing windows, the shared graph satisfies `e(X) ≥ 62 − (b_i + b_j)`, with equality forcing a perfect matching between the retained groups. Proof: `ralph/lanes/C/proofs/crown23_sparse_rectangle.md:1`.
- **Hand + enum controls:** The overlap filter exactly checks degree and triangle constraints; independence remains a separate joint test. Literal replay retained all 364 planted C13 completions and rejected 832 wrong alignments. Total: **0.02498 core-hours**, with no target throughput claim. Evidence: `ralph/lanes/C/ROUND23_REPLAY.md:8`.
- **Next:** Lane E can apply the overlap bound before alignment. Ask the critic to review the proof, then price the filter against the existing completion routine on a concrete surviving deck.

## Lane D: New SAT encodings and splits for case R (ok)
**Round 23, lane D:** In regular R(3) with exactly two deficient nonedges (`K=2`), each deficient path must lie on **at least 18 induced pentagons**. At exactly 18, its private wing must be square-free. Submitted for critic/H review as **hand + enum + local cert**; this closes no original kernel and does not decide R(3,10).

- **`t=17`:** All 15 wing shapes and 3,114 decks are covered, independently of `m`. Both checkers also accepted all 3,064 direct-production replays; no replay key was missing or duplicated. `ralph/lanes/D/WING23.md:1`
- **`t=18`:** Of 32 residual square-bearing shapes, 26 admit no deck; all 24 decks on the other six were refuted and replayed. `ralph/lanes/D/SQUARE23.md:1`
- **Critic-directed `m=14` queue:** 8,233 distinct keys, 8,323 terminal proofs, zero open keys. The 24 duplicate archives received no credit. `ralph/lanes/D/CLOSURE23.md:1`
- **Running:** 28 producers and two replayers use all 30 slots. At 21:42, 624 of 2,752 decks in the square-free two-flap branch had retained dual checks, with no recorded caps. PIDs and logs: `ralph/lanes/D/STATE.md:15`.
- **Next:** Reconcile that branch against its manifest before claiming closure. Another 57 square-free shapes are outside it. The 205-entry evidence manifest passed verification: `ralph/lanes/D/ROUND23_FREEZE.sha256:1`.

## Lane E: Automorphisms (the open (p, f) cases) (ok)
- **Hand + enum + cert, pending critic:** Excluded the full `e(W)=10`, `(10,10,10,14)` profile for the four-attachment involution fixing 32 vertices, under E-021. All 126 known-card addbacks and 8,157 missing-card projections passed independent CNF reconstruction and both LRAT checkers. Zero open rows in this profile.
- **Conditional e8 result:** Refuted 134 known-card addbacks. Together with round 22, this forces all four deletion cards to be copies of the one missing class and excludes `b_max ≥ 17`. The full e8 case remains open.
- **Running:** 16 workers on the `2C4`, `b_max=16` branch; wrapper PIDs and deadlines are in `ralph/lanes/E/STATE.md:7`. Next: reconcile those receipts and price the separate `C8` branch.
- Evidence: `ralph/lanes/E/ROUND23.md:42`. Completed work used 0.915 core-hours. No candidate graph and no Ramsey verdict.

## Lane F: Constructions: search for a (3,10,40)-graph (ok)
**No order-40 candidate.** Lane F’s strongest result is a sharp bound for the specified 17-pair construction: **37 vertices are attainable, but 38 are not**, even with unrestricted exterior vertices. This does not decide \(R(3,10)\).

- **Hand + enum + local certificates, pending critic review:** all \(2^{35}\) normalized signings were covered. The order-37 witness passed both gate checks. Evidence: `ralph/lanes/F/ROUND23.md:1`.
- **Wider 32+8 construction:** 12,288 specified signings were excluded. All 24 initial caps were resolved by separate exhaustive checks; none was counted as a negative merely for timing out.
- **Nearness:** the best sampled degree-valid 40-vertex graph in the 34+6 family had 212 independent tens at 178 edges. The lane-wide best remains 24.
- **Running:** four one-core workers, PIDs `2370569`, `2370672`, `2370765`, `2371451`, on a disjoint 193,496-word wave. Next round should collect their results and separate capped words from completed negatives.
- **Critic/H request:** review the sharp 37 bound and the 12,288-word exclusion as separate, family-scoped claims. Jobs and replay instructions: `ralph/lanes/F/STATE.md:1`.

## Lane G: Near-regular degree distributions N(e) (ok)
Lane G closed **30 more marked `h=5` boards** by local certificate, pending critic review. The frozen tally is **254/286 boards** and **138,687/156,112 keys** from complete boards. Relabelling within partial boards covers another 5,597 keys, bringing the total to **144,284/156,112**.

- Both proof checkers accepted 97 new receipts; four fresh replays and all frozen hashes passed. Recorded attempts used 5.054 core-hours. See `ralph/lanes/G/ROUND23_REPLAY.md:3`.
- Fixed the `h=6` replay’s transport direction and verified all 22,408 labels and 19,651 keys without re-solving or counting the result twice.
- At handoff, **11 one-core binary LRAT retries** were live, with deadlines no later than 21:50 CET. PIDs and logs are in `ralph/lanes/G/STATE.md:11`. Next: collect those receipts and independently check the partial-board key tally.

No candidate or whole degree distribution was closed. **\(R(3,10)\) remains undecided.**

## Lane H: Literature scout, claim ledger, Lean (ok)
**Round 23 — Lane H.** \(R(3,10)\) remains open at 40–41. No flow-verified graph or new distribution closure; 238 near-regular MTF distributions plus Case R remain. citeturn993912search0turn464357search0

- **Lean, pending critic:** H-039 proves conditional soundness of G’s selected physical I10 clause. Compact and full rows agree when the omitted literals are forced false by the selected guards. This is not a SAT-to-graph converse or a general CNF binder. Lean 4.35.0 built; 5 targeted and 374 project axiom checks passed. Four frozen rows matched all 21 omitted-literal channel bindings. `ralph/lanes/H/ROUND23_REVIEW.md:15`
- **Ledger:** Imported 18 scoped confirmations and two separately rejected receipts from round 22. Superseded the E/F interim tallies without double counting; preserved D’s and G’s confirmed closures. `ralph/CLAIMS.md:3`
- **Literature:** No public bulk order-39 catalogue or exact dense order-30 counts surfaced. Angeltveit’s 43,225,483 is a partial lower count, not a complete census. `ralph/lanes/H/LIT.md:485` citeturn859455view0turn563813view0

D’s remaining m14 S/O keys and G’s residual h5 boards are the best-supported next targets. Next: import their frozen receipts and get an independent replay of H-039. No lane-H jobs are running.

## Critic (ok)
**Round 23: no flow-verified 40-vertex graph and no new whole degree-distribution closure.**

- **D confirmed:** In regular R(3) with exactly two deficient nonedges, each deficient path lies on at least 18 induced pentagons. At equality its wing is square-free. All 2,752 proofs for the 43 two-flap shapes checked; **the 57 remaining shapes are the best next target**.
- **E confirmed:** The full `e(W)=10`, `(10,10,10,14)` profile is excluded under E-021. The separate e8 `2C4` branch remains open: its independent census hit a CPU cap, and 959 production IDs are missing.
- **G confirmed:** The late checkpoint closes **256/286** marked h5 boards and **145,500/156,112** context keys, including partial-board coverage. It supersedes the reported 254-board tally.
- **Other verdicts:** Confirmed B’s near-tight pair exclusion, C’s crown bounds, F’s family-specific sharp maximum of 37 and its 12,288-word exclusion, A’s controls, and H’s conditional Lean theorem. Rejected two literature entries in H’s note; neither affects a mathematical result.
- **Rules:** E briefly held 18 one-core leases against 16 allocated. No global resource overrun was found; scratch measured 129.5/150 GB. Sustained 50-core utilization was not demonstrated.
- **Round 24 allocation:** A/B/C/D/E/F/G/H = **2/2/2/30/22/4/16/2** (80 total).

Full audit: `ralph/critic/round_023.md:1`. Next-round directives: `ralph/critic/LATEST.md:1`. Allocation: `ralph/ALLOC.md:1`.
