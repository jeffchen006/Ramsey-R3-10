# DEPENDENCIES: published results the team uses or may use

Owner: lit. Started 2026-10-25. Rule (TEAM_RULES "Trust published results", user 2026-10-25):
results published in journals or on arXiv are TRUSTED hypotheses: use them, do not re-verify them.
Unpublished claims (AI-lab repos, web pages, personal communications) are NOT here as trusted;
they are listed in sec 9 as leads only.

How to use: cite the ID (e.g. [D-E9]) in your notes and lemmas. If you use a published fact that
is not listed, tell lit and it gets an ID. Local copies: data/papers/ (text in runs/lit/txt/).

Notation: R(3,k;n,e) = triangle-free graphs on n vertices, alpha <= k-1, e edges (iso classes).
e(3,k,n) = min edges in R(3,k;n). G_v = H_v = G - N[v].

Sources:
- [GR] Goedgebeur, Radziszowski, EJC 20(1) (2013) #P30; arXiv:1210.5826v4.
- [Ang] Angeltveit, "R(3,10) <= 41", EJC 32(4) (2025) #P4.30, doi 10.37236/12936; arXiv:2401.00392v2.
- [RK88a] Radziszowski, Kreher, JCMCC 4 (1988) 37-52. [RK88b] same, JCMCC 4 (1988) 207-212.
- [RK91] Radziszowski, Kreher, "Minimum triangle-free graphs", Ars Combin. 31 (1991) 65-92.
- [DS1] Radziszowski, Small Ramsey Numbers, EJC Dynamic Survey DS1, revision #18 (2026).
- [Back13] Backelin, arXiv:1309.7874. [Krü] Krüger, Australas. J. Combin. 74(3) (2019) 371-388, arXiv:1608.07489.
- [PR] Pandey, Ravi, arXiv:2601.03572v1 (2026). [Ex89] Exoo, SIAM J. Discrete Math. 2 (1989) 488-490.
- [Ex13] Exoo, "On some small classical Ramsey numbers", EJC 20(1) (2013) #P68.
- [McZ] McKay, Zhang, J. Graph Theory 16 (1992) 99-105. [GrR] Grinstead, Roberts, JCTB 33 (1982) 27-51.
- [DuLBG] Li, Duggan, Bright, Ganesh, IJCAI 2025 pp. 2619-2627, arXiv:2502.06055.
- [HaKr] Harborth, Krause, Congr. Numer. 161 (2003) 139-150 (values via OEIS A000789/A267295).
- [McKayWeb] https://users.cecs.anu.edu.au/~bdm/data/ramsey.html ; [HoG] houseofgraphs.org minimal Ramsey graphs.

## 1. Ramsey numbers R(3,k)

| ID | statement | source |
|----|-----------|--------|
| D-R1 | R(3,3..9) = 6, 9, 14, 18, 23, 28, 36 | [DS1] Table Ia; [GR] Table 1 |
| D-R2 | R(3,8) = 28 | [McZ]; certified [DuLBG] |
| D-R3 | R(3,9) = 36 | [GrR]; certified [DuLBG] (via Graver–Yackel lemma) |
| D-R4 | 40 <= R(3,10) <= 41 | [Ex89] lower; [Ang] Thm 1 upper |
| D-R5 | R(3,10) <= 42 | [GR] Thm 6 (superseded by D-R4) |
| D-R6 | R(3,11) >= 47 | [Ex13] (graph on 46 vertices) |

## 2. Edge numbers e(3,k,n), k = 7..10

General formula, [GR] Thm 2 (= [RK88a] Thms 1, 2, 4 + [RK91]): for e(3,k+1,n) finite,
0 (n <= k); n-k (k < n <= 2k); 3n-5k (2k < n <= 5k/2); 5n-10k (5k/2 < n <= 3k); 6n-13k (3k < n <= 13k/4 - 1);
also = 6n-13k for k = 4t, n = 13t.

