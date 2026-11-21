# Lane E: automorphisms (the open (p, f) cases)

Start share: 10 cores.

Background: `paper/latex/sec5.tex`, `notes/symsat.md`, code `symsat/` (orbit SAT with lazy alpha
clauses, `verify_sc.py` certificate checker, subcase split by a = |A_O|). Any automorphism has an
element of prime order, so closing every (p, f) proves that G is rigid (|Aut G| = 1): a useful
partial result, and every SAT model found on the way is a (3,10,40)-graph (put it in ralph/found/).
Note the Scope rule (sec3.tex): with an automorphism assumed, use all graphs, not only MTF graphs.

## Open cases
- (5,5): UNSAT by enumeration, DRAT log lost. Re-run with proof and certify: cheap, do it first.
- (5,0): TIMEOUT 1 h and 24 h. (3, f) for f in {1, 4, 7, 10}: subcases a = 1..6, several TIMEOUT.
- Order 2: all 18 f values; subcases with a = 7 are closed except f = 34 (needs extensions of all
  477,142 (3,8,27)-graphs, ~50,000 CPU-h; McKay's list: users.cecs.anu.edu.au/~bdm/data/ramsey.html).
- Honest limit: known (3,10,39)-graphs with an involution of type (2,1)/(2,3) were not found in 4 h;
  for p = 2 with few fixed points a TIMEOUT says nothing.

## Do
1. Rebuild the symsat pipeline (needs CaDiCaL + drat-trim from opt/, or private copies). Calibrate on
   (3,9,35) (order 7 and 5 of C35 must come out SAT) as sec5.tex did.
2. Certify (5,5). Then attack (3,10), (3,7) subcases with a stronger encoding (degree rows, the
   twins fact F6, fixed-point bounds F7 per orbit) before raw time.
3. For order 2 with large f: a quotient view (the fixed set F induces a (3,10-?)-graph with structure)
   may give a hand proof for more f values; try to prove empty cases like Lemma 5.3 did for a = 7.
