# R(6) codegree-six paths and cycle check

**Hand review.** The double-neighbour containment uses `H = G - N[x]`
of order 30: each of two partners has degree three in `H`, and they are
nonadjacent because their six-sets in `N(x)` intersect in at least three
vertices. A common neighbour in `H` leaves at least 23 vertices after
deleting their closed neighbourhoods, with independence number at most
six since the two partners can be added. The same argument for three
partners, using the disjoint four-sets, gives order 18 and independence
number at most five. This proves maximum degree two in the codegree-six
graph `J`.

For a four-vertex `J` path, the two distance-two containments imply
`(N₀ ∪ N₁) ∩ N₂ = N₁ ∩ N₂`, while the intersection of
`N₀ ∪ N₁ ∪ N₂` with `N₃` contains `N₂ ∩ N₃`. Thus the first two
neighbourhoods cost 12 vertices and the next two cost at most three
each. If the endpoints were nonadjacent all four roots could be added
outside that union; the complementary residue contradicts `R(3,6) ≤
18`. The endpoint adjacency forces their neighbourhoods disjoint; the
two diagonals' intersections are disjoint three-sets partitioning the
middle codegree-six overlap. This sequential-union proof avoids
formalizing full four-set inclusion-exclusion. In fact only the lower
bound of six for each new overlap is needed for this step; the distance-two
containments are needed for the later decomposition. The generic cardinal
and Ramsey-cover steps are drafted in `lean/R310/Residue.lean`, not yet
typechecked.

The block propagation and length bound in `ralph/lanes/C/proofs/codegree_six_paths.md`
follow from this partition. In particular, on the eleven-vertex path,
distance 3–5 pairs are all edges in `G`, so distance 6–10 pairs are
nonedges. Among the blocks covering the six independent roots, the
five pairs `D_j,D_(j+8)` for `−1 ≤ j ≤ 3` each share `v_(j+4)`;
this is enough for the union bound of 25 irrespective of overlap
between different pairs. For the eight-cycle the consecutive-three
windows omit each of the sixteen boundary vertices five times. That
multiplicity explains `5 d_B(x) ≥ 24` and the cutoff `Δ(X) ≤ 4`.

**Independent enumeration replay.** `check_cycle8.py` does not import lane
C's code or use nauty, its candidate table, or its obstruction table.
It checks all 191 input graphs for order, triangle exclusion, independence
number at most six, and pairwise non-isomorphism. Given the published
count 191 this binds the census. It separately generates independent
six-sets and the eligible 16-vertex residues, builds isomorphisms with
degree-neighbour invariants and explicit pair consistency, enumerates
all 90 ordered pairings, and checks tuple-valued half-load complements.
The positive and negative toy load controls pass. The two implementations
agree: 270 eligible placements, 32 families, 95,984 four-type words,
zero complementary pairs. No codegree-six cycle follows in `R(6)`
if the hand reduction and census premise are accepted; this does not
exclude any complete path branch by itself. Keep C's `enum` label
pending critic acceptance.

Reproduce from `scratch/H`:

```
ulimit -v 16777216
nice -n 5 timeout 180 python3 -B ../../ralph/lanes/H/check_cycle8.py ../../gluing/val/r3_7_22.g6
```

The census SHA-256 is `228d886ee01b3003d90c768af57804954f7adccbca901a3eeb3c69ccc020e8c5`,
equal to lane C's source. The refined traversal used 5.15 CPU-s
(`scratch/H/cycle8-independent-v2.log`), down from 37.67 CPU-s without
the adjacency-first variable order.
