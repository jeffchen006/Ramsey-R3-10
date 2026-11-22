# Mixed saturated f=32: round 16, core 15 only

Core 8 was accepted (E-038). This round handles only zero-based core 15
`GCQf?{` in `scratch/E/r5_saturated/e11.g6`. Scope: `(p,f,t)=(2,32,4)`,
`δ(W)≥2`, `e(W)=11`, the mixed `(10,10,11,11)` profile, universal
`δ(G)≥5`, and E-021's all-graph sole-missing `e=74` premise. All four
omission roles and `K=6,7,8`; no MTF restriction or claim about other cores.

## Price before the complete scan

The known smaller support control and 1,200 band controls passed, as
did native/Python bounds through order four, 520 translated C13 controls
and their mutations, and the six-site exhaustive check. The exact-degree
six-site routes give the intended two completions vs zero, including
SAT with wide fallback on the positive and checked UNSAT in both routes
on the negative. `ordered_cover74.py` rejects swapped/short/extra rows,
swapped lifts, and a genuine narrow CNF misbound to the other branch.
The first native calibration wrapper lacked the current-directory `.so`
and failed before its tests; a fresh local build passed every control.

Census (36.04 CPU-s) and the byte-for-byte independent ordered cover
regeneration (53.42 CPU-s) agree: **94,738 projections / 716,045 lifts**,
34 first branches, all nonempty. The latter uses the independent direct
support generator, lexicographically orders projection and lift tuples,
and checks the full branch ledger. SHA256:
`c64297e77bc655aa7b353ae922d8118b816874af4d11271264599307f783b053`.
The full census's raw 276,191 projection counter is not the denominator.

| Per-branch band (up to 48 each) | Projections | Lifts | Hard projections / lifts | Terminal IDs | Scan / native replay / unchanged replay CPU-s |
|---|---:|---:|---:|---:|---:|
| Front | 1,544 | 14,460 | 203 / 544 | 17 | 3.79 / 1.98 / 4.01 |
| Interior | 1,544 | 10,852 | 79 / 171 | 3 | 1.72 / 0.90 / 2.09 |
| Tail | 1,546 | 7,372 | 85 / 148 | 3 | 1.26 / 0.71 / 1.48 |

Both replay implementations passed on all byte-bound samples. Full
per-branch counts are in `pilot.15.branches.tsv` and `hard.15.tsv`.
Hard lifts lack a single-window witness; per-row maxima are 20, 14, 6.
In the front band 13 of 17 terminal IDs are in one 48-row block (five
in one projection). Extrapolating terminal counts is not a guarantee
and the chance of hitting the 100-ID guard is material. Do not spend
proof-production budget unless the **exact** merged queue passes it.

Take the maximum over all three projections-based and lifts-based
extrapolations separately. Scan ≤233 and unchanged replay ≤247 CPU-s
as planning estimates, 480 combined. Plan eight contiguous shards of
at most 11,843 projections, at most four concurrent scan/replay
workers, caps 95 scan + 110 replay CPU-s each (150 + 165 wall, one at
a time per shard). Split+merge+queue CPU caps sum to 44 s. Even adding
the full worker caps for scan/replay, actual preflight overhead and
600 CPU-s reserved for comparative/production proof work, the budget
is about 2,400 CPU-s (<1 core-h). Cut off proof work if comparison or
exact roster fails; do not infer wider proofs from narrow bytes. The
largest sampled receipt extrapolated by row twice, plus both cover
copies and controls, gives <100 MB before possible proofs. If the
queue is 1–100, compare both routes on up to 16 dispersed IDs including
both ends, price fresh rebind and fallback, and independently check
the complete selected proof roster before any exclusion. The proof
stage has a 1.25-GiB total retention gate including its comparison data.

## Exact queue: stop at 142

All eight native scans and eight full unchanged ordered replays passed.
The merge bound every shard row to the global cover order and classified
all 716,045 lifts with no missing or duplicated ID:

| Disposition | Lifts |
|---|---:|
| Graph witness for entire projection | 559,940 |
| Other single-window graph witness | 142,652 |
| Fused contradiction | 11,733 |
| Marked incompatibility | 1,578 |
| **Terminal / open** | **142** |

The 142 IDs span 110 projections in 12 first branches; per-shard counts
are 0, 2, 0, 11, 1, 32, 49, 47. The two heaviest branches account for
48 and 32 IDs, and one projection accounts for five. The exact queue
extremes are `(22646,18)` and `(93731,12)`. A 16-ID dispersed list
including both extremes is recorded for possible future authorization,
but **the 100-ID gate fired: no target proof pricing or production**.
Neither the queue nor the pilot establishes an exclusion of core 15;
the status is open. The stricter `audit_routes74.py` was calibrated on
the six-site proofs (both routes accepted; wrong branch and wrong replay
ID rejected) before merge, but was not run on this core.

Scan and unchanged replay cost 101.51 and 133.07 CPU-s. Main path
including census, independent cover, split, merge and exact queue:
327.66 CPU-s (0.09102 core-h). All 41 wrappers: 349.09 CPU-s
(0.09697 core-h), 40 zero exits and the recovered native preflight
setup error. About 75 MB logical retained before manifest. No jobs,
graph candidates or additional mixed cores were run.

## Replay (no target solver)

From `scratch/E/r16_shared`, use an absolute scratch audit path `A`
owned by the replayer. `freeze.15.sha256` binds the tools, source,
cover, receipts, queue and controls. The independent cover verification
computes expected ordered bytes from the direct support generator; the
unchanged replay separately verifies the individual dispositions.

```bash
set -e
sha256sum -c --quiet freeze.15.sha256
L=../../../ralph/lanes/E
run() { nice -n 5 timeout -k 8s "$1" bash "$L/limited.sh" "$2" "${@:3}"; }
key=$(sed -n '16p' ../r5_saturated/e11.g6)
run 360s 180 python3 -B "$L/ordered_cover74.py" verify cover.15.jsonl "$key" pilot.15.branches.tsv
for shard in {00..07}; do
    run 165s 110 python3 -B "$L/order_shared74.py" replay "scan.15/cover.$shard.jsonl" "scan.15/cover.$shard.receipt.jsonl"
done
run 42s 22 python3 -B "$L/order_shared74.py" merge cover.15.jsonl scan.15 8 "$A/receipt.15.jsonl"
cmp "$A/receipt.15.jsonl" receipt.15.jsonl
run 24s 12 python3 -B "$L/sample_terminal74.py" "$A/receipt.15.jsonl" "$A/queue.15.jsonl" "$A/spaced.15.jsonl" 16
cmp "$A/queue.15.jsonl" queue.15.jsonl
cmp "$A/spaced.15.jsonl" spaced.15.jsonl
```
