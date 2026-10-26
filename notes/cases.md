# Case split for a hypothetical (3,10,40)-graph

Author: agent `cases`. Date: 2026-10-24. Status: v2, CONFIRMED by `critic` (notes/critic.md Review 6 for v1, Review 9 for v2;
independent re-run matches in all 4 modes). S8 gluing may use MTF pruning only for the MTF split.
Code: `cases/degseq.py` (enumeration, LP checks), `cases/verify_certs.py` (re-checks LP
certificates), `cases/test_lp_on_graphs.py` (tests LP rows on real Ramsey graphs).
Output: `cases/out/degseq_{gr,gr_mtf,self}.json`, `cases/out/cases_{gr,gr_mtf}.csv`,
`cases/out/certs_*.json`. Logs: `runs/cases/degseq_*.log`.

## 0. Notation and cited numbers

G is a (3,10,40)-graph: 40 vertices, no triangle, alpha(G) <= 9. d(v) = degree,
n_d = number of vertices of degree d, e = e(G). N(v) = neighbours, N[v] = N(v) + v.
H_v = G - N[v] (39 - d(v) vertices). Z(v) = sum_{u in N(v)} d(u).
D = set of vertices of degree <= 8; w(u) = 9 - d(u); N = sum_u w(u) = 360 - 2e (the
"deficiency"); eps(v) = sum_{u in N(v)} w(u), so Z(v) = 9 d(v) - eps(v).

Numbers from the literature (reading confirmed by `lit`, see `notes/edge_tables.md`):

| quantity | value | source |
|---|---|---|
| e(3,9,m), m = 30..35 | 86, 95, 104, 118, 129, 140 | [GR] Tables 3, 4 |
| e(3,9,36) | infinite (R(3,9) = 36) | [GR] Table 4 |
| R(3,9,35) | one graph, 8-regular, 140 edges (C35(1,7,11,16)) | [GR] Thm 3 |
| R(3,8) = 28 | | McKay–Zhang 1992, cited in [GR] |
| e(3,10,40) >= 161 | lower bound | [GR] Table 5 (uses GR gluing runs) |
| \|R(3,9,31,95)\|, \|R(3,9,31,96)\| | 560, 35154 | [GR] Table 14 |
| \|R(3,9,30,86)\|, \|R(3,9,30,87)\| | 1800, 147335 | [GR] Table 14 |
| \|R(3,9,32,104..108)\| | 39, 952, 18598, 234681, 2104151 | [GR] Table 14 |
| \|R(3,9,32,<=112)\|, \|R(3,9,33,<=121)\|, \|R(3,9,34,<=130)\| | 1554928360, 14395, 5 | [Ang] Sec 3.3 |

[GR] = Goedgebeur–Radziszowski, EJC 20(1) #P30 (2013), arXiv:1210.5826.
[Ang] = Angeltveit, arXiv:2401.00392v2, EJC 32(4) #P4.30.

Dependency IDs (notes/DEPENDENCIES.md, owner lit): e(3,k,n) k=3..6 [D-E3], k=7 [D-E7],
k=8 [D-E8], k=9 [D-E9]; e(3,10,40) >= 161 [D-E10b]; [GR] Thm 3 [D-G1]; |R(3,8,27,85)| = 4
[D-C8e]; R(3,9;30..34,e) counts incl. [Ang] totals [D-C9a]..[D-C9e]; R(3,3..9) [D-R1];
McKay counts [D-G3], [D-G3b]; (RK) [D-E0b].

Where a statement uses e >= 161 it says "[uses GR161]". `degseq.py --self-e` repeats
everything with the self-proved bound e >= 159 (Lemma L5); results change very little.

## 1. Lemmas (all with hand proofs)

**L1 (degree range).** 4 <= d(v) <= 9 for every v.
*Proof.* N(v) is independent (a triangle otherwise), so d(v) <= alpha <= 9. If I is
independent in H_v then I + v is independent, so alpha(H_v) <= 8; H_v is triangle-free,
so |H_v| <= R(3,9) - 1 = 35, i.e. 39 - d(v) <= 35. QED

**L2 (edges of H_v).** e(H_v) = e - Z(v).
*Proof.* Deleting N[v] deletes exactly the edges with an end in N(v) (every edge at v
ends in N(v)). N(v) is independent, so each such edge has exactly one end in N(v) and is
counted once in sum_{u in N(v)} d(u). QED

**L3 (lower bound).** e(H_v) >= e(3,9,39-d(v)).
*Proof.* H_v is triangle-free with alpha(H_v) <= 8 (proof of L1) on 39-d(v) vertices. QED

**L3' (per-vertex Z bound).** Z(v) <= e - e(3,9,39-d(v)), and Z(v) is at least the sum of
the d(v) smallest degrees among the other 39 vertices. *Proof.* L2 + L3; the second part
is trivial. QED

**L4 (sum identity; GR inequality (4)).** sum_v Z(v) = sum_u d(u)^2, hence
sum_v e(H_v) = sum_v d(v)(20 - d(v)), and
sum_d n_d (d(20-d) - e(3,9,39-d)) >= 0, i.e.
13 n9 + n8 - 13 n7 - 34 n6 - 54 n5 - 76 n4 >= 0.
*Proof.* sum_v Z(v) = sum_v sum_{u ~ v} d(u) = sum_u d(u) * d(u). By L2,
sum_v e(H_v) = 40e - sum d^2 = 20 sum_v d(v) - sum_v d(v)^2. Apply L3 to each v. QED

**L5 (edge range).** 159 <= e <= 180; also e >= 161 [GR Table 5]. e is an integer, so N is
even. *Proof.* e <= 40*9/2 by L1. Let f(d) = d(20-d) - e(3,9,39-d) = (-76,-54,-34,-13,1,13)
for d = 4..9. Then f(d) <= 13 - 12(9-d) for each d (check: -76 <= -47, -54 <= -35,
-34 <= -23, -13 <= -11, 1 <= 1, 13 <= 13). By L4, 0 <= sum_d n_d f(d) <= 520 - 12N,
so N <= 43, N even gives N <= 42, e = 180 - N/2 >= 159. QED

