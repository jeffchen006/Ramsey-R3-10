# R(7) package-packing proof review — round 1

I reviewed `ralph/lanes/C/proofs/pair_packing.md`, the package-generation
conditions in `ralph/lanes/C/pair_packages.py`, and the branch semantics in
`ralph/lanes/C/TRACE.md`. The reduction is sound as a **hand** implication:
if an R(7) graph exists, one of the four 27-vertex residue inputs has a
listed pair of side packages and a surviving colour packing. This review
does not substitute for independent checks of the lists and trees.

## Coverage arguments

1. Use `R310.R7.r7_count`/Lemma R7 and the published 27/85 class count.
   Fix any isomorphism of the residue onto its input graph. The two roots
   are nonadjacent; their exclusive sides each have two vertices with all
   four cross edges. The seven common vertices see both roots but no
   other boundary vertices. The four side masks have size six, the seven
   common-vertex masks size seven; all are independent in the residue.
2. Each residue vertex hits each independent root neighbourhood of
   size nine, or it would extend it to ten. If the vertex misses the
   common side then it must hit both exclusive sides, making a triangle.
   Thus reserve one demand unit for the common side. If the union of a
   package misses an independent seven-set, that set, the two vertices
   of the side, and the opposite root form an independent ten-set.
3. Two masks on the same side overlap in at most four vertices: their
   owners already share the root and both opposite side vertices. Every
   vertex outside a side mask and its residue-neighbourhood must have a
   neighbour in the opposite side: it otherwise forms a nonedge with no
   common neighbour with the mask's owner. A nine-regular triangle-free
   graph with alpha at most nine is maximal, so such a nonedge is not
   possible. This explains the opposite-union containment and own-union
   disjointness filters. Disjointness of the two package unions follows
   from the complete bipartite side block. Ordering masks within a side
   and ordering the pair of side packages lose no case (swapping roots
   exchanges the sides); no quotient by residue automorphisms is needed.

## Trace obligations

- Every residue vertex has exact degree demand after the exclusive masks.
  Every required pair is a nonedge with no common neighbour in the
  residue or the exclusive masks, so needs some selected common mask.
- Common masks are distinct: duplicate masks would give codegree nine
  (seven residue vertices and the two roots); pairwise overlap at most
  five follows for the same reason. For any independent residue
  seven-set, combine its avoiding common masks with the larger avoiding
  exclusive side. The result must have size at most nine. This gives
  the trace budget `2 - max(miss_A,miss_B)`.
- A trace verifier need not certify the *sufficiency* of these conditions
  for graph completion. Each condition is necessary. Every valid
  packing must contain an allowed mask at each positive-demand pivot or
  uncovered-pair pivot. Assign it to the child of its first such mask.
  Removing earlier pivot options at that child preserves the packing;
  budget, demand and overlap deletions preserve it as well. A leaf closes
  only with the stated domain shortage. Rejecting all complete-colour
  leaves in v1 avoids trusting the generator's final graph test.

The computation remains `enum` until the critic accepts the cover and
proof replay. Independent verification should regenerate the four seed
graphs (or use a known complete catalogue plus the published count),
regenerate side packages without using the DFS's package list as the
cover, check the order/degree/cap and input identities, then check every
trace tree, with exact EOF. Lane A reports all 977,008 pairs and
49,569,079 nodes replayed, using an independent trie count and
labelled-input checks (`ralph/lanes/A/R7_REPLAY.md`). That replay is
evidence for the critic, not itself a label change by H.
