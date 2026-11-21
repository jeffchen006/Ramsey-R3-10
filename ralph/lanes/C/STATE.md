# Lane C — round 5, 2026-11-21

R(3,10), Case R, and R(6) remain **open**. No candidate. In R(6), J
is the graph of codegree-six pairs. P3/P4 denotes a consecutive
distinct-root path in J, not a path in G. P2 means an isolated edge
component of J, never an edge of a P3. X denotes the residue of the
specific marked roots; pair and three-root residues are different.

## Claims for H / critic

| Label | Result | Evidence (lane-relative unless absolute) | CPU-h |
|---|---|---|---:|
| accepted | R(7) excluded; R(6) has no P4. C-016 e(X)<=62 for diagonal-five P3 and <=64 for three/four; C-017 isolated f8/e80 has at most one degree-three vertex and when it exists its anchored X' has e(X')<=64. These were confirmed in round 4. | `ralph/critic/round_00{1,3,4}.md`, `P4_REPLAY.md`, `ROUND4_REPLAY.md` | prior |
| cert, composite pending critic | Diagonal-five P3 e62 excluded: 90 ordered, 49 reversal boundary orbits, 44 passing ×30 residue graphs. All 1,320 checked and byte-identically replayed, no caps/absences; exact terminal shard and retained proof hash audit. With C-016 leaves e(X)<=61 at diagonal five. | `ROUND5_REPLAY.md`, `p3_round5_index.py`, `scratch/C/p3r5-e62-index.{log,tsv}` | 0.020 pilot + 2.377 produce + 0.997 replay |
| cert, composite pending critic | Diagonal-three and diagonal-four P3 e64 excluded, 59+59 guarded CNFs, checked, byte-identically replayed and retained proof hashes rechecked, no caps/absences. With C-016 leaves e(X)<=63 at diagonals three/four. Not a pair-residue bound. | `ROUND5_REPLAY.md`, `proofs/p3_e63_relaxation.md`, `scratch/C/p3r5-e64-index.{log,tsv}` | 0.454 produce + 0.196 replay (+ prior pilot) |
| hand bridge, composite corollary | No P3 can have both arm cross counts nine. At diagonal three, at least four X vertices avoid T, thus avoid both wings by a saturated-neighbourhood argument; accepted e(X)<=64 leaves b<=1, so there is an independent boundary eight-set anticomplete to those vertices. C21/C22/C35 and positive/corrupted small complete-arm controls. Global f*=9 forces J to be a matching, not an exclusion of that subcase. H proved the generic T-avoider lemma in Lean; the residue cap is separate. | `proofs/p3_complete_arms.md`, `scratch/C/p3r5-complete-arms.log`, `lean/R310/CompleteArms.lean` | <0.001 |
| cert, composite pending critic | 9/8 P3 excluded. Four-antineighbour CNF excludes 3/16 high-arm diagonal-three layouts at e61..63 (keys 1/5/6); 13 relaxation-SAT. Together with the caps and the other hand layout rules there are two remaining e63 layouts. All 60+60 Lite6 refutations checked, terminal, hash-bound to replay; no caps/absences. Thus at f*>=8 every P3 has two arms of count 8 and diagonal 3 or 4. No conclusion about isolated P2 f=8 or f=9. | `proofs/p3_mixed_arms.md`, `scratch/C/p3r5-antineighbour{,-replay}.log`, `scratch/C/p3r5-mixed-index.{log,tsv}` | <0.001 tiny + 0.021 pilot + 0.318 produce + 0.091 replay |
| hand | Complete-wing pair: 10..12 singleton-C attachments, support excess over two at most 2, lower for any singleton avoiding both wings. Hence in global f*=9 no c6 pair sits inside a wing, each wing sees ≥12 X vertices, at most two X vertices avoid both. Deleting smaller wing gives marked H21 or order-20 window with K13. | `proofs/p2_full_wings.md`, `scratch/C/p2r5-wing-final-control.log` | <0.001 |
| enum cover only | Exact H21 root census: 13,576,969 marks ->35,257 by degree sum ->35,248 with wing packing ->35,099 with root and singleton caps (31,565 classes). K13: 246,483/275,086 pass. C22 7 full-wing pairs, both orientations, plus corrupted overlap checks. Three files byte-identically rebuilt. No e81 exclusion. | `ROUND5_REPLAY.md`, `p2_wing_windows.cpp`, `scratch/C/p2r5-wing-replay.log`, `scratch/C/p2r5-{core13,window21,strong21}.tsv` | <0.003 incl. replay |

## Current jobs

None (all listed round-five wrappers gone as of 21:35:22 CET with
complete terminal indexes). Historical PID/command/log/start/end
records are in `LOG.md`, `scratch/C/p3r5-{mixed,e64}-jobs.tsv` and
`scratch/C/p3e62-{full,replay}.tsv`. Exact bindings and scope:
`ROUND5_REPLAY.md`, `ROUND5_REPLAY.sha256`.

## Next

1. All round-five composites need critic/H review and explicit named
   scopes. Do not rerun any complete production; replay instructions
   and stable indexes are in `ROUND5_REPLAY.md`.
2. Do not repeat the broad flexible lower runs or P4/P5. If an 8/8
   P3 pilot is approved, 996 necessary fixed keys remain after e64
   and 9/8 closure: diagonal 3 gives (1,3,8) layouts at e61..63;
   diagonal 4 gives (0,4,5). Low unconditioned diagonal-five e61/e60
   is 894+320 keys estimated ~4.2 CPU-h production from five each.
3. Full-wing P2 next: try a complement-signature join for wing
   sums (12,12), not 35,099 unpinned SAT calls. Both marked H21
   windows share C plus the two wing-avoiders U. For each c in C,
   their marked column degrees sum to `9 + deg_U(c)` (two root
   incidences, seven total C--X incidences, and U counted twice).
   Mark the U bits and its induced edge, then match complements
   and measure counts before any solve. Handle (12,13/14) and (13,13)
   separately; no overlap assumptions transfer to those branches.
4. Leave isolated f8/e80 anchored e64 (236 fixed keys, not tested)
   separate. Unanchored e80 and e81 have no P3 edge cap. No general
   use of these results in R(5) or another degree distribution.
