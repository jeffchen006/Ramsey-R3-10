# duo: research with Codex on the hard core (agent duo, CPUs 68-71)

Started 2026-10-25 ~07:45. Codex binary: ONLY runs/pilot/codex/bin/codex (<home> is <auth> -> SIGBUS). Codex session <id> (gpt-6.1-sol, xhigh, read-only).
Files: duo/ (scripts, Codex prompts/answers), this log.

## Test bed (d-regular triangle-free graphs with alpha <= d; analogues of the 9-regular case)
duo/regstat.py. Known: C5 (d=2,n=5), Wagner (3,8), C13(1,5) (4,13), Clebsch (5,16),
10 six-regular graphs in R(3,7,22) (McKay r37_22.g6), C35(1,7,11,16) (8,35; r39_35.g6).
A lemma for d = 9, n = 40 must be consistent with these where it has an analogue.

## Log
### Round 1 (lead's prompt runs/lead/codex_prompt_1.txt -> runs/lead/codex_ideas_1.md), my verdicts
1. J9 seed: every H_v (e(G) >= 163) has an induced 7K1+K2. CORRECT (GR e3j13 Table 2: e(3,J9,30) = 117, R(3,J9) = 31).
   Only symmetry breaking; seeded gluing classes are 1-4% of R(3,9;30,99) (gluing MCMC). Optional SAT cut. Not a reduction.
2. Matching lemma: for non-adjacent u,v, nu(A,B) >= d(u)+d(v)-c-9 (Konig); 9-regular: A-B has a perfect matching,
   g >= 9-c, Lemma P bounds become g >= (8,7,6,5,4,3,4). CORRECT. No SAT gain: a Hall violation is a fully decided
   independent 10-set, which the lazy IS propagator already catches. LP rows only.
3. Exact SDP with codegree types: not tested; weak prior (plain 10-vertex flags give only R(3,10) <= 54).
Own tests: duo/multicover.py: 40/40 MCMC samples of R(3,9;30,99) admit the exact multicover by 9 independent
8-sets (so it is no filter). duo/pairlp.py: codegree-typed pair LP feasible, C4 in [540,1050], each n_c can be 0.
Shearer 1991: alpha >= 7.85 only. Analogue codegrees: C35(1,7,11,16) {1:140,2:210,4:105} (every x in N(v) has
exactly one private vertex); 6-regular (3,7,22): c* in {3,4}.
Round 2 sent (duo/codex_r2.txt): ask for a global forcing lemma into a small class, and Angeltveit's regular
pair-gluing trick (arXiv 2401.00392 Sec 5) adapted to the 9-regular case.

