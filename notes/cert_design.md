# Certificate chain for "no (3,10,40)-graph" (R(3,10) = 40)

Author: agent `cert`. Date: 2026-10-24. Status: v3. v1 reviewed by `critic` (notes/critic.md
Review 11: sound for the demo, gaps X3, X4, X5 for n = 40); v2 closes X3-X5 (sec. 1.2, 1.1, 3.7).
Review 14 on v2: X4 confirmed; P1 (check_pbp skipped def_order loosely) and P2 (D bounds read
from solver tags) found; v3 fixes both (sec. 1.2, 3.7).
Code: `cert/` (README in each script header). Demo results: `cert/demo/*/RESULT.txt`.
Prior art: `cert/lit_certified_proofs.md` (how DuLBG, Keller, Schur 5, empty hexagon,
VeriPB/CakePB, SMS and R(4,5) handled each link).

## 0. Goal and principle

Claim to certify: no graph on 40 vertices has no triangle and no independent 10-set.

Principle. Every step after the definition is either
1. a propositional step, checked by a formally verified checker (cake_lpr for LRAT,
   CakePB for VeriPB proofs), or
2. a constraint that every (3,10,40)-graph satisfies ("implied constraint"), with a hand
   proof formalized in Lean (agent `lean`), plus a list of outside facts it uses, or
3. glue that a short script checks (hashes, file equality, "summary ends with empty clause").

No step trusts the search code (CaDiCaL, SMS, satcore, cubers, nauty). Search code
only produces hints: cubes, clauses, permutations, proofs. Checkers re-check all of them.

## 1. The chain for n = 40

Notation. Edge variable x(i,j), 0 <= i < j < 40, 780 variables.
TRI = 9,880 triangle clauses. IS = C(40,10) = 847,660,528 independent-set clauses
(never written in full). F_def = TRI + IS.

| link | statement | tool / checker | trust | demo status |
|---|---|---|---|---|
| (a1) | models of F_def = (3,10,40)-graphs | two independent generators (`cert/gen.py`, satcore/sms) + exhaustive test n <= 7 (`cert/test_encoding.py`); Lean: target statement and encoding | hand + test; Lean planned | done (test passes for 9 (n,s) pairs) |
| (a2) | implied constraints D hold in every (3,10,40)-graph (MTF-free ones: deg <= 9; needing outside facts: deg >= 4 or 5, e >= 159/161, Theorem A ...) | Lean (`lean`, `cases` lemmas); CNF form of D derived in a 2nd VeriPB proof (sec. 3.7) | Lean kernel + outside facts (link g) | Lean has L1, L2, L4, deg bounds (status/lean.md); CNF of degree bounds certified (sec. 3.7) |
| (e1) | MTF: F_def SAT => F_def + MTF SAT | VeriPB `red` steps (no order), checked by CakePB | CakePB | done for n = 14, 18 (`cert/mtf.py`, demo `--mtf`) |
| (e2) | symmetry breaking: F SAT => F + SB SAT | VeriPB `dom` steps, one lex order for ALL SB clauses (static, SMS, cube-defining), checked by CakePB; per-clause re-check `cert/check_sb.py` | CakePB | done: demo n = 14, 18; SMS (3,5,14); satcore lex (3,6,18), (3,7,23) |
| (b) | case split: cubes c_1..c_m | any cuber (untrusted); cubes are clauses of the summary file | none | done (row-0 cubes) |
| (c) | cube cover: F_base + NOT c_1 + ... + NOT c_m UNSAT | LRAT, cake_lpr (last line of summary = empty clause) | cake_lpr | done |
| (d) | each cube: F_j + c_j UNSAT | LRAT per cube, cake_lpr (two-level summary mode or one run per cube) | cake_lpr | done |
| (f) | lazy clauses (IS clauses made during search) are valid | `cert/check_cnf.py` (exact shape check: s vertices, all C(s,2) pairs, positive) | 120-line Python | done |
| (g) | outside computations | list in sec. 5; each one certified, re-computed independently, or cited | varies | list written |

Logical composition (all links):
F_def SAT
 => F_def + MTF + SB SAT                              (e1, e2: CakePB proof 1, output EQUISATISFIABLE)
 => F_def + MTF + SB + D_PB SAT                       (a2: D holds in every model of F_def + MTF)
 => F_def + MTF + SB + D_PB + D_cnf SAT               (CakePB proof 2: aux definitions + CNF of D)
 => some cube c_j with F_def + MTF + SB + D + c_j SAT (c: cover proof)
 => F_j + c_j SAT, F_j = TRI + MTF + SB + D_cnf + L_j  (f: F_j is a subset of the line above, check_cnf)
 => contradiction                                     (d: cake_lpr).

### 1.1 Why implied constraints come after the VeriPB step
`dom`/`red` obligations are checked against the core formula. An implied constraint such
as "deg(v) >= 6" (needs MTF + M1) or "deg(v) <= 9" is true in every model of F_def + MTF,
but VeriPB cannot prove it with short steps (it needs the IS clauses as a whole). So:
the VeriPB proof starts from TRI (+ MTF definitions), and D is added after. This is sound
because D holds in every model of F_def + MTF (Lean), so in every model of
F_def + MTF + SB. D must NOT be used by a `dom` step as core, unless D is invariant under
the witness permutations (true for symmetric D: degree bounds on all vertices, edge count).
Two VeriPB proofs (critic X5): proof 1 (input TRI) derives MTF + SB; proof 2 (input =
output of proof 1 + D as PB constraints) derives the CNF of D (aux definitions by `red`,
clauses by `pol` + `rup`, sec. 3.7). D upper bounds cannot be in the core of proof 1:
an MTF `red` step adds an edge and VeriPB cannot show deg <= 9 still holds.
Critic X4: D is true only in triangle-free models, so the VeriPB input must contain ALL
C(n,3) triangle clauses. `check_cnf.py --opb --require-all-tri in.opb` checks this
(exactly, as a set; one missing clause -> FAIL). All pipelines run it.

