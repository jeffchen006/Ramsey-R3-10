# Lane E log — round 1 archive

Round 1 complete (Nov 21). Share: 10 cores. All symmetry results use
all graphs, not just MTF. No candidate graphs sent to the gate.

## Jobs

No continuing search or checker. Terminated only the redundant unpinned
run after the four checked pins covered `(5,5)`; log UNKNOWN from SIGTERM
is **stopped**, not a timeout or an UNSAT answer.

| Timeout PID / solver PID | Command after limits, cwd `scratch/E` | Log | Cores | Start / planned deadline (host clock) | Final |
|---|---|---|---:|---|---|
| 153778 / 153885 | `python3 -u ../../ralph/lanes/E/orbit_run.py 5 5 n40_p5_f5 --time 3600` (CPU 3600, outer 4200 s) | `n40_p5_f5.log` | 1 | Nov 21 16:37 / 17:47 | SIGTERM 17:01; ~0.274 core-h |
| 736690 / 736840 | `python3 -u ../../ralph/lanes/E/slim5.py II n40_slim5_II --time 330` (CPU 375, outer 420 s) | `n40_slim5_II.log` | 1 | 16:55 / 17:02 | VERIFIED |
| 736693 / 736748 | same with `IC n40_slim5_IC` | `n40_slim5_IC.log` | 1 | 16:55 / 17:02 | VERIFIED |
| 736699 / 736847 | same with `CC n40_slim5_CC` | `n40_slim5_CC.log` | 1 | 16:55 / 17:02 | VERIFIED |
| 736702 / 736771 | same with `CD n40_slim5_CD` | `n40_slim5_CD.log` | 1 | 16:55 / 17:02 | VERIFIED |

## Claims and evidence (for H/critic)

| Claim | Label | Evidence | Core-hours |
|---|---|---|---:|
| `(5,5)` excluded | cert | `ralph/lanes/E/slim5.md`; four `scratch/E/n40_slim5_*.log`, proof files and `cert_sha256.txt` | 0.1485 |
| Original all-graphs `δ≥5` certified result replayed (not new mathematical claim) | cert | `scratch/E/deg4_replay.log`, `deg4_k10.{cnf,drat,lrat}`; original generator `critic/src/deg4_cnf.py`, Review 4 | 0.0155 |
| `(2,34)` excluded, no catalogue needed | hand | `ralph/lanes/E/involution.md`; `scratch/E/cal_involution.log` | <0.001 |
| `(2,32,a=5)` excluded | enum | `ralph/lanes/E/involution.md`, `check_min27.py`, `min27.g6`; `scratch/E/min27_check.log` | <0.001 |
| `(2,32)` with sizes `5,5,5,6` and an isolate in `W` excluded | enum | Same files; the 3,3,12,12 possible core/low triples all fail to partition | <0.001 |
| `(2,28,a=5)` and `(2,30,a=6)` excluded; also replace old `enum` exclusions at `a<=3` for those same `f` | hand | `ralph/lanes/E/involution.md`; Petersen and 3–6 pair phase controls in `scratch/E/cal_involution.log` | <0.001 |
| `(3,f,a)` excluded for `f∈{7,10}`, `a∈{5,6}` (strengthens prior `enum`) | hand | `ralph/lanes/E/cross_neighborhood.md`; C35 and all 729 order-12 shape controls in `scratch/E/cal_cross.log` | <0.001 |

## Tooling and measured work

- `orbit_run.py` uses the original satcore linked against `opt/cadical`
  and original `verify_sc.py` with `opt/bin/drat-trim` for unboosted proofs.
  Positive `(3,9,35)` controls order 7 and 5 pass (0.34 and 29.06 CPU s).
- `slim5.py`: exact five-fixed-point attachment and residual type pins;
  audit of the formula streams lazy witnesses. Smaller `(3,7,22)` with
  `(5,2)` had SAT IC/CD and DRAT-verified UNSAT II/CC. Deliberately
  strengthened lazy clause rejected. Full target pins took 22–64 wall
  seconds to solve (previous unpinned 1321.55 s); DRAT time dominated.
