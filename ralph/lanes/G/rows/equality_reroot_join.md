# The two-window join for mixed e168 equality anchors

## Hypotheses and hand reduction

Work only at `(n6,n7,n8,n9)=(2,7,4,27)`, with the adjacent degree-six
roots, path/leaf A side and matching/incident or path/middle B side of
`pinned_anchor_swap.md`. All three pivots are noncross. Two same-side
pivots are exchanged; call them `s` (retained originally) and `t`
(deleted originally). Call the fixed opposite pivot `f`. This is a
projection, not a claim that every satisfying projection comes from a
40-vertex graph.

Put `P = G-N[f]` and `H = P-N[s]-N[t]`, where the latter two deletions
use closed neighbourhoods in `P`. The root `r` of the exchanged side
survives in `P` (it is opposite the fixed pivot) and has exactly five
neighbours there: the two exchanged pivots and the three smaller-side
anchors of `H`. The other root is absent. The 21-core `H` is precisely
the old equality deletion, with unchanged ordered marks `3+4` and
directed cross edge. By A-018, its small side contains all three
doubles and lacks just one copy of the crossed singleton. The two
paired windows in `P` retain, respectively, `s` and `t`. Let `U` and
`V` be their respective exterior wing sets, and `Z` the common
exterior neighbours of `s,t` in `P`. Then

```
P = H + {s,t,r} + U + V + Z
T_s_retained = H + {s} + U
T_t_retained = H + {t} + V.
```

Each wing is independent and every member of `Z` is nonadjacent to
either wing by triangles. In the following table `τ` records whether
the shared exterior vertex of the two exchanged pivots (when present)
also meets `f`.

| Small side and fixed pivot | Small-side variant | `(|U|,|V|,|Z|)` | Reroot order |
|---|---|---|---:|
| A, d8 | `s` leaf | `(2,5,0)` | 27 |
| A, d8 | `s` full, `τ=0` / `τ=1` | `(2,4,1)` / `(2,5,0)` | 26 / 27 |
| A, d9 | `s` leaf | `(2,4,0)` | 26 |
| A, d9 | `s` full, `τ=0` / `τ=1` | `(2,3,1)` / `(2,4,0)` | 25 / 26 |
| B, A-centre fixed | `τ=0` / `τ=1` | `(4,3,1)` / `(4,4,0)` | 25 / 26 |

For A, the exact hole pairs of the fixed B pivot role are unchanged.
The two full variants for each `τ` correspond to which of the two
retained noncross small anchors is the other leaf. In either choice
the A-centre has no double with the crossed star or the leaf. For B,
the two holes must each contain one of `s,t`: the three core doubles
all occur, s and t are both d8, and the `s,t` double is present. The
other endpoints are either different with one of them the crossed
anchor (matching), or both equal the crossed anchor (middle). At
`τ=0` the codegree-three pivot was deleted originally, giving indexed
widths 4,3 with no symmetry quotient. At `τ=1` both codegrees are 3,
so reversing `s,t` preserves the core and both widths. Choose the
nondecreasing pair of endpoint labels, keeping one of the two
orientations for matching and keeping the self-dual middle orientation.

The larger side of `H` has four anchors. All outside vertices in
`P` have a nonempty support there that avoids `f`; subtract the actual
14 old exterior signatures from the exact four-column multiset.
This leaves 7 slots for A/d8, 6 for A/d9, or 8 for B; these are exactly
the slots of `U∪V∪Z`. A wing vertex already touches its retained
pivot; it can have at most one other small-side contact, from a present
double of that pivot. Each such other contact occurs at most once in
its wing, and the pure pivot singleton occurs at most four times.
The common exterior vertex, when present, has no further small
contact. The scheduler enumerates these roles without assuming that
any projected lift exists.

## Joint bounds

For a specified core anchor contact mask `S`, the possible core
contact set is at most `S ∪ (exterior(H) \ N_H(S))`, and `S` must
be independent. The exact column-size upper bound to `H` is `|S|`
plus α of the optional contact vertices. This bounds degrees and
the two paired edge totals. Every subset of one wing is independent.
Across wings, two vertices are forced nonadjacent if their prescribed
contacts intersect. Add any unchanged core independent set missing
the union of the optimistic contacts. Forbidden totals are 8 in a
paired window, 9 in `P`. In `P`, `Z` can be inserted into any such
wing set, and `r` can also be inserted if the core set avoids the
three smaller anchors. The upper edge bound in `P` uses these column
size caps, all fixed pivot/root edges, and one possible edge per
cross-wing pair without a shared prescribed contact. All these are
necessary; the first surviving table is not a Ramsey-window witness.

For each pivot `f` of degree `d`, its neighbours are its degree-six
root and `d-1` exterior vertices, all degree 7 or 9. If `p` of those
exterior neighbours have degree seven, triangle-freeness gives

```
e(P) = 168 - sum_{x in N(f)} d_G(x) = 162 - 9(d-1) + 2p.
```

So the floors are 108 (B reroot with `d=7`), 99 (A reroot with `d=8`),
90 (A reroot with `d=9`), and the corresponding parity holds exactly.
The `p` degree-seven neighbours must be among `f`'s four singleton
slots, though the join does not require this upper bound. This bound
is conditional only on the named strip and exterior degrees, not on
the global completeness of either degree-8/9 gluing floor.

The joined CNF keeps all H edges, both pivots, the five fixed root
incidences and the shell membership. It enforces triangle-freeness,
the support margins above, parity, published paired edge floors and
Ramsey degree bounds. It uses `δ≥4` for the B order-26 windows via
G-033 and the equality degree; for B/order25 with `τ=0` it uses `δ≥3`
only in the middle shape, by G-037 and the ordinary degree lower
bound. The B matching order-25 floor is **only** two. The eager
clauses enumerate all independent H six-sets and all potentially
independent triples in the rest of `P`. Other independent nine-sets
are not part of the eager certificate CNF. Lex order on wing contact
vectors is legal by independent relabelling within each wing.

## The missing singleton gives a maximal column

All vertices outside the three-anchor side lacking contacts to
**both** exchanged pivots must fill the old-only slots. In `H`, all
three double slots are used and exactly the crossed singleton is
short. To fill the remaining copy, a single exterior vertex `w`
outside `P` has exactly that small-side singleton (so misses both
exchanged pivots). Since `w∈N(f)`, there are no edges to another
neighbour of `f`. Hence in `G`, `N(w) = {f} ∪ N_P(w)`;
`N_P(w)` is independent and has size 6 or 8. If `w` has an extra
larger-side anchor contact besides `f`, it is not a degree-seven
vertex (external d7 requires singleton on both sides), forcing
size 8. Finally any unadjacent `y∈P` needs an MTF witness for the
nonedge `wy`. This witness is in `P`, since `y` misses `f` and no
other vertex outside `P` meets `w`. Thus `N_P(w)` must dominate
`P`. The extra-column pilot pins the unique small singleton and
enforces those constraints; it does not add the other neighbours
of `f`, nor require every independent nine-set of `P` in LRAT runs.
