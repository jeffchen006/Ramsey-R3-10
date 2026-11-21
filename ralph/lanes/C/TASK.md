# Lane C: theory for the 9-regular case R

Start share: 4 cores (small checks, LPs, SDPs, SAT on small n only).

Case R is the core of the problem: G 9-regular on 40 vertices, triangle-free, alpha <= 9, e = 180,
every G - N[v] in R(3,9;30,99) (~1e18 graphs). Read `paper/latex/sec3.tex` (L9, Lemmas P, F, Mc, R7),
`sec8.tex` (what failed, with numbers), `notes/cases.md`, `notes/duo.md`, `notes/critic.md` (reviews).
Known: counting LPs, pair/profile LPs with (F1)-(F3), and codegree-typed LPs are FEASIBLE: they give no
contradiction. So a new lemma needs new information.

## Directions (pick, test, report; add your own)
1. **Lemmas about R(3,9;30,99) proved at n = 30 by SAT.** Every G - N[v] is a (3,9;30)-graph with 99
   edges and degrees in [2,8] (deg_H(y) = 9 - c(v,y)), sum of c(v,y) = 72, at most 9 vertices with
   c = 1, etc. (L9). A 30-vertex SAT problem is far smaller than a 40-vertex one. Find a property P
   that every such H must have (e.g. a bound on the number of degree-2 vertices, on codegree patterns,
   on independent 8-sets through a vertex) and that cuts case R hard. Calibrate on the 35-vertex
   analogue: what does the same method say about C35(1,7,11,16) - N[v]?
2. **Double counting with exact tables.** Use e(3,8,n), e(3,7,n) and the counts of small classes
   (D-C8d, D-C8e) on X = G - N[u] - N[w] for all 600 non-adjacent pairs at once; find the weighting
   that the earlier LPs missed (they used one pair at a time).
3. **Spectral and SDP bounds** for 9-regular triangle-free graphs on 40 vertices with alpha <= 9
   (Lovász theta of the complement structure, interlacing on N(v) and G - N[v], C4 counts q(v) in
   54..87, sec8.tex). A bound that forces alpha >= 10 closes R.
Every hand proof: write it out in full in `ralph/lanes/C/proofs/NAME.md`, with each step checkable,
and ask lane H to formalize short ones in Lean. A numeric claim needs a script and an exact check.
