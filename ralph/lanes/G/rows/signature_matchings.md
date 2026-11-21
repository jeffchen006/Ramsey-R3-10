# Equality-root matching and contact rows (round 6)

## Matching and exact symmetry normalization (hand + enum)

Let a root `u` have `d` independent neighbors `A`, and let `H=G-N[u]`.
Write `a` for the upper bound on the independence number of `G` and
`p=a+1-d`. At equality in the private budget, there are exactly `p`
vertices in each private cell `P_i` and at most one vertex of every
double signature `ij` (see `equality_private.md`). Let `J` have the
double signatures as its edges.

The induced bipartite graph on `P_i,P_j` has a matching of size at least
`p-1+1_{ij∈J}`: its independent sets can be joined to `A-{i,j}`, and
the double `ij`, when present, is isolated from both private cells.
Thus its independence number is at most `p+1-1_{ij∈J}`; use König's
theorem. Without equality the same argument bounds the matching below
by `|P_i|+|P_j|+|D_ij|-(p+1)`, where `D_ij` is the double cell.
Also put `S_i=N(i)∩H`. Within `H`, `S_i∩S_j` is isolated from
`S_i∪S_j` and the exclusive parts are bipartite, so that matching
has size at least `|S_i∪S_j|-(a-1)`.

It is safe to pin a perfect matching by labels on each edge of a
**forest contained in J**: starting in each component, order the
next cell using the chosen matching to its already ordered parent.
Do not pin a common set of unmatched parent vertices on multiple
weak (`ij∉J`) pairs; that would be an invalid symmetry assumption.

For `e=168,d=6`, `p=4`, `J` has six vertices, nine edges and degree
range 1..4. Such a graph is connected: a disconnected graph with no
isolates has at most seven edges. Hence the tree fixes 20 actual edges.
Over the accepted 20 pins, `equality_template.py` gives exactly 3,700
labelled graphs, 14 representative `J` masks and 112 mask/pin pairs;
each pair uses the accepted floor 120 and universal degree-six rows.
Lane A independently matched the complete cover and omission/duplicate
controls (`scratch/A/pair6/g-template-audit.log`). This is a cover,
not a result about the existence of any completion.

## Cell-edge projection (hand)

For a subset `B` of `A`, let `H_B` be all exterior vertices with
support contained in `B`. Both `H_B` and `H_B+B` have independence
number at most `p-1+|B|`: append the independent `A\B`. Thus if
`k=p+|B|`, `s=|H_B|` and `b` is the prescribed number of attachments
to `B`, the internal-edge floor is `max(e3(k,s), e3(k,s+|B|)-b)`.
In the projection, overlapping support cells cannot have an edge.
Edges incident to a cell sum to its exterior degree total. MTF
requires each vertex of a cell not containing `i` to hit column `S_i`,
so the corresponding aggregate edge count is at least the cell size.

Take a nonempty set `I` of double vertices of `H_B` with pairwise
intersecting supports, so `I` is independent. Let `r_i` be the number
of vertices in `P_i` hit by `I` and `m` the number of edges from `I`
to these private cells. Then `m>=Σ r_i`, and `P_i` loses no vertices
if every support in `I` contains `i`. The private remainder can be
joined to `I` and `A\B`, so it has independence number at most
`p-1+|B|-|I|`. In addition, one may include all anchors in `B` not
in the union of the supports of `I`; their only added edges in this
remainder go to their own retained private vertices. Apply the two
edge tables as above. In each matching `P_i-P_j`, at least
`max(0,max(r_i,r_j)-1_{ij∉J})` of the edges touch a removed vertex.
These do not occur in the remainder, and different cell pairs count
disjoint edges. This proves the lower bound computed for private
edges after fixing `r`; minimize `private_edges + w*m` with integer
`0<=r_i<=p` and `w=0,1,2,3` to obtain linear projection rows.

For a triangle of `J` with `p=4`, its three double vertices are
independent and the private remainder after removing their contacts
has independence number at most three, hence order at most eight.
With exactly four contact edges the removal sizes must be `(2,1,1)`
in some order, and the remainder requires ten edges. At least five
matching edges touch the removed group, giving at least 19 edges
including the contacts. With five contact edges, at least seven
private vertices survive. If the private block had just 12 edges,
it would consist of the three perfect matchings. Its cycles have
length divisible by three (the part colors must repeat cyclically),
and length three is prohibited. On 12 vertices they are all even,
so the remaining seven would contain an independent four-set.
Thus five contacts require at least 13 private edges. Six or more
contacts already give 18 edges. In particular the triangle floor
is 18 rather than the uncolored order-15 floor 15.

## Extra rows from adjacent roots (hand)

Use the decomposition in `ralph/lanes/A/ADJACENT_DEG6.md`. In `H_u`,
the other root's five neighbors within the residue form an independent
strip `B`; its 36 edges go to `X=H_u-B`, and each vertex of `X` has
one or two neighbors in `B`. In the projected first-root support
groups the strip is exactly a full private cell plus the unique
double tied to the degree-six anchor. The marked cross endpoint has
two neighbors outside `H_u`; each other strip vertex has one.
The two uncovered pairs in `B` form either a matching or a 2-edge path.
With a matching the cross endpoint must be incident to one of the
two edges (otherwise degree at least ten in `G`). With a path the
cross endpoint is its middle or one of its leaves. These three
possibilities give the following degree multiset of `B` in `G`:

| Uncovered pairs / cross endpoint | Degrees in G |
|---|---|
| matching / incident | 8,8,8,9,9 |
| path / middle | 8,8,8,9,9 |
| path / leaf | 7,8,9,9,9 |

These follow from `d_H(b)=8-(# uncovered pairs incident to b)`.
The two strips in `G` are disjoint, hence in the `n8=2` pin both
must be path/leaf, and when `n8=4` at least one must be path/leaf.
All but the cross endpoint dominate `X` via their neighbors in `X`:
there is no possible common neighbor outside `X` for any missing
edge from such a strip vertex to `X`. These are necessary conditions,
not a claim that either side extends.

## Checked scopes

`local_signature_budget.py` encodes the three-anchor induced window
with **no root**, i.e. three independent anchors plus 12 private
vertices and `q` distinct doubles. It checks all independent seven-set
clauses (skipping only sets containing an already fixed edge), all
triangles and an upper cap on the exterior edges. Forest pins are
the only extra labels. Exact minima by `q=0,1,2,3` are **9,11,15,18**:
all four caps one below these numbers have dual-checked LRATs; all
four minima have a validated graph in `scratch/G/round6/localproof/`.
Each ordered three-anchor signature graph with `q` edges is isomorphic
to the one chosen by the encoder. C13 gave smaller SAT and UNSAT controls.

`signature_rows.py` checks the two matching formulas on C35, saturated
Exoo39 and both smaller controls; performs 13 exact C13 equality
substitutions and one nine-vertex `p=3` equality substitution. The LP
scan compares the matched base and strengthened contact/triple rows.
It is a relaxation, and no feasible outcome is a graph or a proof.
