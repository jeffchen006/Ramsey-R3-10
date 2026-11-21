# Degree-seven residue floor 108 (round 5)

**Cert, pending critic.** In a maximal triangle-free `(3,10,40)` graph,
every degree-seven root has `e(G-N[v]) >=108`. The checked G-011 bound
handles levels below 107 and this package certifies level 107, without
using any degree-eight or degree-nine gluing premise. The catalogue is
exactly all 234,681 classes in Goedgebeur–Radziszowski T14 (arXiv:1210.5826),
as audited in `E162_E107.md`. This subsumes that file's direct e162 cut.

## Clique and pinned-CNF cover

An exterior **demand** is either a singleton or a pair at distance at least
three. It must be covered by one of the seven attachment rows, and two
demands cannot share a row if an exterior edge joins them. Therefore a
verified incompatibility clique on eight demands refutes a root. The
original catalogue has 231,455 such checked witnesses. The exact ordered
complement has 3,226 inputs, each with a verified clique on seven demands.

For a seven-clique, assign a covering row to each of its seven demands.
The rows must be distinct and exhaust the seven rows. Permute the rows so
that row `i` covers demand `i` in the supplied order. Add one unit clause
per demand endpoint to the corresponding row of G's `root_core.py`
necessary CNF. This normalization loses no completion: all seven rows
are initially interchangeable. In particular it is not a lex restriction
in addition to the pins, and it does not assume a demand is uniquely
covered. The CNF retains only necessary MTF row, column and pair coverage,
with triangle exclusions and the degree-at-most-nine column cap; it needs
no further independent-set clauses, total edge count or degree profile.

`e107_core_proofs.py` verifies the seven-clique for each generated CNF
and sends the proof to both `lrat-check` and `cake_lpr`. Its verify-only
mode reconstructs each CNF from the bound residue and pin order and
compares bytes before rerunning both checkers. `replay_floor7_108.sh`
also checks all graph counts and the exact clique complement. The
SHA256 index in the producer log is checked by replay per input. All
3,226 proofs passed at production and replay, with byte-identical
recomputed CNFs and matching indices. See `scratch/B/logs/e107_pin_full.log`
and `scratch/B/logs/e107_floor108_replay.log` (221.28 and 236.77 CPU s).

## Cross-checks and cost

- Separate MTF gluing (`mtfcover_r5 -X -k 9 -d 7 -m 6 -M 9 -E 161 -e 180`):
  234,681 inputs, zero leaves and zero completions, 355.17 CPU s.
- Independent SAT gluing (corrected `D+s-alpha` bound, positive D5/K6
  order-22 control): 64/64 e107 sample UNSAT, 14.14 CPU s.
- Demand-clique generator matches the 39/39 level-104 control and its
  witnesses pass G's Python verifier. Full search at e107 takes 2.30
  CPU s and the separate full verifier takes 47.86 CPU s.
- 64/64 pinned dual LRATs in 4.48 CPU s; the same unpinned core pilot
  took 50.33 CPU s. A stronger single-row support clique filter finds
  no further eight-cliques in the 3,226 complement and is not needed.

From `scratch/B` the no-solve bundle is `src/replay_floor7_108.sh` under
`ralph/lanes/B`, with data bound by `FLOOR7_108.sha256` in that lane.