**L6 (pair lemma).** If u, v are distinct and non-adjacent, then
|N(u) ∩ N(v)| <= d(u) + d(v) - 11. So d(u) + d(v) <= 10 implies u ~ v.
*Proof.* Let X = V - N[u] - N[v]. If I is independent in X, then I + u + v is independent,
so alpha(X) <= 7 and |X| <= R(3,8) - 1 = 27. |X| = 40 - (2 + d(u) + d(v) - c), c = common
neighbours. So 38 - d(u) - d(v) + c <= 27. QED
*Consequences (check_low_degree):* vertices of degree <= 5 are pairwise adjacent, so
n4 + n5 <= 2; a 4-vertex is adjacent to all other vertices of degree <= 6, so n4 >= 1
gives (n4 - 1) + n5 + n6 <= 4; n4 = 2 gives n6 = 0 (else triangle).

**L7 (degree-4 structure).** Let d(u) = 4, N(u) = {x1..x4}, d_i = d(x_i). Then
n9 = sum(d_i - 1) + #{i : d_i = 9}, n8 = 35 - sum(d_i - 1) + #{i : d_i = 8},
n_d = [d = 4] + #{i : d_i = d} for d <= 7, e = 140 + sum d_i, and d_i + d_j >= 12 (i != j).
*Proof.* H_u has 35 vertices, so it is the unique (3,9,35)-graph, which is 8-regular with
140 edges [GR Thm 3] (only "every (3,9,35)-graph is 8-regular" is used). A vertex y of H_u has d(y) = 8 + |N(y) ∩ N(u)| <= 9, so it has at
most one neighbour in N(u). The vertices of H_u with one such neighbour number
sum_i (d_i - 1) and have degree 9; the others have degree 8. e = e(H_u) + Z(u) by L2.
x_i, x_j are non-adjacent and their only common neighbour is u (the sets
N(x_i) - u are disjoint), so 1 <= d_i + d_j - 11 by L6. QED

**L7' (no degree-4 vertex; computer proof by `critic`).** delta(G) >= 5 for every
(3,10,40)-graph. Source: notes/critic.md Rev. 4-5 (own CNF from L7 setting with
H_u = C35(1,7,11,16), UNSAT, drat-trim + cake_lpr verified; premise [GR] Thm 3).
Not used by degseq.py in "all G" mode (it would remove the 49 distributions with n4 >= 1);
MTF mode has delta >= 6 anyway (M1).

**L8 (class LP).** Let C_i = class of degree-i vertices, m_ij = #edges between C_i and C_j
(i <= j), M_ij = m_ij for i != j and M_ii = 2 m_ii. Suppose every v in C_i has
e(H_v) >= L_i. Then the m_ij satisfy all rows of `build_lp`:
(a) sum_j M_ij = i n_i; (b) sum_j j M_ij <= n_i (e - L_i);
(c) for every class weight vector x >= 0 (integer):
    sum_{i<=j} x_i x_j m_ij <= floor((sum_i x_i n_i)^2 / 4);
(d) m_ij <= min(n_i min(i, n_j), n_j min(j, n_i)) (i != j), m_ii <= floor(n_i^2/4);
(e) m_ij = full count (n_i n_j or C(n_i,2)) if i + j <= 10;
(f) [MTF only] sum_j j M_ij >= n_i (i^2 - 11 i + 78).
*Proof.* (a) count edge ends. (b) sum_{v in C_i} Z(v) = sum_j j M_ij, and Z(v) = e - e(H_v)
<= e - L_i. (c) Weighted Mantel (Motzkin–Straus for clique number 2): for a triangle-free
graph and vertex weights x >= 0, sum_{uv in E} x_u x_v <= (sum x)^2/4. Proof: the maximum of
F(x) = sum_{uv in E} x_u x_v on the simplex is attained; if a maximiser has two
non-adjacent vertices a, b in its support, F is linear along x_a + x_b = const, so moving all
weight to one of them does not decrease F; repeat until the support is a clique, which has
<= 2 vertices, where F <= 1/4. Put class-constant weights; the left side is an integer.
(d) a vertex of C_i has at most min(i, n_j) neighbours in C_j; Mantel for C_i. (e) L6.
(f) Lemma M2. QED
An LP infeasibility is accepted only with an exact Farkas certificate: y >= 0 with
min_{0 <= m <= ub} y^T A m > y^T b (computed in fractions; `verify_farkas`). Any feasible m
has y^T A m <= y^T b, contradiction.

**Theorem A (averaging; main case lemma).** G has a vertex v with
(d(v) = 9 and e(H_v) <= 99) or (d(v) = 8 and e(H_v) <= 96).
If G is not 9-regular, G has a vertex v with
(d(v) = 9 and e(H_v) <= 98) or (d(v) = 8 and e(H_v) <= 96).
*Proof.* Let a_v = e(H_v) - d(v)(20 - d(v)). By L4, sum_v a_v = 0. For d <= 7,
d(20-d) = 91, 84, 75, 64 < e(3,9,39-d) = 104, 118, 129, 140, so a_v >= 13 for d(v) <= 7
(L3). Assume no vertex as in the second statement: then a_v >= 0 for 9-vertices and
a_v >= 1 for 8-vertices. So sum a_v >= #(vertices of degree <= 8) > 0 unless G is
9-regular; contradiction. If G is 9-regular, e(H_v) = 180 - 81 = 99 for all v. QED

