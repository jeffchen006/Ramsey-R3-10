# Joint SAT plan for the hard core of n = 40 (owner: sms)

Status: v1, 2026-10-25. Cost estimate: Sec 4 (plain cubes infeasible; structured cubes being probed).
Contributors: sms (engine, cubes, estimate), cases (cube constraints), cert (proof cost),
satcore (second engine, cross-checks), gluing (bounds). Lead asked for this file.

## 0. Scope

Cover (notes/cases.md Sec 4a, 4d; Lean: R310.cover_lemma): if a (3,10,40)-graph exists, some
graph on V = {0..39} satisfies Phi (triangle-free, alpha <= 9) and one cube:

| cube | constraints (besides Phi) | status |
|---|---|---|
| R | all degrees 9; N(0) = {1..9} (MTF implied, M3) | SAT plan here |
| S8 | MTF; d(0)=8; N(0)={1..8}; e(H_0) <= 96 | CLOSED by gluing 2026-10-26 (enumeration, no certificate) |
| N(e), e = 161..179 | MTF; degrees 6..9; d(0)=9; N(0)={1..9}; e(G)=e; T*+1 <= e(H_0) <= t9max(e) | SAT plan here |

t9max(e) and T* per gluing scenario: cases/out/core_cubes.json, notes/cases.md Sec 4d. With the
gluing that is done or running ("U8+N86", T* = 86) all 19 values e = 161..179 stay; with the full
gluing plan ("sel", T* = 90) e = 167..179 stay (13 cubes, 208 degree distributions).
2026-10-26 (gluing final: deg 8 => e(G_v) >= 97, deg 9 => e(G_v) >= 88; no certificate): T* = 87. Filter of the
U8+N86 dists to t9 >= 88 (sms): e = 161 drops; e = 162..179 stay (18 cubes, 524 of 530 dists); the N(e) bound
becomes 88 <= e(H_0). Cube R is unchanged (9-regular => e(H_0) = 99). No new probes: the change is too small to
move the heavy-tailed Sec 4 estimate (R dominates). cases: please confirm in core_cubes.json (new scenario).

## 1. Engine and one order

- Engine: SMS (sms/sms-src, commit 63958bd + my patches: lazy independent-set propagator,
  proof log, edge-only cube cutoff). Details and validation: notes/sms.md.
- ONE symmetry order: SMS lex-min (0 < 1) of the row-wise edge vector, restricted to
  permutations that fix vertex 0 and the blocks N(0) = {1..d} and {d+1..39}
  (`--initial-partition 1 d 39-d`). Every cube constraint is invariant under these permutations.
  Never add satcore `--lex` (lex-max) to an SMS proof (cert rule).
- Encoding: sms/gen_ramsey.py. R: `-n 40 -k 10 --dmin 9 --dmax 9 --mtf --fix-nbhd 9`;
  N(e): `--dmin 6 --dmax 9 --mtf --fix-nbhd 9 --emin e --emax e --h-emin T*+1 --h-emax t9max(e)`;
  smsg `--forbid-independent-set 10 --initial-partition 1 9 30`.
  Optional proven additions (cases Sec 4a notes, cases_local.md): `--codeg-max 7` in R (L6);
  Lemma W in N(e) (only with the block partition; critic Review 21).

## 2. Calibration (what SMS can do now, 1 CPU each)

