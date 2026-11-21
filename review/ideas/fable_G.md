# fable_G: cross-cutting ideas (global bounds, construction side)

Scout: fable_G, 2026-11-21. Focus: global methods; what a (3,10,40)-graph must look like.
Files: `scratch/ideas/fable_G/` (`theta.py`, `excess.py`, `eager35.py`, logs).
Honest headline: I found **no** global method that cuts case R by orders of magnitude.
I found (a) proofs that the spectral / theta / SDP family cannot work, with numbers;
(b) one new root statistic with measured data (pair excess); (c) two cheap triage steps
that stop wasted CPU. No case is closed by this file.

Notation: case R = 9-regular. For non-adjacent u, w: C = N(u) ∩ N(w), c = |C|, A = N(u) − C,
B = N(w) − C, f = e(A,B), X = G − N[u] − N[w]. In R: |X| = 20 + c, e(X) = 18 + 9c + f.

---------------------------------------------------------------------------------------------

## Idea 1. Pair-excess root: split case R (and near-regular N(e)) by the minimum pair excess

**(a) Mechanism.** Define the excess of a non-adjacent pair:
eps(u,w) = e(X) − e(3,8,|X|) >= 0 (Lemma P). Let eps* = min over all non-adjacent pairs.

Fact 1 (proved; possibly known to lane C). In R, for a in A: N(a) ∩ N(w) is in B
(a has no neighbour in C, because C and A are both in N(u)). So d_F(a) = c(a,w) and
**f = sum over a in A of c(a,w) = sum over b in B of c(b,u)**.
Consequences in R(M) (all codegrees <= M): 9 − c <= f <= M(9 − c). This is stronger than
Lemma F (f <= (9−c)^2) when M < 9 − c. Example R(3): a codegree-3 pair has f <= 18, not 36,
so e(X) is in [51, 63] on 23 vertices.

Fact 2 (proved, arithmetic from Fact 1 and the e(3,8,n) table). In R,
eps = f − t_c with t_c = 8, 6, 4, 2, 2, 1, 4 for c = 1..7, and f = (9 − c) + s, where
s = sum over a in A of (c(a,w) − 1) >= 0 is the "cross surplus". So
eps = s + (0, 1, 2, 3, 2, 2, −2) for c = 1..7 (c = 7 forces s = 2: Lemma R7).
A codegree-1 pair with s = 0 has X in R(3,8;21,35): an extremal class.

Split: branch L_k = "some pair has eps <= k"; branch U_k = "every pair has eps >= k+1".
- L_k is a pair-gluing over R(3,8;20+c, e_min .. e_min+k). The root pair is the minimum, so all
  other pairs have eps >= eps(root) (a strong extra constraint for the glue, like Lemma W).
- U_k gives a new global row for every other lane: for every non-adjacent pair,
  s >= k + 1 − (0,1,2,3,2,2)_c. For k = 3: no codegree-1 pair has s <= 3, no codegree-2 pair
  has s <= 2, and so on.

**(b) Block.** Case R, all c* at once (not one R(M) at a time). It also applies to N(e) with the
general Lemma P formula. It does not close R alone: U_k stays open. It moves the root from
"max codegree" (classes ~1e14, sec8) to "min excess" (classes 1e3..1e9).

**(c) Why the cost can fall.** sec8 measured the pair classes on MCMC samples of R(3,9;30,99)
("cheapest pair class has median 10^11.5 graphs"). Those samples are random H, not real G.
My measurement on structured graphs (`excess.py`, 20 CPU-s):

| graph | min eps | where |
|---|---|---|
| C35(1,7,11,16), the unique (3,9,35), (3,7)-analogue | **0** | 35 codegree-1 pairs, X is extremal (3,7;18,30) |
| lane F seed n=40, e=178, I10=24 | 3 (c >= 1) | c = 1 (2 pairs), c = 6 (2 pairs) |
| lane F seed n=40, e=179, I10=24 | 3 (c >= 1) | c = 2 (2 pairs) |
| lane F (3,10,39) seed, e=171 | 4 | c = 2, 3 |

