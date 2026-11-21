# Lane F: constructions (search for a (3,10,40)-graph)

Start share: 12 cores.

One verified (3,10,40)-graph proves R(3,10) = 41. Put every candidate as graph6 in
`ralph/found/F_<tag>.g6`; check it first with `python3 -I .hmz/flows/r310_ralph/gate.py . check FILE`.
Do not report "found" unless that check says ok; the flow's own scan is the only verdict.

Background (read first, do not repeat): `notes/anneal.md` (simulated annealing, tabu, vertex rewiring,
symmetric mode; calibration table), `notes/known39.md` (one-vertex extensions of 18.4M graphs of the
rewire closure of Exoo's (3,10,39)-graph: 0 extend; the GR/Angeltveit set of ~43M (3,10,39)-graphs is
not public), `notes/algebra.md` (orbit/algebraic families), sec5.tex (Cayley graphs excluded; prime
orders >= 7 excluded; order 5 with f = 10, 15 and order 3 with f >= 13 excluded).
Data: Exoo's graph: cs.indstate.edu/ge/RAMSEY/r3.10.39 (0/1 matrix of the COMPLEMENT).

## Do
1. BOOTSTRAP: rebuild `anneal/ls.cpp`; calibrate (time to a (3,9,35)-graph and to a (3,10,39)-graph from
   random starts, as in notes/anneal.md). A searcher that cannot find a 39-graph gets no cores.
2. Search families that are NOT excluded and that earlier lanes did not cover: graphs with an
   automorphism of order 2 (all f open), order 3 with f in {1,4,7,10}, order 5 with f = 0, order 4,
   and 2-, 4-, 5-, 8-block (non-Cayley) circulant structures; one-vertex extensions of new 39-graphs
   (from your own searches, outside Exoo's rewire closure). Lane E proves cases empty; you look for
   models: share results on the BOARD (a family lane E closes needs no more search).
3. Track a measure of nearness (min number of independent 10-sets at n = 40 per family) round by
   round. A family whose best value does not improve in 3 rounds loses its cores.
