# Round 21 — the all-tight degree-six layer of a saturated 32/e108 graph

**Hand, pending critic.** Let `H` be saturated triangle-free, with 32
vertices, 108 edges and `alpha(H)<=8`. If `H` has at most three degree-eight
vertices, some degree-six root has `e(H-N[v])<=69`. More precisely, either
such a root exists or `n8>=4`; in the equality case `n8=4` with all degree-six
punctures at 70 edges, `H[D6]` is forced up to isomorphism, with the external
attachment restrictions below. This is not a statement about which of the
five absent critical keys are saturated or have the all-tight shape.

## Wedge count

Use B-040 (`ROUND20_SATURATION.md`): minimum degree is six, and all d6
punctures have 65..70 edges. Maximum degree is at most eight by independence
of each neighborhood. Assume all d6 punctures have exactly 70 edges, and let
`S=D6`, `s=|S|`. The degree sum gives `n8=s-8`, `n7=40-2s`.

If `v` belongs to `S`, the sum of the degrees of its neighbors is
`108-70=38` (no edges inside the neighborhood). There are two types: four
degree-six neighbors and two degree-seven neighbors, or five degree-six
neighbors and one degree-eight neighbor. Let `x` be the number of the first
type. Thus `2e(H[S])=5s-x`. B-040's equality at every degree-six root gives
only singleton and doubleton columns, so **every pair with an endpoint in
`S` has codegree at most two**.

Count length-two paths with both endpoints in `S`, without orienting them.
The middle vertices in `S` contribute `6x+10(s-x)`. Those in `D7` contribute
at least `max(0,2x-n7)`, since there are `2x` incidences and
`choose(t,2)>=t-1` for every count `t`. We can drop the nonnegative `D8`
contribution. By triangle-freeness the endpoints are nonadjacent, so the
codegree cap bounds the total by `2(choose(s,2)-e(H[S]))`. Rearranging gives

```
max(0,2x-(40-2s)) <= s(s-16)+5x,      x <= s,     x == s (mod 2).
```

- If `s<=10`, the right side is at most `s(s-11)<0`.
- If `s=11`, the right side is at most zero, with equality only at `x=11`;
  then the left side is four.
- If `s=12`, the left side is at least `2x-16` and the right side is
  `-48+5x`. Hence `3x>=32`, and parity forces `x=12`.

This only tightens **existential** root coverage: for `n8<=3` an order-25
source through 69 edges would suffice for the saturated arm of that slice.
It does not replace the 70-edge ceiling at every root or cover `n8>=4`.

## Forced 12-vertex layer when n8=4 and every d6 puncture is tight

All degree-six vertices have type one. The low layer `H[S]` is 4-regular
on 12 vertices with codegree cap two, and there are no `D6`–`D8` edges.
Fix a root `root` in the low layer. Its four row neighbors are independent,
leaving seven columns and 12 row-to-column incidences. Column sizes are
at most two; the doubleton masks are distinct because each pair of rows
already shares `root`. There are exactly five or six doubletons.

- Six doubletons would exhaust the 2-subsets on the rows, with one zero
  column left over. Each doubleton needs two low neighbors in the column
  side and can use only the complementary doubleton and the zero column.
  This would make the zero column adjacent to six vertices, contradicting
  regularity.
- Five doubletons leave two singletons. Call the missing pair `ab`, with
  other rows `c,d`. The singletons must be `x={a}`, `y={b}` because each row
  needs exactly three incidences. The `cd` column must join both `x,y`.
  Each of the other four doubletons can join only its complementary
  doubleton and the one disjoint singleton; it needs both. This forces all
  column-side edges (and already fills `x,y` to degree four).

On the low layer the pairs of codegree one form four disjoint triangles
(these are not edges of `H[S]`):
`{root,x,y}`, `{a,b,cd}`, `{c,ad,bd}`, `{d,ac,bc}`. The remaining low
nonedges have codegree two; this follows by taking literal intersections in
the forced adjacency list. A degree-seven vertex can therefore attach to
multiple low vertices only within one triangle of this auxiliary graph,
and each low pair can be used by at most one degree-seven vertex. If `h_i`
counts degree-seven vertices with `i` low neighbors, `i<=3`, then
`h_2+2h_3-h_0=24-16=8`, while `h_2+3h_3<=12` from the low pair budget.
In particular `h_0+h_3<=4`.

## Fixed controls and decision

`src/r21_tight_controls.py` checks literal triangles, independent subsets
and common-neighbor intersections in C5, C13(1,5), Clebsch (tight wedge
budget), K4,4 (adverse; saturated but fails codegree two), and the forced
12-vertex layer. The latter has independence number four and the exact
12 asserted codegree-one pairs. A separate short integer loop checks the
degree-sum and wedge arithmetic. `scratch/B/logs/r21_tight_controls.log`:
0.02 CPU-s (under 0.000006 core-h), 8,564 KiB RSS, exit 0.

No target data touched, no catalogue scan, no descent, no proof/archive
replay and no solver. No independent input and no calibrated end-to-end
coverage price. All five criticals remain missing; no floor, distribution,
or U88 change. Keep parked per critic.
