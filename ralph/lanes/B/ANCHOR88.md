# Anchors for the remaining e88 slices (hand, pending review)

Let H be a triangle-free graph on 30 vertices with 88 edges and alpha <= 8.
For x of degree d, set Z(x) = sum of the degrees of its neighbors and
`b(x) = 88 - Z(x)`; the latter is the edge count of H minus the closed
neighborhood. By GR Table 3, d >= 3: degrees 0 and 1 leave too many vertices,
and d = 2 gives b <= 84 on 27 vertices, below 85. Also d <= 8.

For this lemma, assume H has **none** of the following roots:

| Degree | Dual edge counts already covered or programmed separately |
|---:|---:|
| 5 | <= 58 (prefix) |
| 6 | <= 51 (prefix) |
| 7 | <= 43 (prefix plus e43 tail) |

Then there are at least four vertices x for which:

1. either d(x) = 6 and b(x) = 52, or d(x) = 7 and b(x) = 44;
2. every neighbor of x has degree at least 5 in H.

## Proof

The lower bounds on b at degrees 3..8 are (73,65,59,52,44,35).
Write n_d for the number of degree-d vertices. Double counting gives
`sum_x (d(x)^2 + b(x)) = 30 * 88`: each degree d is counted d times in
`sum_x Z(x)`. The lower-bound terms for degrees 3..8 are
(82,81,84,88,93,99). Subtract the affine baseline `88+4(d-6)`;
its sum is 2624 because `sum d = 176`. Hence the total excess above the
lower bounds is

```
S = 16 - 6*n3 - n4 - n7 - 3*n8 >= 0.
```

Each degree-6/7 vertex not at the lower bound expends at least one of
these S units. Therefore at least `n6+n7-S` such vertices are at the
lower bounds. A degree-3 vertex has Z <= 15, so at most two of its
neighbors have degree >= 6. A degree-4 vertex has Z <= 23, so at most
three of its neighbors have degree >= 6. Thus at least

```
n6+n7-S-2*n3-3*n4 = 10+6*n3-n4
```

of the lower-bound vertices have no degree-3/4 neighbor, where the
identity uses `n6 = 26+2*n3+n4-2*n7-3*n8`.
Since `n5 = 4-3*n3-2*n4+n7+2*n8 >= 0`, combining it with the upper bound
on `n7+3*n8` from S gives `9*n3+3*n4+n8 <= 20`. In particular n4 <= 6,
so the claimed count is at least four.

## Use

Run gluing from order-23/e52 at degree 6 and order-22/e44 at degree 7
with `glueanchor -S 5 -A 58 -B 51 -C 43` and the existing edge/degree
limits. `-S 5` restricts each new neighbor's attachment size to at least
4; **it does not** impose minimum degree 5 on the full graph. Either
branch alone need not cover the complement; their union does. The lemma
does not require H itself to be maximal triangle-free. It does not turn an
unfinished e43 MTF scan into a closure.
