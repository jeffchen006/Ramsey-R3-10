# Prior certified computer proofs: how each link of the chain was handled

Purpose: input for the certificate-chain design of "no (3,10,40)-graph" (triangle-free, n=40, alpha<=9).
Method: full text of each paper was read (pdftotext of arXiv/proceedings PDFs) on 2026-10-24.
Tags: [S] = stated in the cited source (section given). UNVERIFIED = not confirmed in a primary source.
"Our note" = our inference, not a claim of the paper.

Primary sources used:
- [DuLBG] Z. Li, C. Duggan, C. Bright, V. Ganesh, "Verified Certificates via SAT and Computer Algebra Systems for the Ramsey R(3,8) and R(3,9) Problems", IJCAI 2025, pp. 2619-2627, doi 10.24963/ijcai.2025/292; arXiv:2502.06055v2. https://arxiv.org/abs/2502.06055 . Code: https://github.com/ConDug/MathCheckRamsey
- [BHMN] J. Brakensiek, M. Heule, J. Mackey, D. Narvaez, "The Resolution of Keller's Conjecture", IJCAR 2020 (LNCS, doi 10.1007/978-3-030-51074-9_4); journal version JAR 2022 (volume/pages UNVERIFIED); arXiv:1910.03740. https://arxiv.org/abs/1910.03740
- [GCAH26] J. Gallicchio, C. Codel, J. Avigad, M. Heule, "An End-To-End Verification of Keller's Conjecture", ITP 2026, LIPIcs 26:1-26:20, doi 10.4230/LIPIcs.ITP.2026.26. https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.ITP.2026.26
- [Clune23] J. Clune, "A Formalized Reduction of Keller's Conjecture", CPP 2023, doi 10.1145/3573105.3575669 (abstract only read).
- [Schur5] M. Heule, "Schur Number Five", AAAI 2018, doi 10.1609/aaai.v32i1.12209; arXiv:1711.08076. https://arxiv.org/abs/1711.08076
- [HS24] M. Heule, M. Scheucher, "Happy Ending: An Empty Hexagon in Every Set of 30 Points", TACAS 2024; arXiv:2403.00737. https://arxiv.org/abs/2403.00737
- [SNGCCH24] B. Subercaseaux, W. Nawrocki, J. Gallicchio, C. Codel, M. Carneiro, M. Heule, "Formal Verification of the Empty Hexagon Number", ITP 2024, LIPIcs 309, 35:1-35:19; arXiv:2403.17370. https://arxiv.org/abs/2403.17370 . Code: github.com/bsubercaseaux/EmptyHexagonLean
- [Sz26] S. Szeider, "Streaming LRAT Certificates into Lean Theorems", arXiv:2607.00815v2 (Sep 2026). https://arxiv.org/abs/2607.00815 . Tool: github.com/leansolving/lrat-catcher
- [BGMN23] B. Bogaerts, S. Gocht, C. McCreesh, J. Nordstrom, "Certified Dominance and Symmetry Breaking for Combinatorial Optimisation", JAIR 77 (2023) 1539-1589 (AAAI 2022 conf. version); arXiv:2203.12275. https://arxiv.org/abs/2203.12275
- [A+26] M. Anders, B. Bogaerts, B. Bogo, A. Gontier, W. Koops, C. McCreesh, M. Myreen, J. Nordstrom, A. Oertel, A. Rebola-Pardo, Y.K. Tan, "Faster Certified Symmetry Breaking Using Orders With Auxiliary Variables", AAAI 2026; arXiv:2511.16637. https://arxiv.org/abs/2511.16637
- [GMMNOT24] S. Gocht, C. McCreesh, M. Myreen, J. Nordstrom, A. Oertel, Y.K. Tan, "End-to-End Verification for Subgraph Solving", AAAI 2024, 38(8):8038-8047, doi 10.1609/aaai.v38i8.28642. https://ojs.aaai.org/index.php/AAAI/article/view/28642
- [KS24] M. Kirchweger, S. Szeider, "SAT Modulo Symmetries for Graph Generation and Enumeration", ACM TOCL 25(3) Art. 18, 2024, doi 10.1145/3670405. https://repositum.tuwien.at/bitstream/20.500.12708/208555/1/Kirchweger-2024-ACM%20Transactions%20on%20Computational%20Logic-vor.pdf
- [GB24] T. Gauthier, C.E. Brown, "A Formal Proof of R(4,5)=25", ITP 2024, LIPIcs 309, 16:1-16:18; arXiv:2404.01761. https://arxiv.org/abs/2404.01761
- [THM23] Y.K. Tan, M. Heule, M. Myreen, "Verified Propagation Redundancy and Compositional UNSAT Checking in CakeML", STTT 2023, doi 10.1007/s10009-022-00690-y (cake_lpr). https://research.chalmers.se/publication/534843
- [CAH24] C. Codel, J. Avigad, M. Heule, "Verified Substitution Redundancy Checking", FMCAD 2024, pp. 186-196 (only abstract + citations read).
- [ACH26] M. Anders, C. Codel, M. Heule, "Orbitopal Fixing in SAT", TACAS 2026; arXiv:2601.16855 (abstract only read).
- CaDiCaL NEWS.md (Debian source of cadical 2.1.3): https://sources.debian.org/src/cadical/2.1.3-3/NEWS.md

