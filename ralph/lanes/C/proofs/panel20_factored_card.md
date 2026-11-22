# The core-order-12 fifth-row gate factors across the two windows (hand)

Assume a 9-regular triangle-free completion of order 40 with independence
number at most 9 and maximum nonedge codegree at most 5. Let `U,V` be the
shores of the marked `K4,4`. Let `W` (order 16) contain the private sites
marked by `U`, and `W'` (order 17) those marked by `V`; the two windows
meet just at the unmarked site `z`. Each private site sees at least one
root of its own mark shore and no root of the other shore. The marks
record all such root contacts. Let `x ∈ W` be in exactly three `U` marks
and have three neighbors in the induced graph of `W`.

## Exhaustion in the physical left labels

Write `A=N(x)∩U`, `B=V∪{x}`, and `H=W−({x}∪N_W(x))`. The sets `A,B`
form a `K3,5`; both shores are independent. For each `a∈A`, `N(a)−B`
consists of the four sites of the physical mark of `a` other than `x`.
These sites belong to `W`, omit `z` by the mark binding, and omit
`N_W(x)` by triangle-freeness. Two of the sets cannot meet: the two
different `A` roots already have all five sites of `B` as common
neighbors, and their codegree is at most five. Thus the sets are disjoint
subsets of `H`, and their union has `3·4=12=16−1−3=|H|` sites. They
partition `H` into three independent four-sets. In particular `z∉H`,
so the distinct physical neutral `z` must be in `N_W(x)`.

This uses the assigned marks, not merely the sizes of degree classes.
Indeed the containment, disjointness and exhaustion can be checked
directly in a proposed left frame with its labelled marks. No cross-edge
is needed for that check. In frozen frame 42679 the relevant labels are
`x=0`, `z=7`; the proof excludes the in-core-neutral branch, not any
additional frame-pair ID.

## The only left input to the local restoration test

The exterior sites with no support in `B` are exactly `H`: the remaining
root of `U` sees all four members of `V`, all private sites of `W'` see at
least one member of `V`, and `z` sees `x`. Thus `alpha(H)≤4`. Vertex `x`
has three neighbors in `U`, three in `W`, and no neighbors in `V`.
Consequently its remaining neighbors are a three-set `T` in `W'−{z}`.
It is necessary that `T∪{z}` be independent in `W'`. For `b∈V`, the
pair `x,b` is nonadjacent and its common neighbors are the three roots
of `A` and precisely the sites of `T∩M_b`, with `M_b` the physical mark
of `b` in `W'`. No other sites qualify: `W−{z}` misses `V`, `z` misses
`V`, neither vertex sees a site of `V`, and the remaining `U` root
misses `x`. This is the codegree bound `|T∩M_b|≤2` for each `b`.

Let `Q_b=M_b−⋃_{c∈V−{b}}M_c` be the **original** singleton group.
The sites with singleton support `{b}` in `B` are `S_b=Q_b−T` for `b∈V`,
and `S_x=N_W(x)`. The anti-neighborhood of the other four independent
poles `B−{b}` is exactly the induced card on `H∪{b}∪S_b`, also when
`b=x`. No root of `A` can be in it, since those roots see all five poles.
The completed card is triangle-free with alpha at most five; otherwise
one could adjoin the four deleted poles to an independent six. Its root
is adjacent to all of `S_b` and to no site of `H`. For `b=x` the card is
the given `W`.

For `b∈V` the left and right windows prescribe no incidences between
`H` and `S_b`: the only common site `z` belongs to neither of those
sets. The fixed singleton sites are independent (all in `M_b`) and the
edges to the root are already as required. Consider only this individual
card condition, not consistency with other unknown edges. For any
`k=|S_b|≤3`, delete `3−k` of the three neighbors of `x` in `W` and
relabel the root and retained sites to `b` and the physical `S_b`,
respectively, keeping each label of `H`. The resulting card has the
required bounds by induced deletion and respects every prescribed
incidence. For `k=4`, a card exists exactly when there is a triangle-free
order-17 graph of alpha at most five with a degree-four root whose closed
neighborhood deletion is isomorphic to `H`. An isomorphism on the core
and an arbitrary bijection on the four singleton sites suffice, since
there are no prescribed cross-incidences between them. For `k≥5`, the
card would have at least 18 vertices, contrary to `R(3,6)=18` (see
D. Cariolaro, *On the Ramsey number R(3,6)*, Australas. J. Combin. 37
(2007), 301–304).

Define `flag(H)` as existence of the degree-four card above and put
`tau=3+flag(H)`. The old five-card test, restricted to legal rows,
is therefore exactly

```
  exists T ⊆ W'−{z}, |T|=3, with T∪{z} independent,
    and for every b∈V: |T∩M_b|≤2 and |Q_b−T|≤tau.
```

Equivalently each original group needs `max(0,|Q_b|−tau)` chosen sites;
no group may be dropped just because it starts above `tau`. The same
physical `T` is used for every pole. The only dependence on `W` is
the one bit `flag(H)`. This equivalence is only for the old card gate;
passing gives no assertion about the existence of a joint completion.

## Original sizes on the tested right roster

On an order-17 one-neutral frame the four 5-sets cover exactly 16
private sites. The excess of the sum of the four mark sizes over the
union size is four. A triple site uses up two units of excess and
occupies all three pair intersections among its three marks. Each
mark pair intersects at most once, since its two roots share the four
`U` roots elsewhere. Any further multiply-marked site must therefore
be a double using the remaining mark and one of those three. There
are exactly two such doubles, using distinct mark pairs. The original
singleton sizes are therefore a permutation of `(3,3,3,4)`; at
`tau=3` a row must hit the physical size-four group, while at `tau=4`
every legal row passes. This alone does not guarantee there is a legal
row, or one hitting the required size-four group.
