# Local constraints for the near-regular core (n = 40)

Author: agent `cases`. Date: 2026-10-24. Status: v1 reviewed by `critic`: OK (notes/critic.md Review 13; R7 encoding complete, positive control SAT).
Context: notes/cases.md. After Theorem A and the S8 gluing, the hard core is the
near-regular graphs (e >= 168, some 9-vertex with H_v in R(3,9,30,e <= 96..99)) and the
9-regular case. Gluing estimates |R(3,9,30,99)| ~ 1e18, so this core goes to SAT.
This note gives proved LOCAL constraints that carry knowledge SAT cannot cheaply derive
(the values R(3,k) and e(3,k,n) for k <= 8). All hold for EVERY (3,10,40)-graph (no MTF)
unless marked.

Code: `cases/etables.py` (e(3,k,n), k = 3..9, parsed from [GR] Tables 3, 4),
`cases/local_slack.py` (tightness test), `cases/r7_glue.py` (case R7 below).

## Lemma H (independent-set hierarchy)

Let I be an independent set of G with |I| = s (1 <= s <= 9), N(I) = union of N(x), x in I,
and X_I = V - I - N(I). Then X_I is triangle-free with alpha(X_I) <= 9 - s, so
  (H1) |X_I| <= R(3, 10-s) - 1,   i.e.   |N(I)| >= 40 - s - (R(3,10-s) - 1);
  (H2) e(X_I) >= e(3, 10-s, |X_I|).
*Proof.* If J is independent in X_I then J + I is independent (no vertex of X_I is in I or
adjacent to I), so |J| <= 9 - s. H1: definition of R(3, 10-s). H2: definition of e(3,k,n). QED

Values (R(3,k) = 6, 9, 14, 18, 23, 28, 36 for k = 3..9; [GR] Table 1 / DS1):

| s | alpha(X_I) <= | max \|X_I\| | min \|N(I)\| | e(X_I) >= e(3,10-s,m), m = max \|X_I\| down |
|---|---|---|---|---|
| 1 | 8 | 35 | 4 | e(3,9,m): 35:140, 34:129, 33:118, 32:104, 31:95, 30:86, 29:77, 28:68 |
| 2 | 7 | 27 | 11 | e(3,8,m): 27:85, 26:73, 25:65, 24:56, 23:49, 22:42, 21:35, 20:30 |
| 3 | 6 | 22 | 15 | e(3,7,m): 22:60, 21:51, 20:44, 19:37, 18:30, 17:25, 16:20, 15:15 |
| 4 | 5 | 17 | 19 | e(3,6,m): 17:40, 16:32, 15:25, 14:20, 13:15, 12:11, 11:8, 10:5 |
| 5 | 4 | 13 | 22 | e(3,5,m): 13:26, 12:20, 11:15, 10:10, 9:7, 8:4 |
| 6 | 3 | 8 | 26 | e(3,4,m): 8:10, 7:6, 6:3, 5:2, 4:1 |
| 7 | 2 | 5 | 28 | e(3,3,m): 5:5, 4:2, 3:1 (m = 5 forces X_I = C5) |
| 8 | 1 | 2 | 30 | X_I is empty, K1 or K2 |
| 9 | 0 | 0 | 31 | every independent 9-set dominates G |

s = 1 is L1/L3 of notes/cases.md; s = 2 (H1) is the pair lemma L6. Levels s >= 7 follow
directly from alpha <= 9 + triangle-free; levels 2..6 carry R(3,k), e(3,k,n) knowledge.

**Tightness on real graphs** (`local_slack.py`, n = 39 analogue, 200 graphs from
known39/out/sample1000_39.g6; slack = e(X_I) - e(3,10-s,|X_I|)):

| s | sets | slack 0 | slack 1 | max \|X_I\| seen / bound |
|---|---|---|---|---|
| 1 | 7,800 | 0 | 0 | 34 / 35 |
| 2 | 114,584 | 0 | 229 | 26 / 27 |
| 3 | 840,348 | 1,514 | 5,775 | 21 / 22 |
| 4 | 3,455,880 | 107,378 | 339,019 | 17 / 17 |

On Exoo's graph alone, s = 5: 7,209 sets with slack 0; s = 6: 30,691. So in extremal
(3,10,39)-graphs the deep levels s = 3..6 are often exactly tight, while s = 1 is far from
tight. These constraints are therefore likely to prune a SAT search near the boundary.
(Level-2 double counting over all pairs is loose: about 6000 edges of slack in the 9-regular
case. So the strength is local, not global.)

