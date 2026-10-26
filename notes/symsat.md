# symsat: exhaustive searches for (3,10,40)-graphs with assumed symmetry

Author: symsat. Started 2026-10-24. Status: IN PROGRESS (table below is updated as cases close).
Code: symsat/. Logs: runs/symsat/. CPUs 88-95,168-175.

Target: G on 40 vertices, triangle-free, alpha(G) <= 9 ("(3,10,40)-graph").

## 0. Facts used (all elementary or cited)
- F0. Outside facts: R(3,3..9) = 6, 9, 14, 18, 23, 28, 36 (DS1 rev 18, Table I; R(3,8) = 28
  McKay-Zhang 1992, R(3,9) = 36 Grinstead-Roberts 1982; R(3,8) and R(3,9) re-verified with DRAT
  proofs in [DuLBG], see notes/step0_literature.md). Used in F2, F3, F7.
  Search runs (not certificates) may also use delta >= 5 (critic, notes/critic.md Review 4,
  cake_lpr "s VERIFIED"); runs that do say "dmin 5".
- F1. Neighbourhoods are independent, so Delta <= 9.
- F2. delta >= 4: if deg v = d <= 3, G - N[v] has >= 36 vertices, is triangle-free with alpha <= 8;
  impossible as R(3,9) = 36 (Grinstead-Roberts 1982; DS1 rev 18 Table I). Used only as an
  implied constraint for propagation (it follows from alpha <= 9).
- F3. G is connected. If G = G1 + G2 (disjoint, nonempty) with alpha_i = alpha(G_i), then
  alpha_1 + alpha_2 <= 9 and |G_i| <= R(3, alpha_i + 1) - 1, so
  40 <= max_a [R(3,a+1) + R(3,10-a) - 2] over 1 <= a <= 8 = 36 (a = 1 or 8); contradiction.
  (R(3,2..9) = 2,3,6,9,14,18,23,28,36.)
- F4. No automorphism of prime order p >= 11. Let sigma have order p, fixed set F. A fixed vertex
  with a neighbour in a sigma-orbit of size p has >= p >= 11 > 9 neighbours (F1). So no edge joins
  F to the non-fixed vertices M. By F3, F or M is empty. M empty means sigma = id. F empty means
  p | 40, so p in {2, 5}. Hence p >= 11 is impossible.
  So only p in {2, 3, 5, 7} remain, with f = |F| = 40 mod p.
- F5. Lemma L (standard). If I is independent, then G - N[I] is triangle-free with alpha <= 9 - |I|,
  so |V - N[I]| <= R(3, 10-|I|) - 1.
- F6. Lemma T (twins). sigma of prime order p, F its fixed set, O a sigma-orbit of size p,
  A_O = N(O) cap F. A fixed vertex adjacent to one x in O is adjacent to all of O (apply sigma^i).
  So every x in O has N(x) cap F = A_O. If G[O] has an edge, A_O is empty (else a triangle).
- F7. Fixed-point bounds (symsat's proof; same numbers as the unreviewed "Theorem B" of
  unsolvedlab.com, see notes/symmetric_search_lit.md). Let f > 0. By F3 some edge joins F and M,
  so some orbit O has a = |A_O| >= 1; by F6, G[O] is independent (|O| = p).
  (i) Lemma L with I = O: V - N[O] contains F - A_O and M - O - N(O), and
      |N(O) cap M| <= p(9 - a) (each x in O has a fixed neighbours, degree <= 9). So
      40 - a - p(10 - a) <= R(3, 10-p) - 1.
  (ii) F - A_O is a subset of V - N[O], so f - a <= R(3, 10-p) - 1.
  | p | (i) gives | (ii) gives | f = 40 mod p allowed |
  |---|-----------|------------|----------------------|
  | 7 | 6a - 30 <= 5, a <= 5 | f <= 5 + a <= 10 | f = 5 only |
  | 5 | 4a - 10 <= 13, a <= 5 | f <= 13 + a <= 18 | f in {0, 5, 10, 15} |
  | 3 | 2a + 10 <= 22, a <= 6 | f <= 22 + a <= 28 | f in {1, 4, ..., 28} |
  | 2 | a + 20 <= 27, a <= 7 | f <= 27 + a <= 34 | f in {0, 2, ..., 34} |
  (For p = 5 and p = 2, f = 0 is allowed; f = 0 needs no bound.)
  So 33 cases (p, f) remain: 1 + 4 + 10 + 18.
