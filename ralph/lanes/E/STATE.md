# Lane E state — round 14 complete

2026-11-22; machine time CET. Allocation 30, peak eight worker slots.
Round 13 core 17 accepted; see `LOG.md`. Round 14 worked only on core 5.

## Jobs

Exact foreground wrapper PIDs, commands, logs, starts, limits and
exits are in `scratch/E/r14_shared/{jobs,exits}.tsv` (one capped worker
slot per row). All 75 collected by 09:10:32 CET. No active, stopped,
or detached jobs. One setup error in the sample rebind: outer hard
CPU cap 24 s was below inner checker limit 25 s; retry checked all 16.

| Work | Peak slots | Start range (CET) | Latest allowed finish (CET) |
|---|---:|---|---|
| Controls, census, branch and band price, pilot proofs | 5 | 09:00:03–09:05:22 | 09:09:20 |
| Production 16 native scan / unchanged replay pairs and merge | 8 | 09:04:29–09:07:33 | 09:10:00 |
| Exact queue reprice / diagnosis | 1 | 09:07:55–09:08:51 | 09:09:31 |
| Production width-eight proofs / fresh rebind | 4 | 09:09:26–09:09:56 | 09:11:04 |

## Results and claims (for H / critic)

Core 5 `G?bebo` (zero-based in `scratch/E/r5_saturated/e11.g6`). Scope:
`(p,f,t)=(2,32,4)`, `δ(W)≥2`, `e(W)=11`, profile `(10,10,11,11)`,
universal `δ(G)≥5`, E-021 all-graph sole-missing `e=74` premise.
All four omissions and `K=6,7,8`; no MTF restriction.

| Item | Label | Evidence / cost |
|---|---|---|
| **Core 5 only excluded:** 37 independently bound first branches, none empty; 194,552 projections, 2,204,013 lifts, complete unchanged ordered replay, all 167 original width-eight CNFs freshly regenerated and CakeLRAT checked. | hand + enum + cert, pending critic | `shared74_round14.md`, `scratch/E/r14_shared/freeze.5.sha256`; 0.34909 core-h main, 0.37297 with controls/pricing |
| Three byte-bound price bands and branch-by-branch hard-lift distribution; scan + independent replay price 1,776 CPU-s, actual 932.25 before merge. Exact queue stop at 167, dispersed reprice 16/16 original CNFs. | enum / estimate | `scratch/E/r14_shared/{hard.5.tsv,merge.5.log,sample.queue.5.log,spaced.5.bind.retry.log}` |
| Independent width-three replay pilot: two-sign exact-degree six-vertex control, 512 edge assignments per sign; 14/14 band residuals freshly reconstructed, included in matching wide CNFs and CakeLRAT checked on narrow. No use in production. | hand + cert pilot | `bind_width74.py`, `scratch/E/r14_shared/{calibrate.narrow.exact.log,pilot.5.front.narrowbind.log,pilot.5.interior.narrowbind.log}`; narrow generation/solve/check and fresh binding/recheck ≈0.00171 core-h excluding wide references |

## Handoff

- Ask the critic to independently replay core 5 using `shared74_round14.md`.
  No new scan of other cores this round. Six mixed cores remain if core 5
  is accepted: 1, 6, 8, 9, 15, 18. Choose one priced core with the critic;
  no heavy 9/18 production until cheaper evidence warrants it.
- Width-three standalone literal-inclusion binder is now calibrated.
  It still requires a freshly bound original reference for each ID.
  Price the original fallback on every unresolved/SAT/capped narrow ID
  before any narrow production; narrow SAT alone is not a candidate.
- `(5,5)` already certified. No full `(2,32)` closure, no candidate
  graph, no rigidity or Ramsey verdict.
