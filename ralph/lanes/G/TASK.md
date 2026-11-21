# Lane G: near-regular degree distributions N(e)

Start share: 4 cores.

Background: `paper/latex/sec3.tex` (Sec. "Degree distributions", the class LP with exact Farkas
certificates, t9 per distribution, "sel" reduction, excess lemma), `notes/cases.md`,
`notes/cases_local.md`, `notes/edge_tables.md`, code `cases/` (degseq.py, LPs, certificates).
State: 545 MTF distributions; 20 closed by gluing; 524 open with 162 <= e <= 179, plus case R.
A t9 <= 88 gluing (lane B) closes 15 more.

## Do
1. BOOTSTRAP: rerun `cases/degseq.py` and reproduce the 545 / t9 multiplicities of sec3.tex exactly
   (exact rational certificates; scipy/pysat from opt/venv or your own venv in scratch/G).
2. Add valid rows that the class LP does not have yet, each with a proof: e.g. exact values of
   e(3,8,n) and e(3,9,n) for the pair sets X (Lemma P for all G, not only case R), Lemma N, codegree
   caps per degree pair, counts of independent 8-sets, the MTF private-neighbour bound per class.
   Each new row: a hand proof in `ralph/lanes/G/rows/NAME.md` and a test that it holds on known
   extremal graphs (C35, Exoo 39 - all must satisfy the n-analogue).
3. Report how many of the 524 distributions each new row closes (exact Farkas certificate each).
   The aim: reduce the open list so far that the rest is case R plus a few cubes that lane B can glue.
