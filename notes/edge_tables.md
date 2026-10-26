# Minimum edge counts e(3,k,n) and graph counts (k = 8, 9, 10)

Author: lit. Date: 2026-10-24. Status: first full version.

Notation: e(3,k,n) = min edges of a triangle-free graph on n vertices with alpha < k
(alpha <= k-1). R(3,k;n,e) = set of such graphs with e edges (iso classes).
G_v = G - N[v]. If deg(v) = d then G_v is in R(3,k-1; n-d-1, e(G) - Z(v)),
Z(v) = sum of degrees of neighbours of v.

Abbreviations of sources:
- [GR] Goedgebeur, Radziszowski, "New computational upper bounds for Ramsey numbers R(3,k)",
  EJC 20(1) (2013) #P30; arXiv:1210.5826v4. Local copies: data/papers/arxiv_1210.5826.pdf,
  data/papers/e3k12.pdf (EJC-format preprint from cs.rit.edu; tables identical to arXiv v4).
- [Ang] Angeltveit, "R(3,10) <= 41", arXiv:2401.00392v2; EJC 32(4) #P4.30 (2025).
- [RK88], [RK91]: Radziszowski–Kreher, JCMCC 4 (1988) 37-52 and 207-212; Ars Combin. 31 (1991)
  65-92. Source of Theorem 2 below (as cited by [GR]). Not downloaded.
- [Back]: Backelin, "Contributions to a Ramsey calculus" (unpublished, 500+ pages, per [GR] Sec. 2);
  arXiv:1309.7874 (classifies graphs with e = 6n - 13k exactly).
- [Krü]: Krüger, Australas. J. Combin. 74(3) (2019) 371-388, arXiv:1608.07489;
  PhD thesis, Stockholm Univ. 2019. DS1 rev 18 item 2.2.b says it gives
  "further improvements to bounds on e(3,k,n)".
- [DS1]: Radziszowski, Small Ramsey Numbers, EJC DS1 rev #18 (2026). NOTE: DS1 section 2.4 is
  "Some pillars of asymptotics"; the e(3,k,n) discussion is in item 2.2.a/b, not 2.4.
  Our local copy data/papers/DS1_rev18.pdf has 87 pages: the reference list (pp. 88-149)
  is MISSING from it.

## 1. General formula ([GR] Theorem 2, from [RK88, RK91])

For all n, k with e(3,k+1,n) finite:
- 0 if n <= k; n-k if k < n <= 2k; 3n-5k if 2k < n <= 5k/2;
  5n-10k if 5k/2 < n <= 3k; 6n-13k if 3k < n <= 13k/4 - 1.
- Also e(3,k+1,n) = 6n-13k for k = 4t, n = 13t, and e(3,k+1,n) >= 6n-13k for ALL n, k.
- Backelin bound (unpublished, credited via Lesser 2001, [GR] Sec. 2): e(3,k+1,n) >= (40n - 91k)/6.
- Krüger ([Krü] abstract): 3e - 17n + 35*alpha + N(C4) >= 0 for every triangle-free G.
  Dropping N(C4) >= 0: e >= (17n - 35 alpha)/3. For n = 40, alpha = 9: e >= 122 (weak; my computation).

For n = 40, k+1 = 10: 6n-13k = 123; Backelin: >= 131 (my computation). Both much weaker
than the computational bound 161 below.

### 1b. Which general bounds are computer-free (checked 2026-10-24 for cases/cert)
- e(3,k+1,n) >= 5n - 10k for all k, n: Radziszowski–Kreher, JCMCC 4 (1988) 37-52 [RK88a], Theorem 2 (p.40-41).
  Hand proof by induction on k; base only e(3,4,8) = 10. Computer-free. Local: data/papers/RK1988_paper14.pdf (scan).
- e(3,k+1,n) >= 6n - 13k for all k, n: Radziszowski–Kreher, Ars Combin. 31 (1991) 65-92, Theorem 5.1.1 (p.76).
  Local: data/papers/RK1991_paper18.pdf (scan; source cs.rit.edu/~spr/PUBL/paper18.pdf).
  Induction step is by hand (smallest counterexample: connected, 4-regular, girth >= 5, k0 >= 11, n >= 36;
  Sec 5.2-5.3). BUT the base uses computed data: Prop 5.1.3(a) proof "Check that the values and bounds of
  e(3,k+1,n) calculated in [3],[4],[7],[8] satisfy (4) for k <= 7", and Lemma 5.1.5 uses "examination of all
  values of e(3,k+1,n) for k <= 6 [7]". [7] = RK88a (computer catalogue of all (3,<=6)-graphs and (3,7)-graphs);
  [8] = RK JCMCC 4 (1988) 207-212 (e(3,8,22..27) by "several computer algorithms"; e(3,8,25) >= 65 took
  ~250 h on a VAX780; local data/papers/RK1988_paper15.pdf); [4] Grinstead–Roberts 1982 (e(3,7,19..22)).