---

## 1. Duggan / Li / Bright / Ganesh: R(3,8)=28 and R(3,9)=36 via SAT+CAS (MathCheck) [DuLBG]

Note on names: the IJCAI 2025 paper is first-authored by Zhengyu Li; Duggan is second author. The earlier
AAAI 2024 student abstract "A SAT + Computer Algebra System Verification of the Ramsey Problem R(3,8)"
(https://ojs.aaai.org/index.php/AAAI/article/view/30437) and C. Duggan's Waterloo research paper are precursors.
A related, same-method paper: Li, Bright, Ganesh, "A SAT Solver + Computer Algebra Attack on the Minimum
Kochen-Specker Problem", IJCAI 2024 (https://ijcai.org/proceedings/2024/210).

(a) Reductions / encoding correctness
- Direct CNF: for every K_p one clause "some edge red", for every K_q one clause "some edge blue" [S, Sec. 4.1].
  They solve R(k,3) form (complement), which ran ~6x faster than R(3,k) [S, Sec. 5, 8.2-8.3].
- Degree bounds n - R(p,q-1) <= deg(v) <= R(p-1,q) - 1 (Graver-Yackel) as totalizer cardinality constraints [S, Sec. 4.3].
  R(8,3) on 28 vertices: degree 20..22. R(8,3;27;271): degree 19..22, exactly 271 edges [S, Sec. 8.2, 8.3].
- R(3,9): Lemma 1 (Graver-Yackel 1968, Sec. 3): a (3,9;36)-graph contains a (3,8;27;80)-graph, equivalently
  a (9,3;36)-graph contains an (8,3;27;271)-graph. Lemma is "proved mathematically", used without formalization [S, Sec. 7].
  They do NOT use Grinstead-Roberts' further structural lemmas [S, Sec. 7].
- Encoding correctness is NOT verified: "we cannot claim complete formal proofs since the SAT encodings have not
  been formally verified" [S, Sec. 1.1]; listed again as open item in Sec. 8.4 and Sec. 9.

(b) Case split
- Cube-and-conquer: cubing solver AlphaMapleSAT (MCTS lookahead), each split simplified by CaDiCaL+CAS
  (10,000 conflicts) so cubes see CAS blocking clauses [S, Sec. 6.1, 8.1].
- Stop criterion = number of eliminated edge variables: 120 for R(8,3), 100 for R(8,3;27;271); a cube whose
  proof exceeds 7 GiB is re-cubed (+40 eliminated variables) [S, Sec. 6.1, 8.2, 8.3].
- 7 GiB limit chosen so DRAT-trim can check it within 4 GiB memory [S, Sec. 6.1].

(c) Cube cover
- "Completeness was verified by recursively checking that for any literal x forming a cube phi AND x, all extensions
  of the complementary literal phi AND NOT x were covered by the set of generated cubes" [S, Sec. 8.4].
  This is a custom script; no tautology DRAT proof is reported. Our note: the checker of the cover is unverified code.

(d) Per-cube proof format + checker
- DRAT from CaDiCaL (via IPASIR-UP), checked with DRAT-trim "modified to support clauses specified to be trusted";
  CAS clauses are prefixed 't' in the DRAT file [S, Sec. 8.4]. No LRAT, no verified checker (cake_lpr etc.) used.

(e) Symmetry breaking justification
- Static: Codish et al. (2019) lex constraints on adjacency rows, A_{i,j} <=lex A_{j,i} for all i<j, O(n^3) aux
  vars/clauses, included in all instances [S, Sec. 4.2]. These clauses are part of the input CNF; they get no
  proof (they are covered only by "encoding not verified").
- Dynamic: orderly generation (Read / Faradzev): canonical = lex-least under COLUMN-wise order of above-diagonal
  entries; when an upper-left submatrix is fully assigned, CAS tests canonicity; if non-canonical, a blocking clause
  is learned plus a witness permutation [S, Sec. 5]. They need column-wise order because "parent of canonical is
  canonical" (Property 2); SMS's row-wise order lacks it [S, Sec. 3.1].
- Full canonicity check (not the default pseudo-canonical check) was enabled; CAS time = 7% (R(8,3)) / 38% (R(9,3)) [S, Sec. 8.1].
- Our note: the paper does not give an argument that the static Codish constraints and the column-wise
  lex-least canonical form choose a common representative. Soundness of using both at once needs that lemma.
  RESOLVED by cert (2026-10-24, notes/cert_design.md sec. 1.3): the lemma holds. MathCheck's static
  constraints (gen_instance/cubic.py: row_i <=lex row_j, columns ascending without i, j, for ALL i < j) are
  exactly the lex-leader constraints of the transpositions (i j) under lex-MIN of the COLUMN-wise (colex)
  edge vector, the same order as the CAS blocking clauses. Checked mechanically: cert/mc_cert.py derives all
  cubic clauses and all 1125 CAS clauses of a (3,7,23) run by VeriPB dominance under that one order
  (CakePB OK); brute force n <= 6: every colex-lex-min form satisfies all cubic constraints.

(f) Externally generated clauses
- Each CAS clause is checked by a Python script that applies the stored witness permutation and confirms that the
  blocked partial matrix maps to a lex-smaller matrix [S, Sec. 8.4]. So only "clause blocks a non-canonical
  intermediate matrix" is checked; the meta-argument (orderly generation is complete: every iso class keeps its
  canonical rep, which no such clause removes) is paper-level, not machine-checked.
