# Lane E state — round 8 complete

2026-11-22; allocation and hard working ceiling 16 cores. No candidate
or Ramsey verdict. All symmetry work uses all graphs, not MTF.

## Jobs

No live lane E solver/checker and no detached workers. The following
foreground batches in `scratch/E/r8_shared` are collected. The
`jobs.*.tsv` files bind timeout wrappers to exact slot/log.

| Wrapper PID(s) | Command (all nice 5 and 16 GiB max) | Start / deadline | Cores, logs |
|---|---|---|---|
| 2010706, 2010712, 2010718, 2010726, 2010730, 2010734, 2010738, 2010744, 2010747 | `batch_shared74.py cover.2.jsonl scan.2.graphfirst.jsonl proof.2 --offset 0..8 --stride 9`, CPU 850 s/wall 1500 s, per-solver CPU 15 s/wall 40 s | 00:45:48 / stopped intentionally 00:50:39 | 9; `batch.2.{0..8}.log`, `stop.batch.2.log` |
| 2010753, 2010761, 2010767, 2010775, 2010782, 2010792, 2010797 | shard `replay_shared74.py COVER TRACE`, CPU 150 s/wall 300 s | 00:45:48 / finished before 00:46:49 | 7; `replay.2.{00..06}.log` |
| see `jobs.scan.tsv` | septuple exact scans graph-only and graph-first, plus independent cover bind | 00:43:00 / finished before 00:45:30 | 15; `parts.2/*.log`, `bind.cover.2.log` |
| 2254155, 2254157, 2254164, 2254170, 2254174, 2254181, 2254187, 2254194, 2254198, 2254205, 2254209, 2254218 | `batch_shared74.py cover.2.jsonl todo.final.2.jsonl proof.final.2 --offset 0..11 --stride 12`, CPU 125 s/wall 360 s; checked proofs as above | 00:51:59 / finished before 00:53:59 | 12; `batch.final.2.{0..11}.log` |
| 2130508, 2254294 | fused propagation and deterministic replay, CPU 100 s/wall 160 s | 00:49:13 / 00:49:43; 00:51:59 / 00:52:29 | 1 per phase; `fuse.2.log`, `fuse.2.replay.log` |
| 2355846, 2355851, 2355858, 2355860, 2355866, 2355877, 2355895, 2355902, 2355910, 2355914, 2355926, 2355942 | `bind_shared74.py cover.2.jsonl --trace rebind.final.2/trace.SHARD.jsonl --proofs rebind.final.2/proofs.SHARD`, CPU 125 s/wall 360 s | 00:54:00 / finished before 00:55:51 | 12; `rebind.final.2.{00..11}.log` |

## Results / claims for H and critic

| Claim | Label | Evidence | Core-hours |
|---|---|---|---:|
| Prior profile A, mixed cores `G?Beto` and `G?bBro` unchanged and rehashed | inherited scoped hand + enum + cert | `m11.md`, `shared74.md`; `scratch/E/r8_shared/prior.freeze.log` | — |
| Mixed core **`` G?bF`w `` only** excluded at `(2,32,t=4,δ(W)≥2,e(W)=11)` with shared E-021 e74 premise and universal `δ(G)≥5`. Independent cover replay: 49,330 projections / 556,561 lifts. All 932 residual fresh CNFs byte-match and CakeLRAT checks pass. | hand + enum + cert, pending critic | `shared74_round8.md`, `scratch/E/r8_shared/{bind.cover.2.log,compare.2.log,fuse.2.replay.log,rebind.final.2.log,freeze.final.2.sha256}` | ~0.55 terminal work incl. graph-only comparison; ~0.24 estimated for stopped broad batch |
| Fused propagation of forced/forbidden edges across four roles with exact full fixed-degree rows. Exact queue 40,880 (graph-only) → 5,488 (marked) → 932 (fused); fusion pass 28.86 CPU-s. Exhaustive smaller all-solutions check (67 feasible controls, 12 negatives). | hand + enum, not standalone LRAT | `fuse_shared74.py`, `shared74_round8.md`, `scratch/E/r8_shared/{fuse.2.log,order.spread.2.log}` | included above |

## Next steps

- H/critic: audit `shared74_round8.md`, especially the fused `L⊆F*⊆U`
  invariant and exact residual identity. `freeze.final.2.sha256` is
  the final bundle; `proof.2/` is a stopped pilot, not the claim.
- 16 mixed cores remain. Pilot exact core 4 or 12 with learned size
  spread. Try graph-only → fusion → marked before production only if
  an exact matched sample preserves residual IDs and measures gain.
  Keep K=6/7/8, distinct omitted-group roles, and all-graph scope.
- Catalogue still 1,624/1,625; no reverse-edit repetition, no core-9/18
  capped scans. Inherited `(5,5)` certificate and other scopes unchanged.