- Consequence: for alpha <= 6 and alpha <= 7 graphs (k+1 = 7, 8), 6n - 13k is a COMPUTED fact for n > 3k:
  e(3,7,n) >= 6n-78 needs n = 19..22 (true values 37, 44, 51, 60 >= 36, 42, 48, 54);
  e(3,8,n) >= 6n-91 needs n = 22..27 (true values 42, 49, 56, 65, 73, 85 >= 41, 47, 53, 59, 65, 71).
  For n <= 3k it follows from 5n - 10k (hand). Suggested: certify these 10 facts by SAT + DRAT (large slack).
  Used by cases' Theorem A'' (notes/cases.md): the MTF coarse split needs only e(3,8,m) >= 6m-91 for m = 23..27
  and R(3,8) <= 28; sent to cert for SAT certification.

## 2. e(3,8,n) — all exact ([GR] Table 3; counts [GR] Table 13)

| n  | e(3,8,n) | source |
|----|----------|--------|
| 19 | 25 | Thm 2 / [RK] |
| 20 | 30 | [RK] |
| 21 | 35 | [RK] |
| 22 | 42 | [RK88b] (bold in Table 3) |
| 23 | 49 | [RK88b] |
| 24 | 56 | [RK88b] |
| 25 | 65 | [RK88b] |
| 26 | 73 | [RK88b] |
| 27 | 85 | Brinkmann–Goedgebeur–Schlage-Puchta 2012 |
| 28 | inf | R(3,8) = 28 (McKay–Zhang 1992) |

([GR] p.10-11: "all cases for k = 8 and 22 <= n <= 26 in [19]" = RK 1988 JCMCC 4 207-212;
"e(3,8,27) = 85 was computed in [4]".)

## 3. e(3,9,n) — all exact ([GR] Table 3 for n <= 31, Table 4 for n >= 27)

| n  | e(3,9,n) | source / comment |
|----|----------|------------------|
| 26 | 52 | Thm 2 (5n-10k, k=8) |
| 27 | 61 | [GR] Table 4 |
| 28 | 68 | [GR] Table 4 ("the same as in [Back]") |
| 29 | 77 | [GR] Table 4 |
| 30 | 86 | [GR] Table 4 |
| 31 | 95 | [GR] Table 4 |
| 32 | 104 | [GR] Table 4 |
| 33 | 118 | [GR] Table 4 |
| 34 | 129 | [GR] Table 4 |
| 35 | 140 | [GR] Thm 3: unique (3,9;35)-graph = circulant C35(1,7,11,16), 8-regular (Kalbfleisch 1966) |
| 36 | inf | R(3,9) = 36 |

## 4. e(3,10,n) ([GR] Table 3 for n <= 31, Table 5 for n >= 29)

| n  | e(3,10,n) | exact? | source / comment |
|----|-----------|--------|------------------|
| 30 | 66  | exact | [GR] Table 5 |
| 31 | 73  | exact | [GR] Table 5 |
| 32 | 81  | exact | [GR] Table 5 |
| 33 | 90  | exact | [GR] Table 5 |
| 34 | 99  | exact | [GR] Table 5; lower bound by [GR], (3,10;34,99)-graph by Backelin (pers. comm.) |
| 35 | >= 107 | bound | [GR] Table 5 |
| 36 | >= 117 | bound | [GR] Table 5 |
| 37 | >= 128 | bound | [GR] Table 5 |
| 38 | >= 139 | bound | [GR] Table 5 |
| 39 | >= 151, <= 161 | bound | lower [GR] Table 5; upper: known (3,10;39)-graphs have 161..175 edges ([GR] p.15) |
| 40 | >= 161 | bound | [GR] Table 5 (no graph known) |
| 41 | inf | — | [Ang] (GR Table 5 had ">= 172, 184 maximum") |
| 42 | inf | — | [GR] Thm 6 |

No upper bounds (constructions) for n = 35..38 are given in [GR]. They can be derived from
known 39-vertex graphs by vertex deletion (task for known39; not from literature).

I found NO published improvement of e(3,10,n) for 35 <= n <= 40 after [GR] 2013 ([Ang] does not
state any). DS1 rev 18 item 2.2.b says [Krü] improves some e(3,k,n) bounds; I have not yet
found which ones (thesis text not yet obtained). OPEN: check Krüger thesis for k = 10.

### Quick degree-sequence check for n = 40 (my computation, using only the exact e(3,9,m))

For G in R(3,10;40,e): delta >= 40 - 36 = 4, Delta <= 9. With f(d) = 20d - d^2 - e(3,9,39-d),
inequality (4) of [GR] becomes sum_d n_d f(d) >= 0:

| d | m = 39-d | e(3,9,m) | d^2 + e(3,9,m) | f(d) |
|---|----------|----------|----------------|------|
| 4 | 35 | 140 | 156 | -76 |
| 5 | 34 | 129 | 154 | -54 |
| 6 | 33 | 118 | 154 | -34 |
| 7 | 32 | 104 | 153 | -13 |
| 8 | 31 |  95 | 159 |  +1 |
| 9 | 30 |  86 | 167 | +13 |

Pure (4) gives e >= 159 (e.g. n7 = 2, n8 = 38). [GR] reached 161 with extra gluing runs
(increments t_i, as in [GR] Sec. 3 example). 9-regular: e = 180, gamma = 40*13 = 520,
each G_v in R(3,9;30,99): slack 99 - 86 = 13 edges over the minimum.

## 5. Graph counts at low e

### (3,8;n,e) — [GR] Table 13 (exact counts; "?" = not computed)
| n  | counts by e |
|----|-------------|
| 23 | 49:102, 50:8241, 51:356041, 52:10326716 |
| 24 | 56:51, 57:3419, 58:129347, 59:3288695, 60:64233886 |
| 25 | 65:396, 66:21493, 67:613285, 68:11946369 |
| 26 | 73:62, 74:1625, 75:23409, 76:216151, 77:1526296 |
| 27 | all e (85..94): 4, 92, 1374, 11915, 52807, 122419, 151308, 99332, 33145, 4746; total 477142 |

[Ang] Sec 3.2 (partial census): R(3,8,23,e<=53) = 238 854 716; R(3,8,24,e<=62) = 14 645 288 701;
R(3,8,24,e<=63) "approximately 150 billion" (not stored); R(3,8,25,e<=70) = 2 120 846 970;
R(3,8,26,e<=77) = 1 767 543; R(3,8,27) = 477 142.
Check: [GR] 26: 62+1625+23409+216151+1526296 = 1 767 543 = [Ang]. Agree.

### (3,9;n,e) — [GR] Table 14
| n  | counts by e ("≥" = lower bound only) |
|----|-------------|
| 26 | 52:1, 53:1, 54:444, 55:58484 |
| 27 | 61:700, 62:95164, 63:6498191 |
| 28 | 68:126, 69:17223, 70:1202362 |
| 29 | 77:1342, 78:156686 |
| 30 | 86:1800, 87:147335 |
| 31 | 95:560, 96:35154 |
| 32 | 104:39, 105:952, 106:18598, 107:234681, 108:2104151 |
| 33 | 118:5, 119:69, 120:>=1223, 121:>=13081, 122:>=90235, 123:>=401731, 124:>=1188400, 125:>=2366474, 126:>=3198596, 127:>=2915795, 128:>=1758241, 129:>=673600, 130:>=153676, 131:>=18502, 132:>=922 |
| 34 | 129:1, 130:4, 131:>=15, 132:>=40, 133:>=54, 134:>=43, 135:>=20, 136:>=7 |
| 35 | 140:1 (none for 136..139) |

[Ang] Sec 3.3: R(3,9,32,e<=112) = 1 554 928 360 (completeness checked by McKay);
R(3,9,33,e<=121) = 14 395; R(3,9,34,e<=130) = 5; R(3,9,35,e<=139) empty ([GR] Table 14).
506 regular degree-7 graphs in R(3,9,32,112) ([Ang] Sec 5).
Checks: 34: 1+4 = 5 agrees. 33: [GR] gives 5+69+>=1223+>=13081 = >=14378 <= 14395. Consistent;
[Ang] EJC Sec 3.3 says the same: GR "were missing just 17 such graphs".
[Ang] EJC Sec 3.1-3.3 also says: R(3,7) counts agree with [GR] Table 12 (extended R(3,7,18,e<=36));
R(3,8) agrees with [GR] Table 13 (extended to R(3,8,23,e<=53), R(3,8,24,e<=62)); R(3,9) agrees with
[GR] Table 14 (extended to R(3,9,32,e<=112), R(3,9,33,e<=121)).

### R(3,9;30, e <= 99) — the 9-regular n = 40 case
- [GR]: only e = 86 (1800) and e = 87 (147335) known exactly.
- [Ang] Sec 7: "many orders of magnitude more graphs than R(3,9,32,e<=112)" (no number).
- Unsolved Lab web report (unsolvedlab.com/problems/ramsey-r310, Oct 2026, NOT peer reviewed,
  AI-agent lab): Wang–Landau estimate "about 0.8 to 1.5 x 10^18" graphs in R(3,9,30,99).
  Treat as an unverified estimate.
- No exact count for 88 <= e <= 99 is published (as far as I found).

