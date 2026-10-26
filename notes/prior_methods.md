# Prior methods and exact claims: what a 40-vertex proof needs

Author: lit. Date: 2026-10-24. Readers: cert, satcore, sms, gluing (and cases, lean).
Certification details (DRAT/LRAT/VeriPB, Keller, Schur 5, empty hexagon, R(4,5) HOL4) are in
cert/lit_certified_proofs.md (agent cert); this note does not repeat them.
Local papers: data/papers/ (text in runs/lit/txt/). Numbers are quoted from the papers.

## 1. Goedgebeur–Radziszowski 2013 [GR]: R(3,10) <= 42
EJC 20(1) #P30; arXiv:1210.5826v4. Local: arxiv_1210.5826.pdf, e3k12.pdf.

Exact claims:
- Thm 3: unique (3,9;35)-graph; e(3,9,35) = 140 (C35(1,7,11,16)).
- Thm 4: R(3,10) = 43 iff e(3,10,42) = 189, i.e. any (3,10;42)-graph is 9-regular. Proof: degree-sequence
  solutions of (4) (Table 6, s <= 4) + hand case analysis (Cases 1-5), using e(3,9,33) = 118, e(3,9,34) = 129
  and a computation that G_v is never the (3,9;35)-graph.
- Sec 6 / Lemma 5 / Thm 6: all (3,9;32,108)-graphs: 2 104 151 (set X), from extending (3,8;27), (3,8;26,<=77),
  (3,8;25,<=68), (3,8;24,<=59), (3,8;23,49) plus a special run on all 64 233 886 (3,8;24,60)-graphs for the
  n6 = 8, n7 = 24 degree class. A specialised gluing (neighbours of v -> independent 8-sets; pair table;
  Delta = 9 pruning "particularly strong") found no 9-regular (3,10;42,189)-graph.
- Tables 3-5, 12-15: e(3,k,n) values and counts (see notes/edge_tables.md).
Method:
- Neighbourhood gluing extension (Sec 3, Alg. 2): input H = G_v in R(3,k;m), add v and d neighbours, each
  joined to an independent set of H; prune with the pairwise test "V(H) minus (S_i ∪ S_j) induces no
  independent (k-1)-set" (H in R(3,k), output in R(3,k+1)), precomputed alpha of all 2^n subsets (feasible to n = 31),
  forbidden vertices (degree k reached), edge lower bound; no isomorphism rejection inside, nauty afterwards.