**Theorem A' (Theorem A uses only (RK) = [GR] Thm 2; CONFIRMED by critic, Review 15).** Theorem A holds using only the
general bound (RK) e(3,k+1,n) >= 6n - 13k for all n, k ([GR] Thm 2, credited to
Radziszowski–Kreher [RK88, RK91]; whether its proof is computer-free: to be checked by `lit`).
*Proof.* The proof of Theorem A needs only e(H_v) > d(20-d) for d(v) <= 7, i.e.
e(3,9,39-d) > d(20-d). (RK) with k = 8: e(3,9,m) >= 6m - 104, so for d = 6, 5, 4, 3, 2, 1, 0
(m = 33..39): 94, 100, 106, 112, 118, 124, 130 > 84, 75, 64, 51, 36, 19, 0. (No R(3,9) needed:
m >= 36 is also covered.) For d = 7 (m = 32) (RK) gives only 88, so: let H be triangle-free on
32 vertices with alpha(H) <= 8. For each w, H - N[w] has alpha <= 7, so by (RK) with k = 7,
e(H) - Z_H(w) >= 6(31 - d_H(w)) - 91. Summing (L4 for H): 32 e(H) - sum d^2 >= sum (95 - 6d), i.e.
sum_w q(d_H(w)) >= 0 with q(d) = 22d - d^2 - 95 = 26 - (d - 11)^2. q is concave; if the average
degree is dbar then sum q <= 32 q(dbar), so q(dbar) >= 0; as dbar <= 8 (degrees <= alpha(H) <= 8), dbar >= 11 - sqrt(26) > 5.90,
sum d > 188.8, so sum d >= 190 (even), e(H) >= 95 > 91. QED
So the coarse split {R, S8, N(t9 = 98)} (Sec. 4) uses only (RK) = [GR] Thm 2 (no table of
exact values); whether the (RK) proof is computer-free is open (lit). Besides (RK) it needs only M0, M1 (MTF) or nothing (all G). The refined t9 values and the distribution lists do use
the tables e(3,9,30..35) and e(3,10,40) >= 161.

**Theorem A'' (exact base facts for the MTF coarse split; CONFIRMED by critic, Review 16).** `lit` found that (RK) is
NOT computer-free for k <= 7: its base (RK 1991, Ars Combin. 31, Prop 5.1.3(a)) checks the
computed values e(3,8,22..27), e(3,7,19..22). So write the dependence directly. For MTF G
(degrees 6..9, M1), Theorem A needs only e(3,9,32) > 91 and e(3,9,33) > 84, and these follow from
  F1: e(3,8,m) >= 6m - 91 for 23 <= m <= 27 (true values 49, 56, 65, 73, 85 >= 47, 53, 59, 65, 71), and
  F2: R(3,8) <= 28 (DRAT-certified by [DuLBG], see notes/step0_literature.md).
*Proof.* Let H be triangle-free on M in {32, 33} vertices with alpha(H) <= 8. For w in H,
H_w = H - N[w] has alpha <= 7 and M - 1 - d_H(w) vertices; d_H(w) <= 8, so |H_w| >= 23, and
|H_w| <= 27 by F2. By F1 and L2/L4 for H: M e(H) - sum d^2 >= sum_w (6(M - 1 - d) - 91). With
M e(H) = (M/2) sum d this is sum_w q_M(d_H(w)) >= 0, q_M(d) = (M/2 + 6) d - d^2 - (6M - 97),
concave. Jensen as in A': M = 32: dbar >= 11 - sqrt(26) > 5.90, e(H) >= 95 > 91;
M = 33: q_33(d) = 22.5 d - d^2 - 101, dbar >= 11.25 - sqrt(25.5625) > 6.19, e(H) > 102.2, so
e(H) >= 103 > 84. QED
F1 has slack 2..14 edges, so a SAT certificate ("no (3,8;m,<=6m-92)-graph", m = 23..27) should be
cheap (suggestion of `lit`; for `cert`).

**Theorem B (Angeltveit-type, no 30-vertex graphs).** If G is not 9-regular, some v in D has
e(H_v) <= 180 - 9 d(v), i.e. H_v in R(3,9,31,<=108), R(3,9,32,<=117), R(3,9,33,<=126),
R(3,9,34,<=135) or R(3,9,35) for d(v) = 8,7,6,5,4.
*Proof.* As [Ang] Prop 2.1: by L8(c) with x = w on D, sum_{v in D} w(v) eps(v) =
2 sum_{uv in E(D)} w(u)w(v) <= N^2/2, and sum_{v in D} w(v) = N, so some v in D has
eps(v) <= N/2. Then e(H_v) = e - 9d + eps(v) = 180 - N/2 - 9d + eps(v) <= 180 - 9d. QED
(Not useful in practice: these classes are far larger than in [Ang].)

**Theorem C (min degree 8, closed form).** Let all degrees be 8 or 9, n8 = N (even,
2 <= N <= 38 by L5 [uses GR161]). Suppose every 8-vertex has e(H_v) >= 97 - s, s in {0,2}
(s = 2 is no assumption; s = 0 holds after gluing R(3,9,31,<=96)). Put c = 11 + s. Then
some 9-vertex v has
e(H_v) <= 99 - N/2 + min(9, floor((8N - N max(0, N/2 - c)) / (40 - N))).
*Proof.* For an 8-vertex u, eps(u) = #8-neighbours, e(H_u) = 108 - N/2 + eps(u) >= 97 - s,
so eps(u) >= N/2 - c, and 2 m88 = sum_{u in C8} eps(u) >= N max(0, N/2 - c). For a 9-vertex
v, e(H_v) = 99 - N/2 + eps(v) and sum_{v in C9} eps(v) = m89 = 8N - 2 m88. The minimum
over the 40 - N nine-vertices is at most the average, and eps(v) <= 9 always. QED
The LP gives exactly the same values for every N (checked, see table in Sec. 3).

**L9 (9-regular case).** If G is 9-regular: e = 180, every H_v is in R(3,9,30,99); for
non-adjacent u, v: 1 <= |N(u) ∩ N(v)| <= 7; so every H_v has degrees in [2,8], every
vertex of H_v has 1..7 neighbours in N(v), sum_{y in H_v} |N(y) ∩ N(v)| = 72, and at most 9
vertices of H_v have degree 8 in H_v. The sets S_x = N(x) - v (x in N(v)) are 9 independent
8-sets of H_v. G is maximal triangle-free (M3), so diam(G) = 2.
*Proof.* e(H_v) = 180 - 9*9. Upper bound 7: L6. Lower bound 1: deg_{H_v}(y) = 9 - c(y,v)
and H_v is a (3,9)-graph, so deg_{H_v}(y) <= 8 (its neighbourhood is independent in H_v,
size <= alpha(H_v) <= 8). Sum: edges between N(v) and H_v = 9 * 8. At most 9: if y in H_v
has exactly one neighbour x in N(v), call y private to x; the private vertices of x
together with N(v) - x form an independent set, so 9 - 1 + #private(x) <= 9. QED

