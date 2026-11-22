# Mixed saturated f=32: core 2 and fused propagation

**Hand + enum + cert, pending critic review.** This core only is
excluded. All 932 residuals have a regenerated, byte-bound CNF and
checked CakeLRAT; `rebind.final.2.log` records the full count.

The exact scope is `(p,f,t)=(2,32,4)`, `δ(W)≥2`, `e(W)=11`,
profile `(10,10,11,11)`, and core **`` G?bF`w `` only** (index 2 of
`scratch/E/r5_saturated/e11.g6`). The reductions use universal
`δ(G)≥5` and the all-graph sole-missing e74 class premise E-021, as
in `m11.md` and `shared74.md`. No maximality assumption and no claim
about the missing class's identity or degree histogram. The four
windows retain their distinct omitted-group roles, considering
`K=6,7,8` simultaneously in the sense of `shared74.md`.

## Fusing window implications

Maintain lower and upper graphs on the full fixed set `F`. Start from
the common support pins: `W`, the W–attachment edges, and the only
possible remaining edges (across groups, avoiding triangles on W).
For a completion `F*`, the invariant is `L⊆F*⊆U`. In addition to
triangle freedom, each W vertex has exact fixed degree eight and
each attachment vertex has exact fixed degree seven. Thus a row with
target attained in `L` deletes its optional edges from `U`; a row
with target attained in `U` forces all eligible edges into `L`.
Rows with inconsistent degree bounds or a forced triangle are
impossible. A pair with a forced common neighbor is deleted from `U`.

For each omitted group `A_i`, restrict `L,U` to `H_i=F\A_i` and
run the existing 74-edge, alpha-at-most-seven window propagation.
Every forced edge has its eight-vertex witness and every removal is
reconstructed by `m11_prop.proof_check`. If a checked window step
adds a forced edge or deletes an eligible one, lift that implication
back into `F` in the same labels before visiting the next window.
This does not identify vertices in different windows or assume their
isomorphism. The window bound and the global degree rows are necessary
for every completion, so the invariant is preserved. The updates are
monotone; repeat only on change. Contradictions have hand + enum
status with replay, not LRAT status.

The six-vertex control enumerates all four feasible labelled graphs
for three omitted pairs with degree two, triangle freedom, and
alpha at most two in each retained window. Of 79 available-edge
perturbations with zero, one, or two removed edges, all 67 feasible
ones preserve every solution inside the returned bounds and all 12
infeasible ones are rejected. The 301-projection spread sample of
this core leaves 49 after marked isomorphism; fusion refutes 34 of
those (0.256 CPU-s). Its complete-run effect is stronger.

## Exact counts

| Stage | Count |
|---|---:|
| Primary projections | 49,330 |
| Full support orbits | 556,561 |
| 26,933 projected graph witnesses | 292,234 lifts |
| Other single-window graph witnesses | 223,447 |
| Graph-only remainder | 40,880 |
| Incompatible marked windows | 35,392 |
| Graph-first remainder | 5,488 |
| Fused degree/triangle/window contradictions | 27 / 120 / 4,409 |
| Final LRAT queue | 932 |

The support binder checks every key and lift identity; the seven
contiguous shards replay all graph and compatibility receipts using
explicit root mappings. The shard merger checks byte-identical cover
rows, and the matched comparison checks every receipt ID (and leaves
all graph witnesses unchanged). The fusion trace must contain exactly
one record for every old open ID, in the same order. The broader proof
batch was **stopped** after 1,207 checked proofs, not capped; 153
included in the new queue were reused, leaving 779 new proofs.

Graph-only and graph-first scans use 148.67 and 413.43 aggregate
CPU-s on the exact same cover. Fusing the 5,488 survivors costs
28.86 CPU-s and cuts the original graph-only LRAT queue by 43.9×;
this ratio is a queue reduction, not an end-to-end speedup.
For future work, apply fusion before the expensive marked test on
the spread sample: 294 graph-only survivors give 71 after fusion,
then the marked test returns the same 15 final identities as the
other order. Total ~3.11 CPU-s for this sample, versus ~3.27 in
the deployed order; no whole-core speed claim or reordering used
in the proof bundle. The measurement is in `order.spread.2.log`.

## Replay

All paths below are relative to `scratch/E/r8_shared`. Logs and timings:
`prior.freeze.log`, `estimate.2.txt`, `census.2.log`, `bind.cover.2.log`,
`merge.2.log`, `compare.2.log`, `replay.2.*.log`, `fuse.2.log`,
`fuse.2.replay.log`, `plan.final.2.log`, `batch.final.2.*.log`.
Use `limited.sh` with wall/CPU caps. `cover.2.jsonl` is the full exact
cover and `scan.2.graphfirst.jsonl` its graph/incompatibility trace.
`fuse.2.jsonl` binds the extra propagation receipts to the final queue.

```sh
L=../../../ralph/lanes/E
python3 -B "$L/bind_shared74.py" cover.2.jsonl --key 'G?bF`w'
python3 -B "$L/replay_shared74.py" cover.2.jsonl scan.2.graphfirst.jsonl
python3 -B "$L/fuse_shared74.py" cover.2.jsonl scan.2.graphfirst.jsonl --out replay.fused.jsonl
cmp fuse.2.jsonl replay.fused.jsonl
python3 -B "$L/bind_shared74.py" cover.2.jsonl --trace fuse.2.jsonl --proofs proof.final.2
```

For parallel proof replay, use `shared74_shards.py distribute-proofs`
then the same binder with the full cover and each disjoint subtrace
and file set separately. The native LRATs refute relaxed four-window
CNFs with exact attachment degrees and width-at-most-eight alpha
clauses; they need neither isomorphism nor fused unit clauses.
The complete replay is frozen in `freeze.final.2.sha256`.