| ID | statement | source |
|----|-----------|--------|
| D-E0a | e(3,k+1,n) >= 5n - 10k for all k, n | [RK88a] Thm 2 |
| D-E0b | e(3,k+1,n) >= 6n - 13k for all k, n | [RK91] Thm 5.1.1 (base k <= 7 uses computed tables, see edge_tables.md 1b) |
| D-E0c | 3e(G) - 17n(G) + 35 alpha(G) + N(C4;G) >= 0 for every triangle-free G | [Krü] main theorem |
| D-E0d | equality graphs of e = 6n - 13 alpha classified | [Back13] |
| D-E0e | for k >= 5: if 3.25k - 1 < n < 3.25k then e(3,k+1,n) = 6n-13k+1; if n > 3.25k then e(3,k+1,n) > 6n-13k+1 | [Back13] Cor 4 |
| D-E0f | e(3,k+1,n) >= (40n - 91k)/6 (Backelin, unpublished manuscript; NOT trusted, quoted in [GR] Sec 2 and Lesser 2001 Thm 9) | lead only |
| D-E3 | e(3,k,n) for k = 3..6, all n: [GR] Table 3 (all given by [GR] Thm 2 except e(3,6,16) = 32, e(3,6,17) = 40 (bold, from Graver–Yackel)) | [GR] Table 3 |
| D-E7 | e(3,7,n), n = 16..22: 20, 25, 30, 37, 44, 51, 60; e(3,7,23) = inf | [GR] Table 3 / Table 12 |
| D-E8 | e(3,8,n), n = 19..27: 25, 30, 35, 42, 49, 56, 65, 73, 85; e(3,8,28) = inf | [GR] Table 3 / Table 13; [RK88b] Table I (n = 22..27) |
| D-E9 | e(3,9,n), n = 23..35: 35, 40, 46, 52, 61, 68, 77, 86, 95, 104, 118, 129, 140; e(3,9,36) = inf | [GR] Table 3 (n <= 31), Table 4 (n >= 27) |
| D-E10 | e(3,10,n), n = 29..34 (exact): 58, 66, 73, 81, 90, 99 | [GR] Table 5 |
| D-E10b | e(3,10,n) >= 107, 117, 128, 139, 151, 161, 172 for n = 35..41 | [GR] Table 5 |
| D-E10c | e(3,10,39) <= 161 (known 39-graphs have 161..175 edges) | [GR] Sec 6 end (text says "e(3,9,39)": typo) |
| D-E10d | no (3,10;39,<=150)-graph | [GR] App. 2 |
| D-E10e | e(3,10,41) = inf (i.e. R(3,10) <= 41) | [Ang] |

## 3. Unique / special graphs

| ID | statement | source |
|----|-----------|--------|
| D-G1 | R(3,9;35) has exactly one graph: C35(1,7,11,16), 8-regular, 140 edges; |Aut| = 210 (known39 computed) | [GR] Thm 3; [McKayWeb] r39_35.g6 |
| D-G2 | |R(3,8;27)| = 477 142 (all files public) | [McKayWeb]; [GR] Table 13; [Ang] Table 1 |
| D-G3 | |R(3,7;22)| = 191; |R(3,6;17)| = 7; |R(3,5;13)| = 1 | [McKayWeb]; [Ang] Table 1; [DS1] 2.1.d |
| D-G3b | |R(3,7;21)| = 1 118 436; |R(3,6;16)| = 2576; |R(3,4;8)| = 3; the (3,5;13)-graph is C13(1,5) (all graph files public) | [McKayWeb] (r37_21 found by Brinkmann–Goedgebeur); [DS1] 2.1.d |
| D-G4 | Exoo's (3,10;39)-graph: e = 167 (our check: degrees 6^1 8^14 9^24, |Aut| = 1) | [Ex89]; file http://cs.indstate.edu/ge/RAMSEY/r3.10.39 |
| D-G5 | no triangle-free circulant graph on >= 39 vertices has alpha <= 9; max order 38 | [HaKr] (OEIS A000789(10) = 38, A267295(10) = 39); [DS1] 2.1.i |
| D-G6 | Exoo found 810 non-isomorphic 40-vertex graphs with alpha <= 9 and exactly one triangle (data not public) | [Ex13] Sec "R(3,10)" |

## 4. Counts |R(3,k;n,e)| (exact unless ">=")

