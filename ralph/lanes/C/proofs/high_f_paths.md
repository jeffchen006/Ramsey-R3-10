# Simultaneous cross-edge bounds on three-root components

Use the P3 partition in `path_three.md`. For each codegree-six
pair, use the report's cross-edge count f(u,v)=e(N(u)\N(v),
N(v)\N(u)). For the incident pairs of the marked P3, write

    l = e(Y,B2+B1),   r = e(Z,B0+B1),   b = e(Y,Z).

The edge identity for its 22-vertex residue becomes

    e(X) = 45 + l + r + b.

This relates two cases of the report's f* split at once. In
particular, if f*>=8 then l,r>=8 for every P3, while the converse
need not hold. This does not apply to isolated pairs, and neither
condition is imposed in the unrestricted P3 sweeps.

For diagonal five let the two B1 vertices be a and c. Hall on
each wing into its eligible three central vertices forces each
of a,c to meet both wings, and their joint neighbours must
contain at least two vertices on each wing. As before the wing
graph has alpha<=4 (otherwise add the five vertices of T).

If l=9, then a and c both see all of Y. Their Z-neighbours must
avoid Y by triangle-freeness, and there are at least two such
vertices by Hall. This is an independent five-set with Y, a
contradiction. If l=8, the single missing incidence must be
between Y and some B1 vertex, say c, since otherwise the same
argument applies. Let y* be the omitted Y vertex. A Z-neighbour
of a has no Y-neighbour, and there can be only one such vertex
z0 by alpha<=4. A Z-neighbour of c has Y-neighbours only in
{y*}. By the joint Hall condition, there is such a neighbour
z1 other than z0; its Y-neighbourhood is exactly {y*}. The third
Z vertex has a neighbour in Y\{y*}: otherwise the latter two
Y vertices together with all of Z form an independent five-set.
Thus c cannot hit this third vertex. The two B1 vertices send
at most three incidences to Z, and B0 is a singleton, so r<=6.
By reversal, if r>=8 then l<=6. Hence **no diagonal-five P3
has both incident pair counts at least eight**.

At diagonal four, B1 is a singleton. If both l=r=9 it sees
all of both wings, so Y--Z has no edges. Then T+Y+Z is an
independent 10-set. At diagonal three and l=r=9, the only
variable boundary edges are Y--Z. Conditional on the checked
diagonal-three upper result e(X)<=64, we have b<=1. Thus
the f*=9 P3 branch has only two fixed layouts at diagonal
three, with e(X)=63 and 64, and no layouts at the other
diagonals. Their 60+59 residue tests are not yet run.

For l,r>=8 and s=3 or 4, each 3-by-3 incidence block is full
or misses exactly one edge. If the hole is present, only its
row and whether its central endpoint belongs to B1 matter:
each B0/B2 can be freely permuted and B1 has at most one vertex.
Together with the nine-bit Y--Z graph, these specify every
boundary edge. The script `p3_high_f.py` covers these choices
modulo independent wing permutations and reversal. It uses
e(X)<=64 to avoid unnecessary wing graphs. Its fixed filters
reject only known necessary boundary violations; its output
is a cover, not a proof that any layout extends or fails to
extend. The same construction recovers the exact planted C21
P3 boundary at arm threshold 3 (2-by-2, one hole per arm).
