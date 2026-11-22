# Round 16: one-neutral marked cap-five 16/17 pilot

**Hand + enum (pilot only, pending critique); estimate (production is
not authorized).** No candidate and no whole-case exclusion. On the
named 544 labelled headers, exact package checks found no possible
joint assignment. The remaining **15,051,525,487** labelled headers
are untested by the pilot. Nothing here alters 17/17, the zero-neutral
cases, or any unmarked case.

## Cover, roster and controls

`proofs/panel16_cover.md` proves the physical map. With one exterior
neutral, windows of orders 16 and 17 carry 15 and 16 private sites.
The sorted singleton group shapes are `2233` / `2333` and `2334` /
`3333` / `3334`; even the shapes with only two triples are retained.
All singleton sizes two through four enter the package enumerator,
and both directions bind to the same physical crossing variables.
Only the sole neutral is identified. There is no bit or half-plane
factor. A independently bound all 2,576 and 7 catalogue rows and
counted **15,051,526,031** labelled headers across six degree keys,
broken into 34 nonempty key/shape strata. See
`../A/ROUND16_ONE_NEUTRAL.md` and `../A/ROUND16_FREEZE.sha256`.

The pilot evaluates 16 ranks per stratum, including first, middle,
last and 13 dispersed seeded ranks. `panel16_summary.py` checks
all 34 exact products, sample uniqueness, rank and physical frame
bindings. The largest stratum, `(66,4,2233,2334)`, has 4,569,414,120
headers and is sampled; so are the large `(68,4,2233,2334)` and
`(67,5,2233,2334)` strata, and all six shape pairs. The sample is
stratified, not random-only, and gives no upper bound on unseen tails.

The smaller calibration uses all 153 planted asymmetric 6/7 windows
of 5-regular `(3,6,16)` catalogue graphs with a marked `K2,2` and one
neutral site. C++ and Python reconstruct both package directions and
all 1,596 keyed joint assignments. Their terminal reasons agree:
20 triangle, 1,576 live, with every actual full graph retained. The
independent audit rejects 306 one-direction flips, and verifies 612
single-group replacements that are valid in their own domain but
conflict across a crossing (306 per direction). It also rejects 153
contradictory terminal bounds. The open terminal reason in these
controls only means no contradiction was detected by propagation.

## Pilot result and timing

| Stage | Result |
|---|---:|
| Labelled headers tested | 544 |
| Have an empty domain in the 16→17 direction | 357 |
| Have an empty domain in the 17→16 direction | 401 |
| Have at least one empty domain (union) | 497 |
| All eight individual domains nonempty | 47 |
| All eight remain nonempty after rectangle filtering | 0 |
| Literal C++ join completed / probe-capped | 536 / 8 |
| Filtered C++ and independent Python complete | 544 / 544 |
| Joint assignments (target terminal calls) | 0 |

The literal C++ branch cap was set to ten million package probes per
ID, with at most 2,048 joint fillings and 200,000 packages per group.
The first exploratory target run halted at the first cap; no larger
cap was used. The production-*pilot* code reports each mode's cap
separately. Its literal path never licenses an exclusion when capped.
Its filtered path completes all 544 and Python then independently
rebuilds one exact empty domain for each of 497 IDs, and performs
an exhaustive indexed join after reconstructing all eight domains
for each of the other 47, including all eight literal tails. There
are no target terminal calls to compare. The independent control
join/terminal check is nonvacuous. Clean C++ replay reproduces all
per-ID domain counts, probe counts, cap outcomes, control assignments
and preflight responses when timing columns are omitted.

- Measured C++ run (both modes) **2.60 CPU-s** including setup;
  0.092 s initial host atlas construction, 1.703 s domain work,
  0.776 s capped literal join, 0.0067 s copying/filtering/filtered
  joining. Literal tails took 53.764–98.883 ms with the cap, not a
  price for finishing them. Largest observed individual domain: 3,592
  packages. No per-call reduction is used as an end-to-end speedup.
- Measured independent audit **166.99 CPU-s**, maximum **2.638 s/ID**
  and 16,936 indexed probes on one ID. The 34-row independent spot
  pricing runs and a clean native replay are additional charged work.
- A first-witness exact-existence preflight on the same pilot costs
  **0.46 CPU-s** as a standalone run including setup, with 176 cache
  hits, 826 misses and the identical 47 nonempty IDs. Combining its
  stage timings with the measured full-domain/filter cost only on
  the 47 passing IDs gives a modeled 0.566 s, versus 1.802 s for
  the all-domain filtered stages; this is not an integrated runtime.
- Rank-weighted per-header extrapolation by the 34 A strata, omitting
  repeated cold host atlas construction, is **11,400 core-hours** for
  the all-domain filtered C++ path and **4,348 core-hours** with the
  modeled preflight. Python replay as written extrapolates to roughly
  1.84 million core-hours. These are pricing estimates, not upper or
  lower runtime bounds. Cache performance, new tails and real target
  terminal costs are unknown at scale. No per-header production.

Lane C used under **310 CPU-s** including two independent timing
trials and clean replay, at most two concurrent processes doing this
work (audit plus short compile or replay), under 512 MiB combined
by the observed peaks; max independent RSS 100,024 KiB, max native
compiler RSS 291,568 KiB. Each phase had a 512 MiB virtual memory
limit, CPU and wall caps. C retained about 545 KiB including replay.
No jobs remain. The failed `r015_T` sent no report; scout R and N's
round-15 directions are not for this lane.

## Replay and next step

`bash ralph/lanes/C/replay_panel16.sh scratch/C/EMPTY comparison`
rebuilds and evaluates the smaller controls, the 544 target headers,
and their first-witness preflight. Use `full` to add the independently
reconstructed target audit. `ROUND16_FREEZE.sha256` binds the exact
inputs and round results; fresh timings need not match. From repo
root, `python3 -B ralph/lanes/C/panel16_summary.py summary scratch/A/r16 scratch/C/r16`
rechecks identity coverage and reproduces the measured/model table.

Ask A/critic before doing any more than a bounded sample. To skip
long per-header computation, a future round could count partitions
by destination `(host, neutral)` and source multisets of group demand
vectors, and intersect the two boolean compatibility maps with exact
weights. This does not justify caching literal join outcomes by
demands alone (physical singleton labels matter). No compressed
population count, reduction factor or scalable independent path was
measured here. H may formalize the short size/shape and existence-key
lemmas; they do not formalize the enumeration.
