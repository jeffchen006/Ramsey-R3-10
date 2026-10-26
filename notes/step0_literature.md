# Step 0: literature check (first pass, 2026-10-24)

## Status of R(3,10)
- 40 <= R(3,10) <= 41. Still open in DS1 revision #18 (2026-04-24).
- Lower bound: Exoo 1989 [Ex5], one (3,10,39)-graph.
- Upper bound 41: Angeltveit, arXiv:2401.00392 (v1 2023-12-31, v2 2024-04-08),
  published EJC 32(4) #P4.30, 2025-11-03, doi 10.37236/12936.
- Earlier upper bound 42: Goedgebeur–Radziszowski 2013 [GoeR1], EJC 20(1) #P30, arXiv:1210.5826.
- DS1 warns: an incorrect construction for R(3,10) >= 41 was published in [DuHu].

## Angeltveit's proof (no (3,10,41)-graph)
- Method: neighbourhood gluing extension of Goedgebeur–Radziszowski. No SAT, no proof certificates.
- (n = 41 case) Degrees in {5..9}; 41 odd, so not 9-regular.
- Prop 2.1: some vertex has G - N[v] in R(3,9,32,e<=112), R(3,9,33,e<=121) or R(3,9,34,e<=130).
  R(3,9,35,e<=139) is empty.
- Input counts: R(3,9,32,e<=112) = 1,554,928,360; R(3,9,33,e<=121) = 14,395; R(3,9,34,e<=130) = 5.
  Regular deg-7 graphs in R(3,9,32,112) came from about 150e9 R(3,8,24,63)-graphs (506 results).
- Cost: about 3 CPU years. GR2013 took about 50 CPU years.
- Checks: McKay checked completeness of R(3,9,32,e<=112). Goedgebeur shared 43,117,868 (3,10,39)-graphs.
- Author view: "obvious conjecture is R(3,10) = 40", but "not confident". Proving 40 is
  "quite difficult with current techniques".

## What this means for n = 40
- Degrees are in {4..9} (d <= 9: N(v) independent; d >= 4: R(3,9) = 36).
- Delta = 9 is forced: e(3,10,40) >= 161 [GR2013 Table 5] > 160 = 40*8/2. So 161 <= e(G) <= 180.
  (Added after critic review, 2026-10-24.)
- Hard case is 9-regular: then every G - N[v] is in R(3,9,30, e = 99)
  (e(G) = 180, e(H) = 180 - 81). Angeltveit: this set has "many orders of magnitude more graphs"
  than R(3,9,32,e<=112). So pure gluing is very expensive here; SAT is a good fit for this case.
- TODO: get e(3,9,n) and e(3,10,n) tables (GR2013, Backelin [Back1..4], Krüger [Krü])
  and write the n = 40 analogue of Prop 2.1 (degree / edge case split).

## Construction line: what is already done
- Known (3,10,39)-graphs: at least 43e6 [GoeR2, Ang1].
- GR 2012 slides (cs.rit.edu/~spr/PUBL/ber12.pdf): 37M+ (3,10,39)-graphs, 161 <= e <= 175,
  none extends to a (3,10,40)-graph.
- Angeltveit: his (3,10,38)-graphs do not extend to 40 vertices.
- So one-point extension is documented as checked only for GR's 37M+ graphs (2012 slides), NOT for all
  43,146,537 known graphs. Agent known39 re-checks the full set. A new search should leave these families.
- Circulant graphs: Harborth–Krause [HaKr1] give all best lower bounds up to 102 vertices from cyclic
  graphs; no Table Ia lower bound improves with a cyclic graph on < 102 vertices except R(3,k), k >= 13.
  So circulant (3,10,40)-graphs do not exist. General Cayley / block-circulant: not found yet (TODO).
- AlphaEvolve Ramsey paper (arXiv:2603.09172): new lower bounds for R(3,13), R(3,18), R(4,*);
  nothing for R(3,10).

## Prior art for the certificate chain (B5)
- R(3,8) = 28 and R(3,9) = 36 verified with DRAT proofs by SAT + CAS [DuLBG].
- SAT Modulo Symmetries for Ramsey graph generation [KirS] (Kirchweger–Szeider).
- Lean 4 formalization of Ramsey statements [NaSZ]. R(4,5) = 25 in HOL4 [GauB].

## Other
- Pandey–Ravi, arXiv:2601.03572: structure of hypothetical R(3,10)-critical graphs. CORRECTION (critic review):
  Sec. 3 assumes R(3,10) = 41, i.e. it IS about (3,10,40)-graphs: claims Delta = 9, delta >= 4, diameter 2 or 3.
  Proofs not yet verified by the team. See notes/edge_tables.md Sec. 7.

## Sources
- https://arxiv.org/abs/2401.00392
- https://www.combinatorics.org/ojs/index.php/eljc/article/view/v32i4p30
- https://www.cs.rit.edu/~spr/ElJC/sur.pdf (DS1 rev #18)
- https://ar5iv.labs.arxiv.org/html/1210.5826
- https://www.cs.rit.edu/~spr/PUBL/ber12.pdf
- https://arxiv.org/abs/2601.03572
- https://arxiv.org/abs/2603.09172
