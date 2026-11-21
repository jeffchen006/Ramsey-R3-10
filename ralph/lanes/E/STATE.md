# Lane E state — round 7

2026-11-22; allocation 19 cores, batch ceiling 16. All symmetry
claims concern all graphs, not MTF. No candidate; no Ramsey verdict.
Main scope remains `(p,f,t)=(2,32,4), δ(W)≥2`.

## Jobs

No live lane-E solver or checker, no detached jobs this round.
Foreground production ran in `scratch/E/r7_shared`.

| Wrapper PID(s) | Command | Start, end | Cores, logs |
|---|---|---|---|
| `617493`–`617496` | `prove_shared74.sh cover.3.jsonl todo.3.tsv proof.3 OFFSET 4`, nice 5, wall 180 s, CPU/RAM limits applied | 00:10:16, all collected before 00:12:06 | 4; `proof.3/worker.{0,1,2,3}.log` |
| `713723` (Python `713734`) | `bind_shared74.py cover.3.jsonl --trace scan.3.final.jsonl --proofs proof.3`, wall 210 s/CPU 150 s | 00:12:24, finished after 109 wall-s | 1; `bind.proof.3.log` |

All round-6 detached workers `2053353`–`2053368` had already ended;
round-7 checked prior bundles by SHA, not a new proof campaign.

## Results / claims for H and critic

| Claim | Label | Evidence | Core-hours |
|---|---|---|---:|
| At `(2,32,t=4,δ(W)≥2,e(W)=11)`, profile `(10,10,11,11)`, **`W=G?bBro` only** excluded under inherited universal degree and E-021 census premises. 7,046 projections, 36,612 full support orbits; 4,879 projection witnesses cover 23,294 lifts, 12,939 incompatible lifts, 322 other graph witnesses, 57 fresh-CNF checked LRATs. All scope/receipt identities independently replay. | hand + enum + cert, pending critic | `ralph/lanes/E/shared74.md`, `scratch/E/r7_shared/{bind.cover.3.log,replay.3.final.log,bind.proof.3.log,freeze.3.sha256}` | ~0.07 final census, proof, replay |
| Shared-window compatibility: degree-seven extras form a clique of size ≤2; `K=6,7,8` and at least `|S_i|+|S_j|−K` fixed-W high roots must map to each other. Compare exact marked-root incidence patterns. On core 3: 785→57 proof residuals, 16.28 CPU-s with graph-first vs 71.32 isom-first. C13 controls 520 positive/520 negative. | hand conditional on E-021 + measured enum filter | `ralph/lanes/E/shared74.md`; `scratch/E/r7_shared/{scan.3.unfiltered.log,scan.3.graphfirst.log,marked.final.pilot.log}` | ~0.01 matched timings |
| Prior E-019 profile A and E-020 core `G?Beto` unchanged, manifests rehash. E-017 e12 and mixed-status f=28 frozen. Prior `(5,5)` cert remains unchanged. | inherited statuses | `m11.md`, `cubic32.md`, `f28_cover.md`, `slim5.md`; `scratch/E/r7_shared/prior.freeze.log` | — |

## Next steps

- H/critic: audit `shared74.md` at exactly the `G?bBro` scope, plus
  the necessary cut. K=8 must be included when both big groups
  have six singletons. Only the `*.final.*` receipts and
  `freeze.3.sha256` are the final proof bundle. Early `scan.3.jsonl`
  omitted K=8; the corrected scan moved 12 incompatibilities to
  graph witnesses without changing the set of 57 residual LRATs.
- Remaining mixed cores: 17. Use `--graph-first`; it preserves all
  residual IDs and avoids computing canonical patterns for graph
  propagation rejects. First estimate per-core census and proof
  cost from fresh matched samples; next small likely cores 2, 4,
  or 12. Do not rerun the old core-9/core-18 capped sweeps. 120-row
  sample of each with new filter leaves 35/987 and 8/774 lifts before
  graph propagation; not a whole-core result. No mixed closure for
  any other core besides `G?Beto` and `G?bBro`.
- The reverse e74 catalogue remains 1,624/1,625, max listed d7
  multiplicity 4. No closure at m9, m10, m8 deficit two, or W
  leaves/isolates/t=2,3. Do not repeat unchanged old edit moves.
