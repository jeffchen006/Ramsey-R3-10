# Reciprocal window consequence, cap five

Let G be 9-regular, triangle-free on 40 vertices, with independence
number at most nine and maximum nonedge codegree at most five. Let A
and B be disjoint three-sets with every A--B edge present. Each is
independent by triangle-freeness. Define the window F_S to be the
induced graph on the complement of S and the union of its open
neighbourhoods. In particular, no member of F_A sees any member of A.

For S equal to A or B, write `p_S` for the sum of the three pair
codegrees and `h_S` for the common neighbours of the entire triple.
The full root bipartite graph gives `h_S >= 3`; the cap gives
`p_S <= 15`. Inclusion–exclusion, using the disjointness of S from
its neighbourhood union, gives `|F_S| = 40-3-27+p_S-h_S`.
In particular, `|F_S| <= 22`. Equality holds exactly when all three
pair codegrees are five and the common neighbourhood has size three.
For order 21, `p_S-h_S=11`, so either `p_S=14,h_S=3` or
`p_S=15,h_S=4`. Those cases give pair codegree multisets `(4,5,5)`
and `(5,5,5)`, respectively, and both implications are reversible.

Every independent set in F_A can be extended by A, so its size is at
most six. The same applies to F_B. Thus when the two orders are 22
and 21, their unmarked graphs occur in the complete respective
(3,7) catalogues. The mark/overlap and completion reduction, with all
needed conditions proved, is in `reciprocal_windows.md`. In this split
the overlap has size nine: the vertices consist of the union of the
two windows together with the six roots. Every nonroot vertex belongs
to at least one window because a neighbour in each of A and B would
give a triangle. Thus `|F_A ∩ F_B|=22+21-34=9`. The only unknown
edges pass between the two private sides of sizes 13 and 12.

**Conditional consequence.** Use the cap-five 22/22 exclusion and the
cap-five 22/21 exclusion, both for complete rooted alignments. If
the three pair codegrees of A are five and A has exactly three
common neighbours B, then `|F_B| <= 20`. Equivalently the union of
the three B-masks in F_A has size at least 14, since N(B) is exactly
A plus that union. If also the three pair codegrees of B are five,
then `|F_B|=25-h_B<=20` gives `h_B>=5`; inclusion of the triple
intersection in any pair intersection gives `h_B<=5`. Thus in that
subcase B has exactly five common neighbours and `|F_B|=20`. This
does not exclude the 22/20 profile or guarantee such an A exists.

## Row-selector proof pilot: necessity of every CNF constraint

For a bound marked map let L be the union of its two window graphs
and fixed root edges, and let X and Y be the private sides. All other
vertices are fixed. The edge variables are the pairs in X×Y. If a
pair has a common neighbour already in L, its variable must be
false by triangle-freeness. For a private vertex x, consider patterns
of size `9-d_L(x)` in its allowed private opposite side. In a true
completion its incident new edges form one such pattern P. No two
members of P may have an edge in L (that would form a triangle
through x). For every fixed vertex f to which x is neither adjacent
nor has a common neighbour in L, P must hit N_L(f). Otherwise x
and f would still be nonadjacent with no common neighbour, and
`N_G(f) ∪ {x}` would be independent of size ten. Also
`|(N_L(x)∪P)∩N_L(f)|` is at most five: if x and f are adjacent it
is zero by triangle-freeness, and otherwise this is their final
codegree, with N_L(f)=N_G(f). These are all the tests used to
enumerate row patterns. The calibration substitutes degree and cap
six, so its identical argument uses independent seven.

Assign the selector of x's actual P true and all other selectors
in that row false. This satisfies the existence clause and every
selector-to-edge implication. An edge Boolean also implies the
disjunction of row selectors that agree with its value; the actual
selector witnesses this. Each added clause is obtained from an
independent ten in a provisional model, and consists of **all**
private-opposite pairs inside that set, including disabled pairs.
No fixed edge lies in that set (it was independent in a supergraph
of L), so any true completion must satisfy the disjunction. Therefore
every true cap-five completion extends to a model of the generated
CNF. UNSAT suffices, even though the formula need not constrain all
private/private codegrees or enumerate every possible independence
clause. For proof-grade validation of the 32 stream-live maps use
also the original dense CNF without any selector or codegree cap.