- `orbit_boost.py`: order-three weighted degrees, exact single/pair
  orbit anti-neighborhood constraints, optional seeded independent-set
  clauses. `--boost quotient|seeded` currently `--search-only`. C35
  `(3,5,a=1)` `seeded` SAT (0.28 CPU s); `(3,7,22; p=3,f=1,a=1)`
  UNSAT unchecked (0.12 CPU s). Extra C35 `a=2` trial unknown at 180 s
  (not the positive control). On `(3,10,2)`, `(3,10,3)`, `(3,7,2)`
  (here notation `p,f,a`), both 150 s `quotient` and `seeded` trials
  ended UNKNOWN: `scratch/E/sample_*.log`; 0.198 core-h total. No new
  runtime estimate for finishing these jobs and no long launch.

## Next steps

- Do not rerun `(5,5)` unless requested by the critic. Keep checked
  artifacts. Use pinned structural splits rather than increasing raw
  time for open order-three cases. The 12-vertex cross-neighborhood
  pattern and fixed-footprint options are promising for `a=4`.
- `(2,32,a=6)` crown with `t` size-six attachment sets. `t=1` now
  requires `W` without an isolate and has a size-27 residual with at
  most 87 edges: only 1,470 anchor classes. Build a crown-pinned
  extension splitter, calibrate on the Petersen fixed-set template,
  then measure a small sample before seeking cores. `t=2,3,4` open.
- `(2,28,4)` and `(2,30,{4,5})` have the same crown layout but remain
  open. Cases with few fixed points and `(5,0)` still open.
# Round 11 archive

Round-12 critic confirmed E-029/E-030 and E-031 in
`ralph/critic/round_011.md`. Cores 7 and 13 (only) closed under the
f32/t4/eW11 mixed scope and all-graph E-021 premise. Respectively
50,065/90,117 projections, 278,029/547,674 lifts, 11/29 original
CakeLRATs, 231.72/484.21 terminal CPU-s. Evidence `shared74_round11.md`
and `scratch/E/r11_shared/freeze.{7,13}.sha256`. Every order-26/e≤74
(3,8) graph has minimum degree at least four (191 all-graph order-22
parent CNFs freshly bound and CakeLRAT-checked; exact-e74 d3 census
also found no lift); this is independent of E-021 and does not recover
the missing class. `window74_d3.md`, `scratch/E/r11_shared/freeze.d3.sha256`.
Degree floor pruned 0/42 archived heavy-core IDs. All 61 wrappers
in `scratch/E/r11_shared/jobs.tsv` collected; no live jobs from r11.

# Round 3 handoff (2026-11-21)

- Completed `(2,28,a=4)` with 42 checked DRAT/LRAT proofs; see
  `crown28_exact.md`, `crown_cert/SHA256SUMS`, and round-3 `STATE.md`.
  Independently covered 6/9/15/9/3 core classes at W=4/5/6/7/8.
  Confirmed all 42 byte-identical CNF regenerations and LRAT checks;
  the trace validator rejects a forged `CUT 1` without writing a CNF.
- Main cost: 241.49 CPU s cold generation/solve/check, 114.66 CPU s
  witness search, 24.49 CPU s regeneration/LRAT, plus census/hashes.
  Unsorted W6 trial at 10 CPU s was capped and proof incomplete;
  no use in evidence. W4 unstrengthened pilot had 4 CPU kills.
- Order-three pair-footprint CSP added two independence tests per
  join, including independent sets using the origin O. Evidence
  `order3_a4_pairs.md`. All sixteen templates survive somewhere.
- Round 2 archival exact results retain their labels: no-isolate
  `(2,32,t=1)` 1,470 anchors/13,279 eligible windows and zero partitions
  (`enum`, complete with E-006); `(2,30)` W caps 10 at a=5 and 11
  at a=4 (`enum`); `(2,28,a=4)` prior W≤6 bound superseded;
  order-three a=4 fixes |H|=12 with eight pinned templates (`hand`),
  all 16 pass the one-orbit relaxation. See the lane evidence docs.

Round-3 bounded job archive (all collected): W6 local 1055712/14/17
(18:54, cap 20 CPU/40 wall s); W6–8 proofs (18:56, max 15 slots);
W5 exact 1405129/1405140/1405158 (18:58, cap 65/100 s), W5 cold
1529565–1529624 and W4 pilot 1529533–1529560 (19:00, W4 cap 35/55 s);
W4 anchor 1629917–1629937 (19:02, cap 30/50 s), clean checks
1699357–1699433 (19:03, cap 65/100 s); W4 cold 1785258/1785264/
1785269/1785281/1785292/1854133 (19:04–19:06; solve/check caps 75/50 CPU s).
Replay at 19:07 ended 42/42 with matching hashes.

