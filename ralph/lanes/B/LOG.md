# Lane B reproducibility and round 1 notes

## Sources and seed lineage

- Read Goedgebeur–Radziszowski, arXiv:1210.5826v4, §3 and Tables 3, 12–14;
  read Angeltveit, arXiv:2401.00392v2, §§3.1, 4.1–4.6. Local PDF/text copies are in `scratch/B/ref/`.
- Read-only HoG data fetched from the `data/ramsey/minramsey/Ramseygraphs_*.g6` paths of the minimal Ramsey metadirectory.
  The Exoo 39-vertex input is the **complement** of the 0/1 adjacency matrix `cs.indstate.edu/ge/RAMSEY/r3.10.39`.
- `src/bootstrap.sh` checks references, recompiles the historical gluers and `onepoint`, and rebuilds the missing order-12–15 R(3,6) classes from order 11 by one-point extension. The regenerated sizes are 116792, 275086, 263520, 64732, matching the historical file lengths. In the order-21 gluing calibration, the possible minimum degree is 3–6. Generate min-degree 3 from the 7 order-17 seeds.
- `src/seed.py small` reconstructs upstream R(3,7) windows; `upper52` reconstructs the (3,8) inputs using exactly checked GR increment inequalities. Each chunk must finish with matching input count before canonical output is published. Graph files and solver logs remain under `scratch/B`.
- `src/n30.py` is the stage-4 port of `t9_88.sh`. In `88 --prefix` mode, it checks (5:3,6:3,7:1) for cap 87 and then glues those inputs with cap 88. In full 88 mode use (5:3,6:4,7:3); the difference is the omitted n23,e52 level feeding d6 and n22,e43–44 feeding d7. Only full mode can support an exhaustive e88 claim, with all counts and scans completed.

## Correctness argument for MTF-only extension

Write the final graph as H plus the neighbours `u_i` of a new root `v`. In a maximal triangle-free (MTF) graph, every nonedge has a common neighbour. For any `x` in H outside `S_i = N(u_i) ∩ H`, the common neighbour of `x,u_i` must be in H: `x` is not adjacent to the root, and the `u_j` are independent. Thus each `S_i` is an inclusion-maximal independent set of H, not merely a subset of one. It cannot contain a vertex already of degree `DMAX` in H. Enumerating maximal independent sets in the allowed induced subgraph, then checking maximality in all of H, retains every possible `S_i`. This does not assume H itself is MTF.

Each vertex in H must get enough attachment neighbours to reach `DMIN` and at least one to dominate its nonedge with `v`. Every nonedge `xy` in H with no common neighbour in H must occur together in some `S_i`. For a chosen unsatisfied requirement, each completion therefore contains an eligible candidate from its support. Branch over that support, removing prior alternatives of this branch from later siblings (a completion goes to the first candidate it uses). Before removing the chosen candidate for later siblings, intersect the child domain with its compatibility row; this preserves multiplicity if the chosen set is self-compatible. Saturated vertex degrees remove any more sets using those vertices. If all requirements are met and fewer than D sets are assigned, branch over all eligible sets. Zero support or insufficient degrees is a valid prune.

Pair compatibility requires hitting every independent (K-1)-set left unhit by the chosen set. Each bitset row is an intersection over those hit columns, computed on demand. For a pair of attachments, the triangle-free residual on `H \ (S_i ∪ S_j)` plus the other D-2 attachments has independence at most K-2. Its order gives `|S_i ∪ S_j| >= m + D - R(3,K-1) - 1`. Higher-subset compatibility is checked by exact alpha lookups for each newly formed subset, so no independent (K+1)-set avoiding `v` survives; those including `v` are excluded by alpha(H) <= K-1. Leaf checks enforce degrees, edge bounds, and all missing internal MTF pairs. Thus `-X` is exhaustive for MTF outputs, not for all triangle-free outputs.

For the order-40 run `-m 6 -M 9 -E 161` uses report Lemmas L1, L5, M1. If full e88 is closed, it is sufficient for the reported 15 **MTF** distributions, but is not a proof of the broader statement for all (possibly non-MTF) graphs. Results are `enum`; independent SAT sample agreement never certifies UNSAT.

## Benchmark record

All times below are CPU seconds on this machine, using the same selected inputs within each pair. Exact canonical output checks on order 22 and raw/canonical comparisons are in `scratch/B/work`. `real_23_*.g6` comes from chunk outputs before final global deduplication; it is not a uniform sample over isomorphism classes.

