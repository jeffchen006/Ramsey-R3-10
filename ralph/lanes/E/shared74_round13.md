# Mixed saturated f=32: round 13

Core 17 only, zero-based in `scratch/E/r5_saturated/e11.g6`.
Scope: `(p,f,t)=(2,32,4)`, `δ(W)≥2`, `e(W)=11`, profile
`(10,10,11,11)`, universal `δ(G)≥5`, and E-021's all-graph
sole-missing `e=74` class premise. All four omission roles and
`K=6,7,8` stay in scope; no MTF restriction.

## Stops set before pricing

Same uncached support / fused-first and marked / original four-window
CNF pipeline as for core 16. Repeat the smaller calibration controls.
Cap census at 120 CPU-s and independent binding at 180 CPU-s; include
all canonical first branches, including empties, and count lifts. Bind
three separated bands (front/interior/tail); check every residual from
the price bands against independently regenerated original CNFs. Use the
larger of the projection and lift rates in the worst band, and the
0.77 historical replay/scan ratio as a pricing heuristic, not a bound.

Stop on a projected scan plus replay price above 2,400 CPU-s; also
keep actual aggregate scan/replay worker CPU caps within 2,400. Do not
authorize more than 100 exact terminal IDs without a separate dispersed
queue reprice. Hard production proof budget 600 CPU-s (including fresh
rebind and queue repricing); cap individual proof output files at 2 MiB
and round retained scratch at 1.25 GiB. Stop on missing/capped artifacts,
an unchecked proof, or SAT. No other full-core scans and no roster in
the scan pipeline. No candidate or exclusion before the applicable checks.

## Core 17: cover and first price (before production)

