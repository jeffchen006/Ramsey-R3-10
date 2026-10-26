# satcore: validation and timings

Solver: `satcore/bin/satcore` (see `notes/status/satcore.md` for CLI/API).
CaDiCaL 3.0.1 (commit c60730422e75, from `tools`), g++ 11.4 -O3 -march=native.
All times: wall clock, 1 thread, one CPU of 52-59, `nice -n 5`; machine shared with other jobs.
Every found graph was checked with `tools/check_graph.py --k K` (independent code).

## 1. Correctness tests
| test | result |
|---|---|
| `bin/test_core`: propagator vs brute force (n=8..14, k=3..6, random levels, backtracks, also random pair->variable maps) | soundness of every conflict/propagation + completeness at every fixpoint: all ok |
| `difftest.py`: 550 random small instances (n=7..13, k=3..5, random extra clauses, lex, mtf): modes up / up --no-props / cegar / --keep-lazy vs eager full CNF on cadical | 0 mismatches (400 UNSAT-heavy + 150) |
| cardinality (totalizer) and --codeg-max: count all labelled (3,4,7)-graphs (13842) and filtered counts vs encoded runs | all counts equal |
| symmetry breaking soundness, iso classes (networkx) of enumerated solutions | (3,4,7): 9 classes with no SB, with --lex, with fix-nbhd split; (3,6,17): --lex gives 7 = McKay r36_17 (MTF: 2 = 2); (3,7,22): --lex --mtf gives 18 = MTF graphs in McKay r37_22 |
| --pairmap with circulant maps | (3,5,13) SAT (3 labelled), (3,9,35) SAT (4 labelled, check_graph ok), circulant (3,5,14), (3,7,22), (3,8,27) UNSAT |
| proofs: --proof --lrat on (3,6,18), (3,7,23) with --lex --mtf | lrat-check VERIFIED; `cert`: sections regenerated, VeriPB/CakePB for lex+MTF, cake_lpr VERIFIED |
| `--lex-all` (all pairs i<j) vs `--lex` | identical labelled solution sets on (3,6,17), (3,7,22): no gain |

Note: plain eager CNF (no symmetry breaking) for (3,5,14) on cadical does not finish in 300 s; with `--lex` it takes 0.00 s.

## 2. Validation: SAT at n = R-1, UNSAT at n = R
| k | n | answer | options | time | conflicts |
|---|---|---|---|---|---|
| 4 | 8 | SAT | (none) | 0.00 s | 0 |
| 4 | 9 | UNSAT | (none) | 0.09 s | 9.5e3 |
| 5 | 13 | SAT | --lex | 0.00 s | 239 |
| 5 | 14 | UNSAT | --lex | 0.00 s | 334 |
| 5 | 14 | UNKNOWN | (none) | > 600 s | > 1e7 |
| 6 | 17 | SAT | --lex | 0.00 s | 290 |
| 6 | 18 | UNSAT | --lex / --lex --mtf | 0.08 s / 0.02 s | 6011 / 558 |
| 7 | 22 | SAT | --lex / --lex --mtf | 0.17 s / 0.28 s | 4950 / 5667 |
| 7 | 23 | UNSAT | --lex / --lex --mtf | 59 s / 2.0 s | 1.37e6 / 4.3e4 |
| 8 | 27 | SAT | --lex --mtf | 0.60 s | 8583 |
| 8 | 28 | UNSAT, case Delta=5 | --lex --mtf --fix-nbhd 5 --deg-max 5 --deg-min 5 | 0.01 s | 61 |
| 8 | 28 | UNSAT, case Delta=6 | same with 6 | 0.12 s | 814 |
| 8 | 28 | case Delta=7 | same with 7 | UNKNOWN at 3600 s | 1.79e7 |
| 8 | 28 | case Delta=7 | same + --codeg-max 5 | UNKNOWN at 3600 s | 5.8e6 |
| 8 | 28 | case Delta=7 | 64 lookahead cubes (depth 6, 240 s to make), 3 CPUs, 1800 s/cube | stopped: no cube done in 30 min | |
| 8 | 28 | case Delta=7, 4 h limit | --lex --mtf --fix-nbhd 7 --deg-max 7 --deg-min 5 | (running, CPU 52, from 21:19) | |
| 8 | 28 | 7-regular | --lex --mtf --fix-nbhd 7 --deg-min 7 --deg-max 7 | UNKNOWN at 3600 s | 1.5e7 |
| 8 | 28 | 7-regular | same + --codeg-max 5 | UNKNOWN at 3600 s | 7.1e6 |
| 8 | 28 | no split | --lex / --lex --mtf | UNKNOWN at 3600 s | 2.1e7 / 1.9e7 |

(3,8,28) case split: Delta <= 7 (N(v) independent), delta >= 28 - R(3,7) = 5; MTF is WLOG.

Comparison with SMS (agent `sms`, notes/status/sms.md, same constraints, 1 CPU): Delta=7 case SMS 4269 s
(satcore: > 3600 s); 7-regular SMS 1846 s (satcore: > 3600 s); D=5/6: SMS 0.38/0.58 s, satcore 0.01/0.12 s;
(3,8,27) SAT: satcore 0.6 s, SMS 431 s with canonicity, 1.3 s without. So: SMS is stronger on hard UNSAT,
satcore on SAT and easy cases.

