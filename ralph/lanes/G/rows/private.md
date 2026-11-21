# Private-neighbour budget per degree class (hand)

Use `wedge.md` notation. For degree-`i` vertex `v`, codegree-1 nonneighbours
of `v` are exactly vertices private to some `x` of `N(v)`. For each `x` they
are pairwise nonadjacent (they share `x`) and miss `N(v)-{x}`, so there are
at most `a+1-i` of them for this `x`. Summing over `x` and all degree-`i`
vertices gives `2p_ii1 + sum_{j != i} p_ij1 <= n_i i(a+1-i)`, interpreting
subscripts in increasing degree order. Valid without MTF; for `i=a` this
recovers the budget from Lemma N (nonadjacent codegree 0 also impossible then,
since a nonneighbour missing `N(v)` augments it to an independent `a+1`-set).
This is a separate row from the lower bound on `Z(v)` in `profiles.md`.

Calibration: `../check_rows.py`.
