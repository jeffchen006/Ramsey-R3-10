# e170 equality roots with coincident double sites (hand reduction)

Use G-043 (`e170_equality_signatures.md`): in a target MTF graph at
`e=170` with two degree-six roots, they are adjacent, the wings `L,R`
have five anchors each with just `L0-R0` crossing, and the shared
exterior `W` has 28 vertices and 86 internal edges. On either side,
there are four private sites per anchor and eight distinct double
supports, all edges of a `K5` except for two holes. The cross endpoint
belongs to a hole on each side. Restrict to `h=8`, meaning the two
eight-element sets of double sites in `W` are the same.

## Incidence grid

The remaining twenty sites are private on both wings. Let `M[i,j]`
count these with support `{Li,Rj}`; each margin is four. By the
private-cell matching lemma in `signature_matchings.md`, the four
sites at `Li` have a matching to `R−{R0}` of size at least
`3+[i=0]` (these four anchors form the peer-root private cell).
Each site has exactly one right neighbor, so the number of nonempty
noncross columns in row `i` is at least that size. Transpose to
get the column statement. Triangle-freeness sets `M[0,0]=0` and
row/column zero must each have one site in every noncross position.
Every other row has one in column zero and needs three *distinct*
noncross positions with its three remaining sites. Therefore the
matrix is binary, and its zeros are a perfect matching through
`(0,0)`. Label the right noncross anchors to make these zeros diagonal.
The twenty sites then have distinct supports `{Li,Rj}` for `i≠j`.
This concerns incidence only, not the induced graph on the sites.

## Cover in these labels

Simultaneous `S4` on noncross labels preserves the marked crossing
and the grid. Wing exchange transposes the grid, permutes the hole
sets, and exchanges the two factors of *each* double support. No
target automorphism is needed. Each wing has 30 legal sets of two
holes; expanding the 30 scout representatives under these actions
partitions the 900 ordered pairs. The named representative
`leaf+leaf.1` has left holes `L0L4,L3L4` and right holes `R0R4,R2R4`.

With fixed hole sets, the eight sites that are double on both sides
are a bijection from left to right double pairs. Discard bijections
that put `L0,R0` on the same site (triangle). For each `i>0`, the
nonadjacent `Li,Ri` need a common neighbor by MTF. Neither root
is adjacent to both; no wing anchor can be such a neighbor (each
wing is independent); the label choice leaves no private site on
that pair. Therefore at least one double site must cover each of
those four diagonals. Enumerating the bijections with these two
filters gives 1,828 IDs for the named scheme; labels may count
isomorphic configurations more than once, which is safe for a cover.

## Ordinary local CNF and transfer

Keep all ten anchors with their one edge, the twenty grid sites,
and a chosen subset of paired double sites. For each pair of sites
introduce its edge variable. A shared anchor forces no edge;
every triple of sites has the triangle clause. For any set of
distinct sites and distinct wing anchors of total size ten, if the
anchors are independent and avoid *all* the included site supports,
require at least one edge within the included sites. Such a positive
clause is necessary regardless of the rest of the graph. Keeping
only witnessed positive clauses, as in the receipts, is a relaxation;
an UNSAT certificate suffices. No assumption about site degrees,
root edges, an internal-edge budget, or edges to omitted double sites
enters the CNF.

A contradiction for a retained double subpattern holds for every
alignment containing it, after any of the 48 allowed joint label
actions: relabel the grid sites by their off-diagonal supports,
take the retained paired doubles on their exact supports, and restrict
the graph to those sites and all ten anchors. All three clause
families remain necessary. Proof matches are combined by set union
over `(scheme, sorted double masks)`, not by adding their masses.
Thus an exact cover with bound LRATs excludes this named marked
scheme, not all aligned doubles, other overlaps, or an e170 key.