### Lemmas for maximal triangle-free (MTF) graphs

**M0 (MTF is lossless).** If a (3,10,40)-graph exists, an MTF (3,10,40)-graph exists.
*Proof* (from `lit`, source hraness/algal-lab review; checked here). Add edges one at a
time while no triangle appears; this stops. Adding edges never increases alpha. QED
All lemmas above hold for every (3,10,40)-graph, so also for MTF ones (e >= 161 too).
Do NOT combine MTF with arguments that assume e(G) is minimal.

**M1 (MTF: min degree 6).** In an MTF (3,10,40)-graph, d(v) >= 6.
*Proof.* Let d = d(v), A = N(v), H = H_v (39 - d vertices). MTF: every y in H is not
adjacent to v, so y and v have a common neighbour, which is in A. Let p = #{y in H with
exactly one neighbour in A}. Then e(A,H) >= 2(39 - d) - p. For x in A let P_x = vertices
of H whose only A-neighbour is x; P_x is independent (common neighbour x) and has no
neighbour in A - x, so P_x + (A - x) is independent: |P_x| <= 10 - d, p <= d(10 - d).
Also e(A,H) = Z(v) - d <= 8d. So 78 - 2d - d(10 - d) <= 8d, i.e. d(20 - d) >= 78:
false for every d <= 5 (d = 5 gives 75), so L1's lower bound is not needed. QED