### Round 2 answer (duo/codex_r2.md)
Idea: fractional regular-gluing LP on H in R(3,9;30,99): z_S on independent 8-sets, sum=9, degree rows,
rows sum_{S cap T=0} z_S <= 9-|T| for independent T. Target: LP infeasible for all H (would close case R).
Own test duo/adv_c35.py (H = C35 - indep 5-set - edge, 1209 H): 8-rows alone pass 707; 7+8 rows still give 9.0 for 110.
So the 7-set level is NOT universal. With degree equalities: levels 6/5/4 kill 56/43/11 of the 110 (runs/duo/adv5.log);
no survivor at level 4. LP = minutes per H, so no filter; only a uniform certificate would help. Sent to cases+critic 13:20. critic Review 26: Claim A CONFIRMED (cite L6 for distinct S_i); exact Farkas certs needed before any claim.
Round 3 (duo/codex_r3.txt -> duo/codex_r3.md, job duo/codex_r3): uniform type-based dual; harder adversarial family.
### Round 3 answer (duo/codex_r3.md) and tests
- Coarse type tau=(t, degs, #8-extensions): shared weights CANNOT exclude H=C35-{0,2,4,6,12}-{19,20} (Codex exact rational point).
- 39-vertex rooted family (duo/adv39.py, runs/duo/adv39.log): 159 H, 156 die at level 8, 3 at level 7/6. Weak adversary.
- Shared dual with remainder-type tau (duo/shared.py, job duo/shared11): STOPPED 19:41 after 6 h in HiGHS (11 H, ~15k WL types each).
  Reason: WL-remainder types are not finitely checkable, so even a feasible result gives no uniform proof; coarse types fail (r3). Route closed.
### Round 4 (duo/codex_r4.txt -> duo/codex_r4.md, job duo/codex_r4): Angeltveit-McKay R(5,5) excess + pair overlay, from desktop lead.
Round 4 answer: conditional lemma m>=13 degree-9 vertices with e(H_v)<=98 in non-regular sel cases -> adjacent overlay |X|=22;
catalogue ~2e17, no big cut; 9-regular: no fixed-sum excess. Sent to cases, critic, tlead 14:05. critic Review 28: CONFIRMED (scope: MTF degrees 6..9, e>=167, non-regular, conditional on sel exclusions). cases: true but no use for the split.
### Round 5 (duo/codex_r5.txt -> duo/codex_r5.md, job duo/codex_r5, started 19:41)
Benchmark idea: a case-R method must first classify 8-regular (3,9,35)-graphs (answer C35, [GR] Thm 3) in <= 1 CPU-day;
SMS does not even find C35 in 59 min. Asked Codex for 2 methods that pass this test and scale to k=10, plus a 6 h test.
Round 5 answer (duo/codex_r5.md): EDGE-KERNEL method. For an edge uv: A=N(u)-v, B=N(v)-u, F=G[A,B]. Exact (I checked the proofs):
Delta(F)<=M-1 (M = max codegree), nu(F)>=d-2 (Konig), codeg-1 pairs inside each N(w) form a matching (else N(a)-w+{b,c} is an
independent (d+1)-set) so t1<=n*floor(d/2); convexity + sum_edges e(F)=4C4 give an edge with e(F)<=floor(6+1.5M) (n=35,d=8),
floor((64+20M)/9) (n=40,d=9). Split by M; per kernel SMS completion (kernel labels fixed singletons, rest one SMS cell).
Kernel counts reproduced: 3305 (35, M<=4), 238 (40, M<=3). (35, M=5): X = 22-vertex (3,7,22) with 60/61 edges (7 graphs); M>=6 impossible.
Control (22,6,k=7,M=5, 474 kernels): 93 CPU-s, recovers exactly the 10 six-regular (3,7,22)-graphs (labelg compare). PASS.
Jobs: duo/k35 (CPUs 68-69), duo/k40 (70-71, case R with codeg<=3), queued duo/x35 after k35. Script duo/kernel_run.py, duo/kernel_x.py.
Pass threshold (Codex): 35 classification <= 12 CPU-h and gives only C35; 40/M<=3 <= 6 CPU-h.
Round 5 TEST RESULT (23:05): FAIL. SMS completion per kernel is bimodal (1-75 s or > 1 h): (35,8) 6 UNSAT + 4 TIMEOUT(1 h) of first 10;
case R M<=3: 11 UNSAT + 4 TIMEOUT of first 15 (timeouts at e(F) = 8..10, many degree-2 vertices). Needed mean ~20 s. k35/k40 stopped.
x35 (codeg-5 branch, X fixed, 7 cases, CPUs 68-70) runs to learn if a fixed 22-vertex X makes completion fast.
Round 6 (duo/codex_r6.txt, scout Test A: max-q(v) split + Q/kernel compatibility) not run: (binary moved; restarted 23:2x with runs/pilot/codex/bin/codex).
x35 result (23:04): all 7 codeg-5 X cases UNSAT, 10-18 s each (so no 8-regular (3,9,35)-graph with codegree 5; consistent with C35 max codeg 4).
Fixed large X completes fast at k=9; at k=10 the same idea is Lemma R7 / cases/r7_glue.py and sms R(7), which stays hard. Nothing new for the team.
### Round 6 (duo/codex_r6.md; scout Test A: max-q split). Checked by hand:
q(v)=54+h1+h4+3h5+6h6+10h7 (h_c = #non-nbrs with codeg c); h7<=1, h6<=2, h7>0 => h6=0 (R(3,7)=23, R(3,6)=18); h1<=9.
769 histogram candidates; Q=max q in [54,87]; C4 <= 860 (was 1050). sum_{w in N(u)} e(F_uw) = 2q(u).
Q=54 cube: all codeg in {2,3}, 49 kernels (genbg -d1 -D2 8 8 8:12) - still SAT completion, no kill.
h6(0)=2 (two codeg-6 partners a,b): X = G-N[{0,a,b}] is one of 191 R(3,7;22) graphs (forced seed). C35: q=48 const.
Probe duo/h6probe (duo/kernel_h6.py, CPUs 68-71): 6 X graphs x s=3..6 (|N(a)&N(b)&N(0)|), 1800 s limit:
tests whether completion from a fixed 22-vertex X is fast at n=40 (it was 10-18 s at n=35, x35).
### 24 h kernel experiment (desktop lead, runs/lead/codex_strategy_3.md Sec 4), started 2026-10-26 ~00:20
Fixes: duo/kernel_run2.py (smsg -a; resume only finished kernels; optional Aut(kernel) lex-leader clauses in the SMS order
lex-min row-wise; cap 300 automorphisms, first 400 moved positions; both truncations stay valid). Control (22,6): both versions give exactly the 10 graphs (104 s / 102 s).
Catalogues (duo/gencat.sh, genbg + duo/kfilt.c, nu>=7; runs/duo/kern2/cat): M4 (-D3, e<=16) 96,135; M5 (-D4, e<=18) 2,852,820; M6 (-D5, e<=20) ~26M+.
Generation takes seconds (M4, M5) and minutes (M6). Samples: 32 uniform per M (duo/ksample.py, seeds 4004/5005/6006); 1 h limit; aut 0 and 1.
Jobs (nohup; jobctl refuses lent CPUs): M4 136-139/140-143, M5 40-43/44-47, M6 36-39/68-71; then chain_c35.sh on 136-139 (35-vertex, aut, 6 h).
h6probe (round 6 seed) stopped for this: 6 UNSAT (0.7-277 s), 3 TIMEOUT (30 min) of 9 -> heavy tail too.
24 h experiment RESULT (ended 2026-10-26 12:05): no completion found. Solved in 1 h (no Aut / Aut) of 32: M4 2/3, M5 0/0, M6 1/1.
Lower bounds (timeout = 3600 s): M4 >= 3.2e8, M5 >= 1.0e10, M6 >= 9.2e10 CPU-s. Aut clauses: no gain.
35-vertex control (aut, -a): 11 UNSAT + 15 TIMEOUT of first 26 kernels, stopped. Verdict: kernel route not feasible.
Written into paper/draft.md Sec 8.4 + 8.5 row. Mistake: an M6 wait loop matched itself in pgrep; M6 started 8 h late.
