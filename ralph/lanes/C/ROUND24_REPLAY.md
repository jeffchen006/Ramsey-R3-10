# Round 24 — physically pinned degree-seven trace gate

## Claims and scope

- **C-058 (`hand`, pending).** Under the saturated e8/P0 all-missing
  premise, an omission with all degree-seven sites in `W` gives a
  fully pinned induced high graph. Compare it to each candidate
  choice of at most two exterior high sites in the largest omission.
  Over any induced isomorphism of those high sets, exact subtraction
  of the adjacency-mask histogram to the known high `W` roots gives
  the required trace of the same six omitted support columns. Every
  comparison must be met by that same column multiset. If no retained
  card is an all-W anchor, do not veto. This includes the stated
  b15 anchor cases as a necessary test, not a profile exclusion.
  Full proof: `proofs/crown24_high_trace.md`.
- **C-059 (`enum`, pending).** Exact independent scoped pilot of
  E's existing seven 32-row C8/b16 pilot lists. On these 224 rows,
  both implementations agree on every stage count and the exact
  accepted exterior-high tuple/omitted-support lists. The all-anchor
  gate rejects 220 of 224 and independently replayed 14 pairs with
  14 support assignments on four IDs. All 224 already have E's own
  checked baseline receipts; no additional branch debit.

## C-056 sparse roles and matched denominator

For `H_D` (omitting b16), with retained roles `i,j,k`, the floor
for the **observed** `e_ij` is `30−b_i−b_j` (8 or 10); equality
requires a perfect matching in the **omitted** `D×A_k`. If `k`
contains a proposed exterior high of `H_D`, that high has no edge
to `D` and the floor increases by one. The seven-edge exclusions
apply in `D×A_k`, not in `A_i×A_j`, when the observed count is one
above the original floor. Testing this necessary upper-capacity
condition directly against pinned disjoint-support pairs cut zero
of 15,629 pair choices (zero of 224 rows). All 224 baseline rows
were `CHECKED` with zero lazy witnesses; no actual `H_D` card reached
the equality matching, seven-edge shape or joint matching terminal.
Thus no measured saving from the sparse completion test itself.

## Same-row comparison

| Necessary condition | b10 comparisons only | All pinned high anchors |
|---|---:|---:|
| Rows from E's matched pilot | 224 | 224 |
| Sparse pinned rectangle upper capacity | 224 | 224 |
| Isomorphic degree-seven induced graph | 137 | 137 |
| Nonnegative and locally valid physical trace difference in all anchors | 21 | 11 |
| Same legal six-column support and weak exterior capacity | 16 | 4 |
| Kept pair/support assignments | 178 | 14 |

The four all-anchor survivors are E C8-plan IDs `18822`, `82478`,
`90898`, `207646`; their pair counts are `6,3,2,3`. They survive only
the structural gate. E's actual baseline independently refuted
all four and all 220 structural vetoes. The extra all-anchor cut
compares a retained b11 role with one triple plus one double, or
a b12 role with two triples, when it has six singleton rows.

The 220 vetoed IDs used 33.41582 of the 34.01389 total baseline
CPU-s (generation, solving, initial dual checking and archive). The
four remaining used 0.59807 CPU-s. Clean replay measured 3.44606
CPU-s for the full primary gate inside the loop; hypothetically
using it before the unchanged baseline would save **29.96976 CPU-s**
on exactly these IDs. A separate independent structural replay took
2.30 CPU-s (including import) on these same IDs; charge that too if
required in production. The vetoed baseline receipts account for
1,748,501 of 1,786,133 compressed LRAT bytes. These are matched
benchmark numbers, not realized production savings; no pilot debit,
no altered E queue, and no extrapolation to the untested C8 arm or
to other incidence profiles. E owns the full roster and its solves.

## Controls and replay

The smaller exact `C13(1,5)` control checks triangle-freedom and
`α≤4` literally, finds 20 translated induced deck alignments and
rejects 20 changed adjacency traces with the same high graph. Five
full local omitted-support sets on C8/2C4 are compared with an
unpruned product oracle, including 8,120 restriction histograms.
Ten synthetic incidence controls on C8/2C4 (not Ramsey positives or
E target rows) exercise zero, one and two exterior highs and the
explicit no-anchor outcome. On the target pilot, the alternate
oracle iterates the target six-vertex permutation first, classifies
the two exterior contact words over the ordered source roots, and
compares literal sets/strings and unpruned local supports; it does
not use the optimized direction's canonical high-graph code.

```sh
sha256sum -c ralph/lanes/C/ROUND24_FREEZE.sha256
mkdir scratch/C/r24-review
nice -n 5 timeout 150s prlimit --cpu=100:101 -- \
  bash ralph/lanes/C/replay_crown24.sh scratch/C/r24-review
```

Clean replay uses 16.15 CPU-s, 51,688 KiB peak RSS. Across both
development and clean checks, about 35.2 CPU-s / 0.0098 core-h was
charged. No detached C jobs; no solver, roster sweep, or write into
another lane's space. Case R remains open. No candidate.