Key ``GCR`r_``; both enumerators matched 193,365 projections and
2,135,171 lifts; all **27** canonical first branches were bound, none
empty. The census cost 105.75 CPU-s and independent complete cover /
branch binding cost 23.95 CPU-s. All three price bands were independently
byte-bound to their global indices.

| Band | Projections | Lifts | Python scan / replay CPU-s | Native scan / replay CPU-s | Final IDs |
|---|---:|---:|---:|---:|---:|
| Front | 1,296 | 18,418 | 13.13 / 10.53 | 6.40 / 3.70 | 11 |
| Interior | 1,296 | 14,360 | 6.93 / 5.71 | 3.36 / 1.91 | 7 |
| Tail | 1,296 | 7,078 | 4.39 / 3.32 | 2.37 / 0.88 | 4 |

The Python path **stopped at price**, before any production scan:
worst-band scan estimate 1,959 CPU-s, replay 1,571 (the measured
front-band ratio is larger than the historical 0.77). All 22 band
residuals have checked original width-eight CNFs and fresh independent
CNF regeneration + CakeLRAT, 26.39 CPU-s combined. Pooled density
by projections suggests about 1,094 final IDs, worst band/rate about
1,641; these are estimates, not case counts or upper bounds. No
production proof expansion is authorized by this sample.

## Native graph-witness checker and scan reprice

Profiling singled out Python witness validation in both scan and replay.
`check_trace74.c` and `fast_trace74.py` replace only that validator in
the pilot/scan/replay entry points. No changes were made to the trace
producer, scanning order, fusion, marking, certificate format, or
frozen prior-round tools. For a vertex, OR the rows of its forced
neighbors to get its two-hop mask. Intersection with its own forced
row tests a triangle. At a propagation step a forced edge is retained;
an optional edge survives exactly when neither endpoint is saturated and
the pair has no common forced neighbor. Native validation reconstructs
these rows, checks the supplied independent-set masks without searching
for them, and returns both validated resulting bounds. The old Python
checker is independently callable on the same receipts.

Calibration: through order four all symmetric lower/upper pairs, all
edge targets and `2 <= alpha <= order` gave 15,531 accepted producer
traces with the same final rows in C/Python, covering all six result
codes. Both validators also rejected the same 31,479 mutated traces.
The prior smaller C13 marking and six-vertex exhaustive fusion controls
passed. At full dimension the scan receipts were byte-identical in all
three bands and both replays agreed on every band. No roster cut used.

**Authorize one native scan plus complete ordered replay, not a proof
wave.** Worst-band rate, max by lifts or projections: 955 CPU-s scan,
553 CPU-s replay, total 1,508 (<2,400). Split into 20 contiguous shards
of up to 9,669 projections (two waves of 10), each limited to 74 CPU-s;
bound merged replay to 800 CPU-s, 2,280 aggregate scan/replay. The cover
is 59.53 MB; worst-band receipt-byte extrapolation is 111.2 MB.
Including cover and receipt duplicates and the pilots, allocate 410 MB
logical for the scan/replay data; retain the 1.25 GiB hard stop. Read
the exact merged queue before authorizing any future proof work.

## Exact proof-tail stop and reprice (before proof production)

All 20 shards completed (546.36 CPU-s), ordered merge 9.11 CPU-s.
The merge left **262** IDs: the 100-ID stop triggered, so no production
proofs were launched. Select 16 equally spaced IDs in the exact ordered
queue, including first and last. All 16 original width-eight formulas
gave CakeLRATs and passed fresh regeneration plus recheck: 11.29 +
10.82 CPU-s, or 1.382 CPU-s per ID and about 362 for the exact queue.
Total CNF, LRAT and logs on the sample: 17.56 MB (about 288 MB scaled).

Authorize exactly the 262 IDs, regenerating **original** width-eight
CNFs; do not use narrower trial formulas in production. Six producer
slots at 46 wall-s each and three fresh rebind slots at 64 wall-s each
retain the 600 CPU-s ceiling: including kill grace, measured queue
reprice and a 10 CPU-s partition cap, at most 573 production CPU-s.
Cap individual files at 1.25 MiB; monitor logical retention against the
unchanged 1.25 GiB round ceiling. Byte-bind the proof partition to both
artifact sets (CNF and LRAT) and exact original receipt IDs. No closure
until all 262 original proofs and complete ordered replay pass.

## Narrow I8-cut pilot (not used for production)

The base encoding's triangle and degree clauses and edge/auxiliary
variable numbering do not depend on cut width. The independent-set
clauses of widths 2–5 are only a subset of those at width eight.
`width_shared74.py` tests this on each pilot formula by literal-clause
multiset inclusion with the same variable count, before solving and
checking CakeLRAT. It does not infer anything from a model of a weaker
formula. The existing small exact labelled enumeration controls passed
(10 configurations, completion counts include 3, 33 and 4; C/Python cut
makers agree, and bounded cuts recover exact alpha at sufficient width).

| Width | Checked core-17 band IDs / 22 | CNF bytes (total) | Pilot CPU-s |
|---|---:|---:|---:|
| 2 | 18 (4 relaxed SAT) | 1,807,608 | 1.93 |
| 3 | 22 | 1,943,888 | 2.16 |
| 4 | 22 | 2,533,719 | 2.48 |
| 5 | 22 | 4,005,450 | 3.47 |
| 8 (original) | 22 | 23,445,121 | 13.87 (producer + first CakeLRAT) |

Width three also checked all 107 held-out core-16 exact terminal IDs:
9,487,580 vs 114,159,152 CNF bytes, 10.95 CPU-s including reading and
binding to the stored wider files. These are pilot results only. For
future work, audit a standalone width-three generator/rebinder and
price a width-eight fallback on every unresolved ID. No SAT on a
relaxed formula is a candidate. No trial benefit was assumed in the
core-17 proof-tail budget.

## Terminal result

**Hand + enum + cert, pending critic:** core 17 only is excluded
under the scoped hypotheses at the start. The native full ordered
receipt covers all 27 independently bound first branches.

| Terminal result | Lifts |
|---|---:|
| Projection-wide graph witness | 1,198,635 |
| Other graph witness | 822,822 |
| Fused contradiction | 110,160 |
| Marked incompatibility | 3,292 |
| Original four-window CNF + checked CakeLRAT | 262 |
| **Total** | **2,135,171** |

The first four rows are hand + enum. The last row matches the exact
ordered queue and every CNF/LRAT ID, independently partitioned as
88/87/87. All 262 original DIMACS files are regenerated byte-for-byte
and checked by CakeLRAT. The original formulas do not require the
fusion or marking cuts. Native full ordered replay cost 309.45 CPU-s;
the producer and independent proof rebind cost 167.17 and 149.47
CPU-s. The terminal path with native ordered replay used **1,311.59
CPU-s = 0.36433 core-hours**, excluding sample/price pilots and the
additional unchanged Python replay audit. Seven mixed cores remain if
accepted. No full `(2,32)` closure, rigidity or Ramsey verdict.

The unchanged Python checker then independently replayed **all** 20
ordered shards (local IDs already byte-bound to the global cover and
receipt by merge), matched every category and all 262 terminal IDs, and
accepted every witness and filter verdict; `python.replay.total.17.log`
binds the summed counts. It cost 946.62 CPU-s, bringing terminal work
including that audit to **2,258.21 CPU-s = 0.62728 core-hours**.
Retained round data are about 601 MiB logical. Both freeze manifests
verify; `freeze.width.sha256` covers the separate narrow pilot.

Replay from `scratch/E/r13_shared` using fresh log names. The second
command below deliberately needs no native checker:

```sh
L=../../../ralph/lanes/E
R=$L/r13_worker.sh
key=$(sed -n '18p' ../r5_saturated/e11.g6)
sha256sum -c --quiet freeze.17.sha256
bash "$R" 390s 180 audit.cover.17.log python3 -B "$L/bind_shared74.py" cover.17.jsonl --key "$key" --branches pilot.17.branches.tsv
bash "$R" 2200s 1600 audit.receipt.17.log python3 -B "$L/order_shared74.py" replay cover.17.jsonl receipt.17.jsonl
bash "$R" 540s 210 audit.proofs.17.log python3 -B "$L/bind_shared74.py" cover.17.jsonl --trace receipt.17.jsonl --proofs proof.17
```
