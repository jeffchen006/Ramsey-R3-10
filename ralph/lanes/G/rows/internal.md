# Edge-table averaging inside every antineighbourhood (hand)

Fix vertex `v` of degree `i`. Let `m=N-1-i` be the order of `H_v`. For a
nonneighbour `w` of degree `j` and codegree `c` with `v`, its degree in `H_v`
is `r=j-c`, necessarily at most `a-1` since its neighbourhood there is
independent and omits `v`. Deleting `w` and its neighbours from `H_v` leaves
the pair set `X`, of order `m-1-r`. It has at least `e(3,a-1,m-1-r)` edges,
with the project's published table values. Counting this over `w in H_v`
gives

`sum_w [r(w)^2 + e(3,a-1,m-1-r(w))] <= m e(H_v)`.

Indeed triangle-freeness gives `e(H_v-N_H[w]) = e(H_v)-sum_{y in N_H(w)}r(y)`,
and summing the neighbour degree sums counts `r(y)^2` at each `y`. Sum the
displayed inequality over type-`i` vertices: the left is a linear combination
of the degree-typed pair counts `p_ijc` (factor 2 if `i=j`), the right is
`m * sum_p x_ip (e(G)-sum(p))`. This retains the type rather than globally
averaging all antineighbourhoods together.

Calibration: `../check_rows.py`.
