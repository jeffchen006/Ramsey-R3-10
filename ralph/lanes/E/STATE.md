# Lane E state — round 18 complete

2026-11-22 CET. Allocation ceiling 16, critic authorized pricing **one**
core, ≤2 simultaneous workers, ≤0.35 core-h, ≤512 MiB new scratch,
≤16 matched proof IDs. No authorization for the full scan or any bulk
terminal work. E-041 (core 15) now confirmed by the critic.

## Jobs

None active, stopped, killed or detached. All 24 bounded foreground
wrappers collected (zero exits; one wrapper ran on empty stdin and did
no work, superseded by the estimator rerun). Exact PID, command, log,
start and expected/actual end: `scratch/E/r18_shared/{jobs,exits}.tsv`.

| Work | PID(s) of wrapper | Peak slots | Start / actual end CET |
|---|---|---:|---|
| Controls and census | 3231636, 3238736, 3276830 | 1 | 14:35:56 / 14:37:37 |
| Bands, both replays, independent cover and audit | 3281602, 3281637, 3284404, 3284406, 3285560, 3286354, 3290210, 3290565, 3290681, 3292117, 3292175, 3292256, 3292774 | 2 | 14:37:47 / 14:38:15 |
| Matched proofs and separate fresh bind/check | 3302509, 3302511, 3305918, 3310305, 3315170 | 2 | 14:38:36 / 14:39:03 |
| Estimates and clean uninstrumented replay | see ledger | 1 | 14:39:30 / see ledger |

## Results and claims for H / critic

Scope: zero-based **core 1**, `G?bFbo` in `scratch/E/r5_saturated/e11.g6`;
`(p,f,t)=(2,32,4)`, `δ(W)≥2`, `e(W)=11`, mixed `(10,10,11,11)`,
universal `δ(G)≥5`, E-021 all-graph sole-missing order-26/e74 class,
all four omission roles and `K=6,7,8`; no MTF assumption. No reliable
ranking of all four candidates in the prior data, so used critic default.

| Item | Label | Evidence |
|---|---|---|
| Byte-identical independent ordered cover: 24 nonempty first branches, 68,323 projections, 565,531 lifts; boundaries frozen. | enum (denominator) | `shared74_round18.md`, `scratch/E/r18_shared/{freeze.1.sha256,verify.1.log,metrics.1.tsv}` |
| 3,385 front/interior/tail projections (25,785 lifts), 24 terminal IDs. Both independent replays pass and uninstrumented receipts match. 16 matched IDs check by both narrow and width-eight routes with fresh rebinds: 13.98 versus 26.64 CPU-s. | enum + cert (pilot only) | `scratch/E/r18_shared/{controls.log,clean.pilot.log,pilot_opens.1.tsv,matched.1.jsonl,matched.audit.log}`, same report/freeze |
| Full scan + unchanged replay approx. 219 + 300 CPU-s. Plan staging + current files ~122 MB logical. Clustered sample queue proxy (~1,457) is not a bound. | estimate | `scratch/E/r18_shared/estimates.recheck.1.log`, same report/freeze |

Total 108.29 measured CPU-s (0.03008 core-h), ~53 MiB retained
logically. No other mixed core worked, no candidate or exclusion.

## Handoff

- Request authority only for a full **scan + unchanged ordered replay**
  and exact queue merge of the frozen core-1 cover: 12 shards, ≤2 slots,
  ≤0.40 core-h and ≤192 MiB additional staging. Reuse the frozen cover.
- Authorize no bulk proof work from sample rates; reprice from the
  exact queue, preserving overlap with the checked pilot IDs.
- Four mixed cores `{1,6,9,18}` remain open. `(5,5)` was already certified.
  No claim of the full `(2,32)` case, rigidity, or a Ramsey verdict.
