# SCOUT: hardest-case techniques from other exact Ramsey / SAT results (agent scout, final 2026-10-26)

FINAL SUMMARY. 19 works read. No literature method gives a direct kill of case R. All tested transfers are NEGATIVE:
- Test A (Codish abstraction: vertex 0 = max #C4, split by Q): > 5x slower than plain SMS on the (3,9,36) benchmark (446 s).
- Test B (Schur-5 static hardness predictor, run by sms): too weak (Spearman |rho| <= 0.51, misses the tail cube);
  a short probe solve + re-split (already used in R(7)) is the better predictor. Details: notes/core_plan.md end.
- Test C (empty-hexagon-style structural cubes = codegree histogram of vertex 0): >= 10x slower, 1 cube timeout.
- Gauthier-Brown generalization covers: gain <= ~2x on our gluing classes (critic Review 29: <= 1.89 / 2.01).
- No transfer: flag algebras, Shearer-type bounds, Brandt/Sidorenko class S; AlphaEvolve 2026 only matched 39 vertices.
Still open as ideas from this scan: Wesley batched selectors for list x extension steps (row 13).

Question (user): can a new idea for our hard core (case R = 9-regular, and ~200 near-regular MTF distributions)
come from the way OTHER hard exact results solved their hardest case?
Short answer: most methods are already in our toolbox (notes/LIT_INSIGHTS_2026-10-25.md, prior_methods.md,
cases.md Sec 6-7, duo.md). All successful hardest-case proofs had one thing that we do NOT have: a SMALL
enumerable object for the hardest case (Codish: 78,892 neighbourhood colourings; GR1982: a counting kill;
Angeltveit: 1.55e9 graphs with slack 8). Our case R has R(3,9;30,99) ~ 9.5e17 (slack 99 - e(3,9,30) = 99 - 86 = 13).
So the transfer must give either (a) a new forced small object, or (b) a better split for SAT.
PDFs: data/papers/ (arxiv_<id>.pdf). Text extracts were made in my scratchpad only.

## Table (one row per work)

| # | work | hardest case | key idea | transfers to n = 40? | concrete test (<= 1 day, <= 8 CPUs) |
|---|---|---|---|---|---|
| 1 | Codish-Frank-Itzhakov-Miller, R(4,3,3)=30 (arXiv 1510.08266) | <13,8,8>-regular colourings | (i) degree-triple split kills all non-regular cases by "embed nbhd colourings + SAT" (3105 inst. for <14,8,7>); (ii) ABSTRACTION: degree matrices first (280 degree seqs -> 80 feasible -> 11,933 matrices -> 999 feasible), then SAT per matrix with partitioned lex SB (rows sym-broken only inside equal-row blocks); (iii) regular case: one SAT per nbhd colouring (78,892 inst., mean ~10 h, max 2400 h); (iv) several small nbhd lists merged into ONE constrained matrix (factor 9) | (ii) YES as a split device: vertex abstraction finer than degree = codegree histogram of v (= degree sequence of H_v) or C4-count q(v). (iii) NO: our nbhd class is 1e18 | Test A below |
| 2 | Gauthier-Brown, formal R(4,5)=25 (arXiv 2404.01761, ITP 2024) | gluing R(3,5,d) x R(4,4,24-d) | "generalizations" = partial graphs with <= 10 gray (free) edges; greedy exact cover of each list; one SAT per pair of generalizations; 81x fewer SAT calls, 15-21x less time | WEAK for us. MY TEST (runs/scout, 1000 random graphs each): mean # single-edge flips that stay in the class: full classes R(3,7,21) 11.7, R(3,8,27) 6.8 (dense, like theirs); our enumerable gluing classes R(3,9;30,<=87) 1.6 (9.5% have 0), R(3,9;31,<=96) 2.0, R(3,8;24,<=58) 3.1. Low-edge classes are rigid -> exact covers shrink lists by ~1.5-2x only | none (done; negative) |
| 3 | McKay-Radziszowski R(4,5)=25 (1995) | R(4,5,24) generation | gluing (3,5,d)+(4,4,23-d) with edge-count bounds per degree | already = our Theorem A + gluing | - |
| 4 | Angeltveit-McKay R(5,5)<=46 (arXiv 2409.15709) | near-regular | excess identity forcing MANY special vertices, then glue PAIRS; phased SAT filter | done by cases Sec 7 / duo R4: forcing only at e(H_v) >= 95 (classes 4e14+), empty in case R | - |
| 5 | Angeltveit R(3,10)<=41 (arXiv 2401.00392, EJC Sec 5/7) | 7-regular graphs in R(3,9,32,112) | special PAIRING for the regular case: two dual nbhds in R(3,8,24,63) glued along G' in R(3,7,16..18), hash on degree seqs, ~6 CPU-months for 506 graphs | analogue for case R = pair (u,w) with X_uw in R(3,8;20+c) (Lemma P/F, duo R2). Author (Sec 7): n = 40 9-regular "many orders of magnitude" bigger | already covered (cases Lemma F, gluing Sec 8) |
| 6 | Grinstead-Roberts R(3,9)=36 (1982) | 8-regular (3,9,36) | counting: e(H_v) = 144-64 = 80 < e(3,8,27) = 85, contradiction | analogue fails: 99 > e(3,9,30) = 86 (slack 13). Pair level: X_uw on 20+c vertices, e(X) = 18+9c+f vs e(3,8,20+c): cases Lemma P/F use it | - |
| 7 | McKay-Zhang R(3,8)=28 (1992) | regular-ish (3,8,28) | min-degree extension of complete small lists | same pattern as #5 | - |
| 8 | Goedgebeur-Radziszowski 2013 (arXiv 1210.5826) | e(3,9,n), R(3,10)<=42 | gluing extender with edge bounds; MTF generation | in use | - |
| 9 | Li-Duggan-Bright-Ganesh, certified R(3,8), R(3,9) (arXiv 2502.06055) | (3,9,36) | SAT+CAS (SMS-like orderly generation in CaDiCaL), 2,486 cubes, ~3,300 CPU-h | calibration only; their R(3,9) is our (3,9,36) benchmark (sms: 724 s with N(0) + 8-regular) | - |
| 10 | Heule, Schur number five (arXiv 1711.08076) | whole problem | cube-and-conquer: (i) problem-specific lookahead measure (clause-weight beat var-count); (ii) stop rule "#binary clauses > t"; (iii) HARDNESS PREDICTOR + re-split until no cube predicted hard; (iv) merge sibling cubes | (iii) YES for our heavy-tailed cubes (median 8e4 s vs mean 8e14 s): never estimate a cube set by mean of probes; re-split predicted-hard cubes first | sms: on 67-cube (3,9,36) set, fit predictor (#binary clauses / #free edge vars after cube) vs time |
| 11 | Heule et al., Keller dim 7 (arXiv 1910.03740) | G(7,s) cliques | hand-derived problem-specific SB that FIXES 3 vertices + clausal SB; general SB (shatter) took CPU-years | = our N(0) fixing + Lemma Mc/W; the lesson: derive the WLOG rule from structure, not generic SB | part of Test A |
| 12 | Heule-Scheucher, empty hexagon h(6)=30 (arXiv 2403.00737) | whole problem | (i) aux variables that GENERALIZE conflicts (3-hole vars); (ii) split ONLY on structurally central variables (middle points), with tautology-checked cube set -> linear speed-up on 1000s of cores; 1000 -> 2 CPU-years | (ii) YES: cube on the N(0)-H_0 incidence (codegrees c(0,w), N(1)-N(2) overlaps) instead of generic edge lookahead. (i) maybe: codegree counter vars | Test C below |
| 13 | Wesley R(J4,K7)=28 (arXiv 2606.17021) | 6.8M dual nbhds | batched selector cubes (1000 graphs per formula, 50-100x) | YES for every list x extension (critic W1); for R(6,f*<=5) 1.77M X graphs | gluing/sms (already proposed) |
| 14 | Lidicky-Pfender, SDP + Ramsey (arXiv 1704.03592) | blow-up densities | flag algebras on blow-ups of Ramsey colourings | NO: alpha <= 9 needs flags with >= 10 vertices; 10-vertex flags give only R(3,10) <= 54 (duo) | - |
| 15 | Shearer / Staton / Heckman-Thomas / Jones | alpha of triangle-free bounded-degree | local averaging bounds | NO: Shearer gives alpha >= 7.85 at d = 9, n = 40 (duo) | - |
| 16 | Brandt, Disc. Math 310 (2010) 662-669; Sidorenko, Disc. Math 91 (1991) | class S: triangle-free, every N(v) a maximum indep. set | S-graphs are regular with chi_f = n/alpha; Brandt determines possible chi_f (built from Sidorenko/Bauer graphs) | case-R graph is in S with chi_f = 40/9. NO bound on n: blow-ups keep chi_f. Full text paywalled (not read) | - |
| 17 | Nagda-Raghavan-Thakurta, AlphaEvolve Ramsey (arXiv 2603.09172, 2026-03) | lower bounds | LLM-evolved SA/tabu searches; R(3,10) search (Alg 18: Paley-29 seed, grow n -> n+1, SA on #K3 + #I10) only MATCHED 39 vertices | construction side only: weak evidence against a 40-graph; ideas (common-neighbour delta matrix, targeted flips) for anneal | anneal may reuse; low prior |
| 18 | Kirchweger-Szeider SMS, co-certificate learning (arXiv 2306.10427) | Kochen-Specker etc. | lazy propagators + minimality check | in use (sms) | - |
| 19 | Damnjanovic-Djordjevic, reflective/dihedral Ramsey numbers (arXiv 2607.06817) | symmetric colourings | dihedral-symmetric search | dihedral groups of order 40 already in symsat Cayley exclusion | - |

## Top 3 tests (new; not yet in the team notes as far as I can see)

A. Extremal-vertex WLOG by C4-count (from #1 abstraction + #11). Let q(v) = sum over w not in N[v] of C(c(v,w),2)
   (= number of 4-cycles through v). Choose vertex 0 with MAXIMUM q, add "q(u) <= q(0) for all u" (40 PB rows
   over codegree counters), and split case R by Q = q(0) (optionally also by the codegree histogram of vertex 0
   = degree sequence of H_0, as in Codish's degree-matrix step). Sum identity: sum_v q(v) = 4 C4, so cubes with
   small Q force few 4-cycles everywhere; cubes with large Q force many high codegrees at vertex 0 (smaller H_0
   classes, Lemma P/F). This REPLACES the Lemma Mc vertex choice (do not combine two vertex-0 rules; block
   partition must fix {0}, rest). Benchmark: 8-regular (3,9,36) MTF N(0) fixed (sms: 724 s) and duo's 8-regular
   (3,9,35) classification (answer C35): total time over all Q-cubes vs baseline. Owner: cases (lemma, critic),
   sms (encoding). <= 1 day on 8 CPUs.
B. Hardness predictor + re-split (from #10). Before any new cube-cost estimate, fit a cheap predictor
   (#binary clauses or #unassigned edge vars after the cube, SMS lookahead score) to solve time on the solved
   (3,9,36) cube sets (67 lookahead, 3564 search cubes), then re-split only cubes predicted hard. Goal: does the
   tail (one cube 1060 s of 1855 s) disappear? Owner: sms. <= 4 h.
C. Structural cubes (from #12). Split case R on the incidence between N(0) and H_0 (e.g. N(1) fixed = {10..17}
   WLOG, then codeg(1,j) - 1 = |N(1) cap N(j)| - 1 for j = 2..9 as a sorted vector, then the codegree histogram of
   vertex 0) instead of generic edge lookahead. Measure cube-time spread (max/median) on the (3,9,36) benchmark
   vs lookahead cubes. Owner: sms + cases. <= 1 day.

## Negative result (mine, runs/scout/flipdeg.py, count.py; 2026-10-25)
Gauthier-Brown generalization covers (row 2) do not help our enumerable gluing classes: mean in-class
single-flip neighbours 1.6 (R(3,9;30,<=87), 149,135 graphs), 2.0 (R(3,9;31,<=96)), 3.1 (R(3,8;24,<=58)),
vs 11.7 (R(3,7,21)) and 6.8 (R(3,8,27)). Sample 1000 graphs, seed 1, labelg canonical forms (nauty in tools/bin).
Non-exact covers (supersets) are sound for UNSAT but then the gain is a SAT-batching effect = Wesley #13.

## Results of Tests A and C (scout, 2026-10-25; runs/scout: addc4.py, validate.py, runcube*.sh, results*.txt)
Benchmark: (3,9,36), 8-regular, MTF, N(0) = {1..8} (sms/gen_ramsey.py), smsg --forbid-independent-set 9
--initial-partition 1 8 27, 1 CPU each, CPUs 136-143. Encoder addc4.py (codegree unary counters, q(v) = #C4 through v,
codegree histogram of vertex 0) validated vs exact values on C13, C35 (q = 48) and a random 16-vertex graph (SAT/UNSAT 5/5 each).
- Baseline: UNSAT 446 s (sms's older run: 724 s).
- Test A (vertex 0 = max q; cube "all q(u) <= Q, q(0) >= Q"; Q from 31 up): cube Q = 31 alone 271 s; cube Q = 48 not done at
  2214 s (stopped). So A is > 5x SLOWER than the baseline. Cause: the q counters (2.4M vars, 5.2M clauses) slow SMS a lot,
  and the extreme cubes are not easy. NEGATIVE.
- Test C (cubes = codegree histogram of vertex 0 = degree sequence of H_0, 1577 cubes, sound with the 1 8 27 partition):
  1576 cubes UNSAT, sum 3589 s, median 0.9 s, max 223 s; cube (n1,n2,n3,n8) = (18,4,2,3) TIMEOUT at 900 s.
  Total >= 4489 s = >= 10x SLOWER than the baseline (wall time with full parallelism: still >= 900 s). NEGATIVE.
Conclusion: on this benchmark, plain SMS with one fixed N(0) beats both abstraction splits; the "Codish abstraction" does
not transfer as a speed-up. Not tried at n = 40.
