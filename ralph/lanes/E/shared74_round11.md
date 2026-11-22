# Mixed saturated f=32: round 11

Scope throughout: `(p,f,t)=(2,32,4)`, `δ(W)≥2`, `e(W)=11`, mixed
profile `(10,10,11,11)`, universal `δ(G)≥5`, and inherited E-021
all-graph sole-missing e74-class premise. No MTF assumption. Core numbers
are zero-based in `scratch/E/r5_saturated/e11.g6`.

## Preflight

Only cores 7 and 13 are targeted for exact work. Round 10 used up to 48
projections per canonical first branch at each end: core 7 had
9,118/6,437 lifts in 1,590 projections at each end (2.637/2.978 scanner
CPU-s); core 13 had 8,978/7,354 lifts in 1,324 projections at each end
(3.880/3.034 CPU-s). Both had zero sample survivors, which does not
imply zero whole-source survivors. Round-10 exact censuses of 9,850 to
27,093 projections cost 7.79–15.65 CPU-s; independent checks cost
5.14–27.45 CPU-s. Preflight budgets per new core: 90 census CPU-s and
100 independent-check CPU-s, with timeouts; no whole scan until exact
lift counts and three-band pilot measurements. Include every first
branch, explicitly accounting for empty ones, and check all pilot
residual proofs before pricing a whole queue where the pilot is nonempty.

## Whole-cover price (recorded before production)

Each nonempty canonical first branch contributed up to 48 distinct
projections from each of its front, interior and tail. Short branches
were partitioned into thirds without duplication. Two branches of core
7 have no lifts; core 13 has no empty branches. Counts were taken from
the exact covers, with a per-branch table and byte-bound global IDs.

| Core | Branches (nonempty/total) | Projections | Lifts | Front/interior/tail projections | Front/interior/tail lifts | Scan CPU-s per band (user+sys) |
|---|---:|---:|---:|---|---|---|
| 7 | 34/36 | 50,065 | 278,029 | 1,562 / 1,563 / 1,564 | 9,046 / 9,765 / 6,304 | 3.21 / 3.27 / 3.11 |
| 13 | 29/29 | 90,117 | 547,674 | 1,248 / 1,251 / 1,252 | 8,469 / 6,883 / 6,856 | 4.09 / 1.90 / 2.40 |

All six bands had zero open IDs. Max-band CPU rates per projection
and per lift (take the larger full-cover estimate) price the scans at
about 140 and 300 CPU-s; allow another 210 and 450 CPU-s for replay.
Round 10's full covers left 1–2 IDs even on zero-ID samples; the
16-ID checked control from core 12 also prices the terminal pipeline.
Reserve up to 100 original-CNF proofs/core at about 2–3 CPU-s/ID for
production, check and fresh rebind, with individual proof caps; stop
and reprice if the whole-receipt counts exceed 100. Budget under 1,850
CPU-s for the combined terminal tranche, including census and binding.

## Exact results

**Hand + enum + cert, pending critic.** These exclusions cover only the
indicated core and the scope at the top of this note. All four omitted
group roles are retained and the marked test allows `K=6,7,8`.

| Core | Projections | Lifts | Projection-wide graph deaths | Other graph deaths | Fused deaths | Marked deaths | Original CNF/LRATs | Terminal CPU-s |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 7 ``G?`vBo`` | 50,065 | 278,029 | 183,586 | 85,829 | 7,680 | 923 | 11 | 231.72 |
| 13 `G?qrf?` | 90,117 | 547,674 | 383,552 | 146,882 | 16,326 | 885 | 29 | 484.21 |
| **Total** | **140,182** | **825,703** | **567,138** | **232,711** | **24,006** | **1,808** | **40** | **715.93** |

The independent support binder matched every projection and lift,
including the two empty first branches of core 7. `order_shared74.py`
merged contiguous shards against the bytewise source and replayed the
full ordered receipt. All 40 terminal IDs came directly from complete
receipts despite zero sample IDs. `bind_shared74.py` matches the exact
ID set to the proof directory, regenerates the original four-window
CNFs byte-for-byte, and runs CakeLRAT. The SAT formulas did not require
the graph, fusion or marked filters; those receipts are hand + enum.
Nine mixed cores remain if accepted. No full `(2,32)` closure.

From `scratch/E/r11_shared`, replay under worker limits (set `core` to
`7` or `13` and `key` as in the table; log names must be unused):

```sh
L=../../../ralph/lanes/E
sha256sum -c "freeze.$core.sha256"
bash "$L/r11_worker.sh" 300s 100 "audit.cover.$core.log" python3 -B "$L/bind_shared74.py" "cover.$core.jsonl" --key "$key"
bash "$L/r11_worker.sh" 1020s 520 "audit.receipt.$core.log" python3 -B "$L/order_shared74.py" replay "cover.$core.jsonl" "receipt.$core.jsonl"
bash "$L/r11_worker.sh" 420s 130 "audit.proofs.$core.log" python3 -B "$L/bind_shared74.py" "cover.$core.jsonl" --trace "receipt.$core.jsonl" --proofs "proof.$core"
```
