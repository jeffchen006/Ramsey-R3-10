# Round 22

Began 2026-11-22T19:19:14; ended 2026-11-22T20:46:50.

## Flow checks
```json
{
 "round": 22,
 "verified_340_graphs": [],
 "graph_files_checked": [],
 "solver_processes_now": 2,
 "per_lane_now": {
  "D": 2
 },
 "rss_gb_now": 0.1,
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
Lane A delivered the two-defect calibration and the `h=6` board inventory to G. No target case was closed this round by A; \(R(3,10)\) remains undecided.

- **Hand + enum, pending critic:** The weak `h=6` cover has **49 board orbits** from 22,408 labelled boards and 19,651 hole-context keys. G independently matched every key. These counts do not establish feasibility.
- **Enum calibration:** The strict order-16 and order-17 controls are empty. The relaxed order-16 control has **127,086 labelled placements in 8,119 graph classes**. G matched four board projections and confirmed that the alias and short-padding mutations reject valid graphs.
- **Replay:** All 27 hashes and 15 byte comparisons passed. Total timed cost: **0.0746 core-hours**. No lane A jobs remain; G owns the target solves.

Evidence and replay instructions: `ralph/lanes/A/ROUND22_TWO_DEFECT.md:1`.

## Lane B: Gluing (t9 <= 88, then a faster gluer) (ok)
- **Hand, pending critic:** Every saturated triangle-free 32-vertex graph with 108 edges and independence number at most 8 has a degree-six vertex whose closed-neighborhood deletion leaves **65–69 edges**. The saturated search no longer needs the e70 source. Smaller controls and a clean replay passed. `ralph/lanes/B/ROUND22_TIGHT_FIBRES.md:3`
- **Confirmed source exclusion:** The complete e96 source produced 23 critical lifts, all known. For each of the five missing keys, every spanning `(3,9)` subgraph after deleting one vertex has at least 97 edges. `ralph/critic/round_021.md:30`
- **Open:** All five keys remain missing; the degree-seven residue floor stays 108. No candidate and no live PIDs (0/2 cores): there is no complete, costed e69 search. Next: critic review of the proof and an independently supplied missing key or a costed e69 coverage route.

## Lane C: Theory for the 9-regular case R (ok)
**Round 22, lane C — Case R remains open.** No candidate graph or whole-case closure.

- **Hand + enum, pending:** Calibrated the fixed-label card checker against the C13 plant and a literal small catalogue. On two fresh cap-five frame pairs, 34 of 96 legal rows had an empty separate-card domain. All coordinate minima were zero on the other 62, so C-050 cut no additional row and blocked neither frame.
- **Enum, pending:** The unchanged signed join excluded **eight fresh marked frame pairs**. An independent audit agreed on all eight. These exclusions belong to the signed join, not C-050.
- **No jobs running.** Parked the degree-budget check: it took 23.76 CPU-s on the two-pair pilot, while the original join took 0.01 CPU-s and made zero terminal calls. Total round cost: 0.05848 core-hours.
- **Next:** Critic and lane H should review the eight exclusions separately. Exact IDs and replay instructions are in `ralph/lanes/C/ROUND22_REPLAY.md:68`; the handoff is in `ralph/lanes/C/STATE.md:1`.

## Lane D: New SAT encodings and splits for case R (ok)
**Completed**
- Added the fresh unpinned m15 projection pipeline and certificate replay tools in `ralph/lanes/D/`.
- Locally closed all **149/149** remaining m15 hosts with LRATs accepted by both checkers: `scratch/D/closure22/`.
- Combined with prior D-044/D-050 evidence, this excludes the marked `K=2,t=17,m=15` layer; it does **not** close all of Case R.
- Independently audited the m14 support census: 25,142 representatives, with D/S/O sectors totaling 539/3,847/3,847 positive supports.
- Covered all 539 same-pole D-sector keys, including 55 prefix proofs replacing five raw proof-size caps.
- Added the handoff, replay scripts, freezes, and critic-facing documentation in `ralph/lanes/D/CLOSURE22.md`, `ROUND22_FREEZE.sha256`, and `ROUND22_M14.sha256`.

**Running**
- 24 bounded m14 workers remain active under the listed PIDs in `ralph/lanes/D/STATE.md`.
- Latest snapshot reported 2,686/8,233 m14 keys with receipts; capped leaves remain open and are not counted as UNSAT.
- No candidate graph was found; `R(3,10)` remains undecided.

## Lane E: Automorphisms (the open (p, f) cases) (ok)
**Round 22 — pending critic review**
- **Hand + enum + cert:** Closed mixed cores 6, 9, and 18: 5,779,378 lifts covered, all 1,162 terminal LRATs regenerated and checked by both checkers, zero residuals. Together with the prior results, this closes only the \(t=4,\ \delta(W)\ge2,\ e(W)=11\) stratum of the \((2,32)\) involution case.
- **Hand + enum:** Excluded \(e(W)=8,\ P=2\). The complete 73-edge catalogue yielded 67 eligible core placements but no valid attachment partition.
- **Necessary condition:** For \(e(W)=8,\ P=0\), at least two deletion windows must be copies of the sole missing 74-edge class. This branch remains open.
- **Handoff:** Peak 26 slots, 2.1634 measured core-hours, no live jobs. All priced queues finished. Next: price a join on the two missing windows. Evidence: `ralph/lanes/E/ROUND22.md:3` and `scratch/E/r22_shared/freeze.sha256:1`.
- No candidate graph; \(R(3,10)\) remains undecided.

## Lane F: Constructions: search for a (3,10,40)-graph (ok)
**Lane F ruled out the one-exceptional-site ID8 construction**, pending critic review (`hand + local cert + enum`). No order-40 candidate was produced; **R(3,10) remains undecided**.

All **668 marked rows** are accounted for: 412 admit no valid 36-vertex graph, and 251 admit no 37th vertex. The final five reach order 37, but across all 111 possible signings, none can accommodate two nonadjacent exterior vertices. Any four exterior vertices in a triangle-free graph must contain such a pair.

The bare-card and one-vertex results passed a clean replay; all 2,147 pair exclusions have independently checked physical witnesses. No general involution case or degree distribution was closed.

**Resources:** 0.4443 metered core-hours; no jobs remain. **Next:** critic replay of `ralph/lanes/F/ROUND22.md:1` and `ralph/lanes/F/ROUND22_FREEZE.sha256:1` before ledgering the exclusion.

## Lane G: Near-regular degree distributions N(e) (ok)
- **`h=6` closed pending critic review** (hand + enum + local cert): all 49 boards and 19,651 weak hole-context keys in the marked `e=170` adjacent degree-six slice. Both verifiers accepted 51 LRATs, including four leaves from two exhaustive splits. Cost: ~0.78 core-hours. Evidence: `ralph/lanes/G/ROUND22_REPLAY.md:1`.
- **`h=5` remains open.** At 19:53, both verifiers had accepted 211/286 boards covering 117,224/156,112 weak keys. Fourteen detached single-core workers were still active; PIDs, logs, and deadlines are in `ralph/lanes/G/STATE.md:10`.
- All 37 decoded SAT relaxation models contained an independent 10-set. The larger-blocker pilot timed out; don’t scale it without a better price. Next: collect the queue and price compact witness clauses or exhaustive selector splits. Details: `ralph/lanes/G/ROUND22_H5_HANDOFF.md:1`.

No candidate graph or whole degree distribution was closed. \(R(3,10)\) remains undecided.

## Lane H: Literature scout, claim ledger, Lean (ok)
**\(R(3,10)\) remains open.** The published bounds are still 40–41, and the flow has verified no 40-vertex witness. The literature check found no public bulk order-39 census or exact order-30 counts for 88–99 edges. Sources: `ralph/lanes/H/LIT.md:449`.

- **Lean, pending critic:** H-037 proves that equal support masks do not merge physical slots and that selected mates agree on edge descriptions. H-038 proves C’s disjoint added-degree bound. Lean/Mathlib 4.35.0 builds; seven targeted and 369 project axiom checks passed. Evidence: `ralph/lanes/H/ROUND22_REVIEW.md:3`.
- **Ledger:** Imported all twelve round-21 lane verdicts and six accepted scout entries. Staged round-22 claims without changing the confirmed case totals. See `ralph/CLAIMS.md:1`.

The strongest new regular-case evidence is D’s 149/149 marked-host replays, pending critic review; they do not close an original kernel. E’s mixed-core receipts and G’s two-defect board queue are next to reconcile. Lane H used 0.07016 core-hours and has no live jobs.

## Referee (gemini-4-neon-high, failed)
(the turn failed: exit 3; log scratch/flow/turns/r022_referee.log; )
agent r310-referee: backend=agy model=gemini-4-neon-high cwd=<root>
r310-referee: session cleared; next turn starts a new context


## Critic (ok)
**Round 22: \(R(3,10)\) remains undecided.** No flow-verified graph, whole original kernel, involution case, or degree distribution closed.

- **Confirmed:** D closed the marked `m=15` layer and the `m=14` same-pole sector. All 149 fresh `m=15` proofs passed independent dual replay.
- **Confirmed:** G closed marked `h=6`; all 51 proofs passed dual replay. At `h=5`, 224/286 boards are checked and **62 remain open**.
- **Confirmed:** E closed the scoped `(2,32)` 11-edge stratum and 8-edge `P=2` branch. F excluded its one-exceptional-site ID8 construction.
- **Rejected:** D’s 2,686-key handoff tally and G’s unchanged transport replay. Correcting the transport direction recovered all 22,408 labels and 19,651 keys, preserving the `h=6` result.
- **Rules:** No hard-rule breach substantiated. Scratch measured 113.6/150 GB; the ≥50-core utilization target was not demonstrated.
- **Round 23 cores, A–H:** **2/2/2/30/16/4/22/2**. Best next target: D’s remaining `m=14` two-pole sectors, with a frozen per-key proof index.

Full review: `ralph/critic/round_022.md:1`. Directives: `ralph/critic/LATEST.md:1`. Allocation: `ralph/ALLOC.md:1`.
