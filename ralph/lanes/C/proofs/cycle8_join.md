# Overlapping census windows for the codegree-six eight-cycle

**Status:** enum in R(6); depends on the published census of all 191
graphs in R(3,7;22), and on the structural proof in `codegree_six_paths.md`.

Suppose the codegree-six graph of a Case R(6) model has an eight-cycle.
The structure proof gives eight independent consecutive triple windows:
each anti-neighbourhood comprises the same X on sixteen vertices, plus
three consecutive pairs of boundary vertices (six independent vertices).
Assign an orientation to the cycle. One window in the full 22-census can
be relabelled to each actual window. Conversely, the following projection
can only overestimate what the actual windows allow:

1. For each census graph H and each of its independent six-sets S,
   remove S. Keep the resulting X only if it has max degree at most four
   and 24 <= e(X) <= 32. Also reject if the vertices of S consume more
   than 2*(e(X)-24) units of B-degree: the exact B-degree of b in S is
   6-deg_H(b), and 2*(e(X)-24) is the total B-degree across all 16 slots.
2. Group resulting X by graph isomorphism (nauty `labelg`). Fix one
   labelled representative in each group. Enumerate every isomorphism
   from each occurrence to the representative. For every map record the
   six bitmasks of neighbours of S in X in this common labelling.
3. Partition those six vertices into three unordered pairs; consider
   all 15 matchings and their 6 group orders. Let a type be the sorted
   pair of masks for its two vertices. For two vertices from the same
   type, adjacent types, or types at distance two in the window,
   their common-neighbour count among the eight roots is 3, 2, or 1,
   respectively. Thus their X-mask intersection size is at most 3, 4,
   or 5, respectively, by the global codegree cap six. All nonnegative
   contributions from other B vertices are ignored. Save the allowed
   ordered triples of types into a window library.
4. Any model gives a cyclic word T_0,...,T_7 of types, every consecutive
   triple (including wraps) in this library for the same X. For each
   vertex x of X, the eight types together contribute exactly
   9-deg_X(x) neighbours by regularity and the absence of X--root edges.
   Check whether any such word exists. No requirement is imposed on
   B--B edges, so nonexistence suffices to exclude the cycle.

Two searches check step 4. The first follows the triples as a directed
overlap on pairs, rejecting a prefix only when it overspends a vertex
load. It tries all initial pairs that are both a prefix and a suffix of
some library triple. At depth eight it checks the two wrapping triples
and the load equality. The meet-in-middle check lists all internally
admissible length-four words. Two such words must have complementary
load vectors, and all four joint triples must be allowed. Each vector
uses a base-32 encoding with one digit per X vertex: the sum of loads is
at most 16 per vertex, so no carry can mask a coordinate disagreement.
The searches agree in all 32 X families and on brute-forced toy models.
There were no complementary half-word loads even before checking the
four joining triples. For each X, a small subset of vertex coordinates
already detects this. The obstruction verifier recomputes the load tuples
restricted to the specified coordinates and checks exact noncomplementarity.

Evidence: `cycle8_profiles.py` reads the 191-census and emits
`scratch/C/cycle8_candidates.tsv`; `cycle8_join.py` consumes that table
without `--limit` for the full test. Logs `scratch/C/cycle8_profiles.log`,
`scratch/C/cycle8_join_double.log`. No claim is made about path components.
