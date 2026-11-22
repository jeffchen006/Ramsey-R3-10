# Lane E state — round 12 complete

2026-11-22; timestamps below are machine time (CET, UTC+01:00).
Allocation 23; peak 11 capped foreground worker slots. No detached
jobs launched and no candidate submitted. Symmetry uses all graphs,
not MTF. Critic confirmed round-11 E-029/E-030/E-031; see `LOG.md`.

## Jobs

Exact per-worker PID, command, log, start and wall-cap offset (one
slot per row): `scratch/E/r12_shared/jobs.tsv`. Wrapper applies
`nice -n 5`, `timeout`, CPU limits and 16 GiB address space; grace
8 s. Proof workers also capped individual files at 2 MiB.

| Wrapper PIDs (only listed rows) | Logs / work | Peak slots | Start / latest possible finish (CET) |
|---|---|---:|---|
| 2741845–2780110 | `calibrate.*`, `census.16`, `bind.cover.16`, `sample.16`, `bind.pilot.16`, `pilot.16.*` | 5 | 06:03:50–06:05:13 / 06:11:18 |
| 2796667–2841286 | `split.16`, `parts.16/*.scan`, `merge.16` | 8 | 06:05:49–06:07:34 / 06:12:32 |
| 2850367–2852604 | `replay.16`, `reprice.{proof,rebind}.16` | 2 | 06:08:00–06:08:09 / 06:33:08 |
| 2873982–2898603 | `calibrate.roster`, `proof.16.*`, `rebind.proof.16`, `bind.branches.16`, `roster.*` | 10 plus replay | 06:08:52–06:09:57 / 06:13:25 |
| 2923684–2923798 | `calibrate.roster.v2`, `prefilter.*` | 4 plus replay | 06:10:56 / 06:12:44 |

Independent whole receipt replay (foreground PID 2850370, wrapper
2850367) finished at 06:14:24. All 52 round-12 wrappers collected;
no live or stopped workers.

## Results and claims (for H / critic)

Scope of core 16: `(p,f,t)=(2,32,4)`, `δ(W)≥2`, `e(W)=11`,
mixed `(10,10,11,11)`, universal `δ(G)≥5`, and E-021's all-graph
sole-missing `e=74` class premise; all four omitted-group roles and
`K=6,7,8` kept. Core numbers zero-based in `scratch/E/r5_saturated/e11.g6`.

| Item | Label | Evidence / cost |
|---|---|---|
| Core 16 ``GCR`v?`` excluded under the stated scope: all 25 first branches independently bound (2 empty); 98,448 projections / 834,106 lifts and 107 freshly regenerated original CNFs + CakeLRATs; full ordered receipt replay passed. | hand + enum + cert, pending critic | `shared74_round12.md`, `scratch/E/r12_shared/freeze.16.sha256`; 0.31636 core-h terminal |
| Roster cut filters 31/107 final core-16 IDs and 6/42 final IDs in four archived heavy-core samples; no production use. On 581 fused-open sample IDs, 5.15 vs 1.96 CPU-s for marking if used as prefilter. | hand + enum pilot | `shared74_round12.md`, `scratch/E/r12_shared/freeze.roster.sha256`; ≈0.005 core-h across pilots |

## Handoff

- Ask critic to independently replay core 16. Exact queue hit
  the initial 100-ID stop (107); a dispersed
  12-ID tail reprice checked before production. The 2/0/0 pilot
  residuals are not the terminal counts. Scratch ≈237 MiB logical.
- Price 17 next; eight mixed cores would remain if 16 is accepted:
  1,5,6,8,9,15,17,18. Preserve all first-branch counts and stratified
  pricing. No new full scans on heavy cores 9/18. Try the roster only
  after marking on final IDs; it slowed the marked phase as a prefilter.
- No change to other f32 profiles, (5,5) already certified, and no
  full `(2,32)` closure, rigidity or Ramsey verdict.
