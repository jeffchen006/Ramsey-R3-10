# Idea scouts, 2026-11-21 22:37-23:30: what to try next (operator digest, by Claude Opus 5.5)

Four scouts: fable_R, fable_G (Claude Fable 5.2), astra_R, astra_N (GPT-6.2-astra). Each read `TESTED.md` (astra) or the
paper + notes (fable). Nothing here is a closed case. Each line: idea, file, what is new vs TESTED.md, operator check.

## Lane B
1. Import 1,142 new critical order-32 e108 keys (astra_N.md idea 1, `scratch/ideas/astra_N/handoff.g6`): found by thinning
   order-33 host cards, a host family B never used. Missing e108 classes fall from 1,266 to 124 of 2,104,151 (GR T14).
   Operator replay: `audit_handoff.sh` passes (hash, B validator, irreducible 1142/1142, 1,756 distinct, 123,336 witnesses).
   If the last 124 are found and excluded: 9 more distributions in G's model (6 overlap U88).
2. Four-root views for critical e88 (astra_N.md idea 3): speculative; kill the two-card join (10^12-10^13 pairs).

## Lane C
1. R(6) three-root paths, singleton budget (astra_R.md idea 1): on the two 8/8-arm keys (1,(0,1),(0,1)) and (3,(0,1),(0,1)),
   four boundary independent 5-sets give sum|L_t| <= 16 against >= 20. Operator replay of `singles.py`: 0 uncovered masks
   in both layouts (68 without the 4th blocker). Rebuild independently, bind to C's index, then extend to the other s=4 layouts.
2. Isolated R(6), (12,14) split: test whole wing fives with exact core padding (astra_R.md idea 3): 795/796 sampled maps rejected;
   needs an inverted index to be cheaper than per-map tests (~80 CPU-years per map otherwise).
3. (IF) rows: intersecting families of masks, sum p_M <= 9 - |I| (fable_R.md idea 1, idea 5): proof checked by operator; small gain.

## Lane D
1. Punctured K3,3 root for all of R(3) (astra_R.md idea 2): >= 180 squares of codegree-3 diagonals; 11 boundary profiles (p,q,z)
   fix six neighbourhoods. Calibration: the 3 cap-3 6-regular (3,7,22) classes in 3.071 solver CPU-s.
2. Cold max-codegree root for R(5)/R(4) (astra_R.md idea 4): at a cold root (all C-pair codegrees <= 3), M = 5 forces
   z = t = 0: ten double sites (one per C pair), three singles per coordinate, the doubles span a subgraph of the
   Petersen graph (396 cores mod S5); M = 4: six support profiles. Operator checked the counting identity. Hot roots stay open.
3. Top-pair (non-edge) kernels with f-pattern (fable_R.md idea 3): <= 317 (c*=5) / <= 5,624 (c*=4) keys vs 2.85e6 / 9.6e4 edge kernels;
   per-key cost unknown; calibrate on 8-regular (3,9,35).

## Lane G
1. Two-sided Hall rule with edge forcing for the nine two-root e168 keys (astra_N.md idea 2): 6M sampled overlays -> 46 -> 0
   after propagation (samples, not classes). Enumerate integer tables n_ST, not permutations.
2. Floor-closability triage (fable_G.md idea 2): list distributions no residue floor can close; stop floor censuses that cannot pay.

## Lanes E/F
- Pair-excess root, split on min eps (fable_G.md idea 1): speculative; pair classes 1e14 -> 1e6..1e9 claimed, not measured.
- Do NOT run spectral / theta / SDP / flag jobs: fable_G and fable_R measured them as no cut.

## Operator's own candidate, now weakened
- R(7)-style fixed-X packing for R(6) f* <= 5 (1.77M X): astra_R measured on 8 seeds that the side-triple stage still leaves
  56,773-93,666 triples per seed; not a reason to run the 1.77M catalogue yet.
