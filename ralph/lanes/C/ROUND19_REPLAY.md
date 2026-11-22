# Round 19: fifth-pole held-out bin, November 22, 2026

**Negative fifth filter (hand + enum); 12 distinct exclusions by the
unchanged signed join (hand + enum, pending critic).** No new fifth
veto, no fifth-filter speedup, no whole degree-key/case closure, and
no graph candidate or active job.

## Exact denominator

The bin selected in `ROUND19_PREFLIGHT.md` is frame16 **42679**, host
97, physical neutral **7**, and triple site **x=0**, of degree three
inside the 16-window. It is paired against *all* **116** triple
order-17 frames at the matching key `(75,5)`. Before this left frame,
the only eligible degree-three triple in original order was
`(42072,x=1)`; its right ID 16780 is in the frozen old pilot, so its
entire bin is unavailable under the predeclared rule. No fifth result
entered selection. An independent frame-prefix rebind from the
ordered catalogues (full 59,521-frame order-17 stream), physical
mark and support check, and row-union marginal check confirm every
one of the **928** ordered old-margin group bits and the four counts
`(00,10,01,11)=(18,86,0,12)`. No overlap with the old joint pilot,
the critic's 56 core-order-13 vetoes, or the two round-18 slices
(different degree key). The midpoint sample rule selected all 12
positive IDs, before any new test. No other bin was tested.

## Fifth-row result and controls

On this bin the neutral misses H because it is one of the three
original neighbors of x within W. The indexed check independently
rebound A's format-v1 rooted cards with an explicit residual
automorphism check. A separate full raw-catalogue pass over all
1,458 degree-three and 21 degree-four roots uses VF2 on residual
graphs without loading the index. For this actual H both recover the
same **356/14** rooted degree-three/four cards. Candidate row
generation using 3-combinations of the physical private labels and
the independent scan of every mask give the same decision on each
of **578 legal** `(ID,T)` rows; all **578** pass the five-pole gate.
The four original poles visit singleton sizes 1, 2, 3, 4 at frequencies
184, 862, 1,092 and 174, respectively. The fixed fifth-pole card W
is present literally (not a hypothetical new choice). There is no
credit for vacuous checks or additional half-joins.

The structural explanation is `proofs/panel19_fifth_row.md`: if z is
outside H, deleting neighbors of x in W gives all needed unmarked
cards for k≤3. If a degree-four card deleting to H exists, as it does
here, the five-card condition is vacuous on all legal rows of this
left frame. If no such card exists, the row must hit each original
size-four singleton group; if z is in H, use the full physical
contact checks instead. Do not extrapolate this negative result to
unpriced bins or assume every H has the degree-four card.

The 105 order-35 K2,4 markings give 420 restored cards, 420 planted
distinguished-pole rows, and 210 disjoint tight-pair plants with
correct literal physical inductions. The exhaustive small labelled
comparison checks 1,893 bindings, including 48 rejected size-two
restorations. A synthetic one-contact corruption leaves separate
positive choices for each pole but removes the common row; both
positive common rows survive the uncorrupted instance. A separately
checked all 1,479 high-degree roots and corrupted label bindings.

## Literal signed baseline, price, and accounting

The unchanged `panel16.cpp` baseline performed 33,064 literal probes;
all 12 IDs are arc-empty after signed consistency, with zero caps,
zero compatible tuples and zero terminal calls. Independent Python
physical package reconstruction and indexed signed joins agree
12/12 (all eight domains nonempty before joining for each ID; at most
two probes per indexed join). This excludes only the selected marked
bin: 104 of its 116 IDs were *already* rejected by an old marginal,
and 12 are newly explicitly signed-tested. Pending acceptance the
old **2,542,514,376** both-pass not explicitly signed-tested falls to
**2,542,514,364**; net of the separate 56 prior structural vetoes,
**2,542,514,308** are neither explicitly signed-tested nor excluded
by those vetoes. None of the 12 are structural-only credits.

| CPU seconds | First | Clean |
|---|---:|---:|
| Physical census selection rebind + 928 bits (excluding frame emission) | 1.02 | 0.87 |
| Unchanged baseline, incl. domains and both searches | 0.09 | 0.05 |
| Fifth indexed binding, rows and filter (incl. startup) | 0.39 | 0.26 |
| Independent unindexed fifth-row + raw catalogue replay | 1.25 | 0.91 |
| Independent signed join/domain replay | 30.18 | 32.96 |

In the first indexed run, recorded process-clock stages are 99.88 ms
for raw binding, 47.90 ms for the index/card binding and local masks,
8.00 ms for row generation and 5.47 ms for testing the shared rows.
The 2.44 CPU-s A spent on full root indexing/checking is separate from
C's costs. Terminal calls are 0 versus 0; adding the fifth test is an
overhead here, not a speedup. All C runs, rebuilds and the initial
60-CPU-second capped calibration development attempt cost **136.46
CPU-s (0.03791 core-h)**. The capped attempt contributes no evidence.
Two passes on the successful check cost 76.55 CPU-s combined. Peak
RSS 291,468 KiB including compilation, ≤37,864 KiB for checks.
Two work dirs use about 2.7 MiB of allocated space. Fifteen clean
matches (ten byte-identical and five after removing timings).
No further target work under this directive.

## Replay

```sh
sha256sum -c ralph/lanes/C/ROUND19_FREEZE.sha256
bash ralph/lanes/C/replay_panel19.sh "$PWD/scratch/C/r19-review"
cmp scratch/C/r19/indexed.rows.tsv scratch/C/r19-review/indexed.rows.tsv
cmp scratch/C/r19/indexed.cards.tsv scratch/C/r19-review/indexed.cards.tsv
```

The scope and new method are `hand + enum`, not a checked UNSAT proof
for the R case or a flow candidate verdict.
