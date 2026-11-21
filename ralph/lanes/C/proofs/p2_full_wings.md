# Complete-wing pairs: common-support budget and smaller windows

Let G be triangle-free and d-regular with alpha <= d. Let u,v be an
independent pair of codegree k and use C,Y,Z,X as in `isolated_pair.md`.
Write m=d-k and suppose the Y--Z edges form a complete K(m,m), with
m>=1. Isolation is not needed unless stated. Let `S_Y` and `S_Z` be
the vertices of X meeting Y and Z respectively. They are disjoint by
triangle-freeness. Every x of X must meet C, because otherwise it must
hit both independent d-sets C+Y and C+Z, which is impossible.

## Common-support budget

For each c in C let `L_c` be those x in X whose only neighbour in C
is c. Such vertices are independent, since they share c. At most one
of them avoids Z: two such vertices together with (C minus c)+Z would
form an independent (d+1)-set. Likewise at most one avoids Y. Each
x avoids at least one wing, so |L_c|<=2. If |L_c|=2, exactly one is
in S_Y and one in S_Z; if L_c has a vertex avoiding both wings, that
vertex is the only member of L_c.

Let n1 be the number of vertices with a single C-neighbour. Let E be
the sum, over x in X, of `max(0,deg_C(x)-2)`. Each c sends d-2
edges to X, its only neighbours outside X being the two roots.
Consequently

    k(d-2) = 2|X| - n1 + E,    n1 <= 2k,    E <= kd - 2|X|.

For (d,k,|X|)=(9,6,26), this gives n1=10+E, E<=2, and at least
four c have two singleton attachments. Also if q of the singleton
vertices avoid both wings, n1<=12-q and E<=2-q. These assertions
apply to an individual complete-wing pair, regardless of isolation.

## No two complete-wing maximum-codegree pairs in this arrangement

Now take R(6) with f*=9, so every codegree-six pair has complete
wings. Suppose y1,y2 in Y have codegree six. Their shared neighbours
include `{u}+Z`, four vertices. For the pair y1,y2, the third Y
vertex y3 and the old root v are both in its residue X': neither is
one of those new roots or adjacent to either (Y is independent and
v has no neighbours in Y). In that pair's common neighbourhood C',
y3 meets at least u and all three Z vertices, and v meets all three
Z vertices. Applied to this second pair, the budget gives E'<=2,
but the two distinct residue vertices already contribute (4-2) +
(3-2) = 3, a contradiction. By reversing the original pair there
is no codegree-six pair inside Z either.

More generally the same contradiction applies when it is just the
two marked pairs that both have full wings, even if other codegree-six
pairs do not. For general m>=2, every remaining Y sibling has at least
m+1 common-support neighbours for the second pair and v has at least
m, so the analogous lower bound is m(m-2).

## Residue reduction for f*=9

For y in Y its X-neighbourhood is an independent five-set (its other
neighbours are u and the three Z vertices). Any two of the three
five-sets intersect in at most one: their two Y vertices already
have u and Z in common, and their codegree is at most five by the
preceding argument. Thus |S_Y|>=15-3=12 by inclusion-exclusion;
similarly |S_Z|>=12. Their union lies in X of size 26 and is disjoint.
In particular at most two X vertices avoid both wings.

Orient so `s=|S_Y|<=|S_Z|`; then s is 12 or 13. Put `K=X\S_Y`.
Deleting the closed neighbourhoods of the independent three-set Y
leaves `H={v}+C+K`, a (3,7)-graph of order 33-s with a marked
degree-six vertex v with neighbourhood C. Indeed the removed set is
`{u}+Y+Z+S_Y`, and an independent seven-set of H would extend by Y.
Deleting N_H[v] leaves K, a (3,6)-graph of order 26-s. In K the three
Z-neighbourhoods are independent five-sets meeting pairwise in at
most one. If s=13, |S_Z|=13 and they cover all of K. If s=12, their
union can be 12, 13 or 14. These are necessary conditions only.

Within K (which avoids Y) there is at most one C-singleton per c.
Therefore e(C,K)>=2|K|-6. Likewise S_Y avoids Z and has at most
one singleton per c, giving e(C,S_Y)>=2s-6 and e(C,K)<=42-(2s-6).
Equivalently `sum_{c in C} deg_H(c)` lies in `[2|K|,2|K|+2]`.
For s=12 this is [28,30], and for s=13 it is [26,28]. This narrows
the rooted H21 cover, with no claim of extension or refutation.

## Extra marked-window filters

For fixed H, let `E_K=sum_{x in K} max(0,deg_C(x)-2)`. If a proposed
packing of the Z-neighbourhoods leaves q singleton-C vertices outside
its union, those q vertices avoid both wings. Thus `E_K+q<=2` by the
budget. For any x in K, its codegree with v in G is
`deg_C(x)+deg_Z(x)`. This is <=5 because v's only codegree-six
partner is u (the complete-arm P3 argument plus no-P4). Also two C
vertices already share u and v, so at most four common neighbours
in K are allowed. Equality forces a codegree-six partner, and each
C vertex has at most one such partner. These are necessary tests
in the `strong21` sieve; they do not assume X is already constructed.

`p2_wing_windows.cpp` implements the core/marked-window projections
and runs exact smaller positive checks on C22. Its count depends
only on the supplied known complete catalogues; the hand reduction
itself does not depend on completion software.
