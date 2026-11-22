# Lane E state — round 15 complete

2026-11-22, CET. Allocation 32, actual peak eight slots. Core 5 accepted
by critic, archived in `LOG.md`. This round worked only on core 8.

## Jobs

No active, stopped, killed or detached jobs, zero cores. All 51
foreground capped wrappers exited 0. Exact PID, start, expected end,
command, slots and log: `scratch/E/r15_shared/{jobs,exits}.tsv`.

| Work | Peak slots | Start range (CET) | Latest allowed finish (CET) |
|---|---:|---|---|
| Controls, census, band pricing, independent full branch/cover bind | 5 | 10:23:26–10:26:41 | 10:32:57 |
| Eight production scans and unchanged ordered replays, merge | 8 | 10:27:49–10:28:55 | 10:30:27 |
| Exact queue and comparison of both proof routes | 2 | 10:28:37–10:31:04 | 10:31:36 |
| Width-three production, fresh rebind and final roster audit | 4 | 10:31:37–10:32:22 | 10:32:42 |

## Results and claims for H / critic

Zero-based core 8 `G?qbf_` from `scratch/E/r5_saturated/e11.g6`.
Scope: `(p,f,t)=(2,32,4)`, `δ(W)≥2`, `e(W)=11`, mixed
`(10,10,11,11)`, universal `δ(G)≥5`, E-021 all-graph sole-missing
`e=74` premise, all four omission roles and `K=6,7,8`. Not MTF-only.

| Item | Label | Evidence / cost |
|---|---|---|
| **Core 8 only excluded:** 41 first branches (2 empty), 132,986 projections, 832,295 lifts, full unchanged ordered replay; all 85 terminal width-three CNFs independently reconstructed and included in their fresh original references, with fresh CakeLRAT checks. No fallback required. | hand + enum + cert (conditional), pending critic | `shared74_round15.md`, `scratch/E/r15_shared/freeze.8.sha256`; 0.15664 core-h main, 0.17446 with controls and repricing |
| On 16 dispersed exact terminal IDs including both ends: wide-only 20.31 CPU-s, narrow with fresh references, binding, solve and recheck 18.62 CPU-s including a separate fresh rebind; peak 177,288 vs 40,976 KiB, ~5% more retained bytes. Positive control exercises the original-width fallback; no real-ID fallback needed. | enum + cert (pilot) + estimate | `scratch/E/r15_shared/spaced.8.compare.{wide,narrow,rebind}.log`, `shared74_round15.md` |

## Handoff

- Ask critic to replay the proof route and exact cover using the recipe
  in `shared74_round15.md`. Production proofs this round are on weak
  width three, not on the retained original width-eight references.
- Five mixed cores remain if accepted: 1, 6, 9, 15, 18. Ask critic
  which single core to price next. Core 6 is next in the old ranked
  list but had 70 first branches and concentrated front hard lifts;
  core 15 looks like a cheaper price-only alternative, not yet priced
  beyond archived front/tail. Do not extrapolate core-8 proof behavior
  or run cores 9/18 without a new cost gate.
- `(5,5)` already certified. No full `(2,32)` closure, no candidate,
  no rigidity theorem, and no Ramsey verdict.
