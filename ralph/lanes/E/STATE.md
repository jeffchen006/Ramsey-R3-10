# Lane E state — round 20 complete

2026-11-22 CET. Ceiling 19; critic authorized the frozen 16-ID
matched proof pilot only. Used one serial worker, 0.00892 total
core-h and ~36.4 MiB new staging, below 0.08 core-h / 96 MiB.
Peak RSS 186,460 KiB under 1 GiB hard address-space cap.

## Jobs

None active, detached, stopped or killed. All wrappers exited 0.
Full commands and caps in `scratch/E/r20_shared/{jobs,exits}.tsv`.

| Wrapper PID | Command / log stem | Cores | Start / actual end CET |
|---|---|---:|---|
| 2981483 | inherited hashes and controls / `preflight` | 1 | 17:24:54 / 17:24:56 |
| 2989989 | `paired_core1_74.py target` / `target` | 1 | 17:25:21 / 17:25:50 |
| 3020250 | `paired_core1_74.py audit` / `audit` | 1 | 17:26:41 / 17:26:42 |
| 3021229 | `reprice_core1_74.py` / `pricing` | 1 | 17:26:42 / 17:26:43 |
| 3030352 | independent set and marker cross-check / `crosscheck` | 1 | 17:27:11 / 17:27:11 |

## Claims for H / critic

Core 1 `G?bFbo` only under E-021 and E-042/043 premises: mixed
`(2,32,4)`, `δ(W)≥2`, `e(W)=11`, profile `(10,10,11,11)`, universal
`δ(G)≥5` and the sole-missing all-graph order-26/e74 class. All graph
scope, no MTF. See `shared74_round20.md`; evidence names in the table
are relative to `scratch/E/r20_shared/`.

| Item | Label | Evidence |
|---|---|---|
| Exactly 16 fresh physical IDs certified once each: width three and original width eight each freshly rebound and both checkers verified all 16/16; no fallbacks. Old 16 disjoint; 32 of 147 now certified and 115 unresolved. | cert (conditional local IDs only), open (core) | `paired.jsonl`, `target/`, `audit.log`, `crosscheck.log`, `residual.jsonl`, `freeze.1.sha256` |
| Narrow 11.669 CPU-s vs wide 15.898 CPU-s route totals, ~26.6% less; target wrapper 28.79 CPU-s inclusive of driver. Total round 32.11 CPU-s. | enum (measurement) | `target.log`, `preflight.log`, `pricing.log` |
| 115-ID narrow first estimate 88.00 CPU-s / 129.98 MiB no fallback; 142.95 CPU-s / 185.66 MiB for six stress fallbacks. Wide-only baseline 115.28 CPU-s / 126.59 MiB. Rates for 83 third / 25 branch / 7 global. | estimate | `reprice.strata.tsv`, `pricing.log` |

## Next

- Request critic authority for `residual.jsonl` only: one worker,
  ≤0.065 core-h / ≤1 GiB per process / ≤224 MiB new staging. Narrow
  first with fresh binding/dual check; width eight only on narrow
  SAT/cap. Stop on budget, binding or checker failure, or wide SAT;
  no partial proof counts as UNSAT. Not started.
- Core 1 and the other three conditional mixed cores `{6,9,18}` remain
  open; `(5,5)` remains certified. No candidate, full involution case,
  rigidity, or Ramsey verdict.
