# Review of the R(7) exclusion (claim C-004), by Claude Opus 5.5, 2026-11-21

Verdict: no gap found. Label stays `cert (custom trace)` + this independent `enum` re-check; not Lean, not LRAT.

1. Hand reduction `ralph/lanes/C/proofs/pair_packing.md`: each step re-derived (mask sizes 6/7,
   one C-neighbour per X vertex, disjoint side unions, union meets every independent 7-set,
   same-side overlap <= 4, D-sets from maximality, C masks distinct with overlap <= 5, the
   independence budget 2 - max(missA, missB), required pairs, first-present branching). All are
   necessary conditions; swap of u,w makes unordered package pairs valid.
2. `ralph/lanes/A/r7_audit.cpp` read in full: the cover filters and the replay rules match 1.
   Rebuilt and re-ran here: 977,008 trees, 49,569,079 nodes, all VERIFIED.
3. Own program `r7_independent.cpp` (no trace input, MRV branching, full 40-vertex graph test on any
   complete list): same package counts and the same 261,824 / 261,586 / 226,943 / 226,655 pairs;
   0 complete lists, 0 graphs; 47.2 M nodes, about 106 CPU-s (`r7_independent.log`).
   Calibration that can fail: in the 10 6-regular (3,7,22) graphs, 7 have this shape (cap = d-2);
   the program finds each graph's own completion in all 7.
4. Seeds: McKay's r38_27.g6.gz (477,142 graphs) has exactly 4 graphs at e = 85 (also the minimum);
   their invariant fingerprints equal those of the 4 seeds in `scratch/A/r7-proof-v1/r38_27_e85.g6`.

Premises not re-checked here: Lemma R7 itself (earlier project, Lean r7_count / r7_cover) and
Lemma Mc. Both programs use the same necessary conditions, so an error in the reduction would be
shared; step 1 is the guard against that.