## Lemma P (non-adjacent pair, exact edge count)

Let u, v be distinct, non-adjacent; C = N(u) ∩ N(v), c = |C|; A = N(u) - C, B = N(v) - C;
g(u,v) = e(A, B) = number of paths u-a-b-v of length 3. X = V - N[u] - N[v]. Then
  |X| = 38 - d(u) - d(v) + c <= 27,
  e(X) = e - Z(u) - Z(v) + sum_{x in C} d(x) + g(u,v) >= e(3,8,|X|).
*Proof.* |N[u] ∪ N[v]| = 2 + d(u) + d(v) - c. Let S = N(u) ∪ N(v). The edges inside S are
exactly the A-B edges: N(u), N(v) are independent, and an edge from x in C to N(u) or N(v)
would make a triangle with u or v. Edges with an end in S number
sum_{x in S} d(x) - e(S) = Z(u) + Z(v) - sum_{x in C} d(x) - g. Every edge at u or v has an end in
S, so G - S = X + {u, v} (isolated). Then H2 with s = 2. QED

**9-regular specialisation** (e = 180, Z = 81): |X| = 20 + c, e(X) = 18 + 9c + g,
1 <= c <= 7 (lower bound: L9), g <= (9 - c)^2.

| c | \|X\| | e(X) = | e(3,8,\|X\|) | so g >= | X lies in |
|---|---|---|---|---|---|
| 1 | 21 | 27 + g | 35 | 8 | R(3,8,21) |
| 2 | 22 | 36 + g | 42 | 6 | R(3,8,22) |
| 3 | 23 | 45 + g | 49 | 4 | R(3,8,23) |
| 4 | 24 | 54 + g | 56 | 2 | R(3,8,24, <= 79) |
| 5 | 25 | 63 + g | 65 | 2 | R(3,8,25, <= 79) |
| 6 | 26 | 72 + g | 73 | 1 | R(3,8,26, 73..81) |
| 7 | 27 | 81 + g | 85 | 4 = (9-7)^2 | R(3,8,27,85): 4 graphs, and A-B is complete K_{2,2} |

**Lemma R7.** If G is 9-regular and u, v are non-adjacent with c = 7, then X is one of the 4
graphs of R(3,8,27,85) ([GR] Table 13; HoG file data/graphs/hog/Ramseygraphs_3_8_27_e85.g6),
|A| = |B| = 2 and every vertex of A is adjacent to every vertex of B.
*Proof.* Row c = 7: g >= 4 and g <= |A||B| = 4. Then e(X) = 85. QED
`cases/r7_glue.py` tests by SAT whether any of the 4 graphs extends (status in Sec. 4).
If none extends: every 9-regular (3,10,40)-graph has c(u,v) <= 6 for all non-adjacent pairs.

**Near-regular specialisation.** For two non-adjacent 9-vertices u, v (deficiency N,
e = 180 - N/2, Z(u) = 81 - eps(u)): with w(C) = sum_{x in C} (9 - d(x)),
  e(X) = 18 - N/2 + eps(u) + eps(v) + 9c - w(C) + g(u,v) >= e(3,8,20+c).
(9-regular: N = eps = w = 0 gives the table above.)

## Lemma N (neighbourhood of the chosen vertex)

For the vertex v of Theorem A (d(v) = 9, e(H_v) <= t9), e(H_v) = 99 - N/2 + eps(v), so
  eps(v) = sum_{x in N(v)} (9 - d(x)) <= t9 - 99 + N/2.
E.g. e = 179 (N = 2), t9 = 98: eps(v) = 0, i.e. all 9 neighbours of v have degree 9.
For d(v) = 9 (any G): each x in N(v) has at most one "private" vertex in H_v (a vertex whose
only neighbour in N(v) is x), and every vertex of H_v has a neighbour in N(v).
*Proof.* Private vertices of x plus N(v) - x are independent: at most 9 - 8 = 1. A vertex of
H_v with no neighbour in N(v) together with N(v) is an independent 10-set. QED
(So for d(v) = 9 the "MTF" property holds at v in every G; no WLOG needed.)

## Lemma W (choose vertex 0 as a minimiser; valid extra constraints for cubes N(e), S8)

