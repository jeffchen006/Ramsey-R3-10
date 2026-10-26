# B1 data: counts of (3,8;n,e)-graphs with e <= e(3,8,n)+t (known39, 2026-10-25)

Sources: [GR] = Goedgebeur–Radziszowski, EJC 20(1) #P30 (2013), arXiv:1210.5826, Appendix Table 13
(local data/papers/arxiv_1210.5826.pdf); [Ang] = Angeltveit, EJC 32(4) #P4.30 (2025), Sec 3.2 (cumulative
counts; "d" = derived by me as [Ang] cumulative minus [GR] entries). "?" = not published.

## Count of (3,8;n, e(3,8,n)+t)-graphs (exact e, not cumulative)
| n | e(3,8,n) | t=0 | t=1 | t=2 | t=3 | t=4 | t=5 | t=6 | t=7 | t=8 | t=9 | t=10 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 20 | 30 | 3 | 60 | 1980 | 58649 | 1594047 | ? | ? | ? | ? | ? | ? |
| 21 | 35 | 1 | 20 | 950 | 35797 | 1079565 | ? | ? | ? | ? | ? | ? |
| 22 | 42 | 21 | 1521 | 72353 | 2331462 | ? | ? | ? | ? | ? | ? | ? |
| 23 | 49 | 102 | 8241 | 356041 | 10326716 | 228163616 d | ? | ? | ? | ? | ? | ? |
| 24 | 56 | 51 | 3419 | 129347 | 3288695 | 64233886 | t5+t6 = 14577633303 d | | ~1.5e11 [Ang] | ? | ? | ? |
| 25 | 65 | 396 | 21493 | 613285 | 11946369 | t4+t5 = 2108265427 d | | ? | ? | ? | ? | ? |
| 26 | 73 | 62 | 1625 | 23409 | 216151 | 1526296 | ? | ? | ? | ? | ? | ? |
| 27 | 85 | 4 | 92 | 1374 | 11915 | 52807 | 122419 | 151308 | 99332 | 33145 | 4746 | 0 |
(n = 19, e(3,8,19) = 25: 2, 37, 763, 16939, then ?.) [Ang] cumulative: R(3,8,26,e<=77) = 1 767 543 = sum of the
[GR] row (check OK); R(3,8,27) = 477 142 total (all e, 85..94).

## Local lists checked (data/graphs/)
- mckay/r38_27.g6.gz: all 477 142 (3,8,27)-graphs; edge distribution by countg = [GR] row 27 exactly;
  500 random graphs pass check_graph --k 8 --n 27.
- mckay/r37_21.g6.gz (downloaded 2026-10-25, users.cecs.anu.edu.au/~bdm/data/r37_21.g6.gz): all 1 118 436
  (3,7,21)-graphs; edge distribution 51..63 = [GR] Table 12 n=21 exactly; 500 random pass --k 7 --n 21.
- mckay/r37_22.g6: all 191 (3,7,22)-graphs, e 60..66 = [GR] Table 12; all pass.
- hog/Ramseygraphs_3_8_{19..27}_e*.g6: the t = 0 sets; counts = column t=0; all pass --k 8.
- Published complete (3,7,n) lists exist only for n = 21, 22 (McKay) and t = 0 (HoG, n = 16..22).
  Counts of (3,7;n,e) for n >= 16 are in [GR] Table 12.

## What is feasible to compute (estimate, not run)
- Per row, counts grow ~20-40x per extra edge. The "?" cells for t >= 4/5 are 1e8 .. 1e12 graphs each.
  t <= 10 for n = 20..26 is out of reach (n = 24, t = 7 alone is ~1.5e11 [Ang], ~6 CPU months of his work).
- Cheapest new cells: (19,29), (20,35), (21,40), (22,46), (26,78): ~1e5 .. 1e8 graphs each, by gluing on a
  maximum-degree vertex (G - N[v] is a (3,7)-graph) or SMS with an edge bound. Not started: I wait for
  cases/gluing to say which (n, e) cells they need.

## Estimate for cases: |R(3,8;26,e)|, e = 78..81 (2026-10-25, no enumeration)
Source: gluing's MCMC level ratios runs/gluing/mc38_n26.out (one seed, ~1e6 samples per level), combined with
gluing/src/combine.py anchored at the published e=77 count 1 526 296 ([GR] Table 13).
| e | t | estimate | check vs [GR] |
|---|---|---|---|
| 73 | 0 | 48 | 62 (-22%; small level, symmetric graphs) |
| 74 | 1 | 1536 | 1625 (-5%) |
| 75 | 2 | 22 710 | 23 409 (-3%) |
| 76 | 3 | 212 800 | 216 151 (-2%) |
| 78 | 5 | 1.0e7 | - |
| 79 | 6 | 6.5e7 | - |
| 80 | 7 | 3.6e8 | - |
| 81 | 8 | 1.5e9 | - |
Sum e = 78..81 ~ 1.9e9 (with e = 73..77: ~1.9e9). Error: about +-10% per level near the anchor, compounding
to perhaps +-25% at e = 81 (one seed only; the published levels agree within 5% for t = 1..3).
