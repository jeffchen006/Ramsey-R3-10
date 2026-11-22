# Round 15

Began 2026-11-22T10:24:17; ended 2026-11-22T11:50:32.

## Flow checks
```json
{
 "round": 15,
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
 "referee_turn": "ok"
}
```

## Lane A: Toolchain and certified SAT (the 99 open R(7) cubes) (ok)
**Lane A, round 15 — hand + enum, pending critic review.** Independently verified all 30 new HH receipts against the shore-exchange census and preserved the 12 original ordered receipts.

- All **157,472,001** ordered headers are accounted for: **92,341,930** checked directly, **65,130,071** covered by shore exchange, and **zero unresolved**.
- Both terminals agreed on all **74,632** rejected fillings from the new shards. Smaller controls exercised both neutral-map bits on fixed headers, and the audit rejected corrupted receipts.
- This excludes only the marked cap-five \(K_{4,4}\) with two neutral sites, pending review. Case R and \(R(3,10)\) remain open.
- No Lane A jobs remain. The critic and Lane H have the [handoff] in `ralph/lanes/A/ROUND15_EXCHANGE.md:113` and the final audit in `scratch/A/r15/receipts.final.log:1`.

## Lane B: Gluing (t9 <= 88, then a faster gluer) (ok)
**Lane B — Round 15 (cert, pending critic review).** Excluded all **2,102,271 supplied deletion-reducible 32-vertex, 108-edge residues** at degree-seven roots of maximal triangle-free targets. The ordered audit assigned every rank exactly one disposition: 2,016,206 checked demand cliques and 86,065 dual-checked LRAT proofs, with zero gaps.

- Used **1.99 core-hours** and **240 MiB**. No jobs remain.
- The 1,875 supplied critical residues were outside this run, and five critical classes are still missing. **No floor 109 or case-count change; \(R(3,10)\) remains unresolved.**
- Next: critic replay of the frozen evidence in `ralph/lanes/B/ROUND15_REPLAY.md:61` and `ralph/lanes/B/ROUND15.sha256:1`.

## Lane C: Theory for the 9-regular case R (ok)
**Marked cap-five 17/17 excluded (`hand + enum`, pending critic review).** In a hypothetical cap-five target, every \(K_{4,4}\) must dominate all but at most one vertex. Case R, R(5), and \(R(3,10)\) remain open. No candidate found.

- Both audits account for all 157,472,001 ordered alignments: 92,341,930 scanned directly, 65,130,071 covered by shore exchange, and zero unresolved.
- Both terminals agree on all 74,632 new joint fillings; none survives. The 30 new shards used 270.204 CPU-seconds. No jobs remain.
- Replay and frozen evidence: `ralph/lanes/C/ROUND15_REPLAY.md:76`. Next: critic audit and lane H ledger review before pricing the one-neutral 16/17 case.

## Lane D: New SAT encodings and splits for case R (ok)
**Lane D, round 15:** Submitted for critic review: if an R(3) graph has exactly two deficient pairs, **each deficient path has at least 17 distinct induced pentagon closures**. The pentagons need not be disjoint.

- **Evidence — hand + enum + cert (local):** Excluded all three possible 16-edge wings: C10+C6 (71 cases), C8+C8 (123), and C16 (93). Fresh replay regenerated all 287 CNFs and verified every LRAT with both `cake_lpr` and `lrat-check`.
- **Scope:** The two-deficiency case above 16 remains open. No candidate was found; R(3,10) is undecided.
- **Handoff:** Proof and replay instructions are in `ralph/lanes/D/EQUALITY16.md:1`. No jobs remain: 0 PIDs, 0 cores.
- **Next:** Review the 16-edge exclusion, then classify the 17-edge wings before launching further SAT searches.

## Lane E: Automorphisms (the open (p, f) cases) (ok)
- **Conditional exclusion, pending critic review:** For the mixed `(2,32)` subcase under E-021, Lane E excluded core 8 (`G?qbf_`) only. The independent ordered replay covered 132,986 projections and 832,295 lifts. All 85 remaining lifts passed fresh CakeLRAT checks on independently reconstructed width-three CNFs; none needed width-eight fallback. **Label: hand + enum + cert.**
- **Cost:** 0.17446 core-hours including calibration and pricing. On 16 sampled lifts, width three used 18.62 CPU-seconds including the fresh recheck, versus 20.31 for width eight. No jobs remain.
- **Next:** Ask the critic to replay the frozen evidence and choose the next core to price. If accepted, five mixed cores remain: 1, 6, 9, 15, and 18. No candidate graph or Ramsey verdict.
- **Evidence:** `ralph/lanes/E/shared74_round15.md:93`, `scratch/E/r15_shared/freeze.8.sha256:1`.

## Lane F: Constructions: search for a (3,10,40)-graph (ok)
**Lane F, round 15 — ID21 excluded (hand + cert, pending critic review).** Every triangle-free 36-vertex card with cyclic crossing distances `{5,6,8,9}` contains an independent ten on ten distinct pairs. The exclusion holds whether the named vertical edge is absent or present; it does not assume rotation-invariant crossing signs.

- **Evidence:** 297 ten-site supports suffice. Both `lrat-check` and `cake_lpr` accepted the LRAT certificate, and regeneration from the archived masks produced a byte-identical proof. See `ralph/lanes/F/ROUND15.md:1`.
- **Scope:** Only ID8 remains open in this cyclic-card family. No order-40 candidate was produced; the observed best remains 24 independent tens at both 178 and 179 edges.
- **Resources:** 9.20 aggregate CPU-seconds; no live or stopped jobs, zero cores in use.
- **Next:** Pending critic review, measure the local parity dimension for one missing vertical at ID8 before deciding whether to search it. No extra cores requested.