## Round 4 archive


2026-11-21; share 20 cores, peak 15 one-core foreground jobs. No
candidate graph submitted, no Ramsey verdict. All symmetry claims are
about all graphs, not only MTF. Prior work and PIDs: `LOG.md`.

## Jobs

No live lane-E jobs; no detached jobs this round. All listed wrapper
PIDs were foreground batch children and were collected. Solver/scan jobs
ran in `scratch/E` with `nice -n 5`, wall+CPU caps and 16 GiB `ulimit -v`.

| Command / wrapper PIDs (one core each) | Local start; cap | Evidence and final status |
|---|---|---|
| `involution_cores.py calibrate/28/32`, serial | 19:57; 60 CPU/80 wall s max | `r4_cal_cores.log`, `r4_{28,32}_profiles.log`; 85/3 projected profiles |
| `involution_sat.py --profiles r4_{28,32}_profiles.jsonl`, 727030–727059 | 20:01; 24 CPU/40 wall s | `r4_pilot/{28,32}.*.log`; 11/11 f28 unchecked UNSAT, 3/3 f32 CPU-killed |
| CaDiCaL on six f28 *base* CNFs, 840828–840837 | 20:04; 25 CPU/45 wall s | `r4_base_sat/profile.*.log`; six SAT relaxations, not candidates or proof artifacts |
| f28 six residuals, `involution_sat.py --seed 5`, 870780–870787; f32 nine pinned cores `--seed 6`, 870811–870936 | 20:04; f28 36 CPU/58 wall s, f32 24 CPU/42 wall s | `r4_pilot/28.res.*.log`: all CPU-killed; `32.*.*.log`: three unchecked UNSAT, six CPU-killed |
| `overlap_windows.py --partitions`, PIDs 999132 (naive), then optimized foreground | 20:07; 75/80 CPU and 120/125 wall s | naive killed; optimized 54.13 CPU s, zero surviving root placements; superseded by weighted replay |
| `replay_overlap28.sh`; 42 older crown proof hashes, serial | 20:11–20:12; 40 s outer for scalar replay | `r4_pilot/{overlap.replay,crown28.hashcheck}.log`, all checks pass |
| `crown32_pressure.py` with `t=2/3/4`, 1451422–1451424; raw replay 1481620–1481622 | 20:15–20:16; 15/18 CPU s and 30 wall s | `r4_pilot/{w*.pressure.log,recheck/w*.log}`, all outputs byte-identical |

## Results and claims for H/critic

| Claim/result | Label | Evidence | Decisive core-hours |
|---|---|---|---:|
| `(2,28,a=6)` excluded. Hand reduction forces a four-cycle of overlapping size-six attachments. Four order-17 windows give average fixed-degree sum ≤62 but the exact window minimum is 66. Uses D-G3's seven `(3,6;17)` classes, no δ≥5/MTF dependency. | enum, pending review | `ralph/lanes/E/overlap28.md`, `replay_overlap28.sh`, `overlap17.g6`, `scratch/E/r4_pilot/overlap.replay.log` | 0.00017 |
| Consequently all `f=28` attachment sizes now have exclusions reported, inheriting their distinct statuses; need H/critic to combine a≤3/a=5 hand, a=4 cert, a=6 enum, and a=7 F10. | pending aggregate | above; `involution.md`, `crown28_exact.md`, `notes/symsat.md` F10 | — |
| `f=32`, t=2/3/4: singleton-neighbor capacity necessary bound. Of 6657/1407/356 eligible W cores, 6196/1136/313 survive. At t=4 with min degree of W at least 3, W is cubic and every full attachment has exactly two double rows. | hand bound; enum counts; no full t closure | `ralph/lanes/E/crown32_pressure.md`, `scratch/E/r4_pilot/recheck/w*.log` | 0.0013 |
| `f=32` comparison: three unpinned CPU kills; three of nine pinned unchecked UNSAT, six CPU kills. Unpinned 207–229k base rows, pinned 136–168k. | enum for the three pins only; remaining open | `ralph/lanes/E/crown32_pressure.md`, `scratch/E/r4_pilot/32.*.log` | ~0.063 |
| Prior `(2,28,a=4)` 42 proof bindings intact; no replayed or new proof search this round. `(5,5)` is already cert from round 1. | prior cert / integrity check | `ralph/lanes/E/crown28_exact.md`, `scratch/E/r4_pilot/crown28.hashcheck.log`; `ralph/lanes/E/slim5.md` | — |

