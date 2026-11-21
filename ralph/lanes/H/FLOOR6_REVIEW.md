# Degree-six floor and distribution audit — round 4

**Scope:** G-009/G-010 are `cert` for maximal triangle-free (MTF) graphs.
The hand/Lean steps below do not themselves certify the published class
counts, the graph6–DIMACS bridge, or the finite proof coverage.

## Exact cover and binding

For an MTF triangle-free graph `G` of order 40 with `alpha(G) ≤ 9`, fix
a degree-six vertex `v`. Write `A=N_G(v)`, `H=G−N_G[v]`. The deleted
set has size 7, and any independent nine-set in `H` would extend by `v`.
Thus `H` is triangle-free of order 33 with `alpha(H) ≤ 8`.

Goedgebeur and Radziszowski, *New Computational Upper Bounds for Ramsey
Numbers R(3,k)*, EJC **20**(1), P30 (2013), DOI `10.37236/2568`;
[arXiv:1210.5826v4](https://arxiv.org/abs/1210.5826v4), Tables 4 and 14,
give the exact minimum 118 and the exact isomorphism counts 5 and 69
at 118 and 119. I checked the table rows directly. In the same table,
33/120 is **at least 1,223**, not an exact published count. Angeltveit's
aggregate through 121 does not by itself give the split at 120/121.

`ralph/lanes/G/root_certs/complete33_le119.g6` supplies all 74 because
each entry has the required properties and the per-level distinct class
counts attain the published totals. No guarantee about the completeness of
replacement moves is needed. Its pinned SHA-256 starts `5fbaa07318ee`.
`ralph/lanes/G/replay_floor120.sh` binds the ordered catalogue to the 74
regenerated DIMACS files and proofs via `floor120_inputs.sha256` and
`floor120_dimacs_lrat.sha256`; `scratch/critic/r3-G120.log` records the
critic's full replay with both LRAT checkers. A's independent package
`ralph/lanes/A/FLOOR_AUDIT.md` checks the canonical overlap with the 68-row
snapshot, the six disjoint new rows and an independent CNF reconstruction.
H did not rerun that byte-binding work or generate any proofs.

## Necessary-clause and private-cell hypotheses

Transport a hypothetical extension through any isomorphism from `H` to
its supplied representative; order `A` arbitrarily as the six CNF columns.
For each `a∈A`, let `S_a=N_G(a) ∩ V(H)`, and assign the incidence bits
according to membership. Then:

1. Triangle-freeness makes each `S_a` independent. For any exterior
   nonneighbor `x` of `a`, maximality supplies a common neighbor of `a,x`.
   It is not `v` since `x` is exterior, and it is not in `A` since `A` is
   independent. So `S_a` dominates `H` (closed domination).
2. Maximality for `v,x` puts `x` in some `S_a`. The only additional
   neighbors of `x` beyond `H` lie in `A`; the neighborhood is independent,
   so its degree is at most nine. Cap the number of incidences at
   `9−d_H(x)`. This is not a minimum-degree constraint on `H`.
3. For distinct nonadjacent exterior `x,y` with no common neighbor in
   `H`, maximality supplies one in `A`: `v` sees neither. Set each fresh
   pair auxiliary to its two incidences' conjunction. Only implication
   from the auxiliary is needed because at least one must be true.

These are precisely the necessary clauses in `root_core.py`; they do not
assert sufficiency, fix `e(G)`, or assume either gluing floor. Every true
extension yields a satisfying assignment independent of exterior labels,
which is the direction needed to use UNSAT.

Let `P_a` be the vertices of `H` attached only to `a`. The set
`P_a ∪ (A\{a})` is independent: `P_a⊆S_a`, `A` is independent, and
there are no cross edges by privacy. Since `A\{a}` has size five and is
disjoint from `H`, `|P_a|≤4`; there are at most 24 singly hit vertices.
All 33 exterior vertices are hit (MTF), so there are at least
`2·33−24=42` incidences. The number of removed edges is exactly
`Z(v)=6+Σ_a |S_a|≥48` because `A` has no internal edges. Together with
G-009 this gives `e(G)≥168` whenever `n6>0`. Neither this implication nor
the exclusion at `e=167` uses either gluing floor; counting the increment
relative to a ledger that already used gluing does not change the proof's
premises. `R310.IsMTF.total_edges_of_degree_six_residue` checks this
arithmetic once the residual floor is supplied, reusing the existing Lean
private-neighbor inequality.

## Incremental case accounting

`python3 -S -B ralph/lanes/H/check_floor6_delta.py` reconstructs the
near-regular cohort from the pinned 545-case table and compares exact
distribution sets, not only cardinalities. It uses the recorded certified
bounds, without re-verifying the Farkas coefficients (G/A/critic own that).
The 524 baseline, after earlier cuts, has 454 remaining and 20 possible
further U88 cuts. Of the 56 original `e=167, n6>0` rows exactly one,
`(8,0,2,30)`, was already removed; the 55 new keys match `closed167.csv`
and each of its contradiction right sides is `−n6`. Three of the 55
overlap U88. The e≥168 floor-120 LP makes no further independent cut.
The three degree-seven LP stages remove a disjoint 8/6/9 using the old
gluing floors. The resultant 376 keys, plus regular R, leave exactly
13 further keys with certified upper bound 88. See `scratch/H/floor6-delta.log`.
