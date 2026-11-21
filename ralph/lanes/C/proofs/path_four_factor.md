# Four consecutive codegree-six roots: boundary-side constraints

This is the hand bridge for the P4 CNFs. It is asserted for **four
distinct consecutive roots** in J, the graph of codegree-six pairs in
Case R(6), not for an induced subgraph. It does not use the C8 or P5
exclusions. The census cover and block definitions are in
`codegree_six_paths.md` and `path_windows.md`.

## Layout and forced edges

With roots v0,v1,v2,v3, the matched row A contains X, Y, Z, v0, v3 in
that order, with |X|=20 and |Y|=|Z|=2. In A, N(v0)=Z+{v3} and
N(v3)=Y+{v0}. The deleted part consists of D0,D1,D2,D3 (in that order,
each of size three), then v1,v2. The root neighbourhood lists inside
the deleted blocks are

| root | D-block neighbours |
|---|---|
| v0 | D0,D1 |
| v1 | D0,D1,D2 |
| v2 | D1,D2,D3 |
| v3 | D2,D3 |

The middle roots have no neighbours in A. No two blocks other than
D0,D3 can meet by an edge, since every other pair and each single
block has a common root. The boundary sides L=D0+D1 and R=D2+D3 are
therefore independent. Every L-vertex is adjacent to v0 and thus sees
no vertex of Z and does not see v3; every R-vertex symmetrically has
possible A-attachments only in X+Z, besides its required v3. Hence the
only initially unknown edges are L--(X+Y), R--(X+Z) and D0--D3.

The 14 deleted vertices have 18 edges at v1,v2 and f=|E(D0,D3)|
other internal edges. Summing their degrees shows
e(A)=180-(14*9)+(18+f)=72+f. In the C21 control the same calculation
with block size two and degree six gives e(A)=15+f.

Regular triangle-free G with alpha at most its degree is maximal
triangle-free: any added triangle-free edge would make a new
independent neighbourhood of size degree+1. For y in Y, z in Z,
a common neighbour is possible only in X. Indeed Y avoids R, Z
avoids L, neither middle root sees A, and neither endpoint root
sees both wings. The wings are internally independent. Thus yz is
present if and only if their X masks are disjoint. This is the exact
filter used between the 2,454-row and 1,356-row catalogues. An analogous
rule holds for a in D0, b in D3: they share no root, no block vertex
can be adjacent to both, and their only common possible neighbours
in A are in X. Again ab is present if and only if their X masks
are disjoint. This second rule is not imposed as a separate filter;
it follows from the base triangle and maximality clauses in a joined CNF.

## Eager rows on one boundary side

For each independent set I in A not containing v0, put
P = I intersect (X+Y). For S=L or S=D0 write u_S(P) for the number
of vertices of S having no neighbour in P. A vertex in L has no
neighbour in I if and only if it has no neighbour in P: any of its
non-v0 neighbours in A must be in X+Y. Taking these vertices with I
gives an independent set of size |I|+u_L(P), so

    u_L(P) <= 9 - |I|.

The middle root v2 sees no A-vertex and no D0-vertex. Taking it with
I and the available vertices of D0 gives a second necessary row:

    u_D0(P) <= 8 - |I|.

Reflecting the root sequence gives the two corresponding rows for R
and D3, with I avoiding v3, with projection onto X+Z, and with v1
as the extra root. These are exactly the independence tests restricted
to the induced graph on A, the chosen boundary side, and v1,v2,
assuming alpha(A)<=7: if a nonempty L subset is selected, v0 and v1
are unavailable; v2 can accompany it precisely when it is contained
in D0. If the subset is empty, alpha(A)+2<=9 already. The analogous
argument holds on the right. A joined CNF enforces both projections;
it need not enforce the entire 40-vertex alpha bound to refute the row.

For a common projection P retain the smallest right-hand side. If
Q is a proper subset of P, then u_S(P)<=u_S(Q), so a row with
right-hand side at least that of Q is implied by Q and may be dropped.
This pruning only saves clauses and is not needed for soundness.
For each vertex, the CNF availability literal is forced true when
all incident P-edges are false. When none is fixed true and there
are at least two variable edges, encode
`availability OR edge_1 OR ... OR edge_t`; when there is one use the
negated edge itself. If a fixed true edge occurs use a false literal,
and if no edge is possible it is true. Bounding the number of true
literals by the stated row gives a necessary inequality. A genuine
completion can set each availability variable to its semantic value,
so not encoding the reverse implication does not lose it.

## Base CNF and projection

Initial bounds are the layout above. The preprocessing of
`path_four_forced.py` maintains F subset E(G) subset P, F the forced
edges and P the permitted edges, by the following implications:

- At the required degree, all other incident edges are false; if
  the possible degree equals the required degree, all permitted ones
  are true. Forced degree larger or possible degree smaller is a
  contradiction.
- One forced common neighbour forbids an edge. More than the allowed
  codegree of forced common neighbours is a contradiction; at the cap
  no additional common neighbour can arise, so if one incidence is
  forced true the other is false. For a forced edge every common
  neighbour is forbidden in the same way.
- Zero possible common neighbours forces an edge by maximality. For
  a forbidden edge with exactly one possible common neighbour both
  incidences must be true.

Each implication preserves the invariant, including when possible
sets are read before additional restrictions: using stale upper
bounds in a step can only omit a restriction, not force an invalid one.

A two-side CNF uses all remaining edge variables. A one-side CNF
also includes every D0--D3 edge variable, keeps every known edge or
nonedge, and leaves any unknown attachments on the other side
unobserved. An exact degree d among m total entries gives both
`known true <= d` and `known false <= m-d`, with all constants
counted and unknown entries omitted. The same counting encodes f
among the cross positions (all observed). Triangle clauses are used
only when their variables are observed. For every pair other than
a fixed edge, known shared-neighbour selectors are equated to the
conjunction of the two relevant incidences; their sum is at most
the codegree cap. The MTF disjunction of the edge and a common
neighbour is used only if the edge is observed and *all possible*
shared-neighbour incidences are observed. These rules are necessary
even when not all possible attachments are observed; in the joined
CNF they encode all three conditions exactly. Named constants are
implemented by a unit true literal and its negation. Cardinality rows
use the sequential-counter encoding, with only observed nonconstant
literals passed to the encoder. The eager constraints then use the
chosen side(s). No dynamic independent-witness cuts are used in the
retained LRATs.

## Pinning cross shapes

In the two lower strata f=5 or 6, split instead of relying on the
un-pinned solver. Every f-edge labelled 3-by-3 Boolean matrix is
enumerated. Keep the numerically least matrix over independently
permuting the rows and columns, with bit `3*i+j` representing
D0[i]--D3[j]. This is complete: these permutations just relabel
the unmarked vertices within D0 or D3, fix A pointwise and preserve
all required root incidences. No swapping of the two sides and no
permutation of a marked wing is assumed. Append all nine unit settings
for the chosen matrix (including zero bits). Every full model extends
at least one of these CNFs after relabelling, whether or not the
preprocessor has already forced some of its entries. A missing
pattern among the proofs leaves the row open.

This construction scales to the C21 control by using degree and alpha
bound six, block size two, and codegree bound four. No full 40-vertex
conclusion is claimed from SAT of a relaxation. Conversely, complete
proof coverage here would exclude P4 in R(6) and hence any J-component
of order at least four, since J has maximum degree two and no triangles.
It would not address the two-root components or any of the three
possible diagonals of a three-root component.