## Next steps

- H/critic: review the structural reduction and U-budget algebra
  in `overlap28.md`; `cd scratch/E && bash ../../ralph/lanes/E/replay_overlap28.sh`
  validates the complete min-66 check by two algorithms in under a
  CPU second. BOARD notified F not to repeat the f=28 a=6 branch pending review.
  The earlier 85-profile quotient census and 127,502-cycle join were
  exploratory; the closure needs neither. Never treat SAT base models
  nor CPU-killed lazy runs as candidates/exclusions.
- For `f=32`, test the two cubic W cores within `(t=4,δ(W)≥3)` with
  exact support pins: each double row uses two singleton slots of
  nonneighbors which are adjacent to each other (triangle-freeness and
  α(W+A_i)≤6). Then reuse their profiles in the four attachment
  windows. Do not scale raw pinned/unpinned SAT from the measured sample.
- `(2,30)` smaller windows, `(5,0)`, and order-three open cases untouched.
  For order three, try three-orbit joint constraints only with a matched
  pair baseline; the prior pair-footprint pilot left all templates alive.

## Round 5 archive

- All jobs collected. Saturated f32 case `t=4,δ(W)≥2,e(W)=12`:
  1,058 cubic plus 6,904 noncubic checked CakeLRAT proofs, 1.2144
  production core-hours; replay regenerated all cubic and 56 sampled
  noncubic CNFs. See `cubic32.md`, `replay_cubic32.sh`, and
  `scratch/E/r5_{cubic,saturated}/freeze.log` and their hash lists.
- `window73.md` uses the exact 62-class degree census to show W
  saturation `d_F=8` and for `e(W)≥9` attachment saturation `d_F=7`,
  giving `e(G)=176`. The 25-vertex 396-class control was independent.
  At 11 edges the only incidence profiles are `(10,10,10,12)` and
  `(10,10,11,11)`. This was an enum-assisted necessary bound, not a
  closure. The pre-orbit forecast `e11.forecast.log` was preliminary;
  the round-6 exact case counts supersede it where computed.
- Frozen f28 mixed-status cover in `f28_cover.md`; unchanged f32
  `t=0,1` work, `f=30` reductions, and `(5,5)` proof. No candidate.

## Round 6 archive

- Profile `(10,10,10,12)` at saturated m11 excluded over all 19
  cores: 180,325 projections, 128,474 graph witnesses, 51,845
  primary checked LRATs and 144 exact lifts of six residual
  projections (101 witnesses, 43 checked LRATs). 2.9089 primary
  CPU-hours. All solver wrappers `2053353`–`2053368` collected,
  22:51:33–23:04:28. Evidence `m11.md` and
  `scratch/E/r6_e11/profile_a11.final.log`.
- Mixed m11 `G?Beto` excluded: 9,012 projection and 39,503 lift
  graph witnesses; 389 remaining projections with checked LRATs.
  No runoff to other cores; core-9 and core-18 raw graph scans
  capped, despite exact support generation. Their traces are not
  complete. Other prior f32/e12 and f28 scopes unchanged.
- Reverse e74 partial catalogue 1,624/1,625; known maximum degree
  seven has multiplicity at most four. For mixed m11 all four
  windows must be the same missing class. No new class from
  complete one-/two-star and two-edge swap sweeps.

## Round 7 archive (2026-11-22)

Scope `(2,32,t=4,delta(W)>=2,m=11)`, mixed profile, universal
`delta(G)>=5`, all graphs. `G?bBro` only: 7,046 exact projections,
36,612 full supports, 4,879 projection witnesses covering 23,294
lifts, 12,939 incompatibilities, 322 other graph witnesses and 57
fresh-CNF CakeLRATs (~0.07 core-h final; confirmed by critic round 7).
K=6/7/8; old non-final scan lacked K=8, corrected receipts move 12
lifts from incompatible to graph witnesses but do not change the 57
proof IDs. Matched graph-only vs graph-first: 785 -> 57, 10.55 vs
16.28 CPU-s, compared with 71.32 CPU-s isomorphism-first. C13 controls
520 positive and 520 negative. See `shared74.md`,
`scratch/E/r7_shared/freeze.3.sha256` and `ralph/critic/round_007.md`.
No closure outside this mixed core; no live jobs at round end.