## 3. k = 9, k = 10 (1 h each, 1 CPU)
| instance | options | result |
|---|---|---|
| (3,9,35) SAT (unique graph, C35(1,7,11,16)) | --lex --mtf | UNKNOWN at 3600 s (1.7e7 conflicts) |
| (3,9,35) | --lex --mtf --fix-nbhd 8 --deg-max 8 --deg-min 7, seeds 1, 2 | UNKNOWN at 3600 s (both) |
| (3,9,35) | same, seed 4, 6 h | (running, CPU 57) |
| (3,9,35) | --phase-graph = the solution (relabelled), no SB | SAT 0.00 s; with 5%/10%/20% of pairs flipped: UNKNOWN at 120 s (also with forcephase=1, rephase=0) |
| (3,9,36) UNSAT, 8-regular (delta >= 36-R(3,8)+1 = 8, Delta <= 8) | --lex --mtf --fix-nbhd 8 --deg-min 8 --deg-max 8 | UNKNOWN at 3600 s (1.76e7 conflicts) |
| (3,10,39) SAT | --lex --mtf | UNKNOWN at 3600 s |
| (3,10,39) SAT | --lex --mtf --fix-nbhd 9 --deg-max 9 | UNKNOWN at 3600 s |
| (3,10,39) SAT, 6 h | --lex --mtf --fix-nbhd 9 --deg-min 8 --deg-max 9 --codeg-max 6 (CPU 59); same --config sat --seed 3 without codeg (CPU 53); --lex --mtf --config sat --seed 4 (CPU 58) | (running) |
| (3,10,39), automorphism = three 13-cycles | --pairmap (57 orbit vars) | UNSAT 1700 s (no certificate) |
| (3,10,39), automorphism = thirteen 3-cycles | --pairmap (247 orbit vars) | UNKNOWN at 1800 s |

Remark (3,9,36): with the literature value e(3,8,27) = 85 ([GR] Table 3, see notes/edge_tables.md Sec 2), an 8-regular
(3,9,36)-graph has e(H_0) = 144 - 64 = 80 < 85: a counting contradiction. But CDCL does not find it: the same run
plus `--h-edges-min 85` is still UNKNOWN after 60 s (1.4e5 conflicts). Counting arguments must be done outside SAT
(as `cases` does) and given as case restrictions.

## 3b. Side by side: satcore vs SMS vs MathCheckRamsey (1 CPU each unless noted)
SMS numbers: agent `sms` (notes/status/sms.md, messages 2026-10-24). MathCheckRamsey = Li, Duggan, Bright, Ganesh,
IJCAI 2025 (arXiv 2502.06055), github.com/ConDug/MathCheckRamsey commit 84b2aefc (2025-04-14), cadical-ks
(CaDiCaL 1.9.4 fork + orderly-generation CAS), built by `tools`; run with `./main.sh -n [-d lo -D hi] n 3 k`
(no cubing; its default encoding includes MTF; eager k-set clauses; includes a 100000-conflict simplification
step and DRAT + permutation checks). Driver: satcore/mathcheck.sh, logs runs/satcore/mc_*.log.

| instance | satcore | SMS | MathCheckRamsey |
|---|---|---|---|
| (3,7,23) UNSAT | 2.0 s (--lex --mtf); 59 s (--lex) | 1.0 s | 12.4 s solve; 42 s wall incl. generation + DRAT/perm check |
| (3,8,27) SAT | 0.6 s (--lex --mtf) | 431 s with canonicity; 1.3 s without | no graph in the 450 s simplification phase; (running) |
| (3,8,28) Delta=5 / Delta=6 | 0.01 s / 0.12 s | 0.38 s / 0.58 s | - |
| (3,8,28) Delta=7 (deg 5..7, N(0) fixed, MTF) | UNKNOWN at 14400 s (5.0e7 conflicts) | 4269 s | - |
| (3,8,28) 7-regular, MTF, N(0) fixed | UNKNOWN at 3600 s | 1846 s | `-d 7 -D 7 28 3 8`: timeout at 14400 s |
| (3,8,28) full | UNKNOWN at 3600 s (--lex [--mtf]) | ~71 min (lead) | run by `cert` on CPUs 70-71; paper: 59 h for R(3,8) |
| (3,9,36) 8-regular, MTF, N(0) fixed | UNKNOWN at 3600 s | 724 s | not run: eager encoding needs C(36,9) = 9.4e7 clauses of 36 literals (~10 GB CNF, Python writer) |
| (3,9,35) SAT | UNKNOWN at 3600 s (3 runs) | no result in 38-130 min | - |
| (3,10,39) SAT | UNKNOWN at 3600 s (several configs) and at 21600 s (deg 8..9, codeg<=6) | no result in 38-130 min | - |

Reading: for hard UNSAT, SMS (complete canonicity in the propagator) is clearly the strongest of the three here;
satcore (static lex) is fastest on SAT and on easy cases. MathCheck's eager k-set encoding does not scale to k = 10
(C(40,10) = 8.5e8 clauses).

## 3c. Local edge bound (--hv-min), negative result
`--hv-min m:L,...` adds, for every v and degree d, deg(v) <= d -> e(G - N[v]) >= L(n-1-d) (counts brute-force checked
on all labelled (3,4,7)-graphs). It does not help CDCL on counting instances:
(3,9,36) 8-regular + 27:85 (e(3,8,27) = 85): UNKNOWN at 300 s (pure counting contradiction, e(H_v) = 80);
(3,7,19) with <= 37 edges: SAT in 8.7 s without it, UNKNOWN at 300 s with it; <= 36 edges: UNKNOWN both.

## 4. Profile
perf on (3,7,23) --lex: CaDiCaL propagate 56%, other CaDiCaL search ~40%, propagator (Core::process + search) ~3%.
Decision order via cb_decide (--decide row+/row-/colex+): no gain ((3,7,23) --lex --mtf 1.7-2.3 s vs 2.3 s; --lex alone worse).
CaDiCaL options (--config unsat/sat, phase=0, chrono=0, elim=0, inprocessing=0, --keep-lazy, --no-props): 53-104 s vs 59 s default. No big gain.
