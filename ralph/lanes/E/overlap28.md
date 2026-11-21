# Involution with 28 fixed vertices: maximum attachment six

**Result (`enum`, pending critic review): `(2,28,a=6)` is empty.** The
reduction is `hand`; the only finite check uses the seven complete
`(3,6;17)` classes (D-G3 in `notes/DEPENDENCIES.md`). Neither MTF nor the
stronger minimum-degree-five certificate is assumed. Together with the
other attachment sizes' previously reported closures this would exclude
the entire `f=28` type; that aggregate inherits their evidence and labels.

## Hand reduction

Write `F` for the fixed set, `O_i` for the six moved pairs, and `A_i` for
the fixed neighbors of `O_i`. Each fixed vertex attaches to both members
of an orbit or neither; `A_i` is independent, and is empty for an internal
edge pair. Write `Q` for the simple graph on the moved pairs in which two
pairs are joined if there is at least one edge between them. Between
distinct pairs, invariance allows no edges, one perfect matching, or both
perfect matchings (a double block). Throughout, `|A_i|≤6` and at least one
has size six.

1. If two independent pairs are unjoined, they give four independent
   moved vertices, so `|A_i∪A_j|≥11`: otherwise at least 18 fixed vertices
   could add those four, contradicting `R(3,6)=18`. For an unjoined edge
   pair and independent pair the analogous bound is `|A_i|≥6` on the
   independent pair, by `R(3,7)=23`; two edge pairs cannot be unjoined by
   `R(3,8)=28`. Joined pairs have disjoint attachments, because any common
   fixed neighbor would give a triangle. Consequently overlaps can occur
   only for two unjoined size-six attachments and are at most one vertex
   per pair.
2. For an independent pair, its closed neighborhood has size exactly
   `2+|A_i|+2d_Q(i)`, since a nonempty block covers both vertices of the
   other pair. Its complement has at most 27 vertices by `R(3,8)=28`.
   Hence `|A_i|+2d_Q(i)≥11` and `d_Q(i)≥3`. A double block can involve
   only independent pairs, and its endpoints in `Q` cannot have a common
   neighbor (one can close a triangle through the double block). Their
   `Q` degrees sum to at most six, so both are three. A double block then
   gives each moved vertex four moved neighbors, whence its attachment
   size is at most five by `Δ(G)≤9`, and it is exactly five by the closed
   neighborhood bound. Each of the other four pairs is unjoined to at
   least one of these size-five pairs, and must itself have size six by
   step 1. The attachment sizes sum to 34. Since their union is at most
   28, the sum of pairwise intersections is at least six (the first two
   inclusion-exclusion terms). Only the six intersections between the
   four size-six attachments can contribute, each at most one. Thus all
   four are mutually unjoined, but three mutually unjoined independent
   pairs can add six independent moved vertices to at least ten fixed
   vertices, contradicting `R(3,4)=9`. No double block exists.
3. A size-six pair now has `d_Q=3`: the closed-neighborhood bound gives
   at least three and the degree cap gives at most three. Its closed
   neighborhood's complement has exactly 26 vertices (22 fixed and
   the two unjoined pairs) and independence number at most seven.
   Its minimum degree is at least three, since deleting a vertex and
   its neighborhood leaves independence number at most six and at most
   22 vertices by `R(3,7)=23`. If either remaining pair has an internal
   edge, its endpoints have no fixed neighbors and at most two moved
   neighbors each in this residue (one internal and at most one across).
   This is impossible. By step 1 an edge pair could be unjoined only to
   a size-six pair, so in fact every edge pair is universal in `Q`.
4. Let `D` be the complement of `Q`. Its nonisolated vertices are
   independent pairs with attachment size five or six, since every
   edge of `D` has attachment union at least 11. Their `D` degrees
   are at most two. There are no triangles in `D`, since three mutually
   unjoined independent pairs were ruled out in step 2. There are no
   triple overlaps, since a triple overlap would form such a triangle.
   If `m` pairs are nonisolated in `D`, including `r` size-six pairs,
   the total of their attachment sizes is `5m+r`. There are at most `r`
   overlaps (only among the size-six pairs, at most two per such pair).
   Their union therefore has at least `5m` vertices, so `m≤5` and `Q`
   has a universal pair. Label each pair by phases 0/1, switching as
   needed so every matching to the universal pair is cross-phase.
   Every other matching is then cross-phase: a same-phase edge would
   form a triangle with the corresponding universal vertex. In
   particular, selecting one vertex of the same phase from any number
   of distinct pairs always gives an independent set.
