# Lane D — round 1, 2026-11-21

**Open:** No R(3) closure or 40-vertex candidate. First-round directives: none.
Read required report and notes. Allocation 12; preferring small bounded samples.

## Results

| Label | Result | Evidence | CPU-h |
|---|---|---|---:|
| enum | Regenerated 238 R(3) kernels; independent colored path/cycle signatures agree one-to-one; 166 modulo global side exchange. Formula calibrated on smaller -D2 catalogue (12 oriented, 10 up to exchange). | `scratch/D/catalogues/component_check.log`, `ralph/lanes/D/catalogue_m3.py` | <0.001 |
| enum | All 55 pinned controls extend to satisfying auxiliary assignments: 5 modes × (ten known C22 plus C35), relabeled at globally min-C4 edge. Pin test is not complete enumeration. | `scratch/D/pinned/pinned.log` | 0.0092 |
| estimate | C22 calibration expected ~2–5 minutes wall per variant (repo old 93–116 CPU-s across 474; local first kernel 0.22 CPU-s); both batches cap each solve at 8 CPU-s. | `scratch/D/smoke/results.tsv`, sec8.tex | — |
| enum | Both `local` and `minedge` give only C13(1,5) across 12/12 kernels under M=3; exact canonical comparison. | `scratch/D/cal13_{local,minedge}/canonical.g6` | <0.001 |
| estimate | R3 paired probe: 10 nonduplicate survivor orbits stratified by e(F), seed 3401, at most 75 CPU-s each on base and minedge (0.42 CPU-h worst case across both). Previous first-15 timings 0.6–33s or >3600s; survivor sample deliberately emphasizes unsolved classes, not a uniform whole-catalogue predictor. | `scratch/D/r3_survivor_sample.tsv`, sec8.tex | — |
| enum | Boolean-mask projection: C13 pinned projection accepted (with endpoint minimum-edge rows and all lazy cut families enabled); n=14 control kernel rejected. Both <0.1 CPU-s after import. | `scratch/D/projection_cal{13,14}.log` | <0.001 |
| estimate | Boolean-mask R3 pilot: four matched C LP survivors (two low e and two high e), hard caps 4×60 CPU-s, 0.067 CPU-h; R3 assembly cost unknown (C linear LP builds of same rows take seconds). | `ralph/lanes/D/mask_probe.sh` | — |
| estimate | Efficient totalizer orientation retest, same selected four kernels: original first two exhausted 60 CPU-s during construction (4.5–4.7 GiB RSS). On the n14 control clauses decreased 5991 → 4615; one-sided limits now use the cheaper polarity. New upper budget 4×60 CPU-s. | `scratch/D/r3_mask/`, `scratch/D/projection_cal14_leanTotalizer.log` | — |
| estimate | Lazy Boolean-mask retest on same four: eager v2 still exhausted 60 CPU-s in assembly. Lazy cuts replace large families of totalizers and add independent sets of the possible-edge supergraph. Clauses on n14 control now 2640 vs 5991 originally. Cap remains 4×60 CPU-s. | `scratch/D/r3_mask_v2/`, `scratch/D/projection_cal14_supergraph.log` | — |
| estimate | MiniCard native projection: C13/n14 controls matched, and repeated-literal native cardinality semantics truth-table checked. No CNF auxiliaries: n14 uses 19 selectors and 88 native bounds. Same four probes capped at 4×60 CPU-s; avoid full sweep unless a meaningful fraction resolves quickly. | `scratch/D/projection_cal{13,14}_native.log` | — |
| enum | C22 full root catalogue: base recovered exactly the ten canonical graphs (474/474, 177.01 CPU-s); local recovered same ten (212.78 CPU-s including one 8-s timeout and 8.89-s retry). Minedge had 6 timeouts, 468/474 complete in its 8-s-cap test; not a complete C22 calibration. | `scratch/D/cal22_{base,local_complete,minedge}/results.tsv` and canonical files | 0.184 |
| enum | C16 saturated M=3 calibration: `minedge` across 13/13 kernels recovered the same five canonical 5-regular (3,6,16) graphs as root-only SMS; pinned C16(1,3,8) also accepted by MiniCard projection. | `scratch/D/calibration16/` | <0.001 |
| enum | Lane C's 78 already checked oriented exclusions cover 56 of the 166 side-exchange orbits. Our independent mapping gives **110 representative kernels left**: 1/1/11/23/35/39 for 8/9/10/11/12/13 edges. This does not independently re-certify C's exclusions. | `scratch/D/survivor_orbits.log`, `scratch/D/survivor_orbits/orbits.tsv` | <0.001 |
| open | Paired R3 survivor probe: base 0/10 and minedge 0/10 within bounds, no models. Base 745.10 CPU-s; minedge 696.09 CPU-s (four wall caps censored at 56.85–67.33 CPU-s). Negative bounded experiment, not an extrapolated runtime or closure. | `scratch/D/r3_{base,min}75/results.tsv` | 0.400 |
| open | Boolean-mask projection on the same four survivors, 0/4 decisions in each of original eager, optimized eager, sparse lazy, and native-cardinality runs. All child outcomes 124/152 (timeouts). Sparse eager CNF while delaying residual rows uses ~1.0–1.75M clauses; native uses ~1.7–3.1k selectors and ~9.5–24.7k native rows. Both finished assembly; neither logged a 10-model checkpoint or a verdict. | `scratch/D/r3_mask{,_v2,_lazy,_native}/k*.log` | 0.263 |
| enum | R(3) kernel 0: SMS UNSAT, Lean checked 249 SB clauses, 812 lazy IS clauses passed shape check, all 9,880 TRI present, CakeLPR verified. Lean rejected a complement-flipped witness in the C22 trace control. Lane C already excludes kernel 0. Link (a) (verified base encoding) missing; no new `cert` claim. | `scratch/D/r3_proof/k0000.checked/{sym-lean,cnf,cake}.log`, `scratch/D/cal22_proof/k0000.checked/bad-lean.log` | 0.0018 solver only |

