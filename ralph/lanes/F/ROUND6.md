# Round 6: exact relifting of fixed free-involution quotients

Allocation: two slots. Neither round-4 score-24 seed was used to generate
inputs. All results below concern labelled quotient lists, not the entire
free-involution family. There is no new n40 candidate or improved nearness.

## Reduction (hand)

Represent the free involution by pairs of consecutive vertices called
fibers. A quotient stores the presence of a vertical edge in each fiber,
and the number 0, 1 or 2 of matching orbits between each pair of fibers.
Weight two specifies all four crossing edges. Weight one specifies a
matching whose sign x is 1 for parallel and 0 for crossed. A double edge
with a vertical edge at an endpoint, or with an occupied common neighbor
of its endpoints, creates a triangle for every signing. The other possible
triangles use three distinct fibers and three single edges; they are absent
exactly when x has even sum around each such quotient triangle. Swapping
the two labels in a fiber flips its incident single signs and does not
change the vertical or double edges. Thus single-edge spanning forest signs
can be fixed to zero without losing any attainable score.

Project an independent k-set onto its fully occupied fibers D and its
singly occupied fibers S. D must have no vertical edges and no occupied
quotient edge to any other occupied fiber; no double edges are allowed
between vertices in S. For each single edge ij in S, the labels of the
selected vertices must differ by x(ij). Such a system has solutions exactly
when x sums to zero on the cycle space of the simple graph induced on S.
In that case each connected component has two choices for its root label,
including isolated vertices. Thus this support contributes exactly
2^components to the score, or zero if its parity test fails. Distinct
supports partition independent k-sets. The solver learns a support from
a concrete independent-set witness; its static D and double-edge
conditions therefore hold for all signings of the fixed quotient.

`relift.cpp` uses exact GF(2) row reduction to store the structural
constraints, support cycle tests and branch decisions. At each node, a
support whose equations are all implied contributes a lower bound. If
necessary, an ordinary independent-set walk at a representative signing
adds previously unknown supports. When the representative is over budget,
either the forced bound is too high, or at least one of the over-budget
supports has a nonconstant cycle test to branch on. The two parity branches
partition all remaining signings. At a low-scoring representative the
walk completes, so the reported score is exact. The node cap explicitly
returns `cap`, and a successful row returns only one witness, not a signing
census. `--flat` is a direct-check baseline: enumerate structural free bits
and count independent sets separately, without learning support terms.

## Controls and measurements

Logs/artifacts are relative to `scratch/F/r6`.

| Label | Scope and result | Evidence |
|---|---|---|
| enum | 162 small quotients, 872 explicit triangle-free signings; all 1,620 decisions match direct brute-force scoring across ten ceilings, with every emitted witness recounted. | `small_oracle.stdout`, `small.expected`, `small.*.reaudit` |
| enum | Two validated order-38 sources; 8 pair-removal and reattachment controls recovered, all gate-checked (31 total quotient rows, 9 no, 14 structural filters). Both deliberately switched order-38 parents admit no strict signing, but both planted reverse switches recovered and gated (96 sampled neighbor rows). | `control38fix.stdout`, `control38.gate`, `switch_control.stdout`, `switchCtl{0,1}.{mutant.log,gate}` |
| estimate | Same 16 legal n40 quotients, same ceiling 23 and same no-caps results. Lazy checks 174 concrete lifts / 894 nodes versus 260,096 direct lift checks (1,495x fewer); elapsed 0.02 vs 0.80 s on this small batch. Not a speedup for enumerating all possible quotients. | `benchmark.{stdout,lazy.log,flat.log,lazy.clock,flat.clock}` |
| enum | 1,011 labelled target quotients via appending a fiber to the two order-38 parents, with optional sampled matchings deleted. None at I10<=23: 737 completed parity refutations, 274 double-edge triangle filters, no caps. The 96-row dispersed pilot also gives no I10<=240 (67 legal). | `make_target.stdout`, `full{0,1}.{q,log}`, `final_audit.stdout`, `softpilot{0,1}.stdout`, `target_cost.txt` |
| enum (sampled input cover) | Two older n40 parents (I10=108 and 134), and 256 degree-preserving weighted two-switch neighbors of each: all 514 legal labelled inputs exhaust at ceiling 80 with no hits or caps. The full switch neighborhoods have 310 and 610 rows and were **not** searched. | `switch_prepare.stdout`, `switchTarget{0,1}.q`, `switchP{0,1}_{23,80}.log` |
| enum | Exhausted each of the one- and two-unit downward quotient layers of the two n38 parents, subject to min degree 6. Of 6,136 labelled rows, 33 admit score zero and all pass the gate. The emitted representatives are pairwise nonisomorphic and distinct from the two starting graph6 files (not compared to all known n38 graphs). 23 of 33 are from the two-deletion layers. | `sparse_prepare.stdout`, `sparse_full{0,1}.stdout`, `sparse{0,1}.gate`, `sparse.distinct.g6` |
| enum | Full Cartesian-checked one-fiber attachment quotients from those 33 positive parents give 364 labelled n40 rows, disjoint from the 1,525 earlier rows. All 364 fail at both 23 and 80; all 128 dispersed pilot rows fail at 150. No caps. | `sparse_extensions.stdout`, `sparseExtensions.new.q`, `sparse_ext_full.stdout`, `sparseExtFull_{23,80}.log` |

The downward search tests both layers directly. Filtering first-layer
failures and exploring only children of first-layer successes would not
be justified: adding back a matching might be incompatible with a newly
chosen signing even though deletion in a *fixed* triangle-free lift is
monotone for the edges. The upward search reoptimizes all signs, not only
those of the added fiber. Its completeness is for the listed marked
parent quotients and min/max degree 6..9, e in 161..180; the n40 deleted
fiber is not assumed to land in that list. The earlier blind-deletion
target pool is not exhaustive except for the no-deletion attachments.

Total: 1,889 distinct labelled n40 quotient rows checked at ceiling 23;
1,615 legal and 274 structural rejects. No family closure or proof
certificate is claimed. 21 registered jobs, 24.63 CPU seconds (0.00684
core-hours), peak two slots, no detached jobs left. The initial
`control38` stopped at a generator assertion (vertical edge omitted in
the suffix upper bound); after correction `control38fix` fully passed.
No outputs in `ralph/found`. See the job registry in `STATE.md` for
commands and deadlines.

Use this solver as a cheap exact filter if a new source produces promising
quotients. Do not scale the blind attachments or the switch tail on these
results alone. The new order-38 catalogue is a reusable byproduct; the
tested n40 promotions were not close to the existing I10=24 seeds.