### 1.2 IS clauses and the VeriPB input (meta-lemma M-IS)
VeriPB cannot load 847M IS clauses. The VeriPB input is TRI (+ symmetric D, if used).
Meta-lemma M-IS (hand; Lean target): let P be a VeriPB proof that is valid for core
formula C. Let every witness of P either (i) act on edge variables as a vertex permutation
(aux variables renamed with it), or (ii) map edge variables only to themselves or to 1
(MTF steps: "add an edge"). Let S = IS_all (all positive s-set clauses). Then P is valid
for core C + S, with the same output plus S.
Proof sketch: RUP steps are monotone in the database. For `red`/`dom` the new
obligations are w(D) for D in S. Case (i): w(D) is again an s-set clause, so it is in S
(syntactic match). Case (ii): w(D) is D or is satisfied (a literal set to 1); D has no
aux variable. Order obligations do not change. Deletions: P deletes no input clause.
Claims that are not implied (critic Review 18, Q1): for an edge-bound claim "edges <= E"
the claim constraint is part of S (closed under vertex permutations) but NOT under case (ii):
an "add an edge" witness breaks it. So claim runs must use pure vertex-permutation witnesses
and no MTF: `check_pbp.py --perm-only` (condition P) and satcore_cert.py refuses
--claim-edges-max with an MTF section; sms_card_cert.py uses --perm-only for proof 1.
"Valid for C + S" holds up to the constraint-ID shift: the proof text for input C + S is
the text for C with every numeric ID > |C| increased by |S| (labels and relative IDs do
not change). This needs: P never names an input constraint by a numeric ID.
Machine check of the conditions (critic X3): `cert/check_pbp.py` parses the .pbp and
checks (W) every `red`/`dom` witness maps edge variables by ONE vertex permutation, or to 1
(aux variables free); (D) no `del`/`delc`; (I) no numeric ID <= |C|; (R) only the allowed
rules (no `a`). It passes on all 15 proofs of sec. 2 and 3; it rejects 5 broken variants
(edge -> 0, a witness not induced by a vertex permutation, `del`, a hint to an input ID, `a`).
v3 (critic P1): a `def_order` block is parsed to its own matching `end ;` (sections vars,
spec, def, transitivity, reflexivity; proof/proofgoal ... qed); inside, only variable lists,
constraints starting with a coefficient, and pol/rup in proof goals are allowed; a missing
`output EQUISATISFIABLE FILE` is an error. Rejects: a second def_order followed by a hidden
`del`, `delc` inside a def section, an unclosed block or a proof without output section.
Demo check of M-IS: for n = 14 and 18 the same proof is checked with input TRI and with
input TRI + all IS (both VeriPB and CakePB OK, `cert/demo/r3_*/{veripb,cakepb}_{tri,full}.log`).

