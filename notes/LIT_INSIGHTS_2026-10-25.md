# Literature insights (desktop lead, 2026-10-25 web search)

1. Angeltveit-McKay, R(5,5) <= 46 (arXiv:2409.15709, v2 2025-09-01). Method: (a) an "excess" identity
   sum_v excess_v = 0 with degree-dependent thresholds and catalogues of extremal neighbourhood graphs; it forces
   SEVERAL vertices (not one) to have neighbourhoods in a small catalogue set E, and bounds how many; (b) glue PAIRS
   of pointed neighbourhood graphs along a shared edge (overlay G u_K H), each overlay decided by SAT in ~1 s, with
   part L1 of the remaining vertices fixed in stages; 12M overlaps -> 15,248 SAT -> 17 after phase 2; ~30 CPU-years.
   Paper: further progress "will need new theoretical insights".
   For us: our identity sum_v e(H_v) = 40e - sum d^2 is the analogue of their excess identity. Their extra step is
   forcing MANY vertices into small classes and then overlaying TWO of them. In near-regular distributions this may
   force >= m vertices with small e(H_v); then overlay H_u, H_v (non-adjacent u,v: common part is a (3,8)-graph on
   20+c vertices) and decide each overlay by SAT. Does not bite in the exactly 9-regular case (all e(H_v) = 99).
2. Li-Duggan-Bright-Ganesh, IJCAI 2025 (certified R(3,8), R(3,9); arXiv:2502.06055): R(3,9) by cube-and-conquer,
   2,486 cubes, ~26 h on 128 CPUs (~3,300 CPU-h), ~289 GiB proofs. Calibration point for our cube costs.
3. Wesley, R(K4-e, K7) = 28 (arXiv:2606.17021, 2026-06): SAT-heavy exact value; method not yet read (lit).
4. Yu, R(4,20) >= 252 (arXiv:2608.18169, 2026-08): cyclotomic circulants on prime order. Not usable for n = 40
   (circulants already excluded), but the "cyclotomic class subsets" idea may suit symmetric searches on other groups.
5. No 2025-2026 result changes R(3,10) (still 40 <= R(3,10) <= 41, DS1 rev 18).

## Deep read (critic, 2026-10-25): local PDFs data/papers/arxiv_2409.15709.pdf, arxiv_2606.17021.pdf

### W = Wesley, R(J4,K7) = 28 (arXiv:2606.17021v1, 2026-06-15). Laptop, CPU-days, plain Kissat, no proof certificates.
W1 (Sec 4.4) BATCHED SELECTOR CUBES. To kill 6,817,238 fixed dual neighbourhoods H, put 1000 graphs into ONE
   formula: selector s_H, clauses (-s_H v x_e) for e in E(H), (-s_H v -x_e) for non-edges, and (OR_H s_H).
   Batches = consecutive graphs in graph6 lex order. Mean 43.5 s per 1000 (82 h total) vs "a few seconds" each
   singly: ~50-100x less CPU. The solver shares learned clauses between similar graphs.
   FOR US: every "list x extension" step: cases R(6, f* <= 5) (1,765,856 X in R(3,8;26,75..77)), gluing S8 lists,
   symsat ext27 (H, involution) pairs, known39 extension. Order graphs so that neighbours in a batch share
   structure (canonical labelling + sort by graph6, or group by a common induced subgraph). One proof per batch
   also cuts certificate overhead (cake_lpr per batch, not per graph).
W2 (Sec 4.3, Lemma 8-9) Pick the split vertex to make the residual class small: prove that some vertex in the dual
   neighbourhood has high degree, then glue the two levels (H_w^+ is a matching, H_w^- in a small census).
   Analogue of our Lemma W / max-codegree choice; nothing new for triangle-free.
W3 (Sec 4.3) Time-limit pass first (5 min), then add lex symmetry breaking only on the hard leftovers (243
   instances: avg 229 s). Cheap workflow rule for cube batches.

### AM = Angeltveit-McKay, R(5,5) <= 46 (arXiv:2409.15709v2). ~30 CPU-years + 50 for an independent re-run.
A1 (Sec 4, Prop 5.3) Excess bookkeeping with CLASS WEIGHTS: write the identity as sum over v of
   (slack_v + 1) with per-degree thresholds; vertices whose (dual) neighbourhood lies in a small high-edge catalogue
   E_i lose at most w_i (5, 2, 1) of slack. Then sum of weights >= 46 forces MANY special vertices, and a small
   Ramsey argument on F[E] (the graph induced by the special vertices, itself a Ramsey graph with degree caps)
   forces an EDGE between two special vertices with specific class pairs. Only those class pairs are glued.
   FOR US: in near-regular cases our sum_v e(H_v) identity gives the same slack bookkeeping. F[E] is
   triangle-free with alpha <= 9, so m >= 10 special vertices force an edge u~w; for adjacent u,w the common
   non-neighbourhood V - N(u) - N(w) has 22 vertices and alpha <= 8 (glue H_u, H_w along it). Weighted classes
   (e.g. e(H_v) = 96, 97, 98 with weights 3, 2, 1) could shrink the cube set for Theorem A cases.
A2 (Sec 5, P_k) If a special vertex must have >= k special neighbours, you may pick WHICH edge to glue along:
   drop its k-1 hardest pointed graphs (heuristic difficulty). Cuts the most expensive gluings.
A3 (Sec 6) Grow outputs to a fixed size with extra vertices L1 chosen so that a vertex v of K reaches the minimum
   degree; then N(v)/dual of v must lie in a small class -> extra bottleneck; branch first on those variables.
A4 (Sec 7) Seed L1 by forced induced subgraphs from small censuses ("every R(5,4,13) graph contains two triangles
   sharing an edge"; R(5,4,14) contains B1 or B2). Same idea as cases Lemma T / duo J9 seed; for us forced
   induced subgraphs of R(3,k;m) for the leftover part L (e.g. via (3,7)/(3,8) censuses) are free cube literals.
A5 (Sec 7) Phased filter: propagate + short SAT (Glucose, 1 min) per overlap, keep SAT ones, add one more
   vertex, repeat: 12M overlaps -> 15,248 -> 17 -> 0. Do not enumerate all extensions; never store them.
A6 (Sec 3.2) Census of only the HIGH-edge part R(4,5,n,e >= e0) by gluing R(3,5,p) + R(4,4,q) with degree tuples
   arranged in a tree with a "dense first" vertex order (bottleneck at small k). For us: the low-edge part
   R(3,9;30,e <= t) / R(3,8;n,e <= e(3,8,n)+t) by the GR-style one-vertex gluing with the same tree order.
A7 Conclusion: "future improvements ... will need new theoretical insights" (Sec 8).
