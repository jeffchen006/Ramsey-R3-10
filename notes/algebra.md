# algebra: structured constructions for a (3,10,40)-graph

Author: algebra (CPUs 176-183). Started 2026-10-24. Code in `algebra/`, logs in `runs/algebra/`.
Status: IN PROGRESS (this file is filled in as runs finish).

Score of a graph = (#triangles, #independent 10-sets = c10, #independent 9-sets = c9).
A (3,10,40)-graph has score (0, 0, *). All counts by `algebra/ev.c` (tested against brute force,
`algebra/test_ev.py`).

## Split with other agents
- symsat: all exhaustive symmetric searches (Cayley order 40; automorphism of prime order p, all f).
- algebra (this file): heuristic / constructive families, plus small exact checks.
- Unreviewed web claims (see notes/symmetric_search_lit.md): no vertex-transitive and no Cayley
  (3,10,40)-graph; no automorphism of prime order >= 7. So I spent no CPU on transitive actions.

## Tools
| file | what |
|------|------|
| ev.c, ev.py | triangles, #indep k-sets (cap), alpha, greedy triangle-free fill |
| otabu.c | tabu search over a partition of pairs into classes (orbits); objective 50*tri + c10 (+W9*c9) |
| orbexc.c | exact branch and bound over unions of classes; bound: c10(current + all compatible classes) |
| subtabu.c | tabu search for the best induced m-vertex subgraph of a host graph |
| orbits.py, groups.py, mkclass.py | pair orbits of group actions (free actions + fixed points) |
| pg33.py, permgroups.py | PG(3,3) and classical groups; PGL(2,q) product actions on 40 points |
| levelset.py | non-VT algebraic graphs: u~v iff f(u,v) in S (vertices F_41^*, Z_40, Z5xZ8, ...) |
| progsearch.py | FunSearch-style program search (priority programs + greedy fill, evolved parameters) |
| ext2.py | exact SAT: extend a (3,10,n)-graph by 2 vertices |
| hit46.py | exact SAT: delete d vertices of a (3,11,n)-graph to reach alpha <= 9 |

## Calibration
- Circulants (circ.py, exhaustive): triangle-free circulants with alpha < k: n=35,k=9: 4 sets
  (incl. {1,7,11,16}); n=38,k=10: 9 sets; n=39 and n=40, k=10: none (agrees with Harborth-Krause).
- otabu finds the (3,9,35) circulant inside the Z7 class (85 orbits) in seconds to minutes (tenure 15),
  and a Z2-invariant (3,10,38)-graph (361 orbits) in < 1 min. W9 = 0 (pure c10) worked best.
- orbexc finds the circulant (3,10,38) in the Z19 class (37 classes) exactly, 57k nodes.

## Results
(see sections below)

### Exact small checks (all negative)
| check | method | result |
|-------|--------|--------|
| 9 circulant (3,10,38)-graphs + 2 new vertices | ext2.py, SAT (CaDiCaL 1.5.3 via pysat), all indep 9- and 8-sets as clauses | all 9 UNSAT (no certificate kept). Positive control: circulant minus 2 vertices re-extends (also to new non-circulant 38-graphs); (3,9,35) circulant does not extend to 37 (correct, R(3,9)=36). |
| Exoo's two (3,11,46)-graphs (data/graphs/exoo/g.3.11.46, r3.11.46): delete vertices to get alpha <= 9 | hit46.py, min hitting set of all indep 10-sets (15269 / 15752 sets), SAT + cardinality | minimum hitting set = 8 for both, so the largest induced (3,10)-subgraph has 38 vertices (40 would need 6). |
| triangle-free circulants with alpha 10 on N = 44 (5 graphs) and N = 45 (6 graphs): delete N-40 vertices | circhit.py, same SAT | no hitting set of size 4 (N=44) or 5 (N=45). By counting, N <= 44 is impossible anyway (vertex-transitive: d = N-40 deletions hit at most 10*d*c10/N of the c10 sets, need N-40 >= N/10); SAT confirms N=44. |
| induced 40-subgraphs of Higman-Sims (100 vertices, alpha 22, triangle-free) | subtabu, 2 runs x 10 min | best c10 = 78. Weak family. |

### Structure of Exoo's (3,10,39)-graph (pynauty 2.8.8.1)
- The 9 circulant (3,10,38) connection sets give ONE isomorphism class.
- Exoo39 - v is never this circulant (all 39 v), and |Aut(Exoo39 - v)| = 1 for all v.
- known39 (message 2026-10-24): |Aut| = 1 for Exoo39 and for 390,383 of 390,401 graphs of its rewire
  closure; 18 have |Aut| = 2 (1 fixed vertex + 19 2-cycles); no order 3 or 13.
  Conclusion: the known 39-region has no symmetry to generalise; symmetric 40-vertex searches are probes only.

### Prior art for program search
- Nagda, Raghavan, Thakurta, "Reinforced Generation of Combinatorial Structures: Ramsey Numbers",
  arXiv:2603.09172v5 (2026-04-21), https://arxiv.org/html/2603.09172v5 (read 2026-10-24).
  Evolved searches are annealing / tabu on edge flips with energy ~ c*K3 + I_k, seeded by circulant
  (sum-free) or Paley graphs, plus vertex-by-vertex growth (new neighbourhood = hitting set of
  independent (k-1)-sets). R(3,10) entry (Alg. 17) seeds from Paley P29; no n = 40 result, no negative
  results reported. Nothing there beyond what anneal / known39 / my lifts already do.

### Exact lift classes (orbexc, n=40, free action of a group of order 20 = 2 orbits of 20)
Branch and bound over unions of the pair orbits; no certificate (exhaustive search code, not SAT).
| group | orbits | result | nodes |
|-------|--------|--------|-------|
| Z20 | 40 | min c10 = 40 (exhaustive); start bound 1: none with c10 = 0 | 335,449 / 202,393 |
| Z10xZ2 | 42 | min c10 = 40 (exhaustive) | 523,739 |
| Dic5 | 40 | min c10 = 40 (exhaustive) | 244,117 |
| F20 = Z5:Z4 | 44 | none with c10 = 0 (exhaustive, start bound 1) | 1,012,099 |
| D10 | 50 | not finished in 600 s (tabu best 40) | - |
Tabu (otabu) reached the same minimum 40 on Z10xZ2, Dic5, F20: the two codes agree.
These classes lie inside symsat's prime-order classes (p = 5, f = 0 and p = 2, f = 0); this is an independent partial check.