| Sample | Baseline | Variant | Result |
|---|---:|---:|---|
| 36 × (24,e58), d5, EMAX=88 | glue5 17.22 s | gluepair 7.07 s; gluetrans 9.05 s | same 2,416 raw, identical canonical files |
| 36 × (23,e51), d6 | glue5 44.09 s | gluepair 45.61 s; gluelast 37.17 s | same 37,550 raw; weak improvement |
| 36 × (23,e52), d6 | glue5 23.63 s | gluepair 25.78 s; gluetrans 18.01 s; gluelast 18.59 s | same 2 raw; use gluetrans |
| 96 × (23,e52), d6, uniform over finished class | glue5 63.25 s | gluetrans 49.03 s | same 162 raw outputs; 1.29x |
| 30 synthetic (23,e51), d6 | glue5 32.73 s | gluecut 34.58 s; glueres 33.78 s; gluepair 24.37 s | same 67 raw; not representative |
| 30 synthetic (23,e52), d6 | glue5 18.61 s | gluecut 20.74 s; glueres 19.25 s; gluepair 22.08 s | all zero |
| 12 minimum (24,e56), d5 | glue5 9.61 s | gluefast 20.27 s | same 18,243 raw; no acceleration |
| 24 HoG e86, order-40 MTF glue | gluefast -X 6.00 s | mtfcover eager 1.09 s; mtfcover lazy 0.04 s | all zero; lazy faster than 100x on this sample |
| All 1,800 HoG e86 inputs | historical glue2 879 s (non-MTF scope) | mtfcover lazy 2.53 s (MTF scope) | zero; independent SAT C35 positive, 8/8 e86 negative |
| 40 × n30,e88 from d5 pilot | — | mtfcover 0.04 s | zero; independent SAT 12/12 e88 negative |

Fit estimates: prefix upper bound roughly (364,384 × ~1 s + 132,817 × ~0.2–0.4 s) / 16, about 7–10 hours with overhead. Full e52 stage alone at 0.511 s/input costs ~1,465 CPU-hours, or ~73 hours at 20 busy cores. A complete scan of 5.9M estimated e88 outputs at the e86/pilot e88 rates would cost roughly 2 CPU-hours, but resample the prefix before trusting this extrapolation. Long-mode budget needs <=0.27 CPU s/e52 input (or substantial validated sharing/reallocation). No justified t9<=89 or t8 launch.

## Other experiments

- `gluecut`: a witness independent set for one failed candidate must be hit by all future siblings. Correct pruning but witness construction and bitset application offset the node savings in both samples.
- `gluewin -J`: uses the degree-dependent upper GR z-cap on neighbour-degree sums. Around 2% fewer nodes in the sampled case, but no CPU win. `glueres` tightens singleton/pair/higher compatibility by a necessary minimum edge condition on the residual H plus unused attachments. Costs slightly more in the dominant sample. `gluelast` changes condition order and batches the final hitting constraint; does not improve on `gluetrans` at e52.
- `edgeup`: triangle-free one-edge extension of order-16 e21 gives 159/201 of the e22 graphs; at (24,e57) it gives 118069/129347 at e58. `irreducible` independently identifies 11278 non-deletable graphs at e58, exactly the complement count. The sampled n23,e52 had 1/36 irreducible; this is too small a sample to extrapolate. One-edge extension alone is not complete.
- `gluegroup` tries all legal one-edge additions to a common H in batches of 64 (not production). When a residual has alpha exactly the forbidden size, adding edge xy kills all such sets iff both endpoints belong to their intersection; membership is equivalent to lowering alpha by deleting that vertex. Shared search tracks possible additions as a bitmask. This passed the tiny exact independent comparison `work/group_small.{new,old}` (1035 canonical outputs), but on three n23,e51 parents (201 edge additions) it took 175.08 CPU s versus 86.10 s for separate gluing, both empty. Do not scale it.
- `gluetail -P`: if G is not a prefix output, at e88 its degree-5,6,7 vertices have neighbour-degree sums at most 29,36,45, respectively (otherwise one of the prefix roots applies). This version propagates those tighter z-caps and leaf-checks all vertices; it produced no evident throughput gain on the 36-graph e52 pilot. Experimental only, awaiting full calibration against an independent filter of nonempty outputs.