Alternative without VeriPB semantics (asked of `lean`, 2026-10-24): a Lean "lex-leader
lemma": for the group Gamma of vertex permutations that fix 0 and N(0) (cube constraints and
Phi are Gamma-invariant), every clause C with a witness pi in Gamma and
P(C, pi): "for all x with x |= NOT C, pi x is strictly better than x" holds in the best
labelling of every Gamma-orbit. P(C, pi) is exactly check_sb.py's exact per-clause test (and
CakePB's `dom` check). Then SB rests on that lemma + the per-clause test, and M-IS is needed
only for the VeriPB-only route. Lean status (lean, 2026-10-24): L1, L2, L4, M0, M1,
Theorem A'', Theorem A (MTF, non-regular), Cover Lemma, Enc.fdef_iff (a1 at graph level) are
proved; M-IS is not. The lex-leader lemma is PROVED (lean/R310/LexLeader.lean,
R310.Files.cover_files_sb, no sorry, 2026-10-24): F1, F2, a (3,10,40)-graph, and SB lists for
the three cubes whose witnesses pi fix 0 and map {1..d} onto itself and satisfy SBValid
(for EVERY edge assignment falsifying C, pi x is strictly better under one fixed val and one
direction) -> some assignment satisfies IS_all + a cube file + all its SB clauses. So for
SB clauses over edge ids (SMS, MathCheck, cert's lex clauses) the chain is: Lean lemma +
per-clause test P (check_sb.py; CakePB as second check; a Lean checker offered by `lean`).
satcore's Codish clauses with e_k aux remain on the VeriPB + M-IS route.
Lean-verified per-clause checker (lean, 2026-10-24): lean/.lake/build/bin/sbcheck FILE, input =
check_sb format with header "c order positions= better= vars= d="; soundness theorem
R310.SB.checkSB_sound gives exactly the hypotheses of cover_files_sb (pi in Gamma_d and
SBValid). Trusted: its 100-line parser and the Lean compiler. 0.26 ms/clause (n = 40).
cert's samples: cert/samples/sb_S8_good.wit -> "s VERIFIED 200 clauses"; sb_S8_bad.wit ->
exactly the 2 broken lines FAIL. Difference to check_sb.py: tautological clauses are accepted
(vacuously valid); aux ids are rejected. So for n = 40 SB clauses over edge ids the chain is
fully machine-checked: sbcheck (verified) + cover_files_sb (Lean); check_sb.py stays as an
independent second check; VeriPB/CakePB only on samples.

### 1.3 One order for all symmetry breaking
All `dom` steps must use the same order. Then the order-optimal labelling of any model
satisfies every SB clause. [DuLBG] uses static row-comparison constraints plus a
column-wise canonical form and states no compatibility argument. cert checked that they
ARE compatible: MathCheck's `cubic` clauses (row_i <=lex row_j, all i < j) are the
lex-leaders of the transpositions (i j) under lex-MIN of the colex edge vector, the order of
its CAS clauses (sec. 3.8: VeriPB derives both under that one order; brute force n <= 6).
- SMS order: lex-MIN of the row-wise edge vector, 0 < 1 (confirmed with `sms`: 46/46
  clauses valid under lex-min, 0/46 under lex-max).
- `cert` demo order: lex-MAX of the row-wise vector; canonical vertex 0 then has maximum
  degree and N(0) = {1..Delta}.
- With lex-min, canonical vertex 0 has MINIMUM degree, N(0) = the last d vertices.
Pick the order so that the case split fixes what the canonical form fixes (sec. 3.3).

### 1.4 Cubes and the cover in one verified run
(critic Review 11 confirmed the finding below independently: missing range -> "Intervals do
not reach k", changed summary or F -> "Incorrect prefix"; all exit 0.)
cake_lpr two-level mode: `cake_lpr F summary i-j proof` and `cake_lpr F summary -check out`.
summary = lines NOT c_1, ..., NOT c_m, then the empty clause. Line j is derived from
F + lines < j by LRAT proof j. The last proof is the cover proof.
FINDING (tested): `-check` prints "s VERIFIED INTERVALS COVER 0-k" also when the summary
has NO empty clause. It certifies only "F SAT => F + all summary lines SAT".
The glue must check that the summary contains the empty clause (`cert/demo.py` does).
Also: cake_lpr and cake_pb exit 0 on failure (`tools`). Glue must test the stdout line.
For n = 40, the per-cube lazy clauses L_j differ per cube. Two options:
(i) F = TRI + SB + D_cnf + union of all L_j (one file; size = sum |L_j|), or
(ii) per cube: `cake_lpr F_j proof_j` with F_j = F_base + L_j + units(c_j), and one cover
run on F_base + all NOT c_j; glue checks F_j = F_base + L_j + units(c_j) (byte compare of
the F_base part) and check_cnf on L_j. Option (ii) scales; option (i) has less glue.

### 1.5 Proof transformation for cubes
CaDiCaL refutes F + units(c_j). `cert/demo.py:transform_lrat` turns this into an LRAT
derivation of NOT c_j from F: add NOT c_j to each lemma, drop hints to the unit clauses,
drop lemmas that contain a cube literal, drop deletions of input clauses (cake_lpr range
mode needs all input and summary clauses at the end). cake_lpr re-checks the result.
(drat-trim cannot do this: it requires a refutation, "ERROR: no conflict".)

## 2. Demo results (2026-10-24, CPUs 68-71)

`taskset -c 68-71 nice -n 5 cert/venv/bin/python cert/demo.py N S 1`

| instance | cubes | SB clauses (static + dynamic) | lazy IS | VeriPB full / tri | CakePB full / tri | LRAT | cake_lpr | result |
|---|---|---|---|---|---|---|---|---|
| (3,5,14) | 14 + cover | 454 | 642 | 0.2 s / 0.0 s | 3.4 s / 2.4 s | 0.5 MB | 0.4 s | COVER 0-15, empty clause present |
| (3,6,18) | 18 + cover | 1828 | 4073 | 8.7 s / 0.2 s | 102 s / 5.8 s | 5.0 MB | 3.8 s | COVER 0-19, empty clause present |
| (3,5,14) + MTF | 14 + cover | 133 | 367 | 0.1 s / 0.1 s | 2.6 s / 1.8 s | 0.2 MB | 0.7 s | COVER 0-15, empty clause present |
| (3,6,18) + MTF | 18 + cover | 535 | 1397 | 3.8 s / 0.5 s | 18.3 s / 4.8 s | 0.5 MB | 2.7 s | COVER 0-19, empty clause present |

MTF rows (`demo.py N S 1 --mtf`): the VeriPB proof first derives 3 x C(n,2) x (n-2) aux
definitions + C(n,2) MTF clauses by `red` (5,859 steps for n = 18), then loads the order and
derives SB by `dom` with witnesses that also rename the aux vars. MTF cut the LRAT size 10x.

Chain per instance: F_full (gen.py) -> check_cnf OK -> lazy search per cube
(`cert/lazy.py`) -> SB list + witnesses -> check_sb OK -> VeriPB/CakePB OK ->
F_cert = TRI + SB + lazy IS -> check_cnf OK -> per-cube LRAT -> cake_lpr ranges -> COVER.

SMS run converted: `cert/sms2veripb.py` on sms/proofs/r3_5_14_lazy.* (patched smsg proof
log): 46 SYM clauses, check_sb OK (lex-min), VeriPB + CakePB OK (input TRI and TRI + IS),
check_cnf: 364 TRI + 215 IS + 46 SYM OK, cake_lpr: s VERIFIED UNSAT. Files: cert/demo/sms_r3_5_14_lazy/.

Positive control (`cert/sat_sanity.py`, same SB and cubes at n - 1):
(3,5,13): 1 SAT cube, (3,6,17): 2 SAT cubes; all graphs pass tools/check_graph.py.
Negative tests: a reversed SB clause -> VeriPB "Proofgoal #1 could not be autoproven";
one IS clause removed from input -> VeriPB fails (formula not symmetric); one triangle
clause changed -> check_cnf FAIL; SB clause with a literal removed -> check_sb FAIL;
summary without empty clause -> detected by glue; "x(0,1) is an edge" offered as a `red`
step with witness x(0,1) -> 1 (not valid) -> VeriPB "Proofgoal 1 could not be autoproven".
Baseline: plain CaDiCaL on F_full (3,5,14), no SB: not solved in 600 s.

## 3. Design decisions for n = 40

### 3.1 Lazy IS clauses (link f)
Each lazy clause must be exactly the C(10,2) = 45 positive edge literals of one 10-set.
The solver writes every external/reason clause once to `ext.cnf` (satcore) or the proof
log (sms). check_cnf rejects anything else. Weakened clauses (supersets) are accepted
only with `--weak` (exact superset test). Cost: about 1 us per literal in Python.

### 3.2 MTF (maximal triangle-free), link (e1)
M0 (`cases`) says: WLOG G is MTF. MTF is NOT a symmetry-breaking step. It is a
satisfiability-preserving strengthening that VeriPB can check with `red` (no order):
1. For each pair (i,j) and each l: introduce aux c(i,j,l) <-> x(i,l) and x(j,l) by two
   `red` steps (witness c -> 0, then c -> 1). This is a full definition.
2. Derive MTF(i,j) = x(i,j) or OR_l c(i,j,l) by `red` with witness x(i,j) -> 1 and
   c(a,b,l) -> (the other edge literal) for every aux whose definition contains x(i,j).
   Obligations: TRI clauses with x(i,j) need "no common neighbour", which follows by UP
   from NOT MTF(i,j) and the reverse definitions; IS clauses are positive (stay true);
   earlier MTF clauses follow by UP. All goals are auto-proved by VeriPB (demo below).
3. Do this BEFORE `load_order`: a `red` step with a loaded order has extra obligations.
   `load_order` then moves MTF to the core. The core is still closed under vertex
   permutations if the witness renames c(i,j,l) with the permutation.
Note: sms encodes only c -> x (one direction). That is fine for search, but the VeriPB
derivation needs both directions; the extra clauses can be kept or deleted after.
Under lex-MAX, "add an edge" is also a `dom` step (val grows), so MTF could even share
the SB order. Under lex-MIN (SMS) it cannot; use `red` as above.

### 3.3 "WLOG vertex 0 has property P" (degree cases, Theorem A)
`cases` uses: some vertex v has (d(v) = 9 and e(H_v) <= t9) or ...; then WLOG v = 0,
N(0) = {1..9}. A relabelling depends on the graph, so it is not one fixed witness.
Two certified ways:
(A) red chain, no order (preferred): add p_v <-> P(v) (PB reified, aux vars), add the
    implied constraint OR_v p_v (Lean, link a2), then for v = 1..39 derive
    "p_0 or not p_v" by `red` with witness = transposition (0 v). Resolution gives p_0.
    Then fix N(0) the same way inside the partition. After this, the core is closed only
    under permutations that fix 0 (and N(0) as a set): VeriPB checks that each SMS witness
    respects this (SMS must run with --initial-partition, as `sms` already does).
    Demo (`cert/wlog_demo.py N S K`, P(v) = deg(v) >= K, reified in the input, plus the
    implied constraint "some p_v"): (3,6,17) K = 5 and (3,5,13) K = 4: VeriPB and CakePB
    OK (16 / 12 `red` steps + `rup p_0` + 15 / 11 `dom` SB steps fixing vertex 0);
    positive control: search with deg(0) >= K and the SB is SAT. Negative test: "p_0" in
    one `red` step with witness (0 1) -> rejected.
(B) one combined order "P(0) first, then lex": every SMS clause must then be valid under
    the combined order; true if all SMS witnesses fix vertex 0.
Not certified: running 545 separate SAT problems "d(0) = 9, e(H_0) <= t9(n), degree
counts n" and combining them by a hand argument, unless the hand argument (degree
distribution list complete + WLOG relabel) is in Lean. The distribution list itself comes
from a program (`cases/degseq.py`) + exact LP certificates (`cases/verify_certs.py`);
the enumeration program is an outside computation (re-run independently by `critic`).
Better: make the distribution cases propositional cubes on counter variables, so the cover
is an LRAT proof (link c) and the LP certificates become PB derivations (VeriPB `pol`).

### 3.4 Enumerated graph lists (gluing inputs, case S8)
Any list "all graphs in class K up to isomorphism" (e.g. R(3,9,31,<=96), 35,714 graphs)
can be certified like an UNSAT proof: SMS enumerates canonical models with blocking
clauses NOT H_1, ..., NOT H_m; then F_K + SB + blocking clauses is UNSAT (LRAT, cake_lpr),
and SB is certified by VeriPB (link e2). Inside the 40-vertex formula, the H-part
variables use the same formula, so each listed H_i can be a cube, and the enumeration
proof is the cube cover. Then no outside list is trusted.

### 3.5 Streaming
Store no LRAT for n = 40 (sizes below). Run per cube: CaDiCaL writes LRAT to a FIFO,
cake_lpr reads the FIFO (empty hexagon method). Tested: `mkfifo p; cadical --lrat
--binary=true F_j p & cake_lpr F_j p` -> "s VERIFIED UNSAT" ((3,6,18) cube d = 5).
Streaming fits option (ii) of sec. 1.4 (plain refutation of F_j + units(c_j)); option (i)
needs the transform_lrat filter between solver and checker. Keep only: cube, solver log, cake_lpr
stdout line, sha256 of the cube formula. Re-run a cube if its check fails.

### 3.6 satcore's static lex (Codish sb_l with aux variables)
satcore --lex adds, per adjacent row pair (i, i+1), "row_i >=lex row_{i+1}" (columns
without i, i+1) with aux e_k ("prefix equal", only the forcing direction). This is the
lex-leader of the transposition (i i+1) under lex-MAX of the row-major edge vector,
so it shares the order of `cert`'s demo and of MTF-as-dominance. It must never be mixed
with SMS clauses (lex-MIN). VeriPB derivation (`cert/codish.py`), per transposition:
`dom` of one PB constraint L = sum_k d_k (a_k - b_k) >= 0 (goal #2 needs one `pol` step);
`red` full definitions of e_k (fresh vars); a `pol` chain G_k = G_{k-1} + S (e-chain clause)
+ d (equality clause), G_k = sum_{j>=k} d_j (a_j - b_j) + S_k (1 - e_{k-1}) >= 0; each
satcore clause by `rup` from G_k; `deld` of all helpers. Output = exactly satcore's clauses.
`cert/satcore_cert.py` also regenerates every base.cnf section with cert's own code and
compares clause multisets, so satcore's encoder is not trusted.
Results (satcore files runs/satcore/proofs/, `-k K -n N --lex --mtf --proof --lrat`):
| run | sections regenerated | VeriPB / CakePB (tri; tri+IS) | check_cnf (TRI / IS / MTF+lex) | cake_lpr |
|---|---|---|---|---|
| (3,6,18) | 24 / 24 equal | OK / OK; OK / OK | 816 / 310 / 5831 | s VERIFIED UNSAT |
| (3,7,23) | 24 / 24 equal | OK / OK (tri only) | 1771 / 9333 / 12221 | s VERIFIED UNSAT (1.8 s) |

### 3.7 Cardinality constraints (degree / edge bounds), critic X5
Bounds lo <= sum x <= hi enter as PB constraints in the input of a second VeriPB proof
(input = output of proof 1 + D_PB; D justified as an implied constraint, sec. 1.1).
`cert/card.py` replicates satcore's totalizer (ramsey.hpp: cardinality/totalizer, same
tree, same aux numbering) and derives it: per node output O_i two `red` steps give the
full definition O_i <-> (count >= i+1); each satcore clause is the sum (`pol`) of the two
child definitions and one parent definition (literal axioms for empty or leaf children),
a ">= 1" constraint over exactly the clause literals, then `rup` of the clause; the units
O[lo-1], -O[hi] come from `pol` with the input bound. Helpers are deleted (`deld`).
Output = input + satcore's exact clauses (EQUISATISFIABLE), VeriPB + CakePB.
Tests (`cert/card_demo.py N S LO HI`, input TRI + all IS + degree bounds):
(3,4,9) deg = 3: proof OK, CNF UNSAT by cake_lpr; positive controls (3,4,8) deg 2..3 and
(3,5,13) deg = 4: proof OK, CaDiCaL SAT with degrees in range. Negative: a unit for the
wrong output -> VeriPB "not implied by RUP".
Real satcore run (`satcore -n 18 -k 6 --lex --mtf --deg-min 4 --deg-max 5 --proof --lrat`,
runs/cert/satcore_deg/): `cert/satcore_cert.py ... --resolve`: 37/37 base sections
regenerated equal (triangles, 17 lex, mtf, 18 degree totalizers); proof 1 (MTF + lex) and
proof 2 (4,698 totalizer clauses) VeriPB + CakePB + check_pbp OK; check_cnf OK.
satcore's own LRAT FAILS with card options (its warning "base clause ids not 1..m";
cake_lpr: "clause not empty or singleton after reduction"; reported to satcore).
Re-solving full.cnf with plain CaDiCaL --lrat: cake_lpr "s VERIFIED UNSAT".
FIXED by satcore (2026-10-24: base/ext ids mapped through the Tracer); re-run with the new
binary: satcore's own LRAT -> cake_lpr "s VERIFIED UNSAT", no re-solve (demo/satcore_r3_6_18_deg2).
Not done: "card edges-in-block" (e(H_0) <= t, needs --fix-nbhd) - same method.
Sinz sequential counters (sms encoding, `card.sinz` / `card.sinz_derive`): aux s[i][j] <->
(count of the first i+1 literals >= j+1) by two `red` steps; each sms clause by `rup`, some
after one `pol` of two definitions or of a definition and the input bound. Tested on 12
random (m, K, literal signs): VeriPB OK, and an exhaustive semantic check (CNF projected to
the literals is SAT iff count <= K) agrees.
`cert/sms_card_cert.py` certifies an sms run with counters. Claim: F_def + (edges <= E)
UNSAT; proof 1 (SYM, input TRI; M-IS also covers the claim constraint, which is closed under
vertex permutations), proof 2 (input TRI + SYM + degree bounds + claim as PB -> all counter
clauses), check_cnf, cake_lpr. Results (sms proofs, 2026-10-24):
"no (3,7,17)-graph with <= 24 edges" and "no (3,7,18)-graph with <= 29 edges" certified
(the lower-bound half of e(3,7,17) = 25, e(3,7,18) = 30; the upper half is a witness graph).
v3 (critic P2): the bounds lo/hi are NOT taken on trust from the solver's section tags.
`cert/implied_bounds.txt` is a fixed table of allowed implied bounds per (n, s, all|mtf, degree|
edges), each with its justification (hand lemma, Lean, cited fact); for n = 40: all G
5 <= deg <= 9, MTF 6 <= deg <= 9, 159 <= e <= 180. satcore_cert.py and card_demo.py accept a
tagged bound only if the table implies it (tag lo <= table lo, tag hi >= table hi); a tag
"hi=3" for (3,6,18) is rejected. The table is part of the trusted base (sec. 5).

