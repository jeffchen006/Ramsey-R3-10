# Round 16: exact asymmetric cap-five header domain

**Hand + enum, pending critic.** This sizes the unresolved *labelled
header domain*, not an enumeration of completions. No additional case
is closed, and no solver or production panel scan was launched by A.

## Cover and map

Mark a `K4,4` in a 9-regular, triangle-free order-40 graph with alpha
at most 9 and codegree at most 5. Assume exactly one exterior site `z`
misses all eight roots. No exterior site can meet both shores, and
each nonneutral site meets one. The two exterior antineighbourhoods
of the shores cover 32 sites and intersect in `{z}`; each has alpha
at most 5 by adjoining the four roots it avoids. The published bound
`R(3,6)=18` puts both orders at most 17, so their orders sum to 33 and
are 16 and 17. Put the order-16 window first (regardless of the numerical
frame IDs); its private size is 15, and the other private size is 16.

Window `W` carries the marks of the shore it **meets**, one independent
exterior five-set per root. Transport the physical `W` to any catalogue
representative. Sort its four transported marks (renaming roots only)
and retain all sites in their catalogue order, except the neutral site
is represented just once when combining the two windows. More
explicitly, create four roots for each frame, then a copy of each
nonneutral list, and a single common neutral. Copy the two induced
windows into their own private-plus-neutral lists, add the complete
root biclique and the four marks on each side. These determine all
edges other than private-to-private crossings; in the two read
directions these rectangles are physical transposes, not new IDs.
Each input labelled frame has one uniquely recoverable neutral, the
complement of the mark union. There is no second neutral bit, no
same-size diagonal case, and no division by two. Multiple frame IDs
may cover the same unlabelled graph; that does not create a gap.

### Incidence shapes

The four marks spend 20 incidences. Their pair intersections are at
most one since the two corresponding roots already share four opposite
roots. An `r`-fold site spends `r−1` excess incidences and uses
`C(r,2)` of six distinct pair slots. A site in four marks occupies
all slots but cannot supply the required excess 5 or 4. Two triple
sites would repeat a pair slot. Thus the possibilities are exactly
the following combinatorial shapes (without asserting that any joins
complete):

| Private size | `(single,double,triple)` | Double-slot pattern | Singleton counts per root (descending) |
|---:|---|---|---|
| 15 | `(10,5,0)` | `K4` minus one edge | `3322` |
| 15 | `(11,3,1)` | three spokes from the mark outside the triple | `3332` |
| 16 | `(12,4,0)` | `K4` minus a matching | `3333` |
| 16 | `(12,4,0)` | `K4` minus two incident edges | `4332` |
| 16 | `(13,2,1)` | any two spokes from the mark outside the triple | `4333` |

The frame producer builds every independent five-mask and visits
increasing compatible quadruples with union size `order−1`. It rejects
only cap violations already within the host or among its sites after
adding incident roots, and known degree excess. A site and a root
have at most five known common neighbours since the root only meets
that five-mask among the window sites; the opposite roots contribute
none to this pair, because the site avoids them. For two window
sites already at cap in the host, even one common mark would violate
the cap. Otherwise their codegree remains at most five, since two
common marks would violate the pair intersection cap. The single-mask
filters therefore exactly implement this site-pair test, and the
final repeated-site pass checks the aggregate known degrees. All
four-set shapes above are counted, including `3322` and `4332`.

## Exact denominator

In an order-`q` window let `D_q` be the private degree sum using
window edges and `d_q` the degree of the neutral in the window. The
two contributions to the neutral degree are disjoint, so
`d_16+d_17=9`. The missing crossing-degree sum is
`9(q−1)−20−D_q`; equality of the two missing sums gives
`D_17=D_16+9`. These two equalities are necessary, not sufficient.
The count sums `n16(D,d)*n17(D+9,9−d)`; no cross product was generated.

