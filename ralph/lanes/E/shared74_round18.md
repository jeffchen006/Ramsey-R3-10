# Mixed saturated f=32: round 18 pricing, core 1 only

Zero-based core **1** is `G?bFbo` in `scratch/E/r5_saturated/e11.g6`.
There was no comparable pre-existing ordered branch census across
`{1,6,9,18}`; the interrupted legacy scans on 9 and 18 do not rank
all four, so this uses the critic's default. Round 17 accepted core 15
as E-041. This round did not run the other three cores.

Scope: `(p,f,t)=(2,32,4)`, `δ(W)≥2`, `e(W)=11`, mixed profile
`(10,10,11,11)`, universal `δ(G)≥5`, and the all-graph E-021 premise
that all four `F\A_i` windows must be copies of the sole missing
order-26/e74 class. No MTF assumption. Fixed degrees are 8 on W and 7
on the 24 attachment vertices. The projected cover omits a size-11
group and binds its exact support as a lift; for each lift, tests cover
all four omission roles `i=0,1,2,3` (two size-10 and two size-11),
including the shared degree-seven count branches `K=6,7,8`. The proof
formulas independently use all four windows, not the E-021 compatibility
filter as a SAT axiom.

## Exact cover and sample

Producer: 20.57 CPU-s. Independent direct support generator: 10.74
CPU-s. **Byte-identical** ordered results: **24 nonempty first branches,
68,323 projections, 565,531 lifts**. The earlier counters 113,102 and
112,491 are not the projection denominator. Local catalogues agree at
48 size-ten and 622 size-eleven supports; `|Aut(W)|=2`.
Cover SHA256: `d9d3d68bd75ddc164498bc2948a02e7e98ea4101e7b5a6712acd6f6fe5b63c6c`.
`metrics.1.tsv` freezes the half-open projection and cumulative lift
boundaries and times for each first branch, including receipt bytes.

For each branch, sample up to 48 disjoint rows in each band and **all**
their lifts. The ordered cover bytes bind the sampled rows, and a
separate audit checks the exact offsets, disjointness and terminal IDs.
Untouched native scanning reproduced all instrumented receipts
byte-for-byte; untouched Python replay checked each one. Native replay
also passed on the same receipts.

| Band | Projections | Lifts | Hard lifts | Terminal IDs | CPU-s scan / native replay / Python replay | Receipt bytes |
|---|---:|---:|---:|---:|---:|---:|
| Front | 1,128 | 10,638 | 468 | 20 | 2.99 / 1.19 / 3.77 | 331,594 |
| Interior | 1,128 | 9,439 | 328 | 4 | 1.75 / 1.20 / 2.83 | 262,469 |
| Tail | 1,129 | 5,708 | 241 | 0 | 1.09 / 0.88 / 1.90 | 180,679 |

Hard means no single-window graph witness. The 24 terminal IDs occupy
14 projections in five branches; two front blocks have eight IDs each.
No tail hit is not a tail exclusion. Round-robin across the six
nonempty `(band, first branch)` terminal strata, using center-first
global projection IDs per stratum, selected 16 distinct matched IDs.
All six strata are represented; the remaining eight sampled IDs did
not receive proofs and are not debited from anything.

The smaller support control, native/Python exhaustive tests through
order four, 520 translated C13 positive/negative pairs and six-site
exhaustive test passed. The six-site SAT control reached the wide
fallback; the negative gave two checked proof routes. Wrong branch,
wrong fresh proof ID, swapped lifts, and short/extra cover mutations
were rejected. On the matched target sample there were no fallbacks.

| Matched route | Checks | CPU-s run + separately rebind/check | Peak RSS | Bytes including fresh logs |
|---|---:|---:|---:|---:|
| Narrow first, including regenerated wide reference and clause inclusion | 16/16 | 10.02 + 3.96 = 13.98 | 40,988 KiB | 18,869,483 |
| Original width eight, including byte regeneration | 16/16 | 17.08 + 9.56 = 26.64 | 178,776 KiB | 17,789,500 |

The narrow route costs 47.5% less on these IDs, including the fresh
CakeLRAT rechecks, but retains ~6.1% more bytes. Wide-only times and
checks directly price the fallback work; the target sample does not
establish its frequency or tail cost. A planning charge per future
terminal ID is `3 × (13.98 + 26.64) / 16 ≈ 7.62 CPU-s` (both routes
charged, then tripled); max observed combined-artifact cost per ID
is bounded on the sample by 2,476,021 bytes before any safety factor.
Neither is a general proof budget. Price again from an exact queue.

## Request: scan and independently replay, not proof production

For each first branch and each metric, maximize the row-scaled or
lift-scaled rate over its three bands, then sum across branches. Take
the larger of this sum and the corresponding whole-band estimates.
Plan **219.12 CPU-s scan + 299.95 CPU-s unchanged Python replay**;
native replay by itself prices at 113.94 s but is not a substitute.
The exact cover is already frozen; a fresh two-way reconstruction
costs another 31.31 CPU-s if needed. Estimated receipt size is
24.78 MB, before index/metadata overhead. At this price, existing
55.29 MB logical + 16.98 MB shard input copies + twice 24.78 MB of
receipts (shards and merged) is ~122 MB combined; allow ≤192 MiB new
staging. The terminal proxy (~1,457 from the sum of branch maxima)
is driven by clustered blocks; it is neither a prediction interval
nor a terminal cap. In particular a modest scan price says nothing
about the affordability of a proof queue of that size.

Request only a full native scan and unchanged ordered replay of
this denominator: 12 contiguous shards, at most two workers, then
an exact ordered merge, capped at 0.40 core-h. A starting cap is
50 scan + 65 replay CPU-s per shard (1,380 s aggregate), plus ≤60 s
for split/merge/roster with independent binding. Size shards by
up to ~5,694 projections, splitting the costly branch across shards
if caps demand; stop on any missing/failed shard, not an exclusion.
Do not start terminal production without critic authorization based
on the exact distinct ID queue.

## Evidence and status

**Enum (exact cover), cert (16 pilot IDs only), estimate (cost).** The
conditional core remains open. No full core scan, new core closure,
involution case closure, rigidity claim, or candidate. This round used
about 0.0301 core-h, at most two workers, ~53 MiB retained logically,
and no detached jobs. An estimator attempt with stdin redirected by
the wrapper did no work; the explicit source-file rerun succeeded.

From `scratch/E/r18_shared`, `sha256sum --quiet -c freeze.1.sha256`
binds source, proof artifacts, branch table, receipt bytes and pilot
logs. Commands, expected ends and exits are in `jobs.tsv`/`exits.tsv`.
For clean replay of the cover use `ordered_cover74.py verify` with
the arguments in `verify.1.log`'s job entry. For proof audit, rebind
the two matched directories in scratch copies with `price_width74.py
rebind` (fresh logs must not yet exist), then run `audit_routes74.py
audit` on each. All commands and their caps are explicit in `jobs.tsv`.
