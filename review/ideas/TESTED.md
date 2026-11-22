# What is already tested (old project 2026-10-24..26 + this run, rounds 1-3). Do not re-propose without saying what is new.

Sources: paper/latex/sec5-8, notes/{duo,SCOUT,core_plan,gluing,cases,cases_local,anneal,algebra,known39,symsat,satcore,sms,LIT_INSIGHTS,prior_methods}.md, ralph/CLAIMS.md, ralph/rounds/round_00{1,2,3}.md.

## SAT (all measured, all negative at n = 40)
- SMS cube-and-conquer on cube R and on R(3..7), N(e), calibration C1: Knuth probes, mean 8e14 CPU-s for R; heavy tail.
- Extra rows in SMS: Lemma F (f >= 6), codeg <= 7, deg_H0 in 2..8, Lemma W, independent 5-sets dominate >= 23 (B1 negation), q(v) counters.
- Cube design: lookahead, search cubes, Heule hardness predictor (static features), re-split of hard cubes (R(7): 28/31 sub-cubes > 8 h),
  structural cubes on N(0)-H_0 incidence (codegree histogram of vertex 0, 1577 cubes, >= 10x slower), Codish abstraction by max q(v) (> 5x slower),
  split by max degree.
- satcore (CaDiCaL 3.0.1 + lazy IS + static lex), plain CaDiCaL, decision orders, CaDiCaL configs, --hv-min edge bound rows: no gain.
- Edge kernels (M = 3..6: 238 / 96,135 / 2,852,820 / 26,326,286) + SMS completion, with/without Aut lex clauses: >= 1e11 CPU-s for M = 5, 6.
- Fixed X = G - N[u] - N[w] (|X| = 27) + SAT for 13 vertices: > 1M conflicts per X.
- This run: D tried local / minimum-edge / factored / Boolean-mask / one-sided profile pinning / shared-support encodings on R(3) kernels: all timeouts.

## Gluing (GR / Angeltveit style)
- S8 and t9 <= 87 done (no output). t9 <= 88: ~4 days on 32 cores (old), this run: e88 dual slices, MTF cover gluer, ~1,100 CPU-h left.
- t9 <= 90 ~0.9 CPU-year, <= 92 ~80 CPU-years. 9-regular gluing needs R(3,9;30,99) ~9.5e17 graphs: infeasible.
- Pair gluing (X in R(3,8;20+c)): worst case every pair class >= 1e14; typical min class 1e11.5. Seeds (B1, J9, X+(s-1)K1): seeded classes 1-4% of all.
- Two-step gluing R(6, f* <= 5) (X in R(3,8;26,75..77), 1,765,856 graphs) at ~40 min/X: ~130 CPU-years (old estimate; NOT re-measured with the new packing solver).
- Gauthier-Brown generalization covers: <= 2x. Wesley batched selector cubes: proposed, not run.

## Counting / LP / SDP
- B2 profile LP over independent s-sets (case R): feasible, wide ranges. Codegree-typed pair LP: feasible, C4 in [540,1050].
- Fractional regular-gluing LP on H (independent 8-sets): killed adversarial H only with all 4..8-set rows, minutes per H; uniform type dual too weak (exact counterexample). Route closed.
- AM excess forcing (R(5,5) idea): forces several vertices only at e(H_v) >= 95..98; no use in case R. Profile ILP: 7 kills (certified).
- Flag algebras: 10-vertex flags give only R(3,10) <= 54 (not run with codegree types). Shearer: alpha >= 7.85. Brandt class S: not read.
- This run: G profile / typed wedge / private / pair / lifted / packing Farkas rows; residual floors e(H6) >= 120, e(H7) >= 107 from HoG covers + LRAT.
  C kernel projection LP (78 of 238 R(3) kernels). fable_R: spectral trace LP to degree 12 feasible (no cut).

## Structure (proved, used)
- Lemma Mc (c* split), R7, P, F, H, N, W, M0-M3, Theorem A, L1-L9, matching lemma, q(v) identity and bounds, J9 seed, Lemma T.
- This run: R(7) closed (side packages + colour packing); R(6): codegree-6 graph has components of order <= 3 (C8, P5, P4 excluded);
  P3 diagonal-5 residue e(X) <= 63; no K3,6 / K4,5; K3,3 not in R(3); K4,4 not in R(4).

## Symmetry
- Circulant, Cayley (all 14 groups of order 40), vertex-transitive (1963 minimal transitive groups; web claim), prime order >= 7,
  order 5 (f = 10, 15 cert; (5,5) cert this run; (5,0) open), order 3 (f >= 13 cert; f in {7,10}, a in {5,6} hand this run; f in {1,4,7,10} open),
  order 2 (a = 7 cert except f = 34; this run: (2,34), (2,32) t=1, (2,28,a<=5), (2,30,a=6) closed; 18 classes still open overall).
- Lifts by groups of order 20 (Z20, Z10xZ2, Dic5, F20): min 40 independent 10-sets.