**M2 (MTF: Z lower bound).** Z(v) >= d^2 - 11 d + 78 for d = d(v) (= 48, 50, 54, 60 for
d = 6..9). *Proof.* Z(v) = d + e(A,H) >= d + 2(39 - d) - d(10 - d) (proof of M1). QED
Corollary: an MTF G with a 6-vertex has e >= 118 + 48 = 166 (L3').

**M3.** A 9-regular (3,10,40)-graph is MTF. *Proof.* Adding an edge without a triangle
gives a triangle-free graph with alpha <= 9 and a vertex of degree 10, against L1. QED

### Scope: which statements need MTF

MTF is WLOG only for plain existence. It does NOT carry over to a search inside a class
with an assumed automorphism group (the MTF completion of a sigma-invariant graph need
not be sigma-invariant; remark by `symsat`). Use only the "all G" column there.

| holds for every (3,10,40)-graph | needs G maximal triangle-free |
|---|---|
| L1-L8, L3', L7' (delta >= 5), Theorems A, B, C | M1 (delta >= 6), M2 (Z(v) >= d^2-11d+78) |
| L9 incl. diameter 2 (9-regular G is MTF by M3) | the 545 / 573 distribution lists |
| e >= 161 [GR161], the 1897 / 1938 lists | "every vertex of H_v has a neighbour in N(v)" for non-regular G |
| t9 columns of cases_gr.csv | t9 columns of cases_gr_mtf.csv / cases_self_mtf.csv |

Vertex-transitive G: regular of degree d with e = 20d; e >= 161 [GR161] gives d = 9.
Without GR161, d = 8 (e = 160) is also possible; then every H_v is in R(3,9,31,96), i.e.
case S8, but only if S8 is glued WITHOUT the MTF assumption.

## 2. Degree distributions (cases/degseq.py)

Checks, in order (each a named function with its lemma): check_parity (L5),
check_edge_bounds (L5), check_mtf_min_degree (M1, MTF only), check_gr_sum (L4),
check_low_degree (L6), check_deg4_structure (L7), check_min_Z (L3', M2), check_class_lp (L8).

| mode | sum-40 tuples | survivors | removed by LP | csv |
|---|---|---|---|---|
| all G, e >= 161 [GR161] | 1,221,759 | **1897** | 47 | cases_gr.csv |
| all G, e >= 159 (self) | 1,221,759 | 1938 | 51 | (json only) |
| MTF G, e >= 161 [GR161] | 1,221,759 | **545** | 0 | cases_gr_mtf.csv |
| MTF G, e >= 159 (self) | 1,221,759 | 573 | 0 | cases_self_mtf.csv |

(v2, after critic K3: Mantel weights now also include every vector in {0..3}^classes; this
removes 18 more all-G distributions, matching critic's independent count of 47.)

K1 (table without GR161): with e >= 159 only, MTF gives 573 distributions = the 545 plus 28
with e in {159, 160}. After S8 gluing, 27 of the 28 are impossible; the last one,
(n7, n9) = (20, 20), e = 160, needs a 9-vertex with H_v in R(3,9,30,86) (1800 graphs) or
the "known" d = 7 gluing. The max t9 for every e >= 161 is the same as with GR161. So the
case table holds without GR161 if case N(t) also covers e = 159, 160 (t9 <= 86).

Ranges (all G, GR161): n4 <= 2, n5 <= 2, n6 <= 10, n7 <= 19, n8 <= 38, n9 >= 2.
MTF: n4 = n5 = 0, n6 <= 9 (and n6 >= 1 forces e >= 166), n7 <= 19, n9 >= 2.
Full lists: `cases/out/cases_gr.csv`, `cases/out/cases_gr_mtf.csv`.

Tests: `test_lp_on_graphs.py` evaluates every LP row on real graphs (Exoo's (3,10,39)-graph,
McKay's R(3,9,35)/R(3,8,27)/R(3,7,22) files, 3000 HoG (3,10,33,90)- and 2000 (3,10,30,66)-
graphs; the pair-lemma rows use the n-specific bound). 0 violations. All LP
certificates re-verify with `verify_certs.py` (v2: 7631 + 2176 + 7797 + 2286, 0 failed).

## 3. Gluing classes per case

For a set U of glued D-classes ("no G has a vertex v of degree d with H_v in
R(3,9,39-d, e <= U_d)"), t9(n, U) = least T such that "every 9-vertex has e(H_v) >= T + 1"
has an LP certificate (L8). So: some 9-vertex has H_v in R(3,9,30, e <= t9).
t9 = 85 means the distribution is impossible after the U-gluing.

Scenarios: none; U8 = {8: 96} (35,714 graphs); known = U8 + {7: 108, 6: 119, 5: 130, 4: 140}
(complete sets of [GR] T14); ang = U8 + {7: 112, 6: 121, 5: 130, 4: 140} ([Ang] censuses).

Maximum t9 over all distributions with given N (= 360 - 2e). (The "#dist (all)" column is
from v1, before K3 removed 18 all-G distributions; the max t9 values did not change in v2.)

| N | e | #dist (all) | t9 none | t9 U8 | t9 known | t9 ang | #dist (MTF) | MTF t9 U8 |
|---|---|---|---|---|---|---|---|---|
| 0 | 180 | 1 | 99 | 99 | 99 | 99 | 1 | 99 |
| 2 | 179 | 2 | 98 | 98 | 98 | 98 | 2 | 98 |
| 4 | 178 | 5 | 97 | 97 | 97 | 97 | 4 | 97 |
| 6 | 177 | 9 | 97 | 97 | 97 | 97 | 7 | 97 |
| 8 | 176 | 16 | 97 | 97 | 97 | 97 | 10 | 97 |
| 10 | 175 | 24 | 96 | 96 | 96 | 96 | 14 | 96 |
| 12 | 174 | 35 | 96 | 96 | 96 | 96 | 19 | 96 |
| 14 | 173 | 48 | 96 | 96 | 96 | 96 | 24 | 96 |
| 16 | 172 | 64 | 96 | 96 | 96 | 96 | 30 | 96 |
| 18 | 171 | 81 | 96 | 96 | 96 | 96 | 37 | 96 |
| 20 | 170 | 101 | 97 | 97 | 97 | 97 | 44 | 97 |
| 22 | 169 | 120 | 97 | 97 | 97 | 97 | 52 | 97 |
| 24 | 168 | 141 | 96 | 96 | 96 | 96 | 61 | 96 |
| 26 | 167 | 161 | 96 | 95 | 95 | 95 | 70 | 95 |
| 28 | 166 | 184 | 95 | 94 | 94 | 94 | 80 | 94 |
| 30 | 165 | 205 | 95 | 94 | 93 | 93 | 16 | 94 |
| 32 | 164 | 228 | 94 | 93 | 92 | 92 | 17 | 93 |
| 34 | 163 | 229 | 93 | 92 | 91 | 91 | 18 | 92 |
| 36 | 162 | 184 | 92 | 90 | 90 | 90 | 19 | 90 |
| 38 | 161 | 77 | 92 | 87 | 85 | 85 | 20 | 87 |

Number of MTF distributions by t9 (scenario U8): 85: 6, 86: 8, 87: 6, 88: 15, 89: 24,
90: 43, 91: 59, 92: 80, 93: 91, 94: 85, 95: 74, 96: 37, 97: 14, 98: 2, 99: 1 (9-regular).

Min degree 8 (Theorem C; LP agrees for every N): t9 (none / U8) = N=2: 98/98, 4-8: 97,
10-18: 96, 20-22: 97, 24: 96, 26: 95, 28: 94, 30: 93, 32: 92, 34: 91, 36: 90, 38: 89/85(killed).

## 4. Final case table (for gluing, satcore, symsat)

CAVEAT (symsat, confirmed by critic): "WLOG MTF" (M0, and with it M1, M2 and the 545 list)
is NOT valid for a search that also assumes an automorphism sigma, or any other condition
that adding edges can break: the MTF completion need not keep that condition. Such searches
must use the all-G list (1897 distributions, `cases/out/cases_gr.csv`) and its t9 values.
Theorem A, L6, delta >= 5 (L7') and e >= 161 stay valid there.

For plain existence: WLOG G is MTF (M0). Then G has one of the 545 distributions in `cases/out/cases_gr_mtf.csv`
[uses GR161], and at least one of these holds:

| case | statement | input class | size | difficulty |
|---|---|---|---|---|
| R | G 9-regular (n9 = 40) | every H_v in R(3,9,30,99); L9 structure | est. ~1e18 (lit, unverified web estimate) | very hard; SAT/symmetry, not gluing |
| S8 | some 8-vertex v, e(H_v) <= 96 | R(3,9,31,95..96), glue d = 8 | 35,714 [GR T14] | easy. Status (gluing, no MTF, Delta <= 9, delta >= 4): e = 95 part (560 graphs) 0 outputs; e = 96 part running |
| N(t) | otherwise: some 9-vertex v, e(H_v) <= t9_U8(n) | R(3,9,30, e <= t9) | 86: 1800, 87: 147335, 88..99 unknown | t9 in {86,87}: moderate (149k inputs; 14 MTF dists; 6 more are killed by S8 alone); t9 >= 88: hard to infeasible by gluing |

Preliminary size estimates for R(3,9,30,e) from `gluing` (MCMC, mixing not yet checked,
2026-10-24): e = 88: ~6e6, 90: ~3e9, 93: ~6e12, 96: ~4e15, 98: ~2e17, 99: ~1e18.

Gluing in case S8 may assume, together: G MTF, 6 <= delta, Delta <= 9, e(G) >= 161,
d(v) = 8; then every vertex of H_v has a neighbour in N(v), each x in N(v) has <= 2 private
vertices in H_v, and Z(v) >= max(54, 161 - e(H_v)) (M1, M2, L5).

Optional cheap extra gluing (scenario "known"/"ang": d = 7 with R(3,9,32,<=108) = 2.36M
graphs, d = 6 with R(3,9,33,<=119) = 74 graphs) makes 166 (known) / 296 (ang) of the 545 MTF
distributions impossible (t9 = 85), but does not lower t9 for N <= 24.

How to use per distribution n (SAT): fix vertex 0 with d(0) = 9 and N(0) = {1..9};
add "e(H_0) <= t9(n)" (equivalently Z(0) >= e - t9) and the degree counts n. For case S8
use d(0) = 8 and e(H_0) <= 96. Each SAT run covers one (n, case).

Not covered here (open): structural lemmas beyond degree counts for the near-regular cases
N <= 24 (t9 = 96..99), which hold most of the difficulty; a DRAT-checked kill of case S8.

## 4d. Core cubes for SAT (for `sms`; machine-readable: cases/out/core_cubes.json)

Common to all cubes: n = 40, triangle-free, alpha <= 9, MTF, degrees 6..9 (M1), optional
codeg(u,v) <= d(u) + d(v) - 11 for non-adjacent u, v (L6). Cube R: all degrees 9, N(0) = {1..9}
(then e(H_0) = 99). Cube N(e): e(G) = e, d(0) = 9, N(0) = {1..9}, T* + 1 <= e(H_0) <= t9max(e)
(equivalently e - t9max <= sum_{x in N(0)} d(x) <= e - T* - 1, since e(H_0) = e - Z(0)).

**Cover argument for N(e).** Let G be an MTF (3,10,40)-graph, not 9-regular, with e(G) = e.
If G has a d-vertex with H in a glued class (U_d, or a 9-vertex with e(H) <= T*), gluing
excludes G. Otherwise every d-vertex has e(H_v) >= U_d + 1 and every 9-vertex has e(H_v) >= T* + 1,
so the LP certificate for its distribution n (at T = t9(n)) gives a 9-vertex with
e(H_v) <= t9(n) <= t9max(e); relabel v as 0. Distributions with t9(n) <= T* are closed by the
gluing. Uses: e >= 161 [GR], e(3,9,30..35), the certificates.

t9max(e) (and #distributions) per scenario:

| e | none (no gluing) | U8+N86 (S8 + R(3,9,30,86)) | sel (U8<=99, U7<=112, U6<=121, T*=90) |
|---|---|---|---|
| 161 | 92 (20) | 87 (6) | closed |
| 162 | 92 (19) | 90 (19) | closed |
| 163 | 93 (18) | 92 (18) | closed |
| 164 | 94 (17) | 93 (17) | closed |
| 165 | 95 (16) | 94 (16) | closed |
| 166 | 95 (80) | 94 (80) | closed |
| 167 | 96 (70) | 95 (70) | 91 (1) |
| 168 | 96 (61) | 96 (61) | 93 (5) |
| 169 | 97 (52) | 97 (52) | 94 (10) |
| 170 | 97 (44) | 97 (44) | 95 (44) |
| 171 | 96 (37) | 96 (37) | 95 (37) |
| 172 | 96 (30) | 96 (30) | 96 (30) |
| 173 | 96 (24) | 96 (24) | 96 (24) |
| 174 | 96 (19) | 96 (19) | 96 (19) |
| 175 | 96 (14) | 96 (14) | 96 (14) |
| 176 | 97 (10) | 97 (10) | 97 (10) |
| 177 | 97 (7) | 97 (7) | 97 (7) |
| 178 | 97 (4) | 97 (4) | 97 (4) |
| 179 | 98 (2) | 98 (2) | 98 (2) |
| 180 | cube R | cube R | cube R |

Sec 4d CONFIRMED by critic (Review 21). Note (critic): the "U8+N86" column does not need
e >= 161: the extra MTF distributions with e = 159, 160 (K1) are closed by S8 and N86. In "none",
dropping e >= 161 needs extra cubes for e = 159, 160.
"none" needs no gluing; "U8+N86" needs S8 (running) + R(3,9,30,86) (done, lead); "sel" needs the
full gluing plan of notes/gluing.md Sec 7. T* = 85, 86, 90 respectively.

**Calibration cases (near threshold, k = 10, n = 40, expected UNSAT by gluing):**
C1: MTF, d(0) = 9, N(0) = {1..9}, e(H_0) <= 86 (gluing: 0 outputs from 1800 graphs, lead).
C2: MTF, d(0) = 8, N(0) = {1..8}, e(H_0) = 95 (gluing: 0 outputs from 560 graphs, lead).
C3 ladder: as C1 with e(H_0) <= 87, 88 (gluing can give ground truth: 1.5e5 and 6e6 inputs).
They are the hard-core cubes with a tighter e(H_0) bound, so SAT time vs bound measures how far
SAT is from N(e), and SAT vs gluing is an independent cross-check.

## 4c. Gluing results so far (from `gluing`; enumeration, NO certificate: leads per TEAM_RULES)

| glued class | degree of v | assumptions | outputs | log |
|---|---|---|---|---|
| R(3,9,31,95) (560 graphs) | 8 | Delta <= 9, delta >= 4 | 0 | notes/gluing.md |
| R(3,9,30,86) (1800 graphs = [GR] T14) | 9 | Delta <= 9, delta >= 4 | 0 | runs/gluing/n40/N_e86.* |

Effect on Sec. 3/4b: every distribution with t9 = 86 is closed by these runs (the LP at T >= 87
uses L9 = T + 1 >= 87, so other t9 values do not change). Example: scenario U8 (MTF) closes
8 more distributions (t9 = 86). These are leads until certified.

## 4b. Larger gluing sets (request of `gluing`; cases/t9_scan.py, cases/out/t9_scan_mtf.json)

MTF distributions (545), every scenario also glues U6: R(3,9,33,<=121) (14,395 graphs [Ang]),
U5 <= 130, U4 = 140 (empty for MTF). Number of distributions with t9 <= 90 / 91 / 92 (t9 = 85,
i.e. impossible after the U-gluing, counted in). All 43,727 certificates re-verified.

| U8 \ U7 | none | <= 108 | <= 110 | <= 112 |
|---|---|---|---|---|
| <= 96 | 267/282/317 | 296/311/342 | 310/324/356 | 326/345/377 |
| <= 97 | 282/295/329 | 305/320/349 | 315/329/362 | 327/347/377 |
| <= 98 | 293/302/342 | 315/329/361 | 323/340/373 | 333/353/385 |
| <= 99 | 303/320/355 | 323/339/373 | 329/348/385 | 337/360/395 |
| <= 100 | 310/332/373 | 328/346/388 | 336/356/398 | 342/368/408 |

With `gluing`'s MCMC size estimates (|R(3,9,30,<=90)| ~ 3e9, <=91 ~ 4e10, <=92 ~ 5e11;
|R(3,9,31,<=99)| ~ 2.6e8; |R(3,9,32,<=112)| = 1.55e9 [Ang]), the choice U8 <= 99, U7 <= 112,
T* = 90 costs ~5e9 inputs and closes 337 of 545 distributions; the other 208 have e >= 167
(one at 167, the rest 168..180) and stay for SAT. The near-regular tail never moves.

## 4a. FINAL cover statement for certified SAT (agreed with `cert`, 2026-10-24)

Vertices V = {0, ..., 39}. Phi = "triangle-free and alpha <= 9" (every 3-set has a non-edge,
every 10-set has an edge). MTF = "for all u != v: u ~ v, or some w is adjacent to both".
e(H_0) = number of edges with both ends in V - N[0].

| cube | constraints added to Phi |
|---|---|
| R  | d(x) = 9 for every x; N(0) = {1..9} |
| S8 | MTF; d(0) = 8; N(0) = {1..8}; e(H_0) <= 96 |
| N  | MTF; d(0) = 9; N(0) = {1..9}; e(H_0) <= 98 |

**Cover Lemma.** Assume F1 (e(3,8,m) >= 6m - 91 for 23 <= m <= 27) and F2 (R(3,8) <= 28).
If a (3,10,40)-graph exists, then some graph on V satisfies Phi and one of the cubes R, S8, N.
*Proof.* By M0 there is an MTF (3,10,40)-graph G. By M1 its degrees are in 6..9. If G is
9-regular, relabel any vertex as 0 and its neighbours as 1..9: cube R. Otherwise apply the
non-regular part of Theorem A, whose table input is only e(3,9,32) > 91 and e(3,9,33) > 84
(degrees 6..9), given by Theorem A'' from F1, F2. It gives v with (d(v) = 9, e(H_v) <= 98) or
(d(v) = 8, e(H_v) <= 96). Relabel v as 0 and N(v) as {1..d}. G is MTF: cube N or S8. QED
Notes. (1) Cube R needs no MTF clause; a 9-regular G is MTF anyway (M3), so adding MTF to R is
also valid. (2) Valid optional additions to every cube (consequences of Phi + MTF, or of the
cube): all degrees in 6..9 (M1; R: = 9); codeg(u,v) <= d(u) + d(v) - 11 for non-adjacent u, v
(L6, needs F2-type fact R(3,8) <= 28); in R, e(H_0) = 99. (3) Any symmetry breaking must fix
vertex 0 and the blocks N(0) and V - N[0] as sets (all cube constraints are invariant under such
permutations). (4) The refined per-distribution t9 table (Sec. 3) is NOT part of this
statement; it needs the e(3,9,30..35) table and e(3,10,40) >= 161.

## 6. Bold ideas B1/B2 (notes/BOLD_IDEAS.md): independent-set reductions and counting

Status 2026-10-25, v1, not yet reviewed by `critic`. Published inputs only (TEAM_RULES "Trust
published results"): [GR] Tables 3, 4, 13, 14; McKay data page counts |R(3,7,21)| = 1,118,436,
|R(3,7,22)| = 191, |R(3,6,16)| = 2576, |R(3,6,17)| = 7, |R(3,5,13)| = 1 (C13(1,5)), |R(3,4,8)| = 3.

(Sec 6 reviewed by `critic`: OK, notes/critic.md Review 22.)

### 6.1 B2 (double counting over independent sets): negative at the profile level
`cases/b2_profile_lp.py`: LP for case R (9-regular) with variables I_s (number of independent
s-sets) and p_s(m) (number of independent s-sets S with |X_S| = m). Rows: sum_m p_s(m) = I_s;
sum_m m p_s(m) = (s+1) I_{s+1} (each independent (s+1)-set T is counted once for each S = T - z);
sum_S I_2(X_S) = C(s+2,2) I_{s+2} with I_2(X_S) = C(m,2) - e(X_S) and
e(X_S) in [max(e(3,10-s,m), 9m + 9s - 180), min(m^2/4, m(9-s)/2, 9m + 9s - 180 + fmax)]
(9-regular identity e(X_S) = 9m + 9s - 180 + e(G[N(S)]), Lemma H); I_1..I_3 = 40, 600, 4480;
I_10 = 0; I_9 >= 40 (the 40 neighbourhoods N(v) are independent 9-sets and are distinct:
two vertices with N(u) = N(w) would be non-adjacent with codegree 9 > 7, against L6; gap noted by critic).
Result: FEASIBLE, with wide ranges (I_9 in [40, 18046], I_5 in [24064, 67110]). Still feasible
when tight sets are forbidden (caps 3:21, 4:16, 5:13, 6:8 together). So counting at this level
cannot kill case R, and cannot force tight sets. (Consistent with the known weakness of
counting bounds for R(3,k).) A finer LP (flag-algebra style, with codegree types) is not
tried yet.

### 6.2 Empirical: which S-types are tight in extremal graphs
`cases/tight_sets.py` on 60 graphs of known39/out/sample1000_39.g6 and Exoo's graph (n = 39):

| s | bound on \|X_S\| (R(3,10-s)-1) | max \|X_S\| seen | graphs with a tight set |
|---|---|---|---|
| 3 | 22 | 21 in 60/60 | 0/60 |
| 4 | 17 | 16 in 60/60 (17 once in 200, Sec cases_local) | 0/60 |
| 5 | 13 | 13 in 60/60 | 60/60 (about 65 tight sets per graph) |
| 6 | 8 | 8 in 60/60 | 60/60 (about 2900 per graph) |

### 6.3 Lemma T (seeds) and the B1 split
**Lemma T.** Let S be an independent s-set of G with |X_S| = m, and x in S. Then H_x contains
the induced subgraph X_S + (S - x): X_S plus s - 1 independent vertices with no edge to X_S.
This 'seed' has m + s - 1 vertices and independence number alpha(X_S) + s - 1 <= 8.
*Proof.* Vertices of S - x and of X_S are not adjacent to x and differ from x, so they lie in
H_x. S is independent, and no vertex of X_S is adjacent to S. QED

So, with A_s(m0) = "G has an independent s-set S with |X_S| >= m0", every G satisfies A_s(m0)
or its negation, and:
- A_s(m0): some vertex x (of degree 9 in case R) has H_x in R(3,9,30,99) containing a seed
  X + (s-1)K1 with X in R(3,10-s,m), m >= m0 (published complete lists). Gluing input =
  this seeded subclass, not all of R(3,9,30,99).
- not A_s(m0): every independent s-set has |N(S)| >= 41 - s - m0. A strengthened Lemma H for
  SAT (lazy check), e.g. not A_5(13): |N(S)| >= 23 for all independent 5-sets.

| type | X class (published) | seed size / alpha | extra edge facts (9-regular) |
|---|---|---|---|
| s=3, m=22 | R(3,7,22): 191 | 24 / 8 | e(X) = 45 + f, f = e(G[N(S)]) >= 15 |
| s=3, m=21 | R(3,7,21): 1,118,436 | 23 / 8 | e(X) = 36 + f >= 51, so f >= 15 |
| s=4, m=17 | R(3,6,17): 7 | 20 / 8 | e(X) = 9 + f >= 40 |
| s=4, m=16 | R(3,6,16): 2576 | 19 / 8 | e(X) = f >= 32 |
| s=5, m=13 | R(3,5,13): 1 (C13(1,5)) | 17 / 8 | e(X) = 26 = f - 18, so f = 44 |
| s=6, m=8 | R(3,4,8): 3 | 13 / 8 | e(X) = f - 54 >= 10, so f >= 64 |

RESULT (gluing, MCMC, 472 uniform samples of labelled R(3,9,30,99), 2026-10-25): seeded
subclasses are NOT small: seed X + 2K1 with X in R(3,7,21) occurs in 1.3% (~1e16 graphs);
seed C13(1,5) + 4K1 in 4% (~4e16). Typical H in R(3,9,30,99): max |X| for a pair 19-20, for a
4-set 12. So gluing from seeds is infeasible; the negations ("no such seed") remove 96-99% of
H_x and are useful only as SAT cuts, not as a split that saves work.

Interpretation. In every known extremal 39-graph the types (3,21), (4,16), (5,13), (6,8) occur.
If the same holds at n = 40 (CONJECTURE, not proved), then the case R reduces to gluing from
seeded subclasses of R(3,9,30,99) with a 23-vertex seed (type (3,21)): only 7 vertices of H_x
are free. Sizes of these subclasses are unknown; `gluing` can estimate them by MCMC.
The negations are valid extra SAT constraints and may make the complementary SAT cubes easy.

### 6.4 Published bounds re-check (lead item 1)
All published bounds that apply are already in the split: e(3,9,30..35) and e(3,8,.) ([GR]),
e(3,10,40) >= 161 ([GR] T5), the [GR]/[Ang] counts in the gluing scenarios. Pandey–Ravi
Lemma 3.1 (degree sums of two neighbours >= 12) is L6 with c >= 1; their Thm 3.6 (diam 2 =>
delta >= 6) is M1. Krüger's inequality gives only e >= 122. So no variant shrinks the hard core
beyond Sec 4b/4d: the smallest core is scenario "sel" (e >= 167, 208 distributions) + case R.

## 5. Lemma list (for `lean`)
Status 2026-10-24 (from `lean`): ALL of Sec 1 is proved in Lean 4 (no sorry, standard axioms),
map in lean/README.md. Table values enter as explicit hypotheses: R(3,9) <= 36, R(3,8) <= 28,
e(3,9,30..35), e(3,10,40) >= 161, "every (3,9,35)-graph is 8-regular". Sec 2-4 (enumeration,
LP certificates) not yet checked in Lean; `lean` plans a certificate checker.
Update (lean): Cover Lemma (Sec 4a) proved in Lean as R310.cover_lemma (lean/R310/Cover.lean),
hypotheses only F1, F2; also R310.Files.cover_files over cert's variables (lean/out/cube_*.opb).
Theorem A' is not formalized (superseded by A''). The MTF table is kernel-checked: caseTable_gr_mtf (545 list) and
t9_gr_mtf_<scenario>_main for none/U8/known/ang, from pinned outputs lean/data/cases_pin1
(hyps R(3,9) <= 36, R(3,8) <= 28, e(3,9,30..35), e >= 161). No errors found.
L1, L2, L3, L4, L5, L6, L7, L8(a-f) + weighted Mantel, Theorem A, Theorem B, Theorem C, L9,
M0, M1, M2, M3. Best first targets: L2, L4, Theorem A (pure counting), L6, M0, M1.

## 7. Excess forcing of several small vertices (lead task, AM R(5,5) idea; 2026-10-25, v1)
`cases/mforce.py` (out: cases/out/mforce_sel.json): profile ILP, x[d,p] = #d-vertices with neighbour-degree
multiset p; rows: class counts, edge consistency m_ij, e(H_v) = e - Z(p) >= L_d (scenario sel: 9: 91, 8: 100,
7: 113, 6: 122), M2, Mantel rows. Objective: min m_T = #9-vertices with e(H_v) <= T. Solver results (HiGHS
MILP), no exact certificates.
Result over the 374 MTF distributions with e >= 167 (non-regular):
- 200 are ILP-feasible. The 207 non-regular sel survivors include 7 that the profile ILP kills (uncertified):
  (n6,n7,n8,n9) = (0,9,4,27), (4,3,0,33), (5,1,1,33), (5,2,1,32), (6,0,0,34), (6,0,2,32), (6,1,0,33).
  CERTIFIED 2026-10-25: already the LP relaxation is infeasible; exact Farkas certificates (box form, fractions)
  cases/mforce_cert.py -> cases/out/mforce_certs.json, `--check`: 7/7 VERIFIED (scipy 1.15.3 HiGHS only to find y).
  CONDITIONAL on scenario sel (gluing T* = 90, U8 <= 99, U7 <= 112, U6 <= 121 done), like the 208 list itself.
  CONFIRMED by critic (Review 27).
- Forced small vertices: m_T = 0 for ALL 200 at T <= 90; at T = 91: 177/200 have m = 0; T = 93: 97/200;
  T = 96: 9/200; T = 98: min 8. So forcing gives several vertices only at e(H_v) >= 95..98
  (classes 4e14..2e17). NEGATIVE: no forced pairs in a gluing-feasible class (<= ~90).
gluing (reply 2026-10-25): pair overlay gives no gain over single gluing anyway; the bottleneck is generating
R(3,9;30,<=T). Case R: all e(H_v) = 99, forcing is empty.
