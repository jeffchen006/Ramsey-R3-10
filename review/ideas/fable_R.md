# fable_R: ideas for Case R, c* in {3,4,5}, and the rest of R(6)

Scout: fable_R, 2026-11-21. No case is closed here. Labels: proved / plausible / speculative / measured.
Scratch: `scratch/ideas/fable_R/` (one script, `momlp.py`, 2 runs, < 10 CPU-s in total).

Starting point (my reading of sec3, sec8, lanes C and D). In R(3..5) no residue is tight: for a top
pair, e(X) = 18 + 9c + f is 2..14 edges above e(3,8,20+c), and Lemma H at s = 3..5 has slack. So an
R(7)-type "fixed X + colour packing" has no small X list. A cut must come from (i) rows that use
adjacency between outside vertices, not only counts, or (ii) a root that fixes more edges per key.
Notation: K = rooted kernel, X = V - V(K), M(x) = N(x) /\ V(K) (the mask), p_M = number of x with mask M.

---------------------------------------------------------------------------------------------------
## Idea 1. Intersecting-family rows for every mask LP (proved; cheap; all of R(3), R(4), R(5), N(e))

(a) Mechanism. Two outside vertices x, y with M(x) /\ M(y) != {} are non-adjacent (triangle-free).
Let I be independent in K and let F be a family of masks, each disjoint from I, pairwise intersecting.
Then I + {x : M(x) in F} is independent in G. Hence the row

    sum_{M in F} p_M  <=  9 - |I|                                              (IF)

Proof: pairwise intersecting masks give pairwise non-adjacent outside vertices; M /\ I = {} gives no
edge to I; alpha(G) <= 9. QED. The rows 2 (private) and 5/6 (stars) of
`ralph/lanes/C/proofs/edge_kernel_projection.md` are the case "F = star at one vertex z". New: F is
NOT a star. Smallest cases: the triangle {ab, ac, bc} plus all masks that contain two of a, b, c;
"all masks with at least 2 points in a 3-set"; "at least 3 points in a 5-set"; Fano-type families.
In the edge kernel, masks are subsets of A + B (two independent 8-sets), so a mask family
"M meets A in a_1 or a_2, and meets B in b_1" etc. gives many non-star intersecting families.
Use (IF) once for each maximal intersecting family (an independent set of the "disjointness graph"
of the masks); no fractional version is claimed.

(b) Target. Lane D transport LP on the 13 max12 forest keys and the 76 keys at max 13..16; the 110
min-root keys; the R(4) K3,4 family; lane C/G mask LPs in N(e).

(c) Why cost falls. The present LP rows see X only through sizes (Ramsey row) and stars. (IF) is the
first row family that uses alpha <= 9 on sets of outside vertices with different masks. For root
vertex v (K = N[v], I = N(v) - T) it gives, for every T in N(v):
"sum of p_M over an intersecting family of masks inside T <= |T|". Example |T| = 3 in max12 (all masks
have size 2 or 3): every two masks inside T intersect, so (number of outside vertices with mask
inside T) <= 3, against <= 5 from the Ramsey row (R(3,4) - 1 - 3). Estimate of gain: unknown; I expect
a factor 2..10 more LP-refuted keys or pins, not orders of magnitude alone (plausible). It costs
seconds per key, and each refutation stays an exact Farkas certificate.

(d) Calibration. (3,7,22) 6-regular, the 474 edge kernels of sec8: the 10 graphs must stay feasible
(soundness), and count kernels refuted by LP with/without (IF). Kill: no extra refuted kernel there
and none among D's 34 max12 "feasible" transport points.

(e) New vs. record. Rows 1-7 of C-001, D's TRANSPORT/MAX_ROOT rows and sec8 use stars, privates,
Ramsey sizes and residual degrees only; grep finds no non-star intersecting family row.

(f) Lane D (owner of the LP), lane C for the nonedge-rooted windows. Steps: 1. generate maximal
intersecting families among masks with p_M > 0 in the current feasible LP point (separation: a
maximum-weight independent set in the disjointness graph of the support, a tiny exact search);
2. add violated rows, iterate (cutting plane), keep integer Farkas output; 3. run the (3,7,22) control.

---------------------------------------------------------------------------------------------------
## Idea 2. Star design kernel for the max12 class of R(3) (proved structure; plausible gain)

