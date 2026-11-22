# Lane B — round 10: critical-card generation and proof tranches

Run from `scratch/B`, with `ulimit -v 16777216`. All target jobs were
bounded foreground jobs. The admissible ceiling was 12 cores; peak was
two foreground pipelines. None remains live. No candidate order-40
graph, no floor-109 proof, and no t9<=88 or U88 upgrade.

## Three disjoint proof tranches (cert, local replay)

`timeout 5m nice -n 5 bash ../../ralph/lanes/B/src/e108_scout_r10.sh replay TRANCHE`
validates the input (C graph check and independently checked Python
private independent-nine witness for each edge), nauty form, disjointness
from the preceding full known set, Traces distinctness of the combined
critical part, and the exact sorted union. It verifies the positive
demand-clique witnesses, regenerates the pinned CNFs, and checks each
remaining LRAT with both `lrat-check` and `cake_lpr`. It compares ordered
proof indices and CNF/proof digests to production. Evidence directories:

| TRANCHE | Source | Witnesses | Cliques | Dual LRATs | Census after tranche | Deficit |
|---|---|---:|---:|---:|---:|---:|
| `scout` | `work/e108_r10_import/scout61.g6` (N-001 handoff) | 6,588 | 57 | 4 | 2,104,088 | 63 |
| `stitch` | `work/e108_r10_new/stitch5.g6` (slice B at e98) | 540 | 2 | 3 | 2,104,093 | 58 |
| `repuncture` | `work/e108_r10_micro/repuncture6.g6` (7 e98 parents from the five) | 648 | 5 | 1 | **2,104,099** | **52** |

Round 10 adds **72 individually checked nonextensions: 64 clique
witnesses and 8 dual-checked LRATs**, pending critic review. Each is
restricted to the supplied order-32/e108 graph as a degree-seven
residue of an MTF target, using the same demand/pinned-CNF semantics as
the round-8 tranche. These are extension verdicts, distinct from the
census numbers. Traces finds 1,828 distinct critical keys in the last
union; the unchanged 2,102,271 reducible keys are separately accounted.
The full e108 census is still short of the GR Table 14 count 2,104,151.
See `logs/e108_r10_{replay_scout,replay_stitch,replay_micro}.log`.

## Critical order-30 → order-31 → order-32 lifts (enum)

`src/e108_stitch_r10.sh` rebuilds the N `stitch.cc` and `deck.cc` kernels
and wraps them in a reproducible stratified pilot. For a deletion-critical
child and root v, thinning the card cannot delete an edge incident to a
star neighbour: an edge-private independent set already avoids v.
The repairs therefore lie outside the new star, hit every independent
eight-set disjoint from the star, and must each have a private row. A
separate leaf check requires every edge of the completed child to be
critical. Exact for fixed critical parent, degree and edge goal; not
a statement about coverage by the seed pool (see N-001).

Run `control`, `prepare`, `generate ... a`, `lift ... a`, then
`generate ... b`, `lift ... b`, followed by `repuncture` with a common
new output directory. `control` starts from the independent smaller
order-15/≤16 source (three graphs, two deletion-critical), recovers 36 of
the 42 known critical order-16/e22 keys, and gives exactly the scout's
36 output classes by Traces. The first setup incorrectly required all
three lower-level seeds to be critical; it failed before target work
and was corrected by filtering. `prepare` samples without target keys;
245 hash-selected known targets are sequestered for the recovery score.
The exclusion list normalizes 19,708 keys from the recorded scout pools
and the e95 source. For A/B, each of 64 disjoint prefix-critical seeds
is lifted at d=6/7/8; each fresh order-31 sample is then lifted at d=7/8
with nonnegative repair budget. The repuncture arms use d=7/8.

| Slice | Fresh inputs e98 / e99 / e100 / e101 | Distinct e108 keys | Masked known hits | New keys |
|---|---|---:|---:|---:|
| A | 127 / 128 / 128 / 128 | 34 | 3 | 0 |
| B | 122 / 128 / 128 / 128 | 85 | 16 | 5 |
| Seven-parent follow-up (input is the five new outputs) | 7 / 0 / 0 / 0 | 11 | not blinded | 6 |