| ID | statement | source |
|----|-----------|--------|
| D-C7 | (3,7;n,e) counts n = 16..22 | [GR] Table 12; extended to R(3,7,18,<=36) etc. in [Ang] EJC Sec 3.1 |
| D-C8a | (3,8;23): 49:102, 50:8241, 51:356041, 52:10326716; R(3,8,23,<=53) = 238 854 716 | [GR] T13; [Ang] 3.2 |
| D-C8b | (3,8;24): 56:51, 57:3419, 58:129347, 59:3288695, 60:64233886; R(3,8,24,<=62) = 14 645 288 701; R(3,8,24,<=63) ~ 1.5e11 | [GR] T13; [Ang] 3.2 |
| D-C8c | (3,8;25): 65:396, 66:21493, 67:613285, 68:11946369; R(3,8,25,<=70) = 2 120 846 970 | [GR] T13; [Ang] 3.2 |
| D-C8d | (3,8;26): 73:62, 74:1625, 75:23409, 76:216151, 77:1526296 (total <=77: 1 767 543) | [GR] T13; [Ang] 3.2 |
| D-C8e | (3,8;27): 85:4, 86:92, 87:1374, 88:11915, 89:52807, 90:122419, 91:151308, 92:99332, 93:33145, 94:4746 | [GR] T13 |
| D-C9a | (3,9;30): 86:1800, 87:147335 | [GR] T14 |
| D-C9b | (3,9;31): 95:560, 96:35154 | [GR] T14 |
| D-C9c | (3,9;32): 104:39, 105:952, 106:18598, 107:234681, 108:2104151; R(3,9,32,<=112) = 1 554 928 360; 506 7-regular graphs in R(3,9,32,112) | [GR] T14; [Ang] 3.3, Sec 5 |
| D-C9d | (3,9;33): 118:5, 119:69, 120..132 lower bounds only; R(3,9,33,<=121) = 14 395 | [GR] T14; [Ang] 3.3 |
| D-C9e | (3,9;34): 129:1, 130:4; R(3,9,34,<=130) = 5 | [GR] T14; [Ang] 3.3 |
| D-C9f | (3,9;26..29): 26: 52:1, 53:1, 54:444, 55:58484; 27: 61:700, 62:95164, 63:6498191; 28: 68:126, 69:17223, 70:1202362; 29: 77:1342, 78:156686 | [GR] T14 |
| D-C10 | (3,10;29..34): 29: 58:5, 59:1364; 30: 66:5084, 67:1048442; 31: 73:2657, 74:580667; 32: 81:6592; 33: 90:57099; 34: 99:>=1 | [GR] T15 |
| D-C39 | known (3,10;39)-graphs: >= 43 225 483 (GR set: 43 117 868) | [Ang] EJC Sec 7, Table 1 |

Minimum-edge sets of D-C8..D-C10 are public as files ([HoG]; local data/graphs/hog/).

## 5. Structural theorems (n = 41, 42; usable as patterns)

| ID | statement | source |
|----|-----------|--------|
| D-S1 | any (3,10;42)-graph is 9-regular with 189 edges | [GR] Thm 4 |
| D-S2 | no 9-regular (3,10;42,189)-graph; all 2 104 151 (3,9;32,108)-graphs glued, no output | [GR] Sec 6, Lemma 5, Thm 6 |
| D-S3 | every (3,10;41)-graph has a v with G_v in R(3,9,32,<=112), R(3,9,33,<=121) or R(3,9,34,<=130) | [Ang] Prop 2 (EJC) / 2.1 (arXiv) |
| D-S4 | a (3,9;36)-graph contains a (3,8;27;80)-graph | Graver–Yackel 1968 (as used in [DuLBG] Lemma 1) |

## 6. Extension facts about 38- and 39-vertex graphs

| ID | statement | source |
|----|-----------|--------|
| D-X1 | none of the 37M+ (3,10;39)-graphs of GR (161 <= e <= 175) extends to a (3,10;40)-graph | GR Berlin slides Nov 2012, p.17 (data/papers/GR_ber12_slides.pdf). NOTE: slides, not the paper; [GR] p.15 only says "no (3,10;40)-graphs were constructed" |
| D-X2 | "a large number" of (3,10;38)-graphs produced by Angeltveit's gluing: none extends (one-point) to R(3,10,40) or R(3,10,41) | [Ang] EJC Sec 6 |
| D-X3 | known 39-graphs were enlarged by deleting 1 (and 2, 3) vertices and re-extending in all ways | [Ang] EJC Sec 7 |