### 3.8 Re-using MathCheckRamsey proofs (trusted "t" clauses removed)
[DuLBG]'s pipeline (github.com/ConDug/MathCheckRamsey commit 84b2aefc, built by `tools`)
writes DRAT proofs whose CAS blocking clauses are "t" lines that its drat-trim fork skips;
they are checked only by a Python script against .perm witnesses. `cert/mc_cert.py`
removes this trust: (1) regenerates the CNF (TRI, IS, `cubic` lex clauses with MathCheck's
aux numbering) and compares clause multisets; (2) checks every "t" clause exactly with
check_sb (lex-MIN, colex positions; 0 bad of 1125; the same clauses are invalid under every
other order tested); (3) VeriPB + CakePB from input TRI: each `cubic` pair by `dom` +
`red` + `pol` + `rup` (codish.derive_one) and each "t" clause by one `dom`, all under one
order; check_pbp and --require-all-tri pass; (4) F' = CNF + "t" clauses, DRAT minus "t"
lines -> drat-trim -> LRAT -> cake_lpr "s VERIFIED UNSAT".
Result for R(3,7) = 23 (`generate.py 23 3 7 0 0 0 0 MPCF`, cadical-ks 17 s): all steps OK,
97 s (cert/demo/mc_r3_7_23/). Not yet supported: MathCheck's sinz degree counters and its
MPCF (MTF) encoding (need VeriPB derivations like sec. 3.2 / 3.7).

