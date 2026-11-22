# Mixed saturated f=32: round 15

Core 5 accepted by the critic. This round prices only zero-based core 8
(`G?qbf_` from `scratch/E/r5_saturated/e11.g6`). Scope: `(p,f,t)=(2,32,4)`,
`δ(W)≥2`, `e(W)=11`, profile `(10,10,11,11)`, universal `δ(G)≥5` and
E-021's all-graph sole-missing `e=74` premise. All four omission roles
and `K=6,7,8` remain in scope. Not MTF-restricted.

## Gates before production

Re-run support, three-band sampling, native/Python proof-receipt and
exact-degree width-three controls. Rebuild the full canonical cover
under 120 CPU-s and bind every first branch, including empties, under
180 CPU-s independently. Sample 48 contiguous rows per branch per band
at front/interior/tail, with exact global index and byte binding. Price
native scan and unchanged Python ordered replay separately using the
worst band by projection and lift. Record hard and terminal lift
counts, concentration, and sampled terminal cost separately. Require
both priced and capped scan/replay ≤2,400 CPU-s in aggregate, at most
eight concurrent slots, formulas/proof/rebind including fallback
≤600 CPU-s, and total retained round data ≤1.25 GiB. For >100 exact
terminal IDs, stop and reprice on equally spaced ordered IDs including
the tail. Compare full original-width pipeline with freshly bound
width-three inclusion + proof + fresh check + wide fallback; retain
narrow only if the measured savings justify it. Adverse or unsolved
IDs must receive the original width-eight fallback or remain open.

## Cover and scan authorization (before production)

The repeated calibration passes: the smaller labeled support control,
1,200 band controls, exhaustive native/Python bounds through order four,
520 positive C13 translates and their mutations, and the two signs of
the six-vertex exact-degree width-three test. The complete census took
41.57 CPU-s and the separate exact cover binder 61.93 CPU-s. They agree
on 132,986 canonical projections and 832,295 lifts, with 41 first
branches including two empty. The raw 362,014 projection counter is
before orbit reduction and is not the denominator.

| Band | Projections | Lifts | Hard projections / lifts | Terminal IDs | Scan CPU-s | Native / unchanged Python replay CPU-s |
|---|---:|---:|---:|---:|---:|---:|
| Front | 1,856 | 15,184 | 275 / 654 | 14 | 4.39 | 2.29 / 5.39 |
| Interior | 1,856 | 11,493 | 117 / 205 | 0 | 1.70 | 0.98 / 2.71 |
| Tail | 1,857 | 8,736 | 74 / 116 | 1 | 1.57 | 0.76 / 1.95 |

Hard lifts lack any single-window witness and go to fusion. Per-row hard
maxima are 9, 6, 6. The 15 terminal IDs are in 10 projections in three
branches, at most three per projection. This concentration prevents a
reliable whole-queue price from these sample frequencies. Measure the
actual queue before any proof production; the 600 CPU-s limit is not
relaxed, and the cover scan is not itself exclusion.

Maximizing the projection/lift extrapolations separately over the three
bands gives 315 CPU-s native scan and 387 CPU-s unchanged ordered
replay, total 702 CPU-s (price, not bound). Use eight contiguous shards
of at most 16,624 projections, each scanning then replaying, 110 wall
and CPU-s per stage, plus 8 s grace. Split/merge CPU caps 8 and 22 give
at most `8*(110+110+16)+30 = 1,918` s. With both copies of cover and
receipts, even using the largest sampled per-row receipt, retention
estimate <125 MB before proofs. Stop at the exact merged queue.

## Exact queue and proof authorization (before production)

All eight scans and eight unchanged ordered replays passed in 142.37
and 214.19 CPU-s, respectively. Exact merge took 3.89 CPU-s and left
85 terminal IDs over 73 projections. The required >100 stop did not
fire, but we still sampled 16 exact queue ordinals including 0 and 84
before committing to either proof route. The positive and negative
six-site route controls reproduced SAT (with wide fallback) and
checked UNSAT in both paths; the fresh rebind and stride controls pass.

| Same 16 IDs | Checked | CPU-s | Peak RSS | Retained bytes |
|---|---:|---:|---:|---:|
| Wide-only, including byte regeneration and check | 16/16 | 20.31 | 177,288 KiB | 17,735,235 |
| Width three, new original references + inclusion + two checks | 16/16 | 12.99 | 40,876 KiB | 18,575,264 |
| Additional separate fresh inclusion and check for narrow | 16/16 | 5.63 | 40,976 KiB | <10 KiB additional |

