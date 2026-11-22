# One shared fifth row, with all physical singleton restorations (hand)

Scope: a marked cap-five, 9-regular order-40 completion of two order
16/17 one-neutral frames rooted at `K4,4`. Let U and V be the two root
shores. W is the 16-window, with the four marks giving the neighbors
in W of the four U roots; W' is the 17-window marked by the four V
roots. The two windows meet only in the neutral z. Private sites of W
miss V, private sites of W' miss U, and z misses U and V. The frame
edges and all mark incidences are fixed, not just their margins.

## Geometry and the unknown row

Let x be in exactly three U marks of W and have three neighbors in W.
Let A be its three U roots, u the remaining U root, and B = V + x.
These are the shores of a `K3,5`. No exterior site sees both shores,
by triangle-freeness. Two distinct A vertices already share five
neighbors in B. Hence their four neighbors apiece outside B cannot
overlap, by the codegree cap of five. Every such neighbor belongs to
the 12 actual sites of `H = W − ({x} ∪ N_W(x))`: it cannot see V or x,
it is in an A mark, and that mark has no root or neutral.
The exterior sites missing B are precisely H: all W' private sites
see V and u sees all four V roots. Accordingly H is fixed even before
choosing a cross-edge. It is triangle-free and has alpha at most four
in any completion, since the five independent B poles can be adjoined
to any independent set of H.

The neighbors of x in a completion are its three A roots, the three
sites `N_W(x)`, and exactly three sites among the 16 private sites of
W'. Write T for this last three-set. When z belongs to `N_W(x)`, add z
when checking independence of T in W'. When z is in H, do not add it.
For b in V, x and b already share the three A neighbors; every member
of T in b's mark adds one more. Thus `|T ∩ mark(b)| <= 2`. These tests
are necessary, not sufficient for a whole completion.

## Restored cards and physical labels

For each b in B, let `S_b` consist of exterior sites whose B-support is
exactly `{b}`. The anti-neighborhood of the other four B poles is
exactly `H ∪ {b} ∪ S_b`: each A root sees all of B; other exterior
sites are classified by their support; and the B poles are independent.
Thus the induced card is triangle-free with independence number at
most five. The restored pole is adjacent to S_b and misses H, and
its singleton sites are independent. For b=x the set S_b is exactly
`N_W(x)`, so the restored card is literally W. For b in V, S_b is its
original singleton group in W' minus T. In particular u is never a
singleton (its support is V), and no W site lies in S_b for b in V.

For b in V, the only fixed H–S_b incidences are those involving z, if
z lies in H; they come directly from W'. If z lies outside H, none of
these incidences is fixed by the windows. The separately checked
degree-three/four catalogue cards have `12+1+k` vertices for
`k=|S_b|` and a root of degree k. Removing that root and its k neighbors
must give precisely H up to isomorphism. Every residual isomorphism
can be used in reverse and checked for contacts to z. More explicitly,
when z is present, use every possible image of z under the residual
isomorphisms; the number of its adjacent singleton vertices in the
card must agree with the known number at the physical z. This equality
is also sufficient for the local binding: pair the physical singleton
labels to the rooted card neighbors separately in the adjacent and
nonadjacent classes. They have no other fixed H–S_b edges, and both
singleton lists are independent. With z absent, any residual
isomorphism and any ordering of the singleton set works. This does
not rely on one arbitrary canonical labelling. A value k≥5 is
impossible by `R(3,6)=18`.

## Small cards without a catalogue

For k=0 or 1 the cardinality bound is automatic: an independent set
can use at most one of the new sites, and H has alpha at most four.
Use just the required edge to z, if any, to keep the card triangle-free.
For k=2, each singleton can have any independent neighbor row in H,
of its required z contact sign when specified. Since the two singletons
are nonadjacent, there is no triangle between the rows. An independent
six would have to use both singletons (and not the root) and four sites
of H missed by both rows. Therefore the union of the two rows must hit
every independent four of H. This is also sufficient for the local
card, so no order-15 catalogue is required. If z is specified, knowing
just the contact count is enough, by exchanging the two singleton
labels. These checks may leave additional constraints of the full
graph untested; omitting those constraints cannot reject a completion.

## Exact shortcut when z lies outside H

In that branch `z ∈ S_x`. For every original pole b, no H–S_b incidence
is prescribed by either window. For all k≤3 take the literally present
card W, retain H and x, and keep any k of the three neighbors of x.
After relabelling x to b and the retained sites to S_b, this is a local
card of precisely the required order and degree. Deletion cannot
introduce a triangle or enlarge independence number. Consequently
for these four poles, **every k≤3 always passes** in this branch;
there is no need to enumerate unknown small-card rows in production.
For k=4 all poles need the same unmarked question: does any order-17
degree-four rooted card delete to H? If so, the five-card test is
vacuous on every legal T of this left frame. If not, the test is exactly
that T meet every original singleton group of size four (here just one,
since the opposite window is a triple). This is a shortcut only for the
card filter, not a shortcut for the degree, triangle, or other global
checks. When z lies *in* H the contact signs can obstruct deletion and
this shortcut does not apply.

## Why there is one row, not five

A hypothetical completion supplies **one** T satisfying the row
tests. It supplies all five restored cards at the same T and their
incidences at the same physical z. Thus if no enumerated T survives
all five restorations simultaneously, the header has no completion.
The existential quantifier over T must be outside the conjunction of
the five predicates. A pass is not evidence that the unknown cross
edges, their degrees, or other antineighborhoods can be completed.
