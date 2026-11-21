# Large fixed sets for involutions

**Claim `hand`: `(p,f)=(2,34)` is impossible for a `(3,10,40)`-graph.**
No maximality assumption or classification of automorphisms is used. Inputs:
the universal degree bounds `4 <= d <= 9` (L1), F6–F7 / F10 of
`notes/symsat.md`, `R(3,6)=18`, and `e(3,8;27)=85` (D-E8,
`notes/DEPENDENCIES.md`, GR Table 13).

Let `F` be the fixed set and `O_i` the three moved pairs. If a moved pair
contains an edge, its endpoints have no fixed neighbors by F6. Their
neighbors outside the pair are disjoint by triangle-freeness, and are
subsets of the four other moved vertices. The two endpoints have equal
degree, so each has degree at most 3, contradicting L1.

For each (now independent) pair, let `A_i = N(O_i) ∩ F`. By F7 applied
to this pair, `|A_i| <= 7` and `34 - |A_i| <= 27`; hence `|A_i| = 7`.
In fact, each vertex of `O_i` has exactly two moved neighbors by F10,
since the closed neighborhood of the pair has at least 13 vertices and
at most `2+7+2(9-7)=13`. Every two moved pairs are joined: otherwise
their union is independent, with at least `34-14=20` fixed vertices
nonadjacent to it. Those 20 must have independence number at most 5,
contradicting `R(3,6)=18`. Consequently the three `A_i` are pairwise
disjoint (a common fixed neighbor would form a triangle along a joining
edge), and each is independent (it is in a moved vertex's neighborhood).

Let `W = F \ (A_1 ∪ A_2 ∪ A_3)`, of size 13, and `H_i = G[F \ A_i]`.
Each `H_i` has 27 vertices and independence number at most 7, since
an independent set in `H_i` can add `O_i`. So `Σ_i e(H_i) >= 3·85=255`.
An edge of `G[F]` between distinct `A_i` appears in exactly one `H_i`,
one from an `A_i` to `W` appears in two, and one within `W` appears in
three. No edges lie within any `A_i`. Thus

```
Σ_i e(H_i) = e(G[F]) + Σ_{w∈W} d_{G[F]}(w).
```

There are six edges within the moving set (six moved vertices of moving
degree two) and `3·2·7=42` from it to `F`. By the degree cap there are at
most 180 total edges, so `e(G[F]) <= 132`. Also `Σ_{w∈W} d_{G[F]}(w)
<= 9·13=117`. Together this gives `255 <= 249`, a contradiction.

Calibration: `calibrate_involution.py` checks the crown/edge count on
the Petersen graph as `KG(5,2)` (swap 0 and 1), using exact graph checks
on the resulting graph and the three smaller `F\A_i`. It also checks
all abstract phase patterns of the complete single-matching quotient
for three through five moved pairs. Logs: `scratch/E/cal_involution.log`.

## Order 2, 32 fixed points: structural reduction, not a closure

Use the universal (checked) `δ>=5` cited in sec. 5. An edge pair has no
neighbors in F and its endpoints have disjoint external neighborhoods
within the other six moved vertices, giving `d<=4`. Thus all four moved
pairs are independent. Since `32-2·7=18`, the same `R(3,6)` argument
makes their quotient complete and their `A_i` pairwise disjoint. No
inter-pair block is double: a third pair has a neighbor in each of the
first two at every vertex, giving a triangle with a complete block.

In a complete single-matching quotient, label each pair by bits 0/1
and mark a matching by the XOR of the endpoint bits. Parity zero on
any triple yields a triangle, so all triple parities are one. Switch
pair labels to make the edges at pair zero have marking one; all
remaining edges then have marking one too. This is the crown graph
`K_{4,4}` minus a matching. In particular each moved vertex has moving
degree 3 and `5 <= |A_i| <= 6` by F7 and the degree cap. The same
counting identity generalizes to `Σ_i e(H_i)=2e(G[F])+Σ_W d_F(w)`.
If `t` is the number of size-6 sets, GR gives the lower bound
`340-12t` (85 at 27 vertices, 73 at 26); the degree bound gives
`364-13t`, so this alone does not rule out any `t`.

### Subcase `(2,32,a=5)` (`enum`)

If the maximum attachment is 5, all four `A_i` have size 5. So `|W|=12`,
and `α(W)<=5`: an independent set in `W` can add one entire side of the
crown, of size 4. Every `H_i=F\A_i` has order 27 and `α<=7`; hence its
maximum degree is at most 7 (its neighborhoods are independent). Write
`d_F,d_W` for degrees in the respective induced graphs. For `w∈W`,

```
3 d_F(w) + d_W(w) = Σ_i d_{H_i}(w) <= 28.
```

In particular if `d_W(w)>=2` then `d_F(w)<=8`.

Strip isolates and leaf-neighbor pairs iteratively from `G[W]`. For an
isolate the independence number drops by 1; for a leaf and its neighbor
it also drops by exactly 1 (some maximum independent set contains the
leaf). Thus `|V|-2α`, initially at least 2, never decreases and grows by
1 for each isolate removed. A triangle-free graph of order ≤7 has
`|V|-2α<=1` by `R(3,2)=3`, `R(3,3)=6` (or direct inspection at orders
0–2). So the remaining core has ≥8 vertices, all originally of degree
≥2 in `G[W]`. Therefore `Σ_W d_F <= 8·8+4·9=100`. The 20 vertices in
the `A_i` each have two moved neighbors, so `Σ_{F\W}d_F<=20·7=140`.

By the edge incidence count above,

```
340 <= Σ_i e(H_i) = Σ_{F\W}d_F + 2Σ_W d_F <= 140+200 = 340.
```

Equality forces all four `H_i` to have 85 edges and exactly eight
vertices of `W` to have degree ≥2 in `G[W]`. The core must consist of
those eight and have `α<=3`. No isolates could have been stripped:
the remaining graph has `|V|-2α<=2` by `R(3,3)=6`. The other four
vertices of `W` must form two isolated edges: when stripped in
leaf-neighbor pairs, both endpoints have original degree ≤1, or else
one of the eight core vertices would have been removed. These four
vertices have `d_F=9` by equality. For each of them,
`Σ_i d_{H_i}=3·9+1=28`, so each has degree 7 in every `H_i`.

Necessary condition for even one `H_i`: an induced `2K2` of degree-7
vertices and a disjoint 8-vertex graph of `α<=3` anticomplete to those
four vertices. `check_min27.py` checks the four minimum-edge classes
from McKay's list; none has this induced pattern. Completeness at
85 edges is cross-checked by the independently published count of four
classes (GR Table 13). This uses only a tiny finite enumeration and
is labeled `enum` pending critic review, not DRAT `cert`.

Evidence: `ralph/lanes/E/min27.g6`, `ralph/lanes/E/check_min27.py`,
`scratch/E/min27_check.log`. Obtained with `gzip -dc r38_27.g6.gz |
opt/bin/pickg -e85` (input SHA-256
`9a2e9723342872c95327c5bc194f5d22764b87f079047bcffcba359abf5cc7b5`).
Run `python3 ralph/lanes/E/check_min27.py ralph/lanes/E/min27.g6`.
The `a=6` case, i.e. `t∈{1,2,3,4}`, remains open.

### A sieve for `t=1` (`enum` exclusion only when W has an isolate)

Now the attachment sizes are `5,5,5,6`, so `|W|=11`, `α(W)<=5`.
As in the `a=5` bound, degrees in all four `H_i` are at most 7, and
`d_W>=2` implies `d_F<=8`. If `W` has an isolate, the leaf/isolate
stripping argument gives a core with deficiency `|V|−2α>=2`, so at
least eight high-degree vertices of `W`. Thus

```
328 = 3·85+73 <= Σ_i e(H_i) = Σ_{F\W}d_F+2Σ_W d_F
                                   <= 21·7 + 2(11·9−8) = 329.
```

There cannot be nine high vertices, and all three low vertices have
`d_F=9` since reducing another W degree would cost 2. As before the
eight high vertices form the core of `α<=3`; three low vertices are
`K2+K1` (exactly one isolate stripped, as the final core deficiency is
at most 2). The pair endpoints have degree 7 in every `H_i`; the isolate
has `Σ_i d_{H_i}=27` so has degree 7 in all but one. Since the total edge
slack is one, some size-27 residual `H_i` both has 85 edges and has all
three low vertices of degree 7. In it, the vertices outside `W` must
partition into independent sets of sizes `5,5,6`. The two endpoints
of the low edge each touch exactly two vertices of each such set
(their sum of residual degrees was 28); the isolate touches two or
three per set (its fixed degree 9 and all residual degrees at most 7).

`check_min27.py` checks these necessary partitions, with a planted
positive control and an edge-deletion negative control: the four
graphs have 3,3,12,12 candidate core/low triples, but none partitions.
This does not address `t=1` when W has no isolate. Even without an
isolate, stripping shows ≥5 vertices of degree ≥2 (deficiency starts
at one), yielding `Σ_i e(H_i) <= 335`. Some size-27 residual must
therefore have `e<=87`; from GR Table 13 this gives only 1,470 possible
anchor classes (4+92+1374), not the whole 477,142-graph list.

## Order 2, 28 and 30 fixed points: two more hand exclusions

**Claims `hand`: `(2,28,a=5)` and `(2,30,a=6)` are impossible.**
For `f=28` and `a<=5`, or `f=30` and `a<=6`, prove the moved-pair
quotient is complete even if some pairs contain their internal edge:

- Two unjoined independent pairs would give an independent 4-set
  with at least `f−2a>=18` fixed nonneighbors, forbidden by `R(3,6)=18`.
- For an unjoined edge pair and an independent pair, take one member
  of the former and both of the latter, giving an independent 3-set
  with at least `f−a>=23` fixed nonneighbors, forbidden by `R(3,7)=23`.
  The edge pair has no fixed neighbors by F6.
- For two unjoined edge pairs, take one member of each, giving an
  independent 2-set with all `f>=28` fixed vertices nonadjacent,
  forbidden by `R(3,8)=28`.

With `k=(40−f)/2` moved pairs, every moved vertex has at least
`k−1` moved neighbors (at least one per other pair by invariance).
Consequently an orbit attaining `a` has `a<=9−(k−1)=10−k`, which
excludes `a=5` for `k=6` and `a=6` for `k=5`. Neither the `δ>=5`
certificate nor a computed catalogue is needed in this argument.

The remaining graphs in these ranges have the crown layout, with
possibly some internal pair edges: the double-matching obstruction
and phase argument above apply unaltered. A full side remains
independent, giving `α(W)<=9−k`. This also rules out `a<=3` for
both `f=28` and `f=30`: the disjoint fixed attachment sets have total
size at most `ka`, so `|W|>=28−6·3=10>8` when `f=28`, and
`|W|>=30−5·3=15>13` when `f=30`. Those low `a` cases previously
had enumeration exclusions. Still open in these ranges: `(2,28,4)`
and `(2,30,{4,5})`.
