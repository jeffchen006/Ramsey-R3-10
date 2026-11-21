# Opposite-side attachment filters for R(3)

Let `F` be the fixed bipartite graph on the open neighbor blocks of a
rooted edge, and let `L_x`, `R_x` be the two support masks of an
outside vertex x. Pin the multiset of `L_x`; leave all `R_x` variable
and omit all outside–outside edges. Any completion gives a witness
to the following necessary conditions (`hand`).

- Avoid F edges between `L_x` and `R_x` by triangle-freeness. Each
  `R_x` has size 1..3 by diameter two and the codegree cap at the
  other root. Opposite columns have exact degrees; opposite pair
  budgets and cross-pair cap three follow from codegrees. Use triple
  uniqueness including fixed triples when K3,3 is excluded.
- Given a set S of outside vertices known independent, no independent
  set I in F of size `d+1-|S|` can avoid all their attachments. For
  fixed left masks, enumerate only I with `I_L` disjoint from their
  union, then retain inclusion-minimal right shadows `I_R`. Each
  requires an attachment from S. Singles always apply. Pairs apply
  if their left masks overlap, or conditional on sharing a right
  coordinate. Triples apply if the three left pairs all overlap.
- For a partial pin, apply those rows only to pinned occurrences;
  unpinned slots still count in the full right degree and pair rows.
  Omitting left restrictions weakens the formula. An UNSAT partial
  pin therefore excludes any profile containing the pinned submultiset
  for that same oriented kernel (up to occurrence relabelling).

All implementations require solver input and proof bridges before
calling an UNSAT result `cert`. `opposite_shadow.py` is still `enum`.

## Two hand-checkable blockers

For overlapping left types `P,Q`, let `R_possible` be the union of
their two allowed right domains determined by triangle-freeness. If
some independent `I` in F of size d−1 satisfies `I_L ∩ (P∪Q) = ∅`
and `I_R ∩ R_possible = ∅`, the occurrences and I give an I_(d+1),
so P and Q cannot coexist. For kernel 88 side 1 (zero-indexed), the
left-to-right F rows as masks are `(0,1,6,10,17,48,36,192)`.
The two blocked types 144 and 162 share coordinate 7; their right
domain union is `{1,2,3,5}`. The independent seed is left
`{0,2,3,6}`, right `{0,4,6,7}`. This is a two-slot obstruction,
not an exclusion of the kernel.

If F is a perfect matching, use matched coordinate names on both
sides. The maximum independent sets of F choose one endpoint of each
edge. If two outside vertices share an attachment, they are
nonadjacent and their joint support must contain both endpoints of
some matched edge, or one could add d−1 independent kernel vertices.
In particular an occurrence of singleton `{i}` on the left must hit
`M−{i}` on the right for every other left mask M containing i:
neither occurrence can hit the right endpoint of matching edge i.
Its right support is a transversal of those sets of size at most 3.
At kernel 149, the five masks `32,33,44,50,224` require the singleton
of coordinate 5 to hit the four disjoint sets `{0}`, `{2,3}`, `{1,4}`,
`{6,7}`, which is impossible. The generator tests all such transversals,
not only disjoint set witnesses. A size-at-most-three transversal can
be padded to exactly three among the other coordinates for these widths.

## Measurements and scope

- `scratch/D/opposite_shadow16.partial.log`: all 43 labelled C16
  completions preserved in both full widths plus a partial test.
  `opposite_block_cal16/check.log`: exact labelled output sets match
  an identical flag baseline on all 13 kernels; same five classes.
- `scratch/D/opposite_shadow40.tsv`: on the original 48 matched pins,
  27 reject with singles/pairs (1.34 CPU-s), 32 reject with triples
  (2.23 CPU-s); 16 still feasible relaxations. All 48 had failed the
  stronger full pinned model in round 3. Neither width tests a cover.
- `scratch/D/opposite_shadow40.partial.tsv`: first pin in each of eight
  buckets; 5 reject, minimized by greedy omission to 5, 5, 21, 21 and
  2 slots. Each of those cores except 88 side 1 (12/100) matches one
  of 100 original profiles in its own labelled sample, without using
  coordinate symmetries. Three baseline projections remain feasible.
- `scratch/D/shadow_block40.tsv`: same eight matched buckets as
  round 3. Pair blockers remove 44/501 baseline profiles (39/47 in
  kernel 88 side 1). Transversals remove 104/200 on kernel 149 before
  checking right degree or right codegrees. Both preserve all 43 known
  labelled C16 completions. `factor_sat.py --opposite-blocks` adds both
  to a marginal CNF. First-output probes on 149 side 0 and 88 side 1
  both still yield profiles (1.61 and 0.75 CPU-s); no side exclusion.
- Perfect matching specialization: 0/200 feasible in kernel 149's
  matched full-width-two pin sample (7.61 CPU-s). The joined unpinned
  incidence relaxation preserves all 17 C16 matching-kernel outputs but
  hits a 32 CPU-s cap on R(3), with no verdict. Its row/column symmetry
  is sound: lex-minimize the left matrix under row and simultaneous
  matching-coordinate permutations; among equal left rows sort by the
  right rows. An out-of-order pair of left columns would improve the
  left minimum via their simultaneous swap. No closure of kernel 149.

Next: promote two-slot and small transversal clauses to an unpinned
incidence model with stronger symmetry or a measured case split. Do
not extrapolate 0/200 to the complete profile family. A proof run
needs replay of the kernel shadow clauses and the section 7 chain.
