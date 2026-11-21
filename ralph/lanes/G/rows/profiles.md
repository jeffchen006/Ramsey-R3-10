# Integer local profiles (hand)

Let `G` be triangle-free on `N` vertices, with `alpha(G) <= a`; write `n_i`
for the degree counts, `H_v = G - N[v]` and `Z(v) = sum_{x in N(v)} d(x)`.
This is the profile construction of `cases/mforce.py`, now tried on the actual
post-gluing list rather than the stronger hypothetical `sel` bounds.

A degree-`i` vertex has a multiset `p` of `i` neighbour degrees with at most
`n_j - [i=j]` entries `j`; it has `Z(v)=sum(p)` and `e(H_v)=e(G)-sum(p)`,
because `N(v)` is independent. Restrict to profiles satisfying the applicable
edge floor. In an MTF graph every `y` in `H_v` has at least one neighbour in
`N(v)`. For each `x` in `N(v)`, its private vertices in `H_v`, together with
`N(v)-{x}`, are independent. Hence at most `i(a+1-i)` private vertices in total,
and `Z(v) >= i + 2(N-1-i) - i(a+1-i)`.

For every allowed profile let `x_{i,p}` count its actual vertices. These counts
are nonnegative and at most `n_i`, and sum to `n_i`. If `h_j(p)` is the number
of entries `j` in `p`, then `sum_p h_j(p) x_{i,p}` is the directed degree-class
edge incidence count: `m_ij` for `i != j`, and `2m_ii` when `i=j`. The old class
LP is kept at `(N,a)=(40,9)`. Taking the LP relaxation preserves every graph.

Calibration: `../check_rows.py` constructs actual graph coordinates for the
n-analogues and evaluates every row in exact integer arithmetic.