Typical eps in these graphs is 7..10; the minimum is 0..4. Class sizes at low excess are known
(Angeltveit, `notes/edge_tables.md` l.146): R(3,8;23,e<=53) = 2.4e8 (eps <= 4),
R(3,8;25,e<=70) = 2.1e9 (eps <= 5), R(3,8;24,e<=62) = 1.5e10 (eps <= 6). GR Table 13 has the
lists for eps <= 2..3 (sizes 1e3..1e6; lane must read exact counts). So L_3 costs about
1e6..1e8 pair glues, each with a min-root constraint. Basis for "orders of magnitude": 1e14 -> 1e8.
Label: **speculative** as a route to close R (U_k is still the whole problem);
**plausible** as a cheap certified lemma "every pair has eps >= 4" that all SAT lanes can use.

**(d) Calibration.** (i) 8-regular (3,9,35): run L_0 for the (3,7)-analogue. It must output
exactly C35 from the 35 extremal codegree-1 pairs; U_0 must be empty. Kill: C35 is lost, or
L_0 costs > 1 CPU-h. (ii) 6-regular (3,7,22): the 10 graphs must split correctly between L_k
and U_k for k = 0..3. (iii) Count how many of the 10 + 191 graphs lie in U_3. If most real
extremal graphs lie in U_3, the lemma has little value: kill.

**(e) New vs. sec8.** sec8 has pair gluing with the max-codegree root and R(6), f* <= 5 only.
New: the root is the minimum of eps over all pairs and all codegrees; Fact 1 (f as a codegree
sum, f <= M(9−c)); the measured min eps on C35 and on the near-miss seeds.

**(f) Lane C (owns pair windows); lane H for Fact 1 in Lean.** Steps: 1. Check Fact 1/2 and add
the row "f = sum c(a,w)" to the kernel encodings. 2. Run calibration (i), (ii). 3. Count
R(3,8;21,35..38), (22,42..45), (23,49..52) from GR lists and time 100 dispersed min-root glues.

---------------------------------------------------------------------------------------------

## Idea 2. Floor-closability triage for the 278 distributions (stop floors that cannot pay)

**(a) Mechanism.** Lanes G/B raise residue floors (H6 >= 120, H7 >= 108, H8 >= 97, H9 >= 88) and
re-run the class LP. For each open distribution n, compute the **critical floor set**:
the set of minimal vectors (U6,U7,U8,T9) for which the LP is infeasible, and the vector
"floors at their largest self-consistent value" (e(H_v) <= e − Z_min(v)). If the LP is feasible
even there, **no floor of any height closes n**. This is an LP per distribution and floor
vector: minutes in total.

**(b) Block.** N(e), 278 distributions. sec3 already shows one point of this surface:
sel = (121,112,99,90) leaves 200 + R. So at least about 200 of the 278 are probably
floor-immune. The triage gives the exact list.

**(c) Cost effect.** No speed-up of a proof. It removes work: the e88 gluing (4 days x 32 cores),
T* = 90 (0.9 CPU-year), the e108 census. If a floor closes <= 15 keys and the rest are immune,
the cores go to case R. Label: **plausible** (pure LP, the tools exist: `ralph/lanes/G/typed_lp.py`,
`scan_root_floor.py`).

**(d) Calibration.** The triage must mark the 85 round-5 cuts and G-010/G-012 cuts as closable
at their real floors, and must reproduce "sel leaves 200 + R". Kill: it disagrees with a
checked cut.

**(e) New.** t9(n) is the one-dimensional version. The joint critical surface and the
"immune" list are not in BOARD/CLAIMS.

**(f) Lane G.** Steps: 1. LP with all floors at the self-consistent maximum: list immune keys.
2. For the others: minimal floor vectors, sorted by census cost. 3. Post the list; the critic
moves cores from floors with no closable key.

---------------------------------------------------------------------------------------------

## Idea 3. Construction side: exact "extremal core + few vertices" families

**(a) Mechanism.** tau9(G) = least |W| such that G − W has no independent 9-set.
Lemma (proved): 5 <= tau9(G) <= 10 (R(3,9) = 36; W = N[v] works). tau9 = m means that G is an
induced (3,9;40−m)-graph plus m vertices. For m = 5 the core is the unique C35(1,7,11,16).
For m = 6, 7 the cores are (3,9;34), (3,9;33)-graphs; the known ones (HoG: (3,9,34,129),
(3,9,33,118)) are the natural seeds. Each seed gives one small exact SAT problem:
m new vertices, all independent sets of the core of size 10−m..8 as clauses (no lazy alpha).

