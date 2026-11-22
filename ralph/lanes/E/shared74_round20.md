# Round 20 — core 1 comparison pilot

Authorization: the 16 frozen new IDs only; ≤2 workers, 288 CPU-s,
1 GiB/process and 96 MiB of new scratch. Use one serial worker. The
round-18 identical-size sample took 13.98 + 26.64 = 40.62 CPU-s and
34.96 MiB for both routes. Three times that CPU measurement (121.86 s)
is a planning sensitivity, not a bound. The new independent checker
and textual LRAT may change both costs; allow 190 s wall for target
work, with per-solve 7 CPU-s/15 s wall and per-check 10 CPU-s/30 s wall.
Use 8 MiB per file, stop before 94 MiB logical staging, and bound
setup, calibration and postprocessing separately within the 288 s cap.

For scope and inputs see `shared74_round18.md` and `shared74_round19.md`.

## Binding and results (cert, local only)

This is conditional mixed core 1 `G?bFbo` under `(p,f,t)=(2,32,4)`,
`δ(W)≥2`, `e(W)=11`, profile `(10,10,11,11)`, universal `δ(G)≥5`
and the all-graph sole-missing e74 premise E-021, with the inherited
cover of all four omission roles and `K=6,7,8`. No MTF assumption.

The frozen R18 and R19 manifests passed. Read the R19 full receipt
stream independently to extract its 147 open IDs, check that the 16
R18 IDs and 131 pending IDs partition it, and check that the target
IDs are exactly the frozen 16, all pending. Bind the global cover
rows to the independently indexed branch copies, including lift
ordinal and actual bitmask groups. Reconstruct width eight from the
physical row and compare byte-for-byte at rebind; for width three,
also use `bind_width74.binding`'s independent reconstruction of the
base and cuts and exact inclusion in the original-width reference.
Both CakeLRAT and `lrat-check` accepted each of the 32 textual LRATs.
The six-site positive reaches wide SAT after narrow SAT, and the
negative is dual-checked at both widths. The smaller C13 positives,
exhaustive small controls, and wrong branch/formula/lift controls pass.

| Route | Checked | Setup / solve / verify CPU-s, summed across 16 | Retained route bytes |
|---|---:|---:|---:|
| Width three, including fresh width-eight reference | 16/16 | 10.245 / 0.306 / 1.118 = 11.669 | 19,076,763 |
| Original width eight | 16/16 | 10.420 / 0.753 / 4.724 = 15.898 | 18,971,289 |

Width three took 26.6% less route CPU in this comparison, with 0.56%
more artifact bytes. The driver adds 1.18 CPU-s one-time, mainly
reading the roster, and ~0.00274 s/ID framework overhead. Observed
fallbacks: 0/16, not a bound. The two routes prove the same 16 IDs,
not 32 exclusions. Together with the 16 nonoverlapping old receipts,
32 of 147 have proofs; **115 remain**. No closure of this core, the
involution case, or a degree distribution. No candidate.

## Residual estimate and next authorization request

The residual costs use current dual-checker measurements only. Of 115
IDs, 83 use their branch-third rate (each directly matched stratum has
one measurement), 25 their branch pool, and 7 the global pool. The
table in `reprice.strata.tsv` separates setup, solving, checking and
bytes. Control, audit, one-time setup and per-ID overhead add 4.69
CPU-s to either extrapolation. Width three first with no fallback:
**88.00 CPU-s / 129.98 MiB**. Width eight only: **115.28 CPU-s /
126.59 MiB**. At six fallbacks, conservatively charging an extra 8 s
and the largest sampled checked wide time plus 8 MiB partial LRAT
and a sampled wide-size maximum each, width three first prices at
**142.95 CPU-s / 185.66 MiB**; at 23 the same scenario prices at
298.65 s / 343.42 MiB. These are sensitivities, not worst-case bounds.

Request next-round authorization for the exact `residual.jsonl` only,
narrow first, original-width solve only on recorded narrow SAT or cap,
with fresh binding and both checkers. One worker, ≤0.065 core-h all-in,
≤1 GiB/process, ≤224 MiB new staging, preserve file/time limits and
stop with exact unproved IDs on any cap, failed binding/check or wide
SAT. No residual proofs launched this round; no other core requested.

## Evidence

`scratch/E/r20_shared/freeze.1.sha256` pins the run, prior manifests,
checkers, physical-ID receipts, artifacts and timings. In that work
directory, `sha256sum --quiet -c freeze.1.sha256` reads them all.
`audit.log` binds the ordered paired prefix and exact subtraction;
`crosscheck.log` independently checks the text set difference and
both 32-marker totals. All five wrappers finished normally. Total
**32.11 CPU-s (0.00892 core-h)**, ~36.4 MiB new staging, peak RSS
186,460 KiB; no active/detached jobs.
