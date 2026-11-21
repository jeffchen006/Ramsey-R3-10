# Lane C — round 6, 2026-11-21

R(3,10), Case R and R(6) remain **open**. No candidate. In R(6), J
is the graph of codegree-six pairs. P3/P4 denotes a distinct-root
path in J, not in G. P2 is an isolated edge component of J, not an
arm of a P3. `f*` is the minimum wing cross-edge count across the
codegree-six pairs. Pair and three-root residues are different.

## Results and claims for H / critic

| Label | Result | Evidence (lane-relative unless absolute) | CPU-h |
|---|---|---|---:|
| enum + cert, pending critic | In **global R(6), f*=9**, `(12,12)` wing union sizes are excluded: exact H21 join, 646,736 marked pack pairs ->1,134 pinned completions, all 1,134 CakeLRAT checked and replayed from fresh CNFs with exact hash binding. Thus every such pair has at most one X vertex avoiding both wings. `(12,13),(12,14),(13,13)` open; does not cover all isolated f9 pairs under weaker global conditions. | `proofs/p2_complementary_windows.md`, `ROUND6_REPLAY.{md,sha256}`, `scratch/C/p2r6-cross-index.{tsv,log}` | 0.004 join/redo + 0.120 produce + 0.118 replay + 0.004 CNF pilots |
| hand + enum (filter only) | H21 side 13/14: 243,859/33,222 marks, 1,458,506/353,115 packs. Pure one-window independent-set degree-capacity bounds removed **none**. Exact `(12,14)` projection gives 39 H19 core-edge/degree profiles; no H19 or H20 completion inferred. | `proofs/p2_complementary_windows.md`, `scratch/C/p2r6-asymmetric-capacity.log`, `scratch/C/p2r6-h19-profiles.tsv` | 0.004 |
| enum / estimate (sample only) | On 381 K12 cores, optimized bitset gluer byte-matches the 117,959 raw H19 windows (53.38 ->11.54 CPU-s). Exact 39-profile subset: 5,013 raw / 4,749 rooted classes (3.90 CPU-s), over 513M raw wing-C maps *in the sample alone*. Linear full projection ~1.58e11 maps, not a bound. Unprofiled K13/side12 pilot TIMEOUT at 100 wall-s. No full H19 or H20 run. | `p2_marked_glue.cpp`, `p2_profile_cost.py`, `scratch/C/p2r6-h19-profile-index.log`, `ROUND6_REPLAY.md` | 0.019 K12 tests + bounded K13 pilot |
| previously confirmed | R(7) excluded; R(6) has no P4. Round 5 diagonal-five P3 residue <=61; diagonals three/four <=63. If f*>=8, each P3 has both arms 8 and diagonal 3 or 4. In global f*=9, J is a nonempty matching. These are P3 conclusions, not pair residue edge caps. | `ralph/critic/round_{001,003,004,005}.md`, `ROUND5_REPLAY.md` | prior |
| previously confirmed | Isolated f8/e80 has at most one degree-three vertex and if it exists its anchored X' has e(X')<=64. Complete-wing supports have 10–12 singletons and excess <=2; global f*=9 excludes c6 wing siblings, and each wing covers >=12 X vertices. | `ROUND4_REPLAY.md`, `proofs/p2_full_wings.md`, `ralph/critic/round_{004,005}.md` | prior |

## Current jobs

None. Production PIDs 1308534/1308577/1308640/1308734 and replay
PIDs 1401955/1401989/1402053/1402098 terminal. Full one-core-per-job
records (start, hard end, command and log) in
`scratch/C/p2r6-cross-{jobs,replay-jobs}.tsv`; all queues empty.
Round-five indexes and proof data remain frozen and unchanged.

## Next

1. Critic and H: audit the `(12,12)` closure at its named scope;
   `ROUND6_REPLAY.md` gives bounded spot-check commands and exact
   bindings. The filter itself is `enum`, not a proof-logged solver.
   Do not regenerate all 1,134 refutations in production to spot-check.
2. Other `f*=9` sizes need a stronger pre-join signature than
   bare degree multisets. Do not launch the raw asymmetric join:
   the sample is already over 513M raw maps. Try one-sided incidence
   demands induced by fixed independent 5/6-sets and the smaller
   wing's exact one-/two-wing support types, against an exact small
   matched control. The aggregate degree inequalities are a measured
   no-op; any stronger test should enforce simultaneous incidences.
3. Keep H19 / H20 / H21 windows and their K12 / K13 / K14 cores
   separate. `(12,13)` requires H20 with one marked U; `(13,13)`
   needs two H20s with no U. No inference from the H19 pilot to them.
4. Preserve P3 proofs. Do not rerun wide/flexible lower layers,
   P4/P5, or R7. An isolated f8/ e80 anchored e64 pilot (236 fixed
   keys, not tried) is separate from this round and from P3 caps.