- F9. Subcase split for f > 0 (used for p = 2 and p = 3 with few or many fixed points).
  Let a* = max over sigma-orbits O of |A_O|. By F3 and f > 0, a* >= 1, and by F6 an orbit O* with
  |A_O*| = a* is independent. By F7(i)/(ii), a* <= 7, 5, 6 for p = 2, 5, 3 (p = 7: 5) and
  f - a* <= R(3,10-p) - 1. Relabel (permute whole orbits and fixed points, which commutes with
  sigma): O* = orbit 0 = {0..p-1}, A_O* = the first a* fixed points. Subcase (p, f, a): orbit 0 is
  independent, N(orbit 0) cap F = A (|A| = a), every other orbit has <= a fixed neighbours.
  Subcases a = max(1, f - R(3,10-p) + 1) .. min(f, bound) cover the case (p, f).
  Symmetry breaking inside a subcase: lex-leader for rotations of every orbit, the multiplier
  (p odd), transpositions of orbits 1..k-1, transpositions inside A and inside F - A. These keep
  orbit 0, A and F - A setwise, so they map the subcase onto itself; lex-leader stays sound.
  verify_sc.py checks this property of every breaker and writes the subcase clauses itself.
- F10 (critic Review 25: CONFIRMED). Order-2 shortcut for subcase a = 7 (equality in F7(i)). Let p = 2, O = {x, x'} with
  |A_O| = 7, O independent (F6). Each of x, x' has 7 neighbours in A_O and <= 2 in M (deg <= 9).
  So |N[O]| <= 2 + 7 + 4 = 13 and |V - N[O]| >= 27. Lemma L (I = O): |V - N[O]| <= R(3,8) - 1 = 27.
  So equality holds everywhere: deg x = deg x' = 9, N(x) cap M and N(x') cap M are disjoint
  (2 + 2 vertices), and H = G - N[O] has exactly 27 vertices, is triangle-free with alpha(H) <= 7,
  i.e. H is a (3,8,27)-graph. N[O] is sigma-invariant, so sigma|H is an automorphism of H of
  order 1 or 2 with exactly f - 7 fixed points (F - A_O is in H; M cap H has no fixed points).
  Order 1 only if f - 7 = 27 (f = 34). The complete (3,8,27) list (477142 graphs, Sec 4) has
  involution types (2,1),(2,3),(2,5),(2,7),(2,9),(2,17) only. Hence subcase (2, f, 7) is EMPTY
  unless f - 7 in {1,3,5,7,9,17,27}, i.e. f in {8,10,12,14,16,24,34}.
  Closed by F10 (a = 7): f in {18,20,22,26,28,30,32}. For the 7 other f, the subcase reduces to:
  extend each (H, conjugacy class of involutions of type (2, f-7)) by 13 vertices
  (x, x', A_O, 2 + 2 M-neighbours) -- a small SAT problem per pair, H fixed.
  Result (ext27.py, 2026-10-25): all 2557 classes UNSAT (f=8: 2263, 10: 250, 12: 35, 14: 6, 16: 2,
  24: 1), ~45 CPU-min total. Certificates: 2557/2557 DRAT VERIFIED, 0 FAIL (ext27_verify.py;
  runs/symsat/ext27_verify.log + ext27_verify2.log, 2026-10-26). So (2,f,7) is open only for f = 34.
  Trust base: R(3,8) = 28 and completeness of McKay's (3,8,27) list; nauty Aut + autcycles.py
  for the involution types (each type of order 2 found by enumerating all group elements).
- F8. MTF (maximal triangle-free) reduction is NOT used: adding a single edge orbit to a
  sigma-invariant graph may create triangles, so "WLOG maximal" does not hold inside a symmetry class.

## 1. Cayley graphs (all 14 groups of order 40)

Groups. Sylow: n_5 | 8 and n_5 = 1 mod 5 give n_5 = 1, so every group of order 40 is
Z5 x|_phi P, |P| = 8, phi: P -> Aut(Z5) = Z4 (Schur-Zassenhaus). symsat/groups.py builds all
28 semidirect products (all 5 groups P of order 8, ALL homomorphisms phi, enumerated by brute
force), checks the group axioms, and sorts them into isomorphism classes by an explicit
isomorphism test (search over images of a generating set). Result: 14 classes, which matches
the known number of groups of order 40. The 14 classes also have pairwise different element-order
profiles (not needed for the argument; the isomorphism test is used). The searches run on the 14
representatives; completeness holds because each removed product maps to its representative by an
explicit isomorphism that groups.py checks to be a bijective homomorphism (critic Review 33).

| id | P | phi image | abelian | min alpha over triangle-free Cay(G,S) |
|----|---|-----------|---------|-----|
| G0 | Z8 | 1 | yes (Z40) | 10 |
| G1 | Z8 | Z4 | no | 11 |
| G2 | Z8 | Z2 | no | 10 |
| G3 | Z4xZ2 | 1 | yes | 10 |
| G4 | Z4xZ2 | Z4 | no | 10 |
| G5 | Z4xZ2 | Z2 | no | 10 |
| G6 | Z4xZ2 | Z2 | no | 10 |
| G7 | Z2^3 | 1 | yes | 10 |
| G8 | Z2^3 | Z2 | no | 10 |
| G9 | D4 | 1 | no | 10 |
| G10 | D4 | Z2 | no | 10 |
| G11 | D4 | Z2 | no | 10 |
| G12 | Q8 | 1 | no | 10 |
| G13 | Q8 | Z2 | no | 11 |

Search A (symsat/cayley.c): Cay(G,S), S = S^-1, e not in S, triangle-free iff S product-free.
|S| <= 9 (F1). alpha is non-increasing in S, so only S maximal (among product-free, symmetric,
|S| <= 9) are tested; exact alpha by branch and bound, using vertex-transitivity
(alpha = 1 + alpha(G - N[e])). Time < 2 s for all 14 groups. Log runs/symsat/cayley_all.log.
Search B (symsat/test_cayley_sat.py): orbit SAT + CEGAR (Section 3 method) with H = left
regular action of G. All 14: UNSAT, < 1 s each.
Both agree: NO (3,10,40)-graph is a Cayley graph. Circulants (G0) agree with Harborth-Krause.
Certificate: YES for all 14 (search B with --cert, no symmetry breaking, no degree clauses):
symsat/verify_cert.py rebuilds the CNF (own orbit computation, triangles, the logged
independent 10-sets, each checked), CaDiCaL 3.0.1 + drat-trim: 14/14 VERIFIED
(runs/symsat/cayley_verify.log; certificate JSON in symsat/certs/cayley_G*_K10.json).

## 2. Graphs with an automorphism of prime order p (orbit SAT)

Assumption for case (p, f): sigma in Aut(G), sigma of order p, with k = (40-f)/p cycles of
length p and f fixed points. Labelling: orbit i = {ip, ..., ip+p-1}, sigma(ip+j) = ip+(j+1 mod p),
fixed points kp..39. Any such G is isomorphic to one invariant under this sigma.

Encoding (symsat/orbsat.py, symsat/cyclic.py): one Boolean per <sigma>-orbit on vertex pairs.
Clauses: every vertex triple (projected, deduplicated); degree 4 <= d <= 9 per vertex orbit
(totalizer; implied, for propagation only); independent 10-sets by CEGAR (model -> exact
independent-set search -> clause "some pair of this 10-set is an edge"; each clause is implied by
alpha <= 9). Symmetry breaking: lex-leader x <=lex pi(x) for each generator pi of a subgroup of
the normalizer of <sigma>: rotate one orbit, swap adjacent orbits, multiplier j -> g j
(g primitive root mod p), swap adjacent fixed points. Sound because the full constraint set is
invariant under the normalizer.
Solvers: (a) CEGAR, CaDiCaL 1.9.5 via PySAT 1.9.dev17 (tools/venv), used for calibration;
(b) satcore (satcore/bin/satcore, agent satcore: CaDiCaL 3.0.1 + IPASIR-UP propagator, lazy
independent-set clauses with propagation) with --pairmap = orbit variables, used for n = 40;
(c) symsat/orbsolve.cpp (own IPASIR-UP propagator), spare second solver.
Option --sbfull (used for p = 2 small f): lex-leader for ALL orbit transpositions and all
fixed-point transpositions instead of adjacent ones.

Calibration (complete families from McKay's data, data/graphs/mckay; Aut via nauty 2.9.3,
symsat/autcycles.py): for (3,6,17), (3,7,22), (3,8,27), (3,9,35), every (p,f) case is run and
compared with the set of (p,f) types that occur in the known complete list. See Section 4.

Cases for n = 40: the 33 cases (p, f) left by F7. Search runs: satcore, degree 4..9 clauses,
lex-leader (generators), time limit 3600 s (runs/symsat/n40_satcore.jsonl). Certificate runs
(separate): satcore --proof, extra CNF = lex clauses written by the checker itself, NO degree
clauses; then symsat/verify_sc.py check (Section 3). Certificates in symsat/certs/n40/.

<!-- TABLE_N40 -->
| p | f | p-cycles | orbit vars | result | time (s) | solver | DRAT certificate |
|---|---|---|---|---|---|---|---|
| 7 | 5 | 5 | 120 | UNSAT | 6.81 | satcore | VERIFIED |
| 5 | 15 | 5 | 240 | UNSAT | 7.16 | satcore | VERIFIED |
| 5 | 10 | 6 | 192 | UNSAT | 46.16 | satcore | VERIFIED |
| 5 | 5 | 7 | 164 | UNSAT | 1321.55 | satcore | no |
| 5 | 0 | 8 | 156 | TIMEOUT | 3600.1 | satcore | no |
| 3 | 28 | 4 | 512 | UNSAT | 69.36 | satcore | VERIFIED |
| 3 | 25 | 5 | 460 | UNSAT | 110.1 | satcore | VERIFIED |
| 3 | 22 | 6 | 414 | UNSAT | 5.25 | satcore | VERIFIED |
| 3 | 19 | 7 | 374 | UNSAT | 14.8 | satcore | VERIFIED |
| 3 | 16 | 8 | 340 | UNSAT | 39.05 | satcore | VERIFIED |
| 3 | 13 | 9 | 312 | UNSAT | 75.29 | satcore | VERIFIED |
| 3 | 10 | 10 | 290 | TIMEOUT | 3600.14 | satcore | no |
| 3 | 7 | 11 | 274 | TIMEOUT | 3600.13 | satcore | no |
| 3 | 4 | 12 | 264 | TIMEOUT | 3600.12 | satcore | no |
| 3 | 1 | 13 | 260 | TIMEOUT | 3600.12 | satcore | no |
| 2 | 34 | 3 |  | OPEN (running or queued) |  |  | no |
| 2 | 32 | 4 |  | OPEN (running or queued) |  |  | no |
| 2 | 30 | 5 |  | OPEN (running or queued) |  |  | no |
| 2 | 28 | 6 |  | OPEN (running or queued) |  |  | no |
| 2 | 26 | 7 |  | OPEN (running or queued) |  |  | no |
| 2 | 24 | 8 |  | OPEN (running or queued) |  |  | no |
| 2 | 22 | 9 |  | OPEN (running or queued) |  |  | no |
| 2 | 20 | 10 |  | OPEN (running or queued) |  |  | no |
| 2 | 18 | 11 |  | OPEN (running or queued) |  |  | no |
| 2 | 16 | 12 |  | OPEN (running or queued) |  |  | no |
| 2 | 14 | 13 |  | OPEN (running or queued) |  |  | no |
| 2 | 12 | 14 |  | OPEN (running or queued) |  |  | no |
| 2 | 10 | 15 |  | OPEN (running or queued) |  |  | no |
| 2 | 8 | 16 |  | OPEN (running or queued) |  |  | no |
| 2 | 6 | 17 |  | OPEN (running or queued) |  |  | no |
| 2 | 4 | 18 |  | OPEN (running or queued) |  |  | no |
| 2 | 2 | 19 |  | OPEN (running or queued) |  |  | no |
| 2 | 0 | 20 |  | OPEN (running or queued) |  |  | no |
<!-- /TABLE_N40 -->

## 3. Certificates
- verify_cert.py (for PySAT CEGAR runs): rebuilds the CNF independently of orbsat.py (own orbit
  computation, own lex-leader encoding, triangle clauses, the logged independent 10-sets, each
  checked), then CaDiCaL 3.0.1 with DRAT and drat-trim.
- verify_sc.py (for satcore runs): own orbit variables (union-find, numbered by least pair; the
  pair map given to satcore must agree pair by pair); writes the lex-leader CNF itself; then checks
  that EVERY clause of satcore's PREFIX.full.cnf is a triangle clause, one of its own lex clauses,
  or an all-positive clause equal to the pair variables of a logged 10-set (or containing those of
  some 10-set, found by search); then drat-trim on full.cnf + DRAT. Negative test: one literal
  removed from one lazy clause -> rejected.
- Trust base of a VERIFIED case: drat-trim; verify_sc.py (~200 lines); the lex-leader soundness
  argument (Section 2); the orbit-structure reduction (Section 2, first paragraph).
  NOT in the trust base: orbsat.py, cyclic.py, satcore's propagator, the degree clauses.

## 4. Calibration results
Complete families (McKay data, data/graphs/mckay): (3,6,17) 7 graphs, (3,7,22) 191, (3,8,27) 477142,
(3,9,35) 1 graph. (p,f) types present (nauty + symsat/autcycles.py, all group elements enumerated):
- 17: (2,1),(2,3),(2,9).  22: (2,0),(2,2),(2,6),(2,8),(5,2),(11,0).
- 27: (2,1),(2,3),(2,5),(2,7),(2,9),(2,17).  35 (|Aut| = 210): (2,1),(3,5),(5,0),(7,0).
Runs: every prime p <= n, every f = n mod p, f <= n-p; 139 cases; no degree lower bound.
- PySAT CEGAR (900 s): 114 decided, 0 mismatches; 25 timeouts (runs/symsat/calib.jsonl).
- satcore on the 25 (900 s): 17 more decided, 0 mismatches (incl. (35: 3,5) SAT in 1.6 s);
  8 timeouts, all p = 2 at n = 35, f in {1,3,5,7,9,11,19,21} (runs/symsat/calib2_satcore.jsonl).
- satcore --sbfull (900 s): (35: 2,11) UNSAT 352 s; (35: 2,1), (2,3), (2,5) time out at 900 s.
- satcore --sbfull (4 h limit): (35: 2,1) SAT in 1236 s (the unique (3,9,35)-graph, |Aut| = 210).
- Every SAT model passes tools/check_graph.py.
So: 0 wrong answers in 133 decided calibration cases, and EVERY (p,f) type present in the four
complete families is recovered as SAT. p = 2 with few fixed points is slow (20 min at n = 35).
- Checker's own lex clauses (cert mode, extra CNF = verify_sc.py lex only), positive control at
  n = 35, K = 9: (7,0) SAT 0.2 s, (3,5) SAT 11 s, (5,0) SAT 6.6 s, all pass check_graph
  (runs/symsat/lex_poscontrol.log). (critic RISK S3)
- Known (3,10,39)-graphs with an involution (857 graphs from known39's closure of Exoo's graph,
  runs/known39/bfs_exoo; types (2,1) x835 and (2,3) x22): positive control (39: 2,1), (39: 2,3)
  running.