## Round 8 archive (2026-11-22)

``G?bF`w`` (mixed core 2) alone excluded: 49,330 exact projections /
556,561 lifts. Graph-only 40,880 → marked 5,488 → fused 932; all
932 fresh-CNF CakeLRATs. The critic confirmed this limited scope in
`ralph/critic/round_008.md`. Fusion maintains full fixed-set lower and
upper graphs in the same labels across all four omissions, with exact
degree rows and separately checked window steps. Six-vertex calibration
preserves all solutions on 67 controls and rejects 12 infeasible ones.
Terminal work ~0.55 core-h; intentionally stopped broad pilot ~0.24
core-h is not a TIMEOUT. All old wrappers collected before round 9.
See `shared74_round8.md` and `scratch/E/r8_shared/freeze.final.2.sha256`.

## Round 9 archive (2026-11-22)

Mixed core 4 only: 17,840 projections / 110,716 lifts. Graph-only
2,519 → marked 14 → fusion 0; all 14 marked survivors also have
fresh-CNF CakeLRATs. The critic confirmed the scoped exclusion in
`ralph/critic/round_009.md`. Terminal 88.55 CPU-s; no running jobs.
See `shared74_round9.md` and `scratch/E/r9_shared/freeze.4.sha256`.

## Round 10 archive (2026-11-22)

Critic confirmed (round 010) mixed cores 12, 14, 10 and 11 only,
at `(2,32,t=4,δ(W)≥2,e(W)=11)`, `(10,10,11,11)`, universal
`δ(G)≥5` and all-graph E-021. 73,627 projections/341,854 lifts,
20 fresh CNF/CakeLRATs, 314.99 CPU-s; see `shared74_round10.md`
and `scratch/E/r10_shared/freeze.{12,14,10,11}.sha256`. Exact
labelled query-cache pilots on cores 9/18 produced byte-identical
receipts but only 2.8% scanner CPU reduction. No surviving jobs.

## Round 12 archive (2026-11-22)

Critic confirmed E-032, mixed core 16 only under E-021 (all graphs)
and universal `δ(G)≥5`. The 25 first branches (2 empty) bind 98,448
projections and 834,106 lifts; all 107 terminal width-eight CNFs have
fresh generation and CakeLRAT. Terminal 0.31636 core-h. Roster pilot
rejects 31/107 and 6/42 archived heavy-core sample IDs, but was slower
as a scan prefilter. See `shared74_round12.md` and `scratch/E/r12_shared/`
for exact receipts, proof streams, freeze files, and `jobs.tsv`. All 52
old wrappers were collected at start of round 13; none live or stopped.
# Round 13 handoff (archived in round 14)

The critic accepted core 17 in `ralph/critic/LATEST.md` round 14.
Scope: mixed saturated `(2,32,4)`, `δ(W)≥2`, `e(W)=11`,
`(10,10,11,11)`, universal `δ(G)≥5`, E-021 all-graph premise;
all four omissions and K=6,7,8. The core had 27 first branches,
193,365 projections, 2,135,171 lifts and 262 fresh original-CNF
CakeLRATs. Both ordered replays checked. Cost 0.36433 core-h main,
0.62728 with unchanged Python audit; all 98 wrappers collected.
`shared74_round13.md`, `scratch/E/r13_shared/freeze.17.sha256`.
Native validator price reduced 3,530→1,508 CPU-s; width-three pilot
129/129 checked but not used for closure. Seven mixed cores remained.

## Round 14 archive (2026-11-22)

The critic accepted core 5 in `ralph/critic/LATEST.md` round 15.
Same f32/t4/eW11, δ(W)≥2, all-graph E-021 and universal δ(G)≥5,
mixed (10,10,11,11), all four omissions, K=6,7,8. 37 first
branches (none empty), 194,552 projections and 2,204,013 lifts;
all 167 original-width CNFs freshly rebound and CakeLRAT checked.
Main path 0.34909 core-h, all 75 workers 0.37297 core-h. Pilot 14/14
width-three proofs, not used in that production. No jobs survived.
`shared74_round14.md`, `scratch/E/r14_shared/freeze.5.sha256`.
