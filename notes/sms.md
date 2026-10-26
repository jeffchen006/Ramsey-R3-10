# SAT Modulo Symmetries (SMS) for (3,k)-graphs — evaluation (agent sms)

Status: v1 final, 2026-10-25.

## 1. What SMS is and what I used

- SMS = CaDiCaL (IPASIR-UP fork) + a "minimality check" propagator: during search it checks if
  the partially assigned graph can still be lex-canonical; if not, it adds a clause (with a
  permutation witness). Result: only one graph per isomorphism class is generated.
  Paper: Kirchweger, Szeider, "SAT Modulo Symmetries for Graph Generation and Enumeration",
  ACM TOCL 25(3) Art. 18 (2024), doi 10.1145/3670405 (local: data/papers/KirS_TOCL2024.pdf).
  Their Ramsey results (Sec. 8, Table 9): all R(3,5,n) (1029 graphs, 0.24 s) and all R(4,4,n)
  (3,432,184 graphs, 883 s); eager encoding of independent sets/cliques; no larger R(3,k).
- Code: github.com/markirch/sat-modulo-symmetries, commit 63958bd (2026-08-10), CaDiCaL fork
  2.1.3 (submodule cadical_sms @ b023aaf). Own build in sms/sms-src (gcc 11.4, Release).
  The repo ships NO Ramsey example except pysms `--ramsey a w` (eager: all C(n,a) clauses).
- Canonical form: lex-MIN (0 < 1) of the row-wise upper-triangle edge vector
  (e(0,1), e(0,2), ..., e(0,n-1), e(1,2), ...); variable of e(i,j) = its position (1-based).
  Permutation witness in `--sym-break-clauses` JSON: H'(i,j) = H(perm[i], perm[j]); the clause
  forbids partial graphs where H' < H for every completion (checked: sms/check_ext.py; cert's
  VeriPB check agrees: lex-min 46/46, lex-max 0/46).

### My additions (patch in sms/sms-src; `git -C sms/sms-src diff` + 3 new files)
1. `--forbid-independent-set k` (src/graphPropagators/independentSet.{hpp,cpp}): LAZY
   "no independent k-set". On each propagation call (frequency 1, option
   `--independent-set-frequency`) it searches a k-clique in the graph of pairs assigned
   "non-edge" (bitset branch and bound, greedy colouring bound). If found, it adds the clause
   "some pair of this k-set is an edge". Exact, because it is also run on every full assignment.
2. `--proof-log FILE` (src/proofLogTracer.hpp): CaDiCaL Tracer that logs original clauses
   (input AND external clauses from SMS propagators) with their IDs, and derived clauses with
   LRAT hints. Needed because stock `--lrat-output` omits the external clauses, so the
   LRAT file refers to undefined clause IDs and `lrat-check` fails (tested: "NOT VERIFIED").
3. Tools (sms/): gen_ramsey.py (encoder), lratlog2lrat.py (log -> CNF + LRAT + list of
   external clauses), check_ext.py (independent check of external clauses), edges2g6.py,
   bench.sh, run1.sh, scale_unsat.sh, reg_series.sh.

### Encoder (sms/gen_ramsey.py)
- Triangle clauses (eager, C(n,3)); independent sets eager (`--eager-is`, C(n,k) clauses) or
  lazy (smsg `--forbid-independent-set k`).
- Degree / edge-count bounds: Sinz sequential counters (tested: (3,6,15) with 4 bound sets gives
  the same counts as filtering the full list: 239, 7145, 55315, 265).
- `--mtf`: maximal triangle-free (every non-adjacent pair has a common neighbour); WLOG for an
  existence search (adding edges cannot raise alpha). Tested on (3,5,12/13).
- `--fix-nbhd d`: N(0) = {1..d}; must be run with `--initial-partition 1 d n-1-d` so that SMS
  only uses partition-preserving permutations. Tested: rooted counts for (3,6,16), d = 3,4,5:
  1333, 15130, 20106 = number of vertex orbits of degree d (pynauty) over all 2576 graphs.

## 2. Reproduction of known counts (task step 2)

All runs: 1 CPU (taskset, nice 5), AMD/Intel host of the team, smsg with `--cutoff 0` (exact up
to isomorphism; the default cutoff can print isomorphic copies), lazy IS unless "eager".
Every output graph was checked: nauty `shortg` (no isomorphic duplicates) and
`tools/check_graph.py --k K` (triangle-free, alpha < K). Reference counts: McKay, "Ramsey
graphs" data page, users.cecs.anu.edu.au/~bdm/data/ramsey.html (read 2026-10-24).
Raw table: runs/sms/sweep_small.txt.

| (3,k,n) | count (McKay) | SMS count | lazy s | eager s |
|---|---|---|---|---|
| (3,5,10..13) | 313, 105, 12, 1 | same | <= 0.04 | <= 0.04 |
| (3,5,14) | 0 | 0 | 0.01 | 0.02 |
| (3,6,13) | 275086 | 275086 | 21.4 | 20.4 |
| (3,6,14) | 263520 | 263520 | 27.2 | 25.5 |
| (3,6,15) | 64732 | 64732 | 7.1 | 6.7 |
| (3,6,16) | 2576 | 2576 | 0.74 | 0.74 |
| (3,6,17) | 7 | 7 | 0.13 | 0.22 |
| (3,6,18) | 0 | 0 | 0.05 | 0.14 |
| (3,7,21) | 1118436 | 1118436 | 743 | - |
| (3,7,22) | 191 | 191 | 10.7 | 19.6 |
| (3,7,23) | 0 | 0 | 1.04 | 5.3 |

