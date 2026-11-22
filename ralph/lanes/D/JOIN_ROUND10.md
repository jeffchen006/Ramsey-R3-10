# Unrestricted induced-P8 join: calibration, sample, and stop

The source is **all 168,540 generally live** P7 representatives in
`scratch/D/joint9/all-live.tsv`. No global L=7, no-induced-P8, no-C6,
flat-square or max-codegree-one-hub library enters this experiment.
The 187,712 oriented halves have 1,829 common eight-star fingerprints
and 23,088,908 ordered parent pairs. These are prejoin counts, not ten-star
profile counts. D-019 says an induced P8 exists somewhere, not that every
kernel has one or that marking a path is an unrooted partition.

`induced_pilot.py` drops the other endpoint's unique exterior mask 258
from each half. In a shared cell of size `n` with endpoint marginals
`l,r`, the number of common exterior neighbors ranges from `max(0,l+r−n)`
to `min(l,r)`. These endpoints are opposite-side nonneighbors; they have
no *anchor* common neighbor. Their total overlap is 1..3 by domination
and the cap. Reject a parent pair before expanding if the lower bound
exceeds three or the upper bound is zero. Two common exterior vertices
cannot also share two of the eight shared anchors. Separate counts of
common/left-only/right-only/neither give the actual ten-star multiset.
No general cycle assumption is used. Reversal swaps both roots and both
halves. Give an oriented half a stable ID. Keep the smaller-ID half on
the left; when IDs tie compare the child with its reversal. Deleting either
endpoint of a child recovers the directed pair, so no different pairs on
the same side of this comparison duplicate a canonical child.

**C22.** All 31 planted physical induced P8 marks pass both orientations.
Direct cell-by-cell common-neighbor counts of these 62 views: 42 have
codegree 2, 20 have codegree 3. Zero-overlap would lose all positives.
The planted P7 library joins to 13 labelled children / nine orbits; exact
graph search over all nine recovers precisely the five planted coloured
classes. This also works with global maximum path eight on the control
where that holds. The positive global-cap control is not a target premise.

| Sample (fixed seed; within each fingerprint without replacement) | Initial | Independent second seed |
|---|---:|---:|
| Pairs per fingerprint / actual pairs | 12 / 21,948 | 24 / 43,896 |
| Pass inexpensive overlap index | 21,142 | 42,376 |
| Labelled / canonical sampled children | 52,022 / 25,848 | 103,920 / 51,791 |
| Fingerprint-weighted canonical estimate (±1 design SE) | 20.00M ± 0.27M | 20.29M ± 0.19M |
| Weighted estimate after basic graph propagation | 16.29M | 16.23M |
| Estimated text output | 2.37 GB | 2.40 GB |
| Measured sampler CPU, including reading source | 9.82 s | 13.34 s |

Weight each fingerprint by the number of ordered pairs in its bucket,
not by the number of sampled children. Full multiplicity strata and
overlap-by-codegree totals: `scratch/D/ind10/pilot-summary.log`. The
largest fingerprint has 120,042 pairs; per-pair child counts have weighted
median 1, p95 4 and p99 7 in both draws; the maximum *observed* is 14.
Weighted within-bucket emission-time estimates were 741 / 1,204 CPU-s,
not hard limits. An additional 150-node graph-only completion pilot on
70 spaced, basic-live second-draw children exhausted 26 and **capped 44**
in 0.81 CPU-s. Even this first cap would cost order 50 CPU-h on 16.2M
roots at the pilot rate; it is not an estimate of a completed search.
The overlap index alone is inadequate. **No unrestricted join or SAT
wave was launched.** The small, explicitly scoped hub joins below are not
substitutes for this source.

Replay from the repository root with the usual limits: `induced_pilot.py`
on `joint9/long-cal.tsv` (no `--sample`), then on `joint9/all-live.tsv`
with `--sample 12 --seed 181013` and `--sample 24 --seed 521091` in distinct
destinations. Build the 10-star filter/search by copying both
`long_filter.cpp` and `long_search.cpp` into scratch, applying
`induced_eight_filter.patch` to the **copy** of `long_filter.cpp` and
compiling each with `-DINDUCED_EIGHT`. The frozen round-9 source stays
unchanged. BASIC `filter 40 9` has no maximum-path cap. `pilot_report.py`
reconstructs weighted costs from the ordinals and actual screen output.

## Conditional P8 audit that *does* finish

Under the different, already very restrictive single-hub hypothesis in
`DEFECT_MATCHING.md`, take all generally live P7s again. Restrict both
P6 end-deletions to the **same hub**. The 137 marked P6 survivors at
stage 3 yield 1,283 marked P7s and 12,375 marked P8s; do not claim they
are empty. With the six P6 marks at stage 4, only 14 marked P7s survive.
There is exactly **one raw parent pair** with matching fingerprints and
one permissible unmarked P8. Its two seven-path deletions have **no common
choice of hub**. This is an independent alternate ending to the final six
hub searches, using D-019. The main hub exclusion only requires D-015.
`hub_lift.py`, `marked_p8_join.py`, `hub4/{lift.log,p8-cost.log,join8.log}`.
Both marked end-deletions have direct C22 checks at 155 P7 and 31 P8
physical marks, all sites and both orientations (`lift-cal.log`).
