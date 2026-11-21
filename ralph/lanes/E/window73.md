# Degree saturation from the 73-edge window census

**Label: enum-assisted necessary bound, not a case closure.** Scope:
involution fixing 32 vertices, four independent size-six disjoint
attachments in the crown, and `δ(W)≥2`. The crown needs universal
`δ(G)≥5` as in `involution.md`, not an MTF hypothesis.

The complete 62 `(3,8;26,73)` graphs from the House of Graphs have at
most two degree-seven vertices: 15/16/31 graphs have exactly 0/1/2.
`window73.py` checks the order, edge count, triangle-freeness and absence
of independent eight-sets; `shortg` finds 62 distinct classes, agreeing
with GR Table 13 (D-C8d). The order-25, 65-edge control independently
matches all 396 classes and finds 0–5 degree-seven vertices, checking
that the census does not silently cap at two. See `window73.log`
under `scratch/E/r5_saturated` for the checks and input SHA-256.

Write `m=e(W)`, `S=Σ_{w∈W}d_F(w)`, `D=64−S` and
`P=168−Σ_{v∈∪A_i}d_F(v)`. The residual degree bound of the crown gives
`d_F(w)≤8` for `d_W(w)≥2`; every attachment vertex has degree at most
seven in F. Thus `D,P≥0`, and by summing edge counts in the four
26-vertex windows `H_i=F\A_i`,

```
Σ_i e(H_i) = 296−2D−P,      e(H_i)≥73,      2D+P≤4.
```

Let `r` count the windows of size 73 edges. Other windows have at least
74 edges, so `r≥2D+P`. Set `b_i=e(W,A_i)`. Every `w` has a neighbor in
each group and at most six W rows can be singletons in any group (the
slots of singleton rows are distinct), so each `b_i≥10`. Also
`Σ_i b_i=64−D−2m` and `P≡D (mod 2)` since the total fixed degree sum
is even. There are at least `8−D` fixed-degree-eight vertices in W.
In a 73-edge window at most two of those can be singletons in the
omitted group, since all singleton degree-eight rows have degree seven
in the window. Thus at least `6−D` rows of that group take at least two
edges, so `b_i≥14−D`. Accounting for the total surplus above 10 gives

```
(2D+P)(4−D) ≤ r(4−D) ≤ Σ_i(b_i−10) = 24−2m−D.
```

Now `8≤m≤12`: the lower bound follows from `δ(W)≥2`, and the upper
bound follows from `Σ_i b_i≥40`. If `D=2`, the left side is at least 8
and the right at most 6. If `D=1`, parity forces `P≥1`, so the left
side is at least 9 and the right at most 7. Therefore `D=0`. Parity now
forces `P` even, and `4P≤24−2m`, leaving `P=0` except that `P=2` is
possible at `m=8`. In particular:

- Every `w∈W` has fixed degree eight; each row uses exactly `8−d_W(w)`
  incidence edges across the four attachments.
- For `m≥9`, every attachment vertex has fixed degree seven and hence
  total degree nine. The moved vertices also have degree nine, so the
  entire graph would have 32 vertices of degree nine, 8 of degree eight,
  and 176 edges.
- For `m=11`, no window can have 73 edges: its omitted group would
  consume ≥4 surplus units, but the four groups have two total. Thus
  all four windows have exactly 74 edges. The four `b_i` are
  `(10,10,10,12)` or `(10,10,11,11)` up to group order. In either case
  at least two groups have the exact two-double support pin of the
  `m=12` test. This is a prospective split only; the `m=11` case is open.

This calculation has no implications when `W` has isolates or leaves,
or in the `t=2,3` crown branches.