## Jobs

**None active**, as checked at 17:06 CET. Historical launch table below.

All are launched in `scratch/D` via `setsid nohup nice -n 5 timeout`; every solver has 16GB virtual-memory cap and its own CPU/wall timeout. `batch.py` path `../../ralph/lanes/D/batch.py`.

| Timeout / launcher PID | Command (after timeout) | Log | Cores | Start | Expected end |
|---|---|---|---:|---|---|
| 370312 / 370328 | `batch.py 22 6 5 catalogues/C22.g6 local cal22_local --seconds 8 --workers 4` | `scratch/D/cal22_local.log` | 4 | 16:42:42 | ~16:46; hard 1100s |
| 370316 / 370354 | `batch.py 22 6 5 catalogues/C22.g6 minedge cal22_minedge --seconds 8 --workers 4` | `scratch/D/cal22_minedge.log` | 4 | 16:42:42 | ~16:46; hard 1100s |
| 450393 / 450407 | `batch.py 22 6 5 catalogues/C22.g6 base cal22_base --seconds 8 --workers 3` | `scratch/D/cal22_base.log` | 3 | 16:45:18 | ~16:50; hard 900s |
| 554198 / 554221 | `batch.py 22 6 5 catalogues/C22.g6 local cal22_local_retry --indices cal22_local_retry.ids --seconds 100` | `scratch/D/cal22_local_retry.log` | 1 | 16:48:11 | ~16:52; hard 320s |
| 554199 / 554225 | `batch.py 40 9 3 catalogues/R3.g6 base r3_base75 --indices r3_survivor_sample.ids --seconds 75 --workers 2` | `scratch/D/r3_base75.log` | 2 | 16:48:11 | ~16:57–17:02; hard 1250s |
| 554200 / 554216 | `batch.py 40 9 3 catalogues/R3.g6 minedge r3_min75 --indices r3_survivor_sample.ids --seconds 75 --workers 2` | `scratch/D/r3_min75.log` | 2 | 16:48:11 | ~16:57–17:02; hard 1250s |
| 717958 / 718143 | `bash ../../ralph/lanes/D/mask_probe.sh 0 149 88` | `scratch/D/r3_mask/part0.log` | 1 | 16:54:25 | ~16:58; hard 360s |
| 717959 / 718144 | `bash ../../ralph/lanes/D/mask_probe.sh 1 151 227` | `scratch/D/r3_mask/part1.log` | 1 | 16:54:25 | ~16:58; hard 360s |
| 786702 / 786720 | `MASK_OUTDIR=r3_mask_v2 bash ../../ralph/lanes/D/mask_probe.sh 0 149 88` | `scratch/D/r3_mask_v2/part0.log` | 1 | 16:57:08 | ~17:01; hard 360s |
| 786703 / 786715 | `MASK_OUTDIR=r3_mask_v2 bash ../../ralph/lanes/D/mask_probe.sh 1 151 227` | `scratch/D/r3_mask_v2/part1.log` | 1 | 16:57:08 | ~17:01; hard 360s |
| 863822 / 863852 | `MASK_LAZY_ROWS=1 MASK_OUTDIR=r3_mask_lazy bash ../../ralph/lanes/D/mask_probe.sh 0 149 88` | `scratch/D/r3_mask_lazy/part0.log` | 1 | 17:00:02 | ~17:04; hard 360s |
| 863823 / 863853 | `MASK_LAZY_ROWS=1 MASK_OUTDIR=r3_mask_lazy bash ../../ralph/lanes/D/mask_probe.sh 1 151 227` | `scratch/D/r3_mask_lazy/part1.log` | 1 | 17:00:02 | ~17:04; hard 360s |
| 954519 / 954524 | `bash ../../ralph/lanes/D/mask_native_probe.sh 149 88` | `scratch/D/r3_mask_native/part0.log` | 1 | 17:03:03 | ~17:07; hard 360s |
| 954520 / 954528 | `bash ../../ralph/lanes/D/mask_native_probe.sh 151 227` | `scratch/D/r3_mask_native/part1.log` | 1 | 17:03:03 | ~17:07; hard 360s |

Early eager-mask launcher logs have a shell parse error **after** both
child exits were recorded; editing the shell source while live upset the
reader. Each reported child result is also in its own time log. The revised
script passes `bash -n`; avoid live edits to it.

## Claims / next

- `hand`: complete path/cycle classification of admissible rooted R(3)
  kernels and sound side exchange; `enum`: 238 ordered, 166 modulo exchange.
- `hand`: with R(3) minimum edge C4 count 13, every vertex has at least
  five singleton-codegree partners; all R(3) outside masks are distinct.
  Evidence for both hand claims: `ralph/lanes/D/ENCODING.md`.
- No new certified kernel closure and no candidate. Do not scale the
  measured variants unchanged, and leave R(4) until progress on R(3).
- Next try factoring projections into two side profiles: on each side use
  only 8 singles, 28 pairs, 56 triples. Singleton multiplicities are <=1;
  pair/triple multiplicities <=2 since any inner pair already shares the
  root. Enforce pair-capacity and the singleton-codegree matching locally,
  then couple side profiles only for cross-pair and residual constraints.
  Measure coverage/counts first on C16, then on IDs 149,151,88,227.
- Use `survivor_orbits.py` to rebuild the 110-orbit list from C's two
  baseline shards. If a future R(3) kernel solves, `check_trace.py`
  reproduces the R3 proof plumbing, but finish the VeriPB/CakePB encoding
  link (a) before reporting `cert`.
