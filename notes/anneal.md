# anneal: local search for (3,10,40)-graphs

Agent: anneal. CPUs 72-87. Code: anneal/ls.cpp (C++17, `g++ -O3 -march=native`). Logs: runs/anneal/.
Status and running PIDs: notes/status/anneal.md.

## Method (anneal/ls.cpp)
- Graph = 64-bit adjacency bitsets. Objective f = wK*I10 + w9*I9 (+ wT*triangles) (+ wD*degree excess)
  (+ wX*edges above emax). I_k = number of independent k-sets.
- Exact incremental delta: toggling pair uv changes I_k by the number of independent (k-2)-sets in
  C(u,v) = V - N[u] - N[v]. Counted by bitset recursion (about 5 us per pair at n = 39).
  Full recount at the end of each cycle; it always agreed with the incremental counts.
- Triangles hard (default): "add uv" deletes one edge (random side) to each common neighbour first.
  Soft mode (wT > 0) allows triangles with a penalty.
- Moves: random pair flip; focused flip (pair inside a cached independent 10-set);
  vertex rewiring (VR): delete all edges at v, choose a new independent neighbourhood S, |S| <= 9,
  that hits the most independent 9-sets of G - v (exact branch and bound, node limit 2e5).
  VR is the one-vertex extension test used as a large-neighbourhood move.
- SA: geometric cooling T0 -> T1 (units of one bad set) per cycle of 5e5 moves; next cycle restarts
  from the best graph with 5% of pairs flipped. Also: tabu (best of a sampled neighbourhood),
  symmetric mode (flip whole pair orbits of Z_m acting on blocks of m vertices), grow mode
  (solve at n0, add a vertex by VR, repair, repeat to n).

## Calibration (one CPU each, AMD EPYC 9654; time to first solution)
| target | result |
|---|---|
| (3,8,27) | 0.13-0.17 s |
| (3,9,32) | 0.05-0.16 s |
| (3,9,33) | 4-16 s |
| (3,9,34) | not found in 120 s (16 settings) |
| (3,9,35) unique graph | general SA: no (stuck at 41 bad sets); circulant mode (17 orbits): 2-5 s |
| (3,10,37) | 0.2 s |
| (3,10,38) | 3-53 s; best setting about 6 s per solution (T 2 -> 0.2) |
| (3,10,39) | plain SA: 0 found in 16 x 900 s (best 2 bad sets). SA + VR (p = 0.001-0.002): 4 found in 9 x 900 s of these settings, at 270-680 s |

Findings from the grids on (3,10,38) (120 s per setting, solutions counted, fresh restart after each):
- Temperature matters most: T 2 -> 0.2 (or constant 1) is best; T <= 0.5 or >= 4 is 2-10x worse.
- w9 > 0 (penalise independent 9-sets) is worse (0 solutions vs 9-21).
- Soft triangles (wT = 16..128) are worse than hard triangles with repair moves.
- Hard degree cap 9 and soft degree penalty: no gain at n = 38; worse at n = 34.
- Tabu (best of 50-200 sampled moves): 1 solution in 120 s vs 18-21 for SA.
- Without a degree cap, SA likes degree-10 vertices (each costs only one bad set); near-miss
  39-vertex graphs have e = 172-178, a little denser than known (3,10,39)-graphs (161-175).
- VR: no gain at n = 38, but it is the only change that solved n = 39.
- Symmetric Z_13 and Z_3 at n = 39: best 39 and 12 bad sets in 900 s (no solution).

## Published local-search methods (web review 2026-10-24)
- Exoo, "On some small classical Ramsey numbers", EJC 20(1) #P68 (2013), doi 10.37236/3137,
  local copy data/papers/exoo2013/exoo_v20i1p68.pdf. Sec 4: SA with soft triangles, weight of a triangle
  about (k/3)^1.5 times a bad k-set; triangle weight follows a sawtooth 1..13 over time, reset to 1 at each new
  best (unweighted) count. This made 143447 (3,11,46)-graphs and "thousands" of (3,10,39)-graphs; Sec 2:
  810 colourings of K40 with exactly one triangle and no independent 10-set (data not on
  https://cs.indstate.edu/ge/RAMSEY/ as of 2026-10-24).
  Tested here (`-saw P -sawmin a -sawmax b`, soft triangles): on (3,10,38), 120 s, best 24 solutions
  (period 1e4, T 0.2) vs 42 for hard-triangle SA (T 2 -> 0.2); fixed weight 6 (no sawtooth): 0.
  n = 39 test (4 x 30 min, period 1e4, T 0.3-0.5, with VR p = 0.002): 1 (3,10,39)-graph in 2 CPU-hours,
  about the same rate as hard-triangle SA + VR (about 1 per 1.5 CPU-hours). Its near-misses have 0 independent
  10-sets and 1-3 triangles (like Exoo's one-triangle graphs). Used in one gen39 worker for diversity.
- Exoo–Tatarevic, EJC 22(3) #P3.11 (2015), arXiv:1504.02403v3, Sec 3: Method 1 = steepest descent + tabu list
  of the last L colourings, weights = moving averages of bad-subgraph counts (constant K = 10..100);
  Method 2 = SA over edges in bad subgraphs, for block-circulant colourings. My sampled tabu was 20x slower
  than SA on (3,10,38); not pursued further.
- Nagda–Raghavan–Thakurta (AlphaEvolve), arXiv:2603.09172v1, Algorithm 13 (R(3,10)): Paley(29) seed, add one
  vertex at a time (empty / complete / random neighbourhood), SA on #triangles + #I10. Reaches 40 (= known bound);
  no n = 40 graph. Their R(3,13) growth step picks the new vertex's neighbourhood as a hitting set of the
  independent 12-sets, then a short SA ("Mini-SA") per candidate: same idea as my grow mode with exact VR.
  Constructions: https://github.com/google-research/google-research/tree/master/ramsey_number_bounds/improved_bounds
  (no R(3,10) data).
- No public local-search code for R(3,k) found.

## (3,10,39)-graphs found
runs/anneal/g39/anneal39.g6 (all pass `tools/check_graph.py --k 10`). From random starts, not from Exoo's graph.
The file grows while the gen39 workers run. First one: e = 171, degrees 7..9, 3302 independent 9-sets.

## n = 40 runs
See notes/status/anneal.md for workers and modes. Best graph of each run: runs/anneal/near40.g6,
bad-set counts in runs/anneal/near40.txt (update: `python3 anneal/summ.py`).

| mode | start | best K (independent 10-sets) so far |
|---|---|---|
| rand9 | random triangle-free, max degree 9 | (see status) |
| rand8 | random triangle-free, max degree 8 | |
| vr005 | rand9 start, VR p = 0.005 | |
| f07 | rand9 start, focus 0.7 | |
| exoo | Exoo (3,10,39) + 1 vertex by VR | |
| a39 | own (3,10,39) + 1 vertex by VR | |
| grow | grow 38 -> 39 -> 40 | |

No (3,10,40)-graph found so far.
