# Cycle lower bounds on every edge fixed by a pin

If the rooted edge realizes the graph's minimum C4 count `m`, every
fixed edge `i-x` has at least m 4-cycles. For `i` in the selected
root's neighborhood, all its neighbors are pinned. The count equals
`sum_{y in N(i)-{x}} (c(x,y)-1)`, since each y has i in common with
x. With cap three, each summand is exactly the sum of the threshold
bits `c(x,y) >= 2` and `c(x,y) >= 3`. For a singleton x and m=13,
the selected root contributes zero to edge `i-x`; at least six of
the other seven terms must equal two. This inequality requires a
globally minimum root, not an arbitrary rooted completion.

`pinned_side.py --fixed-min-cycles direct` adds a cardinality row over
the common-neighbor products for those choices of y. `deficit` instead
uses shared one-way threshold witnesses: claimed flags cannot
overstate the realized codegree, and choosing all valid flags attains
the true sum. The latter is equivalent with all codegree caps present.

Both variants reproduce the same 37 expected labeled C16 filtered
completions across all 241 profiles and 13 kernels, retaining the five
unrooted classes. On eight matched R(3) pins, each of base, direct and
deficit decides 8/8 UNSAT. Build plus solve totals 9.57, 27.87 and
13.02 CPU-s respectively (`scratch/D/fixed_cycle_r3/matched.log`).
The stronger variants are slower here. No new kernel exclusion;
do not scale unchanged.