5. For a size-six pair `O_i`, the five other pairs give five such
   independent vertices. If `A_i` had at most one overlap, it would
   have at least five exclusive fixed vertices anticomplete to them,
   producing an independent ten-set. Thus every size-six pair has two
   overlapping size-six neighbors in `D`, so the size-six pairs induce
   a union of cycles of length at least four. There are at most five of
   these pairs by step 4, hence one cycle of length four or five. In a
   five-cycle take any `D` edge `ij` and the unique cycle vertex `k`
   nonadjacent in `D` to both endpoints. All of `A_k` avoids `O_i∪O_j`,
   an independent four-set. This gives a forbidden ten-set. Thus the
   size-six pairs induce a four-cycle `D=C4`, with the other two pairs
   isolated in `D`: neither can have a `D` edge to each other (their
   sizes are at most five) or to a cycle vertex (whose two defect
   neighbors are already used). In fact both remaining sizes `s,t`
   are at most four, since the pairs are joined to all five others.
6. The four size-six attachments have union of size 20, consisting of
   four exclusive independent sets `B_i` of size four and one common
   fixed vertex `x_ij` for each cycle edge `ij`. Let `U` be the other
   eight fixed vertices, including the two disjoint attachments of
   sizes `s,t` and `8−s−t` vertices unattached to any moved pair.
   Choose one vertex of the same phase from each of the two universal
   pairs. Their independent two-set has at least `28−s−t` fixed and
   four other same-phase vertices in its closed antineighborhood.
   As that residue has at most 27 vertices, `s+t≥5` (so both sizes are
   positive as well). Every vertex in these last two attachments has
   two moved neighbors; the other `U` vertices have none. Thus
   `Σ_{u∈U} d_F(u) ≤ 7(s+t)+9(8−s−t) ≤ 62`.

## Weighted window check

For any edge `ij` of the defect four-cycle, the fixed graph
`H_ij=G[U∪B_i∪B_j∪{x_ij}]` has order 17. The two opposite cycle pairs
are unjoined and independent, and avoid this set, so `α(H_ij)≤5`.
`B_i,B_j` are independent, and `x_ij` is anticomplete to both by the
shared moved attachments. Write `b_i=e(U,B_i)`, `z_ij=d_U(x_ij)`.
Then the weighted quantity on a window is

```
L_ij = 2e(U) + 2(b_i+b_j) + 4z_ij
     = 2(e(H_ij) − e(H_ij[B_i∪B_j]) + z_ij).
```

Averaging the four windows counts `2e(U)` once, every `b_i` once
(two incident windows), and every root term `z_ij` once. Exactly these
terms constitute `Σ_{u∈U}d_F(u)`, since `F` is partitioned into `U`, the
four `B_i`, and the four distinct roots. Therefore at least one window
has `L_ij≤62`. In fact all 7,057 eligible marked windows have `L_ij≥66`.

| Catalogue line | Edges | Markings (unordered two sets, labelled root) | Minimum `L` |
|---:|---:|---:|---:|
| 1 | 41 | 1,023 | 70 |
| 2 | 41 | 983 | 68 |
| 3 | 40 | 1,261 | 66 |
| 4 | 41 | 1,015 | 68 |
| 5 | 40 | 1,269 | 68 |
| 6 | 42 | 713 | 68 |
| 7 | 42 | 793 | 70 |

Replay from `scratch/E` with `bash ../../ralph/lanes/E/replay_overlap28.sh`.
The catalogue is copied byte-for-byte from the D-G3 McKay file, then
validated for order, triangle-freeness, absence of independent six-sets,
and seven nonisomorphic classes (`shortg`); the published count gives
completeness. `overlap_scalar.py` independently uses (a) pairs of
disjoint independent four-sets and a root, and (b) a root plus an
eight-set in its antineighborhood, counting balanced bipartitions by
connected components. The two formulae for `L` and the histograms agree.
Controls: `C5` has five markings of size `1+1`, all with `L=12`;
Petersen has 180 markings of size `2+2`, with `L=30` (60) or `32` (120).
Full evidence: `scratch/E/r4_pilot/overlap.replay.log` (0.58 CPU s).
The proof does not need any SAT pilot, full profile census, W-mask join,
nor unproved uniqueness of an intermediate reconstruction.
