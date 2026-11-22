# Upper edge budget for paired path/leaf windows (hand)

Use the hypotheses in `path_leaf_windows.md` for the two e168 pins
with both strips path/leaf. Write `j` for centre codegree, `w=6-j`,
and `T` for the paired antineighbourhood. It has eight retained
anchors and `16+j` exterior vertices. Each retained four-column
strip has (before removal of the opposite-exclusive vertices) 16
single and six double signatures. Its full attachment incidence sum
is `16+12=28`; the cross edge contributes one to its four degrees.
Each of the `w` opposite-exclusive vertices removed from this list
costs at least one incidence. Thus the sum of all eight marked
degrees is at most `58-2w`, i.e. `46+2j`. Meanwhile all exterior
degrees in T are at most seven: their neighbourhoods are independent
in the `(3,8)` graph T. In particular

```
delta(T) <= floor((46+2j)/8) <= 6,
e(T) <= floor((46+2j+7(16+j))/2) = floor((158+9j)/2).
```

This gives `e(T)<=83,88,92` at `j=1,2,3`, respectively. If a
minimum-degree vertex with degree `q` is exterior, subtract `7-q`
from the numerator. This does not require T to be maximal. If `j=2`
and `e(T)=88`, equality forces each retained exterior vertex to have
degree seven in T and every opposite-exclusive vertex to have
singleton support on the opposite strip. In particular an exterior
minimum-degree vertex of degree four at `j=2` implies `e(T)<=86`.
Similarly an exterior minimum-degree vertex of degree three at `j=1`
implies `e(T)<=81`.

The generic marked-window version has side width `b`, singleton
cap `p`, a unique double per pair, `L=bp+binom(b,2)` total
signatures per side, and `w` missing signatures on each side.
When both sides are independent and share exactly one cross edge,
their summed degrees in the window are at most
`2(bp+2*binom(b,2)+1-w)`. Replace 7 above by the actual
independence cap. The correction for an exterior vertex of degree
`q` is still `alpha_cap-q`. The exact degree-sum identity is stronger:
subtract a further one for each missing *double* signature on each
side before halving the numerator.

Separately, in the centre-table relaxation, each `x` exclusive to
one deleted centre must see a vertex exclusive to the other centre.
Indeed `x` is nonadjacent to the other centre; their common neighbour
by maximality is not a root (no X–root edges), is in its six-set,
and cannot be in the common part (the first centre's six-set is
independent). This is why an empty compatible cross row rejects a
centre table. The same argument works with unequal centre degrees.

Calibration: `test_window_budget.py` checks the generic identities
and inequalities on all 21 width-two marks from the exact 410-class
8-vertex control. It independently checks the generic maximality
statement for every nonadjacent pivot pair in the saturated C13,
C35 and Exoo39 controls. See `scratch/G/round8/window-budget.control.log`.
These are cut rows; no whole degree distribution is closed.
