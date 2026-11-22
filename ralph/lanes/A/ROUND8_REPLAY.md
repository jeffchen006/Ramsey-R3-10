# Round 8: paired-strip proof and source audit

The target of this round is enumeration and certificate evidence for two
**subcases**, not a degree-distribution exclusion. Both assume the accepted
degree-six residue hypotheses in G's `rows/path_leaf_windows.md`.

1. Both strips path/leaf, opposite centre codegree 1, and the common
   antineighbourhood `T` has minimum degree 2. This is at the two e168 pins
   `(2,8,2,28)` and `(2,7,4,27)`. Minimum degree 3 and up is not included.
2. At `(2,7,4,27)` only: one path/leaf and one matching/incident or
   path/middle strip, **a specified noncross d8 pivot** opposite the
   path/leaf centre has codegree 4. Lower mixed codegrees are not included.

## Source and cover

The order-25 minimum-degree-two root has a `(3,7;22)` antineighbourhood.
Its two neighbours are independent and have independent supports on the
order-22 graph. Selecting an unordered pair of supports suffices. For
each subset of the two new neighbours, a maximum independent set in
the stem outside their combined supports must have size at most seven
minus the subset size (and sets using the root are separately bounded by
the stem's alpha). This is exactly the check in `gluing/src/glue3.c`.
Degree bounds are `2..7`, so the edge cap 87 does not cut the source.
The input's 191 distinct valid classes bind to the accepted D-G3 count.
On the complete three `(3,4;8)` classes the gluer produces exactly the
unique C13 class after deduplication. Regeneration from the 191 order-22
cores produces a byte-identical stream of 18,333,381 graph6 rows, 15.25
CPU-s; see `scratch/A/strip8/lower.glue.log`.

G uses a rooted mark scan; A uses the previous maximal-independent-seven
traversal with no gluing-root pruning. The independent algorithm matched
all 20,181 marked rows as an exact sorted list after a 400,000-row pilot.
On every marked row A independently checks graph6 lineage, triangle-free,
alpha seven, minimum-root degree and the canonical 22-vertex stem. On the
augmented graph, two same-colour auxiliary vertices are each linked to the
four labels of one side. The ordinary graph vertices are in the anchor
and the exterior colours. Isomorphisms of the augmented graphs are
precisely the marked isomorphisms with optional side exchange. This
independent canonical coding verifies exactly 17,194 orbits and one
supplied representative per orbit. Source logs: `lower.scan.*.time`,
`lower.scan.A.sorted`, `lower.source.{log,time}` under `scratch/A/strip8`.

The mixed audit starts with A's independently scanned 1,988 order-27
keys (bound in Round 7) and tests **both** ordered side assignments.
For the second strip independently choose both missing pairs in the
complete five-anchor list. Exactly one contains the pivot; the other must
be absent from surviving double supports. Disjoint missing pairs require
the cross endpoint among their vertices; incident pairs require the
cross endpoint as their common vertex. This yields 3,688 matching and
1,491 middle roles. All 5,179 supplied records, including raw graph6
source ordering, match one-to-one (`scratch/A/strip8/mixed.source.log`).

## Formula binding and proof accounting

`audit_strip_extensions.py` independently reconstructs every fixed edge:
the T-induced subgraph; adjacent roots; pivot cut membership; missing
signature occurrences pinned on the opposite-exclusive lists; and
absent triangle-ineligible edges. Sorting the two exclusive lists is
legal because they are disjoint labelling freedoms. The G base encoder
enforces triangles, maximality, support occurrence counts and exact
degree classes (H's semantic audit: `ralph/lanes/H/ROUND8_REVIEW.md`).
For the both-path/leaf formula the cut row follows by counting the
incident edges of the roots, centres and deleted exterior vertices,
then restoring the root-root, two root-centre, 12 centre-to-X and
exclusive-cross edges that were counted twice. Mixed uses no cut row.

For each eager clause, independently enumerate the lexicographic I6 and
I7 sets in T and the same-exclusive cut subsets of size 3 or 2. The
opposite pivot completes a ten-set. The only edges not already fixed
absent are those between a retained member and a cut member. Discard a
clause if such an edge is fixed present, otherwise all unfixed edges are
necessary in the edge disjunction. The fast hash replay uses G's base
encoder with eager disabled, appends this independently reconstructed
clause tail, and verifies the byte-identical CNF SHA-256 for each receipt.
Ordinary replayer also compares the exact eager suffix from G's original
emitter. No SMS, symmetry clauses or lazy external clauses occur.

Primary receipt numbers: c1 pilot 42; original production 13,336;
13,378 total distinct. G's retry snapshot omits ten pilot receipts from
its initial closed list, so its 3,826 scheduled keys are 3,816 unattempted
primary keys plus **ten** repeated pilot keys. `pilot.resume.overlaps`
binds exactly those ten IDs. Each duplicate must have the same CNF
SHA-256; the primary proof remains selected for the unique coverage
index. Within-batch duplicates, undeclared overlap, missing/invalid
receipts, wrong shard positions, mismatched hashes and extra trace
files are not accepted as closure. Wrapper-capped work without a
receipt remains unattempted. Evidence and run commands are under
`scratch/A/strip8` and `run_strip_audit.sh`; `inputs.freeze.sha256` binds
code and initial data.

The retry has 3,826 positive receipts; after the ten declared repeats are
collapsed, `lower.terminal.tsv` binds 17,194 distinct certificates to
the 17,194 source keys and their actual trace paths. The mixed logs have
24 pilot plus 5,155 production receipts; `mixed.terminal.tsv` binds all
5,179, with no extra trace files. The producer's `CERT` receipt is
emitted only after checks by CakeLRAT and lrat-check. Additionally A
reran both checkers on 24 independent c1 samples and 295 of the mixed
prefix proofs (plus 12 c1 retry samples and dispersed mixed samples). A manually discontinued the
mixed prefix's dual replay in favour of checking all reconstructed CNF
hashes, not because a checker returned a failure. The LRAT proof and
CNF SHA-256 columns in A replays are joined by
`check_strip_replay_union.py` to the terminal receipt indexes.

**Terminal independent joins:** 17,194/17,194 c1 and 5,179/5,179 mixed
keys have exactly matching regenerated CNF digests and compressed proof
digests. The joins are in `scratch/A/strip8/lower.union.log` and
`scratch/A/strip8/mixed.union.log`; `round8.freeze.sha256` and its nested
`inputs.freeze.sha256` both pass. The complete LRAT checks for all keys
are from the producer; A's separate LRAT replays are sampled as above.
No distribution is closed and no order-40 candidate was produced.

## Higher-minimum-degree pilots

**Boundary arc rule (hand):** For each surviving `y` from X, list all
possible neighbours in the cut given full strip-role supports and
preserved edges. Each list entry avoids triangles at anchors, hits both
centres' removed neighbour sets, hits every unsatisfied retained-anchor
maximality obligation, and respects degree intervals. For two surviving
vertices `y,z` from X: adjacency in T requires disjoint choices; if
nonadjacent with no common neighbour in T, choices must intersect.
The latter follows from MTF, since neither root nor either deleted
centre has a surviving X neighbour. Removing a choice that has no
compatible choice for its peer cannot remove an actual completion.
The test tries both side roles and all support assignments independently
of order labels; this is a necessary test, not a sufficient completion.
All 52 C5/C13/C35 boundary projections pass; a missing-common-neighbour
and a forced-triangle mutation reject. All feasible tuples survive in
9,261 brute-checked three-domain controls. On 24 dispersed c1/δ2
marked keys all 24 survive, despite 3,796 values deleted: do not scale
unchanged. Evidence `scratch/A/strip8/arcs.pilot.{log,time}`.

**Clean order-27 projection (hand + enum):** In a window with the two
marked sides, deletion of any unmarked vertex preserves both marked sides
and their hereditary signature bounds and alpha cap; the union minus one
cross endpoint is still an independent seven-set. Conversely, when an
order-26 window admits a mark-preserving extension to an order-27
`(3,8)` graph, that marked extension must occur in the complete
order-27 cover, so the projection contains its marked class. A smaller
exact comparison (107 order-7 and 410 order-8 triangle-free graphs;
width 2, private cap 2, alpha cap 4) matches direct independent
neighbourhood addback: seven positive and four negative orbits. The 1,988
order-27 marks project to 29,113 distinct order-26 orbits with minimum
degrees 4/5/6 in counts 7,044/21,813/256 (12.02 CPU-s). They include
**none** of the separate 1,767 min-degree-three keys; the projection is
not a universal source reduction. This leaves nonextendible higher
minimum degree open. `scratch/A/strip8/project26.{log,time}`.
