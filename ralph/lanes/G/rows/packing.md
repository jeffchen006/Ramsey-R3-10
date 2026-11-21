# Rooted packing of neighbourhood incidences (hand)

Use `lifted.md` notation. Fix a root `u` of degree `i` and profile `p`.
Let `c(w)=|N(u) cap N(w)|` for `w in H_u`.

1. For `S subset N(u)` of size `k>=2`, the vertices missing `S` consist of
   `N(u)-S` and those vertices `w in H_u` missing `S`. Appending `S` to any
   independent set on those vertices proves that the induced graph has
   independence number at most `a-k`. Its order is at most
   `R(3,a-k+1)-1` (also true for `a-k=0,1`). Summing over all such `S`,
   `sum_w binom(i-c(w),k) <= binom(i,k) (R(3,a-k+1)-1-i+k)`.
2. Take `S` to be the `k` neighbours of highest degree. The number of edges
   from `S` to `H_u` equals the sum of their degrees minus `k`, and is at
   most `sum_w min(c(w),k)` by counting the incidences at `w`.
3. The number of 4-cycles through `u` equals `sum_w binom(c(w),2)` by
   choosing the opposite vertex, then its two common neighbours with `u`.
   Counting by each pair `x,y in N(u)` instead gives one contribution for
   each common neighbour of `x,y` other than `u`. This contribution is at
   most `min(d(x),d(y),d(x)+d(y)-D)-1`, with `D=N-R(3,a-1)-1`, by the
   codegree cap in `wedge.md`. The degrees of `x,y` are from `p`.

Sum each displayed inequality over all roots with a fixed profile to get
the linear rows in `typed_lp.py`. Calibration: `../check_rows.py`.