### 3.9 The three n = 40 case formulas (cases' Cover Lemma, notes/cases.md Sec. 4a)
Link (b) for n = 40 is the Cover Lemma, PROVED in Lean by `lean` (R310.cover_lemma,
lean/R310/Cover.lean; no sorry; hypotheses only F1, F2; 2026-10-24): if a (3,10,40)-graph
exists, then Phi (TRI + IS) plus one of
  R : d(x) = 9 for all x; N(0) = {1..9}
  S8: MTF; d(0) = 8; N(0) = {1..8}; e(H_0) <= 96
  N : MTF; d(0) = 9; N(0) = {1..9}; e(H_0) <= 98
is satisfiable. The relabelling "v -> 0, N(v) -> {1..d}" is inside the lemma, so no VeriPB
WLOG chain (sec. 3.3) is needed. Per case the certificate is:
1. VeriPB proof 1, input = TRI + the case constraints in PB form without solver aux variables
   (units for N(0); degrees and e(H_0) as PB sums; MTF with FULL aux definitions
   c(i,j,w) <-> x(i,w) and x(j,w), all with labels). Output = input + SB clauses (`dom`).
   Every witness must fix vertex 0 and the blocks N(0), V - N[0] as sets (Note 3 of
   Sec. 4a); VeriPB enforces it (the core is not invariant otherwise), check_pbp checks
   M-IS (aux renamed with the permutation).
2. VeriPB proof 2: the solver's CNF of the case constraints (totalizer or Sinz counters,
   card.py; its one-direction MTF clauses are a subset of the full definitions).
3. Cubes inside the case + cover proof (cake_lpr summary mode or per-cube glue), check_cnf.
4. Glue: the case constraints in the solver CNF must equal a fixed per-case table (as
   implied_bounds.txt does for D; critic P2), never the solver's own tags: cert/cases40.txt.
Lean link to the files (agreed with `lean`): (A) a clause-level statement over the colex edge
variables (TRI/IS iff graph property; Cover Lemma restated over x) and (B) Lean-generated
cube_{R,S8,N}.opb (TRI + MTF full definitions with aux id 781 + 38 p(i,j) + r + cube
constraints in PB form), compared with cert's generator and each solver base as sets of
normalized constraints. DONE 2026-10-24: lean/out/cube_{R,S8,N}.opb (99701 / 99700 / 99700
constraints; theorems R310.Files.tri_is_iff and R310.Files.cover_files, no sorry) are EQUAL as
multisets to cert's independent generator `cert/cube_files.py` (output cert/demo/cubes40/);
one changed constraint -> "multisets DIFFER". So the Lean Cover Lemma now reaches the exact
files that the solvers' base formulas are compared with.
VeriPB cost on this core (S8, 99,700 constraints incl. 88,920 MTF definition clauses):
`dom` with partition-preserving witnesses (aux renamed) is 0.23 s per clause (200 random
lex clauses: 46.5 s; 20: 5.0 s), 60x the TRI-only core (3.7 ms). For 1e6-1e7 SB clauses that
is 3-30 CPU-days. Cheaper: proof 1 on core TRI (+ N(0) units, degree PB) only, and the
cube constraints covered by the Lean lex-leader lemma (sec. 1.2): they are Gamma-invariant.
Base CNF certificate (cert/base40_cert.py, 2026-10-25): sms's cube R base
sms/cnf/reg_10_40_fix.cnf (gen_ramsey -n 40 -k 10 --dmin 9 --dmax 9 --mtf --fix-nbhd 9;
190,019 clauses) is (1) equal to cert's regeneration, and (2) after renaming (sms row-major
ids -> colex; sms aux a -> 30420 + a - 780) a subset of the output of a VeriPB proof whose
input is lean/out/cube_R.opb: 188,640 `red` (fresh aux definitions), 150,460 `rup`, 76,360
`pol` (Sinz counters from Lean's degree bounds; MTF bridge c(Lean) -> c'(sms)); VeriPB +
CakePB OK, check_pbp OK; 25 s, 8.7 GB RAM. So: Lean cube R satisfiable => sms base R
satisfiable. Negative: one flipped literal in the sms file -> regeneration FAIL.
R(7) base (2026-10-25): sms/cnf/Rc7b.cnf (893,163 clauses; + --codeg-max 7, --codeg-pair 7,
--edges 10-11,10-12,8-11,8-12,9-11,9-12, --block-from 13 --block-e 85) certified the same way,
with input = lean/out/cube_R.opb + runs/cert/base40/Rc7b/case.opb (the case constraints of
cases' Lemma Mc / Lemma R7: N(10) cap N(0) = {1..7} units, the 6 edge units, codegree <= 7 per
pair via defined aux d(u,v,w) <-> x(u,w) & x(v,w), e({13..39}) = 85). VeriPB + CakePB OK, 2.4 min.
Trust note: case.opb rests on Lemma Mc + R7 (hand, critic-confirmed), not yet in Lean.
Optional additions allowed by Sec. 4a Note 2 (degrees 6..9; L6 codegree bound under F2; R:
e(H_0) = 99) go in the same way and need a table row each.

## 4. Size and time estimates