- Remaining trusted items stated by authors: SAT encoding, and "the custom script used to validate clauses
  generated by the CAS" [S, Sec. 8.4].

(g) Outside computations trusted
- Graver-Yackel Lemma 1 (paper proof). Degree bounds (paper). Existence of a (3,9;35)-graph for the lower bound
  (known construction). Encoding generator, cover script, permutation-check script, modified DRAT-trim.

(h) Sizes / times [S, Sec. 8.2-8.4, Table 3]
- R(8,3) n=28: 41 cubes, all UNSAT; proofs 5.8 GiB total; cubing 1,360 s, simplification 1,217 s, solving 19,811 s,
  verification 22,328 s; 8 h wall on 24 CPUs (Xeon Gold 6226). Sequential: 66,504 s (Sec. 8.4) / 18.5 h (Table 2).
- R(8,3;27;271): 2,486 cubes; proofs 289 GiB; cubing 15,530 s, simplification 42,482 s, solving 697,575 s,
  verification 473,874 s; 26 h wall on 128 CPUs (EPYC 7713).
- Precursor KS problem (IJCAI 2024): certificate 40.3 TiB for order 23 (from search snippet of the IJCAI paper;
  AAAI abstract says 41.6 TiB) - UNVERIFIED in full text.

---

## 2. Keller's conjecture, dimension 7 [BHMN] and its Lean verification [GCAH26] (and [Clune23])

(a) Reductions / encoding correctness
- BHMN: Keller dim 7 false iff a 128-clique exists in G_{7,3}; they show none in G_{7,3}, G_{7,4}, G_{7,6}
  [S, Thm 1, Sec. 1, App. A]. Reduction = paper proof (Perron-style arguments) [S, Sec. 3, 5].
- Encoding sanity check: satisfiable for G_{8,2..6} using Mackey's clique as unit clauses [S, Sec. 7.2]. Encoding itself not verified.
- Clune (CPP 2023): Lean 3 formalization of the reduction to Keller graphs; SAT encoding and symmetry reasoning left open
  [S, GCAH26 Sec. 1].
- GCAH26 (ITP 2026): end-to-end Lean 4. New, more compact encoding of "Keller colorings", verified in Lean with the
  trestle library (VEncCNF = encoding paired with proof it encodes a spec) [S, Sec. 4, 4.1]. With better split they
  solve s = 2^(n-1) directly, so the s in {3,4,6} discretization results need no formalization [S, Sec. 4].

(b) Case split
- BHMN: fix c0, c1, c3 (19 coordinates, unit clauses); then 25 (s=3) or 28 (s>=4) canonical cases for last three
  coordinates of c19,c35,c67, times 861/1326/1378 classes for coordinates 3-4 => 21,525 / 37,128 / 38,584 cases;
  hardest case split into 33 more (+32) [S, Sec. 6.1-6.3]. Cactus plots list 21,557 / 37,160 / 38,616 subformulas.
- GCAH26: split guided by proofix (Battleman, Reeves, Heule, "Problem Partitioning via Proof Prefixes", SAT 2025):
  hardest matrix assignment vs the other 27, times all 1378 red-column cases; hardest cube split 16 ways
  [S, Sec. 6.1]. Table 1: n=7,s=64: 2,771 cubes.

(c) Cube cover
- BHMN: per s, a DNF of the cubes; "we mechanically check that the three DNFs are indeed tautologies" (tool not named)
  [S, Sec. 6.4].
- GCAH26: "we checked that the formula with the negated cubes is easy to refute" [S, Sec. 6.1].
  Whether this refutation is imported into Lean is UNVERIFIED (not stated).

(d) Per-cube proof format + checker
- BHMN: CaDiCaL DRAT -> DRAT-trim (optimize, emits LRAT) -> ACL2check (formally verified LRAT checker) [S, Sec. 7].
- GCAH26: CaDiCaL LRAT, checked by verified LRAT checker [34] = cake_lpr (Tan-Heule-Myreen) [S, Sec. 6];
  for n=2..5 "a proof-by-reflection tool gives a complete proof in Lean" [S, Sec. 6]. [Sz26, Sec. 3.1] says
  GCAH26 re-solved at elaboration time for 3<=d<=5. How the n=6,7 cube verdicts enter Lean (axiom vs reflection)
  is UNVERIFIED.

(e) Symmetry breaking justification
- BHMN: initial fixing of c0, c1, c3 by paper argument = "the only part of the symmetry breaking that is not checked
  mechanically" [S, Sec. 6, Fig. 4]. All further symmetry-breaking clauses added incrementally, each with a clausal
  (DRAT) proof of validity w.r.t. formula + earlier SB clauses, checked with drat-trim [S, Sec. 6]. Canonical
  representatives of assignment classes computed by canonical labeling (McKay-Piperno style) [S, Sec. 6.1].
