# Round 17: exact weights for the one-neutral package filter

**Hand + enum (pending critic).** Lane A bound the multiplicities and the
bidirectional counting rule for the marked cap-five 16/17 roster. The count
**15,051,526,031** is the denominator *before* the package filter. Lane A ran
no target production filter or terminal scan, and closes no new case.

## Key contract and exactness

A physical side frame is a catalogue row, its marked neutral vertex, and its
increasing root mark masks. Write \(D\) for the sum of its private vertices'
degrees **in the window**, \(d\) for the degree of the neutral in that window,
and \(\Delta\) for the ambient regular degree. The stratum `(D,d)` in order
\(n\) joins only to `(D + Δ(m−n), Δ−d)` in order \(m\): opposite private
degree deficits must agree, and the two windows partition the neutral's
neighbors. The stratum does not determine adjacency.

The destination `h=(host,neutral)` names the entire labelled window graph
and the location of its neutral. Catalogue order and bytes are pinned by
the round freeze; `host` is the zero-based line index, not a graph invariant.
For every singleton site \(x\) in a source root class let \(\epsilon\) indicate
its source edge to the neutral. Its encoded type is
`t = 2*(Δ−1−deg_W(x)+ε)+ε`. The demanded row is an independent set in the
destination graph of size `t//2`, and contains the destination neutral iff
`t%2` is one. Using the unchanged `panel16.cpp` predicate, a tuple of such
rows is a package iff for every nonempty subset \(S\) of the group the
destination subgraph outside their row union has independence number at
most `alpha_limit − roots + 1 − |S|`. In particular the neutral is not
deleted from the host in the query, and sizes 2, 3 and 4 are all present.

Permuting positions inside a group, with their types, sets up a bijection
between admissible tuples: it preserves row tests and sends every subset
test to the corresponding permuted test. No source labels or adjacency
inside the group are queried; each singleton group is already independent.
Group existence can thus use the sorted multiset of types. Whole-direction
existence is the conjunction over the groups, so a sorted multiset `P` of
these group tuples suffices. Do not flatten across groups or coalesce a
neutral just because another vertex has the same degree. Duplicate group
tuples are retained in the serialisation for audit.

The TSV schema is `order D d host neutral profile count`. Use decimal
integer types, commas within a tuple and semicolons between tuples. Sort
types numerically, then sort the group tuples lexicographically as integer
tuples. For target weights the file is emitted in host order, then in key
order within each host. The weight is the number of distinct original
physical frame keys in that cell; the profile is not a new header ID.

At a compatible destination pair `(h,k)` with fixed stratum, let `W(h,P)`
and `V(k,Q)` be side weights and `F(P,k)` be direction existence. Write
`a=sum_P W(h,P)*F(P,k)` and `b=sum_Q V(k,Q)*F(Q,h)`, with unfiltered
totals `A` and `B`. The four labelled category weights (both, forward
only, reverse only, neither) are exactly `ab`, `a(B−b)`, `(A−a)b`,
`(A−a)(B−b)`. This holds because at fixed destinations the two conditions
depend on separate frame choices. Sum these weighted categories over
compatible destination pairs. Union rejection is `AB−ab`, not the sum of
direction rejections. Reverse reader uses the inverse stratum map and
swaps the two one-direction-only masses; there is no exchange factor.
This factorisation is for **existence of each individual package only**.
It says nothing about crossing compatibility or terminal equivalence;
retain all physical singleton labels and the orientation for that work.

## Literal and adverse controls

The unkeyed C++ adapter uses the archived C domain routine at the literal
source sites (first witness only); no second package solver was added.
The Python audit rebuilds the 285/460 distinct control frame rosters by
literal set enumeration, calculates demands and weights separately, and
compares the four weighted categories to all 34,504 literal ordered IDs
in both read orders. Lane C also provided an independent query receipt
table, exactly matching all 2,067 small query identities and answers.

| Read order | Both pass | Forward only | Reverse only | Neither |
|---|---:|---:|---:|---:|
| 6/7 | 31,495 | 3,009 | 0 | 0 |
| 7/6 | 31,495 | 0 | 3,009 | 0 |
| Named 16/17 pilot only | 47 | 140 | 96 | 261 |

All 153 physical control marks pass in both directions, mapping to 142
distinct header IDs in A's deduplicated catalogue. For an adverse example,
keep order-7 source frame 326 fixed (profile `2,4,7;4,4,5`). Order-6
destination frames 251 and 256 have the same `(D,d)=(9,3)` and neutral
position 0, but host rows 85 (`EsHG`) and 88 (`Eii?`) give group-existence
bits `01` and `11`, respectively. A cache by margins would be wrong. As
a positive permutation check, target `(order,host,neutral)=(6,0,0)` gives
the same true answer on all observed permutations `(4,4,7)`, `(4,7,4)`
and `(7,4,4)` of one demand tuple, as the bijection predicts.

The target adapter evaluated only the 544 previously bound pilot IDs and
matched every archived group-presence bit before reducing to the four
categories above. Every pilot side profile occurs in the full weight
files at the recorded destination and margins. This labels the 47 as
passing only the package-existence filter; it is not a new terminal check.

## Full weight checksum and replay

The prior frame enumerator streams each frame once. A's separate parser
recomputes neutral and private degrees from the catalogue, checks the union
and strictly increasing frame ID, calculates singleton types, and writes
one pass of host-local weights. Their projections agree with every old
nonempty `(host,D,d,shape,triples)` count and with the full **34** positive
shape-stratum products. They give 2,817,701 / 59,521 frames, 2,223,225 /
28,834 weight cells and heaviest cells of 84 / 66. The 6 complementary
strata give 582,982 compatible destination pairs, 6,118 forward and
1,001,962 reverse possible distinct group queries. A straightforward
subtotal implementation visits 166,899,580 weighted buckets counting
both directions, before short circuiting. These are operation counts,
not a runtime or terminal-tail estimate. See `scratch/A/r17-stream/mass.log`.

Use `bash ralph/lanes/A/replay_direction_profiles.sh all r17-replay`
from the workspace root; the freeze binds inputs, weights and logs.
Full roster weights: `scratch/A/r17-stream/weights16.tsv` and
`scratch/A/r17-stream/weights17.tsv`. Use these, not the failed early
whole-side Python aggregation, which hit the process memory cap and did
not write a usable target file. The successful host-local writer uses
about 61 MiB RSS, and the checksum pass about 77 MiB. No large file was
put under `ralph/` and no detached job was started.