**(b) Block.** Construction (lane F) and symmetry-free structure. Every algebraic construction
of the form "extend the extremal (3,9)-graph" is in these families.

**(c) Cost.** One formula per seed. For C35 + 5: 185 variables, 306,440 clauses
(independent k-sets of C35: 20,265 / 22,995 / 13,760 / 3,360 for k = 5..8).
Status of my run (`eager35.py`, CaDiCaL 1.5.3 via pysat, 1 core, no symmetry breaking):
**TIMEOUT at 13 min; no answer** (TIMEOUT is not UNSAT). No positive control was run.
Next: add the 210 automorphisms of C35 and the S_5 of the new vertices as symmetry breaking
(up to 210 x 120 fewer cases), or cube on the orbits of N(w_1).

**(d) Calibration.** Positive control: (3,9,35) = [C35 − 5 vertices] + 5 must be SAT, and
Exoo-39 − 1 vertex + 1 must be SAT (notes/known39.md has this control for 1 vertex).
Kill: a control fails.

**(e) New.** notes/algebra.md did circulant-38 + 2 and circulants on 44/45 minus vertices;
known39 did Exoo-39 + 1. C35 + 5 and the 34/33-vertex extremal cores were not run.
Lane F's result "local search near-miss score I10 = 24" carries no evidence: notes/anneal.md
shows SA stuck at 41 bad sets on (3,9,35), where a graph exists. So an isolated solution is
found only by exact structured families (this idea and lane E), not by more polishing.

**(f) Lane F.** Steps: 1. Positive controls. 2. C35 + 5 with symmetry breaking and a proof log.
3. HoG (3,9,34,129) + 6 and (3,9,33,118) + 7 (the latter needs |N(w) ∩ core| structure cubes).

---------------------------------------------------------------------------------------------

## Idea 4 (negative, proved). Spectral, Hoffman, Lovász-theta and SDP routes are closed

These were in my focus. I record the proofs so that no lane spends cores here.

**4.1 Moment bound (proved).** Let G be 9-regular, triangle-free, n = 40, eigenvalues
9 = l_1 >= ... >= l_40, tau = −l_40. Then sum_{i>=2} l_i = −9, sum l_i^2 = 279,
sum l_i^3 = −729 (no triangles). Put m_i = l_i + tau >= 0 for i >= 2. Cauchy-Schwarz:
(sum m^2)^2 <= (sum m)(sum m^3), with sum m = 39 tau − 9, sum m^2 = 279 − 18 tau + 39 tau^2,
sum m^3 = −729 + 837 tau − 27 tau^2 + 39 tau^3. This fails for tau < 4.0355 (`theta.py`).
**So every case-R graph has l_min <= −4.0355**, and its Hoffman bound 40 tau/(9 + tau) is
>= 12.38. The Hoffman bound can never certify alpha <= 9 in case R.
(At tau = 3 the check is by hand: 576^2 = 331,776 > 108 x 2592 = 279,936.)

**4.2 Theta is far from alpha on the real extremal graph (computed, exact LP for circulants).**
theta(C35(1,7,11,16)) = 12.41, Hoffman 12.50, alpha = 8. theta(C13(1,5)) = 5.18, alpha = 4.
So a "search for triangle-free G with theta(G) < 10" would miss the true extremal graphs,
and theta-based refutation has the wrong direction (theta bounds alpha from above; we need
alpha >= 10). Inertia and interlacing bounds have the same direction.

**4.3 Hankel/moment LP gives less than the existing LP.** The 3x3 Hankel condition on
(39, −9, 279, −729, 8 C4 − 441) gives C4 >= 504; sec8 already has C4 >= 540.
In R(3): E = A^2 + 2A − 7I − 2J has entries in {−1,0,1}, tr E^2 <= 1120; this allows spectra
near {1.83 (x25), −3.83 (x14)}: feasible, no cut.

**4.4 Analytic lower bounds on alpha.** Shearer 1991 gives 40 x 0.1963 = 7.85 (same value as
notes/duo.md); hard-core occupancy (Davies-Jenssen-Perkins-Roberts) gives less at d = 9.
Flag algebras: 10-vertex flags give R(3,10) <= 54 (SCOUT). All are >= 2 vertices of alpha away.

