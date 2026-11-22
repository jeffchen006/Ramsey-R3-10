# Fixed-label degree-budget projection for a cap-five marked 16/17 frame

Use the hypothesis and notation of `panel20_factored_card.md`. Thus the
target is triangle-free, 9-regular, has independence number at most 9,
and has nonedge codegree at most 5. The two given induced windows `W`,
`W'` of orders 16,17 overlap at the neutral `z`. The eight roots of
the marked `K4,4` are disjoint from both windows, and their contacts
with both windows are fully determined by the marks. Select a vertex
`x` in three left marks with degree three in `W`, and put
`H=W−({x}∪N_W(x))`. The contacts of the three left roots seeing `x`,
after deleting the right roots and `x`, are three disjoint fours
covering `H`; hence `z∈N_W(x)` and `|H|=12`. See the cited proof for
the containment and disjointness arguments.

## Exact completion obligation

Fix the windows, their rooted marks, their given pin values, and the
identification of `z`; there is no relabelling after these choices.
The only unspecified pairs are between `W−{z}` and `W'−{z}`.
The exact obligation is to choose a subset of those pairs such that
the resulting graph has degree 9 at every vertex, is triangle-free,
has no independent ten, and has every nonedge codegree at most 5.
The four listed tests on the assembled graph are sufficient by the
definition of this marked case and necessary by hypothesis.

Every such solution supplies exactly one physical row
`T=N(x)∩(W'−{z})`. It has size three by the fixed degree of `x`;
`T∪{z}` is independent by triangle-freeness; `|T∩M_b|≤2` for each
right root `b`, since `x,b` already share three left roots. Enumerate
all such triples on `W'−{z}`, fix x's incidences into that set, and
test them separately. This is a cover, not an assertion that any row
has a solution.

## Sound pruning and the five cards

After fixing `T`, let `P` be the graph of prescribed present pairs
and `A` the graph of allowed pairs, with `P⊆A`. Maintain the inclusion
`P⊆G⊆A` for any solution `G`. A triangle in `P`, degree greater
than 9 in `P`, or degree less than 9 in `A` makes inclusion impossible.
If degree in `P` equals 9 at a vertex, all optional incidences at
that vertex are absent; if degree in `A` equals 9, all are present.
Any optional edge with a common neighbor in `P` must be absent.
Repeating these rules only makes necessary changes.

The independent poles are `B=V∪{x}`, where `V` is the original right
root quartet. The singleton group `S_x=N_W(x)` is entirely prescribed.
For `b∈V`, let `Q_b` be the sites in its right mark and none of the
other right marks, and put `S_b=Q_b−T`. The five groups are disjoint.
The induced graph on `H∪{b}∪S_b` is anticomplete to the four poles
in `B−{b}`: `H` has no contacts to any pole, a singleton has contacts
to just its root, and the poles form an independent set. Therefore
the card is triangle-free with independence at most 5, since any
independent six in it would combine with the other poles to make ten.
All edges in the card except between `H` and `S_b` are fixed: `H`
is induced, the singleton set is independent, and its root sees
every singleton and no core vertex. For the pole `x` the whole card
is fixed; its contribution to the added incidences is zero.

At a singleton site `s`, write `r(s)=9−d_P(s)` and let `o(s)` be the
number of its optional allowed neighbors **outside** `H`. In any
solution, the number of *added* edges at `s` into `H` belongs to
`[max(0,r(s)−o(s)), r(s)]`. At a core site `h` a single card can
contribute at most `r(h)=9−d_P(h)` added edges. These degree bounds
and all present/absent pins are imposed on each separate labelled
card. They include the outside forced incidences but do not require
that remaining optional outside incidences can be chosen consistently.

## Exhaustive local test and coordinate minima

For each singleton, enumerate every subset of its optional allowed
neighbors in `H`, keeping the fixed core contacts. Require the
resulting core neighbor set to be independent in `H`, exactly ruling
out a triangle involving that singleton. No triangle can use two
singleton sites, nor the root (its only neighbors are independent).
For every subset `U⊆S_b`, independent sets omitting the root and
meeting `S_b` in precisely `U` can have maximum size
`|U|+α(H−⋃_{s∈U}N_H(s))`. Independent sets through the root have
maximum size `1+α(H)`. These formulas prove the exact local cap
test. In a partial tuple of columns, checking subsets of columns
already chosen cannot exclude a later valid tuple, since future
columns do not change the displayed formula for those subsets.
Likewise, exceeding `r(h)` in one partial tuple can only get worse.
Thus enumeration checks **all** physically labelled restorations
allowed by the local projected constraints. No orientation or
permutation of equal size classes can be silently discarded.

For a nonempty card domain, compute `m_b(h)` by trying tighter
upper bounds on that one coordinate from zero up to the count in
a known admissible tuple. The same exhaustive local test under the
tighter bound is an exact existence decision. A found tuple can
also lower the known witness count at another coordinate; this is
safe because it is still a valid tuple without the tight bound.
Finally apply C-050: every extension must have
`sum_{b∈B} m_b(h) ≤ r(h)` at every `h`. Each independently counted
edge has a distinct singleton endpoint across groups, and no such
edge was included in `d_P(h)`. A failure suffices to cut a fixed
row `T`; passing does not establish a common choice of tuples,
let alone a completion of the entire board.
