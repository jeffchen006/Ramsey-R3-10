# Lane E state — round 19 complete

2026-11-22 CET. Ceiling 17; critic authorized core 1 scan and exact
Python replay only (≤2 workers, ≤0.30 core-h, ≤192 MiB new staging).
All work stayed within that authorization. No target proof launch.

## Jobs

None active, detached, stopped or killed. All ten wrappers collected;
full commands, CPU/wall caps, ends in `scratch/E/r19_shared/{jobs,exits}.tsv`.

| Wrapper PID | Command and log stem | Cores | Start / actual end CET |
|---|---|---:|---|
| 1075402 | inherited hash, merge controls and `prepare` | 1 | 16:03:15 / 16:03:16 |
| 1086959 | positive/adversarial `controls` | 1 | 16:03:35 / 16:03:37 |
| 1087116 / 1087118 | `full_core1_74.py scan 0/1` | 2 total | 16:03:37 / 16:04:38, 16:04:55 |
| 1125234 / 1125230 | `full_core1_74.py replay 0/1` | 2 total | 16:04:55 / 16:06:18, 16:06:30 |
| 1163191 | `full_core1_74.py finish` | 1 | 16:06:30 / 16:06:33 |
| 1171627 | `price_full_core1_74.py` (`pricing.log`) | 1 | 16:06:50 / 16:06:50 |
| 1182804 / 1191613 | supplemental text audit, then fixed byte-total cross-check | 1 each | 16:07:18 / 16:07:18; 16:07:43 / 16:07:43 |

## Results and claims for H / critic

Core 1 `G?bFbo` only, `(p,f,t)=(2,32,4)`, `δ(W)≥2`, `e(W)=11`,
profile `(10,10,11,11)`, universal `δ(G)≥5` and E-021 all-graph
sole-missing order-26/e74 class. All four omission roles and `K=6,7,8`;
no MTF assumption. Evidence report: `shared74_round19.md`; all staging
names below relative to `scratch/E/r19_shared/`.

| Item | Label | Evidence |
|---|---|---|
| Entire 24-branch, 12-shard cover (68,323 projections; 565,531 lifts) scanned, unchanged Python replayed, exactly merged. 147 terminal IDs across 113 projections and 14 branches; all 3,385 old pilot projections / 12,814 receipts match. | enum (conditional roster) | `finish.log`, `final.audit.fixed.log`, `terminal.1.jsonl`, `freeze.1.sha256` |
| 24 old pilot terminals, of which the 16 E-042 proofs count once each. Pocket of 131 IDs in 103 projections remains; no new proofs or closure. | cert (inherited 16 only); open | `pending.1.jsonl`, `finish.log`, `../r18_shared/freeze.1.sha256` |
| Full scan + replay 139.44 + 175.54 CPU-s vs 219.12 + 299.95 estimated. Pending base estimate 114.88 CPU-s / 148.43 MiB narrow or 221.70 CPU-s / 138.87 MiB wide. 54/131 use global rates; retries priced separately. | enum timing + estimate | `branch_rates.tsv`, `pricing.log`, `price.strata.tsv` |

Total 321.01 measured CPU-s (0.08917 core-h), 48.14 MiB new logical
staging. The first supplementary audit failed a hardcoded byte total,
then the rerun compared to independent file sizes and passed.

## Handoff

- Request authority only for the frozen **16-ID** stratified matched
  proof pilot in `proposed_pilot.1.jsonl`, at most 2 workers,
  ≤0.08 core-h / ≤96 MiB new scratch. It was not run. Reprice after
  independent rebinding; no extrapolated exclusion or bulk launch.
- Four mixed cores `{1,6,9,18}` remain open, including core 1. `(5,5)`
  was already certified. No candidate, full `(2,32)` debit, rigidity,
  or Ramsey verdict.
