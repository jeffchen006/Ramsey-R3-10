# Four frozen stars for two disjoint codegree-one pairs

`DEFECT_MATCHING.md` supplies existence of the two pairs (hand + enum,
submitted for review). Mark them as (0,1),(2,3). All four stars are
frozen. This is a cover of graphs, **not** a disjoint partition of
unmarked graphs. Unmentioned pairs may have codegree one as well.
The within-pair edges are absent; the cross edges form an arbitrary
2-by-2 binary matrix. The all-ones matrix already violates the two
codegree-one conditions. Quotient by swapping endpoints of either pair
and interchanging the two pairs (order eight), not by arbitrary S4.

The exterior mask multiset has 36 slots, four exact degrees, two exact
codegrees one, all other nonedge codegrees 1..3, and no mask hitting a
core edge. `defect_four.py` enumerates multisets of masks of size >=2,
then gets singles and empty cells by subtraction. `four_witness_audit.py`
instead places each distinguished common neighbor (possibly the *same*
exterior witness for both pairs, or an internal witness). Once these
witnesses are placed, only singleton and **cross-pair** double masks
remain. The independent labelled counts and all canonical input bytes
agree. Both counts are incidence counts, not graph counts.

| Cross shape | All four-star keys | After direct I10 test | At K=2, capped at 5,000 |
|---|---:|---:|---:|
| 0 (none) | 123 | 66 | 34 |
| 1 (one edge) | 57 | 36 | 19 |
| 3 (two sharing an endpoint) | 6 | 6 | 3 |
| 6 (two independent edges) | 6 | 6 | 3 |
| 7 (three edges) | 3 | 3 | 2 |
| **Total** | **195** | **117** | **61** |

The source is 1,164 labelled four-star profiles. All 78 removed on the
unrestricted arm already have an independent ten in the most generous
graph allowing every free exterior edge not blocked by a common frozen
neighbor. No need to trust node search for these exclusions.
`four_obstructions.py` records all ten labels and one frozen triangle
witness for each of the 45 pairs not directly pinned absent. It emits
a small CNF with four fixed stars, the listed triangle clauses, and the
single I10 blocking clause. All **78/78** have independently accepted
CakeLRAT and lrat-check artifacts. These are formula-level certificates
for marked roots; the 195-key cover and the structural matching
reduction are not a Section 7 certificate of unrooted R(3).

Evidence root: `scratch/D/ind10`. `four-direct.log`, `four.log`,
`four-certs/{witnesses.tsv,certificates.tsv,cal.log}`, `four-open-live.in`.
C22: 1,056 labelled / 172 orbits, 2,264 physical disjoint-defect-pair
marks. Complete graph-only search recovers exactly the 54 occupied
profiles and all **349** individually coloured graph classes. All 54 pass
the direct I7 test; it rules out 91 of the 172 incidence profiles. No
C22 graph in this cap/degree stratum has only two deficient pairs.

**Boundary of the experiment.** Unrestricted 650-node runs exhaust
exactly those 78; all 117 other cases cap. No plain restart justified.
If the *entire graph* has exactly two deficient pairs, both are disjoint
by the matching result. Both exact slots are spent in the four frozen
stars, so other nonedges need at least two witnesses. This separate
5,000-node pass exhausts 134/195 (including the unconditional exclusions).
Of nine spaced tail inputs at 40,000, only one terminates (32,756 nodes),
eight hit the node cap. Thus 60 of the original 61 tails remain
unresolved after that extra pilot; there is no K=2 exclusion.

For an independent signed-colour pilot, let L be the **known** two-pair
adjacency, H the indicator of nonedge codegree three. Then
`A²=7I−2A+2J_all+H−L` and `AH−HA=AL−LA`. At the four-star root the right
side is exactly known everywhere because every endpoint of L has a
complete star. H has row degree `12+deg_L(v)`. The strengthened two-colour
intersection search on the same nine used 21.59 CPU-s even at 5,000
nodes, again closing only the first case. Correct planted colour domains
on 156 full/random/empty fixed-star sets across all three C22 graphs
(`signed-cal.log`). No speedup; do not scale these two pilots unchanged.