(a) Mechanism. In D's max12 class every edge is in 12 squares and all non-edge codegrees are 2 or 3
(`ralph/lanes/D/MAX_ROOT.md`). Consequences (proved, 5 lines each):
 1. For every v: h2 = 18, h3 = 12 (h2 + h3 = 30, 2 h2 + 3 h3 = 72).
 2. For every edge vx: exactly 4 of the 8 other neighbours of v have codegree 3 with x
    (sum over a in N(v) - x of (c(a,x) - 1) = q(vx) = 12, each term 1 or 2). So the codegree-3 graph
    N3 is 12-regular and N3[N(v)] is 4-regular on 9 vertices, for every v.
 3. Star design at v: the 30 masks M(y) in N(v) are 18 pairs + 12 triples; each point of N(v) is in
    exactly 4 pair-masks and 4 triple-masks (8 = r + s and 12 = 2r + s); each pair of points is in
    1 or 2 masks; the pairs covered twice form the 4-regular graph of item 2.
 4. (IF) at v: each 3-set T has at most 3 masks inside it; each 4-set T has triple-masks inside T plus,
    per complementary pair-mask class {ab | cd}, the larger multiplicity, at most 4; etc.
 5. If the 12 triples cover each pair exactly once they are the affine plane AG(2,3) (unique), and
    then the pair-masks are a simple 4-regular graph on 9 points (16 such graphs).
So in max12 EVERY vertex carries a design from a finite catalogue D12, and the designs at the two ends
of an edge overlap in D's forest key (F is the trace of both designs on the other neighbourhood).

(b) Target. The 13 max12 forest keys (lane D). A star key fixes 9 + 72 = 81 edges and the type of all
30 outside vertices; an edge key fixes 17 + 12 = 29 edges and no outside type.

(c) Why cost falls. The remaining unknown is only H_v (99 edges on 30 typed vertices, degrees 7 for
pair-masks, 6 for triple-masks, edges only between disjoint masks). Number of possible edge slots:
pairs of disjoint masks only. For two pair-masks the chance of disjointness is 21/36, pair-triple
15/36... about half of the 435 slots are dead at once, and the 9 colour classes are independent 8-sets
that every independent set must respect: |I| + #{x in N(v): I avoids S_x} <= 9 becomes a clause on
typed vertices (eager, about 9 * C(22,..) short clauses, no lazy 45-literal clauses). I expect
|D12| between 1e3 and 1e6 before (IF) (labelled count / 9!, rough: 4-regular 12-triple systems
~1e11 labelled); the gain exists only if (IF) + the "adjacent stars must match" rule cut D12 to
<= 1e3 and each key then solves in minutes (speculative; the per-key hard tail of sec8 may stay).
Second use, cheap and sure: D12 rows are valid in D's LP for each of the 16 kernel vertices that has
its whole star inside K + masks (roots u, v): item 3 is a set of equalities on p_M that the LP
may not yet have (each root sees 4 codegree-3 partners among the other root's neighbours: D has this;
"each point in exactly 4 triple-masks and 4 pair-masks seen from u" in mask form: check).

(d) Calibration. Same class definition at (22,6): 6-regular (3,7,22), 10 graphs: take those with all
edges at the maximum square count (if any), list their star designs, check items 1-4 on them and on
the two (3,10,39)/Exoo-type regular controls D already uses (C16 controls). Then count |D12| exactly
(orderly generation of 12 triples + 4-regular pair multigraph, 9 points; minutes). Kill: |D12| after
(IF) > 1e5, or a D12 key with H_v-only SAT still times out at 1 h on 5 of 5 samples.

(e) New. sec8 reports N(0)-H_0 incidence cubing as 10x slower, but that was lookahead cubing of the
generic cube R, without the max12 regularity (items 1-3) and without (IF). The catalogue D12 and the
4-regular N3[N(v)] fact are not in MAX_ROOT.md / TRANSPORT.md.

(f) Lane D. Steps: 1. generate D12 with items 3-4 and count; 2. add item-3 equalities to the
transport LP at both roots and rerun the 13 forest keys; 3. only if |D12| <= 1e4: H_v-only CNF for
5 dispersed star keys, 600 CPU-s each, compare with the edge-key runs (28 CPU-s cap hits).

---------------------------------------------------------------------------------------------------
## Idea 3. Top-pair (non-edge) kernels with f-pattern for R(5) and R(4) (speculative gain, exact cover)