## Construction (search for 41)
- SA / tabu / vertex rewiring / sawtooth soft triangles (Exoo 2013) / symmetric Z_m / grow 38->39->40: best 40-graphs ~23-44 independent 10-sets.
- known39: Exoo rewire closure 18.4M of 25.3M graphs (incomplete) + 33 components: no extension to 40. One-triangle 40-graphs: 20,000 tested.
- Algebra: PG(3,3), PGL(2,q), level sets over F_41/Z_40/Z5xZ8, FunSearch-style program search, Higman-Sims subgraphs (best 78),
  deletions from Exoo's (3,11,46) graphs (40 impossible) and circulants N = 44, 45, ext2 from (3,10,38) circulants (UNSAT).
- This run: F random start + orbit flips + orbit-window SAT repair; best degree-valid 40-graph 44 independent 10-sets, 9-regular, order-3 automorphism.
- Published: Angeltveit's >= 43M (3,10,39)-graphs do not extend; GR/Ang data not public.

## Not found in any note (candidates for new work)
- SMS on the complement form (DuLBG: R(8,3) 6x faster than R(3,8)). MIP / CP-SAT engines. BDD/ZDD. Exact SDP with codegree types.
- The R(7)-style "fixed X + custom packing solver" for R(6) with f* <= 5 (1.77M X) and for other forced-X branches.
- Batched selector SAT (Wesley) actually run on any list.

- Round 7 fable_R trace grid LP, degree 12/130 rows: feasible again in `scratch/critic/r7/ideas/replay3.log`; no cut. This is not a verdict on untested SDPs.
- Round 7 fable_G spectral/theta screen: C35 has theta ≈12.4106 at alpha 8 (`scratch/critic/r7/ideas/replay3.log`); don't use a theta<10 requirement as a necessary condition, or an alpha upper bound to prove alpha≥10.
- Round 7 fable_G unpinned eager C35+5: 185 variables/306,440 clauses, no terminal answer in the reported 13-minute cap, no positive control (`fable_G.md`, `scratch/ideas/fable_G/eager35.log`); no unchanged retry and no exclusion.
- Round 7 astra_N e88 two-card materialized join: 55,558 compatible d6/d6 record pairs on 1,024 inputs per side after overlap/budget screening (`scratch/ideas/astra_N/mate.log`); 10^12–10^13 total is an extrapolation, not a measured census. No materialized run; indexed multiway idea separate.
- Round 7 astra_R R(6) three-root unstrengthened panel LP: feasible on the tested 8/8 diagonal-three rows and sampled 16+16 lower diagonal-five boundaries (`scratch/ideas/astra_R/{panel,lower}.log`); no further unchanged LP sweep.
- Round 7 astra_R R(6) isolated wing fives tested independently per map: 795/796 sampled maps rejected, one cap, 12.62 CPU-s (`scratch/ideas/astra_R/full32.log`); too slow for the full join. Cached/inverted join is a distinct unmeasured idea.
- Round 7 astra_R R(6), f*≤5 fixed-X side triples: all eight target pilots still had 56,773–93,666 candidates after the side-triple stage (`scratch/ideas/astra_R/wing.log`); no bulk traversal of the 1.77M source on this measurement.
- R009 N: the complete 560 e95 critical parents at d8 yielded 46 novel e108 keys, but d6/d7 yielded none beyond them and none of the 1,142 R7 scout keys were recovered by d8; no repeat of these three completed arms for the remaining 63 (`scratch/critic/r9/{N,N95}.log`).
- R009 N: the 35 additional target-derived e≤101 parents at d7/d8 added zero, and the exact d6 parent extension through e102 added zero (`scratch/ideas/r009_N/{ep.new,f6.6.log,f6.new}`); do not extrapolate this local fixed point to other parent families.
- R009 N: order-33 two-hole source produced 278 known-or-already-seeded keys, zero beyond the e95 wave (`scratch/ideas/r009_N/{strong.set,strong.new}`, `scratch/critic/r9/misc.log`); do not resample unchanged.
- R009 N: e88 outside-prefix **good-root** lift from all 1,342 e77 parents produced zero at d6/b52 and d7/b44, including terminal traversals of 51,918,867 and 14,977,775 nodes (`scratch/critic/r9N/audit89.{6,7}.log`); no rerun, no conclusion for other roots or higher parents.
- R009 R: opposite K3,3 **22/22** search is exhausted at caps five/six (zero refined mates at five; 863 upper-independent deaths + 19 checked proofs at six); don't repeat pairwise enumeration or port the raw pair-count gain as a wall-time estimate (`scratch/critic/r9/R.log`).
- R009 R: at cap five the 274 systematic and 1,024 disjoint held-out **22/21** hosts gave 0 survivors among 330 and 10,964 aligned maps; no rerun of these samples or full-census extrapolation from the low-density systematic sample (`scratch/critic/r9R/{mixed-join,held-join}.log`).
