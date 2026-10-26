# known39: one-vertex extensions of (3,10,39)-graphs (final, 2026-10-25)

Stopped 2026-10-25 by lead decision (published results trusted). No (3,10,40)-graph found.

## Scope (read this first)
The GR/Angeltveit set of ~43M (3,10,39)-graphs is NOT public; the user decided to use public data only.
So everything below is about MY sets: rewire closures of Exoo's graph and of anneal's graphs.
Overlap with the GR set: unknown. The gap for the GR set (critic) is not closed by this work.

## Data
- Exoo (3,10,39): cs.indstate.edu/ge/RAMSEY/r3.10.39 is the 0/1 matrix of the COMPLEMENT.
  data/graphs/exoo/exoo39.g6: n=39, e=167, degrees 6^1 8^14 9^24, |Aut| = 1, 4511 independent 9-sets.
- (3,9,35) (McKay r39_35.g6): |Aut| = 210, vertex-transitive. HoG (3,9,34,129): |Aut| 6; (3,9,33,118): 2 or 6.

## Method
- G + w with N(w) = S is a (3,10)-graph iff S is independent and meets every independent 9-set of G.
- Rewire of vertex v (G - v + w): same test with the 9-sets that avoid v.
- known39/bin/k39 (C, known39/src/k39.c; nauty 2.8.9 compiled in): exact branching hitting-set search;
  `bfs` = closure under rewires with nauty canonical dedup; every graph tested for extension to 40.
- Validation: own Python/CaDiCaL check (src/sat_ext.py) agrees on Exoo and 300 random closure graphs;
  positive controls (all 39 Exoo-v extend; (3,9,35)-v extends with k = 9; (3,9,35) does not);
  each found extension re-verified by brute force; dedup count checked with labelg (nauty 2.9.3).
- No proof certificates.

## Results
| set | graphs tested | extend to 40 |
|-----|---------------|--------------|
| Exoo rewire closure (stopped, NOT complete: 18.4M expanded of 25.3M known) | 18,425,985 | 0 |
| 33 other complete rewire components (anneal seeds + two-vertex-rewire seeds), sizes 4..10,984, disjoint from Exoo closure | 28,121 | 0 |
| 9 labelled (3,10,38) circulants -> 39 | 9 | 0 (no extension to 39) |
- Edge counts seen: 162..175. |Aut| in Exoo closure: 1 (18,421,216), 2 (4,767), 3 (2).
- Each anneal random-start 39-graph gave a new component; 2 (anneal seeds 16, 18) joined the Exoo component.
- Two-step moves 38 -> 40 (delete 1, add 2) = one rewire + one extension: covered for every expanded graph.
- One-triangle 40-graphs (Exoo 2013 class, alpha <= 9): none from the first 20,000 Exoo-closure graphs.
- Near misses (best new vertex): minimum 23 independent 10-sets in G + w (heuristic; exact MaxSAT agreed
  on the top 11 checked earlier). known39/out/nearmiss_final.txt (86 lines, unmet <= 30), older *_partial.* sent to anneal.

## Files
runs/known39/bfs_exoo/{all.g6,results.txt}, runs/known39/comp_*/, runs/known39/bfs_ann1/, known39/out/.