- GCAH26: split in two. (i) Fixed colors of indices 0,1 proved in Lean (each symmetry is a Lean function on colorings,
  proved a symmetry by giving its inverse; uses Keller in dim n-1 by induction) [S, Sec. 5.2]. (ii) Rest written as
  substitution-redundancy (SR) clauses, found manually, generated by a Lean program; dsr-trim (unverified, C) adds
  hints (DSR -> LSR), then the verified LSR checker of [CAH24] (Lean) checks them [S, Sec. 5.3]. One symmetry (CIBF)
  is not expressible in SR and so is done in Lean [S, Sec. 5.3]. Five kinds of SR clauses for n=7 [S, Sec. 5.3].

(f) Externally generated clauses
- None in the sense of a propagator: all SB clauses are static and have DRAT (BHMN) or SR (GCAH26) proofs.

(g) Outside computations trusted
- BHMN: encoding generator, cube DNF tautology checker, initial SB argument, drat-trim (for SB clauses), DRAT-trim (as
  LRAT producer; not trusted since ACL2check re-checks).
- GCAH26: Lean kernel + trestle; cake_lpr verdicts; verified LSR checker; dsr-trim untrusted (produces hints).

(h) Sizes / times
- BHMN [S, Sec. 7.1, Table 3]: s=6 proofs 224 GB binary DRAT, 6.18e9 proof steps, of which 6.39e8 needed (~90% unused).
  CPU hours (solve / proof optimisation / certification): s=3: 43.27 / 22.46 / 4.98; s=4: 77.00 / 44.00 / 9.70;
  s=6: 81.85 / 34.84 / 14.53. Hardest cube ~1.2-2.7 CPU h. 20 nodes x 24 cores, Lonestar 5.
- GCAH26 [S, Table 1]: n=7,s=64: 5,657,894 clauses, 117,376 vars, 2,582 SR clauses, dsr-trim 3,991.6 s, lsr-check 370.5 s,
  2,771 cubes, solve 228.5 h, check 125.0 h. n=7,s=6: 383,142 cls, 385 SR, 2,771 cubes, 29.3 h solve, 19.6 h check.
  n=6: 104 cubes, 0.014 h solve. SR check for n=7 "just over an hour" [S, Sec. 6].
- Reduction part: ~3,000 lines Lean 4, ~1 month (Clune: ~15,000 lines Lean 3) [S, GCAH26 Sec. 2].

---

## 3. Schur number five, S(5)=160 [Schur5]

(a) Reductions / encoding correctness
- F^5_161 (plain encoding: positive, negative, optional clauses) generated by "a dozen lines of straightforward C code";
  "Only the encoding ... was not checked using a theorem prover" [S, Sec. "Correctness"].

(b) Case split
- Cube-and-conquer: modified march_cu (new decision heuristic, "down factor" cutoff) + Glucose 3.0 [S, "Certifying the Proof"].
- Partition P^5 of 10,330,615 cubes after balancing; cube sizes 13..62 literals [S, Sec. on partition].
- Each cube solved on R^5_160 (plain conquer also splits further: 65 billion cubes total) [S].
  For the 961 cubes where R^5_160 AND alpha is SAT, they redo with R^5_161.

(c) Cube cover
- "Tautology proof": cubes form a binary tree by construction; |P^5|-1 resolution steps merging siblings; P^5 (negated
  cubes) 1 GB, tautology proof 3 GB uncompressed DRAT [S, "Tautology Proof"]. Checked in ACL2 like the other parts.

(d) Per-cube proof format + checker
- Glucose DRAT -> DRAT-trim -> LRAT -> verified ACL2 LRAT checker (Heule et al. 2017) [S, "Correctness"].
- Composition is done by ACL2 + Unix tools: (1) ACL2 checks re-encoding proof, returns parsed F', R' and F' |=_w R';
  (2) for each cube clause C=not alpha, ACL2 checks R |= C from refutation of R AND alpha; (3) cat all C into P', ACL2
  refutes P'. Parsed formulas compared with diff [S, "Certifying the Proof"]. Our note: diff/cat are trusted glue.

(e) Symmetry breaking justification
- Color symmetry (5! permutations) broken by compact SB predicate (units v1^1, v2^2, then rules for colors 3,4,5)
  [S, "Symmetry Breaking"].
- "Re-encoding proof": DRAT proof that SAT(F) implies SAT(R) (satisfiability-preserving, not implication), using
  Heule-Hunt-Wetzler 2015 method: per SB clause add definitions "if lex order violated, swap two colors" with aux
  vars; 35 MB uncompressed DRAT, ~1M add + ~1M delete steps [S, "Re-encoding Proof"].

(f) Externally generated clauses
- None.

(g) Outside computations trusted
- C encoder; Unix diff/cat; ACL2 + verified checker. ("Verified Schur number five" as a separate paper: not found -
  UNVERIFIED that it exists; the AAAI paper already has the ACL2-verified chain.)

(h) Sizes / times [S, Abstract, "Implication Proof", "Certifying the Proof"]
- Solving: 27,600 CPU h partition + 95,600 CPU h conquer ~ 14 CPU years; < 3 days wall on 2,400 threads (Lonestar 5).
- Implication proof: 0.88 PB compressed DRAT; 2.18 PB compressed LRAT ("two petabytes"). Producing LRAT: ~20.5 CPU years;
  certifying: 15.6 CPU years; "a little more than 36 CPU years" spent on proof checking [S, Intro].
