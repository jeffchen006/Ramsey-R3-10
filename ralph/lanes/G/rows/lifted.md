# Root-profile lifting and finite degree-availability bound (hand)

Fix a degree-`i` root `u` with neighbour multiset `p`, write `m=N-1-i` for
the order of `H_u`, and `q_j=n_j-h_j(p)-[i=j]` for the available degree-`j`
vertices there. For each `(i,p,j,c)` introduce the count `q(i,p,j,c)` of
ordered pairs `(u,v)` with `v` a nonneighbour of degree `j` and codegree `c`.
Summing over `c` gives `x_ip q_j`, and summing over root profiles gives
`p_ijc` for distinct endpoint degrees or `2p_iic` otherwise. Sum codegrees
over `v` for each fixed root: each vertex `x` in `N(u)` has `d(x)-1`
neighbours in `H_u`, so the sum is `sum(p)-i`. The private bound and the
internal inequality in `private.md` and `internal.md` also hold separately
for each root profile, before summing over a degree class.

For `v` of degree `j` and codegree `c`, let `B=N(v)-N(u)`; it has `r=j-c`
members, all drawn from `H_u-{v}`. For each `b` in `B`, every neighbour of
`b` in `N(u)` is in `A=N(u)-N(v)`, since shared neighbours also touch `v`.
The pair `(u,b)` is nonadjacent, so by the Ramsey codegree cap (`wedge.md`),
the number of such neighbours is at most
`min(i-c, max(0,i+d(b)-(N-R(3,a-1)-1)))`. Write this capped count `cap(b)`.
By the pair identity,

`e(X) = e(H_u) - sum_{b in B} d(b) + f <= e(H_u)-sum_{b in B}(d(b)-cap(b))`.

Take the `r` cheapest costs `d(b)-cap(b)` over the list with multiplicities
`q_t-[t=j]` to obtain an upper bound. Conversely take the `r` largest
degrees in that list and use the cross-edge lower bound in `pair.md` for
a lower bound on `e(X)`. If this interval misses the published edge floor
or the elementary edge ceiling on `X`, the cell `(i,p,j,c)` is impossible.
The implementation also checks `r <= a-1` and availability of `r` vertices.

Calibration: `../check_rows.py` checks the augmented rows in exact arithmetic
on C35, Exoo39, a triangle-free saturation of Exoo39, and the 191 repository
graphs for (3,7,22). The same test checks the simple (3,9,36) contradiction.
