# P4 one-side Ramsey rows: hand audit

Scope: necessity of the two projected independent-set row families in
`ralph/lanes/C/path_four_factor.py`, given the hand P4 block decomposition
and a valid labelled seed A. No P4 catalogue, CNF/proof binding or LRAT
was independently replayed for this audit.

For side 0, let `B=D0∪D1`, `D=D0`, `v=v0` and `r=v2`; for side 1
use `B=D2∪D3`, `D=D3`, `v=v3` and `r=v1`. All vertices of B see v, so
B is independent. The root r has no neighbors in A (A was defined by
deleting both middle closed neighborhoods) and none in D (the three
contiguous blocks in its own neighborhood omit the outer block D).
But r sees the other block of B. Thus the use of the extra vertex is
valid for D, not for all of B.

For an independent `I⊆A` omitting v, let `free(F,I)` be the members of
`F⊆B` having no neighbors in I. The two necessary inequalities in an
extension with independence number at most alpha are

    |free(B,I)| ≤ alpha - |I|
    |free(D,I)| ≤ alpha - |I| - 1.

The first independent set is `I∪free(B,I)`; the second is
`I∪free(D,I)∪{r}`. Omitting I with v only weakens the constraints, and
ensures the projection does not forget a genuinely blocking incidence.
Every remaining A vertex outside `X+Y` for side 0, or `X+Z` for side 1,
sees v and hence cannot have a B neighbor. Therefore the free counts
depend only on the indicated projection J of I. Taking the minimum
limit over identical J is valid. If `J'⊆J`, then `free(F,J')` contains
`free(F,J)`; deleting a row for J is valid when the same table already
imposes an equal or stronger bound at J'. The recursion in
`independent_sets` branches in vertex order and enumerates each
independent set once, including the empty set.

The one-way availability implication is sufficient: if no hit-literal
is true the clause `[available,*hits]` forces `available=true`; an actual
completion extends by setting the indicator to the exact no-hit value.
Consequently its at-most rows hold under a true graph extension even
though the reverse implication is not encoded. `external_block` takes
the first block on side 0 and the last on side 1, matching D0 and D3.

## Unknown side and pin split

The base one-side CNF is also a necessary relaxation. For degree it
counts known true and known false incidences separately; an omitted
incidence is neither. The cross-edge degree-sum constraint retains
every position, even in a one-side formula. Unknown triangle rows are
skipped, and for codegree only the observed conjunctions are bounded.
An MTF row is retained only for an observed edge literal with every
**possible** common-neighbor witness observed. The `unknown` flag is
set on either unobserved incidence for such a possible witness, so no
unknown witness is treated as absent. A fully observed cross pin may
conflict with a previously forced setting, but this only yields a
contradictory branch. There is no need to prune such pins in advance.

`bounds` enumerates the cross positions in row-major order on D0×D3.
Permutations internal to D0 and D3 fix A and both roots pointwise,
preserve all block incidences, and map every completion to one whose
cross matrix is the minimum of its independent row/column orbit.
`check_p4_pin_cover.py` tests these minima by adjacent-swap closure,
not by C's permutation loop. Results match the hand control (row,
column, matching for two edges in a 2×2 matrix) and all actual pin
keys: 126 weight-five matrices give seven representatives, and 84
weight-six matrices give six. This checks the pin key set, not which
proofs successfully cover those keys for each input.