Verdict: **proved** for 4.1; **computed** for 4.2/4.3. No SDP or spectral job should start.
Lane H may put 4.1 in Lean (3 trace identities + Cauchy-Schwarz) if a paper needs it.

---------------------------------------------------------------------------------------------

## Idea 5 (speculative). 5-cycle root with a full partition

**(a) Mechanism.** In an MTF graph with edges inside H_v, every vertex is on a 5-cycle
(an edge yy' of H_v with x_i ~ y, x_j ~ y' gives v x_i y y' x_j). Number of 5-cycles through v:
sum over edges yy' of H_v of c(v,y) c(v,y'). For a 5-cycle Q = v_1..v_5 in R, each v_i has 7
neighbours outside Q; N_i ∩ N_{i+1} is empty; |N_i ∩ N_{i+2}| = c(v_i, v_{i+2}) − 1.
So |Q ∪ N(Q)| = 40 − sum of (diagonal codegree − 1). If all five diagonals have codegree 1,
V = Q + N_1 + ... + N_5 exactly: five independent 7-sets and a 5-cycle, and each
N_i + v_{i+2} and N_i + v_{i+3} is an independent 8-set. Root = the 5-cycle with the least
diagonal codegree sum D. The uncovered part has D − 5 vertices and alpha <= 9 − 2 = 7 is not
forced, so the gain is only the rigid 5 x 7 block structure for small D.

**(b)-(c) Block and cost.** Case R(3), R(4) (low codegrees make D small: D <= 15 in R(3)).
A kernel on 5 + 35 vertices fixes 40 − (D − 5) vertices at once, against 18 for an edge kernel.
I have no count of the block patterns; this is the risk. Label: **speculative**.

**(d) Calibration.** 8-regular (3,9,35): C35 has codegrees {1,2,4}; list its 5-cycles and D;
the 5-cycle kernel search must return C35 only. Kill: more than 1e6 kernels at n = 35.

**(e) New.** No 5-cycle root in sec8/BOARD (edge kernels, P3/P4 paths, max-square roots only).

**(f) Lane D.** Steps: 1. Prove min D bounds from the codegree counts (n1 <= 160, n3 = n1 + 240).
2. Enumerate the N_i-N_{i+1}, N_i-N_{i+2} bipartite patterns for D = 5 at n = 35.
3. Compare the SAT time of one 5-cycle kernel with one edge kernel on the same graph class.

---------------------------------------------------------------------------------------------

## Whole-strategy remarks (not ideas)

- The N(e) work is close to its ceiling: sel leaves 200 + R even with far higher floors.
  The 200 are near-regular and behave like case R. A method for R is the only real cut.
- In R, lanes C (R(6)) and D (R(3)) have roots; **R(4) and R(5) have no lane attack**
  (96,135 and 2,852,820 kernels). Idea 1 is the only item here that covers them.
- Construction: all remaining candidates are asymmetric or in lane E's open (p, f) cases.
  Near-miss scores are not evidence (Idea 3e).

## Summary (5 lines)

1. Pair-excess root (new, speculative/plausible): f = sum of cross codegrees (proved); eps = s + (0,1,2,3,2,2); C35 has min eps 0, near-miss 40-seeds have 3; split on min eps moves pair classes from ~1e14 to 1e6..1e9 and gives a global row "eps >= k+1".
2. Floor-closability triage (plausible, LP minutes): list which of the 278 distributions no residue floor can close (sel suggests ~200); stop floor censuses that cannot pay.
3. Exact core families tau9 = 5, 6, 7 (C35 + 5 and HoG 34/33 cores): tiny SAT problems; C35 + 5 encoded (306,440 clauses); my 13-min run without symmetry breaking timed out (open).
4. Proved negative: every case-R graph has l_min <= −4.0355, Hoffman >= 12.38; theta(C35) = 12.41 vs alpha 8; Shearer 7.85. No spectral/theta/SDP/flag route; start no such job.
5. 5-cycle root with 5 x 7 partition for R(3)/R(4) (speculative); R(4), R(5) have no lane attack; near-miss I10 scores are not evidence of existence.
