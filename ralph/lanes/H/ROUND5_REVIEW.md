# Round 5 hypothesis review

## Degree-six equality

At fixed order 40, total e168, and root degree six, the externally
certified premise `e(H6)≥120` leaves at most 42 incidences between the
33 exterior vertices and the six root neighbors. MTF forces a nonempty
signature at each exterior vertex. Add one to each singleton's weight:
the resulting weights are all at least two, so their total is at least
66. Every set of vertices with a common anchor and signatures inside
the same block is independent with all root neighbors outside the block.
Applied to each singleton block and `alpha≤9`, each private cell has
size at most four. Their disjoint union is all singletons, at most 24
vertices. Both bounds are tight: there are 24 singletons, every private
cell has size four, and all nine remaining signatures are doubles.

Two vertices repeating an unordered pair `{i,j}` would join the four
private vertices of `i` and the four anchor vertices outside `{i,j}` in
an independent ten-set. The generic Lean uniqueness lemma needs a full
private cell at just one endpoint, not maximality or a degree floor;
the concrete equality theorem gets that premise from MTF and the external
residue floor. The final theorem takes the budget `e(G)≤e(H6)+48`, so it
also applies at e169 with an e121 residue. It does not assume the residue
itself is MTF. A degree-six root's signature graph has six vertices and nine
different edges. The Lean modules do not formalize its degree-pair cap,
the six allowable profiles, the census or Farkas/extension artifacts.

## Missing order-33 classes

A's BOARD audit (21:17 CET) states that verified thinning of all known
33/121 classes reaches exactly the 1,223 known 33/120 classes. If this
exact one-edge binding holds, a missing e120 class's triangle-free single
edge additions must all be among the missing e121 classes: adding an edge
cannot increase the independence number, and deletion commutes with graph
isomorphisms. Since that missing e120 class itself spends one of the six
unknown classes, it has at most **five nonisomorphic** e121 additions.
Deleting any of its edges cannot give a valid e119 class if A's complete
one-edge e119 descendants have all been bound. Neither implication gives
a lower bound on admissible e121 additions: the missing class can be
maximal triangle-free at order 33 even though it need not be, and the
number of literal additions is not the number of nonisomorphic outputs.
The 11 e169-pinned rows are valid at e169 only, and cannot be treated as
unpinned or as an input to an e170+ floor. No closure inferred here.

### Targeted minimum-degree-five branch

Three degree-six vertices cannot be mutually adjacent. A nonadjacent
pair has a common neighbor by MTF and at most one by the pair bound
from R(3,8)≤28. The other endpoint thus has degree five in the root
residue. Every vertex of an order-33 triangle-free residue with alpha≤8
has degree at least five by the same Ramsey bound. `Z≥48` makes the
residue edge count at most 121 when the total is at most e169. Thus a
complete exclusion of the minimum-degree-five branch, not only the
construction of a catalogue, would remove 18 open e168 and 21 open
e169 keys with n6≥3 on the frozen round-4 CSV. The 18 at e168 lie within
the 39 prospective e168 cuts, so cannot be counted twice. G's live sweep
is not proof of either exclusion or census completion.

G's maximal-column prefilter is a relaxation: independently enlarge each
root-neighbor attachment to a maximal independent set of the fixed 27-vertex
base. Only edges are added; each column stays independent and alpha cannot
increase. No edge cap can be tested after these enlargements. Every
independent seven-set of the base is maximal, so the pairwise pruning by
common avoidance of those sets is necessary. Higher subsets of columns
use the same independent-set test on the complement of their union. A
prefilter survivor need not have an edge-capped extension.

## Complete arms in a codegree-six path

`C/proofs/path_three.md` gives the neighborhood decomposition for the
three distinct roots and excludes diagonal codegree six. An X-vertex
is outside all three independent neighborhoods. If its only possible
neighbors in the triple intersection T are absent, a left-wing neighbor
forbids the right-side and middle-only blocks. The last root's full-size
independent neighborhood then forces a right-wing neighbor, forbidding
the other side. The middle root's full-size independent neighborhood
would be missed, impossible. Reversal is symmetric. Lean takes the exact
three neighborhood identities and the maximum sizes as hypotheses; it
does not substitute MTF for the max-independent-set argument.

For diagonal 4/5, the nonempty middle-only block puts a common neighbor
on every opposite-wing pair, so the independent triple block plus both
wings has at least ten vertices. At diagonal 3 the three T vertices have
three fixed neighbors each and all remaining neighbors in X (every other
boundary vertex shares a root with each T vertex). Hence at most 18 of the
22 exterior vertices hit T. The accepted `e(X)≤64` at diagonal 3 and both
arms full imply at most one wing-cross edge. Discard an endpoint if needed:
T and five wing vertices give an independent eight-set. The lower bound
four on the number of T-avoiders gives a nonadjacent pair by triangle-freeness.
The degree/window/edge numbers and previously accepted certificate are
external to Lean. `f*` is the **minimum** across codegree-six pairs; thus
forcing no P3 when `f*=9` yields a matching and does not exclude isolated
codegree-six pairs or any entire R(6) family. No 119-key solver repeat.

## Conditional e162 adjacent-degree-seven branch

For B's `(0,2,32,6)` profile, a degree-seven root has seven neighbors
of degree 8 by default, with a correction −1 for a neighbor of degree
7 and +1 for each degree-9 neighbor. G-011 gives `Z≤55`, forcing the
other degree-seven vertex to neighbor the root, no degree-nine neighbor
and exactly `Z=55`. The seven independent attachment rows therefore
have sizes 6 or 7, and MTF makes every row dominating and forces each
uncovered exterior pair to lie together in one row. H-006 certifies
the latter general facts in Lean, not this profile or its finite census.

The `row_support.c` branching proof is sound: the first still-eligible
member of the chosen undominated vertex's closed neighborhood in any
candidate dominating row gives a branch. Earlier choices may be banned
in later branches, and selecting the member bans its closed neighborhood
from all future picks. At a dominated leaf no independent superset can
increase the row size, so returning false for a size outside {6,7} is
valid. The catalogue count premise is the exact 234,681 in GR Table 14,
not swap reachability. B owns the catalogue replay; H did not duplicate
it. The profile is MTF/conditional on G-011, without either gluing floor;
if accepted, the frozen baseline would fall by one and U88 by one. It is
not a complete U88 or degree-seven-floor-108 result.

## Complete-wing pair support budget

Each exterior vertex hits at least one of the full independent sets
`C+Y` and `C+Z`, and indeed both; without a common support it would
have to hit both wings, forming a triangle across the complete wing
block. Vertices private to one common anchor are independent. Two such
vertices avoiding the same wing contradict alpha≤9 when combined with
that wing and the five other common anchors. Thus there are at most
12 private vertices across the six anchors, and each common anchor
sends seven edges into the exterior, for total support 42. The pointwise
positive-support identity gives `E=n1−10`, hence `E≤2`.

Under full wings for every codegree-six pair, a marked wing-sibling pair
would have a common boundary containing the old opposite wing and one
old root. The third sibling and other old root lie outside that new
boundary, with at least four and three supports there, respectively:
they spend at least three excess units, contrary to `E≤2`. Distinct
hypotheses are needed for this second application; the first budget alone
does not exclude a sibling of codegree six with incomplete wings.