| instance | shape | result | time |
|---|---|---|---|
| (3,8,28), MTF, max degree 7 = d(0), N(0) fixed | k=8 near-regular, n = R(3,8) | UNSAT | 4269 s |
| (3,8,28) 7-regular, MTF, N(0) fixed | k=8 analogue of R | UNSAT | 1846 s |
| (3,9,36) 8-regular, MTF, N(0) fixed | k=9 analogue of R | UNSAT | 724 s |
| (3,9,36) same, 67 lookahead cubes (cutoff 250 edge vars) | cube-and-conquer test | all UNSAT | sum 2121 s, median 4.8 s, max 453 s |
| (3,9,36) same, 3564 search cubes (`--simple-assignment-cutoff 160`) | | all UNSAT | sum 1855 s, one cube 1060 s |
| no (3,8,m)-graph with <= E edges (F1), deg <= 7 | edge minima, k=8 | UNSAT | m=23: 3094 s; m=24: 8970 s |
| no (3,7,m)-graph with <= e(3,7,m)-1 edges | k=7 | UNSAT | m=17..20: 1.6, 4.4, 24, 151 s |
| (3,8,22) <= 41 edges | k=8 | UNSAT | 802 s |
| satcore (same cubes, --lex) | | UNKNOWN at 1 h for (3,8,28) D=7, 7-reg, (3,9,36) 8-reg | |

Caveats. (1) (3,9,36) is one vertex above the threshold; the n=40 cubes may be AT the
threshold (a (3,10,40)-graph may exist). (2) SMS is slow at FINDING graphs ((3,8,27) first graph:
431 s with SMS, 1.3 s without), so a long UNKNOWN is no evidence of non-existence.

## 3. Cube-and-conquer design

Level 1 (proof cases): R, and N(e) for each e (cases' cubes; optionally per degree distribution
from core_cubes.json, which adds the degree counts n4..n9 as cardinality constraints).

Level 2 (solver cubes): SMS lookahead cubing on edge variables only
(`--prerun 30 --assignment-cutoff C --cutoff-edge-vars-only --lookahead-only-edge-vars`),
C = number of assigned edge variables per cube. Each cube is solved by its own smsg process
(`--cube-file F --cube-line i`), same base CNF, same partition. Soundness: SMS symmetry clauses
are valid for the whole cube formula (they only remove non-canonical graphs), so cubes refuted
during cubing and the cubes solved later together cover every canonical graph.
Hard cubes (timeout) are re-cubed recursively with a larger C.
Certified run: solve each cube as its own CNF (base + cube units; cuberun {cubecnf}), so each
LRAT ends in the empty clause. The cube COVER also needs a proof: one SMS run on
base + {negation of each decision-only cube} (`--cube-only-decisions` keeps these clauses short),
with proof log; it must be UNSAT. Cube literals that are implied (not decisions) may come from
learned SYM clauses; they are valid for every canonical model, so the cover argument holds.

Search-based cubing (`--simple-assignment-cutoff`) was tested and is badly unbalanced (one cube
holds most of the work); do not use it.

## 4. Cost estimate (2026-10-25, v1)

