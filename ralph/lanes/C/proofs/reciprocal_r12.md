# One-sided projection of the tight reciprocal 22/20 profile

## Hypotheses and statement

Let G be a 9-regular triangle-free graph on 40 vertices with
α(G) ≤ 9 and maximum codegree at most five. Let A and B be disjoint
triples forming a K3,3. Write F_T for the induced graph on the
vertices outside T and with no neighbour in T. Assume |F_A| = 22
and every pair in B has codegree five (the *tight* B profile).
The conclusion submitted here is **e(F_A) ≤ 64**. It uses the
previous reciprocal exclusions, the published order-22 census,
and the 324 locally checked projection proofs; it is not an
exclusion of all 22/20 maps.

## Fixed sites and edge balance (hand)

1. The previous reciprocal count gives
   `|F_A| = 10 + sum_{a<a' in A} c(a,a') − |∩_{a in A} N(a)|`.
   Each c is at most five and the intersection contains B. Therefore
   equality at 22 requires three codegrees five and intersection
   exactly B. In particular the neighbourhood masks of A outside B
   have size six, all three pair intersections of size two, and no
   triple intersection.
2. C-033 and the prior 22/22 exclusion give |F_B| ≤ 20. Applying
   the same formula with B in place of A gives `|F_B| = 25 − h`,
   with `h = |∩_{b in B} N(b)| ≤ 5`. Thus |F_B| = 20, h = 5.
   The three B masks in F_A have size six and pair intersections
   exactly the same two vertices x and y. Write Q for their union
   and Z = V(F_A) \ Q. Then |Q| = 14 and |Z| = 8.
3. Write P for the other twelve vertices (outside F_A, A and B).
   Triangle-freeness prohibits any vertex seeing both A and B, so
   F_B is exactly the induced graph on Z ∪ P. Every site in P is
   adjacent to a nonempty subset of A. By step 1, exactly two sites
   have each nonempty proper subset as their mask: the two sites of
   a doubleton are its pair intersection, then two singleton sites
   are needed to give each root its six neighbours outside B. Edges
   in P can only join disjoint masks, giving at most 24 candidates
   (12 singleton–singleton and 12 singleton–doubleton).
4. Put H = F_A. The edges incident to A ∪ B comprise 9 between the
   triples, 18 from A to P, and 18 from B to H. The degree sum in H
   is `22·9 = 2e(H)+18+e(H,P)`. The degree sum in P is
   `12·9 = 2e(P)+18+e(H,P)`. Subtraction gives **e(P)=e(H)−45**.
   This identity does not rely on the tight profile; it holds for
   any order-22 window A with exactly three common neighbours B.
5. The five vertices in S = A ∪ {x,y} are all adjacent to every
   vertex in B, so S is independent. In H, neither x nor y has
   a neighbour in Q (every member of Q sees some vertex of B).
   Consequently all unknown neighbours of x and y lie in P, and
   their remaining degrees are `6−d_H(x)` and `6−d_H(y)`. Their
   chosen masks of P can share at most `2−|N_H(x)∩N_H(y)|` sites,
   and each chosen mask intersects each original A mask in at most
   two sites: the other three common neighbours lie in B already.
   Within each of the six A mask types, simultaneous relabelling of
   its two P sites preserves all originally fixed data. Sorting the
   joint x,y incidences within each type gives a representative of
   every possible assignment, without imposing any choice on later
   edges on P or from P to H.

## Catalogue and exact projection (hand + enum + cert)

Each independent set in H extends by A, so H is in the all-graph
(3,7;22) census. All 191 hosts have already been matched by validity
and nonisomorphism to the published counts (D-C7; round 10).
On these 191 hosts the tight-profile marking produces 1,307 marks;
the independent common-pair/petal search matches their exact keys.
Of those, H has at most 65 edges; 9 marks in rows 8, 10 and 28
(zero-based; 6, 2, 1 marks) have exactly 65. Steps 4 and 5 require
e(P)=20 for each. For each of the nine marks every qualifying x,y
assignment, modulo the six two-site swaps, gives one of 36 keys.
The independent ledger regenerates their exact set from H.

For each such key, the lower graph contains H, the previously fixed
root edges and the specified x,y incidences. The only undecided
edges have one endpoint in P and the other in P or H−{x,y}. An
undecided edge is impossible if its endpoints already have a lower
common neighbour (triangle), or if it creates a new common neighbour
for a pair already at codegree five. The upper graph adds every
undecided edge not forbidden this way, and includes every possible
completion. The projection uses only variable edges of that upper
graph with both endpoints in W = Z ∪ P. It requires:

- each z ∈ Z has its exact deficit filled, since all of z's edges
  outside W are already known;
- exactly 20 P–P edges, and every site of P fills its deficit using
  at most its available edges outside W (so only necessary bounds
  on its degree in W are asserted);
- no triangle within W;
- for every s ∈ S, N(s)∩W is a fixed independent six-set, since s
  already sees exactly the three vertices of B outside W. It must
  dominate W: a seventh vertex independent of those six would make
  an independent ten-set together with B. The domination clauses
  are therefore necessary, even if s itself is not in W.

The base CNF expresses the exact cardinalities and bounds with a
sequential counter over fresh variables. Any satisfying assignment
of a cardinality bound extends to the counter variables (choose the
prefix count), so introducing them does not eliminate a projection.
For these 324 instances the *only* added clauses forbid selected
positive edges giving a lower codegree over five. For each such
negative clause the ledger physically adds just those edges to the
fixed lower graph and independently observes a pair with at least
six common neighbours. If all listed edges were present the cap
would fail regardless of every unlisted edge, so each clause is
necessary. There are 2,285 such cap clauses across the 324 keys; no
lazy independence axiom enters this complete slice.

Thus any genuine completion with e(H)=65 projects to a model of one
of the bound CNFs, covering all physical keys. The ledger reconstructs
all 324 base clause lists, checks the added clauses and proof/CNF
SHA256s, and freshly checks every LRAT using both checker programs.
Each CNF is UNSAT, ruling out e(H)=65. The host census rules out any
e(H)>65 for this marking. This proves the claimed bound conditional
on the inherited full order-22 class count and reciprocal exclusions.

## Complete zero result for the earlier upper-graph test

The preliminary test for both extra roots uses only the fixed graph
of their shared assignment and an upper graph. It checks degree,
codegree and domination, then tests every triple of S and also B.
The induced subgraph avoiding a root triple must have no independent
seven-set; such a set survives to a completion if found in the upper
graph. The final unrestricted check asks for an upper-graph ten-set.
All 1,307 tight marks have at least one unrefuted assignment in this
test. The census found 54,582 assignment representatives; 36 fail
on the B-rooted window and 162 on global pair domination. No S-reroot
cut was observed at this strength. An unrefuted upper bound is not a
graph. The exact projection above is where the nine-mark cut occurs.
