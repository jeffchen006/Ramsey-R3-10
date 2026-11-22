# Mixed saturated f=32: core 4

**Hand + enum + cert, pending critic review.** Exclude only core index 4,
``G?`fbo``, of `scratch/E/r5_saturated/e11.g6`. The scope is
`(p,f,t)=(2,32,4)`, `δ(W)≥2`, `e(W)=11`, incidence profile
`(10,10,11,11)`, universal `δ(G)≥5`, and the inherited E-021 all-graph
sole-missing e74-class premise. This is not an MTF reduction, a full
profile closure, or a claim about the missing class's identity or histogram.

The support census is unchanged from `m11.md`. The two tests in the
order comparison are the marked overlap filter of `shared74.md` and
the full-fixed-set propagation of `shared74_round8.md`. The marked
filter considers all possible common degree-seven counts `K=6,7,8`;
the ordered roles of the four omitted groups are not identified.
After a single-window graph test, both additional filters read the
same original support pins: the output of fusion is not used to
strengthen the marked test. Final acceptance is their intersection,
so order changes work, not the surviving identities.

## Matched pilot

The samples traverse every canonical first-support branch, taking up
to 160 viable projections per branch in ascending order and up to 100
in descending second/third-support order. They are deterministic and
may overlap, not uniform samples. Every sample row was subsequently
byte-bound into the exact cover. Both orders' receipt streams were
replayed and their ordered residual IDs were identical (empty).

| Sample | Projections / lifts | Graph-only open | Graph → marked → fusion CPU-s | Graph → fusion → marked CPU-s |
|---|---:|---:|---:|---:|
| Ascending | 2,086 / 15,188 | 355 | 4.927 | 4.313 |
| Descending | 1,338 / 11,213 | 412 | 4.375 | 5.610 |

Graph-only costs 2.715 and 3.198 CPU-s (scanner process CPU). To
measure avoided proof work even though both final queues were empty,
24 rank-spread graph-only IDs from the ascending sample were encoded,
solved and CakeLRAT checked: 24/24, 16.06 aggregate CPU-s; regenerating
those CNFs and rechecking cost another 15.01 CPU-s. The pilot supports
using the filters, not a substantial speed advantage of either order.
Marked-first was slightly faster across the two samples in sum and
was used in the exact run. Prelaunch estimates are in `estimate.4.txt`.

## Exact cover and evidence

| Final classification | Count |
|---|---:|
| Independent projected support orbits | 17,840 |
| Independent full support orbits | 110,716 |
| Lifts refuted by 13,862 projection-wide graph witnesses | 73,454 |
| Lifts refuted by another single-window graph witness | 34,743 |
| Marked incompatibilities, replayed using explicit root mappings | 2,505 |
| Remaining lifts: fused contradiction **and** checked four-window LRAT | 14 |
| Open | 0 |

`bind_shared74.py` independently regenerates the normalized quadruple
cover and compares identities, not just cardinalities. Six contiguous
scan shards are joined against the byte-identical original cover;
the full merged receipt replay checks every projection/lift in order.
For each of the 14 fusion tags, the SAT input is the original anchored
four-window CNF, not a CNF strengthened with fused implications or by
marked isomorphism. Fresh generation matches all 14 DIMACS files byte
for byte, and all 14 CakeLRAT checks pass. The proof-ID set matches the
ordered pre-fusion queue exactly. Thus the final 14 exclusions do not
depend on trusting fused propagation; the graph and marked stages still
have hand + enum status. No capped instance or unexplained ID. Tamper
checks reject both a wrong receipt projection ID and wrong DIMACS bytes.

Terminal census, independent cover bind, scan/merge, full receipt
replay, and both proof passes total 88.55 CPU-s (0.02460 core-hours).
No other mixed core was scanned in this round; 15 mixed cores remain.

## Replay

From `scratch/E/r9_shared`, run these under `limited.sh` with wall and
CPU caps. `freeze.4.sha256` binds the inputs, scripts, final receipts,
and every proof file. See `measured.4.log` for the final ID check.

```sh
L=../../../ralph/lanes/E
sha256sum -c freeze.4.sha256
python3 -B "$L/bind_shared74.py" cover.4.jsonl --key 'G?`fbo'
python3 -B "$L/order_shared74.py" replay cover.4.jsonl receipt.4.jsonl
python3 -B "$L/bind_shared74.py" cover.4.jsonl --trace todo.pre-fusion.4.jsonl --proofs proof.4
```