Method: Knuth random probes (sms/knuth_probe.py, sms/probe_loop.sh). Level l: lookahead-cube the
current formula at C_l = C_0 + 60 l assigned edge variables, pick one cube at random, solve it as
base + cube units (300 s limit); if it times out, add its units and go one level deeper.
Estimate = c_0 + b_0 (c_1 + b_1 (... + b_L t_L)) (c = cubing CPU, b = #cubes, t = leaf CPU).
Unbiased but heavy-tailed. Leaves solved as units (assumptions are ~3.6x slower; cert test).
Data: runs/sms/probes/*.jsonl. 1 CPU per probe.

| formula | probes | median | mean | range of single estimates |
|---|---|---|---|---|
| cube R (9-regular, MTF, N(0) fixed), C_0 = 280 | 67 | 8.0e4 CPU-s | 8.4e14 CPU-s (2.7e7 CPU-years) | 2e2 .. 4e16 |
| calibration C1 (e(H_0) <= 86), C_0 = 220 | 14 | 4.0e6 CPU-s | 1.4e10 CPU-s (430 CPU-years) | 1e4 .. 2e11 |

Reading: the tail decides the total, and 15 of 67 R probes (22%) give > 1e9 CPU-s. The mean of a heavy
tail from 67 samples is itself unreliable, but the total for R is very likely >= 1e9 CPU-s
(>= 30 CPU-years), far beyond our 14 CPUs. C1 is a sub-case much smaller than the real N(e) cubes
(e(H_0) up to 92..98 instead of 86) and already costs ~1e10 CPU-s by the mean. Monolithic R and
C1 runs: no answer after 10+ h (CPU 60, 62).
Conclusion: plain SMS cube-and-conquer on the present cubes is NOT feasible.
Calibration (LIT_INSIGHTS 2026-10-25; Li-Duggan-Bright-Ganesh IJCAI 2025, arXiv:2502.06055): certified
R(3,9) took ~3,300 CPU-h = 1.2e7 CPU-s. Single R estimates are 2e-5..4e9 times that (median below it, mean ~7e7 times); R(7)
(median 6.3e5, mean 1.9e7) is at the R(3,9) scale. The calibration does not change the conclusion. Needed: much
stronger structure per cube (next section), then re-estimate with the same probes.

Max-codegree sub-cubes R(c*) (4 h of probes, 1 CPU each, same method): R(7) 6 probes median 6.3e5,
mean 1.9e7 CPU-s; R(6) 3 probes mean 1.9e12; R(4) 1 probe 7.5e8; R(3) 21 probes median 7.6e5, mean
7.7e9 (14% > 1e9); R(5) no finished probe. C1 with 30 more probes: mean 5e10. No sub-cube is
clearly feasible; R(7) (the rigid case) may be. Probes stopped 2026-10-25.

Earlier plan text: probes on the max-codegree sub-cubes R(c*), c* = 3..7 (Lemma Mc, confirmed):
vertex 10 with N(10) & N(0) = {1..c*}, codeg <= c* for all pairs, partition 1 c* 9-c* 1 29.
Also running: R + "every independent 5-set dominates >= 23 vertices" (cases B1, lazy propagator
--forbid-dominated 5 13), CPU 67.

## 5. Proof logging at scale (from cert; full table notes/cert_design.md Sec 4.1)

Measured on emin_8_22 (T = 802 s SMS search):
- LRAT 4.2 MB per solve-second; converter 0.24 T; cake_lpr 0.46 T (4.2 GB RAM).
- Store-and-check 0.7 T; or re-solve with CaDiCaL and stream LRAT into cake_lpr: 1.6 T, no storage.
- Symmetry clauses: Lean-verified sbcheck 0.66 ms/clause (primary), check_sb.py second check;
  VeriPB/CakePB > 2 T, so only sampled.
- Total certified cost: about 1.7-2.6 x the search CPU time.
- Rule: store-and-check for cubes with T < ~1 h (keep ext + sym.json + logs + sha256, delete
  plog/LRAT after "s VERIFIED UNSAT"); re-solve-and-stream or split further for longer cubes.

## 6. Extra constraints (to be measured)

Candidates: codeg <= 7 in R (L6; codeg <= 6 if cases' R7 runs come back UNSAT with DRAT);
deg_{H_0}(y) in 2..8 in R (L9); Lemma W in N(e); e(H_0) >= 87/88 from gluing in N(e).

## Test B (scout, from Heule Schur-5): static cube-hardness predictor on (3,9,36) cubes (2026-10-25, sms/testB_predictor.py)
Features after the cube (edge vars 1..630): #free edges, #binary triangle clauses, #true edges; Spearman vs solve time.
- L250 (67 cubes, 2108 s, max 453 s): rho = +0.19 / -0.22 / -0.23. Top-5% by any feature holds <= 3% of time.
- S160 (3564 cubes, 1855 s, max 1060 s, median 0.00 s): rho = -0.31 / +0.16 / -0.51. Top-5% holds 0%;
  fewest-true-edges 20% holds 100% of time (hardest cube rank 189/3564).
Result: static features are too weak to find the tail cube (no top-5% hit). Only a coarse filter (sparse cubes = 20%).
Use a short probe solve (seconds) as predictor + re-split, as the timeout-split chain for R(7) already does.
