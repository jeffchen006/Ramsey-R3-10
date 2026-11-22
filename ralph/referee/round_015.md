# Referee report, round 015 (Claude Opus 5.5, agy; fresh session)

There were no earlier referee reports (`ralph/referee/` was empty; rounds 9–14 failed or were blocked by quota), so no
claim had been reviewed by a non-GPT referee before. I chose four claims: three new claims from round 14 that rest on hand
reductions (C-038, D round-14 WING_RIDGE, F round-14 / F-025), and the floor with the most dependants (N-003, with
its consumer N-004). My checks used at most 2 cores and about 9 CPU-minutes in total, all under `nice -n 5 timeout`, with
cwd `scratch/referee/`. All scripts and logs are in `scratch/referee/r15_*`.

## 1. N-003 (+ N-004): MTF degree-six residue floor e(G−N[v]) ≥ 122. Verdict: **SOUND**

Steps re-derived by hand:
- **Rows.** For u ∈ N(v), N_H(u) is independent (triangle-free). It is also maximal: a vertex w ∈ H∖N_H(u) is nonadjacent to u,
  so by MTF it shares a neighbour with u, and that neighbour cannot be v. Correct.
- **Demands.** Every w ∈ H lies in some row (MTF at the pair v,w). Every H-nonedge with no common neighbour in H has its
  common neighbour in N(v). Correct.
