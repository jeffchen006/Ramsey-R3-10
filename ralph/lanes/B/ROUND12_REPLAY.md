# Round 12 — exact e98 parent wave

**Scoped enum: 7,954 of 7,954 scheduled parents tested at both d7 and d8;
zero new critical e108 classes.** The catalogue remains **2,104,146 of
2,104,151** (five missing). No repuncture, new extension proof, global
floor 109, or e88/U88 change. No candidate.

| Origin | Distinct parents | Labelled d7 critical leaves | Labelled d8 critical leaves | Lift / check CPU-s |
|---|---:|---:|---:|---:|
| Earlier lane B | 1,340 | 1,850 | 333 | 48.54 |
| Other scout | 6,614 | 8,978 | 4,043 | 261.19 |
| Total | 7,954 | 10,828 | 4,376 | 309.73 |

Across both arms and origins the 15,204 leaves yield **1,724 distinct
critical keys**, all in the archived 1,875-key critical catalogue. Traces
independently counts 1,875 on their concatenation. The terminal audit took
1.59 CPU-s; the budgeted run totals about 334 CPU-s including controls,
build and the interrupted attempt. No jobs left live.

## Calibration and budget

`src/e108_r12.sh prepare` rebuilds the same stitch/deck kernels used in
round 11. The independent smaller inputs reproduce 36 of 42 critical
order-16/e22 graphs with no unexpected classes, and the exact deck-thinning
control reproduces the one archived critical order-15/e16 parent. Both
frozen masked target controls reproduce their exact hits (3 and 16).
The production source is the original frozen 7,954-line `total.98.fresh`,
not newly sampled parents from a larger catalogue.

The disjoint source assignment is 1,340 old-B and 6,614 other-scout keys;
the one frontier key is also in the scout cohort and is scanned there
once. Scout N has no key in this queue. The 64-parent hash-distributed
pilots cost 2.87 CPU-s (old) and 2.50 CPU-s (scout); both returned existing
keys only. Pilot, build and controls cost 18.57 CPU-s. The prelaunch
projection was 332 CPU-s origin-weighted or 370 CPU-s at the slower rate,
plus a 60 CPU-s audit allowance. Both were within the 600 CPU-s budget.
The shell driver records a shard only after both degree arms and
canonicalization succeed. Editing the driver during one foreground run
interrupted its reader at `target.scout.010`; that shard had no receipt.
The resumed run used a copied driver and reran the shard. Its 9.93 CPU-s
failed attempt is charged separately, not counted as coverage.

## Set-aside parents and coverage limits

The frozen inventory remains **9,170 = 7,954 scheduled + 471 previously
bound + 745 set aside**. The 745 are retained as a separate immutable
category. `src/e108_r12_provenance.sh` binds **200 of the 745** to N's
named, previously replayed `audit.deck.g6` source for both d7 and d8.
It also shows 177 match N's `strong31.pilot` list, one matches `untried31`,
and 43 further entries match `ex31.j` outside the first three lists.
Those additional intersections are provenance hints, not credited as
executed rows without a fully bound replay. `not_deck_bound.g6` gives the
remaining 545. These 545 are distinct from the old 471 and the current
target queue. Neither a complete e98 census nor coverage of other root
degrees or thinning levels follows from the known-target decks.
The 0.03894 CPU-s/parent measured rate gives **21.2 CPU-s** for the 545
and **29.0 CPU-s** for all 745, before final audit. Using the slower pilot
rate gives 24.4 and 33.4 CPU-s respectively; propose a 40 CPU-s cap for
the 545 or 50 CPU-s for all 745. No additional set-aside lifts ran.

## Replay

From `scratch/B`, with the standard one-core bounded foreground schedule:

```sh
runner=../../ralph/lanes/B/src/e108_r12.sh
nice -n 5 timeout --kill-after=5s 2m bash "$runner" terminal work/e108_r12
```

The terminal pass is a no-search audit: it verifies receipts against the
frozen input schedule, accounts for both degree arms, rebuilds canonical
output keys from recorded leaves, validates order/edge/triangle/alpha
and independently checks isomorphism counts with Traces. It checks
disjointness from the other parent partitions and recomputes novelty
against round 11's frozen union. It is **not** an independent enumeration
algorithm. A changed digest deliberately injected into a disposable
receipt was rejected (`logs/e108_r12_audit_mutation.log`). A full
regeneration uses `prepare`, `pilot`, `finish`, `terminal` with a fresh
work directory; compare `plan.tsv`, `done.tsv` except its final CPU
column, `target.tested`, `target.remaining`, `produced.keys` and `novel.g6`.
