# Lane E state — round 9 complete

2026-11-22. Round 9 allocation: 22 cores; foreground peak 7 worker
slots, with independent stages and flow-counter checks. No candidate
or Ramsey verdict. Symmetry work uses all graphs, not MTF.

## Jobs

No live or detached lane E jobs. The round-8 wrappers were absent
at collection. All listed round-9 jobs finished. Logs are relative
to `scratch/E/r9_shared`; commands use `nice -n 5`, `timeout`, and
`limited.sh` (16 GiB). Times are CET, 2026-11-22.

| Wrapper PID(s) | Command or phase | Slots | Start / wall deadline | Logs |
|---|---|---:|---|---|
| 198660, 201065, 201890, 217349–217351, 254382, 255241–255243 | `order_shared74.py spread` and matched scans; CPU 65–70 s/wall 120–150 s | ≤3 | 01:49:22–01:50:40 / by 01:53:10 | `spread.tail.4.log`, `*.{spread,broad,tail}.4.log` |
| 254444–254446, 254448, 297565 | 24 graph-only pilot CaDiCaL/CakeLRAT then fresh bind; CPU 50–65 s/wall 140–220 s | 4 then 1 | 01:50:39 / 01:54:19; 01:51:17 / 01:53:37 | `proof.pilot.4.*.log`, `rebind.pilot.4.log` |
| 297556, 297557, 297558, 297560, 297562 | `m11_support.py census --core 4 --profile 1`, matched pilot receipt replays; CPU/wall 140/350 and 55/100 s | 5 | 01:51:17 / 01:57:07 and 01:52:57 | `census.4.log`, `replay.*.*.4.log` |
| 326366–326372 | six `order_shared74.py scan marked-first` shards plus independent exact `bind_shared74.py --key`; CPU/wall 65/140 and 100/200 s | 7 | 01:51:58 / 01:54:18 and 01:55:18 | `parts.4/scan.*.log`, `bind.cover.4.log` |
| 350778–350779, 350781–350783, 353201 | full receipt replay, four proof slots, fresh CNF/CakeLRAT replay; CPU/wall 95/180, 60/140, 60/150 s | 5, then 2 | 01:52:36 / 01:55:36 and 01:54:56; 01:52:40 / 01:55:10 | `replay.4.log`, `proof.4.*.log`, `rebind.proof.4.log` |

## Results / claims for H and critic

| Claim | Label | Evidence | Core-hours |
|---|---|---|---:|
| Mixed core **``G?`fbo`` only** excluded at `(2,32,t=4,δ(W)≥2,e(W)=11)`, profile `(10,10,11,11)`, under universal `δ(G)≥5` and inherited E-021 all-graph e74 premise. Independent exact cover 17,840 projections / 110,716 lifts; graph-only 2,519 → marked 14 → fused 0. All 14 independently have byte-regenerated CNF/CakeLRATs, so the claim need not rely on fusion for those 14. | hand + enum + cert, pending critic | `shared74_round9.md`, `scratch/E/r9_shared/{freeze.4.sha256,bind.cover.4.log,replay.4.log,rebind.proof.4.log,measured.4.log}` | 0.02460 terminal |
| Both orders leave identical empty residual IDs on front and rear samples across 14 first-support branches. Marked-first 9.302 vs fused-first 9.923 scanner CPU-s in sum, with opposite winner by sample; 24/24 graph-only pilot proofs measured at 0.669 CPU-s per ID plus 0.625 for fresh binding. No cross-core speed claim. | enum / estimate | `order_shared74.py`, `shared74_round9.md`, `scratch/E/r9_shared/estimate.4.txt` | pilot, excluded from terminal cost |
| Prior mixed cores `G?Beto`, `G?bBro`, and ``G?bF`w`` unchanged. Round 8 scoped result confirmed. | inherited hand + enum + cert | `m11.md`, `shared74.md`, `shared74_round8.md`, `ralph/critic/round_008.md` | — |

## Next steps

- H/critic: audit the scoped core-4 closure and proof-ID binding.
  `freeze.4.sha256` is the final bundle. Pilot proofs are not closure
  evidence and `proof.4/` is exactly the 14 formerly fused-only IDs.
- Fifteen mixed cores remain. Fresh pilot core 12 if assigned; reuse
  `order_shared74.py` and sample both ends of each branch. Do not assume
  either order wins or that the final proof queue will be empty.
- The 1,624/1,625 catalogue is unchanged; no reverse-edit repetition or
  core-9/18 capped scans. `(5,5)` already certified; other open scopes
  unchanged. This does not close full `(2,32)` or prove rigidity.