### (3,10;n,e) — [GR] Table 15
| n  | counts |
|----|--------|
| 29 | 58:5, 59:1364 |
| 30 | 66:5084, 67:1048442 |
| 31 | 73:2657, 74:580667 |
| 32 | 81:6592 |
| 33 | 90:57099 |
| 34 | 99:>=1 |
| 39 | none with e <= 150 ([GR] App. 2: "all (3,10;39,<=150)-graphs (there are none)", 4.8 CPU years) |

Known (3,10;39)-graphs: arXiv v2 Sec 7: 43 146 537 (union of his 39 745 077 and GR's 43 117 868).
EJC version (Sec 7, Table 1): ">= 43 225 483" after deleting 2 or 3 vertices and re-extending.
USE THE EJC NUMBER 43 225 483 (newest).

## 6. Disagreements / typos found
1. [GR] p.15 says "151 <= e(3,9,39) <= 161". Typo: must be e(3,10,39) (e(3,9,39) = inf).
2. Number of known (3,10;39)-graphs at the time of [GR]: paper says "more than 4*10^7";
   GR Berlin slides (Nov 2012, data/papers/GR_ber12_slides.pdf p.17) say "37M+";
   [Ang] says GR found 43 117 868. Exoo's count: [GR] "almost 300000" vs slides "266K+".
   Probably different dates; not a real conflict.
   Exoo 2013 (EJC 20(1) #P68, Sec "R(3,10)") says Goedgebeur's catalogue has "nearly 50000000" (3,10,39)-graphs,
   vs 43 117 868 in [Ang]. Unresolved; [Ang]'s exact count (the file he received) is the more precise source.
3. [Ang] Sec 5 writes "gluing two graphs G1, G2 in R(3,8,63,e=112)" (arXiv v2) and
   "G1, G2 in R(3,8,24,e=112)" (EJC). Both typos: from context G1, G2 are in R(3,8,24,e=63)
   (the dual neighbourhoods of v and w).
3b. [Ang] arXiv v2 vs EJC (2025): EJC has extra Sec 3.4 (data checks), an LP lemma via the
   McKay–Radziszowski subgraph-counting identity, and the larger 39-vertex count 43 225 483.
   EJC Sec 6: his R(3,10,38)-graphs extend to neither 41 nor 40 vertices. Local: data/papers/Ang_EJC_v32i4p30.pdf.
4. DS1 item 2.1.d: "at least 43*10^6 (3,10)-graphs on 39 vertices [GoeR2, Ang1]". Agrees with [Ang].
5. Unsolved Lab page says "Circulants were excluded by Harborth and Krause in 2003" — DS1 2.1.i
   supports this (no Table Ia bound improves with a cyclic graph on < 102 vertices except R(3,k), k >= 13).

## 7. Pandey–Ravi, arXiv:2601.03572v1 (7 Jan 2026), Section 3 "(3,10,40) graphs"
Local copy data/papers/arxiv_2601.03572.pdf. Hand proofs, no computation. Claims for a (3,10,40)-graph Ω:
- Delta = 9 (because e(3,10,40) >= 161 > 160 = 8-regular). delta >= 4.
- Lemma 3.1: no vertex has two neighbours with degree sum <= 11. Lemma 3.2: |N(v1) ∪ N(v2)| >= 11
  for v1, v2 in N(v).
- Thm 3.3: diam = 2 or 3. 9-regular => diam 2 (easy: deg(u) = 9 forces every vertex within distance 2).
- Lemma 3.5 (deg(v) = 4): 19 <= |Ω2(v)| <= 24, 11 <= |Ω3(v)| <= 17.
- Thm 3.6: if diam = 2 then delta >= 6. Thm 3.8: if diam = 2 then kappa = delta. Thm 3.9: if diam = 2,
  every minimum vertex cut is some N(v).
- No new e(3,k,n) value. Proofs are short and some steps look incomplete (e.g. Lemma 3.5 text says
  ">= 11" then "10 <= |Ω3|"; Thm 3.6 degree-5 case is terse). Treat as UNVERIFIED; check before use.

## 8. Unreviewed recent claims (web, 2026; not literature, use with care)
- hraness/algal-lab GitHub release r310-degree-four-proof-20260928: LRAT-checked refutation
  (140 vars, 98 965 clauses) that a (3,10,40)-graph has no vertex of degree 4, so delta >= 5.
  Uses uniqueness of the (3,9,35)-graph as premise. Independently re-derived by our critic
  (own CNF, drat-trim + cake_lpr VERIFIED; notes/critic.md Rev. 4). So delta >= 5 (premise: GR Thm 3).
  (GR used the same idea at n = 42: G_v cannot be the (3,9;35)-graph, [GR] proof of Thm 4.)
- Unsolved Lab report (same group?): order-7, 11..37 automorphisms excluded; 9-regular case open.
  Details in notes/symmetric_search_lit.md.