(a) Mechanism. Root at the Lemma-Mc pair (u,w), c = c*. K = {u,w} + C + A + B, |K| = 20 - c, and
F = G[A,B] has a perfect matching (Lemma F), d_F(a) = c(a,w) in 1..c*, d_F(b) = c(b,u) in 1..c*,
e(F) = f. Every graph of R(c*) completes one such K (proved: Lemma Mc + Lemma F). Catalogue = bipartite
graphs (9-c)+(9-c) with min degree >= 1, max degree <= min(c*, 9-c), a perfect matching, up to side
swap: at most 317 for c* = 5 (4x4 binary matrices up to row/column permutation), at most 5,624 for
c* = 4 (5x5), against 2,852,820 and 96,135 edge kernels. For c* = 3: 6x6 with max degree 3.
Mask facts at this root (proved): every x in X has |M(x)| >= 2 (Delta(X) <= 7 since alpha(X) <= 7),
M(x) meets A + C and B + C; N_X(z) for z in C is a MAXIMUM independent set of X (size 7);
pairwise overlap of two C-colours <= c* - 2; f = sum_a c(a,w); e(X) = 18 + 9c + f;
for independent triples {u,w,x}: t(u,w,x) >= c* + c(u,x) + c(w,x) - 12 (Lemma H, s = 3).
Extra split that is free: choose the c*-pair with the least f (f*), so every other c*-pair has f >= f*
(the R(6) branch rule of sec3, here used as a row, not as an X list).

(b) Target. R(5) and R(4): replace 2.85e6 + 9.6e4 edge keys by <= 6e3 pair keys.

(c) Why cost could fall. The count of keys falls by 2-4 orders. The cost per key is NOT known to
fall: sec8 has one probe of cube R(4) (7.5e8 CPU-s) and none finished for R(5), and a pair key is that
cube plus an f-pattern. The bet is that the mask LP is much stronger at this root than at an edge
root, because X has alpha <= 7 on 20 + c vertices (Ramsey rows with R(3,8-s) instead of R(3,9-s)),
C gives c* maximum independent sets of X, and (IF) applies with I = {u,w} + ...: for an intersecting
family F of masks, sum p_M <= 7. Example: all x whose mask contains a fixed z: star, <= 7 (known);
all x with >= 2 neighbours in a fixed 3-subset of C: <= 7 (new).

(d) Calibration. (3,7,22), 6-regular, 10 graphs, max codegree 5 there (sec8 control): pair kernels
are bipartite 1x1.. small; run pair-key LP + SMS and reproduce the 10 graphs; compare total CPU with
the 116 s of the 474 edge kernels. Second: 8-regular (3,9,35) with c* <= 4 (only C35): sec8 says 15
of 26 edge kernels time out at 1 h; do the top-pair keys of the same class (4x4.. patterns) refute by
LP or SAT in < 1 h? Kill: pair keys at (3,9,35) time out at the same rate as edge keys.

(e) New. sec8 has pair GLUING (enumerate X: >= 1e14, dead) and edge kernels; it has no catalogue of
(K, f-pattern) pair kernels with a mask LP. Lane C uses this root only for c = 6, 7.

(f) Lane D (K3,4 work in R(4) is stopped by the critic; this is a different root) or lane C after the
P2 join. Steps: 1. generate the catalogues (seconds) and the mask LP with rows 1-6 + (IF);
2. (3,9,35) control on 10 keys; 3. report LP-refuted fraction for c* = 5 (all <= 317 keys, 70 CPU-s each).

---------------------------------------------------------------------------------------------------
## Idea 4. Spectral identities for max12 (proved identities; trace LP measured feasible; SDP speculative)

