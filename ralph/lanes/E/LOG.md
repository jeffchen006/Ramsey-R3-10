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
