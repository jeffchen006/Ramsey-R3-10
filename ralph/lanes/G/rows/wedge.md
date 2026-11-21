# Degree-typed codegrees (hand)

In the notation of `profiles.md`, let `p_ijc` count unordered nonadjacent pairs
of types `i <= j` and codegree `c`, bounded above by `P_ij`, the number of
unordered distinct vertex pairs of this degree type. The pairs partition the
nonedges: `sum_c p_ijc + m_ij = P_ij`. Nonadjacent endpoints have
`X=G-N[u]-N[v]` on `N-2-i-j+c` vertices with independence number at most `a-2`.
Thus `0 <= c <= min(i,j,i+j+R(3,a-1)+1-N)`. In MTF graphs `c>=1`.

Counting length-2 paths, whose endpoints are nonadjacent by triangle-freeness,
gives `sum_c c p_ijc = sum_{t,p} x_tp h_i(p)h_j(p)` when `i != j`, replacing
`h_i h_j` by `binom(h_i,2)` when `i=j`. This links codegree caps and class
availability to the profile concentration of low-degree neighbours.

Calibration: `../check_rows.py`.
