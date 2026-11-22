# Lane D — round 17, 2026-11-22 (final)

**Marked R(3), K=2,t=17,m=16 excluded**, submitted for critic review: hand + enum + cert (local ordinary CNFs). Thus any marked deficient path with exactly 17 pentagons at K=2 must have ≤15 untouched edges. No ruling on all t=17, K=2, R(3), R(4), an original kernel or R(3,10). No candidate. `S=scratch/D/middle17`. Prior R16 pilot D-042 and each-path floor D-041 confirmed. R16 handoff archived in `LOG.md` and `S/state_round16.md`.

## Jobs

| PID | Command / log | Cores now | Start | End |
|---|---|---:|---|---|
| none | No live, stopped or detached jobs. All 4 `middle17.py rest W` workers finished, canonical archives and `.ok` records retained (`S/rest-*.log` and `.time`). | 0 | 13:16:59 | by 13:49:06 |

## Results and claims

| Label | Result | Evidence | Core-h |
|---|---|---|---:|
| hand + enum | Rebuilt 52,065→33→6 support inventory, 15,282 canonical IDs, 320,878 ordered shore pairs on the fixed supports. C22: all 125 plant/mutation pairs passed. | `S/{census.log,plants.log,frozen/SHA256SUMS}` | 0.00127 |
| cert (local) | 384 dispersed canonical IDs, including all 72 old orbits, weight 9,236; canonical orientation also for the two tails and all holdouts. Pre-expansion estimate 2.12 core-h, 1.81 GiB peak. | `S/{preprice.txt,price.log,checkpoint-*/batch*.zip}` | 0.05005 |
| cert (local) | All 14,898 remaining IDs produced and archive-replayed against the independent physical binder, two checker success markers both passes. Total 15,282 (checkpoint not additive). Raw 2.151 GB LRAT, 3.719 GB CNF; 1.716 GiB packed. Slowest combined ID 32:4098, 1.246 CPU-s. | `S/rest-*/batch*.{zip,ok}`, `S/final/{archives.sha256,complete.tsv}` | 2.01128 remainder |
| hand + enum + cert (local), pending | Complete marked slice only. Independent no-scout matching/triangle catalogue gave 6,135 labelled survivors. Independent orbit subtraction checked actual words and weights; second archive reconciliation read/hash-checked every CNF and LRAT and both passes' receipts, open.tsv empty. | `MIDDLE17.md`, `middle17_coverage.py`, `S/final/{coverage.log,reconciled.log,open.tsv}`, `ROUND17_FREEZE.sha256` | 0.01488 final audit; **2.07748 total** |

## Next

1. Critic: `bash ralph/lanes/D/round17_replay.sh scratch/critic/D17-audit sample` for full reconciliation plus another two proof checks on 192 dispersed worker/phase IDs; `full` replays all 15,282. Exact interpretation and replay mode costs in `MIDDLE17.md`. Do not treat this result as global Section 7 certification. Freeze binds the archive manifest in `S/final/archives.sha256`.
2. At K=2,t=17,m=15 the balance gives one exceptional pole of type (1,2) up to shore swap, and a unique three-pole Y site among thirteen two-pole sites. If authorized, do an independent pilot **census only** of this asymmetric support layer before pricing a join. No production or m≤15 run was made, and no extra cores are needed now.
