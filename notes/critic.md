# Critic findings

Author: critic. Classes: ERROR (wrong), GAP (unproven), RISK (could be wrong), OK.
Evidence files are in critic/ (sources in critic/src, test data in critic/g6tests).

## Review 1 (2026-10-24): tools/check_graph.py

Method: own C checker critic/src/mycheck.c, written from the graph6 spec, not from
check_graph.py (strict parse, adjacency matrix, triple-loop triangle test, plain
recursive alpha). mycheck agrees with brute force on 1500 random graphs, n <= 15
(critic/src/brute.py).

Comparison, check_graph.py vs mycheck (n, e, min/max degree, triangle-free, alpha, verdict):
- 9904 graphs (critic/g6tests/mixed1.g6): G(n,p) n = 1..45, random maximal triangle-free
  n = 39, 40 (alpha 10..18), long-form graph6 n = 63..80, triangle-free circulants n = 30..40.
  0 mismatches.
- ALL triangle-free circulants C_n(D), |D| <= 9: n = 39 (1320 graphs), n = 40 (2920 graphs).
  0 mismatches.
- Known graph: C35(1,7,11,16) (the unique (3,9,35)-graph, [GR] Thm 3): both give
  n=35 e=140 8-regular alpha=8. With --k 8 both reject it. OK.

Findings:
- C1 ERROR. A line that starts with ">>" is dropped. nauty writes the header ">>graph6<<"
  with NO newline, so the header line also holds the FIRST graph. That graph is not checked.
  Test critic/g6tests/hdr_drop.g6 = ">>graph6<<" + K5, then C5: exit 0, K5 never checked.
  A file with only a header + one graph crashes (exit 1). Fix: strip the prefix, keep the graph.
- C2 RISK. No length / padding / character check. Too long string "Dhc~~~", nonzero padding
  "Dhd", and "Dhc junk" all pass as C5 (exit 0). Two graphs joined on one line: only the
  first is checked. Fix: require len = header + ceil(n(n-1)/12) bytes, chars 63..126,
  zero padding.
- C3 RISK. Exit 0 does not mean n = 40. A (3,10,39)-graph also passes. The claims rule
  ("passes for n = 40") depends on a person reading n. Fix: add --n N, fail if n != N.
- C4 RISK. Zero graphs read (empty file, blank lines, header only) gives a crash, not a clear
  "no graphs" error. n = 0 graph "?" also crashes. Fix: count graphs, fail if 0, print count.
- C5 RISK. "check_graph.py FILE --k 9" ignores --k 9 and uses k = 10, no warning. Fix: strict
  argument parsing.
- C6 RISK. Matrix checks use assert. Under "python3 -O" an asymmetric matrix passes
  (critic/g6tests/asym.mat: exit 0, e=4). Fix: explicit raise.
- OK: alpha (branch and bound) and triangle test are correct on all tests; long-form graph6
  (n >= 63) parse is correct; CRLF line ends are OK.

## Review 2 (2026-10-24): notes/step0_literature.md vs data/papers

