# Swapping an equality anchor into the mixed B pivot

## Scope and premises

Use only the mixed e168 pin `(n6,n7,n8,n9)=(2,7,4,27)` of
`residual_mixed_windows.md`, with all its strip premises. Write `a`
for A's path/leaf centre and `b` for a noncross B pivot of degree
eight. Set `D_x=N_G(x)∩X` for strip anchors, and `j=|D_a∩D_b|`.
All pairs of noncross opposite pivots have exactly their
`X`-intersection as codegree. Here `|T_b|=23+j` and `1≤j≤4`.

The additional finite premise is that every weak order-21 3+4
marked core has **singleton** deficit at the small side's cross
endpoint. From the rebuilt 1,118,436 order-21 `(3,7)` catalogue, G's
independent pruned/unpruned selector and A's cross-edge-first selector
all give the same 6,160 ordered marks, all with that singleton deficit
(`scratch/G/round10/short-anchor.full.keys`,
`scratch/A/strip11/short.crossfirst.full.keys`,
`scratch/A/strip11/short.cnf.log`). This is **enum**, not a universal
hand result without the class premise.

## The swap (hand, conditional on the finite premise)

Suppose an anchor `s` on the retained **B** side is noncross and
has equality `d_{T_b}(s)=|T_b|−22=1+j`. Delete its closed
neighbourhood in `T_b`. The remaining order-21 `(3,7)` core is a
weak 3(B)+4(A) mark. In particular **all three double signatures**
among the three old B anchors occur in this core (the deficit is a
singleton). Therefore the retained B hole must be `{s,t}` for some
anchor `t`, and the other B hole already involves `b`. The other
hole cannot also contain `s`: matching holes are disjoint, while
intersecting holes have their common endpoint at the cross anchor,
and `s` is noncross. Thus `s` has exactly one missing B pair and
`d_G(s)=1+4+3=8`. The double `{b,s}` is present, with its unique
exterior vertex `z`. In particular `D_b∩D_s={z}`.

Put `τ = 1[z∈D_a]` and now pair `a` with `s` in place of `b`.
Since `s` has no edges to retained anchors, its original window
degree is `|D_s\(D_a∪D_b)|`. Therefore the exchanged codegree is

```
j' = |D_a∩D_s| = 7−1−(1+j)+τ = 5−j+τ.
```

In the new window `T_s`, the original pivot `b` is again noncross
and `d_{T_s}(b)=7−1−j+τ=1+j'=|T_s|−22`. The swap is reversible.
Both B pivots are degree eight and have the same admissible strip
shape, so the existing full `j=4` exclusion (A-013) applies to either.
Consequences, using the certified named scopes as premises:

1. At `j=1`, `j'∈{4,5}`. Order ≤27 forbids 5 and A-013 forbids 4.
   Consequently there is **no B-side equality anchor** for the d8
   order-24 slice, in either B shape. This removes all 30,800 B-small
   structural roles from the direct order-24 list of 49,597, leaving
   the **18,797 A-small roles** outside this argument.
2. For *any* d8 B-side equality pair, after A-013 the only unordered
   possibilities for `(j,j')` are `(2,3)` with `τ=0` or `(3,3)` with
   `τ=1`. Use a pivot of codegree 3, leaving a marked order-26
   window with an equality B anchor of degree 4. The window has
   `δ≥3` by `R(3,7)=23`; G-033 excludes `δ=3`, so `δ=4` is
   the only remaining B-side equality target. This is a reduction
   to a new slice, **not** an exclusion of that slice.

For d9, both holes avoid `b`. The singleton deficit would force both
to meet `s`, impossible in either B shape. Lane A independently
submitted that separate d9 corollary. Neither argument excludes
equality with `s` on A, exterior minima, crossed pivots, or a whole
degree distribution.

## Alternative A-side pivot (hand identity only)

If the equality anchor instead lies on A, it is the other leaf or
one of the full noncross anchors. Put `ε=d_G(s)−8∈{0,1}`. Then
`|D_s|=7+ε`, `|D_s∩D_a|=ε`. With the original B pivot of degree
`d` and codegree `j`, let `τ=|D_s∩D_a∩D_b|`. Swapping A's centre
out gives codegree `d−2−j+τ` and window order `28−ε−j+τ`; the
restored centre has degree `6−ε−j+τ`, again equality. Both order-24
cases therefore exchange to codegree at least five. This is not
the centre-pivot case of A-013 and has no measured proof price.