| `(D16,d16)` | Left frames | Right frames | Ordered headers |
|---|---:|---:|---:|
| `(66,4)` | 319,883 | 19,700 | 6,301,695,100 |
| `(67,5)` | 529,043 | 5,497 | 2,908,149,371 |
| `(68,4)` | 205,527 | 21,254 | 4,368,270,858 |
| `(69,5)` | 266,965 | 3,082 | 822,786,130 |
| `(70,4)` | 64,932 | 9,474 | 615,165,768 |
| `(71,5)` | 68,986 | 514 | 35,458,804 |
| **Total** | **1,455,336** | **59,521** | **15,051,526,031** |

Full side inventories are 2,817,701 and 59,521 frames (raw product
167,712,381,221). By left shape: 2,809,958 / 7,743; by right shape:
16,056 / 43,206 / 259, in the order of the incidence table. All 34
positive key-by-shape products are in `scratch/A/r16/strata.tsv`.
The catalogue sources `gluing/val/r3_6_{16,17}.g6` match the older
local copies and McKay's public catalogue byte for byte (order 16
after decompression). The replay binds both hashes, decodes all records,
checks triangle-freeness and alpha at most 5, and rechecks the 2,576
and 7 distinct isomorphism classes with nauty `shortg`. Completeness
uses the published counts D-G3b/D-G3, not a new catalogue census.

## Controls, delivery and cost

- All 2,576 smaller catalogue records were screened for 5-regularity
  (11 hosts). They yield 153 physical `K2,2` one-neutral marks with
  window orders 6/7 (64 in cap-3 hosts and 89 in cap-4 hosts). Their
  labelled windows deduplicate literally to 98/101 inputs, producing
  285/460 frames. A separate Python set-based enumerator, not the C++
  mask pruning, obtains identical smaller frame rosters. Literal
  pairwise degree-deficit and neutral tests agree by exact ID with
  both bucket read directions, 34,504 headers per direction.
  Each plant's physical edges are reconstructed from the emitted marks,
  window copy and actual crossing in each direction. Deleting a real
  crossing gives exactly two degree violations each time (306 tests).
  A 7-window private shape substituted in the 6-table, a dropped
  frame and a false private degree are each diagnosed and rejected.
- `pilot.frames`: 544 rows of `host neutral mask0 mask1 mask2 mask3`
  for left16 followed by the same six fields for right17. `pilot.index.tsv`
  maps zero-based pilot rows to both full frame IDs plus exact shape
  stratum rank, and `pilot.bound.tsv` adds the individual `D,d`.
  Full IDs are zero-based in `(host, four numerically increasing masks)`
  order. There are 16 samples per stratum: its first, middle and last
  product ranks and 13 seeded ranks. A stream of the two one-sided
  inventories, not the product, bound and individually validated the
  sampled masks in Python and reproduced every C++ per-host bucket.
  No full frame table was retained. This is a deterministic stratified
  pricing sample, not a tail bound or a cover of all potential targets.
- Preflight on single-mask compatibility bounded quadruple loop
  candidates by 163,340,873 and 2,288,144. The 64-host sample containing
  the largest order-16 bound took 0.03 CPU-s; full bucket construction
  took 0.82 CPU-s, below 4.3 MiB RSS per process. The frame-stream
  sampling took 15.09 CPU-s with 37 MiB peak RSS per process (plus
  the small paired producer), well below the 512-MiB cap. Retained
  evidence including binary and smaller controls is under 0.5 MiB.
- Eight bytes per materialized header alone would cost 112.14 GiB,
  exceeding the shared scratch headroom at start of round. Even
  1 microsecond average per exact header would cost 4.18 core-hours
  before a second path or setup; 1 millisecond would cost 4,181
  core-hours. These are unit-cost sensitivities, **not** measured
  terminal times or lower bounds. A's count leaves all headers open;
  Lane C owns the bounded terminal pilot and tail pricing.

Replay: `bash ralph/lanes/A/replay_one_neutral.sh`. The clean work area
is `scratch/A/r16-replay/`; it does not mutate C's pilot input. Exact
inputs, decision code and deterministic outputs: `ROUND16_FREEZE.sha256`.
