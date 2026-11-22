# R(6), diagonal-four 8/8 P3: two singleton-budget obstructions

Use `path_three.md` and the checked no-P4 result C-013. The independent
marked roots form a whole three-vertex component in the codegree-six
graph J. The residue X has order 22 and alpha at most six. Write B for
the 18 deleted vertices, including the three roots. T is the subset of
four vertices common to the three roots. No vertex of T can have an
edge within B except to the three roots: every nonroot in B shares at
least one root with it. Each T vertex has six neighbours in X, so the
total T-incidence on X is 24.

For an actual `x in X` let `M(x) = N(x) intersect B`, identified with a
mask on the 15 nonroots. The following four tests are necessary:

1. M is independent by triangle-freeness and it has no root by the
   definition of X.
2. M hits each independent boundary nine-set, else it and x form an
   independent ten-set.
3. `3 <= |M| <= 5`: in X, `d_X(x) <= 6` because its neighbours are
   independent, and `d_X(x) >= 4` because otherwise `X-N_X[x]` has at
   least 18 vertices and alpha at most five, contrary to `R(3,6)=18`.
   Subtract from `d_G(x)=9`.
4. It uses at most five coordinates in each root neighbourhood. A
   sixth would make x another J-neighbour of a marked root, impossible
   since the marked three roots form a whole J component.

Put `q = # {x : M(x) intersect T empty}` and `L_t = {x : M(x) intersect
T = {t}}`. Sum the elementary identity for `h=|M(x) intersect T|`,

```
2 - h = 2*[h=0] + [h=1] - max(0,h-2).
sum_t |L_t| + 2*q = 44 - 24 + sum_x max(0,h(x)-2) >= 20.
```

If `W` is an independent five-set in `B\T` with no neighbours in
`T\{t}`, then `W union (T\{t})` is an independent eight-set. At most
one member of `L_t` can avoid it: two avoiders have common neighbour
t, so are nonadjacent, and would extend the eight-set to ten.

In boundary numbering `Y=0..2, Z=3..5, T=6..9, B0=10,11,
B2=12,13, B1=14`, take keys `(1,(0,1),(0,1))` and `(3,(0,1),(0,1))`
from `p3_high_f.py`. Both arms miss the edge from their first wing
vertex to 14. Their Y--Z matrices have entries `{(0,3)}` and
`{(0,3),(0,4)}`, respectively, given as graph vertex pairs. For both
layouts use the independent five-sets

```
{0,1,2,10,11}, {3,4,5,12,13}, {10,11,12,13,14},
{0,1,2,4,5} (matrix 1) or {1,2,3,4,5} (matrix 3).
```

The independent boundary replay constructs the graph from those
literal edge rules and compares it with `classify`. It visits every
independent mask of the relevant sizes, applies the four tests,
checks the padded eight-sets, and obtains these counters:

| Layout | Admissible zero masks | Admissible singleton masks per t | Hit all four (per t) | Hit all first three (per t) |
|---|---:|---:|---:|---:|
| 1 | 0 | 112 | 0 | 17 |
| 3 | 0 | 105 | 0 | 17 |

Thus q=0 and `|L_t|<=4` for each t, contradicting the necessary total
of at least 20. This is a finite boundary enumeration plus a hand
argument, not an LRAT result. The witness comes from `astra_R`.

The edge formula is `e(X)=45+8+8+e(Y,Z)`, giving 62 and 63. The
fixed census is independently checked for all 191 rows and SHA-256
content. `singleton-bindings.tsv` binds every matching zero-based
row ID and graph6 digest to the exact boundary digest and key: 30
rows at 62, 60 rows at 63. This is not a no-go for all residues at
either edge count; the other marked boundary layouts remain separate.

## Extra capacity rows in the residual-layout pilot

A row records the count of X vertices whose mask lies in a specified
set. Order and boundary degree rows are equalities, represented by
upper bounds and their complements. A boundary nonedge of known
codegree c has at most `6-c` extra common neighbours in X; if c=0 it
must have an X common neighbour by maximal triangle-freeness.

