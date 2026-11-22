# Lane C — round 8, 2026-11-22

R(3,10), Case R, R(6), and global `f*=9` remain **open**. No candidate.
`J` is the codegree-six graph, `f*` the minimum wing cross count among
those pairs. P2 means an isolated J edge, not an arm of a P3. Keep
their residues separate. For `(12,14)` the order-19 and order-21
windows have private core orders 12 and 14 with no shared core U.

## Results and claims for H / critic

| Label | Exact scope and result | Evidence (lane-relative unless stated) | CPU-h |
|---|---|---|---:|
| hand + enum, C-026 pending critic | In R(6), diagonal-four P3 with both arms 8, matrices 1 and 3 with both holes `(0,1)` contradict the singleton budget. Bound to exactly 30 e62 and 60 e63 residue IDs. 0 zero masks, 112/105 singleton masks per tag; omitting blocker four leaves 17 uncovered per tag in each layout. | `proofs/p3_singleton_budget.md`, `ROUND8_REPLAY.{md,sha256}`, `scratch/C/r8/{singleton-bindings.tsv,singleton-tagged.log,binding-check.log}` | 0.0008 replay |
| hand + enum, pending critic | **All nine** diagonal-four 8/8 layouts have q≤2 and 34/105 compatible zero multiset keys are impossible by integer capacity replay. All q=0 are impossible; the two named layouts `1:0:1:1:0` and `3:0:1:2:0` require q=2. The 71 uncut patterns are checked against exact X degrees/adjacency/codegrees: 3,333 pattern/residue keys, 212,200 placements on all 330 remaining layout/residue rows. No additional row exclusion. | `proofs/p3_singleton_budget.md`, `p3_zero_conditioned.py`, `p3_zero_residue.py`, `scratch/C/r8/{zero-all.json,zero-all-replay.log,zero-residue-bindings.tsv}` | 0.016 discovery + replay + placements |
| enum / estimate | `(12,14)` pre-join index exact audit on 4,910,040 held-out mapped requests across three profiles. 91-predicate bitmap prunes 97.6% before the original arc pass, but end-to-end CPU drops only 9.871→6.552 s (1.51×); 12 queries slower in aggregate. No new profile exclusion; do not scale. | `ROUND8_REPLAY.md`, `p2_prejoin_{build.py,index.hpp,methods.hpp,loop.inc}`, `scratch/C/r8/heldout-*log` | 0.015 incl. audits |
| confirmed round 7, C-025 | In global R(6), f*=9, `(12,14)`, smaller private K12 has 16≤e≤21. Four e23/24 profiles empty, 11 terminal profiles comprising 317,795,664 maps; 24 of 39 profiles (368,851,704,416 raw maps) open. Not an X or P3 bound. | `ROUND7_REPLAY.{md,sha256}`, `ralph/critic/round_007.md` | prior |
| confirmed round 6, C-024 | Global R(6), f*=9 rules out `(12,12)` wing union sizes, so at most one U vertex. Full 1,134 CakeLRAT checks and replay. Both prior frozen manifests still pass. | `ROUND6_REPLAY.{md,sha256}`, `ralph/critic/round_006.md`, `scratch/C/r8/freeze-prior.log` | prior |
| previously confirmed | R(7) excluded; R(6) has no P4. P3 diagonal-five residue e≤61; diagonals three/four e≤63. If f*≥8 each P3 has arms both 8 and diagonal 3 or 4. In global f*=9, J is a nonempty matching. Isolated f8/e80 has at most one degree-three vertex and when anchored X' has e≤64. | `ralph/critic/round_{001,003,004,005}.md`, `ROUND{4,5}_REPLAY.md` | prior |

## Jobs

None. All round-8 work was foreground and terminal, one core per
command, no detached jobs. Round-7 PIDs listed in the previous state
were checked and are gone. The timed commands and caps are in the
round-8 replay and `scratch/C/r8/*.time`; round-7 historical job tables
are `scratch/C/p2r7-census/{jobs,cover-jobs,run-jobs}.tsv`.

## Next

1. H/critic: check the conditional rows and exact 34/105 witnesses,
   separately from the verified four-blocker scope. The small hand
   lemma useful for Lean: two vertices avoiding a fixed independent
   eight-set must be adjacent; if they share any neighbour they
   cannot coexist. See the named proof; existing C-026 is two layouts.
2. P3: on one bounded residual layout, pre-index independent six-sets
   in X by unions of two columns; prescribe the q=1/2 omissions from
   the exact zero placements. Try using exact rounded upper bounds on
   singleton counts to force some h≥3 absent. The unproved LP scores
   in `zero-all.log` only suggest those bounds; require fresh integer
   witnesses. Do not start one solver job per zero or T tuple.
3. P2: do not scale 1.51× to the raw join. A future index must avoid the
   mapped-predicate cost itself, not just avoid passing 97.6% into arcs.
   `(12,13)` still needs U1 logic and calibration; `(13,13)` needs
   H20/K13 catalogues. Isolated anchored f8/e80 e64 (236 keys) is a
   separate bounded option, not a P3 case.
