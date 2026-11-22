# Round 17 — weighted exact first filter for one-neutral 16/17

**Hand + enum, pending critic.** For the ordered one-neutral marked
cap-five `K4,4` 16/17 frame roster, the bidirectional package-existence
filter leaves exactly **2,542,514,492** of **15,051,526,031** labelled
headers; it rejects **12,509,011,539** without a header scan. This is
only the first necessary filter. It neither identifies compatible
packages nor extends a joint assignment to a graph. No new terminal
checks were run. Of the 47 round-16 pilot headers passing this filter,
all already failed the joint check. Thus **2,542,514,445** labelled
survivors have not passed through or been rejected by the joint check.
No candidate and no full 16/17, R(5), or Case R closure.

## Principle and provenance

`proofs/panel17_weighted.md` proves that a single group asks only for
the full destination adjacency, the labelled neutral, and the source
multiset of required row sizes with neutral bits. Sizes 2, 3 and 4 are
checked using every subset of rows. A source profile is the multiset
of group-demand multisets. At a fixed compatible pair of destination
hosts, multiply the two independently filtered frame-weight sums:
`[sum_P L_h(P) F(P,k)] [sum_Q R_k(Q) F(Q,h)]`. This is a product of
finite sums, not statistical independence and not addition of reject
marginals. Host identity includes the catalogue order and labelled
neutral. Source and destination marks, site labels, crossing
orientation, and the neutral must be recovered from the original
frames for later compatibility checks; a profile cannot substitute for
a physical frame. The previous ordered per-frame rosters are unchanged.

Lane A's one-sided weight files in `scratch/A/r17-stream/weights{16,17}.tsv`
stream the round-16 frame producer and independently bind the per-host
projections back to the original shape inventory. Each serialized
weight cell is `order D d host neutral profile count`; numerical types
in groups and groups themselves are sorted and duplicates are
retained. Only complementary `(D,d)` keys are matched. Their weights
sum to 2,817,701/59,521 frames, with 2,223,225/28,834 cells and
40,647/119 labelled hosts. Maximal one-side cell weights are 84/66.
No count of unlabelled isomorphism classes is asserted.

## A complete quotient, not a header scan

| Left `(D,d)` | Compatible host pairs | Raw labelled headers | Pass 16→17 | Pass 17→16 | Pass both |
|---|---:|---:|---:|---:|---:|
| `(66,4)` | 106,680 | 6,301,695,100 | 5,014,812,658 | 1,764,110,258 | 1,384,800,764 |
| `(67,5)` | 68,580 | 2,908,149,371 | 1,925,984,102 | 706,028,267 | 460,905,746 |
| `(68,4)` | 233,562 | 4,368,270,858 | 2,802,989,131 | 956,861,805 | 601,031,627 |
| `(69,5)` | 58,464 | 822,786,130 | 300,068,952 | 199,040,492 | 71,126,535 |
| `(70,4)` | 109,184 | 615,165,768 | 127,742,022 | 113,435,224 | 24,649,820 |
| `(71,5)` | 6,512 | 35,458,804 | 0 | 9,076,812 | 0 |
| **Total** | **582,982** | **15,051,526,031** | **10,171,596,865** | **3,748,552,858** | **2,542,514,492** |

The four disjoint global categories are both pass 2,542,514,492,
forward only 7,629,082,373, reverse only 1,206,038,366 and neither
3,673,890,800. Of 582,982 host-pair buckets, 549,727 have nonzero
intersection. The largest bucket weighs 148,356 raw headers, and the
largest population surviving inside any one bucket is 60,480.
All 34 shape strata are in `scratch/C/r17/target.count.log`.
The native gate made 829,178 distinct host/group decisions after
short-circuiting, split as 47,450 of size two (46,682 pass), 418,524
of size three (301,310 pass), and 363,204 of size four (30,260 pass).
There were 166,899,580 weighted profile evaluations with reuse of
group answers. No individual target headers beyond the existing named
pilot and no joint tuples were enumerated.