- 11 trillion conflict clauses in conquer phase.

---

## 4. Empty hexagon h(6)=30: [HS24] (TACAS 2024) and Lean [SNGCCH24] (ITP 2024), stream import [Sz26]

(a) Reductions / encoding correctness
- HS24: "trusted encoding" (O(n^6) clauses, no mechanical proof) + four optimisations to an O(n^4) domain-consistent
  encoding [S, Sec. 3, 4]. Re-encoding validation [S, Sec. 7.2]: (i) SB clauses have SR property w.r.t. the trusted
  encoding; no SR checker existed, so SR turned into DRAT add/delete steps - feasible only up to n<=10; (ii) entailment
  of new clauses (7) by trusted encoding checked only for n<=12 (~300 s), entailment tool github.com/marijnheule/entailment;
  (iii) other steps via Davis-Putnam resolution expressed in DRAT, and RAT on aux vars.
  So in HS24 the n=30 encoding chain is NOT fully checked.
- SNGCCH24: Lean 4 defines points in R^2, convex hull (mathlib), k-hole; proves that any n points in "canonical position"
  with no 6-hole give an assignment tau_S satisfying phi_n (only this direction is needed) [S, Sec. 1, 6].
  The CNF phi_n is produced by a verified Lean encoder (< 1 s) [S, Sec. 7]. ~4.7k LOC; 1,550 LOC for SB + encoding;
  ~300 person-hours [S, Sec. 8]. Found an error in the HS24 SB proof (x/y vs y/x) and a typo in the Lex condition [S, Sec. 8].

(b) Case split
- HS24: split on o_{a,a+1,a+2} sequences of length l; plus each alternating +,-,+ pattern doubles the cube; l=21 ->
  312,418 cubes; cubes in conflict with certain implied clauses are omitted [S, Sec. 5, 6.3, 7.3].

(c) Cube cover
- HS24: refute (negated cubes + SB predicate + some clauses of the formula); the used clauses are first checked to be
  implied via DRAT-trim (0.3 s); refutation by CaDiCaL in 12 s [S, Sec. 7.3].
- SNGCCH24: same method, 20 s to solve [S, Sec. 6 "Running the CNF"]. Our note: cover check is not in Lean in 2024.
- Sz26: cover is a separate certificate; Lean lemma cover_unsat composes leaf theorems + (negCubesCNF cubes).Unsat
  into a theorem about the base CNF [S, Sec. 6.1, Lemma 17].

(d) Per-cube proof format + checker
- HS24: CaDiCaL 1.9.3 emits LRAT directly; piped to cake_lpr concurrently (first use of this) - no proof file stored
  [S, Sec. 6, 7.1].
- SNGCCH24: CaDiCaL 1.9.5 LRAT, cake_lpr on-the-fly; unsatisfiability of phi_30 is "asserted as an axiom in Lean";
  "we trust that the CNF formula produced by the verified Lean encoder is the same one whose unsatisfiability was
  checked by cake_lpr" [S, Sec. 7].
- Sz26: lrat-catcher streams LRAT into Lean 4's core verified LRAT checker (resumable), giving theorems with only
  standard axioms + native-evaluation axioms; re-solved hexagon, imported 174 TB across 312,418 cubes in 4,882 groups,
  no file written [S, Sec. 7.2]. Caveat by author: earlier tool version shared one feed constant, so the composed
  theorem is not claimed [S, Sec. 7.2]. Import cost ~15x CPU of lrat_isa [S, Sec. 1, 7.1].

(e) Symmetry breaking justification
- HS24: p1 extremal, others CCW around p1, plus x-sorted (Lemma 1, App. A); reflection symmetry partially broken by lex
  predicate (20) on o_{a,a+1,a+2}; choice-of-first-point symmetry left unbroken [S, Sec. 3, 4.4].
- SNGCCH24: geometric Lean theorem symmetry_breaking: any point list in general position is sigma-equivalent to one in
  canonical position (x-order, CCW-order, Lex-order) [S, Sec. 5]. So SB is justified semantically in Lean, not by
  clausal redundancy. SB is also needed for encoding correctness (clauses assume x-sorted points) [S, Sec. 5].

(f) Externally generated clauses
- None.

(g) Outside computations trusted
- SNGCCH24: cake_lpr verdict -> Lean axiom (hand-transferred); cover check by CaDiCaL (unverified); job scripts.
  "the trust story at this connection point has room for improvement" [S, Sec. 8].

(h) Sizes / times
- HS24: ~17,300 CPU h (< 2 CPU years) including LRAT production and checking; 1000 m6i.xlarge AWS; average cube < 200 s,
  all < 1 h; LRAT total 180 TB uncompressed; DRAT estimate 78 TB (LRAT ~2.3x DRAT); cake_lpr kept up with solver on
  another core [S, Sec. 6.3]. Trusted encoding + off-the-shelf split estimated ~1000 CPU years [S, Sec. 3].
- SNGCCH24: 25,876.5 CPU h (~3 CPU years) on Bridges-2 [S, Sec. 6].
- Sz26: 174 TB LRAT imported [S, Abstract, Sec. 7.2].

---

