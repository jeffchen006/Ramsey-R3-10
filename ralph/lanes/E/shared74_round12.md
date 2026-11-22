# Mixed saturated f=32: round 12

Core 16 only, zero-based in `scratch/E/r5_saturated/e11.g6`.
Scope: `(p,f,t)=(2,32,4)`, `δ(W)≥2`, `e(W)=11`, profile
`(10,10,11,11)`, universal `δ(G)≥5`, and the inherited E-021
all-graph sole-missing `e=74` class premise. No MTF restriction.

## Preisolation and stops

Use the unchanged uncached support and four-window pipeline. Rerun
the support, marked/fusion and three-band controls. Census cap 120
CPU-s; independent cover cap 180 CPU-s. Before authorizing any full
scan: bind all canonical first branches (empty branches included),
count projections/lifts exactly, and check original CNFs of every
residual in the front, interior and tail samples. Zero or few sample
survivors are not a bound on the proof tail: cores 7/13 had zero in
all bands and cost 11/29 terminal proofs.

Hard production limits: at most 2,400 CPU-s for scan and ordered
replay, at most 100 terminal residual IDs, 1.25 GiB retained scratch
for this round, and no proof expansion beyond 600 CPU-s. Stop/reprice
on an oversized cost estimate, capped/missing component, a SAT result,
or excess terminal IDs. Work on no other full core in this round.

## Whole-cover price (recorded before production)