### Independently confirmed zero stratum

The marked 16/17 scope with `(D16,d16)=(71,5)` is excluded by the
16→17 direction alone (**hand + enum**, pending critic). Python
recomputes every one of the **76** group predicates for all 1,238
source profiles against the only two destination host/neutral keys,
`(order=17,host=5,z=0)` and `(order=17,host=6,z=0)` (zero-based).
Sixteen of 38 group types pass on each, but no entire profile passes
on either. The complete weights here are 68,986 × 514 = 35,458,804
headers; this calculation is independent of all reverse results.
The check uses hitting every independent set of forbidden size, not
the native subset-alpha recurrence. Evidence: `forward-zero.log`,
`stratum.count.log`, and the independently bound one-sided inputs.
The full count also lists five other zero shape products, but their
gate predicates were not subjected to this complete extra check.

## Calibration, checks, and cost

- On all 34,504 literal smaller 6/7 IDs, the independent Python
  readout matches in both directions, at every individual ID and
  each of 29,220 host pairs: 31,495 pass both, 3,009 pass 6→7 only;
  the other outcomes are empty. A separately binds all 153 physical
  plants (142 distinct header IDs) and checks all 2,067 emitted group
  predicates. Equal margins with different destination adjacency need
  not agree (A's named `326→(85,0)/(88,0)` control).
- All 544 prior bound target pilots agree direction-by-direction
  with their uncompressed domain counts and independent Python
  independent-set hitting: 47 both, 140 forward only, 96 reverse
  only, 261 neither. The pilot has physical singleton sizes 2, 3 and
  4. The independent arithmetic check binds every full host pair to
  its weights, verifies the product of marginal subtotals, reproduces
  the six keys and matches all 34 raw shapes to A's old table. Only a
  deterministic sample of 440 full native group predicates is independently
  re-evaluated (35 of size two, 216 of size three, 189 of size four); an
  arithmetic audit of all buckets is not a full replay of every group
  predicate.
- Priced `(71,5)` at 3.94 CPU-s including stream setup, followed by
  139.45 CPU-s for the full quotient, 125,008 KiB RSS (~122.1 MiB).
  The separately measured complete smaller literal path was 1.24
  CPU-s; the native pilot 0.83 CPU-s and independent all-pilot hitting
  139.91 CPU-s (115,064 KiB). The full target arithmetic audit took
  6.72 CPU-s, independent sample receipts 48.85 CPU-s (92,136 KiB),
  and the complete `(71,5)` forward recheck 8.09 CPU-s.
  No process exceeded 512 MiB virtual memory. Retained outputs include
  only 582,982 quotient bucket rows (~21.4 MB logical), never the
  15-billion-header product. `scratch/C/r17/price.txt` records the
  pre-run estimate and limit. Package count is `enum`, not a SAT cert.
- A clean rebuild and rerun reproduced 17 deterministic outputs byte for
  byte, including every compatible host-pair bucket. Total charged C
  time including both runs, all checks and exploratory builds was
  **784.87 CPU-s (0.21802 core-h)**. The compiler was the highest-RSS
  process at 299,764 KiB. `scratch/C/r17/{budget.log,clean.compare.log}`.

Replay from the frozen inputs:
`bash ralph/lanes/C/replay_panel17_weighted.sh full`.
The script writes only under a fresh `scratch/C` directory. `controls`
and `stratum` are available for narrower rechecks. Evidence paths and
hashes: `ROUND17_FREEZE.sha256`.

## Next

Do not scan 2.54 billion survivors: even 1 ms each would cost about
706 core-hours without any independent replay. If authorized, develop a
way to recover original frame IDs only for passing profiles in those
host pairs. Price the complete physical joins on the two smallest
nonzero shape slices first: `(67,5;2333,3334)` has 46 survivors and
`(68,4;2333,3334)` has 24 (shape digits ascending). Those are not
closed. Beyond such slices, a stronger filter must preserve physical
crossing orientation and the singleton labels; agreement of marginal
packages cannot be used for that test.
