# Lane E state — round 21 complete

2026-11-22 CET. Round-21 authorization was only the exact 115-ID
queue, one worker, ≤234 CPU-s all-in, ≤1 GiB VM and ≤224 MiB new
staging. Measured about 0.024 core-h and 132 MiB new staging.

## Jobs

None active, stopped, killed or detached. The main wrapper exited 0;
reaped Python PID 3642344 and timeout PID 3642343 are also gone.
Proof and resource evidence paths here are relative to `scratch/E/r21_shared/`.

| Wrapper PID | Command / log | Cores | Start / actual end / wall cap (CET) |
|---|---|---:|---|
| 3642341 | `nice -n 5 timeout -k 2s 223s taskset -c 30 ... residual_core1_74.py` / `target.log`, `usage.log`, `jobs.tsv` | 1 | 17:57:32 / 17:58:55 / 18:01:17 |

The short foreground, no-solver artifact pass is in `audit.log` and
`audit.usage`; it completed with exit 0. No solver job followed it.

## Claims for H / critic

Zero-based conditional mixed core 1 `G?bFbo` only under E-021/
E-042/E-043: `(p,f,t)=(2,32,4)`, `δ(W)≥2`, `e(W)=11`, profile
`(10,10,11,11)`, universal `δ(G)≥5`, all four windows are copies
of the sole missing all-graph order-26/e74 class. All four omission
roles and `K=6,7,8`; no MTF assumption. See `shared74_round21.md`.

| Result | Label | Core-h | Evidence |
|---|---|---:|---|
| 115/115 fresh frozen IDs passed fresh physical binding, width-three subset verification, and both LRAT checkers; zero fallback, 0 IDs left. | cert (conditional local IDs) | 0.0230 inclusive | `checked.1.jsonl`, `accepted.1.jsonl`, `remaining.1.jsonl`, `target/`, `target.log` |
| Close **only conditional mixed core 1**, pending critic: 565,384 inherited replayed negative lifts + 16 R18 checked + 16 R20 checked + 115 fresh checked = 565,531 lifts, 68,323 projections and 24 branches, zero outstanding. Independent artifact check: 115 actual omitted groups, 115 raw clause submultisets, 230 markers. | hand + enum + cert (conditional) | 0.00054 additional audit | `target.log`, `audit.log`, `freeze.1.sha256`, inherited R18/R19/R20 freezes |
| 66.788 s formula binding, 2.641 s solve, 8.805 s proof checking across 115 targets, no original-width solver call; main wrapper 82.72 s inclusive. | enum (measurement) | included above | `timing.tsv`, `usage.log` |

## Next

- Three conditional mixed cores remain: 6 `G?bav_`, 9 ``G?q`v_``,
  18 ``GCpb`o``. Ask critic for a bounded ordered-cover census and
  front/interior/tail price-only pilot on core 6, with independent
  binding and repeat controls before scaling. Suggested ceiling one
  worker, 180 CPU-s, 1 GiB VM, 96 MiB new staging; no full scan,
  SAT or proof batch. Unlaunched. See the legacy R10 sampled counts
  in `scratch/E/r10_shared/rank/summary.tsv`; not a ranking between
  current open cores.
- `(5,5)` remains certified. No new entire involution/rigidity
  exclusion, MTF-distribution debit, flow candidate or Ramsey verdict.