## 5. VeriPB line: certified symmetry/dominance breaking, CakePB, SMS-type clauses

5.1 [BGMN23] Certified Dominance and Symmetry Breaking (AAAI 2022 / JAIR 2023)
(a) Proof system: cutting planes over pseudo-Boolean constraints + redundance-based strengthening + new
  dominance-based strengthening rule, relative to a preorder O_<= given as PB formula, proved to be a preorder in a
  proof preamble; order change rule [S, Sec. 3.3-3.8].
(e) Lex-leader constraints for any symmetry group subset are derivable by dominance rule; any combination is sound
  because all clauses refer to the same order [S, Sec. 1, 4]. The lex order is encoded with big-integer coefficients
  (2^(n-i)) [S, Sec. 3.7, 4]; this is the scaling bottleneck.
(h) BreakID with proof logging + Kissat: 1,089 SAT-competition instances with symmetry; overhead negligible for most
  (99% at most 32% slower); SB proofs verified for 1,058/1,089 (2 timeout, 29 out of memory); full solve verified for
  671 of 721 solved [S, Sec. 4]. Also applied to max clique (dynamic vertex dominance) and CP [S, Sec. 5, 6].
(f) Dynamic symmetry breaking during search: not covered; max-clique dominance is the closest "dynamic" case.

5.2 [A+26] Faster certified SB with auxiliary-variable orders (AAAI 2026)
- Orders encoded with auxiliary variables instead of big integers -> orders-of-magnitude speedups in proof logging
  and checking; satsuma emits VeriPB proofs; checked by VeriPB and formally verified CakePB (changes verified in the
  CakePB codebase) [S, Abstract, Sec. on CakePB].
- Static SB only; "investigate proof logging for conditional and dynamic symmetry breaking during search" = future work
  [S, Conclusion].

5.3 [GMMNOT24] CakePB, End-to-end verification for subgraph solving (AAAI 2024)
- Verified encoder frontends (subgraph isomorphism, max clique, max common induced subgraph) in CakeML/HOL4 + verified
  PB normalizer + CakePB kernel checker; VeriPB "elaborator" (untrusted) converts augmented proofs to kernel format
  [S, Sections on CakePB, encoders, elaboration]. Trusted base: HOL4 kernel, CakeML binary extraction [S, trust section].
  Kernel supports dominance-based strengthening [S].

5.4 Certifying SAT Modulo Symmetries (SMS) clauses
- No paper found that certifies SMS lex-minimality clauses inside VeriPB (searched; UNVERIFIED that one exists).
- [KS24, Sec. 8]: SMS proof = two parts: (1) store nc-certificate (permutation pi) for each SB clause; check in
  polynomial time that the blocked partial graph has a (G,pi)-indicator pair; (2) add all SB clauses to the original
  formula and produce a DRAT proof with a second solver, checked by a DRAT checker. Completeness of an enumerated list:
  add blocking clauses for the found graphs, expect UNSAT. Canonicity of each output graph G: CNF M_G unsatisfiable iff
  G canonical, so DRAT also certifies minimality [S, Sec. 8].
  Used for R(3,5,n) and R(4,4,n) enumeration [S, Sec. 8.1].
- [DuLBG Sec. 3.1]: "We opted for SAT+CAS due to the availability of its verification capability, which is not
  currently provided in the SMS repository".
- Related: SR proof system [CAH24] (Lean-verified checker; per DuLBG, a 38-clause SR proof of R(4,4)<=18, SR proofs on
  average 99.6% smaller than RAT); orbitopal fixing with SR certificates [ACH26]; PBLean (Szeider, arXiv:2602.08692)
  imports VeriPB certificates into Lean 4 (from search snippet; UNVERIFIED in full text).

---

## 6. R(4,5)=25 in HOL4 [GB24]

(a) Reductions / encoding correctness
- All high-level arguments in HOL4: neighbourhood/antineighbourhood lemmas; degree parity argument extended to remove
  all odd degrees: some vertex has degree d in {8,10,12} [S, Sec. 3]. Gluing CNFs are generated and stated inside HOL4,
  so encoding correctness is by construction in the prover [S, Sec. 5].
(b) Case split
- Per d: all R(3,5,d)-graphs x all R(4,4,24-d)-graphs, grouped into "generalizations" (graphs with gray = unassigned
  edges), exact covers; d=8: 179 x 313 gens (vs 130,816 x 1,449,166 graphs); d=10: 12 x 2 ... [S, Table 1, Table 3].
(c) Cube cover (here: graph-list completeness)
- Proved in HOL4 by finite induction on k: every extension by one vertex of a generalization in R*(3,5,k) is
  isomorphic to a member of R*(3,5,k+1); custom HOL4 prover branches on gray/new edges; leaves closed by instantiating
  with a nauty-supplied permutation (nauty is an untrusted oracle; its output is checked) [S, Sec. 4.2].
(d) Per-cube proof format + checker
- Each gluing problem solved by MiniSat through HOL4's MiniSat interface; proof replayed through the HOL4 kernel
  ("limiting the uncertainty to the small HOL4 kernel") [S, Abstract, Sec. 1, 8]. MiniSat proof files up to 2 GB
  each [S, Sec. 7]. Replay mechanism details (resolution-proof reconstruction) UNVERIFIED in this paper's text.
