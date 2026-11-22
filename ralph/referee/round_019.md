# Referee report, round 019 (Claude Opus 5.5, agy; fresh session)

Only one earlier referee report exists (`round_015.md`: N-003/N-004, C-038, D WING_RIDGE, F-025, all SOUND). I did not
review those claims again. This round I chose three new round-18 hand reductions (scout R's fifth-pole lemma, scout N's
selector reduction and grid bound, and G's `middle+middle.2` transport) plus G-019. G-019 is the floor that the most
claims depend on (n6≤2, and with it every e168–e170 two-root argument). It has no non-GPT check on record: an old
referee script exists in `scratch/referee/` but no log or report. All checks ran under `nice -n 5 timeout`, with cwd
`scratch/referee/`, ≤2 processes at once, about 5 CPU-minutes in total. Scripts and logs are `scratch/referee/r19_*`.

## 1. Scout R round 18: fifth-pole lemma at |H|=13 (critic: 56 structural exclusions). Verdict: **SOUND**

Files: `review/ideas/r018_R.md`, `ralph/critic/round_018.md` §R. I re-derived each step:
- **Setup.** In cap-five Case R, a site x in three marks of a `K4,4` (roots a1,a2,a3 on one shore) gives `K3,5` with
  A={a1,a2,a3}, B=B0∪{x}. Cap 5 makes the A-pairs share exactly B, so the three sets N(ai)∖B (size 9−5=4) are disjoint.
  They are independent and miss B (triangle). H = the exterior vertices with no B-neighbour. α(H)≤4 (add B, |B|=5), so
  12≤|H|≤13 (R(3,5)=14), and |H|=13 forces C13(1,5). The exterior has 32 vertices, so |Q|=32−|H|. Correct.
- **Incidences.** Each pole b has 3 neighbours in A and 6 outside A∪B, all in Q by definition, so Q carries 30
  incidences. For b, the vertices outside B∖{b} with no neighbour in B∖{b} are exactly H∪{b}∪S_b. A has full
  B-adjacency, so A is excluded. α≤9−4=5. So |T| = 14+s_b ≤ 17, and s_b=3 gives a 17-vertex (3,6) graph in which b has
  degree 3. Correct.
- **Degree fact.** `gluing/val/r3_6_17.g6`: 7 graphs, all triangle-free, α=5, min degree 4 (`r19_r36_17.log`).
  Independent check without the catalogue (`r19_deg3.py`): v of degree 3 forces G−N[v] = C13(1,5). Among all 3-multisets
  of its 183 independent sets as neighbourhoods of N(v), **0** give α≤5 (`r19_deg3.log`). So s_b≤2.
- **Counting.** Σ|supp| = s + 2(19−s) + E = 30 gives s = 8+E ≤ 10, so E≤2. Correct.
- **Application.** For a triple site x in the 16-window W=F_B (x ∈ P_A, d_W(x)=2): H consists of the vertices of
  P_A∪Z = W that are neither x nor adjacent to x, so |H|=16−3=13. The fourth root a4 is not adjacent to x (x is exactly
  triple) and sees all of B0, so it is a Q-site with support exactly 4 and takes E=2. A triple site y ∈ P_B of the
  opposite frame sees ≥3 poles of B0, so E≥3. That is a contradiction, and no crossing edge is needed. Correct.
  The scope is |H|=13 only, as the critic stated.

## 2. Scout N round 18: selector reduction (h=8, fixed left shape) and the grid bound. Verdict: **SOUND**

Files: `review/ideas/r018_N.md`, `ralph/lanes/G/rows/{e170_aligned_grid,e170_equality_signatures,signature_matchings}.md`.
- **Private-cell matching lemma** (the basis of G-043 and of the grid bound). Take P_i,P_j (4 each) in the root-u residue.
  An independent I ⊆ P_i∪P_j joins A∖{i,j} (4 anchors), so |I|≤5. A double ij (when present) is isolated from both
  cells, so |I|≤4. König's theorem gives ν≥3+[ij∈J]. At adjacent roots, P_v = V∖{y}, and the double {i,v} exists iff i=x.
  This gives the matching from L_i's private sites to R∖{R0} of size ≥3+[i=0]. Correct.
- **Grid bound.** Private/private sites in one column all match only R_j, so they contribute ≤1 per distinct noncross
  column (≤t). The 4−s sites with an R-double support contribute ≤1 each. Hence 3+[i=0] ≤ t+4−s, i.e. s−t ≤ 1−[i=0].
  Column-0 sites count in s but not in t, which keeps the bound valid. The transpose follows by wing exchange. Correct.
- **Independent board count** (`r19_boards.py`, my own enumeration from the stated rules: M00=0, margins, row/column
  bounds). h=8: **24 labelled boards, 1 orbit** under S4×S4×transpose (this is the off-diagonal grid). h=7: **1,296
  labelled, 6 orbits**. Both match `burnside.cc` (`r19_boards.log`).
- **Selector CNF semantics.** Padding: from the unused anchors A,B plus u,v, the maximum independent set is
  max(|A|+|B|−[0∈A∩B], 1+|A|, 1+|B|). Here u misses R and v misses L, the only wing edge is L0R0, and u~v. Correct.
  MTF demands for empty cells (i,j)≠(0,0) can only be met by a selected site: roots, anchors and grid sites cannot
  supply them. Edges of z only to grid sites disjoint from its support, and no z–z′ variables: this is a relaxation
  and asserts no nonedge. A guarded blocker needs ≥10 independent vertices. The any-right variant (≤1 per right pair,
  8 left slots) covers every right hole list, including lists the cross-endpoint rule would already reject. Sound as a
  necessary relaxation. I did not re-run the LRATs or the 17-scheme crosswalk; the critic did.

## 3. G round 18: `middle+middle.2` excluded at h=8 by transport. Verdict: **SOUND**

Files: `ralph/lanes/G/rows/e170_middle_2_stabilizer.md`, `ralph/lanes/G/ROUND18_REPLAY.md`.
- **Actions.** Holes L0L3, L0L4 / R0R1, R0R2. A simultaneous σ on {1..4} that keeps the shores must fix {3,4} and {1,2}:
  4 actions. One that exchanges the shores must swap them: 4 actions. Every action fixes 0, so it keeps L0R0, the
  off-diagonal grid and the diagonals {Li,Ri}. Transport is anchor relabelling plus (for the swap) exchanging u,v. Site
  incidence, the one wing edge, triangle clauses and the anchor-independence of every ten-block are all preserved, so a
  destination completion pulls back to a source model. Monotone restriction to a smaller retained double set is valid.
  This is not a symmetry-breaking WLOG combined with other constraints: every ID is covered by an explicit image.
- **Independent roster** (`r19_mm2.py`): bijections from the 8 left doubles to the 8 right doubles, with no site holding
  both L0 and R0 and every diagonal i=1..4 covered. Result: **16,350 IDs**, 8 actions, nonidentity fixed counts
  {256,256,50,0,0,0,0} and **2,114 orbits**. All match G's report exactly (`r19_mm2.log`). I did not re-run the 2,024 LRATs
  (critic did).

## 4. G-019 (+ G-021 consequence): no degree-five vertex in a degree-six residue; n6≤2. Verdict: **SOUND** (hand); enum corroborated

Files: `ralph/lanes/G/rows/no_degree_five_residue.md`, `ralph/lanes/G/root_certs/{d5_order27_survivors,d5_order33}.g6`.
- **Hand.** H=(3,9;33) has Δ≤8. A vertex of degree ≤4 leaves ≥28 vertices with α≤7, contradicting R(3,8)=28.
  A degree-5 x gives Q=(3,8;27) (477,142, pub). The MIS gluing tests over |T|≥2, avoiding independent (a+1−|T|)-sets,
  are necessary and sufficient. They are monotone, so maximal columns suffice. The outer step glues the degree-six root
  of G onto H with a=9, d=6; 1+6+33=40, so G is fully determined. Consequence: d_H(w)=d(w)−c(u,w)≥6, so c≤t−6. Two
  nonadjacent degree-6 vertices would have c=0, which MTF forbids; so the degree-6 vertices form a clique and n6≤2.
  This uses MTF only in the last step, as the file states. Correct.
- **Checker read.** `check_g019.c` (an older referee checker, shares no code with G). I read the MIS enumeration
  (each MIS exactly once, by increasing order), the crit sets (all independent (A−1)-sets are maximum, so maximal), the
  pair-compat via avoid masks (repeated columns allowed), the subset tests at |T|≥3 on the newest column, and the
  multiset order. All correct.
- **Runs** (`r19_g019.log`). Calibration on (3,7;22): 948/948 degree-5 residues and 220/220 6-regular residues survive
  as they must, and D=7 rejects 0/220 (it can fail). **Outer: all 984 order-33 classes rejected at (A=9,D=6)**,
  33.6 CPU-s. Inner: two disjoint dispersed samples of r38_27 (A=8,D=5): 19,881 cores give 2 survivors, both in the 118
  (`r19_g019_inner.log`); 39,762 more are in `r19_g019_inner2.log` (see below). A full inner pass (~21 CPU-min) is over
  my budget, so the completeness of 118 rests on G's two implementations plus these samples: enum, not cert.
- **Not checked:** the 118 → 984 expansion (glue6 and the C++ deletion enumerator). It is the remaining single point
  that only GPT-side code has checked.

## Advice
- No GAP this round. R's lemma is safe for |H|=13 only. Do not reuse it at |H|=12 without a new degree argument: the
  order-17 window bound becomes order 16 there, and the deg-3 contradiction disappears.
- G-019's 118→984 step is the last GPT-only link under n6≤2 (critical for every e168–e170 result). A cheap independent
  re-expansion of the 118 cores (≤1 core-h) would be worth one lane-A slot.
- Not scored this round: C-044. I read `proofs/panel18_signed_join.md` (residue = opposite window ∪ {a} ∪ S, row sizes
  8−d+1_{s~z}, hitting sizes 7−|J|, pairwise agreement suffices because each coordinate lies in ≤2 groups). I found no
  issue, but I did not re-run the joins (opaque header encoding).