- Completeness bookkeeping: increments t_i over e(3,k,m_i) so that inequality (4) has no other solution
  (Table 2 example). Degree-sequence feasibility = small integer program (like Lesser's FRANK).
Verification ([GR] App. 2): independent alpha checker; edge add/remove consistency; Gv re-derivation;
two independent generators (MTF method of Brinkmann–Goedgebeur–Schlage-Puchta vs gluing) agree on
(3,7;21,<=55), (3,7;22), (3,8;26,<=76), (3,8;27,<=88); counts agree with [RK], Backelin. NO proof certificates.
Cost: about 50 CPU years total (Xeon L5520 2.27 GHz). 5.5 + 5.8 CPU years for (3,9;32,108); 0.25 CPU years for
the final 42-vertex gluing; 4.8 CPU years for "all (3,10;39,<=150)-graphs (there are none)".

## 2. Angeltveit 2024/2025 [Ang]: R(3,10) <= 41
arXiv:2401.00392v2; EJC 32(4) #P4.30 (2025), doi 10.37236/12936. Local: arxiv_2401.00392.pdf, Ang_EJC_v32i4p30.pdf.
Use the EJC version (it adds Sec 3.4 data checks and a worked LP lemma).

Exact claims:
- Prop 2 (EJC) / 2.1 (arXiv): every (3,10,41)-graph has a vertex v with G_v in R(3,9,32,e<=112),
  R(3,9,33,e<=121), R(3,9,34,e<=130) (R(3,9,35,e<=139) empty). Proof: N = n8+2n7+3n6+4n5,
  e(G) = (369-N)/2, eps(v) = sum over nbrs of (9 - d(w)); e(G_v) = e(G) - 9d(v) + eps(v);
  auxiliary triangle-free graph on N vertices (9-d(v) copies of v) has a vertex of degree <= (N-1)/2 (N odd).
- Census: R(3,7,16,<=24) 46 514; (17,<=30) 3 131 580; (18,<=36) 23 149 358; (19,<=41) 2 173 527;
  (20,<=46) 10 613. R(3,8,23,<=53) 238 854 716; R(3,8,24,<=62) 14 645 288 701; R(3,8,24,<=63) ~150e9 (not stored);
  R(3,8,25,<=70) 2 120 846 970; R(3,8,26,<=77) 1 767 543; R(3,8,27) 477 142.
  R(3,9,32,<=112) 1 554 928 360; R(3,9,33,<=121) 14 395; R(3,9,34,<=130) 5.
- 506 7-regular graphs in R(3,9,32,112), via a special pairing method (two dual neighbourhoods
  G1, G2 in R(3,8,24,63) glued along G' in R(3,7,16..18), hashmap on degree sequences), ~6 CPU months.
- Gluing all of R(3,9,32,<=112) to 41 vertices: ~3 CPU months; no output. Total ~3 CPU years on 2 desktops.
- Extra check: many R(3,10,38) produced; one-point extension gives none on 41 and none on 40.
- R(3,10,39) known: >= 43 225 483 (EJC).
Method changes vs GR (Sec 4): (1) glue only MAXIMAL independent sets (Lemma 4: compatibility is
monotone under supersets), then expand to subsets with edge pruning; (2) no 2^n alpha table — lazy table
(n <= 27) or hashmap; pairwise compatibility via bitvectors of independent (t-1)-sets in V(G') \ S;
(3) compute independence numbers only for full candidate tuples; (4) order maximal sets so the
largest "mutually incompatible" class is used last (inner loop). Speed: ~250 R(3,8,24)-graphs/s/core.
Completeness of censuses: one-vertex deletion + one-point re-extension (no new graphs), McKay's check of
R(3,9,32,<=112), comparison with [GR] tables 12-14, optimisation on/off comparisons. NO proof certificates.
LP lemma (EJC Sec 3.2): sum_v [2e(G_v^-) - d(v)(n-2d(v)) - 2e(G_v^+)] = 0 (McKay–Radziszowski 1997 identity) plus
c * (dbar - d(v)) terms; choose c so every "too dense G_v" term is positive.

Author's view for n = 40 (EJC Sec 7): 9-regular case has all G_v in R(3,9,30,e = 99), "many orders of
magnitude more graphs than R(3,9,32,e<=112)"; R(3,10) = 40 "quite difficult to prove with current techniques".

### n = 40 analogue of Prop 2 (my derivation; cases/gluing should check)
Same argument with Delta <= 9 and N = sum (9 - d(v)) = 360 - 2e(G): e(G_v) = e(G) - 9d(v) + eps(v), and the
auxiliary triangle-free graph on N vertices has a vertex of degree <= N/2 (Mantel). So either G is 9-regular
(every G_v in R(3,9,30,99)) or some v with d = d(v) <= 8 has e(G_v) <= 180 - 9d:
| d | G_v in | e(3,9,m) | slack above minimum |
|---|--------|----------|---------------------|
| 8 | R(3,9,31, e <= 108) | 95 | 13 |
| 7 | R(3,9,32, e <= 117) | 104 | 13 |
| 6 | R(3,9,33, e <= 126) | 118 | 8 |
| 5 | R(3,9,34, e <= 135) | 129 | 6 |
| 4 | R(3,9,35, e <= 144) = the unique graph | 140 | (excluded by degree-4 result, unreviewed) |
Compare n = 41: slack 8 at m = 32 (112 - 104) gave 1.55e9 graphs. At n = 40 the slack is 13 at m = 31 and 32,
so pure gluing needs far larger censuses. With MTF + delta >= 6 (see below) the d = 4, 5 rows vanish
(but MTF must then be used consistently).
Checked by gluing (same result). SUPERSEDED for planning by cases' Theorem A (notes/cases.md, averaging over
L4): G has a vertex v with (d = 9 and e(H_v) <= 99) or (d = 8 and e(H_v) <= 96); if G is not 9-regular, one with
(d = 9 and e(H_v) <= 98) or (d = 8 and e(H_v) <= 96). Use that.

## 3. Li–Duggan–Bright–Ganesh [DuLBG]: certified R(3,8) = 28 and R(3,9) = 36 by SAT + CAS
Full reference: Zhengyu Li, Conor Duggan, Curtis Bright, Vijay Ganesh, "Verified Certificates via SAT and
Computer Algebra Systems for the Ramsey R(3,8) and R(3,9) Problems", IJCAI 2025, pp. 2619-2627;
arXiv:2502.06055v2. Earlier: Duggan, Li, Bright, Ganesh, "A SAT + Computer Algebra System Verification of
the Ramsey Problem R(3,8) (Student Abstract)", AAAI 2024 (ojs.aaai.org/index.php/AAAI/article/view/30437).
Code: github.com/ConDug/MathCheckRamsey. Local: arxiv_2502.06055.pdf.

What they did:
- Direct encoding (all triangles, all independent k-sets) + static lex row constraints (Codish et al. 2019) +
  degree cardinality constraints n - R(p,q-1) <= deg <= R(p-1,q) - 1 (totalizer).
- Orderly generation (Read/Faradzev) in CaDiCaL via IPASIR-UP: when an upper-left submatrix is fully assigned,
  the CAS checks canonicity (column-wise lex order of above-diagonal entries); non-canonical -> blocking clause
  with a witness permutation.
- Better in the complement form R(k,3): R(8,3) 18.5 h vs R(3,8) 112.1 h sequential (Table 2); CaDiCaL alone > 7 days.
- R(3,9): NOT a direct 36-vertex SAT run. Uses Graver–Yackel lemma (hand proof): a (3,9;36)-graph contains a
  (3,8;27;80)-graph; they show no (8,3;27;271)-graph (complement), degrees 19..22, exactly 271 edges.
  Cube-and-conquer: AlphaMapleSAT cubes (MCTS lookahead), 2 486 cubes, 26 h wall on 128 cores,
  proofs 289 GiB, verification 473 874 s. R(8,3) on 28 vertices: 41 cubes, 8 h wall, 5.8 GiB proofs.
- Verification: DRAT-trim modified to accept trusted clauses (prefix 't'); CAS clauses checked separately by
  a Python script applying witness permutations; cube cover checked recursively.
- Their stated gaps: encoding not verified; custom permutation-check script not verified; Graver–Yackel lemma
  not formalised. "does not constitute formal proofs of the corresponding Ramsey numbers".
- The DS1 tag [DuLBG] matches these authors (Duggan, Li, Bright, Ganesh). DS1 rev 18 ref list is not in our copy.

Lessons for n = 40: the hardest certified instance so far is 27 vertices (with exact edge count) at about
1e6 CPU-s. A 40-vertex direct instance has 780 edge variables and C(40,10) = 847 660 528 independent-10-set
clauses (needs lazy generation). A structural reduction like Graver–Yackel (big vertex-deleted subgraph with
exact edge count) was essential for R(3,9).

## 4. Kirchweger–Szeider SAT Modulo Symmetries [KirS]
- M. Kirchweger, S. Szeider, "SAT Modulo Symmetries for Graph Generation and Enumeration", ACM TOCL 25(3)
  Article 18 (July 2024); preliminary CP 2021 (LIPIcs.CP.2021.34). Local: KirS_TOCL2024.pdf.
- Co-certificate learning: Kirchweger, Peitl, Szeider, arXiv:2306.10427 (IJCAI 2023): lazy learning of
  co-NP side conditions (example: triangle-free and not k-colourable). Local: arxiv_2306.10427.pdf.
- Method: CDCL (CaDiCaL) + propagator that checks lexicographic minimality of PARTIALLY defined graphs
  (MinCheck; row-wise lex order); non-minimal -> clause with nc-certificate (permutation). Complete symmetry
  breaking for fully defined graphs (each iso class exactly once).
- Ramsey results (Table 9): all R(3,5,n) (1 029 graphs, 0.24 s total) and all R(4,4,n) (3 432 184 graphs,
  883.41 s). No new Ramsey bounds; R(3,k) for k >= 6 not reported.
- Proofs: DRAT for the solver part + separate polynomial check of each symmetry clause via its nc-certificate
  (indicator pair); completeness of an enumerated list via extra "differ from each graph" clauses; canonicity of
  output graphs certifiable via a CNF M_G (UNSAT iff G canonical).
- [DuLBG] say SMS lacked a verification path in its repository (2025) and that their column-wise order has a
  property (Property 2) that SMS's row-wise order lacks. Resolved by agent sms (2026-10-24): current SMS repo
  (commit 63958bd, 2026-08) has --lrat-output and --sym-break-clauses (clause + permutation witness), but stock
  LRAT is not checkable (external clauses missing); sms patched it and a small-case chain verifies. "Property 2"
  concerns DuLBG's orderly generation, not SMS soundness. Details: notes/sms.md (agent sms).

## 5. Other relevant prior work (short)
- McKay–Zhang 1992 R(3,8) = 28 (minimum-degree extension); Grinstead–Roberts 1982 R(3,9) = 36
  ((3,8;27;80) structure lemmas); Radziszowski–Kreher 1988 R(3,10) <= 43 (e(3,k,n) bounds).
- Codish et al. 2016: R(4,3,3) = 30 by degree-triple case split + SAT (+ gluing for the hardest case);
  128 CPU years (as summarised in [DuLBG] Sec 3.2). Pattern: degree-regularity case split -> SAT per case.
- Gauthier–Brown 2024: R(4,5) = 25 in HOL4 (gluing + SAT, exact covers of generalised graphs; 2.5 CPU years,
  "44 years without generalizations") — details in cert's note.
- Codel et al. 2024: verified SR proof checker in Lean; 38-clause SR proof of R(4,4) <= 18 (from [DuLBG] Sec 3.1).
- Przybocki–Mackey–Heule–Subercaseaux, arXiv:2604.21187 (2026): doubly saturated Ramsey graphs, SAT + LLM + Lean.
- Unreviewed AI-lab work on n = 40 itself (hraness/algal-lab; unsolvedlab.com): degree-4 exclusion (LRAT),
  MTF delta >= 6 lemma, vertex-transitive/Cayley exclusion, prime-order automorphism classes, degree-6 CEGIS
  SAT runs (inconclusive at 100 000 cuts), estimates "about 10^9 core-hours for a plain SAT decision" and
  "about 3 x 10^13 core-hours for gluing at 40 vertices" (their numbers, not checked).
  See notes/symmetric_search_lit.md, notes/edge_tables.md sec 8, data/papers/algal-lab/.

## 6. What a 40-vertex non-existence proof needs (synthesis)
1. A case split covering all (3,10,40)-graphs (or all MTF ones), each case with an exact, checkable statement:
   9-regular (G_v in R(3,9,30,99) for all v) vs non-regular (some v with the table in Sec 2 above).
   Lossless restrictions available: delta >= 4 (R(3,9) = 36); delta >= 5 (degree-4 exclusion: web LRAT result,
   independently re-derived and verified by critic with drat-trim and cake_lpr, notes/critic.md Rev. 4);
   for MTF graphs delta >= 6 and diameter 2; Delta <= 9; e >= 161 ([GR] Table 5); diameter <= 3 (Pandey–Ravi Thm 3.3).
   Facts true for ALL graphs may be combined with WLOG MTF; do not combine two different WLOG choices
   (WLOG MTF adds edges, WLOG edge-minimal removes edges). Not valid under an assumed automorphism group.
2. For each case, either a census + gluing (GR/Angeltveit style, no certificate in prior art) or a SAT
   formulation with symmetry breaking whose clauses are checkable (orderly generation witnesses as in
   [DuLBG], or SMS nc-certificates), cube cover check, and DRAT/LRAT proofs.
3. Every input fact used as an axiom must be listed: e(3,9,m) values (computed by [GR], uncertified),
   uniqueness of the (3,9,35)-graph ([GR] Thm 3, uncertified), R(3,9) = 36 (certified by [DuLBG] modulo
   Graver–Yackel lemma), R(3,8) = 28 (certified by [DuLBG]).
   cert lists these as uncertified outside computations in link (g) of notes/cert_design.md.
4. Positive controls: rediscover the (3,9,35)-graph, Exoo's (3,10,39) graph, (3,10,38) circulants with the
   same encodings.
5. Scale warning: prior certified record is a 27-vertex instance; [GR] needed ~50 CPU years and [Ang] ~3 CPU years
   for n = 42 / 41 without certificates; n = 40 is believed much harder ([Ang] Sec 7).
