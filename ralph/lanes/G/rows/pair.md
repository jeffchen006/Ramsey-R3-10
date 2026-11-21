# Pair edge and path moments outside case R (hand)

Use `profiles.md` and `wedge.md` notation. For an unordered nonedge `uv`, put
`C=N(u) cap N(v)`, `A=N(u)-C`, `B=N(v)-C`, and `f=e(A,B)`.
The only edges counted twice in `Z(u)+Z(v)` are those incident to `C`
and those joining `A,B`: each neighbourhood is independent, no edge joins
`C` to `A union B`, and `u,v` are nonadjacent. Thus
`e(X)=e(G)-Z(u)-Z(v)+sum_{x in C} d(x)+f`. It lies between
`e(3,a-1,|X|)` and `min(floor(|X|*(a-2)/2),floor(|X|^2/4))` by the
neighbourhood independence bound and Mantel.

- `f <= |A||B|`; also `f >= i+j-c-a` since deleting at most one vertex per
  cross edge from `A union B union C` leaves an independent set.
  In an MTF graph, each vertex of `A` has a neighbour in `B`: as a
  nonneighbour of `v` it has a neighbour in `N(v)`, but none in `C` by
  triangle-freeness at `u`. Symmetrically each vertex of `B` has a neighbour
  in `A`, giving the additional lower bound `max(|A|,|B|)`.
- Sum the pair identity and inequalities separately over each `(i,j,c)` cell.
  Its `w_ijct` counts common-neighbour incidences of degree `t`; it is bounded
  by `min(c,n_t-[t=i]-[t=j]) p_ijc` and `sum_t w_ijct=c p_ijc`.
  Summing over `c` gives exactly the wedge row for centres of degree `t`
  from `wedge.md`, since each such incidence specifies one wedge.
- Its `z_ijct` is the sum of `Z(v)` over degree-`t` endpoint incidences.
  In a cell the number of such incidences is `([t=i]+[t=j]) p_ijc`, so the
  extremes of the allowed type-`t` profiles bound the sum. For each `t`,
  the sum of these `z_ijct` over all cells equals
  `(N-1-t) sum_p x_tp sum(p)` because each type-`t` vertex occurs with
  each of its nonneighbours. Global box bounds follow by `p_ijc <= P_ij`.
- Count oriented simple 3-edge paths starting at a degree-`t` vertex `u`.
  For nonadjacent endpoints `u,v` their number is `f(u,v)` (the middle
  edge crosses `A,B`). For adjacent endpoints the paths are obtained
  by traversing a 4-cycle through `u` in either orientation and stopping
  after the third edge. The number is `sum_{v not adjacent,u!=v} c(u,v)(c(u,v)-1)`:
  `v` is the opposite vertex in the 4-cycle and an ordered pair of its
  common neighbours specifies the traversal. Alternatively count by the
  second vertex `x` of degree `k` and profile `p`: there are `h_t(p)`
  choices for `u`; the third vertex `y` ranges over `N(x)-{u}` and the
  fourth over `N(y)-{x}` (it cannot equal `u`, by triangle-freeness).
  The contribution is `h_t(p) (sum(p)-k-(t-1))`. Summing over `x` gives the
  class-wise 3-path equation. As above, nonedge incidences have factor 2
  when both endpoints have degree `t`.

Calibration: `../check_rows.py`.