- L1 ERROR (FIXED by lead 2026-10-24, re-checked). "Pandey-Ravi ... structure of (3,10,41)-graphs (assumes R = 42). Not about n = 40."
  Wrong: arXiv:2601.03572 Sec. 3 assumes R(3,10) = 41 and studies (3,10,40)-graphs
  (Delta = 9, delta >= 4, diameter 2 or 3, ...). notes/edge_tables.md Sec. 7 has it right.
  Its proofs are unverified (lit's note).
- L2 RISK (FIXED by lead, re-checked). "Degrees in {5..9}" is the n = 41 range. For n = 40 the range is {4..9}
  (40 - 1 - d <= 35). Also e(3,10,40) >= 161 ([GR] Table 5) > 160, so Delta = 9 and
  161 <= e <= 180. Not in step0; edge_tables.md has it.
- L3 GAP (step0 wording FIXED by lead; the gap itself stays open until known39 reports). "One-point extension of known 39-vertex graphs is exhausted." Sources:
  GR slides (data/papers/GR_ber12_slides.pdf: "37M+ ... none of them extends to a
  (3,10;40)-graph"); [GR] p.15: "no (3,10;40)-graphs were constructed".
  The final GR set has 43 117 868 graphs ([Ang] Sec. 1.1) and the union has 43 146 537
  ([Ang] Sec. 7). No source says that the ~6M later GR graphs, or Angeltveit's ~28 669 new
  graphs, were tested for 39 -> 40. [Ang] Sec. 6 tests only the (3,10,38)-graphs from his
  run ("a large number"), not all (3,10,38)-graphs. known39's re-check closes this.
- L4 OK (now with evidence). "Circulant (3,10,40)-graphs do not exist": was an inference from
  DS1 2.1.i [HaKr1]. Own exhaustive check: all 2920 triangle-free C_40(D), |D| <= 9, have
  alpha >= 10 (min 10, 40 graphs); both checkers agree. Same for n = 39: min alpha 10.
  (n = 38: min alpha 9, so a (3,10,38) circulant exists; n = 35: alpha 8 = C35(1,7,11,16).)
- L5 OK. Prop 2.1, input counts (1 554 928 360 / 14 395 / 5), 506 regular graphs from
  ~150e9 R(3,8,24,e=63)-graphs, 3 vs 50 CPU years, McKay check, 43 117 868, author quotes:
  all match arXiv:2401.00392v2. R(3,9,35,e<=139) empty: [GR] Table 4 e(3,9,35) = 140.
- L6 OK. 9-regular n = 40: G_v in R(3,9,30,e=99): e(G_v) = 180 - sum of 9 neighbour
  degrees = 180 - 81 = 99, alpha(G_v) <= 8. Correct.
- L7 OK. DS1 rev #18 date 2026-04-24, [DuHu] incorrect construction, [DuLBG] DRAT, [KirS],
  [NaSZ], [GauB]: match DS1 text. EJC 2025 publication data of [Ang] and arXiv:2603.09172
  are not in local files (not checked).
- Typos in sources (found by lit too, I agree): [GR] p.15 "151 <= e(3,9,39) <= 161" means
  e(3,10,39). [Ang] Sec. 5 "R(3,8,63,e=112)" means R(3,8,24,e=63).

## Review 3 (2026-10-24): notes/edge_tables.md (lit), spot checks

- OK. Theorem 2 formulas = [GR] (5). 6n-13k = 123, Backelin 131, Krüger 122 at n = 40.
- OK. Degree-sequence table f(d) = 20d - d^2 - e(3,9,39-d): I re-derived [GR] (4) for n = 40
  (sum_v e(G_v) = n e - sum d_v^2) and get the same f values (-76,-54,-34,-13,+1,+13) and the
  same pure bound e >= 159 (e = 158 needs 4 deficit units below 8, cost >= 56 > 40).
- OK. Tables 4, 5 values match [GR].

## Own derivation for cross-check (n = 40 analogue of [Ang] Prop 2.1)

Let N = sum over v of (9 - deg v). Then e = (360 - N)/2, so N is even. For deg v = d:
e(G_v) = e - (sum of neighbour degrees) = 180 - N/2 - 9d + eps(v), with
eps(v) = sum over neighbours w of (9 - deg w). [Ang]'s graph Gamma' (9 - deg v copies of each
vertex with deg <= 8) is triangle-free on N vertices, so (Mantel) some copy has degree
eps(v) <= N/2. (For n = 41 [Ang] uses (N-1)/2 because N is odd there; for n = 40 it is N/2.)
So if G is not 9-regular, some v with d <= 8 has e(G_v) <= 180 - 9d:
  d=8: R(3,9,31,e<=108); d=7: R(3,9,32,e<=117); d=6: R(3,9,33,e<=126);
  d=5: R(3,9,34,e<=135); d=4: R(3,9,35) (only the 140-edge graph).
  9-regular: every G_v in R(3,9,30,e=99).
Will compare with cases' table when it is out.

## Review 4 (2026-10-24): degree-4 exclusion (web claim, hraness/algal-lab) - re-derived

Claim: a (3,10,40)-graph has no vertex of degree 4 (so delta >= 5, without MTF).
Own encoding critic/src/deg4_cnf.py (docstring has the reduction). Premise: uniqueness of the
(3,9,35)-graph ([GR] Thm 3); I checked that C35(1,7,11,16) is a (3,9,35)-graph, so it is that graph.
Reduction: deg v = 4 -> G - N[v] = H = C35(1,7,11,16); G is fixed by S_c = N(a_c) in H;
u in H has deg_H = 8, so it is in <= 1 set S_c; S_c independent in H; alpha(G) <= 9 <=> every
independent J of H with |J| = 6, 7, 8 meets >= 1, 2, 3 of the S_c (J has 22995 / 13760 / 3360 sets).
- CNF: 140 vars, 98 965 clauses (same size as the web claim; its CNF hash differs, so not
  byte-identical). sha256 e60640ad...9e42 (critic/deg4/deg4.cnf).
- CaDiCaL 3.0.1: UNSAT in 11 s. drat-trim: VERIFIED. LRAT from drat-trim: cake_lpr "s VERIFIED UNSAT"
  and lrat-check OK.
- Calibration: same generator with alpha <= 10 (K = 11, u in <= 2 sets): SAT; decoded graph
  critic/deg4/k11.g6 is n=40, e=167, deg [4,10], triangle-free, alpha 10 by BOTH checkers.
  So decode + independent-set clauses do what they claim.
- Verdict: OK. delta >= 5 for every (3,10,40)-graph, given [GR] Thm 3 (itself a computer result
  without certificate). Trust base: my 60-line generator + cake_lpr.

## Review 5 (2026-10-24): MTF reduction, delta >= 6 (lit, from algal-lab frontier review)

Claim: if a (3,10,40)-graph exists, a maximal triangle-free (MTF) one exists, and in it
2(n-1) <= d(2k-d) for every degree d, so delta >= 6.
Line by line: adding edges keeps triangle-free and cannot raise alpha -> MTF witness exists;
MTF -> every vertex of H = V - N[v] meets A = N(v). e(A,H) <= d(k-2) (Delta <= k-1, one edge to v).
e(A,H) >= 2|H| - p (p = H-vertices with exactly 1 A-neighbour). Private neighbours P_u of u in A:
P_u + (A - u) is independent (P_u in N(u), private, A independent) -> |P_u| <= k-d, p <= d(k-d).
=> 2(n-d-1) - d(k-d) <= d(k-2) <=> 2(n-1) <= d(2k-d). n=40, k=10: d=5 gives 78 <= 75 false; d=6 84 OK.
Verdict: OK (MTF graphs only; d = 4 also excluded there).
RISK (agree with lit): do not mix two different WLOG choices in one case split (e.g. "WLOG MTF"
adds edges, "WLOG edge-minimal" removes them). Facts true for ALL (3,10,40)-graphs (e >= 161,
Prop 2.1 analogue, delta >= 5) can be combined with MTF, since they hold for the MTF witness too.
For MTF, the Prop 2.1 analogue leaves d in {6,7,8}: R(3,9,33,e<=126), R(3,9,32,e<=117),
R(3,9,31,e<=108), or 9-regular.

## Review 6 (2026-10-24): notes/cases.md v1 (cases), on request

Hand proofs, line by line: L1, L2, L3, L3', L4, L5 (f(d) <= 13 - 12(9-d), N <= 42), L6 and its
consequences, L7, L8 (a)-(f) incl. the Motzkin-Straus argument, Theorem A, Theorem B,
Theorem C (re-did N = 38: s=0 gives 80 -> killed; s=2 gives 89), L9, M0-M3: all OK.
Theorem A re-checked: a_v >= 13 for d <= 7 (91/84/75/64 vs 104/118/129/140); sum a_v = 0 by L4.

Code: read build_lp / verify_farkas / t9_star. Rows match L8; the Farkas check is exact and
sound (y >= 0, box minimum over [0, ub], ub rows are valid). Rounded y that fail are not used,
so t9 can only err upward (safe). verify_certs.py: 2176 MTF certificates, 0 failed.

Independent replication critic/src/cases_rep.py (own code from the lemma statements, float LP,
row families = cases' families plus all Mantel weights in {0..3}^classes):
- all G, GR161: 1944 simple-check survivors (= cases 1915 + 29 LP kills). My stronger LP kills 47;
  cases' 1915 contains all my 1897 (0 distributions only in mine). Consistent.
- MTF, GR161: 545 survivors, identical list. t9_U8 identical for all 544 non-regular
  distributions (my extra Mantel weights do not lower any t9).
Verdict: OK. Findings:
- K1 RISK (stated): the whole table uses e >= 161 ([GR] Table 5, computer result, no
  certificate). --self-e (e >= 159) is run only for all G. Suggest also --self-e --mtf, so the
  table can be quoted without GR161.
- K2 note: L7 / check_deg4_structure can be replaced by delta >= 5 (Review 4, cake_lpr-verified),
  which is simpler and holds for all G. Not needed for MTF (M1).
- K3 note: all-G mode: Mantel weights in {0..3}^classes kill 18 more distributions (float LP,
  not certified). Optional.
- K4 RISK (minor): test_lp_on_graphs.py skips lines starting with '>' (same nauty-header issue
  as check_graph C1); a header file would lose its first graph.
- K5 OK: using the 545 MTF distributions + t9 for SAT runs that do NOT encode MTF is still sound
  (the search space contains the MTF witness). Each SAT run must encode the exact degree
  distribution n AND the case condition for one fixed vertex.
- K6 (lead request): Theorem A CONFIRMED again; identity sum_v e(H_v) = sum d(20-d) also checked
  numerically (critic/src/thmA_identity.py, 201 graphs with 40 vertices). Theorem A (S8 / N(t9) / R) and
  Theorem B (d=8..4 classes) are both valid but different disjunctions: a gluing plan must use one.
  t9_U8 values over the 545 MTF dists: 85 (killed) x6, 86..99. Sent to gluing, lead, cases.

## Review 7 (2026-10-24): known39 extension method (their message)
OK: G+w is a (3,10,40)-graph iff N(w) is independent and meets every independent 9-set of G;
controls are reasonable. Scope: their set is the rewire closure of Exoo's graph, not the
GR/Ang 43M set -> L3 GAP stays open for those. Plan: sample-check their output with own extender.

## Review 8 (2026-10-24): symsat's MTF caveat
OK (symsat is right). "WLOG MTF" is not valid inside a symmetry class: adding sigma-orbits keeps
sigma-invariance but gives only orbit-maximal graphs, not MTF. So under an assumed automorphism
do NOT use M1 (delta >= 6), diameter 2, M2, or the 545 MTF distributions. Valid there (true for
all G): delta >= 5 (Review 4), Delta = 9 and e >= 161 [GR161] (or e >= 159 self), L6, Theorem A,
cases' all-G list (1897 in v2; was 1915 in v1). Same caveat applies to any search with an extra restriction
that is not preserved by edge addition.

## Review 9 (2026-10-24): notes/cases.md v2 (K1-K4 answers)
Re-ran critic/src/cases_rep.py (now with --self-e) in all 4 modes; identical to cases v2:
- all G, e>=161: 1897 = 1897; all G, e>=159: 1938 = 1938;
- MTF, e>=161: 545 = 545, t9_U8 equal on 544; MTF, e>=159: 573 = 573, t9_U8 equal on 572.
- e in {159,160} MTF: 28 dists, 27 with t9_U8 = 85 (killed by S8), 1 = (n7,n9) = (20,20), e=160,
  t9_U8 = 86 (t9_known = 85). Confirmed.
- verify_certs.py: 7631 + 2176 + 7797 + 2286 certificates, 0 failed.
Verdict: OK. The MTF table holds without GR161 if case N(t) for (20,20) uses t9 = 86.
Note: S8 gluing may use MTF pruning only when it is used for the MTF split. For the all-G /
symmetric split (e.g. symsat), the S8 gluing must not use MTF facts.

## Review 10 (2026-10-24): check_graph.py v2 (tools fix of C1-C6) - re-test
Read the whole current file (19:00; the 18:58 edit was by an unknown agent, so I read all of it,
not a diff). Re-ran every critic/g6tests file with python3 and python3 -O:
- C1 FIXED: hdr_drop -> 2 graphs checked, K5 fails, rc=1; hdr -> C5 checked, rc=0.
- C2 FIXED: extra/trunc/pad/sp/gt/s6 -> rc=2 with a clear ERROR.
- C3 FIXED: --n 40 on the 35-vertex graph -> "FAIL: n=35, required n=40", rc=1; --n 35 -> rc=0.
- C4 FIXED: empty/blank -> "no graphs" rc=2; "?" -> "graph with 0 vertices" rc=2; count line printed.
- C5 FIXED: "FILE --k 9" honoured; unknown option -> rc=2.
- C6 FIXED: asym/loop matrix -> rc=2 also under -O.
- Regression: 0 mismatches vs mycheck on mixed1 (9904), circ39 (1320), circ40 (2920).
- New RISK (minor) C7: --selftest uses assert, so "python3 -O check_graph.py --selftest" prints
  "selftest ok" without testing anything. Main checking path has no asserts. Fix: explicit raises.
Verdict: OK for claims ("--k 10 --n 40", exit code 0 + "all pass: True").

## Review 4 addendum: cake_lpr exit code (lead/tools warning)
cake_lpr returns rc=0 also on FAILED checks. My Review 4 used stdout "s VERIFIED UNSAT", not the rc.
Tamper test: truncated LRAT, LRAT with one line deleted, CNF with one clause removed -> all rc=0,
but none prints "s VERIFIED" (messages: "empty clause not derived", "Checking failed at line ...").
The real proof prints "s VERIFIED UNSAT". Review 4 stays OK.

## Review 11 (2026-10-24): notes/cert_design.md v1 + glue (cert), on request
Reproduced: copy of cert/*.py in critic/certcopy (cert's files untouched), demo (3,5,14):
all links OK, "COVER 0-15", empty clause last, 8 s.
- X1 OK. Composition (a)-(f) in sec. 1 is sound as written for the demo (no D).
- X2 OK (cert's finding confirmed). Summary without the empty clause + valid ranges ->
  "s VERIFIED INTERVALS COVER 0-14". One range missing -> "Intervals do not reach 15".
  Changed summary or F -> "Incorrect prefix" (md5 hashes in range lines). Wrong proof for
  a line -> "Checking failed". All with rc=0. demo.py glue (exact string "COVER 0-<len>" +
  last line == "0") is correct and necessary.
- X3 GAP (n = 40). M-IS needs: every red/dom witness in the .pbp is a vertex permutation on
  edge vars (aux renamed) or MTF type, and no input deletion. Now this holds only because
  sb.write_veripb / sms2veripb.py build witnesses that way; sec. 5 lists both as untrusted.
  Need a small independent checker that parses the .pbp and checks each witness and
  deletion. Also state M-IS "up to the shift of constraint IDs" (the proof for TRI and for
  TRI + IS is not the same file: write_veripb takes nformula).
- X4 GAP (n = 40, when D is used). D is justified for models of F_def (+MTF). The model given
  by VeriPB satisfies the VeriPB core, so the core TRI must be COMPLETE (all C(40,3) = 9880
  triangle clauses); otherwise the model can have a triangle and D can fail. check_cnf
  checks soundness only. Add a completeness check (exact set of TRI clauses) on the VeriPB
  input. (S = all IS is complete by definition.)
- X5 GAP. A CNF form of D with aux variables (degree counters, e <= t) passes check_cnf only
  as --extra, so its encoding is unchecked. Proposal: put D in the core as PB constraints
  (justified by Lean, link a2), and derive aux definitions by `red` and the CNF by RUP/pol in
  VeriPB, as already done for the MTF aux variables. Same for cardinality constraints in
  sec. 3.4 (F_K with e <= 96).
- X6 OK (simplification). For the UNSAT direction without D, link (a1) needs only clause
  soundness (check_cnf), not completeness of gen.py. With D: soundness + X4.
- X7 OK. Sec. 1.1 (D after the VeriPB step) is sound for D that holds in EVERY model of
  F_def + MTF. WLOG-type facts ("vertex 0 has P") must go through sec. 3.3, never as D.
- X8 OK. Sec. 3.3 (A): checked the red obligations. With p_0 = 0, p_v = 1, w = (0 v) maps
  "p_0 or not p_v" to "p_v or not p_0" (true) and earlier "p_0 or not p_u" to "p_v or not p_u"
  (true); core invariance needs the p definitions renamed. The order change after this needs
  the derived p_0 moved to core, so later dom witnesses that move 0 are rejected by the
  checker. Sound.
- X9 RISK. Sec. 3.4 (lists as cubes inside the 40-vertex formula): the SB of the H-part must
  come from the one global order, plus X5. Needs its own review before use.
- X10 Sec. 5 table vs notes/cases.md v2: (1) add delta >= 5 (all-G split only; premise [GR] Thm 3);
  (2) the MTF split needs only e(3,9,m) for m = 30..33 (delta >= 6), and R(3,8) only for L9,
  not for the LP (no forced rows when delta >= 6); (3) e >= 161: no longer needed (cases v2 K1:
  e = 159, 160 covered with t9 <= 86); (4) add the N(t) inputs R(3,9,30,e <= t9) if done by
  gluing.
- X11 OK. check_cnf negative tests at n = 40 (44-literal IS, IS on 11 vertices, non-triangle
  TRI) -> FAIL; exact IS and TRI -> OK. demo.py uses stdout lines for veripb/cake_pb/cake_lpr
  and exit codes only for cert's own scripts (which exit 1 on failure). OK.

## Review 12 (2026-10-24): check_graph.py v3 (C7 fix) - re-test
Diff v2 -> v3 read. 0 asserts left; selftest uses explicit checks and passes under -O.
All critic/g6tests give the same rc under python3 and -O (asym/loop/blank/empty/extra/gt/n0/pad/s6/
sp/trunc = 2; hdrK5/hdr_drop/r39_35 with k=3 = 1; others 0). 0 mismatches vs mycheck on
mixed1/circ39/circ40. New: --k 0 -> rc 2; binary file -> rc 2; "~??Dhc" (long size field, n=5) ->
rc 2. C7 FIXED. Note: the selftest case "~?@D" is n = 69 (0*4096 + 1*64 + 5), so it is rejected
by the length check, not by the n < 63 check; "~??Dhc" tests that branch. Cosmetic.
critic/g6tests/mixed.g6 contains an n = 0 line on purpose; rc 2 is the intended result.
- Review 12 addendum: selftest now uses "~??Dhc" (checked, selftest ok under -O). Closed.

## Review 13 (2026-10-24): notes/cases_local.md v1 (cases), on request
- Lemma H: OK (J + I independent). Table re-derived: max |X_I| = R(3,10-s)-1 and min |N(I)|
  = 4, 11, 15, 19, 22, 26, 28, 30, 31 for s = 1..9: all OK.
- cases/etables.py: every entry for k = 3..9 equals [GR] Table 3 (and Table 4 for e(3,9,32..35)).
  Also re-derived the k <= 6 columns from [GR] Thm 2 (formula (5)). OK.
- Lemma P: OK. Edges inside S = N(u)+N(v) are exactly the A-B edges (N(u), N(v) independent);
  u, v isolated in G - S. 9-regular table rows c = 1..7 (g >= 8, 6, 4, 2, 2, 1, 4) and the class
  ranges re-computed: OK. Near-regular formula: OK.
- Lemma R7: OK (g >= 4 and g <= |A||B| = 4).
- Lemma N: OK.
- r7_glue.py encoding: COMPLETE. Fixed part {u,v}+S is determined (C, A, B independent,
  A-B complete, u-v non-adjacent). Its independent sets with |T'| >= 3 are exactly C'+A', C'+B',
  {u}+B, {v}+A ({u,v} needs |I| = 8 > alpha(X) = 7), and the code lists exactly these (no
  duplicate C'-only sets). Exact-size 10 sets suffice. Triangles: only s-y-y' (y~y') and a-b-y;
  both are encoded. Degrees: C 7, A/B 6, y 9 - deg_X(y): OK.
- Positive control (critic/r7ctl/r7_ctl.py = same script, independent-set threshold as a parameter):
  with alpha <= 10 (KK = 11), X0 -> SAT in < 10 min; decoded graph critic/r7ctl/k11/G.g6: n=40,
  9-regular, e=180, triangle-free, alpha = 10, by check_graph v3 and mycheck. So T, D and I
  clauses (and the pysat seqcounter) do what the docstring says.
- Input data: data/graphs/hog/Ramseygraphs_3_8_27_e85.g6: 4 graphs, pairwise non-isomorphic
  (labelg), all (3,8,27,85) by both checkers. Completeness of this list = [GR] Table 13 count 4
  (outside fact; HoG is the GR data).
- Minor: "nx.is_triangle_free if hasattr(...) else True" is a no-op (networkx 3.4 has no
  is_triangle_free); harmless, since the 4 graphs are checked here.
- RISK (for cert chain): conflict clauses from H1/H2 or Lemma P are not TRI/IS-shaped, so
  check_cnf rejects them; they must go through cert's D route (PB + derivation). H2 for s = 2..6
  uses e(3,k,n) for k = 4..8 (outside facts, mostly [GR] Thm 2 / [RK]).
- R7 result: pending. To count, it needs the DRAT checked (drat-trim stdout "s VERIFIED", not rc)
  and the assumptions stated (9-regular case only; [GR] Table 13).

## Review 14 (2026-10-24): cert_design v2 fixes (X3, X4, X5)
- X3 (check_pbp.py): mostly OK. Read the code; it passes on cert/demo/r3_5_14/sb_tri.pbp
  (454 perm witnesses). W (one vertex permutation, edges -> 1 allowed, aux free) is enough for
  M-IS: an IS clause maps to sigma(IS) or contains a literal mapped to 1. I, D, R checks: OK.
  NEW RISK P1: the def_order block is skipped up to the next "load_order" TOKEN, not to the
  block's own end. Test (scratchpad hidden.pbp): valid proof + a second def_order block +
  "del id 7 ;" (and "delc 7 ;") before its load_order -> check_pbp "RESULT: OK". (VeriPB 3 panics
  on my crafted order, "not yet implemented", so I could not show an accepted bad proof.)
  Also: def_order with no later load_order -> IndexError traceback (fails, but no RESULT line).
  Fix: parse the def_order block to its matching end (vars/def/transitivity/proof nesting), and
  reject any other rule inside it.
- X4 (check_cnf --opb --require-all-tri): FIXED. Tests on in_tri.opb (3,5,14): full -> OK; one
  triangle removed -> "363 distinct of 364", FAIL; one triangle duplicated + one removed -> FAIL;
  a non-clause PB line -> rejected.
- X5 (two-stage chain): logic OK. G -> model of TRI+S; proof 1 + M-IS -> model of TRI+S+MTF+SB,
  which is a (3,s,n) MTF graph (TRI complete) -> satisfies D -> model of proof-2 input + S;
  proof 2 (check_pbp-checked) + M-IS -> + D_cnf. F_cert is a subset of that.
  NEW GAP P2: satcore_cert.py takes D (lo, hi of "card degree ..." / "card edges ...") from
  satcore's own section tags. Nothing compares them with the proved bounds. A wrong tag (for
  example deg <= 3) becomes an input assumption of proof 2, and the chain accepts it. Fix: a fixed
  table of allowed D per (n, s, MTF) from the Lean/hand lemmas (e.g. n=40: 5 <= deg <= 9 all G,
  6 <= deg <= 9 MTF; e >= 159, or e >= 161 [GR161]). Each D line must be implied by a table entry
  (lo <= proved lower bound, hi >= proved upper bound).
- X9, X10: accepted by cert (not re-read in detail).
- Review 14 addendum (19:35, cert's re-check request): reproduced in critic/certrepro:
  card_demo.py 9 4 3 3 -> RESULT OK; satcore_cert.py 18 6 ... --resolve -> all sections regenerated,
  VeriPB/CakePB/check_pbp/--require-all-tri OK, satcore's own LRAT fails, CaDiCaL re-solve
  "s VERIFIED UNSAT", RESULT OK. Verdict: X4 confirmed. X3 and X5 NOT yet confirmed: P1 and P2 open
  (files unchanged since Review 14).

## Review 15 (2026-10-24): Theorem A' (notes/cases.md), on request
OK. Theorem A needs only a_v >= 1 for d(v) <= 7 (with the S8/N assumptions giving a_v >= 0, >= 1
for d = 9, 8). (RK) e(3,k+1,n) >= 6n - 13k: [GR] p.3 states it "holds for all n and k".
- d <= 6: 6(39-d) - 104 = 130, 124, 118, 112, 106, 100, 94 > d(20-d) = 0, 19, 36, 51, 64, 75, 84
  (d = 0..6). Re-computed: OK. Covers m >= 36 too, so no R(3,9) needed.
- d = 7: H = H_v, 32 vertices, alpha <= 8. H - N_H[w]: alpha <= 7, 31 - d_H(w) vertices, so
  e(H) - Z_H(w) >= 6(31 - d) - 91 (L2 inside H). Sum: sum_w (22d - d^2 - 95) >= 0;
  q(d) = 26 - (d-11)^2 concave; Jensen gives q(dbar) >= 0; dbar <= 8, so dbar >= 11 - sqrt(26) = 5.901;
  sum d >= 189 (even, so >= 190); e(H) >= 95 > 91. OK.
- The coarse split R / S8 / N(98) then needs only (RK) for k = 7, 8 (and alpha <= 9 for degrees).
GAP (stated by cases): whether the proof of (RK) for all n, k is computer-free (RK88/RK91 induction
bases) is not checked; lit owns that. Until then: "no computed table" = "only (RK), [GR] Thm 2".

## Review 16 (2026-10-24): Theorem A'' (notes/cases.md), on request
OK. MTF -> degrees 6..9 (M1, hand), so Theorem A needs only e(H_v) > 84 (33 vertices) and > 91
(32 vertices). For H on M in {32, 33} vertices: |H_w| = M - 1 - d_H(w) <= 27 by F2 (this forces
d_H(w) >= M - 28) and >= M - 9 >= 23 (d_H <= 8), so F1 applies to every H_w. Sum:
q_M(d) = (M/2 + 6) d - d^2 - (6M - 97): M = 32 -> 22d - d^2 - 95 (as in A'), e >= 95 > 91;
M = 33 -> 22.5d - d^2 - 101, smaller root 11.25 - sqrt(25.5625) = 6.194, sum d >= 204.4, e >= 103 > 84.
F1 check: e(3,8,23..27) = 49, 56, 65, 73, 85 >= 47, 53, 59, 65, 71 ([GR] Table 3). OK.
Dependencies, stated correctly: F1 (computer results: RK 1988 for m <= 26, BGS 2012 for m = 27;
no certificate) and F2 (R(3,8) = 28, DRAT-certified [DuLBG], per DS1 2.1.g). The SAT-certificate
plan for F1 (no (3,8;m, <= 6m-92)-graph, m = 23..27) would close this.

## Review 17 (2026-10-24): cert v3 (P1, P2) - re-test
- P1 FIXED. check_pbp.py on my tamper files: second def_order + hidden "del id 7" -> FAIL;
  same with "delc 7" -> FAIL; a red rule inside def -> FAIL; proof cut inside def_order -> FAIL
  ("no output section"), no traceback; def_order without load_order + edge->0 witness -> FAIL.
  Real proofs r3_5_14, r3_5_14_mtf, r3_6_18 sb_tri.pbp -> OK.
- P2 FIXED. cert/implied_bounds.txt read: rows for n = 8, 9, 13, 18 match deg >= n - R(3,s-1),
  deg <= s-1; n = 40: all 5..9, MTF 6..9, 159 <= e <= 180 (justifications cite L1, L7', M1, L5;
  L5 uses [GR] Table 4). implied(): tag lo <= table lo and tag hi >= table hi (lo <= 0 / hi < 0
  = no bound); mode "mtf" only if an MTF section is present (and certified by proof 1). Test:
  tag "vertex=3 lo=4 hi=4" -> "NOT implied" + section MISMATCH -> run aborted. Untampered
  satcore 18 deg run -> RESULT OK.
Verdict: X3, X4, X5 (Review 11) and P1, P2 (Review 14) all closed. Remaining open in the cert
design: X9 (sec. 3.4 lists as cubes, needs own review), Lean targets (M-IS, encoding, D lemmas).

## Review 18 (2026-10-24): cert sec. 5.1 (F1/F2 routes), --claim-edges-max, implied_bounds v4
- OK: implied_bounds.txt for n = 40 now has only "mtf degree 6..9" (M1 + L1, hand). Conservative.
- OK: satcore_cert --claim-edges-max E accepts an edges section only if lo <= 0 and hi == E,
  and the claim string names the edge bound.
- ERROR Q1 (soundness, not yet in any result): a claim "no (3,s,n)-graph with <= E edges" is
  NOT an implied constraint. It is true only for the graph G of the hypothesis, not for every
  model. Proof 1 guarantees only SOME model of TRI+S+MTF+SB, which can have > E edges (MTF adds
  edges; and the dominance invariant gives a model below G in the order, not G itself). So:
  (a) the claim must be in proof 1's core. The M-IS extension "IS_all + claim are closed under the
      witnesses" holds only for PURE vertex-permutation witnesses: a witness edge -> 1 (MTF red,
      allowed by check_pbp W) does not preserve "sum edges <= E".
  (b) satcore_cert.py with --claim-edges-max does not reject an MTF section. A satcore F1 run with
      --mtf would then "certify" only the MTF statement while reporting the full claim. Fix: with
      --claim-edges-max (or any non-monotone claim), require no MTF section and run check_pbp
      in a new strict mode (--perm-only: every witness is a vertex permutation, no -> 1).
  sms_card_cert.py: the docstring argument (claim closed under vertex permutations) is right, if
  check_pbp also enforces perm-only on proof 1 there. Same fix.
  The F2 route (no (3,8,28)-graph, no edge claim) is not affected: MTF is fine there.
- Review 18 addendum: Q1 FIXED. check_pbp --perm-only: MTF demo proof -> FAIL ("witness sets edge
  variables to 1"); pure-permutation proof -> OK. satcore_cert.py: --claim-edges-max + MTF section ->
  SystemExit "refused". sms_card_cert.py runs proof 1 with --perm-only. With P, M-IS extends to core
  TRI + IS_all + claim (claim is invariant under vertex permutations). OK.
  Note: implied_bounds.txt has no s = 8 rows, so satcore_cert will reject "--deg-max 7" for the F1
  runs (m = 23, 24) until rows "m 8 all degree <lo> 7" (deg <= s-1, hand) are added.
  cert reply: implied() has a built-in rule 'degree lo<=0, hi>=s-1 -> accepted' (deg <= s-1, hand, every n). Read: correct; my note on missing s=8 rows is void.

## Review 19 (2026-10-24): notes/symsat.md (symmetric-search case list), on request
Hand checks:
- F3 OK: max over a = 1..8 of R(3,a+1) + R(3,10-a) - 2 = 36, 32, 30, 30, 30, 30, 32, 36 -> 36 < 40.
- F4 OK: a fixed vertex adjacent to a p-orbit has >= p >= 11 > 9 neighbours; so no F-M edge;
  connected -> F or M empty; F empty -> p | 40. So p in {2, 3, 5, 7} (Cauchy gives a prime-order
  element in any nontrivial Aut).
- F6 OK. F7 OK: (i) |V - N[O]| >= 40 - a - p(10 - a); (ii) F - A_O inside V - N[O]. Rows re-computed:
  p=7: a <= 5, f <= 10 -> f = 5; p=5: a <= 5, f <= 18 -> {0,5,10,15}; p=3: a <= 6, f <= 28 -> 10 values;
  p=2: a <= 7, f <= 34 -> 18 values. 33 cases. OK. Outside facts: R(3,k) for k = 3, 5, 7, 8 (F7) and
  R(3,2..9) (F3), incl. R(3,9) = 36 (DRAT-certified [DuLBG]).
- Groups of order 40: n_5 = 1 (Sylow), Z5 x| P by Schur-Zassenhaus, all 5 P and all phi -> 14 classes;
  completeness does not need the iso test. OK. Cayley "maximal S only" (alpha monotone in S) OK.
  Cayley graphs are also covered by the (2,0) and (5,0) cases.
- Sec. 2 lex-leader: OK. verify_sc.py checks each breaker maps pair-orbits onto pair-orbits (this
  implies a bijection on orbit variables and that sigma-invariant (3,10,40)-graphs map to such
  graphs), one variable order for all breakers, chained-equality encoding of x <=lex x o m read
  clause by clause: correct. Note: "multiplier j -> g j" is in the normalizer only if applied to
  ALL p-orbits at once; the breaker check in verify_sc enforces the needed property anyway.
- Sec. 3 / verify_sc.py: clause classes (triangle / own lex / positive with a K-set) are sound;
  drat-trim verdict read from stdout. All 10 spec files: one generator, order p, f fixed points,
  n = 40, K = 10, matching the file name (checked by me).
  Independent re-run of case (7,5): 9880 tri + 3196 lex + 260514 positive clauses (all matched to
  logged 10-sets), drat-trim "s VERIFIED" (19.6 min on CPU 147). OK.
Findings:
- S1 RISK: verify_sc.py uses assert for the map check, the breaker check, the K-set check and
  "unexplained clause". Under python3 -O these are skipped and the script would still print
  VERIFIED if drat-trim passes. Fix: explicit raises (as in check_graph C6/C7).
- S2 RISK: verify_sc.py does not check that the spec's generator has the case's type (p, f); I
  checked the 10 current files by hand. Fix: take (p, f) on the command line and check order and
  fixed points.
- S3 RISK: no positive control for verify_sc's OWN lex encoding (calibration SAT cases used
  orbsat's). Suggest: one known SAT case (e.g. (3,9,35) with (3,5) or (7,0)) solved with satcore +
  verify_sc lex clauses -> must be SAT, model must pass check_graph.
- S4 note: calibration has no SAT recovery yet for (35: 2,1) (timeout); p = 2 SAT-finding is not
  calibrated at n = 35.
- Scope OK: all 33 closed => every (3,10,40)-graph is asymmetric (given F3, F4, F7, R(3,k) values).

## Review 20 (2026-10-24): notes/gluing.md v1 (gluing), on request
- G1 OK (method). MCMC level estimator g(e)<a>_e = g(e+1)<r>_{e+1} is exact double counting of
  (G, G + edge) pairs between levels (adding an edge keeps alpha, may only create triangles;
  removing keeps triangle-free, may only raise alpha). Valid if sampling is uniform within a level:
  toggle and edge/non-edge swap proposals are symmetric, Wang-Landau weights depend on e only. OK.
  Labelled/n! with the anchor level by sum 1/|Aut|: OK.
- G2 RISK (stated by gluing). Ergodicity is not proved: the moves need not connect the whole
  level set; an unvisited region makes true counts LARGER. Evidence against big errors: 20
  published counts within ~5% over many levels (e.g. R(3,8;24,<=63): 1.58e11 vs ~1.5e11), several
  start types agree at n = 30. So 9.5e17 is good to maybe a factor of a few; the conclusion
  "9-regular case infeasible by gluing" does not depend on that.
- G3 note. The 9-regular inputs need not be all of R(3,9;30,99): L9 gives filters (H-degrees in
  [2,8], at most 9 vertices of H-degree 8, each vertex with 1..7 neighbours in N(v)), and v can be
  chosen canonically. An MCMC estimate of the filtered fraction would make the 9-regular cost
  estimate sharper (unlikely to change the conclusion).
- G4 OK. Cost arithmetic re-done: 9.5e17 x 3 ms = 9e7 CPU-years; t9 <= 91: (4.4e10 + 5.4e9) x 4 ms
  ~ 6 y; t9 <= 92 ~ 80 y. "161 of 545 killed by t9 <= 91" = 6+8+6+15+24+43+59, and the other 384 all
  have e >= 163 (checked in cases/out/degseq_gr_mtf.json).
- G5 OK. tcheck.py logic = GR (4) with increments; exact enumeration of degree sequences; its
  e(3,k,m) table = [GR] Table 3. Ran: (3,9;31,<=96) with t6 = t7 = 3 -> OK; (3,9;30,<=87) with
  t5 = t6 = 3, t7 = 1 -> OK. Both tight: t6 = 2 (157 sequences survive) or no t7 (59 survive) -> FAIL.
- Review 19 addendum: S1-S3 FIXED (read code + logs). verify_sc/verify_cert: no assert left
  (need() exits 1); verify_sc check takes N K P F and checks one generator, all cycles of length 1 or
  P, exactly F fixed points, P prime, non-identity. S3: verify_sc's own lex clauses on known SAT
  cases n = 35: (7,0), (3,5), (5,0) SAT, models pass check_graph --k 9
  (runs/symsat/lex_poscontrol.log). S4 closed: (35: 2,1) now SAT (satcore --sbfull, 1236 s).

## Review 21 (2026-10-24): cases Sec. 4d (core cubes N(e)) and Lemma W (cases_local.md)
- Cover argument for N(e): OK. MTF G, not 9-regular, not excluded by the gluing -> L_d = U_d + 1,
  L_9 = T* + 1 for all vertices -> its distribution's LP certificate at T = t9(n) gives a 9-vertex
  with T* + 1 <= e(H_v) <= t9(n) <= t9max(e) -> relabel. Gluing runs used have no MTF / edge
  assumption, so they combine with the MTF split. Conditional on the gluing leads (no certificates)
  and on e >= 161 [GR161], as stated.
- Table re-computed from cases/out/degseq_gr_mtf.json: "none" (t9max, #dists) and "U8+N86"
  (dists with t9_U8 >= 87) equal the table for every e = 161..180. OK.
- Note: with U8+N86 the table does NOT need GR161: by K1 (Review 9), of the 28 MTF dists with
  e in {159,160}, 27 are closed by S8 and (20,20) has t9 = 86 (closed by N86). With scenario
  "none", cubes for e = 159, 160 are needed if GR161 is dropped.
- Lemma W: W1 OK. Choosing 0 = a 9-vertex with least e(H_v) keeps the cube bounds
  (min <= the LP vertex's value; >= T* + 1). W1 ("every 9-vertex x has Z(x) <= Z(0)") is mapped to
  itself by every permutation that fixes 0 and the blocks {1..9}, {10..39}, so lex symmetry
  breaking inside the blocks stays valid (the lex-least labelling in that group still satisfies
  W1). It is NOT compatible with SB that may move vertex 0 (e.g. plain SMS over all of S_40).
  W2, W3 OK. S8 analogue (8-vertices) OK. For certification, P(v) = "9-vertex with least e(H_v)"
  fits cert's red-chain WLOG (sec. 3.3): OR_v p_v holds and P is permutation-invariant.
- Review 21 addendum (satcore cubes R / A9 / A8, via cases): OK. Theorem A covers every non-regular G
  by A9 (d(0)=9, e(H_0) <= 98) or A8 (d(0)=8, e(H_0) <= 96); R = 9-regular; no e assumption needed
  (e >= 161 optional). codeg <= 7 = L6 (9+9-11). MTF is WLOG (no symmetry assumption). satcore
  --lex with --fix-nbhd is restricted to blocks {1..D}, {D+1..n-1} (notes/status/satcore.md), so it
  fixes 0 and N(0): compatible. Note: satcore's own calibration cannot find the known (3,9,35) or
  (3,10,39) graphs in 1 h, so a satcore UNSAT at n = 40 is meaningful only with its certificate.
- G6 OK (independent re-check of gluing's S8 e = 95 result). Own gluer critic/glue/myglue.py
  (CEGAR SAT, no code from gluing/): unknowns S_i = N(u_i) in H; S_i independent; deg_G(y) <= 9;
  |S_i| <= 8; NO degree lower bound (weaker than gluing's delta >= 4); alpha <= 9 by lazily added
  10-set clauses (all |K|-subsets of the u's); row-lex SB (u_i interchangeable, sound).
  Positive controls on Exoo's (3,10,39)-graph: H = G - N[v] for d = 6, 8, 9 -> SAT, and every glued
  graph passes check_graph --k 10 --n 39. Input file: 560 graphs, all (3,9,31,95) (check_graph).
  Result: 560/560 UNSAT (runs/critic/s8_e95_{a,b}.log, max 41 CEGAR rounds). Confirms "no
  (3,10,40)-graph has a degree-8 vertex v with e(G_v) = 95" (given the HoG list is complete =
  [GR] Table 14 count 560). Still no certificate (CEGAR + pysat CaDiCaL, no proof log).
- Running: same check, d = 9, on 200 random graphs of the 1800 R(3,9;30,86) (seed 2026,
  critic/glue/e86_sample.idx), CPUs 146-147, logs runs/critic/n86_{a,b}.log.
- G3 closed (gluing): L9 filter removes nothing; 472/472 MCMC samples of R(3,9;30,99) pass (H-degrees 4..8, <= 8 vertices of H-degree 8). 9-regular estimate stays ~9.5e17.
- G7 OK (sample re-check of gluing's N86 result): myglue.py d = 9 on 200 random graphs (seed 2026)
  of the 1800 R(3,9;30,86) -> 200/200 UNSAT (runs/critic/n86_{a,b}.log). Consistent with gluing's
  0 outputs from all 1800. (Sample only; no certificate.)

## Review 22 (2026-10-25): notes/cases.md Sec 6 (B1/B2), on request
- 6.1 rows OK: sum_m m p_s(m) = (s+1) I_{s+1} (pairs (S, z), z in X_S <=> S+z independent);
  sum_S I_2(X_S) = C(s+2,2) I_{s+2}; 9-regular identity e(X_S) = 9m + 9s - 180 + e(G[N(S)])
  re-derived from degree sums (e(N,S) = 9s, e(N,X) = 9m - 2e(X)); bounds: e(3,10-s,m) (H2), Mantel,
  deg_X <= alpha(X) <= 9-s, fmax(n) = min(n^2/4, 4n) (each N(S)-vertex has >= 1 neighbour in S).
  I_2 = 780 - 180 = 600, I_3 = 9880 - (3960 + 1440) = 4480: OK.
  GAP (small): I_9 >= 40 needs the 40 neighbourhoods to be distinct; true by L6 (twins would have
  c = 9 > 7). Please add that line. "Feasible" is a float LP; fine for a NEGATIVE result (ranges wide).
- 6.3 Lemma T OK (S - x and X_S lie in H_x, induced, alpha <= (9-s) + s-1 = 8). Split A_s(m0) /
  not A_s(m0) OK; not A_5(13) -> |N(S)| >= 23 OK. Table re-computed: (3,22) e = 45+f, f >= 15;
  (3,21) 36+f, f >= 15; (4,17) 9+f >= 40; (4,16) f >= 32; (5,13) e(X) = 26 = f - 18 -> f = 44 (<= fmax(22)
  = 88); (6,8) e(X) = f - 54 >= 10 -> f >= 64 (row left blank; can be added). OK. Conjecture is labelled.
- 6.4 OK: Pandey-Ravi L3.1 = L6 with c >= 1, Thm 3.6 = M1; Kruger 122 (as in Review 3).
- 6.2: empirical (n = 39), not checked.
- Review 22 addendum, Lemma Mc (cases_local.md): OK. 1440 = 40 x 36 paths of length 2, ends non-adjacent;
  600 non-adjacent pairs -> c* >= 3; c* <= 7 (L6); codeg >= 1 (L9). R(3): n1+n2+n3 = 600, n1+2n2+3n3 = 1440
  give n3 = n1 + 240 EXACTLY (note says >=; true but weaker). Block SB {0},{1..c*},{c*+1..9},{10},{11..39}: OK.

## Review 23 (2026-10-25): cert sec. 3.4 (X9, enumerated lists as cubes); b1_counts_38.md
- X9 design is SOUND in principle, with 3 conditions that the implementation must show:
  (a) The SB used in the enumeration (SMS lex-min canonical on the H-vertices) must be valid INSIDE the
      40-vertex formula: every permutation of the H-vertex positions must map the rest of that formula
      (other SB, Lemma W block clauses, degree/edge cards, the cube itself) onto itself. If the 40-vertex
      formula already has SB that touches H-vertices (e.g. vertex-0 minimiser, row lex), the two SB can
      clash and the cover becomes unsound. Need: one VeriPB proof of the COMBINED SB, not two separate ones.
  (b) Blocking clauses NOT H_i block one labelled graph. Cover is complete only because canonical
      (minimal) labelled copy is unique; so the cubes in the 40-vertex run must use exactly the same
      canonical labelling (same order, same lex-min variant) as the enumeration. State the order.
  (c) The enumerated class F_K (e.g. R(3,9,31,<=96)) must be implied by the 40-vertex case formula for
      the H-part (H = G - N[v], alpha(H) <= 9 - 1, edge bound from the case lemma); cite the lemma.
- Since 2026-10-25 the published list counts ([GR] Table 14) are TRUSTED inputs; X9 is then optional
  (only to remove the outside list). Low priority unless the lead wants a list-free proof.
- b1_counts_38.md: row sums re-added: n=26 t=0..4 = 1 767 543 = [Ang] OK; n=27 sum = 477 142 OK.
  MCMC estimates e=78..81 (sum ~1.9e9) are leads; error bar +-25% is optimistic (one seed, e=73 off by
  22%); treat as factor-2 estimates for cost planning.

## Review 24 (2026-10-25): Lemma F (cases_local.md), on request — CONFIRMED with 2 notes
- Setting: |N(u) u N(w)| = 18-c, |X| = 40-2-(18-c) = 20+c; alpha(X) <= 7 (add u,w). OK.
- (F1) re-derived: common nbr z has its 7 other nbrs in X (triangle-free); a in A has 8 nbrs in B u X,
  so e(A u B, X) = 7c + 2(8(9-c)) - 2f = 144 - 9c - 2f; e(X) = (9(20+c) - 144 + 9c + 2f)/2 = 18+9c+f. OK.
- (F2) OK (Hall/perfect matching as in Review of duo round 1; upper bound |A||B|).
- (F3) re-derived: f(v,y) = #paths v-x-z-y (x in A, z in B forced by triangle-freeness). All such paths:
  9*8*8 = 576. Paths ending in N(v): sum over ordered x != x' in N(v) of (codeg(x,x')-1) = sum_y c(v,y)^2 - 72
  (sum_y c = 72). So sum_{y in H_v} f = 576 - (sum c^2 - 72) = 648 - sum c^2. Global 12960 - sum c^2. OK.
- Split: OK. Note 1: the split needs no min-f choice ("some c*-pair has f <= 5" or "all have f >= 6",
  a labelling-free dichotomy); the min-f choice is only an extra SB. Within-block permutations fix (0,10)
  and preserve all f values, so it is valid. Do NOT combine it with a different vertex-0 rule (Lemma W).
- c* = 6: e(X) = 72+f, f in 3..9; f* <= 5 -> e in 75..77; GR T13 row 26: 23409+216151+1526296 = 1 765 856. OK.
- Note 2: c* = 7: (F2) alone gives f >= 2, not 4. f >= 4 comes from Lemma P (g >= 4 for c = 7, duo/Lemma P
  table). Cite Lemma P there. Then f = 4, e(X) = 85, R(3,8;27,85) = 4 graphs. OK.
- c* = 5: e(X) = 63+f, f >= 4. OK.

## Review 25 (2026-10-25): symsat F10 (order-2, a = 7 shortcut) + symsat/ext27.py, on request — CONFIRMED
- (1) Equality: by F6 each x in O has N(x) cap F = A_O (7), so <= 2 nbrs in M; |N[O]| <= 13, Lemma L
  gives |V - N[O]| <= 27, so |N(O) cap M| = 4: deg x = deg x' = 9 and the M-nbr pairs are disjoint. OK.
- (2) H fixed points = F - A_O (a fixed vertex outside A_O has no nbr in O by definition of A_O); moved
  points in H: |M| - 2 - 4 = 34 - f (even). Total 27. sigma|H = id iff f = 34. OK.
- Involution types: INDEPENDENT check (own backtracking involution search, critic scratch inv.py, on the
  2545 graphs with |Aut| > 1 by countg/pickg; 474597 have |Aut| = 1): fixed-point counts of all involutions
  = {1: 2263, 3: 250, 5: 35, 7: 6, 9: 2, 17: 1}. Same set as symsat. So f in {18,..,32} \ {24} closed. OK.
- (3) ext27.py breakers sound: A rows have no A-A, A-B, A-x/x' freedom (all fixed), so their only free
  entries are the H-columns; any permutation of A commutes with sigma (A fixed) and keeps every fixed
  part -> sorting rows is WLOG. Swap pi = (b1 b2)(b1' b2') commutes with sigma, keeps N(x), N(x') -> rb1 <=lex rb2
  WLOG; acts on rows disjoint from A, so both breakers combine. lex_le encoding checked. Naming b1' = sigma(b1)
  is WLOG (sigma maps N(x) cap M onto N(x') cap M). Class reps by conjugation over all of Aut(H): OK
  (any G gives sigma|H conjugate in Aut(H) to a rep after relabelling H by an isomorphism).
- Not a certificate: UNSAT from pysat/cadical153 with CEGAR IS-clauses, no proof log -> a lead per
  TEAM_RULES. A SAT answer needs check_graph (indep_with may be heuristic).

## Review 26 (2026-10-25): duo fractional regular-gluing LP (duo/codex_r2.md item 1), on request — Claim A CONFIRMED
- Claim A: e(H) = 180 - 9 - 72 = 99, |H| = 30, alpha(H) <= 8 (add v). S_i independent 8-sets (N(x_i) - v).
  Distinct: S_i = S_j gives codeg(x_i,x_j) = 9 > 7, against L6; needed for z <= 1. Please cite L6.
  Degree: #{i : y in S_i} = |N(y) cap N(v)| = 9 - deg_H(y). T-rows: x_i pairwise non-adjacent and
  non-adjacent to T when S_i cap T empty, so T + those x_i is independent: k <= 9 - |T|. OK.
  With degree EQUALITIES, sum z = (sum_y (9 - deg_H y))/8 = (270 - 198)/8 = 9 automatically, so the eq-LP
  is a pure feasibility test; infeasible => H has no extension. Inequality version: max < 9 => none. OK.
- Code: fraclp.indep_sets enumerates exactly the independent k-sets (candidate mask drops nbrs and
  indices <= i). build() rows match the claim; D rows as A_eq in adv6/adv5 (and as A_ub in the
  "v678" variant): OK. adv_c35 filters alpha(H) <= 8 after the edge removal (needed: removing an edge can
  raise alpha): OK. Classification uses float tolerance 1e-6..1e-7; some values are close (8.99452,
  8.9965), so before any claim: exact rational Farkas certificates (as cases/verify_certs.py does).
- Scope: a test on one family (1209 graphs from C35), not a result for R(3,9;30,99).

## Review 27 (2026-10-25): cases Sec 7, 7 profile-LP kills (mforce.py build, mforce_cert.py) — CONFIRMED (conditional on scen. sel)
- Rows re-derived: e(H_v) = e - Z(p) (N(v) independent, so edges meeting N[v] = sum of nbr degrees). Profile
  filter e - Z >= max(L_d, e(3,9,39-d)) (E9 = [GR], L_d = scenario sel, conditional) and Z >= d^2-11d+78 (M2, MTF;
  Review 9). p_j <= n_j - [j = d] OK. m_ij rows (i != j two-sided; 2 m_ii) OK.
  Mantel rows: blow up each d-vertex into x_d in {0..3} twins -> triangle-free graph on sum x_d n_d vertices with
  sum x_i x_j m_ij (i<j) + sum x_i^2 m_ii edges <= floor(N^2/4). OK. Box x <= n_d, m_ij <= min(i n_i, j n_j) valid.
- Certificate test: y >= 0, y^T A' x >= sum_k min(0, c_k) u_k on the box; > y^T b' gives contradiction. Exact Fractions. OK.
- Re-ran `mforce_cert.py --check` myself (CPU 146): 7/7 VERIFIED. All 7 distributions sum to 40.
- Scope: valid for MTF G only (M2), and only under scenario sel (gluing T* = 90, U8..U6), as stated.

## Review 28 (2026-10-25): duo/codex_r4.md sec. 1, "m >= 13" excess lemma — CONFIRMED (conditional on sel; MTF degrees 6..9)
- (1): sum_v [e(H_v) - d(20-d)] = (40e - sum d^2) - (40e - sum d^2) = 0. Lower bounds L_d - d(20-d):
  8: 100-96 = 4, 7: 113-91 = 22, 6: 122-84 = 38. OK. Degree 9: e(H_v) - 99 = (81 - Z) - q >= -q, and >= 91-99 = -8. OK.
  Bad (e(H_v) >= 99) contribute >= 0. OK.
- (2): e(C9) = (9n - 8a - 7b - 6c)/2 + e(D) (degree sum); e(D) >= |D| - 9 (alpha). OK.
- (3): bad v: nbr deficiency sum >= q, so >= k nbrs in D, <= r = 9-k in C9; both Mantel forms OK.
- Finite check RE-RUN by own script (critic scratch m13.py): survivors at m <= 12 are exactly the 8 listed (all m = 12).
- Special cases re-derived:
  * 7-/6-vertex w: e(H_w) >= L_d gives nbr deficiency >= q - 4 (7: Z = 63 - def <= 67 - q; 6: Z = 54 - def <= 58 - q).
  * b=1, a=12/14/16: alpha(D) >= |D| - 1 - e(D) + d_D(w) (delete one end of each edge not at w, then w) -> e(D) >= a+q-13;
    E0 = 76/62/48; ub = 36 + r(n-m) - (n-m-9) (bad set has alpha <= 9) = 75/58/45. Contradiction. OK.
  * (18,1,0): q = 10 > 9 forces every bad vertex to touch w; w has >= 6 nbrs in D, so <= 1 bad; n-m = 9. OK.
  * b=2, a=10/12: S = sum_x def(x) d_D(x) >= 6q-32 (edge w1w2 counts 4, w-8 edges 3; t_i >= q-6). Bad vertices
    receive >= q each: (n-m) q <= sum def*d - S = 108-10 = 98 / 124-16 = 108 -> m >= 14 / 13. OK.
  * c=1, a=11/13: S >= 4(q-4); (n-m) q <= 106-12 / 122-16 -> m >= 15 / 13. OK.
- Corollary: 13 selected vertices, alpha <= 9 -> >= 4 edges among them -> an adjacent selected pair. OK.
- Scope: MTF (degrees 6..9 by M1), e >= 167, non-regular, conditional on scenario sel exclusions.

## Review 29 (2026-10-25): notes/SCOUT.md (scout), Test A WLOG + flip-cover negative — CONFIRMED with notes
(1) Test A, case R (9-regular). q(v) = sum_w C(c(v,w),2) = #C4 through v (triangle-free: c(v,w)=0 for w~v, and each C4
through v has one opposite vertex). sum_v q(v) = 4 C4 holds. Relabel an argmax-q vertex as 0: valid WLOG; the rows
"q(u) <= q(0) for all u" are invariant under any permutation that fixes 0 and the blocks {1..9},{10..39}, so they are
compatible with SMS --initial-partition 1 9 30, NOT with S_40-wide breaking. "Replace, not join" is CORRECT: Lemma Mc
picks 0 as an end of a c*-pair (and Lemma F a min-f pair), Lemma W picks min e(H_v); a q-max vertex need not satisfy them.
Only a lexicographic join is valid (e.g. among ends of c*-pairs choose max q; then the rows hold only for u that are
ends of c*-pairs). Outside case R the rule must be restricted to u with d(u) = d(0).
Free facts for the encoding: in R, sum_w c(0,w) = 72, so q(0) = (sum_w c(0,w)^2 - 72)/2, and by Lemma F (F3)
sum_{y in H_0} f(0,y) = 576 - 2 q(0): max q = min total f at vertex 0. Global floor: all c in {2,3} minimises
sum C(c,2) -> sum_pairs C(c,2) >= 1080 = 2 C4, so C4 >= 540 and Q = q(0) >= 54 (mean q >= 54).
(2) Flip-cover negative. Re-ran scout's flipdeg.py (n=30, <=87 class, 1000 graphs, seed 1, labelg) on CPUs 146-147:
mean 1.607, 95 zeros, 835 with exactly 1; the n=31 file on disk gives mean 2.03 (863 with 1). Both CONFIRMED.
Note: means are inflated by a few outliers (8 graphs with 81, 16 with 64 neighbours); medians are 1.
Stronger form: in an exact cover by generalizations (subcubes of the flip graph inside the class) a graph with
in-class flip degree d lies in a piece of size <= 2^d, so #pieces >= sum_G 2^-d(G). Sample bound: gain <= 1.89 (n=30),
<= 2.01 (n=31). So "<= ~2x" is a sound bound for exact covers (sample estimate). Supersets = batching (Wesley W1), as scout says.
Caveat: runs/scout/flips*.g6 are overwritten per class; the n=30 data on disk are now from n=31.

## Review 30 (2026-10-25): edge-kernel lemma, runs/lead/codex_strategy_3.md Sec 2-3 (for duo) — CONFIRMED with notes
Sec 2 (R, 9-regular). Checked each step: A,B disjoint independent 8-sets; d_F(a) = c(a,v) - 1 <= M-1 (u is a
common nbr); alpha(F) = 16 - nu(F) <= 9 (König; A u B independent in G off F) -> nu >= 7. t1 <= 160: for x in N(w),
{y in N(w): c(x,y)=1} u N(x)-w is independent, so r <= 1; each codeg-1 pair lies in exactly one N(w); floor(9/2)*40.
Chord bound: c(c-1) <= (M+1)c - 2M on 2..M (convex, chord through (2,2),(M,M(M-1))), deficit M-1 at c=1, and c=0
cannot occur (d(x)=9: N(x)+y would be an independent 10-set) -> sum <= 1440(M+1) - 1200M + 160(M-1).
sum_nonedges c(c-1) = 4 C4; e(F_uv) = #C4 through uv; sum over 180 edges = 4 C4 -> min e(F) <= floor((20M+64)/9)
= 13,16,18,20,22 for M = 3..7. All correct. genbg ranges (-D3 7:16, -D4 7:18, -D5 7:20; M=7: -D6 7:22) match.
Sec 3 (MTF, fixed distribution). r <= 10 - d(x) and t1 <= T = floor(sum d(10-d)/2) correct; c >= 1 needs MTF (core
lists are MTF: core_cubes.json common.mtf = true). |A| = a-1, |B| = b-1, nu >= a+b-11 correct. Recomputed B at M=7
from cases/out/core_cubes.json: scenario "sel" (207 dists) 17..22 = claim; "none"/"U8+N86" (544/530) 14..22.
Notes: (a) T is loose: for 9-regular it gives 180 (not 160) and B = 23 (not 22); per-vertex floor needs nbr degrees.
(b) Extra valid WLOG: the chosen edge minimises e(F), so add "#C4 through xy >= e(F_uv) for every edge xy" in the
completion SAT; valid only with symmetry breaking that fixes the kernel blocks {u},{v},A,B (no S_40-wide SB).
(c) Completion must also assert codeg <= M on all nonedges (and in Sec 3 the exact distribution); with M exact,
cases are disjoint, with "<= M" they nest — both sound. (d) u<->v swap is an extra kernel symmetry (genbg keeps parts
apart): sound to ignore, up to 2x saving. (e) Sec 3 core list "sel" is conditional on the sel exclusions (as codex says).

## Review 31 (2026-10-26): gluing final40 (deg 8: e(G_v) >= 97; deg 9: e(G_v) >= 88) — CONFIRMED (enumeration + sample)
- Reduction: d(v)=8 -> G_v = G - N[v] in R(3,9;31); d(v)=9 -> R(3,9;30) (alpha(G_v) <= 8 since v is free of G_v). OK.
- Inputs: gluing/cls/S8_in96.g6 = 35,154 graphs, all n=31 e=96; N_in87.g6 = 147,335, all n=30 e=87; labelg: all
  pairwise non-isomorphic; check_graph --k 9: all triangle-free, alpha = 8. Counts = [GR] T14; with the e=95 (560)
  and e=86 (1800) levels (Review 21, G6/G7) and e(3,9,31)=95, e(3,9,30)=86 [GR], the <=96 / <=87 classes are complete.
- runs/gluing/final40.log: 24 glue2 parts (K=9, deg=[4,9], no edge bound, no MTF), inputs sum 182,489, all out=0.
- Own gluer (critic/glue/myglue.py, CEGAR SAT, no degree lower bound, venv pysat on <server>), seed 2610:
  positive controls d=6,8,9 on Exoo (3,10,39) -> SAT; 100/100 e=96 (d=8) UNSAT; 100/100 e=87 (d=9) UNSAT
  (runs/critic/f40_e96.log, f40_e87.log; max 46 CEGAR rounds). Sample only; no certificate (as claimed).

## Paper sign-offs (paper/draft.md; started 2026-10-26)
| Sec | Owner | Status | Review |
|---|---|---|---|
| 1 | tlead | SIGNED OFF (fixes checked) | Review 36 |
| 2 | cases | SIGNED OFF | Review 34 |
| 3 | cases | SIGNED OFF (fixes 1-4 checked) | Review 34 |
| 4 | cases | SIGNED OFF (re-check lean update) | Review 34 |
| 5 | symsat | SIGNED OFF after fixes 1-2 | Review 33 |
| 6 | gluing | SIGNED OFF after fixes 1-2 | Review 32 |
| 7 | sms | SIGNED OFF (fixes checked; e(3,7,17/18) certs re-run OK) | Review 35 |
| 8 | sms + duo | SIGNED OFF (fixes checked) | Review 37 |
| 9 | tlead | SIGNED OFF (fixes checked) | Review 36 |

## Review 32 (2026-10-26): paper Sec 6 (gluing) — SIGN-OFF after 2 fixes
Checked against logs: CPU d=8 6,962 s / d=9 64,481 s (final40.log sums); e=95 121 s, e=86 879 s (n40/*.err);
generation 67,012 s (A6) and 36,991 + 255,767 + 96 = 292,854 s (B5/B6/B7) ~ 293,000 OK; inputs 132,817 =
51+3419+129347, 3 x 121,461(2) = 364,384 = 102+8241+356041 OK; t9_88.log: R(3,8;23,<=52) = 10,691,100 and
R(3,8;22,<=44) = 73,895 = sum of checked levels OK; "20 of 545" = cases.md l.302 (85:6, 86:8, 87:6) and l.323
(14 + 6 by S8) OK; MCMC table and checks = gluing.md Sec 2 (worst 30% n=33; R(3,8;26,<=77) 1.80e6) OK; cost lines
= gluing.md Sec 4 (0.9 y, 80 y, 9e7 y) OK; R(6) 6.6 s + 462k x 5 ms ~ 40 min/X, x 1.77e6 ~ 130 CPU-y OK.
FIX 1 (error): 6.1 "alpha(G) <= 10 iff" must be "alpha(G) <= 9 iff" (|K| + alpha(G_v - U S_i) <= 9; sets with v
need alpha(G_v) <= 8, which holds).
FIX 2 (status): rows e=96, e=87 -> "enumeration-only; CONFIRMED (critic Review 31: all inputs valid and pairwise
non-isomorphic; own SAT gluer 100/100 UNSAT per class, sample)"; "Review on final classes" -> "Review 31".
Optional: say that the d=6 run alone already gives all 149,135 (B5: 149,106, B7: 0), a good internal cross-check.

## Review 33 (2026-10-26): paper Sec 5 (symsat) — SIGN-OFF after 2 fixes
Proofs re-done: F3 (max_a [R(3,a+1)+R(3,10-a)-2] = 36 at a=1) OK; F4, F6 OK; F7: (p-1)a <= 10p - 41 + R(3,10-p),
f <= a + R(3,10-p) - 1 -> p=7: a<=5, f=5; p=5: a<=5, f<=18; p=3: a<=6, f<=28; p=2: a<=7, f<=34; 1+4+10+18 = 33 OK.
Subcase ranges a = max(1, f-R+1)..min(f, a_max) give 17 + 98 = 115 OK. Lemma 5.3 = Review 25 (fixed points of
sigma|H = f-7; 27 odd) OK. Group facts (Sylow, S-Z, Aut Z5 = Z4) OK; Method A maximal-set argument OK
(a superset with |S| >= 10 has alpha >= 10).
Data: subcase table 5.4 = sub_search.jsonl + rerun1.jsonl exactly (52 U / 63 T, all dmin 5, sb full); no (p,f)
row fully closed OK. Theorem 5.2 runs (n40_satcore.jsonl): 9 UNSAT, dmin 4, 5.25-110.1 s; (7,5) 6.81, (5,15) 7.16,
(5,10) 46.16, (5,5) 1321.55 OK; certs_status.txt 9 VERIFIED (verify_sc clause provenance + drat-trim) OK;
cayley_verify.log 14/14 VERIFIED; cayley_all.log min alpha 10 (12 groups), 11 (G1, G13) OK; p50_search 86,401 s
TIMEOUT OK; calibration 139/133/0 = symsat.md l.205-212 OK.
FIX 1 (error): the two groups with min alpha 11 are G1 = Z5 ⋊ Z8 (|phi(P)| = 4) and G13 = Z5 ⋊ Q8 (|phi| = 2),
not "Z8 ⋊ Z4 and Q8 ⋊ Z2" (those groups have order 32 and 16).
FIX 2 (wording): only the 14 class representatives are searched (G0..G13), not all 28 products. Completeness
holds because each deduplication is an explicit isomorphism checked as a bijective homomorphism (groups.py
isomorphic()). Say that (or run Methods A/B on all 28; < 1 min).
Update: ext27 certificates now 2550/2557 VERIFIED, 0 failed (f8 2263, f10 250, f12 35, f16 2 done; f14 6 + f24 1
pending) — replace 2542 at the [TODO].

## Review 34 (2026-10-26): paper Sec 2-4 (cases) — SIGN-OFF after 4 small fixes
Re-proved: L1, L2-L4 (e(G_v) = e - Z(v), N(v) independent), L5 (Delta = 9), L6 (+ n4+n5 <= 2), L7, M0-M3 (M1:
d(20-d) >= 78; M2 values 48/50/54/60), Theorem A (a_v >= 13 for d <= 7: 104-91, 118-84, ...), L9, Lemma P (R: e(X) =
18+9c+f), Lemma F (F2 via König, F3 = 9*72), Mc, R7 (81+f >= 85), R(6) class 23,409+216,151+1,526,296 = 1,765,856.
Data: cases_gr_mtf.csv: 545 rows; t9_U8 <= 87: 20 (all e=161; e=161 has exactly these 20); open 525; t9=88: 15;
per-e "open" and "t9max" rows equal the csv exactly; multiplicities sum to 545; ranges n4=n5=0, n6<=9, n7<=19,
n9>=2, e 161..180 OK. 19,890 = 7631+2176+7797+2286 (cases.md l.264). 28 extra e in {159,160}: 27 by S8, 1 by N86
(cases.md K1) OK. Lean: all cited names exist in lean/R310; scripts/Axioms.lean has 263 '#print axioms'; no
sorry / native_decide / axiom in R310; toolchain v4.35.0; OPB headers 99,701 / 99,700 / 99,700 OK.
FIX 1: 3.1 "delta >= 5 [cert ...]" also uses D-G1 ([GR] Thm 3) — add it (Sec 5 already says so).
FIX 2: Theorem A proof only shows the "98 / not regular" claim. Add: for the first claim, a_v >= 1 at every
9-vertex (e(G_v) >= 100), so sum a_v > 0 also for regular G.
FIX 3: 3.7 R(6): "all 9 sampled X timed out (>= 1 h by SAT)" — I found no log; cite it or drop it (gluing's
40 min/X is logged).
FIX 4: 3.9: the 4.4e7 unique kernels are the near-regular catalogue with M <= 6 (DIGEST l.107), not case R; say so.
Sec 4 may change after lean's answer; re-check only changed lines.

## Review 35 (2026-10-26): paper Sec 7 (sms) — SIGN-OFF after 2 fixes
Checked: F1 m=23/24/27 cert logs (runs/cert/f1/cert_f1_*.log): RESULT OK certified; Lean sbcheck on ALL SYM
(71,031 / 112,512 / 65,321; 10.4 / 18.4 / 12.6 s), VeriPB/CakePB proof 1 on 500-sample, proof 2 full, check_cnf,
cake_lpr 403.3 s (m=23); IS counts 27,522 / 45,786 / 52,044 OK; SMS WALL 3,093.6 / 8,970.1 / 5,503.2 s OK.
e(3,7,19), (3,7,20): cert logs OK (full VeriPB + CakePB proof 1, no sbcheck), IS 3,871 / 7,410 OK.
R(7): base_Rc7b.log RESULT OK (2m21s); cover: cake "s VERIFIED UNSAT", sbcheck "s VERIFIED 684 clauses",
check_cnf IS 4,214, re-check "s VERIFIED cube"; DONE.json 365 UNSAT / 99 TIMEOUT, 365 VERIFIED, stats = text.
rc7_check.sh demands cake_lpr + coarse sbcheck + check_cnf + partition test + fine-block sbcheck, and fails if
the witness file is missing: link (c) scope holds (sbcheck on full SB lists; VeriPB/CakePB samples only for F1).
subA 37/12,409 UNSAT+VERIFIED, 9h16m OK.
FIX 1: e(3,7,17), e(3,7,18) rows "certified": runs/cert has no cert log for them (edge_scan/e_7_1{7,8}.log are
satcore runs without proof). SMS proof logs exist (runs/sms/emin_7_1{7,8}_*.log, WALL 1.57 / 4.38 s) and
cert_design.md Sec 3.7 says certified. Give the cert log path, or re-run sms_card_cert.py (~1 min), else label
"enumeration".
FIX 2: 7.4 split: "37 parents (1 kept whole) -> 12,409 sub-cubes; 62 parents (6 kept whole) -> 1,668,706"
(rc7_splitA/B.log).
Fixes 1-4 of Review 34 checked in draft (2026-10-26): OK; R(6) logs r6f/x7{5,6,7}s: 2+1+6 = 9 X, all rc 124 (timeout 1 h / 2 h).

## Review 36 (2026-10-26): paper Sec 1 + Sec 9 (tlead) — SIGN-OFF after 4 fixes
Checked each item of the result list against Sec 2-8 and Reviews 31-35.
FIX 1 (error, item 6): "Each is at least about 1000 times over a 180 CPU-year budget" contradicts Sec 8: cube R
has a firm lower bound of only ~1e9 CPU-s (30 CPU-years; probe mean 8.4e14 is a heavy-tailed estimate), t9 <= 90
gluing is ~0.9 CPU-year (feasible, closes only part), near-regular kernels 4.4e7 x >= 1 h ~ 30x budget. Say instead:
"none of them closes the remaining cases within the budget by our estimates; the main routes for case R are
estimated at 1e2..1e7 times the budget (heavy-tailed estimates, not proofs)".
FIX 2 (status, item 3): "order 2 with a = 7 is closed except f = 34" is enumeration (2557 extension runs;
certificates 2550/2557 so far) plus proof (empty f); label it so. Also "certified or proved" there must not cover
(5,5) (enumeration).
FIX 3 (citations): [Ex5], [GoeR1] are not our IDs; use [Ex89] and [GR] (Sec 2.3, DEPENDENCIES.md).
FIX 4 (Sec 9): final40 used glue2 (runs/gluing/final40.log), so list glue2 with glue and glue5; also name symsat's
orbit-SAT code and satcore. SMS is third-party (Kirchweger-Szeider): release our patches with its licence terms.
Item 4 "independently checked": say "sample-checked by independent code (Review 31)".

## Review 37 (2026-10-26): paper Sec 8 (sms + duo) — SIGN-OFF after 5 fixes; round-6 q(v) bounds CONFIRMED
Round-6 bounds (duo/codex_r6.md): q(v) = 54 + h1 + h4 + 3h5 + 6h6 + 10h7 OK (C(c,2) = -3 + 2c + g(c), g = 1,0,0,1,3,6,10;
sum h = 30, sum c h = 72). h7 <= 1 and (h7 > 0 => h6 = 0): two non-nbrs w,w' of v with c1+c2 >= 13 are non-adjacent
and leave |X| >= 10 + c1 + c2 > 22 = R(3,7)-1 OK. h6 <= 2 (three -> |X| >= 18 > 17) OK. h1 <= 9 (Lemma N); sum_v h1 <= 320
(t1 <= 160). h7 > 0 => h1 <= 7: Lemma R7 (A-B complete); a private y of a in A gives {y} + B + C independent, size 10
(y !~ B, else triangle with a) OK — this uses Lemma R7, i.e. F2 + e(3,8,27) >= 85 (D-E8). My enumeration: exactly 769
candidates, max q = 87 at (9,14,1,0,4,2,0), max (q - h1) = 78, so 4 C4 <= 40*78 + 320 -> C4 <= 860 OK. Without the
h1 <= 7 rule max q would be 88 and C4 <= 870, so the rule is needed. Extra subset rules (k >= 3 vertices with c >= 5)
remove no candidate.
8.1: core_cubes.json U8+N86 with t9 >= 88: 18 cubes, 524 dists, e = 162..179 OK (= Sec 3.5).
8.2 probes (runs/sms/probes/*.jsonl ESTIMATE lines): R 67, median 8.0e4, mean 8.4e14, 2e2..4.3e16 OK; R(6) 3,
mean 1.9e12 OK; R(4) 7.5e8 OK; Rc6f6 8.0e9 / 1.4e11 / 1.7e13 OK; R(7) real run 2.31e6 / 1.85e5 OK.
8.4 kernels: catalogue sums 96,135 / 2,852,820 / 26,326,286 OK; s40 res.txt: M4 2/3 solved (5, 16 / 5, 19, 1782),
M5 0/0, M6 1/1 (1.7 / 1.1) OK; bounds 3.25e8, 1.03e10, 9.18e10 OK; c35_a1 26 runs 11 UNSAT 15 TO, 57,677 s OK;
c22 474/474 finished.
FIX 1 (8.4 q bounds): state h1 <= 9, sum_v h1 <= 320 and "h7 > 0 => h1 <= 7 (Lemma R7; uses F2, D-E8)"; without
them 87 / 860 do not follow. Label: hand, CONFIRMED critic Review 37.
FIX 2 (8.2): "1/3 of the R probes give more than 1e9" -> data: 15 of 67 (22%).
FIX 3 (8.2): "Our R probes are 1e2..1e8 times that [1.2e7]" is wrong: single estimates are 2e-5 .. 4e9 times it, the
median (8e4) is below it; the mean is ~7e7 times it. Rephrase.
FIX 4 (8.2 table): R(7) median of the 6 probes is 6.3e5 (not 1.3e6); R(3) now 21 probes, median 7.6e5, mean 7.7e9,
14% > 1e9; C1: the 30 probes on disk give median 1.3e7, mean 5.0e10; the old 14-probe set (4.0e6 / 1.4e10) has no
ESTIMATE lines in runs/sms/probes/old_assumptions — cite where it is, or give only the 30.
FIX 5 (8.4): "about 18 times what the team can use in a year (5.7e9 CPU-s)": 5.7e9 CPU-s is the whole 180 CPU-year
budget. Say "about 18 times the full budget".
Minor: c22 control times in res.txt sum to 116 s / 113 s (text: 104 / 102 s).
Paper review complete 2026-10-26: all 9 sections signed off, all fixes checked (Reviews 32-37).
F10 re-check 2026-10-26: ext27_verify*.log = 2557 distinct VERIFIED (f8 2263, f10 250, f12 35, f14 6, f16 2, f24 1), 0 fail; Sec 1 item 3, Sec 5.5, 5.6 lines OK (trust base nauty + McKay list stated).
Sec 5 re-check 2026-10-26 (symsat changes): rerun1 73/73 (11 UNSAT, 62 TO); merged 53 U / 62 T OK; (2,26,7) UNSAT 8949.7 s OK;
f=34 sample 11/11 UNSAT, 4177.5 s -> 380 s/graph, x 477,142 ~ 5.0e4 CPU-h OK. ONE FIX: 3 of the 62 timed-out subcases,
(2,28,7), (2,30,7), (2,32,7), are closed by proof (Lemma 5.3, f-7 in {21,23,25} not an involution type), so "the other
62 are open" -> "59 are open; 3 more ((2,f,7), f = 28, 30, 32) are closed by Lemma 5.3". Sec 5.6 line likewise.

## Review 38 (2026-10-26): LaTeX conversion paper/latex (cases) — SIGN-OFF after 2 fixes
(1) Numbers: critic/latexcheck/seqdiff.py (per-section number sequences, draft.md vs secN.tex, after removing \ref/\cite,
column widths, LaTeX spacing and 1e9 <-> 10^{9} / a\cdot10^{b}): every remaining difference is a section number now
given by \ref, a citation year/volume moved to refs.bib, C(9,2) -> \binom{9}{2}, NOT -> \lnot, or a \texorpdfstring
duplicate. No number changed. Status words per section (certified, CONFIRMED, enumeration, NOT) equal; review
numbers equal. The one content change (Sec 3.6 "Sec. 4.4" -> 4.3) is correct (Files.cover_files_sb is item 5 of 4.3).
(2) Build: main.log has no undefined refs/citations, no overfull boxes, no errors; blg 0 warnings; no "??" in pdftotext.
(3) refs.bib: 24 entries, 22 cited (main.bbl 22 bibitems); entries checked against my knowledge of the sources and
DEPENDENCIES.md: OK. 
FIX 1: 49 citations are still literal text ([GR] x27, [Ang] x12, [McZ] x4, [DuLBG] x4, [GrR] x2) plus an inline
"[KS24: Kirchweger, Szeider, ACM TOCL ...]" in Sec 7; with bibliographystyle plain the PDF then mixes "[GR]" and
numeric "[7]". Use \cite{...} everywhere (or an alpha-type style whose labels are the keys).
FIX 2: Ex13 and GRK10e are in refs.bib but never cited: cite them or remove them ("24 entries" -> 22).
Note: DuLBG pages 2619-2627 and DS1 "Revision #18, April 24, 2026" I could not confirm offline; check them against
the IJCAI-25 proceedings and the DS1 page before submission.
Review 38 fixes checked 2026-10-26: 0 literal cites left; 22 bib = 22 bibitem; keys.bst labels [GR], [Ang, Sec. 4], ...; build clean (0 undefined/overfull/errors, 0 '??'); number diff unchanged (only cite-option moves). DS1 rev 18 date confirmed from local copy. Open: DuLBG pages (needs online check).