Every output in A/B came from e98. Shared prep and A/B generation and
lift cost 135.0 CPU-s (includes seed selection, canonicalization and
novelty comparison): 27.0 CPU-s per new key. The adaptive seven-parent
follow-up cost a further 0.94 CPU-s (0.16 per new key). The full 1,024
parent cap is spent; no more target lifts were launched. Independent
from the witness/extension check, `logs/e108_r10_target_replay.log`
records the fresh deterministic replay and parent validation against the
recorded exclusions. Rebuild and compare with `timeout 9m nice -n 5 bash ../../ralph/lanes/B/src/replay_e108_r10.sh NEWDIR`.
The replay repeats the method, not a new algorithm.

For the next round, `timeout 3m nice -n 5 bash ../../ralph/lanes/B/src/e108_e98_queue_r10.sh NEWDIR`
reproduces the parent-only queue. Exact thinning on the complete
336-card smaller control matches the n15/e16 key in the scout replay.
On the 11 new e108 keys it gives 352 distinct induced cards, 178
labelled critical e98 parents, and 135 classes. After exclusions **122
are untested**. Evidence: `work/e108_r10_e98_queue/fresh.g6`,
`logs/e108_r10_e98_queue.log` (2.06 CPU-s incl. build/control). This is
an exact e98 deck of the eleven, not a census or a guarantee of finding
the remaining 52. Prioritize this queue over new e99–101 waves.

## Secondary e88 critical-parent price (estimate / open)

`src/e88_deck_r10.sh` regenerates the two 128-seed prefix samples and
greedily thins every puncture with three deterministic deletion orders.
The smaller control first splits the exact critical n16/e22 set 21/21.
From the training side (37 critical decks), the d5 planted weight-15
arm produces 2,250 marked leaves of 2,270 unrestricted, with identical
ordered output under an independent leaf-only filter. One of two
recovered classes is withheld. The initial weight-19 mark was empty
and rejected before target work. This tests the marker and deck; it does
not calibrate any completeness claim for the greedy deck.

| Order-29 parent edge level | Distinct parents acquired | Parents lifted | Marks d | CPU-s per 128, lift only | Critical e88 lifts |
|---|---:|---:|---|---:|---:|
| 78 | 397 | 128 | 6,7 | 3.19 | 0 |
| 79 | 1,534 | 128 | 6,7 | 1.60 | 0 |
| 80 | 1,598 | 128 | 6,7 | 0.73 | 0 |
| 81 | 707 | 128 | 6,7 | 0.38 | 0 |
| 82 | 174 | 128 | 6 | 0.11 | 0 |

Total pilot 28.11 CPU-s incl. all parent production/canonicalization,
sampling and ordered comparisons. The e78 deck reached 397/34,122
(1.16%); 4 keys overlapped the independent seed halves. Charging all
22.10 non-lift sample seconds to e78 and naively carrying forward linear
yield gives ~0.53 CPU-h acquisition plus ~0.24 CPU-h lifting. That is
an illustration, **not** the cost to obtain a complete e78 census: the
prefix-derived deck has no exhaustion argument, and novelty will saturate.

For a full-cost comparison let `N79`–`N82` be actual complete critical
parent counts and `A` be the aggregate acquisition, canonicalization,
validation and missing-source cost for **all five levels** (CPU-h).
Using only pilot rates, projected CPU-h would be
`A + (0.0249*34122 + 0.0125*N79 + 0.00570*N80 + 0.00297*N81 + 0.00086*N82)/3600`.
To be 10× faster than the old ~1,340 CPU-h e52 branch this must be ≤134
CPU-h, before terminal gluing. The unknown acquisition cost and all
four upper-level census sizes prevent a defensible speedup claim; for
example even 10M e79 inputs alone at the pilot rate would cost ~34.7
CPU-h **if supplied**. No e88 scale-up or missing-source closure. Logs:
`logs/e88_deck_r10_{control,probe}.log`.
