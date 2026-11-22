# MTF support implications without shared edge variables (hand)

In the adjacent degree-six equality-root model for `e=170`, let the
roots be `u,v`, the two private wings be `L=N(u)\{v}` and
`R=N(v)\{u}`, and `W` consist of the vertices outside both closed
neighbourhoods. For type `t=(S,T,d)`, let `b_t` be the number of W
vertices with masks `S` in L and `T` in R and total degree `d`. Use
the existing box bound `0 <= b_t <= U_t`. The joint model includes all
types a genuine completion can use. The wings are independent and
the prescribed single crossing joins anchors `(1,1)`.

Fix a wing anchor `a` absent from the support of `t` on its side. If
the opposite support of `t` contains a crossing neighbour of `a`,
every vertex of that type already has a boundary common neighbour
with `a`; do not add a row. This is the only boundary exception:
no W site meets either root, and no anchor has a neighbour in its
own wing. In all other cases, if `b_t>0`, choose a vertex `x` of type
`t`. MTF gives a common neighbour `y` of the nonedge `xa`; by the
preceding observations `y` is in W. The type `s` of `y` contains `a`
on the required side, and its supports on **both** sides are
disjoint from those of `t`. A shared anchor would form a triangle
with the edge `xy`.

Let `E(t,a)` be all positive-upper-bound types `s` with these three
properties. In every completion with `b_t>0`, at least one such
type has `b_s>=1`. The following row is therefore necessary:

`b_t - U_t * sum(b_s for s in E(t,a)) <= 0`.

It is trivial if `b_t=0` and forces `b_t=0` if `E(t,a)` is empty.
At integral points obeying the box bounds it is equivalent to the
individual occupancy implication; at fractional points it is only
a necessary relaxation. It neither locates an edge nor ensures
enough distinct neighbours for several demands. In particular, an
integer point passing the new rows and all old edge table rows is
not a graph. All old variables remain free; the four historical
population points are read only to compute separate receipts and
diagnostics, never to pin the production model. The same proof
works for general two disjoint independent wings with a known
bipartite crossing: use the full opposite-neighbour mask to decide
the exception, as in the C35 and saturated Exoo39 controls.

For a named old tuple failing a row, its positive `b_t` and all
zero eligible `b_s` give an exact contradiction with that tuple's
equalities (these are the only pins). Any old edge entries may
change without affecting the contradiction. This is not an LP
certificate against the unpinned template.