For an independent boundary j-set I, its avoiders in X have alpha at
most `9-j`. For `j=8,7,6` they therefore have at most 2, 5, 8 vertices,
respectively, by triangle-freeness and `R(3,2)=3`, `R(3,3)=6`, `R(3,4)=9`.
Avoiders that share a fixed boundary neighbour are independent, so
their count is at most `9-j`. The latter sharper bound also applies
to the entire avoider family if all pairs of its admissible masks
intersect: two attached vertices can be adjacent only when their
masks are disjoint. Repeated masks are checked as pairs too. Zero
masks are not discarded from any of these rows.

A positive integer weighted sum of rows with coefficient at least
`max(0,2-|M intersect T|)*scale` on each permissible attachment mask
and total right-hand side less than `20*scale` is a contradiction.
The optional discovery LP just proposes weights; `--verify` uses only
integer arithmetic and recomputes every coefficient from the graph.
Its floating objective values are not themselves proof or exclusions.
The planted C21 6-regular P3 checks every capacity row at the smaller
parameters, including actual zero masks (`q=2`, six singletons).

## Condition on zero masks

For each fixed independent eight-set, collect the zero masks disjoint
from it. There are at most two corresponding X vertices: three would
have a nonedge, since X is triangle-free. If all pairs of masks in the
collection intersect (test a repeat too), there is at most one X
vertex. Whenever a union of these mask collections covers all zero
masks, summing their capacities bounds q. The checker searches such
unions by subsets of the at most 15 zero masks. Starting from the
empty subset, it adds a collection and its cost to reach its union;
the full subset cost gives a valid upper bound. The trivial fallback
bound is 22. Each of the nine target layouts has bound at most two.

Under that bound enumerate every multiset of zero masks, including
repeats and the empty multiset. An independent eight-set makes any
two of its avoiders adjacent in X; this is impossible for overlapping
attachment masks. More than two avoiders, or a triangle of such forced
edges, is impossible. This gives 105 remaining (layout, multiset) keys
from 306 before the compatibility test. `p3_singleton_cover.py` reports
all counts, including the seven layouts with nonempty zero classes.

For a fixed surviving multiset, subtract the fixed masks' contributions
from each old capacity row. For each other mask M and fixed zero mask
Z, if both miss the same boundary eight-set, an edge is mandatory.
Drop M if a mandatory edge would share a neighbour in B or closes a
triangle with a forced edge between two fixed zero vertices. For a
fixed zero vertex z, its X degree is `d=9-|Z|`; at most `d-k` nonzero
vertices can have an edge forced to z when `k` zero vertices are forced
neighbours. If at most `p` other zero vertices can be neighbours
(disjoint mask), at least `d-p` nonzero vertices must be neighbours.
Thus at most `22-q-d+p` nonzero masks can meet Z, since those vertices
cannot be neighbours. These are the two new capacity rows at each z.

T consists of four twins in the boundary, so every permutation of T
preserves the admissible mask family, the chosen zero masks, and all
necessary rows (up to renaming). If a completion exists, average its
mask multiplicity vector over the permutations. Every mask in an
orbit then receives its orbit total divided by the orbit size. The
checker uses the orbit totals, scales each row to clear these positive
denominators, and divides by its integer gcd. This is a relaxation,
not a claim that averaged vectors are realizable. The desired lower
bound on the total of singleton orbits is still `20-2q`. Nonnegative
integer weights supply an upper bound strictly below `20-2q` in 34
branches; replay checks each coefficient and strict RHS inequality.
Every q=0 branch is among these. The seven unclosed layouts require
one or two zero vertices, with exact q by layout in `ROUND8_REPLAY.md`.

For each uncut pattern and compatible residue index row, try each
placement at vertices of the prescribed degrees. A required zero-pair
edge must occur in X. For a nonedge between two zero vertices, its
full codegree is the sum of their common-neighbour count in X and
the intersection size of their boundary masks; it belongs to `[1,6]`.
The lower bound uses maximal triangle-freeness; the upper bound is
R(6). For an edge that sum must be zero. These tests leave at least
one pattern on every one of the 330 rows outside the two scout layouts.
They cut patterns, not any additional layout/residue key. The smaller
control preserves the actual zero vertices and validates their orbit
counts against every generated conditional row.