Core ``GCR`v?`` has 25
canonical first branches; 23 nonempty, 2 empty. Census and independent
binder match 98,448 projections and 834,106 lifts (38.56 + 17.75
CPU-s). `pilot.16.branches.tsv` gives exact counts even for the empty
branches; the global ID lists bind every sampled row byte-for-byte.

| Band | Projections | Lifts | Scanner CPU-s | Open |
|---|---:|---:|---:|---:|
| Front | 1,084 | 12,306 | 11.62 | 2 |
| Interior | 1,085 | 9,931 | 5.99 | 0 |
| Tail | 1,085 | 6,893 | 3.49 | 0 |

Both front residuals checked from original four-window CNFs, including
fresh byte-regeneration and CakeLRAT (2.30 CPU-s total; 2.15 MB for the
two CNF/LRAT pairs). Pooled density extrapolates about 60 final IDs;
the worst band by projections extrapolates about 182. Neither is a
bound. Authorize the scan, **not** an unconditional proof queue.

The larger worst-band projection/lift rate gives 1,056 scan CPU-s;
the largest prior replay/scan CPU ratio is under 0.77 (r11), giving
a replay estimate under 814 CPU-s. Caps: 16 shards at 90 CPU-s and
one replay at 900 CPU-s (2,340 total), two waves of eight scan slots.
Conservatively 190 MB logical bytes for cover + receipt plus shard
duplicates, scaling worst-band receipt bytes by lifts. Proof ceiling
100 IDs, 600 CPU-s and 1.25 GiB scratch for the round; verify exact
queue size before running, and cap individual output files at 2 MiB
to keep artifacts within budget. Require checked proofs for all IDs,
otherwise the core stays open.

## Proof-tail stop and reprice

The exact merged receipts leave **107** IDs. The initial 100-ID limit
triggered: no production proofs launched. Check a dispersed sample of
12 from the exact queue (including first and last), freshly regenerating
each. Reprice before committing to 107; keep the 600 CPU-s and 1.25 GiB
limits unchanged. Full independent receipt replay does not depend on
this repricing and can proceed in parallel.

Reprice: all 12 equidistant IDs in the exact ordered queue gave
CakeLRATs, also checked against fresh byte-identical original CNFs.
Production and fresh binding cost 8.15 + 7.23 CPU-s (1.28 combined
per ID, ~137 CPU-s extrapolated; allow >4×). Authorize exactly the
bound 107 IDs, no new IDs: six 60-wall-s proof workers and one
120-wall-s fresh binder, with an 8-s kill grace. Including measured
pilots, at most ~554 CPU-s even if all worker slot caps are reached.
At 2 MiB per output file, four files per ID and a separate 12-ID
pilot, proof artifacts are capped below 1,000 MiB; plus ≤190 MB for
the cover/receipt/shards and the initial two proofs stays below the
1.25 GiB stop. Any incomplete item leaves the core open.

## Exact result

**Hand + enum + cert, pending critic:** core 16 only is excluded under
the hypotheses at the top of this note. All four omitted-group roles
and `K=6,7,8` were retained. The independent branch binder matched all
25 entries, including both empty first branches. The ordered receipt
replayed all 98,448 projections and 834,106 lifts:

| Terminal result | Lifts |
|---|---:|
| Projection-wide graph witness | 440,393 |
| Other graph witness | 333,480 |
| Fused contradiction | 55,423 |
| Marked incompatibility | 4,703 |
| Original four-window CNF + checked CakeLRAT | 107 |

The first four rows are hand + enum. The 107 remaining IDs exactly
match both the CNF and LRAT filenames. The binder regenerates each
original four-window DIMACS byte-for-byte and runs CakeLRAT; these
CNFs do not require the fusion, marking or roster cuts. Receipt replay
took 383.71 CPU-s, 16 scans 542.52 CPU-s, production + final proof
binding 132.07 CPU-s. Terminal work in total (including both cover
binds, splitting/merging and excluding price and roster pilots) cost
1,138.88 CPU-s = 0.31636 core-hours. Retained round data are 237 MiB
logical. Eight mixed cores remain if accepted; no entire fixed-point
case or Ramsey verdict.

Replay from `scratch/E/r12_shared` with unused audit log names:

```sh
L=../../../ralph/lanes/E
R=$L/r12_worker.sh
key=$(sed -n '17p' ../r5_saturated/e11.g6)
sha256sum -c --quiet freeze.16.sha256
bash "$R" 390s 180 audit.cover.16.log python3 -B "$L/bind_shared74.py" cover.16.jsonl --key "$key" --branches pilot.16.branches.tsv
bash "$R" 1500s 900 audit.receipt.16.log python3 -B "$L/order_shared74.py" replay cover.16.jsonl receipt.16.jsonl
bash "$R" 420s 150 audit.proofs.16.log python3 -B "$L/bind_shared74.py" cover.16.jsonl --trace receipt.16.jsonl --proofs proof.16
```

## Roster cut (separate pilot; not used in the exclusion)

Inside a window, the degree-seven vertices of `W` are the known
singletons. An outside vertex is degree seven iff its fixed-set
neighborhood avoids the omitted group. After fusion, an outside
vertex with a forced edge into that group is not eligible as an
extra; one with no eligible edge into the omission is mandatory.
An extra must also have at least seven eligible neighbors outside
the omission. Two extras must lie in different groups and form an
edge, so their pair must be eligible. Given a choice of extras, the
entire degree-seven induced subgraph is determined: all other edges
lie in or meet `W` and are already pinned. Isomorphic windows must
share at least one induced-subgraph signature for a common `K`; use
the sorted degree and two rounds of neighbor-color refinement.
Signature equality is only a necessary condition.

`roster74.py` calibrates on 26 disjoint translated four-group layouts
of `C13(1,5)` (with degree four playing the role of degree seven): 26
exact and 26 partial positives, 26 wrong counts rejected, and exact
induced rows matched direct graph restriction. It rejected **31/107**
of the core-16 terminal queue in 6.05 CPU-s and **6/42** archived
core-9/18 terminal IDs in 1.82 CPU-s including repeat fusion. The latter
includes a rejection at `K=8`, not an instruction to omit `K=8`.

As a prefilter on the **581** fused-open lifts in those four archived
heavy-core bands, it rejects 290 before the old marked test;
however, roster plus still-needed marked calls cost **5.15** CPU-s
versus **1.96** for marked alone and produce only six fewer terminal
IDs. It is not a faster replacement for the existing scan; consider
it only on the final queue. No new full scan on 9/18.

Evidence: `scratch/E/r12_shared/{calibrate.roster.v2.log,roster.16.log,prefilter.*.log,freeze.roster.sha256}`.