In cube N(e) (notes/cases.md Sec 4d) we may also assume, for EVERY vertex x:
  (W1) if d(x) = 9: e(H_x) >= e(H_0), i.e. Z(x) <= Z(0)  (vertex 0 maximises Z among 9-vertices);
  (W2) e(H_x) >= e(3,9,39 - d(x)), i.e. Z(x) <= e - e(3,9,39 - d(x))  (L3', all G);
  (W3) if the gluing of U is done: e(H_x) >= U_{d(x)} + 1 for d(x) <= 8, and e(H_x) >= T* + 1 for
       d(x) = 9 (W3 for d = 9 follows from W1 and the cube bound e(H_0) >= T* + 1).
*Proof.* W2, W3: they hold for every vertex of every G that the gluing did not exclude. W1: the
cover argument of Sec 4d gives some 9-vertex with e(H_v) <= t9max(e); a 9-vertex v0 with the
least e(H_v) also satisfies this bound, so relabel v0 as 0. The block partition {0}, {1..9},
{10..39} is unchanged, so symmetry breaking inside the blocks stays valid. QED
CAUTION (critic, Review 21): W1 is compatible only with symmetry breaking that fixes vertex 0
and the blocks {1..9}, {10..39} (e.g. SMS with --initial-partition 1 9 30). It is NOT compatible
with symmetry breaking over all of S_40 (which may move vertex 0). Lemma W CONFIRMED by critic.
Same for S8 with "8" in place of "9" in W1 (vertex 0 = an 8-vertex with least e(H_v)), and in
cube R W1 is empty (all e(H_x) = 99).
Encoding note: Z(x) = sum_{y ~ x} d(y); with degree indicator variables D[y][d] this is a
pseudo-Boolean constraint per x. W1 + W2 for all 40 vertices is 40 PB constraints of size ~40*4.
Expected effect: in the near-regular cubes the 9-vertices have e(H_x) close to e(H_0)
(average e(H_x) over all x is sum d(20-d)/40, Theorem A), so W1 cuts many partial assignments.

## Lemma Mc (max-codegree split of case R)

Let G be 9-regular and c* = max codeg(u,v) over non-adjacent pairs. Then 3 <= c* <= 7, and after
relabelling: N(0) = {1..9}, vertex 10 is not adjacent to 0, N(10) ∩ N(0) = {1..c*}, and
codeg(x,y) <= c* for every non-adjacent pair x, y.
*Proof.* Each vertex is the middle of C(9,2) = 36 paths of length 2, and the ends of such a path
are non-adjacent (triangle-free), so sum of codegrees over non-adjacent pairs = 40 * 36 = 1440.
There are C(40,2) - 180 = 600 non-adjacent pairs, so c* >= 1440/600 > 2. c* <= 7 by L6. Pick a
pair attaining c*, call it (0, 10), and order N(0) so that the common neighbours come first. The
bound for all pairs is the definition of c*. QED
Sub-cases R(3), ..., R(7). R(7) = Lemma R7 (X in R(3,8,27,85), 4 graphs). R(6): X in
R(3,8,26,73..81), estimated ~1.9e9 graphs (known39, from gluing's MCMC; e = 73..77 published:
62, 1625, 23409, 216151, 1526296 [D-C8*]). In R(3): every codegree is 1, 2 or 3 (>= 1 by L9), with n1 + n2 + n3 = 600,
n1 + 2 n2 + 3 n3 = 1440, so n3 = n1 + 240 exactly (and n2 = 840 - 2 n3). Lemma Mc CONFIRMED by critic.
Symmetry breaking must fix the blocks {0}, {1..c*}, {c*+1..9}, {10}, {11..39} (or a refinement).

## Lemma F (R(c*) split by the cross-edge count f; v1 2026-10-25, CONFIRMED by critic, Review 24)

Setting: case R, max codegree c* (Lemma Mc). For a non-adjacent pair (u,w) with codeg c let
A = N(u)-N(w), B = N(w)-N(u), f(u,w) = e(A,B), X = V - N[u] - N[w] (20+c vertices, alpha <= 7).
(F1) e(X) = 18 + 9c + f. (F2) 9 - c <= f <= (9-c)^2 (Hall: A-B has a perfect matching, duo).
(F3) per vertex v: sum over y in H_v of f(v,y) = 648 - sum_y c(v,y)^2 (paths v-x-z-y of length 3;
     those with y in N(v) are 2 x #C4 through v). Globally: sum over non-adjacent pairs f = 12960 - sum c^2.
Split of R(c*): choose (0,10) among the codeg-c* pairs with the LEAST f; call it f*. Then
f(u,w) >= f* for every codeg-c* pair (valid with block symmetry breaking {0},{1..c*},{c*+1..9},{10},rest).
The split itself needs no min-f choice ("some c*-pair has f <= 5" or "all have f >= 6" holds for any
labelling); min-f is extra symmetry breaking only. Do NOT combine it with the Lemma W vertex-0 rule.
For c* = 6: e(X) = 72 + f*, f* in 3..9.
  R(6, f* <= 5): X in R(3,8;26,75..77) = 1,765,856 graphs ([Ang] 3.2 total <= 77 is 1,767,543;
                 GR T13: 73: 62, 74: 1625). Then X + 14 vertices; two-step gluing X -> H_0 -> G.
  Pipeline test 2026-10-26 (cases): X -> G by selector SAT (cases/r6f_enc.py, smsg --no-SMS) times out on all
  sampled X (e=75: >1 h x2, e=76: >2 h, e=77: >1 h x6); e=73/74 are trivial (f < 3). Generic SAT per X is infeasible.
  PARKED (lead 2026-10-26): revisit with a GR-2013-style extender only if Angeltveit's file arrives.
  gluing (2026-10-26): two-step glue X -> H_0 = X+10+B (d=3, 462k labelled H per X, 6.6 s) -> G (5 ms/H): ~40 min/X,
  ~130 CPU-y. Unused cuts for a revival: |N_X(b)| = 8 - c(0,b) in {5,6,7} (Hall: c(0,b) >= 1), sum_b |N_X(b)| = 24 - f
  in [19,21]; B is interchangeable (labelled H counts >= 6x the classes); step-2 caps from codeg <= 6.
  R(6, f* >= 6): SAT cube with "every codeg-6 pair has f >= 6" (equivalently e(X_{uw}) >= 78).
For c* = 7 (= Lemma R7): f >= 4 by Lemma P (F2 gives only f >= 2), f <= (9-7)^2 = 4, so f = 4, e(X) = 85, X in R(3,8;27,85) (4 graphs).
For c* = 5: f* >= 4, e(X) = 63 + f*; R(3,8;25,<=70) = 2.1e9 [Ang]: too many for gluing.
Pair LP with (F1)-(F3) and e(3,8,n) rows stays feasible (duo pairlp; my check of F3: per-vertex
minimum sum (f_min + c^2) is <= 378 << 648), so (F3) is no kill, only an eager SAT/LP row.

## Remark Q (C4-count q(v); scout Test A, judged by cases 2026-10-25, not yet reviewed)
q(v) = sum_{w in H_v} C(c(v,w),2) = #C4 through v; sum_v q(v) = 4 #C4. In case R: sum_w c = 72 over 30 w,
c >= 1 (L9), so q(v) >= 54 (12 threes, 18 twos), and by F3 + Hall (f >= 9-c): 576 - 2q(v) = sum_y f(v,y) >= 198,
so q(v) <= 189. In R(3): q(v) = 54 + n1(v) exactly (n1(v) = #codeg-1 pairs at v). Q := max q = 54 forces
c* = 3 and n1 = 0 at every vertex (all non-adjacent codegrees in {2,3}).
Verdict: valid WLOG, but no kill and no order-of-magnitude gain: symmetry factor <= 40 (weaker anchor than Mc's
pair), large Q reduces via F3 to small sum f at vertex 0 = the Lemma F / gluing route, middle Q is the bulk.
Use only as a cube variable INSIDE R(3) (= max n1 vertex), not as a replacement for Mc.

## Suggested use (satcore, symsat, sms)

1. For SAT with a lazy independent-set propagator: when a partial assignment fixes an
   independent s-set I (s = 2..6) and decides enough of N(I), check H1 (|N(I)| lower bound)
   and, when X_I is fully decided, H2. Conflict clause: the decided literals.
2. Cheaper eager forms: for every non-adjacent pair, c(u,v) <= d(u) + d(v) - 11 (H1, s = 2);
   in 9-regular runs also g(u,v) >= the table value for each c (Lemma P).
3. Gluing of small classes that come out of Lemma P: R7 (4 graphs, running here).

## 4. Status of computations

- R7 cadical runs (4 CNFs, CPUs 144-147): STOPPED 2026-10-25 after 17 h, no answer; superseded by sms/Rc7b_cert.
