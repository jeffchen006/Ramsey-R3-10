# Adjacent degree-six equality roots (round 6)

## Exact decomposition (hand)

Assume `G` is MTF, triangle-free, of order 40, with `alpha <= 9` and
168 edges, and that two adjacent vertices `u,v` have degree six. Use
the accepted residue floor `e(G-N[w]) >= 120` for a degree-six root `w`.
The accepted no-minimum-five residue bridge ensures adjacency when there
are two degree-six vertices; the decomposition itself only needs the
stated adjacency and floor. It does not use the degree-seven floor or
the degree-eight/nine gluing floors.

At either root, its six neighbors are independent. Each of the 33
exterior vertices has a nonempty set of neighbors among those six.
At most four have each particular singleton set: five such vertices
could join the other five root neighbors. Thus at least `66-24=42`
edges go from the six neighbors to the exterior. The residue floor
gives at most `168-120-6=42`. Equality forces four private vertices
per column and nine vertices with two attachments. Each double pair
occurs at most once: two vertices with the same pair, the four private
vertices in one of those columns, and the other four root neighbors
would be an independent ten-set.

Write `A=N(u)-{v}`, `B=N(v)-{u}`, and `X=G-(N[u] union N[v])`.
The five-sets `A,B` are independent and disjoint. At `u`, exactly
four vertices of `B` are private to `v`; the fifth has one more
attachment, giving the **unique** `A`–`B` edge. At `v`, the four
privates for each column of `B` lie in `X` because every member of
`A` attaches to `u`. Of the nine doubles, just one has the column `u`
and lies in `A`; the other eight are in `X`, with distinct pairs in
`B`. Thus each side sends 36 edges to `X`. We have `|X|=28` and
`e(X)=168-11-1-2*36=84`. In either residue (e.g. `X+B`), the marked
five-set (`B`) has 20 private and eight doubly attached exterior vertices.

### The zero-addition branch cannot occur here

Exactly eight of the ten pairs in `B` have a common neighbor in `X`.
In `X+B`, precisely the other two pairs are legal edge additions **inside
`B`**. There could be additional legal pairs outside `B`. Both marked
edges can be inserted simultaneously: no triangle can use one new edge
and an exterior vertex, and two edges cannot form a triangle entirely in
the independent `B`. Inserting one or both preserves `alpha <= 8`.
This applies to **both** degree-six residues, even if their isomorphism
classes coincide. There is no claim the two single-addition outcomes
are nonisomorphic, nor that the enlarged residues glue back to order 40.

The two-root slice has nine distributions in G's round-6 baseline. A
complete e121 catalogue, with the exact downward incidence to supplied
e120, would therefore suffice for this slice even if the zero-addition
e120 catalogue were incomplete. With today's partial frozen levels, a
hypothetical two-root case instead requires omissions at **both** levels.
This does not handle the eleven one-root distributions. It is a reduction,
not any new closure or additional global gluing floor.

### Exact inverse marks

On the five-set in an e122 completion, every vertex has degree eight:
four private neighbors and one contribution per other marked vertex,
either a common exterior neighbor or the internal new edge. Thus scan
only five degree-eight vertices inducing exactly two edges (matching
or path of length two). In an e121 completion the five degrees are
`7,7,8,8,8` and there is exactly one internal edge. For either edge
level, count the exterior signatures, check four singles per marked
column and eight distinct doubles, and require that the internal edges
lie among the two uncovered pairs. Deleting the internal edge(s)
recovers the marked lower row. **Recheck `alpha <= 8` after deletion**;
the upper bound on the enlarged graph does not imply it on the lower one.
These inverse conditions recover exactly the structural marks, not
necessarily a second compatible side or an order-40 extension.

For a potential lift, the marked cross endpoint `b*` on the `B` side
is incident to at least one uncovered pair: its degree in `X+B` is
at most seven (it needs two edges outside the residue). For `b != b*`,
its neighbor set in `X` must dominate `X`, since an uncovered `b,x`
cannot find a common neighbor outside `X` in the full MTF graph. For
`b=b*`, any failures of this domination must be adjacent to the
opposite cross endpoint `a*`. These are necessary lift conditions,
not part of the structural marking checker.

## Replays (enum, scoped)

- `audit_adjacent_residues.py calibrate gluing/val/r3_4_8.g6
  gluing/val/r3_5_12.g6`: checks the known smaller catalogues and the
  C13 circulant. On 52 oriented C13 and 12 oriented order-eight
  equality pairs, each actual mark replays forward and backward; 18
  actual order-12 controls exercise both the two-edge and each one-edge
  inverse. These controls only require domination at the roots. Negative
  controls reject omitted or duplicate marks, a saturated C5, and C4
  structural inverse candidates for which deleting edges raises alpha.
- The optimized forward search prunes any marked pair with more than
  one common neighbor (there can be no common neighbor inside the
  independent mark). It agreed with literal unpruned independent-set
  enumeration on the calibration and 32 spaced e120 controls. Full
  scan: **0 marks among the 1,223 frozen labelled e120 rows** (3.39 CPU-s),
  scoped to supplied rows. This is not evidence of census completeness.
- `audit_adjacent_residues.py inspect-upper DELTA.g6 121` (or `122`)
  writes an index to stdout: raw upper hash, each labelled mark and
  deletion, lower hash, and exact lower alpha check. Eight e121 controls
  cost 2.62 CPU-s with no structural mark. Do not extrapolate to a cheap
  full upper scan; use for small delta bindings or improve the filter first.
- `audit_equality_templates.py COVER.log BASELINE.csv` independently uses
  `geng` (exact degree/edge window), orbit sizes from automorphism counts,
  and `labelg` to compare the full canonical cover to Lane G's output.
  The count of 14 templates (11 single-root, three two-root), 3,700
  labelled masks, and all 112 template/distribution pairs match. Omitting
  a template, inserting an isomorphic relabelling, or omitting one pin
  all fail. This audits the template cover only, not CNFs or SAT outputs.

Round-6 logs are in `scratch/A/pair6/`. The e120/e121 census gap is still
six without a new augmented input; no prior SAT proof was regenerated.