(e) Symmetry breaking justification
- Isomorphism reduction = generalization covers + nauty witnesses checked in HOL4; no clausal SB [S, Sec. 4].
(f) Externally generated clauses: none (nauty permutations are witnesses, checked).
(g) Outside computations trusted: only HOL4 kernel (and MiniSat output is re-checked) [S, Abstract].
(h) Sizes / times: naive approach est. > 16,000 CPU days; with generalizations < 950 CPU days est. [S, Sec. 4];
  final gluing < 9 days wall on 4 machines x 40 cores (512 GB-1 TB RAM; memory was the limit) [S, Sec. 7];
  authors compare: "approximately a petabyte of DRAT proof files versus 200 terabytes" (Pythagorean triples) [S, Sec. 8].
  DuLBG Sec. 3.1 summarises it as "over 2.5 years of CPU time" (secondary).

---

## 7. Clauses added during search by an external propagator (CAS / SMS / IPASIR-UP / LCG)

Observed patterns:
1. Trusted-tag + side check (MathCheck: Lam's problem, Kochen-Specker, R(3,8), R(3,9)). External clause written to DRAT
   with a 't' prefix; modified DRAT-trim accepts it without check; a separate script re-checks each one from a stored
   witness permutation [DuLBG Sec. 8.4; KS IJCAI 2024 per search snippet]. Weakness: modified (unverified) checker;
   global soundness of "all blocked assignments non-canonical => satisfiability preserved" is a paper argument.
2. Collect, verify, re-solve (SMS) [KS24 Sec. 8]: verify each clause by its nc-certificate, then treat the clause set as
   extra input and get an ordinary DRAT proof from a second solver. Same global meta-argument needed: every clause is
   falsified only by non-lex-minimal (partial) graphs under ONE fixed order, so the lex-minimal representative of every
   iso class satisfies all of them.
3. Express as redundancy in the proof system: DRAT re-encoding with aux swap variables [Schur5], SR clauses with a
   substitution witness [GCAH26, HS24 via SR->DRAT, ACH26], VeriPB dominance rule w.r.t. a declared lex order
   [BGMN23, A+26]. This makes the meta-argument machine-checked, but published tools cover static SB only; dynamic
   (search-time) SB proof logging is open [A+26 Conclusion].
4. Semantic proof in an ITP: [SNGCCH24] proves SB as a geometric theorem; [GCAH26] proves part of SB in Lean.
- Solver support: CaDiCaL 1.7.1 "Added support for LRAT + external propagator in combination"; 2.1.0 "Added support to
  generate incremental proofs (LIDRUP) while using IPASIR-UP" [CaDiCaL NEWS.md]. How external clauses are tagged in the
  LRAT/LIDRUP stream (as input clauses?) is UNVERIFIED from primary docs; our note: a checker must then receive the
  external clauses as part of the formula, so their validity must be shown separately (pattern 1/2/3).
- CP lazy clause generation with VeriPB: Gocht, McCreesh, Nordstrom, "An Auditable Constraint Programming Solver",
  CP 2022 (doi 10.4230/LIPIcs.CP.2022.25): each propagator justifies its inferences by cutting planes or RUP in the
  VeriPB log (from abstract/snippet; details UNVERIFIED).

---

## 8. Sizes / check times summary (numbers from sections above)

| Project | Proof format | Size | Solve | Check | Checker |
|---|---|---|---|---|---|
| Schur 5 (2018) | DRAT -> LRAT | 0.88 PB DRAT (compr.), 2.18 PB LRAT (compr.); SB re-encoding 35 MB; tautology 3 GB | ~14 CPU y | LRAT gen 20.5 CPU y + certify 15.6 CPU y | ACL2 LRAT checker |
| Pythagorean triples (2016, background) | DRAT | ~200 TB (cited in Schur5, GB24) | - | - | DRAT-trim; later Coq |
| Keller BHMN (2020) | DRAT -> LRAT | s=6: 224 GB binary DRAT | 43-82 CPU h per s | 5-15 CPU h certify per s (+22-44 h DRAT-trim) | ACL2check; SB via drat-trim |
| Keller GCAH26 (Lean 4) | LRAT + DSR/LSR | not given | s=64: 228.5 h | 125.0 h; SR 1.1 h | cake_lpr; Lean LSR checker |
| Empty hexagon HS24 | LRAT (streamed) | 180 TB LRAT (~78 TB DRAT est.) | 17,300 CPU h incl. check | concurrent | cake_lpr |
| Empty hexagon SNGCCH24 | LRAT (streamed) | not stored | 25,876.5 CPU h | concurrent | cake_lpr; verdict = Lean axiom |
| Empty hexagon Sz26 | LRAT -> Lean | 174 TB imported | re-solved | ~15x lrat_isa CPU | Lean core LRAT checker (resumable) |
| R(4,5) GB24 | MiniSat proofs in HOL4 | up to 2 GB per call | < 950 CPU d est.; < 9 d wall | inside HOL4 | HOL4 kernel |
| R(3,8) DuLBG | DRAT + 't' | 5.8 GiB | 19,811 s | 22,328 s | modified DRAT-trim + Python |
| R(3,9) DuLBG | DRAT + 't' | 289 GiB | 697,575 s | 473,874 s | modified DRAT-trim + Python |

---

## 9. Summary table: how each chain link was handled

| Link | R(3,8)/(3,9) DuLBG | Keller BHMN | Keller GCAH26 | Schur 5 | Hexagon HS24 | Hexagon Lean | R(4,5) GB24 | SMS KS24 | VeriPB BGMN23/A+26 |
|---|---|---|---|---|---|---|---|---|---|
| Math reduction | paper (Graver-Yackel) | paper; Lean3 later (Clune) | Lean 4 | trivial | paper | Lean 4 + mathlib | HOL4 | n/a | n/a |
| Encoding | unverified Python | unverified; SAT sanity check n=8 | Lean (trestle) | 12 lines C, unverified | trusted enc.; optimised enc. partly checked (n<=12) | verified Lean encoder | built in HOL4 | unverified | CakePB verified encoders (graph problems) |
| Case split | AlphaMapleSAT, 41 / 2,486 cubes | manual canonical classes, ~21k-39k cubes | proofix, 2,771 cubes | march_cu, 10.3M cubes | structured, 312,418 cubes | same | degree + generalization covers | n/a | n/a |
| Cube cover | custom recursive script | "mechanically checked" DNF tautology | refute negated cubes (Lean import UNVERIFIED) | DRAT tautology proof (ACL2) | CaDiCaL refutation + DRAT-trim | CaDiCaL refutation | HOL4 induction + nauty witnesses | n/a | n/a |
| Per-cube checker | modified DRAT-trim | ACL2check (LRAT) | cake_lpr / Lean reflection | ACL2 LRAT | cake_lpr streamed | cake_lpr -> axiom | HOL4 kernel | DRAT checker | VeriPB / CakePB |
| Static SB | Codish lex, unjustified | units by paper; rest DRAT-checked | Lean + SR (verified LSR) | DRAT re-encoding proof | SR->DRAT for n<=10 only | Lean theorem | cover + iso witnesses | n/a | dominance rule |
| Dynamic SB clauses | 't' + witness script | none | none | none | none | none | none | nc-certificate check + re-solve DRAT | open problem |
| Trusted extra | scripts, Lemma 1 | DNF checker, initial SB, encoder | Lean kernel, cake_lpr | encoder, diff/cat | trusted encoding | cake_lpr->axiom glue | HOL4 kernel | MinCheck completeness (for "no iso copies") | CakeML/HOL4 |

---

## 10. Lessons for R(3,10) (n=40, alpha<=9, triangle-free)

1. The weakest links in all non-ITP projects are the encoder and the "glue" (cover check, scripts, diff/cat).
   At minimum, generate the CNF from a small, separately reviewed generator and re-derive it independently (two
   implementations, diff). Best: a Lean/trestle-style verified encoder (GCAH26, SNGCCH24) - the triangle-free / no-I10
   encoding is simple enough for this.
2. State and prove one meta-lemma for ALL symmetry breaking: a single fixed total order on labelled graphs (e.g.
   column-wise above-diagonal lex-least, as in MathCheck) and a proof that every static SB clause AND every dynamic
   blocking clause is satisfied by the order-minimal representative. DuLBG mixes row-wise Codish constraints with a
   column-wise canonical form and gives no compatibility argument (cert later showed the two ARE compatible:
   both are lex-min colex lex-leaders; see sec. 1 note).
3. For dynamic (orderly / SMS) blocking clauses, store a witness permutation per clause and check it with a small
   independent checker (DuLBG, KS24). Prefer the KS24 route (verify clauses, then re-solve with them as input and an
   ordinary LRAT proof) or a fully clausal route (SR with substitution witness, cf. GCAH26/ACH26) over a modified
   DRAT-trim with 't' clauses. Proof logging of dynamic SB in VeriPB/SR is still open (A+26) - a possible contribution.
4. Use LRAT streamed into cake_lpr (HS24): no storage, checker keeps up with solver, verified down to machine code.
   180 TB LRAT for 17,300 CPU h is the reference scale. If a Lean theorem is wanted, lrat-catcher (Sz26) can import
   streamed LRAT with a cover lemma; budget ~15x the checking CPU of lrat_isa.
5. Make the cube cover a checked object: binary-tree resolution proof (Schur5) or refutation of negated cubes + SB
   predicate with LRAT (HS24), checked by the same verified checker, or cake_lpr's compositional format (THM23),
   not a custom script (DuLBG).
6. Any domain theory used to cut the problem (degree bounds, edge-count bounds, (3,9)-graph counts from the
   Radziszowski survey, Goedgebeur-Radziszowski enumerations) is an outside computation. Either reprove it inside the
   chain (with its own certificates) or list it explicitly as trusted. DuLBG deliberately used only Graver-Yackel's
   paper lemma plus degree bounds.
7. Cap per-cube proof size (DuLBG used 7 GiB for DRAT-trim with 4 GiB RAM); streaming LRAT removes this limit.
8. Keep a SAT sanity check of the encoding: show the n=39 instance (with the same SB and cardinality constraints) is
   SAT using a known (3,10;39)-graph, as BHMN did with Mackey's clique for n=8. This tests the SB+encoding chain
   for over-pruning.