## 7. Pandey–Ravi structural claims for a (3,10,40)-graph Ω ([PR] Sec 3; hand proofs, arXiv only, not refereed)

| ID | statement | source |
|----|-----------|--------|
| D-P1 | Delta(Ω) = 9 (from e(3,10,40) >= 161), delta(Ω) >= 4 | [PR] Sec 3 intro |
| D-P2 | no vertex v has two neighbours with degree sum <= 11 | [PR] Lemma 3.1 |
| D-P3 | for v1, v2 in N(v): |N(v1) ∪ N(v2)| >= 11 | [PR] Lemma 3.2 |
| D-P4 | diam(Ω) in {2, 3}; 9-regular => diam 2 | [PR] Thm 3.3 and text |
| D-P5 | if diam 2 and d(v) = 6: at most 2 vertices of degree 6 in N(v) | [PR] Cor 3.4 |
| D-P6 | if d(v) = 4: 19 <= |Ω2(v)| <= 24, 11 <= |Ω3(v)| <= 17 | [PR] Lemma 3.5 |
| D-P7 | if diam 2: delta >= 6; kappa >= 6; kappa = delta; every minimum vertex cut is some N(v) | [PR] Thms 3.6, 3.8, 3.9, Lemma 3.7 |
Caveat: some proofs are terse (the algal-lab review notes arithmetic slips in Thm 3.6 and gives a clean
proof of the delta >= 6 part; our cases M1 is an independent proof). Trusted by rule, but prefer our own proofs where we have them.

## 8. Other published facts that may be used

| ID | statement | source |
|----|-----------|--------|
| D-O1 | Theorem: every finite transitive group contains a minimal transitive subgroup; 1963 minimal transitive groups of degree 40 (315 842 transitive groups of degree 40) | Holt, Royle, arXiv:1811.09015, Tables 1-2 |
| D-O2 | inequality (4) of [GR]: n e - sum_i n_i (i^2 + e(3,k-1,n-i-1)) >= 0 for (3,k;n,e)-graphs | [GR] eq. (4) ([RK88a] Lemma 1) |
| D-O3 | McKay–Radziszowski subgraph-counting identity: sum_v 2e(G_v^-) = sum_v [d(v)(n - 2d(v)) + 2e(G_v^+)] | [Ang] EJC Sec 3.2, citing McKay–Radziszowski JCTB 69 (1997) |
| D-O4 | R(3, K10 - e) = 37: every triangle-free graph on 37 vertices has 10 vertices spanning at most one edge; exact e(3, Kk - e, n) for all n with k <= 10 | Goedgebeur, Radziszowski, EJC 20(4) (2013) #P19 (local data/papers/GR_K10e_e3j13.pdf) |
| D-O5 | Lesser 2001 thesis (Stockholm): table of e(3,y,n) bounds (superseded by [GR] for k <= 10); proof that a (3,10,39,145)-realizer has no vertex of degree < 6 (Sec 5.4; e = 145 < 151 is now impossible by D-E10b) | data/papers/Lesser2001.pdf |

## 9. NOT trusted (unpublished; leads only)
- hraness/algal-lab (GitHub): degree-4 exclusion (also re-derived by our critic: that is OUR result, notes/critic.md Rev. 4),
  vertex-transitive and Cayley exclusions, MTF delta >= 6 review.
- unsolvedlab.com: prime-order automorphism classes, Wang–Landau |R(3,9;30,99)| ~ 0.8-1.5e18.
- Backelin, "Contributions to a Ramsey calculus" (unpublished manuscript; bounds quoted in [GR] and DS1 only).
- Personal communications quoted in papers (e.g. Backelin's (3,10;34,99)-graph in [GR] is a construction; e(3,10,34) = 99 is in [GR] Table 5, so trusted).
