# Rounded common incidences in a diagonal-four 8/8 P3

Scope: in `R(6)`, a whole P3 component of the codegree-six graph with
diagonal four and both wing cross counts eight. Use the boundary cover
of `path_three.md`, `p3_high_f.py`, and the exact scope of C-027. The
root neighbourhood union has 15 vertices (three sizes 9, overlaps
6,6,4, and triple overlap 4). The roots have no neighbours in X; they
are independent because they share a neighbour. Thus the boundary B
has 18 vertices and the residue X has 22. An independent seven-set in
X would extend by the three roots to ten. The common set T has four
vertices and its only neighbours in B are the roots: any other
boundary vertex and a vertex of T share a root. Consequently each
vertex of T sends six edges to X.

## Counting identity, for Lean

Write `h(x) = |N_B(x) ∩ T|`, and `n_i = #{x ∈ X : h(x)=i}` for
`0 <= i <= 4`. Put `q=n_0`, `S=n_1`, `D=n_2`, `U=n_3`, `V=n_4`.
The row and column counts give

```
q + S + D + U + V = 22,
S + 2*D + 3*U + 4*V = 24.
```

Subtracting the latter from twice the former gives `S+2*q = 20+U+2*V`.
In particular `S>=20-2*q`. If `S<=20-2*q` then `U=V=0`; if
`S<=21-2*q` then `V=0` and `U<=1`. These conclusions require no
enumeration once the bounds on `S` are supplied. With `q=1` and
`U=V=0` there are 18 singletons and three doubles. With `q=2` and
`U=V=0` there are 16 singletons and four doubles.

## Capacity rows and exact replay

For `x in X`, `M(x)` is its mask on the 15 nonroot boundary vertices.
It is independent, meets every independent boundary nine-set and uses
at most five neighbours of any root (otherwise x would belong to the
same codegree-six component). Its size is 3 through 5. Indeed
`d_X(x)<=6`; also `d_X(x)<4` would leave at least 18 vertices in
`X-N_X[x]` and an independent six-set there by `R(3,6)=18`, impossible.
In any independent boundary `j`-set I with `j=6,7,8`, those X vertices
whose masks miss I have independence number at most `9-j`. Their
counts are at most 8, 5, 2 by the small Ramsey numbers. Strengthen to
`9-j` for the subgroup that also has a specified mask bit, or for the
whole avoider group if every two admissible avoiding masks intersect.
In both strengthenings the counted vertices are independent, since a
common boundary neighbour rules out an X edge. A column degree row
counts exactly `9-d_B(b)` vertices at column b, so it also gives an
upper bound of that value.

Two X vertices whose masks miss a common independent boundary eight-set
must be adjacent. Thus a matching zero mask pair is impossible when
forced adjacent but sharing a boundary neighbour. A triple is also
impossible if all three pairs are forced adjacent. This necessary test
applied to every length-three multiset of the zero masks finds none
compatible in any of the nine layouts; so no larger multiset can occur.
For a fixed zero multiset, remove each nonzero mask whose forced
adjacency to a zero vertex would make a triangle, whether with a shared
boundary neighbour or with an adjacent pair of zero vertices. Subtract
the fixed zero contribution from each row's right side.

Every permutation of T preserves the boundary and these mask tests;
in particular the fixed zero masks do not change. Average a capacity
row over the permutations of T. For each orbit of nonzero masks its
coefficient is the fraction of the orbit lying in the original row.
This gives a necessary inequality for the total multiplicity of that
orbit. Multiply by the least common multiple of orbit sizes and divide
all coefficients and the right side by their common gcd; both operations
preserve the inequality. Add named rows with the positive integer
weights in the witness. Each orbit with exactly one T bit must receive
coefficient at least `scale`; all other coefficients are nonnegative.
Hence `S <= floor(weighted_rhs / scale)`. A bound strictly less than
`20-2*q` excludes just the fixed zero pattern, not the entire layout.

`p3_upper_audit.py` rebuilds masks by subset enumeration, uses the
necessary forced-edge test above to enumerate all compatible zero
multisets, and independently builds and normalizes each selected
degree, avoider and tagged-avoider row. It does not use the production
LP or the row compressor. It verifies 34 exclusions from round 8 and
bounds all 71 remaining patterns: `U+2*V=0` in 47, and `U+2*V<=1` in
24. The cases with the second bound need not have a triple. This
excludes no additional zero pattern or residue row by itself.

## Deficits of the unaveraged rows for the two single-zero layouts

In layouts `1:0:1:1:1` and `3:0:1:2:1`, q=1 and the respective
unique mask is `{0,4,14}` and `{0,5,14}`. The witnesses in
`rounded.json` give `3S<=56` and `3S<=55`, so `S=18` in both.
For these two witnesses `raw_slack` in `p3_tight_sat.py` independently
expands the named `avoid` row to its four versions (one for each
omitted T bit), and the `deg` row to its fixed post-zero degree bound.
All avoid blocks have three T elements and meet the zero mask. The
only possible avoiders after choosing the unique zero are singletons
of the remaining common vertex. Their caps are 1 and 3 for an eight-
and a six-block, respectively. The raw checker directly verifies that
the sum of raw bounds with the given weights is 56 or 55, and each
remaining admissible nonzero mask gets coefficient at least three
if singleton and at least zero otherwise. For each mask its *margin*
is the coefficient in excess of this requirement. The weighted sum
of all row deficits plus all mask margins is exactly `bound - 3*S`.
Each summand is nonnegative. Since the degree rows are exact, their
deficits are zero. Therefore the combined budget for the avoider row
deficits and mask margins is at most two in the first layout and one
in the second. This is an exact necessary budget, not a claim that
any assignment achieving the budget obeys all graph constraints.

## Joins tested in round 9

**Private wings.** Every actual boundary column's footprint is an
independent set in X of cardinality its degree deficit. For either
private wing, any two columns and the other two roots form an
independent boundary four-set. The union of those two footprints
must therefore meet every independent six-set in X. Store for a
footprint the bitset of six-sets it misses; a pair passes precisely
when these two bitsets are disjoint. Pair intersection sizes must
also satisfy the old codegree bounds. A triple uses the same column
choice at both its incident pairs and must project at each row to one
of that row's allowed attachment masks, using the pinned zero and
known edges and codegrees to it. This is a separate necessary join
within each wing, not a test that projections from the two different
wings lift to a common full attachment.

**Common columns.** In the two unique-zero layouts each common column
footprint is an independent six-set in X. Their union is `X` minus
the zero position, and exactly three vertices are covered twice;
none is covered more often. The footprints are distinct: two equal
ones would give at least six doubled vertices. Sort them and split
the ordered four choices into the first and last pairs. The two
unions cover the prescribed set exactly; a double covered within one
pair cannot lie in the other pair's union. Test the row-wise allowed
multiplicities at this same four-column assignment. These bitset
tests enumerate every necessary cover once, up to the permutation of T.

For one four-column cover, the singletons attached to a tag form an
independent set. For each such row the allowed masks give possible
sets of missed cap-one blockers, a Boolean miss for the cap-three
blocker, and nonnegative margins. The DP for a tag keeps the occupied
cap-one slots and the count for the cap-three blocker, with the least
sum of margins at each state. A transition chooses a row mask, updates
these counts and discards overflow. Each final state pays the total
weighted unfilled slots as well. Add these four minima and the minimum
margin of each doubly covered row (a double meets every padded blocker).
This is a lower bound for the budget of any full attachment extending
that same cover: other restrictions involving exterior columns are
omitted. Reject covers with this lower bound above the budget.
