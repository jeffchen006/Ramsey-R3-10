# Round 11 — five e108 classes still missing

**Partial enum:** GR Table 14 gives 2,104,151 order-32/e108 classes.
Lane B now supplies **2,104,146**, comprising 2,102,271 deletion-reducible
and 1,875 deletion-critical classes. **Scoped cert:** 47 newly recovered
critical classes cannot extend at an MTF degree-seven root. This is not
floor 109: five classes are missing and the reducible tranche still needs
a terminal proof cover. No profile subtraction or candidate was reported.

## Exact e98 parent wave (enum, then scoped cert)

Use `src/e108_e98_r11.sh` under `ralph/lanes/B` from `scratch/B`; each
invocation is under `nice -n 5 timeout --kill-after=5s 7m` with the script's
16 GiB virtual memory ceiling. `search NEWDIR` rebuilds the existing N
stitch/deck/hypergraph tools. The same smaller control regenerates 36 of
42 e22 critical classes from independent order-15 parents (36/36 same as
N's output by Traces); exact thinning of 336 smaller deck classes produces
the stored e16 parent. The two frozen masked e108 controls recover exactly
the previous 3 and 16 hidden keys, respectively. The fresh input is checked
byte-for-byte against the frozen 122-parent queue before any target batch.

| Parent origin / step | Fresh e98 parents tried | New critical e108 classes |
|---|---:|---:|
| Round-10 first five targets only | 40 | 14 |
| Round-10 six repunctured targets only | 69 | 18 |
| Shared between those two origins | 13 | 2 |
| Exact e98 deck of the 34 new targets | 214 | 12 |
| Exact e98 deck of the 12 new targets | 40 | 1 |
| Exact e98 deck of the final new target | 1 | 0 |
| Total | 377 | 47 |

Each lift checks both d=7 and d=8; new parents are intersected with neither
the immutable round-10 deny set nor the accumulated canonical tested set.
Each generation is split into two deterministic, disjoint batches; the
last 20-parent batch and the singleton were both zero-yield, so this wave
stopped. Its small-scale time was 34.99 CPU-s including control builds,
decks, lift and de-duplication (14.62 CPU-s lifting alone). Independent
validity and proof production+replay cost 5.04 CPU-s, for **0.85 CPU-s per
new checked class** all-in, excluding the fresh generation replay. This
is retrospective, not a rate forecast for the last five. The fresh replay
at `work/e108_r11_replay` matched the exact ledger, tested parent set and
novel keys byte-for-byte (32.20 CPU-s); same algorithm, not an independent
generation method. See `logs/e108_e98_r11_search{,_replay}.log`.

`prove work/e108_r11` validates the 47 keys, and `replay work/e108_r11`
reruns the checks without constructing LRATs. It checks independent-nine
witnesses for **all 5,076 edge deletions**, validates the labelled keys,
binds their disjointness from the prior union, and verifies the new critical
union with Traces (1,875 classes). Exact witness/complement row binding:
37 checked eight-demand cliques, 10 separately regenerated CNFs checked
by both `cake_lpr` and `lrat-check` (four RUP and six CaDiCaL proofs; nine
pinned and one unpinned). Same MTF fixed-root obstruction as B-013; these
proofs do not cover any other inputs. `logs/e108_e98_r11_prove.log` and
`work/e108_r11/{cliques.tsv,complement.tsv,pins.tsv,production.log,replay.log,proofs/}`
are the proof receipts. See `ROUND11.sha256` for the frozen files.

## Untried coverage and cost (enum / estimate)

`src/e108_complement_r11.sh NEWDIR` from `scratch/B` takes the exact
e96/e98 deletion-critical decks from **all 1,875 supplied critical targets**
in four disjoint origin cohorts; this does not lift them back to e108.
It uses the calibrated N transversal method as above. Counts are unique
within each origin; the final rows are deduplicated across origins.

| Cohort | e108 targets | e96 critical parents | e98 critical parents | e98 outside recorded exclusions |
|---|---:|---:|---:|---:|
| Earlier lane B | 614 | 0 | 1,344 | 1,340 |
| Scout N | 61 | 24 | 244 | 0 |
| Other scout | 1,142 | 0 | 7,301 | 6,614 |
| Rounds 10–11 frontier | 58 | 0 | 391 | 1 |
| Distinct total | 1,875 | 24 | 9,170 | 7,954 |

Inventory 35.84 CPU-s. Among the 9,170 e98 parents, 471 are positively
bound to the canonical round-10/11 tested sets; another 745 are in older
recorded pools, not asserted all tested. The **7,954** are outside both
and are a distinct next source (not another e99–101 wave). At the recent
0.0388 CPU-s/parent for d=7/8 lifting, budget about **310 CPU-s lift only**;
allow ~10 CPU minutes including checking and canonicalization as a first
budget, not a coverage or yield guarantee. Suggested next round: price
disjoint old/scout-origin pilot shards, then scan only if the measured
cost fits and as directed by the critic. The queue is in
`work/e108_r11_complement/total.98.fresh`; it was **not** lifted this round.
Recovering nothing there would not exhaust e98, let alone e108.

e96 remains an orthogonal source: 560 e95 classes give exactly 33,312
deletion-reducible e96 classes by legal edge addition (35,840 raw). By
GR's count of 35,154 this leaves **1,842** deletion-critical e96 classes;
only 24 occur as thinned parents in the 1,875-target inventory. Full e96
acquisition is not priced by the deck rate. No broad e96/e97/e99+ target
wave ran. e88 remains frozen: no source census or ≥10× full-cost case.

## Complete lower-degree e95 arms (enum)

`src/e108_e95_low_r11.sh NEWDIR` first replays the positive d4/d5 smaller
controls (28,376 / 2,270 labelled leaves) and checks all 560 critical
e95 parents against the GR count with Traces. Its 32-parent forecasts
were 23.4 / 58.9 CPU-s for the remaining 528, gating on ≤110 per arm.
The complete run finds **zero** critical e108 outputs for d=4 and d=5
in 87.70 CPU-s, with all parents bound (`logs/e108_r11_e95_low.log`). In a
valid order-32 residue with α≤8, d≤8 by triangle-freeness and d≥4 because
the anti-neighbourhood must have fewer than R(3,8)=28 vertices. Combined
with N-001's completed d6–8 arms, no currently missing e108 key has a
puncture with any legal thinning to e95. This is a source exclusion, not
a proof that all punctures of a missing key have a parent in the e98
inventory.
