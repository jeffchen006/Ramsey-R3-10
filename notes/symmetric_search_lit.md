# (3,10)-graphs with symmetry: what is known

Author: lit. Date: 2026-10-24. Readers: symsat, algebra.
Two kinds of sources: (L) refereed literature / DS1; (W) unreviewed 2026 web reports by AI-agent
labs (hraness/algal-lab on GitHub; unsolvedlab.com). (W) items are leads to re-check, not results.

## 1. Literature (L)

### Circulant (cyclic) graphs — EXCLUDED at n = 39 and 40
- Harborth, Krause, "Ramsey numbers for circulant colorings", Congr. Numer. 161 (2003) 139-150 [HaKr1].
  Not downloaded (not online). Values via OEIS (entries by Backelin, citing [HaKr1]):
  - A000789(10) = 38: max order of a triangle-free circulant graph with alpha < 10 is **38**.
  - A267295(10) = RC_2(3,10) = 39: every triangle-free circulant on **>= 39** vertices has alpha >= 10.
  - A267296(10) = RC_1(3,10) = 37: some circulant orders below 38 also fail (37 fails).
  - Sequence A000789 (n = 2..12): 2,5,8,13,16,21,26,35,38,45,48. For n = 9: 35 = R(3,9)-1
    (the Kalbfleisch circulant C35(1,7,11,16)).
  So: no circulant (3,10,39) and no circulant (3,10,40). Consistent with DS1 rev 18 item 2.1.i:
  "no lower bound in Table Ia can be improved with a cyclic graph on less than 102 vertices,
  except possibly for R(3,k) for k >= 13".
- [HaKr2] "distance colorings" (slightly more general than circulant): DS1 2.1.i; not obtained.
- Larger cyclic heuristics for R(3,k): [JiLTX1, JiLTX2] (DS1 2.1.i, 2.2.g) — relevant only k >= 13 or so.
- Integer-programming circulant lower bounds: arXiv:2608.18769 (2026) — not read yet.

