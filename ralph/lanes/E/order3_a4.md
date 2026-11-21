# Order three, maximum fixed attachment four: a pinned shell

**`hand`: every root orbit with four fixed neighbors has exactly 12
moved neighbors.** `a=4` here means the maximum, not four fixed points.
As in `cross_neighborhood.md`, an order-three orbit `O` is independent.
Write `A` for its four fixed neighbors and `H=G[N(O)\F]` for the graph
induced on the moved neighbors. `A` is independent and anticomplete to
`H`, so `α(H)≤5`. The antineighborhood of `O` contains `33−|H|` vertices
and has `α≤6`, so `|H|≥11` by `R(3,7)=23`. `|H|` is divisible by 3 and
at most `3(9−4)=15` by the degree bound. Thus `|H|∈{12,15}`.

Suppose `|H|=15`. The root links to each of five `H` orbits by one
matching. Label phases to make all root matchings use difference 0;
then between `H` orbits difference 0 is forbidden (triangle with `O`).
The `H` quotient is complete, since two unjoined orbits give an
independent six-set. Exactly as in the order-three `a=5` argument, the
`+1` arcs form a tournament allowing disjoint bidirected pairs, which
have uniform arcs to each third vertex; contraction orders the singleton
and double blocks. Since the number of orbits is odd, some block is a
singleton. Select phases `0,1` at that singleton, phase 1 at every
earlier orbit, and phase 0 at every later orbit. Within each half the
selected inter-orbit difference is 0, and across halves it is 2, not
the required 1. Earlier-to-singleton differences are 2 and 0, and
singleton-to-later differences are 0 and 2. The six vertices are
independent, a contradiction. This argument works for a singleton in
*any* position, not only an extreme one.

## The residual cover and first experiment

There are only eight pinned templates on the four neighbor orbits
(a cover, not necessarily pairwise nonisomorphic). A root representative
has at most five moved neighbors, so it can have at most one double
matching to the four orbits:

- All single: the ordered singleton/double compositions of 4 are
  `1111, 211, 121, 112, 22`.
- One double: normalize it to `{0,1}` from `O`, call that orbit `D`.
  Normalize the single matchings to `{0}`. The only allowable difference
  from `D` to each ordinary orbit is `+1`, since 0 and 2 would form a
  triangle with `O`. It must occur because the quotient is complete.
  Order the other orbits by their composition `111, 21, 12`.

`order3_a4_profiles.py` computes exact local neighborhood profiles for
one outer 3-orbit `J`. The neighbors of one representative of `J` in
`H` are an independent subset; the other two neighborhoods are its
rotations. Thus the program enumerates all triangle-free words, modulo
rotation of `J`, and reads off `α(H∪J)` by blocking each possible subset
of `J`. If `r=|N(J)∩A|`, the `4−r` vertices of `A` not touching `J`
can join any independent set in `H∪J`, requiring `α(H∪J)≤5+r`.
Each vertex in `A` can touch at most two other moved orbits (three
neighbors each and three already at `O`), so `Σ_J r≤8`. Degree capacities
within each `H` orbit then give an exact integer-profile relaxation.

The one-orbit profile control agrees with a complete direct subset
oracle on six vertices, including the Ramsey-valid 6-cycle and the
invalid empty graph. The `2,1,2` five-orbit template is checked to
contain the indicated independent six-set. See also the previous C35
and order-12 calibrations in `cross_neighborhood.md`.

**Result (`open`):** all eight templates still have feasible aggregate
profile states at each `f=7,10` (16/16). Individual footprint enumeration
does show that every `J` needs `r≥1`, and one with `r=1` needs at least
two edges per representative into `H`. At `r=2` it needs at least one
edge except under `22`. These facts do not account for interactions
among outside orbits, or the fixed vertices outside `A`. Do not scale
this relaxation as a solver. Evidence `scratch/E/order3_a4_profiles.v2.log`
(9.20 CPU s). Useful next discriminator: if two outside orbits share a
fixed neighbor of `A`, triangle-freeness forbids their joining; combine
their footprints with the independent-set constraints on their union.
The open original `a=2/3` branches were not relaunched.