Lazy and eager are equal for k <= 6; lazy is 2-5x faster at k = 7 and the only option at k >= 9
(eager C(n,k) clauses: (3,9,35) 70.6e6, (3,10,40) 8.5e8 clauses of 36/45 literals).

## 3. Harder cases and scaling (task step 3)

1 CPU each, lazy IS, no proof log unless stated. "no result" = stopped or time limit, no answer.

### UNSAT at n = R(3,k)
| instance | encoding | time |
|---|---|---|
| (3,5,14) / (3,6,18) / (3,7,23) | plain | 0.01 / 0.05 / 1.0 s |
| same | + deg bounds / MTF / both | k=7: 1.1 / 1.8 / 1.6 s (no gain at small k) |
| (3,8,28) | plain | no result at 79 min (also 47 min dup.) |
| (3,8,28) | MTF | no result at 77 min |
| (3,8,28) | MTF, deg 5..D, D = d(0) max degree, N(0) = {1..D}, partition 1 D 27-D | D=5 0.38 s, D=6 0.58 s, D=7 4269 s: total ~71 min |
| (3,8,28) | 7-regular, MTF, N(0) fixed | 1846 s |
| (3,9,36) | 8-regular, MTF, N(0) fixed | 724 s |

delta >= 5 in the (3,8,28) split is n - R(3,7) = 28 - 23. 8-regularity of a (3,9,36)-graph is a
known lemma (cited by Li et al.); the 8-regular run is a calibration of the cube-R shape, not a new
proof of R(3,9) = 36.

Comparison: Li, Duggan, Bright, Ganesh, IJCAI 2025 (arXiv:2502.06055): SAT+CAS (MathCheck)
R(8,3) sequential 11 h, R(3,8) 59 h, R(9,3) 26 h wall with parallel cube-and-conquer; plain
CaDiCaL > 7 days. satcore (CaDiCaL 3.0.1 + lazy IS + static lex, notes/satcore.md): (3,8,28)
D=7, 7-regular, 8-regular (3,9,36): all UNKNOWN at 1 h. So SMS symmetry breaking is the main gain
on hard UNSAT cases.

### Edge-minimum UNSAT ("no (3,k,m)-graph with <= E edges", deg <= k-1, proof log on)
| (k,m,E) | time | proof |
|---|---|---|
| (7,17,24), (7,18,29) | 1.6 s, 4.4 s | certified end to end by cert |
| (7,19,36), (7,20,43) | 24.3 s, 151 s | converted, given to cert |
| (8,22,41) | 802 s | converted (LRAT 3.4 GB), given to cert |
| F1 (8,23,46), (8,24,52) | 3094 s, 8970 s | converted, cert certifies |
| F1 (8,25,58), (8,26,64), (8,27,70) | running | |
Split by maximum degree (N(0) fixed) did NOT help F1: (8,23,46) D=5 alone took 3991 s.

### Enumeration and SAT-finding
| instance | result |
|---|---|
| (3,7,21) all graphs | 1,118,436 in 743 s (= McKay) |
| (3,8,27) all graphs (477,142) | >= 137 graphs in 2494 s, stopped: too slow |
| (3,9,35) all graphs (1) | no result at 2.2 h |
| (3,9,35) 8-regular MTF N(0) fixed, find | no result at 59 min |
| (3,9,35) --no-SMS (lazy IS only), find | no result at 38 min |
| (3,10,39) find, SMS / --no-SMS | no result at 38 min / 38 min |
| (3,8,27) first graph | SMS 431 s; --no-SMS 1.3 s; satcore 0.6 s |
SMS canonicity makes SAT-finding much harder (the solver must find a lex-min labelling).
For constructions use other tools.

## 4. What SMS adds for n = 40 (task step 4)

- Degree constraints / fixed neighbourhood: supported via DIMACS counters + `--initial-partition`
  (exact, tested with rooted counts). This (max-degree split, N(0) fixed) is what made (3,8,28)
  and (3,9,36) fast.
- "No independent 10-set": eager is impossible (C(40,10) = 8.5e8 clauses of 45 literals). My lazy
  propagator works (clique search in the assigned-non-edge graph, < 7% of run time in all hard runs).
  A "propagate the last pair" variant was correct but slower on small cases; not used.
- Proofs: stock LRAT is unusable (external clauses missing). With `--proof-log` + sms/lratlog2lrat
  + independent checks of IS/SYM clauses (sms/check_ext.py; cert: Lean sbcheck, VeriPB/CakePB),
  the full chain is verified (cert). Cost ~0.8x solve CPU; proofs ~4 MB per solve-second.
- Comparison with satcore (CaDiCaL 3.0.1 + lazy IS + static lex): satcore is faster for
  finding graphs and easy cases; SMS is much faster on hard UNSAT ((3,8,28) D=7, 7-regular,
  8-regular (3,9,36): SMS 724-4269 s, satcore UNKNOWN at 1 h).

## 5. Recommendation

- Use SMS as the UNSAT engine for structured cubes up to about the (3,9,36) 8-regular level
  (minutes to hours per cube), with proof log and cert's checks. Solve cubes as unit clauses.
- Do NOT use SMS to search for graphs (canonicity makes SAT-finding slow) or for large enumerations.
- For the 40-vertex non-existence search: NOT viable at the present cube level. Probe estimates
  (notes/core_plan.md Sec 4): cube R >= ~1e9 CPU-s likely (mean 8e14), C1 mean 1e10..5e10 CPU-s,
  max-codegree sub-cubes no better. It becomes viable only if new proven structure cuts the cubes
  by several orders of magnitude (to the size of the (3,9,36) 8-regular case, ~1e3 CPU-s per cube,
  times a feasible number of cubes). The probe tools (sms/knuth_probe.py, sms/probe_loop.sh) can
  re-estimate any new cube in a few CPU-hours.
