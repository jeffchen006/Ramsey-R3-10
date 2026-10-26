# Gluing (GR2013 / Angeltveit) for n = 40, and gluing + SAT hybrids

Author: agent `gluing`. Date: 2026-10-24. Status: v1, reviewed by `critic` (notes/critic.md Review 20: no errors; S8 e=95 result independently confirmed).
Code: `gluing/src/` (see `gluing/README.md`). Logs: `runs/gluing/`.
[GR] = Goedgebeur–Radziszowski, EJC 20(1) #P30 (2013), arXiv:1210.5826v4.
[Ang] = Angeltveit, arXiv:2401.00392v2 (EJC 32(4) #P4.30).
Case split: `notes/cases.md` (agent `cases`), Theorem A and Sec. 3-4.

## 0. Summary

1. Pure gluing cannot do the 9-regular case. Every H_v is in R(3,9;30,99). I estimate
   |R(3,9;30,99)| = 9.5e17 (MCMC, Sec. 2). Gluing one H costs 3 ms, so the gluing alone is
   ~9e7 CPU-years, and generating the inputs costs more. Our budget is ~25 CPU-years
   (96 CPUs x 3 months). Gap: about 7 orders of magnitude.
2. Gluing can do the cases where some vertex has a sparse H_v:
   - S8 (some 8-vertex v with e(H_v) <= 96, 35,714 graphs): cheap. Running now (Sec. 5).
   - N(t) with t9 <= 91 (some 9-vertex v with e(H_v) <= t9): feasible with optimised code
     (Angeltveit speed), ~6 CPU-years in total for t9 <= 91; t9 = 92 is ~80 CPU-years
     (not feasible); t9 >= 93 is not feasible.
   With cases' current table (scenario U8), gluing kills the MTF distributions with
   t9 <= 91: 6+8+6+15+24+43+59 = 161 of 545. The other 384 (all with e(G) >= 163, incl. the
   9-regular one) need SAT or a new idea.
3. "Fix H, SAT glues" is slower than the C gluer (65 ms specialised CNF, 20-40 s generic
   satcore, vs 3 ms). "Fix less, SAT does more" (fix X = G - N[u] - N[w] in R(3,8;27), SAT adds
   13 vertices) did not finish one instance in 180 s with satcore. So SAT gives no speed-up on
   a fixed large substructure. SAT is needed where enumeration is impossible (near-regular
   distributions); gluing results go into SAT as extra cardinality constraints (Sec. 6).
   Better (cases' t9 scan with larger glued sets U, cases/out/t9_scan_mtf.json): glue
   U8 = R(3,9;31,<=99) (2.6e8) + U7 = R(3,9;32,<=112) (1.55e9) + U6 = R(3,9;33,<=121) (14,395)
   + R(3,9;30,<=90) (2.9e9), ~5e9 graphs in total (~1-2 CPU-years at [Ang] speed): this closes
   337 of 545 MTF distributions; 208 remain, all with e(G) >= 167 (near-regular, t9 = 96..99).
4. Recommendation (Sec. 7): gluing does S8 + N(t9 <= 90 or 91); SAT does the rest, with the
   gluing-derived constraints "every 8-vertex has e(H_v) >= 97, every 9-vertex has
   e(H_v) >= T+1". The 9-regular case is SAT-only (or needs a new structural idea).

## 1. Gluing method and my implementation

Method ([GR] Sec. 3, [Ang] Sec. 4): v of degree d, H = G_v = G - N[v] is a (3,9)-graph on
39 - d vertices. Each neighbour u_i of v gets N(u_i) = {v} + S_i, S_i independent in H.
G has alpha <= 9 iff for every K subset of {1..d}: alpha(H - union_{i in K} S_i) <= 9 - |K|
(automatic for |K| = 1). Pairs are checked with bitsets over the independent 8-sets of H.

My code (`gluing/src/`, C, n <= 62, no nauty inside; nauty `shortg` from `tools` for iso rejection):
- `glue.c`: GR algorithm: all independent sets with |S| in [DMIN-1, DMAX-1], sorted by size,
  pair-compatibility bitsets, forbidden vertices (degree cap), min-degree coverage pruning, edge
  bounds [EMIN, EMAX], alpha(H - union) <= K - depth at depth >= 3, exact alpha(G) at the leaf.
- `glue2.c`: Angeltveit's variant: only maximal independent sets (Bron–Kerbosch), monotone
  prunings on maximal tuples, then expansion to subsets (canonical owner = first maximal set
  containing S) with degree/edge pruning and subset pair checks. 30x+ faster than glue.c for
  d = 9 near-regular gluing; slower when the edge budget is tight (generation steps).

Validation (all passed):
| test | result | reference |
|---|---|---|
| rebuild all R(3,3..6;n) from scratch (min-degree gluing + shortg) | R(3,4;n) = 1,2,3,6,9,15,9,3; R(3,5;13) = 1, (12) = 12, (11) = 105; R(3,6;17) = 7, (16) = 2576, (15) = 64732 | McKay's tables; [Ang] Table 1 |
| R(3,7;22) from R(3,6;15..17) | 191 | [GR] T12, [Ang] T1 |
| R(3,7;21) from R(3,6;14..17) | 1,118,436 (each e = 51..63 equal to [GR] T12) | [GR] T12 |
| R(3,7;16..19, low e) | 2 / 674 / 9050 / 11, per-e counts equal | [GR] T12 |
| R(3,8;22,42), R(3,8;23,<=51), R(3,8;24,<=58) | 21 (= HoG file), 102/8241/356041, 51/3419/129347 | [GR] T13 |
| glue.c vs glue2.c | identical output sets on all R(3,7;22) steps and edge-limited runs | - |
| re-glue known graphs from their own G_v | C35(1,7,11,16) and Exoo's (3,10;39) are rebuilt; glue = glue2 | - |
Increments t_d for generation (GR Sec. 3) are checked by `tcheck.py` (exact enumeration of all
integer degree sequences) and optimised by `tscan.py`/`topt.py`.

## 2. How many input graphs? (MCMC estimate)

`mcount.c`: Markov chain on labelled (3,k;n,e)-graphs with e in a window; moves = toggle an
edge / swap an edge with a non-edge; Wang–Landau weights, then a fixed-weight production run.
Estimator (broad histogram / transition matrix): g(e) <a>_e = g(e+1) <r>_{e+1}, where a = number
of addable non-edges, r = number of removable edges (exact double counting; within a level the
chain is uniform). Labelled counts / n! = iso-class counts when most graphs have |Aut| = 1;
the anchor level uses the exact sum over a HoG/McKay file of 1/|Aut| (nauty countg --a).

Validation (estimate vs published exact count):
| class | estimate | exact | source |
|---|---|---|---|
| labelled ratios R(3,6;16), R(3,7;21), all e | within 1% / ln-error <= 0.04 | own exact sets | - |
| R(3,9;30,87) | 1.470e5 | 147,335 | [GR] T14 |
| R(3,9;31,96) | 35,160 | 35,154 | [GR] T14 |
| R(3,9;32,105..108) | 880 / 18,130 / 233,000 / 2.10e6 | 952 / 18,598 / 234,681 / 2,104,151 | [GR] T14 |
| R(3,9;32,<=112) | 1.49e9 | 1,554,928,360 | [Ang] 3.3 |
| R(3,9;33,119..121) | 73 / 1481 / 17.5e3 | 69 / >=1223 / >=13081 (total <=121: 14,395) | [GR] T14, [Ang] |
| R(3,8;22,43..45) | 1417 / 69,620 / 2.28e6 | 1521 / 72,353 / 2,331,462 | [GR] T13 |
| R(3,8;23,<=53) | 2.385e8 | 238,854,716 | [Ang] 3.2 |
| R(3,8;24,<=62), (24,<=63) | 1.454e10, 1.58e11 | 14,645,288,701, ~150e9 | [Ang] 3.2 |
| R(3,8;25,<=70) | 2.04e9 | 2,120,846,970 | [Ang] 3.2 |
| R(3,8;26,<=77) | 1.80e6 | 1,767,543 | [Ang] 3.2 |
Typical error: <= 5%; worst seen 30% (n = 33, chain from a circulant start).
Known failure mode: at n = 32 a chain started from C35 minus 3 vertices was trapped in a
different region and never reached e <= 107 (it gave a 150x too high total). Chains started
from the HoG minimum graphs agree with all published numbers. For n = 30 six chains from both
start types agree (sd of ln g = 0.02). Risk: a region that no chain visits would make the
true counts LARGER than the estimates.

**R(3,9;30,e) estimates** (6 chains, runs/gluing/mc_n30_*, mcB_n30_*):
| e | 87 | 88 | 89 | 90 | 91 | 92 | 93 | 94 | 95 | 96 | 97 | 98 | 99 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| count | 1.47e5 | 5.9e6 | 1.5e8 | 2.8e9 | 4.1e10 | 4.9e11 | 5.2e12 | 5.0e13 | 4.3e14 | 3.5e15 | 2.5e16 | 1.7e17 | 9.5e17 |
| cum <= e | 1.49e5 | 6.0e6 | 1.6e8 | 2.9e9 | 4.4e10 | 5.4e11 | 5.8e12 | 5.5e13 | 4.9e14 | 4.0e15 | 2.9e16 | 2.0e17 | 1.1e18 |
(Independent check: https://unsolvedlab.com/problems/ramsey-r310 (AI-agent lab web page, 2026-10-01, not peer
reviewed, no method details) gives a Wang–Landau estimate of 0.8–1.5e18 for R(3,9;30,99); we agree. The same page
says "about 3e13 core-hours for gluing at 40 vertices"; my estimate for the gluing step alone is ~8e11 core-hours
(9.5e17 x 3 ms); both are infeasible.)
R(3,9;31,e): 97: 1.0e6, 98: 1.9e7, 99: 2.4e8, 100: 2.4e9, 101: 1.8e10, 102: 1.2e11, <=108: 1.8e15.
R(3,9;32,e): 109: 1.4e7, 110: 7.4e7, 111: 3.1e8, 112: 1.1e9; above 112 the chains disagree (x3-x10).

## 3. Cost per input graph (measured, 1 core of this machine)

| step | program | cost per input |
|---|---|---|
| 9-regular: glue H in R(3,9;30,99) with d = 9, all degrees 9 | glue | 3 ms (482 MCMC samples, all 0 outputs) |
| non-regular: d = 9, MTF (deg 6..9), e(G) >= 161, H in R(3,9;30,88..99) | glue2 | 0.04–0.13 s (glue.c: > 3 s) |
| S8: d = 8, H in R(3,9;31,95), degrees 4..9, no edge bound | glue2 | 0.22 s |
| same 9-regular task by SAT: own CNF (independent 8-sets explicit, CEGAR), CaDiCaL via pysat | satglue.py | 65 ms |
| same by satcore (generic lazy propagator, --fix-nbhd 9, degree 9) | satcore | 20–40 s |
| generation R(3,8;24,<=58) -> R(3,9;31,<=96), d = 6 | glue | 0.35 s |
| generation R(3,8;23,<=51) -> R(3,9;31,<=96), d = 7 | glue | 1.3 s |
| [Ang] reference: R(3,8;24) -> R(3,9;32,<=112), and R(3,9;32) -> 41 vertices | Angeltveit's code | 4 ms each |
My generation code is ~100x slower than [Ang]'s; my d = 9 gluing is ~10-30x slower.

## 4. Cost per case (n = 40), using cases' Theorem A split

Generation inputs = cheapest increments t_d found by `topt.py` (LP-checked; exact check for
<= 87 by `tcheck.py`), with R(3,8) level counts from [GR] T13 + MCMC.
"opt" = at [Ang] speed (4 ms per input for both generation and gluing; generation of the
R(3,8) inputs themselves not included, it is of the same order for t <= 91).

| case | class | size | generation inputs (R(3,8)) | CPU time, opt | CPU time, my code |
|---|---|---|---|---|---|
| S8 | R(3,9;31,<=96) | 35,714 | 4.97e5 (24,<=58; 23,<=51) | ~1 h | ~150 h gen + 2 h glue (running) |
| N, t9 <= 87 | R(3,9;30,<=87) | 149,135 | 4.97e5 (24,<=58; 23,<=51; 22,42) | ~1 h | ~75 h gen + 4 h glue (running) |
| t9 <= 88 | R(3,9;30,<=88) | 6.0e6 | 1.1e7 (23,<=52 dominant) | ~1 day | ~3 months |
| t9 <= 89 | R(3,9;30,<=89) | 1.6e8 | 2.4e8 (23,<=53) | ~3 weeks | ~10 years |
| t9 <= 90 | R(3,9;30,<=90) | 2.9e9 | 4.4e9 (23,<=54; 24,<=60) | ~0.9 year | - |
| t9 <= 91 | R(3,9;30,<=91) | 4.4e10 | 5.4e9 (+ 24,<=61) | ~6 years | - |
| t9 <= 92 | R(3,9;30,<=92) | 5.4e11 | 7.9e10 | ~80 years | - |
| t9 <= 94 | R(3,9;30,<=94) | 5.5e13 | 1.7e13 | ~9000 years | - |
| R (9-regular) | R(3,9;30,99) | 9.5e17 | (> 1e15) | > 1e8 years | - |
Budget: 96 CPUs x 3 months ~ 24 CPU-years. So t9 <= 91 is the limit, and only with code at
L9 filter (critic G3: H-degrees 2..8, <= 9 vertices of H-degree 8) does not help: 472/472 MCMC samples of
R(3,9;30,99) pass it (min degree 4..6, 0..8 vertices of degree 8). Every sample also has 0 gluing outputs.
[Ang] speed (needs: [Ang]'s ordering trick, lazy alpha table, faster generation).

## 5. Runs and results (n = 40)

- Glue d = 8 of all 560 R(3,9;31,95)-graphs (HoG file; count = [GR] T14), degrees 4..9, no edge or
  MTF assumption: **0 outputs** (glue2, 121 s; runs/gluing/n40/S8_e95.*).
  Meaning: no (3,10;40)-graph has a degree-8 vertex v with e(G_v) = 95.
  No certificate (enumeration); correctness rests on glue2 (validated, Sec. 1) and the HoG file.
- Glue d = 9 of all 1800 R(3,9;30,86)-graphs (HoG file; count = [GR] T14), degrees 4..9, no edge or
  MTF assumption: **0 outputs** (glue2, 879 s; runs/gluing/n40/N_e86.*). Meaning: no (3,10;40)-graph has a
  degree-9 vertex v with e(G_v) = 86 (= e(3,9,30), so "<= 86").
  critic cross-check (own SAT gluer, no shared code): 200/200 random of the 1800 UNSAT (sample only).
- Generation of R(3,9;31,<=96) and R(3,9;30,<=87) (to be checked against 560+35,154 and
  1800+147,335), then glue: running, ETA 2026-10-25 ~16:00 (runs/gluing/gen/).

## 6. Hybrid gluing + SAT: what I tested

(a) Fix H = G_v, SAT finds the gluing (9-regular case). Works, but 20x (own CNF) to 10^4 x
(generic satcore) slower than the C gluer per H. No gain, and the number of H (9.5e17) is the
real problem.
(b) Fix less: X = G - N[u] - N[w] for non-adjacent u, w. alpha(X) <= 7, so X is in
R(3,8;|X|) with |X| = 38 - d(u) - d(w) + |N(u) ∩ N(w)| <= 27 (cases L6). In Exoo's
(3,10;39)-graph the largest X has 26 vertices (n = 39). Sub-case "|X| = 27": X is one of the
477,142 (3,8;27)-graphs (McKay file). satcore with X fixed and 13 free vertices: no answer in
180 s for one X (1M conflicts) -> > 2.7 CPU-years for this sub-case alone. A two-step gluing
(X -> H_u -> G) would be much faster (ms per step). So: when a big part is fixed, gluing beats
SAT; SAT should take the cases that cannot be enumerated.
(c) What SAT gets from gluing: after gluing a set U, every (3,10;40)-graph satisfies
"8-vertex => e(H_v) >= 97" (after S8) and "9-vertex => e(H_v) >= T+1" (after t9 <= T).
With e(H_v) = e - Z(v) these are linear cardinality constraints on the degrees of N(v); cases
already uses them in the LP (t9 tables); SAT teams can add them per distribution. They do not
touch the 9-regular case.
(d) Idea for later (not tested): split by m = max |X| over non-adjacent pairs. m = 27: X in
R(3,8;27) (477k, two-step gluing, cheap); m = 26: X in R(3,8;26) (~5e10 classes by MCMC, too
many); m <= 25: then |N(u) ∩ N(w)| <= d(u) + d(w) - 13 for all non-adjacent pairs, a strong
codegree constraint for SAT (satcore has --codeg-max). In the 9-regular case m <= 25 means
codegree <= 5.

## 7. Recommendation for the split

1. Gluing (agent gluing, CPUs 156-167): finish S8 and t9 <= 87 now (cheap; running). Then
   t9 = 88 (6e6 graphs; needs R(3,8;23,<=52), 1.07e7 graphs) after speeding up generation.
   t9 = 89..91 only if someone ports [Ang]'s optimisations (weeks of work, then months of CPU).
   Best "weeks-to-months" choice (cases' scan): U8 <= 99, U7 <= 112, U6 <= 121, T = 90:
   337/545 MTF distributions closed, 208 left (e >= 167). Note: the left-over near-regular
   distributions (t9 = 96..99 for e >= 168) never move for any U, so gluing helps SAT only if
   SAT is split per degree distribution.
2. SAT (satcore / sms / symsat): all distributions with t9 >= 92 (and >= 89 until gluing reaches
   them), plus the 9-regular case, with the constraints of Sec. 6(c), symmetry breaking, and
   (for 9-regular) codegree splits as in Sec. 6(d).
3. The 9-regular case is the bottleneck for every method. No gluing variant I found makes it
   feasible: the inputs number ~1e18, and fixing a smaller part (X in R(3,8;<=27)) leaves either
   too many classes or too hard SAT instances.

## 8. Open problems / risks

- MCMC counts can be too LOW if a region of graph space is never visited (seen at n = 32 with a
  bad start). Mitigation used: several start types, comparison with 20 published counts.
- Gluing results here have no proof certificates (like [GR] and [Ang]).
- My R(3,8) generation is ~100x slower than [Ang]; the cost table "opt" column assumes his speed.
- e(G) >= 161 [GR T5] and MTF are used only where stated; S8 and the e86 run use neither (only
  Delta <= 9 and delta >= 4), so they hold for every G (also for symsat's all-G split and 8-regular G).
- No public code of [GR] or [Ang] exists (tools, lead). Cross-check of my R(3,9;31,<=96): exact count
  560 + 35,154 per [GR] T14 and equality of the e = 95 part with the HoG file (labelg). A full
  independent rebuild with triangleramsey (MTF graphs + edge deletion) is too expensive: as a calibration,
  `triangleramsey 27 ramsey K8.mc write_all_ramseygraphs` (all 21,798 MTF (3,8;27)-graphs, [GR] Sec 3) did not
  finish in 30 CPU-min; MTF (3,9;31) is much larger, and edge deletion down to 96 edges comes on top.

## 8. B1 pair gluing (s = 2), 9-regular case: estimate (2026-10-25) - NEGATIVE
Non-adjacent u, w with codegree c: X = G - N[u] - N[w] in R(3,8;20+c), e(X) = 18 + 9c + f, f = e(N(u),N(w)).
Two-step gluing X -> H_u (glue w, d = 9-c) -> G (glue u, d = 9). Class sizes |R(3,8;20+c, e(3,8,20+c)+t)| from
MCMC (runs/gluing/mc38_n20..27.out; anchors [GR] T13 at t = 3/4; check at n = 20, 21: +20%, +7% one level up).
- Worst case (counting, gluing/src/b1worst.py): per u, sum over the 30 non-neighbours w of
  (t_w + c_w^2 + e(3,8,20+c_w)) = 1836 and sum c_w = 72. An adversary can make EVERY pair class >= 1e14.25
  (e.g. c in {2,3}, t ~ 10). So counting only guarantees some pair with class <= ~2e14: infeasible.
- Typical H (954 MCMC samples of R(3,9;30,99), gluing/src/b1pair.py): min over w of log10|class(X)|:
  min 7.5, q10 10.1, median 11.5, q90 12.6, max 13.5. Best types (c,t) = (2,7), (1,8), (2,8), (1,9), (3,7).
  Only 3.4% of H have some X with class <= 1e10 (0.2% for <= 1e8). So a "cheap X" split covers few H.
- Verdict: pair gluing is ~3 orders below R(3,9;30,99) (9.5e17) at worst, but still ~1e14 X x 2 steps:
  not feasible. Same conclusion as for seeds (Sec 6.3 of notes/cases.md).
- (critic, lit W1/A5) If a per-X SAT step is ever run (e.g. cases' R(6) with X from [Ang]): batch ~1000 X per
  formula with selector literals (Wesley 2606.17021 Sec 4.4, 50-100x), and extend in phases (propagate + short SAT,
  keep only SAT cases, add one vertex; AM Sec 7) instead of storing all extensions (my step 1 gave 1.7e8 H_0 / 10 X).

## 9. Final S8 and t9 <= 87 results (2026-10-26)
- glue2 d = 8 on all 35,154 R(3,9;31,96) graphs and d = 9 on all 147,335 R(3,9;30,87) graphs (own generation,
  per-e counts = [GR] T14, e = 95 / 86 levels = HoG files): 0 outputs (runs/gluing/final40.log).
- With Sec. 5: no (3,10;40)-graph has a degree-8 vertex v with e(G_v) <= 96 or a degree-9 vertex v with
  e(G_v) <= 87 (degrees 4..9, no MTF/edge assumption). Enumeration, no certificate.
- t9 <= 88: gluing/src/t9_88.sh running (R(3,8;23,<=52) and R(3,8;22,<=44) regenerated, = [GR] T13).
