# Order three: large fixed attachments

**Claims (`hand`): `(3,7,a)`, `(3,10,a)` are impossible for `a=5,6`.**
We use only triangle-freeness, `α<=9`, the degree upper bound 9 and
known Ramsey values (D-R1: `R(3,4)=9`, `R(3,5)=14`, `R(3,7)=23`).
All graphs are in scope, not just MTF graphs. Here `a` is the maximum
number of fixed neighbors of a moved orbit, as in F9.

Let `O` attain `a`, and write `A` for its fixed neighbors, `B=F\A`,
and `H` for the graph induced by the moved neighbors of `O`. A
length-3 orbit of the automorphism is independent (one internal edge
would give a triangle). `A` is independent, and no vertex of `H` has
an edge to `A`: every `A` vertex sees every member of `O`. Because
`O` and `A` are independent, the Ramsey bounds give

```
40 - 3 - a - |H| <= R(3,7)-1 = 22,
|H| <= R(3,10-a)-1.
```

Also `|H|` is a multiple of three. If `a=6`, the first bound yields
`|H|>=9`, but the second gives `|H|<=8`. This excludes `a=6` for
every `f` (the two cited `f` were only enumeration exclusions).

## The forced graph on the moved neighbors when a=5

If `a=5`, the bounds force `|H|=12`, since `10<=|H|<=13`. Let its
four orbits be `H_i`. From any vertex of `O` there is one edge to
each `H_i` (invariance), exactly four moved edges by the degree cap.
In other words every `O`–`H_i` block is a single matching.

Choose cyclic phase labels in `H_i` so these four matchings use phase
difference zero from `O`. Between `H_i,H_j` phase difference zero is
then forbidden (triangle with `O`). Differences 1 and/or 2 are allowed:
there is at least one edge between every pair of `H_i,H_j`, since two
unjoined orbits would give an independent 6-set in `H` but `α(H)<=4`
by adjoining `A`. Draw an arc `i→j` when phase difference `+1`
from `i` to `j` is allowed (the reverse arc means difference `-1`).
There is no directed triangle: a length-3 cycle of +1 shifts would
close in phase mod 3 and give a triangle in `H`.

Bidirected pairs are disjoint: if two share a vertex, either orientation
of the third pair gives a directed triangle. Also a bidirected pair
has uniform arcs to/from any third vertex; nonuniform orientations
would give a directed triangle. After contracting those pairs, the
result is a tournament with no directed triangle, hence transitive:
in a tournament, `u→v` and `v→w` force `u→w` if triangles are absent.
Thus the singletons and bidirected pairs are linearly ordered with
arcs from earlier to later. If there were at most one bidirected
pair, a singleton would be first or last. At a first singleton take
phases `{0,1}` and at every other orbit phase 0; if last instead take
phases `{0,2}` and at every other orbit phase 0. Either gives an
independent 5-set in `H`. Hence there are exactly two bidirected
pairs, forming two ordered blocks.

Consequences: (i) each vertex of `H` has degree 4 within `H`
(two edges to its bidirected partner and one each to the other
orbits) and one neighbor in `O`; (ii) deleting any one orbit from
`H` leaves an independent 4-set (take two phases at the singleton
among the three remaining orbits, as above, and phase 0 at the two
others). In particular every `b∈B` must have a neighbor in `A`: since
the quotient on `H_i` is complete, `b` can touch at most one `H_i`
or it forms a triangle. Otherwise `b` could join `A` and an independent
4-set avoiding its `H_i` (or any `H_i` if it has no neighbor in `H`).

## Count incidences to the remaining moved orbits

Let `J` be a moved orbit outside `O` and `H`. Put
`r_J = |A ∩ N(J)|`, and let `b_J` count neighbors in `H` of one
vertex of `J` (so a double matching counts twice).

- `r_J>=1`: otherwise `H∪J` is anticomplete to `A` and has order
  15, contradicting `R(3,5)=14`.
- If `r_J=1`, `J` must touch all four `H_i`: a missing orbit, `J`,
  and the four nonneighbors in `A` would form an independent 10-set.
  In fact `b_J>=5`. If all four matchings are single, take any `z∈J`.
  Its four neighbors in `H` are independent (triangle-free) and
  anticomplete to the other two members of `J` (single matchings).
  These six plus the four vertices of `A\N(J)` give an independent 10-set.
- If `r_J=2`, `J` touches at least two `H_i`, so `b_J>=2`. If it
  touched at most one, delete that orbit from `H` and use (ii) to
  adjoin four vertices to `J` and the three vertices of `A\N(J)`.

Write `s=Σ_J r_J`. Every vertex of `H` has at most four neighbors
outside `O∪H`, by (i), so `3Σ_J b_J <= 12·4`, i.e. `Σ_J b_J<=16`.
If equality holds then `B` has no edges to `H`. Each vertex of `A`
has three neighbors in `O` and three in each remaining orbit it
touches (and none in `H` or `A`). Thus `e(A,B) <= 30-3s`. Every `b∈B`
touches `A`, so `|B| <= 30-3s`.

- **`f=7`**: six orbits `J` and two vertices in `B`, so `s<=9`.
  The lower bounds give `Σ_J b_J >= Σ_J (6-2r_J) = 36-2s >=18`, a
  contradiction.
- **`f=10`**: five orbits `J` and five vertices in `B`, so `s<=8`.
  If `s<=6`, then `Σ_J b_J>=30-2s>=18`. If `s=7`, the positive
  `r_J` multiset is `(1,1,1,1,3)` or `(1,1,1,2,2)`; the lower
  bound is respectively 20 or 19. If `s=8`, the possibilities are
  `(1,1,1,1,4)`, `(1,1,1,2,3)`, `(1,1,2,2,2)`, with bounds 20,
  17, 16. Thus only the last is possible, and equality shows `B`
  is anticomplete to `H`. Each vertex of `A` touches at most two
  remaining moved orbits. The total deficit from two each is
  `10-s=2`. Only vertices with positive deficit can meet `B`, so
  at most two `A` vertices cover all of `B`. For each independent
  `S ⊆ B` we require `|N_A(S)|>=|S|`, or else `S ∪ (A\N_A(S))`
  has at least six independent vertices anticomplete to `H`, and
  can add four from `H`. Since `B` has order 5 and is triangle-free,
  it has an independent pair. Thus exactly two distinct vertices of
  `A` must meet `B`, and the requirement also implies `α(B)<=2`.
  Each of those two vertices can touch at most two members of `B`
  because its neighborhood is independent. So they cannot cover
  five vertices, a contradiction.

Calibration: `calibrate_cross.py` checks the twelve-vertex shape
enumeration and the single-matching avoidance argument on all 81
attachment patterns to a `(3,5,12)` witness. It also evaluates
the cross-neighborhood inequalities on `C35(1,7,11,16)` with its
order-three automorphism (a smaller positive case).