(a) Mechanism. In max12: A^2 = 9I + 2 N2 + 3 N3 and I + A + N2 + N3 = J, so
N3 = A^2 + 2A - 7I - 2J and N2 = -A^2 - 3A + 6I + 3J are polynomials in A (proved). N3 is a 12-regular
graph and N2 an 18-regular graph, so every eigenvalue t != 9 of A has |(t+1)^2 - 8| <= 12 and
|8.25 - (t+1.5)^2| <= 18, i.e. -5.48 <= t <= 3.48 (proved). Moments are fixed: sum t = -9,
sum t^2 = 279, sum t^3 = -729, sum t^4 = 3879. tr(N3^3) >= 0 gives sum (t+1)^6 >= 24000 while
Cauchy gives only >= 23232: the spectrum is close to two values near 1.8 and -3.8 ("nearly strongly
regular"; a true SRG(40,9,0,mu) does not exist).

(b) Measured (scratch/ideas/fable_R/momlp.py, HiGHS, grid 0.004, all words in A, N2, N3 up to degree
12, 130 trace rows): FEASIBLE. So trace positivity alone is no cut. By-products (LP bounds, estimate
until redone in exact arithmetic): number of 5-cycles in [4320, 4508]; triangles of N3 in [0, 880];
triangles of N2 >= 93.

(c) What could still cut. Level-2: for each v the 40x40 matrices split by the partition
{v}, N(v), N2(v), N3(v) (Terwilliger-type blocks); positivity of the block matrices built from
A, N2, N3 restricted to these cells, with the known constants of Idea 2 (4-regular N3[N(v)], 4/4
split on every edge). This is an SDP of size ~ 20..60 without any enumeration (speculative; chance
of infeasibility low, maybe 5%; cost hours of one core). The class max13..16 has codegree-1 pairs and
N1, N2, N3 are not polynomials in A: there only S = N3 - N1 = A^2 + 2A - 7I - 2J is (entries in
{-1,0,1}, eigenvalues (t+1)^2 - 8 >= -8); weaker.

(d) Calibration. The analogous exact class at (22,6) or the known answer "no 8-regular (3,9,36)":
does the level-2 SDP refute a parameter class that is known empty? Kill: feasible on every known
empty regular class.

(e) New. No spectral or SDP argument in notes/, sec8, BOARD, CLAIMS (grep: none). The trace LP is
now a measured negative.

(f) Lane D or H, 1 core. Steps: 1. redo the trace LP in exact rationals and record the C5 range as a
redundant counter constraint for the max12 SAT runs; 2. write the level-2 SDP for max12;
3. run the calibration before any use.

---------------------------------------------------------------------------------------------------
## Idea 5. (IF) and the triple rule inside lane C's R(6) windows (proved rows; small expected gain)

For an isolated codegree-six pair (u,w): X has 26 vertices, alpha <= 7, six C-colours that are maximum
independent sets of X. For x in X, the triple {u,w,x} gives t(u,w,x) >= c(u,x) + c(w,x) - 6, i.e. the
number of C-neighbours of x is at least c(u,x) + c(w,x) - 6 (proved from Lemma H, s = 3, |X_S| <= 22).
With c(u,x) = |M(x) /\ (A + C)|: |M(x) /\ C| >= |M(x) /\ A| + |M(x) /\ B| + 2 |M(x) /\ C| - 6, so
|M(x) /\ A| + |M(x) /\ B| + |M(x) /\ C| <= 6: every x in X has at most 6 boundary neighbours, hence
deg_X(x) >= 3 (and = 3 forces |X_S| = 22: one of the 191 graphs; this is C-017's "degree-three
anchor"). New part: (IF) with I = {u,w}: any intersecting family of masks has total multiplicity
<= 7; with I = {u} + B' (B' in B): <= 8 - |B'| for masks avoiding B'. For the complementary join of
the marked H21 windows (critic directive C.1) these rows are necessary cross filters between the two
windows before any SAT: two window vertices with intersecting marks are non-adjacent in the join.
Calibration: C's C22 full-wing controls must pass. Kill: no drop in the 1,134 (12,12) pairs.
Lane C; steps: add the filter to `p2_cross_index.py` copy, rerun stage counts, compare.

---------------------------------------------------------------------------------------------------
## Not proposed (checked, no cut found in this session)
- Lemma H at s = 3, 4, 5 on forced sets in R(3..5): all rows have slack (e.g. independent triple:
  |X_S| = 10 + sum c - t <= 22 and g >= e(3,7,m) + 153 - 9m are far from tight for c <= 5).
- Delsarte/Johnson-scheme LP on the 40 blocks N(v): degree 1, 2 rows are the known identities.
- Shearer / occupancy lower bounds on alpha: 7.4 < 10 at d = 9, n = 40.

## Summary (5 lines)
1. (IF) rows, proved: an intersecting family of masks disjoint from an independent I in K has total multiplicity <= 9 - |I|; non-star families are new; add to D/C mask LPs by cutting planes (seconds per key).
2. max12 star design, proved: every vertex has 18 pair-masks + 12 triple-masks, each point in 4 + 4, N3[N(v)] 4-regular; gives new LP equalities and a typed vertex-rooted key that fixes 81 edges (gain plausible, count of designs not yet known).
3. Top-pair kernels (K, f-pattern) for R(5)/R(4): <= 317 and <= 5,624 keys against 2.85e6 and 9.6e4 edge kernels; per-key cost unknown, calibrate on 8-regular (3,9,35) (speculative).
4. Spectral: in max12 N2, N3 are polynomials in A, eigenvalues in [-5.48, 3.48], near two-valued; trace LP to degree 12 is FEASIBLE (measured, no cut); level-2 SDP is speculative.
5. R(6) rest: every x in X of an isolated c6 pair has <= 6 boundary neighbours (proved) and (IF) gives cross filters for C's window join; small gain expected. No case closed.
