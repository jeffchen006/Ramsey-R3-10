# R7 C-packing trace, version 1

Per seed, input `scratch/C/R7_full.INDEX.txt` is text: header
`degree cap order`, then `order` decimal symmetric adjacency masks
for X, then four decimal neighbourhood masks per side-package pair.
The side-package cover is a separate check: the trace verifies there is
no completion for every pair listed in this order. Deleting a package
and its proof is therefore not safe unless the side cover is rechecked.

The binary stream begins with the eight ASCII bytes `R7PACK1\n`
(the last byte is LF). Exactly one tree per pair follows, in the input
order, without separators. Require EOF after the last tree. Each tree
is preorder, one unsigned byte per node:

- `0`: closure. At least one vertex with positive residual C demand has
  fewer allowed colours containing it than its demand, or at least one
  still-required missing pair has no allowed colour containing both.
- `1..31`: branch on X vertex `byte-1` with strictly positive demand.
- `64..127`: branch on missing pair at index `byte-64` that is still
  required. Indices are assigned *before* fixing side packages: iterate
  higher endpoint ascending, and for each, lower endpoint ascending;
  list each nonedge whose endpoints have no common neighbour in X.
- All other bytes invalid. Version 1 accepts only closures by the above
  bounds, not rejection of a fully selected list; a valid trace will
  not exhaust d-2 selections at any node. Generator refuses to emit a
  successful proof if it reaches a complete selected list or a cutoff.

Colours are independent (d-2)-sets of X in lexicographic order of
increasing tuples of vertex indices (not numeric mask order).
This also lists the fixed maximum independent sets for the budget rows.

Initially the residual C demand of x is d minus its X-degree minus
the number of the four side masks containing x. Initially, a missing
pair is required unless both endpoints belong to some same side mask.
Each independent (d-2)-set I has budget
`2 - max(#A masks disjoint from I, #B masks disjoint from I)`.
Initially allow all colours except those disjoint from a zero-budget I.
The source side packages all have strictly positive C demand and
nonnegative initial budgets; check these properties before using them.

For a branch, list *all* currently allowed colours containing its pivot
(both endpoints for a pair pivot), in colour order. A branch must have
at least one child. The kth child selects the kth colour and excludes
that colour and all earlier pivot options from its own allowed domain.
Additionally, selecting a colour updates demands and budgets:

1. Remove all colours with intersection size > cap-2 with the new colour.
2. Decrement demand at each x in the new colour; for each demand now zero,
   remove all colours containing that x.
3. Decrement budget at each I disjoint from the new colour; for each budget
   now zero, remove all colours disjoint from I.
4. Stop requiring any missing pair whose endpoints are in the new colour.

Prohibit a selection if it would cause a demand or budget to become
negative. For every child, independently verify its tree under the
corresponding modified state. Siblings do not share state changes other
than the exclusion of earlier pivot options. Completeness of this branch
rule follows from choosing the first option present in a hypothetical
completion. See `proofs/pair_packing.md` for the graph reduction.