Measured (this machine, one CPU):
- VeriPB `dom` at n = 40, core = TRI (9,880 clauses), 1,000 random SMS-type clauses
  (random permutations): VeriPB 3.7 ms/clause, 24 MB; CakePB 35 ms/clause, 4.2 GB heap;
  proof file 10 KB/clause (witness of up to 780 mappings + order with 780 big integers).
  So 1e7 SB clauses: VeriPB 10 h, CakePB 4 days, 100 GB. Splits into chunks (each chunk
  is its own VeriPB run on the same core; valid because every `dom` step uses only the
  core, the order and its own witness; the chunk outputs combine by the order argument
  in check_sb.py's header).
  Faster option: aux-variable orders: Anders, Bogaerts, ..., Nordström, Oertel, Tan,
  "Faster Certified Symmetry Breaking Using Orders With Auxiliary Variables",
  arXiv:2511.16637v1 (2025-11-20): replaces the big-integer lex order; "orders-of-magnitude"
  speed-ups (satsuma + VeriPB). Our VeriPB 3.0.2 already has the needed `spec` block in
  `def_order` (proof_format_overview.md cites it as [ABB+26]). No code URL in the paper.
  Not yet tried here.
  Prior art check (web, 2026-10-24): certified SMS (VeriPB for SMS clauses) is named as
  future work in arXiv:2501.14363 (Yang-Baxter enumeration with SMS); for UNSAT results
  our per-clause `dom` method (sec. 2, sms2veripb.py) is enough, because completeness of an
  enumeration is not needed.
- check_sb.py: 0.6 ms/clause at n = 40. check_cnf: 31 us per 45-literal IS clause at n = 40 (100k clauses in 3.1 s).

LRAT rate and check ratio (literature, `cert/lit_certified_proofs.md` sec. 8):
| project | proof / solve time | check / solve |
|---|---|---|
| empty hexagon | 180 TB / 17,300 CPU h = 2.9 MB/s | streamed |
| Schur 5 | 2.18 PB LRAT (compressed) / 14 CPU y = 4.9 MB/s | 2.6 |
| R(3,9) [DuLBG] | 289 GiB / 697,575 s = 0.44 MB/s | 0.68 |
| Keller 7 (Lean, cake_lpr) | not given | 125 h / 228 h = 0.55 |
Our demo (tiny): (3,6,18) 5 MB LRAT for 0.3 s solve (17 MB/s), cake_lpr check 13x solve
(dominated by re-loading F per range). satcore (3,7,23) --lex --mtf: 20.5 MB ASCII LRAT
for 2.0 s solve (10 MB/s), cake_lpr 1.8 s (0.9x solve), 0.9 GB RAM.

Estimate for n = 40 with T CPU-years of search:
LRAT = T x 3.15e7 s x (0.4..5 MB/s) = 14..160 TB per CPU-year (stream, do not store);
cake_lpr check = 0.5..2.6 T CPU-years (verified checker).
T is unknown. Inputs: `satcore` / `sms` scaling runs (k = 5..9). Prior compute for the
upper bound 41: GR2013 about 50 CPU-years, Angeltveit about 3 CPU-years (no certificates).
With the team's 96 CPUs, T = 10 needs about 5 weeks solve + 3..13 weeks check.

### 4.1 Core plan: proof cost at scale (for sms's notes/core_plan.md)
Measured on sms's run "no (3,8,22)-graph with <= 41 edges" (SMS lazy IS + proof log, 1 CPU):
| step | cost | relative to SMS time T = 802 s |
|---|---|---|
| SMS solve with proof log | 802 s; plog 722 MB zstd; 54,418 external clauses (36,568 SYM) | 1 |
| plog -> CNF + LRAT (sms C++ converter, 18 MB/s) | LRAT 3.4 GB (4.2 MB per solve-second) | ~0.24 |
| cake_lpr on the stored LRAT | 370 s, 4.2 GB RAM (1 CPU) | ~0.46 |
| or: re-solve CNF + externals with CaDiCaL, LRAT streamed through a FIFO into cake_lpr (nothing stored) | 1,307 s wall, both processes on ONE CPU | ~1.6 |
| SYM clauses: Lean-verified sbcheck (n = 40) / check_sb.py | 0.66 ms / 0.4 ms per clause (36,568 clauses: 24 s / 15 s) | ~0.03 |
| SYM clauses: VeriPB proof 1 (n = 22, TRI core) | > 28 min for 36,568 clauses (derived set grows; CakePB slower) | > 2 |
| check_cnf on the externals | 31 us per clause (54k: 2 s) | < 0.01 |
| VeriPB proof 2 (counters), check_pbp | seconds (small, fixed per cube type) | < 0.01 |
Rules for the n = 40 core (keeps the plan inside the certified chain):
1. One order everywhere: SMS lex-MIN of the row-wise edge vector; witnesses must fix 0 and
   map N(0) onto itself (--initial-partition 1 d 39-d). No satcore --lex, no other static SB.
2. Primary SB check: Lean-verified `sbcheck` (+ Lean lemma cover_files_sb); second check:
   check_sb.py on all clauses; VeriPB/CakePB only on a random sample (e.g. 1,000 per cube
   type), because they cost more than the solve itself.
3. Proof check: per cube, `cake_lpr` must print "s VERIFIED UNSAT" for CNF_j = cube base
   (equal to lean/out/cube_X.opb clauses + solver encodings checked by VeriPB proof 2) +
   the cube's externals (check_cnf: TRI / IS / SYM listed); glue.py percube for the cover.
4. Storage: for cubes with T below ~1 h: store plog.zst, convert, cake_lpr, then delete LRAT
   and plog; keep externals, sym.json, all check logs and sha256 (re-run possible). Peak disk
   per running cube ~ 4 MB/s x T (LRAT) + plog.zst. For longer cubes: re-solve and stream
   (about 1.6 T extra CPU, no proof storage), or split the cube further.
F1 scale (n = 23..27, no Lean lemma yet for these n): sms's unsplit "no (3,8,23)-graph with
<= 46 edges": 3,094 s, LRAT 10 GB, 98,858 externals; VeriPB proof 1 (SYM) ~38 min, CakePB
proof 1 > 8 min and running (CakePB of the (3,8,22) run: stopped after 49 min). Asked `lean`
to generalize the lex-leader lemma and sbcheck to any n with an edge-count claim and degree
bound; then F1 SB checks become sbcheck + check_sb, VeriPB/CakePB sampled. The max-degree
split did not help for m = 23 (D = 5 alone 3,991 s) and was stopped by sms.
cake_lpr is called with --CML_HEAP_SIZE=10000 (MB) for proofs of 10 GB and more.
DONE by `lean` (2026-10-24, lean/R310/GenLex.lean, GenCheck.lean): R310.Gen.lexleader_gen (any
n; Phi = triangle-free + alpha < s + #edges <= E + all deg <= D + optional N(0) units; Gamma =
all permutations if d = 0, else those fixing 0 and {1..d}) and R310.Gen.edgeLowerBound_of_unsat
(D >= k-1, no units: UNSAT of Phi + valid SB clauses -> Lean's F1 hypothesis
EdgeLowerBound k m (E+1)); sbcheck with header "n= s=" (R310.Gen.checkG_sound).
sms_card_cert.py --sb lean uses it: sbcheck + check_sb.py on ALL SYM clauses, VeriPB/CakePB
proof 1 on a 500-clause sample. Test (3,7,18) <= 29: sbcheck 1,588 clauses 0.2 s; CakePB
sample 5 s; RESULT OK. Negatives: one flipped literal or a wrong n -> sbcheck FAIL.
The F1 watcher uses --sb lean (runs/cert/f1/sms_certs.txt).
Cube-family test (2026-10-25, CPUs 68-71, runs/cert/cc_r936/): sms's 67 lookahead cubes of the
8-regular (3,9,36) MTF family with N(0) = {1..8} (the n = 40 cube shape one level down), each
solved by smsg with proof log and --initial-partition 1 8 27, each checked by cube_check.sh
(LRAT conversion, cake_lpr, Lean sbcheck with d = 8, check_cnf; base clauses allowed as extras):
67/67 UNSAT, 67/67 "s VERIFIED cube". Solve CPU 584 s (median 2.7 s, max 116 s); check CPU
486 s = 0.83 x solve; proof log 2.5 GB = 4.3 MB per solve-second; cake_lpr RSS up to 10 GB
(the heap setting); 8 min wall on 4 CPUs. Not yet in this test: the justification of the base
(regeneration of degree counters / MTF and VeriPB proof 2), done once per base, not per cube.
Runner: tools/bin/cuberun (tools/README.md sec. 9) calls cert/cube_check.sh per cube
(--check; verdict only from stdout "s VERIFIED"; FAILED/TIMEOUT/NO_PROOF -> ALERT_errors.txt,
all files kept; --check-parallel 1; proofs hashed then deleted after VERIFIED; ext + sym.json
kept; results.jsonl per cube for glue.py percube).
5. Budget: certification adds about 0.7 T (store-and-check: convert 0.24 T + cake_lpr 0.46 T)
   to 1.6 T (re-solve and stream) per cube, plus SB checks (~0.03 T). For a core of C
   CPU-years: about 1.7 C to 2.6 C CPU-years in total. cake_lpr needs ~4 GB RAM per check
   (default heap; raise with --CML_HEAP_SIZE for larger proofs).

## 5. Outside computations and trusted base (link g)

Trusted (cannot avoid): Lean kernel; CakeML-verified cake_lpr and cake_pb plus their C
FFI shim (basis_ffi.c, unverified; cake_lpr's basis_ffi.c does not match the repo sha file,
see `tools`); hardware/OS; gcc/as/ld for the shipped .S; sha256.
Trusted glue (short, review needed): cert/check_cnf.py (or a Lean-verified variant),
cert/check_pbp.py (M-IS conditions), cert/implied_bounds.txt (allowed D), cert/glue.py,
cert/demo.py glue (summary has empty clause; hashes),
the meta-lemma M-IS (Lean target),
the encoding statement (link a1: Lean target, like the empty-hexagon Lean encoder).
Untrusted (all output re-checked): CaDiCaL, SMS (+ patches), satcore, cubers, nauty,
VeriPB (re-checked by CakePB), drat-trim, lrat-check, check_sb (re-checked by VeriPB),
cert's proof writers sb.py, mtf.py, codish.py, card.py (output checked by VeriPB/CakePB and
check_pbp), satcore_cert.py section regeneration (a second, independent encoder).

