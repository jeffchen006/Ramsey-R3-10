# P4 proof package: no four distinct consecutive roots in R(6)

Status: all finite residual CNFs refuted with checked binary LRAT;
composite exclusion submitted for critic review (not Lean and not a
closure of R(6)). The hand reductions and SAT bridge are in
`proofs/codegree_six_paths.md`, `proofs/path_windows.md`, and
`proofs/path_four_factor.md`. The 191-class seed premise is D-G3 in
`notes/DEPENDENCIES.md`. H checked the projection in
`ralph/lanes/H/P4_SIDE_REVIEW.md`; A independently rebuilt the original
2,454-row catalogue in `ralph/lanes/A/P4_REPLAY.md`.

## Checked strata

| e(A) | Post-MTF rows | Required LRATs |
|---:|---:|---:|
| 81 | 234 | 234 unpinned |
| 80 | 503 | 503 unpinned |
| 79 | 450 | 450 unpinned |
| 78 | 148 | 888 pinned (6 per row) |
| 77 | 21 | 147 pinned (7 per row) |
| all | 1356 | 2222 |

The split by e(A) is exact in this cover; after the hand MTF filter all
lower edge strata are empty. The high proofs consist of 1,164 left-only
CNFs, six right-only CNFs, and 17 joined CNFs. For the low proofs the
full two-side CNF contains all triangle, regularity, MTF and codegree
rows, and the projections of alpha on both sides. It is only a
relaxation of the full Ramsey constraint, which suffices to refute it.
No LRAT in this package relies on a lazy cut or on P5.

## Replay from the pinned inputs

Use PySAT `1.9.dev17`, `opt/bin/cadical` `3.0.1`, and `opt/bin/cake_lpr`.
No solver invocation is needed to replay retained LRATs. Large files
belong in `scratch/C`; producer logs and certificate files live at
`scratch/C/p4proof-{high,low}*`. The actual proof data is about 811 MiB.
From the repository root:

```sh
sha256sum -c ralph/lanes/C/P4_INPUTS.sha256
(cd scratch/C; ulimit -v 16777216
 nice -n 5 timeout 180 python3 -B ../../ralph/lanes/C/verify_p4_index.py \
   p4_full.g6 p4_forced_full.g6 --high p4proof-high --low p4proof-low)
for part in high low; do
  for shard in 0 1 2 3; do
    bash ralph/lanes/C/replay_p4.sh "$part" "$shard"
  done
done
```

The independent index audit decodes graph6 itself, directly recomputes
the MTF filter, and computes orbit representatives by choosing a column
permutation and sorting the row words. It matches every proof hash, key
and file, not just counts. `scratch/C/p4-index.log` reports no missing
keys, and `scratch/C/p4-proof-index.tsv` has one row per LRAT. The replay
script regenerates each CNF, requires the exact `s VERIFIED UNSAT`
checker line (exit zero alone is insufficient), then compares the
recorded row/CNF/proof hashes byte-for-byte with the producer log.

The `PATH_INPUTS.sha256` and `PATH_REPLAY.md` files preserve the P4 and
P5 original joins and the P5 traces. Lane A independently matched the
1,156 P5 rows modulo reversal, including a reversed-input control and
deletion/mark corruptions, in `scratch/A/p5` and
`ralph/lanes/A/check_p5_cover.py`; the P4 package does not require P5.

## Calibration and cost

- C21: exact same eight feasible row keys and five excluded keys as
  the older solver run. Eight explicit witnesses pass the independent
  graph checker. Pinned proof control covers all cross shapes of the
  five infeasible rows; for the eight feasible rows at least one
  representative survives. Logs `p4_factor_control.log`,
  `p4_factor_independent_control.log`, `p4pinned-control.log`.
- Same spread 15-row large pilot: old cap 15/15; eager two-side formula
  refutes ten rows at 7,000 conflicts, and the proof-producing version
  refutes 14 at 4 seconds per solver call (29.00 CPU-s total).
  Pinning handles all six e77/e78 sample rows, with all 39 LRATs checked
  in 35.87 CPU-s. The more expensive mixed-row alternative generated
  over half a million clauses and hit the prototype wall budget; it
  was not scaled. Logs `p4_factor_sample.log`, `p4proof-pilot.log`,
  `p4pinned-pilot.log`, `p4mixed-test.log`.
- Full high and low proof production consumed 795.49 and 839.28 CPU-s,
  respectively, including initial checking, with no caps or unresolved
  CNFs. `p4_factor_corruption.log` records rejection of a deleted cover
  row and a truncated LRAT.
- All eight replay shards finished. All 2,222 regenerated CNF hashes
  and proof hashes matched, and all CakeLPR checks passed again in
  about 949 CPU-s (`scratch/C/p4replay-{0,1,2,3}.log`).

## Scope

J has maximum degree two and no triangles. Any component of order
at least four would contain four consecutive distinct roots, now
refuted by the assembled package. Therefore only isolated vertices,
isolated c6 edges, and three-root components remain in R(6). In
particular there are at most 26 c6 edges and 13 vertices of J-degree
two: a three-vertex component contributes two edges and one middle
vertex, a two-vertex component one edge, and an isolate none. The
three-root diagonal types 3, 4 and 5 remain separate, and this proves
nothing about isolated c6 pairs or other max-codegree cases.