- **Pair rule.** Two anchors that both miss an independent 8-set give an independent 10-set. Two rows that share a vertex
  with d_H = 8 push its degree to 10. Both correct. The support-deletion induction ("the true row covering D is still
  available") is sound.
- **Completeness.** Angeltveit §3.3 (`scratch/H/ang-2401.00392v2.txt` l.141–151, l.290) lists |R(3,9,33,e≤121)| = 14 395.
  §3.2–3.3 say R(3,8,27) was glued as well, so the census does not drop vertices of degree 5. The count is therefore the
  total. I considered whether "partial census" meant a restricted class. It means truncation by e only.
- **Consumer (N-004).** Private cells satisfy |P_u| ≤ 4, because N(v)∖{u} ∪ P_u is independent. Hence
  Z = 6 + Σ_w c(w) ≥ 6 + 33 + (33−24) = 48, and e ≥ 170 at a d6 root. Key (170,2,7,0,31): the degree sum 340 checks. Equality
  forces Z = 48. The second d6 vertex is adjacent to v (G-021) and n8 = 0, so the other five neighbours have odd degree
  and Z = 6+6+odd is odd. Contradiction, correct. G-021 itself depends on G-019 (enum), which I did not re-check this round.

Independent checks (`scratch/referee/r15_floor122.py`, my own encoding written from the statement, not from N/G code):
- **Census.** All 14 395 rows of `scratch/ideas/r012_N/unionall.g6` have n = 33, are triangle-free, have α ≤ 8, and have
  e = 118/119/120/121 with counts 5/69/1223/13098. Zero bad rows (`r15_census.log`). nauty `labelg`: 14 395 distinct canonical
  forms. All 17 rows of `test17.g6` and all six of `handoff.g6` occur in the union.
- **Extension SAT.** Six rows, each independent and dominating, |row| ≤ 8, d_H+mult ≤ 9, vertex and nonedge demands,
  independent 8-sets missed by ≤1 row and 7-sets by ≤2, lex order on rows. **Positive control:** the F-003 (3,10,39) seed,
  made MTF; the residues of its degree-9 and degree-8 roots are SAT (`r15_cal.log`). **All 17 gap rows: UNSAT**, each in
  ≤0.7 s (`r15_test17.log`). **Random sample (seed 15) of 60 of the 14 395 rows: 60/60 UNSAT** (`r15_sample.log`,
  indices in `r15_sample_idx.txt`). These are solver answers without proofs, so the label is enum. They corroborate the
  claim but do not replace the producer LRATs.

## 2. C-038 (cover in `panel17_census.md` + rules in `reciprocal_panel17.md`). Verdict: **SOUND** (prefix scope)

- **Exterior split.** No exterior vertex meets both A and B (triangle with an A–B edge). F_A = P_B ∪ Z and F_B = P_A ∪ Z;
  α(F_·) ≤ 5 (add the avoided 4-set). By R(3,6) = 18 each window has ≤ 17 vertices. |F_A|+|F_B| = 32+|Z| gives |Z| ≤ 2,
  and |Z| = 2 iff the windows are 17/17. Correct.
- **Marks.** Each mark N(a)∖B is an independent 5-set; two marks meet in ≤1 site (codegree 5 minus the 4 shared in B).
  Excess incidences 20−15 = 5 and at most 6 pair slots. I re-derived the case analysis: no site of multiplicity 4 and no two
  triple sites. Singleton counts are 3,3,2,2 (slot graph K4−e) or 3,3,3,2. Hence every frame has ≥2 three-site groups.
  Correct.
- **Restoration.** V(F_{A∖a}) = V(F_A) ⊔ {a} ⊔ S, with α ≤ 6. For J ⊆ S the test α(F_A − ∪M_x) ≤ 6−|J| is exact.
  |M_x| = 8 − |N_{F_B}(x)∖Z| follows from 9-regularity. Correct.
- **Headers.** Private degree sums are equal (both equal 135−20−e(P_A,P_B)). Neutral degrees sum to 9 + [z1z2]. The neutral
  codegree sum is ≤ 5, and Z contributes no common neighbour. Two maps on Z. All necessary.
- **Code read (`ralph/lanes/C/panel17.cpp` l.103–107, 149–179, 311–353, 375–440).** The local neutral-codegree test splits
  the count into origin *private* neighbours (holes masked out) plus the row on the target. A neutral common neighbour is
  therefore not counted twice. I checked for this double count specifically and it is not there. The mark test ≤4 is
  correct (common root a counted once). Same-group +1 is correct. The terminal leaves only the P_A×P_B cross edges free.
  Upper adds an edge only if there is no common lower neighbour. The independent-10 test on upper, codegree/triangle on
  lower, and forced/forbidden degree-9 propagation are all monotone. Sound.
- **Not checked.** The two scanners and the full roster; the critic replayed those. Scope: prefix `[0,24576)` only.
- **Side exchange.** The (i,j,b)↔(j,i,b) transfer that the critic plans (LATEST, A.1) is valid only if every header,
  local and terminal test is symmetric under A↔B. The header (`agrees`) is symmetric. The `local_domains` direction
  (origin→target) must be run in both directions, or shown symmetric, before the transfer is used.

## 3. D round-14 WING_RIDGE (t ≥ 13 at every deficient pair; t ≥ 16 at some). Verdict: **SOUND** (hand steps; LRAT/LP not re-run)

- **Setup.** In a 9-regular graph, MTF holds automatically (Δ ≤ 9), so every nonedge has codegree 1..3. Each A–B edge gives
  a distinct induced pentagon through a−h−b, and conversely. F has a perfect matching, else α(F) ≥ 9 and h is added.
  Degrees ≤ 3 and row overlaps ≤ 2 hold. Correct.
- **Forward-closed 8-sets.** z ∉ N(h) misses some 8-set iff the forward closure of R misses L. So z needs a return pair,
  and i ≠ j because the matching edge would close a triangle. 21 sites lie outside, 7 of them in N(h). The per-site budget
  8−d_F, the pair use ≤ 3 (cap) and the cut formula are all correct.
- **Orbit count.** 8!·#PM/|Aut_bip| for words containing the identity matching is correct. 84 = 59+1+19+5 checks against
  the table.
- **§2.** |S1| = k, |S2| = 18−2k, |S3| = 12+k (from 72 two-walks and 30 nonneighbours). t = 24−2x−y via c(u,b) = d_F(u).
  The bounds l_i and the α-mass bound are correct. **Recount** (`scratch/referee/r15_dmass.py`, geng −t, orders 1..9):
  2 479 graphs, **2 469 fail the mass tests**, and the 10 survivors are exactly A_ (two adjacent singles) plus shapes with
  codegree > 3 or K3,3 (K2,4, K3,3, …), as claimed (4+5+1).
- **Rigidity.** Two adjacent D-partners give c(b,v) = 3 − [v ~ a or c]. Each wing has degree sequence 1,2^7 per side. I
  recounted the path/cycle types: **15**.
- **§4.** Each exterior vertex sees exactly one pentagon site (35/35). Codegree 2 or 3 gives exactly 2 neighbours in every
  other fiber. The seed {i, i+2} leaves three fibers with α ≤ 7. Correct reduction to the 4 LRATs.
- **Not re-checked.** §3 (the 499 duals and 152 conflicts) and the 9 LRATs. Scope: max nonedge codegree 3, i.e. R(3) only.

## 4. F round 14 (F-025 ID15; IDs 43/81 have ≥36 tens). Verdict: **SOUND** (43/81 independently verified; ID15 hand steps only)

- **Convention.** Triangle-freeness on a quotient triangle means Σx = 0; I re-derived this. Indicator of a support =
  ∏(1 + cycle sums) over a fundamental cycle basis. An XOR ≡ 1 forces at least one active support for every signing and
  every vertical pattern. Poles cannot remove old independent sets.
- **Independent check** (`scratch/referee/r15_fxor.py`). I wrote my own parametrisation of the triangle-free subspace of
  C18(D) (63 quotient edges) and expanded in exact ANF. **ID43:** the 7 masks in `seven43.witness` (all rank 2) XOR to
  exactly 1. **ID81:** the 35 masks in `cube81.witness` (7 rank-2, 28 rank-3) XOR to exactly 1. **Mutant control:**
  dropping one ID43 mask gives a polynomial with 46 monomials, i.e. not 1 (`r15_fxor.log`). So IDs 43 and 81 are excluded
  outright under the cyclic-card premise; "≥36" is the stronger counting statement.
- **≥36 counting.** 36 dihedral copies, each with an active support. A support with c components has 0 or 2^c transversals.
  The multiplicity per support is ≤ 2^c (producer integer count; I checked the argument, not the count).
- **ID15.** The hand steps are fine: per-site gauge flips for one column; two contacts at a site sit on opposite endpoints;
  a third is impossible (degree 8 + 1). I did not re-run the 693-mask elimination or the 54-term XOR.
- **Scope.** Only the cyclic inter-pair multiplicity-one 36-card premise (F-023), not free involutions in general.

## Advice
1. N-003: my independent encoding agrees on all 17 gap rows and on 60 random rows. Upgrading the remaining
   14 378 "old" rows to unpinned proofs is not needed for soundness, but a full independent no-pin SAT sweep would take
   about 1 core-hour with this script, if anyone wants a second-family enum over the whole family.
2. Before A/C use the side-exchange transfer, check that `local_domains` and the transposition test are run (or are
   equivalent) in both orientations; the header check alone is symmetric.
3. D: the global-cap assumption (max codegree 3) must stay attached to every downstream use of "some t ≥ 16".
