# A forced degree-nine four-cycle at e=162 (hand, not an exclusion)

Assume the inherited MTF bounds `t8 >= 97` and `t9 >= 88`. In the
degree distribution `(n6,n7,n8,n9)=(0,0,36,4)` at 162 edges, the four
degree-nine vertices induce a 4-cycle.

Indeed, for degree eight, `Z(x)=64+|N(x) intersect V9| <= 162-97=65`.
Hence each degree-eight vertex has at most one degree-nine neighbor.
For degree nine, `Z(x)=72+|N(x) intersect V9| <= 162-88=74`, so the
induced maximum degree on `V9` is at most two. Any nonadjacent pair
in `V9` must have a common neighbor because G is MTF. That neighbor
cannot have degree eight by the first bound. Thus `G[V9]` is connected,
triangle-free, and has diameter at most two and maximum degree at most
two. On four vertices it is necessarily the 4-cycle (the only other
connected triangle-free possibility is the 4-vertex path).

## Twin residuals

Let `v0,v1,v2,v3` be the cycle and `A_i=N(v_i) minus V9`. Each `A_i`
is independent of size seven, and these four sets are disjoint. The
remaining set `T` has size eight. Every vertex of T has a neighbor in
each `A_i` by MTF applied to the pair with `v_i`. Every vertex of `A_i`
also has a neighbor in `A_(i+2)` by MTF applied to the opposite high
vertex: its only V9 neighbor is `v_i`, not adjacent to `v_(i+2)`.

Write `p=e(A0,A2)`, `q=e(A1,A3)`. All four degree-nine residuals have
88 edges because `Z(v_i)=74`. For the opposite pair `v0,v2`, the common
neighbors are exactly `v1,v3`, whose degrees are both nine. The residual
`G - (N[v0] union N[v2])` is `A1 union A3 union T`, a `(3,8;22)` graph
with `162-2*74+18+p=32+p` edges. Here the 18 restores the duplicated
degree sum contributed by the two common neighbors and p restores
the edges between the exclusive neighbor sets counted twice. Interchange
the opposite pairs to get a second `(3,8;22)` graph on `A0 union A2
union T`, with `32+q` edges. Thus `p,q>=10` by the published minimum 42.
Both bipartite graphs between opposite A sets have perfect matchings:
an independent set of eight there would contradict the corresponding
22-vertex residual, so König's theorem gives matching number seven.

Summing the degrees of T into these two residuals gives
`e(T,A1 union A3)+e(T)=32+p-q` and its counterpart `32+q-p`.
Since each T vertex touches both sides in each residual, `|p-q|<=16-e(T)`.
There is no proven upper bound of 11 or 12 on either p or q from these
facts. In particular this reduction does not put the case in the
already-running e43 slice or close any distribution.

## The other 162-edge distribution in the U88 list

For `(n6,n7,n8,n9)=(0,2,32,6)`, also assume the checked MTF bound
`t7 >= 107`. At each degree-seven vertex the neighbor sum is
`56 + (# degree-nine neighbors) - (# degree-seven neighbors) <= 55`.
The two degree-seven vertices therefore are adjacent and have no
degree-nine neighbors. Each sees six degree-eight vertices, in disjoint
sets A and B by triangle-freeness. Both degree-seven residuals have
exactly 107 edges, so any complete degree-seven floor of 108 would
exclude this distribution without any e88 census.

The degree-nine induced graph F has maximum degree at most two, by
the inherited `t9 >= 88`. A degree-eight vertex can have at most one
degree-nine neighbor outside A and B, or at most two inside them, by
`t8 >= 97` and `Z(x)=64+(# degree-nine neighbors)-(# degree-seven neighbors)`.
The number of edges between degrees eight and nine is therefore
`54-2*e(F) <= 20+2*12 = 44`, giving `e(F) >= 5`. A triangle-free graph
on six vertices with maximum degree two and five or six edges is one of
`P6`, `C4 + P2`, `C5 + P1`, or `C6`. In the five-edge case all upper
capacities at degree eight are attained; in the six-edge case the total
slack is two. By MTF, each degree-nine vertex has a neighbor in each of
A and B, since it misses both degree-seven vertices and all their other
neighbors are in the corresponding set. These are reductions only.