## Lane G: Near-regular degree distributions N(e) (ok)
**Lane G, round 15:** No templates or distributions closed. The ledger remains at **238 near-regular distributions plus case R**, with ten conditional U88 keys unchanged.

- **Hand + enum:** The occupancy-only rows passed the C13, C35, and saturated Exoo39 controls. They rejected the same three fixed population tuples as round 14; the fourth passed.
- **Enum + estimate:** All four unpinned templates still had exact integer points in the strengthened relaxation. Adding the rows took 0.25 CPU-s, but packing and solving rose from 11.93 to 18.80 CPU-s. The pilot stops here.
- **Handoff:** No jobs running. Proof, timings, and replay commands are in `ralph/lanes/G/ROUND15_REPLAY.md:1`. No ledger change requested.

## Lane H: Literature scout, claim ledger, Lean (ok)
**\(R(3,10)\) remains open.** The November 22, 2026 literature check found no result superseding the published bounds of 40–41. See `ralph/lanes/H/LIT.md:370`.

- **Lean (H-030):** With \(R(3,6)\le18\) as an explicit premise, a marked \(K_{4,4}\) has exactly two neutral sites iff both antineighborhoods have order 17. The pinned build, 5 targeted and 332 project axiom checks, and smaller controls passed. The proof does not certify the scan. `lean/R310/BicliqueNeutral.lean:76`
- **Ledger:** Imported all round-14 verdicts. The accepted balance remains **238 near-regular distributions plus Case R**, ten conditional U88 keys, and six conditional mixed involution cores. E’s core 8 exclusion is pending. `ralph/CLAIMS.md:3`
- **Best bounded result:** A/C accounted for all **157,472,001** marked alignments, directly or by shore exchange, with none unresolved. If accepted, this excludes only the cap-five \(K_{4,4}\) case with two neutral sites—not all of \(R(5)\). `ralph/CLAIMS.md:292`

**H jobs:** None; 0 cores active. Next: import the critic’s verdicts and consider formalizing the shore-exchange implication if requested.

## Idea scout R (ok): review/ideas/r015_R.md
- D: with exactly two deficiencies, a path on 17 pentagons needs only six support multigraphs when its 14 untouched vertices span 16 edges.
- Codegree and symmetry reduce 82,628,562 ordered shore pairs to 15,282 profiles: over 5,400× fewer, not a runtime estimate.
- All 125 smaller planted paths survived; 48/48 held-out profiles returned UNSAT, and two separate pilot tails have checked LRATs.
- An independent sparse-residue audit gives at least 10 untouched edges at every deficient path, or 11 if its middle has at most one deficient partner.
- Price a proof-producing shard before scaling. The full 17-pentagon layer and R(3) remain open. See `review/ideas/r015_R.md:1`.

## Idea scout N (ok): review/ideas/r015_N.md
- G: when both sets of eight double sites coincide, the twenty private sites have a fixed grid; 169,635 alignments remain before proof reuse.
- Sixty-two checked local proofs cover 10,386 of those alignments; 159,249 are untested by this cover.
- The smaller grid reconstruction recovers exactly 24 known order-15 classes and none on the corresponding order-16 slice.
- Four-anchor cuts reject 32/34 named populations, but all four tested templates admit replacements.
- Next: price the 1,472 uncovered alignments of one scheme. No floor or distribution changes; see `review/ideas/r015_N.md:1`.

## Idea scout T (failed): review/ideas/r015_T.md
(the turn failed: exit 3; log scratch/flow/turns/r015_scout_T.log; )
r310-scout_T: session cleared; next turn starts a new context


## Referee (claude-opus-5-5-high, ok)
Now I'll write an independent validator + extension encoder for the N-003 floor.



## Critic (ok)
**Round 15: no flow-verified target and no whole distribution removed.** The ledger remains at 238 near-regular MTF distributions plus Case R.

- **A/C confirmed:** The marked cap-five regular \(K_{4,4}\) cannot have two neutral sites. All 157,472,001 headers are accounted for: 92,341,930 checked directly and 65,130,071 by shore exchange.
- **B confirmed:** All 2,102,271 supplied deletion-reducible residues are excluded at MTF degree-seven roots. Five critical classes remain missing; the floor stays at 108.
- **D confirmed:** With exactly two deficient pairs in R(3), **each** deficient path has at least 17 induced pentagon closures. All 287 local proofs passed both checkers.
- **E/F confirmed:** Five conditional mixed cores remain after excluding core 8. ID21 is excluded regardless of its verticals; only ID8 remains in that cyclic-card family.
- **G/H confirmed at stated scope:** G cut fixed tuples, not templates. H’s Lean theorem establishes the neutral-site equivalence, not the scan. No submitted exclusion was rejected, no referee gap remained, and no rule breach was identified.

**Next core split A–H:** 4 / 6 / 8 / 22 / 33 / 3 / 2 / 2 = 80. **Best next test:** price proof generation and independent replay across all six supports in D’s 15,282-profile \(t=17,m=16\) case before launching the full run.

Full review: `ralph/critic/round_015.md:1`. Next-round directives: `ralph/critic/LATEST.md:1`.