Outside facts used by `cases` (must be certified, re-computed, or listed as assumptions):
| fact | used by | status | how to certify |
|---|---|---|---|
(Corrected after critic Review 11, X10, against notes/cases.md v2. This table is for the
REFINED split; the coarse split of Theorem A'' needs only F1 and F2, see sec. 5.1.)
| fact | used by | status | how to certify |
|---|---|---|---|
| R(3,9) <= 36 | L1 (deg >= 4) | [DuLBG] DRAT + Graver-Yackel hand lemma, trusted 't' clauses | not needed if MTF: M1 gives deg >= 6 by hand |
| delta >= 5 (L7') | all-G split only | computer proof by `critic`; premise [GR] Thm 3 (R(3,9,35) unique) | not needed for the MTF split |
| R(3,8) <= 28, i.e. no (3,8,28)-graph | L9 (9-regular case); L6 only in the all-G split (MTF split: no forced LP rows when delta >= 6) | McKay-Zhang 1992; [DuLBG] DRAT | our chain: (3,8,28) UNSAT (sms runs r3_8_28) |
| e(3,9,m) | MTF split: m = 30..33 only; all-G split: m = 30..35 | [GR] tables, no certificates | SAT: "no (3,9,m)-graph with <= e(3,9,m)-1 edges" + LRAT (cost unknown) |
| e(3,10,40) >= 161 [GR161] | no longer needed | cases v2 K1: e = 159, 160 covered with t9 <= 86 | - |
| R(3,9,31,95..96) list (35,714) | case S8 | [GR] Table 14 counts | enumeration + blocking-clause UNSAT proof (sec. 3.4; review X9 first) |
| R(3,9,30, e <= t9) lists | case N(t), only if glued | [GR] T14 for e = 86, 87; larger unknown | same as above |
| degree-distribution list (545 MTF) | case split | cases/degseq.py, re-run by critic; LP certs exact | Lean lemma + certs, or cubes on counters (sec. 3.3) |

### 5.1 Outside facts: TRUSTED published dependencies (user rule, 2026-10-25)
Rule "Trust published results" (notes/TEAM_RULES.md): published results are hypotheses, listed
with statement and source in notes/DEPENDENCIES.md (owner: lit); no CPU is spent to re-certify
them. For the chain this means:
- F1 (e(3,8,m) >= 6m-91, m = 23..27; Radziszowski-Kreher 1988 / [GR] Table 3) and
  F2 (R(3,8) = 28; McKay-Zhang 1992, [DuLBG]) are trusted hypotheses of Lean's Cover Lemma.
- [GR] tables and counts are trusted where a split uses them (only the refined split does).
- The F2 MathCheck runs were stopped (2026-10-25, ~4.6 h, no result); F1 runs m = 25, 26 stopped.
- Bonus, already certified (kept): F1 for m = 23, 24, 27 (table below), and the k = 7 edge
  bounds e(3,7,17..20) (sec. 3.7). They show that the method works; they are not required.
- What stays certified: everything the team computes NEW (the n = 40 cubes, sec. 3.9 and 4.1).

(Below: the plan as it was before the rule; kept for the record.)

#### Earlier plan (before 2026-10-25)
cases' Theorem A'' (notes/cases.md; critic Review 16): the MTF coarse split R / S8 / N(98)
needs only hand lemmas (L1, L2, L4, M0, M1; Lean targets) and two computed facts:
  F1: e(3,8,m) >= 6m - 91 for m = 23..27, i.e. no (3,8,m)-graph with <= 6m - 92 edges
      (E = 46, 52, 58, 64, 70; true minima 49, 56, 65, 73, 85: slack 3..15).
      (The general bound 6n - 13k of Radziszowski-Kreher 1991 is NOT computer-free: its base
      uses computed e(3,7,.), e(3,8,.) tables; found by `lit`, notes/edge_tables.md sec. 1b.)
  F2: R(3,8) <= 28, i.e. no (3,8,28)-graph.
It does NOT need e(3,9,*), e(3,10,40) >= 161, R(3,9) <= 36, delta >= 5, the 545-distribution
list or any graph list (S8 becomes a SAT cube: d(0) = 8, N(0) = {1..8}, e(H_0) <= 96).
Existing certificates: only [DuLBG] for F2 (DRAT + trusted CAS clauses, no public files).
| # | fact | route | cost estimate | owner | status |
|---|---|---|---|---|---|
| F1 | no (3,8,m)-graph with <= 6m-92 edges, m = 23..27 | SMS lazy IS + Sinz edge counter, cert/sms_card_cert.py (same route as the certified e(3,7,17), e(3,7,18) bounds, sec. 3.7); second route satcore --lex + totalizer, cert/satcore_cert.py --claim-edges-max | small: slack 3..15 edges; SMS did the exact (3,7,19) bound in 24 s; RK 1988 needed 250 VAX-hours for e(3,8,25) >= 65 itself | sms (runs), cert (certificates), satcore (2nd route) | m = 23 CERTIFIED 22:15, m = 24 CERTIFIED 23:04 (below); m = 25, 26 unsplit SMS runs going, m = 27 to restart; satcore route stopped (slower) |
| F1 split | if F1 runs are too big (sms: proof logs ~11 GB/h per run): split each claim by the maximum degree D = 0..7: vertex 0 has max degree D, N(0) = {1..D}, all degrees <= D (hand lemma: relabel a max-degree vertex; keeps "edges <= E"; D <= 7 since deg <= s-1; all D run, so no R(3,7) fact) | sms --fix-nbhd D --initial-partition 1 D m-1-D --dmax D; cert/sms_card_cert.py --fix-nbhd D (units in proof-1 core: VeriPB checks every SYM witness keeps 0, N(0), rest as blocks; --perm-only) | test (3,7,18) <= 29 edges, D = 4, 5, 6: 1-2 s each (unsplit 4.4 s), all certified | sms, cert | proposed to sms 2026-10-24 |
| F2 | no (3,8,28)-graph | MathCheck + cert/mc_cert.py (sec. 3.8); sms / satcore runs + converters | 6-60 CPU h solve + about the same to check | cert, sms, satcore | STARTED 19:50: cadical-ks, CPUs 70-71, 12 h limit (runs/cert/mc28/) |
| - | e(3,9,*), e(3,10,40) >= 161, R(3,9) <= 36, delta >= 5, lists | not needed by the coarse split | 0 | - | dropped (would be needed only by the refined split). satcore (2026-10-24): even with the local bound L3 as clauses (--hv-min), edge-minimum instances stay UNKNOWN ((3,7,19) <= 36 edges, 300 s); e(3,9,30..33) by pure SAT judged out of reach |
| - | Lean: L1, L2, L4, M0, M1, Theorem A'', the cube cover of R / S8 / N(98) | lean | - | lean | open |
implied_bounds.txt now holds only table-free rows for n = 40 (MTF: 6 <= deg <= 9); the rows
that used [GR] tables were removed.

F1 certificates (sms unsplit SMS runs, --dmax 7, no MTF; cert/sms_card_cert.py --sb lean; Lean
R310.Gen.edgeLowerBound_of_unsat turns each into the F1 hypothesis EdgeLowerBound 8 m (E+1)):
| m | claim | SMS time | externals | SYM (sbcheck) | check_cnf IS / TRI / SYM+counter | cake_lpr | certified |
|---|---|---|---|---|---|---|---|
| 23 | no (3,8,23)-graph with <= 46 edges | 3,094 s | 98,858 | 71,031 (10 s) | 27,522 / 1,771 / 101,810 | 403 s | 2026-10-24 22:15 |
| 24 | no (3,8,24)-graph with <= 52 edges | 8,970 s | 158,959 | 112,512 (18 s) | 45,786 / 2,024 / 149,748 | 898 s | 2026-10-24 23:04 |
| 27 | no (3,8,27)-graph with <= 70 edges | 5,503 s | 117,623 | 65,321 (13 s) | 52,044 / 2,925 / 124,795 | 701 s | 2026-10-24 23:43 |
Files: cert/demo/sms_f1_8_<m>_le<E>/, logs runs/cert/f1/cert_f1_8_<m>_le<E>.log.

## 6. Open risks

1. Search cost T may be far beyond the team (case R alone: ~1e18 R(3,9,30,99) graphs by
   gluing estimate; SAT cost unknown). Certification multiplies cost by 1.5..3.6.
2. Order mismatch: a static SB clause, a cube or a case lemma that is not valid for the
   SMS lex-min canonical form. Mitigation: everything symmetric goes through `dom`
   under ONE order; VeriPB rejects a mismatch (tested).
3. WLOG steps on a non-symmetric core (fixed N(0), P(0)): SMS must use only witnesses that
   respect the partition; VeriPB checks this (core not closed otherwise).
4. MTF + symmetry assumption (symsat): MTF completion breaks an assumed automorphism.
   Only matters for symmetric-class searches; they are a construction aid, not part of a
   non-existence proof.
5. Lazy clauses: a solver bug that adds a clause not of IS shape. check_cnf rejects it.
   A bug that omits a clause from ext.cnf/proof log: cake_lpr rejects the proof (undefined id).
6. Glue errors: cake_lpr/cake_pb exit 0 on failure; COVER without empty clause. Glue
   tests both (sec. 1.4). Glue should get a review and a negative-test suite.
7. VeriPB output check compares core and output formula: the output file must contain
   exactly input + SB. Order of clauses does not matter; duplicates do (dedupe SB first).
8. Proof storage: streaming means no re-check later without re-solving. Keep solver seed,
   version, cube and formula hash per cube so any cube can be re-run and re-checked.
9. Lean coverage: encoding statement, M-IS, M0, implied constraints D. Without these the
   reductions rest on hand proofs (reviewed by `critic`).
10. Solver proof bugs: satcore's LRAT with card options does not check (sec. 3.7). Any
   such failure is caught (cake_lpr), and a re-solve of the same formula is a valid fix.
11. Sec. 3.4 (enumerated lists as cubes) needs its own review before use (critic X9).

## 7. Next steps (owner)

- satcore: DONE for (3,6,18), (3,7,23). Next: same files for --fix-nbhd / --deg-* runs.
- sms: proof logs for an MTF run and for a --fix-nbhd/--initial-partition run; cert adds
  aux renaming to the witnesses and checks the partition obligations in VeriPB.
- cert: a Lean-friendly spec of check_cnf and check_pbp; "card edges-in-block" (e(H_0) <= t);
  certify satcore and sms runs as they come.
- satcore: fix LRAT renumbering with card options (sec. 3.7).
- lean: encoding statement (F_def models = (3,10,40)-graphs), M-IS, M0, and the
  implied constraints used as D.
- cases: state which outside facts each case needs (sec. 5 table).
- critic: review this note, check_cnf.py, check_sb.py, demo.py glue.
