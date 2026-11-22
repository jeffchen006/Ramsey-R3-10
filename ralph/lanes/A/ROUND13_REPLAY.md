# Round 13: independent audit of the 17/17 reciprocal panel

Scope: cap-five 9-regular targets with a marked `K4,4` and two neutral
vertices, so both antineighbourhood windows have order 17. The exhaustive
slice audited here has a triple site on the **left** frame. This audit is
`hand + enum`, not LRAT, and says nothing about a target without the marking,
the no-triple 17/17 complement, other window orders, or cap six.

## Semantic binding

- If `a` is an A root with exactly three singleton neighbours `S` in
  `F_B`, the antineighbourhood of `A−{a}` is exactly `F_A ∪ {a} ∪ S`.
  Restoring `a` introduces neither the other anchors nor any site seeing
  another A root. Inside the lifted graph `a` has neighbourhood `S`;
  deleting its closed neighbourhood recovers the original labelled `F_A`.
  The three still-deleted A roots, independent of the lift and of each
  other, give the lifted graph `α≤6`. The reverse lift is symmetric.
- The independent atlas generator enumerates physical independent masks.
  It computes subset α by a subset-max transform seeded with all
  independent masks, and checks all singleton/pair/triple spoke subsets.
  Entries are multisets. The labelled domain index expands distinct
  permutations into the three physical row positions; the keys store
  ordered `(size, hit first shared site, hit second shared site)` tuples.
  No permutation of the two shared sites is implicit in that index.
- For a singleton, the target row has size `8 − |known neighbours outside Z|`
  and has the prescribed two `Z` entries. For local codegree the checker
  adds the target contribution to the source-private contribution to
  count shared neighbours just once. Opposite anchors, shared sites and
  same-group singleton pairs are checked separately.
- For each pair of three-singleton groups, project the ordered packs onto
  an explicit `bool[3][3]` matrix (implemented as nested arrays). Transpose
  the reverse projection and intersect the two sets of matrices. Filter
  both domains to those matrices, repeating to a fixed point. A true
  completion supplies a package on every group and cannot be deleted. A
  nonempty fixed point need not provide a simultaneous choice of packages.

## Replay and receipts

From the project root run `bash ralph/lanes/A/replay_reciprocal_panel.sh`.
The script runs in `scratch/A/panel13`, checks controls first, then separately
rebuilds the target atlas and inventories physical frames. The producer
source is instrumented in A scratch only to emit per-ID stage receipts;
neither its packed representation nor its row atlas code is used in the
independent calculation. Zero-based IDs are literal line offsets in
`scratch/ideas/r012_R/frames17-5-2.txt`. Every supplied frame matched exactly
one independently regenerated `(host, sorted marks)` key; none missing.

Small atlas: 366 literal degree-two entries on the three order-8 hosts,
byte-equal to the small reference; 3,194 small frames. A planted nonempty
triple of repeated masks survives atlas generation and ordered indexing.
All ten regular order-22 hosts yielded 2,118 oriented `K2,2` occurrences,
8,472 label-preserving individual root lifts (four per occurrence), and
3,448 planted 3×3 panels. All positive panels passed and all 31,032
single-entry mutations failed the same matrix-intersection primitive.
The independent target atlas equals both scout files byte for byte:
1,499 / 1,574 / 2,214 / 1,290 / 2,887 / 223 / 272 entries, total 9,959.

| Shared-site identification | Raw | Header | Forward | Both | Local | Panel |
|---|---:|---:|---:|---:|---:|---:|
| Increasing to increasing (`0`) | 11,011,000 | 61,668 | 2,060 | 532 | 532 | 0 |
| Increasing to decreasing (`1`) | 11,011,000 | 437,000 | 75,438 | 17,072 | 17,072 | 0 |
| Total | 22,022,000 | 498,668 | 77,498 | 17,604 | 17,604 | 0 |

Each of the 498,668 IDs has the same last reached stage in the two
implementations (`slice.depths` and `ref.depths`, digest
`1546569065542a5ca16b28f597b6b8f2c8950be81ab1fb1485902f80e65e4624`;
empty `id-disagreements.diff`). The independent calculation also retains
all 100 of the scout's recorded held panel survivors (34 map `0`, 66 map
`1`); this is a positive panel probe, not a replay of the terminal check.
Final measured one-core CPU: 1.40 s independent slice, 1.80 s producer
identity replay, 0.54 s held probe, 0.03 s controls, 9.42 s including both
compiles. No long or detached jobs and no general scan by A.

Handoff: C owns any disjoint 1% pilot and subsequent production, subject
to the critic's count/timing/tail gates. The old mixed e168 reroot and
B-matching requests are retired: the critic's degree-six floor removed
their parent distributions, irrespective of the scoped strip exclusions.