With the additional independent reconstruction/recheck, width three
is 8.3% cheaper on this sample and peak RSS is about 4.3× lower. The
~5% extra disk is acceptable here. No sample fallback was needed; the
same 16 wide-only measurements price a fallback at ~1.27 CPU-s/ID.
Extrapolation is ~99 CPU-s with no fallback, or ~207 CPU-s generously
adding the full wide-only route for all 85 IDs (not a bound on hard
IDs). Production is four strided pairs: proof routes from the exact
85-ID list (43 wall/CPU-s each), then fresh binds reading the merged
receipt directly (34 wall/CPU-s each), four slots. Each unsuccessful
weak attempt has original width-eight solve/check and fresh written
CNF rebind; open if all applicable checks cannot be finished. The
proof/rebind worker caps, extraction, comparisons and route controls
including kill grace where relevant total 576 s. Keep the 1.25 GiB
cap, per-file limit 1.25 MiB, and 210 MiB per shard; projected data
<250 MB with no fallback. No other core is scanned.

## Terminal result — pending critic

**Hand + enum + cert:** exclude **core 8 only** under the stated
premises. Independent cover and ordered receipt bind every projection
and lift. The exact dispositions of all 832,295 lifts are:

| Disposition | Lifts |
|---|---:|
| Projection-wide graph witness | 612,437 |
| Later individual-window graph witness | 199,268 |
| Fused contradiction | 18,825 |
| Marked incompatibility | 1,680 |
| Bound width-three CNF with checked CakeLRAT | 85 |

The four fresh proof replays cover 22/21/21/21 disjoint IDs and agree
with the ordered merged receipt in `audit.queue.8.log`. Each checked
weaker CNF has the same edge and counter variable meanings as its own
fresh original reference, and its clauses were independently rebuilt
and checked for literal inclusion. Every proof passed both the route
check and the separate fresh recheck. No width-eight fallbacks and no
roster cuts enter the closure. Wide original references are retained,
but the 85 production proofs are **not** proofs on those wider inputs.
Production routes consumed 64.50 CPU-s and the separate fresh binds
33.47 CPU-s. The main path took **563.89 CPU-s = 0.15664 core-h**;
all 51 workers including controls and comparative pricing took
**628.07 CPU-s = 0.17446 core-h**. Retention was ~236 MB logical
before manifest; peak eight slots, no active, stopped or detached jobs.
If accepted, five mixed cores remain: 1, 6, 9, 15, 18. This does not
close `(2,32)` or resolve rigidity or `R(3,10)`.

### Independent replay

From `scratch/E/r15_shared`, use `sha256sum -c --quiet freeze.8.sha256`.
With `L=../../../ralph/lanes/E`, `W=$PWD`, and `A` an **absolute** audit
directory owned by the replayer (e.g. under `scratch/critic/`), the
following binds the roster and independently replays all eight original
ordered receipts, then reconstructs the 85 narrow proofs' CNFs and
checks their proofs again. Keep the frozen source tree unchanged.

```sh
run() { nice -n 5 timeout -k 8s "$1" bash "$L/limited.sh" "$2" "${@:3}"; }
key=$(sed -n '9p' ../r5_saturated/e11.g6)
run 390s 180 python3 -B "$L/bind_shared74.py" cover.8.jsonl --key "$key" --branches pilot.8.branches.tsv
for shard in {00..07}; do
    run 110s 110 python3 -B "$L/order_shared74.py" replay "scan.8/cover.$shard.jsonl" "scan.8/cover.$shard.receipt.jsonl" || exit
done
run 32s 22 python3 -B "$L/order_shared74.py" merge cover.8.jsonl scan.8 8 "$A/receipt.8.jsonl"
cmp "$A/receipt.8.jsonl" receipt.8.jsonl || exit
for offset in {0..3}; do
    mkdir "$A/proof.$offset"
    find "$W/proof.8.$offset" -maxdepth 1 -type f \( -name '*.cnf' -o -name '*.lrat' -o -name '*.replay.log' \) \
        -exec cp -l -t "$A/proof.$offset" -- {} +
    run 34s 34 python3 -B "$L/price_width74.py" rebind cover.8.jsonl "$A/receipt.8.jsonl" "$A/proof.$offset" --offset "$offset" --stride 4 || exit
done
```