### Cayley / other group constructions
- DS1 2.2.d: some lower bounds come from Cayley colourings [Ex16] (Exoo), e.g. R(3,16) >= 82 on
  SmallGroup(81,5) (Exoo's web page). Nothing for (3,10) at n = 40 in the literature.
- No refereed paper (that I found) searches Cayley, vertex-transitive, block-circulant or
  prescribed-automorphism (3,10,40)-graphs.

### Exoo's (3,10,39) graph and the known 39-vertex family
- Exoo, SIAM J. Discrete Math. 2 (1989) 488-490 [Ex5]. Paywalled; method not in my sources.
  The graph (data/graphs/exoo/r3.10.39) has e = 167, degrees 6^1 8^14 9^24, so it is not
  vertex-transitive; |Aut| = 1 (confirmed by known39 with nauty).
- [GR] p.15: Exoo found "almost 300000" (3,10,39)-graphs; GR extended to > 4e7; [Ang] EJC: >= 43 225 483.
  [GR] slides: e from 161 to 175. No paper states the automorphism groups of this family.
- One-vertex extension 39 -> 40 of all known graphs fails ([GR] slides p.17; [Ang] Sec 6-7).
- Exoo, "On some small classical Ramsey numbers", EJC 20(1) #P68 (2013), doi 10.37236/3137 (found by anneal;
  local data/papers/exoo2013/exoo_v20i1p68.pdf). Sec "R(3,10)": "810 pairwise non-isomorphic colorings of K40
  with exactly one monochromatic triangle in color one and no monochromatic copies of K10 in color two"
  (= 40-vertex graphs, alpha <= 9, exactly one triangle). Data NOT public (anneal checked Exoo's site).
  Exoo generated "thousands" of (3,10,39)-graphs by simulated annealing; Goedgebeur's catalogue grew from them.
  Method (Sec 4, for R(3,11)): SA on edge colours, weights ~ inverse 3/2-power of clique size, K3 weight varied by
  a sawtooth 1..13 and reset to 1 at each new best. No public local-search code found (anneal).

### Useful facts for symmetry searches (L, easy)
- Delta <= 9, delta >= 40 - R(3,9) = 4 (any (3,10,40)-graph).
- A vertex-transitive (3,10,40)-graph is d-regular with 4 <= d <= 9 (max degree <= 3 gives alpha >= 10).
- MTF reduction (WLOG maximal triangle-free, then delta >= 6) is NOT compatible with an assumed
  automorphism group: saturating by edge orbits gives only an Aut-maximal graph, not an MTF one
  (point raised by symsat; correct). In symmetric searches use only delta >= 4 (or delta >= 5 if
  the degree-4 exclusion below is accepted).

## 2. Unreviewed 2026 web results (W)

### hraness/algal-lab (GitHub; research/spikes/moonshot-r310/; copies in data/papers/algal-lab/)
1. Vertex-transitive (vertex_transitive__README.md, 2026-09-28): all **1963 minimal transitive
   groups of degree 40** (TransGrp 3.6.5; count matches Holt–Royle arXiv:1811.09015 Tables 1-2:
   315 842 transitive groups, 1 963 minimal), all orbit unions with degrees 4..9:
   2 138 937 triangle-free unions (deg 4: 27 079; 5: 88 249; 6: 224 140; 7: 437 444; 8: 650 847;
   9: 711 178), each rejected with a replayed independent 10-set. C time 2.028 CPU s.
   Also all 4 minimal transitive actions of degree 39: 1 317 graphs, all alpha >= 10 (so no VT (3,10,39)).
2. Cayley: all groups of order 40 (Sylow-5 normal + order-8 complement; 28 semidirect presentations
   incl. duplicates), 9 034 972 triangle-free unions (deg 0..9), all rejected; no certificates kept.
   Subsumed by item 1. (symsat reports an independent Cayley exclusion on all 14 groups of order 40.)
3. Circulant: circulants.py (C40 check), consistent with [HaKr1].
4. Degree 4: LRAT-certified, no vertex of degree 4 in ANY (3,10,40)-graph (no symmetry assumed).
   Independently re-derived by our critic (own CNF, drat-trim + cake_lpr VERIFIED; notes/critic.md Rev. 4).
   Encoding: H = G - N[v] = C35(1,7,11,16); 4 disjoint independent sets S_i (|S_i| <= 6) with cover
   conditions on independent 6-, 7-, 8-sets of H; 140 vars, 98 965 clauses; checked by lrat-trim 0.2.0
   and two own checkers. Hand reduction: only size patterns (5,6,6,6), (6,6,6,6) survive (e = 167/168).

### unsolvedlab.com/problems/ramsey-r310 (page dated 2026-10-01; prime-order automorphisms)
Scheme: an automorphism sigma of prime order p with f fixed points and (40-f)/p p-cycles.
Any nontrivial automorphism group contains an element of prime order, so excluding all (p,f)
excludes every graph with nontrivial Aut. 60 classes; 29 claimed closed:

| p | (p, f) classes | #p-cycles = (40-f)/p | claimed closed | claimed open |
|---|----------------|----------------------|----------------|--------------|
| 11..37 | 14 classes | 1..3 | all 14 (Theorem A, hand proof; also DRAT) | — |
| 7 | f = 5, 12, 19, 26, 33 | 5, 4, 3, 2, 1 | all 5: f >= 12 by Theorem B, (7,5) by 30 DRAT certificates | — |
| 5 | f = 0, 5, ..., 35 | 8, 7, ..., 1 | f = 20, 25, 30, 35 (Theorem B: f <= 15) | f = 0, 5, 10, 15 (303 open cubes) |
| 3 | f = 1, 4, ..., 37 | 13, 12, ..., 1 | f = 28, 31, 34, 37 (Thm B: f <= 28 in text; (3,28) closed by 191 certified cases + "Lemma X") | f = 1, 4, ..., 25 (9 classes) |
| 2 | f = 0, 2, ..., 38 | 20, 19, ..., 1 | f = 36, 38 (Theorem B: f <= 34) | f = 0, 2, ..., 34 (18 classes) |

- Theorem A (check: correct, my reading): p >= 11 does not divide 40, so f >= 1; a fixed vertex
  adjacent to one vertex of a p-cycle is adjacent to all p > 9 of them, impossible; so no fixed-moved
  edges, G disconnected; but a disconnected (3,10)-graph has at most max over a+b = 9 of
  (R(3,a+1)-1)+(R(3,b+1)-1) = 1 + 35 = 36 < 40 vertices.
- Theorem B (claimed, hand proof, not seen): order 7 fixes exactly 5; order 5 fixes <= 15;
  order 3 fixes <= 28; involution fixes <= 34.
- Page inconsistencies: order-3 bound "at most 28" (Thm B) vs "at most 25" (summary); order-5
  certified cube counts 618 vs per-class sum 666.
- Their own note: closing the 4 open order-5 classes "would exclude every Cayley and every
  vertex-transitive (3,10)-graph on 40 vertices". Correct: a VT graph on 40 vertices has 40 | |Aut|,
  so (Cauchy) Aut has an element of order 5, which lies in some class (5,f); closing all eight
  order-5 classes excludes every graph with an order-5 automorphism, VT and Cayley included.
- "Pentagon blocks" (closest to block-circulant / Z5-lifts): rotation tier (incl. Z5-lifts of K8)
  UNSAT with verified proof; tier 2 (translation matchings) closed by 1 300 certificates; tier 3
  (arbitrary matchings, 23 415 live cubes) not run.

### Suggested use (for symsat / algebra)
- Cheap independent re-checks worth doing: VT census (1963 actions), Theorem A (trivial), Theorem B
  bounds (hand), class (7,5).
- Open territory: p = 5 with f in {0,5,10,15}; p = 3 with f <= 25; p = 2 with f <= 34;
  block-circulant / Z5-lift "tier 3"; and graphs with trivial Aut (the generic case — like Exoo's graph).
- Expect that symmetric 40-vertex graphs may simply not exist: the known 39-vertex record graph
  is (claimed) asymmetric, and circulants stop at 38 vertices.
