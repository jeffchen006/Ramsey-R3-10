# Round 18: two small physical header slices

**Enum (pending critic): physical coverage and marginal existence only.**
Lane A recovered all 70 both-direction survivors in the two authorized
marked one-neutral 16/17 slices. C has the cases for its exact joint check.
This is not a crossing compatibility test or a terminal claim.

| `(D16,d16;shape16,shape17)` | Side frames | Raw | Neither | Forward only | Reverse only | Both |
|---|---:|---:|---:|---:|---:|---:|
| `(67,5;2333,3334)` | 1,078 × 30 | 32,340 | 17,904 | 13,644 | 746 | 46 |
| `(68,4;2333,3334)` | 311 × 91 | 28,301 | 15,241 | 12,944 | 92 | 24 |

Each raw slice contains 16 old round-16 pilot headers, checked by the
original IDs, masks, within-shape ranks, product ranks and every group bit.
There are no old both-pass IDs in `(67,5)` and one in `(68,4)`:
`(frame16,frame17)=(2501780,31298)`, old zero-based pilot row 286.
Thus 69 of the 70 were not in the old pilot. The old pilot had already
reported no joint assignment for its 47 total both-pass IDs.

## Identity and conservation

- `scratch/A/r18/survivors.cases.tsv` is the headerless, sorted C handoff.
  Each row gives `frame16 frame17`, then `host neutral mask0 mask1 mask2
  mask3` for order 16 and for order 17. IDs are zero-based full stream
  ordinals from round 16, not local ordinals, profile IDs, or host IDs.
  Each `host` is the zero-based row in the pinned graph6 catalogue.
- `scratch/A/r18/survivors.tsv` gives the same physical IDs, shape-slice
  margins, hosts, neutrals, four decimal masks, singleton labels for each
  increasing mask (semicolon-delimited groups; ascending original labels
  within each), and the ordered row/column axes for the crossing matrix.
  Rows are the original order-16 private labels and columns the original
  order-17 private labels; both are sorted and omit the common neutral.
  Tests in the reverse direction use the transpose, not a renumbering of
  graph6 labels. `prior_pilot_row` is `-` if absent.
- Streamed 2,817,701 / 59,521 existing side records and retained only
  1,389 / 121 demanded frames. Strict original stream ordering was
  checked on clean replay; selected rows were checked against the old
  per-host counts and exactly 1,259 / 111 weighted cells. Ordinals were
  counted before discarding non-target side rows. No other target
  stratum's header product was formed.
- C's unchanged `Gate` resolves all 12,762 exact group keys needed here;
  all four overlapping archived whole-roster receipts agree on clean
  replay. At each destination pair separately, keep frames whose source
  profile passes against the opposite destination; materialize the cross
  product of the two accepted lists. A separate direct loop over physical
  frame pairs checks the full raw ID set's group bits, bucket masses,
  and equality of the surviving ID set. See `scratch/A/r18/buckets.tsv`:
  5,472 / 5,778 raw labelled destination-pair buckets, of which 24 / 18
  have both-pass headers. The exact four counts also agree with C's
  frozen weighted shape result. There is no symmetry factor.

## Calibration, checks and cost

The smaller 6/7 run reproduces all 34,504 physical IDs and every ordered
group bit, all 2,067 archived C group receipts, all 29,220 host-pair
receipts, 31,495 both-pass headers, and all 153 planted marks (142 distinct
physical IDs). Reversing the read order swaps the one-direction-only
count of 3,009 between the two directions. The equal-margin adjacency
counterexample and demand permutation control still pass.

On the target, A independently used the archived `panel16` literal
first-witness evaluator at the physical singleton labels, with no profile
key or memoized direction result. An every-97th-ID sample (626 records)
took 1.42 CPU-s and matched all bits; the estimated full cost was 137.56
CPU-s, not a tail bound. Independently checking all 60,641 raw IDs took
112.91 CPU-s and 27,288 KiB RSS, with `literal.oracle.tsv` byte-identical
to `raw.flags.tsv`. No compatibility/terminal solver was run by A.

The clean binder replay took 30.71 CPU-s including builds. Fifteen
deterministic outputs match byte-for-byte, and the clean summary adds
only the four overlapping archived whole-roster receipt matches. The
two production/replay runs plus the independent target check and sample
account for 176.07 measured CPU-s (0.04891 core-h), peak 330,904 KiB
(compiler; binder checks ≤90,496 KiB), and about 5.1 MiB allocated scratch.
At most two solver/checker processes ran simultaneously; no detached
jobs remain. Both prior freezes pass (33 A and 46 C entries).

```sh
sha256sum -c ralph/lanes/A/ROUND18_FREEZE.sha256
bash ralph/lanes/A/replay_small_slices.sh all r18-review
bash ralph/lanes/A/replay_small_slices.sh literal r18-review
cmp scratch/A/r18/survivors.cases.tsv scratch/A/r18-review/survivors.cases.tsv
cmp scratch/A/r18/literal.oracle.tsv scratch/A/r18-review/literal.oracle.tsv
```

No new graph, certified exclusion, degree-distribution debit, or
whole-case debit. Do not scan other slices or the 2.54-billion survivor
roster based on a result here.
