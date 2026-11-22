# Lane E state — round 11 complete

2026-11-22, CET. Allocation 22; foreground peak nine worker slots,
no detached jobs. No candidate or Ramsey verdict. Symmetry work uses
all graphs, not MTF. Round-10 cores 12/14/10/11 confirmed by critic.

## Jobs

No live, stopped or detached lane E jobs at collection. Prior wrappers
absent; all 61 listed round-11 wrappers absent after completion. Full
per-process table (PID, start, wall deadline offset, log, exact command,
one worker slot/row) is `scratch/E/r11_shared/jobs.tsv`. `r11_worker.sh`
uses `nice -n 5`, `timeout`, CPU caps, and 16 GiB per worker.

| Recorded wrapper PIDs (listed rows only) | Phase / logs | Peak slots | Start range / last possible wall end (CET) |
|---|---|---:|---|
| 820801–843877 | Core census, independent cover, stratified sampling and calibration, `census.*`, `bind.*`, `pilot.*`, `calibrate.*` logs | 9 | 04:42:05–04:43:09 / 04:47:58 |
| 857829–869946 | Two waves, 16 full cover shard scans in `parts.{7,13}/` | 8 | 04:43:53–04:44:22 / 04:51:20 |
| 896724–919858 | Whole receipt replays, 40 proofs and fresh binding, `replay.*`, `proof.*`, `rebind.proof.*` logs | 8 | 04:45:33–04:46:14 / 05:02:42 |
| 970667–1085315 | d3 calibration, census and certificate replay, archived degree-floor pilot, `d3.*.log` | 4 | 04:47:51–04:51:48 / 04:58:04 |

## Results and claims (for H / critic)

First two rows: `(p,f,t)=(2,32,4)`, `δ(W)≥2`, `e(W)=11`,
`(10,10,11,11)`, universal `δ(G)≥5` and all-graph E-021 sole-missing
e74 premise. Each row excludes that core only; indices zero-based in
`scratch/E/r5_saturated/e11.g6`. Complete independent covers and ordered
replays; every residual proof matched to a fresh original four-window
formula, no optional fusion or rooted conditions in those formulas.

| Claim | Label | Evidence | Core-hours |
|---|---|---|---:|
| Core 7 ``G?`vBo`` excluded: 50,065 projections / 278,029 lifts; 11 terminal LRATs. | hand + enum + cert, pending | `shared74_round11.md`, `scratch/E/r11_shared/freeze.7.sha256` | 0.06437 |
| Core 13 `G?qrf?` excluded: 90,117 projections / 547,674 lifts; 29 terminal LRATs. | hand + enum + cert, pending | `shared74_round11.md`, `scratch/E/r11_shared/freeze.13.sha256` | 0.13450 |
| Every `(3,8;26)` graph with `e≤74` has `δ≥4`; 191 published order-22 parent CNFs, all regenerated and CakeLRAT-checked. Does not use E-021. Exact 74-edge independent census also has zero d3 lifts. | hand + cert, pending; separate enum | `window74_d3.md`, `scratch/E/r11_shared/freeze.d3.sha256` | 0.03217 |
| Enforcing the new floor in fusion adds no edges and rejects 0/42 final archived heavy-core pilot IDs. | enum | `window74_d3.md`, `scratch/E/r11_shared/d3.floor.*.log` | pilot <0.001 |

## Next steps

- H/critic: audit proof scopes and artefacts above. Run time: 715.93
  terminal CPU-s for the two exclusions, 115.82 CPU-s for exact d3.
- Nine mixed cores remain if accepted: 1,5,6,8,9,15,16,17,18. Price
  16 next (round-10 front two residual IDs, tail zero), then 17;
  sample all canonical first branches at both ends and interior, not
  only the apparently cheap end. Do not infer proof counts from empty
  pilot bands. Use the uncached scanner; no new full scan on 9/18.
- The new d3 result is a structural property, not recovery of the
  1,625th e74 class. No change to other profiles, `(5,5)` already
  certified. No full `(2,32)` closure, rigidity or Ramsey verdict.
