# Lane A: toolchain and certified SAT (the 99 open R(7) cubes)

Start share: 14 cores (see ralph/ALLOC.md).

## First (BOOTSTRAP): the shared toolchain in `opt/`
Other lanes wait for this; post each tool on ralph/BOARD.md as soon as it works.
Order (most needed first): nauty 2.9.3 (geng, shortg, labelg, genbg; lib); CaDiCaL 3.0.1 + kissat 4.0.4;
SAT Modulo Symmetries at commit 63958bd with OUR patches `sms/sms-patches/upstream-63958bd.diff`
(lazy independent-set propagator `--forbid-independent-set`, `--proof-log`, cube options) and its pinned
CaDiCaL fork; drat-trim + lrat-check; cake_lpr (a36874a); VeriPB 3.0.2; a Python venv `opt/venv`
(python-sat, pynauty, networkx, numpy, scipy). Versions and sources: `tools/README.md` (paths T/... there
are the old machine's; build here under `opt/`). Write `opt/env.sh` and `opt/README.md` (what, version,
how tested). Test each tool as `tools/README.md` says (e.g. php6_5 proofs, nauty link test, SMS
reproduces 275,086 (3,6,13)-graphs, and `(3,6,18)` UNSAT with a cake_lpr-checked proof).

## Then: certified SAT
1. Rebuild the PRc7 base CNF and the 464 cubes (`sms/gen_ramsey.py`, `sms/rc7_*.sh`, `sec7.tex`). Check
   on 5 known-UNSAT cubes that the times match the old ones (median 5.2 s).
2. The 99 open cubes resisted 6 h each and one more lookahead split. Try a different idea before more
   cores: e.g. add the implied rows of Lemma P/F (f >= 4 for the c* = 7 pair is fixed; also every other
   non-adjacent pair with codegree 7 must have the same structure), split on the 4 graphs of
   R(3,8;27,85) for X (Lemma R7 says X is one of them: 4 cubes with X FIXED could be much easier),
   or on the codegree profile of vertex 0. Measure on 3 open cubes first.
3. Every UNSAT you report as cert must pass the full chain of sec7.tex (LRAT -> cake_lpr; lazy IS clauses
   -> cert/check_cnf.py; SB clauses -> sbcheck or cert/check_sb.py). Without the chain, label it enum.

R(7) closed with a certificate gives the theorem "in case R every codegree is <= 6". That is a real step.
